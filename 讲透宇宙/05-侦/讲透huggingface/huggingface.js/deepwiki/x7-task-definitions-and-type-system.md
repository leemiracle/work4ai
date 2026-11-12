<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/huggingface.js · extra page Task Definitions and Type System · fetched 2026-10-26 -->

# Task Definitions and Type System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/inference/src/tasks/cv/imageTextToImage.ts](packages/inference/src/tasks/cv/imageTextToImage.ts)
- [packages/inference/src/tasks/cv/imageTextToVideo.ts](packages/inference/src/tasks/cv/imageTextToVideo.ts)
- [packages/inference/src/tasks/index.ts](packages/inference/src/tasks/index.ts)
- [packages/tasks/.gitignore](packages/tasks/.gitignore)
- [packages/tasks/package.json](packages/tasks/package.json)
- [packages/tasks/pnpm-lock.yaml](packages/tasks/pnpm-lock.yaml)
- [packages/tasks/src/pipelines.ts](packages/tasks/src/pipelines.ts)
- [packages/tasks/src/tasks/chat-completion/inference.ts](packages/tasks/src/tasks/chat-completion/inference.ts)
- [packages/tasks/src/tasks/chat-completion/spec/input.json](packages/tasks/src/tasks/chat-completion/spec/input.json)
- [packages/tasks/src/tasks/chat-completion/spec/output.json](packages/tasks/src/tasks/chat-completion/spec/output.json)
- [packages/tasks/src/tasks/chat-completion/spec/stream_output.json](packages/tasks/src/tasks/chat-completion/spec/stream_output.json)
- [packages/tasks/src/tasks/image-text-to-image/about.md](packages/tasks/src/tasks/image-text-to-image/about.md)
- [packages/tasks/src/tasks/image-text-to-image/data.ts](packages/tasks/src/tasks/image-text-to-image/data.ts)
- [packages/tasks/src/tasks/image-text-to-image/inference.ts](packages/tasks/src/tasks/image-text-to-image/inference.ts)
- [packages/tasks/src/tasks/index.ts](packages/tasks/src/tasks/index.ts)
- [packages/tasks/src/tasks/text-generation/inference.ts](packages/tasks/src/tasks/text-generation/inference.ts)
- [packages/tasks/src/tasks/text-generation/spec/input.json](packages/tasks/src/tasks/text-generation/spec/input.json)
- [packages/tasks/src/tasks/text-generation/spec/output.json](packages/tasks/src/tasks/text-generation/spec/output.json)
- [packages/tasks/src/tasks/text-generation/spec/stream_output.json](packages/tasks/src/tasks/text-generation/spec/stream_output.json)
- [packages/tasks/src/tasks/video-to-video/about.md](packages/tasks/src/tasks/video-to-video/about.md)
- [packages/tasks/src/tasks/video-to-video/data.ts](packages/tasks/src/tasks/video-to-video/data.ts)

</details>



This document covers the task taxonomy, data structures, and type generation system implemented in the `@huggingface/tasks` package. It explains how machine learning tasks are defined, organized by modality, and how TypeScript type definitions are automatically generated from JSON Schema specifications. For information about how these types are consumed by the inference library, see [Task Functions and Types](#2.1.3). For details on model library mappings and code snippets, see [Model Libraries and Snippets](#3.1.2).

## Overview of the Tasks Package

The `@huggingface/tasks` package serves as the canonical source of truth for ML task metadata across the Hugging Face ecosystem. It provides:

- **Task Taxonomy**: A hierarchical classification of 60+ ML tasks organized by modality
- **Type Definitions**: Auto-generated TypeScript interfaces for task inputs and outputs
- **Task Metadata**: Example models, datasets, metrics, and documentation for each task
- **Library Mappings**: Associations between tasks and compatible ML frameworks

The package exports this data as structured TypeScript types and constants that are imported by `@huggingface/inference`, `@huggingface/hub`, `@huggingface/widgets`, and documentation systems.

**Sources**: [packages/tasks/package.json:1-60](), [packages/tasks/src/tasks/index.ts:1-342]()

## Task Taxonomy and Pipeline Types

### PIPELINE_DATA Structure

The foundation of the task system is `PIPELINE_DATA`, a const object that defines all supported ML tasks. Each task has a standardized structure:

```mermaid
graph TB
    PIPELINE_DATA["PIPELINE_DATA<br/>(const object)"]
    
    TASK1["text-classification<br/>(PipelineData)"]
    TASK2["image-to-text<br/>(PipelineData)"]
    TASK3["automatic-speech-recognition<br/>(PipelineData)"]
    
    PROPS["PipelineData Properties"]
    NAME["name: string<br/>e.g. 'Text Classification'"]
    MOD["modality: Modality<br/>e.g. 'nlp', 'cv', 'audio'"]
    SUBTASKS["subtasks?: SubTask[]<br/>Optional granular tasks"]
    FLAGS["hideInModels?: boolean<br/>hideInDatasets?: boolean"]
    
    PIPELINE_DATA --> TASK1
    PIPELINE_DATA --> TASK2
    PIPELINE_DATA --> TASK3
    
    TASK1 --> PROPS
    PROPS --> NAME
    PROPS --> MOD
    PROPS --> SUBTASKS
    PROPS --> FLAGS
```

The `PipelineType` union type is derived from the keys of `PIPELINE_DATA`:

```typescript
export type PipelineType = keyof typeof PIPELINE_DATA;
// Results in: "text-classification" | "image-to-text" | "automatic-speech-recognition" | ...
```

**Sources**: [packages/tasks/src/pipelines.ts:15-652]()

### Modality Organization

Tasks are organized into seven primary modalities defined in the `MODALITIES` constant:

| Modality | Label | Example Tasks |
|----------|-------|---------------|
| `nlp` | Natural Language Processing | text-classification, text-generation, translation |
| `cv` | Computer Vision | image-classification, object-detection, text-to-image |
| `audio` | Audio | automatic-speech-recognition, text-to-speech |
| `multimodal` | Multimodal | visual-question-answering, document-question-answering |
| `tabular` | Tabular | tabular-classification, tabular-regression |
| `rl` | Reinforcement Learning | reinforcement-learning, robotics |
| `other` | Other | graph-ml, other |

```mermaid
graph LR
    MODALITIES["MODALITIES<br/>const array"]
    
    NLP["nlp"]
    CV["cv"]
    AUDIO["audio"]
    MULTI["multimodal"]
    TAB["tabular"]
    RL["rl"]
    OTHER["other"]
    
    NLP_TASKS["text-classification<br/>token-classification<br/>text-generation<br/>translation<br/>summarization<br/>..."]
    CV_TASKS["image-classification<br/>object-detection<br/>text-to-image<br/>image-segmentation<br/>..."]
    AUDIO_TASKS["audio-classification<br/>automatic-speech-recognition<br/>text-to-speech<br/>..."]
    
    MODALITIES --> NLP
    MODALITIES --> CV
    MODALITIES --> AUDIO
    MODALITIES --> MULTI
    MODALITIES --> TAB
    MODALITIES --> RL
    MODALITIES --> OTHER
    
    NLP --> NLP_TASKS
    CV --> CV_TASKS
    AUDIO --> AUDIO_TASKS
```

**Sources**: [packages/tasks/src/pipelines.ts:1-13]()

### Subtask Hierarchy

Many pipeline types include optional subtasks for more granular classification:

```mermaid
graph TD
    TC["text-classification"]
    
    ST1["acceptability-classification"]
    ST2["sentiment-classification"]
    ST3["intent-classification"]
    ST4["multi-label-classification"]
    ST5["...17 more subtasks"]
    
    TC --> ST1
    TC --> ST2
    TC --> ST3
    TC --> ST4
    TC --> ST5
    
    STRUCT["SubTask Interface"]
    TYPE["type: string<br/>e.g. 'sentiment-classification'"]
    NAME["name: string<br/>e.g. 'Sentiment Classification'"]
    
    ST1 --> STRUCT
    STRUCT --> TYPE
    STRUCT --> NAME
```

The `SUBTASK_TYPES` array is derived from all subtasks across all pipeline types using:

```typescript
export const SUBTASK_TYPES = Object.values(PIPELINE_DATA)
  .flatMap((data) => ("subtasks" in data ? data.subtasks : []))
  .map((s) => s.type);
```

**Sources**: [packages/tasks/src/pipelines.ts:22-45](), [packages/tasks/src/pipelines.ts:660-662]()

## Task Data Structures

### TaskData Interface

Each task can have associated metadata defined by the `TaskData` interface:

```typescript
export interface TaskData {
  datasets: ExampleRepo[];       // Example datasets
  demo: TaskDemo;                // Widget demo configuration
  id: PipelineType;              // Task identifier
  canonicalId?: PipelineType;    // Canonical task if alias
  isPlaceholder?: boolean;       // If using placeholder data
  label: string;                 // Display name
  libraries: ModelLibraryKey[];  // Compatible ML frameworks
  metrics: ExampleRepo[];        // Evaluation metrics
  models: ExampleRepo[];         // Example models
  spaces: ExampleRepo[];         // Example Spaces
  summary: string;               // Task description
  widgetModels: string[];        // Models for widget
  youtubeId?: string;            // Tutorial video
}
```

The `TaskDemo` type specifies widget demonstration data with typed entries:

| Entry Type | Fields | Purpose |
|------------|--------|---------|
| `audio` | filename | Audio file reference |
| `chart` | data (label/score pairs) | Chart visualization |
| `img` | filename | Image file reference |
| `tabular` | table (string[][]) | Tabular data display |
| `text` | content, label | Text content |
| `text-with-tokens` | text, tokens (with positions) | Annotated text |

**Sources**: [packages/tasks/src/tasks/index.ts:280-342]()

### TASKS_DATA Assembly

The `TASKS_DATA` record combines pipeline definitions with task-specific data:

```mermaid
graph TB
    PIPELINE["PIPELINE_DATA"]
    TASK_FILES["Task-specific data files<br/>e.g. text-generation/data.ts"]
    PLACEHOLDER["placeholder/data.ts"]
    
    GET_DATA["getData() function"]
    
    TASKS_DATA["TASKS_DATA<br/>Record&lt;PipelineType, TaskData | undefined&gt;"]
    
    TASK1["'text-generation': TaskData"]
    TASK2["'image-to-text': TaskData"]
    TASK3["'graph-ml': undefined"]
    
    PIPELINE --> GET_DATA
    TASK_FILES --> GET_DATA
    PLACEHOLDER --> GET_DATA
    
    GET_DATA --> TASKS_DATA
    
    TASKS_DATA --> TASK1
    TASKS_DATA --> TASK2
    TASKS_DATA --> TASK3
    
    COMPONENTS["TaskData components"]
    ID["id: from PipelineType"]
    LABEL["label: from PIPELINE_DATA.name"]
    LIBS["libraries: from TASKS_MODEL_LIBRARIES"]
    REST["rest: from task data file"]
    
    TASK1 --> COMPONENTS
    COMPONENTS --> ID
    COMPONENTS --> LABEL
    COMPONENTS --> LIBS
    COMPONENTS --> REST
```

The `getData()` function at [packages/tasks/src/tasks/index.ts:207-214]() merges:

1. Task-specific data (datasets, models, summary, etc.)
2. Pipeline metadata (id, label from `PIPELINE_DATA`)
3. Library mappings (from `TASKS_MODEL_LIBRARIES`)

Tasks without specific data use placeholder values, while some tasks (like `graph-ml`, `multiple-choice`) are explicitly set to `undefined` to indicate no task page should be generated.

**Sources**: [packages/tasks/src/tasks/index.ts:207-278]()

## Model Library Mappings

### TASKS_MODEL_LIBRARIES Structure

The `TASKS_MODEL_LIBRARIES` record maps each `PipelineType` to an array of compatible ML library identifiers:

```typescript
export const TASKS_MODEL_LIBRARIES: Record<PipelineType, ModelLibraryKey[]> = {
  "text-classification": ["adapter-transformers", "setfit", "spacy", "transformers", "transformers.js"],
  "text-generation": ["transformers", "transformers.js"],
  "image-classification": ["keras", "timm", "transformers", "transformers.js"],
  "automatic-speech-recognition": ["espnet", "nemo", "speechbrain", "transformers", "transformers.js"],
  // ... 60+ more mappings
}
```

This mapping enables:
- Filtering models by library in the Hub UI
- Generating library-specific code snippets
- Validating model compatibility with tasks

```mermaid
graph LR
    TASK["Task: text-classification"]
    
    LIBS["Compatible Libraries"]
    L1["adapter-transformers"]
    L2["setfit"]
    L3["spacy"]
    L4["transformers"]
    L5["transformers.js"]
    
    TASK --> LIBS
    LIBS --> L1
    LIBS --> L2
    LIBS --> L3
    LIBS --> L4
    LIBS --> L5
    
    USAGE["Used By"]
    U1["Hub model filtering"]
    U2["Code snippet generation"]
    U3["Library compatibility checks"]
    
    LIBS --> USAGE
    USAGE --> U1
    USAGE --> U2
    USAGE --> U3
```

**Sources**: [packages/tasks/src/tasks/index.ts:134-200]()

## Type Generation System

### JSON Schema Specifications

Input and output types for inference tasks are defined using JSON Schema in `spec/` directories within each task folder. For example, `chat-completion` has:

- `spec/input.json` - Defines `ChatCompletionInput` structure
- `spec/output.json` - Defines `ChatCompletionOutput` structure  
- `spec/stream_output.json` - Defines `ChatCompletionStreamOutput` structure

The schemas use JSON Schema draft-06 specification with features like:
- `$ref` for internal references
- `$defs` for reusable definitions
- `oneOf`, `allOf` for union/intersection types
- `nullable`, `required`, `format` for validation

Example schema structure from [packages/tasks/src/tasks/chat-completion/spec/input.json:1-50]():

```json
{
  "$id": "/inference/schemas/chat-completion/input.json",
  "$schema": "http://json-schema.org/draft-06/schema#",
  "title": "ChatCompletionInput",
  "type": "object",
  "required": ["messages"],
  "properties": {
    "messages": {
      "type": "array",
      "items": { "$ref": "#/$defs/ChatCompletionInputMessage" }
    },
    "temperature": { "type": "number", "format": "float" },
    // ... more properties
  },
  "$defs": {
    "ChatCompletionInputMessage": { /* definition */ }
  }
}
```

**Sources**: [packages/tasks/src/tasks/chat-completion/spec/input.json:1-433](), [packages/tasks/src/tasks/text-generation/spec/input.json:1-247]()

### Code Generation Pipeline

The `inference-codegen` script transforms JSON schemas into TypeScript interfaces:

```mermaid
graph TD
    SCHEMA1["JSON Schema Files<br/>*/spec/input.json<br/>*/spec/output.json<br/>*/spec/stream_output.json"]
    
    SCRIPT["inference-codegen script<br/>packages/tasks/scripts/"]
    
    TS_FILES["Generated TypeScript<br/>*/inference.ts"]
    
    INTERFACES["TypeScript Interfaces"]
    I1["ChatCompletionInput"]
    I2["ChatCompletionOutput"]
    I3["ChatCompletionStreamOutput"]
    I4["TextGenerationInput"]
    I5["TextGenerationOutput"]
    
    INDEX["tasks/index.ts"]
    EXPORTS["Re-exported types"]
    
    CONSUMERS["Consumers"]
    C1["@huggingface/inference"]
    C2["@huggingface/widgets"]
    C3["Documentation sites"]
    
    SCHEMA1 --> SCRIPT
    SCRIPT --> TS_FILES
    TS_FILES --> INTERFACES
    INTERFACES --> I1
    INTERFACES --> I2
    INTERFACES --> I3
    INTERFACES --> I4
    INTERFACES --> I5
    
    TS_FILES --> INDEX
    INDEX --> EXPORTS
    
    EXPORTS --> CONSUMERS
    CONSUMERS --> C1
    CONSUMERS --> C2
    CONSUMERS --> C3
```

The generation happens during the build process defined in [packages/tasks/package.json:44]():

```json
"prepublishOnly": "pnpm --filter tasks-gen inference-codegen && git diff --name-only --exit-code src && pnpm run build"
```

This ensures generated types are always in sync with schemas before publishing.

**Sources**: [packages/tasks/package.json:39-51](), [packages/tasks/src/tasks/chat-completion/inference.ts:1-11]()

### Generated TypeScript Interface Structure

The generated interfaces follow consistent patterns. Example from chat completion:

```typescript
// Generated header comment
/**
 * Inference code generated from the JSON schema spec in ./spec
 * Using src/scripts/inference-codegen
 */

// Input interface with all parameters
export interface ChatCompletionInput {
  frequency_penalty?: number;
  max_tokens?: number;
  messages: ChatCompletionInputMessage[];  // Required field
  temperature?: number;
  // ... 15+ more optional parameters
  [property: string]: unknown;  // Allow additional properties
}

// Nested type definitions
export interface ChatCompletionInputMessage {
  content?: ChatCompletionInputMessageContent;
  role: string;
  tool_calls?: ChatCompletionInputToolCall[];
  [property: string]: unknown;
}

// Union types for flexible inputs
export type ChatCompletionInputMessageContent = 
  | ChatCompletionInputMessageChunk[] 
  | string;

// Output interfaces
export interface ChatCompletionOutput {
  choices: ChatCompletionOutputComplete[];
  created: number;
  id: string;
  model: string;
  usage: ChatCompletionOutputUsage;
  [property: string]: unknown;
}
```

Key characteristics:
- All interfaces have `[property: string]: unknown` for extensibility
- Required vs optional fields match schema specifications
- Complex nested structures are broken into separate interfaces
- Union types use TypeScript `|` operator for `oneOf` schemas
- Documentation comments preserved from schema descriptions

**Sources**: [packages/tasks/src/tasks/chat-completion/inference.ts:13-329](), [packages/tasks/src/tasks/text-generation/inference.ts:13-187]()

### Type Export and Re-export Pattern

Generated types are consolidated and re-exported through [packages/tasks/src/tasks/index.ts:53-128]():

```typescript
export type * from "./audio-classification/inference.js";
export type * from "./automatic-speech-recognition/inference.js";
export type {
  ChatCompletionInput,
  ChatCompletionInputMessage,
  ChatCompletionOutput,
  ChatCompletionStreamOutput,
  // ... explicitly named exports for important types
} from "./chat-completion/inference.js";
export type {
  TextGenerationInput,
  TextGenerationOutput,
  TextGenerationStreamOutput,
  // ... explicitly named exports
} from "./text-generation/inference.js";
// ... 30+ more task type exports
```

This creates a single import point for consumers:

```typescript
import type { 
  ChatCompletionInput,
  TextGenerationOutput,
  ImageClassificationInput 
} from "@huggingface/tasks";
```

**Sources**: [packages/tasks/src/tasks/index.ts:53-128]()

## Integration with Inference Package

The generated types are consumed by `@huggingface/inference` to ensure type safety:

```mermaid
graph TB
    TASKS["@huggingface/tasks"]
    TYPES["Generated Types<br/>ChatCompletionInput<br/>TextGenerationOutput<br/>etc."]
    
    INF["@huggingface/inference"]
    FUNCS["Task Functions"]
    
    CHAT["chatCompletion()"]
    TEXT["textGeneration()"]
    IMG["imageClassification()"]
    
    ARGS["Function Arguments"]
    A1["ChatCompletionArgs extends<br/>BaseArgs & ChatCompletionInput"]
    A2["TextGenerationArgs extends<br/>BaseArgs & TextGenerationInput"]
    
    RUNTIME["Runtime Behavior"]
    R1["Type checking at dev time"]
    R2["IntelliSense support"]
    R3["Payload validation"]
    
    TASKS --> TYPES
    TYPES --> INF
    INF --> FUNCS
    FUNCS --> CHAT
    FUNCS --> TEXT
    FUNCS --> IMG
    
    CHAT --> ARGS
    TEXT --> ARGS
    ARGS --> A1
    ARGS --> A2
    
    ARGS --> RUNTIME
    RUNTIME --> R1
    RUNTIME --> R2
    RUNTIME --> R3
```

Example usage from the inference package:

```typescript
// From packages/inference/src/tasks/nlp/chatCompletion.ts
import type { ChatCompletionInput } from "@huggingface/tasks";

export type ChatCompletionArgs = BaseArgs & ChatCompletionInput;

export async function chatCompletion(
  args: ChatCompletionArgs, 
  options?: Options
): Promise<ChatCompletionOutput> {
  // Implementation uses typed args
}
```

This ensures that:
1. API consumers get full TypeScript autocomplete
2. Invalid parameters are caught at compile time
3. Types stay synchronized between schema specs and implementation
4. Breaking changes in schemas are caught by TypeScript compiler

**Sources**: [packages/inference/src/tasks/index.ts:1-47]()

## Complete Type System Flow

```mermaid
graph TD
    TGI["Text Generation Inference Server<br/>OpenAPI specs"]
    
    JSON_IMPORT["inference-tgi-import.ts<br/>Import from TGI specs"]
    
    JSON_SCHEMA["JSON Schema Files<br/>chat-completion/spec/input.json<br/>text-generation/spec/input.json<br/>30+ task schemas"]
    
    CODEGEN["inference-codegen script"]
    
    TS_GEN["Generated TypeScript<br/>chat-completion/inference.ts<br/>text-generation/inference.ts<br/>30+ inference.ts files"]
    
    INDEX["tasks/index.ts<br/>Consolidated exports"]
    
    BUILD["tshy build<br/>ESM + CJS outputs"]
    
    DIST["dist/ directory<br/>Published package"]
    
    CONSUMERS["Package Consumers"]
    
    INF_PKG["@huggingface/inference<br/>Uses types for API"]
    
    HUB_PKG["@huggingface/hub<br/>Uses task metadata"]
    
    WIDGETS["@huggingface/widgets<br/>Uses demo configs"]
    
    DOCS["Documentation sites<br/>Renders task pages"]
    
    TGI --> JSON_IMPORT
    JSON_IMPORT --> JSON_SCHEMA
    JSON_SCHEMA --> CODEGEN
    CODEGEN --> TS_GEN
    TS_GEN --> INDEX
    INDEX --> BUILD
    BUILD --> DIST
    
    DIST --> CONSUMERS
    CONSUMERS --> INF_PKG
    CONSUMERS --> HUB_PKG
    CONSUMERS --> WIDGETS
    CONSUMERS --> DOCS
```

The complete flow ensures:
- **Source of Truth**: TGI server specs define API contracts
- **Type Safety**: JSON schemas generate TypeScript types automatically
- **Distribution**: Dual ESM/CJS builds support all environments
- **Consistency**: Single build step ensures all artifacts stay in sync
- **Validation**: Git diff check in prepublish prevents accidental manual edits

**Sources**: [packages/tasks/package.json:44](), [packages/tasks/src/tasks/chat-completion/inference.ts:1-11](), [packages/tasks/src/tasks/text-generation/inference.ts:1-11]()

---

