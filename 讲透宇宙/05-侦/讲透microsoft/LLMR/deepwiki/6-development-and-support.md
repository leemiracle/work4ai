<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/LLMR · page 6 Development and Support · fetched 2026-10-26 -->

# Development and Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)

</details>



This page provides essential resources for developers working with or contributing to the LLMR (Large Language Model for Mixed Reality) project. It covers how to get support, report issues, understand the development process, and access necessary resources. For specific contribution guidelines, see [Contributing Guidelines](#6.1), and for solutions to common problems, refer to [Troubleshooting](#6.2).

## Support Channels

The LLMR project uses GitHub Issues as the primary channel for tracking bugs and feature requests. Before filing new issues, search existing ones to avoid duplicates.

### Issue Management Workflow

```mermaid
flowchart TD
    A["Issue Discovery"] --> B{"Already Exists?"}
    B -->|"Yes"| C["Comment on Existing Issue"]
    B -->|"No"| D["Create New Issue"]
    D --> E["Issue Triage"]
    E --> F{"Issue Type"}
    F -->|"Bug"| G["Bug Investigation"]
    F -->|"Feature Request"| H["Feature Evaluation"]
    F -->|"Question"| I["Community Support"]
    G --> J["Resolution"]
    H --> J
    I --> J
```

Sources: [SUPPORT.md:3-7]()

## Security Vulnerability Reporting

Security vulnerabilities should not be reported through public GitHub issues. Instead, follow the established security reporting process.

### Security Reporting Process

```mermaid
flowchart TD
    A["Security Vulnerability Discovery"] --> B["Report to Microsoft Security Response Center"]
    B --> C{"Reporting Method"}
    C -->|"Web Portal"| D["https://msrc.microsoft.com/create-report"]
    C -->|"Email"| E["secure@microsoft.com"]
    D --> F["MSRC Triage"]
    E --> F
    F --> G["Vulnerability Assessment"]
    G --> H["Fix Development"]
    H --> I["Coordinated Disclosure"]
```

Sources: [SECURITY.md:9-29]()

## LLMR Development Environment

To contribute to LLMR, you'll need to set up a proper development environment with the following components:

```mermaid
flowchart TD
    A["Development Prerequisites"] --> B["Unity Environment"]
    A --> C["Git & GitHub"]
    A --> D["API Access"]
    
    B --> B1["Unity Editor"]
    B --> B2["Microsoft.CodeAnalysis (Roslyn)"]
    B --> B3["com.siccity.gltfutility"]
    B --> B4["com.openai.unity"]
    
    C --> C1["Git Client"]
    C --> C2["GitHub Account"]
    
    D --> D1["OpenAI API Key"]
    D --> D2["Sketchfab API Key"]
    
    B1 --> E["LLMR Repository Clone"]
    C1 --> E
    E --> F["Project Setup"]
    F --> G["API Configuration"]
    D1 --> G
    D2 --> G
    G --> H["Development Ready"]
```

## License Information

LLMR is licensed under the MIT License, which is a permissive open-source license.

### MIT License Key Components

```mermaid
flowchart TD
    A["MIT License"] --> B["Rights Granted"]
    A --> C["Conditions"]
    A --> D["Limitations"]
    
    B --> B1["Use"]
    B --> B2["Copy"]
    B --> B3["Modify"]
    B --> B4["Merge"]
    B --> B5["Publish"]
    B --> B6["Distribute"]
    B --> B7["Sublicense"]
    B --> B8["Sell"]
    
    C --> C1["Include License Notice"]
    C --> C2["Include Copyright Notice"]
    
    D --> D1["No Liability"]
    D --> D2["No Warranty"]
```

Sources: [LICENSE:1-21]()

## Support Resources Matrix

Below is a matrix of support resources available for different LLMR components:

| Component | Primary Support Channel | Secondary Resources |
|-----------|-------------------------|---------------------|
| Core Framework | GitHub Issues | Project Documentation |
| OpenAI Integration | GitHub Issues | OpenAI Documentation |
| Unity Components | GitHub Issues | Unity Forums |
| Sketchfab Integration | GitHub Issues | Sketchfab Documentation |
| Flask Application | GitHub Issues | Flask Documentation |
| Setup Issues | GitHub Issues | [Troubleshooting Guide](#6.2) |

Sources: [SUPPORT.md:3-11]()

## System Components for Developers

Understanding the LLMR system architecture is crucial for effective development. The following diagram shows the key components that developers will interact with.

### LLMR Component Architecture

```mermaid
flowchart TD
    A["LLMR Developer"] --> B["Unity Components"]
    A --> C["Python Components"]
    A --> D["External Services"]
    
    B --> B1["Orchestration System"]
    B --> B2["Planner"]
    B --> B3["Builder"]
    B --> B4["Inspector"]
    B --> B5["SketchfabLoader"]
    
    C --> C1["Flask Application"]
    C1 --> C2["DALL-E Integration"]
    C1 --> C3["CLIP Model"]
    C1 --> C4["Sketchfab API Client"]
    
    D --> D1["OpenAI API"]
    D --> D2["Sketchfab API"]
```

## Contribution Process Flow

The following diagram illustrates the detailed process flow for contributing to LLMR:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant GH as "GitHub"
    participant CI as "CI/CD Pipeline"
    participant MR as "Maintainer"
    
    Dev->>GH: Fork Repository
    Dev->>Dev: Create Feature Branch
    Dev->>Dev: Implement Changes
    Dev->>Dev: Run Local Tests
    Dev->>GH: Push Changes
    Dev->>GH: Create Pull Request
    GH->>CI: Trigger CI Pipeline
    CI->>GH: Report Test Results
    GH->>MR: Request Review
    
    alt Review Outcome
        MR->>GH: Approve Changes
        GH->>GH: Merge Changes
    else Needs Revision
        MR->>Dev: Request Changes
        Dev->>Dev: Address Feedback
        Dev->>GH: Update PR
        GH->>MR: Re-Review
    end
```

## API Integration in LLMR

The following diagram illustrates how LLMR components interact with external APIs:

```mermaid
sequenceDiagram
    participant Unity as "Unity Environment"
    participant Config as "API Configuration"
    participant OpenAI as "OpenAI API"
    participant Flask as "Flask Application"
    participant Sketchfab as "Sketchfab API"
    
    Unity->>Config: Read API Keys
    Unity->>OpenAI: Send Prompt for Code Generation
    OpenAI->>Unity: Return Generated Code
    
    Unity->>Flask: Request 3D Model
    Flask->>OpenAI: Generate Reference Image with DALL-E
    OpenAI->>Flask: Return Reference Image
    Flask->>Sketchfab: Search Models
    Sketchfab->>Flask: Return Model Candidates
    Flask->>Flask: CLIP Similarity Comparison
    Flask->>Unity: Return Best Match UID
    Unity->>Sketchfab: Download Model
    Sketchfab->>Unity: Return Model Data
```

---

