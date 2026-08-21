# Skeleton: voyager（16 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 10KB | 4 | ~0 | 3 |
| 2 | Installation and Setup | L318 | 7KB | 3 | ~4 | 4 |
| 3 | Minecraft Setup | L604 | 7KB | 4 | ~1 | 2 |
| 4 | Fabric Mods Installation | L827 | 6KB | 4 | ~4 | 2 |
| 5 | Core Architecture | L1029 | 10KB | 7 | ~2 | 3 |
| 6 | Agents | L1333 | 7KB | 3 | ~6 | 2 |
| 7 | Curriculum Agent | L1532 | 11KB | 4 | ~4 | 2 |
| 8 | Action Agent | L1860 | 9KB | 5 | ~3 | 2 |
| 9 | Critic Agent | L2148 | 5KB | 3 | ~2 | 1 |
| 10 | Skill Manager | L2302 | 10KB | 8 | ~2 | 2 |
| 11 | Skill System | L2636 | 9KB | 7 | ~2 | 2 |
| 12 | Skill Library | L2901 | 7KB | 3 | ~1 | 1 |
| 13 | Control Primitives | L3108 | 9KB | 5 | ~2 | 2 |
| 14 | Environment Integration | L3352 | 9KB | 5 | ~5 | 3 |
| 15 | Usage and Examples | L3663 | 11KB | 3 | ~5 | 3 |
| 16 | Troubleshooting | L4077 | 10KB | 6 | ~0 | 3 |


## · Overview  (L6)
  源文件: README.md, voyager/__init__.py, voyager/voyager.py
  Purpose and Scope
  What is Voyager?
  System Architecture Overview
  Core Components
    · Voyager Class
    · Agent System
  Learning and Task Execution
    · Lifelong Learning Cycle
    · Task Execution and Skill Acquisition
  Data Flow
  Key Features and Capabilities
  Usage Modes

## · Installation and Setup  (L318)
  源文件: FAQ.md, README.md, requirements.txt, setup.py
  System Requirements
  Installation Overview
  Python Installation
  Node.js Installation
  Minecraft Authentication Setup
    · Method 1: Azure Login (Recommended)
    · Method 2: Direct Port Connection
  OpenAI API Configuration
  Running Voyager
    · Lifelong Learning Mode
    · Resuming from a Checkpoint
    · Task Execution with a Learned Skill Library
  System Component Integration
  Common Installation Issues
  Estimated Costs

## · Minecraft Setup  (L604)
  源文件: FAQ.md, installation/minecraft_instance_install.md
  Prerequisites
  Setup Methods Overview
  Option 1: Microsoft Azure Login (Recommended)
    · Setup Process
    · Configuration for Voyager
  Option 2: Minecraft Official Launcher
    · Setup Process
    · Configuration for Voyager
  Connection Diagram
  Common Issues and Troubleshooting
    · Connection Errors After Azure Login
    · KeyError: 'access_token' After Copying the Link
    · Subprocess Mineflayer Failed to Start
  Next Steps

## · Fabric Mods Installation  (L827)
  源文件: FAQ.md, installation/fabric_mods_install.md
  Purpose and Scope
  Fabric Loader Installation
    · Installation Process Diagram
  Required Mods Overview
  Mods Integration with Voyager
  Installation Steps
    · Standard Mods Installation
    · Better Respawn Installation
  Configuration
    · Better Respawn Configuration
    · Fabric Version Configuration
  Verification and Troubleshooting
    · Installation Verification
    · Common Issues
  Relationship to System Architecture

## · Core Architecture  (L1029)
  源文件: README.md, voyager/agents/__init__.py, voyager/voyager.py
  System Overview
  Key Components and Their Roles
  Voyager Class Implementation
  Data Flow and Control Loop
  Initialization and Configuration
  Learning Process Implementation
  Task Execution Process
  Integration with Minecraft
  Conclusion

## · Agents  (L1333)
  源文件: voyager/agents/__init__.py, voyager/voyager.py
  Agent Architecture
    · Agent Class Structure
  Agent Types
    · CurriculumAgent
    · ActionAgent
    · CriticAgent
    · SkillManager
  Agent Interaction Flow
  Learning Pipeline
  Agent Configuration Parameters
  Learning Process
  Task Execution Process

## · Curriculum Agent  (L1532)
  源文件: voyager/agents/curriculum.py, voyager/voyager.py
  Architecture and Role
  Core Functionality
    · Task Proposal System
    · Task Tracking and Progress Management
    · Knowledge Acquisition
  Key Components
    · Observation System
    · Question-Answering Cache
    · Task Decomposition
  Implementation Details
    · Initialization Parameters
    · State Management
    · Warm-up System Configuration
    · Special Task Handling
  Integration with Voyager
  File Structure

## · Action Agent  (L1860)
  源文件: voyager/agents/action.py, voyager/voyager.py
  Overview
  Core Functionality
  Implementation Details
    · Initialization
    · Message Generation
    · Processing LLM Response
  Chest Memory Management
    · Chest Memory Operations
  Integration with Voyager
  Configuration Parameters
  Technical Implementation
  Error Handling
  Summary

## · Critic Agent  (L2148)
  源文件: voyager/voyager.py
  Purpose and Role
  Integration with Voyager System
  Implementation Details
    · Core Methods
    · Mode of Operation
  Configuration
  Evaluation Process
  Usage in the Learning Loop
  Related Components

## · Skill Manager  (L2302)
  源文件: voyager/agents/skill.py, voyager/voyager.py
  Overview
  Architecture
  Initialization
  Skill Storage Structure
  Key Operations
    · Adding New Skills
    · Retrieving Skills
    · Generating Skill Descriptions
  Integration with Voyager
  Control Primitives
  Implementation Details
    · Skill Format
    · Vector Database
    · Error Handling and Edge Cases

## · Skill System  (L2636)
  源文件: skill_library/README.md, voyager/agents/skill.py
  Purpose and Overview
  Key Components
    · Skills and Programs
  Skill Storage and Representation
  Skill Operations
    · Skill Retrieval Process
    · Adding New Skills
    · Generating Skill Descriptions
  Integration with Voyager Learning Loop
  Using Skill Libraries
  Technical Implementation
  Contributing to the Skill Library

## · Skill Library  (L2901)
  源文件: skill_library/README.md
  Purpose and Structure
  Interaction with Voyager System
  Available Libraries
    · Official Libraries
    · Community Contributions
  Using a Skill Library
    · Resuming from Community Contributions
  Contributing Your Own Skill Library
  Skill Library Integration
  Technical Implementation

## · Control Primitives  (L3108)
  源文件: voyager/agents/skill.py, voyager/control_primitives/useChest.js
  Purpose and Role in the System
  Integration with Skill System
  Chest Interaction Primitives
    · Core Chest Functions
    · Chest Interaction Flow
    · Detailed Function Behavior
    · Error Handling in Chest Primitives
  Usage in the Skill System
  System Integration of Control Primitives
  Conclusion

## · Environment Integration  (L3352)
  源文件: installation/minecraft_instance_install.md, voyager/env/mineflayer/lib/observation/chests.js, voyager/voyager.py
  Overview of Environment Integration
  Environment Architecture
    · VoyagerEnv Bridge
    · Environment Initialization Flow
  Environment Configuration
  Environment Interaction
    · Step Function
    · Reset Function
  Observation System
    · Chest Observation
  Event Handling
  Integration with Agent System
  Error Handling and Recovery
  Conclusion

## · Usage and Examples  (L3663)
  源文件: README.md, skill_library/README.md, voyager/voyager.py
  Basic Usage Patterns
  Initializing Voyager
    · Azure Login Note
  Learning Mode
  Task Execution Mode
  Checkpoint Management
  Using Skill Libraries
    · Available Skill Libraries
    · Skill Library Structure
  Advanced Usage Examples
    · Custom Task Decomposition and Execution
    · Reset Options for Task Execution
    · Controlling Maximum Retries
  Sample Usage Workflows
    · Lifelong Learning Workflow
    · Task-Specific Execution Workflow

## · Troubleshooting  (L4077)
  源文件: FAQ.md, installation/fabric_mods_install.md, installation/minecraft_instance_install.md
  Common Installation Issues
    · Minecraft and Fabric Setup
    · Authentication Problems
  Runtime Issues
    · Mineflayer Connection Problems
    · Bot Behavior Issues
  LLM Integration Issues
    · Using GPT-3.5 Instead of GPT-4
    · API Costs and Budget Considerations
  Environment Configuration Issues
    · Minecraft World Setup
    · Java Version Issues for Mod Compilation
  System Diagnosis Flowchart
  Component-Specific Troubleshooting
    · Voyager Core System Issues
    · Agent Subsystem Issues
  Voyager-Minecraft Communication Diagram