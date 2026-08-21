# Skeleton: agentk（20 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 7KB | 4 | ~2 | 2 |
| 2 | Core Architecture | L237 | 9KB | 6 | ~2 | 4 |
| 3 | Kernel Components | L520 | 8KB | 3 | ~1 | 3 |
| 4 | LangGraph Implementation | L744 | 9KB | 5 | ~4 | 4 |
| 5 | Agents | L1006 | 10KB | 6 | ~2 | 3 |
| 6 | Hermes: Orchestrator | L1290 | 7KB | 3 | ~2 | 2 |
| 7 | AgentSmith: Agent Creator | L1493 | 9KB | 6 | ~5 | 2 |
| 8 | ToolMaker: Tool Creator | L1731 | 10KB | 4 | ~2 | 2 |
| 9 | WebResearcher: Knowledge Gatherer | L1997 | 9KB | 4 | ~1 | 4 |
| 10 | SoftwareEngineer: Code Management | L2243 | 7KB | 4 | ~3 | 2 |
| 11 | Tools | L2456 | 7KB | 5 | ~2 | 2 |
| 12 | File System Tools | L2691 | 5KB | 2 | ~1 | 4 |
| 13 | Web Interaction Tools | L2854 | 7KB | 5 | ~1 | 3 |
| 14 | Tool Creation Process | L3074 | 9KB | 6 | ~4 | 1 |
| 15 | Configuration | L3371 | 3KB | 2 | ~2 | 2 |
| 16 | Language Model Setup | L3467 | 7KB | 3 | ~6 | 2 |
| 17 | Deployment | L3694 | 6KB | 3 | ~9 | 4 |
| 18 | Developer Guide | L3899 | 11KB | 8 | ~0 | 3 |
| 19 | Creating New Agents | L4263 | 11KB | 4 | ~7 | 3 |
| 20 | Creating New Tools | L4636 | 8KB | 5 | ~10 | 3 |


## · Overview  (L6)
  源文件: README.md, agents/hermes.py
  Introduction to AgentK
  System Architecture
    · Core Kernel Agents
  Workflow and Interaction Patterns
  Implementation Details
    · ReAct Pattern with LangGraph
    · Agent Implementation Example
  Self-Evolution Mechanism
  Deployment
  Related Pages

## · Core Architecture  (L237)
  源文件: README.md, agents/agent_smith.py, agents/hermes.py, agents/tool_maker.py
  Architectural Overview
  Core Design Principles
  Kernel Components
  Agent Relationships and Workflows
  Self-Evolution Mechanisms
  LangGraph Implementation Pattern
  Code Structure

## · Kernel Components  (L520)
  源文件: README.md, agent_kernel.py, agents/hermes.py
  Purpose and Scope
  What is the Kernel?
  Core Kernel Agents
    · Hermes: The Orchestrator
    · AgentSmith: The Agent Creator
    · ToolMaker: The Tool Developer
    · WebResearcher: The Knowledge Gatherer
  Kernel Architecture
    · Design Principles
  Technical Implementation
    · Agent Communication and Workflow
    · Kernel Initialization
    · Available Tools in the Kernel
  Kernel Boundaries and Evolution

## · LangGraph Implementation  (L744)
  源文件: agents/agent_smith.py, agents/hermes.py, agents/tool_maker.py, agents/web_researcher.py
  Core LangGraph Components in AgentK
  Standard ReAct Workflow Pattern
  Implementation Details
    · 1. State Management
    · 2. Node Implementation
    · 3. Decision Logic
  Code-to-Execution Mapping
  Variations in Agent Workflows
    · Hermes: Special Case
  Initializing and Invoking Agents
  Common ReAct Agent Structure

## · Agents  (L1006)
  源文件: README.md, agents/hermes.py, utils.py
  What are Agents in AgentK?
  Agent Architecture
  Agent Registry and Loading
  Core Kernel Agents
  Agent Interaction Patterns
  The Agent Implementation Pattern
  Conclusion

## · Hermes: Orchestrator  (L1290)
  源文件: README.md, agents/hermes.py
  Purpose and Scope
  Overview
  Core Responsibilities
  Implementation Architecture
    · Node Functions
  Tools
  Interaction Pattern
  System Prompt Analysis
  Code Implementation
  Technical Considerations
    · Checkpointing
    · Language Model Configuration
    · Console Interaction
  Summary

## · AgentSmith: Agent Creator  (L1493)
  源文件: README.md, agents/agent_smith.py
  Purpose and Scope
  Role in AgentK Ecosystem
  Implementation Details
  Agent Creation Process
  Code Structure Guidelines
  Tool Integration
  Example Agent Creation
  Integration with the Agent Registry
  Common Challenges and Solutions
  Usage

## · ToolMaker: Tool Creator  (L1731)
  源文件: README.md, agents/tool_maker.py
  Purpose and Scope
  Overview
  Implementation Details
    · Core Components
  Tool Creation Process
    · Steps in Detail
  Tool Structure and Requirements
    · Tool File Requirements
    · Test File Requirements
  Dependency Management
    · Python Dependencies
    · System Dependencies
  Integration with Other Agents
  Example Tool Creation
    · Simple Tool Example
  Conclusion

## · WebResearcher: Knowledge Gatherer  (L1997)
  源文件: README.md, agents/web_researcher.py, tests/tools/test_fetch_web_page_raw_html.py, tools/fetch_web_page_raw_html.py
  Purpose and Scope
  Architecture Overview
  Implementation Details
  Workflow Process
  Web Tools and Capabilities
  System Integration
  Implementation Code Structure
  Testing and Reliability
  Usage Example
  Limitations and Future Improvements

## · SoftwareEngineer: Code Management  (L2243)
  源文件: agents/software_engineer.py, tests/agents/test_software_engineer.py
  Overview
  Capabilities
  Architecture
  Tools Integration
  Workflow Implementation
  Usage Examples
  Integration with Agent System
  System Prompt

## · Tools  (L2456)
  源文件: agents/tool_maker.py, utils.py
  Tool System Architecture
  Tool Loading Process
  Tool Categories
  Tool Implementation Structure
  Tool Creation Process
  How Agents Use Tools
  Tool Management Utilities

## · File System Tools  (L2691)
  源文件: tests/tools/test_delete_file.py, tests/tools/test_read_file.py, tools/delete_file.py, tools/read_file.py
  Overview
  Tool Implementation
    · read_file
    · delete_file
  Tool Usage Pattern
  Tool Invocation
  Error Handling
  Testing

## · Web Interaction Tools  (L2854)
  源文件: agents/web_researcher.py, tests/tools/test_fetch_web_page_raw_html.py, tools/fetch_web_page_raw_html.py
  1. Overview
  2. Available Web Tools
    · 2.1 fetch_web_page_raw_html
    · 2.2 fetch_web_page_content
    · 2.3 duck_duck_go_web_search
  3. Usage in Agents
    · 3.1 Tool Registration and Usage
  4. Implementation Requirements
  5. Security Considerations
  6. Extension Points

## · Tool Creation Process  (L3074)
  源文件: agents/tool_maker.py
  1. ToolMaker Agent Overview
  2. Tool Structure and Requirements
  3. Tool Creation Workflow
  4. ReAct Implementation in ToolMaker
  5. Tool Implementation Details
    · 5.1 Tool Function Structure
    · 5.2 Dependency Management
    · 5.3 Human Input Handling
  6. Tool Testing Process
  7. Tool Integration
  8. Example Tool Creation
    · 8.1 Simple Tool Example
    · 8.2 Parameterless Tool Example

## · Configuration  (L3371)
  源文件: .env.example, config.py
  Overview
  Environment Configuration
  Language Model Configuration
  Configuration Flow Diagram
  Model Provider Selection Process

## · Language Model Setup  (L3467)
  源文件: .env.example, config.py
  Supported Language Model Providers
  Provider Configuration Process
  Environment Variables
  Provider-Specific Configuration
    · OpenAI Configuration
    · Anthropic Configuration
    · Ollama Configuration
  Integration with AgentK Architecture
  Optional LangSmith Integration
  Common Issues and Solutions
  Setting Up a New Environment

## · Deployment  (L3694)
  源文件: Dockerfile, agentk, apt-packages-list.txt, requirements.txt
  Deployment Architecture
  Prerequisites
  Environment Configuration
  Container Build and Setup
    · System Dependencies
    · Python Dependencies
  Running AgentK
  Execution Flow
  Deployment Options
    · Local Development
    · Server Deployment
  Resource Requirements
  Troubleshooting
  Advanced Configuration

## · Developer Guide  (L3899)
  源文件: .gitignore, README.md, utils.py
  1. Development Environment Setup
    · Prerequisites
    · Setting Up Locally
  2. Understanding the Core Architecture
    · Module Loading System
    · Agent System Architecture
    · Tool System Architecture
  3. Creating New Agents
    · Agent Structure Template
    · Key Considerations
  4. Creating New Tools
    · Tool Structure Template
    · Key Considerations
  5. Testing and Debugging
    · Testing Agents and Tools
    · Debugging Techniques
  6. Best Practices
    · Code Organization
    · Agent Design Principles
    · Tool Design Principles
  7. Extending the System
    · Key Extension Areas
  Conclusion

## · Creating New Agents  (L4263)
  源文件: agents/agent_smith.py, agents/software_engineer.py, tests/agents/test_software_engineer.py
  1. Agent Creation Methods
  2. Agent Architecture
  3. Step-by-Step Agent Creation
    · 3.1 Using AgentSmith (Recommended)
    · 3.2 Manual Agent Creation
  4. Agent Implementation Details
    · 4.1 Component Breakdown
    · 4.2 Required Code Structure
  5. Coding the Agent Components
    · 5.1 Required Imports
    · 5.2 System Prompt
    · 5.3 Tool Imports and List
    · 5.4 Reasoning and Tool Call Functions
    · 5.5 Workflow Graph Setup
    · 5.6 Agent Function Definition
  6. Testing Your Agent
  7. Best Practices
    · 7.1 Agent Design Principles
    · 7.2 Naming and Documentation
    · 7.3 Integration with the System
  8. Common Issues and Solutions

## · Creating New Tools  (L4636)
  源文件: agents/tool_maker.py, tests/tools/test_fetch_web_page_raw_html.py, tools/fetch_web_page_raw_html.py
  Purpose and Scope
  What Are Tools in AgentK?
  Tool Structure and Requirements
    · Basic Tool Structure
    · Key Requirements
  Creating a New Tool: Step-by-Step Guide
    · 1. Planning Your Tool
    · 2. Creating the Tool File
    · 3. Handling Dependencies
  Writing Tests for Tools
    · Test File Structure
  Tool Creation with ToolMaker Agent
  Tool Categories and Examples
    · File System Tools
    · Web Interaction Tools
    · Agent Interaction Tools
  Example: Web Page HTML Fetcher
  Best Practices for Tool Creation
  The Tool Registry System
  Troubleshooting Tool Creation