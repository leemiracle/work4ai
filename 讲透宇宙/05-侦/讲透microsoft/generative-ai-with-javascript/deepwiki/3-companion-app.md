<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/generative-ai-with-javascript · page 3 Companion App · fetched 2026-10-26 -->

# Companion App

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/README.md](app/README.md)
- [app/public/characters.json](app/public/characters.json)
- [app/public/images/amelia-avatar.jpeg](app/public/images/amelia-avatar.jpeg)
- [app/public/images/amelia-front.jpeg](app/public/images/amelia-front.jpeg)

</details>



The Companion App is a web-based application that demonstrates practical implementation of generative AI with JavaScript. It enables users to converse with AI-powered historical characters through a chat interface, serving as a hands-on demonstration of concepts taught in the Generative AI with JavaScript course. For details on setting up the development environment, see [Setup and Configuration](#7).

## Architecture Overview

The app uses a client-server architecture centered around an Express server that handles communication between users and AI models:

```mermaid
graph TD
    User["User"] -->|"HTTP Requests"| ExpressServer["app.js (Express Server)"]
    ExpressServer -->|"Route Handler"| SendEndpoint["/send Endpoint"]
    
    SendEndpoint -->|"Constructs Prompts"| AIClient["AI Model Client"]
    CharactersJSON["characters.json"] -->|"System Prompts"| SendEndpoint
    
    AIClient -->|"API Request"| AIService["GitHub Models/OpenAI API"]
    AIService -->|"Generated Response"| AIClient
    AIClient -->|"Processes Response"| SendEndpoint
    SendEndpoint -->|"JSON Response"| ExpressServer
    ExpressServer -->|"HTTP Response"| User
    
    subgraph "Frontend Assets"
        HTMLFiles["HTML Files"]
        CSSFiles["CSS Files"]
        JSFiles["JavaScript Files"]
        Images["public/images/*.jpeg, *.png"]
        OptionalAudio["public/audio/*.mp3"]
    end
    
    User ---|"Interacts with"| HTMLFiles
```

Sources: [app/README.md:1-65](), [README.md:46-50]()

## Character System

The foundation of the Companion App is its character system, defined in `characters.json`. This file contains an array of character definition objects that configure how each historical persona behaves:

```mermaid
classDiagram
    class CharacterDefinition {
        string title
        string name
        string description
        string page
        string image
        string avatar
        number voice
    }
    
    CharacterDefinition "1" --> "1" SystemPrompt: description_provides
    SystemPrompt --> AIModel: influences_response_generation
    CharacterDefinition "1" --> "1" ImageAsset: image_path_references
    CharacterDefinition "1" --> "1" AvatarAsset: avatar_path_references
    CharacterDefinition "1" --> "0..1" AudioFile: name_maps_to_audio_filename
```

Each character entry contains the following properties:

| Property | Type | Purpose | Example |
|----------|------|---------|---------|
| `title` | String | Display name | `"Leonardo Da Vinci"` |
| `name` | String | Internal identifier | `"davinci"` |
| `description` | String | System prompt | `"You are Leonardo da Vinci, a brilliant inventor..."` |
| `page` | String | HTML page reference | `"davinci.html"` |
| `image` | String | Full image path | `"davinci.png"` |
| `avatar` | String | Avatar image path | `"davinci-avatar.jpeg"` |
| `voice` | Number | Voice ID | `182` |

The `description` field serves as the system prompt that instructs the AI model how to respond as that character, forming the foundation of each character's personality and knowledge limitations.

Sources: [app/public/characters.json:1-56](), [app/README.md:22-24]()

## Request-Response Flow

When a user interacts with the Companion App, the following processing flow occurs:

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "Frontend (HTML/JS)"
    participant Server as "app.js (Express Server)"
    participant CharConfig as "characters.json"
    participant AIModel as "AI Model API"
    
    User->>Frontend: Select character
    Frontend->>Frontend: Update UI with character assets
    
    User->>Frontend: Send message
    Frontend->>Server: POST /send {message, characterId}
    Server->>CharConfig: Load character by ID
    Server->>Server: Extract description as system prompt
    Server->>Server: Construct complete prompt with user message
    Server->>AIModel: Send API request
    AIModel->>Server: Return generated response
    Server->>Frontend: Return JSON response
    Frontend->>User: Display character response
```

This flow demonstrates how the app integrates user input with character configurations to generate contextually appropriate responses through AI models.

Sources: [app/README.md:14-20](), [README.md:46-50]()

## Included Characters

The application ships with six predefined historical characters:

| Character | Internal Name | System Prompt Focus |
|-----------|--------------|---------------------|
| Dinocrates | `dinocrates` | Architecture and engineering projects |
| Leonardo Da Vinci | `davinci` | Inventions and artistic works |
| Ludovico Sforza | `sforza` | Patronage of arts and sciences; expresses frustration at Da Vinci's unfinished mural |
| Montezuma | `montezuma` | Aztec leadership and culture |
| Ada Lovelace | `ada` | Mathematics and early computing concepts |
| Amelia Earhart | `ada` | Aviation pioneering and mechanics |

**Note:** The configuration uses the same internal name `ada` for both Ada Lovelace and Amelia Earhart, which could potentially cause selection issues.

Sources: [app/public/characters.json:1-56]()

## Character Customization

The app's flexibility comes from its easily customizable character system:

```mermaid
graph TD
    EditJSON["Edit characters.json"] -->|"Modify"| SystemPrompt["System Prompt (description)"]
    EditJSON -->|"Update"| Assets["Visual Assets (image/avatar)"]
    EditJSON -->|"Add"| NewCharacter["New Character Entry"]
    
    SystemPrompt -->|"Affects"| AIResponses["AI Response Generation"]
    Assets -->|"Changes"| UserInterface["UI Appearance"]
    NewCharacter -->|"Expands"| CharacterSelection["Available Characters"]
```

To modify a character's behavior:
1. Edit the `description` field in their entry in `characters.json`
2. The modified system prompt will change how the AI model responds
3. No server restart is required for changes to take effect

This design allows for quick iterations on character personalities and knowledge boundaries.

Sources: [app/README.md:22-24](), [app/public/characters.json:1-56]()

## Optional Audio Feature

The app includes a commented-out feature for background audio:

```mermaid
graph LR
    AudioFile["Audio File (e.g. davinci.mp3)"] -->|"Placed in"| AudioFolder["public/audio/"]
    CharacterName["character.name property"] -->|"Determines"| AudioFilename["Audio Filename"]
    UncommentCode["Uncomment Code in index.html"] -->|"Enables"| AudioPlayback["Background Audio"]
    
    AudioPlayback -->|"Triggers on"| CharacterSelection["Character Selection"]
    AudioPlayback -->|"Controls via"| VolumeVariable["maxVolume Variable"]
```

To enable background audio:
1. Download royalty-free music files
2. Name each file according to the character's `name` property (e.g., `davinci.mp3`)
3. Place files in the `/public/audio` folder
4. Uncomment the audio code marked by "TODO" in `index.html`

The app documentation suggests potential music choices for different characters from free resources like Pixabay.

Sources: [app/README.md:31-64]()

## Running the Application

The Companion App can be run through two methods:

### GitHub Codespaces
- Creates a preconfigured development environment in the browser
- Provides access to GitHub Models without additional API setup
- Command sequence:
  ```
  cd app
  npm install
  npm start
  ```
- Then click "Open in Browser" button

### Local Installation
1. Clone the repository
2. Navigate to `/app` directory
3. Run `npm install` to install dependencies
4. Run `npm start` to start the Express server
5. Open the provided URL (typically `http://localhost:3000`) in a browser

Sources: [app/README.md:3-8](), [README.md:59-71]()

## Responsible AI Implementation

The app implements responsible AI practices through:

1. Clear disclaimers that characters are fictional representations
2. Explicit statements that generated responses don't represent actual historical views
3. System prompts that limit character knowledge to their historical time period
4. Transparent labeling of content as being for entertainment purposes
5. Adherence to Microsoft's Responsible AI principles

These measures ensure ethical use of generative AI technology while maintaining an engaging user experience.

Sources: [README.md:143-147](), [app/README.md:27-30](), [app/public/characters.json:5-6, 14-15, 23-24, 32-33, 41-42, 50-51]()

This technical documentation provides an overview of the Companion App's architecture, functionality, and customization options. For information about prompt engineering techniques demonstrated in the app, see [Prompt Engineering Techniques](#5.1) and for details about the app's internal architecture, see [App Architecture](#3.1).

---

