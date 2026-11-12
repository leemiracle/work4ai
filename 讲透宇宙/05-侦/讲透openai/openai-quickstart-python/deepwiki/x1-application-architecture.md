<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-quickstart-python · extra page Application Architecture · fetched 2026-10-26 -->

# Application Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/assistant-flask/app.py](examples/assistant-flask/app.py)

</details>



This document details the server-side architecture, endpoints, and backend logic of the Assistant Flask application. For information about the user interface implementation, see [User Interface](#3.1.2). For details on how file management is implemented, see [File Management](#3.1.3).

## Overview

The Assistant Flask application is a web-based implementation that demonstrates the OpenAI Assistants API capabilities. It is built using Flask as the web framework and integrates directly with OpenAI's Python SDK to create and manage assistants, threads, messages, and files.

```mermaid
graph TD
    User["User"] -->|"Interacts with"| Browser["Web Browser"]
    Browser -->|"HTTP Requests"| FlaskApp["Flask Application"]
    
    subgraph "Flask Application"
        Routes["Routes/Endpoints"] --> IndexRoute["/"]
        Routes --> ChatRoute["/chat"]
        Routes --> UploadRoute["/upload"]
        Routes --> GetMessagesRoute["/get_messages"]
        Routes --> GetFilesRoute["/get_files"]
        Routes --> DeleteFilesRoute["/delete_files"]
        Routes --> ResetRoute["/reset"]
        Routes --> GetIDsRoute["/get_ids"]
        
        AppState["Application State"] --> AssistantID["assistant_id"]
        AppState --> ThreadID["thread_id"]
        AppState --> ChatHistory["chat_history"]
    end
    
    FlaskApp -->|"API Calls"| OpenAI["OpenAI SDK"]
    
    subgraph "OpenAI API"
        Assistants["Assistants API"]
        Threads["Threads API"]
        ThreadMessages["Thread Messages API"]
        Runs["Runs API"]
        Files["Files API"]
    end
    
    OpenAI --> Assistants
    OpenAI --> Threads
    OpenAI --> ThreadMessages
    OpenAI --> Runs
    OpenAI --> Files
```

Sources: [examples/assistant-flask/app.py:1-205]()

## Core Components

The application architecture consists of the following core components:

| Component | Description | Implementation |
|-----------|-------------|----------------|
| Flask Application | Web server that handles HTTP requests | [app.py:10]() |
| OpenAI Client | Interface to the OpenAI API | [app.py:6-8]() |
| Application State | Global variables storing application state | [app.py:14-19]() |
| Route Handlers | Functions to handle HTTP endpoints | [app.py:26-193]() |
| Initialization | Setup executed before the first request | [app.py:197-201]() |

Sources: [examples/assistant-flask/app.py:1-205]()

## Application State

The application maintains three key pieces of state:

```mermaid
graph TD
    AppState["Application State"] --> AssistantID["assistant_id: String
    Identifies the OpenAI Assistant"]
    
    AppState --> ThreadID["thread_id: String
    Identifies the OpenAI Thread"]
    
    AppState --> ChatHistory["chat_history: Array
    Stores message history"]
```

Sources: [examples/assistant-flask/app.py:14-19]()

## Route Structure

The application exposes several HTTP endpoints to handle different aspects of the chat interface:

| Route | Method | Purpose | Implementation |
|-------|--------|---------|----------------|
| `/` | GET | Renders the main chat interface | [app.py:142-144]() |
| `/chat` | POST | Processes user messages and gets assistant responses | [app.py:147-182]() |
| `/upload` | POST | Handles file uploads to the assistant | [app.py:26-58]() |
| `/get_ids` | GET | Returns the current assistant and thread IDs | [app.py:61-63]() |
| `/get_messages` | GET | Retrieves message history from the thread | [app.py:66-79]() |
| `/delete_files` | POST | Removes files from the assistant | [app.py:82-92]() |
| `/get_files` | GET | Lists files attached to the assistant | [app.py:95-110]() |
| `/reset` | POST | Resets the conversation and creates a new thread | [app.py:185-193]() |

Sources: [examples/assistant-flask/app.py:26-193]()

## OpenAI Integration

The application creates and manages OpenAI resources upon initialization:

```mermaid
flowchart TD
    Initialize["initialize()
    @app.before_request function"] -->|"Calls"| CreateAssistant["create_assistant()"]
    Initialize -->|"Calls"| CreateThread["create_thread()"]
    
    CreateAssistant -->|"If assistant_id empty"| NewAssistant["client.beta.assistants.create()
    Creates new assistant with
    code_interpreter tool"]
    
    CreateAssistant -->|"If assistant_id exists"| RetrieveAssistant["client.beta.assistants.retrieve()
    Retrieves existing assistant"]
    
    CreateThread -->|"If thread_id empty"| NewThread["client.beta.threads.create()
    Creates new conversation thread"]
    
    CreateThread -->|"If thread_id exists"| RetrieveThread["client.beta.threads.retrieve()
    Retrieves existing thread"]
```

Sources: [examples/assistant-flask/app.py:113-139](), [examples/assistant-flask/app.py:197-201]()

## Chat Flow

The most important functionality is the chat flow, which integrates with OpenAI's Assistants API:

```mermaid
sequenceDiagram
    participant Client as "Web Client"
    participant Server as "Flask Server"
    participant OpenAI as "OpenAI API"
    
    Client->>Server: POST /chat with user message
    Note over Server: Add message to chat_history
    
    Server->>OpenAI: threads.messages.create(thread_id, role="user", content=message)
    Server->>OpenAI: threads.runs.create(thread_id, assistant_id)
    
    loop Until run.status == "completed"
        Server->>OpenAI: threads.runs.retrieve(thread_id, run_id)
        OpenAI-->>Server: Run status
        Note over Server: Sleep 0.5 seconds if not completed
    end
    
    Server->>OpenAI: threads.messages.list(thread_id)
    OpenAI-->>Server: Latest messages including assistant response
    
    Note over Server: Extract text content from response
    Note over Server: Add response to chat_history
    
    Server-->>Client: JSON response with assistant message
```

Sources: [examples/assistant-flask/app.py:147-182]()

## File Management Architecture

The application allows users to upload files and attach them to the OpenAI Assistant:

```mermaid
flowchart TD
    UploadRoute["/upload endpoint"] -->|"Receives"| FileUpload["File upload request"]
    
    FileUpload -->|"Validates"| FileValidation["allowed_file()
    Checks file extension"]
    
    FileValidation -->|"If valid"| SecureFilename["secure_filename()
    Sanitizes filename"]
    
    SecureFilename -->|"Uploads to OpenAI"| CreateFile["client.files.create()
    Uploads file to OpenAI"]
    
    CreateFile -->|"Gets existing files"| ListFiles["client.beta.assistants.files.list()
    Lists assistant's files"]
    
    ListFiles -->|"Combines IDs"| UpdateAssistant["client.beta.assistants.update()
    Updates assistant with new file list"]
    
    DeleteFilesRoute["/delete_files endpoint"] -->|"Deletes file"| DeleteFile["client.beta.assistants.files.delete()
    Removes file from assistant"]
    
    GetFilesRoute["/get_files endpoint"] -->|"Requests files"| RetrieveFiles["client.beta.assistants.files.list()
    Gets all assistant files"]
```

Sources: [examples/assistant-flask/app.py:26-58](), [examples/assistant-flask/app.py:82-110]()

## Reset Functionality

The application provides a way to reset the conversation:

```mermaid
flowchart TD
    ResetRoute["/reset endpoint"] -->|"Resets"| ChatHistory["chat_history
    Reset to initial system message"]
    
    ResetRoute -->|"Clears"| ThreadId["thread_id
    Set to empty string"]
    
    ThreadId -->|"Triggers"| NewThread["create_thread()
    Creates new conversation thread"]
```

Sources: [examples/assistant-flask/app.py:185-193]()

## Application Initialization

The application uses Flask's before_request hook to initialize the OpenAI resources:

```mermaid
flowchart TD
    AppStart["Application Start"] -->|"Registers"| BeforeRequest["@app.before_request
    initialize()"]
    
    BeforeRequest -->|"Executes once"| RemoveHook["Remove initialize from before_request_funcs"]
    
    BeforeRequest -->|"Creates"| Assistant["create_assistant()
    Creates or retrieves assistant"]
    
    BeforeRequest -->|"Creates"| Thread["create_thread()
    Creates or retrieves thread"]
```

Sources: [examples/assistant-flask/app.py:197-201]()

## Code Structure Mapping

This diagram maps the main application concepts to their implementations in the codebase:

```mermaid
classDiagram
    class FlaskApplication {
        app: Flask instance
        client: OpenAI client
        assistant_id: string
        thread_id: string
        chat_history: list
    }
    
    class Endpoints {
        "/"
        "/chat"
        "/upload"
        "/get_ids"
        "/get_messages"
        "/delete_files"
        "/get_files"
        "/reset"
    }
    
    class HelperFunctions {
        allowed_file()
        create_assistant()
        create_thread()
        initialize()
    }
    
    class OpenAIResources {
        Assistant
        Thread
        Messages
        Runs
        Files
    }
    
    FlaskApplication --> Endpoints : exposes
    Endpoints --> HelperFunctions : uses
    HelperFunctions --> OpenAIResources : manages
```

Sources: [examples/assistant-flask/app.py:1-205]()

## Request-Response Flow

The following diagram illustrates the typical request-response flow through the application:

```mermaid
flowchart LR
    Client["Web Client"] -->|"HTTP Request"| Routes["Flask Routes"]
    
    Routes -->|"/"| IndexRoute["index()
    Renders HTML template"]
    
    Routes -->|"/chat"| ChatRoute["chat()
    Processes messages"]
    
    Routes -->|"/upload"| UploadRoute["upload_file()
    Handles file uploads"]
    
    Routes -->|"Other routes"| OtherRoutes["Other endpoint handlers"]
    
    ChatRoute -->|"Calls"| OpenAIClient["OpenAI SDK Client"]
    UploadRoute -->|"Calls"| OpenAIClient
    OtherRoutes -->|"Calls"| OpenAIClient
    
    OpenAIClient -->|"API Requests"| OpenAIAPI["OpenAI API"]
    
    OpenAIAPI -->|"Responses"| OpenAIClient
    OpenAIClient -->|"Processed Data"| Routes
    Routes -->|"HTTP Response"| Client
```

Sources: [examples/assistant-flask/app.py:26-193]()

## Summary

The Assistant Flask application is built on a Flask backend that integrates with OpenAI's Assistants API. It maintains state through global variables for the assistant and thread IDs, exposes HTTP endpoints to handle user interactions, and manages the flow of messages between the user and the OpenAI Assistant. The architecture supports file uploading and management, allowing users to share files with the assistant for analysis and reference.

---

