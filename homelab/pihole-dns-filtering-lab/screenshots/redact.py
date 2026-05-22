"""
Sanitize Pi-hole screenshots for public GitHub publishing.
Redacts: local IP in URL bar, Pi-hole hostname label, internal device
hostnames in Top Clients tables, and all network table rows (IPs, MACs,
hostnames, vendors).

Coordinates verified by pixel-level crop inspection of 1920×1032 originals.
"""

from PIL import Image, ImageDraw
import os

SRC = r"c:\Users\TraeKelly\Documents\IT-Career\homelab\pihole-dns-filtering-lab\screenshots\Originals"
DST = r"c:\Users\TraeKelly\Documents\IT-Career\homelab\pihole-dns-filtering-lab\screenshots\final"

BLACK = (0, 0, 0)

# ── Regions shared across all four screenshots ─────────────────────────────
# Browser address bar: covers "192.168.0.101/admin/" in Brave dark-mode chrome
URL_BAR         = (285,  28, 1545,  63)
# Pi-hole top-right header: "hostname: Pi-Hole-1" badge (confirmed y=130-162)
PIHOLE_HOSTNAME = (1050, 128, 1920, 165)

REDACTIONS = {
    # Dashboard overview – only URL + hostname sensitive; sidebar is decorative
    "01-pihole-dashboard-sanitized.png": [
        URL_BAR,
        PIHOLE_HOSTNAME,
    ],

    # Dashboard scrolled – Top Clients tables expose internal device hostnames
    "01.2-pihole-dashboard-sanitized.png": [
        URL_BAR,
        PIHOLE_HOSTNAME,
        # "Top Clients (total)" – entire Client column (LGwebOSTv.lan, etc.)
        (460, 680, 640, 1032),
        # "Top Clients (blocked only)" – entire Client column
        (882, 680, 1080, 1032),
    ],

    # Network overview – all data rows contain IPs, MACs, hostnames; keep headers
    "02-query-log-blocked-allowed-sanitized.png": [
        URL_BAR,
        PIHOLE_HOSTNAME,
        # Network table data rows (column header row left visible for context)
        (460, 335, 1910, 1032),
    ],

    # Adlists – blocklist URLs are public; only URL bar + hostname are sensitive
    "03-adlists-configured.png": [
        URL_BAR,
        PIHOLE_HOSTNAME,
    ],
}

os.makedirs(DST, exist_ok=True)

for filename, boxes in REDACTIONS.items():
    src_path = os.path.join(SRC, filename)
    dst_path = os.path.join(DST, filename)

    img  = Image.open(src_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    for box in boxes:
        draw.rectangle(box, fill=BLACK)

    img.save(dst_path, "PNG")
    print(f"  saved  {filename}")

print("Done.")
