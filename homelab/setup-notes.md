# Setup Notes — Command Reference

Commands and steps used during the homelab build, organized by phase. These are not a tutorial — they're a personal reference for what was actually done.

---

## Phase 1 — Hardware and BIOS

- Installed Samsung SSD/NVMe as the primary boot drive
- Installed secondary HDD/SSD for media storage
- Entered BIOS setup to verify drive detection and set boot order
- Set SSD as first boot device before inserting the Ubuntu installer USB

---

## Phase 2 — Ubuntu Server Installation

- Created bootable USB from Ubuntu Server ISO
- Booted from USB and followed the installer
- Selected: no GUI, OpenSSH server (installer option), standard partitioning
- Set hostname and created a non-root admin user during install
- Confirmed system booted into Ubuntu and logged in locally

**Verify OS after install:**
```bash
uname -a
lsb_release -a
hostnamectl
```

---

## Phase 3 — SSH Configuration

If OpenSSH was not selected during install:
```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

**Test SSH from another device:**
```bash
ssh username@server-ip
```

**Test SSH over Tailscale (after Tailscale setup):**
```bash
ssh username@tailscale-ip
```

---

## Phase 4 — Tailscale

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate and bring up the network
sudo tailscale up

# Check connection status
tailscale status

# Find the assigned Tailscale IP
tailscale ip
```

Authorize the machine in the Tailscale admin console after running `tailscale up`.

---

## Phase 5 — Docker

```bash
# Install Docker
sudo apt update
sudo apt install docker.io

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker

# Add user to docker group (avoids needing sudo for docker commands)
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect

# Verify
docker --version
docker ps
```

---

## Phase 6 — Portainer

```bash
# Create a named volume for Portainer data
docker volume create portainer_data

# Run Portainer
docker run -d \
  --name portainer \
  --restart=unless-stopped \
  -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce

# Verify it started
docker ps
```

Access the web UI at: `http://server-ip:9000`
Create an admin account on first login.

---

## Phase 7 — Storage Mounting

**Identify drives:**
```bash
lsblk
sudo fdisk -l
```

**Get drive UUID (needed for fstab):**
```bash
sudo blkid /dev/sdX
```

**Create mount point:**
```bash
sudo mkdir -p /mnt/media
```

**Add to /etc/fstab (use UUID, not device name):**
```
UUID=xxxx-xxxx-xxxx-xxxx  /mnt/media  ext4  defaults  0  2
```

**Test without rebooting:**
```bash
sudo mount -a
```

**Verify:**
```bash
df -h
lsblk
```

**Set ownership so services can read/write:**
```bash
sudo chown -R 1000:1000 /mnt/media
sudo chmod -R 755 /mnt/media
```

---

## Phase 8 — Jellyfin

```bash
docker run -d \
  --name jellyfin \
  --restart=unless-stopped \
  -p 8096:8096 \
  -v jellyfin_config:/config \
  -v jellyfin_cache:/cache \
  -v /mnt/media:/media:ro \
  jellyfin/jellyfin

docker ps
```

Access at: `http://server-ip:8096`
Complete the setup wizard, add `/media` as a library path.

---

## Phase 9 — Samba (SMB File Sharing)

```bash
sudo apt install samba

# Edit the config file
sudo nano /etc/samba/smb.conf
```

Add a share block at the bottom of `smb.conf`:
```ini
[media]
   path = /mnt/media
   browsable = yes
   read only = yes
   guest ok = no
```

```bash
# Set Samba password for user
sudo smbpasswd -a username

# Restart Samba
sudo systemctl restart smbd

# Allow through firewall
sudo ufw allow samba

# Verify
sudo systemctl status smbd
```

Access from Windows: `\\server-ip\media`

---

## Useful Day-to-Day Commands

```bash
# Check all running containers
docker ps

# Check container logs
docker logs <container_name>

# Restart a container
docker restart <container_name>

# Check disk space
df -h

# Check mounted drives
lsblk

# Check what's listening on ports
sudo ss -tuln

# Check a service
sudo systemctl status <service_name>

# Check recent system logs
journalctl -xe --no-pager | tail -50
```
