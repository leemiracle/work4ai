<!-- source: DeepWiki mcp.deepwiki.com · repo android/android-health-connect-codelab · page 8 Feature: Differential Changes · fetched 2026-10-23 -->

# Feature: Differential Changes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt](finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt)
- [finished/src/main/java/com/example/healthconnect/codelab/presentation/navigation/HealthConnectNavigation.kt](finished/src/main/java/com/example/healthconnect/codelab/presentation/navigation/HealthConnectNavigation.kt)
- [finished/src/main/res/values/strings.xml](finished/src/main/res/values/strings.xml)
- [start/src/main/res/values/strings.xml](start/src/main/res/values/strings.xml)

</details>



## Purpose and Scope

This document describes the differential changes tracking feature, which enables incremental synchronization of Health Connect data using token-based change detection. This feature allows applications to efficiently monitor modifications (insertions, updates, deletions) to health records without repeatedly querying the entire dataset.

For general information about Health Connect data operations, see [Data Layer - HealthConnectManager](#5). For details on the specific record types that can be tracked, see [Health Records and Data Types](#5.3).

---

## Overview

The differential changes feature implements an incremental sync pattern where the application:

1. Obtains a **changes token** representing a snapshot point in time
2. Stores this token for later use
3. Subsequently retrieves all changes that occurred since that token was created
4. Processes upserted (inserted/updated) and deleted records
5. Updates to the next token for future sync operations

This pattern is significantly more efficient than repeatedly reading entire time ranges of data, particularly for applications that need to synchronize data with external systems or maintain local caches.

**Sources:** [finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt:264-299]()

---

## Token-Based Synchronization Model

```mermaid
graph TD
    subgraph "Token Lifecycle"
        Initial["Initial State:<br/>No Token"]
        ObtainToken["Obtain Token via<br/>getChangesToken()"]
        StoreToken["Store Token:<br/>changesToken = '...'"]
        QueryChanges["Query Changes via<br/>getChanges(token)"]
        ProcessChanges["Process Changes:<br/>Upserts & Deletions"]
        UpdateToken["Update Token:<br/>nextChangesToken"]
    end
    
    subgraph "Time Progression"
        T0["Time T0:<br/>Token Created"]
        T1["Time T1:<br/>Changes Occur"]
        T2["Time T2:<br/>Query Changes"]
    end
    
    Initial --> ObtainToken
    ObtainToken --> StoreToken
    StoreToken --> T0
    T0 --> T1
    T1 --> T2
    T2 --> QueryChanges
    QueryChanges --> ProcessChanges
    ProcessChanges --> UpdateToken
    UpdateToken --> StoreToken
    
    subgraph "Expiration Handling"
        ExpCheck{"Token Valid?"}
        ExpError["IOException:<br/>Token Expired"]
        Fallback["Fallback:<br/>Full Data Read"]
    end
    
    QueryChanges --> ExpCheck
    ExpCheck -->|"Valid"| ProcessChanges
    ExpCheck -->|"Expired"| ExpError
    ExpError --> Fallback
    Fallback --> ObtainToken
```

### Token Characteristics

| Property | Details |
|----------|---------|
| **Validity Period** | 30 days from creation |
| **Scope** | Specific record types specified in `ChangesTokenRequest` |
| **Storage** | Application must persist token between sessions |
| **Uniqueness** | Each token is unique and non-transferable |

Tokens expire after 30 days to prevent indefinite accumulation of change history in the Health Connect system. Applications must check for expiration and handle it gracefully by falling back to a full data read and obtaining a new token.

**Sources:** [finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt:286-294]()

---

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant DCS as DifferentialChangesScreen
    participant DCVM as DifferentialChangesViewModel
    participant HCM as HealthConnectManager
    participant HC as HealthConnectClient
    participant Store as Health Connect Storage
    
    rect 
        Note over User,Store: Phase 1: Enable Tracking
        User->>DCS: Toggle "Track changes" switch
        DCS->>DCVM: enableOrDisableChanges(true)
        DCVM->>HCM: getChangesToken()
        HCM->>HC: getChangesToken(ChangesTokenRequest)
        HC->>Store: Query change tracking token
        Store-->>HC: Return token string
        HC-->>HCM: Token: "abc123..."
        HCM-->>DCVM: Token stored
        DCVM-->>DCS: changesToken updated
    end
    
    rect 
        Note over User,Store: Phase 2: Retrieve Changes
        User->>DCS: Click "Get new changes"
        DCS->>DCVM: getChanges()
        DCVM->>HCM: getChanges(token)
        HCM->>HC: getChanges(token)
        HC->>Store: Query changes since token
        Store-->>HC: Changes list + hasMore flag
        HC-->>HCM: ChangesMessage.ChangeList
        HCM-->>HCM: Check hasMore, loop if needed
        HC-->>HCM: ChangesMessage.NoMoreChanges(nextToken)
        HCM-->>DCVM: Flow<ChangesMessage>
        DCVM-->>DCVM: Collect changes
        DCVM-->>DCS: Display upserted/deleted records
    end
```

The data flow implements a two-phase operation:

1. **Token Acquisition Phase**: User enables tracking, triggering token generation and storage
2. **Change Retrieval Phase**: User requests changes, triggering paginated change retrieval

**Sources:** [finished/src/main/java/com/example/healthconnect/codelab/presentation/navigation/HealthConnectNavigation.kt:194-229]()

---

## Obtaining a Changes Token

The `getChangesToken()` method creates a snapshot token for specified record types.

### Implementation Details

```
suspend fun getChangesToken(): String {
  return healthConnectClient.getChangesToken(
    ChangesTokenRequest(
      setOf(
        ExerciseSessionRecord::class,
        StepsRecord::class,
        TotalCaloriesBurnedRecord::class,
        HeartRateRecord::class,
        WeightRecord::class
      )
    )
  )
}
```

### Record Types Tracked

The following record types are included in the changes token:

| Record Type | Purpose |
|-------------|---------|
| `ExerciseSessionRecord` | Exercise activities and sessions |
| `StepsRecord` | Step count data |
| `TotalCaloriesBurnedRecord` | Calorie expenditure |
| `HeartRateRecord` | Heart rate time series |
| `WeightRecord` | Body weight measurements |

These types align with the data written and read by other features in the application (Exercise Sessions, Weight Input).

**Sources:** [finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt:266-278]()

---

## Retrieving Changes

The `getChanges(token)` method retrieves all changes since the token was created, emitting them as a Flow for efficient processing.

### Flow-Based Change Retrieval

```mermaid
graph LR
    subgraph "getChanges Flow Emission Pattern"
        Start["Start Flow<br/>with token"]
        CallAPI["Call HC<br/>getChanges(token)"]
        CheckExp{"Token<br/>Expired?"}
        Throw["Throw IOException"]
        EmitList["Emit<br/>ChangeList"]
        CheckMore{"hasMore?"}
        UpdateToken["nextToken =<br/>response.nextChangesToken"]
        EmitFinal["Emit<br/>NoMoreChanges"]
        End["End Flow"]
    end
    
    Start --> CallAPI
    CallAPI --> CheckExp
    CheckExp -->|"Yes"| Throw
    CheckExp -->|"No"| EmitList
    EmitList --> CheckMore
    CheckMore -->|"Yes"| UpdateToken
    UpdateToken --> CallAPI
    CheckMore -->|"No"| EmitFinal
    EmitFinal --> End
```

### Pagination Handling

The Health Connect API returns changes in pages. The implementation loops until `hasMore` is false:

```
do {
  val response = healthConnectClient.getChanges(nextChangesToken)
  if (response.changesTokenExpired) {
    throw IOException("Changes token has expired")
  }
  emit(ChangesMessage.ChangeList(response.changes))
  nextChangesToken = response.nextChangesToken
} while (response.hasMore)
emit(ChangesMessage.NoMoreChanges(nextChangesToken))
```

The loop:
1. Fetches a page of changes
2. Checks for token expiration
3. Emits the change list
4. Updates the token for the next page
5. Continues until all pages are retrieved
6. Emits the final token

**Sources:** [finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt:283-299]()

---

## Changes Message Types

The `ChangesMessage` sealed class provides type-safe representation of the Flow emissions.

### Class Hierarchy

```mermaid
classDiagram
    class ChangesMessage {
        <<sealed>>
    }
    
    class NoMoreChanges {
        +String nextChangesToken
    }
    
    class ChangeList {
        +List~Change~ changes
    }
    
    ChangesMessage <|-- NoMoreChanges
    ChangesMessage <|-- ChangeList
    
    class Change {
        <<from SDK>>
        +Record? record
        +String uid
        +ChangeType type
    }
    
    ChangeList --> Change
```

### Message Type Usage

| Message Type | Purpose | Data Contained |
|--------------|---------|----------------|
| `ChangesMessage.ChangeList` | Intermediate emission during pagination | `List<Change>` containing upserted/deleted records |
| `ChangesMessage.NoMoreChanges` | Final emission when all changes retrieved | `nextChangesToken` for subsequent sync operations |

The ViewModel collects these messages and accumulates the `Change` objects:

```kotlin
// Collector pattern in ViewModel
healthConnectManager.getChanges(token).collect { message ->
  when (message) {
    is ChangesMessage.ChangeList -> {
      // Accumulate changes
      changes.addAll(message.changes)
    }
    is ChangesMessage.NoMoreChanges -> {
      // Update token for next sync
      changesToken = message.nextChangesToken
    }
  }
}
```

**Sources:** [finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt:329-332]()

---

## Processing Change Records

Each `Change` object from the Health Connect SDK contains:

- **`record`**: The actual record object (null if deleted)
- **`uid`**: Unique identifier for the record
- **Type information**: Whether the change is an upsert or deletion

### Change Type Categorization

```mermaid
graph TD
    subgraph "Change Processing"
        ChangeObj["Change Object"]
        CheckType{"record != null?"}
        Upserted["Upserted Record:<br/>Insert or Update"]
        Deleted["Deleted Record:<br/>UID only"]
        
        DisplayUpsert["Display in<br/>Upserted Section"]
        DisplayDelete["Display in<br/>Deleted Section"]
    end
    
    ChangeObj --> CheckType
    CheckType -->|"Yes"| Upserted
    CheckType -->|"No"| Deleted
    Upserted --> DisplayUpsert
    Deleted --> DisplayDelete
    
    subgraph "Record Type Resolution"
        RecordObj["record: Record"]
        TypeCheck{"instanceof?"}
        Exercise["ExerciseSessionRecord"]
        Steps["StepsRecord"]
        Calories["TotalCaloriesBurnedRecord"]
        HeartRate["HeartRateRecord"]
        Weight["WeightRecord"]
    end
    
    Upserted --> RecordObj
    RecordObj --> TypeCheck
    TypeCheck --> Exercise
    TypeCheck --> Steps
    TypeCheck --> Calories
    TypeCheck --> HeartRate
    TypeCheck --> Weight
```

The UI categorizes changes into two lists:
- **Upserted**: Records that were created or modified (have non-null `record` field)
- **Deleted**: Records that were removed (have null `record` field, only `uid` available)

**Sources:** [finished/src/main/res/values/strings.xml:123-124]()

---

## Token Lifecycle and Expiration

### Expiration Handling

```mermaid
stateDiagram-v2
    [*] --> NoToken: App First Launch
    NoToken --> ValidToken: getChangesToken()
    ValidToken --> ValidToken: getChanges()<br/>within 30 days
    ValidToken --> ExpiredToken: 30 days elapsed
    ExpiredToken --> ErrorState: getChanges()<br/>throws IOException
    ErrorState --> FullSync: Fallback Strategy
    FullSync --> ValidToken: getChangesToken()<br/>after full read
    ValidToken --> [*]: App Session End
```

### Error Handling Strategy

When a token expires:

1. **Detection**: The `response.changesTokenExpired` flag is checked
2. **Exception**: `IOException("Changes token has expired")` is thrown
3. **Fallback**: Application should:
   - Perform a full data read for the required time range
   - Obtain a new token via `getChangesToken()`
   - Resume using differential changes for future syncs

### Best Practices

| Practice | Rationale |
|----------|-----------|
| **Use changes API regularly** | Prevents token expiration (< 30 days) |
| **Persist token** | Enables cross-session synchronization |
| **Implement fallback** | Handles expiration gracefully |
| **Monitor sync frequency** | Balances efficiency with freshness |

The 30-day expiration prevents indefinite storage of change history in Health Connect, requiring applications to sync data at least monthly.

**Sources:** [finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt:287-293]()

---

## UI Integration

### Screen Structure

The `DifferentialChangesScreen` provides:

1. **Enable/Disable Toggle**: Switch to start/stop change tracking
2. **Current Token Display**: Shows truncated token string
3. **Get Changes Button**: Retrieves new changes since last sync
4. **Changes Display**: Lists upserted and deleted records

### UI String Resources

| String Resource | Usage |
|----------------|-------|
| `differential_changes_title_text` | Explains token concept |
| `differential_changes_continuation_text` | Instructions for retrieving changes |
| `differential_changes_switch_text` | Toggle label: "Track changes" |
| `differential_changes_button_text` | Button label: "Get new changes" |
| `differential_changes_empty` | Shown when no changes found |
| `differential_changes_current_token` | Format string for token display |
| `differential_changes_upserted` | Section header for upserted records |
| `differential_changes_deleted` | Section header for deleted records |

### Record Type Display Labels

Each record type has a corresponding display string:

| Record Type | String Resource |
|-------------|-----------------|
| `ExerciseSessionRecord` | `differential_changes_type_exercise_session` |
| `StepsRecord` | `differential_changes_type_steps` |
| `TotalCaloriesBurnedRecord` | `differential_changes_type_total_calories` |
| `HeartRateRecord` | `differential_changes_type_heart_rate_series` |
| `WeightRecord` | `differential_changes_type_weight` |

**Sources:** [finished/src/main/res/values/strings.xml:116-135](), [finished/src/main/java/com/example/healthconnect/codelab/presentation/navigation/HealthConnectNavigation.kt:194-229]()

---

## Complete Integration Flow

```mermaid
flowchart TD
    subgraph "User Actions"
        ToggleOn["User enables<br/>'Track changes'"]
        ClickGet["User clicks<br/>'Get new changes'"]
    end
    
    subgraph "ViewModel State"
        VMInitial["changesToken = null<br/>changes = emptyList()"]
        VMWithToken["changesToken = 'abc...'<br/>changes = emptyList()"]
        VMWithChanges["changesToken = 'xyz...'<br/>changes = [...]"]
    end
    
    subgraph "HealthConnectManager Operations"
        GetToken["getChangesToken():<br/>Returns token string"]
        GetChanges["getChanges(token):<br/>Returns Flow"]
    end
    
    subgraph "UI Rendering"
        ShowToggle["Show toggle OFF<br/>Button disabled"]
        ShowButton["Show toggle ON<br/>Button enabled"]
        ShowResults["Display upserted<br/>and deleted records"]
    end
    
    VMInitial --> ShowToggle
    ShowToggle --> ToggleOn
    ToggleOn --> GetToken
    GetToken --> VMWithToken
    VMWithToken --> ShowButton
    ShowButton --> ClickGet
    ClickGet --> GetChanges
    GetChanges --> VMWithChanges
    VMWithChanges --> ShowResults
```

The integration follows a clear state progression:

1. **Initial State**: No token, toggle off, button disabled
2. **Tracking Enabled**: Token obtained, toggle on, button enabled
3. **Changes Retrieved**: Changes list populated, next token stored

This design ensures users cannot retrieve changes until a token exists, preventing error conditions.

**Sources:** [finished/src/main/java/com/example/healthconnect/codelab/presentation/navigation/HealthConnectNavigation.kt:207-218](), [finished/src/main/java/com/example/healthconnect/codelab/data/HealthConnectManager.kt:264-299]()

---

