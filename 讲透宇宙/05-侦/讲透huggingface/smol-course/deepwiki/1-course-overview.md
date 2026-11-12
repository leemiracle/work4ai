<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/smol-course · page 1 Course Overview · fetched 2026-10-26 -->

# Course Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [banner.png](banner.png)
- [requirements.txt](requirements.txt)
- [units/en/_toctree.yml](units/en/_toctree.yml)

</details>



This document provides an overview of the smol-course, a practical training program for aligning language models to specific use cases. The course covers the complete pipeline from instruction tuning through preference alignment and multimodal model adaptation, using the SmolLM3 and SmolVLM2 model families. For detailed installation instructions, see [Installation and Setup](#1.1). For specific training methodologies, see [Instruction Tuning](#2), [Preference Alignment](#4), and [Vision-Language Models](#5).

**Sources:** [README.md:1-69]()

## Course Objectives

The smol-course teaches practical alignment techniques for language models that run on consumer hardware. The curriculum emphasizes hands-on learning with minimal GPU requirements and no paid cloud services. Key learning outcomes include:

- **Instruction Tuning**: Adapting pre-trained models to follow instructions using supervised fine-tuning with `SFTTrainer`
- **Parameter Efficiency**: Implementing LoRA and quantization to train models on limited hardware
- **Preference Alignment**: Aligning models to human preferences using DPO and ORPO algorithms
- **Multimodal Adaptation**: Fine-tuning vision-language models for image understanding tasks
- **Model Evaluation**: Benchmarking models using `lighteval` framework with standard and custom metrics
- **Production Deployment**: Training on Hugging Face Jobs infrastructure and publishing to Hub

The course uses SmolLM3-3B for text-only tasks and SmolVLM2-2.2B for multimodal applications. Skills learned with these models transfer to larger models and other small LLM/VLM architectures.

**Sources:** [README.md:5-56]()

## Model Architecture

### Course Unit to Codebase Mapping

```mermaid
graph TB
    subgraph "Repository Structure [github.com/huggingface/smol-course]"
        Root["Root Directory"]
        UnitsDir["units/en/"]
        
        subgraph "Unit 0: Welcome"
            Unit0["units/en/unit0/"]
            Unit0_1["1.md: Welcome"]
        end
        
        subgraph "Unit 1: Instruction Tuning"
            Unit1["units/en/unit1/"]
            Unit1_1["1.md: Introduction"]
            Unit1_2["2.md: Chat Templates"]
            Unit1_3["3.md: SFT"]
            Unit1_3a["3a.md: LoRA and PEFT"]
            Unit1_4["4.md: Practical Exercises"]
            Unit1_5["5.md: HF Jobs Training"]
            Unit1_6["6.md: Final Project"]
        end
        
        subgraph "Unit 2: Preference Alignment"
            Unit2["units/en/unit2/"]
            Unit2_1["1.md: Introduction"]
            Unit2_2["2.md: DPO"]
            Unit2_3["3.md: Advanced DPO"]
            Unit2_4["4.md: Hands-on DPO"]
        end
        
        subgraph "Unit 3: Vision Language Models"
            Unit3["units/en/unit3/"]
            Unit3_1["1.md: Introduction"]
            Unit3_2["2.md: Using Pretrained VLMs"]
            Unit3_3["3.md: Fine-Tuning VLMs"]
            Unit3_4["4.md: Hands-On"]
        end
        
        subgraph "Unit 4: Model Evaluation"
            Unit4["units/en/unit4/"]
            Unit4_1["1.md: Coming Soon"]
        end
        
        TOC["_toctree.yml"]
    end
    
    Root --> UnitsDir
    UnitsDir --> TOC
    UnitsDir --> Unit0
    UnitsDir --> Unit1
    UnitsDir --> Unit2
    UnitsDir --> Unit3
    UnitsDir --> Unit4
    
    Unit0 --> Unit0_1
    
    Unit1 --> Unit1_1
    Unit1 --> Unit1_2
    Unit1 --> Unit1_3
    Unit1 --> Unit1_3a
    Unit1 --> Unit1_4
    Unit1 --> Unit1_5
    Unit1 --> Unit1_6
    
    Unit2 --> Unit2_1
    Unit2 --> Unit2_2
    Unit2 --> Unit2_3
    Unit2 --> Unit2_4
    
    Unit3 --> Unit3_1
    Unit3 --> Unit3_2
    Unit3 --> Unit3_3
    Unit3 --> Unit3_4
    
    Unit4 --> Unit4_1
```

**Sources:** [units/en/_toctree.yml:1-48]()

### Base Models

The course utilizes two pre-trained model families from the Hugging Face Hub:

| Model | Parameters | Architecture | Use Cases |
|-------|-----------|--------------|-----------|
| SmolLM3-3B-Base | 3 billion | Decoder-only transformer | Text instruction tuning, preference alignment |
| SmolVLM2-2.2B-Base | 2.2 billion | Vision encoder + language decoder | Multimodal tasks, image understanding, chart/diagram analysis |

Both models are optimized for efficiency and can be fine-tuned on consumer GPUs with 16GB+ VRAM when using parameter-efficient techniques. The base models are pre-trained on large text corpora (SmolLM3) or multimodal data (SmolVLM2) and require task-specific fine-tuning for instruction following.

**Sources:** [README.md:5-6]()

## Course Structure

The curriculum consists of seven units organized into three phases: core training modules (Units 1-3), evaluation methodology (Unit 4), and advanced techniques (Units 5-6). Unit 7 provides a capstone experience.

### Current Curriculum Status

| Unit | Topic | Status | Key Techniques |
|------|-------|--------|----------------|
| 0 | Welcome | ✅ Released | Course orientation |
| 1 | Instruction Tuning | ✅ Released | `SFTTrainer`, chat templates, LoRA, quantization |
| 2 | Preference Alignment | ✅ Released | `DPOTrainer`, ORPO, preference datasets |
| 3 | Vision Language Models | ✅ Released | `AutoProcessor`, multimodal templates, VLM fine-tuning |
| 4 | Model Evaluation | ✅ Released | `lighteval`, benchmarks, custom metrics |
| 5 | Reinforcement Learning | 🚧 October 2025 | Policy optimization, reward models |
| 6 | Synthetic Data | 🚧 November 2025 | Data generation, distillation |
| 7 | Award Ceremony | 🚧 December 2025 | Project showcase |

Each unit includes markdown documentation, interactive Jupyter notebooks, and hands-on exercises. Units 1-4 progress from basic instruction tuning to advanced evaluation methodologies. Future units will cover reinforcement learning from human feedback and synthetic data generation.

**Sources:** [README.md:31-43](), [units/en/_toctree.yml:1-48]()

### Learning Progression

```mermaid
graph LR
    U0["Unit 0<br/>Welcome"] --> U1["Unit 1<br/>Instruction Tuning<br/>SFTTrainer"]
    U1 --> U2["Unit 2<br/>Preference Alignment<br/>DPOTrainer"]
    U2 --> U3["Unit 3<br/>Vision Language Models<br/>SmolVLM2"]
    U3 --> U4["Unit 4<br/>Model Evaluation<br/>lighteval"]
    U4 --> U5["Unit 5<br/>Reinforcement Learning<br/>TBD"]
    U5 --> U6["Unit 6<br/>Synthetic Data<br/>TBD"]
    U6 --> U7["Unit 7<br/>Award Ceremony"]
    
    U1 -.-> PEFT["Parameter Efficiency<br/>LoRA + Quantization"]
    U2 -.-> PEFT
    U3 -.-> PEFT
    
    U1 -.-> Chat["Chat Templates<br/>apply_chat_template()"]
    U3 -.-> Chat
    
    U1 --> Exercise1["Submit Model<br/>to Leaderboard"]
    U2 --> Exercise2["Submit Model<br/>to Leaderboard"]
    U3 --> Exercise3["Submit Model<br/>to Leaderboard"]
```

**Sources:** [README.md:31-43](), [units/en/_toctree.yml:1-48]()

## Technical Stack

### Core Dependencies

The course uses a curated set of libraries from the Hugging Face ecosystem and PyTorch. All dependencies are managed via `requirements.txt` with pinned versions for reproducibility.

```mermaid
graph TB
    subgraph "Deep Learning Framework"
        PyTorch["torch==2.5.1"]
        CUDA["nvidia-cuda-runtime-cu12==12.4.127"]
        Triton["triton==3.1.0"]
    end
    
    subgraph "Hugging Face Ecosystem"
        Transformers["transformers==4.46.3"]
        TRL["trl==0.12.1"]
        PEFT["peft (via trl)"]
        Datasets["datasets==3.1.0"]
        HFHub["huggingface-hub==0.26.3"]
    end
    
    subgraph "Optimization Libraries"
        Accelerate["accelerate==1.1.1"]
        BitsBytes["bitsandbytes==0.45.0"]
        SafeTensors["safetensors==0.4.5"]
    end
    
    subgraph "Data Processing"
        Tokenizers["tokenizers==0.20.3"]
        Pandas["pandas==2.2.3"]
        PyArrow["pyarrow==18.1.0"]
        Dill["dill==0.3.8"]
    end
    
    subgraph "Evaluation"
        LightEval["lighteval==0.6.2 (optional)"]
        VLLM["vllm (optional)"]
    end
    
    PyTorch --> Transformers
    PyTorch --> TRL
    CUDA --> PyTorch
    
    Transformers --> TRL
    PEFT --> TRL
    Datasets --> TRL
    
    Accelerate --> TRL
    BitsBytes --> PEFT
    
    HFHub --> Transformers
    HFHub --> Datasets
    HFHub --> TRL
    
    Tokenizers --> Transformers
    SafeTensors --> Transformers
    
    Pandas --> Datasets
    PyArrow --> Datasets
    Dill --> Datasets
```

**Sources:** [requirements.txt:1-65]()

### Library Versions and Roles

| Library | Version | Role |
|---------|---------|------|
| `torch` | 2.5.1 | Deep learning framework, model computation |
| `transformers` | 4.46.3 | Model loading, tokenization, inference APIs |
| `trl` | 0.12.1 | Training orchestration (`SFTTrainer`, `DPOTrainer`) |
| `datasets` | 3.1.0 | Dataset loading, preprocessing, streaming |
| `accelerate` | 1.1.1 | Distributed training, device management |
| `bitsandbytes` | 0.45.0 | 4-bit/8-bit quantization for memory efficiency |
| `huggingface-hub` | 0.26.3 | Model/dataset download, Hub uploads |
| `safetensors` | 0.4.5 | Fast, secure model serialization format |

The `trl` library serves as the primary training interface, integrating models from `transformers`, efficiency techniques from `peft`, and data from `datasets`. The `accelerate` library enables multi-GPU training and mixed precision, while `bitsandbytes` provides quantization for memory-constrained environments.

**Sources:** [requirements.txt:3-65]()

### CUDA Dependencies

For GPU acceleration on Linux x86_64 systems, the course includes NVIDIA CUDA 12.4 libraries:

- `nvidia-cuda-runtime-cu12==12.4.127`: CUDA runtime
- `nvidia-cublas-cu12==12.4.5.8`: Linear algebra operations
- `nvidia-cudnn-cu12==9.1.0.70`: Neural network primitives
- `nvidia-nccl-cu12==2.21.5`: Multi-GPU communication

These dependencies are automatically installed on compatible systems and enable GPU training without manual CUDA installation.

**Sources:** [requirements.txt:27-38]()

## Learning Methodology

### Community-Driven Approach

The course operates as a peer-reviewed, open learning platform. Students actively contribute to the course content through pull requests, creating a continuously improving curriculum.

**Participation Model:**
1. Follow the `smol-course` organization on Hugging Face Hub
2. Read unit documentation and complete exercises locally
3. Train models and submit results to the community leaderboard
4. Open pull requests with trained models, evaluation results, and training commands
5. Receive community feedback and climb the leaderboard rankings

This approach encourages collaborative learning where students learn from each other's implementations and training strategies. The leaderboard serves as both a motivational tool and a repository of successful training configurations.

**Sources:** [README.md:7-17](), [README.md:19-23]()

### Repository Access

The course materials are hosted at `https://github.com/huggingface/smol-course`. The repository structure includes:

- `units/en/`: Course content organized by unit
- `requirements.txt`: Python dependencies
- `README.md`: Course overview and quick start
- `v1/`: Legacy course materials (Jupyter notebooks)

Future releases will migrate to Hugging Face Learn platform while maintaining GitHub as the primary development repository.

**Sources:** [README.md:27-29](), [README.md:65-68]()

## Hardware Requirements

### Local Training

The course is designed for consumer hardware with minimal GPU requirements. Successful local training requires:

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | 16GB | 24GB+ |
| System RAM | 16GB | 32GB+ |
| Storage | 50GB | 100GB+ (for datasets) |
| OS | Linux, Windows, macOS | Linux (best CUDA support) |

With 16GB VRAM, students can train SmolLM3-3B using 4-bit quantization and LoRA (rank 8-16). Larger batch sizes and higher LoRA ranks require more VRAM. The course provides memory optimization techniques (gradient checkpointing, gradient accumulation) to work within hardware constraints.

**Sources:** [README.md:48-56]()

### Cloud Training Alternative

For students without local GPU access, Hugging Face Jobs provides cloud training infrastructure:

- **a10g-large**: NVIDIA A10G (24GB VRAM)
- **a100-large**: NVIDIA A100 (40GB/80GB VRAM)

Unit 1, section 5 covers cloud training workflows using the `hf jobs` CLI. This enables identical training code to run locally or on cloud infrastructure without modification.

**Sources:** [units/en/_toctree.yml:19]()

## Prerequisites

Students should have foundational knowledge before starting the course:

### Required Background

- **Machine Learning Fundamentals**: Understanding of supervised learning, loss functions, gradient descent
- **Natural Language Processing**: Familiarity with tokenization, embeddings, transformer architectures
- **Python Programming**: Proficiency with Python 3.8+, package management (pip, conda, uv)
- **PyTorch Basics**: Tensor operations, model loading, basic training loops
- **Transformers Library**: Experience with `AutoModel`, `AutoTokenizer`, `pipeline` APIs

### Optional But Helpful

- Experience with Jupyter notebooks for interactive development
- Git/GitHub for version control and collaboration
- Linux command line for cloud training workflows
- Understanding of model evaluation metrics (perplexity, accuracy)

Students without extensive PyTorch experience can still succeed by following the provided code examples and gradually building understanding through hands-on exercises.

**Sources:** [README.md:58-63]()

## Why Small Language Models

The course focuses on small models (2-3B parameters) rather than large models (70B+) for practical and pedagogical reasons:

### Advantages of Small Models

| Benefit | Description |
|---------|-------------|
| **Efficiency** | Train and deploy on consumer hardware without cloud costs |
| **Customization** | Faster iteration cycles for domain-specific adaptation |
| **Control** | Easier to understand and debug model behavior |
| **Cost** | Lower training and inference costs for production deployment |
| **Privacy** | Can run entirely on-premises without external API calls |
| **Sustainability** | Reduced energy consumption and carbon footprint |
| **Research Accessibility** | Enables academic research without institutional compute clusters |

### Performance Trade-offs

Small models sacrifice some general capability for efficiency. They excel at focused tasks where domain-specific fine-tuning provides the necessary knowledge. The course teaches how to maximize small model performance through:

- High-quality instruction data curation
- Effective preference alignment
- Task-specific evaluation metrics
- Multi-stage training pipelines

Skills learned with SmolLM3-3B and SmolVLM2-2.2B transfer directly to larger models, making this course a practical starting point for language model alignment regardless of target model size.

**Sources:** [README.md:46-56]()

---

