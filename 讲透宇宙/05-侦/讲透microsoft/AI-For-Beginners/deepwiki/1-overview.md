<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/AI-For-Beginners · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [etc/CODE_OF_CONDUCT.md](etc/CODE_OF_CONDUCT.md)
- [etc/Mindmap.html](etc/Mindmap.html)
- [etc/Mindmap.md](etc/Mindmap.md)
- [etc/Mindmap.svg](etc/Mindmap.svg)
- [etc/SUPPORT.md](etc/SUPPORT.md)
- [etc/TRANSLATIONS.md](etc/TRANSLATIONS.md)
- [index.html](index.html)
- [lessons/1-Intro/README.md](lessons/1-Intro/README.md)
- [lessons/1-Intro/translations/README.ja.md](lessons/1-Intro/translations/README.ja.md)
- [lessons/4-ComputerVision/11-ObjectDetection/README.md](lessons/4-ComputerVision/11-ObjectDetection/README.md)
- [lessons/4-ComputerVision/11-ObjectDetection/lab/README.md](lessons/4-ComputerVision/11-ObjectDetection/lab/README.md)
- [lessons/5-NLP/15-LanguageModeling/CBoW-TF.ipynb](lessons/5-NLP/15-LanguageModeling/CBoW-TF.ipynb)
- [lessons/5-NLP/15-LanguageModeling/README.md](lessons/5-NLP/15-LanguageModeling/README.md)
- [lessons/5-NLP/15-LanguageModeling/lab/README.md](lessons/5-NLP/15-LanguageModeling/lab/README.md)
- [lessons/5-NLP/20-LangModels/GPT-PyTorch.ipynb](lessons/5-NLP/20-LangModels/GPT-PyTorch.ipynb)
- [lessons/5-NLP/20-LangModels/README.md](lessons/5-NLP/20-LangModels/README.md)
- [lessons/6-Other/22-DeepRL/README.md](lessons/6-Other/22-DeepRL/README.md)

</details>



The AI-For-Beginners repository (`https://github.com/microsoft/AI-For-Beginners`) is a comprehensive, open-source educational curriculum designed to teach artificial intelligence fundamentals through a structured 12-week, 24-lesson program [README.md:15-21](). The repository combines theoretical content with hands-on implementation exercises using industry-standard frameworks (`PyTorch` and `TensorFlow`), assessment tools, and extensive internationalization support [README.md:15-21]().

This overview covers the high-level architecture, core components, and organizational structure of the repository. For detailed information about the curriculum breakdown, see [Curriculum Structure](#1.1). For details on quizzes, labs, and pedagogical delivery, see [Learning Approach](#1.2).

**Sources:** [README.md:15-21]()

## Purpose and Target Audience

The curriculum targets beginners with no prior AI experience, guiding them from foundational concepts through advanced topics. The repository emphasizes practical implementation with executable Jupyter notebooks and progressive skill-building through labs and quizzes [README.md:15-21]().

The content excludes business-focused AI education, classic machine learning (covered separately in `ML-For-Beginners`), cloud-specific frameworks, and advanced mathematical foundations—instead focusing on conceptual understanding and hands-on coding [README.md:61-75]().

**Sources:** [README.md:15-21](), [README.md:61-75]()

## Repository Architecture

```mermaid
graph TB
    subgraph "Root Structure"
        README["README.md"]
        LESSONS["lessons/"]
        ETC["etc/"]
        TRANS["translations/"]
        EXAMPLES["examples/"]
        DEVCONTAINER[".devcontainer/"]
    end
    
    subgraph "Lesson Structure (lessons/X-Topic/NN-Name)"
        LESSON_README["README.md"]
        NOTEBOOKS["*.ipynb"]
        LAB["lab/README.md"]
        IMAGES["images/"]
    end
    
    subgraph "Quiz System (etc)"
        QUIZ_SRC["quiz-src/"]
        QUIZ_APP["quiz-app/"]
        MINDMAP["Mindmap.md"]
    end
    
    README --> LESSONS
    README --> ETC
    README --> TRANS
    LESSONS --> LESSON_README
    LESSONS --> NOTEBOOKS
    LESSONS --> LAB
    ETC --> QUIZ_SRC
    ETC --> QUIZ_APP
    ETC --> MINDMAP
```

The repository follows a hierarchical structure organized by topic domains (`1-Intro`, `2-Symbolic`, `3-NeuralNetworks`, `4-ComputerVision`, `5-NLP`, `6-Other`, `7-Ethics`, `X-Extras`). Each lesson directory contains Markdown content, dual-framework Jupyter notebooks, supporting images, and optional lab assignments [README.md:15-75](), [etc/Mindmap.md:1-68]().

**Sources:** [README.md:15-75](), [etc/Mindmap.md:1-68]()

## Core Content Organization

### Lesson Taxonomy

```mermaid
graph LR
    L0["0-course-setup"]
    L1["1-Intro"]
    L2["2-Symbolic"]
    L3_5["3-NeuralNetworks"]
    L4["4-ComputerVision"]
    L5["5-NLP"]
    L6["6-Other"]
    L7["7-Ethics"]
    LX["X-Extras"]
    
    L0 --> L1
    L1 --> L2
    L2 --> L3_5
    L3_5 --> L4
    L3_5 --> L5
    L4 --> L6
    L5 --> L6
    L6 --> L7
    L7 --> LX
```

For a comprehensive week-by-week breakdown and topic progression, see [Curriculum Structure](#1.1).

**Sources:** [README.md:61-75](), [etc/Mindmap.md:1-68]()

### Dual-Framework Implementation

Each technical lesson provides parallel implementations in both frameworks:

| Framework | Notebook Patterns | Example Files |
|-----------|------------------|---------------|
| **PyTorch** | `*PyTorch.ipynb` | `lessons/3-NeuralNetworks/05-Frameworks/IntroPyTorch.ipynb` [etc/Mindmap.md:23-23]() |
| **TensorFlow/Keras** | `*TF.ipynb`, `*Keras.ipynb` | `lessons/3-NeuralNetworks/05-Frameworks/IntroKerasTF.md` [etc/Mindmap.md:24-24]() |

For details on how frameworks are utilized across lessons, see [Curriculum Structure](#1.1) and [Learning Approach](#1.2).

**Sources:** [README.md:61-75](), [etc/Mindmap.md:19-25]()

## Technology Stack

```mermaid
graph TB
    subgraph "Development Environments"
        VSCODE["VS Code + Dev Container"]
        CODESPACE["GitHub Codespaces"]
        BINDER["Binder"]
        LOCAL["Local Python"]
    end
    
    subgraph "Python Dependencies"
        CONDA["Miniconda"]
        PYTORCH["PyTorch Stack"]
        TENSORFLOW["TensorFlow Stack"]
        SHARED["Shared Libraries"]
        NLP_TOOLS["NLP Tools"]
    end
    
    subgraph "Quiz Application"
        VUE["Vue.js SPA"]
        VUE_ROUTER["vue-router"]
        VUE_I18N["vue-i18n"]
    end
    
    VSCODE --> CONDA
    CODESPACE --> CONDA
    BINDER --> CONDA
    LOCAL --> CONDA
    
    CONDA --> PYTORCH
    CONDA --> TENSORFLOW
    CONDA --> SHARED
    PYTORCH --> NLP_TOOLS
    TENSORFLOW --> NLP_TOOLS
    
    VUE --> VUE_ROUTER
    VUE --> VUE_I18N
```

The development environment supports four entry points (VS Code Dev Containers, GitHub Codespaces, Binder, local setup) converging on standardized configurations. The Python stack maintains parallel PyTorch and TensorFlow ecosystems with a shared foundation (`numpy`, `scikit-learn`, `opencv`, etc.) [README.md:10-10]().

**Sources:** [README.md:10-10](), [index.html:1-29]()

## Lesson Structure Pattern

For details on the pedagogical approach involving pre/post quizzes, Jupyter notebooks, hands-on labs, and Microsoft Learn integration, see [Learning Approach](#1.2).

**Sources:** [README.md:15-75]()

## Quiz Assessment System

The quiz system is a standalone Vue.js single-page application deployed independently from the main curriculum:

```mermaid
graph LR
    SOURCE["questions-en.txt"]
    JSON["lesson-X.json"]
    INDEX["index.js"]
    APP["App.vue"]
    HOME["Home.vue"]
    QUIZ["Quiz.vue"]
    
    SOURCE -.conversion.-> JSON
    JSON --> INDEX
    INDEX --> APP
    APP --> HOME
    APP --> QUIZ
```

Quizzes are identified by numeric IDs: pre-lecture quizzes use IDs 1-24, post-lecture quizzes use IDs 25-48 [lessons/1-Intro/README.md:7-7](), [lessons/5-NLP/15-LanguageModeling/README.md:5-33]().

**Sources:** [lessons/1-Intro/README.md:7-7](), [lessons/5-NLP/15-LanguageModeling/README.md:5-33]()

## Internationalization Architecture

```mermaid
graph LR
    EN_README["README.md"]
    EN_LESSONS["lessons/README.md"]
    GH_ACTION["Co-op Translator Action"]
    TRANS_README["translations/README.md"]
    
    EN_README --> GH_ACTION
    EN_LESSONS --> GH_ACTION
    GH_ACTION --> TRANS_README
```

The Co-op Translator service automatically generates and maintains translations across 50+ languages [README.md:24-52]().

**Sources:** [README.md:24-52]()

## Key Design Patterns

### Pedagogical Code Duplication
The repository intentionally duplicates utility code across lessons to maintain lesson independence. For example, `torchnlp.py` appears identically across multiple NLP lessons rather than being centralized, prioritizing lesson portability and self-containment [lessons/5-NLP/15-LanguageModeling/README.md:1-43]().

### Framework Parity
Most lessons maintain strict parity between PyTorch and TensorFlow implementations, covering identical concepts with framework-specific syntax [README.md:61-75]().

**Sources:** [README.md:61-75](), [lessons/5-NLP/15-LanguageModeling/README.md:1-43]()

## Community and Support Resources

| Resource | Purpose | Link Pattern |
|----------|---------|--------------|
| **Microsoft Foundry Discord** | Learner community, Q&A | `discord.gg/nTYy5BXMWG` [README.md:13-13]() |
| **Microsoft Learn Collections** | Supplementary learning paths | `learn.microsoft.com/en-us/collections/...` [README.md:74-74]() |

**Sources:** [README.md:13-13](), [README.md:74-74]()

## Repository Statistics
- **Total Lessons:** 24 lessons across 12 weeks [README.md:15-21]()
- **Languages:** 50+ translations via automated GitHub Actions [README.md:24-52]()
- **License:** MIT [README.md:1-1]()

**Sources:** [README.md:1-1](), [README.md:15-21](), [README.md:24-52]()

---

