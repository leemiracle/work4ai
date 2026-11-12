<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/huggingface_hub · page 2 Core API Client (HfApi) · fetched 2026-10-26 -->

# Core API Client (HfApi)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/huggingface_hub/__init__.py](src/huggingface_hub/__init__.py)
- [src/huggingface_hub/_commit_api.py](src/huggingface_hub/_commit_api.py)
- [src/huggingface_hub/_login.py](src/huggingface_hub/_login.py)
- [src/huggingface_hub/constants.py](src/huggingface_hub/constants.py)
- [src/huggingface_hub/file_download.py](src/huggingface_hub/file_download.py)
- [src/huggingface_hub/hf_api.py](src/huggingface_hub/hf_api.py)
- [src/huggingface_hub/utils/__init__.py](src/huggingface_hub/utils/__init__.py)
- [src/huggingface_hub/utils/_headers.py](src/huggingface_hub/utils/_headers.py)
- [src/huggingface_hub/utils/_runtime.py](src/huggingface_hub/utils/_runtime.py)
- [src/huggingface_hub/utils/_xet.py](src/huggingface_hub/utils/_xet.py)
- [tests/test_file_download.py](tests/test_file_download.py)
- [tests/test_hf_api.py](tests/test_hf_api.py)
- [tests/test_utils_headers.py](tests/test_utils_headers.py)
- [tests/test_xet_utils.py](tests/test_xet_utils.py)
- [tests/testing_utils.py](tests/testing_utils.py)

</details>



The `HfApi` class is the primary HTTP-based client for programmatic interaction with the Hugging Face Hub. It provides methods for repository management, file operations, metadata queries, and administrative tasks. This page documents the class structure, initialization patterns, core methods, and design principles. 

For file download and caching mechanisms, see [File Download and Upload](#2.2). For commit operations and LFS integration, see [Commit API and LFS Integration](#2.3). For Git-based workflows, see [Repository Class (Git-based)](#4).

## HfApi Class Structure

The `HfApi` class serves as a stateful wrapper around Hub REST API endpoints, managing authentication tokens, endpoint URLs, and HTTP sessions across multiple operations.

```mermaid
graph TB
    subgraph "HfApi Instantiation"
        Init["HfApi.__init__()"]
        Init --> Endpoint["self.endpoint<br/>default: constants.ENDPOINT"]
        Init --> Token["self.token<br/>from parameter or get_token()"]
        Init --> LibMeta["self.library_name<br/>self.library_version<br/>self.user_agent"]
        Init --> Headers["self.headers<br/>custom headers dict"]
    end
    
    subgraph "Token Resolution Priority"
        TokenParam["1. token parameter"]
        EnvToken["2. get_token()<br/>checks HF_TOKEN, Colab, ~/.cache/huggingface/token"]
        TokenParam --> EnvToken
    end
    
    subgraph "Endpoint Configuration"
        DefaultEndpoint["Default: https://huggingface.co"]
        CustomEndpoint["Custom via endpoint param"]
        EnvEndpoint["HF_ENDPOINT env variable"]
        DefaultEndpoint -.fallback.-> EnvEndpoint
        CustomEndpoint -.overrides.-> EnvEndpoint
    end
    
    Init --> TokenParam
    Init --> DefaultEndpoint
```

**HfApi Initialization and Configuration**

Sources: [src/huggingface_hub/hf_api.py:1896-1982]()

### Initialization Parameters

The `HfApi` constructor accepts optional configuration that applies to all subsequent method calls:

| Parameter | Type | Purpose | Default |
|-----------|------|---------|---------|
| `endpoint` | `str` | Hub API base URL | `constants.ENDPOINT` |
| `token` | `str \| bool` | Authentication token | `None` (auto-resolved) |
| `library_name` | `str` | Client library identifier for telemetry | `None` |
| `library_version` | `str` | Client library version | `None` |
| `user_agent` | `str \| dict` | Additional user agent info | `None` |
| `headers` | `dict` | Custom HTTP headers | `None` |

Token resolution follows a fallback chain: explicit parameter → `get_token()` helper → environment variable `HF_TOKEN` → Google Colab secrets → token file at `~/.cache/huggingface/token`. Setting `token=False` explicitly disables authentication.

Sources: [src/huggingface_hub/hf_api.py:1896-1982](), [src/huggingface_hub/utils/_headers.py:133-171]()

## Core Method Categories

The `HfApi` class organizes ~150 public methods into functional groups. Methods generally accept `repo_id`, `repo_type`, and `revision` parameters following consistent naming patterns.

```mermaid
graph LR
    HfApi["HfApi Instance"]
    
    subgraph "Repository Lifecycle"
        Create["create_repo()<br/>create_branch()<br/>create_tag()"]
        Delete["delete_repo()<br/>delete_branch()<br/>delete_tag()"]
        Update["update_repo_settings()<br/>move_repo()<br/>super_squash_history()"]
    end
    
    subgraph "File Operations"
        Upload["upload_file()<br/>upload_folder()<br/>create_commit()"]
        Download["hf_hub_download<br/>snapshot_download"]
        Remove["delete_file()<br/>delete_folder()"]
    end
    
    subgraph "Information Queries"
        RepoInfo["repo_info()<br/>model_info()<br/>dataset_info()<br/>space_info()"]
        List["list_models()<br/>list_datasets()<br/>list_spaces()<br/>list_repo_files()"]
        Tree["list_repo_tree()<br/>get_paths_info()"]
    end
    
    subgraph "Access Control"
        Gate["list_pending_access_requests()<br/>grant_access()<br/>reject_access_request()"]
        Like["like()<br/>unlike()<br/>list_liked_repos()"]
    end
    
    subgraph "Authentication"
        Auth["whoami()<br/>auth_check()<br/>get_token_permission()"]
    end
    
    HfApi --> Create
    HfApi --> Delete
    HfApi --> Update
    HfApi --> Upload
    HfApi --> Download
    HfApi --> Remove
    HfApi --> RepoInfo
    HfApi --> List
    HfApi --> Tree
    HfApi --> Gate
    HfApi --> Like
    HfApi --> Auth
```

**Method Organization in HfApi**

Sources: [src/huggingface_hub/hf_api.py:1984-5500]()

### Repository Management Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `create_repo()` | Create new repository | `RepoUrl` |
| `delete_repo()` | Delete repository | `None` |
| `update_repo_settings()` | Modify visibility, gating, Xet settings | `None` |
| `move_repo()` | Rename/relocate repository | `None` |
| `repo_exists()` | Check repository existence | `bool` |
| `revision_exists()` | Check if revision exists | `bool` |
| `file_exists()` | Check if file exists at path | `bool` |

The `create_repo()` method returns a `RepoUrl` object that inherits from `str` but provides structured access to repository metadata:

```mermaid
classDiagram
    class RepoUrl {
        +str url
        +str endpoint
        +str namespace
        +str repo_name
        +str repo_id
        +str repo_type
        +__new__(url, endpoint)
        +__repr__()
    }
    
    class Usage {
        api.create_repo("my-model")
        "RepoUrl('https://huggingface.co/user/my-model')"
    }
    
    str <|-- RepoUrl
    Usage ..> RepoUrl
```

**RepoUrl Data Structure**

Sources: [src/huggingface_hub/hf_api.py:534-593](), [tests/test_hf_api.py:413-419]()

### Information Retrieval Methods

Information methods return rich dataclass objects with optional properties depending on query parameters:

```mermaid
graph TB
    subgraph "repo_info() Method"
        Call["api.repo_info(repo_id, files_metadata=True)"]
        Detect["Auto-detect repo_type<br/>from repo_id format"]
        Request["GET /api/{repo_type}s/{repo_id}"]
        Parse["Parse JSON response"]
        Return["Return ModelInfo/DatasetInfo/SpaceInfo"]
        
        Call --> Detect
        Detect --> Request
        Request --> Parse
        Parse --> Return
    end
    
    subgraph "Info Object Attributes"
        Core["Always present:<br/>id, sha, last_modified, private"]
        Optional["Optional (via expand param):<br/>siblings, cardData, safetensors,<br/>downloads, likes, tags"]
        Metadata["files_metadata=True:<br/>siblings with size, blob_id, lfs"]
    end
    
    Return --> Core
    Return --> Optional
    Return --> Metadata
```

**repo_info() Method Flow**

The `files_metadata` parameter controls whether file details (size, blob_id, LFS metadata) are included in `siblings` list. Without this flag, `siblings` contains only filenames.

Sources: [src/huggingface_hub/hf_api.py:2619-2757]()

### List Methods with Pagination

List methods (`list_models()`, `list_datasets()`, `list_spaces()`) return iterators that automatically handle pagination via the `paginate()` utility:

```mermaid
sequenceDiagram
    participant Client
    participant HfApi
    participant Paginate
    participant Hub
    
    Client->>HfApi: list_models(limit=1000)
    HfApi->>Paginate: paginate(endpoint, params)
    
    loop Until exhausted or limit reached
        Paginate->>Hub: GET /api/models?limit=100
        Hub-->>Paginate: {items: [...], next: "token"}
        Paginate->>Paginate: Yield items
        Paginate->>Client: Yield ModelInfo objects
        
        alt Has next page
            Paginate->>Hub: GET /api/models?next=token
        end
    end
    
    Client->>Client: Process results
```

**Pagination in List Methods**

The `paginate()` helper uses response headers (`X-Next`, `Link`) to fetch subsequent pages transparently. The `limit` parameter controls total results, not per-page size.

Sources: [src/huggingface_hub/hf_api.py:2169-2299](), [src/huggingface_hub/utils/_pagination.py:1-100]()

## Data Structures and Return Types

`HfApi` methods return strongly-typed dataclasses that provide both attribute access and dictionary-like behavior for backward compatibility.

```mermaid
classDiagram
    class CommitInfo {
        +str commit_url
        +str commit_message
        +str commit_description
        +str oid
        +str pr_url
        +str pr_revision
        +int pr_num
        +RepoUrl repo_url
        +str _url
    }
    
    class ModelInfo {
        +str id
        +str author
        +str sha
        +datetime last_modified
        +bool private
        +List~RepoSibling~ siblings
        +ModelCardData card_data
        +TransformersInfo transformers_info
        +SafeTensorsInfo safetensors
        +dict config
    }
    
    class RepoSibling {
        +str rfilename
        +int size
        +str blob_id
        +BlobLfsInfo lfs
    }
    
    class RepoFile {
        +str path
        +int size
        +str blob_id
        +BlobLfsInfo lfs
        +LastCommitInfo last_commit
        +BlobSecurityInfo security
    }
    
    class RepoFolder {
        +str path
        +str tree_id
        +LastCommitInfo last_commit
    }
    
    ModelInfo --> RepoSibling
    RepoFile --> BlobLfsInfo
    RepoFile --> LastCommitInfo
```

**Core Data Structures Returned by HfApi**

### CommitInfo Object

`CommitInfo` inherits from `str` for backward compatibility (returns commit URL as string) but provides structured fields:

| Attribute | Type | Description |
|-----------|------|-------------|
| `commit_url` | `str` | Full URL to commit on Hub |
| `commit_message` | `str` | First line of commit message |
| `commit_description` | `str` | Remaining lines of commit message |
| `oid` | `str` | 40-character commit hash |
| `pr_url` | `str` | URL to PR if `create_pr=True` |
| `pr_revision` | `str` | Git ref like `refs/pr/1` |
| `pr_num` | `int` | PR discussion number |
| `repo_url` | `RepoUrl` | Parsed repository URL |

Sources: [src/huggingface_hub/hf_api.py:378-455](), [tests/test_hf_api.py:594-607]()

### ModelInfo, DatasetInfo, SpaceInfo

These info objects share common fields but include type-specific attributes:

**Common Fields:**
- `id`, `author`, `sha`, `created_at`, `last_modified`
- `private`, `disabled`, `gated`, `downloads`, `likes`
- `siblings` (list of `RepoSibling` objects)
- `card_data` (typed CardData object)

**ModelInfo-Specific:**
- `transformers_info`: Auto-detection of model class, pipeline tag
- `safetensors`: Parameter counts and tensor info
- `inference_provider_mapping`: Available inference providers
- `library_name`: Detected ML framework

**SpaceInfo-Specific:**
- `runtime`: Current Space execution status
- `sdk`: Gradio, Streamlit, Docker, or Static
- `models`, `datasets`: Linked repositories

Sources: [src/huggingface_hub/hf_api.py:742-1074]()

## HTTP Communication and Error Handling

`HfApi` methods use a resilient HTTP layer with automatic retries, custom error types, and request ID tracking.

```mermaid
graph TB
    subgraph "Request Flow"
        Method["HfApi method call"]
        Headers["build_hf_headers()<br/>- Authorization token<br/>- User-Agent<br/>- Library metadata"]
        Session["get_session()<br/>Shared requests.Session<br/>with UniqueRequestIdAdapter"]
        Backoff["http_backoff()<br/>Retry on 5xx, timeout, connection errors"]
        Response["requests.Response"]
        RaiseStatus["hf_raise_for_status()<br/>Parse X-Error-Code header"]
        
        Method --> Headers
        Headers --> Session
        Session --> Backoff
        Backoff --> Response
        Response --> RaiseStatus
    end
    
    subgraph "Error Types"
        RaiseStatus --> BadRequest["BadRequestError<br/>400"]
        RaiseStatus --> RepoNotFound["RepositoryNotFoundError<br/>404 + repo error"]
        RaiseStatus --> EntryNotFound["EntryNotFoundError<br/>404 + file error"]
        RaiseStatus --> RevisionNotFound["RevisionNotFoundError<br/>404 + revision error"]
        RaiseStatus --> GatedRepo["GatedRepoError<br/>403"]
        RaiseStatus --> Generic["HfHubHTTPError<br/>Other errors"]
    end
```

**HTTP Request Flow with Error Handling**

### Request ID Tracking

Every request includes a unique `X-Request-Id` header generated client-side. On error, the server's request ID (from response header) is included in exception messages for debugging.

Sources: [src/huggingface_hub/utils/_http.py:242-316](), [src/huggingface_hub/utils/_errors.py:1-400]()

### Retry Logic

The `http_backoff()` function implements exponential backoff with jitter for transient errors:

| Error Type | Retry? | Max Attempts | Backoff |
|------------|--------|--------------|---------|
| 5xx Server Error | Yes | 5 | Exponential + jitter |
| Connection Error | Yes | 5 | Exponential + jitter |
| Timeout | Yes | 5 | Exponential + jitter |
| 4xx Client Error | No | 0 | - |

File upload operations reset the file cursor on retry to enable re-reading from the beginning.

Sources: [src/huggingface_hub/utils/_http.py:95-162]()

### Specialized Error Types

```mermaid
classDiagram
    class HfHubHTTPError {
        +Response response
        +str request_id
        +str server_message
    }
    
    class RepositoryNotFoundError {
        +str message
        "Repository not found or no access"
    }
    
    class EntryNotFoundError {
        +str message
        "File not found in repository"
    }
    
    class RevisionNotFoundError {
        +str message
        "Git revision does not exist"
    }
    
    class GatedRepoError {
        +str message
        "Repository is gated, user not authorized"
    }
    
    HTTPError <|-- HfHubHTTPError
    HfHubHTTPError <|-- RepositoryNotFoundError
    HfHubHTTPError <|-- EntryNotFoundError
    HfHubHTTPError <|-- RevisionNotFoundError
    HfHubHTTPError <|-- GatedRepoError
```

**Error Class Hierarchy**

The `hf_raise_for_status()` function examines the `X-Error-Code` response header to raise specific exception types. This allows client code to handle different failure modes with targeted exception handlers.

Sources: [src/huggingface_hub/utils/_errors.py:80-300](), [src/huggingface_hub/utils/_http.py:399-526]()

## Method Patterns and Conventions

`HfApi` methods follow consistent patterns for parameter naming, validation, and return types.

### Common Parameter Pattern

Most repository-scoped methods accept these parameters:

```python
def method_name(
    repo_id: str,                              # Required: "namespace/repo_name"
    *,
    repo_type: Optional[str] = None,           # "model" (default), "dataset", or "space"
    revision: Optional[str] = None,            # Branch, tag, or commit hash (default: "main")
    token: Optional[Union[str, bool]] = None,  # Auth token (default: instance token)
    headers: Optional[Dict[str, str]] = None,  # Additional HTTP headers
) -> ReturnType:
    ...
```

The `repo_id` parameter accepts multiple formats:
- `"username/repo_name"` (most common)
- `"repo_name"` (uses authenticated user's namespace)
- `"hf://repo_type/username/repo_name"` (explicit format)
- Full Hub URLs (parsed to extract components)

Sources: [src/huggingface_hub/hf_api.py:239-322]()

### Validation Decorator

The `@validate_hf_hub_args` decorator provides automatic parameter validation and normalization:

```mermaid
graph LR
    Call["Method invocation"]
    Decorator["@validate_hf_hub_args"]
    
    Decorator --> ParseRepoId["Parse repo_id format<br/>Extract namespace and name"]
    Decorator --> NormalizeType["Normalize repo_type<br/>'models' → 'model'"]
    Decorator --> ValidateRevision["Validate revision format<br/>Quote special characters"]
    Decorator --> ResolveToken["Resolve token value<br/>True → get_token()"]
    
    Call --> Decorator
    ParseRepoId --> Execute["Execute method"]
    NormalizeType --> Execute
    ValidateRevision --> Execute
    ResolveToken --> Execute
```

**Parameter Validation Flow**

Sources: [src/huggingface_hub/utils/_validators.py:1-200]()

### Deprecation Handling

Deprecated methods and parameters use the `@_deprecate_arguments` decorator to emit `FutureWarning`:

```python
@_deprecate_arguments(version="1.0", deprecated_args={"use_auth_token": "token"})
def some_method(self, token: Optional[str] = None, use_auth_token: Optional[str] = None):
    # Automatically handles migration and warning
    ...
```

The decorator updates docstrings and emits warnings while maintaining backward compatibility during the deprecation period.

Sources: [src/huggingface_hub/utils/_deprecation.py:1-200]()

## Integration with Other Components

`HfApi` serves as the foundation for higher-level abstractions in the library.

```mermaid
graph TB
    subgraph "Direct Consumers"
        CLI["CLI Commands<br/>commands/*.py"]
        Download["hf_hub_download()<br/>snapshot_download()"]
        Mixins["ModelHubMixin<br/>PyTorchModelHubMixin"]
        FileSystem["HfFileSystem"]
        InferenceClient["InferenceClient"]
    end
    
    subgraph "HfApi Core"
        HfApi["HfApi Class"]
        RepoMethods["Repository Methods"]
        FileMethods["File Methods"]
        InfoMethods["Info Methods"]
    end
    
    subgraph "Foundation Layer"
        Auth["get_token()<br/>Token resolution"]
        HTTP["get_session()<br/>http_backoff()"]
        Headers["build_hf_headers()"]
    end
    
    CLI --> HfApi
    Download --> HfApi
    Mixins --> HfApi
    FileSystem --> HfApi
    InferenceClient --> HfApi
    
    HfApi --> RepoMethods
    HfApi --> FileMethods
    HfApi --> InfoMethods
    
    RepoMethods --> Auth
    FileMethods --> Auth
    InfoMethods --> Auth
    
    RepoMethods --> HTTP
    FileMethods --> HTTP
    InfoMethods --> HTTP
    
    RepoMethods --> Headers
    FileMethods --> Headers
    InfoMethods --> Headers
```

**HfApi in System Architecture**

### CLI Integration

Command classes instantiate `HfApi` with endpoint and token from command arguments:

```python
# In commands/user.py
class WhoamiCommand(BaseUserCommand):
    def run(self):
        token = get_token()
        info = self._api.whoami(token)
        print(info["name"])
```

Sources: [src/huggingface_hub/commands/user.py:188-208]()

### Mixin Integration

`ModelHubMixin` uses `HfApi` methods for `push_to_hub()` and `from_pretrained()`:

```python
def push_to_hub(self, repo_id: str, **kwargs):
    api = HfApi()
    api.create_repo(repo_id, exist_ok=True)
    api.upload_folder(folder_path=local_dir, repo_id=repo_id)
```

Sources: [src/huggingface_hub/hub_mixin.py:200-350]()

### HfFileSystem Integration

`HfFileSystem` delegates metadata operations to `HfApi`:

```python
class HfFileSystem:
    def __init__(self, *args, **kwargs):
        self._api = HfApi(...)
    
    def info(self, path: str):
        # Calls api.get_paths_info() internally
        return self._api.get_paths_info(...)
```

Sources: [src/huggingface_hub/hf_file_system.py:100-200]()

## Authentication and Token Management

`HfApi` supports multiple authentication patterns through its `token` parameter and the global token resolution system.

### Token Parameter Behavior

| `token` Value | Behavior |
|---------------|----------|
| `None` (default) | Use instance token or `get_token()` |
| `"hf_..."` string | Use provided token for this request |
| `True` | Explicitly call `get_token()` |
| `False` | Explicitly disable authentication |

The `token=False` pattern is useful for accessing public repositories without triggering token lookup logic.

Sources: [src/huggingface_hub/hf_api.py:1896-1982]()

### Token Storage Locations

The `get_token()` helper checks multiple sources in priority order:

```mermaid
graph TB
    GetToken["get_token()"]
    
    GetToken --> Env["1. HF_TOKEN env variable"]
    Env --> Colab["2. Google Colab secrets<br/>(if running in Colab)"]
    Colab --> File["3. ~/.cache/huggingface/token"]
    File --> Stored["4. stored_tokens<br/>(multi-account support)"]
    Stored --> Return["Return token or None"]
    
    File -.optional.-> Git["Git credential helper<br/>(if configured)"]
```

**Token Resolution Priority**

The stored tokens file (introduced in v0.20) allows managing multiple accounts with `auth_switch()` command.

Sources: [src/huggingface_hub/utils/_auth.py:1-200]()

### whoami() Method

The `whoami()` method returns account information for the authenticated user:

```python
{
    "type": "user",
    "name": "username",
    "fullname": "Full Name",
    "email": "user@example.com",
    "orgs": [
        {"name": "org1", "fullname": "Organization 1"},
        {"name": "org2", "fullname": "Organization 2"}
    ],
    "auth": {
        "type": "access_token",  # or "oauth"
        "accessToken": {"role": "write"}
    }
}
```

For OAuth tokens, the response includes expiration information in the `auth.expiresAt` field.

Sources: [src/huggingface_hub/hf_api.py:2051-2080](), [tests/test_hf_api.py:174-208]()

## Performance Considerations

### Session Reuse

`HfApi` uses `get_session()` which returns a singleton `requests.Session` with connection pooling. This reuses TCP connections across multiple API calls, significantly reducing latency for repeated operations.

Sources: [src/huggingface_hub/utils/_http.py:50-90]()

### Parallel Operations

Methods like `upload_folder()` use thread pools for parallel file uploads:

```python
# Internal implementation
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [
        executor.submit(upload_file, file)
        for file in files
    ]
```

The default thread count is 5 but can be overridden with the `num_threads` parameter in applicable methods.

Sources: [src/huggingface_hub/hf_api.py:4200-4300]()

### Caching Strategy

`HfApi` itself does not implement caching—this is handled by `hf_hub_download()` and the cache system. However, methods like `repo_info()` can be called repeatedly as the overhead is a single HTTP request.

For scenarios requiring frequent metadata queries, consider:
1. Caching `repo_info()` results client-side with a TTL
2. Using `list_repo_tree()` once and filtering locally
3. Using `HfFileSystem` which implements its own caching

Sources: [src/huggingface_hub/hf_file_system.py:1-100]()

---

