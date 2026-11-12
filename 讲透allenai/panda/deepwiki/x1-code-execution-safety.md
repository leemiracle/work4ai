<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/panda · extra page Code Execution & Safety · fetched 2026-11-09 -->

# Code Execution & Safety

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [panda/panda_agent/panda_agent.py](panda/panda_agent/panda_agent.py)
- [panda/utils/pyparser.py](panda/utils/pyparser.py)

</details>



This section covers the core mechanics of executing generated code within the Panda autonomous research agent. It details how code blocks are parsed, vetted against safety constraints and blocklists, checked for forbidden interactive user inputs, scoped within execution namespaces, and constrained by time limits.

---

## 1. Code Parsing and Extraction

Generated responses from Large Language Models often contain markdown code blocks or raw script sections. Panda uses an Abstract Syntax Tree (AST)-based parser to extract and segment executable code blocks cleanly before evaluation.

The primary parsing function is `parse_code(x)`, located in `panda/utils/pyparser.py`. It reads a string `x`, parses it into an AST module using `ast.parse(x)`, and traverses top-level statements to isolate discrete blocks based on starting and ending line numbers.

```mermaid
graph TD
    A["RawLLMOutput"] --> B["parse_code"]
    B --> C["ast.parse"]
    C --> D["ModuleBodyIteration"]
    D --> E["ASTNodeLinesExtraction"]
    E --> F["ExecutableCodeBlocks"]

    subgraph "Code Entity Space"
    B["panda/utils/pyparser.py:parse_code"]
    C["ast.parse"]
    D["module.body"]
    E["get_end_lineno"]
    end
```
*Diagram: Natural language execution payload parsing flow mapping to code entities.*

**Sources:** `[panda/utils/pyparser.py:16-32]()`

---

## 2. Dangerous Pattern Blocklist

To prevent the agent from executing destructive, recursive, or resource-exhausting filesystem operations (such as infinite zipping or directory duplication loops), Panda evaluates code against a set of regex-based `dangerous_patterns`.

The blocklist explicitly prohibits:
- `shutil.make_archive`: Prevents recursive self-archiving loops common in certain LLM outputs.
- `zipfile.ZipFile`: Prevents manual archive generation that can inflate file system storage.
- `tarfile.open`: Prevents tar/gzip bundle creation.

```python
dangerous_patterns = [
    r"shutil\.make_archive",
    r"zipfile.ZipFile",
    r"tarfile\.open",
]
```

```mermaid
graph TD
    A["ExtractedCodeBlock"] --> B["PatternMatching"]
    B --> C{"Matches dangerous_patterns?"}
    C -- Yes --> D["ExecutionBlockedError"]
    C -- No --> E["ProceedToSafetyChecks"]

    subgraph "Code Entity Space"
    B["re.search"]
    C["panda/panda_agent/panda_agent.py:dangerous_patterns"]
    end
```
*Diagram: Safety verification flow checking dangerous patterns.*

**Sources:** `[panda/panda_agent/panda_agent.py:98-103]()`

---

## 3. User-Input Detection

Because Panda runs as a fully autonomous agent, any code that attempts to halt execution and wait for user prompts (`input()`, `getpass()`, or `sys.stdin.read()`) will cause the execution thread to hang. Panda detects and intercepts these patterns statically prior to running the code.

The check is implemented via `code_asks_for_user_input(code)` and the `InputDetector` visitor class in `panda/utils/pyparser.py`.

```mermaid
graph TD
    A["CodeString"] --> B["code_asks_for_user_input"]
    B --> C["ast.parse"]
    C --> D["InputDetector"]
    D --> E{"Visits AST Nodes"}
    E --> F["Detects input / raw_input"]
    E --> G["Detects getpass calls"]
    E --> H["Detects sys.stdin reads"]
    F --> I["Return True"]
    G --> I
    H --> I
    E --> J["No Input Found -> Return False"]

    subgraph "Code Entity Space"
    B["panda/utils/pyparser.py:code_asks_for_user_input"]
    C["ast.parse"]
    D["panda/utils/pyparser.py:InputDetector"]
    E["ast.NodeVisitor"]
    end
```
*Diagram: Static analysis data flow for user-input detection.*

`InputDetector` tracks:
- Module aliases (e.g., `import sys as s`, `import getpass`)
- Function names imported from `getpass`
- File handles defined by `open(...)` or `with open(...)` to ensure legitimate file reads are not flagged as `sys.stdin` reads.

**Sources:** `[panda/utils/pyparser.py:40-162]()`

---

## 4. Execution Namespace and State

Code execution takes place within a shared execution `State` object that persists variables and dataframes across iteration steps. The `State` class is defined in `panda/panda_agent/panda_agent.py`.

```python
class State:
    def __init__(self, iteration=0, observations="", namespace=None):
        self.iteration = iteration
        self.observations = observations
        self.namespace = namespace or {}
```

The `namespace` dictionary acts as the globals/locals scope passed directly into Python's built-in `exec()` function during action execution. This allows variables created in step $N$ (such as pandas DataFrames or trained models) to be accessed natively in step $N+1$.

```mermaid
graph TD
    A["AgentLoopStep"] --> B["StateNamespace"]
    B --> C["ExecEnvironment"]
    C --> D["PythonExec"]
    D --> E["UpdatedNamespaceVariables"]

    subgraph "Code Entity Space"
    A["panda_step"]
    B["panda/panda_agent/panda_agent.py:State"]
    C["namespace"]
    D["exec"]
    end
```
*Diagram: State variable propagation through execution cycles.*

**Sources:** `[panda/panda_agent/panda_agent.py:150-155]()`

---

## 5. Timeouts and Guardrails

To prevent infinite loops or long-hanging external library calls during action execution, Panda wraps code execution in timeout guards using `func_timeout`.

If a generated action block exceeds its allotted execution window, a `FunctionTimedOut` exception is raised, caught by the agent loop, and fed back to the LLM as an observation error so it can self-debug or adjust its approach in subsequent iterations.

**Sources:** `[panda/panda_agent/panda_agent.py:47]()`, `[panda/panda_agent/panda_agent.py:116-122]()`

---

