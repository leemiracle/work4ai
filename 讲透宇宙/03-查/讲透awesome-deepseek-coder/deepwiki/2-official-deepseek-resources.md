> 来源: [https://deepwiki.com/deepseek-ai/awesome-deepseek-coder/2-official-deepseek-resources](https://deepwiki.com/deepseek-ai/awesome-deepseek-coder/2-official-deepseek-resources)
> DeepWiki deepseek-ai/awesome-deepseek-coder

# Official DeepSeek Resources

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1)
 
  This document covers the official DeepSeek Coder models, platforms, and services that form the foundational layer of the DeepSeek Coder ecosystem. This includes the core model variants released by DeepSeek AI, their distribution channels, and the primary access methods for developers. For community-derived models and third-party integrations, see [Community Ecosystem](https://deepwiki.com/deepseek-ai/awesome-deepseek-coder/3-community-ecosystem). For performance metrics and validation data, see [Performance and Validation](https://deepwiki.com/deepseek-ai/awesome-deepseek-coder/4-performance-and-validation).

 
## Core Model Architecture and Distribution

 The official DeepSeek Coder ecosystem is structured around a systematic release pattern with multiple model sizes and two primary variants for each size.

 
### Model Size Hierarchy

 
```

```

 Sources: [README.md16-23](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L16-L23)

 
### Official Model Variants Table

 The following table presents the complete matrix of official DeepSeek Coder models as distributed through the `huggingface.co/deepseek-ai` organization:

 
| Model Size | Base | Instruct |
|---|---|---|
| 1.3B | deepseek-coder-1.3b-base | deepseek-coder-1.3b-instruct |
| 5.7B | deepseek-coder-5.7bmqa-base | deepseek-coder-5.7bmqa-instruct |
| 6.7B | deepseek-coder-6.7B-base | deepseek-coder-6.7B-instruct |
| 33B | deepseek-coder-33B-base | deepseek-coder-33B-instruct |

 Sources: [README.md18-23](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L18-L23)

 
## Official Platform Infrastructure

 The official DeepSeek ecosystem provides multiple access points for different use cases, from interactive chat to programmatic API access.

 
### Platform Architecture

 
```

```

 Sources: [README.md12-13](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L12-L13) [README.md17](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L17-L17)

 
### Distribution Channel Specifications

 The official distribution follows a multi-channel approach designed to serve different technical requirements:

 
| Platform | URL | Primary Function | Target Users |
|---|---|---|---|
| Chat Interface | coder.deepseek.com | Interactive code assistance | Casual users, evaluation |
| Model Repository | huggingface.co/deepseek-ai | Model hosting and download | Researchers, self-hosting |
| API Platform | platform.deepseek.com | Programmatic access | Enterprise integration |

 Sources: [README.md12-13](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L12-L13) [README.md17](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L17-L17)

 
### Model Naming Convention

 The official models follow a consistent naming pattern that encodes size and variant information:

 
```

```

 Sources: [README.md20-23](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L20-L23)

 
## Model Availability Status

 The release status of official models shows variations in availability, particularly for instruct variants:

 
### Current Availability Matrix

 
| Model Size | Base Status | Instruct Status |
|---|---|---|
| 1.3B | ✅ Available | ✅ Available |
| 5.7B | ✅ Available | ⏳ Coming Soon |
| 6.7B | ✅ Available | ✅ Available |
| 33B | ✅ Available | ✅ Available |

 Sources: [README.md21-23](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L21-L23)

 The `deepseek-coder-5.7bmqa-instruct` model is specifically marked as "coming soon" in the official documentation, indicating ongoing development of instruction-tuned variants for the 5.7B parameter size.

 Sources: [README.md21](https://github.com/deepseek-ai/awesome-deepseek-coder/blob/e04a6004/README.md?plain=1#L21-L21)
