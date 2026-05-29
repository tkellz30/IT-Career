# Security Review — esther (Ubuntu 24.04 LTS)

Point-in-time security audit and remediation record.
Updated after each completed hardening action.

**Last reviewed:** 2026-05-29 (SSH hardening)  
**Reviewed by:** Trae Kelly

---

## Current Posture Summary

All high-priority Phase 2 host hardening items are complete. The server enforces
key-only SSH authentication, deny-by-default firewall policy, hardened Samba guest
authentication, automated patching, and zero-trust remote access via Tailscale.
The remaining open finding is the Docker/UFW iptables bypass (Phase 2, pending).

---

## Completed Remediations

### SSH Key-Only Authentication (2026-05-29)

**Finding:** `PasswordAuthentication yes` was active via
`/etc/ssh/sshd_config.d/50-cloud-init.conf` — an Ubuntu 24.04 cloud-init override
that takes precedence over the main `sshd_config`. Password-based SSH logins were
accepted, exposing the server to brute-force attacks.

**Impact:** Medium. No internet exposure (Tailscale + no open WAN ports), but any
device on the LAN could attempt password-based SSH login. Password auth is the primary
attack vector for compromised credentials and brute-force tools.

**Remediation:**
- ED25519 key pair generated on Windows client (`trea-homelab`)
- Public key deployed to `~/.ssh/authorized_keys` on `esther`
- Key login verified from a second SSH session before any config change
- `PasswordAuthentication no` set in `50-cloud-init.conf` (override file, not main sshd_config)
- `sudo sshd -T` confirmed `passwordauthentication no` before reload
- `sudo systemctl reload ssh` applied — existing sessions preserved
- Third new SSH session confirmed key auth still works post-reload

**Validation:** `sshd -T | grep passwordauthentication` → `passwordauthentication no`

**Evidence:** `screenshots/final/05-ssh-key-generated.png`, `screenshots/final/06-ssh-key-auth-success.png`, `screenshots/final/07-ssh-key-only-enforced.png`

---

### Samba Guest Authentication Hardening (2026-05-29)

**Finding:** Two permissive global Samba settings were active:
- `map to guest = Bad User` — unknown usernames were mapped to a guest session before
  share-level access controls evaluated the request
- `usershare allow guests = Yes` — user-created shares could be configured with
  unauthenticated access

**Impact:** Low-Medium. Both production shares (`[Media]`, `[FastStorage]`) already
enforced `guest ok = No` and `valid users`, so no data was accessible to guests. The
issue was at the authentication boundary, not the authorization boundary. Guest sessions
were being established and then denied rather than being rejected at authentication.

**Remediation:**
- Set `map to guest = Never` — unknown usernames now rejected at authentication stage,
  no guest session is established
- Set `usershare allow guests = No` — unused pathway for guest-accessible user-created
  shares removed

**Validation:** `testparm --suppress-prompt` confirmed `Loaded services file OK` before
restart. Both `smbd` and `nmbd` confirmed `active (running)` post-restart.

**Evidence:** `screenshots/final/04-samba-services-after-hardening.png`

---

### UFW Firewall Deployment (2026-05-27)

**Finding:** No host-based firewall was active on the server.

**Impact:** High. All service ports were accessible to any host on the LAN with no
policy-enforced restrictions.

**Remediation:** UFW deployed with deny-by-default inbound policy. Named rules added
for SSH (all interfaces, for Tailscale compatibility), Samba (LAN subnet only), and
Tailscale WireGuard (UDP 41641). All rules staged and reviewed before enabling.

**Evidence:** `screenshots/final/01-ufw-active-status.png`

---

### Docker Container Hygiene (2026-05-29)

**Finding:** Two exited `hello-world` test containers (`cool_feynman`, `busy_noether`)
had been in a stopped state for 13 days.

**Impact:** Operational. Stopped containers consume disk space from their writable
layers and create namespace ambiguity in `docker ps -a`.

**Remediation:** Both containers removed with `docker rm`. Jellyfin and Portainer
unaffected.

**Evidence:** `screenshots/final/03-docker-cleanup-complete.png`

---

## Open Findings

| # | Finding | Severity | Status |
|---|---|---|---|
| 8 | Docker containers bypass UFW via iptables | Medium | Pending Phase 2 |
| 11 | `samba-ad-dc.service` enabled but not running | Low | Pending |
| 12 | `cloud-init` services vestigial on bare-metal | Low | Pending |

---

## Known Architectural Limitation: Docker/UFW Bypass

Docker manages port publishing by writing rules directly to `iptables` chains
(`DOCKER`, `DOCKER-USER`) that are evaluated before UFW's `INPUT` chain. As a result,
UFW rules for ports 8096 (Jellyfin) and 9443 (Portainer) have no effect — those ports
are open to the full LAN regardless of UFW policy.

**Documented fix (Phase 2):** Bind container ports to specific IP addresses at launch:
```yaml
ports:
  - "192.168.x.x:8096:8096"
```
This restricts each service to the intended network interface without requiring
iptables expertise to maintain.

---

## Resume Summary

Conducted a structured security audit of a bare-metal Ubuntu 24.04 LTS homelab server
and executed a hardening program across authentication, firewall, Samba file sharing,
and container management. Enforced SSH key-only authentication using ED25519 keys with
a three-session verification sequence to eliminate lockout risk; identified and corrected
an Ubuntu cloud-init override file that superseded the main sshd_config. Deployed UFW
with deny-by-default policy and interface-aware rules. Tightened Samba global
authentication by eliminating guest session creation and disabling unused share pathways.
Applied production change management practices throughout: dated backups, config
validation before service restarts, one change at a time, verified access after each
step. Identified Docker/UFW bypass as a pending remediation and documented the fix
approach.
