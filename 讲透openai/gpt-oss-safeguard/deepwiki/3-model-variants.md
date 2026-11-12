<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gpt-oss-safeguard · page 3 Model Variants · fetched 2026-10-26 -->

# Model Variants

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/gpt-oss-safeguard-120b.png](docs/gpt-oss-safeguard-120b.png)
- [docs/gpt-oss-safeguard-20b.png](docs/gpt-oss-safeguard-20b.png)

</details>



## Purpose and Scope

This page compares the two model variants in the gpt-oss-safeguard family: `gpt-oss-safeguard-120b` and `gpt-oss-safeguard-20b`. It explains their technical specifications, deployment characteristics, and guidance for selecting the appropriate variant for your use case.

For detailed documentation on each individual variant, see [gpt-oss-safeguard-120b](#3.1) and [gpt-oss-safeguard-20b](#3.2). For information about deploying these models, see [Deployment and Integration](#8). For hardware requirements, see [Hardware Requirements](#8.1).

---

## Model Family Overview

The gpt-oss-safeguard family consists of two model variants built upon [gpt-oss](https://github.com/openai/gpt-oss), each optimized for different deployment scenarios and resource constraints. Both models implement safety reasoning capabilities and require the harmony response format for correct operation.

```mermaid
graph TB
    subgraph "gpt-oss-safeguard Model Family"
        BASE["gpt-oss foundation models"]
        
        SAFEGUARD_120["openai/gpt-oss-safeguard-120b<br/>117B total params<br/>5.1B active params"]
        SAFEGUARD_20["openai/gpt-oss-safeguard-20b<br/>21B total params<br/>3.6B active params"]
        
        BASE -->|"Safety reasoning<br/>training"| SAFEGUARD_120
        BASE -->|"Safety reasoning<br/>training"| SAFEGUARD_20
    end
    
    subgraph "Deployment Targets"
        PROD["Production Systems<br/>General Purpose<br/>High Reasoning"]
        EDGE["Lower Latency<br/>Local Deployment<br/>Specialized Tasks"]
    end
    
    subgraph "Hardware Requirements"
        GPU_120["Single 80GB GPU<br/>NVIDIA H100<br/>AMD MI300X"]
        GPU_20["Lower Resource<br/>Requirements"]
    end
    
    subgraph "Common Infrastructure"
        HF_HUB["Hugging Face Hub<br/>huggingface.co/collections/openai/gpt-oss-safeguard"]
        HARMONY["harmony response format<br/>REQUIRED"]
    end
    
    SAFEGUARD_120 -->|"Targets"| PROD
    SAFEGUARD_20 -->|"Targets"| EDGE
    
    SAFEGUARD_120 -->|"Requires"| GPU_120
    SAFEGUARD_20 -->|"Requires"| GPU_20
    
    SAFEGUARD_120 -.->|"Downloaded from"| HF_HUB
    SAFEGUARD_20 -.->|"Downloaded from"| HF_HUB
    
    SAFEGUARD_120 -.->|"Must use"| HARMONY
    SAFEGUARD_20 -.->|"Must use"| HARMONY
```

**Sources:** [README.md:14-20]()

---

## Technical Specifications Comparison

| Specification | gpt-oss-safeguard-120b | gpt-oss-safeguard-20b |
|--------------|------------------------|----------------------|
| **Total Parameters** | 117B | 21B |
| **Active Parameters** | 5.1B | 3.6B |
| **Architecture Type** | Sparse/Mixture-of-Experts | Sparse/Mixture-of-Experts |
| **GPU Requirement** | Single 80GB (H100, MI300X) | Lower resource requirements |
| **Primary Use Cases** | Production, General purpose, High reasoning | Lower latency, Local deployment, Specialized tasks |
| **Hugging Face Path** | `openai/gpt-oss-safeguard-120b` | `openai/gpt-oss-safeguard-20b` |
| **Response Format** | harmony (required) | harmony (required) |
| **Base Model** | gpt-oss-120b | gpt-oss-20b |

The parameter counts reveal both models use sparse activation patterns, where only a fraction of the total parameters are active during inference. This architectural choice enables efficient inference despite large total parameter counts.

**Sources:** [README.md:17-18]()

---

## Architectural Characteristics

```mermaid
graph LR
    subgraph "gpt-oss-safeguard-120b Architecture"
        PARAMS_120["117B Total Parameters"]
        ACTIVE_120["5.1B Active Parameters<br/>~4.4% activation rate"]
        INFERENCE_120["Single 80GB GPU<br/>Inference"]
        
        PARAMS_120 -->|"Sparse activation"| ACTIVE_120
        ACTIVE_120 -->|"Fits in"| INFERENCE_120
    end
    
    subgraph "gpt-oss-safeguard-20b Architecture"
        PARAMS_20["21B Total Parameters"]
        ACTIVE_20["3.6B Active Parameters<br/>~17% activation rate"]
        INFERENCE_20["Lower GPU Memory<br/>Inference"]
        
        PARAMS_20 -->|"Sparse activation"| ACTIVE_20
        ACTIVE_20 -->|"Fits in"| INFERENCE_20
    end
    
    subgraph "Common Training Foundation"
        SAFETY_TRAINING["Safety reasoning training"]
        HARMONY_FORMAT["harmony response format<br/>training constraint"]
        
        SAFETY_TRAINING -->|"Applied to"| PARAMS_120
        SAFETY_TRAINING -->|"Applied to"| PARAMS_20
        HARMONY_FORMAT -.->|"Required by"| PARAMS_120
        HARMONY_FORMAT -.->|"Required by"| PARAMS_20
    end
```

The 120B model activates approximately 4.4% of its parameters per inference pass, while the 20B model activates approximately 17%. This higher activation ratio in the smaller model contributes to its lower latency characteristics, as fewer routing decisions are required during forward passes.

**Sources:** [README.md:17-18](), [README.md:20]()

---

## Selection Decision Matrix

```mermaid
graph TB
    START{{"Select Model Variant"}}
    
    LATENCY{"Is sub-100ms latency<br/>critical?"}
    GPU{"Single 80GB GPU<br/>available?"}
    REASONING{"High reasoning depth<br/>required?"}
    DEPLOYMENT{"Deployment<br/>environment?"}
    LOCAL{"On-premises or<br/>edge deployment?"}
    
    START --> LATENCY
    
    LATENCY -->|"Yes"| USE_20B["Use gpt-oss-safeguard-20b"]
    LATENCY -->|"No"| GPU
    
    GPU -->|"Yes"| REASONING
    GPU -->|"No"| USE_20B
    
    REASONING -->|"Yes"| USE_120B["Use gpt-oss-safeguard-120b"]
    REASONING -->|"No"| DEPLOYMENT
    
    DEPLOYMENT -->|"Production/Cloud"| USE_120B
    DEPLOYMENT -->|"Edge/Local"| LOCAL
    
    LOCAL -->|"Yes"| USE_20B
    LOCAL -->|"No"| USE_120B
    
    USE_120B -->|"Download"| DL_120["huggingface.co/openai/<br/>gpt-oss-safeguard-120b"]
    USE_20B -->|"Download"| DL_20["huggingface.co/openai/<br/>gpt-oss-safeguard-20b"]
```

**Sources:** [README.md:17-18]()

---

## Use Case Alignment

### gpt-oss-safeguard-120b Optimal Scenarios

The 120B variant is optimized for scenarios where:

- **Production deployment**: Centralized cloud infrastructure with dedicated GPU resources
- **General purpose safety**: Broad applicability across diverse content types and policy domains
- **High reasoning tasks**: Complex policy evaluation requiring nuanced understanding
- **Hardware availability**: Single 80GB GPU (NVIDIA H100 or AMD MI300X) is available
- **Accuracy priority**: Classification precision is more important than response latency

Example use cases:
- Enterprise content moderation systems
- Multi-policy evaluation pipelines
- High-stakes safety decisions (financial services, healthcare)
- Research and policy development

### gpt-oss-safeguard-20b Optimal Scenarios

The 20B variant is optimized for scenarios where:

- **Lower latency**: Response time under 100ms is required
- **Local deployment**: On-premises or edge infrastructure without cloud connectivity
- **Specialized tasks**: Narrow domain with well-defined policy boundaries
- **Resource constraints**: 80GB GPU not available or cost-prohibitive
- **Distributed deployment**: Multiple instances across geographic regions

Example use cases:
- Real-time chat moderation
- Edge device content filtering
- Cost-sensitive deployments
- Specialized vertical applications (e.g., gaming, forums)

**Sources:** [README.md:17-18]()

---

## Common Characteristics

Both model variants share the following characteristics:

| Characteristic | Details |
|---------------|---------|
| **Base Architecture** | Built upon gpt-oss foundation models |
| **Safety Training** | Trained to reason about safety policies |
| **Policy Flexibility** | Support custom user-defined policies (bring your own policy) |
| **Response Format** | Require harmony response format; will not work correctly without it |
| **Reasoning Exposure** | Provide complete reasoning process (not for end users) |
| **Reasoning Effort** | Support low/medium/high configurable reasoning effort |
| **License** | Apache 2.0 permissive license |
| **Distribution** | Hugging Face Hub |
| **Inference API** | Similar to gpt-oss-120b and gpt-oss-20b |

**Sources:** [README.md:14-15](), [README.md:20](), [README.md:24-28]()

---

## Response Format Requirement

```mermaid
graph TB
    INPUT["User Input"]
    POLICY["Safety Policy"]
    
    FORMAT["harmony response format<br/>MANDATORY"]
    
    MODEL_120["gpt-oss-safeguard-120b"]
    MODEL_20["gpt-oss-safeguard-20b"]
    
    CORRECT["Correct Output<br/>Classification + Reasoning"]
    INCORRECT["Incorrect Output<br/>Model will not work correctly"]
    
    INPUT --> FORMAT
    POLICY --> FORMAT
    
    FORMAT -->|"Formatted input"| MODEL_120
    FORMAT -->|"Formatted input"| MODEL_20
    
    FORMAT -.->|"Without format"| INCORRECT
    
    MODEL_120 -->|"With harmony format"| CORRECT
    MODEL_20 -->|"With harmony format"| CORRECT
```

Both models were trained exclusively using the harmony response format. Attempting to use them without this format will result in incorrect behavior. The models will not function as safety classifiers if the input does not conform to the harmony structure.

For details on the harmony response format, see [Harmony Response Format](#4.2). For inference configuration, see [Inference Configuration](#8.3).

**Sources:** [README.md:20]()

---

## Model Access and Downloads

Both model variants are available through the Hugging Face Hub collection:

```
https://huggingface.co/collections/openai/gpt-oss-safeguard
```

Individual model repositories:

- **120B variant**: `https://huggingface.co/openai/gpt-oss-safeguard-120b`
- **20B variant**: `https://huggingface.co/openai/gpt-oss-safeguard-20b`

Download instructions follow the same pattern as `gpt-oss-120b` and `gpt-oss-20b`. For detailed setup instructions, see [Model Download and Setup](#8.2).

An interactive demo of the 20B variant is available at:
```
https://huggingface.co/spaces/openai/gpt-oss-safeguard-20b
```

**Sources:** [README.md:3](), [README.md:6](), [README.md:40]()

---

## Inference Similarity to gpt-oss

```mermaid
graph LR
    subgraph "gpt-oss Inference Pattern"
        GPT_OSS_120["gpt-oss-120b"]
        GPT_OSS_20["gpt-oss-20b"]
        GPT_OSS_API["gpt-oss inference APIs"]
        
        GPT_OSS_120 --> GPT_OSS_API
        GPT_OSS_20 --> GPT_OSS_API
    end
    
    subgraph "gpt-oss-safeguard Inference Pattern"
        SAFEGUARD_120["gpt-oss-safeguard-120b"]
        SAFEGUARD_20["gpt-oss-safeguard-20b"]
        SAFEGUARD_API["Similar inference APIs<br/>+ harmony format requirement"]
        
        SAFEGUARD_120 --> SAFEGUARD_API
        SAFEGUARD_20 --> SAFEGUARD_API
    end
    
    GPT_OSS_API -.->|"Pattern reused"| SAFEGUARD_API
    
    COOKBOOK["OpenAI Cookbook<br/>cookbook.openai.com/topic/gpt-oss"]
    
    COOKBOOK -->|"Guides"| GPT_OSS_API
    COOKBOOK -.->|"Applicable to"| SAFEGUARD_API
```

Inference setup for gpt-oss-safeguard models follows the same patterns as the base gpt-oss models, with the critical addition of the harmony response format requirement. Developers familiar with gpt-oss-120b or gpt-oss-20b can apply the same inference techniques to the safeguard variants.

The OpenAI Cookbook provides detailed inference examples that apply to both model families. For gpt-oss-safeguard-specific guidance, including policy formatting, see the [detailed prompting guide](https://cookbook.openai.com/articles/gpt-oss-safeguard-guide).

**Sources:** [README.md:32](), [README.md:36]()

---

## Performance Trade-offs

| Dimension | gpt-oss-safeguard-120b | gpt-oss-safeguard-20b | Considerations |
|-----------|------------------------|----------------------|----------------|
| **Latency** | Higher | Lower | 20B provides faster response times |
| **Accuracy** | Higher reasoning depth | Optimized for speed | 120B better for complex policies |
| **Resource Cost** | Requires 80GB GPU | Lower requirements | 20B more cost-effective |
| **Deployment Flexibility** | Centralized | Distributed | 20B enables edge deployment |
| **Policy Complexity** | Handles nuanced policies | Best for focused policies | 120B supports richer policy definitions |

The selection between variants should be driven by your deployment constraints and use case requirements rather than a blanket "better/worse" assessment. Both models are production-ready and implement the same core safety reasoning capabilities.

**Sources:** [README.md:17-18]()

---

## Reasoning Effort Configuration

Both model variants support configurable reasoning effort levels (low, medium, high), allowing users to trade latency for accuracy within the same model. This configuration is independent of the variant selection:

- **Low effort**: Fastest response, suitable for high-volume processing
- **Medium effort**: Balanced performance for general use
- **High effort**: Maximum accuracy for critical decisions

The reasoning effort setting applies to both variants, though the absolute latency values differ between the 120B and 20B models. For detailed information on reasoning effort configuration, see [Configurable Reasoning Effort](#4.4).

**Sources:** [README.md:27]()

---

