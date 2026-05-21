# Screenshot Plan — Linux Homelab GitHub Project

A prioritized plan for capturing, ordering, and presenting screenshots that prove technical work and look professional on GitHub.

---

## Guiding Principle

Every screenshot should answer one question: **"How do I know this actually worked?"**

Screenshots that show a process are okay. Screenshots that show a working outcome are better. Screenshots that show a working outcome *and* the command or configuration that produced it are best.

---

## Priority Tiers

### Tier 1 — High Value (must have)

These prove the core technical work was completed. Recruiters and interviewers who know Linux will look for exactly these.

| # | Screenshot | What It Proves | Command / Source |
|---|------------|----------------|------------------|
| 1 | `lsblk` or `df -h` output | Drives are mounted and visible to the OS | `lsblk` or `df -h` in terminal |
| 2 | `/etc/fstab` content | Mounts are persistent across reboots | `cat /etc/fstab` |
| 3 | `systemctl status` for Docker, SSH, and Tailscale | Services are running and enabled | `systemctl status docker ssh tailscale` |
| 4 | `docker ps` output | Containers are running | `docker ps` |
| 5 | Portainer dashboard | Container management is configured | Web UI at port 9000 or 9443 |
| 6 | SSH session from remote machine | Remote access is working end-to-end | Terminal on a second device |
| 7 | Tailscale admin console | VPN node is online and connected | Tailscale web dashboard |
| 8 | Jellyfin web interface | Self-hosted service is accessible and functional | Browser pointed at Jellyfin port |

---

### Tier 2 — Supporting Evidence (good to have)

These add context and show the full scope of the build. Include if the screenshots are clean.

| # | Screenshot | What It Proves |
|---|------------|----------------|
| 9 | Hardware photo (drives, machine internals) | Physical build is real; shows initiative beyond VMs |
| 10 | Ubuntu Server installation screen | OS was installed from scratch, not a pre-built image |
| 11 | VS Code with Remote-SSH connected | Real remote development workflow |
| 12 | Samba share visible in Windows Explorer | File sharing is functional from a client device |
| 13 | Jellyfin library with media loaded | Service is configured, not just installed |
| 14 | A resolved troubleshooting example | Shows you can diagnose and fix real problems |

---

### Tier 3 — Low Value (skip or replace)

| Screenshot | Why It's Weak | Better Alternative |
|------------|---------------|--------------------|
| Generic Ubuntu welcome/login screen | Proves nothing specific | `uname -a` output with hostname instead |
| Empty terminal with just a prompt | No information | Any command with meaningful output |
| Portainer login page | Shows install, not function | Portainer dashboard with containers visible |
| Jellyfin setup wizard | Shows install, not function | Jellyfin library or playback screen |
| Multiple screenshots of similar `ls` output | Redundant | One clean directory tree with `tree` or `ls -lh` |
| Full desktop screenshot | Unfocused, unprofessional | Crop to the relevant terminal or window only |

---

## Recommended Order

Order screenshots to tell a logical story: **hardware → OS → access → services → storage → proof**.

```
1.  Hardware photo (physical server internals or drives)
2.  Ubuntu Server installation in progress
3.  uname -a  →  confirms OS, kernel, hostname
4.  SSH session from a second device
5.  Tailscale admin console showing node online
6.  systemctl status docker ssh tailscale  →  all active
7.  docker ps  →  containers running
8.  Portainer dashboard  →  containers visible in UI
9.  Jellyfin web UI  →  library loaded
10. lsblk or df -h  →  drives mounted
11. cat /etc/fstab  →  mounts are persistent
12. Samba share in Windows Explorer  →  file sharing works
13. Troubleshooting example  →  log output + resolution
```

This order mirrors how a sysadmin would verify a server: confirm hardware → OS → access → services → storage → clients.

---

## Cropping and Cleaning Guidelines

**Always crop:**
- Remove taskbar, window chrome, and unrelated desktop elements
- Crop to the terminal output or UI panel that matters
- If the output is long, show the relevant section — not the full scroll

**Always check before publishing:**
- Blur or remove public IP addresses
- Blur or remove Tailscale node IPs if you prefer privacy
- Remove any personal file names visible in Jellyfin or Samba screenshots
- Make sure no API keys, tokens, or passwords are visible in config files

**Terminal appearance:**
- Use a dark background with high-contrast text (easier to read on GitHub)
- Increase font size before screenshotting so output is legible at 800px wide
- Clear the terminal (`clear`) before running the command you're capturing

**Naming convention for the files:**
```
01-hardware.jpg
02-ubuntu-install.png
03-uname.png
04-ssh-session.png
05-tailscale-console.png
06-systemctl-status.png
07-docker-ps.png
08-portainer-dashboard.png
09-jellyfin-ui.png
10-lsblk.png
11-fstab.png
12-samba-share.png
13-troubleshooting.png
```

Numbered prefixes keep them in order in the file system and make README image references easier to manage.

---

## Troubleshooting Screenshot — What to Capture

This is one of the most valuable screenshots for an entry-level candidate because it shows real diagnostic thinking. A good troubleshooting screenshot includes:

1. The error message or failing state (e.g., a `systemctl status` showing `failed`)
2. The command you ran to investigate (e.g., `journalctl -xe`, `docker logs <name>`)
3. The fix applied (e.g., the corrected command or config change)
4. The confirmed working state after the fix

If you didn't capture this in real time, recreate a realistic example using a service you can intentionally misconfigure and fix (e.g., stop Docker, show the failure, restart it).

---

## README Integration

Once screenshots are captured and named, add them to the README under each relevant section using this format:

```markdown
![SSH session showing remote connection](screenshots/04-ssh-session.png)
```

Avoid putting all screenshots in one gallery at the bottom — inline them next to the section they support so the reader sees the proof alongside the explanation.
