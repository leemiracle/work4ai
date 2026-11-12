# Multi-Agent System Template

> Fill this out and send to Claude Code, Cursor, or any AI coding assistant to scaffold your multi-agent system using the OpenAI Agents SDK.

---

## Project Overview

[One sentence describing what this system does]

**Tech stack:**
- Framework: OpenAI Agents SDK (`openai-agents`)
- UI: Streamlit (or specify alternative)
- Model: [e.g., gpt-4o, huggingface/model-name via LiteLLM]

---

## Agents

### Agent 1: [Name]

| Field | Value |
|-------|-------|
| **Role** | [What this agent does] |
| **Handoff Description** | [How other agents know when to route here - be specific] |
| **Tools** | [List tool names, or "None"] |
| **Hands off to** | [List agent names this agent can transfer to] |

**Routine:**
1. [First step]
2. [Second step]
3. [Escape condition - when to hand off to another agent]

---

### Agent 2: [Name]

| Field | Value |
|-------|-------|
| **Role** | [What this agent does] |
| **Handoff Description** | [How other agents know when to route here] |
| **Tools** | [List tool names] |
| **Hands off to** | [List agent names] |

**Routine:**
1. [First step]
2. [Second step]
3. [Escape condition]

---

### Agent 3: [Name]

| Field | Value |
|-------|-------|
| **Role** | [What this agent does] |
| **Handoff Description** | [How other agents know when to route here] |
| **Tools** | [List tool names] |
| **Hands off to** | [List agent names] |

**Routine:**
1. [First step]
2. [Second step]
3. [Escape condition]

---

*(Copy this section for additional agents)*

---

## Shared Context

Define the state that persists across all agents:

```python
class [ProjectName]Context(BaseModel):
    field_1: str | None = None  # [description]
    field_2: str | None = None  # [description]
    field_3: int | None = None  # [description]
```

---

## Tools

### Tool: [tool_name]

| Field | Value |
|-------|-------|
| **Purpose** | [What this tool does] |
| **Inputs** | [parameter: type - description] |
| **Output** | [What it returns] |
| **Side effects** | [Any context updates, or "None"] |

**Implementation notes:**
- [Any API calls, database queries, or external services needed]
- [Mock behavior for demo, if applicable]

---

### Tool: [tool_name_2]

| Field | Value |
|-------|-------|
| **Purpose** | [What this tool does] |
| **Inputs** | [parameter: type - description] |
| **Output** | [What it returns] |
| **Side effects** | [Any context updates] |

**Implementation notes:**
- [Details]

---

*(Copy this section for additional tools)*

---

## UI Requirements

### Layout
- [ ] Chat interface (main area)
- [ ] Sidebar with agent status
- [ ] Context display
- [ ] Event log (handoffs, tool calls)
- [ ] Reset/clear button

### Agent Transitions Display
- [ ] Show current active agent
- [ ] Display handoff events (from → to)
- [ ] Display tool calls with names
- [ ] Display tool outputs (truncated if long)

### Styling (optional)
- [Color scheme, icons, branding notes]

---

## File Structure

```
project/
├── app.py           # Streamlit UI
├── main.py          # CLI demo (optional)
├── pyproject.toml   # Dependencies
├── README.md        # Setup instructions
└── .env             # API keys (gitignored)
```

---

## Dependencies

```toml
[project]
dependencies = [
    "openai-agents[litellm]>=0.6.5",
    "python-dotenv>=1.2.1",
    "streamlit>=1.45.0",
]
```

---

## Environment Variables

```env
OPENAI_API_KEY=your_key_here
# Or for other providers:
HF_TOKEN=your_huggingface_token
ANTHROPIC_API_KEY=your_anthropic_key
```

---

## Additional Notes

[Any other requirements, constraints, or context the coding agent should know]

---

# Example: Filled Template

<details>
<summary>Click to see a complete example (Airline Customer Service)</summary>

## Project Overview

Airline customer service bot with FAQ and seat booking capabilities.

**Tech stack:**
- Framework: OpenAI Agents SDK
- UI: Streamlit
- Model: huggingface/nscale/Qwen/Qwen3-8B via LiteLLM

## Agents

### Agent 1: Triage Agent

| Field | Value |
|-------|-------|
| **Role** | Entry point, routes to specialists |
| **Handoff Description** | Routes customer requests to appropriate agents |
| **Tools** | None |
| **Hands off to** | FAQ Agent, Seat Booking Agent |

**Routine:**
1. Greet customer
2. Identify intent from their message
3. Hand off to FAQ Agent for questions, Seat Booking Agent for reservations

### Agent 2: FAQ Agent

| Field | Value |
|-------|-------|
| **Role** | Answer questions about airline policies |
| **Handoff Description** | Answers questions about baggage, seats, and WiFi |
| **Tools** | faq_lookup_tool |
| **Hands off to** | Triage Agent |

**Routine:**
1. Identify the question asked
2. Call faq_lookup_tool with the question
3. If tool returns "I don't know", hand back to Triage

### Agent 3: Seat Booking Agent

| Field | Value |
|-------|-------|
| **Role** | Update seat assignments |
| **Handoff Description** | Updates seat reservations for passengers |
| **Tools** | update_seat |
| **Hands off to** | Triage Agent |

**Routine:**
1. Ask for confirmation number
2. Ask for desired seat number
3. Call update_seat tool
4. If user asks unrelated question, hand back to Triage

## Shared Context

```python
class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None
```

## Tools

### Tool: faq_lookup_tool

| Field | Value |
|-------|-------|
| **Purpose** | Look up FAQ answers by keyword matching |
| **Inputs** | question: str - the user's question |
| **Output** | Answer string or "I don't know" |
| **Side effects** | None |

**Implementation notes:**
- Check for keywords: bag/baggage/luggage → return baggage policy
- Check for keywords: seat/seating → return seat info
- Check for keywords: wifi/internet → return wifi info
- Default: return "I don't know"

### Tool: update_seat

| Field | Value |
|-------|-------|
| **Purpose** | Update passenger seat assignment |
| **Inputs** | confirmation_number: str, new_seat: str |
| **Output** | "Updated seat to {new_seat} for confirmation {confirmation_number}" |
| **Side effects** | Updates context.seat_number and context.confirmation_number |

**Implementation notes:**
- Mock implementation (no real database)
- Always succeeds for demo purposes

## UI Requirements

### Layout
- [x] Chat interface (main area)
- [x] Sidebar with agent status
- [x] Context display as JSON
- [x] Event log (handoffs, tool calls)
- [x] Reset button

### Agent Transitions Display
- [x] Metric showing current agent name
- [x] Info boxes for handoffs
- [x] Warning boxes for tool calls
- [x] Success boxes for tool outputs

</details>
