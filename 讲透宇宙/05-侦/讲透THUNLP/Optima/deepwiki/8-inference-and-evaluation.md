<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/Optima · page 8 Inference and Evaluation · fetched 2026-11-02 -->

# Inference and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_revise.md](README_revise.md)

</details>



This document provides a comprehensive guide to Optima's inference and evaluation system, covering how to run inference on trained models, evaluate their performance, and interpret results. The inference system supports both standard batch inference and multi-agent self-consistency approaches to assess model improvements across iterations.

For detailed information on specific aspects of the inference system:
- For script usage and command-line arguments, see [Running Inference](#8.1)
- For multi-agent self-consistency methodology, see [Multi-Agent Self-Consistency](#8.2)
- For metrics and result interpretation, see [Evaluation Metrics](#8.3)

For information on the training pipeline that produces the checkpoints evaluated here, see [Training Pipeline Flow](#4.2).

## Purpose and Scope

The inference and evaluation system serves three primary purposes:

1. **Checkpoint Evaluation**: Run batch inference across all model checkpoints (iteration_0, iteration_1, etc.) to assess progressive improvements
2. **Multi-Agent Testing**: Evaluate models in multi-agent conversation scenarios with self-consistency sampling
3. **Performance Measurement**: Generate metrics for accuracy, token efficiency, and communication effectiveness

## Inference System Architecture

The inference system consists of two main components implemented in separate scripts: `inference_script.py` for batch checkpoint evaluation and `multi_sc_data_generate_script.py` for self-consistency testing.

```mermaid
graph TB
    subgraph "Checkpoint Storage"
        ModelRoot["Model Root Directory<br/>./checkpoints/arc_sft/"]
        Iter0["iteration_0/<br/>checkpoint files"]
        Iter1["iteration_1/<br/>checkpoint files"]
        IterN["iteration_N/<br/>checkpoint files"]
        
        ModelRoot --> Iter0
        ModelRoot --> Iter1
        ModelRoot --> IterN
    end
    
    subgraph "Inference Scripts"
        InferenceScript["inference_script.py<br/>Batch checkpoint evaluation"]
        MultiSCScript["multi_sc_data_generate_script.py<br/>Self-consistency testing"]
    end
    
    subgraph "vLLM Deployment"
        VLLMService["vLLM HTTP Service<br/>Port 8000+<br/>optima-vllm environment"]
        ModelInstance["Deployed Model Instance<br/>GPU device allocation"]
    end
    
    subgraph "Agent System"
        VllmAgent["VllmAgent instances<br/>HTTP communication"]
        ConvMemory["Conversation Memory<br/>llmMessage objects"]
    end
    
    subgraph "Datasets"
        TestData["Test Datasets<br/>arc, hotpot_qa, mwh_qa<br/>trivial_qa, cbt, math<br/>gsm8k, mmlu"]
    end
    
    subgraph "Output"
        InferResults["inference_results/<br/>Checkpoint-specific results"]
        Metrics["Evaluation Metrics<br/>Accuracy, tokens, efficiency"]
    end
    
    Iter0 --> InferenceScript
    Iter1 --> InferenceScript
    IterN --> InferenceScript
    
    Iter0 --> MultiSCScript
    
    InferenceScript --> VLLMService
    MultiSCScript --> VLLMService
    
    VLLMService --> ModelInstance
    ModelInstance --> VllmAgent
    
    VllmAgent --> ConvMemory
    
    TestData --> InferenceScript
    TestData --> MultiSCScript
    
    InferenceScript --> InferResults
    MultiSCScript --> InferResults
    
    InferResults --> Metrics
```

**Sources**: [README.md:94-137]()

## Batch Inference Pipeline

The `inference_script.py` provides batch inference capabilities to evaluate all checkpoints from a training run systematically. This script automates the process of deploying each checkpoint, running inference, and collecting results.

```mermaid
graph LR
    subgraph "Input Parameters"
        ModelRootPath["--model_root_path<br/>./checkpoints/arc_sft"]
        TokenizerPath["--tokenizer_path<br/>Pretrained tokenizer"]
        DatasetType["--dataset_type<br/>arc, mmlu, etc."]
        DevicePort["--device, --port<br/>GPU and port config"]
        OutputRoot["--output_root_path<br/>./inference_results"]
    end
    
    subgraph "Script Execution Flow"
        ParseArgs["Parse Arguments<br/>argparse"]
        ScanCheckpoints["Scan Checkpoints<br/>iteration_0..N"]
        IterateModels["For Each Checkpoint"]
        DeployVLLM["Deploy via vLLM<br/>optima-vllm env"]
        CreateAgents["Initialize VllmAgent"]
        RunInference["Execute Inference<br/>--num_thread workers"]
        SaveResults["Save Results<br/>checkpoint-specific files"]
    end
    
    subgraph "Output Structure"
        ResultFile["inference_results/<br/>iteration_X_results.json"]
        Predictions["Model predictions"]
        Performance["Performance data"]
    end
    
    ModelRootPath --> ParseArgs
    TokenizerPath --> ParseArgs
    DatasetType --> ParseArgs
    DevicePort --> ParseArgs
    OutputRoot --> ParseArgs
    
    ParseArgs --> ScanCheckpoints
    ScanCheckpoints --> IterateModels
    IterateModels --> DeployVLLM
    DeployVLLM --> CreateAgents
    CreateAgents --> RunInference
    RunInference --> SaveResults
    SaveResults --> ResultFile
    ResultFile --> Predictions
    ResultFile --> Performance
```

**Sources**: [README.md:96-110]()

### Key Command-Line Parameters

The `inference_script.py` accepts the following parameters:

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `--model_root_path` | Root directory containing checkpoint iterations | `./checkpoints/arc_sft` |
| `--tokenizer_path` | Path to pretrained tokenizer | `${pretrained_tokenizer_path}` |
| `--dataset_type` | Dataset for evaluation | `arc`, `mmlu`, `gsm8k`, etc. |
| `--device` | GPU index for first deployment | `0` |
| `--port` | First port number for vLLM service | `8000` |
| `--num_thread` | Number of parallel inference threads | `128` |
| `--output_root_path` | Directory for inference results | `./inference_results` |
| `--vllm_env` | Conda environment name for vLLM | `optima-vllm` |

**Sources**: [README.md:96-110]()

## Multi-Agent Self-Consistency

The `multi_sc_data_generate_script.py` implements multi-agent self-consistency evaluation, where multiple conversation samples are generated with temperature-based sampling to assess model robustness and consistency.

```mermaid
graph TB
    subgraph "Script Configuration"
        ModelPath["--model_path<br/>Specific checkpoint"]
        Temperature["--temperature<br/>Sampling parameter"]
        NumSamples["Multiple inference runs<br/>Self-consistency sampling"]
    end
    
    subgraph "Multi-Agent Conversation"
        AliceAgent["Alice VllmAgent<br/>HTTP to vLLM"]
        BobAgent["Bob VllmAgent<br/>HTTP to vLLM"]
        ConvLoop["Turn-taking Conversation<br/>Temperature sampling"]
        Memory["Conversation History<br/>llmMessage list"]
    end
    
    subgraph "Self-Consistency"
        Sample1["Sample 1<br/>temp=0.5"]
        Sample2["Sample 2<br/>temp=0.5"]
        SampleN["Sample N<br/>temp=0.5"]
        Aggregate["Aggregate Results<br/>Majority voting"]
    end
    
    subgraph "Output"
        SCResults["Self-consistency results<br/>Multiple trajectories"]
        ConsistencyMetrics["Consistency metrics<br/>Agreement rates"]
    end
    
    ModelPath --> AliceAgent
    ModelPath --> BobAgent
    Temperature --> ConvLoop
    
    AliceAgent --> ConvLoop
    BobAgent --> ConvLoop
    ConvLoop --> Memory
    
    Memory --> Sample1
    Memory --> Sample2
    Memory --> SampleN
    
    Sample1 --> Aggregate
    Sample2 --> Aggregate
    SampleN --> Aggregate
    
    Aggregate --> SCResults
    Aggregate --> ConsistencyMetrics
```

**Sources**: [README.md:112-137]()

### Self-Consistency Parameters

The `multi_sc_data_generate_script.py` uses these parameters:

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `--model_path` | Path to specific model checkpoint | `./checkpoints/arc_sft/iteration_0` |
| `--tokenizer_path` | Path to tokenizer | `${pretrained_tokenizer_path}` |
| `--device` | GPU index for deployment | `0` |
| `--port` | First port number for vLLM | `8000` |
| `--dataset_type` | Dataset for testing | `arc`, `mmlu`, etc. |
| `--num_thread` | Number of parallel threads | `128` |
| `--output_path` | Directory for output files | `./inference_results` |
| `--temperature` | Sampling temperature | `0.5` |
| `--vllm_env` | Conda environment for vLLM | `optima-vllm` |

**Sources**: [README.md:115-137]()

## vLLM Deployment Architecture

Both inference scripts leverage the `optima-vllm` environment to deploy models via the vLLM HTTP service. The deployment uses port-based model serving with GPU device allocation.

```mermaid
graph TB
    subgraph "Script Invocation"
        InfScript["inference_script.py or<br/>multi_sc_data_generate_script.py"]
        VLLMEnvParam["--vllm_env optima-vllm"]
        DeviceParam["--device 0"]
        PortParam["--port 8000"]
    end
    
    subgraph "vLLM Service Layer"
        CondaActivate["Activate optima-vllm<br/>conda environment"]
        VLLMServer["vLLM Server<br/>vllm==0.5.3"]
        HTTPEndpoint["HTTP Endpoint<br/>localhost:8000/v1/chat/completions"]
    end
    
    subgraph "Model Serving"
        LoadCheckpoint["Load Model Checkpoint<br/>from iteration_X/"]
        GPUAllocation["GPU Device Assignment<br/>CUDA device index"]
        ModelInstance["Inference-ready Model<br/>Flash Attention 2 enabled"]
    end
    
    subgraph "Agent Communication"
        VllmAgentClass["VllmAgent class<br/>HTTP client"]
        RequestFormat["Chat template formatting<br/>Alice_token, Bob_token"]
        ResponseParse["Parse completion response"]
    end
    
    InfScript --> VLLMEnvParam
    InfScript --> DeviceParam
    InfScript --> PortParam
    
    VLLMEnvParam --> CondaActivate
    DeviceParam --> GPUAllocation
    PortParam --> HTTPEndpoint
    
    CondaActivate --> VLLMServer
    VLLMServer --> LoadCheckpoint
    LoadCheckpoint --> GPUAllocation
    GPUAllocation --> ModelInstance
    
    ModelInstance --> HTTPEndpoint
    HTTPEndpoint --> VllmAgentClass
    VllmAgentClass --> RequestFormat
    RequestFormat --> ResponseParse
```

**Sources**: [README.md:96-137]()

## Supported Dataset Types

The inference system supports evaluation on multiple datasets, specified via the `--dataset_type` parameter:

| Dataset Type | Description | Domain |
|--------------|-------------|--------|
| `arc` | AI2 Reasoning Challenge | Commonsense reasoning |
| `hotpot_qa` | HotpotQA | Multi-hop question answering |
| `mwh_qa` | Multi-hop Wikipedia QA | Multi-hop reasoning |
| `trivial_qa` | TriviaQA | Factual question answering |
| `cbt` | Children's Book Test | Reading comprehension |
| `math` | MATH dataset | Mathematical reasoning |
| `gsm8k` | Grade School Math 8K | Math word problems |
| `mmlu` | Massive Multitask Language Understanding | General knowledge |

**Sources**: [README.md:104, 121, 132]()

## Output Directory Structure

Inference results are organized in the `inference_results/` directory with checkpoint-specific subdirectories:

```
inference_results/
├── arc_sft/
│   ├── iteration_0_results.json
│   ├── iteration_1_results.json
│   ├── iteration_N_results.json
│   └── metrics_summary.json
├── arc_dpo/
│   └── ...
└── self_consistency/
    ├── iteration_0_sc_results.json
    └── ...
```

Each result file contains:
- Model predictions for test samples
- Token usage statistics per sample
- Conversation length metrics (for multi-agent settings)
- Accuracy and performance data

**Sources**: [README.md:108, 134]()

## Integration with Training Pipeline

The inference system integrates tightly with the training pipeline to enable iterative evaluation:

```mermaid
graph LR
    subgraph "Training Phase"
        TrainScript["sft_script.py or<br/>dpo_script.py"]
        SaveCheckpoint["Save Checkpoint<br/>checkpoints/dataset_method/"]
        IterationN["iteration_N/"]
    end
    
    subgraph "Inference Phase"
        InferScript["inference_script.py"]
        ModelRootScan["Scan model_root_path<br/>Find all iterations"]
        EvalIteration["Evaluate Each<br/>iteration_0..N"]
    end
    
    subgraph "Analysis Phase"
        CompareResults["Compare Results<br/>Across iterations"]
        Metrics["Compute Metrics<br/>Accuracy, tokens, efficiency"]
        PlotTrends["Plot Improvement Trends"]
    end
    
    TrainScript --> SaveCheckpoint
    SaveCheckpoint --> IterationN
    
    IterationN --> InferScript
    InferScript --> ModelRootScan
    ModelRootScan --> EvalIteration
    
    EvalIteration --> CompareResults
    CompareResults --> Metrics
    Metrics --> PlotTrends
```

**Sources**: [README.md:94-110]()

## Thread-Based Parallel Inference

Both inference scripts support parallel execution via the `--num_thread` parameter, enabling efficient batch processing:

- Thread pool manages concurrent inference requests
- Each thread handles independent test samples
- VllmAgent instances communicate with the same vLLM service
- Thread synchronization ensures proper resource utilization

The recommended thread count is `128` for optimal GPU utilization, though this can be adjusted based on available resources and batch size requirements.

**Sources**: [README.md:107, 121, 133]()

## Usage Example: Complete Inference Workflow

A typical inference workflow involves:

1. **Standard Batch Inference**: Evaluate all checkpoints from a training run
   ```bash
   python inference_script.py \
       --model_root_path ./checkpoints/arc_sft \
       --tokenizer_path ${pretrained_tokenizer_path} \
       --dataset_type arc \
       --device 0 \
       --port 8000 \
       --num_thread 128 \
       --output_root_path ./inference_results \
       --vllm_env optima-vllm
   ```

2. **Self-Consistency Testing**: Test a specific checkpoint with multiple samples
   ```bash
   python multi_sc_data_generate_script.py \
       --model_path ./checkpoints/arc_sft/iteration_0 \
       --tokenizer_path ${pretrained_tokenizer_path} \
       --device 0 \
       --port 8000 \
       --dataset_type arc \
       --num_thread 128 \
       --output_path ./inference_results \
       --temperature 0.5 \
       --vllm_env optima-vllm
   ```

3. **Analyze Results**: Compare metrics across iterations to assess training improvements

**Sources**: [README.md:92-137]()

---

