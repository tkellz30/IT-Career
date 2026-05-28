# System Baseline — esther

**Audit Date:** 2026-05-27  
**Purpose:** Establish documented starting point before any changes; serves as rollback reference.

---

## System Identity

| Field | Value |
|---|---|
| Hostname | `esther` |
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | 6.8.0-117-generic |
| Uptime at audit | 5 days, 16h 38m |
| Last reboot | 2026-05-22 03:44 UTC |

---

## Hardware

| Component | Detail |
|---|---|
| CPU | Intel Core i5-3470 @ 3.20GHz |
| Cores / Threads | 4 cores / 4 threads (single socket, no HyperThreading) |
| Architecture | x86_64 |
| RAM Total | 7.6 GB |
| RAM Used (idle) | ~845 MB |
| Swap | 4.0 GB (0 used at audit) |
| **VT-x Status** | **DISABLED IN BIOS** — must enable for KVM |

---

## Storage Layout

```
sda (465.8 GB SATA HDD)
├── sda1   1 GB    vfat   /boot/efi
├── sda2   2 GB    ext4   /boot       (105 MB used, 6%)
└── sda3  462.7 GB LVM2_member
    └── ubuntu-vg-1-ubuntu-lv   100 GB ext4   /  (10 GB used, 11%)
        ⚠️  362 GB unallocated LVM space on sda3

nvme0n1 (931.5 GB NVMe SSD)
└── nvme0n1p1   931.5 GB ext4   /mnt/fast-storage   (28 GB used, 4%)
```

**Storage observations:**
- Root filesystem has 83 GB free — comfortable headroom
- NVMe has 842 GB free — primary media/data store
- 362 GB of LVM PV space unused (`lvextend` can reclaim this at any time)
- SMART health status could not be verified without `smartctl` sudo access

---

## Network Configuration

| Interface | Address | State | Purpose |
|---|---|---|---|
| `eno1` | 192.168.x.x/24 (DHCP) | UP | Primary LAN — Intel I217 |
| `tailscale0` | 100.x.x.x/32 | UP | Tailscale VPN (WireGuard) |
| `docker0` | 172.17.0.1/16 | UP | Docker default bridge |
| `br-b535ed00b51e` | 172.18.0.1/16 | UP | Jellyfin Docker network |
| `enx5c857e3c904d` | *(none)* | DOWN | USB Ethernet adapter — unused |

**Default route:** `192.168.x.1` via `eno1`

**IPv6:** Public address `<ipv6-redacted>` active on eno1

⚠️ **LAN IP is DHCP-assigned.** A lease change would break Samba share discovery and any LAN bookmarks. Assign a static DHCP reservation on your router.

---

## Running Services

### Docker Containers

| Name | Image | Status | Port |
|---|---|---|---|
| `jellyfin` | jellyfin/jellyfin | Up (healthy) | 8096/tcp |
| `portainer` | portainer/portainer-ce:latest | Up | 9443/tcp |

**Exited containers (cleanup needed):**
- `cool_feynman` — hello-world, exited 11 days ago
- `busy_noether` — hello-world, exited 11 days ago

### Docker Volumes
- `jellyfin_jellyfin_config`
- `jellyfin_jellyfin_cache`
- `portainer_data`

### Samba Shares

| Share Name | Path | Writable | Access |
|---|---|---|---|
| `Media` | `/home/<username>/media` → symlink to `/mnt/fast-storage/media` | Yes | <username> only |
| `FastStorage` | `/mnt/fast-storage` | Yes | <username> only |

**Note:** `Media` is a symlink — both shares resolve to the NVMe drive.

### System Services (key)

All critical services running, 0 failed:

```
containerd, docker, smbd, nmbd, ssh, tailscaled,
rsyslog, unattended-upgrades, systemd-networkd, cron
```

---

## Listening Ports (TCP) — Pre-UFW State

| Port | Service | Bound To |
|---|---|---|
| 22 | SSH | 0.0.0.0 (all) |
| 139 | Samba NetBIOS | 0.0.0.0 (all) |
| 445 | Samba SMB | 0.0.0.0 (all) |
| 8096 | Jellyfin (Docker) | 0.0.0.0 (all) |
| 9443 | Portainer (Docker) | 0.0.0.0 (all) |
| 53 | systemd-resolved | localhost only |

---

## Security Posture at Audit

| Control | State | Risk |
|---|---|---|
| UFW | **Inactive** | High — no inbound filtering |
| SSH password auth | Enabled | Medium |
| Samba `map to guest` | `Bad User` | Medium — permissive guest setting |
| Docker + firewall | Bypass active | Medium — Docker writes iptables directly |
| Unattended-upgrades | Active | ✅ Low risk |
| Root SSH | `without-password` only | ✅ Key-only for root |

---

## Screenshot Evidence

**Screenshot:** `ufw status` showing `inactive` (pre-hardening baseline)  
**File:** `screenshots/00-ufw-inactive-baseline.png`  
**Value:** Establishes "before" state for security improvement documentation
