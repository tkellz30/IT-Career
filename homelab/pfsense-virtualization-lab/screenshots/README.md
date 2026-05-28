# Screenshots — Evidence Collection Index

Screenshots serve as proof-of-work for your portfolio. Each entry describes what to capture,
why it matters professionally, and what (if anything) to blur.

---

## Completed / Ready to Capture

### 00 — UFW Inactive (Baseline)
**Command:** `sudo ufw status`  
**When:** Before UFW was enabled (historical — recreate if needed by temporarily disabling)  
**Why:** Establishes "before" state. Shows you documented problems, not just successes.  
**Blur:** Nothing sensitive.  
**File:** `00-ufw-inactive-baseline.png`

---

### 01 — UFW Active Status
**Command:** `sudo ufw status verbose`  
**When:** Now — UFW is active  
**Why:** Core evidence of firewall deployment. Shows named rules, LAN scoping, and VPN-aware config.  
**Blur:** Nothing sensitive.  
**File:** `01-ufw-active-status.png`

---

### 02 — System Overview (neofetch or htop)
**Command:** `neofetch` or `htop`  
**When:** Any time  
**Why:** Professional summary card — OS, kernel, uptime, RAM, CPU.  
**Blur:** Nothing sensitive.  
**File:** `02-system-overview.png`

---

### 03 — Docker Stack Running
**Command:** `docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"`  
**When:** Now — both containers up  
**Why:** Proves Docker administration: container lifecycle, port management, health checks.  
**Blur:** Nothing sensitive (ports are documentation, not secrets).  
**File:** `03-docker-stack-running.png`

---

### 04 — Tailscale Status
**Command:** `tailscale status`  
**When:** Now  
**Why:** Shows you implement zero-trust remote access, understand VPN concepts.  
**Blur:** Tailscale IP addresses (100.x.x.x) are semi-public within your tailnet — blur if preferred.  
**File:** `04-tailscale-status.png`

---

### 05 — Storage Architecture
**Command:** `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,LABEL && df -hT`  
**When:** Now  
**Why:** Shows dual-storage architecture (SATA HDD with LVM + NVMe), a real sysadmin concept.  
**Blur:** Nothing sensitive.  
**File:** `05-storage-architecture.png`

---

### 06 — Unattended-upgrades Running
**Command:** `sudo journalctl -u unattended-upgrades --no-pager | tail -20`  
**When:** Now  
**Why:** Proves automated patch management — shows actual upgrade execution (vim was upgraded May 26).  
**Blur:** Nothing sensitive.  
**File:** `06-unattended-upgrades-log.png`

---

## Pending (After BIOS Fix)

### 07 — kvm-ok Verified
**Command:** `sudo kvm-ok`  
**When:** After enabling VT-x in BIOS  
**Why:** Proves hypervisor capability. Strong signal for infrastructure roles.  
**Blur:** Nothing sensitive.  
**File:** `07-kvm-ok-verified.png`

---

### 08 — virt-host-validate All PASS
**Command:** `sudo virt-host-validate`  
**When:** After libvirt installed  
**Why:** Shows production-grade hypervisor configuration (IOMMU, KSM, etc.)  
**Blur:** Nothing sensitive.  
**File:** `08-virt-host-validate.png`

---

## Pending (After pfSense VM)

### 09 — pfSense Dashboard
**URL:** pfSense web GUI (via VNC-over-SSH or direct LAN)  
**Why:** Shows you can deploy and manage a real firewall appliance.  
**Blur:** Any WAN IP, license info, or network details depending on context.  
**File:** `09-pfsense-dashboard.png`

### 10 — pfSense Firewall Rules
**Location:** pfSense → Firewall → Rules  
**Why:** Demonstrates firewall rule design — a core skill in networking/security roles.  
**Blur:** Any external IPs.  
**File:** `10-pfsense-firewall-rules.png`

### 11 — virsh list --all (VM Running)
**Command:** `virsh list --all`  
**Why:** Shows KVM VM management from the CLI — relevant to cloud and infrastructure roles.  
**Blur:** Nothing sensitive.  
**File:** `11-virsh-vm-running.png`

---

## Screenshot Naming Convention

```
[sequence]-[descriptor].png

Examples:
01-ufw-active-status.png
03-docker-stack-running.png
09-pfsense-dashboard.png
```

Use sequence numbers so screenshots sort in logical documentation order on GitHub.

---

## Tips for Portfolio Screenshots

1. **Use a clean terminal** — large font, dark theme, full-screen. VS Code integrated terminal works well.
2. **Show the prompt** — include your username and hostname in the screenshot. `<username>@esther:~$` is proof of context.
3. **Run commands right before screenshot** — shows fresh, live output not copy-pasted text.
4. **Include timestamps where possible** — `uptime`, log entries, and `date` output prove liveness.
5. **Annotate with arrows or boxes** (optional) — highlight key output in portfolio presentations.
