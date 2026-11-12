<!-- source: DeepWiki mcp.deepwiki.com · repo resend/resend-skills · page 4 Resend CLI Skill · fetched 2026-10-26 -->

# Resend CLI Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/resend-cli/SKILL.md](skills/resend-cli/SKILL.md)
- [skills/resend-cli/references/automations.md](skills/resend-cli/references/automations.md)
- [skills/resend-cli/references/logs.md](skills/resend-cli/references/logs.md)
- [skills/resend-cli/references/workflows.md](skills/resend-cli/references/workflows.md)

</details>



The **Resend CLI Skill** provides a Node.js-based command-line interface for interacting with the Resend platform. It is designed for developers to manage email infrastructure directly from the terminal, automate tasks via shell scripts, and integrate Resend into CI/CD pipelines [skills/resend-cli/SKILL.md:3-10]().

Beyond standard CRUD operations for platform resources, the CLI features a specialized **Agent Protocol** for non-interactive environments and built-in support for rendering **React Email** templates (`.tsx`) into HTML before sending [skills/resend-cli/SKILL.md:101-115, 174-177]().

### System Architecture: CLI to Code Mapping

The following diagram maps the high-level CLI concepts to their specific implementations and data structures within the codebase.

**CLI Entity Mapping**
```mermaid
graph TD
  subgraph "Natural Language / CLI Space"
    "Command Group"["Command Group (e.g., 'emails')"]
    "Global Flags"["Global Flags (--api-key, --json)"]
    "Agent Mode"["Agent Protocol (Non-TTY)"]
  end

  subgraph "Code Entity Space"
    "SKILL_MD"["skills/resend-cli/SKILL.md"]
    "REF_EMAILS"["references/emails.md"]
    "REF_LOGS"["references/logs.md"]
    "REF_ERRORS"["references/error-codes.md"]
    "ENV_KEY"["RESEND_API_KEY"]
  end

  "Command Group" --> "REF_EMAILS"
  "Command Group" --> "REF_LOGS"
  "Global Flags" --> "ENV_KEY"
  "Agent Mode" --> "SKILL_MD"
  "Agent Mode" --> "REF_ERRORS"
```
Sources: [skills/resend-cli/SKILL.md:12-61](), [skills/resend-cli/references/emails.md:1-5]()

---

### Command Groups Overview

The CLI organizes functionality into logical groups that mirror the Resend API. Each group supports standard operations like `list`, `create`, `get`, and `delete`.

| Command Group | Core Responsibilities |
| :--- | :--- |
| `emails` | Sending single/batch emails, scheduling, and tracking delivery status [skills/resend-cli/SKILL.md:133](). |
| `domains` | Domain registration, DNS record retrieval, and verification [skills/resend-cli/SKILL.md:135](). |
| `automations` | Managing multi-step workflows, step graphs, and execution runs [skills/resend-cli/SKILL.md:138](). |
| `broadcasts` | Creating and sending marketing campaigns to segments or topics [skills/resend-cli/SKILL.md:140](). |
| `webhooks` | Configuring event subscriptions and local webhook tunneling/listening [skills/resend-cli/SKILL.md:146](). |
| `logs` | Inspecting API request/response bodies for debugging [skills/resend-cli/SKILL.md:136](). |

For a complete list of flags and subcommands, see [CLI Commands Reference](#4.1).

---

### Agent Protocol & CI/CD Integration

The CLI is optimized for non-interactive environments (CI/CD, AI agents). It automatically detects if `stdin` is a TTY and adjusts its behavior accordingly [skills/resend-cli/SKILL.md:101-103]().

**Agent Protocol Flow**
```mermaid
graph LR
  "Terminal/Script" -- "resend emails send" --> "TTY Detection"
  "TTY Detection" -- "Non-TTY" --> "JSON Mode"
  "TTY Detection" -- "TTY" --> "Interactive Mode"
  
  subgraph "JSON Mode"
    "No Prompts"["Fail if flags missing"]
    "Quiet"["Suppress Spinners (-q)"]
    "Output"["Stdout: JSON Result / Stderr: JSON Error"]
  end

  subgraph "Interactive Mode"
    "Prompts"["Prompt for missing input"]
    "Spinners"["Show progress animations"]
    "Output_TTY"["Human-readable tables"]
  end
```
Sources: [skills/resend-cli/SKILL.md:101-115]()

**Key Agent Rules:**
*   **No Prompts:** The CLI will never prompt for input in non-TTY mode; all required flags must be provided [skills/resend-cli/SKILL.md:106]().
*   **Standardized Output:** Success results are printed to `stdout` as JSON, while errors are printed to `stderr` as JSON [skills/resend-cli/SKILL.md:109-112]().
*   **Safety Flags:** Commands that delete resources require the `--yes` flag to proceed without a confirmation prompt [skills/resend-cli/SKILL.md:114]().

For details on error codes and CI/CD setup, see [CLI Error Codes & CI/CD Integration](#4.3).

---

### Automation & Log Inspection

The CLI provides deep visibility into Resend's event-driven features. It allows users to define complex **Automations** using JSON files and inspect **API Logs** to debug integration issues.

*   **Automations:** You can create or update automations by passing a JSON file containing the `steps` and `connections` graph [skills/resend-cli/references/automations.md:17-27]().
*   **Logs:** While `logs list` provides a summary, `logs get <id>` retrieves the full `request_body` and `response_body` for any API call made to Resend [skills/resend-cli/references/logs.md:7-27]().

For more information on managing workflows, see [CLI Automations, Workflows & Logs](#4.2).

---

### Child Pages

*   **[CLI Commands Reference](#4.1)**: Comprehensive reference for all command groups, including `emails`, `domains`, `contacts`, and `templates`.
*   **[CLI Automations, Workflows & Logs](#4.2)**: Guide to managing automation step graphs, triggering events, and inspecting request logs.
*   **[CLI Error Codes & CI/CD Integration](#4.3)**: Details on the Agent Protocol, standardized error JSON, and React Email rendering via the CLI.

---

