# Samples

The Game Agent SDK includes a set of sample applications that demonstrate the Chat,
Agent, and RAG APIs in concrete scenarios. The sample source lives under
`source/samples/`; after a build the executables land in `_out/`.

The samples are intended as starting points showing how the SDK can be integrated for various use cases. Further tuning would be needed to improve response quality in a real application.

For an overview of the repository layout, see [API Overview](api-overview.md#whats-in-the-box).

## Building The Game Agent SDK Samples

The samples are built together with the rest of the SDK by the standard build
flow:

```bash
$ setup.bat
$ build.bat
```

`setup.bat` generates Visual Studio project files under `_project/vs2022/`.
`build.bat` invokes msbuild on the resulting solution; pass `-debug` for the
Debug configuration. Sample executables land in `_out/`.

If you're working from the SDK release zip (which ships only the prebuilt SDK
library plus the sample source under `samples/`), use the samples-only build
flow instead:

```bash
$ setup_samples.bat
$ build_samples.bat
```

That generates `_project/vs2022/ACE_Samples.sln` and writes the rebuilt
samples to `bin/`.

## Running The Game Agent SDK Samples

The samples have built-in default paths and can be run with no arguments. Run
them from the directory containing the built binaries (`_out/` after building
from source, or `bin/` when using the release zip):

```bash
$ cd _out
$ .\Agent-Sample.exe
```

Command line arguments are available to override the default model and
database paths; see each sample below.

## Agent-Sample
  **Description:** Demonstrates the ACE Agent APIs with multiple tools. This sample implements a poker assistant that uses two tools (`search` for poker knowledge search and `check_status` for retrieving relevant portions of the current game state) to answer user's questions. The agent autonomously decides which tools to call based on the user's question, receives tool results, and generates a contextual response.

  **Sample Source Code Filename:** `source/samples/Agent-Sample.cpp`

  **Command line arguments:**

  | Arg | Fullname | Meaning |
  | :--: | :------: | :------ |
  | -s | --slm | Path to SLM model file (.GGUF format) |
  | -e | --emb | Path to embedding model file |
  | -c | --cross | Path to cross encoder model |
  | -v | --vecdb | Path to semantic database |
  | -b | --bm25db | Path to lexical database |
  | -g | --gamestate | Path to game state JSON file (optional) |
  | -d | --debug | Enable tool execution output and set log level to InferenceDebug (optional) |
  |  | --no-cig | Disable CiG (CUDA in Graphics) (optional) |

  The `-g` argument loads a static JSON file that feeds the `check_status` tool. This is for testing purposes; in a real game the tool would query the game engine at runtime. If omitted, `check_status` returns empty results.

  **Run From The Command Line:**

  Run with no arguments to use the built-in default paths (assumes running from the binary output directory, `_out/` for source builds or `bin/` for the release zip):
  ```bash
  Agent-Sample.exe
  ```

  To override one or more paths, specify all required arguments:
  ```bash
  Usage: Agent-Sample.exe -s [pathToSLMModelFile]
                          -e [pathToEmbeddingModel]
                          -c [pathToCrossEncoderModel]
                          -v [pathToSemanticDB]
                          -b [pathToLexicalDB]
                          [-g pathToGameStateFile]
                          [-d] [--no-cig]
  ```

  ```bash
  Command Prompt: Agent-Sample.exe -s "../data/models/qwen3.5/Qwen3.5-4B-Q4_K_M.gguf" ^
                          -e "../data/models/miniLM/all-MiniLM-L6-v2.F32.gguf" ^
                          -c "../data/models/miniLM/cross_encoder_ms-marco-MiniLM-L6-v2.onnx" ^
                          -v "../data/dbs/poker.db" ^
                          -b "../data/dbs/poker-lexical.db" ^
                          -g "../data/game-states/poker/game-state.json"

  Powershell: .\Agent-Sample.exe -s "../data/models/qwen3.5/Qwen3.5-4B-Q4_K_M.gguf" `
                          -e "../data/models/miniLM/all-MiniLM-L6-v2.F32.gguf" `
                          -c "../data/models/miniLM/cross_encoder_ms-marco-MiniLM-L6-v2.onnx" `
                          -v "../data/dbs/poker.db" `
                          -b "../data/dbs/poker-lexical.db" `
                          -g "../data/game-states/poker/game-state.json"
  ```

  **Notes:** This sample demonstrates the Agent APIs for building agentic AI assistants with autonomous tool selection. The Agent APIs:
  - Orchestrate tool execution: detect tool requests, receive tool results, re-run the model
  - Handle conversation history windowing and serialization
  - Support transient and redacted message flags for one-shot steering and context-budget management
  - Provide a step-counter cap (`MaxSteps`) on autonomous tool-call chains, plus cancel/rollback and error reporting

  **Tools in this sample:**   
  | Tool | Purpose |
  | -------- | ------- |
  | search | Queries the poker knowledge base (RAG) for rules, hand rankings, odds, and strategy concepts |
  | check_status | Retrieves relevant portions of the current game state |

  **Game state:**
  The bundled game-state file is a single static snapshot. The sample doesn't run a real poker engine; utterances like "I call" or "I fold" don't advance state, and the next `check_status` returns the same data. In a real integration, the application should update game state between turns.

  **Inputs:**
  The user enters questions via the command line. The agent decides whether tool calls are necessary and which tools to use based on the question.

  **Expected Output:**

  Default:
  ```
  You: what's my hand?
  Your hand is **three of a kind** with **Kings** (K♦, K♥, K♣). The remaining cards (9♣, 7♠, 4♥) don’t improve your hand. You have a strong hand! 🃏

  You: should i call?
  Your hand is **three of a kind (Kings)**. With **46% pot odds** and a strong hand, **calling is a good decision**. The pot will grow, and you’re in a strong position.

  You: /exit
  ```

  With `-d` (tool execution details):
  ```
  You: what’s my hand??

  [TOOL EXECUTION] Executing 2 tool calls
  [TOOL] Executing: check_status (id: call_0)
  [TOOL] Executing: search (id: call_1)
    [SEARCH] Processing 1 queries with deduplication
    [SEARCH] Query: hand rankings
    [SEARCH] Found 6 results
    [SEARCH] Combined 1 queries: 6 unique results, 6 in output (2213 tokens), 0 duplicates removed
  [TOOL EXECUTION] Completed

  Your hand is **three of a kind** with **Kings** (K♦, K♥, K♣). The remaining cards (9♣, 7♠, 4♥) don’t improve your hand. You have a strong hand! 🃏
  ```

  With `/think-verbose` (reasoning tokens streamed before each response):
  ```
  You: what’s my hand??

  Think: {reasoning}
  ---
  Your hand is **three of a kind** with **Kings** (K♦, K♥, K♣). The remaining cards (9♣, 7♠, 4♥) don’t improve your hand. You have a strong hand! 🃏
  ```

  > **Note:** `-d` and `/think-verbose` are independent and can be used together.

## Chat-Sample
  **Description:** Demonstrates the ACE Chat APIs with tool calling and RAG. This sample implements a simplified version of the same poker assistant as Agent-Sample, using the same tools (`search` and `check_status`), the same system prompt, and the same RAG pipeline, but uses the lower-level Chat APIs instead of the Agent APIs.

  **When to use which:**
  - **Chat APIs**: A straightforward inference API. Good for simple use cases like one-shot Q&A or conversational flows that don't need tool calling. Also suited for applications that have their own orchestration layer and want full control over the inference loop (e.g., a server framework that manages conversation state externally, or an app porting an existing chat-completions-style integration).
  - **Agent APIs**: Build on the Chat APIs and manage the infer / tool calls / re-infer cycle, history windowing, transient and redacted messages, cancel/rollback, and serialization. A good fit when your application needs tool calling or multi-step reasoning and you want the SDK to manage that complexity.

  **Sample Source Code Filename:** `source/samples/Chat-Sample.cpp`

  **Command line arguments:** Same as Agent-Sample. Replace `Agent-Sample.exe` with `Chat-Sample.exe`.

  **Key differences from Agent-Sample:**

  The Chat-Sample covers the basic tool-calling loop (infer, inspect for tool calls, execute, append results, re-infer) but omits features the Agent APIs handle internally: the `MaxSteps` cap on autonomous tool-call chains, transient and redacted message flags, error status reporting, cancel/rollback, history windowing, and conversation serialization.

  Code-shape differences:

  - Uses `ACEModel::Chat()` with an `ACEChat` message list instead of `ACEAgent::Run()`
  - The caller drives the tool-calling loop: call `model->Chat()`, inspect the response for tool calls, execute them, append tool results to the chat, and re-infer
  - The caller manages conversation history by appending messages to the `ACEChat` directly
  - Response text (`Content()`) and tool calls (`ToolCalls()`) are checked explicitly on each response, mirroring how the Agent delivers `ACEAgentStatus_ResponseText` and `ACEAgentStatus_ToolCalls`

  | Chat APIs | Agent APIs |
  | -------- | ------- |
  | `model->Chat()` returns an `ACEChatMessage` | `agent->Run()` returns a status |
  | Check `response->Content()` | `ACEAgentStatus_ResponseText` |
  | Check `response->ToolCalls().Count() > 0` | `ACEAgentStatus_ToolCalls` |
  | `chat->Add().Role(ACEChatRole_Tool).ToolCallId(id).Content(result)` | `agent->AddToolResult(id, result)` |
  | `while` there are still tool calls to process | `while (status != Idle)` |

  **Inputs:**
  The user enters questions via the command line. The model decides whether tool calls are necessary and which tools to use based on the question.

  **Expected Output:**
  On short interactive sessions, responses look similar to Agent-Sample's. Where the Agent APIs handle features internally that the Chat APIs don't (see Key differences from Agent-Sample, above), behavior can diverge. `-d` and `/think-verbose` work the same way — see Agent-Sample's Expected Output for examples.

## MultiAgent-Sample
  **Description:** Demonstrates running two ACE Agents on top of a single SLM. The sample creates two agents with different system instructions, distinct identifiers, and independent conversation histories, and routes user input to whichever agent the user addresses.

  - `@carlos` is a poker player character at the table. First person, bold/aggressive tone, and has access only to `check_status` (sees his own hole cards as player index 2).
  - `@advisor` is a strategy assistant for player Alice. Has access to `search` (RAG) and `check_status` (sees Alice's hole cards as player index 0).

  **Sample Source Code Filename:** `source/samples/MultiAgent-Sample.cpp`

  **Command line arguments:** Same as Agent-Sample. Replace `Agent-Sample.exe` with `MultiAgent-Sample.exe`.

  **Console commands:**

  | Command | Action |
  | :-- | :-- |
  | `@carlos <msg>` / `@advisor <msg>` | Send a message to the named agent |
  | `@carlos /clear` / `@advisor /clear` | Clear that agent's conversation only |
  | `@carlos /cancel` / `@advisor /cancel` | Cancel that agent's in-flight inference (and pending tools) |
  | `@carlos /save <file>` / `@advisor /save <file>` | Save that agent's conversation |
  | `@carlos /load <file>` / `@advisor /load <file>` | Load that agent's conversation (cancels its pending tools first) |
  | `@<agent> /think-verbose` / `/think` / `/nothink` | Toggle thinking on that agent |
  | `/help` | Show all commands |
  | `/exit` | Quit |

  Each agent has its own inference options. By default Carlos has thinking off (matching his snap-decision persona); Advisor has thinking on with think tokens hidden. The `/think-verbose` / `/think` / `/nothink` subcommands toggle the active mode for one agent at a time via `ace_agentSetInferenceOption`.

  **Concurrency model:**

  Both agents share one `ACEModel`. The sample dispatches tool calls asynchronously via `std::async` so the main loop stays responsive: while one agent is waiting for `search` or `check_status` to complete, the user can send a message to the other agent. `ACEAgent::Run()` is always driven from the main loop thread, so inference itself is serialized across the two agents (one model, one inference at a time); the parallelism is purely in tool execution.

  An auxiliary stdin reader thread feeds a thread-safe queue so the main loop can poll both that queue and the pending tool futures without blocking on `getline`.

  **Inputs:**
  The user enters `@carlos <msg>` or `@advisor <msg>` commands via the command line. Each agent maintains its own conversation history and is independently addressable; returning to a previously-used agent picks up its full prior history.

  **Expected Output:**

  Token output is prefixed with `@carlos:` or `@advisor:` so it is clear which agent is speaking.

  Default:
  ```
  You: @carlos who shoved this hand?
  @carlos: I did, Alice. I went all-in with 10♣ J♣.

  You: @advisor what's my hand?
  @advisor: Your best hand is three Kings (K♦, K♥, K♣). The 9♣ and board cards don't form a straight or flush. You have a strong set, but be cautious of potential straight draws from opponents. Keep betting aggressively to protect your hand.

  You: @carlos any regrets?
  @carlos: No regrets, Alice. I played my hand tight and made the right call. You're the one who should be questioning your move. You got outplayed, and you know it.

  You: /exit
  ```

  With `-d` (tool execution and async dispatch logs):
  ```
  You: @carlos who shoved this hand?

  [TOOLS] @carlos dispatching 1 tool call(s) async
    - check_status (id: call_0)
  [waiting for @carlos tools...]

  You:
  [TOOLS] @carlos tools completed (1 results)

  @carlos: I did, Alice. I went all-in with 10♣ J♣.
  ```

  With `@advisor /think-verbose` (reasoning tokens streamed before the advisor's responses):
  ```
  You: @advisor what's my hand?

  @advisor: Think: {reasoning}
  ---
  Your best hand is three Kings (K♦, K♥, K♣)...

  You: /exit
  ```

  > **Note:** `-d` and `/think-verbose` are independent and can be used together.
