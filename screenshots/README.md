# Homelab Screenshot Portfolio

**Folder structure:**
```
screenshots/
├── Originals/    — untouched source files, never edit these
├── edited/       — intermediate edits (solid black redactions)
└── final/        — portfolio-ready, use these in the GitHub README
```

All images in `final/` were processed from `Originals/` using Python + Pillow.
Sensitive regions use Gaussian blur (radius 28–30) with a subtle white overlay
to produce a frosted-glass effect rather than hard black boxes.
Work-related browser tabs use solid black where blur alone would not be safe.

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
| 10 | `10-tailscale-network-status.png` | 1920×268 | Tailscale VPN network (Tier 2) | ✅ |

---

## Screenshot Detail — What Each One Proves

---

### 01 · `final/01-ssh-remote-login.png`
**Demonstrates:** Linux remote administration, SSH, Tailscale VPN access

The Ubuntu server MOTD shown immediately after SSH login. Confirms:
- Active SSH session to the `esther` server (`tkellz30@esther:~$`)
- Live system stats: 0.02 load, 10% memory, 31°C, 162 processes
- "Last login from 100.106.17.85" — proves the connection came in over Tailscale, not the local network

**Edits applied:**
- IPv4 LAN address line: frosted blur (radius 30, subtle white overlay)
- IPv6 address line: frosted blur (same)
- Bottom empty terminal space cropped (1002px → 630px)

**Sensitive info removed:** LAN IP `192.168.0.24`, IPv6 address
**Kept intentionally:** Tailscale IP in "Last login from" line — it proves remote Tailscale access worked

---

### 02 · `final/02-docker-ps-running.png`
**Demonstrates:** Docker deployment, container lifecycle management

`docker ps` output showing two containers running on the `esther` server:
- `jellyfin/jellyfin` — Up 2 days, **(healthy)** — port 8096
- `portainer/portainer-ce:latest` — Up 2 days — ports 8000, 9000, 9443

The `(healthy)` status on Jellyfin shows a configured Docker health check, not just a running container.
Port mappings confirm correct network configuration.

**Edits applied:** Bottom empty space cropped (1008px → 296px). No blurring needed.
**Sensitive info removed:** None — this screenshot was clean as captured.

---

### 03 · `final/03-portainer-dashboard.png`
**Demonstrates:** Container management via web UI, Docker orchestration

Portainer Community Edition container list showing all deployed containers:
- `jellyfin` — **healthy** — `jellyfin/jellyfin` — IP 172.18.0.2
- `portainer` — **running** — `portainer/portainer-ce:latest` — IP 172.17.0.2
- Two exited `hello-world` test containers (normal, shows container lifecycle awareness)

**Edits applied:**
- Browser tabs 1–4 (First City Internet, UCKP, Branch tools): solid black — too many employer identifiers for blur to be safe
- Ask Gemini tab: solid black
- URL bar Tailscale IP (`100.119.56.65`): frosted blur (radius 22, white overlay)
- Chrome status bar hover URL at bottom: frosted blur (same)
- Portainer tab and Machines–Tailscale tab: preserved and visible

**Sensitive info removed:** Tailscale IP, work employer browser tabs, status bar hover URL

---

### 04 · `final/04-jellyfin-library.png`
**Demonstrates:** Self-hosted media server deployment, service accessibility

Jellyfin home page accessed through the browser:
- "My Media" section with Movies library tile
- Recently added content with artwork visible
- Full Jellyfin navigation bar (Home, Favorites, cast/search/user icons)

Confirms: the service is not just installed — it is configured, has a media library, and is accessible via browser over Tailscale.

**Edits applied:**
- Entire browser tab bar: solid black (all tabs were work or personal identifiers)
- URL bar Tailscale IP (`100.119.56.65`): frosted blur (radius 22, white overlay)

**Sensitive info removed:** Tailscale IP, all browser tabs (work + personal streaming handle)

---

### 05 · `final/05-lsblk-storage-layout.png`
**Demonstrates:** Linux storage administration, LVM, dual-drive setup, mount point configuration

`lsblk` output showing the full block device tree:
- `sda` (465.8G SSD): EFI + boot + LVM partition → `ubuntu--vg--1-ubuntu--lv` (100G at `/`)
- `sr0` (optical drive, unused)
- `nvme0n1` (931.5G NVMe): single partition mounted at `/mnt/fast-storage`

Shows: physical drive identification, LVM volume group, and the secondary NVMe configured as a named storage mount.

**Edits applied:** Bottom empty space cropped (1008px → 380px). Double `.png.png` extension corrected.
**Sensitive info removed:** None — `lsblk` output contains no credentials or network info.

---

### 06 · `final/06-df-storage-usage.png`
**Demonstrates:** Storage mount verification, filesystem usage monitoring

`df -h` output confirming all drives are mounted with correct reported sizes:
- `/dev/mapper/ubuntu--vg--1-ubuntu--lv` → 98G total, 9.9G used, 83G available at `/`
- `/dev/nvme0n1p1` → **916G total, 28G used, 842G available** at `/mnt/fast-storage`

Pairs with `lsblk` (which shows layout) to prove the mount is active and the OS reports correct storage.

**Edits applied:** Bottom empty space cropped (1008px → 408px).
**Sensitive info removed:** None.

---

### 07 · `final/07-fstab-persistent-mounts.png`
**Demonstrates:** Persistent storage configuration, `/etc/fstab`, UUID-based drive identification

`cat /etc/fstab` output showing all mount entries including two custom persistent mounts:
- `UUID=db188f84-...` → `/data` — ext4, `defaults,nofail`
- `UUID=1115e3ef-...` → `/mnt/fast-storage` — ext4, `defaults,noatime`

The `noatime` option on the NVMe mount demonstrates awareness of performance tuning.
UUID-based entries (rather than `/dev/sdX`) prove understanding of stable device identification.

**Note on UUIDs:** UUIDs are filesystem identifiers, not credentials. They are intentionally preserved — they are the evidence that the configuration is correct.

**Edits applied:** Bottom empty space cropped (1008px → 604px).
**Sensitive info removed:** None — UUIDs are not a privacy or security risk.

---

### 08 · `final/08-samba-share-mounted.png`
**Demonstrates:** Samba/SMB file sharing, cross-platform network file access

Windows File Explorer showing the Samba share mounted as drive `Z:`:
- Address bar: `This PC > faststorage (\\esther) (Z:)` — confirms server hostname and share name
- Folder contents: `backups`, `configs`, `downloads`, `lost+found`, `media`, `photos`
- Date modified timestamps visible (May 2026)

This is the only screenshot taken from a client device, proving the service is accessible end-to-end — not just running on the server.

**Edits applied:** Left navigation sidebar cropped at x=215, removing:
- "First City Internet" network/drive shortcut (employer)
- "OneDrive – First City Internet" (work OneDrive)
- "WEB601" (work network computer)

Address bar, folder contents, and all column headers fully preserved.
**Sensitive info removed:** Employer name, work OneDrive, work network computer name.

---

### 09 · `final/09-storage-directory-structure.png`
**Demonstrates:** Storage organization, filesystem layout awareness

`ls /mnt/fast-storage` output showing the organized directory structure on the mounted NVMe:
`backups  configs  downloads  lost+found  media  photos`

Supporting screenshot — shows intentional organization of the storage volume rather than a single flat directory.

**Edits applied:** Heavy crop — only top 156px kept. Original was 1008px tall with content in the first ~136px.
**Sensitive info removed:** None.

---

### 10 · `final/10-tailscale-network-status.png`
**Demonstrates:** Tailscale VPN administration, multi-device network management (Tier 2)

`tailscale status` output from the server showing the Tailscale overlay network with connected devices including `esther` (the server), a Windows desktop, two iOS devices.

Use as a supporting screenshot only. The SSH screenshot (`01`) provides cleaner remote access proof.

**Edits applied:**
- IP address column (all five `100.x.x.x` addresses): frosted blur (radius 30)
- `fci-cpgkpn2` device hostname (work computer): frosted blur
- Public IP `204.15.112.54:60338` in active connection detail: frosted blur
- Bottom empty space cropped (1008px → 268px)

**Sensitive info removed:** All Tailscale IPs, work device name, public endpoint IP.

---

## What Still Needs to Be Captured

The `systemctl status` category has **no usable screenshot** in this set. Both originals (`01-systemctl-services-full.png` and `02-tailscale-connected.png`) have text too small to read at GitHub display size and log tail entries that contain IPs.

**Recapture this command** at 16pt font, one service at a time:
```bash
clear && systemctl status docker --no-pager | head -6
clear && systemctl status ssh --no-pager | head -6
clear && systemctl status tailscaled --no-pager | head -6
```

Save as `final/00-systemctl-services.png`.

---

## Recommended Embed Order in homelab README

Place each screenshot inline within its section — not grouped at the bottom.

```
## Remote Access
  → final/01-ssh-remote-login.png

## Docker / Containers
  → final/02-docker-ps-running.png
  → final/03-portainer-dashboard.png

## Services
  → final/04-jellyfin-library.png

## Storage
  → final/05-lsblk-storage-layout.png
  → final/06-df-storage-usage.png
  → final/07-fstab-persistent-mounts.png
  → final/09-storage-directory-structure.png

## File Sharing
  → final/08-samba-share-mounted.png

## Supporting / Networking
  → final/10-tailscale-network-status.png   (optional, Tier 2)
```

---

## Sensitive Info — What Was Removed and How

| Item | Found In | Method |
|---|---|---|
| Tailscale IP `100.119.56.65` (server) | 03, 04, 10 | Frosted blur |
| LAN IP `192.168.0.24` | 01 | Frosted blur |
| IPv6 address | 01 | Frosted blur |
| All other Tailscale device IPs | 10 | Frosted blur |
| Public IP `204.15.112.54` | 10 | Frosted blur |
| `fci-cpgkpn2` work device | 10 | Frosted blur |
| Chrome status bar hover IP | 03 | Frosted blur |
| Work browser tabs (FCI, UCKP, Branch) | 03, 04 | Solid black — too many identifiers for blur |
| Personal tab (HumbleGOATv) | 04 | Solid black — entire tab bar |
| "First City Internet" in sidebar | 08 | Sidebar crop |
| "OneDrive – First City Internet" | 08 | Sidebar crop |
| "WEB601" work computer | 08 | Sidebar crop |
| UUIDs in fstab | 07 | **Kept** — not sensitive |
| Username `tkellz30` | All | **Kept** — expected in a homelab portfolio |
| Hostname `esther` | All | **Kept** — no risk |
