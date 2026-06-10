# Production Router Cutover Checklist

**Status:** 🟡 In progress — Phases 2–4 complete (clone created, booted and functionally
validated in safe lab mode with a Debian test client — DHCP, gateway, internet routing,
and DNS all passing — and two restorable snapshots captured: `safe-clone-baseline` and
`safe-lab-validated`, 2026-06-08). Phase 1 USB-adapter detection also confirmed from
*inside* pfSense — the Realtek RTL8152 adapter appears as `ue0` (2026-06-07), still
unassigned and not connected to the modem. In Phase 5 planning, the host-level
**`br-lan` bridge prerequisite is now built and verified** on `esther` — `eno1` is a
bridge member, `br-lan` holds the host IP (`192.168.0.28/24`), internet/DNS confirmed
at 0% packet loss (2026-06-10, retried successfully with local console access after an
earlier rollback drill). **No pfSense LAN interface has been attached to `br-lan`.**
Physical NIC assignment to pfSense, switch/AP, Cox bridge-mode, and cutover phases
have not started.
See [docs/11-production-router-migration.md](../docs/11-production-router-migration.md#progress-log)
for the full milestone write-up.  
**Companion docs:** [docs/11-production-router-migration.md](../docs/11-production-router-migration.md) ·
[rollback/production-router-rollback.md](../rollback/production-router-rollback.md)

---

> **How to use this checklist:** Complete phases **in order**. Each phase ends with a
> **Go / No-Go Gate** — do not proceed past a gate that fails. If a gate fails, stop,
> consult [rollback/production-router-rollback.md](../rollback/production-router-rollback.md),
> and resolve the issue before re-attempting that phase.

---

## Phase 0 — Pre-Change Documentation

- [ ] Record current `eno1` IP, gateway, and DNS configuration (read-only — `ip -br addr`, `ip route`)
- [ ] Record current `enx5c857e3c904d` (USB adapter) state — confirm it shows as down/unused
- [ ] Record current `tailscale status` output and confirm Tailscale is healthy
- [ ] Record current Cox modem/router mode (should be normal router mode, not bridge)
- [ ] Record current `virsh list --all`, `virsh net-list --all`, `virsh pool-list --all` output
- [ ] Confirm `pfsense-lab` snapshot `fresh-install` still exists and is restorable
- [ ] Capture screenshot `20-host-network-interfaces-before-cutover.png`

**Go/No-Go Gate:** ✅ Go only if all baseline data is recorded and Tailscale shows active.
❌ No-Go if Tailscale is not connected — fix that first, independent of this project.

---

## Phase 1 — Host / Interface Verification

- [ ] Confirm `eno1` is the interface currently carrying the active management session
- [ ] Confirm `eno1`'s IP/gateway match the recorded baseline from Phase 0
- [ ] Plug in / power the USB-to-Ethernet adapter if not already connected, and confirm
      the host detects it (`ip -br link`, `dmesg | tail`, `lsusb`)
- [ ] Confirm the adapter identifies as Realtek RTL8152 (Fast Ethernet) as expected
- [ ] Confirm the adapter is **not** assigned an IP and is **not** bridged to anything
- [ ] Re-confirm Tailscale is still active after the adapter is connected
- [x] Confirm `pfsense-prod` itself (not just the host) detects the USB adapter when
      attached via USB passthrough — *confirmed 2026-06-07: adapter appears as `ue0` in
      `ifconfig -l`; `ifconfig ue0` shows `media: Ethernet autoselect (none)`,
      `status: no carrier` (expected — no cable connected); `usbconfig` confirms
      `RTL8152 Fast Ethernet Adapter` / `Realtek Semiconductor Corp.` at `usbus3`*
- [x] Confirm the adapter is visible to pfSense but **not** assigned to any role
      (WAN/LAN/OPT) — *confirmed 2026-06-07: `ue0` is detected and inert, no interface
      assignment made inside pfSense; this is detection only, not WAN cutover*
- [ ] Capture screenshot `25-usb-ethernet-detected.png` — *terminal evidence captured
      (`ifconfig -l`, `ifconfig ue0`, `usbconfig` output reviewed showing `ue0` detected
      with `no carrier`); image file not yet saved as a redacted screenshot*

> **Note on scope:** the two items above were verified *from inside pfSense* (proving
> pfSense itself can use the adapter as a WAN candidate), which is a stronger check than
> the host-level detection items still listed above. The remaining unchecked items in
> this phase (host-level `ip -br link`/`lsusb` confirmation, `eno1` baseline checks, and
> the Tailscale re-confirmation) should still be completed and documented separately —
> this entry does not assume they are done.

**Go/No-Go Gate:** ✅ Go only if `eno1` is unchanged, the USB adapter is detected and
inert, and Tailscale is still healthy. ❌ No-Go if connecting the adapter caused any
change to `eno1`'s state, routing, or Tailscale connectivity — disconnect it and
investigate before continuing.

---

## Phase 2 — Clone `pfsense-lab` → `pfsense-prod`

- [x] Confirm `pfsense-lab` is in a clean, known state — *confirmed shut off and untouched (2026-06-08)*
- [ ] Capture screenshot `21-pfsense-lab-running-before-clone.png` (proof the lab VM is untouched pre-clone) — *not yet captured*
- [x] Use `virt-clone` to create `pfsense-prod` as an independent VM with its own disk —
      *completed 2026-06-08; disk at `/mnt/fast-storage/vms/pfsense-prod.qcow2`, distinct UUID/MACs from `pfsense-lab`*
- [x] Verify `pfsense-lab` is still present, unmodified, and independently bootable — *confirmed shut off, untouched*
- [x] Verify `pfsense-prod` appears in `virsh list --all` as a separate, independent VM — *confirmed running*
- [x] Verify `pfsense-prod`'s disk path is distinct from `/mnt/fast-storage/vms/pfsense-lab.qcow2` —
      *confirmed: `pfsense-prod.qcow2` vs. `pfsense-lab.qcow2`*
- [ ] Capture screenshot `22-pfsense-prod-clone-created.png` — *terminal evidence exists (`virsh domiflist`/`domblklist` output reviewed); not yet saved as a redacted screenshot file*

**Go/No-Go Gate:** ✅ Go only if both VMs exist independently, with separate disks,
separate UUIDs, and `pfsense-lab` is provably unmodified. ❌ No-Go if the clone shares
any state (disk, UUID, MAC) with `pfsense-lab` — destroy the bad clone and retry.

---

## Phase 3 — Boot `pfsense-prod` Safely in Lab Mode

- [x] Attach `pfsense-prod` **only** to isolated/NAT libvirt networks — mirror the
      original `pfsense-lab` topology. **No physical NICs attached.** —
      *confirmed: `vnet0` → `default` (DHCP `192.168.122.135/24`), `vnet1` → `pfsense-lab-lan`, `domblklist` shows no CD-ROM (`hda: -`)*
- [x] Boot `pfsense-prod` and confirm it starts cleanly — *confirmed running via `virsh snapshot-list` showing state `running`*
- [ ] Confirm its web GUI is reachable via the same VNC-over-SSH-tunnel approach used for `pfsense-lab` — *not yet separately documented (functional validation below confirms the router/DHCP/DNS roles are working, which implies the GUI-configured services are active, but the GUI-reachability step itself has not been captured)*
- [ ] Confirm WAN/LAN interface assignment inside pfSense matches expectations for the clone — *not yet separately documented*
- [ ] Change any cloned default credentials (do not reuse `pfsense-lab`'s admin password indefinitely) — *not yet documented*
- [ ] Capture screenshot `23-pfsense-prod-first-boot.png` — *not yet captured*
- [x] Optionally repeat a lightweight version of the lab connectivity test (DHCP, ping, GUI reachability) using a throwaway test client on the isolated network —
      *completed and exceeded 2026-06-08: `test-client` (Debian Live, ISO `debian-live-13.5.0-amd64-lxde.iso`) connected to `pfsense-lab-lan`, received DHCP `10.50.0.100/24` from `pfsense-prod` (gateway `10.50.0.1`); `ping -c 4 10.50.0.1`, `ping -c 4 1.1.1.1`, and `ping -c 4 google.com` each returned 4/4 received, 0% packet loss — confirming gateway reachability, internet routing, and DNS resolution all work correctly through `pfsense-prod`*
- [ ] Capture screenshot `24-pfsense-prod-safe-lab-network-verified.png` — *underlying evidence captured at the terminal (DHCP lease, gateway/internet/DNS ping results); image file not yet saved*

**Go/No-Go Gate:** ✅ **PASSED (2026-06-08)** — `pfsense-prod` boots cleanly and behaves
correctly in an isolated network: it issued a correct DHCP lease, routed internet
traffic, and resolved DNS for a LAN-side test client, with 0% packet loss across all
tests. It has reached the same "proven safe in isolation, and functionally correct"
state that `pfsense-lab` reached during its own validation
(see [docs/10-pfsense-lab-validation.md](../docs/10-pfsense-lab-validation.md)).
*(Note: the GUI-reachability and credential-change sub-items above remain open and
should still be completed/documented before considering Phase 3 fully closed — the
gate reflects that the core network-functionality requirement has been met, not that
every checklist item in this phase is finished.)*
❌ No-Go if the VM fails to boot, the GUI is unreachable, or anything about its
network behavior is unexpected — troubleshoot in isolation; do not proceed to physical NICs.

---

## Phase 4 — Snapshot `pfsense-prod`

- [x] Create a snapshot of `pfsense-prod` at this known-good "boots clean, isolated, no physical NICs" state —
      *completed 2026-06-08 as `safe-clone-baseline` ("Baseline clone before production router changes")*
- [x] Verify the snapshot is listed and restorable (`virsh snapshot-list pfsense-prod`) —
      *confirmed: listed with creation time `2026-06-08 01:12:21 +0000`, state `running`*
- [x] Record the exact revert command for this snapshot in this checklist for quick reference:
      `virsh snapshot-revert pfsense-prod safe-clone-baseline`

> **Note:** the actual snapshot name created was `safe-clone-baseline` (not the
> placeholder `safe-baseline` originally suggested in this checklist). The revert
> command above and the Quick-Reference section at the bottom of this file have been
> updated to match the real snapshot name.

**Additional snapshot captured after functional validation (2026-06-08):**

- [x] A second snapshot, `safe-lab-validated` ("pfsense-prod verified with Debian test
      client on lab LAN"), was created immediately after the Phase 3 connectivity
      testing passed — capturing the VM in its "proven working as a router/firewall in
      the safe lab topology" state
- [x] Verified listed and restorable: `virsh snapshot-list pfsense-prod` now shows two
      entries, in order — `safe-clone-baseline` then `safe-lab-validated`
- [x] Revert command recorded: `virsh snapshot-revert pfsense-prod safe-lab-validated`

> Both snapshots remain available as restore points. `safe-clone-baseline` is the
> "clean clone, never configured beyond inheriting `pfsense-lab`'s state" point;
> `safe-lab-validated` is the "proven working correctly as a router/firewall in the
> sandbox" point — the more advanced and currently most relevant restore target before
> any physical NIC work begins.

**Go/No-Go Gate:** ✅ Go only if the snapshot exists and its revert command is verified
and written down. ❌ No-Go if snapshot creation fails — resolve storage/permission
issues before continuing; do not proceed without a restore point.

---

## Phase 5 — Plan Physical NIC Assignment (Documentation Step — No Changes Yet)

> **Note — first LAN bridge test result (2026-06-09):** a draft Netplan bridge
> (`br-lan`) was test-applied on `esther` as a *rollback-mechanism drill*, not a
> completed migration step. **Remote connectivity (SSH/ping) dropped when the bridge
> went up**, and a prepared rollback script + systemd timer **automatically reverted
> `esther` back to its original `eno1` DHCP configuration** — restoring
> `192.168.0.24/24`, the default route via `192.168.0.1 dev eno1`, and
> `/etc/netplan/50-cloud-init.yaml` to `eno1: dhcp4: true`. The bridge was **not**
> kept; this is **not** a completed LAN bridge or physical-NIC-assignment milestone —
> see [docs/11-production-router-migration.md](../docs/11-production-router-migration.md#progress-log)
> and the new tested case in
> [rollback/production-router-rollback.md](../rollback/production-router-rollback.md)
> for the full write-up.
>
> ⚠️ **Caution for future bridge attempts:** connectivity loss during this test was
> brief but real — confirm **local monitor/keyboard access to `esther` is connected
> and tested** (per the Access Priority Ladder in the rollback doc) *before* applying
> any future bridge configuration, even with a rollback timer staged. Do not rely on
> remote access (SSH/Tailscale) alone during a host-networking change of this kind.

> **Update — host bridge retry succeeded with local access available (2026-06-10):**
> the same Netplan bridge change was retried, this time with local monitor/keyboard
> access to `esther` connected and verified first. It **succeeded and was kept**:
> `eno1` is now `dhcp4: false` (a bridge member), `br-lan` holds the host IP
> (`192.168.0.28/24` via DHCP), the default route is `192.168.0.1 dev br-lan`, SSH
> reconnected on its own after the brief expected `netplan apply` interruption,
> Tailscale stayed active, and internet/DNS both verified with 0% packet loss
> (`ping -c 4 1.1.1.1`, `ping -c 4 google.com`). See
> [docs/11-production-router-migration.md](../docs/11-production-router-migration.md#progress-log)
> and the known-good state recorded in
> [rollback/production-router-rollback.md](../rollback/production-router-rollback.md).
> **This proves the host-level bridge prerequisite works — it does not mean pfSense
> LAN attachment, WAN assignment, or any further cutover step is complete.**

- [x] Prepare the host-level bridge (`br-lan`) that a future pfSense LAN interface
      would attach to — *completed and verified 2026-06-10: `br-lan` created via
      Netplan with `eno1` as its member, host networking running cleanly on
      `192.168.0.28/24` with internet/DNS confirmed at 0% packet loss; this is the
      host-side prerequisite only — no pfSense interface has been attached to it*
- [ ] Document the intended mapping in writing, before touching any VM or libvirt config:
      - WAN → `enx5c857e3c904d` (USB-to-Ethernet, Realtek RTL8152)
      - LAN → `eno1` (built-in Intel Ethernet)
- [ ] Confirm this matches the rationale in [docs/11-production-router-migration.md](../docs/11-production-router-migration.md)
      (USB adapter first because it's currently unused and lower-risk; built-in NIC last
      because it currently carries the active management path)
- [ ] Identify exactly which libvirt/VM configuration changes will be required to attach
      these physical interfaces (e.g., PCI/USB passthrough vs. host-bridge approach) —
      research and write down the plan; do not apply it yet — *the host-bridge approach
      now has a working `br-lan` to build on, but the libvirt/VM-side attachment plan
      itself is still not written down or applied*
- [ ] Capture screenshot `29-physical-nic-assignment-planned.png`

**Go/No-Go Gate:** ✅ Go only if the assignment plan is fully written down and reviewed
against the safety rules in [docs/11-production-router-migration.md](../docs/11-production-router-migration.md#safety-rules-hard-requirements-before-any-physical-change).
❌ No-Go if there is any ambiguity about which interface does what — resolve on paper first.

---

## Phase 6 — Prepare the PoE VLAN-Capable Switch

- [ ] Apply basic switch configuration only (management IP, admin access) — **no VLANs yet**
      (VLANs come later, per [docs/12-vlan-switch-and-ap-design.md](../docs/12-vlan-switch-and-ap-design.md))
- [ ] Confirm the switch is reachable via its management interface
- [ ] Confirm PoE ports are functioning (test with a known-good PoE device if available)
- [ ] Capture screenshot `26-switch-vlan-plan.png` (showing the basic/pre-VLAN plan or config screen)

**Go/No-Go Gate:** ✅ Go only if the switch is reachable and configured at a basic
level, with no VLANs applied yet. ❌ No-Go if the switch cannot be managed — resolve
before it becomes part of the live LAN path.

---

## Phase 7 — Prepare the Cisco Access Point

- [ ] Confirm the Cisco AP is reachable via its management interface
- [ ] Confirm its current SSID/configuration (basic — no VLAN SSIDs yet)
- [ ] Capture screenshot `27-cisco-ap-management-access.png`

**Go/No-Go Gate:** ✅ Go only if the AP is reachable and manageable on the current
network. ❌ No-Go if it cannot be reached — resolve before relying on it for the new LAN.

---

## Phase 8 — Keep Deco in AP Mode for TV/PlayStation Bridge

- [ ] Confirm the Deco system is still in AP mode (not router mode) — no change needed
- [ ] Confirm TV and PlayStation remain wired to the Deco satellite unit and functioning normally
- [ ] Note: no action required here beyond verification — this device's role does not change during cutover

**Go/No-Go Gate:** ✅ Go if Deco is confirmed in AP mode and TV/PlayStation are working
normally (this gate exists to make sure cutover work doesn't accidentally disturb them).
❌ No-Go if Deco has drifted into router mode or TV/PlayStation are having issues —
resolve those independently first; don't compound problems.

---

## Phase 9 — Snapshot Immediately Before First Physical NIC Attachment

- [ ] Re-confirm `pfsense-prod` is in the same good state as the Phase 4 snapshot
- [ ] Create a fresh snapshot specifically labeled for this point
      (e.g., `virsh snapshot-create-as pfsense-prod pre-physical-nic "Before attaching any physical NIC"`)
- [ ] Verify the snapshot and its revert command
- [ ] Capture screenshot `28-pfsense-prod-snapshot-before-physical-nic-change.png`

**Go/No-Go Gate:** ✅ Go only if this fresh snapshot exists and is verified restorable.
❌ No-Go — do **not** attach any physical NIC without a fresh, verified snapshot at this exact point.

---

## Phase 10 — Test LAN and Wi-Fi Incrementally

- [ ] Attach the USB-to-Ethernet adapter to `pfsense-prod` as WAN **first** (lowest-risk interface — currently unused)
- [ ] Verify `pfsense-prod` detects and can use the WAN interface (e.g., obtains an address from the existing ISP path, or from a controlled test segment)
- [ ] Only after WAN is verified working, plan and test the LAN-side connection through `eno1` →
      PoE switch → a single test device (not the whole household yet)
- [ ] Bring devices onto the new LAN segment **one at a time**, verifying connectivity after each addition
- [ ] Connect the Cisco AP to the switch and verify basic Wi-Fi connectivity for a single test device
- [ ] Confirm Tailscale and `esther`'s management access remain reachable throughout this phase
- [ ] Do **not** connect the whole household's devices until each step above is verified

**Go/No-Go Gate:** ✅ Go to the next device/step only after the current one is verified
working and management access (Tailscale + local) is confirmed intact. ❌ No-Go —
if at any point management access is lost or a device fails to connect as expected,
stop, do not add more devices, and consult the rollback document.

---

## Phase 11 — ISP Bridge / Passive-Mode Cutover

- [ ] Confirm **every** prior phase passed its Go/No-Go gate — this is the point of no easy return
- [ ] Confirm `pfsense-prod` has been fully verified end-to-end on the new LAN (Phase 10 complete)
- [ ] Confirm rollback steps are written, reviewed, and ready (see [rollback/production-router-rollback.md](../rollback/production-router-rollback.md))
- [ ] Confirm a local console/keyboard/monitor option is available for `esther` (do not rely on remote access alone for this step)
- [ ] Put the Cox modem/router into bridge/passive mode
- [ ] Confirm `pfsense-prod` WAN obtains a real address from the ISP

**Go/No-Go Gate:** ✅ Go only if all of the above are true *simultaneously* —
this is the highest-risk step in the entire migration. ❌ No-Go if **any** condition
is unmet — revert the modem to router mode immediately and do not retry until resolved.

---

## Phase 12 — Validation

- [ ] Confirm internet access works through `pfsense-prod` from a LAN client
- [ ] Confirm DNS resolution works
- [ ] Confirm internal LAN routing and the PoE switch/Cisco AP/Deco all function as expected
- [ ] Confirm `esther`'s own management access (now routed via `pfsense-prod`'s LAN) is reachable
- [ ] Confirm Tailscale remains active and independent
- [ ] Capture screenshot `30-final-topology-after-cutover.png`
- [ ] Update `docs/11-production-router-migration.md` status to reflect completion

**Go/No-Go Gate:** ✅ Migration considered complete only when **all** validation items
pass and remain stable for an observation period (recommend at least 24–48 hours
before considering the old path fully retired). ❌ If anything fails — follow the
rollback document immediately; do not "wait and see" on a broken router cutover.

---

## Phase 13 — Rollback (Reference Only — Use if Any Gate Fails)

- [ ] See the full procedure in [rollback/production-router-rollback.md](../rollback/production-router-rollback.md)
- [ ] Remember: `pfsense-lab` is never touched by any of this — it remains a safe fallback reference and portfolio artifact regardless of how the cutover goes

---

## Quick-Reference Snapshot Commands

```bash
# List snapshots for the production VM
virsh snapshot-list pfsense-prod

# Revert to the verified safe-clone baseline (created 2026-06-08, pre-cutover, never configured)
virsh snapshot-revert pfsense-prod safe-clone-baseline

# Revert to the verified, functionally-tested lab state (created 2026-06-08, after
# DHCP/gateway/internet/DNS validation passed with the Debian test-client)
virsh snapshot-revert pfsense-prod safe-lab-validated

# Revert to the snapshot taken immediately before physical NIC attachment (Phase 9 — not yet created)
virsh snapshot-revert pfsense-prod pre-physical-nic

# Emergency stop (does not delete the VM or its disk)
virsh destroy pfsense-prod
```
