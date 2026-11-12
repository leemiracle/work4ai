<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/satlas-super-resolution · page 8 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ssr/archs/osm_obj_discriminator_arch.py](ssr/archs/osm_obj_discriminator_arch.py)
- [ssr/models/osm_objs_esrgan_model.py](ssr/models/osm_objs_esrgan_model.py)
- [ssr/options/osm_obj_esrgan.yml](ssr/options/osm_obj_esrgan.yml)

</details>



This document covers specialized features designed for advanced use cases and research applications in the Satlas Super-Resolution system. These features extend beyond the standard training and inference workflows to enable sophisticated experiments and enhanced model capabilities.

For basic training procedures, see [Training](#5). For standard model architectures, see [Model Architectures](#4). For experimental configuration details, see [Experimental Configurations](#8.2).

## Overview

The system provides several advanced features that enable research-oriented applications and specialized training scenarios:

| Feature Category | Components | Purpose |
|-----------------|------------|---------|
| Geographic Awareness | OSM Object-Aware Training | Incorporate OpenStreetMap geographic features into discriminator training |
| Attention Mechanisms | Self-Attention Blocks | Enhanced discriminator capability for spatial feature relationships |
| Multi-Path Discriminators | Dual-Path Architecture | Separate processing for full images and extracted geographic objects |
| Advanced Loss Functions | CLIP, SSIM Integration | Semantic and structural similarity optimization |
| Preprocessing Variants | USM Sharpening Options | Configurable ground truth enhancement strategies |

## OSM Object-Aware Training Architecture

The primary advanced feature is the OSM (OpenStreetMap) object-aware training system, which incorporates geographic feature awareness into the discriminator training process.

**OSM Object-Aware Training Pipeline**

```mermaid
flowchart TD
    subgraph input["Input Data"]
        A[s2_images] --> B["S2NAIPDataset"]
        C[naip_images] --> B
        D[osm_chips_to_masks.json] --> B
    end
    
    subgraph processing["Object Processing"]
        B --> E["OSMObjESRGANModel.feed_data()"]
        E --> F["Extract Geographic Objects"]
        F --> G["Random Object Sampling"]
        G --> H["Resize to 32x32"]
    end
    
    subgraph discrimination["Dual-Path Discrimination"]
        I["SSR_RRDBNet Generator"] --> J["Generated Full Image"]
        H --> K["Generated Object Patches"]
        L["Ground Truth Full Image"] --> M["Real Object Patches"]
        
        J --> N["OSMObjDiscriminator.forward()"]
        K --> N
        L --> N
        M --> N
        
        N --> O["Full Image Prediction"]
        N --> P["Object Prediction Average"]
    end
    
    subgraph losses["Loss Computation"]
        O --> Q["Standard GAN Loss"]
        P --> R["Weighted Object GAN Loss"]
        Q --> S["Combined Loss"]
        R --> S
    end
```

Sources: [ssr/models/osm_objs_esrgan_model.py:1-427](), [ssr/archs/osm_obj_discriminator_arch.py:1-109]()

## OSM Discriminator Architecture

The `OSMObjDiscriminator` implements a dual-path architecture that processes both full images and extracted geographic objects through separate pathways.

**OSMObjDiscriminator Internal Architecture**

```mermaid
graph TB
    subgraph full_image["Full Image Path"]
        A["conv0"] --> B["conv1 (spectral_norm)"]
        B --> C["conv2 (spectral_norm)"]
        C --> D["conv3 (spectral_norm)"]
        D --> E["conv4 (upsample)"]
        E --> F["conv5 (upsample)"]
        F --> G["conv6 (upsample)"]
        G --> H["conv7"]
        H --> I["conv8"]
        I --> J["conv9"]
        J --> K["full_image_prediction"]
    end
    
    subgraph osm_path["OSM Object Path"]
        L["o_conv1"] --> M["o_conv2"]
        M --> N["SelfAttentionBlock"]
        N --> O["o_conv3"]
        O --> P["SelfAttentionBlock"]
        P --> Q["o_conv4"]
        Q --> R["object_prediction"]
    end
    
    subgraph attention["Self-Attention Details"]
        S["query_conv"] --> T["attention_computation"]
        U["key_conv"] --> T
        V["value_conv"] --> T
        T --> W["gamma_weighted_output"]
    end
```

Sources: [ssr/archs/osm_obj_discriminator_arch.py:34-109]()

## Self-Attention Implementation

The discriminator incorporates `SelfAttentionBlock` components that enhance spatial feature relationship modeling within geographic objects.

**Self-Attention Block Structure**

```mermaid
graph LR
    subgraph attention_block["SelfAttentionBlock"]
        A["input_tensor"] --> B["query_conv (1x1)"]
        A --> C["key_conv (1x1)"]
        A --> D["value_conv (1x1)"]
        
        B --> E["proj_query"]
        C --> F["proj_key"]
        D --> G["proj_value"]
        
        E --> H["bmm(query, key)"]
        F --> H
        H --> I["softmax(energy)"]
        
        I --> J["bmm(value, attention)"]
        G --> J
        
        J --> K["gamma * attention_out"]
        A --> L["residual_connection"]
        K --> M["output = gamma * out + input"]
        L --> M
    end
```

Sources: [ssr/archs/osm_obj_discriminator_arch.py:8-31]()

## Object Extraction and Processing

The OSM-aware training extracts geographic objects from both generated and ground truth images based on OpenStreetMap feature boundaries.

**Object Extraction Pipeline**

```mermaid
flowchart TD
    subgraph extraction["Object Extraction Process"]
        A["chip_objs[batch_index]"] --> B["Iterate OSM Objects"]
        B --> C["Extract Bounding Box (x1,y1,x2,y2)"]
        C --> D["Edge Case Handling"]
        D --> E["Extract Image Patches"]
        E --> F["torchvision.transforms.functional.resize(32,32)"]
        F --> G["Append to batch_gt/batch_gen"]
    end
    
    subgraph sampling["Random Sampling"]
        G --> H["random.sample(indices, n_osm_objs)"]
        H --> I["torch.stack(selected_objects)"]
        I --> J["torch.cat(all_batches)"]
    end
    
    subgraph discrimination["Discriminator Forward"]
        J --> K["OSMObjDiscriminator.forward(x, osm_objs)"]
        K --> L["Object-Specific Predictions"]
        L --> M["Average Object Predictions"]
    end
```

Sources: [ssr/models/osm_objs_esrgan_model.py:163-201]()

## Configuration Parameters

The OSM object-aware training introduces several specialized configuration parameters that control the geographic feature integration.

| Parameter | Location | Purpose | Default Value |
|-----------|----------|---------|---------------|
| `osm_obj_weight` | Root level | Weight for OSM object loss in total loss | 0.3 |
| `osm_objs_path` | datasets.train | Path to OSM chips-to-masks JSON file | Required |
| `n_osm_objs` | datasets.train | Number of objects sampled per image | 1 |
| `feed_disc_lr` | Root level | Feed low-res images to discriminator | true |

Sources: [ssr/options/osm_obj_esrgan.yml:17](), [ssr/options/osm_obj_esrgan.yml:30](), [ssr/options/osm_obj_esrgan.yml:34](), [ssr/options/osm_obj_esrgan.yml:14]()

## Loss Function Integration

The OSM-aware model extends the standard GAN loss computation to include object-specific adversarial training.

**Loss Computation Flow**

```mermaid
graph TB
    subgraph generator_losses["Generator Losses"]
        A["l_g_pix (L1Loss)"] --> G["l_g_total"]
        B["l_g_percep (PerceptualLoss)"] --> G
        C["l_g_style (PerceptualLoss)"] --> G
        D["l_g_gan (GANLoss)"] --> G
        E["l_g_gan_objs (Weighted GANLoss)"] --> G
        F["l_clip_sim (CLIPLoss)"] --> G
    end
    
    subgraph discriminator_losses["Discriminator Losses"]
        H["l_d_real (GANLoss)"] --> K["l_d_total_real"]
        I["l_d_real_objs (Weighted GANLoss)"] --> K
        
        J["l_d_fake (GANLoss)"] --> L["l_d_total_fake"]
        M["l_d_fake_objs (Weighted GANLoss)"] --> L
    end
    
    subgraph weight_application["Weight Application"]
        N["osm_obj_weight * cri_gan(obj_pred, target)"] --> E
        N --> I
        N --> M
    end
```

Sources: [ssr/models/osm_objs_esrgan_model.py:244-251](), [ssr/models/osm_objs_esrgan_model.py:284-308]()

## Network Input Configuration

The OSM discriminator requires specialized input channel configuration to accommodate additional contextual information beyond standard RGB inputs.

**Discriminator Input Channel Configuration**

```mermaid
graph LR
    subgraph channel_config["Input Channel Configuration"]
        A["base_rgb (3)"] --> D["total_channels (27)"]
        B["old_hr_optional (3)"] --> D
        C["lr_resized_optional (21)"] --> D
        
        E["feed_disc_lr=true"] --> F["Include LR Images"]
        G["old_hr available"] --> H["Include Temporal Context"]
        
        F --> I["lr_resized: F.interpolate(lr, scale_factor=4)"]
        H --> J["old_hr: previous timestamp NAIP"]
        
        I --> K["torch.cat((output, lr_resized, old_hr), dim=1)"]
        J --> K
    end
```

Sources: [ssr/options/osm_obj_esrgan.yml:92](), [ssr/models/osm_objs_esrgan_model.py:231-238](), [ssr/models/osm_objs_esrgan_model.py:269-280]()

## Model Registration and Usage

The OSM object-aware model integrates with the existing model registry system and follows the standard training interface.

**Model Integration Pattern**

```mermaid
graph TB
    subgraph registry["Model Registry"]
        A["@MODEL_REGISTRY.register()"] --> B["OSMObjESRGANModel"]
        B --> C["Inherits from SRGANModel"]
    end
    
    subgraph initialization["Model Initialization"]
        D["opt['model_type']: OSMObjESRGANModel"] --> E["Load osm_objs_path"]
        E --> F["Initialize osm_obj_weight"]
        F --> G["Load n_osm_objs parameter"]
        G --> H["Call super().__init__(opt)"]
    end
    
    subgraph training_hooks["Training Hooks"]
        I["feed_data()"] --> J["Load chip_objs from JSON"]
        K["optimize_parameters()"] --> L["Extract and process objects"]
        L --> M["Dual-path discrimination"]
        M --> N["Weighted loss computation"]
    end
```

Sources: [ssr/models/osm_objs_esrgan_model.py:22-23](), [ssr/models/osm_objs_esrgan_model.py:36-47](), [ssr/models/osm_objs_esrgan_model.py:135-138]()

---

