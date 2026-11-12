<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/OCR-Form-Tools · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.ja-jp.md](README.ja-jp.md)
- [README.md](README.md)
- [README.zh-cn.md](README.zh-cn.md)
- [docs/images/compose.png](docs/images/compose.png)
- [docs/images/keyboard-shortcuts-icon.png](docs/images/keyboard-shortcuts-icon.png)
- [docs/images/share-icon.png](docs/images/share-icon.png)
- [package.json](package.json)
- [src/common/utils.ts](src/common/utils.ts)
- [src/react/components/shell/appSurveyLink.scss](src/react/components/shell/appSurveyLink.scss)
- [src/react/components/shell/appSurveyLink.tsx](src/react/components/shell/appSurveyLink.tsx)
- [yarn.lock](yarn.lock)

</details>



This document provides a comprehensive introduction to the OCR Form Testing Tool (FOTT), explaining its purpose, core architecture, and fundamental capabilities. FOTT is an open-source labeling tool for Form Recognizer, part of the Form OCR Test Toolset, designed to allow users to label forms, train custom machine learning models, and extract key-value pairs from documents.

## Purpose and Scope

The OCR Form Testing Tool is primarily designed to facilitate the process of labeling form data, training custom models using Azure Form Recognizer, and extracting structured information from documents. It enables users to:

- Label forms in various formats (PDF, JPEG, TIFF)
- Train custom models using the labeled data
- Extract key-value pairs from forms using the trained models
- Compose multiple models to enhance extraction capabilities

For detailed instructions on using specific features, refer to other sections in this wiki which cover individual components in greater depth.

Sources: [README.md:9-30](), [package.json:1-15]()

## System Architecture Overview

The OCR Form Testing Tool is built as a React + Redux web application written in TypeScript. It can be run as either a web application, desktop application (using Electron), or deployed via Docker.

### High-Level Architecture

```mermaid
graph TD
    A["User Interface Layer"] --> B["State Management Layer"]
    B --> C["Service Layer"]
    C --> D["External Services"]
    
    subgraph "User Interface Layer"
        UI1["Editor Canvas"]
        UI2["Tag Input System"]
        UI3["Navigation & Routing"]
        UI4["Project Settings UI"]
    end
    
    subgraph "State Management Layer"
        SM1["Redux Store"]
        SM2["Application Actions"]
        SM3["Project Reducers"]
        SM4["Connection Reducers"]
    end
    
    subgraph "Service Layer"
        SV1["Project Service"]
        SV2["Asset Service"]
        SV3["Storage Providers"]
        SV4["Security Service"]
    end
    
    subgraph "External Services"
        ES1["Form Recognizer API"]
        ES2["Azure Blob Storage"]
    end
```

Sources: [README.md:22-30](), [package.json:16-53]()

### Core Components and Data Flow

```mermaid
flowchart LR
    subgraph "Content Providers"
        CP1["Azure Blob Storage"]
        CP2["Local Files (Desktop only)"]
    end
    
    subgraph "FOTT Application"
        UI["User Interface Components"]
        SM["State Management"]
        PS["Project Service"]
        AS["Asset Service"]
        CS["Connection Service"]
        SS["Security Service"]
        
        UI --> SM
        SM --> PS
        SM --> AS
        SM --> CS
        SM --> SS
        PS --> AS
        CS --> AS
    end
    
    subgraph "External Services"
        FR["Form Recognizer Service"]
    end
    
    CP1 --> AS
    CP2 --> AS
    AS --> FR
    PS --> FR
```

Sources: [README.md:31-62](), [src/common/utils.ts:93-124]()

## Key Features and Workflow

The OCR Form Testing Tool provides a structured workflow for document processing, model training, and prediction:

### Document Processing Workflow

```mermaid
flowchart LR
    A["Document Upload"] --> B["OCR Processing"]
    B --> C["Document Labeling"]
    C --> D["Model Training"]
    D --> E["Model Composition (Optional)"]
    E --> F["Form Analysis"]
    
    subgraph "Document Upload"
        A1["From Azure Blob Storage"]
        A2["From Local Files (desktop)"]
    end
    
    subgraph "OCR Processing"
        B1["Text Element Detection"]
        B2["Layout Analysis"]
        B3["Table Detection"]
    end
    
    subgraph "Document Labeling"
        C1["Region Selection"]
        C2["Tag Application"]
        C3["Tag Type Specification"]
        C4["Table Configuration"]
    end
    
    subgraph "Model Training"
        D1["Form Recognizer API Training"]
        D2["Model Evaluation"]
        D3["Model ID Generation"]
    end
    
    subgraph "Form Analysis"
        F1["Key-Value Extraction"]
        F2["Result Visualization"]
    end
```

Sources: [README.md:81-196]()

### Feature Overview

The system provides three main capabilities:

| Feature | Description | Components Involved |
|---------|-------------|---------------------|
| Labeling | Allows users to label text elements and tables in forms | Editor Canvas, Tag Input System, Asset Management |
| Training | Trains a custom model using Azure Form Recognizer with labeled data | Model Management, Form Recognizer Integration |
| Analysis | Uses trained models to analyze new documents and extract key-value pairs | Prediction System, Result Visualization |

Sources: [README.md:24-29](), [README.md:132-182]()

## System Components

### Security and Authentication

The system implements a security token mechanism for protecting sensitive information such as API keys and connection strings. Each project generates a unique security token that can be saved for later use. This token is used to encrypt sensitive project settings when stored.

```mermaid
sequenceDiagram
    participant User
    participant Project as "Project"
    participant SecurityToken as "Security Token"
    participant Storage as "Storage"
    
    User->>Project: Create new project
    Project->>SecurityToken: Generate security token
    User->>Project: Add connections/API keys
    Project->>SecurityToken: Encrypt sensitive data
    Project->>Storage: Store encrypted project
    
    Note over User,Storage: Later retrieval
    
    User->>Storage: Get project data
    User->>SecurityToken: Provide saved token
    Storage->>User: Return encrypted project
    User->>SecurityToken: Decrypt project data
    SecurityToken->>User: Return decrypted project settings
```

Sources: [src/common/utils.ts:93-124](), [README.md:120-132](), [README.md:196-215]()

### Connections and Project Management

The system uses a "Bring Your Own Data" approach, where users configure connections to their data sources. Currently, Azure Blob Storage is the primary supported provider. Projects are managed through project files that store configuration but encrypt sensitive information.

```mermaid
graph TD
    subgraph "Connections Management"
        CO1["Connection Service"]
        CO2["Storage Providers"]
        CO3["Connection Settings"]
    end
    
    subgraph "Project Management"
        PM1["Project Service"]
        PM2["Project Settings"]
        PM3["Project Security"]
    end
    
    subgraph "External Storage"
        ES1["Azure Blob Storage"]
        ES2["Local File System (Desktop)"]
    end
    
    CO1 --> CO2
    CO2 --> ES1
    CO2 --> ES2
    PM1 --> CO1
    PM1 --> PM2
    PM2 --> PM3
    PM3 --> CO3
```

Sources: [README.md:99-117](), [README.md:120-132](), [src/common/utils.ts:93-124]()

## Core UI Components

The user interface is organized into several key components that work together to provide the complete functionality:

```mermaid
graph TD
    subgraph "Main Application"
        App["App Component"]
        App --> NavBar["Navigation Bar"]
        App --> MainContent["Main Content Area"]
        App --> StatusBar["Status Bar"]
        
        MainContent --> HP["Home Page"]
        MainContent --> EP["Editor Page"]
        MainContent --> PP["Predict Page"]
        MainContent --> TP["Training Page"]
        MainContent --> CP["Compose Page"]
        MainContent --> SP["Settings Pages"]
        
        EP --> Canvas["Canvas Component"]
        EP --> TagPanel["Tag Panel"]
        EP --> Properties["Properties Panel"]
        
        Canvas --> ImageMap["Image Map"]
        Canvas --> RegionManager["Region Manager"]
        
        TagPanel --> TagList["Tag List"]
        TagPanel --> TagControls["Tag Controls"]
    end
```

Sources: [README.md:134-142]()

## State Management

The application uses Redux for state management, with a predictable unidirectional data flow:

```mermaid
flowchart LR
    subgraph "Redux State Management"
        A["UI Components"] -- "Dispatch Actions" --> B["Actions"]
        B --> C["Reducers"]
        C --> D["Store"]
        D -- "State Updates" --> A
    end
    
    subgraph "Application State"
        S1["Project State"]
        S2["Asset State"]
        S3["Connection State"]
        S4["Application Settings"]
    end
```

Sources: [README.md:22-23](), [package.json:35-47]()

## Technology Stack

The OCR Form Testing Tool is built using the following key technologies:

| Category | Technologies |
|----------|--------------|
| Frontend Framework | React, Redux |
| UI Components | Fluent UI, Bootstrap |
| State Management | Redux, Redux Thunk |
| Languages | TypeScript |
| Build Tools | Webpack, React Scripts |
| External Services | Azure Form Recognizer, Azure Blob Storage |
| Desktop Integration | Electron |
| Internationalization | react-localization |

Sources: [package.json:17-53](), [README.md:22-23]()

## Deployment Options

The OCR Form Testing Tool can be deployed in three ways:

1. **Web Application**: Hosted service accessible via HTTPS
2. **Desktop Application**: Using Electron for local usage with access to the file system
3. **Docker Container**: Containerized version for easy deployment

Additional features in the desktop application include:
- Support for local file system as storage provider
- Support for cross-domain resource requests

Sources: [README.md:43-83]()

## Internationalization Support

The application supports multiple languages, with built-in support for English, Chinese, and Japanese:

```mermaid
graph TD
    I18N["Internationalization System"]
    I18N --> EN["English (en-us)"]
    I18N --> ZH["Chinese (zh-cn)"]
    I18N --> JP["Japanese (ja-jp)"]
    
    I18N --> Interface["IAppStrings Interface"]
    Interface --> StringUtils["String Utilities"]
    StringUtils --> I1["interpolate()"]
    StringUtils --> I2["interpolateJson()"]
```

Sources: [README.md:257-258](), [README.zh-cn.md](), [README.ja-jp.md]()

## Conclusion

The OCR Form Testing Tool (FOTT) provides a complete solution for labeling forms, training custom Form Recognizer models, and extracting key-value pairs from documents. Its architecture is designed around React and Redux, with modular components that handle different aspects of the workflow. The tool supports multiple deployment options and provides a comprehensive UI for managing the entire process from document upload to analysis.

---

