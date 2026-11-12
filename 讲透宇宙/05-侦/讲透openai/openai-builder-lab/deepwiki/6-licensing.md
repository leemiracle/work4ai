<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-builder-lab · page 6 Licensing · fetched 2026-10-26 -->

# Licensing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [license.txt](license.txt)

</details>



This document outlines the licensing terms that govern the OpenAI Builder Lab project, including the dual licensing structure that covers both the software components and font assets. Understanding these terms is essential for proper usage, modification, and distribution of the project.

## Overview

The OpenAI Builder Lab project operates under a dual licensing structure that separates software components from font assets. This approach ensures appropriate licensing for different types of intellectual property while maintaining open-source accessibility.

```mermaid
graph TB
    subgraph "OpenAI Builder Lab Project"
        Software["Software Components<br/>MIT License"]
        Fonts["Font Assets<br/>SIL Open Font License"]
    end
    
    subgraph "MIT Licensed Components"
        Frontend["Frontend Application<br/>NextJS + React"]
        Backend["Backend Systems<br/>Flask + NextJS API"]
        Config["Configuration Files<br/>Build Scripts"]
        Docs["Documentation<br/>README + Wiki"]
    end
    
    subgraph "SIL OFL Licensed Assets"
        GeistFont["Geist Font Family<br/>Vercel Copyright"]
        GeistMono["Geist Mono Font<br/>Vercel Copyright"]
    end
    
    Software --> Frontend
    Software --> Backend
    Software --> Config
    Software --> Docs
    
    Fonts --> GeistFont
    Fonts --> GeistMono
```

Sources: [license.txt:1-118]()

## MIT License for Software Components

The primary software components of the OpenAI Builder Lab are licensed under the MIT License, providing broad permissions for use, modification, and distribution.

### License Terms

| Aspect | Permission |
|--------|------------|
| **Use** | Unrestricted commercial and personal use |
| **Modify** | Full modification rights |
| **Distribute** | Redistribution permitted |
| **Sublicense** | Sublicensing allowed |
| **Sell** | Commercial sale permitted |

### Covered Components

The MIT License applies to all software components including:

```mermaid
graph LR
    subgraph "MIT Licensed Codebase"
        FrontendCode["src/ directory<br/>React Components"]
        BackendCode["app.py<br/>Flask Backend"]
        APIRoutes["app/api/<br/>NextJS Routes"]
        ConfigFiles["*.config.*<br/>Build Configuration"]
        PackageFiles["package.json<br/>requirements.txt"]
    end
    
    subgraph "License Requirements"
        CopyrightNotice["Copyright Notice<br/>Must be included"]
        LicenseText["License Text<br/>Must be preserved"]
        NoWarranty["No Warranty<br/>As-is provision"]
    end
    
    FrontendCode --> CopyrightNotice
    BackendCode --> CopyrightNotice
    APIRoutes --> CopyrightNotice
    ConfigFiles --> LicenseText
    PackageFiles --> NoWarranty
```

### Copyright Notice

The copyright holder is OpenAI (2025), and the license requires preservation of the copyright notice and license text in all copies or substantial portions of the software.

Sources: [license.txt:1-20]()

## SIL Open Font License for Typography

The Geist font family used throughout the application is licensed under the SIL Open Font License (OFL) Version 1.1, which has different terms than the MIT License.

### Font License Structure

```mermaid
graph TB
    subgraph "Font Copyright Holders"
        Vercel["Vercel<br/>Primary Copyright Holder"]
        Basement["basement.studio<br/>Collaboration Partner"]
    end
    
    subgraph "Licensed Font Software"
        GeistRegular["Geist Font Family<br/>Regular Weights"]
        GeistMono["Geist Mono<br/>Monospace Variant"]
    end
    
    subgraph "Usage Permissions"
        UseStudy["Use & Study<br/>Unrestricted"]
        Modify["Modify<br/>With Conditions"]
        Redistribute["Redistribute<br/>With License"]
        Embed["Embed in Software<br/>Permitted"]
    end
    
    subgraph "Restrictions"
        NoSellAlone["Cannot Sell Fonts Alone<br/>Must Bundle with Software"]
        ReservedNames["Reserved Font Names<br/>Require Permission"]
        SameLicense["Must Maintain OFL<br/>Cannot Change License"]
    end
    
    Vercel --> GeistRegular
    Basement --> GeistRegular
    Vercel --> GeistMono
    
    GeistRegular --> UseStudy
    GeistMono --> UseStudy
    UseStudy --> Modify
    Modify --> Redistribute
    Redistribute --> Embed
    
    Embed --> NoSellAlone
    NoSellAlone --> ReservedNames
    ReservedNames --> SameLicense
```

### Key OFL Provisions

| Provision | Requirement |
|-----------|-------------|
| **Bundling** | Fonts may be bundled with software but not sold independently |
| **Attribution** | Copyright notice must be preserved |
| **License Continuity** | Derivative fonts must remain under OFL |
| **Reserved Names** | "Geist" name cannot be used for modified versions without permission |
| **No Endorsement** | Copyright holders' names cannot be used for promotion without permission |

Sources: [license.txt:23-116]()

## License Compliance Guidelines

### For Software Distribution

When distributing or modifying the OpenAI Builder Lab software:

1. **Include License Text**: The MIT license text must be included in all distributions
2. **Preserve Copyright**: Maintain the OpenAI copyright notice
3. **No Attribution Requirements**: No specific attribution required beyond copyright notice

### For Font Usage

When using or distributing the Geist fonts:

1. **Bundle Requirement**: Fonts cannot be distributed separately from software
2. **License Inclusion**: SIL OFL license text must be included
3. **Name Restrictions**: Cannot use "Geist" name for modified versions
4. **Copyright Preservation**: Vercel copyright notice must be maintained

### Integration Considerations

```mermaid
graph LR
    subgraph "Distribution Package"
        SoftwareBundle["Complete Application<br/>MIT + OFL Licensed"]
        LicenseFile["license.txt<br/>Combined License Text"]
    end
    
    subgraph "Compliance Requirements"
        MITCompliance["MIT Requirements<br/>Copyright + License Text"]
        OFLCompliance["OFL Requirements<br/>Font Bundling + Attribution"]
    end
    
    subgraph "Usage Scenarios"
        DirectUse["Direct Usage<br/>Full Compliance"]
        Modification["Code Modification<br/>MIT Permissions"]
        FontMod["Font Modification<br/>OFL Restrictions"]
    end
    
    SoftwareBundle --> LicenseFile
    LicenseFile --> MITCompliance
    LicenseFile --> OFLCompliance
    
    MITCompliance --> DirectUse
    MITCompliance --> Modification
    OFLCompliance --> DirectUse
    OFLCompliance --> FontMod
```

Sources: [license.txt:1-118]()

## License File Location

The complete licensing information is maintained in [license.txt:1-118](), which contains both the MIT License for software components and the full SIL Open Font License text for the Geist font family. This file serves as the authoritative source for all licensing terms and must be preserved in any distribution of the project.

Sources: [license.txt:1-118]()