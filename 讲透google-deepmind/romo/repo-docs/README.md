# RoMo: Robust Motion Segmentation Improves SfM

Official code for "RoMo: Robust Motion Segmentation Improves Structure from Motion".
### [Project Page](https://romosfm.github.io/) | [Paper](https://arxiv.org/pdf/2411.18650)
<img src="https://raw.githubusercontent.com/RoMoSFM/RoMoSFM.github.io/main/static/videos/banner_video.gif" height=400>

# Installation

Follow the following commands to install the conda environment for the motion segmentation module.
The installation processes for different SfM pipelines are described separately at the end of this README file, in order to perform camera estimation with RoMo masks.

```
conda create -n romo python=3.10 numpy matplotlib pillow scikit-image absl-py opencv tqdm
conda activate romo
pip install torch==2.5.0+cu118 torchvision==0.20.0+cu118 torchaudio==2.5.0 --index-url https://download.pytorch.org/whl/cu118
pip install mediapy
export SAM2_BUILD_ALLOW_ERRORS=0
pip install --no-build-isolation "git+https://github.com/facebookresearch/sam2.git"
```
Finally, download SAMv2 models using:

```
mkdir checkpoints
wget https://github.com/facebookresearch/sam2/raw/c2ec8e14a185632b0a5d8b161928ceb50197eddc/checkpoints/download_ckpts.sh
./download_script.sh
```
Please check that all the needed versions of SAMv2 and SAMv2.1 are downloaded inside the `checkpoints` folder.
## Run

The input video should be pre-processed into a set of images, similar to DAVIS16 dataset. `scene_path` points to the folder containing these images and `gt_mask_path` points to the directory containing the `.png` or `.bmp` masks. `model_path` is the path to the output where output videos, masks and metrics will be saved. `gt_mask_path` can be excluded from the following command if no masks and quantitative evaluation are needed.

```
python romo.py --scene_path .[path to images folder] --model_path [results path] --gt_mask_path [path to gt masks if exists] --num_iters 2 --sam_refine True
```
`num_iters` is the number of refinement iterations. Set to 2 for best results, set to 1 for faster results. `sam-refine` adds a final SAMv2 refinement, this is helpful for getting a final output mask of high detail and resolution. The final masks are saved under your results directory under `masks_sam` folder.
## Run with a SfM pipeline

We describe usage with two different SfM tools below: COLMAP and TheiaSFM.
We suggest using COLMAP for scenes with a rich static background (e.g. Casual Motion dataset) and TheiaSFM together with masked dense tracks from TAPIR for scenes with plain static background (e.g. MPI Sintel).

### COLMAP
#### Installation
Please follow [COLMAP's installation page](https://colmap.github.io/install.html) to install COLMAP's CLI. The RoMo codebase is tested on COLMAP 3.9.
#### Running
After running RoMo on your video and having the final masks saved, run the three commands below to get the sparse reconstruction and cameras from COLMAP. Note the masks are passed to the first command, i.e. the feature extractor.

```
colmap feature_extractor --database_path [path to where .db file should be] --image_path [path to images folder] --ImageReader.mask_path [path to masks folder] --ImageReader.camera_model SIMPLE_RADIAL --SiftExtraction.use_gpu True --random_seed 0
colmap exhaustive_matcher --database_path .[path to .db file] --SiftMatching.use_gpu True --random_seed 0
colmap mapper --database_path [path to .db file] --image_path [path to images folder]  --output_path [results path]
```

For evaluation we rely on the `evo` library. First install this library via:

```
pip install evo
```

Then run evaluation:

```
python camera_eval.py --result_path [result path] --gt_camera_path [path to GT images.bin] --est_camera_path [path to estimated images.bin] --est_format colmap --gt_format colmap
```

There is also support for TUM camera format for the estimated cameras and you can set `est_format` to `tum` if cameras are saved in that format.

### TheiaSfM
#### Installation
For this part we use dense tracks from [TAPIR](https://github.com/google-deepmind/tapnet) and TheiaSFM the same way that is used in [ParticleSfM](https://github.com/bytedance/particle-sfm).
To install TAPIR and download its model checkpoint, run the following:

```
pip install 'tapnet[torch] @ git+https://github.com/google-deepmind/tapnet.git'
pip install tensorflow tensorflow_datasets
mkdir checkpoints/tapnet
wget -P checkpoints/tapnet https://storage.googleapis.com/dm-tapnet/bootstap/bootstapir_checkpoint_v2.pt
```

To install TheiaSfM (the adapted version of the global mapper module from ParticleSfM), first run the following commands to clone the global mapper SfM module from ParticleSfM:

```
git clone --no-checkout https://github.com/bytedance/particle-sfm.git
git sparse-checkout init
git sparse-checkout set sfm
git checkout main
cd .. && mkdir third_party && mkdir third_party/particle-sfm && cp -r particle-sfm/sfm third_party/particle-sfm && rm -rf particle-sfm
```

Then please follow the gmapper [installation README](https://github.com/bytedance/particle-sfm/blob/main/sfm/gmapper/README.md) for installing it. If you have COLMAP previously installed, you can forgo COLMAP and Ceres solver installation steps.

#### Run
To get tracks run the following command:

```
python dense_tracks.py --masks_path [path to RoMo masks] --images_path [path to images] --result_path [path to save results]
```

With TAPIR dense tracks and RoMo masks retrieved, we can run the TheiaSfM global mapper module from ParticleSfM. This module takes the masked tracks, and runs a global camera pose estimation. The global mapper module under the `particle-sfm/sfm` directory contains the code for running this bundle adjuster.

To get  cameras from the global mapper module, please run:

```
python ./third-party/particle-sfm/sfm/main_sfm.py --sfm_dir [results path] --image_dir [path to images] --traj_dir [path to tracks.npy parent directory] --remove_dynamic True
```

### Citation
```
@article{golisabour2024,
    title={{RoMo}: Robust Motion Segmentation Improves Structure from Motion},
    author={Goli, Lily and Sabour, Sara and Matthews, Mark and Brubaker, Marcus and Lagun, Dmitry and Jacobson, Alec and Fleet, David J. and Saxena, Saurabh and Tagliasacchi, Andrea},
    journal={arXiv preprint arXiv:2411.18650},
    year={2024}
}
```

## License and disclaimer

Copyright 2024 DeepMind Technologies Limited

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
