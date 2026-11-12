![Banner](./assets/images/banner.png)

# Lab — Build AI Agents with Microsoft Foundry
Welcome to the hands-on lab for the **Microsoft Cloud & AI Frontier Week Hackathon** — where ideas turn into real solutions.

Throughout Frontier Week, you've explored how AI is transforming organizations. This is where you put that into practice.

In this lab, you'll **build, monitor, evaluate, and orchestrate AI agents** using the Microsoft Foundry SDK — following a guided, scenario-based experience designed to take you from concept to a working, enterprise-ready multi-agent system.

By the end, you won't just understand how agents work — you'll have built one you can **trace, evaluate, and deploy**.

## Choose Your Scenario

All three scenarios use the same five-challenge structure. Pick whichever industry fits your interest.

| Scenario | Domain | What You Build |
|----------|--------|----------------|
| [🏭 Factory](./factory/README.md) | Predictive Maintenance | Anomaly Detection + Fault Diagnosis agents |
| [📋 Claims](./claims/README.md) | Insurance Processing | Claims Triage + Claims Decision agents |
| [📞 Call Center](./callcenter/README.md) | Customer Support | Intent Classification + Resolution Advisor agents |

## Challenge Structure

Every scenario follows the same five challenges:

| # | Challenge | Duration |
|---|-----------|----------|
| 0 | **Setup** — Deploy Azure AI Foundry infrastructure | 20 min |
| 1 | **Build Agents** — Create two AI agents with tools | 30 min |
| 2 | **Monitor** — Enable GenAI tracing with Application Insights | 20 min |
| 3 | **Evaluate** — Run systematic quality evaluations | 30 min |
| 4 | **Workflow** — Multi-agent orchestration via the Foundry portal | 20 min |

## Prerequisites

- Azure subscription with Contributor access
- Python 3.10+
- Azure CLI (`az`) installed and authenticated (`az login`)
- A terminal (bash, PowerShell, or WSL)

## Getting Started

1. Clone this repo and pick a scenario folder (`factory/`, `claims/`, or `callcenter/`)
2. Start with **Challenge 0** — it provisions everything you need
3. Work through challenges 1–4 in order; each builds on the previous one
4. The `agents.py` and `deploy.py` scripts are ready to run — read the README in each challenge folder for what to do
