<!-- source: DeepWiki mcp.deepwiki.com · repo InternLM/lagent · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/en/changelog.md](docs/en/changelog.md)
- [lagent/version.py](lagent/version.py)
- [requirements/runtime.txt](requirements/runtime.txt)

</details>



LAgent is a lightweight open-source framework for building Large Language Model (LLM) powered agents. It provides a modular and extensible architecture that enables developers to create agents capable of reasoning, executing actions, and interacting with various tools. The framework emphasizes Pythonic design patterns inspired by PyTorch, making it intuitive to create and compose agent components.

For information about installing the framework and its dependencies, see [Installation and Setup](#1.1).

## Architecture Overview

LAgent is organized into four primary systems that work together to create functional LLM-powered agents:

```mermaid
graph TD
    User["User/Application"] --> Agent["Agent System"]

    subgraph "Core Components"
        Agent["Agent System\n(Agent, ReAct, AsyncAgent)"] -->|uses| LLM["LLM System\n(BaseLLM implementations)"]
        Agent -->|executes actions via| ActionSystem["Action System\n(ActionExecutor)"]
        Agent -->|utilizes| Support["Support Systems"]
    end

    subgraph "Support Systems"
        Memory["Memory\n(conversation history)"]
        Hooks["Hooks\n(message processors)"]
        Parser["Output Parser\n(ToolParser)"]
        Aggregator["Aggregator\n(DefaultAggregator)"]
    end

    Agent -->|stores context in| Memory
    Agent -->|registers| Hooks
    Agent -->|interprets responses with| Parser
    Agent -->|formats messages via| Aggregator
```

Sources: [README.md:32-78]()

The framework's modular design enables flexible component substitution and extension while maintaining consistent interfaces across the system.

## Communication Model

All components in LAgent communicate using a standardized message format called `AgentMessage`, which serves as the common data structure throughout the system:

```mermaid
classDiagram
    class AgentMessage {
        +content: Union[str, dict]
        +sender: str
        +formatted: Optional[dict]
        +extra_info: Optional[dict]
        +type: Optional[str]
        +receiver: Optional[str]
        +stream_state: AgentStatusCode
    }
    
    class Agent {
        +llm: BaseLLM
        +memory: Memory
        +aggregator: Aggregator
        +output_format: StrParser
        +__call__(message: AgentMessage): AgentMessage
        +forward(message: AgentMessage, session_id: int): AgentMessage
    }
    
    class ActionExecutor {
        +actions: List[BaseAction]
        +hooks: List[Hook]
        +__call__(message: AgentMessage, session_id: int): AgentMessage
    }
    
    Agent ..> AgentMessage: processes
    AgentMessage ..> ActionExecutor: passed to
    ActionExecutor ..> AgentMessage: returns
```

Sources: [README.md:37-58](), [README.md:225-276]()

## Agent System

The Agent System provides the core functionality for creating LLM-powered agents with different capabilities:

```mermaid
classDiagram
    class Agent {
        +llm: BaseLLM
        +memory: Memory
        +aggregator: Aggregator
        +output_format: StrParser
        +__call__(message): AgentMessage
        +forward(message, session_id): AgentMessage
        +reset(): None
    }
    
    class ReAct {
        +actions: ActionExecutor
        +max_turn: int
        +finish_condition: Callable
    }
    
    class StreamingAgent {
        +__call__(message): generator
        +forward(message): generator
    }
    
    class AsyncAgent {
        +async __call__(message)
        +async forward(message)
    }
    
    class Sequential {
        +_agents: OrderedDict
        +forward(message)
    }
    
    class MathCoder {
        +interpreter: ActionExecutor
    }
    
    Agent <|-- ReAct
    Agent <|-- StreamingAgent
    Agent <|-- AsyncAgent
    Agent <|-- Sequential
    ReAct <|-- MathCoder
```

Sources: [README.md:300-337]()

### Key Agent Types

- **Agent**: Base implementation for LLM-powered agents
- **ReAct**: Implements the Reasoning+Acting paradigm for tool use through iterative cycles
- **StreamingAgent**: Provides incremental/streaming responses
- **AsyncAgent**: Asynchronous implementation for concurrent processing
- **Sequential**: Chains multiple agents together for complex workflows

The `__call__` method of an agent handles the core execution flow:

```python
def __call__(self, *message):
    message = pre_hooks(message)
    add_memory(message)
    message = self.forward(*message)
    add_memory(message)
    message = post_hooks(message)
    return message
```

Sources: [README.md:71-77]()

## LLM Integration System

The LLM Integration System provides a unified abstraction layer for different LLM providers:

```mermaid
graph TD
    subgraph "LLM Interface Hierarchy"
        BaseLLM["BaseLLM\n(base interface)"] --> BaseAPILLM["BaseAPILLM\n(API clients)"]
        BaseLLM --> LocalModels["Local Model Interfaces"]
        
        AsyncLLMMixin["AsyncLLMMixin"] --> AsyncBaseAPILLM["AsyncBaseAPILLM"]
    end

    subgraph "API-Based Implementations"
        BaseAPILLM --> GPTAPI["GPTAPI\n(OpenAI)"]
        BaseAPILLM --> ClaudeAPI["ClaudeAPI\n(Anthropic)"]
        BaseAPILLM --> SensenovaAPI["SensenovaAPI"]
        
        AsyncBaseAPILLM --> AsyncGPTAPI["AsyncGPTAPI"]
        AsyncBaseAPILLM --> AsyncClaudeAPI["AsyncClaudeAPI"]
    end

    subgraph "Model-Based Implementations"
        LocalModels --> HFTransformer["HFTransformer"]
        LocalModels --> VllmModel["VllmModel"]
        LocalModels --> LMDeployClient["LMDeployClient"]
        
        AsyncLLMMixin --> AsyncVllmModel["AsyncVllmModel"]
        AsyncLLMMixin --> AsyncLMDeployClient["AsyncLMDeployClient"]
    end
```

Sources: [README.md:38-58](), [README.md:282-290]()

All LLM implementations provide consistent interfaces for:
- `generate()`: Text completion generation
- `chat()`: Chat completion generation
- `stream_generate()` and `stream_chat()`: Streaming variants

The framework offers both API-based LLMs (OpenAI, Claude) and local model integrations (HuggingFace, vLLM, LMDeploy).

## Action System

The Action System enables agents to interact with external tools and services:

```mermaid
classDiagram
    class BaseAction {
        +name: str
        +description: dict
        +__call__(inputs, name): ActionReturn
        +run(params): result
    }
    
    class ActionExecutor {
        +actions: List[BaseAction]
        +hooks: List[Hook]
        +__call__(message, session_id): AgentMessage
    }
    
    class WebBrowser {
        +search(query): dict
        +select(select_ids): dict
        +open_url(url): dict
    }
    
    class IPythonInterpreter {
        +run(command, timeout): ActionReturn
        +reset()
    }
    
    class GoogleScholar {
        +search_google_scholar(query): dict
        +get_author_information(author_id): dict
        +get_citation_format(q): dict
    }
    
    BaseAction <|-- WebBrowser
    BaseAction <|-- IPythonInterpreter
    BaseAction <|-- GoogleScholar
    BaseAction <|-- PythonInterpreter
    BaseAction <|-- ArxivSearch
    BaseAction <|-- PPT
    
    ActionExecutor --> "0..*" BaseAction: contains
```

Sources: [README.md:225-276]()

### Built-in Actions

The framework includes several built-in tools:

| Action | Description |
|--------|-------------|
| `WebBrowser` | Web search and navigation |
| `IPythonInterpreter` | Interactive Python code execution |
| `PythonInterpreter` | Python code execution |
| `GoogleScholar` | Academic search and citation lookup |
| `ArxivSearch` | Search arXiv papers |
| `PPT` | Presentation creation |

Actions are executed via the `ActionExecutor`, which manages action instances and applies hooks for message processing.

## Support Systems

Several support systems enhance agent capabilities and workflow:

### Memory Management

The Memory component maintains conversation history, allowing agents to retain context across multiple turns:

```python
# Access memory
memory = agent.memory.get_memory()

# Clear memory
agent.reset()

# Get serializable memory state
dumped_memory = agent.state_dict()
```

Sources: [README.md:66-88]()

### Hooks System

Hooks intercept and modify behavior at various points in the agent execution flow:

```mermaid
sequenceDiagram
    participant Agent
    participant Hooks as Hook System
    participant ActionExecutor
    
    Agent->>Hooks: before_agent(message)
    Hooks->>Agent: modified message
    Agent->>Agent: process message
    
    Agent->>Hooks: before_action(message)
    Hooks->>ActionExecutor: modified message
    ActionExecutor->>Hooks: after_action(result)
    Hooks->>Agent: modified result
```

Sources: [README.md:235-259]()

Custom hooks can be implemented by extending the `Hook` class and overriding methods like `before_action` and `after_action`.

### Output Parsers

Output Parsers extract structured information from LLM responses. The `ToolParser` is particularly important as it extracts tool calls from LLM output:

```python
parser = ToolParser(tool_type='code interpreter', begin='```python\n', end='\n```\n')
agent = Agent(llm, system_prompt, output_format=parser)
```

Sources: [README.md:191-223]()

### Aggregators

Aggregators format context from memory for LLM consumption. The `DefaultAggregator` converts `AgentMessage` objects to the format expected by LLMs:

```python
class FewshotAggregator(DefaultAggregator):
    def __init__(self, few_shot: List[dict] = None):
        self.few_shot = few_shot or []
    
    def aggregate(self, messages, name, parser=None, system_instruction=None):
        # Custom implementation with few-shot examples
        # ...
```

Sources: [README.md:102-165]()

## Usage Patterns

The typical usage pattern in LAgent involves:

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant LLM
    participant ActionExecutor
    participant Action
    
    User->>Agent: message (query or instruction)
    Agent->>Agent: update memory with message
    Agent->>Agent: aggregate context from memory
    Agent->>LLM: send formatted prompt
    LLM->>Agent: generate response with action plan
    
    loop Until completion or max turns
        Agent->>ActionExecutor: execute specified action
        ActionExecutor->>Action: call with parameters
        Action->>ActionExecutor: return action results
        ActionExecutor->>Agent: return action results
        Agent->>Agent: update memory with results
        Agent->>LLM: send updated context
        LLM->>Agent: generate next step
    end
    
    Agent->>User: final response
```

Sources: [README.md:300-350]()

### Single Agent Example

```python
from lagent.agents import Agent
from lagent.llms import VllmModel, INTERNLM2_META
from lagent.schema import AgentMessage

# Initialize LLM
llm = VllmModel(
    path='Qwen/Qwen2-7B-Instruct',
    meta_template=INTERNLM2_META,
    stop_words=['<|im_end|>'],
    max_new_tokens=1024,
)

# Create agent
agent = Agent(llm, "You are a helpful assistant.")

# Send message and get response
user_msg = AgentMessage(sender='user', content='Hello, what can you help me with?')
bot_msg = agent(user_msg)
```

Sources: [README.md:38-64]()

### Multi-Agent Systems

LAgent supports building multi-agent systems where agents collaborate to solve tasks:

```python
class Blogger(Agent):
    def __init__(self, model_path, writer_prompt, critic_prompt, max_turn=3):
        super().__init__()
        llm = GPTAPI(model_type=model_path)
        self.writer = Agent(llm, writer_prompt, name='writer')
        self.critic = Agent(llm, critic_prompt, name='critic')
        self.max_turn = max_turn

    def forward(self, message: AgentMessage, session_id=0) -> AgentMessage:
        for _ in range(self.max_turn):
            message = self.writer(message, session_id=session_id)
            message = self.critic(message, session_id=session_id)
        return self.writer(message, session_id=session_id)
```

Sources: [README.md:354-413]()

## Dual Interfaces

LAgent provides both synchronous and asynchronous interfaces for all major components:

| Synchronous | Asynchronous |
|-------------|--------------|
| `Agent` | `AsyncAgent` |
| `GPTAPI` | `AsyncGPTAPI` |
| `VllmModel` | `AsyncVllmModel` |
| `ActionExecutor` | `AsyncActionExecutor` |
| `WebBrowser` | `AsyncWebBrowser` |

Sources: [README.md:282-290]()

This dual interface design allows developers to choose the appropriate approach based on their application requirements - synchronous for debugging and asynchronous for production/concurrent processing.

## Dependencies and Requirements

LAgent has several key dependencies:

```
aiohttp           # For async HTTP requests
anthropic         # For Claude API integration  
arxiv             # For arXiv research tool
jupyter           # For IPython interpreter
pydantic          # For data validation
requests          # For HTTP requests
tiktoken          # For token counting
```

Sources: [requirements/runtime.txt:1-21]()

## License

LAgent is released under the Apache 2.0 license.

Sources: [README.md:527-530]()

---

