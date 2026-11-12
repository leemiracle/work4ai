<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/transformers.js · page 16 Examples and Use Cases · fetched 2026-10-26 -->

# Examples and Use Cases

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [package.json](package.json)
- [packages/transformers/docs/source/tutorials/browser-extension.md](packages/transformers/docs/source/tutorials/browser-extension.md)
- [packages/transformers/docs/source/tutorials/electron.md](packages/transformers/docs/source/tutorials/electron.md)
- [packages/transformers/docs/source/tutorials/react.md](packages/transformers/docs/source/tutorials/react.md)
- [packages/transformers/docs/source/tutorials/vanilla-js.md](packages/transformers/docs/source/tutorials/vanilla-js.md)

</details>



This document provides an overview of common usage patterns and practical examples for Transformers.js. It demonstrates how to use the library's Pipeline API, configure the environment, and integrate models into applications across different JavaScript runtimes.

For basic getting-started examples, see [Quick Start Examples](#16.1). For environment-specific integration patterns (vanilla JS, Node.js, React, web workers), see [Environment-Specific Examples](#16.2). For advanced techniques like custom caching, quantization, and streaming, see [Advanced Usage Patterns](#16.3).

For detailed API documentation, see [Public API Surface](#1.3). For installation instructions, see [Installation and Setup](#1.2).

## Usage Pattern Overview

All examples in Transformers.js follow a common pattern centered around the `pipeline` function. The diagram below shows how user code interacts with the core API components:

```mermaid
graph TB
    UserCode["User Application Code"]
    
    subgraph "Core API Exports"
        PipelineFunc["pipeline()<br/>packages/transformers/src/pipelines.js"]
        EnvObj["env<br/>packages/transformers/src/env.js"]
        AutoClasses["Auto Classes<br/>• AutoModel<br/>• AutoTokenizer<br/>• AutoProcessor"]
    end
    
    subgraph "Usage Patterns"
        BasicUsage["Basic Usage<br/>await pipeline(task, model)"]
        ConfigUsage["Configuration<br/>env.allowRemoteModels = false"]
        DirectUsage["Direct Model Usage<br/>AutoModel.from_pretrained()"]
    end
    
    subgraph "Common Tasks"
        TextTasks["Text Tasks<br/>• sentiment-analysis<br/>• text-generation<br/>• fill-mask"]
        VisionTasks["Vision Tasks<br/>• image-classification<br/>• object-detection<br/>• depth-estimation"]
        AudioTasks["Audio Tasks<br/>• automatic-speech-recognition<br/>• audio-classification"]
        MultimodalTasks["Multimodal Tasks<br/>• image-to-text<br/>• zero-shot-image-classification"]
    end
    
    UserCode --> BasicUsage
    UserCode --> ConfigUsage
    UserCode --> DirectUsage
    
    BasicUsage --> PipelineFunc
    ConfigUsage --> EnvObj
    DirectUsage --> AutoClasses
    
    PipelineFunc --> TextTasks
    PipelineFunc --> VisionTasks
    PipelineFunc --> AudioTasks
    PipelineFunc --> MultimodalTasks
```

**Sources:** [README.md:55-93](), [packages/transformers/src/env.js:137-195]()

## Basic Pipeline Usage Pattern

The `pipeline` function provides the simplest interface for running inference. This example demonstrates the canonical usage pattern:

```javascript
import { pipeline } from '@huggingface/transformers';

// Allocate a pipeline for sentiment-analysis
const pipe = await pipeline('sentiment-analysis');

const out = await pipe('I love transformers!');
// [{'label': 'POSITIVE', 'score': 0.999817686}]
```

### Pipeline Instantiation Flow

```mermaid
sequenceDiagram
    participant App as "Application Code"
    participant PipelineFunc as "pipeline()<br/>packages/transformers/src/pipelines.js"
    participant Registry as "MODEL_TYPE_MAPPING<br/>packages/transformers/src/models.js"
    participant Model as "PreTrainedModel<br/>packages/transformers/src/models.js"
    participant Tokenizer as "AutoTokenizer<br/>packages/transformers/src/tokenizers.js"
    participant Cache as "Cache System<br/>packages/transformers/src/utils/hub.js"
    
    App->>PipelineFunc: await pipeline('sentiment-analysis')
    PipelineFunc->>Registry: Resolve task → model mapping
    Registry-->>PipelineFunc: Default model for task
    
    PipelineFunc->>Cache: Check cache for model files
    alt Model cached
        Cache-->>PipelineFunc: Return cached files
    else Model not cached
        PipelineFunc->>Cache: Download from Hub
        Cache-->>PipelineFunc: Cache and return files
    end
    
    PipelineFunc->>Model: from_pretrained(model_id)
    Model-->>PipelineFunc: Model instance
    
    PipelineFunc->>Tokenizer: from_pretrained(model_id)
    Tokenizer-->>PipelineFunc: Tokenizer instance
    
    PipelineFunc-->>App: Pipeline instance ready
    
    App->>PipelineFunc: pipe('I love transformers!')
    PipelineFunc->>Tokenizer: Preprocess text
    PipelineFunc->>Model: Run inference
    PipelineFunc-->>App: Formatted results
```

**Sources:** [README.md:81-89](), [packages/transformers/src/env.js:174-180]()

## Model Specification Patterns

The library supports multiple ways to specify which model to use:

### Default Task Models

```javascript
// Uses default model for the task
const pipe = await pipeline('sentiment-analysis');
```

### Explicit Model ID

```javascript
// Use a specific model from Hugging Face Hub
const pipe = await pipeline(
    'sentiment-analysis',
    'Xenova/bert-base-multilingual-uncased-sentiment'
);
```

### Custom Options

```javascript
// Configure device and quantization
const pipe = await pipeline(
    'sentiment-analysis',
    'Xenova/distilbert-base-uncased-finetuned-sst-2-english',
    {
        device: 'webgpu',  // Use GPU acceleration
        dtype: 'q4',        // 4-bit quantization
    }
);
```

**Sources:** [README.md:96-127]()

## Environment Configuration Patterns

The `env` object provides global configuration for model loading, caching, and backend settings:

### Environment Configuration Flow

```mermaid
graph TB
    subgraph "env Object Properties"
        AllowRemote["allowRemoteModels: boolean<br/>Default: true"]
        RemoteHost["remoteHost: string<br/>Default: 'https://huggingface.co/'"]
        AllowLocal["allowLocalModels: boolean<br/>Default: false (browser), true (node)"]
        LocalPath["localModelPath: string<br/>Default: '/models/'"]
        
        UseBrowserCache["useBrowserCache: boolean<br/>Default: IS_WEB_CACHE_AVAILABLE"]
        UseFSCache["useFSCache: boolean<br/>Default: IS_FS_AVAILABLE"]
        CacheDir["cacheDir: string<br/>Default: './.cache/'"]
        
        BackendsOnnx["backends.onnx.wasm<br/>WASM runtime configuration"]
    end
    
    subgraph "Common Configurations"
        LocalOnly["Local-Only Mode<br/>env.allowRemoteModels = false"]
        CustomPath["Custom Model Path<br/>env.localModelPath = '/path/'"]
        CustomWasm["Custom WASM Path<br/>env.backends.onnx.wasm.wasmPaths"]
        CustomCacheDir["Custom Cache Directory<br/>env.cacheDir = '/cache/'"]
    end
    
    AllowRemote --> LocalOnly
    LocalPath --> CustomPath
    BackendsOnnx --> CustomWasm
    CacheDir --> CustomCacheDir
```

**Sources:** [packages/transformers/src/env.js:137-195]()

### Configuration Examples

```javascript
import { env } from '@huggingface/transformers';

// Disable remote model loading
env.allowRemoteModels = false;

// Set custom local model path
env.localModelPath = '/path/to/models/';

// Set custom cache directory
env.cacheDir = '/path/to/cache/';

// Configure WASM paths
env.backends.onnx.wasm.wasmPaths = '/path/to/wasm/files/';
```

**Sources:** [packages/transformers/src/env.js:142-160]()

## Supported Tasks and Examples

The library supports 30+ tasks across different modalities. Below is a mapping of tasks to their corresponding pipeline types:

| Modality | Task ID | Example Use Case |
|----------|---------|------------------|
| **NLP** | `sentiment-analysis` | Analyze sentiment of reviews |
| | `text-generation` | Generate text completions |
| | `fill-mask` | Fill masked words in text |
| | `question-answering` | Answer questions from context |
| | `summarization` | Summarize long documents |
| | `translation` | Translate between languages |
| | `token-classification` | Named entity recognition |
| **Vision** | `image-classification` | Classify images into categories |
| | `object-detection` | Detect objects in images |
| | `image-segmentation` | Segment images by regions |
| | `depth-estimation` | Estimate depth maps |
| **Audio** | `automatic-speech-recognition` | Transcribe audio to text |
| | `audio-classification` | Classify audio clips |
| | `text-to-speech` | Generate speech from text |
| **Multimodal** | `image-to-text` | Generate captions for images |
| | `zero-shot-image-classification` | Classify images without training |

**Sources:** [README.md:28-32](), [packages/transformers/src/pipelines.js:77-105]()

## Runtime Environment Patterns

The library automatically detects the runtime environment and configures appropriate defaults:

```mermaid
graph TB
    subgraph "Runtime Detection<br/>packages/transformers/src/env.js"
        DetectRuntime["Runtime Detection Logic"]
        
        IsBrowser["IS_BROWSER_ENV<br/>window + document"]
        IsWorker["IS_WEBWORKER_ENV<br/>WorkerGlobalScope"]
        IsNode["IS_NODE_ENV<br/>process.release.name"]
    end
    
    subgraph "Environment Defaults"
        BrowserDefaults["Browser:<br/>• Remote models: true<br/>• Local models: false<br/>• Cache: Browser Cache API<br/>• Backend: WASM"]
        
        WorkerDefaults["Web Worker:<br/>• Remote models: true<br/>• Local models: false<br/>• Cache: Browser Cache API<br/>• Backend: WASM"]
        
        NodeDefaults["Node.js:<br/>• Remote models: true<br/>• Local models: true<br/>• Cache: File System<br/>• Backend: Native ONNX"]
    end
    
    DetectRuntime --> IsBrowser
    DetectRuntime --> IsWorker
    DetectRuntime --> IsNode
    
    IsBrowser --> BrowserDefaults
    IsWorker --> WorkerDefaults
    IsNode --> NodeDefaults
```

**Sources:** [packages/transformers/src/env.js:31-112](), [packages/transformers/src/env.js:179-186]()

## Installation Methods

The library supports multiple installation and import patterns:

### NPM Installation

```bash
npm i @huggingface/transformers
```

**Sources:** [README.md:44-45]()

### CDN Import

```html
<script type="module">
    import { pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.2.0';
    
    const pipe = await pipeline('sentiment-analysis');
    const result = await pipe('I love transformers!');
    console.log(result);
</script>
```

**Sources:** [README.md:49-52]()

## Key Example Categories

Examples in the child pages are organized by complexity and use case:

### Quick Start Examples ([Quick Start Examples](#16.1))
For details, see [Quick Start Examples](#16.1). Covers basic sentiment analysis, text generation, and image classification using the pipeline API.

### Environment-Specific Examples ([Environment-Specific Examples](#16.2))
For details, see [Environment-Specific Examples](#16.2). Covers tutorials for Vanilla JS, React (using Web Workers), Electron, and Browser Extensions.
- **Vanilla JS**: Uses `FileReader` and `pipeline` in a single thread [packages/transformers/docs/source/tutorials/vanilla-js.md:148-185]().
- **React**: Implements a Singleton pattern for the pipeline within a Web Worker to avoid UI freezing [packages/transformers/docs/source/tutorials/react.md:58-73]().

### Advanced Usage Patterns ([Advanced Usage Patterns](#16.3))
For details, see [Advanced Usage Patterns](#16.3). Covers custom caching, quantization (`dtype: 'q4'`), streaming generation (`TextStreamer`), and WebGPU acceleration.

**Sources:** [README.md:106-127](), [packages/transformers/docs/source/tutorials/react.md:58-73]()

## Example Discovery Resources

Additional example resources are available in the ecosystem:

| Resource | Description | Link Reference |
|----------|-------------|----------------|
| Demo Applications | Wide variety of demo apps and templates | [README.md:129]() |
| Hugging Face Spaces | Official Transformers.js template | [README.md:129]() |
| GitHub Examples Repo | Community examples repository | [README.md:129]() |

**Sources:** [README.md:129-129]()

---

