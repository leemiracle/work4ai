<!-- source: DeepWiki mcp.deepwiki.com · repo coreyhaines31/marketingskills · extra page Pricing Strategy · fetched 2026-10-27 -->

# Pricing Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/copywriting/SKILL.md](skills/copywriting/SKILL.md)
- [skills/launch/SKILL.md](skills/launch/SKILL.md)
- [skills/pricing/SKILL.md](skills/pricing/SKILL.md)
- [skills/sales-enablement/SKILL.md](skills/sales-enablement/SKILL.md)

</details>



## Purpose and Scope

This page documents the `pricing-strategy` skill, which provides expertise in SaaS pricing and monetization strategy. The skill guides users through pricing research, tier structure design, value metric selection, and price point optimization. It focuses on value-based pricing methodology and helps align pricing with customer willingness to pay. [skills/pricing/SKILL.md:8-10]()

For in-app upgrade moments and paywall optimization, see [Paywall & Upgrade CRO (4.2.4)](/skills/paywall-upgrade-cro/SKILL.md). For cancel flow discounting and save offers, see [Churn Prevention (4.3.1)](/skills/churn-prevention/SKILL.md). For public pricing page conversion optimization, see [Page CRO (4.2.1)](/skills/page-cro/SKILL.md). For the specific components of an offer (bonuses, guarantees, scarcity), see [Offer Design (4.3.3)](/skills/offers/SKILL.md). [skills/pricing/SKILL.md:3-3]()

---

## Skill Definition

The `pricing-strategy` skill is a markdown-based knowledge module that provides pricing expertise to AI agents. It does not execute code or make API calls; rather, it guides decision-making through frameworks, research methods, and best practices.

**Skill Location:** [skills/pricing/SKILL.md:1-230]()

**Trigger Phrases:** The skill activates when users mention terms like `"pricing,"` `"pricing tiers,"` `"freemium,"` `"free trial,"` `"packaging,"` `"price increase,"` `"value metric,"` `"Van Westendorp,"` `"willingness to pay,"` or `"monetization."` [skills/pricing/SKILL.md:3-3]()

**Primary Outputs:**
- Pricing research methodology recommendations.
- Tier structure designs with feature-to-plan mappings.
- Value metric selection guidance.
- Price point recommendations based on competitive analysis.
- Pricing page structure and copy principles.

Sources: [skills/pricing/SKILL.md:1-10]()

---

## Architecture Context

### Position in Skill Hierarchy

The `pricing-strategy` skill sits in the **Retention & Monetization** category within the Skills Layer. It coordinates with multiple skills across the customer lifecycle:

**System Relationship Diagram**

```mermaid
graph TB
    subgraph "Conversion_Stage"
        PAGECRO["page-cro (4.2.1)<br/>Public pricing page optimization"]
        PAYWALL["paywall-upgrade-cro (4.2.4)<br/>In-app upgrade moments"]
        PRICING["pricing (4.3.2)<br/>Tier structure & price points"]
        OFFERS["offers (4.3.3)<br/>Bonuses, Guarantees, Scarcity"]
    end
    
    subgraph "Retention_Stage"
        CHURN["churn-prevention (4.3.1)<br/>Cancel flow discounts<br/>Save offer pricing"]
    end
    
    subgraph "Strategy_Layer"
        MKTPSYCH["marketing-psychology (4.8.5)<br/>Pricing psychology principles"]
        COPYWRITING["copywriting (4.4.1)<br/>Pricing page copy"]
    end
    
    subgraph "Testing_Layer"
        ABTEST["ab-test-setup (4.7.2)<br/>Price change experiments"]
    end
    
    PRICING -->|"Informs"| PAGECRO
    PRICING -->|"Defines tiers for"| PAYWALL
    PRICING -->|"Sets discount bounds for"| CHURN
    OFFERS -->|"Wraps around"| PRICING
    MKTPSYCH -->|"Provides psychology for"| PRICING
    COPYWRITING -->|"Writes copy for"| PAGECRO
    PRICING -->|"Tests via"| ABTEST
    
    USER["User Request: 'pricing tiers'"]
    USER -->|"Triggers skills/pricing/SKILL.md"| PRICING
```

**Integration Points:**
- **Downstream:** Pricing structure informs `page-cro` for conversion optimization and `paywall-upgrade-cro` for in-app upgrade flows. [skills/pricing/SKILL.md:226-227]()
- **Coordination:** Works with `churn-prevention` to set discount boundaries and save offer limits. [skills/pricing/SKILL.md:225-225]()
- **Support:** Uses `marketing-psychology` for anchoring and framing principles. [skills/pricing/SKILL.md:228-228]()
- **Testing:** Leverages `ab-test-setup` for price change validation. [skills/pricing/SKILL.md:229-229]()

Sources: [skills/pricing/SKILL.md:223-230](), [skills/copywriting/SKILL.md:182-186]()

---

## Core Concepts

### The Three Pricing Axes

The skill organizes pricing decisions into three independent dimensions:

**Pricing Dimension Mapping**

```mermaid
graph LR
    DECISION["Pricing Decision"]
    
    DECISION --> PACKAGING["Axis 1: Packaging<br/>What's included at each tier?"]
    DECISION --> METRIC["Axis 2: Pricing Metric<br/>What do you charge for?"]
    DECISION --> PRICE["Axis 3: Price Point<br/>How much do you charge?"]
    
    PACKAGING --> PACKOUT["• Feature gates<br/>• Usage limits<br/>• Support level<br/>• Access controls"]
    METRIC --> METRICOUT["• Per user/seat<br/>• Per usage<br/>• Per feature<br/>• Flat fee"]
    PRICE --> PRICEOUT["• Dollar amounts<br/>• Perceived value<br/>• Competitive position"]
```

**Implementation Pattern:** The skill recommends addressing these axes sequentially:
1. **Packaging first:** Define features, limits, and support levels. [skills/pricing/SKILL.md:45-47]()
2. **Metric second:** Select how price scales with value (e.g., per user, per usage). [skills/pricing/SKILL.md:49-51]()
3. **Price point last:** Set actual dollar amounts based on perceived value vs. cost. [skills/pricing/SKILL.md:53-55]()

Sources: [skills/pricing/SKILL.md:41-56]()

---

### Value Metric Selection

The skill provides a decision framework for selecting the pricing metric, ensuring it scales as the customer grows. [skills/pricing/SKILL.md:76-80]()

| Metric Type | Logic Mapping | Best For | Example Products |
|-------------|---------------------------|----------|------------------|
| Per user/seat | `seats * price_per_seat` | Collaboration tools | Slack, Notion |
| Per usage | `units * unit_price` | Variable consumption | AWS, Twilio |
| Per feature | `base + addon_price` | Modular products | HubSpot add-ons |
| Per contact/record | `records * tier_price` | CRM, email tools | Mailchimp |
| Per transaction | `amount * fee_percentage` | Payments, marketplaces | Stripe |
| Flat fee | `fixed_price` | Simple products | Basecamp |

**Value Metric Decision Tree:**

```mermaid
graph TD
    START["Value Metric Selection"]
    
    START --> Q1{"Does value scale<br/>with team size?"}
    Q1 -->|"Yes"| PERSEAT["Per user/seat"]
    Q1 -->|"No"| Q2{"Does value scale<br/>with usage volume?"}
    
    Q2 -->|"Yes"| Q3{"Is usage<br/>predictable?"}
    Q3 -->|"Yes"| PERUSAGE["Per usage units"]
    Q3 -->|"No, highly variable"| PERUSAGE
    
    Q2 -->|"No"| Q4{"Modular product<br/>with add-ons?"}
    Q4 -->|"Yes"| PERFEATURE["Per feature/add-on"]
    Q4 -->|"No"| Q5{"Value tied to<br/>data size?"}
    
    Q5 -->|"Yes (contacts, records)"| PERRECORD["Per contact/record"]
    Q5 -->|"No"| Q6{"Processing<br/>transactions?"}
    
    Q6 -->|"Yes"| PERTX["Per transaction %"]
    Q6 -->|"No"| FLAT["Flat fee"]
```

**Key Validation Question:** "As a customer uses more of [metric], do they get more value?" If no, the metric doesn't align with value. [skills/pricing/SKILL.md:95-98]()

Sources: [skills/pricing/SKILL.md:72-98]()

---

### Tier Structure Framework

The skill implements a **Good-Better-Best** packaging model to differentiate tiers via feature gating, usage limits, and support levels. [skills/pricing/SKILL.md:103-115]()

**Tier Architecture Diagram**

```mermaid
graph TB
    subgraph "Tier_Differentiation_Layers"
        FEATURES["Feature Gating Layer"]
        LIMITS["Usage Limits Layer"]
        SUPPORT["Support Level Layer"]
        ACCESS["Access Control Layer"]
    end
    
    subgraph "Good_Tier_Entry"
        G_FEAT["Core features only"]
        G_LIMIT["Restrictive limits"]
        G_SUPP["Email support"]
        G_ACCESS["Basic access"]
    end
    
    subgraph "Better_Tier_Anchor"
        B_FEAT["Full feature set"]
        B_LIMIT["Reasonable limits"]
        B_SUPP["Priority support"]
        B_ACCESS["Standard access"]
    end
    
    subgraph "Best_Tier_Premium"
        P_FEAT["Everything + advanced"]
        P_LIMIT["Unlimited/high limits"]
        P_SUPP["Dedicated support"]
        P_ACCESS["SSO, API, custom"]
    end
    
    FEATURES --> G_FEAT
    FEATURES --> B_FEAT
    FEATURES --> P_FEAT
    
    LIMITS --> G_LIMIT
    LIMITS --> B_LIMIT
    LIMITS --> P_LIMIT
    
    SUPPORT --> G_SUPP
    SUPPORT --> B_SUPP
    SUPPORT --> P_SUPP
    
    ACCESS --> G_ACCESS
    ACCESS --> B_ACCESS
    ACCESS --> P_ACCESS
```

**Tier Design Principles:**
- **Good tier:** Entry level with core features and limited usage. [skills/pricing/SKILL.md:105-105]()
- **Better tier:** Recommended "anchor" price with full features and reasonable limits. [skills/pricing/SKILL.md:106-106]()
- **Best tier:** Premium offering with advanced features, typically 2-3x the price of the Better tier. [skills/pricing/SKILL.md:107-107]()

Sources: [skills/pricing/SKILL.md:101-117]()

---

## Pricing Research Methods

### Van Westendorp Price Sensitivity Meter

The skill references the Van Westendorp method for identifying acceptable price ranges via four specific questions. [skills/pricing/SKILL.md:122-130]()

| Question | Purpose |
|----------|---------|
| "Too expensive (wouldn't consider)" | Identify the absolute ceiling where customers drop out. |
| "Too cheap (question quality)" | Identify the floor where customers doubt the product value. |
| "Expensive but might consider" | Identify the upper range of acceptable pricing. |
| "A bargain" | Identify the price point where customers feel they are getting high value. |

### MaxDiff Analysis

Used to identify which features customers value most by showing sets of features and asking for the "Most important" and "Least important." [skills/pricing/SKILL.md:132-137]() This informs how features should be gated across tiers. [skills/pricing/SKILL.md:137-137]()

Sources: [skills/pricing/SKILL.md:120-139]()

---

## Pricing Change Strategy

### Price Increase Implementation Patterns

The skill defines clear signals for when to raise prices (e.g., conversion > 40%, churn < 3%) and strategies for execution. [skills/pricing/SKILL.md:145-160]()

**Strategy Selection Logic**

```mermaid
graph LR
    INCREASE["Price Increase Decision"]
    
    INCREASE --> GRAND["Strategy 1: Grandfather<br/>New price for new customers only"]
    INCREASE --> DELAY["Strategy 2: Delayed Increase<br/>Announce 3-6 months out"]
    INCREASE --> VALUE["Strategy 3: Tied to Value<br/>Raise price + add features"]
    INCREASE --> RESTRUC["Strategy 4: Plan Restructure<br/>Change plans entirely"]
    
    GRAND --> IMPL1["Existing: Old price<br/>New: New price"]
    DELAY --> IMPL2["Month 0: Announce<br/>Month 3-6: Implement"]
    VALUE --> IMPL3["Before: $X, Y features<br/>After: $X+N, Y+M features"]
    RESTRUC --> IMPL4["Discontinue old plans<br/>Launch new tiers"]
```

**Implementation Strategies:**
- **Grandfathering:** Protect existing revenue while testing higher points on new cohorts. [skills/pricing/SKILL.md:163-163]()
- **Delayed Increase:** Provide a grace period to maintain trust. [skills/pricing/SKILL.md:164-164]()
- **Value-Tied:** Justify increases by adding significant new functionality. [skills/pricing/SKILL.md:165-165]()

Sources: [skills/pricing/SKILL.md:143-168]()

---

## Context Gathering Pattern

The skill implements a mandatory context-checking pattern to reduce repetitive questioning by reading the shared product context file. [skills/pricing/SKILL.md:12-15]()

**Agent Context Initialization Flow**

```mermaid
sequenceDiagram
    participant User
    participant Agent as "AI Agent"
    participant Skill as "skills/pricing/SKILL.md"
    participant PMC as ".agents/product-marketing.md"
    
    User->>Agent: "Help with pricing"
    Agent->>Skill: Load skill trigger
    Skill->>PMC: Read context if exists
    
    alt Context file exists
        PMC-->>Skill: Business Context, Value, Goals
        Skill->>Skill: Filter known info
        Skill->>User: Ask missing specific questions [skills/pricing/SKILL.md:214-219]
    else No context file
        Skill->>User: Ask full Business Context questions [skills/pricing/SKILL.md:19-38]
    end
    
    User-->>Skill: Provide details
    Skill->>Skill: Apply "The Three Pricing Axes" [skills/pricing/SKILL.md:43]
    Skill-->>Agent: Generate Pricing Recommendations
    Agent-->>User: Present Strategy
```

Sources: [skills/pricing/SKILL.md:12-38](), [skills/pricing/SKILL.md:212-220]()

---

