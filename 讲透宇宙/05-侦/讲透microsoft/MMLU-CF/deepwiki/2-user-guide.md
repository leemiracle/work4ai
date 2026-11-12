<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/MMLU-CF · page 2 User Guide · fetched 2026-10-26 -->

# User Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides complete instructions for evaluating language models using the MMLU-CF benchmark system. It covers the step-by-step process for obtaining both validation and test set results, including the different pathways for Hugging Face models versus API models.

For information about the technical architecture and data construction process, see [System Architecture](#3). For details about contamination prevention mechanisms, see [Contamination Prevention](#3.2).

## Overview

MMLU-CF provides a two-tier evaluation system designed to prevent data contamination while enabling reliable model assessment:

- **Validation Set**: 10,000 open-source questions available via Hugging Face for initial model testing
- **Test Set**: 10,000 closed-source questions accessible only through controlled request processes

The system supports two distinct evaluation pathways depending on your model type and deployment method.

## Evaluation Pathways

### User Evaluation Workflow

```mermaid
flowchart TD
    A["User"] --> B["Choose Model Type"]
    B --> C["Hugging Face Model"]
    B --> D["API Model"]
    
    C --> E["Run OpenCompass"]
    E --> F["Get Validation Results"]
    F --> G["Submit GitHub Issue"]
    G --> H["Receive Test Results<br/>(1-2 weeks)"]
    
    D --> I["Run OpenCompass<br/>(if supported)"]
    I --> J["Get Validation Results"]
    J --> K["Email API Key"]
    K --> L["Receive Test Results"]
    
    style C fill:#e3f2fd
    style D fill:#fff3e0
    style H fill:#e8f5e8
    style L fill:#e8f5e8
```

Sources: [README.md:36-73]()

### Model Type Decision Matrix

| Model Type | Access Method | Validation Process | Test Access Method | Timeline |
|------------|---------------|-------------------|-------------------|----------|
| Hugging Face Models | `hf_model_name` | OpenCompass automated | GitHub Issues | 1-2 weeks |
| API Models | API endpoints | OpenCompass (if supported) | Email process | Variable |

Sources: [README.md:38-72]()

## Hugging Face Model Evaluation

### Step 1: Validation Set Evaluation

Use OpenCompass to evaluate your model against the validation set. The system automatically loads the dataset from `microsoft/MMLU-CF` on Hugging Face.

#### 5-Shot Evaluation
```bash
opencompass --models hf_internlm2_5_1_8b_chat --datasets mmlu_cf_few_shot --summarizer mmlu_cf
```

#### 0-Shot Evaluation  
```bash
opencompass --models hf_internlm2_5_1_8b_chat --datasets mmlu_cf_zero_shot --summarizer mmlu_cf
```

#### OpenCompass Integration Components

```mermaid
graph LR
    A["opencompass"] --> B["--models"]
    A --> C["--datasets"] 
    A --> D["--summarizer"]
    
    B --> E["hf_model_name"]
    C --> F["mmlu_cf_few_shot"]
    C --> G["mmlu_cf_zero_shot"]
    D --> H["mmlu_cf"]
    
    E --> I["Hugging Face Model Loading"]
    F --> J["5-shot Evaluation Config"]
    G --> K["0-shot Evaluation Config"]
    H --> L["MMLU-CF Result Summarization"]
    
    I --> M["microsoft/MMLU-CF Dataset"]
    J --> M
    K --> M
```

Sources: [README.md:40-52]()

### Step 2: Test Set Access Request

Submit a GitHub issue following the exact format requirements to request test set evaluation.

#### Required GitHub Issue Format

**Title Format:**
```
Test set evaluation Request - add HF model [model_name]
```

**Content Format:**
```
The result on validation set: X.X%
```

#### GitHub Issue Workflow

```mermaid
sequenceDiagram
    participant U as "User"
    participant GH as "GitHub Issues"
    participant M as "Maintainers"
    participant TS as "Test Set Evaluation"
    
    U->>GH: "Submit formatted issue"
    Note over U,GH: Title: Test set evaluation Request - add HF model [model_name]<br/>Content: The result on validation set: X.X%
    
    GH->>M: "Issue notification"
    M->>TS: "Trigger automated evaluation"
    TS->>M: "Return test results"
    M->>U: "Provide results (1-2 weeks)"
```

Sources: [README.md:54-71]()

#### Format Requirements

| Component | Requirement | Example |
|-----------|-------------|---------|
| Title | Use square brackets `[ ]` | `[microsoft/phi-4]` |
| Model Name | Exact Hugging Face identifier | `microsoft/phi-4` |
| Validation Result | Percentage format | `68.5%` |
| Timeline | Expect 1-2 weeks | Depends on evaluation queue |

Sources: [README.md:68-71]()

## API Model Evaluation

For API-based models (GPT-4o, Gemini, Claude), the evaluation process differs based on OpenCompass support availability.

### API Model Workflow

```mermaid
flowchart TD
    A["API Model"] --> B["Check OpenCompass Support"]
    B --> C["Supported"]
    B --> D["Not Supported"]
    
    C --> E["Run OpenCompass Validation"]
    E --> F["Get Validation Results"]
    F --> G["Email API Key"]
    G --> H["yangyu.huang@microsoft.com"]
    H --> I["Receive Test Results"]
    
    D --> J["Manual Validation"]
    J --> K["Contact Maintainers"]
    K --> L["Custom Evaluation Process"]
```

Sources: [README.md:72]()

### Email Process Requirements

| Component | Details |
|-----------|---------|
| Recipient | `yangyu.huang@microsoft.com` |
| Required | Validation set results |
| Required | Temporary API key |
| Purpose | Test set evaluation access |

Sources: [README.md:72]()

## Access Control Mechanisms

### Test Set Protection System

```mermaid
graph TD
    A["Test Set (10K questions)"] --> B["Closed Source Storage"]
    B --> C["Access Control Layer"]
    C --> D["GitHub Issues Gateway"]
    C --> E["Email Gateway"]
    
    D --> F["HF Model Requests"]
    E --> G["API Model Requests"]
    
    F --> H["Automated Validation"]
    G --> I["Manual Review"]
    
    H --> J["Maintainer Approval"]
    I --> J
    J --> K["Test Evaluation"]
    
    style A fill:#ffcdd2
    style B fill:#ffcdd2
    style C fill:#fff3e0
    style K fill:#e8f5e8
```

Sources: [README.md:76](), based on system architecture

### Validation vs Test Set Comparison

| Aspect | Validation Set | Test Set |
|--------|----------------|----------|
| Access | Open source via Hugging Face | Controlled access only |
| Size | 10,000 questions | 10,000 questions |
| Purpose | Initial model testing | Final evaluation |
| Automation | Fully automated | Request-based |
| Contamination Risk | Managed through guidelines | Prevented through access control |

Sources: [README.md:25-29](), [README.md:76]()

## Expected Results and Timeline

### Performance Expectations

The leaderboard shows typical performance gaps between MMLU and MMLU-CF, indicating the contamination-free nature of the benchmark:

| Model Category | MMLU Range | MMLU-CF Range | Typical Gap |
|----------------|------------|---------------|-------------|
| API Models | 71.4-88.0% | 58.2-73.4% | 10-15% lower |
| Large Models | 68.9-86.3% | 52.2-71.6% | 10-15% lower |
| Medium Models | 55.7-84.8% | 48.3-69.7% | 10-15% lower |

Sources: [README.md:86-595]()

### Timeline Expectations

| Process Stage | Timeline | Dependencies |
|---------------|----------|-------------|
| Validation Evaluation | Minutes-Hours | OpenCompass setup |
| GitHub Issue Submission | Immediate | Proper formatting |
| Test Result Delivery | 1-2 weeks | Evaluation queue |
| API Model Processing | Variable | Manual coordination |

Sources: [README.md:70]()

## Troubleshooting

### Common Issues

| Issue | Solution | Reference |
|-------|----------|-----------|
| OpenCompass command fails | Check model name format | Use exact HF identifier |
| GitHub issue rejected | Verify format requirements | Use square brackets `[ ]` |
| Missing validation results | Re-run OpenCompass evaluation | Ensure dataset loads correctly |
| Extended wait times | Contact maintainers | Check evaluation queue status |

### Contact Information

For technical issues or inquiries:
- **Primary Contact**: Qihao Zhao (`qhzhaoo@gmail.com`)
- **API Model Issues**: Yangyu Huang (`yanghuan@microsoft.com`)

Sources: [README.md:602]()

---

