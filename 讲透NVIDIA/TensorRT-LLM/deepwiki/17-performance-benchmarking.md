<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-LLM · page 17 Performance Benchmarking · fetched 2026-10-26 -->

# Performance Benchmarking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/disaggregated/slurm/cache_transceiver_test/run_cache_transceiver_test.py](examples/disaggregated/slurm/cache_transceiver_test/run_cache_transceiver_test.py)
- [jenkins/scripts/perf/cluster_env.py](jenkins/scripts/perf/cluster_env.py)
- [jenkins/scripts/perf/disaggregated/slurm_ct_precheck_gate.sh](jenkins/scripts/perf/disaggregated/slurm_ct_precheck_gate.sh)
- [jenkins/scripts/perf/disaggregated/slurm_launch_draft.sh](jenkins/scripts/perf/disaggregated/slurm_launch_draft.sh)
- [jenkins/scripts/perf/local/submit.py](jenkins/scripts/perf/local/submit.py)
- [jenkins/scripts/perf/submit.py](jenkins/scripts/perf/submit.py)
- [tensorrt_llm/bench/benchmark/__init__.py](tensorrt_llm/bench/benchmark/__init__.py)
- [tests/integration/defs/examples/serve/test_configs/Nemotron3_Nano_Omni_30B_NVFP4.yml](tests/integration/defs/examples/serve/test_configs/Nemotron3_Nano_Omni_30B_NVFP4.yml)
- [tests/integration/defs/examples/serve/test_configs/Qwen3-30B-A3B-FP8.yml](tests/integration/defs/examples/serve/test_configs/Qwen3-30B-A3B-FP8.yml)
- [tests/integration/defs/examples/serve/test_serve.py](tests/integration/defs/examples/serve/test_serve.py)
- [tests/integration/defs/perf/README.md](tests/integration/defs/perf/README.md)
- [tests/integration/defs/perf/_model_paths.py](tests/integration/defs/perf/_model_paths.py)
- [tests/integration/defs/perf/base_perf_pytorch.csv](tests/integration/defs/perf/base_perf_pytorch.csv)
- [tests/integration/defs/perf/open_search_db_utils.py](tests/integration/defs/perf/open_search_db_utils.py)
- [tests/integration/defs/perf/pytorch_model_config.py](tests/integration/defs/perf/pytorch_model_config.py)
- [tests/integration/defs/perf/sanity_perf_check.py](tests/integration/defs/perf/sanity_perf_check.py)
- [tests/integration/defs/perf/test_perf.py](tests/integration/defs/perf/test_perf.py)
- [tests/integration/defs/perf/test_perf_sanity.py](tests/integration/defs/perf/test_perf_sanity.py)
- [tests/integration/defs/perf/utils.py](tests/integration/defs/perf/utils.py)
- [tests/integration/test_lists/qa/README.md](tests/integration/test_lists/qa/README.md)
- [tests/integration/test_lists/qa/llm_perf_core.yml](tests/integration/test_lists/qa/llm_perf_core.yml)
- [tests/integration/test_lists/qa/llm_perf_multinode.yml](tests/integration/test_lists/qa/llm_perf_multinode.yml)
- [tests/integration/test_lists/qa/llm_spark_core.txt](tests/integration/test_lists/qa/llm_spark_core.txt)
- [tests/integration/test_lists/qa/llm_spark_func.yml](tests/integration/test_lists/qa/llm_spark_func.yml)
- [tests/integration/test_lists/qa/llm_spark_perf.yml](tests/integration/test_lists/qa/llm_spark_perf.yml)
- [tests/integration/test_lists/test-db/l0_gb200_multi_gpus_perf_sanity.yml](tests/integration/test_lists/test-db/l0_gb200_multi_gpus_perf_sanity.yml)
- [tests/integration/test_lists/test-db/l0_perf.yml](tests/integration/test_lists/test-db/l0_perf.yml)
- [tests/scripts/perf-sanity/aggregated/super_ad_blackwell.yaml](tests/scripts/perf-sanity/aggregated/super_ad_blackwell.yaml)
- [tests/scripts/perf-sanity/cache_transceiver_precheck/README.md](tests/scripts/perf-sanity/cache_transceiver_precheck/README.md)
- [tests/scripts/perf-sanity/cache_transceiver_precheck/precheck_config.py](tests/scripts/perf-sanity/cache_transceiver_precheck/precheck_config.py)
- [tests/scripts/perf-sanity/cache_transceiver_precheck/run_precheck.py](tests/scripts/perf-sanity/cache_transceiver_precheck/run_precheck.py)
- [tests/scripts/perf/disaggregated/gb300_kimi-k3-fp4_8k1k_con512_ctx1_dep16_gen1_dep16_eplb0_mtp0_ccb-NIXL.yaml](tests/scripts/perf/disaggregated/gb300_kimi-k3-fp4_8k1k_con512_ctx1_dep16_gen1_dep16_eplb0_mtp0_ccb-NIXL.yaml)
- [tests/unittest/others/test_cache_transceiver_precheck_config.py](tests/unittest/others/test_cache_transceiver_precheck_config.py)
- [tests/unittest/others/test_cache_transceiver_precheck_run.py](tests/unittest/others/test_cache_transceiver_precheck_run.py)
- [tests/unittest/scripts/test_cluster_env.py](tests/unittest/scripts/test_cluster_env.py)
- [tests/unittest/scripts/test_perf_sanity_helpers.py](tests/unittest/scripts/test_perf_sanity_helpers.py)
- [tests/unittest/scripts/test_perf_submit.py](tests/unittest/scripts/test_perf_submit.py)

</details>



## Purpose and Scope

Performance Benchmarking in TensorRT-LLM provides a comprehensive framework for measuring and validating the inference performance of Large Language Models. This system executes automated performance tests across different backends (PyTorch, TensorRT, AutoDeploy), hardware configurations, and model variants, collecting metrics such as throughput, latency, and memory usage to detect regressions and validate optimizations.

**Related Pages:**
- For detailed execution flow and configuration classes, see [Performance Testing Framework](#17.1)
- For backend-specific performance test configuration details, see [Backend-Specific Performance Configuration](#17.2)
- For metric collection and regression detection mechanisms, see [Performance Metrics and Regression Detection](#17.3)
- For accuracy validation and test execution infrastructure, see [Testing Infrastructure](#5)

## Performance Benchmarking Architecture

The performance benchmarking system consists of three major components: the test execution framework (`test_perf.py`), the benchmarking tool (`trtllm-bench`), and configuration management systems (YAML test lists and model-specific configs).

### System Overview and Code Entities
The following diagram maps high-level benchmarking concepts to their specific implementations in the codebase.

Title: Performance Benchmarking System Architecture
```mermaid
graph TB
    subgraph "Test_Orchestration"
        [test_perf.py]::"test_perf"
        [PerfTestConfig]::"PerfTestConfig"
        [TestLists]::"llm_perf_core.yml"
    end
    
    subgraph "Benchmark_Execution"
        [TRTLLMBench]::"trtllm-bench_CLI"
        [ThroughputCmd]::"throughput.py"
        [LatencyCmd]::"low_latency.py"
        [StatsKeeper]::"StatsKeeper"
    end
    
    subgraph "Backend_Configuration"
        [PyTorchConfig]::"pytorch_model_config.py"
        [GeneralExecSettings]::"GeneralExecSettings"
        [PatternConfigs]::"pattern_configs"
    end
    
    subgraph "Metric_Collection"
        [StatsKeeper] --> [PerfItemTuple]::"PerfItemTuple"
        [PerfItemTuple] --> [PerfMetricType]::"PerfMetricType_Enum"
    end
    
    [TestLists] --> [test_perf.py]
    [test_perf.py] --> [PerfTestConfig]
    [PerfTestConfig] --> [TRTLLMBench]
    [PerfTestConfig] --> [PyTorchConfig]
    
    [TRTLLMBench] --> [ThroughputCmd]
    [TRTLLMBench] --> [LatencyCmd]
    
    [PyTorchConfig] --> [PatternConfigs]
    [GeneralExecSettings] --> [TRTLLMBench]
    
    [ThroughputCmd] --> [StatsKeeper]
    [LatencyCmd] --> [StatsKeeper]
```
**Sources:** [tests/integration/defs/perf/test_perf.py:15-39](), [tests/integration/defs/perf/pytorch_model_config.py:55-64](), [tests/integration/defs/perf/utils.py:88-119](), [tensorrt_llm/bench/benchmark/throughput.py:52-70](), [tensorrt_llm/bench/dataclasses/reporting.py:54-60]()

## Test Execution Framework

The `test_perf.py` module implements the core test execution framework using `pytest`. Tests are defined by strings that are parsed into configuration objects specifying model, runtime, batch sizes, quantization, and parallelism parameters. The framework manages a `MODEL_PATH_DICT` that maps model labels to local paths, including support for the latest models like Llama 3.3, DeepSeek R1/V4, and Qwen 3 [tests/integration/defs/perf/_model_paths.py:18-113](). It also identifies models requiring specific settings like `trust_remote_code` or specialized datasets for speculative decoding and multimodal benchmarks [tests/integration/defs/perf/test_perf.py:57-100]().

For details, see [Performance Testing Framework](#17.1).

### Test Execution Flow

The main test function `test_perf` orchestrates the complete benchmark workflow, from dataset preparation to metric validation.

Title: Performance Test Execution Flow
```mermaid
graph TD
    [Start]::"test_perf" --> [ParseConfig]::"PerfTestConfig.load_from_str"
    [ParseConfig] --> [GetModel]::"MODEL_PATH_DICT_lookup"
    [GetModel] --> [PrepDataset]::"trtllm-bench_prepare-dataset"
    
    [PrepDataset] --> [CheckBackend]{"Backend_Type?"}
    
    [CheckBackend] -->|pytorch| [GenPyConfig]::"get_model_yaml_config"
    [CheckBackend] -->|tensorrt| [TRTRun]::"trtllm-bench_throughput"
    
    [GenPyConfig] --> [RunBench]::"trtllm-bench_throughput"
    [RunBench] --> [StatsKeeper]::"StatsKeeper"
    [TRTRun] --> [StatsKeeper]
    
    [StatsKeeper] --> [ParseLogs]::"PERF_METRIC_LOG_QUERIES"
    [ParseLogs] --> [CheckThreshold]::"Threshold_Validation"
    [CheckThreshold] --> [AssertPass]::"Regression_Detection"
```
**Sources:** [tests/integration/defs/perf/test_perf.py:47-150](), [tests/integration/defs/perf/pytorch_model_config.py:55-72](), [tests/integration/defs/perf/utils.py:165-187]()

## trtllm-bench Tool

The `trtllm-bench` command-line tool provides the core benchmarking capabilities. It leverages the `LLM` API to execute requests and collect high-fidelity timing data. The framework integrates this tool through command builders like `PerfBenchScriptTestCmds` and `PerfServeScriptTestCmds` [tests/integration/defs/perf/utils.py:37-39]().

### Benchmarking Modes and Backends

The tool supports multiple backends including `pytorch` and `tensorrt` [tensorrt_llm/bench/benchmark/throughput.py:65-68](). It provides general CLI options for controlling concurrency, streaming, and KV cache percentages. For serving scenarios, the framework includes `PerfServeScriptTestCmds` to validate the performance of `trtllm-serve` using the OpenAI-compatible API [tests/integration/defs/perf/utils.py:37-39](). This is used to test features like multimodal reasoning with models such as `nemotron_3_nano_omni_nvfp4_image` [tests/integration/test_lists/qa/llm_spark_perf.yml:19-27]().

**Sources:** [tests/integration/defs/perf/test_perf.py:78-87](), [tests/integration/defs/perf/utils.py:165-187](), [tensorrt_llm/bench/benchmark/throughput.py:52-122]()

## Performance Metrics and Statistics

The framework tracks multiple performance metrics through the `PerfMetricType` enumeration and regex-based extraction from logs.

### Metric Collection

Individual metrics are categorized into types such as `INFERENCE_TIME`, `FIRST_TOKEN_TIME` (TTFT), and `TOTAL_OUTPUT_THROUGHPUT` [tests/integration/defs/perf/utils.py:88-119](). Extraction is handled by `PERF_METRIC_LOG_QUERIES` which uses compiled regex patterns to find values in command output [tests/integration/defs/perf/test_perf.py:160-191](). The `StatsKeeper` class manages the lifecycle of these metrics during a benchmark run [tensorrt_llm/bench/dataclasses/reporting.py:54-60]().

| Metric Type | Code Entity | Description |
|-----------|-------------|-------------|
| `TOKEN_THROUGHPUT` | `PerfMetricType.TOTAL_OUTPUT_THROUGHPUT` | Total tokens generated per second |
| `TTFT` | `PerfMetricType.FIRST_TOKEN_TIME` | Time to First Token (latency) |
| `SEQ_THROUGHPUT` | `PerfMetricType.SEQ_THROUGHPUT` | Requests or sequences processed per second |
| `GPU_MEM` | `PerfMetricType.INFERENCE_PEAK_GPU_MEMORY` | Peak GPU memory utilization in GB |
| `ENGINE_SIZE` | `PerfMetricType.ENGINE_SIZE` | Size of the serialized engine file in MiB |

**Sources:** [tests/integration/defs/perf/utils.py:88-119](), [tests/integration/defs/perf/test_perf.py:160-191](), [tensorrt_llm/bench/dataclasses/reporting.py:154-200]()

## Backend-Specific Performance Configuration

Different backends require specialized configurations to achieve peak performance. The system manages these via model-specific YAML configurations and pattern matching in `get_model_yaml_config`.

For details, see [Backend-Specific Performance Configuration](#17.2).

### PyTorch Backend Tuning

The PyTorch backend uses `pytorch_model_config.py` to apply pattern-based overrides. This includes enabling features like `enable_attention_dp`, `enable_chunked_prefill`, or specific speculative decoding configurations like `DSpark` for DeepSeek V4 Pro [tests/integration/defs/perf/pytorch_model_config.py:117-143](). It also handles SM-version specific logic, such as selecting the `DEEPGEMM` backend for DeepSeek FP8 models on Hopper (SM90) while ensuring compatibility on Blackwell [tests/integration/defs/perf/pytorch_model_config.py:27-44]().

```python
# Example pattern-based config for DeepSeek V4 Pro DSpark [tests/integration/defs/perf/pytorch_model_config.py:117-143]
{
    'patterns': ['deepseek_v4_pro_dspark'],
    'config': {
        'attn_backend': 'TRTLLM',
        'enable_attention_dp': True,
        'moe_config': {
            'backend': 'MEGAMOE_DEEPGEMM',
        },
        'speculative_config': {
            'decoding_type': 'DSpark',
            'max_draft_len': 5,
        },
    }
}
```

**Sources:** [tests/integration/defs/perf/pytorch_model_config.py:27-182]()

## Test Configuration and Filtering

Tests are organized in YAML files and filtered based on system properties like GPU count, compute capability, and memory availability [tests/integration/test_lists/qa/llm_perf_core.yml:23-29]().

| Test List | Purpose |
|-----------|---------|
| `l0_perf.yml` | Pre-merge performance validation for H100 [tests/integration/test_lists/test-db/l0_perf.yml:1-16](). |
| `llm_perf_core.yml` | Comprehensive coverage across hardware tiers (H100, B200, GB200, A100, etc.) [tests/integration/test_lists/qa/llm_perf_core.yml:1-118](). |
| `llm_spark_perf.yml` | Performance tests for single and multi-GPU Spark release cases, including `gpt_oss_120b_eagle3` and `nemotron_3_nano_omni` [tests/integration/test_lists/qa/llm_spark_perf.yml:1-70](). |
| `l0_gb200_multi_gpus_perf_sanity.yml` | Pre-merge and post-merge sanity checks specifically for GB200 systems, including DeepSeek R1 and Qwen3 [tests/integration/test_lists/test-db/l0_gb200_multi_gpus_perf_sanity.yml:1-62](). |

**Sources:** [tests/integration/test_lists/qa/llm_perf_core.yml:1-118](), [tests/integration/test_lists/qa/llm_spark_perf.yml:1-70](), [tests/integration/test_lists/test-db/l0_perf.yml:1-16](), [tests/integration/test_lists/test-db/l0_gb200_multi_gpus_perf_sanity.yml:1-62]()

---

