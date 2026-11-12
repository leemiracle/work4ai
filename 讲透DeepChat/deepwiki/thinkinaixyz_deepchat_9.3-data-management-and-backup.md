> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/9.3-data-management-and-backup](https://deepwiki.com/thinkinaixyz/deepchat/9.3-data-management-and-backup)（Wayback 快照 2026-04-11）
> DeepWiki deepchat/9.3-data-management-and-backup

# File Content Preparation

  Relevant source files 
 - [src/main/presenter/filePresenter/BaseFileAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/BaseFileAdapter.ts)
 - [src/main/presenter/filePresenter/FileAdapterConstructor.ts](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileAdapterConstructor.ts)
 - [src/main/presenter/filePresenter/FilePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts)
 - [src/main/presenter/filePresenter/FileValidationService.ts](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts)
 - [src/main/presenter/filePresenter/ImageFileAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/ImageFileAdapter.ts)
 - [src/main/presenter/filePresenter/mime.ts](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/mime.ts)
 - [src/renderer/src/components/editor/mention/PromptParamsDialog.vue](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/renderer/src/components/editor/mention/PromptParamsDialog.vue)
 - [src/renderer/src/components/editor/mention/mention.ts](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/renderer/src/components/editor/mention/mention.ts)
 
  
## Purpose and Scope

 This document describes the file content preparation pipeline that transforms raw files into `MessageFile` objects ready for LLM consumption. The preparation process involves creating the appropriate file adapter, extracting metadata, processing file content, and calculating token counts.

 For information about adapter selection and MIME type detection, see [File Adapter Architecture](https://deepwiki.com/thinkinaixyz/deepchat/9.1-file-adapter-architecture) and [MIME Detection & Type Resolution](https://deepwiki.com/thinkinaixyz/deepchat/9.2-mime-detection-and-type-resolution). For validation of files for knowledge base processing, see [File Validation & Support](https://deepwiki.com/thinkinaixyz/deepchat/9.4-file-validation-and-support).

 
---

 
## The prepareFileCompletely Pipeline

 The `prepareFileCompletely` method in `FilePresenter` is the primary entry point for file content preparation. It orchestrates the complete workflow from raw file path to structured `MessageFile` object.

 
```

```

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts121-174](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L121-L174)

 
### Method Signature

 The method accepts three parameters:

 
| Parameter | Type | Description |
|---|---|---|
| absPath | string | Absolute path to the file to process |
| typeInfo | string? | Optional MIME type hint (bypasses detection if provided) |
| contentType | null \| 'origin' \| 'llm-friendly' | Controls which content extraction method is used |

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts121-124](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L121-L124)

 
### Pipeline Stages

 **Stage 1: Adapter Creation**

 The pipeline begins by creating an appropriate file adapter using `createFileAdapter`. This method uses the MIME type (either provided via `typeInfo` or detected automatically) to instantiate the correct adapter subclass from the adapter map.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts68-91](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L68-L91) [src/main/presenter/filePresenter/FilePresenter.ts128](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L128-L128)

 **Stage 2: File Processing**

 The adapter's `processFile()` method extracts basic file metadata including file size, creation date, modification date, and file-specific descriptions. This metadata is stored in the adapter's `fileMetaData` property.

 **Sources:** [src/main/presenter/filePresenter/BaseFileAdapter.ts43-68](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/BaseFileAdapter.ts#L43-L68) [src/main/presenter/filePresenter/FilePresenter.ts131](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L131-L131)

 **Stage 3: Content Extraction**

 Depending on the `contentType` parameter, one of three content extraction paths is taken:

 
 - **`'llm-friendly'`**: Calls `adapter.getLLMContent()` - returns content optimized for LLM processing (e.g., compressed images as base64)
 - **`'origin'`**: Calls `adapter.getContent()` - returns raw or minimally processed content
 - **`null` or default**: Content is set to `null` (metadata-only mode)
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts133-143](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L133-L143)

 **Stage 4: Thumbnail Generation**

 If the adapter supports thumbnails (checked via `adapter.getThumbnail`), a thumbnail is generated. This is primarily used for image files.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts144](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L144-L144)

 **Stage 5: Token Calculation**

 Token counts are calculated based on file type:

 
 - **Image files**: Uses pixel-based calculation via `calculateImageTokens()`
 - **Audio files**: Approximates tokens from the file path string
 - **Text-based files**: Uses `approximateTokenSize()` on the extracted content
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts147-152](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L147-L152) [src/main/presenter/filePresenter/FilePresenter.ts314-322](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L314-L322)

 **Stage 6: Result Assembly**

 A `MessageFile` object is constructed with all gathered information and returned.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts145-165](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L145-L165)

 
---

 
## Content Type Modes

 The `contentType` parameter controls how file content is processed and extracted.

 
### LLM-Friendly Mode

 
```

```

 This mode is the default when calling `prepareFile()` (which is a convenience wrapper that calls `prepareFileCompletely` with `contentType: 'llm-friendly'`). It applies transformations optimized for LLM consumption:

 
 - **Images**: Resized to maximum 1200×1200 pixels, compressed to JPEG at 70% quality, and encoded as base64 data URLs
 - **Documents**: Text is extracted and formatted for readability
 - **Code files**: Syntax is preserved with appropriate formatting
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts176-178](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L176-L178) [src/main/presenter/filePresenter/BaseFileAdapter.ts72](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/BaseFileAdapter.ts#L72-L72)

 
### Origin Mode

 This mode calls `adapter.getContent()` to retrieve minimally processed or raw content. The exact behavior depends on the adapter implementation, but generally preserves the original file format more closely.

 **Sources:** [src/main/presenter/filePresenter/BaseFileAdapter.ts71](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/BaseFileAdapter.ts#L71-L71)

 
### Null Mode

 When `contentType` is `null` or not specified, no content extraction occurs. This is useful when only metadata is needed, such as during file listing or validation operations.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts140-142](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L140-L142)

 
---

 
## Image Processing & Compression

 Images receive special processing to optimize them for vision-capable LLMs while minimizing token usage and API costs.

 
### Image Processing Pipeline

 
```

```

 **Sources:** [src/main/presenter/filePresenter/ImageFileAdapter.ts66-96](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/ImageFileAdapter.ts#L66-L96)

 
### Compression Parameters

 The `ImageFileAdapter` uses the Sharp library for image processing with the following configuration:

 
| Parameter | Value | Purpose |
|---|---|---|
| Max dimensions | 1200×1200 | Reduces pixel count while maintaining detail for vision models |
| Resize fit | 'inside' | Maintains aspect ratio, fits within bounds |
| Enlarge prevention | true | Small images are not upscaled |
| Output format | JPEG | Universal compatibility, good compression |
| Quality | 70% | Balances quality and file size |
| Optimizer | mozjpeg | Enhanced compression algorithm |

 **Sources:** [src/main/presenter/filePresenter/ImageFileAdapter.ts76-86](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/ImageFileAdapter.ts#L76-L86)

 
### Thumbnail Generation

 Thumbnails are generated separately with more aggressive compression for UI preview purposes:

 
 - Resized to maximum 256×256 pixels
 - JPEG quality: 70%
 - Also returned as base64 data URL
 
 **Sources:** [src/main/presenter/filePresenter/ImageFileAdapter.ts46-64](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/ImageFileAdapter.ts#L46-L64)

 
### Metadata Extraction

 Before compression, the adapter extracts original image dimensions and format using Sharp's metadata API. After compression, it updates with the new compressed dimensions to enable accurate token calculation.

 **Sources:** [src/main/presenter/filePresenter/ImageFileAdapter.ts31-44](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/ImageFileAdapter.ts#L31-L44) [src/main/presenter/filePresenter/ImageFileAdapter.ts87-90](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/ImageFileAdapter.ts#L87-L90)

 
---

 
## Token Calculation

 Token counts are estimated differently based on file type to provide accurate usage predictions for LLM API calls.

 
### Token Calculation Logic

 
```

```

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts147-152](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L147-L152)

 
### Image Token Calculation

 Images use a pixel-based formula that accounts for compression:

 
```
tokens = (compressWidth × compressHeight) / 750
```

 The formula uses the **compressed** dimensions (after resizing to max 1200×1200) rather than the original dimensions, providing an accurate estimate of the actual token cost when the image is sent to the LLM.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts314-322](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L314-L322)

 
### Audio Token Calculation

 Audio files use the file path string as a proxy for token estimation, since the actual audio content is not converted to text at this stage:

 
```

```

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts150-151](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L150-L151)

 
### Text-Based Token Calculation

 All other file types (text, code, documents, etc.) use the `approximateTokenSize()` function from the `tokenx` library, which estimates tokens based on the extracted content string.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts152](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L152-L152)

 
---

 
## MessageFile Structure

 The `MessageFile` interface represents the final output of the preparation pipeline, containing all necessary information for displaying and processing the file in chat contexts.

 
### MessageFile Schema

 
```

```

 
### Field Descriptions

 
| Field | Type | Source | Description |
|---|---|---|---|
| name | string | adapter.fileMetaData.fileName | Display name of the file |
| token | number | Calculated | Estimated token count for LLM processing |
| path | string | adapter.filePath | Absolute file system path |
| mimeType | string | adapter.mimeType | Detected or provided MIME type |
| metadata | FileMetaData | adapter.fileMetaData | File metadata including size and timestamps |
| thumbnail | string | adapter.getThumbnail() | Base64 data URL for preview (if available) |
| content | string | Varies by contentType | Extracted file content (may be null) |

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts145-164](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L145-L164)

 
### Content Field Variations

 The `content` field contains different data depending on the extraction mode and file type:

 
 - **Text files**: Plain text or formatted text content
 - **Images (LLM mode)**: Base64 data URL string (e.g., `"data:image/jpeg;base64,..."`)
 - **Images (origin mode)**: Empty string (vision description, currently unused)
 - **Documents**: Extracted text content
 - **Audio files**: Empty or descriptive string
 - **Null mode**: Empty string
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts133-143](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L133-L143) [src/main/presenter/filePresenter/ImageFileAdapter.ts98-104](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/ImageFileAdapter.ts#L98-L104)

 
---

 
## Helper Methods

 The `FilePresenter` class provides convenience methods that wrap `prepareFileCompletely` with common parameter combinations.

 
### prepareFile Method

 
```

```

 This convenience method calls `prepareFileCompletely` with `contentType: 'llm-friendly'`, making it the default method for preparing files for LLM consumption.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts176-178](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L176-L178)

 
### prepareDirectory Method

 For directory handling, a separate method bypasses the adapter system and uses the `DirectoryAdapter` directly:

 
```

```

 This returns a `MessageFile` with `mimeType: 'directory'` and metadata about the directory structure.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts93-112](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L93-L112)

 
---

 
## Error Handling

 The preparation pipeline includes error handling at multiple stages:

 
### Adapter Creation Errors

 If no suitable adapter is found for the detected MIME type, `createFileAdapter` throws an error:

 
```
No adapter found for file "{filePath}" with determined mime type "{mimeType}"
```

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts85-87](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L85-L87)

 
### Processing Errors

 If any stage of the pipeline fails, `prepareFileCompletely` catches the error and throws a generic error message:

 
```
Can not read file: {fullPath}
```

 The original error is logged to the console for debugging purposes.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts169-173](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L169-L173)

 
### Image Size Validation

 For images, if the file size exceeds `maxFileSize` (default 30MB), `getLLMContent()` returns `undefined` rather than processing the image. This prevents memory issues with very large images.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts28-30](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L28-L30) [src/main/presenter/filePresenter/ImageFileAdapter.ts67-70](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/ImageFileAdapter.ts#L67-L70)

 
---

 
## Integration with Chat System

 The prepared `MessageFile` objects are embedded in user messages and sent to LLM providers. The structure allows both metadata display in the UI and content transmission to the LLM API.

 **Workflow Integration:**

 
 - User selects files in the chat interface
 - `FilePresenter.prepareFile()` is called for each file
 - Resulting `MessageFile` objects are attached to the `UserMessage`
 - During LLM API call formatting, the `content` field provides the file data
 - The `token` field contributes to usage tracking and quota management
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts121-174](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L121-L174)
