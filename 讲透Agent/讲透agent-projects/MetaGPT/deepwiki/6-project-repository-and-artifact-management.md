<!-- source: DeepWiki mcp.deepwiki.com · repo FoundationAgents/MetaGPT · page 6 Project Repository and Artifact Management · fetched 2026-10-30 -->

# Project Repository and Artifact Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [metagpt/actions/action.py](metagpt/actions/action.py)
- [metagpt/actions/design_api.py](metagpt/actions/design_api.py)
- [metagpt/actions/prepare_documents.py](metagpt/actions/prepare_documents.py)
- [metagpt/actions/project_management.py](metagpt/actions/project_management.py)
- [metagpt/actions/summarize_code.py](metagpt/actions/summarize_code.py)
- [metagpt/actions/write_code.py](metagpt/actions/write_code.py)
- [metagpt/actions/write_code_review.py](metagpt/actions/write_code_review.py)
- [metagpt/actions/write_prd.py](metagpt/actions/write_prd.py)
- [metagpt/const.py](metagpt/const.py)
- [metagpt/memory/memory.py](metagpt/memory/memory.py)
- [metagpt/prompts/di/swe_agent.py](metagpt/prompts/di/swe_agent.py)
- [metagpt/roles/architect.py](metagpt/roles/architect.py)
- [metagpt/roles/di/swe_agent.py](metagpt/roles/di/swe_agent.py)
- [metagpt/roles/engineer.py](metagpt/roles/engineer.py)
- [metagpt/roles/product_manager.py](metagpt/roles/product_manager.py)
- [metagpt/roles/project_manager.py](metagpt/roles/project_manager.py)
- [metagpt/roles/qa_engineer.py](metagpt/roles/qa_engineer.py)
- [metagpt/roles/role.py](metagpt/roles/role.py)
- [metagpt/schema.py](metagpt/schema.py)
- [metagpt/tools/libs/git.py](metagpt/tools/libs/git.py)
- [metagpt/utils/common.py](metagpt/utils/common.py)
- [metagpt/utils/file_repository.py](metagpt/utils/file_repository.py)
- [metagpt/utils/git_repository.py](metagpt/utils/git_repository.py)
- [tests/metagpt/roles/di/run_swe_agent_for_benchmark.py](tests/metagpt/roles/di/run_swe_agent_for_benchmark.py)
- [tests/metagpt/roles/di/run_swe_agent_open_source_issue.py](tests/metagpt/roles/di/run_swe_agent_open_source_issue.py)
- [tests/metagpt/test_document.py](tests/metagpt/test_document.py)
- [tests/metagpt/tools/libs/test_git.py](tests/metagpt/tools/libs/test_git.py)
- [tests/metagpt/tools/libs/test_image_getter.py](tests/metagpt/tools/libs/test_image_getter.py)

</details>



This document describes MetaGPT's Git-backed project storage system, which manages hierarchical file organization and artifact persistence across the software development lifecycle. The system handles structured documents (PRD, design, tasks) and their human-readable counterparts (Markdown, PDF, SVG) through a dual-hierarchy pattern.

For information about how roles interact with these artifacts during the development workflow, see [Software Development Workflow](#5). For serialization and recovery of entire project state, see [Context Serialization and Recovery](#10.2).

## Overview of ProjectRepo Architecture

The `ProjectRepo` class serves as the primary interface for all project artifact management operations. It maintains parallel directory hierarchies for machine-readable documents (JSON) and human-readable resources (Markdown, PDF, SVG), all backed by Git version control.

```mermaid
graph TB
    subgraph "ProjectRepo Structure"
        PR[ProjectRepo<br/>workdir/project_name/]
        
        subgraph "Git Layer"
            GR[GitRepository<br/>.git/]
            DF[DependencyFile<br/>dependencies.json]
        end
        
        subgraph "docs/ Hierarchy"
            DocsPRD["docs.prd<br/>docs/prd/*.json"]
            DocsDesign["docs.system_design<br/>docs/system_design/*.json"]
            DocsTask["docs.task<br/>docs/task/*.json"]
            DocsPlan["docs.code_plan_and_change<br/>docs/code_plan_and_change/*.json"]
            DocsSummary["docs.code_summary<br/>docs/code_summary/*.json"]
        end
        
        subgraph "resources/ Hierarchy"
            ResPRD["resources.prd<br/>resources/prd/*.md"]
            ResDesign["resources.system_design<br/>resources/system_design/*.pdf"]
            ResTask["resources.api_spec_and_task<br/>resources/api_spec_and_task/*.pdf"]
            ResCompetitive["resources.competitive_analysis<br/>resources/competitive_analysis/*.svg"]
            ResDataAPI["resources.data_api_design<br/>resources/data_api_design/*.svg"]
            ResSeqFlow["resources.seq_flow<br/>resources/seq_flow/*.svg"]
        end
        
        subgraph "Code Repositories"
            Srcs["srcs<br/>src/*.py"]
            Tests["tests<br/>tests/test_*.py"]
            TestOutputs["test_outputs<br/>test_outputs/*.json"]
        end
        
        PR --> GR
        PR --> DF
        PR --> DocsPRD
        PR --> DocsDesign
        PR --> DocsTask
        PR --> DocsPlan
        PR --> DocsSummary
        PR --> ResPRD
        PR --> ResDesign
        PR --> ResTask
        PR --> ResCompetitive
        PR --> ResDataAPI
        PR --> ResSeqFlow
        PR --> Srcs
        PR --> Tests
        PR --> TestOutputs
    end
```

**ProjectRepo Dual Storage Pattern**

| Hierarchy | Content Type | Format | Purpose | Example Path |
|-----------|-------------|--------|---------|--------------|
| `docs/` | Machine-readable | JSON | Structured data for LLM consumption | `docs/prd/20231120_abcd1234.json` |
| `resources/` | Human-readable | MD/PDF/SVG | Formatted output for human review | `resources/prd/20231120_abcd1234.md` |
| `src/` | Source code | .py/.js | Generated application code | `src/main.py` |
| `tests/` | Test code | test_*.py | Generated test cases | `tests/test_main.py` |
| `test_outputs/` | Test results | JSON | Execution results from RunCode | `test_outputs/test_main.py.json` |

Sources: [metagpt/utils/project_repo.py](), [metagpt/const.py:90-111]()

## FileRepository Base Class

`FileRepository` provides the foundational interface for all file operations, managing a specific directory within a Git repository with dependency tracking.

```mermaid
graph LR
    subgraph "FileRepository Interface"
        FR[FileRepository<br/>base class]
        
        subgraph "Core Operations"
            Save["save(filename, content, dependencies)<br/>returns Document"]
            Get["get(filename)<br/>returns Document"]
            Delete["delete(filename)<br/>removes file"]
            SaveDoc["save_doc(doc, dependencies)<br/>updates existing"]
        end
        
        subgraph "Query Methods"
            AllFiles["all_files: Dict[str, ChangeType]<br/>cached list"]
            ChangedFiles["changed_files: Dict[str, ChangeType]<br/>from Git status"]
            GetDependency["get_dependency(filename)<br/>returns Set[str]"]
            GetChangedDep["get_changed_dependency(filename)<br/>filtered by changes"]
        end
        
        subgraph "Properties"
            Workdir["workdir: Path<br/>absolute directory"]
            RootPath["root_path: Path<br/>relative to repo"]
        end
        
        FR --> Save
        FR --> Get
        FR --> Delete
        FR --> SaveDoc
        FR --> AllFiles
        FR --> ChangedFiles
        FR --> GetDependency
        FR --> GetChangedDep
        FR --> Workdir
        FR --> RootPath
    end
    
    Save --> DependencyFile["DependencyFile<br/>update dependencies"]
    GetDependency --> DependencyFile
    Get --> GitIgnore["GitIgnore Rules<br/>skip ignored files"]
```

**Key Methods and Return Types**

```python
# FileRepository core interface
async def save(filename: Path | str, content, dependencies: List[str] = None) -> Document
async def get(filename: Path | str) -> Document | None
async def delete(filename: Path | str) -> bool
async def save_doc(doc: Document, dependencies: Set[str] = None) -> Document
```

The `save` method performs three critical operations:
1. Writes content to disk at `workdir / filename`
2. Updates the dependency graph via `DependencyFile`
3. Returns a `Document` object with metadata

Sources: [metagpt/utils/file_repository.py:23-113]()

## Document Schema and Lifecycle

The `Document` class represents a single file artifact with metadata for dependency tracking and path resolution.

```mermaid
classDiagram
    class Document {
        +str root_path
        +str filename
        +str content
        +get_meta() Document
        +root_relative_path str
        +load(filename, project_path) Document
    }
    
    class Documents {
        +Dict~str,Document~ docs
        +from_iterable(documents) Documents
        +to_action_output() ActionOutput
    }
    
    class CodingContext {
        +str filename
        +Document design_doc
        +Document task_doc
        +Document code_doc
        +Document code_plan_and_change_doc
    }
    
    class TestingContext {
        +str filename
        +Document code_doc
        +Document test_doc
    }
    
    class CodeSummarizeContext {
        +str design_filename
        +str task_filename
        +List~str~ codes_filenames
        +str reason
    }
    
    Documents "1" *-- "*" Document : contains
    CodingContext "1" o-- "3..4" Document : references
    TestingContext "1" o-- "2" Document : references
```

**Document Path Resolution**

The `Document` class maintains both absolute and relative paths:
- `root_path`: Relative directory from repository root (e.g., `"docs/prd"`)
- `filename`: File basename (e.g., `"20231120_abcd1234.json"`)
- `root_relative_path`: Combined path property (e.g., `"docs/prd/20231120_abcd1234.json"`)

This separation enables dependency tracking across different repository sections while maintaining portability when the repository is moved.

Sources: [metagpt/schema.py:138-193](), [metagpt/schema.py:194-222](), [metagpt/schema.py:797-858]()

## Git Integration and Version Control

`GitRepository` wraps the GitPython library and provides MetaGPT-specific operations including dependency management, change tracking, and GitHub integration.

```mermaid
graph TB
    subgraph "GitRepository Operations"
        GR[GitRepository<br/>_repository: Repo]
        
        subgraph "Core Git Operations"
            Init["_init(local_path)<br/>Repo.init + .gitignore"]
            AddChange["add_change(files: Dict)<br/>stage files"]
            Commit["commit(comments)<br/>commit staged"]
            Status["status: str<br/>git status output"]
        end
        
        subgraph "Change Detection"
            ChangedFiles["changed_files: Dict[str, ChangeType]<br/>untracked + diff"]
            ChangeType["ChangeType Enum<br/>ADDED/MODIFIED/DELETED/UNTRACTED"]
        end
        
        subgraph "Dependency System"
            GetDep["get_dependency() DependencyFile<br/>loads dependencies.json"]
            DepFile[DependencyFile<br/>update/get/delete]
        end
        
        subgraph "GitHub Integration"
            CreateIssue["create_issue(repo_name, title, body)<br/>static method"]
            CreatePull["create_pull(base, head, title, body)<br/>static method"]
            ClonePR["clone_from_pr(pr_url)<br/>clone + checkout"]
        end
        
        subgraph "Properties"
            Workdir["workdir: Path<br/>working directory"]
            CurrentBranch["current_branch: str<br/>active branch name"]
            RemoteURL["remote_url: str<br/>origin URL"]
            RepoName["repo_name: str<br/>extracted from URL"]
        end
        
        GR --> Init
        GR --> AddChange
        GR --> Commit
        GR --> Status
        GR --> ChangedFiles
        ChangedFiles --> ChangeType
        GR --> GetDep
        GetDep --> DepFile
        GR --> CreateIssue
        GR --> CreatePull
        GR --> ClonePR
        GR --> Workdir
        GR --> CurrentBranch
        GR --> RemoteURL
        GR --> RepoName
    end
```

**ChangeType Enumeration**

| Value | Constant | Meaning | Git Status |
|-------|----------|---------|------------|
| `"A"` | `ADDED` | New file staged | `A  file.py` |
| `"M"` | `MODIFIED` | Existing file changed | `M  file.py` |
| `"D"` | `DELETED` | File removed | `D  file.py` |
| `"U"` | `UNTRACTED` | File not in version control | `?? file.py` |
| `"C"` | `COPIED` | File copied | `C  file.py` |
| `"R"` | `RENAMED` | File renamed | `R  old.py -> new.py` |
| `"T"` | `TYPE_CHANGED` | File type changed | `T  file` |

The `changed_files` property merges untracked files with the Git index diff to provide a complete picture of modifications.

Sources: [metagpt/utils/git_repository.py:39-47](), [metagpt/utils/git_repository.py:61-189](), [metagpt/utils/git_repository.py:142-150]()

## Dependency Tracking with DependencyFile

`DependencyFile` maintains a persistent JSON graph of file dependencies, enabling change propagation analysis and incremental rebuilds.

```mermaid
graph TB
    subgraph "DependencyFile System"
        DF[DependencyFile<br/>dependencies: Dict[str, Set[str]]]
        
        subgraph "Operations"
            Update["update(filename, dependencies)<br/>record edges"]
            Get["get(filename)<br/>return Set[str]"]
            Delete["delete(filename)<br/>remove node"]
            Load["load(pathname)<br/>read JSON"]
            Save["save(pathname)<br/>write JSON"]
        end
        
        subgraph "Storage Format"
            JSON["dependencies.json<br/>{filename: [dep1, dep2]}"]
        end
        
        DF --> Update
        DF --> Get
        DF --> Delete
        DF --> Load
        DF --> Save
        Save --> JSON
        Load --> JSON
    end
    
    subgraph "Example Dependency Graph"
        Task["docs/task/design_20231120.json"]
        Design["docs/system_design/design_20231120.json"]
        PRD["docs/prd/prd_20231120.json"]
        Code["src/main.py"]
        
        Code --> Task
        Code --> Design
        Task --> Design
        Design --> PRD
    end
```

**Dependency Graph Example**

```json
{
  "src/main.py": [
    "docs/task/design_20231120.json",
    "docs/system_design/design_20231120.json"
  ],
  "docs/task/design_20231120.json": [
    "docs/system_design/design_20231120.json"
  ],
  "docs/system_design/design_20231120.json": [
    "docs/prd/prd_20231120.json"
  ]
}
```

When `WriteTasks` updates a task file, the Engineer can query `get_dependency("src/main.py")` to discover it needs the updated task document and its upstream design document.

Sources: [metagpt/utils/dependency_file.py]() (referenced in [metagpt/utils/git_repository.py:78]())

## ProjectRepo Implementation Details

`ProjectRepo` extends `GitRepository` with specialized `FileRepository` instances for each artifact type, providing type-safe access to different document categories.

```mermaid
graph LR
    subgraph "ProjectRepo Attributes"
        PR[ProjectRepo]
        
        subgraph "Document Repositories"
            DocsPRD["docs.prd<br/>FileRepository"]
            DocsDesign["docs.system_design<br/>FileRepository"]
            DocsTask["docs.task<br/>FileRepository"]
            DocsPlan["docs.code_plan_and_change<br/>FileRepository"]
            DocsSummary["docs.code_summary<br/>FileRepository"]
            Docs["docs<br/>FileRepository<br/>(generic)"]
        end
        
        subgraph "Resource Repositories"
            ResPRD["resources.prd<br/>FileRepository"]
            ResDesign["resources.system_design<br/>FileRepository"]
            ResTask["resources.api_spec_and_task<br/>FileRepository"]
            ResOthers["resources.*<br/>competitive_analysis<br/>data_api_design<br/>seq_flow<br/>code_plan_and_change<br/>code_summary"]
            Resources["resources<br/>FileRepository<br/>(generic)"]
        end
        
        subgraph "Code Repositories"
            Srcs["srcs<br/>FileRepository"]
            Tests["tests<br/>FileRepository"]
            TestOutputs["test_outputs<br/>FileRepository"]
        end
        
        PR --> DocsPRD
        PR --> DocsDesign
        PR --> DocsTask
        PR --> DocsPlan
        PR --> DocsSummary
        PR --> Docs
        
        PR --> ResPRD
        PR --> ResDesign
        PR --> ResTask
        PR --> ResOthers
        PR --> Resources
        
        PR --> Srcs
        PR --> Tests
        PR --> TestOutputs
    end
```

**Repository Path Constants**

The paths are defined in [metagpt/const.py:90-111]():

| Constant | Value | Purpose |
|----------|-------|---------|
| `PRDS_FILE_REPO` | `"docs/prd"` | Product requirement documents |
| `SYSTEM_DESIGN_FILE_REPO` | `"docs/system_design"` | System design specifications |
| `TASK_FILE_REPO` | `"docs/task"` | Task breakdown lists |
| `CODE_PLAN_AND_CHANGE_FILE_REPO` | `"docs/code_plan_and_change"` | Code change plans |
| `CODE_SUMMARIES_FILE_REPO` | `"docs/code_summary"` | Code review summaries |
| `PRD_PDF_FILE_REPO` | `"resources/prd"` | PRD markdown exports |
| `SYSTEM_DESIGN_PDF_FILE_REPO` | `"resources/system_design"` | Design PDF exports |
| `TASK_PDF_FILE_REPO` | `"resources/api_spec_and_task"` | Task PDF exports |
| `COMPETITIVE_ANALYSIS_FILE_REPO` | `"resources/competitive_analysis"` | Competition charts (SVG) |
| `DATA_API_DESIGN_FILE_REPO` | `"resources/data_api_design"` | Class diagrams (SVG) |
| `SEQ_FLOW_FILE_REPO` | `"resources/seq_flow"` | Sequence diagrams (SVG) |
| `TEST_CODES_FILE_REPO` | `"tests"` | Test code |
| `TEST_OUTPUTS_FILE_REPO` | `"test_outputs"` | Test execution results |

Sources: [metagpt/const.py:90-111]()

## Storage Patterns by Development Role

Each role in the software development workflow has specific patterns for reading and writing artifacts through `ProjectRepo`.

### ProductManager (WritePRD)

```mermaid
sequenceDiagram
    participant PM as WritePRD
    participant Repo as ProjectRepo
    participant DocsPRD as docs.prd
    participant ResPRD as resources.prd
    participant ResComp as resources.competitive_analysis
    
    PM->>Repo: docs.save(REQUIREMENT_FILENAME, content)
    PM->>PM: _new_prd(requirement)
    PM->>DocsPRD: save(filename, content, dependencies)
    DocsPRD-->>PM: Document(prd.json)
    PM->>PM: _save_competitive_analysis(prd_doc)
    PM->>ResComp: mermaid_to_file(chart, pathname)
    PM->>ResPRD: save_pdf(doc)
    ResPRD-->>PM: Document(prd.md)
```

The ProductManager:
1. Saves the raw user requirement to `docs/requirement.txt`
2. Generates structured PRD JSON to `docs/prd/{timestamp}_{uuid}.json`
3. Extracts competitive analysis mermaid chart to `resources/competitive_analysis/{name}.svg`
4. Exports human-readable markdown to `resources/prd/{name}.md`

**File Naming Convention**: `FileRepository.new_filename()` generates timestamps like `"20231120_abcd1234"` to ensure unique, sortable filenames.

Sources: [metagpt/actions/write_prd.py:218-230](), [metagpt/actions/write_prd.py:273-283]()

### Architect (WriteDesign)

```mermaid
sequenceDiagram
    participant Arch as WriteDesign
    participant Repo as ProjectRepo
    participant DocsDesign as docs.system_design
    participant ResDesign as resources.system_design
    participant ResDataAPI as resources.data_api_design
    participant ResSeq as resources.seq_flow
    
    Arch->>Arch: _new_system_design(context)
    Arch->>DocsDesign: save(filename, content, dependencies={prd.path})
    DocsDesign-->>Arch: Document(design.json)
    Arch->>Arch: _save_data_api_design(design_doc)
    Arch->>ResDataAPI: mermaid_to_file(class_diagram, pathname)
    Arch->>Arch: _save_seq_flow(design_doc)
    Arch->>ResSeq: mermaid_to_file(sequence_diagram, pathname)
    Arch->>ResDesign: save_pdf(doc)
    ResDesign-->>Arch: Document(design.pdf)
```

The Architect:
1. Loads PRD from `docs/prd/{name}.json`
2. Generates system design to `docs/system_design/{name}.json` with dependency on PRD
3. Extracts class diagram mermaid to `resources/data_api_design/{name}.svg`
4. Extracts sequence diagram to `resources/seq_flow/{name}.svg`
5. Exports PDF to `resources/system_design/{name}.pdf`

Sources: [metagpt/actions/design_api.py:187-207](), [metagpt/actions/design_api.py:209-236]()

### ProjectManager (WriteTasks)

```mermaid
sequenceDiagram
    participant PM as WriteTasks
    participant Repo as ProjectRepo
    participant DocsTask as docs.task
    participant ResTask as resources.api_spec_and_task
    participant Root as repo root
    
    PM->>PM: _run_new_tasks(system_design.content)
    PM->>DocsTask: save(filename, content, dependencies={design.path})
    DocsTask-->>PM: Document(task.json)
    PM->>PM: _update_requirements(task_doc)
    PM->>Root: save(PACKAGE_REQUIREMENTS_FILENAME, packages)
    PM->>ResTask: save_pdf(doc)
    ResTask-->>PM: Document(task.pdf)
```

The ProjectManager:
1. Loads system design from `docs/system_design/{name}.json`
2. Generates task list to `docs/task/{name}.json` with dependency on design
3. Extracts Python package requirements to `requirements.txt` at repository root
4. Exports PDF to `resources/api_spec_and_task/{name}.pdf`

Sources: [metagpt/actions/project_management.py:134-153](), [metagpt/actions/project_management.py:165-176]()

### Engineer (WriteCode)

```mermaid
sequenceDiagram
    participant Eng as Engineer
    participant Repo as ProjectRepo
    participant Srcs as srcs
    participant DocsTask as docs.task
    participant DocsDesign as docs.system_design
    participant DocsPlan as docs.code_plan_and_change
    participant DocsSummary as docs.code_summary
    
    Eng->>DocsTask: get_changed_dependency(filename)
    Eng->>DocsTask: get(task_filename)
    Eng->>DocsDesign: get(design_filename)
    Eng->>DocsPlan: get(code_plan_filename)
    Eng->>Eng: WriteCode(context).run()
    Eng->>Srcs: save(filename, content, dependencies={design, task, plan})
    Srcs-->>Eng: Document(code.py)
    Eng->>Eng: SummarizeCode(context).run()
    Eng->>DocsSummary: save(summary_filename, summary, dependencies)
```

The Engineer:
1. Queries `changed_files` from `repo.docs.task` to find updated tasks
2. Loads dependencies: design doc, task doc, code plan (if incremental mode)
3. Retrieves existing code via `repo.srcs.get(filename)` for modification
4. Saves generated code to `src/{filename}` with dependencies on docs
5. Generates code summary to `docs/code_summary/{design_name}.json`
6. Exports summary markdown to `resources/code_summary/{design_name}.md`

**Incremental Mode**: When `config.inc=True`, Engineer loads `code_plan_and_change_doc` and uses it to guide modifications to existing code rather than rewriting from scratch.

Sources: [metagpt/roles/engineer.py:328-428](), [metagpt/roles/engineer.py:173-198](), [metagpt/roles/engineer.py:290-317]()

### QaEngineer (WriteTest)

```mermaid
sequenceDiagram
    participant QA as QaEngineer
    participant Repo as ProjectRepo
    participant Srcs as srcs
    participant Tests as tests
    participant TestOutputs as test_outputs
    
    QA->>Srcs: get(code_filename)
    QA->>Tests: get("test_" + code_filename)
    QA->>QA: WriteTest(context).run()
    QA->>Tests: save_doc(test_doc, dependencies={code.path})
    Tests-->>QA: Document(test_code.py)
    QA->>QA: RunCode(context).run()
    QA->>TestOutputs: save(output_filename, result, dependencies)
    TestOutputs-->>QA: Document(results.json)
```

The QaEngineer:
1. Iterates through changed files in `repo.srcs.changed_files`
2. Loads source code from `src/{filename}`
3. Generates or loads existing test from `tests/test_{filename}`
4. Saves test code to `tests/test_{filename}` with dependency on source
5. Executes test and saves results to `test_outputs/test_{filename}.json`

Sources: [metagpt/roles/qa_engineer.py:62-104](), [metagpt/roles/qa_engineer.py:105-148]()

## Changed Files Tracking

`FileRepository` and `GitRepository` collaborate to track modifications, enabling incremental workflows where only changed artifacts are reprocessed.

```mermaid
graph TB
    subgraph "Changed Files Detection"
        FR[FileRepository]
        GR[GitRepository]
        
        subgraph "FileRepository.changed_files"
            GetChanges["_get_changed_files()<br/>calls git_repo.changed_files"]
            FilterIgnore["filter by gitignore_rules<br/>skip __pycache__, *.pyc"]
            RelativePath["convert to relative paths<br/>vs self._relative_path"]
            Cache["_cached_files: cache result<br/>for subsequent calls"]
        end
        
        subgraph "GitRepository.changed_files"
            Untracked["untracked_files<br/>files not in Git"]
            IndexDiff["index.diff(None)<br/>staged changes"]
            Merge["merge both sources<br/>return Dict[str, ChangeType]"]
        end
        
        FR --> GetChanges
        GetChanges --> FilterIgnore
        FilterIgnore --> RelativePath
        RelativePath --> Cache
        
        GR --> Untracked
        GR --> IndexDiff
        Untracked --> Merge
        IndexDiff --> Merge
        GetChanges --> Merge
    end
```

**Changed Files Usage Pattern**

```python
# Engineer checks for changed task documents
changed_task_filenames = [
    str(repo.docs.task.workdir / i) 
    for i in list(repo.docs.task.changed_files.keys())
]

# QaEngineer checks for changed source files
changed_src_files = repo.srcs.changed_files
for filename, change_type in changed_src_files.items():
    if change_type in {ChangeType.ADDED, ChangeType.MODIFIED}:
        # Generate tests for this file
        await write_test_for(filename)
```

The `changed_files` property is central to incremental iteration: roles only process artifacts that have been modified since the last commit, avoiding redundant LLM calls.

Sources: [metagpt/utils/file_repository.py:157-183](), [metagpt/utils/git_repository.py:142-150](), [metagpt/roles/engineer.py:331-343]()

## Workspace Initialization and Lifecycle

The `PrepareDocuments` action initializes the workspace structure before any development begins.

```mermaid
sequenceDiagram
    participant User
    participant PrepareDocuments
    participant Config
    participant ProjectRepo
    participant GitRepository
    
    User->>PrepareDocuments: run(with_messages)
    PrepareDocuments->>PrepareDocuments: parse_resources(user_requirement)
    PrepareDocuments->>Config: update_via_cli(project_path, inc)
    PrepareDocuments->>PrepareDocuments: _init_repo()
    alt Project path exists and not incremental
        PrepareDocuments->>PrepareDocuments: shutil.rmtree(path)
    end
    PrepareDocuments->>ProjectRepo: __init__(path)
    ProjectRepo->>GitRepository: open(path, auto_init=True)
    alt Not a git directory
        GitRepository->>GitRepository: _init(path)
        GitRepository->>GitRepository: create .gitignore
        GitRepository->>GitRepository: initial commit
    end
    PrepareDocuments->>ProjectRepo: docs.save(REQUIREMENT_FILENAME, content)
    PrepareDocuments-->>User: AIMessage(PrepareDocumentsOutput)
```

**Initialization Steps**

1. **Path Resolution**: Use `config.project_path` if set, otherwise generate `workspace/{project_name}`
2. **Clean/Incremental Mode**: If `config.inc=False` and path exists, delete it to start fresh
3. **Git Initialization**: Create `.git` directory, add `.gitignore` with Python defaults
4. **Directory Structure**: `FileRepository` constructors create subdirectories on first access
5. **Requirement Persistence**: Save user requirement to `docs/requirement.txt`

The `config.inc` flag controls incremental vs. clean mode:
- `inc=False`: Delete existing workspace, regenerate everything
- `inc=True`: Preserve workspace, modify only changed files

Sources: [metagpt/actions/prepare_documents.py:40-51](), [metagpt/actions/prepare_documents.py:53-90](), [metagpt/utils/git_repository.py:99-112]()

## Special Repository Operations

`FileRepository` provides specialized methods for different artifact types beyond basic save/get/delete.

### PDF Export with save_pdf

```python
async def save_pdf(self, doc: Document, with_suffix: str = ".md", **kwargs) -> Document:
    """
    Save a document as PDF by converting structured JSON to markdown,
    then exporting to the resources/ hierarchy.
    
    Args:
        doc: Document with JSON content
        with_suffix: Output format (default ".md", also supports ".pdf")
    
    Returns:
        Document with exported content
    """
```

The `save_pdf` method:
1. Parses JSON content from the document
2. Converts to markdown using `json_to_markdown`
3. Saves to `resources/{type}/{name}.md` or `.pdf`
4. Maintains the same filename stem as the source document

This creates the parallel docs/resources structure where `docs/prd/design.json` → `resources/prd/design.md`.

Sources: [metagpt/utils/file_repository.py:131-156]()

### Filename Generation with new_filename

```python
@staticmethod
def new_filename(n=8) -> str:
    """
    Generate a unique filename with timestamp and random suffix.
    
    Args:
        n: Length of random hex suffix (default 8)
    
    Returns:
        String like "20231120_a1b2c3d4"
    """
    now = datetime.now()
    return f"{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:n]}"
```

This ensures:
- **Sortability**: Timestamp prefix allows chronological ordering
- **Uniqueness**: UUID suffix prevents collisions
- **Readability**: Human-parseable date component

Used by all document-generating actions to create new files without overwriting.

Sources: [metagpt/utils/file_repository.py:185-195]()

### Directory Existence Check with code_files_exists

```python
def code_files_exists(self) -> bool:
    """
    Check if the repository contains any generated code files.
    
    Returns:
        True if src/ directory exists and is non-empty
    """
    if not self.src_relative_path:
        return False
    return (self.workdir / self.src_relative_path).exists()
```

This is used by `WritePRD` to distinguish between bug fixes (which modify existing code) and new requirements (which generate new code).

Sources: Referenced in [metagpt/actions/write_prd.py:239]()

## Complete Storage Workflow Example

Here's how artifacts flow through the repository during a full development cycle:

```mermaid
sequenceDiagram
    participant User
    participant Prep as PrepareDocuments
    participant PRD as WritePRD
    participant Design as WriteDesign
    participant Task as WriteTasks
    participant Code as Engineer
    participant Test as QaEngineer
    participant Repo as ProjectRepo
    
    User->>Prep: "Write a snake game"
    Prep->>Repo: docs.save(requirement.txt)
    Prep-->>PRD: PrepareDocumentsOutput
    
    PRD->>Repo: docs.prd.save(prd_001.json, dependencies={requirement.txt})
    PRD->>Repo: resources.prd.save_pdf(prd_001.md)
    PRD->>Repo: resources.competitive_analysis.save(chart.svg)
    PRD-->>Design: WritePRDOutput{changed_prd_filenames}
    
    Design->>Repo: docs.system_design.save(design_001.json, deps={prd_001.json})
    Design->>Repo: resources.data_api_design.save(class_diagram.svg)
    Design->>Repo: resources.seq_flow.save(sequence.svg)
    Design->>Repo: resources.system_design.save_pdf(design_001.pdf)
    Design-->>Task: WriteDesignOutput{changed_system_design_filenames}
    
    Task->>Repo: docs.task.save(task_001.json, deps={design_001.json})
    Task->>Repo: save(requirements.txt)
    Task->>Repo: resources.api_spec_and_task.save_pdf(task_001.pdf)
    Task-->>Code: WriteTaskOutput{changed_task_filenames}
    
    Code->>Repo: srcs.save(main.py, deps={task_001.json, design_001.json})
    Code->>Repo: srcs.save(game.py, deps={...})
    Code->>Repo: docs.code_summary.save(summary.json, deps={...})
    Code-->>Test: SummarizeCodeOutput{changed_src_filenames}
    
    Test->>Repo: tests.save(test_main.py, deps={main.py})
    Test->>Repo: tests.save(test_game.py, deps={game.py})
    Test->>Repo: test_outputs.save(test_main.py.json, deps={main.py, test_main.py})
    Test-->>User: WriteTestOutput{changed_test_filenames}
```

**Dependency Chain**

The dependency graph for this workflow:

```
requirement.txt
    └── docs/prd/prd_001.json
            ├── resources/prd/prd_001.md
            ├── resources/competitive_analysis/prd_001.svg
            └── docs/system_design/design_001.json
                    ├── resources/system_design/design_001.pdf
                    ├── resources/data_api_design/design_001.svg
                    ├── resources/seq_flow/design_001.svg
                    └── docs/task/task_001.json
                            ├── resources/api_spec_and_task/task_001.pdf
                            ├── src/main.py
                            │   ├── tests/test_main.py
                            │   └── test_outputs/test_main.py.json
                            ├── src/game.py
                            │   ├── tests/test_game.py
                            │   └── test_outputs/test_game.py.json
                            └── docs/code_summary/design_001.json
                                    └── resources/code_summary/design_001.md
```

Each `save()` call records these dependencies in `dependencies.json`, enabling the system to determine which files need regeneration when upstream dependencies change.

Sources: [metagpt/actions/write_prd.py:129-189](), [metagpt/actions/design_api.py:187-207](), [metagpt/actions/project_management.py:134-153](), [metagpt/roles/engineer.py:328-428](), [metagpt/roles/qa_engineer.py:62-104]()

## Integration with Git Operations

`ProjectRepo` inherits Git operations from `GitRepository` but doesn't automatically commit. Roles must explicitly call `commit()` when appropriate.

**Manual Commit Pattern**

```python
# Typical usage in roles
repo = ProjectRepo(project_path)

# Make changes
await repo.docs.prd.save(filename, content, dependencies)
await repo.resources.prd.save_pdf(doc)

# Commit all changes
changed = repo.changed_files  # Dict[str, ChangeType]
repo.add_change(changed)
repo.commit(f"Add PRD: {filename}")
```

However, most roles in MetaGPT do **not** commit automatically. Instead, they rely on:
1. **End-of-session commits**: The `Team` orchestrator commits after all roles finish
2. **Serialization**: `Team.serialize()` saves state without committing
3. **External commits**: User or CI/CD commits the workspace manually

This separation allows roles to focus on artifact generation while deferring version control strategy to higher layers.

### GitHub Integration

For `SWEAgent` that resolves GitHub issues, Git operations are more sophisticated:

```python
# Clone repository from PR
await GitRepository.clone_from_pr(
    url="https://github.com/owner/repo/pull/123",
    local_path=workspace / "repo",
)

# Make changes...

# Create pull request
pr = await git_create_pull(
    base="main",
    head="feature-branch",
    base_repo_name="owner/repo",
    head_repo_name="contributor/repo",
    title="Fix issue #123",
    body="Description of changes",
    app_name="github",
)
```

Sources: [metagpt/utils/git_repository.py:114-131](), [metagpt/tools/libs/git.py:16-66](), [metagpt/roles/di/swe_agent.py:28-43]()

## Error Handling and Edge Cases

### Missing Dependency Handling

When a file references a dependency that doesn't exist:

```python
# FileRepository.get() returns None for missing files
doc = await repo.docs.task.get("nonexistent.json")
if not doc:
    # Handle missing file
    logger.error(f"Task file not found")
    return None
```

The Engineer checks for this when loading coding context:

```python
if not task_doc or not design_doc:
    if filename == "__init__.py":  # Special case
        return None
    logger.error(f'Detected source code "{filename}" from an unknown origin.')
    raise ValueError(f'Detected source code "{filename}" from an unknown origin.')
```

Sources: [metagpt/roles/engineer.py:305-309]()

### Circular Dependencies

While `DependencyFile` doesn't prevent circular dependencies, the sequential nature of the development workflow (PRD → Design → Tasks → Code) naturally creates a directed acyclic graph (DAG).

### Filename Conflicts

`FileRepository.new_filename()` uses UUID suffixes to prevent conflicts. If a role tries to save with an existing filename, it overwrites:

```python
# First save
await repo.docs.prd.save(filename="my_prd.json", content="v1")

# Second save with same filename
await repo.docs.prd.save(filename="my_prd.json", content="v2")  # Overwrites

# Recommended: use new_filename()
filename = FileRepository.new_filename() + ".json"
await repo.docs.prd.save(filename=filename, content="v1")
```

Sources: [metagpt/utils/file_repository.py:46-64]()

### Git Ignore Rules

The `.gitignore` created during initialization excludes common Python artifacts:

```python
ignores = ["__pycache__", "*.pyc", ".vs"]
```

`FileRepository._get_changed_files()` respects these rules, filtering out ignored files from the changed files list.

Sources: [metagpt/utils/git_repository.py:106-112](), [metagpt/utils/file_repository.py:169-174]()

---

