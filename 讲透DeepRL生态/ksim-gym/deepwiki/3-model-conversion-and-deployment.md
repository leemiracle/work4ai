> 来源: [https://deepwiki.com/kscalelabs/ksim-gym/3-model-conversion-and-deployment](https://deepwiki.com/kscalelabs/ksim-gym/3-model-conversion-and-deployment)
> DeepWiki kscalelabs/ksim-gym | Last indexed: 18 May 2025 (3e92db

# Model Conversion and Deployment

  Relevant source files 
 - [.pre-commit-config.yaml](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/.pre-commit-config.yaml)
 - [README.md](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1)
 - [convert.py](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/convert.py)
 
  This page provides an overview of how trained models in K-Sim Gym are converted from their checkpoint format to a deployable format, and the options available for deploying these models. For detailed explanations of the conversion process, see [Converting Checkpoints to K-Infer](https://deepwiki.com/kscalelabs/ksim-gym/3.1-converting-checkpoints-to-k-infer). For more information about deployment options, see [Deployment Options](https://deepwiki.com/kscalelabs/ksim-gym/3.2-deployment-options).

 
## Purpose and Workflow

 The model conversion and deployment system serves as the bridge between the training environment and the execution environment, allowing trained policies to run on both simulated and real robots. This system transforms complex JAX models with their training-specific components into optimized, portable formats that can be efficiently executed on different hardware platforms.

 
```

```

 Sources: [README.md71-86](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L71-L86) [convert.py1-104](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/convert.py#L1-L104)

 
## Model Conversion Process

 The conversion process extracts the essential components from the trained neural network policy and transforms them into a standardized format that can be deployed on various platforms. The `convert.py` script handles this process by:

 
 - Loading the trained checkpoint
 - Extracting the policy model
 - Creating deployable functions
 - Converting to ONNX format
 - Packaging into the K-Infer format
 
 
```

```

 Sources: [convert.py17-99](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/convert.py#L17-L99)

 
### Core Components

 The conversion process extracts two key functions from the trained model:

 
 - **Initialization Function (`init_fn`)**: Creates the initial recurrent state (carry) for the policy.
 - **Step Function (`step_fn`)**: Takes sensor inputs and current state, and outputs joint position targets.
 
 These functions are converted to ONNX format for platform independence and then packaged into a single K-Infer model file along with metadata like joint names.

 
```

```

 Sources: [convert.py47-76](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/convert.py#L47-L76)

 
### Key Code Components

 The central conversion functionality is implemented in the following components:

 
| Component | Purpose |
|---|---|
| make_export_model() | Creates a function that extracts deterministic actions from the policy |
| init_fn() | Initializes the recurrent state for the policy network |
| step_fn() | Processes observations and outputs actions |
| export_fn() | Converts JAX functions to ONNX format |
| pack() | Packages ONNX models and metadata into K-Infer format |

 Sources: [convert.py17-26](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/convert.py#L17-L26) [convert.py48-76](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/convert.py#L48-L76) [convert.py77-94](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/convert.py#L77-L94)

 
## Deployment Options

 Once converted to the K-Infer format, models can be deployed in two primary environments:

 
```

```

 
### K-Infer Simulator

 The K-Infer simulator allows for testing and visualization of the converted models before deploying to physical hardware. It provides:

 
 - Physics simulation of robot dynamics
 - Visualization of model behavior
 - Ability to record videos for documentation or submission
 
 
### Real Robot Deployment

 Converted models can be deployed to physical robots like K-Bot. This requires:

 
 - Converting the model to K-Infer format
 - Submitting the model for evaluation on physical hardware
 - Integration with the robot's control system
 
 Sources: [README.md77-86](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L77-L86)

 
## Command-Line Interface

 The system provides simple command-line interfaces for both conversion and deployment:

 
### Converting a Model

 
```

```

 This command loads the checkpoint file, converts the model, and saves it in K-Infer format.

 
### Deploying to K-Infer Simulator

 
```

```

 This command loads the converted model into the K-Infer simulator, specifying:

 
 - The model file path
 - The robot type (kbot)
 - Initial conditions (starting height)
 - Video recording options
 
 Sources: [README.md71-80](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L71-L80)

 
## Leaderboard Submission Process

 After successfully converting and testing a model, it can be submitted to the K-Scale Leaderboard:

 
 - Commit the converted K-Infer model to your repository
 - Record a video of the model running in the simulator
 - Make your repository public
 - Submit your repository link to the K-Scale team
 - The K-Scale team will test your model on a physical robot
 - Upon successful deployment, your submission will appear on the leaderboard
 
 Sources: [README.md82-87](https://github.com/kscalelabs/ksim-gym/blob/3e92db5c/README.md?plain=1#L82-L87)

 
## Summary

 The model conversion and deployment system transforms complex trained policies into portable, efficient models that can run on both simulated and physical robots. The conversion process extracts the essential components of the policy, converts them to a standardized format, and packages them for deployment. The resulting models can be tested in simulation before being deployed to physical robots, providing a seamless pipeline from training to real-world execution.
