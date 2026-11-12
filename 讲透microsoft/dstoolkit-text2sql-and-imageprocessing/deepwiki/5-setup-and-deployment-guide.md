<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/dstoolkit-text2sql-and-imageprocessing · page 5 Setup and Deployment Guide · fetched 2026-10-26 -->

# Setup and Deployment Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.devcontainer/Dockerfile](.devcontainer/Dockerfile)
- [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/dependabot.yaml](.github/dependabot.yaml)
- [.github/workflows/codeql-analysis.yaml](.github/workflows/codeql-analysis.yaml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SUPPORT.md](SUPPORT.md)
- [text_2_sql/.env.example](text_2_sql/.env.example)
- [text_2_sql/GETTING_STARTED.md](text_2_sql/GETTING_STARTED.md)
- [text_2_sql/README.md](text_2_sql/README.md)

</details>



This guide provides comprehensive instructions for setting up and deploying the DSTToolkit Text2SQL and Image Processing systems. The guide covers prerequisite Azure resources, environment configurations, code installation, and deployment steps for both systems.

## Overview and Prerequisites

Before beginning the setup process, ensure you have the following:

1. An Azure subscription with permissions to create resources
2. Python 3.11 or higher installed
3. Git installed to clone the repository
4. Access to create and manage the following Azure resources:
   - Azure OpenAI with GPT-4o-mini model and embedding models
   - Azure SQL Server (or other supported database)
   - Azure AI Search service
   - Azure Storage Account
   - Azure Document Intelligence (for image processing)

Sources: [text_2_sql/README.md:3-5](), [text_2_sql/GETTING_STARTED.md:1-7](), [pyproject.toml:3-6]()

## Deployment Architecture

The setup involves deploying several interconnected components across both systems. Here's the high-level deployment architecture:

```mermaid
flowchart TD
    subgraph "Azure Resources"
        AOAI["Azure OpenAI Service"]
        AIS["Azure AI Search"]
        SA["Azure Storage Account"]
        DB[(Database)]
        ADI["Azure Document Intelligence"]
    end

    subgraph "Text2SQL Components"
        T2S["Text2SQL Core"]
        DD["Data Dictionary"]
        AGen["AutoGen Implementation"]
    end

    subgraph "Image Processing Components"
        IP["Image Processing Pipeline"]
    end

    subgraph "Local Dev Environment"
        DevCont["Dev Container / Local Setup"]
    end

    DevCont -->|1. Clone & Configure| T2S
    DevCont -->|1. Clone & Configure| IP
    DevCont -->|2. Deploy Indexes| AIS
    DevCont -->|3. Generate & Upload| DD
    DD -->|4. Store| SA
    SA -->|5. Index| AIS
    T2S -->|6. Connect| AOAI
    T2S -->|6. Connect| AIS
    T2S -->|6. Connect| DB
    AGen -->|7. Use| T2S
    IP -->|8. Connect| AOAI
    IP -->|8. Connect| ADI
    IP -->|8. Connect| AIS
    IP -->|8. Connect| SA
```

Sources: [text_2_sql/GETTING_STARTED.md:1-27](), [pyproject.toml:24-31]()

## 1. Repository Setup

Begin by cloning the repository and setting up your development environment.

### Local Setup

```bash
# Clone the repository
git clone https://github.com/microsoft/dstoolkit-text2sql-and-imageprocessing.git
cd dstoolkit-text2sql-and-imageprocessing
```

### Dev Container Setup (Optional)

The repository includes a development container configuration for Visual Studio Code:

1. Install Docker
2. Install the VS Code Remote Development extension
3. Open the repository in VS Code
4. When prompted, click "Reopen in Container"

The dev container includes all necessary tools and dependencies, including:
- Python 3.x
- ODBC drivers for SQL Server
- Azure CLI
- uv package manager

Sources: [.devcontainer/Dockerfile:1-20](), [.devcontainer/devcontainer.json:1-24]()

## 2. Azure Resources Deployment

Before continuing with code setup, you must provision the necessary Azure resources.

### Required Azure Resources

```mermaid
flowchart LR
    subgraph "Core Azure Resources"
        direction TB
        AOAI["Azure OpenAI Service"]
        AIS["Azure AI Search"]
        SA["Azure Storage Account"]
    end

    subgraph "Database Options"
        TSQL["Azure SQL Server"]
        PG["PostgreSQL"]
        SF["Snowflake"]
        DB["Databricks"]
        SL["SQLite"]
    end

    subgraph "Image Processing"
        ADI["Azure Document Intelligence"]
    end

    DEV["Developer"] -->|"Provision"| AOAI
    DEV -->|"Provision"| AIS
    DEV -->|"Provision"| SA
    DEV -->|"Provision (one or more)"| TSQL
    DEV -->|"Provision (one or more)"| PG
    DEV -->|"Provision (one or more)"| SF
    DEV -->|"Provision (one or more)"| DB
    DEV -->|"Provision (one or more)"| SL
    DEV -->|"Provision (for image processing)"| ADI
```

Sources: [text_2_sql/GETTING_STARTED.md:7-7](), [deploy_ai_search_indexes/pyproject.toml:10-17](), [image_processing/pyproject.toml:10-35]()

## 3. AI Search Indexes Deployment

The system requires several AI Search indexes for its operation. Follow these steps to deploy them:

```bash
# Navigate to the deploy_ai_search_indexes directory
cd deploy_ai_search_indexes

# Create a .env file from the example
cp .env.example .env

# Edit the .env file with your Azure resource information
# Install dependencies
uv sync

# Deploy the AI Search indexes
python -m deploy_ai_search_indexes.deploy
```

The deployment creates the following indexes:
- Schema Store Index - for database schema metadata 
- Column Value Store Index - for sample data values
- Query Cache Index - for caching previously executed queries

Sources: [text_2_sql/GETTING_STARTED.md:7-9](), [deploy_ai_search_indexes/pyproject.toml:10-17]()

## 4. Data Dictionary Generation and Upload

The Data Dictionary is crucial for the Text2SQL system to understand your database schema:

```mermaid
flowchart TD
    subgraph "Data Dictionary Generation"
        DC["Data Dictionary Creator"]
        DC -->|"Select Database Type"| Creators
        
        subgraph "Creators"
            TSQLC["TSQL Creator"]
            PGC["Postgres Creator"]
            SFC["Snowflake Creator"]
            DBC["Databricks Creator"]
            SQLC["SQLite Creator"]
        end
        
        TSQLC -->|"Generate"| Json["JSON Schema Files"]
        PGC -->|"Generate"| Json
        SFC -->|"Generate"| Json
        DBC -->|"Generate"| Json
        SQLC -->|"Generate"| Json
        
        Json -->|"Generate"| CVS["Column Value Store JSONL"]
    end
    
    subgraph "Upload & Index"
        Json -->|"Upload"| SA["Storage Account"]
        CVS -->|"Upload"| SA
        SA -->|"Index"| AIS["AI Search"]
    end
```

### Steps:

1. Set up your database connection in the `.env` file:

```bash
cd text_2_sql_core
cp .env.example .env
# Edit the .env file with your database connection details
```

2. Generate the data dictionary for your database:

```bash
# For SQL Server
python -m text_2_sql_core.data_dictionary.tsql_data_dictionary_creator

# For PostgreSQL
python -m text_2_sql_core.data_dictionary.postgres_data_dictionary_creator

# For other supported databases
# Use the corresponding creator module
```

3. Upload the generated files to Azure Storage Account containers, which will be automatically indexed.

Sources: [text_2_sql/README.md:134-204](), [text_2_sql/GETTING_STARTED.md:17-19](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/postgres_data_dictionary_creator.py:1-121]()

## 5. Text2SQL Core Setup

Set up the Text2SQL core component:

```bash
# Navigate to text_2_sql_core
cd text_2_sql_core

# Create environment file
cp .env.example .env
# Edit the .env file with your configuration

# Install dependencies
uv sync

# For additional database connectors, install optional dependencies
# For PostgreSQL
uv sync --extra postgres

# For Snowflake
uv sync --extra snowflake

# For Databricks
uv sync --extra databricks

# For SQLite
uv sync --extra sqlite
```

### Environment Configuration Options

The `.env` file contains various configuration options that allow you to customize the behavior of the Text2SQL system:

#### Authentication Options

```
IdentityType=<identityType>  # Can be system_assigned, user_assigned, or key
```

#### Text2SQL Core Options

```
Text2Sql__DatabaseEngine=<DatabaseEngine>  # TSQL, Postgres, Snowflake, Databricks, or SQLite
Text2Sql__UseQueryCache=<Boolean>  # Determines if the Query Cache will be used (default: True)
Text2Sql__PreRunQueryCache=<Boolean>  # Determines if results from Query Cache will be pre-run (default: True)
Text2Sql__UseColumnValueStore=<Boolean>  # Determines if Column Value Store will be used (default: True)
Text2Sql__GenerateFollowUpSuggestions=<Boolean>  # Determines if follow-up questions will be generated (default: True)
Text2Sql__RowLimit=<Integer>  # Maximum number of rows returned in a query (default: 100)
```

#### Azure OpenAI Configuration

```
OpenAI__CompletionDeployment=<openAICompletionDeploymentId>  # Used for data dictionary creator
OpenAI__MiniCompletionDeployment=<OpenAIMiniCompletionDeploymentId>  # Used for agentic text2sql
OpenAI__Endpoint=<openAIEndpoint>
OpenAI__ApiKey=<openAIKey>  # Only needed if not using identity-based authentication
OpenAI__ApiVersion=<openAIApiVersion>
```

#### Azure AI Search Configuration

```
AIService__AzureSearchOptions__Endpoint=<AI search endpoint>
AIService__AzureSearchOptions__Key=<AI search key>  # Only needed if not using identity-based authentication
AIService__AzureSearchOptions__Text2SqlSchemaStore__Index=<Schema store index name>
AIService__AzureSearchOptions__Text2SqlSchemaStore__SemanticConfig=<Schema store semantic config>
AIService__AzureSearchOptions__Text2SqlQueryCache__Index=<Query cache index name>
AIService__AzureSearchOptions__Text2SqlQueryCache__SemanticConfig=<Query cache semantic config>
AIService__AzureSearchOptions__Text2SqlColumnValueStore__Index=<Column value store index name>
```

Customize these options to tailor the Text2SQL system to your specific needs.

Sources: [text_2_sql/GETTING_STARTED.md:11-16](), [text_2_sql/.env.example:1-50]()

## 6. AutoGen Implementation Setup

The AutoGen implementation uses the Text2SQL core to provide an agentic approach:

```bash
# Navigate to autogen directory
cd autogen

# Install dependencies
uv sync

# For additional database connectors
uv sync --extra <DATABASE_ENGINE>
```

Once set up, you can test the implementation by running the provided notebook:
```bash
# Open and run the notebook
jupyter notebook "Iteration 5 - Agentic Vector Based Text2SQL.ipynb"
```

Sources: [text_2_sql/GETTING_STARTED.md:21-27](), [text_2_sql/README.md:38-56]()

## 7. Image Processing Setup

Set up the Image Processing component:

```bash
# Navigate to image_processing
cd image_processing

# Create environment file
cp .env.example .env
# Edit the .env file with your configuration

# Install dependencies
uv sync
```

The `.env` file should include configuration for:
- Azure OpenAI API key and endpoint
- Azure Document Intelligence key and endpoint
- Azure AI Search key and endpoint
- Azure Storage Account connection details

Sources: [image_processing/pyproject.toml:1-51]()

## 8. Database Connector Configuration

The system supports multiple database engines through a connector factory pattern. Configure the appropriate connector based on your database:

### TSQL (SQL Server)

Required environment variables:
```
Text2Sql__DatabaseEngine=TSQL
Text2Sql__Tsql__ConnectionString=your-connection-string
Text2Sql__Tsql__Database=your-database
```

### PostgreSQL

Required environment variables:
```
Text2Sql__DatabaseEngine=Postgres
# Option 1: Connection string
Text2Sql__Postgres__ConnectionString=postgresql://username:password@hostname:port/database

# Option 2: Individual parameters
Text2Sql__Postgres__Database=your-database
Text2Sql__Postgres__User=your-username
Text2Sql__Postgres__Password=your-password
Text2Sql__Postgres__Port=5432
Text2Sql__Postgres__ServerHostname=your-server-hostname
```

### Snowflake

Required environment variables:
```
Text2Sql__DatabaseEngine=Snowflake
Text2Sql__Snowflake__User=your-snowflake-user
Text2Sql__Snowflake__Password=your-snowflake-password
Text2Sql__Snowflake__Account=your-snowflake-account
Text2Sql__Snowflake__Warehouse=your-snowflake-warehouse
Text2Sql__Snowflake__Database=your-snowflake-database
```

### Databricks

Required environment variables:
```
Text2Sql__DatabaseEngine=Databricks
Text2Sql__Databricks__Catalog=your-databricks-catalog
Text2Sql__Databricks__ServerHostname=your-databricks-server-hostname
Text2Sql__Databricks__HttpPath=your-databricks-http-path
Text2Sql__Databricks__AccessToken=your-databricks-access-token
```

### SQLite

Required environment variables:
```
Text2Sql__DatabaseEngine=SQLite
Text2Sql__SQLite__ConnectionString=your-sqlite-connection-string
```

Sources: [text_2_sql/.env.example:4-50]()

## 9. Production Deployment Considerations

When deploying to production, consider the following:

### Security Recommendations

1. Use managed identities for Azure resources where possible
2. Limit database permissions to read-only for the Text2SQL service
3. Add validation of SQL queries before execution
4. Consider data masking for sensitive columns

```mermaid
flowchart LR
    subgraph "Security Considerations"
        direction TB
        MI["Managed Identities"]
        RP["Read-Only Permissions"]
        SQ["SQL Query Validation"]
        DM["Data Masking"]
        RLS["Row Level Security"]
    end

    User["End User"] -->|"Access"| App["Application"]
    App -->|"Uses"| T2S["Text2SQL"]
    T2S -->|"Executes"| SQ
    SQ -->|"Validates"| DB["Database"]
    DB -->|"Applies"| RLS
    DB -->|"Applies"| DM
    T2S -->|"Uses"| MI
    DB -->|"Grants"| RP
```

### Performance Optimization

1. Pre-populate the query cache with common questions
2. Implement an effective caching strategy
3. Use pre-assembled views to avoid complex joins
4. Consider scaling options for the Azure resources

Sources: [text_2_sql/README.md:220-229](), [text_2_sql/README.md:76-83]()

## 10. Troubleshooting

### Common Issues

| Issue | Possible Solution |
|-------|------------------|
| Connection errors to Azure resources | Verify network connectivity, check firewall settings, ensure correct connection strings |
| Data dictionary generation failures | Verify database permissions, check connection details |
| SQL query execution errors | Validate SQL syntax, check database permissions, verify column names |
| Image processing failures | Ensure Document Intelligence service is properly configured, check file format support |
| Cache indexing issues | Check storage account permissions, verify index definitions |

### Logging

The system uses Python's logging module. To enable detailed logging, set the log level in your environment variables:

```
LOGGING_LEVEL=DEBUG
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/postgres_sql.py:80-132]()

## 11. Development Tools

The repository includes several development tools:

1. **Pre-commit hooks**: Run quality checks before committing
   ```bash
   # Install pre-commit
   pip install pre-commit
   pre-commit install
   ```

2. **Dev Container**: Provides a consistent development environment

3. **UV Package Manager**: Used for dependency management
   ```bash
   # Update dependencies
   uv sync
   ```

4. **Code Formatting**: Uses Black and Ruff for code formatting

Sources: [.pre-commit-config.yaml:1-57]()

## Conclusion

This guide provides the essential steps to set up and deploy the DSTToolkit Text2SQL and Image Processing systems. Follow the steps in sequence to ensure a proper setup. For advanced configurations or customizations, refer to the source code and READMEs in the respective directories.

For issues or support, please refer to the [SUPPORT.md]() file or create an issue in the GitHub repository.