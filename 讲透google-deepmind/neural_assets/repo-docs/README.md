# Neural Assets: 3D-Aware Multi-Object Scene Synthesis with Image Diffusion Models

Code accompanying the paper

**Neural Assets: 3D-Aware Multi-Object Scene Synthesis with Image Diffusion
Models** ([arXiv](https://arxiv.org/abs/2406.09292), [Project Page](https://neural-assets.github.io/))

_Ziyi Wu, Yulia Rubanova, Rishabh Kabra, Drew A. Hudson, Igor Gilitschenski,
Yusuf Aytar, Sjoerd van Steenkiste, Kelsey Allen, Thomas Kipf_

The code here provides an implementation of our Neural Assets framework in jax,
including a conditioning encoder to extract the appearance and pose tokens from
input data, and a diffusion-based image generator conditioned on the tokens.

We also provide an example notebook showing how to load and process data from a
public dataset MOVi, and run the model on it to compute training losses.

## Installation

Navigate to the code folder (assumed to be `neural_assets/`), and run:

```
# Create a venv.
python3 -m venv neural_assets_venv
source neural_assets_venv/bin/activate

# Install all requirements.
python3 -m pip install -r requirements.txt
```

Additionally, we make use of the ViT implementation of [big_vision](https://github.com/google-research/big_vision), which can be
installed as follows (assuming you are in the folder `neural_assets/`):

```
git clone https://github.com/google-research/big_vision.git
mv big_vision/big_vision/* big_vision/
python3 -m pip install -r big_vision/requirements.txt
```

Python version 3.13 and beyond is currently not supported.

## Usage

To run the demo, open `demo_movi_train.ipynb` inside a jupyter notebook and run
all cells. This will load, process, and visualize a batch of videos from the
[MOVi dataset](https://github.com/google-research/kubric/tree/main/challenges/movi), construct and initialize a Neural Assets model,
and run the model on a single batch to compute the training loss.

The model is defined in `modules.py` and uses a wrapped Stable Diffusion model
defined in `diffusion.py` (incl. a configurable diffusion loss). This code
release does not include a full training loop.

## Citing this work

If you use this work, please cite the following paper

```
@inproceedings{neuralassets_2024,
  title = {{Neural Assets}: 3D-Aware Multi-Object Scene Synthesis with Image Diffusion Models},
  author = {Ziyi Wu and
            Yulia Rubanova and
            Rishabh Kabra and
            Drew A. Hudson and
            Igor Gilitschenski and
            Yusuf Aytar and
            Sjoerd van Steenkiste and
            Kelsey Allen and
            Thomas Kipf},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2024}
}
```

## Acknowledgements

The code of Neural Assets communicates with and/or references the following
separate libraries and packages:

*   [Big Vision](https://github.com/google-research/big_vision)
*   [Diffusers](https://github.com/huggingface/diffusers)
*   [Flax](https://github.com/google/flax)
*   [JAX](https://github.com/jax-ml/jax/)
*   [NumPy](https://numpy.org)
*   [OpenCV](https://github.com/opencv/opencv-python)
*   [Scenic](https://github.com/google-research/scenic)
*   [TensorFlow](https://github.com/tensorflow/tensorflow)

We thank all their contributors and maintainers!

## License and disclaimer

Copyright 2025 Google LLC

All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

This code calls a function to load a Stable Diffusion checkpoint.
Your use of the Stable Diffusion Model is subject to the CreativeML Open
RAIL++-M License, particularly the ‘Use-Based Restrictions’ at paragraph 5,
which can be found here:
https://huggingface.co/stabilityai/stable-diffusion-2/blob/main/LICENSE-MODEL.

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
