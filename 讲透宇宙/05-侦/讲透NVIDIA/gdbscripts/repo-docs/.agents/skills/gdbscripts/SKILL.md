---
name: gdbscripts
description: >-
  Discover available NVIDIA bringup GDB commands by tracing init.gdb, platform
  source files, and their Python import graph. Use when the user asks what GDB
  commands exist, how to use gdbscripts, help with apb/axi/spr/core/vera/grace/thor,
  or needs command syntax before debugging a target.
license: BSD-3-Clause
---

<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
-->

## Install paths

`GDBSCRIPTS_ROOT` is the **install prefix** — the same location as
`GDBSCRIPTS_PATH` in `run_gdb.sh` (parent of `bin/`; override with
`run_gdb.sh --gdbscripts <dir>`).

```
GDBSCRIPTS_ROOT = <install>          # GDBSCRIPTS_PATH in run_gdb.sh
GDBSCRIPTS_SHARE = $GDBSCRIPTS_ROOT/share/gdb
DATA_DIR = <cwd>/run_gdb.sh.data     # default; override with --dir
```

| Role | Path |
|------|------|
| Launcher | `$GDBSCRIPTS_ROOT/bin/run_gdb.sh` |
| Installed init (template) | `$GDBSCRIPTS_SHARE/init.gdb` |
| **Runtime init (via run_gdb.sh)** | `$DATA_DIR/init.gdb` |
| Python modules | `$GDBSCRIPTS_SHARE/python/` |
| Resource DBs | `$GDBSCRIPTS_SHARE/res/` |
| This skill | `$GDBSCRIPTS_SHARE/.agents/skills/gdbscripts/SKILL.md` |

### Which init.gdb to read

`run_gdb.sh` copies the installed init and rewrites path placeholders:

```bash
sed -e "s;@CMAKE_INSTALL_PREFIX@;${GDBSCRIPTS_PATH};g" \
  "$GDBSCRIPTS_ROOT/share/gdb/init.gdb" > "$DATA_DIR/init.gdb"
gdb --init-command "$DATA_DIR/init.gdb"
```

When the user launches via `run_gdb.sh`, **start discovery at
`$DATA_DIR/init.gdb`** — that is the file GDB actually loads. It lists the
resolved `source` paths for platform scripts.

Use `$GDBSCRIPTS_SHARE/init.gdb` only when GDB is started manually (no
`run_gdb.sh`) or before the data dir copy exists.

## gdbscripts command discovery

Learn which GDB commands exist and what they do by walking the load path
starting at the runtime init (or the installed template if no copy exists).
Do not guess command names — trace the tree.

## Load order

1. **Read** `$DATA_DIR/init.gdb` if present, else `$GDBSCRIPTS_SHARE/init.gdb`
   - Sets `sys.path` to `$GDBSCRIPTS_SHARE/python` and `nvgdb_dir` to
     `$GDBSCRIPTS_SHARE` (paths may show as `$GDBSCRIPTS_ROOT/share/gdb` in
     the runtime copy).
   - **Sources**: platform files listed in init (e.g. `vera.py` under
     `$GDBSCRIPTS_SHARE/python/`)
   - GDB `source` executes each `.py` file; imports run as side effects and
     register commands.

2. **For each sourced platform file**, collect direct `import` lines, then
   **recursively follow** local modules (same directory / on `sys.path`).
   Skip stdlib and third-party (`gdb`, `os`, `re`, `time`, `itertools`, …).

3. **In every visited module**, find registered commands:
   - Classes: `class Name(gdb.Command)`
   - Registration: module-level `Name()` or `name_reg_access = Class()` at EOF
   - GDB command string: `super(..., self).__init__("cmdname", ...)` or
     `gdb.Command.__init__(self, "cmdname", ...)`
   - Subcommands: `supported_commands = [...]` or docstring under
     `help <cmd>` / class `__doc__`

4. **Prefer primary sources** for syntax:
   - Class docstring (`__doc__`) — shown by `help <command>` in GDB
   - `supported_commands` lists
   - `invoke()` / `cmd_*` handlers for edge cases

## Command discovery policy

Commands appear after the user runs `$GDBSCRIPTS_ROOT/bin/run_gdb.sh`
(which passes `$DATA_DIR/init.gdb` to GDB via `--init-command`).
Platform attach commands load YAML/XML databases from `$GDBSCRIPTS_SHARE/res/`.

Do not keep a static command catalog in this skill. The source tree is the
authority. When asked to list NVIDIA-specific GDB commands, use the command
context already discovered from the currently loaded gdbscripts files. If that
context is missing or precision matters, refresh it by walking the currently
loaded `init.gdb` and transitive Python imports, then looking for `gdb.Command`
registrations.

Do **not** use `info commands`, `info command`, or other broad GDB
command-listing commands as the primary source; they are not reliable for this
Python-registered command set and can mix in unrelated built-in GDB commands.
Use `help <command>` only for details on a command already found by source
discovery.

### Platform attach (sourced directly)

Typical session: `vera attach <host>` (or `grace` / `thor`), then use bus/register
commands. Attach loads platform DBs and configures `core`, `spr`, etc.

## Workflow checklist

When answering “what commands can I use?” or “how do I read register X?”:

```
- [ ] Read $DATA_DIR/init.gdb (or installed template if not using run_gdb.sh)
- [ ] Walk imports from sourced platform files (and transitive local imports)
- [ ] List gdb.Command classes + command names
- [ ] Read __doc__ / supported_commands for relevant commands
- [ ] Check platform attach path (vera vs grace vs thor) for DB loading
```

## Common patterns

**Register-access commands** share a similar shape:

```
<cmd> load <db>          # once per session / after attach
<cmd> info <pattern>     # search registers
<cmd> read <reg>         # or read /x, field syntax — see help
<cmd> write <reg> = <val>
<cmd> set <param> <args> # access mode, thread, debug, etc.
```

When the user asks about a register, field, address block, or hardware state
name, prefer targeted register lookup before general GDB discovery:

```
<cmd> info <exact_name_or_pattern>
```

Try each discovered register-access command that supports `info` before falling
back to broad commands such as `help`, `info command`, or `info commands`. If an
exact full name does not match, retry with a distinctive suffix or substring.
Only stop early when the output proves the relevant database is not loaded, the
target is not attached, or the command is not available in this session.
