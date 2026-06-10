# Screenshots — Evidence Collection Index

Screenshots serve as proof-of-work for your portfolio. Each entry describes what to capture,
why it matters professionally, and what (if anything) to blur.

All images live in `screenshots/final/`.

---

## Captured ✅

### 01 — UFW Active Status ✅
**Captured:** 2026-05-29  
**Command:** `sudo ufw status verbose`  
**Why:** Core evidence of firewall deployment. Shows deny-by-default policy, named rules,
LAN-scoped Samba, and Tailscale WireGuard integration — all visible in one screenshot.  
**Blur:** Nothing sensitive.  
**File:** `screenshots/final/01-ufw-active-status.png`

---

### 02 — Security Baseline Before Hardening ✅
**Captured:** 2026-05-29  
**Commands:** `docker ps -a`, `sudo sshd -T | grep -E "passwordauthentication|permitrootlogin|port"`,
`sudo testparm --suppress-prompt | grep -E "map to guest|usershare"`  
**Why:** Documents the security findings at audit time — open password auth, permissive Samba guest
config, exited containers. Shows you identified problems before fixing them. Paired with
post-hardening screenshots, this demonstrates a complete security improvement cycle.  
**Blur:** Nothing sensitive.  
**File:** `screenshots/final/02-security-baseline-before-hardening.png`

---

### 03 — Docker Cleanup Complete ✅
**Captured:** 2026-05-29  
**Command:** `docker ps -a`  
**Why:** Before/after pair with screenshot 02. Screenshot 02 shows two exited orphan containers.
This one shows they are gone and both production containers (Jellyfin, Portainer) remain healthy.
Demonstrates active environment maintenance, not just initial setup.  
**Blur:** Nothing sensitive.  
**File:** `screenshots/final/03-docker-cleanup-complete.png`

---

### 04 — Samba Services After Hardening ✅
**Captured:** 2026-05-29  
**Command:** `sudo systemctl status smbd nmbd`  
**Why:** Verifies smbd and nmbd are active and running after changing `map to guest = Never` and
`usershare allow guests = No`. Paired with screenshot 02 (baseline), this shows a complete
before/after security improvement cycle for Samba guest authentication.  
**Blur:** Nothing sensitive.  
**File:** `screenshots/final/04-samba-services-after-hardening.png`

---

### 05 — SSH Key Generated ✅
**Captured:** 2026-05-29  
**Command:** Windows PowerShell — `ssh-keygen -t ed25519 -C "trea-homelab"`  
**Why:** Documents the key generation step. Shows ED25519 algorithm choice and key fingerprint.
Part of the three-screenshot SSH hardening evidence set.  
**Blur:** Full key fingerprint and randomart optional — neither is sensitive.  
**File:** `screenshots/final/05-ssh-key-generated.png`

---

### 06 — SSH Key Auth Success (Pre-Hardening) ✅
**Captured:** 2026-05-29  
**Command:** `ssh -i $env:USERPROFILE\.ssh\id_ed25519 <username>@100.x.x.x`  
**Why:** Proves key-based login was verified working before password auth was disabled —
the critical safety step that prevents lockout. This is Session 2 of the three-session
verification sequence.  
**Blur:** Tailscale IP (100.x.x.x) — blur if preferred.  
**File:** `screenshots/final/06-ssh-key-auth-success.png`

---

### 07 — SSH Key-Only Enforced ✅
**Captured:** 2026-05-29  
**Command:** `sudo sshd -T | grep passwordauthentication` + `sudo systemctl status ssh`  
**Why:** Confirms `passwordauthentication no` in the effective config after reload. This is
Session 3 — a new connection post-reload proving the change is active and key auth still
works. The before/after pair with screenshot 02 shows the full SSH hardening cycle.  
**Blur:** Nothing sensitive.  
**File:** `screenshots/final/07-ssh-key-only-enforced.png`

---

### 08 — Tailscale Status ✅
**Captured:** 2026-06-01  
**Command:** `tailscale status`  
**Why:** Shows zero-trust remote access is active. Confirms server is enrolled in the
tailnet with a live WireGuard tunnel — no port forwarding required.  
**Blur:** Tailscale IP addresses (100.x.x.x) — blur if preferred.  
**File:** `screenshots/final/08-tailscale-status.png`

---

### 09 — Storage Architecture ✅
**Captured:** 2026-06-01  
**Command:** `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT && echo "---" && df -hT | grep -v tmpfs`  
**Why:** Shows dual-storage architecture (SATA HDD with LVM + NVMe), a real sysadmin concept.
Confirms both drives are mounted and sized correctly, matching the written baseline.  
**Blur:** Nothing sensitive.  
**File:** `screenshots/final/09-storage-architecture.png`

---

### 10 — Unattended-Upgrades Running ✅
**Captured:** 2026-06-01  
**Command:** `sudo journalctl -u unattended-upgrades --no-pager | tail -20`  
**Why:** Proves automated patch management — shows actual upgrade execution logged by systemd.  
**Blur:** Nothing sensitive.  
**File:** `screenshots/final/10-unattended-upgrades-log.png`

---

### 11 — kvm-ok Verification ✅
**Captured:** 2026-06-02  
**Commands:** `grep -o 'vmx\|svm' /proc/cpuinfo`, `lscpu | grep -i virtualization`, `ls -la /dev/kvm`, `sudo kvm-ok`  
**Why:** Proves VT-x is active in BIOS and KVM acceleration is available to Ubuntu. Confirms
the BIOS gate is cleared and Phase 2 (libvirt installation) can proceed.  
**Blur:** IPv4 address (eno1 MOTD line), IPv6 address (eno1 MOTD line), and last-login
Tailscale source IP (100.x.x.x) — all blurred before committing.  
**File:** `screenshots/final/11-kvm-ok-verification.png`

---

### 12 — libvirt Install Verified ✅
**Captured:** 2026-06-02  
**Commands:** `groups`, `virsh list --all`, `sudo systemctl status libvirtd`  
**Why:** Composite proof of Phase 2 completion — shows libvirt + kvm group membership,
empty VM list (no stray VMs before pfSense creation), and libvirtd active/running status.  
**Blur:** Server LAN IP in ssh command (`192.168.0.24`) and source LAN IP in Last login
line (`192.168.0.14`) — both blurred before committing.  
**File:** `screenshots/final/12-libvirt-install-verified.png`

---

## Pending (After libvirt Install)

---

### 15 — virsh VM Running Verified ✅
**Captured:** 2026-06-02  
**Commands:** `virsh list --all`, `virsh dominfo pfsense-lab`, `virsh domiflist pfsense-lab`  
**Why:** Composite proof of Phase 6 — VM running, correct resources (2 vCPU/2 GB), correct NIC
mapping (vnet0→default WAN, vnet1→pfsense-lab-lan LAN), AppArmor enforcing, autostart disabled.  
**Blur:** Tailscale IP in SSH tunnel command, UUID value, AppArmor security label string,
both vnet0 and vnet1 MAC addresses — all blurred. Proof lines intact.  
**File:** `screenshots/final/15-virsh-vm-running.png`

---

### 13 — pfSense Dashboard ✅
**Captured:** 2026-06-02  
**URL:** `https://127.0.0.1:8443` — SSH tunnel to pfSense LAN GUI at `10.50.0.1`  
**Why:** Proves pfSense CE 2.8.1 is installed and running in KVM with correct WAN/LAN
assignment and internet connectivity. Shows real firewall appliance management.  
**Blur:** Netgate Device ID, user source IP (`admin@10.50.0.2`), all DNS server IPs
(`127.0.0.1`, `::1`, `192.168.122.1`), WAN IP (`192.168.122.239`), LAN IP (`10.50.0.1`)
— all blurred. pfSense branding, version, KVM Guest, WAN/LAN status arrows intact.  
**File:** `screenshots/final/13-pfsense-dashboard.png`

---

## Pending (After pfSense GUI Setup)

---

### 14 — pfSense Firewall Rules ✅
**Captured:** 2026-06-02  
**Location:** pfSense → Firewall → Rules → LAN tab  
**Why:** Documents the default LAN firewall rule baseline before any hardening — shows the
three default rules (Anti-Lockout, Default allow IPv4, Default allow IPv6) that pfSense
ships with. Proof of working firewall GUI and understanding of default policy.  
**Blur:** None required — all source/destination values are pfSense built-in aliases
(`LAN Address`, `LAN subnets`, `*`) with no actual IPs, MACs, or sensitive identifiers.  
**File:** `screenshots/final/14-pfsense-firewall-rules.png`

---

### 15 — virsh VM Running Verified
**Commands:** `virsh list --all`, `virsh dominfo pfsense-lab`, `virsh domiflist pfsense-lab`  
**Why:** Composite proof of Phase 6 — VM running, correct resources (2 vCPU/2 GB), correct NIC
mapping (vnet0→default WAN, vnet1→pfsense-lab-lan LAN), AppArmor enforcing, autostart disabled.  
**Blur:** Tailscale IP in SSH tunnel command, VM UUID, MAC addresses (both NICs), AppArmor
security label string (contains UUID). Proof lines to keep: `pfsense-lab running`, CPU/RAM,
`autostart: disable`, vnet0/vnet1 source and model, disk path, `cdrom hda -`.  
**File:** `screenshots/final/15-virsh-vm-running.png`

---

## Milestone: Virtual Firewall Baseline + Rule Validation ✅

### 16 — Test Client Network Verified ✅
**Captured:** 2026-06-04  
**Commands:** `ip -br addr`, `ip route`, `ping -c 3 10.50.0.1`, `ping -c 3 8.8.8.8`, `ping -c 3 google.com`, `curl -k -I https://10.50.0.1`  
**Why:** Proves the Debian test-client VM received DHCP from pfSense (10.50.0.100/24),
gateway is 10.50.0.1, internet works through pfSense NAT, DNS resolves, and pfSense GUI
is reachable (HTTP/2 200) — end-to-end virtual lab connectivity confirmed.  
**Blur:** IPv6 address on enp1s0, CDN IP in google.com ping output, PHPSESSID session
token in curl set-cookie header — all blurred. Lab IPs 10.50.0.100/10.50.0.1 retained.  
**File:** `screenshots/final/16-test-client-network-verified.png`

---

### 17 — Firewall Rule Test Result ✅
**Captured:** 2026-06-04  
**Source:** TigerVNC session to Debian test-client VM  
**Why:** Proves selective firewall enforcement: 8.8.8.8 ping blocks with 100% loss when
the block rule is active, while google.com (DNS) and 10.50.0.1 (gateway) remain
reachable — demonstrating per-protocol, per-destination rule precision.  
**Blur:** CDN IP `74.125.136.139` in google.com ping output — blurred. Ping pass/fail
results, gateway reachability, and TigerVNC window title intact.  
**File:** `screenshots/final/17-firewall-rule-test-result.png`

---

### 18 — pfSense LAN Rule Created ✅
**Captured:** 2026-06-04  
**Location:** pfSense → Firewall → Rules → LAN  
**Why:** Shows the block rule was explicitly created in pfSense — IPv4 ICMP from test
client to 8.8.8.8, enabled (red X), alongside the default allow rules. Pairs with
screenshot 17 as the firewall-side proof of the rule that caused the observed blocking.  
**Blur:** Source IP in block rule row — blurred. Rule description, action icon, protocol,
and destination `8.8.8.8` intact.  
**File:** `screenshots/final/18-pfsense-lan-rule-created.png`

---

### 19 — pfSense WAN Rules Baseline ✅
**Captured:** 2026-06-04  
**Location:** pfSense → Firewall → Rules → WAN  
**Why:** Optional supporting context — shows WAN default-deny posture: RFC 1918 and bogon
block rules, no inbound pass rules. Confirms the WAN side is not open to unsolicited traffic.  
**Blur:** None required — only generic source labels (RFC 1918 networks, Reserved/Not
assigned by IANA), no actual IPs, MACs, or credentials.  
**File:** `screenshots/final/19-pfsense-wan-rules-baseline.png`

---

## Planned — Production Router Migration

These screenshots support the production router migration phase
(see [docs/11-production-router-migration.md](../docs/11-production-router-migration.md)
and [checklists/production-router-cutover.md](../checklists/production-router-cutover.md)).

**Status note (2026-06-08, updated 2026-06-07):** the underlying technical milestones
for screenshots 21–25 and 28 — clone created, booted in safe lab mode, **functionally
validated end-to-end with a Debian `test-client`** (DHCP, gateway, internet routing, and
DNS all passing with 0% packet loss), two snapshots captured (`safe-clone-baseline` and
`safe-lab-validated`), and the **Realtek RTL8152 USB-to-Ethernet adapter detected by
pfSense itself as `ue0`** — have now been **completed and verified at the terminal**.
In particular, the evidence underlying screenshot **24** (safe-lab-network verification),
screenshot **25** (USB Ethernet detection — `ue0` visible in pfSense, `usbconfig`
confirms the Realtek hardware), and the snapshot-evidence underlying screenshot **28**
are now considered **ready to capture** — the terminal output exists and has been
reviewed; it just needs to be saved as redacted `.png` files in this directory.
**No actual screenshot image files have been captured or saved yet** for any of
20–30 — the table below still reflects what each one *will* document. No placeholders
or fake screenshots have been created. Each row will be updated with a real filename
entry, full description, and redaction confirmation only once the corresponding `.png`
exists in `screenshots/final/`.

**Additional evidence ready/captured — LAN bridge rollback test (2026-06-09):** the
terminal evidence for the host-level Netplan bridge rollback drill on `esther` (draft
`br-lan` bridge config applied as a test, remote connectivity briefly dropped, prepared
systemd rollback timer auto-restored `eno1` to `192.168.0.24/24` with its original
DHCP Netplan config and default route) is **ready/captured** — see
[docs/11-production-router-migration.md](../docs/11-production-router-migration.md#progress-log)
and the new tested case in
[rollback/production-router-rollback.md](../rollback/production-router-rollback.md).
This event is **not** on the original #20–30 list (it's a host-networking rollback
drill, not a pfSense/VM milestone), so no screenshot filename or row has been assigned
to it here yet. **The raw terminal captures for this event contain `esther`'s real LAN
IP (`192.168.0.24`), gateway (`192.168.0.1`), and Netplan/interface details and MUST be
redacted** (per the existing internal/external-IP and identifier redaction notes below)
**before any public use** — no image file has been saved or committed.

**Additional evidence ready/captured — successful `br-lan` host bridge milestone
(2026-06-10):** the terminal evidence for the *successful* retry of the host bridge
change — performed with local console access available, per the caution raised after
the rollback drill above — is **ready/captured**. This includes the Netplan bridge
config (`eno1: dhcp4: false`, `br-lan` with `eno1` as member, `dhcp4: true`), the new
DHCP lease (`br-lan` → `192.168.0.28/24`, default route `192.168.0.1 dev br-lan`), and
the internet/DNS verification (`ping -c 4 1.1.1.1` and `ping -c 4 google.com`, each
4/4 received, 0% packet loss). See
[docs/11-production-router-migration.md](../docs/11-production-router-migration.md#progress-log)
and the new known-good bridge state recorded in
[rollback/production-router-rollback.md](../rollback/production-router-rollback.md).
Like the rollback-drill evidence above, this event is **not** on the original #20–30
list and has no assigned filename/row. **Before any public use, the raw captures MUST
be redacted for: MAC addresses (bridge/member-interface MACs shown in `ip -br link`
or `bridge link` output), IPv6 addresses (alongside the IPv4 lease in `ip -br addr`),
Tailscale IPs (`100.x.x.x`), and internal IPs (`192.168.0.28`, `192.168.0.1`,
`esther`'s LAN subnet)** — consistent with the redaction precedents already established
for screenshots 15, 16, and 22. **This milestone proves the host bridge works — it
does not mean pfSense is the home router yet; no pfSense interface is attached to
`br-lan`.** No image file has been saved or committed.

| # | Filename | Will document | Evidence status |
|---|---|---|---|
| 20 | `20-host-network-interfaces-before-cutover.png` | Baseline interface state — `eno1` active, USB adapter down, Tailscale present | Not yet captured |
| 21 | `21-pfsense-lab-running-before-clone.png` | Proof `pfsense-lab` is untouched and running before cloning | Underlying state confirmed (lab VM shut off/untouched) — image not yet captured |
| 22 | `22-pfsense-prod-clone-created.png` | `virt-clone` output / `virsh list --all` showing both VMs as independent entities | Terminal evidence reviewed (`virsh domiflist`/`domblklist pfsense-prod`, `virsh list --all` showing `pfsense-prod running` / `pfsense-lab shut off`) — image not yet captured |
| 23 | `23-pfsense-prod-first-boot.png` | `pfsense-prod` booting cleanly as its own VM | VM confirmed running — GUI/first-boot screenshot not yet captured |
| 24 | `24-pfsense-prod-safe-lab-network-verified.png` | `pfsense-prod` verified working on an isolated/NAT network, no physical NICs attached | **Ready to capture** — full functional validation completed via `test-client`: DHCP lease (`10.50.0.100/24`, gateway `10.50.0.1`), `ping -c 4 10.50.0.1` / `ping -c 4 1.1.1.1` / `ping -c 4 google.com` each 4/4 received, 0% loss; `ip -br addr` and `ip route` output reviewed at the terminal — image not yet saved as a file |
| 25 | `25-usb-ethernet-detected.png` | pfSense itself detecting the Realtek RTL8152 USB-to-Ethernet adapter as a WAN candidate (`ue0`) | **Ready to capture** — `pfsense-prod` booted with the adapter attached via USB passthrough; `ifconfig -l` shows `ue0`, `ifconfig ue0` shows `media: Ethernet autoselect (none)` / `status: no carrier` (expected, no cable connected), and `usbconfig` confirms `RTL8152 Fast Ethernet Adapter` / `Realtek Semiconductor Corp.` — detection only, `ue0` not assigned to any role; image not yet saved as a file |
| 26 | `26-switch-vlan-plan.png` | PoE switch basic configuration/plan (pre-VLAN) | Not yet attempted — switch not yet plugged in |
| 27 | `27-cisco-ap-management-access.png` | Cisco AP reachable via its management interface | Not yet attempted |
| 28 | `28-pfsense-prod-snapshot-before-physical-nic-change.png` | `virsh snapshot-list pfsense-prod` showing the pre-physical-NIC snapshot | **Snapshot evidence ready to capture** — `virsh snapshot-list pfsense-prod` now shows two verified, restorable snapshots (`safe-clone-baseline`, `safe-lab-validated`); note the *specific* pre-physical-NIC snapshot this filename refers to (Phase 9) has not been created yet — current snapshot evidence documents the pre-cutover baseline/validation state, not the pre-physical-NIC point specifically — image not yet saved as a file |
| 29 | `29-physical-nic-assignment-planned.png` | Documented WAN/LAN interface mapping before physical changes are made | Not yet attempted |
| 30 | `30-final-topology-after-cutover.png` | Final validated topology after cutover is complete | Not yet attempted — cutover has not started |

**Planned redactions for all of the above (before any public commit):** public IPs,
internal/external IPs, MAC addresses, Tailscale IPs, **IPv6 addresses**, serial numbers,
tokens/keys/passwords, sensitive hostnames, and unnecessary internal network details.

> ⚠️ **Specific notes for upcoming captures:**
> - **`virsh domiflist` output** (relevant to screenshot 22 and any future NIC-related
>   captures): includes the **MAC addresses** of each VM's virtual NICs (e.g.,
>   `vnet0`/`vnet1` entries for `pfsense-prod`). These **must be blurred or redacted**
>   before any such screenshot is committed publicly — consistent with how MAC
>   addresses were already handled in screenshot 15 (`virsh domiflist pfsense-lab`).
> - **`test-client` terminal output** (relevant to screenshot 24): `ip -br addr` shows
>   an **IPv6 address** alongside the IPv4 lease on `enp1s0` — this **must be blurred**
>   before public use, consistent with how the IPv6 address was redacted in screenshot 16
>   (`16-test-client-network-verified.png`). The lab IPv4 addresses (`10.50.0.100`,
>   `10.50.0.1`) and the public test destinations (`1.1.1.1`, `google.com`/`172.253.124.139`)
>   are not sensitive and may remain visible, matching the precedent set in screenshots
>   16 and 17 for the original lab validation.
> - **`ifconfig ue0` output** (relevant to screenshot 25 — USB Ethernet detection):
>   shows the adapter's **MAC address** directly in the output. This **must be blurred
>   or redacted** before public use, matching the precedent set in screenshots 15 and 22
>   for VM/interface MAC addresses. Unnecessary internal identifiers (e.g., the full
>   `usbusN`/`ugenN.N` enumeration lines for unrelated host USB controllers shown in
>   `usbconfig`) should also be cropped or blurred — only the Realtek RTL8152 entry and
>   the `ue0` interface lines are relevant to the story this screenshot tells.

---

## Screenshot Naming Convention

```
screenshots/final/[sequence]-[descriptor].png

Examples:
screenshots/final/01-ufw-active-status.png
screenshots/final/03-docker-cleanup-complete.png
screenshots/final/09-pfsense-dashboard.png
```

Use sequence numbers so screenshots sort in logical documentation order on GitHub.

---

## Tips for Portfolio Screenshots

1. **Use a clean terminal** — large font, dark theme, full-screen. VS Code integrated terminal works well.
2. **Show the prompt** — include your username and hostname in the screenshot. `<username>@esther:~$` is proof of context.
3. **Run commands right before screenshot** — shows fresh, live output not copy-pasted text.
4. **Include timestamps where possible** — `uptime`, log entries, and `date` output prove liveness.
5. **Annotate with arrows or boxes** (optional) — highlight key output in portfolio presentations.
