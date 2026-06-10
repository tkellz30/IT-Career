# Production Router Migration — Planning

**Status:** 🟡 In progress — production clone created, validated end-to-end in safe lab
mode with a Debian test client (DHCP, gateway, internet routing, and DNS all passing),
two restorable snapshots captured (`safe-clone-baseline`, `safe-lab-validated`), the
Realtek RTL8152 USB-to-Ethernet adapter detected by pfSense itself as `ue0` (a WAN
candidate, not yet assigned), a host-level **LAN bridge rollback drill** that proved
the prepared rollback script/timer correctly auto-reverts a failed Netplan bridge
change, and — on retry with local console access available — a **successful `br-lan`
host bridge** now running on `esther` (`eno1` as bridge member, `br-lan` holding the
host IP at `192.168.0.28/24`, internet/DNS verified with 0% packet loss). Still
pre-cutover: **no pfSense LAN interface has been attached to `br-lan`**, no physical
NICs assigned to pfSense, no switch/AP wiring, no Cox bridge-mode change, no pfSense VM
involved in any of this. See the progress log below for the latest milestones.  
**Depends on:** [docs/10-pfsense-lab-validation.md](10-pfsense-lab-validation.md) (lab milestone — complete)  
**Related:** [checklists/production-router-cutover.md](../checklists/production-router-cutover.md) ·
[rollback/production-router-rollback.md](../rollback/production-router-rollback.md) ·
[docs/12-vlan-switch-and-ap-design.md](12-vlan-switch-and-ap-design.md)

---

## Purpose of This Phase

The virtual pfSense lab (`pfsense-lab`) proved that pfSense can be deployed, configured,
and enforce firewall rules correctly inside an isolated KVM/libvirt environment with zero
impact to the production network. This phase plans the **next step**: turning that proof
of concept into a real, physical home-router deployment — replacing the current
ISP router path with a pfSense VM that has direct physical NICs for WAN and LAN.

This document is **planning and design only**. No VM, network, or system changes have
been made as a result of writing it. It exists so that future work has a clear, safe,
reviewable path before any physical cutover happens.

---

## Progress Log

### 2026-06-08 — Production clone created, booted in safe lab mode, baseline snapshot captured

This is the **first completed technical milestone** of the production router migration.
It corresponds to Phases 2–4 of
[checklists/production-router-cutover.md](../checklists/production-router-cutover.md).

What was done (via `virt-clone`, entirely within the existing isolated/NAT libvirt topology):

- `pfsense-prod` was cloned from `pfsense-lab` as an independent VM with its own disk
  (`/mnt/fast-storage/vms/pfsense-prod.qcow2`, distinct from `pfsense-lab.qcow2`)
- `pfsense-prod` was started and is running in **safe lab mode only** — attached to the
  same kind of isolated/NAT libvirt networks the original lab used:
  - `vnet0` → libvirt network `default` (received DHCP address `192.168.122.135/24`)
  - `vnet1` → libvirt network `pfsense-lab-lan`
  - **No physical NICs attached**
- A baseline snapshot was created and verified:
  - Name: `safe-clone-baseline`
  - Description: `Baseline clone before production router changes`
  - State at capture time (`virsh snapshot-list pfsense-prod`): `running`
  - Revert command: `virsh snapshot-revert pfsense-prod safe-clone-baseline`
- `pfsense-lab` was confirmed **shut off and untouched** — preserved exactly as documented
- `test-client` was confirmed shut off (not part of this milestone's scope)

**What this milestone proves — and does not yet prove:**

| Proven | Not yet attempted |
|---|---|
| The production clone exists as an independent VM | No physical NICs have been attached to `pfsense-prod` |
| It boots successfully in the same safe, isolated libvirt topology used for `pfsense-lab` | The PoE switch is not plugged into anything yet |
| It has a verified, restorable baseline snapshot to revert to | The Cox modem/router has not been put into bridge/passive mode |
| `pfsense-lab` remains preserved and unaffected | `eno1` has not been changed — still the active management path |
| | The USB Ethernet adapter has not been connected to the modem |
| | Tailscale and the existing host network path are untouched |

**This is still pre-cutover.** No production routing role has been attempted —
`pfsense-prod` is currently nothing more than a verified, independently-bootable clone
sitting in the same kind of sandboxed network that `pfsense-lab` already proved safe.
The remaining phases (physical NIC planning, switch/AP prep, incremental LAN/Wi-Fi
testing, and the ISP bridge-mode cutover) have not started.

### 2026-06-08 (continued) — Safe lab validation passed using `test-client`, second snapshot captured

Building directly on the milestone above, `pfsense-prod` was then **functionally
validated** end-to-end inside the same safe, isolated libvirt topology — repeating the
same proven test methodology originally used to validate `pfsense-lab`
(see [docs/10-pfsense-lab-validation.md](10-pfsense-lab-validation.md)), this time
against the production clone:

- `test-client` (Debian Live) was started with the ISO
  `/mnt/fast-storage/isos/debian-live-13.5.0-amd64-lxde.iso` inserted, and connected
  to the isolated `pfsense-lab-lan` network — the same network `pfsense-prod`'s `vnet1` is attached to
- `test-client` received DHCP from `pfsense-prod`: **`10.50.0.100/24`**, gateway **`10.50.0.1`**
- **Gateway reachability:** `ping -c 4 10.50.0.1` → 4/4 received, 0% packet loss
- **Internet routing through `pfsense-prod`:** `ping -c 4 1.1.1.1` → 4/4 received, 0% packet loss
- **DNS resolution through `pfsense-prod`:** `ping -c 4 google.com` (resolved to `172.253.124.139`) → 4/4 received, 0% packet loss
- A second snapshot was created immediately after validation:
  - Name: `safe-lab-validated`
  - Description: `pfsense-prod verified with Debian test client on lab LAN`
  - Revert command: `virsh snapshot-revert pfsense-prod safe-lab-validated`
- `virsh snapshot-list pfsense-prod` now shows two restorable snapshots, in order:
  `safe-clone-baseline` → `safe-lab-validated`

**What this validates — and what it still does not:**

| Proven | Not yet attempted |
|---|---|
| `pfsense-prod` correctly serves DHCP, routes, and resolves DNS for a LAN-side client — functionally equivalent to the validated `pfsense-lab` behavior | No physical NICs have been attached to `pfsense-prod` |
| The clone is not just bootable — it actively performs the firewall/router role correctly inside the safe sandbox | The PoE switch remains unplugged from the live network |
| A second, more advanced restore point (`safe-lab-validated`) exists beyond the original clone baseline | The Cox modem/router is unchanged — still in normal router mode |
| | `eno1`, Tailscale, Docker bridges, and the existing home network remain untouched |

**Status remains in progress / pre-cutover — not complete.** This milestone proves
`pfsense-prod` works correctly *as a router and firewall inside the safe libvirt lab
topology* — the same kind of proof `pfsense-lab` already provided. It does **not**
constitute any part of the physical cutover. No physical NIC work, switch/AP wiring,
or ISP bridge-mode change has been attempted.

### 2026-06-07 — USB Ethernet adapter detected by pfSense as `ue0` (WAN candidate)

This milestone corresponds to part of Phase 1 of
[checklists/production-router-cutover.md](../checklists/production-router-cutover.md) —
specifically, confirming that the planned WAN interface is visible to pfSense itself
(not just to the host). It is **detection only**, not a WAN assignment or cutover step.

What was done, with `pfsense-prod` booted **with the Realtek RTL8152 USB-to-Ethernet
adapter attached via USB passthrough** (still inside the safe, isolated lab topology —
no connection to the Cox modem):

- `ifconfig -l` showed a new interface, `ue0`, alongside the existing lab interfaces —
  confirming pfSense itself (not just the FreeBSD/host USB layer) recognizes the adapter
- `ifconfig ue0` showed:
  - media: `Ethernet autoselect (none)`
  - status: `no carrier`
  - MAC address present in the output (to be redacted in any published screenshot)
- The `no carrier` status is **expected and correct** — no Ethernet cable is currently
  connected to the adapter; this only confirms pfSense can see the interface, not that
  it is passing traffic
- `usbconfig` confirmed the device identifies as:
  - `RTL8152 Fast Ethernet Adapter`
  - `Realtek Semiconductor Corp.`
  - connected at `usbus3` (High Speed, 480 Mbps)

**What this proves — and does not yet prove:**

| Proven | Not yet attempted |
|---|---|
| pfSense detects the USB Ethernet adapter as a usable network interface (`ue0`) | `ue0` has not been assigned as WAN (or any role) inside pfSense |
| The adapter identifies correctly as the expected hardware (Realtek RTL8152) | The adapter has not been connected to the Cox modem or any live network |
| The interface is visible and inert — `no carrier`, no IP, no assignment | No interface-assignment changes were made inside pfSense |
| | The Cox modem/router, `eno1`, Netplan, Tailscale, Docker bridges, and the existing home network remain untouched |
| | The PoE switch is still not part of the live network |

**This is still pre-cutover.** This milestone proves only that `pfsense-prod` *can see*
the USB Ethernet adapter as a candidate WAN interface (`ue0`) while running in the safe
lab topology. No WAN assignment, physical cabling to the modem, or any other cutover
step has been attempted. **Status remains in progress / pre-cutover — not complete.**

### 2026-06-09 — LAN bridge test on `esther`: rollback safety mechanism verified (bridge attempt not kept)

This entry documents a **host-networking rollback drill**, not a pfSense milestone.
It tests the safety net that all later physical-cutover phases depend on — proving that
if a host-level network change goes wrong, it can be reversed automatically and the
host returns to a known-good state without requiring physical console intervention.

What was done, and what happened:

- A **draft Netplan bridge configuration** was prepared to (eventually) move `esther`'s
  host networking from `eno1` directly onto a future `br-lan` bridge interface
- Before applying it, a **rollback script and a systemd rollback timer** were prepared
  and staged — the explicit purpose being to auto-revert the change if remote access
  was lost, exactly as recommended in
  [rollback/production-router-rollback.md](../rollback/production-router-rollback.md)
- When the bridge configuration was applied as a test:
  - **Remote connectivity to `esther` temporarily dropped**
  - A Windows client briefly reported the host as unreachable via `ping`
- **The rollback timer fired as designed.** After it ran, `esther` became reachable
  again at its normal address, `192.168.0.24`
- Post-rollback verification confirmed a full return to the known-good state:
  - `eno1` restored with `192.168.0.24/24`
  - Default route restored: `192.168.0.1 dev eno1`
  - `/etc/netplan/50-cloud-init.yaml` restored to its original `eno1: dhcp4: true` form
  - No rollback timer remained active afterward (it had done its job and cleared itself)

**The bridge configuration was not kept.** This was a **test of the rollback mechanism
itself**, not an attempt to complete the LAN bridge migration — and the moment remote
connectivity dropped, the correct outcome was for the change to be reverted, which is
exactly what happened.

**What this proves — and does not yet prove:**

| Proven | Not yet attempted |
|---|---|
| A prepared rollback script + systemd timer can detect a bad host-network change and auto-revert it | The `br-lan` bridge has not been successfully brought up and kept |
| `esther` returns cleanly to its known-good `eno1`/DHCP/Netplan state after a failed change, with no manual recovery required | `eno1` has not been migrated to bridge mode |
| The rollback path restores the **exact** prior configuration — interface, IP, route, and Netplan file all matched the pre-test baseline | Physical NIC reassignment, Cox bridge mode, and PoE switch integration remain untouched |
| | `pfsense-prod` was not involved — it remained shut off throughout this test |

**This is still pre-cutover, and arguably more conservative than before:** rather than
moving forward with the bridge, this test deliberately proved the *exit path* works
first. That is the correct order of operations for any change this disruptive — know
your way back before you need it (see the Guiding Principle in
[rollback/production-router-rollback.md](../rollback/production-router-rollback.md)).
No physical cutover, Cox bridge-mode change, pfSense WAN/LAN reassignment, or PoE
switch integration occurred. **Status remains in progress / pre-cutover — not complete.**

### 2026-06-10 — `br-lan` host bridge created successfully on `esther` (host networking only — pfSense not yet involved)

This entry documents the **successful retry** of the LAN bridge change attempted in
the entry above — this time performed **with local monitor/keyboard access to `esther`
connected and verified beforehand**, exactly as the caution note added after the first
attempt recommended.

What was changed, and what happened:

- Netplan was changed from a direct `eno1: dhcp4: true` configuration to a **bridge**
  configuration:
  - `eno1` → `dhcp4: false` (no longer holds the host IP directly — now a bridge member)
  - `br-lan` → new bridge interface, with `eno1` as its member, `dhcp4: true`
- **SSH temporarily disconnected during `netplan apply`** — this was *expected* and
  matches the same brief interruption pattern observed (and safely recovered from) in
  the rollback drill above; this time, the change was kept because it came up correctly
- The host came back on a **new DHCP lease**:
  - `br-lan` received `192.168.0.28/24`
  - Default route is now via `192.168.0.1 dev br-lan`
- **Internet test:** `ping -c 4 1.1.1.1` → 4/4 received, 0% packet loss
- **DNS test:** `ping -c 4 google.com` → 4/4 received, 0% packet loss
- Tailscale remained active throughout
- The SSH service remained running (the disconnect was the network path changing under
  it, not the service failing)

**What this milestone proves — and what it explicitly does not:**

| Proven | Not yet attempted |
|---|---|
| `esther`'s host networking can run on a bridge (`br-lan`) with `eno1` as a member, instead of `eno1` holding the IP directly | No pfSense VM was started during this change |
| The bridge passes traffic correctly — internet routing and DNS both verified with 0% packet loss | No pfSense LAN interface has been attached to `br-lan` |
| Remote management (Tailscale, SSH) survives the transition to a bridged host network | The Cox modem/router has not been put into bridge/passive mode |
| The host returns to full connectivity on a new DHCP lease without manual recovery | No physical cutover or PoE switch/AP integration has occurred |

**This only moved host networking from `eno1` directly onto `br-lan` — it is not a
pfSense or production-router milestone by itself.** `br-lan` now exists and works as a
bridge on the host, which is a *prerequisite* for eventually attaching a pfSense LAN
interface to it — but that attachment, and everything that depends on it (pfSense LAN
cutover, WAN assignment, Cox bridge mode, physical cutover), **has not happened yet**.
**Status remains in progress / pre-cutover — not complete.**

---

## Current Lab State (Recap)

| Item | State |
|---|---|
| Host | `esther` — Lenovo ThinkCentre M82, Ubuntu 24.04 LTS |
| KVM/libvirt | Installed and verified |
| Lab VM | `pfsense-lab` — running, 2 vCPU / 2048 MB, snapshot `fresh-install` exists |
| Test VM | `test-client` — used for connectivity + firewall rule validation |
| Storage pools | `nvme-vms` → `/mnt/fast-storage/vms/`, `nvme-isos` → `/mnt/fast-storage/isos/` |
| Lab disk | `/mnt/fast-storage/vms/pfsense-lab.qcow2` |
| Lab networks | `default`/`virbr0` (NAT, `192.168.122.0/24`) as WAN; `pfsense-lab-lan`/`virbr-pflan` (isolated, `10.50.0.0/24`) as LAN |
| Lab pfSense LAN IP | `10.50.0.1/24` |
| Validation | Firewall rule test passed — see [docs/10-pfsense-lab-validation.md](10-pfsense-lab-validation.md) |
| `virt-clone` | Installed and available |

---

## Why `pfsense-lab` Should Be Preserved

`pfsense-lab` is **documented portfolio evidence** — its dashboard, firewall rules, and
the validated rule-blocking test are referenced directly in screenshots 13–19 and in
`docs/10-pfsense-lab-validation.md`. Modifying or repurposing it would invalidate that
evidence trail and the reproducibility of the milestone.

It also remains useful as a **safe sandbox** going forward: any new pfSense feature,
package, or rule idea can be tested against `pfsense-lab` in its fully isolated
network (`pfsense-lab-lan`, no physical NICs, no route to the production LAN) without
any risk to the home network — the same property that made the original validation safe.

**Rule: `pfsense-lab` is not modified, cloned-from-and-discarded, or used as the basis
for the production VM's live configuration.** It stays exactly as documented.

---

## Why `pfsense-prod` Should Be a Separate VM

A new VM, **`pfsense-prod`**, will be created (via `virt-clone`, which is already
installed) specifically for the production-router role. Reasons for keeping it separate
from `pfsense-lab` rather than repurposing the lab VM:

1. **Evidence integrity** — `pfsense-lab` stays exactly as captured in the existing
   screenshots and validation doc; nothing about the completed milestone changes.
2. **Safe iteration** — `pfsense-prod` can be booted, configured, broken, and reverted
   via snapshots without any risk of corrupting the lab proof-of-concept.
3. **Clear separation of concerns** — the lab VM answers "does pfSense work and enforce
   rules correctly in an isolated environment?" (already proven). The prod VM answers
   "can pfSense run as the actual home router?" — a different question with different
   risk, different NIC requirements, and a different lifecycle.
4. **Reversibility** — if the production cutover attempt fails or needs to be rolled
   back, `pfsense-prod` can be powered off or deleted entirely, and the home network
   returns to its current state, with `pfsense-lab` completely unaffected either way.

---

## Current Host / Interface Findings (as documented, read-only)

| Interface | Role today | Notes |
|---|---|---|
| `eno1` | Built-in Intel Ethernet — **active management path** | Currently carries `esther`'s LAN IP, default route, and remote-access traffic. Must not be altered while it is the active path. |
| `enx5c857e3c904d` | USB-to-Ethernet adapter (Realtek RTL8152, Fast Ethernet) | Currently down/unused. Candidate for pfSense production WAN. Likely capped near 100 Mbps. |
| `tailscale0` | Tailscale VPN tunnel | Must remain undisturbed — it is the documented out-of-band fallback access path (see [rollback/networking-rollback-procedures.md](../rollback/networking-rollback-procedures.md)). |
| Docker bridges | Container networking | Present and unrelated to this migration — not to be modified. |

---

## Target Physical Topology (Planned — Not Yet Built)

```
Cox modem/router (to be switched to bridge/passive mode — LAST, after pfSense is verified)
        │
        │ WAN
        ▼
USB-to-Ethernet adapter (enx5c857e3c904d, Realtek RTL8152)
        │
        ▼
pfSense production VM (pfsense-prod) on esther (Lenovo ThinkCentre M82)
        │
        │ LAN
        ▼
Built-in Intel Ethernet (eno1)
        │
        ▼
PoE VLAN-capable switch
        │
   ┌────┴─────────────────┐
   ▼                      ▼
Cisco AP             Deco AP (satellite — TV / PlayStation wired bridge)
(main Wi-Fi, future VLAN SSIDs)
```

This is the **end-state design**. It will be reached gradually, in the phases described
below — not in a single cutover.

---

## Planned WAN / LAN Assignment

| Role | Interface | Rationale |
|---|---|---|
| **WAN** | `enx5c857e3c904d` (USB-to-Ethernet, Realtek RTL8152) | Keeps the built-in NIC — and therefore `esther`'s current management path — untouched until the very end of the migration. The USB adapter is currently unused, so assigning it to WAN carries zero risk to the existing LAN connection. |
| **LAN** | `eno1` (built-in Intel Ethernet) | Becomes the production LAN uplink to the PoE switch only *after* pfSense is fully verified and ready for cutover — at which point `esther`'s own management traffic will ride through pfSense's LAN side rather than the ISP router directly. |

This assignment is intentionally chosen so that the **interface currently providing
remote access (`eno1`) is the last thing touched**, and only once pfSense has been
proven safe in a non-production topology first.

---

## Cisco AP and Deco AP Roles

| Device | Planned role |
|---|---|
| **Cisco access point** | Becomes the **main Wi-Fi AP**, eventually configured with VLAN-capable SSIDs (trunk port on the PoE switch). This is the long-term primary wireless device. |
| **Deco system** | Already in **AP mode** (not router mode) — stays that way. Used mainly as a **wireless bridge for the TV and PlayStation**, since the second Deco satellite unit conveniently provides wired Ethernet ports away from the main router/switch location. |
| **TV / PlayStation** | Stay wired into the Deco satellite unless real-world testing later shows the Cisco AP's Wi-Fi performs as well or better — at which point they could move to a wired or wireless connection through the new switch/AP instead. |

See [docs/12-vlan-switch-and-ap-design.md](12-vlan-switch-and-ap-design.md) for the
longer-term VLAN and switch-port plan involving these devices.

---

## Safety Rules (Hard Requirements Before Any Physical Change)

These rules govern the entire migration and must not be skipped or reordered:

1. **Do not put the Cox modem/router into bridge/passive mode** until `pfsense-prod`
   is fully installed, configured, and verified working in a safe (non-production) topology.
2. **Do not change `eno1`** while it remains the active management path to `esther`.
3. **Do not disrupt Tailscale** (`tailscale0`) — it is the documented out-of-band
   fallback access method and must stay independent of any routing change being tested.
4. **Do not attach physical NICs to `pfsense-prod`** until the VM has been verified
   safely in an isolated/lab-style network — exactly as `pfsense-lab` was originally
   verified before any rule testing began.
5. **Do not modify `pfsense-lab`** — it remains the preserved portfolio evidence VM.
6. **Always work from a clone** — `pfsense-prod` is created via `virt-clone` from
   `pfsense-lab`'s install baseline (or built fresh from the same verified ISO), never
   by repurposing the lab VM itself.
7. **Snapshot `pfsense-prod` before every physical NIC change.**
8. **Write down rollback steps before cutover, not during an outage** — see
   [rollback/production-router-rollback.md](../rollback/production-router-rollback.md).

---

## Step-by-Step Migration Phases (Planning Overview)

> Full checkbox-level detail lives in
> [checklists/production-router-cutover.md](../checklists/production-router-cutover.md).
> This section gives the narrative shape of the plan.

1. **Pre-change documentation** — capture the current host/interface/network baseline
   (read-only commands only) so there is a known-good snapshot to compare against and
   roll back to.
2. **Host/interface verification** — confirm `eno1` is the active management path,
   confirm `enx5c857e3c904d` is detected and down/unused, confirm Tailscale is healthy.
3. **Clone `pfsense-lab` → `pfsense-prod`** using `virt-clone`, producing an independent
   disk and VM definition with no shared state with the lab VM.
4. **Boot `pfsense-prod` in lab mode** — attached only to isolated/NAT libvirt networks
   (mirroring the original `pfsense-lab` topology), with **no physical NICs attached**,
   to confirm it boots cleanly and the GUI is reachable as an independent VM.
5. **Snapshot `pfsense-prod`** at this known-good "boots clean, no physical NICs" state.
6. **Plan physical NIC assignment** — document (on paper/in this repo) exactly which
   host interface maps to which pfSense interface (WAN = USB adapter, LAN = `eno1`)
   before making any libvirt or VM changes.
7. **Prepare the PoE VLAN-capable switch** — basic configuration (no VLANs yet —
   see [docs/12-vlan-switch-and-ap-design.md](12-vlan-switch-and-ap-design.md))
   so it is ready to receive a LAN uplink.
8. **Prepare the Cisco AP** — basic management access confirmed, ready to be plugged
   into the new LAN once it exists.
9. **Keep the Deco in AP mode** for the TV/PlayStation wired bridge throughout — no
   changes to its mode or role during this phase.
10. **Snapshot again immediately before the first physical NIC attachment.**
11. **Test LAN and Wi-Fi incrementally** — bring devices onto the new pfSense LAN
    segment gradually, verifying connectivity at each step before adding the next.
12. **ISP bridge/passive-mode cutover** — the final step, only performed once
    `pfsense-prod` has been fully verified end-to-end on the new LAN.
13. **Validation** — confirm internet access, DNS, internal routing, and that
    `esther`'s own management path (now via pfSense's LAN) remains reachable.
14. **Rollback readiness** — confirmed at every phase, not just at the end (see the
    dedicated rollback document).

---

## Evidence / Screenshot Plan

The following screenshots are **planned** for this phase (none have been captured yet —
no fake or placeholder images will be created). They continue the existing numbering
from the lab milestone (`16`–`19`):

| # | Filename | What it will show |
|---|---|---|
| 20 | `20-host-network-interfaces-before-cutover.png` | Baseline `ip -br link`/`ip -br addr` showing `eno1` active, USB adapter down, Tailscale present |
| 21 | `21-pfsense-lab-running-before-clone.png` | Proof `pfsense-lab` is untouched and running before the clone is made |
| 22 | `22-pfsense-prod-clone-created.png` | `virt-clone` output / `virsh list --all` showing both VMs exist independently |
| 23 | `23-pfsense-prod-first-boot.png` | `pfsense-prod` booting cleanly as an independent VM |
| 24 | `24-pfsense-prod-safe-lab-network-verified.png` | `pfsense-prod` reachable and working on an isolated/NAT network, no physical NICs attached |
| 25 | `25-usb-ethernet-detected.png` | Host confirming the Realtek RTL8152 USB adapter is detected and ready |
| 26 | `26-switch-vlan-plan.png` | PoE switch configuration/plan screen (basic setup, pre-VLAN) |
| 27 | `27-cisco-ap-management-access.png` | Cisco AP reachable via its management interface |
| 28 | `28-pfsense-prod-snapshot-before-physical-nic-change.png` | `virsh snapshot-list pfsense-prod` showing the pre-physical-NIC snapshot |
| 29 | `29-physical-nic-assignment-planned.png` | Documented mapping of host interfaces to pfSense WAN/LAN roles before the change is made |
| 30 | `30-final-topology-after-cutover.png` | Final working topology once cutover is complete and validated |

These will be added to `screenshots/README.md` with full descriptions and redaction
notes as each one is actually captured — see the redaction checklist at the end of
this document and in [docs/12-vlan-switch-and-ap-design.md](12-vlan-switch-and-ap-design.md).

---

## Rollback Planning

Full rollback procedures live in
[rollback/production-router-rollback.md](../rollback/production-router-rollback.md).
In summary, the guiding principle is the same one used throughout this project:
**know your exit before you enter.** Every phase of the cutover has a corresponding
"how do I undo this" answer written down *before* the phase is attempted — including
restoring the Cox modem/router to normal mode, reconnecting the previous network path,
powering off `pfsense-prod`, and reverting to a snapshot — all without depending solely
on a network path that the change itself might break.

---

## Risks and Future Improvements

| Risk | Notes / Mitigation |
|---|---|
| USB Ethernet WAN throughput | Realtek RTL8152 is Fast Ethernet (likely ~100 Mbps max). Probably fine for current Cox "basic" internet tiers, but a future bottleneck if the ISP plan is upgraded. **Future improvement:** migrate WAN to a PCIe NIC. |
| USB WAN reliability | USB links are generally less reliable than onboard/PCIe NICs (power management, enumeration on boot, physical connector wear). Documented here as a **known tradeoff**, to be revisited once the design is stable. **Future improvement:** PCIe multi-NIC card for both WAN and LAN. |
| Single point of failure | Once cutover is complete, `esther` becomes the home router — if it's down, the whole house loses internet/LAN routing. **Mitigation:** keep the rollback path fast (power off `pfsense-prod`, restore previous direct-to-ISP path) and consider a cold-spare plan long term. |
| VLAN complexity | Planned VLAN segmentation (Trusted/Lab/IoT/Guest/Management) adds configuration surface area. **Mitigation:** explicitly sequenced *after* basic routing and Wi-Fi are proven — see [docs/12-vlan-switch-and-ap-design.md](12-vlan-switch-and-ap-design.md). |
| Wireless performance unknowns | Whether the Cisco AP outperforms the Deco for TV/PlayStation traffic is untested. **Mitigation:** keep devices on the Deco wired bridge until real-world testing justifies a change. |

---

## Interview Talking Points

```
• Designed a phased migration plan to move a virtualized pfSense firewall from an
  isolated lab environment to a production home-router role — emphasizing
  reversibility, evidence preservation, and zero-downtime risk management at each step

• Applied a "clone, don't repurpose" strategy using virt-clone to separate a
  portfolio-validated lab VM from a production candidate VM, preserving prior
  test evidence while enabling safe iteration on the new role

• Planned a WAN/LAN interface assignment strategy that deliberately sequenced
  changes to protect the active remote-management path until last, minimizing
  the risk of self-inflicted lockout during a router cutover

• Documented rollback procedures and go/no-go gates before attempting any
  physical network change — including ISP modem bridge-mode cutover, snapshot
  recovery, and out-of-band access preservation via Tailscale

• Designed a forward-looking VLAN segmentation plan (Trusted/Lab/IoT/Guest/
  Management) sequenced to follow — not precede — basic routing and Wi-Fi
  validation, reducing combined-change risk during initial deployment
```

---

## Notes on Repo Privacy

This document — and the rest of `homelab/pfsense-virtualization-lab/` — currently lives
in a **private working repository**. Internal IPs, interface names, hardware identifiers,
and topology details are recorded in full here for planning accuracy. Before any of this
material (including future screenshots 20–30) is published or made public, it will be
sanitized following the same redaction approach already used for screenshots 11–19
(see `screenshots/README.md` and the redaction notes below).

### Redaction Notes for Future Public Screenshots (20–30)

Before committing any of the planned screenshots publicly, blur or redact:

- Public IP addresses
- MAC addresses
- Tailscale IPs (`100.x.x.x`)
- IPv6 addresses
- Serial numbers
- Tokens, keys, and passwords
- Sensitive hostnames
- Unnecessary internal network details (e.g., exact subnet layouts beyond what's needed to make the point)
