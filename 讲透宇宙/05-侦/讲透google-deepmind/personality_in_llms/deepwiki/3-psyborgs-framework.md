<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/personality_in_llms · page 3 PsyBORGS Framework · fetched 2026-10-26 -->

# PsyBORGS Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [psyborgs/__init__.py](psyborgs/__init__.py)
- [psyborgs/score_calculation.py](psyborgs/score_calculation.py)
- [psyborgs/survey_bench_lib.py](psyborgs/survey_bench_lib.py)

</details>



## Purpose and Scope

The PsyBORGS Framework is the core psychometric testing system that enables systematic administration of personality assessments to Large Language Models. This framework provides the foundational data structures, survey administration logic, and scoring mechanisms that underpin the entire personality research pipeline.

This page covers the framework's architecture, core data structures, and administration workflow. For detailed implementation of the survey administration library, see [Survey Administration Library](#3.1). For scoring algorithms and psychometric analysis functions, see [Score Calculation and Psychometric Analysis](#3.2). For testing and validation procedures, see [Testing and Validation](#3.3).

## Framework Architecture

The PsyBORGS Framework operates as the central orchestration layer between survey configuration and LLM inference systems. It transforms human-readable survey specifications into structured prompts and continuations that can be systematically administered to language models.

```mermaid
graph TB
    subgraph "Configuration Layer"
        AS["AdministrationSession"]
        MS["MeasureSpecification"]
        RS["ResponseScale"]
    end
    
    subgraph "Survey Administration Library"
        SBL["survey_bench_lib.py"]
        LAS["load_admin_session()"]
        MGR["measure_generator()"]
        PGR["prompt_generator()"]
        CGR["continuation_generator()"]
    end
    
    subgraph "Payload Generation"
        P["Prompt"]
        C["Continuation"]
        PS["PayloadSpec"]
        AP["assemble_payload()"]
    end
    
    subgraph "Inference Interface"
        ASP["assemble_and_score_payload()"]
        CLSF["create_llm_scoring_fns_dict()"]
    end
    
    subgraph "Score Calculation"
        SC["score_calculation.py"]
        NRLP["normalize_response_logprobs()"]
        CHSR["calculate_human_simulated_responses()"]
        SS["score_session()"]
    end
    
    AS --> SBL
    MS --> SBL
    RS --> SBL
    
    SBL --> LAS
    LAS --> MGR
    MGR --> PGR
    MGR --> CGR
    
    PGR --> P
    CGR --> C
    P --> AP
    C --> AP
    AP --> PS
    
    PS --> ASP
    ASP --> CLSF
    
    ASP --> SC
    SC --> NRLP
    SC --> CHSR
    SC --> SS
```

**Sources:** [psyborgs/survey_bench_lib.py:1-435](), [psyborgs/score_calculation.py:1-251]()

## Core Data Structures

The framework is built around a hierarchy of immutable dataclasses that represent survey configurations, individual test items, and response specifications. These structures ensure reproducible and traceable survey administration.

```mermaid
classDiagram
    class AdministrationSession {
        +Dict[str, MeasureSpecification] measures
        +Dict[str, str] item_preambles
        +Dict[str, str] item_postambles
        +Dict[str, ResponseScale] response_scales
        +Dict[str, str] response_choice_postambles
        +Dict[str, ModelSpec] models
        +n_measures: int
    }
    
    class MeasureSpecification {
        +str user_readable_name
        +Dict[str, str] items
        +Dict[str, Scale] scales
    }
    
    class Scale {
        +str user_readable_name
        +List[str] item_ids
        +List[str] reverse_keyed_item_ids
        +List[str] item_preamble_ids
        +List[str] item_postamble_ids
        +List[str] response_scale_ids
        +List[str] response_choice_postamble_ids
    }
    
    class ResponseScale {
        +str user_readable_name
        +Dict[str, str] response_choices
    }
    
    class ModelSpec {
        +str user_readable_name
        +ModelFamily model_family
        +Optional[str] model_endpoint
    }
    
    class Prompt {
        +NamedEntry preamble
        +NamedEntry item
        +NamedEntry postamble
        +payload: str
    }
    
    class Continuation {
        +int response_value
        +str response_scale_id
        +NamedEntry response_choice
        +NamedEntry response_choice_postamble
        +payload: str
    }
    
    class PayloadSpec {
        +str prompt_text
        +str continuation_text
        +float score
        +str measure_id
        +str scale_id
        +str item_id
        +int response_value
        +str model_id
    }
    
    AdministrationSession --> MeasureSpecification
    AdministrationSession --> ResponseScale
    AdministrationSession --> ModelSpec
    MeasureSpecification --> Scale
    Scale --> Prompt
    Scale --> Continuation
    Prompt --> PayloadSpec
    Continuation --> PayloadSpec
```

**Sources:** [psyborgs/survey_bench_lib.py:39-87](), [psyborgs/survey_bench_lib.py:96-151]()

## Survey Administration Workflow

The framework implements a systematic workflow that transforms survey configurations into scored responses through iterative payload generation and LLM scoring. This process ensures comprehensive coverage of all survey items across different framing conditions.

```mermaid
flowchart TD
    subgraph "Initialization"
        JSON["Admin Session JSON"]
        LAS["load_admin_session()"]
        CLSF["create_llm_scoring_fns_dict()"]
    end
    
    subgraph "Iterator Generation"
        MGR["measure_generator()"]
        PGR["prompt_generator()"]
        CGR["continuation_generator()"]
    end
    
    subgraph "Payload Assembly"
        M["Measure Object"]
        P["Prompt Object"]  
        C["Continuation Object"]
        AP["assemble_payload()"]
        ASAP["assemble_and_score_payload()"]
    end
    
    subgraph "Scoring Pipeline"
        RAWDF["Raw Response Scores DataFrame"]
        GRSR["get_raw_and_simulated_responses()"]
        SS["score_session()"]
        SCOREDDF["Scored Session DataFrame"]
    end
    
    JSON --> LAS
    LAS --> CLSF
    LAS --> MGR
    
    MGR --> PGR
    MGR --> CGR
    
    PGR --> P
    CGR --> C
    MGR --> M
    
    M --> ASAP
    P --> ASAP
    C --> ASAP
    P --> AP
    C --> AP
    AP --> ASAP
    
    ASAP --> RAWDF
    RAWDF --> GRSR
    GRSR --> SS
    SS --> SCOREDDF
```

**Sources:** [psyborgs/survey_bench_lib.py:153-168](), [psyborgs/survey_bench_lib.py:352-434](), [psyborgs/score_calculation.py:150-251]()

## Response Processing Pipeline

The framework implements a sophisticated response processing pipeline that converts raw LLM scores into normalized probabilities and human-simulated responses. This enables both fine-grained analysis of response patterns and traditional psychometric scoring.

```mermaid
graph LR
    subgraph "Input Processing"
        RRS["Raw Response Scores"]
        GM["Generative Mode Check"]
        NRLP["normalize_response_logprobs()"]
    end
    
    subgraph "Response Reshaping"
        RRCPS["reshape_response_choice_probability_scores()"]
        CHSR["calculate_human_simulated_responses()"]
        WIDE["Wide Format DataFrame"]
    end
    
    subgraph "Scale Scoring"
        ITEMS["Item Values"]
        RK["Reverse Keying"]
        AVG["Average Calculation"]
        SCALES["Scale Scores"]
    end
    
    RRS --> GM
    GM -->|"generative_mode=True"| NRLP
    GM -->|"generative_mode=False"| RRCPS
    NRLP --> RRCPS
    
    RRS --> CHSR
    RRCPS --> WIDE
    CHSR --> WIDE
    
    WIDE --> ITEMS
    ITEMS --> RK
    RK --> AVG
    AVG --> SCALES
```

**Sources:** [psyborgs/score_calculation.py:26-58](), [psyborgs/score_calculation.py:61-96](), [psyborgs/score_calculation.py:98-147](), [psyborgs/score_calculation.py:179-251]()

## Integration Points

The PsyBORGS Framework serves as the central coordination layer that interfaces with multiple system components. It standardizes survey administration while remaining agnostic to specific LLM backends or analysis methods.

| Component | Interface | Purpose |
|-----------|-----------|---------|
| **Inference Systems** | `model_scoring_fn` callbacks | Abstracts LLM scoring implementations |
| **Configuration Files** | `load_admin_session()` | Loads JSON admin session specifications |
| **Analysis Templates** | Scored DataFrames | Provides structured data for downstream analysis |
| **Validation Systems** | PayloadSpec objects | Enables reproducible experiment tracking |

The framework's design ensures that survey configurations remain portable across different LLM backends while maintaining strict control over prompt construction and response interpretation. This separation of concerns enables researchers to focus on psychometric validity without being constrained by implementation details of specific language models.

**Sources:** [psyborgs/survey_bench_lib.py:179-196](), [psyborgs/survey_bench_lib.py:280-304](), [psyborgs/score_calculation.py:179-204]()

---

