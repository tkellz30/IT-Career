# Troubleshooting Reference

Quick-reference summary of issues encountered during the homelab build. Each entry links to the detailed log in `docs/troubleshooting-log.md`.

---

## Issue Index

| # | Area | Symptom | Status |
|---|------|---------|--------|
| 001 | Hardware / BIOS | BIOS did not detect SSD on first boot | Resolved |
| 002 | OS Installation | Ubuntu installer USB would not boot | Resolved |
| 003 | SSH | Connection refused after OS install | Resolved |
| 004 | Tailscale | Node not appearing in admin console | Resolved |
| 005 | Docker | Container exited immediately — port conflict | Resolved |
| 006 | Storage | Secondary drive not mounting after reboot | Resolved |
| 007 | Jellyfin | Media library scan returned no results | Resolved |
| 008 | Samba | SMB share not accessible from Windows | Resolved |

For full details on each issue (symptom → investigation → fix → lesson), see [docs/troubleshooting-log.md](docs/troubleshooting-log.md).

---

## Quick Diagnostic Commands

Use these first when something stops working.

**Service not reachable?**
```bash
sudo systemctl status <service>
journalctl -xe --no-pager | tail -30
```

**Container not running?**
```bash
docker ps -a
docker logs <container_name>
```

**Port conflict?**
```bash
sudo ss -tuln
```

**Drive not mounted?**
```bash
lsblk
df -h
sudo mount -a
```

**Can't reach service from the network?**
```bash
sudo ufw status
```

**Permission errors?**
```bash
ls -lh /path/to/directory
sudo chown -R user:group /path/to/directory
```
