<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Build25-LAB329 · extra page Environment Configuration · fetched 2026-10-26 -->

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [Lab329/Notebook/sample.env](Lab329/Notebook/sample.env)
- [Lab329/README.md](Lab329/README.md)
- [azure.yaml](azure.yaml)
- [infra/main.parameters.json](infra/main.parameters.json)

</details>



This document provides detailed instructions for configuring the required environment variables, authentication credentials, and development environment needed to execute the Model Distillation Workshop notebooks. The configuration establishes connections to Azure AI services, Azure Machine Learning workspace, and sets up the proper Python environments for each stage of the workflow.

For Azure infrastructure provisioning instructions, see [Azure Infrastructure Setup](#1.1.1). For the complete workshop workflow overview, see [Workshop Workflow](#1.2).

## Configuration Overview

The workshop requires configuration of two primary connection types: teacher model access through Azure AI Foundry and Azure Machine Learning workspace connectivity. These configurations enable the 7-step distillation pipeline to access cloud resources and manage model artifacts.

```mermaid
graph TB
    subgraph "Environment Configuration"
        ENV["sample.env<br/>Configuration File"]
        LOCAL["local.env<br/>User Copy"]
    end
    
    subgraph "Teacher Model Access"
        TEACHER_NAME["TEACHER_MODEL_NAME<br/>DeepSeek-V3"]
        TEACHER_ENDPOINT["TEACHER_MODEL_ENDPOINT<br/>cognitive.microsoft.com"]
        TEACHER_KEY["TEACHER_MODEL_KEY<br/>API Authentication"]
    end
    
    subgraph "Azure ML Workspace"
        SUB_ID["AZUREML_SUBSCRIPTION_ID<br/>Azure Subscription"]
        RG_NAME["AZUREML_RESOURCE_GROUP<br/>Resource Group"]
        WS_NAME["AZUREML_WS_NAME<br/>Workspace Name"]
    end
    
    subgraph "Development Environment"
        PYTHON310["Python 3.10<br/>AzureML Kernel"]
        PYTORCH["Python 3.10<br/>PyTorch Kernel"]
        LOCAL_ENV["Local Python 3.10+<br/>Edge Device"]
    end
    
    ENV --> LOCAL
    LOCAL --> TEACHER_NAME
    LOCAL --> TEACHER_ENDPOINT
    LOCAL --> TEACHER_KEY
    LOCAL --> SUB_ID
    LOCAL --> RG_NAME
    LOCAL --> WS_NAME
    
    TEACHER_NAME --> PYTHON310
    SUB_ID --> PYTHON310
    SUB_ID --> PYTORCH
    LOCAL_ENV --> LOCAL_ENV
```

Sources: [Lab329/Notebook/sample.env:1-12](), [Lab329/README.md:87-98]()

## Environment File Setup

### Creating the Configuration File

The workshop uses environment variables stored in a configuration file to manage sensitive credentials and workspace identifiers. Create your configuration by copying the sample template:

| Configuration Step | Action | File Location |
|-------------------|--------|---------------|
| 1. Locate template | Find sample configuration | `Lab329/Notebook/sample.env` |
| 2. Create user copy | Copy to working directory | `Lab329/Notebook/local.env` |
| 3. Configure values | Replace placeholder values | Update all variables |
| 4. Secure file | Exclude from version control | Add to `.gitignore` |

The configuration file structure follows this format:

```mermaid
graph LR
    subgraph "sample.env Template"
        TEMPLATE_TEACHER["TEACHER_MODEL_NAME=DeepSeek-V3"]
        TEMPLATE_ENDPOINT["TEACHER_MODEL_ENDPOINT=placeholder"]
        TEMPLATE_KEY["TEACHER_MODEL_KEY=placeholder"]
        TEMPLATE_SUB["AZUREML_SUBSCRIPTION_ID=placeholder"]
        TEMPLATE_RG["AZUREML_RESOURCE_GROUP=placeholder"]
        TEMPLATE_WS["AZUREML_WS_NAME=placeholder"]
    end
    
    subgraph "local.env Configuration"
        USER_TEACHER["TEACHER_MODEL_NAME=DeepSeek-V3"]
        USER_ENDPOINT["TEACHER_MODEL_ENDPOINT=actual-endpoint"]
        USER_KEY["TEACHER_MODEL_KEY=actual-key"]
        USER_SUB["AZUREML_SUBSCRIPTION_ID=actual-subscription"]
        USER_RG["AZUREML_RESOURCE_GROUP=actual-rg"]
        USER_WS["AZUREML_WS_NAME=actual-workspace"]
    end
    
    TEMPLATE_TEACHER --> USER_TEACHER
    TEMPLATE_ENDPOINT --> USER_ENDPOINT
    TEMPLATE_KEY --> USER_KEY
    TEMPLATE_SUB --> USER_SUB
    TEMPLATE_RG --> USER_RG
    TEMPLATE_WS --> USER_WS
```

Sources: [Lab329/Notebook/sample.env:1-12](), [Lab329/README.md:87-98]()

### Teacher Model Configuration

Configure access to the DeepSeek-V3 teacher model deployed through Azure AI Foundry:

| Variable | Purpose | Source Location |
|----------|---------|-----------------|
| `TEACHER_MODEL_NAME` | Model identifier | Fixed as "DeepSeek-V3" |
| `TEACHER_MODEL_ENDPOINT` | API endpoint URL | Azure AI Foundry model overview |
| `TEACHER_MODEL_KEY` | Authentication key | Azure AI Foundry model overview |

The teacher model endpoint follows the pattern defined in the sample configuration: `https://westus3.api.cognitive.microsoft.com/models`.

Sources: [Lab329/Notebook/sample.env:1-4](), [azure.yaml:7-14]()

### Azure ML Workspace Configuration

Configure connectivity to your Azure Machine Learning workspace for model training and registration:

| Variable | Purpose | CLI Command |
|----------|---------|-------------|
| `AZUREML_SUBSCRIPTION_ID` | Azure subscription identifier | `az account show --query id --output tsv` |
| `AZUREML_RESOURCE_GROUP` | Resource group name | `az group list --query "[].name" --output tsv` |
| `AZUREML_WS_NAME` | ML workspace name | `az ml workspace list --query "[].name" --output tsv` |

Alternative configuration methods include downloading the `config.json` file from the Azure Portal resource group or using the Azure ML Studio interface.

Sources: [Lab329/Notebook/sample.env:5-12](), [infra/main.parameters.json:4-14]()

## Development Environment Setup

### Jupyter Kernel Configuration

The workshop notebooks require specific Python environments based on their computational requirements:

```mermaid
graph TB
    subgraph "Azure ML Kernels"
        AZUREML_KERNEL["Python 3.10 - AzureML<br/>Standard compute"]
        PYTORCH_KERNEL["Python 3.10 - PyTorch and TensorFlow<br/>GPU compute"]
    end
    
    subgraph "Local Environment"
        LOCAL_PYTHON["Python 3.10+<br/>Edge device"]
    end
    
    subgraph "Notebook Assignments"
        NB01["01.AzureML_Distillation.ipynb"]
        NB02["02.AzureML_FineTuningAndConvertByMSOlive.ipynb"]
        NB03["03.AzureML_RuningByORTGenAI.ipynb"]
        NB04["04.AzureML_RegisterToAzureML.ipynb"]
        NB05["05.Local_Download.ipynb"]
        NB06["06.Local_Inference.ipynb"]
        NB07["07.Local_inference_AIFoundry.ipynb"]
    end
    
    AZUREML_KERNEL --> NB01
    AZUREML_KERNEL --> NB04
    PYTORCH_KERNEL --> NB02
    PYTORCH_KERNEL --> NB03
    LOCAL_PYTHON --> NB05
    LOCAL_PYTHON --> NB06
    LOCAL_PYTHON --> NB07
```

Sources: [Lab329/README.md:82-86]()

### Execution Environment Requirements

| Environment Type | Requirements | Purpose |
|-----------------|-------------|---------|
| Azure ML Standard | Python 3.10 AzureML kernel | Data generation and model registration |
| Azure ML GPU | Python 3.10 PyTorch kernel, A100 GPU | Model fine-tuning and optimization |
| Local Edge Device | Python 3.10+, sufficient resources | Model download and local inference |

The workshop requires access to H100 or A100 GPU resources for the fine-tuning steps, as specified in the computational requirements.

Sources: [Lab329/README.md:101-102]()

## Authentication and Permissions

### Azure Service Authentication

The workshop requires appropriate Azure permissions for the following services:

```mermaid
graph LR
    subgraph "Authentication Requirements"
        AZURE_SUB["Azure Subscription<br/>Contributor Access"]
        AI_FOUNDRY["Azure AI Foundry<br/>Model Access"]
        AZUREML["Azure ML Workspace<br/>Compute Access"]
        COGNITIVE["Cognitive Services<br/>API Access"]
    end
    
    subgraph "Service Connections"
        DEEPSEEK_API["DeepSeek-V3<br/>API Endpoint"]
        ML_COMPUTE["H100/A100<br/>Compute Resources"]
        MODEL_REGISTRY["Model Registry<br/>Storage Access"]
    end
    
    AZURE_SUB --> AI_FOUNDRY
    AI_FOUNDRY --> DEEPSEEK_API
    AZURE_SUB --> AZUREML
    AZUREML --> ML_COMPUTE
    AZUREML --> MODEL_REGISTRY
    AI_FOUNDRY --> COGNITIVE
    COGNITIVE --> DEEPSEEK_API
```

Sources: [Lab329/README.md:100](), [azure.yaml:4-15]()

### Credential Validation

Verify your configuration by testing the connection to each service:

| Service | Validation Method | Expected Response |
|---------|-------------------|-------------------|
| Teacher Model | API endpoint test | HTTP 200 with model metadata |
| Azure ML Workspace | Workspace list command | Workspace details |
| Subscription Access | Resource group list | Available resource groups |

Sources: [Lab329/Notebook/sample.env:6-9]()

## Configuration Validation

### Environment File Verification

Before executing the workshop notebooks, validate your configuration file contains all required variables with actual values (not placeholders):

| Variable Type | Validation Check | Correct Format |
|--------------|------------------|----------------|
| Model Name | Exact match | `DeepSeek-V3` |
| Endpoint URL | Valid HTTPS URL | `https://westus3.api.cognitive.microsoft.com/models` |
| API Key | Non-placeholder string | Alphanumeric key value |
| Subscription ID | Valid GUID format | 36-character UUID |
| Resource Group | Existing resource group | Matches Azure resource group name |
| Workspace Name | Existing ML workspace | Matches Azure ML workspace name |

### Connection Testing

Test each configured connection before proceeding with the workshop:

```mermaid
graph TD
    subgraph "Validation Steps"
        LOAD_ENV["Load local.env file"]
        TEST_TEACHER["Test teacher model API"]
        TEST_AZUREML["Test Azure ML connection"]
        VERIFY_COMPUTE["Verify compute access"]
        CHECK_PERMISSIONS["Check service permissions"]
    end
    
    subgraph "Expected Results"
        API_SUCCESS["Teacher model responds"]
        ML_SUCCESS["Workspace accessible"]
        COMPUTE_SUCCESS["GPU resources available"]
        PERM_SUCCESS["Full service access"]
    end
    
    LOAD_ENV --> TEST_TEACHER
    TEST_TEACHER --> TEST_AZUREML
    TEST_AZUREML --> VERIFY_COMPUTE
    VERIFY_COMPUTE --> CHECK_PERMISSIONS
    
    TEST_TEACHER --> API_SUCCESS
    TEST_AZUREML --> ML_SUCCESS
    VERIFY_COMPUTE --> COMPUTE_SUCCESS
    CHECK_PERMISSIONS --> PERM_SUCCESS
```

Sources: [Lab329/README.md:87-102]()

The environment configuration establishes the foundation for the complete model distillation workflow, enabling seamless execution of the 7-step process from data generation through edge deployment.

---

