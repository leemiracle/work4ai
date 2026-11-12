<!-- source: DeepWiki mcp.deepwiki.com · repo saharmor/voice-lab · page 7 Core Architecture · fetched 2026-10-27 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/evaluator.py](core/evaluator.py)
- [core/providers/openai.py](core/providers/openai.py)
- [speech_testing/data_types.py](speech_testing/data_types.py)

</details>



This document covers the internal architecture of the Voice Lab testing framework, focusing on the foundational components, interfaces, and design patterns that enable multi-modal voice agent testing. This includes the core abstractions, provider implementations, and architectural patterns used across all testing systems.

For detailed information about specific data structures and models, see [Data Types & Models](#7.1). For in-depth coverage of LLM provider implementations, see [LLM Providers & Interfaces](#7.2).

## Architectural Overview

The Voice Lab framework follows a layered architecture with clear separation of concerns between interfaces, implementations, and domain-specific components. The core architecture provides abstractions that enable different testing modalities while maintaining consistency in evaluation and data handling.

### Core Architecture Layers

```mermaid
graph TB
    subgraph "Interface Layer"
        LLMInterface["LLMInterface"]
        ConversationEvaluator["ConversationEvaluator"]
    end
    
    subgraph "Implementation Layer"
        OpenAIProvider["OpenAIProvider"]
        LLMConversationEvaluator["LLMConversationEvaluator"]
    end
    
    subgraph "Data Layer"
        DataTypes["core.data_types"]
        SpeechDataTypes["speech_testing.data_types"]
        AgentConfig["AgentTaskConfig"]
        Personas["CalleePersona"]
    end
    
    subgraph "Testing Systems"
        LLMTesting["LLM Testing"]
        WebTesting["Web Testing"]
        SpeechTesting["Speech Testing"]
        LiveTesting["Live Testing"]
    end
    
    LLMInterface --> OpenAIProvider
    ConversationEvaluator --> LLMConversationEvaluator
    
    OpenAIProvider --> LLMTesting
    OpenAIProvider --> WebTesting
    LLMConversationEvaluator --> LLMTesting
    LLMConversationEvaluator --> WebTesting
    
    DataTypes --> OpenAIProvider
    DataTypes --> LLMConversationEvaluator
    SpeechDataTypes --> SpeechTesting
    AgentConfig --> LLMConversationEvaluator
    Personas --> LLMConversationEvaluator
    
    LLMTesting --> TestResults["Test Results & Reports"]
    WebTesting --> TestResults
    SpeechTesting --> TestResults
    LiveTesting --> TestResults
```

**Sources:** [core/evaluator.py:12-19](), [core/providers/openai.py:9-13](), [speech_testing/data_types.py:7-51]()

## Core Component Architecture

The framework is built around several key architectural components that provide the foundation for all testing modalities.

### Evaluation System Architecture

```mermaid
graph TD
    subgraph "ConversationEvaluator Hierarchy"
        AbstractEvaluator["ConversationEvaluator (ABC)"]
        LLMEvaluator["LLMConversationEvaluator"]
    end
    
    subgraph "Evaluation Dependencies"
        LLMInterface["LLMInterface"]
        EvalMetrics["eval_metrics.json"]
        SystemPrompt["eval_system_prompt"]
    end
    
    subgraph "Data Inputs"
        ConversationHistory["conversation_history: List[Dict]"]
        TaskConfig["AgentTaskConfig"]
        Persona["CalleePersona"]
        SuccessCriteria["success_criteria: str"]
        Guidelines["scenario_guidelines: str"]
    end
    
    subgraph "Evaluation Process"
        PromptCreation["_create_evaluation_prompt()"]
        SystemPromptGen["_get_evaluator_system_prompt()"]
        MetricsPrompt["_generate_metrics_prompt()"]
        LLMCall["generate_response_with_structured_output()"]
    end
    
    subgraph "Output"
        EvaluationResponse["EvaluationResponse"]
    end
    
    AbstractEvaluator --> LLMEvaluator
    LLMInterface --> LLMEvaluator
    EvalMetrics --> LLMEvaluator
    SystemPrompt --> LLMEvaluator
    
    ConversationHistory --> PromptCreation
    TaskConfig --> PromptCreation
    Persona --> PromptCreation
    SuccessCriteria --> PromptCreation
    Guidelines --> PromptCreation
    
    PromptCreation --> LLMCall
    SystemPromptGen --> LLMCall
    MetricsPrompt --> SystemPromptGen
    EvalMetrics --> MetricsPrompt
    
    LLMCall --> EvaluationResponse
```

**Sources:** [core/evaluator.py:12-39](), [core/evaluator.py:61-76](), [core/evaluator.py:41-59]()

### LLM Provider Interface Architecture

```mermaid
graph TD
    subgraph "LLMInterface Contract"
        PlainCall["plain_call()"]
        GenerateResponse["generate_response()"]
        StructuredOutput["generate_response_with_structured_output()"]
        ConversationHistory["generate_response_with_conversation_history()"]
        ImageAnalysis["analyze_image()"]
    end
    
    subgraph "OpenAIProvider Implementation"
        OpenAIClient["openai.OpenAI client"]
        ModelConfig["model: str (gpt-4o-mini)"]
        APIKey["api_key: str"]
    end
    
    subgraph "Response Processing"
        LLMResponse["LLMResponse(content, tool_calls)"]
        StructuredResponse["BaseModel.parsed"]
        ErrorHandling["Exception handling"]
    end
    
    subgraph "Input Processing"
        MessageFormatting["Message role mapping"]
        ConversationContext["ConversationContext"]
        EntitySpeaking["EntitySpeaking enum"]
        Base64Encoding["Base64 image encoding"]
    end
    
    PlainCall --> OpenAIClient
    GenerateResponse --> OpenAIClient
    StructuredOutput --> OpenAIClient
    ConversationHistory --> MessageFormatting
    ImageAnalysis --> Base64Encoding
    
    MessageFormatting --> OpenAIClient
    Base64Encoding --> OpenAIClient
    
    OpenAIClient --> LLMResponse
    OpenAIClient --> StructuredResponse
    OpenAIClient --> ErrorHandling
    
    ConversationContext --> MessageFormatting
    EntitySpeaking --> MessageFormatting
```

**Sources:** [core/providers/openai.py:9-85](), [core/providers/openai.py:15-30](), [core/providers/openai.py:32-42]()

## Data Architecture Patterns

The framework employs consistent data modeling patterns across different testing domains, with specialized extensions for each modality.

### Speech Testing Data Model

```mermaid
graph TD
    subgraph "Core Data Types"
        EntitySpeaking["EntitySpeaking (enum)"]
    end
    
    subgraph "Speech-Specific Data"
        CallSegment["CallSegment"]
        InterruptionData["InterruptionData"]
        PauseData["PauseData"]
        SpeechTestResult["SpeechTestResult"]
    end
    
    subgraph "CallSegment Fields"
        StartTime["start_time: float"]
        EndTime["end_time: float"]
        Speaker["speaker: EntitySpeaking"]
        Text["text: str"]
    end
    
    subgraph "InterruptionData Fields"
        InterruptedSpeaker["interrupted_speaker: EntitySpeaking"]
        InterruptedAt["interrupted_at: float"]
        Duration["interruption_duration: float"]
        InterruptionText["interruption_text: str"]
    end
    
    subgraph "Analysis Configuration"
        WhisperModelSize["WhisperModelSize (enum)"]
        SpeakerMapping["SPEAKER_MAPPING: Dict"]
    end
    
    EntitySpeaking --> CallSegment
    EntitySpeaking --> InterruptionData
    
    CallSegment --> SpeechTestResult
    InterruptionData --> SpeechTestResult
    PauseData --> SpeechTestResult
    
    StartTime --> CallSegment
    EndTime --> CallSegment
    Speaker --> CallSegment
    Text --> CallSegment
    
    InterruptedSpeaker --> InterruptionData
    InterruptedAt --> InterruptionData
    Duration --> InterruptionData
    InterruptionText --> InterruptionData
```

**Sources:** [speech_testing/data_types.py:7-51](), [speech_testing/data_types.py:32-51](), [speech_testing/data_types.py:15-27]()

## Cross-System Integration Patterns

The architecture supports multiple testing modalities through shared interfaces and consistent data flow patterns.

### Multi-Modal Integration Architecture

```mermaid
graph TB
    subgraph "Shared Core Components"
        CoreEvaluator["LLMConversationEvaluator"]
        CoreProvider["OpenAIProvider"]
        CoreDataTypes["core.data_types"]
    end
    
    subgraph "LLM Testing System"
        LLMTestRunner["llm_testing.test_runner"]
        LLMScenarios["test_scenarios.json"]
        LLMResults["LLM TestResult"]
    end
    
    subgraph "Web Testing System"
        WebEvaluator["web_eval.py"]
        WebScenarios["web_test_scenarios.json"]
        WebResults["Web TestResult"]
    end
    
    subgraph "Speech Testing System"
        SpeechTestRunner["speech_testing.run_tests"]
        SpeechDataTypes["speech_testing.data_types"]
        SpeechResults["SpeechTestResult"]
    end
    
    subgraph "Unified Output"
        ReportGenerator["generate_report.py"]
        HTMLReports["Interactive HTML Reports"]
    end
    
    CoreEvaluator --> LLMTestRunner
    CoreEvaluator --> WebEvaluator
    CoreProvider --> LLMTestRunner
    CoreProvider --> WebEvaluator
    
    LLMScenarios --> LLMTestRunner
    WebScenarios --> WebEvaluator
    SpeechDataTypes --> SpeechTestRunner
    
    LLMTestRunner --> LLMResults
    WebEvaluator --> WebResults
    SpeechTestRunner --> SpeechResults
    
    LLMResults --> ReportGenerator
    WebResults --> ReportGenerator
    SpeechResults --> ReportGenerator
    
    ReportGenerator --> HTMLReports
```

**Sources:** [core/evaluator.py:21-39](), [core/providers/openai.py:9-55](), [speech_testing/data_types.py:47-51]()

## Design Patterns and Principles

### Abstract Base Class Pattern

The framework uses abstract base classes to define contracts for key components, ensuring consistent interfaces across implementations.

| Interface | Implementation | Purpose |
|-----------|----------------|---------|
| `ConversationEvaluator` | `LLMConversationEvaluator` | Conversation evaluation abstraction |
| `LLMInterface` | `OpenAIProvider` | LLM service abstraction |

The `ConversationEvaluator` abstract base class [core/evaluator.py:12-19]() defines the evaluation contract with a single `evaluate()` method that all concrete evaluators must implement.

### Dependency Injection Pattern

Components accept their dependencies through constructor injection, enabling flexible configuration and testing:

```python
# LLMConversationEvaluator constructor signature
def __init__(self, evaluation_llm: LLMInterface, eval_metrics_path: str, eval_system_prompt: str)
```

**Sources:** [core/evaluator.py:23-26]()

### Configuration-Driven Architecture

The system uses external JSON configuration files to define behavior, keeping code generic and scenarios configurable:

- Evaluation metrics loaded from `eval_metrics.json` [core/evaluator.py:43-50]()
- Test scenarios defined in separate JSON files
- System prompts externalized for easy modification

**Sources:** [core/evaluator.py:41-59](), [core/evaluator.py:52-59]()

---

