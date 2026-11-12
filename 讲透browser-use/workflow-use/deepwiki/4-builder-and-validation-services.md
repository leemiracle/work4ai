<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/workflow-use · page 4 Builder and Validation Services · fetched 2026-10-30 -->

# AI-Powered Healing and Building

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [workflows/cli.py](workflows/cli.py)
- [workflows/examples/scripts/generate_workflow.py](workflows/examples/scripts/generate_workflow.py)
- [workflows/examples/workflows/basic/example.workflow.yaml](workflows/examples/workflows/basic/example.workflow.yaml)
- [workflows/examples/workflows/basic/pure_semantic.workflow.yaml](workflows/examples/workflows/basic/pure_semantic.workflow.yaml)
- [workflows/examples/workflows/form_filling/semantic_form_fill.workflow.yaml](workflows/examples/workflows/form_filling/semantic_form_fill.workflow.yaml)
- [workflows/tests/test_element_finder.py](workflows/tests/test_element_finder.py)
- [workflows/tests/test_go_back.workflow.yaml](workflows/tests/test_go_back.workflow.yaml)
- [workflows/tests/test_go_back_fix.py](workflows/tests/test_go_back_fix.py)
- [workflows/tests/test_selector_generator_fix.py](workflows/tests/test_selector_generator_fix.py)
- [workflows/tests/test_wait_times.py](workflows/tests/test_wait_times.py)
- [workflows/tests/test_workflow_execution.py](workflows/tests/test_workflow_execution.py)
- [workflows/workflow_use/healing/prompts/workflow_creation_prompt.md](workflows/workflow_use/healing/prompts/workflow_creation_prompt.md)
- [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md](workflows/workflow_use/healing/prompts/workflow_validation_prompt.md)
- [workflows/workflow_use/healing/tests/test_validator.py](workflows/workflow_use/healing/tests/test_validator.py)
- [workflows/workflow_use/recorder/semantic_converter.py](workflows/workflow_use/recorder/semantic_converter.py)
- [workflows/workflow_use/schema/views.py](workflows/workflow_use/schema/views.py)
- [workflows/workflow_use/workflow/service.py](workflows/workflow_use/workflow/service.py)

</details>



The AI-Powered Healing and Building system uses Large Language Models to transform raw workflow recordings and agent histories into optimized, maintainable workflow definitions. This system provides three key capabilities: workflow enhancement via `BuilderService`, quality assurance via `WorkflowValidator`, and semantic optimization for reliable element targeting. The AI layer intelligently analyzes recorded interactions, identifies reusable parameters, converts agent steps to deterministic actions, and validates workflows against best practices.

For information about workflow creation methods, see [Workflow Creation](#3). For execution details, see [Workflow Execution](#5). This page provides an overview of AI-powered enhancements; detailed documentation is available in [Builder Service](#4.1), [Workflow Validation](#4.2), and [Semantic Conversion](#4.3).

## AI Enhancement Architecture

The AI-powered enhancement system operates through three specialized services that work together to optimize workflow quality, reliability, and maintainability.

### AI Service Integration Pipeline

```mermaid
flowchart TB
    subgraph "Input"
        RAW_WF["Raw Workflow<br/>RecordingService output"]
        AGENT_HIST["AgentHistoryList<br/>HealingService output"]
    end
    
    subgraph "BuilderService"
        BUILDER["BuilderService<br/>build_workflow()"]
        BUILD_LLM["ChatBrowserUse<br/>LLM with structured output"]
        PROMPT_TPL["workflow_creation_prompt.md<br/>Vision + instructions"]
    end
    
    subgraph "WorkflowValidator"
        VALIDATOR["WorkflowValidator<br/>validate_workflow()"]
        VAL_LLM["ChatBrowserUse<br/>Issue detection"]
        VAL_PROMPT["workflow_validation_prompt.md<br/>Quality rules"]
    end
    
    subgraph "Semantic Enhancement"
        SEM_CONV["Semantic Converter<br/>target_text generation"]
        VAR_ID["VariableIdentifier<br/>parameterization"]
        SEL_GEN["SelectorGenerator<br/>fallback strategies"]
    end
    
    subgraph "Output"
        OPT_WF["Optimized WorkflowDefinitionSchema<br/>Enhanced + Validated"]
    end
    
    RAW_WF --> BUILDER
    AGENT_HIST --> BUILDER
    BUILDER --> BUILD_LLM
    BUILD_LLM --> PROMPT_TPL
    PROMPT_TPL --> VALIDATOR
    
    VALIDATOR --> VAL_LLM
    VAL_LLM --> VAL_PROMPT
    VAL_PROMPT --> SEM_CONV
    
    SEM_CONV --> VAR_ID
    VAR_ID --> SEL_GEN
    SEL_GEN --> OPT_WF
```

**Sources:** [workflows/workflow_use/builder/service.py:20-47](), [workflows/workflow_use/healing/validator.py:42-96](), [workflows/workflow_use/healing/prompts/workflow_creation_prompt.md:1-50]()

### LLM Integration Points

The system integrates LLMs at multiple stages for different optimization objectives:

| Component | LLM Model | Purpose | Output Format |
|-----------|-----------|---------|---------------|
| `BuilderService` | `ChatBrowserUse` | Transform recordings to workflows | `WorkflowDefinitionSchema` |
| `WorkflowValidator` | `ChatBrowserUse` | Detect and fix issues | `WorkflowValidationResult` |
| `HealingService` | `ChatBrowserUse` | Generate from agent history | `WorkflowDefinitionSchema` |
| `VariableIdentifier` | `ChatBrowserUse` | Extract parameters | `VariableExtractionResult` |

All LLM invocations use structured output via Pydantic models and function calling to ensure reliable parsing.

**Sources:** [workflows/workflow_use/builder/service.py:26-38](), [workflows/workflow_use/healing/validator.py:45-46](), [workflows/workflow_use/healing/service.py:19-26]()

## Workflow Enhancement with BuilderService

The `BuilderService` transforms raw workflow recordings into optimized workflow definitions using LLM-powered analysis. It processes both event data and screenshots to understand user intent and generate semantic, parameterized workflows.

### Enhancement Capabilities

The builder provides intelligent workflow optimization through multi-modal LLM analysis:

```mermaid
flowchart LR
    subgraph "Input Analysis"
        EVENTS["Workflow Events<br/>step data"]
        SCREENSHOTS["Screenshots<br/>base64 images"]
        USER_GOAL["user_goal<br/>task description"]
    end
    
    subgraph "BuilderService.build_workflow()"
        VISION_PREP["Vision message prep<br/>text + images"]
        ACTION_DOC["_get_available_actions_markdown()<br/>action registry"]
        LLM_INVOKE["llm.ainvoke()<br/>output_format=WorkflowDefinitionSchema"]
    end
    
    subgraph "Optimizations"
        PARAM["Parameter extraction<br/>{{variable}} syntax"]
        SEMANTIC["Semantic targeting<br/>target_text fields"]
        STEP_OPT["Step optimization<br/>agent → deterministic"]
    end
    
    EVENTS --> VISION_PREP
    SCREENSHOTS --> VISION_PREP
    USER_GOAL --> VISION_PREP
    VISION_PREP --> ACTION_DOC
    ACTION_DOC --> LLM_INVOKE
    LLM_INVOKE --> PARAM
    LLM_INVOKE --> SEMANTIC
    LLM_INVOKE --> STEP_OPT
```

**Key Enhancement Features:**
- **Screenshot Context**: Includes up to 20 screenshots for visual understanding [workflows/workflow_use/builder/service.py:189-220]()
- **Action Registry Integration**: Provides available actions from `WorkflowController` [workflows/workflow_use/builder/service.py:44-83]()
- **Structured Output**: Uses Pydantic schema for reliable parsing [workflows/workflow_use/builder/service.py:228-230]()
- **Variable Identification**: Extracts reusable parameters from recorded values

**Sources:** [workflows/workflow_use/builder/service.py:132-237](), [workflows/workflow_use/builder/prompts.py:1-6]()

For detailed documentation of the builder prompt engineering and workflow enhancement process, see [Builder Service](#4.1).

## Workflow Validation and Quality Assurance

The `WorkflowValidator` analyzes generated workflows to detect issues and automatically apply corrections. This AI-powered validation ensures workflows follow best practices and avoid common failure patterns.

### Validation Architecture

```mermaid
flowchart TB
    subgraph "Input"
        WF_TO_VAL["WorkflowDefinitionSchema<br/>to validate"]
        TASK_CTX["original_task<br/>context"]
        BROWSER_LOGS["browser_logs<br/>failure diagnostics"]
    end
    
    subgraph "WorkflowValidator"
        VAL_METHOD["validate_workflow()"]
        LOAD_PROMPT["workflow_validation_prompt.md<br/>issue patterns"]
        LLM_ANALYSIS["llm.ainvoke()<br/>output_format=WorkflowValidationResult"]
    end
    
    subgraph "WorkflowValidationResult"
        ISSUES["issues: List[WorkflowIssue]<br/>severity + suggestions"]
        CORRECTED["corrected_workflow<br/>fixed version"]
        SUMMARY["validation_summary<br/>report"]
    end
    
    subgraph "Issue Categories"
        CRITICAL["Critical<br/>agent_step, missing_selector"]
        WARNING["Warning<br/>generic_target_text"]
        SUGGESTION["Suggestion<br/>optimization"]
    end
    
    WF_TO_VAL --> VAL_METHOD
    TASK_CTX --> VAL_METHOD
    BROWSER_LOGS --> VAL_METHOD
    VAL_METHOD --> LOAD_PROMPT
    LOAD_PROMPT --> LLM_ANALYSIS
    LLM_ANALYSIS --> ISSUES
    LLM_ANALYSIS --> CORRECTED
    LLM_ANALYSIS --> SUMMARY
    
    ISSUES --> CRITICAL
    ISSUES --> WARNING
    ISSUES --> SUGGESTION
```

**Sources:** [workflows/workflow_use/healing/validator.py:42-96](), [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:1-50]()

### Common Issue Detection

The validator checks for critical workflow problems that cause execution failures:

| Issue Type | Severity | Detection Pattern | Auto-Fix |
|------------|----------|-------------------|----------|
| `agent_step` | Critical | Agent step replaceable by semantic | Convert to `click`/`input` |
| `missing_selector` | Critical | No `target_text`/`xpath`/`cssSelector` | Add semantic selector |
| `incorrect_step_type` | Critical | Wrong action type used | Replace with correct type |
| `missing_final_extract` | Critical | No extract step at end | Add `extract_page_content` |
| `hardcoded_value` | Warning | Value should be variable | Parameterize with `{{var}}` |
| `generic_target_text` | Warning | Text like "Click here" | Make more specific |

**Validation Rules Enforced:**
1. **All workflows must end with an extract step** [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:42-45]()
2. **Prefer semantic steps over agent steps** (10-30x faster) [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:16-19]()
3. **Target elements must have identification** (`target_text` or selector) [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:21-24]()
4. **Variables must be declared in input_schema** [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:32-34]()

**Sources:** [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:14-80](), [workflows/workflow_use/healing/validator.py:24-40]()

### Automatic Correction

The validator generates corrected workflows when issues are detected:

```python
# Usage from validator.py
result = await validator.validate_workflow(
    workflow=workflow,
    original_task="Fill government form",
    browser_logs=execution_logs  # Optional
)

if result.corrected_workflow:
    # Use the corrected version
    workflow = result.corrected_workflow
```

**Correction Process:**
1. Identify all issues with severity levels [workflows/workflow_use/healing/validator.py:48-61]()
2. Generate complete corrected workflow [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:87-111]()
3. Preserve workflow intent while fixing implementation [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:93-95]()
4. Return both issue list and corrected workflow [workflows/workflow_use/healing/validator.py:34-39]()

**Sources:** [workflows/workflow_use/healing/validator.py:98-118](), [workflows/workflow_use/healing/prompts/workflow_validation_prompt.md:87-111]()

For complete validation prompt engineering details, see [Workflow Validation and Quality Assurance](#4.2).

## Semantic Conversion and Optimization

The semantic conversion process transforms workflows to use text-based element targeting instead of brittle CSS selectors and XPath expressions. This optimization dramatically improves workflow maintainability and resilience to page changes.

### Semantic Targeting Strategy

```mermaid
flowchart TB
    subgraph "Input Step"
        OLD_STEP["Step with selectors<br/>cssSelector, xpath, elementTag"]
    end
    
    subgraph "SemanticConverter"
        EXTRACT_TEXT["Extract target_text<br/>from element properties"]
        GEN_STRAT["Generate selectorStrategies<br/>fallback chain"]
        OPTIMIZE["Optimize selector stability<br/>XPathOptimizer"]
    end
    
    subgraph "Target Text Sources"
        VIS_TEXT["Visible text<br/>elementText"]
        ARIA["ARIA labels<br/>aria-label"]
        PLACEHOLDER["Placeholders<br/>placeholder attr"]
        NAME["Name attribute<br/>input names"]
    end
    
    subgraph "Selector Strategies"
        STRATEGY_1["Priority 1: text_exact"]
        STRATEGY_2["Priority 2: role_text"]
        STRATEGY_3["Priority 3: aria_label"]
        STRATEGY_4["Priority 4: cssSelector"]
    end
    
    OLD_STEP --> EXTRACT_TEXT
    EXTRACT_TEXT --> VIS_TEXT
    EXTRACT_TEXT --> ARIA
    EXTRACT_TEXT --> PLACEHOLDER
    EXTRACT_TEXT --> NAME
    
    VIS_TEXT --> GEN_STRAT
    ARIA --> GEN_STRAT
    PLACEHOLDER --> GEN_STRAT
    NAME --> GEN_STRAT
    
    GEN_STRAT --> STRATEGY_1
    GEN_STRAT --> STRATEGY_2
    GEN_STRAT --> STRATEGY_3
    GEN_STRAT --> STRATEGY_4
    STRATEGY_4 --> OPTIMIZE
```

**Sources:** [workflows/workflow_use/controller/utils.py:12-49](), [workflows/examples/workflows/basic/pure_semantic.workflow.yaml:1-47]()

### Selector Stability Optimization

The `SelectorGenerator` and `XPathOptimizer` create stability-ranked selector strategies:

**Stability Ranking (Most → Least Stable):**

| Priority | Strategy Type | Example | Stability Rationale |
|----------|--------------|---------|---------------------|
| 1 | Attribute-based | `input[placeholder*="Email"]` | Semantic attributes rarely change |
| 2 | Text content | `button:has-text("Submit")` | User-facing text is stable |
| 3 | Role + text | `[role="button"]:has-text("Next")` | ARIA roles + visible text |
| 4 | Tag + classes | `button.submit-btn` | Structure-dependent but common |
| 5 | Full selector | Original CSS/XPath | Fallback for exact targeting |

**Selector Generation Process:**
1. Extract semantic information from element [workflows/workflow_use/controller/utils.py:51-102]()
2. Generate fallback selectors by stability [workflows/workflow_use/controller/utils.py:51-102]()
3. Remove dynamic parts (IDs, state classes) [workflows/workflow_use/controller/utils.py:89-96]()
4. Create text-based selectors when possible [workflows/workflow_use/controller/utils.py:98-100]()

**Sources:** [workflows/workflow_use/controller/utils.py:51-150](), [workflows/examples/workflows/form_filling/semantic_form_fill.workflow.yaml:1-47]()

### Variable Parameterization

The `VariableIdentifier` extracts reusable parameters from workflow values:

**Identification Criteria:**
- **User-specific data**: Names, emails, phone numbers, addresses
- **Search/filter terms**: Query strings, date ranges, categories  
- **Form inputs**: Any user-entered text, numbers, selections
- **Dynamic values**: Amounts, quantities, IDs, references

**Variable Syntax:**
- Template format: `{{variable_name}}` (single braces for Python `str.format()`)
- Input schema: JSON Schema draft-7 with `name`, `type`, `required` fields
- Format hints: Specify patterns like `"MM/DD/YYYY"` or `"user@domain.com"`

**Example Conversion:**
```yaml
# Before: Hard-coded value
- type: input
  target_text: "First Name"
  value: "John"

# After: Parameterized
- type: input
  target_text: "First Name"
  value: "{first_name}"

input_schema:
- name: first_name
  type: string
  required: true
```

**Sources:** [workflows/workflow_use/healing/prompts/workflow_creation_prompt.md:92-116](), [workflows/examples/workflows/basic/example.workflow.yaml:102-111]()

For detailed semantic conversion algorithms, see [Semantic Conversion and Optimization](#4.3).

## Data Transformation Pipeline

The workflow builder implements a comprehensive data transformation pipeline that converts raw browser events into executable workflow definitions through multiple processing stages.

### Event to Workflow Transformation

```mermaid
flowchart TD
    subgraph "Raw Data Layer"
        RAW_EVENTS["Browser Events<br/>RRWeb + Custom"]
        AGENT_HIST["Agent History<br/>AgentHistoryList"]
        SCREENSHOTS["Screenshots<br/>base64 images"]
    end
    
    subgraph "Processing Layer"
        EVENT_FILTER["Event filtering<br/>RecordingService"]
        SEMANTIC_ENHANCE["Semantic enhancement<br/>BuilderService"]
        HISTORY_PARSE["History parsing<br/>HealingService"]
    end
    
    subgraph "LLM Enhancement"
        PROMPT_GEN["Prompt generation<br/>workflow_creation_prompt.md"]
        STRUCT_OUTPUT["Structured output<br/>WorkflowDefinitionSchema"]
        VALIDATION["Schema validation<br/>Pydantic models"]
    end
    
    subgraph "Final Output"
        EXECUTABLE_WF["Executable Workflow<br/>JSON definition"]
        PARAM_INPUTS["Parameterized inputs<br/>{{variable}} syntax"]
        SEMANTIC_STEPS["Semantic steps<br/>elementHash references"]
    end
    
    RAW_EVENTS --> EVENT_FILTER
    AGENT_HIST --> HISTORY_PARSE
    SCREENSHOTS --> SEMANTIC_ENHANCE
    
    EVENT_FILTER --> SEMANTIC_ENHANCE
    HISTORY_PARSE --> PROMPT_GEN
    SEMANTIC_ENHANCE --> STRUCT_OUTPUT
    
    PROMPT_GEN --> STRUCT_OUTPUT
    STRUCT_OUTPUT --> VALIDATION
    VALIDATION --> EXECUTABLE_WF
    
    EXECUTABLE_WF --> PARAM_INPUTS
    EXECUTABLE_WF --> SEMANTIC_STEPS
```

**Sources:** [workflows/workflow_use/healing/prompts/workflow_creation_prompt.md:1-25](), [workflows/workflow_use/builder/service.py:187-232]()

### Workflow Schema Generation

The transformation process creates structured workflow definitions with these key components:

| Schema Field | Purpose | Generation Method |
|--------------|---------|------------------|
| `workflow_analysis` | Task understanding | LLM reasoning about recorded steps |
| `input_schema` | Parameter definitions | JSON Schema draft-7 format |
| `output_schema` | Return data structure | Based on extraction steps |
| `steps` | Action sequence | Deterministic + agentic step mix |

**Step Type Mapping:**
- **Deterministic Steps**: Direct browser actions (`click_element`, `input_text`, `go_to_url`)
- **Agentic Steps**: AI-powered tasks for dynamic content (`agent` type with `task` parameter)
- **Extraction Steps**: Data gathering (`extract_page_content` with `goal` parameter)

**Sources:** [workflows/workflow_use/healing/prompts/workflow_creation_prompt.md:39-122](), [workflows/workflow_use/schema/views.py]()

The Workflow Builder system provides a robust foundation for converting browser interactions into reusable automation workflows, supporting both direct recording enhancement and AI-powered generation from natural language tasks.

---

