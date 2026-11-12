<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Tokenizer · page 6 Development and Contributing · fetched 2026-10-26 -->

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Tokenizer_C#/.editorconfig](Tokenizer_C#/.editorconfig)
- [Tokenizer_C#/Tokenizer/Properties/launchSettings.json](Tokenizer_C#/Tokenizer/Properties/launchSettings.json)
- [Tokenizer_C#/TokenizerLib/Utils/Properties/launchSettings.json](Tokenizer_C#/TokenizerLib/Utils/Properties/launchSettings.json)

</details>



This document provides comprehensive guidance for developers who want to contribute to the Microsoft Tokenizer repository. It covers development environment setup, build processes, testing procedures, coding standards, and contribution workflows for both the TypeScript and C# implementations.

For detailed information about the automated CI/CD pipelines, see [CI/CD Pipelines](#6.1).

## Development Environment Setup

The Microsoft Tokenizer repository supports dual-language development with both TypeScript and C# implementations. Each implementation has its own development requirements and workflows.

### Prerequisites

**For TypeScript Development:**
- Node.js ≥18.0.0
- npm package manager
- Development environment in `tokenizer_ts/` directory

**For C# Development:**
- .NET SDK supporting .NET Standard 2.0
- Development environment in `Tokenizer_C#/` directory
- Visual Studio or compatible IDE (optional)

### Repository Structure

```mermaid
graph TB
    subgraph "Repository Root"
        CONTRIB["CONTRIBUTING.md"]
        GITIGNORE[".gitignore"]
        GITATTR[".gitattributes"]
    end
    
    subgraph "TypeScript Implementation"
        TS_DIR["tokenizer_ts/"]
        TS_PKG["package.json"]
        TS_SRC["src/"]
        TS_DIST["dist/"]
        TS_TEST["test/"]
    end
    
    subgraph "C# Implementation"
        CS_DIR["Tokenizer_C#/"]
        CS_SLN["Tokenizer.sln"]
        CS_LIB["TokenizerLib/"]
        CS_CONSOLE["Tokenizer/"]
        CS_TEST["UnitTests/"]
        EDITOR_CONFIG[".editorconfig"]
    end
    
    CONTRIB --> TS_DIR
    CONTRIB --> CS_DIR
    GITIGNORE --> TS_DIST
    GITIGNORE --> CS_LIB
    
    TS_DIR --> TS_PKG
    TS_DIR --> TS_SRC
    TS_DIR --> TS_TEST
    
    CS_DIR --> CS_SLN
    CS_DIR --> CS_LIB
    CS_DIR --> CS_CONSOLE
    CS_DIR --> EDITOR_CONFIG
```

**Development Environment Architecture**

Sources: [CONTRIBUTING.md:1-77](), [.gitignore:1-358](), [.gitattributes:1-6]()

## Building the Projects

### TypeScript Build Process

The TypeScript implementation uses npm for package management and build automation:

```bash
cd tokenizer_ts
npm install
npm run build
npm pack
```

The build process compiles TypeScript source code and generates distribution files in the `dist/` directory.

### C# Build Process

The C# implementation uses the .NET CLI and MSBuild:

```bash
cd Tokenizer_C#
dotnet build Tokenizer.sln
```

This builds all projects in the solution including the main library, console application, and unit tests.

```mermaid
graph LR
    subgraph "TypeScript Build Flow"
        TS_INSTALL["npm install"]
        TS_BUILD["npm run build"]
        TS_PACK["npm pack"]
        TS_INSTALL --> TS_BUILD
        TS_BUILD --> TS_PACK
    end
    
    subgraph "C# Build Flow"
        CS_RESTORE["dotnet restore"]
        CS_BUILD["dotnet build"]
        CS_RESTORE --> CS_BUILD
    end
    
    subgraph "Build Outputs"
        TS_DIST["dist/ directory"]
        TS_TGZ["*.tgz package"]
        CS_BIN["bin/ directories"]
        CS_OBJ["obj/ directories"]
    end
    
    TS_BUILD --> TS_DIST
    TS_PACK --> TS_TGZ
    CS_BUILD --> CS_BIN
    CS_BUILD --> CS_OBJ
```

**Build Process Flow**

Sources: [CONTRIBUTING.md:10-26]()

## Testing

### TypeScript Testing

Execute the TypeScript test suite using npm:

```bash
cd tokenizer_ts
npm run test
```

### C# Testing

Run the C# unit tests using the .NET CLI:

```bash
cd Tokenizer_C#
dotnet test
```

The C# implementation includes comprehensive unit tests that validate tokenization functionality across different models and scenarios.

| Implementation | Test Command | Test Directory | Test Framework |
|---|---|---|---|
| TypeScript | `npm run test` | `tokenizer_ts/test/` | npm test runner |
| C# | `dotnet test` | `Tokenizer_C#/UnitTests/` | MSTest/xUnit |

Sources: [CONTRIBUTING.md:28-44]()

## Coding Standards and Style

### C# Coding Conventions

The project adheres to Microsoft's C# Coding Conventions as specified in the `.editorconfig` file. Key standards include:

- **Indentation**: 4 spaces, no tabs
- **Line endings**: CRLF (`\r\n`)
- **Modifier order**: `public`, `private`, `protected`, `internal`, `static`, `extern`, `new`, `virtual`, `abstract`, `sealed`, `override`, `readonly`, `unsafe`, `volatile`, `async`
- **Braces**: Always use braces for code blocks
- **Naming**: Use PascalCase for public members, camelCase for private fields

### TypeScript Style Guidelines

For TypeScript development, use the provided formatting and linting tools:

```bash
cd tokenizer_ts
npm run format
npm run eslint
```

These commands ensure consistent code formatting and adherence to project-specific linting rules.

```mermaid
graph TB
    subgraph "C# Style Enforcement"
        EDITOR_CONFIG[".editorconfig"]
        CS_CONVENTIONS["Microsoft C# Conventions"]
        EDITOR_CONFIG --> CS_CONVENTIONS
    end
    
    subgraph "TypeScript Style Enforcement"
        NPM_FORMAT["npm run format"]
        NPM_ESLINT["npm run eslint"]
        TS_RULES["Project ESLint Rules"]
        NPM_FORMAT --> TS_RULES
        NPM_ESLINT --> TS_RULES
    end
    
    subgraph "Style Standards"
        INDENTATION["4-space indentation"]
        BRACES["Consistent brace placement"]
        NAMING["PascalCase/camelCase naming"]
        LINE_ENDINGS["CRLF line endings"]
    end
    
    CS_CONVENTIONS --> INDENTATION
    CS_CONVENTIONS --> BRACES
    CS_CONVENTIONS --> NAMING
    CS_CONVENTIONS --> LINE_ENDINGS
    
    TS_RULES --> INDENTATION
    TS_RULES --> BRACES
    TS_RULES --> NAMING
```

**Coding Standards Architecture**

Sources: [CONTRIBUTING.md:46-59](), [Tokenizer_C#/.editorconfig:1-149]()

## Contributing Workflow

### Development Process

1. **Fork and Branch**: Create a fork of the repository and create a feature branch
2. **Development**: Implement changes following coding standards
3. **Testing**: Run appropriate test suites for your changes
4. **Pull Request**: Submit a pull request with clear description

### Pull Request Requirements

Before submitting a pull request, ensure:

- All tests pass for relevant implementations
- Code follows established style guidelines
- Build process completes successfully
- Changes are well-documented

### Development Configuration

The repository includes launch settings for debugging:

| Configuration File | Purpose | Location |
|---|---|---|
| `launchSettings.json` | Console app debugging | `Tokenizer_C#/Tokenizer/Properties/` |
| `launchSettings.json` | Utils debugging | `Tokenizer_C#/TokenizerLib/Utils/Properties/` |

These configurations set up default command-line arguments for debugging scenarios.

Sources: [CONTRIBUTING.md:4-6](), [Tokenizer_C#/Tokenizer/Properties/launchSettings.json:1-8](), [Tokenizer_C#/TokenizerLib/Utils/Properties/launchSettings.json:1-8]()

## Issue Reporting

For bug reports, feature requests, or other issues, use the GitHub Issues system:

1. **Search Existing Issues**: Check if the issue has already been reported
2. **Create New Issue**: Provide detailed description including:
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Environment details (OS, .NET version, Node.js version)
   - Code samples when applicable

3. **Use Appropriate Labels**: Apply relevant labels to categorize the issue

Sources: [CONTRIBUTING.md:61-63]()

## Contributor License Agreement

### Microsoft CLA Requirement

All contributions require agreement to a Contributor License Agreement (CLA). The process is automated:

1. **First-time Contributors**: CLA bot will prompt you to sign the agreement
2. **Automated Verification**: The bot checks CLA status on each pull request
3. **One-time Process**: CLA signature applies across all Microsoft repositories

### Code of Conduct

The project follows the Microsoft Open Source Code of Conduct. Contributors are expected to:

- Be respectful and inclusive
- Focus on constructive feedback
- Report inappropriate behavior to `opencode@microsoft.com`

```mermaid
graph TB
    subgraph "Contribution Process"
        FORK["Fork Repository"]
        BRANCH["Create Feature Branch"]
        DEVELOP["Implement Changes"]
        TEST["Run Tests"]
        PR["Submit Pull Request"]
        
        FORK --> BRANCH
        BRANCH --> DEVELOP
        DEVELOP --> TEST
        TEST --> PR
    end
    
    subgraph "Automated Checks"
        CLA_BOT["CLA Bot Verification"]
        BUILD_CHECK["Build Validation"]
        TEST_CHECK["Test Execution"]
        
        PR --> CLA_BOT
        PR --> BUILD_CHECK
        PR --> TEST_CHECK
    end
    
    subgraph "Requirements"
        CLA_SIGNED["CLA Signed"]
        TESTS_PASS["Tests Pass"]
        BUILD_SUCCESS["Build Success"]
        CODE_STANDARDS["Code Standards Met"]
        
        CLA_BOT --> CLA_SIGNED
        BUILD_CHECK --> BUILD_SUCCESS
        TEST_CHECK --> TESTS_PASS
        DEVELOP --> CODE_STANDARDS
    end
```

**Contribution Workflow**

Sources: [CONTRIBUTING.md:65-76]()

---

