<!-- source: DeepWiki mcp.deepwiki.com · repo letta-ai/letta · page 3 Governance and Legal · fetched 2026-11-09 -->

# Governance and Legal

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [PRIVACY.md](PRIVACY.md)
- [SECURITY.md](SECURITY.md)
- [TERMS.md](TERMS.md)

</details>



This page provides a high-level overview of the governance, legal frameworks, and privacy policies governing the Letta project. As this repository serves as a landing page and archive for the Letta V1 server, these documents define the relationship between the maintainers and the community during and after the transition to `letta-ai/letta-code`.

## Repository Governance

The Letta project has migrated its active development to a new codebase. Consequently, this repository is in a restricted state regarding community contributions.

*   **Contribution Policy**: This repository is archived and does not accept Pull Requests or Issues for the retired V1 server. All active development occurs in `letta-ai/letta-code`. For details, see [Contributing and Security](#3.1).
*   **Security Disclosure**: Security is a priority for Letta. Vulnerabilities should be reported via private channels rather than public issue trackers to prevent exploitation. For details, see [Contributing and Security](#3.1).

### Governance Workflow Transition

The following diagram illustrates the transition of governance and contribution flow from the legacy repository to the current active development environment.

**Governance Flow Transition**
```mermaid
graph TD
    subgraph "Legacy_Space [letta-ai/letta]"
        [V1_Archive_Branch] -->|Read-Only| [Historical_Reference]
        [Issue_Tracker] -->|Redirect| [letta-ai/letta-code]
    end

    subgraph "Active_Space [letta-ai/letta-code]"
        [PR_Process] -->|Maintains| [App_Server]
        [Security_Policy] -->|Protects| [Agent_SDK]
    end

    [User] -->|Report_Vulnerability| [Email_Support]
    [Email_Support] --> [Security_Team]
    [Security_Team] -->|Patch| [PR_Process]
```
Sources: [CONTRIBUTING.md:1-5](), [SECURITY.md:1-9]()

---

## Legal and Policy Framework

Letta is distributed under standard open-source terms, supplemented by specific terms of service for hosted components and a privacy policy covering telemetry and data handling.

*   **Licensing**: The codebase is licensed under the **Apache License 2.0**. This provides a perpetual, worldwide, non-exclusive grant of copyright and patent rights to users. For details, see [License, Terms, and Privacy](#3.2).
*   **Terms of Service**: Users of Letta services agree to a binding contract that covers account security, content ownership, and liability limits. For details, see [License, Terms, and Privacy](#3.2).
*   **Privacy and Telemetry**: Letta collects basic anonymous telemetry to improve the product. Users can opt-out by setting `telemetry_disabled = True` in their configuration. For details, see [License, Terms, and Privacy](#3.2).

### Data and Licensing Entities

The following diagram maps the legal entities and data flags mentioned in the policy documents to their conceptual roles in the system.

**Policy to Code Entity Mapping**
```mermaid
graph LR
    subgraph "Natural_Language_Policy"
        "Apache_2.0"
        "Telemetry_Opt_Out"
        "User_Content"
    end

    subgraph "Code_Entity_Space"
        "LICENSE_File"["FILE: LICENSE"]
        "Telemetry_Flag"["telemetry_disabled"]
        "Hosted_Services"["Hosted_Endpoints"]
    end

    "Apache_2.0" --- "LICENSE_File"
    "Telemetry_Opt_Out" --- "Telemetry_Flag"
    "User_Content" --- "Hosted_Services"
```
Sources: [LICENSE:1-130](), [TERMS.md:1-42](), [PRIVACY.md:1-15]()

---

## Child Pages

For detailed documentation on specific legal and governance topics, please refer to the following sub-pages:

| Page | Description |
| :--- | :--- |
| **[Contributing and Security](#3.1)** | Detailed guidelines on the archived status of this repo and how to report security vulnerabilities via `support@letta.com`. |
| **[License, Terms, and Privacy](#3.2)** | Full breakdown of the Apache 2.0 license, user responsibilities under the Terms of Service, and technical details on telemetry collection and GDPR/CCPA compliance. |

Sources: [CONTRIBUTING.md:1-5](), [SECURITY.md:1-9](), [LICENSE:1-130](), [TERMS.md:1-42](), [PRIVACY.md:1-15]()

---

