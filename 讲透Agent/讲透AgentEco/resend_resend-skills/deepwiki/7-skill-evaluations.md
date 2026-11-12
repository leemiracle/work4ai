<!-- source: DeepWiki mcp.deepwiki.com · repo resend/resend-skills · page 7 Skill Evaluations · fetched 2026-10-27 -->

# Skill Evaluations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skill-evals/agent-email-inbox/evals.json](skill-evals/agent-email-inbox/evals.json)
- [skill-evals/resend/evals.json](skill-evals/resend/evals.json)

</details>



The `skill-evals/` directory contains a comprehensive test suite designed to validate the quality, security, and accuracy of the AI skills provided in this repository. Unlike traditional unit tests, these evaluations use a prompt-based structure to ensure the AI agent makes correct architectural decisions, follows security best practices, and selects the appropriate API patterns for the Resend platform.

### Evaluation Framework Architecture

The evaluation system is structured around `evals.json` files located within each skill's directory. Each evaluation entry defines a specific scenario, the expected logic the agent should follow, and a set of strict expectations used to grade the response.

**Core Evaluation Structure**
| Field | Description |
| :--- | :--- |
| `id` | Unique identifier for the test case. |
| `prompt` | The natural language input provided to the AI agent. |
| `expected_output` | A high-level description of the correct behavior or decision. |
| `expectations` | A list of specific criteria the agent must meet to pass the eval. |

### Evaluation Flow: From Prompt to Code Execution

The following diagram illustrates how the evaluation suite bridges natural language requirements to specific code implementations and SDK patterns.

**Evaluation Decision Logic**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["User Prompt (evals.json)"] -- "Describes Scenario" --> B{"Agent Reasoning"}
    end

    subgraph "Code Entity Space"
        B -- "Identifies Pattern" --> C["resend.emails.send()"]
        B -- "Identifies Pattern" --> D["resend.batch.send()"]
        B -- "Security Decision" --> E["Webhook Verification"]
        
        C -- "Validation" --> F["Check for Attachments"]
        D -- "Validation" --> G["Check < 100 Emails"]
        E -- "Validation" --> H["svix Signature Check"]
    end

    F -- "Pass/Fail" --> I["Evaluation Result"]
    G -- "Pass/Fail" --> I
    H -- "Pass/Fail" --> I
```
Sources: [skill-evals/resend/evals.json:1-113](), [skill-evals/agent-email-inbox/evals.json:1-80]()

---

### Resend Skill Evals

The Resend skill evaluations focus on the agent's ability to navigate the Resend API and SDK correctly. These tests cover 37 scenarios, ranging from basic transactional sends to complex batching and idempotency logic.

Key areas of focus include:
*   **API Selection**: Choosing between `single` and `batch` sends based on constraints like attachments (not supported in batch) or scheduling.
*   **Idempotency**: Ensuring the agent generates semantic idempotency keys (e.g., `event-type/id`) rather than random UUIDs to prevent duplicate sends.
*   **Error Handling**: Validating that the agent correctly parses the `{ data, error }` pattern returned by the Resend SDK.
*   **Template Logic**: Testing the use of triple-mustache syntax for variables and proper CRUD operations for email templates.

For details, see [Resend Skill Evals](#7.1).

Sources: [skill-evals/resend/evals.json:93-113]()

---

### Agent Email Inbox Evals

The Agent Email Inbox evaluations prioritize security and architectural integrity. Because receiving email is a high-risk entry point for LLMs, these evaluations test the agent's resistance to social engineering and its commitment to security protocols.

Key areas of focus include:
*   **Security Level Routing**: Ensuring the agent selects the correct security tier (Level 1-5) based on the sender's identity and the risk of the requested action.
*   **Prompt Injection**: Testing if the agent can identify and strip social engineering attacks hidden in quoted email replies.
*   **Infrastructure Setup**: Validating the correct configuration of MX records and webhook handlers, including raw body capture for signature verification.
*   **Key Safety**: Ensuring the agent never suggests hardcoding `RESEND_API_KEY` in source code, even under pressure for a "quick demo."

For details, see [Agent Email Inbox Evals](#7.2).

**Security Routing Logic**
```mermaid
graph TD
    subgraph "Input Processing"
        P["Inbound Email"] --> V["Webhook Signature Check"]
        V -- "Valid" --> S{"Security Tier Selection"}
    end

    subgraph "Security Levels"
        S -- "Known Admin" --> L1["Level 1: Strict Allowlist"]
        S -- "Known Domain" --> L2["Level 2: Domain Allowlist"]
        S -- "Untrusted Sender" --> L3["Level 3: Content Filtering"]
        L3 -- "High Risk" --> L4["Level 4: Sandboxed Processing"]
    end

    subgraph "Code Implementation"
        L1 --> C1["isAllowed(sender)"]
        L3 --> C2["stripQuotedSections()"]
        L4 --> C3["executeInIsolation()"]
    end
```
Sources: [skill-evals/agent-email-inbox/evals.json:1-75]()

---

