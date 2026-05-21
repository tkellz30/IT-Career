# Troubleshooting Log

Structured record of issues encountered during the homelab build, how they were investigated, and how they were resolved.

Format: **Symptom → Investigation → Fix → Lesson**

---

## Entry 001 — BIOS Not Detecting SSD on First Boot

**Area:** Hardware / BIOS
**Symptom:** Server powered on but BIOS showed no bootable drive; installation could not proceed.
**Investigation:**
- Entered BIOS setup and checked the boot device list
- Drive was not listed under detected storage devices
- Checked physical connections — SATA/NVMe seating

**Fix:**
- Reseated the drive; confirmed secure connection
- Returned to BIOS, confirmed drive appeared in device list
- Set drive as first boot device and saved settings

**Lesson:** Always confirm the drive appears in BIOS *before* troubleshooting the OS. Physical connection issues look identical to software issues from the outside.

---

## Entry 002 — Ubuntu Server USB Installer Would Not Boot

**Area:** OS Installation
**Symptom:** Server powered on with USB inserted but booted to BIOS instead of the installer.
**Investigation:**
- Verified USB was listed in boot order
- Suspected corrupted or incorrectly written installer image

**Fix:**
- Recreated bootable USB using a verified Ubuntu Server ISO
- Confirmed BIOS Secure Boot setting — adjusted as needed for the installer to load

**Lesson:** A bootable USB made from the wrong tool or a corrupt download will silently fail. Recreating from a fresh, verified image is the fastest fix.

---

## Entry 003 — SSH Connection Refused After OS Install

**Area:** Remote Access / SSH
**Symptom:** Running `ssh user@server-ip` from a remote machine returned "Connection refused."
**Investigation:**
- Confirmed server was running and reachable on the network (`ping` responded)
- SSH port (22) not responding — indicated the service was not running
- Ran `systemctl status ssh` on the server locally — service was inactive

**Fix:**
```bash
sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```
- Retested SSH from remote — connection succeeded

**Lesson:** Ubuntu Server does not always install `openssh-server` by default depending on install options. `systemctl status` is the first command to run when a service is unreachable.

---

## Entry 004 — Tailscale Node Not Appearing in Admin Console

**Area:** Tailscale / Remote Access
**Symptom:** After installing Tailscale on the server, the machine did not appear in the Tailscale admin console.
**Investigation:**
- Ran `tailscale status` — showed not connected
- Service was installed but authentication had not completed

**Fix:**
```bash
sudo tailscale up
```
- Followed the authentication URL, authorized the machine in the browser
- Confirmed node appeared in admin console and Tailscale IP was assigned

**Lesson:** Installing Tailscale and running `tailscale up` are two separate steps. The node doesn't authenticate automatically on install.

---

## Entry 005 — Docker Container Failed to Start (Port Conflict)

**Area:** Docker / Containers
**Symptom:** A container exited immediately after `docker run`. Error indicated the port was already in use.
**Investigation:**
```bash
sudo ss -tuln
```
- Output showed port 9000 was already bound by another process
- Checked running containers — an earlier Portainer attempt was still allocated to the port

**Fix:**
- Stopped and removed the conflicting container:
```bash
docker stop <container_id>
docker rm <container_id>
```
- Relaunched the container — started successfully

**Lesson:** `ss -tuln` is the fastest way to see what's listening on which ports. Container port conflicts are common when redeploying without cleaning up the previous instance.

---

## Entry 006 — Secondary Drive Not Persisting After Reboot

**Area:** Storage / fstab
**Symptom:** Secondary drive was accessible after manual `mount` but disappeared after rebooting the server.
**Investigation:**
- Ran `lsblk` and `df -h` post-reboot — drive not mounted
- Checked `/etc/fstab` — no entry existed for the drive
- Manual mount worked (`sudo mount /dev/sdX /mnt/media`) but is not persistent

**Fix:**
- Retrieved drive UUID:
```bash
sudo blkid /dev/sdX
```
- Added entry to `/etc/fstab`:
```
UUID=xxxx-xxxx  /mnt/media  ext4  defaults  0  2
```
- Tested without rebooting:
```bash
sudo mount -a
```
- Rebooted and confirmed drive mounted automatically

**Lesson:** `mount` is temporary. Persistent mounts require an `/etc/fstab` entry using the UUID (not the device name like `/dev/sdb`, which can change across reboots).

---

## Entry 007 — Jellyfin Not Scanning Media Library

**Area:** Jellyfin / Permissions
**Symptom:** Jellyfin was running but the media library scan returned no results despite files being present.
**Investigation:**
- Confirmed files existed at the correct path with `ls -lh /mnt/media`
- Checked Jellyfin container logs:
```bash
docker logs jellyfin
```
- Log showed permission denied errors when accessing `/mnt/media`

**Fix:**
- Identified the user/group Jellyfin runs as inside the container
- Updated directory ownership:
```bash
sudo chown -R 1000:1000 /mnt/media
```
- Rescanned the library in Jellyfin — files appeared

**Lesson:** Containers run as specific users internally. Volume mounts inherit host permissions, so if the container user doesn't have read access to the mounted directory, it silently fails or logs a permission error.

---

## Entry 008 — Samba Share Not Accessible from Windows

**Area:** Samba / SMB / Networking
**Symptom:** Windows could not connect to the Samba share. "Network path not found" or authentication error.
**Investigation:**
- Confirmed Samba service was running: `systemctl status smbd`
- Checked firewall: UFW rules did not include SMB ports

**Fix:**
- Allowed SMB through the firewall:
```bash
sudo ufw allow samba
```
- Verified share configuration in `/etc/samba/smb.conf`
- Retested from Windows — share appeared and was accessible

**Lesson:** A service can be running and correctly configured but still unreachable if the firewall blocks the port. Always check firewall rules when a service is running but unreachable from the network.
