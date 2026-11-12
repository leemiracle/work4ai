<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/discoveryworld · page 9 Legal & Licensing · fetched 2026-10-26 -->

# Legal & Licensing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE.txt](LICENSE.txt)

</details>



This document covers the legal framework governing the use, modification, and distribution of the DiscoveryWorld codebase. It explains the Apache 2.0 license terms, usage rights, contribution requirements, and practical guidelines for researchers and developers working with the platform.

For information about package distribution and asset management, see [Asset Management & Distribution](#7). For development environment setup and contribution workflows, see [Development Environment](#8.2).

## License Overview

DiscoveryWorld is distributed under the Apache License Version 2.0, a permissive open-source license that allows broad usage while maintaining certain requirements for attribution and redistribution.

### Apache 2.0 License Summary

| Permission | Requirement | Limitation |
|------------|-------------|------------|
| Commercial use | License and copyright notice | Liability |
| Modification | State changes | Warranty |
| Distribution | Include license text | Trademark use |
| Patent use | Preserve attribution | - |
| Private use | - | - |

The full license text is available in [LICENSE.txt:1-202]().

**Sources:** [LICENSE.txt:1-202]()

## Usage Rights and Permissions

### Permitted Activities

The Apache 2.0 license grants users extensive rights to work with the DiscoveryWorld codebase:

```mermaid
graph TD
    subgraph "Apache 2.0 Permissions"
        USE["Commercial Use<br/>Research & Development"]
        MODIFY["Modification<br/>Code Changes & Extensions"]
        DISTRIBUTE["Distribution<br/>Sharing Modified Versions"]
        PATENT["Patent Use<br/>Contributor Patent Rights"]
        PRIVATE["Private Use<br/>Internal Development"]
    end
    
    subgraph "DiscoveryWorld Applications"
        RESEARCH["Academic Research<br/>Agent Development"]
        COMMERCIAL["Commercial Products<br/>AI Evaluation Services"]
        DERIVATIVE["Derivative Works<br/>Custom Environments"]
        INTEGRATION["System Integration<br/>Platform Extensions"]
    end
    
    USE --> RESEARCH
    USE --> COMMERCIAL
    MODIFY --> DERIVATIVE
    MODIFY --> INTEGRATION
    DISTRIBUTE --> COMMERCIAL
    DISTRIBUTE --> RESEARCH
    PATENT --> INTEGRATION
    PRIVATE --> RESEARCH
```

**Key Rights Granted:**

1. **Copyright License** [LICENSE.txt:66-72](): Perpetual, worldwide, non-exclusive rights to reproduce, modify, display, perform, sublicense, and distribute
2. **Patent License** [LICENSE.txt:73-87](): Protection against patent claims from contributors
3. **Modification Rights** [LICENSE.txt:40-46](): Freedom to create derivative works
4. **Commercial Use** [LICENSE.txt:89-129](): No restrictions on commercial applications

**Sources:** [LICENSE.txt:66-87](), [LICENSE.txt:89-129]()

## Distribution Requirements

### Mandatory Inclusions

When redistributing DiscoveryWorld or derivative works, specific requirements must be met:

```mermaid
graph LR
    subgraph "Source Distribution"
        SOURCE_CODE["Source Code Files"]
        LICENSE_COPY["LICENSE.txt Copy"]
        COPYRIGHT_NOTICES["Copyright Notices"]
        CHANGE_NOTICES["Modification Notices"]
    end
    
    subgraph "Binary Distribution"
        COMPILED_CODE["Compiled/Packaged Code"]
        LICENSE_INCLUSION["License Text Inclusion"]
        ATTRIBUTION["Attribution Notices"]
        NOTICE_FILE["NOTICE File (if present)"]
    end
    
    subgraph "Requirements"
        PRESERVE_ATTR["Preserve Attribution"]
        MARK_CHANGES["Mark Changes"]
        INCLUDE_LICENSE["Include License"]
        RETAIN_NOTICES["Retain Notices"]
    end
    
    SOURCE_CODE --> PRESERVE_ATTR
    LICENSE_COPY --> INCLUDE_LICENSE
    COPYRIGHT_NOTICES --> RETAIN_NOTICES
    CHANGE_NOTICES --> MARK_CHANGES
    
    COMPILED_CODE --> PRESERVE_ATTR
    LICENSE_INCLUSION --> INCLUDE_LICENSE
    ATTRIBUTION --> RETAIN_NOTICES
    NOTICE_FILE --> RETAIN_NOTICES
```

**Distribution Checklist:**

1. **License Inclusion** [LICENSE.txt:94-95](): Include a copy of the Apache 2.0 license
2. **Change Notification** [LICENSE.txt:97-98](): Mark modified files with prominent notices
3. **Attribution Preservation** [LICENSE.txt:100-104](): Retain copyright, patent, trademark, and attribution notices
4. **NOTICE File Handling** [LICENSE.txt:106-121](): Include NOTICE file contents if present

**Sources:** [LICENSE.txt:89-129]()

## Contribution Terms

### Contributor License Agreement

The Apache 2.0 license includes an implicit contributor license agreement for all submissions:

```mermaid
graph TD
    subgraph "Contribution Process"
        CONTRIBUTOR["Contributor<br/>(Individual or Legal Entity)"]
        SUBMISSION["Code Submission<br/>Pull Request/Patch"]
        REVIEW["Review Process<br/>Maintainer Evaluation"]
        INTEGRATION["Code Integration<br/>Merge to Main Branch"]
    end
    
    subgraph "License Terms"
        COPYRIGHT_GRANT["Copyright Grant<br/>Same License Terms"]
        PATENT_GRANT["Patent Grant<br/>Defensive Patent Pool"]
        NO_ADDITIONAL["No Additional Terms<br/>Standard Apache 2.0"]
        EXPLICIT_OVERRIDE["Explicit Agreement Override<br/>Separate Licensing"]
    end
    
    CONTRIBUTOR --> SUBMISSION
    SUBMISSION --> REVIEW
    REVIEW --> INTEGRATION
    
    SUBMISSION --> COPYRIGHT_GRANT
    SUBMISSION --> PATENT_GRANT
    SUBMISSION --> NO_ADDITIONAL
    
    COPYRIGHT_GRANT -.-> EXPLICIT_OVERRIDE
    PATENT_GRANT -.-> EXPLICIT_OVERRIDE
```

**Key Contribution Terms:**

1. **Automatic Licensing** [LICENSE.txt:130-133](): Contributions automatically licensed under Apache 2.0
2. **Patent Grant** [LICENSE.txt:73-87](): Contributors grant patent rights for their submissions
3. **No Additional Terms** [LICENSE.txt:130-136](): Standard Apache 2.0 applies unless explicitly stated otherwise
4. **Separate Agreements** [LICENSE.txt:134-136](): Existing separate license agreements take precedence

**Sources:** [LICENSE.txt:130-136](), [LICENSE.txt:73-87]()

## Warranty and Liability

### Disclaimer of Warranty

The Apache 2.0 license includes comprehensive warranty disclaimers that apply to all DiscoveryWorld usage:

| Aspect | Disclaimer |
|--------|------------|
| Warranty | No express or implied warranties |
| Fitness | No guarantee of fitness for particular purpose |
| Non-infringement | No guarantee against IP infringement |
| Merchantability | No guarantee of commercial viability |
| Title | No guarantee of clear title |

### Limitation of Liability

**Liability Protections** [LICENSE.txt:153-163]():
- No liability for direct, indirect, special, incidental, or consequential damages
- Protection covers loss of goodwill, work stoppage, computer failure, and commercial losses
- Applies to all contributors and licensors
- Protection maintained even with advance notice of potential damages

**Additional Liability** [LICENSE.txt:165-174](): Users may voluntarily accept additional warranty or liability obligations when redistributing, but only on their own behalf.

**Sources:** [LICENSE.txt:143-151](), [LICENSE.txt:153-163](), [LICENSE.txt:165-174]()

## Trademark and Attribution

### Trademark Restrictions

The license specifically limits trademark usage [LICENSE.txt:138-141]():

```mermaid
graph LR
    subgraph "Permitted Trademark Use"
        ORIGIN["Describing Work Origin<br/>Source Attribution"]
        NOTICE["NOTICE File Content<br/>Required Attribution"]
        REASONABLE["Reasonable and Customary Use<br/>Academic Citation"]
    end
    
    subgraph "Prohibited Trademark Use"
        TRADE_NAMES["Trade Names<br/>Business Identity"]
        TRADEMARKS["Trademarks<br/>Brand Marks"]
        SERVICE_MARKS["Service Marks<br/>Service Branding"]
        PRODUCT_NAMES["Product Names<br/>Commercial Naming"]
    end
    
    subgraph "DiscoveryWorld Context"
        ATTRIBUTION["DiscoveryWorld Attribution<br/>Academic Papers"]
        FORBIDDEN["DiscoveryWorld Branding<br/>Commercial Products"]
    end
    
    ORIGIN --> ATTRIBUTION
    TRADE_NAMES --> FORBIDDEN
    TRADEMARKS --> FORBIDDEN
    PRODUCT_NAMES --> FORBIDDEN
```

**Trademark Guidelines:**
- Use "DiscoveryWorld" for attribution and academic citation
- Avoid using "DiscoveryWorld" as part of product or service names
- Include proper attribution in research publications
- Reference the original work appropriately in derivative projects

**Sources:** [LICENSE.txt:138-141]()

## Practical Usage Guidelines

### Common Scenarios

| Use Case | Requirements | Recommendations |
|----------|-------------|-----------------|
| Academic Research | Include license in publications | Cite original paper and repository |
| Commercial Product | Include license, mark changes | Provide clear attribution |
| Modified Distribution | License copy, change notices | Document modifications clearly |
| Integration Project | Preserve attributions | Maintain separate license files |

### Best Practices

1. **License File Management**: Always include [LICENSE.txt]() in distributions
2. **Change Documentation**: Clearly mark and document any modifications to source files
3. **Attribution Practices**: Maintain copyright notices and attribution information
4. **Contribution Workflow**: Ensure all contributors understand the Apache 2.0 terms

**Sources:** [LICENSE.txt:1-202]()