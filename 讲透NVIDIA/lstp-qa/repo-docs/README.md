# LSTP QA Test Suite

Hardware-level regression tests for the LSTP host-and-device ecosystem. Pytest
exercises SPI, GPIO, IRQ, LED, I2C, UART, and IPMI interfaces that the Linux
driver exposes over USB, validating the host driver and attached LSTP devices
end-to-end against board YAML expectations.

A companion **wire suite** under [`wire/`](wire/) tests the LSTP protocol itself,
speaking to the device directly over USB bulk endpoints with no kernel driver in
the path. It covers what this suite structurally cannot reach — malformed frames,
short headers, bad lengths, reserved opcodes, config bounds — and shares the same
board YAML. See [`wire/README.md`](wire/README.md).

Please refer to the [LSTP Specification](docs/LSTP%20Specification%201.0%20--%2008-03-2026.pdf)
for details on the LSTP protocol. See [`LSTP-Enabled USB Hub`](docs/LSTP-Enabled%20USB%20Hub.pdf)
for the design document of a USB Hub with LSTP protocol support.

## Prerequisites

- **LSTP hardware** with the `lstp` kernel module loaded (`sudo modprobe lstp`).
  SPI tests also need spidev bound to flash CS lines (`auto_bind_spidev=1` on
  `modprobe`, or the suite binds via sysfs during setup).
- **Board config** in `boards/<name>.yaml` (see [Board configuration](#board-configuration)).
- **Python 3** virtual environment with packages from `requirements.txt`.
- **Elevated commands** — many tests run privileged operations through `sudo -n`
  in [`priv.py`](priv.py) (for example `modprobe`, `i2cdetect`, sysfs writes
  via `tee`, and `dmesg -r`). The test user needs a matching sudoers allowlist,
  or run pytest as root for local debugging.

## Quick start

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Full suite (discovery + every configured domain + multichannel when applicable)
.venv/bin/pytest lstp_test.py -v --tb=short --board HELLOWORLD547

# Pin a specific USB interface (optional)
.venv/bin/pytest lstp_test.py -v --tb=short --board HELLOWORLD547 --usb-path 1-1:1.0

# Discovery plus one domain
.venv/bin/pytest lstp_test.py -v --tb=short --board HELLOWORLD547 --suite spi
```

### `--board`

Required. Selects `boards/<stem>.yaml`; matching is case-insensitive
(`boards/helloworld547.yaml` → `--board HELLOWORLD547`).

### `--usb-path` (optional)

Basename under `/sys/bus/usb/devices` (for example `1-1:1.0`). Use when more
than one LSTP interface matches the board `device_name`; otherwise the first
match is used.

### `--suite` (optional)

Omit for a full run (discovery plus every configured domain, and multichannel
when applicable). When set, discovery always runs, then the selected domain:

| `--suite` | Also runs |
|-----------|-----------|
| `spi` | SPI |
| `gpio` | GPIO |
| `irq` | GPIO and IRQ (IRQ loopback depends on GPIO direction checks passing first) |
| `led` | LED |
| `i2c` | I2C |
| `uart` | UART (the whole UART class is omitted when no device has both `console` and `baud` in YAML) |
| `ipmi` | IPMI module only (no test cases implemented yet) |

**Multichannel** is not a `--suite` value. During a full run, `test_multichannel`
runs when `multichannel.scaling_factor` is non-zero and at least two bandwidth
domains are active: `i2c.bandwidth`, GPIO lines tagged `gpio` (not `led`), or
`uart.devices.*.bandwidth`.

## How it fits together

- [`board_config.py`](board_config.py) loads `boards/*.yaml` (shared with wire/).
- [`lstp_test.py`](lstp_test.py) is the pytest entry point: thin `LstpTest*`
  collectors wrapping the `test_*.py` modules.
- [`conftest.py`](conftest.py) defines CLI options, session fixtures
  (`usb_sysfs`, `lstp_channels`, per-domain maps), and `--suite` filtering.
- [`test_*.py`](.) holds the test logic.
- [`device_results.py`](device_results.py) aggregates per-device pass/fail/skip
  into one result line per test; [`deviations.py`](deviations.py) maps board
  YAML `known_deviations` to xfails (shared with the wire suite).

Discovery selects the USB sysfs node where the `lstp` driver is bound and
`<usb>/lstp/name` matches the board YAML `device_name`. SPI master numbers,
gpiochip indices, and I2C bus numbers come from the live `lstp/channel/` walk,
not from hardcoded values in the tests.

## Board configuration

Add `boards/<stem>.yaml` and pass `--board <stem>`. The repo ships
[`boards/helloworld547.yaml`](boards/helloworld547.yaml) as a reference for the
[OpenSMA Helloworld547](https://github.com/NVIDIA/OpenSMA/tree/vr_sma/src/boards/mcxn547helloworld)
board (`--board HELLOWORLD547`).

Each file documents its schema in comments. Common top-level keys:

| Key | Role |
|-----|------|
| `device_name` | Must match `<usb>/lstp/name` |
| `expected_bcd_device` | Golden USB `bcdDevice` for the wire suite (`0` skips) |
| `known_deviations` | Per-target SADD waivers / open findings (see `deviations.py`) |
| `init` | Expected channel names by type (`spi`, `gpio`, `i2c`, `uart`, `ipmi`, `mmio`) |
| `spi` / `gpio` / `i2c` / `uart` / `ipmi` / `multichannel` | Domain expectations |

Use `[]`, `{}`, or `0` for empty sections, as noted in those comments.

## Test coverage

| Module | What it checks |
|--------|----------------|
| `test_discovery` | Driver loaded, USB bind and `device_name`, channel walk vs `init:` (including `mmio`), dmesg errors since connect |
| `test_spi` | SPI children, spidev bind/unbind, CS count, node access, flash JEDEC ID, sector erase/program/read, flash program/read bandwidth (`spi.bandwidth`) |
| `test_gpio` | Expected gpiochips, line count/names/directions, output toggle, read/write bandwidth |
| `test_irq` | GPIO loopback IRQ edges (`gpio.irq_loopback`) |
| `test_led` | LED devices from GPIO rows tagged `led`: node presence, required sysfs attrs, not requestable as GPIO, brightness set/clamp, timer blink, pattern clear/set/replace |
| `test_i2c` | Expected buses, `i2cdetect` (optional strict mode per bus), basic transaction paths, emulated SMBus block read (+ PEC), at24 EEPROM install/read/write, read bandwidth |
| `test_uart` | Loopback bandwidth and overflow recovery when `uart.devices.<name>` defines `console`, `baud`, and the optional `bandwidth` / `overflow` blocks |
| `test_ipmi` | Placeholder class only — no tests yet |
| `test_multichannel` | Concurrent I2C, GPIO, and UART bandwidth; each parallel result must meet the solo YAML floor times `multichannel.scaling_factor` |

### Protocol-level coverage

Driver-independent protocol tests live in the [`wire/`](wire/) suite (framing,
status codes, config bounds, negative cases, per-target deviation tracking). Run
it from this directory:

```sh
.venv/bin/pip install -r wire/requirements.txt
.venv/bin/pytest wire --board HELLOWORLD547 -m "not slow and not stress"
```

Note that the wire suite detaches the `lstp` driver while it runs, so re-bind the
interface before returning to `lstp_test.py`.

### Not yet covered

- LED sustained bandwidth measurements
- LED triggers beyond timer and hardware pattern (for example default-on, heartbeat)
- IPMI command/response through misc device nodes
- Automated device-tree overlay load/unload

## Python coding style

Sources follow [PEP 8](https://peps.python.org/pep-0008/) with a 100-column limit.
Settings and scripts live under [`style/`](style/):

```sh
.venv/bin/pip install -r style/requirements.txt
./style/format    # ruff format
./style/lint      # ruff format --check + ruff check
```

## Repository layout

```text
.
├── lstp_test.py            # pytest entry point, LstpTest* collectors
├── conftest.py             # CLI options, fixtures, --suite filter
├── test_*.py               # per-domain tests (discovery, spi, gpio, irq, led, i2c, …)
├── priv.py                 # sudo -n wrappers for privileged operations
├── device_results.py       # per-device outcomes and test result messages
├── deviations.py           # known_deviations registry (shared with wire/)
├── board_config.py         # board YAML loader shared with the wire suite
├── boards/                 # board YAML expectations (helloworld547.yaml, …)
├── wire/                   # protocol-level suite over libusb (see wire/README.md)
├── docs/                   # protocol specification and documentation
├── requirements.txt        # pytest runtime dependencies
└── style/                  # ruff config, format/lint/check_license scripts
```
