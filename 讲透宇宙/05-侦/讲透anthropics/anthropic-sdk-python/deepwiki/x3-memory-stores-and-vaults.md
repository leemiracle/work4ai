<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/anthropic-sdk-python · extra page Memory Stores and Vaults · fetched 2026-10-26 -->

# Memory Stores and Vaults

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/anthropic/resources/beta/memory_stores/memories.py](src/anthropic/resources/beta/memory_stores/memories.py)
- [src/anthropic/resources/beta/memory_stores/memory_stores.py](src/anthropic/resources/beta/memory_stores/memory_stores.py)
- [src/anthropic/resources/beta/memory_stores/memory_versions.py](src/anthropic/resources/beta/memory_stores/memory_versions.py)
- [src/anthropic/resources/beta/vaults/credentials.py](src/anthropic/resources/beta/vaults/credentials.py)
- [src/anthropic/resources/beta/vaults/vaults.py](src/anthropic/resources/beta/vaults/vaults.py)
- [src/anthropic/resources/files.py](src/anthropic/resources/files.py)
- [src/anthropic/types/beta/beta_managed_agents_deleted_vault.py](src/anthropic/types/beta/beta_managed_agents_deleted_vault.py)
- [src/anthropic/types/beta/beta_managed_agents_memory_store.py](src/anthropic/types/beta/beta_managed_agents_memory_store.py)
- [src/anthropic/types/beta/beta_managed_agents_vault.py](src/anthropic/types/beta/beta_managed_agents_vault.py)
- [src/anthropic/types/beta/memory_store_create_params.py](src/anthropic/types/beta/memory_store_create_params.py)
- [src/anthropic/types/beta/memory_store_list_params.py](src/anthropic/types/beta/memory_store_list_params.py)
- [src/anthropic/types/beta/memory_store_update_params.py](src/anthropic/types/beta/memory_store_update_params.py)
- [src/anthropic/types/beta/memory_stores/beta_managed_agents_api_actor.py](src/anthropic/types/beta/memory_stores/beta_managed_agents_api_actor.py)
- [src/anthropic/types/beta/memory_stores/beta_managed_agents_deleted_memory.py](src/anthropic/types/beta/memory_stores/beta_managed_agents_deleted_memory.py)
- [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory.py](src/anthropic/types/beta/memory_stores/beta_managed_agents_memory.py)
- [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_prefix.py](src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_prefix.py)
- [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py](src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py)
- [src/anthropic/types/beta/memory_stores/beta_managed_agents_service_account_actor.py](src/anthropic/types/beta/memory_stores/beta_managed_agents_service_account_actor.py)
- [src/anthropic/types/beta/memory_stores/beta_managed_agents_session_actor.py](src/anthropic/types/beta/memory_stores/beta_managed_agents_session_actor.py)
- [src/anthropic/types/beta/memory_stores/beta_managed_agents_user_actor.py](src/anthropic/types/beta/memory_stores/beta_managed_agents_user_actor.py)
- [src/anthropic/types/beta/memory_stores/memory_create_params.py](src/anthropic/types/beta/memory_stores/memory_create_params.py)
- [src/anthropic/types/beta/memory_stores/memory_list_params.py](src/anthropic/types/beta/memory_stores/memory_list_params.py)
- [src/anthropic/types/beta/memory_stores/memory_retrieve_params.py](src/anthropic/types/beta/memory_stores/memory_retrieve_params.py)
- [src/anthropic/types/beta/memory_stores/memory_update_params.py](src/anthropic/types/beta/memory_stores/memory_update_params.py)
- [src/anthropic/types/beta/memory_stores/memory_version_list_params.py](src/anthropic/types/beta/memory_stores/memory_version_list_params.py)
- [src/anthropic/types/beta/memory_stores/memory_version_retrieve_params.py](src/anthropic/types/beta/memory_stores/memory_version_retrieve_params.py)
- [src/anthropic/types/beta/vault_list_params.py](src/anthropic/types/beta/vault_list_params.py)
- [src/anthropic/types/beta/vaults/beta_managed_agents_credential_validation.py](src/anthropic/types/beta/vaults/beta_managed_agents_credential_validation.py)
- [src/anthropic/types/beta/vaults/beta_managed_agents_deleted_credential.py](src/anthropic/types/beta/vaults/beta_managed_agents_deleted_credential.py)
- [src/anthropic/types/beta/vaults/beta_managed_agents_mcp_oauth_auth_response.py](src/anthropic/types/beta/vaults/beta_managed_agents_mcp_oauth_auth_response.py)
- [src/anthropic/types/beta/vaults/beta_managed_agents_mcp_oauth_create_params.py](src/anthropic/types/beta/vaults/beta_managed_agents_mcp_oauth_create_params.py)
- [src/anthropic/types/beta/vaults/beta_managed_agents_mcp_oauth_update_params.py](src/anthropic/types/beta/vaults/beta_managed_agents_mcp_oauth_update_params.py)
- [src/anthropic/types/beta/vaults/credential_list_params.py](src/anthropic/types/beta/vaults/credential_list_params.py)
- [src/anthropic/types/beta/vaults/credential_update_params.py](src/anthropic/types/beta/vaults/credential_update_params.py)
- [src/anthropic/types/file_upload_params.py](src/anthropic/types/file_upload_params.py)
- [tests/api_resources/beta/sessions/test_resources.py](tests/api_resources/beta/sessions/test_resources.py)
- [tests/api_resources/beta/vaults/test_credentials.py](tests/api_resources/beta/vaults/test_credentials.py)

</details>



## 1. Purpose and Scope

This page documents the technical implementation of **Memory Stores** and **Vaults** within the Anthropic Python SDK (`https://github.com/anthropics/anthropic-sdk-python`). These features are part of the managed agents beta system, enabling agents to persist context across interactions via filesystem-mounted memory stores (`/mnt/memory/`), track item versions and path prefixes, record fine-grained actor attribution, and securely manage secrets, credentials, and MCP (Model Context Protocol) OAuth flows using vaults.

---

## 2. Memory Stores, Memories, and Versioning

Memory stores are named, workspace-scoped containers for agent memories (`BetaManagedAgentsMemoryStore`) [src/anthropic/types/beta/beta_managed_agents_memory_store.py:10-14](). When attached to a session, a store mounts as a directory under `/mnt/memory/`, allowing agents to read and write notes or files.

### Core Data Models and Operations

* **Memory Stores (`MemoryStores`, `AsyncMemoryStores`)**: Created via `client.beta.memory_stores.create()` [src/anthropic/resources/beta/memory_stores/memory_stores.py:72-160](), accepting a `name`, optional `description`, and `metadata` (up to 16 key-value pairs) [src/anthropic/types/beta/beta_managed_agents_memory_store.py:44-51]().
* **Memories (`Memories`, `AsyncMemories`)**: Individual text files stored within a memory store under a specific path (e.g., `/projects/foo/notes.md`) [src/anthropic/resources/beta/memory_stores/memories.py:53-143](). Created using `client.beta.memory_stores.memories.create()` with a maximum size of 100 kB (102,400 bytes).
* **Memory Versions (`MemoryVersions`, `AsyncMemoryVersions`)**: Every mutation to a memory (creation, modification, deletion) creates an immutable `BetaManagedAgentsMemoryVersion` record [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py:12-20]().

```
+---------------------------------------------------------------------------------+
|                       Natural Language Space / Agent                            |
|  - Agent reads/writes files under /mnt/memory/ in mounted BetaManagedAgentsSession|
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                         Code Entity Space (SDK Resources)                       |
|  - client.beta.memory_stores.create() -> BetaManagedAgentsMemoryStore           |
|  - client.beta.memory_stores.memories.create() -> BetaManagedAgentsMemory       |
|  - client.beta.memory_stores.memory_versions.retrieve() -> BetaManagedAgentsMemoryVersion|
+---------------------------------------------------------------------------------+
```

Sources:
- `src/anthropic/resources/beta/memory_stores/memory_stores.py` [src/anthropic/resources/beta/memory_stores/memory_stores.py:1-168]()
- `src/anthropic/resources/beta/memory_stores/memories.py` [src/anthropic/resources/beta/memory_stores/memories.py:1-156]()
- `src/anthropic/resources/beta/memory_stores/memory_versions.py` [src/anthropic/resources/beta/memory_stores/memory_versions.py:1-157]()
- `src/anthropic/types/beta/beta_managed_agents_memory_store.py` [src/anthropic/types/beta/beta_managed_agents_memory_store.py:1-67]()
- `src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py` [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py:1-101]()

---

## 3. Memory Versions, Prefixes, and Actor Types

### Memory Versions & Operations
Each memory version tracks state via `BetaManagedAgentsMemoryVersionOperation` (`created`, `modified`, or `deleted`) [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py:40-41](). Versions support redaction, which nullifies `content`, `path`, `content_size_bytes`, and `content_sha256` while retaining audit timestamps (`redacted_at`) [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py:17-18]().

### Prefixes and Depth Listing
When listing memories (`client.beta.memory_stores.memories.list()`), callers can specify a `path_prefix` and `depth`:
* `depth=0` (default): Lists all memories below the prefix [src/anthropic/types/beta/memory_stores/memory_list_params.py:13-20]().
* `depth=1`: Lists direct children; deeper paths are grouped into `BetaManagedAgentsMemoryPrefix` items.

### Actor Types
Changes to memories are attributed via `BetaManagedAgentsActor` unions, distinguishing who performed the write:
* `session_actor`: An agent writing through the mounted filesystem [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py:69-70]().
* `api_actor`: Writes originating from direct API keys.
* `user_actor`: End-user actions.
* `service_account_actor`: Automated service accounts (`svac_...`) [src/anthropic/types/beta/memory_stores/memory_version_list_params.py:48-50]().

```
+---------------------------------------------------------------------------------+
|                      Natural Language Space / Audit Trails                      |
|  - Actor attribution (who modified the memory: agent session vs API key)        |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                         Code Entity Space (SDK Models)                          |
|  - BetaManagedAgentsActor union (session_actor, api_actor, user_actor, ...)     |
|  - BetaManagedAgentsMemoryVersion (operation, redacted_at, content_sha256)      |
|  - BetaManagedAgentsMemoryPrefix (depth grouping for path_prefix queries)       |
+---------------------------------------------------------------------------------+
```

Sources:
- `src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py` [src/anthropic/types/beta/memory_stores/beta_managed_agents_memory_version.py:1-101]()
- `src/anthropic/types/beta/memory_stores/memory_list_params.py` [src/anthropic/types/beta/memory_stores/memory_list_params.py:1-68]()
- `src/anthropic/resources/beta/memory_stores/memory_versions.py` [src/anthropic/resources/beta/memory_stores/memory_versions.py:1-157]()

---

## 4. Vaults, Credentials, and MCP OAuth Credential Flows

**Vaults** (`Vaults`, `AsyncVaults`) and their nested **Credentials** resource (`Credentials`, `AsyncCredentials`) provide secure storage for secrets, tokens, and MCP connection parameters [tests/api_resources/beta/vaults/test_credentials.py:21-49]().

### Vaults and Credentials Architecture

```
+---------------------------------------------------------------------------------+
|                        Natural Language Space / Secrets                         |
|  - Secure secret storage, MCP server authentication tokens, OAuth grants        |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                         Code Entity Space (SDK Resources)                       |
|  - client.beta.vaults.create() -> BetaManagedAgentsVault                        |
|  - client.beta.vaults.credentials.create() -> BetaManagedAgentsCredential       |
|  - client.beta.vaults.credentials.update() -> BetaManagedAgentsCredential       |
+---------------------------------------------------------------------------------+
```

* **Vaults (`BetaManagedAgentsVault`)**: Named workspace-scoped containers for credentials.
* **Credentials (`BetaManagedAgentsCredential`)**: Store authentication payloads (`auth` parameter dictionary) such as `static_bearer` tokens [tests/api_resources/beta/vaults/test_credentials.py:28-32]() or MCP server URLs (`mcp_server_url`).
* **MCP OAuth Credential Flows**: Vault credentials support OAuth integration flows for Model Context Protocol servers, allowing agents to securely authenticate against external MCP tools and endpoints using managed tokens.

Sources:
- `tests/api_resources/beta/vaults/test_credentials.py` [tests/api_resources/beta/vaults/test_credentials.py:1-161]()
- `src/anthropic/resources/beta/vaults/vaults.py` [src/anthropic/resources/beta/vaults/vaults.py:1-1]()
- `src/anthropic/resources/beta/vaults/credentials.py` [src/anthropic/resources/beta/vaults/credentials.py:1-1]()
- `src/anthropic/types/beta/beta_managed_agents_vault.py` [src/anthropic/types/beta/beta_managed_agents_vault.py:1-1]()

---

