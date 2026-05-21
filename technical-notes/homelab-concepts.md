# Homelab Concepts and Explanations

## What is Docker?

Docker is a containerization platform that allows applications to run in isolated environments with their own dependencies and configurations.

I used Docker in my homelab to deploy services like Jellyfin and Portainer on Ubuntu Server.

---

## What is Portainer?

Portainer is a web-based management interface for Docker.

I used it to:
- manage containers
- monitor running services
- restart deployments
- view logs
- simplify Docker management through a GUI

---

## What is Tailscale?

Tailscale is a VPN platform built on WireGuard that allows secure remote access between devices.

I used it to remotely access my Ubuntu server from my phone and laptop using SSH.

---

## What Did You Learn From The Homelab?

I learned:
- Linux administration basics (service management, permissions, log reading)
- remote server management via SSH and Tailscale
- Docker/container fundamentals — deploying, managing, and troubleshooting containers
- persistent storage configuration with `/etc/fstab` and UUIDs
- file sharing with Samba across a local network
- structured troubleshooting: checking service status, reading logs, narrowing by layer
- documentation practices — writing notes during the work, not reconstructing after

The biggest lesson was that most Linux problems explain themselves if you read the logs carefully — `journalctl`, `systemctl status`, and container logs solve a lot.

---

## What Problems Did You Troubleshoot?

- BIOS and boot order problems
- Ubuntu installation issues
- SSD mounting issues
- Docker deployment troubleshooting
- Jellyfin playback issues
- remote access testing
- storage path configuration
- SSH connectivity testing

---

## Why Did You Build This?

I wanted hands-on infrastructure experience outside of helpdesk work. Courses give you a controlled environment where things are set up for you. Building on real hardware — where the BIOS has quirks, the USB won't boot right, and the drive disappears after a reboot — teaches you differently. I also wanted something concrete I could point to in interviews and actually use day-to-day.

---

## Did You Use AI Tools?

Yes — I used AI to speed up research and documentation throughout the build. When I hit an unfamiliar error message, I used AI to understand what it meant and figure out where to look — the same way you'd use a vendor knowledge base or a well-written Stack Overflow thread.

All troubleshooting, testing, and implementation was done by me, on the actual hardware. AI can explain what a command does, but it can't run `blkid` on my specific machine or tell me that my fstab entry has a tab where it needs a space. That hands-on verification is always on me.