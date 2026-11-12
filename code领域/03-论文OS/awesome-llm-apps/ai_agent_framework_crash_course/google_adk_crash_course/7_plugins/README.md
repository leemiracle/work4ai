# 🔌 Tutorial 7: Plugins

## 🎯 What You'll Learn
- **Plugin Fundamentals**: Understanding what plugins are and how they work
- **Global Callback Management**: Using plugins for cross-cutting concerns
- **Practical Plugin Examples**: Logging, monitoring, and request modification

## 💡 Core Concept: Plugins

Plugins in Google ADK are custom code modules that can be executed at various stages of an agent workflow lifecycle using callback hooks. Unlike regular callbacks that are configured on individual agents or tools, plugins are registered once on the `Runner` and apply globally to every agent, tool, and LLM call managed by that runner.

### **Plugin vs Callback Comparison**
```
┌─────────────────┐    ┌─────────────────┐
│   Regular       │    │     Plugin      │
│   Callbacks     │    │   Callbacks     │
├─────────────────┤    ├─────────────────┤
│ • Per agent     │    │ • Global scope  │
│ • Per tool      │    │ • Runner level  │
│ • Specific task │    │ • Cross-cutting │
│ • Local effect  │    │ • Reusable      │
└─────────────────┘    └─────────────────┘
```

### **Plugin Lifecycle Hooks**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Message   │───▶│   Runner Start  │───▶│  Agent Execute  │
│   Callback      │    │   Callback      │    │   Callback      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Model Callback │    │  Tool Callback  │    │  Event Callback │
│   (before/after)│    │   (before/after)│    │   (modify event)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Error Handling │    │  Runner End     │    │  Cleanup Tasks  │
│   Callback      │    │   Callback      │    │   & Reporting   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Why Use Plugins?**
- **Cross-cutting Concerns**: Implement functionality that applies across your entire application
- **Reusability**: Package related callback functions together for reuse
- **Global Monitoring**: Track all agent, tool, and model interactions
- **Policy Enforcement**: Implement security guardrails and access controls
- **Logging & Metrics**: Centralized logging and performance monitoring
- **Request/Response Modification**: Dynamically modify inputs and outputs

## 📖 Tutorial Overview

This tutorial demonstrates how to create and use plugins in Google ADK through a practical example that combines multiple use cases:

### **Demo Plugin Features**
1. **Request Logging**: Log all user messages with timestamps
2. **Request Modification**: Add timestamp context to user messages
3. **Agent Tracking**: Count and monitor agent executions
4. **Tool Monitoring**: Track tool usage and handle errors
5. **Final Reporting**: Generate summary of plugin activity

## 📁 Project Structure

```
7_plugins/
├── README.md                           # This file - concept explanation
├── agent.py                            # Agent implementation with plugin
├── app.py                              # Streamlit interface
├── requirements.txt                    # Dependencies
└── plugin_example.py                   # Standalone plugin demonstration
```

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:

- ✅ **Plugin Architecture**: How plugins extend the BasePlugin class
- ✅ **Global Scope**: How plugins apply across all agents and tools
- ✅ **Callback Hooks**: Available plugin callback methods and their timing
- ✅ **Practical Applications**: Real-world use cases for plugins
- ✅ **Error Handling**: How to implement graceful error recovery
- ✅ **Simple Implementation**: Easy-to-understand plugin structure

## 🚀 Getting Started

### **Prerequisites**
- Python 3.11+
- Google AI Studio API key
- Basic understanding of Google ADK (Tutorials 1-6)

### **Setup**
1. **Get API Key**: Visit [Google AI Studio](https://aistudio.google.com)
2. **Create .env file**: Create a file named `.env` in this directory with:
   ```
   GOOGLE_API_KEY=your_google_ai_studio_api_key_here
   ```
3. **Install dependencies**: `pip install -r requirements.txt`

**Important**: 
- Make sure your `.env` file is in the same directory as the tutorial files
- Replace `your_google_ai_studio_api_key_here` with your actual API key
- The `.env` file should not be committed to version control

### **Run Tutorial**
```bash
cd 7_plugins
streamlit run app.py
```

## 🔧 Key Concepts

### **Plugin Class Structure**
```python
from google.adk.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="my_plugin")
        # Initialize plugin state
    
    async def before_agent_callback(self, *, agent, callback_context):
        # Called before each agent execution
        pass
    
    async def after_model_callback(self, *, callback_context, llm_response):
        # Called after each model call
        pass
```

### **Plugin Registration**
```python
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(
    agent=my_agent,
    app_name="my_app",
    plugins=[MyPlugin()]  # Register plugins here
)
```

### **Available Callback Hooks**
- `on_user_message_callback`: Modify user input
- `before_run_callback`: Setup before execution
- `before_agent_callback` / `after_agent_callback`: Agent lifecycle
- `before_model_callback` / `after_model_callback`: Model interactions
- `before_tool_callback` / `after_tool_callback`: Tool execution
- `on_model_error_callback` / `on_tool_error_callback`: Error handling
- `on_event_callback`: Modify events before streaming
- `after_run_callback`: Cleanup after execution

## 🎯 Use Cases

### **Common Plugin Applications**
1. **Logging & Tracing**: Detailed logs for debugging and analysis
2. **Policy Enforcement**: Security guardrails and access controls
3. **Monitoring & Metrics**: Performance tracking and analytics
4. **Response Caching**: Cache expensive operations
5. **Request/Response Modification**: Add context or standardize outputs
6. **Error Recovery**: Graceful handling of failures
7. **Usage Analytics**: Track patterns and usage statistics

## 🚨 Important Notes

- **Plugin Precedence**: Plugin callbacks run **before** agent-level callbacks
- **Global Scope**: Plugins affect **all** agents, tools, and models in the runner
- **Web Interface**: Plugins are **not supported** by the ADK web interface
- **Error Handling**: Plugin error callbacks can suppress exceptions and provide fallbacks

## 📚 Next Steps

After completing this tutorial, you can:
- Create custom plugins for your specific use cases
- Implement monitoring and analytics plugins
- Build security and policy enforcement plugins
- Explore advanced plugin patterns and combinations

## 🔧 Troubleshooting

### **Common Issues**

**"Missing key inputs argument" Error**
- Ensure you have created a `.env` file with your Google AI Studio API key
- Verify the API key is valid and has the necessary permissions
- Check that the `.env` file is in the same directory as the tutorial files

**Import Errors**
- Make sure you have installed all dependencies: `pip install -r requirements.txt`
- Verify you're using Python 3.11 or higher

**Plugin Not Working**
- Remember that plugins are not supported by the ADK web interface
- Ensure you're running the agent through the Streamlit app or Python script

## 🔗 Additional Resources

- [Google ADK Plugins Documentation](https://google.github.io/adk-docs/plugins)
- [Plugin Callback Hooks](https://google.github.io/adk-docs/plugins/#plugin-callback-hooks)
- [BasePlugin API Reference](https://google.github.io/adk-docs/api/python/google.adk.plugins.base_plugin.BasePlugin)
