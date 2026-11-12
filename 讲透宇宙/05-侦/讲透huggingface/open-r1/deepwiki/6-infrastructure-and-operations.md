<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/open-r1 · page 6 Infrastructure and Operations · fetched 2026-10-26 -->

# Infrastructure and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [README.md](README.md)
- [slurm/evaluate.slurm](slurm/evaluate.slurm)
- [slurm/train.slurm](slurm/train.slurm)

</details>



This page documents the operational framework that enables large-scale training, evaluation, and deployment in the Open-R1 system. The infrastructure layer includes SLURM-based distributed computing orchestration, development automation tools, vLLM-based model serving, and external code execution services.

The infrastructure supports three primary workloads:
1. **Training Jobs** - Multi-node SFT and GRPO training with vLLM integration
2. **Evaluation Jobs** - Distributed benchmark evaluation with result tracking
3. **Code Execution** - Sandboxed code evaluation for reward functions

For detailed information on specific components, see subsections on SLURM Integration (6.1), Development Tools (6.2), and Model Serving with vLLM (6.3).

## Infrastructure Architecture

Infrastructure components and their relationships in the Open-R1 system
```mermaid
graph TB
    subgraph "Development Layer"
        MAKE["Makefile"]
        INSTALL["make install"]
        STYLE["make style"]
        TEST["make test"]
        EVALUATE["make evaluate"]
    end

    subgraph "SLURM Orchestration Layer"
        TRAIN_SLURM["slurm/train.slurm"]
        EVAL_SLURM["slurm/evaluate.slurm"]
        E2B_ROUTER["slurm/e2b_router.slurm"]
        MORPH_ROUTER["slurm/morph_router.slurm"]
        PISTON_LAUNCHER["slurm/piston/launch_piston_workers.sh"]
        SLURM_SCHEDULER["SLURM Scheduler"]
    end

    subgraph "Training Execution"
        ACCEL_LAUNCH["accelerate launch"]
        SFT_PY["src/open_r1/sft.py"]
        GRPO_PY["src/open_r1/grpo.py"]
        VLLM_SERVE["trl vllm-serve"]
    end

    subgraph "Evaluation Execution"
        LIGHTEVAL["lighteval vllm"]
        VLLM_ENGINE["vLLM Engine"]
        HF_UPLOAD["huggingface-cli upload"]
    end

    subgraph "Code Execution Services"
        E2B_SERVICE["E2B Router Service\nPort 8000"]
        MORPH_SERVICE["Morph Router Service\nPort 8001"]
        PISTON_WORKERS["Piston Workers\nPorts 1234-N"]
    end

    subgraph "External Storage"
        HF_HUB["Hugging Face Hub"]
        WANDB["Weights & Biases"]
    end

    MAKE --> INSTALL
    MAKE --> STYLE
    MAKE --> TEST
    MAKE --> EVALUATE

    TRAIN_SLURM --> SLURM_SCHEDULER
    EVAL_SLURM --> SLURM_SCHEDULER
    E2B_ROUTER --> SLURM_SCHEDULER
    MORPH_ROUTER --> SLURM_SCHEDULER
    PISTON_LAUNCHER --> SLURM_SCHEDULER

    SLURM_SCHEDULER --> ACCEL_LAUNCH
    SLURM_SCHEDULER --> LIGHTEVAL
    SLURM_SCHEDULER --> E2B_SERVICE
    SLURM_SCHEDULER --> MORPH_SERVICE
    SLURM_SCHEDULER --> PISTON_WORKERS

    ACCEL_LAUNCH --> SFT_PY
    ACCEL_LAUNCH --> GRPO_PY
    GRPO_PY --> VLLM_SERVE

    LIGHTEVAL --> VLLM_ENGINE
    LIGHTEVAL --> HF_UPLOAD

    GRPO_PY -.uses.-> E2B_SERVICE
    GRPO_PY -.uses.-> MORPH_SERVICE
    GRPO_PY -.uses.-> PISTON_WORKERS

    SFT_PY --> WANDB
    GRPO_PY --> WANDB
    HF_UPLOAD --> HF_HUB
```

Sources: [Makefile:1-54](), [slurm/train.slurm:1-183](), [slurm/evaluate.slurm:1-84](), [README.md:324-368]()

## SLURM Training Orchestration

The [slurm/train.slurm:1-183]() script orchestrates distributed training jobs across GPU clusters. It handles resource allocation, distributed setup, and optional vLLM server deployment for GRPO training.

### Training Job Execution Flow

Training job architecture with node allocation and distributed configuration
```mermaid
graph TB
    subgraph "Job Submission"
        SBATCH["sbatch slurm/train.slurm"]
        ARGS["--model MODEL\n--task TASK\n--config CONFIG\n--accelerator ACCELERATOR\n--dp DP --tp TP"]
        PARSE["Argument Parsing"]
    end

    subgraph "Configuration Loading"
        CONFIG_FILE["recipes/MODEL/TASK/config_CONFIG.yaml"]
        GRAD_ACC["gradient_accumulation_steps"]
        MODEL_PATH["model_name_or_path"]
        MODEL_REV["model_revision"]
        USE_VLLM_CHECK["Check use_vllm flag"]
    end

    subgraph "Node Allocation"
        SLURM_NNODES["SLURM_NNODES"]
        SLURM_NODELIST["SLURM_JOB_NODELIST"]
        NODE_SPLIT{"use_vllm=true?"}
        VLLM_NODE["Last Node\nvLLM Server"]
        TRAIN_NODES["First N-1 Nodes\nTraining"]
        ALL_NODES["All N Nodes\nTraining"]
    end

    subgraph "vLLM Server Launch"
        SRUN_VLLM["srun --nodes=1 --nodelist=VLLM_NODE"]
        TRL_VLLM["trl vllm-serve"]
        VLLM_ARGS["--model MODEL\n--revision REVISION\n--tensor_parallel_size TP\n--data_parallel_size DP"]
    end

    subgraph "Training Launch"
        ACCEL_CONFIG["recipes/accelerate_configs/ACCELERATOR.yaml"]
        ACCEL_LAUNCH["accelerate launch"]
        DIST_ARGS["--num_machines NUM_NODES\n--num_processes WORLD_SIZE\n--main_process_ip MASTER_ADDR\n--machine_rank SLURM_PROCID"]
        TASK_SCRIPT["src/open_r1/TASK.py --config CONFIG_FILE"]
        SRUN_TRAIN["srun execution"]
    end

    SBATCH --> ARGS
    ARGS --> PARSE
    PARSE --> CONFIG_FILE
    CONFIG_FILE --> GRAD_ACC
    CONFIG_FILE --> MODEL_PATH
    CONFIG_FILE --> MODEL_REV
    CONFIG_FILE --> USE_VLLM_CHECK

    USE_VLLM_CHECK --> SLURM_NNODES
    USE_VLLM_CHECK --> SLURM_NODELIST
    SLURM_NNODES --> NODE_SPLIT
    SLURM_NODELIST --> NODE_SPLIT

    NODE_SPLIT -->|"Yes"| VLLM_NODE
    NODE_SPLIT -->|"Yes"| TRAIN_NODES
    NODE_SPLIT -->|"No"| ALL_NODES

    VLLM_NODE --> SRUN_VLLM
    SRUN_VLLM --> TRL_VLLM
    TRL_VLLM --> VLLM_ARGS

    TRAIN_NODES --> ACCEL_CONFIG
    ALL_NODES --> ACCEL_CONFIG
    ACCEL_CONFIG --> ACCEL_LAUNCH
    ACCEL_LAUNCH --> DIST_ARGS
    DIST_ARGS --> TASK_SCRIPT
    TASK_SCRIPT --> SRUN_TRAIN
```

Sources: [slurm/train.slurm:1-183]()

### Key Configuration Variables

The training script extracts and uses the following configuration:

| Variable | Source | Purpose |
|----------|--------|---------|
| `SLURM_NNODES` | SLURM environment | Total number of allocated nodes |
| `SLURM_JOB_NODELIST` | SLURM environment | List of allocated node names |
| `MASTER_ADDR` | First node in `NODELIST` | IP address for distributed training coordination |
| `MASTER_PORT` | Fixed at `6000` | Port for distributed training coordination |
| `WORLD_SIZE` | `NUM_NODES * GPUS_PER_NODE` | Total number of processes across all nodes |
| `USE_VLLM` | Extracted from config YAML | Whether to launch separate vLLM server |

Sources: [slurm/train.slurm:115-136]()

### GRPO with vLLM Server

For GRPO training with `use_vllm: true` in the config, the script implements an N+1 node architecture:

1. **vLLM Server Node**: Last node in allocation runs `trl vllm-serve` with tensor and data parallelism
2. **Training Nodes**: Remaining N-1 nodes run the training script
3. **Communication**: Training nodes connect to vLLM server via `--vllm_server_host` argument

This separation enables efficient generation during GRPO without blocking training processes.

Sources: [slurm/train.slurm:128-136](), [README.md:230-236]()

## SLURM Evaluation Orchestration

The [slurm/evaluate.slurm:1-84]() script manages distributed model evaluation using `lighteval` and `vLLM`. It handles parallelism configuration, result collection, and automatic upload to Hugging Face Hub.

### Evaluation Job Execution Flow

Evaluation job workflow from launch to results upload
```mermaid
graph TB
    subgraph "Job Invocation"
        EVAL_SUBMIT["sbatch slurm/evaluate.slurm"]
        EVAL_ARGS["TASK_NAME TASKS MODEL_ID MODEL_REVISION\nTENSOR_PARALLEL TRUST_REMOTE_CODE"]
    end

    subgraph "Environment Setup"
        MODULE_LOAD["module load cuda/12.4"]
        WEKA_REFRESH["find -L /fsx/h4/ | weka fs tier fetch"]
        ENV_ACTIVATE["source openr1/bin/activate"]
        VLLM_ENV["export VLLM_WORKER_MULTIPROC_METHOD=spawn"]
    end

    subgraph "Parallelism Configuration"
        PARALLEL_CHECK{"TENSOR_PARALLEL?"}
        TENSOR_CONFIG["tensor_parallel_size=NUM_GPUS"]
        DATA_CONFIG["data_parallel_size=NUM_GPUS"]
    end

    subgraph "LightEval Execution"
        MODEL_ARGS["model_name, revision, trust_remote_code,\ndtype=bfloat16, max_model_length=32768,\ngpu_memory_utilization=0.8"]
        LIGHTEVAL_CMD["lighteval vllm"]
        LIGHTEVAL_FLAGS["--use-chat-template\n--output-dir OUTPUT_DIR\n--save-details\n--system-prompt (optional)"]
    end

    subgraph "Results Processing"
        JSON_RESULTS["Find *.json in results/"]
        PARQUET_DETAILS["Find *.parquet in details/"]
        HF_UPLOAD_JSON["huggingface-cli upload"]
        UPLOAD_DETAILS["python scripts/upload_details.py"]
        CLEANUP["rm -rf OUTPUT_DIR"]
    end

    subgraph "Storage Repositories"
        LEADERBOARD["open-r1/open-r1-eval-leaderboard\n(Space)"]
        DETAILS_REPO["open-r1/details-MODEL_NAME\n(Dataset)"]
    end

    EVAL_SUBMIT --> EVAL_ARGS
    EVAL_ARGS --> MODULE_LOAD
    MODULE_LOAD --> WEKA_REFRESH
    WEKA_REFRESH --> ENV_ACTIVATE
    ENV_ACTIVATE --> VLLM_ENV

    VLLM_ENV --> PARALLEL_CHECK
    PARALLEL_CHECK -->|"True"| TENSOR_CONFIG
    PARALLEL_CHECK -->|"False"| DATA_CONFIG

    TENSOR_CONFIG --> MODEL_ARGS
    DATA_CONFIG --> MODEL_ARGS
    MODEL_ARGS --> LIGHTEVAL_CMD
    LIGHTEVAL_CMD --> LIGHTEVAL_FLAGS

    LIGHTEVAL_FLAGS --> JSON_RESULTS
    LIGHTEVAL_FLAGS --> PARQUET_DETAILS

    JSON_RESULTS --> HF_UPLOAD_JSON
    PARQUET_DETAILS --> UPLOAD_DETAILS

    HF_UPLOAD_JSON --> LEADERBOARD
    UPLOAD_DETAILS --> DETAILS_REPO

    HF_UPLOAD_JSON --> CLEANUP
    UPLOAD_DETAILS --> CLEANUP
```

Sources: [slurm/evaluate.slurm:1-84]()

### Parallelism Strategies

The evaluation script supports two parallelism modes determined by the `TENSOR_PARALLEL` argument:

| Mode | Configuration | Use Case |
|------|---------------|----------|
| Data Parallel | `data_parallel_size=NUM_GPUS` | Smaller models that fit on single GPU; increases throughput |
| Tensor Parallel | `tensor_parallel_size=NUM_GPUS` | Large models requiring sharding across multiple GPUs |

When tensor parallelism is enabled, the environment variable `VLLM_WORKER_MULTIPROC_METHOD=spawn` is set to avoid process spawn issues with vLLM.

Sources: [slurm/evaluate.slurm:37-42]()

### Results Upload

Evaluation results are automatically uploaded to two Hugging Face repositories:

1. **Leaderboard Space** (`open-r1/open-r1-eval-leaderboard`): JSON files containing aggregate metrics
2. **Details Dataset** (`open-r1/details-{model_name}`): Parquet files with per-sample predictions

The upload includes retry logic with up to 20 attempts per file to handle transient failures.

Sources: [slurm/evaluate.slurm:44-78]()

## Development Automation

The [Makefile:1-54]() provides standardized commands for development environment setup, code quality checks, testing, and local evaluation.

### Development Targets

Development workflow operations and their implementations
```mermaid
graph TB
    subgraph "Environment Setup"
        MAKE_INSTALL["make install"]
        UV_VENV["uv venv openr1 --python 3.11"]
        UV_PIP["uv pip install --upgrade pip"]
        VLLM_INSTALL["uv pip install vllm==0.8.5.post1"]
        FLASH_ATTN["uv pip install flash-attn --no-build-isolation"]
        DEV_INSTALL["uv pip install -e .[dev]"]
    end

    subgraph "Code Quality"
        MAKE_STYLE["make style"]
        RUFF_FORMAT["ruff format --line-length 119"]
        ISORT["isort check_dirs"]
        MAKE_QUALITY["make quality"]
        RUFF_CHECK["ruff check"]
        ISORT_CHECK["isort --check-only"]
        FLAKE8["flake8 --max-line-length 119"]
    end

    subgraph "Testing"
        MAKE_TEST["make test"]
        PYTEST["pytest -sv --ignore=tests/slow/"]
        MAKE_SLOW["make slow_test"]
        PYTEST_SLOW["pytest -sv -vv tests/slow/"]
    end

    subgraph "Local Evaluation"
        MAKE_EVAL["make evaluate"]
        PARALLEL_LOGIC["Parallelism configuration"]
        LIGHTEVAL["lighteval vllm"]
    end

    MAKE_INSTALL --> UV_VENV
    UV_VENV --> UV_PIP
    UV_PIP --> VLLM_INSTALL
    VLLM_INSTALL --> FLASH_ATTN
    FLASH_ATTN --> DEV_INSTALL

    MAKE_STYLE --> RUFF_FORMAT
    MAKE_STYLE --> ISORT

    MAKE_QUALITY --> RUFF_CHECK
    MAKE_QUALITY --> ISORT_CHECK
    MAKE_QUALITY --> FLAKE8

    MAKE_TEST --> PYTEST
    MAKE_SLOW --> PYTEST_SLOW

    MAKE_EVAL --> PARALLEL_LOGIC
    PARALLEL_LOGIC --> LIGHTEVAL
```

Sources: [Makefile:1-54]()

### Makefile Target Reference

| Target | Command | Purpose |
|--------|---------|---------|
| `install` | `make install` | Creates Python 3.11 virtual environment and installs all dependencies including vLLM 0.8.5.post1 and Flash Attention |
| `style` | `make style` | Formats code with ruff (line length 119) and organizes imports with isort |
| `quality` | `make quality` | Runs ruff, isort, and flake8 checks without modifying files |
| `test` | `make test` | Executes fast unit tests, excluding slow tests |
| `slow_test` | `make slow_test` | Runs complete test suite including slow integration tests |
| `evaluate` | `make evaluate MODEL=... TASK=...` | Runs local evaluation with configurable parallelism |

Sources: [Makefile:10-53]()

### Local Evaluation Usage

The `evaluate` target provides flexible evaluation on local machines with support for data and tensor parallelism:

```bash
# Single GPU evaluation
make evaluate MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B TASK=aime24

# Data parallelism (model replicated across GPUs)
make evaluate MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B TASK=math_500 PARALLEL=data NUM_GPUS=8

# Tensor parallelism (model sharded across GPUs)
make evaluate MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-32B TASK=gpqa PARALLEL=tensor NUM_GPUS=8

# LiveCodeBench (special case)
make evaluate MODEL=open-r1/OpenR1-Distill-7B TASK=lcb PARALLEL=data NUM_GPUS=8
```

The target automatically constructs appropriate `MODEL_ARGS` for `lighteval vllm` based on the parallelism mode.

Sources: [Makefile:35-53](), [README.md:507-525]()

## Distributed Computing with Slurm

Open-R1 utilizes Slurm for orchestrating distributed training, evaluation, and model serving across GPU clusters. The repository includes several Slurm scripts to automate these operations.

### Model Serving Infrastructure

The infrastructure includes scripts for serving fine-tuned models using SGLang and vLLM. Two primary serving architectures are supported:

#### SGLang Serving Architecture

```mermaid
graph TD
    subgraph "SGLang Model Serving"
        direction TB
        SR["serve_router.slurm"]
        S1["serve_r1.slurm\nNode 1"]
        S2["serve_r1.slurm\nNode 2"]
        ROUTER["SGLang Router\nPort 39876"]
        MODEL1["SGLang Server\nNode 1\nPort 39877"]
        MODEL2["SGLang Server\nNode 2\nPort 39877"]
        CLIENT["Client Application"]
    end
    
    SR -->|"launches"| ROUTER
    S1 -->|"launches"| MODEL1
    S2 -->|"launches"| MODEL2
    
    MODEL1 -->|"register"| ROUTER
    MODEL2 -->|"register"| ROUTER
    
    CLIENT -->|"API requests"| ROUTER
    ROUTER -->|"load balance"| MODEL1
    ROUTER -->|"load balance"| MODEL2
```

The SGLang serving architecture consists of:
- A router component running on a CPU node (launched by `serve_router.slurm`)
- Multiple model server instances running across GPU nodes (launched by `serve_r1.slurm`)
- Tensor parallelism (TP=16) across 2 nodes with 8 GPUs each
- Health check system to ensure continuous operation

Sources: [slurm/serve_r1.slurm:1-109](), [slurm/serve_router.slurm:1-45]()

#### vLLM Serving Architecture

```mermaid
graph TD
    subgraph "vLLM Model Serving"
        direction TB
        SLURM["serve_r1_vllm.slurm"]
        RAY_HEAD["Ray Head Node"]
        RAY_WORKER1["Ray Worker Node 1"]
        RAY_WORKER2["Ray Worker Node 2"]
        RAY_WORKER3["Ray Worker Node 3"]
        VLLM["vLLM Server"]
        CLIENT["Client Application"]
    end
    
    SLURM -->|"launches"| RAY_HEAD
    SLURM -->|"launches"| RAY_WORKER1
    SLURM -->|"launches"| RAY_WORKER2
    SLURM -->|"launches"| RAY_WORKER3
    
    RAY_HEAD -->|"ray job submit"| VLLM
    RAY_WORKER1 -->|"execution"| VLLM
    RAY_WORKER2 -->|"execution"| VLLM
    RAY_WORKER3 -->|"execution"| VLLM
    
    CLIENT -->|"API requests"| VLLM
```

The vLLM serving architecture is built on Ray, providing:
- A distributed Ray cluster across multiple nodes
- Tensor parallelism (TP=8) and pipeline parallelism (PP=4)
- Support for very long sequences (up to 32k tokens)
- Health check and monitoring system

Sources: [slurm/experimental/serve_r1_vllm.slurm:1-132]()

## Infrastructure Configuration Options

The infrastructure components support various configuration options for different deployment scenarios:

### Model Serving Configuration

| Parameter | SGLang | vLLM | Description |
|-----------|--------|------|-------------|
| Tensor Parallelism | 16 | 8 | Number of GPUs to split model tensor across |
| Pipeline Parallelism | N/A | 4 | Number of pipeline stages |
| Max Context Length | 32768 | 32768 | Maximum context window size |
| Max Running Requests | 56 | 128 | Number of concurrent requests |
| Memory Utilization | N/A | 0.90 | GPU memory utilization factor |
| Distributed Backend | Custom | Ray | Framework for distributed execution |

Sources: [slurm/serve_r1.slurm:46-58](), [slurm/experimental/serve_r1_vllm.slurm:72-88]()

## Integration with Training Pipeline

The infrastructure components are designed to support the entire model training and evaluation pipeline:

```mermaid
flowchart LR
    subgraph "Infrastructure Integration"
        direction TB
        MAKE["Makefile"]
        SLURM["Slurm Scripts"]
    end
    
    subgraph "Training Pipeline"
        direction TB
        GEN["Data Generation"]
        SFT["Supervised Fine-Tuning"]
        GRPO["GRPO Training"]
        EVAL["Evaluation"]
        SERVE["Model Serving"]
    end
    
    MAKE -->|"automation"| GEN
    MAKE -->|"automation"| SFT
    MAKE -->|"automation"| GRPO
    MAKE -->|"automation"| EVAL
    
    SLURM -->|"distributed execution"| GEN
    SLURM -->|"distributed execution"| SFT
    SLURM -->|"distributed execution"| GRPO
    SLURM -->|"distributed execution"| EVAL
    SLURM -->|"distributed execution"| SERVE
    
    GEN --> SFT
    SFT --> GRPO
    GRPO --> EVAL
    EVAL --> SERVE
```

Sources: [Makefile:1-52](), [slurm/serve_r1.slurm:1-109](), [slurm/experimental/serve_r1_vllm.slurm:1-132]()

## Usage Examples

### Running Evaluation with Tensor Parallelism

To evaluate a model using tensor parallelism across 8 GPUs:

```bash
make evaluate PARALLEL=tensor NUM_GPUS=8 MODEL="deepseek-ai/DeepSeek-R1" TASK="gpqa"
```

This command:
1. Sets up the appropriate tensor parallelism arguments
2. Configures vLLM to use multiprocess worker method
3. Runs LightEval with the specified model and task

Sources: [Makefile:33-52]()

### Serving a Model with SGLang

To serve a DeepSeek-R1 model across 2 nodes with 8 GPUs each:

```bash
sbatch slurm/serve_r1.slurm -m "/path/to/model/checkpoint" -e "sglang_env_name"
```

Sources: [slurm/serve_r1.slurm:1-109](), [slurm/README.md:1-30]()

## Summary

The infrastructure components of Open-R1 provide the foundation for running large-scale LLM training and serving operations. They include:

1. Makefile automation for common development and evaluation tasks
2. Slurm scripts for distributed computing across GPU clusters
3. Model serving capabilities using both SGLang and vLLM
4. Configuration options for different deployment scenarios

This infrastructure enables efficient training, evaluation, and serving of large language models like DeepSeek-R1 at scale.

---

