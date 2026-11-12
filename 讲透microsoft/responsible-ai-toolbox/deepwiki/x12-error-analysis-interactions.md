<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/responsible-ai-toolbox · extra page Error Analysis Interactions · fetched 2026-10-26 -->

# Error Analysis Interactions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/dashboard/src/error-analysis/App.tsx](apps/dashboard/src/error-analysis/App.tsx)
- [libs/core-ui/src/lib/components/SVGToolTip.tsx](libs/core-ui/src/lib/components/SVGToolTip.tsx)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ColorPalette.ts](libs/error-analysis/src/lib/ErrorAnalysisDashboard/ColorPalette.ts)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisView.tsx](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisView.tsx)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/FilterTooltip/FilterTooltip.styles.ts](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/FilterTooltip/FilterTooltip.styles.ts)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/FilterTooltip/FilterTooltip.tsx](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/FilterTooltip/FilterTooltip.tsx)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeLegend/TreeLegend.styles.ts](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeLegend/TreeLegend.styles.ts)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeLegend/TreeLegend.tsx](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeLegend/TreeLegend.tsx)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewNode.tsx](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewNode.tsx)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.styles.ts](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.styles.ts)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewUtils.ts](libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewUtils.ts)
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx](libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx)

</details>



## Purpose and Scope

This page documents the user interaction mechanisms in the Error Analysis Dashboard, focusing on how user actions (clicks, hovers, keyboard inputs) trigger state changes, cohort updates, and view transitions. For details on the tree visualization rendering itself, see [Tree View Renderer](#4.3.1). For matrix heatmap visualization, see [Matrix Filter UI](#4.3.2). For the overall Error Analysis Dashboard architecture, see [Error Analysis Dashboard](#4.3).

This page covers:
- Node selection and temporary cohort creation
- View switching between TreeMap and HeatMap modes
- Panel and modal interactions (feature selection, cohort management)
- Hover interactions and tooltips
- Event propagation and state management patterns

## Interaction Patterns Overview

The Error Analysis Dashboard supports several categories of user interactions that work together to enable exploratory error analysis:

```mermaid
graph TB
    User[User Actions]
    
    subgraph "Selection Interactions"
        NodeClick[Node Click/Focus<br/>TreeViewNode]
        CellClick[Matrix Cell Click<br/>MatrixFilter]
        ClearSelection[Clear Selection Button<br/>TreeLegend]
    end
    
    subgraph "View Switching"
        TabSwitch[TreeMap/HeatMap Tabs<br/>ErrorAnalysisViewTab]
        GlobalTabSwitch[Data Explorer/Explanation Tabs<br/>ErrorAnalysisDashboard]
    end
    
    subgraph "Panel Interactions"
        FeatureList[Feature List Panel<br/>FeatureList]
        CohortList[Cohort List Panel<br/>CohortListPanel]
        SaveCohort[Save Cohort Modal<br/>SaveCohort]
        EditCohort[Edit Cohort Modal<br/>EditCohort]
    end
    
    subgraph "Hover Interactions"
        NodeHover[Node Hover<br/>SVGToolTip]
        PathHover[Path Hover<br/>TreeViewPath]
    end
    
    subgraph "State Updates"
        CohortUpdate[updateSelectedCohort]
        ViewUpdate[updateViewState]
        StateChange[setState]
    end
    
    User --> NodeClick
    User --> CellClick
    User --> TabSwitch
    User --> FeatureList
    User --> NodeHover
    
    NodeClick --> CohortUpdate
    CellClick --> CohortUpdate
    ClearSelection --> CohortUpdate
    TabSwitch --> ViewUpdate
    
    CohortUpdate --> StateChange
    ViewUpdate --> StateChange
    
    NodeHover --> PathHover
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:77-829]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewNode.tsx:1-131]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx:1-184]()

## Node Selection and Cohort Creation

### Selection Mechanism

When a user clicks or focuses on a node in the tree view, a temporary cohort is created based on the path from the root to that node. This interaction flow is central to error analysis exploration:

```mermaid
sequenceDiagram
    participant User
    participant TreeViewNode
    participant TreeViewRenderer
    participant ErrorAnalysisDashboard
    participant ErrorCohort
    
    User->>TreeViewNode: click/focus on node
    TreeViewNode->>TreeViewNode: onSelect()
    TreeViewNode->>TreeViewRenderer: onSelectNode(node)
    
    TreeViewRenderer->>TreeViewRenderer: selectNode(node, createTemporaryCohort=true)
    TreeViewRenderer->>TreeViewRenderer: getFilters(node)
    Note over TreeViewRenderer: Walks up tree to root<br/>collecting filters
    
    TreeViewRenderer->>TreeViewRenderer: calculateCohortStats(node.data)
    TreeViewRenderer->>ErrorAnalysisDashboard: updateSelectedCohort(filters, [], CohortSource.TreeMap, 0, cohortStats)
    
    ErrorAnalysisDashboard->>ErrorAnalysisDashboard: updateSelectedCohort()
    ErrorAnalysisDashboard->>ErrorCohort: new ErrorCohort(...)
    Note over ErrorAnalysisDashboard: Creates temporary cohort<br/>with name "Temporary cohort"
    
    ErrorAnalysisDashboard->>ErrorAnalysisDashboard: setState({cohorts, selectedCohort})
    ErrorAnalysisDashboard-->>TreeViewRenderer: re-render
    TreeViewRenderer->>TreeViewRenderer: selectParentNodes(node)
    Note over TreeViewRenderer: Highlights path from root to selected node
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewNode.tsx:127-129]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:642-693]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:697-744]()

### Filter Generation

The `getFilters` method walks up the tree hierarchy from the selected node to the root, collecting filter conditions at each level:

| Step | Method | Purpose |
|------|--------|---------|
| 1 | `getFilters(node)` at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:622-640]() | Recursively collect filters from node to root |
| 2 | Extract `node.data.arg`, `node.parent.data.nodeName`, `node.data.method` | Build individual filter object |
| 3 | `ErrorCohort.getDataFilters()` | Relabel filters based on feature indices |
| 4 | Combine with base cohort filters | Merge with existing cohort constraints |

The filter structure follows the `IFilter` interface:

```typescript
interface IFilter {
  column: string;      // Feature name from parent node
  method: FilterMethods; // e.g., "less", "greater", "includes"
  arg: number[];       // Threshold value(s)
}
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:622-640]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:705-708]()

### Temporary vs. Permanent Cohorts

The dashboard maintains two types of cohorts:

| Cohort Type | Characteristics | Creation Method |
|-------------|----------------|-----------------|
| **Temporary** | `isTemporary = true`, named "Temporary cohort", automatically replaced on next selection | Created by node/cell selection via `CohortSource.TreeMap` or `CohortSource.HeatMap` |
| **Permanent** | `isTemporary = false`, user-defined name, persists until manually deleted | Created via Save Cohort modal from temporary cohort |

The state management for cohorts at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:734-743]():

```typescript
// Filter out temporary cohorts and add new selection
let cohorts = this.state.cohorts.filter(
  (errorCohort) => !errorCohort.isTemporary
);
if (addTemporaryCohort) {
  cohorts = [...cohorts, selectedCohort];
}
this.setState({
  cohorts,
  selectedCohort
});
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:710-744]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:666-669]()

## View Switching

### TreeMap and HeatMap Toggle

Users can switch between TreeMap and HeatMap visualizations using tabs. The interaction is handled by `ErrorAnalysisViewTab`:

```mermaid
graph LR
    subgraph "ErrorAnalysisViewTab Component"
        Pivot[Pivot Component]
        TreeMapTab["PivotItem<br/>ErrorAnalysisOptions.TreeMap"]
        HeatMapTab["PivotItem<br/>ErrorAnalysisOptions.HeatMap"]
        
        Pivot --> TreeMapTab
        Pivot --> HeatMapTab
    end
    
    subgraph "Event Handlers"
        HandleTabClick[handleTabClick]
        HandleErrorDetectorChanged[props.handleErrorDetectorChanged]
        TelemetryHook[telemetryHook]
    end
    
    subgraph "State Changes"
        CloseFeatureList["setState({openFeatureList: false})"]
        UpdateOption["setState({errorAnalysisOption: key})"]
    end
    
    TreeMapTab --> HandleTabClick
    HeatMapTab --> HandleTabClick
    HandleTabClick --> CloseFeatureList
    HandleTabClick --> HandleErrorDetectorChanged
    HandleTabClick --> TelemetryHook
    HandleErrorDetectorChanged --> UpdateOption
```

At [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx:162-174](), the tab click handler:

```typescript
private readonly handleTabClick = (item?: PivotItem): void => {
  if (item?.props.itemKey === ErrorAnalysisOptions.HeatMap) {
    this.setState({ openFeatureList: false });
  }
  this.props.handleErrorDetectorChanged(item);
  this.props.telemetryHook?.({
    level: TelemetryLevels.ButtonClick,
    type: item?.props.itemKey === ErrorAnalysisOptions.HeatMap
      ? TelemetryEventName.ErrorAnalysisHeatMapTabClick
      : TelemetryEventName.ErrorAnalysisTreeMapTabClick
  });
};
```

**Note:** The Feature List panel is automatically closed when switching to HeatMap mode, as feature selection is only relevant for TreeMap visualization.

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx:79-106]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx:162-174]()

### Global Tab Navigation

The Error Analysis Dashboard also supports switching between global views (Data Explorer, Global Explanation, Local Explanation):

```mermaid
stateDiagram-v2
    [*] --> ErrorAnalysisView
    ErrorAnalysisView --> ExplanationView: viewExplanation()
    ExplanationView --> DataExplorerTab: handleGlobalTabClick(DataExplorerTab)
    ExplanationView --> GlobalExplanationTab: handleGlobalTabClick(GlobalExplanationTab)
    ExplanationView --> LocalExplanationTab: handleGlobalTabClick(LocalExplanationTab)
    
    DataExplorerTab --> GlobalExplanationTab
    GlobalExplanationTab --> LocalExplanationTab
    LocalExplanationTab --> DataExplorerTab
    
    ExplanationView --> ErrorAnalysisView: updateViewState(ErrorAnalysisView)
```

The view state management at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:777-784]():

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:757-768]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:777-784]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:526-625]()

### State Preservation During View Switches

When switching between TreeMap and HeatMap, the component uses static state preservation to maintain user selections:

| Component | State Preservation Mechanism |
|-----------|----------------------------|
| `TreeViewRenderer` | Static `savedState` at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:79]() |
| `MatrixFilter` | Static state via `resetState()` method |
| `MatrixArea` | Static state via `resetState()` method |

The `TreeViewRenderer` saves state on unmount unless explicitly reset at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:136-143]():

```typescript
public componentWillUnmount(): void {
  window.removeEventListener("resize", this.onResize);
  if (TreeViewRenderer.saveStateOnUnmount) {
    TreeViewRenderer.savedState = this.state;
  } else {
    TreeViewRenderer.savedState = undefined;
  }
}
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:79-97]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:136-143]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:454-465]()

## Panel and Modal Interactions

### Feature List Panel

The Feature List panel allows users to select which features to use for tree construction. This interaction is specific to TreeMap mode:

```mermaid
graph TB
    MainMenu[MainMenu Component]
    FeatureListButton[CommandBarButton<br/>"Feature list"]
    FeatureListPanel[FeatureList Component]
    
    MainMenu --> FeatureListButton
    FeatureListButton -->|onClick| OpenFeatureList["setState({openFeatureList: true})"]
    OpenFeatureList --> FeatureListPanel
    
    subgraph "FeatureList Panel"
        FeatureCheckboxes[Feature Checkboxes<br/>with Importance Scores]
        SaveButton[Save Button]
        CancelButton[Dismiss Button]
    end
    
    FeatureListPanel --> FeatureCheckboxes
    FeatureCheckboxes --> SaveButton
    SaveButton -->|saveFeatures| UpdateSelectedFeatures["setState({selectedFeatures: features})"]
    CancelButton -->|onDismiss| ClosePanel["setState({openFeatureList: false})"]
    
    UpdateSelectedFeatures --> FetchTreeNodes[fetchTreeNodes]
    FetchTreeNodes -->|requestDebugML| BackendAPI[Backend API]
```

The button visibility logic at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx:95-104]():

```typescript
{this.props.errorAnalysisOption === ErrorAnalysisOptions.TreeMap && (
  <CommandBarButton
    className={classNames.featureList}
    iconProps={featureListIcon}
    key={"featureList"}
    onClick={this.handleFeatureListClick}
    text={localization.ErrorAnalysis.MainMenu.featureList}
  />
)}
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx:95-104]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/ErrorAnalysisView/ErrorAnalysisViewTab.tsx:129-148]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:636-648]()

### Cohort Management Panels

The dashboard provides several modals for cohort management:

| Modal | Purpose | Trigger | State Key |
|-------|---------|---------|-----------|
| **SaveCohort** | Convert temporary cohort to permanent | Save Cohort button | `openSaveCohort` |
| **EditCohort** | Modify existing cohort filters | Edit button in CohortListPanel | `openEditCohort` |
| **ShiftCohort** | Change base cohort for analysis | Shift Cohort button | `openShiftCohort` |
| **MapShift** | Switch error detector with temporary cohort | Error detector change with temporary cohort | `openMapShift` |
| **CohortListPanel** | View and manage all cohorts | Cohort List button | `openCohortListPanel` |
| **CohortInfoPanel** | View current cohort statistics | Info button | `openInfoPanel` |

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:434-517]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:626-661]()

### Save Cohort Flow

The save cohort interaction creates a permanent cohort from a temporary selection:

```mermaid
sequenceDiagram
    participant User
    participant MainMenu
    participant SaveCohort
    participant Dashboard
    
    User->>MainMenu: Click "Save Cohort"
    MainMenu->>Dashboard: setState({openSaveCohort: true})
    Dashboard->>SaveCohort: Render modal
    
    User->>SaveCohort: Enter cohort name
    User->>SaveCohort: Click Save
    SaveCohort->>Dashboard: handleSaveCohort(savedCohort, switchNew)
    
    Dashboard->>Dashboard: Filter out temporary cohorts
    Note over Dashboard: newCohorts = [...cohorts, savedCohort]<br/>filter(!cohort.isTemporary)
    
    Dashboard->>Dashboard: setState({<br/>  cohorts: newCohorts,<br/>  selectedCohort: switchNew ? savedCohort : prevSelected,<br/>  baseCohort: switchNew ? savedCohort : prevBase,<br/>  showMessageBar: true<br/>})
    
    Dashboard-->>User: Show success message
```

The `handleSaveCohort` method at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:816-828]():

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:434-442]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:816-828]()

### MapShift Modal

The MapShift modal appears when a user attempts to change the error analysis view (TreeMap ↔ HeatMap) while a temporary cohort is selected. This prevents accidental loss of exploration context:

```mermaid
stateDiagram-v2
    [*] --> ViewTreeMap
    ViewTreeMap --> TemporaryCohortSelected: User selects node
    TemporaryCohortSelected --> MapShiftModal: User switches to HeatMap
    
    MapShiftModal --> DiscardAndSwitch: User clicks "Shift"
    MapShiftModal --> SaveCohortModal: User clicks "Save"
    MapShiftModal --> TemporaryCohortSelected: User clicks "Cancel"
    
    DiscardAndSwitch --> ViewHeatMap
    SaveCohortModal --> PermanentCohortCreated
    PermanentCohortCreated --> ViewHeatMap
    
    ViewHeatMap --> [*]
```

The MapShift modal logic at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:414-427]():

```typescript
setErrorDetector={(key: ErrorAnalysisOptions): void => {
  if (this.state.selectedCohort.isTemporary) {
    this.setState({
      mapShiftErrorAnalysisOption: key,
      openFeatureList: false,
      openMapShift: true
    });
  } else {
    this.setState({
      errorAnalysisOption: key,
      openFeatureList: false
    });
  }
}}
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:414-427]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:443-466]()

## Hover and Focus Interactions

### Node Tooltips

When users hover over or focus on a tree node, an SVG tooltip displays detailed error statistics:

```mermaid
graph TB
    subgraph "TreeViewNode Component"
        GElement["g element<br/>with ref"]
        CircleNode[circle<br/>Visual node]
        TextLabel[text<br/>Error count]
    end
    
    subgraph "SVGToolTip Component"
        TargetRef[target: RefObject&lt;SVGElement&gt;]
        EventListeners[mouseenter/mouseleave<br/>focus/focusout]
        PortalTooltip[ReactDom.createPortal]
    end
    
    subgraph "FilterTooltip Content"
        NumCorrect[Correct predictions]
        NumIncorrect[Incorrect predictions]
        ErrorCoverage[Error coverage %]
        MetricValue[Metric value]
    end
    
    GElement --> TargetRef
    TargetRef --> EventListeners
    EventListeners -->|isMouseOver=true| PortalTooltip
    PortalTooltip --> FilterTooltip
    FilterTooltip --> NumCorrect
    FilterTooltip --> NumIncorrect
    FilterTooltip --> ErrorCoverage
    FilterTooltip --> MetricValue
```

The SVGToolTip component at [libs/core-ui/src/lib/components/SVGToolTip.tsx:34-42]() attaches event listeners:

```typescript
public componentDidMount(): void {
  const element = this.props.target.current;
  if (element) {
    element.addEventListener("mouseenter", this.onMouseEnter);
    element.addEventListener("focus", this.onMouseEnter);
    element.addEventListener("mouseleave", this.onMouseLeave);
    element.addEventListener("focusout", this.onMouseLeave);
  }
}
```

The tooltip content structure at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/FilterTooltip/FilterTooltip.tsx:28-107]() includes:
- Correct/incorrect counts (for error rate) or count/error sum (for other metrics)
- Error coverage percentage
- Metric-specific value (error rate, MSE, MAE, etc.)

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewNode.tsx:115-122]()
- [libs/core-ui/src/lib/components/SVGToolTip.tsx:21-110]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/FilterTooltip/FilterTooltip.tsx:1-108]()

### Path Highlighting on Hover

When a user hovers over a link (edge) in the tree, the path label becomes visible to show the filter condition:

```mermaid
sequenceDiagram
    participant User
    participant TreeViewPath
    participant TreeViewRenderer
    participant LinkLabel
    
    User->>TreeViewPath: Mouse enters link
    TreeViewPath->>TreeViewRenderer: onMouseOver(linkId)
    TreeViewRenderer->>TreeViewRenderer: setState({hoverPathId: linkId})
    TreeViewRenderer->>LinkLabel: Re-render with display: visible
    
    User->>TreeViewPath: Mouse leaves link
    TreeViewPath->>TreeViewRenderer: onMouseOut()
    TreeViewRenderer->>TreeViewRenderer: setState({hoverPathId: undefined})
    TreeViewRenderer->>LinkLabel: Re-render with display: none
```

The link label visibility logic at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:233-237]():

```typescript
style: {
  display:
    d.data.nodeState.onSelectedPath || this.state.hoverPathId === d.id
      ? undefined
      : "none",
  transform: `translate(${labelX}px, ${labelY}px)`
}
```

Link labels are visible when either:
1. The path is part of the selected node's path (`onSelectedPath = true`)
2. The user is currently hovering over the link (`hoverPathId === d.id`)

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:391-397]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:218-248]()

### Keyboard Navigation

Tree nodes support keyboard navigation for accessibility:

| Interaction | Event | Handler |
|-------------|-------|---------|
| **Tab to node** | Focus event | Sets focus outline via `:focus-visible` CSS |
| **Enter/Space on node** | Focus + onFocus | Triggers `onSelect()` same as click |
| **Tab through tree** | Sequential focus | Browser default tab order |

The node's keyboard accessibility setup at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewNode.tsx:46-53]():

```typescript
<g
  onFocus={this.onSelect}
  style={node.data.nodeState.style}
  onClick={this.onSelect}
  pointerEvents="all"
  ref={this.ref}
  tabIndex={0}
  aria-label={ariaLabel}
  className={classNames.treeNodeOutline}
>
```

The `aria-label` is generated by `treeNodeAriaLabel` at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewUtils.ts:13-44](), which includes:
- Filter condition text
- Error counts or metric statistics
- Error coverage percentage
- Metric value

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewNode.tsx:46-54]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewUtils.ts:13-44]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.styles.ts:82-88]()

## Event Flow and State Updates

### Complete Interaction Flow

The following diagram shows how a node selection propagates through the component hierarchy and triggers state updates:

```mermaid
graph TB
    subgraph "User Action"
        UserClick["User clicks tree node"]
    end
    
    subgraph "TreeViewNode Component"
        OnSelect["onSelect()<br/>[TreeViewNode.tsx:127-129]"]
    end
    
    subgraph "TreeViewRenderer Component"
        OnSelectNode["onSelectNode(node)<br/>[TreeViewRenderer.tsx:642-647]"]
        SelectNode["selectNode(node, true)<br/>[TreeViewRenderer.tsx:649-693]"]
        GetFilters["getFilters(node)<br/>[TreeViewRenderer.tsx:622-640]"]
        UnselectParent["unselectParentNodes(selectedNode)<br/>[TreeViewRenderer.tsx:613-620]"]
        SelectParent["selectParentNodes(node)<br/>[TreeViewRenderer.tsx:605-611]"]
        CalcStats["calculateCohortStats(node.data)<br/>[TreeViewRenderer.tsx:419-441]"]
    end
    
    subgraph "ErrorAnalysisDashboard Component"
        UpdateSelectedCohort["updateSelectedCohort()<br/>[ErrorAnalysisDashboard.tsx:697-744]"]
        GetDataFilters["ErrorCohort.getDataFilters()<br/>[ErrorAnalysisDashboard.tsx:705-708]"]
        CreateErrorCohort["new ErrorCohort()<br/>[ErrorAnalysisDashboard.tsx:721-733]"]
        FilterCohorts["Filter out temporary cohorts"]
        SetState["setState({cohorts, selectedCohort})"]
    end
    
    subgraph "UI Update"
        Rerender["Component re-renders"]
        HighlightPath["Selected path highlighted"]
        UpdateLegend["Legend shows new stats"]
    end
    
    UserClick --> OnSelect
    OnSelect --> OnSelectNode
    OnSelectNode --> SelectNode
    SelectNode --> UnselectParent
    UnselectParent --> SelectParent
    SelectNode --> GetFilters
    SelectNode --> CalcStats
    
    GetFilters --> UpdateSelectedCohort
    CalcStats --> UpdateSelectedCohort
    UpdateSelectedCohort --> GetDataFilters
    GetDataFilters --> CreateErrorCohort
    CreateErrorCohort --> FilterCohorts
    FilterCohorts --> SetState
    
    SetState --> Rerender
    Rerender --> HighlightPath
    Rerender --> UpdateLegend
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewNode.tsx:127-129]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:642-693]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:697-744]()

### State Synchronization Pattern

The Error Analysis Dashboard uses a centralized state management pattern where the main component holds all interaction state:

| State Category | Properties | Location |
|----------------|-----------|----------|
| **View State** | `viewType`, `errorAnalysisOption`, `activeGlobalTab`, `predictionTab` | [ErrorAnalysisDashboard.tsx:311-344]() |
| **Cohort State** | `cohorts`, `selectedCohort`, `baseCohort`, `editedCohort` | [ErrorAnalysisDashboard.tsx:311-344]() |
| **Panel State** | `openSaveCohort`, `openEditCohort`, `openFeatureList`, `openInfoPanel`, etc. | [ErrorAnalysisDashboard.tsx:311-344]() |
| **Selection State** | `selectedFeatures`, `selectedWeightVector`, `selectedWhatIfIndex` | [ErrorAnalysisDashboard.tsx:311-344]() |

State updates follow these patterns:

1. **Direct setState calls** for simple state changes (panel open/close)
2. **Callback props** passed down to child components that call parent methods
3. **Context providers** for deeply nested components to access state

The context structure at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:356-383]():

```typescript
<ModelAssessmentContext.Provider
  value={{
    baseErrorCohort: this.state.baseCohort,
    errorAnalysisData: this.props.errorAnalysisData,
    errorCohorts: this.state.cohorts,
    jointDataset: this.state.jointDataset,
    selectedErrorCohort: this.state.selectedCohort,
    shiftErrorCohort: this.shiftErrorCohort,
    // ... other context values
  }}
>
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:239-348]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:356-383]()

### Clear Selection Interaction

Users can clear the current node selection to return to the base cohort view:

```mermaid
sequenceDiagram
    participant User
    participant TreeLegend
    participant Dashboard
    participant TreeViewRenderer
    
    User->>TreeLegend: Click "Clear selection" button
    Note over TreeLegend: Button enabled only when<br/>selectedCohort.isTemporary === true
    
    TreeLegend->>Dashboard: props.onClearCohortSelectionClick()
    Dashboard->>Dashboard: clearCohortSelection()
    
    Note over Dashboard: Filter out temporary cohorts<br/>cohorts.filter(!errorCohort.isTemporary)
    
    Dashboard->>Dashboard: setState({<br/>  cohorts: filteredCohorts,<br/>  selectedCohort: baseCohort<br/>})
    
    Dashboard->>TreeViewRenderer: Re-render
    TreeViewRenderer->>TreeViewRenderer: componentDidUpdate detects<br/>selectedCohort.isTemporary changed
    TreeViewRenderer->>TreeViewRenderer: selectNode(root, false)
    Note over TreeViewRenderer: Re-select root without<br/>creating temporary cohort
```

The clear selection handler at [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:746-755]():

```typescript
private clearCohortSelection = (): void => {
  const cohorts = this.state.cohorts.filter(
    (errorCohort) => !errorCohort.isTemporary
  );
  this.setState({
    cohorts,
    selectedCohort: this.state.baseCohort
  });
  this.context.selectedErrorCohort = this.state.baseCohort;
};
```

**Sources:**
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeLegend/TreeLegend.tsx:57-65]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/ErrorAnalysisDashboard.tsx:746-755]()
- [libs/error-analysis/src/lib/ErrorAnalysisDashboard/Controls/TreeViewRenderer/TreeViewRenderer.tsx:126-133]()

---

