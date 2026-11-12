<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/generative-ai-with-javascript · page 4 Lessons · fetched 2026-10-26 -->

# Lessons

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/README.md](app/README.md)
- [lessons/01-intro-to-genai/README.md](lessons/01-intro-to-genai/README.md)
- [lessons/02-first-ai-app/README.md](lessons/02-first-ai-app/README.md)
- [lessons/04-structured-output/README.md](lessons/04-structured-output/README.md)
- [lessons/05-rag/README.md](lessons/05-rag/README.md)

</details>



The Lessons section forms the core educational content of the "Generative AI with JavaScript" repository. This structured curriculum provides JavaScript developers with a progressive learning path for integrating Generative AI capabilities into their applications. The lessons guide learners from foundational concepts to advanced techniques through a combination of narrative storytelling, technical instruction, and practical assignments.

This page documents the overall structure, content, and implementation of the lessons system. For information about the companion app that demonstrates these concepts, see [Companion App](#3).

## Lesson Structure and Organization

Each lesson in the curriculum follows a consistent structure designed to facilitate learning through multiple modalities. Lessons build progressively on each other, introducing new concepts while reinforcing previous learning.

### Lesson Components

```mermaid
flowchart TD
    subgraph "Lesson Structure"
        Lesson["Individual Lesson"] --> Objectives["Learning Objectives"]
        Lesson --> Setup["Setup Instructions"]
        Lesson --> Resources["Related Resources"]
        Lesson --> Narrative["Narrative Element"]
        Lesson --> TechnicalContent["Technical Content"]
        Lesson --> Assignment["Practical Assignment"]
        Lesson --> Solution["Assignment Solution"]
        Lesson --> KnowledgeCheck["Knowledge Check Quiz"]
        Lesson --> SelfStudy["Self-Study Resources"]
        
        Resources --> Video["Short Video"]
        Resources --> Slides["Presentation Slides"]
        
        TechnicalContent --> Concepts["Concept Explanations"]
        TechnicalContent --> CodeExamples["Code Examples"]
        TechnicalContent --> CharacterInteraction["Character Interaction"]
        
        CharacterInteraction -.-> CompanionApp["Companion App"]
    end
```

Sources: [README.md:75-80](), [lessons/01-intro-to-genai/README.md:1-14](), [lessons/02-first-ai-app/README.md:1-14](), [lessons/04-structured-output/README.md:1-14](), [lessons/05-rag/README.md:1-14]()

As shown in the diagram, each lesson contains multiple components that work together to create a comprehensive learning experience:

| Component | Description |
|-----------|-------------|
| Learning Objectives | Clear statements of what learners will achieve by completing the lesson |
| Setup Instructions | Guidance for preparing the development environment |
| Related Resources | Links to videos and presentation slides that supplement the written content |
| Narrative Element | A continuing storyline that contextualizes the technical concepts |
| Technical Content | Explanations, code examples, and demonstrations of key concepts |
| Practical Assignment | Hands-on task to apply the lesson concepts |
| Assignment Solution | Reference implementation for the assignment |
| Knowledge Check Quiz | Questions to test understanding of key concepts |
| Self-Study Resources | Additional learning materials for further exploration |

Sources: [README.md:75-80]()

### Learning Progression

The lessons follow a carefully designed progression that introduces increasingly complex concepts while building on previous knowledge.

```mermaid
graph LR
    subgraph "Lesson Progression Flow"
        L1["Lesson 1: Intro to GenAI"]
        L2["Lesson 2: First AI App"]
        L3["Lesson 3: Prompt Engineering"]
        L4["Lesson 4: Structured Output"]
        L5["Lesson 5: RAG"]
        L6["Lesson 6: Tool Calling"]
        
        L1 -->|"Builds foundation"| L2
        L2 -->|"Applies concepts"| L3
        L3 -->|"Enhances outputs"| L4
        L4 -->|"Adds external data"| L5
        L5 -->|"Extends capabilities"| L6
    end
    
    subgraph "Key Concepts Covered"
        C1["LLM Fundamentals"]
        C2["Basic AI Integration"]
        C3["Advanced Prompting"]
        C4["Data Extraction & Formatting"]
        C5["External Data Integration"]
        C6["Custom Function Integration"]
    end
    
    L1 --- C1
    L2 --- C2
    L3 --- C3
    L4 --- C4
    L5 --- C5
    L6 --- C6
```

Sources: [README.md:82-94]()

## Individual Lessons Overview

The curriculum consists of six lessons, each focusing on specific aspects of Generative AI development with JavaScript:

### Lesson 1: Introduction to Generative AI and LLMs

This foundational lesson introduces the basic concepts of Generative AI and Large Language Models (LLMs). It covers:

- Basic concepts of Generative AI and LLMs
- Applications and limitations in JavaScript development
- Enhancing user experiences with AI
- Introduction to the narrative framework (time-traveling adventure)

Sources: [lessons/01-intro-to-genai/README.md:1-9]()

### Lesson 2: First AI App

This lesson guides learners through building their first AI application, covering:

- Setting up the development environment
- Writing a basic app with JavaScript and AI integration
- Understanding system prompts and their importance
- Creating chat applications with conversation context

Sources: [lessons/02-first-ai-app/README.md:1-12](), [lessons/02-first-ai-app/README.md:144-166]()

### Lesson 3: Prompt Engineering

This lesson focuses on techniques to improve AI outputs through effective prompting:

- Prompt engineering fundamentals
- Advanced techniques for controlling AI responses
- Meta-prompts for precision and accuracy
- Implementation of prompting strategies in JavaScript applications

Sources: [README.md:90]()

### Lesson 4: Structured Output

This lesson teaches how to work with structured data outputs from AI models:

- Extracting specific information from AI responses
- Formatting output in various structured formats (JSON, tables, etc.)
- Data extraction patterns and techniques
- Implementing structured output in practical applications

Sources: [lessons/04-structured-output/README.md:1-9](), [lessons/04-structured-output/README.md:148-223]()

### Lesson 5: Retrieval-Augmented Generation (RAG)

This lesson introduces the concept of RAG for enhancing AI with external data:

- Fundamentals of Retrieval-Augmented Generation
- Integrating external data sources with AI models
- Implementing retrieval components in JavaScript
- Augmenting prompts with retrieved information

Sources: [lessons/05-rag/README.md:1-9](), [lessons/05-rag/README.md:104-141]()

### Lesson 6: Tool Calling/Function Calling

This advanced lesson covers extending AI capabilities through custom functions:

- Implementing tool/function calling with LLMs
- Creating custom tools for AI models to use
- Integrating external capabilities into AI workflows
- Building advanced AI applications with extended functionality

Sources: [README.md:93]()

## Narrative Framework

The lessons utilize a unique narrative framework that follows a time-traveling adventure, where learners interact with historical figures through different time periods. This storytelling approach serves to contextualize technical concepts and make the learning experience more engaging.

```mermaid
flowchart LR
    subgraph "Narrative Timeline Flow"
        Start["London 1860s"]
        Alex["Alexandria 300 BC (Dinocrates)"]
        Florence["Florence 15th Century (Leonardo)"]
        Aztec["Aztec Empire (Montezuma)"]
        Victorian["Victorian Era (Ada Lovelace)"]
        
        Start -->|"Time Travel"| Alex
        Alex -->|"Time Travel"| Florence
        Florence -->|"Time Travel"| Aztec
        Aztec -->|"Time Travel"| Victorian
    end
    
    subgraph "Technical Concepts Mapping"
        Alex --- Intro["Intro to GenAI"]
        Florence --- FirstApp["First AI App"]
        Aztec --- StructuredOutput["Structured Output"]
        Victorian --- RAG["Retrieval-Augmented Generation"]
    end
    
    subgraph "Character Interaction"
        CharApp["characters.json Configuration"]
        AIModels["AI Models (GitHub/OpenAI)"]
        
        Alex & Florence & Aztec & Victorian --- CharApp
        CharApp --- AIModels
    end
```

Sources: [lessons/01-intro-to-genai/README.md:29-158](), [lessons/02-first-ai-app/README.md:25-118](), [lessons/04-structured-output/README.md:25-123](), [lessons/05-rag/README.md:23-76]()

The narrative serves multiple purposes:
1. Contextualizes technical concepts within historical periods
2. Provides engaging scenarios for applying AI concepts
3. Demonstrates the companion app's character interaction capabilities
4. Creates memorable learning experiences through storytelling

Each historical period and character is associated with specific AI concepts that are explored in the corresponding lesson.

## Technical Implementation

### Code Examples and Assignments

Each lesson contains practical code examples that demonstrate key concepts, followed by assignments that allow learners to apply what they've learned. The code examples typically follow this pattern:

```mermaid
flowchart TD
    subgraph "Code Example Pattern"
        Input["1. Define Input/Question"] --> 
        Prompt["2. Construct AI Prompt"] -->
        Client["3. Create AI Client"] -->
        Request["4. Send Request to AI API"] -->
        Response["5. Process Response"] -->
        Output["6. Display/Use Output"]
    end
    
    subgraph "Technologies Used"
        OpenAI["OpenAI SDK"]
        GitHubModels["GitHub Models"]
        Environment["Environment Variables"]
        Formatting["Formatting Utilities"]
        
        Client --- OpenAI
        Client --- GitHubModels
        Client --- Environment
        Prompt & Response --- Formatting
    end
```

Sources: [lessons/02-first-ai-app/README.md:184-223](), [lessons/01-intro-to-genai/README.md:189-235](), [lessons/05-rag/README.md:206-286]()

Key implementation patterns include:

1. **API Integration**: Using the OpenAI SDK to communicate with AI models
2. **Prompt Construction**: Building effective prompts with appropriate context
3. **Response Handling**: Processing and extracting useful information from AI responses
4. **Error Handling**: Implementing proper error handling for API calls
5. **Configuration Management**: Using environment variables for API keys and other settings

Sources: [lessons/02-first-ai-app/README.md:184-223](), [lessons/01-intro-to-genai/README.md:189-235]()

### Character Interaction System

The companion app allows learners to interact with AI-powered historical characters, demonstrating the concepts taught in the lessons. The app uses a system of character definitions and AI integration to create interactive conversations.

```mermaid
flowchart TD
    subgraph "Character Interaction System"
        UserInput["User Input"] --> 
        AppJS["app.js Express Server"] -->
        PromptConstruction["Prompt Construction"]
        
        CharactersJSON["characters.json"] --> PromptConstruction
        
        PromptConstruction --> 
        AIClient["OpenAI/GitHub Client"] -->
        AIModel["AI Model API"]
        
        AIModel --> AIClient --> AppJS --> UserInterface["User Interface"]
        
        subgraph "Character Configuration"
            CharactersJSON --> CharDef["Character Definition"]
            CharDef --> Title["Title"]
            CharDef --> Name["Name"]
            CharDef --> SysMsg["System Message (Prompt)"]
            CharDef --> Images["Image & Avatar"]
        end
    end
```

Sources: [app/README.md:1-29](), [lessons/01-intro-to-genai/README.md:189-235]()

The character interaction system demonstrates several key concepts:

1. **Character Configuration**: Each historical character is defined in the `characters.json` file with a name, description (system message), and visual assets
2. **System Messages**: Special prompts that define a character's personality and knowledge
3. **API Integration**: Connection to AI models through GitHub Models or OpenAI
4. **Conversation Context**: Maintaining context between user messages for coherent interactions

This system serves as both a practical demonstration of the concepts and an engaging way for learners to interact with the course material.

Sources: [app/README.md:19-25](), [lessons/01-intro-to-genai/README.md:160-182]()

## Development Resources

Each lesson includes self-study resources and links to additional materials that help learners deepen their understanding of the concepts covered. These resources typically include:

- Documentation links
- GitHub repositories with sample code
- Video tutorials
- Additional reading materials
- Related workshops and courses

The lessons are designed to be modular and self-contained, but they also provide pathways to more advanced topics and practical applications.

Sources: [lessons/02-first-ai-app/README.md:505-512](), [lessons/05-rag/README.md:346-351]()

## Summary

The Lessons system provides a comprehensive, structured approach to learning Generative AI with JavaScript, combining narrative storytelling, technical instruction, and practical assignments. Through six progressive lessons, learners gain the knowledge and skills needed to integrate AI capabilities into their JavaScript applications, from basic concepts to advanced techniques like RAG and function calling.

The combination of written content, video resources, character interactions, and practical assignments creates a multi-modal learning experience that accommodates different learning styles and reinforces key concepts through repetition and application.

Sources: [README.md:82-94](), [README.md:75-80]()

---

