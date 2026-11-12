<!-- source: DeepWiki mcp.deepwiki.com · repo huifer/Claude-Ally-Health · extra page Growth & Development Monitoring · fetched 2026-10-26 -->

# Growth & Development Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/commands/prostate-health.md](.claude/commands/prostate-health.md)
- [.claude/commands/puberty.md](.claude/commands/puberty.md)
- [.claude/specialists/pediatrics.md](.claude/specialists/pediatrics.md)
- [.claude/specialists/urology.md](.claude/specialists/urology.md)
- [data-example/andropause-tracker.json](data-example/andropause-tracker.json)
- [data-example/child-vaccinations.json](data-example/child-vaccinations.json)

</details>



This document describes the Growth & Development Monitoring system, which tracks pediatric growth using WHO Child Growth Standards and assesses puberty development using Tanner staging. The system provides Z-score calculations (HAZ, WAZ, WHZ, BAZ), growth velocity tracking, and sexual maturation screening for early detection of precocious or delayed puberty.

For vaccination tracking, see [Vaccination Tracking](#4.3.2). For general pediatric assessment and multi-disciplinary consultation, see [AI Specialist Framework](#3.3) and [Individual Specialist Consultations](#7.2).

## System Architecture

The growth monitoring system consists of three major components: growth measurement tracking using WHO standards, puberty assessment using Tanner staging, and integration with the pediatrics AI specialist for comprehensive evaluation.

```mermaid
graph TB
    subgraph "Command Interface"
        GrowthCmd["/growth record<br/>Height/Weight Entry"]
        StatusCmd["/growth status<br/>Current Status"]
        PercentileCmd["/growth percentile<br/>WHO Percentile Lookup"]
        PubertyCmd["/growth puberty<br/>Tanner Staging"]
        CheckCmd["/growth puberty check<br/>Sexual Maturation Screen"]
    end
    
    subgraph "Processing Layer"
        Parser["Natural Language Parser<br/>Extract measurements"]
        WHOCalc["WHO Standards Calculator<br/>HAZ/WAZ/WHZ/BAZ"]
        VelocityCalc["Growth Velocity Calculator<br/>cm/year, kg/year"]
        TannerAssess["Tanner Stage Assessment<br/>B/P/G staging"]
        BoneAgeCalc["Bone Age Evaluator<br/>±years from chronological"]
        MaturityScreen["Sexual Maturation Screener<br/>Precocious/Delayed Detection"]
    end
    
    subgraph "Data Storage"
        GrowthTracker["growth-tracker.json<br/>Height/Weight History<br/>Percentiles & Z-scores"]
        PubertyTracker["puberty-assessment.json<br/>Tanner Stages<br/>Menarche/Voice Change<br/>Bone Age"]
        Profile["profile.json<br/>Birth Date, Sex"]
    end
    
    subgraph "AI Integration"
        PediatricsSpec["Pediatrics Specialist<br/>pediatrics.md"]
        MDTConsult["MDT Consultation<br/>/consult"]
    end
    
    GrowthCmd --> Parser
    StatusCmd --> GrowthTracker
    PercentileCmd --> WHOCalc
    PubertyCmd --> TannerAssess
    CheckCmd --> MaturityScreen
    
    Parser --> WHOCalc
    Parser --> VelocityCalc
    WHOCalc --> GrowthTracker
    VelocityCalc --> GrowthTracker
    
    TannerAssess --> BoneAgeCalc
    TannerAssess --> MaturityScreen
    BoneAgeCalc --> PubertyTracker
    MaturityScreen --> PubertyTracker
    
    Profile --> WHOCalc
    Profile --> TannerAssess
    GrowthTracker --> PediatricsSpec
    PubertyTracker --> PediatricsSpec
    PediatricsSpec --> MDTConsult
    
    style WHOCalc fill:#f9f9f9
    style TannerAssess fill:#f9f9f9
    style MaturityScreen fill:#f9f9f9
```

**Sources:** [.claude/specialists/pediatrics.md:297-364](), [.claude/specialists/pediatrics.md:582-608](), [.claude/commands/puberty.md:1-214]()

## WHO Growth Standards Framework

The system implements the WHO Child Growth Standards (MGRS 2006) for comprehensive growth assessment. Four primary Z-score metrics are calculated to evaluate growth across multiple dimensions.

### Z-Score Metrics

| Metric | Full Name | Purpose | Normal Range |
|--------|-----------|---------|--------------|
| **HAZ** | Height-for-Age Z-score | Linear growth assessment | ≥ -1 SD |
| **WAZ** | Weight-for-Age Z-score | Overall nutritional status | ≥ -1 SD |
| **WHZ** | Weight-for-Height Z-score | Acute malnutrition detection | -2 to +1 SD |
| **BAZ** | BMI-for-Age Z-score | Body composition assessment | -2 to +1 SD |

**Sources:** [.claude/specialists/pediatrics.md:299-329]()

### Growth Status Classification

The system classifies growth status based on Z-score thresholds and provides clinical interpretations:

```mermaid
graph LR
    subgraph "HAZ - Height-for-Age"
        HAZ_Input["Height Measurement"]
        HAZ_Calc["Z = (Height - Median) / SD<br/>From WHO Tables"]
        HAZ_Severe["HAZ < -3<br/>Severe Stunting<br/>🚨 Immediate Medical Attention"]
        HAZ_Moderate["HAZ -3 to -2<br/>Moderate Stunting<br/>⚠️ Medical Evaluation"]
        HAZ_Mild["HAZ -2 to -1<br/>Mild Growth Delay<br/>⚠️ Monitor Closely"]
        HAZ_Normal["HAZ ≥ -1<br/>Normal Height<br/>✓ Continue Routine Monitoring"]
        HAZ_Tall["HAZ > +2<br/>Unusually Tall<br/>⚠️ Evaluate Cause"]
    end
    
    HAZ_Input --> HAZ_Calc
    HAZ_Calc --> HAZ_Severe
    HAZ_Calc --> HAZ_Moderate
    HAZ_Calc --> HAZ_Mild
    HAZ_Calc --> HAZ_Normal
    HAZ_Calc --> HAZ_Tall
```

**Sources:** [.claude/specialists/pediatrics.md:303-307]()

### Growth Velocity Standards

Growth velocity is monitored to detect growth acceleration or deceleration. The system compares actual growth rates against age-specific reference values:

| Age Range | Expected Height Velocity | Expected Weight Velocity | Warning Threshold |
|-----------|-------------------------|-------------------------|-------------------|
| **0-1 year** | 25 cm/year (P50) | 6-7 kg/year | < P5 percentile |
| **1-2 years** | 12 cm/year (P50) | 2-3 kg/year | < P5 percentile |
| **2-3 years** | 9 cm/year (P50) | 2 kg/year | < P5 percentile |
| **3-4 years** | 7.7 cm/year (P50) | 2 kg/year | < P5 percentile |
| **≥4 years** | 5-7 cm/year | 3-4 kg/year (pre-pubertal) | < 5 cm/year |

**Sources:** [.claude/specialists/pediatrics.md:336-350]()

### Growth Anomaly Detection

The system implements multiple warning signals for abnormal growth patterns:

```mermaid
graph TB
    subgraph "Anomaly Detection Rules"
        Rule1["Height crosses down<br/>≥2 major percentile lines<br/>(e.g., P75 → P25)"]
        Rule2["Weight stagnant or decreasing<br/>for ≥3 consecutive months"]
        Rule3["Height velocity < 5 cm/year<br/>after age 4"]
        Rule4["BMI > P95<br/>Obesity risk"]
        Rule5["Head circumference < P3 or > P97<br/>(0-3 years old)"]
        
        Alert["⚠️ Growth Alert Generated"]
        Recommend["Recommendations:<br/>• Re-measure within 1 month<br/>• Check growth hormone<br/>• Check thyroid function<br/>• Pediatric endocrinology referral"]
    end
    
    Rule1 --> Alert
    Rule2 --> Alert
    Rule3 --> Alert
    Rule4 --> Alert
    Rule5 --> Alert
    Alert --> Recommend
```

**Sources:** [.claude/specialists/pediatrics.md:351-357]()

## Growth Tracking Commands

The `/growth` command family provides natural language interfaces for recording and querying growth measurements.

### Command Processing Flow

```mermaid
graph TB
    subgraph "User Input Examples"
        Input1["/growth record 100cm 15kg"]
        Input2["/growth record height 100 weight 15"]
        Input3["/growth status"]
        Input4["/growth percentile height 100cm 3y"]
    end
    
    subgraph "Command Parser"
        ParseAction["Extract Action:<br/>record | status | percentile"]
        ParseMeasure["Extract Measurements:<br/>height_cm, weight_kg"]
        ParseDate["Extract Date:<br/>YYYY-MM-DD or 'today'"]
        ParseAge["Calculate Age:<br/>from profile.json birth_date"]
    end
    
    subgraph "WHO Calculator Module"
        LoadTables["Load WHO Reference Tables:<br/>Sex-specific, Age-specific"]
        FindMedian["Find Median (P50) for age/sex"]
        FindSD["Find Standard Deviation"]
        CalcZ["Calculate Z-score:<br/>Z = (Value - Median) / SD"]
        CalcPercentile["Convert Z to Percentile:<br/>Using standard normal CDF"]
    end
    
    subgraph "Velocity Calculator"
        LoadHistory["Load Previous Measurements<br/>from growth-tracker.json"]
        CalcInterval["Calculate Time Interval<br/>(months)"]
        CalcDelta["Calculate Δ Height, Δ Weight"]
        AnnualizeRate["Annualize:<br/>cm/year = Δh × (12/months)<br/>kg/year = Δw × (12/months)"]
        CompareRef["Compare to WHO Velocity<br/>Reference (P5, P50, P95)"]
    end
    
    subgraph "Data Persistence"
        UpdateJSON["Update growth-tracker.json:<br/>measurements[]<br/>z_scores[]<br/>percentiles[]<br/>velocities[]"]
        UpdateIndex["Update index.json:<br/>last_growth_date<br/>total_measurements"]
    end
    
    Input1 --> ParseAction
    Input2 --> ParseAction
    Input3 --> ParseAction
    Input4 --> ParseAction
    
    ParseAction --> ParseMeasure
    ParseMeasure --> ParseDate
    ParseDate --> ParseAge
    
    ParseAge --> LoadTables
    LoadTables --> FindMedian
    FindMedian --> FindSD
    FindSD --> CalcZ
    CalcZ --> CalcPercentile
    
    CalcZ --> LoadHistory
    LoadHistory --> CalcInterval
    CalcInterval --> CalcDelta
    CalcDelta --> AnnualizeRate
    AnnualizeRate --> CompareRef
    
    CalcPercentile --> UpdateJSON
    CompareRef --> UpdateJSON
    UpdateJSON --> UpdateIndex
```

**Sources:** [.claude/specialists/pediatrics.md:582-590]()

### Natural Language Parsing Patterns

The system recognizes diverse input formats for height and weight measurements:

| Input Pattern | Extracted Data |
|---------------|----------------|
| `"100cm 15kg"` | height: 100, weight: 15 |
| `"height 100 weight 15"` | height: 100, weight: 15 |
| `"身高100厘米 体重15公斤"` | height: 100, weight: 15 |
| `"100 15"` (space-separated) | height: 100, weight: 15 |
| `"1m 15kg"` | height: 100, weight: 15 |

**Sources:** [.claude/specialists/pediatrics.md:297-364]()

## Puberty Assessment System

The puberty assessment system implements Tanner staging for sexual maturation evaluation and screens for precocious or delayed puberty.

### Tanner Staging Framework

```mermaid
graph TB
    subgraph "Female Development Tracking"
        F_Breast["Breast Development (B1-B5)<br/>/growth puberty breast"]
        F_PubicHair["Pubic Hair (P1-P5)<br/>/growth puberty pubic"]
        F_Menarche["Menarche<br/>/growth puberty menarche"]
        
        F_B1["B1: Pre-pubertal<br/>nipple elevation only"]
        F_B2["B2: Breast bud<br/>areola enlargement"]
        F_B3["B3: Further enlargement<br/>single contour"]
        F_B4["B4: Areola projects<br/>secondary mound"]
        F_B5["B5: Mature breast<br/>areola recesses"]
        
        F_Breast --> F_B1
        F_Breast --> F_B2
        F_Breast --> F_B3
        F_Breast --> F_B4
        F_Breast --> F_B5
    end
    
    subgraph "Male Development Tracking"
        M_Testicular["Testicular Volume<br/>/growth puberty testicular"]
        M_PubicHair["Pubic Hair (P1-P5)<br/>/growth puberty pubic"]
        M_Penis["Penis Development<br/>/growth puberty penis"]
        M_Voice["Voice Change<br/>/growth puberty voice"]
        
        M_G1["G1: Pre-pubertal<br/><4ml"]
        M_G2["G2: Enlargement begins<br/>4-6ml"]
        M_G3["G3: Further growth<br/>6-10ml"]
        M_G4["G4: Near adult<br/>10-20ml"]
        M_G5["G5: Adult size<br/>≥20ml"]
        
        M_Testicular --> M_G1
        M_Testicular --> M_G2
        M_Testicular --> M_G3
        M_Testicular --> M_G4
        M_Testicular --> M_G5
    end
    
    subgraph "Bone Age Assessment"
        BoneAge["/growth puberty bone-age"]
        BoneCalc["Compare to<br/>Chronological Age"]
        BoneDelay["<-1 year:<br/>Growth Delay"]
        BoneNormal["-1 to +1 year:<br/>Normal"]
        BoneAdvanced[">+1 year:<br/>Precocious Puberty"]
        
        BoneAge --> BoneCalc
        BoneCalc --> BoneDelay
        BoneCalc --> BoneNormal
        BoneCalc --> BoneAdvanced
    end
```

**Sources:** [.claude/specialists/pediatrics.md:367-445](), [.claude/commands/puberty.md:93-117]()

### Sexual Maturation Screening

The system implements age-based screening criteria to detect precocious or delayed puberty:

```mermaid
graph TB
    subgraph "Precocious Puberty Detection"
        F_Check_Early["Female < 8 years"]
        F_B2_Early["Breast Development (B2)?"]
        F_Menarche_Early["Menarche < 10 years?"]
        F_Alert_Early["🚨 PRECOCIOUS PUBERTY<br/>Refer to Pediatric Endocrinology"]
        
        M_Check_Early["Male < 9 years"]
        M_G2_Early["Testicular Volume > 4ml?"]
        M_Voice_Early["Voice Change?"]
        M_Alert_Early["🚨 PRECOCIOUS PUBERTY<br/>Refer to Pediatric Endocrinology"]
        
        F_Check_Early --> F_B2_Early
        F_Check_Early --> F_Menarche_Early
        F_B2_Early -->|"Yes"| F_Alert_Early
        F_Menarche_Early -->|"Yes"| F_Alert_Early
        
        M_Check_Early --> M_G2_Early
        M_Check_Early --> M_Voice_Early
        M_G2_Early -->|"Yes"| M_Alert_Early
        M_Voice_Early -->|"Yes"| M_Alert_Early
    end
    
    subgraph "Delayed Puberty Detection"
        F_Check_Late["Female > 13 years"]
        F_B2_Late["No Breast Development (B1)?"]
        F_Menarche_Late["Female > 16 years<br/>No Menarche?"]
        F_Alert_Late["⚠️ DELAYED PUBERTY<br/>Evaluate: Turner Syndrome,<br/>Kallmann Syndrome, Chronic Disease"]
        
        M_Check_Late["Male > 14 years"]
        M_G2_Late["Testicular Volume < 4ml?"]
        M_Alert_Late["⚠️ DELAYED PUBERTY<br/>Evaluate: Klinefelter Syndrome,<br/>Hypogonadotropic Hypogonadism"]
        
        F_Check_Late --> F_B2_Late
        F_Check_Late --> F_Menarche_Late
        F_B2_Late -->|"Yes"| F_Alert_Late
        F_Menarche_Late -->|"Yes"| F_Alert_Late
        
        M_Check_Late --> M_G2_Late
        M_G2_Late -->|"Yes"| M_Alert_Late
    end
```

**Sources:** [.claude/specialists/pediatrics.md:448-508](), [.claude/commands/puberty.md:120-130]()

### Puberty Command Processing

The `/growth puberty` command family processes Tanner stage inputs and performs maturity screening:

| Command | Purpose | Example Input | Data Captured |
|---------|---------|---------------|---------------|
| `/growth puberty breast` | Female breast staging | `"breast B3"` | breast_stage: "B3" |
| `/growth puberty pubic` | Pubic hair staging | `"pubic P2"` | pubic_hair_stage: "P2" |
| `/growth puberty menarche` | First menstruation | `"menarche true 11.5"` | menarche_occurred: true, age_at_menarche: 11.5 |
| `/growth puberty testicular` | Male testicular volume | `"testicular 8ml"` | testicular_volume_ml: 8, stage: "G3" |
| `/growth puberty penis` | Penis development | `"penis 6.5cm"` | penis_length_cm: 6.5 |
| `/growth puberty voice` | Voice change | `"voice true"` | voice_change: true |
| `/growth puberty bone-age` | Bone maturation | `"bone-age 10.8"` | bone_age_years: 10.8 |
| `/growth puberty check` | Sexual maturity screen | (no parameters) | Runs age-based screening rules |

**Sources:** [.claude/commands/puberty.md:12-88]()

### Bone Age Evaluation

Bone age assessment compares skeletal maturation to chronological age:

```mermaid
graph LR
    Input["X-ray of Left Hand<br/>Wrist AP View"]
    BoneAge["Bone Age Reading<br/>(years)"]
    ChronoAge["Chronological Age<br/>from profile.json"]
    CalcDiff["Difference = Bone Age - Chrono Age"]
    
    Interpret1["Difference < -1 year<br/>Growth Delay<br/>Causes: GH deficiency,<br/>hypothyroidism, chronic disease"]
    Interpret2["Difference -1 to +1 year<br/>Normal Range<br/>Age-appropriate maturation"]
    Interpret3["Difference > +1 year<br/>Advanced Maturation<br/>Evaluate for:<br/>Precocious puberty,<br/>adrenal hyperplasia"]
    
    Input --> BoneAge
    BoneAge --> CalcDiff
    ChronoAge --> CalcDiff
    CalcDiff --> Interpret1
    CalcDiff --> Interpret2
    CalcDiff --> Interpret3
```

**Sources:** [.claude/specialists/pediatrics.md:433-438]()

## Data Storage Architecture

Growth and puberty data are stored in separate JSON tracker files within the `data/` directory.

### Growth Tracker Data Structure

```json
{
  "created_at": "2020-01-01T00:00:00.000Z",
  "last_updated": "2025-06-20T10:00:00.000Z",
  
  "child_profile": {
    "child_id": "child_20200101",
    "name": "Child Name",
    "birth_date": "2020-01-01",
    "sex": "male"
  },
  
  "growth_measurements": [
    {
      "date": "2025-06-20",
      "age_months": 65,
      "age_years": 5.42,
      "height_cm": 110.5,
      "weight_kg": 18.3,
      "bmi": 15.0,
      "head_circumference_cm": null
    }
  ],
  
  "who_assessment": {
    "height_for_age": {
      "z_score": -0.5,
      "percentile": 31,
      "interpretation": "normal"
    },
    "weight_for_age": {
      "z_score": -0.2,
      "percentile": 42,
      "interpretation": "normal"
    },
    "bmi_for_age": {
      "z_score": 0.1,
      "percentile": 54,
      "interpretation": "normal"
    },
    "weight_for_height": {
      "z_score": 0.3,
      "percentile": 62,
      "interpretation": "normal"
    }
  },
  
  "growth_velocity": {
    "height_velocity_cm_per_year": 6.2,
    "weight_velocity_kg_per_year": 2.5,
    "measurement_interval_months": 6,
    "velocity_percentile": "P25-P50"
  },
  
  "alerts": [
    {
      "type": "growth_velocity_slow",
      "message": "Height velocity < P5 for age",
      "recommendation": "Consider growth hormone evaluation"
    }
  ]
}
```

**Sources:** [.claude/specialists/pediatrics.md:297-365]()

### Puberty Tracker Data Structure

```json
{
  "created_at": "2020-01-01T00:00:00.000Z",
  "last_updated": "2025-06-20T10:00:00.000Z",
  
  "puberty_tracking": {
    "child_id": "child_20200101",
    "chronological_age": 10.5,
    
    "female_development": {
      "breast_stage": "B3",
      "breast_stage_age": 10.2,
      "pubic_hair_stage": "P2",
      "pubic_hair_age": 10.5,
      "menarche": {
        "occurred": false,
        "age_at_menarche": null,
        "predicted_age": "11.5-12.0"
      }
    },
    
    "male_development": {
      "testicular_volume": {
        "left_ml": null,
        "right_ml": null,
        "stage": null
      },
      "penis_length_cm": null,
      "pubic_hair_stage": null,
      "voice_change": false,
      "facial_hair": false
    },
    
    "bone_age": {
      "chronological_age": 10.5,
      "bone_age_years": 10.8,
      "difference_years": 0.3,
      "interpretation": "normal",
      "assessment_date": "2025-06-15"
    },
    
    "assessment": {
      "overall_status": "normal_progression",
      "precocious_puberty_risk": false,
      "delayed_puberty_risk": false,
      "recommendations": [
        "Continue routine monitoring",
        "Next assessment in 6 months"
      ]
    }
  },
  
  "sexual_maturation_screening": {
    "last_screen_date": "2025-06-20",
    "precocious_criteria": {
      "age_threshold_years": 8.0,
      "current_age": 10.5,
      "criteria_met": false
    },
    "delayed_criteria": {
      "age_threshold_years": 13.0,
      "current_age": 10.5,
      "criteria_met": false
    }
  }
}
```

**Sources:** [.claude/commands/puberty.md:142-169]()

## Pediatrics Specialist Integration

The Pediatrics AI specialist (`pediatrics.md`) integrates growth and puberty data for comprehensive child health assessment.

### Specialist Analysis Framework

```mermaid
graph TB
    subgraph "Data Sources"
        GrowthData["growth-tracker.json"]
        PubertyData["puberty-assessment.json"]
        ProfileData["profile.json"]
        BiochemData["生化检查/<br/>Blood tests, Nutrients"]
        ImagingData["影像检查/<br/>Bone age X-ray"]
    end
    
    subgraph "Pediatrics Specialist Analysis"
        GrowthEval["Growth Assessment Module:<br/>• Interpret HAZ/WAZ/WHZ/BAZ<br/>• Compare to percentiles<br/>• Evaluate growth velocity<br/>• Identify growth anomalies"]
        
        NutritionEval["Nutrition Assessment Module:<br/>• Hemoglobin (age-specific ref)<br/>• Iron/Ferritin status<br/>• Vitamin D levels<br/>• Calcium, Zinc evaluation"]
        
        DevelopmentEval["Development Assessment Module:<br/>• Motor milestones<br/>• Language development<br/>• Social behavior<br/>• Tanner staging interpretation"]
        
        RiskEval["Risk Assessment Module:<br/>• Malnutrition risk<br/>• Obesity risk<br/>• Anemia risk<br/>• Developmental delay risk<br/>• Precocious/delayed puberty"]
    end
    
    subgraph "Output Generation"
        Report["Pediatric Analysis Report:<br/>• Growth percentiles<br/>• Nutritional status<br/>• Development status<br/>• Risk factors<br/>• Recommendations"]
        
        Alerts["Clinical Alerts:<br/>⚠️ Growth < P3<br/>⚠️ Precocious puberty<br/>⚠️ Severe malnutrition<br/>🚨 Immediate evaluation needed"]
        
        Guidance["Parent Guidance:<br/>• Nutrition recommendations<br/>• Sleep requirements<br/>• Activity suggestions<br/>• Vaccination reminders<br/>• Development promotion"]
    end
    
    GrowthData --> GrowthEval
    PubertyData --> DevelopmentEval
    ProfileData --> GrowthEval
    BiochemData --> NutritionEval
    ImagingData --> DevelopmentEval
    
    GrowthEval --> RiskEval
    NutritionEval --> RiskEval
    DevelopmentEval --> RiskEval
    
    RiskEval --> Report
    RiskEval --> Alerts
    RiskEval --> Guidance
```

**Sources:** [.claude/specialists/pediatrics.md:59-67](), [.claude/specialists/pediatrics.md:78-140]()

### Specialist Output Format

The pediatrics specialist generates structured reports following this template:

| Report Section | Content | Data Sources |
|----------------|---------|--------------|
| **Growth Evaluation** | Height (value + percentile), Weight (value + percentile), BMI, Growth velocity | growth-tracker.json, WHO tables |
| **Nutrition Assessment** | Hemoglobin, Iron/Ferritin, Zinc, Vitamin D, Calcium levels with age-specific reference values | 生化检查/ directory |
| **Common Disease Screening** | Respiratory, Digestive, Allergic, Infectious disease markers | 生化检查/, 影像检查/ |
| **Development Assessment** | Motor, Language, Social-behavioral milestones, Tanner staging | puberty-assessment.json |
| **Risk Assessment** | Malnutrition risk, Obesity risk, Anemia risk, Developmental delay risk | Composite analysis |
| **Recommendations** | Nutrition guidance, Lifestyle suggestions, Vaccination schedule, Disease prevention, Development promotion, Follow-up timing | Clinical guidelines |

**Sources:** [.claude/specialists/pediatrics.md:68-140]()

### Multi-Disciplinary Consultation Integration

Growth and puberty data are automatically included in MDT consultations when relevant specialists are involved:

```mermaid
graph LR
    Trigger["/consult command"]
    Coordinator["consultation-coordinator.md"]
    
    LoadPediatric["Load Pediatric Data:<br/>• growth-tracker.json<br/>• puberty-assessment.json"]
    
    PediatricSpec["Pediatrics Specialist:<br/>Growth & development analysis"]
    EndoSpec["Endocrinology Specialist:<br/>Hormone evaluation if<br/>precocious/delayed puberty"]
    
    Integration["Opinion Integration:<br/>• Coordinate growth concerns<br/>• Endocrine workup if needed<br/>• Unified recommendations"]
    
    Trigger --> Coordinator
    Coordinator --> LoadPediatric
    LoadPediatric --> PediatricSpec
    LoadPediatric --> EndoSpec
    PediatricSpec --> Integration
    EndoSpec --> Integration
```

**Sources:** [.claude/specialists/pediatrics.md:610-629]()

## Clinical Safety Principles

The system enforces strict safety boundaries for pediatric growth and puberty assessment.

### Safety Red Lines

The following actions are explicitly prohibited by the system:

| Prohibited Action | Reason | Alternative |
|-------------------|--------|-------------|
| **Specific medication dosing** | Requires individualized medical evaluation | Refer to pediatrician for treatment |
| **Definitive diagnoses** | Cannot replace clinical examination | Provide risk assessment and screening results |
| **Prognosis predictions** | Cannot predict future outcomes (e.g., adult height) | Provide reference ranges only |
| **Medical procedures** | Cannot recommend invasive interventions | Suggest specialist consultation |
| **Vaccination contraindication judgments** | Requires physician assessment | List general principles, defer to physician |

**Sources:** [.claude/specialists/pediatrics.md:49-58](), [.claude/commands/puberty.md:175-188]()

### Appropriate vs. Prohibited Expressions

**✅ Appropriate Expressions:**
- "Height is at the 15th percentile, which is within normal range but trending downward. Monitor growth velocity closely."
- "Breast development at age 7.5 meets criteria for precocious puberty screening. Recommend pediatric endocrinology evaluation."
- "Growth velocity is 4.5 cm/year, below expected 6-7 cm/year for age. Consider growth hormone and thyroid function testing."
- "Bone age is 2 years ahead of chronological age, consistent with early pubertal development. Recommend further evaluation."

**❌ Prohibited Expressions:**
- "Administer growth hormone 0.03 mg/kg/day" (specific medication dosing)
- "Diagnosed with constitutional growth delay" (definitive diagnosis)
- "Adult height will be 165 cm" (prognosis prediction)
- "Start leuprolide injections for precocious puberty" (specific prescription)

**Sources:** [.claude/specialists/pediatrics.md:142-154](), [.claude/commands/puberty.md:175-181]()

### Emergency Referral Criteria

The system generates immediate referral recommendations for the following conditions:

```mermaid
graph TB
    subgraph "🚨 Immediate Referral Criteria"
        Severe_Stunting["HAZ < -3 SD<br/>Severe Stunting"]
        Severe_Wasting["WHZ < -3 SD<br/>Severe Acute Malnutrition"]
        Precocious_Early["Sexual development:<br/>Female < 8 years<br/>Male < 9 years"]
        Growth_Crossing["Height crosses down<br/>≥2 major percentiles"]
        Bone_Advanced["Bone age > +2 years<br/>ahead of chronological"]
    end
    
    subgraph "⚠️ Urgent Evaluation (1-4 weeks)"
        Moderate_Stunting["HAZ -3 to -2 SD<br/>Moderate Stunting"]
        Growth_Velocity["Height velocity < 4 cm/year<br/>after age 4"]
        Delayed_Puberty["No development:<br/>Female > 13 years<br/>Male > 14 years"]
        Obesity["BMI > P95<br/>Obesity"]
    end
    
    subgraph "✅ Routine Monitoring"
        Normal["All metrics within<br/>normal ranges"]
        Monitor["Continue<br/>routine checkups"]
    end
    
    Severe_Stunting --> Refer_Immediate["Refer immediately to:<br/>Pediatric Endocrinology<br/>or Child Health Center"]
    Severe_Wasting --> Refer_Immediate
    Precocious_Early --> Refer_Immediate
    Growth_Crossing --> Refer_Immediate
    Bone_Advanced --> Refer_Immediate
    
    Moderate_Stunting --> Refer_Urgent["Schedule evaluation<br/>within 1-4 weeks"]
    Growth_Velocity --> Refer_Urgent
    Delayed_Puberty --> Refer_Urgent
    Obesity --> Refer_Urgent
    
    Normal --> Monitor
```

**Sources:** [.claude/specialists/pediatrics.md:104-109](), [.claude/specialists/pediatrics.md:503-508]()

## Data Privacy and Storage

All growth and development data are stored locally in the `data/` directory with no cloud synchronization:

- **Primary trackers:** `growth-tracker.json`, `puberty-assessment.json`
- **Supplementary data:** Monthly directories under `生化检查/`, `影像检查/`
- **Index catalog:** `index.json` maintains references to all tracker files
- **Git exclusion:** `.gitignore` prevents accidental commit of personal health data
- **Access control:** File permissions restrict access to user only

**Sources:** [.claude/specialists/pediatrics.md:651-656]()

---

