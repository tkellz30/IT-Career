# pfSense Virtualization Planning

**Status:** 🔲 Planned — awaiting KVM setup  
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
| Disk | 20 GB (thin-provisioned from LVM) | pfSense install is ~1 GB; 20 GB for logs/packages |
| Network | 2 virtual NICs (WAN + LAN) | Standard pfSense two-interface setup |

**Storage:** Create a new LVM logical volume for VM images:
```bash
sudo lvcreate -L 100G -n vm-storage ubuntu-vg-1
sudo mkfs.ext4 /dev/ubuntu-vg-1/vm-storage
sudo mkdir /var/lib/libvirt/vms
sudo mount /dev/ubuntu-vg-1/vm-storage /var/lib/libvirt/vms
```

---

## pfSense Download

- Download AMD64 ISO from: https://www.pfsense.org/download/
- Version: pfSense CE (Community Edition) or pfSense Plus (if licensed)
- Architecture: AMD64
- Console: VGA
- Installer: DVD Image (ISO)

Verify SHA256 checksum after download.

---

## Installation Plan

```bash
# Create disk image for pfSense VM
sudo qemu-img create -f qcow2 /var/lib/libvirt/vms/pfsense.qcow2 20G

# Create VM with virt-install
sudo virt-install \
  --name pfsense \
  --ram 1024 \
  --vcpus 1 \
  --disk path=/var/lib/libvirt/vms/pfsense.qcow2,format=qcow2 \
  --os-variant freebsd13.0 \
  --cdrom /var/lib/libvirt/iso/pfSense-CE-2.7.x-amd64.iso \
  --network bridge=virbr0,model=virtio \
  --network network=default,model=virtio \
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
