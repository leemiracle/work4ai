<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/vscode-jupyter · page 4 Notebook System · fetched 2026-10-26 -->

# Notebook System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/notebooks/controllers/commands/installPythonControllerCommands.ts](src/notebooks/controllers/commands/installPythonControllerCommands.ts)
- [src/notebooks/controllers/connectionDisplayData.ts](src/notebooks/controllers/connectionDisplayData.ts)
- [src/notebooks/controllers/controllerRegistration.ts](src/notebooks/controllers/controllerRegistration.ts)
- [src/notebooks/controllers/controllerRegistration.unit.test.ts](src/notebooks/controllers/controllerRegistration.unit.test.ts)
- [src/notebooks/controllers/kernelSource/kernelSourceCommandHandler.ts](src/notebooks/controllers/kernelSource/kernelSourceCommandHandler.ts)
- [src/notebooks/controllers/serviceRegistry.node.ts](src/notebooks/controllers/serviceRegistry.node.ts)
- [src/notebooks/controllers/serviceRegistry.web.ts](src/notebooks/controllers/serviceRegistry.web.ts)
- [src/notebooks/controllers/types.ts](src/notebooks/controllers/types.ts)
- [src/notebooks/controllers/vscodeNotebookController.ts](src/notebooks/controllers/vscodeNotebookController.ts)
- [src/notebooks/controllers/vscodeNotebookController.unit.test.ts](src/notebooks/controllers/vscodeNotebookController.unit.test.ts)
- [src/test/datascience/jupyter/kernels/installationPrompts.vscode.test.ts](src/test/datascience/jupyter/kernels/installationPrompts.vscode.test.ts)
- [src/test/datascience/notebook/controllerDefaultService.ts](src/test/datascience/notebook/controllerDefaultService.ts)
- [src/test/datascience/notebook/controllerPreferredService.ts](src/test/datascience/notebook/controllerPreferredService.ts)
- [src/test/datascience/notebook/kernelCrashes.vscode.test.ts](src/test/datascience/notebook/kernelCrashes.vscode.test.ts)
- [src/test/datascience/notebook/kernelRankingHelper.ts](src/test/datascience/notebook/kernelRankingHelper.ts)
- [src/test/datascience/notebook/remoteNotebookEditor.vscode.common.test.ts](src/test/datascience/notebook/remoteNotebookEditor.vscode.common.test.ts)
- [src/test/datascience/notebook/remoteNotebookEditor.vscode.test.ts](src/test/datascience/notebook/remoteNotebookEditor.vscode.test.ts)
- [src/test/datascience/variableView/variableViewHelpers.ts](src/test/datascience/variableView/variableViewHelpers.ts)

</details>



The Notebook System integrates with VS Code's native notebook API to provide Jupyter functionality within `.ipynb` files and interactive windows. It creates and manages `NotebookController` instances through the `IControllerRegistration` interface, handles cell execution via `VSCodeNotebookController`, and connects notebooks to kernels through the `IKernelProvider` system.

## Purpose and Scope

The Notebook System implements the bridge between VS Code's notebook API and Jupyter kernels. The core components include:

- **Controller Registration** - `ControllerRegistration` class manages controller lifecycle based on available `KernelConnectionMetadata`
- **Controller Implementation** - `VSCodeNotebookController` handles cell execution and kernel communication
- **Kernel Source Selection** - `KernelSourceCommandHandler` provides kernel picker integration
- **Display Data Management** - `IConnectionDisplayDataProvider` generates controller labels and descriptions

This system enables execution of Jupyter notebooks and interactive Python code using local interpreters, kernel specifications, and remote Jupyter servers.

## Architecture Overview

**Notebook Controller System Architecture**

```mermaid
graph TB
    subgraph "VS Code Notebook API"
        notebooks_createNotebookController["notebooks.createNotebookController()"]
        NotebookDocument["NotebookDocument"]
        NotebookController["NotebookController"]
        NotebookCellExecution["NotebookCellExecution"]
    end
    
    subgraph "Controller Registration"
        ControllerRegistration["ControllerRegistration"]
        IKernelFinder["IKernelFinder"]
        loadControllers["loadControllers()"]
        createNotebookControllers["createNotebookControllers()"]
    end
    
    subgraph "Controller Implementation"
        VSCodeNotebookController["VSCodeNotebookController"]
        handleExecution["handleExecution()"]
        executeQueuedCells["executeQueuedCells()"]
        connectToKernel["connectToKernel()"]
        onDidChangeSelectedNotebooks["onDidChangeSelectedNotebooks()"]
    end
    
    subgraph "Kernel Source Commands"
        KernelSourceCommandHandler["KernelSourceCommandHandler"]
        ILocalPythonNotebookKernelSourceSelector["ILocalPythonNotebookKernelSourceSelector"]
        IRemoteNotebookKernelSourceSelector["IRemoteNotebookKernelSourceSelector"]
    end
    
    subgraph "Display Data"
        IConnectionDisplayDataProvider["IConnectionDisplayDataProvider"]
        ConnectionDisplayData["ConnectionDisplayData"]
    end
    
    IKernelFinder --> ControllerRegistration
    ControllerRegistration --> loadControllers
    loadControllers --> createNotebookControllers
    createNotebookControllers --> VSCodeNotebookController
    VSCodeNotebookController --> notebooks_createNotebookController
    
    NotebookController --> handleExecution
    handleExecution --> executeQueuedCells
    executeQueuedCells --> connectToKernel
    
    KernelSourceCommandHandler --> ILocalPythonNotebookKernelSourceSelector
    KernelSourceCommandHandler --> IRemoteNotebookKernelSourceSelector
    
    IConnectionDisplayDataProvider --> ConnectionDisplayData
    ConnectionDisplayData --> VSCodeNotebookController
    
    onDidChangeSelectedNotebooks --> VSCodeNotebookController
```

**Sources:** [src/notebooks/controllers/vscodeNotebookController.ts:91-769](), [src/notebooks/controllers/controllerRegistration.ts:38-369](), [src/notebooks/controllers/kernelSource/kernelSourceCommandHandler.ts:54-325](), [src/notebooks/controllers/types.ts:22-137]()

## Controller Registration and Lifecycle

The `ControllerRegistration` class implements `IControllerRegistration` and manages the complete lifecycle of `VSCodeNotebookController` instances based on available `KernelConnectionMetadata`. It activates as an `IExtensionSyncActivationService` and monitors changes through `IKernelFinder`.

**Controller Registration Flow**

```mermaid
flowchart TD
    activate["ControllerRegistration.activate()"]
    kernelFinderChange["kernelFinder.onDidChangeKernels"]
    loadControllers["loadControllers()"]
    getKernels["kernelFinder.kernels"]
    createNotebookControllers["createNotebookControllers()"]
    batchAdd["batchAdd()"]
    addImpl["addImpl()"]
    VSCodeNotebookController_create["VSCodeNotebookController.create()"]
    notebooks_createNotebookController["notebooks.createNotebookController()"]
    registeredControllers["registeredControllers Map<string, IVSCodeNotebookController>"]
    
    activate --> kernelFinderChange
    kernelFinderChange --> loadControllers
    loadControllers --> getKernels
    getKernels --> createNotebookControllers
    createNotebookControllers --> batchAdd
    batchAdd --> addImpl
    addImpl --> VSCodeNotebookController_create
    VSCodeNotebookController_create --> notebooks_createNotebookController
    notebooks_createNotebookController --> registeredControllers
    
    subgraph "Controller Types"
        JupyterNotebookView["JupyterNotebookView"]
        InteractiveWindowView["InteractiveWindowView"]
    end
    
    addImpl --> JupyterNotebookView
    addImpl --> InteractiveWindowView
```

The registration system creates two controllers per `KernelConnectionMetadata`: one for `JupyterNotebookView` and one for `InteractiveWindowView`. Controllers use `getControllerId()` to generate unique IDs and are automatically disposed via `canControllerBeDisposed()` when kernels become unavailable.

**Sources:** [src/notebooks/controllers/controllerRegistration.ts:83-100](), [src/notebooks/controllers/controllerRegistration.ts:102-141](), [src/notebooks/controllers/controllerRegistration.ts:244-349](), [src/notebooks/controllers/controllerRegistration.ts:359-364]()

## Controller Selection and Kernel Association

When a user selects a controller, the `VSCodeNotebookController` handles the selection through its `onDidChangeSelectedNotebooks` event handler and establishes kernel connections via `KernelConnector.connectToNotebookKernel()`.

**Controller Selection Flow**

```mermaid
flowchart TD
    userSelect["User selects controller in VS Code"]
    onDidChangeSelectedNotebooks["controller.onDidChangeSelectedNotebooks"]
    checkTrusted["workspace.isTrusted check"]
    onDidSelectController["onDidSelectController()"]
    sendKernelTelemetry["sendKernelTelemetryEvent(Telemetry.SwitchKernel)"]
    updateNotebookMetadata["updateNotebookDocumentMetadata()"]
    kernelProviderGetOrCreate["kernelProvider.getOrCreate()"]
    checkAutoStart{"disableJupyterAutoStart?<br/>isLocalConnection?<br/>trustedKernelPaths.isTrusted?"}
    connectToKernel["connectToKernel()"]
    updateCellLanguages["updateCellLanguages()"]
    trackControllerSelection["trackControllerCreation()"]
    
    userSelect --> onDidChangeSelectedNotebooks
    onDidChangeSelectedNotebooks --> checkTrusted
    checkTrusted -->|"workspace.isTrusted = true"| onDidSelectController
    checkTrusted -->|"not trusted"| stop["Stop execution"]
    onDidSelectController --> sendKernelTelemetry
    onDidSelectController --> updateNotebookMetadata
    onDidSelectController --> kernelProviderGetOrCreate
    onDidSelectController --> updateCellLanguages
    onDidSelectController --> checkAutoStart
    checkAutoStart -->|"auto-start enabled"| connectToKernel
    checkAutoStart -->|"disabled"| trackControllerSelection
    connectToKernel --> trackControllerSelection
```

The `updateCellLanguages()` method ensures cell language compatibility by calling `languages.setTextDocumentLanguage()` when cells don't match the controller's `supportedLanguages` from `NotebookCellLanguageService.getSupportedLanguages()`.

**Sources:** [src/notebooks/controllers/vscodeNotebookController.ts:395-455](), [src/notebooks/controllers/vscodeNotebookController.ts:708-768](), [src/notebooks/controllers/vscodeNotebookController.ts:474-492](), [src/notebooks/controllers/vscodeNotebookController.ts:193-218]()

## Cell Execution Flow

VS Code triggers cell execution through the `handleExecution()` method registered as the controller's execution handler. The `VSCodeNotebookController` manages cell queuing, kernel connection, and execution coordination.

**Cell Execution Sequence**

```mermaid
sequenceDiagram
    participant VSCode as "VS Code Notebook API"
    participant VSCodeNotebookController as "VSCodeNotebookController"
    participant CellExecutionCreator as "CellExecutionCreator"
    participant KernelConnector as "KernelConnector"
    participant IKernelProvider as "IKernelProvider"
    participant KernelExecution as "INotebookKernelExecution"
    
    VSCode->>VSCodeNotebookController: "handleExecution(cells, notebook)"
    VSCodeNotebookController->>VSCodeNotebookController: "executeQueuedCells()"
    VSCodeNotebookController->>CellExecutionCreator: "getOrCreate(cell, controller)"
    CellExecutionCreator-->>VSCodeNotebookController: "NotebookCellExecution"
    VSCodeNotebookController->>VSCodeNotebookController: "startKernel(notebook)"
    VSCodeNotebookController->>KernelConnector: "connectToNotebookKernel()"
    KernelConnector->>IKernelProvider: "get/create kernel"
    IKernelProvider-->>KernelConnector: "IKernel instance"
    KernelConnector-->>VSCodeNotebookController: "connected kernel"
    VSCodeNotebookController->>IKernelProvider: "getKernelExecution(kernel)"
    IKernelProvider-->>VSCodeNotebookController: "kernelExecution"
    VSCodeNotebookController->>KernelExecution: "executeCell(cell)"
    KernelExecution-->>VSCode: "cell outputs and status updates"
```

The execution system uses `cellQueue` to manage multiple cell execution requests and `runningCellExecutions` to track active executions. Error handling includes `endCellAndDisplayErrorsInCell()` for kernel failures and `IDataScienceErrorHandler` for user-friendly error messages.

**Sources:** [src/notebooks/controllers/vscodeNotebookController.ts:358-394](), [src/notebooks/controllers/vscodeNotebookController.ts:543-655](), [src/notebooks/controllers/vscodeNotebookController.ts:524-540](), [src/notebooks/controllers/vscodeNotebookController.ts:657-671]()

## Display Data and Controller Metadata

The `IConnectionDisplayDataProvider` interface generates display information for controllers in VS Code's kernel picker. The `ConnectionDisplayData` class implements `IConnectionDisplayData` with dynamic updates through `onDidChange` events.

| Property | Interface | Purpose | Example |
|----------|-----------|---------|---------|
| `label` | `IConnectionDisplayData.label` | Primary display name | "Python 3.9.7" |
| `description` | `IConnectionDisplayData.description` | Additional context | "/usr/local/bin/python" |
| `category` | `IConnectionDisplayData.category` | Grouping classification | `DataScience.kernelCategoryForConda` |
| `serverDisplayName` | `IConnectionDisplayData.serverDisplayName` | Remote server context | "Jupyter Server" |

**Display Data Generation**

```mermaid
graph LR
    KernelConnectionMetadata["KernelConnectionMetadata"]
    getKernelConnectionCategory["getKernelConnectionCategory()"]
    ConnectionDisplayDataProvider["ConnectionDisplayDataProvider"]
    ConnectionDisplayData["ConnectionDisplayData"]
    updateDisplayData["updateDisplayData()"]
    VSCodeNotebookController["VSCodeNotebookController"]
    
    KernelConnectionMetadata --> getKernelConnectionCategory
    getKernelConnectionCategory --> ConnectionDisplayDataProvider
    ConnectionDisplayDataProvider --> ConnectionDisplayData
    ConnectionDisplayData --> updateDisplayData
    updateDisplayData --> VSCodeNotebookController
    
    subgraph "Category Types"
        kernelCategoryForConda["DataScience.kernelCategoryForConda"]
        kernelCategoryForJupyterKernel["DataScience.kernelCategoryForJupyterKernel"]
        kernelCategoryForRemoteJupyterKernel["DataScience.kernelCategoryForRemoteJupyterKernel"]
    end
    
    getKernelConnectionCategory --> kernelCategoryForConda
    getKernelConnectionCategory --> kernelCategoryForJupyterKernel
    getKernelConnectionCategory --> kernelCategoryForRemoteJupyterKernel
```

The `getKernelConnectionCategory()` function maps connection types to localized category strings, while `updateDisplayData()` refreshes controller labels and descriptions when kernel information changes.

**Sources:** [src/notebooks/controllers/connectionDisplayData.ts:13-81](), [src/notebooks/controllers/types.ts:125-137](), [src/notebooks/controllers/vscodeNotebookController.ts:344-357](), [src/notebooks/controllers/vscodeNotebookController.ts:195-204]()

## Integration with VS Code Notebook API

The notebook system leverages several key VS Code notebook APIs to provide seamless integration:

- `notebooks.createNotebookController()` - Creates controller instances that appear in kernel picker
- `NotebookController.executionHandler` - Handles cell execution requests from VS Code  
- `NotebookController.interruptHandler` - Handles kernel interruption requests
- `NotebookCellExecution` - Manages individual cell execution state and outputs
- `NotebookController.onDidChangeSelectedNotebooks` - Monitors controller selection changes

The controllers support execution ordering, multiple programming languages, and custom renderer scripts for development scenarios.

**Sources:** [src/notebooks/controllers/vscodeNotebookController.ts:196-219](), [src/notebooks/controllers/vscodeNotebookController.ts:493-514](), [src/notebooks/controllers/vscodeNotebookController.ts:516-522]()

---

