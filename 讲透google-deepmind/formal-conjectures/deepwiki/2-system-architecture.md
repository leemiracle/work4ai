<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/formal-conjectures · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
- [.gitpod.yml](.gitpod.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [FormalConjectures/Util/Answer.lean](FormalConjectures/Util/Answer.lean)
- [FormalConjectures/Util/Attributes.lean](FormalConjectures/Util/Attributes.lean)
- [FormalConjectures/Util/Attributes/AMS.lean](FormalConjectures/Util/Attributes/AMS.lean)
- [FormalConjectures/Util/Attributes/AttributesTest.lean](FormalConjectures/Util/Attributes/AttributesTest.lean)
- [FormalConjectures/Wikipedia/HadwigerNelson.lean](FormalConjectures/Wikipedia/HadwigerNelson.lean)
- [README.md](README.md)

</details>



This document provides a technical overview of the FormalConjectures system architecture, focusing on the core infrastructure components, categorization mechanisms, and quality control systems that enable formalized mathematical conjecture collection and validation. For information about specific mathematical problem collections, see [Mathematical Problem Collections](#3). For installation and setup procedures, see [Getting Started](#1.1).

## Core Infrastructure Components

The FormalConjectures system is built around several key infrastructure components that work together to enable mathematical conjecture formalization in Lean 4.

### Architecture Overview

```mermaid
graph TB
    subgraph "Core Elaboration System"
        answerElab["answerElab TermElab"]
        AnswerInfo["AnswerInfo Structure"]
        getAnswers["getAnswers Function"]
    end
    
    subgraph "Attribute Management"
        CategoryTag["CategoryTag Structure"]
        SubjectTag["SubjectTag Structure"] 
        categoryExt["categoryExt Environment Extension"]
        subjectExt["subjectExt Environment Extension"]
    end
    
    subgraph "AMS Classification System"
        AMS["AMS Inductive Type"]
        numToAMSName["numToAMSName Function"]
        AMSCommand["#AMS Command"]
    end
    
    subgraph "Problem Import System"
        ProblemImports["ProblemImports Module"]
        UtilAttributes["Util.Attributes Module"]
        UtilAnswer["Util.Answer Module"]
    end
    
    subgraph "Mathematical Content"
        Wikipedia["Wikipedia Directory"]
        Arxiv["Arxiv Directory"] 
        Erdos["ErdosProblems Directory"]
        ForMathlib["ForMathlib Directory"]
    end
    
    answerElab --> AnswerInfo
    AnswerInfo --> getAnswers
    CategoryTag --> categoryExt
    SubjectTag --> subjectExt
    AMS --> numToAMSName
    numToAMSName --> AMSCommand
    
    UtilAttributes --> CategoryTag
    UtilAttributes --> SubjectTag
    UtilAnswer --> answerElab
    ProblemImports --> Wikipedia
    ProblemImports --> Arxiv
    ProblemImports --> Erdos
    
    Wikipedia --> categoryExt
    Arxiv --> categoryExt
    Erdos --> categoryExt
    ForMathlib --> Wikipedia
```

Sources: [README.md:119-126](), [FormalConjectures/Util/Attributes.lean:19-301](), [FormalConjectures/Util/Answer.lean:17-72]()

### The answer() Elaboration System

The `answer()` elaborator provides syntax for marking placeholder answers in mathematical problem statements where the solution requires a specific value or term.

```mermaid
graph LR
    subgraph "Elaboration Pipeline"
        AnswerSyntax["answer($term) Syntax"]
        answerElab["answerElab TermElab"]
        SaveInfo["mkSaveInfoAnnotation"]
        PostponeElab["postponeElabTerm"]
    end
    
    subgraph "Information Extraction"
        InfoTree["InfoTree Inspection"]
        getAnswers["getAnswers Function"]
        AnswerInfo["AnswerInfo Structure"]
        Format["AnswerInfo.format"]
    end
    
    AnswerSyntax --> answerElab
    answerElab --> SaveInfo
    answerElab --> PostponeElab
    SaveInfo --> InfoTree
    InfoTree --> getAnswers
    getAnswers --> AnswerInfo
    AnswerInfo --> Format
```

The elaborator processes terms of the form `answer(sorry)`, `answer(True)`, or `answer(False)` and preserves them for later extraction and analysis. The `AnswerInfo` structure stores both the elaborated term and its context for statistical and documentation purposes.

Sources: [FormalConjectures/Util/Answer.lean:37-72](), [README.md:189-219]()

## Problem Categorization System

The categorization system uses Lean 4 attributes to classify mathematical problems by research status and subject area, with persistent storage in environment extensions.

### Category Classification Architecture

```mermaid
graph TD
    subgraph "Category Attribute Processing"
        CategorySyntax["CategorySyntax Grammar"]
        toCategory["Syntax.toCategory Function"]
        Category["Category Inductive Type"]
        ProblemStatus["ProblemStatus Inductive Type"]
    end
    
    subgraph "AMS Subject Processing"
        SubjectList["subjectList Grammar"]
        toSubjects["Syntax.toSubjects Function"]
        AMS_Type["AMS Inductive Type"]
        numToAMSName["numToAMSName Function"]
    end
    
    subgraph "Persistent Storage"
        CategoryTag["CategoryTag Structure"]
        SubjectTag["SubjectTag Structure"]
        categoryExt["categoryExt Environment Extension"]
        subjectExt["subjectExt Environment Extension"]
    end
    
    subgraph "Statistics and Retrieval"
        getTags["getTags Function"]
        getStatementTags["getStatementTags Function"]
        getCategoryStats["getCategoryStats Function"]
        getSubjectTags["getSubjectTags Function"]
    end
    
    CategorySyntax --> toCategory
    toCategory --> Category
    Category --> ProblemStatus
    Category --> CategoryTag
    
    SubjectList --> toSubjects
    toSubjects --> AMS_Type
    AMS_Type --> numToAMSName
    AMS_Type --> SubjectTag
    
    CategoryTag --> categoryExt
    SubjectTag --> subjectExt
    
    categoryExt --> getTags
    getTags --> getStatementTags
    getStatementTags --> getCategoryStats
    subjectExt --> getSubjectTags
```

The system supports the following category classifications:
- `research open`: Unsolved mathematical problems
- `research solved`: Problems with accepted informal solutions  
- `graduate`, `undergraduate`, `high_school`: Educational level problems
- `test`: Sanity check statements
- `API`: Basic theory construction statements

Sources: [FormalConjectures/Util/Attributes.lean:94-301](), [README.md:129-188]()

### AMS Subject Classification

The AMS (American Mathematical Society) subject classification system maps numerical codes to mathematical subject areas using an inductive type with 54 constructors.

| AMS Code | Subject Area | Constructor |
|----------|--------------|-------------|
| 11 | Number theory | `AMS.«11»` |
| 52 | Convex and discrete geometry | `AMS.«52»` |
| 15 | Linear and multilinear algebra | `AMS.«15»` |
| 5 | Combinatorics | `AMS.«5»` |
| 33 | Special functions | `AMS.«33»` |

The `#AMS` command provides interactive access to all available subject classifications within Lean files.

Sources: [FormalConjectures/Util/Attributes/AMS.lean:39-196](), [FormalConjectures/Util/Attributes/AttributesTest.lean:104-105]()

## Quality Control Pipeline

The quality control system enforces consistent metadata, formatting, and build validation across all conjecture formalizations.

### Validation Workflow

```mermaid
graph TD
    subgraph "Source Validation"
        FileHeader["Copyright Header Check"]
        CategoryCheck["Category Attribute Check"]
        AMSCheck["AMS Attribute Check"]
        AnswerCheck["answer() Syntax Check"]
    end
    
    subgraph "Linting System"
        CategoryLinter["Category Linter"]
        AMSLinter["AMS Linter"] 
        CopyrightLinter["Copyright Linter"]
        addLinter["addLinter Registration"]
    end
    
    subgraph "Build Validation"
        LakeBuild["lake build"]
        DocGeneration["doc-gen4 Processing"]
        StatExtraction["Statistics Extraction"]
    end
    
    subgraph "Documentation Pipeline"
        GitHubActions["GitHub Actions Workflow"]
        GitHubPages["GitHub Pages Deployment"]
        StatsGeneration["Statistics Generation"]
    end
    
    FileHeader --> CopyrightLinter
    CategoryCheck --> CategoryLinter
    AMSCheck --> AMSLinter
    AnswerCheck --> LakeBuild
    
    CategoryLinter --> addLinter
    AMSLinter --> addLinter
    CopyrightLinter --> addLinter
    addLinter --> LakeBuild
    
    LakeBuild --> DocGeneration
    DocGeneration --> StatExtraction
    StatExtraction --> StatsGeneration
    StatsGeneration --> GitHubActions
    GitHubActions --> GitHubPages
```

Each conjecture file must include:
1. Apache 2.0 copyright header as specified in [README.md:250-267]()
2. At least one `@[AMS n]` subject classification attribute
3. One `@[category type]` classification attribute
4. Proper `answer(sorry/True/False)` syntax for questions requiring specific answers

Sources: [README.md:220-267](), [.github/workflows/build-and-docs.yml (inferred)]()

## Mathematical Content Organization

The repository organizes mathematical content using a source-based directory structure that separates conjectures by their origin and provides extensions for mathlib integration.

### Directory Structure Mapping

```mermaid
graph TB
    subgraph "Source-Based Organization"
        Wikipedia_Dir["FormalConjectures/Wikipedia/"]
        Arxiv_Dir["FormalConjectures/Arxiv/"] 
        Erdos_Dir["FormalConjectures/ErdosProblems/"]
        MathOverflow_Dir["FormalConjectures/MathOverflow/"]
        Other_Dir["FormalConjectures/Other/"]
    end
    
    subgraph "Infrastructure Directories"
        Util_Dir["FormalConjectures/Util/"]
        ForMathlib_Dir["FormalConjectures/ForMathlib/"]
    end
    
    subgraph "Core Utilities"
        Attributes_Module["Util/Attributes.lean"]
        Answer_Module["Util/Answer.lean"]
        ProblemImports_Module["Util/ProblemImports.lean"]
    end
    
    subgraph "Mathlib Extensions"
        LinearAlgebra_Ext["ForMathlib/LinearAlgebra/"]
        Combinatorics_Ext["ForMathlib/Combinatorics/"]
        DataTypes_Ext["ForMathlib/Data/"]
    end
    
    subgraph "Example Content"
        HadwigerNelson["Wikipedia/HadwigerNelson.lean"]
        UnitDistancePlaneGraph["UnitDistancePlaneGraph Definition"]
        HadwigerNelsonProblem["HadwigerNelsonProblem Theorem"]
    end
    
    Util_Dir --> Attributes_Module
    Util_Dir --> Answer_Module
    Util_Dir --> ProblemImports_Module
    
    ForMathlib_Dir --> LinearAlgebra_Ext
    ForMathlib_Dir --> Combinatorics_Ext
    ForMathlib_Dir --> DataTypes_Ext
    
    Wikipedia_Dir --> HadwigerNelson
    HadwigerNelson --> UnitDistancePlaneGraph
    HadwigerNelson --> HadwigerNelsonProblem
    
    ProblemImports_Module --> Wikipedia_Dir
    ProblemImports_Module --> Arxiv_Dir
    ProblemImports_Module --> Erdos_Dir
    
    LinearAlgebra_Ext --> Wikipedia_Dir
    Combinatorics_Ext --> Erdos_Dir
```

The `ForMathlib` directory contains mathematical definitions and theorems intended for eventual upstreaming to mathlib, following mathlib's directory structure conventions. This allows the repository to include necessary definitions without waiting for mathlib releases.

Sources: [README.md:114-126](), [README.md:272-280](), [FormalConjectures/Wikipedia/HadwigerNelson.lean:27-70]()

### Build and Development Environment

The system supports multiple development environments through standardized configuration:

- **Gitpod**: Cloud-based development with automatic cache retrieval and build
- **DevContainer**: Local containerized development environment  
- **Local Setup**: Traditional `lake exe cache get` and `lake build` workflow

All environments use the `leanprovercommunity/gitpod4` base image and include automatic Lean 4 extension installation and mathlib cache management.

Sources: [.gitpod.yml:1-14](), [.devcontainer/devcontainer.json:1-17](), [README.md:104-113]()

---

