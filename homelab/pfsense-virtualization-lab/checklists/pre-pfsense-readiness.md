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

- [x] Decide storage location for VM disk images: *(decided 2026-06-02)*
  - **✅ Chosen — Option B:** NVMe direct mount at `/mnt/fast-storage/vms/`
    - Faster disk I/O; 842 GB free; already mounted and persistent via `/etc/fstab`
    - No repartitioning or LVM changes required
  - **⏸ Deferred — Option A:** LVM LV from 362 GB unallocated space on SATA HDD
    - Deferred: adds complexity; LVM extension can recover that space independently later
    - Not needed for initial pfSense VM deployment

- [x] Create VM and ISO storage directories on NVMe: *(completed 2026-06-02)*
  ```bash
  sudo mkdir -p /mnt/fast-storage/vms
  sudo mkdir -p /mnt/fast-storage/isos
  ```

- [x] Set ownership and permissions for libvirt/QEMU access: *(confirmed 2026-06-02)*
  ```bash
  sudo chown libvirt-qemu:kvm /mnt/fast-storage/vms /mnt/fast-storage/isos
  sudo chmod 0751 /mnt/fast-storage/vms /mnt/fast-storage/isos
  ```
  > libvirt-qemu: `uid=64055(libvirt-qemu) gid=994(kvm) groups=994(kvm)`  
  > Result: `drwxr-x--x 2 libvirt-qemu kvm` on both directories

- [x] Verify directories and available space: *(confirmed 2026-06-02)*
  ```bash
  ls -lah /mnt/fast-storage/ | grep -E 'vms|isos'
  df -h /mnt/fast-storage
  ```
  > `/dev/nvme0n1p1` — 916G total, 28G used, **842G available**

- [x] Define libvirt storage pools for VM images and ISOs: *(completed 2026-06-02)*
  ```bash
  virsh pool-define-as nvme-vms  dir --target /mnt/fast-storage/vms
  virsh pool-define-as nvme-isos dir --target /mnt/fast-storage/isos
  # then for each: pool-build, pool-start, pool-autostart, pool-info
  ```
  > `nvme-vms`  — State: running, Persistent: yes, Autostart: yes, Available: 888.45 GiB  
  > `nvme-isos` — State: running, Persistent: yes, Autostart: yes, Available: 888.45 GiB  
  > AppArmor paths registered automatically by libvirt. VM creation can proceed.

---

## Phase 4 — pfSense Download and Verification

- [x] Download Netgate installer ISO: *(completed 2026-06-02)*
  > **File:** `netgate-installer-v1.2-RELEASE-amd64.iso.gz` (327 MB)

- [x] Verify SHA256 checksum on Windows before transfer: *(verified 2026-06-02)*
  > **SHA256:** `184514fe7df0d339362c1e33fa051c464577a450528759b343ade894c7c57955`  
  > Matched official published hash ✅

- [x] Transfer ISO to esther at `/mnt/fast-storage/isos/`: *(completed 2026-06-02)*
  ```bash
  scp netgate-installer-v1.2-RELEASE-amd64.iso.gz <username>@100.x.x.x:/mnt/fast-storage/isos/
  ```
  > `-rw-r--r-- 1 libvirt-qemu kvm 327M Jun  2 04:07 netgate-installer-v1.2-RELEASE-amd64.iso.gz`

- [x] Verify SHA256 on esther after transfer: *(verified 2026-06-02)*
  ```bash
  sha256sum /mnt/fast-storage/isos/netgate-installer-v1.2-RELEASE-amd64.iso.gz
  ```
  > `184514fe7df0d339362c1e33fa051c464577a450528759b343ade894c7c57955` — matches ✅

- [x] Confirm ISO visible in libvirt `nvme-isos` pool: *(confirmed 2026-06-02)*
  ```bash
  virsh pool-refresh nvme-isos
  virsh vol-list nvme-isos
  ```
  > `netgate-installer-v1.2-RELEASE-amd64.iso.gz   /mnt/fast-storage/isos/netgate-installer-v1.2-RELEASE-amd64.iso.gz`

---

## Phase 5 — Network Planning (Before Creating VM)

- [x] Decide network topology: *(decided 2026-06-02)*
  - **✅ Chosen — Option A:** Virtual NAT — `default` NAT network as WAN, isolated `pfsense-lab-lan` as LAN
    - `eno1` untouched, Tailscale untouched, no Linux bridge, no Netplan changes
    - Double-NAT acceptable for initial install and lab testing
  - **⏸ Deferred — Option B:** USB NIC (`enx5c857e3c904d`) as WAN
    - Deferred: real single-NAT topology; migrate after pfSense install is stable

- [x] Run read-only network inspection: *(confirmed 2026-06-02)*
  > `default` network active, persistent, autostart yes — bridge `virbr0` (192.168.122.1/24)  
  > `eno1` remains 192.168.0.24/24 — default route via 192.168.0.1 unchanged  
  > Tailscale present and unaffected — baseline clean

- [x] Create isolated libvirt LAN network `pfsense-lab-lan`: *(completed 2026-06-02)*
  > Bridge `virbr-pflan` — active, persistent, autostart yes  
  > No host IPv4 address on `virbr-pflan` (correct — pfSense owns 10.50.0.0/24)  
  > No 10.50.0.0/24 route appears on host routing table (correct)  
  > `eno1` and default route unchanged — production network unaffected
  > pfSense owns DHCP on this segment — no host DHCP configured here.

---

## Phase 6 — pfSense VM Creation

- [x] Create VM disk image: *(completed 2026-06-02)*
  ```bash
  virsh vol-create-as nvme-vms pfsense-lab.qcow2 20G --format qcow2
  ```
  > Path: `/mnt/fast-storage/vms/pfsense-lab.qcow2` — qcow2, thin-provisioned via `nvme-vms` pool

- [x] Install pfSense via virt-install: *(completed 2026-06-02 — see [docs/04-pfsense-planning.md](../docs/04-pfsense-planning.md))*
  > VM: `pfsense-lab` — 2 vCPUs, 2048 MB RAM, persistent yes, autostart disabled  
  > ISO decompressed from `.iso.gz`; installed via VNC-over-SSH tunnel  
  > CD-ROM slot empty post-install (`virsh domblklist` hda: `-`) ✅

- [x] Complete pfSense initial setup wizard via VNC-over-SSH tunnel: *(completed 2026-06-02)*
  > pfSense 2.8.1-RELEASE booted successfully  
  > WAN: `vtnet0` → libvirt `default` NAT → DHCP `192.168.122.x/24` ✅  
  > LAN: `vtnet1` → `pfsense-lab-lan` → `10.50.0.1/24` ✅  
  > Console ping `8.8.8.8` — 0% packet loss ✅  
  > Console ping `google.com` — 0% packet loss, DNS resolves ✅  
  > `eno1`, Tailscale, home router — all unaffected ✅

- [ ] Verify pfSense web GUI accessible: *(pending — LAN is isolated; requires test client VM or host route)*

- [x] **Take VM snapshot before any firewall rule changes:** *(completed 2026-06-02)*
  ```bash
  virsh snapshot-create-as pfsense-lab fresh-install \
    "Fresh pfSense install before firewall/config changes"
  ```
  > Snapshot `fresh-install` created — 2026-06-02 17:59:11 +0000, state: running ✅  
  > Restore: `virsh snapshot-revert pfsense-lab fresh-install`

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
| Snapshot Gate | Before firewall rules | VM snapshot created and verified restorable | ✅ `fresh-install` — 2026-06-02 |

---

## Emergency Rollback Reference

If you lose access to `esther` at any phase:

1. **Tailscale still works?** → Connect via `ssh <username>@100.x.x.x`
2. **Tailscale down?** → LAN SSH: `ssh <username>@192.168.x.x`
3. **SSH locked?** → UFW emergency disable (requires physical): `sudo ufw disable`
4. **Network routing broken by pfSense?** → `virsh destroy pfsense` (stops VM, restores routing)
5. **Complete recovery:** → See [rollback/networking-rollback-procedures.md](../rollback/networking-rollback-procedures.md)
