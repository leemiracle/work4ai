<!-- source: DeepWiki mcp.deepwiki.com · repo kubestellar/console · page 12 Nightly E2E Monitoring · fetched 2026-10-27 -->

# Nightly E2E Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/api/handlers/nightly_e2e.go](pkg/api/handlers/nightly_e2e.go)
- [web/netlify/functions/nightly-e2e.mts](web/netlify/functions/nightly-e2e.mts)
- [web/src/components/cards/llmd/NightlyE2EStatus.tsx](web/src/components/cards/llmd/NightlyE2EStatus.tsx)
- [web/src/config/cards/nightly-e2e-status.ts](web/src/config/cards/nightly-e2e-status.ts)
- [web/src/hooks/useNightlyE2EData.ts](web/src/hooks/useNightlyE2EData.ts)
- [web/src/lib/llmd/nightlyE2EDemoData.ts](web/src/lib/llmd/nightlyE2EDemoData.ts)

</details>



## Purpose and Scope

The Nightly E2E Monitoring system tracks the health of end-to-end workflow runs from GitHub Actions for the `llm-d` project. It monitors 18 workflows across three Kubernetes platforms (OCP, GKE, CKS), provides pass/fail history visualization, classifies failure causes (GPU unavailability vs. test failures), and offers AI-powered diagnosis of failed runs.

This system is specific to llm-d project monitoring. For general CI/CD automation workflows in the KubeStellar Console itself, see [CI/CD Automation System](#7). For analytics tracking of user interactions, see [Analytics System](#11).

---

## Monitored Workflows

The system tracks 18 nightly E2E workflows across three platforms, with each workflow corresponding to a specific llm-d guide. Workflows are defined in both the Go backend and TypeScript implementations to ensure consistency.

### Workflow Configuration Structure

```mermaid
graph TB
    subgraph "Platform: OCP"
        OCP1["IS (Inference Scheduling)<br/>Qwen3-32B, 2×H100"]
        OCP2["PD (PD Disaggregation)<br/>Qwen3-0.6B, 2×H100"]
        OCP3["PPC (Precise Prefix Cache)<br/>Qwen3-32B, 2×H100"]
        OCP4["SA (Simulated Accelerators)<br/>Simulated, CPU"]
        OCP5["TPC (Tiered Prefix Cache)<br/>Qwen3-0.6B, 1×H100"]
        OCP6["WEP (Wide EP + LWS)<br/>Qwen3-0.6B, 2×H100"]
        OCP7["WVA (WVA)<br/>Llama-3.1-8B, 2×A100"]
        OCP8["BM (Benchmarking)<br/>opt-125m, 1×A100"]
    end
    
    subgraph "Platform: GKE"
        GKE1["IS (Inference Scheduling)<br/>Qwen3-32B, 2×L4"]
        GKE2["PD (PD Disaggregation)<br/>Qwen3-0.6B, 2×L4"]
        GKE3["WEP (Wide EP + LWS)<br/>Qwen3-0.6B, 2×L4"]
        GKE4["BM (Benchmarking)<br/>opt-125m, 1×L4"]
    end
    
    subgraph "Platform: CKS"
        CKS1["IS (Inference Scheduling)<br/>Qwen3-32B, 2×H100"]
        CKS2["PD (PD Disaggregation)<br/>Qwen3-0.6B, 2×H100"]
        CKS3["WEP (Wide EP + LWS)<br/>Qwen3-0.6B, 2×H100"]
        CKS4["WVA (WVA)<br/>Llama-3.1-8B, 2×H100"]
        CKS5["BM (Benchmarking)<br/>opt-125m, 1×H100"]
    end
```

Each workflow definition includes:

| Field | Description | Example |
|-------|-------------|---------|
| `repo` | GitHub repository | `"llm-d/llm-d"` |
| `workflowFile` | YAML filename in `.github/workflows/` | `"nightly-e2e-inference-scheduling-ocp.yaml"` |
| `guide` | Human-readable guide name | `"Inference Scheduling"` |
| `acronym` | Short identifier for UI display | `"IS"` |
| `platform` | Kubernetes platform | `"OCP"`, `"GKE"`, or `"CKS"` |
| `model` | LLM model being tested | `"Qwen3-32B"`, `"Llama-3.1-8B"` |
| `gpuType` | GPU hardware type | `"H100"`, `"A100"`, `"L4"`, `"CPU"` |
| `gpuCount` | Number of GPUs required | `0`, `1`, or `2` |

Sources: [pkg/api/handlers/nightly_e2e.go:111-132](), [web/src/lib/llmd/nightlyE2EDemoData.ts:49-70](), [web/netlify/functions/nightly-e2e.mts:75-96]()

---

## System Architecture

### Data Flow Overview

```mermaid
graph TB
    UI["NightlyE2EStatus Component"]
    Hook["useNightlyE2EData Hook"]
    Cache["useCache Layer<br/>localStorage persistence"]
    
    subgraph "Backend Options"
        GoAPI["Go Backend<br/>/api/nightly-e2e/runs<br/>/api/public/nightly-e2e/runs"]
        NetlifyFn["Netlify Function<br/>/.netlify/functions/nightly-e2e"]
    end
    
    subgraph "Data Sources"
        GitHubAPI["GitHub Actions API<br/>workflow_runs endpoint<br/>jobs endpoint"]
        DemoData["Demo Data Generator<br/>generateDemoNightlyData()"]
    end
    
    subgraph "Storage Layers"
        MemCache["Go In-Memory Cache<br/>NightlyE2EHandler.cache"]
        BlobStore["Netlify Blob Store<br/>getStore('nightly-e2e')"]
        LSCache["localStorage<br/>'nightly-e2e-cache'"]
    end
    
    UI --> Hook
    Hook --> Cache
    Cache --> LSCache
    Cache --> GoAPI
    Cache --> NetlifyFn
    
    GoAPI --> MemCache
    NetlifyFn --> BlobStore
    
    MemCache --> GitHubAPI
    BlobStore --> GitHubAPI
    
    Hook --> DemoData
    
    GoAPI --> GitHubAPI
    NetlifyFn --> GitHubAPI
```

The system implements a **three-tier fallback strategy**:

1. **Primary**: Fetch from backend API (`/api/nightly-e2e/runs` with auth, then `/api/public/nightly-e2e/runs` fallback)
2. **Cache**: Use localStorage-persisted data from previous successful fetch
3. **Demo Mode**: Generate realistic mock data when backend is unavailable

Sources: [web/src/hooks/useNightlyE2EData.ts:61-162](), [pkg/api/handlers/nightly_e2e.go:95-107]()

### Cache TTL Strategy

The system uses **adaptive cache TTL** based on job status:

| Condition | TTL | Rationale |
|-----------|-----|-----------|
| Jobs in progress | 2 minutes | Frequent updates needed during active runs |
| All jobs idle | 5 minutes | Reduce API calls when no activity |

```mermaid
graph LR
    Fetch["Fetch All Workflows"]
    Check{"Any jobs<br/>in_progress?"}
    Active["Set TTL = 2 min<br/>CACHE_ACTIVE_TTL_MS"]
    Idle["Set TTL = 5 min<br/>CACHE_IDLE_TTL_MS"]
    Store["Update Cache<br/>Set expiration"]
    
    Fetch --> Check
    Check -->|Yes| Active
    Check -->|No| Idle
    Active --> Store
    Idle --> Store
```

The `hasInProgressRuns()` function scans all guide runs for `status === "in_progress"` to determine which TTL to apply.

Sources: [pkg/api/handlers/nightly_e2e.go:17-18](), [pkg/api/handlers/nightly_e2e.go:607-616](), [web/netlify/functions/nightly-e2e.mts:15-16](), [web/netlify/functions/nightly-e2e.mts:130-134]()

---

## Backend Implementation

### Go Handler Structure

The `NightlyE2EHandler` manages GitHub API integration with concurrent fetching and failure classification.

```mermaid
graph TB
    Handler["NightlyE2EHandler"]
    
    subgraph "Handler Fields"
        Token["githubToken<br/>string"]
        Client["httpClient<br/>*http.Client<br/>30s timeout"]
        Lock["mu<br/>sync.RWMutex"]
        CacheData["cache<br/>*NightlyE2EResponse"]
        CacheExp["cacheExp<br/>time.Time"]
        LogLock["logMu<br/>sync.RWMutex"]
        LogCache["logCache<br/>map[string]*RunLogsResponse"]
        LogExp["logCacheExp<br/>map[string]time.Time"]
    end
    
    subgraph "API Endpoints"
        GetRuns["GetRuns(c *fiber.Ctx)<br/>Returns aggregated status"]
        GetLogs["GetRunLogs(c *fiber.Ctx)<br/>Fetches job logs"]
    end
    
    subgraph "Internal Methods"
        FetchAll["fetchAll()<br/>Parallel workflow fetch"]
        FetchWF["fetchWorkflowRuns(wf)<br/>Single workflow fetch"]
        Classify["classifyFailures(repo, runs)<br/>GPU vs test failure"]
        Detect["detectGPUFailure(repo, runID)<br/>Step analysis"]
        FetchLog["fetchJobLog(repo, jobID)<br/>Tail 200KB"]
    end
    
    Handler --> Token
    Handler --> Client
    Handler --> Lock
    Handler --> CacheData
    Handler --> CacheExp
    Handler --> LogLock
    Handler --> LogCache
    Handler --> LogExp
    
    GetRuns --> FetchAll
    FetchAll --> FetchWF
    FetchWF --> Classify
    Classify --> Detect
    
    GetLogs --> FetchLog
```

### Concurrent Fetching Pattern

The backend fetches all 18 workflows in parallel using goroutines with a result collection channel:

```mermaid
sequenceDiagram
    participant Client as HTTP Client
    participant Handler as fetchAll()
    participant Ch as Result Channel
    participant G1 as Goroutine 1
    participant G18 as Goroutine 18
    participant GitHub as GitHub API
    
    Client->>Handler: GET /api/nightly-e2e/runs
    Handler->>Ch: Create buffered channel (len 18)
    
    par Parallel Fetch
        Handler->>G1: Launch fetchWorkflowRuns(wf[0])
        Handler->>G18: Launch fetchWorkflowRuns(wf[17])
    end
    
    G1->>GitHub: GET /repos/.../actions/workflows/.../runs
    G18->>GitHub: GET /repos/.../actions/workflows/.../runs
    
    GitHub-->>G1: workflow_runs JSON
    GitHub-->>G18: workflow_runs JSON
    
    G1->>G1: classifyFailures(runs)
    G18->>G18: classifyFailures(runs)
    
    G1->>Ch: result{idx: 0, runs: [...]}
    G18->>Ch: result{idx: 17, runs: [...]}
    
    Handler->>Handler: Collect all 18 results
    Handler->>Handler: Build NightlyGuideStatus[]
    Handler-->>Client: JSON response
```

This pattern ensures that slow workflows (404s, network delays) don't block fast ones. Each goroutine writes its result to the channel independently.

Sources: [pkg/api/handlers/nightly_e2e.go:198-259]()

### GitHub API Integration

The handler makes authenticated requests to three GitHub API endpoints:

| Endpoint | Purpose | Response Fields |
|----------|---------|----------------|
| `/repos/{repo}/actions/workflows/{file}/runs` | List recent runs | `id`, `status`, `conclusion`, `created_at`, `updated_at`, `run_number` |
| `/repos/{repo}/actions/runs/{runId}/jobs` | List jobs for failure classification | `jobs[].steps[].name`, `jobs[].steps[].conclusion` |
| `/repos/{repo}/actions/jobs/{jobId}/logs` | Fetch plain-text logs | Raw log output (text/plain) |

The GitHub token is passed via `Authorization: Bearer {token}` header. On Netlify deployments, the token is stored as an environment variable accessible only to serverless functions (never exposed to client).

Sources: [pkg/api/handlers/nightly_e2e.go:261-330](), [pkg/api/handlers/nightly_e2e.go:349-394](), [pkg/api/handlers/nightly_e2e.go:508-556]()

---

## Failure Classification

### GPU Unavailability Detection

The system distinguishes between two failure types to provide actionable intelligence:

1. **GPU Unavailable** (`gpu_unavailable`): Infrastructure issue, not a test regression
2. **Test Failure** (`test_failure`): Actual test failure requiring investigation

```mermaid
graph TD
    Run["Workflow Run<br/>conclusion=failure"]
    FetchJobs["Fetch jobs for run<br/>GET /actions/runs/{id}/jobs"]
    Jobs["jobs[] array"]
    
    IterateJobs{"For each job"}
    Steps["job.steps[] array"]
    
    IterateSteps{"For each step"}
    CheckFail{"step.conclusion<br/>== failure?"}
    CheckGPU{"isGPUStep(step.name)?<br/>Contains 'gpu' AND 'availab'"}
    
    GPUFail["Return<br/>gpu_unavailable"]
    TestFail["Return<br/>test_failure"]
    
    Run --> FetchJobs
    FetchJobs --> Jobs
    Jobs --> IterateJobs
    IterateJobs -->|Next| Steps
    Steps --> IterateSteps
    IterateSteps -->|Next| CheckFail
    CheckFail -->|No| IterateSteps
    CheckFail -->|Yes| CheckGPU
    CheckGPU -->|Yes| GPUFail
    CheckGPU -->|No| IterateSteps
    IterateJobs -->|Done| TestFail
```

The `isGPUStep()` function checks if a step name contains both "gpu" and "availab" (case-insensitive), matching step names like:
- "Check GPU Availability"
- "Wait for GPU resources"
- "Verify GPU node available"

This classification enables the UI to display amber dots for infrastructure issues vs. red dots for test regressions.

Sources: [pkg/api/handlers/nightly_e2e.go:333-394](), [pkg/api/handlers/nightly_e2e.go:396-400]()

---

## Frontend Implementation

### Component Hierarchy

```mermaid
graph TB
    Card["NightlyE2EStatus<br/>Main card component"]
    
    subgraph "Top-Level Stats"
        StatBoxes["Stat boxes<br/>Overall pass rate, guide count"]
    end
    
    subgraph "Left Column: Guide List"
        PlatformGroups["Platform groups<br/>OCP, GKE, CKS"]
        GuideRow["GuideRow<br/>Per-guide status"]
        RunDot["RunDot<br/>Individual run status"]
    end
    
    subgraph "Right Panel: Details"
        Summary["NightlySummaryPanel<br/>AI-generated summary"]
        Details["GuideDetailPanel<br/>Selected guide stats"]
        Sparkline["TrendSparkline<br/>Pass/fail trend chart"]
    end
    
    subgraph "Interactive Elements"
        Popup["Hover popup<br/>Failure details"]
        DiagnoseBtn["AI Diagnose button"]
        KeyPrompt["ApiKeyPromptModal"]
    end
    
    Card --> StatBoxes
    Card --> PlatformGroups
    Card --> Summary
    Card --> Details
    
    PlatformGroups --> GuideRow
    GuideRow --> RunDot
    
    Details --> Sparkline
    
    RunDot --> Popup
    Popup --> DiagnoseBtn
    DiagnoseBtn --> KeyPrompt
```

### Data Hook Flow

The `useNightlyE2EData` hook implements a layered fetch strategy with localStorage persistence:

```mermaid
sequenceDiagram
    participant Component as NightlyE2EStatus
    participant Hook as useNightlyE2EData
    participant Cache as useCache
    participant LS as localStorage
    participant API as Backend API
    participant Demo as Demo Generator
    
    Component->>Hook: Call hook
    Hook->>LS: Load 'nightly-e2e-cache'
    LS-->>Hook: Cached guides[] or null
    Hook->>Cache: useCache({initialData, demoData, fetcher})
    
    Cache->>Component: Return cached data + isLoading=false
    
    par Background Refresh
        Cache->>API: fetch('/api/nightly-e2e/runs')
        alt Success
            API-->>Cache: {guides, cachedAt}
            Cache->>LS: Save to localStorage
            Cache->>Component: Update with fresh data
        else API Unavailable
            API-->>Cache: Network error
            Cache->>Demo: generateDemoNightlyData()
            Demo-->>Cache: Demo guides[]
            Cache->>Component: Update with demo data
        end
    end
```

The hook uses `loadCachedData()` at module level to provide synchronous initial data, avoiding loading states when localStorage contains recent data.

Sources: [web/src/hooks/useNightlyE2EData.ts:34-59](), [web/src/hooks/useNightlyE2EData.ts:61-162]()

### Run Status Visualization

Each workflow run is displayed as a colored dot with status-based styling:

| Status | Conclusion | Color | Visual Effect | Meaning |
|--------|-----------|-------|---------------|---------|
| `in_progress` | - | Blue (`bg-blue-400`) | Pulsing animation | Currently running |
| `completed` | `success` | Green (`bg-emerald-400`) | Static | Passed |
| `completed` | `failure` + `gpu_unavailable` | Amber (`bg-amber-400`) | Static | GPU unavailable |
| `completed` | `failure` | Red (`bg-red-400`) | Static | Test failed |
| `completed` | `cancelled` | Slate (`bg-slate-500`) | Static | Manually cancelled |

The `RunDot` component handles hover interactions, showing a popup with failure details and an "AI Diagnose" button for failed runs.

Sources: [web/src/components/cards/llmd/NightlyE2EStatus.tsx:69-251]()

### AI Summary Generation

The `generateNightlySummary()` function produces two-paragraph summaries using pattern detection:

**Paragraph 1: Overall Health**
- Total active guides and pass rate across platforms
- Per-platform breakdown (pass/fail counts, trending info)
- Infrastructure context (models tested, GPU types, average duration)
- GPU failure count (amber dots)

**Paragraph 2: Notable Patterns**
- Best performer (highest pass rate)
- Worst performer (0% with 3+ runs)
- Slowest guide (>1.5× average duration)
- Consecutive streaks (3+ passes/failures)
- Currently running guides

Example output:
> "Across 12 active guides, 10 are currently passing with an average pass rate of 87%. Tests average 42m to complete exercising 3 models (Qwen3-32B, Qwen3-0.6B, Llama-3.1-8B) across 18 H100/L4/A100 GPUs. OCP has 7/8 guides passing (avg 85%) with 1 trending upward. GKE is fully green with all 4 guides passing (avg 95%). 2 recent failures were due to GPU unavailability (shown in amber)."

Sources: [web/src/components/cards/llmd/NightlyE2EStatus.tsx:422-567]()

---

## AI Diagnosis Integration

### Triggering Diagnosis

When a user clicks "AI Diagnose" on a failed run, the system:

1. Checks for API key via `useApiKeyCheck()` hook
2. Fetches job logs from `/api/public/nightly-e2e/run-logs?repo={repo}&runId={id}`
3. Launches a mission via `startMission()` with enriched context

```mermaid
sequenceDiagram
    participant User
    participant RunDot
    participant KeyCheck as useApiKeyCheck
    participant LogAPI as /api/public/nightly-e2e/run-logs
    participant Mission as useMissions
    
    User->>RunDot: Click "AI Diagnose"
    RunDot->>KeyCheck: checkKeyAndRun(async fn)
    
    alt No API Key
        KeyCheck-->>RunDot: Show ApiKeyPromptModal
        User->>KeyCheck: Go to Settings or Dismiss
    else API Key Present
        KeyCheck->>LogAPI: fetch(repo, runId)
        LogAPI-->>KeyCheck: {jobs: [{name, conclusion, log}]}
        
        KeyCheck->>Mission: startMission({<br/>  title: "Diagnose IS (OCP) Run #42",<br/>  type: "troubleshoot",<br/>  initialPrompt: "...",<br/>  context: {...}<br/>})
        
        Mission-->>User: Open mission panel with AI analysis
    end
```

### Log Fetching for Diagnosis

The `/api/public/nightly-e2e/run-logs` endpoint fetches logs for all failed jobs in a run:

1. Query GitHub API for jobs list (`/actions/runs/{id}/jobs`)
2. Filter to jobs with `conclusion === "failure"`
3. Fetch logs concurrently (limit 5 parallel requests via semaphore)
4. Truncate each log to last 200KB (failure info is at tail)
5. Return JSON with job name, conclusion, and log text

The log cache persists for 10 minutes since logs are immutable once a run completes.

Sources: [pkg/api/handlers/nightly_e2e.go:405-504](), [web/src/components/cards/llmd/NightlyE2EStatus.tsx:136-194]()

### Mission Prompt Structure

The AI prompt includes structured context for accurate diagnosis:

```typescript
initialPrompt: `Analyze this failed nightly E2E workflow run and diagnose the root cause.

## Run Context
- Guide: ${guide.guide} (${guide.acronym}) on ${guide.platform}
- Repository: ${guide.repo}
- Workflow: ${guide.workflowFile}
- Run #: ${run.runNumber}
- Failure Reason: ${run.failureReason || 'unknown'}
- Model: ${run.model}, GPU: ${run.gpuCount}x ${run.gpuType}
- GitHub URL: ${run.htmlUrl}

## GitHub Actions Logs
${logsContent}

Please provide:
1. Root cause analysis
2. Classification (test flake, infra issue, GPU problem, code regression)
3. Suggested fix
4. Pattern detection (recurring issue?)`
```

This structured prompt enables the AI to provide actionable recommendations with proper context about the infrastructure environment.

Sources: [web/src/components/cards/llmd/NightlyE2EStatus.tsx:164-183]()

---

## Demo Mode Implementation

### Demo Data Generation

When the backend is unavailable (Netlify preview deployments without GitHub token, local dev without agent), the system generates realistic demo data:

```mermaid
graph TB
    Generate["generateDemoNightlyData()"]
    
    subgraph "For each workflow"
        LoadPattern["Load pattern from<br/>DEMO_PATTERNS map"]
        CreateRuns["Create 7 runs with<br/>24-hour spacing"]
        
        subgraph "Per Run"
            CalcTime["createdAt = now - (i × 24h)<br/>2am each night"]
            SetStatus["status = pattern[i]<br/>(success/failure/in_progress)"]
            CalcDuration["duration = 30-60 min random"]
            SetMeta["Copy model/GPU from workflow"]
        end
    end
    
    ComputeStats["Compute passRate and trend"]
    Return["Return NightlyGuideStatus[]"]
    
    Generate --> LoadPattern
    LoadPattern --> CreateRuns
    CreateRuns --> CalcTime
    CalcTime --> SetStatus
    SetStatus --> CalcDuration
    CalcDuration --> SetMeta
    SetMeta --> ComputeStats
    ComputeStats --> Return
```

Demo patterns are hardcoded to show realistic scenarios:
- **Stable guides**: All passes (e.g., "PD Disaggregation-OCP")
- **Flaky guides**: Mixed passes/failures (e.g., "WVA-OCP")
- **Regressed guides**: Recent failures (e.g., "Benchmarking-OCP")
- **Running jobs**: Latest run in `in_progress` state (e.g., "Wide EP + LWS-OCP")
- **New workflows**: Empty runs array (CKS platform, no data yet)

This ensures the UI renders correctly in preview deployments without requiring GitHub access.

Sources: [web/src/lib/llmd/nightlyE2EDemoData.ts:73-151]()

### Demo Mode Detection

The hook uses `isDemoFallback` to track whether demo data is being used:

```typescript
isDemoFallback: cacheResult.isLoading ? false : isDemo
```

The loading check prevents showing the "Demo" badge during cache hydration, which would be misleading when real cached data exists. The badge only appears after loading completes and demo data is confirmed as the source.

Sources: [web/src/hooks/useNightlyE2EData.ts:155]()

---

## Card Configuration

The card is registered in the unified card system with the following configuration:

```typescript
{
  type: 'nightly_e2e_status',
  title: 'Nightly E2E Status',
  category: 'ci-cd',
  description: 'llm-d nightly E2E workflow status across OCP and GKE platforms',
  icon: 'TestTube2',
  iconColor: 'text-emerald-400',
  defaultWidth: 12,    // Full width (12/12 grid columns)
  defaultHeight: 5,    // Tall card to show all platforms
  dataSource: { type: 'hook', hook: 'useNightlyE2EData' },
  content: { type: 'custom', component: 'NightlyE2EStatusView' },
  emptyState: { 
    icon: 'TestTube2', 
    title: 'No E2E Data', 
    message: 'Configure a GitHub token to see nightly E2E status', 
    variant: 'info' 
  },
  loadingState: { type: 'custom' },
  isDemoData: false,
  isLive: true,
}
```

The card uses a custom loading state that shows skeleton rows for guide entries and stats boxes, maintaining the expected layout during data fetch.

Sources: [web/src/config/cards/nightly-e2e-status.ts:1-23]()

---

## Deployment Variations

### Go Backend Deployment

Standard deployment using the Go Fiber server:

- **Endpoint**: `/api/nightly-e2e/runs` (authenticated), `/api/public/nightly-e2e/runs` (public fallback)
- **Cache**: In-memory `sync.RWMutex`-protected map
- **Token**: Read from `GITHUB_TOKEN` environment variable at startup
- **Prewarm**: Background goroutine populates cache on handler initialization

### Netlify Serverless Deployment

Edge deployment using Netlify Functions:

- **Endpoint**: `/.netlify/functions/nightly-e2e`
- **Cache**: Netlify Blob Store (`getStore('nightly-e2e')`)
- **Token**: Read from `process.env.GITHUB_TOKEN` (runtime only, Functions scope)
- **Cold Start**: First request triggers full fetch, subsequent requests use blob cache

Both implementations share identical logic for workflow fetching, failure classification, and trend computation, with only the cache storage mechanism differing.

Sources: [pkg/api/handlers/nightly_e2e.go:95-196](), [web/netlify/functions/nightly-e2e.mts:279-357]()

---

