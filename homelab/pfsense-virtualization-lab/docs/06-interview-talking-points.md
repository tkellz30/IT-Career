# Security Hardening — Design Decisions and Talking Points

Reference document covering the rationale behind each hardening decision in this lab,
validation approach, and how to explain the work in a technical interview.

**Scope:** Host hardening on `esther` (Ubuntu 24.04 LTS) prior to KVM/pfSense deployment.  
**Phase at writing:** Phase 2 in progress — UFW, Docker cleanup, and Samba guest hardening
complete; SSH key auth pending.

---

## Why Harden the Host Before Adding Virtualization

Adding a hypervisor and VM to an unaudited host creates a compounding problem: new network
interfaces (KVM bridges, pfSense WAN/LAN), new routing paths, and new services running
alongside existing ones. Without a documented baseline, diagnosing issues becomes guesswork
about whether a problem existed before or was introduced by the VM layer.

The baseline audit and hardening work creates a known-good state with:
- All services verified operational
- Firewall policy documented and enforced
- Permissive defaults removed
- Rollback procedures written before changes are made

This is the same approach used in production change management: audit, document, harden,
then add complexity.

---

## UFW Firewall

### Design Decisions

**Deny-by-default inbound.** The firewall rejects all inbound traffic unless explicitly
permitted. Each allowed service has a named rule with documented rationale rather than
unnamed numbered rules.

**SSH allowed from all interfaces, not LAN-only.** Restricting SSH to the LAN subnet would
silently break Tailscale SSH access, which arrives on the `tailscale0` interface with a
100.x.x.x source IP, not a LAN address. Tailscale handles its own mutual authentication —
restricting SSH by source IP adds no security benefit while creating a lockout risk.

**Samba restricted to LAN subnet (`192.168.0.0/24`).** File sharing has no legitimate
use case outside the local network. Restricting by subnet means even if a device reaches
the server over Tailscale, it cannot access the Samba shares.

**Tailscale WireGuard (UDP 41641) explicitly allowed.** Blocking this port breaks the
VPN tunnel. UFW's default deny would otherwise silently drop the WireGuard handshake,
leaving the VPN appearing connected briefly before dropping.

**Rules were staged before enabling UFW.** The full rule set was reviewed with
`sudo ufw show added` before `sudo ufw --force enable`. This eliminates the window
where UFW is active but the SSH rule hasn't been added yet — the most common self-lockout
scenario.

### The Docker/UFW Bypass

Docker manages port publishing by writing rules directly to `iptables` — specifically to
the `DOCKER-USER` and `DOCKER` chains, which are evaluated before UFW's `INPUT` chain.
When a container is launched with `-p 8096:8096`, Docker creates iptables rules that permit
that traffic regardless of what UFW says.

**Practical impact:** UFW rules for ports 8096 (Jellyfin) and 9443 (Portainer) have no
effect. Those ports are open to the full LAN because Docker controls them, not UFW.

The documented fix (Phase 2) is binding containers to specific IP addresses at launch:

```yaml
ports:
  - "192.168.x.x:8096:8096"   # responds only on LAN interface
  - "100.x.x.x:8096:8096"     # or Tailscale interface only
```

This approach is preferable to `DOCKER-USER` chain rules because it survives Docker
restarts and doesn't require iptables expertise to maintain. The alternative — setting
`"iptables": false` in Docker's daemon config — breaks container networking entirely
unless masquerading is manually configured.

### Interview Talking Points

**"Walk me through how you secured the firewall on this server."**

> "I deployed UFW with a deny-by-default inbound policy, then added named rules for each
> service with documented rationale. I staged all rules first and reviewed them before
> enabling UFW — that order matters because enabling with no SSH rule locks you out
> immediately. The most interesting part was discovering that Docker bypasses UFW entirely.
> Docker publishes ports by writing to iptables chains that are processed before UFW, so
> UFW rules for container ports have no effect. I've documented that as a Phase 2 fix
> involving interface-bound port bindings in the container configuration."

**"What's the difference between `ufw reload` and `ufw enable`?"**

> "`enable` activates UFW and sets it to start on boot — first run only. `reload`
> re-reads the ruleset without changing the running state. For adding rules to an already
> active firewall, you add the rule and it takes effect immediately. `reload` is used when
> you've made changes to the config directly rather than through the `ufw` command."

---

## Docker Container Hygiene

### What Was Done

Two exited `hello-world` containers were removed: `cool_feynman` and `busy_noether`.
Both had been in a stopped state for 13 days following initial Docker testing.

### Rationale

Stopped containers consume no CPU or memory, but they occupy namespace entries in
`docker ps -a`, consume disk space from their writable layers, and introduce ambiguity
about what is intentionally deployed versus left over from testing. In any environment
where multiple people might run `docker ps -a`, orphaned containers create confusion
and can mask actual issues.

`docker rm` refuses to remove running containers — there is no risk of accidentally
stopping production services. Jellyfin and Portainer were not affected.

### Interview Talking Point

**"How do you maintain your Docker environment?"**

> "I keep the container list clean by removing test containers immediately after testing
> rather than leaving them in an exited state. `docker rm` only removes stopped containers,
> so it's safe to run without verifying each container's state first. For the running
> services, I verify health status via `docker ps` — Jellyfin has a Docker health check
> configured, so the status column shows `(healthy)` rather than just `Up`, which gives
> a slightly higher confidence that the service is actually responding, not just that the
> process is alive."

---

## Samba Guest Configuration

### Configuration Analysis

From `/etc/samba/smb.conf`:

```
[global]
    line 100:  map to guest = Bad User
    line 168:  usershare allow guests = Yes

[Media]
    guest ok = No     ← already correct

[FastStorage]
    guest ok = No     ← already correct
```

Both production shares already enforce `guest ok = No` and `valid users`. The issue is
at the global authentication layer, not the share layer.

### Design Decision: `map to guest = Never`

`Bad User` means Samba creates a guest session for any connection with a non-existent
username, before that session hits share-level access controls. The guest session is
denied access by `valid users`, but the session itself is still established — unnecessary
overhead and a marginally wider attack surface than needed.

`Never` rejects non-existent usernames at the authentication stage, before any session
is created. No guest sessions are established at any point.

### Design Decision: `usershare allow guests = No`

`usershare` controls whether users can create temporary shares via `net usershare add`
independent of `/etc/samba/smb.conf`. No user-created shares exist on this server.
Disabling guest access for that pathway removes an unused capability that doesn't need
to exist.

### Validation Approach

```bash
# Verify syntax before restarting
sudo testparm --suppress-prompt

# Restart only after testparm reports no errors
sudo systemctl restart smbd nmbd

# Confirm services are running
sudo systemctl status smbd nmbd
```

Config was backed up to `/etc/samba/smb.conf.bak-20260529` before any changes.

### Interview Talking Point

**"How did you approach the Samba hardening?"**

> "I used `testparm` to read the live configuration and identify which settings were
> active versus commented out. The production shares already had `guest ok = No` and
> `valid users` set correctly — the issue was at the global level, where `map to guest`
> was set to `Bad User`. That means Samba was creating guest sessions for unknown usernames
> before denying them at the share layer. I changed it to `Never` so the rejection happens
> at authentication, not after session setup. I backed up the config with a dated filename,
> validated the change with `testparm`, then restarted the service and verified it was
> still running."

---

## SSH Key Authentication

### Status: Complete — 2026-05-29

`PasswordAuthentication no` is now enforced. SSH accepts only ED25519 key
authentication. Password-based logins are rejected.

### What Was Done

Key authentication uses asymmetric cryptography — the server holds a public key, the
client proves possession of the corresponding private key without transmitting it.
Disabling password auth eliminates the brute-force attack surface entirely.

**Ubuntu 24.04 finding:** The active `PasswordAuthentication yes` was not in the main
`/etc/ssh/sshd_config` but in `/etc/ssh/sshd_config.d/50-cloud-init.conf` — a
cloud-init override file that takes precedence. Changing only the main config would
have had no effect. `sudo sshd -T` (which reads the full effective config including
all includes) identified the correct file to modify.

**Sequence used:**

1. Generated ED25519 key pair on Windows client (`trea-homelab`, passphrase-protected)
2. Deployed public key to `~/.ssh/authorized_keys` on `esther`
3. Opened Session 2, verified key-based login succeeded — passphrase prompted, login confirmed
4. With Session 2 live and Session 1 still open, backed up `50-cloud-init.conf`
5. Changed `PasswordAuthentication yes → no` in `50-cloud-init.conf`
6. Validated: `sudo sshd -T | grep passwordauthentication` → `passwordauthentication no`
7. Ran `sudo systemctl reload ssh` — Sessions 1 and 2 stayed alive
8. Opened Session 3 (new connection) — key auth confirmed working post-reload

The sequence matters. Disabling password auth before verifying key login from a live
session creates a lockout risk that requires physical console access to recover from.

### Ubuntu 24.04 Finding: Cloud-init Override

On Ubuntu 24.04 LTS, the default SSH configuration includes an override file at
`/etc/ssh/sshd_config.d/50-cloud-init.conf` that sets `PasswordAuthentication yes`.
This file is **processed after** the main `sshd_config` and takes precedence over it.

**Practical consequence:** Changing `PasswordAuthentication no` in `/etc/ssh/sshd_config`
would have had zero effect. The override file would continue to enforce `yes`.

**How it was caught:** `sudo sshd -T` reads the fully-resolved effective configuration —
it processes the main config, all `Include` directives, and all override files in order,
then outputs what the running daemon actually sees. The change had to be made in
`50-cloud-init.conf`, not the main file.

This is the difference between reading a config file and reading what the service
actually runs with. `sshd -T` is the authoritative source.

### Interview Talking Points

**"How would you harden SSH access on a Linux server?"**

> "The main changes are key-only authentication and optionally restricting the source IPs
> or interfaces SSH listens on. For key auth specifically, the sequence matters: deploy the
> key, verify login works from a second connection, then disable passwords with `systemctl
> reload` rather than restart — reload preserves your current session while applying the
> new config. If the key setup is wrong and you've already disabled passwords, you're
> locked out. On this server I also have Tailscale as a backup access path, but the
> correct approach is to verify before disabling, not rely on a recovery path."

---

## Rollback Methodology

The same pattern is used across every change in this lab:

**1. Backup with a dated filename**
```bash
sudo cp /etc/service/config /etc/service/config.bak-$(date +%Y%m%d)
```
Dated filename prevents confusion between the backup and the live file.

**2. Validate before restarting**
- Samba: `sudo testparm --suppress-prompt`
- SSH: `sudo sshd -T` (reads live config including defaults and overrides)
- UFW: `sudo ufw show added` before enabling

**3. Verify access paths before and after**
Confirm Tailscale is connected and LAN SSH is available before touching any
network-adjacent service. Verify connectivity immediately after each change.

**4. One change at a time**
Each change is tested before the next one begins. Stacking multiple untested
changes makes root-cause analysis significantly harder if something breaks.

**SSH rollback:**
```bash
sudo cp /etc/ssh/sshd_config.d/50-cloud-init.conf.bak-20260529 \
    /etc/ssh/sshd_config.d/50-cloud-init.conf
sudo sshd -T | grep passwordauthentication
sudo systemctl reload ssh
```

**Samba rollback:**
```bash
sudo cp /etc/samba/smb.conf.bak-20260529 /etc/samba/smb.conf
sudo testparm --suppress-prompt
sudo systemctl restart smbd nmbd
```

**UFW rollback:**
```bash
sudo ufw disable          # emergency: remove all filtering
# or
sudo ufw delete [rule]    # remove specific rule without disabling
sudo ufw reload           # re-apply ruleset without disable/enable cycle
```

### Interview Talking Point

**"How do you approach making changes to a live system?"**

> "Backup first, always with a dated filename so there's no confusion about which file
> is the live one. Validate the configuration with the service's own config-check tool
> before restarting anything — `testparm` for Samba, `sshd -T` for SSH. Make one change
> at a time and verify connectivity before making the next one. And know the exact rollback
> command before you start, not after something breaks."

---

## Technical Reference

### Host-based vs. network firewall

A host-based firewall (UFW) runs on the server itself and controls what traffic the
OS accepts. A network firewall (pfSense) sits between network segments and controls
what traffic can pass between them.

Both serve different purposes. A network firewall doesn't protect a host from threats
that originate on the same network segment. A host-based firewall provides protection
that survives even if the network perimeter is bypassed.

### Defense in depth on `esther`

```
Layer 1: Tailscale — zero-trust VPN, no exposed ports to internet
Layer 2: UFW — deny-by-default host firewall, LAN-scoped rules
Layer 3: Service access controls — Samba valid users, Docker health checks
Layer 4: Authentication — SSH key-only (enforced), Samba guest = Never
```

### `systemctl reload` vs. `systemctl restart`

`restart` stops the service and starts it again — active connections drop during the
transition. `reload` sends the service a signal to re-read its configuration without
stopping — existing sessions are preserved. Use `reload` for config changes on services
with active connections (SSH, Nginx). Use `restart` when the service state itself needs
to be cleared.

### What `testparm` does

`testparm` parses the Samba configuration file and reports any syntax errors or unknown
parameters without modifying anything or restarting the service. Running it after an
edit and before a restart is the standard Samba change workflow. An equivalent exists
for most well-maintained services: `sshd -T` for SSH, `nginx -t` for Nginx,
`named-checkconf` for BIND.
