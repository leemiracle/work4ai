<!-- source: DeepWiki mcp.deepwiki.com · repo Technion-Kishony-lab/data-to-paper · page 3 Data Analysis System · fetched 2026-10-26 -->

# Data Analysis System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/functional/research_types/scientific_research/test_df_file_formatting.py](tests/functional/research_types/scientific_research/test_df_file_formatting.py)
- [tests/functional/run_gpt_code/test_mydata_df.py](tests/functional/run_gpt_code/test_mydata_df.py)
- [tests/functional/utils/test_check_types.py](tests/functional/utils/test_check_types.py)

</details>



The Data Analysis System is a core component of the data-to-paper framework that handles the processing, validation, transformation, and visualization of research data. It provides specialized data structures and utilities for ensuring data integrity, tracking data transformations, and converting data into formats suitable for publication in scientific papers.

For information about the Document Generation System that uses the analyzed data to create research papers, see [Document Generation System](#4). For details on how code execution is handled in a sandboxed environment, see [Code Execution System](#2).

## System Architecture

The Data Analysis System consists of several interrelated components that work together to process and validate research data:

```mermaid
flowchart TD
    subgraph "Data Analysis System"
        A["InfoDataFrame"] --> B["Data Validation"]
        A --> C["Data Transformation"]
        C --> D["LaTeX Conversion"]
        C --> E["Figure Generation"]
        F["Statistical Processing"] --> A
        G["DataFrame Tracking"] --> A
    end

    H["Raw Data"] --> A
    D --> I["LaTeX Content"]
    E --> J["Figure Files"]
    
    I --> K["Document Generation System"]
    J --> K
```

Sources: [tests/functional/research_types/scientific_research/test_df_file_formatting.py:1-202](), [tests/functional/run_gpt_code/test_mydata_df.py:1-54]()

## Key Components

### InfoDataFrame

The InfoDataFrame is an extended Pandas DataFrame that preserves additional metadata and tracks transformations. It inherits from Pandas DataFrame and adds the ability to store extra information that persists through operations like saving, loading, and transformations.

```mermaid
classDiagram
    class DataFrame {
        +columns
        +index
        +values
        +to_pickle()
        +read_pickle()
        +T
    }
    
    class InfoDataFrame {
        +extra_info
        +to_pickle()
        +read_pickle()
        +T
    }
    
    class InfoDataFrameWithSaveObjFuncCall {
        +get_func_call()
    }
    
    DataFrame <|-- InfoDataFrame
    InfoDataFrame <|-- InfoDataFrameWithSaveObjFuncCall
```

Key features of InfoDataFrame:
- Maintains metadata through serialization/deserialization
- Preserves attributes during operations like transpose
- Integrates with the DataFrame tracking system

Sources: [tests/functional/run_gpt_code/test_mydata_df.py:10-54]()

### Data Validation System

The Data Analysis System includes robust validation mechanisms to ensure data integrity and correct typing:

```mermaid
flowchart LR
    A["Input Data"] --> B["Type Validation"]
    B --> C{Valid?}
    C -->|Yes| D["Process Data"]
    C -->|No| E["Raise WrongTypeException"]
    
    subgraph "Validation Types"
        F["Basic Types"]
        G["Collections (List, Dict)"]
        H["Union Types"]
        I["Optional Types"]
        J["Tuple Types"]
    end
```

The validation system supports:
- Validation of primitive types (int, str, etc.)
- Complex type checking for collections like List[str], Dict[str, int]
- Union type validation (Union[int, str])
- Optional type validation
- Tuple type validation with specific length and element types

Sources: [tests/functional/utils/test_check_types.py:1-57]()

### Data Transformation

The Data Analysis System provides utilities to transform DataFrames into formats suitable for inclusion in research papers:

```mermaid
flowchart TD
    A["InfoDataFrame"] --> B["analysis_df_to_latex"]
    A --> C["analysis_df_to_figure"]
    A --> D["displayitems_df_to_latex"]
    A --> E["displayitems_df_to_figure"]
    
    B --> F["LaTeX Table"]
    C --> G["Figure File"]
    D --> H["Formatted LaTeX Table"]
    E --> I["Formatted Figure File"]
    
    F --> J["Raw Analysis"]
    H --> K["Display Items"]
    G --> J
    I --> K
```

These transformation functions handle:
- Converting DataFrames to LaTeX tables with proper formatting
- Creating figures from DataFrames with appropriate styling
- Handling special formatting for statistical values (e.g., p-values)
- Adding captions, labels, and glossaries for scientific documentation

Sources: [tests/functional/research_types/scientific_research/test_df_file_formatting.py:43-69]()

### Statistical Processing

The Data Analysis System includes specialized handling for statistical entities, particularly p-values:

```mermaid
classDiagram
    class PValue {
        +value: float
        +__str__()
        +__repr__()
        +__lt__()
        +__gt__()
    }
    
    class DataFrame {
        +columns
    }
    
    class DataFrameWithPValues {
        +p_value_column
    }
    
    DataFrame <|-- DataFrameWithPValues
    DataFrameWithPValues --> PValue : contains
```

The `PValue` class provides specialized formatting and comparison operations for statistical p-values. This allows for proper display in scientific papers with appropriate significance indicators.

Sources: [tests/functional/research_types/scientific_research/test_df_file_formatting.py:25-31]()

## DataFrame Tracking

The Data Analysis System includes a tracking mechanism to monitor DataFrame changes during code execution:

```mermaid
sequenceDiagram
    participant User
    participant TrackDataFrames
    participant DataFrame
    participant Storage
    
    User->>TrackDataFrames: Enter context
    DataFrame->>TrackDataFrames: Register DataFrame
    User->>DataFrame: Modify DataFrame
    TrackDataFrames->>DataFrame: Track modifications
    DataFrame->>Storage: Save with to_pickle()
    Storage->>DataFrame: Load with read_pickle()
    DataFrame->>TrackDataFrames: Update tracking state
    User->>TrackDataFrames: Exit context
```

The `TrackDataFrames` context manager:
- Monitors DataFrame creation and modifications
- Ensures persistence of metadata during save/load operations
- Maintains the specialized DataFrame types and their attributes

Sources: [tests/functional/run_gpt_code/test_mydata_df.py:34-42]()

## Integration with Other Systems

The Data Analysis System integrates with other components of the data-to-paper framework:

```mermaid
flowchart LR
    subgraph "Code Execution System"
        A["CodeRunner"]
        B["Statistical Package Overrides"]
    end
    
    subgraph "Data Analysis System"
        C["InfoDataFrame"]
        D["DataFrame Validation"]
        E["Data Transformation"]
    end
    
    subgraph "Document Generation System"
        F["LaTeX Generation"]
        G["Figure Generation"]
        H["PDF Compilation"]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    F --> H
    G --> H
```

Key integrations:
1. **Code Execution System**: Provides the sandboxed environment where data analysis code runs
2. **Statistical Package Overrides**: Ensures statistical functions behave properly during analysis
3. **Document Generation System**: Uses the transformed data to generate publication-ready documents

Sources: [tests/functional/research_types/scientific_research/test_df_file_formatting.py:8-22]()

## Data View Purposes

The Data Analysis System supports multiple presentation formats for different contexts through the `ViewPurpose` enumeration:

| View Purpose | Description | Use Case |
|-------------|-------------|----------|
| CODE_REVIEW | Raw format for code inspection | Code review and debugging |
| PRODUCT | Formatted output for general viewing | General product display |
| HYPERTARGET_PRODUCT | Output with hyperlinks | Interactive document viewing |
| APP_HTML | HTML format for application display | GUI application display |
| FINAL_APPENDIX | Format for document appendices | Research paper appendices |
| FINAL_INLINE | Format for inline document content | Main research paper content |

The system adapts its output formatting based on the view purpose, ensuring appropriate presentation in each context.

Sources: [tests/functional/research_types/scientific_research/test_df_file_formatting.py:106-141]()

## Data Flow

The typical workflow through the Data Analysis System follows these steps:

```mermaid
flowchart TD
    A["Raw Data Input"] --> B["Create InfoDataFrame"]
    B --> C["Apply Statistical Analysis"]
    C --> D["Validate Data"]
    D --> E["Transform to Output Format"]
    E -->|Tables| F["analysis_df_to_latex / displayitems_df_to_latex"]
    E -->|Figures| G["analysis_df_to_figure / displayitems_df_to_figure"]
    F --> H["LaTeX Document"]
    G --> I["Figure Files"]
    H --> J["Document Generation System"]
    I --> J
```

This workflow ensures that raw data is properly processed, validated, and transformed into formats suitable for inclusion in scientific publications.

Sources: [tests/functional/research_types/scientific_research/test_df_file_formatting.py:65-69]()

---

