# KVM / libvirt Setup

**Status:** ⚠️ BLOCKED — VT-x disabled in BIOS. All prerequisites verified; one BIOS change required.

---

## Current State

```
$ grep -o 'vmx\|svm' /proc/cpuinfo
(no output)

$ ls -la /dev/kvm
ls: cannot access '/dev/kvm': No such file or directory

$ dmesg | grep vmx
[    0.081709] x86/cpu: VMX (outside TXT) disabled by BIOS
```

The i5-3470 **supports** Intel VT-x. The kernel modules are installed. The only blocker is a BIOS setting.

---

## Step 1 — Enable VT-x in BIOS (Physical Access Required)

> This step cannot be done remotely. You must have physical or IPMI access to the server.

**What to do:**
1. Power cycle `esther`
2. Press `DEL`, `F2`, or `F10` at the boot screen (depends on your motherboard — check the POST screen)
3. Navigate to: **Advanced → CPU Configuration** (or similar — varies by BIOS vendor)
4. Find **Intel Virtualization Technology** or **Intel VT-x**
5. Set to **Enabled**
6. Save and reboot (`F10` typically)

**Verify it worked:**
```bash
grep -o 'vmx' /proc/cpuinfo | head -1
# Expected output: vmx

ls -la /dev/kvm
# Expected: crw-rw---- 1 root kvm ... /dev/kvm
```

---

## Step 2 — Install KVM and libvirt

Run after BIOS fix is confirmed:

```bash
# Install KVM, QEMU, libvirt, and management tools
sudo apt-get install -y \
  qemu-kvm \
  libvirt-daemon-system \
  libvirt-clients \
  bridge-utils \
  virtinst \
  virt-manager

# Add your user to the libvirt and kvm groups
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER

# Start and enable libvirtd
sudo systemctl enable --now libvirtd
```

**Verify:**
```bash
sudo systemctl status libvirtd
virsh list --all          # Should show empty list (no VMs yet)
kvm-ok                    # Should show "KVM acceleration can be used"
```

---

## Step 3 — Verify KVM Acceleration

```bash
sudo kvm-ok
# Expected:
# INFO: /dev/kvm exists
# KVM acceleration can be used

virt-host-validate
# Check all lines pass
```

---

## Step 4 — Optional: Enable Nested Virtualization

Nested virt allows VMs inside VMs (useful for lab scenarios, not required for pfSense):

```bash
# Check current state
cat /sys/module/kvm_intel/parameters/nested
# Y = enabled, N = disabled

# Enable persistently
echo 'options kvm_intel nested=1' | sudo tee /etc/modprobe.d/kvm-nested.conf
sudo modprobe -r kvm_intel && sudo modprobe kvm_intel
```

---

## Hardware Assessment

| Requirement | Your Hardware | Status |
|---|---|---|
| CPU VT-x/AMD-V | i5-3470 supports VT-x | ⚠️ Disabled in BIOS |
| RAM (host + VMs) | 7.6 GB | ⚠️ Tight — pfSense needs ~512 MB; leaves ~7 GB for host + containers |
| Storage for VMs | 362 GB unallocated LVM | ✅ Can provision LV for VM images |
| IOMMU / VT-d | i5-3470 + motherboard dependent | ❓ Check BIOS for VT-d option |

**RAM planning:**
```
Host OS + Docker:          ~1.5 GB
Jellyfin (idle):           ~300 MB  
pfSense VM:                ~512 MB
─────────────────────────────────
Estimated total:           ~2.3 GB used
Available headroom:        ~5.3 GB
```

---

## Installed Kernel Modules (ready to load after BIOS fix)

```
/lib/modules/6.8.0-117-generic/kernel/arch/x86/kvm/kvm.ko.zst
/lib/modules/6.8.0-117-generic/kernel/arch/x86/kvm/kvm-intel.ko.zst
/lib/modules/6.8.0-117-generic/kernel/drivers/gpu/drm/i915/kvmgt.ko.zst
```

These are pre-installed by Ubuntu. No additional downloads required once VT-x is enabled.

---

## Common Beginner Mistakes

1. **Skipping the BIOS step and wondering why `kvm-ok` fails** — the module is installed but cannot load without hardware support enabled.
2. **Not adding your user to the `libvirt` group** — commands will work with sudo but fail without it; VMs won't appear in virt-manager.
3. **Forgetting to log out/in after `usermod -aG`** — group membership doesn't take effect until a new session.
4. **Not checking VT-d (IOMMU) separately** — VT-x enables CPU virtualization; VT-d enables PCIe passthrough. Different BIOS options.

---

## Screenshot Evidence

| Screenshot | Filename | Value |
|---|---|---|
| `kvm-ok` output showing KVM acceleration available | `screenshots/03-kvm-ok-verified.png` | Proves hypervisor setup |
| `virsh list --all` showing running pfSense VM | `screenshots/07-pfsense-vm-running.png` | Demonstrates KVM VM management |
| `virt-host-validate` all passing | `screenshots/04-virt-host-validate.png` | Shows production-ready hypervisor config |
