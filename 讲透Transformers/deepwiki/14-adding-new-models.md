> 来源: [https://deepwiki.com/huggingface/transformers/14-adding-new-models](https://deepwiki.com/huggingface/transformers/14-adding-new-models)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Adding New Models

  Relevant source files 
 - [.ai/AGENTS.md](https://github.com/huggingface/transformers/blob/8f542025/.ai/AGENTS.md?plain=1)
 - [.ai/skills/add-or-fix-type-checking/SKILL.md](https://github.com/huggingface/transformers/blob/8f542025/.ai/skills/add-or-fix-type-checking/SKILL.md?plain=1)
 - [.github/ISSUE_TEMPLATE/bug-report.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/ISSUE_TEMPLATE/bug-report.yml)
 - [.github/ISSUE_TEMPLATE/migration.yml](https://github.com/huggingface/transformers/blob/8f542025/.github/ISSUE_TEMPLATE/migration.yml)
 - [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/huggingface/transformers/blob/8f542025/.github/PULL_REQUEST_TEMPLATE.md?plain=1)
 - [AGENTS.md](https://github.com/huggingface/transformers/blob/8f542025/AGENTS.md?plain=1)
 - [CLAUDE.md](https://github.com/huggingface/transformers/blob/8f542025/CLAUDE.md?plain=1)
 - [CONTRIBUTING.md](https://github.com/huggingface/transformers/blob/8f542025/CONTRIBUTING.md?plain=1)
 - [docs/source/de/contributing.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/de/contributing.md?plain=1)
 - [docs/source/en/model_doc/fuyu.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/model_doc/fuyu.md?plain=1)
 - [docs/source/en/model_doc/paddleocr_vl.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/model_doc/paddleocr_vl.md?plain=1)
 - [docs/source/en/modular_transformers.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/modular_transformers.md?plain=1)
 - [docs/source/es/pr_checks.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/es/pr_checks.md?plain=1)
 - [docs/source/it/pr_checks.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/it/pr_checks.md?plain=1)
 - [docs/source/ja/pr_checks.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ja/pr_checks.md?plain=1)
 - [docs/source/ko/contributing.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/contributing.md?plain=1)
 - [docs/source/ko/pr_checks.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/ko/pr_checks.md?plain=1)
 - [docs/source/zh/contributing.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/zh/contributing.md?plain=1)
 - [examples/modular-transformers/configuration_duplicated_method.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/configuration_duplicated_method.py)
 - [examples/modular-transformers/configuration_my_new_model.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/configuration_my_new_model.py)
 - [examples/modular-transformers/configuration_my_new_model2.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/configuration_my_new_model2.py)
 - [examples/modular-transformers/configuration_new_model.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/configuration_new_model.py)
 - [examples/modular-transformers/modeling_dummy_bert.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_dummy_bert.py)
 - [examples/modular-transformers/modeling_from_uppercase_model.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_from_uppercase_model.py)
 - [examples/modular-transformers/modeling_global_indexing.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_global_indexing.py)
 - [examples/modular-transformers/modeling_multimodal2.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_multimodal2.py)
 - [examples/modular-transformers/modeling_my_new_model2.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_my_new_model2.py)
 - [examples/modular-transformers/modeling_new_task_model.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_new_task_model.py)
 - [examples/modular-transformers/modeling_roberta.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_roberta.py)
 - [examples/modular-transformers/modeling_super.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_super.py)
 - [examples/modular-transformers/modeling_switch_function.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_switch_function.py)
 - [examples/modular-transformers/modeling_test_detr.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modeling_test_detr.py)
 - [examples/modular-transformers/modular_multimodal2.py](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/modular_multimodal2.py)
 - [src/transformers/models/emu3/processing_emu3.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/emu3/processing_emu3.py)
 - [src/transformers/models/ernie4_5_vl_moe/processing_ernie4_5_vl_moe.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/ernie4_5_vl_moe/processing_ernie4_5_vl_moe.py)
 - [src/transformers/models/fuyu/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/__init__.py)
 - [src/transformers/models/fuyu/image_processing_fuyu.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/image_processing_fuyu.py)
 - [src/transformers/models/fuyu/image_processing_pil_fuyu.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/image_processing_pil_fuyu.py)
 - [src/transformers/models/fuyu/modeling_fuyu.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/modeling_fuyu.py)
 - [src/transformers/models/fuyu/processing_fuyu.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/processing_fuyu.py)
 - [src/transformers/models/paddleocr_vl/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/paddleocr_vl/__init__.py)
 - [src/transformers/models/qwen2_audio/processing_qwen2_audio.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/qwen2_audio/processing_qwen2_audio.py)
 - [src/transformers/utils/auto_docstring.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/auto_docstring.py)
 - [tests/models/emu3/test_processing_emu3.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/emu3/test_processing_emu3.py)
 - [tests/models/ernie4_5_vl_moe/test_modeling_ernie4_5_vl_moe.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/ernie4_5_vl_moe/test_modeling_ernie4_5_vl_moe.py)
 - [tests/models/ernie4_5_vl_moe/test_processing_ernie4_5_vl_moe.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/ernie4_5_vl_moe/test_processing_ernie4_5_vl_moe.py)
 - [tests/models/fuyu/test_image_processing_fuyu.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/fuyu/test_image_processing_fuyu.py)
 - [tests/models/fuyu/test_modeling_fuyu.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/fuyu/test_modeling_fuyu.py)
 - [tests/models/fuyu/test_processing_fuyu.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/fuyu/test_processing_fuyu.py)
 - [tests/models/idefics2/test_processing_idefics2.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/idefics2/test_processing_idefics2.py)
 - [tests/models/idefics3/test_processing_idefics3.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/idefics3/test_processing_idefics3.py)
 - [tests/models/kosmos2/test_modeling_kosmos2.py](https://github.com/huggingface/transformers/blob/8f542025/tests/models/kosmos2/test_modeling_kosmos2.py)
 - [tests/repo_utils/modular/test_conversion_order.py](https://github.com/huggingface/transformers/blob/8f542025/tests/repo_utils/modular/test_conversion_order.py)
 - [tests/repo_utils/test_check_modular_conversion.py](https://github.com/huggingface/transformers/blob/8f542025/tests/repo_utils/test_check_modular_conversion.py)
 - [tests/utils/test_auto_docstring.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_auto_docstring.py)
 - [utils/add_dates.py](https://github.com/huggingface/transformers/blob/8f542025/utils/add_dates.py)
 - [utils/check_docstrings.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_docstrings.py)
 - [utils/check_modular_conversion.py](https://github.com/huggingface/transformers/blob/8f542025/utils/check_modular_conversion.py)
 - [utils/create_dependency_mapping.py](https://github.com/huggingface/transformers/blob/8f542025/utils/create_dependency_mapping.py)
 - [utils/modular_model_converter.py](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py)
 
  Adding a new model architecture to the Hugging Face Transformers library is a structured process designed to maintain code readability, consistency, and ease of use. The library currently supports two primary methods for model addition: the **Modular Transformers System** (recommended for models based on existing architectures) and the **Legacy Single-File Approach** (for entirely novel architectures).

 
### Overview of Model Addition

 The core philosophy of Transformers emphasizes composition over abstraction and self-contained model files. Every new model implementation typically requires:

 
 - A `Configuration` class inheriting from `PreTrainedConfig` [examples/modular-transformers/configuration_my_new_model.py18](https://github.com/huggingface/transformers/blob/8f542025/examples/modular-transformers/configuration_my_new_model.py#L18-L18)
 - A `Model` class inheriting from `PreTrainedModel` [src/transformers/models/fuyu/modeling_fuyu.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/modeling_fuyu.py#L33-L33)
 - Integration with the `Auto` factory classes (e.g., `AutoModel`, `AutoConfig`) [utils/modular_model_converter.py38-39](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py#L38-L39)
 - Standardized docstrings and repository consistency checks [utils/check_docstrings.py65-79](https://github.com/huggingface/transformers/blob/8f542025/utils/check_docstrings.py#L65-L79)
 
 
### 1. Modular Transformers System

 The Modular Transformers system is the modern standard for adding models that share components with existing architectures (e.g., Llama, Mistral, or Mixtral). Instead of duplicating thousands of lines of code, contributors create a `modular_<model_name>.py` file that inherits from and modifies existing classes [docs/source/en/modular_transformers.md16-18](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/modular_transformers.md?plain=1#L16-L18)

 
 - **Workflow**: You write a concise modular file, and a converter tool generates the final, standalone `modeling_<model_name>.py` file to ensure the "single file per model" user experience is preserved [utils/modular_model_converter.py44-50](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py#L44-L50)
 - **Key Tools**: 
 - `modular_model_converter.py`: The engine that parses modular files and generates standalone code [utils/modular_model_converter.py55-71](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py#L55-L71) It uses a `ReplaceNameTransformer` to handle casing and naming conventions [utils/modular_model_converter.py142-165](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py#L142-L165)
 - `check_modular_conversion.py`: A CI tool that ensures the generated modeling files match the source modular definitions [utils/check_modular_conversion.py19-26](https://github.com/huggingface/transformers/blob/8f542025/utils/check_modular_conversion.py#L19-L26)
 
 For a deep dive into inheritance patterns and code generation, see **[Modular Transformers System](https://deepwiki.com/huggingface/transformers/14.1-modular-transformers-system)**.

 **Sources:** [docs/source/en/modular_transformers.md16-20](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/modular_transformers.md?plain=1#L16-L20) [utils/modular_model_converter.py142-165](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py#L142-L165) [utils/check_modular_conversion.py19-26](https://github.com/huggingface/transformers/blob/8f542025/utils/check_modular_conversion.py#L19-L26)

 
### 2. Legacy Single-File Approach

 For models that do not cleanly inherit from existing implementations, the legacy approach involves manually writing the entire `modeling.py`, `configuration.py`, and `tokenization.py` files [docs/source/en/modular_transformers.md22-26](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/modular_transformers.md?plain=1#L22-L26) This approach is more engineering-intensive but provides total control over the implementation.

 
 - **Requirements**: Contributors must ensure all standard methods like `forward` [src/transformers/models/fuyu/modeling_fuyu.py147](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/modeling_fuyu.py#L147-L147) `get_input_embeddings`, and `post_init` [src/transformers/models/fuyu/modeling_fuyu.py63](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/modeling_fuyu.py#L63-L63) are correctly implemented.
 - **Best Practices**: Code should be explicit and type-annotated. For example, multimodal models like Fuyu explicitly define `input_modalities` and `_supports_attention_backend` [src/transformers/models/fuyu/modeling_fuyu.py36-38](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/modeling_fuyu.py#L36-L38)
 
 **Sources:** [src/transformers/models/fuyu/modeling_fuyu.py32-63](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/modeling_fuyu.py#L32-L63) [docs/source/en/modular_transformers.md22-26](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/modular_transformers.md?plain=1#L22-L26)

 
### 3. Consistency and Documentation Tools

 To manage the complexity of hundreds of models, Transformers uses a suite of automated scripts to enforce quality and consistency across the repository.

 
 - **Docstring Automation**: The `@auto_docstring` decorator is used to automatically generate standardized argument descriptions for models, configs, and processors [src/transformers/utils/auto_docstring.py49-57](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/auto_docstring.py#L49-L57) It uses pre-defined argument templates like `ImageProcessorArgs` to maintain uniformity [src/transformers/utils/auto_docstring.py110-215](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/auto_docstring.py#L110-L215)
 - **Validation Scripts**: 
 - `check_docstrings.py`: Checks that all docstrings of public objects have an argument section matching their signature [utils/check_docstrings.py14-15](https://github.com/huggingface/transformers/blob/8f542025/utils/check_docstrings.py#L14-L15)
 - `check_modular_conversion.py`: Validates that no manual edits were made to auto-generated files by diffing the current content against the generator output [utils/check_modular_conversion.py47-54](https://github.com/huggingface/transformers/blob/8f542025/utils/check_modular_conversion.py#L47-L54)
 - `check_repo.py`: The primary entry point for repository-wide consistency checks [utils/check_docstrings.py48](https://github.com/huggingface/transformers/blob/8f542025/utils/check_docstrings.py#L48-L48)
 
 For details on how the CI enforces these standards, see **[Repository Consistency & Documentation Checks](https://deepwiki.com/huggingface/transformers/14.2-repository-consistency-and-documentation-checks)**.

 **Sources:** [src/transformers/utils/auto_docstring.py1-57](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/auto_docstring.py#L1-L57) [utils/check_docstrings.py14-33](https://github.com/huggingface/transformers/blob/8f542025/utils/check_docstrings.py#L14-L33) [utils/check_modular_conversion.py35-71](https://github.com/huggingface/transformers/blob/8f542025/utils/check_modular_conversion.py#L35-L71)

 
### Bridging Concepts to Code

 The following diagrams illustrate how the conceptual requirements for a new model map to specific entities and tools within the codebase.

 
#### Model Addition Infrastructure

 
```

```

 **Sources:** [src/transformers/models/fuyu/modeling_fuyu.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/models/fuyu/modeling_fuyu.py) [utils/modular_model_converter.py](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py) [src/transformers/utils/auto_docstring.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/auto_docstring.py)

 
#### Modular Conversion Pipeline

 
```

```

 **Sources:** [utils/modular_model_converter.py142-165](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py#L142-L165) [utils/modular_model_converter.py94-119](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py#L94-L119) [utils/check_modular_conversion.py74-97](https://github.com/huggingface/transformers/blob/8f542025/utils/check_modular_conversion.py#L74-L97)

 
| Component | File Path | Role |
|---|---|---|
| Converter | utils/modular_model_converter.py | Generates standalone modeling files from modular sources utils/modular_model_converter.py44-50 |
| Checker | utils/check_modular_conversion.py | CI tool to prevent manual drift in generated files utils/check_modular_conversion.py19-26 |
| Docstring Utils | src/transformers/utils/auto_docstring.py | Logic for auto_docstring placeholders and argument unrolling src/transformers/utils/auto_docstring.py49-62 |
| Docstring Checker | utils/check_docstrings.py | Ensures docstrings match function/class signatures utils/check_docstrings.py14-23 |

 **Sources:** [utils/modular_model_converter.py1-50](https://github.com/huggingface/transformers/blob/8f542025/utils/modular_model_converter.py#L1-L50) [utils/check_modular_conversion.py19-26](https://github.com/huggingface/transformers/blob/8f542025/utils/check_modular_conversion.py#L19-L26) [src/transformers/utils/auto_docstring.py1-72](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/auto_docstring.py#L1-L72) [utils/check_docstrings.py14-33](https://github.com/huggingface/transformers/blob/8f542025/utils/check_docstrings.py#L14-L33)
