# Networking Rollback Procedures

**Read this before making any network change. Know your exit before you enter.**

---

## Access Priority Ladder

Always verify the next level of access exists before making changes that could break the current level.

```
Level 1 (most reliable): Physical access / HDMI + keyboard on esther
Level 2:                  LAN SSH — ssh <username>@192.168.x.x
Level 3:                  Tailscale SSH — ssh <username>@100.x.x.x
Level 4 (current):       VS Code SSH via Tailscale
```

Before any networking change: **confirm Level 3 (Tailscale) works**, so you have a fallback if Level 4 breaks.

---

## UFW Rollback

### Scenario: Locked out after UFW enable

**Symptom:** SSH connection refused or timeout.

**If you have LAN access:**
```bash
ssh <username>@192.168.x.x
sudo ufw disable
# Verify: sudo ufw status → "Status: inactive"
```

**If you have physical access only:**
```bash
# Log in at the console
sudo ufw disable
# Or reset all rules and disable:
sudo ufw reset
```

**If you need to recover a specific rule:**
```bash
sudo ufw status numbered
sudo ufw delete [rule-number]
```

### Scenario: Tailscale drops after UFW enable

**Cause:** UDP 41641 (WireGuard) or tailscale0 interface traffic was blocked.

**Fix (if you still have LAN SSH):**
```bash
sudo ufw allow in on tailscale0
sudo ufw allow 41641/udp
sudo ufw reload
# Then verify: tailscale status
```

**Prevention:** Always verify `tailscale status` shows an active connection immediately after `ufw enable`.

---

## Samba Config Rollback

### Scenario: Samba shares inaccessible after config change

**Backup before any smb.conf edit:**
```bash
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak-$(date +%Y%m%d)
```

**Rollback:**
```bash
sudo cp /etc/samba/smb.conf.bak-YYYYMMDD /etc/samba/smb.conf
sudo systemctl restart smbd nmbd
sudo smbclient -L localhost -U <username>   # Verify shares visible
```

---

## KVM / Routing Rollback

### Scenario: pfSense VM causes routing issues

**Symptom:** `esther` itself loses outbound connectivity; Tailscale may still work.

**Fastest fix — stop the VM:**
```bash
virsh destroy pfsense    # Immediately kills VM, removes any routing it controlled
# Verify: ip route show  — should only show default via 192.168.x.1
```

**If virbr bridges created routing conflicts:**
```bash
virsh net-destroy labnet      # Stop the virtual network
virsh net-undefine labnet     # Remove definition
# Or temporarily:
ip link set virbr1 down
```

### Scenario: Bridged `eno1` caused LAN outage

> **This should never happen if you follow the checklist — DO NOT bridge eno1.**

**If it happens anyway:**
```bash
# Remove bridge, restore eno1
sudo ip link set eno1 nomaster
sudo ip link delete br0 type bridge    # or whatever bridge name was used
sudo dhclient eno1                     # Re-request DHCP lease
```

**Physical recovery if SSH is lost:**
```bash
# At the console:
sudo systemctl restart networking
# Or simply reboot (libvirt VMs will re-start based on autostart setting)
sudo reboot
```

---

## Docker Networking Rollback

### Scenario: Docker iptables rules cause unexpected blocking

**Restart Docker (re-creates all iptables rules):**
```bash
sudo systemctl restart docker
# Verify containers are still running:
docker ps
```

**Nuclear option — reset iptables (all Docker rules cleared):**
```bash
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X
sudo systemctl restart docker
sudo ufw reload    # Re-apply UFW rules
```
> ⚠️ This temporarily removes all firewall rules. Only use if Docker networking is fully broken.

---

## Complete System Recovery

### Scenario: Cannot reach `esther` by any remote method

1. Physical access to the server (HDMI + keyboard)
2. Log in as `<username>`
3. Check what's running: `systemctl list-units --state=failed`
4. Check network: `ip addr show && ip route show`
5. If UFW is blocking: `sudo ufw disable`
6. If routing is broken: `sudo systemctl restart systemd-networkd`
7. If Tailscale is down: `sudo systemctl restart tailscaled && tailscale status`
8. Once stable, investigate the root cause before re-enabling changes

---

## Pre-Change Safety Checklist

Run through this before **any** networking change:

```
[ ] I have verified Tailscale is showing active connection
[ ] I know the LAN IP of esther (192.168.x.x)
[ ] I have a fallback SSH method (LAN or physical)
[ ] I have backed up any config file I'm about to modify
[ ] I have staged/reviewed changes before applying
[ ] I know the exact rollback command for this change
[ ] I will test connectivity immediately after the change
[ ] I have not made any other changes in the last 15 minutes (one change at a time)
```

---

## Key Commands Reference Card

```bash
# UFW
sudo ufw status verbose          # Check firewall state
sudo ufw disable                 # Emergency disable (preserves rules)
sudo ufw reset                   # Nuclear: remove all rules + disable
sudo ufw reload                  # Apply rule changes without disable/enable cycle

# Tailscale
tailscale status                 # Check VPN state
sudo systemctl restart tailscaled

# Samba
sudo systemctl status smbd nmbd
sudo testparm                    # Validate smb.conf without restarting

# KVM
virsh list --all                 # List all VMs
virsh destroy [vm-name]          # Force stop VM
virsh snapshot-list [vm-name]    # List snapshots
virsh snapshot-revert [vm-name] [snap-name]  # Roll back VM

# Network state
ip addr show                     # All interfaces + IPs
ip route show                    # Routing table
ss -tlnp                         # Listening TCP ports
```
