<!-- source: DeepWiki mcp.deepwiki.com · repo openai/skills · page 9 Licensing · fetched 2026-10-30 -->

# Licensing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [skills/.curated/figma-code-connect-components/LICENSE.TXT](skills/.curated/figma-code-connect-components/LICENSE.TXT)
- [skills/.curated/figma-create-design-system-rules/LICENSE.TXT](skills/.curated/figma-create-design-system-rules/LICENSE.TXT)
- [skills/.curated/figma-create-new-file/LICENSE.TXT](skills/.curated/figma-create-new-file/LICENSE.TXT)
- [skills/.curated/figma-generate-design/LICENSE.TXT](skills/.curated/figma-generate-design/LICENSE.TXT)
- [skills/.curated/figma-generate-library/LICENSE.TXT](skills/.curated/figma-generate-library/LICENSE.TXT)
- [skills/.curated/figma-implement-design/LICENSE.txt](skills/.curated/figma-implement-design/LICENSE.txt)
- [skills/.curated/figma-use/LICENSE.TXT](skills/.curated/figma-use/LICENSE.TXT)
- [skills/.curated/figma/LICENSE.txt](skills/.curated/figma/LICENSE.txt)

</details>



This page documents the licensing terms that apply to skills in the `openai/skills` repository. It covers the open source licenses used, the specific terms for individual integrations, and what rights and obligations apply to users and contributors.

---

## Overview

All skills in the `openai/skills` repository are distributed under permissive licenses that allow for modular use. The primary license used for the repository's infrastructure and core system skills is the **Apache License 2.0**.

As noted in the root documentation, the license for an individual skill is contained directly within the skill's directory inside a `LICENSE.txt` file [README.md:38-41](). This modular approach ensures that each skill carries its own legal permissions and attributions, which is particularly important for skills that integrate with third-party platforms like Figma.

**Sources:** [README.md:38-41]()

---

## License Distribution by Skill Category

Each skill includes its own `LICENSE.txt` file. While many follow the standard Apache 2.0 format, certain curated skills—specifically those interacting with proprietary design tools—are governed by platform-specific developer terms.

Title: Repository Licensing Structure
```mermaid
graph TB
    subgraph "Repository_Structure"
        ["ROOT [/]"]
        ["SYSTEM [skills/.system/]"]
        ["CURATED [skills/.curated/]"]
    end
    
    subgraph "System_Tier_License"
        ["SC [skill-creator/]"]
        ["SC_LIC [LICENSE.txt (Apache 2.0)]"]
    end
    
    subgraph "Figma_Curated_License"
        ["FIGMA_BASE [figma/]"]
        ["FIGMA_GEN [figma-generate-library/]"]
        ["FIGMA_LIC [LICENSE.txt (Figma Developer Terms)]"]
    end
    
    subgraph "Standard_Curated_License"
        ["GH_FIX [gh-fix-ci/]"]
        ["GH_LIC [LICENSE.txt (Apache 2.0)]"]
    end
    
    ["ROOT [/]"] --> ["SYSTEM [skills/.system/]"]
    ["ROOT [/]"] --> ["CURATED [skills/.curated/]"]
    
    ["SYSTEM [skills/.system/]"] --> ["SC [skill-creator/]"]
    ["SC [skill-creator/]"] --> ["SC_LIC [LICENSE.txt (Apache 2.0)]"]
    
    ["CURATED [skills/.curated/]"] --> ["FIGMA_BASE [figma/]"]
    ["CURATED [skills/.curated/]"] --> ["FIGMA_GEN [figma-generate-library/]"]
    ["CURATED [skills/.curated/]"] --> ["GH_FIX [gh-fix-ci/]"]
    
    ["FIGMA_BASE [figma/]"] --> ["FIGMA_LIC [LICENSE.txt (Figma Developer Terms)]"]
    ["FIGMA_GEN [figma-generate-library/]"] --> ["FIGMA_LIC [LICENSE.txt (Figma Developer Terms)]"]
    ["GH_FIX [gh-fix-ci/]"] --> ["GH_LIC [LICENSE.txt (Apache 2.0)]"]
```

**Sources:** [README.md:12-34](), [skills/.curated/figma/LICENSE.txt:1-2]()

---

## Apache License 2.0

The Apache License 2.0 is the standard license for core system skills and general-purpose curated skills. It provides explicit grants of both copyright and patent rights.

### Key Permissions and Requirements

| Category | Item | Description |
|:---|:---|:---|
| **Permissions** | Commercial Use | Skills may be used in commercial products and services |
| | Modification | Skills may be modified and adapted for specific use cases |
| | Distribution | Skills may be redistributed in original or modified form |
| **Requirements** | License Inclusion | Must include a copy of the Apache 2.0 license |
| | State Changes | Modified files must carry prominent notices stating changes |
| | Attribution | Must retain copyright, patent, trademark, and attribution notices |

**Sources:** [README.md:38-41]()

---

## Figma Developer Terms

Skills within the Figma integration suite are governed by the **Figma Developer Terms** rather than the standard Apache license. This applies to the following skills:

*   `figma` [skills/.curated/figma/LICENSE.txt:1-2]()
*   `figma-implement-design` [skills/.curated/figma-implement-design/LICENSE.txt:1-2]()
*   `figma-generate-design` [skills/.curated/figma-generate-design/LICENSE.TXT:1-2]()
*   `figma-use` [skills/.curated/figma-use/LICENSE.TXT:1-2]()
*   `figma-create-new-file` [skills/.curated/figma-create-new-file/LICENSE.TXT:1-2]()
*   `figma-code-connect-components` [skills/.curated/figma-code-connect-components/LICENSE.TXT:1-2]()
*   `figma-create-design-system-rules` [skills/.curated/figma-create-design-system-rules/LICENSE.TXT:1-2]()
*   `figma-generate-library` [skills/.curated/figma-generate-library/LICENSE.TXT:1-2]()

### Key Provisions
1.  **Governing Terms:** Use of these Materials is governed by the Figma Developer Terms (available at `https://www.figma.com/legal/developer-terms/`) [skills/.curated/figma/LICENSE.txt:1]().
2.  **Automated Use:** By accessing these materials through automated systems or AI agents, you agree to these terms [skills/.curated/figma/LICENSE.txt:1]().
3.  **Beta Status:** These materials are offered as a Beta feature and may be modified or discontinued at any time [skills/.curated/figma/LICENSE.txt:2]().

**Sources:** [skills/.curated/figma/LICENSE.txt:1-2](), [skills/.curated/figma-generate-library/LICENSE.TXT:1-2]()

---

## Natural Language Space to Code Entity Space

The following diagrams bridge the high-level licensing concepts to the specific files and locations within the repository.

Title: License File Discovery and Mapping
```mermaid
graph LR
    subgraph "Natural Language Concepts"
        ["GLOBAL_LIC [Global License Policy]"]
        ["SKILL_LIC [Skill-Specific Terms]"]
        ["PLATFORM_TERMS [Third-Party Terms]"]
    end

    subgraph "Code Entity Space"
        ["README [README.md]"]
        ["SKILL_DIR [skills/.curated/{skill_name}/]"]
        ["LICENSE_FILE [LICENSE.txt]"]
    end

    ["GLOBAL_LIC [Global License Policy]"] -->|"Documented in"| ["README [README.md]"]
    ["SKILL_LIC [Skill-Specific Terms]"] -->|"Located in"| ["LICENSE_FILE [LICENSE.txt]"]
    ["LICENSE_FILE [LICENSE.txt]"] -->|"Resides inside"| ["SKILL_DIR [skills/.curated/{skill_name}/]"]
    ["PLATFORM_TERMS [Third-Party Terms]"] -->|"Defined in"| ["LICENSE_FILE [LICENSE.txt]"]
```

Title: Licensing Verification Logic
```mermaid
graph TD
    subgraph "User Workflow"
        ["INSTALL [$skill-installer install]"]
    end

    subgraph "System Logic"
        ["CHECK_DIR [Check skill directory]"]
        ["FIND_LIC [Find LICENSE.txt]"]
        ["DISPLAY_TERMS [Display/Accept Terms]"]
    end

    ["INSTALL [$skill-installer install]"] --> ["CHECK_DIR [Check skill directory]"]
    ["CHECK_DIR [Check skill directory]"] --> ["FIND_LIC [Find LICENSE.txt]"]
    ["FIND_LIC [Find LICENSE.txt]"] --> ["DISPLAY_TERMS [Display/Accept Terms]"]
```

**Sources:** [README.md:12-41](), [skills/.curated/figma/LICENSE.txt:1-2]()

---

## Warranty and Liability Disclaimers

Standard across all skills in this repository is the provision that they are provided "AS IS" without any warranties.

### Warranty Disclaimer
Contributors provide the Work on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE.

### Liability Limitation
In no event and under no legal theory shall any Contributor be liable for damages, including any direct, indirect, special, incidental, or consequential damages of any character arising as a result of the use or inability to use the Work.

**Sources:** [skills/.curated/figma/LICENSE.txt:1-2]()

---

