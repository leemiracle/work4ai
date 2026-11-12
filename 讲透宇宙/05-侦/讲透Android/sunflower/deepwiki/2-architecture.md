<!-- source: DeepWiki mcp.deepwiki.com · repo android/sunflower · page 2 Architecture · fetched 2026-10-23 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/androidTest/java/com/google/samples/apps/sunflower/data/GardenPlantingDaoTest.kt](app/src/androidTest/java/com/google/samples/apps/sunflower/data/GardenPlantingDaoTest.kt)
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlanting.kt](app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlanting.kt)
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingDao.kt](app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingDao.kt)
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingRepository.kt](app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingRepository.kt)
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/GardenPlantingListViewModel.kt](app/src/main/java/com/google/samples/apps/sunflower/viewmodels/GardenPlantingListViewModel.kt)
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantDetailViewModel.kt](app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantDetailViewModel.kt)
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantListViewModel.kt](app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantListViewModel.kt)
- [app/src/test/java/com/google/samples/apps/sunflower/data/GardenPlantingTest.kt](app/src/test/java/com/google/samples/apps/sunflower/data/GardenPlantingTest.kt)

</details>



## Purpose and Scope

This document outlines the high-level architecture of the Sunflower application, explaining the separation of concerns, data flow patterns, and key architectural components. It provides a technical overview of how different parts of the system interact with each other. For specific implementation details about the MVVM pattern, see [MVVM Pattern](#2.1). For details about how repositories are implemented, see [Repository Pattern](#2.2). For in-depth information about the database and data entities, see [Data Layer](#2.3).

## Architectural Overview

Sunflower implements a clean architecture with distinct layers that separate concerns to promote testability and maintainability.

```mermaid
graph TD
    subgraph "UI Layer"
        ComposeUI["Jetpack Compose UI"]
        LegacyViews["Legacy Views/Fragments"]
    end

    subgraph "Presentation Layer"
        PlantDetailVM["PlantDetailViewModel"]
        PlantListVM["PlantListViewModel"]
        GardenPlantingListVM["GardenPlantingListViewModel"]
    end

    subgraph "Data Layer"
        PlantRepo["PlantRepository"]
        GardenPlantingRepo["GardenPlantingRepository"]
        UnsplashRepo["UnsplashRepository"]
        PlantDAO["PlantDao"]
        GardenPlantingDAO["GardenPlantingDao"]
    end

    subgraph "External Systems"
        AppDB[(AppDatabase)]
        UnsplashAPI["Unsplash API"]
    end

    ComposeUI --> PlantDetailVM & PlantListVM & GardenPlantingListVM
    LegacyViews --> PlantDetailVM & PlantListVM & GardenPlantingListVM
    
    PlantDetailVM --> PlantRepo & GardenPlantingRepo
    PlantListVM --> PlantRepo
    GardenPlantingListVM --> GardenPlantingRepo
    
    PlantRepo --> PlantDAO
    GardenPlantingRepo --> GardenPlantingDAO
    UnsplashRepo --> UnsplashAPI
    
    PlantDAO --> AppDB
    GardenPlantingDAO --> AppDB
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantDetailViewModel.kt]()
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantListViewModel.kt]()
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/GardenPlantingListViewModel.kt]()
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingRepository.kt]()
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingDao.kt]()

## Key Components

### ViewModels

ViewModels serve as the bridge between UI and data layers, exposing data through LiveData or StateFlow for reactive UI updates.

#### PlantDetailViewModel

```mermaid
classDiagram
    class PlantDetailViewModel {
        +String plantId
        +StateFlow~Boolean~ isPlanted
        +LiveData~Plant~ plant
        +LiveData~Boolean~ showSnackbar
        +addPlantToGarden()
        +dismissSnackbar()
        +hasValidUnsplashKey()
    }
    
    class PlantRepository {
        +getPlant(String): Flow~Plant~
    }
    
    class GardenPlantingRepository {
        +isPlanted(String): Flow~Boolean~
        +createGardenPlanting(String)
    }
    
    PlantDetailViewModel --> PlantRepository: uses
    PlantDetailViewModel --> GardenPlantingRepository: uses
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantDetailViewModel.kt:38-74]()

The `PlantDetailViewModel` retrieves plant details and manages garden planting operations. It uses `SavedStateHandle` to persist the plant ID across configuration changes and process death, and exposes plant data and planting status through reactive streams.

#### PlantListViewModel

```mermaid
classDiagram
    class PlantListViewModel {
        -MutableStateFlow~Int~ growZone
        +LiveData~List~Plant~~ plants
        +updateData()
        +setGrowZoneNumber(int)
        +clearGrowZoneNumber()
        +isFiltered()
    }
    
    class PlantRepository {
        +getPlants(): Flow~List~Plant~~
        +getPlantsWithGrowZoneNumber(int): Flow~List~Plant~~
    }
    
    PlantListViewModel --> PlantRepository: uses
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantListViewModel.kt:36-111]()

`PlantListViewModel` manages the plant list and filtering functionality. It uses `flatMapLatest` to switch between data sources when the grow zone filter changes, ensuring the UI always displays the most current data.

#### GardenPlantingListViewModel

```mermaid
classDiagram
    class GardenPlantingListViewModel {
        +StateFlow~List~PlantAndGardenPlantings~~ plantAndGardenPlantings
    }
    
    class GardenPlantingRepository {
        +getPlantedGardens(): Flow~List~PlantAndGardenPlantings~~
    }
    
    GardenPlantingListViewModel --> GardenPlantingRepository: uses
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/GardenPlantingListViewModel.kt:30-41]()

`GardenPlantingListViewModel` provides access to the user's garden plants, exposing them as a `StateFlow` for reactive UI updates.

### Repositories

Repositories abstract data access logic and provide a clean API for ViewModels.

#### GardenPlantingRepository

```mermaid
classDiagram
    class GardenPlantingRepository {
        +createGardenPlanting(String)
        +removeGardenPlanting(GardenPlanting)
        +isPlanted(String): Flow~Boolean~
        +getPlantedGardens(): Flow~List~PlantAndGardenPlantings~~
    }
    
    class GardenPlantingDao {
        +getGardenPlantings(): Flow~List~GardenPlanting~~
        +isPlanted(String): Flow~Boolean~
        +getPlantedGardens(): Flow~List~PlantAndGardenPlantings~~
        +insertGardenPlanting(GardenPlanting): Long
        +deleteGardenPlanting(GardenPlanting)
    }
    
    GardenPlantingRepository --> GardenPlantingDao: uses
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingRepository.kt:23-51]()
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingDao.kt:30-50]()

`GardenPlantingRepository` manages garden-related operations, delegating database operations to the DAO. It's annotated with `@Singleton` to ensure a single instance exists throughout the application's lifecycle.

### Data Access Objects (DAOs)

DAOs define the interface for database operations, using Room annotations to generate SQL queries.

#### GardenPlantingDao

```mermaid
classDiagram
    class GardenPlantingDao {
        +getGardenPlantings(): Flow~List~GardenPlanting~~
        +isPlanted(String): Flow~Boolean~
        +getPlantedGardens(): Flow~List~PlantAndGardenPlantings~~
        +insertGardenPlanting(GardenPlanting): Long
        +deleteGardenPlanting(GardenPlanting)
    }
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingDao.kt:30-50]()

`GardenPlantingDao` defines database operations for garden plantings, returning results as Kotlin Flows to enable reactive programming. The `@Transaction` annotation on `getPlantedGardens()` ensures atomicity when fetching related entities.

### Data Entities

#### Entity Relationships

```mermaid
erDiagram
    Plant ||--o{ GardenPlanting : "planted_as"
    Plant {
        string plantId PK
        string name
        string description
        int growZoneNumber
        int wateringInterval
        string imageUrl
    }
    GardenPlanting {
        long gardenPlantingId PK
        string plantId FK
        Calendar plantDate
        Calendar lastWateringDate
    }
    PlantAndGardenPlantings ||--|| Plant : "contains"
    PlantAndGardenPlantings ||--o{ GardenPlanting : "contains"
    PlantAndGardenPlantings {
        Plant plant
        List~GardenPlanting~ gardenPlantings
    }
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlanting.kt:41-60]()
- [app/src/androidTest/java/com/google/samples/apps/sunflower/data/GardenPlantingDaoTest.kt:88-98]()

The diagram illustrates the relationships between database entities:
- `Plant` represents a plant species with cultivation information
- `GardenPlanting` represents a plant added to the user's garden with tracking metadata
- `PlantAndGardenPlantings` is a convenience class that combines a `Plant` with its associated `GardenPlanting` entries

## Data Flow

```mermaid
sequenceDiagram
    participant UI as "UI Components"
    participant VM as "ViewModels"
    participant Repo as "Repositories"
    participant DAO as "DAOs"
    participant DB as "AppDatabase"

    UI->>VM: Request data
    activate VM
    VM->>Repo: Get data
    activate Repo
    Repo->>DAO: Query data
    activate DAO
    DAO->>DB: SQL query
    activate DB
    DB-->>DAO: Result set
    deactivate DB
    DAO-->>Repo: Entity objects (Flow)
    deactivate DAO
    Repo-->>VM: Domain objects (Flow)
    deactivate Repo
    VM-->>UI: UI state (LiveData/StateFlow)
    deactivate VM
    
    UI->>VM: User action (e.g., add plant)
    activate VM
    VM->>Repo: Update data
    activate Repo
    Repo->>DAO: Modify data
    activate DAO
    DAO->>DB: SQL update
    activate DB
    DB-->>DAO: Success/Failure
    deactivate DB
    DAO-->>Repo: Result
    deactivate DAO
    Repo-->>VM: Result
    deactivate Repo
    VM-->>UI: Updated state
    deactivate VM
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantDetailViewModel.kt:46-67]()
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantListViewModel.kt:45-51]()
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingRepository.kt:27-39]()
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingDao.kt:31-49]()

This diagram illustrates the reactive data flow pattern used in Sunflower:

1. UI layer requests data from ViewModels
2. ViewModels delegate to Repositories
3. Repositories retrieve data from DAOs or remote sources
4. Data flows back as reactive streams (Flows)
5. ViewModels transform Flows to LiveData/StateFlow for UI consumption
6. Updates follow the same path in reverse

## Dependency Injection with Hilt

```mermaid
graph TD
    subgraph "ViewModels"
        PDVM["@HiltViewModel<br>PlantDetailViewModel"]
        PLVM["@HiltViewModel<br>PlantListViewModel"]
        GPLVM["@HiltViewModel<br>GardenPlantingListViewModel"]
    end
    
    subgraph "Repositories"
        PR["@Singleton<br>PlantRepository"]
        GPR["@Singleton<br>GardenPlantingRepository"]
    end
    
    subgraph "DAOs"
        PD["PlantDao"]
        GPD["GardenPlantingDao"]
    end
    
    subgraph "Database"
        AppDB["AppDatabase"]
    end
    
    PDVM -->|"@Inject"| PR & GPR
    PLVM -->|"@Inject"| PR
    GPLVM -->|"@Inject"| GPR
    
    PR -->|"@Inject"| PD
    GPR -->|"@Inject"| GPD
    
    PD & GPD --> AppDB
```

Sources:
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantDetailViewModel.kt:37-38]()
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/PlantListViewModel.kt:35-36]()
- [app/src/main/java/com/google/samples/apps/sunflower/viewmodels/GardenPlantingListViewModel.kt:29-30]()
- [app/src/main/java/com/google/samples/apps/sunflower/data/GardenPlantingRepository.kt:22-23]()

Sunflower uses Hilt for dependency injection:
- `@HiltViewModel` identifies ViewModels for Hilt to inject
- `@Inject` constructor parameters receive dependencies from Hilt
- `@Singleton` ensures only one instance of repositories exist

This approach eliminates manual dependency management and facilitates testing through dependency substitution.

## Testing Architecture

```mermaid
graph TD
    subgraph "Test Types"
        UT["Unit Tests"]
        IT["Integration Tests"]
        UIT["UI Tests"]
    end
    
    subgraph "Test Components"
        VMT["ViewModel Tests"]
        RT["Repository Tests"]
        DAOT["DAO Tests"]
        UIC["UI Component Tests"]
    end
    
    UT --> VMT & RT
    IT --> DAOT
    UIT --> UIC
    
    VMT -->|"Test"| VM["ViewModels"]
    RT -->|"Test"| Repo["Repositories"]
    DAOT -->|"Test"| DAO["DAOs"]
    UIC -->|"Test"| UI["UI Components"]
```

Sources:
- [app/src/androidTest/java/com/google/samples/apps/sunflower/data/GardenPlantingDaoTest.kt:37-99]()
- [app/src/test/java/com/google/samples/apps/sunflower/data/GardenPlantingTest.kt:25-35]()

The clean architecture facilitates extensive testing:

| Layer | Test Type | Testing Focus | Example |
|-------|-----------|---------------|---------|
| ViewModel | Unit Tests | Business logic, state management | Testing `PlantListViewModel.updateData()` |
| Repository | Unit Tests | Data transformation, caching | Testing `GardenPlantingRepository.createGardenPlanting()` |
| DAO | Integration Tests | SQL queries, data persistence | `GardenPlantingDaoTest.testGetPlantAndGardenPlantings()` |
| UI | UI Tests | Component rendering, user interaction | Testing navigation between screens |

This layered approach enables precise testing of each component with appropriate isolation or integration.

---

