<!-- source: DeepWiki mcp.deepwiki.com · repo morluto/rea · page 5 Artifacts and Packages · fetched 2026-10-09 -->

# Artifacts and Packages

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/verify-package-artifact.mjs](scripts/verify-package-artifact.mjs)
- [src/application/ArtifactExtraction.ts](src/application/ArtifactExtraction.ts)
- [src/application/ArtifactGraphConstruction.test.ts](src/application/ArtifactGraphConstruction.test.ts)
- [src/application/ArtifactGraphConstruction.ts](src/application/ArtifactGraphConstruction.ts)
- [src/application/ArtifactInventory.ts](src/application/ArtifactInventory.ts)
- [src/application/ArtifactInventory/scanReader.ts](src/application/ArtifactInventory/scanReader.ts)
- [src/application/ArtifactInventory/types.ts](src/application/ArtifactInventory/types.ts)
- [src/application/AuthorizedArtifactInventory.ts](src/application/AuthorizedArtifactInventory.ts)
- [src/artifacts/ArtifactProvider.ts](src/artifacts/ArtifactProvider.ts)
- [src/cli/artifactCommands.ts](src/cli/artifactCommands.ts)
- [src/contracts/artifactToolContracts.ts](src/contracts/artifactToolContracts.ts)
- [src/domain/artifactInspection.ts](src/domain/artifactInspection.ts)
- [src/server/registerArtifactTools.ts](src/server/registerArtifactTools.ts)
- [tests/boundary/filesystem/artifactDirectoryIdentity.test.ts](tests/boundary/filesystem/artifactDirectoryIdentity.test.ts)
- [tests/boundary/filesystem/artifactInventoryEntryOrder.test.ts](tests/boundary/filesystem/artifactInventoryEntryOrder.test.ts)
- [tests/boundary/filesystem/asarInventoryContainment.test.ts](tests/boundary/filesystem/asarInventoryContainment.test.ts)
- [tests/boundary/mcp/artifactEntryOrderMcp.test.ts](tests/boundary/mcp/artifactEntryOrderMcp.test.ts)
- [tests/boundary/providers/native/artifactProvider.extraction.test.ts](tests/boundary/providers/native/artifactProvider.extraction.test.ts)
- [tests/fixtures/artifactEntryOrder.ts](tests/fixtures/artifactEntryOrder.ts)

</details>



REA provides robust capabilities for inspecting, inventorying, and extracting contents from various package formats and directories. This includes specialized readers for common archive types, a system for constructing a content-addressed graph of artifacts, and mechanisms for safe extraction and integrity verification. The core idea is to represent the contents of an artifact as a graph of nodes and occurrences, allowing for detailed analysis and comparison.

This page offers a high-level overview of REA's artifact handling. For in-depth technical details on specific components, please refer to the linked child pages.

## Artifact Readers

REA implements specialized readers for various artifact formats, enabling efficient and reliable access to their contents. These readers handle the intricacies of each format, providing a unified interface for the artifact inventory system. This includes support for:

*   **Zip archives**: Handled by `ZipArtifactReader` [src/artifacts/ZipArtifactReader.ts]().
*   **ASAR archives**: Processed by `AsarArtifactReader` [src/artifacts/AsarArtifactReader.ts](), which also supports streaming entries.
*   **DMG images**: Managed by `NativeDmgArtifactReader` [src/artifacts/apple/NativeDmgArtifactReader.ts]().
*   **Directories**: Treated as artifacts by `DirectoryArtifactReader` [src/artifacts/DirectoryArtifactReader.ts]().

These readers are designed with considerations for backpressure, cancellation, and handling FIFO races to ensure robust operation.

For details, see [Artifact Readers](#5.1).

Sources:
- [src/artifacts/ArtifactProvider.ts:29]()
- [src/artifacts/AsarArtifactReader.ts]()
- [src/artifacts/DirectoryArtifactReader.ts]()
- [src/artifacts/ZipArtifactReader.ts]()
- [src/artifacts/apple/NativeDmgArtifactReader.ts]()

## Artifact Inventory and Graph Construction

The `ArtifactProvider` [src/artifacts/ArtifactProvider.ts:39-57]() is responsible for managing artifact-related operations. A key function is `inventoryArtifact` [src/application/ArtifactInventory.ts:24-33](), which scans a given input path and constructs a detailed `ArtifactInventoryResult` [src/domain/artifactGraph.ts]() representing the artifact's contents. This process involves:

1.  **Scanning and Classification**: The `scanArtifactInventory` [src/application/ArtifactInventory.ts:36-43]() function, which internally calls `scanCanonicalArtifactInventory` [src/application/ArtifactInventory/scanCanonical.js](), reads the artifact's entries. Each entry is classified by its `entry_kind` (e.g., "file", "directory", "slice") [src/application/ArtifactGraphConstruction.ts:18]().
2.  **Graph Construction**: The `scanReader` [src/application/ArtifactInventory/scanReader.ts:57-90]() function iterates through artifact entries, creating `MutableOccurrence` [src/application/ArtifactGraphConstruction.ts:13-26]() objects for each. These occurrences are then used to build a graph of `ArtifactNode` [src/domain/artifactGraph.ts]() and `ArtifactOccurrence` [src/domain/artifactGraph.ts]() objects, representing the content-addressed identity and logical paths within the artifact. Directories are materialized as nodes, and their identities are derived from their children, ensuring consistent comparison even with reordered or implicit directories [src/application/ArtifactGraphConstruction.ts:72-115]().
3.  **Authorized Inventory**: The `scanAuthorizedArtifactInventory` [src/application/AuthorizedArtifactInventory.ts:10-16]() function ensures that the input path is resolved and authorized before scanning, preventing unauthorized access.
4.  **Entry Ordering Determinism**: The inventory process ensures deterministic ordering of entries, which is crucial for consistent artifact comparisons [tests/boundary/mcp/artifactEntryOrderMcp.test.ts:18-67]().

### Artifact Graph Structure

The artifact graph consists of `ArtifactNode`s and `ArtifactOccurrence`s.

```mermaid
graph TD
    A[ArtifactInventoryResult] --> B{manifest};
    A --> C{nodes};
    A --> D{occurrences};
    A --> E{edges};

    D --> F[ArtifactOccurrence];
    C --> G[ArtifactNode];

    F -- "artifact_id" --> G;
    F -- "parent_occurrence_id" --> F;
    E -- "source_id" --> F;
    E -- "target_id" --> F;

    subgraph "Artifact Node (Content-Addressed Identity)"
        G -- "sha256" --> H[Content Hash];
        G -- "kind" --> I[e.g., "container", "executable", "file"];
        G -- "format" --> J[e.g., "zip", "asar", "mach-o"];
        G -- "size" --> K[Size in bytes];
    end

    subgraph "Artifact Occurrence (Logical Path)"
        F -- "occurrence_id" --> L[Unique ID];
        F -- "logical_path" --> M[Path within artifact];
        F -- "entry_kind" --> N[e.g., "file", "directory", "slice"];
        F -- "hash_status" --> O[e.g., "verified", "mismatched", "unavailable"];
    end
```
**Diagram: Artifact Inventory Result Structure**

Sources:
- [src/artifacts/ArtifactProvider.ts:39-57]()
- [src/application/ArtifactGraphConstruction.ts:13-26]()
- [src/application/ArtifactGraphConstruction.ts:72-115]()
- [src/application/ArtifactInventory.ts:24-33]()
- [src/application/ArtifactInventory.ts:36-43]()
- [src/application/ArtifactInventory/scanCanonical.js]()
- [src/application/ArtifactInventory/scanReader.ts:57-90]()
- [src/application/AuthorizedArtifactInventory.ts:10-16]()
- [src/domain/artifactGraph.ts]()
- [tests/boundary/mcp/artifactEntryOrderMcp.test.ts:18-67]()

## Artifact Extraction

REA provides a secure and controlled mechanism for extracting artifact contents. The `extractArtifact` function [src/application/ArtifactExtraction.ts:36-92]() is responsible for materializing selected regular files from an artifact into a fresh, exclusively owned temporary directory.

Key features of artifact extraction include:

*   **Safe Output**: Extraction occurs into a `SafeOutputTree` [src/artifacts/SafeOutputTree.ts](), which prevents traversal and symlink escapes, never overwrites existing files, and ensures proper cleanup.
*   **Integrity Verification**: During extraction, the integrity of the extracted files is verified against the artifact graph's content hashes.
*   **Cancellation and Backpressure**: The extraction process supports cancellation via `AbortSignal` and handles backpressure during stream operations.
*   **Tool Contract**: The `extract_artifact` tool contract [src/contracts/artifactToolContracts.ts:65-68]() defines the interface for this operation, ensuring consistent behavior across different contexts.

```mermaid
graph TD
    A[User Request] --> B(CLI Command: extract-artifact);
    B --> C(runProviderAnalysis);
    C --> D{ArtifactProvider.execute("extract_artifact")};
    D --> E(createArtifactExtractionDestination);
    E --> F(extractArtifact);
    F --> G(scanArtifactInventory);
    G --> H(createReader);
    H --> I(SafeOutputTree.create);
    I --> J{Iterate Artifact Entries};
    J -- "file/slice" --> K(reader.open);
    K --> L(output.write);
    L --> M(ExtractedOccurrence);
    J -- "directory" --> N(Skip);
    M --> O(createExtractionResult);
    O --> P[ArtifactExtractionResult];
    P -- "output_root" --> Q(Temporary Directory);
    P -- "extraction_manifest" --> R(Extraction Metadata);
    P -- "artifacts" --> S(List of Extracted Files);
    F -- "success" --> I_commit(output.commit);
    F -- "failure" --> I_rollback(output.rollback);
```
**Diagram: Artifact Extraction Workflow**

Sources:
- [src/application/ArtifactExtraction.ts:36-92]()
- [src/artifacts/SafeOutputTree.ts]()
- [src/contracts/artifactToolContracts.ts:65-68]()
- [src/cli/artifactCommands.ts:150-169]()
- [tests/boundary/providers/native/artifactProvider.extraction.test.ts:45-137]()

## Binary Target Resolution

REA's artifact handling also includes sophisticated binary target resolution, particularly for executable files within packages. This involves:

*   **`parseBinaryTarget`**: This function [src/domain/binaryTarget.ts]() is central to identifying and classifying binary files.
*   **App Bundle Resolution**: For macOS `.app` bundles, REA can identify the main executable and other relevant components.
*   **FAT Mach-O Slice Selection**: When dealing with universal (FAT) Mach-O binaries, REA can select the appropriate architecture slice for analysis.
*   **Header Parsing**: It parses ELF, PE, and Mach-O headers to extract crucial metadata about the binary.
*   **SHA-256 Hashing**: Content hashing (SHA-256) is used to uniquely identify binary targets and ensure integrity.
*   **Loader Arguments and Safety Checks**: The system also considers loader arguments and performs various safety checks to ensure that the identified binary target is suitable for analysis.

For details, see [Binary Target Resolution](#5.3).

Sources:
- [src/domain/binaryTarget.ts]()

---

