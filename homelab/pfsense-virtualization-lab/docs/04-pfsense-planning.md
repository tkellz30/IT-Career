# pfSense Virtualization Planning

**Status:** ✅ Complete — virtual firewall baseline validated 2026-06-04  
**Validation:** [docs/10-pfsense-lab-validation.md](10-pfsense-lab-validation.md)  
**Prerequisite:** [docs/03-kvm-libvirt-setup.md](03-kvm-libvirt-setup.md)

---

## Goals

1. Run pfSense as a KVM virtual machine on `esther`
2. Use pfSense as the primary firewall/router for a lab network segment
3. Practice real-world firewall administration (rules, VLANs, IDS/IPS with Suricata/Snort)
4. Create an isolated lab network for security testing without affecting the production LAN

---

## Planned Network Topology

```
Internet → Home Router (192.168.x.1)
                │
                │ LAN (192.168.0.0/24)
                ��
         ┌──────▼──────────────────────────────────────────┐
         │              esther (KVM host)                  │
         │              192.168.x.x                       │
         │                                                  │
         │  ┌────────────────────────────────────────────┐  │
         │  │          pfSense VM                        │  │
         │  │                                            │  │
         │  │  WAN interface: bridge to eno1 (or USB NIC)│  │
         │  │  LAN interface: virtual bridge (virbr1)    │  │
         │  │  192.168.10.0/24 (lab segment)             │  │
         │  └────────────────────────────────────────────┘  │
         │                     │                            │
         │            virbr1 (virtual bridge)               │
         │                     │                            │
         │  ┌────���─────────────┼──────────────────────┐     │
         │  │    Lab VMs / containers                  │     │
         │  │    192.168.10.x  (isolated segment)     │     │
         │  └───���──────────────────────────────────────┘     │
         └─────────────────────────────────────────────────┘
```

**Key design decision:** The USB Ethernet adapter (`enx5c857e3c904d`, currently DOWN) is an excellent candidate for pfSense's WAN interface. This avoids bridging the production `eno1` interface and eliminates the risk of losing LAN access during pfSense VM configuration.

---

## pfSense VM Specifications

| Resource | Planned Allocation | Rationale |
|---|---|---|
| vCPUs | 1 (expandable to 2) | pfSense is lightweight |
| RAM | 512 MB minimum, 1 GB recommended | Suricata IDS needs more if enabled |
| Disk | 20 GB qcow2 on NVMe (`/mnt/fast-storage/vms/`) | pfSense install is ~1 GB; 20 GB for logs/packages |
| Network | 2 virtual NICs (WAN + LAN) | Standard pfSense two-interface setup |

**Storage:** NVMe libvirt pool at `/mnt/fast-storage/vms/` — pool `nvme-vms` already defined, running, and autostarted.
*(LVM LV option deferred — see Phase 3 notes in [03-kvm-libvirt-setup.md](03-kvm-libvirt-setup.md))*

---

## pfSense / Netgate Installer ✅

**Downloaded and verified (Phase 4 — 2026-06-02):**

| Field | Value |
|---|---|
| File | `netgate-installer-v1.2-RELEASE-amd64.iso.gz` |
| Location | `/mnt/fast-storage/isos/` (libvirt pool: `nvme-isos`) |
| Size | 327 MB |
| SHA256 | `184514fe7df0d339362c1e33fa051c464577a450528759b343ade894c7c57955` |
| Verified | On Windows before transfer and on `esther` after transfer — both match ✅ |

---

## Installation Plan

```bash
# Create disk image for pfSense VM (NVMe pool)
sudo qemu-img create -f qcow2 /mnt/fast-storage/vms/pfsense.qcow2 20G

# Create VM with virt-install (Virtual NAT design — see Phase 5 Chosen Design below)
# NOTE: decompress the .iso.gz before use, or verify virt-install supports .gz directly
sudo virt-install \
  --name pfsense \
  --ram 1024 \
  --vcpus 1 \
  --disk path=/mnt/fast-storage/vms/pfsense.qcow2,format=qcow2 \
  --os-variant freebsd13.0 \
  --cdrom /mnt/fast-storage/isos/netgate-installer-v1.2-RELEASE-amd64.iso.gz \
  --network network=default,model=virtio \
  --network network=pfsense-lab-lan,model=virtio \
  --graphics vnc,listen=127.0.0.1 \
  --noautoconsole

# Connect to console via VNC through SSH tunnel
ssh -L 5900:localhost:5900 <username>@100.x.x.x
# Then open VNC client pointing to localhost:5900
```

---

## Network Interface Assignment Strategy

**Option A (Recommended for safety): Virtual WAN**
- pfSense WAN = NAT through `virbr0` (libvirt's default NAT network)
- pfSense LAN = dedicated virtual bridge `virbr1`
- Pro: No changes to `eno1` — production network untouched
- Con: Double-NAT (router → pfSense → lab), acceptable for lab purposes

**Option B (Realistic topology): USB NIC as WAN**
- pfSense WAN = `enx5c857e3c904d` (USB NIC, currently unused)
- pfSense LAN = virtual bridge `virbr1`
- Pro: Real single-NAT topology, pfSense gets real LAN IP
- Con: If USB NIC disconnects, pfSense WAN drops; must not bridge `eno1`

**Recommendation:** Start with Option A for initial setup, migrate to Option B once comfortable.

---

## Phase 5 — Chosen Network Design (2026-06-02)

**Decision: Option A — Virtual NAT.** No physical NIC changes, no Linux bridge, no Netplan changes.

### Network Topology

```
Home Router (192.168.0.1)
        │
        │ LAN (192.168.0.0/24)
        │
   esther (eno1: 192.168.0.24)
        │
   libvirt default NAT (virbr0, 192.168.122.0/24)
        │
   ┌────▼────────────────────────────────┐
   │         pfSense VM                  │
   │  WAN: default (192.168.122.x)       │  ← double-NAT, internet via host
   │  LAN: pfsense-lab-lan (10.50.0.x)  │  ← isolated, no production traffic
   └────────────────────────────────────┘
        │
   pfsense-lab-lan (virbr-pflan, 10.50.0.0/24)
        │
   [future test VMs / controlled access]
```

### Libvirt Networks

| Role | Network Name | Bridge | Type | Subnet | Status |
|---|---|---|---|---|---|
| pfSense WAN | `default` | `virbr0` | NAT | 192.168.122.0/24 | Active ✅ — persistent, autostart yes |
| pfSense LAN | `pfsense-lab-lan` | `virbr-pflan` | Isolated | 10.50.0.0/24 | Active ✅ — persistent, autostart yes, no host IP |

**Verified (2026-06-02):** Both networks active. `eno1` remains 192.168.0.24/24. Default route via 192.168.0.1 unchanged. No 10.50.0.0/24 route on host (correct — pfSense owns that subnet). Tailscale present and unaffected.

### What This Design Can Test

- pfSense installation and boot via VNC-over-SSH tunnel
- pfSense WAN connectivity via double-NAT (internet access works for packages/updates)
- pfSense LAN DHCP server and firewall rules on the isolated 10.50.0.0/24 segment
- pfSense web GUI access from `esther` host over the lab LAN bridge
- Firewall rule design and NAT configuration in a safe, isolated environment

### What This Design Cannot Test Yet

- Replacing the home router (Deco units untouched)
- Real single-NAT WAN topology (requires USB NIC or bridged `eno1` — deferred)
- VLAN trunking to physical APs
- Production client routing through pfSense
- Real WAN failover

### Read-Only Inspection Commands (run before creating anything)

```bash
virsh net-list --all          # confirm 'default' network exists and is active
virsh net-info default        # verify subnet and bridge interface (virbr0)
ip addr show                  # confirm eno1, tailscale0, virbr0 state on host
ip route                      # confirm current routing table — baseline before any changes
```

### Proposed Commands — Isolated LAN Network (pending approval — not yet run)

```bash
# Define the isolated pfSense LAN network via XML
cat > /tmp/pfsense-lab-lan.xml << 'EOF'
<network>
  <name>pfsense-lab-lan</name>
  <bridge name='virbr-pflan' stp='on' delay='0'/>
</network>
EOF
# Isolated: no <forward> element = no routing to host network
# No host DHCP: pfSense owns DHCP on this segment

virsh net-define /tmp/pfsense-lab-lan.xml
virsh net-start pfsense-lab-lan
virsh net-autostart pfsense-lab-lan
virsh net-info pfsense-lab-lan   # confirm active, persistent, autostart yes
```

> **Do not run until `virsh net-list --all` and `virsh net-info default` output is confirmed.**

---

## Safety Rules for pfSense Phase

- **DO NOT** bridge `eno1` to pfSense WAN — this would route LAN traffic through pfSense and can cause outage
- **ALWAYS** have Tailscale as a fallback — it uses `tailscale0` independently of routing changes
- **ALWAYS** keep a physical/HDMI session or IPMI available before making routing changes
- **SNAPSHOT** the pfSense VM before any major firewall rule changes: `virsh snapshot-create-as pfsense snap-name`
- **TEST** connectivity after each rule change before saving permanently

---

## Learning Objectives (Resume Value)

After completing this phase:

```
• Deployed pfSense firewall as a KVM virtual machine on Ubuntu 24.04 LTS using libvirt/QEMU,
  configuring dual virtual NICs for WAN/LAN network segmentation

• Implemented firewall rule policies, NAT configuration, and DHCP server in pfSense for
  an isolated lab network segment (192.168.10.0/24)

• Configured Suricata IDS/IPS on pfSense with ET (Emerging Threats) ruleset for
  network intrusion detection in a controlled lab environment
```
