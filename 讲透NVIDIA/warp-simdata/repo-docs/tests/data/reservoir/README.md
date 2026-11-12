<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# ECLIPSE Test Grids

A small, self-contained spectrum of synthetic ECLIPSE corner-point grids,
provided in **both** the ASCII keyword format (`*.GRDECL`) and the binary
format (`*.EGRID`). Intended for use as fixtures in test suites that need
to exercise grid readers, converters, and visualization code paths.

Each dataset lives in its own subdirectory and contains a `.GRDECL` and
`.EGRID` file built from the same in-memory `Grid`, so the two are
expected to describe identical geometry. Dataset 6 properties appear only in
the GRDECL file; the EGRID contains geometry alone.

These are committed fixtures. There is no in-tree generator for this data;
if the fixtures change, update the files and this README together.

## Coordinate system

All grids use METRIC units (metres). No `MAPAXES` rotation is applied;
local grid axes coincide with map axes. Origin is at `(0, 0)` and the top
of the grid is at depth `0` m.

## Datasets

| # | Subdir | Dims (NX×NY×NZ) | Element size (dx, dy, dz) m | Active | Properties | Purpose |
|---|--------|-----------------|--------------------------|--------|------------|---------|
| 1 | `01_single_cell`    | 1×1×1   | 100, 100, 10 | 1     | —                                | Smallest valid grid; smoke test for readers and edge handling. |
| 2 | `02_tiny`           | 3×3×2   | 50, 50, 5    | 18    | —                                | Minimal multi-element grid for quick functional tests. |
| 3 | `03_small_cubic`    | 10×10×10 | 100, 100, 10 | 1000  | —                                | Cubic uniform grid; baseline regression fixture. |
| 4 | `04_anisotropic`    | 10×8×5  | 200, 100, 5  | 400   | —                                | Non-cubic elements (dx≠dy≠dz); checks aspect-ratio handling. |
| 5 | `05_with_inactive`  | 10×10×5 | 100, 100, 10 | 428   | —                                | ACTNUM mask: NW corner pillar inactive plus scattered holes. Exercises active-vs-global indexing. |
| 6 | `06_with_properties`| 10×10×5 | 100, 100, 10 | 500   | PORO, PERMX, PERMY, PERMZ, NTG   | Full geometry + petrophysical properties. PORO/PERM increase with depth; NTG is constant 0.85. |
| 7 | `07_thin_slice`     | 20×20×1 | 50, 50, 10   | 400   | —                                | Single-layer grid (NZ=1); checks degenerate-Z handling. |
| 8 | `08_column`         | 1×1×20  | 100, 100, 5  | 20    | —                                | Vertical column (NX=NY=1); checks degenerate-XY handling. |
| 9 | `09_medium`         | 30×30×10 | 50, 50, 5   | 9000  | —                                | Larger grid for scale / performance smoke tests. |

## File naming

Inside each subdirectory the basename matches the directory's role:

```
05_with_inactive/
├── WITH_INACTIVE.GRDECL
└── WITH_INACTIVE.EGRID
```

ECLIPSE conventions are case-sensitive on some tools — keep the uppercase
extensions when copying.

## What's in the GRDECL files

Geometry keywords written by `resdata`:

- `MAPUNITS`, `GRIDUNIT` (metric)
- `SPECGRID` (NX, NY, NZ, NUMRES, coordtype)
- `COORD` (pillar lines)
- `ZCORN` (corner-point depths)
- `ACTNUM` (only meaningful in `05_with_inactive` and `06_with_properties`)

Dataset 6 additionally appends `PORO`, `PERMX`, `PERMY`, `PERMZ`, `NTG`
keyword blocks after the geometry.

## What's in the EGRID files

Standard ECLIPSE binary EGRID layout — `FILEHEAD`, `MAPUNITS`, `GRIDUNIT`,
`GRIDHEAD`, `COORD`, `ZCORN`, `ACTNUM`, `ENDGRID`. The EGRID files contain
**only** geometry; petrophysical properties for dataset 6 live in the
`.GRDECL` file. If you need binary INIT-style property files, generate
them separately.

## Fixture verification

When updating or replacing these fixtures, verify that each `.GRDECL` parses
with `resdata` and that each paired `.GRDECL` / `.EGRID` dataset still
describes identical geometry.

## Suggested test coverage

- **Reader smoke tests:** load each `.EGRID` and `.GRDECL`, confirm
  dimensions and active-cell counts match the table above.
- **Format equivalence:** load the GRDECL and EGRID for the same dataset
  and assert geometry arrays (`COORD`, `ZCORN`, `ACTNUM`) are identical.
- **Property handling:** use `06_with_properties` to test that PORO and
  PERM* round-trip correctly and that values respect the ACTNUM mask if
  the consumer applies one.
- **Edge cases:** `01_single_cell`, `07_thin_slice`, `08_column` catch
  off-by-one and degenerate-axis bugs.
- **Scale:** `09_medium` is large enough to surface obvious O(N²) bugs
  without requiring production-scale inputs; runtime depends on the reader and device.

## Updating fixtures

The historical generator has been removed. Use external tooling to add or
replace fixture data, then update the dataset table above and re-run the
reservoir tests before committing the changes.
