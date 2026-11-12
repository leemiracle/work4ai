# diff_knapsack

This repository contains the official implementation of the paper
"Differentiable Knapsack and Top-k Operators via Dynamic Programming".

Knapsack and Top-k operators are useful for selecting discrete subsets of
variables. However, their integration into neural networks is challenging as
they are piecewise constant, yielding gradients that are zero almost everywhere.
This codebase casts these operators as dynamic programs, and provides
differentiable relaxations by regularizing the underlying recursions. It
includes efficient parallel algorithms via Numba, supporting both deterministic
and stochastic forward passes, as well as vector-Jacobian products for the
backward pass.

Supported regularization types:

- Shannon entropy (dense and equivariant operators)
- Gini entropy (sparse operators)
- 1.5-Tsallis entropy (sparse and smooth operators)

## Installation

Simply copy relevant functions to your project.

## Citing this work

If you use this code in your research, please cite our paper:

```
@misc{vivier-ardisson_differentiable_2026,
    title = {Differentiable {Knapsack} and {Top}-k {Operators} via {Dynamic} {Programming}},
    url = {http://arxiv.org/abs/2601.21775},
    doi = {10.48550/arXiv.2601.21775},
    publisher = {arXiv},
    author = {Vivier-Ardisson, Germain and Sander, Michaël E. and Parmentier, Axel and Blondel, Mathieu},
    year = {2026},
    note = {arXiv:2601.21775 [cs]},
}
```

## License and disclaimer

Copyright 2026 Google LLC

All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
