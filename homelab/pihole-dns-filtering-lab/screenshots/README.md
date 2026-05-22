# Screenshots — Pi-hole DNS Filtering Lab

This folder will contain screenshots documenting the Pi-hole DNS filtering lab. All screenshots must be reviewed for sensitive information before publishing.

## Privacy Review Checklist

Before publishing any screenshot, confirm:

- [ ] All private IP addresses are blurred or cropped
- [ ] All real client and device hostnames are blurred
- [ ] No personal domain names are visible
- [ ] No account usernames or email addresses are visible
- [ ] No MAC addresses are visible in logs or ARP tables
- [ ] Pi prompt / shell prompt does not expose hostname or username

---

## Planned Screenshots

| # | Filename (suggested) | Description | Status |
|---|----------------------|-------------|--------|
| 01 | `01-pihole-dashboard-overview.png` | Pi-hole web dashboard — total queries, blocked %, top blocked domains. Blur all client IPs. | Pending |
| 02 | `02-pihole-query-log.png` | Live query log showing recent DNS requests. Blur all client names and IPs in the log. | Pending |
| 03 | `03-pihole-adlists.png` | Adlist/gravity configuration page — blocklist URLs and domain counts visible | Pending |
| 04 | `04-pihole-upstream-dns-settings.png` | Pi-hole Settings → DNS showing upstream set to `127.0.0.1#5335` (Unbound) | Pending |
| 05 | `05-unbound-service-status.png` | `sudo systemctl status unbound` output in terminal showing active/running state. Blur hostname in prompt. | Pending |
| 06 | `06-unbound-dig-test.png` | `dig google.com @127.0.0.1 -p 5335` output confirming Unbound responds on port 5335 | Pending |
| 07 | `07-router-dns-settings.png` | Router DHCP/LAN settings page showing Pi-hole IP as primary DNS. Blur all IPs. | Pending |
| 08 | `08-deco-ap-mode.png` | Deco app showing mesh units configured in AP mode | Pending |
| 09 | `09-blocked-query-example.png` | Pi-hole query log entry for a blocked domain (e.g., `doubleclick.net`) returning `0.0.0.0` | Pending |
| 10 | `10-allowed-query-example.png` | Pi-hole query log entry for an allowed domain resolving normally | Pending |
| 11 | `11-whitelist-example.png` | Pi-hole whitelist/allowlist page with at least one entry visible | Pending |
| 12 | `12-nslookup-before-pihole.png` | `nslookup` output with DNS pointing to ISP resolver or router (before Pi-hole was configured) | Pending |
| 13 | `13-nslookup-after-pihole.png` | `nslookup` output with DNS resolving through Pi-hole | Pending |
| 14 | `14-pihole-status-terminal.png` | `pihole status` or `pihole -c` in terminal confirming Pi-hole is running. Blur hostname/IP in prompt. | Pending |
| 15 | `15-top-blocked-domains.png` | Pi-hole dashboard top blocked domains list | Pending |

---

## Screenshot Notes

**Tools for blurring sensitive data:**
- **Paint.NET** (free, Windows) — select a region, then Effects → Blurs → Gaussian Blur
- **GIMP** (free, cross-platform) — Filters → Blur → Gaussian Blur on a selection
- **Windows Snipping Tool + Paint** — crop first in Snipping Tool, then use Paint's blur or pixel tool

**What to capture from the Pi-hole dashboard:**
- Dashboard is accessed at `http://[pi-ip]/admin` on your local network
- Take screenshots before blurring IPs, then apply blur in an editor before saving to this folder
- Capture at a reasonable resolution — 1280×800 or higher

**Terminal screenshots:**
- Use a clean terminal session before capturing
- If your shell prompt shows your hostname or username, either customize the `PS1` before the session or blur it afterward
- Example clean prompt to set temporarily: `PS1="pi@[redacted]:~$ "`

**After capturing:**
- Add the filename to the table above
- Update the Status column from "Pending" to "Done"
- Update the main lab README to reference the screenshot file if it adds context

---

*Screenshots should be placed directly in this folder. No subfolders needed.*
