# IT Career Portfolio — Michael Kelly

> Hands-on homelab portfolio — Linux servers, Docker containers, DNS filtering, and network configuration. Built on real hardware, documented as I went.

**CompTIA Network+** · **CompTIA Security+** · **CCNA in progress**

---

## About

I'm an IT support professional based in Pensacola, FL working toward network and systems administration. This repo documents the lab work I do outside of my day job — building an Ubuntu Server from scratch, managing Docker containers, configuring a managed switch over the serial console, and setting up Pi-hole DNS filtering on a Raspberry Pi.

Everything here ran on actual hardware. The troubleshooting logs are real problems I ran into and fixed.

**Preferred name:** Trea  
**Email:** michaeltkellyiii@gmail.com  
**LinkedIn:** [linkedin.com/in/trea-kelly-03b0352b4](https://linkedin.com/in/trea-kelly-03b0352b4)  
**GitHub:** [github.com/tkellz30/IT-Career](https://github.com/tkellz30/IT-Career)

---

## Featured Projects

### Ubuntu Server Homelab

A self-hosted server environment built on a repurposed Lenovo desktop running Ubuntu Server. The machine has no monitor or keyboard attached — everything is managed remotely over SSH and Tailscale. It runs Docker containers, serves media through Jellyfin, shares files over SMB, and has a separately mounted NVMe for storage.

**[→ Read the full homelab writeup](homelab/README.md)**

**What's running:**

| Service | What It Does |
|---------|-------------|
| Docker + Portainer | Container runtime with a browser-based management dashboard |
| Jellyfin | Self-hosted media server — streams to any device, no subscription |
| Tailscale | WireGuard VPN that makes the server reachable from anywhere without port forwarding |
| Samba | NVMe storage accessible as a mapped network drive from Windows |

**Architecture:**

```
┌──────────────────────────────────────────────────────────────┐
│                   Home Network (LAN)                         │
│                                                              │
│   ┌──────────────────────────────────────────────────────┐   │
│   │               Ubuntu Server — esther                 │   │
│   │                                                      │   │
│   │   SSH (port 22)          Tailscale (WireGuard VPN)   │   │
│   │                                                      │   │
│   │   Docker Engine                                      │   │
│   │   ├── Portainer ──────── ports 9000, 9443            │   │
│   │   └── Jellyfin  ──────── port 8096                   │   │
│   │                                                      │   │
│   │   Samba (SMB) ─────────── port 445                   │   │
│   │                                                      │   │
│   │   Storage                                            │   │
│   │   ├── sda  (465.8 GB SSD)  →  /  via LVM            │   │
│   │   └── nvme (931.5 GB NVMe) →  /mnt/fast-storage      │   │
│   └──────────────────────────────────────────────────────┘   │
│                                                              │
│   Windows PC ────── SMB ────── faststorage (\\esther) Z:     │
└──────────────────────────────────────────────────────────────┘

                 Tailscale overlay (100.x.x.x)
    ┌───────────────────────────────────────────────────┐
    │  esther  ←──── encrypted tunnel ────  any device  │
    └───────────────────────────────────────────────────┘
```

All remote access routes through Tailscale. No ports are exposed to the public internet.

---

#### Docker and Portainer

Docker Engine runs all services as isolated containers instead of installing them directly on the OS. Portainer provides a browser-based dashboard for managing those containers — start, stop, inspect, and remove without SSH-ing in every time.

![Portainer container dashboard showing Jellyfin as healthy and Portainer running on ports 9000 and 9443](screenshots/final/03-portainer-dashboard.png)

*Both containers up. Jellyfin reports as healthy (Docker health check passing). Accessible at the server's Tailscale address on port 9443.*

---

#### Jellyfin Media Server

Jellyfin is a self-hosted alternative to Plex — scans a library path, generates metadata, and streams to any browser or Jellyfin app. The library is stored on the NVMe at `/mnt/fast-storage/media`, keeping media off the OS drive.

![Jellyfin web interface with the Movies library populated and ready to stream](screenshots/final/04-jellyfin-library.png)

*Jellyfin home screen accessed through the browser. Library is populated and streaming from the NVMe. Reachable from any device on the Tailscale network.*

---

#### Remote Access with Tailscale

The server runs headless — no monitor, no keyboard. Tailscale creates a WireGuard VPN overlay so it's reachable by hostname from anywhere. Devices authenticate once and stay connected without manual reconnects or firewall rules.

![SSH login to the esther server showing Ubuntu MOTD with system stats and last login origin via Tailscale](screenshots/final/01-ssh-remote-login.png)

*The "Last login from" line in the Ubuntu login banner confirms the previous connection came over Tailscale. System stats show 0.02 load, 10% memory, 31°C.*

---

#### Persistent NVMe Storage

The NVMe drive mounts at `/mnt/fast-storage` using a UUID-based entry in `/etc/fstab`. UUIDs are stable — unlike `/dev/sdb`, which can change if drive detection order shifts at boot. The mount survives reboots without any manual steps.

![/etc/fstab showing two UUID-based persistent mount entries for /data and /mnt/fast-storage](screenshots/final/07-fstab-persistent-mounts.png)

*`/etc/fstab` with custom UUID entries. The `noatime` option on the NVMe reduces unnecessary write operations. Tested with `mount -a` before rebooting to verify no typos.*

---

#### Samba File Sharing

Samba makes the NVMe accessible as a standard Windows network drive. Configured the share in `/etc/samba/smb.conf`, added a Samba user, opened UFW for port 445, and mapped it as `Z:` on Windows — accessible directly in File Explorer.

![Windows File Explorer with the faststorage Samba share mounted as drive Z, server path \\esther visible](screenshots/final/08-samba-share-mounted.png)

*Samba share mapped as `Z:`. The address bar confirms the server hostname and share name. All storage folders are accessible from Windows without extra software.*

---

#### Managed Switch / VLAN Lab

Configured a VLAN on a physical ADTRAN NetVanta 1224ST managed switch using the serial console — the same out-of-band method used when a switch has no IP management interface configured yet. Created VLAN 20, assigned an access port, verified before and after with `show vlan brief`, saved with `write memory`.

This is documented in detail in the [homelab README](homelab/README.md#managed-switch--vlan-lab).

---

### Pi-hole DNS Filtering Lab

A network-wide DNS sinkhole running on a Raspberry Pi with Unbound as a recursive upstream resolver. Blocks ads and tracking domains for every device on the network — no client software required. Includes documentation for TP-Link Deco mesh integration and router/AP mode troubleshooting.

**[→ Read the Pi-hole lab writeup](homelab/pihole-dns-filtering-lab/README.md)**

![Pi-hole admin dashboard showing total queries, blocked percentage, and domains on blocklist](homelab/pihole-dns-filtering-lab/screenshots/final/01-pihole-dashboard-sanitized.png)

*Pi-hole admin dashboard. The query log tracks DNS lookups in real time — blocked requests are dropped before they leave the network.*

---

## Technologies Used

**Operating Systems:** Ubuntu Server · Raspberry Pi OS  
**Remote Access:** SSH · Tailscale (WireGuard)  
**Containerization:** Docker Engine · Portainer  
**Services:** Jellyfin · Pi-hole · Unbound  
**File Sharing:** Samba (SMB)  
**Networking:** VLANs · Managed Switch CLI · DNS · TCP/IP  
**Storage:** LVM · `/etc/fstab` · NVMe · `blkid`  
**Shell:** Bash  
**Version Control:** Git · GitHub  
**Scripting:** Python (screenshot redaction pipeline)

**Certifications:** CompTIA Network+ · CompTIA Security+  
**In Progress:** CCNA

---

## Repository Structure

| Folder | Contents |
|--------|----------|
| [`homelab/`](homelab/) | Main homelab project — Ubuntu Server, Docker, Tailscale, Samba, VLAN lab |
| [`homelab/pihole-dns-filtering-lab/`](homelab/pihole-dns-filtering-lab/) | Pi-hole + Unbound recursive DNS on Raspberry Pi |
| [`screenshots/final/`](screenshots/final/) | Portfolio-ready screenshots (reviewed and redacted) |
| [`resume/`](resume/) | Current resume |

---

## Current Learning Roadmap

**Completed:**
- Ubuntu Server setup and administration
- SSH remote access (headless server management)
- Docker Engine and container management (Portainer, Jellyfin)
- Persistent storage configuration with `/etc/fstab` and UUIDs
- Samba SMB file sharing
- Tailscale WireGuard VPN for remote access
- Pi-hole DNS sinkhole with Unbound recursive resolver
- Managed switch VLAN configuration via serial console (ADTRAN NetVanta)
- CompTIA Network+ ✓
- CompTIA Security+ ✓

**In Progress:**
- CCNA lab work (subnetting, routing protocols, switching)
- Network segmentation and VLAN trunking

**Up Next:**
- pfSense firewall — deployment and configuration
- Monitoring stack — Uptime Kuma or Grafana + Prometheus
- Docker Compose migration for reproducible container definitions
- Log aggregation and SIEM tooling (Graylog or ELK stack)
- Reverse proxy — Nginx or Caddy for centralized TLS

---

## Privacy Note

All screenshots have been reviewed before publishing. Private IPs, internal hostnames, and any work-related browser content have been blurred or cropped. Raw screenshots are excluded from version control via `.gitignore`.

---

*Michael Kelly · IT support professional · Pensacola, FL · Preferred name: Trea*
