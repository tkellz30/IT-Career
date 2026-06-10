# VLAN, Switch, and Access Point Design (Future Plan)

**Status:** 🔲 Planned — long-term design notes only. To be implemented **after**
basic pfSense routing and Wi-Fi are working, not before.  
**Depends on:** [docs/11-production-router-migration.md](11-production-router-migration.md)
reaching a stable, validated cutover first.

---

## Why This Comes Second

VLAN segmentation adds real configuration surface area: trunk ports, tagged/untagged
VLAN assignment, inter-VLAN routing rules on pfSense, and AP SSID-to-VLAN mapping.
Combining that complexity with an already-risky router cutover would make it much
harder to isolate the cause of any problem that comes up.

**The plan is deliberately sequenced:**
1. Get `pfsense-prod` routing basic LAN traffic and providing working Wi-Fi through
   the Cisco AP and Deco — a single flat network, no VLANs.
2. Confirm that baseline is stable for a meaningful period.
3. **Only then** introduce VLANs, one at a time, validating connectivity after each addition.

This mirrors the same incremental-risk philosophy used throughout the project (e.g.,
validating the pfSense lab in complete isolation before testing firewall rules, and
testing rules individually before considering the lab "validated").

---

## Target Switch / AP Topology (End State)

```
pfSense-prod (LAN side, via eno1)
        │
        ▼
PoE VLAN-capable switch  ← LAN core
   │
   ├── Trunk port ──► Cisco AP  (carries multiple VLAN SSIDs: Home, Lab, IoT/Media, Guest)
   │
   ├── Access port ──► Deco AP  (single VLAN — likely Home or IoT/Media — TV/PlayStation bridge)
   │
   └── Access ports ──► Wired devices (assigned to appropriate VLANs per device purpose)
```

---

## Roles

### PoE VLAN-Capable Switch — LAN Core

- Becomes the central distribution point for all wired LAN connections downstream of `pfsense-prod`
- Will eventually carry multiple VLANs as tagged (trunk) or untagged (access) traffic depending on the port
- **Initial setup should be basic** — no VLANs configured — so it can be brought online
  and verified as a plain switch first (see Phase 6 of
  [checklists/production-router-cutover.md](../checklists/production-router-cutover.md))

### Cisco Access Point — Trunk Port, Multi-VLAN SSIDs

- Connects to the switch via a **trunk port** carrying multiple tagged VLANs
- Each VLAN maps to a separate SSID (e.g., a "Home" SSID on the Trusted VLAN, a "Guest"
  SSID on the Guest VLAN, etc.)
- Becomes the **main Wi-Fi access point** for the household once configured
- This is the more capable device and is the natural home for VLAN-aware SSIDs

### Deco AP — Access Port, Single VLAN

- Already in **AP mode** (not router mode) — no change to its operating mode
- Connects to the switch via a simple **access port** carrying a single, untagged VLAN
  (likely **Home/Trusted** or **IoT/Media**, depending on what ends up connected to it)
- Used primarily as a **wireless bridge for the TV and PlayStation**, leveraging the
  second Deco satellite unit's wired Ethernet ports
- Does not need (and should not be given) trunk/multi-VLAN configuration — keeping its
  role simple reduces both configuration complexity and risk

---

## Suggested VLAN Plan

| VLAN | Purpose | Example members |
|---|---|---|
| **Home / Trusted** | Primary household devices, personal computers, phones | Trusted personal devices |
| **Lab** | Homelab and testing devices | `esther`, future test VMs/devices, lab equipment |
| **IoT / Media** | Smart-home devices, streaming/media devices | TV, PlayStation, smart-home gadgets |
| **Guest** | Visitor Wi-Fi, isolated from internal resources | Guest phones/laptops |
| **Management / Admin** | Administrative access to network infrastructure | Switch/AP/pfSense management interfaces |

Notes:

- The **Lab** VLAN gives a clean way to keep homelab experimentation traffic separate
  from household devices — useful both for safety and for keeping the "production
  router" and "homelab" identities of `esther` from interfering with each other.
- The **Management/Admin** VLAN is a common best practice — it keeps the administrative
  interfaces of the switch, AP, and pfSense itself off the same broadcast domain as
  general user traffic, reducing exposure if a user device is ever compromised.
- The **Guest** VLAN should be configured with no route (or a tightly restricted route)
  to any other VLAN — visitors get internet access only.
- **IoT/Media** separation is a common recommendation because many smart-home and
  streaming devices have weaker security postures than general-purpose computers;
  isolating them limits the blast radius if one is compromised.

---

## Initial Simple Setup (Before VLANs)

Before any VLAN is configured, the goal is a single flat network that proves the
fundamentals work:

1. `pfsense-prod` routes LAN traffic and provides DHCP/DNS for the household
2. The PoE switch operates as a plain unmanaged-style switch (VLAN features present but unused)
3. The Cisco AP broadcasts a single SSID on the flat network
4. The Deco AP continues bridging the TV/PlayStation on that same flat network
5. All of the above is observed stable for a meaningful period

Only after that baseline is proven should VLANs be introduced — and even then,
**one VLAN at a time**, starting with the lowest-risk segment (e.g., Guest or IoT/Media,
which don't carry management or lab traffic) before tackling Management/Admin or Lab,
which are more sensitive to misconfiguration.

---

## Order of VLAN Introduction (Suggested, Once Baseline Is Stable)

1. **Guest** — fully isolated, easiest to validate ("can a guest device reach the
   internet but nothing else?"), lowest impact if misconfigured
2. **IoT / Media** — moderate isolation requirements, contains the TV/PlayStation
   already on the Deco bridge — a good second test of segmentation without disrupting
   primary household use
3. **Lab** — separates homelab traffic from household traffic; validate that `esther`
   and lab devices function correctly on their own segment
4. **Management / Admin** — move administrative interfaces onto their own VLAN; validate
   carefully, since misconfiguring this one can complicate management of the very
   devices you'd need to fix it
5. **Home / Trusted** — typically becomes "whatever's left" as the default/native VLAN
   once everything else has been carved out

> Each step should be validated independently before moving to the next — exactly the
> same incremental approach used for the physical cutover itself.

---

## Open Questions to Resolve During Implementation (Not Yet Answered)

- Exact VLAN ID numbering scheme (to be decided once the switch/AP models' defaults and constraints are reviewed)
- Whether inter-VLAN routing rules will live entirely in pfSense or partially on the switch
- Final placement of the Deco — Home/Trusted vs. IoT/Media — pending real-world testing
  of whether the TV/PlayStation experience differs meaningfully between the two
- Whether the Cisco AP's SSID-to-VLAN mapping needs additional licensing/feature support
  (to be confirmed against the specific AP model in use)

---

## Evidence / Screenshot Notes

Screenshot `26-switch-vlan-plan.png` (see
[docs/11-production-router-migration.md](11-production-router-migration.md#evidence--screenshot-plan))
is planned to capture the **basic, pre-VLAN** switch configuration — documenting the
"before" state prior to any VLAN work, consistent with this document's "basic setup
first" sequencing. Additional VLAN-specific screenshots will be planned in a future
update to this document once the baseline cutover is complete and VLAN work begins.

### Redaction Reminder

As with all other planned screenshots in this phase, before anything is committed
publicly: blur or redact public IPs, MAC addresses, Tailscale IPs, IPv6 addresses,
serial numbers, tokens/keys/passwords, sensitive hostnames, and unnecessary internal
network details (e.g., specific VLAN ID numbers or internal subnet ranges beyond what's
needed to illustrate the concept).
