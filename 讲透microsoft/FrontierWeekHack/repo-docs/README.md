<img width="990" height="150" alt="Microsoft Agent-a-thon_banner_WEB_990x150" src="https://github.com/user-attachments/assets/5f550061-077d-421c-bba2-4a5820e72fad" />

# Build and Scale AI Agents with Microsoft Foundry
## The Level 3: Architect learning path 
 
Welcome to the hands-on lab experience where ideas turn into real, enterprise-ready solutions. This is the most advanced of the three agent-building learning paths. Where the Explorer path builds your first no-code agent and the Maker path automates work with low-code tools, this path is for developers, engineers, and architects who want complete control over models, orchestration, and operations.

In this lab, you’ll build, monitor, evaluate, and orchestrate AI agents using the Microsoft Foundry SDK. You’ll follow a guided, scenario-based experience designed to help you move from concept to a working, enterprise-ready multi-agent system.
 
By the end, you won’t just understand how agents work — you’ll have built one you can trace, evaluate, and deploy.

All challenge instructions are also available at [microsoft.github.io/FrontierWeekHack](https://microsoft.github.io/FrontierWeekHack/).

## What You'll Learn

This lab walks you through the full lifecycle of building production-ready AI agents with [Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/):

- **Agent design** — Create purpose-built agents with system prompts, tools, and domain-specific data
- **Observability** — Instrument agents with OpenTelemetry-based GenAI tracing via Application Insights
- **Quality evaluation** — Run LLM-as-judge evaluations to systematically measure agent output quality
- **Multi-agent orchestration** — Wire agents into automated workflows using the Python SDK and the Foundry portal

This is a **code-first hackathon** — you'll write and run Python throughout. However, several challenges also have you interact with the **Microsoft Foundry portal** to deploy models, explore traces, review evaluations, and build workflows visually. Expect to move between your IDE and the portal regularly.


## Choose Your Scenario

All paths teach the same Foundry concepts — pick the one that resonates with you the most:

| Scenario | Description | Start Here |
|----------|-------------|------------|
| 🏭 **Factory** | Detect machine anomalies and diagnose faults at TireForge Industries | [Factory Lab](./factory/README.md) |
| 📋 **Claims** | Triage incoming claims and recommend actions at ClaimSight Insurance | [Claims Lab](./claims/README.md) |
| 📞 **Call Center** | Classify call intents and advise resolutions at NovaTel Communications | [Call Center Lab](./callcenter/README.md) |

All scenarios follow the same 5-challenge structure:

| # | Challenge | Duration | What You'll Learn |
|---|-----------|----------|-------------------|
| 0 | **Setup** | 20 min | Provision Microsoft Foundry, deploy a model, verify auth |
| 1 | **Build Agents** | 35 min | Create two agents with tools and system prompts |
| 2 | **Monitor** | 20 min | Enable GenAI tracing with Application Insights |
| 3 | **Evaluate** | 25 min | Run LLM-as-judge evaluations against test datasets |
| 4 | **Workflow** | 20 min | Orchestrate agents in a multi-step pipeline |

## Prerequisites

- **Azure subscription** with **Contributor** and **Foundry User** access
- A **GitHub account**
- **Python 3.10+** installed locally (pre-installed when using Codespaces)
- **Azure CLI** (`az`) installed (pre-installed when using Codespaces)

## Ready to Expand Your Knowledge?

### 1. Put Your Skills to the Test at the Microsoft Agent-a-Thon!
You’ve built production-grade agents — now bring them to a live, hands-on build experience. The Microsoft Agent-a-Thon is where you apply everything from this path, get real-time support as you build, and compete for recognition and prizes. Register at [Microsoft Agent-a-Thon](https://www.microsoft.com/en-us/events/local-events/microsoft-agent-a-thon).

### 2. Join the Tour! 

<img width="4400" height="687" alt="banner" src="agentichacks.jpg" />

Prefer to build alongside experts in the room? Spend a full day exploring advanced use cases, hands-on builds, and expert-led sessions designed to turn ideas into real business impact. Find the event nearest you on [EMEA Agentic AI Hacks - Microsoft Pulse](https://pulse.microsoft.com/en/build-ai-hacks-agentic-ai/).

### 3. Go deeper with the docs

- [What is Microsoft Foundry?](https://learn.microsoft.com/azure/foundry/what-is-foundry)
- [Foundry Agent Service overview](https://learn.microsoft.com/azure/foundry/agents/overview)
- [Trace your agents with Microsoft Foundry](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup)
- [Evaluate agentic workflows](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)
- [azure-ai-projects SDK Reference](https://learn.microsoft.com/python/api/azure-ai-projects/)

### 4. Keep learning on Microsoft Learn

- [Develop an AI agent with Microsoft Foundry Agent Service](https://learn.microsoft.com/training/modules/develop-ai-agent-azure/) — 55 min module
- [Build agent-driven workflows using Microsoft Foundry](https://learn.microsoft.com/training/modules/build-agent-workflows-microsoft-foundry/) — 1 hr module
- [Analyze and debug your generative AI app with tracing](https://learn.microsoft.com/training/modules/tracing-generative-ai-app/) — 1 hr module
- [Evaluate generative AI performance in Microsoft Foundry portal](https://learn.microsoft.com/training/modules/evaluate-models-azure-ai-studio/) — 38 min module
- [Monitor your generative AI application](https://learn.microsoft.com/training/modules/monitor-generative-ai-app/) — 1 hr module
- [Develop generative AI apps in Azure](https://learn.microsoft.com/training/paths/develop-generative-ai-apps/) — learning path
- [Monitor AI workloads on Azure](https://learn.microsoft.com/training/paths/monitor-ai-workloads-on-azure/) — learning path
- [Operationalize AI responsibly with Azure AI Foundry](https://learn.microsoft.com/training/paths/operationalize-ai-responsibly/) — learning path
