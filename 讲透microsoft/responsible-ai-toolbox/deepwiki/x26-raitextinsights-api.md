<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/responsible-ai-toolbox · extra page RAITextInsights API · fetched 2026-10-26 -->

# RAITextInsights API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/CI-e2e-notebooks-text-vision.yml](.github/workflows/CI-e2e-notebooks-text-vision.yml)
- [.github/workflows/CI-notebook-text.yml](.github/workflows/CI-notebook-text.yml)
- [.github/workflows/CI-notebook-vision.yml](.github/workflows/CI-notebook-vision.yml)
- [.github/workflows/CI-responsibleai-text-vision-pytest.yml](.github/workflows/CI-responsibleai-text-vision-pytest.yml)
- [README.md](README.md)
- [notebooks/responsibleaidashboard/text/responsibleaidashboard-openai-model-debugging.ipynb](notebooks/responsibleaidashboard/text/responsibleaidashboard-openai-model-debugging.ipynb)
- [notebooks/test_notebooks.py](notebooks/test_notebooks.py)
- [responsibleai_text/requirements.txt](responsibleai_text/requirements.txt)
- [responsibleai_vision/requirements.txt](responsibleai_vision/requirements.txt)
- [scripts/e2e-widget.js](scripts/e2e-widget.js)

</details>



## Purpose and Scope

This document describes the `RAITextInsights` class, the main entry point for analyzing text and NLP models in the Responsible AI Toolbox. `RAITextInsights` provides specialized support for text classification, question answering, and generative AI tasks.

For general information about the core RAI framework, see [RAIInsights Core API](#3.2). For vision-specific analysis, see [RAIVisionInsights API](#5.1.1). For information about text-specific UI components, see [Text Package](#5.2).

---

## Overview

`RAITextInsights` extends the core RAI framework to handle text data and NLP models. It inherits from `RAIBaseInsights` and adapts the standard analysis managers (error analysis, explainer, causal, counterfactual) to work with text-specific data structures and model outputs.

### Architecture Position

```mermaid
graph TB
    subgraph "Core Framework"
        RAIBaseInsights["RAIBaseInsights<br/>(Abstract Base)"]
    end
    
    subgraph "Modality Extensions"
        RAIInsights["RAIInsights<br/>(Tabular Data)"]
        RAITextInsights["RAITextInsights<br/>(Text/NLP Data)"]
        RAIVisionInsights["RAIVisionInsights<br/>(Image Data)"]
    end
    
    subgraph "Text-Specific Components"
        ModelTask["ModelTask Enum<br/>TEXT_CLASSIFICATION<br/>QUESTION_ANSWERING<br/>GENERATIVE_TEXT"]
        TextManagers["Text-Adapted Managers<br/>- ErrorAnalysisManager<br/>- ExplainerManager"]
        NLPExtractors["nlp_feature_extractors<br/>Token-level features"]
    end
    
    subgraph "Dependencies"
        spacy["spacy<br/>Language models"]
        transformers["transformers<br/>Model interfaces"]
        responsibleai["responsibleai>=0.35.0<br/>Core package"]
    end
    
    RAIBaseInsights -->|extends| RAIInsights
    RAIBaseInsights -->|extends| RAITextInsights
    RAIBaseInsights -->|extends| RAIVisionInsights
    
    RAITextInsights --> ModelTask
    RAITextInsights --> TextManagers
    RAITextInsights --> NLPExtractors
    RAITextInsights --> spacy
    RAITextInsights --> transformers
    RAITextInsights --> responsibleai
    
    style RAITextInsights fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**RAITextInsights Class Position in Package Hierarchy**

Sources: [responsibleai_text/requirements.txt:1-7](), [README.md:27-32]()

---

## Package Dependencies

The `responsibleai_text` package requires the following core dependencies:

| Dependency | Version | Purpose |
|------------|---------|---------|
| `numpy` | >=1.17.2, <2.0.0 | Array operations |
| `pandas` | >=0.25.1 | DataFrame handling |
| `scikit-learn` | >=0.22.1 | Base ML utilities |
| `scipy` | >=1.4.1 | Scientific computing |
| `semver` | ~=2.13.0 | Version management |
| `nlp-feature-extractors` | ==0.1.0 | Text feature extraction |
| `responsibleai` | >=0.35.0 | Core RAI framework |

Additional optional dependencies include `spacy` for language models and `transformers` for HuggingFace model integration.

Sources: [responsibleai_text/requirements.txt:1-7]()

---

## Initialization

### Basic Initialization Pattern

The `RAITextInsights` class follows the same initialization pattern as the core `RAIInsights` class, but with text-specific considerations:

```mermaid
graph LR
    subgraph "Input Requirements"
        Model["model<br/>(predict or predict_proba)"]
        TestData["test_data<br/>(DataFrame with text columns)"]
        TargetColumn["target_column<br/>(str)"]
        TaskType["task_type<br/>(ModelTask enum)"]
    end
    
    subgraph "Initialization"
        Constructor["RAITextInsights()"]
        Validation["Input Validation<br/>- Model interface<br/>- Data format<br/>- Task compatibility"]
        Setup["Setup<br/>- Create JointDataset<br/>- Initialize managers<br/>- Setup metadata"]
    end
    
    subgraph "Output"
        RAIObject["RAITextInsights Instance<br/>Ready for analysis"]
    end
    
    Model --> Constructor
    TestData --> Constructor
    TargetColumn --> Constructor
    TaskType --> Constructor
    
    Constructor --> Validation
    Validation --> Setup
    Setup --> RAIObject
```

**RAITextInsights Initialization Flow**

### Constructor Signature

The typical initialization looks like:

```python
from responsibleai_text import RAITextInsights, ModelTask

rai_insights = RAITextInsights(
    model,                    # Model or pipeline with predict method
    test_data,               # pandas DataFrame with text data
    target_column,           # Name of the target/label column
    task_type=ModelTask.TEXT_CLASSIFICATION,  # Task type
    classes=None,            # Optional: class labels for classification
    text_column=None,        # Optional: name of main text column
    serializer=None          # Optional: custom serializer
)
```

Sources: [notebooks/responsibleaidashboard/text/responsibleaidashboard-openai-model-debugging.ipynb:297-299]()

---

## Supported Task Types

### ModelTask Enum

`RAITextInsights` supports three primary task types through the `ModelTask` enum:

```mermaid
graph TB
    subgraph "ModelTask Enum Values"
        TC["TEXT_CLASSIFICATION<br/>Single or multi-label<br/>text categorization"]
        QA["QUESTION_ANSWERING<br/>Extractive QA<br/>with F1/EM metrics"]
        GT["GENERATIVE_TEXT<br/>Generative AI models<br/>with custom metrics"]
    end
    
    subgraph "Data Format Requirements"
        TC_Data["Classification:<br/>- text column(s)<br/>- label column"]
        QA_Data["Question Answering:<br/>- context column<br/>- questions column<br/>- answers column"]
        GT_Data["Generative:<br/>- prompt column<br/>- generated_text column<br/>- reference column (optional)"]
    end
    
    subgraph "Supported Analysis"
        ErrorAnalysis["Error Analysis<br/>Task-specific error metrics"]
        Explainer["Explainer<br/>Token-level importance"]
        DataExplorer["Data Explorer<br/>Instance browsing"]
    end
    
    TC --> TC_Data
    QA --> QA_Data
    GT --> GT_Data
    
    TC_Data --> ErrorAnalysis
    QA_Data --> ErrorAnalysis
    GT_Data --> ErrorAnalysis
    
    TC_Data --> Explainer
    QA_Data --> Explainer
    
    TC_Data --> DataExplorer
    QA_Data --> DataExplorer
    GT_Data --> DataExplorer
```

**Task Types and Their Requirements**

### Task-Specific Characteristics

#### TEXT_CLASSIFICATION
- Supports binary, multiclass, and multilabel classification
- Model must implement `predict_proba()` for probability outputs
- Compatible with standard classification metrics (accuracy, precision, recall, F1)
- Example notebooks: DBPedia classification, binary text classification

#### QUESTION_ANSWERING
- Dataset requires three columns: `context`, `questions`, `answers`
- Model returns text spans as predictions
- Evaluated using F1 score and Exact Match (EM) metrics
- Supports both extractive QA models and API endpoints (e.g., OpenAI)

#### GENERATIVE_TEXT
- For generative AI models (GPT, T5, etc.)
- Supports custom evaluation metrics
- Can integrate with prompt templates
- Model outputs are free-form text

Sources: [notebooks/responsibleaidashboard/text/responsibleaidashboard-openai-model-debugging.ipynb:73-74](), [README.md:113-118]()

---

## Data Format Expectations

### Text Classification Data

For text classification tasks, data is expected in a pandas DataFrame:

| Column Type | Required | Description |
|-------------|----------|-------------|
| Text column(s) | Yes | One or more columns containing text data |
| Label column | Yes | Target column specified in `target_column` parameter |
| Metadata columns | Optional | Additional columns for cohort analysis |

### Question Answering Data

Question answering requires specific column structure:

| Column Name | Required | Description |
|-------------|----------|-------------|
| `context` | Yes | Background text/passage |
| `questions` | Yes | Questions to be answered |
| `answers` | Yes | Ground truth answers (for evaluation) |

Example from SQuAD dataset:

```mermaid
graph LR
    subgraph "Input DataFrame"
        Context["context:<br/>'In meteorology, precipitation...'"]
        Question["questions:<br/>'What causes precipitation?'"]
        Answer["answers:<br/>'air mass rise'"]
    end
    
    subgraph "Model Processing"
        Pipeline["model.predict(data)"]
    end
    
    subgraph "Output"
        Prediction["predictions:<br/>'air mass rise'"]
        Metrics["F1 Score: 1.0<br/>EM Score: 1.0"]
    end
    
    Context --> Pipeline
    Question --> Pipeline
    Pipeline --> Prediction
    Answer --> Metrics
    Prediction --> Metrics
```

**Question Answering Data Flow**

Sources: [notebooks/responsibleaidashboard/text/responsibleaidashboard-openai-model-debugging.ipynb:131-147]()

---

## Manager Integration

### Text-Adapted Error Analysis

The Error Analysis manager adapts to text-specific model types:

```mermaid
graph TB
    subgraph "ErrorAnalysisManager"
        BaseEA["BaseAnalyzer<br/>(from erroranalysis package)"]
    end
    
    subgraph "Text-Specific Adaptations"
        QAMetrics["Question Answering:<br/>- F1 score per instance<br/>- EM score per instance<br/>- Token overlap analysis"]
        
        ClassMetrics["Text Classification:<br/>- Standard classification metrics<br/>- Per-class error rates<br/>- Confusion matrix"]
        
        GenMetrics["Generative Text:<br/>- Custom metric support<br/>- Reference-based evaluation<br/>- Prompt analysis"]
    end
    
    subgraph "Error Tree Construction"
        SurrogateTree["Surrogate Tree Model<br/>Predicts error patterns<br/>on text features"]
    end
    
    BaseEA --> QAMetrics
    BaseEA --> ClassMetrics
    BaseEA --> GenMetrics
    
    QAMetrics --> SurrogateTree
    ClassMetrics --> SurrogateTree
    GenMetrics --> SurrogateTree
```

**Text-Specific Error Analysis Adaptations**

### Text-Adapted Explainer

The Explainer manager provides token-level explanations:

```mermaid
graph TB
    subgraph "ExplainerManager"
        BaseExplainer["ExplainerManager<br/>(from responsibleai)"]
    end
    
    subgraph "Text Explanation Methods"
        TokenMasking["Token Masking:<br/>- SHAP on token level<br/>- LIME with text perturbations<br/>- Attention weights"]
        
        FeatureExtraction["NLP Feature Extractors:<br/>- Bag of words<br/>- TF-IDF features<br/>- Embeddings"]
    end
    
    subgraph "UI Components"
        InterpretText["interpret-text UI:<br/>- Token highlighting<br/>- Importance visualization<br/>- Interactive perturbation"]
    end
    
    BaseExplainer --> TokenMasking
    BaseExplainer --> FeatureExtraction
    
    TokenMasking --> InterpretText
    FeatureExtraction --> InterpretText
```

**Text Explainer Integration**

Sources: [responsibleai_text/requirements.txt:6]()

---

## Workflow Examples

### Complete Analysis Workflow

```mermaid
graph TB
    subgraph "1. Data Preparation"
        LoadData["Load text dataset<br/>(pandas DataFrame)"]
        PrepareModel["Prepare model/pipeline<br/>(with predict method)"]
    end
    
    subgraph "2. Initialize RAITextInsights"
        CreateInsights["rai_insights = RAITextInsights(<br/>model, test_data, target_column,<br/>task_type=ModelTask.TEXT_CLASSIFICATION<br/>)"]
    end
    
    subgraph "3. Add Analysis Components"
        AddError["rai_insights.error_analysis.add()"]
        AddExplain["rai_insights.explainer.add()"]
    end
    
    subgraph "4. Compute Insights"
        Compute["rai_insights.compute()"]
    end
    
    subgraph "5. Visualize Results"
        Dashboard["ResponsibleAIDashboard(<br/>rai_insights<br/>)"]
    end
    
    LoadData --> CreateInsights
    PrepareModel --> CreateInsights
    CreateInsights --> AddError
    AddError --> AddExplain
    AddExplain --> Compute
    Compute --> Dashboard
```

**End-to-End Text Analysis Workflow**

### Question Answering Example

Based on the OpenAI notebook example:

```mermaid
sequenceDiagram
    participant User
    participant RAITextInsights
    participant ErrorManager
    participant Model
    participant Dashboard
    
    User->>RAITextInsights: Initialize with QA task type
    Note over RAITextInsights: Validate QA data format<br/>(context, questions, answers)
    
    User->>ErrorManager: error_analysis.add()
    Note over ErrorManager: Configure QA-specific metrics
    
    User->>RAITextInsights: compute()
    RAITextInsights->>Model: Generate predictions
    Model-->>RAITextInsights: Return answer texts
    RAITextInsights->>ErrorManager: Calculate F1/EM scores
    ErrorManager-->>RAITextInsights: Return error analysis
    
    User->>Dashboard: ResponsibleAIDashboard(rai_insights)
    Dashboard-->>User: Display interactive UI
```

**Question Answering Analysis Sequence**

Sources: [notebooks/responsibleaidashboard/text/responsibleaidashboard-openai-model-debugging.ipynb:297-337]()

---

## Text-Specific Features

### NLP Feature Extractors

The `nlp_feature_extractors` package provides text-specific feature extraction:

| Extractor Type | Purpose | Output |
|----------------|---------|--------|
| Bag of Words | Token frequency features | Sparse matrix |
| TF-IDF | Term importance weighting | Sparse matrix |
| Word Embeddings | Dense semantic representations | Dense matrix |
| Custom Extractors | Domain-specific features | Custom format |

These extractors enable error analysis and explanation on text data by converting text into numeric features that the surrogate tree and explainer can process.

### Token-Level Explanations

Unlike tabular features, text explanations operate at the token level:

- Individual tokens receive importance scores
- Importance is visualized through text highlighting in the UI
- Supports both local (instance-level) and global explanations
- Compatible with SHAP, LIME, and attention-based methods

---

## Model Interface Requirements

### Standard Prediction Interface

Models must implement one of:

1. **`predict(data)` method**: Returns predictions
   - For classification: class labels
   - For QA: answer text strings
   - For generative: generated text

2. **`predict_proba(data)` method**: Returns probability distributions
   - Required for classification with probability-based explanations
   - Optional for other task types

### API Endpoint Wrapping

For API-based models (e.g., OpenAI, Azure endpoints), use wrapper classes:

```python
from ml_wrappers.model import OpenaiWrapperModel

openai_model = OpenaiWrapperModel(
    api_type="azure",
    api_base="https://your.openai.azure.com/",
    api_version="2023-03-15-preview",
    api_key="your_key",
    engine='gpt-4'
)
```

The wrapper ensures the model conforms to the expected interface while handling API communication.

Sources: [notebooks/responsibleaidashboard/text/responsibleaidashboard-openai-model-debugging.ipynb:167-192]()

---

## Integration with Dashboard

### Dashboard Components for Text

The text dashboard includes specialized UI components:

```mermaid
graph TB
    subgraph "ResponsibleAIDashboard"
        MAD["ModelAssessmentDashboard<br/>(Main React component)"]
    end
    
    subgraph "Text-Specific Views"
        InterpretText["interpret-text library:<br/>- Token highlighting<br/>- Importance display<br/>- QA metrics panel"]
        
        ErrorView["Error Analysis View:<br/>- Text-aware cohorts<br/>- F1/EM metric display<br/>- Token-level filtering"]
        
        DataExplorer["Data Explorer:<br/>- Text preview<br/>- Long text truncation<br/>- Column-based search"]
    end
    
    subgraph "Backend Data"
        RAITextInsights["RAITextInsights<br/>Computed results"]
        DashboardInput["ResponsibleAIDashboardInput<br/>Flask API adapter"]
    end
    
    MAD --> InterpretText
    MAD --> ErrorView
    MAD --> DataExplorer
    
    InterpretText --> DashboardInput
    ErrorView --> DashboardInput
    DataExplorer --> DashboardInput
    
    DashboardInput --> RAITextInsights
```

**Text Dashboard Component Integration**

The dashboard automatically detects the task type from `RAITextInsights` and renders appropriate UI components.

---

## Testing and CI/CD

### Notebook Tests

Text notebooks are tested using the pytest framework with specialized markers:

| Test Marker | Purpose | Notebooks Covered |
|-------------|---------|-------------------|
| `text_notebooks` | Marks text-specific tests | All text notebooks |
| Parametrized | Multiple OS/Python versions | Ubuntu, Windows; Python 3.8-3.10 |

Test execution:
```bash
python -m pytest -s -v notebooks -m text_notebooks
```

### CI Workflows

The text package has dedicated CI workflows:

1. **CI-notebook-text.yml**: Tests text notebooks
   - Runs on: ubuntu-latest, windows-latest
   - Python versions: 3.8, 3.9, 3.10
   - Includes spacy model download

2. **CI-responsibleai-text-vision-pytest.yml**: Unit/integration tests
   - Tests both text and vision packages
   - Matrix excludes macOS due to timeout issues
   - Installs keras compatibility layer for transformers

3. **CI-e2e-notebooks-text-vision.yml**: End-to-end dashboard tests
   - Tests complete widget integration
   - Uses Cypress for UI testing
   - Covers specific notebooks: DBPedia, blbooksgenre, covid-event

Sources: [.github/workflows/CI-notebook-text.yml:1-125](), [.github/workflows/CI-responsibleai-text-vision-pytest.yml:1-166](), [.github/workflows/CI-e2e-notebooks-text-vision.yml:1-174]()

---

## Limitations and Constraints

### Current Limitations

1. **Explainer Support**: Not all explanation methods support API-based models (e.g., OpenAI endpoints)
2. **macOS CI**: Currently excluded from some CI workflows due to timeout issues
3. **Generative Metrics**: Limited built-in metrics for generative text tasks
4. **Large Text**: Very long documents may require truncation or chunking

### Known Issues

- QA notebooks for OpenAI are excluded from automated e2e tests
- Some transformers models require keras compatibility layer (keras==2.15)
- Specific torch/torchvision version constraints for compatibility

Sources: [.github/workflows/CI-responsibleai-text-vision-pytest.yml:20-39](), [notebooks/responsibleaidashboard/text/responsibleaidashboard-openai-model-debugging.ipynb:318-319]()

---

## Example Notebooks

The repository includes several text analysis notebooks:

| Notebook | Task Type | Model | Dataset |
|----------|-----------|-------|---------|
| responsibleaidashboard-DBPedia-text-classification-model-debugging | Classification | Custom | DBPedia |
| responsibleaidashboard-blbooksgenre-binary-text-classification-model-debugging | Binary Classification | Custom | BLBooksGenre |
| responsibleaidashboard-covid-event-multilabel-text-classification-model-debugging | Multilabel Classification | Custom | COVID-19 Events |
| responsibleaidashboard-question-answering-model-debugging | QA | HuggingFace | SQuAD |
| responsibleaidashboard-openai-model-debugging | QA | OpenAI API | SQuAD |

All notebooks follow a similar structure:
1. Load and prepare data
2. Initialize RAITextInsights
3. Add analysis components (error_analysis, explainer)
4. Compute insights
5. Visualize with ResponsibleAIDashboard

Sources: [README.md:113-118](), [notebooks/test_notebooks.py:315-360](), [scripts/e2e-widget.js:30-38]()

---

