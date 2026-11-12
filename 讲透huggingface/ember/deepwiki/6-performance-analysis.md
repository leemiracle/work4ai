<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/ember · page 6 Performance Analysis · fetched 2026-10-26 -->

# Performance Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmark_results.txt](benchmark_results.txt)
- [ember/benchmark.py](ember/benchmark.py)

</details>



This document covers the performance benchmarking tools, metrics analysis, and optimization guidance for the Ember embedding server. It focuses on the system's ability to efficiently process embedding requests across different hardware configurations and batch sizes.

For information about setting up and running the embedding server, see [Model Serving](#4). For development and testing procedures, see [Testing and Simulation](#7.2).

## Benchmarking Architecture

The Ember system includes a comprehensive benchmarking framework designed to measure real-world performance characteristics of the embedding service under various load conditions.

### Benchmark Configuration System

```mermaid
graph TB
    BenchmarkConfig["BenchmarkConfig<br/>dataclass"]
    EmbeddingBenchmark["EmbeddingBenchmark<br/>class"]
    
    BenchmarkConfig --> EmbeddingBenchmark
    
    subgraph "Configuration Parameters"
        total_requests["total_requests: int<br/>Default: 50"]
        max_batch_size["max_batch_size: int<br/>Default: 64"]
        concurrent_requests["concurrent_requests: int<br/>Default: 5"]
        warm_up_iterations["warm_up_iterations: int<br/>Default: 2"]
    end
    
    subgraph "Test Data Generation"
        TEST_MESSAGES["TEST_MESSAGES<br/>List[str]"]
        generate_batch_messages["generate_batch_messages()<br/>method"]
    end
    
    subgraph "Request Execution"
        send_request["send_request()<br/>HTTP POST method"]
        ThreadPoolExecutor["ThreadPoolExecutor<br/>concurrent execution"]
        run_batch_benchmark["run_batch_benchmark()<br/>orchestration"]
    end
    
    BenchmarkConfig --> total_requests
    BenchmarkConfig --> max_batch_size
    BenchmarkConfig --> concurrent_requests
    BenchmarkConfig --> warm_up_iterations
    
    EmbeddingBenchmark --> TEST_MESSAGES
    EmbeddingBenchmark --> generate_batch_messages
    EmbeddingBenchmark --> send_request
    EmbeddingBenchmark --> ThreadPoolExecutor
    EmbeddingBenchmark --> run_batch_benchmark
```

Sources: [ember/benchmark.py:10-16](), [ember/benchmark.py:30-35](), [ember/benchmark.py:69-92]()

### Request Processing Pipeline

The benchmarking system executes performance tests by sending concurrent batched requests to the `/api/embed` endpoint and measuring response characteristics.

```mermaid
sequenceDiagram
    participant CLI as "benchmark.py CLI"
    participant Benchmark as "EmbeddingBenchmark"
    participant ThreadPool as "ThreadPoolExecutor"
    participant Server as "Ember Server<br/>localhost:11434"
    participant Analyzer as "analyze_results()"
    
    CLI->>Benchmark: "Initialize with BenchmarkConfig"
    Benchmark->>Benchmark: "warm_up() iterations"
    Benchmark->>Server: "Warm-up requests"
    Server-->>Benchmark: "Response timing"
    
    Benchmark->>ThreadPool: "Submit concurrent futures"
    
    loop "For each request batch"
        ThreadPool->>Benchmark: "send_request()"
        Benchmark->>Benchmark: "generate_batch_messages()"
        Benchmark->>Server: "POST /api/embed<br/>with batch payload"
        Server-->>Benchmark: "Embedding response + timing"
        Benchmark-->>ThreadPool: "Request result dict"
    end
    
    ThreadPool-->>Benchmark: "All results collected"
    Benchmark->>Analyzer: "Process timing data"
    Analyzer-->>CLI: "Performance statistics"
```

Sources: [ember/benchmark.py:94-102](), [ember/benchmark.py:42-67](), [ember/benchmark.py:69-92]()

## Performance Metrics Framework

### Core Metrics Collection

The system tracks comprehensive performance metrics across multiple dimensions to provide insight into system behavior under load.

| Metric Category | Specific Measurements | Source Method |
|----------------|----------------------|---------------|
| **Request Metrics** | total_requests, successful_requests, failed_requests | [analyze_results():106-108]() |
| **Throughput** | requests_per_second, documents_per_second | [analyze_results():128-129]() |
| **Latency Distribution** | average_duration, median_duration, p95_duration | [analyze_results():121-123]() |
| **Latency Bounds** | min_duration, max_duration, std_dev | [analyze_results():124-126]() |
| **Batch Processing** | documents_per_request, total_documents_processed | [analyze_results():119-120]() |

### Statistical Analysis Implementation

```mermaid
graph LR
    subgraph "Raw Results Collection"
        results["List[Dict]<br/>Request results"]
        successful["successful_requests<br/>Filter by success=True"]
        durations["durations: List[float]<br/>Extract timing data"]
    end
    
    subgraph "Statistical Calculations"
        mean["statistics.mean()<br/>Average latency"]
        median["statistics.median()<br/>Median latency"]
        stdev["statistics.stdev()<br/>Standard deviation"]
        percentile["sorted()[0.95 index]<br/>95th percentile"]
    end
    
    subgraph "Throughput Calculations"
        rps["requests_per_second<br/>requests / total_duration"]
        dps["documents_per_second<br/>(requests * batch_size) / total_duration"]
    end
    
    results --> successful
    successful --> durations
    durations --> mean
    durations --> median
    durations --> stdev
    durations --> percentile
    durations --> rps
    durations --> dps
```

Sources: [ember/benchmark.py:104-130]()

## Hardware Performance Comparison

### ANE vs CPU Performance Analysis

Based on empirical benchmarking results, the system demonstrates significant performance differences between Apple Neural Engine (ANE) and CPU-only execution modes.

#### Batch Size 32 Performance

| Hardware | Requests/sec | Documents/sec | Avg Latency (s) | P95 Latency (s) |
|----------|-------------|---------------|-----------------|-----------------|
| **CPU Only** | 14.691 | 470.118 | 3.154 | 3.395 |
| **ANE** | 20.928 | 669.693 | 2.343 | 2.388 |
| **Improvement** | +42.5% | +42.5% | -25.7% | -29.7% |

#### Batch Size 64 Performance

| Hardware | Requests/sec | Documents/sec | Avg Latency (s) | P95 Latency (s) |
|----------|-------------|---------------|-----------------|-----------------|
| **CPU Only** | 7.333 | 469.299 | 6.417 | 6.759 |
| **ANE** | 10.934 | 699.750 | 4.457 | 4.572 |
| **Improvement** | +49.1% | +49.1% | -30.5% | -32.4% |

Sources: [benchmark_results.txt:1-78]()

### Scaling Behavior Analysis

```mermaid
graph TB
    subgraph "ANE Scaling Pattern"
        ane_bs32["Batch Size 32<br/>669.693 docs/sec"]
        ane_bs64["Batch Size 64<br/>699.750 docs/sec"]
        ane_scaling["+4.5% throughput increase<br/>Linear scaling behavior"]
        
        ane_bs32 --> ane_scaling
        ane_bs64 --> ane_scaling
    end
    
    subgraph "CPU Scaling Pattern"
        cpu_bs32["Batch Size 32<br/>470.118 docs/sec"]
        cpu_bs64["Batch Size 64<br/>469.299 docs/sec"]
        cpu_scaling["-0.2% throughput change<br/>No scaling benefit"]
        
        cpu_bs32 --> cpu_scaling
        cpu_bs64 --> cpu_scaling
    end
    
    subgraph "Key Insight"
        conclusion["ANE scales with batch size<br/>CPU does not scale with batch size"]
    end
    
    ane_scaling --> conclusion
    cpu_scaling --> conclusion
```

Sources: [benchmark_results.txt:77-78]()

## Benchmarking Tool Usage

### Command Line Interface

The `benchmark.py` script provides a flexible command-line interface for performance testing with configurable parameters.

```bash
# Basic benchmark with default settings
python ember/benchmark.py

# Custom configuration
python ember/benchmark.py --requests 100 --batch-size 32 --concurrent 10 --warm-up 5
```

### Configuration Parameters

| Parameter | Default | Description | Impact |
|-----------|---------|-------------|---------|
| `--requests` | 50 | Total number of requests to execute | Higher values provide more statistical confidence |
| `--batch-size` | 64 | Documents per request batch | Affects memory usage and ANE utilization |
| `--concurrent` | 5 | Parallel request threads | Tests server concurrency handling |
| `--warm-up` | 2 | Initial requests before measurement | Eliminates cold-start effects |

Sources: [ember/benchmark.py:142-159]()

### Test Data Generation

The benchmark uses a predefined set of diverse test messages that are automatically replicated to fill the requested batch size.

```mermaid
graph LR
    TEST_MESSAGES["TEST_MESSAGES<br/>10 predefined strings"] --> generate_batch_messages["generate_batch_messages()"]
    
    subgraph "Batch Generation Logic"
        repeats["repeats = ceil(batch_size / 10)"]
        multiply["messages * repeats"]
        slice["[:batch_size] slice"]
    end
    
    generate_batch_messages --> repeats
    repeats --> multiply
    multiply --> slice
    slice --> payload["Request payload<br/>{'documents': [{'content': msg}]}"]
```

Sources: [ember/benchmark.py:17-28](), [ember/benchmark.py:36-48]()

## Performance Optimization Guidance

### Hardware Selection Recommendations

1. **Apple Neural Engine**: Preferred for production deployments due to 42-49% throughput improvements over CPU-only execution
2. **Batch Size Optimization**: Use larger batch sizes (64+) with ANE hardware to maximize throughput efficiency  
3. **Concurrent Request Handling**: The server efficiently handles concurrent requests; tune `concurrent_requests` parameter based on available system resources

### Monitoring and Analysis

Use the benchmark tool's statistical outputs to:

- **Latency Analysis**: Monitor P95 latency to understand worst-case performance
- **Throughput Tracking**: Track `documents_per_second` as the primary throughput metric
- **Scaling Validation**: Test different batch sizes to verify hardware scaling behavior
- **Regression Detection**: Compare benchmark results across model versions or configuration changes

Sources: [ember/benchmark.py:104-141]()

---

