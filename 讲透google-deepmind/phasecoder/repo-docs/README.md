# PhaseCoder: Microphone Geometry-Agnostic Spatial Audio Understanding for Multimodal LLMs
<!-- disableFinding(LINE_OVER_80) -->
[![Paper](https://img.shields.io/badge/arXiv-2402.13217-red.svg)](https://arxiv.org/abs/2601.21124)
<!-- disableFinding(LINE_OVER_80) -->
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
<!-- disableFinding(LINE_OVER_80) -->
[![Localization Demo Colab](https://img.shields.io/static/v1?label=Localization%20Demo%20Colab&message=Google%20Colab&logo=google&color=orange)](https://colab.research.google.com/github/google-deepmind/phasecoder/blob/main/phasecoder/colabs/localization_demo_colab.ipynb)

PhaseCoder is a transformer-only spatial audio encoder that is **agnostic** to
microphone geometry. PhaseCoder takes raw multichannel audio and microphone
coordinates as inputs to perform localization and produces robust spatial
embeddings and localization azimuth, elevation and distance estimates.

This repository releases the model weight checkpoints and hosts JAX / NNX
utility functions for checkpoint loading and model inference.

## Installation

You will need Python 3.10 or later. Download the code from GitHub and install:

```shell
git clone https://github.com/google-deepmind/phasecoder.git
cd phasecoder
pip install jax[cpu]
pip install -r requirements.txt
```

## Model Checkpoints

Pretrained model weights are included in the repository under `checkpoints/v1/`.
No separate download is needed — `checkpoint_utils.load_model()` finds them
automatically.

## Getting Started

```python
import numpy as np
from phasecoder_jax import checkpoint_utils
from phasecoder_jax import phasecoder_model
from phasecoder_jax import utils

# 1. Load the pretrained model
model = checkpoint_utils.load_model()

# 2. Define microphone positions (Cartesian coordinates in meters).
#    Example: STARSS23 tetrahedral mic array (4 mics).
#    Reference: https://arxiv.org/pdf/2206.01948
mic_positions = np.array([
    [ 0.0243,  0.0243,  0.0241],  # M1
    [ 0.0243, -0.0243, -0.0241],  # M2
    [-0.0243,  0.0243, -0.0241],  # M3
    [-0.0243, -0.0243,  0.0241],  # M4
])
mic_embeddings = phasecoder_model.arbitrary_mic_geometry_embeddings(
    mic_positions
)

# 3. Prepare audio input.
#    Shape: (batch, num_samples, num_mics)
#    Expected sample rate: 16000 Hz
sample_rate = 16000
duration_s = 10.0
num_samples = int(duration_s * sample_rate)
num_mics = mic_positions.shape[0]
audio = np.random.randn(1, num_samples, num_mics).astype(np.float32)

# 4. Extract magnitude-phase features
mag_phase = utils.get_mag_phase_features(audio)

# 5. Run inference
azimuth, distance, elevation, embeddings = checkpoint_utils.eval_step(
    model, mag_phase, mic_embeddings
)

# azimuth:   (batch, 38) softmax over 360° in 10° bins (37 + no-source)
# distance:  (batch, 13) softmax over distance bins (0.1 to 6.0 m + no-source)
# elevation: (batch, 18) softmax over elevation bins, (17 + no-source)
# embeddings: (batch, 256) spatial embeddings for downstream tasks
print("Predicted azimuth bin:", int(np.argmax(azimuth, axis=-1)[0]))
print("Predicted distance bin:", int(np.argmax(distance, axis=-1)[0]))
print("Predicted elevation bin:", int(np.argmax(elevation, axis=-1)[0]))
```

## Colab Demo

Try PhaseCoder in your browser with the
[Localization Demo Colab](https://colab.research.google.com/github/google-deepmind/phasecoder/blob/main/phasecoder/colabs/localization_demo_colab.ipynb).
The notebook walks through loading the model, processing multichannel audio, and
visualizing localization predictions.

## Citing this work

If you use PhaseCoder, please cite the following paper:

```
@article{dementyev2026phasecoder,
  title={PhaseCoder: Microphone Geometry-Agnostic Spatial Audio Understanding for Multimodal LLMs},
  author={Dementyev, Artem and Zulfikar, Wazeer and Hersek, Sinan and Getreuer, Pascal and Kumar, Anurag and Kumar, Vivek},
  journal={ICML},
  year={2026}
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
