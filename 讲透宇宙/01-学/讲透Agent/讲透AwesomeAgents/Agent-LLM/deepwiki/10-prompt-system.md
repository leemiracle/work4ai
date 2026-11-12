<!-- source: DeepWiki mcp.deepwiki.com · repo Josh-XT/AGiXT · page 10 Prompt System · fetched 2026-10-26 -->

# Prompt System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agixt/Prompts.py](agixt/Prompts.py)
- [agixt/prompts/Default/Voice Chat without Commands.txt](agixt/prompts/Default/Voice Chat without Commands.txt)
- [agixt/prompts/Default/Voice Chat.txt](agixt/prompts/Default/Voice Chat.txt)

</details>



The Prompt System in AGiXT manages prompt templates, their formatting, categorization, and retrieval. It provides a mechanism for storing reusable prompt templates with dynamic argument substitution, enabling consistent interactions between agents and AI providers.

## Purpose and Scope

This document covers:
- How prompts are structured and stored
- The mechanism for dynamic argument substitution
- Prompt management operations (add, update, delete, retrieve)
- Multi-user support for prompts
- Integration with the broader AGiXT architecture

For information about how agents use these prompts to interact with AI providers, see [Agent System](#2.1).

## Prompt Structure

In AGiXT, prompts are text templates that contain placeholders enclosed in curly braces (`{}`). These placeholders are replaced with actual values at runtime.

### Example Prompt Template

Below is a simplified example of a prompt template:

```
## Context 
{context} 

Today's date is {date}.

## System
You are {agent_name}, an expert at assisting users.

User's latest input: {user_input} 
```

In this example, `{context}`, `{date}`, `{agent_name}`, and `{user_input}` are arguments that will be replaced with actual values when the prompt is used.

Sources: [agixt/prompts/Default/Voice Chat.txt:1-15](), [agixt/prompts/Default/Voice Chat without Commands.txt:1-15]()

## Prompt System Architecture

The diagram below illustrates the core components of the Prompt System and their relationships:

```mermaid
classDiagram
    class Prompts {
        +user: string
        +user_id: int
        +add_prompt()
        +get_prompt()
        +update_prompt()
        +delete_prompt()
        +rename_prompt()
        +get_prompts()
        +get_prompt_args()
        +get_prompt_categories()
    }
    
    class "Prompt" {
        +id: int
        +name: string
        +description: string
        +content: string
        +prompt_category_id: int
        +user_id: int
    }
    
    class "PromptCategory" {
        +id: int
        +name: string
        +description: string
        +user_id: int
    }
    
    class "Argument" {
        +id: int
        +prompt_id: int
        +name: string
    }
    
    Prompts --> "Prompt" : manages
    Prompts --> "PromptCategory" : organizes
    "Prompt" --> "PromptCategory" : belongs to
    "Prompt" --> "Argument" : has
```

Sources: [agixt/Prompts.py:7-356]()

## Integration with AGiXT

The diagram below shows how the Prompt System integrates with the broader AGiXT architecture:

```mermaid
flowchart TD
    subgraph "User Interaction"
        "User"((User)) -->|"provides input"| "Interactions"["Interactions Class"]
    end
    
    subgraph "Prompt Processing"
        "Interactions" -->|"requests prompt"| "Prompts"["Prompts Class"]
        "Prompts" -->|"returns template"| "Interactions"
        "Interactions" -->|"extracts placeholders"| "PromptArgs"["get_prompt_args()"]
        "Interactions" -->|"substitutes arguments"| "FormattedPrompt"["Formatted Prompt"]
    end
    
    subgraph "AI Interaction"
        "FormattedPrompt" -->|"sent to"| "Agent"["Agent Class"]
        "Agent" -->|"communicates with"| "AIProvider"["AI Provider"]
        "AIProvider" -->|"generates response"| "Agent"
        "Agent" -->|"returns response"| "Interactions"
    end
    
    "Interactions" -->|"presents to"| "User"
```

Sources: [agixt/Prompts.py:7-356]()

## Prompt Resolution Process

When a prompt is requested, the system follows a specific resolution path to find and return the appropriate prompt:

```mermaid
flowchart TD
    "Start"[("Prompt Request")] --> "User"{"Check User's Prompts"}
    "User" -->|"Found"| "Return"[("Return Prompt")]
    "User" -->|"Not Found"| "Default"{"Check Default Category"}
    "Default" -->|"Found"| "Return"
    "Default" -->|"Not Found"| "Global"{"Check Global Prompts"}
    "Global" -->|"Found"| "Return" 
    "Global" -->|"Not Found"| "File"{"Check File System"}
    "File" -->|"Found"| "Save"["Save to Database"]
    "File" -->|"Not Found"| "NotFound"[("Return None")]
    "Save" --> "Return"
```

Sources: [agixt/Prompts.py:53-131]()

## Prompt Management Operations

The Prompts class provides several methods for managing prompts:

| Method | Description |
|--------|-------------|
| `add_prompt(prompt_name, prompt, prompt_category)` | Adds a new prompt to the database |
| `get_prompt(prompt_name, prompt_category)` | Retrieves a prompt by name and category |
| `update_prompt(prompt_name, prompt, prompt_category)` | Updates an existing prompt |
| `delete_prompt(prompt_name, prompt_category)` | Removes a prompt |
| `rename_prompt(prompt_name, new_prompt_name, prompt_category)` | Changes a prompt's name |
| `get_prompts(prompt_category)` | Lists all prompts in a category |
| `get_prompt_categories()` | Lists all available prompt categories |
| `get_prompt_args(prompt_text)` | Extracts argument placeholders from prompt text |

Sources: [agixt/Prompts.py:12-356]()

## Argument Extraction

The `get_prompt_args` method extracts arguments from prompt templates by identifying text enclosed in curly braces:

```mermaid
flowchart LR
    "Start"["Prompt Text"] --> "FindStart"["Find First '{'"]
    "FindStart" --> "StartFound"{"Found?"}
    "StartFound" -->|"Yes"| "FindEnd"["Find Matching '}'"]
    "StartFound" -->|"No"| "End"["Return Arguments"]
    "FindEnd" --> "EndFound"{"Found?"}
    "EndFound" -->|"Yes"| "Extract"["Extract Argument"]
    "EndFound" -->|"No"| "End"
    "Extract" --> "AddArg"["Add to Arguments List"]
    "AddArg" --> "FindStart"
```

Sources: [agixt/Prompts.py:230-240]()

## Multi-user Support

The Prompt System supports multiple users with the following features:

1. **User-specific prompts**: Each user has their own set of prompts
2. **Global prompts**: Prompts defined by the default user are available to all users
3. **Priority**: User-specific prompts take precedence over global prompts

```mermaid
graph TD
    subgraph "User Space to Code Entity Mapping"
        "UserA"["User A"] -->|"creates"| "UserAPrompts"["User A's Prompts"]
        "DefaultUser"["DEFAULT_USER"] -->|"creates"| "GlobalPrompts"["Global Prompts"]
        
        "UserAPrompts" -->|"stored as"| "DB_Prompt_UserA"["DB.Prompt(user_id=User A)"]
        "GlobalPrompts" -->|"stored as"| "DB_Prompt_Default"["DB.Prompt(user_id=DEFAULT_USER)"]
        
        "get_user_prompts()"["get_user_prompts() Method"] -->|"retrieves"| "DB_Prompt_UserA"
        "get_global_prompts()"["get_global_prompts() Method"] -->|"retrieves"| "DB_Prompt_Default"
        
        "UserA" -->|"initializes"| "PromptsClass"["Prompts(user='User A')"]
        "PromptsClass" -->|"calls"| "get_user_prompts()"
        "PromptsClass" -->|"calls"| "get_global_prompts()"
    end
```

Sources: [agixt/Prompts.py:8-11](), [agixt/Prompts.py:133-195]()

## File System Fallback

If a prompt is not found in the database, the system checks for prompt files in the `prompts/Default/` directory:

1. The system looks for a file named `{prompt_name}.txt` in the `prompts/Default/` directory
2. If found, it reads the file content and adds it to the database
3. The newly added prompt is then returned to the requester

This mechanism enables a hybrid approach where prompts can be defined in files for easier version control and distribution, while still benefiting from database storage for runtime operations.

Sources: [agixt/Prompts.py:97-125]()

## Technical Implementation Details

The Prompt System is implemented in the `Prompts` class in `agixt/Prompts.py` and relies on the following database models:

- `Prompt`: Stores the prompt content and metadata
- `PromptCategory`: Organizes prompts into categories
- `Argument`: Tracks arguments/placeholders in prompts
- `User`: Associates prompts with specific users

When a prompt is added or updated, the system automatically extracts and saves its arguments, allowing for efficient tracking of what placeholders a prompt contains.

Sources: [agixt/Prompts.py:1-6](), [agixt/Prompts.py:42-50](), [agixt/Prompts.py:294-312]()

---

