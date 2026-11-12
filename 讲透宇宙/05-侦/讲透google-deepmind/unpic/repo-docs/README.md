# unPIC

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380)

Official implementation of unPIC from **How to Spin an Object: First, Get the Shape Right**, 
a CVPRW 2026 paper ([link](https://openaccess.thecvf.com/content/CVPR2026W/GenRecon3d/html/Kabra_How_to_Spin_an_Object_First_Get_the_Shape_Right_CVPRW_2026_paper.html)). 
This repository contains the code to run our hierarchical diffusion model for generating 3D views from a single 2D input.

![unPIC architecture](teaser.png)

## Getting Started

Follow these steps to set up the project locally.

### Prerequisites

*   Python 3.8 or later
*   An NVIDIA GPU with CUDA support (RTX A4000 or above) is recommended for
    performance.

### Installation

1.  **Initialize Git LFS and clone the repository:** 
    ```sh
    git lfs install
    git clone https://github.com/google-deepmind/unpic.git
    cd unpic
    ``` 

2.  **Create and activate a virtual environment (Recommended):** 
    ```sh
    python3 -m venv unpic_env
    source unpic_env/bin/activate
    ```

3.  **Install dependencies:** The required Python packages are listed in
    `pyproject.toml`. Install them using pip: 
    `pip install .`

## Usage

You can run inference on a single image using the `run_unpic.py` script. The script
requires a path to an input image, the pre-trained model variables, and an
output directory.

**Example Command:**

```sh
python run_unpic.py \
  --input_image_path /path/to/your/image.png \
  --checkpoint_dir checkpoint/ \
  --output_dir /path/to/save/outputs/ \
  --config config.py
```

## Citing This Work

```
@InProceedings{Kabra_2026_CVPR,
    author    = {Kabra, Rishabh and A Hudson, Drew and van Steenkiste, Sjoerd and Carreira, Joao and Mitra, Niloy J},
    title     = {How to Spin an Object: First, Get the Shape Right},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops},
    month     = {June},
    year      = {2026},
    pages     = {4708-4718}
}
```
