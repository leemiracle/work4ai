# 🎯 Tutorial 2: Model-Agnostic Agent

Learn how to create agents that work with **different AI models** using OpenRouter. This example shows how ADK can use OpenAI and Anthropic models through separate agent implementations.

## 🎯 What You'll Learn

- **OpenRouter Integration**: Use one API key for multiple model providers
- **Separate Agent Implementations**: Compare different models side-by-side
- **Tool Integration**: Add simple tools to your agents
- **Root Agent Pattern**: Proper ADK agent naming convention

## 🧠 Core Concept: One API, Many Models

[OpenRouter](https://openrouter.ai) provides a unified API to access multiple AI models:
- ✅ **Single API Key**: Access OpenAI and Anthropic with one key
- ✅ **Easy Comparison**: Run different agents to compare responses
- ✅ **Cost Effective**: Pay-per-use pricing
- ✅ **No Vendor Lock-in**: Switch providers anytime

## 📁 Project Structure

```
2_model_agnostic_agent/
├── README.md                       # This overview
├── requirements.txt                # Shared dependencies
├── 2_1_openai_adk_agent/           # OpenAI GPT-4 agent
│   └── agent.py                    # Agent implementation
└── 2_2_anthropic_adk_agent/        # Anthropic Claude agent
    └── agent.py                    # Agent implementation
```

## 🔧 Available Agents

### **OpenAI Agent** (`2_1_openai_adk_agent/`)
- **Model**: GPT-4 via OpenRouter
- **Agent Name**: `root_agent` (required by ADK)
- **Features**: Fun fact tool with OpenAI personality

### **Anthropic Agent** (`2_2_anthropic_adk_agent/`)
- **Model**: Claude 4 Sonnet via OpenRouter
- **Agent Name**: `root_agent` (required by ADK)
- **Features**: Fun fact tool with Claude personality

## 🛠️ Setup & Usage

### 1. **Get OpenRouter API Key**
- Visit: [https://openrouter.ai/keys](https://openrouter.ai/keys)
- Sign up and get your API key

### 2. **Set Environment Variable**
Create a `.env` file in each agent folder:

**In `2_1_openai_adk_agent/.env`:**
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**In `2_2_anthropic_adk_agent/.env`:**
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 3. **Install Dependencies**
```bash
# From the 2_model_agnostic_agent directory
pip install -r requirements.txt
```

### 4. **Test OpenAI Agent**
```bash
adk web
```
Then select the 2_1_openai_adk_agent in the ADK web UI
- Try asking: "Tell me a fun fact!"
- Notice the OpenAI GPT-4 response style

### 5. **Test Anthropic Agent**
```bash
adk web
```
Then select the 2_2_anthropic_adk_agent in the ADK web UI
- Try asking: "Tell me a fun fact!"
- Compare with the GPT-4 response style

## 💡 Key Code Pattern

Each agent follows the same pattern:

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import os

# Create model via OpenRouter
model = LiteLlm(
    model="openrouter/openai/gpt-4",  # or claude model
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Create root_agent (required name for ADK)
root_agent = Agent(
    name="agent_name",
    model=model,
    instruction="Your instructions here...",
    tools=[your_tool_function],
)
```

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ How to use OpenRouter with ADK
- ✅ How to create separate agents for different models
- ✅ How to compare responses from different AI providers
- ✅ How to properly structure ADK agents with `root_agent`

## 🔄 Comparing Models

1. **Run the OpenAI agent** and ask questions
2. **Run the Anthropic agent** with the same questions
3. **Notice differences** in response style and approach
4. **Experiment** with different types of prompts

## 💰 Cost Information

- OpenRouter charges per token usage
- GPT-4o: More expensive but very capable
- Claude 4 Sonnet: Balanced cost and performance
- You can set spending limits in your OpenRouter dashboard
- Free tier available for testing

## 🚨 Important Notes

- **Root Agent**: Each agent must be named `root_agent` for ADK to recognize it
- **Environment Variables**: Each folder needs its own `.env` file
- **API Key**: The same OpenRouter key works for both agents
- **Comparison**: Run agents separately to compare model behaviors