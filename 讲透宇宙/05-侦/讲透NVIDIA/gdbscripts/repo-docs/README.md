<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA Corporation. All rights reserved. -->
<!-- SPDX-License-Identifier: BSD-3-Clause -->

# NVidia's GDB Toolbox
This repository contains NVidia's GDB Python scripts and launcher utilities for
debugging supported NVidia CPU complex targets through GDB and OpenOCD.

# Overview
The GDB Toolbox loads a set of GDB commands for target attach, core
selection, register access, and debug feature inspection. It currently includes
top-level support for the following platforms:
- Grace
- Thor and ThorX
- Vera

After the toolbox is loaded, GDB commands are available for:
- Attaching and detaching platform targets with `grace`, `thor`, and `vera`.
- Selecting and listing active cores with `core`.
- Reading, writing, decoding, and searching APB, AXI/MMIO, and ARM SPR
  registers with `apb`, `axi`, and `spr`.
- Inspecting BRBE records and RAS status with `brbe`, and `ras`.

Platform attach commands automatically configure the relevant core topology,
OpenOCD access path, and packaged register databases when they are available.
Within GDB, use `help <command>` for the complete syntax of each command.

# Getting Started
You will need CMake version 3.22.1 or newer.
```bash
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=<install_path>
make -j8 install
```

The install step places the launcher in `<install_path>/bin`, GDB startup files
in `<install_path>/share/gdb`, Python command modules in
`<install_path>/share/gdb/python`, and packaged register databases in
`<install_path>/share/gdb/res`. It creates a transferable package under
`<install_path>/packages`.

To start GDB with the toolbox loaded:
```bash
<install_path>/bin/run_gdb.sh
```

On first run, `run_gdb.sh` creates a data directory named `run_gdb.sh.data` in
the current directory, detects the Python interpreter used by GDB, creates a
virtual environment, installs the Python dependencies, and writes a resolved
runtime copy of `init.gdb`. Use `--dir <dir>` to choose another data directory
or `--force` to recreate it.

Then attach to the target from inside GDB:
```gdb
vera attach <openocd_host>
```

Use `grace attach <openocd_host>` or `thor attach <openocd_host>` for those
platforms. Any non-launcher arguments are passed through to GDB, and arguments
after `--` are passed to GDB as-is:
```bash
<install_path>/bin/run_gdb.sh -- <gdb_arg> ...
```

You can also load the toolbox manually from an existing GDB session:
```gdb
source <install_path>/share/gdb/init.gdb
```

Useful first commands after launch include:
```gdb
help vera
vera attach <openocd_host>
core list
```

# Requirements
The launcher expects a Linux host with a multi-architecture GDB. By default it
looks for `/usr/bin/gdb-multiarch`; use `--gdb <prog>` to run a different GDB.

Runtime dependencies include Python 3, Python `venv`, `pip`, `lsb_release`,
and `pyyaml`. OpenOCD must be running or reachable for target attach flows.

On Ubuntu, `run_gdb.sh` checks for and can install necessary packages
including: `libhidapi-hidraw0` and `gdb-multiarch`.

`run_gdb.sh` also supports `--gdb <prog>`, `--dir <dir>`,
`--gdbscripts <dir>`, `--verbose`, and `--force`. Run
`<install_path>/bin/run_gdb.sh --help` for the current launcher options.

# Reporting an issue
Please report bugs, feature requests, or documentation issues
[here](https://github.com/NVIDIA/gdbscripts/issues/new/choose).

# Community
Please email swteg-debug-help@nvidia.com if you have any question or feedback.

# License
Files in this project are licensed according to their SPDX license identifiers.
See `LICENSE.md` for details.
