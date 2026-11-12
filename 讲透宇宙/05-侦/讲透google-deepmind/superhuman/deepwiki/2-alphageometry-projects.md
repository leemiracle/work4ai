<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/superhuman · page 2 AlphaGeometry Projects · fetched 2026-10-26 -->

# AlphaGeometry Projects

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [aletheia/Aletheia.pdf](aletheia/Aletheia.pdf)

</details>



## Purpose and Scope

This page documents the AlphaGeometry and AlphaGeometry2 projects, which focus on automated geometry theorem proving. These projects represent the foundational geometry work of the Superhuman Reasoning team and mark the progression from theorem proving (AlphaGeometry) to competitive problem-solving (AlphaGeometry2). Both projects are maintained in external repositories and are referenced from this codebase.

For information about autonomous mathematical research capabilities beyond geometry, see [Aletheia Math Research Agent](#3). For evaluation benchmarks including geometry problems, see [IMO Bench Evaluation Suite](#4). For the complete evolution from these geometry projects to autonomous research, see [Project Timeline and Evolution](#5).

**Sources:** [README.md:1-54]()

## Project Overview

The AlphaGeometry projects consist of two distinct systems developed by the Superhuman Reasoning team:

| Project | Achievement | Publication Date | Repository | Key Milestone |
|---------|-------------|------------------|------------|---------------|
| AlphaGeometry | Nature publication | 2023 | `google-deepmind/alphageometry` | Theorem proving breakthrough |
| AlphaGeometry2 | IMO-silver medal | 2024 | `google-deepmind/alphageometry2` | Competitive performance |

Both projects are hosted in separate GitHub repositories and are referenced from this codebase at [README.md:7-13]().

**Sources:** [README.md:7-13]()

## Repository Structure

```mermaid
graph TB
    REPO["superhuman Repository<br/>(This Codebase)"]
    
    subgraph "External Geometry Projects"
        AG["AlphaGeometry<br/>Repository: alphageometry"]
        AG2["AlphaGeometry2<br/>Repository: alphageometry2"]
    end
    
    subgraph "Internal Projects"
        IMO["IMO Bench<br/>imobench/"]
        ALETHEIA["Aletheia<br/>aletheia/"]
    end
    
    REPO -->|"References via URL<br/>README.md:9"| AG
    REPO -->|"References via URL<br/>README.md:13"| AG2
    REPO -->|"Contains"| IMO
    REPO -->|"Contains"| ALETHEIA
    
    AG -->|"Nature paper link<br/>README.md:8"| NATURE["Nature Article<br/>s41586-023-06747-5"]
    AG2 -->|"Blog post link<br/>README.md:12"| BLOG["DeepMind Blog<br/>IMO-silver announcement"]
```

**Diagram: Repository reference structure for AlphaGeometry projects**

This diagram shows how the AlphaGeometry projects are referenced from the main repository through URL links in the README, distinguishing them from internally-hosted projects.

**Sources:** [README.md:7-13]()

## AlphaGeometry: Theorem Proving Foundation

### Overview

AlphaGeometry is a geometry theorem proving system that achieved breakthrough results in automated mathematical reasoning. The system was published in Nature and represents the team's first major contribution to automated theorem proving.

### Key Information

- **Publication Venue:** Nature journal
- **Article Reference:** `s41586-023-06747-5`
- **Repository:** `https://github.com/google-deepmind/alphageometry`
- **Referenced At:** [README.md:7-9]()

### Publication Details

The Nature paper demonstrates AlphaGeometry's capability to prove geometry theorems at a level comparable to human mathematicians. The system established the foundational approach that would be extended in AlphaGeometry2.

```mermaid
graph LR
    AG["AlphaGeometry<br/>System"]
    
    subgraph "Outputs"
        NATURE["Nature Publication<br/>Article s41586-023-06747-5"]
        REPO["GitHub Repository<br/>alphageometry"]
    end
    
    subgraph "Capabilities"
        PROVE["Theorem Proving"]
        GEO["Geometry Domain"]
        AUTO["Automated Reasoning"]
    end
    
    AG --> NATURE
    AG --> REPO
    AG --> PROVE
    AG --> GEO
    AG --> AUTO
```

**Diagram: AlphaGeometry outputs and capabilities**

**Sources:** [README.md:7-9]()

## AlphaGeometry2: Competitive Problem Solving

### Overview

AlphaGeometry2 extends the original AlphaGeometry system to achieve competitive performance at the International Mathematical Olympiad (IMO) level. The system achieved a silver medal standard in 2024, demonstrating significant advancement in problem-solving capabilities.

### Key Information

- **Achievement:** IMO-silver medal (2024)
- **Blog Post:** DeepMind blog announcement
- **Repository:** `https://github.com/google-deepmind/alphageometry2`
- **Referenced At:** [README.md:11-13]()

### Competition Performance

The 2024 IMO-silver medal achievement represents a milestone in AI mathematical problem-solving, demonstrating that the system can compete at an international level in geometry problem-solving.

```mermaid
graph TB
    AG2["AlphaGeometry2<br/>System"]
    
    subgraph "2024 Achievement"
        IMO["IMO Competition"]
        SILVER["Silver Medal<br/>Performance Level"]
    end
    
    subgraph "Outputs"
        BLOG["DeepMind Blog Post<br/>IMO-silver announcement"]
        REPO2["GitHub Repository<br/>alphageometry2"]
    end
    
    AG2 --> IMO
    IMO --> SILVER
    AG2 --> BLOG
    AG2 --> REPO2
```

**Diagram: AlphaGeometry2 achievement and outputs**

**Sources:** [README.md:11-13]()

## Evolution and Relationship

### Progression Path

The AlphaGeometry projects represent the first two stages in the Superhuman Reasoning team's evolution of mathematical AI capabilities:

```mermaid
timeline
    title "AlphaGeometry Project Evolution"
    
    section Theorem Proving Era
        2023 : AlphaGeometry
             : Nature publication
             : Foundational theorem proving
    
    section Competitive Era
        2024 : AlphaGeometry2
             : IMO-silver medal
             : Competitive problem-solving
    
    section Evaluation Era
        2025 : IMO-gold achievement
             : IMO Bench release
    
    section Research Era
        2025 : Aletheia system
             : Autonomous research
```

**Diagram: Timeline showing AlphaGeometry evolution to subsequent systems**

**Sources:** [README.md:1-54]()

### System Relationships

```mermaid
graph TB
    subgraph "Geometry Specialization"
        AG["AlphaGeometry<br/>Theorem Proving"]
        AG2["AlphaGeometry2<br/>Competition Solving"]
    end
    
    subgraph "General Mathematical Reasoning"
        IMO["IMO Bench<br/>Cross-Domain Evaluation"]
        ALETHEIA["Aletheia<br/>Autonomous Research"]
    end
    
    AG -->|"Evolved to"| AG2
    AG2 -->|"Informed"| IMO
    AG2 -->|"Preceded"| ALETHEIA
    
    IMO -.->|"Includes geometry<br/>problems"| AG2
    ALETHEIA -.->|"Extends beyond<br/>geometry domain"| AG2
```

**Diagram: Relationship between AlphaGeometry projects and subsequent systems**

**Sources:** [README.md:1-54]()

### Capabilities Comparison

| Capability | AlphaGeometry | AlphaGeometry2 | Aletheia |
|------------|---------------|----------------|----------|
| Domain | Geometry | Geometry | Multi-domain |
| Mode | Theorem proving | Competition solving | Research generation |
| Validation | Nature peer review | IMO competition | arXiv publication |
| Output | Proofs | Problem solutions | Research papers |
| Autonomy | Targeted | Targeted | Autonomous research |

**Sources:** [README.md:1-54]()

## Code References

### README Structure

The AlphaGeometry projects are documented in the main repository README through dedicated subsections:

- **AlphaGeometry Section:** [README.md:7-9]()
  - Contains Nature paper link
  - Links to `alphageometry` repository

- **AlphaGeometry2 Section:** [README.md:11-13]()
  - Contains IMO-silver achievement blog link
  - Links to `alphageometry2` repository

```mermaid
graph LR
    README["README.md"]
    
    subgraph "Lines 7-9"
        AG_HEADER["### AlphaGeometry"]
        AG_NATURE["Nature paper link"]
        AG_REPO["Repository URL"]
    end
    
    subgraph "Lines 11-13"
        AG2_HEADER["### AlphaGeometry2"]
        AG2_BLOG["IMO-silver blog link"]
        AG2_REPO["Repository URL"]
    end
    
    README --> AG_HEADER
    AG_HEADER --> AG_NATURE
    AG_HEADER --> AG_REPO
    
    README --> AG2_HEADER
    AG2_HEADER --> AG2_BLOG
    AG2_HEADER --> AG2_REPO
```

**Diagram: README.md structure for AlphaGeometry documentation**

**Sources:** [README.md:7-13]()

## External Repository Access

Both AlphaGeometry projects maintain independent repositories:

### AlphaGeometry Repository
- **URL:** `https://github.com/google-deepmind/alphageometry`
- **License:** Subject to repository-specific licensing
- **Content:** Full implementation and documentation

### AlphaGeometry2 Repository
- **URL:** `https://github.com/google-deepmind/alphageometry2`
- **License:** Subject to repository-specific licensing
- **Content:** Full implementation and IMO competition details

```mermaid
graph TB
    MAIN["superhuman<br/>Repository"]
    
    EXT_AG["External: alphageometry<br/>Full system implementation"]
    EXT_AG2["External: alphageometry2<br/>Full system implementation"]
    
    MAIN -.->|"URL reference<br/>Line 9"| EXT_AG
    MAIN -.->|"URL reference<br/>Line 13"| EXT_AG2
    
    subgraph "External Resources"
        NATURE["Nature Article"]
        BLOG["DeepMind Blog"]
    end
    
    MAIN -.->|"Line 8"| NATURE
    MAIN -.->|"Line 12"| BLOG
```

**Diagram: External repository and resource references**

**Sources:** [README.md:7-13]()

## Role in Mathematical AI Evolution

The AlphaGeometry projects serve as foundational work that enabled subsequent advances:

### Technical Foundation
- Established geometry theorem proving capabilities
- Developed competitive problem-solving approaches
- Created evaluation methodologies for mathematical AI

### Progression to Advanced Systems
- **To IMO Bench:** Geometry problems form a component of the comprehensive evaluation suite ([README.md:15-26]())
- **To Aletheia:** Foundational proving techniques extended to autonomous research across multiple mathematical domains ([README.md:28-33]())

### Domain Specialization vs. Generalization

```mermaid
graph LR
    subgraph "Specialized Systems"
        AG["AlphaGeometry"]
        AG2["AlphaGeometry2"]
    end
    
    subgraph "Generalized Systems"
        IMO["IMO Bench<br/>Multi-domain evaluation"]
        ALETHEIA["Aletheia<br/>Multi-domain research"]
    end
    
    AG -->|"Domain:<br/>Geometry only"| GEOM["Geometry<br/>Specialization"]
    AG2 -->|"Domain:<br/>Geometry only"| GEOM
    
    IMO -->|"Includes:<br/>Algebra, Combinatorics,<br/>Number Theory, Geometry"| MULTI["Multi-domain<br/>Coverage"]
    ALETHEIA -->|"Produces:<br/>Number theory, Algebraic<br/>geometry, Combinatorics, etc."| MULTI
    
    GEOM -.->|"Evolution"| MULTI
```

**Diagram: Evolution from domain-specialized to multi-domain systems**

**Sources:** [README.md:1-54]()

## Integration with Repository Ecosystem

While AlphaGeometry projects are maintained externally, they integrate conceptually with the internal projects:

### IMO Bench Integration
- IMO-AnswerBench includes geometry problems ([README.md:21]())
- IMO-ProofBench contains geometry proofs ([README.md:23]())
- Evaluation methods build on competition problem-solving experience

### Aletheia Relationship
- Aletheia extends capabilities beyond geometry ([README.md:28-33]())
- Similar iterative approach to problem-solving
- Autonomous research vs. targeted theorem proving

```mermaid
graph TB
    subgraph "External Geometry Projects"
        AG["AlphaGeometry"]
        AG2["AlphaGeometry2"]
    end
    
    subgraph "Internal Evaluation"
        AB["IMO-AnswerBench<br/>400 problems<br/>includes geometry"]
        PB["IMO-ProofBench<br/>60 proofs<br/>includes geometry"]
    end
    
    subgraph "Internal Research"
        ALETHEIA["Aletheia<br/>Multi-domain<br/>research agent"]
    end
    
    AG2 -->|"Informed design"| AB
    AG2 -->|"Informed design"| PB
    AG -->|"Proving approach<br/>extended by"| ALETHEIA
    AG2 -->|"Competition experience<br/>extended by"| ALETHEIA
```

**Diagram: Integration of AlphaGeometry projects with internal systems**

**Sources:** [README.md:1-54]()

## Summary

The AlphaGeometry projects establish the Superhuman Reasoning team's foundation in automated mathematical reasoning:

- **AlphaGeometry:** Breakthrough theorem proving published in Nature
- **AlphaGeometry2:** Competitive problem-solving achieving IMO-silver medal
- **Role:** Foundation for subsequent multi-domain systems (IMO Bench, Aletheia)
- **Status:** Maintained in external repositories, referenced from this codebase

These projects represent the geometry-specialized phase of development that preceded the team's expansion into multi-domain mathematical reasoning and autonomous research generation.

**Sources:** [README.md:1-54]()

---

