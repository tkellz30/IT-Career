# Screenshot Capture Checklist

Based on a full inventory of 1,719 existing image files, **8 of 13 required categories have zero coverage.**
This document tells you exactly what to capture, how to capture it cleanly, and what to avoid.

Existing keepers (already in `raw-screenshots/`):
- Tailscale admin console — `raw-screenshots/unsorted/Screenshot 2026-05-19 213202.png`
- Lenovo BIOS boot sequence — phone dump, Batch1
- Boot error on monitor — phone dump, Batch1
- Hardware (RAM, drive bay) — phone dump, Batch1

Everything below still needs to be captured.

---

## Terminal Setup (Do This First)

Before capturing any terminal screenshot:

```bash
clear                    # clear the screen
```

- Set font size to **14–16pt minimum** — output must be legible at 800px wide on GitHub
- Use a **dark background terminal** (black or near-black)
- Maximize the terminal window, then resize to remove empty space after the command output
- Do not have other windows visible behind the terminal

---

## Screenshot 1 — OS Confirmation

**Purpose:** Proves Ubuntu Server is installed and running. Establishes the hostname and kernel version.

**Command:**
```bash
uname -a && lsb_release -a && hostnamectl
```

Or run them separately for a cleaner output — `uname -a` alone is sufficient if the output is clean.

**What should be visible:**
- Kernel version (e.g., `Linux 6.x.x-generic`)
- Architecture (`x86_64`)
- Hostname
- OS description: `Ubuntu 22.04` or similar

**What to avoid:**
- No other commands or clutter above the prompt
- Do not show full session history — run `clear` first

**Suggested filename:** `03-terminal-uname.png`

---

## Screenshot 2 — Services Running

**Purpose:** Proves Docker, SSH, and Tailscale are active and enabled. This is the single most valuable terminal screenshot for sysadmin and infrastructure roles.

**Commands (run each separately for clean output):**
```bash
sudo systemctl status ssh
sudo systemctl status docker
sudo systemctl status tailscaled
```

Or combine into one readable block:
```bash
for svc in ssh docker tailscaled; do echo "=== $svc ==="; systemctl is-active $svc; systemctl is-enabled $svc; done
```

**What should be visible:**
- `Active: active (running)` for each service
- `enabled` in the enabled line — confirms they start on boot
- Service name clearly readable

**What to avoid:**
- Do not show the full `systemctl status` wall of text if the log lines at the bottom contain IP addresses or internal hostnames you want private
- Crop below the "Active:" and "Enabled:" lines if needed

**Suggested filename:** `06-systemctl-status.png`

---

## Screenshot 3 — Docker Containers Running

**Purpose:** Proves containers are deployed and running. Anyone who reviews this resume will look for this exact output.

**Command:**
```bash
docker ps
```

**What should be visible:**
- Container IDs (partial is fine)
- Image names (`portainer/portainer-ce`, `jellyfin/jellyfin`)
- Status: `Up X days` or `Up X hours`
- Port mappings (e.g., `0.0.0.0:9000->9000/tcp`)
- Container names

**What to avoid:**
- Do not run `docker ps -a` if you have stopped/failed containers you don't want visible
- If output wraps awkwardly, widen the terminal window before running the command

**Suggested filename:** `07-docker-ps.png`

---

## Screenshot 4 — Portainer Dashboard

**Purpose:** Proves you can manage containers through a web interface, not just the CLI.

**Page:** Open a browser and navigate to:
```
http://<server-ip>:9000
```
or via Tailscale:
```
http://<tailscale-ip>:9000
```

**What should be visible:**
- Portainer sidebar (Home, Environments, Containers, etc.)
- Container list showing Portainer and Jellyfin as running
- Green "running" indicators
- Stack or container count in the summary

**What to avoid:**
- Do not show the login page — log in first, then screenshot
- Blur or crop the server IP/hostname in the URL bar if preferred
- Do not show the Portainer admin username

**Suggested filename:** `08-portainer-dashboard.png`

---

## Screenshot 5 — Jellyfin Library

**Purpose:** Proves the self-hosted media service is deployed, configured, and accessible with content in the library.

**Page:** Open a browser and navigate to:
```
http://<server-ip>:8096
```

**What should be visible:**
- Jellyfin web UI with at least one library visible (Movies, TV, Music, etc.)
- Library with content loaded — not empty
- Jellyfin logo or nav bar confirming the service

**What to avoid:**
- Do not show personal media titles if you prefer privacy — screenshot the library tile view rather than the content list
- Do not show the Jellyfin setup/install wizard — show the working dashboard
- Blur the URL bar if it contains your server's local IP

**Suggested filename:** `09-jellyfin-library.png`

---

## Screenshot 6 — Storage: df -h

**Purpose:** Proves drives are mounted and the OS can see them.

**Command:**
```bash
df -h
```

**What should be visible:**
- The root filesystem `/` with used/available space
- Your secondary mount point (`/mnt/media` or similar) as a separate line
- Filesystem size and usage percentage

**What to avoid:**
- tmpfs lines at the top are fine but can be cropped if they clutter the output
- Do not blur the mount paths — they are the proof of work

**Suggested filename:** `10-df-storage.png`

---

## Screenshot 7 — Storage: lsblk

**Purpose:** Complements `df -h` by showing the physical drive layout and partition structure. Recruiters who know Linux will appreciate this alongside `df -h`.

**Command:**
```bash
lsblk
```

**What should be visible:**
- All block devices (sda, sdb, nvme0n1, etc.)
- Partition layout with sizes
- Mount points aligned to each partition

**What to avoid:**
- Nothing sensitive here — show it all

**Suggested filename:** `10b-lsblk-drives.png`

---

## Screenshot 8 — /etc/fstab

**Purpose:** Proves the drive mounts are persistent and correctly configured — not just manually mounted. This is a detail that separates people who understand Linux from people who followed a tutorial once.

**Command:**
```bash
cat /etc/fstab
```

**What should be visible:**
- At least one UUID-based entry for your secondary drive
- The mount point (`/mnt/media` or similar)
- Filesystem type (`ext4`)
- Mount options (`defaults`)
- The standard commented header lines are fine to include

**What to avoid:**
- UUIDs are not sensitive — show them
- If you have any commented-out lines with passwords or credentials (e.g., SMB credentials), crop those out

**Suggested filename:** `11-fstab-config.png`

---

## Screenshot 9 — SSH Remote Session

**Purpose:** Proves you can administer the server remotely. This directly demonstrates remote access skill.

**How to capture:**
1. Open a terminal **on a different device** (laptop, separate machine)
2. SSH into the server:
   ```bash
   ssh username@<tailscale-ip>
   ```
3. Once connected, run one or two commands to show it's a live remote session:
   ```bash
   hostname
   uptime
   ```
4. Screenshot the terminal on the connecting device

**What should be visible:**
- The SSH connection line: `username@hostname:~$`
- Evidence it is a remote session — ideally both the local machine prompt and the server prompt visible
- A command running (`hostname`, `uptime`, or `uname -a`)
- Output confirming you are on the server

**What to avoid:**
- Blur the Tailscale IP in the `ssh` command line if you prefer privacy
- Do not show your SSH private key path or any key passphrase

**Suggested filename:** `04-ssh-remote-session.png`

---

## Screenshot 10 — Samba Share in Windows Explorer

**Purpose:** Proves SMB file sharing is configured and accessible from a Windows client. This is a real-world skill that shows up in helpdesk and sysadmin roles.

**How to capture:**
1. On a Windows machine on your local network, open File Explorer
2. In the address bar, type:
   ```
   \\<server-ip>\<share-name>
   ```
   or just navigate to **Network** in the sidebar and find the server
3. If it prompts for credentials, enter them and connect
4. Screenshot File Explorer showing the share contents

**What should be visible:**
- Windows File Explorer with the UNC path in the address bar (`\\servername\media` or similar)
- The share is open and accessible (folder contents visible, even if empty)
- The server name or IP in the address bar

**What to avoid:**
- Do not show personal file names if you prefer privacy — an empty share folder or a folder with generic names is fine
- Blur the server IP in the address bar if preferred

**Suggested filename:** `12-samba-share-windows.png`

---

## Sensitive Information Checklist

Review every screenshot against this list before adding it to the repo.

**Network information:**
- [ ] Tailscale IPs (100.x.x.x range) — blur if preferred, not required
- [ ] LAN IP addresses — blur if preferred
- [ ] MAC addresses — blur always if visible

**Credentials:**
- [ ] No passwords visible anywhere
- [ ] No API keys or tokens visible
- [ ] No SSH private key content visible
- [ ] No Tailscale auth keys visible
- [ ] No Portainer or Jellyfin admin passwords visible

**Personal/client information:**
- [ ] No client names, emails, or phone numbers from work
- [ ] No personal file names or folder names you want private
- [ ] No financial or billing information
- [ ] No work email content

**Work screenshots — do not include in this repo:**
The laptop dump contains First City Internet client data including M365 user accounts, billing records, and client network configs. None of that belongs in a public portfolio repo.

---

## Pre-Publish GitHub Checklist

Run through this before pushing screenshots to the public repo.

**Content:**
- [ ] Every screenshot in `homelab/screenshots/` is homelab-specific — nothing from other projects
- [ ] No work or client content mixed in
- [ ] Sensitive info blurred or cropped per checklist above

**Quality:**
- [ ] All terminal screenshots have font size 14pt or larger
- [ ] All text is legible without zooming in
- [ ] No empty terminal prompts with no output
- [ ] No login/setup wizard screens — only working, configured state

**Naming:**
- [ ] All files follow the `##-category-description.png` convention
- [ ] Files are numbered in logical order (hardware → OS → access → services → storage)
- [ ] No spaces or capital letters in filenames

**README integration:**
- [ ] Each screenshot is embedded inline in the README next to the section it supports
- [ ] Not dropped into a single gallery at the bottom

---

## What Makes a Screenshot Good vs. Bad

### Good
- Shows a **working outcome**: `docker ps` with two containers marked `Up 3 days`
- Shows **persistent configuration**: `cat /etc/fstab` with a UUID entry
- Shows **remote access in action**: SSH prompt from a second device
- **Clean terminal**: one command, readable output, dark background
- **Cropped tight**: no taskbar, no irrelevant desktop

### Bad
- Login screen or install wizard — proves nothing is working
- Empty terminal prompt with no output
- Full desktop screenshot with taskbar and other windows visible
- Command output too small to read on GitHub
- Three screenshots of nearly identical `ls` output
- Screenshot of an error with no follow-up showing the fix

### What Recruiters Actually Care About

People reviewing entry-level IT resumes have seen thousands of them. They are looking for two things: **proof that something is running**, and **proof that you understand what you built**.

The screenshots that do the most work:

1. **`docker ps`** — instantly confirms containers are deployed and up. Two lines of output prove more than a paragraph of description.
2. **`systemctl status`** — shows you know how Linux services work and that yours are configured to start on boot.
3. **`/etc/fstab`** — almost no one at entry level shows this. It proves you understand persistence, not just manual mounting.
4. **SSH session from a second device** — proves remote access is actually working end-to-end, not just described.
5. **Portainer with containers visible** — shows a real management workflow.

The BIOS photo and the boot error photo from your phone are genuinely useful — they show you worked through real hardware problems, not a pre-built cloud VM.

---

## Naming Convention

```
##-category-description.png
```

| File | Description |
|------|-------------|
| `01-hardware-drives.jpg` | Drive bay / hardware (from phone) — already have |
| `02-bios-boot-sequence.jpg` | Lenovo BIOS screen (from phone) — already have |
| `03-terminal-uname.png` | `uname -a` output — **needs capture** |
| `04-ssh-remote-session.png` | SSH from second device — **needs capture** |
| `05-tailscale-console.png` | Tailscale admin (already have in unsorted) |
| `06-systemctl-status.png` | Services running — **needs capture** |
| `07-docker-ps.png` | Containers running — **needs capture** |
| `08-portainer-dashboard.png` | Portainer UI — **needs capture** |
| `09-jellyfin-library.png` | Jellyfin library — **needs capture** |
| `10-df-storage.png` | `df -h` output — **needs capture** |
| `10b-lsblk-drives.png` | `lsblk` output — **needs capture** |
| `11-fstab-config.png` | `cat /etc/fstab` — **needs capture** |
| `12-samba-share-windows.png` | SMB share in File Explorer — **needs capture** |
| `13-troubleshooting-example.png` | Error + resolution — **needs capture** |
