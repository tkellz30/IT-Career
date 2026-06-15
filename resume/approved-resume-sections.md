# Approved Resume Sections — Pre-Rewrite Reference
**Trea Kelly · Built June 2026 · Do not rewrite the full resume until all sections below are confirmed**

---

## Section 1: Approved First City Internet Bullets

**Role header:** Tier 1 Helpdesk Support | First City Internet | 2023–Present

### Core bullets (use all 4):

> Serve as sole Tier 1 technician providing business internet support to small office clients in an ISP environment; diagnose and resolve connectivity issues across customer devices, local networks, and CPE/router configurations.

> Apply structured triage to isolate connectivity issues — determining whether problems originate at the endpoint, Wi-Fi layer, Ethernet, CPE/modem, or upstream service — before escalating infrastructure-level faults to Tier 2/3 network staff.

> Use ping, traceroute, ipconfig, nslookup, and remote access tools alongside router/modem portals and UniFi controller to diagnose issues; escalate ISP-side outages, provisioning failures, and network-layer problems requiring elevated access.

> Manage Microsoft 365 user accounts, licenses, and access permissions for business clients; support account provisioning, credential issues, and access troubleshooting through the M365 admin portal.

### Optional bullet (use when applying to network-specific roles):

> Investigated DNS resolution failures and DHCP assignment issues, including APIPA (169.254.x.x) addressing, to determine whether problems originated at the device, local network, or CPE level.

---

## Section 2: Approved VLAN / Network Segmentation Bullets

These bullets are approved and locked. Placement decisions are noted for each.

### First City VLAN bullet — add to First City section:

> Assisted with VLAN and network segmentation troubleshooting in a small business ISP environment; gathered symptoms, assessed connectivity scope, and escalated suspected network-layer issues to Tier 2/3 staff.

**Note:** This bullet rounds out the First City section for network technician roles. When applying to pure helpdesk or IT admin roles where VLAN experience is less relevant, it can be dropped to keep the section tight.

### Project VLAN bullet — already incorporated into Home Network Infrastructure Lab (see Section 3):

> Designed and documented a VLAN segmentation architecture for guest, IoT, work/lab, and management network separation; topology, migration procedure, cutover plan, and rollback process documented in GitHub IT-Career repo — VLAN implementation in progress.

**Do not upgrade "implementation in progress" language until the following are fully complete:**
- VLAN interfaces configured in pfSense
- Trunk/access ports configured on TP-Link TL-SG108PE
- VLAN-tagged SSIDs live on Cisco AIR-AP2802I
- Per-VLAN DHCP scopes running
- Inter-VLAN firewall rules enforced

---

## Section 3: Approved Home Network Infrastructure Lab

**Project header:** Home Network Infrastructure Lab | Personal Project | 2025–Present

> Deployed pfSense as a virtualized router/firewall using KVM/libvirt on a Lenovo host; configured WAN/LAN assignment, DHCP configuration and testing, and firewall rules validated in a lab VM prior to home network cutover.

> Built a managed home network using a TP-Link TL-SG108PE PoE switch and Cisco AIR-AP2802I access point; configured wireless network via Mobility Express and validated client connectivity across wired and wireless segments.

> Deployed Pi-hole with Unbound as a network-wide recursive DNS resolver; provides DNS filtering, local name resolution, and ad/tracker blocking across all network devices.

> Designed and documented a VLAN segmentation architecture for guest, IoT, work/lab, and management network separation; topology, migration procedure, cutover plan, and rollback process documented in GitHub IT-Career repo — VLAN implementation in progress.

### Optional bullet (add if space allows or role emphasizes remote access):

> Configured Tailscale mesh VPN for secure remote access to homelab infrastructure; enables remote management of pfSense, Ubuntu Server, and Docker containers without exposing services to the public internet.

---

## Section 4: Approved Linux Server / Virtualization Homelab

**Project header:** Linux Server / Virtualization Homelab | Personal Project | 2025–Present

> Configured Lenovo desktop as a KVM/libvirt virtualization host; provisioned storage pools for VM and ISO management and deployed pfSense as a lab VM for testing and validation prior to home network cutover.

> Deployed and managed Docker containers using Portainer; self-hosted Jellyfin media server with persistent volume configuration and container lifecycle management.

> Configured Samba SMB file shares for Windows-accessible network storage; set up persistent volume mounts via /etc/fstab for reliable storage management across reboots.

> Configured SSH and VS Code Remote-SSH for secure remote server administration; manages Ubuntu Server, Docker containers, and file shares from any connected device.

---

## What Is Still Locked — Do Not Include Yet

These items are in progress or unconfirmed and must not appear on the resume as completed experience:

- Full VLAN implementation (interfaces, trunk ports, tagged SSIDs, per-VLAN DHCP, inter-VLAN routing)
- Azure / AZ-900 (not started yet)
- Active Directory on-premises admin (not confirmed)
- Any ticket volume claims
- Any claim of production enterprise network ownership at First City

---

*Pre-rewrite reference for the 2026–2030 Life Operating System. All bullets in this document are approved and interview-defensible. Do not rewrite the full resume until the outstanding decisions below are resolved.*
