<!-- source: DeepWiki mcp.deepwiki.com · repo ShengranHu/ADAS · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [_arc/search.py](_arc/search.py)
- [_drop/search.py](_drop/search.py)
- [_gpqa/search.py](_gpqa/search.py)

</details>



## Purpose and Scope

This document outlines the shared architectural components and design patterns that form the foundation of the ADAS (Automated Diagnostic and Architecture System) framework. The Core Architecture defines the base classes, interfaces, and utilities that power all problem-solving systems across various domains, from abstract reasoning to question answering and mathematical problem solving.

For specifics about the evolutionary search algorithm used to generate solutions, see [Evolutionary Search Algorithm](#2.1). For details on how LLM-generated code is executed, see [Dynamic Code Evaluation](#2.2).

## Key Components Overview

```mermaid
classDiagram
    class LLMAgentBase {
        +output_fields: list
        +agent_name: str
        +role: str
        +model: str
        +temperature: float
        +generate_prompt()
        +query()
        +__call__()
    }
    
    class AgentSystem {
        +forward()
        +run_examples_and_get_feedback()
        +get_test_output_from_code()
    }
    
    class Info {
        +name: str
        +author: str
        +content: str
        +iteration_idx: int
    }
    
    class SearchFunction {
        +search()
        +evaluate()
        +evaluate_forward_fn()
    }
    
    class OpenAIIntegration {
        +get_json_response_from_gpt()
        +get_json_response_from_gpt_reflect()
    }
    
    LLMAgentBase ..> Info : creates/consumes
    LLMAgentBase ..> OpenAIIntegration : uses
    AgentSystem ..> Info : processes
    SearchFunction ..> LLMAgentBase : configures
    SearchFunction ..> AgentSystem : configures
    SearchFunction ..> OpenAIIntegration : uses
```

Sources: [_arc/search.py:20](), [_arc/search.py:31-67](), [_arc/search.py:70-154](), [_arc/search.py:156-234](), [_arc/search.py:237-367]()

## Core Components in Detail

### LLMAgentBase

The `LLMAgentBase` class provides the foundation for all LLM-based agents in the system. It manages interactions with language models and handles prompt construction.

```mermaid
flowchart TD
    subgraph "LLMAgentBase"
        A["__init__()"] --> B["generate_prompt()"]
        B --> C["query()"]
        C --> D["__call__()"]
        
        E["Fields:
        output_fields
        agent_name
        role
        model
        temperature
        id"]
    end
    
    subgraph "Input/Output"
        F["Input: Info Objects"] --> B
        C --> G["Output: Info Objects"]
    end
    
    subgraph "OpenAI API"
        C --> H["get_json_response_from_gpt()"]
        H --> I["OpenAI Chat Completions API"]
    end
```

Key responsibilities:
- Initializes with output field specifications, agent name, role, model, and temperature
- Generates structured prompts combining system instructions and input information
- Handles JSON response formatting and error recovery
- Wraps responses in `Info` objects for consistent information flow

Sources: [_arc/search.py:70-154](), [_drop/search.py:69-138](), [_gpqa/search.py:68-137]()

### AgentSystem

The `AgentSystem` class provides an execution environment for dynamically generated code and handles the evaluation of solutions.

Key features:
- Initialized with example problems and test inputs
- Executes LLM-generated code against examples to provide feedback
- Applies the generated code to test inputs to produce answers
- Manages execution errors and provides diagnostic information

Sources: [_arc/search.py:156-234](), [_drop/search.py:140-142](), [_gpqa/search.py:139-142]()

### Info Structure

The `Info` namedtuple provides a standardized way to represent structured information throughout the system:

```python
Info = namedtuple('Info', ['name', 'author', 'content', 'iteration_idx'])
```

Each field serves a specific purpose:
- `name`: Identifies the type of information (e.g., 'task', 'code', 'answer', 'feedback')
- `author`: Tracks who generated the information
- `content`: Contains the actual information content
- `iteration_idx`: Tracks which iteration of the evolutionary process produced this information

This structure enables consistent information exchange between components and tracking of solution evolution.

Sources: [_arc/search.py:20](), [_drop/search.py:20](), [_gpqa/search.py:19]()

### OpenAI Integration

The system integrates with OpenAI's API through two key functions:

1. `get_json_response_from_gpt`: Sends a single prompt to the API and returns a JSON response
2. `get_json_response_from_gpt_reflect`: Sends a conversation history to enable reflection and refinement

Both functions include:
- Exponential backoff for rate limit handling using the `@backoff.on_exception` decorator
- JSON response format enforcement
- Error handling and validation

Sources: [_arc/search.py:31-67](), [_drop/search.py:30-66](), [_gpqa/search.py:29-65]()

## Search and Evaluation Process

```mermaid
flowchart TB
    Start([Start]) --> LoadArchive["Load/Initialize Archive"]
    LoadArchive --> EvalInitialArchive["Evaluate Initial Solutions"]
    
    subgraph "Solution Generation (search function)"
        EvalInitialArchive --> IterationLoop["Start Generation Loop"]
        IterationLoop --> GetPrompt["Get Prompt from Archive"]
        GetPrompt --> QueryLLM["Query LLM for Solution"]
        QueryLLM --> Reflexion["Apply Reflexion"]
        Reflexion --> EvaluateSolution["Evaluate Solution"]
        EvaluateSolution --> ErrorDetected{Error?}
        ErrorDetected -->|Yes| Debug["Debug with LLM"]
        Debug --> QueryLLM
        ErrorDetected -->|No| CalculateFitness["Calculate Fitness"]
        CalculateFitness --> UpdateArchive["Update Archive"]
        UpdateArchive --> MoreGenerations{More generations?}
        MoreGenerations -->|Yes| IterationLoop
        MoreGenerations -->|No| SaveResults["Save Results"]
    end
    
    SaveResults --> EvalMode["Switch to Evaluation Mode"]
    
    subgraph "Solution Evaluation (evaluate function)"
        EvalMode --> LoadTests["Load Test Data"]
        LoadTests --> DefineFunction["Dynamically Define forward()"]
        DefineFunction --> Execute["Execute in Parallel"]
        Execute --> CalculateMetrics["Calculate Metrics"]
        CalculateMetrics --> ComputeConfidence["Compute Confidence Intervals"]
        ComputeConfidence --> SaveEvalResults["Save Evaluation Results"]
    end
    
    SaveEvalResults --> End([End])
```

The search and evaluation process follows these key steps:

1. **Archive Initialization and Management**:
   - Loads existing archive or initializes with predefined solutions
   - Each solution in the archive contains code, fitness metrics, and metadata

2. **Solution Generation**:
   - Creates prompts based on the current archive
   - Queries the LLM to generate a new solution
   - Applies reflexion prompts to refine the solution

3. **Solution Evaluation**:
   - Dynamically executes the generated code
   - Computes fitness metrics using bootstrap confidence intervals
   - Tracks solution performance

4. **Archive Updates**:
   - Adds new solutions to the archive
   - Maintains solution history for reference and evolution

Sources: [_arc/search.py:237-367](), [_drop/search.py:145-276](), [_gpqa/search.py:144-275]()

## Dynamic Code Execution

```mermaid
flowchart LR
    subgraph "evaluate_forward_fn"
        A["Code String"] --> B["exec() in namespace"]
        B --> C["Extract function"]
        C --> D["Set as AgentSystem.forward"]
        D --> E["Load test data"]
        E --> F["Process in parallel"]
        F --> G["Return accuracy list"]
    end
    
    subgraph "AgentSystem"
        D --> H["forward()"]
        H --> I["Process taskInfo"]
        I --> J["Generate answer"]
    end
    
    subgraph "ThreadPoolExecutor"
        F --> K["Execute tasks in parallel"]
        K --> L["Collect results"]
    end
```

The dynamic code execution mechanism follows these steps:

1. **Function Definition**:
   - The `evaluate_forward_fn` takes LLM-generated code as a string
   - Uses Python's `exec()` to evaluate the code in a controlled namespace
   - Extracts the defined function (typically named `transform` or similar)
   - Dynamically assigns this function as `AgentSystem.forward`

2. **Data Loading and Processing**:
   - Loads task data appropriate for the current domain
   - Creates `AgentSystem` instances and task information
   - Prepares the processing queue

3. **Parallel Execution**:
   - Uses `ThreadPoolExecutor` to process tasks in parallel
   - Handles errors and exceptions at the task level
   - Collects and aggregates results

4. **Confidence Calculation**:
   - Applies bootstrap confidence intervals to compute solution fitness
   - Provides statistical robustness to the evaluation

Sources: [_arc/search.py:369-418](), [_drop/search.py:278-332](), [_gpqa/search.py:277-352]()

## Natural Language to Code Transformation

```mermaid
flowchart TB
    subgraph "Natural Language Space"
        Input["Task Description"] --> Prompt["LLM Prompt"]
        Prompt --> LLMResponse["LLM Response"]
    end
    
    subgraph "Code Entity Space"
        LLMResponse --> CodeGen["Generated Code String"]
        CodeGen --> Namespace["exec() Namespace"]
        Namespace --> FunctionObj["Function Object"]
        FunctionObj --> AgentSystemForward["AgentSystem.forward()"]
        AgentSystemForward --> ExecutionResult["Execution Result"]
    end
    
    subgraph "Assessment Space"
        ExecutionResult --> Accuracy["Accuracy Calculation"]
        Accuracy --> BootstrapCI["bootstrap_confidence_interval()"]
        BootstrapCI --> FitnessScore["Fitness Score"]
    end
```

The system bridges natural language instructions and executable code through:

1. **Prompt Engineering**:
   - Formats task descriptions into structured prompts
   - Includes system instructions and format specifications
   - Incorporates previous solutions for evolutionary improvement

2. **Code Generation**:
   - LLM generates Python code based on the prompt
   - Code is designed to implement a specific transformation or solution strategy
   - The main function (usually named based on the domain) processes input information

3. **Dynamic Assignment**:
   - Code is dynamically executed and assigned to `AgentSystem.forward`
   - This creates a callable interface between natural language instructions and executable code

4. **Evaluation and Feedback**:
   - Results are evaluated and feedback is provided
   - This feedback forms the basis for future generations

Sources: [_arc/search.py:31-154](), [_arc/search.py:369-418](), [_drop/search.py:278-332](), [_gpqa/search.py:277-352]()

## Common Utilities and Patterns

### Error Handling and Rate Limiting

The system incorporates robust error handling and rate limiting mechanisms:

- **Backoff Decorator**: Uses `@backoff.on_exception` to handle OpenAI API rate limits
- **Dynamic Error Recovery**: Attempts to recover from LLM response format errors
- **Code Execution Safety**: Isolates code execution in controlled namespaces
- **Debug Loops**: Implements debugging loops to refine solutions when execution errors occur

### Parallel Processing

Parallel processing is used to efficiently evaluate solutions:

- **ThreadPoolExecutor**: Processes multiple examples in parallel
- **Configurable Workers**: Adjusts the number of workers based on problem size and available resources
- **Progress Tracking**: Uses `tqdm` to provide progress feedback

### Confidence Calculation

Statistical robustness is ensured through:

- **Bootstrap Confidence Intervals**: Calculates confidence intervals to assess solution reliability
- **Multiple Evaluations**: Runs multiple evaluations to ensure consistent performance
- **Fitness Reporting**: Reports fitness as statistical measures rather than point estimates

Sources: [_arc/search.py:31-67](), [_arc/search.py:414-418](), [_drop/search.py:315-332](), [_gpqa/search.py:311-352]()

## Component Reuse Across Problem Domains

```mermaid
flowchart LR
    subgraph "Core Components"
        CoreLLM["LLMAgentBase"]
        CoreInfo["Info Structure"]
        CoreSystem["AgentSystem"]
        CoreSearch["Search Process"]
        CoreEval["Evaluation Process"]
    end
    
    subgraph "ARC (Abstraction and Reasoning)"
        CoreLLM --> ArcLLM["ARC LLMAgentBase"]
        CoreInfo --> ArcInfo["ARC Info"]
        CoreSystem --> ArcSystem["ARC AgentSystem"]
        CoreSearch --> ArcSearch["ARC Search"]
        CoreEval --> ArcEval["ARC Evaluate"]
    end
    
    subgraph "DROP (Reading Comprehension)"
        CoreLLM --> DropLLM["DROP LLMAgentBase"]
        CoreInfo --> DropInfo["DROP Info"]
        CoreSystem --> DropSystem["DROP AgentSystem"]
        CoreSearch --> DropSearch["DROP Search"]
        CoreEval --> DropEval["DROP Evaluate"]
    end
    
    subgraph "GPQA (Question Answering)"
        CoreLLM --> GpqaLLM["GPQA LLMAgentBase"]
        CoreInfo --> GpqaInfo["GPQA Info"]
        CoreSystem --> GpqaSystem["GPQA AgentSystem"]
        CoreSearch --> GpqaSearch["GPQA Search"]
        CoreEval --> GpqaEval["GPQA Evaluate"]
    end
```

The core architecture components are reused across different problem domains with domain-specific adaptations:

| Component | Implementation | Domain-Specific Customization |
|-----------|----------------|-------------------------------|
| LLMAgentBase | [_arc/search.py:70-154]() | Output format, temperature, prompt structure |
| AgentSystem | [_arc/search.py:156-234]() | Run examples, test outputs, error handling |
| Info Structure | [_arc/search.py:20]() | Consistent across domains |
| Search Process | [_arc/search.py:237-332]() | Archive structure, solution format |
| Evaluation | [_arc/search.py:333-418]() | Domain-specific metrics, data formats |

Sources: [_arc/search.py](), [_drop/search.py](), [_gpqa/search.py]()

## Summary

The Core Architecture of ADAS provides a flexible, extensible framework for developing LLM-powered problem-solving systems. By separating concerns into distinct components and providing consistent interfaces between them, the architecture enables:

1. Reuse of common components across different problem domains
2. Consistent handling of LLM interactions, error recovery, and rate limiting
3. Evolutionary improvement of solutions through structured search and evaluation
4. Dynamic execution of LLM-generated code in controlled environments
5. Statistical evaluation of solution quality

These core components form the foundation upon which domain-specific solvers are built, allowing the system to address a wide range of problem types with minimal duplication of effort.

---

