<!-- source: DeepWiki mcp.deepwiki.com · repo giselles-ai/giselle · page 3 Knowledge and Context Systems · fetched 2026-10-26 -->

# Knowledge and Context Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-list.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/sidebar-menu.tsx)
- [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts](apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts)
- [internal-packages/ui/components/form-field.tsx](internal-packages/ui/components/form-field.tsx)
- [internal-packages/ui/components/section-header.tsx](internal-packages/ui/components/section-header.tsx)
- [internal-packages/ui/components/status-indicator.tsx](internal-packages/ui/components/status-indicator.tsx)

</details>



The Knowledge and Context Systems provide retrieval-augmented generation (RAG) capabilities to the Giselle platform. These systems process documents (PDFs, text files, Markdown), manage vector stores (GitHub repositories and uploaded documents), generate embeddings using multiple providers, and execute semantic similarity searches to provide relevant context for AI generations.

The system consists of three primary components:
1. **Document Processing Pipeline** ([3.1](#31-document-processing-pipeline)): Extracts text and images from binary documents using the `@giselles-ai/document-preprocessor` package
2. **Vector Store Management** ([3.2](#32-vector-store-management)): Configures and manages GitHub and Document vector stores through the team settings UI
3. **RAG System and Query Execution** ([3.3](#33-rag-system-and-query-execution)): Chunks documents, generates embeddings, and performs similarity searches using PostgreSQL with pgvector

For information about how the Giselle Engine integrates vector stores into generation workflows, see page 2. For database schema details, see page 2.6.

## 3.1 Document Processing Pipeline

The document preprocessing system transforms raw binary files (PDFs, plain text, Markdown) into normalized text and image data suitable for embedding and indexing. The core functionality is implemented in the `@giselles-ai/document-preprocessor` package, which provides a unified API for extracting text and rendering images from various document formats.

### Architecture and Core Components

```mermaid
graph TB
    subgraph "Document Preprocessor Package"
        extractText["extractText()<br/>packages/document-preprocessor/src/text.ts"]
        extractPdfText["extractPdfText()<br/>packages/document-preprocessor/src/pdf.ts"]
        renderPdfPageImages["renderPdfPageImages()<br/>packages/document-preprocessor/src/pdf.ts"]
        
        subgraph "Internal Utilities"
            withPdfDocument["withPdfDocument()<br/>internal/pdfium.ts"]
            normalizeExtractedText["normalizeExtractedText()<br/>internal/text-normalizer.ts"]
            toUint8Array["toUint8Array()<br/>internal/binary.ts"]
            assertNotAborted["assertNotAborted()<br/>internal/abort.ts"]
        end
    end
    
    subgraph "External Dependencies"
        embedpdf["@embedpdf/pdfium<br/>PDFium WASM bindings"]
        pngjs["pngjs<br/>PNG encoding library"]
    end
    
    subgraph "Input Types"
        BinaryDataInput["BinaryDataInput<br/>Buffer | Uint8Array | ArrayBuffer"]
    end
    
    subgraph "Output Types"
        TextExtractionResult["TextExtractionResult<br/>{ text: string }"]
        PdfTextExtractionResult["PdfTextExtractionResult<br/>{ totalPages, pages[] }"]
        PdfImageRenderResult["PdfImageRenderResult<br/>{ totalPages, pages[] }"]
    end
    
    BinaryDataInput --> extractText
    BinaryDataInput --> extractPdfText
    BinaryDataInput --> renderPdfPageImages
    
    extractText --> toUint8Array
    extractText --> assertNotAborted
    extractText --> TextExtractionResult
    
    extractPdfText --> withPdfDocument
    extractPdfText --> normalizeExtractedText
    extractPdfText --> assertNotAborted
    extractPdfText --> PdfTextExtractionResult
    
    renderPdfPageImages --> withPdfDocument
    renderPdfPageImages --> pngjs
    renderPdfPageImages --> assertNotAborted
    renderPdfPageImages --> PdfImageRenderResult
    
    withPdfDocument --> embedpdf
```

**Sources:** [packages/document-preprocessor/src/index.ts:1-13](), [packages/document-preprocessor/src/pdf.ts:1-138](), [packages/document-preprocessor/src/text.ts:1-37](), [packages/document-preprocessor/src/types.ts:1-53]()

### Processing Functions

| Function | Input | Options | Output | Use Case |
|----------|-------|---------|--------|----------|
| `extractText()` | Buffer, Uint8Array, ArrayBuffer | `encoding`, `signal` | `{ text: string }` | Plain text and Markdown files |
| `extractPdfText()` | Binary PDF data | `password`, `maxPages`, `signal` | `{ totalPages, pages: PdfTextPage[] }` | Extract text content from PDFs |
| `renderPdfPageImages()` | Binary PDF data | `password`, `targetDpi`, `maxPages`, `renderFormFields`, `signal` | `{ totalPages, pages: PdfImagePage[] }` | Render PDF pages as PNG images |

**Sources:** [packages/document-preprocessor/src/pdf.ts:21-54](), [packages/document-preprocessor/src/pdf.ts:56-99](), [packages/document-preprocessor/src/text.ts:13-36]()

### PDF Processing Implementation

The PDF processing pipeline uses the PDFium library through `@embedpdf/pdfium` bindings. The `withPdfDocument()` helper manages the PDFium document lifecycle:

```mermaid
sequenceDiagram
    participant Client
    participant extractPdfText
    participant withPdfDocument
    participant PDFiumDocument
    participant PDFiumPage
    participant normalizeExtractedText
    
    Client->>extractPdfText: Binary data + options
    extractPdfText->>withPdfDocument: bytes, { password, signal }
    withPdfDocument->>PDFiumDocument: Load document
    
    loop For each page (up to maxPages)
        extractPdfText->>extractPdfText: assertNotAborted(signal)
        extractPdfText->>PDFiumDocument: loadPage(index)
        PDFiumDocument->>PDFiumPage: Create page
        extractPdfText->>PDFiumPage: getText()
        PDFiumPage-->>extractPdfText: rawText
        extractPdfText->>normalizeExtractedText: rawText
        normalizeExtractedText-->>extractPdfText: normalized text
        extractPdfText->>PDFiumPage: close()
    end
    
    withPdfDocument->>PDFiumDocument: Close document
    extractPdfText-->>Client: { totalPages, pages }
```

**Sources:** [packages/document-preprocessor/src/pdf.ts:21-54](), [packages/document-preprocessor/README.md:36-50]()

### Text Normalization

The `normalizeExtractedText()` function in [packages/document-preprocessor/src/internal/text-normalizer.ts]() performs the following transformations on extracted PDF text:

1. Repairs hyphenated line breaks (e.g., "exam-\nple" → "example")
2. Normalizes whitespace (multiple spaces/newlines → single space)
3. Removes trailing/leading whitespace
4. Preserves intentional paragraph breaks

**Sources:** [packages/document-preprocessor/README.md:9]()

### Image Rendering Pipeline

For PDFs that require visual processing, `renderPdfPageImages()` converts each page to a PNG buffer:

```mermaid
graph LR
    PDFPage["PDF Page"] --> render["page.render()<br/>scale, renderFormFields"]
    render --> RGBA["RGBA pixel data<br/>Uint8Array"]
    RGBA --> encodeRgbaToPng["encodeRgbaToPng()<br/>width, height"]
    encodeRgbaToPng --> PNG["PNG.pack()"]
    PNG --> chunks["Buffer chunks"]
    chunks --> concat["Buffer.concat()"]
    concat --> Uint8Array["Uint8Array<br/>(PNG data)"]
```

The rendering process:
1. Calculates scale factor from target DPI (default 144 DPI)
2. Renders page to RGBA pixel buffer using PDFium
3. Encodes RGBA data to PNG using `pngjs` library
4. Returns page number, dimensions, and PNG buffer

**Sources:** [packages/document-preprocessor/src/pdf.ts:56-99](), [packages/document-preprocessor/src/pdf.ts:101-130]()

### Abort Signal Support

All extraction functions accept an `AbortSignal` for cancellation:

```typescript
// From pdf.ts
for (let index = 0; index < limit; index += 1) {
    assertNotAborted(signal);  // Throws if aborted
    const page = document.loadPage(index);
    // ... process page
}
```

The `assertNotAborted()` helper throws immediately if the signal has been aborted, enabling responsive cancellation of long-running document processing operations.

**Sources:** [packages/document-preprocessor/src/pdf.ts:37](), [packages/document-preprocessor/README.md:72-79]()

### Security Considerations

From [packages/document-preprocessor/README.md:149-154]():

- **PDFium sandboxing**: PDFium engine executes in a sandboxed environment to mitigate malicious PDF risks
- **Password-protected PDFs**: Handle encrypted PDFs cautiously; not all encryption schemes are fully supported
- **Resource limits**: Enforce file size and processing time limits to prevent DoS attacks

The package supports password-protected PDFs through the `password` option in `PdfTextExtractionOptions` and `PdfImageRenderOptions`.

**Sources:** [packages/document-preprocessor/README.md:149-154](), [packages/document-preprocessor/src/types.ts:14-18](), [packages/document-preprocessor/src/types.ts:32-38]()

## 3.2 Vector Store Management

The vector store system manages two types of repositories: GitHub repositories (code, issues, and pull requests) and document uploads (PDFs and text files). Both use configurable embedding profiles and share a common architecture built on PostgreSQL with the pgvector extension. The management UI is located at `/settings/team/vector-stores` in the Studio application.

### Vector Store Types and Database Schema

```mermaid
graph TB
    subgraph "UI_Components"
        VectorStoresPage["/settings/team/vector-stores/page.tsx<br/>Main vector stores page"]
        RepositoryList["RepositoryList component<br/>repository-list.tsx"]
        DocumentVectorStoreList["DocumentVectorStoreList component<br/>document-vector-store-list.tsx"]
        RepositoryItem["RepositoryItem component<br/>repository-item.tsx"]
        DocumentVectorStoreItem["DocumentVectorStoreItem component<br/>document-vector-store-item.tsx"]
    end
    
    subgraph "Database_Tables"
        githubRepositoryIndex["githubRepositoryIndex<br/>id, owner, repo, teamDbId, installationId"]
        githubRepositoryEmbeddingProfiles["githubRepositoryEmbeddingProfiles<br/>repositoryIndexDbId, embeddingProfileId"]
        githubRepositoryContentStatus["githubRepositoryContentStatus<br/>contentType, status, errorCode, retryAfter, metadata"]
        
        documentVectorStores["documentVectorStores<br/>id, teamDbId, name"]
        documentEmbeddingProfiles["documentEmbeddingProfiles<br/>documentVectorStoreDbId, embeddingProfileId"]
        documentVectorStoreSources["documentVectorStoreSources<br/>id, fileName, storageKey, ingestStatus"]
    end
    
    subgraph "Actions"
        registerRepositoryIndex["registerRepositoryIndex()<br/>actions.ts:107"]
        updateRepositoryIndex["updateRepositoryIndex()<br/>actions.ts:257"]
        triggerManualIngest["triggerManualIngest()<br/>actions.ts:554"]
        createDocumentVectorStore["createDocumentVectorStore()<br/>actions.ts:616"]
        updateDocumentVectorStore["updateDocumentVectorStore()<br/>actions.ts:702"]
    end
    
    VectorStoresPage --> RepositoryList
    VectorStoresPage --> DocumentVectorStoreList
    RepositoryList --> RepositoryItem
    DocumentVectorStoreList --> DocumentVectorStoreItem
    
    RepositoryItem --> registerRepositoryIndex
    RepositoryItem --> updateRepositoryIndex
    RepositoryItem --> triggerManualIngest
    
    DocumentVectorStoreItem --> createDocumentVectorStore
    DocumentVectorStoreItem --> updateDocumentVectorStore
    
    registerRepositoryIndex --> githubRepositoryIndex
    registerRepositoryIndex --> githubRepositoryEmbeddingProfiles
    registerRepositoryIndex --> githubRepositoryContentStatus
    
    createDocumentVectorStore --> documentVectorStores
    createDocumentVectorStore --> documentEmbeddingProfiles
    createDocumentVectorStore --> documentVectorStoreSources
```

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx:1-80](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-892](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:1-565]()

### GitHub Repository Vector Store

GitHub repositories are indexed with three content types: `blob` (code files), `issue` (issue titles, descriptions, and comments), and `pull_request` (merged PR content and discussions). Each content type can be enabled/disabled independently through the `ConfigureSourcesDialog` component, though `blob` is mandatory and cannot be disabled.

#### Repository Index Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | `GitHubRepositoryIndexId` | `gthbi_` prefixed CUID |
| `owner` | `string` | GitHub repository owner |
| `repo` | `string` | Repository name |
| `teamDbId` | `number` | Team association |
| `installationId` | `number` | GitHub App installation ID |

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:166-177]()

#### Content Status Tracking

Each combination of repository + embedding profile + content type has a status record in `githubRepositoryContentStatus`. The `EmbeddingModelCard` component in `repository-item.tsx` displays status for each embedding profile and content type.

**Content Status Lifecycle**

```mermaid
stateDiagram-v2
    [*] --> idle: Initial state
    idle --> running: triggerManualIngest()
    running --> completed: Ingestion succeeds
    running --> failed: Error occurs
    failed --> idle: Retry allowed (retryAfter passed)
    completed --> running: Re-ingest triggered
    
    state failed {
        [*] --> errorCode: Set error code
        errorCode --> retryAfter: Calculate retry timestamp
    }
    
    state completed {
        [*] --> metadata: Store sync metadata
        note right of metadata
            blob: lastIngestedCommitSha
            issue: lastIngestedIssueNumber
            pull_request: lastIngestedPrNumber
        end note
    }
```

The status is displayed in the UI through the `StatusIndicator` and `StatusBadge` components. Each content type section shows:
- **Code**: Status, last sync time, and commit SHA (lines 283-374 in repository-item.tsx)
- **Issues**: Status, last sync time, and issue number (lines 376-468)
- **Pull Requests**: Status, last sync time, and PR number (lines 470-560)

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:240-565](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:1-6]()

#### Registration and Configuration Flow

The `RepositoryRegistrationDialog` component (repository-registration-dialog.tsx) provides the UI for registering new GitHub repositories. Users select:
1. Owner/Organization (from GitHub App installations)
2. Repository name (filtered by selected owner)
3. Content types to ingest (Code, Issues, Pull Requests)
4. Embedding models (at least one required)

**Registration Flow**

```mermaid
sequenceDiagram
    participant User
    participant RepositoryRegistrationDialog as "RepositoryRegistrationDialog<br/>repository-registration-dialog.tsx:41"
    participant registerRepositoryIndex as "registerRepositoryIndex()<br/>actions.ts:107"
    participant validateGitHubAccess as "validateGitHubAccess()<br/>actions.ts:62"
    participant GitHub as "GitHub API"
    participant Database as "db.transaction()"
    participant getInstallationsWithRepos as "getInstallationsWithRepos()<br/>data.ts:58"
    
    User->>RepositoryRegistrationDialog: Open dialog
    RepositoryRegistrationDialog->>getInstallationsWithRepos: Load installations + repos
    getInstallationsWithRepos-->>RepositoryRegistrationDialog: InstallationWithRepos[]
    
    User->>RepositoryRegistrationDialog: Select owner, repo, content types, profiles
    RepositoryRegistrationDialog->>registerRepositoryIndex: registerRepositoryIndex(owner, repo, installationId, contentTypes, embeddingProfileIds)
    
    registerRepositoryIndex->>validateGitHubAccess: validateGitHubAccess(installationId, owner, repo)
    validateGitHubAccess->>GitHub: GET /repos/{owner}/{repo}
    
    alt Repository accessible
        GitHub-->>validateGitHubAccess: 200 OK
        validateGitHubAccess-->>registerRepositoryIndex: { success: true }
        
        registerRepositoryIndex->>Database: Start transaction
        registerRepositoryIndex->>Database: Lock team row (for quota check)
        registerRepositoryIndex->>Database: Check existing repos count < quota.maxStores
        registerRepositoryIndex->>Database: INSERT githubRepositoryIndex
        registerRepositoryIndex->>Database: INSERT githubRepositoryEmbeddingProfiles (for each profile)
        registerRepositoryIndex->>Database: INSERT githubRepositoryContentStatus (profile × contentType)
        Database-->>registerRepositoryIndex: Commit
        
        registerRepositoryIndex->>registerRepositoryIndex: revalidatePath('/settings/team/vector-stores')
        registerRepositoryIndex-->>RepositoryRegistrationDialog: { success: true }
        RepositoryRegistrationDialog-->>User: Close dialog, refresh list
    else Repository not accessible
        GitHub-->>validateGitHubAccess: 404/403
        validateGitHubAccess-->>registerRepositoryIndex: { success: false, error }
        registerRepositoryIndex-->>RepositoryRegistrationDialog: { success: false, error }
        RepositoryRegistrationDialog-->>User: Display error
    end
```

The registration process enforces quota limits by locking the team row during the transaction (lines 161-166 in actions.ts) and checking existing repository count before insertion (lines 188-201).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:62-251](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-registration-dialog.tsx:41-477](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts:58-104]()

### Document Vector Store

Document vector stores allow teams to upload PDF and text files for RAG operations. Each store has a name and one or more embedding profiles. The UI is located at `/settings/team/vector-stores/document` and uses the `DocumentVectorStoreList` and `DocumentVectorStoreItem` components.

#### Document Vector Store Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | `DocumentVectorStoreId` | `dvs_` prefixed CUID (e.g., `dvs_clx9k2...`) |
| `teamDbId` | `number` | Foreign key to teams table |
| `name` | `string` | User-defined name displayed in UI |
| `createdAt` | `Date` | Creation timestamp |

The `createDocumentVectorStore()` action (actions.ts:616-700) creates the store and associated embedding profiles in a single transaction with quota enforcement.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:616-700](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx:1-48]()

#### Document Source Management

Each uploaded file creates a `documentVectorStoreSources` record:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Source ID (CUID) |
| `documentVectorStoreDbId` | `number` | Parent store |
| `fileName` | `string` | Original filename |
| `storageKey` | `string` | Supabase storage path |
| `ingestStatus` | `IngestStatus` | `idle`, `running`, `completed`, `failed` |
| `ingestErrorCode` | `string?` | Error code if failed |

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:254-270]()

#### Document Upload Flow

The `DocumentVectorStoreConfigureDialog` component provides drag-and-drop and file selection UI for uploading documents. File validation occurs client-side before upload.

**File Upload and Ingestion**

```mermaid
sequenceDiagram
    participant User
    participant DocumentVectorStoreConfigureDialog as "DocumentVectorStoreConfigureDialog<br/>document-vector-store-item.tsx:327"
    participant handleFilesUpload as "handleFilesUpload()<br/>:397"
    participant API as "POST /api/vector-stores/document/{id}/documents"
    participant SupabaseStorage as "Supabase Storage<br/>DOCUMENT_VECTOR_STORE_STORAGE_PREFIX"
    participant Database as "documentVectorStoreSources table"
    participant BackgroundIngest as "Background Ingest Job<br/>(trigger.dev or async)"
    
    User->>DocumentVectorStoreConfigureDialog: Drag/drop or select files
    DocumentVectorStoreConfigureDialog->>handleFilesUpload: Validate files
    
    alt Invalid files
        handleFilesUpload->>handleFilesUpload: Check file type, size, empty
        handleFilesUpload-->>User: showErrorToast(error)
    else Valid files
        handleFilesUpload->>API: POST FormData with valid files
        
        loop For each file
            API->>SupabaseStorage: Upload to vector-stores/{storeId}/
            SupabaseStorage-->>API: storageKey
            API->>Database: INSERT documentVectorStoreSources (ingestStatus='idle')
            Database-->>API: sourceId
        end
        
        API-->>handleFilesUpload: { successes: [...], failures: [...] }
        handleFilesUpload->>DocumentVectorStoreConfigureDialog: Update documentSources state
        handleFilesUpload->>DocumentVectorStoreConfigureDialog: setUploadMessage(success message)
        DocumentVectorStoreConfigureDialog-->>User: Display upload success
        
        Note over BackgroundIngest: Triggered asynchronously on insert
        BackgroundIngest->>Database: UPDATE ingestStatus='running'
        BackgroundIngest->>SupabaseStorage: Download file via storageKey
        BackgroundIngest->>BackgroundIngest: extractPdfText() or extractText()
        BackgroundIngest->>BackgroundIngest: Generate embeddings via embedMany()
        BackgroundIngest->>Database: Store embeddings in pgvector
        BackgroundIngest->>Database: UPDATE ingestStatus='completed' or 'failed'
    end
```

**File Validation Rules** (enforced in handleFilesUpload):
- Supported types: PDF, TXT, MD (defined in `DOCUMENT_VECTOR_STORE_SUPPORTED_MIME_TYPES`)
- Max file size: `DOCUMENT_VECTOR_STORE_MAX_FILE_SIZE_BYTES` (displayed as `DOCUMENT_VECTOR_STORE_MAX_FILE_SIZE_LABEL`)
- Empty files rejected
- Validation helper: `isSupportedDocumentFile()` checks MIME type and extension

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:327-634](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:55]()

### Embedding Profile System

Embedding profiles define which embedding model to use for a vector store. Different profiles have different dimensions and providers. The profiles are defined in `@giselles-ai/protocol` and re-exported by the vector store UI components.

#### Embedding Profile Configuration

The `EMBEDDING_PROFILES` constant in `@giselles-ai/protocol` defines four profiles:

| ID | Name | Provider | Model | Dimensions | GitHub Support | Document Support |
|----|------|----------|-------|------------|----------------|------------------|
| 1 | OpenAI Small | openai | text-embedding-3-small | 1536 | ✓ | ✓ |
| 2 | OpenAI Large | openai | text-embedding-3-large | 3072 | ✓ | ✓ |
| 3 | Google | google | text-embedding-004 | 768 | ✓ | ✓ |
| 4 | Cohere | cohere | embed-english-v3.0 | 1024 | ✗ | ✓ |

**GitHub Vector Store Profiles** (github-embedding-profiles.ts:1-13):
```typescript
import { EMBEDDING_PROFILES } from "@giselles-ai/protocol";

export const GITHUB_EMBEDDING_PROFILES = {
  1: EMBEDDING_PROFILES[1], // OpenAI Small
  2: EMBEDDING_PROFILES[2], // OpenAI Large
  3: EMBEDDING_PROFILES[3], // Google (excludes Cohere)
} as const;
```

**Document Vector Store Profiles** (document-embedding-profiles.ts:1-5):
```typescript
import { EMBEDDING_PROFILES } from "@giselles-ai/protocol";

// Surface all currently supported providers (OpenAI, Google, Cohere)
export const DOCUMENT_EMBEDDING_PROFILES = EMBEDDING_PROFILES;
```

Document Vector Stores support all four profiles, while GitHub Vector Stores exclude Cohere (profile ID 4) from the UI selection.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/github-embedding-profiles.ts:1-13](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts:1-6]()

#### Profile Selection and Updates

Users can select multiple embedding profiles when registering a vector store. The system enforces:
- At least one profile must be selected
- The blob content type for GitHub repositories cannot be disabled
- Updates create/remove embedding profiles and content statuses in a transaction

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:114-145](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:216-367]()

### Manual Ingestion and Status Management

Teams can trigger manual ingestion for GitHub repositories through the "Ingest Now" option in the `RepoActionMenu` (repository-item.tsx:130-138). The system enforces ingestability rules before allowing manual triggers.

**Ingestability Check Flow**

```mermaid
flowchart TD
    User["User clicks 'Ingest Now'<br/>RepositoryItem:90"]
    HandleManualIngest["handleManualIngest()<br/>RepositoryItem:90"]
    TriggerManualIngest["triggerManualIngest(indexId)<br/>actions.ts:554"]
    FetchRepo["fetchRepositoryWithStatuses()<br/>actions.ts:896"]
    CheckIngestability["checkIngestability(contentStatuses)<br/>actions.ts:929"]
    
    User --> HandleManualIngest
    HandleManualIngest --> TriggerManualIngest
    TriggerManualIngest --> FetchRepo
    FetchRepo --> CheckIngestability
    
    CheckIngestability --> Rule1{For each enabled<br/>content status}
    
    Rule1 --> StatusCheck{Check status}
    StatusCheck -->|idle or completed| CanIngest[canIngest = true]
    StatusCheck -->|running| IsStale{Updated > 15 min ago?}
    StatusCheck -->|failed| HasRetry{retryAfter <= now?}
    
    IsStale -->|Yes| CanIngest
    IsStale -->|No| CannotIngest[canIngest = false<br/>Return error]
    
    HasRetry -->|Yes| CanIngest
    HasRetry -->|No| CannotIngest
    
    CanIngest --> CreateTrigger["createManualIngestTrigger(userId)<br/>lib/vector-stores/github"]
    CreateTrigger --> ExecuteManualIngest["executeManualIngest(repositoryData, trigger)<br/>actions.ts:978"]
    ExecuteManualIngest --> After["after(() => processRepository())<br/>Next.js after() API"]
    After --> ProcessRepository["processRepository(repositoryData, trigger)<br/>lib/vector-stores/github"]
    ProcessRepository --> UpdateStatus["Update githubRepositoryContentStatus<br/>Set status=running"]
    
    CannotIngest --> ReturnError["Return { success: false, error }"]
```

**Ingestability Rules** (checkIngestability function, actions.ts:929-973):
1. Content status must be `enabled: true`
2. Status must be one of:
   - `idle` or `completed` (ready to re-ingest)
   - `running` with `updatedAt` more than 15 minutes ago (stale, allow re-trigger)
   - `failed` with `retryAfter` timestamp in the past
3. At least one `blob` content status must exist

The manual ingest button is disabled when `canManuallyIngest` is false (repository-item.tsx:105-114).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:554-593](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:929-985](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:90-114]()

### Diagnostic and Recovery System

When a GitHub repository becomes inaccessible (e.g., due to `DOCUMENT_NOT_FOUND` error from changed installation permissions), the `DiagnosticModal` component helps users diagnose and restore connectivity. The modal is triggered by clicking "Check ↗" next to failed content types (repository-item.tsx:320-327).

**Diagnostic Flow**

```mermaid
sequenceDiagram
    participant User
    participant DiagnosticModal as "DiagnosticModal<br/>diagnostic-modal.tsx:31"
    participant RunDiagnosis as "runDiagnosis()<br/>:44"
    participant DiagnoseAction as "diagnoseRepositoryConnection(indexId)<br/>actions.ts:424"
    participant GitHubAPI as "GitHub API"
    participant UpdateAction as "updateRepositoryInstallation(indexId, newId)<br/>actions.ts:505"
    participant Database as "db.update()"
    
    User->>DiagnosticModal: Click "Check ↗" on failed repo
    DiagnosticModal->>RunDiagnosis: open=true triggers useEffect
    RunDiagnosis->>DiagnoseAction: diagnoseRepositoryConnection(repositoryIndex.id)
    
    DiagnoseAction->>GitHubAPI: userClient.getInstallations()
    GitHubAPI-->>DiagnoseAction: installations[]
    
    loop For each installation
        DiagnoseAction->>GitHubAPI: buildAppInstallationClient(installation.id)
        DiagnoseAction->>GitHubAPI: GET /repos/{owner}/{repo}
        
        alt Repository accessible
            GitHubAPI-->>DiagnoseAction: 200 OK
            DiagnoseAction->>DiagnoseAction: Set validInstallationId
        else Repository not accessible
            GitHubAPI-->>DiagnoseAction: 404 or 403
        end
    end
    
    alt Valid installation found
        DiagnoseAction-->>DiagnosticModal: { canBeFixed: true, newInstallationId }
        DiagnosticModal-->>User: Show "Restore Connection" button
        
        User->>DiagnosticModal: Click "Restore Connection"
        DiagnosticModal->>UpdateAction: updateRepositoryInstallation(indexId, newInstallationId)
        
        UpdateAction->>Database: UPDATE githubRepositoryIndex SET installationId
        UpdateAction->>Database: UPDATE githubRepositoryContentStatus<br/>SET status='idle', errorCode=null, retryAfter=null
        UpdateAction->>UpdateAction: revalidatePath('/settings/team/vector-stores')
        UpdateAction-->>DiagnosticModal: Success
        DiagnosticModal-->>User: Close modal, refresh page
        
    else No valid installation
        DiagnoseAction-->>DiagnosticModal: { canBeFixed: false, reason, errorMessage }
        DiagnosticModal-->>User: Show "Delete Repository" button
        
        alt User deletes repo
            User->>DiagnosticModal: Click "Delete Repository"
            DiagnosticModal->>DiagnosticModal: onDelete() callback
        end
    end
```

**Diagnostic Results** (DiagnosticResult type, types.ts:32-41):
- `canBeFixed: true` with `newInstallationId`: Repository found in another installation
- `canBeFixed: false` with reason:
  - `no-installation`: No installation has access
  - `repository-not-found`: Repository not found in database
  - `diagnosis-failed`: Error during diagnosis

The recovery process resets all content statuses to `idle` and clears error codes, allowing re-ingestion under the new installation (actions.ts:534-546).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx:23-206](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:424-549](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:32-42]()

### Storage Layer Integration

Vector stores use two storage systems:

1. **Supabase PostgreSQL** (with pgvector extension) for embeddings and metadata
2. **Supabase Storage** for document source files

The storage prefix for document files is defined as:
```typescript
const DOCUMENT_VECTOR_STORE_STORAGE_PREFIX = "vector-stores";
```

This corresponds to a Supabase bucket where PDF and text files are stored before ingestion.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:53](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:43-52]()

## 3.3 RAG System and Query Execution

The RAG pipeline integrates document processing, embedding generation, and similarity search to enable context-aware generation operations. This section describes how processed documents are chunked, embedded, stored, and queried. The RAG implementation is primarily located in the `@giselles-ai/rag` package and supporting libraries in `lib/vector-stores/`.

### RAG Pipeline Architecture

```mermaid
graph TB
    subgraph "Document Ingestion"
        Upload["Document Upload<br/>PDF, Text, Markdown"]
        Extract["extractPdfText() / extractText()"]
        Chunk["Chunking Strategy<br/>Paragraph/sentence-based"]
        Embed["Embedding Generation<br/>AI SDK embedMany()"]
    end
    
    subgraph "Vector Store"
        PGVector["PostgreSQL + pgvector<br/>Similarity search"]
        Metadata["Metadata Tables<br/>githubRepositoryContentStatus<br/>documentVectorStoreSources"]
    end
    
    subgraph "Query Execution"
        QueryNode["Query Node in Workflow"]
        TemplateResolution["Resolve template references<br/>{{sourceNode.text}}"]
        GenerateEmbedding["Generate query embedding"]
        SimilaritySearch["pgvector similarity search<br/><-> operator"]
        ResultRanking["Rank by cosine similarity"]
    end
    
    subgraph "Generation Context"
        ContextAssembly["Assemble context from results"]
        LLMGeneration["LLM Generation<br/>generateText/generateContent"]
    end
    
    Upload --> Extract
    Extract --> Chunk
    Chunk --> Embed
    Embed --> PGVector
    Embed --> Metadata
    
    QueryNode --> TemplateResolution
    TemplateResolution --> GenerateEmbedding
    GenerateEmbedding --> SimilaritySearch
    SimilaritySearch --> PGVector
    PGVector --> ResultRanking
    ResultRanking --> ContextAssembly
    ContextAssembly --> LLMGeneration
```

**Sources:** [packages/document-preprocessor/src/index.ts:1-13](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts:1-42]()

### Chunking Strategies

After text extraction via `extractPdfText()` or `extractText()`, documents are split into chunks for embedding. The chunking implementation varies by content type and is handled by the ingestion pipeline (not directly visible in the provided vector store UI files).

**Content Type Chunking Strategies**

| Content Type | Strategy | Metadata Displayed in UI | Metadata Location in Code |
|--------------|----------|--------------------------|---------------------------|
| Code (blob) | File-based | Commit SHA (e.g., `abc1234`) | `blobStatus.metadata.lastIngestedCommitSha` (repository-item.tsx:350-356) |
| Issues | Issue-based | Issue number (e.g., `#42`) | `issueStatus.metadata.lastIngestedIssueNumber` (repository-item.tsx:444-448) |
| Pull Requests | PR-based | PR number (e.g., `#123`) | `pullRequestStatus.metadata.lastIngestedPrNumber` (repository-item.tsx:538-542) |
| PDF Documents | Page/paragraph-based | Page number, file name | `documentVectorStoreSources.fileName` (document-vector-store-item.tsx:280-295) |
| Plain Text | Paragraph-based | Source file name | `documentVectorStoreSources.fileName` |

The `metadata` field in `githubRepositoryContentStatus` stores chunk-specific information that is displayed in the UI after successful ingestion (status = `completed`).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:346-361](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:438-452](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:286-295]()

### Embedding Generation

Embeddings are generated using the AI SDK's `embedMany()` function with the configured embedding profile:

```typescript
// Conceptual flow (actual implementation in lib/vector-stores)
const chunks = splitDocumentIntoChunks(text);
const embeddings = await embedMany({
  model: embeddingProfile.model,
  values: chunks.map(chunk => chunk.text),
});

// Store in pgvector
for (let i = 0; i < chunks.length; i++) {
  await db.insert(embeddingTable).values({
    content: chunks[i].text,
    embedding: embeddings[i],
    embeddingProfileId: profile.id,
    metadata: chunks[i].metadata,
  });
}
```

Each embedding profile (OpenAI Small, OpenAI Large, Google, Cohere) uses a different dimension size, which affects storage requirements and query performance.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/github-embedding-profiles.ts:1-13]()

### Query Resolution and Template References

Query nodes in workflows support template references to dynamically include content from source nodes:

```typescript
// Example query template
const queryTemplate = "Find code related to {{sourceNode.text}}";

// Resolution process
const resolvedQuery = resolveTemplateReferences(queryTemplate, sourceNodes);
// Result: "Find code related to authentication implementation"
```

The resolved query text is then embedded using the same embedding profile as the target vector store, ensuring semantic similarity search works correctly.

**Sources:** Based on workflow node query patterns in the codebase (implementation details in query execution layer not shown in provided files)

### Similarity Search with pgvector

PostgreSQL with the pgvector extension provides efficient similarity search using the cosine distance operator (`<->`):

```sql
-- Conceptual query structure
SELECT 
  content,
  metadata,
  1 - (embedding <-> $queryEmbedding) as similarity
FROM embeddings
WHERE embedding_profile_id = $profileId
  AND repository_index_db_id = $repositoryDbId  -- or document_vector_store_db_id
ORDER BY embedding <-> $queryEmbedding
LIMIT $topK;
```

The `<->` operator computes cosine distance between the query embedding and stored embeddings. Results are ranked by similarity (1 - distance), with the most similar chunks returned first.

**Sources:** Based on pgvector usage patterns (actual SQL in lib/vector-stores not shown in provided files)

### Query Execution and Context Assembly

The query execution flow integrates workflow nodes with vector stores through the Giselle Engine. While the detailed implementation is in the `@giselles-ai/rag` and engine packages (see page 2), the vector store UI surfaces key configuration:

**Vector Store Configuration for Queries**

The vector store system provides:
1. **Store Selection**: Users select which GitHub or Document vector store to query
2. **Embedding Profile**: Determines which embedding space to search within
3. **Content Type Filtering**: For GitHub stores, filter by blob/issue/pull_request
4. **Status Visibility**: UI shows which content is ready (`completed`) for querying

**Query Execution Components**

```mermaid
graph LR
    subgraph "Vector_Store_Configuration"
        RepositoryItem["RepositoryItem<br/>repository-item.tsx"]
        DocumentItem["DocumentVectorStoreItem<br/>document-vector-store-item.tsx"]
        EmbeddingProfileSelector["Embedding Profile Selection<br/>GITHUB_EMBEDDING_PROFILES"]
    end
    
    subgraph "Database_Layer"
        PGVector["PostgreSQL + pgvector<br/>Cosine similarity: <->"]
        EmbeddingTables["Embedding tables<br/>(by profile ID)"]
        MetadataTables["githubRepositoryContentStatus<br/>documentVectorStoreSources"]
    end
    
    subgraph "Query_Interface"
        RAGPackage["@giselles-ai/rag<br/>Vector similarity search"]
        QueryServices["Vector Store Query Services<br/>GitHub/Document/Issue/PR"]
    end
    
    subgraph "Workflow_Integration"
        QueryNode["Query Workflow Node<br/>Uses vector store as context"]
        TextGenNode["TextGeneration Node<br/>Receives context from query"]
    end
    
    RepositoryItem --> EmbeddingProfileSelector
    DocumentItem --> EmbeddingProfileSelector
    EmbeddingProfileSelector --> EmbeddingTables
    
    EmbeddingTables --> PGVector
    MetadataTables --> PGVector
    
    PGVector --> RAGPackage
    RAGPackage --> QueryServices
    QueryServices --> QueryNode
    QueryNode --> TextGenNode
```

**Vector Store Status and Query Readiness**

Only vector stores with `status='completed'` content are ready for queries. The UI displays:
- **Ready badge** (green): Content ingested and queryable
- **Processing badge** (blue): Ingestion in progress, not yet queryable
- **Failed badge** (red): Ingestion failed, requires diagnostic check
- **Pending badge** (yellow): Ingestion queued, waiting to start

The `StatusIndicator` and `IngestStatusBadge` components visualize query readiness (repository-item.tsx:289-293, document-vector-store-item.tsx:63-127).

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:240-320](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx:63-127]()

### Error Handling and Retry Logic

The vector store system implements automatic retry logic for failed ingestion operations:

| Error Code | Description | Retry Strategy |
|------------|-------------|----------------|
| `DOCUMENT_NOT_FOUND` | Repository/file not accessible | Manual fix via diagnostic modal |
| `DOCUMENT_FETCH_ERROR` | Transient fetch failure | Exponential backoff with `retryAfter` |
| `DOCUMENT_RATE_LIMITED` | GitHub rate limit hit | Wait until rate limit reset |
| `DOCUMENT_TOO_LARGE` | File exceeds size limit | No retry (permanent failure) |

The `retryAfter` timestamp in `githubRepositoryContentStatus` controls when a failed ingestion can be retried. Users can manually trigger ingestion once `retryAfter` has passed.

**Sources:** [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/types.ts:1-5](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/repository-item.tsx:98-107](), [apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/error-messages.ts]()

### Integration with Workflow Nodes

Vector stores are consumed by workflow nodes through node-specific interfaces:

1. **GitHub Vector Store Node**: Queries code and PR embeddings using repository-specific profiles
2. **Document Vector Store Node**: Queries uploaded document embeddings
3. **Query Node**: Generic interface supporting both GitHub and Document stores

Node properties panels allow users to select the target vector store and configure query parameters (e.g., `topK` results, embedding profile selection).

**Sources:** Based on workflow node patterns described in the architecture diagrams (detailed implementation in workflow-designer-ui not shown in provided files)

---

