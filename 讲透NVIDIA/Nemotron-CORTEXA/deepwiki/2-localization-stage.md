<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Nemotron-CORTEXA · page 2 Localization Stage · fetched 2026-10-26 -->

# Localization Stage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/cortexa/retrieval/embed_retrieve.py](src/cortexa/retrieval/embed_retrieve.py)

</details>



## Purpose and Scope

The Localization Stage is the first phase of the Nemotron-CORTEXA pipeline, responsible for narrowing the search space from entire repositories (thousands of files) to specific code entities (functions, classes) that require modification to fix a bug. This stage operates in two levels: **File Localization** uses semantic embeddings to rank repository files by relevance to bug descriptions, followed by **Entity Localization** which uses an agent-based system to identify specific code constructs within the top-ranked files.

This document provides an overview of how the two localization levels work together. For detailed implementation information, see:
- [File Localization with Embeddings](#2.1) - NV-EmbedCode embedding system
- [Entity Localization with Agents](#2.2) - LocalizeAgent and RepoGraph
- [Localization Evaluation Metrics](#2.3) - Precision/recall measurement

For information about how localization results are consumed, see [Repair Stage](#3).

**Sources:** [README.md:15-72](), [Diagram 4]()

---

## Two-Level Localization Architecture

The localization stage implements a coarse-to-fine strategy that progressively narrows the search space:

| Level | Input | Output | Granularity | Primary Component |
|-------|-------|--------|-------------|-------------------|
| **File Localization** | Bug description or LLM summary | Ranked list of files | File-level | `NIMModel` in `embed_retrieve.py` |
| **Entity Localization** | Top N ranked files + bug description | List of functions/classes | Entity-level | `LocalizeAgent` with `RepoGraph` |

### Localization Pipeline Flow

```mermaid
graph TB
    subgraph Input["Input Sources"]
        BugReport["Bug Report<br/>(problem_statement)"]
        LLMSummary["LLM Summary<br/>(optional)"]
        Repository["Repository<br/>(python_files)"]
        OracleFiles["Oracle Files<br/>(ground truth)"]
    end
    
    subgraph FileLocalization["File Localization (embed_retrieve.py)"]
        NIMModel["NIMModel<br/>(nvidia/nv-embedcode-7b-v1)"]
        ChunkFiles["chunk_files()<br/>max_length=450"]
        QueryEmbed["encode(doc_type='query')"]
        PassageEmbed["encode(doc_type='passage')"]
        CosineSim["cosine_similarity()<br/>get_ordered_files()"]
        
        BugReport --> QueryEmbed
        LLMSummary --> QueryEmbed
        Repository --> ChunkFiles
        ChunkFiles --> PassageEmbed
        QueryEmbed --> NIMModel
        PassageEmbed --> NIMModel
        NIMModel --> CosineSim
    end
    
    subgraph FileOutput["File Localization Output"]
        OrderedFiles["ordered_files.pickle<br/>Dict[instance_id -> (ranked_files, oracle_files)]"]
        EmbedCache["embeddings_chunk450_{instance_id}.pickle<br/>code, embeddings, scores"]
    end
    
    CosineSim --> OrderedFiles
    CosineSim --> EmbedCache
    OracleFiles -.-> OrderedFiles
    
    subgraph EntityLocalization["Entity Localization (entity_localization)"]
        TopFiles["Top N Files<br/>(num_top_files=6)"]
        RepoGraph["RepoGraph<br/>(code structure)"]
        LocalizeAgent["LocalizeAgent<br/>(num_turns=5)"]
        NavCommands["Navigation Commands<br/>(search, view, goto)"]
        
        OrderedFiles --> TopFiles
        TopFiles --> RepoGraph
        RepoGraph --> LocalizeAgent
        LocalizeAgent --> NavCommands
        NavCommands -.feedback.-> LocalizeAgent
    end
    
    subgraph EntityOutput["Entity Localization Output"]
        EntityResults["*_LA_DP_entity.jsonl<br/>instance_id, functions, classes"]
    end
    
    LocalizeAgent --> EntityResults
    
    subgraph RepairStage["Repair Stage Input"]
        RepairContext["Repair Context<br/>(files + entities)"]
    end
    
    EntityResults --> RepairContext
    OrderedFiles --> RepairContext
```

**Sources:** [README.md:15-72](), [embed_retrieve.py:1-269](), [Diagram 4]()

---

## File Localization Process

File localization reduces the search space from thousands of repository files to approximately 10-20 relevant candidates using semantic similarity.

### NIMModel Embedding System

The system uses the `NIMModel` class [embed_retrieve.py:43-90]() to interact with the NV-EmbedCode-7B-v1 API:

```mermaid
graph LR
    subgraph NIMModelClass["NIMModel Class"]
        Init["__init__()<br/>base_url, model_name, truncate"]
        Encode["encode()<br/>sentences, doc_type, instruct_type"]
        ToNumpy["_to_numpy()<br/>response -> np.ndarray"]
        
        Init --> Encode
        Encode --> ToNumpy
    end
    
    subgraph APIInteraction["OpenAI API Client"]
        ClientInit["OpenAI(base_url, api_key)"]
        EmbedCreate["client.embeddings.create()<br/>input_type, truncate"]
    end
    
    Init --> ClientInit
    Encode --> EmbedCreate
    EmbedCreate --> ToNumpy
    
    subgraph InstructTypes["Instruction Prefixes"]
        Original["'original'<br/>Given a bug description..."]
        LLMSummary["'llmsummary'<br/>Given a summary of bug..."]
    end
    
    Encode --> Original
    Encode --> LLMSummary
    
    subgraph DocTypes["Document Types"]
        Query["doc_type='query'<br/>+query_prefix"]
        Passage["doc_type='passage'<br/>no prefix"]
    end
    
    Encode --> Query
    Encode --> Passage
```

**Key configuration parameters:**
- `model_name`: `nvidia/nv-embedcode-7b-v1` (default)
- `base_url`: `https://integrate.api.nvidia.com/v1`
- `truncate`: `END` (default) - controls how content exceeding model context is handled
- `batch_size`: 16 (default) - number of texts encoded per API call
- `max_length`: 450 (default) - token limit per code chunk

**Sources:** [embed_retrieve.py:43-90](), [README.md:21-33]()

### Code Chunking and Ranking

The `chunk_files()` function [embed_retrieve.py:113-138]() splits repository files into fixed-size token chunks:

```mermaid
graph TB
    subgraph ChunkingProcess["chunk_files() Process"]
        PythonFiles["instance_obj.python_files<br/>Dict[filepath -> {'text': lines}]"]
        TokenizeFile["tokenizer(joined_lines)<br/>truncation=False"]
        SplitChunks["Split into chunks<br/>stride=max_length, overlap=0"]
        DecodeChunks["tokenizer.decode(chunk)<br/>prefix='[filepath]'"]
        FilterTests["skip_test=True<br/>is_test(filepath)"]
        
        PythonFiles --> FilterTests
        FilterTests --> TokenizeFile
        TokenizeFile --> SplitChunks
        SplitChunks --> DecodeChunks
    end
    
    subgraph RankingProcess["get_ordered_files() Process"]
        QueryEmbed["query_embeddings<br/>(1, embedding_dim)"]
        PassageEmbed["passage_embeddings<br/>(N_chunks, embedding_dim)"]
        CosineScore["cosine_similarity() * 100<br/>Normalized dot product"]
        HeapQueue["heapq.nlargest()<br/>Top indices by score"]
        DedupeFiles["remove_duplicates()<br/>Keep first occurrence"]
        
        QueryEmbed --> CosineScore
        PassageEmbed --> CosineScore
        CosineScore --> HeapQueue
        HeapQueue --> DedupeFiles
    end
    
    DecodeChunks --> PassageEmbed
```

**Output structure** saved to `cortexa_{target_set}_{query_type}_ordered_files.pickle` [embed_retrieve.py:231]():
```python
Dict[instance_id: str -> Tuple[
    List[str],  # ranked file paths (deduplicated)
    List[str]   # oracle files from ground truth patch
]]
```

**Sources:** [embed_retrieve.py:113-156](), [embed_retrieve.py:170-231]()

---

## Entity Localization Process

Entity localization refines file-level results to specific code entities (functions, classes, methods) using an agent-based exploration system.

### LocalizeAgent Architecture

The `LocalizeAgent` operates in a multi-turn interaction loop over a `RepoGraph` data structure:

```mermaid
graph TB
    subgraph Input["Entity Localization Input"]
        TopNFiles["Top N Files<br/>(num_top_files=6)"]
        BugDescription["Bug Description"]
        EmbedResults["ordered_files.pickle"]
    end
    
    subgraph RepoGraphBuild["RepoGraph Construction"]
        ParsePython["Parse Python files<br/>(tree-sitter)"]
        ExtractEntities["Extract functions/classes"]
        BuildGraph["Build call graph<br/>(networkx)"]
    end
    
    TopNFiles --> ParsePython
    ParsePython --> ExtractEntities
    ExtractEntities --> BuildGraph
    
    subgraph AgentLoop["LocalizeAgent Loop (num_turns=5)"]
        InitPrompt["Initial prompt<br/>+ bug description"]
        LLMResponse["LLM generates command"]
        ExecuteCommand["Execute navigation command"]
        UpdateContext["Update context window"]
        CheckDone["Check termination"]
        
        InitPrompt --> LLMResponse
        LLMResponse --> ExecuteCommand
        ExecuteCommand --> UpdateContext
        UpdateContext --> CheckDone
        CheckDone -.continue.-> LLMResponse
    end
    
    BuildGraph --> InitPrompt
    BugDescription --> InitPrompt
    
    subgraph Commands["Navigation Commands"]
        Search["search(query)<br/>Find entities by name/description"]
        View["view(entity)<br/>Show source code"]
        Goto["goto(entity)<br/>Navigate to definition"]
    end
    
    ExecuteCommand --> Search
    ExecuteCommand --> View
    ExecuteCommand --> Goto
    
    subgraph Output["Entity Localization Output"]
        EntityJSONL["*_LA_DP_entity.jsonl<br/>instance_id, model_name, found_entities"]
    end
    
    CheckDone -.done.-> EntityJSONL
```

**Sources:** [README.md:46-69](), [Diagram 4]()

### Output Format

Entity localization produces JSONL files with the following structure:

```
{instance_id}_entity_{model_config}_{temperature}.jsonl
```

Each line contains:
- `instance_id`: SWE-bench instance identifier
- `model_name`: Model configuration used for localization
- `functions`: List of identified function names
- `classes`: List of identified class names
- `context`: Aggregated code context from exploration

**Merging strategy:** Running entity localization with multiple model configurations and temperatures, then merging results, empirically increases recall [README.md:63]().

**Sources:** [README.md:47-69]()

---

## Integration with Repair Stage

The localization stage produces two key artifacts consumed by the repair stage:

```mermaid
graph LR
    subgraph LocalizationOutputs["Localization Stage Outputs"]
        FileRank["ordered_files.pickle<br/>Ranked file lists"]
        EntityList["*_entity.jsonl<br/>Function/class identifiers"]
    end
    
    subgraph RepairConfig["repair/config.py"]
        LocLogMap["get_default_loc_log_file_map()<br/>Maps instance -> artifacts"]
    end
    
    FileRank --> LocLogMap
    EntityList --> LocLogMap
    
    subgraph RepairAgent["RepairAgent (repair_agent.py)"]
        ContextRetrieval["Context retrieval<br/>Load ranked files + entities"]
        PatchGeneration["Patch generation<br/>repair() method"]
    end
    
    LocLogMap --> ContextRetrieval
    ContextRetrieval --> PatchGeneration
```

The `get_default_loc_log_file_map()` function in [repair/config.py]() (referenced in [README.md:71]()) configures which localization results to use for each instance. By default, it reads pre-processed files from `src/cortexa/retrieval/files/`:
- `cortexa_all_llmsummary_ordered_files.pickle` - File rankings for 707 instances (Lite + Verified)
- `cortexa_all_llmsummary_LA_DP_entity.jsonl` - Entity results

**Sources:** [README.md:71-72](), [Diagram 1]()

---

## Configuration and Usage

### Running File Localization

Command-line interface via `embed_retrieve.py` [README.md:21-33]():

```bash
python -m cortexa.retrieval.embed_retrieve \
    --model_name nvidia/nv-embedcode-7b-v1 \
    --base_url https://integrate.api.nvidia.com/v1 \
    --log_dir ./logs \
    --repo_playground ./repos \
    --batch_size 16 \
    --max_length 450 \
    --dataset_name_or_path princeton-nlp/SWE-bench_Verified \
    --query_type llmsummary \
    --instance_id <instance_id>
```

**Key parameters:**
- `--query_type`: `llmsummary` (uses LLM summaries) or `original` (uses raw problem statements)
- `--instance_id`: Comma-separated list of instances, or omit to process entire benchmark
- `--max_length`: Token limit for code chunks (default: 450)

**Environment requirement:** `NVIDIA_API_KEY` must be set [embed_retrieve.py:45-46]()

**Sources:** [README.md:21-44](), [embed_retrieve.py:234-268]()

### Running Entity Localization

Command-line interface via `entity_localization` module [README.md:49-59]():

```bash
python -m cortexa.localize.entity_localization \
    --log_dir ./logs \
    --repo_playground ./repos \
    --num_turns 5 \
    --num_top_files 6 \
    --embed_results cortexa_verified_llmsummary_ordered_files.pickle \
    --instance_id <instance_id>
```

**Key parameters:**
- `--num_turns`: Maximum agent interaction turns (default: 5)
- `--num_top_files`: Number of top-ranked files to explore (default: 6)
- `--embed_results`: Pickle file from file localization stage

**Model configuration:** Reads from `model_config.yml` with API keys loaded from environment variables via `os.environ[api_key_name]` [README.md:61]()

**Sources:** [README.md:49-63]()

---

## Data Flow and Artifacts

```mermaid
graph TD
    subgraph Inputs["Input Data"]
        Dataset["SWE-bench Dataset<br/>(load_dataset)"]
        Summaries["Bug Summaries<br/>(lite/verified_bug_summaries.jsonl)"]
        RepoFiles["Repository Files<br/>(instance_obj.python_files)"]
    end
    
    subgraph FileLocStage["File Localization Stage"]
        MainFunc["main(dataset, target_set)"]
        ProcessInstance["Process each instance:<br/>- Get queries<br/>- Chunk files<br/>- Compute embeddings<br/>- Rank files"]
    end
    
    Dataset --> MainFunc
    Summaries --> MainFunc
    RepoFiles --> ProcessInstance
    MainFunc --> ProcessInstance
    
    subgraph FileOutputs["File Localization Artifacts"]
        PerInstance["embeddings_chunk{max_length}_{instance_id}.pickle<br/>- code chunks<br/>- passage_embeddings<br/>- query_embeddings<br/>- scores<br/>- ranked docids"]
        AllInstances["cortexa_{target_set}_{query_type}_ordered_files.pickle<br/>Dict[instance_id -> (ranked_files, oracle_files)]"]
    end
    
    ProcessInstance --> PerInstance
    ProcessInstance --> AllInstances
    
    subgraph EntityLocStage["Entity Localization Stage"]
        LoadTopFiles["Load top N files from pickle"]
        AgentExplore["Agent exploration loop"]
    end
    
    AllInstances --> LoadTopFiles
    LoadTopFiles --> AgentExplore
    
    subgraph EntityOutputs["Entity Localization Artifacts"]
        DirectPrompt["*_DP_entity.jsonl<br/>(direct prompt)"]
        AgentResult["*_LA_entity.jsonl<br/>(localize agent)"]
        MergedResult["*_LA_DP_entity.jsonl<br/>(merged)"]
    end
    
    AgentExplore --> DirectPrompt
    AgentExplore --> AgentResult
    DirectPrompt --> MergedResult
    AgentResult --> MergedResult
    
    subgraph RepairInput["Repair Stage Inputs"]
        ConfigMap["repair/config.py<br/>get_default_loc_log_file_map()"]
    end
    
    AllInstances --> ConfigMap
    MergedResult --> ConfigMap
```

**Artifact naming conventions:**
- File localization: `cortexa_{dataset}_{query_type}_ordered_files.pickle`
- Entity localization: `{dataset}_{query_type}_{method}_entity.jsonl`
  - `method`: `DP` (direct prompt), `LA` (localize agent), or `LA_DP` (merged)

**Pre-computed artifacts:** The repository includes pre-computed localization results for SWE-bench Lite and Verified at:
- `src/cortexa/retrieval/files/cortexa_all_llmsummary_ordered_files.pickle` (707 instances) [README.md:44]()
- `src/cortexa/retrieval/files/cortexa_all_llmsummary_LA_DP_entity.jsonl`

**Sources:** [README.md:38-44](), [embed_retrieve.py:170-231](), [README.md:69-72]()

---

## Performance Characteristics

| Metric | File Localization | Entity Localization |
|--------|------------------|---------------------|
| **Input Size** | Full repository (1000s of files) | Top 6-10 files |
| **Output Size** | ~10-20 ranked files | ~5-15 entities |
| **Method** | Semantic similarity (embedding-based) | Agent-based exploration (LLM-driven) |
| **Parallelization** | Batch encoding (batch_size=16) | Sequential agent turns |
| **Caching** | Per-instance pickle files | JSONL streaming |
| **API Calls** | O(N_chunks / batch_size) | O(num_turns) per instance |

**Search space reduction:** File localization reduces search space by ~100x (e.g., 1000 files → 10 files), while entity localization further reduces by ~10x (e.g., 100 entities per file → 10 entities total).

**Evaluation:** Localization quality is measured against ground truth oracle files using standard information retrieval metrics. See [Localization Evaluation Metrics](#2.3) for details.

**Sources:** [README.md:15-72](), [Diagram 4]()

---

