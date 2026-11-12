<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/LEMA · page 6 Project Governance and Contributing · fetched 2026-10-26 -->

# Project Governance and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [LICENSE](LICENSE)
- [NOTICE.md](NOTICE.md)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)

</details>



This page provides the administrative and policy framework for the LEMA (Learning From Mistakes) project. It outlines the legal requirements for using and contributing to the codebase, the expected standards of conduct within the community, and the formal procedures for reporting security vulnerabilities or seeking technical support.

As an open-source project managed by Microsoft, LEMA adheres to standardized corporate policies regarding intellectual property and community interaction.

## Legal and Ethical Framework

The LEMA project is released under the **MIT License**, granting broad permissions for use, modification, and distribution provided that the copyright notice is preserved [LICENSE:1-21](). Contributors must also adhere to the **Microsoft Open Source Code of Conduct**, which establishes expectations for a welcoming and respectful environment [CODE_OF_CONDUCT.md:1-10]().

Because LEMA integrates external research artifacts—specifically the QLoRA training implementation and benchmark datasets like GSM8K and MATH—users must also comply with the attributions and third-party licenses documented in the project's notice file [NOTICE.md:1-87]().

For detailed information on these topics, see **[License, Notice, and Code of Conduct](#6.1)**.

### Governance Entity Relationships

The following diagram illustrates how various administrative documents govern the repository entities.

**Administrative Policy Mapping**
```mermaid
graph TD
    subgraph "Legal_Space [Legal & Policy Space]"
        direction TB
        "MIT_License [MIT License]"
        "CoC [Code of Conduct]"
        "Notice_File [NOTICE.md]"
    end

    subgraph "Code_Entity_Space [Project Assets]"
        direction TB
        "Core_Logic [LEMA Source Code]"
        "Third_Party [External Components]"
        "Contrib [Contributors]"
    end

    "MIT_License" -- "governs" --> "Core_Logic"
    "Notice_File" -- "attributes" --> "Third_Party"
    "CoC" -- "regulates" --> "Contrib"

    style "Core_Logic" stroke-dasharray: 5 5
```
**Sources:** [LICENSE:1-21](), [CODE_OF_CONDUCT.md:1-10](), [NOTICE.md:1-8]()

## Security and Support

Microsoft maintains a strict policy for handling security concerns. Vulnerabilities must never be reported via public GitHub issues. Instead, they should be routed through the **Microsoft Security Response Center (MSRC)** [SECURITY.md:11-13](). This ensures that potential exploits are triaged and mitigated in a coordinated fashion [SECURITY.md:39-41]().

For non-security related issues, such as bug reports or feature requests, the project utilizes standard GitHub Issues [SUPPORT.md:3-7](). General technical questions regarding the LEMA methodology or execution can be directed to the project maintainers via the provided support email [SUPPORT.md:9-9]().

For detailed reporting instructions and contact addresses, see **[Security Policy and Support Channels](#6.2)**.

### Support and Reporting Workflow

The following diagram maps the communication channels to the specific types of project feedback.

**Communication Channel Logic**
```mermaid
graph TD
    "User_Input [User Observation]" --> "Is_Security [Is it a Security Bug?]"
    
    "Is_Security" -- "Yes" --> "MSRC_Portal [MSRC Reporting Portal]"
    "Is_Security" -- "No" --> "Issue_Type [Feedback Type]"
    
    "Issue_Type" -- "Bug/Feature" --> "GH_Issues [GitHub Issues]"
    "Issue_Type" -- "Usage Question" --> "Email_Support [Direct Email Contact]"

    subgraph "Code_Reference [Codebase Context]"
        "MSRC_Portal" -.-> "SECURITY.md"
        "GH_Issues" -.-> "SUPPORT.md"
        "Email_Support" -.-> "an1006634493@stu.xjtu.edu.cn"
    end
```
**Sources:** [SECURITY.md:9-17](), [SUPPORT.md:3-9]()

## Summary of Child Pages

*   **[License, Notice, and Code of Conduct](#6.1)**: Detailed breakdown of the MIT license, required notices for third-party code (QLoRA) and data (GSM8K/MATH), and the Microsoft Code of Conduct.
*   **[Security Policy and Support Channels](#6.2)**: Comprehensive instructions for the Coordinated Vulnerability Disclosure process and contact information for project-specific support.

---

