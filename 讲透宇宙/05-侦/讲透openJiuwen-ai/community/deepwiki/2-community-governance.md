<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/community · page 2 Community Governance · fetched 2026-11-02 -->

# Community Governance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contribute/License-and-Copyright-Guidelines.md](contribute/License-and-Copyright-Guidelines.md)
- [contribute/License-and-Special-License-Review-Guidelines.md](contribute/License-and-Special-License-Review-Guidelines.md)
- [openJiuwen-Community-Code-of-Conduct.md](openJiuwen-Community-Code-of-Conduct.md)
- [sigs/README.md](sigs/README.md)

</details>



## Purpose and Scope
This page provides a high-level overview of how the openJiuwen community is governed, establishing the foundational structures, standards, and behavioral norms that guide all contributors, maintainers, and Special Interest Groups (SIGs). For granular details regarding community leadership charters or behavioral enforcement, please refer to the child pages: [Core Team & Charter](#2.1) and [Code of Conduct & Community Rules](#2.2).

---

## 2.1 Core Team & Charter
The governance of the openJiuwen project is led by the Core Team and the Project Management Committee (PMC), which oversee technical direction, architectural evolution, and cross-SIG coordination. The core team charter establishes the rules for board composition, voting rights, decision-making processes, and lifecycle management for repositories and maintainers.

For detailed information on the charter, board membership, and decision-making workflows, see [Core Team & Charter](#2.1).

```mermaid
graph TD
    subgraph "Community Governance Structure"
        A["PMC & Core Team" / "coreteam/"] --> B["SIG Leads" / "sigs/"]
        B --> C["Maintainers" / "openJiuwen/a/*"]
        C --> D["Contributors" / "pull-requests"]
    end
```
*Diagram 1: Governance hierarchy mapping community roles to structural entities.*

Sources: `sigs/README.md:1-1`

---

## 2.2 Code of Conduct & Community Rules
The openJiuwen community adheres strictly to the Contributor Covenant v3.0 to ensure a safe, inclusive, and productive environment for all participants [openJiuwen-Community-Code-of-Conduct.md:1-3](). 

The community code of conduct defines core pledges, encouraged collaborative behaviors (such as goodwill, respect for different viewpoints, and constructive feedback), and explicitly restricts behaviors such as harassment, personal attacks, discrimination, and breaches of confidentiality [openJiuwen-Community-Code-of-Conduct.md:7-44](). When violations occur, administrators follow a transparent tiered response mechanism [openJiuwen-Community-Code-of-Conduct.md:69-88]().

```mermaid
graph TD
    subgraph "Incident Lifecycle"
        E["Report Incident" / "contact@openjiuwen.com"] --> F["Investigation" / "openJiuwen-Community-Code-of-Conduct.md"]
        F --> G{{"Violation Severity"}}
        G -->|"Tier 1"| H["Warning" / "Private Warning"]
        G -->|"Tier 2"| I["Temporary Restriction" / "Cooling-off Period"]
        G -->|"Tier 3"| J["Temporary Suspension" / "Access Revocation"]
    end
```
*Diagram 2: Code of conduct violation handling workflow mapped to enforcement routines.*

For complete behavioral guidelines, reporting procedures, and legal/privacy statements, see [Code of Conduct & Community Rules](#2.2).

Sources: `openJiuwen-Community-Code-of-Conduct.md:1-88`

---

