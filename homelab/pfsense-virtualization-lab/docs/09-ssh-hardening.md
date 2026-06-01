# SSH Key Authentication Hardening

**Server:** `esther` | **OS:** Ubuntu 24.04 LTS  
**Completed:** 2026-05-29 | **Related:** [docs/08-security-review.md](08-security-review.md)

---

## What Changed

Password-based SSH authentication was disabled on `esther`. The server now accepts only
ED25519 public key authentication. Any connection attempt without a valid private key is
rejected before a password prompt is offered.

The change was applied to `/etc/ssh/sshd_config.d/50-cloud-init.conf` — not to the main
`/etc/ssh/sshd_config` — because of an Ubuntu 24.04 cloud-init override described below.

---

## Why Password Authentication Was Disabled

SSH password authentication is the primary attack vector for:

- **Brute-force attacks** — automated tools can attempt thousands of password combinations
  per minute against an open SSH port
- **Credential stuffing** — passwords reused from other breached services can succeed
  immediately on the first attempt

`esther` has no WAN-exposed SSH port (Tailscale handles all remote access), so the
immediate risk was LAN-only. But Tailscale does not prevent a compromised LAN device from
attempting logins. Disabling password auth eliminates the attack surface entirely at the
authentication layer rather than relying on the assumption that no LAN device is malicious.

A stolen or guessed password grants full shell access. A stolen private key is harder to
exfiltrate silently and can be revoked instantly by removing the corresponding entry from
`authorized_keys` — without changing any credentials.

---

## Why ED25519 Was Used

ED25519 is the current recommended key type for SSH:

- **Short key, strong security** — 256-bit elliptic curve key equivalent to ~3000-bit RSA
  in resistance to classical attacks
- **Fast** — key operations are significantly faster than RSA
- **Fixed-length signature** — no timing side-channel from variable-length RSA operations
- **Default in modern clients** — `ssh-keygen` defaults to ED25519 in OpenSSH 9+; broad
  client support on Windows, macOS, and Linux

The key was generated on the Windows client with:

```powershell
ssh-keygen -t ed25519 -C "trea-homelab"
```

The `-C` comment is metadata only — it has no effect on authentication. It makes the key
identifiable in `authorized_keys` and in `ssh-add -l` output.

---

## The Ubuntu 24.04 Cloud-Init Override: Why `sshd_config` Alone Is Not Enough

Ubuntu 24.04 cloud images ship with a drop-in override file at:

```
/etc/ssh/sshd_config.d/50-cloud-init.conf
```

This file contains:

```
PasswordAuthentication yes
```

OpenSSH processes `/etc/ssh/sshd_config.d/*.conf` files **before** the main
`/etc/ssh/sshd_config`. When two files set the same directive, the **first match wins**
in standard OpenSSH config processing. Because `sshd_config.d/` files load first,
`50-cloud-init.conf` was overriding any `PasswordAuthentication no` set in the main
`sshd_config`.

The fix was to change the value in the override file itself:

```bash
sudo nano /etc/ssh/sshd_config.d/50-cloud-init.conf
# Change: PasswordAuthentication yes  →  PasswordAuthentication no
```

This is why **checking the effective configuration with `sshd -T` matters more than
reading `sshd_config` directly** — see the next section.

---

## What `authorized_keys` Does

`~/.ssh/authorized_keys` is a plain text file on the server that lists every public key
allowed to authenticate as that user. Each line is one key in the format:

```
<key-type> <base64-key> <comment>
```

Example:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... trea-homelab
```

When a client connects, SSH performs a cryptographic challenge:
1. The server checks `authorized_keys` for the client's public key
2. If found, the server sends a challenge encrypted with that public key
3. Only a client holding the matching **private key** can decrypt and respond correctly
4. The private key never leaves the client machine — the server only ever sees the
   public key and the challenge response

The public key in `authorized_keys` is safe to share — it cannot be used to impersonate
the owner or derive the private key.

---

## What `sshd -T` Does and Why It Is More Authoritative Than Reading `sshd_config`

`sshd -T` dumps the **effective running configuration** of the SSH daemon — the result of
processing `sshd_config`, all `sshd_config.d/*.conf` files, compiled-in defaults, and
any command-line flags, in order.

```bash
sudo sshd -T | grep passwordauthentication
# Expected output:  passwordauthentication no
```

Reading `sshd_config` directly only shows what is in that one file. It does not show:
- Overrides from `sshd_config.d/` drop-in files
- Directives inherited from compiled defaults
- The actual precedence resolution when two files conflict

`sshd -T` is the ground truth. If `sshd -T` says `passwordauthentication no`, the running
daemon will not accept passwords — regardless of what any individual config file says.

This is the SSH equivalent of:
- `testparm --suppress-prompt` for Samba
- `nginx -t` for Nginx
- `apachectl configtest` for Apache

Always validate with `sshd -T` before and after any SSH config change.

---

## Why `systemctl reload ssh` Is Safer Than `restart` During Remote Hardening

| Action | Effect on existing sessions |
|--------|---------------------------|
| `systemctl restart ssh` | **Drops all active SSH connections** — process restarts |
| `systemctl reload ssh` | Signals the daemon to re-read its config — **existing sessions stay open** |

When making SSH config changes over a remote connection:
- If the change breaks authentication and you use `restart`, you lose your only session
- If you use `reload`, your current session survives — you can diagnose and revert

The change used:

```bash
sudo systemctl reload ssh
```

After reload, a **new** SSH connection was opened from a fresh terminal window to confirm
key auth still worked. Only after that confirmation was the original session closed.

---

## The Three-Session Verification Sequence

The lockout prevention approach used three separate SSH sessions:

**Session 1 — Original connection (stays open throughout)**  
An existing SSH session, connected before any changes. If anything goes wrong, this
session is the recovery path.

**Session 2 — Verify key auth works before disabling passwords**  
A new SSH connection using the ED25519 key explicitly:

```powershell
ssh -i $env:USERPROFILE\.ssh\id_ed25519 <username>@<tailscale-ip>
```

This proves key-based login works **before** password auth is turned off. If this fails,
do not proceed — diagnose why the key auth failed first.

**Session 3 — Verify key auth still works after reload**  
After `PasswordAuthentication no` is set and `systemctl reload ssh` is run, open a
brand-new connection to confirm:
- The reload applied the change (not just queued it)
- Key auth continues to work under the new config
- The session itself came in without being prompted for a password

Only after Session 3 confirms successful key-only login is the change considered verified.

---

## Evidence

| Screenshot | What It Shows |
|---|---|
| [05-ssh-key-generated.png](../screenshots/final/05-ssh-key-generated.png) | `ssh-keygen -t ed25519` on Windows — key generation with fingerprint |
| [06-ssh-key-auth-success.png](../screenshots/final/06-ssh-key-auth-success.png) | Session 2: key auth succeeds before passwords are disabled |
| [07-ssh-key-only-enforced.png](../screenshots/final/07-ssh-key-only-enforced.png) | Session 3: `sshd -T` shows `passwordauthentication no` post-reload |

---

*Last updated: 2026-05-29*
