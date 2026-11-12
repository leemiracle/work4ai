> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/7.2-file-adapters-and-content-extraction](https://deepwiki.com/thinkinaixyz/deepchat/7.2-file-adapters-and-content-extraction)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/7.2-file-adapters-and-content-extraction

# File Adapters and Content Extraction

  Relevant source files 
 - [src/main/presenter/filePresenter/AudioFileAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/AudioFileAdapter.ts)
 - [src/main/presenter/filePresenter/BaseFileAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts)
 - [src/main/presenter/filePresenter/DirectoryAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/DirectoryAdapter.ts)
 - [src/main/presenter/filePresenter/FileAdapterConstructor.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FileAdapterConstructor.ts)
 - [src/main/presenter/filePresenter/FilePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts)
 - [src/main/presenter/filePresenter/ImageFileAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts)
 - [src/main/presenter/filePresenter/mime.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts)
 - [src/renderer/src/components/editor/mention/MentionList.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue)
 - [src/renderer/src/components/editor/mention/PromptParamsDialog.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/PromptParamsDialog.vue)
 - [src/renderer/src/components/editor/mention/mention.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/mention.ts)
 - [src/renderer/src/components/editor/mention/suggestion.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts)
 
  This document describes the file processing pipeline in DeepChat, focusing on the adapter pattern used to extract content from various file types and transform them into LLM-compatible formats. The system provides a polymorphic architecture where different file types are handled by specialized adapters that implement common interfaces for content extraction, metadata generation, and thumbnail creation.

 For information about how files are attached to messages through the editor, see [Mention System and Prompt Parameters](https://deepwiki.com/thinkinaixyz/deepchat/7.3-mention-system-and-prompt-parameters). For the high-level file processing architecture and FilePresenter's role, see [File Processing Architecture](https://deepwiki.com/thinkinaixyz/deepchat/7.1-file-processing-architecture). This page specifically focuses on the adapter implementations and content extraction logic.

 
## Adapter Pattern Architecture

 The file adapter system uses a polymorphic design where each file type is handled by a specialized adapter class. All adapters inherit from `BaseFileAdapter` and implement a consistent interface for processing files.

 
```

```

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts1-323](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L1-L323) [src/main/presenter/filePresenter/BaseFileAdapter.ts1-75](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts#L1-L75) [src/main/presenter/filePresenter/FileAdapterConstructor.ts1-26](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FileAdapterConstructor.ts#L1-L26)

 
### Adapter Selection Flow

 The `FilePresenter` orchestrates adapter selection through a two-stage MIME type detection process followed by lookup in the adapter registry:

 
```

```

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts68-91](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L68-L91) [src/main/presenter/filePresenter/FilePresenter.ts180-199](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L180-L199) [src/main/presenter/filePresenter/mime.ts110-141](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L110-L141)

 
## MIME Type Detection System

 The MIME type detection system uses a dual-strategy approach combining library-based detection with heuristic content analysis.

 
### Detection Strategies

 
| Strategy | Implementation | Use Case | Priority |
|---|---|---|---|
| Library-based | es-mime-types.lookup() | Standard file extensions | 1st |
| Heuristic | isLikelyTextFile() | Unknown extensions, no extension | 2nd |
| Fallback | application/octet-stream | Detection failure | 3rd |

 The `detectMimeType()` function implements this cascade at [src/main/presenter/filePresenter/mime.ts110-141](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L110-L141):

 
 - **Library lookup**: Uses `es-mime-types` to match file extension to MIME type
 - **Text heuristic**: If library returns nothing, reads first 1024 bytes and checks for: 
 - Null bytes (indicates binary)
 - Non-printable characters (>10% ratio indicates binary)
 - Valid UTF-8 sequences
 
 **Sources:** [src/main/presenter/filePresenter/mime.ts110-141](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L110-L141) [src/main/presenter/filePresenter/mime.ts144-207](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L144-L207)

 
### MIME Type to Adapter Mapping

 The `getMimeTypeAdapterMap()` function at [src/main/presenter/filePresenter/mime.ts16-108](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L16-L108) defines the registry:

 
| MIME Type Pattern | Adapter | Special Cases |
|---|---|---|
| text/plain, text/markdown, text/* | TextFileAdapter | Wildcard match for text |
| text/csv | CsvFileAdapter | Exact match overrides wildcard |
| image/* | ImageFileAdapter | Supports JPEG, PNG, GIF, WebP, BMP |
| audio/mp3, audio/mpeg, audio/wav | AudioFileAdapter | M4A, WAV variants |
| application/javascript, text/x-python, etc. | CodeFileAdapter | 20+ language types |
| video/mp2t | CodeFileAdapter | macOS misdetects .ts as video |
| application/pdf | PdfFileAdapter | - |
| application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | ExcelFileAdapter | XLS, XLSX, ODS, Numbers |
| application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document | DocFileAdapter | DOC, DOCX |
| application/vnd.ms-powerpoint, application/vnd.openxmlformats-officedocument.presentationml.presentation | PptFileAdapter | PPT, PPTX |
| */* | UnsupportFileAdapter | Final fallback |

 **Special Case Handling:** The map handles the macOS bug where TypeScript files (`.ts`) are detected as `video/mp2t` by mapping this MIME type to `CodeFileAdapter` at [src/main/presenter/filePresenter/mime.ts44](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L44-L44)

 **Sources:** [src/main/presenter/filePresenter/mime.ts16-108](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L16-L108)

 
## BaseFileAdapter Abstract Class

 The `BaseFileAdapter` class defines the contract that all file adapters must implement. It provides common functionality for metadata extraction and file processing.

 
### Core Interface

 
```

```

 **Sources:** [src/main/presenter/filePresenter/BaseFileAdapter.ts1-75](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts#L1-L75)

 
### Common Functionality

 The base class provides shared implementations at [src/main/presenter/filePresenter/BaseFileAdapter.ts16-68](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts#L16-L68):

 
| Method | Functionality | Implementation |
|---|---|---|
| readFile() | Read entire file as Buffer | fs.promises.readFile() |
| calculateFileHash() | SHA-256 hash (currently unused) | crypto.createHash('sha256') |
| extractBasicInfo() | File stats (size, dates) | fs.promises.stat() |
| preprocessFile() | MIME type detection | Calls detectMimeType() |
| processFile() | Orchestrate metadata extraction | Calls helper methods, populates fileMetaData |

 
### Abstract Methods

 Each adapter must implement these four methods:

 
 - **`getFileDescription()`**: Returns human-readable file type description
 - **`getContent()`**: Extracts original content (may be raw or processed)
 - **`getLLMContent()`**: Generates LLM-optimized content (may differ from `getContent()`)
 - **`getThumbnail()`**: Creates base64-encoded preview image (or empty string)
 
 **Sources:** [src/main/presenter/filePresenter/BaseFileAdapter.ts70-74](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts#L70-L74)

 
## Specialized Adapter Implementations

 
### ImageFileAdapter

 The `ImageFileAdapter` handles image files using the Sharp library for compression and format conversion.

 **Key Features:**

 
 - Compresses images to reduce token usage
 - Converts all formats to JPEG for consistency
 - Generates thumbnails (256×256) and LLM-friendly versions (1200×1200)
 - Calculates token count based on pixel dimensions
 
 
```

```

 **Implementation Details:**

 
 - Uses Sharp's `resize()` with `fit: 'inside'` to maintain aspect ratio at [src/main/presenter/filePresenter/ImageFileAdapter.ts48-53](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts#L48-L53)
 - Enables `mozjpeg` optimization for better compression at [src/main/presenter/filePresenter/ImageFileAdapter.ts57](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts#L57-L57)
 - Stores compressed dimensions for accurate token calculation at [src/main/presenter/filePresenter/ImageFileAdapter.ts87-90](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts#L87-L90)
 - Token calculation formula: `(compressWidth × compressHeight) / 750` at [FilePresenter.ts314-322](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/FilePresenter.ts#L314-L322)
 
 **File Size Handling:** Images exceeding `maxFileSize` (default 30MB) return `undefined` for LLM content at [src/main/presenter/filePresenter/ImageFileAdapter.ts67-70](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts#L67-L70)

 **Sources:** [src/main/presenter/filePresenter/ImageFileAdapter.ts1-106](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts#L1-L106) [src/main/presenter/filePresenter/FilePresenter.ts314-322](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L314-L322)

 
### AudioFileAdapter

 The `AudioFileAdapter` handles audio files by returning only the file path, as audio content cannot be directly embedded in text-based LLM messages.

 **Characteristics:**

 
 - Does NOT read file content
 - Returns path string: `"Audio file path: {filePath}"`
 - Same output for both `getContent()` and `getLLMContent()`
 - Empty thumbnail
 
 **Token Calculation:** Audio files use path length for token approximation at [FilePresenter.ts150-152](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/FilePresenter.ts#L150-L152):

 
```
approximateTokenSize(`Audio file path: ${adapter.filePath}`)
```

 **Rationale:** Audio transcription requires separate processing (e.g., via speech-to-text APIs) and is not handled by the adapter layer.

 **Sources:** [src/main/presenter/filePresenter/AudioFileAdapter.ts1-26](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/AudioFileAdapter.ts#L1-L26) [src/main/presenter/filePresenter/FilePresenter.ts148-152](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L148-L152)

 
### Text and Code Adapters

 These adapters handle text-based files with UTF-8 encoding:

 
| Adapter | File Types | Special Processing |
|---|---|---|
| TextFileAdapter | .txt, .md, .json, .xml, .yaml | Plain UTF-8 read |
| CodeFileAdapter | .js, .ts, .py, .java, .cpp, .html, .css | Syntax-aware (potentially) |
| CsvFileAdapter | .csv | CSV parsing with structure preservation |

 **Token Calculation:** Text files use content length for token approximation at [FilePresenter.ts148-152](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/FilePresenter.ts#L148-L152):

 
```
approximateTokenSize(content || '')
```

 **Sources:** [src/main/presenter/filePresenter/mime.ts19-66](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L19-L66)

 
### Document Adapters

 Specialized adapters extract text from binary document formats:

 
| Adapter | Library | Formats | Implementation |
|---|---|---|---|
| PdfFileAdapter | pdf-parse | PDF | Text extraction from PDF structures |
| DocFileAdapter | mammoth | DOC, DOCX | Word document conversion to plain text |
| PptFileAdapter | officegen | PPT, PPTX | PowerPoint text extraction |
| ExcelFileAdapter | xlsx | XLS, XLSX, ODS, Numbers | Spreadsheet cell reading |

 **Sources:** [src/main/presenter/filePresenter/mime.ts68-96](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L68-L96)

 
### UnsupportFileAdapter

 The fallback adapter for unsupported file types:

 
 - Implements all required methods
 - Returns minimal or empty content
 - Prevents errors when encountering unknown file types
 
 **Sources:** [src/main/presenter/filePresenter/mime.ts104-105](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L104-L105)

 
### DirectoryAdapter

 The `DirectoryAdapter` handles directory paths (not files) and extracts directory metadata.

 **Functionality:**

 
 - Verifies path is a directory using `stat.isDirectory()` at [src/main/presenter/filePresenter/DirectoryAdapter.ts18-20](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/DirectoryAdapter.ts#L18-L20)
 - Extracts creation and modification dates
 - Returns `DirectoryMetaData` with `dirName`, `dirPath`, and timestamps
 
 **Sources:** [src/main/presenter/filePresenter/DirectoryAdapter.ts1-48](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/DirectoryAdapter.ts#L1-L48)

 
## Content Generation Strategies

 File adapters support three content generation modes controlled by the `contentType` parameter in `prepareFileCompletely()`:

 
### Content Type Modes

 
```

```

 **Implementation:** The switch statement at [src/main/presenter/filePresenter/FilePresenter.ts132-143](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L132-L143) determines which method to call.

 
### LLM-Friendly Content Generation

 The `getLLMContent()` method optimizes content for LLM consumption:

 **Image Files:**

 
 - Resize to max 1200×1200 pixels
 - Convert to JPEG with 70% quality
 - Return base64 data URL
 - Check file size limit before processing
 
 **Text Files:**

 
 - UTF-8 encoding
 - Full content (no truncation in adapter)
 - Token counting for display
 
 **Audio Files:**

 
 - Path-only reference
 - No content embedding
 
 **Document Files:**

 
 - Extracted text without formatting
 - Structured data preservation (tables in Excel/CSV)
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts121-174](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L121-L174)

 
### Original Content vs LLM Content

 The distinction between `getContent()` and `getLLMContent()` allows adapters to provide:

 
 - **Original**: For user display, editing, or external tools
 - **LLM**: For model consumption with optimizations
 
 **Current Usage:** The codebase primarily uses `prepareFile()` which defaults to LLM-friendly content at [src/main/presenter/filePresenter/FilePresenter.ts176-178](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L176-L178)

 **Sources:** [src/main/presenter/filePresenter/BaseFileAdapter.ts71-72](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts#L71-L72)

 
## MessageFile Output Format

 The file processing pipeline produces a standardized `MessageFile` object that encapsulates all file information needed for chat messages.

 
### MessageFile Structure

 
```

```

 **Assembly Process:** The `prepareFileCompletely()` method at [src/main/presenter/filePresenter/FilePresenter.ts145-165](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L145-L165) assembles the MessageFile:

 
 - Create adapter instance based on MIME type
 - Call `adapter.processFile()` to extract metadata
 - Generate content based on `contentType` parameter
 - Generate thumbnail if adapter supports it
 - Calculate tokens based on file type
 - Return complete MessageFile object
 
 **Token Calculation Logic:** Different strategies for different file types at [src/main/presenter/filePresenter/FilePresenter.ts147-153](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L147-L153):

 
 - **Images**: `calculateImageTokens()` using pixel dimensions
 - **Audio**: Token count of path string
 - **Others**: Token count of content string
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts121-174](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L121-L174) [src/main/presenter/filePresenter/FilePresenter.ts314-322](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L314-L322)

 
## File Validation for Knowledge Base

 The `FilePresenter` includes validation functionality for knowledge base processing through the `FileValidationService`.

 
### Validation Methods

 
| Method | Purpose | Return Type |
|---|---|---|
| validateFileForKnowledgeBase() | Check if file is supported | FileValidationResult |
| getSupportedExtensions() | List all supported extensions | string[] |

 **Implementation:** The validation service is injected into FilePresenter at [src/main/presenter/filePresenter/FilePresenter.ts32-36](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L32-L36) and provides methods at [src/main/presenter/filePresenter/FilePresenter.ts264-311](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L264-L311)

 **Supported Extensions Fallback:** If validation service fails, a hardcoded list of common extensions is returned at [src/main/presenter/filePresenter/FilePresenter.ts287-310](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L287-L310) including: txt, md, pdf, docx, pptx, xlsx, csv, json, yaml, xml, and common code file extensions.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts16-20](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L16-L20) [src/main/presenter/filePresenter/FilePresenter.ts264-311](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L264-L311)

 
## Temporary File Management

 The `FilePresenter` manages temporary files for operations like clipboard paste and base64 image conversion.

 
### Temporary File Operations

 
```

```

 **Temp Directory:** Created at `userData/temp/` during FilePresenter initialization at [src/main/presenter/filePresenter/FilePresenter.ts34-45](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L34-L45)

 **`writeTemp()` Implementation:** Handles three content types at [src/main/presenter/filePresenter/FilePresenter.ts201-217](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L201-L217):

 
 - String: Write as UTF-8 text
 - Buffer: Write directly
 - ArrayBuffer: Convert to Buffer then write
 
 **`writeImageBase64()` Implementation:** Extracts base64 data from data URL, converts to binary, and writes file at [src/main/presenter/filePresenter/FilePresenter.ts219-246](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L219-L246)

 **File Naming:** Uses `nanoid()` for unique filenames with original extension preserved at [src/main/presenter/filePresenter/FilePresenter.ts203](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L203-L203)

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts201-246](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L201-L246)

 
## Integration with Mention System

 Files can be attached to messages through the `@` mention system when prompts include file references.

 
### Prompt File Handling Flow

 
```

```

 **File Detection:** The `hasFiles()` function in MentionList checks if a prompt has associated files at [src/renderer/src/components/editor/mention/MentionList.vue88-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L88-L98):

 
```

```

 **File Handler Registration:** The suggestion system stores a callback for file handling at [src/renderer/src/components/editor/mention/suggestion.ts41-59](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L41-L59) using `setPromptFilesHandler()`.

 **File Processing Trigger:** When a prompt with files is selected, the handler processes the file array at [src/renderer/src/components/editor/mention/MentionList.vue229-236](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L229-L236)

 **Sources:** [src/renderer/src/components/editor/mention/MentionList.vue88-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L88-L98) [src/renderer/src/components/editor/mention/MentionList.vue229-236](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L229-L236) [src/renderer/src/components/editor/mention/suggestion.ts41-62](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L41-L62)

 
## Error Handling and Edge Cases

 The adapter system includes defensive error handling for common failure scenarios:

 
### MIME Detection Failures

 **Cascade Strategy:** If library detection fails, try heuristic; if heuristic fails, return `application/octet-stream` at [src/main/presenter/filePresenter/mime.ts124-139](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L124-L139)

 **Text Check Errors:** The `isLikelyTextFile()` function catches errors and returns `false` at [src/main/presenter/filePresenter/mime.ts200-206](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L200-L206)

 
### Adapter Selection Failures

 **Fallback Chain:**

 
 - Try exact MIME match
 - Try wildcard match (e.g., `text/*`)
 - Fall back to `UnsupportFileAdapter`
 
 This is implemented at [src/main/presenter/filePresenter/FilePresenter.ts180-199](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L180-L199)

 
### File Size Limits

 **Enforcement:** The `maxFileSize` setting (default 30MB) is passed to adapters and checked before processing at [src/main/presenter/filePresenter/FilePresenter.ts28-30](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L28-L30)

 **Example:** ImageFileAdapter checks size before compression at [src/main/presenter/filePresenter/ImageFileAdapter.ts67-70](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts#L67-L70)

 
### Directory vs File Detection

 **Directory Check:** The `isDirectory()` method safely handles non-existent paths at [src/main/presenter/filePresenter/FilePresenter.ts248-257](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L248-L257) by catching errors and returning `false`.

 **Sources:** [src/main/presenter/filePresenter/mime.ts124-141](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L124-L141) [src/main/presenter/filePresenter/FilePresenter.ts180-199](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L180-L199) [src/main/presenter/filePresenter/FilePresenter.ts248-257](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L248-L257)
