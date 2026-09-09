> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR/8-contributing](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/8-contributing)
> DeepWiki deepseek-ai/DeepSeek-OCR

# Contributing

  Relevant source files 
 - [LICENSE](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/LICENSE)
 - [README.md](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1)
 
  This page provides guidelines for contributing to the DeepSeek-OCR project, including development setup, coding standards, testing procedures, and the pull request process. Whether you're fixing bugs, adding features, improving documentation, or optimizing performance, this guide will help you make effective contributions.

 For information about using DeepSeek-OCR as an end user, see [Getting Started](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/2-getting-started). For extending the system with custom components, see [Developer Guide](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/5-developer-guide).

 
---

 
## Purpose and Scope

 DeepSeek-OCR is an open-source project released under the MIT License, welcoming contributions from the community. This document covers:

 
 - Development environment setup for contributors
 - Code organization and where to make changes
 - Testing and validation procedures
 - Pull request guidelines and review process
 - Coding standards and best practices
 
 
---

 
## License and Terms

 DeepSeek-OCR is released under the MIT License, which grants broad permissions for use, modification, and distribution. All contributions must be compatible with this license.

 **Key License Terms:**

 
 - Permission to use, copy, modify, merge, publish, distribute, sublicense, and sell [LICENSE5-9](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/LICENSE#L5-L9)
 - Requires attribution and license notice in all copies [LICENSE12-13](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/LICENSE#L12-L13)
 - Provided "as is" without warranty [LICENSE15-17](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/LICENSE#L15-L17)
 - No liability for damages or issues [LICENSE17-21](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/LICENSE#L17-L21)
 
 Before contributing, ensure you have the right to submit your code and that your contribution complies with the MIT License terms.

 **Sources:** [LICENSE1-22](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/LICENSE#L1-L22)

 
---

 
## Development Environment Setup

 
### Prerequisites

 Before contributing, set up a complete development environment that supports both inference pathways (Transformers and vLLM).

 **System Requirements:**

 
 - CUDA 11.8 or higher [README.md69](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L69-L69)
 - Python 3.12.9 [README.md76](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L76-L76)
 - GPU with sufficient memory (A100-40G recommended for full testing) [README.md100](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L100-L100)
 
 
### Environment Installation

 Installation involves cloning the repository, setting up a Conda environment, and installing specific versions of PyTorch and vLLM.

 **Installation Flow:**

 
```

```

 **Installation Steps:**

 
 - **Clone the repository:** [README.md72](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L72-L72)

 
```

```
 - **Create isolated conda environment:** [README.md76-77](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L76-L77)

 
```

```
 - **Install PyTorch with CUDA support:** [README.md83](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L83-L83)

 
```

```
 - **Install vLLM from wheel:** [README.md81-84](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L81-L84)

 
 - Download vllm-0.8.5 wheel from [GitHub releases](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/GitHub releases)
 
 
```

```
 - **Install project dependencies:** [README.md85](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L85-L85)

 
```

```
 - **Install Flash Attention:** [README.md86](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L86-L86)

 
```

```
 
 **Note:** You may see warnings about transformers version conflicts between vLLM and the Hugging Face implementation. This is expected and both will function correctly in the same environment [README.md88](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L88-L88)

 **Sources:** [README.md66-86](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L66-L86)

 
---

 
## Code Organization

 Understanding the codebase structure is essential for making targeted contributions. DeepSeek-OCR is organized into two main inference pathways with shared model components.

 
### Repository Structure

 
```

```

 
### Contribution Areas by Component

 
| Component Type | File Locations | Contribution Examples |
|---|---|---|
| vLLM Inference | DeepSeek-OCR-vllm/ | Add streaming features, optimize batching, improve concurrency README.md91-107 |
| Transformers Inference | DeepSeek-OCR-hf/ | Enhance API, add inference modes, improve error handling README.md165-189 |
| Configuration | DeepSeek-OCR-vllm/config.py | Add parameters, create presets, improve validation README.md92 |
| Logits Processing | vllm.model_executor.models.deepseek_ocr | Add filters, implement constraints, optimize generation README.md120 |
| Documentation | README.md | Add examples, improve clarity, update installation guides README.md201-209 |

 **Sources:** [README.md59-189](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L59-L189)

 
---

 
## Contribution Workflow

 Follow this standard workflow for all contributions, from initial setup through merged pull request.

 
### Development Workflow Diagram

 
```

```

 
### Step-by-Step Process

 **1. Identify the Contribution:**

 
 - Check existing issues for bugs or feature requests.
 - Discuss major changes before implementation.
 
 **2. Fork and Clone:**

 
```

```

 **3. Create Feature Branch:**

 
```

```

 **4. Make Changes:**

 
 - Follow coding standards.
 - Add tests for new functionality.
 - Update documentation as needed.
 
 **5. Test Your Changes:**

 
```

```

 **6. Push and Create PR:**

 
```

```

 **Sources:** [README.md94-107](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L94-L107) [README.md187-189](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L187-L189)

 
---

 
## Testing Guidelines

 Comprehensive testing ensures contributions don't break existing functionality and work across different configurations.

 
### Testing Strategy

 
```

```

 
### Functional Testing

 **Test Transformers Path:** [README.md187-189](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L187-L189)

 
```

```

 **Test vLLM Path:** [README.md94-107](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L94-L107)

 
```

```

 
### Validation Checklist

 
 - Output format is correct (markdown, grounding tags, etc.) [README.md179](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L179-L179)
 - Special tokens like `<image>`, `<|grounding|>`, `<|ref|>` are handled correctly [README.md202-207](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L202-L207)
 - `NGramPerReqLogitsProcessor` effectively prevents repetition [README.md120](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L120-L120)
 - Performance meets expectations (e.g., ~2500 tokens/s on A100 for PDF) [README.md100](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L100-L100)
 
 **Sources:** [README.md96-107](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L96-L107) [README.md120-130](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L120-L130) [README.md178-183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L178-L183)

 
---

 
## Pull Request Guidelines

 
### PR Preparation

 Before submitting a pull request:

 
 - **Ensure all tests pass** in both Transformers and vLLM paths.
 - **Update documentation** if behavior changes.
 - **Check code style** compliance.
 - **Rebase on latest main** to avoid merge conflicts.
 
 
### Code Review Process

 **Review Criteria:**

 
 - Code quality and readability.
 - Test coverage and quality.
 - Documentation completeness.
 - Performance impact.
 - Compatibility with existing features.
 
 
---

 
## Communication Channels

 
### Where to Discuss

 **GitHub Issues:**

 
 - Bug reports, feature requests, and technical questions.
 
 **Discord:** [README.md24-26](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L24-L26)

 
 - Real-time chat: [https://discord.gg/Tc7c45Zzu5](https://discord.gg/Tc7c45Zzu5)
 
 **Twitter:** [README.md27-29](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L27-L29)

 
 - Announcements: [@deepseek_ai](https://twitter.com/deepseek_ai)
 
 **Sources:** [README.md24-30](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L24-L30)

 
---

 
## Summary

 Contributing to DeepSeek-OCR involves:

 
 - **Setup:** Fork repository, create development environment using Conda and specific wheel versions.
 - **Development:** Make focused changes in `DeepSeek-OCR-hf` or `DeepSeek-OCR-vllm`.
 - **Testing:** Validate using provided scripts (`run_dpsk_ocr_image.py`, `run_dpsk_ocr.py`, etc.).
 - **Documentation:** Update `README.md` or wiki pages.
 - **Submission:** Create detailed pull request and address feedback.
 
 Every contribution helps make DeepSeek-OCR better for the community. Happy contributing!
