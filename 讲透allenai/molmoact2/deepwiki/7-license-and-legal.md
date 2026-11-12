<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/molmoact2 · page 7 License and Legal · fetched 2026-10-26 -->

# License and Legal

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This page provides an overview of the legal framework and ethical guidelines governing the MolmoAct2 repository and its associated models. The project is released under an open-source license to facilitate research and real-world deployment in the robotics community.

### Legal and Ethical Framework Overview

The MolmoAct2 project is governed by two primary pillars:
1.  **The Apache License 2.0**: A permissive free software license that defines how the code and documentation can be used, modified, and redistributed [LICENSE:1-201]().
2.  **Responsible Use Guidelines**: Ai2's framework for ensuring that these embodied reasoning models are deployed safely and ethically in research and educational contexts [README.md:121-125]().

The following diagram illustrates the relationship between the legal entities, the software "Work," and the user.

**Legal Entity and Work Relationship**
```mermaid
graph TD
    subgraph "Legal_Framework"
        "Licensor[Ai2]" -- "Grants_Permissions" --> "License[Apache_2.0]"
        "License[Apache_2.0]" -- "Governs" --> "Work[MolmoAct2_Repo]"
    end

    subgraph "Code_Entity_Space"
        "Work[MolmoAct2_Repo]" --> "Source_Form[Python_Code/Docs]"
        "Work[MolmoAct2_Repo]" --> "Object_Form[Compiled_Assets]"
        "Work[MolmoAct2_Repo]" --> "Submodule[lerobot]"
    end

    "You[User/Entity]" -- "Exercises_Rights" --> "License[Apache_2_0]"
    "You[User/Entity]" -- "Must_Comply" --> "Responsible_Use_Guidelines"
```
Sources: [LICENSE:7-47](), [README.md:79-82]()

---

## Apache 2.0 License Terms

The MolmoAct2 repository is distributed under the **Apache License, Version 2.0**. This license allows for significant freedom in using the software for both commercial and non-commercial purposes, provided that certain conditions regarding attribution and liability are met.

Key components of the license include:
*   **Grant of Copyright**: A perpetual, worldwide, non-exclusive license to reproduce and distribute the work [LICENSE:66-72]().
*   **Patent Grant**: A license to use patent claims necessarily infringed by the contribution [LICENSE:73-81]().
*   **Redistribution**: Requirements for providing a copy of the license and prominent notices of any modifications [LICENSE:89-129]().
*   **Disclaimer of Warranty**: The work is provided "AS IS" without warranties of any kind [LICENSE:166-177]().

For a detailed breakdown of these terms and how they apply to derivative works, see [Apache 2.0 License Terms](#7.1).

Sources: [LICENSE:1-201]()

---

## Responsible Use and Citation

Beyond the legal requirements of the Apache 2.0 license, Ai2 provides **Responsible Use Guidelines** to ensure the safe deployment of MolmoAct2. These guidelines are particularly relevant for embodied AI, where model outputs result in physical actions.

The project is intended for research and educational purposes. Users are encouraged to validate model behavior in simulation before moving to physical hardware [README.md:121-125](). Furthermore, formal academic use of the model, architecture, or datasets should cite the corresponding research paper [README.md:127-135]().

**Citation and Usage Mapping**
```mermaid
graph LR
    subgraph "Natural_Language_Space"
        "Research_Paper"
        "Safety_Protocols"
    end

    subgraph "Code_Entity_Space"
        "arXiv:2605.02881" -- "Describes" --> "MolmoAct2_Architecture"
        "README.md" -- "Defines" --> "Responsible_Use_Guidelines"
        "LICENSE" -- "Defines" --> "Legal_Obligations"
    end

    "User" -- "Cites" --> "arXiv:2605.02881"
    "User" -- "Follows" --> "Safety_Protocols"
```
Sources: [README.md:15-17](), [README.md:121-135]()

For details on citation formats, intended use cases, and contact information for collaborations, see [Responsible Use and Citation](#7.2).

Sources: [README.md:121-135]()

---

