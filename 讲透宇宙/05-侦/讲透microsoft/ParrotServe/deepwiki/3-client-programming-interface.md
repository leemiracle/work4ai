<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ParrotServe · page 3 Client Programming Interface · fetched 2026-10-26 -->

# Client Programming Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env-dev](.env-dev)
- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [TRANSPARENCY.md](TRANSPARENCY.md)
- [benchmark/bench_kernel.py](benchmark/bench_kernel.py)
- [docs/README.md](docs/README.md)
- [docs/get_started/launch_server.md](docs/get_started/launch_server.md)
- [docs/sys_design/serve_layer/graph.md](docs/sys_design/serve_layer/graph.md)
- [docs/user_docs/parrot_apis.md](docs/user_docs/parrot_apis.md)
- [docs/user_docs/pfunc.md](docs/user_docs/pfunc.md)
- [docs/version_drafts/v3.md](docs/version_drafts/v3.md)
- [parrot/engine/engine_creator.py](parrot/engine/engine_creator.py)
- [parrot/frontend/pfunc/function.py](parrot/frontend/pfunc/function.py)
- [parrot/frontend/pfunc/interface.py](parrot/frontend/pfunc/interface.py)
- [parrot/frontend/pfunc/vm.py](parrot/frontend/pfunc/vm.py)
- [parrot/testing/localhost_server_daemon.py](parrot/testing/localhost_server_daemon.py)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)
- [tests/engine/builtin/test_llama.py](tests/engine/builtin/test_llama.py)
- [tests/engine/builtin/test_sampler.py](tests/engine/builtin/test_sampler.py)
- [tests/engine/test_engine.py](tests/engine/test_engine.py)
- [tests/engine/test_http_server.py](tests/engine/test_http_server.py)

</details>



## Purpose and Scope

The Client Programming Interface provides user-facing programming abstractions for developing LLM-based applications with ParrotServe. This interface enables developers to write semantic programs using Python decorators and semantic variables that automatically leverage ParrotServe's optimization capabilities including request parallelization, batching, and context sharing.

For detailed information about individual API components, see [PFunc API](#3.1). For VirtualMachine session management, see [VirtualMachine](#3.2). For complete application examples, see [Example Applications](#3.3). For server-side request processing, see [Request Processing Pipeline](#2.3).

## Client Interface Architecture

The client programming interface consists of three main layers that abstract the underlying distributed serving system:

```mermaid
graph TB
    subgraph "User Application Layer"
        UserCode["User Application Code<br/>tell_me_a_joke.py"]
        MainFunc["main() function"]
    end
    
    subgraph "PFunc Programming Interface"
        Decorators["Function Decorators<br/>@P.semantic_function<br/>@P.native_function"]
        ParamTypes["Parameter Types<br/>P.Input, P.Output"]
        SemVar["SemanticVariable<br/>Content containers"]
    end
    
    subgraph "VirtualMachine Runtime"
        VM["VirtualMachine<br/>Session management"]
        FuncRegistry["Function Registry<br/>BasicFunction storage"]
        APIClient["HTTP API Client<br/>ServeCore communication"]
    end
    
    subgraph "ServeCore Communication"
        SessionAPI["Session APIs<br/>/session endpoints"]
        CallAPI["Semantic Call APIs<br/>/semantic_call endpoints"] 
        VarAPI["Variable APIs<br/>/semantic_var endpoints"]
    end
    
    UserCode --> Decorators
    MainFunc --> VM
    Decorators --> SemVar
    Decorators --> ParamTypes
    
    VM --> FuncRegistry
    VM --> APIClient
    
    APIClient --> SessionAPI
    APIClient --> CallAPI
    APIClient --> VarAPI
    
    style VM fill:#ffcc99
    style Decorators fill:#ccffcc
    style SemVar fill:#ccccff
```

Sources: [parrot/frontend/pfunc/vm.py:49-481](), [parrot/frontend/pfunc/interface.py:1-165](), [parrot/frontend/pfunc/function.py:34-633]()

## Core Programming Components

### Function Decorators

The programming interface provides two primary decorators for defining LLM functions:

| Decorator | Purpose | Function Type |
|-----------|---------|---------------|
| `@P.semantic_function()` | Define LLM prompt templates with placeholders | `SemanticFunction` |
| `@P.native_function()` | Define Python computation functions | `PyNativeFunction` |

```mermaid
graph LR
    UserFunc["User Function Definition<br/>with decorator"]
    
    SemanticDec["@P.semantic_function()"]
    NativeDec["@P.native_function()"]
    
    SemanticFunc["SemanticFunction<br/>Template parsing"]
    NativeFunc["PyNativeFunction<br/>Code serialization"]
    
    FuncRegistry["Function Registry<br/>_function_registry"]
    
    UserFunc --> SemanticDec
    UserFunc --> NativeDec
    
    SemanticDec --> SemanticFunc
    NativeDec --> NativeFunc
    
    SemanticFunc --> FuncRegistry
    NativeFunc --> FuncRegistry
```

Sources: [parrot/frontend/pfunc/interface.py:38-147](), [parrot/frontend/pfunc/function.py:225-383](), [parrot/frontend/pfunc/function.py:461-633]()

### Parameter Type System

Function parameters are annotated with semantic types that determine their role in the computation graph:

| Parameter Type | Class | Description |
|----------------|-------|-------------|
| `P.Input` | `ParamType.INPUT_LOC` | Input semantic variable locations |
| `P.Output` | `ParamType.OUTPUT_LOC` | Output semantic variable locations |
| Python objects | `ParamType.INPUT_PYOBJ` | Direct Python object parameters |

Sources: [parrot/frontend/pfunc/interface.py:23-36](), [parrot/frontend/pfunc/function_body.py:15-37]()

### SemanticVariable Container

`SemanticVariable` objects serve as content containers that enable data flow dependencies between function calls:

```mermaid
graph TB
    subgraph "SemanticVariable Lifecycle"
        Create["SemanticVariable Creation<br/>P.variable() or function output"]
        Register["Variable Registration<br/>register_semantic_variable_handler()"]
        SetContent["Content Assignment<br/>set_semantic_variable_handler()"]
        GetContent["Content Retrieval<br/>get_semantic_variable_handler()"]
    end
    
    subgraph "VM Integration"
        VMHandler["VirtualMachine<br/>_virtual_machine_env"]
        SessionMgmt["Session Management<br/>session_id + session_auth"]
        HTTPClient["HTTP API Client<br/>core_http_addr"]
    end
    
    Create --> Register
    Register --> SetContent
    SetContent --> GetContent
    
    Register --> VMHandler
    SetContent --> VMHandler  
    GetContent --> VMHandler
    
    VMHandler --> SessionMgmt
    VMHandler --> HTTPClient
    
    style Create fill:#ccffcc
    style VMHandler fill:#ffcc99
```

Sources: [parrot/frontend/pfunc/semantic_variable.py:1-200](), [parrot/frontend/pfunc/vm.py:85-169]()

## VirtualMachine Session Management

The `VirtualMachine` class provides the runtime environment for executing semantic programs by managing sessions and coordinating with ServeCore:

### Session Lifecycle

```mermaid
graph LR
    VMInit["VirtualMachine<br/>__init__()"]
    
    SessionReg["register_session()<br/>POST /session"]
    RunScope["running_scope()<br/>Context manager"]
    ProgramExec["Program Execution<br/>Semantic function calls"]
    SessionCleanup["unregister_session()<br/>DELETE /session"]
    
    VMInit --> SessionReg
    SessionReg --> RunScope
    RunScope --> ProgramExec
    ProgramExec --> SessionCleanup
    
    subgraph "Session State"
        SessionID["session_id<br/>NONE_SESSION_ID -> actual ID"]
        SessionAuth["_session_auth<br/>Authentication token"]
        FuncReg["_function_registry<br/>Function storage"]
    end
    
    SessionReg --> SessionID
    SessionReg --> SessionAuth
    RunScope --> FuncReg
```

Sources: [parrot/frontend/pfunc/vm.py:277-308](), [parrot/frontend/pfunc/vm.py:387-456]()

### Function Call Processing

When a semantic function is called, the VirtualMachine processes the request through multiple stages:

```mermaid
graph TB
    subgraph "Function Call Processing"
        FuncCall["Semantic Function Call<br/>tell_me_a_joke(topic='chicken')"]
        CallObj["SemanticCall Creation<br/>BasicCall.__init__()"]
        ReqPayload["Request Payload Generation<br/>to_request_payload()"]
        Submit["Submit to ServeCore<br/>submit_semantic_call_handler()"]
        Response["Parameter Info Response<br/>var_id assignments"]
        VarReturn["SemanticVariable Return<br/>Output variable creation"]
    end
    
    subgraph "VM Handler Methods"
        SubmitHandler["submit_semantic_call_handler()<br/>HTTP POST /semantic_call"]
        RegisterVar["register_semantic_variable_handler()<br/>Variable registration"]
        GetVar["get_semantic_variable_handler()<br/>Content retrieval"]
    end
    
    FuncCall --> CallObj
    CallObj --> ReqPayload
    ReqPayload --> Submit
    Submit --> SubmitHandler
    SubmitHandler --> Response
    Response --> VarReturn
    
    VarReturn --> RegisterVar
    VarReturn --> GetVar
    
    style Submit fill:#ffcc99
    style SubmitHandler fill:#ccccff
```

Sources: [parrot/frontend/pfunc/function.py:301-383](), [parrot/frontend/pfunc/vm.py:183-274]()

## HTTP API Communication

The client interface communicates with ServeCore through RESTful HTTP APIs using structured request/response patterns:

### API Endpoint Mapping

| Client Operation | HTTP Endpoint | VM Handler Method |
|------------------|---------------|-------------------|
| Session registration | `POST /session` | `register_session()` |
| Session removal | `DELETE /session` | `unregister_session()` |
| Semantic function call | `POST /semantic_call` | `submit_semantic_call_handler()` |
| Native function call | `POST /py_native_call` | `submit_py_native_call_handler()` |
| Variable registration | `POST /semantic_var` | `register_semantic_variable_handler()` |
| Variable content get | `GET /semantic_var/{var_id}` | `get_semantic_variable_handler()` |
| Variable content set | `POST /semantic_var/{var_id}` | `set_semantic_variable_handler()` |

Sources: [parrot/frontend/pfunc/vm.py:183-274](), [parrot/protocol/public/apis.py:1-200](), [docs/user_docs/parrot_apis.md:1-259]()

## Basic Usage Pattern

The typical client programming pattern follows this structure:

```python
from parrot import P

# Define semantic functions using decorators
@P.semantic_function()
def function_name(param1: P.Input, param2: P.Output):
    """Template with {{param1}} placeholder: {{param2}}"""

# Create VirtualMachine and run program
vm = VirtualMachine(core_http_addr="http://localhost:9000")
def main():
    result = function_name(topic="example")
    content = result.get()  # Retrieve generated content

# Execute under VM context
vm.run(main)
```

This pattern automatically handles session management, function registration, variable creation, and request submission to the distributed serving system.

Sources: [README.md:14-31](), [parrot/frontend/pfunc/vm.py:420-456](), [docs/user_docs/pfunc.md:16-38]()

---

