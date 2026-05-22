"""
Pi-hole screenshot sanitizer — targeted blur standard.

REDACTION RULES
===============
Blur (Gaussian, radius >= 12):
  - Private IPs (10.x, 172.16-31.x, 192.168.x)
  - Public IPs when shown in a local context (URL bar)
  - MAC / hardware addresses
  - Hostnames and device names (*.lan, *.local, custom names)
  - Usernames, profile names, SSIDs
  - Client names visible in Pi-hole tables
  - Browser address-bar local URL (full text from security icon through path)
  - Serial numbers or unique device identifiers

Leave visible:
  - Dashboard metrics and graphs
  - Enabled / disabled status indicators
  - Public blocklist URLs
  - Generic UI labels (Dashboard, Query Log, Groups, etc.)
  - Column headers and table structure
  - "Uses Pi-hole" checkmarks
  - Interface names (eth0, lo, wlan0)
  - Timestamps and query counts

Technique: Gaussian blur (not solid fills). Blurring keeps the region
shape visible so the screenshot still reads as real data, while making
every character unreadable.

COORDINATE NOTES (verified on 1920x1032 originals, 2026-05-22)
================================================================
URL bar:
  Browser chrome: tab bar y=0-90, address bar y=90-108, Pi-hole header y=108-175.
  URL text "⚠ Not secure  192.168.0.101/admin/" sits at y=58-69, x=130-395.
  Box uses generous padding: (125, 53, 410, 74).

Hostname badge:
  "hostname: Pi-Hole-1" in Pi-hole top-right header.
  Verified at x=1340-1590, y=132-168 via color-deviation pixel scan.
  NOT at the x=1078 region — that area is dark background.

Network table columns (image 02):
  Column headers sit at y≈308-340; data rows start at y≈340.
  IP+hostname col: x=440-720. Hardware/MAC col: x=720-865.

Top Clients columns (image 01.2):
  Card + column-header overhead ≈95px; data rows start at y≈775.
  Left table (total) client col: x=455-645.
  Right table (blocked only) client col: x=872-1060.
"""

from PIL import Image, ImageFilter
import os

SRC = r"c:\Users\TraeKelly\Documents\IT-Career\homelab\pihole-dns-filtering-lab\screenshots\Originals"
DST = r"c:\Users\TraeKelly\Documents\IT-Career\homelab\pihole-dns-filtering-lab\screenshots\final"


# ── Blur helpers ─────────────────────────────────────────────────────────────

def blur(img, box, radius=18):
    """Gaussian-blur a rectangular region in-place.

    Prefer this over solid fills — keeps visual context while making
    text unreadable. Increase radius for larger or denser regions.
    """
    x1, y1, x2, y2 = (int(v) for v in box)
    region = img.crop((x1, y1, x2, y2))
    img.paste(region.filter(ImageFilter.GaussianBlur(radius)), (x1, y1))


def pixelate(img, box, cell=10):
    """Pixelate a rectangular region (resize down then back up).

    Alternative to blur when you want a clearly-redacted mosaic look.
    Useful for very small regions where blur might still hint at length.
    """
    x1, y1, x2, y2 = (int(v) for v in box)
    w, h = x2 - x1, y2 - y1
    region = img.crop((x1, y1, x2, y2))
    small = region.resize((max(1, w // cell), max(1, h // cell)), Image.BOX)
    img.paste(small.resize((w, h), Image.NEAREST), (x1, y1))


# ── Shared sensitive regions — verified pixel coordinates ─────────────────────

# Browser address bar: "⚠ Not secure  192.168.0.101/admin/"
# Text confirmed at y=58-69, x=130-395. Box adds padding on all sides.
URL_TEXT = (125, 53, 410, 74)

# Pi-hole top-right header badge: "hostname: Pi-Hole-1"
# Confirmed at x=1340-1590, y=132-168 via color-deviation scan across all images.
HOSTNAME_BADGE = (1340, 132, 1590, 168)


# ── Per-screenshot redaction map ──────────────────────────────────────────────
# Each entry: list of (function, box, kwargs).
# To add a future screenshot, append a new key following the same pattern.

REDACTIONS = {

    # ── 01: Main dashboard ───────────────────────────────────────────────────
    # Sensitive: local IP in URL bar, Pi-hole hostname badge.
    # Safe:      query counts, blocked %, domain count, all charts.
    "01-pihole-dashboard-sanitized.png": [
        (blur, URL_TEXT,       {"radius": 14}),
        (blur, HOSTNAME_BADGE, {"radius": 14}),
    ],

    # ── 01.2: Scrolled dashboard ─────────────────────────────────────────────
    # Sensitive: URL bar, hostname badge, client device names in both tables.
    # Safe:      top permitted/blocked domain lists (public external domains),
    #            request counts, frequency bars.
    # Client column x-ranges: left=455-645, right=872-1060.
    # Data rows confirmed starting at y≈775 (below card title + col-header rows).
    "01.2-pihole-dashboard-sanitized.png": [
        (blur, URL_TEXT,                  {"radius": 14}),
        (blur, HOSTNAME_BADGE,            {"radius": 14}),
        (blur, (455, 775, 645, 1032),     {"radius": 16}),  # "Top Clients (total)" client col
        (blur, (872, 775, 1060, 1032),    {"radius": 16}),  # "Top Clients (blocked only)" client col
    ],

    # ── 02: Network overview ─────────────────────────────────────────────────
    # Sensitive: URL bar, hostname badge, IP+hostname column, MAC column.
    # Safe (left visible): column headers, Interface (eth0/lo), First seen,
    #   Last Query, Number of queries, "Uses Pi-hole" checkmarks, Action buttons.
    # Column x-ranges verified: IP+hostname=440-720, Hardware/MAC=720-865.
    # Table header row (y≈308-340) left untouched for context.
    "02-query-log-blocked-allowed-sanitized.png": [
        (blur, URL_TEXT,                  {"radius": 14}),
        (blur, HOSTNAME_BADGE,            {"radius": 14}),
        (blur, (440, 340, 720, 1032),     {"radius": 20}),  # IP address + hostname cells
        (blur, (720, 340, 865, 1032),     {"radius": 20}),  # Hardware / MAC address cells
    ],

    # ── 03: Adlists management ───────────────────────────────────────────────
    # Sensitive: URL bar, hostname badge.
    # Safe:      public blocklist URLs, enabled/disabled status, group names.
    "03-adlists-configured.png": [
        (blur, URL_TEXT,       {"radius": 14}),
        (blur, HOSTNAME_BADGE, {"radius": 14}),
    ],

}


# ── Runner ────────────────────────────────────────────────────────────────────

os.makedirs(DST, exist_ok=True)

for filename, ops in REDACTIONS.items():
    src_path = os.path.join(SRC, filename)
    dst_path = os.path.join(DST, filename)

    img = Image.open(src_path).convert("RGB")

    for fn, box, kwargs in ops:
        fn(img, box, **kwargs)

    img.save(dst_path, "PNG")
    print(f"  saved  {filename}")

print("Done.")
