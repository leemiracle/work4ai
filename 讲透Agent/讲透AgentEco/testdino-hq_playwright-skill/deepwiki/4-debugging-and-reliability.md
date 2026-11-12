<!-- source: DeepWiki mcp.deepwiki.com · repo testdino-hq/playwright-skill · page 4 Debugging and Reliability · fetched 2026-10-27 -->

# Debugging and Reliability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/debugging.md](core/debugging.md)

</details>



This page provides a high-level overview of diagnosing test failures, analyzing traces, and eliminating flakiness within the playwright-skill framework. For deep technical details, error playbooks, and advanced configuration, refer to the child pages linked below.

- [Debugging Workflows and Error Index](#4.1) — Debug modes, common pitfalls, error message index and playbooks.
- [Trace Analysis](#4.2) — `trace.zip` anatomy, terminal trace CLI, snapshots (DOM, ARIA, screen), agent-native failure triage.
- [Flaky Tests and Dynamic Test Selection](#4.3) — Root causes of flakiness, retries, `retryStrategy` isolated, `reporter.preprocess` quarantine via external APIs.

---

## 4.1 Debugging Workflows and Error Index

Systematic diagnosis starts with understanding the tools available in the testing runtime, such as UI Mode, the Playwright Inspector, and trace viewers [core/debugging.md:7-17](). Most failures can be resolved by following a structured workflow that avoids guesswork—starting from reading the error message, moving through interactive exploration, and ending with deep trace inspection [core/debugging.md:19-36].

For details, see [Debugging Workflows and Error Index](#4.1).

```mermaid
graph TD
    A["User Failure Report"] --> B["UI Mode npx playwright test --ui"]
    A --> C["Playwright Inspector PWDEBUG=1"]
    B --> D["PlaywrightTestRunner core/debugging.md"]
    C --> D
    
    Sources: core/debugging.md:7-17
```

Sources: `core/debugging.md:7-17`, `core/debugging.md:19-36`

---

## 4.2 Trace Analysis

When tests fail in CI or non-interactive environments, post-mortem analysis relies heavily on trace archives (`trace.zip`). Traces capture action snapshots, network activity, console logs, and DOM states [core/debugging.md:140-188]. Developers and AI coding agents use terminal commands like `npx playwright show-trace` to inspect artifacts and isolate the root cause [core/debugging.md:140-167].

For details, see [Trace Analysis](#4.2).

```mermaid
graph TD
    A["CI Failure Artifact"] --> B["trace.zip Archive"]
    B --> C["CLI Viewer npx playwright show-trace"]
    C --> D["TraceViewerNode core/debugging.md"]
    
    Sources: core/debugging.md:140-188
```

Sources: `core/debugging.md:140-188`

---

## 4.3 Flaky Tests and Dynamic Test Selection

Flakiness undermines test suite reliability. Addressing root causes involves configuring robust retries (such as `trace: 'on-first-retry'`) [core/debugging.md:147-158], isolating state, and leveraging reporting hooks or quarantine mechanisms to prevent intermittent failures from blocking pipelines. 

For details, see [Flaky Tests and Dynamic Test Selection](#4.3).

Sources: `core/debugging.md:147-158`

---

