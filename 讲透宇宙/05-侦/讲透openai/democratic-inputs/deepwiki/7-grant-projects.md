<!-- source: DeepWiki mcp.deepwiki.com · repo openai/democratic-inputs · page 7 Grant Projects · fetched 2026-10-26 -->

# Grant Projects

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [projects/collective_dialogues_for_democratic_input/README.md](projects/collective_dialogues_for_democratic_input/README.md)
- [projects/collective_dialogues_for_democratic_input/experiments/research_log.md](projects/collective_dialogues_for_democratic_input/experiments/research_log.md)
- [projects/inclusive_ai_a_chatgpt_plugin_and_dao_to_engage_marginalized_groups_in_ai/README.md](projects/inclusive_ai_a_chatgpt_plugin_and_dao_to_engage_marginalized_groups_in_ai/README.md)
- [projects/making_ai_transparent_and_accountable/README.md](projects/making_ai_transparent_and_accountable/README.md)
- [projects/vtaiwan_and_chatham_house_bridging_the_recursive_public/README.md](projects/vtaiwan_and_chatham_house_bridging_the_recursive_public/README.md)

</details>



This page documents the individual funded projects within OpenAI's Democratic Inputs to AI grant program, which awarded 10 teams to develop and test innovative processes for democratic governance of AI systems. Each project explores different methodological approaches to collecting and integrating public input into AI policy development.

For documentation of the core deliberation platform infrastructure that supports some of these projects, see [System Architecture](#2). For details on the collective dialogues methodology specifically, see [Collective Dialogues Project](#7.1).

## Program Overview

The Democratic Inputs to AI grant program represents a comprehensive exploration of democratic mechanisms for AI governance. The program funded diverse approaches ranging from deliberative processes to technical platforms, each addressing different aspects of the challenge of incorporating public input into AI policy.

```mermaid
graph TB
    subgraph "Grant Program Structure"
        PROGRAM["Democratic Inputs to AI<br/>Grant Program"]
        
        subgraph "Process-Focused Projects"
            COLLECTIVE["Collective Dialogues<br/>projects/collective_dialogues_for_democratic_input"]
            DELIBERATION["Deliberation at Scale<br/>projects/deliberation_at_scale"]
            VTAIWAN["vTaiwan & Chatham House<br/>projects/vtaiwan_and_chatham_house_bridging_the_recursive_public"]
            RAPPLER["Rappler Transparency<br/>projects/making_ai_transparent_and_accountable"]
        end
        
        subgraph "Platform-Focused Projects"
            INCLUSIVE["Inclusive.AI<br/>projects/inclusive_ai_a_chatgpt_plugin_and_dao_to_engage_marginalized_groups_in_ai"]
            ALIGNED["Aligned Platform<br/>projects/Aligned-Platform-EnergizeAI"]
            UBUNTU["Ubuntu-AI<br/>projects/Ubuntu_AI_a_platform_for_equitable_and_inclusive_model_training"]
        end
        
        subgraph "Technical-Focused Projects"
            DEMOCRATIC_FT["Democratic Fine-Tuning<br/>projects/democratic_fine_tuning"]
            GENERATIVE["Generative Social Choice<br/>projects/generative_social_choice"]
            CASELAW["Case Law for AI Policy<br/>projects/case_law_for_ai_policy"]
        end
    end
    
    PROGRAM --> COLLECTIVE
    PROGRAM --> DELIBERATION
    PROGRAM --> VTAIWAN
    PROGRAM --> RAPPLER
    PROGRAM --> INCLUSIVE
    PROGRAM --> ALIGNED
    PROGRAM --> UBUNTU
    PROGRAM --> DEMOCRATIC_FT
    PROGRAM --> GENERATIVE
    PROGRAM --> CASELAW
```

**Project Integration Overview**
This diagram shows how the 10 funded projects are organized by their primary methodological approach, with each project located in its respective directory within the monorepo structure.

Sources: [README.md:1-183]()

## Project Categories and Methodologies

### Process-Driven Democratic Input

These projects focus on developing scalable deliberative processes for collecting and synthesizing public opinion on AI governance questions.

| Project | Core Methodology | Technical Implementation | Key Outputs |
|---------|------------------|-------------------------|-------------|
| Collective Dialogues | Bridging-based consensus finding | GPT-4 policy generation pipeline | AI medical advice policies |
| Deliberation at Scale | Small group video conversations | AI-facilitated discussion management | Consensus through structured dialogue |
| vTaiwan & Chatham House | Recursive public methodology | Adapted vTaiwan platform | Connected participatory processes |
| Rappler Transparency | Offline-online hybrid processes | Text/audio synthesis via LLMs | Policy ideas from focus groups |

**Collective Dialogues Process Flow**
```mermaid
flowchart LR
    subgraph "Collective Dialogues Pipeline"
        CD1["CD1: Learn Public Views<br/>collective_dialogues_for_democratic_input/experiments"]
        POLICY_GEN["Policy Generation<br/>tools/policy generation/policy_gen.ipynb"]
        EXPERT["Expert Refinement<br/>Medical Professional Review"]
        CD2["CD2: Public Refinement<br/>CD2 collective dialogue"]
        CD3["CD3: Evaluation<br/>Large-scale public support assessment"]
        
        CD1 --> POLICY_GEN
        POLICY_GEN --> EXPERT
        EXPERT --> CD2
        CD2 --> CD3
    end
    
    subgraph "Technical Components"
        BRIDGING["Bridging-based Ranking<br/>Consensus Discovery"]
        GPT4["GPT-4 Pipeline<br/>Policy Clause Generation"]
        RIGHTS_CHECK["Human Rights Check<br/>tools/human rights consitency check"]
        
        POLICY_GEN --> BRIDGING
        POLICY_GEN --> GPT4
        CD3 --> RIGHTS_CHECK
    end
```

**Collective Dialogues Technical Implementation**
This shows the systematic process used by the collective dialogues project to transform public input into validated AI policies through multiple stages of refinement.

Sources: [projects/collective_dialogues_for_democratic_input/README.md:1-49](), [projects/collective_dialogues_for_democratic_input/experiments/research_log.md:1-500]()

### Platform-Based Democratic Mechanisms

These projects created technical platforms that enable democratic participation in AI governance decisions.

**Inclusive.AI Architecture**
```mermaid
graph TB
    subgraph "Inclusive.AI Platform"
        WEB3AUTH["Web3Auth<br/>Email SSO + MPC Wallet"]
        PROFILE["Profile Setup<br/>Quillforms Survey"]
        AICHAT["AI Chat Interface<br/>GPT-Powered Conversations"]
        
        subgraph "Voting Infrastructure"
            SNAPSHOT["Snapshot Voting<br/>Transparent Decision System"]
            INCLQ["INCLQ Token Contract<br/>Optimism Blockchain"]
            INCLR["INCLR Token Contract<br/>Optimism Blockchain"]
        end
        
        subgraph "Authentication Flow"
            SIGNUP["Sign Up/Sign In<br/>idToken JWT Storage"]
            DATABASE["User Database<br/>Email, appPubkey, Address"]
        end
    end
    
    WEB3AUTH --> SIGNUP
    SIGNUP --> DATABASE
    SIGNUP --> PROFILE
    PROFILE --> AICHAT
    AICHAT --> SNAPSHOT
    SNAPSHOT --> INCLQ
    SNAPSHOT --> INCLR
```

**Inclusive.AI Platform Components**
This diagram illustrates the technical architecture of the Inclusive.AI platform, showing how Web3 authentication integrates with democratic voting mechanisms through blockchain-based tokens.

The platform uses several key technical components:
- `Web3Auth` for generating MPC wallets while maintaining simple email-based authentication
- `Snapshot` spaces and proposals for transparent voting on value questions
- `INCLQ` and `INCLR` vote token contracts deployed on Optimism for gas-efficient voting
- `Quillforms` for profile data collection to ensure representative participation

Sources: [projects/inclusive_ai_a_chatgpt_plugin_and_dao_to_engage_marginalized_groups_in_ai/README.md:1-83]()

### Technical Innovation Projects

These projects focused on novel technical approaches to incorporating democratic input directly into AI model development and evaluation.

```mermaid
graph LR
    subgraph "Technical Innovation Approaches"
        
        subgraph "Democratic Fine-Tuning"
            CHAT_DIALOGUE["Chat Dialogues<br/>Value Elicitation"]
            MORAL_GRAPH["Moral Graph<br/>Value Relationships"]
            MODEL_TUNING["Model Fine-Tuning<br/>Alignment Process"]
            
            CHAT_DIALOGUE --> MORAL_GRAPH
            MORAL_GRAPH --> MODEL_TUNING
        end
        
        subgraph "Generative Social Choice"
            FREE_TEXT["Free-text Opinions<br/>Large-scale Collection"]
            DISTILLATION["Mathematical Distillation<br/>Social Choice Theory"]
            SLATE["Concise Slate<br/>Fair Representation"]
            
            FREE_TEXT --> DISTILLATION
            DISTILLATION --> SLATE
        end
        
        subgraph "Case Law Approach"
            SCENARIOS["AI Interaction Scenarios<br/>Case Repository"]
            EXPERT_JUDGMENT["Expert + Laypeople<br/>Democratic Engagement"]
            CASE_LAW["Case-Law Judgments<br/>AI Policy Framework"]
            
            SCENARIOS --> EXPERT_JUDGMENT
            EXPERT_JUDGMENT --> CASE_LAW
        end
    end
```

**Technical Innovation Methods**
This shows three distinct technical approaches to incorporating democratic input: value-based model fine-tuning, mathematical opinion synthesis, and case-law-inspired policy development.

Sources: [README.md:77-118]()

## Implementation Status and Results

### Completed Experiments

The most extensively documented project is the Collective Dialogues initiative, which completed full end-to-end policy development cycles for three domains:

**Medical Advice Policy Development**
```mermaid
timeline
    title Medical Advice Policy Development Timeline
    
    section Pre-testing
        8/15/23 : CD1 Pre-test A
                : General AI assistant guidelines
        8/16/23 : CD1 Pre-test C [med]
                : Medical advice focus
                : N=50, cost=$333
    
    section Live Collective Dialogues  
        8/18/23 : CD1 Live Session
                : N=200, cost=$3726
                : Real-time deliberation
        8/30/23 : CD2 Live Session
                : Policy refinement
                : N=228, cost=$3700
    
    section Policy Evolution
        8/22/23 : Initial Policy v0.1
                : 9 policy clauses
        8/23/23 : Expert Review v0.2
                : Medical professional feedback
        8/28/23 : Public Feedback v0.4
                : Pre-test integration
        8/31/23 : Final Policy v0.5
                : >80% public support
```

**Medical Advice Policy Evolution Timeline**
This timeline shows the systematic development of AI medical advice policies through multiple rounds of public input, expert review, and refinement.

The final policy (v0.5) includes specific guidelines for:
- Emergency situation assessment and response [projects/collective_dialogues_for_democratic_input/experiments/research_log.md:38-42]()
- Mental health crisis support protocols [projects/collective_dialogues_for_democratic_input/experiments/research_log.md:43-45]()
- Medical information sharing with source prioritization [projects/collective_dialogues_for_democratic_input/experiments/research_log.md:47-51]()
- Basic health advocacy and minor ailment assistance [projects/collective_dialogues_for_democratic_input/experiments/research_log.md:52-55]()

Sources: [projects/collective_dialogues_for_democratic_input/experiments/research_log.md:1-500]()

### Project Outcomes and Metrics

The grant program generated diverse outputs across methodological approaches:

| Project Type | Key Metrics | Technical Artifacts | Policy Outputs |
|--------------|-------------|-------------------|----------------|
| Collective Dialogues | N=1000+ participants, >80% policy support | 10+ Jupyter notebooks, GPT-4 pipelines | Medical, conflict, vaccine policies |
| Inclusive.AI | Web3Auth + Snapshot integration | Vote token contracts on Optimism | DAO governance mechanisms |
| Platform Projects | Multi-modal data synthesis | Custom platforms and interfaces | Process frameworks |
| Technical Projects | Novel algorithmic approaches | Mathematical models, fine-tuning methods | Alignment methodologies |

**Integration with Core Platform**

Several grant projects contributed components that integrate with the main deliberation platform documented elsewhere in this wiki:

```mermaid
graph TB
    subgraph "Grant Project Integration"
        GRANT_PROJECTS["Grant Projects<br/>Independent Methodologies"]
        
        subgraph "Core Platform Components"
            FRONTEND["Frontend Systems<br/>packages/frontend"]
            ORCHESTRATOR["AI Orchestration<br/>packages/orchestrator"] 
            DATABASE["Data Layer<br/>packages/data"]
        end
        
        subgraph "Shared Infrastructure"
            GRAPHQL["GraphQL API<br/>Real-time Data"]
            SUPABASE["Supabase<br/>Database & Auth"]
            OPENAI_API["OpenAI API<br/>AI Processing"]
        end
        
        GRANT_PROJECTS -.->|"Methodology Insights"| FRONTEND
        GRANT_PROJECTS -.->|"AI Processing Patterns"| ORCHESTRATOR
        GRANT_PROJECTS -.->|"Data Structures"| DATABASE
        
        FRONTEND --> GRAPHQL
        ORCHESTRATOR --> OPENAI_API
        DATABASE --> SUPABASE
    end
```

**Grant Project and Core Platform Integration**
This shows how insights and methodologies from grant projects inform the development of the main deliberation platform, while sharing common infrastructure components.

Sources: [README.md:1-183](), [projects/collective_dialogues_for_democratic_input/README.md:19-26]()

## Research Contributions and Future Directions

The grant projects collectively demonstrate several key findings for democratic AI governance:

### Methodological Insights

1. **Scalable Deliberation**: Projects like Collective Dialogues prove that structured deliberative processes can work at scale (N=1000+) while maintaining quality consensus outcomes
2. **Technical Integration**: Platforms like Inclusive.AI show how Web3 technologies can enable transparent, sybil-resistant democratic participation
3. **Multi-Modal Synthesis**: Projects demonstrate effective techniques for synthesizing diverse input types (text, audio, structured votes) into coherent policy outputs

### Technical Innovations

The projects contributed several reusable technical patterns:
- Bridging-based consensus algorithms for identifying widely-supported positions
- GPT-4 policy generation pipelines with human validation loops  
- Blockchain-based voting mechanisms with democratic token distribution
- Multi-stage refinement processes incorporating both expert and public feedback

### Open Questions and Future Work

The grant program identified several areas requiring further research:
- Scaling considerations for different democratic input mechanisms
- Integration between multiple democratic input methodologies
- Long-term evaluation of policy effectiveness and public acceptance
- Cross-cultural adaptation of democratic input processes

Sources: [projects/collective_dialogues_for_democratic_input/experiments/research_log.md:171-183](), [projects/collective_dialogues_for_democratic_input/README.md:1-49]()

---

