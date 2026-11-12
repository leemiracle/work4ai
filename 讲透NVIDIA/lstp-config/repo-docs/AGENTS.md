# AGENTS.md

## Project

`lstp_config_tool` is a C11 CLI for reading and writing LSTP device configuration over libusb. It produces statically linked x86_64 and ARMv7 hard-float binaries.

## Key files

- `main.c`: CLI flow, confirmation, and driver cleanup
- `lstp_usb.c`: USB and sysfs driver handling
- `lstp_config_usb.c`: protocol serialization and validation
- `yaml_config.c`: strict YAML schema parsing and emission
- `lstp_config.h`: shared types, wire layouts, and protocol constants
- `sample_config/`: schema examples that must track parser changes

## Build and checks

- Build the native x86 binary with `make x86`.
- Build every available architecture with `make`.
- The first build may download and compile libusb and libyaml.
- Format changed C and header files with the repository `.clang-format`.
- Do not commit generated files under `build/` or root-level YAML device dumps.

## Safety and invariants

- Never run hardware tests, `sudo`, or device writes unless explicitly requested.
- Never bypass confirmation for nonvolatile or locked writes without explicit authorization; these operations may consume OTP or permanently lock a device.
- Validate YAML completely before accessing USB or modifying driver state.
- If the `lstp` driver is unbound, preserve cleanup paths that restore it on exit.
- Preserve packed wire layouts, explicit little-endian conversions, and static assertions.
- Keep x86_64 and ARMv7 hard-float builds working.
- When changing the YAML schema, update validation, emission, documentation, and sample configurations together.

## Style

Follow the existing C style and include the Apache-2.0 SPDX header in new source files. Prefer focused changes and descriptive error messages.