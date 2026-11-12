> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/9.4-proxy-configuration-system](https://deepwiki.com/thinkinaixyz/deepchat/9.4-proxy-configuration-system)（Wayback 快照 2026-04-11）
> DeepWiki deepchat/9.4-proxy-configuration-system

# File Validation & Support

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

 This document describes the file validation system used to determine which files are eligible for knowledge base processing. The validation layer filters out unsupported file types (audio, images, binary files) and provides a comprehensive list of supported formats for RAG (Retrieval-Augmented Generation) operations.

 For information about the adapter architecture that processes validated files, see [File Adapter Architecture](https://deepwiki.com/thinkinaixyz/deepchat/9.1-file-adapter-architecture). For details on MIME type detection that feeds into validation, see [MIME Detection & Type Resolution](https://deepwiki.com/thinkinaixyz/deepchat/9.2-mime-detection-and-type-resolution). For the knowledge base system that consumes validated files, see [Knowledge Base Architecture](https://deepwiki.com/thinkinaixyz/deepchat/10.1-knowledge-base-architecture).

 
## System Overview

 The file validation system serves as a gatekeeper between user file selection and knowledge base ingestion. Its primary responsibilities are:

 
 - Determine if a file type is supported for text extraction and embedding
 - Exclude file types that cannot be meaningfully converted to text (audio, images)
 - Provide user-facing lists of supported file extensions
 - Return validation results with error messages and suggestions
 
 The system is built around the `FileValidationService` class, which is instantiated by `FilePresenter` and used during knowledge base file addition workflows.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts16-36](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L16-L36) [src/main/presenter/filePresenter/FileValidationService.ts20-30](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L20-L30)

 
## Core Architecture

 
```

```

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts22-46](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L22-L46) [src/main/presenter/filePresenter/FileValidationService.ts20-30](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L20-L30) [src/main/presenter/filePresenter/FileValidationService.ts6-18](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L6-L18)

 
## FileValidationService Implementation

 
### Class Structure

 The `FileValidationService` implements the `IFileValidationService` interface and maintains an internal exclusion list:

 
| Property | Type | Purpose |
|---|---|---|
| excludedAdapters | string[] | Names of adapter classes not supported for knowledge base processing |

 **Excluded Adapters:**

 
 - `AudioFileAdapter` - Audio files cannot be converted to searchable text
 - `ImageFileAdapter` - Images require vision models, not text embedding
 - `UnsupportFileAdapter` - Unrecognized file formats
 - `DirectoryAdapter` - Directories are structural, not content
 
 
### Core Methods

 
| Method | Return Type | Description |
|---|---|---|
| validateFile(filePath) | Promise<FileValidationResult> | Main validation method that checks file eligibility |
| getSupportedExtensions() | string[] | Returns sorted list of supported file extensions |
| getSupportedMimeTypes() | string[] | Returns sorted list of supported MIME types |
| isAdapterSupported(constructor) | boolean | Checks if adapter is in exclusion list |
| findAdapterForMimeType(mimeType, map) | FileAdapterConstructor \| undefined | Locates appropriate adapter using exact or wildcard matching |

 **Sources:** [src/main/presenter/filePresenter/FileValidationService.ts20-127](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L20-L127)

 
## Validation Workflow

 
```

```

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts264-275](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L264-L275) [src/main/presenter/filePresenter/FileValidationService.ts37-89](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L37-L89)

 
## Validation Result Structure

 The `FileValidationResult` interface provides detailed feedback about validation:

 
```

```

 
### Result Scenarios

 
| Scenario | isSupported | error | suggestedExtensions |
|---|---|---|---|
| Supported file (e.g., PDF) | true | - | - |
| MIME detection failed | false | "Could not determine file type" | ✓ |
| Unsupported type (e.g., audio) | false | "File type not supported for knowledge base processing" | ✓ |
| Validation exception | false | "Error validating file: {message}" | ✓ |

 **Sources:** [src/main/presenter/filePresenter/FileValidationService.ts6-12](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L6-L12) [src/main/presenter/filePresenter/FileValidationService.ts37-89](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L37-L89)

 
## Adapter Exclusion Logic

 
### Exclusion Decision Flow

 
```

```

 **Sources:** [src/main/presenter/filePresenter/FileValidationService.ts96-127](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L96-L127) [src/main/presenter/filePresenter/FileValidationService.ts21-26](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L21-L26)

 
## Supported File Formats

 
### Extension Discovery Algorithm

 The `getSupportedExtensions()` method constructs the supported extension list through a multi-step process:

 
 - **Iterate through adapter map** - Extract all MIME types with non-excluded adapters
 - **Resolve extensions** - Use `mimeTypesExtension()` from `es-mime-types` library
 - **Add common formats** - Inject frequently-used extensions: `['md', 'markdown', 'txt', 'json', 'yaml', 'yml', 'xml']`
 - **Sort and deduplicate** - Return alphabetically sorted unique extensions
 
 
### Supported Format Categories

 
| Category | Extensions | Adapter Class |
|---|---|---|
| Plain Text | txt, md, markdown | TextFileAdapter |
| Structured Data | json, yaml, yml, xml, csv | TextFileAdapter, CsvFileAdapter |
| Documents | pdf, docx, doc, pptx, ppt | PdfFileAdapter, DocFileAdapter, PptFileAdapter |
| Spreadsheets | xlsx, xls, ods, numbers | ExcelFileAdapter |
| Code Files | js, ts, py, java, cpp, c, h, css, html, sh, php, rb, go, rs, swift, kt | CodeFileAdapter |

 
### Excluded Format Categories

 
| Category | Extensions | Reason |
|---|---|---|
| Audio | mp3, wav, m4a | Cannot be converted to searchable text; requires transcription |
| Images | jpg, jpeg, png, gif, webp, bmp | Require vision models; not text-embeddable |
| Binary | exe, bin, so, dll | No meaningful text content |

 **Sources:** [src/main/presenter/filePresenter/FileValidationService.ts133-184](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L133-L184) [src/main/presenter/filePresenter/mime.ts16-108](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/mime.ts#L16-L108)

 
## Integration with FilePresenter

 
### Public API Methods

 The `FilePresenter` class exposes two validation-related methods to the IPC layer:

 
```

```

 **Method Implementations:**

 **`validateFileForKnowledgeBase(filePath: string)`**

 
 - Wraps `FileValidationService.validateFile()` with error handling
 - Returns validation result with suggested extensions on failure
 - Provides fallback error message if service throws exception
 
 **`getSupportedExtensions()`**

 
 - Retrieves comprehensive list of supported file extensions
 - Includes fallback hardcoded list if service fails: `['txt', 'md', 'pdf', 'docx', 'pptx', 'xlsx', 'csv', 'json', ...]`
 - Used to populate file picker filters and UI hints
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts259-311](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L259-L311)

 
## Error Handling and Fallbacks

 
### Validation Error Scenarios

 
```

```

 
### Fallback Extension List

 If the `FileValidationService` fails to generate the supported extensions list (e.g., due to adapter map initialization error), both `FilePresenter.getSupportedExtensions()` and `FileValidationService.getSupportedExtensions()` return identical hardcoded fallback arrays:

 
```

```

 This ensures the UI can always present users with guidance about supported formats, even in degraded scenarios.

 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts264-311](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L264-L311) [src/main/presenter/filePresenter/FileValidationService.ts133-184](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L133-L184)

 
## MIME Type Support Query

 The `FileValidationService` also provides `getSupportedMimeTypes()` for programmatic access to supported MIME types:

 
### Implementation Details

 
 - **Iterate adapter map** - Loop through all entries in `getMimeTypeAdapterMap()`
 - **Filter supported adapters** - Exclude adapters in `excludedAdapters` list
 - **Skip wildcards** - Remove entries containing `*` (e.g., `text/*`, `image/*`)
 - **Return sorted list** - Alphabetically ordered MIME type strings
 
 
### Common Supported MIME Types

 
| MIME Type | File Type |
|---|---|
| text/plain | Plain text files |
| text/markdown | Markdown documents |
| application/pdf | PDF documents |
| application/json | JSON files |
| application/javascript | JavaScript code |
| text/csv | CSV spreadsheets |
| application/vnd.openxmlformats-officedocument.wordprocessingml.document | DOCX documents |
| application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | XLSX spreadsheets |
| application/vnd.openxmlformats-officedocument.presentationml.presentation | PPTX presentations |

 
### Fallback MIME Types

 Similar to extensions, if the adapter map query fails, the method returns a hardcoded list of common MIME types including `text/plain`, `application/pdf`, `application/msword`, and office document formats.

 **Sources:** [src/main/presenter/filePresenter/FileValidationService.ts190-226](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L190-L226)

 
## Usage Example Flow

 
### Knowledge Base File Addition

 When a user attempts to add a file to a knowledge base:

 
 - **UI triggers validation** - Knowledge base dialog calls `validateFileForKnowledgeBase(selectedFilePath)`
 - **MIME detection** - System detects file's MIME type using content inspection
 - **Adapter lookup** - System finds matching adapter in map (exact match → wildcard match → unsupported)
 - **Exclusion check** - System checks if adapter is in `excludedAdapters` list
 - **Result return** - System returns `FileValidationResult` to UI
 - **UI response:** 
 - If `isSupported: true` → Proceed with file processing pipeline (see [File Processing Pipeline](https://deepwiki.com/thinkinaixyz/deepchat/10.2-file-processing-pipeline))
 - If `isSupported: false` → Show error message with `suggestedExtensions`
 
 
### File Picker Filter

 When displaying file selection dialogs for knowledge base operations:

 
 - **UI requests extensions** - Dialog initialization calls `getSupportedExtensions()`
 - **Service queries adapters** - System iterates through adapter map and extracts extensions
 - **UI applies filter** - Dialog restricts file picker to returned extensions
 - **User guidance** - UI displays list of supported formats in help text
 
 **Sources:** [src/main/presenter/filePresenter/FilePresenter.ts264-275](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FilePresenter.ts#L264-L275) [src/main/presenter/filePresenter/FileValidationService.ts37-89](https://github.com/thinkinaixyz/deepchat/blob/f4165c74/src/main/presenter/filePresenter/FileValidationService.ts#L37-L89)
