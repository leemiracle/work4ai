<!-- source: DeepWiki mcp.deepwiki.com · repo coreyhaines31/marketingskills · extra page Onboarding CRO · fetched 2026-10-26 -->

# Onboarding CRO

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [README.md](README.md)
- [VERSIONS.md](VERSIONS.md)

</details>



## Purpose and Scope

The `onboarding-cro` skill is a specialized knowledge module designed to optimize the post-signup experience. Its primary goal is to help users reach their "aha moment" — the point of value realization — as quickly as possible to establish long-term retention habits [skills/onboarding-cro/SKILL.md:8-10]().

This skill focuses on the **Activation** stage of the customer lifecycle [README.md:35](). It is distinct from `signup-flow-cro` (which handles the registration process itself) and `page-cro` (which optimizes marketing pages before a user signs up) [skills/onboarding-cro/SKILL.md:1-6](). It addresses common issues such as "users sign up but don't use the product" or "low activation rates" [skills/onboarding-cro/SKILL.md:3]().

**Sources:** [README.md:35](), [skills/onboarding-cro/SKILL.md:1-10](), [skills/onboarding-cro/SKILL.md:215-221]()

## Core Principles of Activation

The skill operates on four fundamental principles to drive user success:

1.  **Time-to-Value Is Everything**: Remove every unnecessary step between signup and experiencing core value [skills/onboarding-cro/SKILL.md:27-28]().
2.  **One Goal Per Session**: Focus the first session on a single successful outcome. Save advanced features for later [skills/onboarding-cro/SKILL.md:30-31]().
3.  **Do, Don't Show**: Prioritize interactive experiences over passive tutorials. Doing the thing is superior to learning about the thing [skills/onboarding-cro/SKILL.md:33-34]().
4.  **Progress Creates Motivation**: Use visual indicators to show advancement and celebrate completions to make the path visible [skills/onboarding-cro/SKILL.md:36-37]().

**Sources:** [skills/onboarding-cro/SKILL.md:25-39]()

## Technical Implementation Patterns

The skill defines several UI/UX patterns for implementing effective onboarding flows.

### 1. Onboarding Checklist Pattern
Used when products require multiple setup steps or have several features to discover, particularly for self-serve B2B products [skills/onboarding-cro/SKILL.md:78-84]().

*   **Constraints**: 3-7 items to avoid overwhelm [skills/onboarding-cro/SKILL.md:86]().
*   **Ordering**: Start with "quick wins" and order by increasing value/impact [skills/onboarding-cro/SKILL.md:87-88]().
*   **UI Elements**: Requires a progress bar or completion percentage, a celebration mechanic upon finishing, and a dismiss option [skills/onboarding-cro/SKILL.md:89-91]().

### 2. Empty State Optimization
Empty states are treated as onboarding opportunities rather than dead ends [skills/onboarding-cro/SKILL.md:93-95]().

| Element | Purpose |
| :--- | :--- |
| **Explanation** | Defines what the specific area is for [skills/onboarding-cro/SKILL.md:98](). |
| **Visualization** | Shows what the area looks like once populated with data [skills/onboarding-cro/SKILL.md:99](). |
| **Primary Action** | Provides a clear CTA to add the first item [skills/onboarding-cro/SKILL.md:100](). |
| **Sample Data** | Optionally pre-populates with example data to reduce friction [skills/onboarding-cro/SKILL.md:101](). |

### 3. Guided Tours and Tooltips
Best for complex UIs where features are not self-evident [skills/onboarding-cro/SKILL.md:103-105]().
*   **Limit**: Maximum 3-5 steps per tour [skills/onboarding-cro/SKILL.md:108]().
*   **Control**: Must be dismissible at any time and should not repeat for returning users [skills/onboarding-cro/SKILL.md:109-110]().

**Sources:** [skills/onboarding-cro/SKILL.md:78-112]()

## Data Flow and Measurement

The skill emphasizes a data-driven approach to identifying where users stall in the activation funnel.

### The Activation Funnel
This diagram bridges the natural language symptoms reported by users to the specific event-driven logic used to measure onboarding success.

**Activation Funnel Measurement Logic**
```mermaid
graph TD
    subgraph "Natural Language Space"
        [NL_SETUP_FAIL]["'Nobody completes setup'"]
        [NL_NOT_ACTIVATING]["'Users aren't activating'"]
    end

    subgraph "Code Entity Space: onboarding-cro / analytics-tracking"
        [SIGNUP_EV]["signup_completed"]
        [STEP1_EV]["onboarding_step_completed (Step 1)"]
        [STEP2_EV]["onboarding_step_completed (Step 2)"]
        [AHA_EV]["feature_used (Aha Moment)"]
        [RETENTION_EV]["day_30_retention"]
    end

    [NL_SETUP_FAIL] -->|Triggers| [SIGNUP_EV]
    [NL_NOT_ACTIVATING] -->|Analyzes| [AHA_EV]
    [SIGNUP_EV] -->|Drop-off?| [STEP1_EV]
    [STEP1_EV] -->|Drop-off?| [STEP2_EV]
    [STEP2_EV] -->|Goal| [AHA_EV]
    [AHA_EV] -->|Result| [RETENTION_EV]
```
**Sources:** [skills/onboarding-cro/SKILL.md:155-161](), [skills/analytics/SKILL.md:107-108]()

### Key Metrics Table
| Metric | Description | Source |
| :--- | :--- | :--- |
| **Activation Rate** | % of signups who reach the defined activation/aha event | [skills/onboarding-cro/SKILL.md:150]() |
| **Time to Activation** | How long it takes a user to reach their first value moment | [skills/onboarding-cro/SKILL.md:151]() |
| **Onboarding Completion** | % of users who finish the entire setup flow | [skills/onboarding-cro/SKILL.md:152]() |
| **Day 1/7/30 Retention** | Return rate of users by specific timeframe cohorts | [skills/onboarding-cro/SKILL.md:153]() |

**Sources:** [skills/onboarding-cro/SKILL.md:146-154]()

## System Integration and Skill Relationships

`onboarding-cro` acts as a central hub for activation, frequently referencing other skills to complete the user journey.

**Skill Orchestration for User Activation**
```mermaid
graph LR
    subgraph "Acquisition & Registration"
        [SF_SKILL]["signup-flow-cro"]
    end

    subgraph "Activation (onboarding-cro)"
        [CHECKLIST_PAT]["Checklist Pattern"]
        [EMPTY_STATE_PAT]["Empty State Logic"]
        [STALLED_REC]["Stalled User Recovery"]
    end

    subgraph "Support & Retention"
        [EMAIL_SKILL]["emails"]
        [PAYWALL_SKILL]["paywall-upgrade-cro"]
        [AB_SKILL]["ab-testing"]
        [ANALYTICS_SKILL]["analytics"]
    end

    [SF_SKILL] -->|Handoff| [CHECKLIST_PAT]
    [CHECKLIST_PAT] -->|Activation Achieved| [PAYWALL_SKILL]
    [STALLED_REC] -->|Re-engagement| [EMAIL_SKILL]
    [CHECKLIST_PAT] -.->|Experimentation| [AB_SKILL]
    [CHECKLIST_PAT] -.->|Measurement| [ANALYTICS_SKILL]
```
**Sources:** [skills/onboarding-cro/SKILL.md:215-221](), [README.md:27-50](), [VERSIONS.md:33-51]()

### Relationship Details
*   **`emails`**: Used for trigger-based emails like "Welcome" (immediate), "Incomplete Onboarding" (24h/72h), and "Activation Achieved" (celebration) [skills/onboarding-cro/SKILL.md:118-122]().
*   **`paywall-upgrade-cro`**: The next logical step after activation; users should experience value before being asked to upgrade [skills/onboarding-cro/SKILL.md:219]().
*   **`ab-testing`**: Used to test variations in flow simplification, step ordering, and progress mechanics [skills/onboarding-cro/SKILL.md:220]().
*   **`analytics`**: Provides the technical foundation for measuring `onboarding_step_completed` and `feature_used` events [skills/onboarding-cro/SKILL.md:218]().

**Sources:** [skills/onboarding-cro/SKILL.md:114-129](), [skills/onboarding-cro/SKILL.md:215-221](), [README.md:33-40]()

## Experimentation Framework

The skill provides a comprehensive library of experiment ideas to improve activation rates [skills/onboarding-cro/references/experiments.md:1-13]().

### Common Experiment Categories
*   **Flow Simplification**: Testing email verification timing (during vs. after onboarding) and pre-filled templates to accelerate setup [skills/onboarding-cro/references/experiments.md:17-27]().
*   **Progress & Motivation**: Testing progress bars, different checklist lengths (3-5 vs 5-7 items), and starting points (beginning at 20% vs 0%) [skills/onboarding-cro/references/experiments.md:40-50]().
*   **Personalization**: Role-based or goal-based onboarding paths to customize the experience by industry or use-case [skills/onboarding-cro/references/experiments.md:89-100]().
*   **Re-engagement**: Testing the timing of re-engagement emails and human outreach for high-value accounts [skills/onboarding-cro/references/experiments.md:188-200]().

**Sources:** [skills/onboarding-cro/references/experiments.md:1-210]()

---

