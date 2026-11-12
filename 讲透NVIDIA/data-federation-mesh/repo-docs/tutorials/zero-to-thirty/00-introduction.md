<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# How-To: Distribute Python Functions Across DFM Sites

This guide shows you how to take existing Python functions and distribute them across multiple DFM sites, then execute a pipeline that uses these distributed functions.

In this first tutorial, you will use the `local` DFM target to run these functions in different processes as a model of a fully distributed federation.

## Scenario

Assume you have a Python script called `plot_gradient.py` that contains three functions:

- `create_gradient(shape, min, max) -> numpy.ndarray` - Creates a NumPy array of given shape
- `subset(array, index) -> numpy.ndarray` - Extracts a slice from an array given array indices
- `plot2D(array) -> PIL.Image` - Converts a 2D array to a grayscale image

It should look something like this:

```python
import numpy as np
from PIL import Image


def create_gradient(shape: tuple[int, ...], min: float = 0.0, max: float = 1.0) -> np.ndarray:
    ndims = len(shape)
    grads = [np.arange(s) for s in shape]
    grad = sum(g[tuple(slice(None) if i == j else np.newaxis for i in range(ndims))] / (shape[j] - 1) for j, g in enumerate(grads)) / ndims
    return np.asarray((max - min) * grad + min)


def subset(array: np.ndarray, index: list[int, ...]) -> np.ndarray:
    return array[tuple(index)]


def plot2D(array: np.ndarray) -> Image.Image:
    if len(np.shape(array)) != 2:
        raise ValueError("Array must be 2D to be plotted")
    normalized = ((array - array.min()) / (array.max() - array.min()) * 255).astype(np.uint8)
    return Image.fromarray(normalized, mode='L')


if __name__ == '__main__':
    gradient3D = create_gradient((200, 300, 400), min=-100, max=100)
    gradient2D = subset(gradient3D, [100])
    image = plot2D(gradient2D)
    image.save('gradient.jpg', quality=90)
```

Try this script on your system.  It should produce a file called `gradient.jpg` that looks like this:

![gradient](images/gradient.jpg)

**Goal**: Distribute these functions across multiple DFM _sites_ and run them as a pipeline from a Jupyter notebook.

This How-To is divided into the following parts:

1. [Setting up a basic Data Federation and testing it locally](01-local-federation.md)
2. [Setting your federation to use NVIDIA Flare and testing with POC mode](02-flare-poc-mode.md)

