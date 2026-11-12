<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gpt-oss-safeguard · page 8 Deployment and Integration · fetched 2026-10-26 -->

# Deployment and Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides comprehensive technical guidance for deploying `gpt-oss-safeguard-120b` and `gpt-oss-safeguard-20b` models in production environments. It covers hardware requirements, model download procedures, inference configuration, and integration patterns for building safety classification systems.

**Scope:** This page focuses on the operational aspects of deploying the models. For model selection criteria, see [Model Variants](#3). For inference API usage patterns, see [Inference Configuration](#8.3). For policy creation and management, see [Working with Policies](#5).

Sources: [README.md:1-46]()

---

## Deployment Architecture Overview

The gpt-oss-safeguard models support multiple deployment topologies based on resource availability and use case requirements. Both models share common infrastructure patterns but differ in hardware demands and target environments.

### Deployment Topology

```mermaid
graph TB
    subgraph "Model Selection"
        UseCase["Use Case Analysis"]
        UseCase -->|"Production, High Reasoning,<br/>80GB GPU Available"| Path120["120B Deployment Path"]
        UseCase -->|"Lower Latency,<br/>Resource Constrained"| Path20["20B Deployment Path"]
    end
    
    subgraph "120B Deployment Architecture"
        HF120["Hugging Face Hub<br/>openai/gpt-oss-safeguard-120b"]
        GPU120["Single 80GB GPU<br/>H100 or MI300X"]
        Inference120["Inference Server<br/>cookbook.openai.com/topic/gpt-oss"]
        
        HF120 -->|"Download"| GPU120
        GPU120 -->|"Hosts"| Inference120
    end
    
    subgraph "20B Deployment Architecture"
        HF20["Hugging Face Hub<br/>openai/gpt-oss-safeguard-20b"]
        GPU20["GPU/CPU<br/>Lower Resources"]
        Inference20["Inference Server<br/>cookbook.openai.com/topic/gpt-oss"]
        
        HF20 -->|"Download"| GPU20
        GPU20 -->|"Hosts"| Inference20
    end
    
    Path120 --> HF120
    Path20 --> HF20
    
    subgraph "Common Infrastructure"
        HarmonyFormat["harmony response format<br/>MANDATORY"]
        Policy["Custom Policy Files<br/>example_policies/spam/policy.txt"]
        Golden["Golden Datasets<br/>example_policies/spam/golden_dataset.csv"]
        
        Inference120 -.->|"Requires"| HarmonyFormat
        Inference20 -.->|"Requires"| HarmonyFormat
        
        Inference120 -->|"Uses"| Policy
        Inference20 -->|"Uses"| Policy
        
        Inference120 -->|"Validates with"| Golden
        Inference20 -->|"Validates with"| Golden
    end
    
    subgraph "Application Layer"
        SafetyApp["Safety Classification Application"]
        
        Inference120 -->|"API"| SafetyApp
        Inference20 -->|"API"| SafetyApp
    end
```

**Deployment Architecture:** The 120B model targets centralized deployments with dedicated 80GB GPUs (NVIDIA H100, AMD MI300X), while the 20B model enables distributed or resource-constrained environments. Both variants share identical integration patterns through the harmony response format and policy-based configuration.

Sources: [README.md:17-18](), [README.md:40]()

---

## Hardware Requirements

The two model variants have distinct hardware profiles optimized for different deployment scenarios.

| Component | gpt-oss-safeguard-120b | gpt-oss-safeguard-20b |
|-----------|------------------------|------------------------|
| Total Parameters | 117B | 21B |
| Active Parameters | 5.1B | 3.6B |
| GPU Memory | Single 80GB GPU | Lower requirements |
| Recommended GPUs | NVIDIA H100, AMD MI300X | Various GPU/CPU configurations |
| Target Environment | Production, Cloud, Enterprise | Edge, On-premises, Local |

The 120B model's single-GPU requirement simplifies deployment by avoiding multi-GPU coordination complexity. The sparse architecture (5.1B active of 117B total) enables efficient inference despite the large parameter count.

**Detailed specifications:** See [Hardware Requirements](#8.1) for complete hardware specifications, deployment topology options, and resource planning guidelines.

Sources: [README.md:17-18]()

---

## Model Download and Setup

Both models are distributed through the [Hugging Face Hub](https://huggingface.co/collections/openai/gpt-oss-safeguard) and follow similar download patterns to the base `gpt-oss` models.

### Download Process

```mermaid
graph LR
    subgraph "Hugging Face Hub"
        Collection["HF Collection<br/>openai/gpt-oss-safeguard"]
        Model120["openai/gpt-oss-safeguard-120b"]
        Model20["openai/gpt-oss-safeguard-20b"]
        
        Collection --> Model120
        Collection --> Model20
    end
    
    subgraph "Local Environment"
        Download["Download Script<br/>Similar to gpt-oss-120b"]
        Storage["Model Storage<br/>Local filesystem"]
        Verify["Verification<br/>Checksum validation"]
        
        Model120 -->|"HF API"| Download
        Model20 -->|"HF API"| Download
        
        Download --> Storage
        Storage --> Verify
    end
    
    subgraph "Inference Setup"
        Load["Model Loading"]
        Config["Configuration<br/>harmony response format"]
        Ready["Ready for Inference"]
        
        Verify --> Load
        Load --> Config
        Config --> Ready
    end
```

**Model URLs:**
- 120B: `https://huggingface.co/openai/gpt-oss-safeguard-120b`
- 20B: `https://huggingface.co/openai/gpt-oss-safeguard-20b`

The download procedure mirrors the `gpt-oss-120b` setup instructions. Models are available through standard Hugging Face transformers library integration.

**Detailed instructions:** See [Model Download and Setup](#8.2) for step-by-step download procedures, authentication requirements, and initial configuration.

Sources: [README.md:3](), [README.md:40]()

---

## Inference Configuration

The models use inference patterns similar to the base `gpt-oss` models, with the critical requirement of the harmony response format.

### Inference Stack

```mermaid
graph TB
    subgraph "Application Code"
        InputContent["Content to Classify"]
        PolicyFile["Policy Definition<br/>example_policies/spam/policy.txt"]
        ReasoningEffort["Reasoning Effort<br/>low/medium/high"]
    end
    
    subgraph "Harmony Response Format Layer"
        FormatWrapper["harmony response format<br/>REQUIRED INPUT FORMAT"]
        
        InputContent -->|"Wraps"| FormatWrapper
        PolicyFile -->|"Embeds in"| FormatWrapper
        ReasoningEffort -->|"Configures"| FormatWrapper
    end
    
    subgraph "Model Inference"
        InferenceAPI["Inference API<br/>cookbook.openai.com/topic/gpt-oss"]
        ModelEngine["gpt-oss-safeguard Model<br/>120b or 20b"]
        
        FormatWrapper -->|"Input"| InferenceAPI
        InferenceAPI -->|"Processes"| ModelEngine
    end
    
    subgraph "Output Processing"
        Classification["Classification Decision<br/>VALID/INVALID"]
        Reasoning["Detailed Reasoning<br/>Developer-only"]
        Severity["Severity Level<br/>Policy-specific taxonomy"]
        
        ModelEngine -->|"Generates"| Classification
        ModelEngine -->|"Generates"| Reasoning
        ModelEngine -->|"Generates"| Severity
    end
    
    subgraph "Application Layer"
        Decision["Safety Decision"]
        Logging["Audit Logging"]
        Monitoring["Performance Monitoring"]
        
        Classification --> Decision
        Reasoning --> Logging
        Severity --> Monitoring
    end
```

**Critical requirement:** The harmony response format is mandatory. Models trained on this format will not function correctly without it.

**Configuration options:**
- **Reasoning effort:** Adjusts latency vs. accuracy trade-off (`low`, `medium`, `high`)
- **Policy integration:** Custom policies embedded in the inference request
- **Output handling:** Classification decision, detailed reasoning (not for end users), severity levels

The inference API follows patterns documented in the [OpenAI Cookbook](https://cookbook.openai.com/topic/gpt-oss) for `gpt-oss` models, adapted for safety classification.

**Detailed configuration:** See [Inference Configuration](#8.3) for API specifications, harmony format integration, and inference pattern examples.

Sources: [README.md:20](), [README.md:27](), [README.md:32]()

---

## Integration Patterns

### Safety Classification Pipeline

```mermaid
graph TB
    subgraph "User Application"
        UserContent["User-Generated Content"]
        ContentQueue["Content Processing Queue"]
    end
    
    subgraph "Policy Management"
        PolicyStore["Policy Repository<br/>example_policies/"]
        SpamPolicy["spam/policy.txt"]
        CustomPolicy["custom/policy.txt"]
        
        PolicyStore --> SpamPolicy
        PolicyStore --> CustomPolicy
    end
    
    subgraph "Inference Pipeline"
        Router["Policy Router"]
        HarmonyFormatter["Harmony Format Wrapper"]
        InferenceService["gpt-oss-safeguard Inference"]
        
        UserContent --> ContentQueue
        ContentQueue --> Router
        
        SpamPolicy -.->|"Selects"| Router
        CustomPolicy -.->|"Selects"| Router
        
        Router --> HarmonyFormatter
        HarmonyFormatter --> InferenceService
    end
    
    subgraph "Output Processing"
        Parser["Response Parser"]
        DecisionCache["Decision Cache"]
        AuditLog["Audit Trail"]
        
        InferenceService --> Parser
        Parser --> DecisionCache
        Parser --> AuditLog
    end
    
    subgraph "Action Layer"
        Classifier["Classification Result"]
        Moderator["Content Moderation"]
        Analytics["Performance Analytics"]
        
        DecisionCache --> Classifier
        Classifier --> Moderator
        AuditLog --> Analytics
    end
    
    subgraph "Validation Loop"
        GoldenDataset["Golden Dataset<br/>golden_dataset.csv"]
        Metrics["Performance Metrics<br/>Accuracy, Precision, Recall, F1"]
        
        GoldenDataset -.->|"Validates"| InferenceService
        Parser -.->|"Computes"| Metrics
    end
```

**Integration pattern:** Applications maintain policy repositories, route content through policy-specific inference pipelines, cache decisions for efficiency, and maintain audit trails for compliance and debugging.

**Key components:**
- **Policy Router:** Selects appropriate policy based on content type or context
- **Harmony Format Wrapper:** Ensures all requests conform to required input format
- **Decision Cache:** Reduces redundant inference for identical content
- **Audit Log:** Captures reasoning for developer analysis (not exposed to end users)

Sources: [README.md:26](), [README.md:36]()

---

## Production Considerations

### Deployment Checklist

| Phase | Requirement | Reference |
|-------|-------------|-----------|
| **Infrastructure** | Provision 80GB GPU for 120B or equivalent for 20B | [Hardware Requirements](#8.1) |
| **Model Setup** | Download model from Hugging Face Hub | [Model Download and Setup](#8.2) |
| **Format Integration** | Implement harmony response format wrapper | [Inference Configuration](#8.3) |
| **Policy Definition** | Create and validate custom safety policies | [Working with Policies](#5) |
| **Golden Dataset** | Build validation dataset with ground truth | [Golden Datasets](#7.1) |
| **Performance Validation** | Measure accuracy, precision, recall, F1 | [Performance Metrics](#7.2) |
| **Reasoning Effort** | Calibrate low/medium/high settings for use case | [Configurable Reasoning Effort](#4.4) |
| **Audit Logging** | Capture reasoning outputs for debugging | [Production Considerations](#8.4) |
| **Monitoring** | Track latency, throughput, classification distribution | [Production Considerations](#8.4) |
| **Error Handling** | Implement retry logic and fallback mechanisms | [Production Considerations](#8.4) |

### Operational Workflow

```mermaid
graph LR
    subgraph "Pre-Production"
        PolicyDev["Policy Development<br/>example_policies/spam/policy.txt"]
        GoldenSet["Golden Dataset Creation<br/>golden_dataset.csv"]
        Validation["Validation Testing<br/>Metrics: Accuracy, Precision, Recall, F1"]
        
        PolicyDev --> GoldenSet
        GoldenSet --> Validation
    end
    
    subgraph "Production"
        Deploy["Model Deployment<br/>openai/gpt-oss-safeguard"]
        Monitor["Performance Monitoring"]
        Audit["Audit Trail Analysis"]
        
        Validation --> Deploy
        Deploy --> Monitor
        Deploy --> Audit
    end
    
    subgraph "Continuous Improvement"
        Feedback["User Feedback<br/>ROOST Model Community"]
        PolicyIterate["Policy Iteration"]
        ModelUpdate["Model Updates"]
        
        Monitor --> Feedback
        Audit --> Feedback
        Feedback --> PolicyIterate
        Feedback --> ModelUpdate
    end
    
    PolicyIterate -.->|"Redeploy"| PolicyDev
    ModelUpdate -.->|"Upgrade"| Deploy
```

**Operational cycle:** Policies are developed and validated pre-production using golden datasets. Production deployments generate monitoring data and audit trails, which feed back into policy iteration through the ROOST Model Community partnership.

**Critical production aspects:**
1. **Latency optimization:** Reasoning effort configuration balances accuracy and response time
2. **Batch processing:** Group inference requests to maximize throughput
3. **Error handling:** Models require harmony format; malformed inputs will fail
4. **Monitoring:** Track classification distribution to detect policy drift
5. **Reasoning outputs:** Store for debugging but never expose to end users

**Detailed guidance:** See [Production Considerations](#8.4) for comprehensive best practices, including latency optimization, batch processing strategies, error handling patterns, and monitoring model reasoning outputs.

Sources: [README.md:27](), [README.md:44-45]()

---

## Community and Support

The gpt-oss-safeguard models are partner models of the [ROOST Model Community](https://roost.tools/) (Robust Open Online Safety Tools). OpenAI is committed to incorporating user feedback and jointly iterating on future releases.

**Engagement channels:**
- **Feedback submission:** [RMC GitHub repository](https://github.com/roostorg/open-models)
- **Usage examples:** [OpenAI Cookbook](https://cookbook.openai.com/articles/gpt-oss-safeguard-guide)
- **Community discussion:** ROOST Model Community forums
- **Model card:** [arXiv paper](https://arxiv.org/abs/2508.10925)

**Integration support:** The cookbook provides detailed prompting guides, sample policies, and inference examples to accelerate integration.

Sources: [README.md:44-45](), [README.md:7-9]()

---

## Quick Reference

```mermaid
graph TB
    Start["Deployment Planning"]
    
    Start --> SelectModel["Select Model Variant<br/>120B: Production, High Reasoning<br/>20B: Low Latency, Local"]
    
    SelectModel --> ProvisionHW["Provision Hardware<br/>120B: Single 80GB GPU H100/MI300X<br/>20B: Lower requirements"]
    
    ProvisionHW --> DownloadModel["Download from Hugging Face<br/>openai/gpt-oss-safeguard-120b<br/>openai/gpt-oss-safeguard-20b"]
    
    DownloadModel --> ConfigFormat["Configure harmony response format<br/>MANDATORY"]
    
    ConfigFormat --> CreatePolicy["Create/Load Policy<br/>example_policies/spam/policy.txt"]
    
    CreatePolicy --> BuildGolden["Build Golden Dataset<br/>golden_dataset.csv"]
    
    BuildGolden --> Validate["Validate Performance<br/>Accuracy, Precision, Recall, F1"]
    
    Validate --> Deploy["Deploy to Production"]
    
    Deploy --> Monitor["Monitor & Audit"]
    
    Monitor --> Iterate["Iterate via ROOST Community"]
    
    Iterate -.-> CreatePolicy
```

**Deployment sequence:** Model selection → hardware provisioning → download → format configuration → policy creation → validation → production deployment → monitoring → community feedback loop.

Sources: [README.md:1-46]()

---

