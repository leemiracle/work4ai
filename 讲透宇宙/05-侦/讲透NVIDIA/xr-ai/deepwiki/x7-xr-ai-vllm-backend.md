<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/xr-ai · extra page xr-ai-vllm Backend · fetched 2026-10-26 -->

# xr-ai-vllm Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [services/embedding-server/embedding_server.yaml](services/embedding-server/embedding_server.yaml)
- [services/llama-nemotron-llm/llama_nemotron_llm_server.yaml](services/llama-nemotron-llm/llama_nemotron_llm_server.yaml)
- [services/magpie-tts/magpie_tts_server/__main__.py](services/magpie-tts/magpie_tts_server/__main__.py)
- [services/nemotron-omni-llm/nemotron_omni_llm_server.yaml](services/nemotron-omni-llm/nemotron_omni_llm_server.yaml)
- [services/nemotron3-nano-llm/nemotron3_nano_llm_server.yaml](services/nemotron3-nano-llm/nemotron3_nano_llm_server.yaml)
- [services/stt-server/stt_server/__main__.py](services/stt-server/stt_server/__main__.py)
- [services/vlm-server/vlm_server.yaml](services/vlm-server/vlm_server.yaml)
- [tests/test_vllm_diagnostics.py](tests/test_vllm_diagnostics.py)
- [tests/test_vllm_docker.py](tests/test_vllm_docker.py)
- [tests/test_vllm_lifecycle.py](tests/test_vllm_lifecycle.py)
- [utils/xr-ai-vllm/xr_ai_vllm/__init__.py](utils/xr-ai-vllm/xr_ai_vllm/__init__.py)
- [utils/xr-ai-vllm/xr_ai_vllm/_config.py](utils/xr-ai-vllm/xr_ai_vllm/_config.py)
- [utils/xr-ai-vllm/xr_ai_vllm/_diagnostics.py](utils/xr-ai-vllm/xr_ai_vllm/_diagnostics.py)
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py](utils/xr-ai-vllm/xr_ai_vllm/_docker.py)

</details>



This page provides a deep dive into the `xr-ai-vllm` package, which serves as a pluggable backend for vLLM-based inference services within the XR-AI ecosystem. It details the two primary modes of operation: `pip` and `docker`, explaining their implementation, lifecycle management, and specific features like launch contract fingerprinting, container reuse, log streaming, and handling of DGX Spark UMA.

## Overview of `xr-ai-vllm`

The `xr-ai-vllm` package [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:4-14]() offers a unified interface for launching vLLM inference servers, abstracting away the underlying execution environment. Services can choose between a `pip` backend, which runs vLLM from the wrapper's Python virtual environment, or a `docker` backend, which leverages NGC containers. This flexibility allows for consistent configuration across different deployment scenarios while optimizing for specific runtime requirements.

The core entry point for launching a vLLM server is the `serve` function [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:66-84](). It takes parameters such as `backend` (`"pip"` or `"docker"`), `model`, `port`, `model_cache`, and `extra_serve_args` which are passed directly to the vLLM CLI.

```mermaid
graph TD
    A[xr-ai-vllm.serve()] --> B{backend == "pip"?};
    B -- Yes --> C[xr-ai-vllm._pip.run()];
    B -- No --> D{backend == "docker"?};
    D -- Yes --> E[xr-ai-vllm._docker.run()];
    D -- No --> F[Raise ValueError];

    C -- "Launches vLLM CLI in venv" --> G[vLLM Process];
    E -- "Launches docker run command" --> H[Docker Container];
    H -- "Runs vLLM CLI inside container" --> G;
```
**Diagram: `xr-ai-vllm.serve()` Backend Selection**

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:4-14]()
- [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:66-84]()

## Pip Backend

The `pip` backend [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:130-137]() executes the `vllm` CLI directly from the Python virtual environment where `xr-ai-vllm` is installed. This mode is suitable for local development and environments where Docker is not preferred or available.

### Lifecycle Management in Pip Mode

In `pip` mode, the `persistent` flag [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:92-97]() controls the server's lifecycle:
*   If `persistent` is `True`, the vLLM process is started in a new session, allowing it to survive wrapper restarts. Cleanup is handled by `stop_persistent_servers` [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:160-163]().
*   If `persistent` is `False`, the vLLM process terminates with its parent wrapper process.

The `_pip.run` function [utils/xr-ai-vllm/xr_ai_vllm/_pip.py:89]() is responsible for constructing the `vllm` command-line arguments and launching the process. It also handles log streaming and readiness checks.

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:92-97]()
- [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:130-137]()
- [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:160-163]()
- [utils/xr-ai-vllm/xr_ai_vllm/_pip.py:89]()

## Docker Backend

The `docker` backend [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:138-153]() runs vLLM inside an NGC Docker container. This provides isolation, consistent environments, and leverages Docker's resource management capabilities. The `_docker.py` module [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:4-17]() is dedicated to managing this backend.

### `build_run_argv`

The `build_run_argv` function [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:101-113]() constructs the `docker run` command-line arguments. It includes various Docker-specific flags and environment variables to ensure proper operation:
*   `--name`: Assigns a stable name to the container for easier management.
*   `--label`: Adds labels for `xr-ai-vllm.port` and `xr-ai-vllm.config` to identify and fingerprint the container.
*   `--network host`: Allows the container to share the host's network stack, making the vLLM process visible to `ss(8)` on the host for PID-based cleanup.
*   `--ipc host`: Provides the container with the host's larger shared memory namespace, crucial for vLLM workers that communicate via `/dev/shm`.
*   `--runtime nvidia`: Requests GPUs via the NVIDIA container runtime, ensuring proper GPU access.
*   `-e NVIDIA_VISIBLE_DEVICES`: Specifies which GPUs are visible to the container.
*   `-e NVIDIA_DRIVER_CAPABILITIES`: Sets driver capabilities for CUDA compute.
*   `-e HF_HOME`, `-e TRANSFORMERS_CACHE`: Configures Hugging Face cache directories.
*   `-e HF_TOKEN`: Passes the Hugging Face token securely.

```mermaid
graph TD
    A[build_run_argv()] --> B{Input Parameters};
    B --> C[image];
    B --> D[container_name];
    B --> E[port];
    B --> F[model_cache];
    B --> G[hf_token];
    B --> H[cuda_visible_devices];
    B --> I[extra_env];
    B --> J[extra_pip];
    B --> K[vllm_argv];
    B --> L[prefetch_model];

    M[Construct Docker Arguments]
    C,D,E,F,G,H,I,J,K,L --> M;

    M --> N["docker run"];
    M --> O["--name container_name"];
    M --> P["--label xr-ai-vllm.port=port"];
    M --> Q["--label xr-ai-vllm.config=fingerprint"];
    M --> R["--network host"];
    M --> S["--ipc host"];
    M --> T["--runtime nvidia"];
    M --> U["-e NVIDIA_VISIBLE_DEVICES=..."];
    M --> V["-e NVIDIA_DRIVER_CAPABILITIES=compute,utility"];
    M --> W["-e HF_HOME=model_cache"];
    M --> X["-e HF_TOKEN=hf_token (if present)"];
    M --> Y["-e HF_XET_HIGH_PERFORMANCE=1"];
    M --> Z["-v model_cache:model_cache"];
    M --> AA["-v /tmp:/tmp"];
    M --> BB["-v /dev/shm:/dev/shm"];
    M --> CC["image"];
    M --> DD["vllm serve ..."];

    N & O & P & Q & R & S & T & U & V & W & X & Y & Z & AA & BB & CC & DD --> EE[Full docker run argv list];
```
**Diagram: `build_run_argv()` Construction Flow**

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:101-113]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:135-136]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:139-141]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:157-162]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:164-176]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:178-181]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:122-127]()

### Launch Contract Fingerprints and Container Reuse/Eviction

To ensure deterministic and safe container reuse, `xr-ai-vllm` employs a "launch contract fingerprint" [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:86-98](). This fingerprint is a SHA256 digest of all parameters that define a container's launch configuration, including the image, port, model cache, GPU placement, environment variables, and vLLM arguments. It's stored as a Docker label (`xr-ai-vllm.config`) on the container.

When `_docker.run` [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:200-201]() is called, it first checks if a container with the same `container_name` and a matching fingerprint already exists and is running [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:202-203]().
*   If a matching container is found, it's reused.
*   If a container with the same name exists but has a different fingerprint (meaning its launch contract has changed), it is stopped and removed, and a new container is launched.
*   If no container with the given name exists, a new one is launched.

This mechanism prevents silent reuse of misconfigured containers and ensures that updates to the service configuration (e.g., a new vLLM image, different GPU settings) correctly trigger a container replacement. The `credential_digest` function [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:71-82]() is used to include sensitive information like `hf_token` in the fingerprint without exposing the raw credential.

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:86-98]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:71-82]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:200-201]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:202-203]()
- [tests/test_vllm_docker.py:153-160]()

### Log Streaming

The `_LogStreamer` class [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:490-500]() is responsible for continuously reading and forwarding logs from the Docker container's `stdout` and `stderr` to the parent process's logging system. This ensures that all container output is captured and visible, aiding in debugging and monitoring. It runs in a separate thread and handles graceful shutdown.

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:490-500]()
- [tests/test_vllm_docker.py:20-21]()

### `stop_persistent_servers`

The `stop_persistent_servers` function [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:160-163]() is a crucial part of the lifecycle management, especially for `persistent` servers. It iterates through a list of `(label, port)` tuples and attempts to stop the corresponding vLLM server.
1.  **Docker Container Check**: It first tries to find a Docker container labeled `xr-ai-vllm.port=<port>` [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:183-184]() and stops it using `docker stop`.
2.  **PID-on-Port Fallback**: If no Docker container is found, it falls back to identifying the process listening on the given port (`pid_on_port` [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:600-601]()) and sends a `SIGTERM` signal. This covers `pip` mode vLLM processes and other in-process servers.

This dual approach ensures that both Docker containers and standalone processes are gracefully terminated.

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:160-163]()
- [utils/xr-ai-vllm/xr_ai_vllm/__init__.py:183-184]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:600-601]()
- [tests/test_vllm_docker.py:26]()

### DGX Spark UMA Handling

For DGX Spark systems, `xr-ai-vllm` includes specific handling for Unified Memory Architecture (UMA) to mitigate cold-start issues and optimize performance. This is enabled by setting `spark_uma: true` in the service configuration [services/nemotron-omni-llm/nemotron_omni_llm_server.yaml:61]().

The `_gpu_is_dgx_spark` function [utils/xr-ai-vllm/xr_ai_vllm/_config.py:134-155]() detects if the selected GPU is a GB10 in a DGX Spark system. If detected, the Docker backend performs several optimizations:
*   **Prefetching Hugging Face Snapshot**: Before CUDA initialization, the model snapshot is prefetched and synced to disk [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:58-63](). This reduces the likelihood of CUDA driver allocation failures during startup.
*   **Bounded Restart**: If a container launched with `spark_uma` enabled fails due to a non-container-OOM CUDA driver allocation error, `xr-ai-vllm` attempts one bounded restart [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:65-66](). This helps recover from transient UMA-related issues.

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:58-63]()
- [utils/xr-ai-vllm/xr_ai_vllm/_docker.py:65-66]()
- [utils/xr-ai-vllm/xr_ai_vllm/_config.py:134-155]()
- [services/nemotron-omni-llm/nemotron_omni_llm_server.yaml:61]()
- [tests/test_vllm_lifecycle.py:40-63]()

## Failure Diagnostics

`xr-ai-vllm` includes mechanisms to diagnose common startup failures, particularly those related to GPU memory allocation. The `_diagnostics` module [utils/xr-ai-vllm/xr_ai_vllm/_diagnostics.py]() provides utilities for this.

For instance, `_EARLY_CUDA_ALLOCATION_FAILURE` [tests/test_vllm_docker.py:30-36]() is a pattern used to detect specific CUDA out-of-memory errors during the early stages of vLLM initialization. When such an error is detected, the system can provide more targeted advice, such as adjusting `gpu_memory_utilization` or `max_num_seqs` in the configuration.

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/_diagnostics.py]()
- [tests/test_vllm_docker.py:30-36]()

## Configuration Loading and Environment Setup

The `_config.py` module [utils/xr-ai-vllm/xr_ai_vllm/_config.py:4-10]() provides shared helpers for loading YAML configurations, resolving model cache paths, and setting up environment variables.

*   `load_config` [utils/xr-ai-vllm/xr_ai_vllm/_config.py:53-77]() parses `--config` and `--ready-file` arguments, loads the YAML configuration, and reconfigures `stdout`/`stderr` for line-buffered logging.
*   `resolve_model_cache` [utils/xr-ai-vllm/xr_ai_vllm/_config.py:42-50]() determines the absolute path for the model cache, creating it if it doesn't exist.
*   `setup_hf_env` [utils/xr-ai-vllm/xr_ai_vllm/_config.py:81-110]() sets up Hugging Face and CUDA-related environment variables, respecting existing environment values over YAML configurations. This includes `CUDA_VISIBLE_DEVICES`, `HF_TOKEN`, `HF_HOME`, and `TRANSFORMERS_CACHE`.

Example YAML configurations for various services demonstrate the use of these settings:
*   `embedding_server.yaml` [services/embedding-server/embedding_server.yaml:40-45]()
*   `nemotron_omni_llm_server.yaml` [services/nemotron-omni-llm/nemotron_omni_llm_server.yaml:55-59]()
*   `vlm_server.yaml` [services/vlm-server/vlm_server.yaml:60-64]()
*   `nemotron3_nano_llm_server.yaml` [services/nemotron3-nano-llm/nemotron3_nano_llm_server.yaml:68-72]()
*   `llama_nemotron_llm_server.yaml` [services/llama-nemotron-llm/llama_nemotron_llm_server.yaml:39-43]()

Sources:
- [utils/xr-ai-vllm/xr_ai_vllm/_config.py:4-10]()
- [utils/xr-ai-vllm/xr_ai_vllm/_config.py:42-50]()
- [utils/xr-ai-vllm/xr_ai_vllm/_config.py:53-77]()
- [utils/xr-ai-vllm/xr_ai_vllm/_config.py:81-110]()
- [services/embedding-server/embedding_server.yaml:40-45]()
- [services/nemotron-omni-llm/nemotron_omni_llm_server.yaml:55-59]()
- [services/vlm-server/vlm_server.yaml:60-64]()
- [services/nemotron3-nano-llm/nemotron3_nano_llm_server.yaml:68-72]()
- [services/llama-nemotron-llm/llama_nemotron_llm_server.yaml:39-43]()
- [tests/test_vllm_lifecycle.py:65-139]()

---

