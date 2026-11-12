<!-- source: DeepWiki mcp.deepwiki.com · repo openai/build-hours · page 4 Image Generation System · fetched 2026-10-26 -->

# Image Generation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [13-image-gen/imagegen-demo/README.md](13-image-gen/imagegen-demo/README.md)
- [13-image-gen/imagegen-demo/src/app/api/stream/route.ts](13-image-gen/imagegen-demo/src/app/api/stream/route.ts)

</details>



## Purpose and Scope

The Image Generation System is a Next.js web application that provides AI-powered image generation and post-processing capabilities using OpenAI's image generation APIs. The system allows users to upload reference images, apply custom style modifiers, and generate stylized images through a streaming interface. Additionally, it provides post-processing functionality to overlay SVG borders on images.

This system was originally developed for the OpenAI SF Frontiers event and has been repurposed for Build Hours demonstrations. For information about other AI model integrations, see [Fine-tuning Systems](#3). For agent-based systems, see [Agent Systems](#6).

## System Architecture

The Image Generation System is built as a Next.js application with API routes handling image generation and processing. The system integrates with OpenAI's responses API using the `gpt-4.1` model and image generation tools.

### Core Components Architecture

```mermaid
graph TB
    subgraph "Next.js Application"
        UI["Interactive UI"]
        API_STREAM["api/stream/route.ts"]
        API_GENERATE["api/generate"]
        API_PROCESS["api/process"]
    end
    
    subgraph "OpenAI Integration"
        RESPONSES_API["responses.create()"]
        IMAGE_GEN_TOOL["image_generation tool"]
        GPT41["gpt-4.1 model"]
    end
    
    subgraph "Processing Pipeline"
        MODIFIER_MAP["modifierPrompts mapping"]
        STREAM_HANDLER["TransformStream"]
        SVG_OVERLAY["Sharp + SVG border"]
    end
    
    subgraph "File System"
        SVG_FILE["public/OpenAI_Frontiers-2025.svg"]
        ENV_FILE[".env.local"]
    end
    
    UI --> API_STREAM
    UI --> API_GENERATE
    UI --> API_PROCESS
    
    API_STREAM --> MODIFIER_MAP
    API_STREAM --> RESPONSES_API
    RESPONSES_API --> IMAGE_GEN_TOOL
    RESPONSES_API --> GPT41
    
    API_STREAM --> STREAM_HANDLER
    API_PROCESS --> SVG_OVERLAY
    API_PROCESS --> SVG_FILE
    
    ENV_FILE --> API_STREAM
```

Sources: [13-image-gen/imagegen-demo/README.md:1-88](), [13-image-gen/imagegen-demo/src/app/api/stream/route.ts:1-89]()

## Style Modifier System

The system implements a comprehensive style modifier mapping that transforms user-selected modifiers into detailed prompts for image generation. Each modifier corresponds to a specific artistic style or theme.

### Style Modifier Mapping

| Modifier Key | Style Description | Primary Theme |
|--------------|-------------------|---------------|
| `ghibli-style` | Studio Ghibli aesthetic | Soft colors, dreamy atmosphere, magical elements |
| `paperback` | 1980s sci-fi book cover | Vintage paperback with dramatic lighting |
| `action-figure` | Retro toy packaging | 1980s-1990s action figure box design |
| `lego-minifigure-style` | LEGO aesthetic | Blocky proportions, glossy plastic texture |
| `japanese-anime-movie-poster` | Anime theatrical poster | Hand-painted cel-style, dramatic gradients |
| `80s-cave` | Retro-futurist arcade | CRT monitors, circuit boards, neon lighting |
| `mission-patch` | NASA mission patch | Embroidered design with OpenAI branding |
| `knitted-cozy-scene` | Cozy textile art | Chunky yarn, fireplace setting |
| `comic-panel` | Comic book format | Multi-panel story narrative |

### Modifier Processing Flow

```mermaid
graph LR
    subgraph "Input Processing"
        IMAGE_UPLOAD["FormData image"]
        MODIFIER_SELECT["FormData modifier"]
    end
    
    subgraph "Prompt Generation"
        MODIFIER_LOOKUP["modifierPrompts[modifier]"]
        PROMPT_BUILD["mappedPrompt construction"]
        FALLBACK["Generic prompt fallback"]
    end
    
    subgraph "OpenAI Request"
        BASE64_CONV["Buffer.from().toString('base64')"]
        DATA_URL["data:image/type;base64,content"]
        RESPONSES_CREATE["client.responses.create()"]
    end
    
    IMAGE_UPLOAD --> BASE64_CONV
    MODIFIER_SELECT --> MODIFIER_LOOKUP
    MODIFIER_LOOKUP --> PROMPT_BUILD
    MODIFIER_LOOKUP --> FALLBACK
    
    BASE64_CONV --> DATA_URL
    PROMPT_BUILD --> RESPONSES_CREATE
    DATA_URL --> RESPONSES_CREATE
```

Sources: [13-image-gen/imagegen-demo/src/app/api/stream/route.ts:15-36]()

## Streaming Image Generation

The system implements streaming image generation using OpenAI's responses API with real-time partial image updates. This provides users with progressive feedback during the generation process.

### Streaming Implementation

The streaming process uses the `responses.create()` method with specific configuration for image generation:

```mermaid
graph TB
    subgraph "Request Configuration"
        MODEL["model: 'gpt-4.1'"]
        INPUT_CONTENT["input: text + image_url"]
        TOOLS_CONFIG["tools: image_generation"]
        STREAM_ENABLE["stream: true"]
    end
    
    subgraph "Tool Parameters"
        PARTIAL_IMAGES["partial_images: 3"]
        SIZE["size: '1024x1024'"]
        QUALITY["quality: 'high'"]
        MODERATION["moderation: 'low'"]
        TOOL_CHOICE["tool_choice: 'required'"]
    end
    
    subgraph "Stream Processing"
        TRANSFORM_STREAM["TransformStream()"]
        EVENT_LOOP["for await (event of openaiStream)"]
        PARTIAL_HANDLER["response.image_generation_call.partial_image"]
        COMPLETE_HANDLER["response.image_generation_call.completed"]
    end
    
    MODEL --> INPUT_CONTENT
    INPUT_CONTENT --> TOOLS_CONFIG
    TOOLS_CONFIG --> PARTIAL_IMAGES
    PARTIAL_IMAGES --> SIZE
    
    STREAM_ENABLE --> TRANSFORM_STREAM
    TRANSFORM_STREAM --> EVENT_LOOP
    EVENT_LOOP --> PARTIAL_HANDLER
    EVENT_LOOP --> COMPLETE_HANDLER
```

### Event Processing

The streaming handler processes two main event types:

1. **Partial Image Events** (`response.image_generation_call.partial_image`): Provides incremental image updates as base64 data
2. **Completion Events** (`response.image_generation_call.completed`): Signals final image generation completion

Sources: [13-image-gen/imagegen-demo/src/app/api/stream/route.ts:37-87]()

## Post-processing Pipeline

The system includes image post-processing capabilities using the Sharp library to overlay SVG borders on generated or uploaded images. This functionality is accessible through the `/api/process` endpoint.

### SVG Overlay Configuration

The post-processing system expects an SVG border file located at `public/OpenAI_Frontiers-2025.svg`. This path can be customized by modifying the configuration in the process route handler.

### Processing Workflow

```mermaid
graph LR
    subgraph "Input"
        ORIG_IMAGE["Original image upload"]
        SVG_BORDER["SVG border file"]
    end
    
    subgraph "Sharp Processing"
        SHARP_LOAD["Sharp.load()"]
        SVG_OVERLAY["composite() overlay"]
        OUTPUT_FORMAT["format conversion"]
    end
    
    subgraph "Output"
        PROCESSED_IMAGE["Image with border"]
        DOWNLOAD["Download response"]
    end
    
    ORIG_IMAGE --> SHARP_LOAD
    SVG_BORDER --> SVG_OVERLAY
    SHARP_LOAD --> SVG_OVERLAY
    SVG_OVERLAY --> OUTPUT_FORMAT
    OUTPUT_FORMAT --> PROCESSED_IMAGE
    PROCESSED_IMAGE --> DOWNLOAD
```

Sources: [13-image-gen/imagegen-demo/README.md:61-66]()

## API Endpoints and Configuration

The Image Generation System exposes three main API endpoints for different functionality:

### API Endpoint Structure

| Endpoint | Method | Purpose | Key Features |
|----------|--------|---------|--------------|
| `/api/stream` | POST | Streaming image generation | Real-time partial updates, style modifiers |
| `/api/generate` | POST | Standard image generation | Batch processing, style application |
| `/api/process` | POST | Image post-processing | SVG overlay, Sharp integration |

### Environment Configuration

The system requires OpenAI API key configuration through environment variables:

```mermaid
graph TB
    subgraph "Environment Setup"
        ENV_LOCAL[".env.local"]
        OPENAI_KEY["OPENAI_API_KEY"]
        NEXT_CONFIG["Next.js configuration"]
    end
    
    subgraph "Runtime Configuration"
        EDGE_RUNTIME["export const runtime = 'edge'"]
        OPENAI_CLIENT["new OpenAI()"]
        API_ROUTES["API route handlers"]
    end
    
    ENV_LOCAL --> OPENAI_KEY
    OPENAI_KEY --> OPENAI_CLIENT
    NEXT_CONFIG --> EDGE_RUNTIME
    EDGE_RUNTIME --> API_ROUTES
    OPENAI_CLIENT --> API_ROUTES
```

### Deployment and Development

The system supports both development and production deployment configurations:

- **Development**: `npm run dev` starts the development server with hot reloading
- **Production**: `npm run build && npm run start` creates optimized production build
- **Deployment**: Compatible with Vercel deployment platform

Sources: [13-image-gen/imagegen-demo/README.md:33-87](), [13-image-gen/imagegen-demo/src/app/api/stream/route.ts:1-6]()

---

