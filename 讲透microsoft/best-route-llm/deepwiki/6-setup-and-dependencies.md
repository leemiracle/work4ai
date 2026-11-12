<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/best-route-llm · page 6 Setup and Dependencies · fetched 2026-10-26 -->

# Setup and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [notebooks/requirements_data_preparation.txt](notebooks/requirements_data_preparation.txt)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)

</details>



The **BEST-Route** project (utilizing the `hybrid_llm` core package) requires a multi-stage environment setup. Because the project spans from data preparation and reward modeling in Jupyter notebooks to large-scale router training via CLI scripts, dependencies are split between core package requirements and specialized notebook environments.

This page provides a high-level overview of the installation process and dependency management.

### Environment Architecture

The following diagram illustrates how the different dependency files relate to the functional areas of the codebase.

**Dependency Mapping**
```mermaid
graph TD
    subgraph "Core Package Space"
        [setup.py] --> [hybrid_llm_package]
        [requirements.txt] --> [hybrid_llm_package]
        [hybrid_llm_package] -- "depends on" --> ["llm-blender (GitHub)"]
        [hybrid_llm_package] -- "depends on" --> ["py-cpuinfo"]
    end

    subgraph "Data & Modeling Space"
        [notebooks/requirements_data_preparation.txt] --> [Data_Prep_Env]
        [Data_Prep_Env] -- "includes" --> ["transformers"]
        [Data_Prep_Env] -- "includes" --> ["trl (RewardTrainer)"]
        [Data_Prep_Env] -- "includes" --> ["accelerate"]
    end

    [hybrid_llm_package] -- "Imported by" --> [train_router.py]
    [Data_Prep_Env] -- "Used by" --> [reward_modeling.ipynb]
    [Data_Prep_Env] -- "Used by" --> [generate_llm_responses.py]
```
Sources: [setup.py:1-7](), [requirements.txt:1-3](), [notebooks/requirements_data_preparation.txt:1-10]()

---

### 6.1 Core Package Installation

The core logic for routing and ranker architectures is housed in the `hybrid_llm` directory. This is managed as a standard Python package via `setup.py` [setup.py:1-7](). 

Key characteristics of the core installation:
*   **LLM-Blender Dependency**: The project relies heavily on a specific fork/version of `LLM-Blender`, installed directly from GitHub [requirements.txt:2-2](). This provides essential utilities for tokenization, training loops, and the base `pair_ranker` logic.
*   **Hardware Utility**: Includes `py-cpuinfo` for environment diagnostics [requirements.txt:1-1]().
*   **Installation**: Typically performed using `pip install -e .` to allow for development edits to the `hybrid_llm` source.

For detailed installation steps and a breakdown of the `LLM-Blender` integration, see **[Core Package Installation](#6.1)**.

---

### 6.2 Notebook Environment Setup

Data preparation, response generation, and proxy reward model training are conducted using scripts and notebooks that require a more extensive set of ML libraries than the core router.

*   **Model Handling**: Uses `transformers`, `datasets`, and `accelerate` for managing Large Language Models [notebooks/requirements_data_preparation.txt:1-5]().
*   **Reward Modeling**: Requires `trl` (Transformer Reinforcement Learning) specifically for the `RewardTrainer` used in training the proxy reward model [notebooks/requirements_data_preparation.txt:7-7]().
*   **Gated Access**: Requires `huggingface_hub` for authentication, particularly for accessing gated models like Llama 3.1 [notebooks/requirements_data_preparation.txt:4-4]().
*   **GPU Optimization**: Guidance is provided for managing memory via `PYTORCH_CUDA_ALLOC_CONF` to prevent Out-Of-Memory (OOM) errors during heavy inference tasks.

For details on configuring your GPU environment and authenticating for model access, see **[Notebook Environment Setup](#6.2)**.

---

### Dependency Interaction

The relationship between the code entities and the installed dependencies is summarized below:

**System-Code Association**
```mermaid
graph LR
    subgraph "Natural Language Space"
        "Router Training"
        "Proxy Reward Training"
        "Response Generation"
    end

    subgraph "Code Entity Space"
        "Router Training" --> [train_router.py]
        "Proxy Reward Training" --> [notebooks/reward_modeling.py]
        "Response Generation" --> [notebooks/generate_llm_responses.py]
        
        [train_router.py] -.-> ["hybrid_llm (setup.py)"]
        [notebooks/reward_modeling.py] -.-> ["trl (reqs_data_prep.txt)"]
        [notebooks/generate_llm_responses.py] -.-> ["transformers (reqs_data_prep.txt)"]
    end
```
Sources: [setup.py:1-7](), [notebooks/requirements_data_preparation.txt:1-10](), [requirements.txt:1-3]()

---

