<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/PeerRead · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides a high-level introduction to the PeerRead dataset and repository, including its purpose, contents, and the two main machine learning systems for peer review analysis. For detailed setup instructions, see [Getting Started](#2). For in-depth documentation of the ML pipelines, see [Acceptance Classification Pipeline](#5) and [Aspect Prediction Pipeline](#6).

## Purpose and Scope

The PeerRead repository serves two primary functions:

1. **Dataset Distribution**: Provides access to a large-scale dataset of scientific peer reviews, including paper drafts, review texts, and accept/reject decisions from multiple top-tier conferences
2. **Reference Implementations**: Includes baseline models for two NLP research tasks:
   - **Acceptance prediction**: Classifying whether a paper will be accepted or rejected
   - **Aspect score prediction**: Predicting numerical scores for specific review aspects (e.g., clarity, originality, soundness)

The repository is designed for researchers studying peer review processes, developing automatic review generation systems, or exploring machine learning applications in scientific communication.

**Sources:** [README.md:1-11]()

## Dataset Contents

The PeerRead dataset consists of over **14,000 paper drafts** and corresponding accept/reject decisions, along with over **10,000 textual peer reviews** written by domain experts. The data spans multiple venues and time periods:

| Venue/Source | Time Period | Content Type |
|--------------|-------------|--------------|
| ACL | 2017 | Papers + Reviews + Decisions |
| NIPS | 2013-2017 | Papers + Reviews + Decisions |
| ICLR | 2017 | Papers + Reviews + Decisions + Aspect Annotations |
| CoNLL | 2016 | Papers + Reviews + Decisions |
| arXiv (cs.CL, cs.LG, cs.AI) | 2007-2017 | Papers (no reviews) |

The dataset includes:
- **PDF files** of paper drafts
- **JSON-formatted reviews** with text, scores, and metadata
- **Parsed paper content** extracted using Science Parse (sections, references, abstracts)
- **Aspect annotations** for ICLR 2017 reviews (9 numerical aspect scores)

**Sources:** [README.md:4-8]()

## Repository Structure

The repository is organized into two main directories:

```mermaid
graph TB
    Root["PeerRead Repository Root"]
    
    Data["data/<br/>(Dataset Files)"]
    Code["code/<br/>(ML Implementations)"]
    
    DataVenues["Venue-specific directories:<br/>acl_2017/<br/>nips_2013-2017/<br/>iclr_2017/<br/>conll_2016/<br/>arxiv.*_2007-2017/"]
    DataSplits["Each venue contains:<br/>train/, dev/, test/"]
    
    CodeAccept["Acceptance Classification:<br/>featurize.py<br/>classify.py<br/>sent2vec.py"]
    CodeAspect["Aspect Prediction:<br/>predict.py<br/>pred_models.py<br/>config.py"]
    CodeUtils["Shared Utilities:<br/>data_helper.py<br/>assign_annot_iclr_2017.py"]
    
    Root --> Data
    Root --> Code
    
    Data --> DataVenues
    DataVenues --> DataSplits
    
    Code --> CodeAccept
    Code --> CodeAspect
    Code --> CodeUtils
```

**Directory Structure:**
- **`/data/`**: Contains venue-specific subdirectories, each with train/dev/test splits. Each split directory includes `reviews/`, `pdfs/`, and `parsed_pdfs/` subdirectories
- **`/code/`**: Contains Python implementations of the two ML pipelines and shared utilities
- **`/setup.sh`**: Installation script for dependencies and data download

**Sources:** [README.md:8-11]()

## Machine Learning Pipelines

The repository implements two independent ML systems for analyzing peer reviews:

### Pipeline Architecture

```mermaid
graph LR
    subgraph "Data Layer"
        Dataset["PeerRead Dataset<br/>data/venue/split/"]
        PDFs["pdfs/*.pdf"]
        Reviews["reviews/*.json"]
        Parsed["parsed_pdfs/*.json<br/>(Science Parse output)"]
    end
    
    subgraph "Acceptance Classification System"
        Featurize["featurize.py<br/>Feature extraction:<br/>- Text encoders (BOW, TF-IDF, W2V)<br/>- Hand-crafted features (23 types)"]
        Classify["classify.py<br/>Linear models:<br/>- LogisticRegression<br/>- SVC, MLP, AdaBoost"]
        AcceptOut["Output:<br/>Classifier .pkl<br/>Accuracy metrics"]
    end
    
    subgraph "Aspect Prediction System"
        Predict["predict.py<br/>Data preparation:<br/>- Tokenization<br/>- Vocabulary building<br/>- Sequence padding"]
        Models["pred_models.py<br/>Neural architectures:<br/>- CNN (ConvNet)<br/>- RNN (LSTM/GRU)<br/>- DAN (Deep Averaging)"]
        AspectOut["Output:<br/>Model checkpoints<br/>RMSE per aspect"]
    end
    
    Dataset --> PDFs
    Dataset --> Reviews
    Dataset --> Parsed
    
    PDFs --> Featurize
    Reviews --> Featurize
    Parsed --> Featurize
    
    Featurize --> Classify
    Classify --> AcceptOut
    
    Reviews --> Predict
    Predict --> Models
    Models --> AspectOut
```

**Sources:** [README.md:10-11](), High-level diagrams

### Acceptance Classification Pipeline

**Purpose**: Predict whether a paper will be accepted or rejected based on paper content and review text.

**Approach**: Feature engineering with linear classifiers
- **Input**: Paper PDFs (parsed) + review JSONs
- **Method**: Extracts lexical features (bag-of-words, TF-IDF, Word2Vec embeddings) and hand-crafted features (reference statistics, document structure, linguistic patterns)
- **Models**: Linear classifiers selected via 5-fold cross-validation (Logistic Regression, SVM, MLP, AdaBoost)
- **Output**: Binary accept/reject predictions with accuracy metrics

**Key Components**:
- `featurize.py` - Extracts and persists features in SVMLight format
- `classify.py` - Trains and evaluates classification models
- `sent2vec.py` - Implements Word2Vec-based embedding vectorizers
- `run_featurize_classify.sh` - End-to-end pipeline execution script

For detailed documentation, see [Acceptance Classification Pipeline](#5).

**Sources:** [README.md:11](), High-level diagrams

### Aspect Prediction Pipeline

**Purpose**: Predict numerical scores for 9 specific review aspects (e.g., clarity, originality, soundness, impact).

**Approach**: Deep learning with neural networks
- **Input**: Review text + aspect annotations (ICLR 2017 subset)
- **Method**: Trains neural networks to perform multi-output regression, predicting scores for each aspect
- **Models**: Three architectures available - CNN (convolutional), RNN (recurrent), DAN (deep averaging network)
- **Output**: Aspect score predictions with RMSE metrics compared to mean/majority baselines

**Key Components**:
- `predict.py` - Data loading, preprocessing, training loop, and evaluation
- `pred_models.py` - Neural network architecture implementations
- `config.py` - Configuration classes for each model type (CNNConfig, RNNConfig, DANConfig)
- `run_predict.sh` - Pipeline execution script

For detailed documentation, see [Aspect Prediction Pipeline](#6).

**Sources:** [README.md:11](), High-level diagrams

## Code-to-System Mapping

The following diagram maps the conceptual systems to their implementation files:

```mermaid
graph TB
    subgraph "Data Structures"
        PaperModel["models.Paper class<br/>(implicit in featurize.py)"]
        ReviewModel["models.Review class<br/>(implicit in predict.py)"]
        ScienceParseModel["ScienceParse JSON schema<br/>(parsed_pdfs/*.json)"]
    end
    
    subgraph "Acceptance Classification Implementation"
        FeaturizeScript["code/featurize.py<br/>Functions:<br/>- load_train_test_data()<br/>- featurize()<br/>- build_feature_matrix()"]
        
        ClassifyScript["code/classify.py<br/>Functions:<br/>- load_data()<br/>- run_cv()<br/>- run_test()"]
        
        Sent2VecScript["code/sent2vec.py<br/>Classes:<br/>- MeanEmbeddingVectorizer<br/>- TFIDFEmbeddingVectorizer"]
        
        AcceptShell["code/run_featurize_classify.sh<br/>Orchestrates:<br/>1. featurize.py --train<br/>2. featurize.py --dev/test<br/>3. classify.py"]
    end
    
    subgraph "Aspect Prediction Implementation"
        PredictScript["code/predict.py<br/>Functions:<br/>- prepare_data()<br/>- choose_label()<br/>- train()<br/>- evaluate()"]
        
        ModelsScript["code/pred_models.py<br/>Classes:<br/>- TextCNN<br/>- TextRNN<br/>- TextDAN"]
        
        ConfigScript["code/config.py<br/>Classes:<br/>- CNNConfig<br/>- RNNConfig<br/>- DANConfig"]
        
        AspectShell["code/run_predict.sh<br/>Orchestrates:<br/>predict.py with model flags"]
    end
    
    subgraph "Shared Utilities"
        DataHelper["code/data_helper.py<br/>Functions:<br/>- batch_iter()<br/>- pad_sentences()<br/>- get_w2v_embedding()"]
        
        AssignAnnot["code/assign_annot_iclr_2017.py<br/>Merges aspect annotations<br/>into review JSONs"]
    end
    
    ScienceParseModel --> FeaturizeScript
    ReviewModel --> FeaturizeScript
    PaperModel --> FeaturizeScript
    
    Sent2VecScript --> FeaturizeScript
    FeaturizeScript --> ClassifyScript
    FeaturizeScript --> AcceptShell
    ClassifyScript --> AcceptShell
    
    ReviewModel --> PredictScript
    AssignAnnot --> PredictScript
    DataHelper --> PredictScript
    ConfigScript --> PredictScript
    ModelsScript --> PredictScript
    PredictScript --> AspectShell
```

**Sources:** [README.md:11](), High-level diagrams

## Data Flow Summary

The complete end-to-end workflow consists of three sequential phases:

```mermaid
flowchart TD
    Phase1["Phase 1: Data Collection (Optional)<br/>NIPS_crawl.py<br/>Downloads papers and reviews"]
    
    Phase2["Phase 2: Data Preparation (Required)<br/>prepare.py + Science Parse<br/>Splits data, parses PDFs"]
    
    Phase3A["Phase 3A: Acceptance Classification<br/>run_featurize_classify.sh<br/>Feature extraction + training"]
    
    Phase3B["Phase 3B: Aspect Prediction<br/>run_predict.sh<br/>Neural network training"]
    
    Raw["Raw Data:<br/>Conference websites<br/>Opt-in collections<br/>arXiv preprints"]
    
    Structured["Structured Dataset:<br/>data/venue/train/<br/>data/venue/dev/<br/>data/venue/test/"]
    
    Output3A["Acceptance Models:<br/>Classifier .pkl files<br/>Train/dev/test accuracy"]
    
    Output3B["Aspect Models:<br/>TensorFlow checkpoints<br/>RMSE metrics per aspect"]
    
    Raw --> Phase1
    Phase1 --> Phase2
    Raw -.if pre-collected.-> Phase2
    
    Phase2 --> Structured
    
    Structured --> Phase3A
    Structured --> Phase3B
    
    Phase3A --> Output3A
    Phase3B --> Output3B
```

**Key Points**:
1. **Phase 1** (optional): Data can be collected via web crawling or used pre-collected
2. **Phase 2** (required): The `prepare.py` script creates train/dev/test splits and invokes Science Parse to extract structured content from PDFs
3. **Phase 3**: Two independent pipelines that can be run in parallel or separately

For setup and execution details, see [Getting Started](#2). For dataset structure details, see [Dataset Structure](#3).

**Sources:** [README.md:1-14](), High-level diagrams

## External Dependencies

The repository relies on several external tools and libraries:

| Dependency | Purpose | Used By |
|------------|---------|---------|
| **Science Parse** | PDF parsing (extracting sections, references, abstracts) | Data preparation pipeline |
| **scikit-learn** | Feature vectorizers and classification models | Acceptance classification |
| **Gensim** | Word2Vec embeddings | Both pipelines |
| **TensorFlow** | Neural network training | Aspect prediction |
| **NLTK** | Text tokenization and preprocessing | Aspect prediction |

The `setup.sh` script at the repository root installs these dependencies and downloads necessary data files.

**Sources:** [README.md:14](), High-level diagrams

## Research Applications

The dataset and models support research in multiple areas:

1. **Peer Review Analysis**: Understanding what factors influence acceptance decisions
2. **Automatic Review Generation**: Training models to provide feedback on scientific papers
3. **Review Quality Assessment**: Predicting which aspects of a paper need improvement
4. **Scholarly Document Understanding**: Leveraging parsed paper structure for NLP tasks
5. **Transfer Learning**: Using pre-trained models for related scientific document tasks

For citation information and acknowledgements, see [README.md:17-35]().

**Sources:** [README.md:1-11]()

## Quick Start

To begin using PeerRead:

1. **Installation**: Run `./setup.sh` to install dependencies
2. **Explore Data**: Navigate to `data/` to examine the dataset structure (see [Dataset Structure](#3))
3. **Run Acceptance Classification**: Execute `code/run_featurize_classify.sh` (see [Acceptance Classification Pipeline](#5))
4. **Run Aspect Prediction**: Execute `code/run_predict.sh` (see [Aspect Prediction Pipeline](#6))

For complete setup instructions, see [Getting Started](#2).

**Sources:** [README.md:13-14]()

---

