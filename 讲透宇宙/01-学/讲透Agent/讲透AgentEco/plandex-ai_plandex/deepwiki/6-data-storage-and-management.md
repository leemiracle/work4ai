<!-- source: DeepWiki mcp.deepwiki.com · repo plandex-ai/plandex · page 6 Data Storage and Management · fetched 2026-10-27 -->

# Data Storage and Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/server/db/db.go](app/server/db/db.go)
- [app/server/db/git.go](app/server/db/git.go)
- [app/server/db/locks.go](app/server/db/locks.go)
- [app/server/model/plan/state.go](app/server/model/plan/state.go)
- [app/server/model/plan/stop.go](app/server/model/plan/stop.go)
- [app/shared/plan_model_settings.go](app/shared/plan_model_settings.go)
- [releases/cli/versions/0.8.3.md](releases/cli/versions/0.8.3.md)
- [releases/server/versions/0.8.4.md](releases/server/versions/0.8.4.md)
- [releases/server/versions/2.1.3.md](releases/server/versions/2.1.3.md)

</details>



This page covers Plandex's data storage architecture, including database management, repository locking mechanisms, Git integration, and in-memory state management. It documents the persistence layer, concurrency control systems, and data serialization patterns that support plan execution and file management.

For information about API data models and request handling, see [Data Models and Shared Types](#4.2). For database schema details and migrations, see [Database Schema and Migrations](#6.1).

## Storage Architecture Overview

Plandex employs a multi-layered storage architecture combining PostgreSQL for persistent data, Git repositories for version control, and sophisticated in-memory state management for active operations.

### Storage Systems Diagram

```mermaid
graph TB
    subgraph "Client_Requests"
        APIRequest["API Request"]
    end
    
    subgraph "Server_Storage_Layer"
        PostgreSQL[("PostgreSQL Database")]
        GitRepos[("Git Repositories")]
        FileSystem[("Local File System")]
        InMemoryState["activePlans SafeMap"]
    end
    
    subgraph "Data_Management_Components"
        DBConn["db.Conn (*sqlx.DB)"]
        RepoLocks["Repository Locks System"]
        GitOps["Git Operations (GitRepo)"]
        ActivePlanMgr["Active Plan Manager"]
    end
    
    subgraph "Concurrency_Control"
        LockScope["LockScope (Read/Write)"]
        Heartbeat["Lock Heartbeat System"]
        RetryLogic["Exponential Backoff Retry"]
    end
    
    APIRequest --> DBConn
    APIRequest --> ActivePlanMgr
    
    DBConn --> PostgreSQL
    ActivePlanMgr --> InMemoryState
    
    RepoLocks --> PostgreSQL
    GitOps --> GitRepos
    GitOps --> FileSystem
    
    RepoLocks --> LockScope
    RepoLocks --> Heartbeat
    RepoLocks --> RetryLogic
    
    ActivePlanMgr --> GitOps
    ActivePlanMgr --> RepoLocks
    
    style PostgreSQL fill:#f9f
    style GitRepos fill:#9f9
    style InMemoryState fill:#99f
```

Sources: [app/server/db/db.go:18-94](), [app/server/db/locks.go:38-53](), [app/server/model/plan/state.go:17-19](), [app/server/db/git.go:32-40]()

## Database Connection and Configuration

The database layer centers around a global `*sqlx.DB` connection with specific PostgreSQL optimizations for concurrent operations.

### Database Connection Management

```mermaid
graph TB
    subgraph "Connection_Setup"
        EnvVars["Environment Variables"]
        ConnString["Connection String Builder"]
        SqlxDB["db.Conn (*sqlx.DB)"]
    end
    
    subgraph "Connection_Config"
        Timeouts["Timeout Settings"]
        PoolSettings["Connection Pool"]
        PGSettings["PostgreSQL Settings"]
    end
    
    subgraph "Migration_System"
        MigrateInstance["migrate.NewWithDatabaseInstance"]
        MigrationFiles["file://migrations"]
        MigrationUp["m.Up()"]
    end
    
    EnvVars --> ConnString
    ConnString --> SqlxDB
    SqlxDB --> Timeouts
    SqlxDB --> PoolSettings
    SqlxDB --> PGSettings
    
    SqlxDB --> MigrateInstance
    MigrationFiles --> MigrateInstance
    MigrateInstance --> MigrationUp
    
    style SqlxDB fill:#f9f
```

| Configuration Parameter | Production Value | Development Value | Purpose |
|------------------------|------------------|-------------------|---------|
| `StatementTimeout` | 30000ms | 30000ms | Query execution limit |
| `LockTimeout` | 4000ms | 4000ms | Row-level lock timeout |
| `IdleInTransactionSessionTimeout` | 90000ms | 90000ms | Idle transaction cleanup |
| `MaxOpenConns` | 50 | 10 | Connection pool size |
| `MaxIdleConns` | 20 | 5 | Idle connection limit |

The connection initialization includes automatic timezone setting to UTC and comprehensive timeout configuration to prevent hanging transactions during concurrent operations.

Sources: [app/server/db/db.go:20-94](), [app/server/db/db.go:96-175]()

## Repository Locking System

Plandex implements a sophisticated distributed locking mechanism to prevent concurrent modifications to Git repositories during plan execution.

### Lock Types and Scopes

```mermaid
graph TB
    subgraph "Lock_Scopes"
        ReadLock["LockScopeRead"]
        WriteLock["LockScopeWrite"]
    end
    
    subgraph "Lock_Conflicts"
        ReadRead["Read + Read: Allowed (same branch)"]
        ReadWrite["Read + Write: Blocked"]
        WriteWrite["Write + Write: Blocked"]
        ReadReadDiff["Read + Read: Blocked (different branch)"]
    end
    
    subgraph "Lock_Management"
        LockParams["LockRepoParams"]
        HeartbeatSys["Heartbeat System"]
        ExpiredCleanup["Expired Lock Cleanup"]
    end
    
    ReadLock --> ReadRead
    ReadLock --> ReadWrite
    WriteLock --> ReadWrite
    WriteLock --> WriteWrite
    ReadLock --> ReadReadDiff
    
    LockParams --> HeartbeatSys
    HeartbeatSys --> ExpiredCleanup
    
    style WriteLock fill:#fcc
    style ReadLock fill:#cfc
```

The `LockRepoParams` struct defines the complete context for lock acquisition:

| Field | Purpose |
|-------|---------|
| `OrgId` | Organization scope |
| `UserId` | User identification |
| `PlanId` | Plan identifier |
| `Branch` | Git branch target |
| `Scope` | Read or write lock |
| `PlanBuildId` | Build operation context |
| `Reason` | Debug logging context |

Sources: [app/server/db/locks.go:41-52](), [app/server/db/locks.go:249-278]()

### Lock Acquisition and Retry Logic

```mermaid
graph TB
    subgraph "Lock_Acquisition_Flow"
        StartLock["lockRepoDB()"]
        BeginTx["Begin RepeatableRead Tx"]
        SelectForUpdate["SELECT ... FOR UPDATE/SHARE"]
        CheckConflicts["Check Existing Locks"]
        InsertLock["INSERT new lock"]
        CommitTx["Commit Transaction"]
        StartHeartbeat["Start Heartbeat Goroutine"]
    end
    
    subgraph "Retry_Logic"
        RetryCheck{"Retry Needed?"}
        ExponentialBackoff["Exponential Backoff"]
        MaxRetries{"< maxLockRetries?"}
        RetryAttempt["Retry Attempt"]
    end
    
    subgraph "Heartbeat_System"
        HeartbeatLoop["Heartbeat Loop"]
        UpdateTimestamp["UPDATE last_heartbeat_at"]
        CheckHeartbeat{"Heartbeat Success?"}
        CancelOnFailure["Cancel Context"]
    end
    
    StartLock --> BeginTx
    BeginTx --> SelectForUpdate
    SelectForUpdate --> CheckConflicts
    CheckConflicts --> InsertLock
    InsertLock --> CommitTx
    CommitTx --> StartHeartbeat
    
    CheckConflicts -->|Conflict| RetryCheck
    RetryCheck --> ExponentialBackoff
    ExponentialBackoff --> MaxRetries
    MaxRetries -->|Yes| RetryAttempt
    RetryAttempt --> StartLock
    
    StartHeartbeat --> HeartbeatLoop
    HeartbeatLoop --> UpdateTimestamp
    UpdateTimestamp --> CheckHeartbeat
    CheckHeartbeat -->|Failure| CancelOnFailure
    CheckHeartbeat -->|Success| HeartbeatLoop
    
    style RetryAttempt fill:#ffa
    style CancelOnFailure fill:#fcc
```

The retry mechanism uses exponential backoff with jitter to handle lock contention:

- **Initial retry delay**: 300ms
- **Backoff factor**: 2x
- **Jitter**: ±30%
- **Maximum retries**: 6 attempts
- **Delete retries**: 60 attempts with 50ms delay

Sources: [app/server/db/locks.go:54-290](), [app/server/db/locks.go:564-611]()

### Heartbeat and Lock Lifecycle

```mermaid
sequenceDiagram
    participant Client as "Plan Execution"
    participant LockSys as "Lock System"
    participant DB as "PostgreSQL"
    participant Heartbeat as "Heartbeat Goroutine"
    
    Client->>LockSys: lockRepoDB(params)
    LockSys->>DB: BEGIN TRANSACTION
    LockSys->>DB: SELECT FOR UPDATE/SHARE
    LockSys->>DB: INSERT new lock
    LockSys->>DB: COMMIT
    LockSys->>Client: Return lock ID
    
    par Lock Usage
        Client->>Client: Perform Git operations
    and Heartbeat Loop
        loop Every 3 seconds
            Heartbeat->>DB: UPDATE last_heartbeat_at
            DB-->>Heartbeat: Rows affected check
            alt Lock exists
                Heartbeat->>Heartbeat: Continue heartbeat
            else Lock gone
                Heartbeat->>Heartbeat: Stop heartbeat
            end
        end
    end
    
    Client->>LockSys: Release lock
    LockSys->>DB: DELETE FROM repo_locks
    LockSys->>Heartbeat: Context cancellation
```

The heartbeat system maintains lock validity through regular database updates every 3 seconds, with a 60-second timeout for abandoned locks.

Sources: [app/server/db/locks.go:387-457](), [app/server/db/locks.go:480-521]()

## Git Integration and File Management

The Git integration layer provides version control operations with comprehensive lock file handling and retry mechanisms for concurrent access.

### GitRepo Operations

```mermaid
graph TB
    subgraph "GitRepo_Structure"
        GitRepo["GitRepo struct"]
        OrgId["orgId string"]
        PlanId["planId string"]
        PlanDir["getPlanDir()"]
    end
    
    subgraph "Core_Operations"
        GitAdd["GitAddAndCommit()"]
        GitCheckout["GitCheckoutBranch()"]
        GitReset["GitResetToSha()"]
        GitRewind["GitRewindToSha()"]
        GitClean["GitClearUncommittedChanges()"]
    end
    
    subgraph "State_Operations"
        GetCommitSha["GetCurrentCommitSha()"]
        GetHistory["GetGitCommitHistory()"]
        ListBranches["GitListBranches()"]
        CreateBranch["GitCreateBranch()"]
    end
    
    subgraph "Lock_File_Management"
        RemoveLockFiles["gitRemoveIndexLockFileIfExists()"]
        LockPaths["index.lock, HEAD.lock paths"]
        RetryRemoval["Retry lock removal"]
    end
    
    GitRepo --> OrgId
    GitRepo --> PlanId
    PlanDir --> GitAdd
    PlanDir --> GitCheckout
    
    GitAdd --> RemoveLockFiles
    GitCheckout --> RemoveLockFiles
    GitReset --> RemoveLockFiles
    
    RemoveLockFiles --> LockPaths
    RemoveLockFiles --> RetryRemoval
    
    style RemoveLockFiles fill:#ffa
```

All Git write operations are wrapped in `gitWriteOperation()` which provides automatic retry logic for lock file conflicts and exponential backoff for transient failures.

Sources: [app/server/db/git.go:32-65](), [app/server/db/git.go:655-684](), [app/server/db/git.go:604-645]()

### Git Lock File Handling

```mermaid
graph TB
    subgraph "Lock_File_Types"
        IndexLock[".git/index.lock"]
        HeadLock[".git/HEAD.lock"]
        RefHeadLock[".git/refs/heads/HEAD.lock"]
    end
    
    subgraph "Removal_Process"
        CheckExists["os.Stat() check"]
        ParallelRemoval["Parallel goroutines"]
        RetryLoop["Retry up to 10 times"]
        DelayBetween["20ms delay between attempts"]
    end
    
    subgraph "Error_Handling"
        NotExistOK["os.IsNotExist() → OK"]
        OtherErrors["Log other errors"]
        PanicRecovery["Panic recovery"]
    end
    
    IndexLock --> CheckExists
    HeadLock --> CheckExists
    RefHeadLock --> CheckExists
    
    CheckExists --> ParallelRemoval
    ParallelRemoval --> RetryLoop
    RetryLoop --> DelayBetween
    
    ParallelRemoval --> NotExistOK
    ParallelRemoval --> OtherErrors
    ParallelRemoval --> PanicRecovery
    
    style PanicRecovery fill:#fcc
```

The lock file removal system uses parallel goroutines to handle multiple lock file types simultaneously, with comprehensive error handling for race conditions.

Sources: [app/server/db/git.go:604-645](), [app/server/db/git.go:557-602]()

## In-Memory State Management

Active plan state is managed through a thread-safe map structure that coordinates real-time plan execution and client subscriptions.

### Active Plan Lifecycle

```mermaid
graph TB
    subgraph "Plan_State_Map"
        SafeMap["activePlans SafeMap[*ActivePlan]"]
        PlanKey["planId|branch key"]
        ActivePlan["types.ActivePlan"]
    end
    
    subgraph "Plan_Creation"
        CreateActive["CreateActivePlan()"]
        NewActivePlan["types.NewActivePlan()"]
        SetInMap["activePlans.Set()"]
        StartGoroutine["State monitoring goroutine"]
    end
    
    subgraph "State_Monitoring"
        ContextDone["<-activePlan.Ctx.Done()"]
        StreamDone["<-activePlan.StreamDoneCh"]
        SetStopped["SetPlanStatus(Stopped)"]
        SetFinished["SetPlanStatus(Finished)"]
        SetError["SetPlanStatus(Error)"]
    end
    
    subgraph "Plan_Cleanup"
        DeleteActive["DeleteActivePlan()"]
        ClearChanges["GitClearUncommittedChanges()"]
        RemoveFromMap["activePlans.Delete()"]
    end
    
    CreateActive --> NewActivePlan
    NewActivePlan --> SetInMap
    SetInMap --> StartGoroutine
    
    StartGoroutine --> ContextDone
    StartGoroutine --> StreamDone
    ContextDone --> SetStopped
    StreamDone --> SetFinished
    StreamDone --> SetError
    
    SetStopped --> DeleteActive
    SetFinished --> DeleteActive
    SetError --> DeleteActive
    
    DeleteActive --> ClearChanges
    ClearChanges --> RemoveFromMap
    
    style SetError fill:#fcc
    style DeleteActive fill:#ffa
```

The `SafeMap` provides thread-safe operations for the global `activePlans` registry, enabling concurrent access from multiple request handlers while maintaining consistency.

Sources: [app/server/model/plan/state.go:17-29](), [app/server/model/plan/state.go:99-137]()

### Subscription and Real-Time Updates

```mermaid
graph TB
    subgraph "Subscription_System"
        SubscribePlan["SubscribePlan()"]
        GetActivePlan["GetActivePlan()"]
        Subscribe["activePlan.Subscribe(ctx)"]
        ReturnChannel["return id, chan string"]
    end
    
    subgraph "Update_Distribution"
        UpdateActive["UpdateActivePlan()"]
        SafeMapUpdate["activePlans.Update()"]
        StreamMessage["activePlan.Stream()"]
        AllSubscribers["Broadcast to all subscribers"]
    end
    
    subgraph "Cleanup_System"
        UnsubscribePlan["UnsubscribePlan()"]
        Unsubscribe["activePlan.Unsubscribe()"]
        ChannelClose["Close subscriber channel"]
    end
    
    SubscribePlan --> GetActivePlan
    GetActivePlan --> Subscribe
    Subscribe --> ReturnChannel
    
    UpdateActive --> SafeMapUpdate
    SafeMapUpdate --> StreamMessage
    StreamMessage --> AllSubscribers
    
    UnsubscribePlan --> Unsubscribe
    Unsubscribe --> ChannelClose
    
    style AllSubscribers fill:#9f9
```

The subscription system allows multiple clients to receive real-time updates from active plan execution through dedicated channels managed by the `ActivePlan` type.

Sources: [app/server/model/plan/state.go:143-174]()

## Data Serialization and Persistence

Plan configuration and model settings are stored as JSON in PostgreSQL using custom serialization interfaces.

### Plan Settings Storage

```mermaid
graph TB
    subgraph "PlanSettings_Structure"
        PlanSettings["PlanSettings struct"]
        ModelPackName["ModelPackName string"]
        ModelPack["ModelPack *ModelPack"]
        CustomModels["CustomModels []*CustomModel"]
        UpdatedAt["UpdatedAt time.Time"]
    end
    
    subgraph "Serialization_Interface"
        ScanMethod["Scan(interface{}) error"]
        ValueMethod["Value() (driver.Value, error)"]
        JSONMarshal["json.Marshal()"]
        JSONUnmarshal["json.Unmarshal()"]
    end
    
    subgraph "Configuration_Methods"
        Configure["Configure()"]
        GetModelPack["GetModelPack()"]
        SetModelPack["SetModelPackByName()"]
        DeepCopy["DeepCopy()"]
    end
    
    PlanSettings --> ModelPackName
    PlanSettings --> ModelPack
    PlanSettings --> CustomModels
    PlanSettings --> UpdatedAt
    
    PlanSettings --> ScanMethod
    PlanSettings --> ValueMethod
    ValueMethod --> JSONMarshal
    ScanMethod --> JSONUnmarshal
    
    PlanSettings --> Configure
    PlanSettings --> GetModelPack
    PlanSettings --> SetModelPack
    PlanSettings --> DeepCopy
    
    style JSONMarshal fill:#9f9
    style JSONUnmarshal fill:#9f9
```

The `PlanSettings` type implements PostgreSQL's `driver.Valuer` and `sql.Scanner` interfaces for seamless JSON serialization to database columns.

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `Scan()` | Deserialize from database | JSON unmarshal from bytes/string |
| `Value()` | Serialize to database | JSON marshal to bytes |
| `Configure()` | Runtime configuration | Set custom models and providers |
| `DeepCopy()` | Safe copying | Full JSON round-trip |

Sources: [app/shared/plan_model_settings.go:86-103](), [app/shared/plan_model_settings.go:238-249]()

## Concurrency Control and Safety

The storage layer implements multiple levels of concurrency control to ensure data consistency during simultaneous plan operations.

### Multi-Level Locking Strategy

```mermaid
graph TB
    subgraph "Database_Level"
        TransactionIsolation["REPEATABLE READ"]
        RowLevelLocks["FOR UPDATE/SHARE"]
        DeadlockDetection["Deadlock detection"]
    end
    
    subgraph "Application_Level"
        RepoLocks["Repository locks table"]
        HeartbeatMechanism["Heartbeat validation"]
        ExpiredCleanup["Expired lock cleanup"]
    end
    
    subgraph "Git_Level"
        IndexLockHandling["index.lock removal"]
        AtomicOperations["Atomic git commands"]
        RetryOnConflict["Retry on lock conflicts"]
    end
    
    subgraph "Memory_Level"
        SafeMapOps["Thread-safe map operations"]
        ChannelSync["Channel synchronization"]
        ContextCancellation["Context-based cleanup"]
    end
    
    TransactionIsolation --> RowLevelLocks
    RowLevelLocks --> DeadlockDetection
    
    RepoLocks --> HeartbeatMechanism
    HeartbeatMechanism --> ExpiredCleanup
    
    IndexLockHandling --> AtomicOperations
    AtomicOperations --> RetryOnConflict
    
    SafeMapOps --> ChannelSync
    ChannelSync --> ContextCancellation
    
    style DeadlockDetection fill:#ffa
    style ExpiredCleanup fill:#ffa
```

This multi-layered approach ensures that concurrent operations can proceed safely at the database, application, Git, and memory levels without data corruption or deadlocks.

Sources: [app/server/db/locks.go:105-141](), [app/server/db/locks.go:552-562](), [app/server/db/git.go:655-684]()

---

