<!-- source: DeepWiki mcp.deepwiki.com · repo morluto/rea · page 7 Evidence, Investigation and Reconstruction · fetched 2026-10-09 -->

# Evidence, Investigation and Reconstruction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/application/EvidenceBundleCommands.ts](src/application/EvidenceBundleCommands.ts)
- [src/application/EvidenceBundleFiles.ts](src/application/EvidenceBundleFiles.ts)
- [src/application/EvidenceInputResolver.test.ts](src/application/EvidenceInputResolver.test.ts)
- [src/application/binary/BinarySessionRecords.ts](src/application/binary/BinarySessionRecords.ts)
- [src/application/investigation/EvidenceLedger.residualUnknown.test.ts](src/application/investigation/EvidenceLedger.residualUnknown.test.ts)
- [src/application/investigation/EvidenceLedger.test.ts](src/application/investigation/EvidenceLedger.test.ts)
- [src/application/investigation/EvidenceLedger.ts](src/application/investigation/EvidenceLedger.ts)
- [src/application/investigation/InvestigationRecords.test.ts](src/application/investigation/InvestigationRecords.test.ts)
- [src/application/investigation/InvestigationRecords.ts](src/application/investigation/InvestigationRecords.ts)
- [src/application/investigation/UnknownEvidence.ts](src/application/investigation/UnknownEvidence.ts)
- [src/contracts/investigationExamples.ts](src/contracts/investigationExamples.ts)
- [src/domain/changedBehavior.ts](src/domain/changedBehavior.ts)
- [src/domain/evidenceBundle.test.ts](src/domain/evidenceBundle.test.ts)
- [src/domain/evidenceBundle.ts](src/domain/evidenceBundle.ts)
- [src/domain/reconstructionVerification.functionSources.test.ts](src/domain/reconstructionVerification.functionSources.test.ts)
- [src/domain/reconstructionVerification.test.ts](src/domain/reconstructionVerification.test.ts)
- [src/domain/reconstructionVerification.ts](src/domain/reconstructionVerification.ts)
- [src/domain/reconstructionVerificationSchemas.ts](src/domain/reconstructionVerificationSchemas.ts)
- [src/domain/staticRuntimeCorrelation.ts](src/domain/staticRuntimeCorrelation.ts)
- [src/server/promptCompletion.ts](src/server/promptCompletion.ts)
- [src/server/registerProcessComparisonTool.ts](src/server/registerProcessComparisonTool.ts)
- [src/server/sessionToolPolicies.ts](src/server/sessionToolPolicies.ts)
- [tests/boundary/mcp/functionComparisonMcp.test.ts](tests/boundary/mcp/functionComparisonMcp.test.ts)
- [tests/boundary/mcp/processEvidenceIdentityMcp.test.ts](tests/boundary/mcp/processEvidenceIdentityMcp.test.ts)
- [tests/boundary/mcp/processTraceAdaptersParity.test.ts](tests/boundary/mcp/processTraceAdaptersParity.test.ts)
- [tests/boundary/mcp/serverUnknownsMcp.test.ts](tests/boundary/mcp/serverUnknownsMcp.test.ts)
- [tests/boundary/process/processCaptureTerminal.test.ts](tests/boundary/process/processCaptureTerminal.test.ts)
- [tests/composition/analysis-sessions/binarySession.test.ts](tests/composition/analysis-sessions/binarySession.test.ts)

</details>



This section provides a high-level overview of REA's epistemic model, which underpins how REA collects, stores, and reasons about information. It covers the core concepts of evidence records, the management of unknowns, and the mechanisms for verifying reconstructions and evaluating coverage. Detailed explanations and technical specifications for each topic are provided in the linked child pages.

## Evidence Model and Ledger
REA operates on a foundation of immutable evidence records. Each record captures a specific observation or derived fact about a binary target, including its provenance, parameters, and results. These records are stored and managed by an `EvidenceLedger` [src/application/investigation/EvidenceLedger.ts:36-36](), which ensures their integrity and provides mechanisms for deduplication and atomic import of `EvidenceBundle`s [src/application/investigation/EvidenceLedger.ts:63-154](). The ledger also tracks "unknown" evidence, representing gaps in understanding or contradictions that require further investigation. Evidence can be exported and imported as bundle files [src/application/EvidenceBundleFiles.ts:18-37](), allowing for sharing and comparison across different analysis sessions.

For details, see [Evidence Model and Ledger](#7.1).

## Reconstruction Verification and Obligations
REA provides tools to verify the accuracy and completeness of a "reconstruction," which is a model or understanding of a binary's behavior or structure. This involves comparing observed behavior (e.g., via process captures) with static analysis results, and evaluating how well they correlate. The `reconstructionVerification` [src/domain/reconstructionVerification.ts:74-120]() function assesses declared claims against collected evidence, identifying discrepancies or unresolved areas. The system also tracks `changedBehavior` [src/domain/changedBehavior.ts:115-157]() to highlight differences between versions or observed states. An "obligation ledger" (represented by `ResidualUnknown`s [src/domain/residualUnknown.js:13-14]()) records outstanding questions or required investigations, guiding the analysis process.

For details, see [Reconstruction Verification and Obligations](#7.2).

## Process Capture and Ownership
The `src/process` capture subsystem [src/server/registerProcessComparisonTool.ts:26-29]() is crucial for observing the dynamic behavior of binaries. This involves capturing detailed information about process execution, including filesystem interactions, network activity, and inter-process communication. REA ensures proper process ownership and command identity during these captures. Filesystem snapshots are taken to record the state before and after execution, enabling precise comparison. The system also handles cancellation and lifecycle management of captured processes, with specific considerations for Windows owned processes and native addons.

For details, see [Process Capture and Ownership](#7.3).

### Epistemic Model Overview
REA's epistemic model is centered around the concept of `Evidence` [src/domain/evidence.js:9-10](), which forms the basis for all analysis and reasoning. This evidence is collected, stored, and then used to verify claims and identify areas requiring further investigation.

```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Evidence Records"]
        B["Unknowns"]
        C["Obligation Ledger"]
        D["Reconstruction Verification"]
        E["Changed Behavior"]
        F["Static/Runtime Correlation"]
        G["Process Capture"]
    end

    subgraph "Code Entity Space"
        H[/"Evidence" <br/> `src/domain/evidence.js` /]
        I[/"EvidenceLedger" <br/> `src/application/investigation/EvidenceLedger.ts` /]
        J[/"ResidualUnknown" <br/> `src/domain/residualUnknown.js` /]
        K[/"reconstructionVerification" <br/> `src/domain/reconstructionVerification.ts` /]
        L[/"changedBehavior" <br/> `src/domain/changedBehavior.ts` /]
        M[/"correlateStaticAndRuntime" <br/> `src/domain/staticRuntimeCorrelation.ts` /]
        N[/"compareProcessCaptures" <br/> `src/domain/process/processCapture.js` /]
        O[/"PROCESS_CAPTURE_EVIDENCE" <br/> `src/server/registerProcessComparisonTool.ts` /]
    end

    A --> H
    B --> J
    C --> J
    D --> K
    E --> L
    F --> M
    G --> N
    G --> O

    H -- "managed by" --> I
    J -- "managed by" --> I
    K -- "uses" --> I
    K -- "uses" --> J
    L -- "uses" --> H
    L -- "uses" --> N
    M -- "uses" --> H
    M -- "uses" --> N
    N -- "generates" --> H
    O -- "defines" --> N
```
Sources:
- [src/domain/evidence.js:9-10]()
- [src/application/investigation/EvidenceLedger.ts:36-36]()
- [src/domain/residualUnknown.js:13-14]()
- [src/domain/reconstructionVerification.ts:74-120]()
- [src/domain/changedBehavior.ts:115-157]()
- [src/domain/staticRuntimeCorrelation.ts:164-178]()
- [src/domain/process/processCapture.js:18-22]()
- [src/server/registerProcessComparisonTool.ts:26-29]()

### Evidence Flow and Unknown Management
The lifecycle of evidence and unknowns within REA involves recording, comparing, and resolving.

```mermaid
graph TD
    subgraph "Evidence Collection"
        A_NL["Raw Observations / Derived Facts"]
        B_CE["createEvidence()"]
        C_E["Evidence Record"]
    end

    subgraph "Evidence Ledger"
        D_EL["EvidenceLedger.record()"]
        E_EL["EvidenceLedger.import()"]
        F_EL["EvidenceLedger.export()"]
        G_EB["EvidenceBundle"]
    end

    subgraph "Unknown Management"
        H_RU["RecordUnknownInput"]
        I_RU["ResidualUnknown"]
        J_EL["EvidenceLedger.recordUnknown()"]
        K_EL["EvidenceLedger.updateUnknown()"]
        L_EL["EvidenceLedger.listUnknowns()"]
    end

    subgraph "Comparison and Verification"
        M_CP["compare_process_captures"]
        N_CC["compare_artifacts / compare_functions"]
        O_CB["findChangedBehavior()"]
        P_SRC["correlateStaticAndRuntime()"]
        Q_RV["verifyReconstruction()"]
    end

    A_NL --> B_CE
    B_CE --> C_E
    C_E --> D_EL
    C_E --> E_EL
    D_EL --> G_EB
    E_EL --> G_EB
    F_EL --> G_EB

    H_RU --> J_EL
    J_EL --> I_RU
    I_RU --> K_EL
    K_EL --> I_RU
    L_EL --> I_RU

    C_E -- "input to" --> M_CP
    C_E -- "input to" --> N_CC
    M_CP -- "generates" --> C_E
    N_CC -- "generates" --> C_E

    C_E -- "input to" --> O_CB
    O_CB -- "reports" --> I_RU
    C_E -- "input to" --> P_SRC
    P_SRC -- "reports" --> I_RU
    G_EB -- "input to" --> Q_RV
    Q_RV -- "reports" --> I_RU
```
Sources:
- [src/domain/evidence.js:7-11]()
- [src/application/investigation/EvidenceLedger.ts:36-36]()
- [src/application/investigation/EvidenceLedger.ts:41-60]()
- [src/application/investigation/EvidenceLedger.ts:63-154]()
- [src/application/investigation/EvidenceLedger.ts:157-163]()
- [src/application/investigation/EvidenceLedger.ts:178-181]()
- [src/application/investigation/EvidenceLedger.ts:200-203]()
- [src/application/investigation/EvidenceLedger.ts:219-222]()
- [src/domain/residualUnknown.js:13-14]()
- [src/domain/residualUnknown.js:15-19]()
- [src/server/registerProcessComparisonTool.ts:69-85]()
- [src/domain/changedBehavior.ts:115-157]()
- [src/domain/staticRuntimeCorrelation.ts:164-178]()
- [src/domain/reconstructionVerification.ts:74-120]()

---

