# Challenge 1: Build Agents

Time: ~30 minutes

## Objectives

By the end of this challenge, you will have:

- ✅ An **Intent Classification Agent** that analyzes call summaries and categorizes customer intent
- ✅ A **Resolution Advisor Agent** that recommends optimal handling strategies
- ✅ Both agents tested against real call center data

![build](./images/build.png)

## Context

NovaTel Communications receives hundreds of calls daily. Each call has a summary, customer history, and account context. Your agents need to:

1. **Intent Classification**: Analyze the call to determine what the customer needs (billing dispute, tech issue, cancellation risk, upsell opportunity, etc.)
2. **Resolution Advisory**: Given a classified intent + customer context, recommend the best resolution path with scripts, escalation decisions, and available offers

Check out [call_data.json](./call_data.json) to see today's incoming calls.

## Portal or SDK?

Microsoft Foundry gives you two ways to build agents. The **Foundry portal** ([ai.azure.com/nextgen](https://ai.azure.com/nextgen)) provides a visual, no-code interface where you can create agents, attach tools, and test them interactively in a playground — great for exploration and rapid prototyping. The **Azure AI Agents SDK** gives you full programmatic control: you define agent behavior, tools, and orchestration logic in Python, which makes it easy to version, test, and integrate into automated pipelines.

![foundry](./images/foundry.png)

In this challenge we use the **SDK**. The code in [agents.py](./agents.py) creates both agents, registers their tools, and runs them against every call in `call_data.json` — all from the terminal. After the script runs, both agents will also be visible in the portal under **Agents**, so you can inspect them, tweak their instructions, and test them interactively without touching any code.

## Agents and Tools

### What is an agent?

An agent in Microsoft Foundry is a persistent, stateful AI assistant backed by a large language model. Unlike a plain API call — where you send a prompt and get a single response — an agent maintains a **conversation thread**, can **invoke tools autonomously**, and **retains context** across multiple turns. You configure it with:

- A **name** and **model** (e.g. `gpt-5.4`)
- A **system prompt** — instructions that define its role, personality, and constraints
- One or more **tools** it can call when it needs information or actions beyond its training data

Agents are managed resources in your Foundry project. They persist between runs, appear in the portal under **Agents**, and can be versioned, shared, and reused.

### What are tools?

Tools extend an agent's capabilities beyond pure language generation. When the model decides it needs information it doesn't have in its context window, it emits a **tool call** — a structured JSON request specifying the tool name and arguments. The SDK intercepts this, runs the corresponding Python function, and feeds the result back to the model. This reasoning loop continues until the agent produces a final response.

From the model's perspective, tools are described by a **JSON schema** (name, description, parameters). The model reads these descriptions and decides autonomously when and how to call them — you never hard-code the decision logic.

### What tools can you add?

| Tool type | What it does | Best for |
|-----------|-------------|----------|
| **Function** | Calls a local Python function you define | Any custom logic: database lookups, APIs, calculations |
| **Code Interpreter** | Lets the agent write and execute Python in a sandbox | Data analysis, chart generation, file processing |
| **File Search** | Semantic search over a Microsoft Foundry knowledge base | Policy docs, manuals, historical records |
| **Bing Search** | Live web search | Real-time information, news |
| **Azure AI Search** | Queries an Azure Search index | Grounded retrieval over your own data at scale |

#### Vector databases and Microsoft Foundry knowledge bases

When your agent needs to answer questions grounded in a large body of documents — policy manuals, product specs, historical records — you need a **vector database**. Unlike keyword search, a vector database converts text into numerical embeddings and finds semantically similar passages at query time. This lets the agent ask a natural-language question and retrieve the right content even when the exact words don’t appear in the query.

**Microsoft Foundry** includes a built-in knowledge base backed by a vector store. You upload documents (PDFs, Word files, plain text) and the service automatically chunks, embeds, and indexes them. When you attach this knowledge base to an agent as a **File Search** tool, the agent queries it at inference time — pulling relevant passages into its context before generating a response, so its answers are grounded in your actual documents rather than model training data alone.

For the NovaTel call center, useful knowledge bases would include:

- **Customer service policy manual** — refund thresholds, escalation rules, retention offer eligibility by plan tier
- **Product & plan documentation** — features by tier, billing cycles, device return windows, roaming policies
- **Resolution scripts** — approved language for billing disputes, cancellation saves, and upsell conversations

With this in place, the **Resolution Advisor Agent** could query “what retention offers apply to a Premium customer of 3+ years wanting to cancel?” and retrieve the exact offer details from the playbook — rather than hallucinating plausible-sounding but potentially incorrect policies.

In this challenge the agents use **function tools**. The **Intent Classification Agent** uses `lookup_customer` to pull account history and customer tier before deciding intent. Without this tool, the agent would have to guess from the call summary alone — with it, every classification is grounded in real account data.

## Get Started

Open [agents.py](./agents.py) and review the implementation of both agents.

```bash
cd callcenter/challenge-1-build
python agents.py
```

As the script runs, watch the terminal closely — you'll see each agent being created, then each call from `call_data.json` being sent through the **Intent Classification Agent** first, and its output handed off to the **Resolution Advisor Agent**. You'll see the raw agent responses printed for every call, giving you a live view of how the two agents collaborate. Once it completes, head to the [Microsoft Foundry portal](https://ai.azure.com/nextgen), open your project, and navigate to **Agents** in the left sidebar — hit **Refresh** if the agents don't appear immediately, as it can take a few seconds for newly created agents to show up in the portal.


## Success Criteria

- [ ] Intent Classification Agent correctly identifies all 6 intent types across 7 calls
- [ ] Resolution Advisor provides actionable recommendations with scripts and escalation decisions
- [ ] Security concerns are always escalated; billing disputes offer appropriate credits
