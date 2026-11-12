<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/interwhen · page 6 Examples and Benchmarks · fetched 2026-10-26 -->

# Examples and Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/EarlyStopping/README.md](examples/EarlyStopping/README.md)
- [examples/README.md](examples/README.md)
- [examples/TTSwithVerification/README.md](examples/TTSwithVerification/README.md)

</details>



The `interwhen` repository includes a comprehensive suite of examples and benchmark scripts designed to demonstrate the framework's capabilities across different reasoning domains. These examples serve as both evaluation tools for the paper's results and as reference implementations for developers building custom monitors.

The examples are categorized into three main paradigms: **Early Stopping**, **Test-Time Search (TTS) with Step Verification**, and **Formal Code/Spec Verification (Verina)**.

## System-to-Code Mapping

The following diagram maps high-level benchmarking concepts to the specific code entities and scripts used to execute them.

### Benchmark Execution Flow
```mermaid
graph TD
    subgraph "Natural Language Space"
        "User CLI Command" --> "Dataset Loading"
        "Dataset Loading" --> "Prompt Construction"
        "Prompt Construction" --> "Verifier-Guided Inference"
    end

    subgraph "Code Entity Space"
        "User CLI Command" -- "python examples/..." --> [example_scripts]
        [example_scripts] -- "load_dataset()" --> [HuggingFace_Datasets]
        [example_scripts] -- "metaPrompt" --> [Prompt_Templates]
        [example_scripts] -- "stream_completion()" --> [interject.py]
        [interject.py] -- "monitor.verify()" --> [Monitor_Classes]
    end

    [example_scripts]:::code
    [Monitor_Classes]:::code
    [interject.py]:::code

    classDef code font-family:monospace, font-weight:bold;
```
**Sources:** [examples/EarlyStopping/game24_example.py:1-150](), [examples/TTSwithVerification/README.md:1-21](), [README.md:103-120]()

---

## 6.1 Early Stopping Examples
Early stopping examples demonstrate how to reduce inference costs by terminating reasoning traces once the model reaches a stability or confidence threshold. These scripts utilize the `EATMonitor`, `DEERMonitor`, and `K-Stable` variants to inject a `</think>` token and force an answer.

*   **Datasets:** Uses `nlile/24-game` for arithmetic and `microsoft/VISION_LANGUAGE` for Maze/SpatialMap tasks.
*   **Key Scripts:** `game24_example.py`, `maze_example.py`, and `spatialmap_example.py` located in `examples/EarlyStopping/`.
*   **Configuration:** Supports configuring the `earlystop_model` (e.g., a smaller 1.5B model) used for entropy or confidence probing.

For details on configuration and token statistics, see [Early Stopping Examples](#6.1).

**Sources:** [examples/EarlyStopping/README.md:1-159]()

---

## 6.2 Test-Time Search with Verification Examples
These examples showcase active steering of the LLM. Instead of just stopping early, these scripts use domain-specific verifiers to check intermediate reasoning steps (e.g., valid arithmetic moves in Game of 24 or valid grid coordinates in Maze).

*   **Interaction Model:** When a step fails verification, the monitor injects `[VERIFIER FEEDBACK]` into the stream, triggering the LLM's internal correction loop.
*   **Key Scripts:** `game24_stepverifier.py`, `maze_stepverifier.py`, and `spatialmap_stepverifier.py` in `examples/TTSwithVerification/`.
*   **Logic:** Uses `from_prompt` factory methods to automatically initialize verifier state (like Maze grids or Z3 constraints) from the input text.

For details on step extraction and feedback loops, see [Test-Time Search with Verification Examples](#6.2).

**Sources:** [examples/TTSwithVerification/README.md:1-180]()

---

## 6.3 Verina Benchmark Examples
Verina focuses on formal verification tasks using the Lean 4 theorem prover. These examples evaluate the model's ability to generate either executable code or formal specifications that satisfy a set of properties.

*   **Environment:** Requires a Lean 4 "playground" setup to compile and verify generated snippets.
*   **Metrics:** Outputs `verina_results.csv` containing soundness and completeness metrics, along with entropy plots for reasoning traces.
*   **Key Scripts:** `verina_code_example.py` and `verina_spec_example.py`.

For details on Lean sandbox integration and metric interpretation, see [Verina Benchmark Examples](#6.3).

**Sources:** [README.md:120-140]() (Implied by project structure and Verina sections).

---

## Example Directory Structure

The following diagram illustrates how the benchmark results and reasoning traces are organized in the output directory after running the examples.

### Output Artifacts Trace
```mermaid
graph TD
    "Output Root" --> "Task Folder (e.g., game24)"
    "Task Folder (e.g., game24)" --> "Run Timestamp"
    "Run Timestamp" --> "summary.json"
    "Run Timestamp" --> "logs/"
    "logs/" --> "trace_0.txt"
    "logs/" --> "entropy_plots/"
    
    "summary.json" -- "Contains" --> "Accuracy & Token Usage"
    "trace_0.txt" -- "Contains" --> "LLM + [VERIFIER] Interjections"
```
**Sources:** [examples/EarlyStopping/README.md:135-159](), [README.md:71-80]()

## Common CLI Arguments
Most example scripts share a standard set of arguments for consistent benchmarking:

| Argument | Description |
| :--- | :--- |
| `-n`, `--num_examples` | Number of test instances to process. |
| `-m`, `--monitor` | Boolean flag to enable/disable the `Monitor`. |
| `--max_corrections` | Max number of `fix()` attempts allowed per step. |
| `--main_model` | The target LLM (e.g., `Qwen3-30B-Thinking`). |
| `--debug` | Enables verbose logging of the `interjection` loop. |

**Sources:** [examples/EarlyStopping/README.md:150-159](), [examples/TTSwithVerification/README.md:174-180]()

---

