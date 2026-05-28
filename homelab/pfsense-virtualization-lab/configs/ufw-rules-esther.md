# UFW Rule Set — esther

**Applied:** 2026-05-27  
**Status:** Active

---

## Current Rule Set

```
# Restore these rules with:
# ufw reset && [re-run each line below] && ufw --force enable

ufw default deny incoming
ufw default allow outgoing

ufw allow 22/tcp comment 'SSH'
ufw allow in on tailscale0 comment 'Tailscale inbound'
ufw allow out on tailscale0 comment 'Tailscale outbound'
ufw allow 41641/udp comment 'Tailscale WireGuard'
ufw allow from 192.168.0.0/24 to any port 139 proto tcp comment 'Samba NetBIOS LAN'
ufw allow from 192.168.0.0/24 to any port 445 proto tcp comment 'Samba SMB LAN'
```

---

## Rule Rationale

| Rule | Why |
|---|---|
| `deny incoming` (default) | Block all inbound unless explicitly permitted |
| `allow outgoing` (default) | Server must reach apt, Tailscale, NTP, DNS |
| `22/tcp` | SSH from any interface — needed for Tailscale SSH (source is 100.x.x.x) |
| `in on tailscale0` | Allow all inbound over the Tailscale VPN interface (Tailscale handles auth) |
| `out on tailscale0` | Allow return traffic and server-initiated Tailscale outbound |
| `41641/udp` | WireGuard tunnel port — blocking this drops the Tailscale VPN |
| `139/tcp from 192.168.0.0/24` | Samba NetBIOS name service — LAN only |
| `445/tcp from 192.168.0.0/24` | Samba SMB — LAN only |

---

## Ports NOT in UFW (and why)

| Port | Service | Why not in UFW |
|---|---|---|
| 8096 | Jellyfin | Docker bypasses UFW via iptables; UFW rule has no effect |
| 9443 | Portainer | Same — Docker bypass |

These will be addressed in Docker hardening phase by binding ports to specific interfaces rather than `0.0.0.0`.

---

## Planned Future Rules

```bash
# After Docker hardening — these become meaningful once Docker stops bypassing UFW
ufw allow from 192.168.0.0/24 to any port 8096 proto tcp comment 'Jellyfin LAN'
ufw allow from 100.64.0.0/10 to any port 8096 proto tcp comment 'Jellyfin Tailscale'
ufw allow from 192.168.0.0/24 to any port 9443 proto tcp comment 'Portainer LAN'
ufw allow from 100.64.0.0/10 to any port 9443 proto tcp comment 'Portainer Tailscale'

# After KVM setup — libvirt management
ufw allow from 192.168.0.0/24 to any port 16509 proto tcp comment 'libvirtd API LAN'
```
