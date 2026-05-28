# Docker Hardening — UFW Bypass Remediation

**Status:** 🔲 Planned — Phase 2  
**Prerequisite:** UFW active (complete) + confirmed understanding of Docker iptables behavior

---

## The Problem

Docker publishes ports by modifying iptables directly, bypassing UFW's INPUT chain entirely.
When you run a container with `-p 8096:8096`, Docker adds rules to the `DOCKER` and `DOCKER-USER`
iptables chains. These are processed **before** UFW rules.

**Current exposure:**
- Port 8096 (Jellyfin): accessible from all interfaces, ignoring UFW
- Port 9443 (Portainer): accessible from all interfaces, ignoring UFW

---

## Solution Options

### Option A — Bind Ports to Specific Interface (Recommended)

Instead of binding to `0.0.0.0` (all interfaces), bind to a specific IP address.

**Modify Jellyfin docker-compose.yml:**
```yaml
ports:
  - "192.168.x.x:8096:8096"    # LAN only
  # or
  - "100.x.x.x:8096:8096"   # Tailscale only
```

**Trade-off:** Must update bind IP if LAN IP changes (another reason to use a static IP).

### Option B — DOCKER-USER Chain Rules

Add rules directly to the `DOCKER-USER` iptables chain, which Docker respects:

```bash
# Allow Jellyfin from LAN only
sudo iptables -I DOCKER-USER -p tcp --dport 8096 ! -s 192.168.0.0/24 -j DROP

# Allow Portainer from LAN only
sudo iptables -I DOCKER-USER -p tcp --dport 9443 ! -s 192.168.0.0/24 -j DROP
```

**Trade-off:** These rules don't persist across reboots without `iptables-persistent`.

### Option C — Disable Docker iptables Management (Advanced)

```json
// /etc/docker/daemon.json
{
  "iptables": false
}
```

Then manage all Docker networking through UFW manually.

**Trade-off:** Breaks Docker's default networking. Containers lose internet access unless you
manually configure masquerading. Complex and error-prone.

### Recommendation

**Use Option A** (bind to specific interface in docker-compose). It's the cleanest solution,
doesn't require iptables expertise, and survives Docker restarts without scripts.

---

## Implementation (When Ready)

> ⚠️ DO NOT implement this until you have confirmed LAN connectivity and Tailscale backup works.

```bash
# 1. Check current docker-compose location
find /home /opt /root -name 'docker-compose.yml' 2>/dev/null

# 2. Backup current configs
cp docker-compose.yml docker-compose.yml.bak

# 3. Edit port bindings (example for Jellyfin)
# Change: - "8096:8096"
# To:     - "192.168.x.x:8096:8096"

# 4. Apply changes
docker compose down && docker compose up -d

# 5. Verify container is running
docker ps

# 6. Verify from LAN device: http://192.168.x.x:8096
# 7. Verify from outside LAN (should fail): http://[external-ip]:8096
```

---

## Common Beginner Mistakes

1. **Enabling UFW and assuming Docker ports are now protected** — they are not.
2. **Setting `iptables: false` without understanding consequences** — Docker networking breaks.
3. **Not testing from an external IP** — the only way to verify the restriction works.
4. **Forgetting to update port bindings after changing LAN IP** — services stop being reachable.
