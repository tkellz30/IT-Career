# Homelab Infrastructure Project — pfSense Virtualization Lab

**Server:** `esther` | **OS:** Ubuntu 24.04.4 LTS | **Hardware:** Intel i5-3470, 7.6 GB RAM, 1.4 TB storage

A portfolio-quality bare-metal homelab documenting the full lifecycle of a production-grade home infrastructure project: from initial server setup and security hardening, through service containerization, to planned KVM virtualization with pfSense for network segmentation and security lab work.

---

## Architecture Overview

```
                          INTERNET
                              │
                        Home Router
                        192.168.x.1
                              │
                   ┌──────────┴──────────┐
                   │    LAN 192.168.0.0/24│
                   └──────────┬──────────┘
                              │
                   ┌──────────▼──────────┐
                   │   esther (bare metal)│
                   │   192.168.x.x/24   │
                   │   Ubuntu 24.04 LTS  │
                   └──────────┬──────────┘
                              │
               ┌──────────────┼──────────────┐
               │              │              │
        ┌──────▼─────┐  ┌─────▼──────┐  ┌───▼────────┐
        │  Jellyfin   │  │  Portainer │  │   Samba    │
        │  :8096      │  │  :9443     │  │  :445/139  │
        │  (Docker)   │  │  (Docker)  │  │  (native)  │
        └─────────────┘  └────────────┘  └────────────┘

                 Remote Access (Tailscale VPN)
                   100.x.x.x / tailscale0
```

**Planned additions (Phase 2+):**
```
                   ┌─────────────────────┐
                   │   KVM Hypervisor    │
                   │   (libvirt)         │
                   │  ┌───────────────┐  │
                   │  │  pfSense VM   │  │
                   │  │  (firewall/   │  │
                   │  │   router)     │  │
                   │  └───────────────┘  │
                   └─────────────────────┘
```

---

## Current Infrastructure State

| Component | Status | Notes |
|---|---|---|
| Ubuntu 24.04.4 LTS | ✅ Running | Kernel 6.8.0-117-generic |
| UFW Firewall | ✅ Active | Deny-by-default, LAN-scoped Samba, VPN-aware |
| Unattended-upgrades | ✅ Active | Daily security patches, 0 pending |
| Jellyfin | ✅ Healthy | Port 8096, Docker managed |
| Portainer | ✅ Running | Port 9443, Docker managed |
| Samba | ✅ Running | Media + FastStorage shares |
| Tailscale VPN | ✅ Active | Remote access secured |
| KVM / libvirt | ⚠️ Pending | Blocked: VT-x must be enabled in BIOS |
| pfSense VM | 🔲 Planned | Phase 2 |
| Docker network hardening | 🔲 Planned | Phase 2 |
| SSH key-only auth | 🔲 Planned | Phase 2 |

---

## Hardware Inventory

| Component | Spec |
|---|---|
| CPU | Intel Core i5-3470 @ 3.20GHz (4 cores, 4 threads) |
| RAM | 7.6 GB (845 MB used at idle) |
| System Disk | 465.8 GB SATA HDD — LVM, 100 GB root (11% used), 362 GB unallocated |
| Fast Storage | 931.5 GB NVMe SSD — ext4, 28 GB used (4%), mounted `/mnt/fast-storage` |
| Network | Intel I217 (eno1) + USB Ethernet adapter (unused) |
| VPN Interface | tailscale0 — 100.x.x.x/32 |

---

## Documentation Index

| Document | Description |
|---|---|
| [docs/01-system-baseline.md](docs/01-system-baseline.md) | Full system inventory and initial state |
| [docs/02-ufw-firewall-hardening.md](docs/02-ufw-firewall-hardening.md) | UFW deployment, rules, and verification |
| [docs/03-kvm-libvirt-setup.md](docs/03-kvm-libvirt-setup.md) | KVM/libvirt installation and configuration |
| [docs/04-pfsense-planning.md](docs/04-pfsense-planning.md) | pfSense VM planning and network design |
| [docs/05-docker-hardening.md](docs/05-docker-hardening.md) | Docker + UFW bypass remediation (planned) |
| [checklists/pre-pfsense-readiness.md](checklists/pre-pfsense-readiness.md) | Step-by-step pfSense readiness checklist |
| [checklists/security-hardening-progress.md](checklists/security-hardening-progress.md) | Security posture tracking |
| [rollback/networking-rollback-procedures.md](rollback/networking-rollback-procedures.md) | Safe rollback steps for all network changes |
| [configs/ufw-rules-esther.md](configs/ufw-rules-esther.md) | Documented UFW rule set with rationale |
| [screenshots/README.md](screenshots/README.md) | Evidence collection index |

---

## Skills Demonstrated

- **Linux Systems Administration** — Ubuntu 24.04 LTS, systemd, journald, apt/unattended-upgrades
- **Network Security** — UFW firewall, LAN segmentation, VPN integration (Tailscale/WireGuard)
- **Container Management** — Docker, Docker Compose, Portainer, named volumes, bridge networks
- **Storage Architecture** — LVM on SATA, NVMe direct mount, Samba SMB file sharing
- **Virtualization** — KVM/libvirt, planned pfSense VM deployment
- **Remote Administration** — VS Code SSH extension, Tailscale zero-trust remote access
- **Documentation** — Infrastructure as documentation, portfolio-ready evidence collection

---

## Resume Bullets

```
• Deployed and configured UFW host-based firewall on Ubuntu 24.04 LTS with deny-by-default 
  inbound policy, LAN-scoped SMB rules, and VPN-aware Tailscale interface allowances; 
  verified zero service disruption post-enable

• Administered containerized media and infrastructure stack (Jellyfin, Portainer) on bare-metal 
  Ubuntu server using Docker; implemented named volume persistence and health-check monitoring

• Configured and verified automated security patch management via unattended-upgrades; confirmed 
  daily execution and successful package upgrades through systemd journal analysis

• Conducted full infrastructure audit of homelab server documenting hardware specs, storage 
  architecture (LVM + NVMe), network topology, Docker containers, and Samba shares as baseline 
  for ongoing security improvement program

• Implemented zero-trust remote access via Tailscale VPN, enabling encrypted SSH and service 
  access without port forwarding; integrated Tailscale WireGuard rules into UFW firewall policy
```

---

## Project Roadmap

- [x] System baseline audit
- [x] UFW firewall deployment
- [x] Unattended-upgrades verification
- [ ] BIOS: Enable VT-x for KVM
- [ ] KVM/libvirt installation and verification
- [ ] pfSense VM deployment
- [ ] Docker network hardening (UFW bypass fix)
- [ ] Samba guest configuration tightening
- [ ] SSH key-only authentication
- [ ] LVM volume extension (recover 362 GB)
- [ ] Reverse proxy with TLS for Jellyfin/Portainer

---

*Last updated: 2026-05-27*
