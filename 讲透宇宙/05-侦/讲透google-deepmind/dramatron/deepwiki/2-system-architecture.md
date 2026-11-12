<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/dramatron · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [colab/dramatron.ipynb](colab/dramatron.ipynb)
- [docs/details.html](docs/details.html)
- [dramatron-animation.gif](dramatron-animation.gif)

</details>



This document provides a comprehensive overview of Dramatron's system architecture, focusing on the core components, their relationships, and the hierarchical generation process. For specific usage instructions, please refer to the [User Guide](#3).

## Purpose and Scope

The Dramatron system is designed as a co-writing tool that leverages large language models (LLMs) to generate theatrical scripts and screenplays. Its architecture facilitates a hierarchical generation approach to maintain consistency across the entire script, while enabling collaborative interaction between human writers and the system. This document explains the technical design and implementation of the system components.

Sources: [colab/dramatron.ipynb:41-59](), [README.md:12-25]()

## System Overview

Dramatron follows a hierarchical generation approach to create consistent scripts. The system is built around a central orchestrator (`StoryGenerator`) that coordinates the generation process through an abstraction layer (`LanguageAPI`) to interact with language models. The generated content is structured into typed data objects which are ultimately rendered into a screenplay in Fountain format.

```mermaid
graph TD
    User(["Human Writer"]) <--> SG["StoryGenerator"]
    SG <--> LA["LanguageAPI"]
    LA <--> LLM["Large Language Model"]
    SG --> Story["Story Object"]
    Story --> Renderer["render_story()"]
    Renderer --> Script["Fountain Format Script"]
    
    subgraph "Core Components"
        SG
        LA
        Story
        Renderer
    end
    
    subgraph "External Services"
        LLM
        FilterAPI["FilterAPI/Perspective API\n(Optional)"]
    end
    
    LA -.-> FilterAPI
```

Sources: [colab/dramatron.ipynb:983-1057](), [colab/dramatron.ipynb:561-622](), [colab/dramatron.ipynb:437-499]()

## Hierarchical Generation Process

The hierarchical generation approach ensures that each element of the script builds upon previously generated content, maintaining consistency throughout the script.

```mermaid
flowchart TD
    Storyline(["User Storyline"]) --> |"generate_title()"| Title["Title"]
    Storyline --> |"generate_characters()"| Characters["Characters"]
    Storyline & Characters --> |"generate_scenes()"| Scenes["Scenes"]
    Scenes --> |"generate_place_descriptions()"| Places["Places"]
    Storyline & Characters & Scenes & Places --> |"generate_dialog()"| Dialogs["Dialogs"]
    
    Title & Characters & Scenes & Places & Dialogs --> |"get_story()"| Story["Story Object"]
    Story --> |"render_story()"| Script["Fountain Format Script"]
```

Each step in the generation process:
1. Takes inputs from previous stages
2. Constructs a specialized prompt
3. Calls the language model via the LanguageAPI
4. Parses the generated text into appropriate data structures

The StoryGenerator orchestrates this process, allowing the user to intervene at each step to guide the generation.

Sources: [colab/dramatron.ipynb:724-902](), [colab/dramatron.ipynb:1178-1218]()

## Core Components

### StoryGenerator Class

The StoryGenerator class serves as the central orchestrator in Dramatron. It manages the state of the script generation process and provides methods for stepping through the generation process, rewriting elements, and obtaining the final story.

```mermaid
classDiagram
    class StoryGenerator {
        +storyline: str
        +prefixes: Dict[str, str]
        +client: LanguageAPI
        +filter: FilterAPI
        +title: Title
        +characters: Characters
        +scenes: Scenes
        +places: Dict[str, Place]
        +dialogs: List[str]
        +step(level, seed, idx)
        +rewrite(text, level, entity)
        +complete(level, seed, entity, sample_length)
        +get_story()
    }
    
    class Story {
        +storyline: str
        +title: str
        +character_descriptions: Dict[str, str]
        +place_descriptions: Dict[str, Place]
        +scenes: Scenes
        +dialogs: List[str]
    }
    
    StoryGenerator --> Story: produces
```

Sources: [colab/dramatron.ipynb:983-1057](), [colab/dramatron.ipynb:1178-1218](), [colab/dramatron.ipynb:386-406]()

### LanguageAPI Interface

The LanguageAPI class provides an abstraction layer for interacting with language models. It defines a common interface that can be implemented by different language model providers.

```mermaid
classDiagram
    class LanguageAPI {
        +sample_length: int
        +model: str
        +config_sampling: dict
        +seed: int
        +sample(prompt, sample_length, seed, num_samples)
    }
    
    class CustomLanguageAPI {
        +client
        +sample(prompt, sample_length, seed, num_samples)
    }
    
    class LanguageResponse {
        +prompt: str
        +prompt_length: int
        +text: str
        +text_length: int
    }
    
    LanguageAPI <|-- CustomLanguageAPI: implements
    LanguageAPI --> LanguageResponse: returns
```

The LanguageAPI abstraction allows Dramatron to be model-agnostic, enabling users to plug in different language models by implementing the required sample method.

Sources: [colab/dramatron.ipynb:561-622](), [colab/dramatron.ipynb:554-559]()

### Script Data Structures

Dramatron uses a set of structured data types to represent the elements of a script. These are implemented as NamedTuples for type safety and clarity.

| Data Structure | Purpose | Key Properties |
|----------------|---------|----------------|
| Title | Script title | title: str |
| Character | Individual character | name: str, description: str |
| Characters | Collection of characters | character_descriptions: Dict[str, str] |
| Scene | Individual scene | place: str, plot_element: str, beat: str |
| Scenes | Collection of scenes | scenes: List[Scene] |
| Place | Location description | name: str, description: str |
| Story | Complete script | storyline, title, character_descriptions, place_descriptions, scenes, dialogs |

These data structures include methods for serialization (to_string) and deserialization (from_string) to facilitate conversion between text and structured objects.

Sources: [colab/dramatron.ipynb:217-406]()

### Generation Functions

Dramatron includes specialized functions for generating each element of a script:

```mermaid
flowchart LR
    subgraph "Generation Functions"
        direction TB
        gt["generate_title()"]
        gc["generate_characters()"]
        gs["generate_scenes()"]
        gp["generate_place_descriptions()"]
        gd["generate_dialog()"]
    end
    
    subgraph "Text Generation"
        direction TB
        gen["generate_text()"]
        gnl["generate_text_no_loop()"]
    end
    
    gt --> gnl
    gc --> gen
    gs --> gen
    gp --> gen
    gd --> gen
    
    gnl --> LA["LanguageAPI.sample()"]
    gen --> LA
```

Each generation function:
1. Constructs a prompt using predefined templates and existing content
2. Calls `generate_text()` or `generate_text_no_loop()` to obtain text from the language model
3. Parses the generated text into the appropriate data structure
4. Returns the parsed object and the prompt used

The functions handle issues like repetition detection and content filtering to ensure quality output.

Sources: [colab/dramatron.ipynb:637-719](), [colab/dramatron.ipynb:724-902]()

### Rendering Function

The `render_story()` function transforms a Story object into a Fountain format script suitable for screenplay writing. It:

1. Formats the title and metadata
2. Lists character descriptions
3. Details each scene with location, characters, and dialog
4. Applies appropriate formatting according to the Fountain syntax

Sources: [colab/dramatron.ipynb:437-499]()

## User Interaction Flow

Dramatron is designed for collaborative use with a human writer, following this interaction flow:

```mermaid
sequenceDiagram
    participant Writer as "Human Writer"
    participant SG as "StoryGenerator"
    participant LLM as "Language Model"
    
    Writer->>SG: Provide storyline
    
    loop For each level
        Writer->>SG: step(level)
        SG->>LLM: Generate content
        LLM-->>SG: Return generated text
        SG-->>Writer: Present generated element
        
        alt Writer wants changes
            Writer->>SG: rewrite(text, level)
            SG->>LLM: Regenerate content
            LLM-->>SG: Return new text
            SG-->>Writer: Present updated element
        end
    end
    
    Writer->>SG: get_story()
    SG-->>Writer: Return complete Story object
    Writer->>Writer: Edit and finalize script
```

This interaction model supports the co-writing process, allowing the human writer to guide the generation while leveraging the capabilities of the language model.

Sources: [colab/dramatron.ipynb:1178-1302](), [docs/details.html:30-51]()

## Implementation Environment

Dramatron is implemented in Python and runs within a Google Colab notebook environment. This implementation choice provides:

1. Accessibility - users can run Dramatron without local installation
2. Integration with language model APIs
3. Interactive interface for the co-writing process

The system is designed to be "unplugged" from any specific language model, requiring users to implement the LanguageAPI interface to connect with their preferred model.

Sources: [README.md:7-8](), [colab/dramatron.ipynb:1-67]()

## Limitations and Considerations

The Dramatron architecture has several inherent limitations:

1. **Hierarchical Generation** - The top-down approach may not align with all writing processes
2. **Prompt Engineering** - The quality of generated content depends on carefully designed prompts
3. **Content Safety** - Generated content may reproduce biases or contain inappropriate material
4. **Potential Plagiarism** - Language models may reproduce content from their training data

Dramatron includes optional integration with the Perspective API for content moderation and provides mechanisms for rewriting to address these limitations.

Sources: [README.md:17-23](), [docs/details.html:52-77]()

## Technology Stack

Dramatron's architecture is built on these key technologies:

| Component | Technologies |
|-----------|--------------|
| Core Implementation | Python, Named Tuples, Type Annotations |
| Runtime Environment | Google Colab Notebook |
| Language Model Integration | Custom API abstraction layer |
| Output Format | Fountain screenplay format |
| Optional Moderation | Perspective API |

The system is designed to be modular, allowing components to be replaced or extended as needed.

Sources: [colab/dramatron.ipynb:97-126](), [colab/dramatron.ipynb:561-622]()

---

