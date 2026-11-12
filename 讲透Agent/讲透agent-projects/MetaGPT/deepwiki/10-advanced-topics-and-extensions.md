<!-- source: DeepWiki mcp.deepwiki.com · repo FoundationAgents/MetaGPT · page 10 Advanced Topics and Extensions · fetched 2026-10-30 -->

# Advanced Features and Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/fulltest.yaml](.github/workflows/fulltest.yaml)
- [.github/workflows/unittest.yaml](.github/workflows/unittest.yaml)
- [metagpt/config2.py](metagpt/config2.py)
- [metagpt/context.py](metagpt/context.py)
- [metagpt/context_mixin.py](metagpt/context_mixin.py)
- [metagpt/provider/base_llm.py](metagpt/provider/base_llm.py)
- [metagpt/provider/dashscope_api.py](metagpt/provider/dashscope_api.py)
- [metagpt/provider/human_provider.py](metagpt/provider/human_provider.py)
- [metagpt/provider/openai_api.py](metagpt/provider/openai_api.py)
- [metagpt/provider/qianfan_api.py](metagpt/provider/qianfan_api.py)
- [metagpt/software_company.py](metagpt/software_company.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/data/rsp_cache.json](tests/data/rsp_cache.json)
- [tests/metagpt/provider/mock_llm_config.py](tests/metagpt/provider/mock_llm_config.py)
- [tests/metagpt/provider/req_resp_const.py](tests/metagpt/provider/req_resp_const.py)
- [tests/metagpt/provider/test_base_llm.py](tests/metagpt/provider/test_base_llm.py)
- [tests/metagpt/provider/test_bedrock_api.py](tests/metagpt/provider/test_bedrock_api.py)
- [tests/metagpt/provider/test_openai.py](tests/metagpt/provider/test_openai.py)
- [tests/metagpt/test_config.py](tests/metagpt/test_config.py)
- [tests/metagpt/test_context.py](tests/metagpt/test_context.py)
- [tests/metagpt/test_context_mixin.py](tests/metagpt/test_context_mixin.py)
- [tests/mock/mock_llm.py](tests/mock/mock_llm.py)

</details>



This page documents the advanced capabilities and extension mechanisms in MetaGPT beyond the core multi-agent framework. The primary advanced feature is the Self-Supervised Prompt Optimization (SPO) system, which provides automated prompt engineering capabilities. For information about the core agent roles and actions, see [Core Multi-Agent Framework](#2). For LLM provider integration details, see [LLM Integration](#3).

## Self-Supervised Prompt Optimization (SPO)

The SPO system implements an automated prompt engineering framework that optimizes prompts through iterative self-supervised learning. It achieves cost efficiency improvements of 17.8-90.9× compared to conventional methods while maintaining competitive performance.

### SPO System Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        CLI["CLI Interface<br/>examples/spo/optimize.py"]
        StreamlitApp["Streamlit Web App<br/>metagpt/ext/spo/app.py"]
        PythonAPI["Python API<br/>PromptOptimizer class"]
    end
    
    subgraph "Core Components"
        PromptOptimizer["PromptOptimizer<br/>optimize() method<br/>_optimize_prompt()"]
        QuickExecute["QuickExecute<br/>prompt_execute()"]
        QuickEvaluate["QuickEvaluate<br/>prompt_evaluate()"]
    end
    
    subgraph "Utility Classes"
        DataUtils["DataUtils<br/>load_results()<br/>get_best_round()"]
        PromptUtils["PromptUtils<br/>write_prompt()<br/>create_round_directory()"]
        EvaluationUtils["EvaluationUtils<br/>execute_prompt()<br/>evaluate_prompt()"]
        LoadUtils["load module<br/>load_meta_data()<br/>set_file_name()"]
    end
    
    subgraph "LLM Management"
        SPO_LLM["SPO_LLM<br/>optimize_llm<br/>evaluate_llm<br/>execute_llm"]
        RequestType["RequestType enum<br/>OPTIMIZE<br/>EVALUATE<br/>EXECUTE"]
    end
    
    subgraph "Configuration System"
        YAMLTemplate["Template YAML<br/>prompt, requirements<br/>qa pairs, count"]
        ConfigFile["config2.yaml<br/>Multi-model configuration"]
    end
    
    subgraph "Storage System"
        WorkspaceDir["workspace/<project>/<br/>prompts/round_n/<br/>prompt.txt, answers.txt"]
        ResultsJSON["results.json<br/>optimization history"]
    end
    
    CLI --> PromptOptimizer
    StreamlitApp --> PromptOptimizer
    PythonAPI --> PromptOptimizer
    
    PromptOptimizer --> QuickExecute
    PromptOptimizer --> QuickEvaluate
    PromptOptimizer --> DataUtils
    PromptOptimizer --> PromptUtils
    PromptOptimizer --> EvaluationUtils
    
    QuickExecute --> SPO_LLM
    QuickEvaluate --> SPO_LLM
    SPO_LLM --> RequestType
    
    LoadUtils --> YAMLTemplate
    PromptOptimizer --> LoadUtils
    
    SPO_LLM --> ConfigFile
    
    PromptUtils --> WorkspaceDir
    DataUtils --> ResultsJSON
    
    style PromptOptimizer fill:#e1f5fe
    style SPO_LLM fill:#f3e5f5
    style YAMLTemplate fill:#fff3e0
```

Sources: [metagpt/ext/spo/components/optimizer.py:19-137](), [metagpt/ext/spo/app.py:1-302](), [examples/spo/optimize.py:1-50]()

### SPO Optimization Process Flow

The SPO system follows a structured optimization cycle with distinct phases for execution, evaluation, and prompt generation.

```mermaid
graph TD
    subgraph "Initialization Phase"
        LoadTemplate["load.load_meta_data()<br/>Load YAML template<br/>prompt, requirements, qa"]
        InitLLM["SPO_LLM.initialize()<br/>optimize_kwargs<br/>evaluate_kwargs<br/>execute_kwargs"]
        CreateOptimizer["PromptOptimizer()<br/>optimized_path<br/>max_rounds<br/>template"]
    end
    
    subgraph "Round 1 (Initial)"
        InitPrompt["_handle_first_round()<br/>Use original template prompt"]
        ExecuteInit["QuickExecute.prompt_execute()<br/>Generate initial answers"]
        EvaluateInit["QuickEvaluate.prompt_evaluate()<br/>Mark as successful (baseline)"]
        SaveInit["PromptUtils.write_prompt()<br/>PromptUtils.write_answers()"]
    end
    
    subgraph "Optimization Loop (Rounds 2-N)"
        LoadBest["DataUtils.get_best_round()<br/>Find best performing prompt"]
        GenOptPrompt["_generate_optimized_prompt()<br/>PROMPT_OPTIMIZE_PROMPT<br/>LLM optimization request"]
        ExecuteOpt["EvaluationUtils.execute_prompt()<br/>QuickExecute with new prompt"]
        CompareResults["EvaluationUtils.evaluate_prompt()<br/>QuickEvaluate comparison<br/>4x repetition voting"]
        SaveRound["DataUtils.save_results()<br/>Update results.json"]
    end
    
    subgraph "Completion"
        FinalResult["show_final_result()<br/>Display best prompt<br/>Performance summary"]
    end
    
    LoadTemplate --> InitLLM
    InitLLM --> CreateOptimizer
    CreateOptimizer --> InitPrompt
    
    InitPrompt --> ExecuteInit
    ExecuteInit --> EvaluateInit
    EvaluateInit --> SaveInit
    
    SaveInit --> LoadBest
    LoadBest --> GenOptPrompt
    GenOptPrompt --> ExecuteOpt
    ExecuteOpt --> CompareResults
    CompareResults --> SaveRound
    
    SaveRound --> LoadBest
    LoadBest --> FinalResult
    
    style LoadTemplate fill:#e1f5fe
    style GenOptPrompt fill:#f3e5f5
    style CompareResults fill:#fff3e0
```

Sources: [metagpt/ext/spo/components/optimizer.py:40-137](), [metagpt/ext/spo/utils/evaluation_utils.py:25-81](), [metagpt/ext/spo/components/evaluator.py:15-76]()

## Template Configuration System

The SPO system uses YAML-based templates to define optimization tasks. Templates specify the initial prompt, requirements, and evaluation criteria.

### Template Structure

| Component | Description | Example |
|-----------|-------------|---------|
| `prompt` | Initial prompt text | `"Please solve the following problem."` |
| `requirements` | Optimization objectives | `"Generate more thinking, use humorous language"` |
| `count` | Target word count | `50` or `None` |
| `qa` | Question-answer pairs for evaluation | List of `{question, answer}` objects |

### Template Management Classes

```mermaid
graph TB
    subgraph "Template Loading"
        LoadModule["load.py<br/>set_file_name()<br/>load_meta_data()"]
        YAMLFile["settings/*.yaml<br/>Template definitions"]
        GlobalState["FILE_NAME global<br/>SAMPLE_K = 3"]
    end
    
    subgraph "Template Processing"
        DataParsing["yaml.safe_load()<br/>Extract prompt, requirements<br/>Parse qa pairs"]
        RandomSampling["random.sample(qa, k)<br/>Select subset for iteration"]
        CountFormatting["Format count constraint<br/>within N words"]
    end
    
    subgraph "Streamlit Template Editor"
        TemplateMode["Template Mode<br/>Use Existing / Create New"]
        QAEditor["Q&A Editor<br/>Add/Delete/Edit pairs"]
        SaveTemplate["save_yaml_template()<br/>Write to settings/"]
    end
    
    LoadModule --> YAMLFile
    YAMLFile --> DataParsing
    DataParsing --> RandomSampling
    DataParsing --> CountFormatting
    
    GlobalState --> LoadModule
    
    TemplateMode --> QAEditor
    QAEditor --> SaveTemplate
    SaveTemplate --> YAMLFile
    
    style LoadModule fill:#e1f5fe
    style QAEditor fill:#f3e5f5
```

Sources: [metagpt/ext/spo/utils/load.py:1-49](), [metagpt/ext/spo/app.py:14-36](), [metagpt/ext/spo/app.py:139-193]()

## Multi-LLM Architecture

The SPO system uses a three-LLM architecture to separate concerns between optimization, evaluation, and execution phases.

### LLM Role Specialization

| Role | LLM Instance | Default Model | Temperature | Purpose |
|------|-------------|---------------|-------------|---------|
| Optimization | `optimize_llm` | `claude-3-5-sonnet-20240620` | 0.7 | Generate improved prompts |
| Evaluation | `evaluate_llm` | `gpt-4o-mini` | 0.3 | Compare prompt performance |
| Execution | `execute_llm` | `gpt-4o-mini` | 0.0 | Generate consistent outputs |

### SPO_LLM Implementation

```mermaid
graph TB
    subgraph "SPO_LLM Class"
        Singleton["SPO_LLM singleton<br/>_instance class variable<br/>initialize() / get_instance()"]
        ThreeLLMs["optimize_llm<br/>evaluate_llm<br/>execute_llm"]
        ResponserMethod["responser()<br/>RequestType routing<br/>LLM selection"]
    end
    
    subgraph "RequestType Enum"
        OPTIMIZE["RequestType.OPTIMIZE<br/>Prompt improvement"]
        EVALUATE["RequestType.EVALUATE<br/>Performance comparison"]
        EXECUTE["RequestType.EXECUTE<br/>Answer generation"]
    end
    
    subgraph "Configuration Integration"
        ModelsConfig["ModelsConfig.default()<br/>Model configuration lookup"]
        LLMConfig["model_config.model_copy()<br/>Dynamic parameter setting"]
        BaseLLM["LLM(llm_config)<br/>MetaGPT LLM instance"]
    end
    
    subgraph "Response Processing"
        XMLExtraction["extract_content()<br/>Parse XML tags<br/><modification>, <prompt>"]
        AsyncCompletion["llm.acompletion(messages)<br/>Async LLM calls"]
    end
    
    Singleton --> ThreeLLMs
    ResponserMethod --> OPTIMIZE
    ResponserMethod --> EVALUATE
    ResponserMethod --> EXECUTE
    
    ModelsConfig --> LLMConfig
    LLMConfig --> BaseLLM
    BaseLLM --> ThreeLLMs
    
    AsyncCompletion --> XMLExtraction
    ResponserMethod --> AsyncCompletion
    
    style Singleton fill:#e1f5fe
    style ResponserMethod fill:#f3e5f5
```

Sources: [metagpt/ext/spo/utils/llm_client.py:17-84](), [metagpt/ext/spo/utils/llm_client.py:86-107]()

## Usage Interfaces

The SPO system provides three primary interfaces for different use cases and user preferences.

### Interface Comparison

| Interface | Entry Point | Configuration | Use Case |
|-----------|-------------|---------------|----------|
| CLI | `examples/spo/optimize.py` | Command line arguments | Automated/scripted optimization |
| Python API | `PromptOptimizer` class | Direct instantiation | Programmatic integration |
| Streamlit Web UI | `metagpt/ext/spo/app.py` | Interactive forms | User-friendly experimentation |

### Command Line Interface

The CLI interface supports comprehensive parameter configuration:

```bash
python -m examples.spo.optimize \
  --opt-model "claude-3-5-sonnet-20240620" \
  --eval-model "gpt-4o-mini" \
  --exec-model "gpt-4o-mini" \
  --workspace "workspace" \
  --max-rounds 10 \
  --template "Poem.yaml" \
  --name "Poem"
```

Sources: [examples/spo/optimize.py:7-49]()

### Streamlit Web Interface

The web interface provides real-time optimization monitoring and template editing capabilities, including:

- Interactive template creation and editing at [metagpt/ext/spo/app.py:139-193]()
- Live optimization logging with `StreamlitSink` at [metagpt/ext/spo/app.py:197-216]()
- Results visualization with expandable round summaries at [metagpt/ext/spo/app.py:38-73]()
- Prompt testing functionality at [metagpt/ext/spo/app.py:259-297]()

Sources: [metagpt/ext/spo/app.py:75-302]()

## Data Management and Persistence

The SPO system maintains comprehensive records of optimization history and results through structured file organization.

### Workspace Structure

```
workspace/
└── {project_name}/
    └── prompts/
        ├── results.json          # Optimization history metadata
        ├── round_1/
        │   ├── prompt.txt       # Round 1 prompt text
        │   └── answers.txt      # Generated answers
        ├── round_2/
        │   ├── prompt.txt
        │   └── answers.txt
        └── round_n/
            ├── prompt.txt
            └── answers.txt
```

### DataUtils Operations

The `DataUtils` class manages optimization data with methods for:

- `load_results()`: Load optimization history from `results.json`
- `get_best_round()`: Find the highest-performing successful prompt
- `create_result_data()`: Structure round results with metadata
- `save_results()`: Persist results to JSON with timestamp
- `list_to_markdown()`: Format Q&A pairs for prompt generation

Sources: [metagpt/ext/spo/utils/data_utils.py:11-107](), [metagpt/ext/spo/utils/prompt_utils.py:6-35]()

## Evaluation Methodology

The SPO system employs a robust evaluation methodology with voting-based consensus and randomized comparison to ensure reliable optimization decisions.

### Evaluation Process

```mermaid
graph TB
    subgraph "Evaluation Pipeline"
        ExecutePrompt["QuickExecute.prompt_execute()<br/>Generate answers for qa pairs<br/>Using execute_llm"]
        MultipleEvals["4x QuickEvaluate calls<br/>EVALUATION_REPETITION = 4<br/>Consensus voting"]
        RandomSwap["random.random() < 0.5<br/>Randomize sample order<br/>Prevent bias"]
    end
    
    subgraph "Comparison Logic"
        EvalPrompt["EVALUATE_PROMPT template<br/>Compare samples A vs B<br/>Requirements alignment"]
        ChooseExtraction["extract_content(response, 'choose')<br/>Parse A or B selection"]
        SwapLogic["Account for randomization<br/>True result determination"]
    end
    
    subgraph "Success Determination"
        VotingCount["Count True/False results<br/>true_count vs false_count"]
        MajorityRule["succeed = true_count > false_count<br/>Democratic consensus"]
        TokenCounting["count_tokens(sample)<br/>tiktoken cl100k_base encoding"]
    end
    
    ExecutePrompt --> MultipleEvals
    MultipleEvals --> RandomSwap
    RandomSwap --> EvalPrompt
    
    EvalPrompt --> ChooseExtraction
    ChooseExtraction --> SwapLogic
    SwapLogic --> VotingCount
    
    VotingCount --> MajorityRule
    VotingCount --> TokenCounting
    
    style MultipleEvals fill:#e1f5fe
    style VotingCount fill:#f3e5f5
```

Sources: [metagpt/ext/spo/utils/evaluation_utils.py:10-82](), [metagpt/ext/spo/components/evaluator.py:15-76]()

## Extension and Customization Points

The SPO system provides several extension points for customization and integration with other systems.

### Key Extension Interfaces

| Component | Extension Method | Purpose |
|-----------|------------------|---------|
| Template System | Custom YAML schemas | Domain-specific optimization tasks |
| Evaluation Logic | `QuickEvaluate` subclassing | Custom performance metrics |
| LLM Integration | `SPO_LLM` configuration | Alternative model providers |
| Storage Backend | `DataUtils` modification | Custom persistence layers |

### Integration with MetaGPT Core

The SPO system integrates with MetaGPT's core infrastructure through:

- **LLM Provider System**: Uses `ModelsConfig` and `LLM` classes for model management
- **Configuration Framework**: Leverages `config2.yaml` for multi-provider setup  
- **Logging Infrastructure**: Utilizes MetaGPT's logging system with `logger`
- **File Management**: Compatible with MetaGPT's project structure conventions

Sources: [metagpt/ext/spo/utils/llm_client.py:30-51](), [examples/spo/config2.example.yaml:1-26]()

---

