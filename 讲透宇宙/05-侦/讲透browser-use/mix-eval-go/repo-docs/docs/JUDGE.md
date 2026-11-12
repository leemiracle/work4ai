# LLM Judge System

## Overview

The judge uses **Claude as a meta-evaluator** to assess whether an agent successfully completed a task. Evaluation happens **after** task execution completes, using the full execution trace.

## Task Execution Flow

```
┌─────────────────────────────────────────────────────┐
│              Task Execution Pipeline                │
└─────────────────────────────────────────────────────┘

1. Fetch task from Convex
   ├─ Task ID, description, website, etc.
   │
2. Create Mix session (agent instance)
   │
3. Start SSE event stream
   │
4. Send task message to agent
   │
5. Collect events in real-time
   ├─ Tool calls (browser actions, extractions)
   ├─ Screenshots
   ├─ Assistant responses
   │
6. Wait for completion event
   │
7. Retrieve full message history
   │
8. Extract execution history
   │
   ┌─────────────────────────────────────┐
   │    🔍 JUDGE EVALUATION             │  ← Happens HERE
   │    (after everything completes)     │
   └─────────────────────────────────────┘
   │
9. Upload screenshots to Convex storage
   │
10. Save TaskResult to Convex
```

## Judge Input/Output Schema

### **Inputs** (pkg/orchestrator/judge.go:28)

```go
// 1. Task
type Task struct {
    ID              string  // Task identifier
    Text            string  // Task description
    Website         string  // Target website (optional)
    LoginCookie     string  // Auth cookie (optional)
    BrowserProvider string  // Browser provider (optional)
}

// 2. ExecutionHistory
type ExecutionHistory struct {
    ToolCalls     []ToolCallDetail  // All tool executions
    FinalResponse string            // Agent's final text answer
    Reasoning     string            // Agent's reasoning/thinking
    TokensUsed    int64             // LLM tokens consumed
    Cost          float64           // Estimated cost
}

type ToolCallDetail struct {
    ID       string  // Tool call identifier
    Name     string  // Tool name (e.g., "browser_navigate")
    Input    string  // Tool input parameters
    Result   string  // Tool execution result
    IsError  bool    // Did tool call fail?
    Finished bool    // Tool execution completed?
}
```

### **Output** (pkg/convex/client.go:63)

```go
type Evaluation struct {
    Passed    bool     // Did agent complete the task?
    Score     float64  // Score from 0.0 to 1.0
    Reasoning string   // Judge's detailed explanation
    Errors    []string // Error categories (e.g., "incomplete", "wrong_answer")
}
```

## How Judge Evaluation Works

```
┌────────────────────────────────────────────────────────────┐
│                    Judge.Evaluate()                        │
└────────────────────────────────────────────────────────────┘

Step 1: Create temporary Mix session for evaluation

Step 2: Build evaluation prompt
        ┌──────────────────────────────────────────┐
        │ "Evaluate whether the agent              │
        │  successfully completed this task:       │
        │                                          │
        │  Task: {task.Text}                       │
        │                                          │
        │  Execution Summary:                      │
        │  - Tool calls: {count}                   │
        │  - Final response: {finalResponse}       │
        │  - Reasoning provided: {hasReasoning}    │
        │                                          │
        │  Respond with JSON:                      │
        │  {passed, score, reasoning, errors}      │
        │                                          │
        │  Be strict - only pass if fully done."   │
        └──────────────────────────────────────────┘

Step 3: Send prompt to Claude via Mix API

Step 4: Wait 5 seconds for processing

Step 5: Retrieve assistant's response

Step 6: Parse JSON evaluation from response

Step 7: Delete temporary session

Step 8: Return Evaluation struct
```

## Key Design Decisions

### ✅ What Judge Uses
- Task description (text)
- Tool call count
- Agent's final text response
- Agent's reasoning (if provided)

### ❌ What Judge Does NOT Use
- **Screenshots** - Judge cannot see captured images
- **Individual tool results** - Only sees count, not details
- **Streaming events** - Evaluation is post-execution only
- **Browser state** - No access to actual browser

### Limitations

1. **Text-only evaluation**: For visual tasks (e.g., "verify UI looks correct"), judge can't see screenshots and must rely on agent's textual description.

2. **No tool-level analysis**: Judge sees tool call count but not individual tool successes/failures or detailed results.

3. **Synchronous blocking**: Uses `time.Sleep(5s)` instead of streaming, which may timeout for slow responses.

4. **Stateless**: Each evaluation is isolated - no learning or consistency across evaluations.

## Location in Codebase

- **Judge implementation**: `pkg/orchestrator/judge.go`
- **Evaluation types**: `pkg/convex/client.go:63`
- **Execution history**: `pkg/orchestrator/extractor.go`
- **Orchestration**: `pkg/orchestrator/orchestrator.go:129`
