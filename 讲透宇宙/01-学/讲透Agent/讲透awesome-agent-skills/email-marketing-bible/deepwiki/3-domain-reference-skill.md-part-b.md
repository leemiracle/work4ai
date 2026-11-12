<!-- source: DeepWiki mcp.deepwiki.com · repo CosmoBlk/email-marketing-bible · page 3 Domain Reference (SKILL.md Part B) · fetched 2026-10-26 -->

# Domain Reference (SKILL.md Part B)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)
- [skills/email-marketing-bible/SKILL.md](skills/email-marketing-bible/SKILL.md)

</details>



This page serves as an overview of Part B of the agent skill reference, which provides data-backed domain reference material for AI agents and marketers. While Part A establishes the operating manual and safety gates (`[SKILL.md:24-34]`), Part B governs the core data models, benchmark thresholds, lifecycle flow recipes, compliance standards, and vertical playbooks used when executing campaigns through an ESP or connector (`[SKILL.md:4-8]`). 

As a parent page, this section outlines the major thematic pillars of the domain reference. For comprehensive breakdowns, consult the respective child pages linked below.

Sources: `[SKILL.md:1-20]`, `[skills/email-marketing-bible/SKILL.md:1-20]()`

---

## 3.1. Metrics, Flows and Segmentation

The metrics and lifecycle architecture govern how agent-driven campaigns measure success and automate customer journeys. Core performance indicators include open rates, click-through rates, revenue per recipient (RPR), complaint rates (hard-capped under 0.1%), and unsubscription velocity (`[SKILL.md:31]`). Lifecycle flows—such as the welcome series, abandoned cart, post-purchase cross-sell, and win-back sequences—rely on event triggers and audience segmentation rules to deliver contextual messaging.

To prevent list degradation, agents must enforce strict sunset policies that automatically identify, suppress, or re-engage unengaged subscribers after specific inactivity windows (typically 90 to 180 days). AI agents coordinate these segmentation tasks via intent routing based on read access and recent campaign metrics (`[SKILL.md:40-41]`).

For detailed recipes, benchmarks, and lifecycle flow logic, see [Metrics, Flows and Segmentation](#3.1).

```mermaid
graph TD
    "TaskRouter"["TaskRouter"] --> "AuditProgramme"["AuditProgramme"]
    "TaskRouter" --> "BuildFlow"["BuildFlow"]
    "AuditProgramme" --> "ReadState"["ReadState"]
    "BuildFlow" --> "TriggerEngine"["TriggerEngine"]
    "TriggerEngine" --> "WelcomeFlow"["WelcomeFlow"]
    "TriggerEngine" --> "CartFlow"["CartFlow"]
    "TriggerEngine" --> "WinBackFlow"["WinBackFlow"]

    subclass "TaskRouter" skillEntity
```
*Figure 1: Task Router mapping intents to lifecycle flow automation.*

Sources: `[SKILL.md:36-41]`, `[skills/email-marketing-bible/SKILL.md:36-41]()`

---

## 3.2. Deliverability and Authentication

Deliverability forms the foundational boundary of all outbound messaging. Technical authentication requires strict alignment across Sender Policy Framework (SPF), DomainKeys Identified Mail (DKIM), and Domain-based Message Authentication, Reporting, and Conformance (DMARC) set to `p=quarantine` or `p=reject` policies (`[SKILL.md:86]`). Major inbox providers like Microsoft Outlook enforce strict multi-protocol validation for high-volume senders exceeding 5,000 emails per day (`[SKILL.md:86]`).

Agents handling deliverability must continuously monitor complaint and bounce thresholds, handle Apple Mail Privacy Protection (MPP) inflation of open rates, and execute rapid triage procedures when domain reputation dips or spam-trap hits occur (`[SKILL.md:43]`).

For authentication setup guides, complaint mitigation, and triage runbooks, see [Deliverability and Authentication](#3.2).

```mermaid
graph TD
    "AgentDeliverabilityCheck"["AgentDeliverabilityCheck"] --> "VerifySPF"["VerifySPF"]
    "AgentDeliverabilityCheck" --> "VerifyDKIM"["VerifyDKIM"]
    "AgentDeliverabilityCheck" --> "VerifyDMARC"["VerifyDMARC"]
    "VerifyDMARC" --> "EvaluateThresholds"["EvaluateThresholds"]
    "EvaluateThresholds" --> "BlockSend"["BlockSend"]

    subclass "AgentDeliverabilityCheck" skillEntity
```
*Figure 2: Deliverability validation pipeline enforcing safety checks prior to dispatch.*

Sources: `[SKILL.md:43]`, `[SKILL.md:86]`, `[skills/email-marketing-bible/SKILL.md:43]`, `[skills/email-marketing-bible/SKILL.md:86]`

---

## 3.3. Compliance and Consent

Regulatory frameworks dictate strict legal boundaries for automated and manual communications. Agents must enforce compliance across CAN-SPAM, GDPR, CASL, the Australian Spam Act, and CCPA. A critical technical requirement for all commercial email is support for RFC 8058 one-click list-unsubscribe headers alongside a verified physical mailing address in the footer (`[SKILL.md:87]`).

Consent rules vary significantly by channel and jurisdiction, requiring explicit opt-in mechanisms, auditable timestamp collection, and honor-bound suppression lists that immediately propagate opt-out requests across all synced platforms.

For deep-dive compliance matrices and RFC 8058 technical specs, see [Compliance and Consent](#3.3).

Sources: `[SKILL.md:87]`, `[skills/email-marketing-bible/SKILL.md:87]`

---

## 3.4. Multichannel Messaging and Cold Outbound

Beyond traditional email, modern outbound strategies integrate SMS, 10DLC (10-Digit Long Code) registration, WhatsApp Business API templates, and Rich Communication Services (RCS) messaging. Each channel carries strict constraints, including mandatory TCPA quiet hours (e.g., local recipient time between 9:00 PM and 8:00 AM for SMS) (`[SKILL.md:92]`), category-specific WhatsApp opt-in approvals, and strict carrier filtering rules.

Cold email outbound requires specialized infrastructure separate from marketing domains, including distinct sending domains, warming schedules, ideal customer profile (ICP) data hygiene, and controlled daily send volumes to protect domain reputation (`[SKILL.md:48]`).

For channel-specific configuration parameters, quiet-hour calculation logic, and cold-outbound playbooks, see [Multichannel Messaging and Cold Outbound](#3.4).

Sources: `[SKILL.md:48]`, `[SKILL.md:92]`, `[skills/email-marketing-bible/SKILL.md:48]`, `[skills/email-marketing-bible/SKILL.md:92]`

---

## 3.5. Platform Selection and Industry Playbooks

Choosing the correct Email Service Provider (ESP) or Customer Engagement Platform depends on list size, transactional requirements, budget, tech stack integration, and whether the platform supports agent-driven workflows via Model Context Protocol (MCP) or native connectors (`[SKILL.md:46]`). 

The skill reference supplies a comparative ESP evaluation matrix and 19 dedicated vertical playbooks (covering e-commerce, B2B SaaS, publishing, agency operations, and more) to tailor messaging cadences, content archetypes, and data flows to specific business models (`[SKILL.md:4-8]`).

For the complete ESP comparison matrix, MCP connection architectures, and vertical playbooks, see [Platform Selection and Industry Playbooks](#3.5).

Sources: `[SKILL.md:4-8]`, `[SKILL.md:46]`, `[skills/email-marketing-bible/SKILL.md:4-8]`, `[skills/email-marketing-bible/SKILL.md:46]`

---

