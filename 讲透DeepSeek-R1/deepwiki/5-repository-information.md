> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-R1/5-repository-information](https://deepwiki.com/deepseek-ai/DeepSeek-R1/5-repository-information)
> DeepWiki deepseek-ai/DeepSeek-R1

# Repository Information

  Relevant source files 
 - [.github/workflows/stale.yml](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/.github/workflows/stale.yml)
 - [LICENSE](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/LICENSE)
 - [README.md](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1)
 
  This page provides detailed information about the DeepSeek-R1 repository structure, organization, license details, and contribution guidelines. It serves as a reference for understanding how the codebase is organized and managed. For information about the models themselves, see [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-R1/2-model-architecture) and for usage details, see [Model Usage](https://deepwiki.com/deepseek-ai/DeepSeek-R1/3-model-usage).

 
## Repository Overview

 The DeepSeek-R1 repository is primarily focused on providing access to a family of reasoning-specialized language models, including documentation, evaluation benchmarks, and deployment instructions. The repository does not contain the actual model code implementation, which is instead referenced through the DeepSeek-V3 repository for the base models.

 **Repository Structure Diagram**

 
```

```

 Sources: [README.md1-29](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1#L1-L29)

 
## Main Repository Components

 The repository consists of the following primary components:

 
| Component | Description | Purpose |
|---|---|---|
| README.md | Main documentation file | Provides comprehensive information about models, usage, and benchmarks |
| LICENSE | MIT License file | Details the licensing terms for the repository and models |
| .github directory | GitHub-specific files | Contains workflows for repository management |
| figures directory | Image resources | Contains benchmark visualizations and other graphics |
| DeepSeek_R1.pdf | Technical paper | Provides in-depth technical details about model architecture and training |

 Sources: [README.md1-29](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1#L1-L29)

 
### Documentation Organization

 The main documentation is contained in the README.md file, which is organized into the following sections:

 
 - Introduction
 - Model Summary
 - Model Downloads
 - Evaluation Results
 - Chat Website & API Platform
 - How to Run Locally
 - License
 - Citation
 - Contact
 
 This structure provides a comprehensive guide for users to understand, download, and use the DeepSeek-R1 models.

 Sources: [README.md31-277](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1#L31-L277)

 
## Issue Management

 The repository includes an automated system for managing GitHub issues to maintain an organized and responsive project.

 **Issue Management Workflow Diagram**

 
```

```

 Sources: [.github/workflows/stale.yml1-31](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/.github/workflows/stale.yml#L1-L31)

 
### Stale Issue Management

 The repository uses GitHub's stale action to automatically manage inactive issues:

 
 - Issues are marked as stale after 30 days of inactivity
 - Stale issues receive an automated comment notifying contributors
 - Issues are closed after 14 additional days of inactivity
 - Issues with "pinned" or "security" labels are exempt from the stale process
 - Pull requests are not subject to the stale workflow (configured with -1 days)
 
 This automation helps maintain a clean issue tracker by focusing attention on active issues.

 Sources: [.github/workflows/stale.yml12-30](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/.github/workflows/stale.yml#L12-L30)

 
## License Information

 The DeepSeek-R1 repository is released under the MIT License, which provides generous permissions for use, modification, and distribution.

 **License Terms Diagram**

 
```

```

 Sources: [LICENSE1-21](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/LICENSE#L1-L21) [README.md256-261](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1#L256-L261)

 
### License Details

 The MIT License grants the following permissions:

 
 - Freedom to use the software for any purpose
 - Freedom to modify, distribute, and sell the software
 - Permission to use the software in both private and commercial settings
 
 The only requirements are to include the original copyright notice and permission notice in all copies or substantial portions of the software.

 The license explicitly states that the software is provided "as is," without warranty of any kind, and the authors or copyright holders are not liable for any claims, damages, or liabilities.

 Sources: [LICENSE1-21](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/LICENSE#L1-L21)

 
### Model-Specific Licensing

 While the repository itself is under the MIT License, some of the distilled models have different base license considerations:

 
 - **DeepSeek-R1-Distill-Qwen Models** (1.5B, 7B, 14B, 32B):

 
 - Derived from Qwen-2.5 series
 - Original Qwen-2.5 models are licensed under Apache 2.0 License
 - Finetuned with 800k samples curated with DeepSeek-R1
 - **DeepSeek-R1-Distill-Llama Models**:

 
 - DeepSeek-R1-Distill-Llama-8B is derived from Llama3.1-8B-Base
 - DeepSeek-R1-Distill-Llama-70B is derived from Llama3.3-70B-Instruct
 - Subject to the respective Llama3.1 and Llama3.3 licenses
 
 All models support commercial use and allow for modifications and derivative works, including distillation for training other LLMs.

 Sources: [README.md256-261](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1#L256-L261)

 
## Repository File Organization

 The DeepSeek-R1 repository has a relatively simple structure with few directories:

 
```

```

 Sources: [README.md1-29](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1#L1-L29)

 Note that the actual model code and implementation is not contained within this repository. Users seeking to run the DeepSeek-R1 models locally are directed to the DeepSeek-V3 repository for implementation details.

 Sources: [README.md78-79](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1#L78-L79) [README.md166-168](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561/README.md?plain=1#L166-L168)
