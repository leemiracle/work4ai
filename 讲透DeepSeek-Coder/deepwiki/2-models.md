> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Coder/2-models](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/2-models)
> DeepWiki deepseek-ai/DeepSeek-Coder

# Models

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1)
 
  This page provides an overview of the DeepSeek Coder model family, including different model sizes, variants, and their general characteristics. For detailed information about the model architecture, refer to [Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/2.1-architecture). For comprehensive benchmark results and performance metrics, see [Performance and Benchmarks](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/2.2-performance-and-benchmarks).

 
## Model Family Overview

 DeepSeek Coder consists of a series of transformer-based language models specifically trained for code understanding and generation. All models were trained from scratch on a massive corpus of 2 trillion tokens, with a composition of 87% code and 13% natural language (both English and Chinese).

 The model family includes:

 
 - **Base Models** - Foundation models trained on code and related texts
 - **Instruction-tuned Models** - Enhanced versions fine-tuned on instruction data for interactive coding assistance
 
 
```

```

 Sources: [README.md11-26](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L11-L26) [README.md57-62](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L57-L62)

 
## Model Size Comparison

 The DeepSeek Coder family comes in various parameter sizes to suit different deployment requirements, from more efficient smaller models to higher-capability larger models.

 
| Model | Parameters | Context Window | Variants Available |
|---|---|---|---|
| DeepSeek-Coder-1B | 1 billion | 16K tokens | Base |
| DeepSeek-Coder-5.7B | 5.7 billion | 16K tokens | Base |
| DeepSeek-Coder-6.7B | 6.7 billion | 16K tokens | Base, Instruct |
| DeepSeek-Coder-33B | 33 billion | 16K tokens | Base, Instruct |

 Sources: [README.md21-22](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L21-L22) [README.md25](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L25-L25)

 
## Training Process

 The DeepSeek Coder models underwent a comprehensive multi-stage training process to develop both their general code understanding and specialized capabilities.

 
```

```

 Sources: [README.md58-62](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L58-L62)

 
## Supported Programming Languages

 The models support a wide range of programming languages, making them versatile for various development environments and coding tasks.

 
```

```

 The models support over 80 programming languages in total, including: Ada, Agda, Alloy, ANTLR, AppleScript, Assembly, and many others. See the README for the complete list.

 Sources: [README.md27-28](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L27-L28)

 
## Model Capabilities

 DeepSeek Coder models offer a range of capabilities that make them suitable for various coding tasks:

 
```

```

 Sources: [README.md74-104](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L74-L104) [README.md102-141](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L102-L141) [README.md178-254](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L178-L254)

 
### Feature Support by Model Variant

 
| Feature | Base Models | Instruct Models |
|---|---|---|
| Code Completion | ✅ | ✅ |
| Fill-in-the-Middle (FIM) | ✅ | ✅ |
| Repository-Level Understanding | ✅ | ✅ |
| Interactive Chat | ❌ | ✅ |

 Sources: [README.md74-266](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L74-L266)

 
## Performance Overview

 DeepSeek Coder models have demonstrated strong performance across various benchmarks. The largest model, DeepSeek-Coder-Base-33B, outperforms other open-source models of similar size, while even the smaller 6.7B model achieves performance comparable to much larger models from other families.

 
| Model | HumanEval (Python) | MBPP | DS-1000 |
|---|---|---|---|
| DeepSeek-Coder-Base-33B | Leading performance | Leading performance | Leading performance |
| DeepSeek-Coder-Base-6.7B | Comparable to CodeLlama-34B | Comparable to CodeLlama-34B | Comparable to CodeLlama-34B |
| DeepSeek-Coder-Instruct-33B | Outperforms GPT3.5-turbo | Comparable to GPT3.5-turbo | - |

 For detailed benchmark results, please refer to [Performance and Benchmarks](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/2.2-performance-and-benchmarks).

 Sources: [README.md30-43](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L30-L43)

 
## Model Deployment Options

 The DeepSeek Coder models support various deployment options to accommodate different hardware and performance requirements.

 
```

```

 Sources: [README.md333-382](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L333-L382) [README.md386-417](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L386-L417)

 
## Model License and Availability

 All DeepSeek Coder models are available for download from Hugging Face and support commercial use. The models are subject to the Model License, while the code in the repository is licensed under the MIT License.

 Sources: [README.md423-426](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L423-L426)

 
## Conclusion

 DeepSeek Coder models represent a family of code language models designed specifically for software development tasks. Available in different sizes and variants, they offer state-of-the-art performance for code completion, code insertion, repository-level understanding, and interactive assistance. The models support a wide range of programming languages and can be deployed through various methods depending on hardware availability and performance requirements.

 For more detailed information about these models, refer to:

 
 - [Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/2.1-architecture) - Detailed technical architecture information
 - [Performance and Benchmarks](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/2.2-performance-and-benchmarks) - Comprehensive benchmark results
 - [Usage and Inference Methods](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/3-usage-and-inference-methods) - How to use the models for different tasks
