# lstp_config_tool

Userspace LSTP configuration tool: **READ_CONFIG** / **WRITE_CONFIG** over
**libusb**, with **YAML** read and write via libyaml. See [LSTP Specification 1.0.pdf](LSTP%20Specification%201.0.pdf) for more details on LSTP.

The tool only touches sysfs to temporarily unbind the normal `lstp` driver so libusb can claim the
interface, then restores `lstp` on exit if it was bound at start.

Licensed under the Apache License 2.0 — see [LICENSE](LICENSE).

## Build

`make` produces up to **two** deployable outputs when the required compilers are
installed; missing cross-compilers are skipped (not an error).

| Binary | Architecture | Typical target |
|--------|--------------|----------------|
| `build/lstp_config_tool_x86` | x86_64 | Intel/AMD laptop, dev VM |
| `build/lstp_config_tool_ARM` | armhf (ARMv7 hard-float) | OpenBMC AST2600 / ARM BMCs |

The ARM binary is built for **armv7-a** (AST2600). On 64-bit ARM hosts (e.g. RPi
3+, some OpenBMC images), it runs via kernel 32-bit compat when enabled.

Install cross-compilers once, then build from **x86_64**, **aarch64**, or
**armv7l**:

```sh
sudo apt install gcc-arm-linux-gnueabihf gcc-x86-64-linux-gnu
make clean-all
make
file build/lstp_config_tool_x86 build/lstp_config_tool_ARM
ldd build/lstp_config_tool_ARM    # not a dynamic executable
```

On **x86_64**, native `gcc` builds `build/lstp_config_tool_x86`; armhf is
cross-compiled when `gcc-arm-linux-gnueabihf` is installed.

On **aarch64**, armhf and x86 are cross-compiled when their packages are
installed.

On **armv7l** (32-bit ARM), native `gcc` builds `build/lstp_config_tool_ARM`; x86 is
cross-compiled when `gcc-x86-64-linux-gnu` is installed.

```sh
make        # x86 + arm when compilers are installed
make x86    # x86_64 only
make arm    # build/lstp_config_tool_ARM only
```

## Run

`--usb-path` and either `--read` or `--write` are required (sysfs interface id).
Root (sudo) is required for driver unbind and USB access.

### Read

Read all channels from the device and write YAML:

```sh
sudo ./build/lstp_config_tool_ARM -u 1-1.1:1.2 -r
```

If `FILE` is omitted, the output filename is derived from the
management channel name before the first `_`:

```sh
sudo ./build/lstp_config_tool_ARM -u 1-1.1:1.2 -r out.yaml
```

Read path:

1. READ_CONFIG on channel 0 (management), then channels `1..num_channels`
2. READ_CONFIG_MODE on channel 0 (included in YAML as `lock_state`)
3. Write YAML (`schema_version: 1`)

### Write

Load a YAML file and WRITE_CONFIG to the device. When `lock_state` is `nonvolatile` or
`locked`, the tool prompts for confirmation before touching the device (skipped with `-y`).
Non-volatile writes may consume OTP space on devices without flash firmware; locked mode
permanently fuses the config and cannot be undone.

```sh
sudo ./build/lstp_config_tool_ARM -u 1-1.1:1.2 -w write.yaml
```


`-r` / `--read` and `-w` / `--write` are mutually exclusive.

### Options

| Option | Description |
|--------|-------------|
| `-u`, `--usb-path PATH` | Required sysfs interface id (e.g. `1-1.1:1.2`) |
| `-r`, `--read [FILE]` | Read config from device and write YAML (default FILE: `<name before '_'>.yaml`) |
| `-w`, `--write FILE` | Load YAML and WRITE_CONFIG to device |
| `-y`, `--yes` | With `--write`: skip confirmation for `lock_state` nonvolatile or locked |
| `-d`, `--debug` | Verbose USB/protocol logging |
| `-h`, `--help` | Usage |

## YAML

- Root: `schema_version: 1`, `channels:` map keyed by channel id
- Channel 0: `type: management`, `lock_state: nonvolatile\|locked\|volatile`, plus `config.lstp_version` and `config.num_channels`
- Data channels: type-specific `config` (GPIO, I2C, UART, SPI, etc.)
- READ_CONFIG output is normalized to the current schema. Newer firmware may return bytes beyond the current known config layout; the tool drops those bytes, prints a warning, and does not preserve them in YAML. Any other unexpected read size fails the read.
- WRITE_CONFIG sends only fields this tool understands. Valid current YAML may still fail on a target board if the config state is locked/fused or firmware rejects an unsupported option, nonexistent offset, or size policy.
- **Write validation** is strict: every schema field must be present with a valid value; channel count must match `num_channels`
- Optional YAML document markers (`---` at the top, `...` at the end) are ignored by the parser; only `schema_version` and `channels` content matter. Files under `sample_config/` may include them for readability.

### Write-time value checks (selected)

| Channel | Field | Allowed values |
|---------|-------|----------------|
| SPI | `num_devices` | 1–2 |
| SPI | `clock_speed_hz` | non-zero |
| SPI | `output_drive_strength_ma`, `slew_rate`, `input_debounce_us`, `glitch_filter_width_ns` | 0–65535 |
| I2C | `speed` | `100k`, `400k`, `1m`, or `3p4m` |
| I2C | `output_drive_strength_ma`, `slew_rate`, `input_debounce_us`, `glitch_filter_width_ns` | 0–65535 |
| I2C | `bus_low_timeout_ms`, `bus_arbitration_retries` | 0–255 |
| UART | `baud_rate` | non-zero |
| UART | `data_bits` | 5–8 |
| UART | `stop_bits` | 1 or 2 |
| UART | `parity` | `none`, `odd`, `even`, `mark`, or `space` |
| UART | `flow_control` | `none`, `xon_xoff`, `rts_cts`, or `dtr_dsr` |
| UART | `output_drive_strength_ma`, `slew_rate`, `input_debounce_us`, `glitch_filter_width_ns` | 0–65535 |
| GPIO | `ngpio` | 1–255 per block |
| GPIO pin | `name` | non-empty |
| GPIO pin | `default_output` | `low`, `high`, or `z` |
| GPIO pin | numeric fields | within wire limits (uint16 where applicable) |

Invalid wire blobs are also rejected immediately before WRITE_CONFIG.

Example files in the repo:

| File | Description |
|------|-------------|
| `sample_config/lstp_config.yaml` | YAML schema stub (top-level shape) |
| `sample_config/sample_config_schema.yaml` | Per-channel config field reference (all types) |
| `sample_config/sample_all_channels.yaml` | Reference: management + SPI + GPIO + I2C + UART + IPMI + MMIO |
| `sample_config/sample_0_channels.yaml` | No I/O channels (management only) |
| `sample_config/sample_gpio14.yaml` | Default: 1 GPIO channel (14 pins) |
| `sample_config/sample_gpio12_uart.yaml` | 1 GPIO channel (12 pins) + 1 UART channel |
| `sample_config/sample_gpio12_i2c.yaml` | 1 GPIO channel (12 pins) + 1 I2C channel |
| `sample_config/sample_gpio10_uart_i2c.yaml` | 1 GPIO channel (10 pins) + 1 UART + 1 I2C |
