<!-- source: DeepWiki mcp.deepwiki.com · repo voxel51/fiftyone · page 2 Core Data Model · fetched 2026-10-21 -->

# Core Data Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [fiftyone/__public__.py](fiftyone/__public__.py)
- [fiftyone/core/aggregations.py](fiftyone/core/aggregations.py)
- [fiftyone/core/clips.py](fiftyone/core/clips.py)
- [fiftyone/core/collections.py](fiftyone/core/collections.py)
- [fiftyone/core/dataset.py](fiftyone/core/dataset.py)
- [fiftyone/core/document.py](fiftyone/core/document.py)
- [fiftyone/core/expressions.py](fiftyone/core/expressions.py)
- [fiftyone/core/fields.py](fiftyone/core/fields.py)
- [fiftyone/core/frame.py](fiftyone/core/frame.py)
- [fiftyone/core/labels.py](fiftyone/core/labels.py)
- [fiftyone/core/odm/dataset.py](fiftyone/core/odm/dataset.py)
- [fiftyone/core/odm/document.py](fiftyone/core/odm/document.py)
- [fiftyone/core/odm/embedded_document.py](fiftyone/core/odm/embedded_document.py)
- [fiftyone/core/odm/mixins.py](fiftyone/core/odm/mixins.py)
- [fiftyone/core/odm/sample.py](fiftyone/core/odm/sample.py)
- [fiftyone/core/odm/utils.py](fiftyone/core/odm/utils.py)
- [fiftyone/core/patches.py](fiftyone/core/patches.py)
- [fiftyone/core/sample.py](fiftyone/core/sample.py)
- [fiftyone/core/stages.py](fiftyone/core/stages.py)
- [fiftyone/core/video.py](fiftyone/core/video.py)
- [fiftyone/core/view.py](fiftyone/core/view.py)
- [tests/unittests/aggregation_tests.py](tests/unittests/aggregation_tests.py)
- [tests/unittests/dataset_tests.py](tests/unittests/dataset_tests.py)
- [tests/unittests/odm_tests.py](tests/unittests/odm_tests.py)
- [tests/unittests/patches_tests.py](tests/unittests/patches_tests.py)
- [tests/unittests/video_tests.py](tests/unittests/video_tests.py)
- [tests/unittests/view_tests.py](tests/unittests/view_tests.py)

</details>



This document explains the fundamental data structures that power FiftyOne: `Dataset`, `SampleCollection`, `DatasetView`, and the ODM persistence layer. These components form the foundation for storing, organizing, and querying computer vision datasets and their associated annotations.

## Overview

FiftyOne's core data model is built around a hierarchical structure where `Dataset` instances contain collections of `Sample` objects, which can be filtered and transformed through `DatasetView` instances. The entire system is backed by MongoDB through a custom Object Document Mapper (ODM).

### Core Class Hierarchy and Inheritance

```mermaid
graph TD
    SampleCollection["SampleCollection<br/>(collections.py:237)"]
    Dataset["Dataset<br/>(dataset.py:276)"]
    DatasetView["DatasetView<br/>(view.py:33)"]
    Sample["Sample<br/>(sample.py:484)"]
    SampleView["SampleView<br/>(sample.py:517)"]
    ViewStage["ViewStage<br/>(stages.py:47)"]
    
    SampleCollection --> Dataset
    SampleCollection --> DatasetView
    
    Dataset --> Sample
    DatasetView --> SampleView
    DatasetView --> ViewStage
    
    Dataset -.-> DatasetView
    Sample -.-> SampleView
```

Sources: [fiftyone/core/collections.py:237-258](), [fiftyone/core/dataset.py:276-310](), [fiftyone/core/view.py:33-87](), [fiftyone/core/sample.py:484-510]()

## SampleCollection Architecture

The `SampleCollection` abstract base class defines the interface for both `Dataset` and `DatasetView` instances. This design allows consistent operations across both persistent datasets and ephemeral views.

### SampleCollection Implementation Structure

```mermaid
graph TB
    subgraph "collections.py"
        SampleCollection["SampleCollection<br/>(Line 237)"]
        SaveContext["SaveContext<br/>(Line 80)"]
    end
    
    subgraph "Concrete Implementations"
        Dataset["Dataset<br/>(dataset.py:276)"]
        DatasetView["DatasetView<br/>(view.py:33)"]
    end
    
    subgraph "Sample Types"
        Sample["Sample<br/>(sample.py:484)"]
        SampleView["SampleView<br/>(sample.py:517)"]
    end
    
    subgraph "ODM Documents"
        DatasetSampleDocument["DatasetSampleDocument<br/>(odm/sample.py:73)"]
        NoDatasetSampleDocument["NoDatasetSampleDocument<br/>(odm/sample.py:104)"]
    end
    
    SampleCollection --> Dataset
    SampleCollection --> DatasetView
    
    Dataset --> Sample
    DatasetView --> SampleView
    
    Sample --> DatasetSampleDocument
    Sample --> NoDatasetSampleDocument
    SampleView --> DatasetSampleDocument
    
    SaveContext --> SampleCollection
```

Sources: [fiftyone/core/collections.py:237-276](), [fiftyone/core/dataset.py:276-348](), [fiftyone/core/view.py:33-88](), [fiftyone/core/odm/sample.py:73-147]()

### Core SampleCollection Methods and Properties

| Property/Method | Line Location | Purpose |
|-----------------|---------------|---------|
| `media_type` | collections.py:353-355 | Type of media (image, video, group) |
| `group_field` | collections.py:358-362 | Field used for grouping samples |
| `iter_samples()` | collections.py:1274-1372 | Iterator over samples with batching |
| `count()` | collections.py:1511-1547 | Efficient sample/frame counting |
| `aggregate()` | collections.py:3823-3907 | MongoDB aggregation pipeline execution |
| `bounds()` | collections.py:4094-4113 | Compute bounds of numeric fields |

Sources: [fiftyone/core/collections.py:353-430](), [fiftyone/core/collections.py:1274-1547](), [fiftyone/core/collections.py:3823-4113]()

## Dataset Implementation

The `Dataset` class represents a persistent collection of samples stored in MongoDB. It extends `SampleCollection` and implements the `DatasetSingleton` pattern to ensure only one instance exists per dataset name.

### Dataset Class Structure and Key Attributes

```mermaid
graph TB
    subgraph "dataset.py"
        Dataset["Dataset<br/>(Line 276)<br/>metaclass=DatasetSingleton"]
        DatasetSlots["__slots__:<br/>_doc, _sample_doc_cls<br/>_frame_doc_cls, _group_slice<br/>caches..."]
    end
    
    subgraph "Core Properties (Lines 686-1105)"
        name["name (688)"]
        media_type["media_type (460)"]
        persistent["persistent (755)"]
        tags["tags (767)"]
        description["description (792)"]
        info["info (812)"]
        app_config["app_config (836)"]
    end
    
    subgraph "Schema Properties"
        classes["classes (878)"]
        default_classes["default_classes (906)"]
        mask_targets["mask_targets (932)"]
        skeletons["skeletons (1037)"]
    end
    
    subgraph "Temporal Properties"
        created_at["created_at (715)"]
        last_modified_at["last_modified_at (720)"]
        last_loaded_at["last_loaded_at (750)"]
    end
    
    Dataset --> DatasetSlots
    Dataset --> name
    Dataset --> media_type
    Dataset --> persistent
    Dataset --> tags
    Dataset --> description
    Dataset --> info
    Dataset --> app_config
    Dataset --> classes
    Dataset --> default_classes
    Dataset --> mask_targets
    Dataset --> skeletons
    Dataset --> created_at
    Dataset --> last_modified_at
    Dataset --> last_loaded_at
```

Sources: [fiftyone/core/dataset.py:276-348](), [fiftyone/core/dataset.py:686-1105](), [fiftyone/core/dataset.py:460-639]()

### Dataset Creation and Singleton Management

The `DatasetSingleton` metaclass ensures dataset instances are unique per name:

| Function | Line Location | Purpose |
|----------|---------------|---------|
| `Dataset.__init__()` | dataset.py:311-351 | Initialize with name, persistent flag |
| `load_dataset()` | dataset.py:145-175 | Load existing dataset or create new one |
| `dataset_exists()` | dataset.py:95-106 | Check if dataset exists in MongoDB |
| `delete_dataset()` | dataset.py:226-237 | Delete dataset and clean up |

The singleton ensures: `Dataset("name") is load_dataset("name")`

Sources: [fiftyone/core/dataset.py:145-175](), [fiftyone/core/dataset.py:311-351](), [fiftyone/core/singletons.py:1-50]()

## View System Architecture

The view system allows non-destructive filtering and transformation of datasets through a pipeline of `ViewStage` operations. Views are ephemeral and don't modify the underlying dataset.

### DatasetView and ViewStage Pipeline

```mermaid
graph LR
    Dataset["Dataset<br/>(dataset.py:276)"]
    
    subgraph "ViewStage Pipeline (stages.py)"
        ViewStage["ViewStage<br/>(Line 47)"]
        Match["Match<br/>(Line 4270)"]
        Limit["Limit<br/>(Line 3013)"] 
        Select["Select<br/>(Line 3685)"]
        SortBy["SortBy<br/>(Line 3898)"]
    end
    
    DatasetView["DatasetView<br/>(view.py:33)"]
    MongoDB["MongoDB Aggregation<br/>_aggregate()"]
    
    Dataset --> ViewStage
    ViewStage --> Match
    ViewStage --> Limit
    ViewStage --> Select
    ViewStage --> SortBy
    
    Match --> DatasetView
    Limit --> DatasetView
    Select --> DatasetView
    SortBy --> DatasetView
    
    DatasetView --> MongoDB
```

Sources: [fiftyone/core/view.py:33-87](), [fiftyone/core/stages.py:47-100](), [fiftyone/core/stages.py:4270-4310]()

### Key ViewStage Implementations

| Stage Class | Line Location | MongoDB Operation | Purpose |
|-------------|---------------|-------------------|---------|
| `Exclude` | stages.py:513 | `$match` with `$not` | Exclude samples by IDs |
| `ExcludeBy` | stages.py:591 | `$match` with `$nin` | Exclude by field values |
| `Match` | stages.py:4270 | `$match` | Filter by expressions |
| `Limit` | stages.py:3013 | `$limit` | Limit number of samples |
| `Skip` | stages.py:3851 | `$skip` | Skip N samples |
| `SortBy` | stages.py:3898 | `$sort` | Sort by field values |
| `SelectFields` | stages.py:3710 | `$project` | Project specific fields |
| `FilterLabels` | stages.py:2036 | Complex pipeline | Filter arrays of labels |

Sources: [fiftyone/core/stages.py:513-680](), [fiftyone/core/stages.py:2036-2200](), [fiftyone/core/stages.py:3013-4310]()

### View Execution and MongoDB Integration

The `DatasetView` class converts view stages into MongoDB aggregation pipelines:

| Method | Line Location | Purpose |
|--------|---------------|---------|
| `_pipeline()` | view.py:1513-1628 | Convert stages to MongoDB pipeline |
| `_aggregate()` | view.py:1736-1822 | Execute aggregation on MongoDB |
| `iter_samples()` | view.py:454-545 | Iterate over view results |

Sources: [fiftyone/core/view.py:454-545](), [fiftyone/core/view.py:1513-1822]()

## Sample and Document Architecture

Samples represent individual data points (images, videos, etc.) and their associated metadata and annotations. The system uses a dual document approach for samples in and out of datasets.

### Sample Class Hierarchy and ODM Integration

```mermaid
graph TB
    subgraph "Sample Classes (sample.py)"
        _SampleMixin["_SampleMixin<br/>(Line 41)"]
        Sample["Sample<br/>(Line 484)<br/>metaclass=SampleSingleton"]
        SampleView["SampleView<br/>(Line 517)"]
    end
    
    subgraph "ODM Document Classes (odm/sample.py)"
        NoDatasetSampleDocument["NoDatasetSampleDocument<br/>(Line 104)<br/>Before dataset"]
        DatasetSampleDocument["DatasetSampleDocument<br/>(Line 73)<br/>In dataset"]
    end
    
    subgraph "MongoDB Collections"
        samples_collection["samples.{dataset_name}"]
        frames_collection["frames.{dataset_name}"]
    end
    
    subgraph "Document Mixins (odm/mixins.py)"
        DatasetMixin["DatasetMixin<br/>(Line 55)"]
        NoDatasetMixin["NoDatasetMixin<br/>(Line 780)"]
    end
    
    _SampleMixin --> Sample
    _SampleMixin --> SampleView
    
    Sample --> NoDatasetSampleDocument
    Sample --> DatasetSampleDocument
    SampleView --> DatasetSampleDocument
    
    DatasetSampleDocument --> DatasetMixin
    NoDatasetSampleDocument --> NoDatasetMixin
    
    DatasetSampleDocument --> samples_collection
    DatasetSampleDocument --> frames_collection
    
    NoDatasetSampleDocument -.-> DatasetSampleDocument
```

Sources: [fiftyone/core/sample.py:41-68](), [fiftyone/core/sample.py:484-517](), [fiftyone/core/odm/sample.py:73-147](), [fiftyone/core/odm/mixins.py:55-780]()

### Sample Field Schema Definition

The `DatasetSampleDocument` defines default fields for all samples:

| Field | Type | Line Location | Purpose |
|-------|------|---------------|---------|
| `id` | `ObjectIdField` | sample.py:84 | Unique sample identifier |
| `filepath` | `StringField` | sample.py:85 | Path to media file |
| `tags` | `ListField` | sample.py:86 | List of string tags |
| `metadata` | `EmbeddedDocumentField` | sample.py:87 | Media metadata |
| `created_at` | `DateTimeField` | sample.py:88 | Creation timestamp |
| `last_modified_at` | `DateTimeField` | sample.py:89 | Last modification time |
| `_media_type` | `StringField` | sample.py:91 | Media type (image/video/group) |
| `_rand` | `FloatField` | sample.py:92 | Random value for shuffling |
| `_dataset_id` | `ObjectIdField` | sample.py:93 | Reference to parent dataset |

Sources: [fiftyone/core/odm/sample.py:84-94](), [fiftyone/core/sample.py:23-38]()

### Document State Transitions

Sample documents transition between states when added to datasets:

```mermaid
sequenceDiagram
    participant App as "Application"
    participant Sample as "Sample"
    participant NoDatasetDoc as "NoDatasetSampleDocument" 
    participant DatasetDoc as "DatasetSampleDocument"
    participant MongoDB as "MongoDB"
    
    App->>Sample: fo.Sample(filepath="...")
    Sample->>NoDatasetDoc: Create with filepath
    
    App->>Sample: dataset.add_sample(sample)
    Sample->>DatasetDoc: Convert to DatasetSampleDocument
    DatasetDoc->>MongoDB: Insert into samples.{name}
    
    App->>Sample: sample.field = value
    Sample->>DatasetDoc: Mark field as dirty
    
    App->>Sample: sample.save()
    DatasetDoc->>MongoDB: Update document
```

Sources: [fiftyone/core/sample.py:484-600](), [fiftyone/core/odm/sample.py:115-147](), [fiftyone/core/dataset.py:1986-2100]()

## Labels and Field System

The label and field system provides a flexible schema for storing annotations, predictions, and metadata with type safety and validation.

### Label Class Hierarchy

```mermaid
graph TB
    subgraph "Base Classes (labels.py)"
        Label["Label<br/>(Line 50)<br/>DynamicEmbeddedDocument"]
        _HasID["_HasID<br/>(Line 325)<br/>id + tags"]
        _HasAttributesDict["_HasAttributesDict<br/>(Line 201)<br/>attributes dict"]
    end
    
    subgraph "Simple Label Types"
        Regression["Regression<br/>(Line 398)"]
        Classification["Classification<br/>(Line 410)"]
        Detection["Detection<br/>(Line 438)"]
    end
    
    subgraph "Collection Label Types"
        Classifications["Classifications<br/>(Line 424)"]
        Detections["Detections<br/>(Line 675)"]
        Polylines["Polylines<br/>(Line 1458)"]
        Keypoints["Keypoints<br/>(Line 1719)"]
    end
    
    subgraph "Spatial Label Types"
        Polyline["Polyline<br/>(Line 1269)"]
        Segmentation["Segmentation<br/>(Line 1799)"]
        Heatmap["Heatmap<br/>(Line 1916)"]
        GeoLocation["GeoLocation<br/>(Line 2196)"]
    end
    
    Label --> _HasID
    Label --> _HasAttributesDict
    _HasID --> Regression
    _HasID --> Classification
    _HasAttributesDict --> Detection
    Label --> Classifications
    Label --> Detections
    Label --> Polylines
    Label --> Keypoints
    Label --> Polyline
    Label --> Segmentation
    Label --> Heatmap
    Label --> GeoLocation
```

Sources: [fiftyone/core/labels.py:50-134](), [fiftyone/core/labels.py:325-346](), [fiftyone/core/labels.py:398-2300]()

### Field Type System Architecture

```mermaid
graph TB
    subgraph "Core Field Classes (fields.py)"
        Field["Field<br/>(Line 359)<br/>MongoEngine Base"]
        ReadOnlyMixin["ReadOnlyMixin<br/>(Line 346)"]
    end
    
    subgraph "Primitive Fields (Lines 400-800)"
        StringField["StringField<br/>(Line 489)"]
        IntField["IntField<br/>(Line 440)"] 
        FloatField["FloatField<br/>(Line 463)"]
        BooleanField["BooleanField<br/>(Line 542)"]
        DateTimeField["DateTimeField<br/>(Line 628)"]
        ObjectIdField["ObjectIdField<br/>(Line 516)"]
    end
    
    subgraph "Container Fields (Lines 800-1200)"
        ListField["ListField<br/>(Line 889)"]
        DictField["DictField<br/>(Line 959)"]
        EmbeddedDocumentField["EmbeddedDocumentField<br/>(Line 1096)"]
    end
    
    subgraph "Specialized Fields (Lines 1200-2000)"
        VectorField["VectorField<br/>(Line 1241)"]
        ArrayField["ArrayField<br/>(Line 1397)"]
        ClassesField["ClassesField<br/>(Line 1644)"]
        MaskTargetsField["MaskTargetsField<br/>(Line 1712)"]
    end
    
    Field --> ReadOnlyMixin
    Field --> StringField
    Field --> IntField
    Field --> FloatField
    Field --> BooleanField
    Field --> DateTimeField
    Field --> ObjectIdField
    Field --> ListField
    Field --> DictField
    Field --> EmbeddedDocumentField
    Field --> VectorField
    Field --> ArrayField
    Field --> ClassesField
    Field --> MaskTargetsField
```

Sources: [fiftyone/core/fields.py:346-400](), [fiftyone/core/fields.py:440-800](), [fiftyone/core/fields.py:889-1200](), [fiftyone/core/fields.py:1241-2000]()

## ODM (Object Document Mapper) Architecture

The ODM layer handles the mapping between Python objects and MongoDB documents, providing schema management, validation, and persistence.

### ODM Component Architecture

```mermaid
graph TB
    subgraph "Python Objects"
        Dataset["Dataset"]
        Sample["Sample"]
        Label["Label"]
    end
    
    subgraph "ODM Layer"
        DatasetDocument["DatasetDocument"]
        SampleDocument["DatasetSampleDocument"]
        EmbeddedDocument["EmbeddedDocument"]
    end
    
    subgraph "MongoDB"
        DatasetsColl["datasets"]
        SamplesColl["samples.{name}"]
        FramesColl["frames.{name}"]
    end
    
    subgraph "Schema Management"
        FieldDocs["SampleFieldDocument[]"]
        FrameFieldDocs["FrameFieldDocument[]"]
    end
    
    Dataset --> DatasetDocument
    Sample --> SampleDocument
    Label --> EmbeddedDocument
    
    DatasetDocument --> DatasetsColl
    SampleDocument --> SamplesColl
    SampleDocument --> FramesColl
    
    DatasetDocument --> FieldDocs
    DatasetDocument --> FrameFieldDocs
```

Sources: [fiftyone/core/odm/dataset.py:58-160](), [fiftyone/core/odm/sample.py:73-103](), [fiftyone/core/odm/mixins.py:55-120]()

### Dynamic Schema Management

The ODM supports dynamic schema evolution where new fields can be added at runtime:

1. **Field Declaration**: New fields are automatically detected when assigned to samples
2. **Schema Registration**: Field definitions are stored in `SampleFieldDocument` objects
3. **Validation**: Runtime validation ensures type safety
4. **Migration**: Schema changes are propagated to the dataset metadata

Sources: [fiftyone/core/odm/mixins.py:129-203](), [fiftyone/core/odm/utils.py:350-450](), [fiftyone/core/dataset.py:1600-1700]()

### Document Lifecycle

```mermaid
sequenceDiagram
    participant App as "Application"
    participant Sample as "Sample"
    participant Doc as "SampleDocument" 
    participant MongoDB as "MongoDB"
    
    App->>Sample: Create sample
    Sample->>Doc: NoDatasetSampleDocument
    
    App->>Sample: Add to dataset
    Sample->>Doc: Convert to DatasetSampleDocument
    Doc->>MongoDB: Insert document
    
    App->>Sample: Modify field
    Sample->>Doc: Mark field dirty
    
    App->>Sample: Save changes
    Doc->>MongoDB: Update document
```

Sources: [fiftyone/core/sample.py:484-600](), [fiftyone/core/odm/sample.py:104-147](), [fiftyone/core/odm/mixins.py:200-300]()

---

