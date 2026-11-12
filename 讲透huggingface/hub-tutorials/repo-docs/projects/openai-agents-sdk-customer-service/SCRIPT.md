# Multi-Agent Customer Service with OpenAI Agents SDK

**Video Script | ~15 min | Target: Experienced Devs**

---

## 1. HOOK [0:00 - 0:45]

**[ON SCREEN: Streamlit chat interface with agent panel]**

Today we're building a multi-agent customer service system using the OpenAI Agents SDK. But I want to be upfront: for this simple airline FAQ demo, you don't *need* multiple agents. A single agent with a few tools would work fine.

So why multi-agent? Because this is a **learning demo**—we're exploring the patterns, handoffs, and architecture decisions that matter when you *do* need multiple agents. And with tools like Claude Code, you won't be writing this code line-by-line anyway. What matters is understanding **what to ask for**.

By the end, I'll give you a template you can fill out and send to any coding agent to scaffold your own multi-agent system.

---

## 2. WHEN MULTI-AGENT ACTUALLY MATTERS [0:45 - 2:30]

**[ON SCREEN: Comparison table]**

This demo is simple. Here's where multi-agent architecture genuinely shines:

### Real Production Use Cases

| Use Case | Why Multi-Agent? |
|----------|------------------|
| **Document processing pipeline** | Classifier → Extractor → Validator → Summarizer. Each stage has different prompts, models, and failure modes. |
| **Code review system** | Security agent, style agent, performance agent—each with specialized knowledge. Combine their feedback. |
| **Research assistants** | Planner agent breaks down queries, researcher agents fetch from different sources, synthesizer combines results. |
| **E-commerce support** | Order tracking, returns, product questions, escalation to human—each with different tool access and policies. |
| **Data analysis workflows** | Query planner, SQL executor, visualization generator, insight summarizer—handoffs with intermediate validation. |

### When Single Agent is Better

- Simple Q&A with < 5 tools
- Tasks that don't have clear domain boundaries
- When latency matters more than specialization
- Prototyping before you understand the problem space

---

## 3. ARCHITECTURE OVERVIEW [2:30 - 4:00]

**[ON SCREEN: Agent graph visualization]**

```
         ┌─────────────┐
         │   Triage    │
         │    Agent    │
         └──────┬──────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  FAQ Agent  │   │ Seat Agent  │
└─────────────┘   └─────────────┘
```

This is **hub-and-spoke** architecture. Triage is the router. Specialists handle domains.

**Key components:**
- **Agents**: Each has a name, instructions, tools, and handoff targets
- **Handoffs**: How agents transfer control to each other
- **Context**: Shared state that flows through the system
- **Tools**: Actions agents can take (API calls, lookups, etc.)

---

## 4. CORE CONCEPTS [4:00 - 7:30]

### 4.1 The handoff_description

```python
faq_agent = Agent(
    name="FAQ Agent",
    handoff_description="Answers questions about baggage, seats, and WiFi policies.",
)
```

This is the agent's **advertisement**. Other agents read this to decide where to route. Be specific—vague descriptions lead to wrong routing.

### 4.2 The Routine Pattern

```python
instructions="""
You are an FAQ agent.
# Routine
1. Identify the last question asked.
2. Use the faq lookup tool to answer.
3. If you cannot answer, transfer back to triage.
"""
```

Numbered steps give the agent a clear workflow. Every agent needs an **escape hatch**—what to do when it can't handle something.

### 4.3 Bidirectional Handoffs

```python
triage_agent.handoffs = [faq_agent, seat_agent]
faq_agent.handoffs = [triage_agent]
seat_agent.handoffs = [triage_agent]
```

Specialists can hand back to triage. This prevents dead-ends when users change topics.

### 4.4 Shared Context

```python
class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
```

Context flows through handoffs automatically. Tools can update it:

```python
async def update_seat(ctx: RunContextWrapper[AirlineAgentContext], ...):
    ctx.context.seat_number = new_seat
```

---

## 5. STREAMLIT DEMO [7:30 - 10:00]

**[ON SCREEN: Running Streamlit app]**

```bash
uv run streamlit run app.py
```

**[SHOW: Sidebar with agent status, context, and events]**

The sidebar shows:
- **Current Agent**: Which agent is active
- **Context**: The shared state (passenger info, seat, etc.)
- **Events**: Real-time handoffs and tool calls

**[DEMO: Conversation flow]**

```
User: "hello"
→ Triage Agent responds

User: "is my bag allowed in the cabin?"
→ Handoff to FAQ Agent
→ Tool call: faq_lookup_tool
→ FAQ Agent responds

User: "can I change my seat?"
→ Handoff back to Triage
→ Handoff to Seat Booking Agent
→ Seat Agent asks for confirmation number
```

**Key observation**: Users see one coherent assistant. The multi-agent orchestration is invisible to them.

---

## 6. BUILDING WITH AI CODING AGENTS [10:00 - 12:00]

**[ON SCREEN: Template document]**

You don't need to memorize this code. With Claude Code, Cursor, or similar tools, you describe what you want and they generate it.

The trick is knowing **what to specify**. Here's my template:

### Multi-Agent System Template

```markdown
## Project Overview
[One sentence describing the system's purpose]

## Agents

### Agent 1: [Name]
- **Role**: [What this agent does]
- **Handoff Description**: [How other agents know when to route here]
- **Tools**: [List of tools this agent can use]
- **Hands off to**: [Which agents it can transfer to]
- **Routine**:
  1. [Step 1]
  2. [Step 2]
  3. [Escape condition - when to hand off]

### Agent 2: [Name]
...

## Shared Context
[What data needs to persist across agents]
- field_1: type
- field_2: type

## Tools

### Tool 1: [name]
- **Purpose**: [What it does]
- **Inputs**: [Parameters]
- **Output**: [What it returns]
- **Side effects**: [Any context updates]

## UI Requirements
- [Chat interface description]
- [What to show in sidebar/panels]
- [How to display agent transitions]
```

---

## 7. EXAMPLE: FILLING THE TEMPLATE [12:00 - 13:30]

**[ON SCREEN: Filled template for this project]**

Here's how this airline demo maps to the template:

```markdown
## Project Overview
Airline customer service bot with FAQ and seat booking capabilities.

## Agents

### Agent 1: Triage Agent
- **Role**: Entry point, routes to specialists
- **Handoff Description**: Routes customer requests to appropriate agents
- **Tools**: None
- **Hands off to**: FAQ Agent, Seat Booking Agent
- **Routine**:
  1. Greet customer
  2. Identify intent
  3. Hand off to appropriate specialist

### Agent 2: FAQ Agent
- **Role**: Answer questions about airline policies
- **Handoff Description**: Answers questions about baggage, seats, and WiFi
- **Tools**: faq_lookup_tool
- **Hands off to**: Triage Agent
- **Routine**:
  1. Identify the question
  2. Call faq_lookup_tool
  3. If can't answer, hand back to Triage

### Agent 3: Seat Booking Agent
- **Role**: Update seat assignments
- **Handoff Description**: Updates seat reservations for passengers
- **Tools**: update_seat
- **Hands off to**: Triage Agent
- **Routine**:
  1. Ask for confirmation number
  2. Ask for desired seat
  3. Call update_seat tool
  4. If unrelated question, hand back to Triage

## Shared Context
- passenger_name: str | None
- confirmation_number: str | None
- seat_number: str | None
- flight_number: str | None

## Tools

### Tool 1: faq_lookup_tool
- **Purpose**: Look up FAQ answers by keyword
- **Inputs**: question (str)
- **Output**: Answer string
- **Side effects**: None

### Tool 2: update_seat
- **Purpose**: Update passenger seat assignment
- **Inputs**: confirmation_number (str), new_seat (str)
- **Output**: Confirmation message
- **Side effects**: Updates context.seat_number and context.confirmation_number

## UI Requirements
- Streamlit chat interface
- Sidebar showing: current agent, context state, recent events
- Display handoffs as info messages
- Display tool calls as warnings
- Reset button to clear conversation
```

---

## 8. WRAP-UP [13:30 - 14:00]

**[ON SCREEN: Resources list]**

**What we covered:**
- Multi-agent architecture patterns (hub-and-spoke)
- When multi-agent makes sense vs single agent
- Core concepts: handoffs, context, routines
- How to specify requirements for AI coding agents

**Next steps:**
- Fork the repo and extend with new agents
- Try the template on your own use case
- Connect to real backends instead of mock tools

---

## RESOURCES

- [OpenAI Agents SDK Docs](https://openai.github.io/openai-agents-python/)
- [Template file](./TEMPLATE.md)
- [Cookbook example](https://github.com/openai/openai-agents-python/blob/main/examples/customer_service/main.py)

---

## APPENDIX: FULL TEMPLATE

See [TEMPLATE.md](./TEMPLATE.md) for a copy-paste ready version.
