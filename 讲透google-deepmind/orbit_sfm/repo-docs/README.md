# ORBIT: A 360 Based Benchmark for evaluating SFM pipelines

Official code for "ORBIT".

### [Project Page](https://orbit-sfm.github.io/) | [Paper](https://arxiv.org/abs/2608.22039)

## Installation

Follow the commands below to install the conda environment:

```
conda create -n orbit python=3.10 numpy scipy pandas matplotlib pillow \
  scikit-image opencv jupyter
conda activate orbit
pip install evo
```

## Provided Files and Folders

The project includes the following notebooks and data directories:

- **`create_orbit.ipynb`**: Notebook for generating benchmark clips by
  projecting pre-processed panoramic images into perspective camera frames.
- **`orbit_eval.ipynb`**: Notebook for evaluating SfM methods against the
  ground truth camera trajectories.
- **`clip_lists.txt`**: A text file listing all benchmark clips with their
  source video ID, start time, and number of frames.
- **`trajectories/`**: Text files containing the camera intrinsics and extrinsic
  rotations for each clip. Used by `create_orbit.ipynb` to render the
  evaluation clips.
- **`cameras/`**: Text files containing the ground truth camera paths (in TUM
  format). Used by `orbit_eval.ipynb` to evaluate reconstructed trajectories.

## Generating Benchmark Clips with `create_orbit.ipynb`

The input video should be pre-processed into a set of panoramic
(equirectangular) images. For example, to extract images from a
 video using `ffmpeg`:

```bash
ffmpeg -i videoplayback.webm -fps_mode passthrough \
 -enc_time_base 1/1000000 -frame_pts 1 .  /<SCENE_NAME>/images_%011d.jpg
```
It is recommended to download the videos at the highest
 available resolution (4k).

The `create_orbit.ipynb` notebook then projects
these panoramic images into the benchmark clips using the provided camera
trajectories.

Before running, set the following variables in the notebook:

- `images_dir`: Path to the directory containing the source panoramic images,
  organized by clip name.
- `output_dir`: Path to the directory where the projected clip images will be
  saved.

The notebook reads `clip_lists.txt` to determine which clips to process and
loads the corresponding trajectory files from the `trajectories/` directory.
For each clip, it reprojects the panoramic frames into perspective views and
saves the resulting images to `output_dir/{clip_name}/`.

## Evaluating SfM Methods with `orbit_eval.ipynb`

After running an SfM pipeline on the generated clips, use the
`orbit_eval.ipynb` notebook to evaluate the reconstructed camera trajectories
against the ground truth.

Before running, set the following configuration variables in the notebook:

- `CAMERAS_DIR`: Path to the `cameras/` directory containing the ground truth
  trajectories (default: `'./cameras'`).
- `ESTIMATES_DIR`: Path to the directory containing estimated trajectories,
  organized as `{method}/{clip_name}.txt` (default: `'./estimates'`).
- `METHODS`: A list of method names to evaluate, corresponding to
  subdirectories under `ESTIMATES_DIR` (e.g., `['colmap']`).

The notebook computes ATE (Absolute Trajectory Error) and RPE (Relative Pose
Error) metrics, plots per-clip trajectory comparisons, and generates summary
tables and success-rate curves.

### Example: Running with COLMAP

#### Installation

Please follow
[COLMAP's installation page](https://colmap.github.io/install.html) to install
COLMAP's CLI. The ORBIT codebase is tested on COLMAP 3.9.

#### Running

After saving the clip images using `create_orbit.ipynb`, run COLMAP as
follows:

```
colmap feature_extractor --database_path [path to .db file] \
    --image_path [path to images folder] \
    --ImageReader.camera_model SIMPLE_RADIAL \
    --SiftExtraction.use_gpu True \
    --random_seed 0
colmap exhaustive_matcher --database_path [path to .db file] \
    --SiftMatching.use_gpu True \
    --random_seed 0
colmap mapper --database_path [path to .db file] \
    --image_path [path to images folder] \
    --output_path [results path]
```

Then place the estimated trajectories under `ESTIMATES_DIR/colmap/` and run
`orbit_eval.ipynb` to evaluate.
