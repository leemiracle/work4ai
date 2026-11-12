<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Fabric-Manager-Client · page 5 License and Legal · fetched 2026-11-11 -->

# License and Legal

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)

</details>



## Purpose and Scope

This page provides an overview of the legal framework governing the use of the NVIDIA Fabric Manager Client (fmpm) software. The software is distributed under the NVIDIA Software License Agreement, which imposes specific terms, restrictions, and obligations on users. This document summarizes the key legal considerations, compliance requirements, and how the license terms relate to the software architecture and usage.

For detailed information on specific aspects of the license:
- For complete license terms and grant of rights, see [Software License Agreement](#5.1)
- For platform requirements and prohibited actions, see [Usage Restrictions and Requirements](#5.2)
- For warranty disclaimers and liability limitations, see [Disclaimers and Liability](#5.3)
- For intellectual property and feedback provisions, see [Intellectual Property and Feedback](#5.4)
- For arbitration and legal proceedings, see [Dispute Resolution](#5.5)

**Sources:** [LICENSE:1-408]()

---

## License Applicability

The NVIDIA Software License Agreement governs all aspects of the Fabric Manager Client software, including source code, compiled binaries, documentation, and usage. The license establishes a binding legal agreement between the user and NVIDIA Corporation that must be accepted before using the software.

### License Hierarchy

```mermaid
graph TB
    subgraph "Legal Framework"
        License["LICENSE<br/>NVIDIA Software License Agreement<br/>v. November 23, 2023"]
        Terms["License Terms<br/>Sections 1-20"]
        Acceptance["Acceptance Required<br/>Before Use"]
    end
    
    subgraph "Source Code Distribution"
        SourceRepo["GitHub Repository<br/>NVIDIA/Fabric-Manager-Client"]
        SourceFile["fmpm.cpp<br/>Source Code"]
        Makefile["Makefile<br/>Build System"]
        LicenseFile["LICENSE File<br/>Root Directory"]
    end
    
    subgraph "Compiled Software"
        Binary["fmpm<br/>Compiled Executable"]
        Dependencies["Dependencies<br/>libnvfm, libjsoncpp"]
    end
    
    subgraph "Runtime Components"
        FMService["Fabric Manager Service<br/>nvidia-fabricmanager"]
        Hardware["NVIDIA Platform<br/>GPUs, NVSwitch, NVLink"]
    end
    
    subgraph "User Actions"
        BuildAction["Building from Source"]
        DeployAction["Deploying Binary"]
        RuntimeAction["Executing fmpm"]
        IntegrationAction["Integration in Scripts"]
    end
    
    License --> Terms
    License --> Acceptance
    Terms --> LicenseFile
    
    LicenseFile --> SourceRepo
    SourceRepo --> SourceFile
    SourceRepo --> Makefile
    
    SourceFile --> Binary
    Makefile --> Binary
    Dependencies --> Binary
    
    Acceptance --> BuildAction
    Acceptance --> DeployAction
    Acceptance --> RuntimeAction
    Acceptance --> IntegrationAction
    
    BuildAction --> Binary
    DeployAction --> FMService
    RuntimeAction --> FMService
    IntegrationAction --> RuntimeAction
    
    FMService --> Hardware
    
    Terms -.->|"Governs"| BuildAction
    Terms -.->|"Governs"| DeployAction
    Terms -.->|"Governs"| RuntimeAction
    Terms -.->|"Governs"| IntegrationAction
    Terms -.->|"Restricts"| Hardware
```

**Sources:** [LICENSE:1-20](), [fmpm.cpp](), [Makefile]()

---

## License Grant and Restrictions Summary

The license provides specific rights while imposing mandatory restrictions. All users must understand and comply with these terms.

### Granted Rights

| Right | Scope | Reference |
|-------|-------|-----------|
| **Install and Use** | Install and use copies of the SOFTWARE | [LICENSE:21]() |
| **Modify Source** | Modify and create derivative works of source code portions | [LICENSE:23-24]() |
| **Deploy** | Deploy on infrastructure you own or lease | [LICENSE:26-27]() |
| **Distribute (Limited)** | Distribute with OSI-approved open source OS, unmodified binaries only | [LICENSE:29-33]() |

### Key Restrictions

| Restriction | Description | Impact on fmpm | Reference |
|-------------|-------------|----------------|-----------|
| **NVIDIA Platform Only** | SOFTWARE only licensed for use with NVIDIA-designed and NVIDIA-sold hardware | `fmpm` cannot be used with non-NVIDIA GPUs | [LICENSE:39-45]() |
| **No Reverse Engineering** | Cannot reverse engineer, decompile, or disassemble binary portions | Binary `fmpm` executable must not be reverse engineered | [LICENSE:47-49]() |
| **No Binary Modification** | Cannot modify or create derivative works of binary portions | Compiled `fmpm` must not be modified | [LICENSE:51-52]() |
| **GeForce/Titan Datacenter Ban** | GeForce/Titan SOFTWARE not licensed for datacenter deployment | Does not apply to Fabric Manager (datacenter product) | [LICENSE:69-71]() |
| **Critical Application Disclaimer** | Not tested/certified for critical applications (medical, automotive, avionics) | Users assume full liability for critical application use | [LICENSE:77-87]() |

**Sources:** [LICENSE:15-98]()

---

## License Compliance Checkpoints

The following diagram illustrates where license compliance requirements apply throughout the software lifecycle, mapped to specific code entities and system components.

### Software Lifecycle Compliance Points

```mermaid
graph LR
    subgraph "Acquisition Phase"
        Download["git clone<br/>NVIDIA/Fabric-Manager-Client"]
        ReadLicense["Read LICENSE File<br/>LICENSE:1-408"]
        AcceptTerms["Accept Terms<br/>Implicit by Use"]
    end
    
    subgraph "Build Phase"
        PrereqCheck["Install Prerequisites<br/>nvidia-fabricmanager-dev<br/>libjsoncpp-dev"]
        CompileCheck["Compile Source<br/>make -f Makefile<br/>g++ -o fmpm"]
        LinkCheck["Link Libraries<br/>libnvfm.so<br/>libjsoncpp.so"]
    end
    
    subgraph "Deployment Phase"
        BinaryDist["Distribute fmpm Binary"]
        ConfigDeploy["Configure FM Service<br/>FM_CMD_BIND_INTERFACE<br/>FM_CMD_UNIX_SOCKET_PATH"]
        HardwareVerify["Verify NVIDIA Platform<br/>GPUs, NVSwitch"]
    end
    
    subgraph "Runtime Phase"
        ExecuteFmpm["Execute fmpm Commands<br/>-l, -a, -d, --set-activated-list"]
        ConnectFM["Connect to FM Service<br/>TCP or Unix Socket"]
        ManageHardware["Manage GPU Partitions<br/>NVLink Configuration"]
    end
    
    subgraph "License Restrictions"
        PlatformRestrict["Platform Restriction<br/>LICENSE:39-45<br/>NVIDIA Platform Only"]
        BinaryRestrict["Binary Restriction<br/>LICENSE:47-52<br/>No Modification"]
        CriticalAppRestrict["Critical App Disclaimer<br/>LICENSE:77-87<br/>No Liability"]
    end
    
    Download --> ReadLicense
    ReadLicense --> AcceptTerms
    AcceptTerms --> PrereqCheck
    
    PrereqCheck --> CompileCheck
    CompileCheck --> LinkCheck
    LinkCheck --> BinaryDist
    
    BinaryDist --> ConfigDeploy
    ConfigDeploy --> HardwareVerify
    HardwareVerify --> ExecuteFmpm
    
    ExecuteFmpm --> ConnectFM
    ConnectFM --> ManageHardware
    
    PlatformRestrict -.->|"Enforced at"| HardwareVerify
    PlatformRestrict -.->|"Enforced at"| ManageHardware
    BinaryRestrict -.->|"Applies to"| BinaryDist
    BinaryRestrict -.->|"Applies to"| ExecuteFmpm
    CriticalAppRestrict -.->|"User Liability"| ManageHardware
```

**Sources:** [LICENSE:5-10](), [LICENSE:15-98](), [Makefile](), [fmpm.cpp]()

---

## Platform and Hardware Restrictions

The license explicitly restricts the software to NVIDIA Platform hardware. This section maps license restrictions to actual hardware components managed by the software.

### Platform Restriction Architecture

```mermaid
graph TB
    subgraph "License Requirements - LICENSE:39-45"
        PlatformLicense["NVIDIA Platform Requirement<br/>Microprocessors, SoCs, GPUs<br/>Designed AND Sold by NVIDIA"]
        FirmwareRestrict["Firmware Restriction<br/>No Translation to Other Architectures"]
    end
    
    subgraph "Compliant Hardware - Managed by fmpm"
        NVSwitchHW["NVSwitch Fabric<br/>NVIDIA-designed Interconnect"]
        DatacenterGPU["Datacenter GPUs<br/>A100, H100, GH200, etc.<br/>NVIDIA Platform Compliant"]
        NVLinkHW["NVLink Interconnects<br/>NVIDIA Proprietary Technology"]
    end
    
    subgraph "fmpm Operations - Source: fmpm.cpp"
        ListPartCmd["fmpm -l<br/>fmGetSupportedFabricPartitions()"]
        ActivateCmd["fmpm -a ID<br/>fmActivateFabricPartition()"]
        DeactivateCmd["fmpm -d ID<br/>fmDeactivateFabricPartition()"]
        FailedDevCmd["fmpm --get-nvlink-failed-devices<br/>fmGetNvLinkFailedDevices()"]
    end
    
    subgraph "Non-Compliant Hardware - License Violation"
        NonNVGPU["Non-NVIDIA GPUs<br/>AMD, Intel, etc.<br/>LICENSE VIOLATION"]
        GeForceDatacenter["GeForce/Titan in Datacenter<br/>LICENSE:69-71<br/>PROHIBITED"]
    end
    
    subgraph "Fabric Manager Service"
        FMService["nvidia-fabricmanager<br/>Communicates with fmpm<br/>Controls Hardware"]
    end
    
    PlatformLicense --> NVSwitchHW
    PlatformLicense --> DatacenterGPU
    PlatformLicense --> NVLinkHW
    FirmwareRestrict --> NVSwitchHW
    
    ListPartCmd --> FMService
    ActivateCmd --> FMService
    DeactivateCmd --> FMService
    FailedDevCmd --> FMService
    
    FMService --> NVSwitchHW
    FMService --> DatacenterGPU
    FMService --> NVLinkHW
    
    PlatformLicense -.->|"PROHIBITS"| NonNVGPU
    PlatformLicense -.->|"PROHIBITS"| GeForceDatacenter
    
    NonNVGPU -.->|"Cannot Use"| ListPartCmd
    GeForceDatacenter -.->|"Cannot Use"| ListPartCmd
```

**Sources:** [LICENSE:39-45](), [LICENSE:69-71](), [fmpm.cpp]()

---

## Critical Application Disclaimer

Section 2.10 of the license explicitly disclaims liability for critical applications. This applies to all usage of the `fmpm` client and Fabric Manager system.

### Critical Application Categories

| Application Type | Examples | License Position | User Responsibility |
|------------------|----------|------------------|---------------------|
| **Avionics** | Flight control systems, navigation | Not tested or certified | Full liability for safety features |
| **Automotive** | Autonomous driving, vehicle control | Not tested or certified | Comply with regulatory standards |
| **Medical** | Life support, surgical systems | Not tested or certified | Full liability for medical device compliance |
| **Military** | Weapons systems, command and control | Not tested or certified | Full liability for military applications |
| **Life Critical** | Emergency response, nuclear systems | Not tested or certified | Ensure sufficient redundancy |

**Key License Terms:**
- NVIDIA is **not liable** for claims or damages from critical application use
- Users are **solely responsible** for safety and redundancy features
- Users must comply with **all applicable legal and regulatory standards**
- Users must **defend and indemnify** NVIDIA from claims arising from critical application use

**Sources:** [LICENSE:77-87]()

---

## Warranty Disclaimers and Liability Limits

The license includes comprehensive disclaimers and liability limitations that apply to all components of the system.

### Disclaimer and Liability Framework

```mermaid
graph TB
    subgraph "WARRANTY DISCLAIMERS - LICENSE:279-305"
        AsIs["SOFTWARE PROVIDED AS-IS<br/>WITH ALL FAULTS"]
        NoWarranty["No Warranties:<br/>- MERCHANTABILITY<br/>- FITNESS FOR PURPOSE<br/>- NONINFRINGEMENT<br/>- ERROR CORRECTION"]
        NoGuarantee["No Guarantee:<br/>- Meet Requirements<br/>- Free of Viruses<br/>- Available Content"]
    end
    
    subgraph "LIABILITY LIMITATIONS - LICENSE:306-320"
        NoIndirect["No Indirect Damages:<br/>- Punitive<br/>- Consequential<br/>- Incidental<br/>- Special"]
        NoCostDamages["No Cost Damages:<br/>- Substitute Goods<br/>- Lost Profits<br/>- Lost Revenue<br/>- Lost Data"]
        CapLimit["Total Liability Cap:<br/>US $5 Maximum"]
    end
    
    subgraph "USER RESPONSIBILITIES"
        DataBackup["User Must:<br/>- Maintain Data Backups<br/>- System Restore Points<br/>- Configuration Backups"]
        VersionCheck["User Must:<br/>- Verify Correct Version<br/>- Check Hardware Compatibility<br/>- Validate Configuration"]
        LossRisk["User Accepts Risk:<br/>- Configuration Changes<br/>- Data Loss<br/>- System Damage"]
    end
    
    subgraph "Applies to All Components"
        FmpmBinary["fmpm executable"]
        FMServiceComp["Fabric Manager Service"]
        PartitionOps["Partition Operations<br/>Activate/Deactivate"]
        NVLinkMgmt["NVLink Management"]
    end
    
    AsIs --> NoWarranty
    AsIs --> NoGuarantee
    NoWarranty --> DataBackup
    NoGuarantee --> VersionCheck
    
    NoIndirect --> NoCostDamages
    NoCostDamages --> CapLimit
    CapLimit --> LossRisk
    
    DataBackup --> FmpmBinary
    VersionCheck --> FmpmBinary
    LossRisk --> FmpmBinary
    
    FmpmBinary --> FMServiceComp
    FMServiceComp --> PartitionOps
    FMServiceComp --> NVLinkMgmt
```

**Sources:** [LICENSE:279-320]()

---

## License Termination and Enforcement

The license can terminate automatically under specific conditions. Understanding termination triggers is critical for continued legal use of the software.

### Termination Conditions

| Condition | Description | Effect | Reference |
|-----------|-------------|--------|-----------|
| **Breach of Terms** | Failure to comply with any license term | Automatic termination without notice | [LICENSE:161-163]() |
| **Legal Proceeding** | Commencing legal action against NVIDIA regarding SOFTWARE | Automatic termination | [LICENSE:161-163]() |
| **User Termination** | User stops using and destroys all copies | Voluntary termination | [LICENSE:165-166]() |
| **Post-Termination Obligations** | Must stop using and destroy all SOFTWARE copies | Required immediately | [LICENSE:164]() |

### Survival of Terms

Upon termination, all provisions survive **except** for the licenses granted to you. This means:
- Warranty disclaimers remain in effect
- Liability limitations remain in effect
- Indemnification obligations remain in effect
- Prior distributions according to the Agreement are not affected

**Sources:** [LICENSE:159-168]()

---

## Intellectual Property and Ownership

All intellectual property in the SOFTWARE remains the exclusive property of NVIDIA or its licensors. Users receive only the limited license rights explicitly granted in the Agreement.

### Ownership Structure

| Component | Owner | User Rights | Restrictions |
|-----------|-------|-------------|--------------|
| **fmpm Source Code** | NVIDIA | Modify source, create derivatives | Cannot distribute modified headers |
| **fmpm Binary** | NVIDIA | Use, deploy, distribute (limited) | Cannot modify or reverse engineer |
| **libnvfm Library** | NVIDIA | Link and use | Cannot reverse engineer |
| **FM API** | NVIDIA | Call API functions | Cannot bypass security mechanisms |
| **Documentation** | NVIDIA | Use for permitted purposes | Cannot remove copyright notices |

**Key Ownership Terms:**
- NVIDIA reserves **all rights, interests, and remedies** not expressly granted
- **No implied licenses** or rights by estoppel
- Users must **cooperate with compliance verification** by NVIDIA
- Users cannot **misrepresent authorship** of the SOFTWARE

**Sources:** [LICENSE:170-178]()

---

## Feedback and Contributions

If users provide feedback, suggestions, or modifications to NVIDIA, the license includes specific terms regarding intellectual property rights.

### Feedback Provisions

```mermaid
graph LR
    subgraph "User Provides - Optional"
        FeedbackTypes["Feedback Types:<br/>- Suggestions<br/>- Requests<br/>- Bug Fixes<br/>- Modifications<br/>- Enhancements"]
        ConfidentialMark["May Mark as Confidential<br/>No Confidentiality Obligation Created"]
    end
    
    subgraph "License Grant to NVIDIA"
        LicenseScope["Non-exclusive, Perpetual,<br/>Irrevocable, Sublicensable<br/>Worldwide, Royalty-free"]
        LicenseRights["Rights:<br/>- Reproduce<br/>- Use, Make, Have Made<br/>- Sell, Distribute<br/>- Create Derivatives<br/>- Commercialize"]
    end
    
    subgraph "User Restrictions"
        NoImpairment["Cannot Give Feedback<br/>Subject to Restrictions"]
        NoShareRequirement["Cannot Require<br/>License-to-Third-Party<br/>for NVIDIA Products"]
    end
    
    subgraph "Example Scenario"
        UserMod["User Modifies fmpm.cpp<br/>Adds Feature"]
        ShareWithNVIDIA["Shares with NVIDIA<br/>as Feedback"]
        NVIDIAOwns["NVIDIA Can:<br/>- Incorporate in Product<br/>- Commercialize<br/>- No Compensation to User"]
    end
    
    FeedbackTypes --> LicenseScope
    ConfidentialMark --> LicenseScope
    LicenseScope --> LicenseRights
    
    LicenseRights -.->|"Subject to"| NoImpairment
    LicenseRights -.->|"Subject to"| NoShareRequirement
    
    UserMod --> ShareWithNVIDIA
    ShareWithNVIDIA --> NVIDIAOwns
    LicenseRights --> NVIDIAOwns
```

**Important:** Users grant NVIDIA broad rights to any feedback provided. If you want to retain rights to modifications, do not share them with NVIDIA as feedback.

**Sources:** [LICENSE:180-197]()

---

## Dispute Resolution Process

The license mandates a specific dispute resolution process, including informal resolution, arbitration, and limitations on legal proceedings.

### Dispute Resolution Flow

```mermaid
graph TB
    subgraph "Dispute Arises"
        DisputeEvent["Dispute, Claim, or Controversy<br/>Related to SOFTWARE or Agreement"]
    end
    
    subgraph "Step 1: Informal Resolution - LICENSE:201-213"
        InformalStart["Parties Work in Good Faith<br/>to Resolve Informally"]
        ContactNVIDIA["User Contacts NVIDIA:<br/>NVIDIA Corporation, ATTN: Legal<br/>2788 San Tomas Expressway<br/>Santa Clara, CA 95051"]
        NVIDIAOpportunity["Give NVIDIA Opportunity<br/>to Resolve"]
    end
    
    subgraph "Step 2: Small Claims Option - LICENSE:207-213"
        SmallClaimsCheck{"Small Claims<br/>Requirements<br/>Satisfied?"}
        SmallClaimsVenue["File in Small Claims Court:<br/>- Your County of Residence<br/>- Closest to Residence<br/>- Santa Clara County, CA"]
    end
    
    subgraph "Step 3: Binding Arbitration - LICENSE:215-241"
        JAMSArbitration["Binding Arbitration via JAMS<br/>Judicial Mediation & Arbitration Services<br/>Rules: https://www.jamsadr.com/"]
        ArbitrationVenue["Location:<br/>Santa Clara County, CA<br/>Unless In-Person Hearing Requested<br/>in Your Hometown"]
        IndividualOnly["Individual Arbitration Only<br/>No Class Action<br/>No Representative Action"]
        ArbitratorDecides["Arbitrator Decides:<br/>- Jurisdiction<br/>- Arbitrability<br/>- Individual Claims Only"]
    end
    
    subgraph "Step 4: Court (If Necessary) - LICENSE:232-240"
        CourtVenue["If Arbitration Fails:<br/>State or Federal Court<br/>Santa Clara County, CA"]
        EquitableRelief["Exception: Injunctive Relief<br/>for IP or Proprietary Rights<br/>Any Jurisdiction"]
    end
    
    subgraph "Waivers - LICENSE:242-248"
        JuryWaiver["Jury Trial Waived"]
        ClassWaiver["Class Action Waived"]
        CollectiveWaiver["Collective Proceeding Waived"]
    end
    
    subgraph "Opt-Out Option - LICENSE:250-267"
        OptOutWindow["30 Days from:<br/>- Commencement of Use<br/>- Agreement Effective Date<br/>- Future Changes to Section 10.4"]
        OptOutMethod["Written Notice to NVIDIA:<br/>Mail to NVIDIA Legal<br/>Include: Name, Address<br/>Software Reference, Clear Statement"]
        OptOutEffect["If Opt-Out Valid:<br/>Not Required to Arbitrate<br/>Agreement Still Applies"]
    end
    
    DisputeEvent --> InformalStart
    InformalStart --> ContactNVIDIA
    ContactNVIDIA --> NVIDIAOpportunity
    
    NVIDIAOpportunity --> SmallClaimsCheck
    SmallClaimsCheck -->|"Yes"| SmallClaimsVenue
    SmallClaimsCheck -->|"No"| JAMSArbitration
    
    JAMSArbitration --> ArbitrationVenue
    ArbitrationVenue --> IndividualOnly
    IndividualOnly --> ArbitratorDecides
    
    ArbitratorDecides --> CourtVenue
    CourtVenue --> EquitableRelief
    
    JAMSArbitration -.->|"Subject to"| JuryWaiver
    JAMSArbitration -.->|"Subject to"| ClassWaiver
    JAMSArbitration -.->|"Subject to"| CollectiveWaiver
    
    DisputeEvent -.->|"User Can"| OptOutWindow
    OptOutWindow --> OptOutMethod
    OptOutMethod --> OptOutEffect
```

**Key Points:**
- Disputes must first be attempted to be resolved informally
- Arbitration is mandatory unless user opts out within 30 days
- Arbitration location is Santa Clara County, California (unless user requests hometown hearing)
- Class actions are prohibited
- Jury trials are waived

**Sources:** [LICENSE:199-277]()

---

## Governing Law

All disputes are governed by specific legal jurisdictions and laws.

### Legal Jurisdiction

| Aspect | Governing Authority | Reference |
|--------|---------------------|-----------|
| **Primary Law** | Federal Arbitration Act | [LICENSE:270-271]() |
| **State Law** | Delaware State Law (substantive) | [LICENSE:270-271]() |
| **Federal Law** | United States Federal Law | [LICENSE:270-271]() |
| **Conflict of Laws** | Not applicable (explicitly disclaimed) | [LICENSE:271-272]() |
| **International Sales** | UN Convention on International Sale of Goods disclaimed | [LICENSE:272-273]() |
| **Language** | English version governs if conflict with translation | [LICENSE:274-277]() |

**Sources:** [LICENSE:269-277]()

---

## Additional Legal Provisions

### Trade Compliance

Users must comply with all applicable export, import, trade, and economic sanctions laws, including:
- U.S. Export Administration Regulations
- Office of Foreign Assets Control (OFAC) regulations
- Restrictions on destinations, end-users, and end-use

**Sources:** [LICENSE:349-354]()

### Government Use

If supplying the SOFTWARE to the U.S. Government, specific requirements apply:
- SOFTWARE must be treated as commercial computer software
- Developed at private expense
- Subject to this Agreement's terms
- Rights limited to 48 C.F.R. 52.227-19(b)(1)-(2) or 252.227-7013(c)

**Sources:** [LICENSE:356-372]()

### Data Collection

On Windows operating systems, NVIDIA collects data at installation time for:
- System configuration and optimization
- Content/service delivery
- Product improvement

Information collected may include GPU, CPU, and operating system configuration data.

**Sources:** [LICENSE:322-339]()

---

## Contact Information

For questions or legal notices regarding the license:

| Purpose | Contact Method |
|---------|----------------|
| **Legal Notices** | NVIDIA Corporation<br/>Attention: Legal Department<br/>2788 San Tomas Expressway<br/>Santa Clara, CA 95051, USA |
| **Licensing Questions** | Email: driver-licensing@nvidia.com |
| **Privacy Policy** | https://www.nvidia.com/en-us/about-nvidia/privacy-policy |

**Sources:** [LICENSE:374-406]()

---

## License Version and Effective Date

**Current License Version:** November 23, 2023

This license agreement was last updated on November 23, 2023. Users should verify they are operating under the current license terms.

**Sources:** [LICENSE:408]()

---

## Summary of User Obligations

The following table summarizes key user obligations when using the fmpm software:

| Obligation | Requirement | Compliance Action |
|------------|-------------|-------------------|
| **Accept Terms** | Accept all license terms before use | Read and agree to LICENSE file |
| **NVIDIA Platform** | Use only with NVIDIA-designed and NVIDIA-sold hardware | Verify GPU/NVSwitch hardware |
| **No Modification** | Do not modify fmpm binary | Use unmodified compiled executable |
| **No Reverse Engineering** | Do not reverse engineer binaries | Use as provided |
| **Critical App Disclaimer** | Accept full liability for critical applications | Ensure safety features and compliance |
| **Indemnification** | Defend and indemnify NVIDIA from claims | Accept liability for product development |
| **Data Backup** | Maintain backups and restore points | Implement backup procedures |
| **Trade Compliance** | Comply with export/import regulations | Follow applicable trade laws |
| **Dispute Resolution** | Follow informal resolution and arbitration | Contact NVIDIA legal for disputes |

**Sources:** [LICENSE:1-408]()

---

