# Lab Explanations — Interview Reference

Concise explanations for how to describe homelab projects in a technical interview. Keep answers under 2 minutes when spoken. Lead with what you built, why you built it, and one real problem you solved.

---

## Pi-hole DNS Filtering Lab

**One-sentence version:**
I deployed Pi-hole on a Raspberry Pi as a network-wide DNS sinkhole with Unbound for recursive DNS, configured blocklists, and worked through router/mesh DNS propagation issues to get filtering working on every device.

**Full explanation ("tell me about a project you've done"):**

I set up Pi-hole on a Raspberry Pi to act as the DNS server for my entire home network. Pi-hole works as a DNS sinkhole — when any device on the network makes a request for a known ad, tracking, or malicious domain, Pi-hole returns a null response instead of the real IP, so the content is never loaded. Because it works at the DNS level, every device benefits automatically once they receive Pi-hole's IP from DHCP, with no per-device configuration.

On top of Pi-hole I added Unbound, which is a recursive DNS resolver. Instead of forwarding queries to a third-party resolver like Google's 8.8.8.8, Unbound resolves DNS from scratch starting at the root nameservers. This keeps DNS queries off any external provider's infrastructure entirely.

The most interesting part was the troubleshooting. My home network uses a main router with TP-Link Deco mesh APs. The Deco units were running in router mode, which meant they were handling DHCP themselves and handing out their own IP as DNS — so Pi-hole's IP was never reaching any of the devices connected through the mesh. My DNS settings at the main router were completely ignored by Deco clients. Once I figured that out and switched the Deco units to AP mode, the main router took over DHCP and started advertising Pi-hole to all clients.

I also had to tune the blocklists. I started with a few aggressive lists and they broke some smart TV apps and a game console service. The Pi-hole query log showed exactly which domains were being blocked, so I could whitelist specific entries without weakening the overall filtering.

**Follow-up answers:**

- *"How does DNS work?"*
  DNS translates domain names to IP addresses. When you type a URL, your device asks a DNS resolver "what's the IP for this domain?" and uses the answer to connect. Pi-hole sits between the device and any external resolver and drops requests that match known-bad domains before they go anywhere.

- *"What's the difference between forwarding and recursive DNS?"*
  A forwarding resolver passes your query to another resolver and returns whatever it gets back. A recursive resolver — like Unbound — starts at the root of the DNS hierarchy and walks down through authoritative servers to find the answer itself. Slower on the first query, but independent of any third party.

- *"Why not just use a VPN or browser extension for ad blocking?"*
  Pi-hole works at the network level, so every device — phones, TVs, IoT devices — gets filtered without installing anything on them. A browser extension only covers one browser on one device, and most IoT devices don't support extensions at all.

- *"What's the downside?"*
  Pi-hole is a single point of failure. If the Pi goes down or the service crashes, all DNS on the network breaks. I handle this by keeping it on dedicated hardware and knowing how to restart the service quickly. In a production environment you'd want a secondary DNS or health monitoring.

- *"What did you learn from this that applies to a help desk or sysadmin role?"*
  The biggest takeaway was methodical troubleshooting. When DNS wasn't reaching clients, I didn't just restart everything and hope — I traced the path: which device was handing out DHCP, what DNS value it was advertising, and which layer the breakdown was happening at. That's the same process for diagnosing connectivity issues in any network environment.

---

## Linux Homelab (Server Infrastructure)

*(Full documentation in [homelab/README.md](../homelab/README.md))*

**One-sentence version:**
I built a self-hosted server on repurposed desktop hardware running Ubuntu Server, Docker containers, Tailscale VPN, and Samba file sharing.

**Key talking points:**

- **Why Docker:** Isolation, easy cleanup, and reproducible deployments. Each service runs in its own container with defined ports and volumes, so there are no dependency conflicts and removing a service is one command.
- **Why Tailscale:** No port forwarding, no public IP exposure, no firewall rules. Devices authenticate once and are reachable by hostname from anywhere over a WireGuard tunnel.
- **Most instructive troubleshooting:** Jellyfin couldn't scan its media library. Diagnosed through `docker logs` — the container user didn't have permission to read the mounted storage directory. Fixed with `chown`. Taught me that permissions problems in containerized environments often look like the container "not working" but the error is in the logs.
- **`/etc/fstab` lesson:** Using device names like `/dev/sdb` in fstab breaks after a reboot if detection order changes. UUIDs are stable regardless of which port a drive is plugged into.

---

*This file is internal prep — not published content. Update when new labs are added.*
