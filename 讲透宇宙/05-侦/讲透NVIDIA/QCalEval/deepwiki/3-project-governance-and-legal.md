<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/QCalEval · page 3 Project Governance and Legal · fetched 2026-10-26 -->

# Project Governance and Legal

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ATTRIBUTIONS](ATTRIBUTIONS)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)

</details>



This page provides a high-level overview of the legal framework, licensing, and contribution guidelines for the QCalEval project. It outlines how the software and datasets are licensed, the requirements for third-party attributions, and the formal processes for contributing code or reporting security vulnerabilities.

### Governance and Legal Framework

The QCalEval project operates under a standardized open-source model managed by NVIDIA. The governance structure ensures that all contributions are legally cleared through a sign-off process and that security concerns are handled through dedicated professional channels rather than public issue trackers.

#### Legal Entity Relationships
The following diagram illustrates the relationship between the project's legal components and the entities involved in its governance.

**Legal and Contribution Workflow**
```mermaid
graph TD
    subgraph "Legal Framework"
        ["LICENSE (Apache 2.0)"]
        ["ATTRIBUTIONS (Third-Party)"]
    end

    subgraph "Contribution Process"
        ["CONTRIBUTING.md"] -- "Requires" --> ["DCO Sign-off"]
        ["DCO Sign-off"] -- "via" --> ["git commit -s"]
    end

    subgraph "Security Oversight"
        ["SECURITY.md"] -- "Redirects to" --> ["NVIDIA PSIRT"]
    end

    ["Contributor"] -- "Fork & Pull Request" --> ["CONTRIBUTING.md"]
    ["NVIDIA Corporation"] -- "Licensor" --> ["LICENSE (Apache 2.0)"]
```
Sources: [LICENSE:1-12](), [CONTRIBUTING.md:5-13](), [SECURITY.md:20-25]()

---

### License and Attribution
The QCalEval codebase is primarily licensed under the **Apache License 2.0**, which governs the evaluation scripts and associated software tools [LICENSE:1-3](). This license allows for broad use, modification, and distribution while providing a grant of patent rights from contributors [LICENSE:66-88]().

In addition to the primary license, the project maintains an `ATTRIBUTIONS` file to acknowledge and comply with the licenses of third-party Python dependencies used in the evaluation pipeline, such as `datasets`, `httpx`, `Pillow`, and `huggingface-hub` [ATTRIBUTIONS:11-100]().

For details on specific license terms and the CC BY 4.0 license covering the benchmark dataset, see **[License and Attribution (#3.1)]**.

**Sources:** [LICENSE:1-201](), [ATTRIBUTIONS:1-119]()

---

### Contributing and Security
We welcome community contributions to improve the evaluation pipeline. To maintain legal integrity, all contributors must adhere to the **Developer Certificate of Origin (DCO)** by signing off on every commit [CONTRIBUTING.md:5-13](). This is typically handled using the `git commit -s` command [CONTRIBUTING.md:53-54]().

Security is a top priority for NVIDIA. We request that potential vulnerabilities **not** be reported via public GitHub issues. Instead, they should be directed to the **NVIDIA Product Security Incident Response Team (PSIRT)** through their secure submission form or encrypted email [SECURITY.md:5-12]().

For a step-by-step guide on the fork-and-pull model and detailed security reporting instructions, see **[Contributing and Security (#3.2)]**.

#### Code-to-Governance Mapping
The following diagram maps specific files in the repository to their respective governance roles.

**Governance Documentation Mapping**
```mermaid
graph LR
    ["Repository Root"] --> ["LICENSE"]
    ["Repository Root"] --> ["CONTRIBUTING.md"]
    ["Repository Root"] --> ["SECURITY.md"]
    ["Repository Root"] --> ["ATTRIBUTIONS"]

    ["LICENSE"] --- ["Software Usage Terms"]
    ["CONTRIBUTING.md"] --- ["DCO & Pull Request Flow"]
    ["SECURITY.md"] --- ["Vulnerability Disclosure"]
    ["ATTRIBUTIONS"] --- ["Third-party Dependency Credits"]
```
Sources: [LICENSE:1-5](), [CONTRIBUTING.md:1-4](), [SECURITY.md:1-3](), [ATTRIBUTIONS:1-10]()

**Sources:** [CONTRIBUTING.md:5-62](), [SECURITY.md:1-25]()

---

