<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/sciencediscovery · page 8 Review, Provenance, and Permissions · fetched 2026-11-02 -->

# Review, Provenance, and Permissions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/src/EvidenceModal.tsx](apps/web/src/EvidenceModal.tsx)
- [apps/web/src/GovernedDownloadCards.tsx](apps/web/src/GovernedDownloadCards.tsx)
- [apps/web/src/PermissionDecisionActions.tsx](apps/web/src/PermissionDecisionActions.tsx)
- [apps/web/src/Permissions.tsx](apps/web/src/Permissions.tsx)
- [apps/web/src/ReviewerControlCard.tsx](apps/web/src/ReviewerControlCard.tsx)
- [apps/web/src/ReviewerPanel.tsx](apps/web/src/ReviewerPanel.tsx)
- [apps/web/src/ScientificArtifacts.tsx](apps/web/src/ScientificArtifacts.tsx)

</details>



This page documents the full traceability stack within ScienceDiscovery. It covers how the system ensures scientific integrity through the **Reviewer Specialist**, maintains a verifiable chain of custody via **CAS-backed Provenance**, and enforces safety through a structured **Permission Lifecycle**.

## Reviewer Specialist and Integrity Flow

The **Reviewer Specialist** is a built-in agentic service designed to validate scientific artifacts. It operates at multiple levels (Quick, Smart, Deep) to verify structural integrity, citation validity, and evidence consistency [apps/web/src/ReviewerPanel.tsx:18-29]().

### Review Lifecycle
When a review is triggered, the system executes a series of checks defined by the `ArtifactReviewRun` schema [apps/web/src/ReviewerPanel.tsx:15-15]().

1.  **Quick Review**: Focuses on JSON structure and basic artifact provenance [apps/web/src/ReviewerPanel.tsx:108-110]().
2.  **Smart/Deep Review**: Extends to citation identity, claim support, and numeric evidence validation [apps/web/src/ReviewerPanel.tsx:106-107]().
3.  **Finding Generation**: The specialist generates `findings` with specific severity levels (`critical`, `warning`) and standardized error codes [apps/web/src/ReviewerPanel.tsx:42-51]().

### Common Finding Codes
| Code | Label | Description |
| :--- | :--- | :--- |
| `CITATION_CLAIM_NOT_SUPPORTED` | Citation claim unsupported | The linked paper does not support the claim. |
| `ARTIFACT_JSON_INVALID` | Invalid JSON | The artifact does not match its schema. |
| `COMPUTATION_EVIDENCE_VALUE_MISMATCH` | Evidence value mismatch | Numeric data in the artifact contradicts source calculations. |

**Sources:** [apps/web/src/ReviewerPanel.tsx:53-68](), [apps/web/src/ReviewerPanel.tsx:93-102]()

---

## Provenance and Content-Addressed Storage (CAS)

Every artifact and execution record in ScienceDiscovery is backed by a Content-Addressed Storage (CAS) system. This ensures that the history of a scientific discovery is immutable and verifiable.

### Data Flow: From Code to Provenance
The following diagram bridges the **Natural Language Space** (Discovery Process) to the **Code Entity Space** (Schema and Storage).

**Discovery Traceability Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Scientific Claim"]
        B["Supporting Evidence"]
        C["Source Paper"]
    end

    subgraph "Code Entity Space"
        A -->|"derived_from"| A1["ArtifactVersionProvenance"]
        B -->|"extracted_from"| B1["MemoryGraphNode (Evidence)"]
        C -->|"references"| C1["MemoryGraphNode (Paper)"]
        
        A1 -->|"contentHash"| CAS["CAS (SHA-256)"]
        B1 -->|"extra.content"| CAS
    end

    [apps/web/src/ScientificArtifacts.tsx:19-24] --> A1
    [apps/web/src/EvidenceModal.tsx:25-28] --> B1
    [apps/web/src/EvidenceModal.tsx:46-48] --> C1
```
**Sources:** [apps/web/src/ScientificArtifacts.tsx:19-24](), [apps/web/src/EvidenceModal.tsx:25-28](), [apps/web/src/EvidenceModal.tsx:46-48]()

### Artifact Derivation
The UI surfaces provenance through the `ScientificArtifactVersion` and `ArtifactVersionProvenance` types [apps/web/src/ScientificArtifacts.tsx:19-23](). Users can view the exact process environment (environment variables, shell state) and the specific tool invocations that produced a version [apps/web/src/ScientificArtifacts.tsx:154-162]().

---

## Permissions and Governance

ScienceDiscovery implements a request/grant lifecycle for sensitive operations, such as downloading external datasets, executing arbitrary code, or accessing host directories.

### Permission Lifecycle State Machine
Permissions flow through a state machine managed by the API and reflected in the frontend `PermissionCards` [apps/web/src/Permissions.tsx:34-42]().

1.  **Request**: The agent encounters a restricted resource and issues a `PermissionRequest` [apps/web/src/PermissionDecisionActions.tsx:15-15]().
2.  **Decision**: The user provides a `PermissionDecision`: `allow_once`, `allow_matching`, or `deny` [apps/web/src/PermissionDecisionActions.tsx:38-40]().
3.  **Grant**: If allowed, a `PermissionGrant` is created, scoped to the current Session [apps/web/src/Permissions.tsx:81-87]().

**Permission Action Mapping**
```mermaid
graph LR
    subgraph "Permission Actions"
        Code["'code'"]
        Down["'artifact_download'"]
        Conn["'connector'"]
        Host["'host'"]
    end

    subgraph "Code Implementation"
        Code --> P1["PermissionRequest.action"]
        Down --> P1
        Conn --> P1
        Host --> P1
        
        P1 -->|decide| PDA["PermissionDecisionActions.tsx"]
        PDA -->|grant| PGM["PermissionGrantManager"]
    end

    [apps/web/src/Permissions.tsx:25-32] --> P1
    [apps/web/src/PermissionDecisionActions.tsx:29-42] --> PDA
    [apps/web/src/Permissions.tsx:81-93] --> PGM
```
**Sources:** [apps/web/src/Permissions.tsx:25-32](), [apps/web/src/PermissionDecisionActions.tsx:29-42](), [apps/web/src/Permissions.tsx:81-93]()

### Governed Downloads
A specialized form of permission is the **Governed Download**. These are tracked as `ArtifactJob` entities [apps/web/src/GovernedDownloadCards.tsx:17-17](). The system requires explicit user "Preparation" before a download begins, ensuring that the agent cannot exfiltrate or pull large data without oversight [apps/web/src/GovernedDownloadCards.tsx:55-61]().

**Sources:** [apps/web/src/GovernedDownloadCards.tsx:88-102]()

---

## Evidence and Claims Traceability

The system links scientific claims to evidence stored in the **Science Memory Graph**.

### Evidence Verification
When viewing evidence in the `EvidenceModal`, the system fetches the "Chain of Thought" [apps/web/src/EvidenceModal.tsx:74-76](). This involves:
- **Provenance Tab**: Shows the `Paper` nodes from which the evidence was extracted [apps/web/src/EvidenceModal.tsx:80-83]().
- **Memory Graph**: Anchors the `MemoryGraphExplorer` on the specific evidence node to visualize the full logical derivation [apps/web/src/EvidenceModal.tsx:92-105]().

**Sources:** [apps/web/src/EvidenceModal.tsx:23-40](), [apps/web/src/EvidenceModal.tsx:136-150]()

---

