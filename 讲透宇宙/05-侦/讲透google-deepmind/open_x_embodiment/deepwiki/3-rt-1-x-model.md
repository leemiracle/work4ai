<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/open_x_embodiment · page 3 RT-1-X Model · fetched 2026-10-26 -->

# RT-1-X Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [models/rt1.py](models/rt1.py)
- [models/rt1_inference_example.py](models/rt1_inference_example.py)

</details>



This document provides a technical overview of the RT-1-X model architecture and capabilities. RT-1-X is a robotics transformer model designed to map visual inputs and language instructions to robot actions, enabling generalization across different robots and tasks. For details about using the RT-1-X model for inference or training, see [Using RT-1-X](#4).

## Overview

RT-1-X is an evolution of the RT-1 (Robotics Transformer) model, with improvements as described in the RT-X paper (https://arxiv.org/abs/2310.08864). The model takes RGB camera images and natural language instructions as input and outputs robot action parameters.

```mermaid
flowchart TD
    subgraph "RT-1-X Model Architecture"
        direction LR
        Input["Inputs"] --> ImageProc["Image Processing"]
        Input --> LangEmbed["Language Embedding"]
        
        ImageProc --> TokenLearner["TokenLearner"]
        LangEmbed --> FiLM["FiLM Conditioning"]
        
        TokenLearner --> Transformer["Transformer"]
        FiLM --> Transformer
        
        Transformer --> ActionPred["Action Prediction"]
        
        ActionPred --> Output["Robot Actions"]
    end
    
    subgraph "Input Types"
        RGBImage["RGB Image (300x300)"]
        TaskText["Task Instruction"]
    end
    
    subgraph "Output Types"
        WorldVec["World Vector (x,y,z)"]
        RotDelta["Rotation Delta"]
        GripperClose["Gripper Closedness"]
        BaseMovement["Base Movement (optional)"]
    end
    
    RGBImage --> Input
    TaskText --> Input
    Output --> WorldVec
    Output --> RotDelta
    Output --> GripperClose
    Output --> BaseMovement
```

Sources: [models/rt1.py:357-552](), [README.md:23-37]()

## Model Architecture

The RT-1-X model consists of several key components that process visual and language inputs to produce robot actions:

```mermaid
flowchart TD
    subgraph "RT1"["RT-1-X Model (RT1 Class)"]
        direction LR
        ImageToken["Image Tokenizer"] --> TokenFusion["Token Fusion"]
        LangEmbed["Language Embedding"] --> ImageToken
        
        TokenFusion --> TransformerProc["Transformer Processing"]
        
        TransformerProc --> ActionPred["Action Prediction"]
    end
    
    subgraph "ImageTokenizer"
        EfficientNet["EfficientNetWithFilm"] --> Conv["1x1 Convolution"]
        Conv --> FiLM["FiLM Conditioning"]
        FiLM --> TokenLearner["TokenLearnerModuleV11"] 
    end
    
    subgraph "Transformer"
        PosEmbed["Positional Embedding"] --> TransBlocks["Transformer Blocks"]
        TransBlocks --> OutputProj["Output Projection"]
    end
    
    ImageToken -.-> ImageTokenizer
    TransformerProc -.-> Transformer
```

Sources: [models/rt1.py:357-482](), [models/rt1.py:114-189](), [models/rt1.py:71-111]()

### Main Components

The RT-1-X model (`RT1` class) integrates the following core components:

1. **Image Tokenizer**: Processes RGB images using EfficientNet with FiLM conditioning and TokenLearner
2. **Transformer**: Processes the sequence of image tokens and optional action tokens  
3. **Action Tokenization**: Converts model outputs to robot action parameters

The model can be configured with various parameters:
- Number of transformer layers (default: 8)
- Layer size (default: 128)
- Number of attention heads (default: 8)
- Vocabulary size for action discretization (default: 256)
- Number of image tokens (default: 8)
- Number of action tokens (default: 11)

Sources: [models/rt1.py:357-382](), [models/rt1_inference_example.py:153-164]()

## Image Processing Pipeline

The image processing pipeline transforms raw RGB images into tokens that can be processed by the transformer architecture:

```mermaid
flowchart LR
    RGBImage["RGB Image (300x300)"] --> Normalize["Image Normalization"]
    Normalize --> EfficientNet["EfficientNet-B3"]
    LangEmbed["Language Embedding"] --> FiLMLayer["FiLM Layers in EfficientNet"]
    EfficientNet --> Conv["1x1 Convolution"]
    Conv --> FiLM["Final FiLM Conditioning"]
    LangEmbed --> FiLM
    FiLM --> TokenLearner["TokenLearnerModuleV11"]
    TokenLearner --> ImageTokens["Image Tokens (bs, seqlen, num_tokens, features)"]
```

The image processing steps are:

1. **Image Normalization**: Scales image to match EfficientNet requirements
2. **EfficientNet-B3 with FiLM**: Processes the image with language conditioning via FiLM layers
3. **1x1 Convolution**: Projects features to the desired dimension
4. **Final FiLM Conditioning**: Another conditioning layer after feature projection
5. **Token Learner**: Reduces spatial dimensions into a fixed number of tokens

The `TokenLearnerModuleV11` module uses a MLP with GELU activation to implement spatial attention, which transforms the spatial features into a fixed number of tokens that can be processed by the transformer.

Sources: [models/rt1.py:114-189](), [models/rt1.py:192-254]()

## Action System

The RT-1-X model outputs a set of action parameters that control the robot. These actions are tokenized for the model to predict and then detokenized during inference:

### Action Space

The action space consists of the following dimensions:

| Action Component | Shape | Range | Description |
|------------------|-------|-------|-------------|
| terminate_episode | (3,) | [0,1,2] | Mode selection (0: terminate, 1: arm+gripper, 2: base) |
| world_vector | (3,) | [-2.0, 2.0] | Position in world coordinates (x,y,z) |
| rotation_delta | (3,) | [-π/2, π/2] | Rotation change in radians |
| gripper_closedness_action | (1,) | [-1.0, 1.0] | Gripper state (closed to open) |
| base_displacement_vertical_rotation | (1,) | [-π, π] | Base rotation |
| base_displacement_vector | (2,) | [-1.0, 1.0] | Base movement vector |

```mermaid
flowchart LR
    subgraph "Action Tokenization Process"
        ActionInput["Robot Action Parameters"] --> Discretize["Discretize to Vocabulary"]
        Discretize --> TokenizedAction["Tokenized Action (11 dims)"]
    end
    
    subgraph "Action Detokenization Process"
        ModelOutput["Model Prediction"] --> ArgMax["argmax over vocabulary"]
        ArgMax --> TokenVector["Token Vector"]
        TokenVector --> Rescale["Rescale to Action Range"]
        Rescale --> ActionOutput["Robot Action Parameters"]
    end
```

The action tokenization process:
1. Takes continuous action values and clips them to predefined ranges
2. Normalizes values to [0,1] range
3. Scales to the vocabulary size and converts to integer tokens

During inference, the model outputs logits over the vocabulary for each action dimension, which are then converted back to continuous action values.

Sources: [models/rt1.py:257-354](), [README.md:33-37]()

## Inference Process

The inference process with RT-1-X follows this sequence:

```mermaid
sequenceDiagram
    participant Obs as Observation
    participant Model as RT-1-X Model
    participant Action as Robot Action
    
    Obs->>Model: RGB Image (300x300)
    Obs->>Model: Language Embedding
    
    Note over Model: Process image with EfficientNet+FiLM
    Note over Model: Generate image tokens with TokenLearner
    Note over Model: Process tokens through Transformer
    Note over Model: Predict action tokens
    
    Model->>Action: Detokenize action predictions
    Action->>Action: Convert to continuous action values
```

The RT-1-X inference implementation:

1. Takes an observation containing an RGB image and language embedding
2. Processes the image through the image tokenizer
3. Runs the transformer to predict action tokens
4. Detokenizes the action predictions
5. Returns a dictionary with continuous action values

The policy uses a sequence length (history window) of observations to make predictions, though in the default configuration the model doesn't use action history (controlled by the `include_prev_timesteps_actions` parameter).

Sources: [models/rt1_inference_example.py:23-145](), [models/rt1.py:384-482]()

## Model Configuration

The RT-1-X model can be configured with different parameters than the original RT-1 model:

| Parameter | RT-1 | RT-1-X | Description |
|-----------|------|--------|-------------|
| world_vector_range | (-1.0, 1.0) | (-2.0, 2.0) | Range for world position values |
| num_image_tokens | 8 | 81 | Number of image tokens |
| vocab_size | 256 | 512 | Size of action vocabulary |
| layer_size | 128 | 256 | Size of transformer layers |

The RT-1-X model also uses Token Learner to reduce the spatial dimensions of image features to a fixed number of tokens, which allows for more efficient processing in the transformer.

Sources: [models/rt1_inference_example.py:153-164](), [models/rt1.py:357-382]()

## Integration with Open X-Embodiment

RT-1-X is designed to work with the Open X-Embodiment datasets, which provide robotic data in a unified RLDS format. The model serves as a bridge between the standardized datasets and robot control systems, enabling transfer learning across different robot embodiments.

```mermaid
flowchart LR
    subgraph "Data Pipeline"
        RLDS["RLDS Datasets"] --> DataLoader["TensorFlow Datasets"]
        DataLoader --> TrainingLoop["Training Loop"]
    end
    
    subgraph "RT-1-X"
        ImageTokenizer["RT1.image_tokenizer"] --> Transformer["RT1.Transformer"]
        Transformer --> ActionPred["Action Prediction"]
    end
    
    subgraph "Deployment"
        RT1Policy["RT1Policy Class"] --> RobotActions["Robot Control System"]
    end
    
    TrainingLoop --> RT-1-X
    RT-1-X --> RT1Policy
```

The RT-1-X model checkpoint is available for download and can be used for inference using the provided example script. For more details about using RT-1-X for inference or training, refer to [Using RT-1-X](#4).

Sources: [README.md:23-43](), [models/rt1_inference_example.py:1-182]()

---

