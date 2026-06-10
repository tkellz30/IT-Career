# Production Router Rollback Procedures

**Read this before starting the cutover. Know your exit before you enter.**

This document is the companion rollback reference for
[checklists/production-router-cutover.md](../checklists/production-router-cutover.md)
and [docs/11-production-router-migration.md](../docs/11-production-router-migration.md).
It follows the same philosophy as the existing
[rollback/networking-rollback-procedures.md](networking-rollback-procedures.md):
write the exit plan down *before* you need it, not while troubleshooting an outage.

---

## Guiding Principle

**Do not depend solely on the thing you are changing to also be your way back.**
If the cutover affects WAN/LAN routing, your rollback plan cannot assume that routing
still works. Always have at least one access path that is independent of the change
being made — physical console access and Tailscale are the two anchors here.

---

## Access Priority Ladder for This Migration

```
Level 1 (most reliable): Physical console — keyboard + monitor directly on esther
Level 2:                  Direct LAN connection to esther, bypassing pfSense entirely
Level 3:                  Tailscale (100.x.x.x) — independent of LAN/WAN routing changes
Level 4 (least reliable during cutover): Access routed through pfSense-prod itself
```

**Before starting any cutover phase that touches routing, confirm Levels 1–3 are all
available.** Never proceed on Level 4 alone — if pfSense misbehaves, Level 4 disappears
along with your ability to fix it remotely.

> **Keep a local console/keyboard/monitor option available** for the entire duration
> of the physical cutover phases (Phases 9–12 of the checklist). This is non-negotiable
> for the ISP bridge-mode step specifically.

> **Tailscale is your independent fallback — but don't depend on it alone either.**
> Tailscale rides on `tailscale0`, which should remain unaffected by LAN/WAN interface
> changes on `esther`. However, if `esther` itself becomes unreachable (e.g., it loses
> power, crashes, or its routing gets so tangled that even Tailscale can't bind), only
> physical console access will get you back in. Treat Tailscale as a *strong secondary*,
> and physical access as the ultimate guarantee.

---

## ✅ Tested Case: Netplan LAN Bridge Test Caused Connectivity Loss — Rollback Timer Restored `eno1` (2026-06-09)

Unlike the scenarios below (which are *planned* recovery procedures for situations
that have not yet occurred), **this case actually happened and was successfully
recovered from** — making it the first real-world proof that the rollback approach
described in this document works as intended.

**What was attempted:** a draft Netplan bridge configuration was prepared to
(eventually) move `esther`'s host networking from `eno1` onto a future `br-lan`
bridge. Before applying it, a **rollback script and a systemd rollback timer** were
staged specifically so that a bad change would revert itself automatically — exactly
the kind of preparation the Guiding Principle at the top of this document calls for.

**What happened when the bridge config was applied:**
- **Remote connectivity to `esther` dropped** — a Windows client's `ping` briefly
  reported the host as unreachable
- The prepared **systemd rollback timer fired as designed**
- After the timer ran, `esther` became reachable again at its normal address

**Post-rollback verification confirmed a full, exact return to the known-good state:**
```
eno1:           192.168.0.24/24                  (restored)
default route:  192.168.0.1 dev eno1             (restored)
Netplan config: /etc/netplan/50-cloud-init.yaml
                eno1:
                  dhcp4: true                     (restored to original form)
rollback timer: no longer active (cleared itself after running)
```

**Why this matters:** this was a **deliberate test of the rollback mechanism itself**,
not a failed attempt at completing the bridge migration. The bridge was *not* kept —
the moment connectivity dropped, reverting was the correct outcome, and the prepared
safety net did exactly what it was designed to do, with **no manual recovery or
physical console intervention required**. `pfsense-prod` was shut off and uninvolved
throughout; `pfsense-lab`, the Cox modem, and the rest of the home network were
untouched.

**Lesson carried forward — and already reflected in the Phase 5 planning note in
[checklists/production-router-cutover.md](../checklists/production-router-cutover.md):**
even with a rollback timer staged and working, remote connectivity *did* briefly drop.
**Future bridge attempts should be made only with local monitor/keyboard access to
`esther` connected and verified beforehand** — don't rely on the rollback timer (or
Tailscale, or SSH) as your only safety net for a host-networking change of this kind.
Treat the timer as a strong automated backstop, and physical access as the layer
beneath it, per the Access Priority Ladder above.

---

## ✅ Update: `br-lan` Bridge Retried Successfully With Local Access Available — New Known-Good State (2026-06-10)

Following the lesson learned above, the same Netplan bridge change was **retried with
local monitor/keyboard access to `esther` connected and verified beforehand**. This
time it **succeeded and was kept** — `esther`'s host networking now runs on a bridge.

**SSH disconnected briefly during `netplan apply`, exactly as expected** (the same
brief-interruption pattern seen in the rollback drill above), and the host came back
on its own with a new DHCP lease. Tailscale remained active throughout, and internet
(`ping -c 4 1.1.1.1`) and DNS (`ping -c 4 google.com`) both verified at 0% packet loss.

> **This changes the "known-good state" baseline for `esther`'s host networking going
> forward.** Rollback procedures and recovery checks for *future* phases should expect
> and verify the bridge state below — not the pre-bridge `eno1`-direct state recorded
> in the tested case above (which remains accurate as a historical record of that
> specific drill, but is no longer the host's current normal configuration).

**New known-good bridge state on `esther` (current, as of 2026-06-10):**
```
br-lan:         192.168.0.28/24            (DHCP lease, holds the host IP)
default route:  192.168.0.1 dev br-lan
eno1:           bridge member of br-lan, dhcp4: false (no longer holds the host IP)
Tailscale:      active
SSH:            running, reachable (after the brief expected netplan-apply interruption)
```

**What this does *not* change:** `pfsense-prod` was not started or involved in this
change, no pfSense LAN interface has been attached to `br-lan`, the Cox modem/router
is unchanged, and no physical cutover has occurred. `br-lan` existing and working is a
**prerequisite** for an eventual pfSense LAN attachment — it is not that attachment.

---

## Scenario: `pfsense-prod` Fails to Boot or Misbehaves in Lab Mode (Phase 3)

**Symptom:** VM won't start, GUI unreachable, unexpected network behavior — all while
still isolated (no physical NICs attached).

**This is the safest possible failure point** — nothing physical has changed yet.

```bash
# Stop the VM
virsh destroy pfsense-prod

# If needed, remove it entirely and start over from a fresh clone
virsh undefine pfsense-prod --remove-all-storage
```

`pfsense-lab`, the home network, and `eno1` are completely unaffected by anything
that happens to `pfsense-prod` at this stage.

---

## Scenario: Something Goes Wrong After Attaching the USB WAN Adapter (Phase 10, early)

**Symptom:** `pfsense-prod` doesn't see the WAN interface correctly, or attaching it
causes unexpected host-level network behavior.

```bash
# Power off the VM immediately
virsh destroy pfsense-prod

# Detach the physical/USB interface from the VM definition
# (exact command depends on how it was attached — documented in Phase 5 of the checklist
#  before the attachment was made; revert using that same documented method)

# Restore to the pre-physical-NIC snapshot
virsh snapshot-revert pfsense-prod pre-physical-nic
```

Because the USB adapter was previously unused, disconnecting it returns the host to
its exact prior state. `eno1` and the existing LAN path are untouched.

---

## Scenario: LAN Cutover Causes Connectivity Problems (Phase 10, later steps)

**Symptom:** Test devices on the new pfSense LAN segment can't get DHCP, can't reach
the internet, or `esther`'s own management access becomes unstable.

**Immediate action:**
```bash
# Stop pfSense-prod — this halts any routing/DHCP it was providing
virsh destroy pfsense-prod
```

**Reconnect the previous network path:**
1. Physically reconnect `eno1` to its original switch/router port if it was moved
2. Confirm `esther` re-acquires its previous IP/gateway (`ip -br addr`, `ip route`)
3. Confirm Tailscale shows active (`tailscale status`)
4. Confirm LAN devices regain connectivity through the original path (Cox router → switch → devices)

**Leave `pfsense-prod` powered off** until the root cause is understood. Do not restart
it into the same physical configuration without first reverting to the relevant snapshot:

```bash
virsh snapshot-revert pfsense-prod pre-physical-nic
# or, if further back is needed:
virsh snapshot-revert pfsense-prod safe-clone-baseline
```

---

## Scenario: ISP Bridge-Mode Cutover Fails (Phase 11 — Highest Risk)

**Symptom:** After putting the Cox modem/router into bridge/passive mode,
`pfsense-prod` does not obtain a working WAN connection, or the home loses internet.

**This is the step that requires physical console access to be ready in advance.**

**Step-by-step recovery:**

1. **Put the Cox modem/router back into normal router mode.**
   - Use its local admin interface (typically reachable at its default gateway IP
     directly from a device plugged into it, bypassing pfSense entirely)
   - This alone restores internet to the household via the original path, independent
     of anything pfSense is doing
2. **Reconnect the previous network path** — restore the original cable run
   (modem/router → original switch/AP setup) if anything was physically moved for the test
3. **Leave `pfsense-prod` powered off:**
   ```bash
   virsh destroy pfsense-prod
   ```
4. **Restore the `pfsense-prod` snapshot** if any in-VM configuration needs to be
   rolled back before the next attempt:
   ```bash
   virsh snapshot-revert pfsense-prod pre-physical-nic
   ```
5. **Do not modify `pfsense-lab`** at any point in this process — it is not part of
   the cutover and should not be touched, queried for "spare parts," or used as a
   fallback router. It remains the preserved lab/portfolio VM.
6. **Verify full restoration** before attempting cutover again:
   - Internet works via the original Cox router path
   - `esther` is reachable via `eno1` at its normal LAN IP
   - Tailscale shows active and independent
   - All household devices (TV, PlayStation via Deco, etc.) are working normally

**Do not re-attempt the bridge-mode cutover until the root cause of the failure is
understood and a fix is planned** — repeating the same step expecting a different
result risks a longer outage, not a shorter one.

---

## Scenario: Total Loss of Remote Access During Cutover

**Symptom:** Tailscale unreachable, LAN SSH unreachable, nothing responds remotely.

1. **Go to physical console access on `esther`** (this is why it must be staged in advance)
2. Log in locally
3. Check VM state: `virsh list --all`
4. If `pfsense-prod` is running and suspected as the cause: `virsh destroy pfsense-prod`
5. Check host networking: `ip addr show && ip route show`
6. If `eno1` is in an unexpected state (e.g., bridged), follow the existing
   [networking-rollback-procedures.md](networking-rollback-procedures.md) bridge-removal steps:
   ```bash
   sudo ip link set eno1 nomaster
   sudo ip link delete br0 type bridge   # or whatever bridge name was used, if any
   sudo dhclient eno1
   ```
7. If Tailscale itself is down: `sudo systemctl restart tailscaled && tailscale status`
8. Once stable, **stop** — do not attempt the cutover again in the same session.
   Investigate root cause first.

---

## What Stays Untouched No Matter What

Regardless of how a rollback unfolds, the following must remain unaffected — if any
of these are impacted, treat it as a separate incident requiring its own investigation:

- `pfsense-lab` — never modified, never used as a substitute router, never deleted
- `tailscale0` / Tailscale connectivity — independent fallback; restart the service if
  needed, but don't reconfigure it as part of router troubleshooting
- Docker bridges and containers — unrelated to this migration; leave alone
- The `nvme-vms` / `nvme-isos` storage pools and their existing contents (other than
  the new `pfsense-prod` disk, which can be safely deleted/recreated if needed)

---

## Pre-Cutover Rollback Readiness Checklist

Run through this immediately before **Phase 11 (ISP bridge-mode cutover)** specifically —
this is the point where rollback speed matters most:

```
[ ] Physical console (keyboard + monitor) is connected and tested on esther
[ ] I know the Cox modem/router's local admin URL and credentials, reachable
    directly (not through pfSense)
[ ] I have verified Tailscale is active right now
[ ] I have verified eno1's current IP/gateway and written it down
[ ] I have a verified, restorable pfSense-prod snapshot (pre-physical-nic)
[ ] I know the exact commands to power off pfSense-prod (virsh destroy pfsense-prod)
[ ] I know the exact steps to revert the Cox modem/router to normal router mode
[ ] I have allotted enough uninterrupted time to complete this step and roll back
    cleanly if needed — not a "quick test between other things"
[ ] pfsense-lab is confirmed untouched and unaffected by any of this
```

---

## Key Commands Reference Card

```bash
# VM control
virsh list --all                          # Show all VMs and their state
virsh destroy pfsense-prod                # Immediate stop (does not delete)
virsh undefine pfsense-prod --remove-all-storage   # Full removal (only if starting over)

# Snapshots
virsh snapshot-list pfsense-prod
virsh snapshot-revert pfsense-prod safe-clone-baseline
virsh snapshot-revert pfsense-prod pre-physical-nic

# Host network state (read-only — confirm before/after any change)
ip -br link
ip -br addr
ip route show

# Tailscale
tailscale status
sudo systemctl restart tailscaled

# Bridge cleanup, if eno1 was ever bridged (should not normally happen)
sudo ip link set eno1 nomaster
sudo ip link delete br0 type bridge
sudo dhclient eno1
```
