<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-python · page 2 Installation and Setup · fetched 2026-10-26 -->

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [src/openai/__init__.py](src/openai/__init__.py)
- [src/openai/_base_client.py](src/openai/_base_client.py)
- [src/openai/_client.py](src/openai/_client.py)
- [src/openai/_version.py](src/openai/_version.py)
- [src/openai/lib/azure.py](src/openai/lib/azure.py)
- [src/openai/resources/beta/realtime/realtime.py](src/openai/resources/beta/realtime/realtime.py)
- [src/openai/resources/realtime/realtime.py](src/openai/resources/realtime/realtime.py)
- [tests/lib/test_azure.py](tests/lib/test_azure.py)
- [tests/test_client.py](tests/test_client.py)
- [tests/test_utils/test_logging.py](tests/test_utils/test_logging.py)

</details>



This page covers the basic installation process for the OpenAI Python library and initial setup steps. For detailed configuration options including timeouts, retries, and custom HTTP clients, see [Client Configuration](#2.1). For Azure-specific setup, see [Azure OpenAI Configuration](#2.2).

## Installation

### Installing from PyPI

The OpenAI Python library is available on PyPI and can be installed using pip:

```bash
pip install openai
```

The library requires **Python 3.10 or higher**.

Sources: [README.md:18-22](), [pyproject.toml:22](), [CHANGELOG.md:9]()

### Optional Dependencies

The library supports optional feature sets that can be installed as needed via `project.optional-dependencies`:

| Feature Group | Installation Command | Purpose |
|---------------|---------------------|---------|
| `aiohttp` | `pip install openai[aiohttp]` | Alternative async HTTP client support [pyproject.toml:45-48]() |
| `httpx2` | `pip install openai[httpx2]` | Experimental support for HTTPX2 clients [pyproject.toml:49-53](), [CHANGELOG.md:26]() |
| `realtime` | `pip install openai[realtime]` | WebSocket support for Realtime API [pyproject.toml:54]() |
| `datalib` | `pip install openai[datalib]` | NumPy and Pandas integration for data processing [pyproject.toml:55]() |
| `voice_helpers` | `pip install openai[voice_helpers]` | Audio device and numpy support for voice [pyproject.toml:56]() |
| `bedrock` | `pip install openai[bedrock]` | Support for Amazon Bedrock [pyproject.toml:57-59]() |

Sources: [pyproject.toml:44-60](), [README.md:245-249]()

### Core Dependencies

The library relies on several key packages to handle networking, validation, and async concurrency:

**Package Dependency Graph**

```mermaid
graph TB
    ["openai"] --> ["httpx >= 0.23.0, < 1"]
    ["openai"] --> ["pydantic >= 1.9.0, < 3"]
    ["openai"] --> ["typing-extensions >= 4.14, < 5"]
    ["openai"] --> ["anyio >= 3.5.0, < 5"]
    ["openai"] --> ["distro >= 1.7.0, < 2"]
    ["openai"] --> ["sniffio"]
    ["openai"] --> ["jiter >= 0.10.0, < 1"]
    
    ["httpx"] -.provides.-> ["SyncAPIClient"]
    ["httpx"] -.provides.-> ["AsyncAPIClient"]
    
    ["pydantic"] -.validates.-> ["BaseModel"]
    
    ["anyio"] -.supports.-> ["Async Operations"]
```

Sources: [pyproject.toml:11-20]()

## Verifying Installation

### Check Installed Version

After installation, verify the library is correctly installed and check its version:

```python
import openai
print(openai.__version__)  # e.g., "2.49.0"
```

The version string is defined in `src/openai/_version.py` and is synchronized with the project metadata via `release-please`.

Sources: [src/openai/_version.py:3-4](), [pyproject.toml:3](), [.release-please-manifest.json:2]()

### Quick Installation Test

Test basic functionality with a minimal example using the `Responses` API:

```python
from openai import OpenAI

# This will initialize the client (but not make API calls yet)
client = OpenAI()
print("OpenAI client initialized successfully")
```

Sources: [README.md:30-36]()

## Basic Setup

### API Key Configuration

The library requires an OpenAI API key for authentication. The client constructor infers these from environment variables if not provided.

**Method 1: Environment Variable (Recommended)**

Set the `OPENAI_API_KEY` environment variable. The client reads this during initialization.

```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Method 2: Direct Parameter**

Pass the API key directly to the `OpenAI` or `AsyncOpenAI` constructor:

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key-here")
```

**Method 3: Workload Identity (Advanced)**

For secure cloud environments (K8s, Azure, GCP), you can use `workload_identity` with short-lived tokens.

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider("/var/run/secrets/tokens"),
    }
)
```

Sources: [src/openai/_client.py:127-156](), [README.md:74-95]()

### Client Initialization

The library provides specialized clients for different execution models and providers:

**Client Entity Mapping**

```mermaid
graph TD
    subgraph "Natural Language Space"
        ["Synchronous Operations"]
        ["Asynchronous Operations"]
        ["Azure Cloud Provider"]
        ["Amazon Bedrock Provider"]
    end

    subgraph "Code Entity Space"
        ["OpenAI (src/openai/_client.py)"]
        ["AsyncOpenAI (src/openai/_client.py)"]
        ["AzureOpenAI (src/openai/lib/azure.py)"]
        ["BedrockOpenAI (src/openai/lib/bedrock.py)"]
        
        ["SyncAPIClient (src/openai/_base_client.py)"]
        ["AsyncAPIClient (src/openai/_base_client.py)"]
    end

    ["Synchronous Operations"] --- ["OpenAI (src/openai/_client.py)"]
    ["Asynchronous Operations"] --- ["AsyncOpenAI (src/openai/_client.py)"]
    ["Azure Cloud Provider"] --- ["AzureOpenAI (src/openai/lib/azure.py)"]
    ["Amazon Bedrock Provider"] --- ["BedrockOpenAI (src/openai/lib/bedrock.py)"]

    ["OpenAI (src/openai/_client.py)"] -- inherits --> ["SyncAPIClient (src/openai/_base_client.py)"]
    ["AzureOpenAI (src/openai/lib/azure.py)"] -- inherits --> ["SyncAPIClient (src/openai/_base_client.py)"]
    ["BedrockOpenAI (src/openai/lib/bedrock.py)"] -- inherits --> ["OpenAI (src/openai/_client.py)"]
```

Sources: [src/openai/_client.py:106](), [src/openai/_client.py:286](), [src/openai/lib/azure.py:101](), [src/openai/__init__.py:83-84]()

### Environment Variables

The library recognizes several environment variables during initialization:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Primary API authentication [src/openai/_client.py:160]() |
| `OPENAI_ADMIN_KEY` | Admin API authentication [src/openai/_client.py:161]() |
| `OPENAI_ORG_ID` | Organization identifier [src/openai/_client.py:162]() |
| `OPENAI_PROJECT_ID` | Project identifier [src/openai/_client.py:163]() |
| `AZURE_OPENAI_ENDPOINT` | Azure-specific endpoint [src/openai/__init__.py:165]() |

Sources: [src/openai/_client.py:159-167](), [src/openai/__init__.py:161-168]()

## Advanced Configuration Overview

### Timeout and Retry Configuration

The default timeout is **10 minutes** [src/openai/_constants.py:84]() and the default maximum retries is **2** [src/openai/_constants.py:86]().

```python
from openai import OpenAI

client = OpenAI(
    timeout=20.0,
    max_retries=5
)
```

For details, see [Client Configuration](#2.1).

### Module-Level API Usage

For convenience, the library supports a module-level API using a global client proxy `_ModuleClient`.

```python
import openai

openai.api_key = "..."
response = openai.chat.completions.create(model="gpt-5.5", messages=[...])
```

For details, see [Module-Level API Usage](#2.3).

Sources: [src/openai/__init__.py:176-240](), [src/openai/lib/_old_api.py:1-20]()

---

