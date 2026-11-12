<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/personality_in_llms · page 6 Configuration and Experiment Setup · fetched 2026-10-26 -->

# Configuration and Experiment Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [admin_sessions/ablation01_ind_big5_9lvls_50desc_admin_session_rating.json](admin_sessions/ablation01_ind_big5_9lvls_50desc_admin_session_rating.json)
- [admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json](admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json)
- [admin_sessions/prod_run_01_external_rating.json](admin_sessions/prod_run_01_external_rating.json)

</details>



This document provides an overview of the configuration system used to define and manage experiments in the personality traits research framework. It covers the structure of admin session files, experimental design patterns, and how configurations integrate with the inference and analysis pipeline.

For detailed information about admin session file structure and parameters, see [Admin Session Configuration](#6.1). For specific ablation study design patterns, see [Ablation Study Configurations](#6.2).

## Configuration System Overview

The experiment configuration system is built around JSON-based admin session files that define the complete experimental setup including psychological measures, item combinations, and experimental conditions. These configurations serve as the single source of truth for experiment parameters and are consumed by inference scripts and analysis notebooks.

```mermaid
graph TB
    subgraph "Configuration Layer"
        AS1["prod_run_01_external_rating.json<br/>Production Configuration"]
        AS2["ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json<br/>Ablation Study Configuration"]
    end
    
    subgraph "Inference Scripts"
        RHF["run_hf_inference.py"]
        RGP["run_gpt_inference.py"]
        GSU["generate_status_updates.py"]
    end
    
    subgraph "PsyBORGS Framework"
        SBL["survey_bench_lib.py<br/>AdministrationSession"]
        SC["score_calculation.py<br/>Scoring Functions"]
    end
    
    subgraph "Analysis Layer"
        TSA["trait_shaping_analysis_template.ipynb"]
        DTA["downstream_task_analysis_template.ipynb"]
        CVA["construct_validity_analysis_template.ipynb"]
    end
    
    AS1 --> SBL
    AS2 --> SBL
    SBL --> RHF
    SBL --> RGP
    SBL --> GSU
    SBL --> SC
    SC --> TSA
    SC --> DTA
    SC --> CVA
```

**Sources:** [admin_sessions/prod_run_01_external_rating.json](), [admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json]()

## Admin Session File Structure

Admin session files follow a standardized JSON structure with three main components: measures definitions, experimental conditions, and response specifications. The `measures` object contains all psychological instruments used in the study, while additional sections define experimental manipulations and data collection parameters.

| Component | Purpose | Key Fields |
|-----------|---------|------------|
| `measures` | Psychological instrument definitions | `items`, `scales`, `user_readable_name` |
| `items` | Individual test items/questions | Item ID to content mapping |
| `scales` | Scoring subscales | `item_ids`, `reverse_keyed_item_ids`, `item_preamble_ids` |

```mermaid
graph LR
    subgraph "Admin Session JSON"
        M["measures"]
        subgraph "Measure Definition"
            I["items<br/>{item_id: content}"]
            S["scales<br/>{scale_id: config}"]
            U["user_readable_name"]
        end
        subgraph "Scale Configuration"
            II["item_ids[]"]
            RK["reverse_keyed_item_ids[]"]
            IP["item_preamble_ids[]"]
            RS["response_scale_ids[]"]
        end
    end
    
    M --> I
    M --> S
    M --> U
    S --> II
    S --> RK
    S --> IP
    S --> RS
```

**Sources:** [admin_sessions/prod_run_01_external_rating.json:1-50](), [admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json:1-50]()

## Psychological Measures Configuration

The system supports multiple standardized psychological instruments, each with specific item sets and scoring rules. The most commonly used measures include the Big Five Inventory (BFI), IPIP-NEO-300, PANAS, and specialized scales for creativity and aggression.

### Big Five Inventory (BFI) Configuration

```mermaid
graph TB
    subgraph "BFI Measure"
        BFI_ROOT["BFI<br/>user_readable_name: 'Big Five Inventory'"]
        BFI_ITEMS["items<br/>bf1-bf44: '[REDACTED]'"]
        
        subgraph "BFI Scales"
            EXT["BFI-EXT<br/>Extraversion<br/>8 items"]
            AGR["BFI-AGR<br/>Agreeableness<br/>9 items"] 
            CON["BFI-CON<br/>Conscientiousness<br/>9 items"]
            NEU["BFI-NEU<br/>Neuroticism<br/>8 items"]
            OPE["BFI-OPE<br/>Openness<br/>10 items"]
        end
    end
    
    BFI_ROOT --> BFI_ITEMS
    BFI_ROOT --> EXT
    BFI_ROOT --> AGR
    BFI_ROOT --> CON
    BFI_ROOT --> NEU
    BFI_ROOT --> OPE
```

**Sources:** [admin_sessions/prod_run_01_external_rating.json:2-97]()

### IPIP-NEO-300 Configuration

The IPIP-NEO-300 provides a more comprehensive personality assessment with 300 items across five major domains, each containing 60 items with specific reverse-keying patterns.

```mermaid
graph TB
    subgraph "IPIP300 Measure Structure"
        IPIP_ROOT["IPIP300<br/>user_readable_name: 'IPIP-NEO-300'"]
        IPIP_ITEMS["items<br/>ipip1-ipip300"]
        
        subgraph "IPIP300 Scales"
            IPIP_NEU["IPIP300-NEU<br/>60 items<br/>27 reverse-keyed"]
            IPIP_EXT["IPIP300-EXT<br/>60 items<br/>24 reverse-keyed"]
            IPIP_OPE["IPIP300-OPE<br/>60 items<br/>32 reverse-keyed"]
            IPIP_AGR["IPIP300-AGR<br/>60 items<br/>36 reverse-keyed"]
            IPIP_CON["IPIP300-CON<br/>60 items<br/>29 reverse-keyed"]
        end
    end
    
    IPIP_ROOT --> IPIP_ITEMS
    IPIP_ROOT --> IPIP_NEU
    IPIP_ROOT --> IPIP_EXT  
    IPIP_ROOT --> IPIP_OPE
    IPIP_ROOT --> IPIP_AGR
    IPIP_ROOT --> IPIP_CON
```

**Sources:** [admin_sessions/prod_run_01_external_rating.json:99-449](), [admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json:3-448]()

## Experimental Design Patterns

### Factorial Design Configuration

The ablation study configuration demonstrates a factorial experimental design where personality traits are manipulated at different levels. The `item_preamble_ids` encode experimental conditions using a structured naming convention.

```mermaid
graph TB
    subgraph "Factorial Design Structure"
        COND["Experimental Condition<br/>ext1-agr1-con1-neu1-ope1-d1-ev2"]
        
        subgraph "Trait Levels"
            EXT["ext1<br/>Extraversion Level 1"]
            AGR["agr1<br/>Agreeableness Level 1"] 
            CON["con1<br/>Conscientiousness Level 1"]
            NEU["neu1<br/>Neuroticism Level 1"]
            OPE["ope1<br/>Openness Level 1"]
        end
        
        subgraph "Design Parameters"
            DESC["d1-d50<br/>50 Descriptors"]
            EVAL["ev2<br/>Evaluation Method 2"]
        end
    end
    
    COND --> EXT
    COND --> AGR
    COND --> CON
    COND --> NEU
    COND --> OPE
    COND --> DESC
    COND --> EVAL
```

**Sources:** [admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json:401-1400]()

### Multi-Level Trait Manipulation

The system supports manipulation of personality traits at different intensity levels (e.g., `neu1` vs `neu9` for low vs high neuroticism), allowing researchers to study the effects of varying personality trait strengths.

| Trait | Level 1 | Level 9 | 
|-------|---------|---------|
| Extraversion | `ext1` | `ext9` |
| Agreeableness | `agr1` | `agr9` |
| Conscientiousness | `con1` | `con9` |
| Neuroticism | `neu1` | `neu9` |
| Openness | `ope1` | `ope9` |

**Sources:** [admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json:401-1800]()

## Response Scale Configuration

All measures utilize standardized response scales and postamble configurations. The `response_scale_ids` and `response_choice_postamble_ids` fields specify how responses should be collected and processed.

```mermaid
graph LR
    subgraph "Response Configuration"
        SCALE["response_scale_ids<br/>['likert5_numeric']"]
        POST["response_choice_postamble_ids<br/>['none']"]
        ITEM_POST["item_postamble_ids<br/>measure-specific"]
    end
    
    subgraph "Scale Types"
        L5["likert5_numeric<br/>1-5 Likert Scale"]
    end
    
    subgraph "Postamble Types"  
        BFI_POST["plk-bfi-0, plk-bfi-3, etc.<br/>BFI Postambles"]
        IPIP_POST["plk-ipip-0, plk-ipip-3, etc.<br/>IPIP Postambles"]
        PANAS_POST["plk-panas-0, plk-panas-3, etc.<br/>PANAS Postambles"]
    end
    
    SCALE --> L5
    ITEM_POST --> BFI_POST
    ITEM_POST --> IPIP_POST
    ITEM_POST --> PANAS_POST
```

**Sources:** [admin_sessions/prod_run_01_external_rating.json:57-59](), [admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json:1748-1750]()

## Integration with Inference Pipeline

Admin session configurations are loaded by the PsyBORGS framework and used to generate inference payloads for different model backends. The configuration system ensures consistent experimental conditions across all inference runs.

```mermaid
sequenceDiagram
    participant AC as "Admin Config JSON"
    participant AS as "AdministrationSession"
    participant PS as "PayloadSpec"
    participant IS as "Inference Script"
    participant LLM as "Language Model"
    
    AC->>AS: "Load configuration"
    AS->>PS: "Generate payload specs"
    PS->>IS: "Create inference batches"
    IS->>LLM: "Execute inference"
    LLM->>IS: "Return responses"
    IS->>AS: "Store results with config metadata"
```

**Sources:** [admin_sessions/prod_run_01_external_rating.json](), [admin_sessions/ablation_03_conc_big5_2lvls_50desc_admin_session_rating.json]()

---

