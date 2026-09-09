> 来源: [https://deepwiki.com/kscalelabs/ksim-gym/4-usage-guide](https://deepwiki.com/kscalelabs/ksim-gym/4-usage-guide)
> DeepWiki kscalelabs/ksim-gym | Last indexed: 18 May 2025 (3e92db

# Usage Guide

  Relevant source files 
 - [README.md](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1)
 
  This guide provides comprehensive instructions for training, monitoring, converting, and deploying humanoid robot controllers using K-Sim Gym. The guide covers the complete workflow from setting up your environment to submitting your model to the K-Scale Leaderboard. For specific details about the training system architecture, see [Training System](https://deepwiki.com/kscalelabs/ksim-gym/2-training-system), and for information about model conversion and deployment architecture, see [Model Conversion and Deployment](https://deepwiki.com/kscalelabs/ksim-gym/3-model-conversion-and-deployment).

 
## Environment Setup

 Before using K-Sim Gym, you'll need to set up your environment properly.

 
### Prerequisites

 
 - Python 3.11 or later
 - CUDA-compatible GPU (recommended)
 - Git
 
 
### Installation

 
 - Clone the repository:
 
 
```

```

 
 - Create a Python environment (conda recommended):
 
 
```

```

 
 - Install dependencies:
 
 
```

```

 
 - Verify GPU detection:
 
 
```

```

 Sources: [README.md33-46](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L33-L46)

 
## Training Workflow

 The diagram below illustrates the standard training workflow in K-Sim Gym:

 
```

```

 Sources: [README.md48-87](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L48-L87)

 
### Basic Training Command

 To start training with default parameters:

 
```

```

 Training runs indefinitely until you either:

 
 - Press `Ctrl+C` to stop it
 - Set the `max_steps` parameter (e.g., `python -m train max_steps=100`)
 
 The model typically begins to demonstrate walking behavior within approximately 80 training steps (about 30 minutes on an RTX 4090 GPU).

 Sources: [README.md48-59](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L48-L59)

 
### Training Command Options

 To see all available command-line options:

 
```

```

 Common options include:

 
| Option | Description | Example |
|---|---|---|
| max_steps | Maximum number of training steps | python -m train max_steps=100 |
| run_mode | Run mode (train or view) | python -m train run_mode=view |
| load_from_ckpt_path | Path to load checkpoint from | python -m train load_from_ckpt_path=assets/ckpt.bin |
| batch_size | Batch size for training | python -m train batch_size=128 |
| num_envs | Number of parallel environments | python -m train num_envs=1024 |

 Sources: [README.md95-99](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L95-L99)

 
## Monitoring Training Progress

 
### Using TensorBoard

 K-Sim Gym automatically logs training metrics and videos to TensorBoard, which you can access by running:

 
```

```

 This command opens a web interface (typically at [http://localhost:6006](http://localhost:6006)) where you can monitor:

 
 - Learning metrics (reward, loss, curriculum level)
 - Environment videos
 - Model parameters
 
 
```

```

 Sources: [README.md60-63](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L60-L63)

 
## Interactive Model Visualization

 After training, you can visualize your trained model in an interactive 3D viewer:

 
```

```

 Viewer controls:

 
 - Use the mouse to move the camera
 - Hold `Ctrl` and double-click to select a robot body
 - Left or right click to apply forces to the selected body
 
 Sources: [README.md64-69](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L64-L69)

 
## Converting Models for Deployment

 
### Checkpoint to K-Infer Conversion

 To deploy your model on a real robot or in the K-Infer simulator, convert your checkpoint to the K-Infer format:

 
```

```

 This conversion process extracts the needed functions from the model and converts them to ONNX format, then packages them into a K-Infer model.

 
```

```

 Sources: [README.md71-75](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L71-L75)

 
## Visualizing with K-Infer Simulator

 To visualize your converted model in the K-Infer simulator:

 
```

```

 Key K-Infer simulator options:

 
| Option | Description | Example |
|---|---|---|
| --start-height | Initial robot height | --start-height 1.2 |
| --save-video | Save simulation to video | --save-video output.mp4 |
| --duration | Simulation duration (seconds) | --duration 10.0 |

 Sources: [README.md77-81](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L77-L81)

 
## Submitting to the Leaderboard

 To submit your model to the K-Scale Leaderboard:

 
 - Convert your best checkpoint to K-Infer format and record a demonstration video
 - Commit the K-Infer model and the recorded video to your repository
 - Make your repository public (use Git LFS if needed for large files)
 - Share your repository link in the KScale Discord #submissions channel
 - A KScale team member will test your model on a real robot and add it to the leaderboard
 
 
```

```

 Sources: [README.md82-87](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L82-L87)

 
## Advanced Usage

 
### Using Pre-trained Models

 You can initialize training from a pre-trained checkpoint:

 
```

```

 You can also directly visualize a pre-trained model:

 
```

```

 Sources: [README.md107-117](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L107-L117)

 
### Using Jupyter Notebook

 The repository includes a Jupyter notebook version of the training code which can be run in Google Colab:

 
 - Access the notebook at: [https://colab.research.google.com/github/kscalelabs/ksim-gym/blob/master/train.ipynb](https://colab.research.google.com/github/kscalelabs/ksim-gym/blob/master/train.ipynb)
 
 If working locally with the notebook, you can use pre-commit to clean notebooks before committing:

 
```

```

 Sources: [README.md24-26](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L24-L26) [README.md119-124](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L119-L124)

 
## Troubleshooting

 If you encounter issues:

 
 - Check the [KSim documentation](https://docs.kscale.dev/docs/ksim#/)
 - Ensure your GPU is properly detected by JAX
 - Verify you're using Python 3.11 or later
 - Check that your environment has all required dependencies
 - Reach out on the [KScale Discord](https://url.kscale.dev/discord) for help
 
 Sources: [README.md89-91](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L89-L91)
