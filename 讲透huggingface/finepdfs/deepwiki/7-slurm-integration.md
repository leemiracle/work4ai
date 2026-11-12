<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/finepdfs · page 7 SLURM Integration · fetched 2026-10-26 -->

# SLURM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ablations/evaluations/launch_evals.py](ablations/evaluations/launch_evals.py)
- [ablations/tokenization/tk_thom.py](ablations/tokenization/tk_thom.py)
- [ablations/training/training_script.py](ablations/training/training_script.py)

</details>



This document describes how the FinePDFs repository integrates with SLURM (Simple Linux Utility for Resource Management) workload manager for distributed computing across GPU clusters. The system uses SLURM extensively for training, evaluation, and data processing tasks.

**Scope:** This page covers SLURM job submission patterns, resource management, job dependencies, and environment configuration. For training-specific configuration details, see [Training Infrastructure](#3). For evaluation orchestration, see [Evaluation Infrastructure](#4). For tokenization pipeline details, see [Tokenization Pipeline](#2.3).

## Overview

The FinePDFs system leverages SLURM for three primary workflows:

1. **Training Jobs** - Single or multi-node distributed training with nanotron
2. **Evaluation Jobs** - SLURM array jobs for parallel checkpoint evaluation
3. **Tokenization Jobs** - CPU-based distributed data processing via DataTrove's `SlurmPipelineExecutor`

All SLURM integration uses the `hopper-prod` or `hopper-cpu` partitions and supports QoS-based priority scheduling.

Sources: [ablations/training/training_script.py:1-432](), [ablations/evaluations/launch_evals.py:1-512](), [ablations/tokenization/tk_thom.py:1-286]()

## Core SLURM Integration Architecture

```mermaid
graph TB
    subgraph "Python Scripts"
        TRAIN_SCRIPT["training_script.py<br/>launch_slurm_job()"]
        EVAL_SCRIPT["launch_evals.py<br/>launch_slurm_job()"]
        TOK_SCRIPT["tk_thom.py<br/>SlurmPipelineExecutor"]
    end
    
    subgraph "SLURM Job Generation"
        SBATCH_GEN["SBATCH Script<br/>Generation"]
        TEMPFILE["tempfile.NamedTemporaryFile<br/>or Persistent Script"]
        CHMOD["chmod 0o755"]
    end
    
    subgraph "SLURM Submission"
        SBATCH_CMD["subprocess.check_output()<br/>sbatch command"]
        SRUN_CMD["subprocess.Popen()<br/>srun command"]
        JOB_ID["Slurm Job ID<br/>Extraction"]
    end
    
    subgraph "SLURM Cluster"
        SCHEDULER["SLURM Scheduler"]
        HOPPER_PROD["hopper-prod partition<br/>GPU nodes"]
        HOPPER_CPU["hopper-cpu partition<br/>CPU nodes"]
        QOS["QoS Management<br/>normal/high"]
    end
    
    subgraph "Job Execution"
        ENV_SETUP["Environment Setup<br/>SLURM_* variables"]
        MODULE_LOAD["module load cuda/12.4"]
        DISTRIBUTED["Distributed Launch<br/>torch.distributed.run"]
        ARRAY_TASK["Array Task Execution<br/>SLURM_ARRAY_TASK_ID"]
    end
    
    subgraph "Storage"
        LOGS["Log Files<br/>/shared/USER/logs/"]
        SCRIPTS["Launch Scripts<br/>/shared/USER/logs/.../launch_scripts"]
        CONFIGS["Config Files<br/>/shared/USER/logs/.../launch-configs"]
        SCRATCH["/scratch/USER<br/>Local Node Storage"]
    end
    
    TRAIN_SCRIPT --> SBATCH_GEN
    EVAL_SCRIPT --> SBATCH_GEN
    TOK_SCRIPT --> SBATCH_GEN
    
    SBATCH_GEN --> TEMPFILE
    TEMPFILE --> CHMOD
    CHMOD --> SBATCH_CMD
    CHMOD --> SRUN_CMD
    
    SBATCH_CMD --> JOB_ID
    JOB_ID --> SCHEDULER
    SRUN_CMD --> SCHEDULER
    
    SCHEDULER --> QOS
    QOS --> HOPPER_PROD
    QOS --> HOPPER_CPU
    
    HOPPER_PROD --> ENV_SETUP
    HOPPER_CPU --> ENV_SETUP
    ENV_SETUP --> MODULE_LOAD
    MODULE_LOAD --> DISTRIBUTED
    MODULE_LOAD --> ARRAY_TASK
    
    ENV_SETUP -.-> LOGS
    SBATCH_GEN -.-> SCRIPTS
    SBATCH_GEN -.-> CONFIGS
    DISTRIBUTED -.-> SCRATCH
```

Sources: [ablations/training/training_script.py:192-220](), [ablations/evaluations/launch_evals.py:87-111]()

## Job Submission Pattern

The repository implements a common `launch_slurm_job()` helper function pattern for submitting SLURM jobs:

### Training Job Submission

The training script generates and submits SBATCH scripts dynamically:

```mermaid
sequenceDiagram
    participant User
    participant training_script.py
    participant launch_slurm_job
    participant File System
    participant SLURM

    User->>training_script.py: python training_script.py data run_name
    training_script.py->>training_script.py: Load MODEL_CONFIG
    training_script.py->>training_script.py: Update config with args
    training_script.py->>training_script.py: Generate SBATCH script
    training_script.py->>launch_slurm_job: sbatch_script, job_id, nodes, ...
    
    alt job_id provided (srun mode)
        launch_slurm_job->>File System: Write script to SLURM_SCRIPT_PATH
        launch_slurm_job->>SLURM: srun --jobid job_id ... script.sh
        alt background mode
            launch_slurm_job->>SLURM: Popen (non-blocking)
        else foreground mode
            launch_slurm_job->>SLURM: check_call (blocking)
        end
    else no job_id (sbatch mode)
        launch_slurm_job->>File System: Write to tempfile or persistent
        launch_slurm_job->>SLURM: sbatch script.sh
        SLURM->>launch_slurm_job: Job ID
        launch_slurm_job->>training_script.py: Job ID
    end
    
    training_script.py->>User: Launched with Slurm job id=...
```

**Key Functions:**

- `launch_slurm_job()` - [ablations/training/training_script.py:192-220]()
  - Writes SBATCH script to file system
  - Executes `sbatch` or `srun` command
  - Extracts and returns SLURM job ID
  - Supports both foreground and background execution

**SBATCH Script Generation:**

The training script generates a complete SBATCH script with:

```
#SBATCH --job-name={job_name}
#SBATCH --nodes={args.nodes}
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task={NUM_CPUS_IN_NODE}  # 88
#SBATCH --gres=gpu:{NUM_GPUS}                # 8
#SBATCH --partition=hopper-prod
#SBATCH --qos={args.priority}
#SBATCH --time={args.time}
#SBATCH --exclusive
#SBATCH --dependency=afterok:{dependency_job_id}
```

Sources: [ablations/training/training_script.py:353-366]()

### Evaluation Job Submission

Evaluations use SLURM array jobs for parallel checkpoint processing:

```mermaid
graph LR
    subgraph "Job Preparation"
        GET_CKPTS["get_checkpoints_to_run()<br/>Discover S3 checkpoints"]
        FILTER_TASKS["get_evaluated_tasks()<br/>Filter completed tasks"]
        BUILD_ARRAYS["Build bash arrays<br/>CHECKPOINTS_LIST<br/>TASKS_LIST"]
    end
    
    subgraph "SBATCH Generation"
        ARRAY_CONFIG["#SBATCH --array=0-N%parallel"]
        ARRAY_VAR["NSTEP=SLURM_ARRAY_TASK_ID"]
        TASK_SELECT["STEP=CHECKPOINTS_LIST[NSTEP]<br/>TASKS=TASKS_LIST[NSTEP]"]
    end
    
    subgraph "Array Job Execution"
        TASK_0["Task 0<br/>Checkpoint A<br/>GPU 0-7"]
        TASK_1["Task 1<br/>Checkpoint B<br/>GPU 0-7"]
        TASK_N["Task N<br/>Checkpoint N<br/>GPU 0-7"]
    end
    
    GET_CKPTS --> FILTER_TASKS
    FILTER_TASKS --> BUILD_ARRAYS
    BUILD_ARRAYS --> ARRAY_CONFIG
    ARRAY_CONFIG --> ARRAY_VAR
    ARRAY_VAR --> TASK_SELECT
    
    TASK_SELECT --> TASK_0
    TASK_SELECT --> TASK_1
    TASK_SELECT --> TASK_N
```

**Array Job Configuration:**

```bash
#SBATCH --array=0-{len(checkpoints_with_tasks) - 1}%{args.parallel}
```

This creates one array task per checkpoint, with `%{args.parallel}` limiting concurrent execution (default 5).

Sources: [ablations/evaluations/launch_evals.py:381-393]()

**Array Task Indexing:**

Each array task uses `SLURM_ARRAY_TASK_ID` to select its checkpoint and tasks:

```bash
CHECKPOINTS_LIST=("checkpoint_500" "checkpoint_1000" ...)
TASKS_LIST=("task1|task2|..." "task3|task4|..." ...)

NSTEP=$((SLURM_ARRAY_TASK_ID))
STEP=${CHECKPOINTS_LIST[$NSTEP]}
TASKS_TO_EVAL=${TASKS_LIST[$NSTEP]}
```

Sources: [ablations/evaluations/launch_evals.py:423-430]()

### Tokenization Job Submission

Tokenization uses DataTrove's `SlurmPipelineExecutor`:

```python
from datatrove.executor import SlurmPipelineExecutor

tokenizer_executor = SlurmPipelineExecutor(
    job_name=f"tok-{output_name}",
    pipeline=[
        JsonlReader(...),
        SamplerFilter(...),
        DocumentTokenizer(...)
    ],
    tasks=args.n_tasks,           # Number of parallel tasks
    time="20:00:00",
    partition="hopper-cpu",
    logging_dir=f"/shared/user/logs/...",
    cpus_per_task=8,
    mem_per_cpu_gb=2,
    qos=args.qos,
    depends_job_id=args.dep_job_id
)
tokenizer_executor.run()
```

The `SlurmPipelineExecutor` internally:
1. Generates an SBATCH script for each task
2. Submits array jobs to SLURM
3. Manages pipeline execution across tasks

Sources: [ablations/tokenization/tk_thom.py:217-248]()

## Resource Management

### Cluster Configuration

The system targets specific cluster partitions with fixed resource configurations:

| Constant | Value | Usage |
|----------|-------|-------|
| `PARTITION` | `"hopper-prod"` | GPU training/evaluation partition |
| `CPUS_PER_NODE` | `88` | CPUs per node for training/eval |
| `GPUS_PER_NODE` | `8` | GPUs per node |
| `NODES` | `1` (default) | Multi-node for training |

Sources: [ablations/evaluations/launch_evals.py:24-27](), [ablations/training/training_script.py:22-23]()

### Training Resource Allocation

Training jobs request:

```bash
#SBATCH --nodes={args.nodes}
#SBATCH --ntasks-per-node=1          # Crucial - only 1 task per node
#SBATCH --cpus-per-task=88
#SBATCH --gres=gpu:8
#SBATCH --partition=hopper-prod
#SBATCH --exclusive                   # Exclusive node access
```

The `--exclusive` flag ensures no other jobs share the node.

Sources: [ablations/training/training_script.py:353-365]()

### Evaluation Resource Allocation

Evaluation array jobs allocate resources per task:

```bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --partition=hopper-prod
#SBATCH --array=0-N%5                 # Max 5 concurrent tasks
#SBATCH --gres=gpu:{args.gpus}        # Default 8
#SBATCH --time=1:50:00                # Per-task timeout
#SBATCH --cpus-per-task=88
```

Sources: [ablations/evaluations/launch_evals.py:383-390]()

### Tokenization Resource Allocation

Tokenization uses CPU-only nodes:

```python
partition="hopper-cpu"
cpus_per_task=8
mem_per_cpu_gb=2
time="20:00:00"
```

Sources: [ablations/tokenization/tk_thom.py:240-243]()

## Job Dependencies and Scheduling

### Dependency Syntax

The system supports SLURM job dependencies via the `--dependency` flag:

```bash
#SBATCH --dependency=afterok:JOB_ID
```

**Training Dependencies:**

```python
parser.add_argument("-d", help="Dependency job", type=str, default=None)

# In SBATCH script:
{"#SBATCH --dependency=afterok:" + args.d if args.d else ""}
```

Sources: [ablations/training/training_script.py:226](), [ablations/training/training_script.py:365]()

**Evaluation Dependencies:**

```python
deps = []
if args.d:
    deps.append(f"afterok:{args.d}")
if args.run_all and job_id:
    deps.append(f"afterany:{job_id}")

# In SBATCH script:
{"#SBATCH --dependency=" + ",".join(deps) if deps else ""}
```

Sources: [ablations/evaluations/launch_evals.py:368-393]()

**Tokenization Dependencies:**

The `SlurmPipelineExecutor` supports `depends_job_id` and `depends` parameters:

```python
depends_job_id=args.dep_job_id  # Dependency on another job ID

# For merger job:
depends=tokenizer_executor      # Dependency on another executor
```

Sources: [ablations/tokenization/tk_thom.py:247](), [ablations/tokenization/tk_thom.py:281]()

### QoS (Quality of Service)

Priority scheduling is controlled via the `--qos` flag:

| QoS | Usage |
|-----|-------|
| `normal` | Default priority |
| `high` | Higher priority (limited quota) |

```bash
#SBATCH --qos={args.qos}
```

Sources: [ablations/evaluations/launch_evals.py:286](), [ablations/training/training_script.py:230]()

### Sequential Job Execution

The evaluation script supports sequential execution via `--run-all`:

```python
if args.run_all and job_id:
    deps.append(f"afterany:{job_id}")
```

This chains jobs so each model evaluation waits for the previous one to complete (success or failure).

Sources: [ablations/evaluations/launch_evals.py:371-372]()

## SLURM Environment Variables

### Standard SLURM Variables Used

The system reads and uses these SLURM-provided environment variables:

```mermaid
graph TB
    subgraph "Node Discovery"
        NODELIST["SLURM_JOB_NODELIST<br/>List of allocated nodes"]
        HOSTNAMES["scontrol show hostnames<br/>Parse node names"]
        MASTER_ADDR["MASTER_ADDR<br/>First node hostname"]
    end
    
    subgraph "Job Identification"
        JOB_ID["SLURM_JOB_ID<br/>Unique job identifier"]
        PROC_ID["SLURM_PROCID<br/>Process rank (0-N)"]
        NODE_NAME["SLURMD_NODENAME<br/>Current node name"]
    end
    
    subgraph "Array Job Variables"
        ARRAY_TASK_ID["SLURM_ARRAY_TASK_ID<br/>Current array task index"]
        ARRAY_JOB_ID["SLURM_ARRAY_JOB_ID<br/>Parent array job ID"]
    end
    
    subgraph "Distributed Training Setup"
        MASTER_PORT["MASTER_PORT<br/>Random port 1024-65535"]
        COUNT_NODE["COUNT_NODE<br/>wc -l on hostnames"]
        NPROC["--nproc_per_node<br/>GPUs per node"]
        NNODES["--nnodes<br/>Total nodes"]
    end
    
    NODELIST --> HOSTNAMES
    HOSTNAMES --> MASTER_ADDR
    HOSTNAMES --> COUNT_NODE
    
    JOB_ID --> MASTER_PORT
    PROC_ID --> NPROC
    
    ARRAY_TASK_ID --> ARRAY_JOB_ID
    
    MASTER_ADDR --> NPROC
    MASTER_PORT --> NPROC
    COUNT_NODE --> NNODES
```

**Training Environment Setup:**

```bash
export HOSTNAMES=`scontrol show hostnames "$SLURM_JOB_NODELIST"`
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT={random_port}
export COUNT_NODE=`scontrol show hostnames "$SLURM_JOB_NODELIST" | wc -l`
```

Sources: [ablations/training/training_script.py:380-383]()

**Evaluation Environment Setup:**

```bash
export HOSTNAMES=`scontrol show hostnames "$SLURM_JOB_NODELIST"`
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT={master_port}
export COUNT_NODE=`scontrol show hostnames "$SLURM_JOB_NODELIST" | wc -l`

# Array-specific:
NSTEP=$((SLURM_ARRAY_TASK_ID))
STEP=${CHECKPOINTS_LIST[$NSTEP]}
```

Sources: [ablations/evaluations/launch_evals.py:410-428]()

### Custom Environment Variables

The system sets additional environment variables:

```bash
# Scratch space for temporary data
export TMPDIR=/scratch/{USER}/tmp
mkdir -p $TMPDIR

# HuggingFace cache location
export HF_DATASETS_OFFLINE={0|1}

# CUDA configuration
export CUDA_DEVICE_MAX_CONNECTIONS="1"
```

Sources: [ablations/evaluations/launch_evals.py:399](), [ablations/training/training_script.py:385-386]()

## Distributed Training Launch

Training jobs use PyTorch's distributed launcher with SLURM integration:

```mermaid
graph TB
    subgraph "SLURM Job Script"
        SBATCH["SBATCH directives<br/>Resource allocation"]
        ENV_SETUP["Environment setup<br/>SLURM variables"]
        MODULE["module load cuda/12.4"]
    end
    
    subgraph "PyTorch Distributed Launch"
        LAUNCHER["torch.distributed.run<br/>--nproc_per_node 8<br/>--nnodes COUNT_NODE"]
        RDZV["--rdzv-backend c10d<br/>--rdzv-endpoint MASTER_ADDR:PORT<br/>--rdzv-id SLURM_JOB_ID"]
        RANK["--node_rank SLURM_PROCID<br/>--role SLURMD_NODENAME"]
    end
    
    subgraph "Training Execution"
        NANOTRON["run_train.py<br/>--config-file config.yaml"]
        PROCESSES["8 processes per node<br/>Rank 0-7 on each node"]
    end
    
    SBATCH --> ENV_SETUP
    ENV_SETUP --> MODULE
    MODULE --> LAUNCHER
    LAUNCHER --> RDZV
    RDZV --> RANK
    RANK --> NANOTRON
    NANOTRON --> PROCESSES
```

**Launch Command:**

```bash
export LAUNCHER="python -u -m torch.distributed.run \
    --nproc_per_node 8 \
    --nnodes $COUNT_NODE \
    --rdzv-backend c10d \
    --rdzv-endpoint $MASTER_ADDR:$MASTER_PORT \
    --rdzv-id $SLURM_JOB_ID \
    --node_rank $SLURM_PROCID \
    --role $SLURMD_NODENAME: \
    --max_restarts 0 \
    --tee 3 \
    "

CMD="{NANOTRON_PATH}/run_train.py --config-file {config_path}"

bash -c "$LAUNCHER $CMD"
```

Key parameters:
- `--rdzv-backend c10d` - Use PyTorch's c10d rendezvous backend
- `--rdzv-endpoint` - Master node address for coordination
- `--rdzv-id` - Unique ID for this training run (SLURM job ID)
- `--node_rank` - Process ID determines node rank
- `--max_restarts 0` - Don't automatically restart on failure

Sources: [ablations/training/training_script.py:397-415]()

## Log Management

### Log File Organization

The system creates structured log directories:

```mermaid
graph TB
    subgraph "Training Logs"
        TRAIN_ROOT["/shared/USER/logs/pdf_project/experiments/training/"]
        TRAIN_LOGS["logs/{run_name}/<br/>train-{timestamp}-{job_id}"]
        TRAIN_CONFIGS["launch-configs/{run_name}/<br/>{timestamp}.yaml"]
        TRAIN_SCRIPTS["slurm-scripts/{run_name}/<br/>{job_id}-{timestamp}.sh"]
    end
    
    subgraph "Evaluation Logs"
        EVAL_ROOT["/shared/USER/logs/pdf_project/experiments/evals/"]
        EVAL_LOGS["logs/{model_name}/logs/multi-step/<br/>eval-%A_%a.out"]
        EVAL_LAUNCH["logs/{model_name}/launch_scripts/multi-step/"]
        EVAL_CONFIG["logs/{model_name}/model_config/multi-step/"]
    end
    
    subgraph "Tokenization Logs"
        TOK_ROOT["/shared/user/logs/pdf_project/experiments/"]
        TOK_LOGS["tokenization/{output_name}/tokenized/"]
        TOK_MERGED["tokenized/{output_name}/tokenized_merged/"]
    end
    
    TRAIN_ROOT --> TRAIN_LOGS
    TRAIN_ROOT --> TRAIN_CONFIGS
    TRAIN_ROOT --> TRAIN_SCRIPTS
    
    EVAL_ROOT --> EVAL_LOGS
    EVAL_ROOT --> EVAL_LAUNCH
    EVAL_ROOT --> EVAL_CONFIG
    
    TOK_ROOT --> TOK_LOGS
    TOK_ROOT --> TOK_MERGED
```

**Training Log Paths:**

```python
TRAINING_LOGS_PATH = f"/shared/{USER}/logs/pdf_project/experiments/training/logs"
LAUNCH_CONFIGS_PATH = f"/shared/{USER}/logs/pdf_project/experiments/training/launch-configs"
SLURM_SCRIPT_PATH = f"/shared/{USER}/logs/pdf_project/experiments/training/slurm-scripts"

# SBATCH directive:
#SBATCH --output={TRAINING_LOGS_PATH}/{run_name}/train-{timestamp}-%x-%j
```

Sources: [ablations/training/training_script.py:14-20](), [ablations/training/training_script.py:360]()

**Evaluation Log Paths:**

Array jobs use `%A` (array job ID) and `%a` (array task ID):

```python
EVAL_LOGS_PATH = f"/shared/{USER}/logs/pdf_project/experiments/evals/logs"

eval_logs_path = os.path.join(
    EVAL_LOGS_PATH, 
    formatted_model_name, 
    "logs", 
    "multi-step"
)

#SBATCH --output={eval_logs_path}/eval-%A_%a.out
#SBATCH --error={eval_logs_path}/eval-%A_%a.out
```

Sources: [ablations/evaluations/launch_evals.py:19](), [ablations/evaluations/launch_evals.py:337-391]()

## Scratch Space Management

### Local Node Storage

All jobs use `/scratch/{USER}` for temporary data:

```bash
export TMPDIR=/scratch/{USER}/tmp
mkdir -p $TMPDIR
```

**Training Dataset Download:**

For S3 datasets, training jobs download to scratch before training:

```bash
LOCAL_DATASET_PATH=/scratch/{USER}/dataset/{run_name}/
{S5CMD_PATH} cp 's3://bucket/data/*' $LOCAL_DATASET_PATH

# ... training happens ...

# Cleanup after training:
rm -rf $LOCAL_DATASET_PATH
```

Sources: [ablations/training/training_script.py:253](), [ablations/training/training_script.py:345-348](), [ablations/training/training_script.py:419-421]()

**Evaluation Checkpoint Download:**

Each array task downloads its checkpoint to a unique scratch directory:

```bash
RANDOM_NUMBER=$((RANDOM % 60 + 5))
LOCAL_DOWNLOAD_CHECKPOINT_FOLDER=/scratch/{USER}/eval-checkpoints/{model_name}-$RANDOM_NUMBER/$STEP

{S5CMD_PATH} --stat cp \
    --concurrency 50 \
    --exclude "optimizer/*" \
    --exclude "random/*" \
    --exclude "lr_scheduler/*" \
    --part-size 100 \
    "{s3_path}/$STEP/*" "$LOCAL_DOWNLOAD_CHECKPOINT_FOLDER/"

# ... evaluation happens ...

# Cleanup:
rm -rf "$LOCAL_DOWNLOAD_CHECKPOINT_FOLDER"
```

The random number prevents collision when multiple array tasks run on the same node.

Sources: [ablations/evaluations/launch_evals.py:435-497]()

## Advanced Patterns

### Job Requeue Support

Evaluation jobs support automatic requeue on node failure:

```bash
#SBATCH --requeue
```

This allows SLURM to automatically restart failed array tasks on different nodes.

Sources: [ablations/evaluations/launch_evals.py:394]()

### Checkpoint Discovery and Task Filtering

The evaluation system discovers checkpoints from S3 and filters already-completed tasks:

```python
def get_checkpoints_to_run(
    s3_path: str, 
    model_name: str,
    checkpoints: str,
    after_date: Optional[str] = None,
    tasks_list_path: Optional[str] = None
) -> List[Tuple[str, Set[str]]]:
    # 1. List checkpoints from S3
    df = get_datafolder(s3_path)
    avail_checkpoints = sorted(df.ls("", detail=False))
    
    # 2. Filter by date if provided
    reference_date = parse_date(after_date)
    
    # 3. For each checkpoint, get already-evaluated tasks
    for ckpt in selected_checkpoints:
        evaluated_tasks = get_evaluated_tasks(model_name, ckpt, reference_date)
        
        # 4. Calculate remaining tasks
        all_tasks = get_tasks_from_file(tasks_list_path)
        remaining_tasks = all_tasks - evaluated_tasks
        
        if remaining_tasks:
            checkpoints_with_tasks.append((ckpt, remaining_tasks))
    
    return checkpoints_with_tasks
```

This ensures efficient use of compute resources by skipping redundant evaluations.

Sources: [ablations/evaluations/launch_evals.py:175-224]()

### Random Sleep to Avoid Resource Contention

Both training and evaluation include random delays to prevent concurrent HuggingFace Hub requests:

**Training:**

```bash
random_milliseconds=$(( RANDOM % 1001 ))
sleep_time=$(bc <<< "scale=3; $random_milliseconds / 1000")
echo "Sleeping for $sleep_time seconds..."
sleep $sleep_time
```

Sources: [ablations/training/training_script.py:410-413]()

**Tokenization:**

```python
env_command="sleep $((RANDOM % 30))"
```

Sources: [ablations/tokenization/tk_thom.py:245]()

### Multi-Language Task Selection

Both training and evaluation automatically select task files based on language prefix:

```python
custom_tasks = {
    "eng_Latn": "/admin/home/user/shared/projects/new_training_setup/task_list.py",
    "fra_Latn": "lighteval.tasks.multilingual.tasks",
    "arb_Arab": "lighteval.tasks.multilingual.tasks",
    "cmn_Hani": "lighteval.tasks.multilingual.tasks",
    "rus_Cyrl": "lighteval.tasks.multilingual.tasks",
}

tasks_list = {
    "eng_Latn": ".../tasks_eng.txt",
    "fra_Latn": ".../tasks_fra.txt",
    # ... etc
}

# Extract language from model/run name:
language = model_name.split("-")[0]  # or run_name.split("-")[0]
custom_tasks_path = custom_tasks.get(language, custom_tasks["eng_Latn"])
tasks_list_path = tasks_list.get(language, tasks_list["eng_Latn"])
```

Sources: [ablations/evaluations/launch_evals.py:29-43](), [ablations/evaluations/launch_evals.py:307-315](), [ablations/training/training_script.py:176-190](), [ablations/training/training_script.py:283-295]()

## Common Paths and Constants

### Key Directory Paths

| Path | Purpose |
|------|---------|
| `/shared/{USER}/logs/pdf_project/experiments/` | Root for all experiment logs |
| `/shared/user/projects/new_training_setup/nanotron` | Nanotron framework installation |
| `/scratch/{USER}/` | Node-local temporary storage |
| `s3://bucket/experiments/checkpoints/` | S3 checkpoint storage |
| `s3://bucket/experiments/evals-test/` | S3 evaluation results |
| `s3://bucket/experiments/tokenized/` | S3 tokenized data |

Sources: [ablations/training/training_script.py:12-21](), [ablations/evaluations/launch_evals.py:18-22]()

### S5cmd Integration

All S3 operations use `s5cmd` for high-performance data transfer:

```python
S5CMD_PATH = "/shared/user/projects/new_training_setup/training_venv/bin/s5cmd"

# Download:
{S5CMD_PATH} --stat cp \
    --concurrency 50 \
    --part-size 100 \
    "s3://source/*" "/local/destination/"

# Upload (configured in model config):
s3_upload:
  s5cmd_path: {S5CMD_PATH}
  s5cmd_concurrency: 5
  s5cmd_numworkers: 16
  upload_s3_path: {S3_CHECKPOINTS_PREFIX}
  remove_after_upload: true
```

Sources: [ablations/training/training_script.py:17](), [ablations/training/training_script.py:133-138](), [ablations/evaluations/launch_evals.py:22](), [ablations/evaluations/launch_evals.py:442-448]()

---

