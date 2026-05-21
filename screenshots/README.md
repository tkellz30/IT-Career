# Homelab Screenshot Portfolio

**Folder structure:**
```
screenshots/
├── Originals/    — untouched source files, never edit these
├── edited/       — intermediate edits
└── final/        — portfolio-ready, use these in the GitHub README
```

All images in `final/` were processed from `Originals/` using Python + Pillow.
Sensitive regions use Gaussian blur with a subtle white overlay to produce a frosted-glass effect.
Work-related browser content uses solid black where blur alone would not be safe.

---

All screenshots intended for public viewing are stored in `screenshots/final/`. Sensitive details such as IP addresses, device names, browser tabs, account identifiers, and client/work information have been redacted or cropped before publication.

---

## Final Screenshots — Portfolio Ready

| # | File | Dimensions | Demonstrates | Status |
|---|---|---|---|---|
| 1 | `01-ssh-remote-login.png` | 1680×630 | Remote SSH administration | ✅ |
| 2 | `02-docker-ps-running.png` | 1920×296 | Docker container management | ✅ |
| 3 | `03-portainer-dashboard.png` | 1680×1002 | Container web UI management | ✅ |
| 4 | `04-jellyfin-library.png` | 1680×1002 | Self-hosted service deployment | ✅ |
| 5 | `05-lsblk-storage-layout.png` | 1920×380 | Physical drive layout, LVM, NVMe | ✅ |
| 6 | `06-df-storage-usage.png` | 1920×408 | Mounted storage with usage stats | ✅ |
| 7 | `07-fstab-persistent-mounts.png` | 1920×604 | Persistent UUID-based mount config | ✅ |
| 8 | `08-samba-share-mounted.png` | 1686×998 | SMB file sharing from Windows client | ✅ |
| 9 | `09-storage-directory-structure.png` | 1920×156 | Organized storage directory structure | ✅ |
| 10 | `10-tailscale-network-status.png` | 1920×268 | Tailscale VPN network | ✅ |
