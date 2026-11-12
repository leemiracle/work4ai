<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-R1 · page 5 Repository Information · fetched 2026-10-30 -->

# Repository Information

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/stale.yml](.github/workflows/stale.yml)
- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This page provides detailed information about the DeepSeek-R1 repository structure, organization, license details, and contribution guidelines. It serves as a reference for understanding how the codebase is organized and managed. For information about the models themselves, see [Model Architecture](#2) and for usage details, see [Model Usage](#3).

## Repository Overview

The DeepSeek-R1 repository is primarily focused on providing access to a family of reasoning-specialized language models, including documentation, evaluation benchmarks, and deployment instructions. The repository does not contain the actual model code implementation, which is instead referenced through the DeepSeek-V3 repository for the base models.

**Repository Structure Diagram**

```mermaid
graph TD
    subgraph Repository["DeepSeek-R1 Repository Structure"]
        README["README.md\nMain documentation and model overview"]
        LICENSE["LICENSE\nMIT License"]
        GitHubDir[".github directory\nContains GitHub workflows"]
        FiguresDir["figures directory\nBenchmark images"]
        Paper["DeepSeek_R1.pdf\nDetailed technical paper"]
    end
    
    GitHubDir --> WorkflowsDir["workflows directory\nAutomation scripts"]
    WorkflowsDir --> StaleYml["stale.yml\nStale issue management workflow"]
    
    FiguresDir --> BenchmarkImg["benchmark.jpg\nBenchmark performance visualization"]
    
    README --> |"references"| Paper
    README --> |"includes"| BenchmarkImg
```

Sources: [README.md:1-29]()

## Main Repository Components

The repository consists of the following primary components:

| Component | Description | Purpose |
|-----------|-------------|---------|
| README.md | Main documentation file | Provides comprehensive information about models, usage, and benchmarks |
| LICENSE | MIT License file | Details the licensing terms for the repository and models |
| .github directory | GitHub-specific files | Contains workflows for repository management |
| figures directory | Image resources | Contains benchmark visualizations and other graphics |
| DeepSeek_R1.pdf | Technical paper | Provides in-depth technical details about model architecture and training |

Sources: [README.md:1-29]()

### Documentation Organization

The main documentation is contained in the README.md file, which is organized into the following sections:

1. Introduction
2. Model Summary
3. Model Downloads
4. Evaluation Results
5. Chat Website & API Platform
6. How to Run Locally
7. License
8. Citation
9. Contact

This structure provides a comprehensive guide for users to understand, download, and use the DeepSeek-R1 models.

Sources: [README.md:31-277]()

## Issue Management

The repository includes an automated system for managing GitHub issues to maintain an organized and responsive project.

**Issue Management Workflow Diagram**

```mermaid
flowchart TD
    subgraph IssueLifecycle["GitHub Issue Lifecycle"]
        NewIssue["New Issue Created"]
        ActiveIssue["Active Issue"]
        StaleIssue["Stale Issue\nMarked with 'stale' label"]
        ClosedIssue["Closed Issue\nMarked with 'closed-as-stale' label"]
        ExemptIssue["Exempt Issue\nHas 'pinned' or 'security' label"]
    end
    
    NewIssue --> ActiveIssue
    ActiveIssue --> |"No activity for 30 days"| StaleIssue
    StaleIssue --> |"New comment\nor activity"| ActiveIssue
    StaleIssue --> |"No activity for 14 more days"| ClosedIssue
    ActiveIssue --> |"Has exempt label"| ExemptIssue
    ExemptIssue --> |"Exempt label removed"| ActiveIssue
    
    subgraph WorkflowExecution["Workflow Execution"]
        Schedule["Scheduled daily\nCron: 0 0 * * *"]
        Manual["Manual trigger\nWorkflow dispatch"]
        GHAction["GitHub Action\nactions/stale@v9"]
    end
    
    Schedule --> GHAction
    Manual --> GHAction
    GHAction --> |"processes"| IssueLifecycle
```

Sources: [.github/workflows/stale.yml:1-31]()

### Stale Issue Management

The repository uses GitHub's stale action to automatically manage inactive issues:

- Issues are marked as stale after 30 days of inactivity
- Stale issues receive an automated comment notifying contributors
- Issues are closed after 14 additional days of inactivity
- Issues with "pinned" or "security" labels are exempt from the stale process
- Pull requests are not subject to the stale workflow (configured with -1 days)

This automation helps maintain a clean issue tracker by focusing attention on active issues.

Sources: [.github/workflows/stale.yml:12-30]()

## License Information

The DeepSeek-R1 repository is released under the MIT License, which provides generous permissions for use, modification, and distribution.

**License Terms Diagram**

```mermaid
flowchart TD
    subgraph LicenseTerms["MIT License Terms"]
        Rights["Permissions Granted\n- Use\n- Copy\n- Modify\n- Merge\n- Publish\n- Distribute\n- Sublicense\n- Sell"]
        Conditions["Conditions\n- Include copyright notice\n- Include permission notice"]
        Limitations["Limitations\n- No warranty\n- No liability"]
    end
    
    subgraph ModelLicenses["Model-Specific Licensing"]
        DeepSeekR1["DeepSeek-R1 & R1-Zero\nMIT License"]
        DistilledQwen["DeepSeek-R1-Distill-Qwen Models\nDerived from Qwen-2.5 (Apache 2.0)"]
        DistilledLlama8B["DeepSeek-R1-Distill-Llama-8B\nDerived from Llama3.1-8B-Base"]
        DistilledLlama70B["DeepSeek-R1-Distill-Llama-70B\nDerived from Llama3.3-70B-Instruct"]
    end
    
    LicenseTerms --> DeepSeekR1
    DeepSeekR1 --> |"used to finetune"| DistilledQwen
    DeepSeekR1 --> |"used to finetune"| DistilledLlama8B
    DeepSeekR1 --> |"used to finetune"| DistilledLlama70B
```

Sources: [LICENSE:1-21](), [README.md:256-261]()

### License Details

The MIT License grants the following permissions:

- Freedom to use the software for any purpose
- Freedom to modify, distribute, and sell the software
- Permission to use the software in both private and commercial settings

The only requirements are to include the original copyright notice and permission notice in all copies or substantial portions of the software.

The license explicitly states that the software is provided "as is," without warranty of any kind, and the authors or copyright holders are not liable for any claims, damages, or liabilities.

Sources: [LICENSE:1-21]()

### Model-Specific Licensing

While the repository itself is under the MIT License, some of the distilled models have different base license considerations:

1. **DeepSeek-R1-Distill-Qwen Models** (1.5B, 7B, 14B, 32B):
   - Derived from Qwen-2.5 series
   - Original Qwen-2.5 models are licensed under Apache 2.0 License
   - Finetuned with 800k samples curated with DeepSeek-R1

2. **DeepSeek-R1-Distill-Llama Models**:
   - DeepSeek-R1-Distill-Llama-8B is derived from Llama3.1-8B-Base
   - DeepSeek-R1-Distill-Llama-70B is derived from Llama3.3-70B-Instruct
   - Subject to the respective Llama3.1 and Llama3.3 licenses

All models support commercial use and allow for modifications and derivative works, including distillation for training other LLMs.

Sources: [README.md:256-261]()

## Repository File Organization

The DeepSeek-R1 repository has a relatively simple structure with few directories:

```mermaid
graph TD
    subgraph RepoRoot["DeepSeek-R1 Repository Root"]
        RootFiles["Root Files\n- README.md\n- LICENSE\n- DeepSeek_R1.pdf"]
        DotGitHub[".github directory"]
        Figures["figures directory"]
    end
    
    DotGitHub --> Workflows["workflows\n- stale.yml"]
    
    Figures --> BenchmarkJPG["benchmark.jpg"]
    
    subgraph ContentCategories["Content Categories"]
        Documentation["Documentation\n- Model description\n- Benchmarks\n- Usage instructions"]
        LegalInfo["Legal Information\n- License\n- Citation"]
        Automation["Automation\n- GitHub workflows"]
        Resources["Resources\n- Benchmark figures\n- Technical paper"]
    end
    
    RootFiles --> Documentation
    RootFiles --> LegalInfo
    DotGitHub --> Automation
    Figures --> Resources
    RootFiles --> |"DeepSeek_R1.pdf"| Resources
```

Sources: [README.md:1-29]()

Note that the actual model code and implementation is not contained within this repository. Users seeking to run the DeepSeek-R1 models locally are directed to the DeepSeek-V3 repository for implementation details.

Sources: [README.md:78-79](), [README.md:166-168]()

---

