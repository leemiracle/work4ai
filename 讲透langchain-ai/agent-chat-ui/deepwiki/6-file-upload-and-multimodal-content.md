<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/agent-chat-ui · page 6 File Upload and Multimodal Content · fetched 2026-10-26 -->

# File Upload and Multimodal Content

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/thread/ContentBlocksPreview.tsx](src/components/thread/ContentBlocksPreview.tsx)
- [src/components/thread/MultimodalPreview.tsx](src/components/thread/MultimodalPreview.tsx)
- [src/hooks/use-file-upload.tsx](src/hooks/use-file-upload.tsx)
- [src/lib/multimodal-utils.ts](src/lib/multimodal-utils.ts)

</details>



This document covers the file upload system and multimodal content handling within the Agent Chat UI. The system enables users to attach images and PDF files to their messages, which are then processed, encoded, and displayed within the chat interface.

For information about how multimodal content is rendered within messages, see [Message System](#3). For details on thread management and message display, see [Thread Component](#2.1).

## Overview

The multimodal content system provides comprehensive support for file uploads through multiple input methods: traditional file selection, drag-and-drop, and clipboard paste operations. The system converts uploaded files into `Base64ContentBlock` objects that conform to LangChain's message format standards, enabling seamless integration with AI agents that support multimodal inputs.

**Supported File Types:**
- Images: JPEG, PNG, GIF, WEBP
- Documents: PDF

Sources: [src/lib/multimodal-utils.ts:8-14](), [src/hooks/use-file-upload.tsx:6-12]()

## File Processing Pipeline

The file upload system follows a structured pipeline that converts raw files into standardized content blocks suitable for AI processing.

```mermaid
graph TD
    UserFile["User selects/drops/pastes file"] --> FileValidation["File type validation"]
    FileValidation --> DuplicateCheck["Duplicate detection"]
    DuplicateCheck --> FileConversion["fileToContentBlock()"]
    
    FileConversion --> ImageBlock["Image Content Block"]
    FileConversion --> PDFBlock["PDF Content Block"]
    
    ImageBlock --> Base64Encoding["Base64 encoding with metadata"]
    PDFBlock --> Base64Encoding
    
    Base64Encoding --> ContentBlockArray["contentBlocks state array"]
    ContentBlockArray --> PreviewRender["MultimodalPreview rendering"]
    ContentBlockArray --> MessageAttach["Attachment to user message"]
    
    FileValidation --> ValidationError["Toast error notification"]
    DuplicateCheck --> DuplicateError["Toast error notification"]
```

### Core Processing Function

The `fileToContentBlock` function in [src/lib/multimodal-utils.ts:5-43]() serves as the central conversion utility:

```mermaid
graph LR
    File["File object"] --> TypeCheck["MIME type validation"]
    TypeCheck --> ImagePath["Image processing path"]
    TypeCheck --> PDFPath["PDF processing path"]
    
    ImagePath --> ImageContentBlock["Base64ContentBlock type: 'image'"]
    PDFPath --> PDFContentBlock["Base64ContentBlock type: 'file'"]
    
    ImageContentBlock --> Metadata1["metadata: {name: filename}"]
    PDFContentBlock --> Metadata2["metadata: {filename: filename}"]
```

The function creates different content block structures based on file type:
- **Images**: `type: "image"` with `metadata.name`
- **PDFs**: `type: "file"` with `metadata.filename`

Sources: [src/lib/multimodal-utils.ts:25-42]()

## Upload Mechanisms

The `useFileUpload` hook provides three distinct upload mechanisms, each with comprehensive validation and error handling.

### File Input Upload

Traditional file selection through HTML input elements:

```mermaid
graph TD
    FileInput["<input type='file'>"] --> HandleFileUpload["handleFileUpload()"]
    HandleFileUpload --> FileArray["Array.from(files)"]
    FileArray --> ValidationSplit["Split valid/invalid files"]
    ValidationSplit --> DuplicateFilter["Filter duplicates"]
    DuplicateFilter --> BatchConversion["Promise.all(fileToContentBlock)"]
    BatchConversion --> StateUpdate["setContentBlocks()"]
```

Sources: [src/hooks/use-file-upload.tsx:47-80]()

### Drag and Drop System

A sophisticated drag and drop implementation with global event handling:

```mermaid
graph TD
    WindowDragEnter["window dragenter event"] --> DragCounter["dragCounter increment"]
    DragCounter --> DragOverState["setDragOver(true)"]
    
    WindowDrop["window drop event"] --> PreventDefault["e.preventDefault()"]
    PreventDefault --> ExtractFiles["Array.from(dataTransfer.files)"]
    ExtractFiles --> ProcessFiles["File validation and conversion"]
    ProcessFiles --> ResetDragState["Reset drag state"]
    
    WindowDragLeave["window dragleave event"] --> DecrementCounter["dragCounter decrement"]
    DecrementCounter --> CheckCounter{"counter <= 0?"}
    CheckCounter --> ResetDragOver["setDragOver(false)"]
```

The drag and drop system uses a counter-based approach to handle complex drag operations across multiple elements and windows.

Sources: [src/hooks/use-file-upload.tsx:87-147]()

### Clipboard Paste Integration

Paste functionality integrated with text input elements:

```mermaid
graph TD
    PasteEvent["onPaste event"] --> ClipboardItems["e.clipboardData.items"]
    ClipboardItems --> ExtractFiles["Extract files from clipboard"]
    ExtractFiles --> FileValidation["Validate file types"]
    FileValidation --> ProcessPastedFiles["Convert to content blocks"]
    ProcessPastedFiles --> UpdateState["Add to contentBlocks"]
```

Sources: [src/hooks/use-file-upload.tsx:200-258]()

## Content Block Structure

Content blocks follow the LangChain `Base64ContentBlock` interface with specific structures for different file types.

### Image Content Blocks

```typescript
{
  type: "image",
  source_type: "base64",
  mime_type: string, // e.g., "image/jpeg"
  data: string,      // Base64 encoded image data
  metadata: {
    name: string     // Original filename
  }
}
```

### PDF Content Blocks

```typescript
{
  type: "file",
  source_type: "base64", 
  mime_type: "application/pdf",
  data: string,      // Base64 encoded PDF data
  metadata: {
    filename: string // Original filename
  }
}
```

### Type Guard Function

The `isBase64ContentBlock` function [src/lib/multimodal-utils.ts:60-89]() provides runtime type checking for content blocks, supporting both legacy "file" type and newer "image" type blocks.

Sources: [src/lib/multimodal-utils.ts:26-42](), [src/lib/multimodal-utils.ts:60-89]()

## Preview Components

The system provides a hierarchical component structure for displaying uploaded content.

```mermaid
graph TD
    ContentBlocksPreview["ContentBlocksPreview"] --> MultimodalPreview["MultimodalPreview[]"]
    
    MultimodalPreview --> ImagePreview["Image preview with Next.js Image"]
    MultimodalPreview --> PDFPreview["PDF file icon with filename"]
    MultimodalPreview --> FallbackPreview["Unknown file type fallback"]
    
    ImagePreview --> RemoveButton["Remove button (X icon)"]
    PDFPreview --> RemoveButton
    FallbackPreview --> RemoveButton
    
    RemoveButton --> OnRemoveCallback["onRemove(idx) callback"]
    OnRemoveCallback --> StateUpdate["Update contentBlocks array"]
```

### MultimodalPreview Component

The `MultimodalPreview` component [src/components/thread/MultimodalPreview.tsx:14-120]() handles rendering of individual content blocks:

- **Images**: Rendered using Next.js `Image` component with proper sizing and aspect ratio
- **PDFs**: Displayed as file icons with filename labels
- **Unknown types**: Fallback display with generic file icon

### ContentBlocksPreview Component  

The `ContentBlocksPreview` wrapper [src/components/thread/ContentBlocksPreview.tsx:17-37]() manages collections of content blocks with consistent spacing and removal functionality.

Sources: [src/components/thread/MultimodalPreview.tsx:14-120](), [src/components/thread/ContentBlocksPreview.tsx:17-37]()

## Validation and Error Handling

The system implements comprehensive validation with user-friendly error messaging.

### File Type Validation

```mermaid
graph TD
    FileInput["File selection"] --> TypeCheck{"file.type in SUPPORTED_FILE_TYPES?"}
    TypeCheck --> ValidFile["Process file"]
    TypeCheck --> InvalidFile["Add to invalidFiles array"]
    
    InvalidFile --> ErrorToast["Toast: 'Unsupported file type'"]
    ErrorToast --> FilterOut["Exclude from processing"]
```

### Duplicate Detection

The system prevents duplicate uploads using filename and MIME type comparison:

```mermaid
graph TD
    NewFile["New file"] --> DuplicateCheck{"isDuplicate(file, contentBlocks)?"}
    DuplicateCheck --> UniqueFile["Add to uniqueFiles"]
    DuplicateCheck --> DuplicateFile["Add to duplicateFiles"]
    
    DuplicateFile --> DuplicateToast["Toast: 'Duplicate file(s) detected'"]
    DuplicateToast --> Skip["Skip processing"]
```

The duplicate detection logic [src/hooks/use-file-upload.tsx:27-45]() compares:
- **PDFs**: `filename` and `mime_type`
- **Images**: `name`, `mime_type` matching

Sources: [src/hooks/use-file-upload.tsx:27-45](), [src/hooks/use-file-upload.tsx:64-73](), [src/hooks/use-file-upload.tsx:124-133]()

## Integration with Thread System

Multimodal content integrates seamlessly with the broader thread and message system through standardized content block arrays.

```mermaid
graph LR
    useFileUpload["useFileUpload hook"] --> contentBlocks["contentBlocks state"]
    contentBlocks --> ThreadComponent["Thread component"]
    ThreadComponent --> UserMessage["Human message with attachments"]
    UserMessage --> LangGraphSDK["LangGraph SDK transmission"]
    
    LangGraphSDK --> AIAgent["AI agent processing"] 
    AIAgent --> MultimodalResponse["Agent response with context"]
```

The `getContentString` utility [src/components/thread/utils.ts:9-15]() extracts text summaries from multimodal messages for display in thread history and navigation contexts.

Sources: [src/components/thread/utils.ts:9-15]()

---

