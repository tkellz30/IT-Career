# pfSense Lab Validation

**Completed:** 2026-06-04  
**Environment:** Virtual lab on `esther` — KVM/libvirt, Ubuntu 24.04 LTS  
**Status:** ✅ Virtual firewall baseline validated  
**Related:** [docs/04-pfsense-planning.md](04-pfsense-planning.md) · [docs/03-kvm-libvirt-setup.md](03-kvm-libvirt-setup.md)

---

## Milestone: Virtual Firewall Baseline + Rule Validation

This document records the functional validation of the pfSense virtual lab after
deployment. All testing was conducted in an isolated virtual environment with no
impact to the home network, production router, or live client traffic.

---

## What Was Built

A dual-NIC pfSense CE 2.8.1 VM running on KVM/libvirt (`esther`) with:

- **WAN interface (`vtnet0`):** Connected to libvirt's default NAT network (`virbr0`).
  Internet access comes through double-NAT via the host. No physical NIC changes,
  no router modifications.

- **LAN interface (`vtnet1`):** Connected to an isolated libvirt bridge (`virbr-pflan`,
  network `pfsense-lab-lan`, subnet `10.50.0.0/24`). No physical bridge, no production
  LAN exposure.

- **Test client:** Debian 12 Live VM (`test-client`) attached only to `pfsense-lab-lan`,
  receiving all network configuration (DHCP, gateway, DNS) from pfSense.

---

## Topology Summary

```
esther host  (eno1 → home router — untouched throughout)
│
├── virbr0  (libvirt NAT, 192.168.122.0/24)
│     └── pfsense-lab WAN → vtnet0  (DHCP from libvirt NAT)
│
└── virbr-pflan  (isolated bridge, no host IP)
      └── pfsense-lab LAN → vtnet1  (10.50.0.1/24, DHCP server active)
            └── test-client VM  (DHCP → 10.50.0.100/24)
```

`eno1`, Tailscale, the home router, and all Deco units were untouched throughout.

---

## Validation Results

### Test Client Network Connectivity

Debian Live test client (`test-client` VM on `pfsense-lab-lan`):

| Check | Result |
|---|---|
| DHCP assignment | `10.50.0.100/24` from pfSense ✅ |
| Default gateway | `10.50.0.1` via pfSense LAN ✅ |
| Ping pfSense gateway | `10.50.0.1` — 0% loss, sub-1ms ✅ |
| Ping internet (`8.8.8.8`) | 0% loss through pfSense NAT ✅ |
| DNS resolution | `google.com` resolves and responds ✅ |
| pfSense web GUI reachability | HTTP/2 200 from `https://10.50.0.1` via curl ✅ |

**Evidence:** `screenshots/final/16-test-client-network-verified.png`

### pfSense Web GUI

- Accessible via SSH tunnel → `https://127.0.0.1:8443` → pfSense LAN at `10.50.0.1`
- pfSense CE 2.8.1-RELEASE dashboard confirmed
- WAN/LAN interface assignment correct: `vtnet0` WAN, `vtnet1` LAN
- Default admin password changed

**Evidence:** `screenshots/final/13-pfsense-dashboard.png`

---

## Firewall Rule Test

### Rule Created

A targeted LAN rule was added via the pfSense web GUI:

| Field | Value |
|---|---|
| Action | Block |
| Interface | LAN |
| Protocol | IPv4 ICMP |
| Source | `10.50.0.100` (test client) |
| Destination | `8.8.8.8` |
| Description | Block test client ICMP to 8.8.8.8 |

**Evidence:** `screenshots/final/18-pfsense-lan-rule-created.png`

### Rule Behavior

| Test | Outcome | Interpretation |
|---|---|---|
| `ping 8.8.8.8` — rule enabled | 100% packet loss ✅ | ICMP blocked to that destination |
| `ping google.com` — rule enabled | 0% packet loss ✅ | DNS and non-ICMP traffic unaffected |
| `ping 10.50.0.1` — rule enabled | 0% packet loss ✅ | LAN gateway reachable; LAN traffic unaffected |
| `ping 8.8.8.8` — rule disabled | 0% packet loss ✅ | Traffic restored on rule removal |

pfSense enforced the rule as expected: blocking applied to ICMP from one source to one
destination only, while all other traffic continued to pass. Rule order and protocol
specificity work correctly.

**Evidence:** `screenshots/final/17-firewall-rule-test-result.png`

### WAN Posture

Default WAN rules: RFC 1918 block + bogon block + implicit deny-all inbound.
No unsolicited inbound connections can reach the pfSense WAN interface.

**Evidence:** `screenshots/final/19-pfsense-wan-rules-baseline.png`

---

## Cleanup and Rollback

The test block rule was **disabled** after validation — preserved as a reference, not
deleted. The default allow rules remain active.

Snapshot taken before any firewall changes:

```bash
virsh snapshot-revert pfsense-lab fresh-install   # full rollback if needed
```

The test client VM can be removed when no longer needed:

```bash
virsh destroy test-client
virsh undefine test-client --remove-all-storage
```

---

## Scope Boundaries

This validation confirms the isolated virtual lab design only. Not yet implemented:

- No production traffic has been routed through pfSense
- No real WAN interface (USB NIC path deferred)
- No VLAN trunking to physical APs or Deco units
- `eno1`, the home router, and the home network were not modified

This is a controlled virtual lab environment, not a production firewall deployment.
