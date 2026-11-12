<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-language-server · page 6 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/termux_language_server/linter.py](src/termux_language_server/linter.py)
- [src/termux_language_server/searcher/pacman.py](src/termux_language_server/searcher/pacman.py)
- [src/termux_language_server/server.py](src/termux_language_server/server.py)

</details>



## Purpose and Scope
This page defines the core domain terms, protocols, libraries, file formats, and Python classes utilized across `termux-language-server`. It serves as a comprehensive reference linking high-level concepts to their concrete implementations and code pointers within the repository.

---

## Language Server Protocol and Parsing Foundations

### LSP (Language Server Protocol)
An open, JSON-RPC-based protocol standardized by Microsoft that defines the communication between a source code editor (the client) and a language analysis process (the server). It decouples language features like diagnostics, code completion, and hover documentation from specific editors.

Sources: [README.md:1-91]()

### tree-sitter
An incremental parsing library that builds a concrete syntax tree for source files and efficiently updates the tree as the file changes. In this project, tree-sitter parses shell scripts and package configuration formats using the Bash grammar.

Sources: [src/termux_language_server/server.py:13-24]()

### lsp-tree-sitter
The underlying Python framework package that bridges `tree-sitter` parse trees with LSP capabilities. It provides abstract base classes such as `TreeSitterLanguageServer`, `LinterBase`, `PackageSearcher`, `ValueCompleter`, and `PackageCompleter`.

Sources: [src/termux_language_server/server.py:9-12]()

### .scm Query
Tree-sitter query files written in Scheme-like syntax (`.scm`) located in the queries module. They define pattern matches against the syntax tree to extract variable bindings, declarations, and package dependencies (such as `@package.PKGBUILD` and `@package._ebuild`).

Sources: [src/termux_language_server/server.py:16-38]()

---

## Server Classes and Components

### SchemaLinter
A linter class provided by `lsp-tree-sitter` and instantiated in `TermuxLanguageServer` using tree-sitter queries and a schema getter function to validate configuration variables against JSON schemas.

```mermaid
graph TD
    A["TermuxLanguageServer"] -->|passes queries and schema_getter| B["SchemaLinter"]
    B -->|parses via| C["tree-sitter"]
    B -->|validates against| D["JSON Schemas"]

    subcode ["Code Entity Space"]
    style subcode fill:none,stroke:none
```
Sources: [src/termux_language_server/server.py:33-35]()

### PackageLinter
A linter class responsible for checking package dependencies and metadata fields against registered package searchers.

```mermaid
graph TD
    A["TermuxLanguageServer"] -->|passes queries and searcher_getter| B["PackageLinter"]
    B -->|queries package index via| C["PackageSearcher"]

    subcode ["Code Entity Space"]
    style subcode fill:none,stroke:none
```
Sources: [src/termux_language_server/server.py:36-38]()

### NamcapLinter
A custom linter implemented in `src/termux_language_server/linter.py` that delegates PKGBUILD analysis to Arch Linux's `Namcap` package validation library.

```mermaid
graph TD
    A["TermuxLanguageServer"] -->|conditionally adds| B["NamcapLinter"]
    B -->|loads PKGBUILD via| C["Namcap.package.load_from_pkgbuild"]
    B -->|executes rules via| D["Namcap.rules.all_rules"]
    B -->|extracts diagnostics| E["DiagnosticSeverity"]

    subcode ["Code Entity Space"]
    style subcode fill:none,stroke:none
```
Sources: [src/termux_language_server/linter.py:27-47](), [src/termux_language_server/server.py:53-57]()

### ValueCompleter
A completer component initialized with a jq filter file (`value.jq`) and a schema getter that provides value suggestions based on JSON schemas.

Sources: [src/termux_language_server/server.py:39-42]()

### PackageCompleter
A completer component that uses `searcher_getter` to provide package name completions inside dependency arrays.

Sources: [src/termux_language_server/server.py:44]()

### PackageSearcher
An abstract base class implemented in `lsp-tree-sitter` and subclassed by ecosystem-specific searchers to handle package lookup, version resolution, and URL generation.

```mermaid
graph TD
    A["PackageSearcher"] -->|subclassed by| B["PacmanSearcher"]
    A -->|subclassed by| C["PortageSearcher"]
    B -->|queries local db via| D["pyalpm.DB"]
    B -->|queries aur via| E["marisa_trie.Trie"]
    C -->|queries via| F["Portage"]

    subcode ["Code Entity Space"]
    style subcode fill:none,stroke:none
```
Sources: [src/termux_language_server/server.py:11](), [src/termux_language_server/searcher/pacman.py:34-49](), [src/termux_language_server/server.py:74-76]()

---

## Ecosystem File Formats and Variables

| Term | Description / Target Ecosystem | Code Pointer / Asset |
| :--- | :--- | :--- |
| **PKGBUILD** | Arch Linux package build script describing metadata and packaging steps. | `src/termux_language_server/server.py:72` |
| **ebuild** | Gentoo package build script containing metadata and build phases. | `src/termux_language_server/server.py:76` |
| **eclass** | Gentoo shared build function library included by ebuilds. | [README.md:50]() |
| **build.sh** | Termux package build script for cross-compiling Android packages. | [README.md:42]() |
| **subpackage.sh** | Termux script defining secondary/split package properties (`*.subpackage.sh`). | [README.md:43]() |
| **TERMUX_PKG_\*** | Namespace prefix for all package configuration variables in Termux build scripts. | [README.md:39-43]() |
| **makepkg.conf** | Arch Linux build configuration file defining compiler flags and build options. | [README.md:47]() |
| **make.conf** | Gentoo global configuration file for Portage build options and USE flags. | [README.md:51]() |
| **color.map** | Gentoo configuration file mapping console output colors for Portage. | [README.md:52]() |
| **devscripts.conf** | Debian/Ubuntu package maintainer utility configuration (`.devscripts`). | [README.md:54]() |
| **.mdd** | Zsh module definition description file used in the zsh source tree. | [README.md:56]() |

Sources: [README.md:39-56](), [src/termux_language_server/server.py:67-77]()

---

## External Libraries, Databases, and Infrastructure

### pyalpm
A Python binding for libalpm (Arch Linux package manager library) utilized by `PacmanSearcher` to query local package databases and verify installed dependencies.

Sources: [README.md:63](), [src/termux_language_server/searcher/pacman.py:13]()

### portage
Gentoo's package management system and Python API used by `PortageSearcher` to lookup ebuild metadata and dependencies.

Sources: [README.md:64](), [src/termux_language_server/server.py:74-76]()

### namcap
Arch Linux package analysis utility used by `NamcapLinter` to inspect PKGBUILDs and built packages for common errors, styling issues, and policy violations.

Sources: [README.md:67](), [src/termux_language_server/linter.py:17-20]()

### marisa-trie
A memory-efficient Trie implementation in Python/C++ used to cache and search the Arch User Repository (AUR) package list in `PacmanSearcher`.

Sources: [src/termux_language_server/searcher/pacman.py:11](), [src/termux_language_server/searcher/pacman.py:24-30]()

### AUR
Arch User Repository — a community-driven repository for Arch Linux users, integrated into package search and completion via `marisa-trie`.

Sources: [src/termux_language_server/searcher/pacman.py:24-30]()

### NUR
NixOS User Repository — community-maintained package repository ecosystem referenced in CI/CD deployment pipelines.

Sources: [README.md:4]()

### uv
An extremely fast Python package installer and resolver written in Rust, configured as the build backend in `pyproject.toml`.

Sources: [README.md:1-38]()

### jq Value Filter
A jq expression script (`value.jq`) located in assets that extracts candidate completion values from JSON schema definitions.

Sources: [src/termux_language_server/server.py:39-42]()