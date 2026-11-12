<!-- source: DeepWiki mcp.deepwiki.com · repo morluto/rea · page 6 Web, JavaScript and Runtime Observation · fetched 2026-10-16 -->

# Web, JavaScript and Runtime Observation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/browser-observation.md](docs/browser-observation.md)
- [docs/javascript-application-workflows.md](docs/javascript-application-workflows.md)
- [src/browser/CdpCaptureEventHandlers.ts](src/browser/CdpCaptureEventHandlers.ts)
- [src/browser/CdpCaptureEventState.ts](src/browser/CdpCaptureEventState.ts)
- [src/browser/CdpCaptureEvents.ts](src/browser/CdpCaptureEvents.ts)
- [src/browser/CdpConnection.ts](src/browser/CdpConnection.ts)
- [src/browser/CdpObservationSession.ts](src/browser/CdpObservationSession.ts)
- [src/browser/CdpPageCapture.ts](src/browser/CdpPageCapture.ts)
- [src/browser/CdpWebMcpDiscovery.ts](src/browser/CdpWebMcpDiscovery.ts)
- [src/domain/browserObservationSchemas.ts](src/domain/browserObservationSchemas.ts)
- [src/domain/javascript/javascriptAstValues.ts](src/domain/javascript/javascriptAstValues.ts)
- [src/domain/javascript/javascriptModuleDeclaration.ts](src/domain/javascript/javascriptModuleDeclaration.ts)
- [src/domain/javascript/javascriptRpcEndpoints.test.ts](src/domain/javascript/javascriptRpcEndpoints.test.ts)
- [src/domain/javascript/javascriptRpcEndpoints.ts](src/domain/javascript/javascriptRpcEndpoints.ts)
- [src/domain/javascript/javascriptSemanticAnalysis.require_links.test.ts](src/domain/javascript/javascriptSemanticAnalysis.require_links.test.ts)
- [src/domain/javascript/javascriptSemanticAnalysis.scope_depth.test.ts](src/domain/javascript/javascriptSemanticAnalysis.scope_depth.test.ts)
- [src/domain/javascript/javascriptSemanticAnalysis.structure.test.ts](src/domain/javascript/javascriptSemanticAnalysis.structure.test.ts)
- [src/domain/javascript/javascriptSemanticAnalysis.ts](src/domain/javascript/javascriptSemanticAnalysis.ts)
- [src/domain/javascript/javascriptSemanticAnalysis.unions.test.ts](src/domain/javascript/javascriptSemanticAnalysis.unions.test.ts)
- [src/domain/javascript/javascriptSemanticEvaluationOrder.ts](src/domain/javascript/javascriptSemanticEvaluationOrder.ts)
- [src/domain/javascript/javascriptSemanticMutationInitializers.ts](src/domain/javascript/javascriptSemanticMutationInitializers.ts)
- [src/domain/javascript/javascriptSemanticProjection.ts](src/domain/javascript/javascriptSemanticProjection.ts)
- [src/domain/javascript/javascriptSemanticRequireOrigin.ts](src/domain/javascript/javascriptSemanticRequireOrigin.ts)
- [src/domain/javascript/javascriptSemanticReturns.ts](src/domain/javascript/javascriptSemanticReturns.ts)
- [src/domain/javascript/javascriptSemanticState.ts](src/domain/javascript/javascriptSemanticState.ts)
- [src/domain/javascript/javascriptSemanticValues.memo.test.ts](src/domain/javascript/javascriptSemanticValues.memo.test.ts)
- [src/domain/javascript/javascriptSemanticValues.ts](src/domain/javascript/javascriptSemanticValues.ts)
- [src/domain/javascript/javascriptStaticAnalysis.ts](src/domain/javascript/javascriptStaticAnalysis.ts)
- [src/domain/webCaptureDiff.ts](src/domain/webCaptureDiff.ts)
- [tests/acceptance/applications/emptyImportNameCli.test.ts](tests/acceptance/applications/emptyImportNameCli.test.ts)
- [tests/acceptance/applications/exportedFunctionBindingsCli.test.ts](tests/acceptance/applications/exportedFunctionBindingsCli.test.ts)
- [tests/acceptance/applications/javascriptRpcPropertyOwnershipCli.test.ts](tests/acceptance/applications/javascriptRpcPropertyOwnershipCli.test.ts)
- [tests/acceptance/applications/unboundRequires.test.ts](tests/acceptance/applications/unboundRequires.test.ts)
- [tests/boundary/browser/cdpBrowserProvider.document_script.test.ts](tests/boundary/browser/cdpBrowserProvider.document_script.test.ts)
- [tests/boundary/browser/cdpBrowserProvider.sensitive_data.test.ts](tests/boundary/browser/cdpBrowserProvider.sensitive_data.test.ts)
- [tests/boundary/browser/cdpConnection.test.ts](tests/boundary/browser/cdpConnection.test.ts)
- [tests/boundary/browser/cdpHttpComparison.test.ts](tests/boundary/browser/cdpHttpComparison.test.ts)
- [tests/boundary/browser/cdpObservationResourceTypes.test.ts](tests/boundary/browser/cdpObservationResourceTypes.test.ts)
- [tests/boundary/browser/webCaptureDiff.test.ts](tests/boundary/browser/webCaptureDiff.test.ts)
- [tests/boundary/cli/accessibilityCaptureComparison.test.ts](tests/boundary/cli/accessibilityCaptureComparison.test.ts)
- [tests/boundary/cli/httpCaptureComparison.test.ts](tests/boundary/cli/httpCaptureComparison.test.ts)
- [tests/fixtures/fakeCdpBrowser.ts](tests/fixtures/fakeCdpBrowser.ts)
- [tests/fixtures/fakeCdpBrowserEvents.ts](tests/fixtures/fakeCdpBrowserEvents.ts)
- [tests/fixtures/fakeCdpBrowserTypes.ts](tests/fixtures/fakeCdpBrowserTypes.ts)
- [tests/fixtures/httpComparisonBrowser.ts](tests/fixtures/httpComparisonBrowser.ts)
- [tests/fixtures/javascriptReturnShapes.ts](tests/fixtures/javascriptReturnShapes.ts)

</details>



This page provides a high-level overview of REA's capabilities for analyzing web applications, JavaScript code, and runtime environments. This includes observing browser behavior via the Chrome DevTools Protocol (CDP), capturing scenarios with Playwright and Electron, performing static and semantic analysis of JavaScript, recovering source map information, and managing web network captures and script exports. These capabilities enable a comprehensive understanding of web-based applications, from their deployed bundles to their dynamic execution.

## CDP Browser Observation

REA can attach to a running Chrome-family browser using the Chrome DevTools Protocol (CDP) via `CdpConnection` [src/browser/CdpConnection.ts:30-44]() to passively observe web pages. This allows for the capture of various aspects of a web page through `capturePage` [src/browser/CdpPageCapture.ts:70-102](), including DOM structure, accessibility nodes, scripts, network resources, storage fingerprints, and WebMCP declarations. REA's CDP integration focuses on passive observation rather than active browser automation.

For details, see [CDP Browser Observation](#6.1).

Sources:
- [src/browser/CdpConnection.ts:30-44]()
- [src/browser/CdpPageCapture.ts:70-102]()
- [docs/browser-observation.md]()

## Scenario Capture (Playwright and Electron)

Beyond passive observation, REA can actively drive browser and Electron environments to capture specific user scenarios. The `PlaywrightBrowserScenarioProvider` orchestrates browser interactions, recording events and artifacts throughout a defined scenario. For Electron applications, REA can launch and control the application, capturing IPC messages, window events, and process metrics. This provides a controlled and reproducible way to gather runtime evidence.

For details, see [Scenario Capture (Playwright and Electron)](#6.2).

Sources:
- [docs/electron-observation.md]()

## JavaScript Static and Semantic Analysis

REA provides robust capabilities for analyzing JavaScript code without execution. This includes parsing web bundles to identify module imports, routes, API endpoints, and vendor fingerprints via `analyzeJavaScriptStaticSource` [src/domain/javascript/javascriptStaticAnalysis.ts:61-69](). The system can also perform deeper semantic analysis to recover lexical bindings, aliases, constants, and module links using `analyzeJavaScriptSemantics` [src/domain/javascript/javascriptSemanticAnalysis.ts:119-127](). Furthermore, REA can trace and recover original source code from source maps, even when they are unavailable or partial.

### JavaScript Analysis Flow
```mermaid
graph TD
    A["WebPageInspection" --- "src/domain/browserObservationSchemas.ts"] --> B["analyzeCapturedWebBundle" --- "src/domain/webBundleAnalyzer.ts"];
    B --> C["WebBundleAnalysis" --- "src/domain/webBundleAnalyzerTypes.ts"];
    C --> D["Observations (Chunks, Routes, Endpoints, WebMCP)" --- "src/domain/webBundleAnalyzer.ts"];
    C --> E["Inferences (Bundler, Framework)" --- "src/domain/webBundleAnalyzer.ts"];
    C --> F["Completeness (Parse Failures, Visited Nodes)" --- "src/domain/webBundleAnalyzer.ts"];
    C --> G["Source Maps (WebSourceMaps)" --- "src/domain/webBundleAnalyzer.ts"];
    G --> H["fetchWebSourceMaps" --- "src/browser/WebSourceMapFetcher.ts"];
    H --> I["Original Sources" --- "src/browser/WebSourceMapFetcher.ts"];
    H --> J["Original Module Edges" --- "src/browser/WebSourceMapFetcher.ts"];
    H --> K["Mappings" --- "src/browser/WebSourceMapFetcher.ts"];

    subgraph Static Analysis
        B
        C
        D
        E
        F
    end

    subgraph Source Map Recovery
        G
        H
        I
        J
        K
    end
```
Sources:
- [src/domain/javascript/javascriptStaticAnalysis.ts:61-69]()
- [src/domain/javascript/javascriptSemanticAnalysis.ts:119-127]()
- [src/browser/CdpConnection.ts:30-44]()

### Web Bundle Analysis Details

The bundle analyzer processes `WebPageInspection` data to extract various insights. It identifies static and dynamic module imports, API endpoints, and potential application routes. It also detects WebMCP tool declarations and infers bundler or framework usage. The analysis accounts for parsing errors and reports completeness metrics, including visited AST nodes and parse failures.

```mermaid
graph TD
    A["IncludedScript" --- "src/domain/webBundleAnalyzerTypes.ts"] --> B["analyzeScript" --- "src/domain/webBundleAnalyzer.ts"];
    B --> C["parseJavaScriptSource" --- "src/domain/javascript/javascriptSourceParser.ts"];
    C -- "AST" --> D["traverseJavaScriptAstSteps" --- "src/domain/javascript/javascriptSemanticTraversal.ts"];
    D -- "Node" --> E["inspectNode" --- "src/domain/javascript/javascriptStaticAnalysisCalls.ts"];

    E --> F["ImportDeclaration / ExportAllDeclaration" --- "src/domain/javascript/javascriptModuleDeclaration.ts"];
    F -- "specifier" --> G["addEdge(kind: static_import)" --- "src/domain/webBundleAnalyzer.ts"];

    E --> H["ImportExpression" --- "src/domain/javascript/javascriptStaticAnalysisCalls.ts"];
    H -- "specifier" --> I["addEdge(kind: dynamic_import)" --- "src/domain/webBundleAnalyzer.ts"];

    E --> J["CallExpression / NewExpression" --- "src/domain/javascript/javascriptStaticAnalysisCalls.ts"];
    J -- "calleeName" --> K["require / importScripts" --- "src/domain/javascript/javascriptStaticAnalysisCalls.ts"];
    K -- "specifier" --> L["addEdge(kind: require)" --- "src/domain/webBundleAnalyzer.ts"];

    J -- "calleeName" --> M["Route Call Names" --- "src/domain/javascript/javascriptStaticAnalysisCalls.ts"];
    M -- "route" --> N["addFinding(collection: routes)" --- "src/domain/javascript/javascriptStaticAnalysisState.ts"];

    J -- "endpointArgument" --> O["addFinding(collection: endpoints)" --- "src/domain/javascript/javascriptStaticAnalysisState.ts"];

    J -- "modelContext.registerTool" --> P["addWebMcpDeclaration" --- "src/domain/webBundleAnalyzer.ts"];

    E --> Q["ObjectProperty" --- "src/domain/javascript/javascriptStaticAnalysisCalls.ts"];
    Q -- "value" --> R["addFinding(collection: routes)" --- "src/domain/javascript/javascriptStaticAnalysisState.ts"];

    subgraph Analysis Accumulator
        G
        I
        L
        N
        O
        P
        R
    end
```
Sources:
- [src/domain/javascript/javascriptStaticAnalysis.ts:61-69]()
- [src/domain/javascript/javascriptSemanticAnalysis.ts:119-127]()
- [src/domain/javascript/javascriptSemanticTraversal.ts:44-46]()

For details, see [JavaScript Static and Semantic Analysis](#6.3).

## Application Workflows and Version Comparison

REA can project an application graph from collected evidence, enabling advanced workflows like tracing application features and comparing different versions of an application. This involves correlating static analysis results with runtime observations, reconstructing JavaScript artifacts, and classifying reference sources as detailed in cross-layer workflows [docs/javascript-application-workflows.md:1-25]().

For details, see [Application Workflows and Version Comparison](#6.4).

Sources:
- [docs/javascript-application-workflows.md:1-25]()

## Web Network Captures and Script Export

For handling network captures and historical data, REA supports ingestion of HAR and qlog archives, mitmproxy bridges, pcap outputs, and web script publication/export services. Captured Debugger sources can be exported for REA's existing static JavaScript analysis using script export tools [docs/browser-observation.md:1-8]().

For details, see [Web Network Captures and Script Export](#6.5).

Sources:
- [docs/browser-observation.md:1-8]()

---

