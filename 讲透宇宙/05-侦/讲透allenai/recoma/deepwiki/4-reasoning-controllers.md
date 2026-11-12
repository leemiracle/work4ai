<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/recoma · page 4 Reasoning Controllers · fetched 2026-10-26 -->

# Reasoning Controllers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/inference/drop/react.jsonnet](configs/inference/drop/react.jsonnet)
- [configs/prompts/gsm8k/l2m_qa.txt](configs/prompts/gsm8k/l2m_qa.txt)
- [configs/prompts/letter_cat/l2m_qa.txt](configs/prompts/letter_cat/l2m_qa.txt)
- [recoma/models/core/__init__.py](recoma/models/core/__init__.py)
- [recoma/models/core/base_react_controller.py](recoma/models/core/base_react_controller.py)
- [recoma/models/impl/__init__.py](recoma/models/impl/__init__.py)
- [recoma/models/impl/l2m_controller.py](recoma/models/impl/l2m_controller.py)
- [recoma/models/impl/react_controller.py](recoma/models/impl/react_controller.py)

</details>



Reasoning controllers are specialized models that implement structured reasoning patterns within the ReComA framework. They coordinate multiple language model calls through systematic approaches like thought-action-observation loops, problem decomposition, and question-answer synthesis. Unlike simple language model generators, reasoning controllers maintain state across multiple inference steps and orchestrate complex multi-step reasoning workflows.

For information about the base model system and registration, see [Model System Architecture](#2.3). For details on language model generators, see [Language Model Integrations](#3).

## Controller Architecture

Reasoning controllers in ReComA extend the `BaseModel` class and implement specialized logic for multi-step reasoning patterns. They integrate with the search system to create branching reasoning paths and maintain conversation state across multiple model invocations.

```mermaid
graph TD
    subgraph "Base Classes"
        BaseModel["BaseModel<br/>@register pattern"]
        BaseReactController["BaseReactController<br/>ABC with step types"]
    end
    
    subgraph "Concrete Controllers"
        SimpleReactController["SimpleReactController<br/>@register('simple_react')"]
        LeastToMostController["LeastToMostController<br/>@register('l2m_control')"]
        DecompController["DecompController<br/>@register('decomp_control')"]
    end
    
    subgraph "Step Types"
        THOUGHT["THOUGHT = 0"]
        ACTION["ACTION = 1"] 
        OBSERVATION["OBSERVATION = 2"]
        STEP_TYPES["STEP_TYPES = 3"]
    end
    
    subgraph "State Management"
        SearchState["SearchState<br/>Tree container"]
        SearchNode["SearchNode<br/>Individual steps"]
        History["history: List[Any]<br/>Conversation state"]
    end
    
    BaseModel --> BaseReactController
    BaseModel --> LeastToMostController
    BaseModel --> DecompController
    BaseReactController --> SimpleReactController
    
    BaseReactController --> THOUGHT
    BaseReactController --> ACTION
    BaseReactController --> OBSERVATION
    BaseReactController --> STEP_TYPES
    
    SimpleReactController --> SearchState
    LeastToMostController --> SearchState
    DecompController --> SearchState
    
    SearchState --> SearchNode
    SearchNode --> History
```

**Controller Types Overview**

| Controller | Registration Key | Primary Pattern | Use Case |
|------------|------------------|-----------------|----------|
| `SimpleReactController` | `simple_react` | Thought-Action-Observation | Interactive reasoning with tool usage |
| `LeastToMostController` | `l2m_control` | Problem decomposition | Breaking complex questions into sub-questions |
| `DecompController` | `decomp_control` | Question decomposition | General Q&A orchestration |

Sources: [recoma/models/core/base_react_controller.py:8-12](), [recoma/models/impl/react_controller.py:19-20](), [recoma/models/impl/l2m_controller.py:7-8](), [recoma/models/impl/__init__.py:1-6]()

## React Controller Pattern

The React (Reasoning-Action) pattern implements a structured dialogue between thinking, acting, and observing. The `SimpleReactController` maintains conversation history and alternates between generating thoughts, actions, and observations.

```mermaid
sequenceDiagram
    participant SearchAlgo as "SearchAlgo"
    participant ReactController as "SimpleReactController"
    participant ActionModel as "action_model"
    participant ObservationModel as "observation_model"
    participant State as "SearchState"
    
    SearchAlgo->>ReactController: __call__(state)
    ReactController->>State: get_open_node()
    ReactController->>State: get_children()
    
    alt No children (start)
        ReactController->>ReactController: next_step_and_action_input()
        ReactController->>ActionModel: generate(thought_prompt)
        ActionModel-->>ReactController: thought_output
        ReactController->>State: add_next_step(THOUGHT)
    else Last step was THOUGHT
        ReactController->>ReactController: next_step_and_action_input()
        ReactController->>ActionModel: generate(action_prompt)
        ActionModel-->>ReactController: action_output
        ReactController->>State: add_next_step(ACTION)
    else Last step was ACTION
        ReactController->>ReactController: next_step_and_observation_input()
        ReactController->>ObservationModel: generate(observation_prompt)
        ObservationModel-->>ReactController: observation_output
        ReactController->>State: add_next_step(OBSERVATION)
    end
    
    ReactController->>ReactController: terminate_with_output()
    alt Termination condition met
        ReactController->>State: close(answer)
    else Continue reasoning
        ReactController-->>SearchAlgo: [new_state]
    end
```

The controller uses configurable prefixes and regex patterns to structure the conversation:

- `thought_prefix`: Prefix for thought statements (default: "Thought:")
- `action_prefix`: Prefix for action statements (default: "Action:")
- `obs_prefix`: Prefix for observation statements (default: "Observation:")
- `eoq_re`: Regex pattern for termination (default: "Finish\\[(.*)\\]")

Sources: [recoma/models/impl/react_controller.py:25-31](), [recoma/models/core/base_react_controller.py:111-135](), [recoma/models/impl/react_controller.py:33-57]()

## Least-to-Most Controller Pattern

The `LeastToMostController` implements problem decomposition by breaking complex questions into simpler sequential sub-questions. It operates in two phases: decomposition and question-answering.

```mermaid
graph TD
    subgraph "Phase 1: Decomposition"
        Input["Complex Question"]
        DecompModel["l2m_decomp_model"]
        ParseDecomp["parse_decomposition()"]
        Questions["List of sub-questions"]
    end
    
    subgraph "Phase 2: Sequential Q&A"
        Q1["Sub-question 1"]
        QAModel1["l2m_qa_model"]
        A1["Answer 1"]
        Q2["Sub-question 2<br/>+ Previous context"]
        QAModel2["l2m_qa_model"]
        A2["Answer 2"]
        QN["Sub-question N<br/>+ All previous context"]
        QAModelN["l2m_qa_model"]
        FinalAnswer["Final Answer"]
    end
    
    subgraph "Regex Patterns"
        StepRegex["step_regex<br/>To answer (.*)we need to know: (.*)"]
        QuesRegex["ques_regex<br/>Extract quoted questions"]
    end
    
    Input --> DecompModel
    DecompModel --> ParseDecomp
    ParseDecomp --> StepRegex
    ParseDecomp --> QuesRegex
    ParseDecomp --> Questions
    
    Questions --> Q1
    Q1 --> QAModel1
    QAModel1 --> A1
    A1 --> Q2
    Q2 --> QAModel2
    QAModel2 --> A2
    A2 --> QN
    QN --> QAModelN
    QAModelN --> FinalAnswer
```

The controller maintains the decomposition state in the node data and builds contextual prompts for each sub-question by accumulating previous question-answer pairs.

**Key Implementation Details:**

- **Decomposition Parsing**: Uses `step_regex` to extract the main question and sub-questions from the decomposition model output
- **Context Building**: Accumulates previous Q&A pairs to provide context for subsequent questions
- **State Management**: Stores parsed questions in `current_node.data["questions"]` for persistence across calls

Sources: [recoma/models/impl/l2m_controller.py:20-32](), [recoma/models/impl/l2m_controller.py:34-77](), [recoma/models/impl/l2m_controller.py:10-18]()

## Integration with Search System

Reasoning controllers integrate seamlessly with the search system by implementing the `BaseModel.__call__` interface. They receive a `SearchState`, manipulate it to add new reasoning steps, and return updated states for the search algorithm to process.

```mermaid
graph LR
    subgraph "Search Algorithm"
        SearchAlgo["BestFirstSearch"]
        OpenNode["get_open_node()"]
        Execute["execute()"]
    end
    
    subgraph "Controller Interface"
        Controller["ReasoningController"]
        Call["__call__(state)"]
        Clone["state.clone(deep=True)"]
        AddStep["add_next_step()"]
    end
    
    subgraph "State Manipulation"
        CurrentNode["current_node"]
        Children["get_children()"]
        NodeData["node.data"]
        History["conversation history"]
    end
    
    subgraph "Model Delegation"
        TargetModel["target_model"]
        NextStepModel["next_step_model"]
        ModelList["model_list"]
    end
    
    SearchAlgo --> OpenNode
    OpenNode --> Execute
    Execute --> Controller
    Controller --> Call
    Call --> Clone
    Clone --> CurrentNode
    CurrentNode --> Children
    Children --> NodeData
    NodeData --> History
    
    Controller --> AddStep
    AddStep --> TargetModel
    TargetModel --> NextStepModel
    NextStepModel --> ModelList
    
    Controller --> SearchAlgo
```

**State Management Operations:**

- `state.get_open_node()`: Retrieves the current node being processed
- `state.get_children()`: Gets child nodes for history reconstruction
- `state.add_next_step()`: Creates new reasoning steps with specified models
- `node.data`: Persistent storage for controller-specific state (history, questions, etc.)
- `node.close()`: Marks a node as complete with final output

Sources: [recoma/models/core/base_react_controller.py:60-78](), [recoma/models/impl/l2m_controller.py:34-77](), [recoma/search/state.py]()

## Configuration and Usage

Reasoning controllers are configured through JSONNET files that specify the controller type, associated models, and parameters. They integrate with the search system's model registry and can be chained with other models.

**React Controller Configuration Example:**

```json
{
  "models": {
    "drop_react": {
      "type": "simple_react",
      "action_model": "react_lm",
      "observation_model": "qa"
    },
    "react_lm": {
      "type": "prompted_lm",
      "prompt_file": "configs/prompts/drop/react.txt"
    }
  },
  "search": {
    "type": "best_first",
    "start_model": "drop_react"
  }
}
```

**Least-to-Most Controller Configuration:**

The L2M controller requires two specialized models for decomposition and question-answering phases, typically configured with task-specific prompts that demonstrate the expected input/output format.

Sources: [configs/inference/drop/react.jsonnet:1-38](), [configs/prompts/gsm8k/l2m_qa.txt:1-24](), [configs/prompts/letter_cat/l2m_qa.txt:1-19]()

---

