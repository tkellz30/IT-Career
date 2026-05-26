# Project Technical Reference

Design decisions, service explanations, and technical context for the labs in this repository. Companion to the main READMEs — not a replacement for them.

---

## Pi-hole DNS Filtering Lab

*Full lab documentation: [Pi-hole DNS Filtering Lab](../pihole-dns-filtering-lab/README.md)*

### Infrastructure Overview

Pi-hole runs on a Raspberry Pi as the DNS server for the entire home network. Every device's DNS queries pass through it — requests matching known ad, tracking, or malicious domains return NXDOMAIN before they leave the local network. Because filtering happens at the DNS layer, every device benefits automatically once DHCP advertises Pi-hole's IP. No per-device configuration.

Unbound runs alongside Pi-hole as a recursive resolver on port 5335. Instead of forwarding queries to Google (8.8.8.8) or Cloudflare (1.1.1.1), Unbound resolves from the root nameservers directly. The full chain: client → Pi-hole → Unbound → root nameservers → authoritative DNS. No external resolver sees the full query history.

### Design Decisions

**Wired Ethernet for the Pi.** DNS is a foundational dependency — if the Pi loses connectivity, the entire network loses DNS resolution. Wired is more reliable than Wi-Fi for something everything else depends on.

**Static IP via DHCP reservation, not configured on the Pi.** Assigning the IP from the router makes it easier to change without touching the Pi's network config. Keeps the Pi's own networking setup clean.

**No secondary DNS at the router.** A fallback DNS that bypasses Pi-hole defeats the filtering — clients fall back to it whenever Pi-hole is slow or unavailable. The lab accepts Pi-hole as a single point of failure in exchange for consistent coverage.

**Unbound instead of a forwarding resolver.** Forwarding resolvers see every DNS query the network makes. Unbound eliminates that dependency. The tradeoff is a slightly slower first-query time and a more complex setup to maintain.

### Key Troubleshooting — Deco Mesh DNS Propagation

The TP-Link Deco units were running in router mode. In that mode, Deco handles its own DHCP and advertises its own IP as the DNS server — so Pi-hole's IP never reached any mesh-connected device. DNS settings at the main router had zero effect on those clients. Switching the Deco units to AP mode gave DHCP control back to the main router, which then advertised Pi-hole to all clients.

Full troubleshooting table: [Pi-hole troubleshooting notes](../pihole-dns-filtering-lab/README.md#troubleshooting-notes)

### Technical Concepts

**How DNS works at a basic level.**  
DNS translates domain names to IP addresses. When a device makes a request, it asks a DNS resolver for the IP, then uses that IP to connect. Pi-hole sits between the device and any external resolver and drops requests that match known-bad domains before they go further.

**Forwarding vs. recursive DNS.**  
A forwarding resolver passes the query to another resolver and returns what it gets back. A recursive resolver — like Unbound — starts at the DNS root hierarchy and walks down through TLD and authoritative servers to find the answer directly. Slower on the first query for an uncached domain, but independent of any third party.

**Network-level filtering vs. browser extensions.**  
Browser extensions cover one browser on one device. Pi-hole covers everything on the network — phones, TVs, game consoles, IoT devices — without any per-device configuration. Most smart home hardware doesn't support extensions at all.

**Known limitations.**  
- Pi-hole is a single point of failure. If it goes down, the network loses DNS.
- DNS traffic between clients and Pi-hole is plaintext on the local network. DoH/DoT not implemented.
- Devices with hardcoded DNS (some IoT products point directly to 8.8.8.8) bypass Pi-hole entirely. Intercepting that requires firewall rules outside this lab's scope.
- Pi-hole blocks the DNS lookup, not the IP address. A client with a cached IP can still connect directly.

---

## Linux Homelab Infrastructure

*Full lab documentation: [Linux Homelab — Infrastructure Project](../../README.md) → [homelab/README.md](../README.md)*

### Infrastructure Overview

Ubuntu Server running headless on repurposed Lenovo hardware. No monitor, no keyboard attached — all administration happens over SSH or via Tailscale from off-network. Docker manages containerized services (Portainer, Jellyfin). A separate NVMe (931.5 GB) mounts persistently at `/mnt/fast-storage` and is shared over Samba.

### Design Decisions

**Docker instead of direct OS installs.**  
Installing services directly on the OS creates dependency conflicts and leaves config files scattered. Docker isolates each service with defined ports, volumes, and restart policies. Removing a service is `docker stop` + `docker rm`, not a manual cleanup of files and packages.

**Tailscale instead of port forwarding.**  
Exposing ports to the public internet requires managing firewall rules, handling IP changes, and maintaining certificates. Tailscale creates a WireGuard overlay that makes the server reachable by hostname from any authorized device without any exposed ports. Devices authenticate once.

**UUID-based `/etc/fstab` entries.**  
`/dev/sdb` is assigned by detection order at boot and can shift if drives are added, removed, or reordered. UUIDs are tied to the partition itself and stay constant regardless of physical port or boot order. All persistent mounts use UUIDs retrieved with `blkid`.

### Notable Troubleshooting

**Jellyfin media library returned no results.**  
Jellyfin was running (health check passing), but the library showed nothing. `docker logs jellyfin` showed permission denied errors on the mount path. The container runs as a specific user internally; that user didn't have read access to `/mnt/fast-storage`. Fixed with `chown -R 1000:1000 /mnt/fast-storage`. Key lesson: containerized permission failures look like application errors until you check the container logs.

**NVMe drive missing after reboot.**  
Drive was accessible after a manual `mount` command but gone after rebooting. Manual mounts don't persist. Added a UUID-based entry to `/etc/fstab` and tested with `mount -a` before rebooting.

Full 8-entry log: [docs/troubleshooting-log.md](troubleshooting-log.md)
