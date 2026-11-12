# Explorer AI: Curiosity-Driven Agent Platform

Explorer AI is an interactive web-based platform that demonstrates advanced AI agent capabilities using NVIDIA NIMs and ReAct (Reasoning + Acting) architecture. The project showcases curiosity-driven agents that can engage in dynamic conversations, perform web searches, and maintain context across sessions - all powered by powerful language models running on NIMs.

## 🌟 Features

- **Multi-Model Support**: Choose from different NVIDIA NIMs models (Llama 3.1 405B, Llama 3.1 70B, Llama 3.2 3B, DeepSeek V3.1, Qwen3 Next 80B)
- **Web Search Integration**: Real-time web search capabilities using Tavily API
- **Persistent Memory**: Conversation history maintained across sessions using LangGraph checkpointing
- **Interactive Web Interface**: Modern web UI built with FastHTML and Pico CSS
- **ReAct Architecture**: Reasoning and Acting framework for intelligent decision-making
- **Real-time Communication**: WebSocket-based live updates
- **Educational Playbook**: Jupyter notebook demonstrating core concepts step-by-step

## 🏗️ Architecture
<img width="841" height="405" alt="explorer-ai-architecture" src="https://github.com/user-attachments/assets/ad9fdeac-4936-4e06-9ce0-6cd266190031" />

### Core Components

| Component | Purpose |
|-----------|---------|
| **FastHTML** | Modern Python web framework for reactive UI |
| **LangGraph** | State management and agent orchestration |
| **NVIDIA NIMs** | Large language model inference via API |
| **Tavily Search** | Real-time web search tool integration |
| **SQLite** | Persistent storage for chat history and checkpoints |
| **ReAct Agent** | Reasoning and acting framework for intelligent responses |

### Technical Stack

- **Frontend**: FastHTML with Pico CSS for responsive design
- **Backend**: Python with FastHTML and WebSocket support
- **AI Models**: NVIDIA NIMs (Llama 3.1/3.2, DeepSeek V3.1, Qwen3 Next 80B)
- **Agent Framework**: LangGraph with ReAct prebuilt agents
- **Search**: Tavily API for real-time web information
- **Storage**: SQLite for conversation persistence

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ (recommended: Python 3.11.7)
- NVIDIA NIMs API key
- Tavily Search API key
- LangSmith API key (optional, for monitoring)

### Installation

1. **Clone and navigate to the project**:
```bash
cd projects/explorer-ai
```

2. **Set up virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .sample-env .env
# Edit .env file with your API keys
```

5. **Run the application**:
```bash
python curiosity.py
```

6. **Access the interface**:
   - Open your browser to `http://localhost:5001`
   - Start asking questions and exploring!
<img width="1415" height="792" alt="explorer-ai-application" src="https://github.com/user-attachments/assets/4be4cbac-6a63-4368-bd55-687daefdd447" />

## 🔧 Configuration

### Required API Keys

Edit the `.env` file with your API credentials:

```env
NVIDIA_API_KEY=your_nvidia_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here  # Optional
LANGCHAIN_PROJECT=your_project_name_here       # Optional
```

### Available Models

- **Llama 3.1 405B**: Most capable model for complex reasoning
- **Llama 3.1 70B**: Balanced performance and capability
- **Llama 3.2 3B**: Lightweight model for faster responses
- **DeepSeek V3.1**: Advanced reasoning capabilities
- **Qwen3 Next 80B**: High-performance multilingual model

## 📚 Educational Playbook

The `playbook/` directory contains a comprehensive Jupyter notebook that demonstrates:

### Core Concepts Covered

1. **Memory-Augmented Chatbots**: Building persistent conversation memory
2. **Web Search Integration**: Adding real-time search capabilities
3. **ReAct Agent Architecture**: Combining reasoning and acting
4. **LangGraph Integration**: State management and orchestration
5. **NVIDIA NIMs Integration**: Leveraging powerful language models

### Running the Playbook

1. **Navigate to the playbook directory**:
```bash
cd playbook/
pip install -r requirements.txt
```

2. **Edit the notebook** and add your own API keys:
   - Replace `<INSERT NVIDIA API KEY>` with your NVIDIA API key
   - Replace `<INSERT LANGSMITH API KEY>` with your LangSmith API key 
   - Replace `<INSERT TAVILY API KEY>` with your Tavily API key

3. **Launch Jupyter**:
```bash
jupyter notebook edited-reAct-memory-websearch-playbook.ipynb
```

## 🎯 Use Cases

### Research & Learning
- Interactive exploration of topics with real-time web search
- Educational conversations with AI that remembers context
- Research assistance with source attribution

### Development & Prototyping
- Testing different NVIDIA NIMs models
- Experimenting with ReAct agent architectures
- Learning LangGraph and agent-based AI systems

### Business Applications
- Customer support chatbots with search capabilities
- Research assistants for knowledge workers
- Interactive FAQ systems with dynamic information retrieval

## 💡 Key Innovations

### Curiosity-Driven Design
- Agents proactively explore topics and ask follow-up questions
- Dynamic conversation flow based on user interests
- Integration of multiple information sources

### Modular Architecture
- Easy model swapping between different NVIDIA NIMs
- Pluggable tool integration (currently web search)
- Extensible framework for adding new capabilities

### Real-time Intelligence
- WebSocket-based live updates
- Streaming responses for better user experience
- Real-time web search integration

## 🔍 Project Structure

```
explorer-ai/
├── curiosity.py              # Main application server
├── chat_agent.py            # Agent creation and management
├── requirements.txt         # Python dependencies
├── .sample-env             # Environment variables template
├── data/                   # SQLite database storage
│   └── curiosity.db       # Conversation and checkpoint storage
└── playbook/              # Educational materials
    ├── edited-reAct-memory-websearch-playbook.ipynb
    ├── requirements.txt
    └── img/               # Notebook images and assets
```

## 🎨 User Interface Features

- **Clean, Modern Design**: Pico CSS framework for responsive UI
- **Dark/Light Mode**: Automatic theme detection
- **Multi-Chat Support**: Manage multiple conversation threads
- **Model Selection**: Switch between different NVIDIA models
- **Source Attribution**: View web search sources for responses
- **Chat History**: Persistent conversation storage
- **Real-time Updates**: Live response streaming

## 🚀 Advanced Usage

### Custom Model Integration
The agent system is designed to be extensible. You can add new models by modifying the `chat_agent.py` file and adding model configurations.

### Tool Extensions
The ReAct framework supports additional tools beyond web search. Consider integrating:
- Code execution environments
- Database query tools
- File system operations
- API integrations

### Deployment Options
- **Local Development**: Run with `python curiosity.py`
- **Container Deployment**: Docker containerization supported
- **Cloud Deployment**: Compatible with cloud platforms

## 🤝 Contributing

This project demonstrates advanced AI agent architectures and is designed for:
- Educational exploration of LangGraph and NVIDIA NIMs
- Prototyping curiosity-driven AI systems  
- Research into agent-based conversational AI

Project By:
Jewel Aw (NVIDIA Student Ambassador), Darren Tan (NVIDIA), Aik Beng Ng (NVIDIA), Simon See (NVIDIA).

An NVAITC APS project (NVIDIA).

## Updates
- 26/8/2025 by Jewel Aw: Updating README with pictures
- 5/11/2025 by Jewel Aw: Debugged answer rendering problem, added features: support for markdown to render bold/heading, more models including Qwen, better error handling

## 📄 License

This project is licensed under the MIT License - see the repository's [LICENSE](../../LICENSE) file for details.
