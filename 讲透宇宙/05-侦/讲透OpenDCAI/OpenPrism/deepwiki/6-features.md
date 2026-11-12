<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/OpenPrism · page 6 Features · fetched 2026-11-02 -->

# Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [apps/frontend/src/app/EditorPage.tsx](apps/frontend/src/app/EditorPage.tsx)

</details>



This document describes the user-facing features and workflows available in OpenPrism. It covers the functional capabilities exposed through the editor interface, focusing on how users interact with the system and the underlying mechanisms that enable these features.

For architectural details about the frontend structure, see [Frontend Application](#4). For backend service implementation, see [Backend Application](#5). For development guidance on extending features, see [Development Guide](#7).

---

## Overview

OpenPrism provides a comprehensive feature set organized into seven functional areas:

| Category | Features | Primary Purpose |
|----------|----------|-----------------|
| **Editing** | LaTeX editing, auto-save, syntax highlighting | Core document authoring |
| **AI Assistance** | Chat, Agent, Tools modes, autocomplete | AI-powered content generation and editing |
| **Compilation** | Multi-engine support, error parsing | PDF generation and validation |
| **Preview** | PDF viewer, outline, figures gallery | Document visualization |
| **Search** | arXiv search, web search | Research and citation discovery |
| **Generation** | Plot generation, vision OCR | Asset creation from data or images |
| **Review** | Diff viewer, quality checks | Change review and document analysis |

**Sources:** [README.md:63-117](), [apps/frontend/src/app/EditorPage.tsx:1094-1150]()

---

## Feature Activation Flow

The following diagram shows how users activate different features through the editor interface and the corresponding state management:

```mermaid
graph TB
    User["User Action"]
    
    subgraph "UI Activation Points"
        Sidebar["Sidebar Tabs<br/>(activeSidebar state)"]
        TopBar["Top Bar Controls<br/>(compile, save, settings)"]
        Editor["Editor Shortcuts<br/>(Alt+/, Tab, Cmd+S)"]
        RightPanel["Right Panel Views<br/>(rightView state)"]
    end
    
    subgraph "Feature State Management"
        EditorState["EditorPage Component State<br/>~200 state variables"]
        CMState["CodeMirror State<br/>(cmViewRef)"]
        Settings["AppSettings<br/>(localStorage)"]
    end
    
    subgraph "Feature Modules"
        FilesTab["Files Tab<br/>activeSidebar='files'"]
        AgentTab["Agent Tab<br/>activeSidebar='agent'"]
        VisionTab["Vision Tab<br/>activeSidebar='vision'"]
        SearchTab["Search Tabs<br/>search/websearch"]
        PlotTab["Plot Tab<br/>activeSidebar='plot'"]
        ReviewTab["Review Tab<br/>activeSidebar='review'"]
    end
    
    User --> Sidebar
    User --> TopBar
    User --> Editor
    User --> RightPanel
    
    Sidebar --> EditorState
    TopBar --> EditorState
    Editor --> CMState
    RightPanel --> EditorState
    
    EditorState --> Settings
    CMState --> EditorState
    
    EditorState --> FilesTab
    EditorState --> AgentTab
    EditorState --> VisionTab
    EditorState --> SearchTab
    EditorState --> PlotTab
    EditorState --> ReviewTab
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:1094-1150](), [apps/frontend/src/app/EditorPage.tsx:3387-3446]()

---

## LaTeX Editing

### Core Editor Features

OpenPrism uses **CodeMirror 6** as the editing engine with custom LaTeX extensions:

| Feature | Implementation | Code Reference |
|---------|---------------|----------------|
| Syntax Highlighting | `latex()` language mode | [apps/frontend/src/latex/lang:8]() |
| Code Folding | `latexFoldService` function | [apps/frontend/src/app/EditorPage.tsx:288-316]() |
| Autocompletion | `latexCompletionSource` | [apps/frontend/src/app/EditorPage.tsx:590-649]() |
| Auto-save | Debounced `saveActiveFile` | [apps/frontend/src/app/EditorPage.tsx:1690-1709]() |

### File Tree Operations

The file tree supports comprehensive project management:

```mermaid
graph LR
    subgraph "Tree Operations"
        Create["Create File/Folder<br/>beginInlineCreate"]
        Rename["Rename<br/>beginInlineRename"]
        Move["Drag & Drop<br/>moveFileWithOrder"]
        Reorder["Reorder Within Folder<br/>reorderWithinFolder"]
        Upload["Upload Files<br/>handleUpload"]
    end
    
    subgraph "State Management"
        TreeState["tree state<br/>(path, type)[]"]
        FileOrder["fileOrder state<br/>Record<string, string[]>"]
        InlineEdit["inlineEdit state<br/>(kind, path, value)"]
    end
    
    subgraph "Persistence"
        API["updateFileOrder API"]
        FS["File System Operations<br/>writeFile, renamePath"]
    end
    
    Create --> InlineEdit
    Rename --> InlineEdit
    InlineEdit --> TreeState
    
    Move --> FileOrder
    Reorder --> FileOrder
    FileOrder --> API
    
    Upload --> FS
    FS --> TreeState
```

The tree builder (`buildTree` function) constructs a hierarchical representation from flat file paths and applies custom ordering:

**Sources:** [apps/frontend/src/app/EditorPage.tsx:362-410](), [apps/frontend/src/app/EditorPage.tsx:2368-2438](), [apps/frontend/src/app/EditorPage.tsx:2440-2469]()

### Outline Navigation

The outline panel extracts section headings using `parseOutline`:

```mermaid
graph TB
    MainFile["mainFile state<br/>(selected .tex)"]
    Content["Document Content"]
    Parser["parseOutline function<br/>regex: /\\+(section|subsection|subsubsection)/"]
    
    subgraph "Outline Items"
        Item1["OutlineItem<br/>{title, level, pos, line}"]
    end
    
    Display["Outline Panel UI<br/>collapsible list"]
    Jump["Jump to Position<br/>view.dispatch selection"]
    
    MainFile --> Content
    Content --> Parser
    Parser --> Item1
    Item1 --> Display
    Display --> Jump
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:438-460](), [apps/frontend/src/app/EditorPage.tsx:3532-3574]()

---

## AI Assistant Modes

OpenPrism provides three distinct AI interaction modes with different execution behaviors:

### Mode Comparison

| Mode | Execution | File Modifications | Use Case |
|------|-----------|-------------------|----------|
| **Chat** | `mode='direct'` | Read-only | Questions, explanations |
| **Agent** | `mode='direct'` or `mode='tools'` | Generates patches for review | Content editing, rewriting |
| **Tools** | `mode='tools'` | Multi-step with tool calls | Complex refactoring, multi-file edits |

### Interaction Flow

```mermaid
graph TB
    subgraph "UI State"
        ModeToggle["assistantMode state<br/>'chat' | 'agent'"]
        TaskSelect["task state<br/>polish/rewrite/translate/custom"]
        ModeSelect["mode state<br/>'direct' | 'tools'"]
        Prompt["prompt state<br/>user input"]
    end
    
    subgraph "Context Building"
        Selection["selectionText<br/>(editor selection)"]
        FileContent["editorValue<br/>(current file)"]
        ProjectCtx["buildProjectContext()<br/>scans includes"]
        CompileLogCtx["compileLog state<br/>(error context)"]
    end
    
    subgraph "API Call"
        RunAgent["runAgent API<br/>POST /api/agent/run"]
        Payload["AgentRequest<br/>{task, prompt, mode, content}"]
    end
    
    subgraph "Response Handling"
        Reply["res.reply<br/>(conversational)"]
        Suggestion["res.suggestion<br/>(inline replacement)"]
        Patches["res.patches[]<br/>(file modifications)"]
    end
    
    subgraph "UI Updates"
        ChatMsg["chatMessages/agentMessages<br/>append with typewriter"]
        PendingChanges["pendingChanges state<br/>for diff review"]
        RightViewSwitch["setRightView('diff')"]
    end
    
    ModeToggle --> RunAgent
    TaskSelect --> Payload
    ModeSelect --> Payload
    Prompt --> Payload
    
    Selection --> ProjectCtx
    FileContent --> ProjectCtx
    ProjectCtx --> Payload
    CompileLogCtx --> Payload
    
    RunAgent --> Reply
    RunAgent --> Suggestion
    RunAgent --> Patches
    
    Reply --> ChatMsg
    Suggestion --> PendingChanges
    Patches --> PendingChanges
    PendingChanges --> RightViewSwitch
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:3083-3175](), [apps/frontend/src/app/EditorPage.tsx:1800-1835]()

### Task Types

The `DEFAULT_TASKS` constant defines available tasks:

- **polish**: Language refinement
- **rewrite**: Content restructuring
- **structure**: Section reorganization
- **translate**: Language translation with scope (selection/file/project)
- **websearch**: Automated arXiv search with tool calls
- **custom**: User-defined instructions

**Translation Scope Handling:**

```mermaid
graph LR
    TranslateTask["task='translate'"]
    
    subgraph "Scope Selection"
        Selection["translateScope='selection'<br/>uses selectionText"]
        File["translateScope='file'<br/>uses editorValue"]
        Project["translateScope='project'<br/>mode='tools' multi-file"]
    end
    
    subgraph "Execution"
        DirectMode["mode='direct'<br/>single file"]
        ToolsMode["mode='tools'<br/>file operations"]
    end
    
    TranslateTask --> Selection
    TranslateTask --> File
    TranslateTask --> Project
    
    Selection --> DirectMode
    File --> DirectMode
    Project --> ToolsMode
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:82-89](), [apps/frontend/src/app/EditorPage.tsx:3087-3128]()

---

## AI Autocomplete

### Ghost Text Mechanism

Autocomplete uses CodeMirror's decoration system to display inline suggestions:

```mermaid
graph TB
    subgraph "Trigger"
        KeyPress["Keyboard Event<br/>Alt+/ or Cmd+Space"]
        Handler["requestInlineSuggestion"]
    end
    
    subgraph "Context Extraction"
        CursorPos["cursor position<br/>(view.state.selection.main.head)"]
        Before["4000 chars before cursor"]
        After["400 chars after cursor"]
        Heading["findNearestHeading<br/>(section context)"]
        Env["findCurrentEnvironment<br/>(e.g., 'itemize')"]
    end
    
    subgraph "LLM Request"
        Prompt["Autocomplete prompt<br/>'Continue after <CURSOR>'"]
        RunAgent["runAgent<br/>(task='autocomplete', mode='direct')"]
        Response["res.suggestion"]
    end
    
    subgraph "Ghost Decoration"
        GhostWidget["GhostWidget class<br/>WidgetType implementation"]
        SetEffect["setGhostEffect<br/>StateEffect"]
        GhostField["ghostField<br/>StateField"]
        Display["Rendered ghost text<br/>className='cm-ghost'"]
    end
    
    subgraph "Acceptance"
        Tab["Tab key → acceptInlineSuggestion"]
        Arrow["Arrow → acceptSuggestionChunk"]
        Escape["Escape → clearInlineSuggestion"]
    end
    
    KeyPress --> Handler
    Handler --> CursorPos
    CursorPos --> Before
    CursorPos --> After
    CursorPos --> Heading
    CursorPos --> Env
    
    Before --> Prompt
    After --> Prompt
    Heading --> Prompt
    Env --> Prompt
    
    Prompt --> RunAgent
    RunAgent --> Response
    
    Response --> SetEffect
    SetEffect --> GhostField
    GhostField --> GhostWidget
    GhostWidget --> Display
    
    Display --> Tab
    Display --> Arrow
    Display --> Escape
```

**Key Implementation Details:**

1. **GhostWidget Class**: Custom CodeMirror widget for rendering suggestions
   ```typescript
   class GhostWidget extends WidgetType {
     constructor(private text: string) { super(); }
     toDOM() {
       const span = document.createElement('span');
       span.className = 'cm-ghost';
       span.textContent = this.text;
       return span;
     }
   }
   ```

2. **State Field Management**: `ghostField` tracks the current decoration

3. **Chunk Acceptance**: `nextSuggestionChunk` extracts word-by-word for arrow key acceptance

**Sources:** [apps/frontend/src/app/EditorPage.tsx:651-695](), [apps/frontend/src/app/EditorPage.tsx:1579-1627](), [apps/frontend/src/app/EditorPage.tsx:1514-1552]()

---

## Document Compilation

### Engine Selection and Fallback

OpenPrism supports multiple LaTeX engines with auto-fallback:

| Engine | Type | Command | Use Case |
|--------|------|---------|----------|
| `pdflatex` | Standard | `pdflatex` | Default compilation |
| `xelatex` | Extended | `xelatex` | Unicode, Chinese support |
| `lualatex` | Lua-based | `lualatex` | Lua scripting |
| `latexmk` | Build tool | `latexmk -pdf` | Automated multi-pass |
| `tectonic` | Modern | `tectonic` | Lightweight fallback |

### Compilation Pipeline

```mermaid
graph TB
    subgraph "Preparation"
        Trigger["compile() function"]
        SaveCurrent["Save active file<br/>(in-memory → server)"]
        FetchAll["getAllFiles API<br/>GET /api/projects/:id/files"]
        MergeEdits["Merge unsaved edits<br/>fileMap[activePath] = editorValue"]
    end
    
    subgraph "Backend Request"
        CompileAPI["compileProject API<br/>POST /api/compile"]
        Payload["CompileRequest<br/>{projectId, mainFile, engine}"]
    end
    
    subgraph "Backend Processing"
        WriteTemp["Write files to temp dir"]
        ExecEngine["Execute LaTeX engine<br/>child_process.spawn"]
        CaptureOutput["Capture stdout/stderr"]
        ReadPDF["Read generated PDF"]
    end
    
    subgraph "Response Handling"
        ParseLog["parseCompileErrors<br/>extract file:line"]
        SetCompileLog["setCompileLog state"]
        CreateBlob["Create Blob URL<br/>URL.createObjectURL"]
        UpdatePDF["setPdfUrl state"]
    end
    
    subgraph "Error Display"
        CompileErrors["compileErrors useMemo<br/>CompileError[]"]
        ClickableLog["Clickable log items<br/>jumpToError function"]
    end
    
    Trigger --> SaveCurrent
    SaveCurrent --> FetchAll
    FetchAll --> MergeEdits
    MergeEdits --> CompileAPI
    
    CompileAPI --> Payload
    Payload --> WriteTemp
    WriteTemp --> ExecEngine
    ExecEngine --> CaptureOutput
    CaptureOutput --> ReadPDF
    
    ReadPDF --> ParseLog
    ParseLog --> SetCompileLog
    ReadPDF --> CreateBlob
    CreateBlob --> UpdatePDF
    
    SetCompileLog --> CompileErrors
    CompileErrors --> ClickableLog
```

**Error Parsing Logic:**

The `parseCompileErrors` function uses regex to extract structured error information:

```typescript
// Matches: filename.tex:123
const fileLineMatch = line.match(/([A-Za-z0-9_./-]+\.tex):(\d+));

// Matches: ! Error message
if (line.startsWith('!')) {
  const message = line.replace(/^!+\s*/, '').trim();
  // Look ahead for l.123 line number
}
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:2886-2941](), [apps/frontend/src/app/EditorPage.tsx:776-815](), [apps/frontend/src/app/EditorPage.tsx:2697-2716]()

### One-Click Diagnose

The diagnose feature sends compilation errors to the AI for automated fixes:

```mermaid
graph LR
    User["User clicks diagnose"]
    DiagnoseBtn["diagnoseCompile function<br/>(diagnoseBusy state)"]
    
    AgentCall["runAgent<br/>task='debug_compile'"]
    Payload["Payload<br/>{selection: compileLog, mode: 'tools'}"]
    
    Response["Response patches<br/>(fixes)"]
    DiffView["Show in diff viewer<br/>setPendingChanges"]
    
    User --> DiagnoseBtn
    DiagnoseBtn --> AgentCall
    AgentCall --> Payload
    Payload --> Response
    Response --> DiffView
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:3177-3221]()

---

## PDF Preview

### Rendering Architecture

PDF preview uses **PDF.js** with custom text layer rendering:

```mermaid
graph TB
    subgraph "Initialization"
        PdfUrl["pdfUrl state<br/>(Blob URL)"]
        Component["PdfPreview component"]
        Container["containerRef<br/>(DOM element)"]
    end
    
    subgraph "Loading"
        GetDoc["getDocument(pdfUrl)<br/>PDF.js API"]
        LoadTask["Loading task promise"]
        PdfDoc["pdf document object"]
    end
    
    subgraph "Scale Calculation"
        FitWidth["fitWidth prop<br/>(boolean)"]
        ContainerWidth["container.clientWidth"]
        PageViewport["page.getViewport({scale: 1.0})"]
        CalcScale["baseScale = containerWidth / viewport.width"]
    end
    
    subgraph "Page Rendering Loop"
        ForEach["For each page 1..numPages"]
        Canvas["Create canvas element<br/>high DPI scaling"]
        RenderCtx["page.render({canvasContext, viewport})"]
        TextLayer["renderTextLayer<br/>selectable text"]
        PageWrapper["div.pdf-page<br/>data-page-number"]
    end
    
    subgraph "Interactive Features"
        TextClick["onClick handler<br/>onTextClick callback"]
        Outline["getOutline()<br/>onOutline callback"]
        Annotations["pdfAnnotations state<br/>overlay markers"]
    end
    
    PdfUrl --> GetDoc
    GetDoc --> LoadTask
    LoadTask --> PdfDoc
    
    PdfDoc --> FitWidth
    FitWidth --> ContainerWidth
    ContainerWidth --> PageViewport
    PageViewport --> CalcScale
    
    CalcScale --> ForEach
    ForEach --> Canvas
    Canvas --> RenderCtx
    RenderCtx --> TextLayer
    TextLayer --> PageWrapper
    
    PageWrapper --> TextClick
    PdfDoc --> Outline
    Container --> Annotations
```

**Quality Boost:**

High-DPI rendering is achieved by rendering at higher scale then CSS-scaling down:

```typescript
const cssViewport = page.getViewport({ scale: baseScale });
const qualityBoost = Math.min(2.4, (window.devicePixelRatio || 1) * 1.25);
const renderViewport = page.getViewport({ scale: baseScale * qualityBoost });

canvas.width = renderViewport.width;
canvas.height = renderViewport.height;
canvas.style.width = `${cssViewport.width}px`;
canvas.style.height = `${cssViewport.height}px`;
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:882-1092](), [apps/frontend/src/app/EditorPage.tsx:911-1048]()

### Zoom and Navigation

```mermaid
graph LR
    subgraph "Zoom Controls"
        FitBtn["Fit Width button<br/>setPdfFitWidth(true)"]
        ZoomIn["Zoom In<br/>zoomPdf(+0.2)"]
        ZoomOut["Zoom Out<br/>zoomPdf(-0.2)"]
        ScaleValue["pdfScale state<br/>(0.6 - 2.5)"]
    end
    
    subgraph "Display Modes"
        SinglePage["Single Page<br/>spread=false"]
        SpreadView["Spread View<br/>spread=true"]
    end
    
    subgraph "Outline Navigation"
        OutlineItems["pdfOutline state<br/>{title, page, level}[]"]
        TOCPanel["Table of Contents view<br/>rightView='toc'"]
        ScrollTo["scrollToPdfPage<br/>(page number)"]
    end
    
    FitBtn --> ScaleValue
    ZoomIn --> ScaleValue
    ZoomOut --> ScaleValue
    
    ScaleValue --> SinglePage
    ScaleValue --> SpreadView
    
    OutlineItems --> TOCPanel
    TOCPanel --> ScrollTo
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:2989-3007](), [apps/frontend/src/app/EditorPage.tsx:3000-3007]()

---

## Diff Viewer

### Split Diff Rendering

The diff viewer uses the `diff` library to generate line-by-line comparisons:

```mermaid
graph TB
    subgraph "Pending Changes"
        AgentResponse["Agent response patches<br/>res.patches[]"]
        PendingState["pendingChanges state<br/>PendingChange[]"]
        Structure["Structure<br/>{filePath, original, proposed, diff}"]
    end
    
    subgraph "Diff Generation"
        DiffLines["diffLines(original, proposed)<br/>from 'diff' library"]
        Parts["Parts array<br/>{value, added?, removed?}"]
        BuildSplit["buildSplitDiff function"]
        Rows["Rows array<br/>{left, right, leftNo, rightNo, type}"]
    end
    
    subgraph "Rendering"
        Component["SplitDiffView component"]
        LeftCol["Left column<br/>(Before)"]
        RightCol["Right column<br/>(After)"]
        SyncScroll["Synchronized scrolling<br/>lockRef mechanism"]
    end
    
    subgraph "Actions"
        ApplyBtn["Apply button<br/>applyPending function"]
        DiscardBtn["Discard button<br/>discardPending function"]
        WriteFile["writeFile API<br/>persist changes"]
    end
    
    AgentResponse --> PendingState
    PendingState --> Structure
    Structure --> DiffLines
    DiffLines --> Parts
    Parts --> BuildSplit
    BuildSplit --> Rows
    
    Rows --> Component
    Component --> LeftCol
    Component --> RightCol
    LeftCol --> SyncScroll
    RightCol --> SyncScroll
    
    Component --> ApplyBtn
    Component --> DiscardBtn
    ApplyBtn --> WriteFile
```

**Synchronized Scroll Implementation:**

```typescript
const lockRef = useRef(false);

const syncScroll = (source: HTMLDivElement | null, target: HTMLDivElement | null) => {
  if (!source || !target || lockRef.current) return;
  lockRef.current = true;
  target.scrollTop = source.scrollTop;
  target.scrollLeft = source.scrollLeft;
  requestAnimationFrame(() => {
    lockRef.current = false;
  });
};
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:732-767](), [apps/frontend/src/app/EditorPage.tsx:834-880](), [apps/frontend/src/app/EditorPage.tsx:3223-3254]()

---

## Academic Search

### arXiv Search Flow

```mermaid
graph TB
    subgraph "User Input"
        Query["arxivQuery state<br/>(keyword input)"]
        MaxResults["arxivMaxResults<br/>(1-10)"]
        UseLLM["useLlmSearch<br/>(boolean toggle)"]
    end
    
    subgraph "Search Execution"
        DirectSearch["Direct API<br/>arxivSearch API"]
        LLMSearch["LLM-powered<br/>runAgent with tools"]
        SearchMode{{"Search Mode"}}
    end
    
    subgraph "Direct API Path"
        ArxivAPI["GET /api/arxiv/search<br/>searchArxiv endpoint"]
        ArxivResponse["ArxivPaper[]<br/>{title, authors, arxivId, url}"]
    end
    
    subgraph "LLM Tools Path"
        ToolsMode["mode='tools'<br/>arxiv_search + arxiv_bibtex"]
        JSONExtract["extractJsonBlock<br/>safeJsonParse"]
        LLMOutput["llmSearchOutput state<br/>(raw response)"]
        ParsedPapers["Parsed papers with BibTeX"]
    end
    
    subgraph "Results Display"
        ResultsList["arxivResults state<br/>checkbox list"]
        SelectPapers["arxivSelected state<br/>Record<string, boolean>"]
    end
    
    subgraph "BibTeX Generation"
        FetchBib["arxivBibtex API<br/>GET /api/arxiv/bibtex/:id"]
        Cache["arxivBibtexCache state"]
        ExtractKey["extractBibKey<br/>regex: /@\w+\s*{\s*([^,\s]+)/"]
    end
    
    subgraph "Application"
        TargetBib["bibTarget state<br/>(selected .bib file)"]
        WriteBib["Write BibTeX entries<br/>ensureFileContent + writeFile"]
        InsertCite["Insert citations<br/>autoInsertCite option"]
        AIInsert["AI-powered insertion<br/>autoInsertToMain option"]
    end
    
    Query --> SearchMode
    MaxResults --> SearchMode
    UseLLM --> SearchMode
    
    SearchMode -->|useLlmSearch=false| DirectSearch
    SearchMode -->|useLlmSearch=true| LLMSearch
    
    DirectSearch --> ArxivAPI
    ArxivAPI --> ArxivResponse
    ArxivResponse --> ResultsList
    
    LLMSearch --> ToolsMode
    ToolsMode --> JSONExtract
    JSONExtract --> LLMOutput
    LLMOutput --> ParsedPapers
    ParsedPapers --> ResultsList
    ParsedPapers --> Cache
    
    ResultsList --> SelectPapers
    SelectPapers --> FetchBib
    FetchBib --> Cache
    Cache --> ExtractKey
    
    ExtractKey --> TargetBib
    TargetBib --> WriteBib
    WriteBib --> InsertCite
    WriteBib --> AIInsert
```

**LLM Search Prompt:**

```typescript
const prompt = [
  'Search arXiv for the user query.',
  `Return at most ${arxivMaxResults} papers.`,
  'Use arxiv_search and arxiv_bibtex tools.',
  'Return JSON ONLY in this schema:',
  '{"papers":[{"title":"","authors":[],"arxivId":"","bibtex":""}]}.'
].join(' ');
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:1842-1921](), [apps/frontend/src/app/EditorPage.tsx:1923-2045]()

### Citation Insertion

Two insertion modes are available:

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Auto Insert** | `autoInsertCite=true` | Inserts `\cite{key1,key2}` at cursor in active .tex file |
| **AI Insert** | `autoInsertToMain=true` | Uses Agent with Tools mode to insert citations in Related Work section |

**AI Insertion Prompt:**

```typescript
const prompt = [
  'Insert citations into the target TeX file.',
  `Target file: ${targetFile}.`,
  `Use \\cite{${keys.join(',')}}.`,
  'If a Related Work section exists, add the citations there.',
  'Otherwise add a Related Work subsection near the end and cite the papers.',
  'Keep edits minimal and preserve formatting.',
  citePayload.length > 0 ? `Papers: ${JSON.stringify(citePayload)}` : ''
].filter(Boolean).join(' ');
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:1975-2039]()

---

## Web Search

### Multi-Point Search Strategy

Web search implements a query expansion strategy:

```mermaid
graph TB
    subgraph "Query Processing"
        UserQuery["websearchQuery<br/>(user input)"]
        SplitQuery["Split query into 2-4 sub-queries<br/>callLLM with prompt"]
        SubQueries["queries array<br/>(targeted searches)"]
    end
    
    subgraph "Parallel Search"
        Parallel["Promise.all execution"]
        Search1["Search query 1<br/>callLLM with provider search"]
        Search2["Search query 2"]
        Search3["Search query 3"]
        Search4["Search query 4"]
    end
    
    subgraph "Result Aggregation"
        Extract["Extract JSON from each response<br/>extractJsonBlock + safeJsonParse"]
        Dedupe["Deduplicate by URL and title"]
        WebsearchItems["WebsearchItem[]<br/>{id, title, summary, url, bibtex, citeKey}"]
    end
    
    subgraph "Summarization"
        ItemSummaries["Generate per-item summaries<br/>callLLM"]
        ItemNotes["websearchItemNotes state<br/>Record<string, string>"]
        Paragraph["Generate综合总结<br/>callLLM"]
        WebsearchPara["websearchParagraph state<br/>(integrated summary)"]
    end
    
    subgraph "Insertion"
        SelectItems["websearchSelected state<br/>(user checkboxes)"]
        BibWrite["Write BibTeX to target file"]
        TexInsert["Insert summaries to target TeX<br/>itemize + paragraph"]
    end
    
    UserQuery --> SplitQuery
    SplitQuery --> SubQueries
    SubQueries --> Parallel
    
    Parallel --> Search1
    Parallel --> Search2
    Parallel --> Search3
    Parallel --> Search4
    
    Search1 --> Extract
    Search2 --> Extract
    Search3 --> Extract
    Search4 --> Extract
    
    Extract --> Dedupe
    Dedupe --> WebsearchItems
    
    WebsearchItems --> ItemSummaries
    ItemSummaries --> ItemNotes
    WebsearchItems --> Paragraph
    Paragraph --> WebsearchPara
    
    WebsearchItems --> SelectItems
    SelectItems --> BibWrite
    ItemNotes --> TexInsert
    WebsearchPara --> TexInsert
```

**Log Output:**

The `websearchLog` state array tracks progress through the pipeline:

```typescript
appendLog(setWebsearchLog, '拆分查询...');
appendLog(setWebsearchLog, `并行检索: ${queries.join(' | ')}`);
appendLog(setWebsearchLog, `检索中: ${q}`);
appendLog(setWebsearchLog, `完成: ${q} (${count})`);
appendLog(setWebsearchLog, `聚合结果: ${count} 条`);
appendLog(setWebsearchLog, '生成逐条总结...');
appendLog(setWebsearchLog, '生成综合总结...');
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:2082-2247](), [apps/frontend/src/app/EditorPage.tsx:2250-2317]()

### Output Format

The insertion generates structured LaTeX:

```latex
\paragraph{逐条总结}
\begin{itemize}
  \item Summary 1 \cite{key1}
  \item Summary 2 \cite{key2}
  \item Summary 3 \cite{key3}
\end{itemize}

\paragraph{综合总结}
Integrated summary paragraph with inline citations \cite{key1,key2}.
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:2290-2316]()

---

## Plot Generation

### Table-to-Chart Pipeline

```mermaid
graph TB
    subgraph "Input"
        Selection["selectionText<br/>(LaTeX table)"]
        Validate["Validate contains<br/>\\begin{tabular} or \\begin{table}"]
    end
    
    subgraph "Configuration"
        PlotType["plotType: 'bar' | 'line' | 'heatmap'"]
        PlotTitle["plotTitle (optional)"]
        PlotFilename["plotFilename (optional)"]
        PlotPrompt["plotPrompt (optional constraints)"]
        PlotRetries["plotRetries: number (default 2)"]
    end
    
    subgraph "Backend Processing"
        API["plotFromTable API<br/>POST /api/plot/from-table"]
        LLMGen["LLM generates Python code<br/>(matplotlib/seaborn)"]
        TempDir["Create temp directory"]
        WritePayload["Write payload.json + plot.py"]
        ExecPython["Execute python3 plot.py"]
        SaveAsset["Save to project assets/<br/>(generated filename)"]
    end
    
    subgraph "Response Handling"
        AssetPath["res.assetPath<br/>(relative path)"]
        RefreshTree["refreshTree()<br/>(update file list)"]
        InsertFigure["insertFigureSnippet<br/>(if plotAutoInsert)"]
    end
    
    subgraph "Figure Snippet"
        FigureEnv["\\begin{figure}[t]<br/>  \\centering<br/>  \\includegraphics[width=0.9\\linewidth]{path}<br/>  \\caption{Caption.}<br/>  \\label{fig:...}<br/>\\end{figure}"]
    end
    
    Selection --> Validate
    Validate --> API
    
    PlotType --> API
    PlotTitle --> API
    PlotFilename --> API
    PlotPrompt --> API
    PlotRetries --> API
    
    API --> LLMGen
    LLMGen --> TempDir
    TempDir --> WritePayload
    WritePayload --> ExecPython
    ExecPython --> SaveAsset
    
    SaveAsset --> AssetPath
    AssetPath --> RefreshTree
    RefreshTree --> InsertFigure
    InsertFigure --> FigureEnv
```

**LLM Code Generation:**

The backend uses an LLM to generate Python plotting code from the LaTeX table. The prompt includes:
- Table content
- Chart type specification
- Optional user constraints
- Output format requirements (save to specific path)

**Sources:** [apps/frontend/src/app/EditorPage.tsx:2047-2080](), [apps/frontend/src/app/EditorPage.tsx:1745-1756]()

---

## Vision OCR

### Image-to-LaTeX Conversion

```mermaid
graph TB
    subgraph "Input"
        FileSelect["visionFile state<br/>(File object)"]
        ModeSelect["visionMode<br/>equation|table|figure|algorithm|ocr"]
        UserPrompt["visionPrompt<br/>(optional constraints)"]
    end
    
    subgraph "Upload"
        Preview["visionPreviewUrl<br/>URL.createObjectURL"]
        DropZone["Drag & drop / paste / click<br/>image-drop-zone"]
    end
    
    subgraph "Processing"
        API["visionToLatex API<br/>POST /api/vision/latex"]
        FormData["multipart/form-data<br/>{file, mode, prompt, llmConfig}"]
        VisionLLM["Vision-capable LLM<br/>gpt-4o or custom endpoint"]
    end
    
    subgraph "Mode-Specific Prompts"
        EquationMode["mode='equation'<br/>只输出 equation 环境"]
        TableMode["mode='table'<br/>只输出 tabular/table"]
        AlgorithmMode["mode='algorithm'<br/>只输出 algorithm/algorithmic"]
        FigureMode["mode='figure'<br/>图像描述 + 图注"]
        OCRMode["mode='ocr'<br/>纯文字提取"]
    end
    
    subgraph "Output"
        Result["visionResult state<br/>(editable textarea)"]
        InsertBtn["handleVisionInsert<br/>insertAtCursor with block"]
    end
    
    FileSelect --> Preview
    Preview --> DropZone
    DropZone --> API
    
    ModeSelect --> EquationMode
    ModeSelect --> TableMode
    ModeSelect --> AlgorithmMode
    ModeSelect --> FigureMode
    ModeSelect --> OCRMode
    
    EquationMode --> API
    TableMode --> API
    AlgorithmMode --> API
    FigureMode --> API
    OCRMode --> API
    
    UserPrompt --> API
    API --> FormData
    FormData --> VisionLLM
    VisionLLM --> Result
    Result --> InsertBtn
```

**Mode Examples:**

| Mode | Input | Expected Output |
|------|-------|----------------|
| `equation` | Formula image | `\begin{equation} E = mc^2 \end{equation}` |
| `table` | Table screenshot | `\begin{tabular}{lcc} ... \end{tabular}` |
| `algorithm` | Algorithm diagram | `\begin{algorithm} ... \end{algorithm}` |
| `figure` | Chart/graph | Image description suitable for caption |
| `ocr` | Text image | Plain text extraction |

**Vision LLM Configuration:**

The feature uses `visionLlmConfig` which can override the default LLM endpoint:

```typescript
const visionLlmConfig = useMemo(() => {
  const hasOverride = Boolean(visionEndpoint || visionApiKey || visionModel);
  return {
    endpoint: (hasOverride ? visionEndpoint : llmEndpoint) || llmEndpoint,
    apiKey: (hasOverride ? visionApiKey : llmApiKey) || undefined,
    model: (hasOverride ? visionModel : llmModel) || llmModel
  };
}, [llmEndpoint, llmApiKey, llmModel, visionEndpoint, visionApiKey, visionModel]);
```

**Sources:** [apps/frontend/src/app/EditorPage.tsx:3326-3361](), [apps/frontend/src/app/EditorPage.tsx:1271-1278]()

---

## Peer Review

### Quality Check Features

The review tab provides four analysis modes:

| Check Type | Method | Output |
|------------|--------|--------|
| **Review Report** | LLM-based analysis | Full reviewer-style report |
| **Consistency Check** | Term/symbol analysis | List of inconsistencies |
| **Missing Citations** | Statement analysis | Statements needing citations |
| **Compile Summary** | Log analysis | Error summary with fixes |

### Review Report Generation

```mermaid
graph TB
    subgraph "Trigger"
        ReviewBtn["Generate Report button<br/>reviewReportBusy state"]
    end
    
    subgraph "Document Analysis"
        MainContent["mainFile content<br/>or active file"]
        ProjectContext["buildProjectContext()<br/>full project scan"]
    end
    
    subgraph "LLM Analysis"
        Prompt["Review prompt<br/>(quality metrics, structure, clarity)"]
        RunAgent["runAgent<br/>task='review', mode='direct'"]
        Response["Markdown report"]
    end
    
    subgraph "Display"
        ReviewReport["reviewReport state"]
        Markdown["ReactMarkdown component<br/>with remarkGfm"]
        RightPanel["rightView='review'"]
    end
    
    ReviewBtn --> MainContent
    MainContent --> ProjectContext
    ProjectContext --> Prompt
    Prompt --> RunAgent
    RunAgent --> Response
    Response --> ReviewReport
    ReviewReport --> Markdown
    Markdown --> RightPanel
```

**Review Categories:**

The report typically includes:
- **Structure**: Section organization, logical flow
- **Clarity**: Writing quality, technical accuracy
- **Citations**: Completeness of references
- **Figures/Tables**: Quality and relevance
- **Originality**: Contribution assessment
- **Reproducibility**: Method clarity

**Sources:** [apps/frontend/src/app/EditorPage.tsx:3438-3446](), [README.md:110-117]()

---

## Template Management

### Template Application

Templates provide pre-configured project structures:

```mermaid
graph LR
    subgraph "Built-in Templates"
        ACL["ACL Conference<br/>(acl_latex.pdf)"]
        CVPR["CVPR Conference<br/>(cvpr template)"]
        NeurIPS["NeurIPS Conference<br/>(neurips_2024.sty)"]
        ICML["ICML Conference<br/>(icml template)"]
    end
    
    subgraph "Template Structure"
        Manifest["template.json<br/>{name, category, description}"]
        Files["Template files<br/>(.tex, .sty, .cls, .bst)"]
    end
    
    subgraph "Application"
        SelectTemplate["Select during project creation<br/>or conversion"]
        CopyFiles["Copy template files<br/>to project directory"]
        PreserveContent["Preserve existing content<br/>(if conversion)"]
    end
    
    ACL --> Manifest
    CVPR --> Manifest
    NeurIPS --> Manifest
    ICML --> Manifest
    
    Manifest --> Files
    Files --> SelectTemplate
    SelectTemplate --> CopyFiles
    CopyFiles --> PreserveContent
```

**Template Discovery:**

Templates are discovered from the `templates/` directory structure. Each template contains:
- `template.json`: Metadata
- Main `.tex` file: Document structure
- Style files (`.sty`, `.cls`)
- Bibliography styles (`.bst`)

**One-Click Conversion:**

Users can convert existing projects to a different template while preserving content.

**Sources:** [README.md:83-86](), [apps/frontend/src/app/ProjectPage.tsx]()

---

## Project Import

### ZIP File Import

Standard project import from ZIP archives:

```mermaid
graph LR
    Upload["User uploads ZIP"]
    Parse["Extract archive"]
    Create["Create project directory"]
    Write["Write files"]
    Navigate["Navigate to editor"]
    
    Upload --> Parse
    Parse --> Create
    Create --> Write
    Write --> Navigate
```

### arXiv Project Import (SSE)

arXiv import uses Server-Sent Events for progress tracking:

```mermaid
graph TB
    subgraph "User Input"
        ArxivURL["arXiv URL<br/>(e.g., arxiv.org/abs/2301.12345)"]
        ExtractID["Extract arXiv ID<br/>regex pattern"]
    end
    
    subgraph "SSE Connection"
        SSEEndpoint["GET /api/projects/import-arxiv-sse<br/>?arxivId=..."]
        EventStream["Server-Sent Events stream"]
    end
    
    subgraph "Backend Progress"
        Download["Download .tar.gz<br/>from arXiv"]
        Progress1["Event: phase=download<br/>percent=X"]
        Extract["Extract archive"]
        Progress2["Event: phase=extract<br/>percent=Y"]
        CreateProject["Create project directory"]
        WriteFiles["Write extracted files"]
        Progress3["Event: phase=complete<br/>projectId=..."]
    end
    
    subgraph "Frontend Updates"
        ProgressBar["Progress indicator<br/>(phase + percent)"]
        StatusMessage["Status message updates"]
        Complete["Navigate to editor<br/>on completion"]
    end
    
    ArxivURL --> ExtractID
    ExtractID --> SSEEndpoint
    SSEEndpoint --> EventStream
    
    EventStream --> Download
    Download --> Progress1
    Progress1 --> ProgressBar
    
    EventStream --> Extract
    Extract --> Progress2
    Progress2 --> ProgressBar
    
    EventStream --> CreateProject
    CreateProject --> WriteFiles
    WriteFiles --> Progress3
    Progress3 --> Complete
    
    ProgressBar --> StatusMessage
```

**SSE Event Format:**

```json
{
  "phase": "download" | "extract" | "complete",
  "percent": 0-100,
  "projectId": "generated-id" // only on complete
}
```

**Sources:** [apps/frontend/src/app/ProjectPage.tsx](), [apps/backend/src/routes/projects.js]()

---

## Feature Configuration

### Settings Panel

User preferences are stored in `localStorage` under the key `OPENPRISM_SETTINGS_KEY`:

```mermaid
graph TB
    subgraph "Settings State"
        Settings["AppSettings interface<br/>{llmEndpoint, llmApiKey, llmModel, ...}"]
        Default["DEFAULT_SETTINGS constant"]
        Load["loadSettings()<br/>from localStorage"]
        Persist["persistSettings()<br/>to localStorage"]
    end
    
    subgraph "Configuration Categories"
        LLM["LLM Configuration<br/>endpoint, apiKey, model"]
        Search["Search LLM Override<br/>searchEndpoint, searchApiKey, searchModel"]
        Vision["Vision LLM Override<br/>visionEndpoint, visionApiKey, visionModel"]
        Engine["Compile Engine<br/>pdflatex|xelatex|lualatex|latexmk|tectonic"]
    end
    
    subgraph "Configuration Resolution"
        BaseConfig["Base llmConfig<br/>useMemo"]
        SearchConfig["searchLlmConfig<br/>(override if set)"]
        VisionConfig["visionLlmConfig<br/>(override if set)"]
    end
    
    subgraph "UI"
        SettingsBtn["Settings button"]
        Modal["Settings modal"]
        Form["Configuration form"]
    end
    
    Load --> Settings
    Settings --> LLM
    Settings --> Search
    Settings --> Vision
    Settings --> Engine
    
    LLM --> BaseConfig
    Search --> SearchConfig
    Vision --> VisionConfig
    
    Settings --> Persist
    
    SettingsBtn --> Modal
    Modal --> Form
    Form --> Settings
```

**Configuration Precedence:**

1. **Runtime overrides**: Per-request parameters (e.g., specific llmConfig in agent call)
2. **Frontend localStorage**: User settings panel
3. **Backend environment**: `.env` file variables
4. **System defaults**: Hardcoded `DEFAULT_SETTINGS`

**Sources:** [apps/frontend/src/app/EditorPage.tsx:100-143](), [apps/frontend/src/app/EditorPage.tsx:1254-1278]()

---

