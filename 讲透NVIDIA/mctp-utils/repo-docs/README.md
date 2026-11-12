## Table of Contents

- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Linux udev rules](#linux-udev-rules-for-usb-devices)
- [Usage](#usage)
  - [Run via uv](#run-via-uv)
  - [Direct file invocation](#direct-file-invocation)
  - [Subcommands](#subcommands)
  - [Fuse validation](#fuse-validation)
- [Debug](#debug)
  - [`ModuleNotFoundError` when running directly](#modulenotfounderror-when-running-directly)
  - [`cffi` build fails during `uv sync`](#cffi-build-fails-during-uv-sync)

## Setup

### Prerequisites

- Require Python ≥ 3.10
- Require uv
    ```bash
    $ curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
- Install Python dependencies at the root of `mctp-utils`:
    ```bash
    $ uv sync 
    ```
    💡 **Notes:**
    - If you encounter `pyproject.toml not found error`, check your working directory — run `uv sync` at the root of `mctp-utils`.
    - `uv sync` creates `.venv/` and installs every dependency exactly as pinned in `uv.lock`.
- Install libusb (Linux: preinstalled on most distros; install only if missing):
    ```bash
    $ sudo apt-get update && sudo apt-get install -y libusb-1.0-0
    ```

### Linux udev rules (for USB devices)

Required for non-root access to MCU devices over USB:
```bash
echo 'SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="0955", MODE="0666"' | sudo tee /etc/udev/rules.d/99-nv-mcu.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Usage

### Option1: Run via uv (Recommended)

```bash
uv run python -m mctp_utils                                      # list subcommands
uv run python -m mctp_utils mctp_cmd_utils --help
```

### Option2: Direct file invocation

```bash
uv run python mctp_utils/mctp_cmd_utils.py --help
```

Useful for debugging a single utility in isolation.

### Subcommands

| Subcommand | Purpose |
|---|---|
| `mctp_cmd_utils` | MCTP raw commands, EID management, routing |
| `mctp_nsm_utils` | NVIDIA Server Management MCTP utility |
| `mctp_pldm_utils` | PLDM transport over MCTP |
| `mctp_spdm_utils` | SPDM (certificates, measurements) over MCTP |
| `mctp_vdm_utils` | Vendor Defined Messages over MCTP |
| `mfghelper` | Manufacturing helper |

### Fuse validation

Use `etc/fuses_mcxn556_pqc_no_rotkh.json` as a sanitized reference for the fuse
JSON format. The file keeps the measured MCXN556 fuse order, but addresses `11`
through `22` contain zero ROTKH placeholders. Replace those words with the
project/keyset ROTKH values from the matching provisioning package before using
the file to validate a real device.

To calculate the expected fuse measurement from a JSON file:

```bash
uv run python -m mctp_utils mfghelper measure_fuse \
  --fuse_cfg etc/fuses_mcxn556_pqc_no_rotkh.json
```

To verify a device over USB/MCTP:

```bash
uv run python -m mctp_utils mfghelper \
  --bus_num <usb_bus> \
  --dev_num <usb_device> \
  --tcp_port 5000 \
  --context spdm_context_status.json \
  verify_fuse \
  --fuse_cfg <project_fuses.json>
```

Mechanism: `mfghelper` reads the top-level `fuses` array in order, applies the
helper fuse mask, serializes each 32-bit value as little-endian bytes, and
computes a SHA384 digest. `verify_fuse` reads SPDM measurement index `13` from
the device and compares that device digest with the expected digest from the
JSON; firmware patch `215` and newer use the masked calculation.

## Debug

### `ModuleNotFoundError` when running directly

Use `uv run python ...` rather than bare `python ...` — `uv run` activates the venv so the package can find its dependencies. Applies to both `-m mctp_utils` invocation and direct file invocation.

### `cffi` build fails during `uv sync`

On Ubuntu/Debian: `sudo apt install libffi-dev`. On Fedora: `sudo dnf install libffi-devel`. Re-run `uv sync`.
