<!-- source: DeepWiki mcp.deepwiki.com · repo Paramchoudhary/ResumeSkills · page 5 End-to-End Workflows · fetched 2026-10-26 -->

# End-to-End Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document describes complete job search workflows that chain multiple skills together to accomplish complex, multi-stage tasks. Each workflow represents a real-world use case where skills are invoked in sequence, with outputs from one skill feeding into the next.

For individual skill documentation, see [Skills Reference](#4). For basic skill invocation mechanics, see [Skill Invocation and Execution](#3.3). For installation setup, see [Installation](#2.1).

---

## Workflow Architecture Overview

The ResumeSkills system organizes skills into four sequential workflow phases that mirror the job search lifecycle. Each phase contains multiple skills that can be invoked independently or chained together.

```mermaid
graph TD
    START["User starts<br/>job search"] --> PHASE1

    subgraph PHASE1["Phase 1: Resume Creation"]
        R1["resume-ats-optimizer.md"]
        R2["resume-bullet-writer.md"]
        R3["resume-quantifier.md"]
        R4["resume-formatter.md"]
        R5["resume-section-builder.md"]
        
        R1 --> R2
        R2 --> R3
        R3 --> R4
        R4 --> R5
    end

    subgraph PHASE2["Phase 2: Strategic Application"]
        J1["job-description-analyzer.md"]
        J2["resume-tailor.md"]
        J3["resume-version-manager.md"]
        
        J1 --> J2
        J2 --> J3
    end

    subgraph PHASE3["Phase 3: Supporting Documents"]
        S1["cover-letter-generator.md"]
        S2["linkedin-profile-optimizer.md"]
        S3["portfolio-case-study-writer.md"]
        S4["reference-list-builder.md"]
    end

    subgraph PHASE4["Phase 4: Interview & Offer"]
        I1["interview-prep-generator.md"]
        I2["salary-negotiation-prep.md"]
        I3["offer-comparison-analyzer.md"]
        
        I1 --> I2
        I2 --> I3
    end

    PHASE1 --> PHASE2
    PHASE2 --> PHASE3
    PHASE3 --> PHASE4
    PHASE4 --> END["Job offer<br/>accepted"]

    R5 -.->|"Optimized<br/>resume base"| J1
    J3 -.->|"Tailored<br/>versions"| S1
    J3 -.->|"Resume<br/>content"| S2
    R5 -.->|"Experience<br/>bullets"| S3
    S3 -.->|"Reference<br/>context"| S4
    J1 -.->|"Job<br/>requirements"| I1
    J3 -.->|"Resume<br/>context"| I1
```

**Workflow Phases:**

| Phase | Primary Goal | Skills Involved | Output |
|-------|--------------|-----------------|--------|
| Phase 1 | Create ATS-optimized base resume | 5 resume optimization skills | Polished master resume |
| Phase 2 | Analyze and tailor for specific jobs | 3 job search strategy skills | Customized resume versions |
| Phase 3 | Generate supporting materials | 4 document generation skills | Complete application package |
| Phase 4 | Prepare for interviews and negotiate | 3 interview/offer skills | Interview prep + negotiation plan |

**Sources:** [README.md:97-140](), [README.md:156-200]()

---

## Workflow 1: Resume Creation and Optimization Pipeline

This workflow transforms a basic resume into an ATS-optimized, achievement-focused document. Skills execute in sequence, with each step refining the output from the previous step.

### Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant Agent as "AI Agent"
    participant ATS as "resume-ats-optimizer.md"
    participant Bullet as "resume-bullet-writer.md"
    participant Quant as "resume-quantifier.md"
    participant Format as "resume-formatter.md"
    participant Section as "resume-section-builder.md"

    User->>Agent: "Optimize my resume [paste resume]"
    
    Agent->>ATS: Load skill
    ATS-->>Agent: Return instructions
    Agent->>Agent: Execute ATS compatibility check
    Agent-->>User: Compatibility score: 65%<br/>Issues: 8 found
    
    User->>Agent: "Fix these issues"
    Agent->>Bullet: Load skill
    Bullet-->>Agent: Return bullet-writing framework
    Agent->>Agent: Transform weak bullets
    Agent-->>User: Improved bullets with action verbs
    
    User->>Agent: "Add metrics to bullets"
    Agent->>Quant: Load skill
    Quant-->>Agent: Return quantification rules
    Agent->>Agent: Add numbers and percentages
    Agent-->>User: Quantified bullets
    
    User->>Agent: "Format for ATS"
    Agent->>Format: Load skill
    Format-->>Agent: Return formatting guidelines
    Agent->>Agent: Apply ATS-safe formatting
    Agent-->>User: Clean formatted resume
    
    User->>Agent: "Build targeted sections"
    Agent->>Section: Load skill
    Section-->>Agent: Return section templates
    Agent->>Agent: Optimize section order/content
    Agent-->>User: Final optimized resume
```

### Step-by-Step Breakdown

| Step | Skill File | User Prompt | Key Actions | Output |
|------|-----------|-------------|-------------|--------|
| 1 | `resume-ats-optimizer.md` | "Check ATS compatibility" | Parse resume, identify formatting issues, keyword gaps | ATS compatibility report with score |
| 2 | `resume-bullet-writer.md` | "Improve my bullets" | Identify weak bullets, apply achievement framework | Rewritten bullets with action verbs |
| 3 | `resume-quantifier.md` | "Add metrics" | Find quantification opportunities, estimate when needed | Bullets with numbers/percentages |
| 4 | `resume-formatter.md` | "Format for ATS" | Remove tables/columns, standardize fonts, clean spacing | ATS-compatible formatting |
| 5 | `resume-section-builder.md` | "Optimize sections" | Reorder sections, tailor to experience level | Properly structured resume |

### Invocation Patterns

**Pattern 1: Single Prompt Chain**
```
User: "Here's my resume [paste]. Optimize it completely for ATS, improve bullets, 
add metrics, and format it properly."

→ Agent automatically loads and chains:
  1. resume-ats-optimizer.md
  2. resume-bullet-writer.md  
  3. resume-quantifier.md
  4. resume-formatter.md
```

**Pattern 2: Iterative Refinement**
```
User: "Check ATS score"
→ Loads resume-ats-optimizer.md, returns score: 68%

User: "Fix the issues"  
→ Loads resume-bullet-writer.md + resume-formatter.md

User: "Now add metrics"
→ Loads resume-quantifier.md
```

### Data Flow Through Pipeline

```mermaid
flowchart LR
    INPUT["Raw Resume<br/>User provides"]
    
    subgraph OPTIMIZE["Optimization Pipeline"]
        direction TB
        STEP1["ATS Check<br/>resume-ats-optimizer.md<br/>Score + Issues"]
        STEP2["Bullet Rewrite<br/>resume-bullet-writer.md<br/>Action-focused"]
        STEP3["Add Metrics<br/>resume-quantifier.md<br/>Numbers added"]
        STEP4["Format Clean<br/>resume-formatter.md<br/>ATS-safe layout"]
        STEP5["Section Build<br/>resume-section-builder.md<br/>Optimized structure"]
        
        STEP1 --> STEP2
        STEP2 --> STEP3
        STEP3 --> STEP4
        STEP4 --> STEP5
    end
    
    OUTPUT["Optimized Resume<br/>Master version"]
    
    INPUT --> OPTIMIZE
    OPTIMIZE --> OUTPUT
    
    OUTPUT -.->|"Becomes input for"| NEXT["Phase 2:<br/>Job Tailoring"]
```

**Sources:** [README.md:111-116](), [README.md:163-174]()

---

## Workflow 2: Strategic Job Application Process

This workflow analyzes job postings, calculates match scores, and creates customized resume versions for high-fit opportunities.

### Decision Tree Workflow

```mermaid
graph TD
    START["User finds<br/>job posting"] --> ANALYZE

    ANALYZE["Invoke:<br/>job-description-analyzer.md"]
    ANALYZE --> SCORE{"Match<br/>Score?"}
    
    SCORE -->|"< 60%"| LOW["Low Match<br/>Red: Poor Fit"]
    SCORE -->|"60-75%"| MED["Medium Match<br/>Yellow: Possible"]
    SCORE -->|"> 75%"| HIGH["High Match<br/>Green: Apply"]
    
    LOW --> SKIP["Skip application<br/>Continue search"]
    
    MED --> GAPS["Review Gaps"]
    GAPS --> BRIDGE{"Can bridge<br/>gaps?"}
    BRIDGE -->|"No"| SKIP
    BRIDGE -->|"Yes"| TAILOR
    
    HIGH --> TAILOR["Invoke:<br/>resume-tailor.md"]
    
    TAILOR --> CUSTOM["Create customized<br/>resume version"]
    CUSTOM --> VERSION["Invoke:<br/>resume-version-manager.md"]
    
    VERSION --> TRACK["Track:<br/>- Job title<br/>- Company<br/>- Date<br/>- Customizations"]
    
    TRACK --> APPLY["Ready to<br/>apply"]
    
    SKIP --> END["End workflow"]
    APPLY --> END
```

### Skill Interaction Pattern

```mermaid
sequenceDiagram
    participant User
    participant JDA as "job-description-analyzer.md"
    participant Tailor as "resume-tailor.md"
    participant Version as "resume-version-manager.md"
    participant Storage as "Local Files"

    User->>JDA: "Analyze job: [paste JD]"
    Note over JDA: Parse requirements<br/>Calculate match score<br/>Identify gaps
    JDA-->>User: Match: 82%<br/>15 required (met: 13)<br/>8 preferred (met: 6)<br/>Gaps: Python, AWS

    User->>Tailor: "Tailor resume for this job"
    Note over Tailor: Load master resume<br/>Load JD analysis<br/>Identify relevant experience
    Tailor->>Tailor: Reorder bullets<br/>Add keywords<br/>Emphasize relevant skills
    Tailor-->>User: Customized resume

    User->>Version: "Save as 'Senior_Dev_Acme_2024'"
    Note over Version: Create metadata<br/>Store version<br/>Link to JD
    Version->>Storage: Write file:<br/>Senior_Dev_Acme_2024.pdf<br/>+ metadata.json
    Version-->>User: Saved version 47
```

### Match Score Calculation

The `job-description-analyzer.md` skill uses this scoring algorithm:

| Component | Weight | Calculation |
|-----------|--------|-------------|
| Required Skills Met | 70% | (Skills matched / Total required) × 0.70 |
| Preferred Skills Met | 20% | (Skills matched / Total preferred) × 0.20 |
| Experience Level | 10% | Match (1.0) or Partial (0.5) × 0.10 |

**Example Calculation:**
- Required: 13/15 met = 0.867 × 0.70 = 0.607
- Preferred: 6/8 met = 0.750 × 0.20 = 0.150
- Experience: Match = 1.000 × 0.10 = 0.100
- **Final Score: 85.7%**

### Version Tracking Structure

When `resume-version-manager.md` saves a version, it creates:

```
.resume-versions/
├── metadata.json
├── Senior_Dev_Acme_2024.pdf
├── Data_Scientist_Google_2024.pdf
└── PM_Microsoft_2024.pdf
```

**metadata.json structure:**
```json
{
  "versions": [
    {
      "id": 47,
      "filename": "Senior_Dev_Acme_2024.pdf",
      "job_title": "Senior Software Developer",
      "company": "Acme Corp",
      "date_created": "2024-01-15",
      "match_score": 82,
      "customizations": [
        "Added Python projects",
        "Emphasized AWS experience",
        "Reordered sections for backend focus"
      ],
      "job_url": "https://acme.com/careers/123"
    }
  ]
}
```

**Sources:** [README.md:118-122](), [README.md:176-187]()

---

## Workflow 3: Complete Application Package Assembly

This workflow generates all supporting documents needed for a complete application, using the tailored resume as the foundation.

### Parallel Document Generation

```mermaid
graph TB
    BASE["Tailored Resume<br/>From Phase 2"]
    JD["Job Description<br/>User provides"]
    
    subgraph PARALLEL["Parallel Generation"]
        COVER["cover-letter-generator.md"]
        LINKEDIN["linkedin-profile-optimizer.md"]
        PORTFOLIO["portfolio-case-study-writer.md"]
        REF["reference-list-builder.md"]
    end
    
    BASE --> COVER
    JD --> COVER
    BASE --> LINKEDIN
    BASE --> PORTFOLIO
    BASE --> REF
    
    COVER --> OUT1["Personalized<br/>cover letter"]
    LINKEDIN --> OUT2["LinkedIn<br/>profile updates"]
    PORTFOLIO --> OUT3["3-5 detailed<br/>case studies"]
    REF --> OUT4["Reference list<br/>+ prep notes"]
    
    OUT1 & OUT2 & OUT3 & OUT4 --> PACKAGE["Complete<br/>Application Package"]
```

### Document Generation Workflow

```mermaid
sequenceDiagram
    participant User
    participant Base as "Tailored Resume"
    participant Cover as "cover-letter-generator.md"
    participant LinkedIn as "linkedin-profile-optimizer.md"
    participant Portfolio as "portfolio-case-study-writer.md"
    participant Ref as "reference-list-builder.md"

    User->>Cover: "Write cover letter for this job"
    Note over Cover: Load resume + JD<br/>Extract key achievements<br/>Match to job requirements
    Cover-->>User: 3-paragraph cover letter<br/>with specific examples

    User->>LinkedIn: "Sync resume to LinkedIn"
    Note over LinkedIn: Extract headline formula<br/>Build About section<br/>Add keywords
    LinkedIn-->>User: LinkedIn profile sections:<br/>- Headline<br/>- About<br/>- Experience bullets

    User->>Portfolio: "Create case studies from resume"
    Note over Portfolio: Select top 3-5 bullets<br/>Expand to full stories<br/>Add problem/solution/results
    Portfolio-->>User: 3 detailed case studies:<br/>1200-1500 words each

    User->>Ref: "Build reference list"
    Note over Ref: Identify references<br/>Format properly<br/>Create prep notes
    Ref-->>User: Reference list + questions<br/>they might be asked
```

### Document Dependencies

| Output Document | Primary Input | Skills Used | Key Data Extracted |
|-----------------|---------------|-------------|-------------------|
| Cover Letter | Tailored resume + JD | `cover-letter-generator.md` | Top 3 achievements, company research, role requirements |
| LinkedIn Profile | Master/tailored resume | `linkedin-profile-optimizer.md` | Headline formula, keywords, experience bullets |
| Portfolio Case Studies | Master resume bullets | `portfolio-case-study-writer.md` | Individual bullet details, metrics, context |
| Reference List | Career history | `reference-list-builder.md` | Manager names, relationships, anticipated questions |

### Invocation Example

**Single Command Package Generation:**
```
User: "I'm applying to Senior PM at Google. Here's the JD [paste] and my 
tailored resume [paste]. Create the complete application package: cover letter, 
LinkedIn updates, case studies, and references."

→ Agent loads and executes in parallel:
  1. cover-letter-generator.md → 3-paragraph letter
  2. linkedin-profile-optimizer.md → Profile sections
  3. portfolio-case-study-writer.md → 3 case studies  
  4. reference-list-builder.md → Reference list

→ Returns all 4 documents in ~2 minutes
```

**Sources:** [README.md:124-128](), [README.md:188-200]()

---

## Workflow 4: Interview to Offer Acceptance

This workflow prepares for interviews, compares multiple offers, and builds negotiation strategies.

### Interview Preparation Flow

```mermaid
stateDiagram-v2
    [*] --> Interview_Scheduled
    
    Interview_Scheduled --> Load_Context
    
    state Load_Context {
        [*] --> Resume_Content
        [*] --> JD_Analysis
        [*] --> Company_Research
        
        Resume_Content --> Context_Ready
        JD_Analysis --> Context_Ready
        Company_Research --> Context_Ready
    }
    
    Context_Ready --> Generate_Prep
    
    state Generate_Prep {
        direction LR
        [*] --> STAR_Stories: "interview-prep-generator.md"
        STAR_Stories --> Questions: Predict questions
        Questions --> Talking_Points: Create talking points
        Talking_Points --> [*]
    }
    
    Generate_Prep --> Practice
    
    state Practice {
        [*] --> Mock_Answers
        Mock_Answers --> Weakness_Formula
        Weakness_Formula --> Questions_To_Ask
        Questions_To_Ask --> [*]
    }
    
    Practice --> Interview_Conducted
    
    Interview_Conducted --> Offer_Decision
    
    state Offer_Decision {
        [*] --> Got_Offer
        Got_Offer --> Multiple_Offers: > 1 offer?
        Multiple_Offers --> Compare_Yes: Yes
        Multiple_Offers --> Negotiate: No
        
        Compare_Yes --> Comparison: "offer-comparison-analyzer.md"
        Comparison --> Negotiate: Choose best
        
        Negotiate --> Prep_Negotiation: "salary-negotiation-prep.md"
        Prep_Negotiation --> [*]
    }
    
    Offer_Decision --> Accept_Offer
    Accept_Offer --> [*]
```

### Skill Chaining: Interview to Negotiation

```mermaid
sequenceDiagram
    participant User
    participant InterviewPrep as "interview-prep-generator.md"
    participant OfferCompare as "offer-comparison-analyzer.md"
    participant SalaryNeg as "salary-negotiation-prep.md"

    User->>InterviewPrep: "Interview at Acme for Senior Dev<br/>[resume + JD]"
    Note over InterviewPrep: Phase 1: Role Analysis<br/>- Parse JD requirements<br/>- Map to resume experience
    InterviewPrep-->>User: Core competencies: 8 identified

    Note over InterviewPrep: Phase 2: Story Banking<br/>- Extract STAR stories<br/>- Create 15 stories
    InterviewPrep-->>User: STAR Stories:<br/>- Leadership (3)<br/>- Technical (5)<br/>- Collaboration (4)<br/>- Problem-solving (3)

    Note over InterviewPrep: Phase 3: Mock Prep<br/>- Predict questions<br/>- Map stories to questions
    InterviewPrep-->>User: 25 predicted questions<br/>with story mappings

    Note over User: Interviews conducted<br/>Receives 2 offers

    User->>OfferCompare: "Compare offers:<br/>Acme: $150K + equity<br/>Beta: $140K + bonus"
    
    Note over OfferCompare: Calculate total comp:<br/>- Base salary<br/>- Equity value (4yr)<br/>- Bonus<br/>- Benefits
    OfferCompare-->>User: Total Comp:<br/>Acme: $182K<br/>Beta: $168K

    Note over OfferCompare: Score non-monetary:<br/>- Culture fit<br/>- Growth potential<br/>- Work-life balance
    OfferCompare-->>User: Weighted Score:<br/>Acme: 87/100<br/>Beta: 79/100

    User->>SalaryNeg: "Negotiate with Acme<br/>Target: $165K base"
    
    Note over SalaryNeg: Research market rates<br/>Build negotiation script<br/>Create counter-offer
    SalaryNeg-->>User: Negotiation Strategy:<br/>- Market data: $155-165K<br/>- Anchor at $165K<br/>- Walk-away: $152K<br/>- Script provided
```

### STAR Story Generation

The `interview-prep-generator.md` skill extracts stories from resume bullets using this structure:

**Input Bullet:**
```
"Led cross-functional team of 12 to migrate legacy monolith to microservices, 
reducing deployment time by 75% and improving system uptime to 99.99%"
```

**Generated STAR Story:**

| Component | Content |
|-----------|---------|
| **Situation** | Legacy monolith architecture causing slow deployments (4 hours) and frequent downtime (95% uptime). Business losing customers due to reliability issues. |
| **Task** | Assigned to lead migration to microservices while maintaining system stability for 1M+ active users. Budget: $500K, Timeline: 6 months. |
| **Action** | 1. Assembled cross-functional team (4 engineers, 2 QA, 3 DevOps, 3 PMs)<br/>2. Created phased migration plan with zero-downtime rollout<br/>3. Implemented feature flags for gradual traffic shifting<br/>4. Set up comprehensive monitoring and rollback procedures |
| **Result** | - Deployment time: 4 hours → 15 minutes (75% reduction)<br/>- System uptime: 95% → 99.99%<br/>- Customer churn: reduced by 40%<br/>- Team velocity: increased by 3x |

### Offer Comparison Matrix

The `offer-comparison-analyzer.md` skill generates comparison tables:

| Component | Acme Corp | Beta Inc | Gamma LLC |
|-----------|-----------|----------|-----------|
| **Base Salary** | $150,000 | $140,000 | $155,000 |
| **Equity (4yr)** | $120,000 (RSU) | $80,000 (Options) | $60,000 (RSU) |
| **Bonus** | 15% ($22,500) | 20% ($28,000) | 10% ($15,500) |
| **Benefits** | Premium + 401k match 6% | Standard + 401k match 4% | Premium + 401k match 5% |
| **Total Cash (Yr 1)** | $172,500 | $168,000 | $170,500 |
| **Total Comp (4yr)** | $182,500 | $178,000 | $177,500 |
| **PTO Days** | 25 | 20 | 30 |
| **Remote Policy** | Hybrid (3 days) | Full remote | Office required |
| **Growth Stage** | Series C | Public | Series B |
| **Weighted Score** | 87/100 | 79/100 | 82/100 |
| **Recommendation** | **Accept** | Decline | Counter |

**Sources:** [README.md:130-132](), [README.md:188-200]()

---

## Advanced Skill Chaining Patterns

### Pattern 1: Conditional Branching

Skills can create conditional workflows based on intermediate outputs:

```mermaid
graph TD
    START["User provides<br/>resume + JD"]
    
    JDA["job-description-analyzer.md<br/>Calculate match"]
    
    START --> JDA
    
    DECISION{"Match<br/>Score"}
    JDA --> DECISION
    
    DECISION -->|"> 75%"| TAILOR["resume-tailor.md<br/>Customize"]
    DECISION -->|"60-75%"| CHECK["Review gaps"]
    DECISION -->|"< 60%"| STOP["Don't apply"]
    
    CHECK --> GAP_DECISION{"Can close<br/>gaps?"}
    GAP_DECISION -->|"Yes"| TAILOR
    GAP_DECISION -->|"No"| STOP
    
    TAILOR --> MULTI["Determine<br/>application type"]
    
    MULTI --> TYPE{"Role<br/>Category?"}
    
    TYPE -->|"Technical"| TECH["tech-resume-optimizer.md"]
    TYPE -->|"Executive"| EXEC["executive-resume-writer.md"]
    TYPE -->|"Academic"| ACAD["academic-cv-builder.md"]
    TYPE -->|"Creative"| CREA["creative-portfolio-resume.md"]
    TYPE -->|"Career Change"| TRAN["career-changer-translator.md"]
    
    TECH & EXEC & ACAD & CREA & TRAN --> FINAL["Final<br/>customized resume"]
```

### Pattern 2: Iterative Refinement Loop

Users can iterate through optimization cycles until quality thresholds are met:

```mermaid
graph TD
    INPUT["Resume<br/>Draft v1"]
    
    subgraph LOOP["Optimization Loop"]
        ATS["resume-ats-optimizer.md<br/>Check score"]
        SCORE{"Score<br/>> 85%?"}
        FIX["resume-bullet-writer.md +<br/>resume-formatter.md<br/>Fix issues"]
        
        ATS --> SCORE
        SCORE -->|"No"| FIX
        FIX --> ATS
    end
    
    INPUT --> LOOP
    SCORE -->|"Yes"| QUANT["resume-quantifier.md<br/>Add metrics"]
    QUANT --> VALIDATE{"All bullets<br/>quantified?"}
    VALIDATE -->|"No"| QUANT
    VALIDATE -->|"Yes"| OUTPUT["Final<br/>Optimized Resume"]
```

### Pattern 3: Parallel Processing with Merge

Generate multiple documents in parallel, then combine:

```mermaid
graph TB
    BASE["Master Resume"]
    JD["Job Description"]
    
    subgraph PARALLEL["Parallel Execution"]
        P1["cover-letter-generator.md"]
        P2["linkedin-profile-optimizer.md"]
        P3["portfolio-case-study-writer.md"]
    end
    
    BASE --> P1 & P2 & P3
    JD --> P1
    
    P1 --> M1["Cover Letter"]
    P2 --> M2["LinkedIn Sections"]
    P3 --> M3["Case Studies"]
    
    M1 & M2 & M3 --> MERGE["Combine into<br/>Application Package"]
    
    MERGE --> REVIEW["User Review"]
    REVIEW --> DECISION{"Needs<br/>changes?"}
    DECISION -->|"Yes"| SELECT["Select document"]
    SELECT --> REVISE["Re-invoke specific skill"]
    REVISE --> MERGE
    DECISION -->|"No"| SUBMIT["Ready to Submit"]
```

### Pattern 4: Cross-Skill Data Passing

Later skills consume structured output from earlier skills:

```mermaid
sequenceDiagram
    participant User
    participant JDA as "job-description-analyzer.md"
    participant Tailor as "resume-tailor.md"
    participant Cover as "cover-letter-generator.md"
    participant Interview as "interview-prep-generator.md"

    User->>JDA: "Analyze job"
    Note over JDA: Output: Match data structure<br/>{<br/>  score: 82,<br/>  required_met: [list],<br/>  gaps: [list]<br/>}
    JDA-->>User: Analysis complete

    User->>Tailor: "Tailor resume using analysis"
    Note over Tailor: Consumes JDA output<br/>- Prioritizes required_met<br/>- Addresses gaps
    Tailor-->>User: Tailored resume

    User->>Cover: "Write cover letter"
    Note over Cover: Consumes:<br/>- Tailored resume<br/>- JDA match data<br/>Emphasizes top 3 matches
    Cover-->>User: Cover letter

    User->>Interview: "Prep for interview"
    Note over Interview: Consumes:<br/>- Tailored resume<br/>- JDA requirements<br/>Maps stories to requirements
    Interview-->>User: Interview prep
```

**Sources:** [README.md:88-107](), [README.md:156-200]()

---

## Workflow Decision Trees

### Should I Apply? Decision Tree

This decision tree shows how skills guide the application decision:

```mermaid
graph TD
    START["Found Job Posting"]
    
    ANALYZE["Run job-description-analyzer.md"]
    START --> ANALYZE
    
    SCORE{"Match<br/>Score?"}
    ANALYZE --> SCORE
    
    SCORE -->|"> 75%"| STRONG["Strong Match"]
    SCORE -->|"60-75%"| MEDIUM["Medium Match"]
    SCORE -->|"< 60%"| WEAK["Weak Match"]
    
    WEAK --> RED_FLAGS{"Red flags<br/>detected?"}
    RED_FLAGS -->|"Yes"| SKIP["Skip - Poor Fit"]
    RED_FLAGS -->|"No"| SKILL_GAP["Analyze gaps"]
    
    SKILL_GAP --> BRIDGE{"Can bridge<br/>gaps with<br/>current skills?"}
    BRIDGE -->|"No"| SKIP
    BRIDGE -->|"Yes"| MEDIUM
    
    MEDIUM --> REVIEW_GAPS["Review gaps:<br/>- 2+ critical gaps?<br/>- Misleading needed?"]
    REVIEW_GAPS --> GAP_CHECK{"Acceptable?"}
    GAP_CHECK -->|"No"| SKIP
    GAP_CHECK -->|"Yes"| STRONG
    
    STRONG --> COMPANY{"Company<br/>research<br/>positive?"}
    COMPANY -->|"No"| SKIP
    COMPANY -->|"Yes"| APPLY_DECISION["APPLY"]
    
    APPLY_DECISION --> TAILOR["Run resume-tailor.md"]
    TAILOR --> COVER["Run cover-letter-generator.md"]
    COVER --> SUBMIT["Submit Application"]
    
    SKIP --> CONTINUE["Continue Job Search"]
```

### Multi-Offer Evaluation Flowchart

When handling multiple offers, this workflow determines the best choice:

```mermaid
graph TD
    OFFERS["Received Multiple Offers"]
    
    COMPARE["Run offer-comparison-analyzer.md"]
    OFFERS --> COMPARE
    
    CALC["Calculate Total Compensation:<br/>Base + Equity + Bonus + Benefits"]
    COMPARE --> CALC
    
    NON_MONEY["Score Non-Monetary Factors:<br/>Culture, Growth, WLB, Impact"]
    CALC --> NON_MONEY
    
    WEIGHT["Apply Weights:<br/>Comp 50%, Growth 20%,<br/>Culture 15%, WLB 15%"]
    NON_MONEY --> WEIGHT
    
    SCORE["Generate Weighted Scores"]
    WEIGHT --> SCORE
    
    CLEAR_WIN{"Clear winner?<br/>(Score diff > 10)"}
    SCORE --> CLEAR_WIN
    
    CLEAR_WIN -->|"Yes"| NEGOTIATE["Run salary-negotiation-prep.md<br/>for top choice"]
    CLEAR_WIN -->|"No"| TIE["Close tie"]
    
    TIE --> FACTORS["Consider tie-breakers:<br/>- Team quality<br/>- Manager reputation<br/>- Learning opportunities<br/>- Commute/location"]
    
    FACTORS --> FINAL_CHOICE["Select final choice"]
    FINAL_CHOICE --> NEGOTIATE
    
    NEGOTIATE --> STRATEGY["Build negotiation strategy:<br/>- Market research<br/>- Leverage other offers<br/>- Counter-offer script"]
    
    STRATEGY --> EXECUTE["Execute negotiation"]
    EXECUTE --> RESULT{"Satisfied<br/>with result?"}
    
    RESULT -->|"Yes"| ACCEPT["Accept offer"]
    RESULT -->|"No"| BACKUP["Consider backup offers"]
    
    BACKUP --> NEGOTIATE2["Negotiate with #2 choice"]
```

### Resume Quality Gate Workflow

This workflow ensures resumes meet quality standards before application:

```mermaid
graph TD
    DRAFT["Resume Draft"]
    
    GATE1["Gate 1: ATS Check<br/>resume-ats-optimizer.md"]
    DRAFT --> GATE1
    
    CHECK1{"Score > 85%?"}
    GATE1 --> CHECK1
    
    CHECK1 -->|"No"| FIX1["Fix ATS issues:<br/>- Format<br/>- Keywords<br/>- Parsing"]
    FIX1 --> GATE1
    
    CHECK1 -->|"Yes"| GATE2["Gate 2: Bullet Quality<br/>resume-bullet-writer.md"]
    
    GATE2 --> CHECK2{"All bullets<br/>achievement-<br/>focused?"}
    
    CHECK2 -->|"No"| FIX2["Rewrite weak bullets:<br/>- Add action verbs<br/>- Show impact<br/>- Remove duties"]
    FIX2 --> GATE2
    
    CHECK2 -->|"Yes"| GATE3["Gate 3: Quantification<br/>resume-quantifier.md"]
    
    GATE3 --> CHECK3{"80% bullets<br/>quantified?"}
    
    CHECK3 -->|"No"| FIX3["Add metrics:<br/>- Numbers<br/>- Percentages<br/>- Estimates"]
    FIX3 --> GATE3
    
    CHECK3 -->|"Yes"| GATE4["Gate 4: Format<br/>resume-formatter.md"]
    
    GATE4 --> CHECK4{"ATS-safe<br/>formatting?"}
    
    CHECK4 -->|"No"| FIX4["Clean format:<br/>- Remove tables<br/>- Fix fonts<br/>- Adjust spacing"]
    FIX4 --> GATE4
    
    CHECK4 -->|"Yes"| APPROVED["Resume Approved<br/>Ready for Tailoring"]
```

**Sources:** [README.md:176-187](), [README.md:141-159]()

---

## Complete End-to-End Example

### Scenario: Senior Software Engineer Job Search

**Starting Point:** User has basic resume, looking for senior engineering roles.

**Complete Workflow Execution:**

```mermaid
gantt
    title Complete Job Search Timeline
    dateFormat YYYY-MM-DD
    
    section Phase 1: Resume
    Resume optimization          :2024-01-01, 2d
    ATS check + fixes           :2024-01-01, 1d
    Bullet improvements         :2024-01-02, 1d
    
    section Phase 2: Job Search
    Find job postings           :2024-01-03, 5d
    Analyze posting 1           :2024-01-03, 1d
    Analyze posting 2           :2024-01-04, 1d
    Analyze posting 3           :2024-01-05, 1d
    Tailor resume (3x)          :2024-01-06, 2d
    
    section Phase 3: Applications
    Cover letters (3x)          :2024-01-08, 1d
    LinkedIn optimization       :2024-01-08, 1d
    Portfolio case studies      :2024-01-09, 1d
    Submit applications         :2024-01-10, 1d
    
    section Phase 4: Interviews
    Interview prep (Company A)  :2024-01-15, 2d
    Interview prep (Company B)  :2024-01-16, 2d
    Conduct interviews          :2024-01-20, 5d
    
    section Phase 5: Offers
    Receive offers              :2024-01-27, 1d
    Compare offers              :2024-01-28, 1d
    Negotiation prep            :2024-01-29, 1d
    Negotiate                   :2024-01-30, 2d
    Accept offer                :2024-02-01, 1d
```

**Skill Invocations (32 total):**

| Day | Skills Invoked | User Prompts | Outputs Generated |
|-----|---------------|--------------|-------------------|
| **Day 1** | `resume-ats-optimizer.md`<br/>`resume-formatter.md` | "Check ATS compatibility"<br/>"Fix formatting issues" | ATS score: 68% → 92%<br/>Formatted resume |
| **Day 2** | `resume-bullet-writer.md`<br/>`resume-quantifier.md`<br/>`resume-section-builder.md` | "Improve bullets"<br/>"Add metrics"<br/>"Optimize sections" | 15 improved bullets<br/>12 metrics added<br/>Restructured resume |
| **Day 3-5** | `job-description-analyzer.md` (3x) | "Analyze posting: Acme Corp"<br/>"Analyze posting: Beta Inc"<br/>"Analyze posting: Gamma LLC" | Match scores:<br/>Acme: 82%<br/>Beta: 78%<br/>Gamma: 61% |
| **Day 6-7** | `resume-tailor.md` (3x)<br/>`resume-version-manager.md` (3x) | "Tailor for Acme"<br/>"Tailor for Beta"<br/>"Tailor for Gamma"<br/>+ save each | 3 customized resumes<br/>3 tracked versions |
| **Day 8-9** | `cover-letter-generator.md` (3x)<br/>`linkedin-profile-optimizer.md`<br/>`portfolio-case-study-writer.md` | "Write cover letter: Acme"<br/>(repeat 2x)<br/>"Optimize LinkedIn"<br/>"Create case studies" | 3 cover letters<br/>LinkedIn updates<br/>4 case studies |
| **Day 15-16** | `interview-prep-generator.md` (2x) | "Prep for Acme interview"<br/>"Prep for Beta interview" | 18 STAR stories<br/>30 predicted questions |
| **Day 27-28** | `offer-comparison-analyzer.md` | "Compare Acme vs Beta offers" | Comparison matrix<br/>Recommendation: Acme |
| **Day 29-30** | `salary-negotiation-prep.md` | "Negotiate with Acme" | Market research<br/>Negotiation script<br/>Counter-offer: $165K |

**Final Results:**
- 3 applications submitted
- 2 interviews received (67% response rate)
- 2 offers received (100% conversion rate)
- Final salary: $165K (up from $158K offer, +$7K negotiated)
- Total time: 31 days

**Sources:** [README.md:156-200]()

---

