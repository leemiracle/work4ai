<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn_projects · page 6 Helios Foundation Model · fetched 2026-10-26 -->

# Helios Foundation Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/helios/crop_type_mapping/finetune_12months.yaml](data/helios/crop_type_mapping/finetune_12months.yaml)
- [data/helios/crop_type_mapping/finetune_1month.yaml](data/helios/crop_type_mapping/finetune_1month.yaml)
- [data/helios/crop_type_mapping/frozen_12months.yaml](data/helios/crop_type_mapping/frozen_12months.yaml)
- [data/helios/crop_type_mapping/random_12months.yaml](data/helios/crop_type_mapping/random_12months.yaml)
- [rslp/helios/model.py](rslp/helios/model.py)
- [rslp/helios/norm.py](rslp/helios/norm.py)

</details>



The Helios Foundation Model system provides integration of the Helios multimodal foundation model for remote sensing within the rslearn framework. This system enables fine-tuning of Helios models for various downstream tasks including crop type mapping, EuroSAT classification, and vessel attribute prediction.

For information about other foundation models used in the repository, see the SatlasPretrain models which are documented as part of the core infrastructure. For details about specific applications that use Helios, see [Crop Type Mapping](#7.2) and [Vessel Attribute Prediction](#4.5).

## System Architecture

The Helios system integrates into the broader rslearn infrastructure as an encoder within `MultiTaskModel` architectures. The system supports multiple modalities including Sentinel-2 L2A, Sentinel-1, WorldCover, and OpenStreetMap raster data.

```mermaid
graph TB
    subgraph "Helios Integration Architecture"
        checkpoint[checkpoint_path] --> helios_wrapper["Helios wrapper<br/>(rslp.helios.model.Helios)"]
        config_json["config.json"] --> model_config["model_config<br/>(Config.from_dict)"]
        model_config --> flexihelios["FlexiHelios Model<br/>(helios.nn.flexihelios)"]
        
        helios_wrapper --> multitask["MultiTaskModel<br/>(rslearn.models.multitask)"]
        multitask --> pooling_decoder["PoolingDecoder"]
        pooling_decoder --> classification_head["ClassificationHead"]
        
        subgraph "Input Processing"
            input_data["Input Data<br/>(sentinel2_l2a, sentinel1, etc.)"] --> helios_normalize["HeliosNormalize<br/>(rslp.helios.norm)"]
            helios_normalize --> masked_sample["MaskedHeliosSample<br/>(helios.train.masking)"]
        end
        
        masked_sample --> helios_wrapper
        flexihelios --> tokens_masks["TokensAndMasks<br/>(helios.nn.flexihelios)"]
        tokens_masks --> feature_pooling["Temporal/Modality Pooling"]
        feature_pooling --> backbone_features["BCHW Feature Maps"]
    end
```

Sources: [rslp/helios/model.py:26-159](), [data/helios/crop_type_mapping/finetune_12months.yaml:1-27]()

## Model Wrapper Implementation

The `Helios` class serves as a PyTorch module wrapper that integrates the Helios foundation model with rslearn's training infrastructure. The wrapper handles checkpoint loading, model selection, and feature extraction.

```mermaid
graph LR
    subgraph "Helios Model Wrapper Flow"
        init["__init__<br/>(checkpoint_path, selector, forward_kwargs)"] --> load_config["Load config.json<br/>(json.load)"]
        load_config --> build_model["Build Model<br/>(model_config.build)"]
        build_model --> load_checkpoint["Load Checkpoint<br/>(load_model_and_optim_state)"]
        load_checkpoint --> select_module["Select Module<br/>(selector path)"]
        
        forward_input["forward(inputs)"] --> process_modalities["Process Modalities<br/>(MODALITY_NAMES)"]
        process_modalities --> create_sample["Create MaskedHeliosSample<br/>(timestamps, masks)"]
        create_sample --> model_forward["model(sample, **forward_kwargs)"]
        model_forward --> tokens_output["TokensAndMasks output"]
        tokens_output --> temporal_pooling["Temporal/Modality Pooling<br/>(mean over dims [3,4])"]
        temporal_pooling --> spatial_reshape["Spatial Reshape<br/>(BHWC -> BCHW)"]
    end
```

Sources: [rslp/helios/model.py:29-79](), [rslp/helios/model.py:81-145]()

## Configuration Patterns

The system supports multiple training strategies through different configuration patterns. Each pattern is designed for specific use cases and training objectives.

| Configuration Type | File | Random Init | Freeze Strategy | Use Case |
|-------------------|------|-------------|-----------------|----------|
| Fine-tuning (12 months) | `finetune_12months.yaml` | False | Unfreeze at epoch 2 | Full temporal fine-tuning |
| Fine-tuning (1 month) | `finetune_1month.yaml` | False | Unfreeze at epoch 2 | Single timestep fine-tuning |
| Random baseline | `random_12months.yaml` | True | Unfreeze at epoch 0 | Performance baseline |
| Frozen features | `frozen_12months.yaml` | False | Always frozen | Feature extraction only |

Sources: [data/helios/crop_type_mapping/finetune_12months.yaml:8-14](), [data/helios/crop_type_mapping/finetune_1month.yaml:8-14](), [data/helios/crop_type_mapping/random_12months.yaml:8-14](), [data/helios/crop_type_mapping/frozen_12months.yaml:8-14]()

## Data Processing and Normalization

The Helios system includes specialized data processing components to handle the multimodal and multitemporal nature of remote sensing data.

```mermaid
graph TB
    subgraph "Helios Data Processing Pipeline"
        input_bands["Input Bands<br/>(B02, B03, B04, B08, etc.)"] --> concatenate["Concatenate Transform<br/>(rslearn.train.transforms.concatenate)"]
        concatenate --> helios_normalize["HeliosNormalize<br/>(rslp.helios.norm.HeliosNormalize)"]
        
        norm_config["Normalization Config<br/>(computed.json)"] --> helios_normalize
        
        helios_normalize --> normalized_data["Normalized Data<br/>((pixel - min_val) / (max_val - min_val))"]
        
        subgraph "Normalization Details"
            band_stats["Band Statistics<br/>(mean, std per band)"] --> min_max_calc["Min/Max Calculation<br/>(mean ± 2*std)"]
            min_max_calc --> pixel_norm["Pixel Normalization<br/>(per band, per timestep)"]
        end
        
        band_stats --> helios_normalize
    end
```

Sources: [rslp/helios/norm.py:9-58](), [data/helios/crop_type_mapping/finetune_12months.yaml:143-147]()

## Modality and Temporal Handling

The Helios wrapper processes multiple satellite data modalities and handles both single and multitemporal inputs through a unified interface.

| Modality | Description | Bands | Temporal Support |
|----------|-------------|-------|------------------|
| `sentinel2_l2a` | Sentinel-2 Level 2A | 12 bands (B01-B12) | Multitemporal |
| `sentinel1` | Sentinel-1 SAR | Multiple polarizations | Multitemporal |
| `worldcover` | ESA WorldCover | Land cover classes | Single timestep |
| `openstreetmap_raster` | OSM rasterized data | Multiple features | Single timestep |

The wrapper automatically detects the temporal dimension and creates appropriate masks and timestamps for the Helios model:

- **Timestamp Generation**: Creates month-based timestamps for temporal position encoding [rslp/helios/model.py:115-126]()
- **Mask Creation**: Generates `ONLINE_ENCODER` masks for all valid data [rslp/helios/model.py:106-113]()
- **Temporal Pooling**: Averages features across timesteps and band sets [rslp/helios/model.py:134-144]()

Sources: [rslp/helios/model.py:18-23](), [rslp/helios/model.py:91-127]()

## Integration with rslearn Framework

The Helios model integrates seamlessly with rslearn's `MultiTaskModel` architecture, serving as an encoder that can be combined with various decoders for downstream tasks.

```mermaid
graph LR
    subgraph "rslearn Integration Pattern"
        lightning_module["RslearnLightningModule"] --> multitask_model["MultiTaskModel"]
        multitask_model --> helios_encoder["Helios Encoder<br/>(selector: ['encoder'])"]
        multitask_model --> decoder_stack["Decoder Stack"]
        
        subgraph "Decoder Configuration"
            pooling_decoder["PoolingDecoder<br/>(in_channels: ENCODER_EMBEDDING_SIZE)"] --> classification_head["ClassificationHead"]
        end
        
        decoder_stack --> pooling_decoder
        
        subgraph "Training Configuration"
            freeze_callback["FreezeUnfreeze Callback<br/>(module_selector: ['model','encoder',0])"] --> training_control["Training Control<br/>(unfreeze_at_epoch: 2)"]
        end
        
        lightning_module --> freeze_callback
    end
```

The integration supports configurable parameters through template variables:
- `{CHECKPOINT_PATH}`: Path to Helios model checkpoint
- `{PATCH_SIZE}`: Spatial patch size for feature extraction  
- `{ENCODER_EMBEDDING_SIZE}`: Output feature dimension

Sources: [data/helios/crop_type_mapping/finetune_12months.yaml:4-20](), [data/helios/crop_type_mapping/finetune_12months.yaml:172-175]()

---

