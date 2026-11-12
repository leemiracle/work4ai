<!-- source: DeepWiki mcp.deepwiki.com · repo kreuzberg-dev/kreuzberg · page 11 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/reference/api-c.md](docs/reference/api-c.md)
- [docs/reference/api-csharp.md](docs/reference/api-csharp.md)
- [docs/reference/api-elixir.md](docs/reference/api-elixir.md)
- [docs/reference/api-go.md](docs/reference/api-go.md)
- [docs/reference/api-java.md](docs/reference/api-java.md)
- [docs/reference/api-php.md](docs/reference/api-php.md)
- [docs/reference/api-python.md](docs/reference/api-python.md)
- [docs/reference/api-r.md](docs/reference/api-r.md)
- [docs/reference/api-ruby.md](docs/reference/api-ruby.md)
- [docs/reference/api-rust.md](docs/reference/api-rust.md)
- [docs/reference/api-typescript.md](docs/reference/api-typescript.md)
- [docs/reference/api-wasm.md](docs/reference/api-wasm.md)
- [docs/reference/configuration.md](docs/reference/configuration.md)
- [docs/reference/errors.md](docs/reference/errors.md)
- [docs/reference/types.md](docs/reference/types.md)

</details>



Quick-lookup reference documentation for Kreuzberg constants, error codes, environment variables, CLI commands, and cross-language FFI bindings. This page provides tables and diagrams for rapid reference during development.

**Child Pages:**

- **[Configuration Reference](#11.1)**: Complete `ExtractionConfig`, `OcrConfig`, `PdfConfig`, `ChunkingConfig`, and `HierarchyConfig` field documentation.
- **[Supported Document Formats](#11.2)**: Full list of 75+ formats with extraction methods and capabilities.
- **[Feature Flags Reference](#11.3)**: Complete Cargo feature documentation including `pdf`, `ocr`, `embeddings`, `full`, `server`, `cli`, and platform-specific features.
- **[Error Codes and Types](#11.4)**: Comprehensive error classification, error code enumeration, and language-specific exception mapping.
- **[Environment Variables Reference](#11.5)**: Complete list of `KREUZBERG_*` environment variables for configuration, API server tuning, file size limits, and OCR model paths.

**Related Documentation:**

- [API Reference (Python, TypeScript, Java, Go, etc.)](4) - Language-specific API documentation.
- [Concepts](3) - System architecture and pipeline design.
- [Guides](6) - Configuration tutorials and advanced usage patterns.

**Current Version:** 5.0.0-rc.3

**Sources:** [docs/reference/api-csharp.md:5](), [docs/reference/api-go.md:5](), [docs/reference/api-java.md:5](), [docs/reference/api-python.md:5]()

## Quick Reference Tables

This section provides fast lookups for common development tasks. For detailed configuration documentation, see [Configuration Reference](#11.1).

### Package Distribution Matrix

**Package Distribution by Language Ecosystem**

```mermaid
graph LR
    subgraph PyPI["PyPI Registry"]
        PythonPkg["kreuzberg<br/>Python wheels<br/>maturin build"]
    end
    
    subgraph NPM["npm Registry"]
        NodePkg["@kreuzberg/node<br/>NAPI bindings<br/>napi-rs"]
        WasmPkg["@kreuzberg/wasm<br/>wasm-bindgen<br/>wasm-pack"]
    end
    
    subgraph RubyGems["RubyGems.org"]
        RubyPkg["kreuzberg<br/>rb_sys + Magnus"]
    end
    
    subgraph MavenCentral["Maven Central"]
        JavaPkg["dev.kreuzberg:kreuzberg<br/>Panama FFM API"]
    end
    
    subgraph NuGet["NuGet Gallery"]
        CSharpPkg["Kreuzberg<br/>P/Invoke + DllImport"]
    end
    
    subgraph CratesIO["crates.io"]
        RustCore["kreuzberg<br/>Core library"]
        RustCLI["kreuzberg-cli<br/>Binary"]
        RustFFI["kreuzberg-ffi<br/>C ABI"]
    end
    
    subgraph Composer["Packagist"]
        PHPPkg["kreuzberg/kreuzberg<br/>ext-ffi"]
    end
    
    subgraph HexPM["Hex.pm"]
        ElixirPkg["kreuzberg<br/>Rustler NIFs"]
    end
    
    subgraph GoPkg["go.pkg.dev"]
        GoPkgEntity["github.com/.../go/v5<br/>CGo bindings"]
    end
    
    subgraph CRAN["CRAN/r-universe"]
        RPkg["kreuzberg<br/>extendr"]
    end
    
    RustCore --> PythonPkg
    RustCore --> NodePkg
    RustCore --> WasmPkg
    RustFFI --> RubyPkg
    RustFFI --> JavaPkg
    RustFFI --> CSharpPkg
    RustFFI --> PHPPkg
    RustFFI --> GoPkgEntity
    RustCore --> ElixirPkg
    RustCore --> RPkg
```

**Installation Commands by Ecosystem**

| Language | Package Manager | Installation Command | Package Identifier |
|----------|----------------|---------------------|-------------------|
| **Python** | pip / uv | `pip install kreuzberg` | `kreuzberg` |
| **Node.js** | pnpm / npm | `pnpm add @kreuzberg/node` | `@kreuzberg/node` |
| **WASM** | pnpm / npm | `pnpm add @kreuzberg/wasm` | `@kreuzberg/wasm` |
| **Ruby** | gem / bundler | `gem install kreuzberg` | `kreuzberg` |
| **Go** | go get | `go get github.com/kreuzberg-dev/kreuzberg/v5` | `github.com/kreuzberg-dev/kreuzberg/v5` |
| **Java** | maven | See [packages/java/README.md:83-87]() | `dev.kreuzberg:kreuzberg` |
| **C#** | dotnet | `dotnet add package Kreuzberg` | `Kreuzberg` |
| **PHP** | composer | `composer require kreuzberg/kreuzberg` | `kreuzberg/kreuzberg` |

**Sources:** [docs/reference/api-python.md:5](), [docs/reference/api-typescript.md:5](), [docs/reference/api-go.md:5](), [docs/reference/api-java.md:5](), [docs/reference/api-csharp.md:5](), [docs/reference/api-php.md:5]()

### MIME Type Detection and API Entry Points

**MIME Detection Flow**

```mermaid
flowchart TD
    Input["Input: file path or bytes"]
    
    MagicBytes["detect_mime_type_from_bytes()<br/>Magic byte detection"]
    FileExt["Extension-based fallback"]
    Default["application/octet-stream"]
    
    CheckMagic{"Magic bytes<br/>detected?"}
    
    OfficeCheck{"Office format?<br/>inspect_zip_contents"}
    OfficeAnalysis["OOXML structure analysis<br/>DOCX/XLSX/PPTX"]
    
    Result["MIME type string"]
    
    Input --> MagicBytes
    MagicBytes --> CheckMagic
    CheckMagic -->|Yes| OfficeCheck
    CheckMagic -->|No| FileExt
    
    OfficeCheck -->|Yes| OfficeAnalysis
    OfficeCheck -->|No| Result
    OfficeAnalysis --> Result
    
    FileExt --> Result
    Default --> Result
```

**Core Extraction API Functions:**

| Language | Async Function | Sync Wrapper | Return Type |
|----------|----------------|--------------|-------------|
| **Rust** | `extract_file()` | `extract_file_sync()` | `Result<ExtractionResult, Error>` |
| **Python** | `extract_file()` | `extract_file_sync()` | `ExtractionResult` |
| **TypeScript** | `extractFile()` | `extractFileSync()` | `Promise<ExtractionResult>` |
| **Java** | `extractFile()` | `extractFileSync()` | `ExtractionResult` |
| **Go** | `ExtractFile()` | `ExtractFileSync()` | `(ExtractionResult, error)` |
| **C#** | `ExtractFileAsync()` | `ExtractFileSync()` | `Task<ExtractionResult>` |

**Sources:** [docs/reference/api-rust.md:49-107](), [docs/reference/api-python.md:49-107](), [docs/reference/api-typescript.md:49-107](), [docs/reference/api-java.md:49-107](), [docs/reference/api-go.md:49-107](), [docs/reference/api-csharp.md:49-107](), [docs/reference/api-elixir.md:155-188]()

## Environment Variables

**Configuration and Runtime Control**

| Variable | Type | Purpose | Default |
|----------|------|---------|---------|
| `KREUZBERG_CONFIG_PATH` | Path | Override config file discovery | Auto-discover |
| `KREUZBERG_CACHE_DIR` | Path | Set extraction cache directory | System temp |
| `TESSDATA_PREFIX` | Path | Path to Tesseract traineddata | System path |

**Sources:** [docs/reference/configuration.md:79-99](), [docs/reference/api-rust.md:53-61]()

### FFI Layer Architecture

**kreuzberg-ffi: C ABI Bridge for Multi-Language Bindings**

```mermaid
flowchart LR
    subgraph FFIBindings["FFI-Based Bindings"]
        Java["Java<br/>dev.kreuzberg:kreuzberg<br/>Panama FFM API"]
        Go["Go<br/>github.com/.../go/v5<br/>CGo"]
        CSharp["C#<br/>Kreuzberg (NuGet)<br/>P/Invoke"]
        PHP["PHP<br/>kreuzberg/kreuzberg<br/>ext-ffi"]
    end
    
    subgraph DirectBindings["Direct Rust Integration"]
        Python["Python<br/>kreuzberg (PyPI)<br/>PyO3"]
        Node["Node.js<br/>@kreuzberg/node<br/>NAPI-RS"]
        Elixir["Elixir<br/>kreuzberg<br/>Rustler NIFs"]
    end
    
    subgraph FFICrate["crates/kreuzberg-ffi"]
        ExtractFile["extract_file"]
        ExtractBytes["extract_bytes"]
        BatchExtract["batch_extract_files"]
    end
    
    subgraph CoreCrate["crates/kreuzberg"]
        ExtractAPI["extraction::extract_file<br/>extraction::extract_bytes"]
    end
    
    Java --> ExtractFile
    Go --> ExtractFile
    CSharp --> ExtractFile
    PHP --> ExtractFile
    
    Python --> ExtractAPI
    Node --> ExtractAPI
    Elixir --> ExtractAPI
    
    ExtractFile --> ExtractAPI
    ExtractBytes --> ExtractAPI
    BatchExtract --> ExtractAPI
```

**FFI Entry Point Reference**

| Language | Main File Entry Point | Main Bytes Entry Point | Source |
|----------|-----------------------|------------------------|--------|
| **C#** | `ExtractFileAsync` | `ExtractBytesAsync` | [docs/reference/api-csharp.md:33-74]() |
| **Go** | `ExtractFile` | `ExtractBytes` | [docs/reference/api-go.md:33-74]() |
| **Java** | `extractFile` | `extractBytes` | [docs/reference/api-java.md:33-74]() |
| **PHP** | `extractFile` | `extractBytes` | [docs/reference/api-php.md:33-74]() |
| **Ruby** | `extract_file` | `extract_bytes` | [docs/reference/api-ruby.md:33-74]() |

**Sources:** [docs/reference/api-csharp.md:33-74](), [docs/reference/api-go.md:33-74](), [docs/reference/api-java.md:33-74](), [docs/reference/api-php.md:33-74](), [docs/reference/api-ruby.md:33-74]()

## Next Steps

- **[Configuration Reference](#11.1)**: Complete list of all configuration options with types and defaults.
- **[Supported Document Formats](#11.2)**: Comprehensive format capabilities table.
- **[Feature Flags Reference](#11.3)**: Cargo features and build-time configuration.
- **[Error Codes and Types](#11.4)**: Error classification and cross-language exception mapping.
- **[Environment Variables Reference](#11.5)**: Complete list of `KREUZBERG_*` variables.

**Sources:** [docs/reference/configuration.md:5-80](), [docs/reference/types.md:22-53]()

---

