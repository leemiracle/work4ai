<!-- source: DeepWiki mcp.deepwiki.com · repo yusufkaraaslan/Skill_Seekers · extra page GitHub API vs Local Mode · fetched 2026-10-26 -->

# GitHub API vs Local Mode

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/skill_seekers/cli/config_validator.py](src/skill_seekers/cli/config_validator.py)
- [src/skill_seekers/cli/generate_router.py](src/skill_seekers/cli/generate_router.py)
- [src/skill_seekers/cli/github_scraper.py](src/skill_seekers/cli/github_scraper.py)
- [src/skill_seekers/cli/pdf_scraper.py](src/skill_seekers/cli/pdf_scraper.py)
- [src/skill_seekers/cli/presets/github_presets.py](src/skill_seekers/cli/presets/github_presets.py)
- [src/skill_seekers/cli/presets/scrape_presets.py](src/skill_seekers/cli/presets/scrape_presets.py)
- [src/skill_seekers/cli/split_config.py](src/skill_seekers/cli/split_config.py)
- [tests/test_github_scraper.py](tests/test_github_scraper.py)

</details>



This page explains the two operating modes of the `GitHubScraper` component: **GitHub API mode** (remote access via GitHub's REST API using PyGithub) and **Local mode** (direct filesystem access to a cloned repository). It details authentication resolution, rate-limit management strategies, directory exclusion filtering, and configuration fallback mechanisms.

---

## Mode Selection & Initialization

The `GitHubScraper` class [src/skill_seekers/cli/github_scraper.py:184]() supports two distinct operating modes determined by the presence of the `local_repo_path` configuration parameter during initialization via `__init__(config, local_repo_path)` [src/skill_seekers/cli/github_scraper.py:202-225]().

```mermaid
flowchart TD
    subgraph NaturalLanguageSpace ["Natural Language Space"]
        UserConfig["User Configuration Request"] --> ModeDecision["Determine GitHub Scraper Mode"]
    end

    subgraph CodeEntitySpace ["Code Entity Space"]
        ModeDecision --> InitCall["GitHubScraper.__init__(config, local_repo_path) [src/skill_seekers/cli/github_scraper.py:202]"]
        InitCall --> CheckPath{"config.get('local_repo_path') [src/skill_seekers/cli/github_scraper.py:214]"}
        CheckPath -->|"None"| ApiMode["GitHub API Mode"]
        CheckPath -->|"Path provided"| LocalMode["Local Repository Mode"]
        
        ApiMode --> GithubClient["self.github = Github(token) [src/skill_seekers/cli/github_scraper.py:255]"]
        LocalMode --> ExpandPath["os.path.expanduser(self.local_repo_path) [src/skill_seekers/cli/github_scraper.py:216]"]
        ExpandPath --> CheckDir{"os.path.isdir() [src/skill_seekers/cli/github_scraper.py:217]"}
        CheckDir -->|"No"| Fallback["Log warning & Fallback to API [src/skill_seekers/cli/github_scraper.py:218]"]
        CheckDir -->|"Yes"| LocalWalk["Local Filesystem Traversal"]
    end
```

**Mode Selection Logic:** If a provided `local_repo_path` does not exist on the filesystem or is not a valid directory, the system logs a warning and automatically falls back to **GitHub API mode** [src/skill_seekers/cli/github_scraper.py:217-222]().

Sources: [src/skill_seekers/cli/github_scraper.py:184-225]()

---

## GitHub API Mode

GitHub API mode uses the `PyGithub` library [src/skill_seekers/cli/github_scraper.py:27-32]() to fetch repository contents remotely. This is the standard mode for cloud-based scraping where a local clone is unavailable.

### Authentication and Token Configuration

Token handling is managed by a hierarchy of sources, prioritized to ensure security and flexibility. The `GitHubScraper` retrieves the token via `_get_token()` [src/skill_seekers/cli/github_scraper.py:237]().

```mermaid
flowchart TD
    subgraph NaturalLanguageSpace ["Natural Language Space"]
        TokenLookup["Retrieve GitHub Credentials"] --> CheckEnv["Check Environment Variables"]
        CheckEnv --> CheckConfig["Check Configuration File"]
    end

    subgraph CodeEntitySpace ["Code Entity Space"]
        CheckEnv --> EnvFetch["os.environ.get('GITHUB_TOKEN') [tests/test_github_scraper.py:85]"]
        EnvFetch -->|"Found"| UseEnv["Return Environment Token"]
        EnvFetch -->|"Not found"| ConfigFetch["self.config.get('github_token') [src/skill_seekers/cli/github_scraper.py:237]"]
        ConfigFetch -->|"Found"| UseConfig["Return Config Token"]
        ConfigFetch -->|"Not found"| NoAuth["Return None (Unauthenticated)"]
        
        UseEnv --> GithubInit["Github(token) [tests/test_github_scraper.py:89]"]
        UseConfig --> GithubInit
        NoAuth --> GithubUnauth["Github() [tests/test_github_scraper.py:96]"]
    end
```

**Authentication Priority Order:**

| Priority | Source | Implementation | Rate Limit |
|----------|--------|----------------|------------|
| 1 | Environment Variable | `os.environ.get("GITHUB_TOKEN")` [tests/test_github_scraper.py:85]() | 5000/hour |
| 2 | Config File | `config["github_token"]` [src/skill_seekers/cli/github_scraper.py:237]() | 5000/hour |
| 3 | Unauthenticated | `Github()` [tests/test_github_scraper.py:96]() | 60/hour |

Sources: [src/skill_seekers/cli/github_scraper.py:237-251](), [tests/test_github_scraper.py:63-115]()

### Rate Limit Strategies

The `ConfigManager` allows per-profile configuration of `rate_limit_strategy`. The scraper explicitly handles `RateLimitExceededException` [src/skill_seekers/cli/github_scraper.py:29]() to prevent hard crashes during long extraction jobs by catching rate-limit blocks and applying waiting or token-switching strategies.

Sources: [src/skill_seekers/cli/github_scraper.py:27-32]()

---

## Local Repository Mode

Local mode analyzes a repository directly from the disk. This is significantly faster and bypasses all GitHub API constraints.

### File Tree Extraction (Local)

Local mode uses `os.walk()` for traversal and supports `.gitignore` filtering if `pathspec` is installed [src/skill_seekers/cli/github_scraper.py:37-42]().

```mermaid
flowchart TD
    Start["_extract_file_tree_local()"] --> Walk["os.walk(self.local_repo_path)"]
    Walk --> FilterDir{"should_exclude_dir(dir)"}
    FilterDir -->|"Excluded"| Skip["Remove from dirs list"]
    FilterDir -->|"Included"| FileLoop["Iterate files in dir"]
    FileLoop --> ExcludeFile{"is_excluded_file(file)?"}
    ExcludeFile -->|"No"| Add["Add to file_tree list"]
```

**Directory Exclusion:** The scraper uses a predefined `EXCLUDED_DIRS` set [src/skill_seekers/cli/github_scraper.py:56-100]() to avoid processing massive build artifacts or dependency folders (e.g., `node_modules`, `venv`, `Library`, `.godot`).

### Advantages of Local Mode

| Advantage | Implementation Detail |
|-----------|----------------------|
| **No Rate Limits** | File content is read via standard I/O, avoiding network bottlenecks. |
| **Full Codebase Analysis** | Enables `CodeAnalyzer` to perform deep AST parsing on the entire project [src/skill_seekers/cli/github_scraper.py:47-52](). |
| **No Auth Required** | Works on private repositories as long as they are cloned locally. |
| **Speed** | Traversing local storage is orders of magnitude faster than sequential REST API calls. |

Sources: [src/skill_seekers/cli/github_scraper.py:37-100](), [src/skill_seekers/cli/github_scraper.py:213-225]()

---

## Configuration Fallback & Resolution

When the CLI is invoked with a config reference, configuration resolution handles locating local files or fetching remote templates seamlessly.

```mermaid
sequenceDiagram
    participant CLI as CLI/Scraper
    participant CF as config_fetcher.py
    participant LOCAL as Local Filesystem
    participant API as SkillSeekersWeb API
    
    CLI->>CF: resolve_config_path("react")
    CF->>LOCAL: Check ./react.json
    CF->>LOCAL: Check ./configs/react.json
    CF->>LOCAL: Check ~/.config/skill-seekers/configs/react.json
    
    alt Not Found Locally
        CF->>API: GET /api/configs/react
        API-->>CF: Return JSON config + download_url
        CF->>LOCAL: Save to configs/react.json
    end
    
    CF-->>CLI: Return resolved Path
```

Sources: [src/skill_seekers/cli/config_validator.py:78-102]()

---

