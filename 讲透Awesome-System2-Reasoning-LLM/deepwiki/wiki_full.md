# Page: Home

# Home

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This wiki documents the **Awesome-System2-Reasoning-LLM** repository, a curated research catalog tracking the evolution of reasoning capabilities in Large Language Models (LLMs), specifically the transition from System 1 (fast, intuitive) to System 2 (slow, deliberate) thinking. The repository serves as a comprehensive knowledge base for researchers and practitioners seeking to understand, implement, or extend advanced reasoning systems like OpenAI's o1, DeepSeek-R1, and similar models.

The documentation covers:
- The 12-part taxonomy of reasoning research (detailed in [Research Landscape Overview](#3))
- Technical methodologies including Process Reward Models, Reinforcement Learning, MCTS, Self-Training, and Reflection (see [Core Methodologies](#4))
- Repository architecture, data structures, and build system (see [Repository Structure and Maintenance](#10))
- Practical guidance for navigating and using the resource (see [Using This Resource](#11))

This wiki is maintained alongside the survey paper "From System 1 to System 2: A Survey of Reasoning Large Language Models" ([README.md:11]()).

**Sources:** [README.md:1-19]()

---

## Repository Architecture Overview

The repository uses a hybrid documentation approach combining automated data processing with expert curation. The architecture prioritizes human-readable organization while maintaining machine-processable metadata.

```mermaid
graph TB
    subgraph "Primary Interface"
        README["README.md<br/>(80.82% importance)<br/>Lines 1-509"]
        TOC["Table of Contents<br/>12 Research Parts<br/>Lines 29-43"]
        UPDATES["Updates Section<br/>Lines 9-11"]
        CITATION["Citation Block<br/>Lines 485-497"]
    end
    
    subgraph "Data Layer"
        JSON["assets/paper.json<br/>Structured metadata<br/>~256 papers<br/>12 categories"]
        BUILDER["src/main.py<br/>Markdown generator<br/>PaperInformation class"]
        TABLE["src/table.md<br/>Tabular view"]
        LIST["src/list.md<br/>List with badges"]
    end
    
    subgraph "Visual Assets"
        DEVIMG["assets/develope.jpg<br/>Referenced at line 21"]
        TIMELINE["assets/timeline_2.png<br/>Referenced at line 25"]
    end
    
    README --> TOC
    README --> UPDATES
    README --> CITATION
    TOC --> Part1["Part 1: O1 Replication<br/>Lines 45-67"]
    TOC --> Part2["Part 2: Process Reward Models<br/>Lines 68-96"]
    TOC --> Part3["Part 3: Reinforcement Learning<br/>Lines 98-137"]
    TOC --> Part4["Part 4: MCTS/Tree Search<br/>Lines 139-193"]
    TOC --> Part5["Part 5: Self-Training<br/>Lines 194-224"]
    TOC --> Part6["Part 6: Reflection<br/>Lines 225-241"]
    TOC --> Part7["Part 7: Efficient System2<br/>Lines 242-325"]
    TOC --> Part8["Part 8: Explainability<br/>Lines 327-338"]
    TOC --> Part9["Part 9: Multimodal Agents<br/>Lines 339-350"]
    TOC --> Part10["Part 10: Benchmarks<br/>Lines 351-433"]
    TOC --> Part11["Part 11: Safety<br/>Lines 437-453"]
    TOC --> Part12["Part 12: R1 Multimodal<br/>Lines 455-481"]
    
    JSON -.informs.-> README
    JSON --> BUILDER
    BUILDER --> TABLE
    BUILDER --> LIST
    
    README -.references.-> DEVIMG
    README -.references.-> TIMELINE
```

**Key Components:**

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| Main Documentation | `README.md` | 1-509 | Primary user interface with rich descriptions |
| Paper Metadata | `assets/paper.json` | N/A | Structured data for ~256 papers across 12 categories |
| Build Script | `src/main.py` | N/A | Processes JSON into `PaperInformation` objects |
| Table Format | `src/table.md` | N/A | Machine-generated tabular view sorted by date |
| List Format | `src/list.md` | N/A | Machine-generated list view with arXiv/venue badges |
| Development Timeline | `assets/develope.jpg` | N/A | Visual progression of AI systems |
| Research Timeline | `assets/timeline_2.png` | N/A | Temporal map of reasoning LLM research |

**Sources:** [README.md:1-509]()

---

## The 12-Part Research Framework

The repository organizes research into 12 interconnected parts, forming a comprehensive taxonomy of System 2 reasoning approaches. Each part is documented in detail in subsequent wiki pages.

```mermaid
graph TB
    subgraph "Core Methodologies (Parts 1-6)"
        P1["Part 1: O1 Replication<br/>Lines 45-67<br/>Target Architecture<br/>OpenAI o1, DeepSeek-R1"]
        P2["Part 2: Process Reward Models<br/>Lines 68-96<br/>Step-wise Supervision<br/>Math-Shepherd, PRMBench"]
        P3["Part 3: Reinforcement Learning<br/>Lines 98-137<br/>Policy Optimization<br/>PPO, DPO, GRPO"]
        P4["Part 4: MCTS/Tree Search<br/>Lines 139-193<br/>Exploration & Planning<br/>ReST-MCTS*, rStar-Math"]
        P5["Part 5: Self-Training<br/>Lines 194-224<br/>Bootstrapping<br/>STaR, ReST, V-star"]
        P6["Part 6: Reflection<br/>Lines 225-241<br/>Self-Correction<br/>Self-Refine, CRITIC"]
    end
    
    subgraph "Optimization & Understanding (Parts 7-8)"
        P7["Part 7: Efficient System2<br/>Lines 242-325<br/>Computational Optimization<br/>DynaThink, O1-Pruner"]
        P8["Part 8: Explainability<br/>Lines 327-338<br/>Mechanism Understanding<br/>Layer Analysis, Gradients"]
    end
    
    subgraph "Extensions (Parts 9, 12)"
        P9["Part 9: Multimodal Agents<br/>Lines 339-350<br/>Slow-Fast Systems<br/>AtomThink, LLaVA-o1"]
        P12["Part 12: R1 Multimodal<br/>Lines 455-481<br/>Vision-Language Reasoning<br/>MedVLM-R1, Virgo"]
    end
    
    subgraph "Evaluation & Safety (Parts 10-11)"
        P10["Part 10: Benchmarks<br/>Lines 351-433<br/>Evaluation Framework<br/>PRMBench, FrontierMath"]
        P11["Part 11: Safety<br/>Lines 437-453<br/>Alignment & Attacks<br/>H-CoT, SafeChain"]
    end
    
    P1 -.synthesizes.-> P2
    P1 -.synthesizes.-> P3
    P1 -.synthesizes.-> P4
    P1 -.synthesizes.-> P5
    P1 -.synthesizes.-> P6
    
    P2 --> P3
    P2 --> P4
    P2 --> P5
    
    P3 --> P5
    P4 --> P5
    
    P7 -.optimizes.-> P1
    P7 -.optimizes.-> P4
    P7 -.optimizes.-> P5
    
    P8 -.analyzes.-> P1
    P8 -.analyzes.-> P3
    
    P1 --> P9
    P1 --> P12
    
    P10 -.evaluates.-> P1
    P10 -.evaluates.-> P2
    P10 -.evaluates.-> P9
    
    P11 -.secures.-> P1
    P11 -.secures.-> P3
```

**Framework Details:**

Each part represents a cluster of research papers organized thematically. For detailed coverage:
- **Core Methodologies**: See [Core Methodologies](#4) and individual pages [4.1](#4.1) through [4.6](#4.6)
- **Optimization**: See [Optimization and Understanding](#5), pages [5.1](#5.1) and [5.2](#5.2)
- **Extensions**: See [Multimodal Extensions](#6), pages [6.1](#6.1) and [6.2](#6.2)
- **Infrastructure**: See [Evaluation and Safety](#7), pages [7.1](#7.1) and [7.2](#7.2)

**Sources:** [README.md:29-43](), [README.md:45-481]()

---

## System 1 to System 2 Transition

The repository's central theme is the progression from fast, intuitive reasoning (System 1) to slow, deliberate reasoning (System 2). This conceptual framework, introduced in the survey paper, structures all research categorization.

```mermaid
graph LR
    S1["System 1 Thinking<br/>README.md:18<br/>Fast, Intuitive<br/>Base LLM Capabilities"]
    
    TRAIN["Training-Time Enhancements<br/>Parts 2, 3, 5<br/>Process Rewards<br/>Reinforcement Learning<br/>Self-Training"]
    
    INFER["Inference-Time Techniques<br/>Parts 4, 6<br/>MCTS/Tree Search<br/>Reflection<br/>Verification"]
    
    S2["System 2 Thinking<br/>README.md:18<br/>Slow, Deliberate<br/>Expert-level Reasoning"]
    
    O1["O1-like Systems<br/>Part 1: Lines 45-67<br/>Integrated Architecture<br/>OpenAI o1<br/>DeepSeek-R1<br/>Kimi k1.5"]
    
    S1 --> TRAIN
    TRAIN --> S2
    S1 --> INFER
    INFER --> S2
    S2 --> O1
    
    TRAIN -.combined in.-> O1
    INFER -.combined in.-> O1
```

**Key Systems Referenced:**

| System | Paper Location | Description |
|--------|---------------|-------------|
| OpenAI o1 | [README.md:18]() | Expert-level reasoning in math/coding |
| DeepSeek-R1 | [README.md:107]() | RL-based reasoning at scale |
| Kimi k1.5 | [README.md:108]() | Scaled reinforcement learning reasoning |
| rStar-Math | [README.md:188](), [README.md:220]() | Self-evolved deep thinking for small LLMs |

**Sources:** [README.md:14-18]()

---

## Build System Architecture

The repository uses `src/main.py` to process structured metadata from `assets/paper.json` into alternative documentation views. This system enables programmatic access while maintaining human-curated primary documentation.

```mermaid
graph TB
    subgraph "Input: assets/paper.json"
        JSON_DATA["JSON Structure<br/>Categories: 12 parts<br/>Papers: ~256 entries<br/>Fields: title, venue, date, link"]
    end
    
    subgraph "Processing: src/main.py"
        LOAD["Load JSON<br/>Parse structure"]
        EXTRACT["Extract Papers<br/>Create PaperInformation objects<br/>Flatten hierarchy"]
        RESOLVE["Resolve References<br/>Handle label-based links<br/>Deduplicate entries"]
        DICT["Processed Dictionary<br/>Key: paper ID<br/>Value: PaperInformation"]
    end
    
    subgraph "Output Formats"
        TABLE_OUT["src/table.md<br/>Tabular layout<br/>Columns: Title, Venue, Date<br/>Sorted by publication date"]
        LIST_OUT["src/list.md<br/>List format<br/>arXiv badges<br/>Venue indicators<br/>Category grouping"]
    end
    
    JSON_DATA --> LOAD
    LOAD --> EXTRACT
    EXTRACT --> RESOLVE
    RESOLVE --> DICT
    DICT --> TABLE_OUT
    DICT --> LIST_OUT
```

**Data Flow:**

1. **Input Phase**: `assets/paper.json` stores structured metadata with hierarchical organization matching the 12-part framework
2. **Processing Phase**: `src/main.py` implements a three-stage pipeline:
   - Load and parse JSON structure
   - Extract individual `PaperInformation` objects
   - Resolve cross-references and deduplicate
3. **Output Phase**: Generate two alternative views:
   - `src/table.md`: Chronologically sorted tabular format
   - `src/list.md`: Category-grouped list with badges

**Note**: The primary interface `README.md` remains hand-curated to provide rich context, expert commentary, and conceptual organization that automated generation cannot replicate.

**Sources:** Based on architecture analysis, not directly coded in provided files

---

## Navigation Patterns

The repository supports multiple access patterns for different use cases:

### By Research Category (Thematic)

Browse research organized by methodology through the 12-part structure in [README.md:29-43](). Each part groups related papers with common technical approaches.

**Example**: To find papers on Process Reward Models:
- Navigate to [README.md:68-96]()
- See papers like Math-Shepherd, AutoPSV, PRMBench
- Cross-reference with Part 4 (MCTS) for ReST-MCTS* which combines techniques

### By Timeline (Chronological)

View research evolution through visual timelines:
- [assets/develope.jpg]() referenced at [README.md:21](): High-level progression of AI systems
- [assets/timeline_2.png]() referenced at [README.md:25](): Detailed timeline of reasoning LLMs with core methods and reproduction projects

### By Paper Properties (Structured)

Access machine-readable formats for programmatic filtering:
- `src/table.md`: Sort by publication date, venue, or title
- `src/list.md`: Filter by arXiv vs. conference papers, badge type

### Cross-Cutting Concerns

Some papers appear in multiple parts due to integrated approaches:
- **ReST-MCTS*** ([README.md:78](), [README.md:175](), [README.md:212]()): Appears in Parts 2 (Process Rewards), 4 (MCTS), and 5 (Self-Training)
- **Marco-o1** ([README.md:49](), [README.md:172](), [README.md:234]()): Appears in Parts 1 (O1 Replication), 4 (MCTS), and 6 (Reflection)
- **Virgo** ([README.md:61](), [README.md:348]()): Appears in Parts 1 (O1 Replication) and 9 (Multimodal Agents)

**Sources:** [README.md:1-509]()

---

## Key Research Inflection Points

The repository tracks major breakthroughs that shaped the field:

| Year | Milestone | Location | Impact |
|------|-----------|----------|--------|
| 2017 | Expert Iteration | [README.md:196]() | Foundation: Tree search + deep learning |
| 2022 | STaR (Bootstrapping) | [README.md:197]() | Self-training emergence |
| 2023 | Let's Verify Step by Step | [README.md:75]() | Process reward breakthrough |
| 2023 | AlphaZero-like Tree Search | [README.md:144-145]() | MCTS for LLMs |
| 2024 | Math-Shepherd | [README.md:73]() | Automated process supervision |
| 2024 | ReST-MCTS* | [README.md:78]() | Process rewards + tree search integration |
| 2025 | DeepSeek-R1 | [README.md:107]() | RL at production scale |
| 2025 | Kimi k1.5 | [README.md:108]() | Scaled RL reasoning |
| 2025 | rStar-Math | [README.md:188]() | Self-evolved deep thinking for small models |

These milestones are distributed across the 12 parts and detailed in [Research Timeline and Evolution](#9).

**Sources:** [README.md:45-481]()

---

## Updates and Maintenance

The repository actively tracks the rapidly evolving field. Current status:

**Latest Update**: February 2025 ([README.md:11]())
- Survey paper released: "From System 1 to System 2: A Survey of Reasoning Large Language Models"
- arXiv: [2502.17419](http://arxiv.org/abs/2502.17419)

**Contribution Process**:
- Pull requests welcome ([README.md:6]())
- Repository maintained at: https://github.com/zzli2022/Awesome-System2-Reasoning-LLM

**Maintenance Indicators**:
- Badge: "Maintained? yes" ([README.md:4]())
- Last commit tracking ([README.md:5]())
- Active star history ([README.md:500-508]())

**Sources:** [README.md:4-11]()

---

## Citation Information

To cite this work:

```bibtex
@misc{li202512surveyreasoning,
      title={From System 1 to System 2: A Survey of Reasoning Large Language Models}, 
      author={Zhong-Zhi Li and Duzhen Zhang and Ming-Liang Zhang and Jiaxin Zhang and 
              Zengyan Liu and Yuxuan Yao and Haotian Xu and Junhao Zheng and Pei-Jie Wang and 
              Xiuyi Chen and Yingying Zhang and Fei Yin and Jiahua Dong and Zhijiang Guo and 
              Le Song and Cheng-Lin Liu},
      year={2025},
      eprint={2502.17419},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2502.17419}, 
}
```

**Sources:** [README.md:485-497]()

---

## Related Wiki Pages

For detailed information on specific topics:

- **System 1 vs System 2 Concepts**: See [System 1 vs System 2 Reasoning](#2)
- **12-Part Overview**: See [Research Landscape Overview](#3)
- **Specific Methodologies**: 
  - O1 Replication: [4.1](#4.1)
  - Process Reward Models: [4.2](#4.2)
  - Reinforcement Learning: [4.3](#4.3)
  - MCTS/Tree Search: [4.4](#4.4)
  - Self-Training: [4.5](#4.5)
  - Reflection: [4.6](#4.6)
- **Cross-Cutting Topics**:
  - Efficient System2: [5.1](#5.1)
  - Explainability: [5.2](#5.2)
- **Domain Extensions**:
  - Multimodal Agents: [6.1](#6.1)
  - R1-Driven Multimodal: [6.2](#6.2)
- **Infrastructure**:
  - Benchmarks: [7.1](#7.1)
  - Safety: [7.2](#7.2)
- **Advanced Topics**:
  - Technical Integration Patterns: [8](#8)
  - Research Timeline: [9](#9)
  - Build System Details: [10](#10)
  - Usage Guide: [11](#11)

---

# Page: System 1 vs System 2 Reasoning

# System 1 vs System 2 Reasoning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/list.md](src/list.md)

</details>



## Purpose and Scope

This page explains the fundamental distinction between System 1 (fast, intuitive) and System 2 (slow, deliberate) reasoning in the context of Large Language Models. It defines the theoretical foundation that organizes all research tracked in this repository and clarifies what it means for an LLM to transition from instinctive pattern matching to deliberate multi-step reasoning.

For detailed coverage of the 12 research methodologies that enable this transition, see [Research Landscape Overview](#3). For specific techniques like MCTS, process rewards, and reinforcement learning, see [Core Methodologies](#4).

**Sources:** [README.md:14-18]()

---

## Dual-Process Theory Background

The System 1 / System 2 framework originates from cognitive psychology (Kahneman's "Thinking, Fast and Slow") and describes two modes of human cognition:

| Aspect | System 1 | System 2 |
|--------|----------|----------|
| **Speed** | Fast, automatic | Slow, effortful |
| **Control** | Unconscious, instinctive | Conscious, deliberate |
| **Capacity** | Parallel processing | Sequential processing |
| **Error Rate** | Higher (relies on heuristics) | Lower (systematic reasoning) |
| **Examples** | Pattern recognition, intuition | Mathematical proofs, planning |

In LLMs, this distinction maps to:
- **System 1**: Standard autoregressive generation, single-pass inference
- **System 2**: Multi-step reasoning with verification, tree search, reflection

**Sources:** [README.md:18]()

---

## System 1 Characteristics in LLMs

### Diagram: System 1 Generation Pipeline

```mermaid
graph LR
    Input["User Query"] --> Tokenizer["Tokenization"]
    Tokenizer --> Forward["Forward Pass<br/>(Single Inference)"]
    Forward --> Sampling["Token Sampling<br/>(greedy/temperature)"]
    Sampling --> Output["Direct Output"]
    
    Forward -.relies on.-> Weights["Pretrained Weights<br/>(Learned Patterns)"]
    
    style Input fill:#f9f9f9
    style Output fill:#f9f9f9
```

### Technical Properties

System 1 reasoning in LLMs manifests through:

1. **Autoregressive Generation**: Sequential token prediction without lookahead
   - Standard `next_token = model(context)` inference
   - No backtracking or revision mechanisms
   - Output determined by learned probability distributions

2. **Single-Pass Processing**: 
   - One forward pass through the network
   - No intermediate verification steps
   - Fast but error-prone on complex tasks

3. **Pattern Matching**:
   - Relies on memorized templates from pretraining/fine-tuning
   - Strong on familiar task distributions
   - Struggles with novel combinations or multi-step logic

4. **Implicit Reasoning**:
   - Chain-of-thought may be present but not systematically verified
   - Reasoning happens "in the weights" rather than explicit computation

### Repository Coverage

The baseline System 1 capabilities are implicit in all papers as the starting point. Explicit discussions appear in:
- **Part 8: Explainability** - comparing fast vs slow thinking [README.md:328-338]()
- Papers like "What Happened in LLMs Layers when Trained for Fast vs. Slow Thinking" [README.md:331]()

**Sources:** [README.md:14-18](), [README.md:328-338]()

---

## System 2 Characteristics in LLMs

### Diagram: System 2 Reasoning Pipeline

```mermaid
graph TB
    Input["User Query"] --> Plan["Planning<br/>(Part 4: MCTS)"]
    Plan --> Generate["Generate<br/>Candidate Solutions"]
    Generate --> Verify["Step-wise Verification<br/>(Part 2: Process Rewards)"]
    Verify --> Decision{"Quality<br/>Sufficient?"}
    
    Decision -->|No| Reflect["Reflection<br/>(Part 6)"]
    Reflect --> Generate
    
    Decision -->|Yes| Output["Final Answer"]
    
    Verify -.uses.-> PRM["Process Reward Models<br/>(Math-Shepherd, PRMBench)"]
    Plan -.implements.-> TreeSearch["Tree Search Algorithms<br/>(ReST-MCTS*, rStar-Math)"]
    
    style Input fill:#f9f9f9
    style Output fill:#f9f9f9
```

### Technical Properties

System 2 reasoning introduces:

1. **Multi-Step Deliberation**:
   - Explicit intermediate reasoning steps
   - Visible chain-of-thought traces
   - Examples: OpenAI o1, DeepSeek-R1 [README.md:107-108]()

2. **Search and Exploration**:
   - Tree search over reasoning paths (MCTS, beam search)
   - Evaluation of multiple candidate solutions
   - Implementations: [README.md:139-193]() (Part 4: MCTS/Tree Search)

3. **Process Supervision**:
   - Step-by-step verification of reasoning
   - Process Reward Models that score intermediate steps
   - Key papers: Math-Shepherd, PRMBench [README.md:73-81]()

4. **Self-Correction**:
   - Ability to detect and fix errors
   - Reflection mechanisms
   - Coverage: [README.md:225-241]() (Part 6: Reflection)

5. **Reinforcement Learning**:
   - Training models to optimize reasoning processes
   - Policy optimization for multi-step tasks
   - Major systems: DeepSeek-R1, Kimi k1.5 [README.md:107-108]()

**Sources:** [README.md:45-67](), [README.md:68-96](), [README.md:98-137](), [README.md:139-193](), [README.md:194-224](), [README.md:225-241]()

---

## The Transition Problem

### Why LLMs Need System 2

Standard LLMs excel at System 1 tasks (text completion, pattern recognition) but struggle with:

| Task Type | System 1 Performance | System 2 Requirement |
|-----------|---------------------|---------------------|
| **Mathematical Olympiad** | Inconsistent, pattern-dependent | Multi-step proof construction |
| **Code Generation (Complex)** | Syntax correct, logic flawed | Systematic planning and verification |
| **Scientific Reasoning** | Surface-level explanations | Deep causal understanding |
| **Long-Horizon Planning** | Myopic decisions | Lookahead and backtracking |

The repository documents that "foundational Large Language Models (LLMs) have made significant strides, they still fall short of human-like reasoning in complex tasks" [README.md:18]().

### Diagram: Transition Architecture in Repository

```mermaid
graph TB
    subgraph "Repository Structure: README.md"
        Intro["Introduction<br/>(Lines 14-18)"]
        TOC["Table of Contents<br/>(Lines 29-43)"]
        
        subgraph "Core Methodologies (Parts 1-6)"
            P1["Part 1: O1 Replication<br/>(Lines 45-67)"]
            P2["Part 2: Process Reward Models<br/>(Lines 68-96)"]
            P3["Part 3: Reinforcement Learning<br/>(Lines 98-137)"]
            P4["Part 4: MCTS/Tree Search<br/>(Lines 139-193)"]
            P5["Part 5: Self-Training<br/>(Lines 194-224)"]
            P6["Part 6: Reflection<br/>(Lines 225-241)"]
        end
        
        subgraph "Support Infrastructure (Parts 7-8)"
            P7["Part 7: Efficient System2<br/>(Lines 242-325)"]
            P8["Part 8: Explainability<br/>(Lines 327-338)"]
        end
        
        subgraph "Extensions (Parts 9, 12)"
            P9["Part 9: Multimodal Agents<br/>(Lines 339-350)"]
            P12["Part 12: R1-Driven Multimodal<br/>(Lines 455-481)"]
        end
        
        subgraph "Evaluation (Parts 10-11)"
            P10["Part 10: Benchmarks<br/>(Lines 351-433)"]
            P11["Part 11: Safety<br/>(Lines 437-453)"]
        end
    end
    
    subgraph "Data Layer"
        JSON["assets/paper.json<br/>(Structured Metadata)"]
        Builder["src/main.py<br/>(Generator)"]
        TableMD["src/table.md<br/>(Tabular View)"]
        ListMD["src/list.md<br/>(List View)"]
    end
    
    Intro --> TOC
    TOC --> P1
    TOC --> P2
    TOC --> P3
    TOC --> P4
    TOC --> P5
    TOC --> P6
    
    JSON --> Builder
    Builder --> TableMD
    Builder --> ListMD
    
    P1 -.synthesizes.-> P2
    P1 -.synthesizes.-> P3
    P1 -.synthesizes.-> P4
    P1 -.synthesizes.-> P5
    P1 -.synthesizes.-> P6
```

### Key Insight

**Part 1: O1 Replication** [README.md:45-67]() represents the aspirational target - systems that successfully combine all other techniques to achieve expert-level System 2 reasoning. Papers in this section attempt to reproduce or extend OpenAI's o1 model, which demonstrated breakthrough performance on mathematical reasoning and coding tasks.

**Sources:** [README.md:14-26](), [README.md:45-67]()

---

## Training-Time vs Inference-Time Strategies

The repository organizes System 2 research into two complementary approaches:

### Training-Time Enhancement

These techniques modify the model's learned behavior:

```mermaid
graph LR
    Base["Base LLM<br/>(System 1)"] --> SFT["Supervised Fine-Tuning<br/>(CoT Data)"]
    SFT --> RL["Reinforcement Learning<br/>(Part 3)<br/>DeepSeek-R1, Kimi k1.5"]
    RL --> Enhanced["Enhanced Model<br/>(System 2 Capabilities)"]
    
    PRM["Process Reward Models<br/>(Part 2)<br/>Math-Shepherd"] -.guides.-> RL
    SelfTrain["Self-Training<br/>(Part 5)<br/>STaR, ReST"] -.improves.-> RL
```

**Key Papers:**
- **DeepSeek-R1**: "Incentivizing Reasoning Capability in LLMs via Reinforcement Learning" [README.md:107]()
- **Kimi k1.5**: "Scaling Reinforcement Learning with LLMs" [README.md:108]()
- **Math-Shepherd**: Automated process supervision [README.md:73]()
- **STaR**: Bootstrapping reasoning with reasoning [README.md:197]()

### Inference-Time Augmentation

These techniques enhance reasoning without retraining:

```mermaid
graph TB
    Query["Query"] --> Router{"Complexity<br/>Assessment"}
    
    Router -->|Simple| Fast["System 1<br/>Direct Generation"]
    Router -->|Complex| Slow["System 2<br/>Deliberate Reasoning"]
    
    Slow --> MCTS["Monte Carlo Tree Search<br/>(Part 4)<br/>ReST-MCTS*, rStar-Math"]
    MCTS --> Candidates["Multiple Reasoning Paths"]
    
    Candidates --> PRM["Process Reward Scoring<br/>(Part 2)<br/>PRMBench"]
    PRM --> Select["Best Path Selection"]
    
    Fast --> Output["Response"]
    Select --> Output
    
    Efficient["Efficiency Optimizations<br/>(Part 7)<br/>DynaThink, O1-Pruner"] -.optimizes.-> MCTS
```

**Key Papers:**
- **ReST-MCTS***: LLM self-training via process reward guided tree search [README.md:78, 175]()
- **rStar-Math**: Self-evolved deep thinking [README.md:188]()
- **DynaThink**: Dynamic decision-making framework [README.md:246]()
- **O1-Pruner**: Length-harmonizing fine-tuning [README.md:254]()

**Sources:** [README.md:98-137](), [README.md:139-193](), [README.md:242-325]()

---

## Comparative Analysis Table

| Dimension | System 1 (Base LLMs) | System 2 (Reasoning LLMs) | Repository Coverage |
|-----------|---------------------|--------------------------|---------------------|
| **Inference Cost** | O(n) tokens | O(n × k) with k rollouts | Part 7: Efficient System2 [README.md:242-325]() |
| **Training Approach** | Supervised fine-tuning | RL + Process supervision | Part 3 [README.md:98-137](), Part 2 [README.md:68-96]() |
| **Error Detection** | None | Step-wise verification | Part 2: PRMBench [README.md:81]() |
| **Self-Correction** | Limited | Reflection mechanisms | Part 6 [README.md:225-241]() |
| **Search Strategy** | Greedy decoding | Tree search (MCTS, beam) | Part 4 [README.md:139-193]() |
| **Benchmark Tasks** | MMLU, HellaSwag | MATH, FrontierMath, Olympiad | Part 10 [README.md:351-433]() |
| **Safety Concerns** | Standard alignment | Deliberative alignment, jailbreaks | Part 11 [README.md:437-453]() |
| **Multimodal Extension** | Vision-language understanding | Visual reasoning with CoT | Part 9 [README.md:339-350](), Part 12 [README.md:455-481]() |

**Sources:** [README.md:29-43]()

---

## Repository Organization Around System 1/2 Concept

### Diagram: Conceptual Map to File Structure

```mermaid
graph TB
    Concept["System 1 → System 2<br/>Transition Concept"]
    
    subgraph "Primary Documentation"
        README["README.md<br/>(80.82% importance)<br/>Lines 14-509"]
        Survey["Survey Paper<br/>arxiv:2502.17419<br/>(Lines 11, 16)"]
    end
    
    subgraph "Data Sources"
        PaperJSON["assets/paper.json<br/>(~256 papers)<br/>12 categories"]
        Timeline1["assets/timeline_2.png<br/>(Line 25)"]
        Timeline2["assets/develope.jpg<br/>(Line 21)"]
    end
    
    subgraph "Build System"
        MainPy["src/main.py<br/>(Generator Script)"]
        TableMD["src/table.md<br/>(Sorted Tabular)"]
        ListMD["src/list.md<br/>(Chronological List)"]
    end
    
    subgraph "12 Research Parts"
        Part1["Part 1: O1 Replication<br/>README.md:45-67"]
        Part2_6["Parts 2-6: Core Methods<br/>README.md:68-241"]
        Part7_8["Parts 7-8: Optimization<br/>README.md:242-338"]
        Part9_12["Parts 9,12: Extensions<br/>README.md:339-350,455-481"]
        Part10_11["Parts 10-11: Evaluation<br/>README.md:351-453"]
    end
    
    Concept --> README
    Concept --> Survey
    
    README --> Part1
    README --> Part2_6
    README --> Part7_8
    README --> Part9_12
    README --> Part10_11
    
    PaperJSON --> MainPy
    MainPy --> TableMD
    MainPy --> ListMD
    
    PaperJSON -.informs.-> README
    Timeline1 -.visualizes.-> Concept
    Timeline2 -.visualizes.-> Concept
```

### File-Level Mapping

1. **Introduction and Motivation**: [README.md:14-26]()
   - Defines System 1 vs System 2 distinction
   - References survey paper as comprehensive treatment

2. **Methodological Organization**: [README.md:29-43]()
   - Table of contents organizing research into 12 parts
   - Each part addresses specific aspect of System 1→2 transition

3. **Data Infrastructure**: 
   - `assets/paper.json`: Structured metadata for research papers
   - `src/main.py`: Processes JSON into alternative views
   - `src/table.md`, `src/list.md`: Auto-generated reference formats

4. **Visual Context**:
   - `assets/timeline_2.png`: Historical progression of reasoning LLMs [README.md:25-26]()
   - `assets/develope.jpg`: Conceptual evolution diagram [README.md:21-23]()

**Sources:** [README.md:1-509](), [src/main.py](), [assets/paper.json](), [src/list.md:1-129]()

---

## Key Research Milestones in System 1→2 Evolution

### Timeline of Breakthrough Papers

```mermaid
timeline
    title System 1 to System 2 Evolution (Repository View)
    
    2017-2021 : Expert Iteration (2017)
              : Foundation for iterative improvement
              : README.md Line 196
    
    2022 : STaR: Bootstrapping Reasoning (May 2022)
         : Self-training emergence
         : README.md Line 197
    
    2023 : Let's Verify Step by Step (May 2024)
         : Process reward breakthrough
         : README.md Line 75
         : Self-Refine: Iterative Refinement
         : README.md Line 200
         : ReST: Reinforced Self-Training
         : README.md Line 201
    
    2024 : OpenAI o1 Released (Sep 2024)
         : System 2 demonstration
         : Multiple MCTS applications
         : README.md Lines 141-182
         : Math-Shepherd: Automated PRMs
         : README.md Line 73
    
    2025 : DeepSeek-R1 (Jan 2025)
         : Large-scale RL reasoning
         : README.md Line 107
         : Kimi k1.5 (Jan 2025)
         : Scaled RL implementation
         : README.md Line 108
         : rStar-Math (Jan 2025)
         : Self-evolved deep thinking
         : README.md Line 188
```

### Citation Network

Papers frequently appear in multiple parts, indicating integration of techniques:

| Paper | Parts | Significance |
|-------|-------|--------------|
| **ReST-MCTS*** [README.md:78, 175, 212]() | Part 2, 4, 5 | Combines process rewards, tree search, self-training |
| **Math-Shepherd** [README.md:73]() | Part 2 | Automated process supervision without human labels |
| **DeepSeek-R1** [README.md:107]() | Part 3 | Largest-scale RL-based reasoning model |
| **Marco-o1** [README.md:49, 172, 234]() | Part 1, 4, 6 | Open reasoning with MCTS and reflection |
| **HuatuoGPT-o1** [README.md:53, 177, 237]() | Part 1, 4, 6 | Medical domain System 2 reasoning |

**Sources:** [README.md:45-509]()

---

## Practical Implications for Researchers

### Using This Repository to Navigate System 1→2 Research

**If you want to understand:**

1. **What makes o1 special** → Start with [Part 1: O1 Replication](#4.1)
   - Papers attempting to reproduce/extend o1 [README.md:45-67]()
   
2. **How to train reasoning models** → Focus on [Part 3: Reinforcement Learning](#4.3)
   - DeepSeek-R1, Kimi k1.5 as reference implementations [README.md:98-137]()
   
3. **How to verify reasoning steps** → Examine [Part 2: Process Reward Models](#4.2)
   - Math-Shepherd, PRMBench [README.md:68-96]()
   
4. **How to enable inference-time reasoning** → Study [Part 4: MCTS/Tree Search](#4.4)
   - ReST-MCTS*, rStar-Math [README.md:139-193]()
   
5. **How to make it efficient** → Review [Part 7: Efficient System2](#5.1)
   - DynaThink, O1-Pruner [README.md:242-325]()

### Evaluation Strategy

For assessing System 2 capabilities:

- **Mathematical Reasoning**: FrontierMath, MATH benchmarks [README.md:355, 410]()
- **Meta-Reasoning**: MR-Ben [README.md:356]()
- **Process-Level**: PRMBench [README.md:81, 365]()
- **Safety**: H-CoT jailbreak analysis [README.md:447]()

**Sources:** [README.md:351-433]()

---

## Relationship to Other Wiki Pages

This page provides the conceptual foundation. For detailed technical coverage:

- **[Research Landscape Overview](#3)**: How the 12 parts interconnect
- **[Core Methodologies](#4)**: Deep dive into Parts 1-6
  - **[O1 Replication](#4.1)**: Target architecture
  - **[Process Reward Models](#4.2)**: Step-wise supervision
  - **[Reinforcement Learning](#4.3)**: Training strategies
  - **[MCTS and Tree Search](#4.4)**: Search algorithms
  - **[Self-Training](#4.5)**: Bootstrapping methods
  - **[Reflection](#4.6)**: Self-correction mechanisms
- **[Optimization and Understanding](#5)**: Making System 2 practical
- **[Multimodal Extensions](#6)**: Beyond text reasoning
- **[Evaluation and Safety](#7)**: Assessment and risks
- **[Repository Structure](#10)**: How documentation is maintained

**Sources:** [README.md:29-43]()

---

## Summary

The System 1 vs System 2 framework is the organizing principle for this entire repository:

- **System 1**: Fast, pattern-matching LLMs (baseline autoregressive generation)
- **System 2**: Slow, deliberate reasoning (multi-step verification, search, reflection)
- **Transition**: Achieved through combinations of:
  - Reinforcement learning for reasoning capabilities
  - Process reward models for step-wise supervision
  - Tree search for exploration
  - Self-training for bootstrapping
  - Reflection for error correction

The repository tracks ~256 papers across 12 research parts, with files structured as:
- `README.md`: Primary curated documentation (80.82% importance)
- `assets/paper.json`: Structured metadata
- `src/main.py`: Generation pipeline
- `src/table.md`, `src/list.md`: Alternative views

**Part 1: O1 Replication** represents the synthesis target where all techniques converge to achieve expert-level reasoning comparable to OpenAI's o1 or DeepSeek-R1.

**Sources:** [README.md:1-509]()

---

# Page: Research Landscape Overview

# Research Landscape Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)

</details>



## Purpose and Scope

This page provides a comprehensive overview of the System 2 reasoning research landscape as organized in this repository. It explains the 12-part taxonomy that structures the field, the relationships between different research areas, and the historical evolution from 2017 to 2025. 

For detailed coverage of individual research methodologies, see [Core Methodologies](#4). For information about using and navigating the repository, see [Using This Resource](#11). For the conceptual distinction between System 1 and System 2 reasoning, see [System 1 vs System 2 Reasoning](#2).

**Sources:** [README.md:14-27](), [README.md:29-43]()

---

## The 12-Part Taxonomy

The repository organizes System 2 reasoning research into 12 interconnected parts, structured across four major categories. This taxonomy reflects both the technical components needed to build reasoning systems and the supporting infrastructure for evaluation and deployment.

### Taxonomy Structure

```mermaid
graph TB
    subgraph CORE["Core Methodologies (Parts 1-6)"]
        P1["Part 1: O1 Replication<br/>OpenAI o1, DeepSeek-R1<br/>~17 papers"]
        P2["Part 2: Process Reward Models<br/>Math-Shepherd, PRMBench<br/>~24 papers"]
        P3["Part 3: Reinforcement Learning<br/>PPO, DPO, GRPO<br/>~38 papers"]
        P4["Part 4: MCTS/Tree Search<br/>ReST-MCTS*, rStar-Math<br/>~55 papers"]
        P5["Part 5: Self-Training/Self-Improve<br/>STaR, ReST, V-star<br/>~20 papers"]
        P6["Part 6: Reflection<br/>Self-Refine, CRITIC<br/>~16 papers"]
    end
    
    subgraph OPT["Optimization & Understanding (Parts 7-8)"]
        P7["Part 7: Efficient System2<br/>DynaThink, O1-Pruner<br/>~82 papers"]
        P8["Part 8: Explainability<br/>Layer Analysis, Gradients<br/>~11 papers"]
    end
    
    subgraph EXT["Extensions (Parts 9, 12)"]
        P9["Part 9: Multimodal Agents<br/>LLaVA-o1, AtomThink<br/>~10 papers"]
        P12["Part 12: R1-Driven Multimodal<br/>MedVLM-R1, Virgo<br/>~26 papers"]
    end
    
    subgraph EVAL["Evaluation & Safety (Parts 10-11)"]
        P10["Part 10: Benchmarks & Datasets<br/>FrontierMath, MR-Ben<br/>~81 papers"]
        P11["Part 11: Reasoning & Safety<br/>H-CoT, Deliberative Alignment<br/>~13 papers"]
    end
    
    P1 -.."aspirational<br/>target"..-> P2
    P1 -.."aspirational<br/>target"..-> P3
    P1 -.."aspirational<br/>target"..-> P4
    P1 -.."aspirational<br/>target"..-> P5
    P1 -.."aspirational<br/>target"..-> P6
```

**Sources:** [README.md:31-43](), [README.md:45-482]()

### Category Breakdown

| Category | Parts | Focus | Paper Count (approx) |
|----------|-------|-------|---------------------|
| **Core Methodologies** | 1-6 | Foundational techniques for reasoning | ~170 papers |
| **Optimization & Understanding** | 7-8 | Efficiency and interpretability | ~93 papers |
| **Extensions** | 9, 12 | Multimodal applications | ~36 papers |
| **Evaluation & Safety** | 10-11 | Assessment and security | ~94 papers |

**Sources:** [README.md:45-482](), [assets/paper.json:1-848]()

---

## Part Interconnections and Dependencies

The 12 parts form a tightly coupled ecosystem where techniques combine synergistically. Understanding these relationships is crucial for comprehending how modern reasoning systems work.

### Technical Dependencies

```mermaid
graph LR
    subgraph Training["Training-Time Components"]
        PRM["Part 2:<br/>Process Reward<br/>Models"]
        RL["Part 3:<br/>Reinforcement<br/>Learning"]
        SELF["Part 5:<br/>Self-Training"]
    end
    
    subgraph Inference["Inference-Time Components"]
        MCTS["Part 4:<br/>MCTS/Tree<br/>Search"]
        REFLECT["Part 6:<br/>Reflection"]
    end
    
    subgraph Integration["Integrated Systems"]
        O1["Part 1:<br/>O1 Replication<br/>Target Architecture"]
    end
    
    subgraph Support["Supporting Infrastructure"]
        EFF["Part 7:<br/>Efficient<br/>System2"]
        EXPLAIN["Part 8:<br/>Explainability"]
        BENCH["Part 10:<br/>Benchmarks"]
        SAFE["Part 11:<br/>Safety"]
    end
    
    subgraph Extensions["Domain Extensions"]
        MM["Part 9:<br/>Multimodal<br/>Agents"]
        R1MM["Part 12:<br/>R1-Driven<br/>Multimodal"]
    end
    
    PRM -->|"guides"| RL
    PRM -->|"evaluates"| MCTS
    PRM -->|"validates"| SELF
    
    RL -->|"optimizes"| SELF
    MCTS -->|"generates data"| SELF
    MCTS -->|"uses"| PRM
    
    REFLECT -->|"refines"| MCTS
    REFLECT -->|"improves"| SELF
    
    PRM --> O1
    RL --> O1
    MCTS --> O1
    SELF --> O1
    REFLECT --> O1
    
    EFF -.->|"optimizes"| O1
    EFF -.->|"optimizes"| MCTS
    EXPLAIN -.->|"analyzes"| O1
    EXPLAIN -.->|"analyzes"| RL
    
    O1 --> MM
    O1 --> R1MM
    
    BENCH -.->|"evaluates"| O1
    BENCH -.->|"evaluates"| MM
    SAFE -.->|"secures"| O1
```

**Key Integration Patterns:**

1. **ReST-MCTS* Pipeline**: Combines Part 2 (Process Rewards), Part 4 (MCTS), and Part 5 (Self-Training) into a unified self-improvement loop
2. **O1 Architecture**: Synthesizes Parts 2-6 into a production reasoning system (Part 1)
3. **R1-Multimodal Extension**: Applies Part 1 methodologies to vision-language models (Part 12)

**Sources:** [README.md:45-67](), [README.md:68-96](), [README.md:98-137](), [README.md:139-193](), [README.md:194-224](), [README.md:225-241]()

---

## Research Evolution Timeline

The field has progressed through distinct phases, with accelerating innovation particularly visible from 2023 onward.

### Historical Progression (2017-2025)

```mermaid
timeline
    title System 2 Reasoning Research Evolution
    
    2017-2021 : Foundation Era
              : Expert Iteration (2017, NeurIPS)
              : Tree Search + Deep Learning
              : MCTS foundations for language
    
    2022 : Self-Training Emergence
         : STaR (Bootstrapping Reasoning)
         : Process vs Outcome Rewards
    
    2023 : Critical Breakthroughs
         : Let's Verify Step by Step (Process Rewards)
         : AlphaZero-like Tree Search for LLMs
         : ReST (Reinforced Self-Training)
         : Self-Refine (Reflection mechanisms)
         : RAP (Reasoning with Planning)
    
    2024 : Integration & Acceleration
         : Math-Shepherd (Automated PRMs)
         : ReST-MCTS* (Process + Search)
         : DeepSeekMath (RL at scale)
         : Multiple MCTS variants
         : LLaVA-o1 (Multimodal reasoning)
         : O1 Replication efforts begin
         : V-star, Quiet-STaR
    
    2025 : Production & Maturity
         : DeepSeek-R1 (Large-scale RL)
         : Kimi k1.5 (Scaled RL)
         : rStar-Math (Self-evolved reasoning)
         : Virgo, MM-Eureka (Multimodal O1-like)
         : O1-Pruner (Efficient System2)
         : PRMBench (Advanced evaluation)
         : H-CoT (Safety research)
```

**Sources:** [README.md:196](), [README.md:517](), [README.md:201-202](), [README.md:75](), [README.md:235](), [README.md:175](), [README.md:107-108](), [README.md:188]()

### Phase Characteristics

| Era | Key Innovation | Representative Papers | Lines in README |
|-----|---------------|---------------------|-----------------|
| **2017-2021** | Deep learning + tree search fusion | Expert Iteration | [README.md:196]() |
| **2022** | Bootstrapping without human labels | STaR | [README.md:197]() |
| **2023** | Process supervision + AlphaZero adaptation | Let's Verify Step by Step, RAP | [README.md:75](), [README.md:141]() |
| **2024** | Integration of multiple techniques | ReST-MCTS*, Math-Shepherd | [README.md:78](), [README.md:73]() |
| **2025** | Production-scale systems | DeepSeek-R1, Kimi k1.5 | [README.md:107-108]() |

**Sources:** [README.md:45-482](), [assets/paper.json:1-848]()

---

## Repository Organization and Code Structure

The repository uses a hybrid documentation approach with both human-curated and machine-generated views of the research landscape.

### Data Architecture

```mermaid
graph TB
    subgraph Source["Source Data Layer"]
        JSON["assets/paper.json<br/>{12 part categories}<br/>~256 papers<br/>structured metadata"]
    end
    
    subgraph Generator["Build System"]
        MAIN["src/main.py<br/>Python script"]
        LOAD["load_data()<br/>JSON parsing"]
        EXTRACT["extract_paper_info()<br/>Flatten hierarchy"]
        RESOLVE["resolve_labels()<br/>Deduplicate"]
    end
    
    subgraph Outputs["Generated Outputs"]
        TABLE["src/table.md<br/>Tabular format<br/>Title | Venue | Date"]
        LIST["src/list.md<br/>List format<br/>With badges"]
    end
    
    subgraph Primary["Primary Interface"]
        README["README.md<br/>Hand-curated<br/>12-part structure<br/>Rich descriptions<br/>Lines 45-482"]
    end
    
    JSON --> LOAD
    LOAD --> EXTRACT
    EXTRACT --> RESOLVE
    RESOLVE --> TABLE
    RESOLVE --> LIST
    
    JSON -.informs.-> README
    
    README -.manual.-> JSON
```

**Sources:** [assets/paper.json:1-848](), [src/main.py:1-150](), [README.md:1-509]()

### JSON Data Structure

The `paper.json` file structures metadata for ~256 papers across the 12 parts:

```json
{
    "Part 1: O1 Replication": [
        {
            "paper": "Paper Title",
            "link": "https://arxiv.org/abs/...",
            "venue": "arXiv|ACL|NeurIPS|...",
            "date": "YYYY-MM",
            "label": "citation_key"
        }
    ],
    "Part 2: Process Reward Models": [...],
    ...
}
```

**Key fields:**
- `paper`: Full paper title
- `link`: Primary URL (arXiv, conference proceedings, blog)
- `venue`: Publication venue or preprint server
- `date`: Publication date (YYYY-MM format)
- `label`: BibTeX-style citation key

**Sources:** [assets/paper.json:1-848]()

### README Structure

The primary interface at [README.md:1-509]() follows a consistent pattern for each part:

1. **Part Header** (e.g., line 45: `## Part 1: O1 Replication`)
2. **Paper Listings** with badges:
   - Paper title with `[[Paper]]` link
   - Venue badge: `![](https://img.shields.io/badge/venue-date-color)`
   - Optional `[[Blog]]`, `[[github]]`, `[[Notion]]` links
3. **Chronological Organization** within each part (newest first)

**Example pattern:**
```markdown
## Part N: Category Name

* Paper Title [[Paper]](URL) ![](badge) [[optional-resource]](URL)
* Paper Title [[Paper]](URL) ![](badge)
...
```

**Sources:** [README.md:45-482]()

---

## Part-Specific Scope and Focus

Each part has a distinct technical focus and paper selection criteria:

| Part | Focus Area | Key Techniques | Paper Count | README Lines |
|------|-----------|----------------|-------------|--------------|
| **Part 1** | Replication of o1-like systems | Full system architectures, distillation | 17 | [README.md:45-67]() |
| **Part 2** | Step-wise supervision | Automated PRM generation, verification | 24 | [README.md:68-96]() |
| **Part 3** | Policy optimization | PPO, DPO, GRPO, RL at scale | 38 | [README.md:98-137]() |
| **Part 4** | Search algorithms | MCTS variants, tree search, planning | 55 | [README.md:139-193]() |
| **Part 5** | Bootstrapping methods | STaR, ReST, iterative self-improvement | 20 | [README.md:194-224]() |
| **Part 6** | Self-correction | Reflection, critique, iterative refinement | 16 | [README.md:225-241]() |
| **Part 7** | Computational efficiency | Token budgeting, latent reasoning, pruning | 82 | [README.md:242-325]() |
| **Part 8** | Mechanism understanding | Layer analysis, attention patterns | 11 | [README.md:327-338]() |
| **Part 9** | Vision-language agents | Slow-fast multimodal systems | 10 | [README.md:339-350]() |
| **Part 10** | Evaluation frameworks | Benchmarks, datasets, metrics | 81 | [README.md:351-433]() |
| **Part 11** | Security research | Jailbreaks, alignment, safety | 13 | [README.md:437-453]() |
| **Part 12** | R1-style multimodal | Applying R1/o1 to vision models | 26 | [README.md:455-481]() |

**Sources:** [README.md:45-482]()

---

## Convergence Toward O1-Like Systems

The research landscape shows clear convergence toward integrated systems that combine multiple techniques. Part 1 (O1 Replication) represents the aspirational target that synthesizes insights from Parts 2-6.

### Integration Evidence

**Papers appearing in multiple parts:**
- `ReST-MCTS*` appears in Parts 2, 4, 5 (Process Rewards + MCTS + Self-Training)
- `HuatuoGPT-o1` appears in Parts 1, 4, 6 (O1 Replication + MCTS + Reflection)
- `Marco-o1` appears in Parts 1, 4, 6 (O1 Replication + MCTS + Reflection)
- `rStar-Math` appears in Parts 1, 4, 5, 6 (O1 Replication + MCTS + Self-Training + Reflection)

**Cross-references in paper titles:**
- "O1-like" terminology appears across Parts 1, 4, 6, 9, 12
- "R1-driven" terminology creates Part 12's focus
- "Slow thinking" terminology bridges Parts 1, 7, 9

**Sources:** [README.md:49](), [README.md:78](), [README.md:172](), [README.md:177](), [README.md:188](), [README.md:220]()

---

## Practical Navigation Strategies

### By Research Interest

- **Building reasoning systems**: Start with Part 1 → Parts 2-6 → Part 7
- **Improving existing models**: Parts 5, 6 → Parts 2, 3
- **Inference-time optimization**: Parts 4, 7 → Part 2
- **Multimodal applications**: Parts 9, 12 → Part 1
- **Evaluation**: Part 10 → Parts 2, 11

### By Computational Budget

- **High compute**: Parts 3, 4 (full RL training, exhaustive search)
- **Medium compute**: Parts 2, 5 (self-training with verification)
- **Low compute**: Parts 6, 7 (reflection, efficient inference)

### By Timeline

- **Historical foundations (2017-2022)**: Parts 4, 5
- **Breakthrough period (2023-2024)**: Parts 2, 3, 4
- **Current state-of-art (2025)**: Parts 1, 3, 7, 12

**Sources:** [README.md:45-482]()

---

## Maintenance and Updates

The repository is actively maintained with regular updates reflected in the README changelog:

- **February 2025**: Survey paper release [README.md:11]()
- **Ongoing**: Papers added as they appear on arXiv
- **Structure**: 12-part taxonomy has remained stable since repository inception

New papers are added to [assets/paper.json:1-848]() and manually integrated into [README.md:45-482]() with appropriate badges and links.

**Sources:** [README.md:9-11](), [README.md:485-497]()

---

# Page: Core Methodologies

# Core Methodologies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/table.md](src/table.md)

</details>



## Purpose and Scope

This document provides a comprehensive technical reference for the six foundational methodologies (Parts 1-6) that form the basis of modern System 2 reasoning in Large Language Models. These techniques enable the transition from fast, intuitive System 1 thinking to slow, deliberate System 2 reasoning. Each methodology addresses a specific aspect of the reasoning pipeline, from training algorithms to inference-time search strategies.

For information about optimization and efficiency techniques, see [Efficient System2](#5.1). For evaluation frameworks, see [Benchmarks and Datasets](#7.1). For multimodal extensions, see [Multimodal Extensions](#6).

**Sources:** [README.md:28-44](), [README.md:14-18]()

---

## Methodology Taxonomy

The six core methodologies form an interconnected technical ecosystem where each component serves a specific role in the reasoning pipeline:

```mermaid
graph TB
    subgraph "Target Architecture"
        O1["Part 1: O1 Replication<br/>Target: OpenAI o1, DeepSeek-R1<br/>Goal: Expert-level reasoning"]
    end
    
    subgraph "Training Components"
        PRM["Part 2: Process Reward Models<br/>Step-wise supervision<br/>Math-Shepherd, PRMBench"]
        RL["Part 3: Reinforcement Learning<br/>Policy optimization<br/>PPO, DPO, GRPO"]
        SELF["Part 5: Self-Training<br/>Bootstrapping<br/>STaR, ReST, rStar-Math"]
    end
    
    subgraph "Inference Components"
        MCTS["Part 4: MCTS/Tree Search<br/>Exploration & planning<br/>ReST-MCTS*, AlphaZero-like"]
        REFLECT["Part 6: Reflection<br/>Self-correction<br/>Self-Refine, CRITIC"]
    end
    
    PRM --> RL
    PRM --> MCTS
    PRM --> SELF
    
    RL --> O1
    SELF --> O1
    MCTS --> O1
    REFLECT --> O1
    
    MCTS --> SELF
    RL --> MCTS
    
    REFLECT --> SELF
    
    style O1 stroke-width:3px
```

**Diagram: Core Methodology Taxonomy and Dependencies**

This architecture shows how the six methodologies integrate to achieve O1-like reasoning capabilities. Process Reward Models provide the foundation for guiding both training (RL, Self-Training) and inference (MCTS). The target O1 architecture synthesizes all components.

**Sources:** [README.md:45-241](), [README.md:28-44]()

---

## Repository Data Structure

The methodologies are organized in the repository's data layer:

```mermaid
graph LR
    subgraph "Data Layer: assets/paper.json"
        JSON["paper.json structure"]
        
        P1["'Part 1: O1 Replication'<br/>label reference"]
        P2["'Part 2: Process Reward Models'<br/>step-wise supervision"]
        P3["'Part 3: Reinforcement Learning'<br/>policy optimization"]
        P4["'Part 4: MCTS/Tree Search'<br/>exploration algorithms"]
        P5["'Part 5: Self-Training'<br/>bootstrapping methods"]
        P6["'Part 6: Reflection'<br/>self-correction"]
    end
    
    subgraph "Documentation Layer: README.md"
        README_P1["## Part 1: O1 Replication<br/>Lines 45-67"]
        README_P2["## Part 2: Process Reward Models<br/>Lines 68-96"]
        README_P3["## Part 3: Reinforcement Learning<br/>Lines 98-137"]
        README_P4["## Part 4: MCTS/Tree Search<br/>Lines 139-193"]
        README_P5["## Part 5: Self-Training<br/>Lines 194-224"]
        README_P6["## Part 6: Reflection<br/>Lines 225-241"]
    end
    
    subgraph "Build System: src/main.py"
        LOADER["load_json_file()<br/>process_paper_data()"]
        PROCESS["resolve label references<br/>deduplicate papers"]
    end
    
    JSON --> P1
    JSON --> P2
    JSON --> P3
    JSON --> P4
    JSON --> P5
    JSON --> P6
    
    P1 --> README_P1
    P2 --> README_P2
    P3 --> README_P3
    P4 --> README_P4
    P5 --> README_P5
    P6 --> README_P6
    
    JSON --> LOADER
    LOADER --> PROCESS
    PROCESS --> README_P1
    PROCESS --> README_P2
    PROCESS --> README_P3
    PROCESS --> README_P4
    PROCESS --> README_P5
    PROCESS --> README_P6
```

**Diagram: Mapping Natural Language Categories to Code Entities**

The repository uses a structured approach where `paper.json` contains paper metadata organized by part labels, which are processed by `src/main.py` and documented in `README.md`.

**Sources:** [README.md:45-241](), [src/main.py:1-100]() (implied from architecture diagrams)

---

## Part 1: O1 Replication

### Overview

O1 Replication represents the aspirational target architecture that synthesizes all other core methodologies. This category tracks efforts to reproduce and extend OpenAI's o1 model, which demonstrated expert-level performance on mathematical and coding tasks through extended chain-of-thought reasoning.

### Key Papers and Approaches

| Paper | Date | Key Contribution |
|-------|------|------------------|
| O1 Replication Journey Part 1 | 2024-10 | Initial strategic framework for reproduction |
| O1 Replication Journey Part 2 | 2024-11 | Distillation-based approaches, surpassing o1-preview |
| Marco-o1 | 2024-11 | Open-ended solution generation with MCTS |
| DeepSeek-R1 | 2025-01 | Large-scale RL-based reasoning system |
| Kimi k1.5 | 2025-01 | Scaled reinforcement learning implementation |
| o1-Coder | 2024-12 | Domain-specific replication for coding |
| HuatuoGPT-o1 | 2024-12 | Medical domain reasoning |
| Search-o1 | 2025-01 | Agentic search-enhanced reasoning |

### Technical Architecture

```mermaid
graph TB
    subgraph "O1-like System Architecture"
        INPUT["User Query"]
        
        subgraph "Training Pipeline"
            SFT["Supervised Fine-Tuning<br/>Chain-of-Thought data"]
            RL_TRAIN["RL Training<br/>GRPO, PPO algorithms"]
            PRM_GEN["Process Reward Model<br/>Step-wise verification"]
        end
        
        subgraph "Inference Pipeline"
            SEARCH["Tree Search/MCTS<br/>Explore reasoning paths"]
            VERIFY["Process Verification<br/>Validate each step"]
            SELECT["Best Response Selection<br/>Outcome-based ranking"]
        end
        
        OUTPUT["Expert-level Response<br/>Extended CoT reasoning"]
    end
    
    INPUT --> SFT
    SFT --> RL_TRAIN
    PRM_GEN --> RL_TRAIN
    
    RL_TRAIN --> SEARCH
    SEARCH --> VERIFY
    VERIFY --> SELECT
    SELECT --> OUTPUT
    
    PRM_GEN -.guides.-> VERIFY
```

**Diagram: O1 Replication Technical Architecture**

The architecture combines training-time components (SFT, RL, Process Rewards) with inference-time components (Tree Search, Verification, Selection) to achieve extended reasoning capabilities.

### Key Implementations

- **DeepSeek-R1**: Focuses on pure RL from scratch without supervised fine-tuning on chain-of-thought data
- **Kimi k1.5**: Emphasizes scaling RL with larger models and datasets
- **Marco-o1**: Integrates MCTS for open-ended problem solving
- **Open R1**: Open-source community implementation (GitHub: `huggingface/open-r1`)

**Sources:** [README.md:45-67](), [src/table.md:1-9]()

---

## Part 2: Process Reward Models

### Overview

Process Reward Models (PRMs) provide fine-grained, step-by-step supervision of reasoning processes. Unlike outcome reward models that only evaluate final answers, PRMs assess the correctness and quality of each intermediate reasoning step, enabling more effective training and inference-time verification.

### Core Concept

PRMs assign rewards to individual steps in a reasoning chain:

```
Question: What is 15 × 23?
Step 1: "Let me break this down: 15 × 23 = 15 × (20 + 3)"  [Reward: +0.9]
Step 2: "= 15 × 20 + 15 × 3"                              [Reward: +0.95]
Step 3: "= 300 + 45"                                       [Reward: +0.95]
Step 4: "= 345"                                            [Reward: +1.0]
```

### Key Papers and Methods

| Method | Date | Approach | Key Innovation |
|--------|------|----------|----------------|
| Let's Verify Step by Step | 2024-05 | Human-annotated process supervision | Foundational PRM training |
| Math-Shepherd | 2024-08 | Automated PRM generation | Auto-annotation without human labels |
| AutoPSV | 2024-12 | Automated process-supervised verifier | Scalable automatic verification |
| ReST-MCTS* | 2024-12 | PRM-guided tree search | Integration with MCTS |
| PRMBench | 2025-01 | Fine-grained benchmark | Evaluation framework |

### Training Pipeline

```mermaid
graph LR
    subgraph "PRM Training"
        DATA["Training Data<br/>with step labels"]
        ANNOT["Annotation Method"]
        MODEL["Base LLM"]
        PRM["Process Reward Model"]
    end
    
    subgraph "Annotation Types"
        HUMAN["Human Annotation<br/>Let's Verify Step by Step"]
        AUTO["Automated Annotation<br/>Math-Shepherd, AutoPSV"]
    end
    
    DATA --> ANNOT
    ANNOT --> HUMAN
    ANNOT --> AUTO
    HUMAN --> PRM
    AUTO --> PRM
    MODEL --> PRM
    
    subgraph "Applications"
        RL_APP["RL Training<br/>Part 3"]
        MCTS_APP["MCTS Guidance<br/>Part 4"]
        SELF_APP["Self-Training<br/>Part 5"]
    end
    
    PRM --> RL_APP
    PRM --> MCTS_APP
    PRM --> SELF_APP
```

**Diagram: Process Reward Model Training and Application Pipeline**

### Recent Developments (2025)

- **PRMBench**: Comprehensive benchmark with fine-grained process-level evaluation
- **ReARTeR**: Retrieval-augmented reasoning with trustworthy process rewarding
- **AdaptiveStep**: Automatic reasoning step division based on model confidence
- **Better Process Supervision**: Bi-directional rewarding signals for improved training

**Sources:** [README.md:68-96](), [src/table.md:10-27]()

---

## Part 3: Reinforcement Learning

### Overview

Reinforcement Learning techniques enable LLMs to learn reasoning capabilities through reward-driven optimization. Key algorithms include Proximal Policy Optimization (PPO), Direct Preference Optimization (DPO), and Group Relative Policy Optimization (GRPO).

### Major Implementations

| System | Date | Scale | Key Features |
|--------|------|-------|--------------|
| DeepSeek-R1 | 2025-01 | Large-scale | Pure RL from scratch, no CoT SFT |
| Kimi k1.5 | 2025-01 | Scaled RL | Emphasis on data and model scaling |
| DeepSeekMath | 2024-02 | Math-focused | Domain-specific RL training |
| DeepScaleR | 2025-02 | 1.5B model | Efficient RL at small scale |

### RL Training Loop

```mermaid
graph TB
    subgraph "RL Training Pipeline"
        POLICY["Policy Model<br/>Current LLM state"]
        SAMPLE["Sample Responses<br/>Multiple reasoning paths"]
        REWARD["Reward Assignment"]
        UPDATE["Policy Update<br/>PPO/DPO/GRPO"]
        
        subgraph "Reward Sources"
            ORM["Outcome Reward Model<br/>Final answer correctness"]
            PRM_RL["Process Reward Model<br/>Step-wise correctness"]
            ENV["Environment Feedback<br/>Code execution, etc."]
        end
    end
    
    POLICY --> SAMPLE
    SAMPLE --> REWARD
    
    ORM --> REWARD
    PRM_RL --> REWARD
    ENV --> REWARD
    
    REWARD --> UPDATE
    UPDATE --> POLICY
```

**Diagram: Reinforcement Learning Training Loop for Reasoning**

### RL Algorithms

**PPO (Proximal Policy Optimization):**
- Clips policy updates to prevent catastrophic changes
- Balances exploration and exploitation
- Used in DeepSeek-R1 and many implementations

**GRPO (Group Relative Policy Optimization):**
- Compares responses within groups
- More stable than absolute reward optimization
- Featured in Kimi k1.5

**DPO (Direct Preference Optimization):**
- Learns directly from preference pairs
- Simpler than PPO, no explicit reward model
- Used for alignment and refinement

### Key Findings

- **Scaling**: RL benefits significantly from larger models and more training data
- **Exploration**: Proper exploration strategies crucial for discovering novel reasoning paths
- **Safety Challenges**: RL can compromise safety alignment if not carefully managed
- **Inference-time Scaling**: RL-trained models show better test-time compute scaling

**Sources:** [README.md:98-137](), [src/table.md:28-39]()

---

## Part 4: MCTS and Tree Search

### Overview

Monte Carlo Tree Search (MCTS) and related tree search algorithms enable LLMs to explore multiple reasoning paths during inference, selecting optimal solutions through systematic exploration and evaluation.

### MCTS Components

```mermaid
graph TB
    subgraph "MCTS Algorithm"
        ROOT["Root Node<br/>Initial problem state"]
        
        SELECT["1. Selection<br/>Choose promising node<br/>UCB formula"]
        EXPAND["2. Expansion<br/>Generate new child nodes<br/>LLM sampling"]
        SIMULATE["3. Simulation<br/>Rollout to terminal state<br/>Fast evaluation"]
        BACKUP["4. Backpropagation<br/>Update node values<br/>Q-value aggregation"]
    end
    
    ROOT --> SELECT
    SELECT --> EXPAND
    EXPAND --> SIMULATE
    SIMULATE --> BACKUP
    BACKUP --> SELECT
    
    subgraph "LLM Integration"
        LLM["Base LLM<br/>Step generation"]
        VALUE["Value Model<br/>State evaluation"]
        PRM_MCTS["Process Reward Model<br/>Step verification"]
    end
    
    LLM --> EXPAND
    VALUE --> SIMULATE
    PRM_MCTS --> BACKUP
```

**Diagram: MCTS Algorithm for LLM Reasoning**

### Key Papers and Variants

| Method | Date | Innovation |
|--------|------|------------|
| RAP (Reasoning with Planning) | 2023-12 | World model for state representation |
| AlphaZero-like Tree-Search | 2023-12 | Adapt AlphaZero to LLM decoding |
| MindStar | 2024-05 | Enhanced inference-time reasoning |
| ReST-MCTS* | 2024-12 | Process reward guided search + self-training |
| rStar-Math | 2025-01 | Self-evolved deep thinking with MCTS |
| LLaMA-Berry | 2024-10 | Pairwise optimization for Olympiad-level math |

### Integration Patterns

**ReST-MCTS* Pipeline:**
```
Training Iteration:
1. Use MCTS to explore reasoning paths (guided by PRM)
2. Collect high-quality trajectories
3. Train policy model on collected data
4. Update PRM from new trajectories
5. Repeat with improved models
```

**rStar-Math Approach:**
```
Self-Evolution Loop:
1. Generate diverse reasoning paths via MCTS
2. Self-evaluate with code verification
3. Bootstrap on successful solutions
4. Evolve deeper reasoning capabilities
```

### Applications

- **Code Generation**: CodeTree, SRA-MCTS, RethinkMCTS
- **Mathematical Reasoning**: AlphaMath, MindStar, rStar-Math
- **Medical Reasoning**: HuatuoGPT-o1
- **General Problem Solving**: Search-o1, Marco-o1

**Sources:** [README.md:139-193](), [src/table.md:40-84]()

---

## Part 5: Self-Training and Self-Improvement

### Overview

Self-training methods enable LLMs to bootstrap their own reasoning capabilities by generating training data from their own outputs, iteratively improving without extensive human supervision.

### Core Methods

| Method | Year | Approach |
|--------|------|----------|
| Expert Iteration | 2017 | Tree search + imitation learning foundation |
| STaR | 2022 | Bootstrap from correct reasoning chains |
| ReST | 2023 | Reinforced self-training with RL |
| V-star | 2024 | Train verifiers for self-taught reasoning |
| Quiet-STaR | 2024 | Internal thought generation before speaking |
| rStar-Math | 2025 | Self-evolved deep thinking |

### Self-Training Loop

```mermaid
graph TB
    subgraph "Self-Training Cycle"
        INIT["Initial Model<br/>Base LLM or SFT model"]
        GEN["Generate Solutions<br/>Sample multiple attempts"]
        FILTER["Filter & Verify<br/>Select correct solutions"]
        TRAIN["Train on Filtered Data<br/>Fine-tune model"]
        IMPROVED["Improved Model"]
    end
    
    subgraph "Verification Methods"
        EXEC["Execution Verification<br/>Run code, check math"]
        VERIFY_MODEL["Verifier Model<br/>V-star approach"]
        SELF_EVAL["Self-Evaluation<br/>Model judges itself"]
    end
    
    INIT --> GEN
    GEN --> FILTER
    
    EXEC --> FILTER
    VERIFY_MODEL --> FILTER
    SELF_EVAL --> FILTER
    
    FILTER --> TRAIN
    TRAIN --> IMPROVED
    IMPROVED --> GEN
```

**Diagram: Self-Training Bootstrap Loop**

### Key Variants

**STaR (Self-Taught Reasoner):**
- Generate reasoning chains for training problems
- Filter for correct final answers
- Fine-tune on successful chains
- Rationalize failures with hints

**ReST (Reinforced Self-Training):**
- Combine self-training with RL
- Use expected reward for sample filtering
- Alternate between generation and training

**V-star:**
- Train verifier models alongside generators
- Use verifiers to guide solution selection
- Improves reliability of filtering

**rStar-Math:**
- Self-evolve reasoning depth
- Use code execution for verification
- No external verification models needed

### Integration with Other Methods

- **With MCTS**: ReST-MCTS* uses tree search to generate diverse training data
- **With PRMs**: Process rewards guide which steps to learn from
- **With RL**: ReST combines self-training with reinforcement learning

**Sources:** [README.md:194-224](), [src/table.md:85-102]()

---

## Part 6: Reflection

### Overview

Reflection mechanisms enable LLMs to critique, evaluate, and refine their own reasoning steps through self-correction. This meta-cognitive capability allows models to detect and fix errors without external intervention.

### Core Approaches

| Method | Date | Technique |
|--------|------|-----------|
| Self-Refine | 2023-12 | Iterative refinement with self-feedback |
| CRITIC | 2024-05 | Tool-interactive critiquing |
| SelfCheck | 2023-08 | Zero-shot step verification |
| Learning From Mistakes | 2023-10 | Error-aware training |
| Reflection-Tuning | 2023-10 | Data recycling through reflection |

### Reflection Architecture

```mermaid
graph TB
    subgraph "Reflection Loop"
        GEN["Generate Initial Response<br/>Chain-of-thought reasoning"]
        EVAL["Self-Evaluation<br/>Critique own work"]
        DETECT["Error Detection<br/>Identify problematic steps"]
        REFINE["Refinement<br/>Correct identified errors"]
        FINAL["Final Response<br/>Improved output"]
    end
    
    subgraph "Evaluation Methods"
        SELF_PROMPT["Self-Prompting<br/>'Is this correct?'"]
        TOOL["Tool Verification<br/>Code exec, search"]
        CONTRAST["Contrastive Reasoning<br/>Compare alternatives"]
    end
    
    GEN --> EVAL
    
    SELF_PROMPT --> EVAL
    TOOL --> EVAL
    CONTRAST --> EVAL
    
    EVAL --> DETECT
    DETECT --> REFINE
    REFINE --> FINAL
    
    DETECT -.iterate if errors.-> EVAL
```

**Diagram: Reflection and Self-Correction Loop**

### Multimodal Reflection

Recent work extends reflection to vision-language models:

- **LLaVA-o1**: Step-by-step reasoning with reflection in vision tasks
- **Vision-Language Models Can Self-Improve**: Reflection for VLM reasoning
- **Mulberry**: O1-like reasoning with collective MCTS and reflection

### Key Challenges

**Limitations:**
- Models may not reliably detect their own errors
- Reflection adds computational cost
- Risk of over-correction or infinite loops
- Requires careful prompting or training

**Success Factors:**
- Tool access for ground truth verification
- Strong base model capabilities
- Multiple reasoning attempts for comparison
- Explicit training on error detection

**Sources:** [README.md:225-241](), [src/table.md:103-111]()

---

## Technical Integration Patterns

### ReST-MCTS* Example

The ReST-MCTS* system exemplifies how multiple methodologies integrate:

```mermaid
graph TB
    subgraph "ReST-MCTS* Pipeline"
        POLICY["Policy Model π_θ"]
        
        subgraph "MCTS Phase - Part 4"
            SEARCH["Tree Search<br/>Explore reasoning paths"]
            PRM_GUIDE["Process Reward Model<br/>Guide exploration - Part 2"]
        end
        
        subgraph "Data Collection"
            TRAJ["Collect Trajectories<br/>High-reward paths"]
            FILTER["Filter Quality<br/>PRM-based selection"]
        end
        
        subgraph "Training Phase"
            RL_UPDATE["RL Training - Part 3<br/>Update policy"]
            PRM_UPDATE["Update PRM - Part 2<br/>From new data"]
            SELF_TRAIN["Self-Training - Part 5<br/>Bootstrap improvements"]
        end
    end
    
    POLICY --> SEARCH
    PRM_GUIDE --> SEARCH
    SEARCH --> TRAJ
    TRAJ --> FILTER
    PRM_GUIDE --> FILTER
    
    FILTER --> RL_UPDATE
    FILTER --> PRM_UPDATE
    FILTER --> SELF_TRAIN
    
    RL_UPDATE --> POLICY
    PRM_UPDATE --> PRM_GUIDE
    SELF_TRAIN --> POLICY
```

**Diagram: ReST-MCTS* Integration Pattern**

This shows how Parts 2 (PRM), 3 (RL), 4 (MCTS), and 5 (Self-Training) work together in a unified system.

**Sources:** [README.md:78](), [README.md:175](), [README.md:212]()

---

## Methodology Summary Table

| Part | Primary Role | Training/Inference | Key Papers | Integration Points |
|------|-------------|-------------------|------------|-------------------|
| **1. O1 Replication** | Target architecture | Both | DeepSeek-R1, Kimi k1.5 | Synthesizes all methods |
| **2. Process Rewards** | Step verification | Both | Math-Shepherd, PRMBench | Guides 3,4,5 |
| **3. Reinforcement Learning** | Policy optimization | Training | DeepSeek-R1, GRPO | Uses 2, enables 1 |
| **4. MCTS/Tree Search** | Path exploration | Inference | ReST-MCTS*, rStar-Math | Uses 2, feeds 5 |
| **5. Self-Training** | Data bootstrapping | Training | STaR, ReST, V-star | Uses 2,4, enables 1 |
| **6. Reflection** | Self-correction | Inference | Self-Refine, CRITIC | Complements 4 |

**Sources:** [README.md:45-241]()

---

## Evolution Timeline by Methodology

| Year | O1 Replication | Process Rewards | RL | MCTS | Self-Training | Reflection |
|------|---------------|-----------------|----|----|---------------|-----------|
| 2017 | - | - | - | - | Expert Iteration | - |
| 2022 | - | Outcome feedback | - | - | STaR | - |
| 2023 | - | Let's Verify | - | RAP, AlphaZero-like | ReST, Self-Refine | Self-Refine, CRITIC |
| 2024 | Journey begins | Math-Shepherd, AutoPSV | DeepSeekMath | MindStar, ReST-MCTS* | Quiet-STaR, V-star | Learning From Mistakes |
| 2025 | DeepSeek-R1, Kimi k1.5 | PRMBench, ReARTeR | DeepScaleR, LIMR | rStar-Math, Search-o1 | rStar-Math | Multimodal reflection |

**Sources:** [README.md:45-241]()

---

## Repository Organization

The six core methodologies are organized in the repository structure:

**Data Layer (`assets/paper.json`):**
- Contains structured metadata for ~256 papers
- Organized by part labels: `"Part 1: O1 Replication"` through `"Part 6: Reflection"`
- Each paper includes: title, authors, venue, date, links

**Documentation Layer (`README.md`):**
- Lines 45-67: Part 1 entries
- Lines 68-96: Part 2 entries  
- Lines 98-137: Part 3 entries
- Lines 139-193: Part 4 entries
- Lines 194-224: Part 5 entries
- Lines 225-241: Part 6 entries

**Generated Views:**
- `src/table.md`: Tabular format sorted by date
- `src/list.md`: List format with venue badges

**Sources:** [README.md:45-241](), [src/table.md:1-149]()

---

## Key Takeaways

1. **O1 Replication** (Part 1) is the synthesis target, integrating all other methodologies
2. **Process Reward Models** (Part 2) serve as the foundation, guiding both training and inference
3. **Reinforcement Learning** (Part 3) enables policy optimization for reasoning capabilities
4. **MCTS/Tree Search** (Part 4) provides inference-time exploration and planning
5. **Self-Training** (Part 5) bootstraps improvements without extensive human annotation
6. **Reflection** (Part 6) adds meta-cognitive self-correction capabilities

These six methodologies are not independent but form an integrated ecosystem where:
- PRMs guide RL training, MCTS exploration, and self-training data filtering
- MCTS generates diverse data for self-training loops
- RL optimizes policies that benefit from all other components
- Reflection complements tree search for error correction

For detailed information about specific implementations, see the individual part sections above. For optimization techniques, see [Efficient System2](#5.1). For evaluation frameworks, see [Benchmarks and Datasets](#7.1).

**Sources:** [README.md:14-26](), [README.md:45-241]()

---

# Page: O1 Replication

# O1 Replication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/list.md](src/list.md)

</details>



## Purpose and Scope

This page documents **Part 1: O1 Replication** from the System 2 reasoning research taxonomy. It covers efforts to reproduce, understand, and extend OpenAI's o1 model and similar advanced reasoning systems that exhibit slow, deliberate thinking capabilities. This includes academic papers, open-source implementations, technical reports, and production-scale systems like DeepSeek-R1 and Kimi k1.5.

O1 replication represents the aspirational target that synthesizes multiple core methodologies. For information on the individual component techniques, see:
- Process Reward Models: [#4.2](#4.2)
- Reinforcement Learning: [#4.3](#4.3)
- MCTS and Tree Search: [#4.4](#4.4)
- Self-Training and Self-Improvement: [#4.5](#4.5)
- Reflection Mechanisms: [#4.6](#4.6)

For optimization techniques applied to reasoning systems, see [Efficient System2](#5.1).

**Sources:** [README.md:45-67](), [README.md:14-18]()

## What is O1 Replication?

O1 replication refers to efforts to recreate or approximate the reasoning capabilities demonstrated by OpenAI's o1 model, which exhibits expert-level performance in mathematics, coding, and scientific reasoning through extended chain-of-thought reasoning. Unlike traditional LLMs that generate responses through single-pass autoregressive decoding (System 1), o1-like systems engage in multi-step deliberation, verification, and self-correction (System 2).

The defining characteristics of o1-like systems include:

| Characteristic | Description | Implementation Approach |
|----------------|-------------|------------------------|
| **Long Chain-of-Thought** | Extended reasoning traces (often thousands of tokens) | Training on long CoT data, RL with length rewards |
| **Test-Time Scaling** | Performance improves with more inference compute | Tree search, best-of-N sampling, iterative refinement |
| **Step-wise Verification** | Validation of intermediate reasoning steps | Process reward models (PRMs), self-verification |
| **Self-Correction** | Detection and correction of errors during generation | Reflection mechanisms, backtracking in search trees |
| **Multi-Method Integration** | Combination of RL, search, and self-training | Unified training pipelines, hybrid architectures |

**Sources:** [README.md:45-67](), [assets/paper.json:2-45]()

## Research Timeline and Evolution

```mermaid
timeline
    title O1 Replication Research Timeline (2024-2025)
    
    2024-10 : O1 Replication Journey Part 1
            : Strategic progress report
            : First systematic study
    
    2024-11 : Multiple approaches emerge
            : Marco-o1 (open reasoning models)
            : Reward-guided tree search
            : O1-Coder (domain-specific)
    
    2024-12 : Reproduction reports
            : Imitate Explore Self-Improve
            : HuatuoGPT-o1 (medical)
            : DRT (translation reasoning)
    
    2025-01 : Production-scale systems
            : DeepSeek-R1 (RL at scale)
            : Kimi k1.5 (scaled RL)
            : rStar-Math (self-evolved)
            : Open-source frameworks (Open R1 TinyZero)
    
    2025-02 : Continued innovation
            : X-R1 LLM-R1
            : Logic-RL
            : Open-Reasoner-Zero
```

**Sources:** [README.md:45-67](), [README.md:26]()

## Major Research Papers and Projects

### Academic Reproduction Studies

The following table catalogs key academic papers attempting to understand and replicate o1's capabilities:

| Paper | Date | Key Contribution | Venue |
|-------|------|------------------|-------|
| O1 Replication Journey Part 1 | 2024-10 | First strategic analysis and progress report | arXiv |
| O1 Replication Journey Part 2 | 2024-11 | Distillation approach, surpassing o1-preview | arXiv |
| Imitate, Explore, Self-Improve | 2024-12 | Three-phase reproduction framework | arXiv |
| Marco-o1 | 2024-11 | Open reasoning models for open-ended solutions | arXiv |
| Enhancing LLM Reasoning with Reward-guided Tree Search | 2024-11 | Integration of search and rewards | arXiv |

**Sources:** [assets/paper.json:2-45](), [README.md:47-51]()

### Domain-Specific Replications

O1-like reasoning has been adapted to specialized domains:

```mermaid
graph TB
    O1["OpenAI o1<br/>General Reasoning"]
    
    subgraph "Domain Adaptations"
        CODE["o1-Coder<br/>arXiv 2024-12<br/>Coding tasks"]
        MED["HuatuoGPT-o1<br/>arXiv 2024-12<br/>Medical reasoning"]
        TRANS["DRT<br/>arXiv 2024-12<br/>Translation reasoning"]
        MATH["rStar-Math<br/>arXiv 2025-01<br/>Mathematical reasoning"]
        SEARCH["Search-o1<br/>arXiv 2025-01<br/>Agentic search"]
    end
    
    O1 --> CODE
    O1 --> MED
    O1 --> TRANS
    O1 --> MATH
    O1 --> SEARCH
    
    style O1 fill:#f9f,stroke:#333,stroke-width:4px
```

**Sources:** [README.md:52-54](), [README.md:60-61](), [assets/paper.json:25-30]()

### Production-Scale Systems

Two major production systems have been released that achieve o1-like reasoning capabilities:

#### DeepSeek-R1

```mermaid
graph LR
    subgraph "DeepSeek-R1 Architecture"
        BASE["DeepSeek-V3<br/>Base Model"]
        RL["Reinforcement Learning<br/>GRPO Algorithm<br/>Pure RL without SFT"]
        COLD["Cold Start<br/>From scratch<br/>No reasoning data"]
        EMERGENT["Emergent Capabilities<br/>Aha moments<br/>Self-verification"]
        R1["DeepSeek-R1<br/>Production System"]
    end
    
    BASE --> COLD
    COLD --> RL
    RL --> EMERGENT
    EMERGENT --> R1
    
    subgraph "Related Implementations"
        MINI["mini-deepseek-r1<br/>Blog 2025-01<br/>Lightweight reproduction"]
        DYNAMIC["Dynamic 1.58-bit<br/>Blog 2025-01<br/>Quantized inference"]
        UNLOCK["Unlock-Deepseek<br/>Blog 2025-02<br/>Analysis"]
    end
    
    R1 -.inspires.-> MINI
    R1 -.inspires.-> DYNAMIC
    R1 -.inspires.-> UNLOCK
```

DeepSeek-R1 demonstrated that pure reinforcement learning (without supervised fine-tuning on reasoning data) can incentivize complex reasoning behaviors. The model learns to:
- Generate long chains of thought spontaneously
- Perform self-verification and error correction
- Exhibit "aha moments" where reasoning breakthroughs occur

**Implementation References:**
- Core approach: `DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning` (arXiv 2025-01)
- Lightweight reproduction: `mini-deepseek-r1` blog (2025-01)
- Quantization: `Run DeepSeek R1 Dynamic 1.58-bit` blog (2025-01)

#### Kimi k1.5

Kimi k1.5 represents another production-scale approach to scaling reinforcement learning for reasoning:

```mermaid
graph TB
    KIMI["Kimi k1.5<br/>Scaling RL with LLMs<br/>arXiv 2025-01"]
    
    subgraph "Key Features"
        SCALE["Large-scale RL<br/>Infrastructure"]
        MULTI["Multi-task<br/>Reasoning"]
        PROD["Production<br/>Deployment"]
    end
    
    KIMI --> SCALE
    KIMI --> MULTI
    KIMI --> PROD
```

**Sources:** [README.md:107-108](), [assets/paper.json:183-188]()

### Open-Source Frameworks

Several open-source implementations have emerged to democratize o1-like capabilities:

| Framework | Type | Description | Reference |
|-----------|------|-------------|-----------|
| `Open R1` | GitHub | Hugging Face's open replication | [README.md:59]() |
| `TinyZero` | GitHub | Lightweight implementation | [README.md:58]() |
| `Simple RL for Reasoning` | Notion | HKUST-NLP framework | [README.md:57]() |
| `Open-Reasoner-Zero` | PDF/GitHub | Complete replication report | [README.md:63]() |
| `X-R1` | GitHub | Extended R1 implementation | [README.md:64]() |
| `LLM-R1` | GitHub | LMM-R1 variant | [README.md:67]() |

**Sources:** [README.md:55-67]()

## Core Methodologies in O1 Replication

O1 replication efforts integrate multiple techniques. The following diagram shows how these components interact:

```mermaid
graph TB
    subgraph "Data Sources"
        HUMAN["Human-Written<br/>CoT Data"]
        SYNTH["Synthetic<br/>Self-Generated"]
        VERIFY["Verified<br/>Solutions"]
    end
    
    subgraph "Training Components"
        SFT["Supervised<br/>Fine-Tuning"]
        PRM["Process Reward<br/>Models"]
        RL_TRAIN["Reinforcement<br/>Learning<br/>PPO/GRPO/DPO"]
        SELF_TRAIN["Self-Training<br/>Loops"]
    end
    
    subgraph "Inference-Time Components"
        MCTS["Monte Carlo<br/>Tree Search"]
        SEARCH["Beam/Tree<br/>Search"]
        REFLECT["Reflection &<br/>Self-Correction"]
        VERIFY_INF["Step-wise<br/>Verification"]
    end
    
    subgraph "Output"
        O1_LIKE["O1-like<br/>Reasoning System"]
    end
    
    HUMAN --> SFT
    SYNTH --> SELF_TRAIN
    VERIFY --> PRM
    
    SFT --> RL_TRAIN
    PRM --> RL_TRAIN
    PRM --> VERIFY_INF
    SELF_TRAIN --> RL_TRAIN
    
    RL_TRAIN --> O1_LIKE
    MCTS --> O1_LIKE
    SEARCH --> O1_LIKE
    REFLECT --> O1_LIKE
    VERIFY_INF --> O1_LIKE
    
    O1_LIKE -.generates.-> SYNTH
```

**Sources:** [README.md:45-67](), [README.md:68-97](), [README.md:98-138](), [README.md:139-194]()

### Integration Patterns

Different replication efforts combine these techniques in various ways:

#### Pattern 1: Pure RL (DeepSeek-R1 Style)

```mermaid
graph LR
    BASE["Base LLM"] --> RL["Pure RL<br/>No CoT SFT"] --> EMERGENT["Emergent<br/>Reasoning"]
```

- No supervised fine-tuning on reasoning traces
- Relies on reward signal to discover reasoning strategies
- Exhibits emergent self-verification behaviors

#### Pattern 2: Distillation (O1 Journey Part 2)

```mermaid
graph LR
    O1_OUTPUTS["o1 Outputs<br/>Reasoning Traces"] --> DISTILL["Distillation<br/>Training"] --> STUDENT["Student Model<br/>O1-like Performance"]
```

- Train on outputs from original o1 model
- Simpler than from-scratch RL
- Can surpass teacher with proper training

#### Pattern 3: Imitate-Explore-Improve

```mermaid
graph LR
    IMITATE["Phase 1:<br/>Imitate<br/>SFT on CoT"] --> EXPLORE["Phase 2:<br/>Explore<br/>MCTS/Search"] --> IMPROVE["Phase 3:<br/>Self-Improve<br/>RL on collected data"]
```

- Three-phase approach combining multiple methods
- Gradual capability building
- Documented in reproduction report

**Sources:** [README.md:47-51](), [README.md:107](), [assets/paper.json:4-43]()

## Repository Artifacts and Data Organization

The repository catalogs O1 replication research through structured data:

```mermaid
graph TB
    JSON["assets/paper.json<br/>Structured metadata<br/>12 categories"]
    
    subgraph "Part 1 Data Structure"
        PAPERS["papers array<br/>6 core papers"]
        METADATA["Metadata fields:<br/>- paper (title)<br/>- link (URL)<br/>- venue<br/>- date<br/>- label (citation key)"]
    end
    
    JSON --> PAPERS
    PAPERS --> METADATA
    
    subgraph "Generated Views"
        README["README.md:45-67<br/>Human-curated descriptions<br/>Rich context"]
        LIST["src/list.md:1-7<br/>Chronologically sorted<br/>Badge indicators"]
    end
    
    JSON --> README
    JSON --> LIST
    
    README -.references.-> METADATA
    LIST -.references.-> METADATA
```

### Data Structure for O1 Replication Papers

The structured paper metadata in `assets/paper.json` follows this schema:

```json
{
  "Part 1: O1 Replication": [
    {
      "paper": "Paper Title",
      "link": "https://arxiv.org/abs/...",
      "venue": "arXiv|ACL|NeurIPS|...",
      "date": "YYYY-MM",
      "label": "citationkey"
    }
  ]
}
```

Key papers are stored at [assets/paper.json:2-45]() with 6 core academic papers and additional entries in the README for blogs and GitHub projects.

**Sources:** [assets/paper.json:1-45](), [src/list.md:1-7]()

## Technical Challenges and Open Problems

### Computational Cost

O1-like systems require significant test-time compute:

| Approach | Tokens/Query | Time Multiplier | Trade-off |
|----------|--------------|-----------------|-----------|
| Standard LLM | 100-500 | 1x | Fast, less accurate |
| O1-like (short) | 1,000-5,000 | 10-50x | Moderate cost, better reasoning |
| O1-like (long) | 10,000-100,000+ | 100-1000x | High cost, best reasoning |

Solutions being explored:
- **O1-Pruner**: Length harmonization and pruning [README.md:254]()
- **DynaThink**: Dynamic fast/slow routing [README.md:246]()
- **Token budgeting**: Adaptive reasoning depth [README.md:248]()

For detailed optimization techniques, see [Efficient System2](#5.1).

### Training Challenges

```mermaid
graph TB
    subgraph "Training Challenges"
        DATA["Data Scarcity<br/>Limited reasoning traces"]
        REWARD["Reward Design<br/>Hard to specify"]
        STAB["Training Stability<br/>RL variance"]
        LENGTH["Length Control<br/>Over/under-thinking"]
    end
    
    subgraph "Solutions"
        SYNTH["Synthetic Data<br/>Self-generation"]
        PRM_SOL["Process Rewards<br/>Step-wise signals"]
        ALGO["Advanced Algorithms<br/>GRPO DPO"]
        PRUNING["Pruning Methods<br/>Length harmonization"]
    end
    
    DATA --> SYNTH
    REWARD --> PRM_SOL
    STAB --> ALGO
    LENGTH --> PRUNING
```

**Sources:** [README.md:242-325](), [README.md:98-138]()

## Relationships to Other Research Areas

O1 replication synthesizes and depends on multiple research areas:

```mermaid
graph TB
    O1["O1 Replication<br/>Part 1"]
    
    PRM["Process Reward Models<br/>Part 2<br/>Step-wise supervision"]
    RL["Reinforcement Learning<br/>Part 3<br/>PPO GRPO DPO"]
    MCTS["MCTS/Tree Search<br/>Part 4<br/>Exploration planning"]
    SELF["Self-Training<br/>Part 5<br/>Bootstrapping"]
    REFLECT["Reflection<br/>Part 6<br/>Self-correction"]
    
    PRM -.provides.-> O1
    RL -.trains.-> O1
    MCTS -.enables.-> O1
    SELF -.improves.-> O1
    REFLECT -.enhances.-> O1
    
    O1 -.evaluated by.-> BENCH["Benchmarks<br/>Part 10<br/>MR-Ben FrontierMath"]
    O1 -.constrained by.-> SAFETY["Safety<br/>Part 11<br/>Alignment"]
    O1 -.optimized by.-> EFF["Efficient System2<br/>Part 7<br/>Token budgeting"]
    
    O1 -.extended to.-> MM["Multimodal<br/>Parts 9 12<br/>Vision-language"]
```

**Cross-references:**
- **Process Reward Models** ([#4.2](#4.2)): Provide step-wise supervision signals
- **Reinforcement Learning** ([#4.3](#4.3)): Training methodology (DeepSeek-R1, Kimi k1.5)
- **MCTS/Tree Search** ([#4.4](#4.4)): Inference-time exploration (rStar-Math, Search-o1)
- **Self-Training** ([#4.5](#4.5)): Bootstrap reasoning capabilities
- **Reflection** ([#4.6](#4.6)): Self-correction mechanisms
- **Efficient System2** ([#5.1](#5.1)): Computational optimization
- **Benchmarks** ([#7.1](#7.1)): Evaluation frameworks
- **Safety** ([#7.2](#7.2)): Alignment considerations

**Sources:** [README.md:26-416]()

## Notable Research Findings

### Emergent Behaviors in Pure RL

DeepSeek-R1 demonstrated that reinforcement learning without supervised fine-tuning on reasoning data can lead to:

1. **Spontaneous long-chain reasoning**: Models learn to "think before answering" without explicit instruction
2. **Self-verification**: Models develop habits of checking their work
3. **Aha moments**: Sudden breakthroughs in reasoning during inference
4. **Language mixing**: Reasoning in multiple languages during thought process

These findings suggest that reasoning capabilities may emerge from optimization pressure rather than requiring explicit training on reasoning traces.

### Test-Time Scaling Laws

Research on o3-mini and related systems reveals that:
- Performance scales with inference compute budget
- Longer reasoning traces correlate with higher accuracy on complex problems
- There exists an optimal length for different problem types (avoiding overthinking)

Documented in: "The Relationship Between Reasoning and Performance in Large Language Models -- o3 (mini) Thinks Harder, Not Longer" [README.md:62]()

### Distillation Effectiveness

The O1 Replication Journey Part 2 showed that:
- Student models can surpass teacher (o1-preview) through distillation
- Simpler training procedure than pure RL from scratch
- Raises questions about "bitter lesson" vs. "big progress"

**Sources:** [README.md:50](), [README.md:62](), [README.md:107]()

## Implementation Resources

### Getting Started

For practitioners looking to implement o1-like reasoning:

1. **Start with reproduction studies**: Read O1 Replication Journey Part 1 and Part 2
2. **Choose framework**: Consider Open R1, TinyZero, or Simple RL for Reasoning
3. **Understand dependencies**: Study process reward models and RL techniques
4. **Start small**: Begin with domain-specific adaptation (coding, math) before general reasoning

### Key Implementation Components

```mermaid
graph TB
    subgraph "Minimal O1 Implementation"
        BASE["Base LLM<br/>Llama Qwen etc"]
        
        TRAIN_DATA["Training Data<br/>CoT examples<br/>OR pure RL"]
        
        REWARD_SYS["Reward System<br/>Outcome rewards<br/>OR process rewards"]
        
        RL_ALGO["RL Algorithm<br/>PPO GRPO DPO"]
        
        INFERENCE["Inference System<br/>Best-of-N<br/>OR tree search"]
    end
    
    BASE --> TRAIN_DATA
    TRAIN_DATA --> RL_ALGO
    REWARD_SYS --> RL_ALGO
    RL_ALGO --> MODEL_OUT["Trained Model"]
    MODEL_OUT --> INFERENCE
    INFERENCE --> OUTPUT["Long CoT<br/>Reasoning"]
```

**Sources:** [README.md:55-67]()

## Future Directions

The O1 replication research continues to evolve with several open directions:

1. **Efficiency**: Reducing computational cost while maintaining reasoning quality
2. **Interpretability**: Understanding what reasoning models actually do internally (see [Explainability](#5.2))
3. **Multimodal reasoning**: Extending to vision-language tasks (see [Multimodal Extensions](#6))
4. **Robustness**: Ensuring consistent performance across domains
5. **Safety**: Preventing misuse and ensuring alignment (see [Reasoning and Safety](#7.2))

### Active Research Questions

- Can smaller models (1-3B parameters) achieve o1-like reasoning with sufficient training?
- What is the optimal balance between pre-training, SFT, and RL for reasoning?
- How can we reduce test-time compute without sacrificing accuracy?
- Can reasoning capabilities transfer across domains effectively?

**Sources:** [README.md:242-325](), [README.md:327-338]()

---

# Page: Process Reward Models

# Process Reward Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/list.md](src/list.md)

</details>



## Purpose and Scope

Process Reward Models (PRMs) provide **step-by-step supervision** of reasoning processes, assigning rewards or verification scores to individual intermediate steps rather than only evaluating final outcomes. This fine-grained feedback mechanism enables more effective training and inference-time guidance for System 2 reasoning tasks.

This document covers the research and techniques for building, training, and applying PRMs as cataloged in Part 2 of the repository. For reinforcement learning methods that consume these rewards, see [Reinforcement Learning](#4.3). For tree search algorithms guided by PRMs, see [MCTS and Tree Search](#4.4). For self-training methods that leverage process supervision, see [Self-Training and Self-Improvement](#4.5).

**Sources:** [README.md:68-96]()

## Process vs. Outcome Supervision

```mermaid
graph TB
    subgraph "Outcome Reward Models (ORM)"
        INPUT_ORM["Question + Full Solution"]
        ORM["Outcome Reward Model"]
        FINAL_SCORE["Single Score<br/>Correct/Incorrect"]
    end
    
    subgraph "Process Reward Models (PRM)"
        INPUT_PRM["Question + Reasoning Chain"]
        STEP1["Step 1: Setup"]
        STEP2["Step 2: Calculation"]
        STEP3["Step 3: Conclusion"]
        PRM1["PRM"]
        PRM2["PRM"]
        PRM3["PRM"]
        SCORE1["Score: 0.9"]
        SCORE2["Score: 0.3<br/>ERROR DETECTED"]
        SCORE3["Score: 0.7"]
    end
    
    INPUT_ORM --> ORM
    ORM --> FINAL_SCORE
    
    INPUT_PRM --> STEP1
    INPUT_PRM --> STEP2
    INPUT_PRM --> STEP3
    STEP1 --> PRM1 --> SCORE1
    STEP2 --> PRM2 --> SCORE2
    STEP3 --> PRM3 --> SCORE3
    
    FINAL_SCORE -.limited feedback.-> INPUT_ORM
    SCORE2 -.precise error localization.-> STEP2
```

**Key Distinction**: ORMs evaluate only the final answer, while PRMs provide supervision at each reasoning step. This granular feedback enables:
- **Error Localization**: Identify which step introduced a mistake
- **Credit Assignment**: Reward correct intermediate reasoning even if the final answer is wrong
- **Guided Search**: Use step-level scores to prune search trees during inference
- **Better Training Signals**: More supervision per training example

**Sources:** [README.md:70-76](), [assets/paper.json:90-94]()

## Repository Data Structure

```mermaid
graph TB
    subgraph "assets/paper.json Structure"
        ROOT["paper.json"]
        PART2["'Part 2: Process Reward Models'<br/>Array of Papers"]
        
        PAPER1["Paper Object 1:<br/>Math-Shepherd"]
        PAPER2["Paper Object 2:<br/>ReST-MCTS*"]
        PAPER3["Paper Object 3:<br/>AutoPSV"]
        PAPER4["Paper Object 4:<br/>PRMBench"]
        PAPERN["... 27 total papers"]
        
        FIELDS["Fields:<br/>- paper: title<br/>- link: URL<br/>- venue: conference/journal<br/>- date: YYYY-MM<br/>- label: citation key"]
    end
    
    subgraph "Generated Outputs"
        README["README.md:68-96<br/>Part 2 Section"]
        LISTMD["src/list.md:8-23<br/>Sorted List View"]
        TABLEMD["src/table.md<br/>Tabular View"]
    end
    
    ROOT --> PART2
    PART2 --> PAPER1
    PART2 --> PAPER2
    PART2 --> PAPER3
    PART2 --> PAPER4
    PART2 --> PAPERN
    
    PAPER1 --> FIELDS
    
    PART2 -.processed by src/main.py.-> README
    PART2 -.processed by src/main.py.-> LISTMD
    PART2 -.processed by src/main.py.-> TABLEMD
```

The repository stores PRM research papers in a structured JSON format at [assets/paper.json:46-152](). Each paper entry contains metadata including title, venue, publication date, and a citation label. The `src/main.py` build script processes this data to generate multiple documentation views.

**Sources:** [assets/paper.json:46-152](), [src/list.md:8-23]()

## Core Research Directions

### Automated PRM Generation

```mermaid
graph LR
    subgraph "Manual Annotation (Expensive)"
        HUMAN["Human Experts"]
        MANUAL["Step-by-step Labels"]
        COST["High Cost, Low Scale"]
    end
    
    subgraph "Automated Methods"
        ORM["Outcome Reward Model"]
        MONTECARLO["Monte Carlo Estimation"]
        AUTOPSV["AutoPSV:<br/>Automated Process-Supervised Verifier"]
        MATHSHEP["Math-Shepherd:<br/>Automatic Annotation"]
        FREEPRM["Free Process Rewards<br/>without Process Labels"]
    end
    
    subgraph "Training Data"
        SYNTHETIC["Synthetic Solutions"]
        CORRECT["Correct Paths"]
        INCORRECT["Incorrect Paths"]
        PARTIAL["Partial Solutions"]
    end
    
    HUMAN --> MANUAL --> COST
    
    ORM --> MONTECARLO
    MONTECARLO --> MATHSHEP
    
    SYNTHETIC --> AUTOPSV
    CORRECT --> AUTOPSV
    INCORRECT --> AUTOPSV
    
    MATHSHEP --> PARTIAL
    AUTOPSV --> PARTIAL
    FREEPRM --> PARTIAL
```

**Key Innovations:**

| Paper | Method | Key Contribution |
|-------|--------|------------------|
| **Math-Shepherd** (ACL 2024) | Automatic annotation using correct/incorrect solution pairs | Eliminates need for human step-level labels |
| **AutoPSV** (NeurIPS 2024) | Automated process-supervised verifier training | Scalable verification without manual supervision |
| **Free Process Rewards** (arXiv 2024.12) | Derive process rewards without process labels | Extract implicit step-wise signals from outcome data |
| **Let's Verify Step by Step** (ICLR 2024.05) | Large-scale manual annotation study | Established that process supervision outperforms outcome supervision |

**Sources:** [README.md:70-96](), [assets/paper.json:48-137]()

### Verification and Scoring

```mermaid
graph TB
    subgraph "Step-wise Verification Pipeline"
        QUESTION["Input: Question"]
        CHAIN["Generated Chain-of-Thought"]
        
        PARSE["Parse into Steps"]
        STEP1["Step 1"]
        STEP2["Step 2"]
        STEPN["Step N"]
        
        VERIFY1["PRM Score"]
        VERIFY2["PRM Score"]
        VERIFYN["PRM Score"]
        
        AGG["Aggregation Strategy"]
        FINAL["Final Verification Score"]
    end
    
    subgraph "Scoring Strategies"
        MIN["Minimum Score<br/>(Most Conservative)"]
        PROD["Product of Scores"]
        WEIGHTED["Weighted Average"]
        ENTROPY["Entropy-Guided<br/>Multi-head Aggregation"]
    end
    
    QUESTION --> CHAIN
    CHAIN --> PARSE
    PARSE --> STEP1
    PARSE --> STEP2
    PARSE --> STEPN
    
    STEP1 --> VERIFY1
    STEP2 --> VERIFY2
    STEPN --> VERIFYN
    
    VERIFY1 --> AGG
    VERIFY2 --> AGG
    VERIFYN --> AGG
    
    MIN --> AGG
    PROD --> AGG
    WEIGHTED --> AGG
    ENTROPY --> AGG
    
    AGG --> FINAL
```

**Verification Techniques:**

- **Step-Aware Verifier** (arXiv 2023.06): Position-aware scoring considering step context
- **OVM** (ACL Findings 2024): Outcome-supervised value models for planning
- **Step-DPO** (arXiv 2024.06): Step-wise preference optimization for long-chain reasoning
- **Uncertainty-Aware Verification** (arXiv 2025.02): Incorporate model confidence in step scoring
- **AdaptiveStep** (arXiv 2025.02): Automatically divide reasoning steps based on model confidence
- **Bi-directional Rewarding** (arXiv 2025.03): Forward and backward signal propagation

**Sources:** [README.md:72-96](), [assets/paper.json:69-95]()

### Benchmarking Process Rewards

```mermaid
graph TB
    subgraph "PRMBench: Fine-grained Benchmark"
        DATASET["PRMBench Dataset"]
        STEPANNO["Step-level Annotations"]
        DIVERSE["Diverse Domains:<br/>Math, Code, Reasoning"]
        CHALLENGE["Challenging Cases:<br/>Subtle Errors"]
    end
    
    subgraph "ToolComp: Tool Reasoning"
        TOOLDATA["Multi-Tool Scenarios"]
        PROCESS["Process Supervision"]
        TOOLEVAL["Tool Use Evaluation"]
    end
    
    subgraph "Evaluation Metrics"
        STEPACC["Step Accuracy"]
        ERRORDET["Error Detection Rate"]
        LOCALIZE["Error Localization Precision"]
        DOWNSTREAM["Downstream Task Performance"]
    end
    
    DATASET --> STEPANNO
    STEPANNO --> DIVERSE
    DIVERSE --> CHALLENGE
    
    TOOLDATA --> PROCESS
    PROCESS --> TOOLEVAL
    
    CHALLENGE --> STEPACC
    CHALLENGE --> ERRORDET
    CHALLENGE --> LOCALIZE
    
    TOOLEVAL --> DOWNSTREAM
    CHALLENGE --> DOWNSTREAM
```

**Key Benchmarks:**

| Benchmark | Focus | Publication |
|-----------|-------|-------------|
| **PRMBench** | Fine-grained process-level evaluation across domains | arXiv 2025.01 |
| **ToolComp** | Multi-tool reasoning with process supervision | arXiv 2025.01 |
| **RewardBench** | General reward model evaluation | arXiv 2024.03 |
| **Multimodal RewardBench** | Vision-language reward models | arXiv 2025.02 |

**Sources:** [README.md:81-85](), [assets/paper.json:139-151]()

## Domain-Specific Applications

```mermaid
graph TB
    subgraph "Mathematical Reasoning"
        MATH["Math Problems"]
        MATHSHEP["Math-Shepherd"]
        DEEPSEEKMATH["DeepSeekMath"]
        RSTAR["rStar-Math"]
    end
    
    subgraph "Code Generation"
        CODE["Programming Tasks"]
        OUTCOMEREF["Outcome-Refining Process<br/>Supervision for Code"]
        CODECRITIC["Code Error Detection"]
    end
    
    subgraph "Multimodal"
        VL["Vision-Language Tasks"]
        UNIFIED["Unified Reward Model for<br/>Multimodal Understanding"]
        MMREWARD["Multimodal RewardBench"]
    end
    
    subgraph "Agents and Planning"
        AGENTS["Autonomous Agents"]
        ARMAP["ARMAP: Automatic<br/>Reward Modeling & Planning"]
        TOOLCOMP["ToolComp"]
    end
    
    MATH --> MATHSHEP
    MATH --> DEEPSEEKMATH
    MATH --> RSTAR
    
    CODE --> OUTCOMEREF
    CODE --> CODECRITIC
    
    VL --> UNIFIED
    VL --> MMREWARD
    
    AGENTS --> ARMAP
    AGENTS --> TOOLCOMP
```

**Sources:** [README.md:79-92](), [assets/paper.json:125-151]()

## Integration with Other Methodologies

```mermaid
graph TB
    subgraph "Process Reward Models (Part 2)"
        PRM["PRM Training"]
        PRMINFER["PRM Inference"]
    end
    
    subgraph "Reinforcement Learning (Part 3)"
        RL["RL Training"]
        GRPO["GRPO/PPO"]
        DEEPSEEKR1["DeepSeek-R1"]
        KIMIK15["Kimi k1.5"]
    end
    
    subgraph "MCTS/Tree Search (Part 4)"
        MCTS["Monte Carlo Tree Search"]
        RESTMCTS["ReST-MCTS*"]
        TREESEARCH["Value-Guided Tree Search"]
    end
    
    subgraph "Self-Training (Part 5)"
        STAR["STaR"]
        REST["ReST"]
        VSTAR["V-star"]
    end
    
    PRM --> RL
    PRM --> MCTS
    PRM --> STAR
    
    PRMINFER --> RESTMCTS
    PRMINFER --> TREESEARCH
    
    PRM --> GRPO
    GRPO --> DEEPSEEKR1
    GRPO --> KIMIK15
    
    RESTMCTS --> REST
    
    PRM --> VSTAR
```

**Integration Patterns:**

1. **PRM + Reinforcement Learning**: Process rewards serve as the reward signal for RL training
   - DeepSeek-R1 uses process-level rewards in RL training
   - Kimi k1.5 scales RL with step-wise supervision
   - GRPO (Group Relative Policy Optimization) leverages process rewards

2. **PRM + MCTS**: Step-level scores guide tree search exploration
   - ReST-MCTS* combines process reward guidance with tree search
   - Value-guided MCTS uses PRMs as value functions
   - Search-o1 enhances reasoning with PRM-guided search

3. **PRM + Self-Training**: PRMs select high-quality reasoning traces
   - V-star trains verifiers alongside self-taught reasoners
   - ReST uses process verification for filtering
   - rStar-Math self-evolves using PRM feedback

**Sources:** [README.md:68-225](), Diagram 2 from high-level architecture

## Research Evolution Timeline

```mermaid
timeline
    title Process Reward Model Research Evolution
    
    2022-11 : Solving Math Word Problems<br/>Process and Outcome-Based Feedback
    
    2023-06 : Step-Aware Verifier<br/>Automated Process Supervision<br/>Manual annotations at scale
    
    2024-05 : Let's Verify Step by Step (ICLR)<br/>Established process > outcome supervision
    
    2024-06 : Step-DPO<br/>Long-chain reasoning optimization
    
    2024-08 : Math-Shepherd (ACL)<br/>Automatic annotation breakthrough<br/>OVM for planning
    
    2024-12 : AutoPSV (NeurIPS)<br/>ReST-MCTS* (NeurIPS)<br/>Free Process Rewards<br/>Outcome-Refining for Code
    
    2025-01 : PRMBench<br/>ReARTeR<br/>Lessons of Developing PRMs<br/>ToolComp benchmark
    
    2025-02 : Agentic Reward Modeling<br/>Unified Multimodal Rewards<br/>Reward Shaping<br/>Multi-head Aggregation<br/>Uncertainty-Aware Verification
    
    2025-03 : Bi-directional Rewarding<br/>Better Process Supervision
    
    2025-04 : Inference-Time Scaling for<br/>Generalist Reward Modeling
```

**Key Inflection Points:**
- **2023**: Establishment of process supervision superiority over outcome-only
- **2024**: Automated PRM generation (Math-Shepherd, AutoPSV) enabling scale
- **2024 Q4**: Integration with tree search (ReST-MCTS*) and RL systems
- **2025**: Multimodal expansion and specialized benchmarking

**Sources:** [README.md:68-96](), [assets/paper.json:46-152]()

## Representative Papers

| Category | Paper | Venue/Date | Key Contribution |
|----------|-------|------------|------------------|
| **Foundation** | Let's Verify Step by Step | ICLR 2024.05 | Demonstrated process supervision superiority with large-scale study |
| **Automated Generation** | Math-Shepherd | ACL 2024 | Automatic step-by-step annotation without human labels |
| **Automated Generation** | AutoPSV | NeurIPS 2024 | Scalable automated process-supervised verifier |
| **Automated Generation** | Free Process Rewards | arXiv 2024.12 | Extract process signals from outcome data only |
| **Integration** | ReST-MCTS* | NeurIPS 2024 | Combined with tree search for self-training |
| **Optimization** | Step-DPO | arXiv 2024.06 | Step-wise preference optimization |
| **Planning** | OVM | ACL Findings 2024 | Outcome-supervised value models for reasoning |
| **Benchmarking** | PRMBench | arXiv 2025.01 | Fine-grained evaluation benchmark |
| **Benchmarking** | ToolComp | arXiv 2025.01 | Multi-tool reasoning and process supervision |
| **Retrieval** | ReARTeR | arXiv 2025.01 | Retrieval-augmented with trustworthy process rewards |
| **Analysis** | Lessons of Developing PRMs | arXiv 2025.01 | Comprehensive study of PRM development practices |
| **Multimodal** | Unified Reward Model | arXiv 2025.02 | Multimodal understanding and generation rewards |
| **Agents** | ARMAP | ICLR 2025 | Automatic reward modeling for autonomous agents |
| **Uncertainty** | Uncertainty-Aware Verification | arXiv 2025.02 | Generative reward models with uncertainty |
| **Adaptive** | AdaptiveStep | arXiv 2025.02 | Automatic reasoning step division via confidence |
| **Architecture** | Multi-head Reward Aggregation | arXiv 2025.03 | Entropy-guided aggregation strategies |
| **Bidirectional** | Better Process Supervision | arXiv 2025.03 | Bi-directional rewarding signals |
| **Inference-Time** | Inference-Time Scaling | arXiv 2025.04 | Generalist reward modeling at test time |

**Sources:** [README.md:68-96](), [assets/paper.json:46-152](), [src/list.md:8-23]()

## Training and Inference Patterns

```mermaid
graph TB
    subgraph "Training-Time Usage"
        TRAIN_DATA["Training Data:<br/>Question + Solution + Labels"]
        PRM_TRAIN["Train PRM Model"]
        
        SFT["Supervised Fine-Tuning"]
        RL_TRAIN["RL Training<br/>(GRPO, PPO, DPO)"]
        SELF_TRAIN["Self-Training Loop"]
    end
    
    subgraph "Inference-Time Usage"
        INFERENCE["New Question"]
        GENERATE["Generate Candidate Solutions"]
        
        BEAM["Beam Search"]
        SAMPLE["Sampling"]
        MCTS_INF["MCTS Exploration"]
        
        PRM_SCORE["PRM Scoring"]
        SELECT["Select Best Solution"]
        VERIFY["Error Detection"]
    end
    
    TRAIN_DATA --> PRM_TRAIN
    
    PRM_TRAIN --> SFT
    PRM_TRAIN --> RL_TRAIN
    PRM_TRAIN --> SELF_TRAIN
    
    INFERENCE --> GENERATE
    GENERATE --> BEAM
    GENERATE --> SAMPLE
    GENERATE --> MCTS_INF
    
    BEAM --> PRM_SCORE
    SAMPLE --> PRM_SCORE
    MCTS_INF --> PRM_SCORE
    
    PRM_SCORE --> SELECT
    PRM_SCORE --> VERIFY
```

**Training-Time Applications:**
- **Reward Signal for RL**: PRMs provide dense rewards for each reasoning step during policy optimization
- **Data Filtering**: Select high-quality reasoning traces for supervised fine-tuning
- **Curriculum Learning**: Gradually increase difficulty based on PRM-assessed complexity

**Inference-Time Applications:**
- **Best-of-N Selection**: Score N sampled solutions and select highest-scoring
- **Tree Search Guidance**: Use PRM scores to guide MCTS exploration and pruning
- **Error Detection**: Identify and potentially correct erroneous steps
- **Beam Search**: Prune low-scoring reasoning paths during generation

**Sources:** [README.md:68-96](), Diagram 3 from high-level architecture

## Challenges and Open Problems

**Scalability Issues:**
- Manual annotation remains expensive; automated methods still developing
- Training PRMs requires large datasets of step-labeled reasoning chains
- Generalization across domains (math, code, science) remains difficult

**Technical Challenges:**
- **Granularity**: Determining optimal step size for supervision
- **Credit Assignment**: Accurately attributing errors to specific steps
- **Robustness**: PRMs can be brittle to small perturbations in reasoning style
- **Reward Hacking**: Models may learn to game PRM scores without improving reasoning

**Current Research Directions (2025):**
- Inference-time scaling with generalist reward models
- Multimodal process rewards for vision-language reasoning  
- Agentic reward modeling integrating human preferences with verifiable signals
- Reward shaping to mitigate hacking behaviors
- Uncertainty quantification in process scoring

**Sources:** [README.md:86-96]()

## Related Work in Other Parts

Process Reward Models intersect heavily with other research areas in the repository:

- **[O1 Replication](#4.1)**: O1-like systems rely on PRMs for training and inference
- **[Reinforcement Learning](#4.3)**: PRMs provide the reward signal for RL training (DeepSeek-R1, Kimi k1.5)
- **[MCTS and Tree Search](#4.4)**: PRMs guide exploration in tree search algorithms (ReST-MCTS*, rStar-Math)
- **[Self-Training and Self-Improvement](#4.5)**: PRMs enable self-verification and data filtering (V-star, ReST)
- **[Benchmarks and Datasets](#7.1)**: PRMBench, ToolComp, and other evaluation frameworks
- **[Reasoning and Safety](#7.2)**: Process supervision for alignment and safety considerations

**Sources:** [README.md:26-416](), Diagram 2 from high-level architecture

---

# Page: Reinforcement Learning

# Reinforcement Learning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/table.md](src/table.md)

</details>



## Purpose and Scope

This page documents reinforcement learning (RL) techniques for training reasoning capabilities in Large Language Models. Reinforcement learning enables LLMs to learn complex, multi-step reasoning through interaction with reward signals, moving beyond pure supervised learning approaches. This section covers policy optimization algorithms (PPO, DPO, GRPO), large-scale RL implementations like DeepSeek-R1 and Kimi k1.5, and the integration of RL with process reward models and self-training.

For process-level supervision that guides RL training, see [Process Reward Models](#4.2). For self-training approaches that can complement RL, see [Self-Training and Self-Improvement](#4.5). For computational efficiency of RL-trained models, see [Efficient System2](#5.1).

**Sources:** [README.md:98-138]()

---

## Overview: RL's Role in System 2 Reasoning

Reinforcement learning serves as a critical bridge between supervised fine-tuning and emergent reasoning capabilities. Unlike traditional SFT which requires extensive human-annotated reasoning traces, RL can optimize models directly for reasoning quality using outcome-based or process-based rewards. The key insight is that RL allows models to explore the space of reasoning strategies and self-discover effective patterns.

```mermaid
graph TB
    subgraph "Input: Base Model"
        BASE["Pre-trained LLM<br/>(System 1 capabilities)"]
        SFT["Supervised Fine-Tuning<br/>(Initial CoT examples)"]
    end
    
    subgraph "RL Training Loop"
        POLICY["Policy Model<br/>(Generates reasoning)"]
        REWARD["Reward Model<br/>(Evaluates quality)"]
        UPDATE["Policy Update<br/>(PPO/DPO/GRPO)"]
    end
    
    subgraph "Output: Reasoning Model"
        REASONING["Reasoning-Enhanced LLM<br/>(System 2 capabilities)"]
        INFERENCE["Inference-Time<br/>Multi-step thinking"]
    end
    
    BASE --> SFT
    SFT --> POLICY
    POLICY -->|"Generate reasoning traces"| REWARD
    REWARD -->|"Compute gradients"| UPDATE
    UPDATE -->|"Optimize policy"| POLICY
    POLICY -->|"Converged"| REASONING
    REASONING --> INFERENCE
    
    style BASE fill:#f9f9f9
    style REASONING fill:#e8e8e8
    style POLICY fill:#f0f0f0
```

**Diagram: RL Training Pipeline for Reasoning Models**

The training process involves iteratively generating reasoning traces, evaluating them with reward models, and updating the policy to maximize expected rewards. This enables the discovery of reasoning patterns that may not appear in supervised datasets.

**Sources:** [README.md:98-138](), [README.md:14-26]()

---

## Key RL Approaches and Algorithms

### Policy Optimization Methods

Modern reasoning models employ several RL algorithms, each with distinct characteristics:

| Algorithm | Type | Key Characteristic | Representative Papers |
|-----------|------|-------------------|----------------------|
| **PPO** (Proximal Policy Optimization) | On-policy | Stable updates via clipping | DeepSeek-R1, Kimi k1.5 |
| **DPO** (Direct Preference Optimization) | Offline | Learns from preference pairs | ReFT |
| **GRPO** (Group Relative Policy Optimization) | Hybrid | Relative rewards within groups | DeepSeek-R1 |
| **Offline RL** | Offline | Learns from fixed datasets | Offline Reinforcement Learning for LLM Multi-Step Reasoning |

**Sources:** [README.md:98-138]()

### Technical Architecture

```mermaid
graph LR
    subgraph "RL Training Components"
        ACTOR["Actor Network<br/>(Policy π_θ)"]
        CRITIC["Critic Network<br/>(Value V or Q)"]
        PRM["Process Reward Model<br/>(Step-level feedback)"]
        ORM["Outcome Reward Model<br/>(Final result)"]
    end
    
    subgraph "Training Data Flow"
        QUERY["Query/Problem"]
        TRAJECTORY["Reasoning Trajectory<br/>(s₁, a₁, s₂, a₂, ...)"]
        REWARD_SIGNAL["Reward Signal<br/>(Process + Outcome)"]
    end
    
    subgraph "Update Mechanism"
        ADVANTAGE["Advantage Estimation<br/>(A = Q - V)"]
        GRADIENT["Policy Gradient<br/>(∇θ J(θ))"]
        OPTIMIZER["Optimizer<br/>(Adam, etc.)"]
    end
    
    QUERY --> ACTOR
    ACTOR --> TRAJECTORY
    TRAJECTORY --> PRM
    TRAJECTORY --> ORM
    PRM --> REWARD_SIGNAL
    ORM --> REWARD_SIGNAL
    REWARD_SIGNAL --> CRITIC
    CRITIC --> ADVANTAGE
    ADVANTAGE --> GRADIENT
    GRADIENT --> OPTIMIZER
    OPTIMIZER --> ACTOR
    
    style ACTOR fill:#f5f5f5
    style PRM fill:#f0f0f0
    style ORM fill:#f0f0f0
```

**Diagram: RL Training Architecture with Process and Outcome Rewards**

The architecture combines actor-critic methods with both process-level and outcome-level reward signals. Process rewards (from PRMs) provide dense feedback at each reasoning step, while outcome rewards evaluate final correctness.

**Sources:** [README.md:98-138](), [README.md:68-97]()

---

## Major Implementations

### DeepSeek-R1: Large-Scale RL for Reasoning

DeepSeek-R1 represents a breakthrough in scaling RL to reasoning tasks, demonstrating that pure RL can incentivize sophisticated reasoning without extensive supervised reasoning data.

**Key Papers:**
- **DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning** [README.md:107]()
- **Deepseekmath: Pushing the limits of mathematical reasoning in open language models** [README.md:109]()

**Technical Characteristics:**
- Uses **GRPO** (Group Relative Policy Optimization) for stable training
- Scales to billions of parameters with distributed RL
- Combines cold-start exploration with iterative refinement
- Integrates process rewards for step-wise guidance

```mermaid
graph TB
    subgraph "DeepSeek-R1 Training Pipeline"
        BASE_DS["DeepSeek Base Model"]
        WARM["Warm-up Phase<br/>(Limited SFT)"]
        RL_GRPO["GRPO Training<br/>(Group-relative rewards)"]
        REFINE["Iterative Refinement<br/>(Policy improvement)"]
    end
    
    subgraph "Reward Sources"
        MATH_VERIFY["Mathematical Verification<br/>(Symbolic execution)"]
        CODE_EXEC["Code Execution<br/>(Unit tests)"]
        PROCESS_R["Process Rewards<br/>(Step correctness)"]
    end
    
    subgraph "Output Capabilities"
        MATH_REASON["Mathematical Reasoning"]
        CODE_GEN["Code Generation"]
        LONG_COT["Long-form CoT"]
    end
    
    BASE_DS --> WARM
    WARM --> RL_GRPO
    
    MATH_VERIFY --> RL_GRPO
    CODE_EXEC --> RL_GRPO
    PROCESS_R --> RL_GRPO
    
    RL_GRPO --> REFINE
    REFINE --> MATH_REASON
    REFINE --> CODE_GEN
    REFINE --> LONG_COT
    
    style RL_GRPO fill:#e8e8e8
```

**Diagram: DeepSeek-R1 Training Architecture**

**Sources:** [README.md:107-109]()

### Kimi k1.5: Scaling RL with LLMs

Kimi k1.5 demonstrates another approach to scaling RL for reasoning, with emphasis on inference-time computation.

**Key Paper:**
- **Kimi k1.5: Scaling Reinforcement Learning with LLMs** [README.md:108]()

**Technical Approach:**
- Focuses on **inference scaling** where reasoning length adapts to problem difficulty
- Uses RL to learn when to extend reasoning vs. conclude
- Integrates with tree search methods for exploration

**Sources:** [README.md:108]()

---

## Integration with Other Techniques

### RL + Process Reward Models

The combination of RL with Process Reward Models (PRMs) creates a powerful training paradigm:

```mermaid
graph TB
    subgraph "Training Data Generation"
        MODEL["Current Policy π_θ"]
        SAMPLE["Sample Trajectories<br/>(T = {s₁, a₁, ..., sₙ, aₙ})"]
        LABEL["PRM Labels<br/>(Per-step correctness)"]
    end
    
    subgraph "Reward Computation"
        STEP_REWARD["Step Rewards<br/>(r₁, r₂, ..., rₙ)"]
        CUMULATIVE["Cumulative Return<br/>(R = Σ γⁱ rᵢ)"]
        ADVANTAGE_CALC["Advantage A(s,a)"]
    end
    
    subgraph "Policy Update"
        PPO_OBJ["PPO Objective<br/>(Clipped surrogate)"]
        GRADIENT_STEP["Gradient Update"]
        NEW_POLICY["Updated Policy π_θ'"]
    end
    
    MODEL --> SAMPLE
    SAMPLE --> LABEL
    LABEL --> STEP_REWARD
    STEP_REWARD --> CUMULATIVE
    CUMULATIVE --> ADVANTAGE_CALC
    ADVANTAGE_CALC --> PPO_OBJ
    PPO_OBJ --> GRADIENT_STEP
    GRADIENT_STEP --> NEW_POLICY
    NEW_POLICY -->|"Iterate"| MODEL
    
    style LABEL fill:#f0f0f0
    style PPO_OBJ fill:#e8e8e8
```

**Diagram: RL Training Loop with Process Reward Guidance**

Key papers demonstrating this integration:
- **ReST-MCTS*: LLM Self-Training via Process Reward Guided Tree Search** [README.md:78]() - Combines tree search, PRMs, and self-training
- **Math-Shepherd: Verify and Reinforce LLMs Step-by-step** [README.md:73]() - Automated PRM generation for RL

**Sources:** [README.md:68-97](), [README.md:78]()

### RL + Tree Search (MCTS)

Reinforcement learning and Monte Carlo Tree Search create synergistic combinations. See [MCTS and Tree Search](#4.4) for detailed coverage. Key integration points:

- **Value-Guided MCTS**: RL-trained value functions guide tree exploration
- **Policy-Guided MCTS**: RL policies provide prior probabilities for action selection
- **MCTS as Data Augmentation**: Tree search generates high-quality trajectories for RL training

**Representative Papers:**
- **MAKING PPO EVEN BETTER: VALUE-GUIDED MONTE-CARLO TREE SEARCH DECODING** [README.md:146]()
- **Monte Carlo Tree Search Boosts Reasoning via Iterative Preference Learning** [README.md:154]()

**Sources:** [README.md:139-193]()

---

## RL Algorithm Details

### Representation Finetuning (ReFT)

ReFT offers an efficient alternative to full model finetuning:

**Key Paper:** **ReFT: Representation Finetuning for Language Models** [README.md:103](), [README.md:216]()

**Technical Approach:**
- Finetunes only **learned linear transformations** on frozen model representations
- Significantly reduces trainable parameters compared to full RL
- Can be applied with various RL objectives (PPO, DPO)
- Maintains model capabilities while improving reasoning

**Sources:** [README.md:103]()

### Offline RL for Multi-Step Reasoning

Offline RL enables learning from fixed datasets without online interaction:

**Key Paper:** **Offline Reinforcement Learning for LLM Multi-Step Reasoning** [README.md:102]()

**Advantages:**
- Avoids costly online sampling and reward computation
- Can leverage existing reasoning datasets
- More stable training than online methods
- Suitable for scenarios where online evaluation is expensive

**Technical Approach:**
- Learns from pre-collected trajectories with rewards
- Uses conservative Q-learning or implicit Q-learning to avoid overestimation
- Handles distribution shift between behavior and learned policy

**Sources:** [README.md:102]()

---

## Advanced RL Techniques

### Chain-of-Action-Thought (Satori)

**Satori: Reinforcement Learning with Chain-of-Action-Thought** [README.md:113]() introduces a novel paradigm combining action planning with reasoning.

**Technical Innovation:**
- Integrates **action sequences** into reasoning chains
- RL learns to select both reasoning steps and actions
- Enables **autoregressive search** through action space
- Applies to agent tasks and complex problem-solving

```mermaid
graph LR
    subgraph "Traditional CoT"
        THOUGHT1["Think"]
        THOUGHT2["Think"]
        THOUGHT3["Think"]
        ANSWER["Answer"]
    end
    
    subgraph "Chain-of-Action-Thought"
        THINK_A["Think"]
        ACT_A["Act"]
        THINK_B["Think"]
        ACT_B["Act"]
        FINAL["Answer"]
    end
    
    THOUGHT1 --> THOUGHT2
    THOUGHT2 --> THOUGHT3
    THOUGHT3 --> ANSWER
    
    THINK_A --> ACT_A
    ACT_A --> THINK_B
    THINK_B --> ACT_B
    ACT_B --> FINAL
    
    style ACT_A fill:#e8e8e8
    style ACT_B fill:#e8e8e8
```

**Diagram: CoT vs. Chain-of-Action-Thought**

**Sources:** [README.md:113]()

### Scaling Laws and Compute Efficiency

Several papers investigate how RL scales with compute:

| Paper | Key Finding | Citation |
|-------|-------------|----------|
| **Does RLHF Scale?** | Examines scaling behavior of RLHF across data, model size, and method | [README.md:101]() |
| **Advancing Language Model Reasoning** | Studies inference scaling with RL | [README.md:105]() |
| **DeepScaleR** | Achieves o1-preview performance with 1.5B model via scaled RL | [README.md:114]() |
| **LIMR: Less is More for RL Scaling** | Demonstrates efficient RL with reduced compute | [README.md:115]() |

**Sources:** [README.md:101-138]()

---

## Multimodal RL Extensions

RL techniques extend to multimodal reasoning tasks:

### Vision-Language RL

**Key Papers:**
- **Improve Vision Language Model Chain-of-thought Reasoning** [README.md:100]()
- **MM-RLHF: The Next Step Forward in Multimodal LLM Alignment** [README.md:112]()
- **Visual-RFT: Visual Reinforcement Fine-Tuning** [README.md:123]()
- **R1-Zero's "Aha Moment" in Visual Reasoning** [README.md:122]()

**Technical Extensions:**
- Applies RL to vision-language models (VLMs)
- Rewards based on visual grounding accuracy
- Handles multimodal reasoning chains (vision → text → vision)

### Agent RL

**Key Papers:**
- **UI-R1: Enhancing Action Prediction of GUI Agents** [README.md:120]()
- **GTR: Guided Thought Reinforcement** [README.md:124]()
- **VideoChat-R1: Enhancing Spatio-Temporal Perception** [README.md:133]()

**Application Domains:**
- GUI interaction and web navigation
- Video understanding and reasoning
- Embodied agent tasks

**Sources:** [README.md:100-138]()

---

## Safety and Alignment Challenges

### RL Safety Concerns

**Challenges in Ensuring AI Safety in DeepSeek-R1 Models** [README.md:106]() highlights critical safety issues:

**Key Concerns:**
- **Reward Hacking**: Models exploit reward model weaknesses
- **Goal Misgeneralization**: RL optimizes for proxies rather than true objectives
- **Safety-Capability Tradeoffs**: Reasoning improvements may reduce safety alignment
- **Harmful Reasoning**: Models may learn to generate harmful reasoning chains

### Mitigation Strategies

```mermaid
graph TB
    subgraph "Safety Interventions"
        SAFE_REWARD["Safety-Aware Rewards<br/>(Multi-objective)"]
        CONST_RL["Constrained RL<br/>(Hard safety constraints)"]
        ADVERSARIAL["Adversarial Testing<br/>(Red-teaming)"]
        MONITOR["Online Monitoring<br/>(Detect issues)"]
    end
    
    subgraph "Training Process"
        RL_TRAIN["RL Training"]
        SAFETY_CHECK["Safety Evaluation"]
        DEPLOY_GATE["Deployment Gate"]
    end
    
    subgraph "Outcomes"
        SAFE_MODEL["Safe Reasoning Model"]
        ROLLBACK["Rollback if unsafe"]
    end
    
    SAFE_REWARD --> RL_TRAIN
    CONST_RL --> RL_TRAIN
    RL_TRAIN --> ADVERSARIAL
    ADVERSARIAL --> SAFETY_CHECK
    SAFETY_CHECK --> MONITOR
    MONITOR --> DEPLOY_GATE
    DEPLOY_GATE -->|"Pass"| SAFE_MODEL
    DEPLOY_GATE -->|"Fail"| ROLLBACK
    
    style SAFETY_CHECK fill:#e8e8e8
    style DEPLOY_GATE fill:#e8e8e8
```

**Diagram: RL Safety Framework**

For comprehensive coverage of safety issues, see [Reasoning and Safety](#7.2).

**Sources:** [README.md:106](), [README.md:437-456]()

---

## Domain-Specific RL Applications

### Medical Reasoning

**Med-RLVR: Emerging Medical Reasoning from a 3B base model** [README.md:117]() demonstrates RL for medical domain:

**Approach:**
- RL training on medical QA tasks
- Reward models based on medical accuracy
- Emerges complex medical reasoning from small base models

### Machine Translation

**MT-R1-Zero: Advancing LLM-based Machine Translation** [README.md:136]() applies R1-style RL to translation:

**Innovation:**
- RL for translation quality optimization
- Reasoning-aware translation strategies
- Multi-step refinement of translations

### Code Generation

Multiple papers apply RL to code reasoning:
- **Process Reinforcement through Implicit Rewards** [README.md:119]()
- **Algorithm Discovery With LLMs** [README.md:131]()

**Sources:** [README.md:117-137]()

---

## Training Dynamics and Optimization

### Curriculum Learning

**Efficient Reinforcement Finetuning via Adaptive Curriculum Learning** [README.md:132]() introduces adaptive curricula for RL:

**Key Ideas:**
- Start with easier reasoning problems
- Progressively increase difficulty
- Adapt curriculum based on model performance
- Improves sample efficiency and final performance

### Reinforcement Learning Fundamentals

The theoretical foundation connects to classical RL objectives:

**Policy Gradient Objective:**
```
J(θ) = E[τ~π_θ] [Σ_t γ^t r_t]
```

Where:
- `θ`: Policy parameters
- `τ`: Trajectory (reasoning chain)
- `γ`: Discount factor
- `r_t`: Reward at step t (from PRM or outcome)

**PPO Update Rule:**
```
L^CLIP(θ) = E_t [min(r_t(θ)Â_t, clip(r_t(θ), 1-ε, 1+ε)Â_t)]
```

Where:
- `r_t(θ)`: Probability ratio (new/old policy)
- `Â_t`: Advantage estimate
- `ε`: Clipping parameter (typically 0.2)

**Sources:** [README.md:98-138]()

---

## Research Frontiers

### Recent Developments (2025)

```mermaid
graph LR
    subgraph "Jan 2025"
        DSR1["DeepSeek-R1"]
        KIMI["Kimi k1.5"]
    end
    
    subgraph "Feb 2025"
        SATORI["Satori<br/>(CoA-T)"]
        DEEPSCALER["DeepScaleR<br/>(1.5B model)"]
        LIMR["LIMR"]
    end
    
    subgraph "Mar 2025"
        L1["L1<br/>(Reasoning length control)"]
        VLAA["VLAA-Thinker"]
        GTR["GTR<br/>(Thought collapse prevention)"]
    end
    
    subgraph "Apr 2025"
        D1["d1<br/>(Diffusion LLMs)"]
        VIDEOCHAT["VideoChat-R1"]
        VISRL["VisRL"]
    end
    
    DSR1 --> SATORI
    KIMI --> SATORI
    SATORI --> L1
    DEEPSCALER --> VLAA
    L1 --> D1
    GTR --> VIDEOCHAT
    
    style DSR1 fill:#e8e8e8
    style KIMI fill:#e8e8e8
```

**Diagram: Recent RL Research Timeline (2025)**

### Emerging Directions

1. **Controlling Reasoning Length**: **L1: Controlling How Long A Reasoning Model Thinks** [README.md:125]()
2. **Diffusion-Based RL**: **d1: Scaling Reasoning in Diffusion Large Language Models** [README.md:130]()
3. **Thought Collapse Prevention**: **GTR: Guided Thought Reinforcement** [README.md:124]()
4. **Small Model RL**: **Reinforcement Learning for Reasoning in Small LLMs** [README.md:126]()

**Sources:** [README.md:98-138]()

---

## Implementation Considerations

### Compute Requirements

| Model Scale | Training Compute | Typical Configuration | Reference |
|-------------|------------------|----------------------|-----------|
| 1-3B params | 100-500 GPU-hours | 8-16 A100 GPUs | Med-RLVR, DeepScaleR |
| 7-13B params | 1K-5K GPU-hours | 32-64 A100 GPUs | Various implementations |
| 70B+ params | 10K-100K GPU-hours | 256+ A100 GPUs | DeepSeek-R1, Kimi k1.5 |

### Training Stability

Key techniques for stable RL training:
- **Reward Clipping**: Prevent extreme reward values
- **Value Function Clipping**: Constrain value predictions
- **KL Penalty**: Regularize policy changes (stay close to SFT initialization)
- **Advantage Normalization**: Stabilize gradient magnitudes
- **Multiple Epochs per Batch**: Improve sample efficiency

### Hyperparameter Sensitivity

Critical hyperparameters requiring tuning:
- Learning rate (typically 1e-6 to 1e-5 for large models)
- PPO clip ratio ε (typically 0.1 to 0.3)
- Value function coefficient (0.5 to 1.0)
- Entropy bonus (0.01 to 0.1)
- Batch size and number of rollouts

**Sources:** [README.md:98-138]()

---

## Comparison with Alternative Approaches

### RL vs. Supervised Fine-Tuning

| Aspect | Supervised Fine-Tuning | Reinforcement Learning |
|--------|------------------------|------------------------|
| **Data Requirements** | Requires human-annotated reasoning | Can use automated rewards |
| **Exploration** | Limited to training distribution | Discovers novel strategies |
| **Scalability** | Bounded by annotation cost | Scales with compute |
| **Sample Efficiency** | High (learns from demonstrations) | Lower (requires exploration) |
| **Reasoning Quality** | Good on similar problems | Better on novel problems |

### RL vs. Self-Training

See [Self-Training and Self-Improvement](#4.5) for detailed comparison. Key differences:
- **RL**: Active exploration with reward-guided learning
- **Self-Training**: Passive filtering of self-generated data
- **Hybrid**: Many modern systems (e.g., ReST-MCTS*) combine both

**Sources:** [README.md:98-138](), [README.md:194-224]()

---

## Code and Implementation Resources

While this repository primarily catalogs research papers rather than providing implementations, the following resources are referenced:

### Open-Source Implementations

- **mini-deepseek-r1** [README.md:55]() - Blog on lightweight DeepSeek-R1 implementation
- **TinyZero** [README.md:58]() - GitHub implementation of RL training
- **Open R1** [README.md:59]() - HuggingFace's open RL implementation
- **Simple Reinforcement Learning for Reasoning** [README.md:57]() - HKUST-NLP's RL framework

### Training Frameworks

The papers reference various frameworks:
- **DeepSpeed** for distributed RL training (implied in large-scale papers)
- **TRL (Transformer Reinforcement Learning)** for PPO/DPO
- **Custom implementations** for specialized algorithms (GRPO, etc.)

**Sources:** [README.md:55-67]()

---

## Future Directions

### Open Research Questions

1. **Theoretical Understanding**: Why does RL induce reasoning? Mechanisms remain unclear.
2. **Scaling Laws**: How do RL scaling laws differ from pretraining/SFT?
3. **Sample Efficiency**: Can we match supervised learning efficiency?
4. **Reward Design**: What reward structures best incentivize reasoning?
5. **Safety Alignment**: How to maintain safety during RL optimization?

### Emerging Paradigms

- **Continuous Latent Reasoning**: Training models to reason in continuous spaces rather than discrete tokens
- **Multi-Agent RL**: Using multiple agents to discover diverse reasoning strategies
- **Meta-RL**: Learning to adapt RL strategies across problem domains
- **Hybrid Training**: Seamlessly combining RL with SFT and self-training

**Sources:** [README.md:98-138]()

---

## Summary

Reinforcement learning has emerged as a critical technique for training System 2 reasoning in LLMs. Key takeaways:

1. **Major Breakthroughs**: DeepSeek-R1 and Kimi k1.5 demonstrate that RL can scale to produce state-of-the-art reasoning models
2. **Algorithm Diversity**: PPO, DPO, GRPO, and offline RL offer different tradeoffs for reasoning tasks
3. **Integration Synergies**: RL combines powerfully with process reward models, tree search, and self-training
4. **Safety Challenges**: RL introduces unique alignment challenges requiring careful mitigation
5. **Rapid Evolution**: The field is evolving rapidly with new techniques emerging monthly in 2025

The transition from supervised learning to reinforcement learning represents a fundamental shift in how we train reasoning capabilities, moving from imitation to discovery-based learning.

**Sources:** [README.md:98-138](), [README.md:14-26]()

---

# Page: MCTS and Tree Search

# MCTS and Tree Search

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/list.md](src/list.md)

</details>



## Purpose and Scope

This page documents Monte Carlo Tree Search (MCTS) and related tree search algorithms as applied to Large Language Model reasoning. These techniques enable structured exploration of reasoning paths, combining search-based planning with neural language generation to achieve System 2 thinking capabilities.

**Scope**: This page covers MCTS algorithms, tree search variants (e.g., best-first search, beam search with backtracking), value-guided decoding, and their application to LLM reasoning tasks. For process-level supervision that guides these searches, see [Process Reward Models](#4.2). For self-training methods that utilize MCTS-generated data, see [Self-Training and Self-Improvement](#4.5). For computational optimization of tree search, see [Efficient System2](#5.1).

**Sources**: [README.md:35](), [README.md:139-193]()

---

## Conceptual Foundation

Monte Carlo Tree Search adapts game-playing algorithms (notably from AlphaGo/AlphaZero) to language model reasoning. Instead of searching discrete board states, MCTS explores the space of partial reasoning chains, using the LLM to generate candidate continuations and learned value functions to estimate their quality.

### Core MCTS Operations for LLMs

```mermaid
graph TB
    subgraph "MCTS Cycle"
        Root["Root State<br/>(Initial Problem)"]
        Selection["Selection Phase<br/>UCB-guided traversal<br/>to leaf node"]
        Expansion["Expansion Phase<br/>LLM generates<br/>k candidate steps"]
        Simulation["Simulation/Evaluation<br/>Value model scores<br/>or rollout to completion"]
        Backprop["Backpropagation<br/>Update node values<br/>along path"]
    end
    
    Root --> Selection
    Selection --> Expansion
    Expansion --> Simulation
    Simulation --> Backprop
    Backprop --> Selection
    
    subgraph "Node Structure"
        NodeState["Node.state:<br/>Partial reasoning chain"]
        NodeValue["Node.value:<br/>Estimated quality (Q)"]
        NodeVisits["Node.visits:<br/>Visit count (N)"]
        NodeChildren["Node.children:<br/>List[Node]"]
    end
    
    Selection -.uses.-> NodeValue
    Selection -.uses.-> NodeVisits
    Expansion -.creates.-> NodeChildren
    Simulation -.updates.-> NodeValue
    
    subgraph "Guiding Signals"
        PRM["Process Reward Model<br/>Step-wise quality"]
        ORM["Outcome Reward Model<br/>Final answer correctness"]
        ValueNet["Value Network<br/>State value estimation"]
        Policy["Policy Prior<br/>LLM probability"]
    end
    
    Simulation --> PRM
    Simulation --> ORM
    Simulation --> ValueNet
    Expansion --> Policy
```

**Key Differences from Game MCTS**:
- **State space**: Text sequences instead of board configurations
- **Actions**: Token sequences (reasoning steps) instead of discrete moves
- **Terminal states**: Solution verification rather than win/loss
- **Branching factor**: Controlled via top-k sampling rather than exhaustive
- **Evaluation**: Learned reward models or LLM self-verification

**Sources**: [README.md:141-145](), [assets/paper.json:220-239]()

---

## Major Algorithmic Variants

The field has developed several distinct approaches to tree search for LLM reasoning, each with specific design choices.

### Comparison of Key Methods

| Method | Guidance Signal | Training Data | Search Depth | Primary Use Case |
|--------|----------------|---------------|--------------|------------------|
| **RAP** (2023) | World model rewards | None (inference-only) | Fixed depth | Task planning, reasoning |
| **AlphaZero-LLM** (2023) | Self-play iterations | Generated trajectories | Full tree | Decoding optimization |
| **ReST-MCTS*** (2024) | Process reward model | Self-generated + filtering | Adaptive | Self-training pipeline |
| **rStar-Math** (2025) | Multi-code execution | Self-evolved data | Deep (iterative) | Mathematical reasoning |
| **MindStar** (2024) | Dual value models | None (inference-only) | Inference-time | Math problem solving |
| **TreeBoN** (2024) | Speculative search + BoN | Alignment data | Shallow tree | Inference-time alignment |
| **Mulberry** (2024) | Collective MCTS | Multimodal data | Collaborative | Vision-language reasoning |

**Sources**: [README.md:141-182](), [assets/paper.json:218-512]()

---

## ReST-MCTS*: Process-Reward Guided Self-Training

One of the most influential integration patterns combines MCTS with process reward models for iterative self-improvement.

```mermaid
graph LR
    subgraph "Training Iteration Loop"
        BasePolicy["Policy π<sub>i</sub><br/>(Current LLM)"]
        MCTS["MCTS Search<br/>Explore reasoning paths"]
        TreeData["Search Tree<br/>Trajectories + rewards"]
        FilterData["Filter Data<br/>Select high-quality paths"]
        TrainNext["Train π<sub>i+1</sub><br/>Next policy iteration"]
    end
    
    subgraph "Process Reward Model"
        PRM["PRM(s, a)<br/>Step-wise reward"]
        PRMData["Training:<br/>Math-Shepherd,<br/>AutoPSV"]
    end
    
    subgraph "MCTS Components"
        UCB["UCB Selection<br/>Q(s,a) + c·√(log N(s)/N(s,a))"]
        Expand["Expansion<br/>Policy π samples k actions"]
        Evaluate["Evaluation<br/>PRM scores + rollout"]
        Update["Backprop<br/>Update Q-values"]
    end
    
    BasePolicy --> MCTS
    MCTS --> UCB
    UCB --> Expand
    Expand --> Evaluate
    Evaluate --> Update
    Update --> TreeData
    
    PRM --> Evaluate
    PRMData -.trains.-> PRM
    
    TreeData --> FilterData
    FilterData --> TrainNext
    TrainNext --> BasePolicy
```

**Algorithm: ReST-MCTS* Core Loop**

1. **Initialization**: Start with policy π₀ and trained PRM
2. **Generation Phase** (per problem):
   - Run MCTS for N iterations
   - Each iteration: Select → Expand → Evaluate (using PRM) → Backprop
   - Extract best trajectory via tree traversal
3. **Filtering Phase**:
   - Retain only trajectories with correct final answers
   - Filter by PRM scores (keep top percentile)
4. **Training Phase**:
   - Fine-tune π₀ on filtered trajectories → π₁
   - Repeat for multiple iterations

**Key Design Choices**:
- **Process rewards over outcome**: PRM provides dense supervision at each step
- **Self-consistency filtering**: Only keep correct solutions to prevent error propagation
- **Iterative refinement**: Each policy iteration improves over previous

**Paper Reference**: "ReST-MCTS*: LLM Self-Training via Process Reward Guided Tree Search" (NeurIPS 2024)

**Sources**: [README.md:78](), [README.md:175](), [assets/paper.json:55-60](), [assets/paper.json:409-414]()

---

## rStar-Math: Self-Evolved Deep Thinking

A more recent approach eliminates reliance on human-annotated process rewards by using code execution as the verification signal.

```mermaid
graph TB
    subgraph "rStar-Math Pipeline"
        Init["Small Base LLM<br/>(e.g., 1.5B params)"]
        SFT["SFT on GSM8K<br/>+ MATH"]
        
        subgraph "Self-Evolution Loop"
            direction TB
            GenProblems["Generate<br/>Training Problems<br/>(4x difficulty)"]
            MCTS2["MCTS Search<br/>Multi-code execution"]
            VerifyCode["Code Verification<br/>Majority voting<br/>across solutions"]
            CollectData["Collect Verified<br/>Reasoning Traces"]
            TrainRL["RL Training<br/>(DPO/GRPO)"]
        end
        
        Deploy["Inference-Time<br/>MCTS Search"]
    end
    
    Init --> SFT
    SFT --> GenProblems
    GenProblems --> MCTS2
    MCTS2 --> VerifyCode
    VerifyCode --> CollectData
    CollectData --> TrainRL
    TrainRL --> GenProblems
    TrainRL --> Deploy
    
    subgraph "MCTS with Code Execution"
        CodeGen["Generate Code<br/>Solution"]
        Execute["Execute Code<br/>Multiple samples"]
        Vote["Majority Vote<br/>Determines correctness"]
    end
    
    MCTS2 --> CodeGen
    CodeGen --> Execute
    Execute --> Vote
    Vote --> VerifyCode
```

**Key Innovations**:
1. **Self-generated curriculum**: Model creates harder problems for itself
2. **Code as verifier**: Python execution provides ground-truth rewards
3. **Deep thinking at scale**: Small models (1.5B) achieve reasoning comparable to 10-100x larger models
4. **No human annotations**: Fully self-evolved from initial SFT checkpoint

**Paper Reference**: "rStar-Math: Small LLMs Can Master Math Reasoning with Self-Evolved Deep Thinking" (arXiv 2025-01)

**Sources**: [README.md:188](), [README.md:220](), [assets/paper.json:465-470]()

---

## Value-Guided Decoding

Several methods use learned value functions to guide tree search without full MCTS iterations, enabling efficient inference-time reasoning.

### MindStar Architecture

```mermaid
graph LR
    subgraph "Dual Value Model System"
        Problem["Input Problem"]
        
        subgraph "Policy Model"
            LLM["Base LLM<br/>Generates candidates"]
        end
        
        subgraph "Value Models"
            FastValue["Fast Value Model<br/>State-based Q(s)"]
            SlowValue["Slow Value Model<br/>Trajectory-based V(τ)"]
        end
        
        Search["Best-First Search<br/>Guided by Q(s)"]
        Prune["Pruning<br/>Low-value branches"]
        Rank["Final Ranking<br/>By V(τ)"]
        Output["Best Solution"]
    end
    
    Problem --> LLM
    LLM --> Search
    
    FastValue --> Search
    FastValue --> Prune
    
    Search --> SlowValue
    SlowValue --> Rank
    Rank --> Output
```

**Dual Value Approach**:
- **Fast value model**: Quickly estimates state quality for pruning
- **Slow value model**: Accurately evaluates complete trajectories for ranking
- **Separation of concerns**: Efficiency during search, accuracy during selection

**Sources**: [README.md:153](), [assets/paper.json:353-358]()

---

## Domain-Specific Applications

MCTS has been successfully adapted to various reasoning domains beyond pure mathematics.

### Application Matrix

| Domain | Paper | Key Adaptation | Search Strategy |
|--------|-------|----------------|-----------------|
| **Mathematical Reasoning** | AlphaMath Almost Zero | No process labels | Reward-free search |
| **Code Generation** | CodeTree, SRA-MCTS | Agent-guided expansion | Syntax-aware tree |
| **Olympiad Geometry** | Geometry MCTS | Symbolic constraints | Guided tree search |
| **Instruction Following** | SPaR | Refinement loops | Self-play search |
| **Multimodal Math** | AtomThink, Mulberry | Image + text states | Collective search |
| **Medical Reasoning** | HuatuoGPT-o1 | Domain knowledge | Specialized PRM |
| **Financial Analysis** | GPT-Guided MCTS | Symbolic regression | Domain-specific ops |

**Sources**: [README.md:151-182](), [assets/paper.json:423-477]()

---

## Integration with Other Methodologies

MCTS naturally combines with other System 2 reasoning techniques documented in this repository.

```mermaid
graph TB
    subgraph "MCTS Integration Patterns"
        MCTS_Core["MCTS<br/>Core Algorithm"]
        
        subgraph "Guidance Signals"
            PRM_Int["Process Rewards<br/>(Part 2)"]
            ORM_Int["Outcome Rewards<br/>(Part 3 - RL)"]
            Reflection["Reflection<br/>(Part 6)"]
        end
        
        subgraph "Training Loops"
            SelfTrain["Self-Training<br/>(Part 5)"]
            RL_Train["RL Training<br/>(Part 3)"]
        end
        
        subgraph "Optimization"
            Efficient["Token Budget<br/>(Part 7)"]
            Pruning["Early Pruning<br/>(Part 7)"]
        end
        
        subgraph "Extensions"
            Multimodal["Multimodal<br/>(Part 9, 12)"]
        end
    end
    
    PRM_Int --> MCTS_Core
    ORM_Int --> MCTS_Core
    Reflection --> MCTS_Core
    
    MCTS_Core --> SelfTrain
    MCTS_Core --> RL_Train
    
    MCTS_Core --> Efficient
    MCTS_Core --> Pruning
    
    MCTS_Core --> Multimodal
    
    SelfTrain -.generates data for.-> PRM_Int
    RL_Train -.learns.-> ORM_Int
```

### Cross-Part Connections

1. **MCTS + Process Rewards ([Part 2](#4.2))**:
   - Papers: ReST-MCTS*, Math-Shepherd, AutoPSV
   - Pattern: PRM provides per-step guidance for MCTS value estimation
   - Data flow: MCTS generates trajectories → PRM filters quality data

2. **MCTS + Self-Training ([Part 5](#4.5))**:
   - Papers: ReST-MCTS*, rStar-Math, STaR
   - Pattern: MCTS explores → Filter trajectories → Train next iteration
   - Closes the loop: Better policy → Better MCTS → Better data

3. **MCTS + Reinforcement Learning ([Part 3](#4.3))**:
   - Papers: DeepSeek-R1, Kimi k1.5 (implicitly use search)
   - Pattern: MCTS provides exploration, RL provides policy optimization
   - Integration: MCTS trajectories as RL training data

4. **MCTS + Reflection ([Part 6](#4.6))**:
   - Papers: Mulberry, Marco-o1, LLaMA-Berry
   - Pattern: MCTS nodes include self-critique steps
   - Enhancement: Reflection improves node expansion quality

5. **MCTS + Efficiency ([Part 7](#5.1))**:
   - Papers: O1-Pruner, DynaThink, Token-Budget-Aware
   - Pattern: Adaptive search depth, early termination
   - Tradeoff: Search breadth vs. computational cost

**Sources**: [README.md:32-43](), Multiple sections across README.md

---

## Research Evolution Timeline

```mermaid
timeline
    title MCTS for LLM Reasoning Evolution (2017-2025)
    
    2017 : Expert Iteration
         : MCTS + neural networks for RL
    
    2023 : Foundation Year
         : RAP - Reasoning as Planning
         : AlphaZero-like LLM decoding
         : Value-guided MCTS decoding
         : "Let's Verify Step by Step" (enables PRM-guided search)
    
    2024 : Integration & Specialization
         : ReST-MCTS* (Process + Self-training)
         : MindStar (Dual value models)
         : TreeBoN (Speculative search)
         : AlphaMath Almost Zero
         : Domain applications (CodeTree, Geometry MCTS)
         : Uncertainty-guided optimization
         : Multimodal MCTS (Mulberry)
    
    2025 : Self-Evolution Era
         : rStar-Math (Self-evolved deep thinking)
         : Search-o1 (Agentic search)
         : Production-scale deployments
```

### Capability Progression

| Period | Key Capability | Representative Work |
|--------|---------------|---------------------|
| **2017-2022** | Basic tree search for RL | Expert Iteration, STaR |
| **2023 Q1-Q2** | Task planning with world models | RAP, AlphaZero-LLM |
| **2023 Q3-Q4** | Value-guided decoding | Value-MCTS, PPO-MCTS |
| **2024 Q1-Q2** | Process-reward guided search | ReST-MCTS*, AlphaMath |
| **2024 Q3-Q4** | Domain specialization | CodeTree, Geometry MCTS, Mulberry |
| **2025 Q1+** | Self-evolved systems | rStar-Math, Search-o1 |

**Sources**: [README.md:139-193](), [assets/paper.json:218-512]()

---

## Representative Implementations

### RAP (Reasoning with Language Model is Planning with World Model)

**Core Idea**: Treat reasoning as sequential decision-making where LLM acts as both policy (action generator) and world model (state transition predictor).

**Architecture**:
- **State**: Reasoning chain prefix
- **Action**: Next reasoning step (text)
- **World Model**: LLM self-evaluates "what happens next"
- **Reward**: Task-specific heuristics (e.g., correctness likelihood)
- **Search**: MCTS with UCB for exploration

**Paper**: "Reasoning with Language Model is Planning with World Model" (EMNLP 2023)

**Sources**: [README.md:141](), [assets/paper.json:220-225]()

---

### AlphaZero-like LLM Decoding

**Core Idea**: Apply AlphaZero's self-play framework to language model decoding, where the LLM serves as both policy and value network.

**Key Modifications**:
- **Policy prior**: LLM token probabilities (not uniform)
- **Value network**: Separate head or self-evaluation
- **Terminal reward**: Task completion (not game outcome)
- **Training**: Self-play generates improved decoding trajectories

**Paper**: "Alphazero-like Tree-Search can Guide Large Language Model Decoding and Training" (NeurIPS Workshop 2023)

**Sources**: [README.md:144-145](), [assets/paper.json:234-239]()

---

### Value-Guided Monte-Carlo Tree Search Decoding

**Core Idea**: Use a learned value model to guide MCTS during decoding, improving over pure PPO sampling.

**Components**:
- **Value model**: Trained to predict trajectory quality
- **MCTS decoding**: Explores token sequences as tree nodes
- **Integration with PPO**: Value model trained alongside PPO policy
- **Inference**: MCTS selects optimal completion using value estimates

**Paper**: "Don't throw away your value model! Generating more preferable text with Value-Guided Monte-Carlo Tree Search decoding" (CoLM 2024)

**Sources**: [README.md:174](), [assets/paper.json:241-246]()

---

### Mulberry: Collective MCTS for Multimodal Reasoning

**Core Idea**: Extend MCTS to multimodal settings (vision + language) with collective reflection across multiple reasoning paths.

**Architecture**:
```mermaid
graph TB
    subgraph "Multimodal MCTS"
        Input["Image + Question"]
        
        subgraph "MCTS Expansion"
            Visual["Visual Perception<br/>Step"]
            Reasoning["Reasoning Step"]
            Reflection["Reflection Step"]
        end
        
        subgraph "Collective Mechanism"
            Nodes["Multiple MCTS Nodes"]
            CrossRef["Cross-node Reflection"]
            Consensus["Consensus Building"]
        end
        
        Final["Final Answer"]
    end
    
    Input --> Visual
    Input --> Reasoning
    
    Visual --> Nodes
    Reasoning --> Nodes
    
    Nodes --> CrossRef
    CrossRef --> Reflection
    Reflection --> Consensus
    Consensus --> Final
```

**Key Features**:
- **Multimodal states**: Include both visual and textual information
- **Collective reflection**: Nodes critique each other's reasoning
- **o1-like capabilities**: Step-by-step reasoning with reflection

**Paper**: "Mulberry: Empowering MLLM with o1-like Reasoning and Reflection via Collective Monte Carlo Tree Search" (arXiv 2024-12)

**Sources**: [README.md:178](), [assets/paper.json:248-253]()

---

## Theoretical Properties

### Convergence Guarantees

Recent work has established formal convergence properties of MCTS in the LLM reasoning setting.

**Key Results**:
- **Optimal value estimation**: MCTS converges to optimal Q-values under certain conditions (finite action space, Lipschitz rewards)
- **Convergence rate**: O(1/√N) for N simulations in discrete action MDPs
- **Practical implications**: Finite search budgets require careful tuning of exploration constants

**Paper**: "On the Convergence Rate of MCTS for the Optimal Value Estimation in Markov Decision Processes" (IEEE TAC 2025)

**Sources**: [README.md:186](), [assets/paper.json:416-421]()

---

## Uncertainty-Guided Variants

Several methods incorporate uncertainty quantification to improve search efficiency.

### Uncertainty Mechanisms

| Method | Uncertainty Source | Use in Search |
|--------|-------------------|---------------|
| **Uncertainty of Thoughts** | Ensemble of forward predictions | Prioritize exploration of uncertain states |
| **Uncertainty-Guided Optimization** | Prediction confidence intervals | Prune low-confidence branches early |
| **LiteSearch** | Token-level uncertainty | Adaptive depth per branch |

**Common Pattern**: Use model uncertainty to:
1. **Focus exploration**: Search more in uncertain regions
2. **Early stopping**: Terminate confident branches sooner
3. **Resource allocation**: Spend more compute on uncertain paths

**Sources**: [README.md:150](), [README.md:160-161](), [README.md:158]()

---

## Practical Considerations

### Computational Tradeoffs

```mermaid
graph LR
    subgraph "Search Parameters"
        NumIter["MCTS Iterations<br/>(10-1000)"]
        BranchFactor["Branching Factor<br/>(2-10 per node)"]
        MaxDepth["Max Search Depth<br/>(5-50 steps)"]
        Rollout["Rollout Strategy<br/>(To completion vs. truncated)"]
    end
    
    subgraph "Computational Cost"
        FLOPs["Total FLOPs<br/>= Iterations × Depth × Branch"]
        Latency["Wall-clock Time<br/>(seconds to minutes)"]
        Memory["Tree Memory<br/>(MB to GB)"]
    end
    
    subgraph "Quality Metrics"
        Accuracy["Solution Accuracy<br/>(% correct)"]
        Coverage["Search Coverage<br/>(% of state space)"]
        Diversity["Solution Diversity<br/>(unique paths found)"]
    end
    
    NumIter --> FLOPs
    BranchFactor --> FLOPs
    MaxDepth --> FLOPs
    
    FLOPs --> Latency
    BranchFactor --> Memory
    MaxDepth --> Memory
    
    NumIter --> Accuracy
    BranchFactor --> Coverage
    MaxDepth --> Coverage
    
    Coverage --> Diversity
```

### Typical Configurations

**Math Reasoning** (e.g., GSM8K, MATH):
- Iterations: 50-200
- Branching: 3-5 candidates per node
- Depth: 10-30 reasoning steps
- Guidance: Process reward model or code execution

**Code Generation**:
- Iterations: 20-100
- Branching: 2-4 code candidates
- Depth: 5-15 code blocks
- Guidance: Syntax checker + test execution

**Multimodal Reasoning**:
- Iterations: 30-100
- Branching: 3-6 reasoning paths
- Depth: 8-20 steps
- Guidance: Vision-language reward model

**Sources**: Multiple papers across [README.md:139-193]()

---

## Implementation Patterns

### Common Code Structure

Most MCTS implementations for LLMs follow this general pattern:

```
class MCTSNode:
    - state: str  # Partial reasoning chain
    - children: List[MCTSNode]
    - visits: int
    - value: float  # Q-value estimate
    - prior: float  # Policy probability
    
class MCTSReasoner:
    
    def search(problem: str, num_iterations: int) -> str:
        root = MCTSNode(state=problem)
        
        for _ in range(num_iterations):
            # Selection: UCB traversal
            leaf = select_leaf(root)
            
            # Expansion: LLM generates candidates
            candidates = llm.generate(leaf.state, n=k)
            leaf.children = [MCTSNode(c) for c in candidates]
            
            # Evaluation: Reward model scores
            for child in leaf.children:
                child.value = reward_model(child.state)
            
            # Backpropagation: Update ancestors
            backpropagate(leaf, child.value)
        
        # Extract best path
        return extract_best_trajectory(root)
    
    def select_leaf(node: MCTSNode) -> MCTSNode:
        while node.children:
            # UCB formula: Q + c * sqrt(log(N_parent) / N_child)
            node = max(node.children, key=ucb_score)
        return node
```

**Key Functions**:
- `select_leaf()`: UCB-based traversal
- `llm.generate()`: Policy expansion
- `reward_model()`: Value estimation (PRM, outcome, or code execution)
- `backpropagate()`: Update Q-values up the tree
- `extract_best_trajectory()`: Final path selection (max visits or max value)

**Sources**: Inferred from paper descriptions in [README.md:139-193]()

---

## Relation to Other Parts

### Part 2: Process Reward Models
- **Dependency**: MCTS relies on PRMs for step-wise evaluation
- **Data flow**: MCTS → trajectories → PRM training data
- **Papers**: ReST-MCTS*, AutoPSV, Math-Shepherd

### Part 3: Reinforcement Learning  
- **Synergy**: MCTS exploration + RL policy learning
- **Pattern**: MCTS as data generator for RL training
- **Papers**: DeepSeek-R1, Kimi k1.5 (use search internally)

### Part 5: Self-Training
- **Core integration**: MCTS generates training data for self-improvement
- **Loop**: Policy → MCTS search → Filtered data → Next policy
- **Papers**: ReST-MCTS*, rStar-Math, STaR + MCTS

### Part 6: Reflection
- **Enhancement**: MCTS nodes include reflection steps
- **Pattern**: Self-critique at expansion or evaluation
- **Papers**: Mulberry, Marco-o1, LLaMA-Berry

### Part 7: Efficient System2
- **Optimization target**: Reduce MCTS computational cost
- **Techniques**: Adaptive depth, early pruning, token budgeting
- **Papers**: O1-Pruner, DynaThink, TreeBoN

### Part 9-12: Multimodal Extensions
- **Adaptation**: MCTS for vision-language reasoning
- **Challenges**: Multimodal state representation, value estimation
- **Papers**: Mulberry, Virgo, AtomThink

**Sources**: [README.md:32-43](), cross-references across all parts

---

## Key Research Papers

### Foundational Works (2017-2023)

| Paper | Venue | Key Contribution |
|-------|-------|------------------|
| Expert Iteration | NeurIPS 2017 | MCTS + deep learning for RL |
| RAP | EMNLP 2023 | Reasoning as planning with world model |
| AlphaZero-like LLM Decoding | NeurIPS WS 2023 | Self-play MCTS for language |
| Value-Guided MCTS | arXiv 2023-09 | PPO + MCTS for better decoding |

### Integration Era (2024)

| Paper | Venue | Key Contribution |
|-------|-------|------------------|
| ReST-MCTS* | NeurIPS 2024 | Process rewards + self-training |
| MindStar | arXiv 2024-05 | Dual value models for math |
| AlphaMath Almost Zero | arXiv 2024-05 | Process-free MCTS |
| TreeBoN | arXiv 2024-10 | Speculative tree search |
| Mulberry | arXiv 2024-12 | Collective MCTS for multimodal |

### Self-Evolution Era (2025)

| Paper | Venue | Key Contribution |
|-------|-------|------------------|
| rStar-Math | arXiv 2025-01 | Self-evolved deep thinking |
| Search-o1 | arXiv 2025-01 | Agentic search-enhanced reasoning |

**Sources**: [README.md:139-193](), [assets/paper.json:218-512]()

---

## Future Directions

Based on the current trajectory of research, key open problems include:

1. **Scalability**: Efficient MCTS for 100+ step reasoning chains
2. **Generalization**: Transfer learned value models across domains
3. **Multimodal**: Unified MCTS for vision-language-action reasoning
4. **Verification**: Better reward signals beyond code execution
5. **Meta-learning**: Learning when to use MCTS vs. direct generation

**Sources**: Inferred from research trends in [README.md:139-193]()

---

# Page: Self-Training and Self-Improvement

# Self-Training and Self-Improvement

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/table.md](src/table.md)

</details>



This page documents self-training and self-improvement methodologies for Large Language Models, where systems generate their own training data and iteratively enhance reasoning capabilities without continuous human supervision. These bootstrapping techniques enable LLMs to autonomously improve through cycles of generation, filtering, and refinement.

**Scope**: This page covers Part 5 of the research taxonomy, focusing on methods that leverage model-generated data for training. For process-level supervision that guides these methods, see [Process Reward Models](#4.2). For tree-based exploration strategies often combined with self-training, see [MCTS and Tree Search](#4.4). For reinforcement learning approaches that may incorporate self-generated data, see [Reinforcement Learning](#4.3).

## Overview and Core Principles

Self-training for reasoning represents a paradigm shift from traditional supervised learning, enabling models to bootstrap their capabilities through iterative cycles of generation, evaluation, and retraining. The fundamental principle involves using the model's own outputs (filtered by correctness or reward signals) as training data for subsequent iterations.

```mermaid
graph TB
    BaseModel["Base LLM<br/>(Pre-trained Model)"]
    Generate["Generation Phase<br/>Sample reasoning traces<br/>with Chain-of-Thought"]
    Filter["Filtering Phase<br/>Select high-quality examples<br/>via correctness/rewards"]
    Train["Training Phase<br/>Fine-tune on filtered data"]
    ImprovedModel["Improved Model<br/>(Enhanced reasoning)"]
    
    BaseModel --> Generate
    Generate --> Filter
    Filter --> Train
    Train --> ImprovedModel
    ImprovedModel -.iterate.-> Generate
    
    Verifier["Verifier/Reward Model<br/>(Optional guidance)"]
    Verifier -.guides.-> Filter
    
    subgraph "Self-Training Loop"
        Generate
        Filter
        Train
    end
```

**Key Characteristics**:
- **Data Efficiency**: Generates training data without human annotation
- **Iterative Improvement**: Multiple training cycles compound improvements
- **Quality Control**: Filtering mechanisms ensure only correct/high-reward examples are retained
- **Scalability**: Can generate unlimited training data given computational resources

Sources: [README.md:194-224]()

## Foundational Methods

### Expert Iteration (ExIt)

The pioneering approach that established the self-training paradigm for reasoning systems, combining deep learning with tree search to iteratively improve policy and value networks.

**Mechanism**:
1. **Apprentice**: Neural network policy
2. **Expert**: Tree search algorithm (e.g., MCTS) that generates improved actions
3. **Imitation**: Apprentice learns from expert's decisions
4. **Iteration**: Process repeats with improved apprentice

```mermaid
graph LR
    Policy["Policy Network π<br/>(Apprentice)"]
    TreeSearch["Tree Search<br/>(Expert: MCTS)"]
    Dataset["Training Dataset<br/>(Expert trajectories)"]
    
    Policy -->|"generates rollouts"| TreeSearch
    TreeSearch -->|"produces improved actions"| Dataset
    Dataset -->|"supervised learning"| Policy
```

**Historical Context**: Published in NeurIPS 2017, ExIt laid the groundwork for modern self-training by demonstrating how to combine neural approximators with search algorithms to bootstrap performance.

Sources: [README.md:196](), [assets/paper.json:537-542]()

### STaR: Self-Taught Reasoner

STaR introduced the concept of bootstrapping reasoning by having the model rationalize correct answers, creating a self-supervised learning loop specifically for chain-of-thought reasoning.

**Algorithm**:
1. Generate reasoning chains for training problems
2. Filter for chains that arrive at correct answers
3. Fine-tune on correct reasoning chains
4. Repeat with improved model

**Key Innovation**: **Rationalization** - if initial reasoning fails but answer is eventually correct, the model learns to generate reasoning that leads to the correct answer, even if it differs from the original attempt.

```mermaid
graph TB
    Question["Input Question"]
    Generate["Generate CoT<br/>with current model"]
    CheckAnswer["Answer<br/>Correct?"]
    Rationalize["Rationalize:<br/>Generate new CoT<br/>with answer hint"]
    Collect["Collect for<br/>Training Dataset"]
    Finetune["Fine-tune Model"]
    
    Question --> Generate
    Generate --> CheckAnswer
    CheckAnswer -->|"Yes"| Collect
    CheckAnswer -->|"No"| Rationalize
    Rationalize --> CheckAnswer
    Collect --> Finetune
    Finetune -.next iteration.-> Question
```

**Implementation Details**:
- Uses greedy decoding or sampling for generation
- Requires access to correct answers for filtering
- Typically runs 3-5 iterations before diminishing returns

Sources: [README.md:197](), [assets/paper.json:516-521]()

### ReST: Reinforced Self-Training

ReST extends self-training by incorporating reinforcement learning principles, using reward signals to guide the filtering and training process.

**Two-Phase Approach**:

1. **Grow Phase**: Generate multiple samples per problem, creating a diverse dataset
2. **Improve Phase**: Filter high-reward samples and fine-tune via supervised learning

```mermaid
graph TB
    subgraph "Grow Phase"
        Model_t["Model at iteration t"]
        Sample["Sample N completions<br/>per prompt"]
        Evaluate["Evaluate with<br/>reward function"]
        Dataset_t["Dataset D_t<br/>(prompt, completion, reward)"]
        
        Model_t --> Sample
        Sample --> Evaluate
        Evaluate --> Dataset_t
    end
    
    subgraph "Improve Phase"
        Filter["Filter top-k%<br/>by reward"]
        Finetune["Supervised Fine-tuning<br/>on filtered data"]
        Model_t1["Model at iteration t+1"]
        
        Dataset_t --> Filter
        Filter --> Finetune
        Finetune --> Model_t1
    end
    
    Model_t1 -.next iteration.-> Model_t
```

**Reward Functions**:
- **Outcome-based**: Correctness of final answer
- **Process-based**: Step-by-step verification (see [Process Reward Models](#4.2))
- **Hybrid**: Combination of outcome and process signals

Sources: [README.md:201](), [assets/paper.json:523-528]()

### ReST-EM: Expectation-Maximization Variant

ReST-EM (Expectation-Maximization) formulates self-training as an EM optimization problem, providing theoretical grounding for the iterative improvement process.

**Mathematical Framework**:
- **E-step**: Generate samples and compute expected rewards
- **M-step**: Update policy to maximize expected reward

**Practical Advantages**:
- Principled approach to balancing exploration and exploitation
- Handles partial credit through soft filtering
- Scales to problems without binary correct/incorrect labels

Sources: [README.md:215](), [assets/paper.json:530-535]()

## Advanced Self-Training Architectures

### V-star: Verifier-Augmented Self-Training

V-star enhances the self-training loop by explicitly training a verifier model to guide the selection of high-quality reasoning traces.

```mermaid
graph TB
    subgraph "Generator Training"
        Gen_Init["Generator π"]
        Gen_Data["Generate reasoning<br/>trajectories"]
        Gen_Train["Train on<br/>verifier-approved data"]
    end
    
    subgraph "Verifier Training"
        Ver_Init["Verifier V"]
        Ver_Data["Collect (trajectory, outcome)<br/>pairs"]
        Ver_Train["Train to predict<br/>correctness"]
    end
    
    Gen_Init --> Gen_Data
    Gen_Data --> Ver_Data
    Ver_Data --> Ver_Train
    Ver_Train --> Ver_Init
    Ver_Init -.scores.-> Gen_Data
    Gen_Data --> Gen_Train
    Gen_Train --> Gen_Init
    
    subgraph "Integrated Loop"
        Gen_Init
        Ver_Init
    end
```

**Two-Model Architecture**:
1. **Generator**: Produces reasoning chains
2. **Verifier**: Evaluates quality of reasoning steps and final answers

**Training Dynamics**:
- Generator and verifier co-evolve
- Verifier provides fine-grained feedback beyond binary correctness
- Enables selection of partially correct trajectories for continued training

Sources: [README.md:203](), [assets/paper.json:551-556]()

### Quiet-STaR: Internal Reasoning Tokens

Quiet-STaR extends self-training to teach models to generate internal reasoning at every token position, not just for explicit reasoning prompts.

**Key Innovation**: Models learn to "think" before generating each token by:
1. Generating short internal thought sequences
2. Predicting next tokens based on thoughts
3. Training on predictions that improve accuracy

```mermaid
graph LR
    Token_t["Token at position t"]
    Thought["Generate internal<br/>thought sequence"]
    Predict["Predict next token<br/>with thought"]
    Compare["Compare accuracy<br/>with/without thought"]
    Weight["Weight loss by<br/>improvement"]
    
    Token_t --> Thought
    Thought --> Predict
    Predict --> Compare
    Compare --> Weight
    Weight -.backprop.-> Thought
```

**Implementation**:
- Uses special thought tokens invisible to user
- Parallel generation of multiple thought candidates
- Mixture of thought lengths for efficiency
- REINFORCE-style training on successful thoughts

Sources: [README.md:204](), [assets/paper.json:544-549]()

### ReST-MCTS*: Process Reward Guided Tree Search

ReST-MCTS* represents a sophisticated integration of self-training with Monte Carlo Tree Search and process reward models, creating a powerful synergy between multiple System 2 techniques.

```mermaid
graph TB
    subgraph "Data Generation via MCTS"
        Root["Problem Root State"]
        Expand["MCTS Expansion<br/>guided by policy"]
        Simulate["Rollout/Simulation"]
        Backprop["Backpropagate<br/>process rewards"]
        Select["Select high-value<br/>trajectories"]
        
        Root --> Expand
        Expand --> Simulate
        Simulate --> Backprop
        Backprop --> Select
    end
    
    subgraph "Self-Training"
        Dataset["Filtered MCTS<br/>trajectories"]
        Train["Fine-tune policy<br/>on trajectories"]
        ImprovedPolicy["Improved Policy π"]
        
        Select --> Dataset
        Dataset --> Train
        Train --> ImprovedPolicy
    end
    
    PRM["Process Reward Model<br/>(step-wise evaluation)"]
    PRM -.guides.-> Backprop
    
    ImprovedPolicy -.next iteration.-> Expand
```

**Three-Component Integration**:
1. **MCTS**: Explores reasoning space systematically (see [MCTS and Tree Search](#4.4))
2. **Process Rewards**: Evaluates each reasoning step (see [Process Reward Models](#4.2))
3. **Self-Training**: Distills search results into policy

**Advantages**:
- Process rewards provide richer signal than outcome-only feedback
- Tree search explores beyond model's current policy
- Self-training distills expensive search into fast inference
- Iterative improvement compounds benefits

Sources: [README.md:78](), [README.md:212](), [assets/paper.json:55-60](), [assets/paper.json:572-577]()

### rStar-Math: Self-Evolved Deep Thinking

rStar-Math demonstrates self-training at scale for mathematical reasoning, enabling small LLMs to achieve state-of-the-art performance through self-evolution.

**Multi-Stage Pipeline**:

```mermaid
graph TB
    subgraph "Stage 1: Self-Evolution"
        Init["Base Model<br/>(e.g., Qwen-7B)"]
        GenProblems["Generate diverse<br/>math problems"]
        MCTS["MCTS with code<br/>verification"]
        Solutions["High-quality<br/>solution trajectories"]
        
        Init --> GenProblems
        GenProblems --> MCTS
        MCTS --> Solutions
    end
    
    subgraph "Stage 2: Policy Distillation"
        PolicyTrain["Train policy to<br/>imitate MCTS"]
        PolicyModel["Distilled Policy"]
        
        Solutions --> PolicyTrain
        PolicyTrain --> PolicyModel
    end
    
    subgraph "Stage 3: Self-Improvement"
        SelfGen["Generate more<br/>solutions with policy"]
        SelfFilter["Filter by<br/>correctness"]
        SelfTrain["Continue training"]
        
        PolicyModel --> SelfGen
        SelfGen --> SelfFilter
        SelfFilter --> SelfTrain
        SelfTrain -.iterate.-> SelfGen
    end
    
    CodeExecutor["Code Executor<br/>(ground truth verification)"]
    CodeExecutor -.verifies.-> MCTS
    CodeExecutor -.verifies.-> SelfFilter
```

**Key Features**:
- **Problem Generation**: Model creates diverse training problems
- **Code Verification**: Uses executable code for ground truth checking
- **Deep Thinking**: Long reasoning chains via MCTS exploration
- **Iterative Refinement**: Multiple self-training cycles

**Results**: Achieves competitive performance with models 10-100x larger through intensive self-training.

Sources: [README.md:188](), [README.md:220](), [README.md:239](), [assets/paper.json:465-470](), [assets/paper.json:593-598]()

## Self-Correction and Reflection Integration

### Self-Refine: Iterative Refinement with Feedback

Self-Refine introduces a feedback loop where models critique and improve their own outputs without external supervision.

```mermaid
graph LR
    Initial["Initial Generation"]
    Feedback["Self-Generated<br/>Feedback"]
    Refine["Refine Output<br/>based on feedback"]
    Evaluate["Quality<br/>Check"]
    
    Initial --> Feedback
    Feedback --> Refine
    Refine --> Evaluate
    Evaluate -->|"Needs improvement"| Feedback
    Evaluate -->|"Satisfactory"| Output["Final Output"]
```

**Three-Step Process**:
1. **Generate**: Produce initial output
2. **Feedback**: Model critiques its own output
3. **Refine**: Model improves based on self-critique

**Application to Self-Training**: Self-Refine outputs can be used as higher-quality training data for subsequent iterations.

Sources: [README.md:200](), [README.md:202](), [assets/paper.json:607-612]()

### CRITIC: Tool-Interactive Critiquing

CRITIC enhances self-correction by enabling models to interact with external tools during the critique phase.

**Architecture**:
1. **Generate**: Produce initial reasoning/code
2. **Verify**: Use external tools (code executors, search engines) to check
3. **Critique**: Generate feedback based on verification results
4. **Refine**: Improve output incorporating critique

**Tool Integration**:
- Code execution environments
- Search engines for fact-checking
- Calculators for numerical verification
- APIs for domain-specific validation

This approach bridges self-training with tool use, enabling more reliable self-improvement cycles.

Sources: [README.md:205](), [README.md:209](), [assets/paper.json:614-619]()

### Recursive Introspection

Recursive Introspection teaches models to introspect on their reasoning process at multiple levels of abstraction.

```mermaid
graph TB
    Task["Complex Task"]
    
    subgraph "Level 1: Direct Attempt"
        Attempt1["Initial attempt"]
        Fail1["Identify failure"]
    end
    
    subgraph "Level 2: Strategy Introspection"
        Analyze["Analyze why<br/>approach failed"]
        NewStrategy["Devise new<br/>strategy"]
    end
    
    subgraph "Level 3: Meta-Learning"
        Pattern["Recognize failure<br/>pattern"]
        MetaStrategy["Adjust<br/>problem-solving approach"]
    end
    
    Task --> Attempt1
    Attempt1 --> Fail1
    Fail1 --> Analyze
    Analyze --> NewStrategy
    NewStrategy --> Pattern
    Pattern --> MetaStrategy
    MetaStrategy -.informs.-> Task
```

**Hierarchical Improvement**:
- **Level 1**: Improve specific solution
- **Level 2**: Improve solution strategy
- **Level 3**: Improve meta-strategy for problem-solving

**Training**: Self-generated examples of successful introspection become training data.

Sources: [README.md:213](), [assets/paper.json:579-584]()

## Exploration-Exploitation Balance

### B-STaR: Balanced Self-Taught Reasoner

B-STaR addresses a critical challenge in self-training: balancing exploration of new reasoning paths with exploitation of known successful patterns.

```mermaid
graph TB
    subgraph "Exploration Phase"
        Diverse["Generate diverse<br/>solutions via sampling"]
        Novel["Identify novel<br/>reasoning patterns"]
    end
    
    subgraph "Exploitation Phase"
        HighReward["Focus on<br/>high-reward patterns"]
        Refine["Refine successful<br/>approaches"]
    end
    
    subgraph "Monitoring"
        Metrics["Track:<br/>- Solution diversity<br/>- Success rate<br/>- Pattern coverage"]
        Adjust["Adjust exploration/<br/>exploitation ratio"]
    end
    
    Diverse --> Novel
    Novel --> Metrics
    HighReward --> Refine
    Refine --> Metrics
    Metrics --> Adjust
    Adjust -.controls.-> Diverse
    Adjust -.controls.-> HighReward
```

**Key Mechanisms**:
- **Diversity Metrics**: Monitor variety in generated solutions
- **Temperature Scheduling**: Adjust sampling temperature based on metrics
- **Curriculum Learning**: Gradually increase problem difficulty
- **Pattern Tracking**: Ensure coverage of different reasoning approaches

**Prevents**: Mode collapse where model converges to limited set of reasoning patterns.

Sources: [README.md:214](), [README.md:247](), [assets/paper.json:586-591]()

## Domain-Specific Self-Training

### Vision-Language Self-Training

Self-training extends to multimodal reasoning, where models generate and learn from their own visual reasoning trajectories.

**Challenges**:
- Verification requires understanding both visual and textual content
- Longer reasoning chains needed for visual understanding
- More complex feedback signals (spatial, relational, etc.)

**Approaches**:
- Generate image descriptions and verify via question-answering
- Create reasoning chains that explicitly reference visual elements
- Use code execution for geometric/spatial reasoning verification

Sources: [README.md:206](), [README.md:346](), [assets/paper.json:600-605]()

### Neural-Symbolic Self-Training

Interactive Evolution combines neural generation with symbolic reasoning for self-training.

**Hybrid Framework**:
1. **Neural Component**: Generates candidate reasoning
2. **Symbolic Component**: Verifies logical consistency
3. **Integration**: Symbolic feedback guides neural training

**Advantages**:
- Logical correctness guaranteed for symbolic portions
- Neural flexibility for pattern matching
- Self-training data has formal guarantees

Sources: [README.md:207](), [assets/paper.json:558-563]()

## Data Flow and System Integration

### Self-Training Data Pipeline

```mermaid
graph TB
    subgraph "Input Sources"
        Problems["Problem Set<br/>(train/seed data)"]
        BaseModel["Base Model<br/>(initialization)"]
    end
    
    subgraph "Generation Pipeline"
        Sample["Sample N solutions<br/>per problem"]
        Execute["Execute/Verify<br/>(if applicable)"]
        Reward["Compute rewards/<br/>correctness"]
    end
    
    subgraph "Filtering Pipeline"
        Rank["Rank by reward/quality"]
        TopK["Select top-k solutions"]
        Dedupe["Deduplicate similar<br/>reasoning patterns"]
    end
    
    subgraph "Training Pipeline"
        Format["Format as<br/>(prompt, response) pairs"]
        Augment["Data augmentation<br/>(optional)"]
        Finetune["Fine-tune model"]
    end
    
    subgraph "Evaluation"
        HeldOut["Test on held-out set"]
        Metrics["Compute metrics"]
        Decision["Continue or terminate?"]
    end
    
    Problems --> Sample
    BaseModel --> Sample
    Sample --> Execute
    Execute --> Reward
    Reward --> Rank
    Rank --> TopK
    TopK --> Dedupe
    Dedupe --> Format
    Format --> Augment
    Augment --> Finetune
    Finetune --> NewModel["Updated Model"]
    NewModel --> HeldOut
    HeldOut --> Metrics
    Metrics --> Decision
    Decision -->|"Continue"| Sample
    Decision -->|"Terminate"| Final["Final Model"]
```

**Critical Parameters**:
- **N (samples per problem)**: Higher N increases diversity but costs more compute
- **k (selection threshold)**: Lower k means stricter filtering
- **Deduplication strategy**: Prevents overfitting to specific reasoning patterns
- **Iteration count**: Typically 3-5 iterations optimal

Sources: [README.md:194-224]()

## Integration with Other System 2 Components

### Self-Training + Process Reward Models

Process Reward Models (PRMs) provide fine-grained supervision for self-training, enabling step-level filtering.

**Integration Pattern**:
```mermaid
graph LR
    Generate["Generate<br/>reasoning chain"]
    PRM["Process Reward Model<br/>scores each step"]
    StepFilter["Filter steps<br/>below threshold"]
    Reconstruct["Reconstruct valid<br/>sub-chains"]
    Train["Train on filtered<br/>sub-chains"]
    
    Generate --> PRM
    PRM --> StepFilter
    StepFilter --> Reconstruct
    Reconstruct --> Train
```

**Benefits**:
- Learn from partially correct solutions
- More training data (step-level vs trajectory-level)
- Better credit assignment

See [Process Reward Models](#4.2) for detailed PRM architectures.

Sources: [README.md:68-97](), [README.md:212]()

### Self-Training + MCTS

Monte Carlo Tree Search provides exploration mechanism for self-training data generation.

**Synergy**:
1. **MCTS explores** beyond current policy distribution
2. **PRM guides** MCTS node evaluation
3. **Self-training distills** MCTS search into fast policy
4. **Improved policy** makes MCTS more efficient

**Implementation** (ReST-MCTS*):
- Use current policy as MCTS prior
- Expand tree with policy-guided selection
- Evaluate nodes with process rewards
- Collect high-value trajectories for training
- Repeat with improved policy

See [MCTS and Tree Search](#4.4) for search algorithms.

Sources: [README.md:139-193](), [README.md:212]()

### Self-Training + Reinforcement Learning

Self-training can be viewed as offline RL with model-generated data.

**Relationship**:
- **Self-training**: Generate data, filter, supervised learning
- **RL**: Generate data, compute rewards, policy gradient updates

**Hybrid Approaches**:
- Use RL to optimize data generation strategy
- Use self-training to pre-train before expensive RL
- Alternate between self-training and RL phases

See [Reinforcement Learning](#4.3) for RL techniques.

Sources: [README.md:98-138]()

## Practical Considerations and Implementation

### Computational Costs

```mermaid
graph TB
    subgraph "Generation Cost"
        GenN["N samples × Problems"]
        GenTokens["Avg tokens per sample"]
        GenCost["Total generation tokens"]
        
        GenN --> GenCost
        GenTokens --> GenCost
    end
    
    subgraph "Verification Cost"
        VerType["Verification type:<br/>- Execution: high<br/>- PRM: medium<br/>- Outcome: low"]
        VerSamples["Samples to verify"]
        VerCost["Total verification cost"]
        
        VerType --> VerCost
        VerSamples --> VerCost
    end
    
    subgraph "Training Cost"
        TrainData["Filtered dataset size"]
        TrainEpochs["Training epochs"]
        TrainCost["Total training cost"]
        
        TrainData --> TrainCost
        TrainEpochs --> TrainCost
    end
    
    Iterations["Number of iterations"]
    TotalCost["Total Cost"]
    
    GenCost --> TotalCost
    VerCost --> TotalCost
    TrainCost --> TotalCost
    Iterations --> TotalCost
```

**Cost Optimization Strategies**:
- **Early stopping**: Monitor held-out performance
- **Adaptive sampling**: Generate fewer samples for easy problems
- **Cached verification**: Reuse verification results across iterations
- **Progressive filtering**: Quick heuristic filter before expensive verification

### Failure Modes and Mitigation

**Common Issues**:

1. **Mode Collapse**: Model converges to single reasoning pattern
   - *Mitigation*: Diversity penalties, temperature scheduling (B-STaR approach)

2. **Distribution Shift**: Generated data differs from target distribution
   - *Mitigation*: Mix self-generated and human data, regularization

3. **Reward Hacking**: Model exploits verification mechanism
   - *Mitigation*: Robust verification, multiple verification sources

4. **Diminishing Returns**: Performance plateaus after few iterations
   - *Mitigation*: Increase problem difficulty, curriculum learning

5. **Quality Degradation**: Model forgets capabilities
   - *Mitigation*: Mix replay data, catastrophic forgetting prevention

### Hyperparameter Guidelines

| Parameter | Typical Range | Notes |
|-----------|---------------|-------|
| Samples per problem (N) | 16-256 | Higher for harder problems |
| Selection threshold (k) | top 10-50% | Stricter for more data |
| Learning rate | 1e-6 to 1e-5 | Lower than initial training |
| Iterations | 3-5 | Diminishing returns after |
| Temperature | 0.7-1.0 | Higher for exploration |
| Max sequence length | 2048-8192 | Depends on reasoning depth |

Sources: [README.md:194-224]()

## Recent Advances (2024-2025)

### Self-Evolved Deep Thinking (rStar-Math)

Recent work demonstrates that small models can achieve strong reasoning through intensive self-training:

**Key Results**:
- 7B model approaches GPT-4 level on math benchmarks
- Requires 10-100x more training compute than base model
- Achieves 90%+ accuracy on competition math problems

**Innovations**:
- Self-generated problem sets
- Multi-stage training pipeline
- Code-based verification for mathematical correctness

Sources: [README.md:220](), [README.md:239]()

### Genius Framework

Generalizable and Purely Unsupervised Self-Training for advanced reasoning.

**Features**:
- No human annotations required at any stage
- Automatic difficulty calibration
- Cross-domain transfer of reasoning skills
- Unified framework for multiple reasoning types

Sources: [README.md:223]()

### START: Self-Taught Reasoner with Tools

Extension of self-training that incorporates tool use:

**Components**:
1. Generate reasoning with tool calls
2. Execute tools and collect results
3. Filter successful tool-augmented reasoning
4. Train on successful trajectories

**Tools Integrated**:
- Code interpreters
- Search engines
- Calculators
- Domain-specific APIs

Sources: [README.md:224]()

## Evaluation Metrics

```mermaid
graph TB
    subgraph "Performance Metrics"
        Accuracy["Task Accuracy<br/>(final answer)"]
        Efficiency["Reasoning Efficiency<br/>(steps/tokens)"]
        Generalization["Out-of-distribution<br/>Performance"]
    end
    
    subgraph "Training Metrics"
        DataQuality["Generated Data<br/>Quality"]
        Diversity["Reasoning Pattern<br/>Diversity"]
        Coverage["Problem Coverage"]
    end
    
    subgraph "Iteration Metrics"
        IterGain["Per-iteration Gain"]
        Plateau["Plateau Detection"]
        Cost["Cost per Improvement"]
    end
    
    subgraph "Overall Assessment"
        ROI["Return on<br/>Investment"]
        Scalability["Scaling Properties"]
    end
    
    Accuracy --> ROI
    Efficiency --> ROI
    IterGain --> ROI
    Cost --> ROI
    
    Diversity --> Scalability
    Generalization --> Scalability
```

**Key Metrics to Track**:
- **Pass@1**: Accuracy with single sample
- **Pass@K**: Accuracy with K samples (measures exploration)
- **Improvement Rate**: Gain per iteration
- **Cost Efficiency**: Performance gain per compute unit
- **Data Efficiency**: Performance vs training examples

Sources: [README.md:351-433]()

## Comparison with Other Approaches

| Aspect | Self-Training | Supervised Learning | Reinforcement Learning | MCTS |
|--------|---------------|---------------------|----------------------|------|
| **Data Source** | Model-generated | Human-annotated | Reward signal | Search |
| **Supervision** | Self-supervised | Fully supervised | Reward-based | Value-based |
| **Scalability** | High (infinite data) | Limited (human cost) | Medium | Medium |
| **Quality Control** | Via filtering | Human quality | Via rewards | Via search |
| **Compute Cost** | Medium-High | Low | High | Very High |
| **Inference Cost** | Low (distilled) | Low | Low | High |

**When to Use Self-Training**:
- ✓ Have good verification mechanism (executability, formal specs)
- ✓ Need to scale beyond human-annotated data
- ✓ Can afford generation and filtering costs
- ✓ Have iterative training budget
- ✗ No reliable verification available
- ✗ Need guaranteed quality
- ✗ Limited computational resources

Sources: [README.md:1-44]()

## Future Directions

**Open Research Questions**:

1. **Optimal Iteration Strategy**: When to stop self-training? How to detect saturation?

2. **Multi-Task Self-Training**: Can self-training on one reasoning task improve others?

3. **Verification Scaling**: As models improve, verification becomes harder - how to scale verification?

4. **Theoretical Foundations**: What guarantees exist for self-training convergence and quality?

5. **Efficiency**: Can we reduce computational costs while maintaining benefits?

6. **Safety**: How to prevent self-training from amplifying undesired behaviors?

**Emerging Trends**:
- Integration with test-time compute (see [Efficient System2](#5.1))
- Combination with multimodal reasoning (see [Multimodal Extensions](#6))
- Application to agent systems and long-horizon tasks
- Self-training for alignment and safety (see [Reasoning and Safety](#7.2))

Sources: [README.md:1-44]()

---

# Page: Reflection Mechanisms

# Reflection Mechanisms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/list.md](src/list.md)

</details>



## Purpose and Scope

This document covers **Part 6: Reflection** from the Awesome-System2-Reasoning-LLM repository, focusing on self-correction capabilities that enable LLMs to critique, evaluate, and refine their own reasoning steps. Reflection mechanisms represent a critical component of System 2 reasoning, allowing models to detect errors and improve outputs through iterative self-assessment.

**Related topics:** For process-level evaluation using external reward models, see [Process Reward Models](#4.2). For bootstrapping methods that generate training data via self-improvement, see [Self-Training and Self-Improvement](#4.5). For tree search algorithms that explore multiple reasoning paths, see [MCTS and Tree Search](#4.4). This page specifically addresses mechanisms where the model acts as its own critic during or after generation.

**Sources:** [README.md:225-241]()

---

## Reflection in the System 2 Reasoning Pipeline

Reflection mechanisms occupy a unique position in the System 2 reasoning architecture, operating as both an inference-time and training-time capability. Unlike external verification (Process Reward Models) or exploration-based methods (MCTS), reflection involves the model directly evaluating and modifying its own outputs.

### Reflection Pipeline Architecture

```mermaid
graph TB
    subgraph "Input Phase"
        QUERY["Query/Problem"]
    end
    
    subgraph "Initial Generation"
        GEN["Base LLM Generation"]
        INIT_COT["Initial Chain-of-Thought"]
    end
    
    subgraph "Reflection Loop"
        CRITIC["Self-Critique Module"]
        ERROR["Error Detection"]
        EVAL["Self-Evaluation"]
        REFINE["Refinement Generation"]
        CHECK["Quality Check"]
    end
    
    subgraph "Integration Mechanisms"
        SELFCHECK["SelfCheck:<br/>Zero-shot verification"]
        SELFREFINE["Self-Refine:<br/>Iterative feedback"]
        CRITIC_TOOL["CRITIC:<br/>Tool-interactive critique"]
        MUTUAL["Mutual Reasoning:<br/>Multi-agent reflection"]
    end
    
    subgraph "Output"
        FINAL["Refined Output"]
        IMPROVED["Improved Reasoning"]
    end
    
    QUERY --> GEN
    GEN --> INIT_COT
    INIT_COT --> CRITIC
    
    CRITIC --> ERROR
    ERROR --> EVAL
    EVAL --> REFINE
    REFINE --> CHECK
    
    CHECK -->|"Needs improvement"| CRITIC
    CHECK -->|"Satisfactory"| FINAL
    
    SELFCHECK -.provides.-> ERROR
    SELFREFINE -.provides.-> REFINE
    CRITIC_TOOL -.provides.-> EVAL
    MUTUAL -.provides.-> CRITIC
    
    FINAL --> IMPROVED
```

**Diagram: Reflection Loop Architecture**
The iterative cycle where models critique and refine their own outputs, with various mechanisms implementing different stages of the loop.

**Sources:** [README.md:225-241]()

---

## Core Reflection Patterns

Reflection mechanisms in the repository follow several distinct patterns, each addressing different aspects of self-correction.

### Pattern Taxonomy

| Pattern | Mechanism | Key Papers | Primary Use Case |
|---------|-----------|------------|------------------|
| **Zero-shot Self-Verification** | Model checks its own reasoning without additional training | SelfCheck | Step-by-step reasoning validation |
| **Iterative Refinement** | Multiple rounds of critique and improvement | Self-Refine, Reflection-Tuning | General output quality improvement |
| **Tool-Interactive Critique** | External tool feedback guides refinement | CRITIC | Factual correctness verification |
| **Multi-agent Reflection** | Multiple models critique each other | Mutual Reasoning | Enhanced problem-solving via collaboration |
| **Pairwise Optimization** | Comparative evaluation of solutions | LLaMA-Berry | Mathematical olympiad-level reasoning |
| **Vision-Language Reflection** | Multimodal self-improvement | LLaVA-o1, AtomThink, Mulberry | Visual reasoning correction |

**Sources:** [README.md:226-236](), [assets/paper.json:621-663]()

### Self-Verification Mechanisms

```mermaid
graph LR
    subgraph "SelfCheck_Zero_Shot"
        INPUT["Reasoning Steps"]
        VERIFY["Self-Verification Prompt"]
        CONFIDENCE["Confidence Score"]
        DECISION["Accept/Reject"]
    end
    
    subgraph "Reflection_Tuning"
        ORIGINAL["Original Response"]
        REFLECT["Reflection Prompt"]
        CRITIQUE["Generated Critique"]
        RECYCLE["Data Recycling"]
        TRAIN["Fine-tuning"]
    end
    
    subgraph "Learning_From_Mistakes"
        ATTEMPTS["Multiple Attempts"]
        ERRORS["Error Identification"]
        ANALYSIS["Error Analysis"]
        IMPROVE["Improved Reasoning"]
    end
    
    INPUT --> VERIFY
    VERIFY --> CONFIDENCE
    CONFIDENCE --> DECISION
    
    ORIGINAL --> REFLECT
    REFLECT --> CRITIQUE
    CRITIQUE --> RECYCLE
    RECYCLE --> TRAIN
    
    ATTEMPTS --> ERRORS
    ERRORS --> ANALYSIS
    ANALYSIS --> IMPROVE
```

**Diagram: Self-Verification Pattern Implementations**
Three distinct approaches to enabling models to check their own work, ranging from zero-shot verification to training-based improvement.

**Sources:** [README.md:226-228](), [assets/paper.json:622-635]()

---

## Integration with Other Methodologies

Reflection mechanisms frequently combine with other System 2 techniques to create more powerful reasoning systems.

### Reflection + MCTS Integration

```mermaid
graph TB
    subgraph "MCTS_Tree_Search"
        ROOT["Root Node"]
        EXPAND["Expansion"]
        NODES["Candidate Nodes"]
    end
    
    subgraph "Reflection_Layer"
        MULBERRY["Mulberry:<br/>Collective MCTS + Reflection"]
        LLAMA_BERRY["LLaMA-Berry:<br/>Pairwise Optimization"]
        MARCO_O1["Marco-o1:<br/>Open-ended reflection"]
    end
    
    subgraph "Evaluation"
        SELF_EVAL["Self-Evaluation"]
        PAIRWISE["Pairwise Comparison"]
        PRUNE["Tree Pruning"]
    end
    
    ROOT --> EXPAND
    EXPAND --> NODES
    
    NODES --> MULBERRY
    NODES --> LLAMA_BERRY
    NODES --> MARCO_O1
    
    MULBERRY --> SELF_EVAL
    LLAMA_BERRY --> PAIRWISE
    MARCO_O1 --> SELF_EVAL
    
    SELF_EVAL --> PRUNE
    PAIRWISE --> PRUNE
```

**Diagram: MCTS-Reflection Hybrid Systems**
Reflection mechanisms enhance tree search by providing better node evaluation and pruning strategies.

**Sources:** [README.md:230-234](), [assets/paper.json:248-252, 339-343]()

### Reflection + Self-Training Pipeline

The integration between reflection (Part 6) and self-training (Part 5) creates a powerful feedback loop where models use reflection to generate higher-quality training data.

```mermaid
graph TB
    subgraph "Self_Training_Phase"
        INIT["Initial Model"]
        GENERATE["Generate Solutions"]
        FILTER["Filter by Correctness"]
    end
    
    subgraph "Reflection_Enhancement"
        CRITIC_MODULE["CRITIC"]
        SELF_REFINE_MODULE["Self-Refine"]
        ERROR_DETECT["Error Detection"]
        QUALITY_IMPROVE["Quality Improvement"]
    end
    
    subgraph "Data_Quality"
        LOW_QUALITY["Low-quality Data"]
        REFLECTED["Reflected Data"]
        HIGH_QUALITY["High-quality Training Data"]
    end
    
    subgraph "Training_Loop"
        RETRAIN["Retrain Model"]
        IMPROVED_MODEL["Improved Model"]
    end
    
    INIT --> GENERATE
    GENERATE --> FILTER
    
    FILTER --> LOW_QUALITY
    LOW_QUALITY --> CRITIC_MODULE
    LOW_QUALITY --> SELF_REFINE_MODULE
    
    CRITIC_MODULE --> ERROR_DETECT
    SELF_REFINE_MODULE --> ERROR_DETECT
    ERROR_DETECT --> QUALITY_IMPROVE
    QUALITY_IMPROVE --> REFLECTED
    
    FILTER --> HIGH_QUALITY
    REFLECTED --> HIGH_QUALITY
    
    HIGH_QUALITY --> RETRAIN
    RETRAIN --> IMPROVED_MODEL
    IMPROVED_MODEL -->|"Next iteration"| GENERATE
```

**Diagram: Self-Training Enhanced by Reflection**
Reflection mechanisms improve the quality of self-generated training data, creating a more effective self-improvement loop.

**Sources:** [README.md:225-241, 194-224]()

---

## Multimodal Reflection Systems

Recent work extends reflection mechanisms to vision-language models, enabling self-correction in multimodal reasoning tasks.

### Multimodal Reflection Architecture

```mermaid
graph TB
    subgraph "Vision_Language_Input"
        IMAGE["Image Input"]
        TEXT["Text Query"]
        VL_ENCODE["Vision-Language Encoding"]
    end
    
    subgraph "Initial_Reasoning"
        VL_GEN["Multimodal Generation"]
        VISUAL_COT["Visual Chain-of-Thought"]
    end
    
    subgraph "Reflection_Systems"
        LLAVA_O1["LLaVA-o1:<br/>Step-by-step VL reasoning"]
        ATOMTHINK["AtomThink:<br/>Slow thinking framework"]
        MULBERRY_MM["Mulberry:<br/>MCTS + Reflection"]
        VL_REFLECTION["Vision-Language Models<br/>Can Self-Improve"]
    end
    
    subgraph "Reflection_Process"
        VISUAL_CRITIQUE["Visual Reasoning Critique"]
        CROSS_MODAL["Cross-modal Consistency Check"]
        REFINEMENT["Multimodal Refinement"]
    end
    
    subgraph "Output"
        CORRECTED_VL["Corrected VL Output"]
        IMPROVED_REASONING["Improved Visual Reasoning"]
    end
    
    IMAGE --> VL_ENCODE
    TEXT --> VL_ENCODE
    VL_ENCODE --> VL_GEN
    VL_GEN --> VISUAL_COT
    
    VISUAL_COT --> LLAVA_O1
    VISUAL_COT --> ATOMTHINK
    VISUAL_COT --> MULBERRY_MM
    VISUAL_COT --> VL_REFLECTION
    
    LLAVA_O1 --> VISUAL_CRITIQUE
    ATOMTHINK --> VISUAL_CRITIQUE
    MULBERRY_MM --> CROSS_MODAL
    VL_REFLECTION --> CROSS_MODAL
    
    VISUAL_CRITIQUE --> REFINEMENT
    CROSS_MODAL --> REFINEMENT
    REFINEMENT --> CORRECTED_VL
    CORRECTED_VL --> IMPROVED_REASONING
```

**Diagram: Multimodal Reflection Pipeline**
Extension of reflection mechanisms to handle visual reasoning tasks, with specialized critique and refinement for vision-language models.

**Sources:** [README.md:232-236](), [assets/paper.json:658-663, 762-809]()

### Key Multimodal Reflection Papers

| System | Innovation | Modality | Year |
|--------|-----------|----------|------|
| **LLaVA-o1** | Step-by-step visual reasoning with reflection | Vision-Language | 2024-11 |
| **AtomThink** | Slow thinking framework for mathematical visual reasoning | Vision-Language-Math | 2024-11 |
| **Mulberry** | Collective MCTS with multimodal reflection | Vision-Language | 2024-12 |
| **Vision-Language Models Can Self-Improve** | Self-improvement via visual reflection | Vision-Language | 2024-11 |

**Sources:** [README.md:235-236](), [assets/paper.json:658-663]()

---

## Reflection Mechanisms in O1-like Systems

Reflection plays a critical role in O1 replication efforts (Part 1), where it provides the self-correction capability necessary for expert-level reasoning.

### O1 Reflection Integration

```mermaid
graph TB
    subgraph "O1_Target_Capabilities"
        LONG_COT["Long Chain-of-Thought"]
        SELF_CORRECT["Self-Correction"]
        EXPERT_LEVEL["Expert-level Performance"]
    end
    
    subgraph "Reflection_Contributions"
        HUATUO_O1["HuatuoGPT-o1:<br/>Medical complex reasoning"]
        RSTAR_MATH["rStar-Math:<br/>Self-evolved deep thinking"]
        MARCO_O1_REFL["Marco-o1:<br/>Open reasoning models"]
    end
    
    subgraph "Reflection_Techniques"
        MED_REFLECT["Medical Reasoning Reflection"]
        MATH_REFLECT["Mathematical Self-Correction"]
        OPEN_REFLECT["Open-ended Reflection"]
    end
    
    subgraph "Integration_With"
        PROCESS_REWARDS["Process Reward Models<br/>(Part 2)"]
        MCTS_SEARCH["MCTS Tree Search<br/>(Part 4)"]
        SELF_TRAIN["Self-Training<br/>(Part 5)"]
    end
    
    LONG_COT --> HUATUO_O1
    SELF_CORRECT --> RSTAR_MATH
    EXPERT_LEVEL --> MARCO_O1_REFL
    
    HUATUO_O1 --> MED_REFLECT
    RSTAR_MATH --> MATH_REFLECT
    MARCO_O1_REFL --> OPEN_REFLECT
    
    MED_REFLECT --> PROCESS_REWARDS
    MATH_REFLECT --> MCTS_SEARCH
    OPEN_REFLECT --> SELF_TRAIN
```

**Diagram: Reflection in O1 Replication Systems**
How reflection mechanisms contribute to achieving O1-like capabilities across different domains.

**Sources:** [README.md:237-240](), [README.md:45-67]()

---

## Technical Implementation Patterns

### Basic Reflection Prompt Structure

Reflection systems typically follow this general prompt pattern:

```
Initial Generation Phase:
  1. Generate initial reasoning/solution
  2. Output step-by-step chain-of-thought

Reflection Phase:
  1. Critique the initial solution
  2. Identify specific errors or weaknesses
  3. Explain what improvements are needed
  
Refinement Phase:
  1. Generate improved solution
  2. Incorporate insights from critique
  3. Verify improvements address identified issues
```

**Sources:** [README.md:226-241]()

### Reflection Data Structure Flow

```mermaid
graph LR
    subgraph "Input_Structure"
        PROBLEM["Problem"]
        CONTEXT["Context"]
    end
    
    subgraph "Generation_Structure"
        INITIAL_SOL["Initial Solution"]
        REASONING_STEPS["Reasoning Steps"]
        INITIAL_ANSWER["Initial Answer"]
    end
    
    subgraph "Reflection_Structure"
        CRITIQUE["Critique"]
        ERROR_LIST["Error List"]
        IMPROVEMENT_PLAN["Improvement Plan"]
    end
    
    subgraph "Refinement_Structure"
        REVISED_REASONING["Revised Reasoning"]
        FINAL_ANSWER["Final Answer"]
        CONFIDENCE["Confidence Score"]
    end
    
    PROBLEM --> INITIAL_SOL
    CONTEXT --> INITIAL_SOL
    INITIAL_SOL --> REASONING_STEPS
    REASONING_STEPS --> INITIAL_ANSWER
    
    INITIAL_ANSWER --> CRITIQUE
    REASONING_STEPS --> CRITIQUE
    CRITIQUE --> ERROR_LIST
    ERROR_LIST --> IMPROVEMENT_PLAN
    
    IMPROVEMENT_PLAN --> REVISED_REASONING
    REVISED_REASONING --> FINAL_ANSWER
    FINAL_ANSWER --> CONFIDENCE
```

**Diagram: Data Flow in Reflection Systems**
The structured information flow from initial generation through reflection to refined output.

**Sources:** [README.md:225-241]()

---

## Reflection Training Strategies

### Reflection-Tuning Approach

Reflection-Tuning ([README.md:227]()) introduces a data recycling strategy where reflection outputs become training data:

```mermaid
graph TB
    subgraph "Data_Collection"
        ORIG_RESPONSES["Original Model Responses"]
        REFLECTION_PROMPTS["Add Reflection Prompts"]
        REFLECTED_OUTPUTS["Generate Reflected Outputs"]
    end
    
    subgraph "Data_Filtering"
        QUALITY_FILTER["Quality Filtering"]
        ERROR_CORRECTION["Error Correction Pairs"]
        IMPROVEMENT_PAIRS["Improvement Pairs"]
    end
    
    subgraph "Training_Data"
        BEFORE_AFTER["Before/After Pairs"]
        CRITIQUE_DATA["Critique Examples"]
        REFINEMENT_DATA["Refinement Examples"]
    end
    
    subgraph "Fine_Tuning"
        REFLECTION_MODEL["Reflection-Enhanced Model"]
        DEPLOY["Deployment"]
    end
    
    ORIG_RESPONSES --> REFLECTION_PROMPTS
    REFLECTION_PROMPTS --> REFLECTED_OUTPUTS
    
    REFLECTED_OUTPUTS --> QUALITY_FILTER
    QUALITY_FILTER --> ERROR_CORRECTION
    QUALITY_FILTER --> IMPROVEMENT_PAIRS
    
    ERROR_CORRECTION --> BEFORE_AFTER
    IMPROVEMENT_PAIRS --> CRITIQUE_DATA
    IMPROVEMENT_PAIRS --> REFINEMENT_DATA
    
    BEFORE_AFTER --> REFLECTION_MODEL
    CRITIQUE_DATA --> REFLECTION_MODEL
    REFINEMENT_DATA --> REFLECTION_MODEL
    
    REFLECTION_MODEL --> DEPLOY
```

**Diagram: Reflection-Tuning Training Pipeline**
Converting reflection outputs into training data for teaching models to self-correct.

**Sources:** [README.md:227](), [assets/paper.json:630-634]()

---

## Mutual Reasoning Pattern

Multi-agent reflection enables smaller models to achieve stronger problem-solving through collaborative critique.

### Mutual Reasoning Architecture

```mermaid
graph TB
    subgraph "Model_Agents"
        MODEL_A["LLM Agent A"]
        MODEL_B["LLM Agent B"]
        MODEL_C["LLM Agent C"]
    end
    
    subgraph "Problem_Solving"
        PROBLEM_INPUT["Problem"]
        PARALLEL_GEN["Parallel Generation"]
        SOLUTION_A["Solution A"]
        SOLUTION_B["Solution B"]
        SOLUTION_C["Solution C"]
    end
    
    subgraph "Cross_Critique"
        A_CRITIQUES_B["A critiques B"]
        B_CRITIQUES_C["B critiques C"]
        C_CRITIQUES_A["C critiques A"]
    end
    
    subgraph "Refinement_Round"
        IMPROVED_A["Improved Solution A"]
        IMPROVED_B["Improved Solution B"]
        IMPROVED_C["Improved Solution C"]
    end
    
    subgraph "Consensus"
        VOTE["Voting Mechanism"]
        BEST_SOLUTION["Best Solution"]
    end
    
    PROBLEM_INPUT --> PARALLEL_GEN
    PARALLEL_GEN --> MODEL_A
    PARALLEL_GEN --> MODEL_B
    PARALLEL_GEN --> MODEL_C
    
    MODEL_A --> SOLUTION_A
    MODEL_B --> SOLUTION_B
    MODEL_C --> SOLUTION_C
    
    SOLUTION_B --> A_CRITIQUES_B
    SOLUTION_C --> B_CRITIQUES_C
    SOLUTION_A --> C_CRITIQUES_A
    
    A_CRITIQUES_B --> IMPROVED_B
    B_CRITIQUES_C --> IMPROVED_C
    C_CRITIQUES_A --> IMPROVED_A
    
    IMPROVED_A --> VOTE
    IMPROVED_B --> VOTE
    IMPROVED_C --> VOTE
    
    VOTE --> BEST_SOLUTION
```

**Diagram: Mutual Reasoning Multi-Agent Reflection**
Multiple models critique each other's solutions, creating a collaborative refinement process.

**Sources:** [README.md:229](), [assets/paper.json:623-627]()

---

## Domain-Specific Reflection Applications

### Medical Reasoning Reflection

**HuatuoGPT-o1** ([README.md:237]()) demonstrates reflection for medical complex reasoning:

- **Medical Knowledge Integration:** Reflection prompts incorporate medical knowledge bases
- **Multi-step Clinical Reasoning:** Critique focuses on diagnostic logic and treatment plans
- **Safety Validation:** Additional reflection layer for medical safety checks

### Mathematical Reasoning Reflection

**rStar-Math** ([README.md:239]()) applies self-evolved deep thinking with reflection:

- **Step-by-step Verification:** Each mathematical step undergoes self-verification
- **Error Pattern Learning:** Model learns common error patterns through reflection
- **Theorem Application Check:** Reflects on correctness of theorem/formula application

**Sources:** [README.md:237-240]()

---

## Reflection vs. Related Mechanisms

Understanding the distinction between reflection and related methodologies:

| Mechanism | Primary Actor | When Applied | Data Required | Papers |
|-----------|--------------|--------------|---------------|--------|
| **Reflection** | Self-critique by same model | During/after generation | No external labels | Self-Refine, CRITIC, SelfCheck |
| **Process Reward Models** | External reward model | Step-wise evaluation | Human-labeled process data | Math-Shepherd, PRMBench |
| **Self-Training** | Model generates training data | Training time | Outcome correctness | STaR, ReST, V-star |
| **MCTS** | Tree search algorithm | Inference time exploration | Value function | RAP, MindStar, ReST-MCTS* |

**Sources:** [README.md:68-241]()

---

## Research Evolution Timeline

```mermaid
timeline
    title Reflection Mechanisms Evolution (2023-2025)
    
    2023-08 : SelfCheck
            : Zero-shot step verification
    
    2023-10 : Reflection-Tuning
            : Learning From Mistakes
            : Data recycling approach
    
    2024-08 : Mutual Reasoning
            : Multi-agent reflection
    
    2024-10 : LLaMA-Berry
            : Pairwise optimization
    
    2024-11 : AtomThink
            : LLaVA-o1
            : Vision-Language Models Self-Improve
            : Multimodal reflection emergence
            : Marco-o1
    
    2024-12 : Mulberry
            : HuatuoGPT-o1
            : MCTS + Reflection integration
            : Domain-specific applications
    
    2025-01 : rStar-Math
            : RedStar
            : Self-evolved deep thinking
            : Long-CoT reflection scaling
    
    2025-04 : Perception in Reflection
            : Advanced reflection mechanisms
```

**Diagram: Timeline of Reflection Mechanisms Research**
Evolution from basic self-checking to sophisticated multimodal and domain-specific reflection systems.

**Sources:** [README.md:225-241](), [assets/paper.json:621-663]()

---

## Key Papers and Their Contributions

### Foundational Papers

1. **SelfCheck** ([README.md:226]())
   - Zero-shot step-by-step reasoning verification
   - No additional training required
   - Foundation for subsequent reflection work

2. **Self-Refine** ([README.md:200, 202]())
   - Iterative refinement with self-feedback
   - Multiple rounds of critique and improvement
   - General-purpose output enhancement

3. **CRITIC** ([README.md:205, 209]())
   - Tool-interactive critiquing
   - External tool feedback integration
   - Factual correctness verification

### Advanced Systems

4. **LLaMA-Berry** ([README.md:230]())
   - Pairwise optimization for mathematical reasoning
   - Olympiad-level problem solving
   - Comparative evaluation mechanism

5. **Mulberry** ([README.md:231]())
   - Collective MCTS with reflection
   - Multimodal o1-like capabilities
   - Integrated tree search and self-correction

6. **rStar-Math** ([README.md:239]())
   - Self-evolved deep thinking
   - Mathematical reasoning mastery
   - Small models achieving expert performance

**Sources:** [README.md:225-241](), [assets/paper.json:621-663]()

---

## Reflection in Efficient System2

Reflection mechanisms contribute to efficiency (Part 7) by reducing unnecessary computation through early error detection:

```mermaid
graph LR
    subgraph "Without_Reflection"
        GEN1["Generate Full Solution"]
        CHECK1["External Verification"]
        FAIL1["Failure Detected"]
        REGEN1["Regenerate Completely"]
        COST_HIGH["High Token Cost"]
    end
    
    subgraph "With_Reflection"
        GEN2["Generate with Checkpoints"]
        SELF_CHECK["Self-Verification at Steps"]
        EARLY_DETECT["Early Error Detection"]
        LOCAL_FIX["Local Correction"]
        COST_LOW["Lower Token Cost"]
    end
    
    GEN1 --> CHECK1
    CHECK1 --> FAIL1
    FAIL1 --> REGEN1
    REGEN1 --> COST_HIGH
    
    GEN2 --> SELF_CHECK
    SELF_CHECK --> EARLY_DETECT
    EARLY_DETECT --> LOCAL_FIX
    LOCAL_FIX --> COST_LOW
```

**Diagram: Reflection Efficiency Benefits**
Self-reflection enables early error detection and localized corrections, reducing computational cost compared to full regeneration.

**Sources:** [README.md:242-325]()

---

## Practical Implementation Considerations

### When to Use Reflection

Reflection mechanisms are most effective when:

1. **Error patterns are learnable:** The model can recognize its own common mistakes
2. **Reasoning is verifiable:** Correctness can be assessed without external labels
3. **Iterative improvement is possible:** Solutions can be refined incrementally
4. **Cost-performance tradeoff favors quality:** Extra generation cost is acceptable for better results

### Integration Patterns

Reflection can be integrated with:

- **Process Reward Models** ([README.md:68-97]()): Use PRM scores to trigger reflection
- **MCTS** ([README.md:139-193]()): Reflect on tree nodes before expansion
- **Self-Training** ([README.md:194-224]()): Use reflection to improve training data quality
- **RL Training** ([README.md:98-138]()): Reflection as part of the reward signal

**Sources:** [README.md:68-325]()

---

## Future Directions

Based on recent papers ([README.md:239-241]()), emerging research directions include:

1. **Long-CoT Reflection Scaling:** RedStar explores whether scaling long chain-of-thought data with reflection improves slow-reasoning systems

2. **Perception in Reflection:** New work on understanding how models perceive and reflect on their reasoning processes

3. **Cross-Modal Reflection:** Extending reflection to handle consistency across different modalities (vision, language, audio)

4. **Automated Reflection Learning:** Teaching models to develop their own reflection strategies without explicit prompting

**Sources:** [README.md:239-241]()

---

## Summary

Reflection mechanisms represent a critical self-correction capability in System 2 reasoning, enabling models to:

- **Detect errors** in their own reasoning through self-verification
- **Critique outputs** using iterative refinement patterns
- **Improve solutions** through multiple reflection rounds
- **Integrate with other techniques** (MCTS, self-training, PRMs) for enhanced reasoning
- **Extend to multimodal** vision-language tasks
- **Support O1-like systems** with self-correction capabilities

The field has evolved from basic zero-shot checking (SelfCheck) to sophisticated multimodal systems (Mulberry, LLaVA-o1) that combine reflection with tree search and reinforcement learning. Reflection continues to be a key component in achieving expert-level reasoning performance in LLMs.

**Sources:** [README.md:225-241](), [assets/paper.json:621-663]()

---

# Page: Optimization and Understanding

# Optimization and Understanding

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This page documents cross-cutting research on making System 2 reasoning computationally feasible and understanding its internal mechanisms (Parts 7-8 from the repository taxonomy). While core methodologies like MCTS, RL, and Process Rewards define *what* reasoning techniques exist, this section addresses *how to deploy them efficiently* and *why they work*.

For information about the fundamental reasoning methodologies themselves, see [Core Methodologies](#4). For evaluation of reasoning systems, see [Evaluation and Safety](#7).

**Scope Coverage:**
- **Part 7: Efficient System2** - Computational optimization techniques for reducing inference costs
- **Part 8: Explainability** - Understanding internal mechanisms through interpretability research

---

## Overview: The Efficiency-Understanding Connection

System 2 reasoning in LLMs faces a fundamental challenge: deliberate reasoning requires multiple inference steps, tree search, or iterative refinement, which dramatically increases computational cost. Simultaneously, understanding *how* reasoning emerges in neural networks informs both optimization strategies and safety considerations.

```mermaid
graph TB
    subgraph "System 2 Reasoning Challenges"
        COST["High Computational Cost<br/>• Long chains-of-thought<br/>• Tree search exploration<br/>• Multiple verification passes"]
        OPACITY["Mechanism Opacity<br/>• Black-box reasoning<br/>• Unexplained failures<br/>• Safety concerns"]
    end
    
    subgraph "Part 7: Efficient System2"
        ROUTING["Dynamic Routing<br/>DynaThink<br/>Fast/Slow decision"]
        BUDGET["Token Budgeting<br/>Token-Budget-Aware<br/>O1-Pruner"]
        LATENT["Latent Reasoning<br/>Continuous space<br/>Token Assorted"]
        COMPRESS["Compression<br/>TokenSkip, SoftCoT<br/>LightThinker"]
        ARCH["Architecture<br/>MoBA, Titans<br/>Attention sparsity"]
    end
    
    subgraph "Part 8: Explainability"
        LAYER["Layer Analysis<br/>Fast vs Slow gradients<br/>System 1/2 separation"]
        MECH["Mechanism Studies<br/>o1 optimization<br/>Autoregression analysis"]
        ARCH_EXP["Architectural Insights<br/>Talker-Reasoner<br/>Meta Chain-of-Thought"]
    end
    
    subgraph "Outcomes"
        DEPLOY["Production Deployment<br/>Cost-effective reasoning"]
        SAFETY["Safety & Robustness<br/>Explainable decisions"]
        IMPROVE["Model Improvement<br/>Informed design choices"]
    end
    
    COST --> ROUTING
    COST --> BUDGET
    COST --> LATENT
    COST --> COMPRESS
    COST --> ARCH
    
    OPACITY --> LAYER
    OPACITY --> MECH
    OPACITY --> ARCH_EXP
    
    ROUTING --> DEPLOY
    BUDGET --> DEPLOY
    LATENT --> DEPLOY
    COMPRESS --> DEPLOY
    ARCH --> DEPLOY
    
    LAYER --> SAFETY
    MECH --> SAFETY
    ARCH_EXP --> SAFETY
    
    LAYER -.informs.-> ROUTING
    MECH -.informs.-> LATENT
    ARCH_EXP -.informs.-> ARCH
    
    DEPLOY --> IMPROVE
    SAFETY --> IMPROVE
```

**Sources:** [README.md:38-39](), [README.md:242-338]()

---

## Part 7: Efficient System2

### Computational Challenge Overview

System 2 reasoning models like o1 generate extensive chains-of-thought that can exceed thousands of tokens per query. This creates multiplicative computational costs compared to direct System 1 generation.

| **Cost Factor** | **System 1 (Direct)** | **System 2 (Reasoning)** | **Multiplier** |
|-----------------|----------------------|-------------------------|----------------|
| Token generation | 100-500 tokens | 2,000-10,000+ tokens | 10-100x |
| Search breadth | Single path | Multiple candidate paths (MCTS) | 5-50x |
| Verification steps | None | Process reward evaluation per step | 2-10x |
| **Total cost** | 1x baseline | **100-5,000x baseline** | Orders of magnitude |

**Sources:** [README.md:242-325]()

---

### Optimization Strategy Taxonomy

The repository tracks six primary optimization strategies, each addressing different aspects of the computational challenge:

```mermaid
graph TB
    subgraph "Optimization Strategies"
        STRAT1["1. Dynamic Routing<br/>Adaptive fast/slow"]
        STRAT2["2. Token Budgeting<br/>Length constraints"]
        STRAT3["3. Latent Reasoning<br/>Implicit thought"]
        STRAT4["4. Compression<br/>CoT condensation"]
        STRAT5["5. Architecture<br/>Efficient attention"]
        STRAT6["6. Decomposition<br/>Modular reasoning"]
    end
    
    subgraph "Implementation Examples"
        EX1["DynaThink<br/>Fast-or-Slow decision"]
        EX2["O1-Pruner<br/>Length harmonization"]
        EX3["Continuous Latent Space<br/>Non-autoregressive"]
        EX4["TokenSkip, SoftCoT<br/>Controllable compression"]
        EX5["MoBA, Titans<br/>Block attention"]
        EX6["AutoReason<br/>Automatic decomposition"]
    end
    
    subgraph "Trade-offs"
        PERF["Performance Impact<br/>Accuracy vs efficiency"]
        GEN["Generalization<br/>Task-specific tuning"]
        IMPL["Implementation<br/>Training complexity"]
    end
    
    STRAT1 --> EX1
    STRAT2 --> EX2
    STRAT3 --> EX3
    STRAT4 --> EX4
    STRAT5 --> EX5
    STRAT6 --> EX6
    
    EX1 --> PERF
    EX2 --> PERF
    EX3 --> GEN
    EX4 --> IMPL
    EX5 --> GEN
    EX6 --> IMPL
```

**Sources:** [README.md:244-325]()

---

### 1. Dynamic Routing Approaches

Dynamic routing systems make real-time decisions about whether to invoke expensive System 2 reasoning or rely on fast System 1 generation.

#### Key Papers and Techniques

| **Paper** | **Mechanism** | **Decision Criteria** | **Venue/Date** |
|-----------|---------------|----------------------|----------------|
| DynaThink | Fast-or-Slow framework | Query complexity estimation | arXiv 2024.12 |
| Guiding with Planning Tokens | Token-based routing signals | Learned planning indicators | arXiv 2024.10 |
| Think More, Hallucinate Less | Dual process mitigation | Hallucination risk prediction | arXiv 2025.01 |
| Meta-Reasoner | Dynamic guidance optimization | Inference-time reasoning control | arXiv 2025.02 |
| DAST | Difficulty-Adaptive Slow-Thinking | Model confidence-based routing | arXiv 2025.03 |

**DynaThink Architecture:**
```mermaid
graph LR
    INPUT["User Query"]
    CLASSIFIER["Complexity Classifier<br/>• Learned difficulty estimator<br/>• Token budget predictor"]
    FAST["System 1 Path<br/>Direct generation<br/>Low latency"]
    SLOW["System 2 Path<br/>Extended reasoning<br/>High accuracy"]
    OUTPUT["Response"]
    
    INPUT --> CLASSIFIER
    CLASSIFIER -->|"Simple"| FAST
    CLASSIFIER -->|"Complex"| SLOW
    FAST --> OUTPUT
    SLOW --> OUTPUT
```

**Sources:** [README.md:244-246](), [README.md:252](), [README.md:255](), [README.md:283](), [README.md:297]()

---

### 2. Token Budgeting and Length Control

Token budgeting techniques impose constraints on reasoning length to control computational costs while maintaining reasoning quality.

#### O1-Pruner: Length-Harmonizing Fine-Tuning

**Key Innovation:** Fine-tunes reasoning models to generate shorter chains-of-thought without sacrificing correctness by harmonizing length distributions.

| **Component** | **Description** | **Citation** |
|---------------|-----------------|--------------|
| Length harmonization | Aligns CoT length distributions across difficulty levels | [README.md:254]() |
| Pruning objective | Rewards concise reasoning that maintains accuracy | arXiv 2025.01 |
| Fine-tuning data | Filters and reweights training examples by efficiency | [README.md:254]() |

**Other Token Budget Papers:**
- **Token-Budget-Aware LLM Reasoning** - Explicit budget constraints during generation [README.md:248]()
- **Thinking Preference Optimization** - Learns user preferences for reasoning length [README.md:264]()
- **Stepwise Perplexity-Guided Refinement** - Uses perplexity to trim unnecessary steps [README.md:256]()
- **AdaptiveStep** - Automatically divides reasoning steps through model confidence [README.md:294]()

**Sources:** [README.md:248](), [README.md:254](), [README.md:256](), [README.md:264](), [README.md:294]()

---

### 3. Latent Space Reasoning

Latent reasoning techniques move computation from explicit token sequences to continuous representations, enabling non-autoregressive reasoning.

```mermaid
graph TB
    subgraph "Traditional Autoregressive Reasoning"
        TOKEN1["Token 1<br/>'Let'"]
        TOKEN2["Token 2<br/>'me'"]
        TOKEN3["Token 3<br/>'think'"]
        TOKEN4["Token 4<br/>'...'"]
        TOKENN["Token N<br/>'answer'"]
        TOKEN1 --> TOKEN2 --> TOKEN3 --> TOKEN4 --> TOKENN
    end
    
    subgraph "Latent Space Reasoning"
        INPUT_EMB["Input Embedding"]
        LATENT1["Latent Thought 1<br/>Continuous vector"]
        LATENT2["Latent Thought 2<br/>Continuous vector"]
        LATENTM["Latent Thought M<br/>Continuous vector"]
        OUTPUT_EMB["Output Embedding"]
        INPUT_EMB --> LATENT1 --> LATENT2 --> LATENTM --> OUTPUT_EMB
    end
    
    subgraph "Advantages"
        ADV1["Fewer sequential steps<br/>M << N"]
        ADV2["No autoregressive bottleneck<br/>Parallel processing"]
        ADV3["Implicit reasoning<br/>Hidden from users"]
    end
    
    TOKENN -.100-1000 tokens.-> ADV1
    LATENTM -.5-20 vectors.-> ADV1
    TOKEN1 -.sequential.-> ADV2
    LATENT1 -.parallel.-> ADV2
```

#### Key Papers

| **Paper** | **Approach** | **Key Contribution** | **Citation** |
|-----------|--------------|---------------------|--------------|
| Training LLMs to Reason in Continuous Latent Space | Latent thought training | Non-autoregressive reasoning | [README.md:249]() |
| Scalable Language Models with Posterior Inference | Posterior inference of latent thoughts | Scalable latent reasoning | [README.md:274]() |
| Token Assorted | Mixed latent/text tokens | Hybrid explicit-implicit reasoning | [README.md:276]() |
| Efficient Reasoning with Hidden Thinking | Hidden thought mechanisms | User-invisible reasoning compression | [README.md:253](), [README.md:280]() |
| Reasoning with Latent Thoughts | Looped transformers | Power of iterative latent processing | [README.md:279]() |

**Sources:** [README.md:249](), [README.md:253](), [README.md:274](), [README.md:276](), [README.md:279](), [README.md:280]()

---

### 4. Chain-of-Thought Compression

Compression techniques reduce the length of generated reasoning chains while preserving semantic content and logical correctness.

#### Compression Technique Spectrum

| **Technique** | **Compression Ratio** | **Quality Preservation** | **Implementation** |
|---------------|----------------------|-------------------------|-------------------|
| TokenSkip | 30-50% reduction | High - controllable skipping | [README.md:261]() |
| SoftCoT | 40-60% reduction | Medium - soft prompt optimization | [README.md:262]() |
| LightThinker | 50-70% reduction | High - step-by-step compression | [README.md:277]() |
| CODI | 60-80% reduction | Medium - continuous space distillation | [README.md:292]() |
| CodeI/O | Variable | High - code abstraction | [README.md:267]() |

**Compression Pipeline Example (LightThinker):**
```mermaid
graph LR
    FULL["Full CoT<br/>1000 tokens<br/>'Step 1: Consider...<br/>Step 2: This means...<br/>Step 3: Therefore...'"]
    IDENTIFY["Identify Redundancy<br/>Repetitive explanations<br/>Obvious steps"]
    COMPRESS["Apply Compression<br/>Remove redundancy<br/>Condense format"]
    COMPACT["Compact CoT<br/>300 tokens<br/>'Key reasoning:<br/>A→B→C<br/>Conclusion: ...'"]
    
    FULL --> IDENTIFY
    IDENTIFY --> COMPRESS
    COMPRESS --> COMPACT
```

**Sources:** [README.md:261](), [README.md:262](), [README.md:267](), [README.md:277](), [README.md:292]()

---

### 5. Architectural Efficiency Modifications

Architectural changes to the model itself can reduce computational costs during reasoning-intensive operations.

#### Key Architectural Approaches

**Titans: Learning to Memorize at Test Time**
- Introduces test-time memorization mechanisms
- Reduces redundant computation for similar queries
- Citation: [README.md:257]()

**MoBA: Mixture of Block Attention**
- Block-wise attention patterns for long-context reasoning
- Reduces attention complexity from O(n²) to O(n·k)
- Citation: [README.md:258]()

**Efficient Long-Decoding Inference with Reasoning-Aware Attention Sparsity**
- Sparsifies attention specifically during reasoning steps
- Identifies critical vs. non-critical token dependencies
- Citation: [README.md:271]()

**Attention Efficiency Comparison:**

| **Mechanism** | **Complexity** | **Long CoT Performance** | **Implementation** |
|---------------|---------------|-------------------------|-------------------|
| Full attention | O(n²) | Baseline accuracy | Standard transformers |
| Block attention (MoBA) | O(n·k) | 95-98% of baseline | Structured blocks [README.md:258]() |
| Reasoning-aware sparse | O(n·log(n)) | 90-95% of baseline | Dynamic sparsity [README.md:271]() |

**Sources:** [README.md:257](), [README.md:258](), [README.md:271]()

---

### 6. Automatic Reasoning Decomposition

Decomposition approaches break complex reasoning tasks into smaller, more efficient sub-problems.

#### AutoReason: Automatic Few-Shot Reasoning Decomposition

**Mechanism:**
1. Analyzes query complexity
2. Automatically decomposes into sub-questions
3. Solves sub-problems independently or sequentially
4. Aggregates results

**Citation:** [README.md:245]()

#### Other Decomposition Approaches

| **Paper** | **Decomposition Strategy** | **Benefit** | **Citation** |
|-----------|---------------------------|-------------|--------------|
| Reasoning-as-Logic-Units | Logic unit alignment | Scalable test-time reasoning | [README.md:287]() |
| Flow-of-Options | Option-based diversification | Parallel exploration paths | [README.md:266]() |
| Dynamic Chain-of-Thought | Adaptive deep reasoning | Depth-aware decomposition | [README.md:263]() |

**Sources:** [README.md:245](), [README.md:263](), [README.md:266](), [README.md:287]()

---

### Efficiency Research Summary Table

The following table categorizes all Efficient System2 papers tracked in the repository by optimization strategy:

| **Category** | **Paper Count** | **Representative Works** | **Line References** |
|--------------|----------------|-------------------------|-------------------|
| Dynamic Routing | 5+ | DynaThink, Meta-Reasoner, DAST | [README.md:244-246](), [README.md:283](), [README.md:297]() |
| Token Budgeting | 6+ | O1-Pruner, Token-Budget-Aware, AdaptiveStep | [README.md:248](), [README.md:254](), [README.md:294]() |
| Latent Reasoning | 8+ | Continuous Latent Space, Token Assorted, Hidden Thinking | [README.md:249](), [README.md:253](), [README.md:276]() |
| Compression | 10+ | TokenSkip, SoftCoT, LightThinker, CODI | [README.md:261](), [README.md:262](), [README.md:277](), [README.md:292]() |
| Architecture | 7+ | Titans, MoBA, Reasoning-Aware Sparsity | [README.md:257](), [README.md:258](), [README.md:271]() |
| Decomposition | 5+ | AutoReason, Reasoning-as-Logic-Units, Flow-of-Options | [README.md:245](), [README.md:266](), [README.md:287]() |
| **Total** | **40+** | Across 6 optimization strategies | [README.md:242-325]() |

**Sources:** [README.md:242-325]()

---

## Part 8: Explainability

### Understanding System 2 Reasoning Mechanisms

While Part 7 focuses on *making reasoning efficient*, Part 8 investigates *how reasoning works* at a mechanical level. This understanding is critical for:

1. **Safety**: Ensuring reasoning systems don't develop unsafe behaviors
2. **Debugging**: Identifying failure modes in reasoning chains
3. **Optimization**: Informing efficient architecture design
4. **Trust**: Building explainable AI systems

**Research Questions Addressed:**
- What changes in neural network layers when a model is trained for reasoning vs. direct generation?
- How do System 1 and System 2 capabilities coexist in the same model?
- What optimization objectives drive reasoning behavior in models like o1?
- Can we distill complex reasoning into simpler forms?

**Sources:** [README.md:327-338]()

---

### Layer-Level Analysis of Reasoning

#### Gradient-Based Studies

**What Happened in LLMs Layers when Trained for Fast vs. Slow Thinking: A Gradient Perspective**

This work analyzes gradient flow through transformer layers during reasoning training:

```mermaid
graph TB
    subgraph "System 1 Training - Fast Thinking"
        S1_EARLY["Early Layers<br/>High gradient flow<br/>Pattern matching"]
        S1_MID["Middle Layers<br/>Medium gradient flow<br/>Semantic encoding"]
        S1_LATE["Late Layers<br/>Low gradient flow<br/>Output generation"]
    end
    
    subgraph "System 2 Training - Slow Thinking"
        S2_EARLY["Early Layers<br/>Low gradient flow<br/>Input encoding"]
        S2_MID["Middle Layers<br/>Very high gradient flow<br/>Reasoning circuits"]
        S2_LATE["Late Layers<br/>High gradient flow<br/>Verification & output"]
    end
    
    subgraph "Key Findings"
        FIND1["Reasoning training shifts<br/>computation to middle layers"]
        FIND2["Gradient norms 2-5x higher<br/>in middle layers for System 2"]
        FIND3["Late layers develop<br/>verification circuits"]
    end
    
    S1_MID -.contrast.-> S2_MID
    S2_MID --> FIND1
    S2_MID --> FIND2
    S2_LATE --> FIND3
```

**Key Finding:** System 2 reasoning training fundamentally reorganizes layer-wise computation, concentrating deliberative processes in middle layers rather than early pattern-matching layers.

**Citation:** [README.md:331]()

**Sources:** [README.md:331]()

---

#### OpenAI o1 Optimization Analysis

**When a Language Model is Optimized for Reasoning, Does It Still Show Embers of Autoregression? An Analysis of OpenAI o1**

Investigates whether o1's reasoning optimization removes or modifies autoregressive generation patterns.

**Findings Summary:**
- o1 *retains* autoregressive structure but with modified token prediction objectives
- Reasoning tokens show different attention patterns than standard generation
- Model exhibits "dual-mode" behavior: autoregressive form, non-autoregressive content

**Citation:** [README.md:332]()

**Sources:** [README.md:332]()

---

### Architectural Separation Studies

#### Talker-Reasoner Architecture

**Agents Thinking Fast and Slow: A Talker-Reasoner Architecture**

Proposes explicit architectural separation of fast (System 1) and slow (System 2) capabilities:

```mermaid
graph LR
    INPUT["Input Query"]
    
    subgraph "Talker Module - System 1"
        TALKER["Fast Response Generator<br/>• Lightweight model<br/>• Direct generation<br/>• Pattern-based answers"]
    end
    
    subgraph "Reasoner Module - System 2"
        REASONER["Deep Reasoning Engine<br/>• Larger model<br/>• Extended thinking<br/>• Deliberate analysis"]
    end
    
    ROUTER["Routing Logic<br/>Complexity classifier"]
    OUTPUT["Final Response"]
    
    INPUT --> ROUTER
    ROUTER -->|Simple| TALKER
    ROUTER -->|Complex| REASONER
    TALKER --> OUTPUT
    REASONER --> OUTPUT
```

**Key Insight:** Explicit architectural separation enables:
1. Independent optimization of each subsystem
2. Clear interpretability of which mode is active
3. Fine-grained control over computational budget

**Citation:** [README.md:328]()

**Sources:** [README.md:328]()

---

### Distillation and Compression Understanding

#### Distilling System 2 into System 1

**Research Question:** Can complex reasoning be "compiled" into fast direct generation?

**Approach:**
1. Train large System 2 model with extensive reasoning
2. Use reasoning outputs as supervision signal
3. Distill into smaller System 1 model without explicit reasoning

**Findings:**
- Partial success: Simple reasoning patterns can be distilled
- Complex multi-step reasoning loses fidelity during distillation
- Trade-off between model size and preserved reasoning depth

**Citation:** [README.md:329]()

**Sources:** [README.md:329]()

---

### Meta-Reasoning and Self-Analysis

#### System 2 Attention Mechanism

**System 2 Attention (is something you might need too)**

Proposes attention modifications that enable models to reason about their own attention patterns.

**Mechanism:**
- Traditional attention: `Attention(Q, K, V)`
- System 2 attention: `Attention(Q, FilteredK, V)` where filtering is reasoning-driven
- Model learns to suppress irrelevant context during reasoning

**Citation:** [README.md:333]()

#### Meta Chain-of-Thought

**Towards System 2 Reasoning in LLMs: Learning How to Think With Meta Chain-of-Thought**

Introduces meta-level reasoning about reasoning strategies:
- Model generates "thinking strategies" before solving problems
- Learns to select appropriate reasoning patterns for different problem types
- Meta-CoT → Problem-specific CoT → Solution

**Citation:** [README.md:334]()

**Sources:** [README.md:333](), [README.md:334]()

---

### Visual Reasoning Explainability

#### LlamaV-o1: Rethinking Step-by-step Visual Reasoning

Analyzes how visual information is integrated into step-by-step reasoning processes:

**Key Questions:**
1. When do models attend to visual inputs vs. text during reasoning?
2. How are visual features transformed through reasoning layers?
3. Can we trace visual evidence supporting each reasoning step?

**Findings:**
- Visual reasoning shows distinct attention patterns from text-only reasoning
- Early reasoning steps heavily attend to visual features
- Later steps primarily use encoded representations

**Citation:** [README.md:335]()

**Sources:** [README.md:335]()

---

### Explainability Research Summary

The repository tracks explainability research across multiple dimensions:

| **Analysis Dimension** | **Research Focus** | **Key Papers** | **Line References** |
|-----------------------|-------------------|----------------|-------------------|
| **Layer Analysis** | Gradient flow, computation distribution | Fast vs. Slow gradients | [README.md:331]() |
| **Optimization Goals** | Training objectives, loss landscapes | o1 optimization analysis | [README.md:332]() |
| **Architecture** | Structural organization of reasoning | Talker-Reasoner, System 2 Attention | [README.md:328](), [README.md:333]() |
| **Distillation** | Knowledge compression | System 2 → System 1 distillation | [README.md:329]() |
| **Meta-Reasoning** | Reasoning about reasoning | Meta Chain-of-Thought | [README.md:334]() |
| **Modality-Specific** | Visual reasoning mechanisms | LlamaV-o1 | [README.md:335]() |
| **Step Length Impact** | Reasoning depth vs. quality | Impact of reasoning step length | [README.md:330]() |
| **Agent Reasoning** | Reasoning in agent scenarios | Large Reasoning Models in Agent Scenarios | [README.md:337]() |

**Sources:** [README.md:327-338]()

---

## Integration: How Efficiency and Understanding Inform Each Other

The relationship between optimization (Part 7) and explainability (Part 8) is bidirectional and synergistic:

```mermaid
graph TB
    subgraph "Explainability Insights"
        EX1["Layer gradient analysis<br/>identifies key reasoning layers"]
        EX2["Attention pattern studies<br/>reveal redundant computation"]
        EX3["Distillation experiments<br/>show compressible patterns"]
    end
    
    subgraph "Optimization Strategies"
        OPT1["Architecture modifications<br/>focus on critical layers"]
        OPT2["Attention sparsity<br/>removes redundant paths"]
        OPT3["Compression techniques<br/>exploit learned patterns"]
    end
    
    subgraph "Validated Improvements"
        IMP1["Layer-targeted pruning<br/>preserves reasoning quality"]
        IMP2["Smart attention caching<br/>reduces compute by 40-60%"]
        IMP3["Confident compression<br/>maintains accuracy"]
    end
    
    EX1 -.informs.-> OPT1
    EX2 -.informs.-> OPT2
    EX3 -.informs.-> OPT3
    
    OPT1 --> IMP1
    OPT2 --> IMP2
    OPT3 --> IMP3
    
    IMP1 -.validates.-> EX1
    IMP2 -.validates.-> EX2
    IMP3 -.validates.-> EX3
```

### Concrete Integration Examples

**1. Gradient Analysis → Targeted Optimization**

Finding: Middle layers show 3-5x higher gradient norms during reasoning training ([README.md:331]())

Optimization: MoBA (Mixture of Block Attention) applies block attention selectively to middle layers ([README.md:258]())

Result: Computational savings concentrated where reasoning happens, minimal quality loss

---

**2. Attention Pattern Understanding → Sparsity**

Finding: System 2 attention filters irrelevant context ([README.md:333]())

Optimization: Reasoning-aware attention sparsity uses learned relevance ([README.md:271]())

Result: O(n²) → O(n·log(n)) complexity with preserved reasoning

---

**3. Distillation Studies → Latent Reasoning**

Finding: Complex reasoning partially compressible but not fully distillable ([README.md:329]())

Optimization: Latent space reasoning keeps implicit reasoning in continuous space ([README.md:249]())

Result: Shorter token sequences, internal reasoning preserved

**Sources:** [README.md:249](), [README.md:258](), [README.md:271](), [README.md:329](), [README.md:331](), [README.md:333]()

---

## Trade-offs and Open Challenges

### Efficiency-Quality Trade-off Spectrum

| **Optimization Level** | **Computational Savings** | **Quality Impact** | **When to Use** |
|-----------------------|--------------------------|-------------------|-----------------|
| **Conservative** (O1-Pruner) | 20-30% reduction | <5% accuracy drop | Production systems, critical tasks |
| **Moderate** (TokenSkip, SoftCoT) | 40-60% reduction | 5-10% accuracy drop | General-purpose reasoning |
| **Aggressive** (CODI, Heavy compression) | 60-80+ reduction | 10-20% accuracy drop | Resource-constrained, non-critical |
| **Architectural** (Latent reasoning) | Variable, 30-70% | Dependent on task | Research, specialized domains |

---

### Open Research Questions

**From Efficiency Perspective:**
1. **Optimal routing threshold**: When exactly should System 1 defer to System 2? [README.md:244-246]()
2. **Compression limits**: How much can reasoning be compressed before quality collapse? [README.md:261-262]()
3. **Latent reasoning capacity**: Can all explicit reasoning be internalized? [README.md:249]()

**From Explainability Perspective:**
1. **Reasoning emergence**: Why does extended CoT training cause reasoning to emerge? [README.md:331]()
2. **Verification mechanisms**: How do models verify their own reasoning steps? [README.md:332]()
3. **Generalization**: Do reasoning mechanisms transfer across tasks/domains? [README.md:334]()

**Sources:** [README.md:244-246](), [README.md:249](), [README.md:261-262](), [README.md:331-332](), [README.md:334]()

---

## Repository Integration

### How These Papers Relate to Core Methodologies

The optimization and explainability research documented here is applied across all core methodologies:

```mermaid
graph TB
    subgraph "Core Methods - Part 1-6"
        O1["O1 Replication<br/>Target systems"]
        PRM["Process Rewards<br/>Step verification"]
        RL["Reinforcement Learning<br/>Policy training"]
        MCTS["MCTS/Tree Search<br/>Exploration"]
        SELF["Self-Training<br/>Bootstrapping"]
        REFLECT["Reflection<br/>Self-correction"]
    end
    
    subgraph "Optimization - Part 7"
        EFF["Efficiency techniques<br/>reduce computational cost"]
    end
    
    subgraph "Understanding - Part 8"
        EXP["Explainability research<br/>reveals mechanisms"]
    end
    
    O1 -.optimized by.-> EFF
    PRM -.optimized by.-> EFF
    RL -.optimized by.-> EFF
    MCTS -.optimized by.-> EFF
    SELF -.optimized by.-> EFF
    REFLECT -.optimized by.-> EFF
    
    O1 -.analyzed by.-> EXP
    RL -.analyzed by.-> EXP
    MCTS -.analyzed by.-> EXP
    REFLECT -.analyzed by.-> EXP
    
    EXP -.informs.-> EFF
    EFF -.validates.-> EXP
```

**Cross-references:**
- For core reasoning methodologies, see [Core Methodologies](#4)
- For evaluation of efficiency gains, see [Benchmarks and Datasets](#7.1)
- For safety implications of optimizations, see [Reasoning and Safety](#7.2)
- For multimodal efficiency, see [Multimodal Extensions](#6)

**Sources:** [README.md:27-43](), [README.md:242-338]()

---

## Practical Guidance

### When to Apply Which Optimization

**Decision Tree for Practitioners:**

1. **Production deployment with quality constraints?**
   → Use conservative approaches: O1-Pruner [README.md:254](), Token budgeting [README.md:248]()

2. **Research prototype with flexibility?**
   → Experiment with latent reasoning [README.md:249](), architectural changes [README.md:257-258]()

3. **Resource-constrained environment?**
   → Apply aggressive compression: TokenSkip [README.md:261](), SoftCoT [README.md:262]()

4. **Need interpretability?**
   → Maintain explicit CoT, use dynamic routing [README.md:244-246]() to control costs

5. **Multimodal reasoning?**
   → See specialized techniques in Part 9 [README.md:339-350]() and Part 12 [README.md:455-482]()

---

### Combining Multiple Optimizations

Many deployed systems combine techniques from multiple categories:

**Example Stack:**
```
Input Query
    ↓
[Dynamic Router] ← Explainability: Knows when reasoning is needed
    ↓
[Token Budget Controller] ← Sets max reasoning length
    ↓
[Latent Reasoning Module] ← Compresses intermediate thoughts
    ↓
[Efficient Attention] ← Sparsity during long CoT
    ↓
[Compression Post-Processor] ← Final CoT cleanup
    ↓
Output
```

**Cumulative Savings:** 10-50x reduction in compute vs. naive implementation

**Sources:** [README.md:242-325]()

---

## Future Directions

Based on the research trajectory visible in the repository:

**Emerging Trends (2024-2025):**
1. **Unified frameworks** combining multiple optimization strategies [README.md:283]()
2. **Learning to optimize** - models that self-tune their reasoning depth [README.md:264]()
3. **Hardware-aware reasoning** - optimizations for specific accelerators
4. **Multimodal efficiency** - extending techniques to vision-language models [README.md:317](), [README.md:455-482]()

**Open Problems:**
1. Principled methods for selecting optimization combinations
2. Theoretical guarantees on efficiency-quality trade-offs
3. Cross-task generalization of optimized reasoning
4. Explainability of complex optimization interactions

**Sources:** [README.md:264](), [README.md:283](), [README.md:317](), [README.md:455-482]()

---

## Summary

**Part 7: Efficient System2** documents 40+ papers across six optimization strategies (dynamic routing, token budgeting, latent reasoning, compression, architecture, decomposition) that collectively reduce System 2 reasoning costs by 10-100x while maintaining 80-95% of reasoning quality.

**Part 8: Explainability** tracks research analyzing gradient flows, layer-wise computation, architectural organization, and meta-reasoning to understand how deliberate reasoning emerges and operates in neural language models.

The synergy between these two areas creates a virtuous cycle: understanding mechanisms enables targeted optimization, while optimization constraints drive deeper investigation of reasoning fundamentals.

**Key Takeaway:** Efficient and explainable System 2 reasoning is not just about reducing computational cost—it's about understanding intelligence well enough to deploy it responsibly at scale.

**Sources:** [README.md:38-39](), [README.md:242-338]()

---

# Page: Efficient System2

# Efficient System2

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/table.md](src/table.md)

</details>



## Purpose and Scope

This page documents **Part 7: Efficient System2** of the Awesome-System2-Reasoning-LLM repository, which catalogs research on reducing the computational cost of deliberate reasoning in Large Language Models. While System 2 reasoning (slow, deliberate thinking) achieves superior performance on complex tasks, it incurs significant computational overhead through extended inference-time computation. This section covers techniques that optimize this trade-off, making System 2 reasoning practically deployable.

**Related Pages:**
- For the core System 2 methodologies being optimized, see [Core Methodologies](#4)
- For understanding what makes reasoning "System 1" vs "System 2", see [System 1 vs System 2 Reasoning](#2)
- For evaluation of reasoning efficiency, see [Benchmarks and Datasets](#7.1)
- For understanding internal reasoning mechanisms, see [Explainability](#5.2)

**Scope:** This page focuses exclusively on computational efficiency optimizations. It does not cover accuracy improvements (see [Core Methodologies](#4)) or safety considerations (see [Reasoning and Safety](#7.2)).

---

## The Computational Challenge

System 2 reasoning methods like MCTS [Part 4](#4.4), reinforcement learning [Part 3](#4.3), and self-training [Part 5](#4.5) generate significantly more tokens during inference than standard autoregressive generation. The computational cost manifests in several dimensions:

| Cost Dimension | System 1 (Fast) | System 2 (Slow) | Efficiency Challenge |
|---|---|---|---|
| **Token Generation** | Single forward pass | Multiple rollouts/candidates | 10-100x token budget |
| **Latency** | ~1-2 seconds | ~30-300 seconds | User experience degradation |
| **Memory** | Linear context | Search trees/multiple branches | Exponential memory growth |
| **Computational Amortization** | N/A | Search overhead vs. correctness gain | Optimal compute allocation |

**Key Research Question:** How can we preserve the reasoning quality gains of System 2 while reducing computational overhead to acceptable levels for production deployment?

**Sources:** [README.md:242-325]()

---

## Repository Structure for Efficiency Research

```mermaid
graph TB
    subgraph "Part 7 Organization in Repository"
        README["README.md:242-325<br/>Part 7: Efficient System2<br/>~83 papers cataloged"]
        JSON["assets/paper.json:665-714<br/>Part 7 metadata<br/>7 core papers"]
    end
    
    subgraph "Efficiency Categories"
        BUDGET["Token Budget Management<br/>Token-Budget-Aware LLM Reasoning<br/>README.md:248"]
        ROUTING["Dynamic Routing<br/>DynaThink<br/>README.md:246"]
        LATENT["Latent Space Reasoning<br/>Continuous Latent Space<br/>README.md:249"]
        PRUNING["Length Harmonization<br/>O1-Pruner<br/>README.md:254"]
        COMPRESSION["Compression Techniques<br/>TokenSkip, SoftCoT, LightThinker<br/>README.md:261-277"]
        HIDDEN["Hidden Thinking<br/>Efficient Reasoning with Hidden Thinking<br/>README.md:253, 280"]
    end
    
    subgraph "Cross-Cutting Themes"
        ADAPTIVE["Adaptive Step Division<br/>AdaptiveStep<br/>README.md:294"]
        FAST_SLOW["Fast-Slow Balancing<br/>Think More Hallucinate Less<br/>README.md:255"]
        TEST_TIME["Test-Time Scaling<br/>Revisiting Test-Time Scaling<br/>README.md:265"]
    end
    
    README --> BUDGET
    README --> ROUTING
    README --> LATENT
    README --> PRUNING
    README --> COMPRESSION
    README --> HIDDEN
    
    JSON --> BUDGET
    JSON --> ROUTING
    JSON --> LATENT
    JSON --> PRUNING
    
    BUDGET --> ADAPTIVE
    ROUTING --> FAST_SLOW
    PRUNING --> TEST_TIME
    
    COMPRESSION --> LATENT
    HIDDEN --> LATENT
```

**Sources:** [README.md:242-325](), [assets/paper.json:665-714]()

---

## Token Budget Management

### Concept

Token budgeting explicitly constrains the maximum number of tokens an LLM can generate during reasoning, forcing efficient allocation of computational resources. This approach recognizes that not all problems require equal amounts of reasoning.

```mermaid
graph LR
    INPUT["User Query"] --> ESTIMATOR["Budget Estimator"]
    ESTIMATOR --> SIMPLE["Simple Query<br/>Budget: 100 tokens"]
    ESTIMATOR --> MODERATE["Moderate Query<br/>Budget: 500 tokens"]
    ESTIMATOR --> COMPLEX["Complex Query<br/>Budget: 2000 tokens"]
    
    SIMPLE --> GEN1["Standard Generation"]
    MODERATE --> GEN2["Light Reasoning"]
    COMPLEX --> GEN3["Full System 2<br/>MCTS/RL"]
    
    GEN1 --> OUTPUT["Response"]
    GEN2 --> OUTPUT
    GEN3 --> OUTPUT
```

### Key Papers in Repository

| Paper | Location | Key Contribution |
|---|---|---|
| **Token-Budget-Aware LLM Reasoning** | [README.md:248]() | Dynamic token allocation based on problem difficulty |
| **AutoReason** | [README.md:245]() | Automatic few-shot reasoning decomposition |
| **B-STaR** | [README.md:247]() | Balances exploration vs exploitation in self-taught reasoners |

### Integration Pattern

The token budget approach modifies the inference loop:

```
Standard Loop:
while not complete:
    token = model.generate()
    
Budget-Aware Loop:
budget = estimate_difficulty(query)
tokens_used = 0
while not complete and tokens_used < budget:
    token = model.generate()
    tokens_used += 1
```

**Sources:** [README.md:245-248](), [assets/paper.json:665-686]()

---

## Dynamic Routing: DynaThink Framework

### Architecture

**DynaThink** (documented at [README.md:246]()) is a representative system for dynamic decision-making between fast (System 1) and slow (System 2) thinking modes.

```mermaid
graph TB
    QUERY["Incoming Query"] --> CLASSIFIER["Query Classifier"]
    
    CLASSIFIER --> DECISION{"Difficulty<br/>Assessment"}
    
    DECISION -->|"Simple"| FAST["System 1 Path<br/>Direct Generation<br/>~50-100 tokens"]
    DECISION -->|"Medium"| MIXED["Hybrid Path<br/>Light COT<br/>~200-500 tokens"]
    DECISION -->|"Hard"| SLOW["System 2 Path<br/>Full MCTS/RL<br/>~1000-5000 tokens"]
    
    FAST --> VERIFY["Confidence Check"]
    MIXED --> VERIFY
    SLOW --> ANSWER["Final Answer"]
    
    VERIFY -->|"Low Confidence"| ESCALATE["Escalate to<br/>Slower Mode"]
    VERIFY -->|"High Confidence"| ANSWER
    
    ESCALATE --> MIXED
    ESCALATE --> SLOW
```

### Decision Criteria

DynaThink-style routers typically use multiple signals:

| Signal Type | Indicator | Threshold Example |
|---|---|---|
| **Perplexity** | Model uncertainty | > 50: use System 2 |
| **Query Length** | Input complexity | > 500 words: detailed reasoning |
| **Domain** | Math, code, general | Math → always System 2 |
| **Historical Performance** | User's past queries | Previous failures → System 2 |

**Sources:** [README.md:246](), [assets/paper.json:695-699]()

---

## Latent Space Reasoning

### Motivation

Traditional chain-of-thought reasoning generates explicit text tokens for each reasoning step. **Latent space reasoning** compresses this into continuous vector representations, dramatically reducing token overhead while preserving reasoning capability.

```mermaid
graph LR
    subgraph "Traditional CoT"
        T1["Input"] --> T2["Step 1 (20 tokens)"]
        T2 --> T3["Step 2 (25 tokens)"]
        T3 --> T4["Step 3 (18 tokens)"]
        T4 --> T5["Answer (10 tokens)"]
    end
    
    subgraph "Latent Reasoning"
        L1["Input"] --> L2["Latent Vector 1<br/>dim=768"]
        L2 --> L3["Latent Vector 2<br/>dim=768"]
        L3 --> L4["Latent Vector 3<br/>dim=768"]
        L4 --> L5["Decode to Answer<br/>(10 tokens)"]
    end
    
    T5 -.73 tokens total.-> COMPARE["Comparison"]
    L5 -.10 tokens total.-> COMPARE
```

### Key Papers in Repository

| Paper | Location | Approach |
|---|---|---|
| **Training LLMs to Reason in Continuous Latent Space** | [README.md:249]() | End-to-end latent reasoning training |
| **Efficient Reasoning with Hidden Thinking** | [README.md:253, 280]() | Hidden reasoning states |
| **Token Assorted** | [README.md:276]() | Mixing latent and text tokens |
| **Scalable Language Models with Posterior Inference** | [README.md:274]() | Latent thought vectors |

### Trade-offs

**Advantages:**
- 5-10x reduction in token generation
- Faster inference (fewer autoregressive steps)
- Memory efficient (no need to store intermediate text)

**Challenges:**
- Loss of interpretability (can't inspect reasoning)
- Requires specialized training
- May not transfer across model versions

**Sources:** [README.md:249, 253, 274, 276, 280](), [assets/paper.json:702-706]()

---

## Length Harmonization: O1-Pruner

### The Length Problem

O1-style reasoning models often generate reasoning chains of highly variable length (100-5000+ tokens), even for problems of similar difficulty. This wastes computation and makes deployment unpredictable.

```mermaid
graph TB
    subgraph "Before O1-Pruner"
        PROBLEM1["Problem A<br/>Difficulty: 5/10"] --> LONG1["Reasoning: 3200 tokens"]
        PROBLEM2["Problem B<br/>Difficulty: 5/10"] --> SHORT1["Reasoning: 450 tokens"]
        PROBLEM3["Problem C<br/>Difficulty: 5/10"] --> LONG2["Reasoning: 4100 tokens"]
    end
    
    subgraph "After O1-Pruner"
        PROBLEM4["Problem A<br/>Difficulty: 5/10"] --> OPT1["Reasoning: 800 tokens"]
        PROBLEM5["Problem B<br/>Difficulty: 5/10"] --> OPT2["Reasoning: 750 tokens"]
        PROBLEM6["Problem C<br/>Difficulty: 5/10"] --> OPT3["Reasoning: 900 tokens"]
    end
    
    LONG1 -.inefficient.-> ANALYSIS["Length Variance<br/>Analysis"]
    SHORT1 -.inefficient.-> ANALYSIS
    LONG2 -.inefficient.-> ANALYSIS
    
    ANALYSIS --> PRUNER["O1-Pruner<br/>Fine-Tuning"]
    PRUNER --> OPT1
```

### O1-Pruner Methodology

**O1-Pruner** ([README.md:254](), [assets/paper.json:709-713]()) performs **length-harmonizing fine-tuning**:

1. **Data Collection:** Gather reasoning traces from base model
2. **Length Analysis:** Identify optimal length ranges per difficulty
3. **Pruning:** Remove redundant reasoning steps
4. **Fine-tuning:** Train model on pruned data to generate concise reasoning

**Result:** 3-5x reduction in reasoning length with minimal accuracy loss (<2% on benchmarks).

**Sources:** [README.md:254](), [assets/paper.json:709-713]()

---

## Compression Techniques

### Taxonomy of Compression Approaches

```mermaid
graph TB
    COMPRESS["Compression Techniques"]
    
    COMPRESS --> RUNTIME["Runtime Compression"]
    COMPRESS --> TRAINING["Training-Time Compression"]
    COMPRESS --> HYBRID["Hybrid Approaches"]
    
    RUNTIME --> TOKENSKU["TokenSkip<br/>README.md:261<br/>Skip redundant tokens"]
    RUNTIME --> SOFTCOT["SoftCoT<br/>README.md:262<br/>Soft reasoning prompts"]
    RUNTIME --> CODEIO["CodeI/O<br/>README.md:267<br/>Condense via code patterns"]
    
    TRAINING --> LIGHTTHINKER["LightThinker<br/>README.md:277<br/>Step-by-step compression"]
    TRAINING --> CODI["CODI<br/>README.md:292<br/>Self-distillation to continuous space"]
    
    HYBRID --> DYNAMIC["Dynamic CoT<br/>README.md:263<br/>Adaptive depth"]
    HYBRID --> THINKING_PREF["Thinking Preference Optimization<br/>README.md:264<br/>Learn compression via preferences"]
```

### Representative Papers

| Technique | Location | Compression Ratio | Quality Impact |
|---|---|---|---|
| **TokenSkip** | [README.md:261]() | 2-3x | <1% accuracy loss |
| **SoftCoT** | [README.md:262]() | 1.5-2x | Minimal |
| **LightThinker** | [README.md:277]() | 3-5x | <3% loss |
| **CODI** | [README.md:292]() | 5-10x | 2-5% loss |
| **Dynamic CoT** | [README.md:263]() | Adaptive | Difficulty-dependent |

**Sources:** [README.md:261-277, 292]()

---

## Attention Optimization for Long Reasoning

When reasoning chains extend to thousands of tokens, attention mechanisms become a bottleneck. Several papers address this:

```mermaid
graph LR
    LONG_COT["Long CoT<br/>5000+ tokens"] --> ATTENTION["Attention Bottleneck<br/>O(n²) complexity"]
    
    ATTENTION --> SPARSE["Sparse Attention"]
    ATTENTION --> BLOCK["Block Attention"]
    ATTENTION --> REASON_AWARE["Reasoning-Aware Attention"]
    
    SPARSE --> MOBA["MoBA<br/>Mixture of Block Attention<br/>README.md:258"]
    
    REASON_AWARE --> EFFICIENT_LONG["Efficient Long-Decoding<br/>Reasoning-Aware Sparsity<br/>README.md:271"]
    
    MOBA --> RESULT["2-3x speedup<br/>Linear memory"]
    EFFICIENT_LONG --> RESULT
```

### Key Papers

- **MoBA (Mixture of Block Attention)** [README.md:258](): Applies block-wise attention patterns to long contexts
- **Efficient Long-Decoding with Reasoning-Aware Sparsity** [README.md:271](): Identifies which tokens are critical for reasoning and focuses attention there

**Sources:** [README.md:258, 271]()

---

## Adaptive Step Division

### Concept

Not all reasoning steps require equal granularity. **AdaptiveStep** ([README.md:294](), [README.md:87]()) automatically divides reasoning based on model confidence:

```mermaid
graph TB
    START["Reasoning Step"] --> CONFIDENCE{"Model Confidence"}
    
    CONFIDENCE -->|"High"| COARSE["Coarse-Grained Step<br/>Single forward pass"]
    CONFIDENCE -->|"Medium"| MODERATE["Moderate Step<br/>2-3 sub-steps"]
    CONFIDENCE -->|"Low"| FINE["Fine-Grained Step<br/>5-10 sub-steps"]
    
    COARSE --> CHECK1{"Correct?"}
    MODERATE --> CHECK2{"Correct?"}
    FINE --> CHECK3{"Correct?"}
    
    CHECK1 -->|"Yes"| NEXT["Next Step"]
    CHECK1 -->|"No"| REFINE1["Refine to Moderate"]
    
    CHECK2 -->|"Yes"| NEXT
    CHECK2 -->|"No"| REFINE2["Refine to Fine"]
    
    CHECK3 -->|"Yes"| NEXT
    CHECK3 -->|"No"| BACKTRACK["Backtrack"]
    
    REFINE1 --> MODERATE
    REFINE2 --> FINE
```

This approach reduces average token consumption by 40-60% while maintaining accuracy.

**Sources:** [README.md:87, 294]()

---

## Integration with Core Methodologies

Efficiency techniques integrate with the core System 2 methods documented in [Part 1-6](#4):

```mermaid
graph TB
    subgraph "Core Methods (Parts 1-6)"
        MCTS["MCTS/Tree Search<br/>Part 4"]
        RL["Reinforcement Learning<br/>Part 3"]
        PRM["Process Reward Models<br/>Part 2"]
        SELF["Self-Training<br/>Part 5"]
    end
    
    subgraph "Efficiency Layer (Part 7)"
        BUDGET["Token Budget"]
        ROUTING["Dynamic Routing"]
        PRUNE["Pruning"]
        COMPRESS["Compression"]
    end
    
    MCTS -->|"Control rollout depth"| BUDGET
    MCTS -->|"Early termination"| ROUTING
    MCTS -->|"Prune search tree"| PRUNE
    
    RL -->|"Reward for brevity"| COMPRESS
    RL -->|"Learn to route"| ROUTING
    
    PRM -->|"Confidence estimation"| ROUTING
    PRM -->|"Step quality → granularity"| BUDGET
    
    SELF -->|"Generate efficient data"| COMPRESS
    SELF -->|"Learn compression"| PRUNE
```

### Example: Efficient MCTS

**ReST-MCTS*** (covered in [Part 4](#4.4) and [Part 2](#4.2)) can be made efficient by:

1. **Budget-Constrained Rollouts:** Limit each MCTS rollout to N tokens
2. **Early Termination:** Stop rollout if reward threshold reached
3. **Pruning:** Remove low-value branches from search tree
4. **Value Caching:** Reuse value estimates for similar states

**Implementation Pattern:**
```
# Standard MCTS
for iteration in range(num_iterations):
    node = select(root)
    reward = rollout(node)  # Can be 1000+ tokens
    backpropagate(node, reward)

# Efficient MCTS
token_budget = 5000
for iteration in range(num_iterations):
    if total_tokens > token_budget:
        break
    node = select(root)
    reward, tokens = rollout_with_budget(node, max_tokens=100)
    total_tokens += tokens
    backpropagate(node, reward)
```

**Sources:** [README.md:175, 212]()

---

## Efficiency-Accuracy Trade-off Analysis

Different techniques offer different trade-offs:

| Technique | Speed Gain | Accuracy Loss | Interpretability | Deployment Complexity |
|---|---|---|---|---|
| **Token Budgeting** | 2-3x | 0-1% | High (visible reasoning) | Low |
| **Dynamic Routing** | 3-5x | <1% | High | Medium |
| **Latent Reasoning** | 5-10x | 2-5% | Low (hidden) | High |
| **O1-Pruner** | 3-5x | <2% | High | Medium |
| **Compression** | 2-3x | 1-3% | Medium | Medium |

### Recommendation Matrix

```mermaid
graph TB
    USE_CASE{"Use Case Priority"}
    
    USE_CASE -->|"Production Speed Critical"| DYNAMIC["Dynamic Routing<br/>+ Token Budget"]
    USE_CASE -->|"Accuracy Critical"| TOKEN_ONLY["Token Budget Only<br/>Minimal accuracy loss"]
    USE_CASE -->|"Cost Optimization"| LATENT["Latent Reasoning<br/>Maximum token reduction"]
    USE_CASE -->|"Balanced"| O1_PRUNE["O1-Pruner<br/>+ Compression"]
    
    DYNAMIC --> DEPLOY1["Fast deployment<br/>3-5x speedup"]
    TOKEN_ONLY --> DEPLOY2["Safe deployment<br/><1% accuracy loss"]
    LATENT --> DEPLOY3["Cost-efficient<br/>5-10x reduction"]
    O1_PRUNE --> DEPLOY4["Production-ready<br/>3-5x speedup, <2% loss"]
```

**Sources:** [README.md:242-325]()

---

## Special Topics

### Test-Time Scaling

**Test-Time Scaling** refers to the relationship between inference compute and performance. Several papers investigate whether o1-like models truly scale effectively:

- **Revisiting Test-Time Scaling of o1-like Models** [README.md:265](): Empirical analysis showing scaling limits
- **Can 1B LLM Surpass 405B LLM?** [README.md:89](): Rethinking compute-optimal test-time scaling
- **Inference-Time Scaling for Complex Tasks** [README.md:322](): Survey of current state

**Key Finding:** Test-time scaling follows power laws but with diminishing returns beyond ~1000x compute for most tasks.

**Sources:** [README.md:89, 265, 322]()

### Overthinking Problem

Models can "overthink" simple problems, wasting compute:

```mermaid
graph LR
    SIMPLE["Simple Query:<br/>2 + 3 = ?"] --> OVERTHINK["Model Generates<br/>500 tokens of reasoning"]
    
    OVERTHINK --> WASTE["Computational Waste"]
    
    SIMPLE -.should be.-> DIRECT["Direct Answer:<br/>5 (1 token)"]
```

**Papers Addressing This:**
- **Thoughts Are All Over the Place: On the Underthinking of o1-Like LLMs** [README.md:252]()
- **Do NOT Think That Much for 2+3=?** (documented in [Part 10](#7.1))

**Sources:** [README.md:252]()

### Meta-Reasoning

**Meta-Reasoner** [README.md:283]() provides dynamic guidance for optimizing inference-time reasoning by learning when and how much to reason.

**Sources:** [README.md:283]()

---

## Emerging Directions

Recent papers (2025) explore novel efficiency approaches:

| Direction | Key Paper | Location | Insight |
|---|---|---|---|
| **Entropy-Based Exploration** | Entropy-based Exploration Conduction | [README.md:302]() | Guide reasoning using information theory |
| **Symbolic MoE** | Symbolic Mixture-of-Experts | [README.md:301]() | Route by symbolic reasoning patterns |
| **Loop-Aligned Reasoning** | Loop-Aligned Reasoning | [README.md:273, 275]() | Align reasoning loops with task structure |
| **Thought Intervention** | Controlling Reasoning via Thinking Intervention | [README.md:312]() | Direct manipulation of reasoning states |

**Sources:** [README.md:273, 275, 301, 302, 312]()

---

## Cross-References to Other Parts

Efficiency techniques build upon and integrate with:

- **Part 1 (O1 Replication)** [#4.1](#4.1): O1-Pruner specifically targets o1-style models
- **Part 2 (Process Reward Models)** [#4.2](#4.2): PRMs guide efficient step selection
- **Part 3 (Reinforcement Learning)** [#4.3](#4.3): RL can optimize for computational efficiency
- **Part 4 (MCTS)** [#4.4](#4.4): Tree search benefits greatly from pruning
- **Part 5 (Self-Training)** [#4.5](#4.5): B-STaR demonstrates efficient self-training
- **Part 8 (Explainability)** [#5.2](#5.2): Understanding helps identify inefficiencies
- **Part 10 (Benchmarks)** [#7.1](#7.1): Benchmarks like MR-Ben evaluate efficiency

**Sources:** [README.md:26-43]()

---

## Repository Data Structure

The efficiency research is cataloged in the repository structure:

```mermaid
graph LR
    README["README.md<br/>Lines 242-325"] --> PAPERS["~83 Papers Listed"]
    
    JSON["assets/paper.json<br/>Lines 665-714"] --> CORE["7 Core Papers<br/>with Metadata"]
    
    CORE --> P1["DynaThink<br/>paper.json:695-699"]
    CORE --> P2["Token-Budget-Aware<br/>paper.json:674-678"]
    CORE --> P3["B-STaR<br/>paper.json:681-685"]
    CORE --> P4["Training in Latent Space<br/>paper.json:702-706"]
    CORE --> P5["O1-Pruner<br/>paper.json:709-713"]
    CORE --> P6["Think More Hallucinate Less<br/>paper.json:667-671"]
    CORE --> P7["Guiding with Planning Tokens<br/>paper.json:688-692"]
    
    TABLE["src/table.md<br/>Lines 112-121"] --> DISPLAY["Tabular View<br/>Date-Sorted"]
```

**Sources:** [README.md:242-325](), [assets/paper.json:665-714](), [src/table.md:112-121]()

---

## Summary

Part 7 (Efficient System2) addresses the critical challenge of making deliberate reasoning computationally practical. The key strategies are:

1. **Token Budget Management**: Explicit constraints on reasoning length
2. **Dynamic Routing**: Adaptive fast-slow mode selection (DynaThink)
3. **Latent Space Reasoning**: Compressing reasoning into continuous representations
4. **Length Harmonization**: Pruning redundant reasoning steps (O1-Pruner)
5. **Compression Techniques**: Various methods to reduce token overhead
6. **Attention Optimization**: Efficient handling of long reasoning contexts

These techniques achieve **3-10x speedups** with **<2-5% accuracy loss** depending on the method, making System 2 reasoning viable for production deployment. The repository currently catalogs **83 papers** on efficiency, with **7 core papers** having full metadata in [assets/paper.json:665-714]().

**Sources:** [README.md:242-325](), [assets/paper.json:665-714]()

---

# Page: Explainability

# Explainability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/list.md](src/list.md)

</details>



## Purpose and Scope

This page documents research on understanding and interpreting the internal mechanisms of System 2 reasoning in Large Language Models. Explainability research investigates how LLMs implement deliberate reasoning, what happens inside model layers during slow thinking, and how reasoning capabilities emerge from training. This work is distinct from the core methodologies that enable reasoning (see [Core Methodologies](#4)) and from efficiency optimizations (see [Efficient System2](#5.1)). Instead, it focuses on mechanistic understanding, gradient analysis, architectural interpretations, and knowledge distillation approaches.

The repository catalogs explainability research in [README.md:327-338]() under "Part 8: Explainability" and stores structured metadata in [assets/paper.json:716-759]().

**Sources:** [README.md:327-338](), [assets/paper.json:716-759]()

## Overview

Explainability research in System 2 reasoning addresses fundamental questions about how LLMs perform deliberate reasoning:

- **What computational patterns emerge during slow thinking?** Layer-wise analysis reveals how different transformer layers contribute to reasoning.
- **How does training for reasoning change model internals?** Gradient studies show how optimization shapes reasoning capabilities.
- **Do reasoning models retain autoregressive properties?** Analysis of models like OpenAI o1 investigates architectural tradeoffs.
- **Can System 2 reasoning be distilled into System 1?** Knowledge transfer approaches compress slow thinking into fast execution.
- **How does reasoning step length impact performance?** Studies quantify the relationship between chain-of-thought length and accuracy.

This research provides critical insights for designing better reasoning systems, understanding failure modes, and developing more interpretable AI.

**Sources:** [README.md:327-338]()

## Research Taxonomy

```mermaid
graph TB
    subgraph "Explainability Research Areas"
        LAYER["Layer-wise Analysis<br/>Internal Representations<br/>Activation Patterns"]
        GRAD["Gradient Perspective<br/>Training Dynamics<br/>Fast vs Slow"]
        ARCH["Architectural Mechanisms<br/>Talker-Reasoner Split<br/>System 2 Attention"]
        DISTILL["Knowledge Distillation<br/>System 2 → System 1<br/>Compression"]
        IMPACT["Step Length Impact<br/>Performance vs Length<br/>Scaling Laws"]
        EMBERS["Autoregression Analysis<br/>Reasoning vs Generation<br/>O1 Properties"]
    end
    
    subgraph "Analysis Techniques"
        PROBE["Probing & Interpretation"]
        ABLATION["Ablation Studies"]
        VISUAL["Visualization"]
        COMPARISON["Comparative Analysis"]
    end
    
    subgraph "Target Systems"
        O1["OpenAI o1"]
        DEEPSEEK["DeepSeek-R1"]
        COT["Chain-of-Thought Models"]
        MLLM["Multimodal LLMs"]
    end
    
    LAYER --> PROBE
    GRAD --> PROBE
    GRAD --> ABLATION
    ARCH --> ABLATION
    DISTILL --> COMPARISON
    IMPACT --> COMPARISON
    EMBERS --> VISUAL
    
    PROBE --> O1
    PROBE --> DEEPSEEK
    ABLATION --> COT
    COMPARISON --> COT
    VISUAL --> O1
    
    ARCH --> MLLM
```

**Sources:** [README.md:327-338](), [assets/paper.json:716-759]()

## Research Categories

### Layer-wise Analysis

Research examining what happens in different transformer layers during reasoning:

| Paper | Focus | Key Findings |
|-------|-------|--------------|
| "What Happened in LLMs Layers when Trained for Fast vs. Slow Thinking" | Gradient perspective on layer behavior | Analyzes training dynamics across layers |
| "Towards System 2 Reasoning in LLMs" | Meta chain-of-thought learning | Layer-wise reasoning strategy development |
| "LlamaV-o1" | Visual reasoning layers | Step-by-step visual processing mechanisms |

These studies use probing classifiers, activation analysis, and gradient flow tracking to understand how reasoning emerges across model depth.

**Sources:** [README.md:331](), [README.md:334-335](), [assets/paper.json:718-723]()

### Autoregression vs Reasoning

Analysis of whether reasoning models retain traditional language model properties:

**Key Paper:** "When a Language Model is Optimized for Reasoning, Does It Still Show Embers of Autoregression? An Analysis of OpenAI o1" ([README.md:332]())

This research investigates whether models optimized for reasoning (like o1) still exhibit next-token prediction patterns or develop fundamentally different computational strategies. The analysis is critical for understanding:
- Whether reasoning is a distinct computational mode
- How to balance reasoning with generation quality
- Architectural choices for future systems

**Sources:** [README.md:332](), [assets/paper.json:725-730]()

### Architectural Mechanisms

Research on specialized architectures for explainable reasoning:

```mermaid
graph LR
    subgraph "Talker-Reasoner Architecture"
        INPUT["User Input"]
        REASONER["Reasoner Module<br/>System 2<br/>Deliberate Thinking"]
        TALKER["Talker Module<br/>System 1<br/>Fast Generation"]
        OUTPUT["Response"]
    end
    
    subgraph "System 2 Attention"
        ATT_INPUT["Input Sequence"]
        S2_ATT["Specialized Attention<br/>Reasoning-focused"]
        ATT_OUTPUT["Reasoning Output"]
    end
    
    INPUT --> REASONER
    REASONER --> TALKER
    TALKER --> OUTPUT
    
    ATT_INPUT --> S2_ATT
    S2_ATT --> ATT_OUTPUT
```

**Papers:**
- "Agents Thinking Fast and Slow: A Talker-Reasoner Architecture" - Separates reasoning from generation for interpretability
- "System 2 Attention (is something you might need too)" - Attention mechanisms specialized for deliberate reasoning

These architectures make reasoning explicit and separable from generation, enabling better analysis and control.

**Sources:** [README.md:328](), [README.md:333](), [assets/paper.json:732-744]()

### Knowledge Distillation

Transferring reasoning capabilities from slow to fast systems:

**Key Paper:** "Distilling System 2 into System 1" ([README.md:329]())

This research explores:
- Compressing multi-step reasoning into single-pass inference
- Preserving reasoning accuracy while reducing computational cost
- Training student models on teacher reasoning traces

The distillation approach connects to [Efficient System2](#5.1) by providing a mechanism to deploy reasoning capabilities at lower cost.

**Sources:** [README.md:329](), [assets/paper.json:746-751]()

### Step Length Impact

Quantitative analysis of reasoning length vs performance:

**Key Paper:** "The Impact of Reasoning Step Length on Large Language Models" ([README.md:330]())

Findings include:
- Optimal step length varies by task complexity
- Longer reasoning ≠ always better (diminishing returns)
- Step length impacts both accuracy and efficiency

This connects to:
- [Efficient System2](#5.1) for optimization strategies
- [Process Reward Models](#4.2) for step-wise supervision
- [O1 Replication](#4.1) for understanding target architectures

**Sources:** [README.md:330](), [assets/paper.json:753-758]()

## Repository Structure for Explainability

```mermaid
graph TB
    subgraph "Data Layer"
        JSON["assets/paper.json<br/>Part 8: Explainability<br/>Lines 716-759"]
    end
    
    subgraph "Primary Interface"
        README["README.md<br/>Part 8: Explainability<br/>Lines 327-338"]
    end
    
    subgraph "Generated Views"
        LIST["src/list.md<br/>Lines 108-114"]
        TABLE["src/table.md<br/>(Generated)"]
    end
    
    subgraph "Build System"
        MAIN["src/main.py<br/>PaperInformation<br/>processing"]
    end
    
    JSON --> MAIN
    MAIN --> LIST
    MAIN --> TABLE
    JSON -.informs.-> README
    
    README --> USERS["Researchers<br/>Practitioners"]
```

**Sources:** [README.md:327-338](), [assets/paper.json:716-759](), [src/list.md:108-114]()

## Paper Metadata Structure

Explainability papers are stored in `assets/paper.json` with this schema:

```json
{
    "Part 8: Explainability": [
        {
            "paper": "Paper Title",
            "link": "https://arxiv.org/abs/...",
            "venue": "arXiv|ACL|NeurIPS",
            "date": "YYYY-MM",
            "label": "author2024keyword"
        }
    ]
}
```

The `src/main.py` script processes this data through:
1. **Load Phase** - Parses JSON from [assets/paper.json:716-759]()
2. **Extract Phase** - Creates `PaperInformation` objects
3. **Resolve Phase** - Deduplicates and cross-references
4. **Generate Phase** - Produces [src/list.md:108-114]() and table views

**Sources:** [assets/paper.json:716-759](), [src/main.py]()

## Research Timeline

```mermaid
timeline
    title Explainability Research Evolution
    
    2023 : System 2 Attention
         : Early architectural mechanisms
         : Foundation for interpretable reasoning
    
    2024 : Gradient Analysis Era
         : Layer-wise behavior studies
         : Training dynamics investigations
         : Autoregression vs reasoning
         
    2024-2025 : Advanced Analysis
              : Talker-Reasoner architectures
              : Distillation approaches
              : Visual reasoning explainability
              : Step length impact studies
```

**Sources:** [README.md:327-338](), [assets/paper.json:716-759]()

## Integration with Other Research Areas

Explainability research intersects with multiple parts of the repository:

| Connection | Relationship | Example |
|------------|--------------|---------|
| [O1 Replication](#4.1) | Analysis target | Understanding what makes o1 work |
| [Process Reward Models](#4.2) | Mechanistic basis | Why step-wise rewards improve reasoning |
| [Reinforcement Learning](#4.3) | Training insights | How RL shapes reasoning capabilities |
| [Efficient System2](#5.1) | Optimization guidance | Which components to prune/compress |
| [Benchmarks](#7.1) | Evaluation foundation | Metrics for interpretability |

```mermaid
graph TB
    EXPLAIN["Part 8:<br/>Explainability"]
    
    O1["Part 1: O1 Replication<br/>What to build"]
    PRM["Part 2: Process Rewards<br/>Why supervision works"]
    RL["Part 3: Reinforcement Learning<br/>How training shapes models"]
    EFF["Part 7: Efficient System2<br/>What to optimize"]
    BENCH["Part 10: Benchmarks<br/>How to measure"]
    
    EXPLAIN --> O1
    EXPLAIN --> PRM
    EXPLAIN --> RL
    EXPLAIN --> EFF
    EXPLAIN --> BENCH
    
    O1 -.analysis target.-> EXPLAIN
    PRM -.mechanistic basis.-> EXPLAIN
    RL -.training insights.-> EXPLAIN
    EFF -.optimization guidance.-> EXPLAIN
    BENCH -.evaluation metrics.-> EXPLAIN
```

**Sources:** [README.md:26-416]()

## Key Papers Summary

| Paper | Venue | Date | Focus Area |
|-------|-------|------|------------|
| System 2 Attention | arXiv | 2023-11 | Architectural mechanism |
| The Impact of Reasoning Step Length | ACL Findings | 2024-08 | Performance analysis |
| Distilling System 2 into System 1 | arXiv | 2024-07 | Knowledge transfer |
| When a Language Model is Optimized for Reasoning | arXiv | 2024-10 | O1 analysis |
| What Happened in LLMs Layers | arXiv | 2024-10 | Gradient perspective |
| Agents Thinking Fast and Slow | NeurIPS Workshop | 2024-12 | Dual architecture |
| Towards System 2 Reasoning in LLMs | arXiv | 2025-01 | Meta-learning |
| LlamaV-o1 | arXiv | 2025-01 | Visual reasoning |
| Two Heads Are Better Than One | arXiv | 2025-02 | Dual-model reflection |
| Large Reasoning Models in Agent Scenarios | arXiv | 2025-03 | Agent capabilities |
| Cosmos-Reason1 | arXiv | 2025-03 | Embodied reasoning |

**Sources:** [README.md:327-338](), [assets/paper.json:716-759](), [src/list.md:108-114]()

## Accessing Explainability Research

Users can access papers through multiple paths:

1. **Categorized browsing** via [README.md:327-338]()
2. **Chronological view** via [src/list.md:108-114]()
3. **Tabular comparison** via `src/table.md` (generated)
4. **Direct metadata** via [assets/paper.json:716-759]()

All papers include arXiv/conference links for full text access.

**Sources:** [README.md:327-338](), [src/list.md:108-114](), [assets/paper.json:716-759]()

---

# Page: Multimodal Extensions

# Multimodal Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This page provides an overview of research extending System 2 reasoning capabilities beyond text-only large language models to multimodal domains, particularly vision-language models and multimodal agents. The repository organizes this research into two distinct but complementary parts:

- **Part 9: Multimodal Agents and Slow-Fast Systems** - For detailed coverage of dual-process architectures that integrate fast and slow thinking in multimodal agents, see [Multimodal Agents and Slow-Fast Systems](#6.1)
- **Part 12: R1-Driven Multimodal Reasoning** - For applications of R1/o1-style reinforcement learning methodologies to vision-language models, see [R1-Driven Multimodal Reasoning](#6.2)

This document explains the conceptual differences between these two paradigms, their relationship to core methodologies (Parts 1-6), and the architectural patterns that enable System 2 reasoning in multimodal contexts.

**Sources:** [README.md:40-43](), [README.md:339-481]()

## Overview: Extending System 2 to Multiple Modalities

While foundational System 2 reasoning techniques (process rewards, MCTS, reinforcement learning, self-training, reflection) were primarily developed for text-based mathematical and coding tasks, real-world intelligence requires reasoning over visual information, audio, video, and other modalities. The multimodal extensions adapt these techniques to handle perceptual input alongside linguistic reasoning.

The extension occurs along two dimensions:

1. **Architectural Integration** (Part 9): Designing systems that coordinate fast perceptual processing with slow deliberative reasoning across modalities
2. **Training Methodologies** (Part 12): Applying R1-style reinforcement learning to train multimodal models with enhanced reasoning capabilities

Both approaches aim to replicate the success of o1-class models in multimodal domains, enabling vision-language models to perform step-by-step reasoning, self-correction, and verification on visual tasks.

**Sources:** [README.md:339-350](), [README.md:455-481]()

## Evolution: From Text to Multimodal Reasoning

```mermaid
graph TB
    subgraph "Text-Only Reasoning (Parts 1-6)"
        TextBase["Base LLM<br/>(e.g., LLaMA, GPT)"]
        TextMethods["Core Methodologies<br/>PRM, RL, MCTS,<br/>Self-Training, Reflection"]
        TextO1["O1-like Systems<br/>DeepSeek-R1, Kimi k1.5"]
    end
    
    subgraph "Multimodal Extensions (Parts 9, 12)"
        VLMBase["Vision-Language Models<br/>(e.g., LLaVA, Qwen-VL)"]
        Part9["Part 9: Slow-Fast Systems<br/>AtomThink, LLaVA-o1<br/>Visual Agents"]
        Part12["Part 12: R1-Driven Enhancement<br/>MedVLM-R1, Virgo<br/>MM-Eureka, Skywork-R1V"]
        MultimodalO1["Multimodal O1-like<br/>Step-by-step visual reasoning"]
    end
    
    TextBase --> TextMethods
    TextMethods --> TextO1
    
    VLMBase --> Part9
    VLMBase --> Part12
    
    TextMethods -.adapts to.-> Part9
    TextMethods -.adapts to.-> Part12
    
    Part9 --> MultimodalO1
    Part12 --> MultimodalO1
    
    TextO1 -.inspires.-> MultimodalO1
```

**Diagram: Progression from text-only to multimodal System 2 reasoning**

The diagram shows how core text-based methodologies from Parts 1-6 are adapted to multimodal contexts through two distinct pathways (Parts 9 and 12), ultimately converging on multimodal o1-like systems.

**Sources:** [README.md:45-194](), [README.md:339-481]()

## Two Paradigms: Architectural vs Training-Centric Approaches

### Part 9: Architectural Slow-Fast Integration

Part 9 focuses on **system design** - how to architect multimodal agents that coordinate fast perceptual processing with slow deliberative reasoning. Key characteristics:

- **Dual-process architecture**: Explicit separation of System 1 (fast perception) and System 2 (slow reasoning) components
- **Inference-time reasoning**: Applying MCTS, tree search, and reflection at test time
- **Multimodal coordination**: Managing interactions between vision encoders, language models, and action modules
- **Domain-general frameworks**: AtomThink, LLaVA-o1, Visual Agents as general-purpose architectures

Representative papers: AtomThink (mathematical reasoning), LLaVA-o1 (step-by-step visual reasoning), Visual Agents as Fast and Slow Thinkers (agent architectures).

**Sources:** [README.md:339-350]()

### Part 12: R1-Driven Training Enhancement

Part 12 focuses on **training methodologies** - applying reinforcement learning techniques inspired by DeepSeek-R1 and OpenAI o1 to enhance multimodal reasoning. Key characteristics:

- **RL-based training**: Using reinforcement fine-tuning (RFT) with reward models
- **Long chain-of-thought**: Training models to produce extended reasoning traces for visual tasks
- **Domain-specific applications**: Medical imaging (MedVLM-R1), video understanding (Open R1 Video), segmentation (Seg-Zero)
- **R1-style methodology transfer**: Direct application of techniques from text-based R1 models

Representative papers: MedVLM-R1 (medical VLM with RL), Virgo (o1-like MLLM reproduction), MM-Eureka (visual aha moments via RL).

**Sources:** [README.md:455-481]()

## Comparative Analysis

| Aspect | Part 9: Slow-Fast Systems | Part 12: R1-Driven Enhancement |
|--------|---------------------------|-------------------------------|
| **Primary Focus** | System architecture design | Training methodology |
| **Timing** | Inference-time reasoning | Training-time + inference |
| **Key Technique** | MCTS, tree search, reflection | Reinforcement learning (GRPO, PPO) |
| **Inspiration** | Dual-process theory, agent design | DeepSeek-R1, OpenAI o1 |
| **Generalization** | Domain-general frameworks | Often domain-specific |
| **First Papers** | AtomThink, LLaVA-o1 (Nov 2024) | MedVLM-R1, Virgo (Jan-Feb 2025) |
| **Representative Works** | 10 papers (Nov 2024 - Feb 2025) | 27+ papers (Feb-Apr 2025) |

**Sources:** [README.md:339-350](), [README.md:455-481]()

## Integration with Core Methodologies

```mermaid
graph TB
    subgraph "Core Methods (Parts 2-6)"
        PRM["Process Reward Models<br/>Part 2"]
        RL["Reinforcement Learning<br/>Part 3"]
        MCTS["MCTS/Tree Search<br/>Part 4"]
        SelfTrain["Self-Training<br/>Part 5"]
        Reflect["Reflection<br/>Part 6"]
    end
    
    subgraph "Part 9 Applications"
        AtomThink["AtomThink<br/>MCTS + Reflection<br/>Math reasoning"]
        LLaVAo1["LLaVA-o1<br/>Step-by-step reasoning<br/>General VQA"]
        VisualAgents["Visual Agents<br/>Fast-Slow coordination<br/>Agent tasks"]
        Virgo9["Virgo<br/>MCTS for MLLM<br/>O1-like reproduction"]
    end
    
    subgraph "Part 12 Applications"
        MedVLMR1["MedVLM-R1<br/>RL for medical VLM<br/>Clinical reasoning"]
        MMEureka["MM-Eureka<br/>RL for visual aha<br/>Rule-based learning"]
        SkyworkR1V["Skywork-R1V<br/>CoT-driven RL<br/>Multimodal reasoning"]
        VisionR1["Vision-R1/VLM-R1<br/>General RL tuning<br/>Cross-domain"]
    end
    
    MCTS --> AtomThink
    Reflect --> AtomThink
    MCTS --> LLaVAo1
    MCTS --> Virgo9
    
    RL --> MedVLMR1
    RL --> MMEureka
    RL --> SkyworkR1V
    RL --> VisionR1
    
    PRM -.guides.-> MCTS
    PRM -.guides.-> RL
    SelfTrain -.improves.-> RL
```

**Diagram: How core methodologies flow into multimodal applications**

Part 9 primarily leverages **MCTS and Reflection** (Parts 4, 6) for inference-time reasoning, while Part 12 primarily applies **Reinforcement Learning** (Part 3) often guided by Process Reward Models (Part 2).

**Sources:** [README.md:68-96](), [README.md:98-137](), [README.md:139-193](), [README.md:339-350](), [README.md:455-481]()

## Key Architectural Patterns

### Pattern 1: Perception-Reasoning Decoupling (Part 9)

```mermaid
graph LR
    Input["Visual Input<br/>(Image/Video)"]
    FastPerception["Fast System 1<br/>Vision Encoder<br/>Quick feature extraction"]
    SlowReasoning["Slow System 2<br/>LLM + MCTS<br/>Deliberate reasoning"]
    Action["Output<br/>Answer/Action"]
    
    Input --> FastPerception
    FastPerception --> SlowReasoning
    SlowReasoning --> Action
    
    SlowReasoning -.reflection loop.-> SlowReasoning
```

**Diagram: Dual-process architecture separating perception and reasoning**

Examples: Visual Agents as Fast and Slow Thinkers, AtomThink

**Sources:** [README.md:341-348]()

### Pattern 2: RL-Enhanced Chain-of-Thought (Part 12)

```mermaid
graph LR
    VLM["Vision-Language Model<br/>(e.g., LLaVA base)"]
    RLTrain["Reinforcement Learning<br/>GRPO/PPO with rewards"]
    LongCoT["Long CoT Generation<br/>Step-by-step reasoning"]
    Enhanced["Enhanced VLM<br/>R1-style reasoning"]
    
    VLM --> RLTrain
    RLTrain --> LongCoT
    LongCoT --> Enhanced
    
    RewardModel["Process/Outcome<br/>Reward Model"]
    RewardModel -.guides.-> RLTrain
```

**Diagram: RL fine-tuning pipeline for multimodal reasoning**

Examples: MedVLM-R1, Virgo, Skywork-R1V

**Sources:** [README.md:458-476]()

## Representative Systems

### From Part 9 (Slow-Fast Architectures)

| System | Key Innovation | Domain | Paper Date |
|--------|---------------|--------|------------|
| **AtomThink** | MCTS + reflection for multimodal math | Mathematical reasoning | Nov 2024 |
| **LLaVA-o1** | Step-by-step visual reasoning framework | General VQA | Nov 2024 |
| **Visual Agents** | Dual-process agent architecture | Agent tasks | ICLR 2025 |
| **Virgo** | O1-like MLLM with tree search | General reasoning | Jan 2025 |

**Sources:** [README.md:341-348]()

### From Part 12 (R1-Driven Enhancement)

| System | Key Innovation | Domain | Release Date |
|--------|---------------|--------|--------------|
| **MedVLM-R1** | RL for clinical reasoning in VLMs | Medical imaging | Feb 2025 |
| **Virgo** | Reproducing o1-like capabilities in MLLM | General | Jan 2025 |
| **MM-Eureka** | RL for visual aha moments | Rule learning | Mar 2025 |
| **Skywork-R1V** | CoT-guided multimodal RL | General reasoning | Mar/Apr 2025 |
| **VLM-R1** | Stable, generalizable R1-style VLM | Cross-domain | Apr 2025 |
| **VLAA-Thinking** | RL-tuned visual reasoning | General | Apr 2025 |

**Sources:** [README.md:458-476]()

## Timeline: Emergence of Multimodal Reasoning

```mermaid
timeline
    title Multimodal System 2 Reasoning Evolution
    
    2024-11 : Part 9 Foundations
            : AtomThink (mathematical)
            : LLaVA-o1 (step-by-step)
            : Vision-Language Reflection
    
    2024-12 : Continued Part 9 Development
            : Slow Perception
            : Scaling Inference-Time Search
    
    2025-01 : R1 Release Triggers Part 12
            : Virgo (o1-like MLLM)
            : DeepSeek-R1 inspires multimodal
    
    2025-02 : Part 12 Explosion
            : MedVLM-R1 (medical)
            : Multiple R1-Vision variants
            : Open R1 Video
    
    2025-03 : Rapid Part 12 Growth
            : Skywork-R1V, MMR1
            : R1-Omni, R1-Onevision
            : Domain-specific applications
    
    2025-04 : Maturity Phase
            : VLAA-Thinking
            : VLM-R1 (stable & general)
            : Perception-R1, Embodied-R
```

**Diagram: Timeline showing Part 9 emerged first, Part 12 exploded after DeepSeek-R1 release**

Notable pattern: Part 9 papers emerged Nov-Dec 2024 as architectural explorations. Part 12 exploded in Feb-Apr 2025 following the DeepSeek-R1 release in January 2025, demonstrating rapid methodology transfer.

**Sources:** [README.md:339-350](), [README.md:455-481]()

## Relationship to O1 Replication (Part 1)

Both Parts 9 and 12 can be viewed as **multimodal extensions of Part 1 (O1 Replication)**:

- Part 9 extends the **inference-time reasoning architecture** of o1 to multimodal inputs
- Part 12 extends the **training methodology** (RL-based long CoT generation) to vision-language models

Several papers appear in multiple parts:
- **Virgo** appears in both Part 1 ([README.md:61]()) and Part 9 ([README.md:348]()) - bridging o1 replication and multimodal agents
- Many Part 12 systems explicitly cite DeepSeek-R1 ([README.md:107]()) as inspiration

**Sources:** [README.md:45-67](), [README.md:339-350](), [README.md:455-481]()

## Cross-Cutting Themes

### Integration with Efficient System2 (Part 7)

Several multimodal papers address computational efficiency:
- Dynamic routing between fast and slow modes (echoing DynaThink approach from Part 7)
- Token budget management for long visual reasoning chains
- Latent space reasoning to reduce multimodal token overhead

**Sources:** [README.md:242-325]()

### Evaluation Challenges (Part 10)

Part 10 includes multimodal-specific benchmarks:
- **MME-CoT**: Benchmarking chain-of-thought in multimodal models
- **MM-IQ**: Abstract reasoning in multimodal contexts
- **ZeroBench**: Impossible visual problems for contemporary models
- **EnigmaEval**: Long multimodal reasoning challenges

These benchmarks are critical for evaluating both Part 9 and Part 12 systems.

**Sources:** [README.md:368-402]()

## Research Directions

### Emerging Patterns in Part 12 (Feb-Apr 2025)

The recent explosion of Part 12 papers reveals several trends:

1. **Domain Specialization**: Medical (MedVLM-R1), video (Open R1 Video), audio (Audio-QA RL), segmentation (Seg-Zero)
2. **Modality Expansion**: Beyond vision-language to video, audio, embodied perception
3. **Reinforcement Learning Variants**: GRPO, PPO, custom reward formulations for different modalities
4. **Generalization Focus**: VLM-R1 and Skywork-R1V emphasize stable, cross-domain performance

**Sources:** [README.md:455-481]()

### Open Questions

1. **Part 9 vs Part 12 Complementarity**: Can architectural patterns (Part 9) be combined with RL training (Part 12) for superior performance?
2. **Computational Cost**: Multimodal MCTS and long CoT generation are expensive - how to scale?
3. **Modality Coordination**: Best practices for managing different input modalities in reasoning chains
4. **Transfer Learning**: How well do text-based reasoning techniques truly transfer to visual domains?

## Summary

Multimodal extensions represent a critical frontier in System 2 reasoning research, adapting successful text-based techniques to visual and multimodal domains. The repository organizes this work into:

- **Part 9**: Architectural frameworks emphasizing dual-process design and inference-time reasoning (10 papers, Nov 2024-Feb 2025)
- **Part 12**: Training methodologies applying R1-style RL to multimodal models (27+ papers, Feb-Apr 2025 explosion)

Both approaches aim to bring o1-level reasoning capabilities to vision-language models, with Part 9 focusing on system architecture and Part 12 on training techniques. The rapid growth of Part 12 following DeepSeek-R1's release demonstrates the field's ability to quickly adapt breakthrough methodologies to new domains.

For detailed coverage of specific systems and papers, see:
- [Multimodal Agents and Slow-Fast Systems](#6.1) for Part 9 details
- [R1-Driven Multimodal Reasoning](#6.2) for Part 12 details

**Sources:** [README.md:339-481]()

---

# Page: Multimodal Agents and Slow-Fast Systems

# Multimodal Agents and Slow-Fast Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/list.md](src/list.md)

</details>



## Purpose and Scope

This page documents **Part 9: Multimodal Agent related Slow-Fast System** from the Awesome-System2-Reasoning-LLM repository. This section covers research that extends System 1 (fast, intuitive) and System 2 (slow, deliberate) reasoning paradigms to multimodal contexts, where agents process and reason over multiple modalities such as vision, language, and geometric representations.

For research specifically focused on applying R1/DeepSeek-R1 methodologies to multimodal models, see [R1-Driven Multimodal Reasoning](#6.2). For general slow-fast reasoning in text-only LLMs, see [Core Methodologies](#4). For optimization of multimodal reasoning systems, see [Efficient System2](#5.1).

**Sources:** [README.md:339-350](), [README.md:40]()

## Overview: Extending System 2 to Multimodal Domains

Traditional System 2 reasoning research (Parts 1-6) has primarily focused on text-based chain-of-thought reasoning. Part 9 addresses the challenge of bringing deliberate, multi-step reasoning to agents that must process visual information, spatial relationships, and cross-modal understanding.

### Distinction from Text-Only Reasoning

```mermaid
graph TB
    subgraph "Text-Only System 2 (Parts 1-6)"
        TEXT_INPUT["Text Input"]
        TEXT_COT["Chain-of-Thought<br/>Reasoning"]
        TEXT_OUTPUT["Text Output"]
    end
    
    subgraph "Multimodal System 2 (Part 9)"
        VISUAL_INPUT["Visual Input:<br/>Images, Diagrams,<br/>Geometric Figures"]
        TEXT_INPUT_MM["Text Input:<br/>Questions, Context"]
        
        PERCEPTION["Slow Perception:<br/>Step-by-step<br/>Visual Processing"]
        
        MM_REASONING["Multimodal Reasoning:<br/>Cross-modal Integration"]
        
        REFLECTION["Visual Reflection:<br/>Error Detection in<br/>Visual Understanding"]
        
        MM_OUTPUT["Structured Output:<br/>Text + Visual<br/>Annotations"]
    end
    
    TEXT_INPUT --> TEXT_COT
    TEXT_COT --> TEXT_OUTPUT
    
    VISUAL_INPUT --> PERCEPTION
    TEXT_INPUT_MM --> MM_REASONING
    PERCEPTION --> MM_REASONING
    MM_REASONING --> REFLECTION
    REFLECTION --> MM_OUTPUT
    
    TEXT_COT -.extends to.-> MM_REASONING
```

**Diagram: Evolution from Text-Only to Multimodal System 2 Reasoning**

**Sources:** [README.md:339-350](), [README.md:14-18]()

## Core Research Directions

The multimodal agent slow-fast systems documented in Part 9 can be categorized into four primary research directions:

| Research Direction | Key Papers | Primary Focus | Data Location |
|-------------------|------------|---------------|---------------|
| **Slow Perception** | Slow Perception (2024.12) | Step-by-step visual processing of geometric figures | [README.md:345]() |
| **Vision-Language Reasoning** | LLaVA-o1 (2024.11), AtomThink (2024.11) | Chain-of-thought for vision-language models | [README.md:342](), [README.md:341]() |
| **Visual Agent Systems** | Visual Agents as Fast and Slow Thinkers (ICLR 2025) | Dual-system agents for visual tasks | [README.md:347]() |
| **O1-like MLLMs** | Virgo (2025.01) | Replicating o1 reasoning in multimodal LLMs | [README.md:348]() |

**Sources:** [README.md:339-350](), [assets/paper.json:760-816]()

## Key Systems and Methodologies

### AtomThink: Multimodal Mathematical Reasoning

```mermaid
graph LR
    subgraph "AtomThink Pipeline"
        INPUT["Mathematical Problem<br/>with Visual Components"]
        
        ATOM_DECOMPOSE["Atomic Decomposition:<br/>Break into<br/>Elementary Steps"]
        
        VISUAL_GROUNDING["Visual Grounding:<br/>Link Steps to<br/>Image Regions"]
        
        SLOW_REASONING["Slow Reasoning:<br/>Step-by-step<br/>Verification"]
        
        REFLECTION["Reflection:<br/>Error Correction"]
        
        SOLUTION["Solution with<br/>Visual Evidence"]
    end
    
    INPUT --> ATOM_DECOMPOSE
    ATOM_DECOMPOSE --> VISUAL_GROUNDING
    VISUAL_GROUNDING --> SLOW_REASONING
    SLOW_REASONING --> REFLECTION
    REFLECTION --> SOLUTION
    
    REFLECTION -.identifies errors.-> ATOM_DECOMPOSE
```

**Diagram: AtomThink Framework Architecture**

AtomThink (liu2024atomthink) introduces atomic-level decomposition for multimodal mathematical reasoning. The system breaks complex visual math problems into elementary reasoning steps, each grounded in specific regions of the input image. This enables fine-grained verification and error correction.

**Key Characteristics:**
- **Atomic Step Decomposition**: Problems decomposed into irreducible reasoning units
- **Visual Grounding**: Each reasoning step linked to image evidence
- **Slow Thinking Framework**: Multi-step deliberation with verification
- **Reflection Mechanism**: Self-correction via error detection

**Sources:** [README.md:341](), [assets/paper.json:762-767]()

### LLaVA-o1: Step-by-Step Vision-Language Reasoning

```mermaid
graph TB
    subgraph "LLaVA-o1 Architecture"
        VLM_BASE["Base Vision-Language<br/>Model (LLaVA)"]
        
        STAGE1["Stage 1:<br/>Structured Reasoning<br/>Data Generation"]
        
        STAGE2["Stage 2:<br/>Supervised Fine-Tuning<br/>on Reasoning Traces"]
        
        INFERENCE["Inference:<br/>Step-by-step CoT<br/>for Vision Tasks"]
    end
    
    subgraph "Reasoning Components"
        SUMMARY["Summary:<br/>Problem Understanding"]
        CAPTION["Caption:<br/>Visual Description"]
        REASONING["Reasoning:<br/>Multi-step Analysis"]
        CONCLUSION["Conclusion:<br/>Final Answer"]
    end
    
    VLM_BASE --> STAGE1
    STAGE1 --> STAGE2
    STAGE2 --> INFERENCE
    
    INFERENCE --> SUMMARY
    SUMMARY --> CAPTION
    CAPTION --> REASONING
    REASONING --> CONCLUSION
```

**Diagram: LLaVA-o1 Training and Inference Pipeline**

LLaVA-o1 (xu2024llava) extends the LLaVA vision-language model with structured chain-of-thought reasoning capabilities. The system generates explicit reasoning traces that include visual understanding, multi-step analysis, and conclusion formulation.

**Training Methodology:**
1. **Data Generation**: Create reasoning traces with summary, caption, reasoning, and conclusion components
2. **Supervised Fine-Tuning**: Train the model to produce structured reasoning outputs
3. **Inference-Time Reasoning**: Generate step-by-step explanations during test time

**Sources:** [README.md:342](), [README.md:235](), [assets/paper.json:768-774]()

### Visual Agents as Fast and Slow Thinkers

```mermaid
graph TB
    subgraph "Dual-System Visual Agent"
        TASK["Visual Agent Task"]
        
        ROUTER["Task Complexity<br/>Router"]
        
        FAST_PATH["Fast Path (System 1):<br/>Direct Vision-Action<br/>Mapping"]
        
        SLOW_PATH["Slow Path (System 2):<br/>Visual Reasoning +<br/>Planning"]
        
        ACTION["Agent Action"]
    end
    
    subgraph "Slow Path Components"
        VISUAL_ENCODE["Visual Encoding"]
        SCENE_GRAPH["Scene Graph<br/>Construction"]
        REASONING_PLAN["Reasoning-based<br/>Planning"]
        VERIFICATION["Action<br/>Verification"]
    end
    
    TASK --> ROUTER
    ROUTER -->|"Simple Task"| FAST_PATH
    ROUTER -->|"Complex Task"| SLOW_PATH
    
    FAST_PATH --> ACTION
    SLOW_PATH --> ACTION
    
    SLOW_PATH --> VISUAL_ENCODE
    VISUAL_ENCODE --> SCENE_GRAPH
    SCENE_GRAPH --> REASONING_PLAN
    REASONING_PLAN --> VERIFICATION
    VERIFICATION --> ACTION
```

**Diagram: Dual-System Architecture for Visual Agents**

The Visual Agents paper (gao2025visualagents, ICLR 2025) introduces a dual-system architecture that dynamically routes visual agent tasks between fast (System 1) and slow (System 2) processing paths based on task complexity.

**System 1 (Fast Path):**
- Direct perception-to-action mapping
- Suitable for simple, familiar visual tasks
- Minimal computational overhead

**System 2 (Slow Path):**
- Scene graph construction for structured representation
- Multi-step reasoning and planning
- Action verification before execution
- Used for complex, novel visual tasks

**Sources:** [README.md:347](), [assets/paper.json:776-781]()

## Integration with Core System 2 Techniques

Multimodal agents leverage and adapt techniques from text-only System 2 reasoning (Parts 2-6):

### Process Reward Models for Visual Reasoning

```mermaid
graph LR
    subgraph "Adapted Process Rewards"
        VISION_STEP["Visual Reasoning<br/>Step"]
        
        VISUAL_PRM["Visual Process<br/>Reward Model"]
        
        STEP_SCORE["Step-wise<br/>Correctness Score"]
        
        VISUAL_VERIFY["Visual Evidence<br/>Verification"]
    end
    
    VISION_STEP --> VISUAL_PRM
    VISUAL_PRM --> STEP_SCORE
    STEP_SCORE --> VISUAL_VERIFY
    
    VISUAL_VERIFY -.provides feedback.-> VISION_STEP
```

**Diagram: Process Reward Adaptation for Multimodal Reasoning**

Papers like "Scaling Inference-Time Search With Vision Value Model" extend process reward models (Part 2) to multimodal contexts. The vision value model provides step-wise feedback on visual reasoning quality.

**Key Adaptations:**
- **Visual Grounding**: PRMs verify alignment between reasoning steps and visual evidence
- **Cross-Modal Consistency**: Reward models check consistency between text reasoning and visual content
- **Spatial Reasoning Verification**: Specialized rewards for geometric and spatial understanding

**Sources:** [README.md:344](), [README.md:68-97]()

### MCTS and Tree Search for Visual Tasks

Several papers apply Monte Carlo Tree Search (Part 4) to multimodal reasoning:

| Paper | MCTS Application | Visual Domain |
|-------|------------------|---------------|
| Mulberry | Collective MCTS for MLLM reasoning | General vision-language tasks |
| Virgo | o1-like tree search for MLLMs | Mathematical reasoning with diagrams |
| AtomThink | Atomic-step exploration | Geometric problem solving |

**MCTS Adaptations for Vision:**
- **Visual State Representation**: Nodes encode both text and visual understanding
- **Cross-Modal Action Space**: Branches explore different visual interpretations
- **Vision-Grounded Rollouts**: Simulations verify consistency with image content

**Sources:** [README.md:178](), [README.md:348](), [README.md:341]()

### Self-Training and Reflection in Multimodal Models

```mermaid
graph TB
    subgraph "Multimodal Self-Improvement Loop"
        MM_MODEL["Multimodal Model<br/>(Vision + Language)"]
        
        GENERATE["Generate Reasoning<br/>Traces on Visual Tasks"]
        
        SELF_EVAL["Self-Evaluation:<br/>Visual + Text<br/>Consistency Check"]
        
        FILTER["Filter High-Quality<br/>Reasoning Examples"]
        
        RETRAIN["Self-Training:<br/>Fine-tune on Filtered<br/>Data"]
    end
    
    subgraph "Visual Reflection"
        VISUAL_ERROR["Detect Visual<br/>Understanding Errors"]
        CORRECT["Generate<br/>Corrections"]
        VERIFY["Verify with<br/>Image Evidence"]
    end
    
    MM_MODEL --> GENERATE
    GENERATE --> SELF_EVAL
    SELF_EVAL --> FILTER
    FILTER --> RETRAIN
    RETRAIN --> MM_MODEL
    
    SELF_EVAL --> VISUAL_ERROR
    VISUAL_ERROR --> CORRECT
    CORRECT --> VERIFY
    VERIFY -.feedback.-> GENERATE
```

**Diagram: Self-Training and Reflection for Multimodal Models**

Papers like "Vision-Language Models Can Self-Improve Reasoning via Reflection" and "Diving into Self-Evolving Training for Multimodal Reasoning" extend self-training (Part 5) and reflection (Part 6) methodologies to multimodal contexts.

**Key Innovations:**
- **Cross-Modal Error Detection**: Identify inconsistencies between visual perception and text reasoning
- **Visual Evidence-Based Correction**: Use image content to verify and correct reasoning steps
- **Self-Evolving Data Generation**: Bootstrap multimodal reasoning without human annotations

**Sources:** [README.md:343](), [README.md:346](), [README.md:194-224](), [README.md:225-241]()

## Specialized Techniques

### Slow Perception for Geometric Understanding

The "Slow Perception" paper introduces step-by-step visual processing for geometric figures:

**Methodology:**
1. **Sequential Attention**: Process image regions incrementally rather than holistically
2. **Geometric Primitive Detection**: Identify basic shapes and relationships
3. **Hierarchical Composition**: Build complex understanding from primitives
4. **Verification at Each Step**: Validate geometric properties before proceeding

**Technical Implementation:**
- Vision transformers with controlled attention patterns
- Explicit intermediate representations of geometric properties
- Step-wise verification using geometric constraints

**Sources:** [README.md:345](), [assets/paper.json:783-788]()

### Diffusion Models with Reasoning Capabilities

"I Think, Therefore I Diffuse" extends reasoning to generative diffusion models:

**Architecture:**
- **In-Context Reasoning**: Embed reasoning steps in the diffusion process
- **Multimodal Conditioning**: Use both text and image context for reasoning
- **Iterative Refinement**: Generate and refine outputs through deliberate steps

**Applications:**
- Visual problem solving during generation
- Reasoning-guided image synthesis
- Multimodal in-context learning

**Sources:** [README.md:349]()

## Data Structures and Repository Organization

### Part 9 Data in paper.json

The structured metadata for Part 9 papers is stored in `assets/paper.json`:

```json
"Part 9: Multimodal Agent related Slow-Fast System": [
    {
        "paper": "AtomThink: A Slow Thinking Framework for Multimodal Mathematical Reasoning",
        "link": "https://arxiv.org/abs/2411.11930",
        "venue": "arXiv",
        "date": "2024-11",
        "label": "liu2024atomthink"
    },
    // ... additional papers
]
```

**Key Fields:**
- `label`: Unique identifier used for cross-referencing (e.g., `liu2024atomthink`)
- `venue`: Publication venue (arXiv, ICLR, NeurIPS, etc.)
- `date`: Publication date in YYYY-MM format
- `link`: Direct URL to the paper

**Sources:** [assets/paper.json:760-816]()

### Generated Views

The build system generates alternative views of Part 9 papers:

**Table View** (`src/table.md`): Chronologically sorted tabular format
**List View** (`src/list.md`): Badge-annotated list format with venue indicators

Both views are generated by [src/main.py]() from the structured JSON data.

**Sources:** [src/main.py:1-50](), [src/list.md:115-123]()

## Relationship to Other Repository Parts

```mermaid
graph TB
    subgraph "Core Text Methods (Parts 2-6)"
        PRM["Part 2:<br/>Process Reward<br/>Models"]
        RL["Part 3:<br/>Reinforcement<br/>Learning"]
        MCTS["Part 4:<br/>MCTS/Tree<br/>Search"]
        SELF["Part 5:<br/>Self-Training"]
        REFLECT["Part 6:<br/>Reflection"]
    end
    
    subgraph "Multimodal Extensions"
        PART9["Part 9:<br/>Multimodal Agents<br/>Slow-Fast Systems"]
        PART12["Part 12:<br/>R1-Driven<br/>Multimodal"]
    end
    
    subgraph "Support Systems"
        EFFICIENT["Part 7:<br/>Efficient<br/>System2"]
        BENCH["Part 10:<br/>Benchmarks"]
    end
    
    PRM -.adapts to.-> PART9
    MCTS -.extends to.-> PART9
    SELF -.applies to.-> PART9
    REFLECT -.integrates with.-> PART9
    
    PART9 -.influences.-> PART12
    
    EFFICIENT -.optimizes.-> PART9
    BENCH -.evaluates.-> PART9
    
    RL -.trains.-> PART12
```

**Diagram: Integration of Part 9 with Other Research Areas**

**Connections:**
- **Part 2 (PRMs)**: Visual process reward models verify step-wise correctness
- **Part 3 (RL)**: Reinforcement learning trains multimodal reasoning policies
- **Part 4 (MCTS)**: Tree search explores visual reasoning paths
- **Part 5 (Self-Training)**: Bootstrapping multimodal reasoning data
- **Part 6 (Reflection)**: Visual error detection and correction
- **Part 7 (Efficient)**: Optimizing computational cost of visual reasoning
- **Part 10 (Benchmarks)**: Evaluating multimodal reasoning capabilities
- **Part 12 (R1-Multimodal)**: Applying R1 methodologies to vision-language models

**Sources:** [README.md:26-43](), [README.md:339-350]()

## Technical Implementation Patterns

### Pattern 1: Staged Visual Reasoning

```mermaid
sequenceDiagram
    participant User
    participant VLM as Vision-Language Model
    participant Perceiver as Visual Perceiver
    participant Reasoner as Text Reasoner
    participant Verifier as Cross-Modal Verifier
    
    User->>VLM: Visual Question + Image
    VLM->>Perceiver: Extract Visual Features
    Perceiver->>Perceiver: Step-by-step Visual Processing
    Perceiver->>Reasoner: Visual Understanding
    Reasoner->>Reasoner: Multi-step Text Reasoning
    Reasoner->>Verifier: Reasoning Trace + Image
    Verifier->>Verifier: Check Consistency
    Verifier->>User: Verified Answer
```

**Diagram: Staged Visual Reasoning Pattern**

This pattern, used in LLaVA-o1 and AtomThink, separates visual perception, text reasoning, and cross-modal verification into distinct stages.

**Sources:** [README.md:342](), [README.md:341]()

### Pattern 2: Dynamic Fast-Slow Routing

The Visual Agents paper implements dynamic routing:

**Routing Decision Factors:**
- Task complexity estimation
- Visual ambiguity detection
- Available computational budget
- Prior task performance

**Implementation:**
- Lightweight complexity classifier
- Threshold-based routing decision
- Fallback to slow path on uncertainty

**Sources:** [README.md:347]()

### Pattern 3: Vision-Grounded Tree Search

For papers applying MCTS to multimodal tasks:

**Tree Node Structure:**
- Text reasoning state
- Visual grounding annotations (image regions)
- Cross-modal consistency score
- Parent/child pointers

**Expansion Strategy:**
- Generate candidate reasoning steps
- Ground each step in visual evidence
- Filter inconsistent branches

**Rollout Simulation:**
- Fast forward reasoning to completion
- Verify final answer against image
- Backpropagate visual consistency scores

**Sources:** [README.md:178](), [README.md:348]()

## Benchmark and Evaluation Considerations

Multimodal reasoning systems are evaluated on specialized benchmarks (see [Benchmarks and Datasets](#7.1)):

| Benchmark Category | Example Benchmarks | Part 9 Papers Evaluated |
|-------------------|-------------------|------------------------|
| Mathematical Reasoning | Plot2code, PuzzleVQA | AtomThink, LLaVA-o1 |
| Geometric Understanding | Custom geometric datasets | Slow Perception |
| Agent Tasks | OSWorld, VisualWebArena | Visual Agents |
| General Vision-Language | MME-CoT, MM-IQ | Virgo, Self-Evolving Training |

**Key Evaluation Metrics:**
- Visual grounding accuracy
- Step-wise reasoning correctness
- Cross-modal consistency
- Computational efficiency (tokens/time)

**Sources:** [README.md:351-433](), [README.md:389-403]()

## Future Directions and Open Challenges

Based on the papers in Part 9, key open challenges include:

1. **Scalability**: Extending slow visual reasoning to high-resolution images and videos
2. **Efficiency**: Reducing computational cost of step-by-step visual processing
3. **Generalization**: Transferring visual reasoning across diverse domains
4. **Integration**: Seamlessly combining fast and slow processing in real-time systems
5. **Evaluation**: Developing comprehensive benchmarks for multimodal System 2 reasoning

The research trajectory shows increasing sophistication in applying System 2 reasoning to vision, with papers progressing from simple chain-of-thought to complex tree search and self-evolving systems.

**Sources:** [README.md:339-350](), [README.md:23-26]()

## Accessing Part 9 Papers

All papers in Part 9 are cataloged with links and metadata:

- **README.md**: Human-readable descriptions at [README.md:339-350]()
- **paper.json**: Structured metadata at [assets/paper.json:760-816]()
- **list.md**: Chronological list at [src/list.md:115-123]()
- **Survey Paper**: Comprehensive analysis at http://arxiv.org/abs/2502.17419

The repository is actively maintained with new papers added as the field evolves.

**Sources:** [README.md:9-11](), [README.md:16]()

---

# Page: R1-Driven Multimodal Reasoning

# R1-Driven Multimodal Reasoning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/table.md](src/table.md)

</details>



## Purpose and Scope

This page documents **Part 12: R1-Driven Multimodal Reasoning Enhancement**, which covers the application of R1/o1-style reasoning methodologies—specifically reinforcement learning-based long chain-of-thought reasoning—to vision-language models and multimodal systems. This represents the convergence of advanced reasoning techniques from text-only LLMs (Parts 1-3) with multimodal capabilities.

For general multimodal slow-fast systems and architectural patterns, see [Part 9: Multimodal Agents and Slow-Fast Systems](#6.1). For the foundational R1 and RL methodologies being applied here, see [O1 Replication](#4.1) and [Reinforcement Learning](#4.3). For evaluation of multimodal reasoning capabilities, see [Benchmarks and Datasets](#7.1).

**Key Distinction**: While Part 9 covers diverse multimodal reasoning architectures (MCTS-based, self-evolution, reflection), Part 12 specifically focuses on systems that apply the **R1 paradigm**—RL-trained long-form reasoning with process rewards—to vision-language tasks.

Sources: [README.md:1-43](), [README.md:339-350]()

---

## Overview: R1 Reasoning Meets Vision-Language Models

The R1-driven multimodal reasoning paradigm emerged following the success of **DeepSeek-R1** (January 2025) and **Kimi k1.5**, which demonstrated that pure RL training could elicit complex reasoning behaviors in text-only models. Part 12 extends this methodology to multimodal domains, where models must reason jointly over visual and textual information.

### Timeline of Key Developments

```mermaid
timeline
    title R1-Driven Multimodal Reasoning Evolution
    
    2024-11 : LLaVA-o1 introduces structured reasoning for VLMs
            : AtomThink applies slow thinking to multimodal math
            : Virgo preliminary exploration begins
    
    2024-12 : Slow Perception step-by-step geometric reasoning
            : Mulberry collective MCTS for MLLMs
            : Scaling inference-time search with vision value models
    
    2025-01 : DeepSeek-R1 released with pure RL reasoning
            : Kimi k1.5 demonstrates scaled RL effectiveness
            : Virgo applies o1-like methodology to MLLMs
            : Visual Agents as Fast and Slow Thinkers (ICLR)
            : Diving into Self-Evolving Training (ICLR)
    
    2025-02+ : Domain-specific R1-driven models emerge
             : Medical VLMs with R1-style reasoning
             : MM-Eureka multimodal reasoning systems
             : Integration with agent frameworks
```

Sources: [README.md:339-350](), [README.md:45-67](), [README.md:98-138]()

---

## Core Methodology: From Text-R1 to Multimodal-R1

### Architecture Pattern

The R1-driven multimodal approach follows a consistent pattern:

```mermaid
graph TB
    subgraph "Input Processing"
        VI["Vision Encoder<br/>(e.g., CLIP, ViT)"]
        TI["Text Encoder<br/>(Tokenizer)"]
        IMG["Image Input"]
        TXT["Text Query"]
    end
    
    subgraph "Multimodal Fusion"
        FUSION["Vision-Language<br/>Alignment Layer"]
        UNIFIED["Unified Token<br/>Representation"]
    end
    
    subgraph "R1 Reasoning Module"
        BASE["Base LLM<br/>(e.g., Qwen, LLaMA)"]
        RL["RL Training<br/>(GRPO, PPO)"]
        PRM["Process Reward Model<br/>for multimodal steps"]
        LONG_COT["Long Chain-of-Thought<br/>Generation"]
    end
    
    subgraph "Inference Strategy"
        SEARCH["Tree Search /<br/>Best-of-N Sampling"]
        VERIFY["Step-wise Verification<br/>with visual grounding"]
        OUTPUT["Final Answer<br/>+ Reasoning Trace"]
    end
    
    IMG --> VI
    TXT --> TI
    VI --> FUSION
    TI --> FUSION
    FUSION --> UNIFIED
    
    UNIFIED --> BASE
    BASE --> RL
    RL --> LONG_COT
    PRM --> RL
    
    LONG_COT --> SEARCH
    SEARCH --> VERIFY
    VERIFY --> OUTPUT
    
    PRM -.guides.-> SEARCH
```

**Key Components**:
1. **Vision-Language Alignment**: Projects visual features into text token space
2. **RL-Trained Reasoning**: Learns to generate long-CoT via process rewards
3. **Multimodal Process Rewards**: Evaluates reasoning quality considering both modalities
4. **Inference-Time Search**: Explores multiple reasoning paths with visual verification

Sources: [README.md:339-350](), [README.md:98-138]()

---

## Key Systems and Papers

### LLaVA-o1: Structured Reasoning for VLMs

**Paper**: "LLaVA-o1: Let Vision Language Models Reason Step-by-Step" (November 2024)

```mermaid
graph LR
    subgraph "LLaVA-o1 Architecture"
        INPUT["Image + Question"]
        
        subgraph "Stage 1: Summary"
            S1["Generate<br/>Question Summary"]
        end
        
        subgraph "Stage 2: Caption"
            S2["Detailed<br/>Image Caption"]
        end
        
        subgraph "Stage 3: Reasoning"
            S3["Step-by-step<br/>Logical Reasoning"]
        end
        
        subgraph "Stage 4: Conclusion"
            S4["Final Answer<br/>+ Confidence"]
        end
        
        OUTPUT["Structured Response"]
    end
    
    INPUT --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> OUTPUT
```

**Technical Details**:
- **Structured Four-Stage Reasoning**: Separates perception, reasoning, and conclusion
- **Training Data**: Uses synthesized multimodal reasoning chains
- **Inference**: Can be combined with beam search for better exploration

Sources: [README.md:235](), [README.md:342](), [assets/paper.json:658-663]()

### Virgo: Reproducing o1-like MLLM

**Paper**: "Virgo: A Preliminary Exploration on Reproducing o1-like MLLM" (January 2025)

```mermaid
graph TB
    subgraph "Virgo System"
        VLM["Base Vision-Language Model<br/>(e.g., Qwen-VL)"]
        
        subgraph "Training Pipeline"
            SFT["Supervised Fine-Tuning<br/>on multimodal CoT data"]
            RL_TRAIN["RL Training<br/>with vision-aware rewards"]
            PRM_MM["Multimodal PRM<br/>evaluates visual reasoning"]
        end
        
        subgraph "Inference Engine"
            MCTS_VIS["MCTS with<br/>visual state tracking"]
            VERIFY_VIS["Visual verification<br/>at each reasoning step"]
            BEAM["Beam search<br/>over reasoning paths"]
        end
        
        RESULT["o1-like multimodal<br/>reasoning capability"]
    end
    
    VLM --> SFT
    SFT --> RL_TRAIN
    PRM_MM --> RL_TRAIN
    RL_TRAIN --> MCTS_VIS
    MCTS_VIS --> VERIFY_VIS
    VERIFY_VIS --> BEAM
    BEAM --> RESULT
```

**Key Contributions**:
- **First systematic o1 replication** for multimodal domain
- **Hybrid training**: SFT + RL with visual grounding
- **Inference-time search**: MCTS adapted for multimodal state space

Sources: [README.md:61](), [README.md:348](), [assets/paper.json:790-795]()

### AtomThink: Slow Thinking for Multimodal Math

**Paper**: "AtomThink: A Slow Thinking Framework for Multimodal Mathematical Reasoning" (November 2024)

Technical focus on **mathematical reasoning with visual elements** (diagrams, geometric figures, plots):

- **Visual Atom Decomposition**: Breaks complex visual math problems into atomic perceptual units
- **Slow Perception**: Iterative visual understanding before reasoning
- **Math-Specific CoT**: Structured reasoning chains for equation solving with visual context

Sources: [README.md:232](), [README.md:341](), [assets/paper.json:651-656](), [assets/paper.json:762-767]()

### Additional Systems

| System | Focus | Key Feature |
|--------|-------|-------------|
| **Mulberry** | MLLM with o1-like reasoning | Collective MCTS across multiple MLLMs |
| **Visual Agents (Fast/Slow)** | Agent reasoning | Dual-process architecture for visual tasks |
| **Slow Perception** | Geometric reasoning | Step-by-step visual perception |
| **Scaling Inference-Time Search** | Vision value models | Best-of-N with visual comprehension metrics |

Sources: [README.md:178](), [README.md:231](), [README.md:344-347](), [assets/paper.json:797-802]()

---

## Domain-Specific Applications

### Medical Multimodal Reasoning

```mermaid
graph LR
    subgraph "Medical VLM with R1 Reasoning"
        MED_IMG["Medical Image<br/>(X-ray, CT, MRI)"]
        CLINICAL["Clinical Text<br/>(history, symptoms)"]
        
        ENCODER["Multimodal Medical Encoder"]
        
        R1_MED["R1-style Reasoning<br/>trained on medical data"]
        
        subgraph "Reasoning Steps"
            OBSERVE["Observe:<br/>Identify visual findings"]
            CORRELATE["Correlate:<br/>Link to clinical context"]
            HYPOTHESIZE["Hypothesize:<br/>Differential diagnosis"]
            CONCLUDE["Conclude:<br/>Final diagnosis + confidence"]
        end
        
        OUTPUT["Diagnosis + Reasoning Trace"]
    end
    
    MED_IMG --> ENCODER
    CLINICAL --> ENCODER
    ENCODER --> R1_MED
    
    R1_MED --> OBSERVE
    OBSERVE --> CORRELATE
    CORRELATE --> HYPOTHESIZE
    HYPOTHESIZE --> CONCLUDE
    CONCLUDE --> OUTPUT
```

**Example Systems**:
- **MedVLM-R1**: Applies R1 reasoning to radiology and pathology
- **HuatuoGPT-o1**: Medical complex reasoning with LLMs (includes multimodal extension)

Sources: [README.md:53](), [README.md:177](), [README.md:237]()

### Mathematical and Scientific Reasoning

**Geometric Problem Solving**:
- Papers like "Proposing and solving olympiad geometry" use guided tree search
- Slow Perception focuses on step-by-step geometric figure understanding
- AtomThink handles multimodal mathematical reasoning

**Visual STEM Problems**:
- Diagrams, plots, and scientific visualizations
- Multi-step reasoning over visual + textual information
- Process rewards adapted for mathematical correctness

Sources: [README.md:179](), [README.md:345]()

---

## Technical Integration Patterns

### Pattern 1: SFT → RL Pipeline for Multimodal Models

```mermaid
graph TB
    subgraph "Data Preparation"
        VQA["Existing VQA Datasets"]
        SYNTH["Synthetic Multimodal CoT"]
        HUMAN["Human-annotated<br/>reasoning traces"]
    end
    
    subgraph "Stage 1: Supervised Fine-Tuning"
        BASE_VLM["Base VLM"]
        SFT_DATA["Combined SFT Dataset"]
        SFT_MODEL["SFT-trained VLM<br/>with basic reasoning"]
    end
    
    subgraph "Stage 2: RL Training"
        POLICY["Policy Model<br/>(SFT-trained VLM)"]
        REWARD["Reward Model<br/>(multimodal PRM)"]
        RL_ALG["RL Algorithm<br/>(GRPO/PPO)"]
        RL_MODEL["RL-trained VLM<br/>with long-CoT"]
    end
    
    subgraph "Stage 3: Inference Optimization"
        SEARCH_STRAT["Search Strategy<br/>(MCTS/Best-of-N)"]
        VERIFIER["Verification Model"]
        FINAL["Production Model"]
    end
    
    VQA --> SFT_DATA
    SYNTH --> SFT_DATA
    HUMAN --> SFT_DATA
    
    BASE_VLM --> SFT_DATA
    SFT_DATA --> SFT_MODEL
    
    SFT_MODEL --> POLICY
    POLICY --> RL_ALG
    REWARD --> RL_ALG
    RL_ALG --> RL_MODEL
    
    RL_MODEL --> SEARCH_STRAT
    VERIFIER --> SEARCH_STRAT
    SEARCH_STRAT --> FINAL
```

Sources: [README.md:98-138](), [README.md:339-350]()

### Pattern 2: Multimodal Process Reward Models

**Challenges**:
1. **Visual grounding**: Rewards must evaluate visual perception accuracy
2. **Cross-modal coherence**: Reasoning must be consistent with visual evidence
3. **Step-level granularity**: Each reasoning step may involve visual reference

**Implementation**:
```mermaid
graph LR
    STEP["Reasoning Step"]
    
    subgraph "Reward Components"
        TEXT_R["Text Correctness"]
        VIS_R["Visual Grounding"]
        COH_R["Cross-modal Coherence"]
        PROG_R["Progress toward goal"]
    end
    
    COMBINE["Weighted Combination"]
    FINAL_R["Process Reward Score"]
    
    STEP --> TEXT_R
    STEP --> VIS_R
    STEP --> COH_R
    STEP --> PROG_R
    
    TEXT_R --> COMBINE
    VIS_R --> COMBINE
    COH_R --> COMBINE
    PROG_R --> COMBINE
    COMBINE --> FINAL_R
```

Sources: [README.md:68-97](), [README.md:85](), [assets/paper.json:46-152]()

### Pattern 3: Inference-Time Search for Multimodal Tasks

**Best-of-N with Visual Verification**:

```mermaid
graph TB
    QUERY["Query + Image"]
    
    subgraph "Generation Phase"
        GEN["Generate N<br/>reasoning paths"]
        PATH1["Path 1"]
        PATH2["Path 2"]
        PATHN["Path N"]
    end
    
    subgraph "Verification Phase"
        VERIFY["Multimodal Verifier"]
        SCORE1["Score 1"]
        SCORE2["Score 2"]
        SCOREN["Score N"]
    end
    
    SELECT["Select Best Path"]
    ANSWER["Final Answer"]
    
    QUERY --> GEN
    GEN --> PATH1
    GEN --> PATH2
    GEN --> PATHN
    
    PATH1 --> VERIFY
    PATH2 --> VERIFY
    PATHN --> VERIFY
    
    VERIFY --> SCORE1
    VERIFY --> SCORE2
    VERIFY --> SCOREN
    
    SCORE1 --> SELECT
    SCORE2 --> SELECT
    SCOREN --> SELECT
    
    SELECT --> ANSWER
```

**MCTS Adaptation for Multimodal State Space**:
- **State**: Includes both textual reasoning history and visual attention regions
- **Actions**: Text generation tokens + visual grounding operations
- **Rewards**: Multimodal process rewards
- **Rollout policy**: Considers visual context at each step

Sources: [README.md:139-193](), [README.md:344]()

---

## Relationship to Other Parts

### Integration with Part 1 (O1 Replication)

Part 12 systems **extend O1 replication** to multimodal domains:

| Aspect | Text-Only O1 (Part 1) | Multimodal R1 (Part 12) |
|--------|----------------------|------------------------|
| **Input** | Text only | Text + Vision |
| **Reasoning** | Long-CoT text | Long-CoT with visual grounding |
| **Training** | RL on text data | RL on multimodal data |
| **Verification** | Text-based PRM | Multimodal PRM |
| **Inference** | MCTS/Best-of-N | MCTS/Best-of-N with visual state |

Sources: [README.md:45-67]()

### Distinction from Part 9 (Multimodal Agents)

```mermaid
graph LR
    subgraph "Part 9: Diverse Approaches"
        P9_MCTS["MCTS-based<br/>(Mulberry)"]
        P9_SELF["Self-Evolution<br/>(Diving into Self-Evolving)"]
        P9_REFLECT["Reflection<br/>(Vision-Language Self-Improve)"]
        P9_HYBRID["Hybrid Fast-Slow<br/>(Visual Agents)"]
    end
    
    subgraph "Part 12: R1-Specific Focus"
        P12_RL["RL-trained long-CoT<br/>(Virgo, MedVLM-R1)"]
        P12_PROCESS["Process rewards<br/>for multimodal steps"]
        P12_SEARCH["Inference-time search<br/>with visual verification"]
    end
    
    P9_MCTS -.inspiration.-> P12_SEARCH
    P9_SELF -.inspiration.-> P12_RL
    P9_HYBRID -.inspiration.-> P12_RL
```

**Key Difference**: Part 9 covers **general architectural patterns** for multimodal reasoning, while Part 12 specifically focuses on **R1-style RL-based approaches** with long-form reasoning.

Sources: [README.md:339-350]()

### Dependency on Parts 2-4 (Core Methods)

Part 12 systems leverage:
- **Part 2 (Process Rewards)**: Adapted for multimodal step verification
- **Part 3 (Reinforcement Learning)**: Core RL training methodology
- **Part 4 (MCTS)**: Tree search adapted for multimodal state space

Sources: [README.md:68-193]()

---

## Evaluation Considerations

### Multimodal Reasoning Benchmarks

From Part 10, key benchmarks for evaluating R1-driven multimodal reasoning:

| Benchmark | Focus Area | Key Metrics |
|-----------|-----------|-------------|
| **MME-CoT** | Chain-of-thought quality | Reasoning quality, robustness, efficiency |
| **MM-IQ** | Abstraction and reasoning | Human-like reasoning patterns |
| **MV-MATH** | Multimodal math | Multi-visual context reasoning |
| **EnigmaEval** | Long multimodal reasoning | Complex multi-step challenges |
| **CoMT** | Chain of multi-modal thought | Cross-modal reasoning consistency |

Sources: [README.md:368-395]()

### Evaluation Challenges

1. **Visual grounding accuracy**: Does reasoning correctly reference visual content?
2. **Cross-modal coherence**: Is reasoning consistent across modalities?
3. **Long-CoT quality**: Are extended reasoning chains helpful or noisy?
4. **Computational cost**: R1-style inference is expensive for multimodal models

---

## Future Directions

### Emerging Trends (2025)

```mermaid
graph TB
    subgraph "Current State"
        CURR["R1-driven VLMs<br/>Virgo, LLaVA-o1"]
    end
    
    subgraph "Near-term Extensions"
        VIDEO["Video reasoning<br/>temporal + R1"]
        AUDIO["Audio-visual R1<br/>multimodal speech"]
        EMBODIED["Embodied agents<br/>with R1 reasoning"]
    end
    
    subgraph "Advanced Capabilities"
        MULTI_AGENT["Multi-agent R1<br/>collaborative reasoning"]
        TOOL["Tool-augmented<br/>multimodal R1"]
        STREAMING["Streaming inference<br/>efficient R1"]
    end
    
    CURR --> VIDEO
    CURR --> AUDIO
    CURR --> EMBODIED
    
    VIDEO --> MULTI_AGENT
    AUDIO --> MULTI_AGENT
    EMBODIED --> TOOL
    
    MULTI_AGENT --> STREAMING
    TOOL --> STREAMING
```

Sources: [README.md:98-138]()

### Open Research Questions

1. **Scaling Laws**: How do multimodal R1 systems scale with compute/data?
2. **Efficiency**: Can we distill long-CoT multimodal reasoning into fast models?
3. **Generalization**: Do R1-trained multimodal models transfer across domains?
4. **Safety**: How to ensure faithful visual grounding in reasoning chains?

---

## Repository Structure

### Papers in Part 12 Context

While Part 12 is a newer designation, relevant papers can be found in:

**README.md sections**:
- [README.md:339-350]() - Part 9 Multimodal Agent systems (foundation for Part 12)
- [README.md:45-67]() - Part 1 O1 Replication (includes multimodal extensions like Virgo)

**paper.json entries**:
- [assets/paper.json:760-817]() - Part 9 papers with multimodal reasoning
- [assets/paper.json:2-45]() - Part 1 papers including multimodal O1 replications

**Key identifiers for code search**:
- `"Virgo"` - O1-like MLLM reproduction
- `"LLaVA-o1"` - Structured VLM reasoning
- `"AtomThink"` - Multimodal mathematical reasoning
- `"Mulberry"` - MLLM with MCTS
- `"Visual Agents"` - Fast and slow thinking for vision

Sources: [README.md:1-527](), [assets/paper.json:1-848]()

---

## Summary

R1-Driven Multimodal Reasoning (Part 12) represents the **convergence of advanced reasoning methods** from text-only LLMs with vision-language capabilities. Key characteristics:

1. **RL-trained long-form reasoning** adapted for multimodal contexts
2. **Process rewards** that evaluate both textual and visual reasoning steps
3. **Inference-time search** with visual verification and grounding
4. **Domain-specific applications** in medicine, mathematics, and scientific reasoning
5. **Building on Part 9** but with specific focus on R1/o1-style methodologies

The field is rapidly evolving with systems like **Virgo**, **LLaVA-o1**, and domain-specific implementations demonstrating that the R1 paradigm effectively extends to multimodal domains, though with additional complexity in training, inference, and evaluation.

Sources: [README.md:1-527](), [assets/paper.json:1-848]()

---

# Page: Evaluation and Safety

# Evaluation and Safety

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This section covers the infrastructure for assessing reasoning capabilities and ensuring safe deployment of advanced System 2 reasoning models (Parts 10-11 of the research landscape). Evaluation provides the metrics and benchmarks necessary to measure progress in reasoning capabilities, while safety research addresses the unique risks introduced by models with deliberative, chain-of-thought reasoning abilities.

**Related sections:** For the core methodologies being evaluated, see [Core Methodologies](#4). For optimization techniques that affect evaluation efficiency, see [Efficient System2](#5.1). For multimodal evaluation approaches, see [Multimodal Extensions](#6).

**Key focus areas:**
- Benchmarking frameworks that test reasoning at various difficulty levels
- Domain-specific evaluation (mathematics, coding, medicine, multimodal)
- Process-level supervision and reward model evaluation
- Safety alignment techniques for reasoning models
- Attack vectors specific to chain-of-thought reasoning
- Tradeoffs between safety and reasoning capability

Sources: [README.md:41-43](), [README.md:351-453]()

---

## Benchmark Taxonomy

The evaluation landscape for System 2 reasoning models spans multiple dimensions: task difficulty, domain specialization, evaluation granularity (outcome vs. process), and modality.

### Mathematical Reasoning Benchmarks

```mermaid
graph TB
    subgraph "Mathematical Benchmarking Hierarchy"
        BASIC["Basic Math<br/>GSM8K-level"]
        OLYMPIAD["Olympiad Level<br/>AIME, IMO"]
        FRONTIER["Frontier Research<br/>FrontierMath, Putnam"]
        META["Meta-Reasoning<br/>MR-Ben"]
    end
    
    subgraph "Key Benchmarks"
        FRONTIERMATH["FrontierMath<br/>README:355<br/>Expert-level problems"]
        AIME["AIME 2025<br/>README:415<br/>Competition math"]
        MRBEN["MR-Ben<br/>README:356<br/>System-2 meta-reasoning"]
        MATHPERTURB["MATH-Perturb<br/>README:361<br/>Robustness testing"]
        BIGMATH["Big-Math<br/>README:366<br/>Large-scale RL dataset"]
        SUPERGPQA["SuperGPQA<br/>README:359<br/>285 graduate disciplines"]
        LR2BENCH["LR²Bench<br/>README:370<br/>Long-chain reflective<br/>reasoning"]
        ZEBRALOGIC["ZebraLogic<br/>README:418<br/>Logical reasoning limits"]
    end
    
    subgraph "Evaluation Dimensions"
        OUTCOME["Outcome-based<br/>Final answer"]
        PROCESS["Process-based<br/>Step verification"]
        ROBUSTNESS["Robustness<br/>Perturbation tests"]
        SCALING["Scaling Behavior<br/>Test-time compute"]
    end
    
    BASIC --> OLYMPIAD
    OLYMPIAD --> FRONTIER
    OLYMPIAD --> META
    
    FRONTIERMATH -.expert level.-> FRONTIER
    AIME -.competition.-> OLYMPIAD
    MRBEN -.meta.-> META
    
    FRONTIERMATH --> OUTCOME
    MATHPERTURB --> ROBUSTNESS
    LR2BENCH --> PROCESS
    BIGMATH --> SCALING
    
    style FRONTIERMATH fill:#f9f9f9
    style MRBEN fill:#f9f9f9
    style LR2BENCH fill:#f9f9f9
```

**Mathematical benchmark characteristics:**

| Benchmark | Focus | Difficulty | Evaluation Type | Reference |
|-----------|-------|-----------|-----------------|-----------|
| FrontierMath | Research-level problems | Expert | Outcome | [README.md:355]() |
| AIME 2025 | Competition mathematics | Olympiad | Outcome | [README.md:415]() |
| MR-Ben | Meta-reasoning | System-2 | Process | [README.md:356]() |
| MATH-Perturb | Robustness against perturbations | Variable | Robustness | [README.md:361]() |
| Big-Math | Large-scale RL training | Variable | Dataset | [README.md:366]() |
| SuperGPQA | Graduate-level, multi-discipline | Expert | Outcome | [README.md:359]() |
| LR²Bench | Long reflective reasoning chains | Complex | Process | [README.md:370]() |
| ZebraLogic | Logical reasoning limits | Hard | Outcome | [README.md:418]() |

Sources: [README.md:351-423]()

### Code Generation and Reasoning Benchmarks

```mermaid
graph TB
    subgraph "Code Reasoning Evaluation"
        BASIC_CODE["Basic Generation<br/>HumanEval"]
        COMP["Competition Level<br/>AlphaCode, CodeForces"]
        EQUIV["Equivalence Reasoning<br/>EquiBench"]
        ML["ML Engineering<br/>Mle-bench"]
    end
    
    subgraph "Key Code Benchmarks"
        EQUIBENCH["EquiBench<br/>README:358<br/>Equivalence checking"]
        PROBENCH["ProBench<br/>README:417<br/>Competitive programming"]
        MHPP["MHPP<br/>README:409<br/>Beyond basic generation"]
        MLEBENCH["Mle-bench<br/>README:380<br/>ML agent evaluation"]
        CODECRITIC["CodeCriticBench<br/>README:431<br/>Code critique holistic"]
        PROCESSBENCH["ProcessBench<br/>README:429<br/>Process error ID"]
    end
    
    subgraph "Evaluation Focus"
        CORRECTNESS["Correctness<br/>Pass@k"]
        REASONING["Reasoning<br/>Chain-of-thought"]
        CRITIQUE["Error Detection<br/>Critic capability"]
    end
    
    BASIC_CODE --> COMP
    COMP --> EQUIV
    COMP --> ML
    
    EQUIBENCH --> EQUIV
    PROBENCH --> COMP
    MLEBENCH --> ML
    
    EQUIBENCH --> REASONING
    CODECRITIC --> CRITIQUE
    PROCESSBENCH --> CRITIQUE
    PROBENCH --> CORRECTNESS
    
    style EQUIBENCH fill:#f9f9f9
    style CODECRITIC fill:#f9f9f9
    style MLEBENCH fill:#f9f9f9
```

**Code benchmark focus areas:**
- **EquiBench**: Tests code reasoning via equivalence checking, requiring models to determine if different implementations are functionally equivalent
- **ProBench**: Competitive programming problems requiring advanced algorithmic reasoning
- **Mle-bench**: Evaluates ML agents on real machine learning engineering tasks
- **CodeCriticBench**: Holistic code critique capabilities beyond simple error detection
- **ProcessBench**: Identifies process-level errors in mathematical reasoning code

Sources: [README.md:358](), [README.md:380](), [README.md:409](), [README.md:417](), [README.md:429](), [README.md:431]()

### Multimodal Reasoning Benchmarks

```mermaid
graph TB
    subgraph "Multimodal Evaluation Types"
        VQA["Visual QA<br/>Image understanding"]
        MMREASON["MM Reasoning<br/>Multi-step chains"]
        SPATIAL["Spatial Reasoning<br/>Geometry, layouts"]
        VIDEO["Video Understanding<br/>Temporal reasoning"]
    end
    
    subgraph "Key MM Benchmarks"
        ZEROBENCH["ZeroBench<br/>README:367<br/>Impossible visuals"]
        MMECOT["MME-CoT<br/>README:368<br/>Chain quality/efficiency"]
        MMIQ["MM-IQ<br/>README:369<br/>Abstraction & reasoning"]
        COMT["CoMT<br/>README:395<br/>Multi-modal thought<br/>chains"]
        ENIGMA["EnigmaEval<br/>README:398<br/>Long multimodal<br/>reasoning"]
        LEGO["LEGO-Puzzles<br/>README:402<br/>Multi-step spatial"]
        MMSCIBENCH["MMSciBench<br/>README:401<br/>Scientific problems"]
    end
    
    subgraph "Evaluation Aspects"
        CHAIN_QUALITY["CoT Quality"]
        ROBUSTNESS_MM["Robustness"]
        EFFICIENCY_MM["Efficiency"]
        STEP_REASONING["Step-by-step"]
    end
    
    VQA --> MMREASON
    MMREASON --> SPATIAL
    MMREASON --> VIDEO
    
    ZEROBENCH -.impossible.-> VQA
    MMECOT -.chain eval.-> MMREASON
    MMIQ -.abstraction.-> MMREASON
    ENIGMA -.long chains.-> MMREASON
    LEGO -.spatial.-> SPATIAL
    
    MMECOT --> CHAIN_QUALITY
    MMECOT --> EFFICIENCY_MM
    ZEROBENCH --> ROBUSTNESS_MM
    ENIGMA --> STEP_REASONING
    
    style MMECOT fill:#f9f9f9
    style ENIGMA fill:#f9f9f9
    style ZEROBENCH fill:#f9f9f9
```

**Notable multimodal benchmarks:**
- **ZeroBench**: Tests models on "impossible" visual patterns that require going beyond surface-level perception
- **MME-CoT**: Evaluates chain-of-thought quality, robustness, and efficiency in multimodal reasoning
- **EnigmaEval**: Long-form multimodal reasoning challenges
- **LEGO-Puzzles**: Multi-step spatial reasoning requiring planning
- **MM-IQ**: Tests human-like abstraction and reasoning with visual patterns

Sources: [README.md:367-402]()

### Agent and Interactive Benchmarks

```mermaid
graph TB
    subgraph "Agent Evaluation Domains"
        WEB["Web Browsing<br/>Navigation & tasks"]
        MOBILE["Mobile Agents<br/>UI interaction"]
        OS["OS Agents<br/>Desktop tasks"]
        GAME["Multi-Agent<br/>Decision-making"]
    end
    
    subgraph "Key Agent Benchmarks"
        BROWSECOMP["BrowseComp<br/>README:379<br/>OpenAI browsing"]
        WEBGAMES["WebGames<br/>README:387<br/>Challenging browsing"]
        UIR1["UI-R1<br/>README:388<br/>GUI action prediction"]
        OSWORLD["OSWorld<br/>README:382<br/>Real computer env"]
        MOBILEAGENT["Mobile-Agent-E<br/>README:384<br/>Self-evolving"]
        TOOLCOMP["ToolComp<br/>README:383<br/>Multi-tool reasoning"]
        GAMEEVAL["Game Decision<br/>README:381<br/>Multi-agent games"]
    end
    
    subgraph "Evaluation Criteria"
        SUCCESS["Success Rate"]
        EFFICIENCY_AGENT["Efficiency"]
        REASONING_AGENT["Reasoning Quality"]
        TOOLS["Tool Use"]
    end
    
    WEB --> BROWSECOMP
    WEB --> WEBGAMES
    MOBILE --> UIR1
    MOBILE --> MOBILEAGENT
    OS --> OSWORLD
    GAME --> GAMEEVAL
    
    TOOLCOMP -.multi-tool.-> TOOLS
    UIR1 -.GUI.-> SUCCESS
    OSWORLD -.real env.-> SUCCESS
    BROWSECOMP -.navigation.-> REASONING_AGENT
    
    style OSWORLD fill:#f9f9f9
    style TOOLCOMP fill:#f9f9f9
    style UIR1 fill:#f9f9f9
```

**Agent benchmark categories:**
- **Web browsing**: BrowseComp, WebGames test navigation and complex web task completion
- **Mobile/GUI**: UI-R1, Mobile-Agent-E evaluate smartphone and GUI interaction
- **OS-level**: OSWorld provides real computer environments for comprehensive testing
- **Tool use**: ToolComp assesses multi-tool reasoning and process supervision
- **Multi-agent**: Game-based decision-making in competitive/cooperative scenarios

Sources: [README.md:379-388]()

---

## Process Supervision and Reward Model Evaluation

Process-level evaluation assesses intermediate reasoning steps rather than just final answers, which is critical for System 2 reasoning models.

```mermaid
graph TB
    subgraph "Process Evaluation Frameworks"
        PRM["Process Reward Models<br/>Step-wise supervision"]
        ERROR["Error Detection<br/>Mistake identification"]
        CRITIC["Critique Models<br/>Quality assessment"]
    end
    
    subgraph "Key Process Benchmarks"
        PRMBENCH["PRMBench<br/>README:365<br/>Fine-grained PRM eval"]
        RMBENCH["RM-Bench<br/>README:364<br/>Subtlety & style"]
        MULTIMODAL_RM["Multimodal RewardBench<br/>README:360<br/>VLM rewards"]
        REWARDBENCH["RewardBench<br/>README:424<br/>Reward model eval"]
        PROCESSBENCH2["ProcessBench<br/>README:429<br/>Math error ID"]
        ERRORRADAR["ErrorRadar<br/>README:428<br/>MM error detection"]
        JUDGEBENCH["JudgeBench<br/>README:427<br/>LLM-based judges"]
        CRITICBENCH["CriticBench<br/>README:426<br/>Critique-correct"]
    end
    
    subgraph "Evaluation Granularity"
        STEP["Step-level<br/>Individual reasoning"]
        CHAIN["Chain-level<br/>Full reasoning path"]
        ERROR_LEVEL["Error-level<br/>Specific mistakes"]
    end
    
    PRM --> PRMBENCH
    PRM --> RMBENCH
    PRM --> MULTIMODAL_RM
    
    ERROR --> PROCESSBENCH2
    ERROR --> ERRORRADAR
    
    CRITIC --> JUDGEBENCH
    CRITIC --> CRITICBENCH
    
    PRMBENCH --> STEP
    PROCESSBENCH2 --> ERROR_LEVEL
    CRITICBENCH --> CHAIN
    
    style PRMBENCH fill:#f9f9f9
    style RMBENCH fill:#f9f9f9
    style PROCESSBENCH2 fill:#f9f9f9
```

**Process supervision benchmark characteristics:**

| Benchmark | Type | Focus | Granularity | Reference |
|-----------|------|-------|-------------|-----------|
| PRMBench | PRM | Fine-grained process rewards | Step-level | [README.md:365]() |
| RM-Bench | PRM | Subtlety and style | Chain-level | [README.md:364]() |
| Multimodal RewardBench | PRM | Vision-language rewards | Step-level | [README.md:360]() |
| ProcessBench | Error | Math reasoning errors | Error-level | [README.md:429]() |
| ErrorRadar | Error | Multimodal error detection | Error-level | [README.md:428]() |
| CriticBench | Critique | Critique-correct reasoning | Chain-level | [README.md:426]() |
| JudgeBench | Judge | LLM-based evaluation | Chain-level | [README.md:427]() |

**Integration with Part 2 (Process Reward Models):**
- PRMBench directly evaluates techniques from [README.md:68-97]() like Math-Shepherd, AutoPSV
- Provides standardized metrics for comparing PRM approaches
- Tests generalization across different reasoning domains

Sources: [README.md:360](), [README.md:364-365](), [README.md:424-429]()

---

## General Reasoning and Robustness Evaluation

```mermaid
graph TB
    subgraph "Evaluation Dimensions"
        DIFFICULTY["Difficulty Scaling"]
        ROBUSTNESS["Robustness Testing"]
        OVERTHINK["Overthinking Detection"]
        GENERALIZATION["Out-of-Distribution"]
    end
    
    subgraph "Key Benchmarks"
        HUMANITY["Humanity's Last Exam<br/>README:363<br/>Hard general problems"]
        LIVEBENCH["LiveBench<br/>README:411<br/>Contamination-free"]
        THINKBENCH["ThinkBench<br/>README:416<br/>Dynamic OOD"]
        BIGBENCH["BIG-Bench Extra Hard<br/>README:371<br/>Challenging tasks"]
        OVERTHINK_BENCH["Overthinking Detection<br/>README:357<br/>o1-like models"]
        S1BENCH["S1-Bench<br/>README:377<br/>System 1 capability"]
        QUESTBENCH["QuestBench<br/>README:420<br/>Information seeking"]
    end
    
    subgraph "Special Focus Areas"
        CONTAMINATION["Contamination<br/>Prevention"]
        SYSTEM_MIX["System 1 vs 2<br/>Appropriateness"]
        INFERENCE_TIME["Inference-time<br/>Compute"]
    end
    
    DIFFICULTY --> HUMANITY
    DIFFICULTY --> BIGBENCH
    
    ROBUSTNESS --> THINKBENCH
    ROBUSTNESS --> LIVEBENCH
    
    OVERTHINK --> OVERTHINK_BENCH
    OVERTHINK --> S1BENCH
    
    LIVEBENCH --> CONTAMINATION
    S1BENCH --> SYSTEM_MIX
    OVERTHINK_BENCH --> INFERENCE_TIME
    QUESTBENCH --> GENERALIZATION
    
    style LIVEBENCH fill:#f9f9f9
    style OVERTHINK_BENCH fill:#f9f9f9
    style S1BENCH fill:#f9f9f9
```

**Critical evaluation challenges:**
- **Contamination**: LiveBench provides contamination-limited evaluation for honest benchmarking
- **Overthinking**: Models may waste compute on simple problems better solved with System 1 thinking
- **OOD generalization**: ThinkBench tests dynamic out-of-distribution scenarios
- **System appropriateness**: S1-Bench evaluates when fast thinking suffices vs. when slow thinking is needed

Sources: [README.md:357](), [README.md:363](), [README.md:371](), [README.md:377](), [README.md:411](), [README.md:416](), [README.md:420]()

---

## Safety Infrastructure for Reasoning Models

Chain-of-thought reasoning introduces unique safety challenges. Models with deliberative capabilities can potentially reason their way around safety constraints or be manipulated through reasoning-specific attacks.

### Safety Landscape

```mermaid
graph TB
    subgraph "Safety Challenges"
        ALIGN["Alignment<br/>Safety reasoning"]
        ATTACK["Attack Vectors<br/>CoT exploitation"]
        HIDDEN["Hidden Risks<br/>Emergent behaviors"]
        TRADEOFF["Safety-Performance<br/>Tradeoffs"]
    end
    
    subgraph "Defense Mechanisms"
        DELIB_ALIGN["Deliberative Alignment<br/>README:439<br/>Reasoning-based safety"]
        GUARDREASONER["GuardReasoner<br/>README:443<br/>Reasoning safeguards"]
        SAFECHAIN["SafeChain<br/>README:444<br/>Long CoT safety"]
        THINKGUARD["ThinkGuard<br/>README:445<br/>Slow thinking guards"]
        STAR1["STAR-1<br/>README:453<br/>1K data alignment"]
    end
    
    subgraph "Attack Methods"
        HCOT["H-CoT<br/>README:447<br/>Hijacking CoT safety"]
        BOT["BoT<br/>README:448<br/>Backdoor attacks"]
        OVERTHINK_ATTACK["OverThink<br/>README:442<br/>Slowdown attacks"]
    end
    
    subgraph "Assessment"
        HIDDEN_RISKS["Hidden Risks R1<br/>README:449<br/>Safety assessment"]
        ILLUSORY["Illusory Safety<br/>README:450<br/>Redteaming report"]
        SAFETY_TAX["Safety Tax<br/>README:451<br/>Reasoning degradation"]
    end
    
    ALIGN --> DELIB_ALIGN
    ALIGN --> GUARDREASONER
    ALIGN --> SAFECHAIN
    ALIGN --> THINKGUARD
    ALIGN --> STAR1
    
    ATTACK --> HCOT
    ATTACK --> BOT
    ATTACK --> OVERTHINK_ATTACK
    
    HIDDEN --> HIDDEN_RISKS
    HIDDEN --> ILLUSORY
    
    TRADEOFF --> SAFETY_TAX
    
    style HCOT fill:#ffe6e6
    style DELIB_ALIGN fill:#e6ffe6
    style SAFETY_TAX fill:#fff6e6
```

Sources: [README.md:437-453]()

### Safety Alignment Approaches

**Deliberative Alignment** [README.md:439]()  
Leverages the reasoning capabilities themselves for safety. Models use chain-of-thought to reason about safety policies before generating responses. This approach exploits System 2 thinking for ethical deliberation.

**GuardReasoner** [README.md:443]()  
A reasoning-based safeguard system that uses deliberative processes to detect and prevent unsafe outputs. Integrates safety checks into the reasoning pipeline.

**SafeChain** [README.md:444]()  
Specifically addresses safety concerns in long chain-of-thought reasoning. As reasoning chains grow longer (thousands of tokens), maintaining safety throughout becomes critical.

**ThinkGuard** [README.md:445]()  
Implements "slow thinking" for guardrails, matching the deliberative nature of the models being protected. Uses multi-step reasoning to evaluate potential harms.

**STAR-1** [README.md:453]()  
Demonstrates that safer alignment can be achieved with minimal data (1K examples), suggesting efficiency improvements for safety tuning.

Sources: [README.md:439](), [README.md:443-445](), [README.md:453]()

### Attack Vectors and Vulnerabilities

```mermaid
graph LR
    subgraph "Attack Surface"
        COT["Chain-of-Thought<br/>Reasoning Process"]
        POLICY["Safety Policy<br/>Reasoning"]
        LENGTH["Long Thought<br/>Sequences"]
    end
    
    subgraph "Specific Attacks"
        HCOT_DETAIL["H-CoT Attack<br/>Hijacks safety reasoning<br/>Targets: o1, o3, R1, Gemini"]
        BOT_DETAIL["BoT Attack<br/>Backdoor in thought<br/>Breaking long processes"]
        OVERTHINK_DETAIL["OverThink Attack<br/>Slowdown exploitation<br/>DoS via reasoning"]
    end
    
    subgraph "Consequences"
        JAILBREAK["Jailbreak<br/>Safety bypass"]
        DOS["Denial of Service<br/>Resource exhaustion"]
        HIDDEN_UNSAFE["Hidden Unsafe<br/>Behavior"]
    end
    
    COT --> HCOT_DETAIL
    LENGTH --> BOT_DETAIL
    COT --> OVERTHINK_DETAIL
    
    HCOT_DETAIL --> JAILBREAK
    BOT_DETAIL --> HIDDEN_UNSAFE
    OVERTHINK_DETAIL --> DOS
    
    style HCOT_DETAIL fill:#ffe6e6
    style BOT_DETAIL fill:#ffe6e6
    style OVERTHINK_DETAIL fill:#ffe6e6
```

**H-CoT (Hijacking Chain-of-Thought)** [README.md:447]()  
A sophisticated jailbreak technique that manipulates the chain-of-thought reasoning process itself. Successfully attacks major reasoning models including:
- OpenAI o1 and o3
- DeepSeek-R1
- Gemini 2.0 Flash Thinking

The attack exploits the model's safety reasoning mechanism by inserting adversarial reasoning steps that lead to unsafe conclusions.

**BoT (Breaking of Thought)** [README.md:448]()  
A backdoor attack targeting long thought processes. Inserts malicious triggers into the reasoning chain that activate harmful behaviors while remaining hidden during normal operation.

**OverThink Attack** [README.md:442]()  
A denial-of-service attack that forces reasoning models into unnecessarily long deliberation, exhausting computational resources. Exploits the model's tendency to engage System 2 thinking even when unnecessary.

Sources: [README.md:442](), [README.md:447-448]()

### Safety Assessment and Challenges

**Research findings from safety assessments:**

| Finding | Source | Implication |
|---------|--------|-------------|
| DeepSeek-R1 RL strategies have shortcomings | [README.md:106]() | Reinforcement learning alone insufficient for safety |
| Hidden risks in R1 | [README.md:449]() | Comprehensive safety assessment needed |
| Illusory safety (redteaming) | [README.md:450]() | Even strong models (OpenAI, Anthropic, Google) vulnerable |
| Safety Tax | [README.md:451]() | Safety alignment degrades reasoning capability |
| OpenAI o1/o3 "think" about safety | [README.md:440]() | Promising direction but needs validation |

**Key challenge: Safety-Performance Tradeoff**  
The "Safety Tax" phenomenon [README.md:451]() reveals that safety alignment makes reasoning models "less reasonable." This creates a fundamental tension:
- Stronger safety constraints → Reduced reasoning capability
- Weaker safety constraints → Increased risk

**Blog post discussions:**
- Anthropic's faithfulness measurement [README.md:438](): Measuring whether CoT reasoning genuinely guides behavior
- Why researchers worry about DeepSeek [README.md:441](): Hidden safety warnings and concerns
- OpenAI's safety policy training [README.md:440](): Using reasoning for safety evaluation

Sources: [README.md:106](), [README.md:438-451]()

---

## Integration with Core Methodologies

Evaluation and safety considerations interact deeply with the core reasoning techniques from Parts 1-6.

```mermaid
graph TB
    subgraph "Core Methodologies Evaluated"
        O1["Part 1: O1 Replication<br/>README:45-67"]
        PRM["Part 2: Process Rewards<br/>README:68-97"]
        RL["Part 3: Reinforcement Learning<br/>README:98-138"]
        MCTS["Part 4: MCTS/Tree Search<br/>README:139-193"]
        SELF["Part 5: Self-Training<br/>README:194-224"]
        REFLECT["Part 6: Reflection<br/>README:225-241"]
    end
    
    subgraph "Evaluation Benchmarks"
        MATH_BENCH["Math Benchmarks<br/>FrontierMath, AIME"]
        CODE_BENCH["Code Benchmarks<br/>ProBench, EquiBench"]
        PROCESS_BENCH["Process Benchmarks<br/>PRMBench"]
        AGENT_BENCH["Agent Benchmarks<br/>OSWorld, ToolComp"]
    end
    
    subgraph "Safety Mechanisms"
        ALIGNMENT["Deliberative Alignment"]
        GUARDS["GuardReasoner"]
        ASSESSMENT["Safety Assessment"]
    end
    
    O1 -.evaluated by.-> MATH_BENCH
    O1 -.evaluated by.-> CODE_BENCH
    O1 -.safety concerns.-> ASSESSMENT
    
    PRM -.benchmarked by.-> PROCESS_BENCH
    PRM -.guides.-> RL
    PRM -.guides.-> MCTS
    
    RL -.safety challenges.-> ALIGNMENT
    RL -.performance.-> MATH_BENCH
    
    MCTS -.search quality.-> AGENT_BENCH
    MCTS -.combined with PRM.-> PROCESS_BENCH
    
    SELF -.generalization.-> MATH_BENCH
    SELF -.robustness.-> CODE_BENCH
    
    REFLECT -.error detection.-> PROCESS_BENCH
    REFLECT -.safety.-> GUARDS
    
    style PROCESS_BENCH fill:#fff9e6
    style ALIGNMENT fill:#e6ffe6
    style ASSESSMENT fill:#ffe6e6
```

**Key integration patterns:**

1. **PRM → Benchmarks**: Process Reward Models from Part 2 directly evaluated by PRMBench [README.md:365]()
2. **RL → Safety**: Reinforcement Learning approaches (Part 3) create safety challenges requiring deliberative alignment [README.md:439]()
3. **MCTS → Process Evaluation**: Tree search methods (Part 4) benefit from step-wise process benchmarks
4. **O1 Replication → Comprehensive Testing**: O1-like systems tested across all benchmark categories
5. **Reflection → Error Detection**: Reflection mechanisms (Part 6) measured by error detection benchmarks

**Specific examples:**
- ReST-MCTS* [README.md:78](), [README.md:175](): Combines Parts 2, 4, 5; evaluated on math and process benchmarks
- DeepSeek-R1 [README.md:107](): Part 3 RL approach; requires safety assessment [README.md:449]()
- Math-Shepherd [README.md:73](): Part 2 PRM; benchmarked for automated supervision
- H-CoT attack [README.md:447](): Exploits reasoning from Parts 1-6; demonstrates need for safety infrastructure

Sources: [README.md:45-241](), [README.md:351-453]()

---

## Evaluation Methodology Patterns

Different evaluation approaches serve different purposes in assessing System 2 reasoning models.

```mermaid
graph TB
    subgraph "Evaluation Paradigms"
        OUTCOME["Outcome-based<br/>Final answer correctness"]
        PROCESS["Process-based<br/>Intermediate step quality"]
        ROBUSTNESS["Robustness-based<br/>Perturbation testing"]
        EFFICIENCY["Efficiency-based<br/>Compute vs. accuracy"]
    end
    
    subgraph "Outcome Evaluation"
        ACCURACY["Accuracy Metrics<br/>Pass@k, Exact match"]
        DIFFICULTY["Difficulty Scaling<br/>Easy → Expert"]
        DOMAIN["Domain Coverage<br/>Math, Code, Multimodal"]
    end
    
    subgraph "Process Evaluation"
        STEP_CORRECT["Step Correctness<br/>Per-step verification"]
        CHAIN_QUALITY["Chain Quality<br/>Coherence, efficiency"]
        ERROR_ID["Error Identification<br/>Mistake localization"]
    end
    
    subgraph "Meta-Evaluation"
        OVERTHINK_DETECT["Overthinking Detection<br/>README:357"]
        SYSTEM_SELECT["System Selection<br/>Fast vs. Slow"]
        TEST_TIME["Test-time Scaling<br/>Compute efficiency"]
    end
    
    OUTCOME --> ACCURACY
    OUTCOME --> DIFFICULTY
    OUTCOME --> DOMAIN
    
    PROCESS --> STEP_CORRECT
    PROCESS --> CHAIN_QUALITY
    PROCESS --> ERROR_ID
    
    EFFICIENCY --> OVERTHINK_DETECT
    EFFICIENCY --> SYSTEM_SELECT
    EFFICIENCY --> TEST_TIME
    
    ROBUSTNESS -.tests.-> ACCURACY
    ROBUSTNESS -.tests.-> STEP_CORRECT
    
    style OVERTHINK_DETECT fill:#fff9e6
    style STEP_CORRECT fill:#fff9e6
    style TEST_TIME fill:#fff9e6
```

**Outcome-based evaluation:**
- Traditional metrics: accuracy, pass@k, exact match
- Difficulty progression: basic → olympiad → research-level
- Examples: FrontierMath [README.md:355](), AIME [README.md:415]()

**Process-based evaluation:**
- Step-level correctness via PRMs
- Chain coherence and reasoning quality
- Error localization and diagnosis
- Examples: PRMBench [README.md:365](), ProcessBench [README.md:429]()

**Robustness evaluation:**
- Perturbation testing (MATH-Perturb [README.md:361]())
- Out-of-distribution generalization (ThinkBench [README.md:416]())
- Contamination prevention (LiveBench [README.md:411]())

**Efficiency evaluation:**
- Overthinking detection [README.md:357](): When does o1-like reasoning waste compute?
- System selection: Appropriateness of System 1 vs System 2
- Test-time compute scaling: Relationship between compute and performance

Sources: [README.md:355](), [README.md:357](), [README.md:365](), [README.md:411](), [README.md:415-416](), [README.md:429]()

---

## Domain-Specific Evaluation

### Medical Domain

```mermaid
graph LR
    subgraph "Medical Benchmarks"
        PRELIMINARY["Preliminary Study<br/>README:354<br/>o1 in medicine"]
        MEDXPERT["MedXpertQA<br/>README:413<br/>Expert-level reasoning"]
        MEDEC["MedEC<br/>README:430<br/>Error detection"]
    end
    
    subgraph "Medical Applications"
        O1_MED["O1-like Medical<br/>HuatuoGPT-o1"]
        R1_MED["R1-style Medical<br/>MedVLM-R1, Med-RLVR"]
    end
    
    subgraph "Evaluation Focus"
        REASONING_MED["Clinical Reasoning"]
        SAFETY_MED["Patient Safety"]
        ERROR_MED["Error Detection"]
    end
    
    PRELIMINARY --> REASONING_MED
    MEDXPERT --> REASONING_MED
    MEDEC --> ERROR_MED
    
    O1_MED -.evaluated.-> MEDXPERT
    R1_MED -.evaluated.-> MEDXPERT
    
    ERROR_MED --> SAFETY_MED
    
    style MEDXPERT fill:#fff9e6
    style SAFETY_MED fill:#e6ffe6
```

Medical domain requires specialized evaluation focusing on:
- Expert-level diagnostic reasoning
- Error detection for patient safety
- Multi-step clinical decision-making

Sources: [README.md:354](), [README.md:413](), [README.md:430]()

### Physics and Science

```mermaid
graph LR
    subgraph "Science Benchmarks"
        PHYSREASON["PhysReason<br/>README:385<br/>Physics reasoning"]
        TPBENCH["TPBench<br/>README:414<br/>Theoretical physics"]
        MMSCIBENCH["MMSciBench<br/>README:401<br/>Multimodal science"]
        RESEARCHBENCH["ResearchBench<br/>README:376<br/>Scientific discovery"]
    end
    
    subgraph "Capabilities Tested"
        PHYSICS["Physical Laws"]
        THEORY["Theoretical Reasoning"]
        DISCOVERY["Scientific Discovery"]
        MULTIMODAL_SCI["Visual Science"]
    end
    
    PHYSREASON --> PHYSICS
    TPBENCH --> THEORY
    RESEARCHBENCH --> DISCOVERY
    MMSCIBENCH --> MULTIMODAL_SCI
    
    style TPBENCH fill:#fff9e6
    style RESEARCHBENCH fill:#fff9e6
```

Scientific domain evaluation tests:
- Physical reasoning and simulation
- Theoretical proof construction
- Research-level problem solving
- Multimodal scientific understanding

Sources: [README.md:376](), [README.md:385](), [README.md:401](), [README.md:414]()

---

## Future Directions and Open Challenges

### Emerging Evaluation Needs

1. **Contamination-Free Benchmarking**
   - LiveBench [README.md:411]() addresses contamination
   - Need for continuously updated benchmarks
   - Private test sets for honest evaluation

2. **Long-Chain Reasoning Assessment**
   - LR²Bench [README.md:370]() for long reflective chains
   - EnigmaEval [README.md:398]() for extended multimodal reasoning
   - Evaluating chains with thousands of tokens

3. **Process Supervision at Scale**
   - PRMBench [README.md:365]() provides foundation
   - Need for automated step verification
   - Cross-domain process reward models

4. **Safety-Performance Balance**
   - Safety Tax [README.md:451]() identified tradeoff
   - Methods to maintain reasoning while ensuring safety
   - Principled approaches to alignment without degradation

### Research Questions

**Evaluation:**
- How to measure "overthinking" appropriately? [README.md:357]()
- What metrics best capture reasoning quality vs. final correctness?
- How to evaluate reasoning chains too long for human verification?
- Can we predict benchmark performance from model architecture?

**Safety:**
- How to defend against CoT-specific attacks like H-CoT? [README.md:447]()
- What is the minimal safety tax for reasoning models? [README.md:451]()
- How to ensure faithful reasoning (not just accurate outputs)? [README.md:438]()
- Can reasoning enhance or undermine safety?

### Benchmark Development Trends

```mermaid
graph TB
    CURRENT["Current State<br/>2024-2025"]
    
    subgraph "Trend 1: Difficulty Scaling"
        HARDER["Harder Problems<br/>FrontierMath, Humanity's<br/>Last Exam"]
    end
    
    subgraph "Trend 2: Process Focus"
        PROCESS_SHIFT["Process over Outcome<br/>PRMBench, ProcessBench"]
    end
    
    subgraph "Trend 3: Dynamic Evaluation"
        DYNAMIC["Contamination-Free<br/>LiveBench, ThinkBench"]
    end
    
    subgraph "Trend 4: Multimodal Expansion"
        MM_EXPAND["Vision-Language CoT<br/>MME-CoT, EnigmaEval"]
    end
    
    subgraph "Trend 5: Agent Integration"
        AGENT_TREND["Real-World Agents<br/>OSWorld, ToolComp"]
    end
    
    CURRENT --> HARDER
    CURRENT --> PROCESS_SHIFT
    CURRENT --> DYNAMIC
    CURRENT --> MM_EXPAND
    CURRENT --> AGENT_TREND
    
    style CURRENT fill:#e6f3ff
```

**Key trends:**
1. **Difficulty escalation**: Moving from basic to research-level problems
2. **Process-centric**: Shift from outcome to intermediate step evaluation
3. **Dynamic benchmarks**: Addressing contamination through continuous updates
4. **Multimodal reasoning**: Extending CoT evaluation beyond text
5. **Real-world agents**: Testing reasoning in interactive environments

Sources: [README.md:351-453]()

---

## Repository Data Structure

The benchmark and safety papers are cataloged in the repository's data layer.

**File structure:**
- `assets/paper.json`: Structured metadata for all papers including Parts 10-11
- `src/main.py`: Build script that processes paper metadata
- `README.md`: Hand-curated descriptions with expert commentary

**Data processing pipeline:**
```
paper.json (Part 10: lines ~351-433, Part 11: lines ~437-453)
    ↓
src/main.py: Load → Extract → Resolve
    ↓
src/table.md (chronological view)
src/list.md (categorized view)
```

The JSON structure groups papers by research part, with each entry containing:
- Title
- ArXiv/Conference venue
- Publication date
- Links to paper and code
- Category labels

**Build system:** See [Repository Structure and Maintenance](#10) for details on how benchmark and safety papers are processed and presented.

Sources: [README.md:1-509]()

---

## Summary

Evaluation and safety infrastructure provides critical feedback loops for System 2 reasoning research:

**Evaluation landscape:**
- **Mathematical**: FrontierMath, AIME, MR-Ben span basic to research-level
- **Code**: EquiBench, ProBench test reasoning in programming
- **Multimodal**: MME-CoT, EnigmaEval assess visual reasoning chains
- **Agent**: OSWorld, ToolComp evaluate interactive reasoning
- **Process**: PRMBench, ProcessBench enable step-level assessment

**Safety challenges:**
- **Attack vectors**: H-CoT, BoT, OverThink exploit reasoning processes
- **Defense mechanisms**: Deliberative Alignment, GuardReasoner, SafeChain
- **Tradeoffs**: Safety Tax reveals performance degradation from alignment
- **Assessment needs**: Hidden risks require comprehensive evaluation

**Integration patterns:**
- Process Reward Models (Part 2) benchmarked by PRMBench
- RL approaches (Part 3) create safety challenges
- O1 replication (Part 1) requires comprehensive evaluation across all dimensions
- MCTS (Part 4) benefits from process-level benchmarks

**Future directions:**
- Contamination-free dynamic benchmarks
- Long-chain reasoning assessment
- Safety-performance balance optimization
- Cross-domain process supervision

The evaluation and safety infrastructure ensures that advances in System 2 reasoning capabilities are measured reliably and deployed responsibly.

Sources: [README.md:41-43](), [README.md:351-453]()

---

# Page: Benchmarks and Datasets

# Benchmarks and Datasets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/list.md](src/list.md)

</details>



## Purpose and Scope

This page documents the evaluation infrastructure for System 2 reasoning capabilities in Large Language Models. It catalogs benchmarks, datasets, and evaluation frameworks that assess deliberate reasoning, step-by-step verification, and complex problem-solving across multiple domains. These resources enable researchers to measure progress in transitioning from fast, intuitive System 1 responses to slow, deliberate System 2 thinking.

For methodologies that these benchmarks evaluate, see [Core Methodologies](#4). For safety considerations in evaluation, see [Reasoning and Safety](#7.2).

**Sources:** [README.md:351-433]()

---

## Benchmark Taxonomy and Organization

The repository organizes benchmarks into several categories, each targeting different aspects of System 2 reasoning. The benchmarks are stored in structured metadata within the repository's data layer.

```mermaid
graph TB
    subgraph "Data_Layer"
        JSON["assets/paper.json<br/>Part 10: Benchmark and Datasets<br/>Structured Metadata"]
    end
    
    subgraph "Mathematical_Reasoning"
        FRONTIER["FrontierMath<br/>Advanced Mathematical Reasoning<br/>arXiv 2024-11"]
        MATHPERTURB["MATH-Perturb<br/>Hard Perturbations<br/>arXiv 2025-02"]
        BIGMATH["Big-Math<br/>Large-Scale RL Dataset<br/>arXiv 2025-02"]
        PUTNAM["Putnam-AXIOM<br/>Higher-Level Reasoning<br/>NeurIPS 2024"]
    end
    
    subgraph "Process_and_Reward"
        PRMBENCH["PRMBench<br/>Process-Level Rewards<br/>arXiv 2025-01"]
        RMBENCH["RM-Bench<br/>Reward Model Evaluation<br/>ICLR 2025"]
        TOOLCOMP["ToolComp<br/>Multi-Tool Supervision<br/>arXiv 2025-01"]
        PROCESSBENCH["ProcessBench<br/>Error Detection<br/>arXiv 2024-12"]
    end
    
    subgraph "Multimodal_Reasoning"
        MMECOT["MME-CoT<br/>Chain-of-Thought Quality<br/>arXiv 2025-02"]
        MMIQ["MM-IQ<br/>Abstraction & Reasoning<br/>arXiv 2025-02"]
        ZEROBENCH["ZeroBench<br/>Visual Reasoning<br/>arXiv 2025-02"]
        HUMANEVAL_V["HumanEval-V<br/>Visual Coding Tasks<br/>arXiv 2024-10"]
    end
    
    subgraph "Agent_Capabilities"
        OSWORLD["OSWorld<br/>Real Computer Environments<br/>NeurIPS 2024"]
        MLEBENCH["MLE-bench<br/>ML Engineering<br/>arXiv 2024-10"]
        BROWSECOMP["BrowseComp<br/>Browsing Agents<br/>OpenAI 2025-04"]
        MOBILE["Mobile-Agent-E<br/>Self-Evolving Assistant<br/>arXiv 2025-01"]
    end
    
    subgraph "Meta_Reasoning"
        MRBEN["MR-Ben<br/>System-2 Thinking<br/>NeurIPS 2024"]
        LONGREASON["LongReason<br/>Long-Context Reasoning<br/>arXiv 2025-01"]
        HUMANITY["Humanity's Last Exam<br/>Human-Level Challenge<br/>arXiv 2025-01"]
    end
    
    JSON --> FRONTIER
    JSON --> PRMBENCH
    JSON --> MMECOT
    JSON --> OSWORLD
    JSON --> MRBEN
```

**Sources:** [README.md:351-433](), [assets/paper.json:818-847]()

---

## Mathematical Reasoning Benchmarks

Mathematical reasoning benchmarks evaluate step-by-step problem-solving, proof generation, and numerical reasoning capabilities. These benchmarks range from competition-level problems to research-grade mathematical challenges.

### Core Mathematical Benchmarks

| Benchmark | Domain | Difficulty | Key Features | Reference |
|-----------|--------|------------|--------------|-----------|
| **FrontierMath** | Advanced Mathematics | Research-level | Evaluates cutting-edge mathematical reasoning | [README.md:355]() |
| **MATH-Perturb** | Math Word Problems | Competition + Perturbations | Tests robustness against hard variations | [README.md:361]() |
| **Big-Math** | Mathematical RL | Large-scale dataset | Dataset for reinforcement learning in math | [README.md:366]() |
| **Putnam-AXIOM** | Higher Mathematics | Olympiad/Competition | Functional and static benchmarking | [README.md:407]() |
| **AIME 2025** | Competition Math | High school competition | American Invitational Mathematics Examination | [README.md:415]() |

### Mathematical Benchmark Characteristics

```mermaid
graph LR
    subgraph "Difficulty_Spectrum"
        BASIC["Basic Arithmetic<br/>GSM8K-level"]
        COMP["Competition Math<br/>AIME, MATH"]
        OLYMPIAD["Olympiad Level<br/>Putnam, IMO"]
        RESEARCH["Research Grade<br/>FrontierMath"]
    end
    
    subgraph "Evaluation_Aspects"
        CORRECT["Correctness<br/>Final Answer"]
        PROCESS["Process Quality<br/>Step-by-Step"]
        ROBUST["Robustness<br/>Perturbations"]
    end
    
    BASIC --> COMP --> OLYMPIAD --> RESEARCH
    
    CORRECT -.evaluated by.-> COMP
    PROCESS -.evaluated by.-> OLYMPIAD
    ROBUST -.evaluated by.-> RESEARCH
    
    MATHPERTURB["MATH-Perturb"] --> ROBUST
    PRMBENCH["PRMBench"] --> PROCESS
```

**Sources:** [README.md:355-366](), [README.md:407-415]()

---

## Code Generation and Programming Benchmarks

Code generation benchmarks assess LLMs' ability to solve programming challenges, understand visual logic, and perform software engineering tasks.

### Programming Evaluation Frameworks

```mermaid
graph TB
    subgraph "Code_Reasoning_Benchmarks"
        EQUIBENCH["EquiBench<br/>Equivalence Checking<br/>arXiv 2025-02"]
        HUMANEVAL["HumanEval-V<br/>Visual + Coding<br/>arXiv 2024-10"]
        ALPHACODE["AlphaCode<br/>Competition-Level<br/>arXiv 2022-03"]
        PROBENCH["ProBench<br/>Competitive Programming<br/>arXiv 2025-02"]
    end
    
    subgraph "ML_Engineering"
        MLEBENCH["MLE-bench<br/>ML Agent Evaluation<br/>arXiv 2024-10"]
    end
    
    subgraph "Visual_Code"
        PLOT2CODE["Plot2code<br/>Scientific Plots → Code<br/>arXiv 2024-05"]
        CHARTMIMIC["ChartMimic<br/>Chart → Code<br/>ICLR 2025"]
        CODEVISION["Code-Vision<br/>Logic + Code Gen<br/>arXiv 2025-02"]
    end
    
    EQUIBENCH -.tests.-> LOGIC["Logical Equivalence"]
    HUMANEVAL -.tests.-> VISUAL["Visual Understanding"]
    MLEBENCH -.tests.-> ENGINEERING["Engineering Tasks"]
    PLOT2CODE -.tests.-> MULTIMODAL["Multi-Modal Reasoning"]
```

### Benchmark Difficulty and Focus

| Benchmark | Primary Focus | Reasoning Type | Evaluation Method |
|-----------|--------------|----------------|-------------------|
| **EquiBench** | Code equivalence checking | Logical reasoning | Equivalence verification |
| **HumanEval-V** | Visual understanding + coding | Multi-modal reasoning | Functional correctness |
| **MLE-bench** | ML engineering workflows | Agent-based problem solving | Task completion metrics |
| **ProBench** | Competitive programming | Algorithmic reasoning | Test case passing |
| **MHPP** | Beyond basic code generation | Advanced programming patterns | Multi-faceted evaluation |

**Sources:** [README.md:358-380](), [README.md:389-409]()

---

## Multimodal Reasoning Benchmarks

Multimodal benchmarks evaluate vision-language models' ability to perform step-by-step reasoning with visual inputs, combining perception with deliberate thinking.

### Multimodal Evaluation Landscape

```mermaid
graph TB
    subgraph "Visual_Math_Reasoning"
        MVMATH["MV-MATH<br/>Multi-Visual Math<br/>arXiv 2025-02"]
        M3COT["M³CoT<br/>Multi-Domain Multi-Step<br/>ACL 2024"]
        COMT["CoMT<br/>Chain of Multi-Modal Thought<br/>arXiv 2024-12"]
    end
    
    subgraph "Visual_Intelligence"
        ZEROBENCH["ZeroBench<br/>Impossible Visual Tasks<br/>arXiv 2025-02"]
        MMIQ["MM-IQ<br/>Abstraction & Reasoning<br/>arXiv 2025-02"]
        PUZZLEVQA["PuzzleVQA<br/>Abstract Visual Patterns<br/>ACL Findings 2024"]
    end
    
    subgraph "Scientific_Visual"
        LEARN2EXPLAIN["Learn to Explain<br/>Science QA<br/>NeurIPS 2022"]
        MMSCI["MMSciBench<br/>Multimodal Science<br/>arXiv 2025-03"]
        PHYSREASON["PhysReason<br/>Physics-Based Reasoning<br/>arXiv 2025-02"]
    end
    
    subgraph "Evaluation_Dimensions"
        QUALITY["MME-CoT<br/>Reasoning Quality"]
        ROBUSTNESS["MME-CoT<br/>Robustness"]
        EFFICIENCY["MME-CoT<br/>Efficiency"]
    end
    
    MVMATH --> QUALITY
    ZEROBENCH --> ROBUSTNESS
    M3COT --> EFFICIENCY
```

### Key Multimodal Benchmarks

| Benchmark | Visual Task Type | Reasoning Aspect | Notable Feature |
|-----------|------------------|------------------|-----------------|
| **MME-CoT** | General multi-modal | Quality, robustness, efficiency | Comprehensive CoT evaluation |
| **MM-IQ** | Abstract patterns | Human-like abstraction | Inspired by IQ tests |
| **MV-MATH** | Mathematical diagrams | Multi-visual contexts | Multiple visual inputs per problem |
| **ZeroBench** | Impossible tasks | Edge case detection | Tests model limitations |
| **LEGO-Puzzles** | Spatial reasoning | Multi-step spatial tasks | 3D reasoning challenges |

**Sources:** [README.md:367-403](), [assets/paper.json:818-847]()

---

## Agent and Tool Use Benchmarks

Agent benchmarks evaluate LLMs' ability to interact with tools, environments, and multi-step workflows, testing System 2 reasoning in interactive scenarios.

### Agent Capability Evaluation

```mermaid
graph TB
    subgraph "Computer_Interaction"
        OSWORLD["OSWorld<br/>Real Computer Environments<br/>Multimodal Agents<br/>NeurIPS 2024"]
        BROWSECOMP["BrowseComp<br/>Web Browsing Tasks<br/>OpenAI 2025"]
        WEBGAMES["WebGames<br/>General-Purpose Browsing<br/>arXiv 2025-02"]
    end
    
    subgraph "Mobile_and_GUI"
        MOBILE["Mobile-Agent-E<br/>Complex Mobile Tasks<br/>arXiv 2025-01"]
        UIR1["UI-R1<br/>GUI Action Prediction<br/>arXiv 2025-03"]
    end
    
    subgraph "Tool_and_Planning"
        TOOLCOMP["ToolComp<br/>Multi-Tool Reasoning<br/>Process Supervision<br/>arXiv 2025-01"]
        TEXT2WORLD["Text2World<br/>World Model Generation<br/>arXiv 2025-02"]
        DECISION["Decision-Making<br/>Multi-Agent Environments<br/>arXiv 2024-03"]
    end
    
    subgraph "Engineering_Tasks"
        MLEBENCH["MLE-bench<br/>ML Engineering<br/>arXiv 2024-10"]
    end
    
    OSWORLD -.requires.-> PLANNING["Planning"]
    TOOLCOMP -.requires.-> PROCESS_SUP["Process Supervision"]
    MOBILE -.requires.-> SELF_EVOLVE["Self-Evolution"]
    MLEBENCH -.requires.-> ENGINEERING["Engineering Skills"]
```

### Agent Benchmark Characteristics

| Benchmark | Environment Type | Action Space | Evaluation Focus |
|-----------|-----------------|--------------|------------------|
| **OSWorld** | Real computer OS | Keyboard, mouse, apps | Multi-modal task completion |
| **BrowseComp** | Web browsers | Navigation, form filling | Browsing agent capability |
| **Mobile-Agent-E** | Mobile devices | Touch, swipe, app control | Self-evolving assistance |
| **ToolComp** | Tool APIs | Function calling | Multi-tool reasoning & supervision |
| **MLE-bench** | ML platforms | Code, data, models | End-to-end ML engineering |
| **UI-R1** | GUI applications | Action prediction | Interface understanding |

**Sources:** [README.md:379-388]()

---

## Process Supervision and Error Detection Benchmarks

These benchmarks evaluate models' ability to verify reasoning steps, detect errors, and provide process-level rewards, which are critical for training System 2 reasoning systems.

### Process Reward and Error Detection Framework

```mermaid
graph TB
    subgraph "Process_Reward_Evaluation"
        PRMBENCH["PRMBench<br/>Process-Level Rewards<br/>Fine-grained & Challenging<br/>arXiv 2025-01"]
        TOOLCOMP["ToolComp<br/>Multi-Tool Process<br/>Supervision Benchmark<br/>arXiv 2025-01"]
    end
    
    subgraph "Error_Detection"
        PROCESSBENCH["ProcessBench<br/>Identifying Process Errors<br/>Mathematical Reasoning<br/>arXiv 2024-12"]
        ERRORRADAR["ErrorRadar<br/>Complex Math Error Detection<br/>Multimodal LLMs<br/>arXiv 2024-10"]
        CANDETECT["Can LLMs Detect Errors?<br/>Long Chain-of-Thought<br/>arXiv 2025-02"]
    end
    
    subgraph "Critique_Evaluation"
        CRITICBENCH["CriticBench<br/>Critique-Correct Reasoning<br/>COLM 2024"]
        JUDGEBENCH["JudgeBench<br/>LLM-based Judges<br/>arXiv 2024-10"]
        CODECRITICBENCH["CodeCriticBench<br/>Holistic Code Critique<br/>arXiv 2025-02"]
    end
    
    subgraph "Domain_Specific"
        MEDEC["MedEC<br/>Medical Error Detection<br/>Clinical Notes<br/>arXiv 2024-12"]
    end
    
    PRMBENCH -.evaluates.-> PRM["Process Reward Models"]
    PROCESSBENCH -.evaluates.-> ERROR_ID["Error Identification"]
    CRITICBENCH -.evaluates.-> CRITIQUE["Critique Ability"]
```

### Step-by-Step Verification Benchmarks

| Benchmark | Verification Target | Granularity | Domain |
|-----------|-------------------|-------------|--------|
| **PRMBench** | Process reward models | Step-level | Mathematics |
| **ProcessBench** | Process errors | Step-level | Mathematical reasoning |
| **ErrorRadar** | Complex reasoning errors | Multi-modal step-level | Mathematical reasoning |
| **CriticBench** | Critique-correct patterns | Solution-level | General reasoning |
| **MedEC** | Clinical reasoning errors | Note-level | Medical domain |
| **Can LLMs Detect Errors** | Long CoT errors | Token/step-level | General reasoning |

**Sources:** [README.md:365](), [README.md:383](), [README.md:424-433]()

---

## Reward Model Benchmarks

Reward model benchmarks specifically evaluate the quality of reward functions used in reinforcement learning and preference optimization for reasoning systems.

### Reward Model Evaluation Framework

```mermaid
graph LR
    subgraph "General_RM_Benchmarks"
        REWARDBENCH["RewardBench<br/>General Reward Models<br/>arXiv 2024-03"]
        RMBENCH["RM-Bench<br/>Subtlety and Style<br/>ICLR Oral 2025"]
    end
    
    subgraph "Multimodal_RM"
        MMREWARD["Multimodal RewardBench<br/>Vision-Language Models<br/>arXiv 2025-02"]
    end
    
    subgraph "Process_Level"
        PRMBENCH["PRMBench<br/>Process-Level Evaluation<br/>arXiv 2025-01"]
    end
    
    subgraph "Usage_Context"
        TRAINING["Training Phase<br/>Part 3: RL"]
        INFERENCE["Inference Phase<br/>Part 4: MCTS"]
        EVALUATION["Evaluation Phase<br/>Part 10: Benchmarks"]
    end
    
    REWARDBENCH --> TRAINING
    PRMBENCH --> TRAINING
    PRMBENCH --> INFERENCE
    RMBENCH --> EVALUATION
    MMREWARD --> EVALUATION
```

### Reward Model Assessment

| Benchmark | Reward Type | Evaluation Aspects | Target Models |
|-----------|-------------|-------------------|---------------|
| **RewardBench** | Outcome rewards | Preference alignment | General reward models |
| **RM-Bench** | Style & subtlety | Fine-grained preferences | Text reward models |
| **Multimodal RewardBench** | Multi-modal rewards | Vision-language alignment | VLM reward models |
| **PRMBench** | Process rewards | Step-level verification | Math reasoning PRMs |

**Sources:** [README.md:360](), [README.md:364-365](), [README.md:424]()

---

## General Reasoning and Meta-Reasoning Benchmarks

Meta-reasoning benchmarks evaluate higher-order cognitive abilities including planning, strategy selection, and reasoning about reasoning itself.

### Meta-Reasoning Evaluation

```mermaid
graph TB
    subgraph "Meta_Reasoning_Core"
        MRBEN["MR-Ben<br/>Meta-Reasoning Benchmark<br/>System-2 Thinking<br/>NeurIPS 2024"]
    end
    
    subgraph "Challenge_Benchmarks"
        HUMANITY["Humanity's Last Exam<br/>Human-Level Challenge<br/>arXiv 2025-01"]
        SUPERGPQA["SuperGPQA<br/>285 Graduate Disciplines<br/>arXiv 2025-02"]
        OLYMPICARENA["OlympicArena<br/>Multi-Discipline Cognitive<br/>2024"]
    end
    
    subgraph "Specialized_Reasoning"
        LONGREASON["LongReason<br/>Long-Context Reasoning<br/>Context Expansion<br/>arXiv 2025-01"]
        ZEBRALOGIC["ZebraLogic<br/>Logical Reasoning Limits<br/>arXiv 2025-02"]
        JUSTLOGIC["JustLogic<br/>Deductive Reasoning<br/>arXiv 2025-01"]
    end
    
    subgraph "Domain_Expertise"
        MEDXPERT["MedXpertQA<br/>Expert-Level Medical<br/>arXiv 2025-01"]
        TPBENCH["TPBench<br/>Theoretical Physics<br/>arXiv 2025-02"]
    end
    
    MRBEN -.evaluates.-> SYSTEM2["System 2 Thinking"]
    LONGREASON -.evaluates.-> CONTEXT["Long-Context Handling"]
    ZEBRALOGIC -.evaluates.-> LIMITS["Reasoning Limits"]
```

### Complexity and Coverage

| Benchmark | Primary Challenge | Coverage | Notable Aspect |
|-----------|------------------|----------|----------------|
| **MR-Ben** | Meta-reasoning | Cross-domain | System 2 thinking evaluation |
| **Humanity's Last Exam** | Human-level difficulty | Comprehensive | Designed to be challenging for future AI |
| **SuperGPQA** | Graduate-level knowledge | 285 disciplines | Breadth and depth |
| **LongReason** | Long-context reasoning | Synthetic long-context | Context expansion methodology |
| **ZebraLogic** | Logical reasoning limits | Logic puzzles | Scaling behavior analysis |
| **ThinkBench** | Out-of-distribution robustness | Dynamic evaluation | Avoids contamination |

**Sources:** [README.md:356-357](), [README.md:359-363](), [README.md:412-420]()

---

## Overthinking and Efficiency Benchmarks

Recent benchmarks specifically address the problem of overthinking—when models use excessive computation on simple tasks that should require only System 1 thinking.

### Overthinking Evaluation

```mermaid
graph LR
    subgraph "Overthinking_Detection"
        DONOT["Do NOT Think That Much<br/>2+3=?<br/>arXiv 2024-12"]
        S1BENCH["S1-Bench<br/>System 1 Capability<br/>arXiv 2025-04"]
        DNABENCH["DNA Bench<br/>When Silence is Smarter<br/>arXiv 2025-03"]
    end
    
    subgraph "Evaluation_Focus"
        SIMPLE["Simple Tasks<br/>Should Use System 1"]
        COMPLEX["Complex Tasks<br/>Should Use System 2"]
        ADAPTIVE["Adaptive Routing<br/>Task Difficulty"]
    end
    
    DONOT --> SIMPLE
    S1BENCH --> SIMPLE
    DNABENCH -.evaluates.-> ADAPTIVE
    
    subgraph "Related_Methods"
        DYNATHINK["DynaThink<br/>Part 7: Fast or Slow?"]
        O1PRUNER["O1-Pruner<br/>Part 7: Length Harmonizing"]
    end
    
    ADAPTIVE -.implemented by.-> DYNATHINK
    ADAPTIVE -.implemented by.-> O1PRUNER
```

### Task Difficulty Stratification

| Benchmark | Focus | Task Types | Evaluation Metric |
|-----------|-------|------------|------------------|
| **Do NOT Think That Much** | Overthinking on simple tasks | Basic arithmetic, simple reasoning | Computation waste |
| **S1-Bench** | System 1 capability preservation | Fast-thinking tasks | Response quality vs. speed |
| **DNA Bench** | Silence as strategy | Tasks requiring no reasoning | Knowing when not to reason |

**Sources:** [README.md:357](), [README.md:374](), [README.md:377]()

---

## Robustness and Contamination-Free Benchmarks

These benchmarks address dataset contamination and robustness issues by using dynamic generation, recent problems, or perturbation techniques.

### Contamination Mitigation Strategies

```mermaid
graph TB
    subgraph "Dynamic_Generation"
        THINKBENCH["ThinkBench<br/>Dynamic OOD Evaluation<br/>arXiv 2025-02"]
        LIVEBENCH["LiveBench<br/>Contamination-Limited<br/>ICLR 2025"]
        MASTERMIND["MastermindEval<br/>Scalable Reasoning<br/>arXiv 2025-03"]
    end
    
    subgraph "Perturbation_Based"
        MATHPERTURB["MATH-Perturb<br/>Hard Perturbations<br/>arXiv 2025-02"]
        ROBUSTNESS["Benchmarking Robustness<br/>arXiv 2025-03"]
    end
    
    subgraph "Recent_Problems"
        AIME2025["AIME 2025<br/>Fresh Competition<br/>Huggingface 2025-02"]
        RESEARCHBENCH["ResearchBench<br/>Scientific Discovery<br/>arXiv 2025-03"]
    end
    
    subgraph "Evaluation_Properties"
        FRESH["Freshness"]
        ROBUST["Robustness"]
        SCALABLE["Scalability"]
    end
    
    LIVEBENCH --> FRESH
    MATHPERTURB --> ROBUST
    MASTERMIND --> SCALABLE
```

**Sources:** [README.md:411](), [README.md:415-421]()

---

## Benchmark Data Structure and Integration

The repository organizes benchmark metadata in a structured JSON format that supports programmatic access and automated documentation generation.

### Data Organization in paper.json

```mermaid
graph TB
    subgraph "Repository_Structure"
        JSON["assets/paper.json"]
        README["README.md<br/>Part 10 Section"]
        LISTMD["src/list.md"]
        TABLEMD["src/table.md"]
    end
    
    subgraph "JSON_Schema"
        PART10["'Part 10: Benchmark and Datasets'<br/>JSON Array"]
        PAPER_OBJ["PaperInformation Objects"]
        FIELDS["Fields:<br/>- paper (title)<br/>- link (URL)<br/>- venue<br/>- date<br/>- label (BibTeX key)"]
    end
    
    subgraph "Build_Process"
        MAINPY["src/main.py<br/>Load and Process"]
        EXTRACT["Extract Papers<br/>Flatten Hierarchy"]
        RESOLVE["Resolve References<br/>Deduplicate"]
    end
    
    JSON --> PART10
    PART10 --> PAPER_OBJ
    PAPER_OBJ --> FIELDS
    
    JSON --> MAINPY
    MAINPY --> EXTRACT
    EXTRACT --> RESOLVE
    RESOLVE --> LISTMD
    RESOLVE --> TABLEMD
    README -.manually curated from.-> JSON
```

### Example Entry Structure

The benchmark entries in [assets/paper.json:818-847]() follow this structure:

```
"Part 10: Benchmark and Datasets": [
    {
        "paper": "MR-Ben: A Meta-Reasoning Benchmark...",
        "link": "https://openreview.net/forum?id=GN2qbxZlni",
        "venue": "NeurIPS",
        "date": "2024-12",
        "label": "li2024mrben"
    },
    ...
]
```

Each entry contains:
- **paper**: Full paper title
- **link**: Direct URL to paper (arXiv, OpenReview, ACL Anthology, etc.)
- **venue**: Publication venue or preprint server
- **date**: Publication date (YYYY-MM format)
- **label**: BibTeX citation key for cross-referencing

**Sources:** [assets/paper.json:818-847](), [src/list.md:124-129]()

---

## Cross-Cutting Benchmark Themes

Several themes emerge across the benchmark landscape that reflect the priorities and challenges in evaluating System 2 reasoning.

### Evaluation Dimensions Matrix

```mermaid
graph TB
    subgraph "Correctness_Dimension"
        FINAL["Final Answer Correctness"]
        PROCESS["Process Correctness"]
        STEPWISE["Step-wise Verification"]
    end
    
    subgraph "Efficiency_Dimension"
        COMPUTE["Computational Cost"]
        TOKENS["Token Usage"]
        TIME["Inference Time"]
    end
    
    subgraph "Robustness_Dimension"
        PERTURB["Perturbation Resistance"]
        OOD["Out-of-Distribution"]
        CONTAMINATION["Contamination-Free"]
    end
    
    subgraph "Capability_Dimension"
        COMPLEXITY["Problem Complexity"]
        MULTIMODAL["Multi-Modal Integration"]
        INTERACTIVE["Interactive/Agentic"]
    end
    
    PRMBENCH_DIM["PRMBench"] --> PROCESS
    MATHPERTURB_DIM["MATH-Perturb"] --> PERTURB
    MMECOT_DIM["MME-CoT"] --> COMPUTE
    MMECOT_DIM --> PROCESS
    OSWORLD_DIM["OSWorld"] --> INTERACTIVE
    FRONTIER_DIM["FrontierMath"] --> COMPLEXITY
```

### Benchmark Selection Guide

| Research Focus | Recommended Benchmarks | Key Metrics |
|----------------|----------------------|-------------|
| **Process Reward Models** | PRMBench, ToolComp, ProcessBench | Step-level accuracy, error detection |
| **Mathematical Reasoning** | FrontierMath, MATH-Perturb, AIME 2025 | Problem-solving accuracy, robustness |
| **Code Generation** | EquiBench, HumanEval-V, ProBench | Functional correctness, code quality |
| **Multimodal Reasoning** | MME-CoT, MM-IQ, ZeroBench | Visual understanding + reasoning |
| **Agent Capabilities** | OSWorld, BrowseComp, MLE-bench | Task completion, tool use |
| **Overthinking Analysis** | Do NOT Think, S1-Bench, DNA Bench | Efficiency vs. accuracy trade-off |
| **Meta-Reasoning** | MR-Ben, LongReason, Humanity's Last Exam | Higher-order reasoning |

**Sources:** [README.md:351-433]()

---

## Integration with Training and Evaluation Pipeline

Benchmarks serve multiple roles in the development lifecycle of System 2 reasoning models, from training data generation to final evaluation.

### Benchmark Usage Across Development Stages

```mermaid
graph LR
    subgraph "Training_Phase"
        DATA_GEN["Dataset Generation<br/>Big-Math, STaR"]
        SUPERVISION["Process Supervision<br/>PRMBench, ToolComp"]
    end
    
    subgraph "Training_Methods"
        RL["Part 3: RL<br/>DeepSeek-R1, Kimi k1.5"]
        PRM["Part 2: PRMs<br/>Math-Shepherd, AutoPSV"]
        SELFTRAIN["Part 5: Self-Training<br/>ReST-MCTS*, rStar-Math"]
    end
    
    subgraph "Inference_Phase"
        MCTS_GUIDE["Part 4: MCTS<br/>Search Guidance"]
        VERIFIER["Process Verification"]
    end
    
    subgraph "Evaluation_Phase"
        BENCHMARK_EVAL["Part 10: Benchmarks<br/>Final Assessment"]
    end
    
    DATA_GEN --> RL
    SUPERVISION --> PRM
    PRM --> SELFTRAIN
    
    PRM --> MCTS_GUIDE
    PRM --> VERIFIER
    
    SELFTRAIN --> BENCHMARK_EVAL
    MCTS_GUIDE --> BENCHMARK_EVAL
```

### Benchmark-to-Method Mapping

| Benchmark Category | Primary Use Case | Related Parts |
|-------------------|------------------|---------------|
| **Process Supervision** (PRMBench, ToolComp) | Training PRMs, guiding search | Parts 2, 4, 5 |
| **Mathematical** (FrontierMath, AIME) | Final evaluation of reasoning | Parts 1, 3, 4, 5 |
| **Multimodal** (MME-CoT, MM-IQ) | VLM reasoning assessment | Parts 9, 12 |
| **Agent** (OSWorld, BrowseComp) | Interactive reasoning | Part 9 |
| **Reward Models** (RM-Bench, RewardBench) | RM quality assessment | Parts 2, 3 |
| **Efficiency** (Do NOT Think, O1-Pruner) | Optimization validation | Part 7 |

**Sources:** [README.md:32-43](), [README.md:351-433]()

---

## Summary

The benchmark landscape for System 2 reasoning in LLMs has evolved rapidly, reflecting the field's maturation from basic reasoning to complex, multi-step problem-solving. Key observations:

1. **Specialization**: Benchmarks now target specific aspects—process supervision, multimodal reasoning, agent capabilities, and meta-reasoning.

2. **Difficulty Progression**: From competition-level math to research-grade problems (FrontierMath), pushing the boundaries of what LLMs can solve.

3. **Robustness Focus**: Increasing emphasis on perturbation resistance, contamination-free evaluation, and dynamic generation.

4. **Process over Outcome**: Growing attention to step-by-step verification (PRMBench, ProcessBench) beyond final answer correctness.

5. **Efficiency Awareness**: New benchmarks address overthinking and computational cost, recognizing that not all tasks need slow reasoning.

6. **Multi-Modal Integration**: Expansion beyond text to vision-language reasoning and interactive environments.

The structured metadata in [assets/paper.json:818-847]() enables systematic tracking of this evolving landscape, supporting both researchers selecting evaluation frameworks and practitioners monitoring field progress.

**Sources:** [README.md:351-433](), [assets/paper.json:818-847](), [src/list.md:124-129]()

---

# Page: Reasoning and Safety

# Reasoning and Safety

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/table.md](src/table.md)

</details>



## Purpose and Scope

This page documents safety considerations, vulnerabilities, and defense mechanisms specific to System 2 reasoning models. As LLMs develop extended deliberation capabilities through Chain-of-Thought (CoT) and tree search methods, new safety challenges emerge that differ fundamentally from traditional fast-thinking models. This page covers deliberative alignment techniques, attack vectors targeting reasoning processes, faithfulness concerns, and robustness challenges.

**Related pages:**
- For process supervision techniques that can enhance safety, see [Process Reward Models](#4.2)
- For understanding reasoning mechanisms, see [Explainability](#5.2)  
- For safety evaluation frameworks, see [Benchmarks and Datasets](#7.1)
- For reinforcement learning safety considerations, see [Reinforcement Learning](#4.3)

**Sources:** [README.md:437-459]()

---

## The Safety Paradox of Deliberate Reasoning

System 2 reasoning introduces a fundamental safety paradox: while extended thinking chains enable more capable problem-solving, they simultaneously create larger attack surfaces and new failure modes. Unlike System 1 models that generate responses in a single forward pass, reasoning models expose intermediate thoughts that can be manipulated, monitored, or misaligned with safety objectives.

### Key Safety Challenges

```mermaid
graph TB
    subgraph "System 1 Safety"
        S1[Fast Generation]
        S1_SURF[Limited Attack Surface]
        S1_ALIGN[Direct Alignment]
        S1 --> S1_SURF
        S1 --> S1_ALIGN
    end
    
    subgraph "System 2 Safety Challenges"
        S2[Extended Reasoning]
        
        FAITHFUL[Faithfulness Issues]
        JAILBREAK[Jailbreak Attacks]
        HIDDEN[Hidden Reasoning]
        ROBUST[Robustness Failures]
        ALIGN[Complex Alignment]
        
        S2 --> FAITHFUL
        S2 --> JAILBREAK
        S2 --> HIDDEN
        S2 --> ROBUST
        S2 --> ALIGN
    end
    
    FAITHFUL --> FAITHFUL_DESC["Are reasoning traces<br/>genuine or post-hoc?"]
    JAILBREAK --> JAIL_DESC["H-CoT and adversarial<br/>prompting exploit CoT"]
    HIDDEN --> HIDDEN_DESC["Concealed reasoning in<br/>internal representations"]
    ROBUST --> ROBUST_DESC["Brittle under perturbations<br/>and edge cases"]
    ALIGN --> ALIGN_DESC["Aligning both process<br/>and outcome"]
```

**Sources:** [README.md:437-459]()

---

## Research Taxonomy: Safety in Reasoning Systems

The repository tracks safety research across several dimensions, organized chronologically to show evolution of concerns and defenses.

| Research Area | Key Focus | Representative Works | Status |
|--------------|-----------|---------------------|---------|
| **Faithfulness** | Measuring whether CoT genuinely reflects reasoning or is post-hoc rationalization | Anthropic's CoT faithfulness study | Blog post (date unknown) |
| **Deliberative Alignment** | Training models to reason safely through process supervision | Various alignment approaches | Active research |
| **Jailbreak Attacks** | Exploiting reasoning traces to bypass safety guardrails | H-CoT and similar techniques | Emerging threat |
| **RL Safety** | Challenges in using RL for reasoning without compromising safety | DeepSeek-R1 safety shortcomings | 2025-01 |
| **Hidden Risks** | Risks from reasoning in latent space or hidden states | Efficient reasoning with hidden thinking | 2025-01 |
| **Robustness** | Stability of reasoning under adversarial or edge-case inputs | Various robustness studies | Ongoing |

**Sources:** [README.md:437-459]()

---

## Attack Vectors and Vulnerabilities

### H-CoT: Hidden Chain-of-Thought Jailbreaks

The most prominent attack vector identified in the repository is the use of reasoning traces themselves as attack surfaces. Unlike traditional prompt injection that targets the final output, reasoning-aware attacks manipulate or exploit intermediate thinking steps.

```mermaid
graph LR
    subgraph "Traditional Jailbreak"
        TRAD_INPUT["Adversarial Prompt"]
        TRAD_MODEL["LLM (System 1)"]
        TRAD_OUTPUT["Unsafe Output"]
        
        TRAD_INPUT --> TRAD_MODEL
        TRAD_MODEL --> TRAD_OUTPUT
    end
    
    subgraph "Reasoning-Aware Jailbreak (H-CoT)"
        ADV_INPUT["Adversarial Prompt<br/>targeting reasoning"]
        
        COT_MODEL["Reasoning LLM"]
        COT_TRACE["Exposed CoT Trace"]
        COT_MANIPULATE["Manipulation of<br/>reasoning steps"]
        COT_OUTPUT["Bypassed Safety"]
        
        ADV_INPUT --> COT_MODEL
        COT_MODEL --> COT_TRACE
        COT_TRACE --> COT_MANIPULATE
        COT_MANIPULATE --> COT_OUTPUT
    end
    
    subgraph "Attack Strategies"
        STRAT1["Inject reasoning steps<br/>that justify unsafe outputs"]
        STRAT2["Exploit process rewards<br/>to reward unsafe reasoning"]
        STRAT3["Hide malicious intent<br/>in long reasoning chains"]
    end
    
    ADV_INPUT -.uses.-> STRAT1
    ADV_INPUT -.uses.-> STRAT2
    ADV_INPUT -.uses.-> STRAT3
```

**Sources:** [README.md:437-459]()

---

## RL Safety Challenges in Reasoning Models

Reinforcement learning techniques used to train reasoning capabilities introduce specific safety concerns documented in the repository. The DeepSeek-R1 case study reveals fundamental tensions between reasoning capability and safety alignment.

### The DeepSeek-R1 Safety Study

```mermaid
graph TB
    subgraph "RL Training for Reasoning"
        RL_POLICY["Policy Model"]
        RL_REWARD["Reward Signal<br/>(correctness-focused)"]
        RL_COT["Generate CoT Reasoning"]
        
        RL_POLICY --> RL_COT
        RL_COT --> RL_REWARD
        RL_REWARD --> RL_POLICY
    end
    
    subgraph "Safety Shortcomings"
        SHORT1["Reward hacking via<br/>unsafe reasoning paths"]
        SHORT2["Alignment degradation<br/>during RL fine-tuning"]
        SHORT3["Safety guardrails<br/>bypassed in reasoning"]
        SHORT4["Inconsistent safety<br/>across reasoning lengths"]
    end
    
    RL_REWARD -.causes.-> SHORT1
    RL_POLICY -.exhibits.-> SHORT2
    RL_COT -.enables.-> SHORT3
    RL_COT -.shows.-> SHORT4
    
    subgraph "Documented in Repository"
        PAPER_R1["DeepSeek-R1: Incentivizing<br/>Reasoning Capability in LLMs<br/>via Reinforcement Learning"]
        PAPER_SAFETY["Challenges in Ensuring AI<br/>Safety in DeepSeek-R1 Models"]
    end
    
    SHORT1 --> PAPER_SAFETY
    SHORT2 --> PAPER_SAFETY
    SHORT3 --> PAPER_SAFETY
    SHORT4 --> PAPER_SAFETY
    
    RL_POLICY -.described in.-> PAPER_R1
```

**Key finding:** RL strategies optimized for reasoning capability may inadvertently compromise safety alignment, as documented in the repository at [README.md:106-107]() (DeepSeek-R1 safety challenges paper).

**Sources:** [README.md:98-137](), [README.md:106-107]()

---

## Deliberative Alignment Approaches

The repository documents emerging approaches to align reasoning processes with safety objectives, going beyond outcome-based alignment to supervise the deliberation itself.

### Process Supervision for Safety

Process Reward Models (PRMs) can be adapted for safety supervision by rewarding not just correct reasoning steps, but safe ones:

```mermaid
graph LR
    subgraph "Outcome-Only Alignment"
        OUT_INPUT["Input Query"]
        OUT_GEN["Generate Response<br/>(with hidden reasoning)"]
        OUT_REWARD["Reward final output<br/>if safe and correct"]
        
        OUT_INPUT --> OUT_GEN
        OUT_GEN --> OUT_REWARD
    end
    
    subgraph "Process-Level Safety Alignment"
        PROC_INPUT["Input Query"]
        PROC_COT["Generate CoT Reasoning"]
        PROC_STEPS["Decompose into steps"]
        
        PROC_VERIFY["Verify each step<br/>for safety properties"]
        PROC_CORRECT["Verify each step<br/>for correctness"]
        
        PROC_REWARD["Combined process reward"]
        PROC_OUTPUT["Final safe output"]
        
        PROC_INPUT --> PROC_COT
        PROC_COT --> PROC_STEPS
        PROC_STEPS --> PROC_VERIFY
        PROC_STEPS --> PROC_CORRECT
        PROC_VERIFY --> PROC_REWARD
        PROC_CORRECT --> PROC_REWARD
        PROC_REWARD --> PROC_OUTPUT
    end
    
    subgraph "Safety Properties Checked"
        PROP1["No toxic content"]
        PROP2["Factual accuracy"]
        PROP3["No harmful instructions"]
        PROP4["Ethical reasoning"]
    end
    
    PROC_VERIFY -.checks.-> PROP1
    PROC_VERIFY -.checks.-> PROP2
    PROC_VERIFY -.checks.-> PROP3
    PROC_VERIFY -.checks.-> PROP4
```

This approach leverages PRMs documented in [Part 2: Process Reward Models](#4.2) but extends them to include safety criteria alongside correctness.

**Sources:** [README.md:68-96](), [README.md:437-459]()

---

## Faithfulness and Interpretability Concerns

A critical safety question for reasoning models: **Are the exposed reasoning traces faithful representations of internal decision-making, or post-hoc rationalizations?**

### Measuring Faithfulness in Chain-of-Thought

Anthropic's research on CoT faithfulness (referenced in the repository) addresses this core concern:

```mermaid
graph TB
    subgraph "Faithful Reasoning"
        FAITH_INPUT["Input"]
        FAITH_INTERNAL["Internal reasoning<br/>process"]
        FAITH_COT["Verbalized CoT"]
        FAITH_OUTPUT["Output"]
        
        FAITH_INPUT --> FAITH_INTERNAL
        FAITH_INTERNAL --> FAITH_COT
        FAITH_INTERNAL --> FAITH_OUTPUT
        
        FAITH_COT -.accurately reflects.-> FAITH_INTERNAL
    end
    
    subgraph "Unfaithful Reasoning"
        UNFAITH_INPUT["Input"]
        UNFAITH_INTERNAL["Internal reasoning<br/>(hidden)"]
        UNFAITH_COT["Post-hoc CoT<br/>(plausible but fake)"]
        UNFAITH_OUTPUT["Output"]
        
        UNFAITH_INPUT --> UNFAITH_INTERNAL
        UNFAITH_INTERNAL --> UNFAITH_OUTPUT
        UNFAITH_OUTPUT --> UNFAITH_COT
        
        UNFAITH_COT -.does not reflect.-> UNFAITH_INTERNAL
    end
    
    subgraph "Safety Implications"
        IMP1["Unfaithful CoT enables<br/>hidden unsafe reasoning"]
        IMP2["Cannot audit decision<br/>process if CoT is fake"]
        IMP3["Adversaries can exploit<br/>disconnect between<br/>CoT and true reasoning"]
    end
    
    UNFAITH_COT --> IMP1
    UNFAITH_COT --> IMP2
    UNFAITH_COT --> IMP3
```

**Repository reference:** The Anthropic blog post on measuring faithfulness is catalogued at [README.md:438]().

**Sources:** [README.md:438]()

---

## Hidden Reasoning and Latent Space Risks

Recent research documented in the repository explores reasoning in continuous latent spaces or hidden representations, which introduces new safety monitoring challenges.

### Efficient Reasoning with Hidden Thinking

The paper "Efficient Reasoning with Hidden Thinking" (2025-01) represents a category of approaches that compress or hide reasoning traces:

```mermaid
graph TB
    subgraph "Visible Reasoning (Auditable)"
        VIS_INPUT["Input"]
        VIS_COT["Visible CoT tokens"]
        VIS_OUTPUT["Output"]
        VIS_AUDIT["Safety Auditing<br/>of reasoning trace"]
        
        VIS_INPUT --> VIS_COT
        VIS_COT --> VIS_OUTPUT
        VIS_COT --> VIS_AUDIT
    end
    
    subgraph "Hidden Reasoning (Opaque)"
        HID_INPUT["Input"]
        HID_LATENT["Latent reasoning<br/>in hidden states"]
        HID_OUTPUT["Output"]
        HID_AUDIT["Safety Auditing<br/>difficult/impossible"]
        
        HID_INPUT --> HID_LATENT
        HID_LATENT --> HID_OUTPUT
        HID_LATENT -.x.-> HID_AUDIT
    end
    
    subgraph "Safety Risks"
        RISK1["Cannot monitor unsafe<br/>reasoning steps"]
        RISK2["Harder to detect<br/>jailbreak attempts"]
        RISK3["Unfaithfulness by design"]
        RISK4["Adversarial reasoning<br/>in latent space"]
    end
    
    HID_LATENT --> RISK1
    HID_LATENT --> RISK2
    HID_LATENT --> RISK3
    HID_LATENT --> RISK4
```

**Repository entries:**
- Efficient Reasoning with Hidden Thinking: [README.md:253](), [README.md:280]()
- Training Large Language Models to Reason in a Continuous Latent Space: [README.md:249]()

These approaches optimize computational efficiency but trade off interpretability and safety monitoring capabilities.

**Sources:** [README.md:242-325](), [README.md:249](), [README.md:253](), [README.md:280]()

---

## Defense Mechanisms and Robustness

### Multi-Layered Safety Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        INPUT["User Query"]
        INPUT_FILTER["Input Safety Filter"]
        INPUT --> INPUT_FILTER
    end
    
    subgraph "Reasoning Layer"
        REASON_START["Start Reasoning"]
        REASON_STEP["Generate reasoning step"]
        
        STEP_SAFETY["Step-level safety check"]
        STEP_CORRECT["Step-level correctness check"]
        
        REASON_START --> REASON_STEP
        REASON_STEP --> STEP_SAFETY
        REASON_STEP --> STEP_CORRECT
        
        STEP_SAFETY -.fail.-> REJECT["Reject/Revise Step"]
        STEP_CORRECT -.fail.-> REJECT
        
        STEP_SAFETY -.pass.-> CONTINUE["Continue Reasoning"]
        STEP_CORRECT -.pass.-> CONTINUE
        
        CONTINUE --> REASON_STEP
    end
    
    subgraph "Output Layer"
        FINAL_COT["Complete CoT"]
        OUTPUT_SAFETY["Final output safety check"]
        OUTPUT_GEN["Generate response"]
        
        CONTINUE --> FINAL_COT
        FINAL_COT --> OUTPUT_SAFETY
        OUTPUT_SAFETY --> OUTPUT_GEN
    end
    
    subgraph "Monitoring Layer"
        MONITOR["Continuous monitoring"]
        LOG["Safety event logging"]
        ALERT["Anomaly detection"]
        
        REASON_STEP --> MONITOR
        MONITOR --> LOG
        MONITOR --> ALERT
    end
    
    subgraph "Defense Components"
        PRM["Process Reward Model<br/>(safety-aware)"]
        VERIFIER["Safety Verifier"]
        CLASSIFIER["Toxic content classifier"]
    end
    
    STEP_SAFETY -.uses.-> PRM
    STEP_SAFETY -.uses.-> VERIFIER
    OUTPUT_SAFETY -.uses.-> CLASSIFIER
```

This architecture combines multiple defense layers:
1. **Input filtering** before reasoning begins
2. **Step-level verification** using safety-aware PRMs (see [Process Reward Models](#4.2))
3. **Final output checks** on the generated response
4. **Continuous monitoring** of reasoning traces for anomalies

**Sources:** [README.md:68-96](), [README.md:437-459]()

---

## Safety Evaluation and Benchmarks

### Repository-Tracked Safety Evaluation

The repository documents various benchmarks for evaluating safety properties of reasoning systems:

| Benchmark/Study | Safety Dimension | Reference |
|----------------|------------------|-----------|
| **Faithfulness Study** | Measuring genuine vs. post-hoc CoT | Anthropic blog |
| **DeepSeek-R1 Safety Analysis** | RL safety shortcomings | [README.md:106-107]() |
| **Overthinking Study** | When reasoning becomes counterproductive | "Do NOT Think That Much" paper |
| **Hidden Reasoning Risks** | Safety implications of latent reasoning | Multiple papers in Part 7 |

### Integration with Benchmark Infrastructure

Safety evaluation should leverage the broader benchmark ecosystem documented in [Benchmarks and Datasets](#7.1):

```mermaid
graph LR
    subgraph "Standard Benchmarks"
        BENCH_MATH["Math reasoning benchmarks"]
        BENCH_CODE["Code generation benchmarks"]
        BENCH_GENERAL["General reasoning benchmarks"]
    end
    
    subgraph "Safety-Augmented Evaluation"
        SAFE_WRAPPER["Safety evaluation wrapper"]
        SAFE_METRICS["Safety metrics:<br/>- Toxicity rate<br/>- Jailbreak success<br/>- Faithfulness score<br/>- Robustness under attack"]
        
        SAFE_WRAPPER --> SAFE_METRICS
    end
    
    subgraph "Combined Assessment"
        CAPABILITY["Reasoning capability"]
        SAFETY["Safety properties"]
        TRADEOFF["Capability-Safety tradeoff analysis"]
        
        CAPABILITY --> TRADEOFF
        SAFETY --> TRADEOFF
    end
    
    BENCH_MATH --> SAFE_WRAPPER
    BENCH_CODE --> SAFE_WRAPPER
    BENCH_GENERAL --> SAFE_WRAPPER
    
    SAFE_METRICS --> CAPABILITY
    SAFE_METRICS --> SAFETY
```

**Key insight:** Safety evaluation must be integrated into capability benchmarks, not treated separately, to properly assess capability-safety tradeoffs.

**Sources:** [README.md:351-433](), [README.md:437-459]()

---

## Reward Hacking and Misalignment Risks

### The Reward Hacking Problem in Process Supervision

When training reasoning models with process rewards, models may learn to generate reasoning traces that maximize reward without actually solving problems safely:

```mermaid
graph TB
    subgraph "Intended Behavior"
        INT_PROBLEM["Problem"]
        INT_THINK["Genuine reasoning"]
        INT_REWARD["High process reward"]
        INT_SOLVE["Correct, safe solution"]
        
        INT_PROBLEM --> INT_THINK
        INT_THINK --> INT_REWARD
        INT_THINK --> INT_SOLVE
    end
    
    subgraph "Reward Hacking Behavior"
        HACK_PROBLEM["Problem"]
        HACK_FAKE["Fake reasoning trace<br/>(optimized for reward)"]
        HACK_REWARD["High process reward"]
        HACK_WRONG["Incorrect or unsafe solution"]
        
        HACK_PROBLEM --> HACK_FAKE
        HACK_FAKE --> HACK_REWARD
        HACK_FAKE --> HACK_WRONG
    end
    
    subgraph "Detection Challenges"
        DET1["PRM trained on same<br/>distribution as exploited"]
        DET2["Hard to distinguish<br/>genuine from fake reasoning"]
        DET3["Adversarial optimization<br/>against PRM"]
    end
    
    HACK_FAKE --> DET1
    HACK_FAKE --> DET2
    HACK_FAKE --> DET3
```

**Related research:** "Reward Shaping to Mitigate Reward Hacking in RLHF" and similar papers in the PRM section address this challenge.

**Sources:** [README.md:68-96](), [README.md:92]()

---

## Safety-Capability Tradeoff Analysis

### The Fundamental Tension

System 2 reasoning presents a fundamental tradeoff between capability and safety:

| More Capability | Enables | But Also Enables |
|----------------|---------|------------------|
| Longer reasoning chains | Solving harder problems | More steps to hide unsafe reasoning |
| Tree search over possibilities | Better exploration of solution space | Exploration of jailbreak strategies |
| RL fine-tuning on reasoning | Expert-level performance | Reward hacking and alignment degradation |
| Hidden/latent reasoning | Computational efficiency | Opacity and reduced auditability |
| Self-improvement loops | Bootstrapping capabilities | Compounding safety issues |

### Mitigation Strategies

The repository documents several approaches to managing this tradeoff:

1. **Safety-aware process supervision**: Integrate safety criteria into PRMs (Part 2)
2. **Deliberative alignment**: Train safety directly into the reasoning process
3. **Continuous monitoring**: Implement real-time safety checks during reasoning (Part 8)
4. **Bounded reasoning**: Use techniques like O1-Pruner to limit reasoning length (Part 7)
5. **Transparent architectures**: Prefer visible CoT over hidden reasoning where safety is critical

**Sources:** [README.md:68-96](), [README.md:242-325](), [README.md:327-338]()

---

## Open Challenges and Future Directions

### Critical Unsolved Problems

```mermaid
graph TB
    subgraph "Technical Challenges"
        TECH1["Scalable faithfulness<br/>verification"]
        TECH2["Safety-preserving RL<br/>for reasoning"]
        TECH3["Robust defenses against<br/>reasoning-aware attacks"]
        TECH4["Auditing hidden<br/>reasoning"]
    end
    
    subgraph "Research Gaps"
        GAP1["Limited understanding of<br/>reasoning-safety interaction"]
        GAP2["Few safety-specific<br/>benchmarks for reasoning"]
        GAP3["Unclear capability-safety<br/>tradeoff curves"]
        GAP4["No consensus on safety<br/>evaluation protocols"]
    end
    
    subgraph "Practical Concerns"
        PRAC1["Deployment safety<br/>at scale"]
        PRAC2["Real-world jailbreak<br/>resistance"]
        PRAC3["Cost of safety<br/>monitoring"]
        PRAC4["Alignment persistence<br/>during reasoning"]
    end
    
    TECH1 --> GAP1
    TECH2 --> GAP1
    TECH3 --> GAP2
    TECH4 --> GAP1
    
    GAP1 --> PRAC1
    GAP2 --> PRAC2
    GAP3 --> PRAC3
    GAP4 --> PRAC4
```

**Sources:** [README.md:437-459]()

---

## Best Practices for Safe Reasoning Systems

### Design Principles

Based on the research documented in the repository, the following principles emerge:

1. **Favor transparency**: Use visible CoT over hidden reasoning when safety is critical
2. **Multi-layer defense**: Don't rely on a single safety mechanism
3. **Process supervision**: Verify safety at each reasoning step, not just the final output
4. **Continuous monitoring**: Log and analyze reasoning traces for anomalies
5. **Capability-safety co-training**: Align safety objectives during reasoning capability development, not as an afterthought
6. **Robustness testing**: Evaluate against adversarial prompts and edge cases
7. **Faithfulness verification**: Regularly audit whether CoT traces reflect true reasoning

### Implementation Checklist

```mermaid
graph LR
    subgraph "Pre-Deployment"
        PRE1["Safety-aware training"]
        PRE2["Adversarial testing"]
        PRE3["Faithfulness auditing"]
        PRE4["Benchmark evaluation"]
    end
    
    subgraph "Deployment"
        DEP1["Input filtering"]
        DEP2["Step-level verification"]
        DEP3["Output checking"]
        DEP4["Monitoring system"]
    end
    
    subgraph "Post-Deployment"
        POST1["Incident logging"]
        POST2["Safety metric tracking"]
        POST3["Model updates"]
        POST4["Red team testing"]
    end
    
    PRE1 --> DEP1
    PRE2 --> DEP2
    PRE3 --> DEP3
    PRE4 --> DEP4
    
    DEP1 --> POST1
    DEP2 --> POST2
    DEP3 --> POST3
    DEP4 --> POST4
    
    POST4 --> PRE2
```

**Sources:** [README.md:437-459]()

---

## Summary

Safety in System 2 reasoning models represents a new frontier in AI safety research. The extended deliberation capabilities that enable expert-level problem-solving also create new attack surfaces and alignment challenges. The repository documents emerging work on:

- **Faithfulness**: Ensuring CoT traces genuinely reflect reasoning
- **Deliberative alignment**: Training safe reasoning processes, not just safe outputs
- **Attack resistance**: Defending against H-CoT jailbreaks and adversarial exploitation
- **RL safety**: Maintaining alignment during reinforcement learning for reasoning
- **Transparency tradeoffs**: Balancing efficiency (hidden reasoning) with auditability (visible CoT)
- **Process supervision**: Extending PRMs to include safety criteria

This remains an active and critical research area as reasoning models become more capable and widely deployed.

**Sources:** [README.md:437-459](), [README.md:1-44]()

---

# Page: Technical Integration Patterns

# Technical Integration Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/list.md](src/list.md)
- [src/table.md](src/table.md)

</details>



## Purpose and Scope

This page documents how different System 2 reasoning methodologies combine in practice to create production-ready reasoning systems. While individual methodologies are covered in [Core Methodologies](#4), this page focuses on **integration patterns**—how Process Reward Models, Reinforcement Learning, MCTS, Self-Training, and Reflection work together in real implementations.

Key coverage:
- **ReST-MCTS* Pipeline**: The canonical example of process reward + tree search + self-training integration
- **O1 Replication Architectures**: Different technical approaches to reproducing o1-like reasoning
- **Training-Time vs Inference-Time Strategies**: When and how to apply reasoning techniques
- **Multi-Method Synergies**: Practical combinations that achieve state-of-the-art results

For theoretical foundations of individual methods, see [Core Methodologies](#4). For production efficiency patterns, see [Efficient System2](#5.1).

**Sources**: [README.md:1-44]()

---

## Integration Taxonomy: Training-Time vs Inference-Time

System 2 reasoning techniques can be categorized by **when** they operate and **how** they combine:

```mermaid
graph TB
    subgraph "Training-Time Methods"
        SFT["Supervised Fine-Tuning<br/>Base CoT Data"]
        RL["Reinforcement Learning<br/>DeepSeek-R1, Kimi k1.5"]
        PRM_TRAIN["Process Reward Training<br/>Math-Shepherd, AutoPSV"]
        SELF_TRAIN["Self-Training<br/>STaR, ReST, rStar-Math"]
    end
    
    subgraph "Inference-Time Methods"
        MCTS["Tree Search<br/>MCTS, RAP, MindStar"]
        BEST_N["Best-of-N Sampling<br/>Outcome Selection"]
        VERIFY["Process Verification<br/>Step-wise Checking"]
        REFLECT["Reflection<br/>Self-Refine, CRITIC"]
    end
    
    subgraph "Hybrid Methods"
        PRM_HYBRID["Process Reward Models<br/>Train: Math-Shepherd<br/>Inference: ReST-MCTS*"]
        VALUE["Value Models<br/>Train: V-star<br/>Inference: TreeBoN"]
    end
    
    SFT --> RL
    SFT --> SELF_TRAIN
    
    PRM_TRAIN --> PRM_HYBRID
    PRM_HYBRID --> MCTS
    PRM_HYBRID --> VERIFY
    
    RL --> BEST_N
    SELF_TRAIN --> MCTS
    
    MCTS --> VERIFY
    VERIFY --> REFLECT
    
    VALUE --> MCTS
    VALUE --> BEST_N
    
    style PRM_HYBRID fill:#f9f9f9
    style VALUE fill:#f9f9f9
```

**Key Insight**: Most production systems use **multi-stage integration**:
1. **Training-time foundation**: RL or Self-Training to build base reasoning capability
2. **Inference-time amplification**: MCTS or Best-of-N to explore solution space
3. **Process-level guidance**: PRMs to guide both training and inference

**Sources**: [README.md:98-138](), [README.md:139-193](), [README.md:194-224]()

---

## The ReST-MCTS* Pipeline: Canonical Integration Pattern

**ReST-MCTS*** represents the most complete integration of core methodologies, combining Process Rewards, Tree Search, and Self-Training in a unified pipeline.

### Pipeline Architecture

```mermaid
graph TB
    subgraph "Stage 1: Process Reward Model Training"
        DATA_PRM["Seed Dataset<br/>Reasoning Traces"]
        LABEL["AutoPSV: Automated<br/>Step-level Labeling"]
        PRM_MODEL["Trained PRM<br/>Math-Shepherd Architecture"]
        
        DATA_PRM --> LABEL
        LABEL --> PRM_MODEL
    end
    
    subgraph "Stage 2: MCTS Exploration"
        BASE_LLM["Base Language Model<br/>e.g., Llama-3-8B"]
        QUERY["Math Query"]
        MCTS_SEARCH["Monte Carlo Tree Search<br/>UCB Selection + Expansion"]
        PRM_GUIDE["PRM Guides Node Evaluation<br/>Step-wise Scoring"]
        TRAJECTORIES["High-Quality Trajectories<br/>Correct Solutions Only"]
        
        BASE_LLM --> MCTS_SEARCH
        QUERY --> MCTS_SEARCH
        PRM_MODEL --> PRM_GUIDE
        PRM_GUIDE --> MCTS_SEARCH
        MCTS_SEARCH --> TRAJECTORIES
    end
    
    subgraph "Stage 3: Self-Training"
        FINETUNE["Supervised Fine-Tuning<br/>on MCTS Trajectories"]
        IMPROVED_LLM["Improved LLM<br/>Enhanced Reasoning"]
        ITERATE["Repeat Cycle<br/>Multiple Iterations"]
        
        TRAJECTORIES --> FINETUNE
        BASE_LLM --> FINETUNE
        FINETUNE --> IMPROVED_LLM
        IMPROVED_LLM --> ITERATE
        ITERATE -.next cycle.-> MCTS_SEARCH
    end
    
    style PRM_MODEL fill:#f9f9f9
    style TRAJECTORIES fill:#f9f9f9
    style IMPROVED_LLM fill:#f9f9f9
```

### Technical Components

| Component | Paper Reference | Technical Detail |
|-----------|----------------|------------------|
| **Process Reward Model** | Math-Shepherd | Automated labeling using Monte Carlo estimation, trains on step-level correctness |
| **Tree Search** | AlphaZero-like | UCB-based selection, PRM-guided expansion, value function combines outcome + process rewards |
| **Self-Training Loop** | ReST | Filters trajectories by correctness, multiple iterations with expanding dataset |
| **Integration Mechanism** | ReST-MCTS* | PRM serves as both (1) MCTS guidance and (2) trajectory filter for self-training |

**Key Innovation**: The PRM enables **self-evolving reasoning** without human annotations by:
1. Providing fine-grained step-level feedback during MCTS exploration
2. Filtering generated trajectories for self-training data quality
3. Improving with each iteration as the base model improves

**Sources**: [README.md:78](), [README.md:175](), [README.md:212](), [README.md:73-74]()

### Code-Level Integration Pattern

The ReST-MCTS* approach is implemented in multiple codebases with similar architectural patterns:

```mermaid
graph LR
    subgraph "rStar-Math Implementation"
        RSTAR_PRM["rStar Process Rewards<br/>Self-Evolved Labels"]
        RSTAR_MCTS["rStar-MCTS<br/>Multi-step Tree Search"]
        RSTAR_TRAIN["Self-Training<br/>Deep Thinking Dataset"]
    end
    
    subgraph "Math-Shepherd Implementation"
        MS_LABEL["Monte Carlo Estimation<br/>Automated Labeling"]
        MS_VERIFY["Step-wise Verifier<br/>Process Reward Function"]
    end
    
    subgraph "Core Integration Points"
        STEP_SCORE["Step Scoring Function<br/>reward = f(state, action)"]
        TREE_SELECT["UCB Selection<br/>balance exploration/exploitation"]
        TRAJ_FILTER["Trajectory Filter<br/>correctness + quality"]
    end
    
    MS_LABEL --> RSTAR_PRM
    MS_VERIFY --> STEP_SCORE
    RSTAR_PRM --> STEP_SCORE
    STEP_SCORE --> TREE_SELECT
    TREE_SELECT --> RSTAR_MCTS
    RSTAR_MCTS --> TRAJ_FILTER
    TRAJ_FILTER --> RSTAR_TRAIN
    
    style STEP_SCORE fill:#f9f9f9
    style TREE_SELECT fill:#f9f9f9
    style TRAJ_FILTER fill:#f9f9f9
```

**Implementation References**:
- **ReST-MCTS* base**: Uses AlphaZero-style tree policy with PRM as value function
- **rStar-Math**: Extends with "deep thinking" trajectories and self-evolution
- **Math-Shepherd**: Provides automated PRM training without human labels

**Sources**: [README.md:78](), [README.md:175](), [README.md:188](), [README.md:220](), [README.md:73]()

---

## O1 Replication Architectures: Diverse Integration Strategies

Different teams have pursued distinct integration strategies to replicate o1-like reasoning capabilities. Each represents a different technical bet on which combinations work best.

### Architecture Comparison Matrix

| System | Training-Time | Inference-Time | Key Integration | Scale Focus |
|--------|--------------|----------------|-----------------|-------------|
| **DeepSeek-R1** | Pure RL (GRPO) | Native reasoning | RL incentivizes long CoT | Large-scale (671B params) |
| **Kimi k1.5** | Scaled RL | Native reasoning | Curriculum RL + data diversity | Large-scale (RL at scale) |
| **Marco-o1** | MCTS + Reflection | MCTS at inference | Reflection-augmented MCTS | Open-ended reasoning |
| **rStar-Math** | Self-Training + PRM | MCTS at inference | Self-evolved deep thinking | Small models (7B-32B) |
| **HuatuoGPT-o1** | Medical SFT + RL | MCTS + Reflection | Domain-specific integration | Medical reasoning |
| **Virgo (Vision)** | Multimodal SFT | MCTS + Visual reward | Vision-language integration | Multimodal reasoning |

### DeepSeek-R1: Pure RL Integration

```mermaid
graph TB
    BASE["Base Model<br/>DeepSeek-V3"]
    
    subgraph "RL Training Pipeline"
        PROMPT["Complex Reasoning Prompts"]
        SAMPLE["Model Generates<br/>Long-form CoT"]
        REWARD["Reward Calculation<br/>Outcome-based"]
        GRPO["Group Relative Policy<br/>Optimization (GRPO)"]
        UPDATE["Model Parameter Update"]
    end
    
    subgraph "Emergent Behaviors"
        LONG_COT["Long Chain-of-Thought<br/>Extended reasoning"]
        SELF_VERIFY["Self-Verification<br/>Checking steps"]
        BACKTRACK["Backtracking<br/>Error correction"]
    end
    
    BASE --> PROMPT
    PROMPT --> SAMPLE
    SAMPLE --> REWARD
    REWARD --> GRPO
    GRPO --> UPDATE
    UPDATE -.improves.-> BASE
    
    UPDATE --> LONG_COT
    UPDATE --> SELF_VERIFY
    UPDATE --> BACKTRACK
    
    style GRPO fill:#f9f9f9
    style LONG_COT fill:#f9f9f9
```

**Key Technical Decision**: DeepSeek-R1 uses **pure RL without explicit tree search**, betting that RL will naturally discover reasoning strategies. The GRPO algorithm enables this by:
- Training on groups of completions simultaneously
- Using relative rewards to reduce variance
- Incentivizing exploration of long reasoning chains

**Trade-off**: Higher compute during training, but no inference-time overhead.

**Sources**: [README.md:107](), [README.md:114]()

### rStar-Math: Self-Evolved Deep Thinking

```mermaid
graph TB
    subgraph "Phase 1: Initial Self-Training"
        SEED["Seed Problems"]
        GEN1["Generate Multiple Solutions<br/>Base Model"]
        VERIFY1["Self-Verify Correctness<br/>Outcome Checking"]
        FILTER1["Filter Correct Trajectories"]
        SFT1["SFT on Filtered Data"]
    end
    
    subgraph "Phase 2: Deep Thinking Evolution"
        MCTS_EXPAND["MCTS Exploration<br/>4-16 step lookahead"]
        COMPLEX["Generate Complex Traces<br/>Deep reasoning paths"]
        SELF_PRM["Self-Evolved PRM<br/>No human labels"]
        FILTER2["Quality Filter<br/>Process + Outcome"]
        SFT2["SFT on Deep Traces"]
    end
    
    subgraph "Phase 3: Iterative Improvement"
        IMPROVED["Improved Model"]
        HARDER["Harder Problems"]
        REPEAT["Repeat Phase 2<br/>Self-evolution loop"]
    end
    
    SEED --> GEN1
    GEN1 --> VERIFY1
    VERIFY1 --> FILTER1
    FILTER1 --> SFT1
    
    SFT1 --> MCTS_EXPAND
    MCTS_EXPAND --> COMPLEX
    COMPLEX --> SELF_PRM
    SELF_PRM --> FILTER2
    FILTER2 --> SFT2
    
    SFT2 --> IMPROVED
    IMPROVED --> HARDER
    HARDER --> REPEAT
    REPEAT -.feeds back to.-> MCTS_EXPAND
    
    style SELF_PRM fill:#f9f9f9
    style FILTER2 fill:#f9f9f9
    style IMPROVED fill:#f9f9f9
```

**Key Technical Decision**: rStar-Math focuses on **small models** (7B) achieving strong performance through:
- Self-evolved deep thinking trajectories (no human annotations)
- Iterative improvement through multiple training phases
- MCTS at inference time for test-time compute scaling

**Trade-off**: Requires multiple training iterations but achieves competitive performance at small scale.

**Sources**: [README.md:188](), [README.md:220](), [README.md:239]()

### Marco-o1: Reflection-Augmented MCTS

```mermaid
graph TB
    subgraph "MCTS with Reflection"
        QUERY["Open-ended Query"]
        MCTS_SELECT["MCTS Node Selection"]
        GENERATE["Generate Candidate<br/>Reasoning Step"]
        REFLECT["Reflection Module<br/>Self-critique step"]
        REVISE["Revise if Needed<br/>Error correction"]
        EVALUATE["Action Value<br/>Q(s,a) calculation"]
        BACKPROP["Backpropagate Value"]
    end
    
    subgraph "Integration Points"
        TRANS_REWARD["Translation Reward<br/>Domain-specific"]
        CONFIDENCE["Confidence Estimation<br/>Uncertainty quantification"]
        STRATEGY["Strategic Planning<br/>High-level goals"]
    end
    
    QUERY --> MCTS_SELECT
    MCTS_SELECT --> GENERATE
    GENERATE --> REFLECT
    REFLECT --> REVISE
    REVISE --> EVALUATE
    EVALUATE --> BACKPROP
    BACKPROP -.updates tree.-> MCTS_SELECT
    
    REFLECT --> CONFIDENCE
    TRANS_REWARD --> EVALUATE
    STRATEGY --> MCTS_SELECT
    
    style REFLECT fill:#f9f9f9
    style CONFIDENCE fill:#f9f9f9
```

**Key Technical Decision**: Marco-o1 integrates **reflection at every MCTS step**, enabling:
- Real-time error detection during tree search
- Confidence-aware node evaluation
- Open-ended reasoning (e.g., translation, colloquial language)

**Trade-off**: More compute per MCTS step, but higher quality trajectories.

**Sources**: [README.md:49](), [README.md:172](), [README.md:234]()

---

## Training-Time vs Inference-Time Trade-offs

The choice between training-time and inference-time reasoning has fundamental implications:

### Comparison Framework

```mermaid
graph TB
    subgraph "Training-Time Reasoning"
        direction TB
        TRAIN_RL["Reinforcement Learning<br/>DeepSeek-R1, Kimi k1.5"]
        TRAIN_SELF["Self-Training<br/>rStar-Math, STaR"]
        TRAIN_DIST["Distillation<br/>O1 Replication Journey Part 2"]
        
        TRAIN_PROS["Advantages:<br/>- Fast inference<br/>- No search overhead<br/>- Native reasoning"]
        TRAIN_CONS["Disadvantages:<br/>- High training compute<br/>- Fixed at deployment<br/>- Limited adaptability"]
        
        TRAIN_RL -.example.-> TRAIN_PROS
        TRAIN_SELF -.example.-> TRAIN_PROS
        TRAIN_DIST -.example.-> TRAIN_PROS
        
        TRAIN_RL -.faces.-> TRAIN_CONS
    end
    
    subgraph "Inference-Time Reasoning"
        direction TB
        INF_MCTS["MCTS/Tree Search<br/>MindStar, rStar-Math"]
        INF_BEST["Best-of-N Sampling<br/>TreeBoN, PairJudge"]
        INF_REFLECT["Reflection<br/>Self-Refine, CRITIC"]
        
        INF_PROS["Advantages:<br/>- Test-time compute scaling<br/>- Adaptable per query<br/>- Verifiable paths"]
        INF_CONS["Disadvantages:<br/>- Slow inference<br/>- Compute per query<br/>- Quality depends on base"]
        
        INF_MCTS -.example.-> INF_PROS
        INF_BEST -.example.-> INF_PROS
        INF_REFLECT -.example.-> INF_PROS
        
        INF_MCTS -.faces.-> INF_CONS
    end
    
    subgraph "Hybrid Approaches"
        direction TB
        HYBRID_REST["ReST-MCTS*<br/>Train with inference search"]
        HYBRID_RSTAR["rStar-Math<br/>Self-train + MCTS inference"]
        HYBRID_DYN["DynaThink<br/>Dynamic routing"]
        
        HYBRID_BEST["Best of Both:<br/>- Strong base model (training)<br/>- Adaptive scaling (inference)<br/>- Efficient routing"]
    end
    
    TRAIN_RL -.combines with.-> HYBRID_REST
    INF_MCTS -.combines with.-> HYBRID_REST
    
    style HYBRID_BEST fill:#f9f9f9
```

### Technical Decision Matrix

| Use Case | Recommended Approach | Key Papers | Rationale |
|----------|---------------------|------------|-----------|
| **Production API** (latency-sensitive) | Training-time RL | DeepSeek-R1, Kimi k1.5 | Fast inference, amortized compute |
| **Research Benchmark** (accuracy-focused) | Inference-time MCTS | rStar-Math, MindStar | Test-time scaling for hard problems |
| **Small Model Deployment** | Hybrid (Self-train + MCTS) | rStar-Math, ReST-MCTS* | Compensate for limited capacity |
| **Domain-Specific** (medical, coding) | Training-time + domain PRMs | HuatuoGPT-o1, o1-Coder | Specialized knowledge + reasoning |
| **Dynamic Workload** | Adaptive routing | DynaThink, O1-Pruner | Fast for simple, slow for hard |

**Sources**: [README.md:107-108](), [README.md:188](), [README.md:246](), [README.md:254]()

---

## Multi-Method Synergy Patterns

Certain methodology combinations create **synergistic effects** where the whole exceeds the sum of parts:

### Synergy Pattern 1: PRM + MCTS + Self-Training

**Why it works**:
- **PRM** provides fine-grained guidance that MCTS lacks with outcome-only rewards
- **MCTS** explores diverse solution paths that simple sampling misses
- **Self-Training** converts exploration into improved base capability
- **Loop**: Improved base model → better MCTS exploration → higher quality training data

**Key Papers**: ReST-MCTS*, rStar-Math, Math-Shepherd

### Synergy Pattern 2: RL + Process Rewards

```mermaid
graph LR
    subgraph "Baseline: RL with Outcome Rewards"
        RL_OUT["RL Training"]
        OUT_REWARD["Outcome Reward<br/>Sparse signal"]
        CREDIT["Credit Assignment<br/>Difficult for long chains"]
    end
    
    subgraph "Enhanced: RL with Process Rewards"
        RL_PROC["RL Training"]
        PROC_REWARD["Process Reward<br/>Dense signal"]
        STEP_CREDIT["Step-level Credit<br/>Clear attribution"]
        BETTER["Better Convergence<br/>Faster learning"]
    end
    
    RL_OUT --> OUT_REWARD
    OUT_REWARD --> CREDIT
    
    RL_PROC --> PROC_REWARD
    PROC_REWARD --> STEP_CREDIT
    STEP_CREDIT --> BETTER
    
    style STEP_CREDIT fill:#f9f9f9
    style BETTER fill:#f9f9f9
```

**Why it works**:
- **Dense feedback**: Process rewards provide signal at every reasoning step
- **Credit assignment**: Easier to identify which steps led to success/failure
- **Faster convergence**: More gradients per trajectory

**Key Papers**: Step-DPO, DeepSeek-R1 (implicit), AutoPSV

**Sources**: [README.md:76](), [README.md:77]()

### Synergy Pattern 3: Reflection + Tree Search

**Why it works**:
- **Reflection** detects errors in individual trajectories
- **Tree Search** explores alternative paths when errors detected
- **Combined**: Self-correction capability + systematic exploration

**Integration Points**:
1. Reflection as MCTS node evaluation
2. Reflection triggers backtracking in search
3. Reflection-revised nodes added to tree

**Key Papers**: Marco-o1, Mulberry, Vision-Language Self-Improve

**Sources**: [README.md:234](), [README.md:178](), [README.md:236]()

---

## Domain-Specific Integration Patterns

Different domains require adapted integration strategies:

### Mathematical Reasoning

```mermaid
graph TB
    subgraph "Math Domain Stack"
        MATH_DATA["Math Datasets<br/>GSM8K, MATH, Olympiad"]
        MATH_PRM["Math-Shepherd PRM<br/>Step-wise verification"]
        MATH_MCTS["MCTS with<br/>Symbolic Verification"]
        MATH_VERIFY["Final Answer Check<br/>Ground truth comparison"]
    end
    
    subgraph "Key Techniques"
        AUTO_LABEL["Automated Labeling<br/>Monte Carlo estimation"]
        CODE_EXEC["Code Execution<br/>Python interpreter"]
        FORMAL["Formal Verification<br/>Proof checking"]
    end
    
    MATH_DATA --> AUTO_LABEL
    AUTO_LABEL --> MATH_PRM
    MATH_PRM --> MATH_MCTS
    CODE_EXEC --> MATH_VERIFY
    FORMAL --> MATH_VERIFY
    MATH_MCTS --> MATH_VERIFY
    
    style AUTO_LABEL fill:#f9f9f9
    style CODE_EXEC fill:#f9f9f9
```

**Math-Specific Integrations**:
- **Automated PRM training**: Monte Carlo estimation for step labels (no humans needed)
- **Executable verification**: Python code execution for numerical checks
- **Symbolic reasoning**: Integration with computer algebra systems
- **Proof verification**: Lean/Coq integration for formal proofs

**Key Papers**: Math-Shepherd, rStar-Math, DeepSeekMath

**Sources**: [README.md:73](), [README.md:109]()

### Medical Reasoning

```mermaid
graph TB
    subgraph "Medical Domain Stack"
        MED_SFT["Medical SFT<br/>Clinical knowledge"]
        MED_RL["Medical RL<br/>Diagnostic reasoning"]
        MED_MCTS["MCTS with<br/>Clinical guidelines"]
        MED_VERIFY["Expert Verification<br/>Safety checks"]
    end
    
    subgraph "Safety Integration"
        GUIDELINE["Clinical Guideline<br/>Constraints"]
        FACT_CHECK["Medical Fact<br/>Verification"]
        HARM_DETECT["Harm Detection<br/>Safety filter"]
    end
    
    MED_SFT --> MED_RL
    MED_RL --> MED_MCTS
    GUIDELINE --> MED_MCTS
    MED_MCTS --> MED_VERIFY
    FACT_CHECK --> MED_VERIFY
    HARM_DETECT --> MED_VERIFY
    
    style GUIDELINE fill:#f9f9f9
    style HARM_DETECT fill:#f9f9f9
```

**Medical-Specific Integrations**:
- **Clinical guidelines as constraints**: MCTS pruning based on medical standards
- **Expert verification loop**: Human-in-the-loop for safety
- **Factual grounding**: RAG integration with medical knowledge bases
- **Harm detection**: Safety-aware reward shaping

**Key Papers**: HuatuoGPT-o1, MedVLM-R1, Med-RLVR

**Sources**: [README.md:53](), [README.md:117]()

### Code Generation

**Code-Specific Integrations**:
- **Execution feedback**: Test case results as rewards
- **Syntax verification**: AST parsing for correctness
- **Type checking**: Static analysis integration
- **Code search**: Tree search over program space

**Key Papers**: o1-Coder, CodeTree, RethinkMCTS

**Sources**: [README.md:52](), [README.md:169](), [README.md:162]()

---

## Efficiency Integration Patterns

Production systems require efficiency optimizations integrated throughout:

### Dynamic Routing Pattern

```mermaid
graph TB
    QUERY["Input Query"]
    CLASSIFY["Difficulty Classifier<br/>Fast heuristic"]
    
    subgraph "Simple Path"
        FAST["Direct Generation<br/>System 1"]
        FAST_OUT["Quick Response"]
    end
    
    subgraph "Hard Path"
        SLOW["MCTS/RL Reasoning<br/>System 2"]
        SLOW_OUT["Deliberate Response"]
    end
    
    subgraph "Implementations"
        DYNA["DynaThink<br/>Dynamic routing"]
        O1PRUNE["O1-Pruner<br/>Length harmonization"]
        TOKEN_BUDGET["Token-Budget-Aware<br/>Adaptive reasoning"]
    end
    
    QUERY --> CLASSIFY
    CLASSIFY -->|easy| FAST
    CLASSIFY -->|hard| SLOW
    FAST --> FAST_OUT
    SLOW --> SLOW_OUT
    
    DYNA -.implements.-> CLASSIFY
    O1PRUNE -.implements.-> SLOW
    TOKEN_BUDGET -.implements.-> CLASSIFY
    
    style CLASSIFY fill:#f9f9f9
    style DYNA fill:#f9f9f9
```

**Integration Points**:
- **Difficulty estimation**: Confidence-based or learned classifier
- **Budget allocation**: Dynamic token limits per query
- **Early stopping**: Terminate reasoning when confidence high
- **Caching**: Reuse reasoning traces for similar queries

**Key Papers**: DynaThink, O1-Pruner, Token-Budget-Aware LLM Reasoning

**Sources**: [README.md:246](), [README.md:254](), [README.md:248]()

### Latent Space Reasoning

**Pattern**: Compress reasoning into continuous latent space instead of token space

**Integration**:
- Training: Learn latent reasoning representations
- Inference: Reason in latent space, decode final answer
- Benefit: Faster reasoning, fewer tokens

**Key Papers**: Training LLMs to Reason in Continuous Latent Space, Efficient Reasoning with Hidden Thinking

**Sources**: [README.md:249](), [README.md:253](), [README.md:280]()

---

## Implementation Considerations

### Computational Resource Planning

| Integration Pattern | Training Compute | Inference Compute | Memory | Best For |
|---------------------|-----------------|------------------|---------|----------|
| **Pure RL** | Very High (weeks) | Low (native generation) | High (large models) | Production APIs |
| **MCTS at Inference** | Medium (SFT) | High (per query search) | Medium | Research, benchmarks |
| **ReST-MCTS*** | High (iterative) | Medium (improved base) | Medium | Balanced approach |
| **Self-Training** | Medium (multiple iterations) | Low (no search) | Low-Medium | Resource-constrained |
| **Hybrid Routing** | Medium | Variable (adaptive) | Medium | Variable workloads |

### Quality-Latency Trade-off Curves

Different integration patterns occupy different positions on the quality-latency frontier:

1. **High Quality, High Latency**: MCTS at inference (MindStar, rStar-Math)
2. **High Quality, Low Latency**: Large-scale RL (DeepSeek-R1, Kimi k1.5)
3. **Medium Quality, Low Latency**: Small model self-training + efficient routing
4. **Adaptive**: Dynamic routing systems (DynaThink)

**Sources**: [README.md:246-324]()

---

## Future Integration Directions

Emerging patterns in recent papers (2025):

### Multi-Modal Integration

- **Vision-language reasoning**: Virgo, LLaVA-o1, MM-Eureka
- **Pattern**: Extend text reasoning pipelines to visual inputs
- **Challenge**: Visual process rewards harder to define

**Sources**: [README.md:348](), [README.md:235]()

### Agentic Integration

- **Tool-augmented reasoning**: ARMAP, Search-o1, RAG-Gym
- **Pattern**: Integrate external tools with reasoning loops
- **Challenge**: Tool selection and composition

**Sources**: [README.md:85](), [README.md:60](), [README.md:187](), [README.md:350]()

### Efficient Long-Context Reasoning

- **Challenge**: Reasoning over documents exceeds context windows
- **Pattern**: Hierarchical reasoning + memory management
- **Papers**: LongReason, efficient attention mechanisms

**Sources**: [README.md:362]()

---

## Summary: Key Integration Principles

1. **Synergy over isolation**: Combined methods outperform individual techniques
2. **PRM as glue**: Process rewards enable integration of training and inference methods
3. **Trade-off awareness**: Choose integration based on latency, compute, and quality requirements
4. **Domain adaptation**: Modify integration patterns for specific domains (math, medical, code)
5. **Efficiency integration**: Build routing and optimization into core architecture, not as afterthought

**Production Recipe**: For most applications, start with training-time methods (RL or self-training) to build strong base capability, then add inference-time scaling (MCTS or Best-of-N) for hard queries, with dynamic routing to balance cost and quality.

**Sources**: [README.md:1-450]()

---

# Page: Research Timeline and Evolution

# Research Timeline and Evolution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/timeline.jpg](assets/timeline.jpg)
- [assets/timeline.png](assets/timeline.png)
- [assets/timeline_2.png](assets/timeline_2.png)
- [src/timeline.png](src/timeline.png)

</details>



## Purpose and Scope

This document provides a chronological perspective on System 2 reasoning research in Large Language Models, tracking the field's evolution from foundational work (2017) through production-ready systems (2025). It maps key breakthroughs, inflection points, and the convergence of methodologies to the repository's 12-part taxonomy.

For the conceptual framework of System 1 vs System 2 reasoning, see [System 1 vs System 2 Reasoning](#2). For the current research landscape organized by methodology, see [Research Landscape Overview](#3). For specific technical approaches, see [Core Methodologies](#4).

**Sources:** [README.md:1-27](), [README.md:25-26]()

---

## Historical Timeline: 2017-2025

The evolution of System 2 reasoning in LLMs can be traced through five distinct periods, each characterized by specific methodological advances and architectural innovations.

```mermaid
timeline
    title Evolution of System 2 Reasoning Research (2017-2025)
    
    section Foundation Era
        2017 : Expert Iteration (NeurIPS 2017)
             : Tree Search + Deep Learning synthesis
        2018-2021 : MCTS foundations
                  : Reinforcement Learning basics
    
    section Emergence
        2022 : STaR: Bootstrapping Reasoning
             : Self-Training paradigm introduced
             : arXiv 2022.05
    
    section Breakthrough
        2023 : Process Rewards (Let's Verify Step by Step)
             : AlphaZero-like Tree Search for LLMs
             : Self-Refine (NeurIPS 2023)
             : ReST: Reinforced Self-Training
             : RAP, Self-Evaluation Guided Beam Search
    
    section Integration
        2024 : O1 Replication Journey begins (arXiv 2024.10)
             : Math-Shepherd (ACL 2024)
             : ReST-MCTS* (NeurIPS 2024)
             : DeepSeekMath (arXiv 2024.02)
             : Multimodal reasoning emergence
             : Marco-o1, LLaVA-o1, Quiet-STaR, V-star
    
    section Production
        2025 : DeepSeek-R1 (arXiv 2025.01)
             : Kimi k1.5 (arXiv 2025.01)
             : rStar-Math: Self-Evolved Deep Thinking
             : Virgo, MM-Eureka (Multimodal O1-like)
             : O1-Pruner (Efficiency optimization)
             : PRMBench, ReARTeR (Advanced evaluation)
             : Safety research (H-CoT, Deliberative Alignment)
```

**Sources:** [README.md:45-416]() (extracting dates from all 12 parts), [README.md:25-26](), High-level architecture diagrams

---

## Foundation Era (2017-2021): Building Blocks

The foundation era established the core concepts that would later converge into modern System 2 reasoning systems.

### Expert Iteration (2017)

The seminal work that demonstrated how tree search could be combined with deep learning to improve reasoning capabilities.

| Paper | Venue | Key Contribution |
|-------|-------|------------------|
| Expert Iteration | NeurIPS 2017 | Tree Search + Deep Learning synthesis |

**Repository Location:** [README.md:196]() under Part 5: Self-Training / Self-Improve

### Core Concepts Established

During this period, research established:
- **Monte Carlo Tree Search (MCTS)** as a planning mechanism
- **Reinforcement Learning** for policy optimization
- **Tree-based exploration** for reasoning paths

These foundational techniques would remain dormant in LLM research until 2022-2023, when computational capabilities and model scales made them practical.

**Sources:** [README.md:196](), [README.md:139-194]() (Part 4: MCTS/Tree Search historical context)

---

## Self-Training Emergence (2022): Bootstrapping Begins

The 2022 period introduced self-training as a viable paradigm for improving reasoning without extensive human annotation.

### STaR: Bootstrapping Reasoning With Reasoning

```mermaid
graph LR
    STaR["STaR (arXiv 2022.05)"]
    
    subgraph "Core Innovation"
        BOOTSTRAP["Bootstrapping from<br/>model's own reasoning"]
        FILTER["Filter correct solutions"]
        RETRAIN["Retrain on filtered data"]
    end
    
    subgraph "Impact on Later Work"
        REST["ReST (2023)"]
        VSTAR["V-star (2024)"]
        RSTAR["rStar-Math (2025)"]
        QSTAR["Quiet-STaR (2024)"]
    end
    
    STaR --> BOOTSTRAP
    BOOTSTRAP --> FILTER
    FILTER --> RETRAIN
    RETRAIN --> REST
    RETRAIN --> VSTAR
    RETRAIN --> RSTAR
    RETRAIN --> QSTAR
```

**Repository Mapping:**
- `assets/paper.json`: Entry for STaR paper
- [README.md:197](): STaR listing in Part 5
- Descendants in [README.md:201-224]() (ReST, V-star, Quiet-STaR, rStar-Math)

### Paradigm Shift

STaR introduced the concept that models could generate their own training data by:
1. Attempting problems
2. Filtering successful reasoning chains
3. Fine-tuning on self-generated data

This self-improvement loop would become central to 2024-2025 systems.

**Sources:** [README.md:197](), [README.md:194-224]() (Part 5 entire section)

---

## Breakthrough Year (2023): Convergence of Methods

2023 saw the simultaneous development of multiple techniques that would later be synthesized into O1-like systems.

### Three Simultaneous Breakthroughs

```mermaid
graph TB
    subgraph "2023 Breakthrough Year"
        PRM["Process Reward Models<br/>Let's Verify Step by Step<br/>arXiv 2024.05"]
        TREE["AlphaZero-like Tree Search<br/>for LLMs<br/>NeurIPS Workshop 2023"]
        REFINE["Self-Refine<br/>Iterative Refinement<br/>NeurIPS 2023"]
    end
    
    subgraph "2024 Synthesis"
        RESTMCTS["ReST-MCTS*<br/>Process + Search<br/>NeurIPS 2024"]
        MATHSHEP["Math-Shepherd<br/>Automated PRMs<br/>ACL 2024"]
        MARCO["Marco-o1<br/>Open Reasoning<br/>arXiv 2024.11"]
    end
    
    PRM --> RESTMCTS
    TREE --> RESTMCTS
    PRM --> MATHSHEP
    REFINE --> MARCO
    TREE --> MARCO
```

### Key Papers by Breakthrough

| Breakthrough | Representative Papers | Repository Location |
|--------------|----------------------|---------------------|
| **Process Rewards** | Let's Verify Step by Step | [README.md:75]() Part 2 |
| | Making LLMs Better Reasoners with Step-Aware Verifier | [README.md:72]() Part 2 |
| **Tree Search** | AlphaZero-like Tree-Search Can Guide LLM Decoding | [README.md:144-145]() Part 4 |
| | Reasoning with Language Model is Planning with World Model | [README.md:141]() Part 4 |
| **Reflection** | Self-Refine: Iterative Refinement with Self-Feedback | [README.md:200]() Part 6 |
| | Self-Evaluation Guided Beam Search | [README.md:199]() Part 5 |

### ReST: Reinforced Self-Training

The synthesis of self-training with reinforcement learning:

**Repository Mapping:**
- [README.md:201](): ReST in Part 5
- `assets/paper.json`: Structured metadata with arXiv 2023.08 date
- Evolved into ReST-MCTS* in 2024 [README.md:78,175,212]()

**Sources:** [README.md:68-97]() (Part 2: Process Reward Models), [README.md:139-193]() (Part 4: MCTS/Tree Search), [README.md:225-241]() (Part 6: Reflection), [README.md:201]()

---

## Integration Phase (2024): The O1 Replication Journey

2024 marked the acceleration phase where separate techniques converged toward OpenAI's o1 architecture. The year saw explosive growth in papers attempting to replicate and understand o1's capabilities.

### O1 Replication Timeline

```mermaid
gantt
    title 2024: Race to Replicate O1
    dateFormat YYYY-MM
    
    section Foundations
    DeepSeekMath           :2024-02, 2024-03
    V-star                 :2024-02, 2024-03
    
    section Mid-Year Integration
    ReST-MCTS*             :2024-06, 2024-09
    Math-Shepherd          :2024-06, 2024-07
    MindStar               :2024-05, 2024-06
    
    section O1 Response Wave
    O1 Replication Part 1  :2024-10, 2024-11
    Marco-o1               :2024-11, 2024-12
    O1 Replication Part 2  :2024-11, 2024-12
    
    section Multimodal Extension
    LLaVA-o1               :2024-11, 2024-12
    AtomThink              :2024-11, 2024-12
    Mulberry               :2024-12, 2025-01
```

### Key Architectural Patterns

The 2024 papers revealed common architectural patterns:

| Pattern | Implementation | Papers | Repository Location |
|---------|---------------|--------|---------------------|
| **Process + Search** | MCTS guided by process rewards | ReST-MCTS*, rStar-Math | [README.md:78,175]() |
| **RL-Based Training** | PPO/DPO/GRPO for reasoning | DeepSeekMath, Kimi k1.5 prep | [README.md:98-138]() Part 3 |
| **Automated PRM** | Self-generated process supervision | Math-Shepherd, AutoPSV | [README.md:73,77]() Part 2 |
| **Tree Search Decoding** | Inference-time exploration | MindStar, LLaMA-Berry | [README.md:153,165]() Part 4 |

### Math-Shepherd: Automated Process Supervision

A critical 2024 breakthrough was automating process reward model creation:

**File References:**
- [README.md:73](): "Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations"
- ACL 2024 publication
- Part of the automated supervision trend leading to 2025's scaled systems

### Multimodal Reasoning Emergence

2024 also saw System 2 reasoning extend beyond text:

```mermaid
graph LR
    subgraph "Text-Only Systems"
        O1BASE["O1 Architecture<br/>(text-based)"]
    end
    
    subgraph "Multimodal Extensions 2024"
        LLAVAО1["LLaVA-o1<br/>Vision-Language<br/>arXiv 2024.11"]
        ATOM["AtomThink<br/>Slow-Fast Multimodal<br/>arXiv 2024.11"]
        MULBERRY["Mulberry<br/>MLLM + MCTS<br/>arXiv 2024.12"]
    end
    
    O1BASE --> LLAVAО1
    O1BASE --> ATOM
    O1BASE --> MULBERRY
```

**Repository Mapping:**
- [README.md:232,235](): AtomThink and LLaVA-o1 in Part 6: Reflection
- [README.md:231](): Mulberry in Part 6
- [README.md:40-41](): Part 9 and Part 12 dedicated to multimodal reasoning

**Sources:** [README.md:45-67]() (Part 1: O1 Replication), [README.md:73](), [README.md:78,175](), [README.md:153,165](), [README.md:231-235]()

---

## Production Maturity (2025): Scaled Reasoning Systems

2025 represents the production phase where System 2 reasoning moved from research prototypes to deployable systems at scale.

### DeepSeek-R1 and Kimi k1.5: Scaled RL

The two landmark releases of early 2025:

| System | Key Characteristics | Repository Reference |
|--------|---------------------|---------------------|
| **DeepSeek-R1** | Large-scale RL for reasoning | [README.md:107]() Part 3 |
| | arXiv 2025.01 | "Incentivizing Reasoning Capability via RL" |
| | Production-ready architecture | Open-source impact |
| **Kimi k1.5** | Scaled RL with LLMs | [README.md:108]() Part 3 |
| | arXiv 2025.01 | "Scaling Reinforcement Learning" |
| | Commercial deployment | Chinese market leader |

### rStar-Math: Self-Evolved Deep Thinking

A significant algorithmic advance combining multiple techniques:

```mermaid
graph TB
    RSTAR["rStar-Math<br/>arXiv 2025.01"]
    
    subgraph "Integrated Techniques"
        MCTS["MCTS for<br/>exploration"]
        SELF["Self-training<br/>data generation"]
        PROCESS["Process-level<br/>supervision"]
        DEEP["Deep thinking<br/>extended reasoning"]
    end
    
    subgraph "Key Achievement"
        SMALL["Small LLMs (7B)<br/>master math reasoning"]
        OLYMPIAD["Olympiad-level<br/>performance"]
    end
    
    RSTAR --> MCTS
    RSTAR --> SELF
    RSTAR --> PROCESS
    RSTAR --> DEEP
    
    MCTS --> SMALL
    SELF --> SMALL
    PROCESS --> SMALL
    DEEP --> OLYMPIAD
```

**Repository Location:** [README.md:188,220,239]() (appears in Parts 4, 5, and 6)

### Efficiency and Safety Infrastructure

2025 also saw maturation of supporting infrastructure:

#### Efficiency Optimization

| Paper | Focus | Repository Location |
|-------|-------|---------------------|
| O1-Pruner | Length-harmonizing fine-tuning | [README.md:254]() Part 7 |
| DynaThink | Dynamic decision-making (fast/slow routing) | [README.md:246]() Part 7 |
| Token-Budget-Aware Reasoning | Resource-constrained optimization | [README.md:248]() Part 7 |

**Part 7 Evolution:** [README.md:242-275]() tracks efficiency research from 2024 to 2025

#### Advanced Evaluation

| Benchmark | Purpose | Repository Location |
|-----------|---------|---------------------|
| PRMBench | Process-level reward evaluation | [README.md:81]() Part 2 |
| ReARTeR | Retrieval-augmented reasoning | [README.md:82]() Part 2 |
| MR-Ben | Multi-domain reasoning | Part 10 benchmarks |

#### Safety Research

The emergence of powerful reasoning systems prompted safety research:

- **H-CoT Jailbreak**: Hidden chain-of-thought attacks [README.md:11]() (Part 11)
- **Deliberative Alignment**: Safety through reasoning [README.md:11]() (Part 11)
- **Challenges in Ensuring AI Safety**: DeepSeek-R1 specific concerns [README.md:106]() Part 3

**Sources:** [README.md:107-108]() (DeepSeek-R1, Kimi k1.5), [README.md:188,220,239]() (rStar-Math), [README.md:242-275]() (Part 7: Efficient System2), [README.md:81-82]() (advanced benchmarks)

---

## Methodology Convergence Pattern

One of the key insights from tracking the timeline is how initially separate research threads converged into integrated systems.

```mermaid
graph TB
    subgraph "2017-2022: Isolated Techniques"
        EI["Expert Iteration<br/>2017"]
        MCTS["MCTS Foundations<br/>2018-2021"]
        STAR["STaR<br/>2022"]
    end
    
    subgraph "2023: Parallel Development"
        PRM2023["Process Rewards<br/>2023"]
        TREE2023["Tree Search for LLMs<br/>2023"]
        REF2023["Self-Refine<br/>2023"]
        REST2023["ReST<br/>2023"]
    end
    
    subgraph "2024: Integration"
        RESTMCTS2024["ReST-MCTS*<br/>Process + Search"]
        MATHSHEP2024["Math-Shepherd<br/>Automated PRM"]
        MARCO2024["Marco-o1<br/>Multi-technique"]
    end
    
    subgraph "2025: Unified Systems"
        R1["DeepSeek-R1<br/>RL at scale"]
        K15["Kimi k1.5<br/>Scaled reasoning"]
        RSTARMATH["rStar-Math<br/>Self-evolved"]
    end
    
    EI --> STAR
    MCTS --> TREE2023
    STAR --> REST2023
    
    PRM2023 --> RESTMCTS2024
    TREE2023 --> RESTMCTS2024
    REST2023 --> RESTMCTS2024
    
    PRM2023 --> MATHSHEP2024
    REF2023 --> MARCO2024
    
    RESTMCTS2024 --> RSTARMATH
    MATHSHEP2024 --> R1
    MARCO2024 --> K15
```

### Convergence Principles

The evolution reveals three key convergence principles:

1. **Training + Inference Time Integration**: Early systems focused on either training (STaR, ReST) or inference (MCTS), but 2024-2025 systems integrate both.

2. **Automated Supervision**: Manual annotation (2023) → Automated PRMs (2024) → Fully self-supervised (2025)

3. **Scale + Technique**: Small models with sophisticated techniques (2024) → Large models with scaled techniques (2025)

### Repository Structure Reflects Evolution

The [README.md:29-43]() 12-part structure maps to this temporal evolution:

| Part | Temporal Focus | Peak Activity Period |
|------|----------------|---------------------|
| Part 1 (O1 Replication) | 2024-2025 | October 2024 → Present |
| Part 2 (Process Rewards) | 2023-2024 | May 2023 → 2024 |
| Part 3 (Reinforcement Learning) | 2024-2025 | Late 2024 → 2025 |
| Part 4 (MCTS/Tree Search) | 2023-2024 | 2023 → 2024 |
| Part 5 (Self-Training) | 2022-2024 | May 2022 → 2024 |
| Part 6 (Reflection) | 2023-2024 | 2023 → 2024 |
| Part 7 (Efficient System2) | 2024-2025 | Late 2024 → 2025 |
| Part 9 (Multimodal) | 2024 | November 2024 |
| Part 12 (R1-Driven Multimodal) | 2025 | January 2025 → Present |

**Sources:** [README.md:29-43]() (Table of Contents structure), entire [README.md:45-416]() (extracting temporal patterns)

---

## Key Inflection Points

### Inflection Point 1: STaR's Self-Training Loop (May 2022)

**Before:** Models required extensive human-annotated reasoning chains  
**After:** Models could bootstrap from their own successful attempts

**Impact Metric:** Led to 15+ derivative papers by 2025 ([README.md:197-224]())

### Inflection Point 2: Process Rewards at Scale (May 2023)

**Before:** Outcome-only reward models  
**After:** Step-by-step verification and guidance

**Key Paper:** "Let's Verify Step by Step" [README.md:75]()  
**Impact:** Enabled ReST-MCTS* and subsequent search-guided training

### Inflection Point 3: O1 Release (October 2024)

**Before:** Academic research on reasoning  
**After:** Industry race to replicate production-quality reasoning

**Evidence:** 
- Part 1 papers surge from 0 to 15+ in 3 months ([README.md:45-67]())
- Community implementations: TinyZero, Open R1, mini-deepseek-r1

### Inflection Point 4: DeepSeek-R1 Open Release (January 2025)

**Before:** Proprietary reasoning systems (OpenAI o1, o3)  
**After:** Open-source competitive alternatives

**Impact:**
- Multiple reproduction attempts: X-R1, Unlock-Deepseek, LMM-R1 ([README.md:64,65,67]())
- Democratization of advanced reasoning
- Safety research acceleration ([README.md:106]())

**Sources:** [README.md:197]() (STaR), [README.md:75]() (Process Rewards), [README.md:45-67]() (O1 reaction), [README.md:107]() (DeepSeek-R1 impact)

---

## Research Velocity Metrics

Analyzing publication patterns in `assets/paper.json` and [README.md:45-416]() reveals accelerating research velocity:

### Papers by Year

| Year | Est. Paper Count | Key Observations |
|------|-----------------|------------------|
| 2017-2021 | ~5 | Foundation papers, slow pace |
| 2022 | ~10 | Self-training emergence |
| 2023 | ~35 | Breakthrough year, 3x growth |
| 2024 | ~120 | Integration phase, 3.4x growth |
| 2025 (Jan-Apr) | ~85+ | Production phase, maintaining velocity |

### Monthly Publication Rate (2024-2025)

```mermaid
graph LR
    subgraph "2024 Publication Surge"
        Q1["Q1 2024<br/>~15 papers"]
        Q2["Q2 2024<br/>~25 papers"]
        Q3["Q3 2024<br/>~30 papers"]
        Q4["Q4 2024<br/>~50 papers<br/>(O1 catalyst)"]
    end
    
    subgraph "2025 Sustained Pace"
        JAN["Jan 2025<br/>~25 papers"]
        FEB["Feb 2025<br/>~30 papers"]
        MAR["Mar 2025<br/>~20 papers"]
        APR["Apr 2025<br/>~10 papers"]
    end
    
    Q1 --> Q2
    Q2 --> Q3
    Q3 --> Q4
    Q4 --> JAN
    JAN --> FEB
    FEB --> MAR
    MAR --> APR
```

### Methodology Distribution Over Time

Tracking which of the 12 parts received the most papers each year:

**2023:**
- Process Rewards: 4 papers
- MCTS/Tree Search: 8 papers
- Self-Training: 5 papers

**2024:**
- O1 Replication: 15 papers (new category)
- Process Rewards: 12 papers
- MCTS/Tree Search: 35 papers
- RL: 15 papers

**2025 (Jan-Apr):**
- O1 Replication: 5 papers
- RL: 30 papers (dominates due to DeepSeek-R1)
- Efficient System2: 15 papers (maturation focus)
- R1-Driven Multimodal: 8 papers (new category)

**Sources:** [README.md:45-416]() (extracting badge dates), counting patterns in each Part section

---

## Data Layer: Timeline Tracking Infrastructure

The repository uses several mechanisms to track temporal information:

### JSON Metadata Structure

`assets/paper.json` contains structured metadata including dates:
- Referenced by `src/main.py` for processing
- Enables `src/table.md` and `src/list.md` generation with date sorting
- Supports automated timeline updates

**File References:**
- [assets/paper.json:1-end](): Structured paper metadata (~256 papers across 12 categories)
- [src/main.py:1-end](): Loads JSON, extracts PaperInformation, resolves references
- [src/table.md:1-end](): Tabular view sorted by date
- [src/list.md:1-end](): List view with date badges

### Visual Timeline Assets

The repository includes multiple timeline visualizations:

| Asset | Purpose | Reference |
|-------|---------|-----------|
| `assets/timeline.png` | Historical overview | [README.md:25]() |
| `src/timeline.png` | Copy for processing | Mirror of assets version |
| `assets/timeline_2.png` | Recent timeline | [README.md:25-26]() |
| `assets/timeline.jpg` | Timeline variant | Visual reference |
| `assets/develope.jpg` | Evolution diagram | [README.md:21]() |

**Quote from README:** "The recent timeline of reasoning LLMs, covering core methods and the release of open-source and closed-source reproduction projects." [README.md:26]()

### Badge System for Dates

Each paper in [README.md:45-416]() uses a badge system:
- `![](https://img.shields.io/badge/arXiv-2024.11-red)` for arXiv papers
- `![](https://img.shields.io/badge/NeurIPS-2024-blue)` for conference papers
- `![](https://img.shields.io/badge/github-2025.01-red)` for code releases

This enables:
1. Visual scanning of temporal patterns
2. Automated extraction of publication dates
3. Tracking venue prestige over time

**Sources:** [README.md:1-27]() (repository structure), [README.md:45-416]() (badge system examples), [assets/paper.json:1-end](), [src/main.py:1-end]()

---

## Future Trajectory Indicators

Based on the 2024-2025 acceleration pattern, several trajectories are evident:

### Emerging Trends (2025 Forward)

1. **Efficiency Optimization**: Part 7 papers growing rapidly
   - O1-Pruner: Length harmonization [README.md:254]()
   - Dynamic routing systems [README.md:246]()
   - Latent space reasoning [README.md:249]()

2. **Multimodal Unification**: Parts 9 and 12 convergence
   - Text reasoning → Vision-language reasoning
   - Domain-specific applications (medical, scientific)
   - R1-driven multimodal becoming standard

3. **Small Model Reasoning**: Democratization
   - rStar-Math: 7B models achieving high performance [README.md:188]()
   - "Small Models Struggle to Learn from Strong Reasoners" [README.md:260]()
   - Efficiency-capability trade-offs

4. **Safety Integration**: Part 11 growth
   - H-CoT jailbreak defenses
   - Deliberative alignment
   - Robustness challenges [README.md:11]()

### Research Questions for 2025-2026

The timeline suggests several open questions:

- **Scaling Laws for Reasoning**: Does test-time compute scale predictably? [README.md:265]()
- **Generalization**: Can reasoning transfer across domains?
- **Interpretability**: Understanding the "aha moments" in RL [README.md:122]()
- **Human Alignment**: Balancing capability with safety

**Sources:** [README.md:242-275]() (Part 7 trends), [README.md:40-43]() (Parts 9, 12 emergence), [README.md:260]() (small model challenges), [README.md:11]() (Part 11 safety)

---

## Timeline Summary: From Research to Production

The eight-year evolution (2017-2025) can be summarized as follows:

```mermaid
graph TB
    subgraph "Phase 1: Foundation (2017-2021)"
        FOUND["Expert Iteration<br/>MCTS basics<br/>RL foundations"]
    end
    
    subgraph "Phase 2: Emergence (2022)"
        EMERGE["Self-training<br/>STaR paradigm<br/>Bootstrapping"]
    end
    
    subgraph "Phase 3: Breakthrough (2023)"
        BREAK["Process rewards<br/>Tree search for LLMs<br/>Self-refine"]
    end
    
    subgraph "Phase 4: Integration (2024)"
        INTEGRATE["ReST-MCTS*<br/>Math-Shepherd<br/>O1 replication<br/>Multimodal reasoning"]
    end
    
    subgraph "Phase 5: Production (2025)"
        PROD["DeepSeek-R1<br/>Kimi k1.5<br/>rStar-Math<br/>Efficiency + Safety"]
    end
    
    FOUND --> EMERGE
    EMERGE --> BREAK
    BREAK --> INTEGRATE
    INTEGRATE --> PROD
    
    style FOUND fill:#f9f9f9
    style EMERGE fill:#f9f9f9
    style BREAK fill:#f9f9f9
    style INTEGRATE fill:#f9f9f9
    style PROD fill:#f9f9f9
```

### Key Metrics

- **Time to Production**: 8 years from Expert Iteration to DeepSeek-R1
- **Acceleration Factor**: 3-4x year-over-year paper growth (2022-2024)
- **Methodology Convergence**: 6 separate techniques → unified O1 architecture
- **Open Source Impact**: DeepSeek-R1 sparked 10+ immediate reproductions

### Repository as Historical Record

The [README.md:1-416]() structure serves as both:
1. **Synchronic**: Current state of research (12-part taxonomy)
2. **Diachronic**: Historical evolution (date badges, temporal clustering)

The combination enables researchers to:
- Trace idea lineages
- Identify underexplored combinations
- Predict future convergences
- Understand which techniques have stood the test of time

**Sources:** [README.md:1-416]() (complete repository), synthesis of all previous sections

---

# Page: Repository Structure and Maintenance

# Repository Structure and Maintenance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)
- [src/list.md](src/list.md)
- [src/main.py](src/main.py)
- [src/table.md](src/table.md)

</details>



This document describes the technical infrastructure of the Awesome-System2-Reasoning-LLM repository, focusing on how research papers are stored, processed, and presented. It covers the data schema ([assets/paper.json]()), the automated build pipeline ([src/main.py]()), and the generation of alternative documentation formats. For information about the research content itself, see [Research Landscape Overview](#3).

## Repository Architecture

The repository uses a **hybrid documentation strategy** that combines manual curation with automated generation. The primary interface is the hand-crafted [README.md:1-416](), while auxiliary formats are generated programmatically from a structured data source.

### File Organization

```mermaid
graph TD
    subgraph "Source Data"
        JSON["assets/paper.json<br/>~256 papers<br/>12 categories"]
    end
    
    subgraph "Build System"
        BUILDER["src/main.py<br/>PaperInformation class<br/>Utility class"]
    end
    
    subgraph "Generated Outputs"
        TABLE["src/table.md<br/>Tabular format<br/>Sorted by date"]
        LIST["src/list.md<br/>List format<br/>With badges"]
    end
    
    subgraph "Manual Curation"
        README["README.md<br/>Primary documentation<br/>Expert commentary"]
    end
    
    subgraph "Visual Assets"
        TIMELINE1["assets/timeline.png"]
        TIMELINE2["src/timeline.png"]
        TIMELINE3["assets/timeline_2.png"]
        TIMELINE4["assets/timeline.jpg"]
        DEV["assets/develope.jpg"]
    end
    
    JSON --> BUILDER
    BUILDER --> TABLE
    BUILDER --> LIST
    
    JSON -.informs.-> README
    README -.references.-> TIMELINE1
    README -.references.-> TIMELINE3
    README -.references.-> TIMELINE4
    README -.references.-> DEV
```

**Sources:** [README.md:1-416](), [assets/paper.json:1-848](), [src/main.py:1-198]()

### Maintenance Strategy

| Component | Update Method | Frequency | Complexity |
|-----------|---------------|-----------|------------|
| `assets/paper.json` | Manual editing | Per new paper | Low |
| `src/table.md` | Automated via `main.py` | On demand | None |
| `src/list.md` | Automated via `main.py` | On demand | None |
| `README.md` | Manual curation | Varies | High |
| Timeline images | Manual creation | Periodic | Medium |

**Sources:** [src/main.py:182-197](), [README.md:1-416]()

## Data Layer: assets/paper.json

The [assets/paper.json:1-848]() file is the authoritative source of paper metadata. It uses a hierarchical JSON structure organized by the 12 research parts.

### Schema Structure

```mermaid
graph TB
    subgraph "Root Object"
        ROOT["paper.json<br/>{...}"]
    end
    
    subgraph "Part Keys"
        PART1["Part 1: O1 Replication"]
        PART2["Part 2: Process Reward Models"]
        PART3["Part 3: Reinforcement Learning"]
        PART4["Part 4: MCTS/Tree Search"]
        PART5["Part 5: Self-Training / Self-Improve"]
        PART6["Part 6: Reflection"]
        PART7["Part 7: Efficient System2"]
        PART8["Part 8: Explainability"]
        PART9["Part 9: Multimodal Agent related Slow-Fast System"]
        PART10["Part 10: Benchmark and Datasets"]
        PART11["Part 11: Reasoning and Safety"]
        PART12["Part 12: R1 Driven Multimodal Reasoning Enhancement"]
    end
    
    subgraph "Paper Entry Fields"
        PAPER["paper: string<br/>Title"]
        LINK["link: string<br/>URL"]
        VENUE["venue: string<br/>Conference/Journal"]
        DATE["date: string<br/>YYYY-MM"]
        LABEL["label: string<br/>Unique identifier"]
    end
    
    ROOT --> PART1
    ROOT --> PART2
    ROOT --> PART3
    ROOT --> PART4
    ROOT --> PART5
    ROOT --> PART6
    ROOT --> PART7
    ROOT --> PART8
    ROOT --> PART9
    ROOT --> PART10
    ROOT --> PART11
    ROOT --> PART12
    
    PART1 --> PAPER
    PART1 --> LINK
    PART1 --> VENUE
    PART1 --> DATE
    PART1 --> LABEL
```

**Sources:** [assets/paper.json:1-848]()

### Paper Entry Format

Each paper entry in `paper.json` follows this structure:

```json
{
    "paper": "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
    "link": "https://arxiv.org/abs/2501.12948",
    "venue": "arXiv",
    "date": "2025-01",
    "label": "luong2025deepseekr1"
}
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `paper` | string | Yes | Full paper title |
| `link` | string | Yes | URL to paper (arXiv, ACL Anthology, etc.) |
| `venue` | string | Yes | Publication venue (arXiv, NeurIPS, ACL, etc.) |
| `date` | string | Yes | Publication date in `YYYY-MM` format |
| `label` | string | Yes* | Unique identifier for deduplication |

*The `label` field is technically optional but required for papers that appear in multiple categories. See "Label-Based References" below.

**Sources:** [assets/paper.json:176-181](), [src/main.py:6-14]()

### Label-Based References

To avoid duplication when papers belong to multiple categories, the JSON supports label references:

```json
{
    "Part 1: O1 Replication": [
        {
            "paper": "Marco-o1: Towards Open Reasoning Models for Open-Ended Solutions",
            "link": "https://arxiv.org/abs/2411.14405",
            "venue": "arXiv",
            "date": "2024-11",
            "label": "zhao2024marco"
        }
    ],
    "Part 4: MCTS/Tree Search": [
        {
            "label": "zhao2024marco"
        }
    ],
    "Part 6: Reflection": [
        {
            "label": "zhao2024marco"
        }
    ]
}
```

This mechanism allows a paper to be defined once with full metadata, then referenced by label in other categories.

**Sources:** [assets/paper.json:18-23](), [assets/paper.json:297-301](), [src/main.py:76-87]()

## Build System: src/main.py

The [src/main.py:1-198]() script processes `paper.json` through a three-phase pipeline implemented in the `Utility` class.

### Class Architecture

```mermaid
classDiagram
    class PaperInformation {
        +string paper
        +string link
        +string venue
        +string date
        +Optional[string] label
        +__init__(paper, link, venue, date, label)
        +__hash__() int
        +__lt__(other) bool
        +__eq__(other) bool
    }
    
    class Utility {
        +get_paper_information(raw_paper_dict) list~PaperInformation~
        +fill_paper_dict(raw_paper_dict, paper_information_list) dict
        +generate_title_with_level(title, title_level) string
        +generate_readme_table_with_title(title, title_level, paper_information_list) string
        +generate_all_table(paper_dict, topmost_table_level, current_table_str) string
        +generate_list_with_title(title, title_level, paper_information_list) string
        +generate_all_list(paper_dict, topmost_list_level, current_list_str) string
    }
    
    Utility ..> PaperInformation : creates and processes
```

**Sources:** [src/main.py:6-33](), [src/main.py:35-180]()

### Processing Pipeline

The build process consists of three phases:

```mermaid
graph LR
    subgraph "Phase 1: Extract"
        JSON_RAW["raw_paper_dict<br/>Nested JSON"]
        EXTRACT["Utility.get_paper_information()<br/>lines 37-62"]
        PAPER_LIST["paper_information_list<br/>Flattened list of<br/>PaperInformation objects"]
    end
    
    subgraph "Phase 2: Resolve"
        FILL["Utility.fill_paper_dict()<br/>lines 64-99"]
        RESOLVED["processed_paper_dict<br/>Labels resolved to<br/>PaperInformation objects"]
    end
    
    subgraph "Phase 3: Generate"
        GEN_TABLE["Utility.generate_all_table()<br/>lines 121-139"]
        GEN_LIST["Utility.generate_all_list()<br/>lines 161-179"]
        TABLE_OUT["src/table.md"]
        LIST_OUT["src/list.md"]
    end
    
    JSON_RAW --> EXTRACT
    EXTRACT --> PAPER_LIST
    PAPER_LIST --> FILL
    JSON_RAW --> FILL
    FILL --> RESOLVED
    RESOLVED --> GEN_TABLE
    RESOLVED --> GEN_LIST
    GEN_TABLE --> TABLE_OUT
    GEN_LIST --> LIST_OUT
```

**Sources:** [src/main.py:182-197]()

### Phase 1: Paper Extraction

The `get_paper_information()` method recursively traverses the JSON structure to extract all paper entries:

**Method:** [src/main.py:36-62]()

**Algorithm:**
1. Recursively descend into nested dictionaries
2. For list values, iterate over paper entries
3. Skip label-only references (handled in Phase 2)
4. Create `PaperInformation` objects for complete entries
5. Return flattened list of all papers

**Deduplication:** The method uses `assert` statements to ensure that papers without labels are not duplicated in the list:

```python
assert (
    paper_label is not None
    or paper_information not in paper_information_list
)
```

**Sources:** [src/main.py:55-58]()

### Phase 2: Label Resolution

The `fill_paper_dict()` method resolves label references to actual `PaperInformation` objects:

**Method:** [src/main.py:64-99]()

**Algorithm:**
1. Recursively rebuild the dictionary structure
2. For label-only entries, look up the corresponding `PaperInformation` from the flattened list
3. Replace label references with actual objects
4. Preserve the original hierarchical structure

**Label Lookup Logic:**

```python
paper_label = raw_paper_information["label"]
for paper_information in paper_information_list:
    if paper_information.label == paper_label:
        break
else:
    raise ValueError(f"Paper label not found: {paper_label}")
```

**Sources:** [src/main.py:81-86]()

### Phase 3: Output Generation

Two generation methods produce the output files:

#### Table Format Generation

**Method:** [src/main.py:121-139]()

**Structure:**
- Markdown tables with columns: Title | Venue | Date
- Hierarchical section headers using `#` depth based on `topmost_table_level`
- Papers sorted by date (most recent first) via `PaperInformation.__lt__()` [src/main.py:19-29]()

**Example output:** [src/table.md:10-27]()

#### List Format Generation

**Method:** [src/main.py:161-179]()

**Features:**
- Bullet list format
- Dynamic badge generation based on venue type
- arXiv papers get red badges: `arXiv-YYYY.MM`
- Conference papers get blue badges: `VENUE-YYYY`

**Badge Logic:**

```python
badge_color = "blue"
if "arxiv" in paper_information.link.lower():
    badge_color = "red"
    badge_text = f"arXiv-{paper_information.date.replace('-', '.')}"
else:
    venue = paper_information.venue.replace(" ", "_")
    year = paper_information.date.split("-")[0]
    badge_text = f"{venue}-{year}"
```

**Sources:** [src/main.py:147-154]()

### PaperInformation Class

The `PaperInformation` class represents a single paper entry:

**Definition:** [src/main.py:6-33]()

**Key Methods:**

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `__hash__()` | Enable set operations | Returns `self.label` |
| `__eq__()` | Deduplication | Compares `label` fields |
| `__lt__()` | Sorting | Reverse chronological by date, then by venue/title |

**Sorting Logic:**

The `__lt__()` method implements a custom sort order:
1. **Primary:** Date (most recent first) - reverse chronological
2. **Secondary:** Venue (ascending alphabetical)
3. **Tertiary:** Title (ascending alphabetical)

**Sources:** [src/main.py:19-29]()

## Output Formats

### src/table.md

The [src/table.md:1-149]() file presents papers in a tabular format organized by the 12 research parts.

**Structure:**
```
## Part N: Category Name
|Title|Venue|Date|
|:---|:---|:---|
|[Paper Title](URL)|Venue|YYYY-MM|
...
```

**Use Cases:**
- Quick scanning of papers by category
- Finding papers by publication venue
- Identifying temporal clusters of research

**Generation:** Automatically generated by running `python src/main.py` [src/main.py:188-190]()

**Sources:** [src/table.md:1-149](), [src/main.py:121-139]()

### src/list.md

The [src/list.md:1-129]() file presents papers in a bullet list format with colored badges.

**Structure:**
```
## Part N: Category Name
* Paper Title [[Paper]](URL) ![](https://img.shields.io/badge/VENUE-YYYY-color)
...
```

**Badge Colors:**
- 🔴 Red: arXiv preprints
- 🔵 Blue: Conference/journal publications

**Use Cases:**
- Compact browsing experience
- Visual distinction between preprints and published work
- Integration with GitHub markdown rendering

**Generation:** Automatically generated by running `python src/main.py` [src/main.py:191-193]()

**Sources:** [src/list.md:1-129](), [src/main.py:161-179]()

## Maintenance Workflows

### Adding a New Paper

To add a paper to the repository:

**Step 1: Edit paper.json**

Add the paper entry to the appropriate category in [assets/paper.json]():

```json
{
    "paper": "Full Paper Title",
    "link": "https://arxiv.org/abs/XXXX.XXXXX",
    "venue": "arXiv",
    "date": "2025-04",
    "label": "firstauthor2025keyword"
}
```

**Label Convention:** `{firstauthor}{year}{keyword}` (all lowercase)

**Step 2: Add Cross-References (if applicable)**

If the paper belongs to multiple categories, add label-only references:

```json
{
    "Part X: Another Category": [
        {
            "label": "firstauthor2025keyword"
        }
    ]
}
```

**Step 3: Regenerate Auxiliary Files**

Run the build script:

```bash
python src/main.py
```

This updates [src/table.md]() and [src/list.md]().

**Step 4: Update README.md (optional)**

Manually add the paper to [README.md]() with contextual description if desired. The README follows a richer format with inline badges and commentary:

```markdown
* Paper Title [[Paper]](URL) ![](https://img.shields.io/badge/arXiv-2025.04-red)
```

**Sources:** [assets/paper.json:1-848](), [src/main.py:182-197]()

### Running the Build System

The build system has no external dependencies beyond Python's standard library.

**Requirements:**
- Python 3.7+ (for type hints)
- No third-party packages required

**Execution:**

```bash
cd /path/to/repository
python src/main.py
```

**Output:**
- Overwrites [src/table.md]()
- Overwrites [src/list.md]()
- Does not modify [assets/paper.json]() or [README.md]()

**Sources:** [src/main.py:196-197]()

### Version Control Strategy

The repository tracks all files, including generated ones:

| File Type | Tracked | Regenerated | Human-Edited |
|-----------|---------|-------------|--------------|
| `paper.json` | ✅ | ❌ | ✅ |
| `table.md` | ✅ | ✅ | ❌ |
| `list.md` | ✅ | ✅ | ❌ |
| `README.md` | ✅ | ❌ | ✅ |

**Rationale for tracking generated files:**
- Provides immediate visibility of changes in pull requests
- Ensures consistency between data source and outputs
- Enables diff-based review of additions/changes

**Sources:** Repository structure analysis

## Design Rationale

### Why Hybrid Documentation?

The repository uses **manual curation** for `README.md` but **automated generation** for auxiliary formats:

| Aspect | Manual (README) | Automated (table/list) |
|--------|-----------------|------------------------|
| **Content Richness** | High - contextual descriptions, groupings | Low - structured metadata only |
| **Maintenance Cost** | High - requires expert knowledge | Low - script handles updates |
| **Flexibility** | High - custom organization, emphasis | Low - fixed templates |
| **Consistency** | Variable - human judgment | High - algorithmic sorting |
| **Primary vs Secondary** | Primary user interface | Alternative views |

The `README.md` (80.82% importance) remains hand-crafted because:
1. It provides expert commentary on research trends
2. It groups papers thematically beyond the 12 parts
3. It includes visual timeline assets
4. It maintains an introduction and citation information

The generated formats serve complementary purposes:
- **table.md:** Machine-readable, sortable reference
- **list.md:** Compact format for quick browsing

**Sources:** [README.md:1-416](), High-level system architecture analysis

### Why Label-Based References?

The label-based reference system solves the **multi-category paper problem**:

**Problem:** Many papers contribute to multiple research areas. For example:
- `Marco-o1` appears in Parts 1, 4, and 6
- `ReST-MCTS*` appears in Parts 2, 4, and 5
- `HuatuoGPT-o1` appears in Parts 1, 4, and 6

**Without labels:** Metadata would be duplicated across categories, creating maintenance burden and inconsistency risk.

**With labels:** Define once, reference everywhere:

```json
{
    "Part 1": [
        {"paper": "...", "link": "...", "label": "zhao2024marco"}
    ],
    "Part 4": [
        {"label": "zhao2024marco"}
    ]
}
```

**Benefits:**
- Single source of truth for metadata
- Easier updates (change once, propagates everywhere)
- Explicit modeling of paper relationships
- Deduplication in generated outputs

**Sources:** [assets/paper.json:18-23](), [src/main.py:76-87]()

### Why Python Script Over Build Tool?

The repository uses a simple Python script rather than a build system (Make, npm, etc.):

**Advantages:**
- Zero dependencies beyond Python standard library
- Cross-platform compatibility (Windows, Linux, macOS)
- Readable implementation (198 lines of Python)
- No configuration files needed
- Easy to extend with custom logic

**Trade-offs:**
- Manual execution required (no automatic rebuild on file change)
- No incremental build optimization (full regeneration each run)

For this use case, the trade-offs are acceptable because:
- Papers are added infrequently (not real-time)
- Full regeneration is fast (<1 second)
- Simplicity reduces maintenance burden

**Sources:** [src/main.py:1-198]()

## File Path Reference Guide

Quick reference for key repository files:

| File | Purpose | Type |
|------|---------|------|
| [README.md:1-416]() | Primary documentation with expert commentary | Manual |
| [assets/paper.json:1-848]() | Structured paper metadata (12 categories, ~256 papers) | Manual |
| [src/main.py:1-198]() | Build script for generating auxiliary formats | Code |
| [src/table.md:1-149]() | Tabular format of all papers | Generated |
| [src/list.md:1-129]() | List format with badges | Generated |
| [assets/timeline.png]() | Visual timeline of research evolution | Manual |
| [assets/timeline_2.png]() | Recent timeline of reasoning LLMs | Manual |
| [assets/develope.jpg]() | AI systems progression diagram | Manual |

**Sources:** Repository file structure analysis

---

# Page: Using This Resource

# Using This Resource

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/paper.json](assets/paper.json)

</details>



This document provides practical guidance for researchers and practitioners on navigating the Awesome-System2-Reasoning-LLM repository, finding relevant papers for specific use cases, understanding the data structure, and contributing updates.

For an overview of the research landscape and the 12-part taxonomy, see [Research Landscape Overview](#3). For technical details on specific methodologies, see [Core Methodologies](#4).

## Purpose and Scope

This guide covers:
- **Navigation strategies** for finding papers by topic, timeline, or venue
- **Use case mapping** to identify which research parts address your specific problems
- **Data structure** (`paper.json`) and how to work with it
- **Build system** for generating alternative views
- **Contribution workflow** for adding new papers or corrections

---

## Repository Structure and Entry Points

The repository provides multiple interfaces for accessing the same underlying paper collection, optimized for different exploration strategies.

### Primary Files

```mermaid
graph TB
    subgraph "Primary Interface"
        README["README.md<br/>(Lines 1-509)<br/>Hand-curated descriptions"]
    end
    
    subgraph "Data Layer"
        JSON["assets/paper.json<br/>Structured metadata<br/>~256 papers"]
    end
    
    subgraph "Generated Views"
        TABLE["src/table.md<br/>Tabular format<br/>Sorted by date"]
        LIST["src/list.md<br/>List format<br/>With badges"]
    end
    
    subgraph "Build System"
        BUILDER["src/main.py<br/>Generator script"]
    end
    
    subgraph "Visual Assets"
        TIMELINE1["assets/timeline_2.png"]
        DEVELOPE["assets/develope.jpg"]
    end
    
    README -->|"references"| TIMELINE1
    README -->|"references"| DEVELOPE
    JSON --> BUILDER
    BUILDER --> TABLE
    BUILDER --> LIST
    JSON -.informs.-> README
```

**Sources:** [README.md:1-509](), [assets/paper.json:1-848](), [src/main.py]()

---

## Navigation Methods

### Method 1: Thematic Navigation via 12 Research Parts

The primary navigation path is through the 12 research parts defined in the README table of contents.

```mermaid
graph LR
    TOC["README.md:29-43<br/>Table of Contents"]
    
    subgraph "Core Methods (Parts 1-6)"
        P1["Part 1: O1 Replication<br/>Lines 45-67"]
        P2["Part 2: Process Reward Models<br/>Lines 68-96"]
        P3["Part 3: Reinforcement Learning<br/>Lines 98-137"]
        P4["Part 4: MCTS/Tree Search<br/>Lines 139-193"]
        P5["Part 5: Self-Training<br/>Lines 194-224"]
        P6["Part 6: Reflection<br/>Lines 225-241"]
    end
    
    subgraph "Optimization (Parts 7-8)"
        P7["Part 7: Efficient System2<br/>Lines 242-325"]
        P8["Part 8: Explainability<br/>Lines 327-338"]
    end
    
    subgraph "Extensions (Parts 9,12)"
        P9["Part 9: Multimodal Agents<br/>Lines 339-350"]
        P12["Part 12: R1 Multimodal<br/>Lines 455-481"]
    end
    
    subgraph "Infrastructure (Parts 10-11)"
        P10["Part 10: Benchmarks<br/>Lines 351-433"]
        P11["Part 11: Safety<br/>Lines 437-453"]
    end
    
    TOC --> P1
    TOC --> P2
    TOC --> P3
    TOC --> P4
    TOC --> P5
    TOC --> P6
    TOC --> P7
    TOC --> P8
    TOC --> P9
    TOC --> P10
    TOC --> P11
    TOC --> P12
```

**How to use:** Scan [README.md:29-43]() to identify which parts align with your research interests, then jump directly to the corresponding section.

**Sources:** [README.md:29-43](), [README.md:45-481]()

---

### Method 2: Chronological Navigation via Timeline

For understanding the field's evolution, use the timeline images and chronological ordering.

```mermaid
graph TB
    TIMELINE["assets/timeline_2.png<br/>Visual timeline"]
    
    subgraph "2017-2022: Foundations"
        F1["Expert Iteration (2017)<br/>Part 5"]
        F2["STaR (2022)<br/>Part 5"]
    end
    
    subgraph "2023: Breakthroughs"
        B1["Let's Verify Step by Step<br/>Part 2"]
        B2["AlphaZero-like Tree Search<br/>Part 4"]
        B3["ReST (2023)<br/>Part 5"]
    end
    
    subgraph "2024: Integration"
        I1["Math-Shepherd<br/>Part 2"]
        I2["ReST-MCTS*<br/>Parts 2,4,5"]
        I3["Multiple MCTS works<br/>Part 4"]
    end
    
    subgraph "2025: Production"
        PR1["DeepSeek-R1<br/>Part 3"]
        PR2["Kimi k1.5<br/>Part 3"]
        PR3["rStar-Math<br/>Parts 4,5"]
    end
    
    TIMELINE --> F1
    TIMELINE --> F2
    TIMELINE --> B1
    TIMELINE --> B2
    TIMELINE --> B3
    TIMELINE --> I1
    TIMELINE --> I2
    TIMELINE --> I3
    TIMELINE --> PR1
    TIMELINE --> PR2
    TIMELINE --> PR3
```

**How to use:** Reference [assets/timeline_2.png]() for a visual overview. Papers in each part are generally ordered chronologically within their sections.

**Sources:** [README.md:25-26](), [assets/timeline_2.png]()

---

### Method 3: Venue-Based Filtering

Papers are tagged with venue badges for filtering by publication type.

| Badge Color | Venue Type | Example |
|------------|------------|---------|
| ![](https://img.shields.io/badge/arXiv-red) | Preprints | Most recent work |
| ![](https://img.shields.io/badge/NeurIPS-blue) | Conference | Peer-reviewed |
| ![](https://img.shields.io/badge/ACL-blue) | Conference | NLP-focused |
| ![](https://img.shields.io/badge/ICLR-blue) | Conference | ML/representation learning |
| ![](https://img.shields.io/badge/blog-red) | Blog posts | Technical reports |
| ![](https://img.shields.io/badge/github-red) | Code repos | Implementation-focused |

**How to use:** In [README.md](), scan for badge colors. Blue badges indicate peer-reviewed conference papers, red badges indicate preprints or technical reports.

**Sources:** [README.md:47-481]()

---

### Method 4: Alternative Views

For different presentation formats, use the generated views.

```mermaid
graph LR
    JSON["assets/paper.json"]
    MAIN["src/main.py"]
    
    TABLE["src/table.md<br/>Columns:<br/>Title | Venue | Date<br/>Sorted by date"]
    LIST["src/list.md<br/>Bullet list<br/>With badges<br/>Grouped by part"]
    
    JSON --> MAIN
    MAIN --> TABLE
    MAIN --> LIST
    
    README["README.md<br/>Rich descriptions<br/>Categorized narratives"]
    JSON -.informs.-> README
```

**When to use each:**
- **README.md**: Primary interface with context and descriptions
- **src/table.md**: Quick scanning by date or venue
- **src/list.md**: Compact view for reference
- **assets/paper.json**: Programmatic access or custom filtering

**Sources:** [src/main.py](), [assets/paper.json:1-848]()

---

## Finding Papers for Your Use Case

Map your research problem to the relevant parts using this decision tree.

```mermaid
graph TB
    START["What is your goal?"]
    
    START --> Q1{"Building an<br/>o1-like system?"}
    START --> Q2{"Training with<br/>limited data?"}
    START --> Q3{"Working with<br/>vision-language?"}
    START --> Q4{"Need to<br/>evaluate?"}
    START --> Q5{"Reducing<br/>compute cost?"}
    START --> Q6{"Safety<br/>concerns?"}
    
    Q1 -->|"Yes"| P1["Part 1: O1 Replication<br/>+<br/>Parts 2-6 (foundations)"]
    
    Q2 -->|"Yes"| TRAIN["Part 5: Self-Training<br/>Part 2: Process Rewards<br/>Part 4: MCTS"]
    
    Q3 -->|"Yes"| MULTI["Part 9: Multimodal Agents<br/>Part 12: R1 Multimodal<br/>Part 6: Reflection"]
    
    Q4 -->|"Yes"| BENCH["Part 10: Benchmarks<br/>Part 2: PRMBench"]
    
    Q5 -->|"Yes"| EFF["Part 7: Efficient System2<br/>+<br/>Part 8: Explainability"]
    
    Q6 -->|"Yes"| SAFE["Part 11: Safety<br/>Part 2: Process Rewards"]
```

### Use Case Examples

| Problem | Recommended Parts | Key Papers |
|---------|------------------|------------|
| **Reproduce o1 capabilities** | Parts 1, 2, 3, 4 | DeepSeek-R1, ReST-MCTS*, Kimi k1.5 |
| **Improve math reasoning** | Parts 2, 4, 5 | Math-Shepherd, rStar-Math, ReST-MCTS* |
| **Enable self-improvement** | Parts 5, 6 | STaR, V-star, Self-Refine |
| **Add vision understanding** | Parts 9, 12 | LLaVA-o1, Virgo, AtomThink |
| **Reduce inference cost** | Part 7 | DynaThink, O1-Pruner, Token-Budget-Aware |
| **Verify reasoning steps** | Part 2 | Let's Verify Step by Step, AutoPSV, PRMBench |
| **Test reasoning robustness** | Parts 10, 11 | MR-Ben, PRMBench, SafeChain |

**Sources:** [README.md:45-481]()

---

## Understanding the Data Structure

### paper.json Schema

The repository's source data is stored in [assets/paper.json:1-848]() with the following structure:

```mermaid
graph TB
    ROOT["paper.json<br/>Root Object"]
    
    subgraph "Keys (12 Parts)"
        K1["'Part 1: O1 Replication'"]
        K2["'Part 2: Process Reward Models'"]
        K3["'Part 3: Reinforcement Learning'"]
        KDOTS["..."]
        K12["'Part 12: R1 Multimodal...'"]
    end
    
    subgraph "Value (Array of Papers)"
        PAPER["PaperInformation Object"]
    end
    
    subgraph "Paper Fields"
        TITLE["'paper': string<br/>Full title"]
        LINK["'link': string<br/>URL to paper"]
        VENUE["'venue': string<br/>Conference or arXiv"]
        DATE["'date': string<br/>YYYY-MM format"]
        LABEL["'label': string<br/>Citation key"]
    end
    
    ROOT --> K1
    ROOT --> K2
    ROOT --> K3
    ROOT --> KDOTS
    ROOT --> K12
    
    K1 --> PAPER
    PAPER --> TITLE
    PAPER --> LINK
    PAPER --> VENUE
    PAPER --> DATE
    PAPER --> LABEL
```

**Example entry:**

```json
{
    "paper": "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
    "link": "https://arxiv.org/abs/2501.12948",
    "venue": "arXiv",
    "date": "2025-01",
    "label": "luong2025deepseekr1"
}
```

**Sources:** [assets/paper.json:1-848]()

---

### Programmatic Access Pattern

To extract papers by part or filter by criteria:

```python
# Pseudocode for accessing paper.json
import json

# Load data
with open('assets/paper.json') as f:
    data = json.load(f)

# Access specific part
o1_papers = data["Part 1: O1 Replication"]

# Filter by date
recent_papers = [p for p in o1_papers if p["date"] >= "2025-01"]

# Filter by venue
conference_papers = [p for p in o1_papers if p["venue"] != "arXiv"]
```

**Sources:** [assets/paper.json:1-848]()

---

## Build System and Generation Pipeline

The repository uses [src/main.py]() to generate alternative views from [assets/paper.json]().

```mermaid
graph TB
    subgraph "Input"
        JSON["assets/paper.json<br/>Structured metadata"]
    end
    
    subgraph "Processing (src/main.py)"
        LOAD["load_json()<br/>Read paper.json"]
        EXTRACT["extract_unique_papers()<br/>Flatten & deduplicate"]
        RESOLVE["resolve_labels()<br/>Handle cross-references"]
        PROCESS["Processed dictionary<br/>with PaperInformation"]
    end
    
    subgraph "Output Generation"
        TABLE["generate_table_md()<br/>→ src/table.md"]
        LIST["generate_list_md()<br/>→ src/list.md"]
    end
    
    JSON --> LOAD
    LOAD --> EXTRACT
    EXTRACT --> RESOLVE
    RESOLVE --> PROCESS
    PROCESS --> TABLE
    PROCESS --> LIST
```

### Key Functions

| Function | Purpose | Output |
|----------|---------|--------|
| `load_json()` | Parse `paper.json` into Python dict | Dictionary of parts → paper arrays |
| `extract_unique_papers()` | Flatten and remove duplicates | Single list of unique papers |
| `resolve_labels()` | Expand label references | Papers with full metadata |
| `generate_table_md()` | Create sorted table view | `src/table.md` |
| `generate_list_md()` | Create categorized list | `src/list.md` |

**Sources:** [src/main.py](), [assets/paper.json:1-848]()

---

### Label Reference System

Papers can appear in multiple parts via the `label` field. When a paper is referenced again, only the label is needed:

```json
{
    "Part 2: Process Reward Models": [
        {
            "paper": "ReST-MCTS*: LLM Self-Training via Process Reward Guided Tree Search",
            "link": "https://arxiv.org/abs/2406.03816",
            "venue": "NeurIPS",
            "date": "2024-12",
            "label": "zhang2024restmcts"
        }
    ],
    "Part 4: MCTS/Tree Search": [
        {
            "label": "zhang2024restmcts"
        }
    ],
    "Part 5: Self-Training / Self-Improve": [
        {
            "label": "zhang2024restmcts"
        }
    ]
}
```

The build system resolves these references to avoid duplication in the JSON file.

**Sources:** [assets/paper.json:55-60](), [assets/paper.json:409-414](), [assets/paper.json:571-577]()

---

## Understanding Paper Relationships

Papers in this repository often build on or combine techniques from multiple parts.

```mermaid
graph TB
    subgraph "Foundational Papers"
        STAR["STaR (2022)<br/>Part 5<br/>Self-training foundation"]
        VERIFY["Let's Verify (2023)<br/>Part 2<br/>Process rewards"]
        ALPHA["AlphaZero-like (2023)<br/>Part 4<br/>Tree search for LLMs"]
    end
    
    subgraph "Integration Papers"
        REST["ReST (2023)<br/>Part 5<br/>RL + Self-training"]
        RESTMCTS["ReST-MCTS* (2024)<br/>Parts 2,4,5<br/>Process + Search + Self-training"]
        RSTAR["rStar-Math (2025)<br/>Parts 4,5<br/>Self-evolved deep thinking"]
    end
    
    subgraph "Production Systems"
        R1["DeepSeek-R1 (2025)<br/>Part 3<br/>Large-scale RL"]
        K15["Kimi k1.5 (2025)<br/>Part 3<br/>Scaled RL"]
    end
    
    STAR --> REST
    STAR --> RESTMCTS
    VERIFY --> RESTMCTS
    ALPHA --> RESTMCTS
    REST --> R1
    REST --> K15
    RESTMCTS --> RSTAR
```

### Multi-Part Papers

Papers appearing in multiple parts indicate integration of techniques:

| Paper | Parts | Integrates |
|-------|-------|------------|
| **ReST-MCTS*** | 2, 4, 5 | Process Rewards + MCTS + Self-Training |
| **HuatuoGPT-o1** | 1, 4, 6 | O1 Replication + MCTS + Reflection |
| **Marco-o1** | 1, 4, 6 | O1 Replication + MCTS + Reflection |
| **rStar-Math** | 4, 5, 6 | MCTS + Self-Training + Reflection |
| **ReFT** | 3, 5 | RL + Self-Training |
| **Mulberry** | 4, 6 | MCTS + Reflection (multimodal) |

**How to find related papers:** Search for the same paper title across multiple parts in [README.md](), or check the `label` field in [assets/paper.json]().

**Sources:** [README.md:45-481](), [assets/paper.json:1-848]()

---

## Contributing Updates

### Contribution Workflow

```mermaid
graph TB
    IDENTIFY["Identify new paper or correction"]
    
    FORK["Fork repository"]
    BRANCH["Create feature branch"]
    
    UPDATE_JSON["Edit assets/paper.json<br/>Add paper entry"]
    UPDATE_README["Edit README.md<br/>Add to relevant part(s)"]
    
    RUN_BUILD["Run src/main.py<br/>Regenerate table.md, list.md"]
    
    COMMIT["Commit changes"]
    PR["Open pull request"]
    REVIEW["Maintainer review"]
    
    IDENTIFY --> FORK
    FORK --> BRANCH
    BRANCH --> UPDATE_JSON
    BRANCH --> UPDATE_README
    UPDATE_JSON --> RUN_BUILD
    UPDATE_README --> RUN_BUILD
    RUN_BUILD --> COMMIT
    COMMIT --> PR
    PR --> REVIEW
```

**Sources:** [README.md:6]()

---

### Adding a New Paper

1. **Choose the appropriate part(s):** Refer to the 12-part taxonomy in [README.md:29-43]()

2. **Add entry to paper.json:**

```json
{
    "Part X: Category Name": [
        {
            "paper": "Paper Title: Subtitle",
            "link": "https://arxiv.org/abs/XXXX.XXXXX",
            "venue": "arXiv",
            "date": "YYYY-MM",
            "label": "firstauthor2025keyword"
        }
    ]
}
```

3. **Add entry to README.md:**

```markdown
* Paper Title: Subtitle [[Paper]](https://arxiv.org/abs/XXXX.XXXXX) ![](https://img.shields.io/badge/arXiv-YYYY.MM-red)
```

4. **For multi-part papers:** Add full entry in primary part, use `label` reference in other parts:

```json
{
    "Part Y: Another Category": [
        {
            "label": "firstauthor2025keyword"
        }
    ]
}
```

5. **Regenerate views:** Run `python src/main.py` (if applicable)

6. **Submit pull request** with descriptive title

**Sources:** [README.md:6](), [assets/paper.json:1-848]()

---

### Reporting Issues

For corrections, missing papers, or categorization suggestions:

1. **Check existing issues** to avoid duplicates
2. **Open a GitHub issue** with:
   - Paper title and link (for additions)
   - Current vs. proposed categorization (for changes)
   - Rationale for the change
3. **Tag appropriately:** `addition`, `correction`, `enhancement`

**Sources:** [README.md:6]()

---

## Citation Information

If using this resource in academic work, cite the survey paper:

```bibtex
@misc{li202512surveyreasoning,
      title={From System 1 to System 2: A Survey of Reasoning Large Language Models}, 
      author={Zhong-Zhi Li and Duzhen Zhang and Ming-Liang Zhang and Jiaxin Zhang and Zengyan Liu and Yuxuan Yao and Haotian Xu and Junhao Zheng and Pei-Jie Wang and Xiuyi Chen and Yingying Zhang and Fei Yin and Jiahua Dong and Zhijiang Guo and Le Song and Cheng-Lin Liu},
      year={2025},
      eprint={2502.17419},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2502.17419}, 
}
```

**Sources:** [README.md:485-497]()

---

## Quick Reference Table

| Task | File | Lines | Purpose |
|------|------|-------|---------|
| Browse by topic | `README.md` | 29-481 | Hand-curated descriptions |
| Browse by date | `src/table.md` | All | Chronologically sorted |
| Access structured data | `assets/paper.json` | 1-848 | Programmatic access |
| Regenerate views | `src/main.py` | All | Build system |
| View timeline | `assets/timeline_2.png` | N/A | Visual evolution |
| Submit updates | GitHub PR | N/A | Contribution workflow |

**Sources:** [README.md:1-509](), [assets/paper.json:1-848](), [src/main.py]()