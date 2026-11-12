<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/generative-ai-with-javascript · page 2 Course Structure · fetched 2026-10-26 -->

# Course Structure

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



This page provides a comprehensive overview of how the Generative AI with JavaScript course is organized, the progression of lessons, and the learning objectives. It details the structure of course materials, learning paths, and how different components contribute to the overall learning experience. For information about the companion application that demonstrates these concepts, see [Companion App](#3).

## Overview of Course Organization

The Generative AI with JavaScript course is structured as a series of progressive lessons, each building on concepts from previous lessons. The curriculum follows a time-traveling narrative that combines technical learning with an engaging storyline, allowing learners to interact with historical figures while building practical AI skills.

```mermaid
flowchart TB
    subgraph "Course Structure"
        Lessons["Lessons (6)"] --> Components["Lesson Components"]
        Components --> WrittenContent["Written Content"]
        Components --> Assignments["Practical Assignments"]
        Components --> Solutions["Assignment Solutions"]
        Components --> Quizzes["Knowledge Check Quizzes"]
        Components --> Translations["Translations Directory"]
        
        App["Companion App"] --> Characters["Character Interactions"]
        
        Videos["Additional Video Series"] --> VideoContent["10 Topic-Specific Videos"]
    end
    
    Lessons --> LearningPathway["Progressive Learning Pathway"]
    App --> LearningPathway
    
    class Lessons,App,Videos,LearningPathway emphasis
```

Sources: [README.md:82-93](), [README.md:74-81]()

## Lesson Content Structure

Each lesson in the course follows a consistent structure, combining narrative elements with technical content, practical exercises, and knowledge verification. This structure ensures that learners can build skills methodically while remaining engaged through the storyline.

### Standard Lesson Components

Each lesson is organized with the following components:

| Component | Purpose | Location |
|-----------|---------|----------|
| Written Lesson | Primary instructional content with narrative | `/lessons/[lesson-number]/README.md` |
| Assignments | Practical exercises to apply concepts | Within lesson README.md |
| Solutions | Complete solutions to assignments | `/lessons/[lesson-number]/solution/` |
| Knowledge Checks | Quiz questions to verify understanding | End of lesson README.md |
| Quiz Solutions | Answers to knowledge check questions | `/lessons/[lesson-number]/solution/solution-quiz.md` |
| Character Integration | Interactive demonstrations through the companion app | Referenced in lesson content |
| Translations | Multilingual versions of content | `/lessons/[lesson-number]/translations/` |

```mermaid
flowchart TB
    subgraph "Lesson Structure"
        LessonReadme["Lesson README.md"] --> Narrative["Time-Travel Narrative"]
        LessonReadme --> Concepts["Technical Concepts"]
        LessonReadme --> CodeExamples["Code Examples"]
        LessonReadme --> PracticalAssignments["Practical Assignments"]
        LessonReadme --> KnowledgeCheck["Knowledge Check Quiz"]
    end
    
    subgraph "Supporting Materials"
        Solutions["Solution Files"] --> AssignmentSolutions["Assignment Solutions"]
        Solutions --> QuizSolutions["Quiz Solutions"]
        Assets["Asset Files"] --> Images["Images"]
        Assets --> CodeFiles["Supplementary Code"]
    end
    
    LessonReadme -.-> CompanionApp["Companion App Integration"]
    PracticalAssignments --> Solutions
    KnowledgeCheck --> QuizSolutions
```

Sources: [lessons/01-intro-to-genai/README.md:1-27](), [lessons/02-first-ai-app/README.md:1-27](), [README.md:74-81]()

## Curriculum Progression

The course curriculum follows a logical progression, starting with foundational concepts and gradually advancing to more complex applications of Generative AI with JavaScript.

### Lesson Sequence and Learning Objectives

```mermaid
flowchart LR
    Start["Start Course"] --> Lesson1
    
    subgraph "Learning Pathway"
        Lesson1["1. Intro to GenAI"] --> Lesson2["2. First AI App"]
        Lesson2 --> Lesson3["3. Prompt Engineering"]
        Lesson3 --> Lesson4["4. Structured Output"]
        Lesson4 --> Lesson5["5. RAG"]
        Lesson5 --> Lesson6["6. Tool Calling"]
    end
    
    Lesson1 --- Concepts1["LLM Basics and<br>Generative AI Foundations"]
    Lesson2 --- Concepts2["Environment Setup<br>Basic App Creation<br>System Prompts"]
    Lesson3 --- Concepts3["Prompt Design<br>Advanced Techniques<br>Meta-prompts"]
    Lesson4 --- Concepts4["Structured Data<br>Formats (JSON, etc.)<br>Data Extraction"]
    Lesson5 --- Concepts5["External Data Integration<br>Augmented Responses"]
    Lesson6 --- Concepts6["Function/Tool Calling<br>Extended Capabilities"]
```

Sources: [README.md:84-93]()

Here's a detailed breakdown of each lesson's focus and learning objectives:

| Lesson | Title | Core Learning Objectives | Key Technical Components |
|--------|-------|--------------------------|--------------------------|
| 1 | Introduction to Generative AI and LLMs | Understand GenAI fundamentals, applications and limitations | Generative AI concepts, LLM basics, JavaScript integration |
| 2 | First AI App | Set up development environment, create basic app, understand system prompts | Environment setup, API integration, system messages |
| 3 | Prompt Engineering | Learn techniques to craft effective prompts, understand meta-prompts | Advanced prompting, techniques to control AI outputs |
| 4 | Structured Output | Generate formatted output, extract data from prompts | JSON/XML formatting, data extraction, structured responses |
| 5 | RAG (Retrieval Augmented Generation) | Integrate external data sources, improve relevance and accuracy | Data retrieval, context augmentation, source integration |
| 6 | Tool Calling/Function Calling | Extend LLM capabilities with custom functions | Function integration, tool calling patterns, capability extension |

Sources: [lessons/01-intro-to-genai/README.md:1-7](), [lessons/02-first-ai-app/README.md:1-7](), [lessons/04-structured-output/README.md:1-7](), [lessons/05-rag/README.md:1-7](), [README.md:84-93]()

## Narrative Framework

A unique aspect of this course is its immersive narrative framework, which uses a time-traveling storyline to engage learners. This framework integrates technical learning with interactions with historical figures, providing context and engagement.

```mermaid
flowchart TB
    subgraph "Time Travel Narrative"
        TimeBeetle["Time Beetle Device"] --> TimeTravel["Time Travel<br>Framework"]
        
        TimeTravel --> Location1["Alexandria 300 BC<br>(Dinocrates)"]
        TimeTravel --> Location2["Florence 15th Century<br>(Leonardo da Vinci)"]
        TimeTravel --> Location3["Aztec Empire<br>(Montezuma)"]
        TimeTravel --> Location4["19th Century England<br>(Ada Lovelace)"]
        
        Location1 --> Lesson1["Lesson 1:<br>Intro to GenAI"]
        Location2 --> Lesson2["Lesson 2:<br>First AI App"]
        Location3 --> Lesson4["Lesson 4:<br>Structured Output"]
        Location4 --> Lesson5["Lesson 5:<br>RAG"]
    end
    
    subgraph "Character System Integration"
        CharactersJSON["characters.json"] --> HistoricalFigures["Historical Figure<br>Definitions"]
        HistoricalFigures --> SystemPrompts["Character-Specific<br>System Prompts"]
        SystemPrompts --> AIResponses["AI-Generated<br>Character Responses"]
    end
    
    TimeTravel -.-> CharactersJSON
```

Sources: [lessons/01-intro-to-genai/README.md:29-159](), [lessons/02-first-ai-app/README.md:23-117](), [lessons/04-structured-output/README.md:25-122](), [lessons/05-rag/README.md:23-79](), [app/README.md:1-29]()

The narrative follows a mechanic from 1860s London who travels through time using a device called the "Time Beetle." This journey connects with each lesson's technical content, providing a cohesive learning experience. The companion app allows learners to interact with these historical characters, reinforcing concepts through practical application.

## Companion App Integration

The course includes a companion application that allows learners to interact with historical characters using the Generative AI technologies taught in the lessons. This integration provides a practical demonstration of the concepts and enhances the learning experience.

```mermaid
flowchart TB
    subgraph "User Interaction"
        User["Learner"] --> AppInterface["Companion App Interface"]
        AppInterface --> CharacterSelection["Character Selection"]
        AppInterface --> MessageInput["Message Input"]
        AppInterface --> AIResponse["AI-Generated Response"]
    end
    
    subgraph "Backend Processing"
        MessageInput --> AppJS["app.js ExpressServer"]
        CharacterSelection --> CharactersJSON["characters.json"]
        CharactersJSON --> SystemMessage["Character System Message"]
        
        AppJS --> AIRequest["API Request"]
        SystemMessage --> AIRequest
        
        AIRequest --> AIModel["AI Model (GPT-4o-mini)"]
        AIModel --> ProcessedResponse["Processed Response"]
        ProcessedResponse --> AIResponse
    end
    
    class AppJS,CharactersJSON,AIModel emphasis
```

Sources: [app/README.md:1-29](), [lessons/01-intro-to-genai/README.md:160-235]()

The companion app utilizes a character system defined in `characters.json`, where each historical figure has a specific system message that shapes their responses. The app demonstrates practical implementation of the AI concepts taught in the lessons, providing an engaging way for learners to experiment with the technology.

## Code Examples and Assignments

Throughout the course, code examples and practical assignments reinforce learning objectives. These components progress in complexity, building upon previously learned concepts.

### Code Example Progression

```mermaid
graph TB
    subgraph "Code Examples Progression"
        Basic["Basic Text Generation<br>Simple API Calls"] --> Chat["Chat Conversation<br>System Messages"]
        Chat --> StructuredOutput["Structured Output<br>JSON Formatting"]
        StructuredOutput --> RAG["Retrieval Augmented<br>Generation"]
        RAG --> ToolCalling["Tool/Function<br>Calling"]
    end
    
    Basic --> OpenAIClient["OpenAI Client<br>Setup"]
    Basic --> SimplePrompt["Simple Prompt<br>Construction"]
    
    Chat --> MessageArray["Message Array<br>Construction"]
    Chat --> SystemRole["System Role<br>Definition"]
    
    StructuredOutput --> OutputTemplate["Output Template<br>Definition"]
    StructuredOutput --> JSONFormat["JSON Response<br>Handling"]
    
    RAG --> DataRetrieval["Data Retrieval<br>Component"]
    RAG --> PromptAugmentation["Prompt<br>Augmentation"]
    
    ToolCalling --> FunctionDefinition["Function<br>Definition"]
    ToolCalling --> ParameterExtraction["Parameter<br>Extraction"]
```

Sources: [lessons/02-first-ai-app/README.md:180-360](), [lessons/04-structured-output/README.md:170-300](), [lessons/05-rag/README.md:205-285]()

### Assignment Structure

Each lesson includes practical assignments that challenge learners to apply the concepts they've learned. Assignments are designed to build upon previously learned skills while introducing new concepts.

| Lesson | Assignment Focus | Skills Applied | Integration with Narrative |
|--------|------------------|----------------|----------------------------|
| 1 | Using LLMs for research | Basic prompt construction | Helping Dinocrates build a lighthouse |
| 2 | Building an engineering assistant | System messages, response generation | Assisting Leonardo with aerial screw calculations |
| 4 | Creating encoded structured output | Output formatting, data transformation | Repairing Leonardo's aerial screw |
| 5 | Implementing RAG with Wikipedia | External data integration, context augmentation | Helping Ada Lovelace improve the Time Beetle |

Sources: [lessons/01-intro-to-genai/README.md:322-337](), [lessons/02-first-ai-app/README.md:446-486](), [lessons/04-structured-output/README.md:513-536](), [lessons/05-rag/README.md:305-329]()

## Multilingual Support

The course is designed with global accessibility in mind, featuring a translation system that provides content in multiple languages.

```mermaid
flowchart LR
    subgraph "Multilingual Support System"
        OriginalContent["Original English Content<br>README.md"] --> TranslationsDir["translations/ Directory"]
        
        TranslationsDir --> PTBRFile["README.pt-br.md<br>Portuguese"]
        TranslationsDir --> ZHCNFile["README.zh-cn.md<br>Chinese"]
        TranslationsDir --> BNFile["README.bn.md<br>Bengali"]
        TranslationsDir --> ESFile["README.es.md<br>Spanish"]
        
        ContributionSystem["Translation Contribution<br>Process"] --> NewTranslations["New Language<br>Translations"]
        NewTranslations --> TranslationsDir
    end
```

Sources: [README.md:33-35]()

Each lesson includes a `translations/` directory where multilingual versions of the content are stored. The current supported languages include Portuguese, Chinese, Bengali, and Spanish, with an open invitation for community contributions to expand language support.

## Additional Learning Resources

Beyond the core lessons, the course provides additional resources to support learners, including a complementary video series and links to related courses.

```mermaid
flowchart TB
    subgraph "Additional Learning Resources"
        VideoSeries["Video Series"] --> IntroVideo["Series Introduction"]
        VideoSeries --> LLMBasics["LLM Fundamentals"]
        VideoSeries --> PromptEngineering["Prompt Engineering"]
        VideoSeries --> RAGVideo["RAG Implementation"]
        VideoSeries --> LangChainJS["LangChain.js"]
        VideoSeries --> LocalModels["Local AI Models"]
        VideoSeries --> Playground["Phi-3 Playground"]
        VideoSeries --> AIFoundry["Azure AI Foundry"]
        VideoSeries --> CosmosDB["Cosmos DB Integration"]
        VideoSeries --> AzureTools["Azure Hosting Tools"]
        
        RelatedCourses["Related Courses"] --> GenAIBeginners["Generative AI for Beginners"]
        RelatedCourses --> GenAIDotNet["GenAI for .NET"]
        RelatedCourses --> AIBeginners["AI for Beginners"]
        RelatedCourses --> DataScience["Data Science for Beginners"]
        RelatedCourses --> MLBeginners["ML for Beginners"]
    end
```

Sources: [README.md:97-140]()

These additional resources provide deeper dives into specific topics and alternative learning paths for different programming languages and platforms, ensuring learners can continue their AI education beyond the core curriculum.

## Summary

The Generative AI with JavaScript course is structured as a progressive learning journey that combines technical instruction with an engaging narrative framework. Through six comprehensive lessons, learners develop skills in creating and integrating Generative AI into JavaScript applications, with practical demonstrations through the companion app. The course structure supports various learning styles with written content, code examples, practical assignments, and interactive elements, all designed to build competence in Generative AI implementation.

---

