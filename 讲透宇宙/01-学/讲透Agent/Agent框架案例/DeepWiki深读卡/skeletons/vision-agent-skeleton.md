# Skeleton: vision-agent（31 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 10KB | 6 | ~0 | 3 |
| 2 | System Architecture | L355 | 14KB | 8 | ~0 | 6 |
| 3 | Installation and Dependencies | L814 | 9KB | 4 | ~8 | 5 |
| 4 | Agent System | L1129 | 14KB | 7 | ~3 | 6 |
| 5 | VisionAgentV2 | L1554 | 10KB | 5 | ~2 | 5 |
| 6 | VisionAgentCoderV2 | L1844 | 14KB | 4 | ~5 | 5 |
| 7 | VisionAgentPlannerV2 | L2244 | 11KB | 4 | ~1 | 4 |
| 8 | LLM Integration | L2594 | 10KB | 5 | ~4 | 4 |
| 9 | Vision Tools | L2895 | 20KB | 6 | ~18 | 2 |
| 10 | Tools Registry | L3470 | 10KB | 4 | ~0 | 2 |
| 11 | Object Detection Tools | L3766 | 12KB | 4 | ~6 | 4 |
| 12 | Video Processing Tools | L4110 | 10KB | 4 | ~6 | 6 |
| 13 | Document Analysis Tools | L4414 | 13KB | 5 | ~0 | 3 |
| 14 | Meta Tools | L4784 | 10KB | 8 | ~2 | 3 |
| 15 | Code Execution System | L5126 | 16KB | 6 | ~0 | 6 |
| 16 | Code Interpreter | L5625 | 9KB | 4 | ~0 | 3 |
| 17 | Execution Workflow | L5934 | 14KB | 5 | ~4 | 6 |
| 18 | Utility Systems | L6319 | 13KB | 4 | ~21 | 4 |
| 19 | Image Utilities | L6677 | 8KB | 4 | ~7 | 4 |
| 20 | Video Utilities | L6939 | 12KB | 4 | ~2 | 5 |
| 21 | Remote Tool Execution | L7320 | 9KB | 6 | ~5 | 2 |
| 22 | Similarity Search | L7598 | 11KB | 6 | ~2 | 4 |
| 23 | Frontend Applications | L7920 | 11KB | 6 | ~4 | 8 |
| 24 | Chat Interface | L8240 | 15KB | 6 | ~3 | 7 |
| 25 | Visualization Components | L8724 | 13KB | 8 | ~2 | 8 |
| 26 | Examples and Usage | L9157 | 12KB | 4 | ~5 | 4 |
| 27 | Basic Usage | L9553 | 8KB | 4 | ~1 | 2 |
| 28 | Custom Tools | L9859 | 9KB | 4 | ~3 | 3 |
| 29 | Developer Guide | L10139 | 10KB | 6 | ~9 | 6 |
| 30 | CI/CD Pipeline | L10468 | 8KB | 5 | ~2 | 2 |
| 31 | Documentation System | L10737 | 8KB | 4 | ~4 | 6 |


## · Overview  (L6)
  源文件: README.md, docs/index.md, vision_agent/agent/__init__.py
  System Purpose
  High-Level Architecture
    · System Components Diagram
    · Agent Core Architecture
    · Vision Tools Architecture
    · Code Execution Architecture
    · LLM Integration Architecture
  Operation Workflow
  Usage Patterns
    · 1. Prompting VisionAgent (Code Generation)
    · 2. Direct Tool Usage
  Prerequisites and Requirements

## · System Architecture  (L355)
  源文件: README.md, docs/index.md, vision_agent/agent/__init__.py, vision_agent/agent/vision_agent_coder_v2.py, vision_agent/agent/vision_agent_prompts_v2.py, vision_agent/agent/vision_agent_v2.py
  Core Architecture Overview
  Agent System Components
    · VisionAgentV2
    · VisionAgentCoderV2
    · VisionAgentPlannerV2
  Request Processing Flow
  Vision Tools System
  Code Execution System
  LLM Integration
  Data Models and Message Flow
  Configuration System
  Summary

## · Installation and Dependencies  (L814)
  源文件: README.md, docs/index.md, poetry.lock, pyproject.toml, vision_agent/utils/execute.py
  Prerequisites
    · Installation Workflow
  Why API Keys Are Required
  Basic Installation
  API Key Configuration
    · Obtaining API Keys
    · Setting Environment Variables
  Dependency Structure
    · Main Dependencies
    · Development Dependencies
  Code Execution System
  Alternative LLM Provider Configuration
  Troubleshooting
    · Common Installation Issues
  Next Steps

## · Agent System  (L1129)
  源文件: examples/chat/app.py, vision_agent/agent/__init__.py, vision_agent/agent/agent.py, vision_agent/agent/vision_agent_coder_v2.py, vision_agent/agent/vision_agent_prompts_v2.py, vision_agent/agent/vision_agent_v2.py
  Architecture Overview
  Core Components
    · Agent Base Classes
    · VisionAgentV2
    · VisionAgentCoderV2
  Interaction and Execution Flow
  Human-in-the-Loop Interaction
  Code Structure and Key Methods
  Communication and Callback Mechanism
  Integration with Other Components

## · VisionAgentV2  (L1554)
  源文件: examples/chat/app.py, vision_agent/agent/agent.py, vision_agent/agent/vision_agent_coder_v2.py, vision_agent/agent/vision_agent_prompts_v2.py, vision_agent/agent/vision_agent_v2.py
  Purpose and Functionality
  Class Structure and Components
  Constructor Parameters
  Interaction Flow
  Key Methods
    · `__call__` Method
    · `chat` Method
  Message Processing Workflow
  Action Handling
  Conversation Management
  Human-in-the-Loop Mode
  Code Execution Security
  Usage Example
  Integration with Application Frameworks

## · VisionAgentCoderV2  (L1844)
  源文件: vision_agent/agent/vision_agent_coder_prompts_v2.py, vision_agent/agent/vision_agent_coder_v2.py, vision_agent/agent/vision_agent_planner_prompts_v2.py, vision_agent/agent/vision_agent_prompts_v2.py, vision_agent/agent/vision_agent_v2.py
  Overview
  Class Architecture
  Initialization and Components
    · Key Components:
  Code Generation Process
    · generate_code
    · generate_code_from_plan
  Tool Selection and Code Generation
    · Tool Recommendation
    · Code Writing
  Testing and Debugging
    · Test Generation
    · Code Execution and Debugging
  Output Format
  Integration with VisionAgentV2
  Prompts and Templates
  API Reference
    · Main Methods
    · Support Functions

## · VisionAgentPlannerV2  (L2244)
  源文件: vision_agent/agent/vision_agent_coder_prompts_v2.py, vision_agent/agent/vision_agent_planner_prompts_v2.py, vision_agent/agent/vision_agent_planner_v2.py, vision_agent/tools/planner_tools.py
  Purpose and Scope
  System Architecture
    · Component Integration
  Planning Process
    · Initialization
    · Planning Workflow
  Key Components
    · Planning-Specific Tools
    · Multi-Trial Planning
    · Plan Critique and Refinement
    · Tool Selection
  Human-in-the-Loop Mode
  Plan Finalization
  Safety Mechanisms
    · Code Safety
    · Response Safety
  Conclusion

## · LLM Integration  (L2594)
  源文件: docs/api/lmm.md, docs/api/tools.md, vision_agent/lmm/__init__.py, vision_agent/lmm/lmm.py
  Architecture Overview
    · LMM Class Hierarchy
    · LMM Integration with Vision Agent Components
  Core Interface
    · LMM Abstract Methods
  Provider Implementations
    · Provider Comparison
    · OpenAILMM
    · AzureOpenAILMM
    · OllamaLMM
    · AnthropicLMM
    · GoogleLMM
  Image Handling
    · Image Processing Workflow
  Response Streaming
  Usage Example

## · Vision Tools  (L2895)
  源文件: vision_agent/tools/__init__.py, vision_agent/tools/tools.py
  Tools Registry System
    · Tool Registration
    · Tool Structure
  Vision Tool Categories
    · Object Detection Tools
    · Instance Segmentation Tools
    · Video Tracking Tools
    · OCR & Text Extraction
    · Document Analysis
    · Visual Question-Answering Tools
    · Image Processing Tools
  Remote Inference System
  Tool Integration with Agent System
    · Tool Documentation
  Summary

## · Tools Registry  (L3470)
  源文件: vision_agent/tools/__init__.py, vision_agent/tools/meta_tools.py
  Purpose and Functionality
  Registry Architecture
  Tool Registration Mechanism
    · Registration Decorator Implementation
  Tool Organization
  Tool Discovery and Description
  Integration with the Agent System
  Extending the Tools Registry
  Meta Tools
  Summary

## · Object Detection Tools  (L3766)
  源文件: tests/integ/test_tools.py, vision_agent/tools/tools.py, vision_agent/utils/exceptions.py, vision_agent/utils/video_tracking.py
  Purpose and Scope
  Object Detection System Overview
  Available Object Detection Models
  Basic Object Detection Workflow
  Common Object Detection Tools
    · OwlV2 Object Detection
    · Florence2 Object Detection
    · CountGD Object Detection
    · Custom Object Detection
  Instance Segmentation Tools
    · SAM2 Segmentation
  Video Tracking
  Implementation Details
    · ODModels Enum
    · Output Format
  Error Handling
  Usage Considerations

## · Video Processing Tools  (L4110)
  源文件: tests/integ/test_tools.py, tests/unit/tools/test_video.py, vision_agent/tools/tools.py, vision_agent/utils/exceptions.py, vision_agent/utils/video.py, vision_agent/utils/video_tracking.py
  Purpose and Scope
  Video Processing Architecture
  Video Tracking Data Flow
  Core Utilities
    · Video Manipulation Functions
    · Video Tracking Utilities
  Object Tracking System
  High-Level Video Tools
    · Generic Video Tracking
    · Model-Specific Video Tracking Tools
    · Example: Florence2 Video Tracking
  Object Detection Models
  Implementation Details
    · Chunk-based Processing
    · Object Identity Preservation
    · Post-processing
  Integration with Other Systems

## · Document Analysis Tools  (L4414)
  源文件: vision_agent/.sim_tools/df.csv, vision_agent/.sim_tools/embs.npy, vision_agent/tools/tools.py
  Purpose and Scope
  Document Analysis Tools Overview
  Text Recognition Tools
    · Florence2 OCR
    · Generic OCR
    · Claude35 Text Extraction
  Document Understanding Tools
    · Document Extraction
    · Document QA
  Visual Question Answering for Documents
    · Qwen 2.5 Visual Language Model for Documents
  Document Analysis Tools Integration
  Implementation Details
    · OCR Implementation
    · Result Display and Visualization
  Usage Examples
    · Basic Text Extraction
    · Document Question Answering
    · Structured Document Extraction
  Future Directions

## · Meta Tools  (L4784)
  源文件: tests/unit/test_meta_tools.py, tests/unit/test_vac.py, vision_agent/tools/meta_tools.py
  Overview
  Artifact Management System
    · Artifacts Class
    · File Operations Workflow
  Media Artifact Handling
    · Media Functions
  Code and Text Utilities
    · Line Viewing and Diffing
  Tool Discovery
    · Tool Description
  Result Display
    · Result Display System
  Integration with Vision Agent System
  Usage Patterns
  Relationship to Other Systems

## · Code Execution System  (L5126)
  源文件: poetry.lock, pyproject.toml, vision_agent/agent/vision_agent_coder_v2.py, vision_agent/agent/vision_agent_prompts_v2.py, vision_agent/agent/vision_agent_v2.py, vision_agent/utils/execute.py
  Purpose and Overview
  System Architecture
  Key Components
    · CodeInterpreter Interface
    · LocalCodeInterpreter
    · CodeInterpreterFactory
    · Result Data Models
  Execution Workflow
    · Code Execution Process
    · Error Handling and Recovery
  Integration with Agent Components
    · VisionAgentV2 Integration
    · VisionAgentCoderV2 Integration
  Implementation Details
    · Execution Result Parsing
    · MIME Type Support
  Usage Examples
    · Basic Usage Pattern
    · Executing Code in Isolation
    · Working with Files
  Conclusion

## · Code Interpreter  (L5625)
  源文件: poetry.lock, pyproject.toml, vision_agent/utils/execute.py
  Architecture Overview
  Interface and Implementation
    · CodeInterpreter Abstract Interface
    · LocalCodeInterpreter Implementation
    · Factory Pattern
  Integration with Vision Agent
  Execution Data Models
    · Execution
    · Result Types and MIME Types
  Execution Process
  Error Handling
  Example Usage
  Integration with Other Components

## · Execution Workflow  (L5934)
  源文件: poetry.lock, pyproject.toml, vision_agent/agent/vision_agent_coder_v2.py, vision_agent/agent/vision_agent_prompts_v2.py, vision_agent/agent/vision_agent_v2.py, vision_agent/utils/execute.py
  Execution System Architecture
  Execution Workflow
  Code Execution Process
  Result Processing
  Error Handling and Debugging Workflow
  Integration with Agent System
  Execution Callbacks and Telemetry
  Execution Formats and MIME Types

## · Utility Systems  (L6319)
  源文件: .github/workflows/ci_cd.yml, vision_agent/sim/sim.py, vision_agent/utils/image_utils.py, vision_agent/utils/tools.py
  Overview of Utility Systems
  Image Utilities
    · Image Format Conversion
    · Bounding Box Utilities
    · Mask Utilities
    · Visualization Utilities
  Remote Tool Execution
    · API Request Management
    · Authentication and Error Handling
    · Auxiliary Tool Functions
  Similarity Search System
    · Base Similarity Class
    · Embedding Providers
    · Tool Recommendation
    · Caching Mechanisms
  Summary

## · Image Utilities  (L6677)
  源文件: .github/workflows/ci_cd.yml, vision_agent/.sim_tools/df.csv, vision_agent/.sim_tools/embs.npy, vision_agent/utils/image_utils.py
  Purpose and Scope
  System Context
  Functional Components
  Image Format Conversion
    · Key Functions
  Bounding Box Operations
    · Key Functions
  Mask Encoding and Decoding
    · Key Functions
  Visualization Functions
    · Key Functions
  Common Usage Patterns
    · Processing Detection Results
    · Handling Segmentation Masks
    · Format Conversion for API Integration
  Integration with Vision Tools
  Summary

## · Video Utilities  (L6939)
  源文件: tests/integ/test_tools.py, tests/unit/tools/test_video.py, vision_agent/utils/exceptions.py, vision_agent/utils/video.py, vision_agent/utils/video_tracking.py
  Overview
  Core Video Processing Functions
    · Video Creation
    · Frame Extraction
  Video Tracking Utilities
    · Tracking Workflow
    · Key Components
  Integration with Vision Tools
  Error Handling
  Performance Considerations
  Usage Examples

## · Remote Tool Execution  (L7320)
  源文件: vision_agent/sim/sim.py, vision_agent/utils/tools.py
  System Overview
  Authentication and Configuration
  Core API Functions
    · Inference Request Workflow
  Request Types and Data Handling
    · File Handling
  Retry and Error Handling
  Tool Call Tracing
  Remote Embedding Requests
  Remote Endpoints
  Integration with the Vision Agent System
  Environment Variables

## · Similarity Search  (L7598)
  源文件: vision_agent/.sim_tools/df.csv, vision_agent/.sim_tools/embs.npy, vision_agent/sim/sim.py, vision_agent/utils/tools.py
  Purpose and Scope
  Architecture Overview
  Core Components
    · Sim Class
    · Embedding and Caching
  Implementation Details
    · Data Storage
    · Similarity Calculation
  Specialized Implementations
    · 1. OpenAI Embeddings (Base Sim)
    · 2. Azure OpenAI Embeddings
    · 3. Ollama Embeddings
    · 4. Stella Embeddings
  Usage
    · Tool Recommendation
    · Embedding Workflow
  Caching Mechanisms
  Integration with Tool Registry
  Configuration
  Summary

## · Frontend Applications  (L7920)
  源文件: .gitignore, examples/chat/chat-app/ResultVisualizer.tsx, examples/chat/chat-app/src/app/page.tsx, examples/chat/chat-app/src/components/ChatSection.tsx, examples/chat/chat-app/src/components/ImageVisualizer.tsx, examples/chat/chat-app/src/components/PolygonDrawer.tsx, examples/chat/chat-app/src/components/PreviewSection.tsx, vision_agent/sim/__init__.py
  Overview
  Main Components
  Application Layout
  Message Handling and Display
  Component Functionality
    · ChatSection
    · PolygonDrawer
    · PreviewSection
  Communication with Backend
  Human-in-the-Loop Interaction
  Visualization Components
  State Management
  Frontend Technologies

## · Chat Interface  (L8240)
  源文件: examples/chat/app.py, examples/chat/chat-app/src/app/page.tsx, examples/chat/chat-app/src/components/ChatSection.tsx, examples/chat/chat-app/src/components/ImageVisualizer.tsx, examples/chat/chat-app/src/components/PreviewSection.tsx, vision_agent/agent/agent.py, vision_agent/sim/__init__.py
  Overview
  Architecture Components
  Backend Server
    · Key Components
  Frontend Client
    · Chat Section
    · WebSocket Communication
    · Message Formatting
  Interactive Features
    · Human-in-the-Loop (HIL) Mode
    · Polygon Drawing
  Preview Section
  Agent Integration
  Communication Protocol
    · Backend to Frontend
    · Frontend to Backend
  Usage Example
  Starting the Chat Interface

## · Visualization Components  (L8724)
  源文件: .gitignore, examples/chat/chat-app/ResultVisualizer.tsx, examples/chat/chat-app/src/app/page.tsx, examples/chat/chat-app/src/components/ChatSection.tsx, examples/chat/chat-app/src/components/ImageVisualizer.tsx, examples/chat/chat-app/src/components/PolygonDrawer.tsx, examples/chat/chat-app/src/components/PreviewSection.tsx, vision_agent/sim/__init__.py
  Purpose and Scope
  Component Overview
  Detection Visualization Components
    · Component Hierarchy
    · VisualizerHiL
    · ImageVisualizer
  User Annotation Components
    · PolygonDrawer
  Display and Preview Components
    · PreviewSection
    · ChatSection Visualization Handling
  Data Flow and Integration
    · Detection Data Structure
  Human-in-the-Loop (HIL) Interaction
  Integration with Main Application

## · Examples and Usage  (L9157)
  源文件: README.md, docs/index.md, examples/custom_tools/README.md, examples/custom_tools/run_custom_tool.py
  Basic Usage Patterns
    · Prompt-Based Usage Workflow
    · Direct Tool Usage
  Creating Custom Tools
    · Custom Tool Architecture
    · Creating a Custom Tool
    · Important Considerations for Custom Tools
    · Using Custom Tools
  Common Use Cases and Workflows
    · End-to-End Workflow Example
  LLM Provider Configuration
  Available Models and When to Use Them

## · Basic Usage  (L9553)
  源文件: README.md, docs/index.md
  Prerequisites
  Installation
  Setting Up API Keys
  Basic Usage Patterns
    · Usage Pattern Workflow
  Prompting VisionAgent
    · VisionAgent Prompting System
    · Sample Code for Prompting VisionAgent
    · What Happens During Execution
  Using Specific Tools Directly
    · Vision Tools System
    · Example: Object Detection
    · Example: Video Tracking
  Configuring LLM Providers
    · Using Only Anthropic Models
    · Manually Configuring LLM Providers
  Complete Workflow Example

## · Custom Tools  (L9859)
  源文件: examples/custom_tools/README.md, examples/custom_tools/run_custom_tool.py, vision_agent/tools/__init__.py
  Tool Registration System
  Creating a Custom Tool
    · Required Structure
  Example: Template Matching Tool
  Import Requirements
  Using Custom Tools
  Best Practices
  Implementation Details
  Integration with Vision Agent

## · Developer Guide  (L10139)
  源文件: .github/workflows/ci_cd.yml, .github/workflows/docs.yml, vision_agent/models/__init__.py, vision_agent/models/agent_types.py, vision_agent/utils/agent.py, vision_agent/utils/image_utils.py
  Development Environment Setup
  CI/CD Pipeline
    · Automated Testing
    · Release Process
  Documentation System
    · Documentation Workflow
  Code Architecture
    · Core Data Models
  Image Utilities
    · Key Image Utility Functions
  Agent Utilities
    · Code and Content Extraction
  Development Best Practices
  Conclusion

## · CI/CD Pipeline  (L10468)
  源文件: .github/workflows/ci_cd.yml, vision_agent/utils/image_utils.py
  Overview
  Workflow Triggers
  Unit Test Job
  Integration Test Job
  Release Job
  Development Workflow Integration
  Package Publishing Details
  Environment Setup and Dependencies
  Skipping CI or Releases

## · Documentation System  (L10737)
  源文件: .github/workflows/docs.yml, docs/api/agent.md, mkdocs.yml, vision_agent/models/__init__.py, vision_agent/models/agent_types.py, vision_agent/utils/agent.py
  System Architecture
  Build and Deployment Workflow
  Documentation Configuration
    · Site Settings
    · Theme Configuration
    · Navigation Structure
  API Documentation Generation
    · Docstring Extraction
    · Plugin Configuration
  Markdown Extensions
  Local Development
    · Setup and Preview
  Contributing to Documentation
    · API Documentation
    · Manual Documentation
    · Documentation Organization
  Model Documentation