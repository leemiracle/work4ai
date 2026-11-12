# 🎉 Lab Complete — Predictive Maintenance (TireForge Industries)

Congratulations — you've built, instrumented, evaluated, and deployed a production-ready multi-agent AI system from scratch. Here's what you accomplished.

---

## Recap

| # | Challenge | What You Built |
|---|-----------|----------------|
| 0 | **Setup** | Provisioned a Microsoft Foundry Resource, project, GPT model deployment, Log Analytics workspace, and Application Insights instance via a single `deploy.sh` script |
| 1 | **Build Agents** | Created an **Anomaly Detection Agent** (reads live sensor telemetry — temperature, vibration, pressure — and identifies machines operating outside safe thresholds) and a **Fault Diagnosis Agent** (determines root cause and recommends maintenance actions per machine type) |
| 2 | **Monitor** | Enabled OpenTelemetry GenAI tracing — every model call, tool invocation, and token count is captured as a distributed trace in Application Insights |
| 3 | **Evaluate** | Ran systematic LLM-as-judge evaluations across the full sensor dataset, producing repeatable coherence and fluency scores you can version-track across prompt changes |
| 4 | **Production Workflow** | Wired both agents into an orchestrated pipeline in the Foundry portal — a stable, testable endpoint with run history that plant operators can inspect |

### Skills you practiced

- Designing agent system prompts with clear role boundaries and constraints
- Grounding agents in real sensor telemetry via tool calls (function calling)
- Distributed tracing for AI systems with OpenTelemetry
- LLM-as-judge evaluation with the Azure AI Evaluation SDK
- Multi-agent orchestration in the Foundry portal

---

## Next Steps

Want to take the TireForge system further? Here are some directions:

- **Add more agents** — a Parts Inventory agent that checks whether replacement components are in stock before recommending maintenance, or a Scheduling agent that finds the earliest maintenance window with minimal production impact
- **Connect real data** — replace the static `sensor_data.json` with a live IoT Hub or Azure Event Hub stream
- **Improve evaluation** — add task-specific evaluators (e.g., "did the agent correctly identify a Curing Press failure from elevated temperature + abnormal pressure combination?") alongside the generic coherence scores
- **Set up CI/CD** — run your evaluation dataset automatically on every prompt change using GitHub Actions and fail the build if quality scores drop below a threshold
- **Explore fine-tuning** — use your traced fault diagnoses as training data to fine-tune a smaller, cheaper model for the initial anomaly detection step
- **Try another scenario** — the [Claims](../claims/README.md) and [Call Center](../callcenter/README.md) scenarios cover insurance processing and customer support using the same lifecycle

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
bash factory/cleanup.sh
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
