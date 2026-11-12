<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/hf-hub · page 7 Development Environment · fetched 2026-10-26 -->

# Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/rust.yml](.github/workflows/rust.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [flake.lock](flake.lock)
- [flake.nix](flake.nix)

</details>



This document covers the setup and tooling required for contributors and advanced users working with the hf-hub codebase. It provides guidance on establishing a development environment, understanding the quality assurance processes, and navigating the multi-platform testing infrastructure.

For specific details about Nix development shell usage, see [Nix Development Shell](#7.1). For comprehensive information about the testing pipeline and code quality processes, see [CI/CD and Code Quality](#7.2).

## Development Setup Options

The hf-hub project provides multiple approaches for setting up a development environment, accommodating different developer preferences and system configurations.

### Nix Development Shell

The project includes a Nix flake configuration that provides a reproducible development environment across different platforms. The `flake.nix` defines a development shell with all necessary dependencies pre-configured.

**Development Environment Components**
```mermaid
graph TB
    FlakeNix["flake.nix"] --> DevShell["mkShell"]
    DevShell --> Rustup["rustup<br/>Rust Toolchain Manager"]
    DevShell --> PkgConfig["pkg-config<br/>Library Discovery"]
    DevShell --> OpenSSL["openssl<br/>Cryptographic Libraries"]
    
    Rustup --> StableToolchain["stable toolchain"]
    Rustup --> Rustfmt["rustfmt<br/>Code Formatter"]
    Rustup --> Clippy["clippy<br/>Linter"]
    
    PkgConfig --> SystemLibs["System Library Linking"]
    OpenSSL --> TLSSupport["TLS Backend Support"]
    
    subgraph "Supported Platforms"
        AArch64Linux["aarch64-linux"]
        X8664Linux["x86_64-linux"] 
        AArch64Darwin["aarch64-darwin"]
    end
    
    DevShell --> AArch64Linux
    DevShell --> X8664Linux
    DevShell --> AArch64Darwin
```

Sources: [flake.nix:1-33]()

### Manual Development Setup

For developers who prefer not to use Nix, the core dependencies can be installed manually:

| Component | Purpose | Installation Method |
|-----------|---------|-------------------|
| `rustup` | Rust toolchain management | https://rustup.rs/ |
| `pkg-config` | System library discovery | System package manager |
| `openssl` | Cryptographic library | System package manager |
| `cargo-audit` | Security vulnerability scanning | `cargo install cargo-audit` |

## Core Dependencies and System Requirements

The development environment requires several system-level dependencies that support the various feature combinations and TLS backends.

**System Dependencies**
```mermaid
graph TD
    SystemDeps["System Dependencies"] --> PkgConfig["pkg-config"]
    SystemDeps --> OpenSSLDev["openssl-dev"]
    SystemDeps --> CompilerToolchain["C/C++ Compiler"]
    
    PkgConfig --> LibraryLinking["Dynamic Library Linking"]
    OpenSSLDev --> NativeTLSBackend["native-tls Backend"]
    CompilerToolchain --> NativeDependencies["Native Code Compilation"]
    
    subgraph "Rust Toolchain Components"
        RustStable["stable toolchain"]
        RustFmt["rustfmt component"] 
        ClippyComponent["clippy component"]
    end
    
    LibraryLinking --> RustStable
    NativeTLSBackend --> RustStable
    NativeDependencies --> RustStable
    
    RustStable --> RustFmt
    RustStable --> ClippyComponent
```

Sources: [flake.nix:23-27](), [.github/workflows/rust.yml:19-24]()

## Development Workflow and Quality Assurance

The project maintains code quality through automated tooling and comprehensive testing across multiple feature combinations and platforms.

### Pre-commit Hooks

The `.pre-commit-config.yaml` configures automatic code quality checks that run before each commit:

| Hook | Purpose | Configuration |
|------|---------|---------------|
| `fmt` | Code formatting via `rustfmt` | Enforces consistent style |
| `clippy` | Static analysis and linting | Runs with `-Dwarnings` for strict checking |

**Quality Assurance Pipeline**
```mermaid
graph LR
    Developer["Developer"] --> PreCommit["pre-commit hooks"]
    PreCommit --> FmtCheck["rustfmt check"]
    PreCommit --> ClippyCheck["clippy --tests --examples -- -Dwarnings"]
    
    FmtCheck --> CommitAllowed{"Commit Allowed?"}
    ClippyCheck --> CommitAllowed
    
    CommitAllowed -->|Yes| GitCommit["git commit"]
    CommitAllowed -->|No| FixIssues["Fix formatting/lint issues"]
    FixIssues --> PreCommit
    
    GitCommit --> CIPipeline["CI Pipeline Trigger"]
```

Sources: [.pre-commit-config.yaml:1-16]()

### Multi-Platform Testing Strategy

The CI pipeline validates the codebase across multiple operating systems and feature combinations to ensure broad compatibility.

**CI Testing Matrix**
```mermaid
graph TB  
    CIPipeline["rust.yml CI Pipeline"] --> MatrixStrategy["Matrix Strategy"]
    
    MatrixStrategy --> Ubuntu["ubuntu-latest"]
    MatrixStrategy --> Windows["windows-latest"] 
    MatrixStrategy --> MacOS["macOS-latest"]
    
    subgraph "Test Phases"
        BuildPhase["cargo build --all-targets"]
        LintPhase["cargo clippy --all-features"]
        TestAllFeatures["cargo test --all-features"]
        TestNoSSL["cargo test --no-default-features"]
        TestFeatureCross["Feature combination testing"]
        AuditPhase["cargo audit -D warnings"]
    end
    
    Ubuntu --> BuildPhase
    Windows --> BuildPhase
    MacOS --> BuildPhase
    
    BuildPhase --> LintPhase
    LintPhase --> TestAllFeatures
    TestAllFeatures --> TestNoSSL
    TestNoSSL --> TestFeatureCross
    TestFeatureCross --> AuditPhase
    
    subgraph "Feature Combinations Tested"
        UreqNative["ureq + native-tls"]
        UreqRustls["ureq + rustls-tls"]
        TokioNative["tokio + native-tls"] 
        TokioRustls["tokio + rustls-tls"]
    end
    
    TestFeatureCross --> UreqNative
    TestFeatureCross --> UreqRustls
    TestFeatureCross --> TokioNative
    TestFeatureCross --> TokioRustls
```

Sources: [.github/workflows/rust.yml:1-52]()

## Testing and Feature Validation

The development environment emphasizes comprehensive testing across the library's feature matrix. The CI pipeline validates four critical feature combinations:

- **Synchronous + Native TLS**: `ureq` with `native-tls` backend
- **Synchronous + Pure Rust TLS**: `ureq` with `rustls-tls` backend  
- **Asynchronous + Native TLS**: `tokio` with `native-tls` backend
- **Asynchronous + Pure Rust TLS**: `tokio` with `rustls-tls` backend

This ensures that all supported HTTP client and TLS backend combinations function correctly across different operating systems.

### Security and Dependency Management

The development workflow includes automated security scanning through `cargo-audit`, which checks for known vulnerabilities in the dependency tree. This tool is installed during CI and run with `-D warnings` to treat any security advisories as build failures.

Sources: [.github/workflows/rust.yml:28-29](), [.github/workflows/rust.yml:50-51](), [.github/workflows/rust.yml:44-48]()

---

