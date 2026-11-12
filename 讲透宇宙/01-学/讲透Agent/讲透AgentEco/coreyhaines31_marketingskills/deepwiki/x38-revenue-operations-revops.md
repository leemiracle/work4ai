<!-- source: DeepWiki mcp.deepwiki.com · repo coreyhaines31/marketingskills · extra page Revenue Operations (RevOps) · fetched 2026-10-27 -->

# Revenue Operations (RevOps)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/churn-prevention/SKILL.md](skills/churn-prevention/SKILL.md)
- [skills/cold-email/SKILL.md](skills/cold-email/SKILL.md)
- [skills/revops/SKILL.md](skills/revops/SKILL.md)
- [skills/revops/references/automation-playbooks.md](skills/revops/references/automation-playbooks.md)
- [skills/revops/references/lifecycle-definitions.md](skills/revops/references/lifecycle-definitions.md)
- [skills/revops/references/routing-rules.md](skills/revops/references/routing-rules.md)
- [skills/revops/references/scoring-models.md](skills/revops/references/scoring-models.md)

</details>



The Revenue Operations (RevOps) skill provides a framework for designing and optimizing the systems that connect marketing, sales, and customer success into a unified revenue engine. It focuses on the technical implementation of lead lifecycles, scoring models, and automated routing rules within a CRM to eliminate handoff leaks and increase pipeline velocity.

## Purpose and Scope

RevOps acts as the operational glue between GTM (Go-To-Market) strategy and technical execution. The primary goal is to establish a "Single Source of Truth" by picking a CRM as the canonical record and syncing all marketing and product data to it [skills/revops/SKILL.md:32-33]().

The scope includes:
*   **Lead Lifecycle Management:** Defining stages from Subscriber to Evangelist [skills/revops/SKILL.md:50-58]().
*   **Lead Scoring:** Implementing fit (explicit) and engagement (implicit) models [skills/revops/SKILL.md:83-95]().
*   **Routing Logic:** Automating lead distribution based on territories, accounts, or round-robin rules [skills/revops/SKILL.md:126-131]().
*   **SLA Enforcement:** Measuring and alerting on speed-to-lead benchmarks [skills/revops/SKILL.md:140-147]().
*   **Pipeline Hygiene:** Managing deal stages and stale deal detection [skills/revops/SKILL.md:155-157]().

## Lead Lifecycle Framework

The lifecycle framework defines the technical state transitions a contact undergoes. Each stage requires specific entry and exit criteria to ensure data hygiene across the funnel [skills/revops/SKILL.md:48-58]().

### Lifecycle State Transitions

The following diagram illustrates the flow of a contact through the revenue engine, mapping the natural language stages to the operational owners.

**Title: Lead Lifecycle State Machine**
```mermaid
graph TD
    subgraph "Marketing_Owned"
        ["Subscriber"] -- "Provides_Company_Info" --> ["Lead"]
        ["Lead"] -- "Passes_Fit_Engagement_Threshold" --> ["MQL"]
    end

    subgraph "Sales_Owned"
        ["MQL"] -- "Sales_Acceptance_SLA" --> ["SQL"]
        ["SQL"] -- "Conversation_Qualified" --> ["Opportunity"]
        ["Opportunity"] -- "Closed_Won" --> ["Customer"]
    end

    subgraph "CS_Marketing_Owned"
        ["Customer"] -- "High_NPS_Referral" --> ["Evangelist"]
    end

    style ["MQL"] stroke-width:4px
    style ["SQL"] stroke-width:4px
```
Sources: [skills/revops/SKILL.md:50-58](), [skills/revops/references/lifecycle-definitions.md:7-138]()

## Lead Scoring Implementation

Scoring is divided into **Fit (Explicit)** and **Engagement (Implicit)** dimensions. A contact typically becomes a Marketing Qualified Lead (MQL) only when the combined score crosses a defined threshold (usually 50-80 points) [skills/revops/SKILL.md:62-67]().

### Scoring Dimensions and Weights

| Category | Attribute / Signal | Example Point Value | Decay Logic |
| :--- | :--- | :--- | :--- |
| **Fit** | Job Title (C-Suite) | +25 [skills/revops/references/scoring-models.md:31]() | None |
| **Fit** | Company Size (Enterprise) | +20 [skills/revops/references/scoring-models.md:14]() | None |
| **Engagement** | Demo Request | +30 [skills/revops/references/scoring-models.md:61]() | None |
| **Engagement** | Pricing Page Visit | +20 [skills/revops/references/scoring-models.md:62]() | -5 per week |
| **Negative** | Competitor Domain | -50 [skills/revops/references/scoring-models.md:109]() | Immediate |
| **Product (PLG)** | Invited Team Member | +25 [skills/revops/references/scoring-models.md:97]() | None |

Sources: [skills/revops/references/scoring-models.md:9-102](), [skills/revops/references/scoring-models.md:125-180]()

## Automated Routing Rules

Routing ensures that leads are delivered to the correct representative instantly. The system follows a "Specific-to-General" logic: it checks for named accounts first, then territories, and finally falls back to a round-robin distribution [skills/revops/SKILL.md:135-136]().

### Routing Logic Flow

This diagram bridges the high-level routing strategy to the implementation logic found in CRM workflows.

**Title: RevOps Routing Logic (Code Entity Space)**
```mermaid
flowchart TD
    ["New_Lead_Event"] --> ["Check_Named_Target_Account"]
    ["Check_Named_Target_Account"] -- "Match_Found" --> ["Route_to_Account_Owner"]
    ["Check_Named_Target_Account"] -- "No_Match" --> ["Check_Territory_Match"]
    
    ["Check_Territory_Match"] -- "Geo_Industry_Match" --> ["Route_to_Territory_Owner"]
    ["Check_Territory_Match"] -- "No_Match" --> ["Round_Robin_Dispatcher"]
    
    subgraph "CRM_Implementation_Logic"
        ["Round_Robin_Dispatcher"] --> ["Rotation_Counter_Property"]
        ["Rotation_Counter_Property"] --> ["Assign_Contact_Owner"]
        ["Assign_Contact_Owner"] --> ["Create_Follow_up_Task_with_SLA"]
    end
```
Sources: [skills/revops/SKILL.md:126-131](), [skills/revops/references/routing-rules.md:9-30](), [skills/revops/references/routing-rules.md:56-61]()

## Pipeline Velocity and SLAs

Pipeline velocity is heavily dependent on **Speed-to-Lead**. Response time is the single biggest factor in lead conversion; contacting within 5 minutes is 21x more likely to qualify [skills/revops/SKILL.md:142-143]().

### SLA Automation Playbook

To enforce these benchmarks, the RevOps system implements escalation recipes in tools like HubSpot or Salesforce:
1.  **Trigger:** Lifecycle Stage changed to MQL [skills/revops/references/routing-rules.md:50]().
2.  **Assignment:** Rotate contact owner among selected users [skills/revops/references/routing-rules.md:51]().
3.  **Tasking:** Create follow-up task with SLA deadline [skills/revops/references/routing-rules.md:61]().
4.  **Escalation:** If no activity logged in 15 min, alert backup rep [skills/revops/references/routing-rules.md:192]().
5.  **Reassignment:** If no activity in 60 min, reassign via round-robin [skills/revops/references/routing-rules.md:194]().

### Pipeline Stages

| Stage | Required Fields | Exit Criteria |
| :--- | :--- | :--- |
| **Discovery** | Pain points, Use case | Discovery call completed |
| **Validation** | Success criteria | Demo/POC successful |
| **Proposal** | Final pricing | Proposal sent |
| **Negotiation** | Legal/Security review | Contract sent |

Sources: [skills/revops/SKILL.md:157](), [skills/revops/references/routing-rules.md:186-194](), [skills/revops/references/automation-playbooks.md:7-32]()

## Data Hygiene and Tooling

RevOps maintains the integrity of the "Single Source of Truth" through automated data hygiene and integration architectures. This includes managing negative scoring for competitors and job-seekers to keep the pipeline clean [skills/revops/references/scoring-models.md:107-120]().

**Title: RevOps Data Flow Architecture**
```mermaid
graph LR
    ["Marketing_Automation_Platform"] -- "Sync_Contact_Properties" --> ["CRM_System_of_Record"]
    ["Product_Usage_Data"] -- "Implicit_Scoring_Signals" --> ["CRM_System_of_Record"]
    ["Enrichment_Tools_Clay_Clearbit"] -- "Explicit_Fit_Data" --> ["CRM_System_of_Record"]
    
    subgraph "CRM_Workflow_Engine"
        ["Auto_MQL_on_Threshold"]
        ["SLA_Timer_and_Escalation"]
        ["Routing_Decision_Tree"]
    end
    
    ["CRM_System_of_Record"] -- "Alert_Notification" --> ["Sales_Rep_Push_Email"]
    ["CRM_System_of_Record"] -- "Task_Sync" --> ["Sales_Engagement_Platform"]
```
Sources: [skills/revops/SKILL.md:32-33](), [skills/revops/references/routing-rules.md:186-195](), [skills/revops/references/scoring-models.md:107-120](), [skills/revops/references/automation-playbooks.md:38-46]()

---

