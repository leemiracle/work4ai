<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/samples-for-ai · page 6 Development Tools and Resources · fetched 2026-10-26 -->

# Development Tools and Resources

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/LandingPageContent.json](examples/LandingPageContent.json)
- [examples/LandingPageContent_zh-CN.json](examples/LandingPageContent_zh-CN.json)
- [examples/resourcePanel.vscode.json](examples/resourcePanel.vscode.json)
- [examples/resourcePanel.vscode.zh-cn.json](examples/resourcePanel.vscode.zh-cn.json)

</details>



## Purpose and Scope

This document covers the tools, integrations, and resource discovery systems that support the AI development workflow in the samples-for-ai repository. This includes the resource panel configurations for IDE integration, content management systems for developer resources, and mechanisms for discovering AI learning materials and popular projects.

For information about the automated installation and environment setup tools, see [Installation and Environment Setup](#2.1). For details about Visual Studio integration and development workflow, see [Visual Studio and Development Tools](#2.2). For information about the project metadata and categorization system, see [Project Catalog and Discovery](#6.1).

## Resource Panel System Architecture

The repository implements a resource panel system that provides curated AI learning resources directly within development environments. The system uses JSON-based configuration files to manage content across different IDEs and localization requirements.

```mermaid
graph TB
    subgraph "VS Code Integration"
        VSCODE["VS Code Editor"]
        RESOURCE_PANEL["Resource Panel Extension"]
    end
    
    subgraph "Configuration Files"
        VSCODE_EN["resourcePanel.vscode.json"]
        VSCODE_CN["resourcePanel.vscode.zh-cn.json"]
    end
    
    subgraph "Content Categories"
        AI_LEARNING["AI Learning Resources"]
        GITHUB_PROJECTS["Popular Github AI Projects"] 
        EXPLORE_MORE["Explore More"]
    end
    
    subgraph "External Resources"
        EDX_COURSE["EDX AI Course"]
        MS_BLOG["Microsoft AI Blog"]
        SNIPER_REPO["SNIPER Repository"]
        MACE_REPO["mace Repository"]
        ROBOSAT_REPO["robosat Repository"]
        TOOLS_AI_REPO["vscode-tools-for-ai"]
    end
    
    VSCODE --> RESOURCE_PANEL
    RESOURCE_PANEL --> VSCODE_EN
    RESOURCE_PANEL --> VSCODE_CN
    
    VSCODE_EN --> AI_LEARNING
    VSCODE_EN --> GITHUB_PROJECTS
    VSCODE_EN --> EXPLORE_MORE
    
    AI_LEARNING --> EDX_COURSE
    AI_LEARNING --> MS_BLOG
    GITHUB_PROJECTS --> SNIPER_REPO
    GITHUB_PROJECTS --> MACE_REPO
    GITHUB_PROJECTS --> ROBOSAT_REPO
    EXPLORE_MORE --> TOOLS_AI_REPO
```

The resource panel system uses a structured JSON format with event tracking capabilities. Each resource entry includes a `name`, `url`, and `event` field for analytics tracking:

| Field | Purpose | Example Value |
|-------|---------|---------------|
| `name` | Display text for the resource | "Curriculum about AI" |
| `url` | Target URL for the resource | "https://www.edx.org/microsoft-professional-program-artificial-intelligence" |
| `event` | Analytics event identifier | "homepage/openAICourse" |

**Sources:** [examples/resourcePanel.vscode.json:1-52](), [examples/resourcePanel.vscode.zh-cn.json:1-52]()

## Landing Page Content Management

The landing page content system provides a more comprehensive resource discovery interface with additional categorization and AI library listings. This system supports both the main landing page and localized versions.

```mermaid
graph LR
    subgraph "Landing Page System"
        LANDING_PAGE["Landing Page Interface"]
        RIGHT_PANE["RightPane Content"]
        AI_LIBRARIES["AILibraries Section"]
    end
    
    subgraph "Content Files"
        CONTENT_EN["LandingPageContent.json"]
        CONTENT_CN["LandingPageContent_zh-CN.json"]
    end
    
    subgraph "Content Structure"
        AI_RESOURCE["AI Resource Section"]
        POPULAR_GITHUB["Popular GitHub Projects"]
        EXPLORE_MORE_LP["Explore More Section"]
        LIBRARY_LIST["AI Library Listings"]
    end
    
    subgraph "Referenced Libraries"
        NUMPY["NumPy and Scipy"]
        JUPYTER["Jupyter Notebook"] 
        PANDAS["Pandas"]
        MATPLOTLIB["Matplotlib"]
        ML_FRAMEWORKS["ML Frameworks"]
    end
    
    LANDING_PAGE --> RIGHT_PANE
    LANDING_PAGE --> AI_LIBRARIES
    
    RIGHT_PANE --> CONTENT_EN
    RIGHT_PANE --> CONTENT_CN
    AI_LIBRARIES --> CONTENT_EN
    AI_LIBRARIES --> CONTENT_CN
    
    CONTENT_EN --> AI_RESOURCE
    CONTENT_EN --> POPULAR_GITHUB
    CONTENT_EN --> EXPLORE_MORE_LP
    CONTENT_EN --> LIBRARY_LIST
    
    LIBRARY_LIST --> NUMPY
    LIBRARY_LIST --> JUPYTER
    LIBRARY_LIST --> PANDAS
    LIBRARY_LIST --> MATPLOTLIB
    LIBRARY_LIST --> ML_FRAMEWORKS
```

The landing page content system organizes resources into distinct sections within the `RightPane` array structure. The `AILibraries` section specifically lists essential Python libraries and ML frameworks that developers need for AI development.

**Sources:** [examples/LandingPageContent.json:1-76](), [examples/LandingPageContent_zh-CN.json:1-82]()

## Resource Discovery and Navigation

The resource discovery system provides structured pathways for developers to access learning materials, explore popular projects, and dive deeper into specific AI technologies. The system implements a hierarchical navigation structure with consistent URL patterns.

### Learning Resource Categories

| Category | Description | Key Resources |
|----------|-------------|---------------|
| **AI Learning Resources** | Educational content and courses | EDX AI Program, Microsoft AI Blog |
| **Popular GitHub Projects** | Trending AI repositories | SNIPER, mace, robosat |
| **Exploration Paths** | Entry points to examples | First AI model tutorial, samples-for-ai repository |

The exploration section provides direct links to key starting points within the repository:

- First AI model training: [examples/tensorflow/MNIST]()
- Complete examples collection: [examples/]()
- Tools for AI documentation: Links to Visual Studio and VS Code extensions

**Sources:** [examples/LandingPageContent.json:39-57](), [examples/resourcePanel.vscode.json:37-51]()

## IDE Integration Architecture

The development tools system integrates with both Visual Studio and VS Code through dedicated extensions that provide contextual access to AI resources and examples.

```mermaid
graph TB
    subgraph "Developer Workflow"
        DEVELOPER["Developer"]
        IDE_CHOICE{"IDE Selection"}
    end
    
    subgraph "Visual Studio Integration"
        VS["Visual Studio"]
        VS_TOOLS["VS Tools for AI"]
        VS_LANDING["Landing Page Integration"]
    end
    
    subgraph "VS Code Integration" 
        VSCODE_IDE["VS Code"]
        VSCODE_EXTENSION["VS Code Tools for AI"]
        VSCODE_PANEL["Resource Panel"]
    end
    
    subgraph "Resource Configuration"
        CONFIG_SYSTEM["Configuration System"]
        LOCALIZATION["Localization Support"]
        EVENT_TRACKING["Event Tracking"]
    end
    
    subgraph "Content Delivery"
        WEB_RESOURCES["Web Resources"]
        GITHUB_REPOS["GitHub Repositories"] 
        LOCAL_EXAMPLES["Local Examples"]
    end
    
    DEVELOPER --> IDE_CHOICE
    IDE_CHOICE --> VS
    IDE_CHOICE --> VSCODE_IDE
    
    VS --> VS_TOOLS
    VS_TOOLS --> VS_LANDING
    
    VSCODE_IDE --> VSCODE_EXTENSION
    VSCODE_EXTENSION --> VSCODE_PANEL
    
    VS_LANDING --> CONFIG_SYSTEM
    VSCODE_PANEL --> CONFIG_SYSTEM
    
    CONFIG_SYSTEM --> LOCALIZATION
    CONFIG_SYSTEM --> EVENT_TRACKING
    
    CONFIG_SYSTEM --> WEB_RESOURCES
    CONFIG_SYSTEM --> GITHUB_REPOS
    CONFIG_SYSTEM --> LOCAL_EXAMPLES
```

### Event Tracking Implementation

The resource panel system implements analytics tracking through standardized event names:

| Event Pattern | Purpose | Example |
|---------------|---------|---------|
| `homepage/openAICourse` | Track course access | EDX AI curriculum clicks |
| `homepage/openAIBlog` | Track blog visits | Microsoft AI blog access |
| `homepage/openGithubProject` | Track project exploration | SNIPER, mace, robosat clicks |
| `homepage/openSamples4AIGithub` | Track samples repository access | samples-for-ai navigation |
| `homepage/openTools4AIGithub` | Track tools documentation access | Tools for AI repository visits |

**Sources:** [examples/resourcePanel.vscode.json:8-48](), [examples/resourcePanel.vscode.zh-cn.json:8-48]()

## Localization and International Support

The system provides comprehensive localization support with separate configuration files for different languages. The Chinese localization includes region-specific resources and culturally relevant content.

### Localization Differences

| Aspect | English Version | Chinese Version |
|--------|----------------|-----------------|
| **AI Courses** | EDX Microsoft Professional Program | Microsoft AI Course on Azure School (school.azure.cn) |
| **Video Resources** | Not specified | Bilibili video tutorials |
| **Blog Content** | Microsoft AI Blog | CNBlogs technical articles |
| **Resource Titles** | "AI Learning Resources" | "AI 学习资源" |

The Chinese version includes additional resources such as:
- Bilibili video tutorial: "AI 应用开发入门视频：看图识熊" 
- CNBlogs technical blog: "AI 应用开发入门博客：手写识别"

**Sources:** [examples/LandingPageContent_zh-CN.json:1-82](), [examples/resourcePanel.vscode.zh-cn.json:1-52]()

## AI Library and Framework Listings

The system maintains curated lists of essential AI development libraries and frameworks that developers should be familiar with. This serves both as a reference and as a checklist for environment setup.

### Core Libraries Categorization

```mermaid
graph TD
    subgraph "AI Development Stack"
        SCIENTIFIC["Scientific Computing"]
        DEVELOPMENT["Development Environment"]
        DATA_SCIENCE["Data Science"]
        VISUALIZATION["Data Visualization"]
        ML_FRAMEWORKS_SECTION["ML Frameworks"]
    end
    
    subgraph "Library Categories"
        NUMPY_SCIPY["NumPy and Scipy"]
        JUPYTER_NB["Jupyter Notebook"]
        PANDAS_LIB["Pandas"]
        MATPLOTLIB_LIB["Matplotlib"]
        DEEP_LEARNING["Deep Learning Frameworks"]
    end
    
    subgraph "Framework Examples"
        CNTK_FW["CNTK"]
        TENSORFLOW_FW["TensorFlow"]
        PYTORCH_FW["PyTorch"] 
        CAFFE2_FW["Caffe2"]
    end
    
    SCIENTIFIC --> NUMPY_SCIPY
    DEVELOPMENT --> JUPYTER_NB
    DATA_SCIENCE --> PANDAS_LIB
    VISUALIZATION --> MATPLOTLIB_LIB
    ML_FRAMEWORKS_SECTION --> DEEP_LEARNING
    
    DEEP_LEARNING --> CNTK_FW
    DEEP_LEARNING --> TENSORFLOW_FW
    DEEP_LEARNING --> PYTORCH_FW
    DEEP_LEARNING --> CAFFE2_FW
```

The `AILibraries` section provides a comprehensive overview of the development stack, from foundational scientific computing libraries to advanced deep learning frameworks. This aligns with the automated installation capabilities documented in the installer system.

**Sources:** [examples/LandingPageContent.json:59-75](), [examples/LandingPageContent_zh-CN.json:65-81]()

---

