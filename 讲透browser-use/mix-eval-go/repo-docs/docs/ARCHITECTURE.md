# Architecture

## Evaluation Ecosystem

Mix-Eval-Go is part of a unified evaluation ecosystem with multiple specialized runners sharing a common backend.

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  evaluation-platform                        │
│                  (Convex Backend + UI)                      │
│  - Shared test cases database                               │
│  - Results storage                                          │
│  - REST API endpoints                                       │
│  - Screenshot storage                                       │
└────────┬──────────────┬──────────────┬─────────────────────┘
         │              │              │
         │ REST API     │ REST API     │ REST API
         │              │              │
    ┌────┴───┐     ┌────┴───┐     ┌───┴──────┐
    │        │     │        │     │          │
    ▼        ▼     ▼        ▼     ▼          ▼
┌─────────────┐ ┌─────────────┐ ┌──────────────────┐
│ manus-eval  │ │ mix-eval-go │ │ evaluations-     │
│ (Python)    │ │ (Go)        │ │ internal         │
│             │ │             │ │ (Python)         │
│ Targets:    │ │ Targets:    │ │ Targets:         │
│ Manus Agent │ │ Mix Agent   │ │ browser-use      │
│ (tool-based)│ │ (new agent) │ │ (DOM-based)      │
└─────────────┘ └─────────────┘ └──────────────────┘
```

## Repository Roles

### evaluation-platform
Central hub providing shared infrastructure for all evaluation runners. Built with React + Convex, it stores test cases, manages runs, hosts judge evaluations, and provides REST API endpoints used by all runners.

### manus-eval (Python)
Evaluates the Manus agent, which uses explicit tool calls (browser_*, bash, python, read, write) for task execution. Tracks detailed tool calls with arguments, results, and sandbox files. Included as a git submodule in the manus-use repository.

### mix-eval-go (Go, this repository)
Newest evaluation runner built in Go for the Mix Agent. Uses the Mix Go SDK and communicates via HTTP + SSE. Architecturally inspired by manus-eval but rewritten for performance and type safety.

### evaluations-internal (Python)
Original evaluation framework targeting the browser-use agent with DOM-based automation. Predecessor to both manus-eval and mix-eval-go, maintaining similar structure but focused on traditional browser automation patterns.

## Key Characteristics

All runners share the same evaluation-platform backend, enabling consistent task definitions and result comparison across different agents. Each runner specializes in its target agent's execution model while following similar architectural patterns: fetch tasks, execute with agent, evaluate with Claude judge, submit results.

Mix-Eval-Go distinguishes itself through Go's performance benefits, compile-time type safety, and single-binary deployment, making it ideal for production environments requiring high concurrency and minimal operational overhead.

## Implementation Status

See [IMPLEMENTATION_STATUS.md](../IMPLEMENTATION_STATUS.md) for detailed status.

**Current Status:** Phase 2-4 complete (Go-Eval Orchestrator)

**Known Limitation:** Mix Agent CDP support (Phase 1) not yet implemented - currently uses local browser mode

## Technical Details

### SSE Streaming

Mix-Eval-Go uses **manual HTTP streaming** instead of the SDK's `StreamEvents()` method due to a known bug where events aren't properly collected. The implementation:

- Opens HTTP GET to `/stream?sessionId={id}`
- Parses SSE format (`data: {...}`) with `bufio.Scanner`
- Waits 1 second for stream connection before sending messages
- Properly captures `tool_execution_start`, `content`, and `complete` events

See `pkg/orchestrator/orchestrator.go:156-207` and `test/e2e/browser_automation_test.go:165-237` for implementation details.
