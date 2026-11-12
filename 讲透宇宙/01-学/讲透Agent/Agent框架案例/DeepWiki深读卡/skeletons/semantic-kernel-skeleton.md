# Skeleton: semantic-kernel（30 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 14KB | 4 | ~6 | 33 |
| 2 | Architecture | L303 | 12KB | 3 | ~2 | 33 |
| 3 | .NET Implementation | L520 | 21KB | 3 | ~1 | 22 |
| 4 | Python Implementation | L835 | 20KB | 3 | ~2 | 25 |
| 5 | Package Management and Dependencies | L1151 | 17KB | 4 | ~4 | 22 |
| 6 | Core Components | L1396 | 15KB | 3 | ~4 | 18 |
| 7 | Kernel Orchestration | L1632 | 25KB | 10 | ~4 | 18 |
| 8 | Functions and Plugins | L2088 | 31KB | 5 | ~0 | 16 |
| 9 | Memory and Vector Stores | L2523 | 26KB | 4 | ~6 | 20 |
| 10 | AI Service Integration | L2864 | 23KB | 6 | ~2 | 16 |
| 11 | OpenAI and Azure OpenAI Connectors | L3255 | 24KB | 4 | ~0 | 19 |
| 12 | Service Selection and Configuration | L3589 | 22KB | 3 | ~0 | 14 |
| 13 | Other AI Service Connectors | L3820 | 41KB | 2 | ~2 | 18 |
| 14 | Agent Framework | L4168 | 14KB | 7 | ~0 | 24 |
| 15 | Agent Architecture and Base Classes | L4489 | 23KB | 4 | ~6 | 19 |
| 16 | .NET Agent Implementations | L4873 | 23KB | 2 | ~2 | 16 |
| 17 | Python Agent Implementations | L5147 | 19KB | 3 | ~1 | 18 |
| 18 | Multi-Agent Orchestration | L5393 | 14KB | 3 | ~3 | 25 |
| 19 | Advanced Features | L5607 | 13KB | 4 | ~0 | 18 |
| 20 | OpenAPI Integration | L5839 | 19KB | 4 | ~4 | 19 |
| 21 | Prompt Execution Settings and Tool Calling | L6111 | 20KB | 4 | ~4 | 15 |
| 22 | Filtering and Extensibility | L6362 | 20KB | 3 | ~2 | 18 |
| 23 | Python Code Execution Tools | L6648 | 13KB | 2 | ~5 | 20 |
| 24 | Process Framework | L6842 | 19KB | 2 | ~4 | 24 |
| 25 | Model Context Protocol (MCP) Integration | L7078 | 19KB | 2 | ~4 | 14 |
| 26 | Development Guide | L7304 | 8KB | 2 | ~0 | 33 |
| 27 | CI/CD and Build System | L7460 | 11KB | 3 | ~2 | 35 |
| 28 | Sample Applications and Getting Started | L7709 | 21KB | 4 | ~4 | 21 |
| 29 | Configuration and Setup | L8026 | 14KB | 2 | ~3 | 21 |
| 30 | Glossary | L8247 | 21KB | 2 | ~0 | 35 |


## · Overview  (L6)
  源文件: .github/_typos.toml, FEATURE_MATRIX.md, README.md, docs/decisions/0033-kernel-filters.md, docs/decisions/0034-rag-in-sk.md, docs/decisions/0071-multi-agent-orchestration.md, docs/images/sk_logo.png, dotnet/Directory.Packages.props, dotnet/README.md, dotnet/docs/EXPERIMENTS.md, dotnet/notebooks/05-using-function-calling.ipynb, dotnet/notebooks/README.md
  What is Semantic Kernel
  Multi-Language Implementation Architecture
  Core Concepts to Code Entity Mapping
  Key System Capabilities
    · Function and Plugin System
    · Agent Framework Architecture
    · AI Service Integration
  Development and Usage Patterns
    · Basic Kernel Setup Pattern
    · Memory and Vector Stores

## · Architecture  (L303)
  源文件: .github/_typos.toml, FEATURE_MATRIX.md, README.md, docs/decisions/0033-kernel-filters.md, docs/decisions/0034-rag-in-sk.md, docs/decisions/0071-multi-agent-orchestration.md, docs/images/sk_logo.png, dotnet/Directory.Packages.props, dotnet/README.md, dotnet/docs/EXPERIMENTS.md, dotnet/notebooks/05-using-function-calling.ipynb, dotnet/notebooks/README.md
  Purpose and Scope
  Overall Repository Architecture
  Framework Component Architecture
  Package and Dependency Architecture
  Cross-Language Agent Architecture
  Build and CI/CD Architecture

## · .NET Implementation  (L520)
  源文件: docs/decisions/0004-error-handling.md, docs/decisions/0006-open-api-dynamic-payload-and-namespaces.md, docs/decisions/0007-prompt-extract-template-engine.md, docs/decisions/0008-support-generic-llm-request-settings.md, docs/decisions/0009-support-multiple-named-args-in-template-function-calls.md, docs/decisions/0010-dotnet-project-structure.md, docs/decisions/0011-function-and-kernel-result-types.md, docs/decisions/0012-kernel-service-registration.md, docs/decisions/0013-memory-as-plugin.md, docs/decisions/0014-chat-completion-roles-in-prompt.md, docs/decisions/0015-completion-service-selection.md, docs/decisions/0016-custom-prompt-template-formats.md
  Core Architecture
    · Key Components and Relationships
    · Core Classes and Execution Model
  Function Types and Implementation
    · Method-Based Functions
    · Prompt-Based Functions
  Microsoft.Extensions.AI Interoperability
    · Service Bridging
    · Content Conversion
  Dependency Injection and Builder Pattern
  Telemetry and Instrumentation

## · Python Implementation  (L835)
  源文件: docs/decisions/0037-audio-naming.md, python/.env.example, python/pyproject.toml, python/samples/__init__.py, python/samples/concepts/README.md, python/samples/concepts/agents/azure_ai_agent/azure_ai_agent_azure_ai_search.py, python/samples/concepts/agents/azure_ai_agent/azure_ai_agent_file_manipulation.py, python/samples/concepts/agents/azure_ai_agent/azure_ai_agent_streaming.py, python/samples/concepts/mcp/README.md, python/samples/concepts/mcp/agent_with_mcp_plugin.py, python/samples/concepts/mcp/agent_with_mcp_sampling.py, python/samples/concepts/mcp/azure_ai_agent_with_mcp_plugin.py
  Core Architecture Overview
    · Python Kernel Architecture
  Kernel Orchestration
    · Kernel Class Structure
  Dependency Structure and Models
    · Dependency Configuration
  Functions and Plugins
    · Function Creation Patterns
  Agent Framework
    · Agent Class Hierarchy
    · Agent Execution Patterns
  AI Service Integration
    · Service Selection
  Filtering and Extensibility
    · Filter Types

## · Package Management and Dependencies  (L1151)
  源文件: .github/_typos.toml, docs/decisions/0071-multi-agent-orchestration.md, dotnet/Directory.Packages.props, dotnet/SK-dotnet.slnx, dotnet/docs/EXPERIMENTS.md, dotnet/nuget/nuget-package.props, dotnet/samples/AgentFrameworkMigration/AzureOpenAI/Step04_ToolCall_WithOpenAPI/AzureOpenAI_Step04_ToolCall_WithOpenAPI.csproj, dotnet/samples/AgentFrameworkMigration/AzureOpenAI/Step04_ToolCall_WithOpenAPI/OpenAPISpec.json, dotnet/samples/AgentFrameworkMigration/AzureOpenAI/Step04_ToolCall_WithOpenAPI/Program.cs, dotnet/samples/Concepts/Concepts.csproj, dotnet/samples/Concepts/FunctionCalling/FunctionCalling_SharedState.cs, dotnet/samples/Concepts/Memory/OpenAI_EmbeddingGeneration.cs
  Package Structure Overview
    · Package Hierarchy
  .NET Package Management
    · Central Package Management (CPM)
    · NuGet Versioning Strategy
  Python Package Management
    · Dependency Configuration
    · Optional Dependency Groups (Extras)
    · Reproducible Builds with uv
  Cross-Language Dependency Mapping

## · Core Components  (L1396)
  源文件: dotnet/src/Connectors/Connectors.OpenAI.UnitTests/Core/AutoFunctionInvocationFilterTests.cs, dotnet/src/InternalUtilities/planning/PlannerInstrumentation.cs, dotnet/src/SemanticKernel.Abstractions/AI/PromptNode.cs, dotnet/src/SemanticKernel.Abstractions/Events/CancelKernelEventArgs.cs, dotnet/src/SemanticKernel.Abstractions/Events/FunctionInvokedEventArgs.cs, dotnet/src/SemanticKernel.Abstractions/Events/FunctionInvokingEventArgs.cs, dotnet/src/SemanticKernel.Abstractions/Events/KernelEventArgs.cs, dotnet/src/SemanticKernel.Abstractions/Events/PromptRenderedEventArgs.cs, dotnet/src/SemanticKernel.Abstractions/Events/PromptRenderingEventArgs.cs, dotnet/src/SemanticKernel.Abstractions/Filters/AutoFunctionInvocation/AutoFunctionInvocationContext.cs, dotnet/src/SemanticKernel.Abstractions/Filters/AutoFunctionInvocation/IAutoFunctionInvocationFilter.cs, dotnet/src/SemanticKernel.Abstractions/Filters/Function/FunctionInvocationContext.cs
  Component Architecture Overview
  Kernel: Central Orchestration Engine
    · Core Responsibilities
    · Kernel Class Structure
  KernelFunction: Executable Function Abstraction
    · Function Hierarchy
    · Metadata System
  KernelPlugin: Function Collections
    · Plugin Management
  Data Flow and Results
    · Function Results
    · Content Abstractions
  Child Pages

## · Kernel Orchestration  (L1632)
  源文件: dotnet/src/Agents/Bedrock/Extensions/BedrockAgentInvokeExtensions.cs, dotnet/src/Agents/OpenAI/Internal/AssistantMessageFactory.cs, dotnet/src/Agents/OpenAI/Internal/ResponseThreadActions.cs, dotnet/src/Agents/UnitTests/OpenAI/Internal/AssistantMessageFactoryTests.cs, dotnet/src/Agents/UnitTests/OpenAI/Internal/ResponseThreadActionsTests.cs, dotnet/src/Connectors/Connectors.Google/Core/Gemini/Models/GeminiPart.cs, dotnet/src/Connectors/Connectors.OpenAI.UnitTests/Core/AutoFunctionInvocationFilterTests.cs, dotnet/src/InternalUtilities/connectors/AI/FunctionCalling/FunctionCallsProcessor.cs, dotnet/src/InternalUtilities/planning/Extensions/KernelFunctionMetadataExtensions.cs, dotnet/src/InternalUtilities/planning/PlannerInstrumentation.cs, dotnet/src/SemanticKernel.Abstractions/AI/PromptExecutionSettings.cs, dotnet/src/SemanticKernel.Abstractions/AI/PromptNode.cs
  Core Architecture Overview
    · High-Level Orchestration Architecture
  Kernel Class and Core Components
    · .NET Kernel Implementation
    · Python Kernel Implementation
  Function Orchestration Patterns
    · Function Invocation Flow
    · Streaming Orchestration
    · Auto Function Invocation Pattern
  Filter System and Execution Pipeline
    · Filter Types and Pipeline
    · Filter Execution Implementation
  Service Integration and Selection
    · Service Selection Flow
  Cross-Language Implementation Consistency
    · Implementation Comparison
    · Kernel Creation Patterns

## · Functions and Plugins  (L2088)
  源文件: docs/decisions/0037-audio-naming.md, dotnet/samples/Concepts/Functions/MethodFunctions_Advanced.cs, dotnet/samples/Concepts/Plugins/CreatePluginFromOpenApiSpec_RepairService.cs, dotnet/samples/Concepts/Plugins/OpenApiPlugin_Customization.cs, dotnet/samples/Concepts/Resources/Plugins/ProductsPlugin/openapi.json, dotnet/samples/Demos/OllamaFunctionCalling/Program.cs, dotnet/src/Extensions/Extensions.UnitTests/Extensions.UnitTests.csproj, dotnet/src/Extensions/Extensions.UnitTests/PromptTemplates/Handlebars/HandlebarsPromptTemplateFactoryTests.cs, dotnet/src/Extensions/Extensions.UnitTests/PromptTemplates/Handlebars/HandlebarsPromptTemplateTests.cs, dotnet/src/Extensions/Extensions.UnitTests/PromptTemplates/Handlebars/Helpers/KernelFunctionHelpersTests.cs, dotnet/src/Extensions/Extensions.UnitTests/PromptTemplates/Handlebars/Helpers/KernelHelperUtilsTests.cs, dotnet/src/Extensions/Extensions.UnitTests/PromptTemplates/Handlebars/Helpers/KernelSystemHelpersTests.cs
  Function Types and Creation
    · Function Creation Overview
    · Method-based Functions
    · Prompt-based Functions
  Template Rendering Engine
    · Block-based Tokenization
    · Variable Resolution
    · Function Calling in Templates
  OpenAPI Plugin System
    · OpenAPI Plugin Architecture
  Plugin Management and Organization
    · Plugin Management Architecture
  Function Execution and Results
    · Invocation Pipeline
    · Result Handling

## · Memory and Vector Stores  (L2523)
  源文件: .gitignore, docs/decisions/0072-agents-with-memory.md, dotnet/samples/Concepts/Agents/ChatCompletion_Mem0.cs, dotnet/samples/Concepts/Agents/ChatCompletion_Rag.cs, dotnet/samples/Concepts/Agents/ChatCompletion_Whiteboard.cs, dotnet/samples/Concepts/Memory/TextChunkerUsage.cs, dotnet/samples/Concepts/Memory/TextChunkingAndEmbedding.cs, dotnet/src/Agents/Bedrock/Agents.Bedrock.csproj, dotnet/src/Experimental/Orchestration.Flow.IntegrationTests/Experimental.Orchestration.Flow.IntegrationTests.csproj, dotnet/src/Experimental/Orchestration.Flow.UnitTests/Experimental.Orchestration.Flow.UnitTests.csproj, dotnet/src/Experimental/Process.Abstractions/KernelProcess.cs, dotnet/src/Experimental/Process.UnitTests/KernelProcessTests.cs
  Overview
    · .NET Memory Architecture
    · Python Memory Architecture
  Memory Abstractions and Data Flow
    · .NET Vector Store Model
    · Filter Translators
  Vector Store Connectors
    · SQL Server & Azure SQL
    · PostgreSQL (pgvector)
    · In-Memory Vector Store
  Retrieval-Augmented Generation (RAG) and TextSearch
    · TextSearchStore
    · TextChunker
  Implementation Details: SQL Generation
    · SQL Server Type Mapping
    · PostgreSQL Type Mapping

## · AI Service Integration  (L2864)
  源文件: dotnet/docs/OPENAI-CONNECTOR-MIGRATION.md, dotnet/samples/Concepts/ChatCompletion/OpenAI_ChatCompletionExtraBody.cs, dotnet/src/Connectors/Connectors.AzureOpenAI.UnitTests/Services/AzureOpenAIChatCompletionExtraBodyTests.cs, dotnet/src/Connectors/Connectors.AzureOpenAI.UnitTests/Services/AzureOpenAIChatCompletionServiceTests.cs, dotnet/src/Connectors/Connectors.AzureOpenAI.UnitTests/Settings/AzureOpenAIPromptExecutionSettingsTests.cs, dotnet/src/Connectors/Connectors.AzureOpenAI/Core/AzureClientCore.ChatCompletion.cs, dotnet/src/Connectors/Connectors.AzureOpenAI/Settings/AzureOpenAIPromptExecutionSettings.cs, dotnet/src/Connectors/Connectors.OpenAI.UnitTests/Core/ClientCoreTests.cs, dotnet/src/Connectors/Connectors.OpenAI.UnitTests/Services/OpenAIChatCompletionExtraBodyTests.cs, dotnet/src/Connectors/Connectors.OpenAI.UnitTests/Services/OpenAIChatCompletionServiceTests.cs, dotnet/src/Connectors/Connectors.OpenAI.UnitTests/Settings/OpenAIPromptExecutionSettingsTests.cs, dotnet/src/Connectors/Connectors.OpenAI/Core/ClientCore.ChatCompletion.cs
  AI Service Architecture Overview
    · Service Integration Architecture
  Service Selection and Configuration
    · OrderedAIServiceSelector
  Base Service Abstractions
    · Python Service Abstractions
    · Service Execution Flow
  Provider Implementations
    · OpenAI Service Implementations
    · Provider Implementation Hierarchy
    · HuggingFace Implementation
  Prompt Execution Settings
    · OpenAI Execution Settings
    · Settings Hierarchy and Conversion
  Function Calling Support
    · .NET ToolCallBehavior
    · Python FunctionChoiceBehavior  
    · Function Calling Flow
  Error Handling and Content Filtering
    · Content Filter Exception Handling
  Python Code Execution Tool

## · OpenAI and Azure OpenAI Connectors  (L3255)
  源文件: docs/decisions/0065-realtime-api-clients.md, dotnet/docs/OPENAI-CONNECTOR-MIGRATION.md, dotnet/samples/Concepts/ChatCompletion/AzureOpenAIWithData_ChatCompletion.cs, dotnet/samples/Concepts/ChatCompletion/AzureOpenAI_ChatCompletion.cs, dotnet/samples/Concepts/ChatCompletion/AzureOpenAI_ChatCompletionStreaming.cs, dotnet/samples/Concepts/ChatCompletion/AzureOpenAI_ChatCompletionWithReasoning.cs, dotnet/samples/Concepts/ChatCompletion/AzureOpenAI_CustomClient.cs, dotnet/samples/Concepts/ChatCompletion/ChatHistoryInFunctions.cs, dotnet/samples/Concepts/ChatCompletion/HuggingFace_ChatCompletion.cs, dotnet/samples/Concepts/ChatCompletion/HuggingFace_ChatCompletionStreaming.cs, dotnet/samples/Concepts/ChatCompletion/LMStudio_ChatCompletion.cs, dotnet/samples/Concepts/ChatCompletion/LMStudio_ChatCompletionStreaming.cs
  Purpose and Architecture
    · OpenAI and Azure OpenAI Connector Architecture
  Connector Implementation
    · .NET Connector Class Hierarchy
  .NET Implementation
    · ClientCore and AzureClientCore
    · Service Classes
  Python Implementation
    · OpenAIHandler and Client Bases
    · Python Connector Class Hierarchy
  Execution Settings
    · Key Settings and Features
  Chat Completion Flow
  Azure OpenAI with Data (On Your Data)
  Migration and Compatibility

## · Service Selection and Configuration  (L3589)
  源文件: dotnet/samples/Concepts/FunctionCalling/FunctionCalling.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/Core/Gemini/Clients/GeminiChatClientFunctionCallingTests.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/Core/Gemini/Clients/GeminiChatGenerationFunctionCallingTests.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/Core/Gemini/Clients/GeminiChatStreamingFunctionCallingTests.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/Core/Gemini/GeminiFunctionToolCallTests.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/Core/Gemini/GeminiMetadataTests.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/Core/Gemini/GeminiPartTests.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/GeminiToolCallBehaviorTests.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/TestData/chat_function_with_thought_signature_response.json, dotnet/src/Connectors/Connectors.Google.UnitTests/TestData/chat_one_function_response.json, dotnet/src/Connectors/Connectors.Google.UnitTests/TestData/chat_text_with_thought_signature_response.json, dotnet/src/Connectors/Connectors.Google/Extensions/GeminiKernelFunctionMetadataExtensions.cs
  Service Selection Architecture
    · Service Selection Flow
  Execution Settings Hierarchy
    · Settings Class Hierarchy
  Function Choice and Tool Call Behavior
    · Auto-Function Invocation Loop
  Microsoft.Extensions.AI Interoperability
  Python Service Configuration

## · Other AI Service Connectors  (L3820)
  源文件: docs/decisions/0054-processes.md, docs/decisions/diagrams/process/process_diagram_basic.png, dotnet/samples/Concepts/ChatCompletion/Google_GeminiChatCompletionWithFile.cs, dotnet/samples/Concepts/ChatCompletion/Google_GeminiChatCompletionWithThinking.cs, dotnet/samples/Concepts/ChatCompletion/MistralAI_ChatCompletion.cs, dotnet/samples/Concepts/FunctionCalling/NexusRaven_FunctionCalling.cs, dotnet/samples/Concepts/Plugins/CreatePromptPluginFromDirectory.cs, dotnet/samples/Demos/AmazonBedrockModels/AmazonBedrockAIModels.csproj, dotnet/samples/Demos/AmazonBedrockModels/Program.cs, dotnet/samples/Demos/OnnxSimpleChatWithCuda/OnnxSimpleChatWithCuda.csproj, dotnet/samples/Demos/OnnxSimpleChatWithCuda/Program.cs, dotnet/samples/Demos/OnnxSimpleChatWithCuda/README.md
  Architecture Overview
    · Core Service Abstractions
  Supported Providers
    · Google AI and Vertex AI
    · MistralAI
    · Azure AI Inference
    · Ollama, ONNX, and NVIDIA
  Implementation Patterns
    · Gemini Data Flow
    · Execution Settings and Tool Calling
  Provider-Specific Features
    · Gemini ThinkingConfig
    · Multimodal Support
    · Structured Outputs

## · Agent Framework  (L4168)
  源文件: .github/_typos.toml, docs/decisions/0071-multi-agent-orchestration.md, dotnet/Directory.Packages.props, dotnet/docs/EXPERIMENTS.md, dotnet/samples/Concepts/Concepts.csproj, dotnet/samples/Concepts/FunctionCalling/FunctionCalling_SharedState.cs, dotnet/samples/Concepts/README.md, dotnet/samples/Concepts/Resources/travel-destination-overview.txt, dotnet/samples/GettingStartedWithAgents/GettingStartedWithAgents.csproj, dotnet/samples/GettingStartedWithAgents/README.md, dotnet/src/Agents/UnitTests/Agents.UnitTests.csproj, dotnet/src/IntegrationTests/IntegrationTests.csproj
  Core Architecture
    · Base Agent Abstractions
    · Agent Thread Management
  Agent Implementations
    · ChatCompletionAgent
    · OpenAI Assistant Agent
    · Azure AI Agent
    · Bedrock Agent
  Multi-Agent Orchestration
  Cross-Language Implementation
  Agent Declarative Specifications

## · Agent Architecture and Base Classes  (L4489)
  源文件: dotnet/samples/Concepts/Agents/AzureAIAgent_FileManipulation.cs, dotnet/samples/Concepts/Agents/ChatCompletion_HistoryReducer.cs, dotnet/samples/Concepts/Agents/ChatCompletion_ServiceSelection.cs, dotnet/samples/Concepts/Agents/ComplexChat_NestedShopper.cs, dotnet/samples/Concepts/Agents/MixedChat_Agents.cs, dotnet/samples/Concepts/Agents/OpenAIAssistant_ChartMaker.cs, dotnet/samples/Concepts/Agents/OpenAIAssistant_FileManipulation.cs, dotnet/samples/Concepts/Agents/OpenAIAssistant_FunctionFilters.cs, dotnet/samples/Concepts/ChatCompletion/ChatHistoryReducers/ChatCompletionServiceExtensions.cs, dotnet/samples/Concepts/ChatCompletion/ChatHistoryReducers/ChatCompletionServiceWithReducer.cs, dotnet/samples/Concepts/ChatCompletion/ChatHistoryReducers/ChatHistoryExtensions.cs, dotnet/samples/Concepts/ChatCompletion/ChatHistoryReducers/ChatHistoryMaxTokensReducer.cs
  Overview of Agent Architecture
    · Agent System Architecture
  Core Components
    · Core Component Relationships
  Agent Base Class
    · Key Properties
    · Core Methods
  AgentThread
    · Thread Implementations
  AgentChannel
  Agent Invocation Flow
    · ChatCompletionAgent Invocation Sequence
  Declarative Agent Definitions (DeclarativeSpecMixin)
    · Agent Specification Structure
  AgentChat and GroupChat
    · Chat History Synchronization
  Content Generation and Mapping

## · .NET Agent Implementations  (L4873)
  源文件: dotnet/samples/Concepts/Agents/AzureAIAgent_Streaming.cs, dotnet/samples/Concepts/Agents/ChatCompletion_FunctionTermination.cs, dotnet/samples/Concepts/Agents/ChatCompletion_ServiceSelection.cs, dotnet/samples/Concepts/Agents/ChatCompletion_Streaming.cs, dotnet/samples/Concepts/Agents/OpenAIAssistant_Streaming.cs, dotnet/samples/GettingStartedWithAgents/AzureAIAgent/Step08_AzureAIAgent_Declarative.cs, dotnet/samples/GettingStartedWithAgents/AzureAIAgent/Step09_AzureAIAgent_BingGrounding.cs, dotnet/samples/GettingStartedWithAgents/BedrockAgent/Step01_BedrockAgent.cs, dotnet/samples/GettingStartedWithAgents/BedrockAgent/Step02_BedrockAgent_CodeInterpreter.cs, dotnet/samples/GettingStartedWithAgents/BedrockAgent/Step03_BedrockAgent_Functions.cs, dotnet/samples/GettingStartedWithAgents/BedrockAgent/Step04_BedrockAgent_Trace.cs, dotnet/samples/GettingStartedWithAgents/BedrockAgent/Step05_BedrockAgent_FileSearch.cs
  Agent Implementation Architecture
    · Agent Hierarchy and Channels
  ChatCompletionAgent Implementation
    · Core Features
    · Function Invocation Loop
  OpenAI Assistant Implementations
    · OpenAIAssistantAgent (Assistant API)
    · OpenAIResponseAgent (Responses API)
  AzureAIAgent Implementation
  BedrockAgent Implementation
  Declarative Agent Definitions
  Summary Table of Agent Capabilities

## · Python Agent Implementations  (L5147)
  源文件: python/.vscode/launch.json, python/pyproject.toml, python/samples/concepts/README.md, python/samples/concepts/agents/azure_ai_agent/azure_ai_agent_azure_ai_search.py, python/samples/concepts/agents/azure_ai_agent/azure_ai_agent_file_manipulation.py, python/samples/concepts/agents/azure_ai_agent/azure_ai_agent_streaming.py, python/samples/concepts/agents/bedrock_agent/bedrock_agent_retrieval.py, python/samples/concepts/agents/bedrock_agent/bedrock_agent_simple_chat.py, python/samples/concepts/agents/bedrock_agent/bedrock_agent_simple_chat_streaming.py, python/samples/concepts/agents/bedrock_agent/bedrock_agent_with_code_interpreter.py, python/samples/concepts/agents/bedrock_agent/bedrock_agent_with_code_interpreter_streaming.py, python/samples/concepts/agents/bedrock_agent/bedrock_agent_with_kernel_function.py
  Agent Implementation Architecture
    · Code Entity Space: Agent Class Hierarchy
  Azure AI Agent Implementation
    · Core Architecture and Run Loop
    · Key Features
  OpenAI Assistant Agent Implementation
    · Invocation and Tool Mapping
  OpenAI Responses Agent Implementation
    · Streaming and Delta Processing
  Amazon Bedrock Agent Implementation
  Specialized Agent Implementations
    · CopilotStudio Agent
    · AutoGen Conversable Agent
  Content Generation and Tool Mapping

## · Multi-Agent Orchestration  (L5393)
  源文件: .github/_typos.toml, docs/decisions/0071-multi-agent-orchestration.md, dotnet/Directory.Packages.props, dotnet/docs/EXPERIMENTS.md, dotnet/samples/Concepts/Concepts.csproj, dotnet/samples/Concepts/FunctionCalling/FunctionCalling_SharedState.cs, dotnet/samples/Concepts/README.md, dotnet/samples/Concepts/Resources/travel-destination-overview.txt, dotnet/samples/GettingStartedWithAgents/GettingStartedWithAgents.csproj, dotnet/samples/GettingStartedWithAgents/README.md, dotnet/samples/GettingStartedWithAgents/Step04_KernelFunctionStrategies.cs, dotnet/src/Agents/Abstractions/AgentChannel.cs
  Orchestration Patterns
    · Group Chat Orchestration
    · Handoff and Sequential Orchestration
  Magentic-One Pattern
  Actor Model and Runtime
    · Agent Runtime Space
  Execution and Results
    · OrchestrationResult
    · Communication Channels

## · Advanced Features  (L5607)
  源文件: dotnet/nuget/nuget-package.props, dotnet/samples/Concepts/Memory/OpenAI_EmbeddingGeneration.cs, dotnet/src/Functions/Functions.OpenApi/CompatibilitySuppressions.xml, dotnet/src/Functions/Functions.OpenApi/Extensions/OpenApiFunctionExecutionParameters.cs, dotnet/src/Functions/Functions.OpenApi/Extensions/RestApiOperationExtensions.cs, dotnet/src/Functions/Functions.OpenApi/Model/RestApiOperation.cs, dotnet/src/Functions/Functions.OpenApi/OpenApi/OpenApiDocumentParser.cs, dotnet/src/Functions/Functions.OpenApi/OpenApiKernelPluginFactory.cs, dotnet/src/Functions/Functions.OpenApi/RestApiOperationRunner.cs, dotnet/src/Functions/Functions.OpenApi/RestApiOperationServerUrlValidationOptions.cs, dotnet/src/Functions/Functions.OpenApi/ServerUrlValidator.cs, dotnet/src/Functions/Functions.Prompty/Functions.Prompty.csproj
  OpenAPI Integration
    · OpenAPI Plugin Factory Architecture
    · REST API Operation Execution
  Prompt Execution Settings and Tool Calling
    · Tool Call Processing Pipeline
  Filtering and Extensibility
    · Filter Pipeline Architecture
  Model Context Protocol (MCP) Integration
    · MCP Integration Flow
  Process Framework
  Python Code Execution Tools

## · OpenAPI Integration  (L5839)
  源文件: dotnet/nuget/nuget-package.props, dotnet/samples/Concepts/Memory/OpenAI_EmbeddingGeneration.cs, dotnet/samples/Concepts/Plugins/OpenApiPlugin_CustomHttpContentReader.cs, dotnet/src/Functions/Functions.OpenApi.Extensions/Extensions/ApiManifestKernelExtensions.cs, dotnet/src/Functions/Functions.OpenApi/CompatibilitySuppressions.xml, dotnet/src/Functions/Functions.OpenApi/Extensions/OpenApiFunctionExecutionParameters.cs, dotnet/src/Functions/Functions.OpenApi/Extensions/OpenApiKernelExtensions.cs, dotnet/src/Functions/Functions.OpenApi/Extensions/RestApiOperationExtensions.cs, dotnet/src/Functions/Functions.OpenApi/Functions.OpenApi.csproj, dotnet/src/Functions/Functions.OpenApi/HttpResponseContentReader.cs, dotnet/src/Functions/Functions.OpenApi/HttpResponseContentReaderContext.cs, dotnet/src/Functions/Functions.OpenApi/Model/RestApiOperation.cs
  Architecture Overview
    · OpenAPI Integration Pipeline
    · Core Component Architecture
  Document Processing Pipeline
    · OpenAPI Parsing Flow
  Core Components
    · OpenApiKernelPluginFactory
    · OpenApiDocumentParser
    · RestApiOperationRunner
  Python Implementation
    · Python OpenAPI Components
  Function Creation and Execution
    · Parameter Processing and Sanitization
    · Function Execution Flow
  Configuration and Security
    · OpenApiFunctionExecutionParameters
    · SSRF Protection via ServerUrlValidator

## · Prompt Execution Settings and Tool Calling  (L6111)
  源文件: dotnet/docs/OPENAI-CONNECTOR-MIGRATION.md, dotnet/samples/Concepts/ChatCompletion/OpenAI_ChatCompletionExtraBody.cs, dotnet/samples/Concepts/FunctionCalling/FunctionCalling.cs, dotnet/samples/Concepts/PromptTemplates/ChatPromptWithAudio.cs, dotnet/samples/Concepts/PromptTemplates/ChatPromptWithBinary.cs, dotnet/samples/Concepts/PromptTemplates/HandlebarsVisionPrompts.cs, dotnet/src/Connectors/Connectors.AzureOpenAI.UnitTests/Services/AzureOpenAIChatCompletionExtraBodyTests.cs, dotnet/src/Connectors/Connectors.AzureOpenAI.UnitTests/Services/AzureOpenAIChatCompletionServiceTests.cs, dotnet/src/Connectors/Connectors.AzureOpenAI.UnitTests/Settings/AzureOpenAIPromptExecutionSettingsTests.cs, dotnet/src/Connectors/Connectors.AzureOpenAI/Core/AzureClientCore.ChatCompletion.cs, dotnet/src/Connectors/Connectors.AzureOpenAI/Settings/AzureOpenAIPromptExecutionSettings.cs, dotnet/src/Connectors/Connectors.Google.UnitTests/Core/Gemini/Clients/GeminiChatClientFunctionCallingTests.cs
  Overview of Prompt Execution Settings
    · Core Configuration Properties
    · Structured Outputs and JSON Schema
  Tool Calling and Function Invocation
    · Function Choice Behavior Modes
    · The Auto-Invocation Loop
    · Safety and Limits
  Implementation Details
    · Mapping to Provider Options
    · Chat Prompt Parsing
    · Metrics and Telemetry

## · Filtering and Extensibility  (L6362)
  源文件: dotnet/samples/Concepts/AudioToText/OpenAI_AudioToText.cs, dotnet/samples/Concepts/ChatCompletion/ChatHistorySerialization.cs, dotnet/samples/Concepts/ChatCompletion/OpenAI_ChatCompletionWithVision.cs, dotnet/samples/Concepts/ImageToText/HuggingFace_ImageToText.cs, dotnet/samples/Concepts/Resources/what-is-semantic-kernel.json, dotnet/src/Connectors/Connectors.OpenAI.UnitTests/Core/AutoFunctionInvocationFilterTests.cs, dotnet/src/InternalUtilities/planning/PlannerInstrumentation.cs, dotnet/src/SemanticKernel.Abstractions/AI/ChatCompletion/AuthorRole.cs, dotnet/src/SemanticKernel.Abstractions/AI/ChatCompletion/ChatHistory.cs, dotnet/src/SemanticKernel.Abstractions/AI/ChatCompletion/StreamingKernelContentItemCollection.cs, dotnet/src/SemanticKernel.Abstractions/AI/PromptNode.cs, dotnet/src/SemanticKernel.Abstractions/Contents/BinaryContent.cs
  Filter System Overview
    · Filter Architecture
  Content Model and ChatHistory
    · Chat Message Content Model
    · ChatHistory Management
  Filter Types and Contexts
    · Function Invocation Filters
    · Prompt Rendering Filters
    · Auto Function Invocation Filters
  Filter Pipeline Architecture
    · .NET Filter Pipeline
    · Python Filter Pipeline
  Extensibility Patterns
    · Service Provider Integration
    · Context Modification Patterns
  Implementation Details
    · Thread Safety and Immutability
    · Performance Considerations

## · Python Code Execution Tools  (L6648)
  源文件: dotnet/samples/Demos/CodeInterpreterPlugin/CodeInterpreterPlugin.csproj, dotnet/samples/Demos/CodeInterpreterPlugin/Program.cs, dotnet/samples/Demos/CodeInterpreterPlugin/README.md, dotnet/src/Experimental/Orchestration.Flow.IntegrationTests/FlowOrchestratorTests.cs, dotnet/src/IntegrationTests/Plugins/Core/SessionsPythonPluginTests.cs, dotnet/src/IntegrationTests/TestData/SessionsPythonPlugin/file_to_upload_1.txt, dotnet/src/IntegrationTests/TestData/SessionsPythonPlugin/file_to_upload_2.txt, dotnet/src/IntegrationTests/TestSettings/AzureContainerAppSessionPoolConfiguration.cs, dotnet/src/InternalUtilities/src/Http/HttpClientProvider.cs, dotnet/src/InternalUtilities/src/System/PathUtilities.cs, dotnet/src/InternalUtilities/test/HttpMessageHandlerStub.cs, dotnet/src/Plugins/Plugins.Core/CodeInterpreter/SessionsPythonCodeExecutionResult.cs
  Overview
    · System Architecture
  Core Implementation Details
    · .NET Implementation: `SessionsPythonPlugin`
    · Python Implementation: `SessionsPythonTool`
  Configuration and Settings
    · `SessionsPythonSettings`
  Security and Path Validation
    · Path Validation Logic
  Data Flow: Code Execution
  Integration Patterns
    · Auto-Function Calling
    · Comparison with other Plugins

## · Process Framework  (L6842)
  源文件: .vscode/extensions.json, .vscode/launch.json, .vscode/settings.json, .vscode/tasks.json, docs/decisions/0072-agents-with-memory.md, dotnet/samples/Concepts/Agents/ChatCompletion_Mem0.cs, dotnet/samples/Concepts/Agents/ChatCompletion_Rag.cs, dotnet/samples/Concepts/Agents/ChatCompletion_Whiteboard.cs, dotnet/samples/Demos/ProcessWithDapr/Controllers/ProcessController.cs, dotnet/samples/Demos/ProcessWithDapr/ProcessWithDapr.csproj, dotnet/samples/Demos/ProcessWithDapr/README.md, dotnet/samples/GettingStartedWithProcesses/Step04/Steps/RenderMessageStep.cs
  Overview and Core Abstractions
    · Key Classes
    · Natural Language to Code Entity Mapping
  Process Building and Event Routing
    · Event Propagation
    · Routing Logic
  Runtimes: Local vs. Distributed
    · 1. Local Runtime
    · 2. Dapr Distributed Runtime
    · Runtime Architecture Diagram
  Python Implementation
    · Python Dapr Integration
  Data Flow: Event to Function Call

## · Model Context Protocol (MCP) Integration  (L7078)
  源文件: dotnet/samples/Demos/AgentFrameworkWithAspire/ChatWithAgent.AppHost/ChatWithAgent.AppHost.csproj, dotnet/samples/Demos/BookingRestaurant/BookingRestaurant.csproj, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPClient/Extensions/PromptResultExtensions.cs, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPClient/Extensions/ReadResourceResultExtensions.cs, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPClient/Extensions/RoleExtensions.cs, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPClient/MCPClient.csproj, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPClient/Program.cs, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPServer/Extensions/McpServerBuilderExtensions.cs, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPServer/Extensions/VectorStoreExtensions.cs, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPServer/MCPServer.csproj, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPServer/Program.cs, dotnet/samples/Demos/ModelContextProtocolClientServer/MCPServer/Prompts/PromptDefinition.cs
  Overview of MCP Architecture
    · Data Flow and Component Interaction
  MCP Client Integration
    · Supported Transports
    · Implementation Detail: Name Normalization
  Sampling and Security
    · Sampling Consent Callback
  SK-as-MCP-Server
    · .NET Implementation
    · Python Implementation
  Content Mapping
  Advanced Demos and Samples

## · Development Guide  (L7304)
  源文件: .github/workflows/codeql-analysis.yml, .github/workflows/dotnet-build-and-test.yml, .github/workflows/dotnet-ci.yml, .github/workflows/dotnet-format.yml, .github/workflows/dotnet-integration-tests.yml, .github/workflows/markdown-link-check.yml, .github/workflows/python-build.yml, .github/workflows/python-integration-tests.yml, .github/workflows/python-lint.yml, .github/workflows/python-manual-release.yml, .github/workflows/python-test-coverage-report.yml, .github/workflows/python-test-coverage.yml
  Development Environment Setup
    · .NET Development
    · Python Development
    · Bridge: Development Tooling to Code Entities
  Building and Testing
    · .NET Build System
    · Python Build System
  Configuration and Telemetry
    · Bridge: CI/CD Pipeline to Code Quality
  Sample Applications
  Contribution Workflow

## · CI/CD and Build System  (L7460)
  源文件: .github/.linkspector.yml, .github/dependabot.yml, .github/workflows/codeql-analysis.yml, .github/workflows/dotnet-build-and-test.yml, .github/workflows/dotnet-ci.yml, .github/workflows/dotnet-format.yml, .github/workflows/dotnet-integration-tests.yml, .github/workflows/label-title-prefix.yml, .github/workflows/markdown-link-check.yml, .github/workflows/python-build.yml, .github/workflows/python-integration-tests.yml, .github/workflows/python-lint.yml
  Overview
    · CI/CD Architecture
  Python Build System
    · Python Project Configuration
    · Python Testing Workflows
    · Python Code Quality
  .NET Build System
    · .NET Build and Test Workflow
    · .NET Code Formatting
  Security and Dependency Management
    · CodeQL Analysis
    · Dependabot
    · Utility Workflows
  Integration Testing Strategy
    · Integration Test Configuration
    · Data Stores

## · Sample Applications and Getting Started  (L7709)
  源文件: dotnet/notebooks/00-getting-started.ipynb, dotnet/notebooks/01-basic-loading-the-kernel.ipynb, dotnet/notebooks/02-running-prompts-from-file.ipynb, dotnet/notebooks/03-semantic-function-inline.ipynb, dotnet/notebooks/04-kernel-arguments-chat.ipynb, dotnet/notebooks/07-DALL-E-3.ipynb, dotnet/notebooks/08-chatGPT-with-DALL-E-3.ipynb, dotnet/samples/Concepts/Agents/OpenAIAssistant_Templating.cs, dotnet/samples/Concepts/ChatCompletion/Onnx_ChatCompletion.cs, dotnet/samples/Concepts/ChatCompletion/Onnx_ChatCompletionStreaming.cs, dotnet/samples/Concepts/ChatCompletion/OpenAI_ReasonedFunctionCalling.cs, dotnet/samples/Concepts/ChatCompletion/OpenAI_RepeatedFunctionCalling.cs
  Overview
  .NET Sample Applications
    · Concepts Samples
    · Getting Started with Agents and Processes
    · Demo Applications
  Python Sample Applications
    · Getting Started Notebooks
    · Learn Resources and Concepts
  Prompt Template Samples Directory
  Configuration Management
    · .NET Configuration System
    · Python Configuration System
  Running Samples
    · Command Line (.NET)
    · Jupyter Notebooks

## · Configuration and Setup  (L8026)
  源文件: .vscode/extensions.json, .vscode/launch.json, .vscode/settings.json, .vscode/tasks.json, dotnet/samples/Demos/ProcessWithDapr/Controllers/ProcessController.cs, dotnet/samples/Demos/ProcessWithDapr/ProcessWithDapr.csproj, dotnet/samples/Demos/ProcessWithDapr/README.md, dotnet/samples/Demos/TelemetryWithAppInsights/Program.cs, dotnet/samples/Demos/TelemetryWithAppInsights/README.md, dotnet/samples/Demos/TelemetryWithAppInsights/TelemetryWithAppInsights.csproj, dotnet/samples/Demos/TelemetryWithAppInsights/TestConfiguration.cs, dotnet/samples/GettingStartedWithProcesses/Step04/Steps/RenderMessageStep.cs
  .NET Development Setup
    · Local Configuration Management
    · Integration Test Configuration (`TestConfiguration.cs`)
    · Model Diagnostics and Telemetry
  Python Development Setup
    · Environment Configuration (`.env`)
    · Tooling and Pre-commit Hooks
  IDE Integration (Visual Studio Code)
    · Tasks and Launch Configurations
    · Recommended Extensions
  Testing Infrastructure
    · .NET Test Settings (`testsettings.json`)
    · Python Testing

## · Glossary  (L8247)
  源文件: .github/.linkspector.yml, .github/_typos.toml, FEATURE_MATRIX.md, README.md, docs/COSINE_SIMILARITY.md, docs/DOT_PRODUCT.md, docs/EMBEDDINGS.md, docs/EUCLIDEAN_DISTANCE.md, docs/GLOSSARY.md, docs/PLANNERS.md, docs/PLUGINS.md, docs/PROMPT_TEMPLATE_LANGUAGE.md
  Core Orchestration Terms
    · Kernel
    · Plugin
    · Kernel Function
    · Kernel Arguments
  Technical Concept Mapping
    · Natural Language Space to Code Entity Space: Function Invocation
  Specialized Jargon
    · Auto-Function Invocation (Tool Calling)
    · Filters
    · Content Model
  Agent Framework Terms
    · Agent
    · Multi-Agent Orchestration
  Infrastructure & Tooling
    · Model Context Protocol (MCP)
    · Central Package Management (CPM)
    · Feature Matrix