# System Architecture

## Network Overview

```
[ Home Router / Mesh Network ]
          |
          | LAN (192.168.x.x)
          |
  [ Ubuntu Server — Lenovo Hardware ]
    |
    ├── SSH daemon             port 22
    ├── Tailscale agent        WireGuard overlay (100.x.x.x)
    |
    ├── Docker Engine
    │     ├── Portainer        port 9000
    │     └── Jellyfin         port 8096
    |
    ├── Samba (SMB)            port 445
    |
    └── Storage
          ├── /                Samsung SSD / NVMe  (OS + Docker)
          └── /mnt/media       Secondary HDD / SSD (media, backups)


[ Tailscale Overlay Network ]
    ├── Server node            (accessible remotely via Tailscale IP)
    └── Remote clients         (laptop, phone — authorized devices)


[ Local Network Clients ]
    ├── Windows PC             → Samba file share access
    └── Any browser / device   → Jellyfin media playback (local or via Tailscale)
```

---

## Services Running on the Server

| Service | Purpose | Access Method | Port |
|---------|---------|---------------|------|
| SSH | Remote terminal access | `ssh user@server-ip` or Tailscale IP | 22 |
| Tailscale | Secure remote access overlay (WireGuard) | Tailscale app / admin console | N/A |
| Docker Engine | Container runtime | `docker` CLI or Portainer UI | N/A |
| Portainer | Docker management web UI | Browser → `http://server-ip:9000` | 9000 |
| Jellyfin | Self-hosted media server | Browser or Jellyfin app | 8096 |
| Samba | SMB file sharing | Windows Explorer / file manager | 445 |

---

## Storage Layout

| Mount Point | Device | Purpose |
|------------|--------|---------|
| `/` | Samsung SSD / NVMe | OS, Docker images, container data |
| `/mnt/media` | Secondary HDD / SSD | Media files, photos, backups |

Mounts are configured in `/etc/fstab` using drive UUIDs so they persist across reboots.

---

## Remote Access Flow

**Local network:**
```
Client device → home router → server LAN IP → SSH or Jellyfin port
```

**Remote (off-network):**
```
Client device → Tailscale app → WireGuard tunnel → server Tailscale IP → SSH or Jellyfin port
```

No ports are exposed to the public internet. All remote access goes through the Tailscale overlay.

---

## Docker Container Architecture

```
Docker Engine
├── portainer/portainer-ce    (management UI)
│     └── Volumes: portainer_data
│
└── jellyfin/jellyfin         (media server)
      └── Volumes:
            /mnt/media         → /media          (read-only library)
            jellyfin_config    → /config
            jellyfin_cache     → /cache
```

---

## Notes

- Server runs headless (no monitor, no desktop environment)
- All administration is done remotely via SSH or Tailscale
- Portainer is used for container management without needing to SSH in for routine tasks
- Jellyfin is accessible both on the local network and remotely over Tailscale
