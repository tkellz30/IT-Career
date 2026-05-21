# Project Notes — Linux Homelab

Explanations and talking points for this project. For resume/LinkedIn copy, see [career-snippets.md](career-snippets.md). For technical Q&A, see [technical-qa/technical-questions.md](technical-qa/technical-questions.md).

---

## Project Overview (30–45 seconds)

"I built a Linux homelab on repurposed physical hardware to get experience I couldn't get from studying alone. I installed Ubuntu Server, configured SSH and Tailscale for remote access, and deployed Docker containers — Portainer for container management and Jellyfin as a self-hosted media server. I also set up persistent storage with fstab and configured Samba for file sharing across my local network. Most of the learning came from troubleshooting real failures — boot issues, permission errors, container conflicts. It's a working environment I actively use and maintain."

---

## Why Did You Build This?

"I wanted hands-on experience with tools that actually show up in IT jobs — Linux, SSH, Docker, remote access, storage. Courses and labs give you a controlled environment. Building something on real hardware where things actually break and you have to fix them teaches you differently. I also wanted something concrete I could point to as portfolio evidence and actually use day-to-day."

---

## What Was the Hardest Part?

"Getting storage to persist across reboots. I mounted the drive manually and it worked, but after a reboot it was gone. I had to learn how `/etc/fstab` works, find the correct UUID for the drive using `blkid`, and add the right entry. Then I tested it with `mount -a` before rebooting to confirm the syntax was correct. It's a common real-world task that I wouldn't have run into in a lab environment."

---

## What Would You Do Differently?

"I'd document as I go more consistently. Some troubleshooting steps I had to reconstruct from memory. Going forward I write down what I tried and what the error said before I fix it, not after. I'd also set up monitoring earlier — something like Uptime Kuma — so I'd know when a service goes down rather than noticing it when I try to use it."

---

## Did You Use AI Tools?

"Yes — I used AI to speed up research, understand error messages, and structure documentation. But all the testing, troubleshooting, and verification was done by me. If something didn't work, I had to figure out why. AI can explain what a command does, but it can't tell you that your specific drive UUID is wrong or that your fstab entry has a typo. That part is still on you."

---

## How Is This Relevant to IT Support Roles?

**Helpdesk:**
"A lot of helpdesk work is asking the right questions and knowing where to look when something isn't working. Building this taught me to check service status, read logs, and narrow down whether an issue is hardware, network, or application — before touching anything."

**Junior sysadmin:**
"I've done the fundamentals hands-on: Linux administration, SSH, service management with systemctl, Docker, storage configuration, and network troubleshooting. It's a small environment, but the skills transfer directly."

**NOC/infrastructure support:**
"This project gave me a troubleshooting methodology I can apply to unfamiliar systems — check the service, check the logs, check the network, check the firewall. That process scales regardless of the environment."
