<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Agent-Toolkit · page 13 Agent Performance Primitives (APP) · fetched 2026-10-26 -->

# Agent Performance Primitives (APP)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ci/markdown-link-check-config.json](ci/markdown-link-check-config.json)
- [ci/scripts/path_checks.py](ci/scripts/path_checks.py)
- [ci/vale/styles/config/vocabularies/nat/accept.txt](ci/vale/styles/config/vocabularies/nat/accept.txt)
- [docs/Makefile](docs/Makefile)
- [docs/source/build-workflows/memory.md](docs/source/build-workflows/memory.md)
- [docs/source/components/agents/auto-memory-wrapper/auto-memory-wrapper.md](docs/source/components/agents/auto-memory-wrapper/auto-memory-wrapper.md)
- [docs/source/components/integrations/index.md](docs/source/components/integrations/index.md)
- [docs/source/components/integrations/integrating-oci-generative-ai-models.md](docs/source/components/integrations/integrating-oci-generative-ai-models.md)
- [docs/source/conf.py](docs/source/conf.py)
- [docs/source/index.md](docs/source/index.md)
- [examples/README.md](examples/README.md)
- [examples/agents/auto_memory_wrapper/README.md](examples/agents/auto_memory_wrapper/README.md)
- [examples/memory/memanto/README.md](examples/memory/memanto/README.md)
- [packages/nvidia_nat_langchain/src/nat/plugins/langchain/agent/auto_memory_wrapper/agent.py](packages/nvidia_nat_langchain/src/nat/plugins/langchain/agent/auto_memory_wrapper/agent.py)

</details>



The Agent Performance Primitives (APP) package, `nvidia-nat-app`, provides a high-performance execution layer for agentic workflows [uv.lock:57](), [pyproject.toml:57](), [pyproject.toml:99](). It offers framework-agnostic primitives for graph compilation, parallel task scheduling, and speculative execution to significantly reduce the latency of complex agent systems.

While standard agent frameworks execute nodes sequentially, APP analyzes the underlying execution graph to identify optimization opportunities, such as running independent tools in parallel or speculating on the next likely state in a conditional flow.

Sources: [uv.lock:57](), [pyproject.toml:57](), [pyproject.toml:99]()

## Core Capabilities

The APP package focuses on three primary performance pillars:

| Feature | Description |
| :--- | :--- |
| **Graph Compilation** | Transforms high-level agent definitions into optimized execution plans by analyzing topology and data dependencies. |
| **Parallel Scheduling** | Automatically identifies and executes independent branches of an agent graph concurrently using conflict detection. |
| **Speculative Execution** | Reduces latency in conditional logic by pre-computing likely future states based on early signals from router nodes. |

Sources: [uv.lock:57](), [pyproject.toml:57](), [pyproject.toml:99]()

## System Integration

APP is designed to sit between the high-level workflow definition and the low-level execution. It bridges the gap between natural language reasoning and efficient code execution by profiling state access and node relationships. The system integrates with the core `Runner` and `Context` to manage execution state [packages/nvidia_nat_core/src/nat/runtime/runner.py:52-80](), [packages/nvidia_nat_core/src/nat/builder/context.py:142-146]().

### From Natural Language to Code Entity Space: Runtime Mapping

The following diagram bridges natural language execution intent to concrete code entities within the toolkit's runtime and data models.

**APP Entity Mapping**
```mermaid
graph TD
    subgraph "Natural_Language_Space" ["Natural Language Space"]
        "Agent_Logic"["Agent Logic & Flow"]
        "Parallel_Tasks"["Parallel Tasks"]
        "Conditional_Branch"["Conditional Branching"]
        "Execution_State"["Execution State"]
    end

    subgraph "Code_Entity_Space" ["Code Entity Space"]
        "Runner"["Runner"]
        "ContextState"["ContextState"]
        "InvocationNode"["InvocationNode"]
        "SpanKind"["SpanKind"]
        "IntermediateStep"["IntermediateStep"]
    end

    "Agent_Logic" --> "Runner"
    "Parallel_Tasks" --> "InvocationNode"
    "Conditional_Branch" --> "SpanKind"
    "Execution_State" --> "ContextState"
    "Agent_Logic" --> "IntermediateStep"
```
Sources: [packages/nvidia_nat_core/src/nat/runtime/runner.py:52-80](), [packages/nvidia_nat_core/src/nat/builder/context.py:67-86](), [packages/nvidia_nat_core/src/nat/data_models/invocation_node.py:29-35](), [packages/nvidia_nat_core/src/nat/data_models/span.py:35-51]()

## APP Architecture and Graph Compilation

The graph compilation engine transforms agent workflows into optimized execution structures. It manages a pipeline that extracts graph definitions, validates topology, and performs node analysis to identify parallelization opportunities. 

For detailed information on the `DefaultGraphCompiler` pipeline, compilation stages, and the `quick_optimize` API entry point, see [APP Architecture and Graph Compilation](#13.1).

### From Natural Language to Code Entity Space: Compilation Mapping

The following diagram maps high-level compilation goals to the underlying compiler classes and execution functions.

**Compilation Entity Mapping**
```mermaid
graph TD
    subgraph "Natural_Language_Space" ["Natural Language Space"]
        "Workflow_Definition"["Workflow Definition YAML"]
        "Graph_Optimization"["Graph Optimization Intent"]
        "Topology_Analysis"["Topology Analysis"]
    end

    subgraph "Code_Entity_Space" ["Code Entity Space"]
        "DefaultGraphCompiler"["DefaultGraphCompiler"]
        "quick_optimize"["quick_optimize"]
        "Runner"["Runner"]
    end

    "Workflow_Definition" --> "quick_optimize"
    "Graph_Optimization" --> "DefaultGraphCompiler"
    "Topology_Analysis" --> "Runner"
```
Sources: [packages/nvidia_nat_core/src/nat/runtime/runner.py:52-101](), [packages/nvidia_nat_core/src/nat/data_models/invocation_node.py:29-35]()

## Speculative Execution

Speculative execution in NAT allows an agent to "guess" the outcome of a conditional branch before the LLM has finished generating the full reasoning path. This is particularly useful for reducing Time to First Token (TTFT) and overall interaction latency [README.md:44](), [README.md:65]().

For detailed information on the `SpeculationPlan` system, `router_branch` strategy, `ResolutionPolicy`, and `SpeculationSafetyConfig`, see [Speculative Execution](#13.2).

### Execution Flow Comparison

This diagram compares standard sequential execution against the optimized APP execution flow which leverages parallel groups and speculative triggers.

**Standard vs. APP Execution**
```mermaid
graph LR
    subgraph "Standard_Execution" ["Standard Execution"]
        "S_LLM"["LLM Call"] --> "S_Tool"["Tool Execution"]
        "S_Tool" --> "S_Next"["Next LLM Call"]
    end

    subgraph "APP_Optimized_Execution" ["APP Optimized Execution"]
        "A_LLM"["LLM Call"] -- "Speculative Trigger" --> "A_Spec"["Speculative Tool"]
        "A_LLM" -- "Parallel Group" --> "A_Tool2"["Tool B"]
        "A_LLM" -- "Parallel Group" --> "A_Tool1"["Tool A"]
    end
    
    "A_Spec" -.-> "A_Next"["Next LLM Call"]
    "A_Tool1" --> "A_Next"
    "A_Tool2" --> "A_Next"
```
Sources: [packages/nvidia_nat_core/src/nat/runtime/runner.py:172-188](), [packages/nvidia_nat_core/src/nat/builder/context.py:81-86](), [packages/nvidia_nat_core/src/nat/data_models/span.py:54-82]()

## Framework Adapters

To remain framework-agnostic, APP uses adapters to interface with various ecosystems like LangChain, CrewAI, Agno, and Microsoft Semantic Kernel [README.md:44](), [packages/nvidia_nat_langchain/pyproject.toml:33-36](), [packages/nvidia_nat_semantic_kernel/pyproject.toml:33-36](). These adapters allow the toolkit to extract graphs from third-party frameworks, apply APP optimizations, and then execute them using the NAT `Runner` [packages/nvidia_nat_core/src/nat/runtime/runner.py:52-60]().

Sources: [packages/nvidia_nat_core/src/nat/runtime/runner.py:52-101](), [packages/nvidia_nat_core/src/nat/builder/context.py:67-140](), [README.md:44-45](), [packages/nvidia_nat_langchain/pyproject.toml:62-65](), [packages/nvidia_nat_semantic_kernel/pyproject.toml:64-64]()

---

