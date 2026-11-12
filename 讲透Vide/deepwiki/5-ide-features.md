<!-- source: DeepWiki mcp.deepwiki.com · repo pascal-lab/vide · page 5 IDE Features · fetched 2026-10-12 -->

# IDE Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [crates/ide/src/analysis.rs](crates/ide/src/analysis.rs)
- [crates/ide/src/definitions.rs](crates/ide/src/definitions.rs)
- [crates/ide/src/document_symbols.rs](crates/ide/src/document_symbols.rs)
- [crates/ide/src/lib.rs](crates/ide/src/lib.rs)
- [crates/ide/src/navigation_target.rs](crates/ide/src/navigation_target.rs)
- [crates/ide/src/verilog_2005.rs](crates/ide/src/verilog_2005.rs)
- [src/config/caps.rs](src/config/caps.rs)
- [src/config/user_config.rs](src/config/user_config.rs)
- [src/global_state/handlers/request.rs](src/global_state/handlers/request.rs)
- [src/lsp_ext/ext.rs](src/lsp_ext/ext.rs)
- [src/lsp_ext/to_proto.rs](src/lsp_ext/to_proto.rs)

</details>



The `ide` crate provides the high-level intelligence layer for SystemVerilog support in Vide. It abstracts the complexities of the [HIR (High-level Intermediate Representation)](#4) and [Incremental Database (Salsa / RootDb)](#2.2) into a consumer-friendly `Analysis` API [crates/ide/src/analysis.rs:57-58]().

This layer is responsible for transforming raw semantic data into editor-facing features such as completions, diagnostics, and navigation targets.

### The Analysis API

The primary entry point for all IDE features is the `AnalysisSnapshot` (aliased as `Analysis`) [crates/ide/src/analysis.rs:51-58](). It provides a thread-safe snapshot of the `RootDb` and handles cancellation via `Cancellable<T>` [crates/ide/src/lib.rs:10-12](). Most methods take a `FileId` or `FilePosition` [crates/ide/src/lib.rs:8]() and return structured data that is later translated to LSP types in the `lsp_server` crate [src/lsp_ext/to_proto.rs:48-52]().

#### Data Flow: From Code to IDE Intelligence

The following diagram illustrates how a user action (like hovering over a module instance) flows through the system to return an IDE feature response.

**IDE Feature Resolution Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        "UserHover"["User hovers over 'u_child'"]
    end

    subgraph "Code Entity Space"
        "LSP"["LSP RequestHandler"]
        "Analysis"["ide::Analysis::hover"]
        "Sema"["hir::semantics::Semantics"]
        "DefClass"["ide::definitions::DefinitionClass::resolve"]
        "Markup"["ide::markup::Markup"]
    end

    "UserHover" --> "LSP"
    "LSP" -- "FilePosition" --> "Analysis"
    "Analysis" --> "Sema"
    "Sema" -- "SyntaxToken" --> "DefClass"
    "DefClass" -- "ModuleId/InstanceId" --> "Markup"
    "Markup" -- "Markdown/PlainText" --> "LSP"
```
Sources: [crates/ide/src/analysis.rs:223-228](), [crates/ide/src/definitions.rs:39-44](), [src/global_state/handlers/request.rs:22-26]().

### Supported Features

Vide supports a wide array of SystemVerilog-specific IDE features, categorized below.

#### [Diagnostics](#5.1)
Diagnostics are aggregated from multiple sources: `SlangParse` (syntax errors), `SlangSemantic` (compiler-level semantic checks), and `Vide` (IDE-specific lints like ambiguous module instantiations) [src/lsp_ext/to_proto.rs:146-153](). They are filtered and configured via `DiagnosticSelector` and `DiagnosticsConfig` [src/config/user_config.rs:3-6]().

#### [Completion Engine](#5.2)
The completion system uses a `CompletionContext` to detect if the caret is in a port list, expression, or directive [crates/ide/src/analysis.rs:25-28](). It provides snippets for complex structures like `module` or `generate` blocks, and handles trigger characters like `.` or `` ` `` [crates/ide/src/analysis.rs:211-216]().

#### [Navigation: Go-to-Definition, References, and Rename](#5.3)
Vide implements cross-file navigation using `NavTarget` [crates/ide/src/navigation_target.rs:34-44](). It supports `goto_definition`, `goto_declaration` [crates/ide/src/analysis.rs:160-172](), and a robust `rename` engine that handles SystemVerilog-specific syntax like `PortConnShorthand` transformation [crates/ide/src/definitions.rs:29-31]().

#### [Hover, Inlay Hints, and Semantic Tokens](#5.4)
*   **Hover**: Renders signatures and documentation for symbols, supporting both Markdown and PlainText formats [crates/ide/src/analysis.rs:223-228]().
*   **Inlay Hints**: Displays parameter names and port names inline, controlled by `InlayHintConfig` [crates/ide/src/analysis.rs:229-234]().
*   **Semantic Tokens**: Provides high-fidelity syntax highlighting, distinguishing between clock/reset ports and standard nets via custom token types like `port_clock` and `port_reset` [src/lsp_ext/ext.rs:75-77]().

#### [Code Actions and Signature Help](#5.5)
Code actions provide "Quick Fixes" such as adding missing port connections or converting ordered connections to named ones [crates/ide/src/analysis.rs:23-24](). `SignatureHelp` provides real-time guidance during module instantiation and function calls [crates/ide/src/analysis.rs:260-265]().

#### [Document Symbols, Folding, and Formatting](#5.6)
*   **Document Symbols**: Generates a hierarchical outline of the file (modules, tasks, generate blocks) using a `SymbolCollecter` [crates/ide/src/document_symbols.rs:56-70]().
*   **Folding**: Provides folding ranges for blocks, specify sections, and regions [crates/ide/src/analysis.rs:191-193]().
*   **Formatting**: Integrates with the `Verible` formatter for document, range, and on-type formatting [crates/ide/src/analysis.rs:200-210]().

### Symbol Classification
The IDE layer classifies syntax into `SymbolKind` to drive consistent icons and behavior across features [crates/ide/src/lib.rs:51-74]().

**Symbol Mapping: Syntax to IDE Kind**
```mermaid
graph LR
    subgraph "Syntax Space"
        "ast::ModuleDeclaration"
        "ast::UdpDeclaration"
        "ast::HierarchicalInstance"
        "ast::FunctionDeclaration"
    end

    subgraph "IDE SymbolKind"
        "Module"["SymbolKind::Module"]
        "Primitive"["SymbolKind::Primitive"]
        "Instance"["SymbolKind::Instance"]
        "Fn"["SymbolKind::Fn"]
    end

    "ast::ModuleDeclaration" --> "Module"
    "ast::UdpDeclaration" --> "Primitive"
    "ast::HierarchicalInstance" --> "Instance"
    "ast::FunctionDeclaration" --> "Fn"
```
Sources: [crates/ide/src/lib.rs:77-102](), [crates/ide/src/navigation_target.rs:34-44]().

---

### Child Pages
*   [Diagnostics](#5.1) — Diagnostic sources and filtering.
*   [Completion Engine](#5.2) — Two-phase completion and snippet building.
*   [Navigation: Go-to-Definition, References, and Rename](#5.3) — Symbol resolution and refactoring.
*   [Hover, Inlay Hints, and Semantic Tokens](#5.4) — Rich text rendering and inline metadata.
*   [Code Actions and Signature Help](#5.5) — Quick fixes and parameter guidance.
*   [Document Symbols, Folding, and Formatting](#5.6) — Structural analysis and code styling.

Sources: [crates/ide/src/lib.rs:12-49](), [crates/ide/src/analysis.rs:59-157](), [src/lsp_ext/to_proto.rs:1-34]().

---

