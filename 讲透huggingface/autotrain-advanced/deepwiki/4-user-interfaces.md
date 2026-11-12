<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/autotrain-advanced · page 4 User Interfaces · fetched 2026-10-26 -->

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [colabs/AutoTrain.ipynb](colabs/AutoTrain.ipynb)
- [colabs/AutoTrain_ngrok.ipynb](colabs/AutoTrain_ngrok.ipynb)
- [src/autotrain/app/api_routes.py](src/autotrain/app/api_routes.py)
- [src/autotrain/app/models.py](src/autotrain/app/models.py)
- [src/autotrain/app/params.py](src/autotrain/app/params.py)
- [src/autotrain/app/templates/index.html](src/autotrain/app/templates/index.html)
- [src/autotrain/app/ui_routes.py](src/autotrain/app/ui_routes.py)
- [src/autotrain/backends/base.py](src/autotrain/backends/base.py)
- [src/autotrain/backends/spaces.py](src/autotrain/backends/spaces.py)
- [src/autotrain/client.py](src/autotrain/client.py)
- [src/autotrain/logging.py](src/autotrain/logging.py)
- [src/autotrain/parser.py](src/autotrain/parser.py)

</details>



This page provides an overview of the different ways users can interact with AutoTrain Advanced. The system offers multiple interfaces to accommodate various user preferences and workflows, from command-line operations to graphical user interfaces. For detailed information about specific interface implementations, see [Command Line Interface](#4.1), [Web Application](#4.2), and [Colab and Notebook Integration](#4.3).

## Available User Interfaces

AutoTrain Advanced provides four primary user interfaces:

1. **Command Line Interface (CLI)** - For users who prefer terminal-based workflows
2. **Web User Interface (Web UI)** - A browser-based graphical interface
3. **Colab Integration** - Jupyter notebook interfaces specifically for Google Colab
4. **Python API** - Programmatic access for developers and custom workflows

```mermaid
graph TD
    User([User]) --- Interfaces

    subgraph "Interfaces"
        CLI["Command Line Interface<br>(autotrain commands)"]
        WebUI["Web User Interface<br>(Browser-based)"]
        ColabUI["Colab Integration<br>(Jupyter Notebooks)"]
        PythonAPI["Python API<br>(Client class)"]
    end
    
    subgraph "Backend Systems"
        ProjectMgmt["AutoTrainProject<br>(Project Management)"]
        DB[(AutoTrainDB)]
        Params["AppParams<br>(Parameter Processing)"]
        Models["Model Selection<br>(fetch_models)"]
    end
    
    CLI --> |"--config file.yaml"| ConfigParser["AutoTrainConfigParser"]
    CLI --> |"direct commands"| ProjectMgmt
    
    WebUI --> UIRoutes["ui_router<br>(FastAPI Routes)"]
    UIRoutes --> Params
    UIRoutes --> DB
    UIRoutes --> ProjectMgmt
    UIRoutes --> Models
    
    WebUI --> APIRoutes["api_router<br>(API Endpoints)"]
    APIRoutes --> Params
    APIRoutes --> ProjectMgmt
    
    ColabUI --> |"colab_app()"| WebUI
    
    PythonAPI --> |"Client.create()"| APIRoutes
    
    ConfigParser --> ProjectMgmt
    
    ProjectMgmt --> Training["Training Process<br>(Various Backends)"]
    
    classDef interface fill:#f9f9f9,stroke:#333,stroke-width:1px;
    class CLI,WebUI,ColabUI,PythonAPI interface;
```

Sources: 
- [README.md:25-34]()
- [src/autotrain/app/ui_routes.py:41-93]()
- [src/autotrain/client.py:166-294]()
- [colabs/AutoTrain.ipynb:1-50]()
- [colabs/AutoTrain_ngrok.ipynb:1-52]()

## Interface Relationships and Data Flow

The following diagram illustrates how user input flows through the system, regardless of which interface is used:

```mermaid
flowchart TD
    User([User]) --> |"Input"| UserInterface["User Interface<br>(CLI/Web UI/Colab/API)"]
    
    UserInterface --> |"Creates config"| ParameterHandling["Parameter Handling<br>(AppParams)"]
    ParameterHandling --> |"Validates and<br>transforms"| TaskSpecificParams["Task-Specific Parameters<br>(e.g., LLMTrainingParams)"]
    
    UserInterface --> |"Provides"| DataSource["Data Source<br>(Files/Hub Dataset)"]
    
    TaskSpecificParams --> ProjectCreation["Project Creation<br>(AutoTrainProject)"]
    DataSource --> ProjectCreation
    
    ProjectCreation --> |"Selects"| Backend["Backend Selection<br>(Local/Spaces/Endpoints)"]
    Backend --> |"Executes"| Training["Training Job"]
    
    Training --> |"Produces"| Results["Results<br>(Model, Logs)"]
    Results --> |"Displayed in"| UserInterface
```

Sources:
- [src/autotrain/app/params.py:139-489]()
- [src/autotrain/app/ui_routes.py:493-703]()
- [src/autotrain/client.py:214-282]()
- [src/autotrain/parser.py:38-229]()

## Command Line Interface

The Command Line Interface (CLI) provides a terminal-based way to interact with AutoTrain. It supports both direct commands for specific tasks and configuration file-based execution.

```mermaid
graph LR
    User([User]) --> CLI["autotrain<br>command"]
    
    CLI --> |"app"| WebApp["Start Web UI<br>(autotrain app --port 8080)"]
    CLI --> |"--config"| ConfigFile["YAML Config File<br>(autotrain --config file.yaml)"]
    CLI --> |"task-specific"| TaskCommands["Task Commands<br>(e.g., autotrain llm)"]
    CLI --> |"setup"| Setup["Environment Setup<br>(autotrain setup)"]
    
    ConfigFile --> ConfigParser["AutoTrainConfigParser"]
    ConfigParser --> AutoTrainProject["AutoTrainProject.create()"]
    
    TaskCommands --> AutoTrainProject
    
    AutoTrainProject --> Backend["Training Backends<br>(Local/Spaces/etc.)"]
```

Sources:
- [README.md:57-113]()
- [src/autotrain/parser.py:38-230]()

## Web User Interface

The Web UI provides a graphical interface accessible through a web browser. It's built with FastAPI for the backend and uses Jinja2 templates for rendering the frontend.

```mermaid
graph TD
    User([User]) --> |"Access"| WebUI["Web UI (Browser)"]
    
    WebUI --> |"GET /"| IndexRoute["load_index()<br>(ui_routes.py)"]
    WebUI --> |"GET /params/{task}/{param_type}"| ParamsRoute["fetch_params()<br>(ui_routes.py)"]
    WebUI --> |"GET /model_choices/{task}"| ModelsRoute["fetch_model_choices()<br>(ui_routes.py)"]
    WebUI --> |"POST /create_project"| CreateRoute["handle_form()<br>(ui_routes.py)"]
    WebUI --> |"GET /logs"| LogsRoute["fetch_logs()<br>(ui_routes.py)"]
    
    subgraph "Backend Components"
        IndexRoute --> Templates["Jinja2 Templates<br>(index.html)"]
        
        ParamsRoute --> TaskParams["Task Parameters<br>(UI_PARAMS)"]
        ModelsRoute --> ModelSelection["Model Selection<br>(MODEL_CHOICE)"]
        
        CreateRoute --> ProjectCreation["Project Creation<br>(AutoTrainProject)"]
        LogsRoute --> LogStorage["Log Retrieval<br>(autotrain.log)"]
        
        Authentication["user_authentication()<br>(ui_routes.py)"] --> |"Authenticates"| AllRoutes["All Routes"]
    end
    
    ProjectCreation --> |"Creates"| TrainingJob["Training Job"]
    ProjectCreation --> |"Stores job ID"| DB[(AutoTrainDB)]
    
    TrainingJob --> LogStorage
```

Sources:
- [src/autotrain/app/ui_routes.py:41-796]()
- [src/autotrain/app/templates/index.html:1-480]()
- [src/autotrain/app/params.py:139-489]()
- [src/autotrain/app/models.py:336-374]()

### Web UI Components and Parameters

The Web UI presents a form-based interface where users can configure various parameters for their training jobs:

```mermaid
graph TD
    WebUI["Web UI"] --> FormSections["Form Sections"]
    
    FormSections --> ProjectInfo["Project Information<br>(Name, Description)"]
    FormSections --> TaskSelection["Task Selection<br>(LLM, Classification, etc.)"]
    FormSections --> ModelSelection["Model Selection<br>(Base Model)"]
    FormSections --> DataSource["Data Source<br>(Upload/Hub Dataset)"]
    FormSections --> ColumnMapping["Column Mapping<br>(Text, Label, etc.)"]
    FormSections --> TrainingParams["Training Parameters<br>(Basic/Full)"]
    FormSections --> HardwareSelection["Hardware Selection<br>(Local/Cloud)"]
    
    TrainingParams --> BasicParams["Basic Parameters<br>(epochs, batch_size, lr)"]
    TrainingParams --> AdvancedParams["Advanced Parameters<br>(PEFT, Quantization, etc.)"]
    
    DataSource --> LocalUpload["Local File Upload"]
    DataSource --> HFDataset["Hugging Face Dataset"]
    
    SubmitForm["'Start Training' Button"] --> HandleForm["handle_form()<br>(ui_routes.py)"]
    HandleForm --> AppParams["AppParams<br>(params.py)"]
    AppParams --> AutoTrainProject["AutoTrainProject<br>(project.py)"]
```

Sources:
- [src/autotrain/app/ui_routes.py:45-291]()
- [src/autotrain/app/ui_routes.py:493-703]()
- [src/autotrain/app/templates/index.html:148-380]()

## Colab and Notebook Integration

AutoTrain Advanced provides special integration for Google Colab through dedicated notebooks:

```mermaid
graph TD
    User([User]) --> ColabNotebook["Google Colab Notebook"]
    
    ColabNotebook --> Standard["Standard Integration<br>(AutoTrain.ipynb)"]
    ColabNotebook --> NGrok["Ngrok Integration<br>(AutoTrain_ngrok.ipynb)"]
    
    Standard --> |"colab_app()"| IPythonWidgets["IPython Widgets<br>(Form Interface)"]
    NGrok --> |"autotrain app --share"| WebUIviaURL["Web UI via<br>Public URL"]
    
    IPythonWidgets --> |"Creates"| AppParams["AppParams"]
    WebUIviaURL --> |"Uses"| UIRoutes["UI Routes<br>(ui_routes.py)"]
    
    AppParams --> AutoTrainProject["AutoTrainProject"]
    UIRoutes --> AutoTrainProject
    
    AutoTrainProject --> |"Executes on"| ColabGPU["Colab GPU Resource"]
```

Sources:
- [colabs/AutoTrain.ipynb:1-50]()
- [colabs/AutoTrain_ngrok.ipynb:1-52]()

## Python API

The Python API provides programmatic access to AutoTrain through the `Client` class:

```mermaid
graph TD
    User([Developer]) --> |"Uses"| PythonCode["Python Code"]
    
    PythonCode --> |"from autotrain.client import Client"| ClientClass["Client Class"]
    
    ClientClass --> |"create()"| CreateProject["Create Project<br>client.create()"]
    ClientClass --> |"get_logs()"| GetLogs["Get Logs<br>client.get_logs()"]
    ClientClass --> |"stop_training()"| StopTraining["Stop Training<br>client.stop_training()"]
    
    CreateProject --> |"API Request"| APIEndpoint["API Endpoint<br>/api/create_project"]
    GetLogs --> |"API Request"| LogsEndpoint["API Endpoint<br>/api/logs"]
    StopTraining --> |"API Request"| StopEndpoint["API Endpoint<br>/api/stop_training/{job_id}"]
    
    APIEndpoint --> AutoTrainProject["AutoTrainProject<br>(project.py)"]
```

Sources:
- [src/autotrain/client.py:166-294]()
- [src/autotrain/app/api_routes.py:1-140]()

### Python API Usage Example

Here's a simplified example of how to use the Python API:

```python
from autotrain.client import Client

# Initialize client
client = Client(
    host="https://autotrain-projects-autotrain-advanced.hf.space/", 
    token="YOUR_HF_TOKEN",
    username="YOUR_USERNAME"
)

# Create a project
response = client.create(
    project_name="my-llm-project",
    task="llm:sft",
    base_model="mistralai/Mistral-7B-v0.1",
    backend="spaces-a10g-large",
    dataset="my-dataset",
    train_split="train",
    column_mapping={"text_column": "text"},
    params={
        "epochs": 3,
        "batch_size": 4,
        "lr": 5e-5,
        "peft": True,
        "quantization": "int4"
    }
)

# Get logs for a job
logs = client.get_logs(job_id="username/autotrain-my-llm-project")

# Stop training for a job
client.stop_training(job_id="username/autotrain-my-llm-project")
```

Sources:
- [src/autotrain/client.py:166-294]()

## Authentication Flow

All interfaces in AutoTrain Advanced require authentication with Hugging Face credentials:

```mermaid
graph TD
    User([User]) --> |"Provides Credentials"| Interface["User Interface"]
    
    Interface --> |"Check token"| TokenSource["Token Source"]
    
    TokenSource --> |"Option 1"| EnvVar["Environment Variable<br>HF_TOKEN"]
    TokenSource --> |"Option 2"| OAuthSession["OAuth in Session<br>request.session['oauth_info']"]
    TokenSource --> |"Option 3"| BearerToken["Bearer Token<br>in Request Headers"]
    
    EnvVar --> TokenVerification["Token Verification<br>token_verification()"]
    OAuthSession --> TokenVerification
    BearerToken --> TokenVerification
    
    TokenVerification --> |"Valid"| Authenticated["Authenticated<br>Request Proceeds"]
    TokenVerification --> |"Invalid"| Unauthenticated["Unauthenticated<br>Error or Login Page"]
```

Sources:
- [src/autotrain/app/ui_routes.py:318-367]()
- [src/autotrain/client.py:189-206]()

## Interface Selection Guidelines

Each interface in AutoTrain Advanced is designed for specific use cases:

| Interface | Best For | Key Features | Limitations |
|-----------|----------|--------------|-------------|
| **CLI** | Automation, scripting, CI/CD pipelines | Scriptable, supports configuration files | Steeper learning curve |
| **Web UI** | Visual exploration, interactive experimentation | User-friendly, visual, guided workflow | Requires running a server |
| **Colab** | Quick experimentation, limited local resources | Free GPU access, notebook environment | Limited by Colab constraints |
| **Python API** | Custom applications, programmatic control | Full programmatic control, integration with other Python code | Requires coding knowledge |

Sources:
- [README.md:25-56]()

## Environment Variables and Configuration

All interfaces respect various environment variables that control AutoTrain's behavior:

| Environment Variable | Description | Used By |
|----------------------|-------------|---------|
| `HF_TOKEN` | Hugging Face authentication token | All interfaces |
| `SPACE_ID` | ID when running in Hugging Face Spaces | Web UI |
| `ENABLE_NGC` | Enable NVIDIA GPU Cloud backend (0/1) | Web UI |
| `ENABLE_NVCF` | Enable NVIDIA Cloud Functions backend (0/1) | Web UI |
| `AUTOTRAIN_LOCAL` | Enable local backend (0/1) | Web UI |
| `HF_USERNAME` | Default username for Hugging Face | Python API |
| `AUTOTRAIN_API` | Override API endpoint URL | Python API |
| `AUTOTRAIN_CUSTOM_MODELS` | Comma-separated list of custom models | Web UI |

Sources:
- [src/autotrain/app/ui_routes.py:31-37]()
- [src/autotrain/client.py:10-29]()
- [colabs/AutoTrain_ngrok.ipynb:26-29]()

## Conclusion

AutoTrain Advanced provides multiple user interfaces to accommodate different user preferences and workflows. Whether you prefer command-line operations, visual interfaces, notebook environments, or programmatic control, there's an interface designed to meet your needs. Each interface ultimately leverages the same core functionality, ensuring consistent behavior regardless of how you choose to interact with the system.

All interfaces connect to the same underlying project management system and training components, allowing users to select the interface that best suits their workflow while benefiting from the full capabilities of AutoTrain Advanced.

---

