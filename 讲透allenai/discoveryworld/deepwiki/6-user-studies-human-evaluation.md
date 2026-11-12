<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/discoveryworld · page 6 User Studies & Human Evaluation · fetched 2026-10-26 -->

# User Studies & Human Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README-USERSTUDY.md](README-USERSTUDY.md)

</details>



This page covers the human evaluation system in DiscoveryWorld, which enables researchers to collect baseline human performance data for comparison with AI agents. The user study system provides a standardized interface for human participants to complete the same scientific discovery tasks that AI agents are evaluated on.

For detailed instructions on setting up and running user studies, see [Running User Studies](#6.1). For information about analyzing the collected data and performance metrics, see [Data Collection & Analysis](#6.2). For general information about AI agent evaluation and metrics, see [Scenarios & Tasks](#2.3).

## Overview

The user study system serves as a critical component for establishing human performance baselines across DiscoveryWorld's scientific discovery scenarios. By having humans complete the same tasks under controlled conditions, researchers can meaningfully compare AI agent capabilities against human problem-solving approaches.

The system is built around the `userstudy.py` script, which provides a graphical interface that allows human participants to interact with the same virtual environment and scenarios that AI agents encounter. All participant actions, decisions, and performance metrics are logged in the same format as AI agent data, enabling direct comparison.

## User Study Architecture

### System Components

```mermaid
graph TB
    subgraph "User Study Interface"
        userstudy["scripts/userstudy.py<br/>Main GUI Interface"]
        controls["Keyboard Controls<br/>Movement & Actions"]
        display["Visual Rendering<br/>Game State Display"]
    end
    
    subgraph "Scenario Management"
        scenarios["Scenario Selection<br/>Tutorial, Normal, Challenge"]
        variations["Task Variations<br/>Seed-based Instances"]
        instructions["Task Instructions<br/>TAB Key Display"]
    end
    
    subgraph "Data Collection System"
        logger["Comprehensive Logging<br/>JSON State Capture"]
        frames["Frame Capture<br/>Screenshot Recording"]
        archive["Log Archiving<br/>ZIP File Generation"]
    end
    
    subgraph "External Documentation"
        notebook["User Notebook<br/>Manual Notes & Analysis"]
        tools["External Tools<br/>Spreadsheets, Statistics"]
        evidence["Supporting Evidence<br/>Hypothesis Documentation"]
    end
    
    userstudy --> scenarios
    userstudy --> controls
    userstudy --> display
    
    scenarios --> variations
    scenarios --> instructions
    
    userstudy --> logger
    logger --> frames
    frames --> archive
    
    notebook --> tools
    notebook --> evidence
    
    style userstudy fill:#e1f5fe
    style logger fill:#f3e5f5
    style notebook fill:#fff3e0
```

**Sources:** [README-USERSTUDY.md:1-193]()

### Participant Workflow

```mermaid
graph TD
    setup["Installation & Setup<br/>conda environment<br/>pip install requirements"]
    
    tutorial["Mandatory Tutorial<br/>Learn controls & mechanics<br/>Obtain completion code"]
    
    selection["Scenario Selection<br/>Archaeology, Chemistry, etc.<br/>Normal/Challenge difficulty"]
    
    subgraph "Gameplay Loop"
        play["Active Gameplay<br/>Keyboard controls<br/>Scientific discovery"]
        notes["External Note-taking<br/>Hypothesis formation<br/>Data analysis"]
        evidence["Evidence Collection<br/>Experimental results<br/>Model building"]
    end
    
    completion["Task Completion<br/>Automatic detection<br/>Optional continuation (F5)"]
    
    logging["Data Logging<br/>JSON state files<br/>Frame captures<br/>ZIP archiving"]
    
    submission["Data Submission<br/>Log files + notes<br/>Multiple attempts allowed"]
    
    setup --> tutorial
    tutorial --> selection
    selection --> play
    
    play --> notes
    notes --> evidence
    evidence --> play
    
    play --> completion
    completion --> logging
    logging --> submission
    
    style tutorial fill:#ffcdd2
    style logging fill:#c8e6c9
    style submission fill:#bbdefb
```

**Sources:** [README-USERSTUDY.md:13-17](), [README-USERSTUDY.md:50-132]()

## Data Collection System

### Logging Architecture

The user study system implements comprehensive data collection that mirrors the logging used for AI agent evaluation, ensuring consistent data formats for comparison.

```mermaid
graph TB
    subgraph "Real-time Data Capture"
        gamestate["Game State JSON<br/>Complete world state<br/>Each turn recorded"]
        actions["User Actions<br/>Keyboard inputs<br/>Decision timing"]
        frames["Frame Rendering<br/>Screenshot capture<br/>Visual progression"]
    end
    
    subgraph "Log Directory Structure"
        logdir["/logs/<session-id>/<br/>Individual session folder"]
        statelog["state_log.json<br/>Turn-by-turn game state"]
        framedir["/frames/<br/>Screenshot directory"]
        archive["session.zip<br/>Compressed archive"]
    end
    
    subgraph "Session Metadata"
        scenario["Scenario Name<br/>Difficulty Level<br/>Task Variation"]
        timing["Start Time<br/>Completion Time<br/>Total Duration"]
        completion["Completion Status<br/>Success/Failure<br/>Exit Condition"]
    end
    
    gamestate --> statelog
    actions --> statelog
    frames --> framedir
    
    statelog --> logdir
    framedir --> logdir
    logdir --> archive
    
    scenario --> statelog
    timing --> statelog
    completion --> statelog
    
    style gamestate fill:#e1f5fe
    style archive fill:#f3e5f5
    style timing fill:#fff3e0
```

**Sources:** [README-USERSTUDY.md:134-179]()

### Data Format Consistency

The logging system ensures that human performance data is collected in the same format as AI agent data, enabling direct statistical comparison:

| Data Type | Human Study | AI Agent | Purpose |
|-----------|-------------|----------|---------|
| State Logs | JSON per turn | JSON per turn | Complete world state tracking |
| Action Logs | Keyboard inputs | API calls | Decision sequence analysis |
| Frame Captures | Screenshots | Rendered images | Visual behavior analysis |
| Timing Data | Real-time stamps | Processing time | Performance comparison |
| Completion Metrics | Success/failure | Scorecard system | Task evaluation |

**Sources:** [README-USERSTUDY.md:173-179]()

## Scenario Coverage

### Available Scenarios

The user study system covers the same scientific discovery scenarios available to AI agents:

```mermaid
graph LR
    subgraph "Mandatory Component"
        tutorial["Tutorial<br/>Control familiarization<br/>Completion code required"]
    end
    
    subgraph "Core Scenarios"
        archaeology["Archaeology Dig<br/>Normal + Challenge"]
        chemistry["Combinatorial Chemistry<br/>Normal + Challenge"]
        nutrients["Plant Nutrients<br/>Normal + Challenge"]
        proteomics["Proteomics<br/>Normal + Challenge"]
        reactor["Reactor Lab<br/>Normal + Challenge"]
        translation["Lost in Translation<br/>Normal + Challenge"]
        spacesick["Space Sick<br/>Normal + Challenge"]
        rocket["Rocket Science<br/>Normal only"]
    end
    
    subgraph "Task Configuration"
        variation["Task Variation: 1<br/>Standardized instances"]
        difficulty["Difficulty Levels<br/>Normal: 1000 steps<br/>Challenge: 1000 steps"]
    end
    
    tutorial --> archaeology
    tutorial --> chemistry
    tutorial --> nutrients
    tutorial --> proteomics
    tutorial --> reactor
    tutorial --> translation
    tutorial --> spacesick
    tutorial --> rocket
    
    variation --> archaeology
    variation --> chemistry
    difficulty --> archaeology
    difficulty --> chemistry
    
    style tutorial fill:#ffcdd2
    style variation fill:#e1f5fe
    style difficulty fill:#f3e5f5
```

**Sources:** [README-USERSTUDY.md:59-74](), [README-USERSTUDY.md:77-81]()

## Integration with Evaluation Framework

### Human-AI Comparison Pipeline

The user study system integrates with DiscoveryWorld's broader evaluation framework to enable systematic comparison between human and AI agent performance:

```mermaid
graph TB
    subgraph "Human Performance Collection"
        human_ui["scripts/userstudy.py<br/>Human interface"]
        human_logs["Human log files<br/>JSON + frames"]
        human_notes["External notes<br/>Hypothesis documentation"]
    end
    
    subgraph "AI Agent Evaluation"
        agent_api["DiscoveryWorldAPI<br/>Agent interface"]
        agent_logs["Agent log files<br/>JSON + frames"]
        agent_scores["Automated scoring<br/>Scorecard system"]
    end
    
    subgraph "Comparative Analysis"
        format_align["Data Format Alignment<br/>Consistent JSON structure"]
        perf_metrics["Performance Metrics<br/>Completion rates<br/>Time to solution<br/>Action efficiency"]
        behavior_analysis["Behavioral Analysis<br/>Strategy comparison<br/>Decision patterns"]
    end
    
    subgraph "Research Outputs"
        baselines["Human Baselines<br/>Performance benchmarks"]
        comparisons["Human-AI Comparison<br/>Capability assessment"]
        insights["Research Insights<br/>Improvement directions"]
    end
    
    human_ui --> human_logs
    human_logs --> format_align
    human_notes --> behavior_analysis
    
    agent_api --> agent_logs
    agent_logs --> format_align
    agent_scores --> perf_metrics
    
    format_align --> perf_metrics
    perf_metrics --> behavior_analysis
    
    behavior_analysis --> baselines
    baselines --> comparisons
    comparisons --> insights
    
    style human_ui fill:#fff3e0
    style agent_api fill:#e1f5fe
    style format_align fill:#f3e5f5
    style insights fill:#c8e6c9
```

**Sources:** [README-USERSTUDY.md:5-8](), [README-USERSTUDY.md:88-94]()

## Controls and Interface

The user study interface provides comprehensive keyboard controls that map human actions to the same action space available to AI agents:

| Control Category | Keys | Function | AI Agent Equivalent |
|------------------|------|----------|-------------------|
| Movement | Arrow keys | Rotate/move forward/backward | `move()`, `rotate()` |
| Object Interaction | Space, d, p | Pick up, drop, put in container | `pickup()`, `drop()`, `put()` |
| Device Control | o, c, a, s | Open/close, activate/deactivate | `open()`, `close()`, `activate()` |
| Communication | t, r | Talk to characters, read objects | `talk()`, `read()` |
| Discovery | v | View discovery feed | Discovery feed access |
| Task Management | TAB | View current task | Task information API |

**Sources:** [README-USERSTUDY.md:140-158]()

The argument selection system uses number keys and bracket keys to specify interaction targets, mirroring the structured argument system used by AI agents when calling environment methods.

**Sources:** [README-USERSTUDY.md:142-143]()

---

