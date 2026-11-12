<!-- source: DeepWiki mcp.deepwiki.com · repo RLinf/RLinf · page 11 Troubleshooting and FAQ · fetched 2026-10-21 -->

# Troubleshooting and FAQ

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug-report.yml](.github/ISSUE_TEMPLATE/bug-report.yml)
- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/ISSUE_TEMPLATE/troubleshooting.yml](.github/ISSUE_TEMPLATE/troubleshooting.yml)
- [.github/workflows/ci-tests.yml](.github/workflows/ci-tests.yml)
- [AGENTS.md](AGENTS.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [docs/README.md](docs/README.md)
- [docs/autobuild.sh](docs/autobuild.sh)
- [docs/source-en/rst_source/examples/index.rst](docs/source-en/rst_source/examples/index.rst)
- [docs/source-zh/rst_source/examples/index.rst](docs/source-zh/rst_source/examples/index.rst)
- [examples/agent/tools/search_local_server_faiss/local_retrieval_server.py](examples/agent/tools/search_local_server_faiss/local_retrieval_server.py)
- [examples/agent/tools/search_local_server_qdrant/local_retrieval_server.py](examples/agent/tools/search_local_server_qdrant/local_retrieval_server.py)
- [rlinf/algorithms/rewards/math/math_verifier/parser.py](rlinf/algorithms/rewards/math/math_verifier/parser.py)
- [rlinf/data/datasets/reasoning.py](rlinf/data/datasets/reasoning.py)
- [rlinf/hybrid_engines/fsdp/__init__.py](rlinf/hybrid_engines/fsdp/__init__.py)

</details>



This page provides systematic guidance for resolving common issues encountered when installing, configuring, and running RLinf. It covers installation problems, runtime errors, configuration issues, environment-specific failures, and performance optimization strategies using built-in profiling and debugging tools.

## Overview: Common Failure Points

The following diagram maps the typical failure points in RLinf's execution pipeline and where to look for solutions:

### RLinf Execution Pipeline and Failure Nodes
```mermaid
graph TB
    [Start] --> [Install]
    [Install] --> [InstallFail]
    [Install] --> [Config]
    [Config] --> [ConfigFail]
    [Config] --> [Init]
    [Init] --> [InitFail]
    [Init] --> [Training]
    [Training] --> [TrainFail]
    [Training] --> [Eval]
    [Eval] --> [EvalFail]

    [InstallFail] ["Installation Failures<br/>━━━━━━━━━━━<br/>• Missing system deps<br/>• UV/pip errors<br/>• Flash-attn build<br/>• Apex compilation<br/>• Environment clone"]
    
    [ConfigFail] ["Configuration Failures<br/>━━━━━━━━━━━<br/>• Invalid YAML<br/>• Hydra resolution errors<br/>• Missing model paths<br/>• Placement conflicts"]
    
    [InitFail] ["Initialization Failures<br/>━━━━━━━━━━━<br/>• GPU detection<br/>• Ray cluster connection<br/>• Model loading<br/>• Environment setup<br/>• Worker launch"]
    
    [TrainFail] ["Training Failures<br/>━━━━━━━━━━━<br/>• OOM errors<br/>• Communication timeout<br/>• Gradient NaN<br/>• Channel deadlock<br/>• Worker crash"]
    
    [EvalFail] ["Evaluation Failures<br/>━━━━━━━━━━━<br/>• Video recording<br/>• Metric collection<br/>• Environment reset<br/>• Action dim mismatch"]
```

**Sources**: [.github/ISSUE_TEMPLATE/troubleshooting.yml:1-80](), [.github/ISSUE_TEMPLATE/bug-report.yml:1-87]()

---

## 1. Installation Troubleshooting

RLinf uses `uv` and a custom `install.sh` script to manage complex dependencies across different hardware platforms (NVIDIA, AMD, Ascend) [README.md:141-143]().

### 1.1 UV and Python Environment Errors
**Symptom**: `uv sync` or `install.sh` fails with dependency resolution errors or missing Python versions.

**Common Fixes**:
*   **Python Version**: RLinf generally targets Python 3.10+ [README.md:16-17]().
*   **Dependency Management**: RLinf utilizes `uv` for fast, reproducible installs [.github/ISSUE_TEMPLATE/troubleshooting.yml:51-51](). If resolution fails, ensure your `uv` version is up-to-date.
*   **Flash-Attn Build**: Building `flash-attn` from source can fail if CUDA toolkits are mismatched. Ensure `nvidia-smi` shows compatible driver and toolkit versions [.github/ISSUE_TEMPLATE/troubleshooting.yml:52-52]().

### 1.2 Multi-Hardware Support
**Symptom**: Failures when running on non-NVIDIA hardware.

**Fix**: RLinf v0.3 introduced support for **Ascend (CANN)**, **AMD (ROCm)**, and **Musa** [README.md:141-143](). Ensure the correct backend-specific environment variables and drivers are installed for your specific `AcceleratorManager` target.

**Sources**: [README.md:141-143](), [.github/ISSUE_TEMPLATE/troubleshooting.yml:46-62]()

---

## 2. Breakpoint Debugging

RLinf supports methods for debugging distributed Ray tasks, enabling inspection of `Worker` state and `Trajectory` data flow.

### 2.1 Ray Distributed Debugger (Recommended)
This method allows interactive debugging within VSCode or Cursor using the `debugpy` library.

1.  **Environment Setup**: Ensure `debugpy` is available in your environment.
2.  **VSCode Configuration**: Install the "Ray Distributed Debugger" extension and register the cluster endpoint (default `127.0.0.1:8265` or your `ray start --head` address).
3.  **Set Breakpoint**: Insert `breakpoint()` in your code, for example, before `input_transform` in a worker class.
4.  **Execution**: Run your script using the provided example runners or CI scripts.
5.  **Attach**: When execution pauses, the task appears in the Ray extension "Paused Tasks" list. Click the play/attach icon to start an interactive session.

**Sources**: [AGENTS.md:5-5](), [.github/workflows/ci-tests.yml:57-165]()

---

## 3. Simulator and Model Specific Issues

### 3.1 Environment and Action Space
**Symptom**: Action mismatches or simulator crashes.

**Fixes**:
*   **BEHAVIOR**: RLinf v0.3 supports v3.7.1 / v3.7.2 with specific patches and object randomization [README.md:42-42]().
*   **ManiSkill**: Verified with `ManiSkill-GS` for Real2Sim2Real training [README.md:22-22]().
*   **IsaacLab**: Specifically optimized for `gr00t+isaaclab` workflows [README.md:30-30]().

### 3.2 VLA and Model Training
**Symptom**: Model weights not syncing or gradients not updating.

**Fixes**:
*   **OpenPI**: Ensure gradient checkpointing is handled correctly; v0.2 fixed a bug where it had to be disabled manually [README.md:88-88]().
*   **Weight Sync**: RLinf v0.3 upgraded the `Weight Syncer` to support broadcast-based sync, incremental patches, and bucketed synchronization to reduce communication overhead [README.md:134-135]().

**Sources**: [README.md:22-42](), [README.md:88-135]()

---

## 4. Performance Optimization

RLinf provides system-level optimizations for high-throughput training.

### 4.1 System-Level Optimizations
For environments like **BEHAVIOR**, RLinf implements several strategies to reduce end-to-end latency [README.md:39-40]():

*   **Feature Slimming**: Removing unnecessary multi-modal observations.
*   **On-Demand Observation**: Only generating observations when required by the action chunk.
*   **Hybrid Pipeline Parallelism**: Overlapping model inference with environment stepping.

### 4.2 Throughput Comparison
| Strategy | Implementation | Benefit |
| :--- | :--- | :--- |
| **Async PPO** | `AsyncEmbodiedRunner` | Overlaps training with rollout generation [README.md:101-103](). |
| **Decoupled Env** | `Decoupled env mode` | Unbinds Env Workers from Rollout Workers to maximize GPU utilization [README.md:127-127](). |
| **FUSCO** | `FUSCO` communication library | Optimizes All-to-All communication for MoE models in Megatron [README.md:67-67](). |
| **DreamZero SFT** | WAN-based VLA | 4x throughput improvement via FSDP2/CUDA Graph [README.md:21-21](). |

**Sources**: [README.md:21-127](), [AGENTS.md:34-38]()

---

## 5. Submitting a Support Request

When reporting issues via the [Troubleshoot Issue Template](.github/ISSUE_TEMPLATE/troubleshooting.yml), please provide the following technical details.

### Natural Language to Code Mapping for Reports
```mermaid
graph LR
    [UserReport] ["User Issue Report"]
    
    subgraph "Code_Entity_Space"
        [ConfigYAML] ["Hydra Configuration<br/>(examples/*/config/)"]
        [LogFile] ["Log File<br/>(outputs/ or logs/)"]
        [EnvInfo] ["Environment Info<br/>(uv pip list)"]
        [IssueTemplate] ["Troubleshooting Template<br/>(.github/ISSUE_TEMPLATE/troubleshooting.yml)"]
    end
    
    [UserReport] --> [ConfigYAML]
    [UserReport] --> [LogFile]
    [UserReport] --> [EnvInfo]
    [UserReport] --> [IssueTemplate]
```

**Required Information Checklist**:
1.  **Configuration**: Full YAML content or the `python` command with overrides [.github/ISSUE_TEMPLATE/troubleshooting.yml:16-25]().
2.  **Logs**: Provide the full stack trace from the `logs/` folder [.github/ISSUE_TEMPLATE/troubleshooting.yml:30-41]().
3.  **Environment**: Output of `uv pip list` and `nvidia-smi` [.github/ISSUE_TEMPLATE/troubleshooting.yml:46-58]().
4.  **Versions**: RLinf version and Docker image tag if applicable [.github/ISSUE_TEMPLATE/troubleshooting.yml:59-60]().

**Sources**: [.github/ISSUE_TEMPLATE/troubleshooting.yml:1-80](), [README.md:1-143]()

---

