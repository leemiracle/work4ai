<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/generative-ai-with-javascript · page 1 Overview · fetched 2026-10-26 -->

# Overview

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



The Generative AI with JavaScript repository is a comprehensive educational resource that teaches JavaScript developers how to build applications with Generative AI capabilities. The repository follows a narrative-driven approach where learners progress through various lessons while experiencing a time-travel adventure interacting with historical figures via a companion application.

This document provides a technical overview of the repository structure, key components, and the relationships between them. For specific setup instructions, see [Setup and Configuration](#7).

## Repository Structure and Components

The repository is organized into several key directories that serve different purposes within the learning framework:

```mermaid
graph TD
    subgraph "generative-ai-with-javascript"
        Lessons["lessons/"]
        App["app/"]
        Docs["docs/"]
        Videos["videos/"]
    end
    
    Lessons --> Lesson1["01-intro-to-genai/"]
    Lessons --> Lesson2["02-first-ai-app/"]
    Lessons --> Lesson3["03-prompt-engineering/"]
    Lessons --> Lesson4["04-structured-output/"]
    Lessons --> Lesson5["05-rag/"]
    Lessons --> Lesson6["06-tool-calling/"]
    
    App --> AppJS["app.js (Express Server)"]
    App --> CharactersJSON["characters.json (Character Definitions)"]
    App --> PublicDir["public/ (Assets)"]
    
    Docs --> Setup["setup/"]
    Docs --> Images["images/"]
    
    Videos --> Slides["slides/"]
    Videos --> Demos["demos/"]
    Videos --> Sessions["sessions/"]
```

Sources: [README.md:15-16](), [README.md:82-93](), [app/README.md:1-5]()

Each lesson directory contains:
- README.md with lesson content
- assets/ folder with images
- solution/ directory with assignment solutions
- Some lessons contain example/ directories with code samples

The companion app serves as a practical demonstration of the concepts taught in the lessons, allowing learners to interact with AI-powered historical characters.

## Companion App Architecture

The companion app provides a chat interface for interacting with AI-simulated historical figures. Here's the technical flow of how the app processes user messages:

```mermaid
sequenceDiagram
    participant User as "Web Browser"
    participant Express as "app.js:POST/send"
    participant Characters as "characters.json"
    participant OpenAIClient as "OpenAI Client"
    participant AIModels as "GitHub Models API"
    
    User->>Express: POST /send {message: "user input"}
    Express->>Characters: Load character definition
    Note over Express,Characters: Character includes system message that defines personality
    Express->>OpenAIClient: Construct messages array
    Note over Express,OpenAIClient: messages = [{role: "system", content: "character description"}, {role: "user", content: "user input"}]
    OpenAIClient->>AIModels: chat.completions.create({model: "gpt-4o-mini", messages: messages})
    AIModels->>OpenAIClient: Return completion object
    OpenAIClient->>Express: Extract completion.choices[0].message.content
    Express->>User: JSON response {prompt: "user input", answer: "AI response"}
```

Sources: [lessons/01-intro-to-genai/README.md:189-225](), [app/README.md:1-14]()

The app uses GitHub Models API for generating text responses, which is accessed via the OpenAI client library. Character personalities are defined in the system message stored in `characters.json`.

## Learning Progression and Technical Concepts

The course follows a carefully designed learning progression, with each lesson building upon previous knowledge:

```mermaid
flowchart LR
    Start["Start Course"] --> Lesson1["1. Intro to GenAI"]
    Lesson1 --> Lesson2["2. First AI App"]
    Lesson2 --> Lesson3["3. Prompt Engineering"]
    Lesson3 --> Lesson4["4. Structured Output"]
    Lesson4 --> Lesson5["5. RAG"]
    Lesson5 --> Lesson6["6. Tool Calling"]
    
    Lesson1 --- Concept1["LLM Fundamentals"]
    Lesson2 --- Concept2["JavaScript AI Integration"]
    Lesson3 --- Concept3["Prompt Engineering Techniques"]
    Lesson4 --- Concept4["Structured Output Formats"]
    Lesson5 --- Concept5["External Data Integration"]
    Lesson6 --- Concept6["Function/Tool Calling"]
```

Sources: [README.md:82-93]()

### Key Technical Components

#### Retrieval-Augmented Generation (RAG) System

Lesson 5 introduces RAG, which enhances AI responses by incorporating external data sources. The implementation demonstrates the core components and data flow:

```mermaid
graph TD
    Question["question variable"] --> WordsExtract["words extraction (lines 234-238)"]
    WordsExtract --> MatchSearch["matches filtering (line 239)"]
    CSVData["hybrid.csv data"] --> MatchSearch
    MatchSearch --> TableFormatting["markdown table formatting (lines 242-245)"]
    TableFormatting --> AugmentedPrompt["augmentedPrompt construction (lines 253-264)"]
    Question --> AugmentedPrompt
    AugmentedPrompt --> OpenAIRequest["openai.chat.completions.create() (lines 274-278)"]
    OpenAIRequest --> AIResponse["AI-generated response"]
```

Sources: [lessons/05-rag/README.md:206-285]()

The RAG implementation demonstrates how to:
1. Extract keywords from user questions
2. Search external data sources (CSV file in this example)
3. Format the retrieved information
4. Augment the prompt with this information
5. Generate a more accurate and contextually relevant response

#### Character System Implementation

The character system controls how the AI responds, using system messages to define each character's personality:

```mermaid
graph TD
    CharactersJSON["characters.json"] --> CharacterDef["Character Definition"]
    CharacterDef --> SystemMsg["System Message (description property)"]
    CharacterDef --> CharMeta["Character Metadata (name, title, avatar)"]
    
    SystemMsg --> MessageArray["messages array construction"]
    UserInput["User Input"] --> MessageArray
    
    MessageArray --> OpenAIRequest["openai.chat.completions.create()"]
    OpenAIRequest --> AIResponse["Character-specific response"]
```

Sources: [app/README.md:22-24](), [lessons/01-intro-to-genai/README.md:189-225]()

## Narrative Integration with Technical Learning

The repository combines a narrative-driven approach with technical learning. Each lesson presents a story segment where the learner "time travels" to meet historical figures while learning specific AI concepts:

| Lesson | Historical Figure | Time Period | Technical Focus |
|--------|-------------------|------------|----------------|
| 1 | Dinocrates | Alexandria, 300 BC | Intro to GenAI |
| 2 | Leonardo da Vinci | Renaissance Florence | First AI App |
| 4 | Montezuma | Aztec Empire | Structured Output |
| 5 | Ada Lovelace | Victorian England | RAG |

Sources: [lessons/01-intro-to-genai/README.md:29-33](), [lessons/02-first-ai-app/README.md:25-33](), [lessons/04-structured-output/README.md:25-34](), [lessons/05-rag/README.md:24-32]()

## API Integration Architecture

The repository demonstrates how to integrate with AI models via API calls, primarily using the OpenAI client library to access GitHub Models:

```mermaid
graph TD
    AppJS["app.js"] --> OpenAIClient["OpenAI Client Initialization"]
    OpenAIClient --> OpenAIParams["Parameters Configuration"]
    OpenAIParams --> Model["model: 'gpt-4o-mini'"]
    OpenAIParams --> Messages["messages array with system & user content"]
    OpenAIParams --> Options["Optional parameters (temperature, max_tokens)"]
    Messages --> SystemMsg["system: Character personality"]
    Messages --> UserMsg["user: User input"]
    OpenAIParams --> APIRequest["API Request to GitHub Models"]
    APIRequest --> ResponseProcessing["Extract completion.choices[0].message.content"]
```

Sources: [lessons/01-intro-to-genai/README.md:189-225](), [lessons/02-first-ai-app/README.md:184-222]()

## JavaScript AI Workflow and Best Practices

The repository illustrates several core patterns for JavaScript AI development:

1. **System Message Configuration**: Using system messages to control AI behavior and create character personalities.
   
2. **Context Window Management**: Setting `max_tokens` parameter to control the length of generated responses.
   
3. **Temperature Setting**: Adjusting the `temperature` parameter to control the randomness/creativity of responses.
   
4. **Structured Output**: Techniques for requesting AI responses in specific formats (JSON, tables, etc.).
   
5. **Retrieval-Augmented Generation**: Enhancing AI responses with information from external sources.

Sources: [lessons/02-first-ai-app/README.md:335-352](), [lessons/02-first-ai-app/README.md:402-440](), [lessons/04-structured-output/README.md:220-238]()

These patterns and practices are demonstrated through practical examples in each lesson, making the repository a valuable resource for JavaScript developers looking to integrate Generative AI into their applications.

---

