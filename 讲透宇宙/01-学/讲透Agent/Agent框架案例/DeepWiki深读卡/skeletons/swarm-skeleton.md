# Skeleton: swarm（22 页）

| # | 页面 | full.md 行 | 大小KB | mermaid | 表格 |
|---|------|-----------|--------|---------|------|
| 1 | Overview | L6 | 6KB | 3 | ~7 |
| 2 | Core Implementation | L167 | 7KB | 5 | ~0 |
| 3 | Swarm Class (core.py) | L365 | 8KB | 3 | ~0 |
| 4 | Types and Data Models | L582 | 6KB | 2 | ~25 |
| 5 | Utility Functions | L729 | 7KB | 2 | ~9 |
| 6 | REPL and Demo Loop | L891 | 6KB | 2 | ~6 |
| 7 | Tool System | L1035 | 5KB | 3 | ~22 |
| 8 | Examples | L1193 | 5KB | 2 | ~6 |
| 9 | Basic Examples | L1316 | 5KB | 2 | ~10 |
| 10 | Airline Customer Service Example | L1435 | 8KB | 2 | ~5 |
| 11 | Customer Service Streaming Example | L1580 | 7KB | 3 | ~5 |
| 12 | Customer Service Swarm Class | L1705 | 7KB | 3 | ~4 |
| 13 | Engines | L1895 | 10KB | 3 | ~4 |
| 14 | Other Examples | L2111 | 6KB | 3 | ~0 |
| 15 | Testing | L2248 | 4KB | 2 | ~0 |
| 16 | Unit Tests | L2347 | 5KB | 2 | ~11 |
| 17 | Mock Client | L2478 | 5KB | 2 | ~5 |
| 18 | Developer Guide | L2587 | 4KB | 2 | ~0 |
| 19 | Creating Custom Agents | L2693 | 6KB | 3 | ~8 |
| 20 | Creating Custom Tools | L2842 | 7KB | 2 | ~21 |
| 21 | Building Custom Applications | L3035 | 6KB | 3 | ~5 |
| 22 | Glossary | L3175 | 6KB | 2 | ~7 |


## · Overview  (L6)
  Purpose and Scope
  Core Primitives
  High-Level Architecture
    · System Components
    · The Run Loop
  Key Concepts
    · Agents and Instructions
    · Context Variables
    · Tool Execution
  Data Flow: Code to API
  Implementation Variations

## · Core Implementation  (L167)
  Architecture Overview
  Components
    · Swarm Class (core.py)
    · Types and Data Models
    · Utility Functions
    · REPL and Demo Loop
  Execution Flow
  Bridge: Natural Language to Code Entities
    · Agent Definition Bridge
    · Tool Execution Bridge
  Integration with OpenAI API

## · Swarm Class (core.py)  (L365)
  Purpose and Overview
  Class Structure and Initialization
  Core Components and Relationships
  Execution Flow
  Key Methods
    · get_chat_completion
    · handle_tool_calls
    · handle_function_result
    · run and run_and_stream
  Data Flow
  Context Variables
  Agent Switching (Handoffs)
  Summary

## · Types and Data Models  (L582)
  Core Data Architecture
    · Agent
    · Response
    · Result
  Data Flow and Transitions
    · Code Entity Flow: Request to Response
  Tool Execution and Handoff Logic
    · Tool Return Handling Logic
  Detailed Field Definitions
    · AgentFunction
    · Summary Table: Type Flow

## · Utility Functions  (L729)
  Overview
  Function Conversion
    · Natural Language to Code Entity Space: Function Conversion
    · Function to JSON Conversion
  Response Merging
    · Code Entity Space: Streaming Data Flow
    · Merge Functions
  Debug Printing
    · Debug Print Function
  Integration with Core Swarm

## · REPL and Demo Loop  (L891)
    · Overview of the Demo Loop
    · Key Functions
    · Implementation Detail: The Run Loop
    · Usage Example

## · Tool System  (L1035)
  Purpose and Scope
  Core Logic: `function_to_json`
    · Transformation Process
    · Type Mapping
  Context Variables Injection
    · Data Flow for Tool Execution
  Key Implementation Details
    · Docstring Extraction
    · The `Result` Object
    · Handling Handoffs
  Pydantic Schema (Customer Service Example)
  Summary Table of Tool Attributes

## · Examples  (L1193)
  High-Level Architecture of Examples
    · Mapping Natural Language to Code Entities
  Basic Examples
  Airline Customer Service
  Customer Service Streaming
  Other Specialized Examples
    · Entity Relationship: Examples to Core Components

## · Basic Examples  (L1316)
  Bare Minimum Implementation
    · Data Flow: Bare Minimum
  Agent Handoffs
    · Logic Flow: Language Handoff
  Context Variables
    · Key Implementation Details
  Function Calling
    · Example: Weather Tool
  Interactive Loop (No Helpers)
    · Manual Loop Logic

## · Airline Customer Service Example  (L1435)
  Agent Architecture and Hierarchy
    · Agent Roles
    · Agent Relationship Diagram
  Policies and Instructions
    · Policy Implementation
  Tools and Implementation
    · Action Tools
    · Data Flow Diagram
  Evaluation Framework
    · Evaluation Cases
    · Running Evaluations

## · Customer Service Streaming Example  (L1580)
  Purpose and Scope
  Architecture Overview
    · System Mapping: Natural Language to Code Entities
  Key Components
    · Swarm and Engine Selection
    · Task and Prompt System
    · Tool Configurations
    · Knowledge Base Integration
  Detailed Sub-Pages

## · Customer Service Swarm Class  (L1705)
  Purpose and Scope
  Overview
  Class Definition and Initialization
    · Initialization
  Core Functionality
    · Task Deployment Lifecycle
    · Task Management and Loading
  Engine Instantiation Logic
  System Constants and Configuration

## · Engines  (L1895)
  Purpose and Scope
  Engine System Overview
    · Engine Architecture
    · Engine Selection Flow
  Engine Types
    · AssistantsEngine
    · LocalEngine
  Engine Selection and Initialization
    · Engine Selection Table
    · Initialization Code
    · Deployment Process
  Engine Interface
    · Implementation Diagram
  Summary

## · Other Examples  (L2111)
  Triage Agent
    · Implementation Detail
    · Evaluation Logic
  Weather Agent
    · Key Components
  Personal Shopper
    · Database Integration
    · Agent Hierarchy
  Support Bot
    · Implementation Components

## · Testing  (L2248)
  Infrastructure Overview
    · Natural Language to Code Mapping: Testing Space
  Unit Tests
  Mock Client

## · Unit Tests  (L2347)
  Core Logic Testing (test_core.py)
    · Key Test Scenarios
    · Data Flow: Tool Execution and Handoff
  Utility Testing (test_util.py)
    · Schema Generation Mapping
  Implementation Details
    · Test Execution Loop
    · Handling Context Variables

## · Mock Client  (L2478)
  Overview
    · Key Components
  Implementation Details
    · MockOpenAIClient Class
    · Response Generation
  Key Functions
    · `create_mock_response`
    · `set_sequential_responses`
  Usage in Testing
    · Data Flow Example: Tool Execution

## · Developer Guide  (L2587)
  Purpose and Scope
  Core Development Workflow
  Creating Custom Agents
  Creating Custom Tools
  Building Custom Applications

## · Creating Custom Agents  (L2693)
  Overview
  Defining an Agent
    · Model Selection
  Instructions and Dynamic Context
  Tool Assignment and Handoff Patterns
    · Handoffs (Agent Switching)
  Implementation Detail: The Run Loop
    · Response Object
  Best Practices

## · Creating Custom Tools  (L2842)
  Overview of Tool Execution
  Defining Custom Functions
    · Basic Function
    · Context Variables Injection
  The Result Return Type
    · Result Fields
    · Implementation Example
  Technical Implementation Details
    · Schema Generation (`function_to_json`)
    · Execution Logic (`handle_tool_calls`)
  Bridge: Natural Language to Code Entity Space
  Advanced Patterns
    · Agent Handoffs
    · Tool Schema Mapping
  Summary Table

## · Building Custom Applications  (L3035)
  Purpose and Scope
  Swarm Application Architecture
    · Natural Language to Code Entity Mapping
  Core Implementation Patterns
    · 1. The Execution Loop
    · 2. Multi-Agent Triage and Handoffs
  Implementation Approaches
    · 1. Direct Core Integration
    · 2. Task-Based and Streaming Architectures
  Best Practices for Custom Applications
  Case Study: Airline Multi-Agent System

## · Glossary  (L3175)
  Core Concepts
    · Agent
    · Handoff
    · Context Variables
    · Turn
  Technical Terms & Jargon
  Data Flow: Natural Language to Code Entity
  Architecture: Component Interaction
  Example-Specific Terminology
    · Triage Agent
    · Routine
    · REPL (Read-Eval-Print Loop)
