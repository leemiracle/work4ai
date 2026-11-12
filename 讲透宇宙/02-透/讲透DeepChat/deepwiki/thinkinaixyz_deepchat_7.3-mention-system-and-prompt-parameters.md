> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/7.3-mention-system-and-prompt-parameters](https://deepwiki.com/thinkinaixyz/deepchat/7.3-mention-system-and-prompt-parameters)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/7.3-mention-system-and-prompt-parameters

# Mention System and Prompt Parameters

  Relevant source files 
 - [electron.vite.config.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/electron.vite.config.ts)
 - [package.json](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/package.json)
 - [src/main/presenter/filePresenter/AudioFileAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/AudioFileAdapter.ts)
 - [src/main/presenter/filePresenter/BaseFileAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts)
 - [src/main/presenter/filePresenter/DirectoryAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/DirectoryAdapter.ts)
 - [src/main/presenter/filePresenter/FileAdapterConstructor.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FileAdapterConstructor.ts)
 - [src/main/presenter/filePresenter/FilePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts)
 - [src/main/presenter/filePresenter/ImageFileAdapter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts)
 - [src/main/presenter/filePresenter/mime.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts)
 - [src/main/presenter/mcpPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/index.ts)
 - [src/main/presenter/mcpPresenter/mcpClient.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/mcpClient.ts)
 - [src/main/presenter/mcpPresenter/serverManager.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/serverManager.ts)
 - [src/main/presenter/mcpPresenter/toolManager.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/mcpPresenter/toolManager.ts)
 - [src/renderer/src/components/editor/mention/MentionList.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue)
 - [src/renderer/src/components/editor/mention/PromptParamsDialog.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/PromptParamsDialog.vue)
 - [src/renderer/src/components/editor/mention/mention.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/mention.ts)
 - [src/renderer/src/components/editor/mention/suggestion.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts)
 - [src/renderer/src/components/markdown/MarkdownRenderer.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/markdown/MarkdownRenderer.vue)
 - [src/renderer/src/composables/useArtifactCodeEditor.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/useArtifactCodeEditor.ts)
 - [src/renderer/src/main.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/main.ts)
 - [src/renderer/src/stores/mcp.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts)
 
  The mention system provides an @ autocomplete interface in the chat input editor, allowing users to reference skills, prompts, MCP tools, resources, and workspace files. This page documents the TipTap-based mention extension, the suggestion system that aggregates data from multiple sources, prompt parameter collection via dialogs, and file attachment integration.

 For file adapter details, see page 7.2. For MCP prompt and resource integration, see page 4.

 
## System Architecture

 The mention system consists of three primary layers: the TipTap extension, the suggestion engine, and the UI components. The extension provides the @ trigger mechanism, the suggestion engine aggregates data from multiple sources (MCP prompts, skills, workspace files), and the UI renders the dropdown list with category indicators.

 
### Mention System Component Architecture

 
```

```

 **Sources:** [src/renderer/src/components/editor/mention/mention.ts1-42](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/mention.ts#L1-L42) [src/renderer/src/components/editor/mention/suggestion.ts1-187](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L1-L187) [src/renderer/src/components/editor/mention/MentionList.vue1-286](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L1-L286) [src/main/presenter/filePresenter/FilePresenter.ts68-91](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L68-L91)

 
## TipTap Mention Extension

 The mention extension is defined in `mention.ts` by calling `TipTMention.extend()` to add custom attributes beyond the base mention functionality. The extension defines `category` and `content` attributes via the `addAttributes()` method, which are serialized to HTML as `data-category` and `data-content`.

 
### Mention Extension Attributes

 The `addAttributes()` method defines custom attributes:

 
| Attribute | Purpose | HTML Attribute | parseHTML | renderHTML |
|---|---|---|---|---|
| category | Type of mention (skills, prompts, tools, files, resources) | data-category | getAttribute('data-category') | { 'data-category': attributes.category } |
| content | Serialized data (JSON string for prompts with params/files) | data-content | getAttribute('data-content') | { 'data-content': attributes.content } |
| id | Unique identifier (inherited from base TipTMention) | data-id | Inherited | Inherited |
| label | Display text (inherited from base TipTMention) | data-label | Inherited | Inherited |

 The `category` attribute distinguishes mention types for rendering (e.g., `item.category === 'skills'` in MentionList.vue line 15). The `content` attribute stores the full `mcpEntry` data, including `arguments` arrays and `files` arrays for prompts.

 **Sources:** [src/renderer/src/components/editor/mention/mention.ts3-41](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/mention.ts#L3-L41) [src/renderer/src/components/editor/mention/MentionList.vue15-24](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L15-L24)

 
## Suggestion System

 The suggestion system aggregates data from multiple sources and filters results based on the user's query. The core configuration is defined in `suggestion.ts` which exports a TipTap suggestion configuration object.

 
### Data Structure

 The `CategorizedData` interface (lines 9-18) represents each suggestion item:

 
```

```

 The `mcpEntry` field stores the raw MCP data structure (PromptListEntry, ResourceListEntry, or MCPToolDefinition). For prompts, this includes the `arguments` array and `files` array. The `content` field is used for serialization when calling `props.command()` to insert the mention.

 **Sources:** [src/renderer/src/components/editor/mention/suggestion.ts9-18](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L9-L18)

 
### Suggestion Item Resolution

 
```

```

 The `items()` function (lines 67-104) is called with the query string (without the `@` character). It first checks `workspaceMentionHandler?.isEnabled.value` (line 75). If enabled, it calls `workspaceMentionHandler.searchWorkspaceFiles(query)` (line 76) and retrieves results from `workspaceFileResults.value` (line 77). Then it filters `mentionData.value` by checking if `item.label.toLowerCase().includes(query.toLowerCase())` (line 88). If query is present, results are limited to 5 items (line 92). Workspace results are prepended to other items in the returned array (line 102).

 **Sources:** [src/renderer/src/components/editor/mention/suggestion.ts67-104](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L67-L104)

 
## MentionList Component

 The `MentionList.vue` component renders the dropdown UI for mention suggestions. It displays items with category-specific icons, handles keyboard navigation, and manages the prompt parameter dialog.

 
### Category Display

 The component assigns icons via conditional rendering in the template (lines 14-27):

 
| Category Check | Icon | CSS Class |
|---|---|---|
| item.category === 'skills' (line 15) | ✨ | Default |
| item.category === 'prompts' (line 17) | 💬 | text-blue-500 |
| item.category === 'tools' (line 22) | 🔧 | text-green-600 |
| item.icon present (line 26) | Custom <Icon :icon="item.icon"> | Default |

 If a prompt has associated files, a paperclip icon is displayed (line 30): `<Icon v-if="hasFiles(item)" icon="lucide:paperclip">`. The `hasFiles()` function (lines 88-98) checks for the presence of the `files` array in the `mcpEntry` by verifying `mcpEntry && 'files' in mcpEntry && mcpEntry.files && Array.isArray(mcpEntry.files) && mcpEntry.files.length > 0`.

 **Sources:** [src/renderer/src/components/editor/mention/MentionList.vue14-30](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L14-L30) [src/renderer/src/components/editor/mention/MentionList.vue88-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L88-L98)

 
### Keyboard Navigation

 The component exposes an `onKeyDown()` method (lines 257-280) via `defineExpose()` (line 282-284) that handles keyboard events:

 
```

```

 The `selectedIndex` ref (line 84) is clamped to valid bounds via a watcher (lines 117-124) when `displayItems.value` changes. The selected item is scrolled into view using `itemElements.value[selectedIndex.value]?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })` (lines 141-146).

 **Sources:** [src/renderer/src/components/editor/mention/MentionList.vue84](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L84-L84) [src/renderer/src/components/editor/mention/MentionList.vue117-148](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L117-L148) [src/renderer/src/components/editor/mention/MentionList.vue257-284](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L257-L284)

 
## Prompt Parameters System

 Prompts can define parameters (arguments) that require user input before insertion. When a prompt with parameters is selected, the `PromptParamsDialog` is displayed to collect values.

 
### Parameter Definition

 Parameters are stored in the `mcpEntry.arguments` array within the prompt's `CategorizedData`. The `PromptParam` interface (lines 64-68 in PromptParamsDialog.vue) defines each parameter:

 
```

```

 The MCP prompt entry structure (PromptListEntry from @shared/presenter) includes:

 
```

```

 **Sources:** [src/renderer/src/components/editor/mention/MentionList.vue156-161](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L156-L161) [src/renderer/src/components/editor/mention/MentionList.vue202](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L202-L202) [src/renderer/src/components/editor/mention/PromptParamsDialog.vue64-68](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/PromptParamsDialog.vue#L64-L68)

 
### Parameter Collection Flow

 
```

```

 The dialog's `validateParams()` function (lines 93-105) checks required fields and populates `errors.value`. The `hasErrors` computed property (lines 122-136) disables the submit button when required parameters are missing or validation errors exist. When submitted, `handlePromptParams()` (lines 163-188) merges parameter values into `promptContent.argumentsValue` (line 169) before calling `props.command()` (lines 171-176).

 **Sources:** [src/renderer/src/components/editor/mention/MentionList.vue163-225](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L163-L225) [src/renderer/src/components/editor/mention/PromptParamsDialog.vue93-136](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/PromptParamsDialog.vue#L93-L136)

 
## File Attachment to Prompts

 Prompts can have associated files that are automatically attached to the chat message when the prompt is inserted. The system uses a callback mechanism defined in `suggestion.ts` to decouple mention selection from file handling.

 
### File Handler Registration

 The suggestion system defines a module-level variable `promptFilesHandler` (lines 41-54) with registration functions:

 
```

```

 The handler is registered by the chat input component via `setPromptFilesHandler()` and retrieved by `MentionList.vue` via `getPromptFilesHandler()` (lines 178, 230) when a prompt with files is selected.

 
### File Adapter Pattern

 The file attachment system uses an adapter pattern to handle different file types. When `prepareFile()` is called, it delegates to `createFileAdapter()` which:

 
 - Determines MIME type via `detectMimeType()` using the `es-mime-types` library with fallback to text heuristics
 - Looks up the appropriate adapter from `getMimeTypeAdapterMap()` in [src/main/presenter/filePresenter/mime.ts16-108](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L16-L108)
 - Instantiates the adapter with `new AdapterConstructor(filePath, this.maxFileSize)` (line 90)
 
 The adapter map includes adapters for:

 
 - Text files: `TextFileAdapter` (text/plain, text/markdown, application/json)
 - Code files: `CodeFileAdapter` (application/javascript, text/x-python, etc.)
 - Images: `ImageFileAdapter` (image/jpeg, image/png, etc.) - compresses to 1200x1200 JPEG at 70% quality
 - PDFs: `PdfFileAdapter` (application/pdf)
 - Documents: `DocFileAdapter`, `PptFileAdapter`, `ExcelFileAdapter`
 - Audio: `AudioFileAdapter` (audio/mp3, audio/wav, etc.) - returns only file path
 - CSV: `CsvFileAdapter`
 - Unsupported: `UnsupportFileAdapter` (default fallback)
 
 Each adapter extends `BaseFileAdapter` and implements:

 
 - `getFileDescription()`: Returns file type description
 - `getContent()`: Returns original file content
 - `getLLMContent()`: Returns LLM-friendly representation (may compress/transform)
 - `getThumbnail()`: Returns base64 thumbnail (optional)
 
 **Sources:** [src/renderer/src/components/editor/mention/suggestion.ts41-62](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L41-L62) [src/renderer/src/components/editor/mention/MentionList.vue178](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L178-L178) [src/renderer/src/components/editor/mention/MentionList.vue230](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L230-L230) [src/main/presenter/filePresenter/FilePresenter.ts68-91](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L68-L91) [src/main/presenter/filePresenter/mime.ts16-108](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L16-L108) [src/main/presenter/filePresenter/BaseFileAdapter.ts1-74](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts#L1-L74) [src/main/presenter/filePresenter/ImageFileAdapter.ts66-96](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/ImageFileAdapter.ts#L66-L96)

 
### File Attachment Flow

 
```

```

 The `hasFiles()` function (lines 88-98) checks `item.category === 'prompts'` and verifies the `files` array exists via `mcpEntry && 'files' in mcpEntry && mcpEntry.files && Array.isArray(mcpEntry.files) && mcpEntry.files.length > 0`. When files are detected during `selectItem()` (line 229), the handler is retrieved via `getPromptFilesHandler()` (line 230) and called with `mcpEntry.files` (line 232).

 The handler processes files through `FilePresenter.prepareFile()` (line 176-178), which calls `createFileAdapter()` (line 68-91). The adapter creation process involves:

 
 - MIME type detection via `detectMimeType()` from [src/main/presenter/filePresenter/mime.ts110-141](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L110-L141)
 - Adapter selection via `findAdapterForMimeType()` from [src/main/presenter/filePresenter/FilePresenter.ts180-199](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L180-L199)
 - File processing via `adapter.processFile()` from [src/main/presenter/filePresenter/BaseFileAdapter.ts43-68](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts#L43-L68)
 - Content extraction via `adapter.getLLMContent()` (line 135)
 
 The `MessageFile` object returned includes `name`, `token`, `path`, `mimeType`, `metadata`, `thumbnail`, and `content` fields. File processing occurs asynchronously in a `.catch()` block (lines 232-234), allowing mention insertion to proceed in parallel.

 **Sources:** [src/renderer/src/components/editor/mention/MentionList.vue88-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L88-L98) [src/renderer/src/components/editor/mention/MentionList.vue190-236](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/MentionList.vue#L190-L236) [src/main/presenter/filePresenter/FilePresenter.ts68-178](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/FilePresenter.ts#L68-L178) [src/main/presenter/filePresenter/mime.ts110-141](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/mime.ts#L110-L141) [src/main/presenter/filePresenter/BaseFileAdapter.ts43-74](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/filePresenter/BaseFileAdapter.ts#L43-L74)

 
## Workspace File Integration

 The mention system can integrate with workspace file search through the `WorkspaceMentionHandler` interface. This allows users to mention files from their active workspace.

 
### Workspace Handler Interface

 The `WorkspaceMentionHandler` type (lines 28-32) defines the interface for workspace file search:

 
```

```

 The handler is stored in the module-level variable `workspaceMentionHandler` (line 34) and registered via `setWorkspaceMention()` (lines 36-38). During suggestion resolution in the `items()` function (line 75), the system checks `workspaceMentionHandler?.isEnabled.value`. When enabled, `workspaceMentionHandler.searchWorkspaceFiles(query)` is called (line 76), and results from `workspaceFileResults.value` (line 77) are prepended to the mention list (line 102).

 **Sources:** [src/renderer/src/components/editor/mention/suggestion.ts28-38](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L28-L38) [src/renderer/src/components/editor/mention/suggestion.ts73-102](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L73-L102)

 
## Usage in Editor

 The mention system is integrated into the TipTap editor configuration with the custom `Mention` extension and the `suggestion` configuration. The mention trigger character is `@`, and it's allowed after any character (null prefix restriction).

 When a user types `@`, the suggestion system is activated. As they continue typing, the item list is filtered in real-time. Selecting an item (via click or Enter) inserts a mention node into the editor with the specified attributes.

 The inserted mention preserves the `category` and `content` attributes through HTML serialization, allowing the system to extract prompt data with parameters and file references when the message is submitted.

 **Sources:** [src/renderer/src/components/editor/mention/suggestion.ts64-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/suggestion.ts#L64-L98) [src/renderer/src/components/editor/mention/mention.ts1-42](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/editor/mention/mention.ts#L1-L42)
