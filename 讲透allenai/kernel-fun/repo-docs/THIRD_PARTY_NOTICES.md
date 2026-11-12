# Third-party notices

kernel-fun
Copyright © 2026 The Allen Institute for Artificial Intelligence

kernel-fun is licensed under the Apache License, Version 2.0 (see `LICENSE`).
This file lists the third-party open source projects it depends on, with each
project's license and required notices.

**Scope.** This package does not vendor or redistribute any of the projects
below — every one of them is installed separately by pip (see the
`dependencies` and `[project.optional-dependencies]` tables in
`pyproject.toml`). The entries here are attribution for the code kernel-fun
builds on and calls into.

The one exception is flash-linear-attention: several modules under
`src/kernel_fun/kda/_kernels/` are restructured ports of fla kernels and carry
that lineage into this repository's own source. `NOTICE` names them module by
module; the MIT license below is the one that governs those portions.

None of the dependencies below are Apache-2.0 licensed, so there is no upstream
`NOTICE` file to reproduce. If a dependency is added that is Apache-2.0, check
it for a `NOTICE` and reproduce its contents here.

## Runtime dependencies

| Component | Version tested against | License |
| --- | --- | --- |
| [fla-core](https://github.com/fla-org/flash-linear-attention) | 0.5.2 | MIT |
| [torch](https://pytorch.org) | 2.11.0+cu130 | BSD-3-Clause |
| [triton](https://github.com/triton-lang/triton) | 3.6.0 | MIT |

## Optional dependencies (`cu13` / `cu12` extras)

These ride in with the NVIDIA training base image rather than being installed
by kernel-fun in production; when absent, the runtime probe falls back to fla.

| Component | Version tested against | License |
| --- | --- | --- |
| [nvidia-cutlass-dsl](https://github.com/NVIDIA/cutlass) | 4.6.0.dev0 | NVIDIA proprietary |
| [cuda-python](https://nvidia.github.io/cuda-python/) | 13.3.1 | NVIDIA Software License |

---

## MIT License

### flash-linear-attention (fla-core) — https://github.com/fla-org/flash-linear-attention

Copyright © 2023-2026 Songlin Yang, Yu Zhang, Zhiyuan Li

### Triton — https://github.com/triton-lang/triton

Copyright © 2018-2020 Philippe Tillet
Copyright © 2020-2022 OpenAI

### License text

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## BSD 3-Clause "New" or "Revised" License

### PyTorch (torch) — https://github.com/pytorch/pytorch

From PyTorch:

    Copyright (c) 2016-     Facebook, Inc            (Adam Paszke)
    Copyright (c) 2014-     Facebook, Inc            (Soumith Chintala)
    Copyright (c) 2011-2014 Idiap Research Institute (Ronan Collobert)
    Copyright (c) 2012-2014 Deepmind Technologies    (Koray Kavukcuoglu)
    Copyright (c) 2011-2012 NEC Laboratories America (Koray Kavukcuoglu)
    Copyright (c) 2011-2013 NYU                      (Clement Farabet)
    Copyright (c) 2006-2010 NEC Laboratories America (Ronan Collobert, Leon Bottou, Iain Melvin, Jason Weston)
    Copyright (c) 2006      Idiap Research Institute (Samy Bengio)
    Copyright (c) 2001-2004 Idiap Research Institute (Ronan Collobert, Samy Bengio, Johnny Mariethoz)

From Caffe2:

    Copyright (c) 2016-present, Facebook Inc. All rights reserved.

    All contributions by Facebook:      Copyright (c) 2016 Facebook Inc.
    All contributions by Google:        Copyright (c) 2015 Google Inc.
    All contributions by Yangqing Jia:  Copyright (c) 2015 Yangqing Jia
    All contributions by Kakao Brain:   Copyright 2019-2020 Kakao Brain
    All contributions by Cruise LLC:    Copyright (c) 2022 Cruise LLC
    All contributions by Tri Dao:       Copyright (c) 2024 Tri Dao
    All contributions by Arm:           Copyright (c) 2021, 2023-2025 Arm Limited and/or its affiliates
    All contributions from Caffe:       Copyright (c) 2013, 2014, 2015, the respective contributors
    All other contributions:            Copyright (c) 2015, 2016 the respective contributors

    All rights reserved.

The full copyright roster, including the Caffe2 per-contributor model, is in
PyTorch's own `LICENSE`; the terms are:

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the names of Facebook, Deepmind Technologies, NYU, NEC Laboratories
   America and IDIAP Research Institute nor the names of its contributors may
   be used to endorse or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---

## NVIDIA proprietary licenses

The two components below are **not** open source and are **not** redistributed
by kernel-fun. They are declared as optional extras (`cu13` / `cu12`) and are
normally already present in the NVIDIA CUDA training base image, whose EULA
governs their use. Each is subject to its own NVIDIA license agreement, which
accompanies the distribution you install.

### nvidia-cutlass-dsl — https://github.com/NVIDIA/cutlass

Version 4.6.0.dev0. Distributed by NVIDIA under a proprietary license
("Other/Proprietary License" in the wheel metadata). Note that the CUTLASS
*source repository* is BSD-3-Clause, but the CuTe DSL wheels — the artifact
kernel-fun's CuTe kernels are compiled by — are shipped under NVIDIA's own
terms. Consult the license bundled with the installed package.

### cuda-python — https://nvidia.github.io/cuda-python/

Version 13.3.1. Distributed by NVIDIA under the NVIDIA Software License
(`LicenseRef-NVIDIA-SOFTWARE-LICENSE`). Consult the license bundled with the
installed package.

---

## Keeping this file current

Regenerate the dependency inventory when `pyproject.toml`'s dependency tables
change, e.g. with `pip-licenses` in the training image:

```bash
pip-licenses --format=markdown --with-urls --with-license-file \
    --packages torch triton fla-core nvidia-cutlass-dsl cuda-python
```

No trained model weights or datasets ship with this package, so there is no
weights/data attribution section.
