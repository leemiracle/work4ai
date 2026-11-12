> 来源: [https://deepwiki.com/sgl-project/sglang/23-sglang-frontend-language](https://deepwiki.com/sgl-project/sglang/23-sglang-frontend-language)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# SGLang Frontend Language

  Relevant source files 
 - [.claude/skills/add-jit-kernel/SKILL.md](https://github.com/sgl-project/sglang/blob/94183a8d/.claude/skills/add-jit-kernel/SKILL.md?plain=1)
 - [.claude/skills/add-sgl-kernel/SKILL.md](https://github.com/sgl-project/sglang/blob/94183a8d/.claude/skills/add-sgl-kernel/SKILL.md?plain=1)
 - [.claude/skills/generate-profile/SKILL.md](https://github.com/sgl-project/sglang/blob/94183a8d/.claude/skills/generate-profile/SKILL.md?plain=1)
 - [.claude/skills/llm-torch-profiler-analysis/references/heuristics.md](https://github.com/sgl-project/sglang/blob/94183a8d/.claude/skills/llm-torch-profiler-analysis/references/heuristics.md?plain=1)
 - [.claude/skills/llm-torch-profiler-analysis/references/source-map.md](https://github.com/sgl-project/sglang/blob/94183a8d/.claude/skills/llm-torch-profiler-analysis/references/source-map.md?plain=1)
 - [python/sglang/compile_deep_gemm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/compile_deep_gemm.py)
 - [python/sglang/lang/backend/runtime_endpoint.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py)
 - [python/sglang/multimodal_gen/runtime/layers/activation.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/multimodal_gen/runtime/layers/activation.py)
 - [python/sglang/srt/layers/activation.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/activation.py)
 - [python/sglang/srt/layers/moe/cutlass_moe.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/cutlass_moe.py)
 - [python/sglang/srt/layers/moe/cutlass_w4a8_moe.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/cutlass_w4a8_moe.py)
 - [python/sglang/srt/layers/moe/token_dispatcher/deepep.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/token_dispatcher/deepep.py)
 - [python/sglang/srt/layers/quantization/w4afp8.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/quantization/w4afp8.py)
 - [test/registered/unit/layers/moe/test_w4afp8_deepep_dtype.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/layers/moe/test_w4afp8_deepep_dtype.py)
 - [test/registered/unit/layers/moe/test_w4afp8_deepep_post_reorder.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/layers/moe/test_w4afp8_deepep_post_reorder.py)
 
  The SGLang Frontend Language is a domain-specific language (DSL) designed to simplify the composition of complex LLM programs. It allows developers to express multi-turn dialogues, structured output constraints, and parallel generation patterns using a native Pythonic interface. By treating LLM interactions as program execution, SGLang enables optimizations like prefix caching and speculative execution that are difficult to achieve with standard chat APIs.

 
### Core Concept: Programmatic Prompting

 In SGLang, a "program" is defined using the `@function` decorator, which creates an instance of `SglFunction` [python/sglang/lang/ir.py141](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/ir.py#L141-L141) These functions take a state object `s` (a `ProgramState`) as their first argument, which tracks the prompt history and generated variables [python/sglang/lang/interpreter.py80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/interpreter.py#L80-L80)

 
```

```

 
### Relationship Between Frontend and Backend

 The frontend language acts as a high-level interface that compiles user-defined functions into an Intermediate Representation (IR) defined in `python/sglang/lang/ir.py`. This IR is then executed by an interpreter (`StreamExecutor`) that communicates with a backend, such as the `RuntimeEndpoint` [python/sglang/lang/backend/runtime_endpoint.py26](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L26-L26)

 The frontend primitives map directly to the backend's generation capabilities. For instance, when a user specifies a `dtype` constraint in the frontend, the `RuntimeEndpoint` converts it to a regex pattern for the server [python/sglang/lang/backend/runtime_endpoint.py127-157](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L127-L157)

 **Bridging Natural Language to Code Entities** The following table and diagram illustrate how high-level frontend constructs map to the underlying execution entities in the codebase.

 
| Frontend Concept | Code Entity | Purpose |
|---|---|---|
| Program Definition | SglFunction | Encapsulates the decorated Python function and its arguments python/sglang/lang/ir.py141 |
| Execution State | ProgramState | Manages the current text, history, and variables during execution python/sglang/lang/interpreter.py80 |
| Backend Link | BaseBackend | Abstract class for different execution targets (SRT, OpenAI, etc.) python/sglang/lang/backend/runtime_endpoint.py26 |
| Generation Primitives | SglSamplingParams | Dataclass representing specific LLM operations and sampling parameters python/sglang/lang/ir.py21 |
| Template Management | ChatTemplate | Handles role-based prefix/suffix injection for specific models python/sglang/lang/chat_template.py12 |

 **System Architecture Overview** The diagram below shows the flow from a Python function definition to server-side execution, bridging the user's "Natural Language Space" (prompts) to the "Code Entity Space".

 Title: "SGLang Frontend Execution Architecture"

 
```

```

 Sources: [python/sglang/lang/ir.py141-152](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/ir.py#L141-L152) [python/sglang/lang/interpreter.py71-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/interpreter.py#L71-L80) [python/sglang/lang/backend/runtime_endpoint.py159-196](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L159-L196) [python/sglang/srt/managers/tokenizer_manager.py96](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L96-L96)

 
### Language Primitives

 SGLang provides several primitives to control the generation process:

 
 - **`gen`**: The primary generation primitive (`SglGen`). It supports `max_new_tokens`, `stop` sequences, and structured constraints [python/sglang/lang/ir.py21](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/ir.py#L21-L21)
 - **`select`**: Forces the model to choose from a predefined list of options (`SglSelect`).
 - **`fork`**: Creates copies of the current state for parallel exploration.
 - **Role Wrappers**: `system`, `user`, and `assistant` help manage `ChatTemplate` mapping automatically.
 - **Multimodal Primitives**: `image` and `video` primitives allow embedding visual data. These are handled by the `RuntimeEndpoint` which adds them to the request data [python/sglang/lang/backend/runtime_endpoint.py184](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L184-L184)
 
 
### Structured and Constrained Output

 SGLang produces structured data by leveraging the underlying runtime's ability to constrain sampling.

 
 - **Regex Constraints**: Enforce strict formatting using regex patterns [python/sglang/lang/ir.py17-20](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/ir.py#L17-L20)
 - **DType Constraints**: The frontend handles type-to-regex conversion for standard types (int, float, bool, str) in `RuntimeEndpoint._handle_dtype_to_regex` [python/sglang/lang/backend/runtime_endpoint.py127-157](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L127-L157)
 - **Sampling Parameters**: Parameters like `temperature`, `top_p`, and `presence_penalty` are encapsulated in `SglSamplingParams` [python/sglang/lang/ir.py21](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/ir.py#L21-L21)
 
 
### Backend Integrations

 The frontend language is backend-agnostic. It can target:

 
 - **SRT (SGLang Runtime)**: The native high-performance serving engine accessed via `RuntimeEndpoint` [python/sglang/lang/backend/runtime_endpoint.py26](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L26-L26)
 - **API Providers**: Support for OpenAI-compatible endpoints via the OpenAI backend integration.
 
 
### Program Execution Flow

 The diagram below maps the internal classes involved in moving from a user request to a backend call.

 Title: "Frontend Program Lifecycle to SRT Backend"

 
```

```

 Sources: [python/sglang/lang/ir.py160-183](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/ir.py#L160-L183) [python/sglang/lang/interpreter.py71-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/interpreter.py#L71-L80) [python/sglang/srt/managers/tokenizer_manager.py26](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py#L26-L26) [python/sglang/lang/backend/runtime_endpoint.py165-172](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L165-L172)

 
### Child Pages

 For more technical details on how these components work under the hood, refer to the following sub-pages:

 
 - **[Language IR and Interpreter](https://deepwiki.com/sgl-project/sglang/23.1-language-ir-and-interpreter)**: Deep dive into the IR primitives (`gen`, `select`, `fork`), the `StreamExecutor` logic, and program composition.
 - **[Backend Integrations for Frontend Language](https://deepwiki.com/sgl-project/sglang/23.2-backend-integrations-for-frontend-language)**: Details on how `RuntimeEndpoint` and OpenAI backends map frontend programs to server calls and handle chat templates [python/sglang/lang/backend/runtime_endpoint.py26-55](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L26-L55)
 
 Sources: [python/sglang/lang/ir.py1-41](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/ir.py#L1-L41) [python/sglang/lang/interpreter.py1-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/interpreter.py#L1-L80) [python/sglang/lang/backend/runtime_endpoint.py1-196](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/lang/backend/runtime_endpoint.py#L1-L196)
