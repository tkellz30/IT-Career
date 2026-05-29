# UFW Firewall Hardening

**Date:** 2026-05-27  
**Status:** ✅ Complete — UFW active, all services verified

---

## Problem Statement

At baseline, `esther` had UFW installed but inactive. All inbound ports were unfiltered:
- SSH (22) — accessible from anywhere on LAN
- Samba (139, 445) — accessible from anywhere on LAN
- Jellyfin (8096) — accessible from anywhere on LAN
- Portainer (9443) — accessible from anywhere on LAN

No deny-by-default policy was enforced.

---

## Key Decision: Docker + UFW Bypass

**This is the most important concept in this document.**

Docker bypasses UFW by writing directly to `iptables`. When Docker publishes a port (`-p 8096:8096`), it adds rules to the `DOCKER-USER` and `DOCKER` iptables chains, which are processed before UFW's `INPUT` chain rules.

**Practical consequence:**
| Service | Controlled by UFW? |
|---|---|
| SSH (port 22) — native systemd | ✅ Yes |
| Samba (139, 445) — native systemd | ✅ Yes |
| Jellyfin (8096) — Docker container | ❌ No — Docker iptables bypass |
| Portainer (9443) — Docker container | ❌ No — Docker iptables bypass |

Adding UFW rules for 8096 or 9443 has no effect without additional Docker configuration. Docker hardening is a separate future phase.

**Why this matters for the portfolio:** Understanding this gotcha separates candidates who have actually run Docker in a secured environment from those who have only read about it.

---

## Rules Implemented

Rules were staged **before** UFW was enabled, then reviewed before activation.

```bash
# Defaults
sudo ufw default deny incoming     # Block everything not explicitly allowed
sudo ufw default allow outgoing    # Server can make outbound connections

# SSH — allowed from all interfaces
# Rationale: restricting to LAN-only would break Tailscale SSH access
sudo ufw allow 22/tcp comment 'SSH'

# Tailscale — allow all traffic on the VPN interface
# Rationale: Tailscale handles its own auth/encryption; blanket allow is safe
sudo ufw allow in on tailscale0 comment 'Tailscale inbound'
sudo ufw allow out on tailscale0 comment 'Tailscale outbound'

# Tailscale WireGuard UDP port
# Rationale: This is the underlying VPN tunnel port; blocking it drops the VPN
sudo ufw allow 41641/udp comment 'Tailscale WireGuard'

# Samba — restricted to LAN subnet only
sudo ufw allow from 192.168.0.0/24 to any port 139 proto tcp comment 'Samba NetBIOS LAN'
sudo ufw allow from 192.168.0.0/24 to any port 445 proto tcp comment 'Samba SMB LAN'

# Enable (--force skips interactive "may disrupt connections" prompt)
sudo ufw --force enable
```

---

## Verification Steps

Every step was verified before proceeding to the next.

### Step 1 — Rules staged, UFW still inactive
```
$ sudo ufw show added
Added user rules (see 'ufw status' for running firewall):
ufw allow 22/tcp comment 'SSH'
ufw allow in on tailscale0 comment 'Tailscale inbound'
ufw allow out on tailscale0 comment 'Tailscale outbound'
ufw allow 41641/udp comment 'Tailscale WireGuard'
ufw allow from 192.168.0.0/24 to any port 139 proto tcp comment 'Samba NetBIOS LAN'
ufw allow from 192.168.0.0/24 to any port 445 proto tcp comment 'Samba SMB LAN'
```

### Step 2 — UFW enabled
```
$ sudo ufw --force enable
Firewall is active and enabled on system startup
```

### Step 3 — Status verified
```
$ sudo ufw status verbose
Status: active
Default: deny (incoming), allow (outgoing), deny (routed)

To                           Action      From
--                           ------      ----
22/tcp                       ALLOW IN    Anywhere                   # SSH
Anywhere on tailscale0       ALLOW IN    Anywhere                   # Tailscale inbound
41641/udp                    ALLOW IN    Anywhere                   # Tailscale WireGuard
139/tcp                      ALLOW IN    192.168.0.0/24             # Samba NetBIOS LAN
445/tcp                      ALLOW IN    192.168.0.0/24             # Samba SMB LAN
Anywhere                     ALLOW OUT   Anywhere on tailscale0     # Tailscale outbound
```

### Step 4 — Connectivity verified post-enable
- SSH connection remained active throughout (confirmed by continued remote session)
- Tailscale showed active direct connection to peer
- `smbd` and `nmbd` both reported `active` after enable
- `hostname` command returned `esther` — SSH alive

---

## iptables Result

UFW's activation sets the INPUT chain default policy to DROP:

```
Chain INPUT (policy DROP)
1    ts-input   (Tailscale's own rules, prepended by tailscaled)
2    ufw-before-logging-input
3    ufw-before-input
4    ufw-after-input
...
```

Note `ts-input` at position 1 — Tailscale daemon manages its own iptables entries. This is expected and confirms Tailscale is working correctly alongside UFW.

---

## Known Limitations & Future Work

| Issue | Impact | Fix | Status |
|---|---|---|---|
| Docker bypasses UFW for ports 8096, 9443 | Jellyfin/Portainer accessible from full LAN | Bind Docker ports to specific interface IPs in docker-compose | Pending Phase 2 |
| SSH allows password auth | Password brute-force possible | Deploy SSH keys, set `PasswordAuthentication no` | ✅ Resolved 2026-05-29 |
| Samba guest config permissive | `map to guest = Bad User` set globally | Set `map to guest = Never` in smb.conf | ✅ Resolved 2026-05-29 |
| LAN IP is DHCP | UFW rule `192.168.0.0/24` still works; Samba discovery may break if IP changes | Set static DHCP reservation at router | Pending |

---

## Common Beginner Mistakes (Lessons)

1. **Enabling UFW before adding SSH rule** — locks you out of the server. Always stage rules first, verify with `ufw show added`, then enable.
2. **Forgetting Tailscale WireGuard UDP port** — UFW will block the underlying VPN tunnel. The VPN may appear connected briefly on cached state, then drop silently.
3. **Assuming UFW controls Docker ports** — it does not without additional configuration. Many tutorials miss this entirely.
4. **Adding rules after enabling** — safe to do, but riskier than staging beforehand. Develop the habit of staging → reviewing → enabling.

---

## Screenshot Evidence

| Screenshot | Filename | Value |
|---|---|---|
| `sudo ufw status verbose` output | `screenshots/final/01-ufw-active-status.png` | Proves firewall deployment with named rules |
| Security baseline before hardening | `screenshots/final/02-security-baseline-before-hardening.png` | Shows pre-hardening state: open password auth, permissive Samba, orphan containers |

**What to blur:** Nothing sensitive in UFW status output.
