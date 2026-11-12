# LSTP Wire Test Suite

Protocol-level regression tests that speak LSTP directly over USB bulk endpoints
via libusb, with no kernel driver in the path. Where the parent suite asks "does
the driver expose working SPI/GPIO/I2C/UART interfaces?", these tests ask "does
the device implement the LSTP protocol as specified?" — framing, status codes,
config layout, bounds checking, ordering, and negative cases the driver would
never produce.

That difference is the reason the suite exists. A kernel driver never emits a
malformed frame, a short header, an over-declared length, or a reserved opcode,
so those paths are unreachable from the parent suite by construction.

## Relationship to the parent suite

|  | Parent suite (`../lstp_test.py`) | Wire suite (here) |
|--|----------------------------------|-------------------|
| Path to device | kernel `lstp` driver, then sysfs / `/dev` nodes | libusb bulk endpoints |
| Question answered | do the Linux interfaces work end to end | does the device obey the protocol |
| Needs the module loaded | yes | no — it detaches the driver while it runs |
| Malformed / negative frames | not reachable | core of the suite |

The two are complementary and share board YAML through
[`../board_config.py`](../board_config.py), so one file describes a part for both,
plus [`../device_results.py`](../device_results.py) (`DeviceRunner`) for
per-item pass/fail/skip tracking and [`../deviations.py`](../deviations.py)
for per-target `known_deviations` (most findings are exercised here; the driver
suite consults the same registry).

Running the wire suite detaches the kernel driver from the interface. Re-bind it
before running the parent suite again, for example:

```sh
echo -n "1-1.2.1:1.2" | sudo tee /sys/bus/usb/drivers/lstp/bind
```

## Prerequisites

- **LSTP hardware** reachable over USB. The kernel module does *not* need to be
  loaded; if it is, the suite detaches it for the duration of the run.
- **Board config** in `../boards/<name>.yaml` — the same files the parent suite
  uses, plus a few wire-only keys (see [Board configuration](#board-configuration)).
- **Python 3** virtual environment with [`requirements.txt`](requirements.txt)
  (pytest and pyusb, plus a libusb backend).
- **Device access.** Either run as root, or install a udev rule granting the test
  user access to the LSTP interface. A rule matching the vendor id and setting
  `MODE=0666` is enough, and is preferable to running the whole suite as root.

## Quick start

Run from the parent directory so the shared board loader resolves:

```sh
python3 -m venv .venv
.venv/bin/pip install -r wire/requirements.txt

# Everything except the long tiers -- the usual local run
.venv/bin/pytest wire --board HELLOWORLD547 -m "not slow and not stress"

# One module, verbose
.venv/bin/pytest wire/test_wire_config.py --board HELLOWORLD547 -v

# Full run including soak and stress (takes the SADD-mandated durations)
.venv/bin/pytest wire --board HELLOWORLD547

# Record what deviated, for the trackers
.venv/bin/pytest wire --board HELLOWORLD547 --deviations-report=wire-deviations.json
```

## Command-line options

| Option | Purpose |
|--------|---------|
| `--board <name>` | Selects `../boards/<stem>.yaml`, case-insensitively. Expected pins, buses, bandwidth floors, and declared deviations all come from it. |
| `--usb-path <PATH>` | sysfs basename (e.g. `1-1.2.1:1.2`) to pick one of several attached LSTP devices. With more than one present and no path given, the suite skips and lists the candidates rather than guessing. |
| `--wire-vid <HEX>` | Override the USB vendor id used to find the interface. |
| `--transport <name>` | Wire transport; `libusb` today. |
| `--target <name>` | Device under test (`real`; an emulated target arrives later). |
| `--allow-destructive` | Opt in to tests that mutate persistent or one-time-programmable state. Off by default, so a normal run cannot brick a part. |
| `--allow-i2c-data-path` | Force I2C bus-transaction tests to run on a firmware revision known to hang the link on any I2C transfer. |
| `--uart-loopback-raw` | Assert the UART TX/RX pair is a true hardware short. Without it, UART tests assume a console peer and stay printable-safe. |
| `--stress-iters <N>` | Iteration count for stress/soak/fuzz tests (default 200). |
| `--soak-seconds <S>` | Wall-clock duration for the `soak` profile of parametrized soak tests. |
| `--soak-cycles <N>` | Cycle count for the `soak` profile of reset cycling. |
| `--deviations-report <PATH>` | Write this run's per-finding deviation record as JSON. |

## Test tiers

Markers select how much of the suite runs:

| Marker | Meaning |
|--------|---------|
| `slow` | Long-running soak tests; nightly rather than per-commit. |
| `stress` | High-volume stress and fuzz tests. |
| `destructive` | Mutates persistent or OTP state; additionally gated by `--allow-destructive`. |
| `transport(name)` | The wire transport a test targets. |
| `target(name)` | The device type a test targets. |
| `faults` | Device-to-host fault injection; needs the emulated target. |

Tests that exist in both a fast and a full form are parametrized `[smoke]` and
`[soak]`, so `-m "not slow"` keeps the smoke variant and drops the soak one.

## Known deviations

The suite **always asserts specification-correct behaviour**. It never softens an
assertion because a particular part misbehaves. Instead, when a test observes a
deviation it consults a per-target registry ([`../deviations.py`](../deviations.py)) to
decide the verdict:

| Situation | Verdict |
|-----------|---------|
| The board YAML declares this finding | `xfail`, naming the finding and its disposition |
| It does not declare it | **hard failure** — a new defect, or a part inheriting another part's quirk |
| Declared, but observing it damages the device | `xfail` without touching the device |

The point is regression control. A blanket `xfail` written for one part silently
excuses the same bug on every other part and can never fail again; declaring
deviations per target makes each board file an explicit, reviewable compliance
record, and keeps a fresh firmware bug from hiding inside a green-looking xfail.

### Declaring a deviation

In `../boards/<name>.yaml`:

```yaml
known_deviations:
  F12:
    status: open        # an open defect; xfail only so it does not block CI
    note: "partial config writes are ACKed but never latch"
    ticket: LSTP-1234   # optional
  F3:
    status: accepted    # a reviewed, deliberate waiver for this part
    note: "MMIO config is read-only by design here"
```

A bare string (`F12: "note"`) or a plain list (`known_deviations: [F1, F2]`) also
works and means `status: open`, which is the right default while a part is still
being stabilised.

The key is a finding id, and it must match the one the deviation site names in its
`finding <ID>: ...` message — that phrase is how the id is parsed, which is also
why a message may mention requirement ids of the same shape (`GPIO-013`) without
being mistaken for one. `F<n>` ids are shared protocol-stack findings that any part
can exhibit; a deviation seen on only one part is better given a target-qualified
id (`MYBOARD-1`) so it cannot be confused with an unrelated finding elsewhere.

`open` and `accepted` both xfail, so neither blocks CI. They differ in what they
assert and in their exit criteria:

- **open** — this is broken and expected to be fixed. The declaration is a
  temporary loan against a real defect and should be deleted once the fix lands.
- **accepted** — reviewed and waived for this part. It stays.

### Reading a run

Every run ends with the deviation ledger:

```text
=================== LSTP deviations: <board> ===================
  F1    open        seen      bulk-OUT spanning >1 USB max packet is framed per ...
  F3    accepted    not seen  MMIO config is read-only by design on this part ...
  totals: 15 open defect(s) xfailed, 2 accepted waiver(s), 0 undeclared
  never reproduced this run: F3, F10 -- either the covering test did not run
  (marker/layout skip), or the device no longer deviates and the declaration
  should be deleted
```

`not seen` is a warning, never a failure: the covering test may simply have been
filtered out by a marker or skipped for the layout. But on a full run it is the
signal that a declaration has outlived its defect and should go.

### Workflows

**A run reports an undeclared deviation.** Treat it as a new finding. Reproduce
it, raise it, then either fix the device or declare it `open` with a ticket. Do
not declare it just to green the run — that is what the failure is protecting
against.

**A declared deviation stops reproducing.** The ledger lists it under "never
reproduced". Confirm the covering test actually ran, then delete the declaration
so the test goes green and any regression fails loudly again.

**Observing a deviation damages the device.** Some defects cannot be probed
safely — a flag toggle that wedges a bus, or a command that hangs the firmware
until a power cycle. Those sites call `deviations.unsafe_to_probe(fid, ...)`,
which xfails without issuing the damaging request when the target declares the
finding, and otherwise lets the real check run so a fixed part can prove it.

## Board configuration

The wire suite reads the same `../boards/<name>.yaml` files as the parent suite
and adds a few keys of its own:

| Key | Purpose |
|-----|---------|
| `expected_bcd_device` | Golden USB `bcdDevice` for the programmed image, checked as a manufacturing trace. |
| `known_deviations` | This part's declared deviations (above). |
| `i2c.smbus` | Declares a true SMBus-block-capable target. SMBus compliance tests skip without it, because an EEPROM cannot answer the question. |
| `UNSAFE_ignore_write_config_mode_result` | Lets config-write tests proceed on firmware with no to-RAM config mode. Writes may then reach non-volatile storage — opt in deliberately. |

Pins, buses, addresses, and bandwidth floors come from the shared sections, so
per-part expectations live in one file rather than in the tests.

## Test coverage

| Module | What it checks |
|--------|----------------|
| `test_wire_discovery` | Interface descriptors, LSTP version, channel enumeration, per-channel descriptors, manufacturing trace |
| `test_wire_config` | ch0 `READ_CONFIG` / `WRITE_CONFIG`: offsets, bounds, chunked reassembly, config modes, descriptor and flag writes, channel enable/disable, config lock, serviceability sweeps |
| `test_wire_protocol` | Framing, header validation, short and over-declared lengths, reserved opcodes, ordering, bulk packing, status mapping, USB reset recovery |
| `test_wire_spi` | Config prefix validity, full-duplex transfer, chip-select selection and hold, idle reads, unknown opcodes, posted writes |
| `test_wire_gpio` | Pin table, directions, values, config-field writes, debounce, IRQ config and events, LED pattern policy, reset defaults |
| `test_wire_i2c` | Config and speeds, target presence and NACK behaviour, EEPROM integrity, length bounds, bus recovery, SMBus block reads and PEC |
| `test_wire_uart` | Config and baud rates, data bits, flow-control policy, loopback patterns, RX burst handling, break generation, soak |
| `test_wire_multichannel` | Concurrent multi-channel traffic, isolation, status reporting, full service sequences |
| `test_wire_stress` | Latency benchmarks, concurrency and ordering under load, fuzz and soak profiles |

## How it fits together

- [`transport.py`](transport.py) — L1: interface discovery, bulk I/O, reset and
  re-enumeration.
- [`lstp_proto.py`](lstp_proto.py) — L0: header build/parse, status and enum
  definitions, protocol constants.
- [`ops/`](ops) — L2: per-subsystem request builders and decoders (`ch0`, `gpio`,
  `i2c`, `uart`, `spi`, `mmio`).
- [`mux.py`](mux.py) — thread-safe channel multiplexer that demultiplexes
  responses from unsolicited events for concurrency tests.
- [`softloop.py`](softloop.py) — safe UART exchange against a console peer, for
  rigs with no true hardware loopback.
- [`helpers.py`](helpers.py) — shared assertions used across wire tests.
- [`../deviations.py`](../deviations.py) — the per-target deviation registry
  (shared with the driver suite).
- [`../board_config.py`](../board_config.py) / [`../device_results.py`](../device_results.py)
  — shared board YAML loader and per-item result aggregation.
- [`conftest.py`](conftest.py) — CLI options, session fixtures, safety gates, and
  the deviation ledger.

## Python coding style

Same rules as the parent suite: [PEP 8](https://peps.python.org/pep-0008) with a
100-column limit, enforced with the scripts under [`../style/`](../style).

```sh
../style/lint      # ruff format --check + ruff check
```

## Layout

```text
../board_config.py          # board YAML loader (shared with driver suite)
../device_results.py        # per-item pass/fail/skip aggregation
../deviations.py            # per-target deviation registry (shared with driver suite)
wire/
├── conftest.py            # CLI options, fixtures, safety gates, deviation ledger
├── transport.py           # L1 host USB transport (libusb)
├── lstp_proto.py          # L0 framing, status codes, constants
├── ops/                   # L2 per-subsystem operations
├── mux.py                 # concurrent channel multiplexer
├── softloop.py            # console-safe UART loopback helpers
├── helpers.py             # shared assertions
├── test_wire_*.py         # the tests
└── requirements.txt       # pytest + pyusb
```
