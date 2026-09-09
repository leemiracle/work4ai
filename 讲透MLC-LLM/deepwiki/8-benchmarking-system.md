> 来源: [https://deepwiki.com/mlc-ai/mlc-llm/8-benchmarking-system](https://deepwiki.com/mlc-ai/mlc-llm/8-benchmarking-system)
> DeepWiki mlc-ai/mlc-llm | Last indexed: 30 March 2026 (fcce2c

# Benchmarking System

  Relevant source files 
 - [.pylintrc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.pylintrc)
 - [python/mlc_llm/bench/__init__.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__init__.py)
 - [python/mlc_llm/bench/__main__.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py)
 - [python/mlc_llm/bench/api_endpoint.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py)
 - [python/mlc_llm/bench/dataset.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py)
 - [python/mlc_llm/bench/request_processor.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py)
 - [python/mlc_llm/bench/request_record.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py)
 - [python/mlc_llm/cli/lib_delivery.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/cli/lib_delivery.py)
 - [python/mlc_llm/serve/entrypoints/debug_entrypoints.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/debug_entrypoints.py)
 - [python/mlc_llm/support/logging.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/support/logging.py)
 
  This page documents the `mlc_llm.bench` module, which provides a comprehensive framework for benchmarking LLM serving performance. The system supports multiple dataset types, execution modes, API backends, and generates detailed performance metrics.

 For information on serving deployment, see page 7. For engine configuration, see page 6.

 
## Overview

 The `mlc_llm.bench` module is a modular benchmarking framework that measures LLM serving performance. It provides:

 **Dataset Support**:

 
 - `ShareGPTDataset`: Real conversation data from ShareGPT [python/mlc_llm/bench/dataset.py46-168](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L46-L168)
 - `LoogleDataset`: Long-context QA tasks with common prefix sharing [python/mlc_llm/bench/dataset.py170-261](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L170-L261)
 - `LLMPerfDataset`: Synthetic workload generation [python/mlc_llm/bench/dataset.py264-343](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L264-L343)
 - `ReActDataset`: Multi-turn agent interaction traces [python/mlc_llm/bench/dataset.py407-587](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L407-L587)
 - `WildChatDataset`: Real-world chat conversations [python/mlc_llm/bench/dataset.py590-708](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L590-L708)
 - `AzureLLMInferenceDataset`: Production trace replay with timestamps [python/mlc_llm/bench/dataset.py711-786](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L711-L786)
 - `JSONModeEvalDataset`: Structured output validation [python/mlc_llm/bench/dataset.py345-404](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L345-L404)
 
 **Execution Modes**:

 
 - Fixed concurrent requests (`FixedConcurrentRequestExecutor`) [python/mlc_llm/bench/request_processor.py372-481](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L372-L481)
 - Fixed request rate (`FixTimestampExecutor` with Poisson arrival) [python/mlc_llm/bench/request_processor.py484-600](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L484-L600)
 - Dataset replay (`FixTimestampExecutor` with original timestamps) [python/mlc_llm/bench/request_processor.py484-600](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L484-L600)
 
 **Backend Support**:

 
 - OpenAI-compatible APIs: `/v1/chat/completions` and `/v1/completions` [python/mlc_llm/bench/api_endpoint.py36-248](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L36-L248)
 - TensorRT-LLM: `/v2/models/ensemble/generate_stream` [python/mlc_llm/bench/api_endpoint.py251-431](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L251-L431)
 - Compatible with MLC, vLLM, SGLang servers [python/mlc_llm/bench/api_endpoint.py438-464](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L438-L464)
 
 **Metrics**:

 
 - TTFT (Time To First Token): Prefill latency [python/mlc_llm/bench/request_record.py27-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L27-L43)
 - TPOT (Time Per Output Token): Decode latency per token [python/mlc_llm/bench/request_record.py27-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L27-L43)
 - ITL (Inter-Token Latency): Average latency per token [python/mlc_llm/bench/request_record.py27-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L27-L43)
 - Throughput: Requests/sec, tokens/sec [python/mlc_llm/bench/request_record.py88-99](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L88-L99)
 - Latency distributions: P25, P50, P75, P90, P95, P99 [python/mlc_llm/bench/request_record.py148-158](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L148-L158)
 
 The benchmark can launch an MLC server automatically via `PopenServer` or connect to an existing endpoint [python/mlc_llm/bench/__main__.py76-85](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L76-L85)

 Sources: [python/mlc_llm/bench/__main__.py1-32](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L1-L32) [python/mlc_llm/bench/dataset.py1-20](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L1-L20) [python/mlc_llm/bench/api_endpoint.py438-464](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L438-L464)

 
## Benchmarking Architecture

 
### System Components

 
```

```

 **Key Components**:

 
 - `main()`: Orchestrates benchmark execution, launches optional server, coordinates dataset and pipeline creation [python/mlc_llm/bench/__main__.py129-176](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L129-L176)
 - `Dataset` classes: Generate `RequestRecord` objects with input/output specifications [python/mlc_llm/bench/dataset.py22-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L22-L43)
 - `RequestProcessor` pipeline: Transform requests through modular processors (sampling, timestamp attachment, warmup) [python/mlc_llm/bench/request_processor.py30-38](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L30-L38)
 - `Executor` implementations: Execute requests with different concurrency patterns [python/mlc_llm/bench/request_processor.py372-600](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L372-L600)
 - `APIEndPoint` backends: Send requests to serving endpoints and collect metrics [python/mlc_llm/bench/api_endpoint.py18-33](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L18-L33)
 
 Sources: [python/mlc_llm/bench/__main__.py88-176](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L88-L176) [python/mlc_llm/bench/dataset.py22-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L22-L43) [python/mlc_llm/bench/request_processor.py30-38](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L30-L38) [python/mlc_llm/bench/api_endpoint.py18-33](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L18-L33)

 
### Request Processing Flow

 
```

```

 **Processing Stages**:

 
 - **Dataset Generation**: Creates requests with input/output length specifications [python/mlc_llm/bench/dataset.py35-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L35-L43)
 - **Request Sampling**: Selects `num_requests` from dataset, assigns `request_id` [python/mlc_llm/bench/request_processor.py51-121](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L51-L121)
 - **Attribute Attachment**: Adds model name, timestamps, sampling parameters, execution features [python/mlc_llm/bench/request_processor.py124-211](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L124-L211)
 - **Warmup**: Runs warmup requests to stabilize server state [python/mlc_llm/bench/request_processor.py256-338](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L256-L338)
 - **Execution**: Sends requests via executors with concurrency control [python/mlc_llm/bench/request_processor.py372-600](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L372-L600)
 - **Metrics Analysis**: Tokenizes outputs, computes derived metrics (TPOT, ITL) [python/mlc_llm/bench/request_processor.py214-253](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L214-L253)
 - **Report Generation**: Aggregates statistics and prints results [python/mlc_llm/bench/request_record.py67-113](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L67-L113)
 
 Sources: [python/mlc_llm/bench/__main__.py88-116](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L88-L116) [python/mlc_llm/bench/request_processor.py603-692](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L603-L692)

 
## Dataset Support

 The benchmarking system supports multiple dataset types, each with specific characteristics:

 
| Dataset Class | Purpose | Timestamp Support | Fake Warmup Required | Key Features |
|---|---|---|---|---|
| ShareGPTDataset | Real conversation data | No | No | Filters by conversation length, supports chat templates python/mlc_llm/bench/dataset.py46-168 |
| LoogleDataset | Long-context QA | No | Yes | Common prefix sharing, grouped requests python/mlc_llm/bench/dataset.py170-261 |
| LLMPerfDataset | Synthetic workload | No | No | Configurable input/output lengths with std dev python/mlc_llm/bench/dataset.py264-343 |
| ReActDataset | Multi-turn agent traces | No | Yes | Grouped sequential requests with shared context python/mlc_llm/bench/dataset.py407-587 |
| WildChatDataset | Real chat conversations | No | No | Similar to ShareGPT, different source python/mlc_llm/bench/dataset.py590-708 |
| AzureLLMInferenceDataset | Production trace replay | Yes | No | Contains actual timestamps for replay python/mlc_llm/bench/dataset.py711-786 |
| JSONModeEvalDataset | Structured output | No | No | JSON schema validation python/mlc_llm/bench/dataset.py345-404 |

 Sources: [python/mlc_llm/bench/dataset.py22-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L22-L43) [python/mlc_llm/bench/dataset.py46-108](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L46-L108) [python/mlc_llm/bench/dataset.py170-209](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L170-L209) [python/mlc_llm/bench/dataset.py264-343](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L264-L343) [python/mlc_llm/bench/dataset.py407-587](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L407-L587) [python/mlc_llm/bench/dataset.py590-708](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L590-L708) [python/mlc_llm/bench/dataset.py711-786](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L711-L786) [python/mlc_llm/bench/dataset.py345-404](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L345-L404)

 
### Dataset Implementation

 
```

```

 **Key Methods**:

 
 - `generate_request_records(input_len, output_len, input_len_std, output_len_std)`: Generates list of `RequestRecord` objects [python/mlc_llm/bench/dataset.py35-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L35-L43)
 - For datasets with `timestamp_available=True`, timestamps are preserved for replay [python/mlc_llm/bench/dataset.py33](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L33-L33)
 - For datasets with `require_fake_warmup=True`, warmup uses synthetic requests to avoid prefix cache pollution [python/mlc_llm/bench/dataset.py29](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L29-L29)
 
 Sources: [python/mlc_llm/bench/dataset.py22-43](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L22-L43) [python/mlc_llm/bench/dataset.py46-167](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L46-L167) [python/mlc_llm/bench/dataset.py170-261](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L170-L261) [python/mlc_llm/bench/dataset.py711-786](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/dataset.py#L711-L786)

 
## Request Processors and Executors

 
### Request Processor Pipeline

 The `RequestProcessor` base class enables modular request transformation:

 
```

```

 **Processor Types**:

 
 - **Transformation**: Modify request attributes (model name, timestamps, sampling params) [python/mlc_llm/bench/request_processor.py124-211](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L124-L211)
 - **Orchestration**: Coordinate multiple processors (`SequentialProcessor`, `WarmupAndRun`) [python/mlc_llm/bench/request_processor.py256-369](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L256-L369)
 - **Analysis**: Post-process results to compute derived metrics [python/mlc_llm/bench/request_processor.py214-253](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L214-L253)
 
 Sources: [python/mlc_llm/bench/request_processor.py30-253](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L30-L253) [python/mlc_llm/bench/request_processor.py341-353](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L341-L353)

 
### Executor Implementations

 
```

```

 **FixedConcurrentRequestExecutor** [python/mlc_llm/bench/request_processor.py372-481](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L372-L481):

 
 - Maintains constant number of concurrent requests.
 - When a request completes, immediately starts next request [python/mlc_llm/bench/request_processor.py468-471](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L468-L471)
 - Supports `multi_round` mode to simulate conversation with history [python/mlc_llm/bench/request_processor.py374](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L374-L374)
 - Auto-calculates `num_processes` based on concurrency (max 32 requests per process) [python/mlc_llm/bench/request_processor.py382-385](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L382-L385)
 
 **FixTimestampExecutor** [python/mlc_llm/bench/request_processor.py484-600](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L484-L600):

 
 - Sends requests according to specified timestamps [python/mlc_llm/bench/request_processor.py575-580](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L575-L580)
 - Uses `asyncio.loop.call_at()` for precise scheduling [python/mlc_llm/bench/request_processor.py579](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L579-L579)
 - Accounts for `max_schedule_gap` tolerance in scheduling [python/mlc_llm/bench/request_processor.py487](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L487-L487)
 - Supports request rate (exponential inter-arrival) and dataset replay modes [python/mlc_llm/bench/request_processor.py136-148](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L136-L148)
 
 Sources: [python/mlc_llm/bench/request_processor.py372-600](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L372-L600)

 
## API Endpoints

 The `APIEndPoint` abstraction supports multiple serving backends:

 
```

```

 **Common Metrics Collected**:

 
 - `start_time`, `finish_time`: Monotonic timestamps [python/mlc_llm/bench/api_endpoint.py86-148](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L86-L148)
 - `time_to_first_token_s`: Time until first content chunk [python/mlc_llm/bench/api_endpoint.py106-107](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L106-L107)
 - `end_to_end_latency_s`: Total request duration [python/mlc_llm/bench/api_endpoint.py155](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L155-L155)
 - `first_chunk_output_str`: First chunk for verification [python/mlc_llm/bench/api_endpoint.py108](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L108-L108)
 - `output_str`: Complete generated text [python/mlc_llm/bench/api_endpoint.py126](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L126-L126)
 
 **Server Metrics** (OpenAIChatEndPoint only, requires `include_server_metrics=True`):

 
 - `prefill_tokens`, `prefill_tokens_per_s` [python/mlc_llm/bench/api_endpoint.py114-117](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L114-L117)
 - `inter_token_latency_s`, `decode_tokens_per_s` [python/mlc_llm/bench/api_endpoint.py118-119](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L118-L119)
 - Included in response `usage.extra` field [python/mlc_llm/bench/api_endpoint.py109](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L109-L109)
 
 Sources: [python/mlc_llm/bench/api_endpoint.py18-431](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L18-L431) [python/mlc_llm/bench/api_endpoint.py438-460](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/api_endpoint.py#L438-L460)

 
## Metrics Collection and Analysis

 
### Metrics Data Model

 
```

```

 Sources: [python/mlc_llm/bench/request_record.py14-54](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L14-L54)

 
### Metrics Computation

 The `MetricAnalyzer` processor computes derived metrics after request completion:

 
```

```

 **Key Metrics**:

 
 - **TTFT (Time To First Token)**: `time_to_first_token_s` - latency until first token appears [python/mlc_llm/bench/request_record.py39](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L39-L39)
 - **TPOT (Time Per Output Token)**: `(end_to_end_latency_s - time_to_first_token_s) / (output_tokens - first_chunk_tokens)` - average decode time per token [python/mlc_llm/bench/request_processor.py243-247](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L243-L247)
 - **ITL (Inter-Token Latency)**: `end_to_end_latency_s / output_tokens` - average time per token including prefill [python/mlc_llm/bench/request_processor.py249-250](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L249-L250)
 
 Sources: [python/mlc_llm/bench/request_processor.py214-252](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L214-L252)

 
### Report Generation

 The `generate_metrics_summary()` function aggregates metrics across all requests [python/mlc_llm/bench/request_record.py67-113](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L67-L113):

 **Aggregated Statistics**:

 
 - **Throughput**: `request_throughput`, `input_token_throughput`, `output_token_throughput` (per GPU) [python/mlc_llm/bench/request_record.py90-99](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L90-L99)
 - **Distributions**: P25, P50, P75, P90, P95, P99 percentiles for all latency metrics [python/mlc_llm/bench/request_record.py151](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L151-L151)
 - **Basic Stats**: Mean, min, max, stddev for each metric [python/mlc_llm/bench/request_record.py154-157](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L154-L157)
 - **Counts**: `num_total_requests`, `num_completed_requests`, `duration` [python/mlc_llm/bench/request_record.py87-89](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L87-L89)
 
 Sources: [python/mlc_llm/bench/request_record.py67-113](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L67-L113) [python/mlc_llm/bench/request_record.py169-272](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L169-L272)

 
## Performance Optimization Tools

 
### Debug Endpoints

 The MLC server exposes debug endpoints for performance analysis [python/mlc_llm/serve/entrypoints/debug_entrypoints.py1-133](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/debug_entrypoints.py#L1-L133):

 
```

```

 **Endpoint Usage**:

 
 - **Event Trace** [python/mlc_llm/serve/entrypoints/debug_entrypoints.py16-54](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/debug_entrypoints.py#L16-L54): Returns recorded events in Chrome Trace Event Format.
 - **CUDA Profiling** [python/mlc_llm/serve/entrypoints/debug_entrypoints.py60-83](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/debug_entrypoints.py#L60-L83): Starts/stops process-wise CUDA profiling via `mlc.debug_cuda_profiler_start/stop`.
 - **Engine Metrics** [python/mlc_llm/serve/entrypoints/debug_entrypoints.py86-106](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/debug_entrypoints.py#L86-L106): Dumps current engine internal metrics.
 - **Engine Reset** [python/mlc_llm/serve/entrypoints/debug_entrypoints.py109-132](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/debug_entrypoints.py#L109-L132): Resets engine state and clears metrics.
 
 Sources: [python/mlc_llm/serve/entrypoints/debug_entrypoints.py1-131](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/debug_entrypoints.py#L1-L131)

 
### CUDA Profiling Integration

 The `WarmupAndRun` processor supports CUDA profiling via server debug endpoints [python/mlc_llm/bench/request_processor.py311-320](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L311-L320):

 
```

```

 Sources: [python/mlc_llm/bench/request_processor.py311-320](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L311-L320) [python/mlc_llm/bench/__main__.py375-380](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L375-L380)

 
### Warmup Strategy

 The `WarmupAndRun` processor implements warmup with batch size variation [python/mlc_llm/bench/request_processor.py324-338](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L324-L338):

 
 - **First request**: 128 tokens to warm up large batches.
 - **Subsequent requests**: Incrementing output length to warm up different batch sizes.
 - **Fake Warmup**: For datasets with common prefix sharing (Loogle, ReAct), generates synthetic warmup requests to avoid prefix cache pollution [python/mlc_llm/bench/request_processor.py272-289](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L272-L289)
 
 Sources: [python/mlc_llm/bench/request_processor.py324-338](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L324-L338) [python/mlc_llm/bench/request_processor.py272-289](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_processor.py#L272-L289)

 
## Output Format

 
### CSV Report

 The benchmark outputs a CSV file with flattened metrics via `convert_reports_to_df` [python/mlc_llm/bench/request_record.py161-174](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L161-L174)

 
| Column | Description |
|---|---|
| exec_feature | JSON string with execution parameters python/mlc_llm/bench/request_record.py108 |
| num_gpus | Number of GPUs used python/mlc_llm/bench/request_record.py86 |
| duration | Total benchmark duration (seconds) python/mlc_llm/bench/request_record.py87 |
| request_throughput | Requests per second python/mlc_llm/bench/request_record.py90 |
| input_token_throughput | Input tokens per second python/mlc_llm/bench/request_record.py96 |
| output_token_throughput | Output tokens per second python/mlc_llm/bench/request_record.py98 |
| time_to_first_token_s.mean | Mean TTFT python/mlc_llm/bench/request_record.py154 |
| time_to_first_token_s.quantiles.p50 | Median TTFT python/mlc_llm/bench/request_record.py151 |

 Sources: [python/mlc_llm/bench/request_record.py153-166](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/request_record.py#L153-L166) [python/mlc_llm/bench/__main__.py159-162](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L159-L162)

 
### Debug Dump

 The `--debug-dump` flag writes detailed `RequestRecord` objects to JSON for debugging [python/mlc_llm/bench/__main__.py163-169](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L163-L169)

 Sources: [python/mlc_llm/bench/__main__.py163-169](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/bench/__main__.py#L163-L169)
