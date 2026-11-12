<!-- source: DeepWiki mcp.deepwiki.com · repo mukul975/Anthropic-Cybersecurity-Skills · extra page CSF Alignment Details · fetched 2026-10-26 -->

# CSF Alignment Details

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mappings/mitre-attack/coverage-summary.md](mappings/mitre-attack/coverage-summary.md)
- [mappings/nist-csf/README.md](mappings/nist-csf/README.md)
- [mappings/nist-csf/csf-alignment.md](mappings/nist-csf/csf-alignment.md)
- [mappings/owasp/README.md](mappings/owasp/README.md)
- [skills/implementing-gdpr-data-protection-controls/SKILL.md](skills/implementing-gdpr-data-protection-controls/SKILL.md)
- [skills/implementing-iso-27001-information-security-management/SKILL.md](skills/implementing-iso-27001-information-security-management/SKILL.md)
- [skills/implementing-pci-dss-compliance-controls/SKILL.md](skills/implementing-pci-dss-compliance-controls/SKILL.md)
- [skills/performing-nist-csf-maturity-assessment/SKILL.md](skills/performing-nist-csf-maturity-assessment/SKILL.md)
- [skills/performing-soc2-type2-audit-preparation/SKILL.md](skills/performing-soc2-type2-audit-preparation/SKILL.md)

</details>



This document details the subdomain-to-category alignment that maps the 817 cybersecurity skills to NIST Cybersecurity Framework (CSF) 2.0 functions and categories. It provides the complete mapping table, coverage analysis across the six CSF core functions, and gap identification for underrepresented categories.

For general information about the NIST CSF 2.0 mapping approach and function descriptions, see [NIST CSF 2.0 Mapping](#4.2). For MITRE ATT&CK framework mappings, see [MITRE ATT&CK Mapping](#4.1).

## Alignment Methodology

The CSF alignment operates through a two-level mapping strategy: skills are first organized into **29 subdomains** (defined in `index.json`), and each subdomain is then mapped to one or more **CSF categories** within the six core functions (Govern, Identify, Protect, Detect, Respond, Recover). This approach enables efficient categorization of skills without requiring manual CSF tagging on every individual skill.

### Data Flow: Skill to CSF Category
The following diagram illustrates how a skill's metadata (subdomain) determines its alignment with the NIST CSF 2.0 categories.

```mermaid
graph LR
    subgraph "Skills Layer"
        S1["SKILL.md frontmatter<br/>(subdomain field)"]
    end
    
    subgraph "Subdomain Layer"
        SD1["api-security (28)"]
        SD2["cloud-security (48)"]
        SD3["compliance-governance (5)"]
        SD4["threat-hunting (35)"]
        SD5["incident-response (24)"]
        SD6["... 24 more subdomains"]
    end
    
    subgraph "CSF Function Layer"
        GV["GV: Govern"]
        ID["ID: Identify"]
        PR["PR: Protect"]
        DE["DE: Detect"]
        RS["RS: Respond"]
        RC["RC: Recover"]
    end
    
    subgraph "CSF Category Layer"
        GV_RM["GV.RM: Risk Management"]
        ID_RA["ID.RA: Risk Assessment"]
        PR_AA["PR.AA: Access Control"]
        DE_CM["DE.CM: Continuous Monitoring"]
        RS_AN["RS.AN: Incident Analysis"]
        RC_RP["RC.RP: Recovery Planning"]
    end
    
    S1 --> SD1
    S1 --> SD2
    S1 --> SD3
    S1 --> SD4
    S1 --> SD5
    
    SD1 --> PR
    SD2 --> ID
    SD2 --> PR
    SD3 --> GV
    SD4 --> DE
    SD5 --> RS
    SD5 --> RC
    
    PR --> PR_AA
    ID --> ID_RA
    DE --> DE_CM
    RS --> RS_AN
    RC --> RC_RP
```

**Sources:** [mappings/nist-csf/csf-alignment.md:1-39](), [mappings/nist-csf/README.md:14-90]()

## Complete Subdomain-to-CSF Alignment

The complete alignment is defined in `mappings/nist-csf/csf-alignment.md` as a reference table mapping each skill subdomain to their primary CSF function(s), specific CSF category IDs, and alignment rationale.

### Alignment Table Structure

| Field | Description | Example |
|-------|-------------|---------|
| **Subdomain (Skills)** | Subdomain name with skill count | `api-security (28)` |
| **Primary CSF Function** | Main CSF function(s) | `Protect (PR)` |
| **CSF Categories** | Specific category IDs | `PR.DS, PR.PS` |
| **Alignment Rationale** | Explanation of mapping | `API hardening, authentication, input validation` |

**Sources:** [mappings/nist-csf/csf-alignment.md:13-38]()

### Key Subdomain Mappings

#### High-Coverage Subdomains
The repository shows significant concentration in technical subdomains like `cloud-security` (48 skills) and `web-application-security` (41 skills), which drive the majority of coverage in the **Protect** and **Identify** functions.

```mermaid
graph TB
    subgraph "Protect Function Subdomains"
        IAM["identity-access-management<br/>(33 skills)"]
        ZTA["zero-trust-architecture<br/>(13 skills)"]
        CRYPTO["cryptography<br/>(13 skills)"]
        DEVSEC["devsecops<br/>(16 skills)"]
    end
    
    subgraph "Detect Function Subdomains"
        TH["threat-hunting<br/>(35 skills)"]
        SOC["soc-operations<br/>(33 skills)"]
        MALWARE["malware-analysis<br/>(34 skills)"]
    end
    
    subgraph "Respond Function Subdomains"
        IR["incident-response<br/>(24 skills)"]
        DF["digital-forensics<br/>(34 skills)"]
    end
    
    subgraph "CSF Categories"
        PR_AA["PR.AA: Access Control"]
        PR_DS["PR.DS: Data Security"]
        DE_CM["DE.CM: Continuous Monitoring"]
        DE_AE["DE.AE: Adverse Event Analysis"]
        RS_MA["RS.MA: Incident Management"]
        RS_AN["RS.AN: Incident Analysis"]
    end
    
    IAM --> PR_AA
    ZTA --> PR_AA
    CRYPTO --> PR_DS
    DEVSEC --> PR_DS
    
    TH --> DE_CM
    TH --> DE_AE
    SOC --> DE_CM
    SOC --> DE_AE
    MALWARE --> DE_AE
    
    IR --> RS_MA
    IR --> RS_AN
    DF --> RS_AN
```

**Sources:** [mappings/nist-csf/csf-alignment.md:13-38](), [mappings/nist-csf/README.md:14-90]()

#### Multi-Function Subdomains
Several subdomains reflect the cross-functional nature of modern security operations:

| Subdomain | Functions | Categories | Rationale |
|-----------|-----------|------------|-----------|
| `cloud-security` (48) | Identify, Protect | `ID.AM`, `PR.DS`, `PR.PS`, `PR.IR` | Asset management + data protection + infrastructure |
| `incident-response` (24) | Respond, Recover | `RS.MA`, `RS.AN`, `RS.MI`, `RS.CO`, `RC.RP`, `RC.CO` | Full incident lifecycle |
| `soc-operations` (33) | Detect, Respond, Govern | `DE.CM`, `DE.AE`, `RS.MA`, `GV.OV` | Monitoring + triage + oversight |
| `threat-intelligence` (43) | Identify, Detect | `ID.RA`, `DE.AE` | Risk assessment + threat detection |
| `devsecops` (16) | Protect, Govern | `PR.PS`, `GV.SC` | Platform security + supply chain |

**Sources:** [mappings/nist-csf/csf-alignment.md:16-38]()

## Coverage Analysis by CSF Function

The alignment produces a distribution across the six CSF core functions. While the collection is robust in **Protect** (~160 skills) and **Identify** (~115 skills), the **Recover** function remains an area for expansion.

### Function Coverage Distribution

```mermaid
graph TB
    subgraph "CSF Functions by Coverage"
        direction LR
        PR["Protect (PR)<br/>~160 skills<br/>████████████████████"]
        ID["Identify (ID)<br/>~115 skills<br/>██████████████████"]
        RS["Respond (RS)<br/>~111 skills<br/>██████████████████"]
        DE["Detect (DE)<br/>~102 skills<br/>████████████████"]
        GV["Govern (GV)<br/>~54 skills<br/>████████████"]
        RC["Recover (RC)<br/>~29 skills<br/>████"]
    end
    
    subgraph "Primary Contributing Subdomains"
        direction TB
        PR_SUB["IAM, ZTA, devsecops,<br/>cryptography, cloud-security"]
        ID_SUB["vulnerability-management,<br/>threat-intelligence, cloud-security"]
        RS_SUB["incident-response,<br/>digital-forensics, malware-analysis"]
        DE_SUB["threat-hunting,<br/>soc-operations, malware-analysis"]
        GV_SUB["compliance-governance,<br/>identity-access-management"]
        RC_SUB["incident-response,<br/>ransomware-defense"]
    end
    
    PR --> PR_SUB
    ID --> ID_SUB
    RS --> RS_SUB
    DE --> DE_SUB
    GV --> GV_SUB
    RC --> RC_SUB
```

**Sources:** [mappings/nist-csf/README.md:92-101]()

### Coverage Metrics by Function

| Function | Approx. Skills | Primary Subdomains | Coverage Assessment |
|----------|--------|------------------|---------------------|
| Protect (PR) | ~160 | IAM, cloud-security, cryptography | Strong coverage across access control and data security. |
| Identify (ID) | ~115 | vulnerability-management, threat-intelligence | Strong coverage in risk assessment and asset discovery. |
| Respond (RS) | ~111 | incident-response, digital-forensics | Strong coverage across the investigation lifecycle. |
| Detect (DE) | ~102 | threat-hunting, soc-operations | Good coverage in proactive monitoring and analysis. |
| Govern (GV) | ~54 | compliance-governance, IAM | Focused primarily on compliance frameworks (PCI, SOC2, GDPR). |
| Recover (RC) | ~29 | incident-response, ransomware-defense | Limited to specific recovery planning and communication skills. |

**Sources:** [mappings/nist-csf/README.md:16-101]()

## Coverage Analysis by CSF Category

The alignment maps skills to **22 CSF categories** across the six functions. Category-level analysis reveals specific strengths and gaps.

### Govern (GV) Categories
The Govern function was introduced in CSF 2.0 and is primarily populated by the `compliance-governance` subdomain.

| Category | ID | Subdomain Coverage |
|----------|-----|-------------------|
| Organizational Context | GV.OC | compliance-governance |
| Risk Management Strategy | GV.RM | compliance-governance, vulnerability-management |
| Roles, Responsibilities | GV.RR | compliance-governance, identity-access-management |
| Policy | GV.PO | compliance-governance, zero-trust-architecture |
| Oversight | GV.OV | compliance-governance, soc-operations |
| Supply Chain Risk Mgmt | GV.SC | devsecops, container-security |

**Sources:** [mappings/nist-csf/README.md:20-27](), [mappings/nist-csf/csf-alignment.md:44-51]()

### Identify (ID) Categories

| Category | ID | Subdomain Coverage | Skill Count |
|----------|-----|-------------------|-------------|
| Asset Management | ID.AM | cloud-security, container-security, network-security | 107 |
| Risk Assessment | ID.RA | vulnerability-mgmt, threat-intel, pen-testing, red-teaming | 67 |
| Improvement | ID.IM | soc-operations, red-teaming, compliance-governance | 38 |

**Sources:** [mappings/nist-csf/README.md:35-39](), [mappings/nist-csf/csf-alignment.md:55-59]()

### Protect (PR) Categories

| Category | ID | Subdomain Coverage | Skill Count |
|----------|-----|-------------------|-------------|
| Access Control | PR.AA | identity-access-management, zero-trust-architecture | 46 |
| Awareness & Training | PR.AT | phishing-defense, compliance-governance | 21 |
| Data Security | PR.DS | cryptography, cloud-security, api-security | 89 |
| Platform Security | PR.PS | endpoint-security, container-security, devsecops | 58 |
| Infra Resilience | PR.IR | network-security, zero-trust-architecture | 46 |

**Sources:** [mappings/nist-csf/README.md:47-53](), [mappings/nist-csf/csf-alignment.md:63-69]()

## Gap Identification

The alignment table identifies **five CSF categories** with low coverage, indicating areas for future skill development.

```mermaid
graph TB
    subgraph "Identified Gaps"
        direction TB
        GAP1["GV.OC: Organizational Context<br/>5 skills<br/>CRITICAL GAP<br/>Need mission alignment skills"]
        GAP2["GV.PO: Policy<br/>Low coverage<br/>Need policy development skills"]
        GAP3["PR.AT: Awareness & Training<br/>21 skills<br/>MODERATE GAP<br/>Expand beyond phishing"]
        GAP4["RC.RP: Recovery Planning<br/>29 skills<br/>SIGNIFICANT GAP<br/>Need disaster recovery/BC skills"]
        GAP5["RC.CO: Recovery Communication<br/>Low coverage<br/>Need stakeholder mgmt skills"]
    end
    
    subgraph "Current State"
        CURRENT_GV["Govern: Focused on<br/>compliance-governance<br/>subdomain only"]
        CURRENT_RC["Recover: Limited to<br/>incident-response and<br/>ransomware-defense"]
    end
    
    CURRENT_GV --> GAP1
    CURRENT_GV --> GAP2
    CURRENT_RC --> GAP4
    CURRENT_RC --> GAP5
```

**Sources:** [mappings/nist-csf/csf-alignment.md:94-102]()

## Case Study: Compliance-Governance Alignment
Skills within the `compliance-governance` subdomain provide direct mapping to specific NIST CSF 2.0 categories through their YAML frontmatter.

| Skill Name | NIST CSF Mapping | Subdomain |
|------------|------------------|-----------|
| `performing-nist-csf-maturity-assessment` | GV.OC-01, GV.RM-01, GV.PO-01, ID.RA-01, GV.OV-01 | compliance-governance |
| `implementing-pci-dss-compliance-controls` | GV.PO-01, PR.DS-01, PR.AA-01, DE.CM-01, ID.RA-01 | compliance-governance |
| `performing-soc2-type2-audit-preparation` | GV.OC-01, GV.RM-01, GV.PO-01, GV.OV-01 | governance-risk-compliance |

**Sources:** [skills/performing-nist-csf-maturity-assessment/SKILL.md:17-22](), [skills/implementing-pci-dss-compliance-controls/SKILL.md:14-19](), [skills/performing-soc2-type2-audit-preparation/SKILL.md:24-28]()

## Implementation Files

### File: csf-alignment.md
Contains the complete subdomain-to-category mapping table and the detailed gap analysis identifying underrepresented categories.
**File path:** [mappings/nist-csf/csf-alignment.md:1-102]()

### File: README.md
Contains the high-level function descriptions, visual coverage distribution, and instructions for AI agents to query skills by CSF function using subdomain filters.
**File path:** [mappings/nist-csf/README.md:1-134]()

**Sources:** [mappings/nist-csf/csf-alignment.md:1-102](), [mappings/nist-csf/README.md:1-134]()

---

