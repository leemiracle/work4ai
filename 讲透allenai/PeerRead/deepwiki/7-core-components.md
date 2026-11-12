<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/PeerRead · page 7 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [code/__init__.py](code/__init__.py)
- [code/models/__init__.py](code/models/__init__.py)

</details>



## Purpose and Scope

This document provides an overview of the shared infrastructure components used across both the Acceptance Classification and Aspect Prediction pipelines in the PeerRead repository. These components include data models, text processing utilities, embedding management, and helper functions that enable consistent data handling throughout the system.

For detailed documentation of specific components:
- Data structure specifications: see [Data Models](#7.1)
- Utility function implementations: see [Data Helper Utilities](#7.2)

The components documented here form the foundation that both pipelines build upon, ensuring consistent data representation and processing across different modeling approaches.

---

## Component Architecture Overview

The PeerRead system is built on three layers of shared components: data models that represent core entities, text processing utilities that transform raw text into model inputs, and helper functions that manage data flow during training and evaluation.

### High-Level Component Relationships

```mermaid
graph TB
    subgraph "Data Layer"
        Paper["Paper Model<br/>(paper metadata)"]
        Review["Review Model<br/>(review text + scores)"]
        ScienceParse["ScienceParse Model<br/>(parsed PDF structure)"]
    end
    
    subgraph "Text Processing"
        Tokenizer["Tokenization<br/>(sentence splitting, word tokens)"]
        VocabBuilder["Vocabulary Builder<br/>(word -> index mapping)"]
        Padding["Sequence Padding<br/>(fixed-length sequences)"]
    end
    
    subgraph "Embedding Layer"
        Word2VecUtils["sent2vec.py<br/>MeanEmbeddingVectorizer<br/>TFIDFEmbeddingVectorizer"]
        VectorizerCache["Vectorizer Persistence<br/>(pickle serialization)"]
    end
    
    subgraph "Batch Processing"
        BatchIterator["data_helper.batch_iter<br/>(mini-batch generation)"]
        DataLoader["Data Loading<br/>(JSON/TSV parsing)"]
    end
    
    subgraph "Consumers"
        AcceptPipeline["Acceptance Classification<br/>featurize.py<br/>classify.py"]
        AspectPipeline["Aspect Prediction<br/>predict.py<br/>pred_models.py"]
    end
    
    Paper --> AcceptPipeline
    Review --> AcceptPipeline
    ScienceParse --> AcceptPipeline
    
    Paper --> AspectPipeline
    Review --> AspectPipeline
    
    Tokenizer --> VocabBuilder
    VocabBuilder --> Padding
    
    Tokenizer --> AcceptPipeline
    VocabBuilder --> AcceptPipeline
    Padding --> AspectPipeline
    
    Word2VecUtils --> AcceptPipeline
    Word2VecUtils --> VectorizerCache
    VectorizerCache --> AcceptPipeline
    
    BatchIterator --> AspectPipeline
    DataLoader --> AcceptPipeline
    DataLoader --> AspectPipeline
```

**Sources:** Diagrams 1, 3, 4 from architecture overview

---

## Data Models

The system defines three primary data structures that represent the core entities in the PeerRead dataset. These models provide a consistent interface for accessing paper and review information across both pipelines.

### Model Responsibilities

| Model | Primary Responsibility | Key Attributes | Used By |
|-------|----------------------|----------------|---------|
| `Paper` | Paper metadata and content | Title, authors, abstract, venue | Both pipelines |
| `Review` | Review text and scores | Comments, ratings, aspects | Both pipelines |
| `ScienceParse` | Structured PDF content | Sections, references, figures | Acceptance classification |

### Data Model Interaction Pattern

```mermaid
graph LR
    subgraph "File System"
        ReviewJSON["reviews/*.json<br/>(review metadata)"]
        PaperPDF["pdfs/*.pdf<br/>(paper content)"]
        ParsedJSON["parsed_pdfs/*.json<br/>(Science Parse output)"]
    end
    
    subgraph "Object Models"
        PaperObj["Paper Object<br/>metadata fields"]
        ReviewObj["Review Object<br/>text + scores"]
        SParseObj["ScienceParse Object<br/>structure + references"]
    end
    
    subgraph "Feature Extraction"
        TextFeatures["Text Features<br/>(BOW, TF-IDF, embeddings)"]
        HandFeatures["Hand Features<br/>(23 statistics)"]
        AspectLabels["Aspect Labels<br/>(9 dimensions)"]
    end
    
    ReviewJSON --> PaperObj
    ReviewJSON --> ReviewObj
    PaperPDF --> SParseObj
    ParsedJSON --> SParseObj
    
    PaperObj --> TextFeatures
    ReviewObj --> TextFeatures
    ReviewObj --> AspectLabels
    SParseObj --> HandFeatures
    
    TextFeatures --> AcceptClassifier["classify.py"]
    HandFeatures --> AcceptClassifier
    
    TextFeatures --> AspectPredictor["predict.py"]
    AspectLabels --> AspectPredictor
```

**Sources:** [code/models/__init__.py:1](), Diagrams 1, 3, 4

The models are implemented as Python classes or dictionaries that parse JSON files from the dataset. Detailed field specifications are covered in [Data Models](#7.1).

---

## Text Processing Utilities

Text processing utilities provide standardized methods for converting raw text into numerical representations suitable for machine learning models. These utilities are shared across both pipelines but used differently depending on the modeling approach.

### Tokenization and Vocabulary Building

The system uses two approaches to vocabulary management:

**Acceptance Classification Approach:**
- Uses scikit-learn's built-in tokenization within vectorizers
- Vocabulary size determined by `max_vocab_size` parameter
- Vectorizers persisted as pickle files for consistent test-time encoding

**Aspect Prediction Approach:**
- Custom tokenization with NLTK sentence and word tokenizers
- Vocabulary built from training data with minimum frequency thresholds
- Special tokens: `<PAD>`, `<UNK>` for padding and unknown words

### Sequence Processing Pipeline

```mermaid
graph LR
    RawText["Raw Text<br/>(review comments)"]
    
    subgraph "Preprocessing"
        Clean["Text Cleaning<br/>(lowercase, punctuation)"]
        Tokenize["Tokenization<br/>(word splitting)"]
    end
    
    subgraph "Vocabulary"
        BuildVocab["Vocabulary Building<br/>(word -> int mapping)"]
        OOV["OOV Handling<br/>(UNK token)"]
    end
    
    subgraph "Encoding"
        BOWPath["BOW Encoding<br/>(CountVectorizer)"]
        TFIDFPath["TF-IDF Encoding<br/>(TfidfVectorizer)"]
        SeqPath["Sequence Encoding<br/>(int arrays)"]
    end
    
    subgraph "Post-processing"
        Pad["Padding<br/>(fixed length)"]
        Sparse["Sparse Matrix<br/>(scipy.sparse)"]
    end
    
    RawText --> Clean
    Clean --> Tokenize
    Tokenize --> BuildVocab
    BuildVocab --> OOV
    
    OOV --> BOWPath
    OOV --> TFIDFPath
    OOV --> SeqPath
    
    BOWPath --> Sparse
    TFIDFPath --> Sparse
    SeqPath --> Pad
```

**Sources:** Diagrams 3, 4 from architecture overview

---

## Embedding Management

The `sent2vec.py` module provides utilities for converting text into dense vector representations using pre-trained Word2Vec embeddings. This component bridges the gap between sparse bag-of-words representations and dense semantic embeddings.

### Embedding Vectorizers

The system implements two custom vectorizers compatible with scikit-learn's transformer interface:

```mermaid
graph TB
    subgraph "Word2Vec Model Loading"
        W2VFile["Pre-trained Model<br/>(GoogleNews-vectors)"]
        Gensim["gensim.models.KeyedVectors"]
        W2VModel["Word2Vec Model<br/>(300-dim vectors)"]
    end
    
    subgraph "Vectorizers"
        MeanEmbed["MeanEmbeddingVectorizer<br/>(average word vectors)"]
        TFIDFEmbed["TFIDFEmbeddingVectorizer<br/>(TF-IDF weighted average)"]
    end
    
    subgraph "Text Input"
        Tokens["Tokenized Text<br/>(list of words)"]
    end
    
    subgraph "Vector Output"
        MeanVec["Mean Vector<br/>(300-dim)"]
        TFIDFVec["TF-IDF Vector<br/>(300-dim)"]
    end
    
    W2VFile --> Gensim
    Gensim --> W2VModel
    
    W2VModel --> MeanEmbed
    W2VModel --> TFIDFEmbed
    
    Tokens --> MeanEmbed
    Tokens --> TFIDFEmbed
    
    MeanEmbed --> MeanVec
    TFIDFEmbed --> TFIDFVec
```

**Sources:** Diagram 3, [code/models/sent2vec.py]()

### Vectorizer Features

| Vectorizer Class | Aggregation Method | Use Case | Output Dimension |
|-----------------|-------------------|----------|------------------|
| `MeanEmbeddingVectorizer` | Arithmetic mean | Simple semantic representation | 300 |
| `TFIDFEmbeddingVectorizer` | TF-IDF weighted mean | Term-importance aware | 300 |

Both vectorizers implement the `fit()` and `transform()` interface, making them compatible with scikit-learn pipelines. They handle out-of-vocabulary words by skipping them during aggregation.

---

## Batch Processing and Data Loading

Data helper utilities manage the flow of data from disk to model inputs, handling batching, shuffling, and format conversions. These utilities are particularly important for the neural network training in the aspect prediction pipeline.

### Batch Iterator Implementation

The `data_helper.batch_iter` function generates mini-batches for training:

```mermaid
graph LR
    subgraph "Input Data"
        X["Feature Arrays<br/>(padded sequences)"]
        Y["Label Arrays<br/>(aspect scores)"]
    end
    
    subgraph "batch_iter Function"
        Shuffle["Optional Shuffling<br/>(random permutation)"]
        Chunk["Batch Chunking<br/>(batch_size slicing)"]
        Yield["Yield Generator<br/>(memory efficient)"]
    end
    
    subgraph "Training Loop"
        Model["Neural Model<br/>(CNN/RNN/DAN)"]
        Loss["Loss Computation<br/>(MSE)"]
        Backprop["Gradient Update<br/>(RMSProp)"]
    end
    
    X --> Shuffle
    Y --> Shuffle
    
    Shuffle --> Chunk
    Chunk --> Yield
    
    Yield --> Model
    Model --> Loss
    Loss --> Backprop
    Backprop -.next batch.-> Yield
```

**Sources:** Diagram 4, [code/data_helper.py]()

### Data Loading Functions

| Function | Purpose | Input Format | Output Format |
|----------|---------|--------------|---------------|
| `load_papers` | Load paper metadata | JSON files | Paper objects/dicts |
| `load_reviews` | Load review data | JSON files | Review objects/dicts |
| `load_parsed_pdfs` | Load Science Parse output | JSON files | ScienceParse objects/dicts |
| `prepare_data` | Tokenize and build vocab | Raw text | Sequences + vocab dict |
| `batch_iter` | Generate mini-batches | NumPy arrays | Batch tuples |

---

## Cross-Pipeline Usage Patterns

The core components are utilized differently by each pipeline, reflecting their distinct modeling approaches:

### Component Usage Matrix

```mermaid
graph TB
    subgraph "Core Components"
        DataModels["Data Models<br/>(Paper, Review, ScienceParse)"]
        TextProc["Text Processing<br/>(tokenization, vocab)"]
        Embeddings["Embeddings<br/>(sent2vec.py)"]
        Batching["Batching<br/>(batch_iter)"]
    end
    
    subgraph "Acceptance Classification"
        LoadData1["Load all models"]
        Vectorize["sklearn vectorizers<br/>(fit on train)"]
        ExtractFeatures["Extract 23 hand features<br/>(from ScienceParse)"]
        Combine["Merge text + hand features"]
        Persist["Persist vectorizers<br/>(*.pkl files)"]
    end
    
    subgraph "Aspect Prediction"
        LoadData2["Load Paper + Review"]
        BuildVocab["Build vocabulary<br/>(training set)"]
        Pad["Pad sequences<br/>(fixed length)"]
        Batch["Generate batches<br/>(shuffled)"]
        Train["Train neural model<br/>(epochal training)"]
    end
    
    DataModels --> LoadData1
    DataModels --> LoadData2
    
    TextProc --> Vectorize
    TextProc --> BuildVocab
    
    Embeddings --> Vectorize
    
    LoadData1 --> Vectorize
    LoadData1 --> ExtractFeatures
    Vectorize --> Combine
    ExtractFeatures --> Combine
    Combine --> Persist
    
    LoadData2 --> BuildVocab
    BuildVocab --> Pad
    Pad --> Batch
    
    Batching --> Batch
    Batch --> Train
```

**Sources:** Diagrams 3, 4, 5

### Pipeline-Specific Patterns

**Acceptance Classification:**
- Loads all three data models (Paper, Review, ScienceParse)
- Creates dense feature vectors through featurization
- Persists fitted vectorizers for test-time consistency
- No batching required (linear models process full matrices)

**Aspect Prediction:**
- Loads only Paper and Review models
- Builds vocabulary from training data
- Uses sequence padding for fixed-length inputs
- Requires batching for mini-batch gradient descent
- Early stopping based on development set performance

---

## Vectorizer Persistence and Reuse

A critical design pattern in the acceptance classification pipeline is the persistence of fitted vectorizers. This ensures that feature spaces remain consistent across train, dev, and test splits.

### Vectorizer Lifecycle

```mermaid
graph TD
    subgraph "Training Phase"
        TrainData["Training Data"]
        FitVectorizer["fit() on training<br/>(learn vocabulary)"]
        TransformTrain["transform() training<br/>(encode features)"]
        SaveVectorizer["Pickle vectorizer<br/>(vect_*.pkl)"]
    end
    
    subgraph "Dev/Test Phase"
        LoadVectorizer["Unpickle vectorizer<br/>(same vocab)"]
        DevTestData["Dev/Test Data"]
        TransformDevTest["transform() dev/test<br/>(encode features)"]
    end
    
    subgraph "Persistence Layer"
        VectBOW["vect_bow.pkl"]
        VectTFIDF["vect_tfidf.pkl"]
        VectW2V["vect_w2v.pkl"]
        VectW2VTFIDF["vect_w2v_tfidf.pkl"]
    end
    
    TrainData --> FitVectorizer
    FitVectorizer --> TransformTrain
    FitVectorizer --> SaveVectorizer
    
    SaveVectorizer --> VectBOW
    SaveVectorizer --> VectTFIDF
    SaveVectorizer --> VectW2V
    SaveVectorizer --> VectW2VTFIDF
    
    VectBOW --> LoadVectorizer
    VectTFIDF --> LoadVectorizer
    VectW2V --> LoadVectorizer
    VectW2VTFIDF --> LoadVectorizer
    
    LoadVectorizer --> TransformDevTest
    DevTestData --> TransformDevTest
```

**Sources:** Diagram 3, [code/featurize.py]()

This pattern prevents data leakage by ensuring that vocabulary and IDF statistics are computed only from training data, while dev and test data are encoded using the same learned parameters.

---

## Component Interaction Summary

The following table summarizes how core components integrate with the main pipeline scripts:

| Component | featurize.py | classify.py | predict.py | pred_models.py |
|-----------|-------------|-------------|------------|----------------|
| **Data Models** | Loads all three | Loads features | Loads Paper, Review | Receives preprocessed |
| **Tokenization** | Via sklearn | N/A | Custom NLTK | N/A |
| **Embeddings** | sent2vec vectorizers | N/A | Pre-trained (optional) | Embedding layer |
| **Vocabulary** | Built by vectorizers | N/A | Built from training | Embedding lookup |
| **Batching** | N/A | N/A | batch_iter | Consumes batches |
| **Persistence** | Saves vectorizers | Loads vectorizers | Saves checkpoints | N/A |

**Sources:** [code/featurize.py](), [code/classify.py](), [code/predict.py](), [code/pred_models.py](), Diagrams 3, 4

---

## Module Organization

The core components are organized into the following module structure:

```mermaid
graph TB
    subgraph "code/"
        Init1["__init__.py"]
        
        subgraph "models/"
            Init2["models/__init__.py"]
            Paper["Paper model definitions"]
            Review["Review model definitions"]
            SParse["ScienceParse model definitions"]
        end
        
        Featurize["featurize.py<br/>(feature extraction)"]
        Classify["classify.py<br/>(model training)"]
        Predict["predict.py<br/>(aspect prediction)"]
        PredModels["pred_models.py<br/>(neural architectures)"]
        
        subgraph "Utilities"
            Sent2Vec["sent2vec.py<br/>(embedding vectorizers)"]
            DataHelper["data_helper.py<br/>(batch utilities)"]
            Config["config.py<br/>(model configs)"]
        end
    end
    
    Init1 --> Init2
    Init2 --> Paper
    Init2 --> Review
    Init2 --> SParse
    
    Paper --> Featurize
    Review --> Featurize
    SParse --> Featurize
    
    Paper --> Predict
    Review --> Predict
    
    Sent2Vec --> Featurize
    DataHelper --> Predict
    Config --> PredModels
```

**Sources:** [code/__init__.py:1](), [code/models/__init__.py:1]()

The `__init__.py` files enable Python package imports and may define module-level exports. The modular organization allows each pipeline to import only the components it requires.

---

## Configuration Management

Model configurations are centralized in configuration objects that define hyperparameters for both pipelines:

| Configuration Class | Pipeline | Key Parameters |
|--------------------|----------|----------------|
| `CNNConfig` | Aspect Prediction | `num_filters`, `kernel_sizes`, `fc_layers` |
| `RNNConfig` | Aspect Prediction | `rnn_type`, `num_layers`, `hidden_size` |
| `DANConfig` | Aspect Prediction | `embedding_dim`, `fc_layers` |
| Feature config | Acceptance Classification | `encoder_type`, `max_vocab_size`, `ngram_range` |

These configurations provide a standardized interface for hyperparameter tuning and experimental reproducibility.

**Sources:** Diagram 4, [code/config.py]()

---

For detailed information on specific components, refer to the following subsections:
- [Data Models](#7.1) - Detailed field specifications and loading procedures
- [Data Helper Utilities](#7.2) - Implementation details of utility functions

---

