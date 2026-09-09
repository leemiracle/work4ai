> 来源: [https://deepwiki.com/deepseek-ai/DreamCraft3D/2-core-pipeline](https://deepwiki.com/deepseek-ai/DreamCraft3D/2-core-pipeline)
> DeepWiki deepseek-ai/DreamCraft3D

# Core Pipeline

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1)
 
  The Core Pipeline of DreamCraft3D implements a hierarchical 3D generation approach that creates high-fidelity, coherent 3D objects from a single 2D reference image and a text prompt. This page explains the overall pipeline architecture and how the three-stage process works together to produce textured 3D models.

 For specific implementation details of each stage, see [Stage 1: Coarse Geometry Generation](https://deepwiki.com/deepseek-ai/DreamCraft3D/2.1-stage-1:-coarse-geometry-generation), [Stage 2: Geometry Refinement](https://deepwiki.com/deepseek-ai/DreamCraft3D/2.2-stage-2:-geometry-refinement), and [Stage 3: Texture Refinement](https://deepwiki.com/deepseek-ai/DreamCraft3D/2.3-stage-3:-texture-refinement).

 
## Pipeline Overview

 DreamCraft3D employs a hierarchical generation strategy with three sequential stages, each building upon the results of the previous stage. This design allows the system to progressively refine both geometry and texture.

 
```

```

 Sources:

 
 - [README.md97-121](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L97-L121)
 - [README.md26-29](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L26-L29)
 
 
## Hierarchical Generation Process

 The pipeline processes a single image through multiple stages, with each stage specializing in a specific aspect of 3D generation:

 
```

```

 Sources:

 
 - [README.md10-19](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L10-L19)
 - [README.md97-121](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L97-L121)
 
 
## Pipeline Execution Flow

 The pipeline is executed in sequential stages, with each stage using the output from the previous stage as its starting point:

 
 - **Preprocessing**: Before the main pipeline begins, the input image is processed to remove the background and generate depth and normal maps.
 - **Stage 1**: Coarse Geometry Generation

 
 - Part 1: NeRF training for multi-view consistency
 - Part 2: NeuS training for surface reconstruction
 - Output: Initial 3D geometry model
 - **Stage 2**: Geometry Refinement

 
 - Uses Score Distillation Sampling with view-dependent diffusion guidance
 - Refines the geometry while maintaining view consistency
 - Output: Refined 3D geometry
 - **Stage 3**: Texture Refinement

 
 - Uses Bootstrapped Score Distillation with a personalized diffusion model
 - Alternates between training the diffusion model and optimizing the 3D scene
 - Output: Final textured 3D mesh
 
 Each stage saves checkpoint files that are used as inputs for the next stage, creating a sequential pipeline flow.

 Sources:

 
 - [README.md97-121](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L97-L121)
 
 
## Command Structure

 
```

```

 Sources:

 
 - [README.md97-121](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L97-L121)
 - [README.md166-171](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L166-L171)
 
 
## Key Technical Components

 The pipeline integrates several key technical components that work together to achieve high-quality 3D generation:

 
### Data Flow Between Stages

 
```

```

 Sources:

 
 - [README.md97-121](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L97-L121)
 - [README.md166-171](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L166-L171)
 
 
### Bootstrapped Optimization in Stage 3

 A key innovation in DreamCraft3D is the bootstrapped optimization approach used in Stage 3. This process involves:

 
 - Training a personalized diffusion model (Dreambooth) on the renderings of the current 3D scene
 - Using this model to guide further optimization of the 3D scene
 - As the 3D scene improves, it provides better training data for the diffusion model
 - This creates a positive feedback loop (bootstrapping) that enhances both the diffusion model and 3D scene
 
 This approach allows for significant texture quality improvements while maintaining view consistency.

 Sources:

 
 - [README.md10-19](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L10-L19)
 - [README.md97-121](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L97-L121)
 
 
## Configuration Files

 The pipeline is configured through a set of YAML files, each corresponding to a stage in the process:

 
 - `configs/dreamcraft3d-coarse-nerf.yaml` - Stage 1, Part 1 (NeRF)
 - `configs/dreamcraft3d-coarse-neus.yaml` - Stage 1, Part 2 (NeuS)
 - `configs/dreamcraft3d-geometry.yaml` - Stage 2
 - `configs/dreamcraft3d-texture.yaml` - Stage 3
 
 These configuration files define the parameters, models, and training strategies used at each stage.

 
## Optional Components

 
### Handling the Janus Problem

 If the "Janus problem" (inconsistent facial features on different sides) arises in Stage 1, the pipeline provides an optional process to train a custom Text2Image model:

 
 - Generate multi-view images using Zero123++
 - Train a personalized DeepFloyd model using DreamBooth Lora
 - Use this personalized model for guidance in the training stages
 
 Sources:

 
 - [README.md123-161](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L123-L161)
 
 
## Conclusion

 The DreamCraft3D Core Pipeline represents a hierarchical approach to 3D generation that progressively refines both geometry and texture. By leveraging different specialized techniques at each stage and implementing bootstrapped optimization, the pipeline achieves high-fidelity, coherent 3D objects from a single reference image and text prompt.

 For detailed implementation of each stage, refer to the respective stage documentation ([Stage 1](https://deepwiki.com/deepseek-ai/DreamCraft3D/2.1-stage-1:-coarse-geometry-generation), [Stage 2](https://deepwiki.com/deepseek-ai/DreamCraft3D/2.2-stage-2:-geometry-refinement), [Stage 3](https://deepwiki.com/deepseek-ai/DreamCraft3D/2.3-stage-3:-texture-refinement)).
