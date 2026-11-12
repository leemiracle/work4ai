<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/Paper2Any · page 11 Development Guide · fetched 2026-11-02 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dataflow_agent/cli.py](dataflow_agent/cli.py)
- [dataflow_agent/templates/agent.py.jinja](dataflow_agent/templates/agent.py.jinja)
- [dataflow_agent/templates/test_workflow.py.jinja](dataflow_agent/templates/test_workflow.py.jinja)
- [dataflow_agent/templates/workflow.py.jinja](dataflow_agent/templates/workflow.py.jinja)
- [docs/contributing.md](docs/contributing.md)
- [docs/guides/index.md](docs/guides/index.md)
- [docs/guides/open_source_deployment.md](docs/guides/open_source_deployment.md)
- [docs/index.md](docs/index.md)
- [docs/installation.md](docs/installation.md)
- [docs/quickstart.md](docs/quickstart.md)
- [mkdocs.yml](mkdocs.yml)

</details>



This guide provides comprehensive instructions for developers extending Paper2Any with custom workflows, agents, and state models. It covers the creation of new document processing pipelines, AI agents, and integration with the DataFlow-Agent framework using the CLI scaffolding system.

**Scope**: This page focuses on the **development workflow** and **code generation patterns**. For architectural concepts, see [Architecture Overview](#1.2). For operational deployment, see [Deployment](#12). For workflow composition patterns, see [DataFlow-Agent Framework](#5).

**Key Development Areas**:
- **Custom Workflows**: Create new document processing pipelines (e.g., extending Paper2PPT, PDF2PPT) [dataflow_agent/templates/workflow.py.jinja:1-10]()
- **Custom Agents**: Implement specialized AI agents for specific tasks (e.g., layout analysis, content extraction) [dataflow_agent/templates/agent.py.jinja:1-10]()
- **Custom State Models**: Define domain-specific state objects for workflow data flow [dataflow_agent/cli.py:146-156]()
- **Tool Integration**: Add pre-tools (context injection) and post-tools (agent-callable functions) [dataflow_agent/templates/workflow.py.jinja:51-75]()

---

## Development Workflow Overview

The DataFlow-Agent framework provides a CLI-driven development workflow that generates scaffolding code from Jinja templates. The typical development cycle follows this pattern:

```mermaid
graph TB
    "Start"["Developer identifies<br/>extension need"]
    
    subgraph "Code_Generation_Phase"
        "CLI"["dfa create command"]
        "Template"["Jinja Template<br/>(templates/*.jinja)"]
        "Scaffold"["Generated Scaffolding"]
    end
    
    subgraph "Implementation_Phase"
        "Customize"["Customize Generated Code"]
        "Register"["Auto-registration<br/>(@register decorator)"]
        "Implement"["Implement Business Logic"]
    end
    
    subgraph "Integration_Phase"
        "Test"["Run Tests"]
        "Execute"["Execute via CLI/Gradio"]
        "Debug"["Debug & Iterate"]
    end
    
    "Start" --> "CLI"
    "CLI" --> "Template"
    "Template" --> "Scaffold"
    "Scaffold" --> "Customize"
    "Customize" --> "Register"
    "Register" --> "Implement"
    "Implement" --> "Test"
    "Test" --> "Execute"
    "Execute" --> "Debug"
    "Debug" -->|Issues Found| "Customize"
    "Debug" -->|Success| "End"["Deployed Component"]
```

**Key Principles**:
1. **Template-driven scaffolding**: All components are generated from Jinja templates [dataflow_agent/cli.py:8-19]()
2. **Auto-registration**: Decorators automatically register components in global registries [dataflow_agent/templates/workflow.py.jinja:43]()
3. **Minimal manual wiring**: Framework handles most integration automatically [dataflow_agent/templates/workflow.py.jinja:18-31]()
4. **Iterative refinement**: Generated code is a starting point for customization [dataflow_agent/templates/agent.py.jinja:7-10]()

**Sources**: [dataflow_agent/cli.py:1-187](), [dataflow_agent/templates/workflow.py.jinja:1-203](), [dataflow_agent/templates/agent.py.jinja:1-165]()

---

## CLI Code Generation Tool

### Command Syntax

The `dfa create` command (defined in `dataflow_agent/cli.py`) generates scaffolding code for various component types [dataflow_agent/cli.py:27-39]():

| Component Type | Command | Output Location |
|---------------|---------|-----------------|
| **Workflow** | `dfa create --wf_name <name>` | `dataflow_agent/workflow/wf_<name>.py` [dataflow_agent/cli.py:62]() |
| **Agent** | `dfa create --agent_name <name>` | `dataflow_agent/agentroles/common_agents/<name>_agent.py` [dataflow_agent/cli.py:88]() |
| **State** | `dfa create --state_name <name>` | `dataflow_agent/states/<name>_state.py` [dataflow_agent/cli.py:148]() |
| **Prompt Template** | `dfa create --prompt_name <name>` | `dataflow_agent/promptstemplates/resources/pt_<name>_repo.py` [dataflow_agent/cli.py:118]() |

### Template Resolution

```mermaid
graph LR
    "Command"["dfa create<br/>--wf_name my_workflow"]
    
    subgraph "Template_Lookup"
        "TemplateDir"["dataflow_agent/templates/"]
        "WfTemplate"["workflow.py.jinja"]
        "TestTemplate"["test_workflow.py.jinja"]
    end
    
    subgraph "Variable_Injection"
        "Context"["Template Context:<br/>- wf_name<br/>- timestamp<br/>- entry_point"]
        "Render"["Jinja2 Rendering"]
    end
    
    subgraph "File_Generation"
        "WfFile"["wf_my_workflow.py"]
        "TestFile"["test_my_workflow.py"]
    end
    
    "Command" --> "TemplateDir"
    "TemplateDir" --> "WfTemplate"
    "TemplateDir" --> "TestTemplate"
    "WfTemplate" --> "Context"
    "TestTemplate" --> "Context"
    "Context" --> "Render"
    "Render" --> "WfFile"
    "Render" --> "TestFile"
```

**Sources**: [dataflow_agent/cli.py:58-82](), [dataflow_agent/cli.py:160-183]()

---

## Creating Custom Workflows

### Workflow Structure

A workflow is a Python function decorated with `@register` that returns a `GenericGraphBuilder` [dataflow_agent/templates/workflow.py.jinja:43-44]().

```mermaid
graph TB
    subgraph "Workflow_File_Structure"
        "Imports"["Imports Section"]
        "Register"["@register decorator"]
        "Factory"["Factory Function<br/>create_xxx_graph()"]
        
        subgraph "Builder_Configuration"
            "StateModel"["GenericGraphBuilder(<br/>state_model=xxState,<br/>entry_point='step1')"]
        end
        
        subgraph "Tool_Definitions"
            "PreTools"["@builder.pre_tool()<br/>Context injection"]
            "PostTools"["@builder.post_tool()<br/>Agent-callable functions"]
        end
        
        subgraph "Node_Definitions"
            "AsyncNodes"["async def step1(state)<br/>async def step2(state)"]
        end
    end
    
    "Imports" --> "Register"
    "Register" --> "Factory"
    "Factory" --> "StateModel"
    "StateModel" --> "PreTools"
    "PreTools" --> "PostTools"
    "PostTools" --> "AsyncNodes"
```

### Implementation Steps

1.  **Generate Scaffolding**: Run `dfa create --wf_name <name>` [dataflow_agent/cli.py:58]().
2.  **Define State**: Use `xxState` or create a custom state inheriting from `MainState` [dataflow_agent/templates/workflow.py.jinja:48]().
3.  **Define Tools**:
    *   **Pre-tools**: Inject strings/dicts into prompts [dataflow_agent/templates/workflow.py.jinja:55-57]().
    *   **Post-tools**: Define `@tool` functions for the agent to call [dataflow_agent/templates/workflow.py.jinja:60-75]().
4.  **Implement Nodes**: Use `create_simple_agent`, `create_react_agent`, or `create_vlm_agent` to execute logic [dataflow_agent/templates/workflow.py.jinja:98-135]().

For details, see [Creating Custom Workflows](#11.1).

**Sources**: [dataflow_agent/templates/workflow.py.jinja:1-203](), [dataflow_agent/cli.py:58-82]()

---

## Creating Custom Agents

### Agent Definition

Agents are subclasses of `BaseAgent` registered via `@register` [dataflow_agent/templates/agent.py.jinja:27-28]().

| Property | Description |
|---|---|
| `role_name` | Unique identifier for the agent [dataflow_agent/templates/agent.py.jinja:38]() |
| `system_prompt_template_name` | ID for the system prompt in the repo [dataflow_agent/templates/agent.py.jinja:42]() |
| `task_prompt_template_name` | ID for the task prompt in the repo [dataflow_agent/templates/agent.py.jinja:47]() |

### Execution Modes

Developers can choose different execution strategies via `Config` objects [dataflow_agent/templates/workflow.py.jinja:89-94]():
- **SimpleConfig**: Single LLM call [dataflow_agent/templates/workflow.py.jinja:140-146]().
- **ReactConfig**: Loop with validation and retries [dataflow_agent/templates/workflow.py.jinja:149-156]().
- **VLMConfig**: For vision-language tasks [dataflow_agent/templates/workflow.py.jinja:168-175]().

For details, see [Creating Custom Agents](#11.2).

**Sources**: [dataflow_agent/templates/agent.py.jinja:1-165](), [dataflow_agent/templates/workflow.py.jinja:89-176]()

---

## Creating Custom State Models

State models define how data is structured as it moves through the graph. They typically inherit from `MainState` and use Python dataclasses [dataflow_agent/cli.py:148-156]().

```python
@dataclass
class CustomState(MainState):
    """Generated by dfa create --state_name custom"""
    new_field: str = ""
    results: Dict[str, Any] = field(default_factory=dict)
```

For details, see [Creating Custom State Models](#11.3).

**Sources**: [dataflow_agent/cli.py:146-157](), [dataflow_agent/templates/workflow.py.jinja:16-18]()

---

## Testing

Paper2Any provides a `test_workflow.py.jinja` template to automatically generate `pytest` files for new workflows [dataflow_agent/cli.py:75-81]().

**Generated Test Structure**:
- **`run_xxx_pipeline()`**: Helper to initialize state and run `run_workflow` [dataflow_agent/templates/test_workflow.py.jinja:25-48]().
- **`test_xxx_pipeline()`**: Async test case with assertions on `final_state` [dataflow_agent/templates/test_workflow.py.jinja:52-79]().

Run tests using:
```bash
pytest tests/test_your_workflow.py -v -s
```

For details, see [Testing](#11.5).

**Sources**: [dataflow_agent/templates/test_workflow.py.jinja:1-86](), [dataflow_agent/cli.py:72-82]()

---

