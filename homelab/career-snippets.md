# Homelab — Career Snippets

Quick-reference versions of the homelab project for job applications and interviews.

---

## Resume — Project Section

**Linux Homelab Infrastructure Project** | Personal Project | 2025–Present

- Deployed and administered Ubuntu Server on physical hardware, including BIOS configuration, OS installation, and drive setup
- Configured SSH and Tailscale for secure remote access; managed server remotely via CLI and VS Code Remote-SSH
- Installed Docker and deployed containerized services (Portainer, Jellyfin); troubleshot port conflicts, volume mounts, and file permission issues
- Mounted additional drives using `/etc/fstab` for persistent storage; configured Samba (SMB) for local network file sharing
- Documented build steps and troubleshooting procedures on GitHub

---

## LinkedIn — Project Description

**Linux Homelab Infrastructure Project**

Built a self-hosted Linux server environment on physical hardware to develop practical skills in system administration, remote access, and containerization.

**What I built:**
- Ubuntu Server deployed on repurposed Lenovo hardware
- SSH + Tailscale configured for secure remote access from any device
- Docker with Portainer for containerized service management
- Jellyfin self-hosted media server with persistent mounted storage
- Samba (SMB) file sharing for local network access

**What I worked through:** BIOS and boot issues, SSH configuration, container deployment, drive mounting with `/etc/fstab`, and file permission troubleshooting.

This project gave me hands-on experience with the tools and problem-solving process used in real Linux infrastructure environments.

`#Linux` `#Ubuntu` `#Docker` `#SSH` `#Homelab` `#SysAdmin` `#Networking`

---

## Interview — 30-Second Explanation

> Read this aloud a few times until it feels natural. Target: ~35–45 seconds.

"I built a Linux homelab on repurposed physical hardware to get experience I couldn't get from just studying. I installed Ubuntu Server, set up SSH and Tailscale for remote access, and deployed Docker containers — including Portainer for managing containers and Jellyfin as a self-hosted media server. I also configured additional storage drives to mount persistently and set up Samba for file sharing across my network. Most of the learning came from troubleshooting — things like fixing boot issues, resolving container port conflicts, and correcting file permissions when services wouldn't start. It's a working environment I actively use and maintain."

---

## Interview — Follow-Up Answers

**"What was the hardest part?"**
> "Getting storage to mount persistently across reboots. I had to learn how `/etc/fstab` works, find the correct UUID for each drive, and use `mount -a` to test it without rebooting. It's a common real-world task I wouldn't have learned from a course."

**"Did you use any automation or scripting?"**
> "Not yet — right now everything is configured manually, which was intentional. I wanted to understand what each command does before abstracting it away. Automating repetitive tasks with scripts is something I'm working toward."

**"Why did you build this instead of just using a cloud VM?"**
> "I wanted experience with physical hardware — BIOS settings, drive installation, boot troubleshooting — because that's part of helpdesk and infrastructure support work. Cloud skills matter too, but I wanted the hands-on side first."
