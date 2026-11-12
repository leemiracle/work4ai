<!-- source: DeepWiki mcp.deepwiki.com · repo x1xhlol/system-prompts-and-models-of-ai-tools · extra page Script Execution and Debugging System · fetched 2026-10-30 -->

# Script Execution and Debugging System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [v0 Prompts and Tools/Prompt.txt](v0 Prompts and Tools/Prompt.txt)

</details>



## Purpose and Scope

The Script Execution and Debugging System enables v0 to execute Python, Node.js, and SQL scripts directly within Code Projects through the `/scripts` folder structure. This system provides immediate code execution, database management, data processing capabilities, and real-time debugging feedback without requiring users to leave the v0 environment.

For information about v0's general Code Project architecture and file operations, see [Project Architecture and File Lifecycle](#4.1.1). For integration-specific database setup, see [Integration Ecosystem and Configuration](#4.1.6).

**Sources:** [v0 Prompts and Tools/Prompt.txt:175-253]()

---

## Script File Organization

### Required Directory Structure

All executable scripts in v0 MUST follow a strict organizational structure:

| Requirement | Description | Enforcement |
|-------------|-------------|-------------|
| Code Project Membership | Scripts MUST be part of a Code Project | System-enforced |
| Directory Location | Scripts MUST be added to `/scripts` folder | System-enforced |
| File Naming | No specific naming convention required | Flexible |
| Language Support | Python (`.py`), Node.js (`.js`, `.mjs`), SQL (`.sql`) | System-defined |

### Script Folder Architecture

```mermaid
graph TB
    CodeProject["Code Project Root"]
    ScriptsFolder["/scripts Folder"]
    PythonScripts["Python Scripts<br/>.py files"]
    NodeScripts["Node.js Scripts<br/>.js/.mjs files"]
    SQLScripts["SQL Scripts<br/>.sql files"]
    
    CodeProject --> ScriptsFolder
    ScriptsFolder --> PythonScripts
    ScriptsFolder --> NodeScripts
    ScriptsFolder --> SQLScripts
    
    PythonScripts --> PyExample1["data_processing.py"]
    PythonScripts --> PyExample2["image_analysis.py"]
    
    NodeScripts --> JSExample1["api_test.js"]
    NodeScripts --> JSExample2["data_transform.mjs"]
    
    SQLScripts --> SQLExample1["001_create_tables.sql"]
    SQLScripts --> SQLExample2["002_seed_data.sql"]
    SQLScripts --> SQLExample3["003_add_columns.sql"]
```

**Sources:** [v0 Prompts and Tools/Prompt.txt:175-182]()

---

## Language Capabilities Matrix

### Supported Languages and Features

```mermaid
graph LR
    subgraph Python["Python Execution"]
        PyLibs["NumPy, Matplotlib,<br/>Pillow, pandas"]
        PyOutput["print() for output"]
        PyStyle["Pure functions<br/>preferred"]
        PyAttach["Direct attachment<br/>reading"]
    end
    
    subgraph NodeJS["Node.js Execution"]
        JSModules["ES6+ syntax<br/>import only"]
        JSFetch["Built-in fetch API"]
        JSImage["sharp for images"]
        JSOutput["console.log() output"]
    end
    
    subgraph SQL["SQL Execution"]
        SQLCreate["Table creation"]
        SQLSeed["Data seeding"]
        SQLMigrate["Schema migrations"]
        SQLVersion["Version-based files"]
    end
    
    ScriptsFolder["/scripts Folder"] --> Python
    ScriptsFolder --> NodeJS
    ScriptsFolder --> SQL
```

| Language | Output Mechanism | Key Libraries | Module System | Special Requirements |
|----------|------------------|---------------|---------------|---------------------|
| Python | `print()` statements | NumPy, Matplotlib, Pillow | Standard imports | Read attachments directly, no copying |
| Node.js | `console.log()` statements | `sharp`, built-in `fetch` | ES6 `import` only, never `require` | ES6+ syntax mandatory |
| SQL | Execution results | N/A | N/A | Version-numbered files for modifications |

**Sources:** [v0 Prompts and Tools/Prompt.txt:185-213]()

---

## Python Script Execution

### Python Project Initialization with uv

v0 uses the `uv` tool for Python project management in the `/scripts` folder:

```mermaid
graph TD
    InitProject["uv init --bare<br/>&lt;path/to/project&gt;"]
    CreateToml["Creates pyproject.toml"]
    AddPackage["uv add &lt;package&gt;"]
    InstallDeps["Install dependencies<br/>(NumPy, Matplotlib, etc.)"]
    RunScript["uv run &lt;filename&gt;.py"]
    Execute["Execute Python script"]
    
    InitProject --> CreateToml
    CreateToml --> AddPackage
    AddPackage --> InstallDeps
    InstallDeps --> RunScript
    RunScript --> Execute
```

**Python Project Setup Workflow:**

1. **Initialize Project**: `uv init --bare <path/to/project>` creates a `pyproject.toml` file
2. **Add Packages**: `uv add <package>` installs libraries like NumPy, Matplotlib, Pillow
3. **Run Scripts**: `uv run <filename>.py` executes the Python script

### Python Best Practices and Requirements

```mermaid
graph TD
    PyScript["Python Script in /scripts"]
    
    subgraph Guidelines["Python Guidelines"]
        Libs["Use popular libraries:<br/>NumPy, Matplotlib, Pillow"]
        Output["Use print() for output<br/>(captured by execution env)"]
        Pure["Write pure function<br/>implementations"]
        Attach["Read directly from<br/>attachments, no copying"]
    end
    
    PyScript --> Libs
    PyScript --> Output
    PyScript --> Pure
    PyScript --> Attach
    
    Output --> Logs["Execution logs<br/>returned to v0"]
```

**Key Python Requirements:**

1. **Library Usage**: Utilize popular libraries like NumPy, Matplotlib, and Pillow for necessary tasks
2. **Output Capture**: The execution environment captures all `print()` statements as logs
3. **Functional Style**: Write pure function implementations when possible to minimize side effects
4. **Attachment Handling**: Don't copy attachments with data into the code project; read directly from the attachment

**Sources:** [v0 Prompts and Tools/Prompt.txt:49-56](), [v0 Prompts and Tools/Prompt.txt:187-193]()

---

## Node.js Script Execution

### Node.js Module System Requirements

v0 enforces strict ES6+ module conventions for all Node.js scripts:

```mermaid
graph TD
    NodeScript["Node.js Script in /scripts"]
    
    subgraph Mandatory["Mandatory Requirements"]
        ES6["ES6+ syntax ONLY"]
        Import["import statements<br/>NEVER require()"]
        Fetch["Built-in fetch for HTTP"]
        Sharp["sharp for image processing"]
    end
    
    subgraph Output["Output Handling"]
        ConsoleLog["console.log() statements"]
        Captured["Captured by execution env"]
    end
    
    NodeScript --> ES6
    NodeScript --> Import
    NodeScript --> Fetch
    NodeScript --> Sharp
    NodeScript --> ConsoleLog
    ConsoleLog --> Captured
    
    Import -.X.-> Require["require() - FORBIDDEN"]
    
    style Require fill:#f9f9f9,stroke:#666,stroke-width:2px,stroke-dasharray: 5 5
```

**Key Node.js Requirements:**

1. **ES6+ Syntax**: Always use modern JavaScript syntax
2. **Import-Only Module System**: Always use `import` statements; `require()` is strictly forbidden
3. **HTTP Requests**: Use the built-in `fetch` API for HTTP operations
4. **Image Processing**: Use `sharp` library for image manipulation tasks
5. **Output**: Utilize `console.log()` for all output (captured by execution environment)

**Sources:** [v0 Prompts and Tools/Prompt.txt:196-202]()

---

## SQL Script Execution and Versioning

### SQL Version Control Strategy

v0 implements a mandatory versioning system for SQL scripts to prevent destructive modifications:

```mermaid
graph TD
    InitialScript["001_create_tables.sql<br/>EXECUTED"]
    ModRequest["User requests modification<br/>to add new column"]
    
    Decision{"Can modify<br/>existing script?"}
    
    Forbidden["❌ FORBIDDEN<br/>Do NOT rewrite/delete<br/>001_create_tables.sql"]
    CreateNew["✓ CREATE NEW<br/>002_add_column.sql"]
    
    Execute["Execute new script"]
    NextMod["Future modification needed"]
    CreateAnother["✓ CREATE<br/>003_next_change.sql"]
    
    InitialScript --> ModRequest
    ModRequest --> Decision
    Decision -->|"Existing executed script"| Forbidden
    Decision -->|"Correct approach"| CreateNew
    CreateNew --> Execute
    Execute --> NextMod
    NextMod --> CreateAnother
```

### SQL Script Organization Rules

| Rule | Description | Rationale |
|------|-------------|-----------|
| Table Existence Check | MUST verify tables exist before updating data | Prevents runtime errors |
| File Splitting | Split SQL scripts into multiple files for organization | Better version control and clarity |
| No Rewrites | Don't rewrite or delete existing executed SQL scripts | Preserves execution history |
| Version-Based Naming | Use numbered prefixes (001_, 002_, etc.) for sequential execution | Clear ordering and dependency management |
| Additive-Only | Only add new scripts if modification needed | Immutable execution history |

### SQL Execution Workflow

```mermaid
sequenceDiagram
    participant User
    participant v0
    participant ScriptsFolder as "/scripts Folder"
    participant Integration as "Database Integration<br/>(Supabase/Neon)"
    
    User->>v0: "Create database tables"
    v0->>ScriptsFolder: Write 001_create_tables.sql
    v0->>Integration: Execute SQL script
    Integration-->>v0: Execution results
    v0-->>User: Tables created
    
    User->>v0: "Add new column to table"
    v0->>ScriptsFolder: Write 002_add_column.sql<br/>(NOT modify 001_)
    v0->>Integration: Execute SQL script
    Integration-->>v0: Execution results
    v0-->>User: Column added
```

**Sources:** [v0 Prompts and Tools/Prompt.txt:205-210](), [v0 Prompts and Tools/Prompt.txt:557-562]()

---

## Debugging System with console.log

### Debug Logging Convention

v0 implements a specialized debugging system using the `console.log("[v0] ...")` prefix convention. Debug logs are captured by the execution environment and returned in `<v0_app_debug_logs>` tags:

```mermaid
graph TD
    Issue["Debugging Issue or<br/>Solving Problem"]
    
    AddLogs["Add console.log('[v0] ...')<br/>statements in code"]
    
    Execute["Execute code in<br/>v0 environment"]
    
    Capture["Logs captured by<br/>execution environment"]
    
    Return["Logs returned in<br/>&lt;v0_app_debug_logs&gt;"]
    
    Analyze["v0 analyzes logs to<br/>understand issue"]
    
    Decision{"Issue<br/>resolved?"}
    
    RemoveLogs["Remove debug statements"]
    NextIteration["Add more targeted<br/>debug statements"]
    
    Issue --> AddLogs
    AddLogs --> Execute
    Execute --> Capture
    Capture --> Return
    Return --> Analyze
    Analyze --> Decision
    Decision -->|"Yes"| RemoveLogs
    Decision -->|"No"| NextIteration
    NextIteration --> Execute
```

### Debug Statement Format and Code Examples

All debugging statements MUST follow the `console.log("[v0] ...")` format for proper log identification. The execution environment captures these logs and returns them in `<v0_app_debug_logs>` tags for analysis:

| Purpose | Example Statement | When to Use |
|---------|-------------------|-------------|
| Data Inspection | `console.log("[v0] User data received:", userData)` | When receiving external data |
| API Tracing | `console.log("[v0] API call starting with params:", params)` | Before API calls |
| Component Rendering | `console.log("[v0] Component rendered with props:", props)` | During render cycles |
| Error Context | `console.log("[v0] Error occurred in function:", error.message)` | When catching errors |
| State Changes | `console.log("[v0] State updated:", newState)` | After state mutations |

### Debug Output Channel Mapping

```mermaid
graph LR
    CodeFile["Code File with<br/>console.log('[v0] ...')"]
    ExecEnv["Execution Environment"]
    LogCapture["Log Capture System"]
    XMLTags["&lt;v0_app_debug_logs&gt;<br/>XML Tags"]
    v0Analysis["v0 AI Analysis"]
    
    CodeFile --> ExecEnv
    ExecEnv --> LogCapture
    LogCapture --> XMLTags
    XMLTags --> v0Analysis
```

### Debug Logging Best Practices

```mermaid
graph LR
    subgraph BestPractices["Debugging Best Practices"]
        Context["Include relevant context<br/>in debug messages"]
        Both["Log both successful<br/>operations AND errors"]
        Values["Include variable values<br/>and object states"]
        Clear["Use clear, descriptive<br/>messages"]
    end
    
    subgraph Workflow["Debug Workflow"]
        Add["Add [v0] debug logs"]
        Receive["Receive logs in<br/>&lt;v0_app_debug_logs&gt;"]
        Solve["Solve the problem"]
        Remove["Remove debug statements<br/>when resolved"]
    end
    
    BestPractices --> Workflow
```

**Debug Lifecycle Rules:**

1. **Add During Problem-Solving**: Insert debug statements when investigating issues or solving problems
2. **Receive Feedback**: Logs are returned in `<v0_app_debug_logs>` tags for analysis
3. **Trace Execution Flow**: Use debug statements to understand control flow and variable states
4. **Clean Up**: Remove debug statements once the issue is resolved or user has moved on from the topic

**Sources:** [v0 Prompts and Tools/Prompt.txt:35-53](), [v0 Prompts and Tools/Prompt.txt:228-253]()

---

## Preview Environment and Hot Module Replacement

### Automatic Development Server Detection

v0's preview environment automatically detects and displays applications with Hot Module Replacement (HMR):

```mermaid
graph TD
    DevServer["Development Server<br/>(any framework)"]
    OpenPort["Open Port Detection"]
    Preview["Preview Environment"]
    HMR["Hot Module Replacement"]
    FileChange["File Changes"]
    ImmediateReflection["Immediate Reflection<br/>(no full page reload)"]
    
    DevServer --> OpenPort
    OpenPort --> Preview
    Preview --> HMR
    FileChange --> HMR
    HMR --> ImmediateReflection
```

**Preview Environment Features:**

| Feature | Description | Supported Frameworks |
|---------|-------------|---------------------|
| Automatic Port Detection | Preview detects open port from dev server | All frameworks |
| Hot Module Replacement | File changes reflect immediately | Next.js, Vite, etc. |
| No Reload Required | Updates without full page reload | Framework-dependent |
| Framework Agnostic | Works with any framework | Universal |

**Workflow:**

1. **Run Dev Server**: Start any framework's development server (Next.js, Vite, etc.)
2. **Automatic Detection**: Preview automatically picks up the open port
3. **Live Updates**: File changes reflect immediately via HMR
4. **No User Action Required**: Preview updates without manual refresh

**Sources:** [v0 Prompts and Tools/Prompt.txt:271-276]()

---

## Integration with Storage Systems

### Database Script Execution

SQL scripts in the `/scripts` folder integrate directly with v0's storage integrations without requiring external tools:

```mermaid
graph TD
    UserRequest["User: 'Set up database tables'"]
    
    v0Generate["v0 generates SQL script<br/>in /scripts folder"]
    
    Integration["GetOrRequestIntegration<br/>checks database connection"]
    
    subgraph StorageOptions["Storage Integrations"]
        Supabase["Supabase"]
        Neon["Neon"]
        Upstash["Upstash"]
        VercelBlob["Vercel Blob"]
    end
    
    Execute["v0 executes script directly<br/>(no external tools needed)"]
    
    Results["Execution results<br/>returned to user"]
    
    UserRequest --> v0Generate
    v0Generate --> Integration
    Integration --> StorageOptions
    StorageOptions --> Execute
    Execute --> Results
```

**Key Integration Points:**

1. **No ORM Required**: v0 NEVER uses an ORM to connect to SQL databases (Supabase, Neon) unless explicitly asked
2. **Direct Execution**: Users do NOT need to leave v0 to run scripts; v0 executes them directly
3. **Version Control**: Instead of editing existing scripts, v0 creates new files with version numbers
4. **Automatic Environment Variables**: Storage integrations automatically provide necessary connection credentials

**Sources:** [v0 Prompts and Tools/Prompt.txt:557-562]()

---

## Use Cases and Applications

### Supported Script Execution Scenarios

v0's script execution system supports the following use cases:

```mermaid
graph TB
    ScriptSystem["/scripts Execution System"]
    
    subgraph DatabaseOps["Database Operations"]
        Create["Creating and<br/>seeding databases"]
        Migrate["Performing database<br/>migrations"]
    end
    
    subgraph DataOps["Data Operations"]
        Process["Data processing<br/>and analysis"]
        Transform["Data transformation<br/>pipelines"]
    end
    
    subgraph Development["Development Tasks"]
        Demo["Interactive algorithm<br/>demonstrations"]
        Functions["Individual functions<br/>outside web apps"]
        Execute["Tasks requiring<br/>immediate execution"]
    end
    
    ScriptSystem --> DatabaseOps
    ScriptSystem --> DataOps
    ScriptSystem --> Development
```

| Use Case Category | Specific Applications | Typical Language |
|-------------------|----------------------|-----------------|
| Database Management | Table creation, data seeding, schema migrations | SQL |
| Data Processing | CSV/JSON parsing, data cleaning, statistical analysis | Python |
| Data Analysis | Visualization generation, algorithm demonstrations | Python (NumPy, Matplotlib) |
| Image Processing | Image manipulation, format conversion | Python (Pillow) or Node.js (sharp) |
| API Testing | HTTP request testing, response validation | Node.js (fetch) |
| Function Development | Individual utility functions, standalone logic | Python or Node.js |
| Immediate Execution | Any task requiring code execution and output | Any supported language |

**Sources:** [v0 Prompts and Tools/Prompt.txt:218-226]()

---

## Script Execution Requirements Summary

### Mandatory Requirements Across All Languages

```mermaid
graph TD
    Requirement1["MUST be part of<br/>Code Project"]
    Requirement2["MUST be in<br/>/scripts folder"]
    Requirement3["MUST use valid<br/>language-specific syntax"]
    Requirement4["Output captured via<br/>print() or console.log()"]
    
    Python["Python Scripts"] --> Requirement1
    NodeJS["Node.js Scripts"] --> Requirement1
    SQL["SQL Scripts"] --> Requirement1
    
    Requirement1 --> Requirement2
    Requirement2 --> Requirement3
    Requirement3 --> Requirement4
    
    subgraph Forbidden["Forbidden Patterns"]
        ForbidRequire["Node.js: require()"]
        ForbidSQLRewrite["SQL: Rewriting executed scripts"]
        ForbidCopyAttach["Python: Copying attachments<br/>into project"]
    end
```

**Universal Requirements:**

| Requirement | All Languages | Enforcement Level |
|-------------|--------------|-------------------|
| Code Project Membership | ✓ Required | System-enforced |
| `/scripts` Directory | ✓ Required | System-enforced |
| Valid Best Practices | ✓ Required | v0-enforced |
| Output Capture | ✓ Required | Environment-handled |

**Language-Specific Prohibitions:**

- **Python**: Do NOT copy attachment data into the project
- **Node.js**: Do NOT use `require()` statements (use `import` only)
- **SQL**: Do NOT rewrite or delete executed scripts (create new versioned files)

**Sources:** [v0 Prompts and Tools/Prompt.txt:175-213]()

---

