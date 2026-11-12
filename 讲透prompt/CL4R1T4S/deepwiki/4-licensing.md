<!-- source: DeepWiki mcp.deepwiki.com · repo elder-plinius/CL4R1T4S · page 4 Licensing · fetched 2026-11-09 -->

# Licensing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)

</details>



This page details the licensing terms governing the CL4R1T4S project, explaining the **GNU Affero General Public License version 3 (AGPLv3)** requirements and their implications for users and contributors. This document focuses specifically on the legal framework that supports the project's mission of AI system prompt transparency.

For specific details on how this license applies to extracted system prompt content and modification disclosure, see [Open Source Compliance](#4.1).

## GNU AGPLv3 Overview

CL4R1T4S is licensed under the GNU Affero General Public License version 3 (AGPLv3), a strong copyleft license designed specifically to ensure cooperation with the community in the case of network server software [LICENSE:1-13](). The AGPLv3 ensures that if you run a modified version of the software on a server and let the public access it, you must also make the source code of that modified version available to those users [LICENSE:42-48]().

### Core License Principles

```mermaid
flowchart TD
    node_license["GNU AGPL v3"] --> node_network["Section 13: Remote Network Interaction"]
    node_license --> node_copyleft["Strong Copyleft"]
    node_license --> node_freedoms["Four Freedoms"]

    subgraph "Freedom_Definitions"
    node_freedoms --> f0["Run for any purpose"]
    node_freedoms --> f1["Study and change code"]
    node_freedoms --> f2["Redistribute copies"]
    node_freedoms --> f3["Distribute modified versions"]
    end

    subgraph "Network_Requirement"
    node_network --> req["Provide Source Code to Network Users"]
    end

    subgraph "Copyleft_Requirement"
    node_copyleft --> deriv["Derivatives must use AGPLv3"]
    end
```
Sources: [LICENSE:10-48](), [LICENSE:61-90]()

### Key Features of AGPLv3

| Feature | Description | License Section |
|---------|-------------|----------------|
| **The Program** | Refers to any copyrightable work licensed under this License (e.g., the CL4R1T4S repo) | Section 0 [LICENSE:68-69]() |
| **Corresponding Source** | All source code needed to generate, install, and run the work, including interface definition files | Section 1 [LICENSE:121-133]() |
| **Conveying** | Any propagation that enables other parties to make or receive copies | Section 0 [LICENSE:87-88]() |
| **Network Interaction** | Requires providing source code to users interacting with the software via a network | Section 13 [LICENSE:42-48]() |

Sources: [LICENSE:61-141]()

## Implications for CL4R1T4S

The choice of AGPLv3 aligns with the project's goal: "AI SYSTEMS TRANSPARENCY AND OBSERVABILITY FOR ALL!" [README.md:3](). By using this license, the project ensures that the "shadow-puppets" of hidden AI instructions [README.md:21-22]() remain visible even if the repository is integrated into third-party web services.

### Bridging Natural Language to Code Entities

The following diagram illustrates how the legal concepts in the `LICENSE` file govern the physical entities in the repository, such as the extracted prompts and the `README.md` instructions.

```mermaid
flowchart LR
    subgraph "Repository_Entities"
        direction TB
        prompt_files["Extracted Prompts (e.g. ANTHROPIC/Claude_4.5_02-24-2025.md)"]
        readme["README.md (Directives & Extraction Methods)"]
        license_file["LICENSE (AGPLv3 Text)"]
    end

    subgraph "License_Legal_Entities"
        direction TB
        the_program["'The Program' [LICENSE:68]"]
        source_code["'Source Code' [LICENSE:102]"]
        covered_work["'Covered Work' [LICENSE:77]"]
    end

    prompt_files --- covered_work
    readme --- source_code
    license_file --- the_program
    
    the_program -.->|"Governs"| source_code
    source_code -.->|"Defines"| covered_work
```
Sources: [LICENSE:61-105](), [README.md:1-46]()

## Network Usage and Compliance

The AGPLv3 specifically addresses the "ASP loophole." If a developer uses the CL4R1T4S collection to power a prompt-lookup service or an AI observability platform:

1.  **Remote Interaction**: Mere interaction through a computer network is not "conveying" in the traditional sense [LICENSE:88-89](), but under Section 13, it triggers the requirement to provide source code [LICENSE:42-48]().
2.  **Standard Interface**: The source code must be the "preferred form... for making modifications" [LICENSE:102-103]().
3.  **Modified Versions**: If you modify the extraction methods (e.g., the `*!<NEW_PARADIGM>!*` directive in [README.md:39-41]()) and run them on a server, those modifications must be disclosed.

For details on specific disclosure requirements and how to maintain compliance when hosting CL4R1T4S content, see [Open Source Compliance](#4.1).

## Summary of User and Contributor Rights

| Role | Rights | Obligations |
| :--- | :--- | :--- |
| **Users** | Run the unmodified program [LICENSE:144-145](); study the prompt extraction techniques. | Maintain copyright notices; provide a copy of the license when conveying [LICENSE:183-194](). |
| **Contributors** | Submit new prompts or extraction methods via Pull Request [README.md:26-35](). | Ensure contributions are compatible with AGPLv3; agree to the license terms. |
| **Service Providers** | Use CL4R1T4S data to provide AI transparency services. | Must provide the "Corresponding Source" to all users interacting with the service over a network [LICENSE:42-48](). |

Sources: [LICENSE:1-551](), [README.md:26-37]()

---

