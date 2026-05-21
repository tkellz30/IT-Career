# Technical Interview Questions — Homelab Project

Prepared answers to technical questions an interviewer might ask about this project. These are realistic for helpdesk, junior sysadmin, NOC, and infrastructure support roles.

---

## Linux and System Administration

**Q: What Linux distribution did you use and why?**
> Ubuntu Server. It has strong community documentation, is widely used in enterprise environments, and the package ecosystem (apt) is beginner-friendly while still being production-relevant.

**Q: How did you manage the server since it doesn't have a GUI?**
> Entirely through the command line — either directly on the machine during initial setup, or remotely over SSH once that was configured. I also used VS Code with the Remote-SSH extension for editing files.

**Q: What does `systemctl` do and how did you use it?**
> `systemctl` manages services in systemd-based Linux systems. I used it to check service status (`systemctl status ssh`), start services, stop them, and enable them to start automatically on boot (`systemctl enable docker`). It was my first stop when something wasn't reachable.

**Q: How did you check what was running on the server?**
> Several commands depending on what I was looking for: `systemctl status` for service state, `docker ps` for running containers, `ss -tuln` for open ports and listening services, `df -h` and `lsblk` for storage, and `journalctl` when I needed to dig into logs.

---

## Networking and Remote Access

**Q: What is SSH and how does it work at a basic level?**
> SSH (Secure Shell) is a protocol for encrypted remote terminal access. The client initiates a connection to the server on port 22, they negotiate encryption, and you get an authenticated shell session. I used it to manage the server remotely without needing to be physically in front of it.

**Q: What is Tailscale and why did you use it instead of just opening a port?**
> Tailscale is a VPN overlay built on WireGuard. It connects devices through a private encrypted network without requiring me to expose ports on my home router to the internet. It was simpler and more secure than configuring port forwarding and managing firewall rules for public access.

**Q: What's the difference between SSH and a VPN?**
> SSH gives you a secure connection to run commands or transfer files on a specific machine. A VPN connects devices at the network level, making remote machines appear as if they're on the same local network. I used both: Tailscale (VPN) to reach the server when off-network, and SSH to actually administer it.

**Q: How would you verify a server is reachable before troubleshooting deeper?**
> Start with `ping` to confirm basic network connectivity. If that works, check if the specific port is reachable using `telnet server-ip port` or `nc -zv server-ip port`. If the port is closed, check the service status on the server and the firewall rules.

---

## Docker and Containers

**Q: What is Docker and why use it instead of installing services directly?**
> Docker lets you run applications in isolated containers. Each container has its own environment, dependencies, and configuration. It's easier to deploy, update, and remove services without affecting the host system. If a container breaks, it doesn't take down the whole server.

**Q: What's the difference between a Docker image and a container?**
> An image is the blueprint — a read-only snapshot of the application and its dependencies. A container is a running instance of that image. You can run multiple containers from the same image, each isolated from the others.

**Q: How did you deploy services in Docker?**
> Using `docker run` with flags for port mapping (`-p`), volume mounts (`-v`), and restart policy (`--restart=unless-stopped`). I also used Portainer as a web interface for managing containers without typing commands for routine tasks.

**Q: What did you do when a container wouldn't start?**
> First checked `docker ps -a` to see the container's exit status. Then ran `docker logs <container_name>` to read the error output. Most issues were either a port conflict (fixed with `ss -tuln` to identify what was using the port) or a volume permission issue (fixed with `chown`).

---

## Storage

**Q: How did you configure persistent storage on the server?**
> I mounted drives manually first to verify they worked, then added entries to `/etc/fstab` using the drive's UUID so they mount automatically on every reboot. Using the UUID instead of the device name (like `/dev/sdb`) prevents issues if drive detection order changes.

**Q: What's the difference between `/dev/sdb` and a UUID for identifying a drive?**
> Device names like `/dev/sdb` are assigned at boot based on detection order and can change if you add or remove drives. UUIDs are unique identifiers tied to the filesystem itself — they're stable regardless of which port or slot the drive is in.

**Q: How did you test an fstab change without rebooting?**
> `sudo mount -a` — it processes all entries in `/etc/fstab` and mounts anything not already mounted. If there's an error in the entry, it fails with an error message rather than waiting until the next reboot to discover the problem.

---

## Troubleshooting Approach

**Q: Walk me through how you approach a problem when something stops working.**
> I start by narrowing the layer: is it a network issue, a service issue, or an application issue? I check service status first (`systemctl status`), then logs (`journalctl`, `docker logs`), then network connectivity (`ping`, `ss -tuln`). I work from broad to specific rather than jumping straight to configuration changes.

**Q: Give me an example of a real problem you solved.**
> The secondary drive didn't persist after rebooting. After the reboot, `df -h` showed it wasn't mounted. I knew the drive was fine because manually mounting it worked. I realized the issue was that I had never added it to `/etc/fstab`. I got the UUID with `sudo blkid`, added the entry, tested with `mount -a`, and rebooted to confirm. The lesson was that manual mounts are temporary — persistence requires an fstab entry.

**Q: What's the first thing you check when a service is running but unreachable from the network?**
> The firewall. A service can be running and listening on a port, but if UFW or iptables is blocking that port, incoming connections will be silently dropped. `sudo ufw status` shows the current rules. That was the issue with my Samba share — the service was running fine, but SMB ports weren't allowed through the firewall.
