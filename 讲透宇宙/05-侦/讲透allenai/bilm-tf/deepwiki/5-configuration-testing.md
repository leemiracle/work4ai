<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/bilm-tf · page 5 Configuration & Testing · fetched 2026-10-26 -->

# Configuration & Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/fixtures/model/options.json](tests/fixtures/model/options.json)
- [tests/test_data.py](tests/test_data.py)
- [tests/test_model.py](tests/test_model.py)

</details>



This document covers the configuration system and testing framework for the bilm-tf repository. It explains how model hyperparameters are specified, how the system validates correctness through comprehensive testing, and the relationship between configuration files and model behavior.

For detailed model configuration options, see [Model Configuration](#5.1). For comprehensive testing procedures and test suite documentation, see [Testing Framework](#5.2).

## Configuration System

The bilm-tf system uses JSON configuration files to specify model architecture and hyperparameters. The primary configuration mechanism centers around `options.json` files that define the complete model specification.

### Configuration Flow Architecture

```mermaid
graph TD
    OptionsJSON["options.json"] --> BiLM["BidirectionalLanguageModel"]
    WeightsHDF5["lm_weights.hdf5"] --> BiLM
    VocabFile["vocab_test.txt"] --> Batcher["Batcher/TokenBatcher"] 
    Batcher --> BiLM
    BiLM --> LMEmbeddings["lM_embeddings"]
    
    subgraph "Configuration Components"
        LSTMConfig["lstm: {cell_clip, n_layers, proj_clip, projection_dim, dim}"]
        CharCNNConfig["char_cnn: {embedding, filters, n_highway, n_characters, max_characters_per_token, activation}"]
        OptionsJSON --> LSTMConfig
        OptionsJSON --> CharCNNConfig
    end
    
    LSTMConfig --> BiLM
    CharCNNConfig --> BiLM
```

Sources: [tests/fixtures/model/options.json:1-2](), [tests/test_model.py:59-63]()

The configuration system follows a hierarchical structure where the `BidirectionalLanguageModel` class accepts an `options_file` parameter that points to a JSON configuration file containing nested configuration objects for different model components.

### Core Configuration Parameters

| Component | Parameters | Purpose |
|-----------|------------|---------|
| `lstm` | `cell_clip`, `use_skip_connections`, `n_layers`, `proj_clip`, `projection_dim`, `dim` | LSTM architecture and clipping |
| `char_cnn` | `embedding.dim`, `filters`, `n_highway`, `n_characters`, `max_characters_per_token`, `activation` | Character-level CNN processing |

Sources: [tests/fixtures/model/options.json:1-2]()

## Testing Framework

The bilm-tf testing framework provides comprehensive validation of model behavior, data processing, and embedding generation. The test suite is organized around core component validation and uses fixtures to ensure reproducible test conditions.

### Testing Architecture

```mermaid
graph TB
    subgraph "Test Structure"
        TestModel["TestBidirectionalLanguageModel"]
        TestModelToken["TestBidirectionalLanguageModelTokenInput"] 
        TestData["TestVocabulary, TestUnicodeCharsVocabulary, TestBatcher, TestTokenBatcher, TestLMDataset"]
    end
    
    subgraph "Test Fixtures"
        FixturesModel["tests/fixtures/model/"]
        FixturesData["tests/fixtures/data/"]
        FixturesTrain["tests/fixtures/train/"]
        
        OptionsJSON["options.json"] 
        WeightsHDF5["lm_weights.hdf5"]
        VocabTest["vocab_test.txt"]
        LMEmbeddings["lm_embeddings_*.hdf5"]
        SentencesJSON["lm_embeddings_sentences.json"]
    end
    
    TestModel --> FixturesModel
    TestModelToken --> FixturesModel
    TestData --> FixturesData
    TestData --> FixturesTrain
    
    FixturesModel --> OptionsJSON
    FixturesModel --> WeightsHDF5  
    FixturesModel --> LMEmbeddings
    FixturesModel --> SentencesJSON
    FixturesData --> VocabTest
```

Sources: [tests/test_model.py:15](), [tests/test_data.py:10-11]()

### Component Testing Coverage

The testing framework validates the following core components:

#### Model Testing
- **Character Input Path**: Tests `BidirectionalLanguageModel` with character-level inputs via `Batcher`
- **Token Input Path**: Tests `BidirectionalLanguageModel` with pre-computed token embeddings via `TokenBatcher`  
- **Embedding Validation**: Compares generated embeddings against expected fixtures with tolerance `atol=1.0e-6`
- **State Management**: Validates LSTM state updates and batch size handling

Sources: [tests/test_model.py:51-101](), [tests/test_model.py:143-220]()

#### Data Processing Testing
- **Vocabulary Management**: Tests `Vocabulary` and `UnicodeCharsVocabulary` encoding and decoding
- **Batching Logic**: Validates `Batcher` and `TokenBatcher` sentence batching with proper padding
- **Dataset Iteration**: Tests `LMDataset` and `BidirectionalLMDataset` batch generation

Sources: [tests/test_data.py:14-38](), [tests/test_data.py:101-187](), [tests/test_data.py:202-364]()

### Test Execution Patterns

```mermaid
sequenceDiagram
    participant TestRunner
    participant TestCase
    participant TensorFlowSession
    participant Fixtures
    
    TestRunner->>TestCase: "setUp()"
    TestCase->>TensorFlowSession: "tf.Session()"
    TestCase->>Fixtures: "Load test data"
    
    TestRunner->>TestCase: "test_method()"
    TestCase->>TensorFlowSession: "Run operations"
    TestCase->>TestCase: "Assert results"
    
    TestRunner->>TestCase: "tearDown()"
    TestCase->>TensorFlowSession: "tf.reset_default_graph()"
    TestCase->>TensorFlowSession: "session.close()"
```

Sources: [tests/test_model.py:44-49](), [tests/test_model.py:134-141]()

The testing framework follows a consistent pattern where each test class manages TensorFlow session lifecycle, loads appropriate fixtures, executes model operations, and validates results against expected outputs. This ensures isolation between tests and reproducible validation of system behavior.

### Testing Data Flow

Testing Data Flow Architecture shows how test data flows through the validation process:

```mermaid
graph LR
    subgraph "Input Fixtures"
        SentencesJSON["lm_embeddings_sentences.json"]
        ExpectedEmbeds["lm_embeddings_*.hdf5"]
        VocabFile["vocab_test.txt"]
    end
    
    subgraph "Test Execution"
        LoadSentences["_load_sentences_embeddings()"]
        BatcherTest["Batcher.batch_sentences()"]
        ModelRun["BidirectionalLanguageModel()"]
        EmbedValidation["np.allclose() validation"]
    end
    
    SentencesJSON --> LoadSentences
    ExpectedEmbeds --> LoadSentences
    VocabFile --> BatcherTest
    LoadSentences --> BatcherTest
    BatcherTest --> ModelRun
    ModelRun --> EmbedValidation
    LoadSentences --> EmbedValidation
```

Sources: [tests/test_model.py:18-40](), [tests/test_model.py:74-100]()

## Configuration-Testing Integration

The configuration and testing systems are tightly integrated, with test fixtures providing canonical examples of valid configuration files and expected model behavior. This integration ensures that configuration changes are automatically validated through the comprehensive test suite.

The `TestBidirectionalLanguageModel` class specifically validates that models instantiated with fixture configurations produce expected embeddings, creating a direct validation path from configuration to model behavior.

Sources: [tests/test_model.py:59-60](), [tests/fixtures/model/options.json:1-2]()

---

