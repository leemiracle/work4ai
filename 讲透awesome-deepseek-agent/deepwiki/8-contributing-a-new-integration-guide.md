> 来源: [https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/8-contributing-a-new-integration-guide](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/8-contributing-a-new-integration-guide)
> DeepWiki deepseek-ai/awesome-deepseek-agent

# Contributing a New Integration Guide

  Relevant source files 
 - [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/.github/PULL_REQUEST_TEMPLATE.md?plain=1)
 - [CONTRIBUTING.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1)
 
  This page provides a high-level overview of the process for contributing new tool integration guides to the `awesome-deepseek-agent` repository. The goal is to maintain a high-quality, bilingual community knowledge base that reflects the latest capabilities of DeepSeek V4 models.

 The contribution workflow is designed to ensure that every guide is technically accurate, supports advanced features like 1M context and reasoning effort, and is accessible to both English and Chinese-speaking developers.

 
### Contribution Workflow Overview

 The lifecycle of a contribution begins with verifying the current state of the repository and the DeepSeek API, followed by document creation and a structured review process.

 
 - **Preparation**: Check [open PRs](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/open PRs) to avoid duplication and consult the [DeepSeek API docs](https://api-docs.deepseek.com/) to ensure your guide uses current model specifications [CONTRIBUTING.md5-9](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L5-L9)
 - **Creation**: Author the guide following the **installation → configuration → first run** structure [CONTRIBUTING.md11-13](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L11-L13)
 - **Bilingual Support**: Create both English and Simplified Chinese versions of the documentation [CONTRIBUTING.md15-17](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L15-L17)
 - **Submission**: Open a single Pull Request (PR) containing the documentation, assets, and README updates [CONTRIBUTING.md75-78](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L75-L78)
 
 
#### Documentation Architecture

 The diagram below illustrates how a new contribution integrates into the existing codebase structure.

 **Contribution Structure Map**

 
```

```

 **Sources:** [CONTRIBUTING.md15-22](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L15-L22) [CONTRIBUTING.md79-81](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L79-L81) [.github/PULL_REQUEST_TEMPLATE.md1-20](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L20)

 
---

 
### Guide Format and Requirements

 Every contribution must adhere to specific formatting and bilingual standards to be accepted. This includes a mandatory file structure and the placement of assets.

 
 - **Bilingual Requirement**: Every guide requires an English version (`docs/tool_name.md`) and a Simplified Chinese version (`docs/tool_name.zh-CN.md`) [CONTRIBUTING.md15-17](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L15-L17)
 - **README Indexing**: The tool must be added to the tables in both `README.md` and `README.zh-CN.md` in **alphabetical order** [CONTRIBUTING.md19-21](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L19-L21)
 - **Assets**: Screenshots and diagrams must be placed in `docs/assets/` with descriptive filenames [CONTRIBUTING.md79-81](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L79-L81)
 
 For detailed instructions on the required document structure and bilingual standards, see [Guide Format and Bilingual Requirements](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/8.1-guide-format-and-bilingual-requirements).

 **Sources:** [CONTRIBUTING.md11-22](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L11-L22) [CONTRIBUTING.md79-81](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L79-L81)

 
---

 
### Technical Checklist and Critical Checks

 To maintain technical excellence, all PRs are evaluated against a set of critical checks centered on the DeepSeek V4 model capabilities.

 
 - **Model Naming**: Use `deepseek-v4-pro` and `deepseek-v4-flash`. Legacy names like `deepseek-chat` or `deepseek-reasoner` are deprecated [CONTRIBUTING.md27-34](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L27-L34)
 - **1M Context Window**: Configurations must support or mention the 1,000,000 token context window [CONTRIBUTING.md36-44](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L36-L44)
 - **Reasoning Effort**: Guides must configure the highest available reasoning effort (e.g., `CLAUDE_CODE_EFFORT_LEVEL=max`) [CONTRIBUTING.md46-54](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L46-L54)
 - **Pricing**: If pricing is mentioned, it must be verified against the official API pricing page [CONTRIBUTING.md56-63](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L56-L63)
 
 For a full breakdown of the technical requirements and common pitfalls to avoid, see [Technical Checklist and Critical Checks](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/8.2-technical-checklist-and-critical-checks).

 **Sources:** [CONTRIBUTING.md23-63](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L23-L63) [.github/PULL_REQUEST_TEMPLATE.md5-12](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L5-L12)

 
---

 
### The Review Process

 Once a PR is submitted, maintainers use a standardized checklist to verify both the documentation quality and the agent configuration.

 **PR Review Workflow**

 
```

```

 **Sources:** [CONTRIBUTING.md83-102](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/CONTRIBUTING.md?plain=1#L83-L102) [.github/PULL_REQUEST_TEMPLATE.md3-20](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L3-L20)
