# pfSense Virtualization Readiness Checklist

Complete these items **in order**. Do not proceed past a blocked item.

---

## Phase 0 — Security Baseline (Prerequisites)

- [x] UFW enabled with deny-by-default policy
- [x] Tailscale VPN confirmed as working backup access path
- [x] Unattended-upgrades active and verified
- [x] 0 pending security updates
- [x] Samba `map to guest = Never` (tighten before exposing new network segments)
- [x] SSH key authentication deployed (before exposing pfSense admin interface)
- [ ] LVM extended to recover 362 GB (optional but recommended before VM storage setup)

---

## Phase 1 — BIOS / Hardware (Physical Access Required)

- [x] **Enable Intel VT-x in BIOS** *(completed 2026-06-02)*
  - Boot to BIOS setup (DEL or F2 on POST screen)
  - Navigate: Advanced → CPU Configuration → Intel Virtualization Technology
  - Set: **Enabled**
  - Save and reboot
  
- [x] Verify VT-x active: *(confirmed 2026-06-02)*
  ```bash
  grep -o 'vmx' /proc/cpuinfo | head -1
  # Expected: vmx
  ```

- [x] Verify `/dev/kvm` exists: *(confirmed 2026-06-02)*
  ```bash
  ls -la /dev/kvm
  # Expected: crw-rw---- 1 root kvm ...
  ```

- [ ] (Optional) Enable VT-d (IOMMU) in BIOS for PCIe passthrough capability
  - Check BIOS for "VT-d", "Intel VT-d", or "IOMMU"
  - Not required for basic pfSense VM, useful for advanced passthrough later

---

## Phase 2 — KVM / libvirt Installation

- [x] Install KVM and libvirt packages: *(completed 2026-06-02)*
  ```bash
  sudo apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients \
    bridge-utils virtinst
  ```

- [x] Add user to groups: *(completed 2026-06-02)*
  ```bash
  sudo usermod -aG libvirt $USER
  sudo usermod -aG kvm $USER
  # Log out and back in after this
  ```

- [x] Start and enable libvirtd: *(active/running confirmed 2026-06-02)*
  ```bash
  sudo systemctl enable --now libvirtd
  sudo systemctl status libvirtd
  # Expected: active (running)
  ```

- [x] Run `kvm-ok`: *(confirmed — see screenshot 11)*
  ```bash
  sudo kvm-ok
  # Expected: INFO: /dev/kvm exists — KVM acceleration can be used
  ```

- [x] Run `virt-host-validate`: *(2026-06-02 — QEMU/KVM lines PASS; two non-blocking warnings)*
  ```bash
  sudo virt-host-validate
  # All entries should PASS
  ```
  > ⚠️ **Secure guest support:** WARN — not required for standard QEMU/KVM VM operation.  
  > ⚠️ **LXC freezer controller:** FAIL — LXC-specific; no impact on QEMU/KVM pfSense VM path.

- [x] Verify virsh works: *(confirmed 2026-06-02 — empty table, no VMs)*
  ```bash
  virsh list --all
  # Expected: empty table (no VMs yet)
  ```

**Screenshot checkpoint:** `screenshots/final/11-kvm-ok-verification.png` — `kvm-ok` output ✅  
**Screenshot checkpoint:** `screenshots/final/12-libvirt-install-verified.png` — libvirtd status, virsh, groups ✅

---

## Phase 3 — VM Storage Preparation

- [ ] Decide storage location for VM disk images (options):
  - **Option A:** Provision new LVM LV from the 362 GB unallocated space
    ```bash
    sudo lvcreate -L 50G -n vm-images ubuntu-vg-1
    sudo mkfs.ext4 /dev/ubuntu-vg-1/vm-images
    sudo mkdir -p /var/lib/libvirt/vms
    # Add to /etc/fstab for persistence
    ```
  - **Option B:** Use NVMe directly (`/mnt/fast-storage/vms/`)
    - Faster disk I/O; good for VM storage
    - Less separation from media data

- [ ] Create ISO storage directory:
  ```bash
  sudo mkdir -p /var/lib/libvirt/iso
  ```

- [ ] Verify available space:
  ```bash
  df -h
  ```

---

## Phase 4 — pfSense Download and Verification

- [ ] Download pfSense CE AMD64 ISO from pfsense.org
- [ ] Verify SHA256 checksum against published hash
- [ ] Copy ISO to server:
  ```bash
  scp pfSense-CE-*.iso <username>@100.x.x.x:/var/lib/libvirt/iso/
  ```

---

## Phase 5 — Network Planning (Before Creating VM)

- [ ] Decide network topology (see [docs/04-pfsense-planning.md](../docs/04-pfsense-planning.md))
  - [ ] Option A: Virtual NAT (safe, double-NAT) — recommended for first attempt
  - [ ] Option B: USB NIC as WAN interface

- [ ] If using USB NIC (Option B):
  - [ ] Confirm `enx5c857e3c904d` is detected: `ip link show enx5c857e3c904d`
  - [ ] **DO NOT** modify `eno1` in this phase
  - [ ] Confirm UFW rule exists for Tailscale before any routing changes
  - [ ] Document the USB NIC MAC address for reference

- [ ] Create libvirt virtual network for pfSense LAN:
  ```bash
  # Create isolated bridge network (lab segment)
  virsh net-define /etc/libvirt/qemu/networks/labnet.xml
  virsh net-start labnet
  virsh net-autostart labnet
  ```

---

## Phase 6 — pfSense VM Creation

- [ ] Create VM disk image:
  ```bash
  sudo qemu-img create -f qcow2 /var/lib/libvirt/vms/pfsense.qcow2 20G
  ```

- [ ] Install pfSense via virt-install (see [docs/04-pfsense-planning.md](../docs/04-pfsense-planning.md))

- [ ] Complete pfSense initial setup wizard via VNC-over-SSH tunnel

- [ ] Verify pfSense web interface accessible from Tailscale or LAN

- [ ] **Take VM snapshot before any firewall rule changes:**
  ```bash
  virsh snapshot-create-as pfsense "fresh-install" --description "Clean pfSense install"
  ```

**Screenshot checkpoint:** `screenshots/final/13-pfsense-dashboard.png` — pfSense dashboard  
**Screenshot checkpoint:** `screenshots/final/14-pfsense-firewall-rules.png` — firewall rules  
**Screenshot checkpoint:** `screenshots/final/15-virsh-vm-running.png` — `virsh list` output

---

## Go/No-Go Gates

| Gate | Condition | Pass Criteria |
|---|---|---|
| BIOS Gate | Before Phase 2 | `vmx` appears in `/proc/cpuinfo` |
| KVM Gate | Before Phase 4 | `kvm-ok` returns green, `/dev/kvm` exists |
| Network Gate | Before Phase 6 | Virtual network created, confirmed no impact to `eno1` |
| Snapshot Gate | Before firewall rules | VM snapshot created and verified restorable |

---

## Emergency Rollback Reference

If you lose access to `esther` at any phase:

1. **Tailscale still works?** → Connect via `ssh <username>@100.x.x.x`
2. **Tailscale down?** → LAN SSH: `ssh <username>@192.168.x.x`
3. **SSH locked?** → UFW emergency disable (requires physical): `sudo ufw disable`
4. **Network routing broken by pfSense?** → `virsh destroy pfsense` (stops VM, restores routing)
5. **Complete recovery:** → See [rollback/networking-rollback-procedures.md](../rollback/networking-rollback-procedures.md)
