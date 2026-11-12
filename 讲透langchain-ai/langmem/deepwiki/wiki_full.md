# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/docs/concepts/conceptual_guide.md](docs/docs/concepts/conceptual_guide.md)
- [pyproject.toml](pyproject.toml)

</details>



LangMem is a memory management system for LLM applications that enables agents to learn and adapt from their interactions over time. It provides prebuilt utilities for memory extraction, storage, optimization, and retrieval that work with any storage system, with native integration for LangGraph's storage layer.

For detailed information about specific memory types, see [Memory Management](#2). For integration with different agent frameworks, see [Integration](#4). For API documentation, see [API Reference](#9).

## Purpose and Scope

LangMem addresses the challenge of giving LLM applications persistent, searchable memory. The system extracts important information from conversations, optimizes agent behavior through prompt refinement, and maintains long-term memory across sessions.

The library follows a two-layer design:
- **Core API Layer**: Stateless functions like `create_memory_manager` and `create_prompt_optimizer` that work with any storage system
- **Stateful Integration Layer**: Components like `create_memory_store_manager` and memory tools that integrate with LangGraph's `BaseStore`

LangMem supports two main processing approaches:
- **Hot Path Processing**: Agent-driven memory operations during conversations using `create_manage_memory_tool` and `create_search_memory_tool`
- **Background Processing**: Deferred memory extraction and consolidation using `ReflectionExecutor`

Sources: [README.md:1-96](), [docs/docs/concepts/conceptual_guide.md:318-339](), [pyproject.toml:1-93]()

## LangMem High-Level System Architecture

LangMem follows a two-layer architecture that separates stateless core operations from stateful integrations:

```mermaid
graph TB
    subgraph "LangMem Core Architecture"
        subgraph "Core API Layer (Stateless)"
            MM["create_memory_manager<br/>Memory Extraction & Updates"]
            PO["create_prompt_optimizer<br/>Prompt Refinement"]
            TE["create_thread_extractor<br/>Conversation Summarization"]
            SM["summarize_messages<br/>Short-term Memory"]
        end
        
        subgraph "Stateful Integration Layer"
            MSM["create_memory_store_manager<br/>Persistent Memory Operations"]
            MMT["create_manage_memory_tool<br/>Agent Memory Tools"]
            SMT["create_search_memory_tool<br/>Agent Search Tools"]
        end
        
        subgraph "Background Processing"
            RE["ReflectionExecutor<br/>Deferred Memory Processing"]
        end
    end
    
    subgraph "LangGraph Ecosystem"
        BS["BaseStore<br/>Storage Interface"]
        CRA["create_react_agent<br/>Agent Framework"]
        LGS["LangGraph Services"]
    end
    
    subgraph "LLM Providers"
        OAI["OpenAI<br/>GPT Models"]
        ANT["Anthropic<br/>Claude Models"]
        LS["LangSmith<br/>Observability"]
    end
    
    subgraph "Application Layer"
        CA["Custom Agents"]
        CB["Chatbots"]
        WF["Workflows"]
    end
    
    MM --> MSM
    PO --> MSM
    TE --> MM
    SM --> MSM
    
    MSM --> BS
    MMT --> BS
    SMT --> BS
    MMT --> CRA
    SMT --> CRA
    
    RE --> MSM
    RE --> LGS
    
    MM --> OAI
    MM --> ANT
    PO --> OAI
    PO --> ANT
    MSM --> LS
    
    CRA --> CA
    MSM --> CB
    MMT --> WF
    SMT --> WF
```

The **Core API Layer** provides stateless functions that transform memory state without side effects. These work with any storage system and include:
- `create_memory_manager`: Extract and consolidate memories from conversations
- `create_prompt_optimizer`: Optimize system prompts based on feedback
- `create_thread_extractor`: Generate conversation summaries
- `summarize_messages`: Handle short-term memory within token limits

The **Stateful Integration Layer** builds on the Core API to provide persistent memory operations with LangGraph's `BaseStore`:
- `create_memory_store_manager`: Automatically persist extracted memories
- `create_manage_memory_tool`: Agent tools for creating/updating/deleting memories
- `create_search_memory_tool`: Agent tools for semantic memory search

Sources: [README.md:30-87](), [docs/docs/concepts/conceptual_guide.md:318-339](), [pyproject.toml:8-17]()

## Core Components

LangMem is built around several key components that handle different aspects of memory management:

| Component | Purpose | Key Functions | Layer |
|-----------|---------|---------------|--------|
| **Memory Manager** | Extract, consolidate, and update memories from conversations | `create_memory_manager` | Core API |
| **Store Manager** | Persist extracted memories to LangGraph storage | `create_memory_store_manager` | Stateful Integration |
| **Memory Tools** | Agent-accessible memory operations during conversations | `create_manage_memory_tool`, `create_search_memory_tool` | Stateful Integration |
| **Prompt Optimizer** | Improve system behavior through prompt refinement | `create_prompt_optimizer`, `create_multi_prompt_optimizer` | Core API |
| **Message Summarizer** | Handle short-term memory and conversation context | `summarize_messages` | Core API |
| **Thread Extractor** | Extract conversation summaries and insights | `create_thread_extractor` | Core API |
| **Reflection Executor** | Background processing coordination for deferred memory operations | `ReflectionExecutor` | Background Processing |

### Memory Types and Processing Pipeline

```mermaid
graph LR
    subgraph "Memory Types"
        SEM["Semantic Memory<br/>Facts & Knowledge<br/>User Preferences"]
        EPI["Episodic Memory<br/>Past Experiences<br/>Interaction History"]
        PROC["Procedural Memory<br/>System Behavior<br/>Prompt Rules"]
        ST["Short-term Memory<br/>Conversation Context<br/>Message Summarization"]
    end
    
    subgraph "Storage Patterns"
        COL["Collection Pattern<br/>Individual Documents<br/>Searchable & Updateable"]
        PROF["Profile Pattern<br/>Single Document<br/>Current State Only"]
        RULES["Rule Pattern<br/>System Instructions<br/>Behavioral Guidelines"]
    end
    
    subgraph "Processing Modes"
        HOT["Hot Path Processing<br/>During Conversation<br/>Agent Tools"]
        BG["Background Processing<br/>After Conversation<br/>Reflection & Analysis"]
    end
    
    subgraph "Core Operations"
        EXT["Extract<br/>New Information"]
        UPD["Update<br/>Existing Memories"]
        CON["Consolidate<br/>Related Information"]
        DEL["Delete<br/>Outdated Information"]
        SEARCH["Search<br/>Relevant Context"]
    end
    
    SEM --> COL
    SEM --> PROF
    EPI --> COL
    PROC --> RULES
    ST --> PROF
    
    HOT --> EXT
    HOT --> UPD
    HOT --> SEARCH
    BG --> CON
    BG --> DEL
    BG --> UPD
    
    COL --> EXT
    COL --> UPD
    COL --> CON
    COL --> DEL
    COL --> SEARCH
    PROF --> UPD
    RULES --> UPD
```

Sources: [docs/docs/concepts/conceptual_guide.md:19-292](), [docs/docs/concepts/conceptual_guide.md:295-316]()

## Memory Types and Processing

LangMem supports multiple memory types that mirror human memory systems, each with specific storage patterns and processing approaches:

### Semantic Memory
Stores facts and knowledge using two patterns:
- **Collections** (`enable_inserts=True`): Unbounded knowledge stored as individual documents, searchable and updateable
- **Profiles** (with Pydantic schemas): Structured information that updates in-place for current state

### Episodic Memory  
Captures successful interactions as learning examples using collection pattern with Episode schemas:
- Situation context and relevant environment
- Thought processes and reasoning steps
- Actions taken in response
- Results achieved and why they worked

### Procedural Memory
Encodes system behavior and response patterns:
- Core personality through system prompts
- Behavioral guidelines using rule patterns
- Adaptive improvements via `create_prompt_optimizer`

### Short-term Memory
Handles conversation context within token limits:
- Message summarization using `summarize_messages`
- Running conversation state with profile pattern
- Context management for ongoing interactions

| Memory Type | Storage Pattern | Key Functions | Use Case |
|-------------|-----------------|---------------|----------|
| Semantic Collections | Collection | `create_memory_manager(enable_inserts=True)` | Facts, preferences, knowledge |
| Semantic Profiles | Profile | `create_memory_manager(schemas=[UserProfile])` | Current user state, settings |
| Episodic | Collection | `create_memory_manager(schemas=[Episode])` | Learning from past successes |
| Procedural | Rules/Prompts | `create_prompt_optimizer()` | System behavior adaptation |
| Short-term | Profile | `summarize_messages()` | Conversation context |

Sources: [docs/docs/concepts/conceptual_guide.md:19-292](), [docs/docs/concepts/conceptual_guide.md:295-316]()

## Processing Approaches

LangMem supports two distinct processing approaches for memory formation:

### Hot Path Processing (Agent-Driven)
Memory operations occur during conversations with immediate latency impact:
- Agents use `create_manage_memory_tool` to actively decide what to store
- `create_search_memory_tool` provides semantic search during conversations  
- Memory updates happen in real-time as part of agent tool execution
- Higher latency but immediate context availability

### Background Processing (Subconscious)
Memory operations occur after conversations without latency impact:
- `ReflectionExecutor` coordinates deferred memory processing
- `create_memory_store_manager` handles batch memory extraction
- Pattern analysis and consolidation without blocking user interactions
- Delayed updates but comprehensive analysis

| Processing Type | Latency Impact | Update Speed | Processing Load | Implementation |
|----------------|----------------|--------------|-----------------|----------------|
| Hot Path | Higher | Immediate | During Response | `create_manage_memory_tool`, `create_search_memory_tool` |
| Background | None | Delayed | Between/After Calls | `ReflectionExecutor`, `create_memory_store_manager` |

## Integration Patterns

LangMem follows a two-layer integration design:

### 1. Core API Layer (Stateless)
Side-effect-free functions that work with any storage system:
- `create_memory_manager`: Transform memory state without persistence
- `create_prompt_optimizer`: Update prompts based on feedback
- `create_multi_prompt_optimizer`: Optimize multiple prompts together
- `summarize_messages`: Handle conversation context
- `create_thread_extractor`: Extract conversation insights

### 2. Stateful Integration Layer  
Components that integrate with LangGraph's `BaseStore`:
- `create_memory_store_manager`: Automatically persist extracted memories
- `create_manage_memory_tool`: Agent tools for memory operations
- `create_search_memory_tool`: Agent tools for memory retrieval

```mermaid
graph TB
    subgraph "Core API Layer (Stateless)"
        MM["create_memory_manager"]
        PO["create_prompt_optimizer"]
        MPO["create_multi_prompt_optimizer"]
        SM["summarize_messages"]
        TE["create_thread_extractor"]
    end
    
    subgraph "Stateful Integration Layer"
        MSM["create_memory_store_manager"]
        MMT["create_manage_memory_tool"]
        SMT["create_search_memory_tool"]
    end
    
    subgraph "LangGraph Storage"
        BS["BaseStore"]
        IMS["InMemoryStore"]
        PGS["AsyncPostgresStore"]
        PS["Platform Store"]
    end
    
    subgraph "Agent Frameworks"
        CRA["create_react_agent"]
        CA["Custom Agents"]
        CREW["CrewAI"]
    end
    
    MM --> MSM
    PO --> MSM
    MPO --> MSM
    
    MSM --> BS
    MMT --> BS
    SMT --> BS
    
    BS --> IMS
    BS --> PGS
    BS --> PS
    
    MMT --> CRA
    SMT --> CRA
    MSM --> CA
    MSM --> CREW
```

Sources: [docs/docs/concepts/conceptual_guide.md:295-316](), [docs/docs/concepts/conceptual_guide.md:318-339](), [README.md:30-87]()

## Storage and Namespace Organization

The storage system is built on LangGraph's `BaseStore` interface and supports hierarchical namespace organization:

### Namespace Structure
Namespaces provide natural data segmentation:
- **Multi-level hierarchies**: Organization → User → Application
- **Template variables**: Dynamic resolution using `"{user_id}"` syntax
- **Contextual keys**: Unique identification within namespaces

### Storage Backends
- **InMemoryStore**: Development and testing
- **AsyncPostgresStore**: Production persistence
- **LangGraph Platform Store**: Default cloud deployment

```mermaid
graph TB
    subgraph "Namespace Templates"
        UserNamespace["('memories', '{user_id}')"]
        TeamNamespace["('team', '{team_id}')"]
        GlobalNamespace["('global',)"]
    end
    
    subgraph "Storage Interface"
        BaseStore["BaseStore Interface"]
        DirectAccess["Direct Access<br/>store.get()"]
        SemanticSearch["Semantic Search<br/>store.search()"]
        MetadataFilter["Metadata Filtering<br/>store.search(filter={})"]
    end
    
    subgraph "Concrete Stores"
        InMemoryStore["InMemoryStore<br/>(Development)"]
        PostgresStore["AsyncPostgresStore<br/>(Production)"]
        PlatformStore["LangGraph Platform Store<br/>(Default)"]
    end
    
    UserNamespace --> BaseStore
    TeamNamespace --> BaseStore
    GlobalNamespace --> BaseStore
    
    BaseStore --> DirectAccess
    BaseStore --> SemanticSearch
    BaseStore --> MetadataFilter
    
    BaseStore --> InMemoryStore
    BaseStore --> PostgresStore
    BaseStore --> PlatformStore
    
    style BaseStore fill:#e8f5e8
    style UserNamespace fill:#fff3e0
    style InMemoryStore fill:#f3e5f5
```

Sources: [docs/docs/concepts/conceptual_guide.md:341-377](), [README.md:40-62]()

## Key Design Principles

LangMem is built on several key principles:

1. **Dual Processing Modes**: Support both real-time and background memory processing
2. **Storage Agnostic**: Core functionality works with any storage system
3. **Framework Flexible**: Native LangGraph integration with support for other frameworks
4. **Memory Type Diversity**: Support for semantic, episodic, and procedural memory
5. **Namespace Organization**: Hierarchical organization for multi-tenancy
6. **Prompt Optimization**: Continuous improvement through feedback-driven optimization

This architecture enables LangMem to serve as a comprehensive memory management solution for language model applications, from simple chatbots to complex multi-agent systems.

Sources: [docs/docs/concepts/conceptual_guide.md:1-377](), [README.md:1-96](), [src/langmem/__init__.py:1-28]()

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This document covers installing LangMem and setting up your environment to start building memory-enabled agents. It includes both basic installation for users and development setup for contributors.

For information about integrating LangMem with specific frameworks after installation, see [Agent Integration](#4.2). For storage backend configuration, see [Storage Types](#7.1).

## System Requirements

LangMem requires Python 3.10 or higher and integrates with the LangChain ecosystem.

### Core Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | >=3.10 | Runtime environment |
| LangChain | >=0.3.15 | Core framework |
| LangGraph | >=0.6.0 | State management and tools |

**Sources:** [pyproject.toml:6](), [pyproject.toml:9-10](), [pyproject.toml:13]()

## Installation

### Standard Installation

Install LangMem from PyPI:

```bash
pip install -U langmem
```

This installs the current version (0.0.30) with all core dependencies including `langchain`, `langgraph`, `trustcall`, and LLM provider integrations.

### Development Installation

For development work, clone the repository and use `uv`:

```bash
# Clone the repository
git clone https://github.com/langchain-ai/langmem
cd langmem

# Install with development dependencies
uv sync --group dev
```

**Sources:** [README.md:20-22](), [pyproject.toml:3](), [pyproject.toml:26-36]()

## Environment Setup

### API Key Configuration

LangMem requires an LLM provider API key. Configure your environment with one of the supported providers:

```bash
# Anthropic (recommended)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."
```

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | Anthropic Claude models | `sk-ant-api03-...` |
| `OPENAI_API_KEY` | OpenAI models and embeddings | `sk-...` |
| `LANGSMITH_API_KEY` | Optional: LangSmith tracing | `ls__...` |

**Sources:** [README.md:24-28](), [pyproject.toml:14-15]()

## Core Dependencies

### LangMem Runtime Dependencies

```mermaid
graph TB
    subgraph "LangMem Core"
        langmem["langmem==0.0.30"]
    end
    
    subgraph "LangChain Framework"
        langchain["langchain>=0.3.15"]
        langchain_core["langchain-core>=0.3.46"]
        langgraph["langgraph>=0.6.0"]
        langgraph_checkpoint["langgraph-checkpoint>=2.0.12"]
    end
    
    subgraph "LLM Providers"
        langchain_openai["langchain-openai>=0.3.1"]
        langchain_anthropic["langchain-anthropic>=0.3.3"]
    end
    
    subgraph "Core Libraries"
        trustcall["trustcall>=0.0.39"]
        langsmith["langsmith>=0.3.8"]
    end
    
    subgraph "Storage Backends"
        InMemoryStore["InMemoryStore"]
        AsyncPostgresStore["AsyncPostgresStore"]
    end
    
    langmem --> langchain
    langmem --> langchain_core
    langmem --> langgraph
    langmem --> langgraph_checkpoint
    langmem --> langchain_openai
    langmem --> langchain_anthropic
    langmem --> trustcall
    langmem --> langsmith
    
    langgraph --> InMemoryStore
    langgraph --> AsyncPostgresStore
```

### Key Function Dependencies

| LangMem Function | Required Dependencies | Purpose |
|------------------|----------------------|---------|
| `create_manage_memory_tool` | `langgraph`, `langchain-core` | Memory management tools |
| `create_search_memory_tool` | `langgraph`, `langchain-core` | Memory search tools |
| `create_memory_manager` | `trustcall`, LLM provider | Memory extraction |
| `create_react_agent` | `langgraph.prebuilt` | Agent creation |

**Sources:** [pyproject.toml:8-17](), [README.md:36-38](), [README.md:49-57]()

## Basic Setup Verification

### Quick Start Test

After installation, verify LangMem works with this minimal example:

```python
# Test basic imports
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent

# Create basic store
store = InMemoryStore()

# Verify tools can be created
memory_tool = create_manage_memory_tool(namespace=("test",))
search_tool = create_search_memory_tool(namespace=("test",))

print("LangMem setup successful!")
```

### Storage Configuration Test

```python
# Test with embedding support
from langgraph.store.memory import InMemoryStore

store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)

print("Storage with embeddings configured!")
```

**Sources:** [README.md:40-46](), [README.md:52-54]()

## Development Setup

For contributors working on LangMem itself:

### Development Environment Setup

```mermaid
graph TB
    subgraph "Development Workspace"
        uv_workspace["uv workspace"]
        langmem_root["langmem (root package)"]
        evals_gen["evals/gen (evaluation tools)"]
    end
    
    subgraph "Development Tools"
        pytest_suite["pytest test suite"]
        ruff_tools["ruff linting & formatting"]
        langgraph_cli["langgraph-cli development"]
        mkdocs_docs["mkdocs documentation"]
    end
    
    subgraph "Quality Checks"
        test_run["uv run pytest"]
        lint_check["uv run ruff check"]
        format_check["uv run ruff format"]
        docs_build["uv run mkdocs build"]
    end
    
    uv_workspace --> langmem_root
    uv_workspace --> evals_gen
    
    langmem_root --> pytest_suite
    langmem_root --> ruff_tools
    langmem_root --> langgraph_cli
    langmem_root --> mkdocs_docs
    
    pytest_suite --> test_run
    ruff_tools --> lint_check
    ruff_tools --> format_check
    mkdocs_docs --> docs_build
```

### Development Dependencies

| Category | Key Packages | Purpose |
|----------|-------------|---------|
| Testing | `pytest>=8.3.4`, `pytest-xdist>=3.6.1` | Test execution |
| Code Quality | `ruff>=0.12.12` | Linting and formatting |
| LangGraph Tools | `langgraph-cli[inmem]>=0.1.70` | Development utilities |
| Documentation | `mkdocs>=1.6.1`, `mkdocs-material>=9.6.1` | Docs generation |

**Sources:** [pyproject.toml:55-56](), [pyproject.toml:27-36](), [pyproject.toml:38-53]()

## Verification Steps

After installation, verify the setup:

### For Production Installation

```python
import langmem
print(langmem.__version__)  # Should print 0.0.28
```

### For Development Installation

```bash
# Run tests
uv run pytest

# Check code quality
uv run ruff check
uv run ruff format --check

# Build documentation (if docs group installed)
uv run mkdocs build
```

### Testing Workspace Members

```bash
# Test the main package
uv run pytest

# Test evaluation utilities
cd evals/gen
uv run pytest
```

**Sources:** [pyproject.toml:2-3](), [pyproject.toml:55-56](), [pyproject.toml:32-35]()

---

# Page: Key Concepts

# Key Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/concepts/conceptual_guide.md](docs/docs/concepts/conceptual_guide.md)
- [src/langmem/__init__.py](src/langmem/__init__.py)
- [src/langmem/prompts/types.py](src/langmem/prompts/types.py)

</details>



This document explains the fundamental concepts underlying LangMem's memory system for LLM applications. It covers memory types, processing modes, storage patterns, and architectural layers that enable persistent, searchable memory capabilities.

For specific implementation details about memory managers and tools, see [Memory Management](#2). For integration with agents and workflows, see [Integration](#4). For storage configuration and setup, see [Storage](#7).

## Memory Types

LangMem supports four distinct memory types, each serving specific purposes in LLM applications. These types align with human memory structures to create adaptive, context-aware systems.

```mermaid
graph TB
    subgraph "Memory Types and Code Entities"
        subgraph "Semantic Memory"
            SM["`**Semantic Memory**
            Facts & Knowledge`"]
            SMCode["`create_memory_manager
            enable_inserts=True
            Collection Pattern`"]
            SMProfile["`enable_inserts=False
            Profile Pattern`"]
        end
        
        subgraph "Episodic Memory"
            EM["`**Episodic Memory**
            Past Experiences`"]
            EMCode["`Episode schema
            BaseModel classes
            Collection storage`"]
        end
        
        subgraph "Procedural Memory"
            PM["`**Procedural Memory**
            System Behavior`"]
            PMCode["`create_prompt_optimizer
            Prompt TypedDict
            metaprompt strategy`"]
        end
        
        subgraph "Short-term Memory"
            STM["`**Short-term Memory**
            Conversation Context`"]
            STMCode["`summarize_messages
            RunningSummary
            SummarizationNode`"]
        end
    end
    
    SM --> SMCode
    SM --> SMProfile
    EM --> EMCode
    PM --> PMCode
    STM --> STMCode
```

**Sources:** [docs/docs/concepts/conceptual_guide.md:19-29](), [src/langmem/__init__.py:1-27]()

### Semantic Memory: Facts and Knowledge

Semantic memory stores factual information and knowledge that grounds agent responses. Two primary storage patterns are available:

| Pattern | Code Entity | Use Case | Enable Inserts |
|---------|-------------|----------|----------------|
| **Collection** | `create_memory_manager(enable_inserts=True)` | Unbounded knowledge accumulation | `True` |
| **Profile** | `create_memory_manager(enable_inserts=False)` | Current state tracking | `False` |

Collections create individual memory documents that can be searched and updated independently. The memory enrichment process in `create_memory_manager` balances memory creation with consolidation to prevent over-extraction while maintaining recall.

Profiles maintain a single document representing current state, updating in-place rather than creating new records. This pattern works well for user preferences, settings, and other state-based information.

**Sources:** [docs/docs/concepts/conceptual_guide.md:30-165]()

### Episodic Memory: Past Experiences  

Episodic memory captures successful interactions as learning examples. Unlike semantic memory's factual storage, episodic memory preserves full interaction context including situation, reasoning process, and success factors.

Episodic memories typically use Pydantic `BaseModel` schemas with fields like `observation`, `thoughts`, `action`, and `result` to structure experience data systematically.

**Sources:** [docs/docs/concepts/conceptual_guide.md:167-248]()

### Procedural Memory: System Instructions

Procedural memory encodes agent behavior patterns and response guidelines. The `create_prompt_optimizer` function with strategies like `metaprompt` enables iterative refinement of system prompts based on interaction feedback.

The `Prompt` TypedDict in [src/langmem/prompts/types.py:7-34]() provides structured prompt management with fields for `name`, `prompt`, `update_instructions`, and `when_to_update`.

**Sources:** [docs/docs/concepts/conceptual_guide.md:250-292](), [src/langmem/prompts/types.py:7-34]()

### Short-term Memory: Conversation Context

Short-term memory manages immediate conversation context within token limits. Key components include:

- `summarize_messages` for conversation summarization
- `RunningSummary` for incremental context management  
- `SummarizationNode` for workflow integration

This memory type focuses on maintaining conversational coherence rather than long-term knowledge retention.

**Sources:** [src/langmem/__init__.py:7-8]()

## Processing Modes

LangMem supports two distinct processing modes that determine when and how memories are formed.

```mermaid
graph LR
    subgraph "Processing Modes"
        subgraph "Hot Path Processing"
            HP["`**Hot Path**
            During Conversation`"]
            HPTools["`create_manage_memory_tool
            create_search_memory_tool
            Agent-driven decisions`"]
        end
        
        subgraph "Background Processing"  
            BP["`**Background**
            After Conversation`"]
            BPCode["`ReflectionExecutor
            create_thread_extractor
            Deferred analysis`"]
        end
        
        subgraph "Trade-offs"
            Latency["`**Latency Impact**
            Hot: Higher latency
            Background: No latency`"]
            
            Speed["`**Update Speed**
            Hot: Immediate
            Background: Delayed`"]
        end
    end
    
    HP --> HPTools
    BP --> BPCode
    HP --> Latency
    BP --> Latency
    HP --> Speed
    BP --> Speed
```

**Sources:** [docs/docs/concepts/conceptual_guide.md:295-316]()

### Hot Path (Conscious) Formation

Hot path processing occurs during active conversations using memory tools. Agents make real-time decisions about memory operations through `create_manage_memory_tool` and `create_search_memory_tool`.

This approach provides immediate memory updates but adds perceptible latency to user interactions. The agent must balance memory management with primary task completion.

**Sources:** [docs/docs/concepts/conceptual_guide.md:306-310]()

### Background (Subconscious) Formation

Background processing uses `ReflectionExecutor` and `create_thread_extractor` to analyze conversations after completion. This enables deeper pattern analysis without impacting response time.

The `ReflectionExecutor` orchestrates deferred memory operations, allowing for more thorough analysis and consolidation processes.

**Sources:** [docs/docs/concepts/conceptual_guide.md:312-316](), [src/langmem/__init__.py:14]()

## Integration Architecture

LangMem's architecture consists of two distinct layers that provide different levels of integration complexity.

```mermaid
graph TB
    subgraph "LangMem Architecture Layers"
        subgraph "Core API Layer - Stateless"
            CAL["`**Core API**
            Pure Functions`"]
            MM["`create_memory_manager
            Transform memory state`"]
            PO["`create_prompt_optimizer
            Update prompts`"]
            TE["`create_thread_extractor
            Extract from conversations`"]
        end
        
        subgraph "Stateful Integration Layer"
            SIL["`**Stateful Integration**
            LangGraph Dependent`"]
            MSM["`create_memory_store_manager
            Persistent operations`"]
            MMT["`create_manage_memory_tool
            Agent memory tools`"]
            SMT["`create_search_memory_tool
            Agent search tools`"]
        end
        
        subgraph "External Dependencies"
            LG["`langgraph.store.base.BaseStore
            Storage interface`"]
            LC["`langchain_core
            LLM integrations`"]
        end
    end
    
    CAL --> MM
    CAL --> PO  
    CAL --> TE
    SIL --> MSM
    SIL --> MMT
    SIL --> SMT
    MSM --> MM
    MMT --> LG
    SMT --> LG
    MM --> LC
    PO --> LC
```

**Sources:** [docs/docs/concepts/conceptual_guide.md:318-340](), [src/langmem/__init__.py:1-27]()

### Core API Layer

The Core API provides stateless functions that transform memory state without side effects. These functions operate independently of any storage system:

- `create_memory_manager`: Extracts, updates, and consolidates memories
- `create_prompt_optimizer`: Refines prompts based on feedback
- `create_thread_extractor`: Processes conversation threads

This layer enables memory operations in any application context without requiring specific storage infrastructure.

**Sources:** [docs/docs/concepts/conceptual_guide.md:322-330]()

### Stateful Integration Layer

The Stateful Integration layer depends on LangGraph's `BaseStore` interface for persistence. Components include:

- `create_memory_store_manager`: Automatically persists extracted memories
- `create_manage_memory_tool`: Provides agent tools for memory operations
- `create_search_memory_tool`: Enables agent memory search capabilities

This layer simplifies LangGraph integration by handling storage operations automatically.

**Sources:** [docs/docs/concepts/conceptual_guide.md:331-340]()

## Storage Patterns and Namespace Organization

LangMem organizes memories using namespace hierarchies and flexible retrieval mechanisms built on LangGraph's storage primitives.

```mermaid
graph TB
    subgraph "Storage Organization"
        subgraph "Namespace Structure"
            NS["`**Namespaces**
            Hierarchical organization`"]
            NST["`NamespaceTemplate
            (org, user_id, context)`"]
            NSConfig["`RunnableConfig
            configurable fields`"]
        end
        
        subgraph "Retrieval Methods"
            DA["`BaseStore.get()
            Direct access by key`"]
            SS["`BaseStore.search()
            Semantic similarity`"]
            MF["`BaseStore.search()
            Metadata filtering`"]
        end
        
        subgraph "Storage Implementations"
            IMS["`InMemoryStore
            Development/testing`"]
            PGS["`AsyncPostgresStore
            Production storage`"]
        end
    end
    
    NS --> NST
    NST --> NSConfig
    NS --> DA
    NS --> SS  
    NS --> MF
    DA --> IMS
    DA --> PGS
    SS --> IMS
    SS --> PGS
    MF --> IMS
    MF --> PGS
```

**Sources:** [docs/docs/concepts/conceptual_guide.md:341-377]()

### Memory Namespaces

Namespaces provide hierarchical memory organization using tuple structures like `("acme_corp", "{user_id}", "code_assistant")`. Template variables in namespaces get populated from `RunnableConfig.configurable` fields at runtime.

The `NamespaceTemplate` utility manages dynamic namespace configuration, enabling user isolation and contextual memory organization.

**Sources:** [docs/docs/concepts/conceptual_guide.md:350-367]()

### Flexible Retrieval

LangMem integrates with LangGraph's `BaseStore` interface supporting multiple retrieval patterns:

- **Direct Access**: `BaseStore.get()` retrieves specific memories by key
- **Semantic Search**: `BaseStore.search()` finds memories by similarity
- **Metadata Filtering**: `BaseStore.search()` filters by memory attributes

Storage implementations include `InMemoryStore` for development and `AsyncPostgresStore` for production deployments.

**Sources:** [docs/docs/concepts/conceptual_guide.md:368-377]()

---

# Page: Memory Management

# Memory Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/concepts/conceptual_guide.md](docs/docs/concepts/conceptual_guide.md)
- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)

</details>



This document covers LangMem's core memory management capabilities, focusing on the two primary factory functions `create_memory_manager` and `create_memory_store_manager` and their respective implementations. These functions provide the foundation for extracting, processing, and managing conversation memories in LLM applications.

For information about specific memory types (semantic, episodic, procedural), see [Semantic Memory](#2.1), [Episodic Memory](#2.2), and [User Profiles](#2.4). For short-term memory and conversation summarization, see [Short-Term Memory and Summarization](#2.3). For hot path versus background processing approaches, see [Processing Approaches](#3).

## Core Memory Management Functions

LangMem provides two main factory functions that handle memory management at different levels of integration:

| Function | Purpose | Storage Integration | Use Case |
|----------|---------|-------------------|-----------|
| `create_memory_manager` | Stateless memory processing | None - returns extracted memories | Standalone memory extraction, custom storage |
| `create_memory_store_manager` | Stateful memory processing | LangGraph BaseStore | Automatic persistence, full memory lifecycle |

Both functions return `Runnable` instances that can be invoked with conversation messages to process memories, but they differ significantly in their integration patterns and capabilities.

**Sources:** [src/langmem/knowledge/extraction.py:536-692](), [src/langmem/knowledge/extraction.py:1666-2105]()

## Memory Manager Architecture

The `MemoryManager` class provides the core stateless memory processing functionality. It analyzes conversation messages against existing memories to extract, update, consolidate, or remove memory entries.

```mermaid
graph TB
    subgraph "MemoryManager Core"
        MM["MemoryManager"]
        TE["trustcall extractor"]
        INST["_MEMORY_INSTRUCTIONS"]
    end
    
    subgraph "Input Processing"
        MS["MemoryState"]
        PM["_prepare_messages()"]
        PE["_prepare_existing()"]
    end
    
    subgraph "Processing Loop"
        ML["max_steps loop"]
        TC["tool calling"]
        DONE["Done tool"]
    end
    
    subgraph "Output"
        EM["ExtractedMemory[]"]
        FR["_filter_response()"]
    end
    
    MS --> PM
    MS --> PE
    PM --> MM
    PE --> MM
    MM --> TE
    TE --> ML
    ML --> TC
    TC --> DONE
    ML --> FR
    FR --> EM
    
    INST --> MM
```

The `MemoryManager` supports configurable memory operations through boolean flags:

- `enable_inserts`: Allow creation of new memories
- `enable_updates`: Allow modification of existing memories  
- `enable_deletes`: Allow removal of outdated memories

**Sources:** [src/langmem/knowledge/extraction.py:217-533](), [src/langmem/knowledge/extraction.py:185-207]()

## Memory Store Manager Architecture  

The `MemoryStoreManager` extends memory management with full storage integration, automatic memory search, and lifecycle management. It combines memory processing with LangGraph's `BaseStore` for persistence.

```mermaid
graph TB
    subgraph "MemoryStoreManager"
        MSM["MemoryStoreManager"]
        MM2["MemoryManager"]
        ST["search_tool"]
        QG["query_gen"]
    end
    
    subgraph "Storage Layer"
        BS["BaseStore"]
        NS["namespace()"]
        SM["store_map"]
    end
    
    subgraph "Processing Pipeline"
        QS["query search"]
        ER["enrich memories"]
        PH["phases processing"]
        AU["apply updates"]
    end
    
    subgraph "Memory Lifecycle"
        SR["search & retrieve"]
        EX["extract & update"]  
        CO["consolidate"]
        PS["persist to store"]
    end
    
    MSM --> MM2
    MSM --> ST
    MSM --> QG
    MSM --> BS
    BS --> NS
    BS --> SM
    
    MSM --> QS
    QS --> ER
    ER --> PH
    PH --> AU
    
    SR --> EX
    EX --> CO
    CO --> PS
    
    style MSM fill:#f9f9f9
    style MM2 fill:#e8f5e8
    style BS fill:#fff3e0
```

The `MemoryStoreManager` includes several advanced features:
- **Query Generation**: Uses a separate LLM to generate optimized search queries
- **Default Factory**: Provides fallback memories when no existing memories are found
- **Multi-Phase Processing**: Supports multiple rounds of memory enrichment
- **Namespace Templating**: Dynamic namespace configuration with runtime variables

**Sources:** [src/langmem/knowledge/extraction.py:832-1665](), [src/langmem/knowledge/extraction.py:877-914]()

## Memory Processing Data Flow

The following diagram shows how conversation messages flow through the memory processing pipeline from input to persistent storage:

```mermaid
sequenceDiagram
    participant C as "Client"
    participant MSM as "MemoryStoreManager"  
    participant QM as "query_model"
    participant BS as "BaseStore"
    participant MM as "MemoryManager"
    participant LLM as "Language Model"
    
    C->>MSM: "MemoryStoreManagerInput"
    MSM->>MSM: "namespace(config)"
    
    alt query_model configured
        MSM->>QM: "generate search queries"
        QM-->>MSM: "tool_calls[]"
        MSM->>BS: "asearch(namespace, queries)"
    else no query_model
        MSM->>MSM: "get_dilated_windows()"
        MSM->>BS: "asearch(namespace, windows)"
    end
    
    BS-->>MSM: "search_results[]"
    MSM->>MSM: "_sort_results()"
    
    MSM->>MM: "ainvoke(messages, existing)"
    MM->>LLM: "extract & consolidate"
    LLM-->>MM: "tool_calls[]"
    MM-->>MSM: "ExtractedMemory[]"
    
    loop for each phase
        MSM->>MM: "_build_phase_manager()"
        MM->>LLM: "phase processing"
        LLM-->>MM: "phase results"
        MM-->>MSM: "phase memories"
    end
    
    MSM->>MSM: "_apply_manager_output()"
    MSM->>BS: "aput() / adelete()"
    BS-->>MSM: "persistence confirmation"
    MSM-->>C: "final_puts[]"
```

**Sources:** [src/langmem/knowledge/extraction.py:1006-1137](), [src/langmem/knowledge/extraction.py:977-989]()

## Memory State and Schemas

Both memory managers work with structured memory representations using Pydantic models. The base `Memory` class provides a simple content-based memory, while custom schemas enable structured memory types.

| Class | Purpose | Key Fields | Usage |
|-------|---------|------------|--------|
| `Memory` | Default unstructured memory | `content: str` | Basic memory storage |
| `ExtractedMemory` | Processed memory result | `id: str`, `content: BaseModel` | Memory manager output |
| `MemoryState` | Input state container | `messages: list`, `existing: list`, `max_steps: int` | Processing input |
| `MemoryStoreManagerInput` | Store manager input | `messages: list`, `max_steps: int` | Store processing input |

The memory processing supports multi-step extraction with a configurable `max_steps` parameter. When `max_steps > 1`, the system adds a `Done` tool to allow the LLM to signal completion of memory formation.

**Sources:** [src/langmem/knowledge/extraction.py:64-94](), [src/langmem/knowledge/extraction.py:78-81](), [src/langmem/knowledge/extraction.py:209-215]()

## Memory Operations and Filtering

The memory processing pipeline handles three core operations on existing memories:

```mermaid
graph LR
    subgraph "Memory Operations"
        INS["Insert New"]
        UPD["Update Existing"] 
        DEL["Delete Outdated"]
    end
    
    subgraph "Processing Flags"
        EI["enable_inserts"]
        EU["enable_updates"]
        ED["enable_deletes"]
    end
    
    subgraph "Filtering Logic"
        FR["_filter_response()"]
        ER["exclude_removals"]
        EXT["external_ids"]
    end
    
    EI --> INS
    EU --> UPD
    ED --> DEL
    
    INS --> FR
    UPD --> FR
    DEL --> FR
    
    FR --> ER
    FR --> EXT
    
    style FR fill:#f9f9f9
```

The `_filter_response()` method handles complex memory ID tracking to distinguish between externally-provided memories (that can be deleted) and internally-generated memories (that should not appear as deletions in the final output).

**Sources:** [src/langmem/knowledge/extraction.py:509-533](), [src/langmem/knowledge/extraction.py:940-975]()

## Integration with LangGraph Store

The `MemoryStoreManager` provides a complete storage interface through delegation to LangGraph's `BaseStore`. Key storage methods include:

| Method | Purpose | Async Version | Key Features |
|--------|---------|---------------|--------------|
| `get()` | Retrieve single item | `aget()` | TTL refresh, default factory |
| `search()` | Find multiple items | `asearch()` | Query + filter, pagination |
| `put()` | Store/update item | `aput()` | Indexing control, TTL |
| `delete()` | Remove item | `adelete()` | Namespace-aware deletion |

All storage operations use the configured namespace template, supporting dynamic runtime configuration through `RunnableConfig`.

**Sources:** [src/langmem/knowledge/extraction.py:1318-1658](), [src/langmem/knowledge/extraction.py:877-914]()

---

# Page: Semantic Memory

# Semantic Memory

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_semantic_memories.md](docs/docs/guides/extract_semantic_memories.md)
- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)

</details>



This document covers LangMem's semantic memory extraction and management capabilities. Semantic memory handles the extraction, structuring, and storage of factual information, preferences, relationships, and knowledge from conversations. For episodic memory (capturing interaction experiences), see [Episodic Memory](#2.2). For user profile management, see [User Profiles](#2.4).

## Core Architecture

LangMem's semantic memory system centers around two primary components: `MemoryManager` for stateless extraction and `MemoryStoreManager` for integrated storage management. Both use schema-based extraction to convert conversational content into structured memory objects.

```mermaid
graph TB
    subgraph "Core Extraction Layer"
        MM["MemoryManager"]
        CM["create_memory_manager()"]
        CM --> MM
    end
    
    subgraph "Storage Integration Layer"
        MSM["MemoryStoreManager"] 
        CMSM["create_memory_store_manager()"]
        CMSM --> MSM
        MSM --> MM
    end
    
    subgraph "Schema System"
        Memory["Memory (default)"]
        Triple["Triple (custom)"]
        UserSchema["User Schemas"]
    end
    
    subgraph "Storage Backends"
        BS["BaseStore"]
        IMS["InMemoryStore"]
        PGS["AsyncPostgresStore"]
        BS --> IMS
        BS --> PGS
    end
    
    MM --> Memory
    MM --> Triple
    MM --> UserSchema
    MSM --> BS
    
    subgraph "Extraction Process"
        TC["trustcall.create_extractor"]
        LLM["Language Model"]
        TC --> LLM
        MM --> TC
    end
```

**Sources:** [src/langmem/knowledge/extraction.py:217-692](), [src/langmem/knowledge/extraction.py:832-2105]()

## Memory Extraction Process

The memory extraction process uses `trustcall.create_extractor` to enable structured extraction through parallel tool calling. The system analyzes conversations against existing memories and generates create, update, or delete operations.

```mermaid
sequenceDiagram
    participant Input as "MemoryState"
    participant MM as "MemoryManager"  
    participant Extractor as "create_extractor"
    participant LLM as "Language Model"
    participant Output as "ExtractedMemory[]"
    
    Input->>MM: "messages + existing memories"
    MM->>MM: "_prepare_messages()"
    MM->>MM: "_prepare_existing()"
    MM->>Extractor: "tools=[schemas], enable_inserts/updates/deletes"
    
    loop "max_steps iterations"
        MM->>Extractor: "payload with prepared data"
        Extractor->>LLM: "parallel tool calling"
        LLM-->>Extractor: "tool responses + metadata"
        Extractor-->>MM: "responses with json_doc_id"
        MM->>MM: "update results dict"
        
        alt "step > 1"
            MM->>Extractor: "add Done tool"
        end
        
        alt "is_done or no tool_calls"
            break
        end
        
        MM->>MM: "prepare next iteration payload"
    end
    
    MM->>MM: "_filter_response()"
    MM-->>Output: "filtered ExtractedMemory list"
```

**Sources:** [src/langmem/knowledge/extraction.py:237-339](), [src/langmem/knowledge/extraction.py:457-478]()

## Schema-Based Extraction

Semantic memory uses Pydantic schemas to define the structure of extracted information. The default `Memory` schema provides unstructured text storage, while custom schemas enable structured extraction.

### Default Memory Schema

The basic `Memory` schema stores unstructured content:

[src/langmem/knowledge/extraction.py:86-93]()

### Custom Schemas

Custom schemas like `Triple` enable structured fact extraction:

```mermaid
graph LR
    subgraph "Schema Definition"
        TS["Triple Schema"]
        Subject["subject: str"]  
        Predicate["predicate: str"]
        Object["object: str"]
        Context["context: str | None"]
        
        TS --> Subject
        TS --> Predicate  
        TS --> Object
        TS --> Context
    end
    
    subgraph "Extraction Process"
        Conv["Conversation"]
        Extractor["create_extractor"]
        Tools["tools=[Triple]"]
        
        Conv --> Extractor
        Tools --> Extractor
    end
    
    subgraph "Output"
        EM1["ExtractedMemory(Triple)"]
        EM2["ExtractedMemory(Triple)"]
        EM3["ExtractedMemory(Triple)"]
    end
    
    Extractor --> EM1
    Extractor --> EM2  
    Extractor --> EM3
```

**Sources:** [docs/docs/guides/extract_semantic_memories.md:17-31](), [src/langmem/knowledge/extraction.py:222-235]()

## Collection vs Profile Patterns

Semantic memory supports two primary storage patterns:

| Pattern | Description | Use Case | Storage |
|---------|-------------|----------|---------|
| Collection | Multiple related memories with unique IDs | Facts, preferences, relationships | Multiple documents |
| Profile | Single consolidated memory document | User profiles, system state | Single document with updates |

### Collection Pattern

The collection pattern stores multiple discrete memory objects, each with unique identifiers. This pattern supports the full range of operations: create, update, and delete.

**Memory Manager Configuration:**
- `enable_inserts=True` - Allow new memory creation
- `enable_updates=True` - Allow memory modifications  
- `enable_deletes=True` - Allow memory removal

**Sources:** [src/langmem/knowledge/extraction.py:543-544](), [docs/docs/guides/extract_semantic_memories.md:28-31]()

### Profile Pattern 

The profile pattern maintains a single memory document that gets updated in-place. This pattern typically disables inserts and deletes to maintain a consolidated view.

**Memory Store Manager Configuration:**
- `enable_inserts=False` - Prevent new memory creation
- Default value initialization for empty profiles

**Sources:** [src/langmem/knowledge/extraction.py:1674-1675](), [src/langmem/knowledge/extraction.py:1696-1700]()

## Memory Enrichment Operations

The memory enrichment process supports three core operations managed through the `MemoryManager` class:

### Insert Operations

New memories are created when `enable_inserts=True` and novel information is detected. Each memory receives a unique UUID identifier.

**Sources:** [src/langmem/knowledge/extraction.py:224](), [src/langmem/knowledge/extraction.py:284-287]()

### Update Operations  

Existing memories are modified when `enable_updates=True` and contradictory or supplementary information is found. Updates preserve the original memory ID.

**Sources:** [src/langmem/knowledge/extraction.py:225](), [src/langmem/knowledge/extraction.py:301-308]()

### Delete Operations

Memories are marked for deletion when `enable_deletes=True` and information becomes outdated or contradicted. The system returns `RemoveDoc` objects for external handling.

**Sources:** [src/langmem/knowledge/extraction.py:226](), [src/langmem/knowledge/extraction.py:304-306]()

## Storage Integration

The `MemoryStoreManager` integrates semantic memory with LangGraph's `BaseStore` system, providing automatic search, persistence, and namespace organization.

```mermaid
graph TB
    subgraph "MemoryStoreManager Integration"
        MSM["MemoryStoreManager"]
        QueryGen["query_gen (optional)"]
        SearchTool["create_search_memory_tool"]
        MM["memory_manager"]
        
        MSM --> QueryGen
        MSM --> SearchTool  
        MSM --> MM
    end
    
    subgraph "Storage Operations"
        Search["asearch() / search()"]
        Put["aput() / put()"] 
        Delete["adelete() / delete()"]
        
        MSM --> Search
        MSM --> Put
        MSM --> Delete
    end
    
    subgraph "BaseStore Backends"
        Store["BaseStore"]
        Memory["InMemoryStore"]
        Postgres["AsyncPostgresStore"]
        
        Store --> Memory
        Store --> Postgres
    end
    
    subgraph "Memory Lifecycle" 
        Retrieve["Retrieve relevant memories"]
        Extract["Extract new memories"]
        Apply["Apply updates to store"]
        
        Search --> Retrieve
        MM --> Extract  
        Put --> Apply
        Delete --> Apply
    end
    
    Store --> Search
    Store --> Put
    Store --> Delete
```

### Query Generation

Optional query model support enables optimized memory retrieval through the `query_model` parameter. When configured, the system uses a separate model to generate search queries before extracting memories.

**Sources:** [src/langmem/knowledge/extraction.py:846](), [src/langmem/knowledge/extraction.py:1015-1029]()

### Namespace Organization  

Memory organization uses tuple-based namespaces with template variable support:

```python
# Template namespace
("memories", "{langgraph_user_id}")

# Resolved at runtime
("memories", "user-123")
```

**Sources:** [src/langmem/knowledge/extraction.py:848](), [src/langmem/knowledge/extraction.py:877]()

### Memory Phases

The system supports multi-phase processing through the `phases` parameter, enabling complex memory consolidation workflows:

**Sources:** [src/langmem/knowledge/extraction.py:850](), [src/langmem/knowledge/extraction.py:1087-1100]()

---

# Page: Episodic Memory

# Episodic Memory

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_episodic_memories.md](docs/docs/guides/extract_episodic_memories.md)
- [docs/docs/guides/memory_tools.md](docs/docs/guides/memory_tools.md)
- [docs/docs/guides/use_tools_in_crewai.md](docs/docs/guides/use_tools_in_crewai.md)
- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)

</details>



Episodic memory in LangMem captures complete interaction experiences rather than isolated facts. While semantic memory (see [Semantic Memory](#2.1)) stores what the agent knows, episodic memory preserves how the agent successfully reasoned through problems. This enables experience replay and adaptive learning from past successful interactions.

## What is Episodic Memory

Episodic memory stores structured records of successful problem-solving experiences, including the complete reasoning chain that led to positive outcomes. Each episode contains the context, internal thought process, actions taken, and retrospective analysis.

**Key Differences from Semantic Memory:**

| Memory Type | Content | Purpose | Schema Pattern |
|-------------|---------|---------|----------------|
| Semantic | Facts, preferences, relationships | Knowledge base | Triple, UserProfile |
| Episodic | Complete interaction experiences | Learning from success | Episode with reasoning chain |

Sources: [docs/docs/guides/extract_episodic_memories.md:1-196](), [src/langmem/knowledge/extraction.py:185-206]()

## Episode Schema Structure

The standard episodic memory schema captures four essential components of successful interactions:

```python
class Episode(BaseModel):
    observation: str  # Context and setup - what happened
    thoughts: str     # Internal reasoning process - "I..."  
    action: str       # What was done and how - "I..."
    result: str       # Outcome and retrospective - "I..."
```

This schema is designed to preserve the complete decision-making process, enabling the agent to learn not just what worked, but why it worked and how to replicate the success.

**Episode Schema Architecture:**

```mermaid
graph TB
    subgraph "Episode Components"
        OBS["observation<br/>\"Context & Setup\""]
        THO["thoughts<br/>\"Internal Reasoning\""]
        ACT["action<br/>\"What Was Done\""]
        RES["result<br/>\"Outcome & Analysis\""]
    end
    
    subgraph "Memory Processing"
        MM["MemoryManager"]
        EXT["ExtractedMemory"]
        STORE["BaseStore"]
    end
    
    subgraph "Usage Flow"
        CONV["Conversation Messages"]
        SCHEMA["Episode Schema"]
        EXTRACT["Extract Episodes"]
        PERSIST["Store & Index"]
        RECALL["Similarity Search"]
        APPLY["Apply to New Situations"]
    end
    
    OBS --> MM
    THO --> MM  
    ACT --> MM
    RES --> MM
    
    MM --> EXT
    EXT --> STORE
    
    CONV --> EXTRACT
    SCHEMA --> EXTRACT
    EXTRACT --> PERSIST
    PERSIST --> RECALL
    RECALL --> APPLY
```

Sources: [docs/docs/guides/extract_episodic_memories.md:19-47](), [src/langmem/knowledge/extraction.py:86-93]()

## Episodic Extraction Process

Episodic memory extraction uses the same `MemoryManager` infrastructure as semantic memory but with Episode-specific schemas and instructions focused on capturing successful reasoning patterns.

**Memory Manager Configuration:**

```python
manager = create_memory_manager(
    model="anthropic:claude-3-5-sonnet-latest",
    schemas=[Episode],
    instructions="Extract examples of successful explanations, capturing the full chain of reasoning.",
    enable_inserts=True
)
```

The extraction process analyzes conversation messages to identify successful interactions and structures them into Episode records containing the complete reasoning chain.

**Episodic Memory Extraction Flow:**

```mermaid
sequenceDiagram
    participant CONV as "Conversation"
    participant MM as "MemoryManager"
    participant EXT as "create_extractor"
    participant LLM as "Language Model" 
    participant EP as "Episode Schema"
    participant EM as "ExtractedMemory"
    
    CONV->>MM: "invoke(messages)"
    MM->>MM: "_prepare_messages()"
    MM->>EXT: "create_extractor(schemas=[Episode])"
    MM->>LLM: "Analyze for successful patterns"
    LLM->>EP: "Structure reasoning chain"
    EP->>EM: "ExtractedMemory(id, Episode)"
    EM->>MM: "List[ExtractedMemory]"
    MM->>CONV: "Return episodes"
```

Sources: [src/langmem/knowledge/extraction.py:217-294](), [src/langmem/knowledge/extraction.py:536-692]()

## Storage and Retrieval Patterns

Episodic memories use the collection storage pattern, where each episode is stored as a separate document that can be searched and retrieved based on similarity to current situations.

**Storage Architecture:**

```mermaid
graph TB
    subgraph "Storage Layer"
        MSM["MemoryStoreManager"]
        NS["namespace=(\"memories\", \"episodes\")"]
        BS["BaseStore"]
        VS["Vector Search"]
    end
    
    subgraph "Episode Lifecycle"
        EXT["Extract Episode"]
        INDEX["Index for Search"]
        SIMILAR["Find Similar Episodes"]
        APPLY["Apply Past Learning"]
    end
    
    subgraph "Code Entities"
        CMS["create_memory_store_manager"]
        CM["create_memory_manager"] 
        ST["search_tool"]
        EMC["ExtractedMemory"]
    end
    
    EXT --> MSM
    MSM --> NS
    NS --> BS
    BS --> VS
    
    SIMILAR --> ST
    ST --> VS
    
    CMS --> MSM
    CM --> EMC
    EMC --> INDEX
```

**Key Storage Operations:**

| Operation | Method | Purpose |
|-----------|--------|---------|
| Store Episode | `MemoryStoreManager.ainvoke()` | Persist new episodes |
| Search Similar | `BaseStore.asearch()` | Find relevant past experiences |
| Update Episode | `enable_updates=True` | Refine existing episodes |
| Namespace Episodes | `("memories", "episodes")` | Organize by memory type |

Sources: [docs/docs/guides/extract_episodic_memories.md:82-172](), [src/langmem/knowledge/extraction.py:832-1137]()

## Integration with Memory Manager

Episodic memory integrates with LangMem's core memory management infrastructure through the `MemoryManager` class and storage systems.

**Core Integration Points:**

- **Schema Definition**: Episode schemas define the structure of episodic memories
- **Memory Manager**: `create_memory_manager()` processes conversations into episodes  
- **Storage Manager**: `create_memory_store_manager()` handles persistence and retrieval
- **Vector Search**: `BaseStore.asearch()` enables similarity-based episode retrieval
- **Extraction Pipeline**: `create_extractor()` with Episode tools structures the reasoning chains

**Memory Manager Integration:**

```mermaid
graph LR
    subgraph "Input Processing"
        MSGS["messages: list[AnyMessage]"]
        EXIST["existing: list[ExtractedMemory]"]
        STEPS["max_steps: int"]
    end
    
    subgraph "MemoryManager Core"
        MM["MemoryManager"]
        PREP["_prepare_messages()"]
        PEXIST["_prepare_existing()"] 
        FILT["_filter_response()"]
    end
    
    subgraph "Extraction Engine"
        CE["create_extractor"]
        TOOLS["tools=[Episode]"]
        RESP["responses"]
        META["response_metadata"]
    end
    
    subgraph "Output"
        EXMEM["ExtractedMemory"]
        EPIS["Episode content"]
    end
    
    MSGS --> PREP
    EXIST --> PEXIST
    STEPS --> MM
    
    MM --> CE
    TOOLS --> CE
    CE --> RESP
    RESP --> META
    META --> FILT
    FILT --> EXMEM
    EXMEM --> EPIS
```

Sources: [src/langmem/knowledge/extraction.py:217-446](), [src/langmem/knowledge/extraction.py:457-508]()

## Usage Patterns

Episodic memory supports both standalone extraction and integrated storage workflows:

**Standalone Extraction**: Use `create_memory_manager()` to extract episodes without persistence
**Integrated Storage**: Use `create_memory_store_manager()` for persistent episodes with search capabilities
**Experience Replay**: Search similar episodes before processing new interactions
**Adaptive Learning**: Update system prompts based on retrieved episode insights

The episodic memory system enables agents to build expertise through experience rather than just accumulating facts, creating a foundation for continuous learning and improvement.

Sources: [docs/docs/guides/extract_episodic_memories.md:9-82](), [docs/docs/guides/extract_episodic_memories.md:185-196]()

---

# Page: Short-Term Memory and Summarization

# Short-Term Memory and Summarization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [docs/docs/guides/summarization.md](docs/docs/guides/summarization.md)
- [src/langmem/short_term/summarization.py](src/langmem/short_term/summarization.py)
- [tests/cassettes/ed2e87ca-f890-4900-9a09-dfbc12b51964.yaml](tests/cassettes/ed2e87ca-f890-4900-9a09-dfbc12b51964.yaml)
- [tests/short_term/__init__.py](tests/short_term/__init__.py)
- [tests/short_term/test_summarization.py](tests/short_term/test_summarization.py)

</details>



This document covers LangMem's short-term memory and message summarization capabilities, focusing on managing conversation context within token limits through intelligent summarization. For long-term memory storage and retrieval, see [Memory Management](#2). For background processing of conversations, see [Background Memory Processing](#3.2).

## Purpose and Scope

Short-term memory in LangMem addresses the fundamental challenge of context window limitations in LLM applications. As conversations grow longer or agents make numerous tool calls, the message history can exceed model token limits. LangMem's summarization system provides automated, incremental summarization that preserves important context while keeping conversations within token budgets.

The system operates on conversation messages, creating summaries when token thresholds are exceeded and maintaining a running summary across multiple conversation turns. This differs from long-term semantic memory extraction, which focuses on persistent knowledge storage.

## Core Components

```mermaid
graph TB
    subgraph "Core Functions"
        SM["summarize_messages()"]
        ASM["asummarize_messages()"]
    end
    
    subgraph "LangGraph Integration"
        SN["SummarizationNode"]
    end
    
    subgraph "Data Structures"
        RS["RunningSummary"]
        SR["SummarizationResult"]
        PM["PreprocessedMessages"]
    end
    
    subgraph "Configuration"
        IDP["DEFAULT_INITIAL_SUMMARY_PROMPT"]
        ESP["DEFAULT_EXISTING_SUMMARY_PROMPT"]
        FSP["DEFAULT_FINAL_SUMMARY_PROMPT"]
        TC["TokenCounter"]
    end
    
    SM --> SR
    ASM --> SR
    SN --> SM
    SN --> ASM
    
    SM --> RS
    ASM --> RS
    
    SM --> IDP
    SM --> ESP  
    SM --> FSP
    SM --> TC
    
    SR --> RS
    SM --> PM
    ASM --> PM
```

**Sources:** [src/langmem/short_term/summarization.py:1-658]()

The summarization system centers around the `summarize_messages` function, which processes message lists and returns `SummarizationResult` objects containing both the summarized messages and updated `RunningSummary` state.

| Component | Purpose | Key Fields/Methods |
|-----------|---------|-------------------|
| `summarize_messages` | Main synchronous summarization function | `messages`, `running_summary`, `model`, `max_tokens` |
| `asummarize_messages` | Asynchronous version of summarization | Same parameters as synchronous version |
| `RunningSummary` | Tracks summarization state across calls | `summary`, `summarized_message_ids`, `last_summarized_message_id` |
| `SummarizationResult` | Output containing processed messages | `messages`, `running_summary` |
| `SummarizationNode` | LangGraph node wrapper for summarization | `model`, `max_tokens`, `input_messages_key`, `output_messages_key` |

**Sources:** [src/langmem/short_term/summarization.py:52-80](), [src/langmem/short_term/summarization.py:337-496](), [src/langmem/short_term/summarization.py:660-857]()

## Message Processing Flow

```mermaid
sequenceDiagram
    participant App as "Application"
    participant SM as "summarize_messages"
    participant PP as "_preprocess_messages"
    participant LLM as "Language Model"
    participant PR as "_prepare_summarization_result"
    
    App->>SM: "messages, running_summary, model, max_tokens"
    SM->>PP: "Analyze token counts and determine cutoff"
    PP-->>SM: "PreprocessedMessages"
    
    alt "Summarization needed"
        SM->>SM: "_prepare_input_to_summarization_model"
        SM->>LLM: "Summary prompt + messages to summarize"
        LLM-->>SM: "Generated summary"
        SM->>SM: "Create new RunningSummary"
    else "No summarization needed"
        SM->>SM: "Return original messages"
    end
    
    SM->>PR: "Build final result"
    PR-->>SM: "SummarizationResult"
    SM-->>App: "messages + running_summary"
```

**Sources:** [src/langmem/short_term/summarization.py:337-496](), [src/langmem/short_term/summarization.py:102-222](), [src/langmem/short_term/summarization.py:289-335]()

The summarization process involves several key steps:

1. **Message Preprocessing** - `_preprocess_messages` analyzes the message list to determine if summarization is needed based on token counts and identifies which messages should be summarized.

2. **Token Budget Management** - The system calculates remaining token budgets, accounting for system messages, existing summaries, and the target summary length.

3. **Cutoff Point Detection** - Messages are processed sequentially until the `max_tokens_before_summary` threshold is reached, with special handling for AI messages with tool calls.

4. **Summary Generation** - When needed, messages are sent to the LLM with appropriate prompts to generate or update summaries.

5. **Result Assembly** - Final messages are constructed with summaries integrated and `RunningSummary` state updated.

## RunningSummary for Incremental Processing

```mermaid
graph LR
    subgraph "First Call"
        M1["Messages 1-6"] --> RS1["RunningSummary{summary: 'First summary', summarized_message_ids: [1,2,3,4,5,6], last_summarized_message_id: '6'}"]
    end
    
    subgraph "Second Call" 
        M2["Messages 1-10"] --> PP["_preprocess_messages"]
        RS1 --> PP
        PP --> M2S["Messages 7-8 to summarize"]
        M2S --> RS2["RunningSummary{summary: 'Updated summary', summarized_message_ids: [1,2,3,4,5,6,7,8], last_summarized_message_id: '8'}"]
    end
    
    subgraph "Result"
        RS2 --> FR["Final Result: [Summary Message] + Messages 9-10"]
    end
```

**Sources:** [src/langmem/short_term/summarization.py:52-67](), [src/langmem/short_term/summarization.py:144-156]()

The `RunningSummary` class enables incremental summarization by tracking:

- **`summary`** - The current text summary of all previously summarized messages
- **`summarized_message_ids`** - Set of message IDs that have already been processed  
- **`last_summarized_message_id`** - ID of the most recent message included in the summary

This state prevents re-summarizing the same messages on subsequent calls. When `summarize_messages` is called with a `RunningSummary`, it:

1. Identifies previously summarized messages using the stored message IDs
2. Only processes new messages that haven't been summarized yet
3. Updates the existing summary by incorporating new content
4. Maintains the tracking state for future calls

**Sources:** [tests/short_term/test_summarization.py:330-431](), [tests/short_term/test_summarization.py:433-533]()

## SummarizationNode Integration

```mermaid
graph TB
    subgraph "LangGraph State"
        MS["messages: list[AnyMessage]"]
        CTX["context: dict[str, Any]"]
        SM["summarized_messages: list[AnyMessage]"]
    end
    
    subgraph "SummarizationNode"
        PI["_parse_input()"]
        SF["_func() / _afunc()"]
        PSU["_prepare_state_update()"]
    end
    
    subgraph "Node Configuration"
        IMK["input_messages_key: 'messages'"]
        OMK["output_messages_key: 'summarized_messages'"]
        MOD["model: LanguageModelLike"]
        MT["max_tokens: int"]
    end
    
    MS --> PI
    CTX --> PI
    PI --> SF
    SF --> PSU
    PSU --> SM
    PSU --> CTX
    
    IMK --> PI
    OMK --> PSU
    MOD --> SF
    MT --> SF
```

**Sources:** [src/langmem/short_term/summarization.py:660-857](), [src/langmem/short_term/summarization.py:795-828]()

`SummarizationNode` provides a LangGraph-compatible wrapper around the core summarization functionality. Key features include:

- **State Integration** - Reads messages from configurable state keys and writes results to separate keys
- **Context Management** - Stores `RunningSummary` in the `context` field of graph state
- **Flexible I/O** - Supports different input/output message keys to isolate summarization from main message flow
- **Remove Messages Support** - When input and output keys are the same, automatically removes old messages using `RemoveMessage`

The node supports both synchronous and asynchronous execution through `_func` and `_afunc` methods that delegate to the appropriate summarization function.

**Sources:** [tests/short_term/test_summarization.py:734-792](), [tests/short_term/test_summarization.py:794-890]()

## Token Management Strategy

```mermaid
graph TB
    subgraph "Token Budget Allocation"
        MT["max_tokens"]
        MST["max_summary_tokens"]
        MRT["max_remaining_tokens = max_tokens - max_summary_tokens"]
    end
    
    subgraph "Message Processing"
        TC["TokenCounter function"]
        SM_MSG["System Message tokens"]
        HIST["Message History tokens"]
        SUM["Existing Summary tokens"]
    end
    
    subgraph "Decision Logic"
        MTBS["max_tokens_before_summary"]
        CUTOFF["Cutoff Point Calculation"]
        TRIM["trim_messages if needed"]
    end
    
    MT --> MST
    MT --> MRT
    TC --> SM_MSG
    TC --> HIST
    TC --> SUM
    
    MTBS --> CUTOFF
    CUTOFF --> TRIM
    
    MST --> MRT
    SM_MSG --> MRT
    SUM --> MRT
```

**Sources:** [src/langmem/short_term/summarization.py:112-121](), [src/langmem/short_term/summarization.py:225-256]()

The system uses a sophisticated token management approach:

1. **Budget Allocation** - `max_tokens` is split between summary space (`max_summary_tokens`) and remaining message space
2. **System Message Handling** - System messages are excluded from summarization but counted against the token budget
3. **Existing Summary Accounting** - When a `RunningSummary` exists, its token cost is deducted from the available budget
4. **Cutoff Determination** - Messages are processed until `max_tokens_before_summary` is reached and remaining messages fit in `max_remaining_tokens`
5. **Overflow Protection** - If messages to summarize exceed `max_tokens`, `trim_messages` reduces them to fit the summarization model's context window

| Parameter | Purpose | Default Behavior |
|-----------|---------|------------------|
| `max_tokens` | Total token budget for final output | Required parameter |
| `max_tokens_before_summary` | Threshold to trigger summarization | Defaults to `max_tokens` |
| `max_summary_tokens` | Reserved space for summary | 256 tokens |
| `token_counter` | Function to count message tokens | `count_tokens_approximately` |

**Sources:** [src/langmem/short_term/summarization.py:342-348](), [src/langmem/short_term/summarization.py:14]()

## Tool Call Handling

The summarization system includes special logic for handling AI messages with tool calls to maintain conversation coherence:

```mermaid
graph LR
    subgraph "Message Sequence"
        AI["AIMessage with tool_calls"] --> TM1["ToolMessage call_id=1"]
        AI --> TM2["ToolMessage call_id=2"] 
        TM1 --> NEXT["Next Messages..."]
        TM2 --> NEXT
    end
    
    subgraph "Summarization Logic"
        CHECK["Check if last message has tool_calls"]
        MATCH["Find matching ToolMessages"]
        INCLUDE["Include in summary"]
    end
    
    AI --> CHECK
    CHECK --> MATCH
    MATCH --> INCLUDE
    TM1 --> INCLUDE
    TM2 --> INCLUDE
```

**Sources:** [src/langmem/short_term/summarization.py:204-214](), [tests/short_term/test_summarization.py:536-575]()

When the last message to be summarized is an AI message with tool calls, the system automatically includes the corresponding tool messages in the summary. This prevents incomplete tool call sequences that would cause issues with LLM providers expecting tool calls to be followed by their results.

## Configuration and Customization

The summarization system provides several customization points through prompt templates and configuration parameters:

| Prompt Template | Usage | Default Behavior |
|----------------|--------|------------------|
| `DEFAULT_INITIAL_SUMMARY_PROMPT` | First-time summarization | Simple "create a summary" instruction |
| `DEFAULT_EXISTING_SUMMARY_PROMPT` | Updating existing summaries | "Extend this summary" with previous context |
| `DEFAULT_FINAL_SUMMARY_PROMPT` | Final message assembly | Integrates summary with remaining messages |

**Sources:** [src/langmem/short_term/summarization.py:23-49]()

Advanced configuration options include:

- **Custom Token Counters** - Replace approximate counting with model-specific implementations using `model.get_num_tokens_from_messages`
- **Model Binding** - Use `model.bind(max_tokens=N)` to enforce summary length limits at the LLM level
- **Prompt Customization** - Override default prompts for domain-specific summarization styles
- **Async Support** - Use `asummarize_messages` for non-blocking operation in async applications

**Sources:** [docs/docs/guides/summarization.md:22-23](), [docs/docs/guides/summarization.md:37-38]()

---

# Page: User Profiles

# User Profiles

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/manage_user_profile.md](docs/docs/guides/manage_user_profile.md)
- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)

</details>



User profiles maintain a single, structured representation of a user (or agent) that gets updated in-place as new information becomes available. Unlike semantic memory collections that accumulate multiple facts over time, profiles use the "profile pattern" to maintain current state information in a single document.

For information about managing multiple evolving facts and knowledge, see [Semantic Memory](#2.1). For managing successful interaction patterns, see [Episodic Memory](#2.2).

## Profile Pattern vs Collection Pattern

User profiles implement a specific storage pattern that differs fundamentally from standard memory collection approaches:

| Aspect | Profile Pattern | Collection Pattern |
|--------|----------------|-------------------|
| Storage | Single document per namespace | Multiple documents per namespace |
| Updates | In-place modification | Accumulative insertion |
| `enable_inserts` | `False` | `True` |
| Use Cases | User preferences, current state | Facts, experiences, knowledge |

```mermaid
graph TB
    subgraph "Memory Storage Patterns"
        subgraph CP["Collection Pattern"]
            CP1["enable_inserts=True"]
            CP2["Multiple Documents"]
            CP3["Semantic Facts"]
            CP4["Episodic Experiences"]
        end
        
        subgraph PP["Profile Pattern"]
            PP1["enable_inserts=False"]
            PP2["Single Document"]
            PP3["User State"]
            PP4["Agent State"]
        end
    end
    
    subgraph "Implementation Classes"
        MM["MemoryManager"]
        MSM["MemoryStoreManager"]
    end
    
    CP1 --> MM
    PP1 --> MM
    MM --> MSM
    
    subgraph "Storage Layer"
        BS["BaseStore"]
        NS["NamespaceTemplate"]
    end
    
    MSM --> BS
    MSM --> NS
```

**Implementation Classes for Profile Pattern**
- Profile Pattern uses `enable_inserts=False`
- Collection Pattern uses `enable_inserts=True`
- Both patterns use `MemoryManager` and `MemoryStoreManager`
- Storage organized via `NamespaceTemplate`

Sources: [src/langmem/knowledge/extraction.py:224](), [src/langmem/knowledge/extraction.py:844](), [docs/docs/guides/manage_user_profile.md:36]()

## Core Components

### MemoryManager with Profile Configuration

The `MemoryManager` class handles profile extraction with specific parameters for in-place updates:

```mermaid
graph LR
    subgraph "MemoryManager Configuration"
        MM["MemoryManager"]
        EI["enable_inserts: bool = False"]
        EU["enable_updates: bool = True"]
        ED["enable_deletes: bool = False"]
        SC["schemas: Sequence[BaseModel]"]
    end
    
    subgraph "Profile Behavior"
        IP["In-Place Updates"]
        SD["Single Document"]
        CS["Current State Only"]
    end
    
    MM --> EI
    MM --> EU
    MM --> ED
    MM --> SC
    
    EI --> IP
    EU --> IP
    ED --> SD
    SC --> CS
```

**Profile-Specific Parameters**
- `enable_inserts=False` prevents creating multiple profile instances
- `enable_updates=True` allows modifying existing profile data
- `enable_deletes=False` prevents accidental profile removal
- `schemas` defines profile structure using Pydantic models

Sources: [src/langmem/knowledge/extraction.py:218-235](), [src/langmem/knowledge/extraction.py:542-544]()

### MemoryStoreManager for Persistent Profiles

The `MemoryStoreManager` extends profile management with persistent storage and namespace organization:

```mermaid
graph TB
    subgraph "MemoryStoreManager Profile Features"
        MSM["MemoryStoreManager"]
        DF["default_factory: Callable"]
        DEF["default: str | dict | BaseModel"]
        NS["namespace: tuple[str, ...]"]
        ST["store: BaseStore"]
    end
    
    subgraph "Profile Initialization"
        DI["Default Instance Creation"]
        UN["User Namespace Isolation"]
        PS["Persistent Storage"]
    end
    
    MSM --> DF
    MSM --> DEF
    MSM --> NS
    MSM --> ST
    
    DF --> DI
    DEF --> DI
    NS --> UN
    ST --> PS
    
    subgraph "Namespace Examples"
        U1["('users', 'user-123', 'profile')"]
        U2["('agents', 'assistant-1', 'profile')"]
        U3["('teams', 'sales', 'profile')"]
    end
    
    UN --> U1
    UN --> U2
    UN --> U3
```

**Profile Storage Features**
- `default` or `default_factory` creates initial profile instances
- `namespace` isolates profiles by user, agent, or team
- `store` provides persistent storage via `BaseStore`
- Profile namespaces typically end with `"profile"` for organization

Sources: [src/langmem/knowledge/extraction.py:832-851](), [src/langmem/knowledge/extraction.py:1666-1681]()

## Namespace Organization

User profiles use specific namespace patterns for isolation and organization:

| Namespace Pattern | Purpose | Example |
|------------------|---------|---------|
| `("users", "{user_id}", "profile")` | Individual user profiles | `("users", "alice-123", "profile")` |
| `("agents", "{agent_id}", "profile")` | Agent self-profiles | `("agents", "assistant-v1", "profile")` |
| `("teams", "{team_id}", "profile")` | Team/group profiles | `("teams", "engineering", "profile")` |
| `("sessions", "{session_id}", "profile")` | Session-specific profiles | `("sessions", "chat-abc", "profile")` |

The `NamespaceTemplate` class handles runtime substitution of template variables like `{user_id}` from the LangGraph configuration.

Sources: [src/langmem/knowledge/extraction.py:877](), [docs/docs/guides/manage_user_profile.md:89](), [docs/docs/guides/manage_user_profile.md:138-148]()

## Profile Schema Definition

Profiles are typically defined using Pydantic models that specify the structure and validation rules:

```mermaid
graph TB
    subgraph "Profile Schema Components"
        BM["BaseModel"]
        UP["UserProfile"]
        AP["AgentProfile"]
        TP["TeamProfile"]
    end
    
    subgraph "Common Profile Fields"
        PF1["name: Optional[str]"]
        PF2["preferences: dict"]
        PF3["context: str"]
        PF4["updated_at: datetime"]
    end
    
    subgraph "Validation & Serialization"
        V1["Pydantic Validation"]
        V2["JSON Schema Export"]
        V3["Type Safety"]
    end
    
    BM --> UP
    BM --> AP
    BM --> TP
    
    UP --> PF1
    UP --> PF2
    AP --> PF3
    TP --> PF4
    
    UP --> V1
    AP --> V2
    TP --> V3
```

**Profile Model Features**
- Inherit from Pydantic `BaseModel` for validation
- Use `Optional` fields for incomplete information
- Support nested structures for complex preferences
- Automatic JSON serialization for storage

Sources: [docs/docs/guides/manage_user_profile.md:24-29](), [src/langmem/knowledge/extraction.py:86-93]()

## Factory Functions and Creation

### create_memory_manager for Profiles

```mermaid
graph LR
    subgraph "create_memory_manager"
        CMM["create_memory_manager()"]
        M["model: str | BaseChatModel"]
        S["schemas: Sequence[BaseModel]"]
        EI["enable_inserts=False"]
        EU["enable_updates=True"]
    end
    
    subgraph "Returns"
        MM["MemoryManager"]
        MS["MemoryState Input"]
        EM["list[ExtractedMemory] Output"]
    end
    
    CMM --> M
    CMM --> S
    CMM --> EI
    CMM --> EU
    
    CMM --> MM
    MM --> MS
    MM --> EM
```

**Profile Manager Creation**
- `create_memory_manager()` factory function
- `enable_inserts=False` for profile pattern
- Returns `MemoryManager` instance
- Input: `MemoryState` with messages and existing memories
- Output: `list[ExtractedMemory]` with updated profile

Sources: [src/langmem/knowledge/extraction.py:536-545](), [src/langmem/knowledge/extraction.py:685-692]()

### create_memory_store_manager for Persistent Profiles

```mermaid
graph TB
    subgraph "create_memory_store_manager"
        CMSM["create_memory_store_manager()"]
        MOD["model: str | BaseChatModel"]
        SCH["schemas: list[BaseModel]"]
        DEF["default: str | dict | BaseModel"]
        DF["default_factory: Callable"]
        NS["namespace: tuple[str, ...]"]
        ST["store: BaseStore"]
    end
    
    subgraph "Returns"
        MSM["MemoryStoreManager"]
        MSI["MemoryStoreManagerInput"]
        LD["list[dict] Output"]
    end
    
    subgraph "Storage Operations"
        GNS["get_namespace()"]
        PUT["put() / aput()"]
        GET["get() / aget()"]
        SRC["search() / asearch()"]
    end
    
    CMSM --> MOD
    CMSM --> SCH
    CMSM --> DEF
    CMSM --> DF
    CMSM --> NS
    CMSM --> ST
    
    CMSM --> MSM
    MSM --> MSI
    MSM --> LD
    
    MSM --> GNS
    MSM --> PUT
    MSM --> GET
    MSM --> SRC
```

**Persistent Profile Manager Features**
- `create_memory_store_manager()` factory function
- `default` or `default_factory` for profile initialization
- `namespace` template for user isolation
- Storage operations for profile CRUD
- Returns update operations as `list[dict]`

Sources: [src/langmem/knowledge/extraction.py:1666-1681](), [src/langmem/knowledge/extraction.py:2092-2105]()

## Profile Lifecycle

```mermaid
sequenceDiagram
    participant U as "User/Agent"
    participant MSM as "MemoryStoreManager"
    participant MM as "MemoryManager"
    participant BS as "BaseStore"
    participant NS as "NamespaceTemplate"
    
    Note over U,NS: Profile Initialization
    U->>MSM: First conversation
    MSM->>NS: get_namespace(config)
    NS-->>MSM: ("users", "alice-123", "profile")
    MSM->>BS: search(namespace)
    BS-->>MSM: [] (no existing profile)
    MSM->>MSM: apply default_factory()
    MSM->>BS: put(namespace, "default", profile)
    
    Note over U,NS: Profile Updates
    U->>MSM: Subsequent conversation
    MSM->>BS: search(namespace)
    BS-->>MSM: [existing profile]
    MSM->>MM: ainvoke(messages, existing=[profile])
    MM-->>MSM: [updated profile]
    MSM->>BS: put(namespace, key, updated_profile)
    
    Note over U,NS: Profile Retrieval
    U->>MSM: get("default")
    MSM->>NS: get_namespace(config)
    MSM->>BS: get(namespace, "default")
    BS-->>MSM: profile item
    MSM-->>U: coerced profile
```

**Profile Lifecycle Stages**
1. **Initialization**: Create default profile if none exists
2. **Updates**: In-place modification via `enable_inserts=False`
3. **Retrieval**: Direct access via key or search
4. **Namespace Resolution**: Runtime template substitution

Sources: [src/langmem/knowledge/extraction.py:1006-1137](), [src/langmem/knowledge/extraction.py:1318-1351]()

## Integration Patterns

User profiles integrate with LangGraph applications through several patterns:

| Integration Pattern | Implementation | Use Case |
|-------------------|----------------|----------|
| Direct Manager | `create_memory_manager()` | Standalone profile extraction |
| Store Manager | `create_memory_store_manager()` | Persistent cross-session profiles |
| Agent Tools | `create_manage_memory_tool()` | Agent-driven profile updates |
| Background Processing | `ReflectionExecutor` | Deferred profile enrichment |

For more information on tool-based profile management, see [Memory Creation and Management](#5.1). For background profile processing, see [Background Memory Processing](#3.2).

Sources: [docs/docs/guides/manage_user_profile.md:67-151](), [src/langmem/knowledge/extraction.py:1666-2105]()

---

# Page: Processing Approaches

# Processing Approaches

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/background_quickstart.md](docs/docs/background_quickstart.md)
- [docs/docs/concepts/conceptual_guide.md](docs/docs/concepts/conceptual_guide.md)
- [docs/docs/hot_path_quickstart.md](docs/docs/hot_path_quickstart.md)

</details>



## Purpose and Scope

This document explains the two main approaches for memory processing in LangMem:
1. **Hot Path (Conscious)** - Memory management driven directly by agents using memory tools
2. **Background (Subconscious)** - Automatic memory extraction that happens without agent involvement

These approaches represent fundamentally different architectures for when and how memories are formed, extracted, and managed within LangMem applications. For information about specific memory types (semantic, episodic, etc.), see Key Concepts (1.2).

## Comparison of Processing Approaches

The table below compares the key characteristics of hot path and background memory processing:

| Feature | Hot Path (Agent-Driven) | Background (Automatic) |
|---------|-------------------------|-----------------------|
| When memories are formed | During conversation (immediate) | After conversation or during quiet periods |
| Who initiates memory creation | Agent explicitly via tools | System automatically |
| Latency impact | Higher (adds to response time) | None (happens in background) |
| Agent complexity | Higher (agent must decide when to use memory tools) | Lower (agent doesn't need to manage memory) |
| Implementation components | `create_manage_memory_tool`, `create_search_memory_tool` | `create_memory_store_manager`, optional `ReflectionExecutor` |
| Best suited for | Critical context that must be saved immediately | Pattern analysis, summaries, non-urgent extraction |

The two approaches are complementary and can be used together in the same application.

**Diagram: Processing Approaches Overview**
```mermaid
graph TD
    subgraph "Processing Approaches"
        HotPath["Hot Path (Conscious)"]
        Background["Background (Subconscious)"]
    end
    
    subgraph "Agent Integration"
        ReactAgent["create_react_agent"]
        CrewAgent["CrewAI Integration"]
        CustomAgent["Custom Agent"]
    end
    
    subgraph "Storage Layer"
        InMemStore["InMemoryStore"]
        PostgresStore["AsyncPostgresStore"]
        BaseStore["BaseStore Interface"]
    end
    
    subgraph "Hot Path Components"
        ManageTool["create_manage_memory_tool"]
        SearchTool["create_search_memory_tool"]
    end
    
    subgraph "Background Components"
        StoreManager["create_memory_store_manager"]
        ReflectionExec["ReflectionExecutor"]
    end
    
    ReactAgent -->|"Uses tools"| HotPath
    CrewAgent -->|"Uses tools"| HotPath
    CustomAgent -->|"Uses tools"| HotPath
    
    HotPath --> ManageTool
    HotPath --> SearchTool
    
    Messages["Message History"] --> Background
    Background --> StoreManager
    Background --> ReflectionExec
    
    ManageTool --> BaseStore
    SearchTool --> BaseStore
    StoreManager --> BaseStore
    
    BaseStore --> InMemStore
    BaseStore --> PostgresStore
```

Sources: [docs/docs/hot_path_quickstart.md:9-13](), [docs/docs/background_quickstart.md:8-13](), [docs/docs/hot_path_quickstart.md:74-89]()

## Hot Path Memory (Agent-Driven)

In the hot path approach, the agent actively manages its own memory using tools. This "conscious" memory formation happens during the conversation, enabling immediate updates when critical context emerges.

The agent must decide when to save memories and when to retrieve them, making memory management an explicit part of its decision-making process. This approach gives finer control but adds complexity to the agent implementation and impacts response time.

### Components and Architecture

The hot path approach is implemented using memory management tools:

- `create_manage_memory_tool`: Allows agents to create, update, and delete memories
- `create_search_memory_tool`: Enables agents to search for previously stored memories

These tools are provided to the agent, which can decide when to use them based on its reasoning about the conversation.

**Diagram: Hot Path Memory Flow with Code Entities**
```mermaid
graph TD
    subgraph "Hot Path Memory Flow"
        User["User"] -->|"Message"| ReactAgent["create_react_agent"]
        ReactAgent -->|"Response"| User
        
        ReactAgent -->|"Tool Call"| ManageTool["create_manage_memory_tool"]
        ReactAgent -->|"Tool Call"| SearchTool["create_search_memory_tool"]
        
        ManageTool -->|"store.put()"| InMemStore["InMemoryStore"]
        ManageTool -->|"store.delete()"| InMemStore
        SearchTool -->|"store.search()"| InMemStore
        
        InMemStore -->|"search results"| SearchTool
        SearchTool -->|"Memory context"| ReactAgent
        
        subgraph "Namespace Organization"
            Namespace["('memories', '{user_id}')"]
        end
        
        ManageTool --> Namespace
        SearchTool --> Namespace
    end
```

Sources: [docs/docs/hot_path_quickstart.md:15-89](), [docs/docs/hot_path_quickstart.md:74-89](), [docs/docs/hot_path_quickstart.md:48-63]()

### Implementation Pattern

To implement the hot path approach:

1. Create memory tools with appropriate namespaces
2. Add these tools to your agent framework (LangGraph ReAct, CrewAI, or custom)
3. The agent will call these tools to manage its memory during conversations

### Implementation Pattern

The hot path approach uses the `create_react_agent` pattern from LangGraph with memory tools. The complete implementation is shown in [docs/docs/hot_path_quickstart.md:74-89]() where:

- `create_manage_memory_tool` creates a tool that agents can use to store/update/delete memories
- `create_search_memory_tool` enables memory retrieval during conversations  
- Both tools operate on a `BaseStore` instance (typically `InMemoryStore` or `AsyncPostgresStore`)
- Namespace configuration supports multi-tenancy patterns like `("memories", "{user_id}")`

The agent configuration and prompt function that integrates memory search is demonstrated in [docs/docs/hot_path_quickstart.md:46-63]().

Sources: [docs/docs/hot_path_quickstart.md:74-89](), [docs/docs/hot_path_quickstart.md:91-121]()

## Background Memory Processing

In the background approach, memories are automatically extracted from conversations without the agent's direct involvement. This "subconscious" memory formation happens after the conversation or during quiet periods, allowing deeper pattern analysis without impacting response time.

The agent doesn't need to be aware of the memory extraction process, making implementation simpler but giving less direct control over what information is stored.

### Components and Architecture

The background approach is implemented using:

- `create_memory_store_manager`: Creates a memory manager that automatically extracts and stores memories
- Optional `ReflectionExecutor`: Provides debounced processing to avoid redundant work

**Diagram: Background Memory Flow with Code Entities**
```mermaid
graph TD
    subgraph "Background Memory Flow"
        User["User"] -->|"Message"| ChatFunc["@entrypoint chat()"]
        ChatFunc -->|"Response"| User
        
        ChatFunc -->|"Format messages"| MessageFormat["OpenAI message format"]
        MessageFormat -->|"{'messages': [...]}"| StoreManager["create_memory_store_manager"]
        
        StoreManager -->|"LLM extraction"| LLMModel["anthropic:claude-3-5-sonnet-latest"]
        LLMModel -->|"Memory objects"| StoreManager
        
        StoreManager -->|"store.put()"| InMemStore["InMemoryStore"]
        
        subgraph "Memory Processing"
            MemoryTypes["Semantic, Episodic, User Profile"]
            Namespace["('memories',)"]
        end
        
        StoreManager --> MemoryTypes
        StoreManager --> Namespace
    end
```

Sources: [docs/docs/background_quickstart.md:15-69](), [docs/docs/background_quickstart.md:33-69](), [docs/docs/background_quickstart.md:55-63]()

### Implementation Pattern

The background approach uses `create_memory_store_manager` to automatically extract memories from conversations. The complete implementation is shown in [docs/docs/background_quickstart.md:33-69]() where:

- `create_memory_store_manager` creates a Runnable that processes conversation history
- Messages must be formatted in OpenAI's message format: `{"messages": [{"role": "user", "content": "..."}, ...]}`
- The `@entrypoint` decorator from LangGraph provides store integration
- Memory extraction happens via `ainvoke()` calls on the memory manager

The store configuration and memory search example is demonstrated in [docs/docs/background_quickstart.md:84-105]().

Sources: [docs/docs/background_quickstart.md:33-69]()

### Delayed Processing with ReflectionExecutor

When conversations are active, processing each message immediately for memory extraction can be inefficient. `ReflectionExecutor` allows you to defer memory processing until conversation activity settles, using debouncing to cancel redundant work.

**Diagram: ReflectionExecutor Debouncing Flow**
```mermaid
graph TD
    subgraph "ReflectionExecutor Flow"
        Messages["New Messages"] -->|"submit(to_process, after_seconds=delay)"| ReflectionExec["ReflectionExecutor"]
        
        ReflectionExec -->|"If quiet period elapsed"| MemoryManager["create_memory_store_manager"]
        ReflectionExec -->|"If new messages arrive"| CancelTask["Cancel Pending Task"]
        
        CancelTask -->|"Reschedule with accumulated context"| ReflectionExec
        
        MemoryManager -->|"LLM processing"| LLMExtract["Memory extraction"]
        LLMExtract -->|"store.put()"| InMemStore["InMemoryStore"]
        
        subgraph "Serverless Consideration"
            RemoteExec["Remote ReflectionExecutor"]
            PlatformURL["url='http://localhost:2024'"]
        end
        
        ReflectionExec -.->|"For serverless"| RemoteExec
        RemoteExec --> PlatformURL
    end
```

### Implementation Pattern

The `ReflectionExecutor` wraps `create_memory_store_manager` to provide debounced processing, as shown in [docs/docs/guides/delayed_processing.md:19-53]() where:

- `ReflectionExecutor(memory_manager)` creates a wrapper for delayed processing
- `executor.submit(to_process, after_seconds=delay)` schedules memory processing
- Cancellation and rescheduling happens automatically when new messages arrive
- For serverless deployments, remote execution is configured via URL parameter

The complete delayed processing pattern is demonstrated in [docs/docs/guides/delayed_processing.md:25-53]().

Sources: [docs/docs/guides/delayed_processing.md:8-53]()

## Choosing and Combining Approaches

Both approaches have their strengths and can be used together in the same application:

- **Hot Path (Agent-Driven)** is best for:
  - Critical information that must be saved immediately
  - Selective memory storage where the agent should decide what's important
  - Interactive memory management where users might instruct the agent about what to remember

- **Background (Automatic)** is best for:
  - Comprehensive memory extraction without interrupting conversations
  - Pattern analysis across multiple interactions
  - Maintaining consistent memory without relying on agent decisions

**Diagram: Combined Processing Approach**
```mermaid
graph TD
    subgraph "Combined Processing Approach"
        User["User"] -->|"Message"| ReactAgent["create_react_agent"]
        ReactAgent -->|"Response"| User
        
        ReactAgent -->|"Immediate critical info"| ManageTool["create_manage_memory_tool"]
        ManageTool -->|"store.put()"| InMemStore["InMemoryStore"]
        
        Messages["Message History"] -->|"Automatic processing"| StoreManager["create_memory_store_manager"]
        StoreManager -->|"LLM extraction"| LLMModel["anthropic:claude-3-5-sonnet-latest"]
        LLMModel -->|"Memory objects"| InMemStore
        
        InMemStore -->|"store.search()"| SearchTool["create_search_memory_tool"]
        SearchTool -->|"Retrieved context"| ReactAgent
        
        subgraph "Optional Debouncing"
            ReflectionExec["ReflectionExecutor"]
            DelayedProc["after_seconds=1800"]
        end
        
        Messages -.->|"For efficiency"| ReflectionExec
        ReflectionExec --> DelayedProc
        DelayedProc --> StoreManager
    end
```

In practice, many applications combine both approaches:
- Use hot path for immediate, critical memory operations
- Use background processing for thorough, non-disruptive memory management

By understanding both approaches, you can choose the best strategy for your specific use case or combine them for a comprehensive memory management solution.

Sources: [docs/docs/concepts/conceptual_guide.md:296-307]()

---

# Page: Hot Path Memory (Agent-Driven)

# Hot Path Memory (Agent-Driven)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/hot_path_quickstart.md](docs/docs/hot_path_quickstart.md)
- [src/langmem/knowledge/tools.py](src/langmem/knowledge/tools.py)

</details>



This document covers LangMem's hot path memory processing approach, where agents actively decide what information to store as memories during real-time conversations using memory management tools. This approach gives agents conscious control over their memory formation process.

For automated memory extraction that happens after conversations, see [Background Memory Processing](#3.2). For the broader context of memory processing approaches, see [Processing Approaches](#3).

## Overview

Hot path memory processing enables agents to make deliberate decisions about memory storage during active conversations. Agents use specialized tools to create, update, delete, and search memories in real-time as part of their reasoning process. This approach provides immediate memory persistence and allows for strategic memory management based on conversational context.

The hot path approach relies on two primary tools from [src/langmem/knowledge/tools.py]():
- `create_manage_memory_tool` for creating, updating, and deleting memories
- `create_search_memory_tool` for retrieving relevant memories during conversations

**Hot Path Memory Flow During Conversation**
```mermaid
sequenceDiagram
    participant User
    participant Agent[Agent]
    participant ManageTool[manage_memory]
    participant SearchTool[search_memory]
    participant BaseStore[BaseStore]
    
    User->>Agent: "Remember that I prefer dark mode"
    Agent->>SearchTool: "Search for display preferences"
    SearchTool->>BaseStore: "search(namespace, query='display preferences')"
    BaseStore-->>SearchTool: "[]"
    SearchTool-->>Agent: "No relevant memories found"
    Agent->>ManageTool: "create(content='User prefers dark mode')"
    ManageTool->>BaseStore: "put(namespace, key=uuid, value=content)"
    BaseStore-->>ManageTool: "Memory stored"
    ManageTool-->>Agent: "created memory {uuid}"
    Agent-->>User: "I'll remember your dark mode preference"
    
    Note over User,BaseStore: Later conversation
    User->>Agent: "What display mode do I like?"
    Agent->>SearchTool: "Search for display preferences"
    SearchTool->>BaseStore: "search(namespace, query='display mode')"
    BaseStore-->>SearchTool: "[{content: 'User prefers dark mode'}]"
    SearchTool-->>Agent: "Found: User prefers dark mode"
    Agent-->>User: "You prefer dark mode"
```

Sources: [src/langmem/knowledge/tools.py:25-486](), [docs/docs/hot_path_quickstart.md:1-176]()

## Memory Management Tool

The `create_manage_memory_tool` function creates a tool that agents can use to perform CRUD operations on their memory store. This tool supports three primary actions: create, update, and delete.

### Tool Configuration

The tool accepts several configuration parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `namespace` | `tuple[str, ...]` or `str` | Namespace template for organizing memories |
| `instructions` | `str` | Custom instructions for when to use the tool |
| `schema` | `Type` | Expected schema for memory content (defaults to `str`) |
| `actions_permitted` | `tuple` | Allowed actions: create, update, delete |
| `store` | `BaseStore` | Storage backend (uses context if None) |
| `name` | `str` | Tool name for agent usage |

**Memory Management Tool Architecture**
```mermaid
graph TB
    subgraph ToolCreation["create_manage_memory_tool Function"]
        Config[Configuration]
        NamespaceTemplate[NamespaceTemplate]
        ActionValidation[Action Validation]
    end
    
    subgraph ToolImplementation["Generated Tool Functions"]
        AsyncFunc[amanage_memory]
        SyncFunc[manage_memory]
        Wrapper[_ToolWithRequired]
    end
    
    subgraph Operations["Memory Operations"]
        Create[Create Memory]
        Update[Update Memory] 
        Delete[Delete Memory]
    end
    
    subgraph Storage["Storage Layer"]
        BaseStoreInterface[BaseStore Interface]
        NamespaceResolution[Namespace Resolution]
        Serialization[Content Serialization]
    end
    
    Config --> NamespaceTemplate
    Config --> ActionValidation
    NamespaceTemplate --> AsyncFunc
    NamespaceTemplate --> SyncFunc
    ActionValidation --> AsyncFunc
    ActionValidation --> SyncFunc
    
    AsyncFunc --> Wrapper
    SyncFunc --> Wrapper
    
    Wrapper --> Create
    Wrapper --> Update
    Wrapper --> Delete
    
    Create --> BaseStoreInterface
    Update --> BaseStoreInterface
    Delete --> BaseStoreInterface
    
    BaseStoreInterface --> NamespaceResolution
    BaseStoreInterface --> Serialization
```

Sources: [src/langmem/knowledge/tools.py:25-356]()

### Action Types and Validation

The tool validates actions and parameters based on the permitted operations:

- **Create**: Requires `content`, generates new UUID, rejects explicit `id`
- **Update**: Requires both `content` and `id` of existing memory
- **Delete**: Requires only `id`, removes memory from store

The function dynamically creates type annotations based on `actions_permitted` using `typing.Literal` [src/langmem/knowledge/tools.py:266]().

Sources: [src/langmem/knowledge/tools.py:271-303](), [src/langmem/knowledge/tools.py:305-337]()

## Memory Search Tool

The `create_search_memory_tool` function creates a tool for retrieving memories using semantic or exact matching. The tool queries the BaseStore and returns formatted results.

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search query to match against memories |
| `limit` | `int` | Maximum results to return (default: 10) |
| `offset` | `int` | Results to skip for pagination (default: 0) |
| `filter` | `dict` | Additional filter criteria |

The tool supports two response formats controlled by the `response_format` parameter:
- `"content"`: Returns serialized memory content only
- `"content_and_artifact"`: Returns both serialized content and raw memory objects

Sources: [src/langmem/knowledge/tools.py:362-486]()

## Agent Integration Patterns

Hot path memory tools integrate with agents through LangGraph's tool system. Agents receive these tools in their tool list and can call them during their reasoning process.

### ReAct Agent Integration

```mermaid
graph TB
    subgraph AgentSetup["Agent Setup"]
        CreateReactAgent[create_react_agent]
        PromptFunction[prompt function]
        MemoryTools[Memory Tools]
    end
    
    subgraph MemoryTools["Memory Tools"]
        ManageMemoryTool[create_manage_memory_tool]
        SearchMemoryTool[create_search_memory_tool]
    end
    
    subgraph Execution["Agent Execution"]
        MessageProcessing[Message Processing]
        ToolSelection[Tool Selection]
        MemoryOperations[Memory Operations]
        Response[Response Generation]
    end
    
    subgraph Storage["Storage Layer"]
        BaseStore[BaseStore]
        NamespaceOrg[Namespace Organization]
        Persistence[Memory Persistence]
    end
    
    CreateReactAgent --> PromptFunction
    CreateReactAgent --> MemoryTools
    PromptFunction --> SearchMemoryTool
    ManageMemoryTool --> CreateReactAgent
    SearchMemoryTool --> CreateReactAgent
    
    MessageProcessing --> ToolSelection
    ToolSelection --> MemoryOperations
    MemoryOperations --> Response
    
    MemoryOperations --> BaseStore
    BaseStore --> NamespaceOrg
    NamespaceOrg --> Persistence
```

Sources: [docs/docs/hot_path_quickstart.md:74-89]()

### Custom Agent Integration

The tools work with any LangGraph agent architecture that supports tool calling. Custom agents can integrate memory tools by including them in their tool list and implementing appropriate tool calling logic.

Sources: [src/langmem/knowledge/tools.py:25-39]()

## Namespace Organization

Namespaces provide hierarchical organization for memories using the `NamespaceTemplate` utility. Templates support runtime variable substitution from the LangGraph configuration.

### Namespace Patterns

| Pattern | Template | Use Case |
|---------|----------|----------|
| Global | `("memories",)` | Shared memories across all users |
| Per-user | `("memories", "{langgraph_user_id}")` | User-specific memory isolation |
| Per-organization | `("memories", "{org_id}", "{user_id}")` | Hierarchical organization |
| Feature-specific | `("memories", "{user_id}", "preferences")` | Categorized memory types |

The `NamespaceTemplate` class [src/langmem/knowledge/tools.py:263]() handles runtime template resolution by substituting bracketed variables with values from the LangGraph configuration's `configurable` field.

Sources: [docs/docs/hot_path_quickstart.md:94-103](), [src/langmem/knowledge/tools.py:292](), [src/langmem/knowledge/tools.py:326](), [src/langmem/knowledge/tools.py:444]()

## Storage Integration

Hot path memory tools integrate with LangGraph's `BaseStore` interface through the `_get_store` helper function [src/langmem/knowledge/tools.py:489-497](). The function either uses a provided store or retrieves the store from LangGraph's context using `get_store()`.

### Content Serialization

The `_ensure_json_serializable` function [src/langmem/knowledge/tools.py:500-510]() handles serialization of memory content:
- Primitives (str, int, float, bool, dict, list) are stored directly  
- Pydantic models are serialized using `model_dump(mode="json")`
- Other objects fall back to string representation

### Store Configuration

```mermaid
graph TB
    subgraph StoreConfig["Store Configuration"]
        InitialStore[initial_store parameter]
        ContextStore[get_store from context]
        StoreSelection[_get_store function]
    end
    
    subgraph StoreTypes["Store Types"]
        InMemoryStore[InMemoryStore]
        PostgresStore[AsyncPostgresStore] 
        CustomStore[Custom BaseStore]
    end
    
    subgraph Operations["Store Operations"]
        Put[put/aput]
        Search[search/asearch]
        Delete[delete/adelete]
    end
    
    InitialStore --> StoreSelection
    ContextStore --> StoreSelection
    StoreSelection --> InMemoryStore
    StoreSelection --> PostgresStore
    StoreSelection --> CustomStore
    
    InMemoryStore --> Put
    PostgresStore --> Put
    CustomStore --> Put
    
    InMemoryStore --> Search
    PostgresStore --> Search
    CustomStore --> Search
    
    InMemoryStore --> Delete
    PostgresStore --> Delete
    CustomStore --> Delete
```

Sources: [src/langmem/knowledge/tools.py:489-497](), [src/langmem/knowledge/tools.py:500-510](), [docs/docs/hot_path_quickstart.md:66-71]()

## Tool Schema Customization

The management tool supports custom schemas for structured memory content. When a schema is provided, the tool validates and serializes content according to the schema definition.

### Schema Examples

For string-based memories (default):
```python
# Uses str schema by default
memory_tool = create_manage_memory_tool(namespace=("memories",))
```

For structured memories with Pydantic models:
```python
class UserProfile(BaseModel):
    name: str
    preferences: dict
    
memory_tool = create_manage_memory_tool(
    namespace=("profiles", "{user_id}"),
    schema=UserProfile
)
```

The tool automatically handles serialization through the `_ensure_json_serializable` function for both simple and complex data types.

Sources: [src/langmem/knowledge/tools.py:178-197](), [src/langmem/knowledge/tools.py:500-510]()

---

# Page: Background Memory Processing

# Background Memory Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/background_quickstart.md](docs/docs/background_quickstart.md)
- [src/langmem/graphs/semantic.py](src/langmem/graphs/semantic.py)
- [src/langmem/reflection.py](src/langmem/reflection.py)

</details>



Background memory processing enables automatic, deferred extraction and consolidation of memories from conversation history without blocking the main conversation flow. This approach processes memories "subconsciously" after conversations occur, as opposed to hot path processing where agents actively decide what to remember during conversation. For information about agent-driven memory processing, see [Hot Path Memory (Agent-Driven)](#3.1).

The core component for background processing is the `ReflectionExecutor` system, which handles task queuing, threading, and both local and remote execution patterns. This system integrates with memory managers created by `create_memory_store_manager` to process conversation history asynchronously.

## ReflectionExecutor Architecture

The `ReflectionExecutor` provides a unified interface for background memory processing through two implementation patterns: local processing with threading and queue management, and remote processing via LangGraph services.

```mermaid
graph TB
    subgraph "ReflectionExecutor Factory"
        RF["ReflectionExecutor()"]
    end
    
    subgraph "Local Processing Path"
        LRE["LocalReflectionExecutor"]
        TQ["_task_queue<br/>PriorityQueue"]
        PT["_pending_tasks<br/>dict[str, PendingTask]"]
        WT["_worker<br/>threading.Thread"]
        BS["BaseStore"]
    end
    
    subgraph "Remote Processing Path"
        RRE["RemoteReflectionExecutor"]
        LC["LangGraphClient"]
        SLC["SyncLangGraphClient"]
        CTPE["ContextThreadPoolExecutor"]
    end
    
    subgraph "Common Interface"
        SM["submit()"]
        SR["search()"]
        ASR["asearch()"]
    end
    
    subgraph "Memory Processing"
        R["Runnable reflector"]
        MM["create_memory_store_manager"]
        PL["payload: dict[str, Any]"]
    end
    
    RF --> LRE
    RF --> RRE
    
    LRE --> TQ
    LRE --> PT
    LRE --> WT
    LRE --> BS
    
    RRE --> LC
    RRE --> SLC
    RRE --> CTPE
    
    LRE --> SM
    LRE --> SR
    LRE --> ASR
    
    RRE --> SM
    RRE --> SR
    RRE --> ASR
    
    MM --> R
    R --> PL
    
    style RF fill:#e1f5fe
    style LRE fill:#f3e5f5
    style RRE fill:#e8f5e8
```

Sources: [src/langmem/reflection.py:89-141]()

## Local vs Remote Processing

The `ReflectionExecutor` factory function determines the execution mode based on the reflector parameter type. Local processing uses a `Runnable` reflector with direct store access, while remote processing uses a string assistant ID to delegate work to LangGraph services.

### Local Processing

Local processing uses `LocalReflectionExecutor` with threading and queue management to handle background tasks without blocking the main application.

```mermaid
graph TB
    subgraph "LocalReflectionExecutor Components"
        LRE["LocalReflectionExecutor"]
        R["_reflector: Runnable"]
        NS["_namespace: NamespaceTemplate"]
        S["_store: BaseStore"]
    end
    
    subgraph "Task Management"
        TQ["_task_queue<br/>PriorityQueue[tuple[float, PendingTask]]"]
        PT["_pending_tasks<br/>dict[str, PendingTask]"]
        WR["_worker_running: bool"]
        W["_worker: threading.Thread"]
    end
    
    subgraph "Task Processing"
        PTK["PendingTask"]
        CE["cancel_event: threading.Event"]
        F["future: Future"]
        C["config: RunnableConfig"]
        P["payload: dict[str, Any]"]
    end
    
    subgraph "Queue Processing Loop"
        PQ["_process_queue()"]
        ET["execute_at check"]
        CC["cancel check"]
        RI["_reflector.invoke()"]
        SR["set_result()"]
    end
    
    LRE --> R
    LRE --> NS
    LRE --> S
    LRE --> TQ
    LRE --> PT
    LRE --> WR
    LRE --> W
    
    TQ --> PTK
    PT --> PTK
    PTK --> CE
    PTK --> F
    PTK --> C
    PTK --> P
    
    W --> PQ
    PQ --> ET
    PQ --> CC
    PQ --> RI
    PQ --> SR
    
    style LRE fill:#f3e5f5
    style TQ fill:#fff3e0
    style PQ fill:#e8f5e8
```

Sources: [src/langmem/reflection.py:254-387](), [src/langmem/reflection.py:389-472]()

### Remote Processing

Remote processing uses `RemoteReflectionExecutor` to delegate memory processing tasks to LangGraph services running elsewhere.

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| `_assistant_id` | Target LangGraph assistant | String identifier |
| `_aclient` | Async LangGraph client | Auto-configured or provided |
| `_client` | Sync LangGraph client | Auto-configured or provided |
| `_executor` | Thread pool executor | `ContextThreadPoolExecutor` |

Sources: [src/langmem/reflection.py:143-252]()

## Task Queuing and Threading

The `LocalReflectionExecutor` implements sophisticated task management with priority queuing, cancellation support, and thread-safe execution.

### Task Lifecycle

```mermaid
sequenceDiagram
    participant C as "Client Code"
    participant LRE as "LocalReflectionExecutor"
    participant TQ as "_task_queue"
    participant PT as "_pending_tasks"
    participant W as "_worker thread"
    participant R as "_reflector"
    
    C->>LRE: "submit(payload, after_seconds=5)"
    LRE->>LRE: "create PendingTask with Future"
    LRE->>PT: "store by thread_id (cancel existing)"
    LRE->>TQ: "put (execute_at, task)"
    LRE-->>C: "return Future"
    
    Note over W: "Background processing"
    W->>TQ: "get(timeout=1)"
    W->>W: "check execute_at vs current time"
    alt "too early"
        W->>W: "sleep(min(delay, 1))"
        W->>TQ: "put back if still early"
    else "ready to execute"
        W->>W: "check cancel_event"
        W->>R: "invoke(payload)"
        R-->>W: "result"
        W->>LRE: "future.set_result(result)"
        W->>PT: "remove from pending_tasks"
    end
```

Sources: [src/langmem/reflection.py:273-330](), [src/langmem/reflection.py:401-472]()

### Cancellation and Conflict Resolution

The system handles task cancellation and thread-specific conflict resolution to prevent duplicate processing:

- When a new task is submitted for an existing `thread_id`, the previous task is cancelled via `cancel_event.set()`
- Tasks check cancellation status before execution in `_process_queue`
- The `Future` objects allow callers to cancel or wait for completion

Sources: [src/langmem/reflection.py:308-313](), [src/langmem/reflection.py:414-423]()

## Integration with Memory Managers

Background processing integrates with memory managers created by `create_memory_store_manager` to process conversation history asynchronously.

```mermaid
graph LR
    subgraph "Memory Manager Creation"
        CMSM["create_memory_store_manager()"]
        R["returns Runnable"]
        NS["namespace parameter"]
    end
    
    subgraph "ReflectionExecutor Setup"
        RE["ReflectionExecutor(reflector=runnable)"]
        LRE["LocalReflectionExecutor"]
        NMT["namespace: NamespaceTemplate"]
    end
    
    subgraph "Background Processing"
        S["submit(payload)"]
        PL["payload: {'messages': [...]}"]
        I["reflector.invoke(payload)"]
        EX["extract/consolidate memories"]
        ST["store in BaseStore"]
    end
    
    subgraph "Store Integration"
        BS["BaseStore"]
        SR["search() / asearch()"]
        MI["MemoryItem results"]
    end
    
    CMSM --> R
    R --> RE
    RE --> LRE
    LRE --> NMT
    
    S --> PL
    PL --> I
    I --> EX
    EX --> ST
    ST --> BS
    
    LRE --> SR
    SR --> MI
    
    style CMSM fill:#e1f5fe
    style RE fill:#f3e5f5
    style BS fill:#e8f5e8
```

Sources: [src/langmem/reflection.py:257-262](), [docs/docs/background_quickstart.md:48-63]()

## Usage Patterns

### Basic Background Processing

The most common pattern involves creating a memory manager and using it for deferred processing:

```python
# Create memory manager for background processing
memory_manager = create_memory_store_manager(
    "anthropic:claude-3-5-sonnet-latest",
    namespace=("memories",),
)

# Use in LangGraph entrypoint
@entrypoint(store=store)
async def chat(message: str):
    response = llm.invoke(message)
    to_process = {"messages": [{"role": "user", "content": message}] + [response]}
    await memory_manager.ainvoke(to_process)  # Background processing
    return response.content
```

Sources: [docs/docs/background_quickstart.md:48-63](), [src/langmem/graphs/semantic.py:40-47]()

### Direct ReflectionExecutor Usage

For more control over background processing, you can use `ReflectionExecutor` directly:

```python
# Create executor with memory manager
executor = ReflectionExecutor(memory_manager, store=store)

# Submit tasks with delay
future = executor.submit(
    {"messages": conversation_history},
    after_seconds=30  # Process 30 seconds after submission
)

# Search processed memories
memories = executor.search(query="user preferences", limit=5)
```

The `after_seconds` parameter enables debounced processing to avoid redundant work during active conversations.

Sources: [src/langmem/reflection.py:273-330]()

### Remote Processing Setup

For distributed deployments, use remote processing with LangGraph services:

```python
# Remote executor with assistant ID
executor = ReflectionExecutor(
    "memory-assistant-v1",  # String assistant ID
    namespace=("user", "123"),
    url="https://my-langgraph-service.com"
)

# Same interface as local processing
future = executor.submit(conversation_data)
memories = await executor.asearch(query="recent topics")
```

Sources: [src/langmem/reflection.py:143-158](), [src/langmem/reflection.py:161-198]()

---

# Page: Integration

# Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/langmem/knowledge/tools.py](src/langmem/knowledge/tools.py)

</details>



This document provides an overview of how LangMem integrates with different frameworks and systems. It covers the core integration architecture, patterns for connecting LangMem with various agent frameworks, and the tool-based integration approach that enables seamless memory management across different systems.

For detailed information about specific integration approaches, see [LangGraph Integration](#4.1), [ReAct Agents](#4.2.1), [CrewAI Integration](#4.2.2), and [Custom Agents](#4.2.3).

## Integration Architecture

LangMem follows a two-layer integration architecture that provides flexibility for different deployment scenarios and framework requirements:

### Two-Layer Integration Design

```mermaid
graph TB
    subgraph "Application Layer"
        CA["Custom Agents"]
        RA["create_react_agent"]
        CB["Chatbots"]
        CR["CrewAI"]
        WF["Workflows"]
    end
    
    subgraph "LangMem Integration Layers"
        subgraph "Stateful Integration Layer"
            MSM["create_memory_store_manager"]
            MMT["create_manage_memory_tool"]
            SMT["create_search_memory_tool"]
            RE["ReflectionExecutor"]
        end
        
        subgraph "Core API Layer (Stateless)"
            MM["create_memory_manager"]
            PO["create_prompt_optimizer"]
            TE["create_thread_extractor"]
            SM["summarize_messages"]
        end
    end
    
    subgraph "Storage & External Systems"
        BS["BaseStore"]
        IMS["InMemoryStore"]
        PGS["AsyncPostgresStore"]
        LLM["LLM Providers"]
    end
    
    %% Application to Stateful Integration
    RA --> MMT
    RA --> SMT
    CA --> MSM
    CA --> MMT
    CB --> SM
    CR --> MMT
    WF --> RE
    
    %% Stateful to Core API
    MSM --> MM
    MMT --> MM
    SMT --> MM
    RE --> MM
    RE --> TE
    
    %% Core to Storage/External
    MM --> LLM
    PO --> LLM
    MSM --> BS
    MMT --> BS
    SMT --> BS
    
    %% Storage implementations
    BS --> IMS
    BS --> PGS
```

**Core API Layer (Stateless)**: Provides functional primitives that work with any storage system. These functions handle memory extraction, prompt optimization, and conversation processing without maintaining state.

**Stateful Integration Layer**: Connects the Core API to specific frameworks and storage systems. This layer manages persistent state, provides agent tools, and handles background processing.

Sources: [src/langmem/knowledge/tools.py:1-531](), [README.md:1-96]()

## Integration Patterns

LangMem supports three primary integration patterns, each suited for different use cases and architectural requirements:

### Integration Pattern Overview

```mermaid
graph LR
    subgraph "Hot Path Integration"
        HP_APP["Application"]
        HP_TOOLS["Memory Tools"]
        HP_STORE["BaseStore"]
        
        HP_APP --> HP_TOOLS
        HP_TOOLS --> HP_STORE
    end
    
    subgraph "Background Integration"
        BG_APP["Application"]
        BG_EXEC["ReflectionExecutor"]
        BG_MGR["Memory Manager"]
        BG_STORE["BaseStore"]
        
        BG_APP --> BG_EXEC
        BG_EXEC --> BG_MGR
        BG_MGR --> BG_STORE
    end
    
    subgraph "Hybrid Integration"
        HY_APP["Application"]
        HY_TOOLS["Memory Tools"]
        HY_EXEC["ReflectionExecutor"] 
        HY_STORE["BaseStore"]
        
        HY_APP --> HY_TOOLS
        HY_APP --> HY_EXEC
        HY_TOOLS --> HY_STORE
        HY_EXEC --> HY_STORE
    end
```

| Pattern | Description | Use Cases | Key Components |
|---------|-------------|-----------|----------------|
| **Hot Path** | Agents actively manage memory during conversations | Interactive agents, ReAct workflows | `create_manage_memory_tool`, `create_search_memory_tool` |
| **Background** | Deferred memory processing after conversations | High-throughput systems, batch processing | `ReflectionExecutor`, `create_memory_manager` |
| **Hybrid** | Combines immediate and deferred memory operations | Complex agents needing both patterns | All memory components |

Sources: [src/langmem/knowledge/tools.py:25-356](), [README.md:30-86]()

## Tool-Based Integration

The primary integration mechanism for LangMem is through memory tools that can be added to any agent framework supporting LangChain tools. These tools provide a standardized interface for memory operations across different systems.

### Memory Tool Integration

```mermaid
graph TB
    subgraph "Agent Frameworks"
        REACT["create_react_agent"]
        CUSTOM["Custom Agents"]
        CREWAI["CrewAI Agents"]
    end
    
    subgraph "LangMem Tools"
        MMT["create_manage_memory_tool"]
        SMT["create_search_memory_tool"]
    end
    
    subgraph "Tool Functions"
        subgraph "Memory Management"
            CREATE["create action"]
            UPDATE["update action"] 
            DELETE["delete action"]
        end
        
        subgraph "Memory Search"
            SEARCH["search query"]
            FILTER["filter options"]
            LIMIT["result limiting"]
        end
    end
    
    subgraph "Storage Integration"
        NS["NamespaceTemplate"]
        BS["BaseStore"]
        STORE["get_store()"]
    end
    
    %% Framework to Tools
    REACT --> MMT
    REACT --> SMT
    CUSTOM --> MMT
    CUSTOM --> SMT
    CREWAI --> MMT
    CREWAI --> SMT
    
    %% Tools to Functions
    MMT --> CREATE
    MMT --> UPDATE
    MMT --> DELETE
    SMT --> SEARCH
    SMT --> FILTER
    SMT --> LIMIT
    
    %% Functions to Storage
    CREATE --> NS
    UPDATE --> NS
    DELETE --> NS
    SEARCH --> NS
    NS --> BS
    BS --> STORE
```

**Memory Management Tool**: The `create_manage_memory_tool` function creates tools that allow agents to create, update, and delete memories. It supports customizable schemas and action permissions.

**Memory Search Tool**: The `create_search_memory_tool` function creates tools for semantic and exact matching searches across stored memories with filtering and pagination support.

**Namespace Integration**: Both tools use `NamespaceTemplate` for dynamic namespace resolution, enabling user isolation and organizational flexibility.

Sources: [src/langmem/knowledge/tools.py:25-356](), [src/langmem/knowledge/tools.py:362-486]()

## Framework Support

LangMem provides integration support for multiple agent frameworks through its tool-based architecture:

### Framework Integration Matrix

| Framework | Integration Type | Key Features | Status |
|-----------|-----------------|--------------|--------|
| **LangGraph** | Native | BaseStore integration, create_react_agent support | Full Support |
| **Custom Agents** | Tool-based | Direct tool integration, flexible architecture | Full Support |
| **CrewAI** | Tool-based | Multi-agent memory sharing, team workflows | Full Support |
| **LangChain Agents** | Tool-based | Standard tool interface, callback support | Full Support |

### Integration Requirements

All framework integrations share common requirements:

1. **Tool Support**: Framework must support LangChain `StructuredTool` interface
2. **Storage Access**: Access to a `BaseStore` implementation for persistence  
3. **Configuration**: Ability to pass runtime configuration for namespace resolution
4. **Async Support**: Optional but recommended for better performance

### Framework-Specific Integration

```mermaid
graph TB
    subgraph "LangGraph Integration"
        LG_STORE["BaseStore"]
        LG_CONFIG["Runtime Config"]
        LG_TOOLS["Memory Tools"]
        LG_AGENT["create_react_agent"]
        
        LG_STORE --> LG_TOOLS
        LG_CONFIG --> LG_TOOLS  
        LG_TOOLS --> LG_AGENT
    end
    
    subgraph "CrewAI Integration"
        CREW_TOOLS["Memory Tools"]
        CREW_STORE["External Store"]
        CREW_AGENTS["Multiple Agents"]
        CREW_SHARED["Shared Namespace"]
        
        CREW_STORE --> CREW_TOOLS
        CREW_TOOLS --> CREW_AGENTS
        CREW_SHARED --> CREW_TOOLS
    end
    
    subgraph "Custom Integration"
        CUSTOM_LOOP["REACT Loop"]
        CUSTOM_TOOLS["Memory Tools"]
        CUSTOM_STORE["Custom Store"]
        CUSTOM_LOGIC["Custom Logic"]
        
        CUSTOM_STORE --> CUSTOM_TOOLS
        CUSTOM_TOOLS --> CUSTOM_LOOP
        CUSTOM_LOGIC --> CUSTOM_LOOP
    end
```

**LangGraph**: Provides the most seamless integration with native BaseStore support, automatic configuration, and prebuilt agent compatibility.

**CrewAI**: Enables multi-agent systems with shared memory through namespace organization and external store configuration.

**Custom Agents**: Offers maximum flexibility for custom REACT loops and specialized agent architectures.

Sources: [src/langmem/knowledge/tools.py:489-497](), [README.md:34-58]()

---

# Page: LangGraph Integration

# LangGraph Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/hot_path_quickstart.md](docs/docs/hot_path_quickstart.md)
- [src/langmem/graphs/auth.py](src/langmem/graphs/auth.py)
- [src/langmem/knowledge/__init__.py](src/langmem/knowledge/__init__.py)
- [src/langmem/knowledge/tools.py](src/langmem/knowledge/tools.py)

</details>



This document covers LangMem's native integration with LangGraph, focusing on how LangMem leverages LangGraph's storage layer, configuration system, and agent framework. This includes the memory tools that agents can use and how they interface with LangGraph's `BaseStore`.

For information about integrating with other agent frameworks like CrewAI or custom agents, see [Agent Integration](#4.2).

## Core Integration Components

LangMem's LangGraph integration centers around two main tools that provide agents with memory capabilities through LangGraph's `BaseStore` infrastructure. These tools are designed to work seamlessly within LangGraph's configuration and execution context.

```mermaid
graph TB
    subgraph "LangGraph Framework"
        BS["BaseStore<br/>(InMemoryStore / AsyncPostgresStore)"]
        CRA["create_react_agent<br/>PreBuilt Agent"]
        GS["get_store()<br/>Context Access"]
        EP["@entrypoint<br/>Graph Entry Point"]
        SG["StateGraph<br/>Custom Graph"]
    end
    
    subgraph "LangMem Tools"
        MMT["create_manage_memory_tool<br/>Memory CRUD Operations"]
        SMT["create_search_memory_tool<br/>Memory Retrieval"]
        NT["NamespaceTemplate<br/>Dynamic Namespacing"]
    end
    
    subgraph "Memory Operations"
        CREATE["Create Memory<br/>store.aput()"]
        UPDATE["Update Memory<br/>store.aput()"] 
        DELETE["Delete Memory<br/>store.adelete()"]
        SEARCH["Search Memory<br/>store.asearch()"]
    end
    
    subgraph "Configuration System"
        CFG["RunnableConfig<br/>Thread & User Context"]
        NS["Namespace Resolution<br/>{user_id} → actual_value"]
    end
    
    %% Tool dependencies
    MMT --> BS
    SMT --> BS
    MMT --> GS
    SMT --> GS
    MMT --> NT
    SMT --> NT
    
    %% Memory operations
    MMT --> CREATE
    MMT --> UPDATE
    MMT --> DELETE
    SMT --> SEARCH
    
    %% Storage operations
    CREATE --> BS
    UPDATE --> BS
    DELETE --> BS
    SEARCH --> BS
    
    %% Agent integration
    CRA --> MMT
    CRA --> SMT
    EP --> MMT
    EP --> SMT
    SG --> MMT
    SG --> SMT
    
    %% Configuration flow
    CFG --> NT
    NT --> NS
    NS --> BS
```

**LangGraph Integration Architecture**

Sources: [src/langmem/knowledge/tools.py:1-531](), [docs/docs/hot_path_quickstart.md:35-90]()

## Memory Tools

LangMem provides two primary tools that integrate with LangGraph's tool system and storage infrastructure:

### Memory Management Tool

The `create_manage_memory_tool` function creates a tool that allows agents to perform CRUD operations on their persistent memory.

| Operation | Description | Tool Parameters |
|-----------|-------------|----------------|
| `create` | Create new memory | `content`, `action="create"` |
| `update` | Update existing memory | `content`, `id`, `action="update"` |
| `delete` | Delete memory by ID | `id`, `action="delete"` |

```mermaid
sequenceDiagram
    participant A as Agent
    participant MMT as manage_memory_tool
    participant GS as get_store()
    participant BS as BaseStore
    participant NT as NamespaceTemplate
    
    A->>MMT: "action='create', content='user prefers dark mode'"
    MMT->>GS: get_store()
    GS-->>MMT: BaseStore instance
    MMT->>NT: namespacer()
    NT-->>MMT: ("memories", "user-123")
    MMT->>BS: aput(namespace, key=uuid, value=content)
    BS-->>MMT: Success
    MMT-->>A: "created memory {uuid}"
```

**Memory Management Tool Flow**

The tool signature supports customizable schemas and action restrictions:

```python
# Basic string content
create_manage_memory_tool(namespace=("memories", "{user_id}"))

# Custom schema with restricted actions  
create_manage_memory_tool(
    namespace=("profiles", "{user_id}"),
    schema=UserProfile,
    actions_permitted=("create", "update")
)
```

Sources: [src/langmem/knowledge/tools.py:25-356]()

### Memory Search Tool

The `create_search_memory_tool` function creates a tool for semantic and exact search across stored memories.

```mermaid
graph LR
    subgraph "Search Parameters"
        Q["query: str<br/>Search Query"]
        L["limit: int<br/>Max Results"]
        O["offset: int<br/>Skip Results"]
        F["filter: dict<br/>Additional Criteria"]
    end
    
    subgraph "Search Process"
        SMT["search_memory_tool"]
        NS["Namespace Resolution"]
        SS["store.asearch()"]
        RF["Response Formatting"]
    end
    
    subgraph "Response Formats"
        CO["content<br/>JSON serialized memories"]
        CAA["content_and_artifact<br/>JSON + raw memory objects"]
    end
    
    Q --> SMT
    L --> SMT
    O --> SMT
    F --> SMT
    
    SMT --> NS
    NS --> SS
    SS --> RF
    
    RF --> CO
    RF --> CAA
```

**Memory Search Process**

Sources: [src/langmem/knowledge/tools.py:362-486]()

## Storage Integration

LangMem integrates with LangGraph's `BaseStore` system, supporting both development and production storage backends.

### Store Configuration

| Store Type | Use Case | Configuration |
|------------|----------|---------------|
| `InMemoryStore` | Development/Testing | Ephemeral, vector indexing |
| `AsyncPostgresStore` | Production | Persistent, scalable |
| Custom `BaseStore` | Specialized needs | User-implemented |

```python
# Development setup
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)

# Production setup (provided automatically on LangGraph platform)
# AsyncPostgresStore with persistent storage
```

### Context-Based Store Access

LangMem tools use LangGraph's context system to access the configured store:

```mermaid
graph TB
    subgraph "LangGraph Context"
        CV["contextvars<br/>Thread-local Context"]
        GS["get_store()<br/>Context Accessor"]
        CFG["RunnableConfig<br/>Execution Context"]
    end
    
    subgraph "Tool Execution"
        MMT["manage_memory_tool"]
        SMT["search_memory_tool"]
        GSF["_get_store()<br/>Helper Function"]
    end
    
    subgraph "Store Resolution"
        IS["initial_store<br/>Explicit Store"]
        CS["Configured Store<br/>From Context"]
        CE["ConfigurationError<br/>No Store Available"]
    end
    
    CFG --> CV
    CV --> GS
    
    MMT --> GSF
    SMT --> GSF
    
    GSF --> IS
    GSF --> GS
    GS --> CS
    
    IS --> CS
    CS --> MMT
    CS --> SMT
    
    GS -.->|RuntimeError| CE
```

**Store Resolution Process**

Sources: [src/langmem/knowledge/tools.py:489-497](), [docs/docs/hot_path_quickstart.md:48-49](), [docs/docs/hot_path_quickstart.md:117-119]()

## Configuration and Namespacing

LangMem uses LangGraph's configuration system to provide dynamic namespace resolution and user isolation.

### Namespace Templating

The `NamespaceTemplate` class enables runtime namespace resolution using configuration values:

```python
# Template definition
namespace = ("memories", "{langgraph_user_id}", "preferences")

# Runtime resolution
config = {"configurable": {"langgraph_user_id": "user-123"}}
# Resolves to: ("memories", "user-123", "preferences")
```

### Common Namespace Patterns

| Pattern | Namespace Template | Use Case |
|---------|-------------------|----------|
| Global | `("memories",)` | Shared across all users |
| Per-user | `("memories", "{langgraph_user_id}")` | User isolation |
| Hierarchical | `("org", "{org_id}", "{user_id}")` | Multi-tenant |
| Typed | `("memories", "{user_id}", "preferences")` | Memory categorization |

```mermaid
graph TD
    subgraph "Configuration Input"
        RC["RunnableConfig"]
        CFG["configurable: dict"]
        UID["langgraph_user_id: 'user-123'"]
        OID["org_id: 'acme-corp'"]
    end
    
    subgraph "Namespace Templates"
        T1["('memories', '{langgraph_user_id}')"]
        T2["('{org_id}', 'memories', '{langgraph_user_id}')"]
        T3["('memories', '{langgraph_user_id}', 'preferences')"]
    end
    
    subgraph "Resolved Namespaces"
        R1["('memories', 'user-123')"]
        R2["('acme-corp', 'memories', 'user-123')"]
        R3["('memories', 'user-123', 'preferences')"]
    end
    
    RC --> CFG
    CFG --> UID
    CFG --> OID
    
    T1 --> R1
    T2 --> R2
    T3 --> R3
    
    UID --> R1
    UID --> R2
    UID --> R3
    OID --> R2
```

**Namespace Template Resolution**

Sources: [src/langmem/knowledge/tools.py:263](), [docs/docs/hot_path_quickstart.md:94-103]()

## Agent Integration

LangMem tools integrate seamlessly with LangGraph's agent constructs, particularly `create_react_agent`.

### ReAct Agent Integration

```python
from langgraph.prebuilt import create_react_agent
from langmem import create_manage_memory_tool, create_search_memory_tool

agent = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest",
    tools=[
        create_manage_memory_tool(namespace=("memories", "{langgraph_user_id}")),
        create_search_memory_tool(namespace=("memories", "{langgraph_user_id}")),
    ],
    store=store,
    checkpointer=checkpointer,
)
```

### Memory-Enhanced Prompts

Agents can dynamically load relevant memories in their prompt function:

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant PF as prompt_function
    participant GS as get_store()
    participant BS as BaseStore
    participant LLM as Language Model
    
    U->>A: User message
    A->>PF: state with messages
    PF->>GS: get_store()
    GS-->>PF: BaseStore instance
    PF->>BS: search(namespace, query=latest_message)
    BS-->>PF: relevant memories
    PF-->>A: enhanced prompt with memories
    A->>LLM: prompt + conversation + tools
    LLM-->>A: response with potential tool calls
    A-->>U: final response
```

**Memory-Enhanced Agent Flow**

Sources: [docs/docs/hot_path_quickstart.md:46-63](), [src/langmem/knowledge/tools.py:142-175]()

## Usage Patterns

### Basic Integration

```python
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool

# Configure store with embedding support
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)

# Create agent with memory capability
agent = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest", 
    tools=[create_manage_memory_tool(namespace=("memories",))],
    store=store,
)
```

### Multi-User Configuration

```python
# Per-user memory isolation
memory_tool = create_manage_memory_tool(
    namespace=("memories", "{langgraph_user_id}"),
    instructions="Store user-specific preferences and context."
)

# Usage with user-specific configuration
config = {"configurable": {"langgraph_user_id": "user-123"}}
agent.invoke({"messages": [...]}, config=config)
```

### Custom Schema Integration

```python
from pydantic import BaseModel

class UserPreferences(BaseModel):
    theme: str = "light"
    language: str = "en"
    notifications: bool = True

profile_tool = create_manage_memory_tool(
    namespace=("profiles", "{langgraph_user_id}"),
    schema=UserPreferences,
    actions_permitted=("create", "update"),
)
```

Sources: [docs/docs/hot_path_quickstart.md:32-90](), [src/langmem/knowledge/tools.py:178-258]()

---

# Page: Agent Integration

# Agent Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_episodic_memories.md](docs/docs/guides/extract_episodic_memories.md)
- [docs/docs/guides/memory_tools.md](docs/docs/guides/memory_tools.md)
- [docs/docs/guides/use_tools_in_crewai.md](docs/docs/guides/use_tools_in_crewai.md)
- [docs/docs/guides/use_tools_in_custom_agent.md](docs/docs/guides/use_tools_in_custom_agent.md)

</details>



This page provides an overview of integrating LangMem with different agent frameworks. LangMem's memory tools can be integrated with various types of agents to enable them to store, retrieve, and manage memories across conversations. For specific implementation details, see the child pages on [ReAct Agents](#4.2.1), [CrewAI Integration](#4.2.2), and [Custom Agents](#4.2.3).

## Memory Tools for Agent Integration

LangMem provides two primary tools that can be integrated with any agent framework:

1. `create_manage_memory_tool` - Allows agents to create, update, and delete memories
2. `create_search_memory_tool` - Enables agents to search through previously stored memories

These tools work with LangGraph's storage layer (typically `BaseStore` implementations) to provide persistent memory capabilities to agents.

```mermaid
graph TD
    subgraph "Agent System"
        Agent["Agent<br>(LangGraph ReAct, CrewAI, or Custom)"]
        
        subgraph "Memory Tools"
            ManageTool["create_manage_memory_tool()"]
            SearchTool["create_search_memory_tool()"]
        end
        
        subgraph "Storage Layer"
            Store["BaseStore<br>(InMemoryStore/AsyncPostgresStore)"]
        end
    end
    
    Agent -->|"uses"| ManageTool
    Agent -->|"uses"| SearchTool
    ManageTool -->|"store/update"| Store
    SearchTool -->|"retrieve"| Store
```

Sources: [README.md:36-57]()

## Integration Patterns

LangMem follows a consistent pattern for integrating with different agent frameworks. The general approach is:

1. Set up a storage backend (e.g., `InMemoryStore` or `AsyncPostgresStore`)
2. Create memory tools that are connected to this store
3. Add these tools to your agent's available tools
4. The agent can then actively use these tools during conversations

This pattern works across all supported agent frameworks, with minor variations in syntax.

```mermaid
sequenceDiagram
    participant User
    participant Agent as "Agent"
    participant MemTools as "Memory Tools"
    participant Store as "BaseStore"
    
    User->>Agent: Send message
    Agent->>MemTools: Call manage_memory tool
    MemTools->>Store: Store information
    Store-->>MemTools: Confirm storage
    MemTools-->>Agent: Return result
    
    User->>Agent: Ask about previous info
    Agent->>MemTools: Call search_memory tool
    MemTools->>Store: Search for relevant memories
    Store-->>MemTools: Return matching memories
    MemTools-->>Agent: Return search results
    Agent->>User: Respond with retrieved information
```

Sources: [README.md:68-86](), [docs/docs/guides/use_tools_in_crewai.md:19-49]()

## Supported Agent Frameworks

LangMem can be integrated with multiple agent frameworks:

### LangGraph ReAct Agents

The simplest integration is with LangGraph's `create_react_agent`, where memory tools are added directly to the agent's tool list.

### CrewAI

For multi-agent systems built with CrewAI, memory tools can be added to individual agents or shared across agents.

### Custom Agent Implementations

LangMem tools can also be used with custom agent implementations built on top of LLM APIs like Anthropic or OpenAI.

```mermaid
graph TD
    subgraph "Memory Tools"
        ManageTool["create_manage_memory_tool()"]
        SearchTool["create_search_memory_tool()"]
    end
    
    subgraph "Agent Frameworks"
        React["LangGraph ReAct<br>create_react_agent()"]
        CrewAI["CrewAI<br>Agent class"]
        Custom["Custom Agents<br>(Anthropic/OpenAI)"]
    end
    
    subgraph "Storage Layer"
        Store["BaseStore<br>Implementation"]
    end
    
    ManageTool -->|"integrated with"| React
    SearchTool -->|"integrated with"| React
    
    ManageTool -->|"integrated with"| CrewAI
    SearchTool -->|"integrated with"| CrewAI
    
    ManageTool -->|"integrated with"| Custom
    SearchTool -->|"integrated with"| Custom
    
    React -->|"uses"| Store
    CrewAI -->|"uses"| Store
    Custom -->|"uses"| Store
```

Sources: [README.md:36-57](), [docs/docs/guides/use_tools_in_crewai.md:19-49](), [docs/docs/guides/use_tools_in_custom_agent.md:19-137]()

## Storage Configuration

Agents using LangMem tools can use different storage backends:

| Storage Type | Use Case | Persistence |
|--------------|----------|-------------|
| `InMemoryStore` | Development, testing | In-process only (lost on restart) |
| `AsyncPostgresStore` | Production | Persistent across restarts |

The storage configuration is consistent across all agent frameworks, using the index parameter to enable vector search capabilities:

```python
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)
```

Sources: [README.md:40-46](), [docs/docs/guides/use_tools_in_crewai.md:26-32](), [docs/docs/guides/use_tools_in_custom_agent.md:102-107]()

## Example Integration Flow

The following diagram illustrates the typical workflow when using memory tools in an agent system:

```mermaid
flowchart TD
    subgraph "Setup Phase"
        A["Create BaseStore<br>(InMemory or Postgres)"] --> B["Create memory tools<br>with namespace and store"]
        B --> C["Add tools to agent"]
    end
    
    subgraph "Usage Phase"
        D["User message"] --> E["Agent processes message"]
        E --> F{"Need to manage<br>memory?"}
        F -->|"Yes"| G["Call manage_memory tool"]
        F -->|"No"| H{"Need to search<br>memory?"}
        H -->|"Yes"| I["Call search_memory tool"]
        H -->|"No"| J["Generate response"]
        G --> J
        I --> J
        J --> K["Return response to user"]
    end
    
    C --> D
```

Sources: [README.md:68-86](), [docs/docs/guides/use_tools_in_custom_agent.md:42-97]()

## Implementation Differences

While the core concept remains the same, there are some implementation differences when integrating with different agent frameworks:

| Framework | Tool Integration | Message Handling | Store Access |
|-----------|------------------|------------------|--------------|
| LangGraph ReAct | Direct tool list | Handled by framework | Store passed to agent |
| CrewAI | Agent tool parameter | Handled by framework | Store created separately |
| Custom (Anthropic) | Tool conversion required | Manual tool execution | Manual storage management |
| Custom (OpenAI) | Tool schema conversion | Manual tool execution | Manual storage management |

For detailed implementation specifics for each agent framework, refer to the dedicated child pages:
- [ReAct Agents](#4.2.1)
- [CrewAI Integration](#4.2.2)
- [Custom Agents](#4.2.3)

Sources: [docs/docs/guides/use_tools_in_crewai.md:19-49](), [docs/docs/guides/use_tools_in_custom_agent.md:19-265]()

---

# Page: ReAct Agents

# ReAct Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_episodic_memories.md](docs/docs/guides/extract_episodic_memories.md)
- [docs/docs/guides/memory_tools.md](docs/docs/guides/memory_tools.md)
- [docs/docs/guides/use_tools_in_crewai.md](docs/docs/guides/use_tools_in_crewai.md)
- [docs/docs/hot_path_quickstart.md](docs/docs/hot_path_quickstart.md)

</details>



This page documents how to integrate LangMem's memory capabilities with LangGraph's prebuilt ReAct agents. ReAct (Reasoning + Acting) agents use `langgraph.prebuilt.create_react_agent()` and allow LLMs to interleave reasoning steps with concrete actions through tools. For information about other agent integrations, see [CrewAI Integration](#4.2.2) and [Custom Agents](#4.2.3).

## Overview of ReAct Agents with Memory

LangGraph's `create_react_agent()` function creates agents that can be enhanced with LangMem memory tools, providing:
- Long-term memory capabilities through `create_manage_memory_tool()` and `create_search_memory_tool()`
- Persistent storage via LangGraph's `BaseStore` interface
- Automatic memory management during agent execution
- Namespace-based memory organization for multi-user applications

The integration leverages LangGraph's built-in tool calling capabilities, allowing agents to invoke memory tools during their ReAct loops.

Sources: [docs/docs/guides/use_tools_in_custom_agent.md:1-281]()

## Architecture

### ReAct Agent Memory Integration

```mermaid
graph TD
    subgraph "User Interaction"
        User["User"] -->|"Sends message"| ReactAgent
        ReactAgent -->|"Response with memory context"| User
    end
    
    subgraph "LangGraph Components"
        ReactAgent["create_react_agent()"]
        ManageTool["create_manage_memory_tool()"]
        SearchTool["create_search_memory_tool()"]
    end
    
    subgraph "Storage Layer"
        BaseStore["BaseStore interface"]
        InMemoryStore["InMemoryStore"]
        PostgresStore["AsyncPostgresStore"]
        Namespace["Namespace tuple<br/>('memories', user_id)"]
    end
    
    ReactAgent -->|"Tool invocation"| ManageTool
    ReactAgent -->|"Tool invocation"| SearchTool
    ManageTool -->|"store.put()/update()"| BaseStore
    SearchTool -->|"store.search()"| BaseStore
    BaseStore --> InMemoryStore
    BaseStore --> PostgresStore
    BaseStore -->|"Organizes by"| Namespace
```

The `create_react_agent()` function integrates with LangMem through the `create_manage_memory_tool()` and `create_search_memory_tool()` functions. These tools use LangGraph's `BaseStore` interface for persistence, supporting both `InMemoryStore` and `AsyncPostgresStore` implementations.

Sources: [docs/docs/guides/use_tools_in_custom_agent.md:24-111]()

### Memory Flow Process

```mermaid
sequenceDiagram
    participant User as "User"
    participant ReactAgent as "create_react_agent()"
    participant ManageTool as "create_manage_memory_tool()"
    participant SearchTool as "create_search_memory_tool()"
    participant BaseStore as "BaseStore.put()/search()"
    
    User->>ReactAgent: "Remember I prefer dark mode"
    ReactAgent->>ReactAgent: "Decides to store information"
    ReactAgent->>ManageTool: "tool.invoke({'action': 'create', 'content': '...'})"
    ManageTool->>BaseStore: "store.put(namespace, key, value)"
    BaseStore->>ManageTool: "Item stored successfully"
    ManageTool->>ReactAgent: "Memory created: preference stored"
    ReactAgent->>User: "I'll remember your preference for dark mode"
    
    User->>ReactAgent: "What are my preferences?"
    ReactAgent->>ReactAgent: "Recognizes need for memory lookup"
    ReactAgent->>SearchTool: "tool.invoke({'query': 'preferences'})"
    SearchTool->>BaseStore: "store.search(namespace, query='preferences')"
    BaseStore->>SearchTool: "Returns matching Item objects"
    SearchTool->>ReactAgent: "Found: User prefers dark mode"
    ReactAgent->>User: "You prefer dark mode"
```

This sequence shows how `create_react_agent()` uses the `tool.invoke()` method to call memory tools, which then interact with the underlying `BaseStore` using methods like `put()` and `search()`.

Sources: [docs/docs/guides/use_tools_in_custom_agent.md:28-40](), [docs/docs/guides/use_tools_in_custom_agent.md:156-168]()

## Implementation

### Creating a ReAct Agent with Memory

The recommended pattern for creating a ReAct agent with memory capabilities uses a custom `prompt` function for eager memory retrieval:

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langgraph.utils.config import get_store
from langmem import create_manage_memory_tool

def prompt(state):
    """Prepare the messages for the LLM with memory context."""
    # Get store from configured contextvar
    store = get_store()
    memories = store.search(
        ("memories",),
        query=state["messages"][-1].content,
    )
    system_msg = f"""You are a helpful assistant.

## Memories
<memories>
{memories}
</memories>
"""
    return [{"role": "system", "content": system_msg}, *state["messages"]]

# Set up storage with vector indexing
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
) 

# Set up checkpointer for conversation state
checkpointer = MemorySaver()

# Create ReAct agent with memory tools
agent = create_react_agent( 
    "anthropic:claude-3-5-sonnet-latest",
    prompt=prompt,
    tools=[
        create_manage_memory_tool(namespace=("memories",)),
    ],
    store=store,
    checkpointer=checkpointer, 
)
```

| Component | Purpose | Key Parameters |
|-----------|---------|----------------|
| `prompt()` | Eager memory retrieval and context injection | Uses `get_store()` and `store.search()` |
| `create_manage_memory_tool()` | Agent-driven memory management | `namespace` tuple |
| `InMemoryStore` | Vector-indexed memory storage | `index` with embedding config |
| `MemorySaver` | Conversation state persistence | Maintains thread history |
| `create_react_agent()` | LangGraph's prebuilt ReAct agent | `model`, `prompt`, `tools`, `store`, `checkpointer` |

Sources: [docs/docs/hot_path_quickstart.md:35-89]()

### Memory Flow Process

```mermaid
sequenceDiagram
    participant User as "User"
    participant create_react_agent as "create_react_agent()"
    participant prompt_function as "prompt(state)"
    participant get_store as "get_store()"
    participant store_search as "store.search()"
    participant create_manage_memory_tool as "create_manage_memory_tool()"
    participant store_put as "store.put()"
    participant InMemoryStore as "InMemoryStore"
    
    Note over User,InMemoryStore: Memory Storage Flow
    User->>create_react_agent: "dark. Remember that."
    create_react_agent->>create_react_agent: "Agent decides to use manage_memory tool"
    create_react_agent->>create_manage_memory_tool: "tool.invoke() with content"
    create_manage_memory_tool->>store_put: "store.put(('memories',), key, value)"
    store_put->>InMemoryStore: "Store memory item"
    InMemoryStore-->>store_put: "Item stored successfully"
    store_put-->>create_manage_memory_tool: "Storage confirmation"
    create_manage_memory_tool-->>create_react_agent: "Memory saved"
    create_react_agent-->>User: "I'll remember your preference"
    
    Note over User,InMemoryStore: Memory Retrieval Flow
    User->>create_react_agent: "Do you remember me?"
    create_react_agent->>prompt_function: "Process state messages"
    prompt_function->>get_store: "Get configured store"
    get_store->>store_search: "store.search(('memories',), query=...)"
    store_search->>InMemoryStore: "Vector search for memories"
    InMemoryStore-->>store_search: "Return matching items"
    store_search-->>prompt_function: "Retrieved memory items"
    prompt_function-->>create_react_agent: "System message with memories"
    create_react_agent-->>User: "Yes, you prefer dark display mode"
```

This sequence demonstrates the dual-path memory integration: eager retrieval through the `prompt()` function using `get_store()` and `store.search()`, and agent-driven storage through `create_manage_memory_tool()` using `store.put()`.

Sources: [docs/docs/hot_path_quickstart.md:46-63](), [docs/docs/hot_path_quickstart.md:125-166]()

## Advanced Features

### Using the Agent

The ReAct agent usage pattern demonstrates both memory storage and cross-thread retrieval:

```python
# Configure thread for conversation persistence
config = {"configurable": {"thread_id": "thread-a"}}

# Agent stores memory when instructed
response = agent.invoke(
    {"messages": [{"role": "user", "content": "dark. Remember that."}]},
    config=config,
)

# New thread demonstrates cross-conversation memory persistence
new_config = {"configurable": {"thread_id": "thread-b"}}
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Hey there. Do you remember me? What are my preferences?"}]},
    config=new_config,
)
print(response["messages"][-1].content)
# Output: "Based on my memory search, I can see that you've previously indicated a preference for dark display mode..."
```

Key behaviors:

| Aspect | Mechanism | Implementation |
|--------|-----------|----------------|
| **Memory Storage** | Agent-driven tool usage | `create_manage_memory_tool()` invoked by agent |
| **Memory Retrieval** | Eager search in prompt | `store.search()` in `prompt()` function |
| **Thread Isolation** | `MemorySaver` checkpointer | Separate conversation state per thread |
| **Cross-Thread Memory** | Persistent store | Memories accessible across threads |

The agent autonomously decides when to store memories using tools, while memory retrieval happens automatically for every message through the `prompt()` function.

Sources: [docs/docs/hot_path_quickstart.md:128-166]()

### User-Specific Memory with Namespaces

```mermaid
graph TD
    subgraph "Multi-User Memory Architecture"
        create_react_agent["create_react_agent()"]
        prompt_function["prompt(state)"]
        
        create_react_agent --> prompt_function
        create_react_agent --> create_manage_memory_tool["create_manage_memory_tool()<br/>namespace=('memories', '{user_id}')"]
        
        prompt_function --> get_store["get_store()"]
        get_store --> store_search["store.search(('memories', user_id))"]
        create_manage_memory_tool --> store_put["store.put(('memories', user_id))"]
        
        store_search --> InMemoryStore["InMemoryStore"]
        store_put --> InMemoryStore
        
        InMemoryStore --> user_a_ns["Namespace: ('memories', 'user-a')"]
        InMemoryStore --> user_b_ns["Namespace: ('memories', 'user-b')"]
        InMemoryStore --> user_n_ns["Namespace: ('memories', 'user-n')"]
    end
```

LangMem supports templated namespaces that resolve dynamically based on the `configurable` values in the runtime config:

| Organization Pattern | Namespace Template | Use Case |
|---------------------|------------------|-----------|
| By user | `("memories", "{user_id}")` | Separate memories per user |
| By assistant | `("memories", "{assistant_id}")` | Assistant may have memories spanning multiple users |
| By user & organization | `("memories", "{organization_id}", "{user_id}")` | Search across organization while scoping per user |
| Further subdivisions | `("memories", "{user_id}", "manual_memories")` | Organize different types of user data |

Implementation with templated namespaces:

```python
def prompt(state):
    """Prompt function with dynamic namespace resolution."""
    store = get_store()
    # Namespace resolves automatically from config
    memories = store.search(
        ("memories", "{user_id}"),
        query=state["messages"][-1].content,
    )
    # ... rest of prompt logic

agent = create_react_agent( 
    "anthropic:claude-3-5-sonnet-latest",
    prompt=prompt,
    tools=[
        create_manage_memory_tool(namespace=("memories", "{user_id}")),
    ],
    store=store,
    checkpointer=checkpointer,
)

# Usage with different users
response_a = agent.invoke(
    {"messages": [{"role": "user", "content": "Remember my favorite color is blue"}]},
    config={"configurable": {"user_id": "user-a"}}
)

response_b = agent.invoke(
    {"messages": [{"role": "user", "content": "Remember I prefer dark mode"}]},
    config={"configurable": {"user_id": "user-b"}}
)
```

The `{user_id}` template gets resolved at runtime from the `configurable` field, ensuring memory isolation between users while maintaining the same agent code.

Sources: [docs/docs/hot_path_quickstart.md:94-103]()

## Use Cases and Examples

### Prompt Function Memory Integration

The recommended pattern uses a `prompt()` function for eager memory retrieval, automatically including relevant memories in every LLM call:

```python
from langgraph.utils.config import get_store

def prompt(state):
    """Prepare messages with automatic memory context injection."""
    # Get store from LangGraph's managed context
    store = get_store()
    
    # Search for memories relevant to the latest user message
    memories = store.search(
        ("memories",),
        query=state["messages"][-1].content,
    )
    
    # Inject memories into system message
    system_msg = f"""You are a helpful assistant.

## Memories
<memories>
{memories}
</memories>
"""
    return [{"role": "system", "content": system_msg}, *state["messages"]]

# Agent uses prompt function for automatic memory integration
agent = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest",
    prompt=prompt,  # Key: custom prompt function
    tools=[create_manage_memory_tool(namespace=("memories",))],
    store=store,
    checkpointer=checkpointer,
)
```

**Prompt Function Memory Integration Benefits:**

| Aspect | Manual Tool-Based Search | Prompt Function Integration |
|--------|--------------------------|----------------------------|
| **Performance** | Requires agent tool invocation | Direct `store.search()` call |
| **Consistency** | Agent may forget to search | Always includes relevant memories |
| **Token Efficiency** | Tool call overhead | Direct system message inclusion |
| **Context Availability** | Only when agent searches | Every LLM interaction |

The `get_store()` function accesses the LangGraph-managed store via context variables, eliminating the need to pass the store explicitly through function parameters.

Sources: [docs/docs/hot_path_quickstart.md:46-63](), [docs/docs/hot_path_quickstart.md:117-119]()

### Domain-Specific Knowledge Building

ReAct agents can accumulate domain-specific knowledge through memory tools:

| Use Case | Memory Tool Usage | Example Storage |
|----------|------------------|-----------------|
| **Personal Training** | `create_manage_memory_tool()` stores goals | `{"content": "User training for half marathon in May 2024"}` |
| **Product Support** | `create_search_memory_tool()` finds past issues | `{"content": "User had WiFi connection issues with device model X"}` |
| **Customer Service** | Both tools for preferences and history | `{"content": "User prefers email contact, not phone"}` |
| **Educational Tools** | Memory of learning patterns | `{"content": "User needs detailed math explanations"}` |

Example implementation for a support agent:

```python
# Support agent with domain-specific memory
support_agent = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest",
    tools=[
        create_manage_memory_tool(namespace=("support", "{user_id}"), store=store),
        create_search_memory_tool(namespace=("support", "{user_id}"), store=store),
    ],
    store=store,
)

# Usage tracks support history automatically
response = support_agent.invoke(
    {"messages": [{"role": "user", "content": "I'm having the same WiFi issue again"}]},
    config={"configurable": {"user_id": "customer-123"}}
)
```

The agent will automatically search for previous WiFi-related issues and store new information about the current problem.

Sources: [docs/docs/guides/use_tools_in_custom_agent.md:108-111]()

## Best Practices

### Cross-Thread Memory Persistence

ReAct agents demonstrate memory persistence across different conversation threads:

```python
# Initial conversation thread
config_a = {"configurable": {"thread_id": "thread-a"}}
agent.invoke({
    "messages": [{"role": "user", "content": "Know which display mode I prefer?"}]
}, config=config_a)
# Output: "I don't seem to have any stored memories about your display mode preferences..."

agent.invoke({
    "messages": [{"role": "user", "content": "dark. Remember that."}]
}, config=config_a)
# Agent uses create_manage_memory_tool() to store preference

# New conversation thread - demonstrates cross-thread memory
config_b = {"configurable": {"thread_id": "thread-b"}}
response = agent.invoke({
    "messages": [{"role": "user", "content": "Hey there. Do you remember me? What are my preferences?"}]
}, config=config_b)

print(response["messages"][-1].content)
# Output: "Based on my memory search, I can see that you've previously indicated a preference for dark display mode..."
```

Key characteristics:

| Memory Aspect | Implementation | Behavior |
|---------------|----------------|----------|
| **Storage** | `create_manage_memory_tool()` | Agent-driven, explicit memory creation |
| **Retrieval** | `prompt()` function with `store.search()` | Automatic, every message processed |
| **Thread Isolation** | `MemorySaver` checkpointer | Separate conversation state per thread |
| **Cross-Thread Persistence** | `InMemoryStore` namespace | Memories accessible across all threads |

This demonstrates that while conversation state (checkpointer) is isolated per thread, memories (store) persist across all conversations.

Sources: [docs/docs/hot_path_quickstart.md:128-166]()

### Namespace Design Patterns

| Pattern | Namespace Example | Purpose |
|---------|------------------|---------|
| **User-scoped** | `("memories", "{user_id}")` | Individual user memories |
| **Team-scoped** | `("team", "{team_id}")` | Shared team knowledge |
| **Global** | `("global",)` | Application-wide knowledge |
| **Domain-specific** | `("support", "{user_id}")` | Domain-specific memories |

### Performance Optimization

- **Eager retrieval**: Use custom prompt functions for frequently accessed memories
- **Namespace design**: Structure namespaces to minimize search scope
- **Vector indexing**: Configure appropriate embedding dimensions for your use case

Sources: [docs/docs/guides/use_tools_in_custom_agent.md:102-107](), [docs/docs/guides/use_tools_in_custom_agent.md:226-231]()

## Related Components

- [Memory Tools](#5): Detailed documentation on memory management tools
- [Memory Creation and Management](#5.1): How to create, update, and delete memories
- [Memory Search and Retrieval](#5.2): How to search for and retrieve memories
- [Using Namespaces](#5.3): How to organize memories with namespaces
- [Storage Types](#7.1): Different storage backends supported by LangMem

---

# Page: CrewAI Integration

# CrewAI Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_episodic_memories.md](docs/docs/guides/extract_episodic_memories.md)
- [docs/docs/guides/memory_tools.md](docs/docs/guides/memory_tools.md)
- [docs/docs/guides/use_tools_in_crewai.md](docs/docs/guides/use_tools_in_crewai.md)

</details>



This document covers how to integrate LangMem memory tools with CrewAI multi-agent systems to enable persistent knowledge sharing across agents. CrewAI agents use LangMem's memory tools to store, update, and search memories in shared knowledge bases.

For LangGraph-native agent integration, see [LangGraph Integration](#4.1). For building custom agents with memory tools, see [Custom Agents](#4.2.3).

## Architecture Overview

CrewAI integration follows a tool-based pattern where LangMem provides memory management capabilities as tools that CrewAI agents can use during task execution.

### CrewAI-LangMem Integration Architecture

```mermaid
graph TB
    subgraph "CrewAI Layer"
        Crew["Crew"]
        AgentA["Agent (role='Knowledge Learner')"]
        AgentB["Agent (role='Knowledge Teacher')"] 
        TaskA["Task (learn_task)"]
        TaskB["Task (teach_task)"]
    end
    
    subgraph "LangMem Tools Layer"
        MMT["create_manage_memory_tool"]
        SMT["create_search_memory_tool"]
    end
    
    subgraph "Storage Layer"
        IMS["InMemoryStore"]
        PGS["AsyncPostgresStore"]
        NS[("namespace=('memories')")]
    end
    
    subgraph "LLM Layer"
        LLM["function_calling_llm='gpt-4o-mini'"]
    end
    
    Crew --> AgentA
    Crew --> AgentB
    Crew --> TaskA
    Crew --> TaskB
    
    AgentA --> MMT
    AgentA --> SMT
    AgentB --> MMT
    AgentB --> SMT
    
    MMT --> IMS
    MMT --> PGS
    SMT --> IMS
    SMT --> PGS
    
    MMT --> NS
    SMT --> NS
    
    AgentA --> LLM
    AgentB --> LLM
    
    TaskA --> AgentA
    TaskB --> AgentB
```

Sources: [docs/docs/guides/use_tools_in_crewai.md:22-92]()

## Basic Configuration

CrewAI agents receive memory tools through their `tools` parameter. Both `create_manage_memory_tool` and `create_search_memory_tool` require explicit store configuration when used outside LangGraph.

### Core Components Setup

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| `InMemoryStore` | Development storage | `index={"dims": 1536, "embed": "openai:text-embedding-3-small"}` |
| `create_manage_memory_tool` | Memory CRUD operations | `namespace="memories", store=store` |
| `create_search_memory_tool` | Memory retrieval | `namespace="memories", store=store` |
| `Agent.tools` | Tool assignment | `tools=[memory_tools]` |

```python
# Basic tool configuration
memory_tools = [
    create_manage_memory_tool(namespace="memories", store=store),
    create_search_memory_tool(namespace="memories", store=store),
]

# Agent configuration  
knowledge_agent = Agent(
    role='Knowledge Manager',
    goal='Build and maintain a knowledge base',
    tools=memory_tools,
    verbose=True
)
```

Sources: [docs/docs/guides/use_tools_in_crewai.md:34-48]()

## Multi-Agent Knowledge Sharing

CrewAI's shared execution context enables multiple agents to access the same memory store, creating collaborative knowledge management workflows.

### Multi-Agent Memory Sharing Flow

```mermaid
sequenceDiagram
    participant Crew
    participant LearnerAgent["Agent(role='Knowledge Learner')"]
    participant TeacherAgent["Agent(role='Knowledge Teacher')"]  
    participant MMT["create_manage_memory_tool"]
    participant SMT["create_search_memory_tool"]
    participant Store["InMemoryStore/AsyncPostgresStore"]
    
    Note over Crew,Store: Learning Phase
    Crew->>LearnerAgent: execute learn_task
    LearnerAgent->>MMT: store knowledge
    MMT->>Store: write to namespace=("memories")
    Store-->>MMT: confirm storage
    MMT-->>LearnerAgent: storage complete
    LearnerAgent-->>Crew: task complete
    
    Note over Crew,Store: Teaching Phase  
    Crew->>TeacherAgent: execute teach_task
    TeacherAgent->>SMT: search for knowledge
    SMT->>Store: query namespace=("memories")
    Store-->>SMT: return matching items
    SMT-->>TeacherAgent: knowledge retrieved
    TeacherAgent-->>Crew: response with stored knowledge
```

Sources: [docs/docs/guides/use_tools_in_crewai.md:77-112]()

## Memory Organization Patterns

CrewAI integration supports multiple namespace organization patterns for different collaboration scenarios.

### Namespace Configuration Options

| Pattern | Namespace | Use Case |
|---------|-----------|----------|
| Shared Knowledge | `"memories"` | Team-wide knowledge base |
| Agent-Specific | `("memories", "agent_id")` | Individual agent memories |
| Project-Scoped | `("memories", "project_x")` | Project-specific knowledge |
| Role-Based | `("memories", "role_name")` | Role-specific expertise |

### Team Knowledge Base Example

```python
# Shared namespace for team collaboration
base_tools = [
    create_manage_memory_tool(namespace="memories", store=store),
    create_search_memory_tool(namespace="memories", store=store),
]

# Multiple agents sharing same knowledge base
learner = Agent(
    role="Knowledge Learner", 
    tools=base_tools,
    function_calling_llm="gpt-4o-mini",
)

teacher = Agent(
    role="Knowledge Teacher",
    tools=base_tools, 
    function_calling_llm="gpt-4o-mini", 
)
```

Sources: [docs/docs/guides/use_tools_in_crewai.md:71-92]()

## Implementation Details

### Store Configuration Requirements

CrewAI integration requires explicit store configuration since CrewAI agents operate outside LangGraph's automatic store management.

```python
# Required store configuration
store = InMemoryStore(
    index={
        "dims": 1536,  # OpenAI text-embedding-3-small dimensions
        "embed": "openai:text-embedding-3-small",
    }
)

# Tools require explicit store parameter
create_manage_memory_tool(namespace="memories", store=store)
create_search_memory_tool(namespace="memories", store=store)
```

### Task Execution Integration

CrewAI tasks trigger memory operations through agent tool usage during task execution.

```python
# Task definitions that utilize memory tools
learn_task = Task(
    description="Save some of your favorite Demon Slayer quotes in memory.",
    agent=learner,
    expected_output="Response:",
)

teach_task = Task(
    description="Search your memories for information about your teammates.", 
    agent=teacher,
    expected_output="Response:",
)

# Sequential task execution
crew = Crew(agents=[learner, teacher], tasks=[learn_task])
result = crew.kickoff()

crew = Crew(agents=[learner, teacher], tasks=[teach_task]) 
result = crew.kickoff()
```

Sources: [docs/docs/guides/use_tools_in_crewai.md:95-112]()

## Production Considerations

### Storage Backend Selection

| Environment | Store Type | Configuration |
|-------------|------------|---------------|
| Development | `InMemoryStore` | No persistence, fast startup |
| Production | `AsyncPostgresStore` | Persistent, scalable, concurrent |
| Testing | `InMemoryStore` | Isolated test environments |

### Memory Item Structure

CrewAI agents store memories as `Item` objects with standardized structure:

```python
# Example stored memory structure
Item(
    namespace=["memories"],
    key="bd61f87e-d591-45b7-b950-3f9318604ea3", 
    value={
        "content": '"The bond between Nezuko and I can never be severed..." - Tanjiro'
    },
    created_at="2025-02-07T22:24:37.736962+00:00",
    updated_at="2025-02-07T22:24:37.736969+00:00",
    score=None,
)
```

### Function Calling LLM Requirements

CrewAI memory tools require function calling capabilities:

```python
# Supported function calling models
Agent(
    function_calling_llm="gpt-4o-mini",  # OpenAI
    function_calling_llm="anthropic:claude-3-5-sonnet-latest",  # Anthropic
)
```

Sources: [docs/docs/guides/use_tools_in_crewai.md:27-32](), [docs/docs/guides/use_tools_in_crewai.md:83-91](), [docs/docs/guides/use_tools_in_crewai.md:114-127]()

---

# Page: Custom Agents

# Custom Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/use_tools_in_custom_agent.md](docs/docs/guides/use_tools_in_custom_agent.md)
- [src/langmem/knowledge/tools.py](src/langmem/knowledge/tools.py)

</details>



This document covers building custom agents that integrate LangMem's memory tools for persistent knowledge across conversations. Custom agents give you full control over the agent implementation while leveraging LangMem's memory management capabilities.

For prebuilt agent solutions using LangGraph's `create_react_agent`, see [ReAct Agents](#4.2.1). For multi-agent system integration, see [CrewAI Integration](#4.2.2).

## Core Integration Pattern

Custom agents with LangMem follow a standard pattern where agents use memory tools during their reasoning loops to store and retrieve persistent information. The integration centers around two key tools from [src/langmem/knowledge/tools.py:25-356]():

- `create_manage_memory_tool` - Creates, updates, and deletes memories
- `create_search_memory_tool` - Searches through stored memories

```mermaid
graph TB
    subgraph "Custom Agent Architecture"
        Agent["Custom Agent Implementation"]
        LLM["Language Model<br/>(OpenAI, Anthropic, etc)"]
        Loop["REACT Loop<br/>(Reason-Act-Observe)"]
        Tools["Tool Registry"]
    end
    
    subgraph "LangMem Memory Tools"
        MMT["create_manage_memory_tool"]
        SMT["create_search_memory_tool"]
    end
    
    subgraph "Storage Layer"
        Store["BaseStore<br/>(InMemoryStore, PostgresStore)"]
        NS["Namespace Organization"]
    end
    
    subgraph "External LLM APIs"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Other["Other Providers"]
    end
    
    Agent --> Loop
    Loop --> LLM
    Loop --> Tools
    Tools --> MMT
    Tools --> SMT
    MMT --> Store
    SMT --> Store
    Store --> NS
    LLM --> OpenAI
    LLM --> Anthropic
    LLM --> Other
    
    Agent -.->|"Tool Results"| Loop
    Loop -.->|"Memory Context"| LLM
```

**Sources:** [src/langmem/knowledge/tools.py:25-486](), [docs/docs/guides/use_tools_in_custom_agent.md:1-282]()

## Tool Integration

### Memory Management Tool

The `create_manage_memory_tool` function creates a tool that allows agents to perform CRUD operations on memories. The tool signature includes:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `content` | `schema` (default: `str`) | Memory content to store |
| `action` | `Literal["create", "update", "delete"]` | Operation type |
| `id` | `UUID` | Memory identifier for update/delete |

The tool is configured with a namespace pattern and optional action restrictions via `actions_permitted` parameter from [src/langmem/knowledge/tools.py:34-36]().

### Memory Search Tool

The `create_search_memory_tool` function creates a tool for semantic and exact memory search with these parameters:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `query` | `str` | Search query text |
| `limit` | `int` | Maximum results (default: 10) |
| `offset` | `int` | Result offset (default: 0) |
| `filter` | `dict` | Additional filter criteria |

**Sources:** [src/langmem/knowledge/tools.py:362-486]()

## Implementation Patterns

### REACT Loop Implementation

Custom agents typically implement a REACT (Reason-Act-Observe) loop that integrates memory tools. The pattern involves:

```mermaid
sequenceDiagram
    participant U as User
    participant A as Custom Agent
    participant L as LLM Provider
    participant T as Memory Tools
    participant S as BaseStore
    
    U->>A: "User input"
    
    loop "REACT Loop (max_steps)"
        A->>L: "Messages + Available Tools"
        L-->>A: "Response with tool calls"
        
        alt "Tool calls present"
            loop "For each tool call"
                A->>T: "Execute tool (manage_memory/search_memory)"
                T->>S: "Store operation or search"
                S-->>T: "Result/memories"
                T-->>A: "Tool result"
            end
            A->>A: "Add tool results to message history"
        else "No tool calls"
            A-->>U: "Final response"
        end
    end
```

**Sources:** [docs/docs/guides/use_tools_in_custom_agent.md:43-98](), [docs/docs/guides/use_tools_in_custom_agent.md:171-222]()

### Tool Execution Function

Custom agents require a tool execution handler that maps tool calls to actual tool invocations. The pattern from [docs/docs/guides/use_tools_in_custom_agent.md:28-40]() shows:

```python
def execute_tool(tools_by_name: Dict[str, Any], tool_call: Dict[str, Any]) -> str:
    tool_name = tool_call.name  # or tool_call["function"]["name"] for OpenAI
    tool = tools_by_name[tool_name]
    result = tool.invoke(tool_call.input)  # or tool_call["function"]["arguments"]
    return str(result)
```

### Store Configuration

Custom agents must configure a `BaseStore` instance and pass it to the memory tools. The typical setup involves:

```python
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)
memory_tools = [
    create_manage_memory_tool(namespace="memories", store=store),
    create_search_memory_tool(namespace="memories", store=store),
]
```

**Sources:** [docs/docs/guides/use_tools_in_custom_agent.md:102-111]()

## Provider-Specific Implementations

### Anthropic Integration

Anthropic's Claude models use a specific tool calling format where tools are converted to their schema format:

```mermaid
graph LR
    subgraph "Anthropic Tool Flow"
        LT["LangChain Tool"]
        AS["Anthropic Schema"]
        TC["Tool Call Response"]
        TR["Tool Result"]
    end
    
    LT -->|"tool.tool_call_schema.model_json_schema()"| AS
    AS -->|"messages.create(tools=anthropic_tools)"| TC
    TC -->|"execute_tool(tools_by_name, tool_call)"| TR
```

The schema conversion uses `tool.tool_call_schema.model_json_schema()` from [docs/docs/guides/use_tools_in_custom_agent.md:54]().

### OpenAI Integration

OpenAI's format requires wrapping tools in a function specification:

```python
openai_tools = [
    {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.tool_call_schema.model_json_schema(),
        },
    }
    for tool in tools
]
```

**Sources:** [docs/docs/guides/use_tools_in_custom_agent.md:178-188]()

## Namespace and Store Management

### Namespace Configuration

Custom agents must handle namespace configuration for memory organization. The tools use `NamespaceTemplate` from [src/langmem/knowledge/tools.py:263]() to support dynamic namespacing:

```python
# Simple namespace
create_manage_memory_tool(namespace="memories", store=store)

# Dynamic namespace (requires config context)
create_manage_memory_tool(namespace=("memories", "{user_id}"), store=store)
```

### Store Retrieval

When not providing an explicit store parameter, tools use `get_store()` from [src/langmem/knowledge/tools.py:494]() to retrieve the store from LangGraph context. Custom agents typically provide the store explicitly via the `store` parameter.

**Sources:** [src/langmem/knowledge/tools.py:489-497]()

## Error Handling

Custom agents should handle several error scenarios:

| Error Type | Source | Handling |
|------------|--------|----------|
| Tool not found | Agent implementation | Return error message |
| Invalid tool arguments | Memory tools | Catch `ValueError` exceptions |
| Store configuration | `_get_store()` function | Handle `ConfigurationError` |
| Action restrictions | `actions_permitted` validation | Validate before execution |

The tools include built-in validation for actions like preventing ID specification during creation from [src/langmem/knowledge/tools.py:283-286]().

**Sources:** [src/langmem/knowledge/tools.py:278-291](), [src/langmem/knowledge/tools.py:489-497]()

---

# Page: Memory Tools

# Memory Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_episodic_memories.md](docs/docs/guides/extract_episodic_memories.md)
- [docs/docs/guides/memory_tools.md](docs/docs/guides/memory_tools.md)
- [docs/docs/guides/use_tools_in_crewai.md](docs/docs/guides/use_tools_in_crewai.md)
- [src/langmem/knowledge/tools.py](src/langmem/knowledge/tools.py)

</details>



This document covers LangMem's memory tools that enable agents to actively manage their own persistent memory. These tools provide a "hot path" approach where agents make deliberate decisions about what to remember during conversations, as opposed to background memory processing approaches.

For background memory processing using reflection and consolidation, see [Background Memory Processing](#3.2). For core memory management concepts, see [Memory Management](#2).

## Overview

LangMem provides two primary tools that agents can use to manage persistent memories stored in LangGraph's BaseStore system:

| Tool | Function | Purpose |
|------|----------|---------|
| Memory Management | `create_manage_memory_tool` | Create, update, and delete memories |
| Memory Search | `create_search_memory_tool` | Search and retrieve existing memories |

These tools integrate directly with LangGraph's agent framework and storage layer, enabling agents to proactively store information they deem important and retrieve relevant context when needed.

**Tool Architecture Diagram**

```mermaid
graph TB
    subgraph "Agent Layer"
        A[Agent] --> MT["manage_memory tool"]
        A --> ST["search_memory tool"]
    end
    
    subgraph "LangMem Tools Layer"
        MT --> CMT["create_manage_memory_tool()"]
        ST --> CST["create_search_memory_tool()"]
    end
    
    subgraph "LangGraph Integration"
        CMT --> NT["NamespaceTemplate"]
        CST --> NT
        CMT --> GS["get_store()"]
        CST --> GS
    end
    
    subgraph "Storage Layer"
        GS --> BS["BaseStore"]
        BS --> IMS["InMemoryStore"]
        BS --> PGS["AsyncPostgresStore"]
    end
    
    subgraph "Tool Operations"
        CMT --> CR["create"]
        CMT --> UP["update"] 
        CMT --> DEL["delete"]
        CST --> SE["search"]
    end
```

Sources: [src/langmem/knowledge/tools.py:25-356](), [src/langmem/knowledge/tools.py:362-486]()

## Memory Management Tool

The `create_manage_memory_tool` function creates a tool that allows agents to create, update, and delete memories. The tool operates on structured memory objects stored in configurable namespaces within LangGraph's BaseStore.

### Function Signature and Parameters

The tool factory function accepts several configuration parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `namespace` | `tuple[str, ...]` or `str` | Required | Namespace structure with runtime placeholders |
| `instructions` | `str` | Predefined guidelines | Custom instructions for tool usage |
| `schema` | `Type` | `str` | Expected content schema for memories |
| `actions_permitted` | `tuple` | `("create", "update", "delete")` | Allowed operations |
| `store` | `BaseStore` | `None` | Explicit store (uses runtime store if None) |
| `name` | `str` | `"manage_memory"` | Tool name |

**Generated Tool Interface**

```mermaid
graph LR
    subgraph "Tool Input Schema"
        CI["content: schema"]
        AI["action: Literal[actions_permitted]"]
        II["id: UUID | None"]
    end
    
    subgraph "Tool Logic Flow"
        CI --> VL["Validation Logic"]
        AI --> VL
        II --> VL
        VL --> NS["Namespace Resolution"]
        NS --> SO["Store Operations"]
    end
    
    subgraph "Store Operations"
        SO --> SC["store.aput() / store.put()"]
        SO --> SD["store.adelete() / store.delete()"]
    end
    
    subgraph "Output"
        SC --> OR["'{action}d memory {id}'"]
        SD --> OR
    end
```

Sources: [src/langmem/knowledge/tools.py:64-69](), [src/langmem/knowledge/tools.py:271-337]()

### Validation and Error Handling

The tool implements several validation rules:

- **Create operations**: Cannot specify an ID (auto-generated via `uuid.uuid4()`)
- **Update/Delete operations**: Must specify an existing memory ID
- **Action validation**: Only permitted actions are allowed
- **Store availability**: Validates BaseStore access via `_get_store()`

The validation logic is implemented in both sync and async versions of the tool function:

Sources: [src/langmem/knowledge/tools.py:283-291](), [src/langmem/knowledge/tools.py:317-325]()

### Content Serialization

Memory content is serialized through the `_ensure_json_serializable` function, which handles:

- Primitive types (str, int, float, bool, dict, list)
- Pydantic models via `model_dump(mode="json")`
- Fallback to string representation for other types

Sources: [src/langmem/knowledge/tools.py:500-510]()

## Memory Search Tool

The `create_search_memory_tool` function creates a tool for semantic and exact search of stored memories. It leverages the BaseStore's vector search capabilities when configured with embeddings.

### Search Parameters and Response Formats

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | Search query text |
| `limit` | `int` | 10 | Maximum results to return |
| `offset` | `int` | 0 | Results to skip (pagination) |
| `filter` | `dict` | `None` | Additional filter criteria |

The `response_format` parameter controls output structure:
- `"content"`: Returns serialized memory data only
- `"content_and_artifact"`: Returns both serialized data and raw memory objects

**Search Tool Data Flow**

```mermaid
sequenceDiagram
    participant A as "Agent"
    participant ST as "search_memory tool"
    participant NT as "NamespaceTemplate"
    participant BS as "BaseStore"
    participant VS as "Vector Store"
    
    A->>ST: "search_memory(query, limit, offset, filter)"
    ST->>NT: "namespacer()"
    NT-->>ST: "resolved namespace"
    ST->>BS: "store.asearch(namespace, query, ...)"
    BS->>VS: "vector similarity search"
    VS-->>BS: "ranked results"
    BS-->>ST: "memory items"
    ST->>ST: "utils.dumps(memory.dict())"
    ST-->>A: "serialized memories"
```

Sources: [src/langmem/knowledge/tools.py:436-454](), [src/langmem/knowledge/tools.py:456-474]()

## Namespace Configuration

Both tools use the `NamespaceTemplate` class for dynamic namespace resolution. This enables runtime configuration of memory organization patterns.

### Namespace Template System

The namespace system supports hierarchical organization with runtime variable substitution:

```mermaid
graph TD
    subgraph "Namespace Template Examples"
        NT1["('memories', '{user_id}')"]
        NT2["('team', '{team_id}', 'agent_{agent_id}')"]
        NT3["('project', '{project_id}', 'memories')"]
    end
    
    subgraph "Runtime Resolution"
        RC["Runtime Config"]
        RC --> RV1["user_id: 'user-123'"]
        RC --> RV2["team_id: 'team-a'"]
        RC --> RV3["agent_id: 'agent-1'"]
    end
    
    subgraph "Resolved Namespaces"
        RN1["('memories', 'user-123')"]
        RN2["('team', 'team-a', 'agent_agent-1')"]
        RN3["('project', 'proj-x', 'memories')"]
    end
    
    NT1 --> RN1
    NT2 --> RN2
    NT3 --> RN3
```

Sources: [src/langmem/knowledge/tools.py:263](), [src/langmem/knowledge/tools.py:292](), [src/langmem/knowledge/tools.py:326](), [src/langmem/knowledge/tools.py:433](), [src/langmem/knowledge/tools.py:444]()

### Common Namespace Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| User-specific | Personal memories | `("memories", "{user_id}")` |
| Team-shared | Collaborative knowledge | `("team", "{team_id}")` |
| Agent-specific | Individual agent state | `("agents", "{agent_id}", "memories")` |
| Project-scoped | Project-specific context | `("projects", "{project_id}", "memories")` |

For detailed namespace organization strategies, see [Using Namespaces](#5.3).

## Integration Patterns

### LangGraph Agent Integration

The tools integrate seamlessly with LangGraph's `create_react_agent`:

**ReAct Agent Integration Architecture**

```mermaid
graph TB
    subgraph "create_react_agent"
        RA["ReAct Agent"] --> TL["Tool Loop"]
        RA --> PM["Prompt Management"]
    end
    
    subgraph "Memory Tools"
        MMT["create_manage_memory_tool"]
        SMT["create_search_memory_tool"]
    end
    
    subgraph "LangGraph Infrastructure" 
        TL --> MMT
        TL --> SMT
        MMT --> GS["get_store()"]
        SMT --> GS
        GS --> BS["BaseStore"]
        PM --> CFG["get_config()"]
    end
    
    subgraph "Runtime Context"
        CFG --> UC["User Config"]
        UC --> NS["Namespace Resolution"]
        NS --> BS
    end
```

Sources: [docs/docs/guides/memory_tools.md:32-40](), [docs/docs/guides/memory_tools.md:142-175]()

### Custom Agent Integration

For agents built outside LangGraph's prebuilt patterns, the tools can be used directly by providing an explicit `store` parameter:

Sources: [src/langmem/knowledge/tools.py:37](), [src/langmem/knowledge/tools.py:366]()

### CrewAI Integration

The tools integrate with CrewAI by providing the `store` parameter explicitly, since CrewAI doesn't use LangGraph's configuration system:

Sources: [docs/docs/guides/use_tools_in_crewai.md:35-38]()

## Tool Configuration Options

### Schema Customization

Tools support custom Pydantic schemas for structured memory content:

Sources: [src/langmem/knowledge/tools.py:33](), [src/langmem/knowledge/tools.py:178-198]()

### Action Restrictions

The `actions_permitted` parameter allows limiting available operations:

| Configuration | Actions Available | Use Case |
|---------------|-------------------|----------|
| `("create", "update", "delete")` | All operations | Full memory management |
| `("create", "update")` | Creation and updates only | Append-only patterns |
| `("update",)` | Updates only | Profile management |

Sources: [src/langmem/knowledge/tools.py:34-36](), [src/langmem/knowledge/tools.py:264-268]()

### Custom Instructions

The `instructions` parameter customizes when and how agents should use the tools:

Sources: [src/langmem/knowledge/tools.py:28-32](), [src/langmem/knowledge/tools.py:350-352]()

## Tool Implementation Details

### Store Resolution

Both tools use the `_get_store` helper function to resolve the BaseStore instance:

1. Use explicit `store` parameter if provided
2. Fall back to `get_store()` from LangGraph runtime
3. Raise `ConfigurationError` if no store available

Sources: [src/langmem/knowledge/tools.py:489-497]()

### Error Handling

The tools implement comprehensive error handling for common failure modes:

- Missing store configuration
- Invalid action types
- Missing required parameters
- Serialization failures

Sources: [src/langmem/knowledge/tools.py:278-291](), [src/langmem/knowledge/tools.py:312-325]()

### Tool Schema Enhancement

The `_ToolWithRequired` class ensures proper OpenAI function calling schema generation by adding required field information:

Sources: [src/langmem/knowledge/tools.py:513-531]()

---

# Page: Memory Creation and Management

# Memory Creation and Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_episodic_memories.md](docs/docs/guides/extract_episodic_memories.md)
- [docs/docs/guides/memory_tools.md](docs/docs/guides/memory_tools.md)
- [docs/docs/guides/use_tools_in_crewai.md](docs/docs/guides/use_tools_in_crewai.md)
- [src/langmem/knowledge/tools.py](src/langmem/knowledge/tools.py)

</details>



This page covers the `create_manage_memory_tool` function, which creates tools that agents can use to create, update, and delete persistent memories. This function is the primary interface for agent-driven memory management in hot path scenarios.

For information about searching existing memories, see [Memory Search and Retrieval](#5.2). For background memory processing without agent tools, see [Background Memory Processing](#3.2).

## Tool Creation Overview

The `create_manage_memory_tool` function creates a `StructuredTool` that agents can use to manage persistent memories stored in a LangGraph `BaseStore`. The tool supports three primary operations: create, update, and delete memories.

```mermaid
graph TB
    subgraph "Tool Creation Flow"
        CMT["create_manage_memory_tool()"]
        NT["NamespaceTemplate"]
        ASM["amanage_memory()"]
        SM["manage_memory()"]
        TWR["_ToolWithRequired"]
    end
    
    subgraph "Configuration Parameters"
        NS["namespace: tuple[str, ...] | str"]
        AP["actions_permitted: tuple[Literal, ...]"]
        SCHEMA["schema: Type"]
        STORE["store: BaseStore | None"]
    end
    
    subgraph "Runtime Components"
        BS["BaseStore"]
        UUID["uuid.uuid4()"]
        SER["_ensure_json_serializable()"]
    end
    
    CMT --> NT
    CMT --> ASM
    CMT --> SM
    CMT --> TWR
    
    NS --> CMT
    AP --> CMT
    SCHEMA --> CMT
    STORE --> CMT
    
    ASM --> BS
    SM --> BS
    ASM --> UUID
    SM --> UUID
    ASM --> SER
    SM --> SER
```

Sources: [src/langmem/knowledge/tools.py:25-357]()

## Function Signature and Parameters

The `create_manage_memory_tool` function accepts several key parameters for configuration:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `namespace` | `tuple[str, ...] \| str` | Required | Namespace structure for organizing memories |
| `instructions` | `str` | Predefined guidelines | Custom instructions for tool usage |
| `schema` | `Type` | `str` | Type hint for memory content validation |
| `actions_permitted` | `tuple[Literal, ...] \| None` | `("create", "update", "delete")` | Allowed operations |
| `store` | `BaseStore \| None` | `None` | BaseStore instance (uses runtime store if None) |
| `name` | `str` | `"manage_memory"` | Tool name identifier |

Sources: [src/langmem/knowledge/tools.py:25-39]()

## Memory Operations

The generated tool supports three primary memory operations through the `action` parameter:

```mermaid
flowchart TD
    subgraph "Memory Operations Flow"
        INPUT["Tool Input: content, action, id"]
        
        subgraph "Action Validation"
            AV["actions_permitted check"]
            CREATE_CHECK["action == 'create' and id is not None"]
            UPDATE_DELETE_CHECK["action in ('delete', 'update') and not id"]
        end
        
        subgraph "Operation Execution"
            CREATE["CREATE: Generate UUID, store content"]
            UPDATE["UPDATE: Update existing memory by ID"]
            DELETE["DELETE: Remove memory by ID"]
        end
        
        OUTPUT["Return: '{action}d memory {id}'"]
    end
    
    INPUT --> AV
    AV --> CREATE_CHECK
    AV --> UPDATE_DELETE_CHECK
    
    CREATE_CHECK -->|"Valid"| CREATE
    UPDATE_DELETE_CHECK -->|"Valid"| UPDATE
    UPDATE_DELETE_CHECK -->|"Valid"| DELETE
    
    CREATE --> OUTPUT
    UPDATE --> OUTPUT
    DELETE --> OUTPUT
```

### Create Operation

Creates a new memory with auto-generated UUID:

- Validates that no `id` is provided [src/langmem/knowledge/tools.py:283-286]()
- Generates new UUID using `uuid.uuid4()` [src/langmem/knowledge/tools.py:297]()
- Serializes content using `_ensure_json_serializable` [src/langmem/knowledge/tools.py:301]()
- Stores in BaseStore using `aput`/`put` [src/langmem/knowledge/tools.py:298-302]()

### Update Operation

Updates existing memory content:

- Requires valid `id` parameter [src/langmem/knowledge/tools.py:288-291]()
- Uses same storage mechanism as create [src/langmem/knowledge/tools.py:298-302]()
- Overwrites existing content at the specified key

### Delete Operation

Removes memory from storage:

- Requires valid `id` parameter [src/langmem/knowledge/tools.py:288-291]()
- Uses `adelete`/`delete` methods [src/langmem/knowledge/tools.py:294-295]()
- Returns confirmation message [src/langmem/knowledge/tools.py:295]()

Sources: [src/langmem/knowledge/tools.py:271-337]()

## Namespace Management

The tool uses `NamespaceTemplate` for dynamic namespace resolution:

```mermaid
graph LR
    subgraph "Namespace Resolution"
        CONFIG["LangGraph Config"]
        TEMPLATE["NamespaceTemplate(namespace)"]
        RESOLVED["Resolved Namespace"]
        BASESTORE["BaseStore Operations"]
    end
    
    subgraph "Template Patterns"
        STATIC["('memories', 'team_a')"]
        DYNAMIC["('memories', '{langgraph_user_id}')"]
        NESTED["('memories', '{user_id}', 'preferences')"]
    end
    
    CONFIG --> TEMPLATE
    TEMPLATE --> RESOLVED
    RESOLVED --> BASESTORE
    
    STATIC --> TEMPLATE
    DYNAMIC --> TEMPLATE
    NESTED --> TEMPLATE
```

The namespace template supports runtime variable substitution using LangGraph's configuration system. Common patterns include:

- **Static namespaces**: `("memories", "global")`
- **User-scoped**: `("memories", "{langgraph_user_id}")`
- **Team-scoped**: `("memories", "{team_id}", "shared")`
- **Multi-level**: `("memories", "{user_id}", "preferences")`

Sources: [src/langmem/knowledge/tools.py:263](), [src/langmem/knowledge/tools.py:292](), [src/langmem/knowledge/tools.py:326]()

## Content Serialization

The `_ensure_json_serializable` function handles content serialization:

```mermaid
flowchart TD
    INPUT["Input Content"]
    
    subgraph "Serialization Logic"
        PRIMITIVE["Primitive Types Check"]
        PYDANTIC["Pydantic Model Check"]
        FALLBACK["String Fallback"]
    end
    
    OUTPUT["JSON-Serializable Content"]
    
    INPUT --> PRIMITIVE
    PRIMITIVE -->|"str, int, float, bool, dict, list"| OUTPUT
    PRIMITIVE -->|"Other"| PYDANTIC
    PYDANTIC -->|"hasattr(content, 'model_dump')"| OUTPUT
    PYDANTIC -->|"Exception or No model_dump"| FALLBACK
    FALLBACK --> OUTPUT
```

The serialization process:

1. **Primitive types**: Direct pass-through for `str`, `int`, `float`, `bool`, `dict`, `list` [src/langmem/knowledge/tools.py:502-503]()
2. **Pydantic models**: Use `model_dump(mode="json")` [src/langmem/knowledge/tools.py:506]()
3. **Fallback**: Convert to string [src/langmem/knowledge/tools.py:509]()

Sources: [src/langmem/knowledge/tools.py:500-511]()

## Schema Validation

The `schema` parameter provides type hints for memory content validation. The tool dynamically creates type annotations based on the provided schema:

- **Default**: `str` type for simple text memories
- **Custom**: Any Python type, commonly Pydantic models for structured data
- **Integration**: Schema becomes part of the tool's function signature [src/langmem/knowledge/tools.py:272](), [src/langmem/knowledge/tools.py:306]()

Sources: [src/langmem/knowledge/tools.py:33](), [src/langmem/knowledge/tools.py:266]()

## Actions Permission Control

The `actions_permitted` parameter controls which operations the tool supports:

| Configuration | Allowed Operations | Use Case |
|--------------|-------------------|----------|
| `("create", "update", "delete")` | All operations | Full memory management |
| `("create", "update")` | Create and modify only | Prevent accidental deletion |
| `("create",)` | Create only | Append-only logging |
| `("update",)` | Update only | Profile management |

The tool validates actions at runtime and generates appropriate error messages for invalid operations [src/langmem/knowledge/tools.py:278-281]().

Sources: [src/langmem/knowledge/tools.py:34-36](), [src/langmem/knowledge/tools.py:264-268]()

## Store Integration

The tool integrates with LangGraph's BaseStore system through the `_get_store` helper function:

- **Provided store**: Uses the explicitly provided `BaseStore` instance
- **Runtime store**: Retrieves store from LangGraph context using `get_store()` [src/langmem/knowledge/tools.py:494]()
- **Error handling**: Raises `ConfigurationError` if no store available [src/langmem/knowledge/tools.py:497]()

Sources: [src/langmem/knowledge/tools.py:489-498](), [src/langmem/knowledge/tools.py:277](), [src/langmem/knowledge/tools.py:311]()

## Tool Schema Enhancement

The `_ToolWithRequired` class extends `StructuredTool` to ensure proper schema generation with required fields:

- Inherits from `StructuredTool` [src/langmem/knowledge/tools.py:513]()
- Uses `@functools.cached_property` for performance [src/langmem/knowledge/tools.py:514-515]()
- Applies `_ensure_schema_contains_required` to guarantee required fields [src/langmem/knowledge/tools.py:529-530]()

Sources: [src/langmem/knowledge/tools.py:513-531](), [src/langmem/knowledge/tools.py:354-356]()

---

# Page: Memory Search and Retrieval

# Memory Search and Retrieval

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)
- [src/langmem/knowledge/tools.py](src/langmem/knowledge/tools.py)

</details>



This document covers LangMem's memory search and retrieval capabilities, specifically focusing on the `create_search_memory_tool` function and related search functionality. This enables agents to find and retrieve relevant memories from their persistent storage during conversations.

For information about creating and managing memories, see [Memory Creation and Management](#5.1). For namespace organization patterns, see [Using Namespaces](#5.3).

## Overview

LangMem provides two primary approaches for memory search and retrieval:

1. **Agent-driven search tools** - Tools that agents can call to search their memories
2. **Automated search pipelines** - Background systems that automatically find relevant context

The search system integrates with LangGraph's `BaseStore` to perform both semantic and exact matching searches across organized memory namespaces.

**Memory Search Architecture**

```mermaid
graph TB
    subgraph "Agent Layer"
        Agent["Agent/LLM"]
        SearchTool["create_search_memory_tool()"]
    end
    
    subgraph "Search Pipeline"
        QueryGen["Query Generation"]
        NamespaceRes["NamespaceTemplate()"]
        StoreSearch["BaseStore.search()"]
        ResultFormat["Response Formatting"]
    end
    
    subgraph "Storage Layer" 
        BaseStore["LangGraph BaseStore"]
        InMemStore["InMemoryStore"]
        PostgresStore["AsyncPostgresStore"]
    end
    
    Agent --> SearchTool
    SearchTool --> QueryGen
    QueryGen --> NamespaceRes
    NamespaceRes --> StoreSearch
    StoreSearch --> BaseStore
    BaseStore --> InMemStore
    BaseStore --> PostgresStore
    StoreSearch --> ResultFormat
    ResultFormat --> Agent
```

Sources: [src/langmem/knowledge/tools.py:362-487](), [src/langmem/knowledge/extraction.py:695-816]()

## Search Tool Creation

The `create_search_memory_tool` function creates a structured tool that agents can use to search their persistent memories.

### Function Signature

```python
def create_search_memory_tool(
    namespace: tuple[str, ...] | str,
    *,
    instructions: str = "",
    store: BaseStore | None = None,
    response_format: Literal["content", "content_and_artifact"] = "content",
    name: str = "search_memory",
) -> StructuredTool
```

### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `namespace` | `tuple[str, ...]` | Storage namespace with template placeholders like `{langgraph_user_id}` |
| `instructions` | `str` | Custom instructions for when to use the search tool |
| `store` | `BaseStore \| None` | Optional store instance; uses LangGraph context if None |
| `response_format` | `Literal` | Either `"content"` or `"content_and_artifact"` |
| `name` | `str` | Tool name for agent recognition |

The namespace parameter supports runtime template resolution through `NamespaceTemplate`, allowing dynamic namespace construction based on configuration values.

Sources: [src/langmem/knowledge/tools.py:362-379](), [src/langmem/utils.py:NamespaceTemplate]()

## Search Query Patterns

The search tool accepts several query parameters that control how memories are retrieved:

### Tool Function Signature

```python
def search_memory(
    query: str,
    *,
    limit: int = 10,
    offset: int = 0, 
    filter: Optional[dict] = None,
) -> Union[str, Tuple[str, List[SearchItem]]]
```

### Query Types

**Semantic Search**
- Uses vector embeddings to find conceptually similar memories
- Requires store configured with embedding model
- Query example: `"user preferences about dark mode"`

**Exact Matching** 
- Searches for specific terms or phrases
- Works with any store implementation
- Query example: `"dark mode"`

**Filtered Search**
- Combines text search with metadata filters
- Uses `filter` parameter with key-value pairs
- Example: `{"type": "preference", "category": "ui"}`

**Search Tool Integration Flow**

```mermaid
sequenceDiagram
    participant Agent as "Agent/LLM"
    participant Tool as "search_memory Tool"
    participant NS as "NamespaceTemplate"
    participant Store as "BaseStore"
    participant Embed as "Embedding Model"
    
    Agent->>Tool: "search_memory(query='user preferences')"
    Tool->>NS: "resolve namespace from config"
    NS-->>Tool: "('memories', 'user-123')"
    Tool->>Store: "search(namespace, query, limit, filter)"
    
    alt Semantic Search
        Store->>Embed: "embed query text"
        Embed-->>Store: "query_vector"
        Store->>Store: "vector similarity search"
    else Exact Search
        Store->>Store: "text matching search"
    end
    
    Store-->>Tool: "List[SearchItem]"
    Tool->>Tool: "format response"
    Tool-->>Agent: "formatted memories"
```

Sources: [src/langmem/knowledge/tools.py:456-474](), [src/langmem/knowledge/tools.py:436-454]()

## Response Formats

The search tool supports two response formats controlled by the `response_format` parameter:

### Content Only Format

When `response_format="content"` (default):
- Returns serialized JSON string of memory contents
- Optimized for direct agent consumption
- Excludes metadata and search artifacts

```python
# Returns string like:
'[{"namespace": ["memories", "user-123"], "key": "pref-1", "value": {...}}]'
```

### Content and Artifact Format

When `response_format="content_and_artifact"`:
- Returns tuple of `(serialized_content, raw_search_items)`
- Provides access to `SearchItem` objects with scores and metadata
- Useful for advanced processing or ranking

```python
# Returns tuple like:
(
    '[{...}]',  # Serialized JSON string
    [SearchItem(...), SearchItem(...)]  # Raw objects with .score, .created_at, etc.
)
```

Sources: [src/langmem/knowledge/tools.py:452-454](), [src/langmem/knowledge/tools.py:472-474]()

## Automated Search Pipeline

LangMem also provides `create_memory_searcher` for automated memory retrieval with LLM-generated queries.

### Pipeline Architecture

```mermaid
graph LR
    subgraph "Input Processing"
        Messages["Conversation Messages"]
        Template["ChatPromptTemplate"]
    end
    
    subgraph "Query Generation"
        LLM["Language Model"]
        SearchTool["create_search_memory_tool"]
        ToolBinding["bind_tools()"]
    end
    
    subgraph "Search Execution" 
        ToolCalls["Tool Calls"]
        BatchSearch["search_tool.batch()"]
        StoreQueries["BaseStore.search()"]
    end
    
    subgraph "Result Processing"
        Dedup["Deduplication"]
        Scoring["Score-based Sorting"]
        Ranking["Result Ranking"]
    end
    
    Messages --> Template
    Template --> LLM
    LLM --> ToolBinding
    ToolBinding --> ToolCalls
    ToolCalls --> BatchSearch
    BatchSearch --> StoreQueries
    StoreQueries --> Dedup
    Dedup --> Scoring 
    Scoring --> Ranking
```

The pipeline uses `tool_choice="search_memory"` to ensure the model generates appropriate search queries, then executes multiple searches in parallel and ranks results by relevance score.

Sources: [src/langmem/knowledge/extraction.py:777-815](), [src/langmem/knowledge/extraction.py:786-804]()

## Integration Examples

### ReAct Agent Integration

```python
from langgraph.prebuilt import create_react_agent
from langmem import create_search_memory_tool

search_tool = create_search_memory_tool(
    namespace=("memories", "{langgraph_user_id}"),
)

agent = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest",
    tools=[search_tool],
    store=store,
)
```

### Custom Agent Integration

The search tool integrates with any agent framework that supports structured tools:

```python
# Agent can call the tool with:
result = await search_tool.ainvoke({
    "query": "user preferences about themes",
    "limit": 5,
    "filter": {"category": "ui"}
})
```

Sources: [src/langmem/knowledge/tools.py:406-431]()

## Error Handling

The search system includes several error conditions:

### Store Configuration Errors

When no store is available, the tool raises a `ConfigurationError`:

```python
# From _get_store function
try:
    store = get_store()
except RuntimeError as e:
    raise errors.ConfigurationError("Could not get store") from e
```

### Namespace Resolution Errors

Invalid namespace templates or missing configuration values cause runtime errors during namespace resolution.

Sources: [src/langmem/knowledge/tools.py:489-498](), [src/langmem/errors.py:ConfigurationError]()

## Performance Considerations

### Search Optimization

- **Limit Control**: Use appropriate `limit` values to balance context vs performance
- **Offset Pagination**: For large result sets, use `offset` for pagination
- **Parallel Searches**: Automated pipeline executes multiple queries concurrently
- **Result Deduplication**: Pipeline automatically deduplicates results across searches

### Store Configuration

Search performance depends heavily on the underlying `BaseStore` implementation:
- **InMemoryStore**: Fast for development, limited scalability
- **AsyncPostgresStore**: Production-ready with persistent storage
- **Vector Indexing**: Configure embedding dimensions and models for semantic search

Sources: [src/langmem/knowledge/extraction.py:994-1004](), [src/langmem/knowledge/tools.py:445-451]()

---

# Page: Using Namespaces

# Using Namespaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/langmem/knowledge/tools.py](src/langmem/knowledge/tools.py)
- [src/langmem/utils.py](src/langmem/utils.py)

</details>



This document explains how to organize and isolate memories using namespaces in langmem. Namespaces provide hierarchical organization and enable multi-tenancy by creating isolated memory spaces for different users, teams, or projects.

For information about memory storage backends, see [Storage Types](#7.1). For memory organization strategies, see [Namespace Organization](#7.2).

## Purpose and Structure

Namespaces in langmem are implemented as tuples of strings that create hierarchical paths for organizing memories. They enable isolation between different contexts and support dynamic variable substitution at runtime.

### Namespace Template System

The `NamespaceTemplate` class handles dynamic namespace resolution with variable substitution from `RunnableConfig`:

```mermaid
graph TB
    subgraph "NamespaceTemplate System"
        NT[NamespaceTemplate] --> Template["template: tuple[str, ...]"]
        NT --> Variables["vars: dict[int, str]"]
        Template --> Fixed["('memories', 'user_123')"]
        Template --> Dynamic["('memories', '{user_id}')"]
        Variables --> Substitution["configurable field lookup"]
    end
    
    subgraph "Runtime Resolution"
        Config[RunnableConfig] --> Configurable["configurable: dict"]
        Configurable --> Values["user_id: 'alice'"]
        Values --> Resolved["('memories', 'alice')"]
    end
    
    NT --> Config
    Dynamic --> Resolved
```

Sources: [src/langmem/utils.py:15-92]()

### Namespace Hierarchy Patterns

Common namespace organization patterns support different use cases:

| Pattern | Structure | Use Case |
|---------|-----------|----------|
| Personal | `("memories", "{user_id}")` | Individual user memories |
| Team | `("memories", "team-{team_id}")` | Shared team knowledge |
| Multi-level | `("memories", "team_a", "agent_a")` | Agent-specific within team |
| Global | `("global",)` | System-wide shared memories |
| Project | `("memories", "project-{project_id}")` | Project-specific isolation |

Sources: [docs/docs/guides/memory_tools.md:59-70]()

## Dynamic Variable Substitution

The `NamespaceTemplate` class supports runtime variable substitution using curly brace syntax:

```mermaid
flowchart TD
    subgraph "Variable Processing"
        Input["'{user_id}'"] --> GetKey["_get_key() function"]
        GetKey --> Extract["Extract 'user_id'"]
        Extract --> Store["vars[index] = 'user_id'"]
    end
    
    subgraph "Runtime Resolution"
        Config["RunnableConfig"] --> Configurable["configurable field"]
        Configurable --> Lookup["configurable['user_id']"]
        Lookup --> Substitute["Replace '{user_id}' with value"]
    end
    
    Store --> Lookup
    Substitute --> Result["('memories', 'alice')"]
```

Sources: [src/langmem/utils.py:67-71](), [src/langmem/utils.py:94-95]()

### Implementation Details

The `NamespaceTemplate.__call__` method performs the substitution:

- Retrieves config using `get_config()` from langgraph context
- Accesses the `configurable` field from `RunnableConfig`
- Substitutes variables using the `vars` mapping
- Raises `ConfigurationError` for missing keys

Sources: [src/langmem/utils.py:73-91]()

## Memory Tool Integration

Memory tools use namespaces to organize and isolate memories across different contexts:

```mermaid
graph TB
    subgraph "Memory Tool Configuration"
        ManageTool["create_manage_memory_tool"] --> ManageNS["namespace=('memories', '{user_id}')"]
        SearchTool["create_search_memory_tool"] --> SearchNS["namespace=('memories', '{user_id}')"]
        ManageNS --> SharedNS["Shared namespace template"]
        SearchNS --> SharedNS
    end
    
    subgraph "Runtime Execution"
        Agent["ReAct Agent"] --> InvokeA["invoke with config"]
        InvokeA --> ConfigA["configurable: {'user_id': 'alice'}"]
        ConfigA --> NamespaceA["('memories', 'alice')"]
        
        Agent --> InvokeB["invoke with config"]
        InvokeB --> ConfigB["configurable: {'user_id': 'bob'}"]
        ConfigB --> NamespaceB["('memories', 'bob')"]
    end
    
    SharedNS --> NamespaceA
    SharedNS --> NamespaceB
```

Sources: [docs/docs/guides/memory_tools.md:36-37]()

### Multi-Agent Namespace Patterns

Complex systems can use hierarchical namespaces for different read/write access patterns:

```mermaid
graph TB
    subgraph "Team Memory Organization"
        TeamRoot["('memories', 'team_a')"] --> AgentA["('memories', 'team_a', 'agent_a')"]
        TeamRoot --> AgentB["('memories', 'team_a', 'agent_b')"]
        
        AgentA --> WriteA["Agent A writes here"]
        AgentB --> WriteB["Agent B writes here"]
        TeamRoot --> ReadShared["Both agents read from team level"]
    end
    
    subgraph "Tool Configuration"
        AgentATools["agent_a_tools"] --> ManageA["create_manage_memory_tool<br/>namespace=('memories', 'team_a', 'agent_a')"]
        AgentATools --> SearchA["create_search_memory_tool<br/>namespace=('memories', 'team_a')"]
        
        AgentBTools["agent_b_tools"] --> ManageB["create_manage_memory_tool<br/>namespace=('memories', 'team_a', 'agent_b')"]
        AgentBTools --> SearchB["create_search_memory_tool<br/>namespace=('memories', 'team_a')"]
    end
    
    ManageA --> WriteA
    ManageB --> WriteB
    SearchA --> ReadShared
    SearchB --> ReadShared
```

Sources: [docs/docs/guides/memory_tools.md:88-93](), [docs/docs/guides/memory_tools.md:105-109]()

## Storage Integration

Namespaces integrate with the `BaseStore` interface to provide organized memory access:

```mermaid
sequenceDiagram
    participant Tool as "Memory Tool"
    participant Template as "NamespaceTemplate"
    participant Store as "BaseStore"
    participant Storage as "InMemoryStore/PostgresStore"
    
    Tool->>Template: "__call__(config)"
    Template->>Template: "get_config() from context"
    Template->>Template: "substitute variables"
    Template->>Tool: "resolved namespace tuple"
    Tool->>Store: "store.put(namespace, key, value)"
    Store->>Storage: "organized by namespace"
    
    Note over Tool,Storage: Search with namespace isolation
    Tool->>Store: "store.search(namespace, query)"
    Store->>Storage: "search within namespace only"
    Storage->>Store: "namespace-scoped results"
    Store->>Tool: "relevant memories"
```

Sources: [src/langmem/utils.py:73-91]()

## CrewAI Integration

CrewAI agents use fixed namespaces since they don't have access to `RunnableConfig`:

```mermaid
graph TB
    subgraph "CrewAI Memory Setup"
        Store["InMemoryStore"] --> Tools["memory_tools"]
        Tools --> ManageTool["create_manage_memory_tool<br/>namespace='memories'"]
        Tools --> SearchTool["create_search_memory_tool<br/>namespace='memories'"]
        
        ManageTool --> Agent1["knowledge_agent"]
        SearchTool --> Agent1
        ManageTool --> Agent2["teacher_agent"]
        SearchTool --> Agent2
    end
    
    subgraph "Shared Namespace"
        SharedNS["('memories',)"] --> Memory1["Agent 1 memories"]
        SharedNS --> Memory2["Agent 2 memories"]
        Memory1 --> Access["Both agents access same namespace"]
        Memory2 --> Access
    end
    
    Agent1 --> SharedNS
    Agent2 --> SharedNS
```

Sources: [docs/docs/guides/use_tools_in_crewai.md:35-38]()

## Background Processing Integration

Background memory processing also uses namespaces for organization:

```mermaid
graph TB
    subgraph "Memory Store Manager"
        Manager["create_memory_store_manager"] --> Namespace["namespace=('memories', 'episodes')"]
        Namespace --> EpisodicNS["('memories', 'episodes')"]
    end
    
    subgraph "Storage Operation"
        Manager --> StoreOp["manager.invoke({'messages': conversation})"]
        StoreOp --> Extract["Extract Episode objects"]
        Extract --> Store["store.put(('memories', 'episodes'), key, episode)"]
    end
    
    subgraph "Retrieval Operation"
        Search["store.search(('memories', 'episodes'), query)"] --> Results["namespace-scoped results"]
        Results --> EpisodicMemories["Retrieved episodes"]
    end
    
    EpisodicNS --> Store
    EpisodicNS --> Search
```

Sources: [docs/docs/guides/extract_episodic_memories.md:102-103]()

## Error Handling

The `NamespaceTemplate` system provides robust error handling for configuration issues:

```mermaid
flowchart TD
    subgraph "Configuration Resolution"
        Template["NamespaceTemplate.__call__()"] --> GetConfig["get_config()"]
        GetConfig --> ConfigExists{"Config available?"}
        ConfigExists -->|No| DefaultConfig["config = {}"]
        ConfigExists -->|Yes| UseConfig["Use retrieved config"]
    end
    
    subgraph "Variable Substitution"
        UseConfig --> HasVars{"Has variables?"}
        HasVars -->|No| ReturnTemplate["Return template as-is"]
        HasVars -->|Yes| GetConfigurable["config['configurable']"]
        GetConfigurable --> VarExists{"Variable exists?"}
        VarExists -->|No| ConfigError["raise ConfigurationError"]
        VarExists -->|Yes| Substitute["Substitute variable"]
    end
    
    DefaultConfig --> HasVars
    ConfigError --> ErrorMessage["'Missing key in configurable field'"]
```

Sources: [src/langmem/utils.py:74-89]()

## Best Practices

### Namespace Design Patterns

1. **Consistent Hierarchy**: Use consistent namespace structures across your application
2. **Variable Naming**: Use descriptive variable names like `{user_id}` instead of `{id}`
3. **Depth Management**: Keep namespace depth reasonable (2-4 levels typically)
4. **Isolation**: Ensure proper isolation between different contexts

### Configuration Management

1. **Required Variables**: Always provide required variables in the `configurable` field
2. **Error Handling**: Handle `ConfigurationError` for missing variables
3. **Context Awareness**: Use `get_config()` for automatic context retrieval in LangGraph

Sources: [src/langmem/utils.py:86-89]()

---

# Page: Prompt Optimization

# Prompt Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/reference/index.md](docs/docs/reference/index.md)
- [src/langmem/__init__.py](src/langmem/__init__.py)
- [src/langmem/prompts/optimization.py](src/langmem/prompts/optimization.py)
- [src/langmem/prompts/types.py](src/langmem/prompts/types.py)

</details>



LangMem's prompt optimization system provides tools for iteratively improving LLM prompts based on conversation history and feedback. The system enables both single prompt optimization and multi-prompt optimization with different strategies to adapt to varying performance requirements and cost constraints.

For information about managing prompts as procedural memory, see [Key Concepts](1.2).

## Overview

LangMem's prompt optimization capabilities are exposed through two main functions in the public API:

- `create_prompt_optimizer` - Optimizes individual prompts using configurable strategies
- `create_multi_prompt_optimizer` - Optimizes multiple related prompts while maintaining consistency

These functions analyze `AnnotatedTrajectory` objects (conversation history with feedback) and return optimized prompt text that should perform better on similar future interactions.

## Integration with LangMem Ecosystem

Prompt optimization integrates with LangMem's broader memory management system:

```mermaid
graph TB
    subgraph "LangMem Core API"
        MM["create_memory_manager"]
        PO["create_prompt_optimizer"]
        MPO["create_multi_prompt_optimizer"]
        TE["create_thread_extractor"]
    end
    
    subgraph "Application Layer"
        Agent["Agent Systems"]
        Workflow["LangGraph Workflows"]
        CB["Chatbots"]
    end
    
    subgraph "Memory Types"
        Semantic["Semantic Memory"]
        Episodic["Episodic Memory"]
        Procedural["Procedural Memory<br/>(System Prompts)"]
    end
    
    subgraph "LLM Providers"
        OpenAI["OpenAI Models"]
        Anthropic["Anthropic Models"]
    end
    
    Agent --> PO
    Agent --> MPO
    Workflow --> PO
    CB --> MPO
    
    PO --> OpenAI
    PO --> Anthropic
    MPO --> OpenAI
    MPO --> Anthropic
    
    PO --> Procedural
    MPO --> Procedural
    MM --> Semantic
    MM --> Episodic
    TE --> MM
```

Sources: [src/langmem/__init__.py:9-13](), [src/langmem/prompts/optimization.py:50-269]()

## Single Prompt Optimization

The `create_prompt_optimizer` function creates an optimizer that analyzes and improves individual prompts based on conversation trajectories and feedback.

```python
def create_prompt_optimizer(
    model: str | BaseChatModel,
    kind: Literal["gradient", "prompt_memory", "metaprompt"] = "gradient",
    config: Optional[Union[GradientOptimizerConfig, MetapromptOptimizerConfig]] = None,
) -> Runnable[prompt_types.OptimizerInput, str]:
    """Create a prompt optimizer that improves prompt effectiveness."""
```

## Optimization Strategies

The `create_prompt_optimizer` function supports three optimization strategies through the `kind` parameter:

### Strategy: `kind="gradient"`

```mermaid
sequenceDiagram
    participant Client
    participant create_gradient_prompt_optimizer
    participant GradientOptimizer
    participant LLM["Language Model"]

    Client->>create_gradient_prompt_optimizer: "OptimizerInput"
    
    loop "min_reflection_steps to max_reflection_steps"
        create_gradient_prompt_optimizer->>GradientOptimizer: "Reflect on current prompt"
        GradientOptimizer->>LLM: "Critique current state"
        LLM-->>GradientOptimizer: "Areas for improvement"
        GradientOptimizer->>LLM: "Apply specific updates"
        LLM-->>GradientOptimizer: "Updated prompt text"
    end
    
    create_gradient_prompt_optimizer-->>Client: "Optimized prompt string"
```

- **Implementation**: Uses `create_gradient_prompt_optimizer` from `langmem.prompts.gradient`
- **Configuration**: `GradientOptimizerConfig` with `gradient_prompt`, `metaprompt`, and reflection step limits
- **LLM Calls**: 2 per reflection step (critique + update), total 4-10 calls
- **Best for**: Thorough optimization with separation of concerns

### Strategy: `kind="metaprompt"`

```mermaid
sequenceDiagram
    participant Client
    participant create_metaprompt_optimizer
    participant MetapromptOptimizer
    participant LLM["Language Model"]

    Client->>create_metaprompt_optimizer: "OptimizerInput"
    
    loop "min_reflection_steps to max_reflection_steps"
        create_metaprompt_optimizer->>MetapromptOptimizer: "Analyze trajectories"
        MetapromptOptimizer->>LLM: "Meta-learning analysis"
        LLM-->>MetapromptOptimizer: "Direct prompt update"
    end
    
    create_metaprompt_optimizer-->>Client: "Optimized prompt string"
```

- **Implementation**: Uses `create_metaprompt_optimizer` from `langmem.prompts.metaprompt`
- **Configuration**: `MetapromptOptimizerConfig` with `metaprompt` and reflection step limits
- **LLM Calls**: 1 per reflection step, total 2-5 calls
- **Best for**: Balanced speed and improvement quality

### Strategy: `kind="prompt_memory"`

```mermaid
sequenceDiagram
    participant Client
    participant PromptMemoryMultiple
    participant LLM["Language Model"]

    Client->>PromptMemoryMultiple: "OptimizerInput"
    PromptMemoryMultiple->>LLM: "Single-shot optimization"
    LLM-->>PromptMemoryMultiple: "Updated prompt"
    PromptMemoryMultiple-->>Client: "Optimized prompt string"
```

- **Implementation**: Uses `PromptMemoryMultiple` from `langmem.prompts.stateless`
- **Configuration**: No additional configuration required
- **LLM Calls**: 1 total
- **Best for**: Fast, simple updates with minimal cost

Sources: [src/langmem/prompts/optimization.py:23-269](), [src/langmem/prompts/optimization.py:260-265]()

### Performance Comparison

| Strategy | LLM Calls | Implementation | Configuration Type | Best For |
|----------|-----------|----------------|-------------------|----------|
| `prompt_memory` | 1 | `PromptMemoryMultiple` | None | Fast, simple updates |
| `metaprompt` | 1-5 | `create_metaprompt_optimizer` | `MetapromptOptimizerConfig` | Balanced cost/quality |
| `gradient` | 2-10 | `create_gradient_prompt_optimizer` | `GradientOptimizerConfig` | Thorough optimization |

The `gradient` strategy uses 2 LLM calls per reflection step (critique + update), while `metaprompt` uses 1 call per step. Both support configurable `min_reflection_steps` and `max_reflection_steps` (defaults: min=1, max=3 for gradient; min=1, max=3 for metaprompt).

Sources: [src/langmem/prompts/optimization.py:236-258](), [src/langmem/prompts/optimization.py:112-117](), [src/langmem/prompts/optimization.py:140-144]()

## Data Types

### Prompt TypedDict

The optimization system uses the `Prompt` TypedDict for structured prompt management:

```mermaid
classDiagram
    class Prompt {
        +str name*
        +str prompt*
        +str update_instructions?
        +str when_to_update?
    }
    
    class OptimizerInput {
        +Sequence~AnnotatedTrajectory~ trajectories
        +str|Prompt prompt
    }
    
    class MultiPromptOptimizerInput {
        +Sequence~AnnotatedTrajectory~ trajectories
        +list~Prompt~ prompts
    }
    
    class AnnotatedTrajectory {
        +Sequence~AnyMessage~ messages
        +dict|str|None feedback
    }
    
    OptimizerInput --> Prompt
    OptimizerInput --> AnnotatedTrajectory
    MultiPromptOptimizerInput --> Prompt
    MultiPromptOptimizerInput --> AnnotatedTrajectory
```

The `Prompt` TypedDict structure provides:
- `name` (Required): Unique identifier for the prompt
- `prompt` (Required): The actual prompt text to optimize
- `update_instructions` (Optional): Guidelines for how to modify the prompt
- `when_to_update` (Optional): Dependencies between prompts during multi-prompt optimization

### Input Types

- `OptimizerInput`: Used by `create_prompt_optimizer`, contains trajectories and a single prompt
- `MultiPromptOptimizerInput`: Used by `create_multi_prompt_optimizer`, contains trajectories and multiple prompts
- `AnnotatedTrajectory`: Conversation messages with optional feedback for optimization analysis

Sources: [src/langmem/prompts/types.py:7-34](), [src/langmem/prompts/types.py:62-93](), [src/langmem/prompts/types.py:95-136]()

### Usage Example

```python
from langmem import create_prompt_optimizer

optimizer = create_prompt_optimizer("anthropic:claude-3-5-sonnet-latest")

# Example conversation with feedback
conversation = [
    {"role": "user", "content": "Tell me about the solar system"},
    {"role": "assistant", "content": "The solar system consists of..."},
]
feedback = {"clarity": "needs more structure"}

# Use conversation history to improve the prompt
trajectories = [(conversation, feedback)]
better_prompt = await optimizer.ainvoke(
    {"trajectories": trajectories, "prompt": "You are an astronomy expert"}
)
print(better_prompt)
```

Sources: [src/langmem/prompts/optimization.py:169-187]()

## Multi-Prompt Optimization

The `create_multi_prompt_optimizer` function creates a `MultiPromptOptimizer` that optimizes multiple related prompts while maintaining consistency. This is essential for prompt chains, multi-agent systems, and complex workflows.

### Multi-Prompt Architecture

```mermaid
graph TD
    create_multi_prompt_optimizer["create_multi_prompt_optimizer()"] --> MultiPromptOptimizer["MultiPromptOptimizer class"]
    
    MultiPromptOptimizer --> _optimizer["_optimizer<br/>(create_prompt_optimizer)"]
    MultiPromptOptimizer --> create_extractor["create_extractor<br/>(trustcall)"]
    
    _optimizer -->|kind=gradient| create_gradient_prompt_optimizer
    _optimizer -->|kind=metaprompt| create_metaprompt_optimizer  
    _optimizer -->|kind=prompt_memory| PromptMemoryMultiple
    
    create_extractor --> Classify["Classify tool<br/>(BaseModel)"]
    Classify --> which_prompts["which: list[str]"]
    Classify --> reasoning["reasoning: str"]
    
    MultiPromptOptimizer --> asyncio_gather["asyncio.gather()"]
    asyncio_gather --> Updated_Prompts["list[Prompt]"]
```

The `MultiPromptOptimizer` class:
1. Initializes with a single-prompt optimizer (`_optimizer`) internally
2. Uses `create_extractor` with a `Classify` tool to determine which prompts need updates
3. Optimizes selected prompts concurrently using `asyncio.gather`
4. Returns the complete prompt list with updates applied

Sources: [src/langmem/prompts/optimization.py:272-287](), [src/langmem/prompts/optimization.py:471-616]()

### Multi-Prompt Optimization Workflow

```mermaid
sequenceDiagram
    participant Client
    participant MultiPromptOptimizer
    participant create_extractor
    participant Classify
    participant _optimizer
    participant asyncio_gather

    Client->>MultiPromptOptimizer: "MultiPromptOptimizerInput"
    
    alt "len(prompts) == 1 and no when_to_update"
        MultiPromptOptimizer->>_optimizer: "Direct optimization"
        _optimizer-->>MultiPromptOptimizer: "Updated prompt text"
    else "Multiple prompts or when_to_update specified"
        MultiPromptOptimizer->>create_extractor: "Classification prompt"
        create_extractor->>Classify: "Analyze trajectories"
        Classify-->>create_extractor: "Classify(reasoning, which)"
        create_extractor-->>MultiPromptOptimizer: "to_update list"
        
        MultiPromptOptimizer->>asyncio_gather: "Concurrent optimization"
        loop "For each prompt in to_update"
            asyncio_gather->>_optimizer: "Optimize individual prompt"
            _optimizer-->>asyncio_gather: "Updated prompt text"
        end
        asyncio_gather-->>MultiPromptOptimizer: "All updated results"
    end
    
    MultiPromptOptimizer-->>Client: "Complete list[Prompt]"
```

### Classification Process

The multi-prompt optimizer uses a `Classify` tool created with `create_extractor` to determine which prompts need updates:

1. **Analysis**: Examines `trajectories` (conversation history with feedback)
2. **Evaluation**: Identifies which named prompts contributed to performance issues  
3. **Selection**: Returns `which` list containing prompt names to update
4. **Validation**: Ensures selected names exist in the provided prompts list

The classifier uses this prompt template:
```text
Analyze the following trajectories and decide which prompts 
ought to be updated to improve the performance on future trajectories:

{sessions_str}

Below are the prompts being optimized:
{prompt_joined_content}
```

Sources: [src/langmem/prompts/optimization.py:289-373](), [src/langmem/prompts/optimization.py:317-350](), [src/langmem/prompts/optimization.py:356-363]()

## Implementation Details

### Function Signatures and Overloads

The `create_prompt_optimizer` function uses Python overloads for type safety:

```mermaid
classDiagram
    class create_prompt_optimizer {
        +@overload(model, kind="gradient", config: GradientOptimizerConfig?)
        +@overload(model, kind="metaprompt", config: MetapromptOptimizerConfig?)
        +@overload(model, kind="prompt_memory", config=None)
        +actual_implementation(model, kind: KINDS, config: Union[configs])
    }
    
    class KINDS {
        <<"Literal">>
        gradient
        metaprompt 
        prompt_memory
    }
    
    create_prompt_optimizer --> KINDS
```

### Factory Pattern Implementation

Both optimizer functions follow a factory pattern:

```mermaid
graph LR
    create_prompt_optimizer --> Factory_Logic{kind?}
    Factory_Logic -->|gradient| create_gradient_prompt_optimizer
    Factory_Logic -->|metaprompt| create_metaprompt_optimizer
    Factory_Logic -->|prompt_memory| PromptMemoryMultiple
    
    create_multi_prompt_optimizer --> MultiPromptOptimizer
    MultiPromptOptimizer -->|internal| create_prompt_optimizer
```

### Error Handling

The system includes validation for:
- Invalid `kind` values: raises `NotImplementedError` with expected options
- Invalid prompt names in classification: `Classify` model validator ensures names exist in choices
- Type safety through overloads and TypedDict structures

Sources: [src/langmem/prompts/optimization.py:26-48](), [src/langmem/prompts/optimization.py:260-269](), [src/langmem/prompts/optimization.py:327-334]()

### Usage Example

```python
from langmem import create_multi_prompt_optimizer

optimizer = create_multi_prompt_optimizer("anthropic:claude-3-5-sonnet-latest")

# Example conversation with feedback
conversation = [
    {"role": "user", "content": "Tell me about the solar system"},
    {"role": "assistant", "content": "The solar system consists of..."},
]
feedback = {"clarity": "needs more structure"}

# Define multiple prompts to optimize
prompts = [
    {"name": "research", "prompt": "Research the given topic thoroughly"},
    {"name": "summarize", "prompt": "Summarize the research findings"},
]

# Use conversation history to improve the prompts
trajectories = [(conversation, feedback)]
better_prompts = await optimizer.ainvoke(
    {"trajectories": trajectories, "prompts": prompts}
)
print(better_prompts)
```

Sources: [src/langmem/prompts/optimization.py:538-562]()

## Implementation Architecture

Title: Complete Prompt Optimization Implementation Architecture

```mermaid
graph TD
    Client["Client Application"] -->|"uses"| PromptOptAPI["Prompt Optimization API"]
    
    subgraph "Public API"
        PromptOptAPI -->|"single prompt"| create_prompt_optimizer["create_prompt_optimizer()"]
        PromptOptAPI -->|"multiple prompts"| create_multi_prompt_optimizer["create_multi_prompt_optimizer()"]
    end
    
    subgraph "Implementation"
        create_prompt_optimizer -->|"kind=gradient"| create_gradient_prompt_optimizer["create_gradient_prompt_optimizer()"]
        create_prompt_optimizer -->|"kind=metaprompt"| create_metaprompt_optimizer["create_metaprompt_optimizer()"]
        create_prompt_optimizer -->|"kind=prompt_memory"| PromptMemoryMultiple["PromptMemoryMultiple"]
        
        create_multi_prompt_optimizer --> MultiPromptOptimizer["MultiPromptOptimizer"]
        MultiPromptOptimizer -->|"internal use"| create_prompt_optimizer
    end
    
    subgraph "Data Types"
        create_prompt_optimizer --> OptimizerInput["OptimizerInput"]
        create_multi_prompt_optimizer --> MultiPromptOptimizerInput["MultiPromptOptimizerInput"]
        OptimizerInput --> AnnotatedTrajectory["AnnotatedTrajectory"]
        OptimizerInput --> Prompt["Prompt"]
        MultiPromptOptimizerInput --> AnnotatedTrajectory
        MultiPromptOptimizerInput --> Prompt
    end
    
    subgraph "Utilities"
        MultiPromptOptimizer --> create_extractor["create_extractor (trustcall)"]
        MultiPromptOptimizer --> format_sessions["format_sessions()"]
    end
```

Sources: [src/langmem/prompts/optimization.py:1-619](), [src/langmem/prompts/types.py:1-136]()

## Integration with LangMem

The prompt optimization system integrates with the broader LangMem ecosystem:

1. It supports the same storage patterns as other LangMem components
2. It can be used with other LangMem memory types, particularly for procedural memory
3. It can be integrated with both agent-driven and background memory processes

When used in conjunction with LangMem's memory management, prompt optimization enables systems to:
1. Store and retrieve optimized prompts
2. Apply learned improvements across different contexts
3. Continuously refine prompts based on ongoing interactions

Sources: [src/langmem/prompts/__init__.py:1-28]()

---

# Page: Single Prompt Optimization

# Single Prompt Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/reference/index.md](docs/docs/reference/index.md)
- [src/langmem/__init__.py](src/langmem/__init__.py)
- [src/langmem/prompts/optimization.py](src/langmem/prompts/optimization.py)
- [src/langmem/prompts/types.py](src/langmem/prompts/types.py)

</details>



Single prompt optimization in LangMem provides automated improvement of individual prompts through iterative refinement using conversation feedback and trajectory analysis. This page covers the `create_prompt_optimizer` function and its three optimization strategies for enhancing prompt effectiveness.

For information about optimizing multiple prompts simultaneously, see [Multi-Prompt Optimization](#6.2). For the general overview of prompt optimization capabilities, see [Prompt Optimization](#6).

## Overview

The `create_prompt_optimizer` function creates a `Runnable` that analyzes conversation trajectories and feedback to iteratively improve prompt quality. It accepts three different optimization strategies, each with distinct approaches to prompt refinement.

```mermaid
graph TB
    subgraph "create_prompt_optimizer Function"
        CPO["create_prompt_optimizer()"]
        INPUT["OptimizerInput"]
        OUTPUT["Optimized Prompt String"]
        
        CPO --> STRATEGIES["Strategy Selection"]
        
        subgraph "Strategy Implementations" 
            GRAD["create_gradient_prompt_optimizer()"]
            META["create_metaprompt_optimizer()"]  
            PMEM["PromptMemoryMultiple()"]
        end
        
        STRATEGIES --> GRAD
        STRATEGIES --> META
        STRATEGIES --> PMEM
    end
    
    INPUT --> CPO
    CPO --> OUTPUT
    
    subgraph "Input Components"
        TRAJ["AnnotatedTrajectory[]"]
        PROMPT["Prompt | str"]
    end
    
    TRAJ --> INPUT
    PROMPT --> INPUT
```

**Single Prompt Optimizer Architecture**

Sources: [src/langmem/prompts/optimization.py:50-269]()

## Function Signature and Parameters

The `create_prompt_optimizer` function provides type-safe overloads for each optimization strategy:

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `str \| BaseChatModel` | Language model for optimization |
| `kind` | `"gradient" \| "metaprompt" \| "prompt_memory"` | Optimization strategy |
| `config` | Strategy-specific config | Optional configuration object |

The function returns a `Runnable[OptimizerInput, str]` that processes conversation trajectories and returns an optimized prompt string.

Sources: [src/langmem/prompts/optimization.py:26-58]()

## Optimization Strategies

### Gradient Strategy

The gradient optimizer uses a two-phase approach separating critique generation from prompt updates through reflection cycles.

```mermaid
sequenceDiagram
    participant USER as "User Input"
    participant OPT as "GradientOptimizer"
    participant REFL as "ReflectionChain"
    participant UPD as "UpdateChain"
    participant LLM as "Language Model"
    
    USER->>OPT: "OptimizerInput"
    
    loop "min_steps to max_steps"
        OPT->>REFL: "Current prompt + feedback"
        REFL->>LLM: "Analyze and critique"
        LLM-->>REFL: "Improvement suggestions"
        REFL-->>OPT: "Reflection results"
        
        OPT->>UPD: "Apply improvements"
        UPD->>LLM: "Update prompt text"
        LLM-->>UPD: "Updated prompt"
        UPD-->>OPT: "New prompt version"
    end
    
    OPT-->>USER: "Final optimized prompt"
```

**Gradient Optimization Flow**

The gradient strategy requires 2 LLM calls per iteration (reflection + update) and supports `GradientOptimizerConfig` for customization:

- `gradient_prompt`: Custom reflection prompt
- `metaprompt`: Custom update instructions  
- `max_reflection_steps`: Maximum iterations (default: 3)
- `min_reflection_steps`: Minimum iterations (default: 1)

Sources: [src/langmem/prompts/optimization.py:88-118](), [src/langmem/prompts/gradient.py]()

### Metaprompt Strategy

The metaprompt optimizer uses meta-learning to analyze patterns and directly propose prompt improvements in single steps.

```mermaid
sequenceDiagram
    participant USER as "User Input"
    participant META as "MetapromptOptimizer" 
    participant ANALYZER as "PatternAnalyzer"
    participant LLM as "Language Model"
    
    USER->>META: "OptimizerInput"
    
    loop "min_steps to max_steps"
        META->>ANALYZER: "Trajectory patterns"
        ANALYZER->>LLM: "Meta-learning prompt"
        LLM-->>ANALYZER: "Pattern insights"
        ANALYZER-->>META: "Optimization strategy"
        
        META->>LLM: "Apply meta-updates"
        LLM-->>META: "Updated prompt"
    end
    
    META-->>USER: "Optimized prompt"
```

**Metaprompt Optimization Flow**

The metaprompt strategy uses 1 LLM call per step and supports `MetapromptOptimizerConfig`:

- `metaprompt`: Custom meta-learning instructions
- `max_reflection_steps`: Maximum meta-steps (default: 3)  
- `min_reflection_steps`: Minimum meta-steps (default: 1)

Sources: [src/langmem/prompts/optimization.py:119-145](), [src/langmem/prompts/metaprompt.py]()

### Prompt Memory Strategy  

The prompt memory optimizer extracts successful patterns from conversation history for single-shot prompt enhancement.

```mermaid
sequenceDiagram
    participant USER as "User Input"
    participant PMEM as "PromptMemoryMultiple"
    participant EXTRACTOR as "PatternExtractor" 
    participant LLM as "Language Model"
    
    USER->>PMEM: "OptimizerInput"
    PMEM->>EXTRACTOR: "Extract success patterns"
    EXTRACTOR->>LLM: "Pattern extraction prompt"
    LLM-->>EXTRACTOR: "Successful patterns"
    EXTRACTOR-->>PMEM: "Pattern library"
    
    PMEM->>LLM: "Apply patterns to prompt"
    LLM-->>PMEM: "Enhanced prompt"
    PMEM-->>USER: "Optimized prompt"
```

**Prompt Memory Optimization Flow**

The prompt memory strategy requires only 1 LLM call total and learns directly from conversation history without additional configuration.

Sources: [src/langmem/prompts/optimization.py:146-166](), [src/langmem/prompts/stateless.py]()

## Data Structures

### OptimizerInput

The `OptimizerInput` TypedDict defines the input structure for single prompt optimization:

| Field | Type | Description |
|-------|------|-------------|
| `trajectories` | `Sequence[AnnotatedTrajectory] \| str` | Conversation history with feedback |
| `prompt` | `str \| Prompt` | Prompt to optimize |

### AnnotatedTrajectory

The `AnnotatedTrajectory` NamedTuple contains conversation messages with optional feedback:

| Field | Type | Description |
|-------|------|-------------|
| `messages` | `Sequence[AnyMessage]` | Conversation messages |
| `feedback` | `dict \| str \| None` | Optimization feedback |

### Prompt TypedDict

The `Prompt` TypedDict provides structured prompt management:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `str` | Yes | Prompt identifier |
| `prompt` | `str` | Yes | Prompt text |
| `update_instructions` | `str \| None` | No | Modification guidelines |
| `when_to_update` | `str \| None` | No | Update conditions |

Sources: [src/langmem/prompts/types.py:7-93]()

## Usage Patterns

### Basic Optimization

```python
from langmem import create_prompt_optimizer

optimizer = create_prompt_optimizer("anthropic:claude-3-5-sonnet-latest")

trajectories = [AnnotatedTrajectory(
    messages=[
        {"role": "user", "content": "What's the weather?"},
        {"role": "assistant", "content": "I can't check weather"}
    ],
    feedback="Should use search tools"
)]

result = await optimizer.ainvoke({
    "trajectories": trajectories,
    "prompt": "You are a helpful assistant"
})
```

### Strategy Selection

```python
# Gradient optimization with custom config
gradient_optimizer = create_prompt_optimizer(
    "openai:gpt-4",
    kind="gradient",
    config=GradientOptimizerConfig(max_reflection_steps=5)
)

# Metaprompt optimization
meta_optimizer = create_prompt_optimizer(
    "openai:gpt-4", 
    kind="metaprompt"
)

# Simple prompt memory optimization
memory_optimizer = create_prompt_optimizer(
    "openai:gpt-4",
    kind="prompt_memory"
)
```

Sources: [src/langmem/prompts/optimization.py:167-234]()

## Performance Characteristics

### LLM Call Patterns

| Strategy | Calls per Step | Total Calls | Speed | Thoroughness |
|----------|----------------|-------------|-------|--------------|
| `prompt_memory` | 1 | 1 | Fastest | Limited |
| `metaprompt` | 1 | 1-5 | Moderate | Balanced |
| `gradient` | 2 | 2-10 | Slowest | Highest |

### Strategy Selection Guidelines

```mermaid
flowchart TD
    START["Need prompt optimization?"]
    SIMPLE["Simple patterns?"]
    COST["Cost sensitive?"]
    QUALITY["Quality priority?"]
    
    START --> SIMPLE
    SIMPLE -->|Yes| PMEM["prompt_memory"]
    SIMPLE -->|No| COST
    COST -->|Yes| META["metaprompt"] 
    COST -->|No| QUALITY
    QUALITY -->|Highest| GRAD["gradient"]
    QUALITY -->|Balanced| META
    
    PMEM --> RESULT1["1 LLM call<br/>Basic improvements"]
    META --> RESULT2["1-5 LLM calls<br/>Balanced optimization"]  
    GRAD --> RESULT3["2-10 LLM calls<br/>Thorough refinement"]
```

**Strategy Selection Decision Tree**

Sources: [src/langmem/prompts/optimization.py:236-258]()

### Integration with LangGraph

Single prompt optimizers integrate with LangGraph workflows through the standard `Runnable` interface, enabling use in agent chains and memory systems.

```mermaid
graph LR
    subgraph "LangGraph Workflow"
        AGENT["create_react_agent"]
        TOOLS["Agent Tools"]
        MEMORY["Memory Systems"]
    end
    
    subgraph "Prompt Optimization"
        OPT["create_prompt_optimizer"] 
        TRAJ["Trajectory Collection"]
        FEEDBACK["Feedback Analysis"]
    end
    
    AGENT --> TRAJ
    TOOLS --> TRAJ  
    MEMORY --> TRAJ
    TRAJ --> OPT
    FEEDBACK --> OPT
    OPT --> AGENT
```

**LangGraph Integration Pattern**

Sources: [src/langmem/__init__.py:9-13](), [src/langmem/prompts/optimization.py:1-28]()

---

# Page: Multi-Prompt Optimization

# Multi-Prompt Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/reference/index.md](docs/docs/reference/index.md)
- [src/langmem/__init__.py](src/langmem/__init__.py)
- [src/langmem/prompts/optimization.py](src/langmem/prompts/optimization.py)
- [src/langmem/prompts/types.py](src/langmem/prompts/types.py)

</details>



Multi-prompt optimization provides coordinated improvement of multiple interconnected prompts using classification-based prompt selection. The `create_multi_prompt_optimizer` function returns a `MultiPromptOptimizer` instance that analyzes conversation trajectories to determine which prompts contributed to performance issues and selectively updates only those prompts.

The system uses credit assignment through structured extraction to identify which prompts need optimization, then applies the same underlying optimization strategies as single-prompt optimization to the selected prompts.

## Core Concepts

Multi-prompt optimization addresses several key challenges when working with systems of prompts:

1. **Credit Assignment** - Determining which specific prompts contributed to performance issues from conversation trajectories
2. **Selective Updates** - Only updating prompts that need improvement rather than modifying all prompts indiscriminately  
3. **Consistency Maintenance** - Ensuring that changes to one prompt don't conflict with other prompts in the system
4. **Concurrent Optimization** - Optimizing multiple prompts simultaneously using the same underlying strategy

Sources: [src/langmem/prompts/optimization.py:471-477]()

## Implementation and Usage

### Factory Function

The `create_multi_prompt_optimizer` function creates a `MultiPromptOptimizer` instance:

```python
def create_multi_prompt_optimizer(
    model: str | BaseChatModel,
    /,
    *,
    kind: Literal["gradient", "prompt_memory", "metaprompt"] = "gradient",
    config: Optional[dict] = None,
) -> Runnable[MultiPromptOptimizerInput, list[Prompt]]
```

### Function Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `str \| BaseChatModel` | Language model for optimization |
| `kind` | `Literal["gradient", "prompt_memory", "metaprompt"]` | Optimization strategy (default: "gradient") |
| `config` | `Optional[dict]` | Strategy-specific configuration passed to underlying `create_prompt_optimizer` |

### MultiPromptOptimizer Class Structure

The returned `MultiPromptOptimizer` extends `Runnable[MultiPromptOptimizerInput, list[Prompt]]` with these key attributes:

- `_optimizer`: Internal `create_prompt_optimizer` instance for individual prompt optimization
- `model`, `kind`, `config`: Configuration passed to constructor

### Input Types

Multi-prompt optimization uses structured input types from `langmem.prompts.types`:

**MultiPromptOptimizerInput**:
```python
{
    "trajectories": Sequence[AnnotatedTrajectory] | str,
    "prompts": list[Prompt]
}
```

**Prompt TypedDict**:
```python
{
    "name": str,                    # Required: prompt identifier
    "prompt": str,                  # Required: prompt text  
    "update_instructions": str,     # Optional: how to modify prompt
    "when_to_update": str          # Optional: dependencies for updates
}
```

**AnnotatedTrajectory**:
```python
AnnotatedTrajectory(
    messages=Sequence[AnyMessage],
    feedback=dict[str, str | int | bool] | str | None
)
```

Sources: [src/langmem/prompts/optimization.py:471-477](), [src/langmem/prompts/optimization.py:272-283](), [src/langmem/prompts/types.py:7-34](), [src/langmem/prompts/types.py:95-136]()

## Architecture and Code Entities

Multi-Prompt Optimization Code Structure

```mermaid
graph TB
    subgraph "create_multi_prompt_optimizer Factory"
        Factory["create_multi_prompt_optimizer()"] --> |"Returns"| MPO["MultiPromptOptimizer"]
        Factory --> |"Parameters"| Config["model, kind, config"]
    end
    
    subgraph "MultiPromptOptimizer Class"
        MPO --> |".__init__()"| Init["self._optimizer = create_prompt_optimizer()"]
        MPO --> |".ainvoke()"| AInvoke["ainvoke(MultiPromptOptimizerInput)"]
        MPO --> |".invoke()"| Invoke["invoke(MultiPromptOptimizerInput)"]
        MPO --> |".__call__()"| Call["__call__(trajectories, prompts)"]
    end
    
    subgraph "Credit Assignment Pipeline"
        AInvoke --> |"len(prompts) > 1"| ClassifySchema["Classify BaseModel"]
        ClassifySchema --> |"create_extractor()"| Extractor["create_extractor(model, tools=[Classify])"]
        Extractor --> |"classifier.ainvoke()"| Extract["Extract which prompts to update"]
        Extract --> |"result.responses[0].which"| Selection["List of prompt names"]
    end
    
    subgraph "Concurrent Optimization"
        Selection --> |"asyncio.gather()"| Gather["Concurrent prompt optimization"]
        Gather --> |"For each selected"| SingleOpt["self._optimizer.ainvoke()"]
        SingleOpt --> |"Merge results"| Results["list[Prompt]"]
    end
    
    subgraph "Underlying Strategies"
        Init --> |"kind='gradient'"| GradOpt["create_gradient_prompt_optimizer"]
        Init --> |"kind='metaprompt'"| MetaOpt["create_metaprompt_optimizer"] 
        Init --> |"kind='prompt_memory'"| MemOpt["PromptMemoryMultiple"]
    end
```

Sources: [src/langmem/prompts/optimization.py:471-616](), [src/langmem/prompts/optimization.py:272-290](), [src/langmem/prompts/optimization.py:336-373]()

## Execution Flow

MultiPromptOptimizer.ainvoke() Implementation Flow

```mermaid
flowchart TD
    subgraph "MultiPromptOptimizer.ainvoke() Method"
        Start["ainvoke(input: MultiPromptOptimizerInput)"] --> TraceStart["ls.trace('multi_prompt_optimizer.ainvoke')"]
        TraceStart --> ExtractInput["trajectories = input['trajectories']<br/>prompts = input['prompts']"]
        
        ExtractInput --> BuildChoices["choices = [p['name'] for p in prompts]"]
        BuildChoices --> FormatCheck["len(prompts) == 1 and prompts[0].get('when_to_update') is None?"]
        
        FormatCheck --> |"True"| DirectPath["updated_prompt = await self._optimizer(trajectories, prompts[0])"]
        DirectPath --> DirectReturn["Return [{...prompts[0], 'prompt': updated_prompt}]"]
        
        FormatCheck --> |"False"| MultiPath["Format sessions_str = utils.format_sessions(trajectories)"]
        MultiPath --> JoinPrompts["prompt_joined_content = join prompt names and content"]
        
        JoinPrompts --> DefineClassify["Define Classify(BaseModel) with reasoning and which fields"]
        DefineClassify --> CreateExtractor["classifier = create_extractor(self.model, tools=[Classify])"]
        
        CreateExtractor --> BuildPrompt["classification_prompt with sessions_str + prompt_joined_content"]
        BuildPrompt --> ExtractCall["result = await classifier.ainvoke(classification_prompt)"]
        
        ExtractCall --> GetToUpdate["to_update = result['responses'][0].which"]
        GetToUpdate --> FilterSelected["which_to_update = [p for p in prompts if p['name'] in to_update]"]
        
        FilterSelected --> AsyncGather["updated_results = await asyncio.gather(*[self._optimizer(trajectories, prompt=p) for p in which_to_update])"]
        AsyncGather --> BuildMap["updated_map = {p['name']: new_text for p, new_text in zip(...)}"]
        
        BuildMap --> MergeResults["Merge updated_map back into original prompts list"]
        MergeResults --> TraceEnd["rt.add_outputs({'output': final_list})"]
        TraceEnd --> Return["return final_list"]
        
        DirectReturn --> Return
    end
```

### Key Implementation Details

| Step | Code Entity | Purpose |
|------|-------------|---------|
| Input validation | `len(prompts) == 1 and prompts[0].get('when_to_update') is None` | Skip credit assignment for single prompt |
| Session formatting | `utils.format_sessions(trajectories)` | Convert trajectories to readable text |
| Credit assignment | `create_extractor(self.model, tools=[Classify])` | Use structured extraction for prompt selection |
| Concurrent optimization | `asyncio.gather(*[self._optimizer(...) for ...])` | Optimize selected prompts in parallel |
| Result merging | `{**p, "prompt": updated_map[p["name"]]}` | Preserve original prompt metadata with updated text |

Sources: [src/langmem/prompts/optimization.py:289-373](), [src/langmem/prompts/optimization.py:356-372]()

## Credit Assignment Implementation

Multi-prompt optimization uses `create_extractor()` with a `Classify` schema to determine which prompts contributed to performance issues:

Classification-Based Prompt Selection

```mermaid
flowchart TD
    subgraph "Credit Assignment in MultiPromptOptimizer.ainvoke()"
        Input["MultiPromptOptimizerInput"] --> FormatCheck["len(prompts) == 1?"]
        FormatCheck --> |"Yes & no when_to_update"| DirectOpt["Direct self._optimizer call"]
        FormatCheck --> |"No"| BuildChoices["choices = [p['name'] for p in prompts]"]
        
        BuildChoices --> FormatSessions["utils.format_sessions(trajectories)"]
        FormatSessions --> JoinPrompts["Join prompt content with names"]
        
        JoinPrompts --> CreateClassify["class Classify(BaseModel)"]
        CreateClassify --> |"reasoning: str"| ReasoningField["LLM reasoning for selection"]
        CreateClassify --> |"which: list[str]"| WhichField["Prompt names to update"]
        
        WhichField --> ModelValidator["@model_validator validates choices in available names"]
        ModelValidator --> CreateExtractor["classifier = create_extractor(model, tools=[Classify])"]
        
        CreateExtractor --> ClassificationPrompt["Generate classification prompt with trajectories + prompts"]
        ClassificationPrompt --> ExtractorCall["result = classifier.ainvoke(prompt)"]
        
        ExtractorCall --> GetSelection["to_update = result['responses'][0].which"]
        GetSelection --> FilterPrompts["which_to_update = [p for p in prompts if p['name'] in to_update]"]
    end
```

### Classify Schema Implementation

The `Classify` BaseModel schema enforces structured prompt selection:

```python
class Classify(BaseModel):
    """After analyzing the provided trajectories, determine which prompt modules (if any) contributed to degraded performance."""
    
    reasoning: str = Field(description="Reasoning for which prompts to update.")
    which: list[str] = Field(description=f"List of prompt names that should be updated. Must be among {choices}")
    
    @model_validator(mode="after")
    def validate_choices(self) -> "Classify":
        invalid = set(self.which) - set(choices)
        if invalid:
            raise ValueError(f"Invalid choices: {invalid}. Must be among: {choices}")
        return self
```

The schema ensures:
- `reasoning` field provides LLM rationale for selections
- `which` field contains only valid prompt names from the input list
- `model_validator` prevents invalid prompt name selection

Sources: [src/langmem/prompts/optimization.py:317-335](), [src/langmem/prompts/optimization.py:404-421](), [src/langmem/prompts/optimization.py:336-352]()

## Optimization Strategies

Multi-prompt optimization leverages the same underlying strategies as single-prompt optimization, applying them to selected prompts after credit assignment:

### Strategy Overview

| Strategy | Description | LLM Calls per Prompt | Best For |
|----------|-------------|---------------------|----------|
| `gradient` | Reflection-based iterative improvement | 2-10 (configurable) | Complex prompt systems with subtle interdependencies |
| `metaprompt` | Meta-learning pattern recognition | 1-5 (configurable) | Balanced speed and improvement quality |
| `prompt_memory` | Memory-based pattern application | 1 | Simple, fast updates |

### 1. Gradient Strategy (Default)

Uses `create_gradient_prompt_optimizer()` for each selected prompt:
- Separates concerns between finding areas for improvement and applying updates
- Configurable via `GradientOptimizerConfig`
- Most thorough but computationally expensive

### 2. Metaprompt Strategy

Uses `create_metaprompt_optimizer()` for each selected prompt:
- Direct prompt updates through meta-learning
- Configurable via `MetapromptOptimizerConfig`
- Moderate cost with good results

### 3. Prompt Memory Strategy

Uses `PromptMemoryMultiple()` for each selected prompt:
- Simple single-shot optimization
- No additional configuration
- Fastest option

Sources: [src/langmem/prompts/optimization.py:286-287](), [src/langmem/prompts/optimization.py:260-269]()

## Usage Examples

### Basic Multi-Prompt Optimization

```python
from langmem import create_multi_prompt_optimizer
from langmem.prompts.types import AnnotatedTrajectory

# Create optimizer with gradient strategy
optimizer = create_multi_prompt_optimizer(
    "anthropic:claude-3-5-sonnet-latest", 
    kind="gradient"
)

# Define system prompts with names and optional metadata
prompts = [
    {
        "name": "classifier",
        "prompt": "Classify user requests into technical, billing, or general categories",
        "when_to_update": "When misclassifications occur"
    },
    {
        "name": "responder", 
        "prompt": "Respond appropriately based on the classification",
        "update_instructions": "Focus on matching response tone to category"
    }
]

# Conversation with feedback using AnnotatedTrajectory
trajectory = AnnotatedTrajectory(
    messages=[
        {"role": "user", "content": "I can't log into my account"},
        {"role": "assistant", "content": "That sounds like a general inquiry..."}
    ],
    feedback={"issue": "misclassified login issue as general instead of technical"}
)

# Optimize using Runnable interface
result = await optimizer.ainvoke({
    "trajectories": [trajectory],
    "prompts": prompts
})

# Access updated prompts (preserves all original fields)
for prompt in result:
    print(f"{prompt['name']}: {prompt['prompt']}")
```

### Alternative Call Interface

The `MultiPromptOptimizer` supports direct calling via `__call__`:

```python
# Alternative calling pattern
updated_prompts = await optimizer(trajectories=[trajectory], prompts=prompts)
```

### Configuration with Different Strategies

```python
# Use metaprompt strategy with configuration
optimizer = create_multi_prompt_optimizer(
    "anthropic:claude-3-5-sonnet-latest",
    kind="metaprompt", 
    config={"max_reflection_steps": 2, "min_reflection_steps": 1}
)

# Use prompt_memory strategy (fastest, single LLM call per prompt)
optimizer = create_multi_prompt_optimizer(
    "anthropic:claude-3-5-sonnet-latest",
    kind="prompt_memory"
)
```

Sources: [src/langmem/prompts/optimization.py:539-587](), [src/langmem/prompts/optimization.py:458-468](), [src/langmem/prompts/types.py:36-60]()

## Performance Characteristics

### Computational Costs by Strategy

| Strategy | LLM Calls per Selected Prompt | Total System Cost | Best Use Case |
|----------|------------------------------|-------------------|---------------|
| `prompt_memory` | 1 | 1 + N selected prompts | Fast iterations, simple systems |
| `metaprompt` | 1-5 (configurable) | 1 + (1-5 × N selected) | Balanced performance/cost |
| `gradient` | 2-10 (configurable) | 1 + (2-10 × N selected) | Complex interdependent systems |

**Note**: All strategies require 1 additional LLM call for credit assignment via the `Classify` schema, except when optimizing a single prompt without `when_to_update`.

### Credit Assignment Bypass

Single prompts bypass credit assignment when:
```python
len(prompts) == 1 and prompts[0].get("when_to_update") is None
```

This optimization reduces costs by calling `self._optimizer` directly without classification.

### Concurrent Optimization

Selected prompts are optimized concurrently using `asyncio.gather()`:
```python
updated_results = await asyncio.gather(
    *[self._optimizer(trajectories, prompt=p) for p in which_to_update]
)
```

This parallelization reduces total execution time when multiple prompts need updates.

Sources: [src/langmem/prompts/optimization.py:312-315](), [src/langmem/prompts/optimization.py:356-359]()

## Technical Limitations

### Credit Assignment Constraints

- The `Classify` schema depends on LLM reasoning to identify problematic prompts
- Classification accuracy affects which prompts get optimized
- Complex prompt interdependencies may not be captured in credit assignment

### Concurrency and Error Handling

- `asyncio.gather()` fails fast if any individual prompt optimization fails
- No built-in retry logic for failed optimizations
- Prompt validation occurs at the `Classify` schema level, not at optimization time

### State Management

- Multi-prompt optimization is stateless - no memory of previous optimizations
- Each call requires complete trajectory and prompt context
- No built-in deduplication of similar optimization requests

### LangSmith Integration

The system includes tracing via `langsmith.trace()`:
- Traces include optimization kind and input/output metadata
- Useful for monitoring optimization patterns and costs
- Provides visibility into credit assignment decisions

Sources: [src/langmem/prompts/optimization.py:295-299](), [src/langmem/prompts/optimization.py:327-334](), [src/langmem/prompts/optimization.py:356-372]()

## Summary

Multi-prompt optimization enables coordinated improvement of interdependent prompts in complex LLM applications. By analyzing conversation threads and understanding prompt relationships, it generates consistent updates that enhance overall system performance while maintaining the integrity of prompt interactions.

---

# Page: Storage

# Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_semantic_memories.md](docs/docs/guides/extract_semantic_memories.md)
- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)

</details>



LangMem's storage system provides persistent, searchable memory management built on LangGraph's BaseStore abstraction. This system supports both development and production deployments with various storage backends, namespace organization patterns, and embedding-based search capabilities.

For detailed comparisons of specific storage implementations, see [Storage Types](#7.1). For namespace design patterns and templating, see [Namespace Organization](#7.2).

## Storage Architecture

LangMem integrates with LangGraph's storage layer through the BaseStore interface, providing a unified API for memory persistence across different storage backends:

### LangMem Storage Integration

```mermaid
graph TB
    subgraph "LangMem Components"
        MSM["MemoryStoreManager"]
        MM["MemoryManager"] 
        MT["Memory Tools"]
        MSE["create_memory_searcher"]
    end
    
    subgraph "LangGraph Storage Layer"
        BS["BaseStore Interface"]
        subgraph "Storage Implementations"
            IMS["InMemoryStore"]
            PGS["AsyncPostgresStore"]
            CS["Custom Stores"]
        end
    end
    
    subgraph "Storage Operations"
        PUT["put()"]
        GET["get()"]
        SEARCH["search()"]
        DELETE["delete()"]
    end
    
    subgraph "Data Organization"
        NS["Namespace Patterns"]
        IDX["Vector Indexing"]
        TTL["TTL Management"]
    end
    
    MSM --> BS
    MT --> BS
    MSE --> BS
    BS --> IMS
    BS --> PGS
    BS --> CS
    BS --> PUT
    BS --> GET
    BS --> SEARCH
    BS --> DELETE
    BS --> NS
    BS --> IDX
    BS --> TTL
```

Sources: [src/langmem/knowledge/extraction.py:12-23](), [src/langmem/knowledge/extraction.py:898-913]()

### Storage Flow Architecture

```mermaid
sequenceDiagram
    participant App as "Application"
    participant MSM as "MemoryStoreManager"
    participant BS as "BaseStore"
    participant EMB as "Embedding Service"
    participant DB as "Storage Backend"
    
    Note over App,DB: Memory Search & Retrieval
    App->>MSM: "search(query='user preferences')"
    MSM->>BS: "asearch(namespace, query)"
    BS->>EMB: "embed(query)"
    EMB-->>BS: "query_vector"
    BS->>DB: "vector_search()"
    DB-->>BS: "search_results"
    BS-->>MSM: "SearchItem[]"
    MSM-->>App: "coerced_results"
    
    Note over App,DB: Memory Storage
    App->>MSM: "ainvoke(messages)"
    MSM->>BS: "asearch() # find existing"
    BS-->>MSM: "existing_memories"
    MSM->>MSM: "memory_manager.ainvoke()"
    MSM->>BS: "aput(namespace, key, value)"
    BS->>EMB: "embed(content)"
    EMB-->>BS: "content_vector"
    BS->>DB: "insert/update"
    DB-->>BS: "success"
    BS-->>MSM: "success"
    MSM-->>App: "final_puts"
```

Sources: [src/langmem/knowledge/extraction.py:1006-1137](), [src/langmem/knowledge/extraction.py:1513-1578]()

## Storage Patterns

LangMem uses three main storage patterns for organizing different types of memories:

| Pattern | Use Case | Namespace Example | enable_inserts | Description |
|---------|----------|-------------------|----------------|-------------|
| **Collection** | Semantic memories, episodic memories | `("memories", "{user_id}")` | `True` | Multiple documents, searchable and updateable |
| **Profile** | User profiles, system preferences | `("profile", "{user_id}")` | `False` | Single document, in-place updates only |
| **Rules** | System instructions, behavioral guidelines | `("rules", "system")` | `False` | Static configuration, minimal updates |

Sources: [src/langmem/knowledge/extraction.py:844-846](), [src/langmem/knowledge/extraction.py:224-235]()

### Collection Pattern Example

```python
# Semantic memories - multiple facts per user
manager = create_memory_store_manager(
    "anthropic:claude-3-5-sonnet-latest",
    namespace=("memories", "{langgraph_user_id}"),
    enable_inserts=True,  # Allow new memories
    enable_deletes=True   # Allow removing outdated memories
)
```

### Profile Pattern Example

```python
# User profile - single document per user
manager = create_memory_store_manager(
    "anthropic:claude-3-5-sonnet-latest", 
    namespace=("profile", "{langgraph_user_id}"),
    enable_inserts=False,  # Only update existing profile
    enable_deletes=False   # Never delete profile
)
```

Sources: [src/langmem/knowledge/extraction.py:1666-1680](), [docs/docs/guides/extract_semantic_memories.md:138-145]()

## Namespace Organization

Namespaces provide hierarchical organization of memories using tuple-based paths:

### Namespace Template System

```mermaid
graph LR
    subgraph "Namespace Templates"
        UT["('memories', '{user_id}')"]
        TT["('team', '{team_id}', '{user_id}')"] 
        GT["('global', 'system')"]
        DT["('domain', '{project}', '{user_id}')"]
    end
    
    subgraph "Runtime Resolution"
        subgraph "User Context"
            U1["('memories', 'user-123')"]
            U2["('memories', 'user-456')"]
        end
        subgraph "Team Context" 
            T1["('team', 'eng', 'user-123')"]
            T2["('team', 'eng', 'user-456')"]
        end
        subgraph "Global Context"
            G1["('global', 'system')"]
        end
    end
    
    UT --> U1
    UT --> U2
    TT --> T1
    TT --> T2
    GT --> G1
```

### NamespaceTemplate Resolution

```python
# Template definition with placeholders
namespace_template = NamespaceTemplate(("memories", "{langgraph_user_id}"))

# Runtime resolution from config
config = {"configurable": {"langgraph_user_id": "user-123"}}
resolved = namespace_template(config)
# Result: ("memories", "user-123")
```

Sources: [src/langmem/knowledge/extraction.py:877](), [src/langmem/knowledge/extraction.py:1013](), [src/langmem/knowledge/extraction.py:1660-1663]()

## Storage Configuration

### Development Setup

```python
from langgraph.store.memory import InMemoryStore

# Development store with embedding support
store = InMemoryStore(
    index={
        "dims": 1536,  # OpenAI text-embedding-3-small
        "embed": "openai:text-embedding-3-small",
    }
)
```

### Production Setup

```python
from langgraph.store.postgres import AsyncPostgresStore

# Production store with persistent storage
store = AsyncPostgresStore(
    connection_string="postgresql://user:pass@host:5432/db",
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small", 
    }
)
```

Sources: [docs/docs/guides/extract_semantic_memories.md:132-137]()

## Memory Store Manager Integration

The `MemoryStoreManager` provides the primary interface for storage operations, automatically handling search, enrichment, and persistence:

### Store Access Pattern

```mermaid
graph LR
    subgraph "Store Resolution"
        MSM["MemoryStoreManager"]
        PROP["_store property"]
        CTX["LangGraph Context"]
        DIRECT["Direct Store Instance"]
    end
    
    MSM --> PROP
    PROP --> |"if self._store"| DIRECT
    PROP --> |"else get_store()"| CTX
    CTX --> |"RuntimeError if not configured"| ERR["ValueError"]
```

```python
@property
def store(self) -> BaseStore:
    """Get the store to use for memory storage.
    
    Returns the store provided during initialization if available,
    otherwise falls back to the store configured in the LangGraph context.
    """
    if self._store is not None:
        return self._store
    try:
        self._store = get_store()
    except RuntimeError as e:
        raise ValueError(
            "Memory Manager's store not configured in LangGraph context. "
            "First use in the graph before calling, or initialize with an instance of the store."
        ) from e
    return self._store
```

Sources: [src/langmem/knowledge/extraction.py:897-913]()

## Key Storage Operations

### Memory Enrichment Flow

1. **Search Phase**: Query existing memories by embedding similarity or direct lookup
2. **Enrichment Phase**: Process new information with LLM using existing context
3. **Persistence Phase**: Apply updates, insertions, and deletions to store
4. **Coercion Phase**: Convert stored values to appropriate Pydantic models

### Search and Retrieval

```python
# Vector search with query generation
search_results_lists = await asyncio.gather(
    *[
        store.asearch(
            namespace, **({**tc["args"], "limit": self.query_limit})
        )
        for tc in query_req.tool_calls
    ]
)
```

### Batch Operations

```python
# Parallel puts and deletes
await asyncio.gather(
    *(store.aput(**put) for put in final_puts),
    *(store.adelete(ns, key) for (ns, key) in final_deletes),
)
```

Sources: [src/langmem/knowledge/extraction.py:1022-1029](), [src/langmem/knowledge/extraction.py:1132-1135]()

The storage system provides a flexible foundation for memory management, supporting both simple development workflows and complex production deployments with proper isolation, search capabilities, and data persistence.

---

# Page: Storage Types

# Storage Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_semantic_memories.md](docs/docs/guides/extract_semantic_memories.md)
- [examples/standalone_examples/README.md](examples/standalone_examples/README.md)
- [examples/standalone_examples/custom_store_example.py](examples/standalone_examples/custom_store_example.py)

</details>



This document covers the different storage backends available in langmem for persisting memories and their characteristics. For information about organizing memories within storage using hierarchical namespaces, see [Namespace Organization](#7.2).

## Storage Architecture Overview

Langmem's storage system is built on LangGraph's `BaseStore` interface, providing a flexible abstraction that supports multiple backend implementations. The system separates the core memory processing logic from storage concerns, allowing you to choose the appropriate backend based on your deployment requirements.

### Storage Backend Architecture

```mermaid
graph TB
    subgraph "LangMem Core"
        MM["create_memory_manager()"]
        MSM["create_memory_store_manager()"]
        Tools["Memory Tools"]
    end
    
    subgraph "Storage Abstraction Layer"
        BaseStore["BaseStore Interface"]
        Operations["get() / put() / search() / delete()"]
    end
    
    subgraph "Storage Backends"
        InMemory["InMemoryStore"]
        Postgres["AsyncPostgresStore"]
        Platform["LangGraph Platform Store"]
    end
    
    subgraph "Use Cases"
        Development["Development & Testing"]
        Production["Production Deployment"]
        Managed["Managed Platform"]
    end
    
    MM --> BaseStore
    MSM --> BaseStore
    Tools --> BaseStore
    
    BaseStore --> Operations
    Operations --> InMemory
    Operations --> Postgres
    Operations --> Platform
    
    InMemory --> Development
    Postgres --> Production
    Platform --> Managed
```

**Sources:** [docs/docs/concepts/conceptual_guide.md:341-376]()

## InMemoryStore

The `InMemoryStore` is designed for development, testing, and prototyping scenarios where persistence across application restarts is not required. It provides fast, local memory storage that mirrors the full `BaseStore` interface.

### Characteristics

| Feature | InMemoryStore |
|---------|---------------|
| **Persistence** | Session-only (lost on restart) |
| **Performance** | Fastest (no I/O overhead) |
| **Setup Complexity** | None (no dependencies) |
| **Use Cases** | Development, testing, demos |
| **Scalability** | Limited to single process |

### When to Use InMemoryStore

- **Development Environment**: Rapid iteration without database setup
- **Testing**: Unit tests and integration tests requiring clean state
- **Prototyping**: Quick demonstrations and proof-of-concept applications
- **CI/CD**: Automated testing pipelines where ephemeral storage is sufficient

**Sources:** [docs/docs/concepts/conceptual_guide.md:341-376]()

## PostgresStore

The `AsyncPostgresStore` provides production-ready persistent storage with full ACID compliance and advanced search capabilities. It's designed for applications requiring durable memory storage and concurrent access.

### Characteristics

| Feature | AsyncPostgresStore |
|---------|-------------------|
| **Persistence** | Full ACID durability |
| **Performance** | Optimized for concurrent access |
| **Setup Complexity** | Requires PostgreSQL instance |
| **Use Cases** | Production applications |
| **Scalability** | Horizontal scaling support |

### Production Considerations

- **Connection Management**: Supports connection pooling for high-concurrency scenarios
- **Schema Management**: Automatically handles table creation and migrations
- **Search Capabilities**: Leverages PostgreSQL's full-text search and vector similarity
- **Backup & Recovery**: Standard PostgreSQL backup procedures apply

**Sources:** [docs/docs/concepts/conceptual_guide.md:341-376]()

## LangGraph Platform Store

The LangGraph Platform provides a managed storage solution that handles infrastructure concerns while offering the same `BaseStore` interface. This option is ideal for cloud deployments where you want to focus on application logic rather than storage management.

### Platform Integration

```mermaid
graph TB
    subgraph "LangGraph Platform"
        PlatformStore["Platform Store"]
        Management["Managed Infrastructure"]
        Scaling["Auto-scaling"]
        Monitoring["Built-in Monitoring"]
    end
    
    subgraph "Application Layer"
        LangMemApp["LangMem Application"]
        MemoryOps["Memory Operations"]
        Namespaces["Namespace Management"]
    end
    
    subgraph "Storage Features"
        Persistence["Persistent Storage"]
        Search["Semantic Search"]
        Backup["Automated Backup"]
        Security["Access Control"]
    end
    
    LangMemApp --> MemoryOps
    MemoryOps --> Namespaces
    Namespaces --> PlatformStore
    
    PlatformStore --> Management
    Management --> Scaling
    Management --> Monitoring
    
    PlatformStore --> Persistence
    PlatformStore --> Search
    PlatformStore --> Backup
    PlatformStore --> Security
```

### Platform Benefits

- **Zero Infrastructure Management**: No database setup or maintenance required
- **Built-in Monitoring**: Automatic performance metrics and alerting
- **Security**: Enterprise-grade access controls and encryption
- **Scalability**: Automatic scaling based on application demands

**Sources:** [docs/docs/concepts/conceptual_guide.md:341-376]()

## BaseStore Interface

The `BaseStore` interface provides a unified API across all storage backends, ensuring that memory operations work consistently regardless of the underlying storage implementation.

### Core Operations

```mermaid
graph LR
    subgraph "BaseStore Interface"
        Get["get(namespace, key)"]
        Put["put(namespace, key, value)"]
        Search["search(namespace, query)"]
        Delete["delete(namespace, key)"]
        List["list(namespace)"]
    end
    
    subgraph "Storage Implementations"
        InMemoryImpl["InMemoryStore"]
        PostgresImpl["AsyncPostgresStore"]
        PlatformImpl["Platform Store"]
    end
    
    Get --> InMemoryImpl
    Get --> PostgresImpl
    Get --> PlatformImpl
    
    Put --> InMemoryImpl
    Put --> PostgresImpl
    Put --> PlatformImpl
    
    Search --> InMemoryImpl
    Search --> PostgresImpl
    Search --> PlatformImpl
    
    Delete --> InMemoryImpl
    Delete --> PostgresImpl
    Delete --> PlatformImpl
    
    List --> InMemoryImpl
    List --> PostgresImpl
    List --> PlatformImpl
```

### Interface Methods

| Method | Purpose | Parameters |
|--------|---------|------------|
| `get()` | Retrieve specific memory by key | `namespace`, `key` |
| `put()` | Store or update memory | `namespace`, `key`, `value` |
| `search()` | Find memories by semantic similarity | `namespace`, `query`, `limit`, `filter` |
| `delete()` | Remove memory | `namespace`, `key` |
| `list()` | List all memories in namespace | `namespace`, `prefix` |

**Sources:** [docs/docs/concepts/conceptual_guide.md:370-376]()

## Storage Selection Guide

Choose the appropriate storage backend based on your deployment requirements and application lifecycle stage:

### Decision Matrix

```mermaid
flowchart TD
    Start["Choose Storage Backend"] --> DevOrProd{"Development or Production?"}
    
    DevOrProd -->|Development| DevNeeds{"Need Persistence?"}
    DevOrProd -->|Production| ProdNeeds{"Self-managed or Managed?"}
    
    DevNeeds -->|No| InMemory["InMemoryStore<br/>• Fast setup<br/>• No dependencies<br/>• Session-only"]
    DevNeeds -->|Yes| LocalPG["Local PostgresStore<br/>• Full persistence<br/>• Production-like testing"]
    
    ProdNeeds -->|Self-managed| PostgresProd["AsyncPostgresStore<br/>• Full control<br/>• Custom scaling<br/>• Own infrastructure"]
    ProdNeeds -->|Managed| Platform["LangGraph Platform<br/>• Zero maintenance<br/>• Built-in scaling<br/>• Enterprise features"]
```

### Selection Criteria

| Criteria | InMemoryStore | AsyncPostgresStore | Platform Store |
|----------|---------------|-------------------|----------------|
| **Setup Time** | Immediate | Moderate | Fast |
| **Operational Overhead** | None | High | None |
| **Cost** | Free | Infrastructure costs | Service fees |
| **Scalability** | Limited | Manual scaling | Auto-scaling |
| **Persistence** | None | Full | Full |
| **Performance** | Fastest | Good | Good |
| **Suitable For** | Development, testing | Production, self-hosted | Production, managed |

**Sources:** [docs/docs/concepts/conceptual_guide.md:341-376]()

---

# Page: Namespace Organization

# Namespace Organization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/guides/extract_semantic_memories.md](docs/docs/guides/extract_semantic_memories.md)
- [src/langmem/utils.py](src/langmem/utils.py)

</details>



This document covers the hierarchical organization and dynamic namespace resolution system in langmem. Namespaces provide a way to organize memories by user, team, project, or other organizational units, enabling multi-tenancy and access control within the memory system.

For information about different storage backends that use these namespaces, see [Storage Types](#7.1). For details on how tools use namespaces to organize memory operations, see [Using Namespaces](#5.3).

## NamespaceTemplate System

The core of langmem's namespace organization is the `NamespaceTemplate` class, which provides dynamic namespace resolution based on runtime configuration. This system allows namespace patterns to be defined once and resolved differently for each user, team, or context.

### Template Structure and Resolution

```mermaid
graph TB
    Template[NamespaceTemplate] --> Parser["_get_key()"]
    Parser --> Variables["Variables Map"]
    Parser --> StaticParts["Static Parts"]
    
    Config["RunnableConfig"] --> Configurable["configurable field"]
    Configurable --> UserContext["user_id, team_id, etc."]
    
    Template --> Call["__call__()"]
    Call --> Variables
    Call --> UserContext
    Call --> ResolvedNamespace["Resolved Namespace Tuple"]
    
    ResolvedNamespace --> UserMem["('memories', 'alice')"]
    ResolvedNamespace --> TeamMem["('team', 'team_123')"]
    ResolvedNamespace --> GlobalMem["('global',)"]
```

Sources: [src/langmem/utils.py:15-96]()

### Dynamic Variable Substitution

The `NamespaceTemplate` class extracts variables from template strings using curly brace notation and substitutes them with values from the runtime configuration:

```mermaid
flowchart TD
    Input["Template: ('org', '{user_id}', '{project}')"] --> Extract["_get_key() extraction"]
    Extract --> VarMap["vars = {1: 'user_id', 2: 'project'}"]
    
    RuntimeConfig["RunnableConfig"] --> Configurable["configurable: {'user_id': 'alice', 'project': 'proj_1'}"]
    
    VarMap --> Resolve["__call__() resolution"]
    Configurable --> Resolve
    Resolve --> Output["('org', 'alice', 'proj_1')"]
    
    ErrorPath["Missing Keys"] --> ConfigError["ConfigurationError"]
    Resolve --> ErrorPath
```

Sources: [src/langmem/utils.py:67-91]()

## Common Namespace Patterns

Based on actual usage patterns in the codebase, langmem supports several standard namespace patterns for organizing different types of memories:

| Pattern | Template | Example Resolution | Use Case |
|---------|----------|-------------------|----------|
| User Semantic Memory | `("chat", "{user_id}", "triples")` | `("chat", "user_123", "triples")` | User-specific semantic facts |
| User Preferences | `("chat", "{user_id}", "preferences")` | `("chat", "user_123", "preferences")` | Personal preferences and settings |
| Team Knowledge | `("chat", "team_{team_id}", "triples")` | `("chat", "team_x", "triples")` | Shared team knowledge base |
| Global Memory | `("chat", "global", "triples")` | `("chat", "global", "triples")` | System-wide facts and rules |
| Simple Memory Store | `("memories",)` | `("memories",)` | Basic memory collection |
| Hierarchical | `("org", "{team_id}", "{user_id}")` | `("org", "eng", "alice")` | Multi-level organization |

Sources: [docs/docs/guides/extract_semantic_memories.md:140-162]()

## Configuration Integration

The namespace system integrates with LangGraph's configuration system to automatically resolve variables from the runtime context:

```mermaid
sequenceDiagram
    participant Agent
    participant NamespaceTemplate
    participant LangGraphConfig as "get_config()"
    participant ConfigurableField as "configurable"
    participant ResolvedNamespace as "Resolved Namespace"
    
    Agent->>NamespaceTemplate: template = ("user", "{user_id}")
    Agent->>NamespaceTemplate: ns()
    NamespaceTemplate->>LangGraphConfig: get_config()
    LangGraphConfig->>ConfigurableField: extract configurable
    ConfigurableField-->>NamespaceTemplate: {"user_id": "alice"}
    NamespaceTemplate->>ResolvedNamespace: ("user", "alice")
    ResolvedNamespace-->>Agent: namespace tuple
```

Sources: [src/langmem/utils.py:73-77]()

## Error Handling and Validation

The namespace system includes comprehensive error handling for missing configuration keys:

```mermaid
graph TD
    Resolution["Namespace Resolution"] --> CheckVars["Check Variables"]
    CheckVars --> HasVars{"Has Variables?"}
    
    HasVars -->|No| DirectReturn["Return Static Template"]
    HasVars -->|Yes| ExtractConfig["Extract Configurable"]
    
    ExtractConfig --> CheckKeys["Check Required Keys"]
    CheckKeys --> AllPresent{"All Keys Present?"}
    
    AllPresent -->|Yes| Substitute["Substitute Variables"]
    AllPresent -->|No| ConfigError["ConfigurationError"]
    
    ConfigError --> ErrorMessage["Missing key in 'configurable' field"]
    Substitute --> ResolvedTuple["Resolved Namespace Tuple"]
```

Sources: [src/langmem/utils.py:78-89]()

## Integration with Storage Systems

Namespaces are used throughout the langmem system to organize memory storage and retrieval operations:

```mermaid
graph TB
    subgraph "Memory Tools"
        create_manage_memory_tool["create_manage_memory_tool"]
        create_search_memory_tool["create_search_memory_tool"]
    end
    
    subgraph "Memory Managers"
        create_memory_store_manager["create_memory_store_manager"]
        MemoryStoreManager["MemoryStoreManager"]
    end
    
    subgraph "Storage Layer"
        BaseStore["BaseStore"]
        InMemoryStore["InMemoryStore"]
        AsyncPostgresStore["AsyncPostgresStore"]
    end
    
    subgraph "Namespace Resolution"
        NamespaceTemplate["NamespaceTemplate"]
        get_config["get_config()"]
        RunnableConfig["RunnableConfig"]
    end
    
    create_manage_memory_tool --> NamespaceTemplate
    create_search_memory_tool --> NamespaceTemplate
    create_memory_store_manager --> NamespaceTemplate
    
    MemoryStoreManager --> BaseStore
    
    NamespaceTemplate --> get_config
    get_config --> RunnableConfig
    
    BaseStore --> InMemoryStore
    BaseStore --> AsyncPostgresStore
    
    InMemoryStore --> chat_user_triples["('chat', 'user_123', 'triples')"]
    AsyncPostgresStore --> memories_namespace["('memories',)"]
```

Sources: [src/langmem/utils.py:15-96](), [docs/docs/guides/extract_semantic_memories.md:125-146]()

## Usage Examples

### Basic Static Namespace

```python
# Fixed namespace - no variables
ns = NamespaceTemplate("global_knowledge")
resolved = ns()  # Returns: ('global_knowledge',)
```

### Dynamic User-Specific Namespace

```python
# Variable namespace for user-specific memories
ns = NamespaceTemplate(("memories", "{user_id}"))
resolved = ns({"configurable": {"user_id": "alice"}})  # Returns: ('memories', 'alice')
```

### Multi-Level Hierarchical Namespace

```python
# Complex hierarchical organization
ns = NamespaceTemplate(("org", "{team_id}", "{project_id}", "{user_id}"))
config = {
    "configurable": {
        "team_id": "engineering",
        "project_id": "langmem",
        "user_id": "alice"
    }
}
resolved = ns(config)  # Returns: ('org', 'engineering', 'langmem', 'alice')
```

Sources: [src/langmem/utils.py:22-53]()

---

# Page: Examples and Tutorials

# Examples and Tutorials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/hot_path_quickstart.md](docs/docs/hot_path_quickstart.md)
- [examples/standalone_examples/README.md](examples/standalone_examples/README.md)
- [examples/standalone_examples/custom_store_example.py](examples/standalone_examples/custom_store_example.py)

</details>



This document provides practical examples and tutorials demonstrating LangMem in action across different use cases and integration patterns. Examples range from hot path agent-driven memory management to standalone applications, showing how to implement the core concepts covered in [Key Concepts](#1.2) and [Processing Approaches](#3).

For detailed API usage, see [API Reference](#9). For framework-specific integration details, see [Integration](#4).

## Example Categories and Use Cases

The examples demonstrate LangMem's flexibility across different processing approaches and integration patterns:

```mermaid
graph TB
    subgraph "Example Categories"
        subgraph "Hot Path Examples"
            HQ["Hot Path Quickstart<br/>create_react_agent + tools"]
            AT["Agent Tools Examples<br/>create_manage_memory_tool<br/>create_search_memory_tool"]
        end
        
        subgraph "Background Processing Examples"
            BQ["Background Quickstart<br/>create_memory_store_manager<br/>ReflectionExecutor"]
            SC["Subconscious Memory<br/>Deferred processing"]
        end
        
        subgraph "Standalone Examples"
            CSE["custom_store_example.py<br/>InMemoryStore integration"]
            PSE["Persistent Store Examples<br/>AsyncPostgresStore"]
        end
        
        subgraph "Testing Examples"
            UT["Unit Test Patterns<br/>Memory validation"]
            IT["Integration Tests<br/>End-to-end flows"]
        end
    end
    
    subgraph "Core Functions Demonstrated"
        CMM["create_memory_manager<br/>Core extraction"]
        CMSM["create_memory_store_manager<br/>Stateful operations"]
        CMMT["create_manage_memory_tool<br/>Agent memory tools"]
        CSMT["create_search_memory_tool<br/>Memory retrieval"]
    end
    
    subgraph "Integration Patterns"
        LG["LangGraph Integration<br/>BaseStore + MemorySaver"]
        SA["Standalone Applications<br/>Custom store setup"]
        CA["Custom Agents<br/>Direct tool usage"]
    end
    
    HQ --> CMMT
    HQ --> CSMT
    HQ --> LG
    AT --> CMMT
    AT --> CSMT
    
    BQ --> CMSM
    BQ --> LG
    SC --> CMSM
    
    CSE --> CMM
    CSE --> SA
    PSE --> CMSM
    
    UT --> CMM
    UT --> CMSM
    IT --> LG
    
    style HQ fill:#e1f5fe
    style CSE fill:#f3e5f5
    style BQ fill:#e8f5e8
```

Sources: [docs/docs/hot_path_quickstart.md](), [examples/standalone_examples/README.md](), [examples/standalone_examples/custom_store_example.py]()

## Hot Path Agent Examples

### LangGraph ReAct Agent with Memory Tools

The primary hot path example demonstrates agent-driven memory management using `create_react_agent` with memory tools:

```mermaid
graph LR
    subgraph "Hot Path Agent Architecture"
        RA["create_react_agent<br/>anthropic:claude-3-5-sonnet-latest"]
        PT["prompt function<br/>System message + memories"]
        CMMT_tool["create_manage_memory_tool<br/>namespace=('memories',)"]
        CSMT_tool["create_search_memory_tool<br/>Memory retrieval"]
    end
    
    subgraph "LangGraph Infrastructure"
        IMS["InMemoryStore<br/>index: openai:text-embedding-3-small"]
        MS["MemorySaver<br/>Conversation checkpointing"]
        GS["get_store()<br/>Context access"]
    end
    
    subgraph "Runtime Flow"
        UC["User Input<br/>messages"]
        MT["Memory Tools<br/>manage_memory calls"]
        SR["Store Operations<br/>search + put/delete"]
        AR["Agent Response<br/>With memory context"]
    end
    
    RA --> PT
    RA --> CMMT_tool
    RA --> CSMT_tool
    
    PT --> GS
    GS --> IMS
    CMMT_tool --> IMS
    CSMT_tool --> IMS
    
    UC --> RA
    RA --> MT
    MT --> SR
    SR --> IMS
    IMS --> AR
    
    style RA fill:#e1f5fe
    style IMS fill:#f3e5f5
```

Key implementation details from [docs/docs/hot_path_quickstart.md:35-90]():

- **Agent Creation**: Uses `create_react_agent` with memory tools in the tools list
- **Store Configuration**: `InMemoryStore` with OpenAI embeddings for development
- **Memory Tools**: `create_manage_memory_tool` allows create/update/delete operations
- **Context Access**: `get_store()` retrieves the configured store in the prompt function
- **Namespace Organization**: `("memories",)` namespace for shared memories

### Memory Persistence Across Conversations

The example demonstrates cross-thread memory access using different `thread_id` values in the config:

```mermaid
sequenceDiagram
    participant U1 as "User (thread-a)"
    participant A as "Agent"
    participant MT as "manage_memory tool"
    participant S as "InMemoryStore"
    participant U2 as "User (thread-b)"
    
    Note over U1,U2: Thread A - Initial Memory Formation
    U1->>A: "dark. Remember that."
    A->>MT: Call manage_memory tool
    MT->>S: Store preference in ("memories",)
    S-->>MT: Memory stored with ID
    MT-->>A: Tool execution result
    A-->>U1: "I'll remember your preference"
    
    Note over U1,U2: Thread B - Memory Retrieval
    U2->>A: "Do you remember me? What are my preferences?"
    A->>S: Search ("memories",) namespace
    S-->>A: Retrieved dark mode preference
    A-->>U2: "Based on my memory search, you prefer dark display mode"
```

Sources: [docs/docs/hot_path_quickstart.md:128-169]()

## Standalone Examples

### Custom Store Integration

The standalone examples show LangMem usage outside LangGraph's context management:

Key components from [examples/standalone_examples/custom_store_example.py:19-48]():

- **Custom Schema**: `PreferenceMemory` Pydantic model for structured memory storage
- **Store Creation**: `InMemoryStore` with OpenAI embedding configuration
- **Manager Setup**: `create_memory_store_manager` with custom store parameter
- **Config Pattern**: `{"configurable": {"langgraph_user_id": "user123"}}` for namespace templating

### Memory Schema Patterns

```mermaid
graph TB
    subgraph "Memory Schema Examples"
        PM["PreferenceMemory<br/>category: str<br/>preference: str<br/>context: str"]
        TM["Triple<br/>subject: str<br/>predicate: str<br/>object: str"]
        EM["Episode<br/>context: str<br/>lessons: List[str]"]
    end
    
    subgraph "Storage Patterns"
        CP["Collection Pattern<br/>enable_inserts=True<br/>Multiple documents"]
        PP["Profile Pattern<br/>enable_inserts=False<br/>Single document updates"]
    end
    
    subgraph "Namespace Templates"
        UN["User Namespaces<br/>('project', '{langgraph_user_id}')"]
        ON["Organization Namespaces<br/>('memories', '{org_id}', '{user_id}')"]
        TN["Type Namespaces<br/>('memories', '{user_id}', 'preferences')"]
    end
    
    PM --> CP
    TM --> CP
    EM --> CP
    
    CP --> UN
    PP --> UN
    CP --> ON
    PP --> TN
    
    style PM fill:#e1f5fe
    style CP fill:#f3e5f5
```

Sources: [examples/standalone_examples/custom_store_example.py:19-24]()

## Integration Patterns and Code Entities

### Core Function Usage Patterns

Different integration scenarios use different combinations of LangMem's core functions:

| Integration Type | Core Functions | Store Management | Context |
|------------------|----------------|------------------|---------|
| **Hot Path Agents** | `create_manage_memory_tool`, `create_search_memory_tool` | LangGraph `BaseStore` | Agent tools in `create_react_agent` |
| **Background Processing** | `create_memory_store_manager`, `ReflectionExecutor` | LangGraph `BaseStore` | Deferred processing |
| **Standalone Applications** | `create_memory_manager`, `create_memory_store_manager` | Custom `BaseStore` | Manual store management |
| **Custom Agents** | `create_manage_memory_tool` + direct invocation | Any `BaseStore` | Manual tool integration |

### Memory Manager Function Mapping

```mermaid
graph TB
    subgraph "Function Categories"
        subgraph "Core API (Stateless)"
            CMM["create_memory_manager<br/>Memory extraction only"]
            CPO["create_prompt_optimizer<br/>Prompt refinement"]
            CTE["create_thread_extractor<br/>Conversation analysis"]
            SM["summarize_messages<br/>Context compression"]
        end
        
        subgraph "Stateful Integration"
            CMSM["create_memory_store_manager<br/>Store + extract + update"]
            CMMT["create_manage_memory_tool<br/>Agent memory operations"]
            CSMT["create_search_memory_tool<br/>Agent memory search"]
        end
        
        subgraph "Background Processing"
            RE["ReflectionExecutor<br/>Deferred memory processing"]
        end
    end
    
    subgraph "Example Usage Context"
        HPA["Hot Path Agents<br/>docs/hot_path_quickstart.md"]
        BPA["Background Processing<br/>ReflectionExecutor usage"]
        SAE["Standalone Examples<br/>examples/standalone_examples/"]
    end
    
    CMMT --> HPA
    CSMT --> HPA
    
    CMSM --> BPA
    RE --> BPA
    
    CMM --> SAE
    CMSM --> SAE
    
    style CMMT fill:#e1f5fe
    style CMSM fill:#f3e5f5
    style RE fill:#e8f5e8
```

### Store and Configuration Patterns

Examples demonstrate different store setup and configuration approaches:

**Development Setup** ([docs/docs/hot_path_quickstart.md:66-71]()):
```python
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)
```

**Standalone Setup** ([examples/standalone_examples/custom_store_example.py:26-33]()):
```python
def create_store():
    return InMemoryStore(
        index={
            "dims": 1536,
            "embed": "openai:text-embedding-3-small",
        }
    )
```

**Namespace Configuration** ([docs/docs/hot_path_quickstart.md:82](), [examples/standalone_examples/custom_store_example.py:45]()):
- Fixed namespaces: `namespace=("memories",)`
- Templated namespaces: `namespace=("project", "{langgraph_user_id}")`
- Config resolution: `config={"configurable": {"langgraph_user_id": "user123"}}`

Sources: [docs/docs/hot_path_quickstart.md](), [examples/standalone_examples/custom_store_example.py](), [examples/standalone_examples/README.md]()

## Example Directory Structure

The codebase provides examples in multiple locations:

- **Documentation Examples**: [docs/docs/hot_path_quickstart.md]() - Complete walkthrough examples
- **Standalone Examples**: [examples/standalone_examples/]() - Independent usage patterns  
- **Test Examples**: Referenced in [Testing and Development Examples](#8.2)

Each example category serves different learning objectives:
- **Hot Path**: Agent-driven memory management with LangGraph
- **Standalone**: LangMem integration without LangGraph context
- **Background**: Deferred memory processing patterns
- **Testing**: Validation and development patterns

Sources: [examples/standalone_examples/README.md:1-72]()

---

# Page: Standalone Examples

# Standalone Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/standalone_examples/README.md](examples/standalone_examples/README.md)
- [examples/standalone_examples/custom_store_example.py](examples/standalone_examples/custom_store_example.py)

</details>



## Purpose and Scope

This document covers examples demonstrating how to use LangMem independently of LangGraph's integrated context and state management. These examples show how to integrate LangMem into custom applications and frameworks using your own storage backends and configuration.

For information about integrating LangMem with LangGraph's built-in state management, see [LangGraph Integration](#4.1). For general agent integration patterns, see [Agent Integration](#4.2).

## Overview

The standalone examples demonstrate LangMem's flexibility as a memory management library that can work outside of LangGraph's ecosystem. The primary focus is on showing how to:

- Use custom storage backends with memory managers
- Define structured memory schemas using Pydantic models
- Process conversations and extract memories without LangGraph context
- Retrieve and work with stored memories programmatically

## Custom Store Example Architecture

The main example demonstrates using `InMemoryStore` with a custom `PreferenceMemory` schema:

```mermaid
graph TD
    App["Custom Application"] --> Manager["create_memory_store_manager"]
    Manager --> Store["InMemoryStore"]
    Manager --> Schema["PreferenceMemory"]
    Manager --> LLM["openai:gpt-4o-mini"]
    
    Store --> Embeddings["OpenAI Embeddings<br/>text-embedding-3-small"]
    Schema --> Validation["Pydantic Validation"]
    
    Conversation["User Conversation"] --> Manager
    Manager --> Processing["Memory Processing"]
    Processing --> Storage["Memory Storage"]
    Processing --> Retrieval["Memory Retrieval"]
    
    Storage --> Store
    Retrieval --> Store
    
    Store --> Namespace["Namespace<br/>('project', 'user123')"]
```

*Sources: [examples/standalone_examples/custom_store_example.py:1-75]()*

## Memory Processing Flow

The custom store example follows this processing pattern:

```mermaid
sequenceDiagram
    participant App as "Custom Application"
    participant Manager as "create_memory_store_manager"
    participant Store as "InMemoryStore"
    participant LLM as "OpenAI GPT-4o-mini"
    participant Schema as "PreferenceMemory"
    
    App->>Manager: "Initialize with custom store"
    Manager->>Store: "Configure with embeddings"
    
    App->>Manager: "Process conversation messages"
    Manager->>LLM: "Extract structured memories"
    LLM->>Schema: "Validate against Pydantic model"
    Schema->>Manager: "Return structured memory"
    Manager->>Store: "Store in namespace"
    
    App->>Store: "Search for memories"
    Store->>App: "Return memory results"
```

*Sources: [examples/standalone_examples/custom_store_example.py:36-75]()*

## Example Implementation Details

### Memory Schema Definition

The example defines a custom Pydantic model for user preferences:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `PreferenceMemory` | Structure for user preferences | Pydantic model with `category`, `preference`, and `context` fields |
| Schema validation | Ensure memory consistency | Built-in Pydantic validation |
| Memory typing | Enable structured retrieval | Used by `create_memory_store_manager` |

*Sources: [examples/standalone_examples/custom_store_example.py:19-24]()*

### Store Configuration

The custom store setup uses OpenAI embeddings:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| `dims` | 1536 | Embedding dimensions for OpenAI model |
| `embed` | `openai:text-embedding-3-small` | Embedding model for semantic search |
| Store type | `InMemoryStore` | Development/testing storage backend |

*Sources: [examples/standalone_examples/custom_store_example.py:26-33]()*

### Memory Manager Initialization

The `create_memory_store_manager` function is configured with:

| Parameter | Value | Purpose |
|-----------|--------|---------|
| `model` | `openai:gpt-4o-mini` | LLM for memory extraction |
| `schemas` | `[PreferenceMemory]` | Available memory types |
| `namespace` | `("project", "{langgraph_user_id}")` | Memory organization pattern |
| `store` | Custom `InMemoryStore` | Storage backend |

*Sources: [examples/standalone_examples/custom_store_example.py:42-47]()*

## Running the Examples

### Setup Requirements

The examples require specific dependencies and configuration:

```bash
uv venv
source .venv/bin/activate
uv sync
export OPENAI_API_KEY=your_api_key_here
```

### Execution Process

Examples can be run directly from the standalone examples directory:

```bash
cd examples/standalone_examples
uv run custom_store_example.py
```

*Sources: [examples/standalone_examples/README.md:19-38]()*

## Available Examples

### Current Examples

| Example | File | Purpose |
|---------|------|---------|
| Custom Store | `custom_store_example.py` | Using custom `InMemoryStore` with memory manager |

### Future Examples

The following examples are planned for future releases:

| Example | Purpose |
|---------|---------|
| Persistent Store | Using persistent storage backends |
| Multi-User Memory | Managing memories across multiple users |
| Memory Migration | Moving memories between different stores |

*Sources: [examples/standalone_examples/README.md:11-15]()*

## Key Learning Outcomes

These examples demonstrate several important concepts:

### Independence from LangGraph Context

The examples show how LangMem can operate without LangGraph's integrated state management, making it suitable for:

- Custom application frameworks
- Non-LangGraph agent systems
- Direct integration with existing applications

### Custom Storage Integration

The examples demonstrate how to:

- Configure custom storage backends
- Set up embedding models for semantic search
- Organize memories using namespace patterns

### Memory Processing Patterns

The examples illustrate:

- Structured memory extraction using Pydantic schemas
- Conversation processing workflows
- Memory retrieval and search operations

*Sources: [examples/standalone_examples/README.md:60-65]()*

## Technical Considerations

### API Key Requirements

The examples use OpenAI's embedding model (`text-embedding-3-small`) and require appropriate API access for both:

- Memory extraction via `gpt-4o-mini`
- Semantic search via embedding generation

### Storage Backend Selection

The examples use `InMemoryStore` for demonstration purposes. Production applications should consider:

- Persistent storage for data durability
- Distributed storage for scalability
- Security considerations for memory access

### Namespace Organization

The examples use the namespace pattern `("project", "{langgraph_user_id}")` to demonstrate:

- Memory isolation between users
- Hierarchical organization
- Dynamic namespace resolution

*Sources: [examples/standalone_examples/README.md:67-71]()*

---

# Page: Testing and Development Examples

# Testing and Development Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/short_term/__init__.py](tests/short_term/__init__.py)
- [tests/short_term/test_summarization.py](tests/short_term/test_summarization.py)
- [tests/test_docstring_examples.py](tests/test_docstring_examples.py)

</details>



This page documents testing patterns and development practices from the LangMem test suite. These examples demonstrate proper usage patterns for testing memory systems, mock implementations, and validation approaches for stateful components.

For standalone usage examples, see [Standalone Examples](#8.1).

## Testing Architecture Overview

LangMem employs a comprehensive testing strategy with unit tests for core components, docstring example validation, and mock implementations for LLM interactions. The testing framework handles the asynchronous and stateful nature of memory operations.

**LangMem Testing Framework Architecture**
```mermaid
graph TB
    subgraph "Test Organization"
        UnitTests[test_summarization.py]
        DocTests[test_docstring_examples.py]
        MockUtils[tests/short_term/utils.py]
    end
    
    subgraph "Mock Components"
        FakeChatModel[FakeChatModel]
        TestStore[InMemoryStore]
        MockLLM[Mock LLM Responses]
    end
    
    subgraph "Test Targets"
        summarize_messages[summarize_messages]
        SummarizationNode[SummarizationNode]
        RunningSummary[RunningSummary]
        DocstringExamples[Docstring Code Blocks]
    end
    
    UnitTests --> FakeChatModel
    UnitTests --> summarize_messages
    UnitTests --> SummarizationNode
    DocTests --> DocstringExamples
    FakeChatModel --> MockLLM
    
    style UnitTests fill:#e1f5fe
    style DocTests fill:#f3e5f5
    style FakeChatModel fill:#e8f5e8
```

Sources: [tests/short_term/test_summarization.py:1-14](), [tests/test_docstring_examples.py:1-19]()

### Notebook Locations

| Notebook Name | Location | Primary Concepts |
|---------------|----------|------------------|
| Semantic Memory | examples/intro_videos/semantic_memory.ipynb | User information, facts, search capabilities |
| Procedural Memory | examples/intro_videos/procedural_memory.ipynb | System instructions, prompt optimization |

Sources: [examples/intro_videos/semantic_memory.ipynb:1-10](), [examples/intro_videos/procedural_memory.ipynb:1-10]()

## Semantic Memory Notebook

The Semantic Memory notebook demonstrates how to create, store, and retrieve factual information about users or domains. This notebook shows multiple approaches to memory management, from basic implementations to more sophisticated pattern matching.

### Key Demonstrations

1. **Basic Agent Setup**: Creating a ReAct agent without memory
2. **Adding Memory Tools**: Implementing memory capabilities with LangMem tools
3. **User-Specific Namespaces**: Creating separate memory spaces for different users
4. **Eager Memory Retrieval**: Implementing efficient memory access patterns

```mermaid
flowchart TB
    subgraph "Semantic Memory Notebook Flow"
        Start["Initial Agent Setup"]
        MemTools["Add Memory Tools"]
        UserInteract["User Interaction"]
        StoreMemory["Store Memories"]
        RetrieveMemory["Retrieve Memories"]
        UserNamespaces["User-Specific Namespaces"]
        EagerRetrieval["Eager Memory Retrieval"]
    end
    
    Start --> MemTools
    MemTools --> UserInteract
    UserInteract --> StoreMemory
    StoreMemory --> RetrieveMemory
    RetrieveMemory --> UserNamespaces
    UserNamespaces --> EagerRetrieval
    
    subgraph "Code Components"
        create_manage_memory_tool["create_manage_memory_tool()"]
        create_search_memory_tool["create_search_memory_tool()"]
        InMemoryStore["InMemoryStore"]
        chat_function["chat() function"]
    end
    
    MemTools --> create_manage_memory_tool
    MemTools --> create_search_memory_tool
    MemTools --> InMemoryStore
    UserInteract --> chat_function
```

Sources: [examples/intro_videos/semantic_memory.ipynb:127-132](), [examples/intro_videos/semantic_memory.ipynb:149-162](), [examples/intro_videos/semantic_memory.ipynb:52-56]()

### Implementation Examples

The notebook includes several practical examples:

1. **Marathon Training Plan**: A conversational example where an agent creates and later references a training plan
2. **Multi-User Memory**: Demonstration of maintaining separate memories for different users (User-A and User-B)
3. **Memory Retrieval Optimization**: Implementation of an "eager" memory retrieval pattern to improve response quality

```mermaid
graph TD
    subgraph "Semantic Memory Implementation"
        Setup["1. Setup<br/>Create store and tools"]
        ThreadA["2. Thread A<br/>Create marathon plan"]
        SaveMem["3. Save Memories<br/>Store training details"]
        ThreadB["4. Thread B<br/>Different conversation"]
        Retrieve["5. Retrieve<br/>Access specific memories"]
        
        Setup --> ThreadA
        ThreadA --> SaveMem
        SaveMem --> ThreadB
        ThreadB --> Retrieve
    end
    
    subgraph "Code Components"
        InMemoryStore["InMemoryStore<br/>with embeddings"]
        Tools["Memory Tools<br/>manage_memory, search_memory"]
        Namespace["Namespace Structure<br/>(agent_memories, user_id)"]
        Store["store.search()<br/>store.put()"]
    end
    
    Setup --> InMemoryStore
    Setup --> Tools
    Setup --> Namespace
    SaveMem --> Store
    Retrieve --> Store
```

Sources: [examples/intro_videos/semantic_memory.ipynb:185-202](), [examples/intro_videos/semantic_memory.ipynb:267-282](), [examples/intro_videos/semantic_memory.ipynb:392-395]()

## Procedural Memory Notebook

The Procedural Memory notebook demonstrates how to store and optimize system instructions that guide agent behavior. This notebook focuses on improving agent performance through prompt optimization.

### Key Demonstrations

1. **Storing Instructions**: Setting up procedural memory for agent instructions
2. **Prompt Optimization**: Using feedback to improve prompts automatically
3. **Multi-Agent Systems**: Managing procedural memory across multiple specialized agents

```mermaid
flowchart TB
    subgraph "Procedural Memory Flow"
        StoreInstructions["Store Initial Instructions"]
        CreateAgent["Create Agent with Instructions"]
        UseAgent["Use Agent"]
        Feedback["Gather Feedback"]
        OptimizePrompt["Optimize Prompt"]
        UpdateStore["Update Stored Instructions"]
        UseImproved["Use Improved Agent"]
    end
    
    StoreInstructions --> CreateAgent
    CreateAgent --> UseAgent
    UseAgent --> Feedback
    Feedback --> OptimizePrompt
    OptimizePrompt --> UpdateStore
    UpdateStore --> UseImproved
    
    subgraph "Code Components"
        store_put["store.put((instructions,), key=agent_instructions)"]
        prompt_fn["prompt() function"]
        create_prompt_optimizer["create_prompt_optimizer()"]
        create_multi_prompt_optimizer["create_multi_prompt_optimizer()"]
    end
    
    StoreInstructions --> store_put
    CreateAgent --> prompt_fn
    OptimizePrompt --> create_prompt_optimizer
    OptimizePrompt --> create_multi_prompt_optimizer
```

Sources: [examples/intro_videos/procedural_memory.ipynb:29-33](), [examples/intro_videos/procedural_memory.ipynb:42-55](), [examples/intro_videos/procedural_memory.ipynb:110-126]()

### Implementation Examples

The notebook includes these practical examples:

1. **Email Assistant**: An agent that drafts emails based on stored instructions
2. **Prompt Optimization**: Improving email templates based on feedback
3. **Multi-Agent System**: Coordinating multiple agents (email and social media) with separate procedural memories
4. **Multi-Prompt Optimization**: Selectively updating prompts based on specific feedback

```mermaid
graph TD
    subgraph "Procedural Memory Implementation"
        InitInstructions["1. Initialize Instructions<br/>Write good emails"]
        CreateAgent["2. Create Agent<br/>With stored instructions"]
        UseAgent["3. Use Agent<br/>Draft email"]
        GetFeedback["4. Provide Feedback<br/>Sign off as William"]
        Optimize["5. Optimize Prompt<br/>Improve instructions"]
        UpdateStore["6. Update Store<br/>Save improved instructions"]
        TestImproved["7. Test Improved Agent<br/>Draft better email"]
    end
    
    subgraph "Multi-Agent Example"
        MultiStore["Store multiple instruction sets"]
        EmailAgent["Email Assistant"]
        TweetAgent["Social Media Assistant"]
        Supervisor["Supervisor Workflow"]
        MultiOptimize["Multi-prompt optimization"]
    end
    
    InitInstructions --> CreateAgent
    CreateAgent --> UseAgent
    UseAgent --> GetFeedback
    GetFeedback --> Optimize
    Optimize --> UpdateStore
    UpdateStore --> TestImproved
    
    TestImproved --> MultiStore
    MultiStore --> EmailAgent
    MultiStore --> TweetAgent
    EmailAgent --> Supervisor
    TweetAgent --> Supervisor
    Supervisor --> MultiOptimize
```

Sources: [examples/intro_videos/procedural_memory.ipynb:29-55](), [examples/intro_videos/procedural_memory.ipynb:110-176](), [examples/intro_videos/procedural_memory.ipynb:286-322](), [examples/intro_videos/procedural_memory.ipynb:407-517]()

## Running the Notebooks

To run these notebooks:

1. Install the required packages:
   ```python
   pip install -U langmem langgraph
   ```

2. For multi-agent examples, also install:
   ```python
   pip install -U langgraph-supervisor
   ```

3. Open the notebooks in Jupyter or a compatible environment.

4. Execute the cells in order to see the demonstrations.

5. Modify the examples to experiment with different memory configurations.

Sources: [examples/intro_videos/semantic_memory.ipynb:17-19](), [examples/intro_videos/procedural_memory.ipynb:17-20](), [examples/intro_videos/procedural_memory.ipynb:271-273]()

## Video Resources

Video tutorials demonstrating LangMem concepts and implementations are planned as complementary resources to the notebooks. These videos will provide step-by-step guidance on implementing different memory types and integrating them with agents.

The notebooks are designed to align with these upcoming video tutorials, allowing users to follow along with the code examples while watching the explanatory content.

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/reference/index.md](docs/docs/reference/index.md)
- [src/langmem/__init__.py](src/langmem/__init__.py)
- [src/langmem/prompts/optimization.py](src/langmem/prompts/optimization.py)
- [src/langmem/prompts/types.py](src/langmem/prompts/types.py)

</details>



This page provides complete API documentation for all LangMem functions, classes, and utilities. It covers the Core API layer (stateless functions) and Stateful Integration layer (persistent memory management), along with supporting data types and utilities.

For detailed usage examples and integration patterns, see [Memory Management](#2), [Memory Tools](#5), and [Integration](#4). For background on the system architecture, see [Key Concepts](#1.2).

## Core API Structure

LangMem's API is organized around key functional areas, each providing specific capabilities for memory-enabled LLM applications:

#### LangMem API Organization

```mermaid
graph TB
    subgraph "Core API Exports"
        subgraph "Memory Management"
            CMM["create_memory_manager()"]
            CMSM["create_memory_store_manager()"]
            CTE["create_thread_extractor()"]
            CMS["create_memory_searcher()"]
        end
        
        subgraph "Memory Tools"
            CMMT["create_manage_memory_tool()"]
            CSMT["create_search_memory_tool()"]
        end
        
        subgraph "Prompt Optimization"  
            CPO["create_prompt_optimizer()"]
            CMPO["create_multi_prompt_optimizer()"]
        end
        
        subgraph "Background Processing"
            RE["ReflectionExecutor"]
        end
        
        subgraph "Data Types"
            P["Prompt"]
            AT["AnnotatedTrajectory"] 
            OI["OptimizerInput"]
            MPOI["MultiPromptOptimizerInput"]
        end
        
        subgraph "Utilities"
            NT["NamespaceTemplate"]
            FS["format_sessions()"]
        end
    end
    
    subgraph "LangGraph Integration"
        BS["BaseStore"]
        CRA["create_react_agent()"]
    end
    
    subgraph "LLM Providers"
        BCM["BaseChatModel"]
        MS["Model Strings"]
    end
    
    %% Memory Management connections
    CMM --> BCM
    CMSM --> BS
    CMSM --> CMM
    CTE --> CMM
    
    %% Tool connections  
    CMMT --> CMSM
    CSMT --> CMSM
    CMMT --> CRA
    CSMT --> CRA
    
    %% Optimization connections
    CPO --> BCM
    CPO --> MS
    CMPO --> CPO
    
    %% Data type usage
    P --> CPO
    P --> CMPO
    AT --> CPO
    AT --> CMPO
    OI --> CPO
    MPOI --> CMPO
    
    %% Utility usage
    NT --> CMSM
    FS --> CMPO
    
    %% Background processing
    RE --> CMSM
```

**Sources:** [src/langmem/__init__.py:1-28](), [docs/docs/reference/index.md:1-34]()

## Memory Management APIs

The memory management layer provides both stateless (`create_memory_manager`) and stateful (`create_memory_store_manager`) approaches to extracting, storing, and retrieving memories from conversations.

#### Memory Manager Architecture

```mermaid
graph LR
    subgraph "Stateless Layer"
        CMM["create_memory_manager()"]
        CTE["create_thread_extractor()"] 
        CMS["create_memory_searcher()"]
    end
    
    subgraph "Stateful Layer"
        CMSM["create_memory_store_manager()"]
        MSM["MemoryStoreManager"]
    end
    
    subgraph "Memory Types"
        SM["Semantic Memory"]
        EM["Episodic Memory"]  
        PM["Procedural Memory"]
        STM["Short-term Memory"]
    end
    
    subgraph "Storage Patterns"
        CP["Collection Pattern"]
        PP["Profile Pattern"] 
        RP["Rule Pattern"]
    end
    
    %% API relationships
    CMM --> SM
    CMM --> EM
    CMM --> PM
    CTE --> STM
    
    CMSM --> CMM
    CMSM --> MSM
    
    %% Storage pattern mapping
    SM --> CP
    SM --> PP
    EM --> CP
    PM --> RP
    STM --> PP
```

The `create_memory_manager` function creates stateless memory extractors that analyze conversations and return structured memory objects. The `create_memory_store_manager` function wraps this with persistent storage capabilities using LangGraph's `BaseStore`.

The `create_thread_extractor` specializes in conversation summarization and context management, while `create_memory_searcher` provides semantic search across stored memories.

**Sources:** [src/langmem/__init__.py:1-8](), [docs/docs/reference/index.md:10-16]()

## Memory Tools APIs

Memory tools enable agents to actively manage their own memory through structured tool calls during conversations. These tools provide the "hot path" memory formation capabilities.

#### Memory Tools Integration

```mermaid
graph TB
    subgraph "Agent Tools"
        CMMT["create_manage_memory_tool()"]
        CSMT["create_search_memory_tool()"]
    end
    
    subgraph "Tool Actions"
        subgraph "Management Actions"
            CREATE["create"]
            UPDATE["update"]
            DELETE["delete"]
        end
        
        subgraph "Search Actions"
            SEARCH["search"]
            RETRIEVE["retrieve"]
        end
    end
    
    subgraph "Agent Frameworks"
        CRA["create_react_agent()"]
        CA["Custom Agents"]
        CREW["CrewAI"]
    end
    
    subgraph "Storage Layer"
        BS["BaseStore"]
        IMS["InMemoryStore"]
        PGS["AsyncPostgresStore"]
    end
    
    %% Tool to action mapping
    CMMT --> CREATE
    CMMT --> UPDATE  
    CMMT --> DELETE
    CSMT --> SEARCH
    CSMT --> RETRIEVE
    
    %% Agent integration
    CMMT --> CRA
    CSMT --> CRA
    CMMT --> CA
    CSMT --> CA
    CMMT --> CREW
    CSMT --> CREW
    
    %% Storage integration
    CMMT --> BS
    CSMT --> BS
    BS --> IMS
    BS --> PGS
```

The `create_manage_memory_tool` creates a tool that agents can use to store, update, and delete memories with configurable `actions_permitted` parameters. The `create_search_memory_tool` creates a tool for semantic search and retrieval of relevant memories based on queries.

**Sources:** [src/langmem/__init__.py:2-3,19-20](), [docs/docs/reference/index.md:17-23]()

## Prompt Optimization APIs

The prompt optimization system provides iterative improvement of prompts based on conversation feedback and performance analysis.

#### Prompt Optimization Strategies

```mermaid
graph TB
    subgraph "Single Prompt Optimization"
        CPO["create_prompt_optimizer()"]
        
        subgraph "Optimization Strategies"
            GRAD["gradient"]
            META["metaprompt"]
            PMEM["prompt_memory"]
        end
    end
    
    subgraph "Multi-Prompt Optimization"
        CMPO["create_multi_prompt_optimizer()"]
        MPO["MultiPromptOptimizer"]
        
        subgraph "Credit Assignment"
            CLASS["Classify"]
            REASON["reasoning"]
            WHICH["which"]
        end
    end
    
    subgraph "Input Types"
        OI["OptimizerInput"]
        MPOI["MultiPromptOptimizerInput"]
        AT["AnnotatedTrajectory"]
        P["Prompt"]
    end
    
    subgraph "Optimization Configs"
        GOC["GradientOptimizerConfig"]
        MOC["MetapromptOptimizerConfig"]
    end
    
    %% Strategy connections
    CPO --> GRAD
    CPO --> META
    CPO --> PMEM
    
    %% Multi-prompt connections
    CMPO --> MPO
    MPO --> CPO
    MPO --> CLASS
    CLASS --> REASON
    CLASS --> WHICH
    
    %% Input type usage
    CPO --> OI
    CMPO --> MPOI
    OI --> AT
    OI --> P
    MPOI --> AT
    MPOI --> P
    
    %% Config usage
    CPO --> GOC
    CPO --> MOC
```

The `create_prompt_optimizer` function supports three optimization strategies with different trade-offs between speed and thoroughness. The `create_multi_prompt_optimizer` function extends this to handle multiple prompts simultaneously with credit assignment to determine which prompts need updates.

**Sources:** [src/langmem/prompts/optimization.py:50-269](), [src/langmem/prompts/optimization.py:471-616](), [src/langmem/__init__.py:9-13,22-23]()

## Background Processing APIs

The `ReflectionExecutor` enables deferred memory processing and analysis separate from real-time conversation flow.

#### Reflection Processing Architecture

```mermaid
graph LR
    subgraph "Conversation Layer"
        CONV["Conversation"]
        USER["User Interaction"]
    end
    
    subgraph "Background Processing"
        RE["ReflectionExecutor"]
        
        subgraph "Processing Tasks"
            EXTRACT["Memory Extraction"]
            CONSOLIDATE["Memory Consolidation"]
            UPDATE["Memory Updates"]
            ANALYZE["Conversation Analysis"]
        end
    end
    
    subgraph "Storage Integration"
        CMSM["create_memory_store_manager()"]
        BS["BaseStore"]
    end
    
    subgraph "LangGraph Services"
        LGS["LangGraph Services"]
        SCHED["Task Scheduling"]
    end
    
    %% Flow connections
    CONV --> RE
    USER --> RE
    
    RE --> EXTRACT
    RE --> CONSOLIDATE  
    RE --> UPDATE
    RE --> ANALYZE
    
    %% Storage integration
    RE --> CMSM
    CMSM --> BS
    
    %% Service integration
    RE --> LGS
    LGS --> SCHED
```

The `ReflectionExecutor` processes conversations asynchronously to extract insights, consolidate related memories, and perform deeper analysis without blocking real-time interactions.

**Sources:** [src/langmem/__init__.py:14,25](), [docs/docs/reference/index.md:31-34]()

## Data Types and Schemas

LangMem defines several key data types for structured memory management and prompt optimization.

#### Core Data Type Relationships

```mermaid
graph TB
    subgraph "Prompt Types"
        P["Prompt"]
        PN["name: str"]
        PP["prompt: str"]  
        UI["update_instructions: str | None"]
        WTU["when_to_update: str | None"]
    end
    
    subgraph "Trajectory Types"
        AT["AnnotatedTrajectory"]
        MSG["messages: Sequence[AnyMessage]"]
        FB["feedback: dict | str | None"]
    end
    
    subgraph "Input Types"
        OI["OptimizerInput"]
        MPOI["MultiPromptOptimizerInput"]
        TRAJ["trajectories"]
        PROMPT["prompt"]
        PROMPTS["prompts"]
    end
    
    subgraph "Memory Types"
        EM["ExtractedMemory"]
        RS["RunningSummary"]
        TRIP["Triple"]
        EP["Episode"]
    end
    
    %% Prompt structure
    P --> PN
    P --> PP
    P --> UI
    P --> WTU
    
    %% Trajectory structure
    AT --> MSG
    AT --> FB
    
    %% Input type composition
    OI --> TRAJ
    OI --> PROMPT
    MPOI --> TRAJ
    MPOI --> PROMPTS
    
    %% Usage relationships
    TRAJ --> AT
    PROMPT --> P
    PROMPTS --> P
```

The `Prompt` type provides structured prompt management with optimization metadata. The `AnnotatedTrajectory` type pairs conversation history with feedback for optimization. Input types like `OptimizerInput` and `MultiPromptOptimizerInput` structure the data flow for optimization functions.

**Sources:** [src/langmem/prompts/types.py:7-136](), [src/langmem/__init__.py:26]()

## Function Signature Reference

| Function | Parameters | Returns | Purpose |
|----------|------------|---------|---------|
| `create_memory_manager` | `model`, `memory_types`, `config` | Memory extractor | Stateless memory extraction |
| `create_memory_store_manager` | `model`, `store`, `namespace_template` | `MemoryStoreManager` | Persistent memory management |
| `create_manage_memory_tool` | `memory_store_manager`, `actions_permitted` | Agent tool | Memory management tool |
| `create_search_memory_tool` | `memory_store_manager`, `query_config` | Agent tool | Memory search tool |
| `create_prompt_optimizer` | `model`, `kind`, `config` | Prompt optimizer | Single prompt optimization |
| `create_multi_prompt_optimizer` | `model`, `kind`, `config` | Multi-prompt optimizer | Multiple prompt optimization |
| `create_thread_extractor` | `model`, `config` | Thread extractor | Conversation summarization |
| `create_memory_searcher` | `store`, `config` | Memory searcher | Semantic memory search |

**Sources:** [src/langmem/__init__.py:16-27](), [docs/docs/reference/index.md:8-34]()

---

# Page: Main API Functions

# Main API Functions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/langmem/__init__.py](src/langmem/__init__.py)
- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)
- [src/langmem/prompts/types.py](src/langmem/prompts/types.py)

</details>



This document covers the core factory functions that create LangMem's primary components. These functions serve as the main entry points for integrating memory capabilities into LLM applications. 

For information about using these components with agents, see [Memory Tools](#5). For details about specific memory types and schemas, see [Memory Types and Classes](#9.2). For background processing workflows, see [Background Memory Processing](#3.2).

## Core Factory Functions

LangMem provides several factory functions that create the main system components. These functions follow a consistent pattern of accepting a model specification and configuration parameters, then returning configured runnables or tools.

### Memory Management Factories

The primary memory management functions create components for extracting, storing, and retrieving memories from conversations.

```mermaid
graph TB
    subgraph "Factory Functions"
        cmm["create_memory_manager()"]
        cmsm["create_memory_store_manager()"] 
        cms["create_memory_searcher()"]
        cte["create_thread_extractor()"]
    end
    
    subgraph "Created Components"
        mm["MemoryManager"]
        msm["MemoryStoreManager"]
        searcher["Memory Search Pipeline"]
        extractor["Thread Extractor"]
    end
    
    subgraph "Core Interfaces"
        runnable["Runnable[Input, Output]"]
        store["BaseStore"]
        llm["BaseChatModel"]
    end
    
    cmm --> mm
    cmsm --> msm
    cms --> searcher
    cte --> extractor
    
    mm --> runnable
    msm --> runnable
    searcher --> runnable
    extractor --> runnable
    
    msm --> store
    cms --> store
    
    mm --> llm
    msm --> llm
    searcher --> llm
    extractor --> llm
```

**Sources:** [src/langmem/knowledge/extraction.py:536-692](), [src/langmem/knowledge/extraction.py:832-914](), [src/langmem/knowledge/extraction.py:695-815](), [src/langmem/knowledge/extraction.py:113-182]()

#### create_memory_manager

The `create_memory_manager` function creates a stateless memory extraction component that processes conversation messages and generates structured memory entries.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str \| BaseChatModel` | Required | Language model for memory extraction |
| `schemas` | `Sequence[BaseModel]` | `(Memory,)` | Pydantic models defining memory structure |
| `instructions` | `str` | Built-in instructions | Custom instructions for memory generation |
| `enable_inserts` | `bool` | `True` | Allow creating new memory entries |
| `enable_updates` | `bool` | `True` | Allow updating existing memories |
| `enable_deletes` | `bool` | `False` | Allow deleting existing memories |

**Returns:** `Runnable[MemoryState, list[ExtractedMemory]]`

**Sources:** [src/langmem/knowledge/extraction.py:536-692]()

#### create_memory_store_manager

The `create_memory_store_manager` function creates a stateful memory management component that automatically handles persistence, search, and consolidation of memories.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str \| BaseChatModel` | Required | Language model for memory processing |
| `schemas` | `list[BaseModel] \| None` | `None` | Memory schema definitions |
| `namespace` | `tuple[str, ...]` | `("memories", "{langgraph_user_id}")` | Storage namespace template |
| `store` | `BaseStore \| None` | `None` | Storage backend (uses LangGraph context if None) |
| `enable_inserts` | `bool` | `True` | Allow memory creation |
| `enable_deletes` | `bool` | `True` | Allow memory deletion |
| `query_model` | `str \| BaseChatModel \| None` | `None` | Model for search query generation |
| `query_limit` | `int` | `5` | Maximum memories to retrieve |

**Returns:** `MemoryStoreManager` (implements `Runnable[MemoryStoreManagerInput, list[dict]]`)

**Sources:** [src/langmem/knowledge/extraction.py:832-914]()

#### create_memory_searcher

The `create_memory_searcher` function creates a memory search pipeline that generates queries from conversation context and returns ranked results.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str \| BaseChatModel` | Required | Model for query generation |
| `prompt` | `str` | Built-in search prompt | Instructions for query generation |
| `namespace` | `tuple[str, ...]` | `("memories", "{langgraph_user_id}")` | Search namespace template |

**Returns:** `Runnable[MessagesState, list[SearchItem]]`

**Sources:** [src/langmem/knowledge/extraction.py:695-815]()

#### create_thread_extractor

The `create_thread_extractor` function creates conversation summarizers using schema-based extraction.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | Required | Language model for summarization |
| `schema` | `BaseModel \| type \| None` | `None` | Output schema (uses `SummarizeThread` if None) |
| `instructions` | `str` | Built-in instructions | Summarization instructions |

**Returns:** `Runnable[MessagesState, BaseModel]`

**Sources:** [src/langmem/knowledge/extraction.py:113-182]()

### Tool Creation Factories

LangMem provides factory functions for creating tools that agents can use to manage their own memories.

```mermaid
graph TB
    subgraph "Tool Factories"
        cmmt["create_manage_memory_tool()"]
        csmt["create_search_memory_tool()"]
    end
    
    subgraph "Agent Tools"
        manage["ManageMemoryTool"]
        search["SearchMemoryTool"]
    end
    
    subgraph "Tool Actions"
        create["create"]
        update["update"]
        delete["delete"]
        query["search"]
    end
    
    subgraph "Storage Operations"
        put["store.put()"]
        get["store.get()"]
        asearch["store.asearch()"]
        adelete["store.adelete()"]
    end
    
    cmmt --> manage
    csmt --> search
    
    manage --> create
    manage --> update
    manage --> delete
    
    search --> query
    
    create --> put
    update --> put
    delete --> adelete
    query --> asearch
```

**Sources:** [src/langmem/knowledge/tools.py](), [src/langmem/__init__.py:1-8]()

### Prompt Optimization Factories

For prompt optimization capabilities, LangMem provides factory functions that create prompt refinement systems.

| Function | Purpose | Input Type | Output Type |
|----------|---------|------------|-------------|
| `create_prompt_optimizer` | Single prompt optimization | `OptimizerInput` | Optimized `Prompt` |
| `create_multi_prompt_optimizer` | Multi-prompt system optimization | `MultiPromptOptimizerInput` | List of optimized `Prompt`s |

**Sources:** [src/langmem/prompts/optimization.py](), [src/langmem/__init__.py:9-13]()

## Component Relationships

The factory functions create components that work together in LangMem's two-layer architecture:

```mermaid
graph TB
    subgraph "Core API Layer (Stateless)"
        cmm["create_memory_manager()"]
        cte["create_thread_extractor()"] 
        cms["create_memory_searcher()"]
        cpo["create_prompt_optimizer()"]
    end
    
    subgraph "Stateful Integration Layer"
        cmsm["create_memory_store_manager()"]
        cmmt["create_manage_memory_tool()"]
        csmt["create_search_memory_tool()"]
    end
    
    subgraph "Background Processing"
        re["ReflectionExecutor"]
    end
    
    subgraph "External Dependencies"
        store["BaseStore"]
        model["BaseChatModel"] 
        config["RunnableConfig"]
    end
    
    cmsm --> cmm
    cmsm --> store
    
    cmmt --> store
    csmt --> store
    
    cms --> store
    
    re --> cmsm
    
    cmm --> model
    cmsm --> model
    cms --> model
    cte --> model
    cpo --> model
    
    cmmt --> config
    csmt --> config
    cmsm --> config
```

**Sources:** [src/langmem/knowledge/extraction.py:1-50](), [src/langmem/__init__.py:1-27]()

## Usage Patterns

### Direct Memory Processing

Use core API functions for stateless memory processing:

```python
# Create memory manager for extraction
manager = create_memory_manager("gpt-4")

# Process conversation
memories = await manager.ainvoke({
    "messages": conversation,
    "existing": existing_memories
})
```

### Persistent Memory Management  

Use stateful integration functions for automatic persistence:

```python
# Create persistent memory manager
store_manager = create_memory_store_manager(
    "claude-3-5-sonnet",
    namespace=("user_memories", "{user_id}"),
    store=postgres_store
)

# Automatically extracts and stores memories
updates = await store_manager.ainvoke({
    "messages": conversation
})
```

### Agent Integration

Use tool creation functions for agent-driven memory:

```python
# Create tools for agent use
memory_tool = create_manage_memory_tool(
    namespace=("agent_knowledge", "{session_id}")
)
search_tool = create_search_memory_tool(
    namespace=("agent_knowledge", "{session_id}")
)

# Add to agent
agent = create_react_agent(
    model, 
    tools=[memory_tool, search_tool]
)
```

**Sources:** [src/langmem/knowledge/extraction.py:575-683](), [src/langmem/knowledge/extraction.py:1282-1283](), [src/langmem/knowledge/tools.py]()

## Configuration and Namespaces

Most factory functions accept namespace configuration using `NamespaceTemplate` for organizing memories:

```mermaid
graph LR
    subgraph "Namespace Templates"
        static["('memories', 'global')"]
        user["('memories', '{langgraph_user_id}')"]
        session["('chat', '{session_id}')"]
        custom["('team', '{team_id}', '{project}')"]
    end
    
    subgraph "Runtime Resolution"
        config["RunnableConfig"]
        vars["configurable variables"]
    end
    
    subgraph "Resolved Namespaces"
        r_static["('memories', 'global')"]
        r_user["('memories', 'user-123')"]
        r_session["('chat', 'abc-456')"]
        r_custom["('team', 'engineering', 'langmem')"]
    end
    
    static --> r_static
    user --> r_user
    session --> r_session
    custom --> r_custom
    
    config --> vars
    vars --> r_user
    vars --> r_session
    vars --> r_custom
```

**Sources:** [src/langmem/utils.py](), [src/langmem/knowledge/extraction.py:877]()

---

# Page: Memory Types and Classes

# Memory Types and Classes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/langmem/knowledge/extraction.py](src/langmem/knowledge/extraction.py)
- [src/langmem/short_term/summarization.py](src/langmem/short_term/summarization.py)

</details>



This page documents the core memory-related classes, data structures, and type definitions in LangMem. These classes handle memory extraction, storage, retrieval, and summarization operations within the LangMem system.

For information about using these classes in practice, see [Memory Management](#2). For details about the main API functions that create these classes, see [Main API Functions](#9.1).

## Core Memory Data Structures

### ExtractedMemory

The `ExtractedMemory` type represents the fundamental unit of extracted memory content returned by memory processing operations.

```mermaid
classDiagram
    class ExtractedMemory {
        +str id
        +BaseModel content
    }
    class BaseModel {
        <<pydantic>>
    }
    ExtractedMemory --> BaseModel : contains
```

**ExtractedMemory Structure**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier for the memory |
| `content` | `BaseModel` | Structured memory content as Pydantic model |

Sources: [src/langmem/knowledge/extraction.py:78-81]()

### Memory Schema

The default `Memory` schema provides a simple structure for unstructured memory content.

```mermaid
classDiagram
    class Memory {
        +str content
        +model_dump() dict
        +__repr_name__() str
    }
    BaseModel <|-- Memory
```

Sources: [src/langmem/knowledge/extraction.py:86-93]()

### RunningSummary

The `RunningSummary` dataclass tracks conversation summarization state across multiple summarization operations.

```mermaid
classDiagram
    class RunningSummary {
        +str summary
        +set~str~ summarized_message_ids
        +str|None last_summarized_message_id
    }
```

**RunningSummary Fields**

| Field | Type | Description |
|-------|------|-------------|
| `summary` | `str` | Latest summary text |
| `summarized_message_ids` | `set[str]` | IDs of all summarized messages |
| `last_summarized_message_id` | `str \| None` | ID of most recently summarized message |

Sources: [src/langmem/short_term/summarization.py:53-67]()

## Memory Processing Classes

### MemoryManager

The `MemoryManager` class handles core memory extraction and updating logic without persistent storage.

```mermaid
classDiagram
    class MemoryManager {
        -BaseChatModel model
        -Sequence~type~ schemas
        -str instructions
        -bool enable_inserts
        -bool enable_updates
        -bool enable_deletes
        +ainvoke(MemoryState) list~ExtractedMemory~
        +invoke(MemoryState) list~ExtractedMemory~
        +__call__(messages, existing) list~ExtractedMemory~
        -_prepare_messages(messages, max_steps) list~dict~
        -_prepare_existing(existing) list~tuple~
        -_filter_response(memories, external_ids, exclude_removals) list~ExtractedMemory~
    }
    
    class MemoryState {
        +list~AnyMessage~ messages
        +list~tuple~ existing
        +int max_steps
    }
    
    MemoryManager --> MemoryState : processes
    MemoryManager --> ExtractedMemory : returns
```

**Key Methods:**
- `ainvoke()` / `invoke()`: Process messages and extract memories
- `_prepare_messages()`: Format conversation for LLM processing
- `_prepare_existing()`: Format existing memories for update operations
- `_filter_response()`: Handle memory removals and updates

Sources: [src/langmem/knowledge/extraction.py:217-534]()

### MemoryStoreManager

The `MemoryStoreManager` integrates memory processing with persistent storage via LangGraph's `BaseStore`.

```mermaid
classDiagram
    class MemoryStoreManager {
        -BaseChatModel model
        -BaseChatModel|None query_model
        -list~type~ schemas
        -NamespaceTemplate namespace
        -BaseStore _store
        -MemoryManager memory_manager
        -SearchTool search_tool
        +ainvoke(MemoryStoreManagerInput) list~dict~
        +invoke(MemoryStoreManagerInput) list~dict~
        +get(key, config) Item|None
        +search(query, filter, limit, config) list~SearchItem~
        +put(key, value, config) None
        +delete(key, config) None
        +aget(key, config) Item|None
        +asearch(query, filter, limit, config) list~SearchItem~
        +aput(key, value, config) None
        +adelete(key, config) None
        +get_namespace(config) tuple~str~
        -_coerce_default(default, schemas) BaseModel
        -_apply_manager_output(manager_output, store_based, store_map, ephemeral) tuple
        -_sort_results(search_results_lists, query_limit) dict
    }
    
    class BaseStore {
        <<interface>>
    }
    
    class NamespaceTemplate {
        +__call__(config) tuple~str~
    }
    
    MemoryStoreManager --> BaseStore : uses
    MemoryStoreManager --> NamespaceTemplate : uses
    MemoryStoreManager --> MemoryManager : contains
```

**Storage Operations:**
- `get()` / `aget()`: Retrieve single memory by key
- `search()` / `asearch()`: Search memories with query/filter
- `put()` / `aput()`: Store memory with indexing options
- `delete()` / `adelete()`: Remove memory from storage

**Memory Processing:**
- `ainvoke()` / `invoke()`: Full memory enrichment pipeline
- `_apply_manager_output()`: Apply memory updates to storage
- `_sort_results()`: Rank search results by relevance

Sources: [src/langmem/knowledge/extraction.py:832-1663]()

## Storage Integration Classes

### Item and SearchItem

Enhanced versions of LangGraph's storage items with automatic Pydantic model coercion.

```mermaid
classDiagram
    class BaseItem {
        <<langgraph>>
        +tuple~str~ namespace
        +str key
        +dict value
        +datetime created_at
        +datetime updated_at
    }
    
    class BaseSearchItem {
        <<langgraph>>
        +float|None score
    }
    
    class Item {
        +BaseModel|dict value
        +dict() dict
    }
    
    class SearchItem {
        +BaseModel|dict value
        +dict() dict
    }
    
    BaseItem <|-- Item
    BaseSearchItem <|-- SearchItem
    BaseItem <|-- BaseSearchItem
```

**Key Features:**
- Automatic coercion of `dict` values to Pydantic models
- Enhanced `dict()` serialization with JSON mode
- Maintains compatibility with LangGraph storage interface

Sources: [src/langmem/knowledge/extraction.py:44-61]()

## Summarization Classes

### SummarizationResult

Container for message summarization output and state tracking.

```mermaid
classDiagram
    class SummarizationResult {
        +list~AnyMessage~ messages
        +RunningSummary|None running_summary
    }
    
    class RunningSummary {
        +str summary
        +set~str~ summarized_message_ids
        +str|None last_summarized_message_id
    }
    
    SummarizationResult --> RunningSummary : contains
```

Sources: [src/langmem/short_term/summarization.py:70-79]()

### SummarizationNode

LangGraph-compatible node for message summarization within graph workflows.

```mermaid
classDiagram
    class RunnableCallable {
        <<langgraph>>
    }
    
    class SummarizationNode {
        -LanguageModelLike model
        -int max_tokens
        -int|None max_tokens_before_summary
        -int max_summary_tokens
        -TokenCounter token_counter
        -ChatPromptTemplate initial_summary_prompt
        -ChatPromptTemplate existing_summary_prompt
        -ChatPromptTemplate final_prompt
        -str input_messages_key
        -str output_messages_key
        +_func(input) dict
        +_afunc(input) dict
        -_parse_input(input) tuple
        -_prepare_state_update(context, result) dict
    }
    
    RunnableCallable <|-- SummarizationNode
```

**Configuration Options:**
- `input_messages_key`: State key for input messages (default: `"messages"`)
- `output_messages_key`: State key for output messages (default: `"summarized_messages"`)
- Token limits and prompt templates for summarization control

Sources: [src/langmem/short_term/summarization.py:660-860]()

## State and Configuration Types

### Input State Types

```mermaid
classDiagram
    class MessagesState {
        +list~AnyMessage~ messages
    }
    
    class MemoryState {
        +list~AnyMessage~ messages
        +list~tuple~ existing
        +int max_steps
    }
    
    class MemoryStoreManagerInput {
        +list~AnyMessage~ messages
        +int max_steps
    }
    
    MessagesState <|-- MemoryState
```

**State Type Usage:**
- `MessagesState`: Basic message container for thread extraction
- `MemoryState`: Extended state for memory processing with existing memories
- `MemoryStoreManagerInput`: Input schema for storage-integrated memory management

Sources: [src/langmem/knowledge/extraction.py:64-830]()

### Memory Processing Configuration

```mermaid
classDiagram
    class MemoryPhase {
        +str instructions
        +bool include_messages
        +bool enable_inserts
        +bool enable_deletes
    }
    
    class TokenCounter {
        <<type alias>>
    }
    
    class NamespaceTemplate {
        +tuple~str~ template
        +__call__(config) tuple~str~
    }
```

**Configuration Types:**
- `MemoryPhase`: Defines multi-phase memory processing steps
- `TokenCounter`: Function type for counting message tokens
- `NamespaceTemplate`: Dynamic namespace resolution from runtime config

Sources: [src/langmem/knowledge/extraction.py:818-823](), [src/langmem/short_term/summarization.py:20]()

## Class Relationships and Data Flow

```mermaid
flowchart TD
    Messages["list[AnyMessage]"] --> MemoryManager
    MemoryManager --> ExtractedMemory
    ExtractedMemory --> MemoryStoreManager
    MemoryStoreManager --> BaseStore
    BaseStore --> Item
    BaseStore --> SearchItem
    
    Messages --> SummarizationNode
    SummarizationNode --> SummarizationResult
    SummarizationResult --> RunningSummary
    
    MemoryStoreManager -.-> MemoryManager : "uses internally"
    MemoryStoreManager -.-> NamespaceTemplate : "resolves namespaces"
    
    subgraph "Memory Processing"
        MemoryManager
        ExtractedMemory
    end
    
    subgraph "Storage Layer"
        MemoryStoreManager
        BaseStore
        Item
        SearchItem
    end
    
    subgraph "Summarization"
        SummarizationNode
        SummarizationResult
        RunningSummary
    end
```

This diagram shows how messages flow through the different class layers, from raw message processing through memory extraction to persistent storage, with summarization as a parallel concern for managing conversation context.

Sources: [src/langmem/knowledge/extraction.py:217-1663](), [src/langmem/short_term/summarization.py:53-860]()

---

# Page: Utility Functions

# Utility Functions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/langmem/short_term/__init__.py](src/langmem/short_term/__init__.py)
- [src/langmem/utils.py](src/langmem/utils.py)

</details>



This page documents the utility functions provided by LangMem that support the core functionality of the system. These utilities handle common operations such as namespace templating, conversation formatting, variable management, and serialization, allowing the main components to focus on their primary responsibilities.

## Overview

The utility functions in LangMem serve as supporting tools for several key operations:

1. **Namespace Management** - Utilities that handle templating and dynamic namespacing
2. **Conversation Formatting** - Functions for formatting, merging, and processing conversation histories
3. **Variable Handling** - Tools for managing variables in prompts and templates
4. **Serialization** - Functions for object serialization

Core langmem.utils Module Functions
```mermaid
graph TD
    subgraph "langmem.utils Module"
        NamespaceTemplate["NamespaceTemplate<br/>class"]
        
        get_conversation["get_conversation()<br/>function"]
        get_dialated_windows["get_dialated_windows()<br/>function"] 
        format_sessions["format_sessions()<br/>function"]
        
        get_var_healer["get_var_healer()<br/>function"]
        get_prompt_extraction_schema["get_prompt_extraction_schema()<br/>function"]
        
        dumps["dumps()<br/>function"]
        
        _get_key["_get_key()<br/>helper function"]
    end
    
    subgraph "External Dependencies"
        merge_message_runs["merge_message_runs<br/>from langchain_core.messages.utils"]
        get_config["get_config<br/>from langgraph.utils.config"]
        orjson["orjson<br/>JSON serialization"]
    end
    
    get_conversation --> merge_message_runs
    NamespaceTemplate --> get_config
    dumps --> orjson
    NamespaceTemplate --> _get_key
```

Sources: [src/langmem/utils.py:1-252]()

## Namespace Utilities

### NamespaceTemplate

The `NamespaceTemplate` class provides a flexible way to create dynamic namespaces that can include variables substituted from configuration.

NamespaceTemplate Implementation Details
```mermaid
graph TD
    subgraph "NamespaceTemplate Class"
        init["__init__()<br/>template: Union[tuple, str, NamespaceTemplate]"]
        call["__call__()<br/>config: RunnableConfig | None"]
        template_slot["template: tuple[str, ...]<br/>__slots__"]
        vars_slot["vars: dict[int, str]<br/>__slots__"]
    end
    
    subgraph "Processing Flow"
        RunnableConfig["RunnableConfig"]
        get_config_func["get_config()<br/>from langgraph.utils.config"]
        configurable["config['configurable']"]
        _get_key_func["_get_key()<br/>helper function"]
    end
    
    subgraph "Error Handling"
        ConfigurationError["ConfigurationError<br/>from langmem.errors"]
    end
    
    init --> template_slot
    init --> vars_slot
    init --> _get_key_func
    call --> get_config_func
    call --> configurable
    call --> ConfigurationError
    RunnableConfig --> get_config_func
```

Sources: [src/langmem/utils.py:15-91]()

#### Key Features

- Substitutes variables in curly braces with values from the RunnableConfig's 'configurable' field
- Works with both simple string namespaces and tuple namespaces
- Automatically retrieves the current config when called in a LangGraph context

#### Usage Examples

```python
# Fixed namespace
ns = NamespaceTemplate("user_123")
ns()  # Returns: ('user_123',)

# Variable namespace
ns = NamespaceTemplate(("org", "{user_id}"))
ns({"configurable": {"user_id": "alice"}})  # Returns: ('org', 'alice')

# In LangGraph context, the config is automatically retrieved
@entrypoint()
def my_agent(messages):
    ns = NamespaceTemplate(("org", "{user_id}"))
    print(ns())  # Will use the configurable field from context
```

Sources: [src/langmem/utils.py:15-91]()

## Conversation Formatting Utilities

LangMem provides several utilities for working with conversation histories:

### get_conversation

Merges and formats a list of messages into a pretty-printed conversation string.

```python
def get_conversation(messages: list, delimiter="\n\n"):
    merged = merge_message_runs(messages)
    return delimiter.join(m.pretty_repr() for m in merged)
```

Sources: [src/langmem/utils.py:98-100]()

### get_dialated_windows

Creates "dilated" windows of conversation history, where each window is approximately twice the size of the previous one, up to the full conversation length.

Conversation Window Processing
```mermaid
graph LR
    subgraph "get_dialated_windows Function"
        messages["messages: list"]
        N["N: int = 5"]
        delimiter["delimiter: str = '\\n\\n'"]
    end
    
    subgraph "Processing Logic"
        M["M = len(messages)"]
        size["size = min(M, 1 << i)<br/>exponential growth"]
        slice["messages[M - size:]<br/>window slicing"]
        get_conversation_call["get_conversation()<br/>format window"]
        seen["seen: set<br/>deduplication"]
    end
    
    messages --> M
    N --> size
    M --> size
    size --> slice
    slice --> get_conversation_call
    get_conversation_call --> seen
    delimiter --> get_conversation_call
```

Sources: [src/langmem/utils.py:103-119]()

### format_sessions

Formats a list of conversation sessions, possibly with associated feedback, into a standardized string format suitable for prompts.

```python
def format_sessions(
    sessions: list[list[AnyMessage]] | list[AnyMessage] | list[tuple[list[AnyMessage], dict]] | tuple[list[AnyMessage], dict] | str,
):
    # Formats sessions with optional feedback into a string
    # Each session gets a unique ID and structured format
```

Sources: [src/langmem/utils.py:125-162]()

## Variable Handling Utilities

### get_var_healer

Creates a function that handles f-string variable substitution in prompts, ensuring variables are properly escaped and retained.

Variable Healing Implementation
```mermaid
graph TD
    subgraph "get_var_healer Function"
        vars_input["vars: set[str] | str"]
        all_required["all_required: bool = False"]
        var_to_uuid["var_to_uuid: dict"]
        uuid_to_var["uuid_to_var: dict"]
    end
    
    subgraph "Generated Functions"
        escape["escape()<br/>local function"]
        mask["mask()<br/>local function"]
        unmask["unmask()<br/>local function"]
        assert_all_required["assert_all_required()<br/>local function"]
        pipe["pipe()<br/>returned function"]
    end
    
    subgraph "Regex Patterns"
        mask_pattern["mask_pattern<br/>re.compile()"]
        unmask_pattern["unmask_pattern<br/>re.compile()"]
        strip_to_optimize_pattern["strip_to_optimize_pattern<br/>re.compile()"]
    end
    
    vars_input --> var_to_uuid
    var_to_uuid --> uuid_to_var
    var_to_uuid --> mask_pattern
    uuid_to_var --> unmask_pattern
    
    mask_pattern --> mask
    unmask_pattern --> unmask
    strip_to_optimize_pattern --> pipe
    
    all_required --> assert_all_required
    
    escape --> pipe
    mask --> pipe
    unmask --> pipe
    assert_all_required --> pipe
```

Sources: [src/langmem/utils.py:165-209]()

### get_prompt_extraction_schema

Creates a Pydantic schema for extracting and validating optimized prompts, ensuring that all required variables are preserved.

OptimizedPromptOutput Schema Generation
```mermaid
graph TD
    subgraph "get_prompt_extraction_schema Function"
        original_prompt["original_prompt: str"]
        required_variables["required_variables: set<br/>from re.findall()"]
        variables_str["variables_str: str"]
        prompt_description["prompt_description: str"]
        pipeline["pipeline: function<br/>from get_var_healer()"]
    end
    
    subgraph "Generated Pydantic Model"
        OptimizedPromptOutput["OptimizedPromptOutput<br/>BaseModel"]
        analysis["analysis: str<br/>Field()"]
        improved_prompt["improved_prompt: Optional[str]<br/>Field()"]
        validate_input_variables["validate_input_variables()<br/>@model_validator"]
    end
    
    original_prompt --> required_variables
    required_variables --> variables_str
    variables_str --> prompt_description
    required_variables --> pipeline
    
    prompt_description --> improved_prompt
    pipeline --> validate_input_variables
    
    OptimizedPromptOutput --> analysis
    OptimizedPromptOutput --> improved_prompt
    OptimizedPromptOutput --> validate_input_variables
```

Sources: [src/langmem/utils.py:212-248]()

## Serialization Utilities

### dumps

A simple wrapper around `orjson.dumps` that ensures the output is a UTF-8 string.

```python
def dumps(obj: typing.Any) -> str:
    return orjson.dumps(obj).decode("utf-8")
```

Sources: [src/langmem/utils.py:251-252]()

## JSON Serialization Utilities

### dumps

A simple wrapper around `orjson.dumps` that ensures the output is a UTF-8 string.

```python
def dumps(obj: typing.Any) -> str:
    return orjson.dumps(obj).decode("utf-8")
```

Sources: [src/langmem/utils.py:251-252]()

## Integration with LangMem Components

The utility functions integrate with other LangMem components to provide essential functionality for the memory management system.

langmem.utils Integration Points
```mermaid
graph TD
    subgraph "langmem.utils Functions"
        NamespaceTemplate_class["NamespaceTemplate"]
        get_conversation_func["get_conversation()"]
        get_dialated_windows_func["get_dialated_windows()"]
        format_sessions_func["format_sessions()"]
        get_var_healer_func["get_var_healer()"]
        get_prompt_extraction_schema_func["get_prompt_extraction_schema()"]
        dumps_func["dumps()"]
    end
    
    subgraph "LangMem Core Components"
        create_manage_memory_tool["create_manage_memory_tool<br/>Memory Tools"]
        create_search_memory_tool["create_search_memory_tool<br/>Memory Tools"]
        summarize_messages["summarize_messages<br/>Short-Term Memory"]
        create_prompt_optimizer["create_prompt_optimizer<br/>Prompt Optimization"]
        create_multi_prompt_optimizer["create_multi_prompt_optimizer<br/>Prompt Optimization"]
    end
    
    subgraph "External Dependencies"
        BaseStore["BaseStore<br/>from langgraph.store"]
        RunnableConfig["RunnableConfig<br/>from langchain_core.runnables"]
    end
    
    NamespaceTemplate_class --> create_manage_memory_tool
    NamespaceTemplate_class --> create_search_memory_tool
    NamespaceTemplate_class --> BaseStore
    NamespaceTemplate_class --> RunnableConfig
    
    get_conversation_func --> summarize_messages
    get_dialated_windows_func --> summarize_messages
    format_sessions_func --> create_prompt_optimizer
    format_sessions_func --> create_multi_prompt_optimizer
    
    get_var_healer_func --> create_prompt_optimizer
    get_prompt_extraction_schema_func --> create_prompt_optimizer
    
    dumps_func --> BaseStore
```

Sources: [src/langmem/utils.py:15-91](), [src/langmem/utils.py:98-100](), [src/langmem/utils.py:165-209]()

## Utility Function Reference Table

Here's a summary of the utility functions available in LangMem:

| Function | Purpose | Location |
|----------|---------|----------|
| `NamespaceTemplate` | Templates namespace strings with variable substitution | [src/langmem/utils.py:15-91]() |
| `get_conversation` | Formats message lists into readable conversation strings | [src/langmem/utils.py:98-100]() |
| `get_dialated_windows` | Creates exponentially growing conversation windows | [src/langmem/utils.py:103-119]() |
| `format_sessions` | Formats conversation sessions with optional feedback | [src/langmem/utils.py:125-162]() |
| `get_var_healer` | Creates a function to preserve variables in strings | [src/langmem/utils.py:165-209]() |
| `get_prompt_extraction_schema` | Creates schema for validating optimized prompts | [src/langmem/utils.py:212-248]() |
| `dumps` | Serializes objects to JSON strings | [src/langmem/utils.py:251-252]() |
| `create_prompt_optimizer` | Creates a single prompt optimizer | [src/langmem/prompts/optimization.py:50-269]() |
| `create_multi_prompt_optimizer` | Creates a multi-prompt optimizer | [src/langmem/prompts/optimization.py:471-616]() |

Sources: [src/langmem/utils.py:1-252](), [src/langmem/prompts/optimization.py:50-269](), [src/langmem/prompts/optimization.py:471-616]()

---

# Page: Development

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [pyproject.toml](pyproject.toml)

</details>



This section covers information for developers who want to contribute to LangMem or understand its internal development processes. It includes details about the project structure, build system, dependency management, and development workflows.

For information about using LangMem in your applications, see [Overview](#1). For API documentation, see [API Reference](#9).

## Development Environment

LangMem uses the `uv` package manager for dependency management and workspace configuration. The project follows modern Python packaging standards with a `pyproject.toml`-based configuration.

### Package Manager and Build System

The project uses `uv` as the primary package manager with workspace support:

```mermaid
graph TD
    UV["uv package manager"] --> PYPROJECT["pyproject.toml"]
    UV --> WORKSPACE["uv.workspace"]
    
    PYPROJECT --> HATCH["hatchling build backend"]
    PYPROJECT --> DEPS["Runtime dependencies"]
    PYPROJECT --> DEVDEPS["dev dependency group"]
    PYPROJECT --> DOCSDEPS["docs dependency group"]
    
    WORKSPACE --> MEMBERS["workspace members"]
    MEMBERS --> EVALSGEN["evals/gen"]
    
    HATCH --> BUILD["Build artifacts"]
    HATCH --> EXCLUDE["Build exclusions"]
    
    DEVDEPS --> PYTEST["pytest testing"]
    DEVDEPS --> RUFF["ruff linting"]
    DEVDEPS --> LANGGRAPH["langgraph-cli"]
    
    DOCSDEPS --> MKDOCS["mkdocs"]
    DOCSDEPS --> MKDOCSTRINGS["mkdocstrings"]
```

Sources: [pyproject.toml:1-93]()

The build system uses `hatchling` as the backend with specific exclusion patterns for development and testing files. Key configuration elements:

| Component | Configuration | Location |
|-----------|---------------|----------|
| Build Backend | `hatchling.build` | [pyproject.toml:23-24]() |
| Package Discovery | `src/` layout | [pyproject.toml:19-20]() |
| Workspace | `uv.workspace` | [pyproject.toml:55-56]() |
| Linting | `ruff` with specific rules | [pyproject.toml:58-74]() |

### Dependency Groups

LangMem organizes dependencies into distinct groups for different development contexts:

**Runtime Dependencies** ([pyproject.toml:8-17]())
- Core LangChain ecosystem packages (`langchain`, `langchain-core`, `langgraph`)
- LLM provider integrations (`langchain-openai`, `langchain-anthropic`)
- Utilities (`trustcall`, `langsmith`)

**Development Dependencies** ([pyproject.toml:27-37]())
- Testing framework (`pytest`, `pytest-watch`, `pytest-xdist`)
- Code quality (`ruff` for linting and formatting)
- LangGraph development tools (`langgraph-cli[inmem]`)

**Documentation Dependencies** ([pyproject.toml:38-53]())
- MkDocs ecosystem (`mkdocs`, `mkdocs-material`, `mkdocstrings`)
- Documentation plugins and utilities

## Project Structure

```mermaid
graph TD
    ROOT["Project Root"] --> SRC["src/"]
    ROOT --> TESTS["tests/"]
    ROOT --> DOCS["docs/"]
    ROOT --> EVALS["evals/"]
    ROOT --> CONFIG["Configuration Files"]
    
    SRC --> LANGMEM["langmem/"]
    LANGMEM --> KNOWLEDGE["knowledge/"]
    LANGMEM --> SHORTTERM["short_term/"]
    LANGMEM --> PROMPTS["prompts/"]
    LANGMEM --> REFLECTION["reflection/"]
    LANGMEM --> UTILS["utils/"]
    
    TESTS --> TESTFILES["*.py test files"]
    DOCS --> DOCSOURCE["Documentation source"]
    EVALS --> EVALSGEN["evals/gen workspace member"]
    
    CONFIG --> PYPROJECT["pyproject.toml"]
    CONFIG --> GITIGNORE[".gitignore"]
    CONFIG --> LICENSE["LICENSE"]
    CONFIG --> README["README.md"]
    
    KNOWLEDGE --> EXTRACTION["extraction.py"]
    KNOWLEDGE --> TOOLS["tools.py"]
    SHORTTERM --> SUMMARIZATION["summarization.py"]
    PROMPTS --> OPTIMIZATION["optimization.py"]
    REFLECTION --> REFLECTIONPY["reflection.py"]
    UTILS --> NAMESPACE["namespace.py"]
```

Sources: [pyproject.toml:19-20](), [pyproject.toml:76-92]()

The project follows the `src/` layout pattern, with source code organized under `src/langmem/`. Build exclusions are configured to prevent development artifacts from being included in distributions.

## Build Exclusions and Artifacts

The build system explicitly excludes development and testing artifacts:

```mermaid
graph LR
    HATCHBUILD["hatch.build.exclude"] --> TESTDIR["tests/"]
    HATCHBUILD --> DOCSDIR["docs/"]
    HATCHBUILD --> GITHUB[".github/"]
    HATCHBUILD --> EXAMPLES["examples.py & examples/"]
    HATCHBUILD --> DEVFILES["Development files"]
    
    DEVFILES --> EDITORCONFIG[".editorconfig"]
    DEVFILES --> DBDIR["db/"]
    DEVFILES --> EVALSDIR["evals/"]
    DEVFILES --> LANGGRAPHAPI[".langgraph_api"]
    DEVFILES --> NOTEBOOKS["*.ipynb"]
    DEVFILES --> PYTHONVERSION[".python-version"]
    DEVFILES --> VENV[".venv*/**"]
    DEVFILES --> PYTEST["pytest.ini"]
```

Sources: [pyproject.toml:76-92]()

This configuration ensures that only the core `langmem` package and essential metadata are included in built distributions.

## Code Quality and Linting

LangMem uses `ruff` for both linting and code formatting with specific rule configurations:

### Ruff Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| Line Length | 88 characters | [pyproject.toml:61]() |
| Indent Width | 4 spaces | [pyproject.toml:62]() |
| Selected Rules | `E`, `F`, `I`, `TID251` | [pyproject.toml:59]() |
| Ignored Rules | `E501` (line too long) | [pyproject.toml:60]() |
| Extended Include | `*.ipynb` | [pyproject.toml:63]() |

### Import Management

The configuration includes specific rules for import management, including banned API patterns:

```mermaid
graph TD
    RUFF["ruff linting"] --> IMPORTS["Import rules"]
    RUFF --> FORMAT["Code formatting"]
    
    IMPORTS --> TIDYIMPORTS["flake8-tidy-imports"]
    IMPORTS --> ISORT["Import sorting"]
    
    TIDYIMPORTS --> BANNEDAPI["Banned API rules"]
    BANNEDAPI --> TYPEDDICT["typing.TypedDict -> typing_extensions.TypedDict"]
    
    FORMAT --> QUOTES["Double quotes"]
    FORMAT --> INDENTS["Space indentation"]  
    FORMAT --> DOCSTRINGS["Docstring formatting"]
    FORMAT --> LINEENDING["Auto line endings"]
```

Sources: [pyproject.toml:58-74]()

## Version Management

The project maintains version information in the `pyproject.toml` file:

- Current version: `0.0.30` ([pyproject.toml:3]())
- Python requirement: `>=3.10` ([pyproject.toml:6]())
- License: MIT ([pyproject.toml:7](), [LICENSE:1-21]())

## Development Workflow

The development environment supports various workflows through the dependency groups and tooling configuration:

```mermaid
graph TD
    DEVSETUP["Development Setup"] --> UVINSTALL["uv install --dev"]
    DEVSETUP --> DOCSSETUP["uv install --docs"]
    
    UVINSTALL --> TESTING["Testing Workflow"]
    UVINSTALL --> LINTING["Code Quality"]
    
    TESTING --> PYTEST["pytest execution"]
    TESTING --> PYTESTWATCH["pytest-watch"]
    TESTING --> PYTESTXDIST["pytest-xdist parallel"]
    
    LINTING --> RUFFCHECK["ruff check"]
    LINTING --> RUFFFORMAT["ruff format"]
    
    DOCSSETUP --> MKDOCSBUILD["mkdocs build"]
    DOCSSETUP --> MKDOCSSERVE["mkdocs serve"]
    
    PYTEST --> ANYIO["anyio async testing"]
    PYTEST --> LANGGRAPHCLI["langgraph-cli[inmem]"]
```

Sources: [pyproject.toml:26-37](), [pyproject.toml:38-53]()

The workspace configuration supports additional evaluation components through the `evals/gen` member, enabling extended testing and evaluation workflows.

---

# Page: Project Structure

# Project Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This document describes the organization of the langmem codebase, including its build system, package configuration, dependency management, and development tools setup. Understanding this structure is essential for contributing to the project and maintaining consistency across the codebase.

For information about the actual memory management components and their APIs, see [Memory Management](#2) and [API Reference](#9).

## Package Configuration and Build System

The langmem project uses a modern Python packaging setup with `pyproject.toml` as the central configuration file. The package is built using the `hatchling` build backend and follows PEP 517/518 standards.

### Package Metadata

```mermaid
flowchart TD
    subgraph "Package Configuration"
        PT["pyproject.toml"]
        PT --> PM["Package Metadata"]
        PT --> BS["Build System"]
        PT --> DG["Dependency Groups"]
        PT --> WS["Workspace Config"]
    end
    
    subgraph "Package Metadata"
        PM --> Name["name = 'langmem'"]
        PM --> Version["version = '0.0.30'"]
        PM --> Desc["description = 'Memory management utilities'"]
        PM --> Python["requires-python = '>=3.10'"]
        PM --> License["license = { file = 'LICENSE' }"]
    end
    
    subgraph "Build System"
        BS --> Hatch["hatchling"]
        BS --> FindPkg["find = { where = ['src'] }"]
        BS --> Excludes["Build Excludes"]
    end
    
    subgraph "Dependency Groups"
        DG --> CoreDeps["Core Dependencies"]
        DG --> DevDeps["dev = [pytest, ruff, ...]"]
        DG --> DocsDeps["docs = [mkdocs, mkdocstrings, ...]"]
    end
    
    subgraph "Workspace Config"
        WS --> UVWorkspace["uv.workspace"]
        WS --> Members["members = ['evals/gen']"]
    end
```

Sources: [pyproject.toml:1-24]()

### Core Dependencies

The project has carefully selected dependencies that align with the LangChain ecosystem:

| Category | Dependencies | Purpose |
|----------|--------------|---------|
| Core | `langchain>=0.3.15`, `langchain-core>=0.3.46` | Base LangChain functionality |
| Graph | `langgraph>=0.3.23`, `langgraph-checkpoint>=2.0.12` | State management and persistence |
| LLMs | `langchain-openai>=0.3.1`, `langchain-anthropic>=0.3.3` | Language model integrations |
| Tools | `trustcall>=0.0.39`, `langsmith>=0.3.8` | Function calling and observability |

Sources: [pyproject.toml:8-17]()

## Directory Structure and Build Configuration

The project follows a standard Python package structure with source code in the `src/` directory. The build system excludes development and documentation files from the distributed package.

### Source Organization

```mermaid
flowchart TD
    subgraph "Project Root"
        SRC["src/"]
        TESTS["tests/"]
        DOCS["docs/"]
        EXAMPLES["examples/"]
        EVALS["evals/"]
        CONFIG["Configuration Files"]
    end
    
    subgraph "Source Directory"
        SRC --> LANGMEM["langmem/"]
        LANGMEM --> CORE["Core Modules"]
        LANGMEM --> MEMORY["Memory Management"]
        LANGMEM --> TOOLS["Agent Tools"]
        LANGMEM --> STORAGE["Storage Backends"]
    end
    
    subgraph "Build Exclusions"
        TESTS --> EXCLUDED["Excluded from build"]
        DOCS --> EXCLUDED
        EXAMPLES --> EXCLUDED
        EVALS --> EXCLUDED
        DB["db/"] --> EXCLUDED
        NOTEBOOKS["*.ipynb"] --> EXCLUDED
        VENV[".venv*/"] --> EXCLUDED
    end
    
    subgraph "Configuration Files"
        CONFIG --> PYPROJECT["pyproject.toml"]
        CONFIG --> PYTEST["pytest.ini"]
        CONFIG --> EDITOR[".editorconfig"]
        CONFIG --> PYTHON[".python-version"]
        CONFIG --> LANGGRAPH[".langgraph_api"]
    end
```

Sources: [pyproject.toml:19-21](), [pyproject.toml:76-92]()

### Workspace Configuration

The project uses `uv` for dependency management with workspace support:

```mermaid
flowchart LR
    subgraph "UV Workspace"
        ROOT["langmem (root)"]
        EVAL_GEN["evals/gen"]
        
        ROOT --> MAIN_DEPS["Main Dependencies"]
        ROOT --> DEV_DEPS["Development Dependencies"]
        ROOT --> DOC_DEPS["Documentation Dependencies"]
        
        EVAL_GEN --> EVAL_DEPS["Evaluation Dependencies"]
        
        MAIN_DEPS --> LOCK["uv.lock"]
        DEV_DEPS --> LOCK
        DOC_DEPS --> LOCK
        EVAL_DEPS --> LOCK
    end
```

Sources: [pyproject.toml:55-56]()

## Development Tools Configuration

The project includes comprehensive development tool configuration for code quality, testing, and documentation.

### Code Quality Tools

```mermaid
flowchart TD
    subgraph "Development Tools"
        RUFF["ruff"]
        PYTEST["pytest"]
        MKDOCS["mkdocs"]
    end
    
    subgraph "Ruff Configuration"
        RUFF --> SELECT["lint.select = ['E', 'F', 'I', 'TID251']"]
        RUFF --> IGNORE["lint.ignore = ['E501']"]
        RUFF --> LENGTH["line-length = 88"]
        RUFF --> INDENT["indent-width = 4"]
        RUFF --> NOTEBOOKS["extend-include = ['*.ipynb']"]
    end
    
    subgraph "Format Settings"
        RUFF --> QUOTES["quote-style = 'double'"]
        RUFF --> SPACES["indent-style = 'space'"]
        RUFF --> DOCSTRING["docstring-code-format = true"]
        RUFF --> ENDINGS["line-ending = 'auto'"]
    end
    
    subgraph "Import Bans"
        RUFF --> TYPEDDICT["typing.TypedDict -> typing_extensions.TypedDict"]
    end
    
    subgraph "Test Configuration"
        PYTEST --> XDIST["pytest-xdist for parallel testing"]
        PYTEST --> WATCH["pytest-watch for development"]
        PYTEST --> ANYIO["anyio for async testing"]
    end
```

Sources: [pyproject.toml:58-75]()

### Development Dependencies

The development environment includes tools for testing, linting, and development workflow:

| Tool | Purpose | Version Constraint |
|------|---------|-------------------|
| `pytest` | Test framework | `>=8.3.4` |
| `pytest-xdist` | Parallel test execution | `>=3.6.1` |
| `pytest-watch` | Continuous testing | `>=4.2.0` |
| `anyio` | Async testing support | `>=4.8.0` |
| `langgraph-cli[inmem]` | Development CLI | `>=0.1.70` |
| `langgraph-prebuilt` | Prebuilt components | `>=0.1.1` |

Sources: [pyproject.toml:26-36]()

## Documentation Structure

The documentation system uses MkDocs with Material theme and comprehensive plugin support for API documentation generation.

### Documentation Configuration

```mermaid
flowchart TD
    subgraph "Documentation System"
        MKDOCS["mkdocs.yml"]
        MATERIAL["Material Theme"]
        PLUGINS["Plugin System"]
        CONTENT["Content Structure"]
    end
    
    subgraph "MkDocs Configuration"
        MKDOCS --> SITE["site_name: 'LangMem'"]
        MKDOCS --> URL["site_url: langchain-ai.github.io/langmem"]
        MKDOCS --> REPO["repo_url: github.com/langchain-ai/langmem"]
        MKDOCS --> EDIT["edit_uri: edit/main/docs/docs/"]
    end
    
    subgraph "Theme Configuration"
        MATERIAL --> LOGOS["Custom logos (light/dark)"]
        MATERIAL --> FAVICON["favicon.png"]
        MATERIAL --> FEATURES["Navigation features"]
        MATERIAL --> PALETTE["Color schemes"]
        MATERIAL --> FONTS["Public Sans / Roboto Mono"]
    end
    
    subgraph "Plugin System"
        PLUGINS --> SEARCH["Search with custom separator"]
        PLUGINS --> AUTOREFS["Auto-reference linking"]
        PLUGINS --> REDIRECTS["URL redirects"]
        PLUGINS --> MKDOCSTRINGS["API documentation"]
    end
    
    subgraph "Content Navigation"
        CONTENT --> INTRO["Introduction"]
        CONTENT --> QUICKSTART["Quickstart guides"]
        CONTENT --> CONCEPTS["Concepts"]
        CONTENT --> HOWTO["How-to guides"]
        CONTENT --> REFERENCE["API Reference"]
    end
```

Sources: [docs/mkdocs.yml:1-120]()

### API Documentation Generation

The documentation system automatically generates API reference from docstrings:

```mermaid
flowchart LR
    subgraph "API Documentation Pipeline"
        DOCSTRINGS["Python Docstrings"]
        MKDOCSTRINGS["mkdocstrings plugin"]
        TEMPLATES["Custom templates"]
        OUTPUT["Generated docs"]
    end
    
    subgraph "Configuration"
        PRELOAD["Preload modules"]
        IMPORTS["External object inventories"]
        OPTIONS["Display options"]
    end
    
    DOCSTRINGS --> MKDOCSTRINGS
    MKDOCSTRINGS --> TEMPLATES
    TEMPLATES --> OUTPUT
    
    PRELOAD --> MKDOCSTRINGS
    IMPORTS --> MKDOCSTRINGS
    OPTIONS --> MKDOCSTRINGS
    
    subgraph "Preloaded Modules"
        PRELOAD --> LANGCHAIN["langchain"]
        PRELOAD --> LANGCHAIN_CORE["langchain_core"]
        PRELOAD --> LANGGRAPH["langgraph"]
    end
    
    subgraph "External References"
        IMPORTS --> PYTHON_DOCS["Python 3 docs"]
        IMPORTS --> LANGCHAIN_DOCS["LangChain API reference"]
    end
```

Sources: [docs/mkdocs.yml:60-93]()

### Documentation Dependencies

The documentation build requires specialized packages:

| Package | Purpose | Version |
|---------|---------|---------|
| `mkdocs` | Static site generator | `>=1.6.1` |
| `mkdocs-material` | Material design theme | `>=9.6.1` |
| `mkdocstrings` | API doc generation | `>=0.27.0` |
| `mkdocstrings-python` | Python support | `>=1.13.0` |
| `markdown-callouts` | Callout styling | `>=0.4.0` |
| `markdown-include` | File inclusion | `>=0.8.1` |

Sources: [pyproject.toml:37-53]()

## Development Workflow Integration

The project structure supports modern Python development workflows with comprehensive tooling integration.

### Build and Release Process

```mermaid
flowchart TD
    subgraph "Development Workflow"
        DEV["Development"]
        TEST["Testing"]
        LINT["Linting"]
        DOCS["Documentation"]
        BUILD["Build"]
        RELEASE["Release"]
    end
    
    subgraph "Tool Chain"
        UV["uv (dependency management)"]
        PYTEST["pytest (testing)"]
        RUFF["ruff (linting/formatting)"]
        MKDOCS["mkdocs (documentation)"]
        HATCH["hatchling (build)"]
    end
    
    DEV --> UV
    TEST --> PYTEST
    LINT --> RUFF
    DOCS --> MKDOCS
    BUILD --> HATCH
    
    UV --> LOCK["uv.lock"]
    PYTEST --> COVERAGE["Test coverage"]
    RUFF --> FORMATTED["Formatted code"]
    MKDOCS --> SITE["Documentation site"]
    HATCH --> WHEEL["Package wheel"]
    
    subgraph "Quality Gates"
        COVERAGE --> QUALITY["Quality checks"]
        FORMATTED --> QUALITY
        SITE --> QUALITY
        WHEEL --> QUALITY
    end
    
    QUALITY --> RELEASE
```

Sources: [pyproject.toml:22-24](), [pyproject.toml:26-53]()

This project structure provides a solid foundation for collaborative development while maintaining high code quality and comprehensive documentation. The configuration files work together to create a seamless development experience with modern Python tooling.

---

# Page: Contributing

# Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [docs/mkdocs.yml](docs/mkdocs.yml)
- [tests/test_docstring_examples.py](tests/test_docstring_examples.py)

</details>



This guide covers the contribution workflow for LangMem, including development environment setup, testing procedures, documentation generation, and the release process. It provides the technical details needed to contribute code, documentation, and improvements to the project.

For information about the overall project structure and codebase organization, see [Project Structure](#10.1).

## Development Environment Setup

LangMem uses `uv` as its package manager and build system. The development environment is configured through the `pyproject.toml` file with dependencies managed via `uv.lock`.

### Package Management

The project uses `uv` for all package management operations:

```bash
# Install development environment
uv sync

# Add new dependencies
uv add <package-name>

# Build package
uv build

# Publish package
uv publish
```

**Development Environment Setup Process**

```mermaid
graph TD
    subgraph "Development Setup"
        pyproject["pyproject.toml<br/>Project Configuration"]
        uvlock["uv.lock<br/>Dependency Lock File"]
        uvcmd["uv sync<br/>Install Dependencies"]
        devenv["Development Environment<br/>Ready for Contribution"]
    end
    
    pyproject --> uvcmd
    uvlock --> uvcmd
    uvcmd --> devenv
    
    subgraph "Key Configuration"
        pythonver["Python Version<br/>from pyproject.toml"]
        deps["Dependencies<br/>langchain, langgraph, etc"]
        testdeps["Test Dependencies<br/>pytest, anyio"]
    end
    
    devenv --> pythonver
    devenv --> deps
    devenv --> testdeps
```

Sources: [.github/workflows/release.yml:14-24](), [pyproject.toml]()

## Testing

The testing system automatically validates code examples from both docstrings and documentation files. The primary test runner is implemented in `test_docstring_examples.py`.

### Docstring Example Testing

The testing framework extracts and executes Python code blocks from:
- Function and class docstrings in the `src/` directory
- Markdown files in the `docs/docs/` directory  
- The main `README.md` file

**Test Discovery and Execution Pipeline**

```mermaid
graph TB
    subgraph "Test Discovery"
        srcdir["src/ Directory<br/>Python Files"]
        docsdir["docs/docs/ Directory<br/>Markdown Files"]
        readme["README.md<br/>Main Documentation"]
        
        visitor["DocstringVisitor<br/>AST-based Extraction"]
        extractor["extract_code_blocks()<br/>Markdown Parser"]
    end
    
    subgraph "Code Block Processing"
        setupblocks["get_file_setup()<br/>File-level Setup"]
        codeblocks["Code Blocks<br/>Python Examples"]
        testcases["pytest.param<br/>Test Cases"]
    end
    
    subgraph "Test Execution"
        namespace["Execution Namespace<br/>Isolated Context"]
        langsmith["ls.tracing_context<br/>LangSmith Tracing"]
        asyncexec["Async Execution<br/>await support"]
    end
    
    srcdir --> visitor
    docsdir --> extractor
    readme --> extractor
    
    visitor --> setupblocks
    visitor --> codeblocks
    extractor --> codeblocks
    
    setupblocks --> testcases
    codeblocks --> testcases
    
    testcases --> namespace
    namespace --> langsmith
    namespace --> asyncexec
```

### Test Configuration

The test system uses several key components:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `DocstringVisitor` | Extract code blocks from Python AST | [tests/test_docstring_examples.py:97-129]() |
| `extract_code_blocks()` | Parse markdown code blocks | [tests/test_docstring_examples.py:52-94]() |
| `get_file_setup()` | Extract file-level setup code | [tests/test_docstring_examples.py:25-49]() |
| `collect_docstring_tests()` | Generate pytest parameters | [tests/test_docstring_examples.py:183-232]() |

### Special Test Features

- **Setup Blocks**: File-level setup code in comments starting with `# ```python setup`
- **Async Support**: Automatic detection and handling of `await` statements
- **Namespace Isolation**: Each test maintains its own execution context
- **LangSmith Integration**: All tests run under `langmem_docstrings` project tracing
- **Selective Skipping**: CrewAI examples skip in CI but test locally

Sources: [tests/test_docstring_examples.py:1-298]()

## Documentation

Documentation is built using MkDocs with the Material theme and several plugins for enhanced functionality.

### Documentation Stack

The documentation system uses:

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| MkDocs | Static site generator | [docs/mkdocs.yml:1-5]() |
| Material Theme | Modern documentation theme | [docs/mkdocs.yml:6-53]() |
| mkdocstrings | API reference generation | [docs/mkdocs.yml:60-92]() |
| Mermaid | Diagram rendering | [docs/mkdocs.yml:162-164]() |

### Documentation Build Process

```mermaid
graph TD
    subgraph "Source Content"
        markdown["Markdown Files<br/>docs/docs/*.md"]
        docstrings["Python Docstrings<br/>src/**/*.py"]
        notebooks["Notebook Hooks<br/>_scripts/notebook_hooks.py"]
    end
    
    subgraph "MkDocs Processing"
        mkdocs["MkDocs Engine<br/>Site Generation"]
        material["Material Theme<br/>UI Components"]
        mkdocstrings["mkdocstrings Plugin<br/>API Reference"]
        mermaid["Mermaid Plugin<br/>Diagram Rendering"]
    end
    
    subgraph "Output"
        staticsite["Static Site<br/>langchain-ai.github.io/langmem"]
        apidocs["API Reference<br/>Generated from Code"]
    end
    
    markdown --> mkdocs
    docstrings --> mkdocstrings
    notebooks --> mkdocs
    
    mkdocs --> material
    mkdocstrings --> apidocs
    mkdocs --> mermaid
    
    material --> staticsite
    apidocs --> staticsite
    mermaid --> staticsite
```

### Key Documentation Features

- **Auto-generated API Reference**: Using mkdocstrings with Google-style docstrings
- **Cross-references**: Automatic linking with autorefs plugin
- **Code Highlighting**: Pygments-based syntax highlighting
- **Mermaid Diagrams**: Native diagram support for system documentation
- **Mobile Responsive**: Material theme with responsive design
- **Search**: Full-text search with advanced features

**Navigation Structure**:
- Introduction and quickstarts
- Conceptual guides
- How-to guides
- API reference with automatic generation

Sources: [docs/mkdocs.yml:1-201]()

## Release Process

LangMem uses GitHub Actions for automated building and releasing to PyPI.

### Release Workflow

The release process is triggered manually through GitHub's workflow dispatch:

**Release Pipeline**

```mermaid
graph TD
    subgraph "Release Trigger"
        dispatch["Workflow Dispatch<br/>Manual Trigger"]
    end
    
    subgraph "Build Environment"
        checkout["Checkout Code<br/>actions/checkout@v4"]
        setupuv["Install uv<br/>astral-sh/setup-uv@v5"]
        setuppy["Setup Python<br/>from pyproject.toml"]
        cache["Enable Cache<br/>uv.lock dependency"]
    end
    
    subgraph "Build Process"
        uvbuild["uv build<br/>Package Creation"]
        artifacts["Built Artifacts<br/>wheel and sdist"]
    end
    
    subgraph "Publication"
        pypi["PyPI Publication<br/>uv publish"]
        token["UV_PUBLISH_TOKEN<br/>GitHub Secret"]
    end
    
    dispatch --> checkout
    checkout --> setupuv
    setupuv --> setuppy
    setuppy --> cache
    
    cache --> uvbuild
    uvbuild --> artifacts
    
    artifacts --> pypi
    token --> pypi
```

### Release Configuration

| Step | Tool | Configuration |
|------|------|---------------|
| Environment Setup | `uv` v0.6.3 | [.github/workflows/release.yml:14-19]() |
| Python Version | `pyproject.toml` | [.github/workflows/release.yml:24]() |
| Package Build | `uv build` | [.github/workflows/release.yml:28]() |
| PyPI Upload | `uv publish` | [.github/workflows/release.yml:30-33]() |

### Release Security

- **Secret Management**: Uses `PYPI_API_TOKEN` stored in GitHub secrets
- **Manual Trigger**: Requires explicit workflow dispatch to prevent accidental releases
- **Dependency Caching**: Caches based on `uv.lock` for consistent builds

Sources: [.github/workflows/release.yml:1-33]()

## Contribution Workflow

### Code Contributions

1. **Setup Development Environment**:
   ```bash
   git clone https://github.com/langchain-ai/langmem
   cd langmem
   uv sync
   ```

2. **Run Tests**:
   ```bash
   pytest tests/
   # Run specific docstring tests
   pytest tests/test_docstring_examples.py -v
   ```

3. **Update Documentation**:
   - Add docstring examples to new functions
   - Update markdown files in `docs/docs/`
   - Test examples are automatically validated

4. **Build Documentation Locally**:
   ```bash
   mkdocs serve
   ```

### Testing Guidelines

- All public functions should include docstring examples
- Code blocks in docstrings must be executable
- Use `# ```python setup` for file-level test setup
- Mark non-executable blocks with `skip` in the language identifier

### Documentation Guidelines

- Follow Google-style docstrings for API documentation
- Include practical examples in how-to guides
- Use mermaid diagrams for system architecture
- Test all code examples automatically

**Contribution Validation Pipeline**

```mermaid
graph LR
    subgraph "Developer Actions"
        code["Write Code<br/>with Docstrings"]
        docs["Update Docs<br/>Markdown Files"]
        test["Run Tests<br/>pytest"]
    end
    
    subgraph "Automated Validation"
        doctest["test_docstring_examples<br/>Code Validation"]
        mkdocstest["mkdocs build<br/>Doc Validation"]
        langsmith["LangSmith Tracing<br/>Test Observability"]
    end
    
    subgraph "Integration"
        pr["Pull Request<br/>GitHub Review"]
        merge["Merge<br/>Main Branch"]
        release["Release<br/>Manual Trigger"]
    end
    
    code --> doctest
    docs --> mkdocstest
    test --> langsmith
    
    doctest --> pr
    mkdocstest --> pr
    langsmith --> pr
    
    pr --> merge
    merge --> release
```

Sources: [.github/workflows/release.yml:1-33](), [tests/test_docstring_examples.py:235-298](), [docs/mkdocs.yml:94-201]()