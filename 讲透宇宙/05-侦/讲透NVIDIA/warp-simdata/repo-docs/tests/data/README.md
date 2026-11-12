<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Test data

This directory contains test datasets used by the test suite.

## Files

- `multicomb_0.vts` - VTK Structured Grid dataset for testing structured grid operations
- `StaticMixer_Mixed.cgns` - the CGNS example project's CC0 Static Mixer
  dataset, contributed by Richard Hann
- `StaticMixer.cgns` - a derived form of the CC0 Static Mixer dataset with
  mixed element sections expanded into homogeneous sections
- `squareBend/` - the VTK and ParaView OpenFOAM reader test dataset, derived
  from the OpenFOAM `squareBend` tutorial

The Static Mixer source and its public-domain dedication are documented on the
[CGNS example datasets page](https://cgns.org/current/examples.html#static-mixer).
The `squareBend` files match the
[VTK OpenFOAM reader test data](https://github.com/Kitware/VTK/tree/master/Testing/Data/OpenFOAM/squareBend);
full attribution is recorded in the repository's `NOTICE.md`.

## Fetch fixtures

Scientific fixture files in this directory are tracked using Git LFS (Large
File Storage); Markdown documentation is explicitly excluded by `.gitattributes`.
From the source checkout, with Git LFS installed:

```bash
git lfs install
git lfs pull
```

## Adding fixtures

Keep fixture files here and check their LFS attributes with `git check-attr filter -- path/to/file`.
Record each fixture's source, license, and any transformations; preserve required
attribution in `NOTICE.md`. Prefer small synthetic inputs where they cover the
behavior under test.
