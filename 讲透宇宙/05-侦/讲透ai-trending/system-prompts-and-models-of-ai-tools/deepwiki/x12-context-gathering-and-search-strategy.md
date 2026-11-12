<!-- source: DeepWiki mcp.deepwiki.com · repo x1xhlol/system-prompts-and-models-of-ai-tools · extra page Context Gathering and Search Strategy · fetched 2026-10-30 -->

# Context Gathering and Search Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [v0 Prompts and Tools/Prompt.txt](v0 Prompts and Tools/Prompt.txt)

</details>



## Purpose and Scope

This document details v0's context gathering and search strategy for exploring codebases before making changes. It covers the four primary context tools (`Glob`, `Grep`, `Read`, `Search`), the mandatory "gather context first" philosophy, parallel tool execution optimization, and systematic search patterns for understanding project structure and dependencies.

For information about file editing operations after context gathering, see [File Editing and Tool Schema](). For overall v0 architecture and CodeProject structure, see [v0 by Vercel Development Platform]().

Sources: [v0 Prompts and Tools/Prompt.txt:480-531]()

---

## Four Context Tools Overview

v0 provides four specialized tools for codebase exploration, each optimized for different discovery patterns:

| Tool | Primary Use Case | Speed | Scope |
|------|-----------------|-------|-------|
| `Grep` | Pattern/term search across entire codebase | Fast | All files |
| `Glob` | Directory/file listing for structure discovery | Fastest | File system |
| `Read` | Read specific file contents | Medium | Single file |
| `Search` | Comprehensive exploration and analysis | Slowest | All files + deep analysis |

Sources: [v0 Prompts and Tools/Tools.json:10-13, 18-21, 26-29, 34-37]()

---

## Tool Architecture and Invocation

```mermaid
graph TB
    subgraph UserRequest["User Request"]
        Request["User asks for code change"]
    end
    
    subgraph ContextPhase["Context Gathering Phase MANDATORY"]
        Glob["Glob<br/>List files/directories<br/>Understand structure"]
        Grep["Grep<br/>Search for patterns<br/>Find specific terms"]
        Read["Read<br/>Read identified files<br/>Understand implementation"]
        Search["Search<br/>Comprehensive search<br/>Last resort fallback"]
    end
    
    subgraph EditPhase["Edit Phase"]
        WriteFile["Write/Edit files<br/>Apply changes"]
    end
    
    Request --> Glob
    Request --> Grep
    Glob --> Read
    Grep --> Read
    Read --> Search
    Search --> Read
    
    Read --> WriteFile
    Search --> WriteFile
    
    Glob -.->|"Parallel execution"| Grep
    Grep -.->|"Multiple parallel"| Read
```

Sources: [v0 Prompts and Tools/Prompt.txt:480-531]()

---

## Grep: Pattern-Based Search

`Grep` performs fast pattern matching across the entire codebase using search terms, patterns, or code snippets.

**Primary Use Cases:**
- Finding specific function/class names
- Locating API endpoints or route handlers
- Searching for import statements
- Finding usage of specific libraries or patterns

**Example Queries:**
```typescript
// Finding authentication patterns
Grep("AuthContext")
Grep("useAuth")
Grep("signInWithPassword")

// Finding API routes
Grep("api/")
Grep("route.ts")
```

Sources: [v0 Prompts and Tools/Tools.json:18-21]()

---

## Glob: File System Discovery

`Glob` lists files and directories to understand project structure and locate relevant files without reading contents.

**Primary Use Cases:**
- Discovering project organization
- Finding related files by name patterns
- Locating component directories
- Understanding folder hierarchy

**Example Workflow:**
```typescript
// 1. List root to understand structure
Glob("/")

// 2. Drill into specific directories
Glob("/app")
Glob("/components")

// 3. Find files matching patterns
Glob("/components/auth")
```

Sources: [v0 Prompts and Tools/Tools.json:10-13]()

---

## Read: Content Retrieval

`Read` reads specific files or code sections once identified through `Glob` or `Grep`.

**Mandatory Usage Pattern:**
- **ALWAYS** read files before editing them [v0 Prompts and Tools/Prompt.txt:96-98]()
- Reading prevents overwriting important code
- Enables understanding of existing implementation patterns

**Example Pattern:**
```typescript
// 1. Find the file
Glob("/app")

// 2. Read before editing
Read("/app/page.tsx")

// 3. Only then write changes
Write("/app/page.tsx", changes)
```

Sources: [v0 Prompts and Tools/Tools.json:26-29, v0 Prompts and Tools/Prompt.txt:96-98]()

---

## Search: Comprehensive Exploration

`Search` performs comprehensive search and exploration of the codebase, used as a **last resort fallback** when other tools are insufficient.

**When to Use:**
- Initial codebase overview ("Give me an overview of the codebase")
- Complex multi-file relationships
- When `Grep` and `Glob` don't provide enough context
- Understanding broad architectural patterns

**Invocation Pattern:**
```typescript
// Get codebase overview
Search("Give me an overview of the codebase")

// Understand specific system
Search("How is authentication implemented?")

// Find design patterns
Search("Show me the component structure")
```

Sources: [v0 Prompts and Tools/Tools.json:34-37, v0 Prompts and Tools/Prompt.txt:967-971]()

---

## "Don't Stop at the First Match" Philosophy

v0 enforces thorough exploration of search results to ensure correct understanding and implementation.

```mermaid
graph LR
    subgraph AntiPattern["❌ Anti-Pattern"]
        FirstMatch["Find first match"]
        AssumeCorrect["Assume it's correct"]
        MakeChanges["Make changes"]
    end
    
    subgraph BestPractice["✅ Best Practice"]
        MultipleMatches["Find multiple matches"]
        ExamineAll["Examine ALL results"]
        VerifyContext["Verify context/variants"]
        CheckRelated["Check parent/related"]
        ThenEdit["Make informed changes"]
    end
    
    FirstMatch --> AssumeCorrect
    AssumeCorrect --> MakeChanges
    
    MultipleMatches --> ExamineAll
    ExamineAll --> VerifyContext
    VerifyContext --> CheckRelated
    CheckRelated --> ThenEdit
```

**Key Principles from [v0 Prompts and Tools/Prompt.txt:490-495]():**

| Principle | Action Required |
|-----------|----------------|
| **Multiple files found** | Examine ALL of them, not just first |
| **Component found** | Check if correct variant/version |
| **Pattern found** | Look for similar patterns elsewhere |
| **Parent relationships** | Check parent components, wrappers, global styles |

Sources: [v0 Prompts and Tools/Prompt.txt:490-495]()

---

## Systematic Search Strategy: "Understand the Full System"

Before making changes, v0 must understand the complete system context by following domain-specific search patterns.

### Domain-Specific Search Patterns

```mermaid
graph TB
    subgraph LayoutIssues["Layout Issues"]
        CheckParents["Check parents<br/>wrappers<br/>global styles"]
    end
    
    subgraph AddingFeatures["Adding Features"]
        FindSimilar["Find existing<br/>similar implementations<br/>Follow patterns"]
    end
    
    subgraph StateChanges["State Changes"]
        TraceState["Trace where state<br/>actually lives and flows"]
    end
    
    subgraph APIWork["API Work"]
        UnderstandPatterns["Understand existing<br/>patterns and<br/>error handling"]
    end
    
    subgraph Styling["Styling"]
        CheckTheme["Check theme systems<br/>utility classes<br/>component variants"]
    end
    
    subgraph NewDeps["New Dependencies"]
        CheckExisting["Check existing imports<br/>utilities may<br/>already exist"]
    end
    
    subgraph TypesValidation["Types/Validation"]
        FindSchemas["Look for existing<br/>schemas, interfaces<br/>validation patterns"]
    end
    
    subgraph Testing["Testing"]
        UnderstandSetup["Understand test setup<br/>and patterns before<br/>writing tests"]
    end
    
    subgraph Routing["Routing/Navigation"]
        CheckRoutes["Check existing<br/>route structure and<br/>navigation patterns"]
    end
```

**Detailed Search Requirements:**

**Layout Issues** [v0 Prompts and Tools/Prompt.txt:499]()
- Check parent components first
- Check wrappers
- Check global styles (app/globals.css)

**Adding Features** [v0 Prompts and Tools/Prompt.txt:500]()
- Find existing similar implementations
- Follow established patterns

**State Changes** [v0 Prompts and Tools/Prompt.txt:501]()
- Trace where state actually lives
- Understand state flow between components

**API Work** [v0 Prompts and Tools/Prompt.txt:502]()
- Understand existing API patterns
- Check error handling conventions

**Styling** [v0 Prompts and Tools/Prompt.txt:503]()
- Check theme systems (globals.css)
- Check utility classes
- Check component variants

**New Dependencies** [v0 Prompts and Tools/Prompt.txt:504]()
- Check existing imports
- Verify utilities don't already exist
- Avoid duplicate implementations

**Types/Validation** [v0 Prompts and Tools/Prompt.txt:505]()
- Look for existing schemas
- Find interface definitions
- Check validation patterns

**Testing** [v0 Prompts and Tools/Prompt.txt:506]()
- Understand test setup
- Follow existing test patterns

**Routing/Navigation** [v0 Prompts and Tools/Prompt.txt:507]()
- Check existing route structure
- Understand navigation patterns

Sources: [v0 Prompts and Tools/Prompt.txt:497-508]()

---

## Pre-Change Verification Checklist

Before making any code changes, v0 must answer these questions [v0 Prompts and Tools/Prompt.txt:521-526]():

```mermaid
graph TB
    PreChange["Before Making Changes"]
    
    Q1["Is this the right file<br/>among multiple options?"]
    Q2["Does a parent/wrapper<br/>already handle this?"]
    Q3["Are there existing utilities<br/>or patterns to use?"]
    Q4["How does this fit into<br/>broader architecture?"]
    
    PreChange --> Q1
    PreChange --> Q2
    PreChange --> Q3
    PreChange --> Q4
    
    Q1 --> Verified["All Verified"]
    Q2 --> Verified
    Q3 --> Verified
    Q4 --> Verified
    
    Verified --> ProceedWithChanges["Proceed with Changes"]
```

Sources: [v0 Prompts and Tools/Prompt.txt:521-526]()

---

## Parallel Tool Call Optimization

v0 prioritizes parallel tool execution to maximize speed (3-5x faster for independent operations).

### Parallel Execution Rules

**Rule 1: Independent Operations = Parallel Execution**

```typescript
// ✅ CORRECT: Parallel execution for independent reads
Read("/app/page.tsx")     // Call 1
Read("/components/nav.tsx") // Call 2
Read("/lib/utils.ts")      // Call 3
// All three execute simultaneously
```

**Rule 2: Dependent Operations = Sequential Execution**

```typescript
// ✅ CORRECT: Sequential when results inform next step
Glob("/components")           // Call 1: Find files
// Wait for result...
Read("/components/auth.tsx") // Call 2: Use result from Call 1
```

**Rule 3: Never Use Placeholders**

```typescript
// ❌ WRONG: Guessing parameters
Read("placeholder.tsx") // Called in parallel with guess

// ✅ CORRECT: Wait for actual file path
Glob("/components")
// Get actual filename
Read("/components/actual-file.tsx")
```

Sources: [v0 Prompts and Tools/Prompt.txt:510-519]()

### Parallel vs Sequential Decision Tree

```mermaid
graph TB
    Decision["Tool calls needed"]
    
    CheckDep{"Are tool calls<br/>independent?"}
    
    Decision --> CheckDep
    
    CheckDep -->|"Yes:<br/>No shared parameters<br/>No dependencies"| Parallel["Execute in PARALLEL<br/>3-5x faster"]
    
    CheckDep -->|"No:<br/>Need results from previous<br/>Parameters depend on results"| Sequential["Execute SEQUENTIALLY<br/>Wait for each result"]
    
    Parallel --> Example1["Example:<br/>Read 3 different files<br/>All at once"]
    
    Sequential --> Example2["Example:<br/>1. Glob to find files<br/>2. Wait for results<br/>3. Read on found files"]
```

Sources: [v0 Prompts and Tools/Prompt.txt:510-519]()

---

## Search Methodology: Broad → Specific → Verify

v0 follows a systematic search pattern: **broad → specific → verify relationships** [v0 Prompts and Tools/Prompt.txt:529]().

### Phase 1: Broad Discovery
```typescript
// Start with high-level structure
Search("Give me an overview of the codebase")
Glob("/")
Glob("/app")
Glob("/components")
```

### Phase 2: Specific Targeting
```typescript
// Narrow down to relevant areas
Grep("AuthContext")
Grep("signInWithPassword")
Glob("/components/auth")
```

### Phase 3: Verify Relationships
```typescript
// Read and understand connections
Read("/components/auth/login-form.tsx")
Read("/components/auth/auth-provider.tsx")
Read("/app/api/auth/route.ts")
Grep("import.*AuthProvider") // Find all usages
```

Sources: [v0 Prompts and Tools/Prompt.txt:529]()

---

## Real-World Search Examples

### Example 1: Updating Form Styles

From alignment examples [v0 Prompts and Tools/Prompt.txt:993-1008]():

```mermaid
sequenceDiagram
    participant User
    participant v0
    participant Glob
    participant Read
    
    User->>v0: "Update sign in form to match login form styles"
    
    Note over v0: Thought: Need to understand both forms first
    
    v0->>Glob: Find files related to "sign in" and "login"
    Glob-->>v0: Returns file paths
    
    Note over v0: Found both forms, now read them
    
    par Parallel Reads
        v0->>Read: Read sign-in-form.tsx
        v0->>Read: Read login-form.tsx
    end
    
    Read-->>v0: Both file contents
    
    Note over v0: Analyzed style differences
    
    v0->>User: "Updating sign in form styles to match login"
```

Sources: [v0 Prompts and Tools/Prompt.txt:993-1008]()

### Example 2: Adding Like Functionality

From alignment examples [v0 Prompts and Tools/Prompt.txt:1067-1087]():

```mermaid
sequenceDiagram
    participant User
    participant v0
    participant GetOrRequestIntegration
    participant Search
    participant Read
    
    User->>v0: "Add likes to my social media app"
    
    Note over v0: First: Check database schema
    
    v0->>GetOrRequestIntegration: Examine database structure
    GetOrRequestIntegration-->>v0: Returns schema (users, posts tables)
    
    Note over v0: Need likes table - will create migration
    Note over v0: Now find post components
    
    v0->>Search: Find post components and API routes
    Search-->>v0: Located relevant files
    
    par Read Multiple Components
        v0->>Read: Read post-card.tsx
        v0->>Read: Read api/posts/route.ts
        v0->>Read: Read post-actions.tsx
    end
    
    Read-->>v0: All component implementations
    
    Note over v0: Now understand full system - ready to add likes
```

Sources: [v0 Prompts and Tools/Prompt.txt:1067-1087]()

### Example 3: Refactoring Authentication

From alignment examples [v0 Prompts and Tools/Prompt.txt:1027-1044]():

```mermaid
graph TB
    Request["Refactor auth to use<br/>new useAuth hook"]
    
    Search["Search:<br/>Find AuthContext usage<br/>across codebase"]
    
    Analysis["Found: 15+ components<br/>in multiple directories<br/>Complex refactoring needed"]
    
    TodoList["Create systematic plan:<br/>1. Update Core Auth Hook<br/>2. Refactor Login Components<br/>3. Update Dashboard<br/>4. Update API Integration<br/>5. Test Auth Flow"]
    
    Execute["Execute step-by-step<br/>according to plan"]
    
    Request --> Search
    Search --> Analysis
    Analysis --> TodoList
    TodoList --> Execute
```

**Systematic Approach:**
1. Use `Search` to find all `AuthContext` usage (discovered 15+ files)
2. Create todo list to track complex refactoring
3. Execute changes systematically according to plan
4. Ensures nothing is missed in large-scale changes

Sources: [v0 Prompts and Tools/Prompt.txt:1027-1044]()

---

## Integration with File Operations

Context gathering is **mandatory before file operations** [v0 Prompts and Tools/Prompt.txt:94-98]():

```mermaid
graph LR
    subgraph Mandatory["MANDATORY: Read-Before-Write"]
        Step1["1. Search/List<br/>Glob or Search"]
        Step2["2. Read<br/>Read"]
        Step3["3. Write<br/>Edit file"]
    end
    
    subgraph Forbidden["❌ FORBIDDEN"]
        Direct["Write without<br/>reading first"]
    end
    
    Step1 --> Step2
    Step2 --> Step3
    
    style Forbidden fill:#fee
    style Mandatory fill:#efe
```

**Critical Rules:**
- **NEVER** write/edit a file without reading it first
- **ALWAYS** use `Search` to read files before editing
- Risk of breaking code if this rule is violated
- Postamble should be 2-4 sentences explaining changes [v0 Prompts and Tools/Prompt.txt:98]()

Sources: [v0 Prompts and Tools/Prompt.txt:94-98]()

---

## Tool Selection Decision Matrix

```mermaid
graph TB
    Start["Need codebase information"]
    
    Q1{"Know exact<br/>file path?"}
    Q2{"Need to search<br/>for pattern?"}
    Q3{"Need directory<br/>structure?"}
    Q4{"Need comprehensive<br/>exploration?"}
    
    Start --> Q1
    Q1 -->|Yes| Read["Use Read"]
    Q1 -->|No| Q2
    
    Q2 -->|Yes| Grep["Use Grep<br/>Fast pattern search"]
    Q2 -->|No| Q3
    
    Q3 -->|Yes| Glob["Use Glob<br/>List files/dirs"]
    Q3 -->|No| Q4
    
    Q4 -->|Yes| Search["Use Search<br/>Last resort"]
    
    Read --> ParallelCheck{"Multiple files<br/>to read?"}
    ParallelCheck -->|Yes| ParallelReads["Execute Read<br/>in parallel"]
    ParallelCheck -->|No| SingleRead["Single Read"]
```

Sources: [v0 Prompts and Tools/Prompt.txt:480-531]()

---

## Performance Optimization Summary

| Strategy | Speed Gain | When to Use |
|----------|-----------|-------------|
| Parallel `Read` calls | 3-5x faster | Independent file reads |
| `Grep` before `Read` | High | Finding specific patterns |
| `Glob` before `Read` | Medium | Discovering structure |
| `Search` (last resort) | Slowest | Comprehensive exploration |

**Key Principle:** Maximize parallel execution for independent operations while maintaining sequential execution for dependent operations [v0 Prompts and Tools/Prompt.txt:510-519]().

Sources: [v0 Prompts and Tools/Prompt.txt:510-519]()

---

