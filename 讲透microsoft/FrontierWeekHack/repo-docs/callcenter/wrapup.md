# 🎉 Lab Complete — Call Center Triage (NovaTel Communications)

Congratulations — you've built, instrumented, evaluated, and deployed a production-ready multi-agent AI system from scratch. Here's what you accomplished.

---

## Recap

| # | Challenge | What You Built |
|---|-----------|----------------|
| 0 | **Setup** | Provisioned a Microsoft Foundry Resource, project, GPT model deployment, Log Analytics workspace, and Application Insights instance via a single `deploy.sh` script |
| 1 | **Build Agents** | Created an **Intent Classification Agent** (classifies billing, tech, cancellation, upsell, security intents with a `lookup_customer` tool) and a **Resolution Advisor Agent** (recommends retention offers and actions per customer tier) |
| 2 | **Monitor** | Enabled OpenTelemetry GenAI tracing — every model call, tool invocation, and token count is captured as a distributed trace in Application Insights |
| 3 | **Evaluate** | Ran systematic LLM-as-judge evaluations across the full call dataset, producing repeatable coherence and fluency scores you can version-track across prompt changes |
| 4 | **Production Workflow** | Wired both agents into an orchestrated pipeline in the Foundry portal — a stable, testable endpoint with run history that supervisors can inspect |

### Skills you practiced

- Designing agent system prompts with clear role boundaries and constraints
- Grounding agents in real data via tool calls (function calling)
- Distributed tracing for AI systems with OpenTelemetry
- LLM-as-judge evaluation with the Azure AI Evaluation SDK
- Multi-agent orchestration in the Foundry portal

---

## Next Steps

Want to take the NovaTel system further? Here are some directions:

- **Add more agents** — a Sentiment Analysis agent that scores call tone, or a Knowledge Base agent that retrieves troubleshooting articles before the resolution advisor responds
- **Connect real data** — replace the static `call_data.json` with a live CRM query or a telephony webhook
- **Improve evaluation** — add task-specific evaluators (e.g., "did the agent offer a retention discount to a cancellation-risk Premium customer?") alongside the generic coherence scores
- **Set up CI/CD** — run your evaluation dataset automatically on every prompt change using GitHub Actions and fail the build if quality scores drop below a threshold
- **Explore fine-tuning** — use your traced conversations as training data to fine-tune a smaller, cheaper model for intent classification
- **Try another scenario** — the [Factory](../factory/README.md) and [Claims](../claims/README.md) scenarios cover predictive maintenance and insurance processing using the same lifecycle

---

## Clean Up Azure Resources

> **Important:** The resources deployed in Challenge 0 incur Azure costs while they exist. Delete them when you're done.

### What gets deleted

- The resource group `foundry-hackathon-rg-<suffix>` and everything inside it:
  - Microsoft Foundry Resource + project
  - GPT model deployment
  - Log Analytics workspace
  - Application Insights instance

### Option 1 — Script

Run the cleanup script from the repo root:

```bash
bash callcenter/cleanup.sh
```

The script reads the `.env` file written by `deploy.sh` so it knows exactly which resource group to target. It asks for confirmation before deleting.

### Option 2 — Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **Resource groups**
3. Find `foundry-hackathon-rg-<your-suffix>`
4. Click **Delete resource group** and confirm

### Option 3 — Azure CLI

```bash
# Replace <suffix> with the value shown in your .env file
az group delete --name foundry-hackathon-rg-<suffix> --yes --no-wait
```
