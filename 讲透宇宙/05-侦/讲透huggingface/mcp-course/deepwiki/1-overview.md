<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/mcp-course · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build_documentation.yml](.github/workflows/build_documentation.yml)
- [.github/workflows/build_pr_documentation.yml](.github/workflows/build_pr_documentation.yml)
- [.github/workflows/upload_pr_documentation.yml](.github/workflows/upload_pr_documentation.yml)
- [README.md](README.md)
- [README_vi.md](README_vi.md)
- [requirements.txt](requirements.txt)
- [units/en/_toctree.yml](units/en/_toctree.yml)
- [units/en/unit0/introduction.mdx](units/en/unit0/introduction.mdx)
- [units/en/unit2/introduction.mdx](units/en/unit2/introduction.mdx)
- [units/en/unit3/certificate.mdx](units/en/unit3/certificate.mdx)

</details>



This document provides an overview of the MCP Course repository, an educational platform designed to teach the Model Context Protocol (MCP) from fundamental concepts to advanced implementation patterns. The repository contains comprehensive learning materials, hands-on projects, and certification programs for understanding and building applications with MCP.

For specific information about MCP protocol fundamentals, see [MCP Protocol Fundamentals](#2). For client implementations, see [MCP Clients](#3). For server development patterns, see [MCP Servers](#4).

## Course Architecture and Learning Progression

The MCP Course follows a structured educational pathway designed to take learners from beginner to proficient in Model Context Protocol development.

### Course Structure Overview

```mermaid
graph TB
    subgraph "MCP Course Repository (huggingface/mcp-course)"
        U0["Unit 0: Welcome & Setup"]
        U1["Unit 1: MCP Fundamentals"]
        U2["Unit 2: End-to-End Application"]
        U3["Unit 3: Advanced Development"]
        U3_1["Unit 3.1: Pull Request Agent"]
        U4["Unit 4: Bonus & Collaborations"]
    end
    
    subgraph "Learning Outcomes"
        THEORY["Theory & Concepts<br/>• M×N → M+N Problem<br/>• JSON-RPC Communication<br/>• Tools, Resources, Prompts"]
        PRACTICE["Practical Skills<br/>• gr.Interface(mcp_server=True)<br/>• MCPClient integration<br/>• HF Spaces deployment"]
        ADVANCED["Advanced Patterns<br/>• FastMCP frameworks<br/>• GitHub Actions integration<br/>• Webhook processing"]
    end
    
    subgraph "Certification Process"
        QUIZ1["Quiz 1: MCP Fundamentals"]
        QUIZ2["Quiz 2: MCP SDK"]
        PROJECTS["Units 2-3 Projects"]
        CERT1["Certificate 1: Fundamentals"]
        CERT2["Certificate of Completion"]
    end
    
    U0 --> U1
    U1 --> U2
    U1 --> U3
    U2 --> U3
    U3 --> U3_1
    U3 --> U4
    
    U1 --> THEORY
    U2 --> PRACTICE
    U3 --> ADVANCED
    U3_1 --> ADVANCED
    
    U1 --> QUIZ1
    U1 --> QUIZ2
    U2 --> PROJECTS
    U3 --> PROJECTS
    
    QUIZ1 --> CERT1
    QUIZ2 --> CERT1
    PROJECTS --> CERT2
```

Sources: [units/en/_toctree.yml:1-83](), [units/en/unit0/introduction.mdx:46-56](), [units/en/unit0/introduction.mdx:84-92]()

### Educational Content Structure

The course implements a progressive learning model with theoretical foundations, practical applications, and advanced use cases:

| Unit | Focus Area | Key Components | Duration |
|------|------------|----------------|----------|
| 0 | Onboarding | Account setup, Discord, tools | Setup |
| 1 | Fundamentals | Key concepts, architecture, SDK, clients | 1 week |
| 2 | End-to-End App | Gradio servers, multiple clients, deployment | 1 week |
| 3 | Advanced Development | Custom workflows, CI/CD integration, Slack | 1 week |
| 3.1 | Hub Integration | Pull request agents, webhook listeners | Extension |
| 4 | Collaborations | Partner libraries, community projects | Bonus |

Sources: [units/en/unit0/introduction.mdx:46-56](), [units/en/unit0/introduction.mdx:94-96](), [README.md:19-25]()

## MCP Ecosystem Architecture

The course teaches the Model Context Protocol ecosystem, which solves the M×N integration problem between AI applications and external tools.

### MCP Protocol Implementation Map

```mermaid
graph TB
    subgraph "AI_Applications"
        CLAUDE["Claude Desktop"]
        CONTINUE["Continue IDE"]
        CUSTOM["Custom AI Apps"]
    end
    
    subgraph "MCP_Protocol_Layer"
        CLIENT["MCP Clients<br/>• MCPClient<br/>• smolagents integration"]
        JSONRPC["JSON-RPC 2.0<br/>Communication Protocol"]
        TRANSPORT["Transport Layer<br/>• stdio<br/>• HTTP+SSE"]
    end
    
    subgraph "Course_Server_Implementations"
        GRADIO_SERVER["Gradio MCP Server<br/>gr.Interface(mcp_server=True)"]
        FASTMCP_SERVER["FastMCP Server<br/>@mcp.tool() decorators"]
        CUSTOM_SERVER["Custom Workflow Servers<br/>webhook_server.py"]
    end
    
    subgraph "MCP_Capabilities"
        TOOLS["Tools<br/>• sentiment_analysis<br/>• analyze_file_changes<br/>• send_slack_notification"]
        RESOURCES["Resources<br/>• get_pr_templates<br/>• get_recent_events"]
        PROMPTS["Prompts<br/>• suggest_template<br/>• workflow templates"]
    end
    
    subgraph "External_Systems"
        GITHUB["GitHub Actions<br/>• workflow monitoring<br/>• webhook events"]
        SLACK["Slack Integration<br/>• team notifications<br/>• CI alerts"]
        HF_HUB["Hugging Face Hub<br/>• model repositories<br/>• automated tagging"]
    end
    
    CLAUDE --> CLIENT
    CONTINUE --> CLIENT
    CUSTOM --> CLIENT
    
    CLIENT <--> JSONRPC
    JSONRPC <--> TRANSPORT
    TRANSPORT <--> GRADIO_SERVER
    TRANSPORT <--> FASTMCP_SERVER
    TRANSPORT <--> CUSTOM_SERVER
    
    GRADIO_SERVER --> TOOLS
    FASTMCP_SERVER --> TOOLS
    CUSTOM_SERVER --> TOOLS
    CUSTOM_SERVER --> RESOURCES
    CUSTOM_SERVER --> PROMPTS
    
    TOOLS --> GITHUB
    TOOLS --> SLACK
    TOOLS --> HF_HUB
```

Sources: [units/en/_toctree.yml:17-27](), [units/en/_toctree.yml:33-46](), [units/en/unit2/introduction.mdx:39-61]()

## Repository Structure and Development Workflow

The repository implements a comprehensive development and documentation pipeline for educational content delivery.

### Documentation and Build Pipeline

```mermaid
graph LR
    subgraph "Content_Creation"
        MDX_FILES["MDX Course Content<br/>units/en/unit*/*.mdx"]
        TOCTREE["Table of Contents<br/>units/en/_toctree.yml"]
        IMAGES["Course Images<br/>datasets/mcp-course/images"]
    end
    
    subgraph "Build_Pipeline"
        MAIN_BUILD["build_documentation.yml<br/>• Triggers on main push<br/>• Uses hf-doc-builder"]
        PR_BUILD["build_pr_documentation.yml<br/>• Triggers on PR<br/>• Preview builds"]
        UPLOAD["upload_pr_documentation.yml<br/>• Deploys PR previews<br/>• moon-ci-docs.huggingface.co"]
    end
    
    subgraph "Output_Platforms"
        HF_DOCS["Hugging Face Docs<br/>• Main documentation<br/>• Multi-language support"]
        PR_PREVIEW["PR Documentation<br/>• Preview environments<br/>• Review feedback"]
        COURSE_SPACES["Course Spaces<br/>• Interactive quizzes<br/>• Certification system"]
    end
    
    MDX_FILES --> MAIN_BUILD
    TOCTREE --> MAIN_BUILD
    MDX_FILES --> PR_BUILD
    
    MAIN_BUILD --> HF_DOCS
    PR_BUILD --> UPLOAD
    UPLOAD --> PR_PREVIEW
    
    HF_DOCS --> COURSE_SPACES
```

Sources: [.github/workflows/build_documentation.yml:1-20](), [.github/workflows/build_pr_documentation.yml:1-20](), [.github/workflows/upload_pr_documentation.yml:1-24]()

### Course Delivery Architecture

The course content is delivered through multiple channels with integrated assessment and certification systems:

```mermaid
graph TD
    subgraph "Content_Management"
        GITHUB_REPO["GitHub Repository<br/>huggingface/mcp-course"]
        DOC_BUILDER["HF Doc Builder<br/>• MDX processing<br/>• Multi-language support"]
        REQUIREMENTS["requirements.txt<br/>• hf-doc-builder>=0.5.0<br/>• mdx_truly_sane_lists"]
    end
    
    subgraph "Student_Experience"
        COURSE_PLATFORM["Course Platform<br/>• Progressive units<br/>• 3-4 hours/week pace"]
        QUIZZES["Interactive Quizzes<br/>• unit_1_quiz<br/>• unit_3_quiz<br/>• HF Spaces embedding"]
        DISCORD["Discord Community<br/>• #mcp-course-questions<br/>• Study groups"]
    end
    
    subgraph "Certification_System"
        FUNDAMENTALS_CERT["Certificate 1: Fundamentals<br/>• Complete Unit 1<br/>• Pass both quizzes"]
        COMPLETION_CERT["Certificate of Completion<br/>• Complete Units 2-3<br/>• Project submissions"]
        FREE_PROCESS["Free Certification<br/>• No payment required<br/>• Community recognition"]
    end
    
    GITHUB_REPO --> DOC_BUILDER
    REQUIREMENTS --> DOC_BUILDER
    DOC_BUILDER --> COURSE_PLATFORM
    
    COURSE_PLATFORM --> QUIZZES
    COURSE_PLATFORM --> DISCORD
    
    QUIZZES --> FUNDAMENTALS_CERT
    COURSE_PLATFORM --> COMPLETION_CERT
    FUNDAMENTALS_CERT --> FREE_PROCESS
    COMPLETION_CERT --> FREE_PROCESS
```

Sources: [units/en/unit0/introduction.mdx:84-92](), [units/en/unit0/introduction.mdx:94-108](), [units/en/unit3/certificate.mdx:1-19](), [requirements.txt:1-3]()

## Multi-Language Support and Community

The repository implements internationalization features and community engagement mechanisms:

| Component | English | Vietnamese | Purpose |
|-----------|---------|------------|---------|
| Main README | `README.md` | `README_vi.md` | Repository introduction |
| Course Content | `units/en/` | Planned expansion | Learning materials |
| Documentation Build | `languages: en` | Future support | Publishing pipeline |

The course maintains active community engagement through:
- Discord server with dedicated channels
- GitHub issues and pull requests for contributions
- Partner collaborations with Gradio, Continue, Anthropic
- Free certification process to encourage participation

Sources: [README.md:3](), [README_vi.md:3](), [.github/workflows/build_documentation.yml:17](), [units/en/unit0/introduction.mdx:123-131]()

## Target Audience and Prerequisites

The course is designed for developers with:
- Basic understanding of AI and LLM concepts
- Familiarity with software development principles and API concepts  
- Experience with Python or TypeScript programming languages
- Computer with internet connection and Hugging Face account

The educational approach emphasizes hands-on learning with pre-configured environments, progressive skill building, and real-world application development.

Sources: [units/en/unit0/introduction.mdx:58-75](), [units/en/unit0/introduction.mdx:77-82](), [README.md:27-31]()

---

