<!-- source: DeepWiki mcp.deepwiki.com · repo openai/GPTs-are-GPTs · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [data/automation_gpt4_human_labels.tsv](data/automation_gpt4_human_labels.tsv)
- [data/occupation_2023_final.xlsx](data/occupation_2023_final.xlsx)

</details>



This document provides a comprehensive overview of the GPTs-are-GPTs repository, a research platform designed to analyze the economic impact of AI and automation on occupations through systematic comparison of human expert assessments with GPT-4's evaluations of job task automation potential.

The system integrates authoritative government economic data with AI-generated automation assessments to create a comprehensive analytical framework for studying labor market disruption. For detailed research methodology, see [Research Methodology](#2). For specific data sources and formats, see [Data Sources](#3). For analysis code and tools, see [Analysis & Research Code](#4).

## Research Platform Purpose

The GPTs-are-GPTs platform serves as a comprehensive research infrastructure for answering the core question: **How do large language models like GPT-4 assess automation potential of job tasks compared to human experts?** 

The system processes thousands of occupational tasks from the O*NET database, applies both human expert and GPT-4 automation assessments using a standardized T0-T4 scale, and integrates this with economic productivity data to analyze automation's impact on the labor market.

```mermaid
graph TB
    subgraph "Research Question"
        Q["How do GPT-4 automation assessments<br/>compare to human expert assessments<br/>across occupational tasks?"]
    end
    
    subgraph "Core Datasets"
        AUTO["automation_gpt4_human_labels.tsv<br/>• GPT-4 vs Human comparisons<br/>• T0-T4 automation scale<br/>• O*NET task linkage"]
        ONET["full_onet_data.tsv<br/>• Job tasks & descriptions<br/>• Occupational classifications"]
        ECON["BEA_BLS_industry_lp.csv<br/>• Labor productivity data<br/>• Economic indicators"]
    end
    
    subgraph "Analysis Output"
        NOTEBOOKS["gpts_are_gpts_script1.ipynb<br/>gpts_are_gpts_script2.ipynb"]
        STATA["norm_otherscore_statsregs.do"]
        FINAL["occupation_2023_final.xlsx"]
    end
    
    Q --> AUTO
    Q --> ONET
    Q --> ECON
    
    AUTO --> NOTEBOOKS
    ONET --> NOTEBOOKS
    ECON --> STATA
    
    NOTEBOOKS --> FINAL
    STATA --> FINAL
```

Sources: [data/automation_gpt4_human_labels.tsv:1-400](), [data/full_onet_data.tsv](), [README.md:1]()

## System Architecture Overview

The platform follows a data integration pipeline that processes multiple government data sources, applies automation assessments, and feeds into statistical analysis tools for academic research.

### Core Data Integration Pipeline

```mermaid
flowchart TD
    subgraph "Government_Data_Sources"
        BEA["BEA_BLS_industry_lp.csv<br/>BEA_BLS_industry_tfp.csv"]
        ONET_RAW["full_onet_data.tsv<br/>occupations_onet_basic_skills.csv<br/>occupations_onet_work_contexts.csv"]
        BLS["bls_occupation_demographics_2022.xlsx<br/>national_May2021_dl.csv"]
    end
    
    subgraph "Automation_Assessment"
        LABELS["automation_gpt4_human_labels.tsv"]
        LABELSET["full_labelset.tsv"]
    end
    
    subgraph "Integration_Layer"
        MATCHED["occupations_onet_bls_matched.csv"]
        CROSSWALK["nem-onet-to-soc-crosswalk.xlsx"]
        PROJECTIONS["occupations_projections_processed.csv"]
    end
    
    subgraph "Final_Datasets"
        SCORES["autoScores.csv"]
        FINAL_DATA["occupation_2023_final.xlsx"]
    end
    
    subgraph "Research_Analysis"
        NOTEBOOK1["gpts_are_gpts_script1.ipynb"]
        NOTEBOOK2["gpts_are_gpts_script2.ipynb"]
        STATA_REG["norm_otherscore_statsregs.do"]
    end
    
    BEA --> MATCHED
    ONET_RAW --> MATCHED
    BLS --> MATCHED
    
    LABELS --> SCORES
    LABELSET --> SCORES
    
    MATCHED --> SCORES
    CROSSWALK --> SCORES
    PROJECTIONS --> SCORES
    
    SCORES --> FINAL_DATA
    FINAL_DATA --> NOTEBOOK1
    FINAL_DATA --> NOTEBOOK2
    SCORES --> STATA_REG
```

Sources: [data/automation_gpt4_human_labels.tsv:1-10](), [data/occupations_onet_bls_matched.csv](), [data/autoScores.csv](), [data/occupation_2023_final.xlsx]()

## Automation Assessment Framework

The system employs a standardized T0-T4 automation scoring scale applied to individual job tasks extracted from the O*NET occupational database.

### T0-T4 Automation Scale

| Score | Automation Level | Description |
|-------|------------------|-------------|
| T0    | No Automation    | Tasks requiring human creativity, complex social interaction, or physical dexterity |
| T1    | Low Automation   | Tasks with some routine elements but requiring human judgment |
| T2    | Medium Automation| Tasks that are partially automatable with current technology |
| T3    | High Automation  | Tasks that are largely automatable but may require human oversight |
| T4    | Full Automation  | Tasks that can be completely automated with existing technology |

### Assessment Comparison Structure

```mermaid
graph LR
    subgraph "ONET_Tasks"
        TASK1["Task ID: 21527<br/>Occupation: Accountants and Auditors<br/>Task: 'Advise clients in areas such as<br/>compensation, employee health care benefits...'"]
        TASK2["Task ID: 7648<br/>Occupation: Actors<br/>Task: 'Attend auditions and casting calls<br/>to audition for roles.'"]
    end
    
    subgraph "automation_gpt4_human_labels_tsv"
        GPT4["gpt4_automation: T2"]
        HUMAN["human_automation: T2"]
        GPT4_2["gpt4_automation: T0"]
        HUMAN_2["human_automation: T0"]
    end
    
    subgraph "Analysis_Results"
        AGREEMENT["Agreement Analysis<br/>• Correlation coefficients<br/>• Disagreement patterns<br/>• Task category analysis"]
    end
    
    TASK1 --> GPT4
    TASK1 --> HUMAN
    TASK2 --> GPT4_2
    TASK2 --> HUMAN_2
    
    GPT4 --> AGREEMENT
    HUMAN --> AGREEMENT
    GPT4_2 --> AGREEMENT
    HUMAN_2 --> AGREEMENT
```

Sources: [data/automation_gpt4_human_labels.tsv:2-50]()

## Key Research Components

### Primary Analysis Notebooks

The research analysis is conducted through two main Jupyter notebooks that process the automation assessment data:

- `gpts_are_gpts_script1.ipynb`: Primary comparative analysis between GPT-4 and human assessments
- `gpts_are_gpts_script2.ipynb`: Secondary analysis and validation studies

### Statistical Modeling

The `norm_otherscore_statsregs.do` Stata script performs regression analysis examining relationships between:

- **Dependent Variables**: GPT-4 exposure ratings, Human exposure ratings
- **Independent Variables**: Webb measures, SML scores, Routine task measures, AI impact scores

### Final Integrated Dataset

The `occupation_2023_final.xlsx` file represents the culmination of the data integration pipeline, containing:
- Matched occupational data across classification systems
- Automation scores from both sources
- Economic and productivity measures
- Demographics and employment projections

```mermaid
graph TB
    subgraph "occupation_2023_final_xlsx"
        A["Occupation Classifications<br/>• O*NET-SOC codes<br/>• BLS occupation codes<br/>• Title standardization"]
        B["Automation Assessments<br/>• GPT-4 scores by task<br/>• Human expert scores<br/>• Aggregated occupation scores"]
        C["Economic Indicators<br/>• Labor productivity measures<br/>• Total factor productivity<br/>• Employment statistics"]
        D["Demographics<br/>• Age distributions<br/>• Gender composition<br/>• Education requirements"]
    end
    
    subgraph "Research_Applications"
        E["Statistical Analysis<br/>norm_otherscore_statsregs.do"]
        F["Visualization<br/>plot_styles.py"]
        G["Academic Research<br/>Publication outputs"]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> F
    E --> G
```

Sources: [data/occupation_2023_final.xlsx](), [analysis/norm_otherscore_statsregs.do](), [analysis/gpts_are_gpts_script1.ipynb]()

This research platform enables systematic analysis of how artificial intelligence, specifically large language models, assess automation potential compared to human domain experts, providing crucial insights into the future of work and economic disruption from AI technologies.

---

