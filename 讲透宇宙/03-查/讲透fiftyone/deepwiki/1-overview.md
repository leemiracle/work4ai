<!-- source: DeepWiki mcp.deepwiki.com · repo voxel51/fiftyone · page 1 Overview · fetched 2026-10-21 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/README.md](app/README.md)
- [docs/source/_includes/substitutions.rst](docs/source/_includes/substitutions.rst)
- [docs/source/_static/images/tutorials/pandas_tutorial.png](docs/source/_static/images/tutorials/pandas_tutorial.png)
- [docs/source/_static/images/tutorials/small_object_detection.jpg](docs/source/_static/images/tutorials/small_object_detection.jpg)
- [docs/source/cheat_sheets/fiftyone_terminology.rst](docs/source/cheat_sheets/fiftyone_terminology.rst)
- [docs/source/cheat_sheets/filtering_cheat_sheet.rst](docs/source/cheat_sheets/filtering_cheat_sheet.rst)
- [docs/source/cheat_sheets/index.rst](docs/source/cheat_sheets/index.rst)
- [docs/source/cheat_sheets/pandas_vs_fiftyone.rst](docs/source/cheat_sheets/pandas_vs_fiftyone.rst)
- [docs/source/cheat_sheets/views_cheat_sheet.rst](docs/source/cheat_sheets/views_cheat_sheet.rst)
- [docs/source/faq/index.rst](docs/source/faq/index.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/integrations/index.rst](docs/source/integrations/index.rst)
- [docs/source/recipes/index.rst](docs/source/recipes/index.rst)
- [docs/source/recipes/remove_duplicate_annos.ipynb](docs/source/recipes/remove_duplicate_annos.ipynb)
- [docs/source/release-notes.rst](docs/source/release-notes.rst)
- [docs/source/tutorials/cosmos-transfer-integration.ipynb](docs/source/tutorials/cosmos-transfer-integration.ipynb)
- [docs/source/tutorials/gemini_vision.ipynb](docs/source/tutorials/gemini_vision.ipynb)
- [docs/source/tutorials/image_embeddings.ipynb](docs/source/tutorials/image_embeddings.ipynb)
- [docs/source/tutorials/images/sahi_base_model.gif](docs/source/tutorials/images/sahi_base_model.gif)
- [docs/source/tutorials/images/sahi_base_model_predictions_filtered.jpg](docs/source/tutorials/images/sahi_base_model_predictions_filtered.jpg)
- [docs/source/tutorials/images/sahi_dataset.jpg](docs/source/tutorials/images/sahi_dataset.jpg)
- [docs/source/tutorials/images/sahi_high_conf_fp_view.jpg](docs/source/tutorials/images/sahi_high_conf_fp_view.jpg)
- [docs/source/tutorials/images/sahi_slices.gif](docs/source/tutorials/images/sahi_slices.gif)
- [docs/source/tutorials/images/sahi_small_boxes_view.gif](docs/source/tutorials/images/sahi_small_boxes_view.gif)
- [docs/source/tutorials/index.rst](docs/source/tutorials/index.rst)
- [docs/source/tutorials/open_images.ipynb](docs/source/tutorials/open_images.ipynb)
- [docs/source/tutorials/pandas_comparison.ipynb](docs/source/tutorials/pandas_comparison.ipynb)
- [docs/source/tutorials/small_object_detection.ipynb](docs/source/tutorials/small_object_detection.ipynb)
- [docs/source/user_guide/app.rst](docs/source/user_guide/app.rst)
- [docs/source/user_guide/basics.rst](docs/source/user_guide/basics.rst)
- [docs/source/user_guide/config.rst](docs/source/user_guide/config.rst)
- [docs/source/user_guide/evaluation.rst](docs/source/user_guide/evaluation.rst)
- [docs/source/user_guide/index.rst](docs/source/user_guide/index.rst)
- [docs/source/user_guide/plots.rst](docs/source/user_guide/plots.rst)
- [docs/source/user_guide/using_aggregations.rst](docs/source/user_guide/using_aggregations.rst)
- [docs/source/user_guide/using_datasets.rst](docs/source/user_guide/using_datasets.rst)
- [docs/source/user_guide/using_views.rst](docs/source/user_guide/using_views.rst)
- [fiftyone/__public__.py](fiftyone/__public__.py)
- [fiftyone/core/aggregations.py](fiftyone/core/aggregations.py)
- [fiftyone/core/clips.py](fiftyone/core/clips.py)
- [fiftyone/core/collections.py](fiftyone/core/collections.py)
- [fiftyone/core/config.py](fiftyone/core/config.py)
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
- [install.bat](install.bat)
- [tests/unittests/aggregation_tests.py](tests/unittests/aggregation_tests.py)
- [tests/unittests/dataset_tests.py](tests/unittests/dataset_tests.py)
- [tests/unittests/odm_tests.py](tests/unittests/odm_tests.py)
- [tests/unittests/patches_tests.py](tests/unittests/patches_tests.py)
- [tests/unittests/video_tests.py](tests/unittests/video_tests.py)
- [tests/unittests/view_tests.py](tests/unittests/view_tests.py)

</details>



FiftyOne is an open-source tool for building high-quality datasets and computer vision models. It provides a platform for dataset management, model evaluation, and data visualization through a Python library and an interactive web application.

The public Python API is defined in [fiftyone/__public__.py](), which is re-exported as the `fiftyone` top-level package (`import fiftyone as fo`). The system architecture centers around the `Dataset` class in `fiftyone.core.dataset`, backed by MongoDB via a mongoengine ODM layer. A Starlette/Strawberry GraphQL server (`fiftyone.server`) provides APIs for a React frontend. The platform supports multiple media types (`image`, `video`, `3d`, `point-cloud`, `group`), a wide range of annotation formats, and integrates with ML frameworks via the Model Zoo and `apply_model`.

This overview covers the high-level architecture, core components, and data flow patterns. For detailed information about specific subsystems, see:

| Section | Topic |
|---------|-------|
| [Core Data Model](#2) | Dataset, Sample, View, Labels, ODM layer |
| [Server Architecture](#3) | Starlette server, GraphQL API, session management |
| [Frontend Architecture](#4) | React app, Looker viewer, 3D visualization, state management |
| [Data Processing and I/O](#5) | Import/export formats, Dataset Zoo |
| [Model Integration and Evaluation](#6) | Model Zoo, `apply_model`, evaluation framework |
| [Extensibility Framework](#9) | Operators, delegated ops, plugin system |
| [Command Line Interface](#10) | `fiftyone` CLI commands |

## System Architecture

FiftyOne's architecture is organized around several key subsystems that work together to provide comprehensive dataset management capabilities:

## FiftyOne System Architecture

```mermaid
graph TB
    subgraph "Python Library (fiftyone.*)"
        PublicAPI["fiftyone/__public__.py\nPublic API surface (import fiftyone as fo)"]
        Dataset["fiftyone.core.dataset.Dataset\n(DatasetSingleton metaclass)"]
        SampleCollection["fiftyone.core.collections.SampleCollection\nAbstract base for Dataset and DatasetView"]
        DatasetView["fiftyone.core.view.DatasetView\nChained ViewStage pipeline"]
        ViewStage["fiftyone.core.stages.ViewStage\nAbstract pipeline stage"]
        Aggregation["fiftyone.core.aggregations.Aggregation\nCount, Bounds, Mean, Values, etc."]
        ODM["fiftyone.core.odm\nMongoEngine document classes"]
    end

    subgraph "Server (fiftyone.server.*)"
        ServerMain["fiftyone.server.main\nHypercorn ASGI entry point"]
        GraphQLApp["fiftyone.server.app\nStarlette + Strawberry GraphQL"]
        StateDesc["fiftyone.core.state.StateDescription\nShared session state"]
        MongoDB[("MongoDB\nDocument storage")]
    end

    subgraph "Frontend (app/packages/*)"
        ReactApp["@fiftyone/app\nMain React application"]
        LookerCore["@fiftyone/looker\n2D image/video viewer"]
        Looker3D["@fiftyone/looker-3d\n3D / point-cloud viewer"]
        StatePackage["@fiftyone/state\nRecoil atoms and selectors"]
    end

    subgraph "Extensibility"
        Operators["fiftyone.operators\nOperator / plugin framework"]
        Zoo["fiftyone.zoo\nModel Zoo + Dataset Zoo"]
        Evaluation["fiftyone.core.evaluation\nBaseRun evaluation framework"]
    end

    PublicAPI --> Dataset
    Dataset --> SampleCollection
    SampleCollection --> DatasetView
    DatasetView --> ViewStage
    SampleCollection --> Aggregation
    Dataset --> ODM
    ODM --> MongoDB

    ServerMain --> GraphQLApp
    GraphQLApp --> StateDesc
    StateDesc --> Dataset

    ReactApp --> LookerCore
    ReactApp --> Looker3D
    ReactApp --> StatePackage
    StatePackage --> GraphQLApp

    Operators --> GraphQLApp
    Zoo --> Dataset
    Evaluation --> Dataset
```

Sources: [fiftyone/__public__.py:1-50](), [fiftyone/core/dataset.py:271-310](), [fiftyone/core/collections.py:329-340](), [fiftyone/core/view.py:33-61](), [fiftyone/core/stages.py:48-58](), [fiftyone/core/aggregations.py:35-58]()

## Core Data Model

The foundation of FiftyOne is built around the `Dataset` class and its associated data structures. `Dataset` uses the `DatasetSingleton` metaclass so that all calls with the same dataset name in a process return the same Python object.

## Core Data Model Architecture

```mermaid
graph TB
    subgraph "Collection Layer"
        SampleCollection["SampleCollection\nfiftyone.core.collections\nAbstract base class"]
        Dataset["Dataset\nfiftyone.core.dataset\nDatasetSingleton metaclass"]
        DatasetView["DatasetView\nfiftyone.core.view\nChained ViewStage result"]
        SaveContext["SaveContext\nfiftyone.core.collections\nBatched sample writes"]
    end

    subgraph "Sample Layer"
        Sample["Sample\nfiftyone.core.sample\nIndividual media document"]
        SampleView["SampleView\nfiftyone.core.sample\nFiltered sample instance"]
        Frames["Frames\nfiftyone.core.frame\nOrdered frame dict (video)"]
        Frame["Frame\nfiftyone.core.frame\nSingle video frame"]
    end

    subgraph "Pipeline"
        ViewStage["ViewStage\nfiftyone.core.stages\nAbstract pipeline stage"]
        Aggregation["Aggregation\nfiftyone.core.aggregations\nCount/Bounds/Mean/Values/..."]
        ViewExpression["ViewField / ViewExpression\nfiftyone.core.expressions\nMongoDB expression builder"]
    end

    subgraph "Schema and Labels"
        Field["Field\nfiftyone.core.fields\nBooleanField, StringField, ..."]
        Label["Label\nfiftyone.core.labels\nClassification, Detection, ..."]
        Metadata["Metadata\nfiftyone.core.metadata\nImageMetadata, VideoMetadata"]
    end

    subgraph "ODM (fiftyone.core.odm.*)"
        DatasetDoc["DatasetDocument\nfiftyone.core.odm.dataset\nDataset backing document"]
        SampleDoc["DatasetSampleDocument\nfiftyone.core.odm.sample\nSample backing document"]
        FrameDoc["DatasetFrameDocument\nfiftyone.core.odm.frame\nFrame backing document"]
        SampleFieldDoc["SampleFieldDocument\nfiftyone.core.odm.dataset\nField schema record"]
    end

    Dataset --> SampleCollection
    DatasetView --> SampleCollection
    Dataset --> DatasetView
    DatasetView --> ViewStage
    SampleCollection --> Aggregation
    Aggregation --> ViewExpression
    SampleCollection --> SaveContext

    Dataset --> Sample
    Sample --> SampleView
    Sample --> Frames
    Frames --> Frame

    Sample --> Field
    Sample --> Label
    Sample --> Metadata

    Dataset --> DatasetDoc
    Sample --> SampleDoc
    Frame --> FrameDoc
    DatasetDoc --> SampleFieldDoc
```

Sources: [fiftyone/core/dataset.py:271-310](), [fiftyone/core/collections.py:329-340](), [fiftyone/core/sample.py:44-100](), [fiftyone/core/view.py:33-61](), [fiftyone/core/stages.py:48-58](), [fiftyone/core/aggregations.py:35-58](), [fiftyone/core/labels.py:50-60](), [fiftyone/core/odm/sample.py:73-127](), [fiftyone/core/odm/dataset.py:58-80]()

## Server and API Architecture

The server layer provides GraphQL endpoints for frontend communication and state management. It is started via `fo.launch_app()`, which launches a `hypercorn` ASGI process hosting a Starlette application with a Strawberry GraphQL schema.

## Server and GraphQL Architecture

```mermaid
graph TB
    subgraph "ASGI Layer"
        HypercornServer["hypercorn.asyncio.serve\nASGI server runtime"]
        ServerMain["fiftyone.server.main\nServer entry point"]
        AppFactory["fiftyone.server.app\nStarlette application factory"]
        EventSystem["fiftyone.server.events\nServer-sent events (SSE)"]
    end

    subgraph "GraphQL API (Strawberry)"
        Schema["strawberry.Schema\nGraphQL schema root"]
        QueryResolvers["fiftyone.server.query\nQuery resolvers"]
        MutationResolvers["fiftyone.server.mutation\nMutation resolvers"]
        AggregationEndpoint["fiftyone.server.aggregations\nAggregation HTTP endpoint"]
    end

    subgraph "Session and State"
        StateDescription["fiftyone.core.state.StateDescription\nSerializable shared state"]
        Session["fiftyone.core.session.Session\nProgrammatic App control"]
        LaunchApp["fo.launch_app()\nfiftyone.core.session"]
    end

    subgraph "Database"
        DBConn["fiftyone.core.odm.database.get_db_conn()\nMongoDB connection"]
        ViewPipeline["DatasetView._aggregate()\nMongoDB aggregation pipeline"]
        MongoDB[("MongoDB")]
    end

    HypercornServer --> ServerMain
    ServerMain --> AppFactory
    AppFactory --> Schema
    AppFactory --> EventSystem
    AppFactory --> AggregationEndpoint

    Schema --> QueryResolvers
    Schema --> MutationResolvers

    QueryResolvers --> StateDescription
    StateDescription --> Session
    LaunchApp --> Session
    LaunchApp --> HypercornServer

    QueryResolvers --> DBConn
    AggregationEndpoint --> ViewPipeline
    ViewPipeline --> DBConn
    DBConn --> MongoDB
```

Sources: [fiftyone/core/collections.py:329-340](), [fiftyone/core/view.py:33-61](), [fiftyone/core/odm/mixins.py:56-80]()

## Frontend Application Structure

The frontend is a Yarn workspace monorepo under `app/packages/`. The main application is `@fiftyone/app`, which coordinates media viewing, state management, and the plugin/operator UI.

## Frontend Package Architecture

```mermaid
graph TB
    subgraph "Application Shell"
        AppPackage["@fiftyone/app\napp/packages/app\nMain React application root"]
        CorePackage["@fiftyone/core\napp/packages/core\nBusiness logic and shared hooks"]
        ComponentsPackage["@fiftyone/components\napp/packages/components\nReusable UI components"]
        UtilitiesPackage["@fiftyone/utilities\napp/packages/utilities\nShared utility functions"]
    end

    subgraph "Media Rendering"
        LookerPackage["@fiftyone/looker\napp/packages/looker\n2D image/video overlay engine"]
        Looker3DPackage["@fiftyone/looker-3d\napp/packages/looker-3d\n3D / point-cloud renderer (Three.js)"]
        FlashlightPackage["@fiftyone/flashlight\napp/packages/flashlight\nVirtualized sample grid"]
    end

    subgraph "State and Data"
        StatePackage["@fiftyone/state\napp/packages/state\nRecoil atoms and selectors"]
        RelayPackage["@fiftyone/relay\napp/packages/relay\nGraphQL client and fragments"]
    end

    subgraph "Extensibility UI"
        OperatorsPackage["@fiftyone/operators\napp/packages/operators\nOperator execution and registry"]
        PluginsPackage["@fiftyone/plugins\napp/packages/plugins\nPlugin loading and management"]
        PanelsPackage["@fiftyone/panels\napp/packages/panels\nCustom panel framework"]
    end

    AppPackage --> CorePackage
    AppPackage --> LookerPackage
    AppPackage --> FlashlightPackage
    AppPackage --> OperatorsPackage

    CorePackage --> ComponentsPackage
    CorePackage --> StatePackage
    CorePackage --> UtilitiesPackage

    LookerPackage --> Looker3DPackage

    StatePackage --> RelayPackage

    OperatorsPackage --> PluginsPackage
    OperatorsPackage --> PanelsPackage
```

Sources: [docs/source/user_guide/app.rst:1-60]()

## Data Flow Architecture

The system processes data through several key pathways from ingestion to visualization:

```mermaid
graph LR
    subgraph "Data Sources"
        LocalFiles["Local Media Files<br/>Images, Videos, 3D"]
        CloudStorage["Cloud Storage<br/>S3, GCS, Azure"]
        Annotations["Annotation Formats<br/>COCO, YOLO, CVAT"]
        Models["ML Models<br/>PyTorch, TensorFlow"]
    end
    
    subgraph "Ingestion Layer"
        DataImporter["fiftyone.utils.data.DataImporter<br/>Format-specific importers"]
        DatasetImporter["fiftyone.utils.data.DatasetImporter<br/>Dataset format handlers"]
        ModelApplicator["fiftyone.core.models<br/>Model inference engine"]
    end
    
    subgraph "Core Processing"
        Dataset["fiftyone.core.dataset.Dataset<br/>Central data container"]
        ViewEngine["fiftyone.core.view<br/>Query processing engine"]
        Aggregator["fiftyone.core.aggregations<br/>Data aggregation"]
    end
    
    subgraph "Output Systems"
        AppVisualization["FiftyOne App<br/>Interactive visualization"]
        DataExporter["fiftyone.utils.data.DataExporter<br/>Format-specific exporters"]
        BrainInsights["fiftyone.brain<br/>ML-powered analysis"]
    end
    
    LocalFiles --> DataImporter
    CloudStorage --> DataImporter
    Annotations --> DatasetImporter
    Models --> ModelApplicator
    
    DataImporter --> Dataset
    DatasetImporter --> Dataset
    ModelApplicator --> Dataset
    
    Dataset --> ViewEngine
    ViewEngine --> Aggregator
    
    ViewEngine --> AppVisualization
    Dataset --> DataExporter
    Aggregator --> BrainInsights
```

Sources: [docs/source/user_guide/using_datasets.rst:1-200](), [docs/source/user_guide/import_datasets.rst:1-100]()

## Key Technologies and Dependencies

| Layer | Technology | Role in FiftyOne |
|-------|------------|-----------------|
| Python library | Python 3.9–3.12 | Core application logic |
| Database | MongoDB + `mongoengine` | Document storage and ODM (`fiftyone.core.odm`) |
| DB distribution | `fiftyone-db` package | Bundled MongoDB for local use |
| ASGI server | `hypercorn` + `starlette` | Hosts `fiftyone.server` |
| API schema | `strawberry-graphql` | GraphQL schema for `fiftyone.server.query/mutation` |
| Frontend | React 18 + TypeScript | `@fiftyone/app` and related packages |
| Frontend state | Recoil | `@fiftyone/state` atoms and selectors |
| GraphQL client | Relay | `@fiftyone/relay` fragments |
| Build tooling | Vite + Yarn Workspaces | `app/` monorepo build pipeline |
| Image/video | `opencv-python`, `Pillow`, `eta` | Media processing in `fiftyone.utils` |
| 3D rendering | Three.js + WebGL | `@fiftyone/looker-3d` |
| ML frameworks | PyTorch, HuggingFace Transformers | Model Zoo wrappers in `fiftyone.utils.torch_utils` |
| Numeric | NumPy, SciPy, scikit-learn | Label utilities, evaluation, brain |
| Config | `fiftyone.core.config.FiftyOneConfig` | Loaded from `~/.fiftyone/config.json` or env vars |

Sources: [fiftyone/core/config.py:1-30](), [fiftyone/core/odm/mixins.py:1-35](), [docs/source/user_guide/config.rst:1-50]()

## Plugin and Extension System

FiftyOne provides a comprehensive plugin framework for extending functionality:

## Plugin and Operator Framework

```mermaid
graph TB
    subgraph "Operator Core"
        OperatorBase["fiftyone.operators.operator.Operator<br/>Base operator class"]
        ExecutorService["fiftyone.operators.executor.ExecutorService<br/>Operator execution orchestrator"]
        TypeSystem["fiftyone.operators.types<br/>Input/output type definitions"]
        Registry["fiftyone.operators.registry<br/>Operator discovery and registration"]
    end
    
    subgraph "Execution Context"
        ExecutionContext["fiftyone.operators.executor.ExecutionContext<br/>Runtime execution environment"]
        StoreService["fiftyone.operators.store.ExecutionStoreService<br/>Persistent operator state storage"]
        DelegatedOps["fiftyone.operators.delegated<br/>Background task execution"]
    end
    
    subgraph "Frontend Integration"
        OperatorIO["@fiftyone/operators/src/OperatorIO<br/>Input/output component rendering"]
        OperatorBrowser["@fiftyone/operators/src/OperatorBrowser<br/>Operator selection interface"]
        PanelFramework["@fiftyone/panels<br/>Custom panel development framework"]
    end
    
    subgraph "Extension Points"
        CLIExtensions["fiftyone.core.cli<br/>Custom CLI command registration"]
        ServerHooks["fiftyone.server<br/>Custom GraphQL resolvers"]
        PluginManager["fiftyone.plugins<br/>Plugin installation and management"]
    end
    
    OperatorBase --> ExecutorService
    ExecutorService --> TypeSystem
    ExecutorService --> Registry
    
    ExecutorService --> ExecutionContext
    ExecutionContext --> StoreService
    ExecutionContext --> DelegatedOps
    
    ExecutorService --> OperatorIO
    OperatorIO --> OperatorBrowser
    OperatorIO --> PanelFramework
    
    Registry --> CLIExtensions
    ExecutorService --> ServerHooks
    Registry --> PluginManager
```

Sources: [fiftyone/operators/executor.py:1-50](), [fiftyone/operators/operator.py:1-100](), [fiftyone/operators/store.py:1-50](), [fiftyone/operators/registry.py:1-50]()

The FiftyOne system provides a unified platform for dataset management, model evaluation, and data visualization through its modular architecture and extensible plugin system. The core Python library handles data storage and processing, while the React frontend provides interactive visualization capabilities, all connected through a GraphQL API layer that enables real-time collaboration and analysis.

---

