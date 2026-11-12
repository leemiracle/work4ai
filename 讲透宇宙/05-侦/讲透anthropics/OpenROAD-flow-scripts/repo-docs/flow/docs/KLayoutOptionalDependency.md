# KLayout as an Optional Dependency

KLayout is only required for GDS/OAS stream generation, DRC, and LVS
verification. All other ORFS functionality — synthesis, floorplanning,
placement, CTS, routing, timing reports, and abstract generation — works
without KLayout installed.

## Makefile Targets

| Target | Requires KLayout | Description |
|---|---|---|
| `make finish` | Yes | Complete flow including GDS generation |
| `make gds` | Yes | Generate GDS/OAS from finished design |
| `make drc` | Yes | Run DRC checks (requires GDS) |
| `make lvs` | Yes | Run LVS checks (requires GDS) |
| `make gallery` | Yes | Generate layout screenshots |
| `make klayout_<file>` | Yes | Open result in KLayout viewer |
| `make generate_abstract` | No | Generate LEF/LIB abstracts |

A `check-klayout` guard produces a clear error message when KLayout is
missing and a KLayout-dependent target is invoked:

```
Error: KLayout not found. Install KLayout or set KLAYOUT_CMD.
Hint: KLayout is needed for GDS/DRC/LVS targets.
```

## bazel-orfs Integration

bazel-orfs uses the `do-` prefixed targets which bypass Make's dependency
management. `do-finish` / `do-final` only run the finish stage recipe
itself, while `make finish` also pulls in the GDS target as a Make
dependency. `do-gds` runs GDS generation separately (requires KLayout).

An `orfs_gds()` Bazel rule can call `do-gds` independently from
`orfs_flow()`, making KLayout an optional toolchain dependency configured
in `MODULE.bazel`.

## KLayout Tech File Generation

The `do-klayout` and `do-klayout_wrap` targets generate `.lyt` technology
files by substituting LEF and map file paths into platform templates.
This is implemented in `util/generate_klayout_tech.py` using stdlib XML
processing — no KLayout dependency required.

## Testing Without KLayout

Unit tests for all KLayout-related Python scripts use `unittest.mock` to
mock the `pya` API:

```
cd flow/test
python -m unittest test_generate_klayout_tech test_def2stream test_convertDrc
```

These tests cover:
- `.lyt` tech file generation (`test_generate_klayout_tech.py`)
- DEF-to-GDS merging logic (`test_def2stream.py`)
- DRC report conversion (`test_convertDrc.py`)
