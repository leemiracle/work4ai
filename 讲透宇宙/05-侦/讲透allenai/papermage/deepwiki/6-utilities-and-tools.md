<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/papermage · page 6 Utilities and Tools · fetched 2026-10-26 -->

# Utilities and Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [papermage/magelib/indexer.py](papermage/magelib/indexer.py)
- [papermage/utils/annotate.py](papermage/utils/annotate.py)

</details>



This page documents the utility components and tools in the papermage library that support core functionality by providing efficient entity indexing, annotation helpers, visualization capabilities, and evaluation metrics. These utilities serve as important building blocks that enhance the usability and effectiveness of the main document processing pipeline. For information about the core document processing pipeline, see [Document Processing Pipeline](#3).

## Indexing Utilities

Papermage provides specialized indexing utilities that enable efficient entity search and intersection operations, which are critical for document analysis tasks.

```mermaid
classDiagram
    class Indexer {
        <<abstract>>
        +find(query: Entity): List[Entity]
    }
    
    class EntitySpanIndexer {
        -List[Entity] _entities
        -NCLS _index
        +__init__(entities: List[Entity])
        +find(query: Entity): List[Entity]
        -_ensure_disjoint()
    }
    
    class EntityBoxIndexer {
        -List[Entity] _entities
        -Dict _box_id_to_entity_id
        -List[Box] _boxes
        -np_boxes_x1, np_boxes_y1, np_boxes_x2, np_boxes_y2, np_boxes_page
        +__init__(entities: List[Entity], allow_overlap: bool)
        +find(query: Entity): List[Entity]
        -_find_overlap_boxes(query: Box): List[int]
        -_find_overlap_entities(query: Box): List[int]
        -_ensure_disjoint()
    }
    
    Indexer <|-- EntitySpanIndexer
    Indexer <|-- EntityBoxIndexer
```

The indexing utilities provide a standardized interface for finding entities that intersect with a query entity. This is particularly useful for tasks such as locating all sentences within a paragraph or finding figures that overlap with certain text regions.

### Indexer Base Class

The abstract `Indexer` class defines the basic interface for all indexing utilities in papermage. It requires implementing a `find()` method that accepts an entity query and returns matching entities.

```python
# Abstract interface for all indexers
find(query: Entity) -> List[Entity]
```

Sources: [papermage/magelib/indexer.py:19-26]()

### EntitySpanIndexer

The `EntitySpanIndexer` class provides efficient indexing for text span-based entity searching. It implements a Nested Containment List (NCL) data structure for fast interval queries.

Key features:
- Builds an NCLS index from entity spans
- Enforces disjoint spans by default (no overlaps)
- Returns entities whose spans overlap with the query entity

```python
# Usage example (not in source code)
indexer = EntitySpanIndexer(entities)
matching_entities = indexer.find(query_entity)
```

The implementation uses the NCLS library for efficient interval queries, making it suitable for tasks that require frequent text span intersection operations.

Sources: [papermage/magelib/indexer.py:29-99]()

### EntityBoxIndexer

The `EntityBoxIndexer` class provides efficient indexing for visual box-based entity searching. This is particularly useful for finding entities that overlap in the rendered document space.

Key features:
- Uses numpy arrays for efficient box overlap calculations
- Can optionally enforce disjoint boxes (no overlaps)
- Returns entities whose boxes overlap with the query entity

The implementation uses numpy vectorized operations to quickly identify box overlaps, making it efficient for visual layout analysis tasks.

Sources: [papermage/magelib/indexer.py:102-172]()

## Entity Relationship and Indexing Flow

```mermaid
flowchart TD
    subgraph "Entity Data"
        E1["Entity 1"] --> S1["Spans: [10-15, 20-25]"]
        E1 --> B1["Boxes: [page1: (10,10,50,20)]"]
        E2["Entity 2"] --> S2["Spans: [30-40]"]
        E2 --> B2["Boxes: [page1: (100,10,50,20)]"]
    end
    
    subgraph "Indexing Utilities"
        SpanIdx["EntitySpanIndexer"] --> NCLS["NCLS Data Structure"]
        BoxIdx["EntityBoxIndexer"] --> NPArrays["Numpy Array Representation"]
    end
    
    subgraph "Query Processing"
        Query["Query Entity"]
        SpanOverlap["Find Span Overlaps"]
        BoxOverlap["Find Box Overlaps"]
        Results["Matching Entities"]
    end
    
    E1 --> SpanIdx
    E2 --> SpanIdx
    E1 --> BoxIdx
    E2 --> BoxIdx
    
    Query --> SpanOverlap
    Query --> BoxOverlap
    NCLS --> SpanOverlap
    NPArrays --> BoxOverlap
    SpanOverlap --> Results
    BoxOverlap --> Results
```

Sources: [papermage/magelib/indexer.py:19-172]()

## Annotation Utilities

Papermage provides utilities for grouping and annotating entities based on their metadata properties. These tools help organize and categorize entities for further processing or analysis.

### Entity Grouping

The `group_by` function takes a list of entities and groups them according to a specified metadata field. This is useful for classifying entities into different categories or layers.

Key features:
- Groups entities by a specified metadata field
- Allows custom mapping of metadata values to group names
- Returns predictions that can be used to annotate a document

```python
# Example usage (not in source code)
predictions = group_by(entities, metadata_field="entity_type")
doc.annotate(predictions)
```

This utility is particularly useful for organizing entities into semantic categories that can be processed together or visualized distinctly.

```mermaid
flowchart LR
    subgraph "Input Entities"
        E1["Entity (metadata.type='title')"]
        E2["Entity (metadata.type='paragraph')"]
        E3["Entity (metadata.type='title')"]
        E4["Entity (metadata.type='figure')"]
    end
    
    subgraph "group_by Operation"
        GB["group_by(entities, 'type')"]
    end
    
    subgraph "Output Predictions"
        P1["Prediction(name='title', entities=[E1, E3])"]
        P2["Prediction(name='paragraph', entities=[E2])"]
        P3["Prediction(name='figure', entities=[E4])"]
    end
    
    E1 --> GB
    E2 --> GB
    E3 --> GB
    E4 --> GB
    
    GB --> P1
    GB --> P2
    GB --> P3
```

Sources: [papermage/utils/annotate.py:7-45]()

## Visualization Tools

While the specific visualization files weren't provided, the project architecture overview indicates the presence of visualization utilities that help display document content and entity annotations. These tools are crucial for debugging, analysis, and results presentation.

Key visualization capabilities likely include:
- Rendering document pages with entity annotations
- Highlighting different entity types with distinct visual styles
- Visualizing spatial relationships between entities

The visualizers module contains functions like `plot_entities_on_page` that allow for visual inspection of entity annotations on document pages.

```mermaid
flowchart TD
    subgraph "Document and Entities"
        Doc["Document"]
        Entities["Entities (Tokens, Sentences, Blocks, etc.)"]
    end
    
    subgraph "Visualization Process"
        PlotFunc["plot_entities_on_page()"]
        RenderPage["Render Page Image"]
        DrawBoxes["Draw Entity Boxes"]
        HighlightText["Highlight Text Spans"]
        AddLabels["Add Entity Labels"]
    end
    
    subgraph "Output"
        Display["Visual Representation"]
    end
    
    Doc --> RenderPage
    Entities --> DrawBoxes
    Entities --> HighlightText
    Entities --> AddLabels
    
    RenderPage --> PlotFunc
    DrawBoxes --> PlotFunc
    HighlightText --> PlotFunc
    AddLabels --> PlotFunc
    
    PlotFunc --> Display
```

Sources: Based on system architecture overview provided

## Evaluation Tools

The evaluation tools in papermage provide metrics and methods for assessing model performance on document processing tasks. While specific implementation details weren't provided, these tools typically support standard evaluation workflows.

Common evaluation capabilities likely include:
- Computing precision, recall, and F1 scores for entity detection
- Evaluating entity classification accuracy
- Measuring spatial accuracy of detected entity boxes
- Comparing system outputs against ground truth annotations

These evaluation utilities help in benchmarking model performance, comparing different approaches, and tracking improvements during development.

```mermaid
flowchart TD
    subgraph "Input"
        Pred["Predicted Entities"]
        Gold["Gold Standard Entities"]
    end
    
    subgraph "Evaluation Process"
        Match["Entity Matching"]
        Metrics["Metric Calculation"]
        subgraph "Metrics Types"
            PrecRec["Precision/Recall"]
            F1["F1 Score"]
            IoU["Intersection over Union"]
        end
    end
    
    subgraph "Output"
        Results["Evaluation Results"]
        Visual["Visualization of Errors"]
    end
    
    Pred --> Match
    Gold --> Match
    
    Match --> Metrics
    Metrics --> PrecRec
    Metrics --> F1
    Metrics --> IoU
    
    PrecRec --> Results
    F1 --> Results
    IoU --> Results
    
    Results --> Visual
```

Sources: Based on system architecture overview provided

## Integration with Core Components

The utilities and tools described above integrate seamlessly with the core document processing pipeline in papermage. They provide essential support functions that complement the primary document parsing and entity prediction components.

```mermaid
flowchart TD
    subgraph "Document Processing"
        Parse["Parse PDF"]
        Rasterize["Rasterize PDF"]
        Predict["Apply Predictors"]
        Annotate["Annotate Document"]
    end
    
    subgraph "Utility Components"
        direction LR
        Index["Indexers"]
        Group["Annotation Utilities"]
        Vis["Visualization Tools"]
        Eval["Evaluation Tools"]
    end
    
    Parse --> Rasterize
    Rasterize --> Predict
    Predict --> Annotate
    
    Annotate --> |"creates document with entities"| Index
    Predict --> |"group predictions"| Group
    Group --> |"grouped entities"| Annotate
    Annotate --> |"visualize results"| Vis
    Annotate --> |"evaluate quality"| Eval
```

Sources: Based on system architecture overview provided

---

