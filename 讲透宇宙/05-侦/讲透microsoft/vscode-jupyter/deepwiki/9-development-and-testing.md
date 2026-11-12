<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/vscode-jupyter · page 9 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.eslintrc.js](.eslintrc.js)
- [src/test/datascience/notebook/executionService.vscode.test.ts](src/test/datascience/notebook/executionService.vscode.test.ts)
- [src/test/datascience/notebook/helper.ts](src/test/datascience/notebook/helper.ts)
- [src/test/datascience/notebook/interruptRestart.vscode.test.ts](src/test/datascience/notebook/interruptRestart.vscode.test.ts)
- [src/test/datascience/notebook/nonPythonKernels.vscode.test.ts](src/test/datascience/notebook/nonPythonKernels.vscode.test.ts)

</details>



This document covers the development infrastructure, testing framework, and quality assurance processes for the VS Code Jupyter extension. It includes code quality enforcement through ESLint, comprehensive testing infrastructure, and test execution patterns.

The testing system provides extensive utilities for notebook testing, kernel management, and execution validation across multiple environments and kernel types.

## Code Quality and Linting

The extension enforces strict code quality standards through ESLint with comprehensive architectural constraints. The linting configuration prevents circular dependencies and enforces module boundaries to maintain clean architecture.

### ESLint Architectural Constraints

The linting system enforces strict import restrictions to maintain architectural boundaries:

```mermaid
graph TB
    subgraph "platform_module"[Platform Module]
        PLATFORM["src/platform"]
    end
    
    subgraph "telemetry_module"[Telemetry Module]
        TELEMETRY["src/telemetry"]
    end
    
    subgraph "kernels_module"[Kernels Module]
        KERNELS["src/kernels"]
    end
    
    subgraph "notebooks_module"[Notebooks Module]
        NOTEBOOKS["src/notebooks"]
    end
    
    subgraph "interactive_module"[Interactive Window Module]
        INTERACTIVE["src/interactive-window"]
    end
    
    subgraph "webviews_module"[Webviews Module]
        WEBVIEWS["src/webviews"]
    end
    
    subgraph "standalone_module"[Standalone Module]
        STANDALONE["src/standalone"]
    end
    
    KERNELS --> PLATFORM
    KERNELS --> TELEMETRY
    NOTEBOOKS --> PLATFORM
    NOTEBOOKS --> TELEMETRY
    NOTEBOOKS --> KERNELS
    INTERACTIVE --> PLATFORM
    INTERACTIVE --> TELEMETRY
    INTERACTIVE --> KERNELS
    INTERACTIVE --> NOTEBOOKS
    WEBVIEWS -.-> PLATFORM
    WEBVIEWS -.-> TELEMETRY
    STANDALONE -.-> WEBVIEWS
```

**Sources:** [.eslintrc.js:140-209]()

### Import Restriction Rules

The ESLint configuration includes specific rules for maintaining module boundaries:

| Restriction | Target | Allowed Dependencies | Purpose |
|-------------|--------|---------------------|---------|
| Kernels Module | `src/kernels/**` | `platform`, `telemetry` | Core kernel functionality isolation |
| Notebooks Module | `src/notebooks/**` | `platform`, `telemetry`, `kernels` | Notebook controller separation |
| Interactive Window | `src/interactive-window/**` | `platform`, `telemetry`, `kernels`, `notebooks` | Interactive execution isolation |
| Platform Module | `src/platform/**` | None (self-contained) | Foundation layer isolation |
| Webviews Module | Core components | Prohibited | UI layer separation |
| Standalone Module | Other components | Prohibited | Independent tool isolation |

**Sources:** [.eslintrc.js:170-208]()

### TypeScript and Code Standards

The linting configuration enforces TypeScript best practices and code quality:

```mermaid
graph LR
    subgraph "typescript_rules"[TypeScript Rules]
        NO_EXPLICIT_ANY["@typescript-eslint/no-explicit-any"]
        NO_FLOATING_PROMISES["@typescript-eslint/no-floating-promises"]
        NO_UNUSED_VARS["@typescript-eslint/no-unused-vars"]
        NO_USE_BEFORE_DEFINE["@typescript-eslint/no-use-before-define"]
    end
    
    subgraph "custom_rules"[Custom Rules]
        NODE_IMPORTS["local-rules/node-imports"]
        DONT_USE_PROCESS["local-rules/dont-use-process"]
        DONT_USE_FSPATH["local-rules/dont-use-fspath"]
        DONT_USE_FILENAME["local-rules/dont-use-filename"]
    end
    
    subgraph "test_overrides"[Test Overrides]
        TEST_EXPLICIT_ANY["Allow explicit any in tests"]
        TEST_RESTRICTED_IMPORTS["Disable import restrictions"]
    end
    
    NO_EXPLICIT_ANY --> NODE_IMPORTS
    NO_FLOATING_PROMISES --> DONT_USE_PROCESS
    NODE_IMPORTS --> TEST_EXPLICIT_ANY
    DONT_USE_PROCESS --> TEST_RESTRICTED_IMPORTS
```

**Sources:** [.eslintrc.js:31-67](), [.eslintrc.js:211-256]()

## Testing Infrastructure

The extension employs a comprehensive testing infrastructure built around notebook testing, kernel management, and execution validation. The system provides extensive helper utilities for creating test environments and validating notebook behavior.

### Notebook Test Helper Architecture

The core testing infrastructure centers around notebook test helpers that manage the complete test lifecycle:

```mermaid
graph TB
    subgraph "test_services"[Test Services]
        GET_SERVICES["getServices()"]
        CONTROLLER_REGISTRATION["IControllerRegistration"]
        KERNEL_FINDER["IKernelFinder"]
        KERNEL_PROVIDER["IKernelProvider"]
        INTERPRETER_SERVICE["IInterpreterService"]
    end
    
    subgraph "notebook_creation"[Notebook Creation]
        CREATE_EMPTY_PYTHON["createEmptyPythonNotebook()"]
        CREATE_TEMPORARY_NOTEBOOK["createTemporaryNotebook()"]
        CREATE_FROM_FILE["createTemporaryNotebookFromFile()"]
        GENERATE_TEMP_PATH["generateTemporaryFilePath()"]
    end
    
    subgraph "cell_management"[Cell Management]
        INSERT_CODE_CELL["insertCodeCell()"]
        INSERT_MARKDOWN_CELL["insertMarkdownCell()"]
        DELETE_CELL["deleteCell()"]
        DELETE_ALL_CELLS["deleteAllCellsAndWait()"]
    end
    
    subgraph "execution_helpers"[Execution Helpers]
        WAIT_FOR_EXECUTION["waitForExecutionCompletedSuccessfully()"]
        WAIT_FOR_ERRORS["waitForExecutionCompletedWithErrors()"]
        WAIT_FOR_TEXT_OUTPUT["waitForTextOutput()"]
        WAIT_FOR_QUEUED["waitForQueuedForExecution()"]
    end
    
    GET_SERVICES --> CONTROLLER_REGISTRATION
    GET_SERVICES --> KERNEL_FINDER
    CREATE_EMPTY_PYTHON --> INSERT_CODE_CELL
    CREATE_TEMPORARY_NOTEBOOK --> GENERATE_TEMP_PATH
    INSERT_CODE_CELL --> WAIT_FOR_EXECUTION
    WAIT_FOR_EXECUTION --> WAIT_FOR_TEXT_OUTPUT
```

**Sources:** [src/test/datascience/notebook/helper.ts:113-129](), [src/test/datascience/notebook/helper.ts:285-313](), [src/test/datascience/notebook/helper.ts:153-168]()

### Kernel Selection and Management

The test infrastructure provides sophisticated kernel selection and management capabilities:

```mermaid
graph TB
    subgraph "kernel_selection"[Kernel Selection]
        WAIT_FOR_KERNEL_CHANGE["waitForKernelToChange()"]
        SELECT_DEFAULT_CONTROLLER["selectDefaultController()"]
        GET_DEFAULT_KERNEL_CONNECTION["getDefaultKernelConnection()"]
        WAIT_FOR_AUTO_SELECT["waitForKernelToGetAutoSelected()"]
    end
    
    subgraph "connection_types"[Connection Types]
        ACTIVE_INTERPRETER["getActiveInterpreterKernelConnection()"]
        REMOTE_PYTHON["getDefaultPythonRemoteKernelConnectionForActiveInterpreter()"]
        LOCAL_KERNEL_SPEC["startUsingLocalKernelSpec"]
        PYTHON_INTERPRETER["startUsingPythonInterpreter"]
    end
    
    subgraph "controller_management"[Controller Management]
        CONTROLLER_PREFERRED["ControllerPreferredService"]
        COMPUTE_PREFERRED["computePreferred()"]
        GET_SELECTED["getSelected()"]
        WAIT_FOR_ACTIVE_EDITOR["waitForActiveNotebookEditor()"]
    end
    
    WAIT_FOR_KERNEL_CHANGE --> SELECT_DEFAULT_CONTROLLER
    GET_DEFAULT_KERNEL_CONNECTION --> ACTIVE_INTERPRETER
    GET_DEFAULT_KERNEL_CONNECTION --> REMOTE_PYTHON
    SELECT_DEFAULT_CONTROLLER --> CONTROLLER_PREFERRED
    WAIT_FOR_AUTO_SELECT --> COMPUTE_PREFERRED
```

**Sources:** [src/test/datascience/notebook/helper.ts:426-549](), [src/test/datascience/notebook/helper.ts:612-621](), [src/test/datascience/notebook/helper.ts:697-834]()

### Test Execution Utilities

The testing framework provides comprehensive utilities for validating cell execution and output:

```mermaid
classDiagram
    class NotebookTestHelper {
        +waitForExecutionCompletedSuccessfully(cell, timeout)
        +waitForExecutionCompletedWithErrors(cell)
        +waitForCellExecutionToComplete(cell)
        +waitForTextOutput(cell, text, outputIndex, isExact)
        +waitForOutputs(cell, expectedCount, timeout)
        +waitForCellHavingOutput(cell)
        +getCellOutputs(cell): string
        +hasErrorOutput(outputs): boolean
    }
    
    class ExecutionStateHelper {
        +waitForExecutionInProgress(cell, timeout)
        +waitForQueuedForExecution(cell, timeout)
        +waitForQueuedForExecutionOrExecuting(cell, timeout)
        +waitForCellExecutionState(cell, state, disposables, timeout)
        +assertVSCCellIsNotRunning(cell)
    }
    
    class NotebookCellStateTracker {
        +getCellState(cell): NotebookCellExecutionState
        +getCellStatus(cell): string
    }
    
    NotebookTestHelper --> ExecutionStateHelper
    ExecutionStateHelper --> NotebookCellStateTracker
```

**Sources:** [src/test/datascience/notebook/helper.ts:954-974](), [src/test/datascience/notebook/helper.ts:1018-1064](), [src/test/datascience/notebook/helper.ts:940-953]()

## Test Categories and Execution Patterns

The extension supports multiple test categories with specialized execution patterns and environment configurations.

### Kernel Execution Tests

The core execution tests validate notebook cell execution across different environments and scenarios:

```mermaid
graph TB
    subgraph "execution_test_suite"[Execution Test Suite]
        KERNEL_EXECUTION["Kernel Execution @kernelCore"]
        EXECUTION_SERVICE["executionService.vscode.test.ts"]
        TEST_NOTEBOOK_DOCUMENT["TestNotebookDocument"]
        KERNEL_EXECUTION_INTERFACE["INotebookKernelExecution"]
    end
    
    subgraph "test_scenarios"[Test Scenarios]
        BASIC_EXECUTION["Execute cell using VSCode Kernel @mandatory"]
        STREAMED_OUTPUT["Testing streamed output"]
        ERROR_HANDLING["Verify output & metadata for executed cell with errors"]
        DISPLAY_UPDATES["Updating display data"]
        CLEAR_OUTPUT["Clearing output via code"]
        BACKGROUND_THREADS["More messages from background threads"]
    end
    
    subgraph "execution_validation"[Execution Validation]
        WAIT_FOR_COMPLETION["waitForExecutionCompletedSuccessfully()"]
        WAIT_FOR_TEXT["waitForTextOutput()"]
        GET_CELL_OUTPUTS["getCellOutputs()"]
        HAS_ERROR_OUTPUT["hasErrorOutput()"]
        ASSERT_EXECUTION_ORDER["assertExecutionOrderOfCells()"]
    end
    
    KERNEL_EXECUTION --> EXECUTION_SERVICE
    EXECUTION_SERVICE --> TEST_NOTEBOOK_DOCUMENT
    BASIC_EXECUTION --> WAIT_FOR_COMPLETION
    STREAMED_OUTPUT --> WAIT_FOR_TEXT
    ERROR_HANDLING --> HAS_ERROR_OUTPUT
```

**Sources:** [src/test/datascience/notebook/executionService.vscode.test.ts:71-139](), [src/test/datascience/notebook/executionService.vscode.test.ts:140-147](), [src/test/datascience/notebook/executionService.vscode.test.ts:447-469]()

### Non-Python Kernel Tests

Specialized tests for non-Python kernels validate multi-language support:

```mermaid
graph TB
    subgraph "non_python_test_suite"[Non-Python Test Suite]
        NON_PYTHON_KERNELS["Non-Python Kernel @nonPython"]
        DENO_TESTS["simpleDeno.ipynb test file"]
        PYTHON_EXTENSION_CHECKER["PythonExtensionChecker"]
        PREFERRED_CONTROLLER["ControllerPreferredService"]
    end
    
    subgraph "deno_specific_tests"[Deno Specific Tests]
        AUTO_PICK_DENO["Automatically pick Deno kernel when opening a Deno Notebook"]
        RUN_DENO_NOTEBOOK["Can run a Deno notebook"]
        TYPESCRIPT_EXECUTION["TypeScript cell execution"]
    end
    
    subgraph "kernel_selection_logic"[Kernel Selection Logic]
        COMPUTE_PREFERRED["computePreferred()"]
        START_USING_LOCAL_KERNEL_SPEC["startUsingLocalKernelSpec"]
        TYPESCRIPT_LANGUAGE["kernelSpec.language === 'typescript'"]
        CONTROLLER_CREATION["createKernelController()"]
    end
    
    NON_PYTHON_KERNELS --> DENO_TESTS
    AUTO_PICK_DENO --> COMPUTE_PREFERRED
    RUN_DENO_NOTEBOOK --> START_USING_LOCAL_KERNEL_SPEC
    TYPESCRIPT_EXECUTION --> CONTROLLER_CREATION
```

**Sources:** [src/test/datascience/notebook/nonPythonKernels.vscode.test.ts:28-53](), [src/test/datascience/notebook/nonPythonKernels.vscode.test.ts:75-93](), [src/test/datascience/notebook/nonPythonKernels.vscode.test.ts:94-125]()

### Interrupt and Restart Tests

Critical tests for kernel lifecycle management:

```mermaid
graph TB
    subgraph "interrupt_restart_suite"[Restart/Interrupt/Cancel/Errors @kernelCore]
        INTERRUPT_TESTS["Interrupt Tests"]
        RESTART_TESTS["Restart Tests"]
        KERNEL_LIFECYCLE["Kernel Lifecycle Management"]
        IJUPYTER_SETTINGS["IJupyterSettings"]
    end
    
    subgraph "interrupt_scenarios"[Interrupt Scenarios]
        INTERRUPT_WITH_CANCEL["Interrupting kernel with Cancelling token will cancel cell execution"]
        INTERRUPT_AND_RERUN["Interrupt and running cells again should only run the necessary cells"]
        KERNEL_INTERRUPT["kernel.interrupt()"]
        WAIT_FOR_STOPPED["waitForStoppedEvent()"]
    end
    
    subgraph "restart_scenarios"[Restart Scenarios]
        RESTART_CANCEL_EXECUTION["Restarting kernel will cancel cell execution & we can re-run a cell"]
        RESTART_DURING_RUN_ALL["Restarting kernel during run all will skip the rest of the cells"]
        RESTART_AFTER_DEATH["Can restart a kernel after it dies"]
        KERNEL_RESTART["kernel.restart()"]
        ON_RESTARTED_EVENT["onRestarted event"]
    end
    
    subgraph "validation_helpers"[Validation Helpers]
        CLICK_OK_FOR_RESTART["clickOKForRestartPrompt()"]
        CREATE_EVENT_HANDLER["createEventHandler()"]
        WAIT_FOR_EXECUTION_WITH_ERRORS["waitForExecutionCompletedWithErrors()"]
        NOTEBOOK_CELL_STATE_TRACKER["NotebookCellStateTracker"]
    end
    
    INTERRUPT_TESTS --> INTERRUPT_WITH_CANCEL
    RESTART_TESTS --> RESTART_CANCEL_EXECUTION
    INTERRUPT_WITH_CANCEL --> KERNEL_INTERRUPT
    RESTART_CANCEL_EXECUTION --> KERNEL_RESTART
    KERNEL_RESTART --> ON_RESTARTED_EVENT
    ON_RESTARTED_EVENT --> CREATE_EVENT_HANDLER
```

**Sources:** [src/test/datascience/notebook/interruptRestart.vscode.test.ts:39-103](), [src/test/datascience/notebook/interruptRestart.vscode.test.ts:105-133](), [src/test/datascience/notebook/interruptRestart.vscode.test.ts:134-185]()

### Test Environment Configuration

Test suites require careful setup and teardown with kernel management:

```mermaid
sequenceDiagram
    participant SUITE as "Test Suite"
    participant SETUP as "Suite Setup"
    participant HELPER as "Test Helpers"
    participant KERNEL as "Kernel Provider"
    participant CLEANUP as "Cleanup"
    
    SUITE->>SETUP: suiteSetup()
    SETUP->>HELPER: initialize() API
    SETUP->>HELPER: startJupyterServer()
    SETUP->>KERNEL: getDefaultKernelConnection()
    SETUP->>KERNEL: kernelProvider.getOrCreate()
    KERNEL->>KERNEL: kernel.start()
    
    loop For each test
        SUITE->>HELPER: setup() - clear notebook.cells
        SUITE->>HELPER: execute test logic
        SUITE->>CLEANUP: teardown()
        CLEANUP->>CLEANUP: captureScreenShot() [on failure]
    end
    
    SUITE->>CLEANUP: suiteTeardown()
    CLEANUP->>CLEANUP: closeNotebooksAndCleanUpAfterTests()
    CLEANUP->>CLEANUP: shutdownAllNotebooks()
```

**Sources:** [src/test/datascience/notebook/executionService.vscode.test.ts:82-127](), [src/test/datascience/notebook/helper.ts:364-385](), [src/test/datascience/notebook/helper.ts:315-321]()

## Debug Testing Infrastructure

The extension includes specialized debugging test infrastructure for testing debugger functionality and Run by Line features.

### Debug Test Architecture

```mermaid
graph TB
    subgraph "Debug_Test_Components"
        DEBUG_MANAGER["IDebuggingManager<br/>Debug session management"]
        DEBUG_ADAPTER["getDebugSessionAndAdapter<br/>Adapter access"]
        STOPPED_EVENT["waitForStoppedEvent<br/>Breakpoint handling"]
    end
    
    subgraph "Variable_Testing"
        VAR_PROVIDER["ITestVariableViewProvider<br/>Variable inspection"]
        VAR_MATCHER["waitForVariablesToMatch<br/>State verification"]
        TEST_WEBVIEW["ITestWebviewHost<br/>UI testing interface"]
    end
    
    subgraph "Debug_Commands"
        RUN_BY_LINE["Commands.RunByLine<br/>Step debugging"]
        RUN_BY_LINE_NEXT["Commands.RunByLineNext<br/>Step execution"]
        RUN_BY_LINE_STOP["Commands.RunByLineStop<br/>Stop debugging"]
        INTERRUPT_KERNEL["Commands.InterruptKernel<br/>Kernel interruption"]
    end
    
    DEBUG_MANAGER --> DEBUG_ADAPTER
    DEBUG_ADAPTER --> STOPPED_EVENT
    VAR_PROVIDER --> VAR_MATCHER
    VAR_MATCHER --> TEST_WEBVIEW
    RUN_BY_LINE --> RUN_BY_LINE_NEXT
    RUN_BY_LINE_NEXT --> RUN_BY_LINE_STOP
```

**Sources:** [src/test/datascience/debugger.vscode.test.ts:37-343](), [src/test/datascience/variableView/variableView.vscode.test.ts:32-351]()

### Test Lifecycle Management

Debug tests require careful lifecycle management with setup and teardown procedures:

```mermaid
sequenceDiagram
    participant SUITE as "Test Suite"
    participant SETUP as "Suite Setup"
    participant TEST as "Individual Test"
    participant TEARDOWN as "Teardown"
    
    SUITE->>SETUP: suiteSetup()
    SETUP->>SETUP: initialize() API
    SETUP->>SETUP: closeNotebooksAndCleanUpAfterTests()
    SETUP->>SETUP: prewarmNotebooks()
    SETUP->>TEST: ready for tests
    
    loop For each test
        TEST->>TEST: setup() - create notebook
        TEST->>TEST: execute test logic
        TEST->>TEARDOWN: teardown() - cleanup
        TEARDOWN->>TEARDOWN: closeNotebooks()
        TEARDOWN->>TEARDOWN: captureScreenShot() [on failure]
    end
    
    SUITE->>TEARDOWN: suiteTeardown()
    TEARDOWN->>TEARDOWN: final cleanup
```

**Sources:** [src/test/datascience/debugger.vscode.test.ts:43-71](), [src/test/datascience/debugger.vscode.test.ts:99-108]()

## Performance Testing

The extension includes specialized performance testing infrastructure for measuring notebook and execution performance.

### Performance Test Categories

Performance tests are categorized by their focus areas and execution environments:

```mermaid
graph TD
    subgraph "Notebook_Performance"
        NB_PERF["@notebookPerformance<br/>UI responsiveness"]
        NB_NO_EXT["without Jupyter & Python<br/>Baseline performance"]
        NB_STICKY["notebook.stickyScroll.enabled<br/>Scroll performance"]
    end
    
    subgraph "Execution_Performance"
        EXEC_PERF["@executionPerformance<br/>Code execution speed"]
        EXEC_WITH_EXT["with Jupyter & Python<br/>Full stack performance"]
        EXEC_METRICS["Performance metrics<br/>Timing and memory"]
    end
    
    subgraph "Performance_Environment"
        PERF_FLAG["VSC_JUPYTER_PERF_TEST<br/>Performance mode"]
        INSIDERS_CHANNEL["VSC_JUPYTER_CI_TEST_VSC_CHANNEL<br/>VS Code version"]
        PERF_EXT["vscode-notebook-perf<br/>Performance extension"]
    end
    
    NB_PERF --> NB_NO_EXT
    NB_NO_EXT --> NB_STICKY
    EXEC_PERF --> EXEC_WITH_EXT
    EXEC_WITH_EXT --> EXEC_METRICS
    PERF_FLAG --> PERF_EXT
```

**Sources:** [.vscode/launch.json:323-354](), [.vscode/launch.json:356-385](), [src/test/standardTest.node.ts:51-53]()

This comprehensive development and testing infrastructure ensures code quality, functionality verification, and performance optimization across multiple environments and use cases. The system supports both automated CI/CD workflows and interactive development debugging, providing developers with the tools needed to maintain and extend the extension effectively.

---

