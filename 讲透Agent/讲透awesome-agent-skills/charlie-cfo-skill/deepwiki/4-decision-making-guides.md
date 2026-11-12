<!-- source: DeepWiki mcp.deepwiki.com · repo EveryInc/charlie-cfo-skill · page 4 Decision-Making Guides · fetched 2026-10-26 -->

# Decision-Making Guides

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This section provides practical application guides for applying Charlie's five financial frameworks to common decisions facing bootstrapped startups. While the Core Philosophy ([Section 2](#2)) establishes the underlying principles and the Five Financial Frameworks ([Section 3](#3)) detail the calculation methods, this section focuses on **how to use those frameworks to make actual decisions**.

Each decision type covered here follows a structured process that combines:
- Quantitative analysis using formulas from [references/metrics-benchmarks.md:1-end]()
- Threshold validation against targets defined in [SKILL.md:14-25]()
- Contextual guidance from case studies in [references/case-studies.md:1-end]()
- Multi-framework integration where decisions impact multiple areas

For detailed metric calculations and formulas, see [Metrics and Benchmarks Reference](#5.1). For real-world examples of how successful bootstrapped companies made similar decisions, see [Bootstrapped Company Case Studies](#5.2).

**Sources:** [SKILL.md:1-162](), [README.md:1-59]()

---

## Decision Framework Architecture

Charlie structures all financial decisions through a hierarchical framework system where certain frameworks act as **gates** that must be satisfied before others can be evaluated. This prevents optimization of secondary metrics while violating survival requirements.

### Decision Processing Hierarchy

```mermaid
graph TB
    subgraph "Input Layer"
        QUERY["User Decision Query<br/>(Natural Language)"]
        CONTEXT["Financial Context<br/>(Current metrics)"]
    end
    
    subgraph "Gate 1: Survival Requirements"
        UNIT_CHECK["Unit Economics Gate<br/>SKILL.md:14-18<br/>LTV:CAC ≥ 3:1<br/>Payback < 12 months"]
        CASH_CHECK["Cash Position Gate<br/>SKILL.md:29-33<br/>Runway ≥ 24 months<br/>Reserves sufficient"]
    end
    
    subgraph "Gate 2: Efficiency Validation"
        RPE_CHECK["Revenue Per Employee<br/>SKILL.md:20-25<br/>Benchmark comparison"]
        BURN_CHECK["Burn Multiple<br/>SKILL.md:42-47<br/>Target < 1.5x"]
    end
    
    subgraph "Gate 3: Strategic Evaluation"
        PAYBACK["Payback Period Analysis<br/>SKILL.md:51<br/>Target < 12 months"]
        RULE40["Rule of 40 Assessment<br/>SKILL.md:53-57<br/>Growth + Margin ≥ 40%"]
    end
    
    subgraph "Output Layer"
        DECISION["Structured Decision Output<br/>- Quantitative analysis<br/>- Recommendation<br/>- Case study examples<br/>- Risk warnings"]
    end
    
    QUERY --> UNIT_CHECK
    CONTEXT --> UNIT_CHECK
    
    UNIT_CHECK -->|"PASS"| CASH_CHECK
    UNIT_CHECK -->|"FAIL"| REJECT["Reject Decision<br/>Death spiral risk"]
    
    CASH_CHECK -->|"PASS"| RPE_CHECK
    CASH_CHECK -->|"FAIL"| DEFER["Defer Decision<br/>Insufficient runway"]
    
    RPE_CHECK --> BURN_CHECK
    BURN_CHECK --> PAYBACK
    PAYBACK --> RULE40
    
    RULE40 --> DECISION
    REJECT --> DECISION
    DEFER --> DECISION
```

**Sources:** [SKILL.md:14-67]()

### Framework Integration Matrix

Different decision types activate different combinations of frameworks. This table maps decision categories to the frameworks that evaluate them:

| Decision Type | Primary Framework | Secondary Frameworks | Validation Source | Typical Query |
|--------------|-------------------|---------------------|-------------------|---------------|
| **Hiring** | Capital Allocation ([SKILL.md:59-66]()) | Cash Management, Unit Economics | [SKILL.md:59-66]() | "Should we make this hire?" |
| **Tool/Software Purchase** | Capital Allocation ([SKILL.md:51]()) | Working Capital | [SKILL.md:51]() | "Should we buy this tool?" |
| **Marketing Spend** | Unit Economics ([SKILL.md:14-18]()) | Capital Allocation | [SKILL.md:14-18]() | "Should we increase ad spend?" |
| **Pricing Change** | Unit Economics ([SKILL.md:14-18]()) | Forecasting, Cash | [references/metrics-benchmarks.md]() | "Should we raise prices?" |
| **Payment Terms** | Working Capital ([SKILL.md:69-90]()) | Cash Management | [SKILL.md:82-89]() | "Should we offer prepay discounts?" |
| **Strategic Investment** | Capital Allocation ([SKILL.md:51]()) | All frameworks | [SKILL.md:49-67]() | "Should we build this feature?" |

**Sources:** [SKILL.md:49-90](), [references/metrics-benchmarks.md:1-end]()

---

## The Four-Phase Decision Process

Every decision in Charlie follows a standardized four-phase process that ensures consistency and completeness:

### Phase 1: Context Gathering

```mermaid
graph LR
    subgraph "Current State Metrics"
        REVENUE["Current ARR/MRR<br/>references/metrics-benchmarks.md"]
        RUNWAY["Current Runway<br/>SKILL.md:29-33"]
        UNIT_METRICS["Unit Economics<br/>LTV, CAC, Payback<br/>SKILL.md:14-18"]
        BURN["Burn Rate<br/>SKILL.md:42-47"]
    end
    
    subgraph "Decision Specifics"
        COST["Direct Cost<br/>$ amount"]
        TIMING["Time to Value<br/>Payback period"]
        REVENUE_IMPACT["Revenue Impact<br/>Direct or indirect"]
        ALTERNATIVES["Opportunity Cost<br/>What else could $ fund"]
    end
    
    REVENUE --> ANALYSIS["Context Analysis<br/>Complete financial picture"]
    RUNWAY --> ANALYSIS
    UNIT_METRICS --> ANALYSIS
    BURN --> ANALYSIS
    
    COST --> ANALYSIS
    TIMING --> ANALYSIS
    REVENUE_IMPACT --> ANALYSIS
    ALTERNATIVES --> ANALYSIS
```

**Sources:** [SKILL.md:29-47](), [references/metrics-benchmarks.md:1-end]()

### Phase 2: Threshold Validation

This phase checks the decision against hard thresholds defined in [SKILL.md:14-25](). Violations trigger automatic warnings:

| Threshold Type | Source | Target | Violation Response |
|----------------|--------|--------|-------------------|
| **LTV:CAC Ratio** | [SKILL.md:16]() | ≥ 3:1 | Reject if < 3:1 (death spiral warning) |
| **CAC Payback** | [SKILL.md:17]() | < 12 months | Reject if ≥ 12 months |
| **Runway** | [SKILL.md:31]() | ≥ 24 months | Defer if < 24 months post-decision |
| **Payback Period** | [SKILL.md:51]() | < 12 months | Reject if ≥ 12 months |
| **Burn Multiple** | [SKILL.md:42-46]() | < 1.5x | Warning if > 1.5x |
| **Customer Concentration** | [SKILL.md:121]() | < 10% per customer | Warning if ≥ 10% |

**Sources:** [SKILL.md:14-67](), [SKILL.md:121]()

### Phase 3: Multi-Framework Impact Analysis

```mermaid
graph TB
    DECISION_INPUT["Decision Input<br/>(e.g., hire for $120K)"]
    
    subgraph "Framework Impact Calculations"
        CASH_IMPACT["Cash Management Impact<br/>SKILL.md:27-47<br/>- New burn rate<br/>- Updated runway<br/>- Reserve adequacy"]
        
        UNIT_IMPACT["Unit Economics Impact<br/>SKILL.md:14-18<br/>- CAC impact<br/>- LTV impact<br/>- Margin impact"]
        
        CAP_IMPACT["Capital Allocation Impact<br/>SKILL.md:49-67<br/>- ROI calculation<br/>- Payback period<br/>- Rule of 40 impact"]
        
        WORK_IMPACT["Working Capital Impact<br/>SKILL.md:69-90<br/>- Cash conversion cycle<br/>- DSO/DPO changes"]
        
        FORECAST_IMPACT["Forecasting Impact<br/>SKILL.md:123-145<br/>- Driver changes<br/>- Scenario updates<br/>- 13-week cash impact"]
    end
    
    DECISION_INPUT --> CASH_IMPACT
    DECISION_INPUT --> UNIT_IMPACT
    DECISION_INPUT --> CAP_IMPACT
    DECISION_INPUT --> WORK_IMPACT
    DECISION_INPUT --> FORECAST_IMPACT
    
    CASH_IMPACT --> SYNTHESIS["Impact Synthesis<br/>Aggregate effects"]
    UNIT_IMPACT --> SYNTHESIS
    CAP_IMPACT --> SYNTHESIS
    WORK_IMPACT --> SYNTHESIS
    FORECAST_IMPACT --> SYNTHESIS
```

**Sources:** [SKILL.md:14-145]()

### Phase 4: Recommendation Generation

The final phase combines quantitative analysis with qualitative context:

1. **Quantitative Summary**: Calculated impacts on key metrics
2. **Threshold Status**: Pass/fail on each validation gate
3. **Case Study Context**: Relevant examples from [references/case-studies.md:1-end]()
4. **Recommendation**: Approve / Approve with conditions / Defer / Reject
5. **Follow-up Actions**: Specific next steps based on decision outcome

**Sources:** [SKILL.md:1-162](), [references/case-studies.md:1-end]()

---

## Decision Type Coverage

This section covers four major decision categories, each detailed in its own subsection:

### Hiring Decisions ([Section 4.1](#4.1))

Evaluates personnel additions through a four-question framework defined in [SKILL.md:59-66]():
- Direct revenue contribution assessment
- Time-to-productivity calculation
- Opportunity cost analysis
- Team productivity multiplier effects

Applies constraints from [SKILL.md:66](): never grow a department >50% at once.

### Investment and Spending Decisions ([Section 4.2](#4.2))

Evaluates any capital expenditure using the <12 month payback rule from [SKILL.md:51](). Covers:
- Software/tool purchases
- Marketing campaigns
- Product development investments
- Strategic initiatives

### Financial Review Rhythms ([Section 4.3](#4.3))

Establishes the review cadences defined in [SKILL.md:92-111]():
- **Weekly (60-90 min)**: Cash, AR, pipeline, revenue
- **Monthly**: Full close, variance analysis, forecast updates
- **Quarterly**: Strategic recalibration, scenario refresh

### Key Metrics Dashboard ([Section 4.4](#4.4))

Implements the monitoring dashboard from [SKILL.md:112-122]() covering:
- Revenue metrics (MRR/ARR, growth, NRR)
- Unit economics (LTV:CAC, payback, margins)
- Cash metrics (burn, runway, operating cash flow)
- Customer health (churn, concentration)

**Sources:** [SKILL.md:59-122]()

---

## Reference Material Integration

Charlie integrates two reference documents into every decision:

### Quantitative References

[references/metrics-benchmarks.md:1-end]() provides:
- **Calculation formulas** for all metrics
- **Industry benchmarks** by company stage
- **Performance targets** for validation
- **Spending allocation guidelines** by ARR level

These are used in Phase 2 (Threshold Validation) and Phase 3 (Multi-Framework Impact Analysis).

### Qualitative References

[references/case-studies.md:1-end]() provides:
- **Mailchimp**: Freemium pivot, viral loops, <$100 CAC
- **Zapier**: Programmatic SEO, near-zero CAC, "hire when it hurts"
- **Basecamp**: Profit distributions, $1.4M revenue per employee
- **ConvertKit**: Crisis turnaround, 51% margin in 5 months
- **Zoho**: 60% to R&D, zero advertising, vertical integration

These are used in Phase 4 (Recommendation Generation) to provide context and proven patterns.

**Sources:** [SKILL.md:159-161](), [references/metrics-benchmarks.md:1-end](), [references/case-studies.md:1-end]()

---

## Decision Flow Example: Hire Evaluation

The following diagram illustrates how a typical hiring decision flows through all four phases:

```mermaid
sequenceDiagram
    participant User
    participant Charlie
    participant UnitEconFramework as "Unit Economics<br/>Framework<br/>SKILL.md:14-18"
    participant CashFramework as "Cash Management<br/>Framework<br/>SKILL.md:27-47"
    participant CapAllocFramework as "Capital Allocation<br/>Framework<br/>SKILL.md:49-67"
    participant MetricsBenchmarks as "references/<br/>metrics-benchmarks.md"
    participant CaseStudies as "references/<br/>case-studies.md"
    
    User->>Charlie: "Should we hire a sales rep<br/>for $120K + $30K variable?"
    
    Note over Charlie: Phase 1: Context Gathering
    Charlie->>User: Request current metrics
    User->>Charlie: ARR $3M, runway 28 months,<br/>LTV:CAC 4:1, payback 8 months
    
    Note over Charlie: Phase 2: Threshold Validation
    Charlie->>UnitEconFramework: Check unit economics gates
    UnitEconFramework-->>Charlie: PASS (LTV:CAC 4:1 > 3:1,<br/>payback 8mo < 12mo)
    
    Charlie->>CashFramework: Check runway post-hire
    CashFramework-->>Charlie: New runway = 24.5 months<br/>WARNING (near minimum threshold)
    
    Note over Charlie: Phase 3: Multi-Framework Impact
    Charlie->>CapAllocFramework: Calculate hiring ROI
    CapAllocFramework->>MetricsBenchmarks: Get sales productivity benchmarks
    MetricsBenchmarks-->>CapAllocFramework: Sales rep: $500K-$700K ARR target<br/>Ramp time: 3-6 months
    CapAllocFramework-->>Charlie: Expected payback: 4-5 months<br/>ROI: 3.3x-4.7x annual
    
    Charlie->>CashFramework: Calculate burn impact
    CashFramework-->>Charlie: Burn increases $150K/year<br/>Runway drops to 24.5 months
    
    Note over Charlie: Phase 4: Recommendation Generation
    Charlie->>CaseStudies: Retrieve hiring examples
    CaseStudies-->>Charlie: Zapier: "hire when it hurts"<br/>Basecamp: 52 people at $100M ARR
    
    Charlie-->>User: RECOMMENDATION: Approve with conditions<br/>✓ ROI analysis: 4-5 month payback<br/>⚠ Runway warning: drops to 24.5mo<br/>📋 Context: Zapier hired conservatively<br/>📌 Actions: Accelerate ramp plan,<br/>    defer next hire until runway > 26mo
```

**Sources:** [SKILL.md:14-67](), [references/metrics-benchmarks.md:1-end](), [references/case-studies.md:1-end]()

---

## Common Decision Patterns

Through analysis of the case studies in [references/case-studies.md:1-end](), several recurring decision patterns emerge:

### Pattern 1: Conservative Hiring (Zapier Model)

- **Trigger**: "Hire when it hurts" - wait until pain is obvious
- **Validation**: LTV:CAC ≥ 3:1, payback < 12 months ([SKILL.md:16-17]())
- **Constraint**: Maintain 24-36 month runway ([SKILL.md:31]())
- **Case**: Zapier grew to $5B valuation with minimal team

### Pattern 2: Profit Distribution (Basecamp/ConvertKit Model)

- **Trigger**: Annual profitability achieved
- **Validation**: Operating reserves 3-6 months ([SKILL.md:38]())
- **Constraint**: Never distribute more than 50% of annual profit
- **Case**: Basecamp distributed profits for 20+ years, ConvertKit implemented after turnaround

### Pattern 3: Product-Led CAC Reduction (Mailchimp/Zapier Model)

- **Trigger**: CAC payback > 9 months
- **Strategy**: Invest in product virality, SEO, free tier
- **Target**: CAC < $100 ([references/case-studies.md]())
- **Case**: Mailchimp's freemium, Zapier's programmatic SEO

### Pattern 4: Crisis Response (ConvertKit Model)

- **Trigger**: Runway < 12 months
- **Response**: 
  1. Immediate cost cuts to reach profitability
  2. Focus on direct sales (higher margins)
  3. Defer all growth investments
- **Target**: 51% margin within 5 months ([references/case-studies.md]())
- **Case**: ConvertKit's 2017 turnaround

**Sources:** [references/case-studies.md:1-end](), [SKILL.md:14-47]()

---

## Decision Output Format

All Charlie decisions follow a standardized output structure:

```
DECISION ANALYSIS: [Decision Type]

CURRENT STATE
├─ Revenue: $X ARR/MRR
├─ Unit Economics: LTV:CAC X:1, Payback X months
├─ Cash Position: X months runway, $X reserves
└─ Burn Rate: $X/month (Burn Multiple: X.Xx)

THRESHOLD VALIDATION
├─ Unit Economics Gate: [PASS/FAIL] (details)
├─ Cash Position Gate: [PASS/FAIL/WARNING] (details)
├─ Payback Period: [PASS/FAIL] (X months vs 12 month target)
└─ Revenue Per Employee: [details vs benchmark]

MULTI-FRAMEWORK IMPACT
├─ Cash Impact: New burn $X/mo, runway drops to X months
├─ Unit Economics Impact: [CAC/LTV/margin changes]
├─ Capital Allocation: ROI X.Xx, payback X months
└─ Rule of 40: [current] → [new] (growth + margin)

CASE STUDY CONTEXT
[1-2 relevant examples from references/case-studies.md]

RECOMMENDATION: [APPROVE / APPROVE WITH CONDITIONS / DEFER / REJECT]

RATIONALE
[2-3 sentence explanation tying metrics to philosophy]

FOLLOW-UP ACTIONS
1. [Specific action item]
2. [Specific action item]
3. [Monitoring requirement]
```

**Sources:** [SKILL.md:1-162]()

---

## Navigation

- **[4.1 Evaluating Hiring Decisions](#4.1)**: Four-question hiring framework with ROI calculation
- **[4.2 Investment and Spending Decisions](#4.2)**: <12 month payback rule application
- **[4.3 Financial Review Rhythms](#4.3)**: Weekly, monthly, quarterly review processes
- **[4.4 Key Metrics Dashboard](#4.4)**: Complete monitoring dashboard with targets

For the underlying frameworks these decisions apply, see [The Five Financial Frameworks](#3).

**Sources:** [SKILL.md:1-162]()

---

