<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/agent-lightning · page 6 Examples & Recipes · fetched 2026-10-26 -->

# Examples & Recipes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/50-example-calc-x.md](docs/50-example-calc-x.md)
- [docs/75-example-coding-agent.md](docs/75-example-coding-agent.md)

</details>



The `examples/` directory catalogs implementation patterns for **Harnessed Agentic RL**, demonstrating how to train agents using real tools, context, and control flows by routing interactions through the `agl-server` proxy [docs/50-example-calc-x.md:7](). Each recipe is self-contained, supplying agent logic, training configurations, and orchestration scripts (`run_local.sh`, `run_minikube.sh`, or `run.sh`) [docs/50-example-calc-x.md:53-68](), [docs/75-example-coding-agent.md:81-98]().

Sources: [docs/50-example-calc-x.md:7](), [docs/75-example-coding-agent.md:81-98]()

---

## 6.1 Math & Tool-Use Examples

These examples focus on reasoning tasks where the agent leverages external tools or structured thought processes to derive a final answer. **Calc-X** is a math reasoning agent built with **AutoGen** and **MCP calculator tools** [docs/50-example-calc-x.md:7](). It demonstrates how to wrap a tool-using agent for reinforcement learning with minimal GPU overhead using `verl` [docs/50-example-calc-x.md:7](). The example supports both local multi-process execution (`run_local.sh`) and Kubernetes/Minikube jobs (`run_minikube.sh`) [docs/50-example-calc-x.md:9-14](). **GSM8K** handles grade-school math reasoning tasks, showcasing support for both standard Chat Completions and raw Completions APIs.

### Natural Language to Code Entity Space: Math RL
The following diagram maps the natural language math problem-solving flow to the concrete code entities managing tool execution and reward computation.

**Math Tool-Use Topology**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        "Question"["MathProblemPrompt"]
        "AnsFormat"["AnswerConventionFormat"]
    end

    subgraph "CodeEntitySpace"
        "Agent"["Agent (examples.calc_x.calc_agent.Agent)"]
        "Tool"["McpCalculator / stdioserver"]
        "Proxy"["ProxyRouter (agl-server)"]
        "Trainer"["AgentLightningRayPPOTrainer"]
        "Config"["build_config()"]
    end

    "Question" --> "Agent"
    "Agent" -->|"ToolCall"| "Proxy"
    "Proxy" -->|"Executes"| "Tool"
    "Tool" -->|"Result"| "Agent"
    "Agent" -->|"FinalAnswer"| "AnsFormat"
    "AnsFormat" -->|"RewardSignal"| "Trainer"
    "Config" -->|"Overrides"| "Trainer"
```
Sources: [docs/50-example-calc-x.md:7-14](), [examples/calc_x/train_calc_agent.py:13-100]()

For details on dataset preparation, GRPO configuration, and reward calculation, see [Math & Tool-Use Examples](#6.1).

Sources: [docs/50-example-calc-x.md:1-73]()

---

## 6.2 Search & Retrieval Examples

These examples involve multi-turn interactions with external environments or information retrieval backends. **Search-R1** implements multi-turn retrieval-augmented reasoning using a dedicated retrieval server and tool-calling interfaces to optimize information retrieval prior to generation. **ScienceWorld** operates within an interactive text-based environment for scientific problem-solving, employing trajectory-level aggregation and multi-turn credit assignment.

For technical details on the retrieval server setup, trajectory aggregation, and environment configuration, see [Search & Retrieval Examples](#6.2).

Sources: [docs/75-example-coding-agent.md:1-17]()

---

## 6.3 Coding Agent Examples

Agent Lightning provides recipes for training coding agents that interact directly with real filesystems and compilers. **SWE-smith** utilizes a `bash` action space and repository unit tests as ground-truth reward signals, executing each rollout as an isolated Kubernetes Job [docs/75-example-coding-agent.md:7](). The setup involves a multi-machine architecture separating the Kubernetes controller machine (Machine A) from the GPU training machine (Machine B) [docs/75-example-coding-agent.md:9-14](). **LLM-in-Sandbox** leverages the `llm-in-sandbox` library to execute agent-generated code inside secure Kubernetes Jobs, isolating the host environment during training.

### Natural Language to Code Entity Space: Coding Rollouts
This diagram illustrates how natural language coding requirements are translated into sandboxed execution environments via Kubernetes reconcilers and job templates.

**Coding Sandbox Topology**
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        "Issue"["GitHubIssuePrompt"]
        "Test"["PytestUnitResult"]
    end

    subgraph "CodeEntitySpace"
        "Runner"["K8sReconciler"]
        "Job"["KubernetesJobManifest"]
        "Agent"["CodingAgentClass"]
        "Env"["llm-in-sandbox"]
        "Gateway"["agl-server"]
    end

    "Issue" --> "Agent"
    "Agent" -->|"RequestJob"| "Runner"
    "Runner" -->|"Render"| "Job"
    "Job" -->|"Contains"| "Env"
    "Env" -->|"Returns"| "Test"
    "Test" -->|"Reward"| "Agent"
    "Agent" -->|"ProxyCall"| "Gateway"
```
Sources: [docs/75-example-coding-agent.md:7-14]()

For details on Jinja2 templates, Docker image management, network isolation, and K8s Job execution, see [Coding Agent Examples](#6.3).

Sources: [docs/75-example-coding-agent.md:1-118]()

---

## 6.4 Multimodal QA Example

The **Multimodal QA** example demonstrates training Vision-Language Models (VLMs) on synthetic visual reasoning tasks. The implementation handles `image_url` content parts through the proxy layer and applies rule-based reward scoring. Orchestration scripts coordinate local Ray clusters alongside `agl-server` and `agl-controller` instances for training execution.

For details on image-based reward scoring, `mrope` position IDs, and orchestration scripts, see [Multimodal QA Example](#6.4).

Sources: [docs/50-example-calc-x.md:1-73]()

---

## 6.5 Agent Skills

The `skills/` directory documents the **Agent Skills** specification, enabling coding agents to function as agent optimizers via the `agent-lightning` skill format. It defines action spaces using `SKILL.md` configurations, supports `.claude-plugin/plugin.json` integration metadata, and incorporates automated release tooling.

For technical details on the skill schema and installation instructions, see [Agent Skills](#6.5).

Sources: [docs/75-example-coding-agent.md:1-118]()

---

