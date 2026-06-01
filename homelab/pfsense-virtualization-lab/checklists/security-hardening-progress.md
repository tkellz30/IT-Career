# Security Hardening Progress

Tracks the server's security posture improvement over time. Update after each completed item.

---

## Current Status: Phase 2 In Progress

**Hardening Level:** Intermediate  
**Last Updated:** 2026-05-29

---

## Completed

| # | Item | Date | Notes |
|---|---|---|---|
| 1 | UFW enabled with deny-by-default policy | 2026-05-27 | Rules verified, SSH + Tailscale confirmed working |
| 2 | Unattended-upgrades active and verified | 2026-05-27 | Daily execution confirmed via journald — evidence: `screenshots/final/10-unattended-upgrades-log.png` |
| 3 | Samba shares restricted to named user | Existing | `valid users = <username>` on both shares |
| 4 | Root SSH restricted to key-only | Existing | `PermitRootLogin without-password` |
| 5 | Tailscale VPN for remote access | Existing | No port forwarding required |
| 6 | Tighten Samba guest config | 2026-05-29 | `map to guest = Never`, `usershare allow guests = No` — backed up, testparm validated, smbd/nmbd restarted and confirmed running |
| 7 | SSH key-only authentication | 2026-05-29 | `PasswordAuthentication no` in `/etc/ssh/sshd_config.d/50-cloud-init.conf` — ED25519 key deployed, three-session verification sequence completed, reload not restart |
| 9 | Remove exited test containers | 2026-05-29 | `docker rm cool_feynman busy_noether` — Jellyfin and Portainer unaffected |

---

## Pending — High Priority

| # | Item | Risk if Skipped | Notes |
|---|---|---|---|
| 8 | Docker + UFW bypass remediation | Medium | Docker containers bypass UFW; restrict port bindings |

---

## Pending — Medium Priority

| # | Item | Risk if Skipped | Notes |
|---|---|---|---|
| 10 | Static DHCP reservation for 192.168.x.x | Low-Medium | IP change breaks Samba discovery |
| 11 | Disable `samba-ad-dc.service` | Low | Enabled but not running; unnecessary on standalone server |
| 12 | Disable cloud-init services | Low | Vestigial from Ubuntu cloud image; not needed on bare metal |
| 13 | LVM volume extension | Operational | Recover 362 GB unallocated space |

---

## Pending — Future Phases

| # | Item | Phase | Notes |
|---|---|---|---|
| 14 | KVM/libvirt installation | Phase 2 | Blocked: VT-x disabled in BIOS |
| 15 | pfSense VM deployment | Phase 2 | Requires KVM |
| 16 | Reverse proxy (Caddy/Traefik) + TLS | Phase 3 | HTTPS for Jellyfin and Portainer |
| 17 | Fail2ban for SSH brute-force protection | Phase 3 | Extra layer on top of UFW |
| 18 | SMART disk health monitoring | Phase 3 | `smartmontools` with email alerts |
| 19 | Log aggregation (Loki or ELK) | Phase 4 | Centralized log visibility |

---

## Hardening Score (Informal)

```
Baseline (2026-05-27):          ████░░░░░░  35%
After Phase 1 (UFW + updates):  ██████░░░░  55%
Current (2026-05-29):           ███████░░░  ~60%
After Phase 2 (target):         ████████░░  75%
After Phase 3 (target):         █████████░  90%
```

---

## Scoring Criteria

| Category | Weight | Current | Max |
|---|---|---|---|
| Firewall / Network | 25% | 15% | 25% |
| Authentication | 20% | 16% | 20% |
| Updates / Patching | 20% | 18% | 20% |
| Service Hardening | 15% | 5% | 15% |
| Monitoring / Logging | 10% | 3% | 10% |
| Backups / Recovery | 10% | 0% | 10% |
