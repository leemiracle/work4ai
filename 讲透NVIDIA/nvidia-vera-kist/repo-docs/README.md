# Nvidia Vera KIST

nvidia-vera-kist is a daemon that orchestrates CPU IST (In-System Test). It
manages the full IST lifecycle — verifying test vector collateral, running
signature checks, coordinating host power-cycle sequences, launching the
`kist_itm` test runner, and archiving results. It also handles test vector
firmware updates by accepting PLDM-wrapped images and managing mount/activation
state.

The daemon runs as a systemd service (`com.nvidia.vera.ist.service`) and exposes
its functionality over D-Bus, which is made available to clients through Redfish
via bmcweb.

## Usage

### Building

```bash
meson setup build
ninja -C build
meson test -C build
```

To set the architecture subdirectory for `kist_itm` lookup:

```bash
meson setup build -Dkist_arch_subdir=aarch64
```

### OpenBMC / Yocto Integration

Add the Yocto recipe (`nvidia-vera-kist_git.bb`) to the appropriate meta-layer
and include it in the image:

```bash
IMAGE_INSTALL:append = " nvidia-vera-kist"
```

Board-specific `.bbappend` files should install:

- `/etc/ist/platform_cfg.json` — runtime configuration
- `/usr/share/ist/kist_itm_verify_key.pem` — ECDSA-P384 public key for
  `kist_itm` signature verification
- Hook scripts referenced by `hookPaths` in the platform configuration

### Runtime Configuration

The daemon reads `/etc/ist/platform_cfg.json` at startup:

```json
{
  "hookDirectory": "/usr/share/ist/hooks/",
  "hookPaths": {
    "istBootAssert": "/usr/share/ist/hooks/ist_boot_enable.sh",
    "istBootDeassert": "/usr/share/ist/hooks/ist_boot_disable.sh",
    "resetSystem": "/usr/share/ist/hooks/ist_sys_rst.sh",
    "errorCheck": "/usr/share/ist/hooks/ist_check_error.sh"
  },
  "storageConfig": {
    "vectorMountPath": "/var/emmc/ist/IST_Test_Package/",
    "vectorStoragePath": "/var/emmc/ist/",
    "resultStoragePath": "/var/emmc/ist/results/"
  },
  "softwareInventoryId": "IST_Vectors"
}
```
