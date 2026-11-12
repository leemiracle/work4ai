<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ParrotServe · page 8 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [parrot/testing/fake_engine_server.py](parrot/testing/fake_engine_server.py)
- [tests/serve/test_context.py](tests/serve/test_context.py)
- [tests/serve/test_graph.py](tests/serve/test_graph.py)
- [tests/serve/test_prefix_matcher.py](tests/serve/test_prefix_matcher.py)
- [tests/serve/test_session.py](tests/serve/test_session.py)
- [tests/serve/test_sv.py](tests/serve/test_sv.py)
- [tests/serve/test_tokenizer.py](tests/serve/test_tokenizer.py)

</details>



This document covers the development infrastructure and testing framework for ParrotServe, including testing utilities, fake server implementations, and comprehensive test suites for all major system components. The testing infrastructure enables isolated unit testing, integration testing, and performance validation of the distributed LLM serving system.

For information about system configuration and deployment procedures, see [Configuration and Deployment](#7). For details about the runtime APIs being tested, see [HTTP APIs](#6).

## Testing Infrastructure

ParrotServe provides a comprehensive testing framework built around fake server implementations and isolated component testing. The infrastructure supports both unit testing of individual components and integration testing of the complete system workflow.

### Fake Server Architecture

The testing framework includes sophisticated fake server implementations that simulate the behavior of real LLM engines without requiring actual model inference.

```mermaid
graph TB
    subgraph "Testing Environment"
        TestClient["Test Client Applications"]
        FakeCore["Fake ServeCore Server<br/>localhost:9000"]
        FakeEngine["fake_engine_server.py<br/>localhost:9001"]
    end
    
    subgraph "Fake Engine Components"
        EngineApp["FastAPI Application"]
        FillEndpoint["/fill endpoint"]
        GenerateEndpoint["/generate endpoint"]
        StreamEndpoint["/generate_stream endpoint"]
        FreeEndpoint["/free_context endpoint"]
        PingEndpoint["/ping endpoint"]
    end
    
    subgraph "Simulation Logic"
        TokenSim["Token Processing Simulation<br/>TESTING_FILL_PERTOKEN_TIME"]
        MemSim["Memory Usage Simulation<br/>context_len_map"]
        RuntimeSim["Runtime Info Simulation<br/>EngineRuntimeInfo"]
        HeartbeatSim["Heartbeat Daemon<br/>fake_engine_daemon()"]
    end
    
    TestClient --> FakeCore
    FakeCore --> FakeEngine
    FakeEngine --> EngineApp
    
    EngineApp --> FillEndpoint
    EngineApp --> GenerateEndpoint
    EngineApp --> StreamEndpoint
    EngineApp --> FreeEndpoint
    EngineApp --> PingEndpoint
    
    FillEndpoint --> TokenSim
    GenerateEndpoint --> TokenSim
    StreamEndpoint --> TokenSim
    FreeEndpoint --> MemSim
    PingEndpoint --> RuntimeSim
    
    FakeEngine --> HeartbeatSim
    HeartbeatSim --> FakeCore
```

The `fake_engine_server.py` implements a complete engine simulation that tracks context length, simulates token processing time, and provides realistic runtime information reporting. The fake engine registers with the ServeCore using the same protocols as real engines.

**Sources:** [parrot/testing/fake_engine_server.py:1-240]()

### Test Organization and Utilities

ParrotServe organizes tests by system component, with each major subsystem having dedicated test modules that verify both isolated functionality and integration behavior.

```mermaid
graph TB
    subgraph "Test Module Organization"
        TestServe["tests/serve/"]
        TestContext["test_context.py<br/>Context & Prefix Cache"]
        TestGraph["test_graph.py<br/>Graph Operations"]
        TestSV["test_sv.py<br/>Semantic Variables"]
        TestSession["test_session.py<br/>Session Management"]
        TestTokenizer["test_tokenizer.py<br/>Tokenization"]
        TestPrefix["test_prefix_matcher.py<br/>Prefix Matching"]
    end
    
    subgraph "Testing Infrastructure"
        FakeEngineServer["fake_engine_server.py"]
        LocalhostDaemon["localhost_server_daemon"]
        GetConfigs["get_configs.py"]
    end
    
    subgraph "Core Components Under Test"
        ContextManager["ServeCoreContextManager"]
        PrefixCache["PrefixCache"]
        ComputeGraph["ComputeGraph"]
        SemanticVarMgr["SemanticVariableManager"]
        SessionManager["SessionManager"]
        TokenizerWrapper["TokenizersWrapper"]
    end
    
    TestServe --> TestContext
    TestServe --> TestGraph
    TestServe --> TestSV
    TestServe --> TestSession
    TestServe --> TestTokenizer
    TestServe --> TestPrefix
    
    TestContext --> ContextManager
    TestContext --> PrefixCache
    TestGraph --> ComputeGraph
    TestSV --> SemanticVarMgr
    TestSession --> SessionManager
    TestTokenizer --> TokenizerWrapper
    
    FakeEngineServer --> TestSession
    LocalhostDaemon --> TestSession
    GetConfigs --> TestContext
```

**Sources:** [tests/serve/test_context.py:1-79](), [tests/serve/test_graph.py:1-223](), [tests/serve/test_sv.py:1-76](), [tests/serve/test_session.py:1-195]()

## Component Testing

### Context Management Testing

The context management testing validates the `ServeCoreContextManager` and `PrefixCache` implementations, ensuring proper context lifecycle management and prefix sharing optimization.

The `test_context.py` module provides comprehensive testing for:

- **Prefix Cache Operations**: Testing `PrefixCache.cache_prefix_context()` with hash-based prefix identification using `ServeCoreContextManager._hash_var_id()`
- **Context Registration**: Validating `ServeCoreContextManager.register_engine_prefix_cache()` for engine-specific context pools
- **Task Context Assignment**: Testing `ServeCoreContextManager.set_task_contexts()` for proper context allocation to `CompletionTask` instances
- **Reference Counting**: Verifying context reference counting mechanisms in `_context_ref_counter`

**Sources:** [tests/serve/test_context.py:23-74]()

### Graph Operations Testing

Graph testing validates the core computation graph construction, manipulation, and traversal algorithms that enable semantic variable dependencies and request chaining.

Key test scenarios include:

- **Request Chain Construction**: Testing `RequestChain.from_nodes()` with `ConstantFill`, `PlaceholderFill`, and `PlaceholderGen` nodes
- **Graph Insertion and Removal**: Validating `ComputeGraph.insert_and_update_request_chain()` and `ComputeGraph.remove_completion_chain()`
- **Dependency Traversal**: Testing semantic variable activation with `activate_sv()` and `PerformanceCriteria` propagation
- **Chain Parsing**: Validating `ChunkedSemanticCallRequest.parse_from_payload()` for template-based request parsing

The graph testing includes complex dependency scenarios where semantic variables form chains (A → B → C) with proper depth calculation and activation propagation.

**Sources:** [tests/serve/test_graph.py:18-223]()

### Semantic Variable Testing

Semantic variable testing focuses on the core abstraction that enables cross-request dependencies and content-based optimization.

Test coverage includes:

- **Content-Based Hashing**: Testing `SemanticVariableManager._get_local_var_by_content()` for duplicate content detection
- **Variable Creation**: Validating `SemanticVariableManager.create_var()` and `SemanticVariableManager.create_vars_for_semantic_request_chain()`
- **Request Chain Hashing**: Testing consistent hash generation for identical request chains to enable optimization
- **Local Variable Spaces**: Validating session-scoped variable management with `register_local_var_space()`

**Sources:** [tests/serve/test_sv.py:15-75]()

### Session Management Testing

Session testing validates the complete session lifecycle and integration between multiple system components.

```mermaid
graph TB
    subgraph "Session Test Components"
        SessionMgr["SessionManager<br/>life_span=10"]
        GraphExec["GraphExecutor"]
        NativeExec["PyNativeExecutor"]
        GlobalSched["GlobalScheduler"]
        TaskCreator["TaskCreator"]
    end
    
    subgraph "Supporting Services"
        VarMgr["SemanticVariableManager"]
        TokenWrapper["TokenizersWrapper"]
        ContextMgr["ServeCoreContextManager"]
        EngineMgr["EngineManager"]
        PrefixMatch["PrefixMatcher"]
    end
    
    subgraph "Test Operations"
        SessionReg["Session Registration<br/>register_session()"]
        SessionExp["Session Expiration<br/>check_running_sessions()"]
        GraphTest["Graph Execution Test<br/>RequestChain processing"]
        NativeTest["Native Function Test<br/>@native_function"]
    end
    
    SessionMgr --> GraphExec
    SessionMgr --> TaskCreator
    SessionMgr --> GlobalSched
    GraphExec --> NativeExec
    
    SessionMgr --> VarMgr
    SessionMgr --> TokenWrapper
    SessionMgr --> ContextMgr
    SessionMgr --> EngineMgr
    SessionMgr --> PrefixMatch
    
    SessionReg --> SessionMgr
    SessionExp --> SessionMgr
    GraphTest --> GraphExec
    NativeTest --> NativeExec
```

Session testing includes integration with the fake engine server using `fake_engine_server()` context manager and validates both semantic function execution and native Python function execution through the `@native_function` decorator.

**Sources:** [tests/serve/test_session.py:36-195]()

## Development Tools

### Tokenizer Testing

The tokenizer testing validates the `TokenizersWrapper` implementation that provides unified tokenization across different model families.

Test scenarios cover:

- **Tokenizer Registration**: Testing `TokenizersWrapper.register_tokenizer()` with different tokenizer types
- **Encoding/Decoding**: Validating `tokenize()` and `detokenize()` operations with known test vectors
- **Request Tokenization**: Testing `CompletionTask.tokenize_chain()` for request chain tokenization across multiple tokenizers
- **Multi-Tokenizer Support**: Ensuring consistent results across different tokenizer implementations like `"hf-internal-testing/llama-tokenizer"` and `"facebook/opt-13b"`

The tests use predefined test vectors to ensure tokenization consistency:

```python
TESTING_PROMPT_TEXT = "He is widely acknowledged as one of the top achievers in his class"
TESTING_TOKEN_IDS = [940, 338, 17644, 24084, 3192, 408, 697, 310, 278, 2246, 3657, 347, 874, 297, 670, 770]
```

**Sources:** [tests/serve/test_tokenizer.py:18-106]()

### Prefix Matching Testing

Prefix matching testing validates the `PrefixMatcher` implementation that optimizes shared prompt prefixes for performance.

The testing covers:

- **Threshold-Based Addition**: Testing prefix addition only after reaching `PrefixMatcher._GP_THRESHOLD + 1` occurrences
- **Prefix Query Operations**: Validating `query_prefix()` for finding longest matching prefixes
- **Counter Management**: Testing `_prefix_counter` tracking for prefix frequency
- **Start Length Configuration**: Testing prefix matching with `PrefixMatcher._START_LEN` constraints

The test creates a scenario where multiple similar strings share a common prefix, validates that the prefix is detected only after sufficient frequency, and verifies correct prefix/suffix splitting.

**Sources:** [tests/serve/test_prefix_matcher.py:4-23]()

---

