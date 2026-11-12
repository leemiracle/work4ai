<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/responsible-ai-toolbox · page 4 TypeScript Dashboard Architecture · fetched 2026-10-26 -->

# TypeScript Dashboard Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/dashboard-e2e/src/describer/interpret/individualFeatureImportance/describeSubBarChart.ts](apps/dashboard-e2e/src/describer/interpret/individualFeatureImportance/describeSubBarChart.ts)
- [apps/widget/src/app/ModelAssessment.tsx](apps/widget/src/app/ModelAssessment.tsx)
- [libs/core-ui/src/index.ts](libs/core-ui/src/index.ts)
- [libs/core-ui/src/lib/Context/ModelAssessmentContext.tsx](libs/core-ui/src/lib/Context/ModelAssessmentContext.tsx)
- [libs/core-ui/src/lib/Interfaces/IExplanationContext.ts](libs/core-ui/src/lib/Interfaces/IExplanationContext.ts)
- [libs/core-ui/src/lib/util/StatisticsUtils.ts](libs/core-ui/src/lib/util/StatisticsUtils.ts)
- [libs/e2e/src/lib/describer/interpretText/validateBarChart.ts](libs/e2e/src/lib/describer/interpretText/validateBarChart.ts)
- [libs/error-analysis/src/index.ts](libs/error-analysis/src/index.ts)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/MetricSelector/MetricSelector.tsx](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/MetricSelector/MetricSelector.tsx)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Interfaces/IErrorAnalysisDashboardState.ts](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Interfaces/IErrorAnalysisDashboardState.ts)
- [libs/interpret-vision/src/lib/VisionExplanationDashboard/Interfaces/IVisionExplanationDashboardProps.ts](libs/interpret-vision/src/lib/VisionExplanationDashboard/Interfaces/IVisionExplanationDashboardProps.ts)
- [libs/localization/src/lib/en.json](libs/localization/src/lib/en.json)
- [libs/mlchartlib/src/lib/components/AccessibleChart.tsx](libs/mlchartlib/src/lib/components/AccessibleChart.tsx)
- [libs/model-assessment/src/lib/ModelAssessmentDashboard/Context/buildModelAssessmentContext.ts](libs/model-assessment/src/lib/ModelAssessmentDashboard/Context/buildModelAssessmentContext.ts)
- [libs/model-assessment/src/lib/ModelAssessmentDashboard/Controls/ModelOverview/ModelOverview.tsx](libs/model-assessment/src/lib/ModelAssessmentDashboard/Controls/ModelOverview/ModelOverview.tsx)
- [libs/model-assessment/src/lib/ModelAssessmentDashboard/Controls/ModelOverview/StatsTableUtils.ts](libs/model-assessment/src/lib/ModelAssessmentDashboard/Controls/ModelOverview/StatsTableUtils.ts)
- [libs/model-assessment/src/lib/ModelAssessmentDashboard/Controls/TabsView/TabsViewProps.ts](libs/model-assessment/src/lib/ModelAssessmentDashboard/Controls/TabsView/TabsViewProps.ts)
- [libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboard.tsx](libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboard.tsx)
- [libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboardProps.ts](libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboardProps.ts)
- [libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboardState.ts](libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboardState.ts)
- [nx.json](nx.json)
- [package.json](package.json)
- [raiwidgets/raiwidgets/responsibleai_dashboard.py](raiwidgets/raiwidgets/responsibleai_dashboard.py)
- [raiwidgets/raiwidgets/responsibleai_dashboard_input.py](raiwidgets/raiwidgets/responsibleai_dashboard_input.py)
- [tsconfig.base.json](tsconfig.base.json)
- [workspace.json](workspace.json)
- [yarn.lock](yarn.lock)

</details>



## Purpose and Scope

This document describes the TypeScript/React dashboard architecture, which provides the interactive web interface for the Responsible AI Toolbox. The dashboard is built as an Nx monorepo containing 14+ TypeScript libraries that render various analysis views including error analysis, model explanations, causal analysis, and counterfactuals.

For information about the Python backend that serves data to this dashboard, see [Python Backend Architecture](#3). For details on specific dashboard components, see [Model Assessment Dashboard](#4.2) and [Error Analysis Dashboard](#4.3).

---

## Nx Monorepo Structure

The TypeScript codebase is organized as an Nx monorepo located in the `libs/` directory. This structure allows multiple libraries to share code while maintaining independent versioning and build configurations.

**Monorepo Library Organization**

```mermaid
graph TB
    subgraph "Nx Monorepo"
        subgraph "Core Libraries"
            core-ui["core-ui<br/>Shared components, utilities,<br/>JointDataset, Context"]
            localization["localization<br/>i18n strings"]
            mlchartlib["mlchartlib<br/>Chart components<br/>Plotly wrapper"]
        end
        
        subgraph "Feature Libraries"
            model-assessment["model-assessment<br/>ModelAssessmentDashboard<br/>Main orchestrator"]
            error-analysis["error-analysis<br/>TreeMap, HeatMap<br/>Error exploration"]
            interpret["interpret<br/>Model explanations<br/>Feature importance"]
            causality["causality<br/>Causal analysis views"]
            counterfactuals["counterfactuals<br/>What-If panel"]
            dataset-explorer["dataset-explorer<br/>Data visualization"]
            fairness["fairness<br/>Fairness metrics"]
            interpret-vision["interpret-vision<br/>Image explanations"]
            interpret-text["interpret-text<br/>Text explanations"]
            forecasting["forecasting<br/>Time series views"]
        end
        
        subgraph "Applications"
            dashboard["dashboard<br/>Standalone app"]
            widget["widget<br/>Jupyter widget app"]
        end
    end
    
    model-assessment --> core-ui
    model-assessment --> error-analysis
    model-assessment --> interpret
    model-assessment --> causality
    model-assessment --> counterfactuals
    model-assessment --> dataset-explorer
    
    error-analysis --> core-ui
    error-analysis --> mlchartlib
    interpret --> core-ui
    causality --> core-ui
    counterfactuals --> core-ui
    dataset-explorer --> core-ui
    fairness --> core-ui
    interpret-vision --> core-ui
    interpret-text --> core-ui
    forecasting --> core-ui
    
    core-ui --> localization
    core-ui --> mlchartlib
    
    dashboard --> model-assessment
    widget --> model-assessment
```

Sources: [workspace.json:1-1000](), [nx.json:1-80](), [package.json:1-158]()

---

## Core Library: `core-ui`

The `core-ui` library provides foundational abstractions used across all dashboard components.

| Component | Description | Key Exports |
|-----------|-------------|-------------|
| **JointDataset** | Unified dataset representation merging features, predictions, labels | `JointDataset` class |
| **Cohort System** | Data filtering and segmentation | `Cohort`, `ErrorCohort`, `DatasetCohort` |
| **Context Provider** | React Context for state sharing | `ModelAssessmentContext` |
| **Chart Components** | Shared visualization primitives | `BasicHighChart`, `FeatureImportanceBar` |
| **Utilities** | Statistical calculations, data processing | `generateMetrics`, `StatisticsUtils` |

**Key Classes and Interfaces**

- **`JointDataset`**: [libs/core-ui/src/lib/util/JointDataset.ts:1-500]() - Combines features, predictions, labels, and explanations into a single queryable dataset
- **`ErrorCohort`**: [libs/core-ui/src/lib/Cohort/ErrorCohort.ts:1-200]() - Represents a filtered subset of data with associated error metrics
- **`ModelAssessmentContext`**: [libs/core-ui/src/lib/Context/ModelAssessmentContext.tsx:1-221]() - React Context providing dataset, cohorts, and backend request functions to all components

Sources: [libs/core-ui/src/index.ts:1-129](), [libs/core-ui/src/lib/Context/ModelAssessmentContext.tsx:1-221]()

---

## Component Hierarchy

The dashboard follows a hierarchical React component structure with `ModelAssessmentDashboard` as the root.

**Component Tree**

```mermaid
graph TB
    MAD["ModelAssessmentDashboard<br/>(Root Component)"]
    
    subgraph "Top Level"
        MainMenu["MainMenu<br/>Tab selector, cohort switcher"]
        TabsView["TabsView<br/>Renders active tabs"]
        SaveCohort["SaveCohort<br/>Modal for saving cohorts"]
    end
    
    subgraph "Tab Components"
        ModelOverview["ModelOverview<br/>Metrics and disaggregated analysis"]
        DataExplorer["DataExplorer<br/>Scatter plots, table view"]
        ErrorAnalysis["ErrorAnalysis<br/>TreeMap/HeatMap views"]
        Interpret["FeatureImportances<br/>Global/local explanations"]
        Causal["CausalAnalysis<br/>Treatment effects, policy"]
        Counterfactual["CounterfactualPanel<br/>What-If scenarios"]
        VisionTab["VisionExplanationDashboard<br/>Image-specific views"]
        TextTab["TextExplanationDashboard<br/>Text-specific views"]
    end
    
    subgraph "ModelOverview Sub-components"
        DatasetCohortStats["DatasetCohortStatsTable<br/>Cohort comparison table"]
        DisaggregatedAnalysis["DisaggregatedAnalysisTable<br/>Feature-based heatmap"]
        ChartPivot["ModelOverviewChartPivot<br/>Bar/Box chart views"]
        MetricFlyout["MetricConfigurationFlyout"]
        FeatureFlyout["FeatureConfigurationFlyout"]
    end
    
    subgraph "ErrorAnalysis Sub-components"
        TreeView["TreeViewRenderer<br/>D3 tree visualization"]
        MatrixFilter["MatrixFilter<br/>Highcharts heatmap"]
        FeatureList["FeatureList<br/>Feature selection panel"]
    end
    
    MAD --> MainMenu
    MAD --> TabsView
    MAD --> SaveCohort
    
    TabsView --> ModelOverview
    TabsView --> DataExplorer
    TabsView --> ErrorAnalysis
    TabsView --> Interpret
    TabsView --> Causal
    TabsView --> Counterfactual
    TabsView --> VisionTab
    TabsView --> TextTab
    
    ModelOverview --> DatasetCohortStats
    ModelOverview --> DisaggregatedAnalysis
    ModelOverview --> ChartPivot
    ModelOverview --> MetricFlyout
    ModelOverview --> FeatureFlyout
    
    ErrorAnalysis --> TreeView
    ErrorAnalysis --> MatrixFilter
    ErrorAnalysis --> FeatureList
```

Sources: [libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboard.tsx:1-379](), [libs/model-assessment/src/lib/ModelAssessmentDashboard/Controls/TabsView/TabsView.tsx:1-200](), [libs/model-assessment/src/lib/ModelAssessmentDashboard/Controls/ModelOverview/ModelOverview.tsx:1-600]()

---

## State Management: Context Pattern

The dashboard uses React Context to share state across components without prop drilling.

**State Flow Diagram**

```mermaid
graph TB
    subgraph "Component State"
        MADState["ModelAssessmentDashboard.state<br/>- cohorts: ErrorCohort[]<br/>- selectedCohort: ErrorCohort<br/>- jointDataset: JointDataset<br/>- modelMetadata<br/>- activeGlobalTabs"]
    end
    
    subgraph "Context Provider"
        ContextProvider["ModelAssessmentContext.Provider<br/>Wraps entire dashboard"]
        ContextValue["Context Value Object<br/>- dataset: IDataset<br/>- errorCohorts<br/>- baseErrorCohort<br/>- selectedErrorCohort<br/>- addCohort()<br/>- deleteCohort()<br/>- shiftErrorCohort()<br/>- requestPredictions()<br/>- requestDebugML()<br/>- requestMatrix()<br/>- telemetryHook()"]
    end
    
    subgraph "Consumer Components"
        ModelOverview2["ModelOverview<br/>useContext(ModelAssessmentContext)"]
        ErrorAnalysis2["ErrorAnalysisDashboard<br/>static contextType"]
        Causal2["CausalAnalysis<br/>useContext()"]
    end
    
    MADState --> ContextValue
    ContextValue --> ContextProvider
    ContextProvider --> ModelOverview2
    ContextProvider --> ErrorAnalysis2
    ContextProvider --> Causal2
    
    ModelOverview2 -->|"setState()"| MADState
    ErrorAnalysis2 -->|"addCohort()"| MADState
    Causal2 -->|"shiftErrorCohort()"| MADState
```

**Context Interface**

The `IModelAssessmentContext` interface defines all shared state and callbacks:

```typescript
// Key properties from ModelAssessmentContext
interface IModelAssessmentContext {
  dataset: IDataset;
  jointDataset: JointDataset;
  errorCohorts: ErrorCohort[];
  baseErrorCohort: ErrorCohort;
  selectedErrorCohort: ErrorCohort;
  modelMetadata: IExplanationModelMetadata;
  
  // Backend request functions
  requestDebugML?: (request: any[]) => Promise<IErrorAnalysisTreeNode[]>;
  requestMatrix?: (request: any[]) => Promise<IErrorAnalysisMatrix>;
  requestPredictions?: (request: any[]) => Promise<any[]>;
  requestExp?: (index: number | number[]) => Promise<any[]>;
  
  // Cohort management callbacks
  addCohort(cohort: Cohort, switchNew?: boolean): void;
  editCohort(cohort: Cohort, switchNew?: boolean): void;
  deleteCohort(cohort: ErrorCohort): void;
  shiftErrorCohort(cohort: ErrorCohort): void;
}
```

Sources: [libs/core-ui/src/lib/Context/ModelAssessmentContext.tsx:28-221](), [libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboard.tsx:56-175]()

---

## Backend Communication

Dashboard components communicate with the Python Flask backend via HTTP POST requests and WebSocket connections.

**Request Flow**

```mermaid
sequenceDiagram
    participant User as User Interaction
    participant Component as React Component
    participant Context as ModelAssessmentContext
    participant Flask as Flask Backend
    participant Manager as Python Manager
    
    User->>Component: Click TreeMap node
    Component->>Context: requestDebugML(filters)
    Context->>Flask: POST /tree
    Flask->>Manager: ErrorAnalysisManager.compute_error_tree()
    Manager-->>Flask: JSON tree structure
    Flask-->>Context: HTTP Response
    Context-->>Component: Update state
    Component-->>User: Render tree visualization
```

**Request Functions**

Request functions are injected into the Context from the widget app:

| Function | Endpoint | Purpose | Python Handler |
|----------|----------|---------|----------------|
| `requestDebugML` | `/tree` | Get error tree structure | `ResponsibleAIDashboardInput.debug_ml()` |
| `requestMatrix` | `/matrix` | Get error heatmap data | `ResponsibleAIDashboardInput.matrix()` |
| `requestPredictions` | `/predict` | Get model predictions | `ResponsibleAIDashboardInput.on_predict()` |
| `requestImportances` | `/importances` | Get feature importances | `ResponsibleAIDashboardInput.importances()` |
| `requestExp` | `/get_exp` | Get image explanations | `ResponsibleAIDashboardInput.get_exp()` |
| `requestObjectDetectionMetrics` | `/get_object_detection_metrics` | Get OD metrics | `ResponsibleAIDashboardInput.get_object_detection_metrics()` |

**WebSocket for Object Detection**

For computationally expensive operations like object detection metrics, the system uses Socket.IO for real-time updates:

```mermaid
graph LR
    Component["ObjectDetectionWidgets"] -->|"Emit 'handle_object_detection_json'"| SocketIO["socket.io-client"]
    SocketIO -->|WebSocket| FlaskSocket["Flask-SocketIO"]
    FlaskSocket -->|"on('handle_object_detection_json')"| Handler["ResponsibleAIDashboard.handle_object_detection_json()"]
    Handler -->|"Emit 'object_detection_result'"| FlaskSocket
    FlaskSocket -->|WebSocket| SocketIO
    SocketIO -->|"on('object_detection_result')"| Component
```

Sources: [apps/widget/src/app/ModelAssessment.tsx:1-280](), [raiwidgets/raiwidgets/responsibleai_dashboard_input.py:1-400](), [raiwidgets/raiwidgets/responsibleai_dashboard.py:1-180]()

---

## Build and Bundle Pipeline

The monorepo uses Nx for building and bundling TypeScript libraries into distributable packages.

**Build Process**

```mermaid
graph TB
    subgraph "Source Code"
        TSX["*.tsx files<br/>React components"]
        TS["*.ts files<br/>TypeScript modules"]
        JSON["localization/*.json<br/>i18n strings"]
    end
    
    subgraph "Build Tools"
        NxBuild["nx run-many --target=build<br/>Orchestrates parallel builds"]
        TSCompiler["TypeScript Compiler<br/>tsconfig.lib.json"]
        Rollup["Rollup<br/>rollup.config.js<br/>Module bundler"]
        Webpack["Webpack<br/>For widget app"]
    end
    
    subgraph "Build Outputs"
        ESM["dist/libs/*/index.esm.js<br/>ES Module format"]
        CJS["dist/libs/*/index.cjs.js<br/>CommonJS format"]
        DTS["dist/libs/*/index.d.ts<br/>Type definitions"]
        WidgetBundle["dist/apps/widget/index.js<br/>Compiled dashboard"]
    end
    
    TSX --> TSCompiler
    TS --> TSCompiler
    TSCompiler --> Rollup
    JSON --> Rollup
    
    NxBuild --> Rollup
    NxBuild --> Webpack
    
    Rollup --> ESM
    Rollup --> CJS
    Rollup --> DTS
    Webpack --> WidgetBundle
    
    WidgetBundle -->|Embedded in| PythonPackage["raiwidgets Python package<br/>Served by Flask"]
```

**Build Configuration**

Each library has a `project.json` or entry in `workspace.json` defining:
- Entry point: `libs/*/src/index.ts`
- Output directory: `dist/libs/*`
- External dependencies (not bundled): React, FluentUI, Highcharts, Plotly
- Build target: `@nrwl/web:package`

Example from [workspace.json:99-130]():
```json
"build": {
  "builder": "@nrwl/web:package",
  "options": {
    "outputPath": "dist/libs/core-ui",
    "tsConfig": "libs/core-ui/tsconfig.lib.json",
    "entryFile": "libs/core-ui/src/index.ts",
    "external": ["@fluentui/react", "highcharts", "react", "react-dom"],
    "rollupConfig": "./rollup.config.js"
  }
}
```

The final widget bundle is embedded in the Python `raiwidgets` package and served by Flask at runtime.

Sources: [workspace.json:1-1000](), [package.json:6-42](), [nx.json:1-80]()

---

## Chart Visualization Libraries

The dashboard uses three primary charting libraries, each serving different visualization needs.

| Library | Use Cases | Wrapper Component |
|---------|-----------|-------------------|
| **Highcharts** | Heatmaps, bar charts, box plots | `BasicHighChart`, `HeatmapHighChart` |
| **D3** | Tree maps, custom SVG visualizations | `TreeViewRenderer` (error analysis) |
| **Plotly** | Scatter plots, 3D visualizations | `AccessibleChart` in `mlchartlib` |

**Chart Component Architecture**

```mermaid
graph TB
    subgraph "Chart Abstraction Layer"
        AccessibleChart["AccessibleChart<br/>Plotly wrapper<br/>libs/mlchartlib"]
        BasicHighChart["BasicHighChart<br/>Highcharts wrapper<br/>libs/core-ui"]
        TreeViewRenderer["TreeViewRenderer<br/>D3 wrapper<br/>libs/error-analysis"]
    end
    
    subgraph "Underlying Libraries"
        Plotly["plotly.js<br/>react-plotly.js"]
        Highcharts["highcharts<br/>v10.1.0"]
        D3["d3-hierarchy<br/>d3-selection<br/>d3-zoom"]
    end
    
    subgraph "Consumer Components"
        DataExplorerChart["DataExplorer<br/>Scatter plots"]
        ModelOverviewChart["ModelOverviewChartPivot<br/>Bar/box charts"]
        ErrorTreeMap["Error Analysis TreeMap"]
        ErrorHeatMap["Error Analysis HeatMap"]
    end
    
    AccessibleChart --> Plotly
    BasicHighChart --> Highcharts
    TreeViewRenderer --> D3
    
    DataExplorerChart --> AccessibleChart
    ModelOverviewChart --> BasicHighChart
    ErrorTreeMap --> TreeViewRenderer
    ErrorHeatMap --> BasicHighChart
```

All chart components support theming via FluentUI's `ITheme` interface and localization via the `localization` library.

Sources: [libs/mlchartlib/src/lib/components/AccessibleChart.tsx:1-150](), [libs/core-ui/src/lib/Highchart/BasicHighChart.tsx:1-100](), [package.json:43-77]()

---

## Data Flow: Initialization to Render

This section traces how data flows from initial props through to rendered UI.

**Initialization Flow**

```mermaid
graph TB
    subgraph "Python Backend"
        RAIInsights["RAIInsights.get_data()"]
        DashboardInput["ResponsibleAIDashboardInput.dashboard_input"]
    end
    
    subgraph "Widget App"
        WidgetProps["IModelAssessmentDashboardProps<br/>- dataset: IDataset<br/>- modelExplanationData<br/>- errorAnalysisData<br/>- causalAnalysisData"]
    end
    
    subgraph "Dashboard Initialization"
        BuildContext["buildInitialModelAssessmentContext()<br/>libs/model-assessment/.../buildModelAssessmentContext.ts"]
        
        CreateJointDataset["new JointDataset({<br/>  dataset,<br/>  localExplanations,<br/>  metadata,<br/>  predictedY,<br/>  trueY<br/>})"]
        
        CreateCohorts["Create ErrorCohorts<br/>- Default 'All data' cohort<br/>- Pre-built cohorts<br/>- Time series cohorts"]
        
        InitialState["IModelAssessmentDashboardState<br/>- jointDataset<br/>- cohorts<br/>- baseCohort<br/>- selectedCohort<br/>- activeGlobalTabs"]
    end
    
    subgraph "Render"
        ContextProvider2["ModelAssessmentContext.Provider<br/>value = {state + callbacks}"]
        ComponentTree["React Component Tree<br/>Tabs → Sub-components"]
    end
    
    RAIInsights --> DashboardInput
    DashboardInput --> WidgetProps
    WidgetProps --> BuildContext
    
    BuildContext --> CreateJointDataset
    BuildContext --> CreateCohorts
    
    CreateJointDataset --> InitialState
    CreateCohorts --> InitialState
    
    InitialState --> ContextProvider2
    ContextProvider2 --> ComponentTree
```

**Key Initialization Steps**

1. **Props Processing**: [libs/model-assessment/src/lib/ModelAssessmentDashboard/Context/buildModelAssessmentContext.ts:39-174]()
   - Builds `IExplanationModelMetadata` from dataset
   - Creates `JointDataset` merging all data sources
   - Processes pre-built cohorts or generates time series cohorts
   
2. **Tab Selection**: [libs/model-assessment/src/lib/ModelAssessmentDashboard/AvailableTabs.ts:1-100]()
   - Determines which tabs to show based on available data
   - Only includes tabs with required data (e.g., Causal Analysis tab only if `causalAnalysisData` exists)

3. **Context Population**: [libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboard.tsx:59-121]()
   - Combines state with request callbacks
   - Injects telemetry hook
   - Provides cohort management functions

Sources: [libs/model-assessment/src/lib/ModelAssessmentDashboard/Context/buildModelAssessmentContext.ts:39-288](), [libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboard.tsx:32-175]()

---

## Localization

All user-facing strings are centralized in the `localization` library for internationalization support.

**Localization Structure**

```mermaid
graph LR
    subgraph "Source"
        EN["libs/localization/src/lib/en.json<br/>English strings (default)"]
        OtherLang["Future: es.json, fr.json, etc."]
    end
    
    subgraph "Localization Module"
        LocalizedStrings["LocalizedStrings class<br/>from 'localized-strings'"]
        LocalizationObject["localization object<br/>Exported from @responsible-ai/localization"]
    end
    
    subgraph "Components"
        Component1["ModelOverview<br/>localization.ModelAssessment.ModelOverview.title"]
        Component2["ErrorAnalysis<br/>localization.ErrorAnalysis.Cohort.defaultLabel"]
    end
    
    EN --> LocalizedStrings
    OtherLang -.future.-> LocalizedStrings
    LocalizedStrings --> LocalizationObject
    
    LocalizationObject --> Component1
    LocalizationObject --> Component2
```

**Localization Keys Structure** (excerpt from [libs/localization/src/lib/en.json:1-100]()):

```json
{
  "Common": { "close": "Close", "loading": "Loading..." },
  "ErrorAnalysis": {
    "Cohort": { "defaultLabel": "All data" },
    "TreeView": { "treeDescription": "The tree visualization uses..." }
  },
  "ModelAssessment": {
    "ModelOverview": {
      "topLevelDescription": "Evaluate your model...",
      "metrics": { "accuracy": { "name": "Accuracy", "description": "..." } }
    }
  }
}
```

Components access localized strings via: `localization.ModelAssessment.ModelOverview.topLevelDescription`

The dashboard locale can be set via props: `<ModelAssessmentDashboard locale="en" />`

Sources: [libs/localization/src/lib/en.json:1-1000](), [libs/model-assessment/src/lib/ModelAssessmentDashboard/ModelAssessmentDashboard.tsx:40-53]()

---

