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

## Pending (After pfSense VM)

### 13 — pfSense Dashboard
**URL:** pfSense web GUI (via VNC-over-SSH or direct LAN)  
**Why:** Shows you can deploy and manage a real firewall appliance.  
**Blur:** Any WAN IP, license info, or network details depending on context.  
**File:** `screenshots/final/13-pfsense-dashboard.png`

---

### 14 — pfSense Firewall Rules
**Location:** pfSense → Firewall → Rules  
**Why:** Demonstrates firewall rule design — a core skill in networking and security roles.  
**Blur:** Any external IPs.  
**File:** `screenshots/final/14-pfsense-firewall-rules.png`

---

### 15 — virsh list --all (VM Running)
**Command:** `virsh list --all`  
**Why:** Shows KVM VM management from the CLI — relevant to cloud and infrastructure roles.  
**Blur:** Nothing sensitive.  
**File:** `screenshots/final/15-virsh-vm-running.png`

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
