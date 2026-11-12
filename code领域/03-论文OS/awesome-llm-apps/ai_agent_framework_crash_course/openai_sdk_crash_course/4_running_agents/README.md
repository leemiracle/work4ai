# 🚀 Tutorial 4: Running Agents

Master the complete OpenAI Agents SDK execution system! This tutorial covers all aspects of running agents including execution methods, streaming, the agent loop, exception handling, and advanced configuration based on the [official running agents documentation](https://openai.github.io/openai-agents-python/running_agents).

## 🎯 What You'll Learn

- **Three Execution Methods**: `Runner.run()`, `Runner.run_sync()`, `Runner.run_streamed()`
- **The Agent Loop**: Understanding LLM calls, tool execution, and handoffs
- **Streaming Events**: Real-time response handling with detailed event processing
- **Exception Handling**: Managing all SDK exceptions properly
- **Advanced Run Configuration**: Guardrails, tracing, and workflow control

## 🧠 Core Concept: The Agent Loop

When you call any Runner method, the SDK executes a sophisticated loop that handles the complete agent workflow:

```
┌─────────────────────────────────────────────────────────────┐
│                    THE AGENT LOOP                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  START: Runner.run(agent, input)                            │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐    1. CALL LLM                             │
│  │     LLM     │    ◦ Current agent + input                 │
│  │   CALL      │    ◦ Generate response                     │
│  └─────────────┘                                            │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐    2. PROCESS OUTPUT                       │
│  │   OUTPUT    │    ◦ Final output? → END                   │
│  │  ANALYSIS   │    ◦ Tool calls? → Execute tools           │
│  └─────────────┘    ◦ Handoff? → Switch agent               │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐    3. CONTINUE LOOP                        │
│  │   REPEAT    │    ◦ Append results to input               │ 
│  │   LOOP      │    ◦ Check max_turns limit                 │
│  └─────────────┘    ◦ Loop until final output               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Tutorial Overview

This tutorial demonstrates **five key running patterns**:

### **1. Execution Methods** (`4_1_execution_methods/`)
- Sync, async, and streaming execution comparison
- Performance and use case analysis
- Basic agent loop understanding

### **2. Conversation Management** (`4_2_conversation_management/`)
- Manual conversation threading with `to_input_list()`
- Automatic conversation management with Sessions
- Thread ID and group management

### **3. Run Configuration** (`4_3_run_configuration/`)
- Model overrides and settings
- Tracing configuration and metadata
- Workflow naming and organization

### **4. Streaming Events** (`4_4_streaming_events/`)
- Detailed streaming event handling
- `RunResultStreaming` object usage
- Real-time response processing patterns

### **5. Exception Handling** (`4_5_exception_handling/`)
- All SDK exceptions: `MaxTurnsExceeded`, `ModelBehaviorError`, etc.
- Proper error handling patterns
- Recovery and retry strategies

## 📁 Project Structure

```
4_running_agents/
├── README.md                           # This file - comprehensive guide
├── requirements.txt                    # Dependencies
├── 4_1_execution_methods/
│   ├── __init__.py
│   └── agent.py                       # Three execution methods (45 lines)
├── 4_2_conversation_management/
│   ├── __init__.py  
│   └── agent.py                       # Manual vs automatic threading (40 lines)
├── 4_3_run_configuration/
│   ├── __init__.py
│   └── agent.py                       # RunConfig examples (55 lines)
├── 4_4_streaming_events/
│   ├── __init__.py
│   └── agent.py                       # Detailed streaming handling (50 lines)
├── 4_5_exception_handling/
│   ├── __init__.py
│   └── agent.py                       # All exception types (60 lines)
├── agent_runner.py                    # Streamlit demo interface (recommended)
└── env.example                        # Environment variables
```

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ The complete agent execution loop and when each step occurs
- ✅ How to choose between sync, async, and streaming execution
- ✅ Detailed streaming event processing for real-time applications
- ✅ Proper exception handling for production-ready applications
- ✅ Advanced run configuration for complex workflows

## 🚀 Getting Started

1. **Install OpenAI Agents SDK**:
   ```bash
   pip install openai-agents
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Test execution methods**:
   ```bash
   python -m 4_1_execution_methods.agent
   ```

4. **Try conversation management**:
   ```bash
   python -m 4_2_conversation_management.agent
   ```

5. **Explore run configuration**:
   ```bash
   python -m 4_3_run_configuration.agent
   ```

6. **Test streaming events**:
   ```bash
   python -m 4_4_streaming_events.agent
   ```

7. **Practice exception handling**:
   ```bash
   python -m 4_5_exception_handling.agent
   ```

## 🔧 Key Running Concepts

### 1. **The Agent Loop Process**
- **LLM Call**: Agent processes input and generates response
- **Output Analysis**: Check for final output, tool calls, or handoffs
- **Tool Execution**: Run any tool calls and append results
- **Handoff Processing**: Switch to new agent if handoff occurs
- **Loop Continuation**: Repeat until final output or max_turns reached

### 2. **Three Execution Methods**
```python
# 1. Async (non-blocking, returns RunResult)
result = await Runner.run(agent, "message")

# 2. Sync (blocking, wraps async under hood)  
result = Runner.run_sync(agent, "message")

# 3. Streaming (async, returns RunResultStreaming)
async for event in Runner.run_streamed(agent, "message"):
    # Process events in real-time
    pass
```

### 3. **Streaming Event Types**
Based on the documentation, streaming provides real-time events as the LLM generates responses, including partial text, tool calls, and completion events.

### 4. **Exception Hierarchy**
- **AgentsException**: Base exception class
- **MaxTurnsExceeded**: Too many loop iterations
- **ModelBehaviorError**: LLM output issues (malformed JSON, etc.)
- **UserError**: SDK usage errors
- **InputGuardrailTripwireTriggered**: Input validation failures
- **OutputGuardrailTripwireTriggered**: Output validation failures

## 🧪 Sample Use Cases

### Execution Methods
- **Sync**: Simple scripts, batch processing, quick responses
- **Async**: Web applications, concurrent users, non-blocking operations  
- **Streaming**: Long content generation, real-time chat, progress updates

### Conversation Management
- **Manual**: Custom conversation logic, special threading requirements
- **Sessions**: Standard chat applications, automatic history management

### Exception Handling
- **Production Apps**: Graceful error recovery, user-friendly messages
- **Development**: Debugging agent behavior, understanding failures

## 💡 Running Agents Best Practices

1. **Choose Right Method**: Sync for scripts, async for apps, streaming for long responses
2. **Handle Exceptions**: Always wrap Runner calls in proper exception handling
3. **Configure Appropriately**: Use RunConfig for production settings
4. **Monitor Performance**: Track execution time and resource usage
5. **Manage Conversations**: Choose manual vs Sessions based on requirements

## 🔗 Next Steps

After completing this tutorial, you'll be ready for:
- **[Tutorial 5: Context Management](../5_context_management/README.md)** - Advanced state management
- **[Tutorial 6: Guardrails & Validation](../6_guardrails_validation/README.md)** - Input/output safety
- **[Tutorial 7: Sessions](../7_sessions/README.md)** - Memory and conversation management

## 🚨 Troubleshooting

- **Async Issues**: Always use `await` with `Runner.run()` and `Runner.run_streamed()`
- **Streaming Problems**: Handle partial events and connection interruptions
- **Exception Handling**: Catch specific exception types for better error recovery
- **Performance**: Monitor max_turns settings to prevent infinite loops
- **Configuration**: Verify RunConfig settings match your use case requirements

## 💡 Pro Tips

- **Start Simple**: Begin with `run_sync`, move to `run` when you need concurrency
- **Use Streaming Wisely**: Reserve for responses longer than 30 seconds
- **Exception Strategy**: Plan for each exception type in production code
- **Configuration Consistency**: Use RunConfig for repeatable execution patterns
- **Monitor the Loop**: Use tracing to understand complex agent interactions