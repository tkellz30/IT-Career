# Verification and Testing Methodology

Documents the validation approach used across all configuration changes in this lab.
The same pattern is applied consistently regardless of which service is being changed.

---

## Core Principle: Validate Before Restart

Every service change in this lab follows a four-step sequence:

1. **Backup** — dated filename before any edit
2. **Validate** — service's own config checker before restart
3. **Restart** — only after validation passes
4. **Verify** — confirm service is running and access paths still work

Skipping step 2 turns every service restart into a gamble. Running a config checker is
a one-second operation that eliminates the class of failure where a typo kills a running
service and requires manual rollback under pressure.

---

## Validation Tools by Service

| Service | Command | What It Checks |
|---|---|---|
| Samba | `sudo testparm --suppress-prompt` | smb.conf syntax, unknown parameters, effective config with defaults |
| SSH | `sudo sshd -T` | sshd_config including all includes and runtime defaults |
| Nginx | `sudo nginx -t` | nginx.conf syntax |
| Apache | `sudo apachectl configtest` | httpd.conf syntax |
| UFW | `sudo ufw show added` | staged ruleset before enabling |
| systemd units | `systemd-analyze verify <unit>` | unit file syntax and dependencies |

---

## Backup Convention

```bash
sudo cp /etc/service/config /etc/service/config.bak-$(date +%Y%m%d)
```

Dated filename prevents confusion between the backup and the live file. Multiple changes
on the same day use `+%Y%m%d-%H%M%S` for second-level granularity.

---

## Samba Hardening — Verification Record (2026-05-29)

**Change:** `map to guest = Bad User → Never`, `usershare allow guests = Yes → No`  
**Backup:** `/etc/samba/smb.conf.bak-20260529`

### Pre-Change Audit

```bash
sudo testparm --suppress-prompt | grep -E "map to guest|usershare"
# map to guest = Bad User
# usershare allow guests = Yes
```

### Edit

```bash
sudo sed -i 's/map to guest = bad user/map to guest = Never/i' /etc/samba/smb.conf
sudo sed -i 's/usershare allow guests = yes/usershare allow guests = No/i' /etc/samba/smb.conf
```

### Validation

```bash
sudo testparm --suppress-prompt
# Result: Loaded services file OK.
```

### Restart

```bash
sudo systemctl restart smbd nmbd
```

### Verification

```bash
sudo systemctl status smbd nmbd
# smbd.service: active (running) ✅
# nmbd.service: active (running) ✅
```

**Evidence:** `screenshots/final/04-samba-services-after-hardening.png`

### Rollback (if needed)

```bash
sudo cp /etc/samba/smb.conf.bak-20260529 /etc/samba/smb.conf
sudo testparm --suppress-prompt
sudo systemctl restart smbd nmbd
```

---

## SSH Key Authentication — Verification Record (2026-05-29)

**Change:** `PasswordAuthentication yes → no`  
**Change target:** `/etc/ssh/sshd_config.d/50-cloud-init.conf` (Ubuntu 24.04 cloud-init override — not main sshd_config)  
**Backup:** `/etc/ssh/sshd_config.d/50-cloud-init.conf.bak-20260529`  
**Key algorithm:** ED25519, passphrase-protected, comment `trea-homelab`

### Pre-Change Audit

```bash
sudo sshd -T | grep -E "passwordauthentication|kbdinteractiveauthentication|usepam"
# passwordauthentication yes     ← active via override file
# kbdinteractiveauthentication no
# usepam yes

ls /etc/ssh/sshd_config.d/
# 50-cloud-init.conf              ← source of active PasswordAuthentication yes
```

### Backup

```bash
sudo cp /etc/ssh/sshd_config.d/50-cloud-init.conf \
    /etc/ssh/sshd_config.d/50-cloud-init.conf.bak-$(date +%Y%m%d)
```

### Edit

```bash
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' \
    /etc/ssh/sshd_config.d/50-cloud-init.conf
```

### Validation

```bash
sudo sshd -T | grep passwordauthentication
# Result: passwordauthentication no ✅
```

### Reload (not restart)

```bash
sudo systemctl reload ssh
# Active sessions preserved through reload
```

### Verification

```bash
sudo systemctl status ssh --no-pager
# ssh.service: active (running) ✅
```

Three-session verification sequence:
- Session 1 (password-capable) remained open throughout
- Session 2 (key auth) verified before any config change
- Session 3 (new connection post-reload) confirmed key auth still works ✅

**Evidence:** `screenshots/final/05-ssh-key-generated.png`, `screenshots/final/06-ssh-key-auth-success.png`, `screenshots/final/07-ssh-key-only-enforced.png`

### Rollback (if needed)

```bash
sudo cp /etc/ssh/sshd_config.d/50-cloud-init.conf.bak-20260529 \
    /etc/ssh/sshd_config.d/50-cloud-init.conf
sudo sshd -T | grep passwordauthentication
sudo systemctl reload ssh
```

---

## UFW Deployment — Verification Record (2026-05-27)

**Change:** UFW enabled with deny-by-default inbound policy

### Pre-Change

```bash
sudo ufw show added     # reviewed full ruleset before enabling
```

### Enable

```bash
sudo ufw --force enable
```

### Verification

```bash
sudo ufw status verbose
# Status: active, Default: deny (incoming)
# SSH, Samba (LAN-scoped), Tailscale WireGuard rules confirmed ✅
```

**Evidence:** `screenshots/final/01-ufw-active-status.png`
