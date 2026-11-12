<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/garak · extra page Package Hallucination Probes · fetched 2026-10-26 -->

# Package Hallucination Probes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [garak/detectors/packagehallucination.py](garak/detectors/packagehallucination.py)
- [garak/probes/packagehallucination.py](garak/probes/packagehallucination.py)
- [tests/detectors/test_detectors_packagehallucination.py](tests/detectors/test_detectors_packagehallucination.py)
- [tests/probes/test_probes_packagehallucination.py](tests/probes/test_probes_packagehallucination.py)
- [tools/packagehallucination/dart/create_dataset.py](tools/packagehallucination/dart/create_dataset.py)
- [tools/packagehallucination/javascript/main.py](tools/packagehallucination/javascript/main.py)
- [tools/packagehallucination/perl/create_dataset.py](tools/packagehallucination/perl/create_dataset.py)
- [tools/packagehallucination/python/main.py](tools/packagehallucination/python/main.py)
- [tools/packagehallucination/raku/create_dataset.py](tools/packagehallucination/raku/create_dataset.py)
- [tools/packagehallucination/ruby/main.py](tools/packagehallucination/ruby/main.py)

</details>



The package hallucination system in `garak` is designed to detect LLM supply-chain risks where a model recommends importing non-existent programming packages. Attackers can identify these "hallucinated" names and register them on public repositories (e.g., PyPI, npm), leading to code that silently executes malicious dependencies [garak/probes/packagehallucination.py:63-70]().

This system covers multiple ecosystems: Python, JavaScript, Rust, Ruby, Raku, Perl, and Dart [garak/detectors/packagehallucination.py:141-300]().

## System Architecture

The package hallucination detection pipeline follows a standard probe-detector flow but relies on external datasets of valid packages to verify model outputs.

### Natural Language to Code Entity Mapping

The following diagram illustrates how natural language tasks are transformed into code-specific probes and then validated against language-specific package registries.

**Diagram: Package Hallucination Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["stub_prompts"] --> B["code_tasks"]
        B --> C["PackageHallucinationProbe"]
    end

    subgraph "Code Entity Space"
        C --> D["Python (Probe)"]
        C --> E["JavaScript (Probe)"]
        
        D -- "primary_detector" --> F["PythonPypi (Detector)"]
        E -- "primary_detector" --> G["JavaScriptNpm (Detector)"]
        
        F -- "validates against" --> H[("PyPI Dataset")]
        G -- "validates against" --> I[("npm Dataset")]
        
        F -- "extracts" --> J["re.findall('import ...')"]
        G -- "extracts" --> K["re.findall('from ...')"]
    end
```
Sources: [garak/probes/packagehallucination.py:20-60](), [garak/probes/packagehallucination.py:105-152](), [garak/detectors/packagehallucination.py:141-211]()

## Probes

Probes in this module generate prompts that ask the LLM to perform specific coding tasks using a target language. The tasks are split into `real_code_tasks` (legitimate libraries) and `unreal_code_tasks` (fictional systems like "HAL 9000" or "StombergDB") to provoke hallucination [garak/probes/packagehallucination.py:32-60]().

### Key Probe Classes
| Class | Language | Target Repository | Primary Detector |
| :--- | :--- | :--- | :--- |
| `Python` | Python3 | PyPI | `packagehallucination.PythonPypi` |
| `JavaScript` | JavaScript | npm | `packagehallucination.JavaScriptNpm` |
| `Rust` | Rust | crates.io | `packagehallucination.RustCrates` |
| `Ruby` | Ruby | RubyGems | `packagehallucination.RubyGems` |
| `RakuLand` | Raku | raku.land | `packagehallucination.RakuLand` |

Sources: [garak/probes/packagehallucination.py:105-185]()

## Detectors

Detectors evaluate the model's response by extracting package names and checking them against a known-good list. 

### Implementation Logic
1.  **Extraction**: Each subclass implements `_extract_package_references` using regular expressions tailored to the language's syntax (e.g., `import` in Python, `require` in Ruby) [garak/detectors/packagehallucination.py:51-53]().
2.  **Dataset Loading**: The `_load_package_list` method fetches package datasets from Hugging Face (e.g., `garak-llm/pypi-20241031`) [garak/detectors/packagehallucination.py:55-61]().
3.  **Cutoff Filtering**: If a `cutoff_date` is provided, packages first seen after that date are excluded from the "valid" list to simulate the model's knowledge cutoff [garak/detectors/packagehallucination.py:64-81]().
4.  **Comparison**: The `detect` method compares extracted names against the loaded set. If a name is missing, it is flagged as a hallucination (score `1.0`) [garak/detectors/packagehallucination.py:126-136]().

**Diagram: Detector Inheritance and Data Flow**
```mermaid
classDiagram
    class Detector {
        <<interface>>
        +detect(attempt)
    }
    class PackageHallucinationDetector {
        <<abstract>>
        +cutoff_date
        +packages: Set
        +detect(attempt)
        #_load_package_list()
        #_extract_package_references(output)*
    }
    class PythonPypi {
        +language_name: "python"
        +dataset_name: "garak-llm/pypi-20241031"
        #_extract_package_references(output)
    }
    class RubyGems {
        +language_name: "ruby"
        +dataset_name: "garak-llm/rubygems-20241031"
        #_extract_package_references(output)
    }

    Detector <|-- PackageHallucinationDetector
    PackageHallucinationDetector <|-- PythonPypi
    PackageHallucinationDetector <|-- RubyGems
```
Sources: [garak/detectors/packagehallucination.py:33-173]()

## Ecosystem Specifics

### Python (`PythonPypi`)
*   **Extraction**: Uses regex to find `import <pkg>` and `from <pkg> import` patterns [garak/detectors/packagehallucination.py:158-165]().
*   **Validation**: Combines the PyPI dataset with `sys.stdlib_module_names` to ensure standard library modules are not flagged [garak/detectors/packagehallucination.py:152-156]().

### JavaScript (`JavaScriptNpm`)
*   **Extraction**: Matches `import` statements, `require()` calls, and `from 'npm:<pkg>'` syntax [garak/detectors/packagehallucination.py:213-233]().

### Ruby (`RubyGems`)
*   **Extraction**: Matches `require '<gem>'`, `require_relative`, and `gem '<gem>'` [garak/detectors/packagehallucination.py:187-200]().

## Dataset Generation Tools

The repository includes tools for refreshing the package lists used by detectors. These scripts scrape official registries or use APIs to generate JSONL files compatible with Hugging Face Datasets.

*   **Raku**: Scrapes `raku.land` using `BeautifulSoup` [tools/packagehallucination/raku/create_dataset.py:6-33]().
*   **Perl**: Queries the MetaCPAN API [tools/packagehallucination/perl/create_dataset.py:12-18]().
*   **Dart**: Uses the `pub.dev` API [tools/packagehallucination/dart/create_dataset.py:9-30]().
*   **Python/JS/Ruby**: Use batch processing with `ThreadPoolExecutor` and `backoff` to handle rate limits while fetching package creation dates [tools/packagehallucination/python/main.py:67-73](), [tools/packagehallucination/javascript/main.py:62-66]().

Sources: [tools/packagehallucination/raku/create_dataset.py:1-43](), [tools/packagehallucination/perl/create_dataset.py:1-61](), [tools/packagehallucination/dart/create_dataset.py:1-47](), [tools/packagehallucination/python/main.py:1-106]()

---

