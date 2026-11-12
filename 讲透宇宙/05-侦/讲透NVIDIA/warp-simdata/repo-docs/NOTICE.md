<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Notices and Attributions

Warp SimData  
Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

This product includes software developed by third parties. The following
notices apply to those components as required by their respective licenses.

---

## Bundled / Derived Components

### CGNS Static Mixer test data

`tests/data/StaticMixer_Mixed.cgns` is the Static Mixer example dataset
published by the CGNS project. `tests/data/StaticMixer.cgns` is a derived form
with mixed element sections expanded into homogeneous sections.

**Dedication:** [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0)

**Contributor:** Richard Hann

**Source:** https://cgns.org/current/examples.html#static-mixer

---

### VTK / ParaView squareBend OpenFOAM test data

`tests/data/squareBend` is the OpenFOAM `squareBend` reader test dataset
distributed by VTK and ParaView. The files match VTK's
`Testing/Data/OpenFOAM/squareBend` ExternalData objects. The case originated
from the OpenFOAM `squareBend` tutorial.

**License:** BSD 3-Clause License (VTK)

**Copyright:** Copyright (c) 1993-2015 Ken Martin, Will Schroeder, Bill Lorensen

**Sources:**

- https://github.com/Kitware/VTK/tree/master/Testing/Data/OpenFOAM/squareBend
- https://github.com/Kitware/ParaView/tree/master/Testing/Data/squareBend
- https://www.openfoam.com/news/main-news/openfoam-v1806/post-processing

---

### VTK linear-cell contour and edge tables

The compressed linear-cell case and edge tables in
`warp_simdata/operators/_iso_surface_tables.py` are derived from
`Common/DataModel/vtkMarchingCellsContourCases.cxx` at VTK commit
`f761daf6d525755e5fa854791223770f2f257a9e` and the corresponding linear-cell
implementations in that revision. See the
[pinned source file](https://gitlab.kitware.com/vtk/vtk/-/blob/f761daf6d525755e5fa854791223770f2f257a9e/Common/DataModel/vtkMarchingCellsContourCases.cxx).

**License:** BSD 3-Clause License (VTK license)

**Copyright:** Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen

**Source:** https://gitlab.kitware.com/vtk/vtk

```
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither name of Ken Martin, Will Schroeder, or Bill Lorensen nor the names
  of any contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

---

## Runtime Dependencies

### warp-lang

**License:** Apache License 2.0  
**Copyright:** Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.  
**Source:** https://github.com/NVIDIA/warp

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

---

### NumPy

**License:** BSD 3-Clause License  
**Copyright:** Copyright (c) 2005-2024, NumPy Developers. All rights reserved.  
**Source:** https://github.com/numpy/numpy

```
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the NumPy Developers nor the names of any contributors
  may be used to endorse or promote products derived from this software
  without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

---

## Optional Dependencies

### h5py (`warp-simdata[test]`)

**License:** BSD 3-Clause License  
**Copyright:** Copyright (c) 2008-2022, Andrew Collette and contributors. All rights reserved.  
**Source:** https://github.com/h5py/h5py

```
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the h5py project nor the names of its contributors
  may be used to endorse or promote products derived from this software
  without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

---

### cae-openusd-plugins (`warp-simdata[usd]`)

**License:** Apache License 2.0  
**Copyright:** Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

---

## Test Dependencies

These packages are used only during development and testing. They are not
required to install or run Warp SimData.

### pytest

**License:** MIT License  
**Copyright:** Copyright (c) 2004 Holger Krekel and others  
**Source:** https://github.com/pytest-dev/pytest

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the
following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Additional pytest plugins used under the same MIT License:
- **pytest-cov** — Copyright (c) 2010 Maho Pacheco and contributors
- **pytest-xdist** — Copyright (c) 2014 Holger Krekel and contributors
- **pytest-timeout** — Copyright (c) 2012 Floris Bruynooghe

---

## Development Tools

These tools are used only during development and do not ship with the package.

| Package     | License      | Copyright / Source |
|-------------|--------------|-------------------|
| Ruff        | MIT          | Copyright (c) 2022 Astral Software Inc.; https://github.com/astral-sh/ruff |
| mypy        | MIT          | Copyright (c) 2012-2024 Jukka Lehtosalo and contributors; https://github.com/python/mypy |
| Bandit      | Apache-2.0   | Copyright (c) 2014 PyCQA; https://github.com/PyCQA/bandit |
| pre-commit  | MIT          | Copyright (c) 2014 pre-commit dev team; https://github.com/pre-commit/pre-commit |

---

## ParaView Extensions (`extras/paraview/`)

The scripts in `extras/paraview/` are designed to run inside **ParaView**, an open-source
scientific visualization application.

**License:** BSD 3-Clause License (ParaView license)  
**Copyright:** Copyright (c) 2005-2008 Sandia Corporation, Kitware Inc.  
**Source:** https://www.paraview.org / https://github.com/Kitware/ParaView

```
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of Kitware nor Sandia Corporation nor the names of any
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

ParaView itself bundles numerous third-party libraries (VTK, Python, Qt, etc.) each
with their own licenses. When deploying a ParaView installation, consult ParaView's
own NOTICE and license documentation at https://www.paraview.org/paraview-license/.
