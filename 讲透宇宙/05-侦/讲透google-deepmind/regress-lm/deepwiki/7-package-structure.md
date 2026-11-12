<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/regress-lm · page 7 Package Structure · fetched 2026-10-26 -->

# Package Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [regress_lm/__init__.py](regress_lm/__init__.py)
- [regress_lm/models/__init__.py](regress_lm/models/__init__.py)

</details>



This document covers the internal organization of the `regress_lm` Python package, including its subpackage hierarchy, initialization patterns, and import structure. For detailed information about the core data structures and concepts, see [Core Concepts](#4). For specific model implementation details, see [Model System](#5).

## Package Organization

The `regress_lm` package follows a layered architecture with clear separation between abstractions, implementations, and data processing components. The package structure reflects the system's modular design where abstract interfaces are defined at higher levels and concrete implementations are organized in specialized subpackages.

### Top-Level Package Layout

```mermaid
graph TD
    subgraph "regress_lm/"
        Init["__init__.py<br/>Package version: 0.0.1.alpha"]
        RLM["rlm.py<br/>RegressLM main API"]
        Core["core.py<br/>Example & ExampleInput"]
        Inference["inference.py<br/>InferenceFn protocol"]
    end
    
    subgraph "regress_lm/models/"
        ModelsInit["__init__.py<br/>Model imports"]
        Base["base.py<br/>Model & FineTuner abstractions"]
    end
    
    subgraph "regress_lm/models/pytorch/"
        PyModel["model.py<br/>PyTorchModel & PyTorchFineTuner"]
        PyArch["architecture.py<br/>EncoderDecoder"]
    end
    
    subgraph "regress_lm/vocabs/"
        VocabsInit["__init__.py"]
        EncoderVocab["encoder_vocab.py<br/>Text tokenization"]
        DecoderVocab["decoder_vocab.py<br/>Numerical tokenization"]
    end
    
    subgraph "regress_lm/tokenizers/"
        TokenizersInit["__init__.py"]
        Tokenizers["tokenizers.py<br/>P10 & IEEE tokenizers"]
    end
    
    Init --> RLM
    Init --> Core
    ModelsInit --> Base
    ModelsInit --> PyModel
    PyModel --> PyArch
    VocabsInit --> EncoderVocab
    VocabsInit --> DecoderVocab
    DecoderVocab --> TokenizersInit
    TokenizersInit --> Tokenizers
```

Sources: [regress_lm/__init__.py:1-18]()

### Package Initialization

The main package initialization is minimal, focusing only on version information. The `regress_lm` package defines its version as `"0.0.1.alpha"`, indicating it is in early development stage.

```mermaid
graph LR
    subgraph "Package Initialization Flow"
        MainInit["regress_lm/__init__.py<br/>__version__ = '0.0.1.alpha'"]
        ModelsInit["models/__init__.py<br/>Import Model & PyTorchModel"]
        PyTorchCheck["Try/except PyTorchModel import<br/>Log error if PyTorch unavailable"]
    end
    
    MainInit --> ModelsInit
    ModelsInit --> PyTorchCheck
```

Sources: [regress_lm/__init__.py:17](), [regress_lm/models/__init__.py:15-26]()

## Import Structure and Dependencies

The package uses a hierarchical import structure with conditional imports for optional dependencies. This design allows the package to gracefully handle missing dependencies while maintaining clean public APIs.

### Models Package Import Pattern

The `models` subpackage demonstrates the package's approach to handling optional dependencies:

| Import | Status | Error Handling |
|--------|--------|----------------|
| `Model` from `base.py` | Always imported | Required base class |
| `PyTorchModel` from `pytorch.model` | Conditional | Logs error if PyTorch unavailable |

The models package uses a try-except pattern to handle PyTorch availability:

```python
try:
  from regress_lm.models.pytorch.model import PyTorchModel
except ImportError:
  logging.error('Cannot import PyTorchModel.')
```

Sources: [regress_lm/models/__init__.py:22-25]()

### Dependency Management Strategy

```mermaid
graph TD
    subgraph "Core Dependencies"
        AbslLogging["absl.logging<br/>Error reporting"]
        BaseClasses["base.py<br/>Model & FineTuner protocols"]
    end
    
    subgraph "Optional Dependencies"
        PyTorch["PyTorch Framework<br/>Neural network implementation"]
        TorchText["TorchText<br/>Vocabulary management"]
        SentencePiece["SentencePiece<br/>Subword tokenization"]
    end
    
    subgraph "Import Handling"
        ConditionalImport["try/except ImportError<br/>Graceful degradation"]
        ErrorLogging["logging.error()<br/>Inform user of missing deps"]
    end
    
    BaseClasses --> AbslLogging
    PyTorch --> ConditionalImport
    TorchText --> ConditionalImport
    SentencePiece --> ConditionalImport
    ConditionalImport --> ErrorLogging
```

Sources: [regress_lm/models/__init__.py:18](), [regress_lm/models/__init__.py:24-25]()

## Subpackage Architecture

The package structure reflects the system's layered architecture with clear separation of concerns:

### Core Layer
- **`core.py`**: Defines `Example` and `ExampleInput` data structures
- **`inference.py`**: Defines `InferenceFn` protocol for type safety
- **`rlm.py`**: Contains the main `RegressLM` user-facing API class

### Model Layer
- **`models/base.py`**: Abstract `Model` and `FineTuner` interfaces
- **`models/pytorch/`**: Concrete PyTorch implementations
  - `model.py`: `PyTorchModel` and `PyTorchFineTuner` classes
  - `architecture.py`: `EncoderDecoder` neural architecture

### Data Processing Layer
- **`vocabs/`**: Vocabulary management for text and numerical data
  - `encoder_vocab.py`: Text tokenization vocabularies
  - `decoder_vocab.py`: Numerical tokenization vocabularies
- **`tokenizers/`**: Specialized numerical tokenizers
  - `tokenizers.py`: `P10Tokenizer` and `IEEEFloatTokenizer` classes

### Package Hierarchy Relationships

```mermaid
graph TB
    subgraph "Abstraction Level: High"
        RegressLMAPI["rlm.RegressLM<br/>Main user interface"]
        CoreTypes["core.Example & ExampleInput<br/>Data structures"]
    end
    
    subgraph "Abstraction Level: Medium"
        ModelBase["models.base.Model<br/>Abstract model interface"]
        FineTunerBase["models.base.FineTuner<br/>Abstract fine-tuning interface"]
    end
    
    subgraph "Abstraction Level: Low"
        PyTorchImpl["models.pytorch.PyTorchModel<br/>Concrete implementation"]
        Architecture["models.pytorch.EncoderDecoder<br/>Neural architecture"]
        Vocabularies["vocabs.EncoderVocab & DecoderVocab<br/>Tokenization"]
        Tokenizers["tokenizers.P10Tokenizer & IEEEFloatTokenizer<br/>Numerical encoding"]
    end
    
    RegressLMAPI --> ModelBase
    RegressLMAPI --> CoreTypes
    ModelBase --> PyTorchImpl
    FineTunerBase --> PyTorchImpl
    PyTorchImpl --> Architecture
    PyTorchImpl --> Vocabularies
    Vocabularies --> Tokenizers
```

Sources: [regress_lm/models/__init__.py:19](), [regress_lm/models/__init__.py:23]()

---

