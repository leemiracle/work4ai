> 来源: [https://deepwiki.com/deepseek-ai/Janus/5-advanced-topics](https://deepwiki.com/deepseek-ai/Janus/5-advanced-topics)
> DeepWiki deepseek-ai/Janus

# Advanced Topics

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1)
 
  This document covers advanced usage scenarios and customization options for DreamCraft3D. These topics are intended for users who have successfully run the basic pipeline and want to improve results, customize the generation process, or optimize resource usage. For basic usage and setup information, see [Overview](https://deepwiki.com/deepseek-ai/DreamCraft3D/1-overview) and [Quick Start Guide](https://deepwiki.com/deepseek-ai/DreamCraft3D/1.2-quick-start-guide).

 
## Handling the Janus Problem

 The "Janus problem" is a common issue in single-view 3D reconstruction where the model generates inconsistent or duplicate faces on the unseen side of an object (like the Roman god Janus who had two faces). This problem frequently appears during Stage 1 of the DreamCraft3D pipeline.

 
### What Causes the Janus Problem

 The Janus problem occurs because the diffusion model lacks enough 3D understanding to consistently generate the unseen parts of an object. This results in inconsistent renderings when viewing the object from different angles.

 
```

```

 Sources: [README.md123-161](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L123-L161)

 
### Solution: Training a Custom Text2Image Model

 To address the Janus problem, DreamCraft3D offers the option to train a personalized diffusion model specific to your object. This creates a more 3D-consistent guidance signal.

 The process involves two main steps:

 
 - Generate multi-view images from the reference image using Zero123++
 - Train a personalized DeepFloyd model using DreamBooth Lora
 
 
```

```

 Sources: [README.md126-161](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L126-L161)

 
### Implementation Steps

 
 - Generate multi-view images:
 
 
```

```

 
 - Train a personalized DeepFloyd model:
 
 
```

```

 
 - Use the personalized model for Stage 1 training:
 
 
```

```

 Sources: [README.md126-161](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L126-L161)

 
## Custom Diffusion Models

 DreamCraft3D's texture refinement in Stage 3 relies on Bootstrapped Score Distillation, which can be enhanced through custom diffusion models. This section covers how to train and integrate these models for better results.

 
### Training Custom Diffusion Models

 The system supports training personalized diffusion models specific to your 3D object. This approach leverages the DreamBooth technique with LoRA (Low-Rank Adaptation) to fine-tune pretrained models.

 
```

```

 Sources: [README.md9-19](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L9-L19)

 The bootstrap process is the key innovation in DreamCraft3D, where:

 
 - The current 3D model renders are used to improve the diffusion model
 - The improved diffusion model provides better guidance for 3D optimization
 - This cycle creates a mutually reinforcing improvement
 
 
### Model Selection and Compatibility

 DreamCraft3D supports multiple diffusion model architectures:

 
| Model Type | Purpose | Configuration |
|---|---|---|
| DeepFloyd IF | High-detail initial generation | system.prompt_processor.pretrained_model_name_or_path="DeepFloyd/IF-I-XL-v1.0" |
| Stable Diffusion | Texture refinement | system.guidance.pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5" |

 Both model types can be used with personalization techniques like DreamBooth and LoRA for object-specific optimization.

 
### Integration Pipeline

 
```

```

 Sources: [README.md97-121](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L97-L121)

 
## Memory Optimization Techniques

 DreamCraft3D can be resource-intensive, especially during the NeuS training phase. Here are strategies to optimize memory usage for systems with limited VRAM.

 
### Reducing Rendering Resolution

 The most effective way to reduce memory usage is to lower the rendering resolution, particularly during the NeuS stage:

 
```

```

 This technique can be applied to all stages of the pipeline. The memory consumption scales approximately quadratically with resolution.

 
```

```

 Sources: [README.md163-164](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L163-L164)

 
### Batch Size and Step Adjustments

 For further memory optimization, consider:

 
 - Reducing batch size in training configs
 - Using gradient accumulation
 - Simplifying model complexity at the cost of quality
 
 
## Advanced Export Options

 DreamCraft3D provides options for exporting high-quality textured 3D meshes after completion of all stages.

 
### Exporting Textured Meshes

 To export the final 3D model as an OBJ file with materials:

 
```

```

 This generates an OBJ file with associated MTL and texture files that can be imported into standard 3D software.

 
```

```

 Sources: [README.md166-179](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L166-L179)

 
### Export Customization

 The mesh exporter supports several configuration options:

 
| Parameter | Description | Default |
|---|---|---|
| system.exporter_type | Type of exporter (mesh-exporter, point-cloud-exporter) | mesh-exporter |
| system.mesh_resolution | Resolution of the exported mesh | 256 |
| system.export_name | Name of the exported file | output |

 
## Troubleshooting Advanced Scenarios

 
### Common Issues with the Janus Problem

 If the custom diffusion model training doesn't adequately solve the Janus problem:

 
 - Try using a different reference image with clearer object boundaries
 - Experiment with longer training duration for the personalized model (increase `max_train_steps`)
 - Adjust the instance prompt to be more specific about the object's characteristics
 
 
### Geometry vs. Texture Quality Trade-offs

 DreamCraft3D involves inherent trade-offs between geometry consistency and texture fidelity:

 
 - Stage 2 prioritizes geometry consistency at the cost of texture detail
 - Stage 3 enhances texture while preserving the geometry
 
 For optimal results, consider running Stage 3 for additional iterations if texture quality is paramount, or focus more on Stage 2 if geometric accuracy is more important.

 
```

```

 Sources: [README.md11-19](https://github.com/deepseek-ai/DreamCraft3D/blob/644dca44/README.md?plain=1#L11-L19)
