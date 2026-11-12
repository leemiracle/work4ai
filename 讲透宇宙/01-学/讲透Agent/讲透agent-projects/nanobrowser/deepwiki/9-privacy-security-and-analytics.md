<!-- source: DeepWiki mcp.deepwiki.com · repo nanobrowser/nanobrowser · page 9 Privacy, Security and Analytics · fetched 2026-10-29 -->

# Privacy, Security and Analytics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PRIVACY.md](PRIVACY.md)
- [SECURITY.md](SECURITY.md)
- [src/agent/__tests__/overflow-recovery.test.ts](src/agent/__tests__/overflow-recovery.test.ts)
- [src/agent/guards.ts](src/agent/guards.ts)
- [src/background/checks/analytics.ts](src/background/checks/analytics.ts)

</details>



This page provides a high-level overview of Nanobrowser's security posture, safety guardrails, privacy guarantees, and analytics architecture. Nanobrowser is designed around a local-first processing model where user conversations, credentials, and API keys remain strictly local to the browser [PRIVACY.md:13-16](). 

This parent page summarizes key aspects of the safety, privacy, and telemetry implementations. For deep technical details, refer to the child pages:
- [Safety Guardrails and Site Permissions](#9.1) — Covers prompt-injection guards (`src/agent/guards.ts`), consequential-action classification, hardcoded never-allowed actions, per-site allow/ask/block rules, and the permissions UI.
- [Analytics and Telemetry](#9.2) — Covers `src/extension/analytics.ts`, analytics payload structures, opt-out handling, and data collection policies.

---

## 1. Local-First Processing and API Key Management

Nanobrowser operates entirely within the browser environment [PRIVACY.md:13-13](). All user conversations, attachments, saved shortcuts, and custom instructions are stored locally using browser storage APIs [PRIVACY.md:14-14](). Authentication cookies and sensitive field values (such as passwords and payment cards) never leave the local browser context through the extension [PRIVACY.md:15-16]().

API keys supplied by users for LLM providers are stored locally and transmitted exclusively to their respective endpoints [PRIVACY.md:38-41](). They are never exposed in exports or system logs [PRIVACY.md:42-43]().

```mermaid
graph TD
    subgraph "Natural Language Space"
        User[""User API Key Input""]
        BrowserStorage[""Local Browser Storage""]
    end
    
    subgraph "Code Entity Space"
        SettingsStore[""settingsStorage (@src/store)""]
        LLMProviderModule[""src/llm/providers.ts""]
    end
    
    User -->| "Enters Key" | SettingsStore
    SettingsStore -->| "Persists Locally" | BrowserStorage
    BrowserStorage -->| "Loads Key" | LLMProviderModule
    LLMProviderModule -->| "Direct API Call only" | ExternalLLM[""Authorized LLM Endpoint""]
    
    classDef default stroke:#333,stroke-width:2px;
```
**Diagram: Local API Key Isolation and Flow**

Sources:
* [PRIVACY.md:13-16]()
* [PRIVACY.md:38-43]()

---

## 2. Safety Guardrails and Site Permissions

To protect users from unintended actions, malicious web pages, and prompt injection attacks, Nanobrowser enforces deterministic guardrails and permission tiers. The agent treats web page text strictly as data rather than executable instructions.

Key safety mechanisms include:
- **Consequential Action Gating:** Sensitive actions such as submitting, sending, deleting, or uploading require explicit user approval in **Ask mode** (the default).
- **Hardcoded Never-Allowed Actions:** Certain actions, such as direct handling of payment fields or passwords without user handover, are restricted or handed over directly to the user.
- **Loop and Error Defenses:** The `Guards` class in `src/agent/guards.ts` tracks repeated tool calls, consecutive failures, and null-effect loops, issuing nudges or stopping the run automatically [src/agent/guards.ts:45-86]().

For detailed information on prompt-injection defense, action classification, and site rules, see [Safety Guardrails and Site Permissions](#9.1).

```mermaid
graph TD
    subgraph "Natural Language Space"
        AgentGoal[""Agent Tool Call""]
        UserPrompt[""User Approval Prompt""]
    end
    
    subgraph "Code Entity Space"
        GuardsClass[""Guards (src/agent/guards.ts)""]
        RunManager[""RunManager (src/extension/run-manager.ts)""]
        PromptBroker[""PromptBroker (src/extension/prompt-broker.ts)""]
    end
    
    AgentGoal -->| "Inspects Signature" | GuardsClass
    GuardsClass -->| "Evaluates Repeat/Error limits" | RunManager
    RunManager -->| "Checks Ask/Auto Mode" | PromptBroker
    PromptBroker -->| "Requests confirmation if consequential" | UserPrompt
    
    classDef default stroke:#333,stroke-width:2px;
```
**Diagram: Guardrails and Action Dispatch Flow**

Sources:
* [src/agent/guards.ts:45-86]()

---

## 3. Anonymous Analytics and Telemetry

Nanobrowser collects minimal, anonymous telemetry to monitor stability and guide development, utilizing PostHog [PRIVACY.md:19-25](). Analytics are completely optional and can be managed directly via settings or privacy UI cards [PRIVACY.md:22-24]().

- **Daily Pings:** Tracks general metadata such as browser type, UI language, and whether an active run occurred, without identifying specific users [PRIVACY.md:22-22]().
- **Usage Counts:** Counts aggregated daily execution metrics, feature usage (e.g., voice input, attachments, shortcuts), and error codes [PRIVACY.md:23-23]().
- **Opt-Out Control:** Users can turn off daily pings and usage statistics at any time in the settings menu, which immediately flushes pending local counters [PRIVACY.md:50-52]().

For a full breakdown of the analytics event schema, payload fields, and test coverage (`src/background/checks/analytics.ts`), see [Analytics and Telemetry](#9.2).

Sources:
* [PRIVACY.md:19-25]()
* [PRIVACY.md:50-52]()
* [src/background/checks/analytics.ts:1-25]()

---

## 4. LLM Provider Data Flow and Vulnerability Reporting

When executing browser automation tasks, Nanobrowser transmits necessary context (such as text content and tab screenshots) directly between the user's browser and their chosen LLM provider [PRIVACY.md:31-34](). Nanobrowser acts solely as a local conduit; data processing is governed by the respective provider's privacy policies [PRIVACY.md:35-36]().

### Vulnerability Reporting
If you discover a security vulnerability within Nanobrowser, please do not disclose it publicly in issues or pull requests [SECURITY.md:5-5](). Instead, report it confidentially through the [GitHub Security Advisory](https://github.com/nanobrowser/nanobrowser/security/advisories/new) interface so that it can be addressed safely [SECURITY.md:7-7]().

Sources:
* [PRIVACY.md:31-36]()
* [SECURITY.md:5-7]()

---

