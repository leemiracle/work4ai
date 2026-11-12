# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



This document provides an introduction to the `bugbounty-gpt` system, a tool designed to automate the triage and classification of bug bounty submissions from the BugCrowd platform using OpenAI's language models. The system classifies incoming submissions, stores them in a database, and can automatically respond to certain types of submissions based on their classification.

For detailed information about the system architecture, see [System Architecture](#1.1). For configuration details, see [Configuration](#1.2). For deployment instructions, see [Deployment](#1.3).

## Purpose and Functionality

The `bugbounty-gpt` system serves as an automated triage tool for BugCrowd bug bounty programs. It performs the following key functions:

1. Fetches new submissions from the BugCrowd API
2. Uses OpenAI's language models to classify submissions into predefined categories
3. Stores submission data and classifications in a PostgreSQL database
4. Automatically responds to and closes submissions based on their classification
5. Provides a configurable framework for handling different types of bug reports

Sources: [README.md:1-4](), [pyproject.toml:2-4]()

## System Overview

```mermaid
flowchart TD
    subgraph "External Services"
        BugCrowdAPI["BugCrowd API"]
        OpenAIAPI["OpenAI API"]
        PostgresDB[(PostgreSQL Database)]
    end
    
    subgraph "bugbounty-gpt Core"
        MainModule["bugbounty_gpt module"]
        FetchSubmissions["Fetch Submissions"]
        ClassifySubmission["Classify with OpenAI"]
        StoreSubmission["Store in Database"]
        ProcessSubmission["Process Submissions"]
        GenerateResponse["Generate Response"]
    end
    
    MainModule --> FetchSubmissions
    FetchSubmissions --> BugCrowdAPI
    FetchSubmissions --> ClassifySubmission
    ClassifySubmission --> OpenAIAPI
    ClassifySubmission --> StoreSubmission
    StoreSubmission --> PostgresDB
    ProcessSubmission --> PostgresDB
    ProcessSubmission --> GenerateResponse
    GenerateResponse --> BugCrowdAPI
```

Sources: [README.md:1-4](), [Dockerfile:37-38]()

## Key Components

The system consists of several interconnected components:

| Component | Description | Related Files |
|-----------|-------------|---------------|
| BugCrowd API Integration | Handles communication with the BugCrowd platform to fetch submissions and post responses | See [BugCrowd API Integration](#2.1) |
| OpenAI Integration | Uses OpenAI models to classify submissions based on configurable prompts | See [OpenAI Integration](#2.2) |
| Database Layer | Stores submission data, classifications, and processing state | See [Database](#3) |
| Submission Handler | Processes submissions based on their classification | See [Submission Handling](#2.3) |
| Configuration System | Manages settings through config files and environment variables | See [Configuration](#1.2) |

Sources: [README.md:3-4](), [README.md:35-63]()

## System Workflow

```mermaid
sequenceDiagram
    participant BC as "BugCrowd API"
    participant App as "bugbounty-gpt"
    participant OAI as "OpenAI API"
    participant DB as "PostgreSQL DB"
    
    App->>BC: Fetch new submissions
    BC-->>App: Return submissions
    
    loop For each submission
        App->>OAI: Send submission for classification
        OAI-->>App: Return classification
        App->>DB: Store submission with classification
        
        alt In-scope submission
            App->>App: Generate appropriate response
            App->>BC: Post response to submission
            App->>BC: Close submission if needed
        else Out-of-scope submission
            App->>DB: Mark for manual review
        end
    end
```

Sources: [README.md:28-34](), [Dockerfile:37-38]()

## Code Organization

The codebase is organized as a Python package named `bugbounty_gpt`. The main components are:

1. Core application logic in the `bugbounty_gpt` package
2. Configuration through `config.yaml` and environment variables
3. Database migrations managed by Alembic
4. Containerization with Docker for easy deployment

Sources: [pyproject.toml:9-12](), [Dockerfile:13-24]()

## Deployment Options

The system can be deployed in multiple ways:

1. **Docker Container**: The recommended approach for production use
2. **Docker Compose**: Useful for development and testing with an ephemeral database
3. **Direct Python Execution**: Running the module directly with `python -m bugbounty_gpt`

Sources: [README.md:28-34](), [Dockerfile:33-38]()

## Technology Stack

The `bugbounty-gpt` system is built using the following technologies:

| Technology | Purpose |
|------------|---------|
| Python 3.11 | Core programming language |
| SQLAlchemy | ORM for database operations |
| Alembic | Database migration management |
| OpenAI API | AI-powered classification |
| PostgreSQL | Data storage |
| Docker | Containerization |
| Poetry | Dependency management |

Sources: [pyproject.toml:14-27](), [Dockerfile:1-5]()

## System Requirements

To run the system, you need:

1. Python 3.11
2. PostgreSQL database
3. BugCrowd API key
4. OpenAI API key
5. Docker (optional, for containerized deployment)

Sources: [README.md:21-27](), [pyproject.toml:15]()

## Configuration Overview

The system is configured through:

1. A `config.yaml` file for general settings
2. Environment variables for sensitive information like API keys
3. Docker Compose configuration for development environments

For detailed configuration instructions, see [Configuration](#1.2).

Sources: [README.md:35-63](), [README.md:103-114]()

## Code to System Mapping

```mermaid
graph TD
    subgraph "Code Structure"
        BugbountyGPT["bugbounty_gpt package"]
        MainModule["__main__.py"]
        APIModule["api handlers"]
        DBModule["database models"]
        ConfigModule["configuration"]
    end
    
    subgraph "System Components"
        FetchProcess["Submission Fetching"]
        ClassifyProcess["Classification Process"]
        ResponseProcess["Response Generation"]
        StorageProcess["Data Storage"]
        ConfigProcess["Configuration Management"]
    end
    
    BugbountyGPT --> MainModule
    BugbountyGPT --> APIModule
    BugbountyGPT --> DBModule
    BugbountyGPT --> ConfigModule
    
    MainModule --> FetchProcess
    APIModule --> FetchProcess
    APIModule --> ResponseProcess
    DBModule --> StorageProcess
    ConfigModule --> ConfigProcess
    
    FetchProcess --> ClassifyProcess
    ClassifyProcess --> StorageProcess
    StorageProcess --> ResponseProcess
```

Sources: [pyproject.toml:9-12](), [README.md:35-63]()

## Summary

The `bugbounty-gpt` system provides an automated solution for triaging and responding to bug bounty submissions. By leveraging OpenAI's language models, it can accurately classify submissions and generate appropriate responses, reducing the manual effort required to manage a bug bounty program. The system is designed to be flexible and configurable, allowing it to be adapted to different bug bounty programs and requirements.

For more detailed information about specific components of the system, please refer to the linked sections in this documentation.

Sources: [README.md:1-4](), [pyproject.toml:2-4]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bugbounty_gpt/__main__.py](bugbounty_gpt/__main__.py)
- [bugbounty_gpt/env.py](bugbounty_gpt/env.py)
- [bugbounty_gpt/handlers/bugcrowd_api.py](bugbounty_gpt/handlers/bugcrowd_api.py)
- [bugbounty_gpt/handlers/openai_handler.py](bugbounty_gpt/handlers/openai_handler.py)

</details>



This document describes the high-level architecture of the `bugbounty-gpt` system, including its main components and their interactions. The system is designed to automate the triage and classification of bug bounty submissions from the BugCrowd platform using OpenAI's language models.

For information about configuring the system, see [Configuration](#1.2). For deployment details, see [Deployment](#1.3).

## System Overview

The `bugbounty-gpt` system is an automated solution for processing bug bounty submissions. It fetches new submissions from BugCrowd, classifies them using OpenAI's language models, and takes appropriate actions based on the classification results.

```mermaid
graph TB
    subgraph "External Services"
        BugCrowdAPI["BugCrowd API"]
        OpenAIAPI["OpenAI API"]
        PostgresDB[("PostgreSQL Database")]
    end
    
    subgraph "bugbounty-gpt Core"
        MainLoop["Main Processing Loop"]
        BugCrowdHandler["BugCrowd API Handler"]
        OpenAIHandler["OpenAI Handler"]
        DBHandler["Database Handler"]
        SubmissionHandler["Submission Handler"]
        ConfigSystem["Configuration System"]
    end
    
    MainLoop --> BugCrowdHandler
    MainLoop --> OpenAIHandler
    MainLoop --> DBHandler
    MainLoop --> SubmissionHandler
    
    BugCrowdHandler --> BugCrowdAPI
    OpenAIHandler --> OpenAIAPI
    DBHandler --> PostgresDB
    SubmissionHandler --> BugCrowdHandler
    
    ConfigSystem --> MainLoop
    ConfigSystem --> BugCrowdHandler
    ConfigSystem --> OpenAIHandler
```

Sources: [bugbounty_gpt/__main__.py:1-100](), [bugbounty_gpt/env.py:1-71](), [bugbounty_gpt/handlers/bugcrowd_api.py:1-137](), [bugbounty_gpt/handlers/openai_handler.py:1-85]()

## Core Components

### Main Processing Loop

The main processing loop is the central orchestrator of the system. It periodically:
1. Fetches new submissions from BugCrowd
2. Classifies them using OpenAI
3. Stores the results in the database
4. Processes submissions that are in scope
5. Generates responses and updates the submissions on BugCrowd

```mermaid
flowchart TD
    Start["Start Main Loop"] --> FetchSubmissions["process_new_submissions()"]
    FetchSubmissions --> ProcessInScope["process_in_scope_submissions()"]
    ProcessInScope --> Sleep["Sleep for 1 minute"]
    Sleep --> FetchSubmissions
```

Sources: [bugbounty_gpt/__main__.py:84-100]()

### BugCrowd API Handler

The `BugCrowdAPI` class handles all interactions with the BugCrowd API, including:
- Fetching submissions
- Creating comments
- Updating submission states

```mermaid
classDiagram
    class BugCrowdAPI {
        +_get_headers(content_type) static
        +_fetch_page(url, params, page_limit, page_offset) static
        +fetch_submissions(params) static
        +fetch_submission(submission_id) static
        +create_comment(comment_data) static
        +patch_submission(submission_id, data) static
    }
```

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:9-137]()

### OpenAI Handler

The `OpenAIHandler` class is responsible for classifying submissions using OpenAI's language models. It:
- Builds the request data for the OpenAI API
- Handles the response from the API
- Sanitizes and validates the classification results

```mermaid
classDiagram
    class OpenAIHandler {
        +_classifications_sanitization(input_string) static
        +_build_request_data(submission_content) static
        +_handle_response_error(error) static
        +_handle_response(response) static
        +classify_submission(submission_content) static
    }
```

Sources: [bugbounty_gpt/handlers/openai_handler.py:9-85]()

### Database Handler

The database handler manages all interactions with the PostgreSQL database, including:
- Inserting new submissions
- Updating submission states
- Fetching submissions based on state and classification

Sources: [bugbounty_gpt/__main__.py:19-25](), [bugbounty_gpt/__main__.py:58](), [bugbounty_gpt/__main__.py:68](), [bugbounty_gpt/__main__.py:80](), [bugbounty_gpt/__main__.py:82]()

### Submission Handler

The `BugCrowdSubmission` class represents a submission and provides methods to:
- Check if a submission is new
- Generate comment text based on classification
- Create comments on the submission
- Close the submission

Sources: [bugbounty_gpt/__main__.py:71-82]()

### Configuration System

The configuration system loads and validates settings from a YAML file and environment variables. It provides:
- API settings (BugCrowd and OpenAI)
- Database connection details
- User-specific settings
- Categories and responses for classification

```mermaid
flowchart LR
    ConfigYAML["config.yaml"] --> LoadConfig["load_config()"]
    EnvVars["Environment Variables"] --> LoadConfig
    LoadConfig --> ValidateConfig["validate_config()"]
    ValidateConfig --> ConfigObject["CONFIG object"]
    ConfigObject --> APISettings["API Settings"]
    ConfigObject --> DBSettings["Database Settings"]
    ConfigObject --> UserSettings["User Settings"]
    ConfigObject --> Categories["Categories & Responses"]
```

Sources: [bugbounty_gpt/env.py:8-70]()

## Data Flow

The following diagram illustrates the data flow through the system:

```mermaid
sequenceDiagram
    participant Main as "Main Loop"
    participant BugCrowd as "BugCrowd API"
    participant OpenAI as "OpenAI API"
    participant DB as "Database"
    
    Main->>BugCrowd: Fetch new submissions
    BugCrowd-->>Main: Return submissions
    
    loop For each submission
        Main->>OpenAI: Classify submission
        OpenAI-->>Main: Return classification
        Main->>DB: Store submission with classification
    end
    
    Main->>DB: Fetch in-scope submissions
    DB-->>Main: Return in-scope submissions
    
    loop For each in-scope submission
        Main->>Main: Generate response
        Main->>BugCrowd: Create comment
        Main->>BugCrowd: Close submission
        Main->>DB: Update submission state
    end
```

Sources: [bugbounty_gpt/__main__.py:29-82]()

## Component Interactions

The following diagram shows how the different components interact with each other:

```mermaid
graph TB
    subgraph "Main Processing Loop"
        ProcessNewSubmissions["process_new_submissions()"]
        ProcessInScopeSubmissions["process_in_scope_submissions()"]
    end
    
    subgraph "BugCrowd API Handler"
        FetchSubmissions["fetch_submissions()"]
        CreateComment["create_comment()"]
        PatchSubmission["patch_submission()"]
    end
    
    subgraph "OpenAI Handler"
        ClassifySubmission["classify_submission()"]
    end
    
    subgraph "Database Handler"
        InsertSubmission["insert_submission()"]
        FetchSubmissionByState["fetch_submission_by_state_and_classification()"]
        UpdateSubmissionState["update_submission_state()"]
    end
    
    subgraph "Submission Handler"
        IsSubmissionNew["is_submission_new()"]
        GenerateCommentText["generate_comment_text()"]
        CreateSubmissionComment["create_comment()"]
        CloseSubmission["close_submission()"]
    end
    
    ProcessNewSubmissions --> FetchSubmissions
    ProcessNewSubmissions --> ClassifySubmission
    ProcessNewSubmissions --> InsertSubmission
    
    ProcessInScopeSubmissions --> FetchSubmissionByState
    ProcessInScopeSubmissions --> IsSubmissionNew
    ProcessInScopeSubmissions --> GenerateCommentText
    ProcessInScopeSubmissions --> CreateSubmissionComment
    ProcessInScopeSubmissions --> CloseSubmission
    ProcessInScopeSubmissions --> UpdateSubmissionState
    
    CreateSubmissionComment --> CreateComment
    CloseSubmission --> PatchSubmission
```

Sources: [bugbounty_gpt/__main__.py:29-82]()

## Database Schema

The system uses a PostgreSQL database to store submission data and track the state of each submission.

```mermaid
erDiagram
    SUBMISSION {
        string submission_id PK
        string user_id
        string classification
        enum submission_state
        string reasoning
        timestamp created_at
        timestamp updated_at
    }
```

Sources: [bugbounty_gpt/__main__.py:5](), [bugbounty_gpt/__main__.py:50-56]()

## Execution Flow

The main execution flow of the system is as follows:

```mermaid
flowchart TD
    Start["Start Application"] --> InitDB["Initialize Database Connection"]
    InitDB --> MainLoop["Enter Main Loop"]
    
    MainLoop --> FetchNew["Fetch New Submissions"]
    FetchNew --> ProcessNew["Process New Submissions"]
    ProcessNew --> Classify["Classify with OpenAI"]
    Classify --> StoreDB["Store in Database"]
    
    StoreDB --> FetchInScope["Fetch In-Scope Submissions"]
    FetchInScope --> ProcessInScope["Process In-Scope Submissions"]
    ProcessInScope --> GenerateResponse["Generate Response"]
    GenerateResponse --> CreateComment["Create Comment"]
    CreateComment --> CloseSubmission["Close Submission"]
    CloseSubmission --> UpdateState["Update Submission State"]
    
    UpdateState --> Sleep["Sleep for 1 minute"]
    Sleep --> MainLoop
```

Sources: [bugbounty_gpt/__main__.py:84-100](), [bugbounty_gpt/__main__.py:29-82]()

## Configuration Dependencies

The system relies on configuration from both a YAML file and environment variables:

| Configuration Source | Provides |
|----------------------|----------|
| config.yaml | API base URL, OpenAI model, user ID, filter program, valid categories, response categories, default category, OpenAI prompt |
| Environment Variables | BugCrowd API key, OpenAI API key, Database connection URL |

Sources: [bugbounty_gpt/env.py:8-70]()

## Error Handling

The system includes error handling at various levels:

1. API request errors are logged and handled gracefully
2. OpenAI classification errors result in using the default category
3. Database errors are caught and logged
4. The main loop continues running even if individual submissions fail to process

Sources: [bugbounty_gpt/handlers/openai_handler.py:38-48](), [bugbounty_gpt/handlers/bugcrowd_api.py:42-48](), [bugbounty_gpt/handlers/bugcrowd_api.py:132-135]()

## Summary

The `bugbounty-gpt` system architecture follows a modular design with clear separation of concerns. The main components (BugCrowd API Handler, OpenAI Handler, Database Handler, and Submission Handler) interact through well-defined interfaces, orchestrated by the main processing loop. The configuration system provides centralized management of settings, and the database ensures persistence of submission data and state.

This architecture allows for easy extension and modification of individual components without affecting the overall system, making it maintainable and adaptable to changing requirements.

---

# Page: Configuration

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bugbounty_gpt/env.py](bugbounty_gpt/env.py)
- [tests/test_config_validation.py](tests/test_config_validation.py)

</details>



This page explains how to configure the BugCrowd GPT Classifier system using the `config.yaml` file and environment variables. The configuration system controls all aspects of the application's behavior, from API connections to submission categorization and automated responses.

For information about deploying the system, see [Deployment](#1.3).

## Configuration Overview

The BugCrowd GPT Classifier uses a combination of:
1. A YAML configuration file (`config.yaml`)
2. Environment variables for sensitive information

```mermaid
flowchart TD
    subgraph "Configuration Sources"
        ConfigYAML["config.yaml"]
        EnvVars["Environment Variables"]
    end
    
    subgraph "Configuration Components"
        APISettings["API Settings"]
        UserSettings["User Settings"]
        Categories["Categories & Responses"]
        OpenAIPrompt["OpenAI Prompt"]
    end
    
    subgraph "Environment Variables"
        BUGCROWD_API_KEY["BUGCROWD_API_KEY"]
        OPENAI_API_KEY["OPENAI_API_KEY"]
        SQLALCHEMY_URL["SQLALCHEMY_URL"]
    end
    
    ConfigYAML --> APISettings
    ConfigYAML --> UserSettings
    ConfigYAML --> Categories
    ConfigYAML --> OpenAIPrompt
    
    EnvVars --> BUGCROWD_API_KEY
    EnvVars --> OPENAI_API_KEY
    EnvVars --> SQLALCHEMY_URL
    
    BUGCROWD_API_KEY --> APISettings
    OPENAI_API_KEY --> APISettings
    SQLALCHEMY_URL --> APISettings
```

Sources: [README.md:35-69](). [bugbounty_gpt/env.py:1-71]()

## Configuration File Structure

The `config.yaml` file is located in the root directory of the project and contains the following main sections:

| Section | Purpose |
|---------|---------|
| `api` | API connection settings for BugCrowd and OpenAI |
| `user` | User-specific settings like user ID and program filter |
| `categories` | Defines valid categories and automated responses |
| `openai_prompt` | The prompt template used for OpenAI classification |

Sources: [README.md:40-63](), [bugbounty_gpt/env.py:8-12]()

## API Settings

The `api` section in `config.yaml` configures the connections to external APIs:

```yaml
api:
  base_url: "https://api.bugcrowd.com"
  openai_model: "gpt-4"
```

- `base_url`: The base URL for the BugCrowd API
- `openai_model`: The OpenAI model to use for classification (e.g., "gpt-4")

Sources: [README.md:42-44](), [bugbounty_gpt/env.py:48-52]()

## User Settings

The `user` section contains settings specific to the user and program:

```yaml
user:
  user_id: ""  # BugCrowd user ID
  filter_program: "openai-test-sandbox"  # Program identifier
```

- `user_id`: The BugCrowd ID of the user assigned to reports (can be empty)
- `filter_program`: The specific BugCrowd program to filter submissions by

Sources: [README.md:46-50](), [bugbounty_gpt/env.py:57-59]()

## Categories Configuration

The `categories` section is crucial for the classification and response system:

```mermaid
flowchart TD
    subgraph "Categories Configuration"
        Valid["valid: Array of category names"]
        Default["default: Fallback category"]
        Response["response: Array of objects with name and response"]
    end
    
    subgraph "Processing"
        Sanitize["sanitize_categories()"]
        Validate["validate_config()"]
    end
    
    subgraph "Runtime Variables"
        VALID_CATEGORIES["VALID_CATEGORIES"]
        DEFAULT_CATEGORY["DEFAULT_CATEGORY"]
        RESPONSE_CATEGORIES["RESPONSE_CATEGORIES"]
        RESPONSES["RESPONSES"]
    end
    
    Valid --> Sanitize
    Default --> Sanitize
    Response --> Sanitize
    
    Sanitize --> VALID_CATEGORIES
    Sanitize --> DEFAULT_CATEGORY
    Sanitize --> RESPONSE_CATEGORIES
    Response --> RESPONSES
    
    Valid --> Validate
    Default --> Validate
    Response --> Validate
```

The categories section has three main components:

1. **Valid Categories**: A list of all possible classification categories
   ```yaml
   categories:
     valid:
       - "Functional Bugs or Glitches"
       - "Customer Support Issues"
       - "Security Report"
       # ... other categories
   ```

2. **Default Category**: The fallback category when classification fails
   ```yaml
   categories:
     default: "Security Report"
   ```

3. **Response Categories**: Categories that receive automated responses
   ```yaml
   categories:
     response:
       - name: "Functional Bugs or Glitches"
         response: "Thank you for your submission. This appears to be a functional bug rather than a security issue..."
       - name: "Customer Support Issues"
         response: "Thank you for your submission. This appears to be a customer support issue..."
       # ... other response pairs
   ```

Sources: [README.md:53-59](), [bugbounty_gpt/env.py:64-68](), [tests/test_config_validation.py:13-39]()

## OpenAI Prompt

The `openai_prompt` section contains the template used to instruct the OpenAI model:

```yaml
openai_prompt: |
  You are a bug bounty submission classifier. Your task is to categorize the following submission into one of these categories:
  - Functional Bugs or Glitches
  - Customer Support Issues
  - Security Report
  # ... additional instructions and guidelines
```

This multi-line string provides detailed instructions to the AI model on how to classify submissions.

Sources: [README.md:61-63](), [bugbounty_gpt/env.py:61-62]()

## Environment Variables

Sensitive information is stored in environment variables rather than in the configuration file:

| Variable | Purpose |
|----------|---------|
| `BUGCROWD_API_KEY` | API key for BugCrowd authentication |
| `OPENAI_API_KEY` | API key for OpenAI services |
| `SQLALCHEMY_URL` | Database connection string |

The `SQLALCHEMY_URL` should follow the format:
```
postgresql+asyncpg://<username>:<password>@<host>:<port>/<database>
```

Sources: [README.md:65-69](), [bugbounty_gpt/env.py:50-55]()

## Configuration Validation

The system validates the configuration at startup to ensure it meets requirements:

```mermaid
flowchart TD
    LoadConfig["load_config()"] --> Config["CONFIG"]
    Config --> ValidateConfig["validate_config()"]
    
    subgraph "Validation Functions"
        ValidateValidCategories["validate_valid_categories()"]
        ValidateResponseCategoriesSubset["validate_response_categories_subset()"]
        ValidateResponsePairs["validate_response_pairs()"]
    end
    
    ValidateConfig --> ValidateValidCategories
    ValidateConfig --> ValidateResponseCategoriesSubset
    ValidateConfig --> ValidateResponsePairs
    
    ValidateValidCategories -- "Error if missing" --> Error1["ValueError"]
    ValidateResponseCategoriesSubset -- "Error if not subset" --> Error2["ValueError"]
    ValidateResponsePairs -- "Error if missing keys" --> Error3["ValueError"]
```

The validation ensures:
1. Valid categories are defined
2. Response categories are a subset of valid categories
3. Each response category has both a name and response text

Sources: [bugbounty_gpt/env.py:22-44](), [tests/test_config_validation.py:13-39]()

## Category Sanitization

Category names are sanitized to create valid Python identifiers for use in the database:

```python
def sanitize_category(category: str) -> str:
    """Sanitizes a single category name to ensure it is a valid Python identifier."""
    return re.sub(r'\W|^(?=\d)', '_', category).upper().strip()
```

For example:
- "Functional Bugs or Glitches" → "FUNCTIONAL_BUGS_OR_GLITCHES"
- "123 Category with Special!@#$%^&*()" → "_123_CATEGORY_WITH_SPECIAL__________"

Sources: [bugbounty_gpt/env.py:14-20](), [tests/test_config_validation.py:4-11]()

## Docker Compose Configuration

When using Docker Compose for development or testing, additional environment variables are needed:

| Variable | Purpose |
|----------|---------|
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `DB_NAME` | Database name |
| `BUGCROWD_API_KEY` | BugCrowd API key |
| `OPENAI_API_KEY` | OpenAI API key |

These variables are used to configure the ephemeral database for testing configuration changes.

Sources: [README.md:71-114]()

## Configuration Loading Process

The configuration loading process follows these steps:

1. Load the YAML configuration file
2. Validate the configuration structure
3. Sanitize category names
4. Set up environment variables
5. Create runtime configuration variables

```mermaid
sequenceDiagram
    participant App as Application
    participant Env as env.py
    participant YAML as config.yaml
    participant OS as Environment Variables
    
    App->>Env: Import module
    Env->>YAML: load_config()
    YAML-->>Env: Raw configuration
    Env->>Env: validate_config()
    Env->>Env: sanitize_categories()
    Env->>OS: Get environment variables
    Env-->>App: Provide configuration constants
```

Sources: [bugbounty_gpt/env.py:1-71]()

## Best Practices

When configuring the system, follow these best practices:

1. Keep API keys and database credentials in environment variables, not in the configuration file
2. Test configuration changes using the ephemeral database in Docker Compose
3. Ensure all response categories are a subset of valid categories
4. Provide detailed instructions in the OpenAI prompt for accurate classification
5. Use descriptive category names that clearly distinguish different types of submissions

Sources: [README.md:35-114]()

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [bugbounty_gpt/start.sh](bugbounty_gpt/start.sh)

</details>



This document describes how to deploy the BugCrowd GPT Classifier system using Docker and Docker Compose. It covers the deployment process, configuration requirements, and operational considerations for both development and production environments.

For information about system architecture, see [System Architecture](#1.1). For details on configuration options, see [Configuration](#1.2).

## Deployment Overview

The BugCrowd GPT Classifier can be deployed using Docker containers, which package all dependencies and configuration into a standardized environment. The system supports two primary deployment modes:

1. **Development Mode** - Uses an ephemeral database for testing configuration changes
2. **Production Mode** - Connects to a persistent database for long-term operation

```mermaid
flowchart TB
    subgraph "Deployment Options"
        Dev["Development Deployment"]
        Prod["Production Deployment"]
    end
    
    subgraph "Components"
        Docker["Docker Container"]
        DockerCompose["Docker Compose"]
        EphemeralDB[(Ephemeral Database)]
        PersistentDB[(Persistent Database)]
        Config["config.yaml"]
        EnvVars["Environment Variables"]
    end
    
    Dev --> DockerCompose
    DockerCompose --> Docker
    DockerCompose --> EphemeralDB
    Docker --> Config
    Docker --> EnvVars
    
    Prod --> Docker
    Docker --> PersistentDB
```

Sources: [Dockerfile](). [README.md:21-34]().

## Docker Container Setup

The system is containerized using a Dockerfile that:

1. Uses Python 3.11 as the base image
2. Installs Poetry for dependency management
3. Creates a non-root user for security
4. Copies application code and configuration files
5. Installs dependencies using Poetry
6. Sets up Alembic for database migrations
7. Configures the startup command based on deployment mode

```mermaid
flowchart TB
    subgraph "Docker Container"
        Python["Python 3.11 Runtime"]
        Poetry["Poetry Dependency Manager"]
        AppCode["Application Code"]
        Config["Configuration Files"]
        Alembic["Alembic Migration Scripts"]
        StartScript["start.sh Script"]
    end
    
    subgraph "Execution"
        EphemeralMode["Ephemeral Mode"]
        ProductionMode["Production Mode"]
    end
    
    Python --> Poetry
    Poetry --> AppCode
    AppCode --> Config
    AppCode --> Alembic
    
    EphemeralMode --> StartScript
    StartScript --> Alembic
    StartScript --> AppCode
    
    ProductionMode --> AppCode
```

Sources: [Dockerfile:1-38](). [bugbounty_gpt/start.sh:1-8]().

## Deployment Methods

### Development Deployment with Docker Compose

For development and testing, Docker Compose provides a convenient way to set up the application with an ephemeral database:

1. Configure environment variables and `config.yaml`
2. Build the containers with `docker-compose build`
3. Start the application with `docker-compose up`
4. When finished, tear down everything with `docker-compose down -v`

This approach is particularly useful when testing configuration changes, especially modifications to category types that require database schema updates.

### Production Deployment

For production environments:

1. Configure environment variables and `config.yaml`
2. Build the Docker image without the `ephemeral_db` argument
3. Run the container, connecting it to a persistent PostgreSQL database
4. Manage database migrations manually using Alembic

## Required Configuration

### Environment Variables

The following environment variables must be set for deployment:

| Variable | Description | Required For |
|----------|-------------|-------------|
| `BUGCROWD_API_KEY` | API key for BugCrowd | All deployments |
| `OPENAI_API_KEY` | API key for OpenAI | All deployments |
| `SQLALCHEMY_URL` | Database connection URL | Production deployments |
| `DB_USER` | Database username | Docker Compose development |
| `DB_PASSWORD` | Database password | Docker Compose development |
| `DB_NAME` | Database name | Docker Compose development |

### Configuration File

The `config.yaml` file must be properly configured before deployment. This file contains:

- API settings (base URLs, model names)
- User settings (user ID, program filter)
- Category definitions
- OpenAI prompt template

Sources: [README.md:35-64](). [Dockerfile:15-16]().

## Deployment Process

```mermaid
sequenceDiagram
    participant User
    participant Docker as Docker/Docker Compose
    participant Container as Application Container
    participant DB as Database
    participant APIs as External APIs

    User->>Docker: Configure environment variables
    User->>Docker: Configure config.yaml
    User->>Docker: Build container
    Docker->>Container: Create container
    
    alt Development Mode
        User->>Docker: docker-compose up
        Docker->>DB: Create ephemeral database
        Container->>DB: Run migrations (start.sh)
        Container->>Container: Start application
    else Production Mode
        User->>Docker: docker run
        Container->>DB: Connect to persistent database
        Container->>Container: Start application
    end
    
    Container->>APIs: Connect to BugCrowd API
    Container->>APIs: Connect to OpenAI API
    Container->>DB: Store and retrieve data
```

Sources: [Dockerfile:33-38](). [bugbounty_gpt/start.sh:1-8]().

## Docker Container Structure

The Docker container includes the following components:

1. **Application Code**: The `bugbounty_gpt` package containing the application logic
2. **Configuration**: The `config.yaml` file with application settings
3. **Database Migration Scripts**: Alembic configuration and migration scripts
4. **Start Script**: A shell script that runs migrations and starts the application in ephemeral mode

The container is configured to run as a non-root user for security purposes.

Sources: [Dockerfile:7-31]().

## Ephemeral Database Mode

The ephemeral database mode is controlled by the `EPHEMERAL_DB` build argument in the Dockerfile. When set to `true`, the container runs the `start.sh` script, which:

1. Executes database migrations using `python -m bugbounty_gpt.db.migrate`
2. Starts the main application with `python -m bugbounty_gpt`

This mode is useful for testing configuration changes that affect the database schema, particularly changes to category types that are stored as Enum values in the database.

Sources: [Dockerfile:33-38](). [bugbounty_gpt/start.sh:1-8](). [README.md:70-81]().

## Production Considerations

When deploying to production:

1. Use a persistent PostgreSQL database with proper backup procedures
2. Manage database migrations carefully, especially when changing category types
3. Set up monitoring and logging for the container
4. Consider implementing a container orchestration system for high availability
5. Secure API keys and database credentials using environment variables or a secrets management system

Sources: [README.md:82-102]().

## Troubleshooting Deployment Issues

Common deployment issues include:

1. **Missing Environment Variables**: Ensure all required environment variables are set
2. **Database Connection Issues**: Verify the database connection URL and credentials
3. **Permission Problems**: Check that the container has appropriate permissions for file access
4. **Migration Failures**: When changing category types, you may need to recreate the database schema

For testing configuration changes that affect the database schema, use the ephemeral database mode with Docker Compose to quickly iterate without affecting production data.

Sources: [README.md:103-114]().

---

# Page: Core Components

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bugbounty_gpt/__main__.py](bugbounty_gpt/__main__.py)
- [pyproject.toml](pyproject.toml)

</details>



This page provides an overview of the main components that make up the bugbounty-gpt system. It describes the core modules, their responsibilities, and how they interact with each other to automate the triage and classification of bug bounty submissions.

For information about the high-level system architecture, see [System Architecture](#1.1). For details on specific integrations, see [BugCrowd API Integration](#2.1) and [OpenAI Integration](#2.2).

## Component Overview

The bugbounty-gpt system consists of several core components that work together to process bug bounty submissions:

```mermaid
graph TB
    subgraph "Core Components"
        MainLoop["Main Processing Loop<br>(__main__.py)"]
        BugCrowdAPI["BugCrowdAPI<br>(bugcrowd_api.py)"]
        OpenAIHandler["OpenAIHandler<br>(openai_handler.py)"]
        DBHandler["Database Handler<br>(db_handler.py)"]
        SubmissionHandler["Submission Handler<br>(submission_handler.py)"]
        ConfigSystem["Configuration System<br>(env.py)"]
    end
    
    MainLoop -->|"fetch_submissions()"| BugCrowdAPI
    MainLoop -->|"classify_submission()"| OpenAIHandler
    MainLoop -->|"insert_submission()<br>fetch_submission_by_state_and_classification()<br>update_submission_state()"| DBHandler
    MainLoop -->|"create BugCrowdSubmission"| SubmissionHandler
    
    SubmissionHandler -->|"create_comment()<br>close_submission()"| BugCrowdAPI
    
    ConfigSystem -->|"provides configuration"| MainLoop
    ConfigSystem -->|"provides API keys"| BugCrowdAPI
    ConfigSystem -->|"provides API keys"| OpenAIHandler
    
    classDef component fill:#f5f5f5,stroke:#333,stroke-width:1px;
    class MainLoop,BugCrowdAPI,OpenAIHandler,DBHandler,SubmissionHandler,ConfigSystem component;
```

Sources: [bugbounty_gpt/__main__.py:1-100]()

## Main Processing Loop

The main processing loop is the orchestrator of the system, responsible for:

1. Fetching new submissions from BugCrowd
2. Classifying them using OpenAI
3. Storing them in the database
4. Processing submissions that are in scope
5. Generating responses and closing submissions

The main loop runs continuously with a configurable wait period between iterations.

```mermaid
flowchart TD
    Start["Start Main Loop"] --> FetchNew["Fetch New Submissions<br>process_new_submissions()"]
    FetchNew --> ProcessInScope["Process In-Scope Submissions<br>process_in_scope_submissions()"]
    ProcessInScope --> Wait["Wait (Sleep)"]
    Wait --> FetchNew
    
    subgraph "process_new_submissions()"
        FetchAPI["BugCrowdAPI.fetch_submissions()"] --> FilterDuplicates["Filter Already Seen"]
        FilterDuplicates --> Classify["OpenAIHandler.classify_submission()"]
        Classify --> StoreDB["db_handler.insert_submission()"]
    end
    
    subgraph "process_in_scope_submissions()"
        FetchInScope["db_handler.fetch_submission_by_state_and_classification()"] --> CheckNew["submission.is_submission_new()"]
        CheckNew -->|"Yes"| GenerateComment["submission.generate_comment_text()"]
        GenerateComment --> CreateComment["submission.create_comment()"]
        CreateComment --> CloseSubmission["submission.close_submission()"]
        CloseSubmission --> UpdateState["db_handler.update_submission_state()"]
        CheckNew -->|"No"| UpdateOutOfBand["db_handler.update_submission_state()<br>(UPDATED_OUT_OF_BAND)"]
    end
```

Sources: [bugbounty_gpt/__main__.py:29-97]()

## BugCrowd API Integration

The `BugCrowdAPI` class handles all interactions with the BugCrowd platform, including:

- Fetching submissions with specific filters
- Creating comments on submissions
- Closing submissions
- Assigning submissions to users

This component abstracts away the details of the HTTP requests and authentication required to interact with the BugCrowd API.

Sources: [bugbounty_gpt/__main__.py:8-8](), [bugbounty_gpt/__main__.py:40-40]()

## OpenAI Integration

The `OpenAIHandler` is responsible for classifying bug bounty submissions using OpenAI's language models. It:

1. Takes the submission content as input
2. Sends it to the OpenAI API with a specific prompt
3. Parses the response to extract the classification and reasoning
4. Returns this information to the main loop

The classification determines whether a submission is in scope and what type of issue it represents.

Sources: [bugbounty_gpt/__main__.py:6-6](), [bugbounty_gpt/__main__.py:49-49]()

## Database Handler

The `db_handler` module provides functions for interacting with the PostgreSQL database, including:

- Inserting new submissions
- Updating submission states
- Fetching submissions based on state and classification

The database serves as the system's persistent storage and state management mechanism.

```mermaid
graph LR
    subgraph "Database Operations"
        Insert["insert_submission()"]
        Update["update_submission_state()"]
        Fetch["fetch_submission_by_state_and_classification()"]
    end
    
    subgraph "Database Models"
        Submission["Submission<br>(id, submission_id, user_id,<br>classification, submission_state, reasoning)"]
        SubmissionState["SubmissionState Enum<br>(NEW, UPDATED, UPDATED_OUT_OF_BAND)"]
    end
    
    Insert --> Submission
    Update --> Submission
    Fetch --> Submission
    Submission --> SubmissionState
```

Sources: [bugbounty_gpt/__main__.py:4-5](), [bugbounty_gpt/__main__.py:58-58](), [bugbounty_gpt/__main__.py:68-68](), [bugbounty_gpt/__main__.py:80-82]()

## Submission Handler

The `BugCrowdSubmission` class represents a submission from BugCrowd and provides methods to:

- Generate appropriate comment text based on the classification
- Create comments on the submission
- Close the submission
- Check if the submission is still in the "new" state

This component encapsulates the business logic for responding to different types of submissions.

Sources: [bugbounty_gpt/__main__.py:7-7](), [bugbounty_gpt/__main__.py:71-82]()

## Configuration System

The configuration system, primarily implemented in `env.py`, provides centralized access to all configuration parameters, including:

- BugCrowd API credentials
- OpenAI API credentials
- Database connection string
- User ID for assignment
- Program filter
- Response categories

Configuration can be set through a combination of environment variables and a YAML configuration file.

| Configuration Parameter | Description | Used By |
|------------------------|-------------|---------|
| `USER_ID` | The ID of the user to assign submissions to | Main Loop |
| `FILTER_PROGRAM` | The BugCrowd program to filter submissions by | Main Loop |
| `RESPONSE_CATEGORIES` | Categories of submissions that should receive responses | Main Loop |
| `SQLALCHEMY_URL` | Database connection string | Database Handler |

Sources: [bugbounty_gpt/__main__.py:9-9](), [bugbounty_gpt/__main__.py:34-36](), [bugbounty_gpt/__main__.py:67-67](), [bugbounty_gpt/__main__.py:72-72]()

## Component Interactions

The following diagram illustrates how the core components interact during the processing of a bug bounty submission:

```mermaid
sequenceDiagram
    participant Main as "Main Loop"
    participant BugCrowd as "BugCrowdAPI"
    participant OpenAI as "OpenAIHandler"
    participant DB as "Database Handler"
    participant Submission as "BugCrowdSubmission"
    
    Main->>BugCrowd: fetch_submissions(params)
    BugCrowd-->>Main: submissions
    
    loop For each submission
        Main->>OpenAI: classify_submission(content)
        OpenAI-->>Main: classification, reasoning
        Main->>DB: insert_submission(data)
    end
    
    Main->>DB: fetch_submission_by_state_and_classification(states, classifications)
    DB-->>Main: in_scope_submissions
    
    loop For each in-scope submission
        Main->>Submission: create BugCrowdSubmission(id, classification, reasoning)
        Main->>Submission: is_submission_new()
        Submission-->>Main: is_new
        
        alt is_new is true
            Main->>Submission: generate_comment_text()
            Submission-->>Main: comment_body
            Main->>Submission: create_comment(comment_body)
            Main->>Submission: close_submission()
            Main->>DB: update_submission_state(id, UPDATED)
        else is_new is false
            Main->>DB: update_submission_state(id, UPDATED_OUT_OF_BAND)
        end
    end
```

Sources: [bugbounty_gpt/__main__.py:29-97]()

## Data Flow

The data flow through the system follows a clear path from input to output:

```mermaid
graph LR
    subgraph "Input"
        BugCrowdAPI["BugCrowd API"]
    end
    
    subgraph "Processing"
        FetchSubmissions["Fetch Submissions"]
        ClassifySubmission["Classify with OpenAI"]
        StoreSubmission["Store in Database"]
        ProcessInScope["Process In-Scope Submissions"]
        GenerateResponse["Generate Response"]
    end
    
    subgraph "Output"
        CreateComment["Create Comment on BugCrowd"]
        CloseSubmission["Close Submission on BugCrowd"]
    end
    
    BugCrowdAPI --> FetchSubmissions
    FetchSubmissions --> ClassifySubmission
    ClassifySubmission --> StoreSubmission
    StoreSubmission --> ProcessInScope
    ProcessInScope --> GenerateResponse
    GenerateResponse --> CreateComment
    GenerateResponse --> CloseSubmission
    CreateComment --> BugCrowdAPI
    CloseSubmission --> BugCrowdAPI
```

Sources: [bugbounty_gpt/__main__.py:29-97]()

## Dependencies

The core components rely on several external libraries:

| Library | Purpose |
|---------|---------|
| `httpx` | HTTP client for API requests |
| `openai` | Client for OpenAI API |
| `sqlalchemy` | ORM for database operations |
| `asyncpg` | Async PostgreSQL driver |
| `pyyaml` | YAML parsing for configuration |

Sources: [pyproject.toml:14-27]()

## Summary

The core components of bugbounty-gpt work together to create an automated system for triaging and responding to bug bounty submissions. The main processing loop orchestrates the flow, while specialized handlers manage interactions with external services and the database. The configuration system provides flexibility in how the system operates.

For more detailed information about specific components, see:
- [BugCrowd API Integration](#2.1)
- [OpenAI Integration](#2.2)
- [Submission Handling](#2.3)
- [Database](#3)

---

# Page: BugCrowd API Integration

# BugCrowd API Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bugbounty_gpt/handlers/bugcrowd_api.py](bugbounty_gpt/handlers/bugcrowd_api.py)
- [tests/test_bugcrowd_api_client.py](tests/test_bugcrowd_api_client.py)
- [tests/test_comment_handling.py](tests/test_comment_handling.py)

</details>



This document describes the BugCrowd API integration in the bugbounty-gpt system. It covers how the system interacts with the BugCrowd API to fetch submissions, create comments, and update submission states. For information about how submissions are processed and classified, see [Submission Handling](#2.3).

## Overview

The BugCrowd API integration is implemented in the `BugCrowdAPI` class, which provides methods for interacting with the BugCrowd API. This class handles authentication, request formatting, and response parsing.

```mermaid
flowchart TB
    subgraph "BugCrowd API Integration"
        BugCrowdAPI["BugCrowdAPI Class"]
        FetchSubmissions["fetch_submissions()"]
        FetchSubmission["fetch_submission()"]
        CreateComment["create_comment()"]
        PatchSubmission["patch_submission()"]
    end

    subgraph "External Service"
        BugCrowdAPIService["BugCrowd API Service"]
    end

    subgraph "System Components"
        SubmissionHandler["Submission Handler"]
    end

    BugCrowdAPI --> FetchSubmissions
    BugCrowdAPI --> FetchSubmission
    BugCrowdAPI --> CreateComment
    BugCrowdAPI --> PatchSubmission

    FetchSubmissions --> BugCrowdAPIService
    FetchSubmission --> BugCrowdAPIService
    CreateComment --> BugCrowdAPIService
    PatchSubmission --> BugCrowdAPIService

    SubmissionHandler --> BugCrowdAPI
```

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:9-136]()

## Authentication and Headers

The BugCrowd API requires authentication using an API key. The API key is stored in the environment configuration and accessed through the `BUGCROWD_API_KEY` variable.

```mermaid
flowchart LR
    subgraph "Authentication Flow"
        Config["Environment Config"]
        GetHeaders["_get_headers()"]
        APIRequest["API Request"]
    end

    Config -->|"BUGCROWD_API_KEY"| GetHeaders
    GetHeaders -->|"Authorization: Token {API_KEY}"| APIRequest
    GetHeaders -->|"Accept: application/vnd.bugcrowd+json"| APIRequest
```

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:11-21](), [bugbounty_gpt/env.py]()

The `_get_headers` method generates the necessary headers for API requests:

- `Accept`: Specifies the content type, defaulting to `application/vnd.bugcrowd+json`
- `Authorization`: Includes the API key in the format `Token {BUGCROWD_API_KEY}`

For PATCH requests, an additional `Content-Type` header is set to `application/vnd.bugcrowd.v4+json`.

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:11-21](), [bugbounty_gpt/handlers/bugcrowd_api.py:125-127]()

## Core API Methods

The `BugCrowdAPI` class provides several static methods for interacting with the BugCrowd API:

| Method | Purpose | Parameters | Return Value |
|--------|---------|------------|--------------|
| `fetch_submissions` | Fetches all submissions from BugCrowd | `params`: Query parameters | List of submissions or None |
| `fetch_submission` | Fetches a specific submission | `submission_id`: ID of the submission | Submission data or None |
| `create_comment` | Creates a comment on a submission | `comment_data`: Data for the comment | Response object |
| `patch_submission` | Updates a submission | `submission_id`: ID of the submission, `data`: Update data | Response object or None |

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:50-136]()

### Fetching Submissions

The `fetch_submissions` method retrieves all submissions from BugCrowd that match the provided parameters. It uses pagination to handle large result sets, fetching up to 100 submissions per page.

```mermaid
flowchart TB
    Start["fetch_submissions(params)"] --> Initialize["Initialize variables:
    page_limit = 100
    page_offset = 0
    all_submissions = []"]
    Initialize --> FetchPage["_fetch_page(url, params, 
    page_limit, page_offset)"]
    FetchPage --> CheckResults{"submissions 
    empty?"}
    CheckResults -->|"Yes"| Return["Return all_submissions 
    or None"]
    CheckResults -->|"No"| AddSubmissions["Add submissions 
    to all_submissions"]
    AddSubmissions --> IncrementOffset["Increment page_offset 
    by page_limit"]
    IncrementOffset --> Delay["Add delay (2 seconds)"]
    Delay --> FetchPage
```

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:50-75]()

The `_fetch_page` method handles the actual API request for a single page of submissions:

1. Constructs pagination parameters
2. Makes an HTTP GET request to the BugCrowd API
3. Parses the JSON response
4. Returns the data array or an empty list if there's an error

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:23-48]()

### Fetching a Single Submission

The `fetch_submission` method retrieves a specific submission by its ID:

```mermaid
flowchart LR
    Start["fetch_submission(submission_id)"] --> Request["GET /submissions/{submission_id}"]
    Request --> CheckStatus{"status code 
    == 200?"}
    CheckStatus -->|"Yes"| ReturnData["Return JSON data"]
    CheckStatus -->|"No"| LogError["Log error"] --> ReturnNone["Return None"]
```

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:77-94]()

### Creating Comments

The `create_comment` method posts a comment to a submission:

```mermaid
flowchart LR
    Start["create_comment(comment_data)"] --> Request["POST /comments"]
    Request --> CheckStatus{"status code 
    == 201?"}
    CheckStatus -->|"Yes"| LogSuccess["Log success"]
    CheckStatus -->|"No"| LogError["Log error"]
    LogSuccess --> ReturnResponse["Return response"]
    LogError --> ReturnResponse
```

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:96-113]()

The comment data structure follows a specific format:

```json
{
  "data": {
    "type": "comment",
    "attributes": {
      "body": "Comment text",
      "visibility_scope": "everyone"
    },
    "relationships": {
      "submission": {
        "data": {
          "id": "submission_id",
          "type": "submission"
        }
      }
    }
  }
}
```

Sources: [tests/test_comment_handling.py:7-27]()

### Updating Submissions

The `patch_submission` method updates a submission's attributes:

```mermaid
flowchart LR
    Start["patch_submission(submission_id, data)"] --> Request["PATCH /submissions/{submission_id}"]
    Request --> CheckStatus{"status code 
    == 200?"}
    CheckStatus -->|"Yes"| ReturnResponse["Return response"]
    CheckStatus -->|"No"| LogError["Log error"] --> ReturnNone["Return None"]
```

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:115-136]()

## Error Handling

The BugCrowd API integration includes error handling for various scenarios:

1. **JSON Decoding Errors**: When the API response cannot be parsed as JSON
2. **HTTP Error Codes**: When the API returns non-success status codes
3. **Empty Results**: When no submissions are found

All errors are logged using the Python logging module, with appropriate error messages.

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:42-46](), [bugbounty_gpt/handlers/bugcrowd_api.py:92-94](), [bugbounty_gpt/handlers/bugcrowd_api.py:111-113](), [bugbounty_gpt/handlers/bugcrowd_api.py:132-134]()

## Rate Limiting

To avoid hitting rate limits on the BugCrowd API, the `fetch_submissions` method includes a delay of 2 seconds between API calls when paginating through results.

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:63](), [bugbounty_gpt/handlers/bugcrowd_api.py:73]()

## Integration with Submission Handler

The BugCrowd API is used by the Submission Handler to:

1. Fetch submissions for processing
2. Create comments on submissions
3. Update submission states (e.g., closing submissions)

```mermaid
sequenceDiagram
    participant SH as "Submission Handler"
    participant API as "BugCrowdAPI"
    participant BC as "BugCrowd Service"
    
    SH->>API: fetch_submissions(params)
    API->>BC: GET /submissions
    BC-->>API: Submissions data
    API-->>SH: Processed submissions
    
    SH->>API: create_comment(comment_data)
    API->>BC: POST /comments
    BC-->>API: Response
    API-->>SH: Status
    
    SH->>API: patch_submission(id, data)
    API->>BC: PATCH /submissions/{id}
    BC-->>API: Response
    API-->>SH: Status
```

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:50-136](), [tests/test_comment_handling.py:1-53]()

## Configuration

The BugCrowd API integration relies on two configuration values:

1. `API_BASE_URL`: The base URL for the BugCrowd API
2. `BUGCROWD_API_KEY`: The API key for authentication

These values are imported from the environment configuration module.

Sources: [bugbounty_gpt/handlers/bugcrowd_api.py:5](), [bugbounty_gpt/env.py]()

## Testing

The BugCrowd API integration is tested using unit tests that mock the HTTP client to simulate API responses. The tests cover:

1. Header generation
2. Fetching submissions (single page and pagination)
3. Fetching a specific submission
4. Creating comments
5. Updating submissions

Sources: [tests/test_bugcrowd_api_client.py:1-70](), [tests/test_comment_handling.py:1-53]()

---

# Page: OpenAI Integration

# OpenAI Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bugbounty_gpt/handlers/openai_handler.py](bugbounty_gpt/handlers/openai_handler.py)
- [tests/test_openai_classification.py](tests/test_openai_classification.py)

</details>



This document describes how the bugbounty-gpt system integrates with OpenAI's API to classify bug bounty submissions. The OpenAI integration is responsible for analyzing submission content and categorizing it according to predefined categories.

For information about how submissions are processed after classification, see [Submission Handling](#2.3).

## Overview

The OpenAI integration is a core component that enables automated classification of bug bounty submissions. It sends submission content to OpenAI's API and processes the response to determine the appropriate category and explanation for each submission.

```mermaid
flowchart LR
    subgraph "Submission Flow"
        submission["Submission Content"] --> openai_handler["OpenAIHandler.classify_submission()"]
        openai_handler --> openai_api["OpenAI API"]
        openai_api --> response["API Response"]
        response --> processing["Response Processing"]
        processing --> result["Classification Result"]
    end
    
    result --> |"Category & Explanation"| next_steps["Further Processing"]
```

Sources: [bugbounty_gpt/handlers/openai_handler.py:68-84]()

## Architecture

The OpenAI integration is implemented through the `OpenAIHandler` class, which provides methods for building requests, sending them to the OpenAI API, and processing the responses.

```mermaid
classDiagram
    class OpenAIHandler {
        +classify_submission(submission_content) async
        -_build_request_data(submission_content)
        -_handle_response(response)
        -_handle_response_error(error)
        -_classifications_sanitization(input_string)
    }
    
    OpenAIHandler --> "OpenAI API" : sends requests to
    OpenAIHandler --> "VALID_CATEGORIES" : validates against
    OpenAIHandler --> "DEFAULT_CATEGORY" : fallback to
    OpenAIHandler --> "OPENAI_PROMPT" : uses
    OpenAIHandler --> "OPENAI_MODEL" : uses
```

Sources: [bugbounty_gpt/handlers/openai_handler.py:9-84]()

## Configuration

The OpenAI integration relies on several configuration parameters defined in the environment:

| Parameter | Description | Source |
|-----------|-------------|--------|
| `OPENAI_PROMPT` | System prompt that guides the AI's classification | env.py |
| `OPENAI_MODEL` | The OpenAI model to use (e.g., "gpt-3.5-turbo") | env.py |
| `VALID_CATEGORIES` | List of valid classification categories | env.py |
| `DEFAULT_CATEGORY` | Fallback category when classification fails | env.py |

Sources: [bugbounty_gpt/handlers/openai_handler.py:5]()

## Classification Process

The classification process involves several steps:

1. Building the request data with the submission content
2. Sending the request to OpenAI's API
3. Processing the response to extract the category and explanation
4. Sanitizing and validating the category
5. Returning the classification result

```mermaid
sequenceDiagram
    participant Client as "Client Code"
    participant Handler as "OpenAIHandler"
    participant API as "OpenAI API"
    
    Client->>Handler: classify_submission(content)
    Handler->>Handler: _build_request_data(content)
    Handler->>API: openai.ChatCompletion.create()
    API-->>Handler: response
    Handler->>Handler: _handle_response(response)
    Handler->>Handler: _classifications_sanitization(judgement)
    alt Valid Category
        Handler-->>Client: (sanitized_judgement, explanation)
    else Invalid Category
        Handler-->>Client: (DEFAULT_CATEGORY, explanation)
    end
    
    Note over Handler,API: Error handling at each step
```

Sources: [bugbounty_gpt/handlers/openai_handler.py:68-84](), [bugbounty_gpt/handlers/openai_handler.py:49-66]()

### Request Building

The `_build_request_data` method constructs the request payload for the OpenAI API:

```mermaid
flowchart LR
    content["Submission Content"] --> build["_build_request_data()"]
    build --> request["Request Data"]
    
    subgraph "Request Data Structure"
        model["model: OPENAI_MODEL"]
        temp["temperature: 0"]
        tokens["max_tokens: 512"]
        messages["messages: [system, user]"]
    end
    
    request --> model
    request --> temp
    request --> tokens
    request --> messages
```

Sources: [bugbounty_gpt/handlers/openai_handler.py:20-36]()

### Response Handling

The response from OpenAI is processed to extract the classification category and explanation:

```mermaid
flowchart TD
    response["OpenAI Response"] --> handle["_handle_response()"]
    
    subgraph "Response Processing"
        extract["Extract response_text"]
        split["Split into judgement and explanation"]
        sanitize["Sanitize judgement"]
        validate["Validate category"]
    end
    
    handle --> extract
    extract --> split
    split --> sanitize
    sanitize --> validate
    
    validate -->|"Valid Category"| valid["Return (sanitized_judgement, explanation)"]
    validate -->|"Invalid Category"| invalid["Return (DEFAULT_CATEGORY, explanation)"]
    
    error["Exception"] --> handle_error["_handle_response_error()"]
    handle_error --> default["Return (DEFAULT_CATEGORY, error_message)"]
```

Sources: [bugbounty_gpt/handlers/openai_handler.py:49-66](), [bugbounty_gpt/handlers/openai_handler.py:38-47]()

### Category Sanitization

The `_classifications_sanitization` method ensures consistent formatting of category names:

1. Removes leading and trailing spaces
2. Replaces spaces with underscores
3. Converts to uppercase

This standardization allows for reliable category matching against the `VALID_CATEGORIES` list.

Sources: [bugbounty_gpt/handlers/openai_handler.py:10-18]()

## Error Handling

The OpenAI integration includes robust error handling to manage various failure scenarios:

1. API request failures
2. Response parsing errors
3. Invalid category classifications

In all error cases, the system falls back to the `DEFAULT_CATEGORY` and provides an appropriate error message.

Sources: [bugbounty_gpt/handlers/openai_handler.py:38-47](), [bugbounty_gpt/handlers/openai_handler.py:83-84]()

## Rate Limiting

The integration includes a basic rate limiting mechanism to prevent exceeding OpenAI's API rate limits:

```python
time.sleep(5)  # Consider replacing with a more robust rate-limiting strategy
```

This simple delay helps manage API request frequency, though as noted in the code comment, a more sophisticated approach may be beneficial for production use.

Sources: [bugbounty_gpt/handlers/openai_handler.py:77]()

## Asynchronous Operation

The `classify_submission` method operates asynchronously, allowing the system to handle multiple submissions efficiently:

```mermaid
flowchart LR
    subgraph "Asynchronous Processing"
        classify["classify_submission()"] --> loop["Get running asyncio loop"]
        loop --> executor["Run in executor"]
        executor --> api["OpenAI API call"]
        api --> handle["_handle_response()"]
        handle --> result["Classification Result"]
    end
```

The method uses `asyncio.get_running_loop()` and `run_in_executor()` to make the synchronous OpenAI API call non-blocking.

Sources: [bugbounty_gpt/handlers/openai_handler.py:68-84]()

## Testing

The OpenAI integration includes comprehensive unit tests that verify:

1. Category sanitization
2. Request data building
3. Response handling for successful cases
4. Response handling for error cases
5. End-to-end classification functionality

These tests ensure the reliability of the classification process and proper error handling.

Sources: [tests/test_openai_classification.py:1-68]()

---

# Page: Submission Handling

# Submission Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bugbounty_gpt/__main__.py](bugbounty_gpt/__main__.py)
- [bugbounty_gpt/handlers/submission_handler.py](bugbounty_gpt/handlers/submission_handler.py)
- [tests/test_comment_handling.py](tests/test_comment_handling.py)

</details>



This page documents the submission handling process in the bugbounty-gpt system, focusing on how bug bounty submissions from BugCrowd are processed, classified, and responded to. The submission handling component is a core part of the system that bridges the BugCrowd API integration ([BugCrowd API Integration](#2.1)) with the OpenAI classification system ([OpenAI Integration](#2.2)).

## Overview

The submission handling process involves fetching new submissions from BugCrowd, classifying them using OpenAI, storing them in the database, and then processing them based on their classification. For submissions that fall into specific response categories, the system generates appropriate comments and closes the submissions.

```mermaid
flowchart TD
    subgraph "Submission Processing Flow"
        FetchNew["Fetch New Submissions"]
        Classify["Classify with OpenAI"]
        Store["Store in Database"]
        ProcessInScope["Process In-Scope Submissions"]
        GenerateComment["Generate Comment Text"]
        CreateComment["Create Comment on BugCrowd"]
        CloseSubmission["Close Submission"]
    end

    FetchNew --> Classify
    Classify --> Store
    Store --> ProcessInScope
    ProcessInScope --> GenerateComment
    GenerateComment --> CreateComment
    CreateComment --> CloseSubmission
```

Sources: [bugbounty_gpt/__main__.py:29-97](), [bugbounty_gpt/handlers/submission_handler.py:8-158]()

## BugCrowdSubmission Class

The `BugCrowdSubmission` class is the central component for handling individual submissions. It encapsulates all operations that can be performed on a submission, including checking its status, creating comments, and closing the submission.

```mermaid
classDiagram
    class "BugCrowdSubmission" {
        +String submission_id
        +Enum classification
        +String reasoning
        +is_submission_new()
        +close_submission()
        +create_comment()
        +generate_comment_text()
        +assign_to_user()
    }
    
    "BugCrowdSubmission" --> "BugCrowdAPI": uses
    "BugCrowdSubmission" --> "RESPONSES": references
```

Sources: [bugbounty_gpt/handlers/submission_handler.py:8-158]()

### Key Methods

The `BugCrowdSubmission` class provides several key methods for handling submissions:

| Method | Purpose |
|--------|---------|
| `is_submission_new()` | Checks if the submission is in the "new" state on BugCrowd |
| `close_submission()` | Closes the submission by setting its state to "not_applicable" |
| `create_comment(comment_body)` | Creates a comment on the submission with the specified text |
| `generate_comment_text()` | Generates a response text based on the submission's classification |
| `assign_to_user(user_id)` | Assigns the submission to a specific user |

Sources: [bugbounty_gpt/handlers/submission_handler.py:64-157]()

## Submission Processing Workflow

The submission processing workflow consists of two main phases: fetching and processing new submissions, and handling in-scope submissions.

```mermaid
sequenceDiagram
    participant "Main Loop" as Main
    participant "process_new_submissions()" as PNS
    participant "BugCrowdAPI" as API
    participant "OpenAIHandler" as OAI
    participant "Database" as DB
    participant "process_in_scope_submissions()" as PIS
    participant "BugCrowdSubmission" as BCS

    Main->>PNS: Call every minute
    PNS->>API: fetch_submissions()
    API-->>PNS: Return submissions
    
    loop For each submission
        PNS->>OAI: classify_submission()
        OAI-->>PNS: Return classification and reasoning
        PNS->>DB: insert_submission()
    end
    
    Main->>PIS: Call every minute
    PIS->>DB: fetch_submission_by_state_and_classification()
    DB-->>PIS: Return in-scope submissions
    
    loop For each in-scope submission
        PIS->>BCS: Create BugCrowdSubmission instance
        PIS->>BCS: is_submission_new()
        BCS-->>PIS: Return submission status
        
        alt If submission is new
            PIS->>BCS: generate_comment_text()
            BCS-->>PIS: Return comment text
            PIS->>BCS: create_comment()
            PIS->>BCS: close_submission()
            PIS->>DB: update_submission_state()
        else If submission is not new
            PIS->>DB: update_submission_state()
        end
    end
```

Sources: [bugbounty_gpt/__main__.py:29-97]()

### Fetching and Processing New Submissions

The `process_new_submissions()` function fetches new, non-duplicate submissions from BugCrowd and processes them:

1. Fetch submissions using the BugCrowd API with specific filters
2. For each submission:
   - Check if it has been seen before
   - Extract submission ID, user ID, and content
   - Classify the submission using OpenAI
   - Store the submission data in the database

Sources: [bugbounty_gpt/__main__.py:29-58]()

### Processing In-Scope Submissions

The `process_in_scope_submissions()` function handles submissions that have been classified into specific response categories:

1. Fetch submissions with state "NEW" and classifications in the configured response categories
2. For each submission:
   - Create a `BugCrowdSubmission` instance
   - Check if the submission is still in the "new" state on BugCrowd
   - Generate a comment based on the classification
   - Create the comment on BugCrowd
   - Close the submission
   - Update the submission state in the database

Sources: [bugbounty_gpt/__main__.py:60-82]()

## Comment Generation and Handling

The system generates comments for submissions based on their classification. The comment text is retrieved from the `RESPONSES` configuration, which maps classification names to appropriate response texts.

```mermaid
flowchart LR
    subgraph "Comment Generation Process"
        Classification["Classification"]
        RESPONSES["RESPONSES Config"]
        CommentText["Comment Text"]
        BugCrowd["BugCrowd API"]
    end
    
    Classification -->|"classification.name"| RESPONSES
    RESPONSES -->|"Lookup response text"| CommentText
    CommentText -->|"Format with greeting"| BugCrowd
```

Sources: [bugbounty_gpt/handlers/submission_handler.py:144-157](), [bugbounty_gpt/handlers/submission_handler.py:129-143]()

### Comment Creation

The `create_comment()` method handles the creation of comments on BugCrowd:

1. Prepare the comment data with the specified text and visibility scope
2. Send the comment data to the BugCrowd API
3. Handle any errors that occur during comment creation

The method includes robust error handling for various HTTP status codes (400, 404, 409) that might be returned by the BugCrowd API.

Sources: [bugbounty_gpt/handlers/submission_handler.py:91-143](), [tests/test_comment_handling.py:7-53]()

## Submission Closing

After creating a comment, the system closes the submission by setting its state to "not_applicable". This is done through the `close_submission()` method, which sends a PATCH request to the BugCrowd API.

```mermaid
flowchart TD
    subgraph "Submission Closing Process"
        PrepareData["Prepare Data\n{state: not_applicable}"]
        PatchSubmission["PATCH Submission"]
        CheckResponse["Check Response"]
        HandleError["Handle Error"]
    end
    
    PrepareData --> PatchSubmission
    PatchSubmission --> CheckResponse
    CheckResponse -->|"Status != 200"| HandleError
```

Sources: [bugbounty_gpt/handlers/submission_handler.py:74-89]()

## Integration with Main Loop

The submission handling process is integrated into the main loop of the application, which runs continuously:

1. Fetch and process new submissions
2. Process in-scope submissions
3. Wait for a specified interval (1 minute)
4. Repeat

This ensures that new submissions are regularly processed and responded to in a timely manner.

Sources: [bugbounty_gpt/__main__.py:84-97]()

## Data Flow

The following diagram illustrates the data flow through the submission handling system:

```mermaid
flowchart TD
    subgraph "External Systems"
        BugCrowdAPI["BugCrowd API"]
        OpenAIAPI["OpenAI API"]
    end
    
    subgraph "Internal Components"
        MainLoop["Main Loop"]
        ProcessNew["process_new_submissions()"]
        ProcessInScope["process_in_scope_submissions()"]
        BugCrowdSubmission["BugCrowdSubmission Class"]
        Database[(PostgreSQL Database)]
    end
    
    MainLoop -->|"Call"| ProcessNew
    MainLoop -->|"Call"| ProcessInScope
    
    ProcessNew -->|"Fetch submissions"| BugCrowdAPI
    BugCrowdAPI -->|"Return submissions"| ProcessNew
    ProcessNew -->|"Classify"| OpenAIAPI
    OpenAIAPI -->|"Return classification"| ProcessNew
    ProcessNew -->|"Store"| Database
    
    ProcessInScope -->|"Fetch in-scope"| Database
    Database -->|"Return submissions"| ProcessInScope
    ProcessInScope -->|"Create"| BugCrowdSubmission
    BugCrowdSubmission -->|"Check status"| BugCrowdAPI
    BugCrowdSubmission -->|"Create comment"| BugCrowdAPI
    BugCrowdSubmission -->|"Close submission"| BugCrowdAPI
    ProcessInScope -->|"Update state"| Database
```

Sources: [bugbounty_gpt/__main__.py:29-97](), [bugbounty_gpt/handlers/submission_handler.py:8-158]()

## Configuration Dependencies

The submission handling system relies on several configuration parameters:

| Parameter | Purpose |
|-----------|---------|
| `USER_ID` | The ID of the user to assign submissions to |
| `FILTER_PROGRAM` | The BugCrowd program to filter submissions by |
| `RESPONSE_CATEGORIES` | Categories of submissions that should receive responses |
| `RESPONSES` | Mapping of classification names to response texts |

These parameters are loaded from the configuration system, which is documented in the [Configuration](#1.2) page.

Sources: [bugbounty_gpt/__main__.py:9](), [bugbounty_gpt/handlers/submission_handler.py:2]()

## Error Handling

The submission handling system includes robust error handling for various scenarios:

1. Failed API requests to BugCrowd
2. Invalid or missing response templates
3. Submissions that have been updated out-of-band

Errors are logged with appropriate severity levels, and the system is designed to continue processing other submissions even if one fails.

Sources: [bugbounty_gpt/handlers/submission_handler.py:117-143](), [tests/test_comment_handling.py:38-53]()

---

# Page: Database

# Database

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bugbounty_gpt/db/db_handler.py](bugbounty_gpt/db/db_handler.py)
- [bugbounty_gpt/db/models.py](bugbounty_gpt/db/models.py)

</details>



This page provides an overview of the database system used in the bugbounty-gpt application. It covers the database structure, models, operations, and how the application interacts with the database to store and retrieve submission data.

For information about database migrations, see [Database Migrations](#3.3).

## Database Overview

The bugbounty-gpt application uses a PostgreSQL database to store information about bug bounty submissions. The database serves as a persistent storage layer that tracks submissions, their classifications, and their processing states.

```mermaid
graph TD
    subgraph "Database System"
        DB[("PostgreSQL Database")]
        Models["Database Models"]
        DBHandler["Database Handler"]
    end
    
    subgraph "Application Components"
        MainLoop["Main Processing Loop"]
        SubmissionHandler["Submission Handler"]
    end
    
    MainLoop --> SubmissionHandler
    SubmissionHandler --> DBHandler
    DBHandler --> DB
    Models --> DB
    
    subgraph "Database Models"
        SubmissionModel["Submission"]
        ReportCategoryEnum["ReportCategory Enum"]
        SubmissionStateEnum["SubmissionState Enum"]
    end
    
    Models --> SubmissionModel
    Models --> ReportCategoryEnum
    Models --> SubmissionStateEnum
```

Sources: [bugbounty_gpt/db/models.py:1-54](), [bugbounty_gpt/db/db_handler.py:1-87]()

## Database Models

The database schema is defined using SQLAlchemy's ORM (Object-Relational Mapping) system. The primary model is the `Submission` class, which represents bug bounty submissions.

### Submission Model

The `Submission` model is the core data structure that stores information about bug bounty reports:

```mermaid
classDiagram
    class Submission {
        +String submission_id
        +String user_id
        +Text reasoning
        +ReportCategory classification
        +SubmissionState submission_state
        +DateTime created_at
        +DateTime updated_at
    }
    
    class ReportCategory {
        <<enumeration>>
        +VALID_CATEGORIES from config
    }
    
    class SubmissionState {
        <<enumeration>>
        +NEW
        +UPDATED_OUT_OF_BAND
        +UPDATED
    }
    
    Submission --> ReportCategory : has
    Submission --> SubmissionState : has
```

Sources: [bugbounty_gpt/db/models.py:33-54]()

### Enumerations

The database uses two key enumerations:

1. **ReportCategory**: Dynamically generated from the `VALID_CATEGORIES` configuration setting. This enum represents the possible classifications for a submission.

2. **SubmissionState**: Represents the processing state of a submission with the following values:
   - `NEW`: A newly received submission that hasn't been processed
   - `UPDATED_OUT_OF_BAND`: A submission that was updated outside the normal flow
   - `UPDATED`: A submission that has been processed and updated

Sources: [bugbounty_gpt/db/models.py:26-32]()

## Database Operations

The database operations are encapsulated in the `db_handler.py` module, which provides functions for interacting with the database. These operations are implemented as asynchronous functions using SQLAlchemy's async capabilities.

### Key Database Operations

| Operation | Function | Description |
|-----------|----------|-------------|
| Insert Submission | `insert_submission` | Adds a new submission to the database if it doesn't already exist |
| Update Submission State | `update_submission_state` | Updates the state of an existing submission |
| Fetch by State and Classification | `fetch_submission_by_state_and_classification` | Retrieves submissions matching specific states and classifications |
| Fetch by ID | `fetch_submission_by_id` | Retrieves a specific submission by its ID |

```mermaid
sequenceDiagram
    participant App as "Application"
    participant DBHandler as "Database Handler"
    participant DB as "PostgreSQL Database"
    
    App->>DBHandler: insert_submission(submission_data)
    DBHandler->>DB: Check if submission exists
    DB-->>DBHandler: Return existing submission (if any)
    
    alt Submission doesn't exist
        DBHandler->>DB: Create new submission
        DB-->>DBHandler: Confirm creation
    else Submission exists
        DBHandler-->>App: Skip insertion (log message)
    end
    
    App->>DBHandler: update_submission_state(id, new_state)
    DBHandler->>DB: Find submission by ID
    DB-->>DBHandler: Return submission
    DBHandler->>DB: Update submission state
    DB-->>DBHandler: Confirm update
    DBHandler-->>App: Return success/failure
    
    App->>DBHandler: fetch_submission_by_state_and_classification(states, classifications)
    DBHandler->>DB: Query submissions with filters
    DB-->>DBHandler: Return matching submissions
    DBHandler-->>App: Return submissions list
```

Sources: [bugbounty_gpt/db/db_handler.py:20-87]()

### Submission Insertion

The `insert_submission` function checks if a submission already exists in the database before inserting it. This prevents duplicate entries:

```
1. Check if submission exists using _find_submission_by_id
2. If submission exists, log and skip
3. If submission doesn't exist, create a new Submission object and commit to database
```

Sources: [bugbounty_gpt/db/db_handler.py:20-38]()

### State Management

The `update_submission_state` function allows the application to track the processing status of submissions:

```
1. Find the submission by ID
2. If found, update its submission_state attribute
3. Commit the changes to the database
4. Return success/failure status
```

Sources: [bugbounty_gpt/db/db_handler.py:40-57]()

### Query Operations

The database handler provides functions to query submissions based on various criteria:

- `_find_submission_by_id`: Internal helper function to find a submission by ID
- `fetch_submission_by_state_and_classification`: Retrieves submissions matching specific states and classifications
- `fetch_submission_by_id`: Public function to retrieve a submission by ID

Sources: [bugbounty_gpt/db/db_handler.py:7-18](), [bugbounty_gpt/db/db_handler.py:59-87]()

## Database Interaction Flow

The following diagram illustrates how the application interacts with the database during the submission processing workflow:

```mermaid
flowchart TD
    subgraph "Application Flow"
        FetchFromBugCrowd["Fetch Submissions from BugCrowd"]
        ClassifyWithOpenAI["Classify with OpenAI"]
        StoreInDB["Store in Database"]
        ProcessSubmissions["Process Submissions"]
        UpdateState["Update Submission State"]
    end
    
    subgraph "Database Operations"
        InsertSubmission["insert_submission()"]
        UpdateSubmissionState["update_submission_state()"]
        FetchByStateAndClass["fetch_submission_by_state_and_classification()"]
    end
    
    subgraph "Database"
        SubmissionTable[("Submission Table")]
    end
    
    FetchFromBugCrowd --> ClassifyWithOpenAI
    ClassifyWithOpenAI --> StoreInDB
    StoreInDB --> InsertSubmission
    InsertSubmission --> SubmissionTable
    
    ProcessSubmissions --> FetchByStateAndClass
    FetchByStateAndClass --> SubmissionTable
    ProcessSubmissions --> UpdateState
    UpdateState --> UpdateSubmissionState
    UpdateSubmissionState --> SubmissionTable
```

Sources: [bugbounty_gpt/db/db_handler.py:1-87](), [bugbounty_gpt/db/models.py:1-54]()

## Database Connection Management

The database connection is managed at the application level, with session objects being passed to the database handler functions. This approach allows for efficient connection pooling and transaction management.

The application uses SQLAlchemy's async session capabilities to perform database operations asynchronously, which helps maintain application responsiveness while waiting for database operations to complete.

Sources: [bugbounty_gpt/db/db_handler.py:7-87]()

## Summary

The database system in bugbounty-gpt provides:

1. **Persistence**: Stores bug bounty submissions and their processing state
2. **Classification tracking**: Records the AI-generated classification of each submission
3. **State management**: Tracks the processing state of each submission
4. **Efficient querying**: Allows filtering submissions by state and classification

The database design follows a simple but effective schema that supports the application's core functionality of processing and responding to bug bounty submissions.

---

# Page: Database Models

# Database Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bugbounty_gpt/db/models.py](bugbounty_gpt/db/models.py)
- [tests/test_database_and_models.py](tests/test_database_and_models.py)

</details>



This document describes the database models used in the bugbounty-gpt system. It covers the core data structures that represent submissions and their classifications in the database. For information about database operations and how the system interacts with these models, see [Database Operations](#3.2). For details on database migrations, see [Database Migrations](#3.3).

## Overview

The bugbounty-gpt system uses SQLAlchemy ORM (Object-Relational Mapping) to define and interact with the database models. The models are defined in the `models.py` file and represent the core data structures used to store bug bounty submissions and their classifications.

Sources: [bugbounty_gpt/db/models.py:1-55]()

## Database Model Structure

The database model structure consists of a single table `submission` and two enum types: `ReportCategory` and `SubmissionState`.

```mermaid
classDiagram
    class "Submission" {
        +String submission_id (PK)
        +String user_id
        +Text reasoning
        +ReportCategory classification
        +SubmissionState submission_state
        +DateTime created_at
        +DateTime updated_at
    }
    
    class "ReportCategory" {
        <<enumeration>>
        +POLICY_OR_CONTENT_COMPLAINTS
        +Other categories from config
    }
    
    class "SubmissionState" {
        <<enumeration>>
        +NEW = 1
        +UPDATED_OUT_OF_BAND = 2
        +UPDATED = 3
    }
    
    Submission --> "1" ReportCategory : classification
    Submission --> "1" SubmissionState : submission_state
```

Sources: [bugbounty_gpt/db/models.py:28-54]()

## Submission Model

The `Submission` class is the primary database model that represents a bug bounty submission. It is defined using SQLAlchemy's declarative base and maps to the `submission` table in the database.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| submission_id | String(100) | Primary key, unique identifier for the submission |
| user_id | String(100) | Identifier for the user who created the submission |
| reasoning | Text | Reasoning text for the submission classification |
| classification | ReportCategory | Classification of the report using the ReportCategory enum |
| submission_state | SubmissionState | State of the submission using the SubmissionState enum |
| created_at | DateTime | Timestamp of submission creation (auto-generated) |
| updated_at | DateTime | Timestamp of the last update (auto-updated) |

Sources: [bugbounty_gpt/db/models.py:33-54]()

## Enum Types

The system uses two enum types to represent the state and classification of submissions.

### ReportCategory Enum

The `ReportCategory` enum is dynamically generated from the `VALID_CATEGORIES` configuration defined in the environment settings. This allows the system to be flexible and adapt to different categorization schemes without changing the database schema.

The enum is created using helper functions:

1. `_sanitize_category_name`: Converts category names to uppercase with underscores
2. `_create_enum_members`: Creates a dictionary mapping sanitized names to original category names

```mermaid
flowchart LR
    subgraph "Configuration"
        VALID_CATEGORIES["VALID_CATEGORIES from env.py"]
    end
    
    subgraph "Helper Functions"
        sanitize["_sanitize_category_name()"]
        create_members["_create_enum_members()"]
    end
    
    subgraph "Enum Creation"
        ReportCategory["ReportCategory Enum"]
    end
    
    VALID_CATEGORIES --> create_members
    create_members --> sanitize
    create_members --> ReportCategory
```

Sources: [bugbounty_gpt/db/models.py:8-26]()

### SubmissionState Enum

The `SubmissionState` enum represents the current state of a submission in the system's workflow. It has three possible values:

1. `NEW` (1): A newly created submission
2. `UPDATED_OUT_OF_BAND` (2): A submission that was updated outside the normal flow
3. `UPDATED` (3): A submission that has been processed and updated

Sources: [bugbounty_gpt/db/models.py:28-31]()

## Database Model Integration

The database models integrate with the rest of the system as follows:

```mermaid
flowchart TB
    subgraph "Configuration"
        env["env.py (VALID_CATEGORIES)"]
    end
    
    subgraph "Database Models"
        models["models.py"]
        Base["SQLAlchemy Base"]
        Submission["Submission Model"]
        ReportCategory["ReportCategory Enum"]
        SubmissionState["SubmissionState Enum"]
    end
    
    subgraph "Database Operations"
        db_ops["Database Operations"]
    end
    
    subgraph "Migrations"
        alembic["Alembic Migrations"]
    end
    
    env --> models
    models --> Base
    Base --> Submission
    models --> ReportCategory
    models --> SubmissionState
    Submission --> ReportCategory
    Submission --> SubmissionState
    
    Base --> alembic
    Submission --> db_ops
```

Sources: [bugbounty_gpt/db/models.py:1-55]()

## Testing

The database models are tested in the `test_database_and_models.py` file, which includes tests for:

1. Sanitizing category names
2. Creating enum members
3. Verifying the ReportCategory enum values

These tests ensure that the helper functions work correctly and that the enum types are properly created.

Sources: [tests/test_database_and_models.py:1-13]()

## Summary

The database models in bugbounty-gpt provide a simple but flexible structure for storing and tracking bug bounty submissions. The key features include:

1. A single `Submission` table that stores all relevant information about a submission
2. A dynamically generated `ReportCategory` enum that adapts to the categories defined in the configuration
3. A `SubmissionState` enum that tracks the processing state of each submission

This design allows the system to efficiently store and retrieve submission data while maintaining the flexibility to adapt to different categorization schemes.

---

# Page: Database Operations

# Database Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bugbounty_gpt/__main__.py](bugbounty_gpt/__main__.py)
- [bugbounty_gpt/db/db_handler.py](bugbounty_gpt/db/db_handler.py)

</details>



This document describes the database operations in the bugbounty-gpt system, focusing on how the application interacts with the PostgreSQL database to store and retrieve submission data. For information about database models and their structure, see [Database Models](#3.1). For details on database migrations, see [Database Migrations](#3.3).

## Overview

The database operations in bugbounty-gpt are primarily handled by the `db_handler.py` module, which provides a set of asynchronous functions for common database operations such as inserting new submissions, updating submission states, and fetching submissions based on specific criteria.

```mermaid
flowchart TB
    subgraph "Application Layer"
        MainLoop["Main Loop (__main__.py)"]
        SubmissionHandler["Submission Handler"]
    end
    
    subgraph "Database Layer"
        DBHandler["db_handler.py"]
        Models["models.py"]
        SQLAlchemy["SQLAlchemy ORM"]
    end
    
    subgraph "Database"
        PostgreSQL[(PostgreSQL Database)]
    end
    
    MainLoop --> |"insert_submission()\nupdate_submission_state()\nfetch_submission_by_state_and_classification()"| DBHandler
    SubmissionHandler --> |"fetch_submission_by_id()"| DBHandler
    DBHandler --> |"Uses"| Models
    DBHandler --> |"Executes queries via"| SQLAlchemy
    SQLAlchemy --> |"Connects to"| PostgreSQL
```

Sources: [bugbounty_gpt/db/db_handler.py:1-88](), [bugbounty_gpt/__main__.py:1-101]()

## Database Connection Setup

The database connection is established in the main module using SQLAlchemy's async engine. The application uses a session factory pattern to create database sessions as needed.

```mermaid
sequenceDiagram
    participant Main as "__main__.py"
    participant SQLAlchemy
    participant DB as "PostgreSQL Database"
    
    Main->>SQLAlchemy: create_async_engine(SQLALCHEMY_URL)
    SQLAlchemy-->>Main: Return engine
    Main->>SQLAlchemy: sessionmaker(bind=engine, class_=AsyncSession)
    SQLAlchemy-->>Main: Return SessionLocal factory
    Main->>Main: async with SessionLocal() as session
    Main->>SQLAlchemy: Execute database operations
    SQLAlchemy->>DB: Execute SQL queries
    DB-->>SQLAlchemy: Return results
    SQLAlchemy-->>Main: Return ORM objects
```

Sources: [bugbounty_gpt/__main__.py:17-25]()

## Core Database Operations

The `db_handler.py` module provides the following key operations:

### 1. Finding Submissions by ID

The `_find_submission_by_id` function is an internal helper that retrieves a submission by its ID:

```python
async def _find_submission_by_id(session, submission_id):
    stmt = select(Submission).filter(Submission.submission_id == submission_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

Sources: [bugbounty_gpt/db/db_handler.py:7-18]()

### 2. Inserting New Submissions

The `insert_submission` function adds a new submission to the database if it doesn't already exist:

```mermaid
flowchart TD
    Start["insert_submission(session, submission_data)"] --> CheckExists["Check if submission exists"]
    CheckExists --> Exists{"Submission exists?"}
    Exists -->|"Yes"| Skip["Log and skip insertion"]
    Exists -->|"No"| Insert["Create Submission object\nAdd to session\nCommit transaction"]
    Insert --> End
    Skip --> End
```

Sources: [bugbounty_gpt/db/db_handler.py:20-38]()

### 3. Updating Submission State

The `update_submission_state` function changes the state of an existing submission:

```mermaid
flowchart TD
    Start["update_submission_state(session, submission_id, new_state)"] --> Find["Find submission by ID"]
    Find --> Exists{"Submission exists?"}
    Exists -->|"Yes"| Update["Update submission state\nCommit transaction\nReturn True"]
    Exists -->|"No"| Fail["Return False"]
    Update --> End
    Fail --> End
```

Sources: [bugbounty_gpt/db/db_handler.py:40-57]()

### 4. Fetching Submissions by State and Classification

The `fetch_submission_by_state_and_classification` function retrieves submissions that match specific states and classifications:

```mermaid
flowchart TD
    Start["fetch_submission_by_state_and_classification(session, states, classifications)"] --> Query["Create query with filters:\n- submission_state in states\n- classification in classifications"]
    Query --> Execute["Execute query"]
    Execute --> Return["Return all matching submissions"]
```

Sources: [bugbounty_gpt/db/db_handler.py:59-75]()

### 5. Fetching Submission by ID

The `fetch_submission_by_id` function is a public wrapper around the internal `_find_submission_by_id` function:

```mermaid
flowchart TD
    Start["fetch_submission_by_id(session, submission_id)"] --> Query["Query submission by ID"]
    Query --> Return["Return submission or None"]
```

Sources: [bugbounty_gpt/db/db_handler.py:77-87]()

## Database Usage in the Application

The main application uses these database operations in two primary workflows:

### 1. Processing New Submissions

```mermaid
sequenceDiagram
    participant Main as "__main__.py"
    participant BugCrowdAPI
    participant OpenAIHandler
    participant DBHandler as "db_handler"
    participant DB as "Database"
    
    Main->>BugCrowdAPI: fetch_submissions(params)
    BugCrowdAPI-->>Main: Return submissions
    loop For each submission
        Main->>Main: Check if submission already seen
        Main->>OpenAIHandler: classify_submission(content)
        OpenAIHandler-->>Main: Return classification and reasoning
        Main->>DBHandler: insert_submission(session, submission_data)
        DBHandler->>DB: Check if submission exists
        DB-->>DBHandler: Return result
        alt Submission does not exist
            DBHandler->>DB: Insert new submission
        end
        DBHandler-->>Main: Operation complete
    end
```

Sources: [bugbounty_gpt/__main__.py:29-58]()

### 2. Processing In-Scope Submissions

```mermaid
sequenceDiagram
    participant Main as "__main__.py"
    participant DBHandler as "db_handler"
    participant DB as "Database"
    participant Submission as "BugCrowdSubmission"
    
    Main->>DBHandler: fetch_submission_by_state_and_classification(session, states, classifications)
    DBHandler->>DB: Query submissions
    DB-->>DBHandler: Return matching submissions
    DBHandler-->>Main: Return submissions
    
    loop For each submission
        Main->>Submission: Create BugCrowdSubmission object
        Main->>Submission: is_submission_new()
        Submission-->>Main: Return status
        
        alt Submission is new
            Main->>Submission: generate_comment_text()
            Submission-->>Main: Return comment text
            
            alt Comment text exists
                Main->>Submission: create_comment(comment_body)
                Main->>Submission: close_submission()
                Main->>DBHandler: update_submission_state(session, submission_id, UPDATED)
                DBHandler->>DB: Update submission state
            end
        else Submission is not new
            Main->>DBHandler: update_submission_state(session, submission_id, UPDATED_OUT_OF_BAND)
            DBHandler->>DB: Update submission state
        end
    end
```

Sources: [bugbounty_gpt/__main__.py:60-82]()

## Database Session Management

The application uses SQLAlchemy's async session management with context managers to ensure proper handling of database connections:

```python
async with SessionLocal() as session:
    # Database operations
    # Session is automatically closed when the block exits
```

This pattern is used consistently throughout the application to ensure that database connections are properly managed and released.

Sources: [bugbounty_gpt/__main__.py:39-58](), [bugbounty_gpt/__main__.py:65-82]()

## Database Operation Parameters

| Function | Parameters | Return Value | Description |
|----------|------------|--------------|-------------|
| `_find_submission_by_id` | `session`, `submission_id` | Submission object or None | Internal helper to find a submission by ID |
| `insert_submission` | `session`, `submission_data` | None | Inserts a new submission if it doesn't exist |
| `update_submission_state` | `session`, `submission_id`, `new_state` | Boolean | Updates a submission's state |
| `fetch_submission_by_state_and_classification` | `session`, `states`, `classifications` | List of Submission objects | Fetches submissions matching criteria |
| `fetch_submission_by_id` | `session`, `submission_id` | Submission object or None | Public function to find a submission by ID |

Sources: [bugbounty_gpt/db/db_handler.py:7-87]()

## Error Handling

The database operations include basic error handling through logging and return values. For example, `update_submission_state` returns `True` if the update was successful and `False` otherwise. The application logs database operations for debugging purposes.

Sources: [bugbounty_gpt/db/db_handler.py:5-87]()

## Summary

The database operations in bugbounty-gpt provide a clean, asynchronous interface for interacting with the PostgreSQL database. The operations are designed to be simple and focused, handling common tasks such as inserting new submissions, updating submission states, and fetching submissions based on specific criteria. The application uses SQLAlchemy's async session management to ensure proper handling of database connections.

---

# Page: Database Migrations

# Database Migrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [alembic.ini](alembic.ini)
- [alembic/env.py](alembic/env.py)
- [bugbounty_gpt/db/migrate.py](bugbounty_gpt/db/migrate.py)

</details>



This document describes the database migration system used in the bugbounty-gpt project. It covers how migrations are managed using Alembic, the configuration of the migration environment, and the automated migration process. For information about database models, see [Database Models](#3.1), and for database operations, see [Database Operations](#3.2).

## Overview of Database Migrations

The bugbounty-gpt project uses Alembic, a lightweight database migration tool for SQLAlchemy, to manage database schema changes. Alembic provides a way to incrementally update the database schema while preserving existing data.

```mermaid
graph TD
    subgraph "Migration Components"
        A["alembic.ini"] --> B["alembic/env.py"]
        B --> C["Migration Scripts"]
        D["bugbounty_gpt/db/migrate.py"] --> B
    end
    
    subgraph "Database"
        E["Models"] --> F["Database Schema"]
        C --> F
    end
    
    subgraph "Configuration"
        G["SQLALCHEMY_URL"] --> B
        G --> D
    end
```

Sources: [alembic.ini](), [alembic/env.py](), [bugbounty_gpt/db/migrate.py]()

## Alembic Configuration

The Alembic configuration is defined in the `alembic.ini` file at the root of the project. This file contains settings for the migration environment, including the location of migration scripts, logging configuration, and other Alembic-specific settings.

Key configuration settings include:

| Setting | Value | Description |
|---------|-------|-------------|
| script_location | alembic | Directory containing migration scripts |
| prepend_sys_path | . | Adds current directory to Python path |
| version_path_separator | os | Uses OS-specific path separator |
| sqlalchemy.url | driver://user:pass@localhost/dbname | Database URL (overridden in env.py) |

Sources: [alembic.ini:1-64]()

## Migration Environment

The migration environment is configured in `alembic/env.py`. This file sets up the connection to the database and defines how migrations are executed.

Key aspects of the migration environment:

1. **Target Metadata**: The metadata from the application's models is used to generate migrations.
2. **Database URL**: The URL is obtained from the application's environment configuration and converted to a synchronous format for Alembic.
3. **Migration Modes**: Supports both online and offline migration modes.

```mermaid
flowchart TD
    A["alembic/env.py"] --> B["Import models.Base.metadata"]
    A --> C["Get SQLALCHEMY_URL from env"]
    C --> D["Convert to synchronous URL"]
    D --> E["Configure Alembic context"]
    E --> F["Run migrations"]
    
    subgraph "Migration Modes"
        G["Offline Mode"] --> F
        H["Online Mode"] --> F
    end
```

Sources: [alembic/env.py:1-74]()

### Database URL Handling

The migration system handles the conversion between the asynchronous database URL used by the application and the synchronous URL required by Alembic:

```python
SYNCHRONOUS_SQLALCHEMY_URL = SQLALCHEMY_URL.replace("+asyncpg", "")
sqlalchemy_url = SYNCHRONOUS_SQLALCHEMY_URL
config.set_main_option("sqlalchemy.url", f"{sqlalchemy_url}")
```

This conversion is necessary because the application uses asyncpg for asynchronous database operations, but Alembic requires a synchronous connection.

Sources: [alembic/env.py:21-23]()

## Automated Migration Process

The project includes an automated migration system in `bugbounty_gpt/db/migrate.py` that checks if the required database tables exist and creates them if necessary. This is particularly useful for development and testing environments.

```mermaid
flowchart TD
    A["migrate.py"] --> B["Get database URL"]
    B --> C["Create engine"]
    C --> D["Attempt database connection"]
    D --> E{"Table 'submission' exists?"}
    E -->|No| F["Run Alembic migration"]
    F --> G["Generate migration script"]
    G --> H["Apply migration"]
    E -->|Yes| I["Database ready"]
    
    subgraph "Connection Retry Logic"
        D --> J["MAX_ATTEMPTS = 5"]
        D --> K["WAIT_TIME = 5 seconds"]
    end
```

Sources: [bugbounty_gpt/db/migrate.py:1-54]()

### Connection Retry Logic

The migration system includes a robust connection retry mechanism to handle situations where the database might not be immediately available (common in containerized environments):

```python
for attempt in range(MAX_ATTEMPTS):
    try:
        check_and_init_submission_table(engine)
        break # Exit the loop if connection is successful
    except OperationalError as e:
        logger.warning(f"Failed to connect to database (attempt {attempt + 1} of {MAX_ATTEMPTS}). Retrying in {WAIT_TIME} seconds...")
        time.sleep(WAIT_TIME)
```

This retry logic attempts to connect to the database up to 5 times, with a 5-second wait between attempts.

Sources: [bugbounty_gpt/db/migrate.py:35-51]()

### Table Initialization

The `check_and_init_submission_table` function checks if the required `submission` table exists, and if not, generates and applies a migration to create it:

```python
def check_and_init_submission_table(engine):
    inspector = inspect(engine)
    if "submission" not in inspector.get_table_names():
        logger.info("Submission table not found - attempting alembic auto-generate & init.")
        alembic_cfg = Config("/usr/src/app/alembic.ini")
        command.revision(alembic_cfg, autogenerate=True, message="Auto-generated migration for 'submission' table.")
        command.upgrade(alembic_cfg, "head")
```

This function uses SQLAlchemy's `inspect` to check for the existence of the table, and if it's not found, uses Alembic's `command.revision` to generate a migration script and `command.upgrade` to apply it.

Sources: [bugbounty_gpt/db/migrate.py:22-33]()

## Migration Workflow

The typical workflow for managing database migrations in the project is as follows:

```mermaid
sequenceDiagram
    participant D as "Developer"
    participant A as "Alembic"
    participant DB as "Database"
    
    D->>A: Make changes to models
    D->>A: Generate migration script
    Note over A: alembic revision --autogenerate -m "Description"
    A->>D: Create migration script
    D->>A: Review and edit migration script
    D->>A: Apply migration
    Note over A: alembic upgrade head
    A->>DB: Execute schema changes
    
    alt Automated Migration
        Note over D,DB: Application startup
        DB->>A: Check for "submission" table
        A->>DB: Auto-generate and apply migration if needed
    end
```

Sources: [alembic/env.py](), [bugbounty_gpt/db/migrate.py]()

## Integration with Application Startup

The migration system is integrated with the application startup process through the `migrate.py` module. This ensures that the database schema is always up-to-date when the application starts, particularly in development and ephemeral database environments.

The module includes a log message indicating that the "Migration auto-init script" is activated, which can be disabled by rebuilding without the `EPHEMERAL_DB` argument.

Sources: [bugbounty_gpt/db/migrate.py:10-11]()

## Conclusion

The database migration system in bugbounty-gpt provides a robust way to manage database schema changes. It uses Alembic for migration management and includes an automated process for initializing the database schema when needed. This approach ensures that the database structure remains consistent with the application's models while allowing for incremental changes over time.

---

# Page: Development

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/python-app.yml](.github/workflows/python-app.yml)
- [poetry.lock](poetry.lock)
- [pyproject.toml](pyproject.toml)

</details>



This document provides information for developers working on the `bugbounty-gpt` project. It covers the development environment setup, testing approach, dependency management, and continuous integration/continuous deployment (CI/CD) pipeline.

For information about deploying the system, see [Deployment](#1.3).

## Development Environment

The `bugbounty-gpt` project uses modern Python development tools to ensure code quality and maintainability.

### Python Version

The project requires Python 3.11 as specified in the project configuration:

```mermaid
graph TD
    A["Python 3.11"] --> B["bugbounty-gpt"]
    B --> C["Dependencies"]
```

Sources: [pyproject.toml:14-15]()

### Poetry for Dependency Management

The project uses Poetry for dependency management. Poetry provides a modern approach to Python package management with features like:

- Dependency resolution
- Virtual environment management
- Package building and publishing

To install dependencies:

```bash
poetry install
```

To add a new dependency:

```bash
poetry add package-name
```

Sources: [pyproject.toml:1-32](), [.github/workflows/python-app.yml:21-27]()

## Project Dependencies

The project has several key dependencies that are managed through Poetry:

### Core Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| alembic | 1.12.1 | Database migration tool |
| asyncpg | 0.28.0 | Asynchronous PostgreSQL client |
| httpx | 0.25.0 | HTTP client for API requests |
| openai | 0.28.1 | OpenAI API client |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| SQLAlchemy | 2.0.22 | SQL toolkit and ORM |
| PyYAML | 6.0.1 | YAML parser for configuration |

### Development Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| pytest | * | Testing framework |
| pytest-mock | * | Mocking library for pytest |
| pytest-asyncio | ^0.20.3 | Async testing support |

```mermaid
graph TD
    subgraph "Runtime Dependencies"
        A["SQLAlchemy"] --> DB[(PostgreSQL)]
        B["alembic"] --> DB
        C["asyncpg"] --> DB
        D["openai"] --> E["OpenAI API"]
        F["httpx"] --> G["BugCrowd API"]
        H["PyYAML"] --> I["Configuration"]
    end
    
    subgraph "Development Dependencies"
        J["pytest"] --> K["Testing"]
        L["pytest-mock"] --> K
        M["pytest-asyncio"] --> K
    end
```

Sources: [pyproject.toml:14-32]()

## Testing

The project uses pytest as its testing framework, with additional support for mocking and asynchronous testing through pytest-mock and pytest-asyncio.

### Running Tests

To run the tests:

```bash
poetry run pytest
```

### Test Structure

Tests are organized to match the structure of the application code, with unit tests for individual components and integration tests for testing interactions between components.

```mermaid
graph TD
    A["pytest"] --> B["Unit Tests"]
    A --> C["Integration Tests"]
    B --> D["Component Tests"]
    B --> E["Model Tests"]
    B --> F["API Client Tests"]
    C --> G["End-to-End Tests"]
    C --> H["Database Tests"]
```

Sources: [pyproject.toml:29-32](), [.github/workflows/python-app.yml:28-30]()

## Continuous Integration

The project uses GitHub Actions for continuous integration to ensure code quality and prevent regressions.

### CI Workflow

The CI workflow is defined in `.github/workflows/python-app.yml` and includes the following steps:

1. Check out the code
2. Set up Python 3.11
3. Install Poetry
4. Install dependencies
5. Run tests

```mermaid
flowchart TD
    A["Push to GitHub"] --> B["GitHub Actions Triggered"]
    B --> C["Set up Python 3.11"]
    C --> D["Install Poetry"]
    D --> E["Install Dependencies"]
    E --> F["Run Tests"]
    F -->|Success| G["Build Passes"]
    F -->|Failure| H["Build Fails"]
```

The CI workflow runs on:
- Push to the main branch
- Pull requests to the main branch

Sources: [.github/workflows/python-app.yml:1-30]()

## Development Workflow

The recommended development workflow for contributing to the project is as follows:

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests locally
5. Submit a pull request
6. Wait for CI to pass
7. Address review comments
8. Merge to main

```mermaid
flowchart TD
    A["Fork Repository"] --> B["Create Feature Branch"]
    B --> C["Make Changes"]
    C --> D["Run Tests Locally"]
    D -->|Tests Pass| E["Submit Pull Request"]
    D -->|Tests Fail| C
    E --> F["CI Runs"]
    F -->|CI Passes| G["Code Review"]
    F -->|CI Fails| C
    G -->|Changes Requested| C
    G -->|Approved| H["Merge to Main"]
```

Sources: [.github/workflows/python-app.yml:1-30]()

## Database Migrations

The project uses Alembic for database migrations. For more information about database migrations, see [Database Migrations](#3.3).

## Development Environment Setup

To set up a development environment:

1. Clone the repository
2. Install Poetry
3. Install dependencies with `poetry install`
4. Set up environment variables or configuration file
5. Run the application with `poetry run python -m bugbounty_gpt`

For local development, you can use Docker Compose to set up a PostgreSQL database:

```bash
docker-compose up -d db
```

Sources: [pyproject.toml:1-32]()

## Code Organization

The codebase follows a modular structure:

```mermaid
graph TD
    A["bugbounty_gpt/"] --> B["__init__.py"]
    A --> C["models/"]
    A --> D["api/"]
    A --> E["db/"]
    A --> F["config/"]
    A --> G["utils/"]
    C --> C1["__init__.py"]
    C --> C2["submission.py"]
    D --> D1["__init__.py"]
    D --> D2["bugcrowd.py"]
    D --> D3["openai.py"]
    E --> E1["__init__.py"]
    E --> E2["session.py"]
    F --> F1["__init__.py"]
    F --> F2["env.py"]
```

This organization separates concerns and makes the codebase easier to navigate and maintain.

Sources: [pyproject.toml:8-12]()

## Development Best Practices

When developing for the project, follow these best practices:

1. Write tests for new functionality
2. Follow PEP 8 style guidelines
3. Use type hints
4. Document code with docstrings
5. Keep functions small and focused
6. Use async/await for I/O-bound operations
7. Handle exceptions appropriately
8. Use dependency injection for testability

Sources: [pyproject.toml:1-32](), [.github/workflows/python-app.yml:1-30]()

## Conclusion

This document provides an overview of the development process for the `bugbounty-gpt` project. By following the guidelines and using the tools described here, developers can contribute effectively to the project while maintaining code quality and reliability.

For more information about specific components of the system, refer to the other wiki pages:
- [Overview](#1)
- [Core Components](#2)
- [Database](#3)
- [Testing](#4.1)
- [Dependencies](#4.2)
- [CI/CD](#4.3)

---

# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/python-app.yml](.github/workflows/python-app.yml)
- [tests/test_bugcrowd_api_client.py](tests/test_bugcrowd_api_client.py)
- [tests/test_comment_handling.py](tests/test_comment_handling.py)
- [tests/test_config_validation.py](tests/test_config_validation.py)
- [tests/test_database_and_models.py](tests/test_database_and_models.py)
- [tests/test_openai_classification.py](tests/test_openai_classification.py)

</details>



This page documents the testing approach for the `bugbounty-gpt` system. It covers the testing framework, test organization, and how to run tests. For information about CI/CD integration, see [CI/CD](#4.3).

## Overview of Testing Approach

The `bugbounty-gpt` project uses pytest as its primary testing framework. Tests are organized by component and focus on unit testing the core functionality of the system.

```mermaid
flowchart TD
    subgraph "Testing Framework"
        pytest["pytest"]
        asyncio["pytest-asyncio"]
        mocking["unittest.mock"]
    end
    
    subgraph "Test Categories"
        api_tests["API Client Tests"]
        handler_tests["Handler Tests"]
        config_tests["Configuration Tests"]
        db_tests["Database Tests"]
    end
    
    subgraph "CI Integration"
        github_actions["GitHub Actions"]
        automated_testing["Automated Test Runs"]
    end
    
    pytest --> api_tests
    pytest --> handler_tests
    pytest --> config_tests
    pytest --> db_tests
    
    asyncio --> api_tests
    asyncio --> handler_tests
    
    mocking --> api_tests
    mocking --> handler_tests
    
    api_tests --> automated_testing
    handler_tests --> automated_testing
    config_tests --> automated_testing
    db_tests --> automated_testing
    
    automated_testing --> github_actions
```

Sources: [.github/workflows/python-app.yml:1-31](), [tests/test_bugcrowd_api_client.py:1-7](), [tests/test_openai_classification.py:1-5]()

## Test Organization

Tests are organized in the `tests/` directory and are grouped by component:

| Test File | Purpose |
|-----------|---------|
| `test_bugcrowd_api_client.py` | Tests for the BugCrowd API client |
| `test_comment_handling.py` | Tests for comment creation and handling |
| `test_config_validation.py` | Tests for configuration validation |
| `test_database_and_models.py` | Tests for database models |
| `test_openai_classification.py` | Tests for OpenAI integration and classification |

Sources: [tests/test_bugcrowd_api_client.py](), [tests/test_comment_handling.py](), [tests/test_config_validation.py](), [tests/test_database_and_models.py](), [tests/test_openai_classification.py]()

## Testing Components

### BugCrowd API Testing

Tests for the BugCrowd API client focus on verifying that the client correctly interacts with the BugCrowd API, including:

- Header generation
- Submission fetching
- Comment creation
- Submission patching

```mermaid
sequenceDiagram
    participant "Test" as test
    participant "BugCrowdAPI" as api
    participant "Mock httpx.AsyncClient" as httpx
    
    test->>api: call method
    api->>httpx: HTTP request
    httpx-->>api: mocked response
    api-->>test: processed result
    
    Note over test,httpx: All external HTTP calls are mocked
```

Sources: [tests/test_bugcrowd_api_client.py:8-70]()

### OpenAI Integration Testing

Tests for the OpenAI integration verify that:

- Request data is correctly built
- Responses are properly parsed
- Error handling works as expected
- Classification results are correctly sanitized

```mermaid
flowchart TD
    subgraph "OpenAIHandler Tests"
        build_request["_build_request_data()"]
        handle_response["_handle_response()"]
        handle_error["_handle_response_error()"]
        classify["classify_submission()"]
        sanitize["_classifications_sanitization()"]
    end
    
    subgraph "Test Scenarios"
        success["Successful Classification"]
        error["Error Handling"]
        invalid["Invalid Category"]
    end
    
    build_request --> classify
    handle_response --> classify
    handle_error --> classify
    sanitize --> handle_response
    
    classify --> success
    classify --> error
    handle_response --> invalid
```

Sources: [tests/test_openai_classification.py:6-68]()

### Comment Handling Testing

Tests for comment handling verify:

- Comment data preparation
- Successful comment creation
- Error handling during comment creation

Sources: [tests/test_comment_handling.py:1-54]()

### Configuration Testing

Tests for configuration validation ensure:

- Category sanitization works correctly
- Configuration validation catches invalid configurations
- Response categories are properly validated

Sources: [tests/test_config_validation.py:1-39]()

### Database Model Testing

Tests for database models verify:

- Category name sanitization
- Enum member creation
- Enum value correctness

Sources: [tests/test_database_and_models.py:1-13]()

## Asynchronous Testing

Many components in the system use asynchronous functions. The project uses `pytest-asyncio` to test these components. Asynchronous tests are marked with the `@pytest.mark.asyncio` decorator.

```python
@pytest.mark.asyncio
async def test_async_function():
    # Test code here
    result = await some_async_function()
    assert result == expected_value
```

Sources: [tests/test_bugcrowd_api_client.py:13-70](), [tests/test_comment_handling.py:29-53](), [tests/test_openai_classification.py:52-68]()

## Mocking

The tests use the `unittest.mock` module to mock external dependencies, particularly HTTP requests to the BugCrowd API and OpenAI API. This ensures that tests can run without actual API access and provides deterministic results.

```python
# Example of mocking an HTTP request
with patch.object(httpx.AsyncClient, 'get', return_value=mock_response) as mock_get:
    result = await function_under_test()
    assert result == expected_value
```

Sources: [tests/test_bugcrowd_api_client.py:23-25](), [tests/test_openai_classification.py:53-58]()

## Running Tests

Tests can be run locally using Poetry:

```bash
poetry run pytest
```

To run a specific test file:

```bash
poetry run pytest tests/test_file_name.py
```

To run tests with verbose output:

```bash
poetry run pytest -v
```

Sources: [.github/workflows/python-app.yml:28-30]()

## CI Integration

Tests are automatically run as part of the CI pipeline using GitHub Actions. The workflow is defined in `.github/workflows/python-app.yml`.

```mermaid
flowchart TD
    subgraph "GitHub Actions Workflow"
        checkout["Checkout Code"]
        setup_python["Setup Python 3.11"]
        install_poetry["Install Poetry"]
        install_deps["Install Dependencies"]
        run_tests["Run Tests"]
    end
    
    checkout --> setup_python
    setup_python --> install_poetry
    install_poetry --> install_deps
    install_deps --> run_tests
```

The CI workflow:
1. Checks out the code
2. Sets up Python 3.11
3. Installs Poetry
4. Installs project dependencies
5. Runs the tests using pytest

Sources: [.github/workflows/python-app.yml:1-31]()

## Test Coverage

The current test suite focuses on unit testing the core components of the system. The main areas covered are:

1. BugCrowd API integration
2. OpenAI classification
3. Comment handling
4. Configuration validation
5. Database models

Future improvements could include:
- Integration tests
- End-to-end tests
- Increased test coverage for edge cases

Sources: [tests/test_bugcrowd_api_client.py](), [tests/test_openai_classification.py](), [tests/test_comment_handling.py](), [tests/test_config_validation.py](), [tests/test_database_and_models.py]()

---

# Page: Dependencies

# Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [poetry.lock](poetry.lock)
- [pyproject.toml](pyproject.toml)

</details>



This page documents the dependencies used in the `bugbounty-gpt` project, their purposes, and how they are managed. It covers both runtime dependencies and development dependencies required for the system to function properly.

## Overview

The `bugbounty-gpt` project uses Poetry for dependency management. All dependencies are defined in the `pyproject.toml` file, with their exact versions locked in the `poetry.lock` file to ensure reproducible builds.

Sources: [pyproject.toml:1-33](), [poetry.lock:1-30]()

## Dependency Management

### Poetry

Poetry is the primary dependency management tool used in this project. It handles package installation, dependency resolution, and virtual environment management.

```mermaid
flowchart TD
    subgraph "Dependency Management"
        pyproject["pyproject.toml"]
        lock["poetry.lock"]
        venv["Virtual Environment"]
    end

    subgraph "Commands"
        install["poetry install"]
        update["poetry update"]
        add["poetry add <package>"]
    end

    pyproject --> lock
    install --> venv
    update --> lock
    add --> pyproject
    lock --> venv
```

Sources: [pyproject.toml:1-33](), [poetry.lock:1-30]()

## Core Dependencies

The project relies on several key libraries to function:

### Database Dependencies

```mermaid
flowchart LR
    subgraph "Database Layer"
        sqlalchemy["SQLAlchemy 2.0.22"]
        alembic["Alembic 1.12.1"]
        asyncpg["AsyncPG 0.28.0"]
        psycopg2["psycopg2-binary 2.9.9"]
    end

    sqlalchemy --> |"ORM Mapping"| DB[("PostgreSQL Database")]
    alembic --> |"Migrations"| DB
    asyncpg --> |"Async Driver"| DB
    psycopg2 --> |"Sync Driver"| DB
```

- **SQLAlchemy (2.0.22)**: ORM for database interactions
- **Alembic (1.12.1)**: Database migration tool built on SQLAlchemy
- **AsyncPG (0.28.0)**: Asynchronous PostgreSQL driver
- **psycopg2-binary (2.9.9)**: PostgreSQL adapter for Python

Sources: [pyproject.toml:16-17](), [pyproject.toml:18](), [pyproject.toml:25-26]()

### API and HTTP Dependencies

```mermaid
flowchart LR
    subgraph "HTTP Clients"
        httpx["HTTPX 0.25.0"]
        openai["OpenAI 0.28.1"]
    end

    httpx --> |"HTTP Requests"| bugcrowd["BugCrowd API"]
    openai --> |"API Calls"| openaiapi["OpenAI API"]
```

- **HTTPX (0.25.0)**: Modern HTTP client with async support, used for BugCrowd API interactions
- **OpenAI (0.28.1)**: Official OpenAI client library for API access

Sources: [pyproject.toml:18](), [pyproject.toml:24]()

### Configuration Dependencies

```mermaid
flowchart TD
    subgraph "Configuration"
        yaml["PyYAML 6.0.1"]
    end

    yaml --> |"Parse"| config["config.yaml"]
    config --> app["Application"]
```

- **PyYAML (6.0.1)**: YAML parser for configuration files

Sources: [pyproject.toml:27]()

## Development Dependencies

The project uses several tools for testing and development:

```mermaid
flowchart LR
    subgraph "Testing Framework"
        pytest["pytest"]
        pytest_mock["pytest-mock"]
        pytest_asyncio["pytest-asyncio 0.20.3"]
    end

    pytest --> |"Runs"| tests["Test Suite"]
    pytest_mock --> |"Mocking"| tests
    pytest_asyncio --> |"Async Testing"| tests
```

- **pytest**: Testing framework
- **pytest-mock**: Thin wrapper around the mock package for easier use with pytest
- **pytest-asyncio**: Pytest support for asyncio

Sources: [pyproject.toml:30-32]()

## Dependency Relationships

The following diagram shows the relationships between major dependencies in the system:

```mermaid
graph TD
    subgraph "Application Core"
        app["bugbounty-gpt Application"]
    end

    subgraph "External APIs"
        bugcrowd["BugCrowd API"]
        openaiapi["OpenAI API"]
    end

    subgraph "Database"
        db["PostgreSQL Database"]
        migrations["Database Migrations"]
    end

    subgraph "Dependencies"
        httpx["HTTPX"]
        openai["OpenAI Client"]
        sqlalchemy["SQLAlchemy"]
        alembic["Alembic"]
        asyncpg["AsyncPG"]
        pyyaml["PyYAML"]
    end

    app --> httpx
    app --> openai
    app --> sqlalchemy
    app --> pyyaml
    
    httpx --> bugcrowd
    openai --> openaiapi
    
    sqlalchemy --> db
    alembic --> migrations
    migrations --> db
    asyncpg --> db
    
    alembic --> sqlalchemy
```

Sources: [pyproject.toml:14-27]()

## Dependency Version Constraints

The project specifies exact versions for most dependencies to ensure reproducibility. The Python version is constrained to Python 3.11.x.

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.11.* | Runtime environment |
| alembic | 1.12.1 | Database migrations |
| asyncpg | 0.28.0 | Async PostgreSQL driver |
| httpx | 0.25.0 | HTTP client |
| idna | 3.4 | Internationalized Domain Names |
| iniconfig | 2.0.0 | INI file parsing |
| Mako | 1.2.4 | Template engine (used by Alembic) |
| MarkupSafe | 2.1.3 | String handling for templates |
| multidict | 6.0.4 | Dictionary with multiple values per key |
| openai | 0.28.1 | OpenAI API client |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| SQLAlchemy | 2.0.22 | SQL toolkit and ORM |
| PyYAML | 6.0.1 | YAML parser |

Sources: [pyproject.toml:14-27]()

## Transitive Dependencies

The main dependencies pull in several transitive dependencies. Key ones include:

- **aiohttp**: Used by the OpenAI client for async HTTP requests
- **certifi**: Provides Mozilla's CA Bundle for secure connections
- **charset-normalizer**: Character encoding detection
- **h11**: HTTP/1.1 implementation used by httpx
- **anyio**: Asynchronous I/O library

Sources: [poetry.lock:3-96](), [poetry.lock:145-162](), [poetry.lock:258-353](), [poetry.lock:508-516]()

## Installing Dependencies

Dependencies are installed using Poetry:

```bash
# Install all dependencies (including dev)
poetry install

# Install only production dependencies
poetry install --no-dev
```

When running in Docker, dependencies are installed during the container build process.

Sources: [pyproject.toml:1-33]()

## Updating Dependencies

To update dependencies:

```bash
# Update all dependencies
poetry update

# Update specific dependency
poetry update <package-name>
```

After updating, the `poetry.lock` file will be regenerated with the new dependency versions.

Sources: [poetry.lock:1-30]()

---

# Page: CI/CD

# CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/python-app.yml](.github/workflows/python-app.yml)
- [Dockerfile](Dockerfile)

</details>



This page documents the Continuous Integration and Continuous Deployment (CI/CD) setup for the bugbounty-gpt project. It covers the GitHub Actions workflow configuration, Docker containerization, and the deployment process.

For information about dependencies management, see [Dependencies](#4.2).

## Overview

The bugbounty-gpt project uses GitHub Actions for continuous integration and Docker for containerization and deployment. The CI pipeline automatically runs tests on pull requests and pushes to the main branch, while the Docker configuration enables consistent deployment across environments.

```mermaid
flowchart TD
    subgraph "CI Process"
        PR["Pull Request/Push"]
        GHA["GitHub Actions"]
        Tests["Run Tests"]
        BuildCheck["Build Check"]
    end
    
    subgraph "CD Process"
        Docker["Docker Build"]
        Image["Container Image"]
        Deploy["Deployment"]
    end
    
    PR --> GHA
    GHA --> Tests
    GHA --> BuildCheck
    BuildCheck --> Docker
    Docker --> Image
    Image --> Deploy
```

Sources: [.github/workflows/python-app.yml:1-31](), [Dockerfile:1-40]()

## GitHub Actions Workflow

The project uses GitHub Actions for continuous integration. The workflow is defined in the `.github/workflows/python-app.yml` file and is triggered on:
- Push events to the main branch
- Pull request events targeting the main branch

### Workflow Configuration

The workflow consists of a single job named "build" that runs on the latest Ubuntu environment and performs the following steps:

1. Check out the repository code
2. Set up Python 3.11
3. Install Poetry (dependency management tool)
4. Install project dependencies using Poetry
5. Run tests using pytest

```mermaid
flowchart TD
    subgraph "GitHub Actions Workflow"
        Trigger["Trigger: Push to main or PR"]
        Checkout["actions/checkout@v3"]
        SetupPython["actions/setup-python@v3\n(Python 3.11)"]
        InstallPoetry["Install Poetry"]
        InstallDeps["poetry install"]
        RunTests["poetry run pytest"]
    end
    
    Trigger --> Checkout
    Checkout --> SetupPython
    SetupPython --> InstallPoetry
    InstallPoetry --> InstallDeps
    InstallDeps --> RunTests
```

Sources: [.github/workflows/python-app.yml:1-31]()

## Docker Containerization

The project uses Docker for containerization, which ensures consistent deployment across different environments. The Docker configuration is defined in the `Dockerfile`.

### Docker Image Configuration

The Docker image is built on top of the official Python 3.11 slim-bookworm image and includes:

1. Poetry installation
2. Creation of a non-root user for security
3. Copy of application code, configuration, and dependencies
4. Installation of dependencies using Poetry
5. Copy of Alembic configuration and migration scripts for database management
6. Configuration for running the application with or without an ephemeral database

```mermaid
flowchart TD
    subgraph "Docker Image Layers"
        BaseImage["python:3.11-slim-bookworm"]
        PoetryLayer["Install Poetry"]
        UserLayer["Create non-root user"]
        CodeLayer["Copy application code"]
        ConfigLayer["Copy config files"]
        DepsLayer["Install dependencies"]
        AlembicLayer["Copy Alembic files"]
        PermissionsLayer["Set permissions"]
        UserSwitchLayer["Switch to non-root user"]
        EnvLayer["Set environment variables"]
        CmdLayer["Set CMD instruction"]
    end
    
    BaseImage --> PoetryLayer
    PoetryLayer --> UserLayer
    UserLayer --> CodeLayer
    CodeLayer --> ConfigLayer
    ConfigLayer --> DepsLayer
    DepsLayer --> AlembicLayer
    AlembicLayer --> PermissionsLayer
    PermissionsLayer --> UserSwitchLayer
    UserSwitchLayer --> EnvLayer
    EnvLayer --> CmdLayer
```

Sources: [Dockerfile:1-40]()

### Build Arguments and Environment Variables

The Docker image accepts a build argument `EPHEMERAL_DB` which determines the startup behavior:

- If `EPHEMERAL_DB=true`, the container runs the `start.sh` script
- Otherwise, it directly runs the Python module `bugbounty_gpt`

This allows for flexible deployment configurations, particularly useful for development versus production environments.

Sources: [Dockerfile:33-38]()

## CI/CD Integration

The CI/CD pipeline integrates the GitHub Actions workflow with Docker containerization to provide a complete development and deployment process.

```mermaid
flowchart LR
    subgraph "Development"
        LocalDev["Local Development"]
        PR["Pull Request"]
    end
    
    subgraph "CI Pipeline"
        GHActions["GitHub Actions"]
        Tests["Run Tests"]
        BuildCheck["Build Check"]
    end
    
    subgraph "CD Pipeline"
        DockerBuild["Docker Build"]
        DockerImage["Docker Image"]
        Deployment["Deployment"]
    end
    
    LocalDev --> PR
    PR --> GHActions
    GHActions --> Tests
    GHActions --> BuildCheck
    BuildCheck --> DockerBuild
    DockerBuild --> DockerImage
    DockerImage --> Deployment
```

Sources: [.github/workflows/python-app.yml:1-31](), [Dockerfile:1-40]()

## Development Workflow

The typical development workflow for the bugbounty-gpt project is:

1. Developers make changes locally and create a pull request
2. GitHub Actions automatically runs tests on the pull request
3. After approval and merge, GitHub Actions runs tests on the main branch
4. The Docker image can be built and deployed manually or through additional automation

This workflow ensures that code quality is maintained through automated testing before changes are merged into the main branch.

| Step | Action | Triggered By | Output |
|------|--------|-------------|--------|
| 1 | Run tests | Pull request or push to main | Test results |
| 2 | Build check | Successful tests | Build status |
| 3 | Docker build | Manual or automated trigger | Docker image |
| 4 | Deployment | Manual or automated trigger | Deployed application |

Sources: [.github/workflows/python-app.yml:1-31](), [Dockerfile:1-40]()

## Security Considerations

The CI/CD pipeline includes several security measures:

1. The GitHub Actions workflow has limited permissions (read-only access to repository contents)
2. The Docker image runs as a non-root user to reduce the risk of container breakout
3. Dependencies are explicitly defined and locked using Poetry to prevent supply chain attacks

For more information about security considerations, see [Security](#5).

Sources: [.github/workflows/python-app.yml:8-9](), [Dockerfile:7-8](), [Dockerfile:30-31]()

---

# Page: Security

# Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)

</details>



This page documents the security aspects of the bugbounty-gpt system, including security policies, vulnerability reporting procedures, and security-related considerations for deployment and operation.

## Security Policy Overview

The bugbounty-gpt project follows OpenAI's Coordinated Vulnerability Disclosure Policy. This policy outlines how security vulnerabilities should be reported and how they will be addressed by the OpenAI team.

The full details of the policy can be found in the SECURITY.md file in the repository root and on OpenAI's official website.

Sources: [SECURITY.md:1-4]()

## Vulnerability Reporting

If you discover a security vulnerability in the bugbounty-gpt system, please follow these steps:

1. Report the vulnerability to OpenAI's security team using the contact information provided in the security policy.
2. Include detailed information about the vulnerability, including steps to reproduce.
3. Allow time for the OpenAI team to investigate and address the issue before public disclosure.

OpenAI provides a PGP key for secure communication about vulnerabilities, which can be found at the URL referenced in the SECURITY.md file.

Sources: [SECURITY.md:1-4]()

## Security Architecture

The bugbounty-gpt system interacts with several external services and handles potentially sensitive data. Understanding the security architecture is essential for secure deployment and operation.

```mermaid
flowchart TD
    subgraph "External Services"
        BC["BugCrowd API"]
        OAI["OpenAI API"]
    end
    
    subgraph "bugbounty-gpt System"
        Config["Configuration System"]
        APIKeys["API Keys Storage"]
        DBCreds["Database Credentials"]
        Submissions["Submission Data"]
    end
    
    subgraph "Data Storage"
        DB["PostgreSQL Database"]
    end
    
    BC <-->|"HTTPS API Calls"| bugbounty-gpt
    OAI <-->|"HTTPS API Calls"| bugbounty-gpt
    
    Config -->|"Loads"| APIKeys
    Config -->|"Loads"| DBCreds
    
    bugbounty-gpt -->|"Stores"| Submissions
    Submissions -->|"Persisted in"| DB
    
    APIKeys -.->|"Secures access to"| BC
    APIKeys -.->|"Secures access to"| OAI
    DBCreds -.->|"Secures access to"| DB
```

Sources: [SECURITY.md:1-4]()

## Credential Management

The bugbounty-gpt system requires several credentials to operate:

1. BugCrowd API credentials
2. OpenAI API key
3. Database credentials

These credentials should be managed securely using environment variables or a secure configuration file that is not committed to version control.

### Recommended Practices

| Credential Type | Storage Recommendation | Notes |
|----------------|------------------------|-------|
| API Keys | Environment variables | Never commit API keys to version control |
| Database Credentials | Environment variables or secure config | Use strong, unique passwords |
| Configuration Files | Use .gitignore to exclude from repo | Maintain separate configs for dev/prod |

## Data Security Considerations

The bugbounty-gpt system processes bug bounty submissions which may contain sensitive information. Consider the following security aspects:

1. **Data in Transit**: All API communications should use HTTPS
2. **Data at Rest**: Database should be properly secured with access controls
3. **Data Retention**: Implement appropriate data retention policies for submissions
4. **Access Control**: Limit access to the system and its data to authorized personnel only

## License and Legal Considerations

The bugbounty-gpt system is released under the MIT License, which has specific provisions regarding liability and warranty. Users should review the license terms to understand their rights and obligations.

```mermaid
graph TD
    subgraph "MIT License Key Provisions"
        Permission["Permission to use, copy, modify, distribute"]
        Attribution["Copyright notice must be included"]
        NoWarranty["No warranty provided"]
        NoLiability["No liability for damages"]
    end
    
    subgraph "User Responsibilities"
        SecureDeployment["Secure deployment"]
        CredentialProtection["Protection of credentials"]
        DataHandling["Proper handling of sensitive data"]
        ComplianceWithLaws["Compliance with applicable laws"]
    end
    
    MIT["MIT License"] --> Permission
    MIT --> Attribution
    MIT --> NoWarranty
    MIT --> NoLiability
    
    NoWarranty -.->|"Implies"| SecureDeployment
    NoLiability -.->|"Implies"| CredentialProtection
    NoLiability -.->|"Implies"| DataHandling
    NoLiability -.->|"Implies"| ComplianceWithLaws
```

Sources: [LICENSE:1-21]()

## Security Best Practices for Deployment

When deploying the bugbounty-gpt system, consider the following security best practices:

1. **Container Security**: If using Docker, follow container security best practices:
   - Use minimal base images
   - Run containers with non-root users
   - Keep container images updated

2. **Network Security**:
   - Use network segmentation
   - Implement proper firewall rules
   - Consider using a VPN for administrative access

3. **Monitoring and Logging**:
   - Implement logging for security-relevant events
   - Set up monitoring for unusual activity
   - Regularly review logs for security issues

4. **Updates and Patches**:
   - Keep all dependencies updated
   - Regularly check for security advisories affecting the system components
   - Apply security patches promptly

## Related Documentation

For information about system deployment, see [Deployment](#1.3).
For details about configuration, including secure handling of credentials, see [Configuration](#1.2).