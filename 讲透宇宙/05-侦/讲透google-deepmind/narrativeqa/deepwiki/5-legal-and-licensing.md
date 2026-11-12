<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/narrativeqa · page 5 Legal and Licensing · fetched 2026-10-26 -->

# Legal and Licensing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [third_party/wikipedia/LICENSE](third_party/wikipedia/LICENSE)

</details>



This document provides comprehensive coverage of all licensing requirements and legal obligations for using the NarrativeQA dataset. The dataset employs a dual licensing structure with different terms governing different components of the system.

For technical documentation on the dataset components themselves, see [Dataset Reference](#3). For information about Wikipedia content structure and processing, see [Wikipedia Summaries (summaries.csv)](#3.3).

## Licensing Overview

The NarrativeQA dataset operates under a dual licensing framework that reflects the diverse origins of its content. The repository uses two distinct licenses to govern different portions of the dataset:

```mermaid
graph TB
    subgraph "Apache_2.0_Licensed_Content"
        A["LICENSE"]
        B["documents.csv"]
        C["qaps.csv"] 
        D["download_stories.sh"]
        E["compare.sh"]
        F["README.md"]
    end
    
    subgraph "CC_BY_SA_3.0_Licensed_Content"
        G["third_party/wikipedia/LICENSE"]
        H["third_party/wikipedia/summaries.csv"]
        I["third_party/wikipedia/ATTRIBUTION"]
    end
    
    subgraph "External_Content"
        J["External Story Sources"]
        K["Project Gutenberg"]
        L["Other Story Repositories"]
    end
    
    A -->|"governs"| B
    A -->|"governs"| C
    A -->|"governs"| D
    A -->|"governs"| E
    A -->|"governs"| F
    
    G -->|"governs"| H
    I -->|"attribution_requirements"| H
    
    B -->|"references_via_story_url"| J
    J -->|"individual_licensing"| K
    J -->|"individual_licensing"| L
    
    style A fill:#e1f5fe,stroke:#1976d2,stroke-width:2px
    style G fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

**Dual Licensing Structure**
Sources: [LICENSE:1-203](), [third_party/wikipedia/LICENSE:1-362]()

This licensing architecture ensures compliance with the legal requirements of both the primary dataset infrastructure and the Wikipedia-derived content that forms a crucial component of the reading comprehension challenge.

## Legal Compliance Requirements

The dual licensing structure creates specific obligations depending on how you use the dataset:

| Usage Type | Apache 2.0 Requirements | CC BY-SA 3.0 Requirements |
|------------|-------------------------|---------------------------|
| **Dataset Infrastructure** | Attribution to original authors | Not applicable |
| **Wikipedia Summaries** | Attribution to original authors | Attribution + ShareAlike |
| **Derivative Works** | Include license copy | Must use compatible license |
| **Distribution** | Include license notice | Include attribution + license |

### Attribution Flow Requirements

```mermaid
flowchart TD
    A["User_Downloads_Dataset"] --> B["documents.csv"]
    A --> C["qaps.csv"] 
    A --> D["summaries.csv"]
    
    B -->|"Apache_2.0"| E["Include_LICENSE_Copy"]
    C -->|"Apache_2.0"| E
    
    D -->|"CC_BY_SA_3.0"| F["Include_Wikipedia_LICENSE"]
    D -->|"CC_BY_SA_3.0"| G["Include_ATTRIBUTION_File"]
    D -->|"CC_BY_SA_3.0"| H["ShareAlike_Requirement"]
    
    E --> I["Research_Publication"]
    F --> I
    G --> I
    H --> J["Derivative_Dataset"]
    
    I -->|"citation_required"| K["Cite_Original_Paper"]
    J -->|"must_use_compatible_license"| L["CC_BY_SA_3.0_or_Compatible"]
    
    style D fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style H fill:#ffebee,stroke:#c62828,stroke-width:2px
```

**Attribution and ShareAlike Requirements**
Sources: [third_party/wikipedia/LICENSE:217-247](), [third_party/wikipedia/LICENSE:189-216]()

### License Compatibility Matrix

When creating derivative works or combining the dataset with other resources, license compatibility becomes critical:

```mermaid
graph LR
    subgraph "NarrativeQA_Components"
        A["Apache_2.0_Content"]
        B["CC_BY_SA_3.0_Content"]
    end
    
    subgraph "Compatible_Licenses"
        C["Apache_2.0"]
        D["MIT_License"]
        E["CC_BY_SA_3.0"]
        F["CC_BY_SA_4.0"]
        G["GPL_v3_Plus"]
    end
    
    subgraph "Incompatible_Licenses"
        H["GPL_v2"]
        I["Proprietary_License"]
        J["CC_BY_NC"]
    end
    
    A -->|"compatible_with"| C
    A -->|"compatible_with"| D
    A -->|"compatible_with"| E
    
    B -->|"compatible_with"| E
    B -->|"compatible_with"| F
    B -->|"compatible_with"| G
    
    B -.->|"incompatible_with"| H
    B -.->|"incompatible_with"| I
    B -.->|"incompatible_with"| J
    
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style H fill:#ffebee,stroke:#c62828,stroke-width:1px
    style I fill:#ffebee,stroke:#c62828,stroke-width:1px
    style J fill:#ffebee,stroke:#c62828,stroke-width:1px
```

**License Compatibility for Derivative Works**
Sources: [third_party/wikipedia/LICENSE:52-60](), [third_party/wikipedia/LICENSE:189-216]()

## Practical Usage Guidelines

### Research and Academic Use

For academic research and publication:

1. **Citation Requirements**: Include appropriate citations to the original NarrativeQA paper
2. **License Acknowledgment**: Acknowledge both Apache 2.0 and CC BY-SA 3.0 licenses
3. **Attribution**: Provide proper attribution for Wikipedia-derived content per [third_party/wikipedia/ATTRIBUTION]()

### Commercial Use

Commercial applications must comply with both license terms:

- **Apache 2.0 Content**: Permits commercial use with attribution
- **Wikipedia Content**: Requires ShareAlike licensing for any derivatives of `summaries.csv`

### Distribution Requirements

When redistributing any portion of the dataset:

| Component | Required Files | Attribution Method |
|-----------|---------------|-------------------|
| **Core Dataset** | `LICENSE` copy | Include in distribution root |
| **Wikipedia Summaries** | `third_party/wikipedia/LICENSE`, `third_party/wikipedia/ATTRIBUTION` | Include in distribution |
| **Combined Distribution** | Both license files | Clearly identify which content uses which license |

Sources: [LICENSE:90-122](), [third_party/wikipedia/LICENSE:167-188](), [third_party/wikipedia/LICENSE:217-247]()

## External Content Considerations

The dataset references external story content through URLs in `documents.csv`. These external sources maintain their own licensing terms:

- **Project Gutenberg**: Public domain or specific license terms
- **Other Repositories**: Individual licensing requirements
- **User Responsibility**: Verify licensing for downloaded content

Users must independently verify the licensing status of any external content accessed through the `story_url` fields in [documents.csv]().

Sources: [documents.csv (story_url field)]()

---

