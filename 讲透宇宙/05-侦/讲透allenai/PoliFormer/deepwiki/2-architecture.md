<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/PoliFormer · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [architecture/agent.py](architecture/agent.py)
- [architecture/models/allenact_transformer_models/allenact_dino_transformer.py](architecture/models/allenact_transformer_models/allenact_dino_transformer.py)

</details>



This document provides a comprehensive overview of the PoliFormer system architecture, detailing how the different components interact to implement on-policy reinforcement learning with transformer models for robot navigation tasks. For details about specific subsystems, see the corresponding pages for [Model Architecture](#2.1), [Inference Agent](#2.2), and [Preprocessors](#2.3).

## System Overview

PoliFormer is organized into four core subsystems that work together to enable transformer-based reinforcement learning for embodied navigation:

1. **Model Architecture** - The transformer-based neural networks that process multimodal inputs and produce action decisions
2. **Environment** - Components that represent the robot, world, and sensor observations
3. **Training System** - Infrastructure for both online and offline training of the models
4. **Evaluation System** - Components that assess model performance in navigational tasks

### High-Level Architecture Diagram

```mermaid
graph TD
    subgraph "System Components"
        ModelArch["Model Architecture"]
        Env["Environment"]
        Training["Training System"]
        Eval["Evaluation System"]
    end
    
    subgraph "Model Architecture"
        ModelArch --> DinoModel["DinoLLAMATxNavActorCritic"]
        ModelArch --> GoalEnc["DinoTxGoalEncoder"]
        ModelArch --> Preproc["Preprocessors"]
    end
    
    subgraph "Environment"
        Env --> StretchCtrl["StretchController"]
        Env --> Sensors["Sensors"]
        Env --> State["StretchState"]
    end
    
    subgraph "Training System"
        Training --> OnlineTrain["Online Training"]
        Training --> OfflineTrain["Offline Training"]
    end
    
    subgraph "Evaluation System"
        Eval --> EvalManager["OnlineEvaluatorManager"]
        Eval --> EvalWorker["OnlineEvaluatorWorker"]
        Eval --> Metrics["Metrics & Logging"]
    end
    
    DinoModel --> EvalManager
    StretchCtrl --> Sensors
    DinoModel --> OnlineTrain
    DinoModel --> OfflineTrain
    Sensors --> DinoModel
```

Sources: 
- [architecture/models/allenact_transformer_models/allenact_dino_transformer.py:51-372]()
- [architecture/agent.py:5-51]()

## Component Relationships

The PoliFormer architecture follows a modular design pattern where each component has a specific responsibility:

1. **Model Architecture**: Contains the core transformer models that process sensor data and goal specifications to produce navigation actions.
2. **Environment**: Manages the robot state, sensors, and interaction with the simulated world (AI2-THOR).
3. **Training System**: Implements the RL algorithms for training the transformer models.
4. **Evaluation System**: Handles online evaluation of trained models in navigation tasks.

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant ModelArch as "DinoLLAMATxNavActorCritic"
    participant Env as "Environment"
    participant Training as "Training System"
    participant Eval as "Evaluation System"
    
    note over ModelArch, Env: Initialization Phase
    Env->>ModelArch: Provide observation spaces
    ModelArch->>ModelArch: Initialize model components
    
    note over ModelArch, Training: Training Phase
    Training->>Env: Reset environment
    Env->>Training: Initial observations
    loop For each step
        Training->>ModelArch: Forward pass(observations, prev_actions)
        ModelArch->>Training: ActorCriticOutput(actions, values)
        Training->>Env: Execute action
        Env->>Training: New observations, rewards
        Training->>Training: Update model
    end
    
    note over ModelArch, Eval: Evaluation Phase
    Eval->>Env: Reset environment
    Env->>Eval: Initial observations
    loop For each step
        Eval->>ModelArch: Forward pass(observations)
        ModelArch->>Eval: Predicted action
        Eval->>Env: Execute action
        Env->>Eval: New observations
        Eval->>Eval: Record metrics
    end
```

Sources:
- [architecture/models/allenact_transformer_models/allenact_dino_transformer.py:248-372]()
- [architecture/agent.py:37-51]()

## Model Architecture Components

The core of PoliFormer is its transformer-based model architecture, which consists of several key components:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| DinoLLAMATxNavActorCritic | Main transformer model combining vision, text, and navigation | [allenact_dino_transformer.py:51-372]() |
| DinoTxGoalEncoder | Encodes goal specifications and visual observations | [allenact_dino_transformer.py:375-542]() |
| PositionalEncoder | Provides positional encoding for transformer inputs | [allenact_dino_transformer.py:30-48]() |

### Model Data Flow

```mermaid
graph TD
    subgraph "Input Processing"
        Obs["Observations"]
        PrevAct["Previous Actions"]
        Goal["Text Goal"]
        
        Obs --> DinoPreproc["DINO Preprocessor"]
        Goal --> T5Enc["T5 Text Encoder"]
        DinoPreproc --> VisEmb["Visual Embeddings"]
        T5Enc --> TextEmb["Text Embeddings"]
        PrevAct --> ActEmb["Action Embeddings"]
    end
    
    subgraph "Transformer Processing"
        VisEmb --> JointEmb["Joint Embeddings"]
        TextEmb --> JointEmb
        ActEmb --> JointEmb
        
        JointEmb --> PosEnc["PositionalEncoder"]
        PosEnc --> TxDec["LLAMA Transformer Decoder"]
        TxDec --> Beliefs["Belief States"]
    end
    
    subgraph "Output Processing"
        Beliefs --> Actor["Actor Head"]
        Beliefs --> Critic["Critic Head"]
        
        Actor --> Policy["Action Distribution"]
        Critic --> Value["Value Estimate"]
    end
```

Sources:
- [architecture/models/allenact_transformer_models/allenact_dino_transformer.py:51-372]()
- [architecture/models/allenact_transformer_models/allenact_dino_transformer.py:375-542]()

## Model Component Details

The `DinoLLAMATxNavActorCritic` class extends `VisualNavActorCritic` and serves as the primary model for navigational decisions. It processes visual input through the DINO (a vision transformer) and combines it with text goals through a T5 encoder.

Key internal components include:

1. **Goal Visual Encoder** - Processes visual observations and text goals
2. **State Encoders** - LLAMA transformer decoders that maintain belief states
3. **Actor-Critic Heads** - Output action distributions and value estimates

The data processing flow in the forward method can be summarized as:

```mermaid
flowchart TD
    subgraph "DinoLLAMATxNavActorCritic.forward()"
        A["Get observation embeddings"]
        B["Get previous action embeddings"]
        C["Combine embeddings"]
        D["Process through transformer decoders"]
        E["Fuse beliefs (for multiple belief models)"]
        F["Generate actor-critic output"]
        
        A --> C
        B --> C
        C --> D
        D --> E
        E --> F
    end
```

Sources:
- [architecture/models/allenact_transformer_models/allenact_dino_transformer.py:248-372]()

## Goal Encoding Process

The `DinoTxGoalEncoder` handles multimodal input processing:

```mermaid
graph TD
    subgraph "DinoTxGoalEncoder Components"
        DINO["DINO Visual Features"]
        TextGoal["Text Goal"]
        BBox["Object Bounding Boxes"]
        
        DINO --> DinoComp["DINO Compressor"]
        TextGoal --> T5["T5 Encoder"]
        BBox --> BBoxEnc["Bounding Box Encoder"]
        
        DinoComp --> VisFeats["Visual Features"]
        T5 --> TextFeats["Text Features"]
        BBoxEnc --> BBoxFeats["Box Features"]
        
        VisFeats --> TxComb["Transformer Combiner"]
        TextFeats --> TxComb
        BBoxFeats --> TxComb
        FusionToken["Fusion Token"] --> TxComb
        
        TxComb --> CombinedEmb["Combined Embeddings"]
    end
```

Sources:
- [architecture/models/allenact_transformer_models/allenact_dino_transformer.py:375-542]()

## Agent Interface

The `AbstractAgent` class defines the interface for agents in the system:

```mermaid
classDiagram
    class AbstractAgent {
        +reset() void
        +get_action_list() List[str]
        +get_action(observations, goal) Tuple[str, Any]
    }
    
    class ConcreteAgent {
        +reset() void
        +get_action_list() List[str]
        +get_action(observations, goal) Tuple[str, Any]
    }
    
    AbstractAgent <|-- ConcreteAgent
```

Sources:
- [architecture/agent.py:5-51]()

## Integration with Training and Evaluation

The model architecture integrates with the training and evaluation systems through standardized interfaces:

1. **For Training**:
   - The model receives batched observations, previous actions, and masks
   - It returns action distributions and value estimates
   - The training system uses these to compute losses and update the model

2. **For Evaluation**:
   - The model processes single observations to produce action decisions
   - The evaluation system executes these actions in the environment
   - Performance metrics are tracked and logged

## Conclusion

The PoliFormer architecture represents a sophisticated approach to visual navigation using transformer models. Its modular design allows for flexibility in experimentation, while the integration of vision transformers (DINO) with language models (LLAMA, T5) enables effective multimodal reasoning. The system supports both online reinforcement learning and offline training approaches, with a comprehensive evaluation framework to assess performance.

For more detailed information about specific components, please refer to the dedicated pages for [Model Architecture](#2.1), [Inference Agent](#2.2), and [Preprocessors](#2.3).

---

