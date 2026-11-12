<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/compute-eval · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [compute_eval/__init__.py](compute_eval/__init__.py)
- [compute_eval/main.py](compute_eval/main.py)

</details>



This document provides a comprehensive overview of the ComputeEval system architecture, focusing on the core components, their interactions, and the overall data flow within the system. It explains how the different modules work together to generate and evaluate CUDA code samples produced by Large Language Models (LLMs).

For specific details about the Code Generation process, see [Code Generation](#3.1). For information about the Evaluation process, see [Code Evaluation](#3.2).

## 1. High-Level Architecture Overview

ComputeEval is structured as a pipeline-oriented architecture centered around two primary workflows: code generation and code evaluation. The system is designed with a clear separation of concerns, allowing independent operation of its major components.

```mermaid
graph TD
    subgraph "Command Interface Layer"
        CLI["CLI Interface
        (main.py)"]
    end
    
    subgraph "Core Process Layer"
        Generate["Code Generation
        (generate_completions.py)"]
        Evaluate["Evaluation
        (evaluation.py)"]
    end
    
    subgraph "Service Layer"
        Models["Model Integration
        (models.py)"]
        DataOps["Data Handling
        (data.py)"]
        Executor["Code Execution
        (executor.py)"]
    end
    
    CLI -->|"generate_samples_with_config()"| Generate
    CLI -->|"evaluate_functional_correctness_with_config()"| Evaluate
    Generate --> Models
    Generate --> DataOps
    Evaluate --> DataOps
    Evaluate --> Executor
    Executor --> DataOps
    
    classDef default font-family:Arial;
```

**Diagram: High-Level System Architecture**

Sources: [compute_eval/main.py:16-52]()

## 2. Command Interface Layer

The Command Interface Layer serves as the entry point to the system, exposing two primary commands through a CLI built with the Fire library.

```mermaid
classDiagram
    class FireCLI {
        +main()
        +generate_samples_with_config()
        +evaluate_functional_correctness_with_config()
        +load_config()
    }
    
    class ConfigFile {
        YAML configuration
    }
    
    FireCLI --> ConfigFile: reads
    
    note for FireCLI "Located in main.py\nProvides CLI interface"
```

**Diagram: Command Layer Structure**

The CLI accepts YAML configuration files that define parameters for both code generation and evaluation processes. The `load_config()` function reads these files and passes the parameters to the appropriate functions.

Sources: [compute_eval/main.py:16-52]()

## 3. Core Process Layer

The Core Process Layer contains the two primary workflows of the system: Code Generation and Code Evaluation.

```mermaid
flowchart TB
    subgraph "Configuration"
        Config["YAML Config Files"]
    end
    
    subgraph "Generation Process"
        GenProcess["generate_samples()"]
        ModelInvoke["Generate Model Completions"]
        ParseFunc["Parse Function Body"]
        WriteOutputs["Write Completions"]
    end
    
    subgraph "Evaluation Process"
        EvalProcess["evaluate_functional_correctness()"]
        CheckCorrect["check_correctness()"]
        EstimatePass["estimate_pass_at_k()"]
    end
    
    Config -->|"Parameters"| GenProcess
    Config -->|"Parameters"| EvalProcess
    
    GenProcess --> ModelInvoke
    ModelInvoke --> ParseFunc
    ParseFunc --> WriteOutputs
    
    EvalProcess --> CheckCorrect
    CheckCorrect --> EstimatePass
```

**Diagram: Core Process Flow**

The generation process creates CUDA code using LLMs, while the evaluation process tests the correctness of the generated code and calculates pass@k metrics.

Sources: [compute_eval/main.py:19-20]()

## 4. Data Flow Architecture

The data flow in ComputeEval follows a pipeline pattern, where problem definitions flow into the generation process, resulting in code samples that are then evaluated for correctness.

```mermaid
flowchart LR
    ProblemFile["Problem File
    (JSONL)"] -->|"read_problems()"| ProblemDict["Problem Dictionary"]
    
    ProblemDict -->|"Input"| Generation["generate_samples()"]
    ModelConfig["Model Configuration"] -->|"Parameters"| Generation
    
    Generation -->|"Output"| SampleFile["Sample File
    (JSONL)"]
    
    SampleFile -->|"Input"| Evaluation["evaluate_functional_correctness()"]
    ProblemDict -->|"Reference"| Evaluation
    
    Evaluation -->|"Compile & Execute"| Results["Evaluation Results
    (JSONL)"]
    
    subgraph "Key Data Entities"
        ProblemEntity["Problem:
        - problem_id
        - description
        - function_signature
        - reference_solution
        - tests"]
        
        SampleEntity["Sample:
        - problem_id
        - completion
        - model_id
        - timestamp"]
        
        ResultEntity["Result:
        - problem_id
        - completion_id
        - status (pass/fail)
        - error_message
        - execution_time"]
    end
    
    ProblemFile -.->|"Contains"| ProblemEntity
    SampleFile -.->|"Contains"| SampleEntity
    Results -.->|"Contains"| ResultEntity
```

**Diagram: System Data Flow**

Sources: [compute_eval/main.py:19-20]()

## 5. Model Integration Architecture

The system integrates with various LLM providers through a flexible model interface that supports both preset models and custom model configurations.

```mermaid
graph TD
    subgraph "Model Selection"
        ModelParam["model parameter"] -->|"Maps to"| PresetModels["Preset Models"]
        CustomConfig["custom_model configuration"] -->|"Configures"| CustomAPI["Custom Model API"]
    end
    
    subgraph "Preset Model Options"
        llama["llama3.1-70b"]
        mixtral["mixtral-8x22b"]
        gemma["gemma-2b"]
        nemotron["nemotron-mini-4b"]
        starcoder["starcoder2-7b"]
    end
    
    PresetModels --> llama
    PresetModels --> mixtral
    PresetModels --> gemma
    PresetModels --> nemotron
    PresetModels --> starcoder
    
    subgraph "Authentication"
        NEMO["NEMO_API_KEY"]
        OPENAI["OPENAI_API_KEY"]
        ANTHROPIC["ANTHROPIC_API_KEY"]
    end
    
    NEMO -->|"For NVIDIA models"| ModelAccess["Model Access"]
    OPENAI -->|"For OpenAI/custom models"| ModelAccess
    ANTHROPIC -->|"For Anthropic models"| ModelAccess
    
    ModelAccess --> ModelInvocation["Model Invocation"]
    
    CustomAPI -->|"api_endpoint & model_id"| ExternalAPI["External LLM API"]
    ExternalAPI --> ModelInvocation
```

**Diagram: Model Integration Architecture**

Sources: [README.md:38-130]()

## 6. Execution Environment Architecture

The execution environment is designed to safely compile and run generated CUDA code, preventing potential security issues while accurately testing the code's functionality.

```mermaid
flowchart TD
    subgraph "Execution Process"
        CheckCorrectness["check_correctness()"]
        CompileCUDA["compile_cuda_file()"]
        ExecuteBinary["execute_binary()"]
        Validation["Validate Results"]
    end
    
    subgraph "Security Measures"
        Sandboxing["Sandboxed Execution"]
        Timeout["Execution Timeout"]
        AllowExec["--allow-execution Flag"]
    end
    
    CheckCorrectness --> CompileCUDA
    CompileCUDA --> ExecuteBinary
    ExecuteBinary --> Validation
    
    Sandboxing -->|"Protects"| ExecuteBinary
    Timeout -->|"Limits"| ExecuteBinary
    AllowExec -->|"Required for"| CheckCorrectness
```

**Diagram: Execution Environment Architecture**

Sources: [README.md:76-80]()

## 7. Component Relationships

The following diagram maps the key system components to their interactions, showing how data and control flow between different parts of the system.

```mermaid
classDiagram
    class Main {
        +main()
        +load_config()
        +generate_samples_with_config()
        +evaluate_functional_correctness_with_config()
    }
    
    class Generator {
        +generate_samples()
        +generate_model_completions()
        +parse_function_body()
    }
    
    class Evaluator {
        +evaluate_functional_correctness()
        +check_correctness()
        +estimate_pass_at_k()
    }
    
    class Executor {
        +compile_cuda_file()
        +execute_binary()
        +safe_execution_environment()
    }
    
    class DataHandler {
        +read_problems()
        +stream_jsonl()
        +write_completions_to_dir()
        +write_jsonl()
    }
    
    class ModelInterface {
        +get_model_completion()
        +format_prompt()
        +handle_api_auth()
    }
    
    Main --> Generator: invokes
    Main --> Evaluator: invokes
    Generator --> ModelInterface: uses
    Generator --> DataHandler: uses
    Evaluator --> Executor: uses
    Evaluator --> DataHandler: uses
    Executor --> DataHandler: uses
```

**Diagram: Component Relationship Mapping**

Sources: [compute_eval/main.py:16-52]()

## 8. Configuration Architecture

The system uses YAML configuration files to control its behavior, allowing flexible experimental setups without code changes.

```mermaid
graph TD
    subgraph "Configuration Types"
        GenConfig["Generation Configuration"]
        EvalConfig["Evaluation Configuration"]
    end
    
    subgraph "Generation Parameters"
        ProblemFile["problem_file"]
        SampleFile["sample_file"]
        Model["model or custom_model"]
        NumSamples["num_samples_per_problem"]
        SystemPrompt["system_prompt"]
        MaxTokens["max_tokens"]
    end
    
    subgraph "Evaluation Parameters"
        SampleFileEval["sample_file"]
        ProblemFileEval["problem_file"]
        KValues["k (for pass@k)"]
        Workers["n_workers"]
        Timeout["timeout"]
        SaveDir["save_completions_dir"]
    end
    
    GenConfig --> ProblemFile
    GenConfig --> SampleFile
    GenConfig --> Model
    GenConfig --> NumSamples
    GenConfig --> SystemPrompt
    GenConfig --> MaxTokens
    
    EvalConfig --> SampleFileEval
    EvalConfig --> ProblemFileEval
    EvalConfig --> KValues
    EvalConfig --> Workers
    EvalConfig --> Timeout
    EvalConfig --> SaveDir
```

**Diagram: Configuration Architecture**

Sources: [README.md:82-163]()

## Summary

The ComputeEval system architecture is built around two primary workflows:
1. **Code Generation**: Uses LLMs to generate CUDA code samples for predefined problems
2. **Code Evaluation**: Tests the functional correctness of generated code and calculates pass@k metrics

The system design emphasizes:
- **Separation of concerns**: Each component has a clear responsibility
- **Configurable operation**: YAML files control system behavior
- **Secure execution**: Sandboxed environment for running generated code
- **Flexible model integration**: Support for multiple LLM providers
- **Streamlined data flow**: Consistent data formats throughout the pipeline

This architecture enables efficient evaluation of LLM capabilities for CUDA code generation, providing a framework that can be extended with additional models and evaluation methodologies.

Sources: [README.md:1-209](), [compute_eval/main.py:16-52]()

---

