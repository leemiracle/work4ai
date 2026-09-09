> 来源: [https://deepwiki.com/deepseek-ai/awesome-deepseek-coder/3-community-ecosystem](https://deepwiki.com/deepseek-ai/awesome-deepseek-coder/3-community-ecosystem)
> DeepWiki deepseek-ai/awesome-deepseek-coder

# Community Ecosystem

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1)
 
  This document covers the extensive community-driven extensions, derivatives, and tools built around DeepSeek Coder models. The community ecosystem encompasses specialized model variants, optimized distributions, and integration tools that extend the capabilities of the base DeepSeek Coder models.

 For information about the official DeepSeek models and platforms, see [Official DeepSeek Resources](https://deepwiki.com/deepseek-ai/awesome-deepseek-coder/2-official-deepseek-resources). For performance metrics and validation of these community tools, see [Performance and Validation](https://deepwiki.com/deepseek-ai/awesome-deepseek-coder/4-performance-and-validation).

 
## Community Model Architecture

 The community ecosystem follows a hierarchical derivation pattern from the official DeepSeek Coder base models:

 
#### Community Model Derivation Flow

 
```

```

 Sources: [README.md27-44](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L27-L44)

 
## Community-Derived Models

 The community has developed specialized variants of DeepSeek Coder models, each targeting specific use cases and improvements over the base models.

 
### Model Distribution by Size Categories

 
| Model Size | Community Models | Specialization |
|---|---|---|
| 1.3B | OpenCodeInterpreter-DS-1.3B | Code interpretation and execution |
| 6.7B | Magicoder-DS-6.7BMagicoder-S-DS-6.7BOpenCodeInterpreter-DS-6.7Bopenbuddy-deepseekcoder-6b-v16.1-32k | Magic promptingSource-only trainingCode interpretationMultilingual support |
| 33B | WizardCoder-33B-V1.1CodeFuse-DeepSeek-33BOpenCodeInterpreter-DS-33Bopenbuddy-deepseekcoder-33b-v16.1-32k | Evol-Instruct methodologyMulti-tasking fusionCode interpretationMultilingual support |

 
#### Community Model Ecosystem Mapping

 
```

```

 Sources: [README.md27-33](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L27-L33)

 
## Quantized Models and Optimizations

 The community maintains comprehensive quantized versions of all DeepSeek Coder models through TheBloke's systematic quantization efforts, providing multiple format options for deployment optimization.

 
### Quantization Format Matrix

 
#### TheBloke Quantization Coverage

 
```

```

 
### Quantized Model Repository Structure

 
| Model Size | Base AWQ | Base GGUF | Base GPTQ | Instruct AWQ | Instruct GGUF | Instruct GPTQ |
|---|---|---|---|---|---|---|
| 1.3B | TheBloke/deepseek-coder-1.3b-base-AWQ | TheBloke/deepseek-coder-1.3b-base-GGUF | TheBloke/deepseek-coder-1.3b-base-GPTQ | TheBloke/deepseek-coder-1.3b-instruct-AWQ | TheBloke/deepseek-coder-1.3b-instruct-GGUF | TheBloke/deepseek-coder-1.3b-instruct-GPTQ |
| 5.7B | TheBloke/deepseek-coder-5.7bmqa-base-AWQ | TheBloke/deepseek-coder-5.7bmqa-base-GGUF | TheBloke/deepseek-coder-5.7bmqa-base-GPTQ | Coming soon | Coming soon | Coming soon |
| 6.7B | TheBloke/deepseek-coder-6.7B-base-AWQ | TheBloke/deepseek-coder-6.7B-base-GGUF | TheBloke/deepseek-coder-6.7B-base-GPTQ | TheBloke/deepseek-coder-6.7B-instruct-AWQ | TheBloke/deepseek-coder-6.7B-instruct-GGUF | TheBloke/deepseek-coder-6.7B-instruct-GPTQ |
| 33B | TheBloke/deepseek-coder-33B-base-AWQ | TheBloke/deepseek-coder-33B-base-GGUF | TheBloke/deepseek-coder-33B-base-GPTQ | TheBloke/deepseek-coder-33B-instruct-AWQ | TheBloke/deepseek-coder-33B-instruct-GGUF | TheBloke/deepseek-coder-33B-instruct-GPTQ |

 Sources: [README.md35-44](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L35-L44)

 
## Development Tools and Integrations

 The community has developed multiple AI coding assistants and development environments that integrate DeepSeek Coder models, providing various deployment and interaction patterns.

 
### Copilot Integration Architecture

 
#### Tool Integration Ecosystem

 
```

```

 
### Tool-Specific Capabilities

 
#### refact Integration

 
 - **Repository**: `smallcloudai/refact`
 - **Supported Models**: `deepseek-coder/1.3b/base`, `deepseek-coder/5.7b/mqa-base`, `deepseek-coder/6.7b/instruct`, `deepseek-coder/33b/instruct`
 - **Features**: Code completion, code improvement tools, chat interface
 - **Deployment**: Open-source AI coding assistant
 
 
#### Tabby Integration

 
 - **Repository**: `TabbyML/tabby`
 - **Model Performance**: `deepseek-coder-6.7B` ranks as top performer in code completion
 - **Leaderboard**: Available at `leaderboard.tabbyml.com`
 - **Documentation**: `tabby.tabbyml.com/docs/models/`
 - **Type**: Self-hosted GitHub Copilot alternative
 
 
#### AutoDev Integration

 
 - **Repository**: `unit-mesh/auto-dev`
 - **Target Platform**: JetBrains IDE
 - **Fine-tuning Framework**: `unit-mesh/unit-eval`
 - **Dataset**: `unit-mesh/unit-eval-completion`
 - **Fine-tuned Model**: `unit-mesh/autodev-deepseek-6.7b-finetunes`
 - **API Server**: `unit-eval/blob/master/finetunes/deepseek/api-server-python38.py`
 
 
### Community API Services

 The community also provides API access to quantized models:

 
| Provider | Model | Format | Access |
|---|---|---|---|
| limcheekin | deepseek-coder-6.7B-instruct-GGUF | GGUF | huggingface.co/spaces/limcheekin/deepseek-coder-6.7B-instruct-GGUF |

 Sources: [README.md46-57](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L46-L57)
