<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/OSMO · page 8 Authentication and Security · fetched 2026-10-26 -->

# Authentication and Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



## Purpose and Scope

This document describes OSMO's authentication and security architecture, including OAuth2/OIDC integration, credential encryption, and access control mechanisms. It covers how users, CLI clients, and backend operators authenticate with the platform, and how sensitive data is encrypted at rest.

For specific configuration details, see:
- Keycloak SSO setup: [Keycloak SSO Integration](#8.1)
- Envoy proxy configuration: [Envoy Authentication Proxy](#8.2)
- Credential encryption implementation: [Credential Management and Encryption](#8.3)

For deployment instructions, refer to [Deployment Options Comparison](#2.2) and [Deploying a Backend](#5.2).

---

## Authentication Architecture Overview

OSMO implements a multi-tier authentication system with three primary authentication methods and centralized encryption for sensitive data.

### High-Level Authentication Flow

```mermaid
graph TB
    subgraph "Authentication Methods"
        Browser["Browser Users<br/>(OAuth2 Authorization Code)"]
        CLI["CLI Users<br/>(OAuth2 Device Flow)"]
        Backend["Backend Operators<br/>(Service Tokens)"]
    end
    
    subgraph "Identity Provider"
        Keycloak["Keycloak<br/>OAuth2/OIDC Provider"]
    end
    
    subgraph "OSMO Control Plane"
        Envoy["Envoy Sidecars<br/>JWT Validation"]
        API["API Service"]
        UIService["Web UI Service"]
    end
    
    subgraph "Security Layer"
        SecretManager["SecretManager<br/>src/utils/secret_manager.py"]
        MEK["Master Encryption Key<br/>(JWK Format)"]
        UEK["User Encryption Keys<br/>(Per-User)"]
    end
    
    subgraph "Data Store"
        PostgreSQL[("PostgreSQL<br/>credential table<br/>access_token table<br/>ueks table")]
    end
    
    Browser --> Keycloak
    CLI --> Keycloak
    Backend --> API
    
    Keycloak --> Envoy
    Envoy --> API
    Envoy --> UIService
    
    API --> SecretManager
    SecretManager --> MEK
    SecretManager --> UEK
    SecretManager --> PostgreSQL
```

**Sources:** [src/utils/connectors/postgres.py:38-49](), [docs/deployment_guide/getting_started/deploy_service.rst:116-323](), Diagram 6 from high-level architecture

### Authentication Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Keycloak** | OAuth2/OIDC identity provider | External service |
| **Envoy Sidecars** | JWT validation and session management | API and UI pods |
| **SecretManager** | Credential encryption/decryption | [src/utils/secret_manager.py]() |
| **PostgreSQL** | Encrypted credential storage | `credential`, `access_token`, `ueks` tables |
| **Master Encryption Key (MEK)** | Root encryption key | Vault or file system |

**Sources:** [src/utils/connectors/postgres.py:156-161](), [src/utils/connectors/postgres.py:252-261]()

---

## Authentication Flows

OSMO supports three distinct authentication flows for different client types.

### Browser Authentication Flow (OAuth2 Authorization Code)

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Envoy
    participant Keycloak
    participant APIService
    
    User->>Browser: Access https://osmo.example.com
    Browser->>Envoy: HTTP Request
    
    alt No Valid Session
        Envoy->>Keycloak: Redirect to /auth<br/>(authorization_endpoint)
        Keycloak->>User: Login Page
        User->>Keycloak: Enter Credentials
        Keycloak-->>Browser: Authorization Code
        Browser->>Envoy: Request with Code
        Envoy->>Keycloak: Exchange Code<br/>(token_endpoint)
        Keycloak-->>Envoy: JWT Access Token<br/>audience: osmo-browser-flow
        Envoy->>Envoy: Set HMAC Cookie
    end
    
    Envoy->>Envoy: Validate JWT<br/>Check issuer, audience<br/>Verify signature (JWKS)
    Envoy->>Envoy: Extract user claim<br/>x-osmo-user header
    Envoy->>APIService: Forward Request<br/>with x-osmo-user
    APIService-->>Envoy: Response
    Envoy-->>Browser: Response
```

**Key Configuration:**
- **Client ID:** `osmo-browser-flow`
- **Grant Type:** Authorization Code
- **Session Storage:** HMAC-signed cookies
- **User Header:** `x-osmo-user` (injected by Envoy)

**Sources:** Diagram 6 from high-level architecture, [docs/deployment_guide/getting_started/deploy_service.rst:301-318]()

### Device Flow Authentication (CLI)

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Keycloak
    participant APIService
    
    User->>CLI: osmo login https://osmo.example.com
    CLI->>Keycloak: POST /device<br/>(device_authorization_endpoint)
    Keycloak-->>CLI: device_code<br/>user_code<br/>verification_uri
    CLI->>User: Display:<br/>"Visit https://auth.osmo.example.com/device<br/>Enter code: ABCD-EFGH"
    
    User->>Keycloak: Navigate to verification_uri<br/>Enter user_code
    Keycloak->>User: Approve device
    
    loop Poll for Token
        CLI->>Keycloak: POST /token<br/>device_code
        alt Not Yet Approved
            Keycloak-->>CLI: authorization_pending
        else Approved
            Keycloak-->>CLI: JWT Access Token<br/>audience: osmo-device
        end
    end
    
    CLI->>APIService: API Request<br/>Bearer <token>
    APIService->>APIService: Validate JWT
    APIService-->>CLI: Response
```

**Key Configuration:**
- **Client ID:** `osmo-device`
- **Grant Type:** Device Authorization
- **Token Storage:** Local config file (`~/.osmo/config.yaml`)
- **Polling Interval:** Configured in Keycloak

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:34-48](), Diagram 6 from high-level architecture

### Service Token Authentication (Backend Operators)

Backend operators use long-lived service tokens for authentication:

```bash
# Create service token
osmo token set backend-token \
  --expires-at 2025-12-31 \
  --description "Backend Operator Token" \
  --service \
  --roles osmo-backend
```

Service tokens are stored in the `access_token` table with type `SERVICE`:

```mermaid
graph LR
    Backend["Backend Operator"] --> Token["Service Token<br/>(access_token table)"]
    Token --> API["API Service"]
    API --> Validation["Token Validation"]
    Validation --> Role["Role Check:<br/>osmo-backend"]
```

**Service Token Storage Schema:**

| Column | Type | Description |
|--------|------|-------------|
| `user_name` | TEXT | Token owner |
| `token_name` | TEXT | Token identifier |
| `access_token` | BYTEA | Hashed token value |
| `expires_at` | TIMESTAMP | Expiration timestamp |
| `access_type` | TEXT | `SERVICE` or `USER` |
| `roles` | TEXT[] | Associated roles |

**Sources:** [src/utils/connectors/postgres.py:975-988](), [docs/deployment_guide/install_backend/deploy_backend.rst:34-48]()

---

## Credential Types and Storage

OSMO manages multiple types of credentials for different purposes.

### Credential Type Enum

```python
class CredentialType(enum.Enum):
    GENERIC = 'GENERIC'   # General credentials
    REGISTRY = 'REGISTRY' # Docker registry credentials
    DATA = 'DATA'         # Object storage credentials
```

**Sources:** [src/utils/connectors/postgres.py:62-67]()

### Credential Database Schema

```mermaid
erDiagram
    credential {
        TEXT user_name PK
        TEXT cred_name PK
        credential_type cred_type
        TEXT profile "Credential profile name"
        HSTORE payload "Encrypted key-value pairs"
    }
    
    access_token {
        TEXT user_name PK
        TEXT token_name PK
        BYTEA access_token "Hashed token"
        TIMESTAMP expires_at
        TEXT access_type "SERVICE or USER"
        TEXT_ARRAY roles
    }
    
    ueks {
        TEXT uid PK "User ID"
        HSTORE keys "Encrypted user keys (per key ID)"
    }
    
    credential ||--o{ ueks : "encrypted_with"
    access_token ||--o{ credential : "grants_access_to"
```

**Table Definitions:**

**`credential` table** - Stores encrypted user credentials:
- **Primary Key:** `(user_name, cred_name)`
- **Unique Constraint:** `(user_name, profile)` - one credential per profile per user
- **Payload Format:** PostgreSQL HSTORE (encrypted key-value pairs)

**`access_token` table** - Stores service and user tokens:
- **Primary Key:** `(user_name, token_name, access_type)`
- **Unique Constraint:** `access_token` - prevents token reuse

**`ueks` table** - Stores user encryption keys:
- **Primary Key:** `uid`
- **Keys Format:** HSTORE mapping key IDs to encrypted keys

**Sources:** [src/utils/connectors/postgres.py:960-972](), [src/utils/connectors/postgres.py:975-988](), [src/utils/connectors/postgres.py:852-860]()

---

## Encryption Architecture

OSMO implements a hierarchical encryption system with a Master Encryption Key (MEK) and per-user encryption keys (UEKs).

### Encryption Key Hierarchy

```mermaid
graph TB
    subgraph "Key Management"
        MEK["Master Encryption Key (MEK)<br/>JWK Format<br/>File: mek.yaml or Vault"]
        SecretManager["SecretManager<br/>src/utils/secret_manager.py"]
    end
    
    subgraph "User Encryption Keys"
        UEK1["User 1 UEK<br/>(kid: key_id_1)"]
        UEK2["User 2 UEK<br/>(kid: key_id_2)"]
        UEK3["User N UEK<br/>(kid: key_id_N)"]
    end
    
    subgraph "Encrypted Data"
        Cred1["User 1 Credentials<br/>JWE Compact Format"]
        Cred2["User 2 Credentials<br/>JWE Compact Format"]
        Cred3["User N Credentials<br/>JWE Compact Format"]
    end
    
    MEK --> SecretManager
    SecretManager --> UEK1
    SecretManager --> UEK2
    SecretManager --> UEK3
    
    UEK1 --> Cred1
    UEK2 --> Cred2
    UEK3 --> Cred3
```

**Sources:** [src/utils/connectors/postgres.py:156-161](), [src/utils/connectors/postgres.py:252-261]()

### Credential Encryption Flow

**Encryption Process:**

```mermaid
sequenceDiagram
    participant User
    participant API
    participant SecretManager
    participant PostgreSQL
    
    User->>API: Store Credential<br/>(plaintext)
    API->>SecretManager: encrypt(value, user)
    
    alt UEK Exists
        SecretManager->>PostgreSQL: SELECT keys FROM ueks<br/>WHERE uid = user
        PostgreSQL-->>SecretManager: Encrypted UEK
        SecretManager->>SecretManager: Decrypt UEK with MEK
    else UEK Does Not Exist
        SecretManager->>SecretManager: Generate new UEK
        SecretManager->>SecretManager: Encrypt UEK with MEK
        SecretManager->>PostgreSQL: INSERT INTO ueks
    end
    
    SecretManager->>SecretManager: Encrypt credential with UEK<br/>(JWE Compact Format)
    SecretManager-->>API: Encrypted credential
    API->>PostgreSQL: UPDATE credential<br/>SET payload = encrypted_value
```

**Decryption Process:**

```mermaid
sequenceDiagram
    participant API
    participant SecretManager
    participant PostgreSQL
    
    API->>PostgreSQL: SELECT payload FROM credential
    PostgreSQL-->>API: Encrypted credential (HSTORE)
    API->>SecretManager: decrypt(encrypted, user)
    
    SecretManager->>PostgreSQL: SELECT keys FROM ueks<br/>WHERE uid = user
    PostgreSQL-->>SecretManager: Encrypted UEK
    SecretManager->>SecretManager: Decrypt UEK with MEK
    SecretManager->>SecretManager: Extract kid from JWE header
    SecretManager->>SecretManager: Decrypt credential with UEK
    SecretManager-->>API: Plaintext credential
```

**Sources:** [src/utils/connectors/postgres.py:475-500](), [src/utils/connectors/postgres.py:502-507]()

### PostgresConnector Encryption Methods

**Key Methods:**

| Method | Purpose | Location |
|--------|---------|----------|
| `encrypt_dict()` | Encrypts dictionary of credentials | [src/utils/connectors/postgres.py:502-507]() |
| `decrypt_credential()` | Decrypts credential from database | [src/utils/connectors/postgres.py:475-500]() |
| `encode_hstore()` | Encodes dict to PostgreSQL HSTORE | [src/utils/connectors/postgres.py:515-517]() |
| `decode_hstore()` | Decodes HSTORE to dict | [src/utils/connectors/postgres.py:519-524]() |

**HSTORE Encoding Example:**

The `credential.payload` column uses PostgreSQL's HSTORE type for storing key-value pairs:

```python
# Input: {'access_key': 'AKIAIOSFODNN7EXAMPLE', 'secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'}
# After encryption:
# HSTORE: '"access_key"=>"eyJhbGc...","secret_key"=>"eyJhbGc..."'
```

**Sources:** [src/utils/connectors/postgres.py:515-524]()

---

## Master Encryption Key (MEK) Configuration

The MEK is loaded during `PostgresConnector` initialization and used by `SecretManager` for all encryption operations.

### MEK Initialization

```python
# From PostgresConnector.__init__
mek_file = self.config.mek_file
if self.config.method == 'dev':
    ExtraArgBaseModel.set_extra(ExtraType.ALLOW)
    mek_file = os.path.join(os.path.dirname(__file__), '..', 'secret_manager', 'mek.yaml')

self.secret_manager = SecretManager(
    mek_file,
    self.read_uek,      # Callback to read UEK from database
    self.write_uek,     # Callback to write UEK to database
    self.read_current_kid,  # Callback to get current key ID
    self.add_user       # Callback to add user
)
```

**Configuration Fields:**

| Field | Environment Variable | Default | Description |
|-------|---------------------|---------|-------------|
| `mek_file` | `OSMO_MEK_FILE` | `/home/osmo/vault-agent/secrets/vault-secrets.yaml` | Path to MEK file |
| `method` | N/A | `None` | Set to `'dev'` for local development |

**MEK File Format (JWK):**

```yaml
keys:
  - kid: "key_2024_01"
    kty: "oct"
    k: "<base64-encoded-key>"
    alg: "A256GCM"
  - kid: "key_2024_02"
    kty: "oct"
    k: "<base64-encoded-key>"
    alg: "A256GCM"
```

**Sources:** [src/utils/connectors/postgres.py:252-261](), [src/utils/connectors/postgres.py:156-161]()

---

## Authentication Header Extraction

Envoy sidecars extract user identity from validated JWTs and inject it as the `x-osmo-user` header.

### User Header Middleware

```mermaid
graph LR
    Request["Incoming Request"] --> Envoy["Envoy Sidecar"]
    Envoy --> Validate["Validate JWT<br/>Check issuer<br/>Check audience<br/>Verify signature"]
    Validate --> Extract["Extract user claim<br/>from JWT payload"]
    Extract --> Inject["Inject Header:<br/>x-osmo-user: username"]
    Inject --> Forward["Forward to<br/>API/UI Service"]
```

**JWT Claims Validation:**

Envoy validates the following JWT claims:
- **`iss` (Issuer):** Must match Keycloak issuer URL
- **`aud` (Audience):** Must be `osmo-browser-flow` or `osmo-device`
- **`exp` (Expiration):** Token must not be expired
- **Signature:** Verified using Keycloak's JWKS endpoint

**User Extraction:**

The username is extracted from the JWT `preferred_username` or `sub` claim and injected as `x-osmo-user`.

**Sources:** Diagram 6 from high-level architecture, [src/utils/connectors/postgres.py:167-172]()

---

## Task Authentication

Tasks running in the backend cluster authenticate to the OSMO service using refresh tokens stored in the `tasks` table.

### Task Refresh Token Flow

```mermaid
sequenceDiagram
    participant Task["Task Pod<br/>(osmo-ctrl container)"]
    participant API["API Service"]
    participant DB["PostgreSQL"]
    
    Note over Task,DB: Task initialization
    Task->>DB: INSERT INTO tasks<br/>refresh_token = random_bytes(32)
    
    Note over Task,DB: Task execution
    Task->>Task: Read refresh_token<br/>from /osmo/login/config
    Task->>API: POST /refresh<br/>Bearer <refresh_token>
    API->>DB: SELECT * FROM tasks<br/>WHERE refresh_token = hash(token)
    DB-->>API: task_uuid, workflow_id, user
    API->>API: Generate JWT<br/>user from task.user
    API-->>Task: JWT Access Token
    
    Task->>API: API requests<br/>Bearer <JWT>
    API->>API: Validate JWT
    API-->>Task: Response
```

**Refresh Token Storage:**

| Column | Type | Description |
|--------|------|-------------|
| `refresh_token` | BYTEA | 32-byte random token |
| `task_uuid` | TEXT | Unique task identifier |
| `workflow_id` | TEXT | Parent workflow ID |

**Token Generation:**

```python
# Generate refresh token (task creation)
refresh_token = secrets.token_bytes(REFRESH_TOKEN_LENGTH)  # 32 bytes
```

**Sources:** [src/utils/job/task.py:54-56](), [src/utils/connectors/postgres.py:745]()

---

## Role-Based Access Control (RBAC)

OSMO implements role-based access control through the `roles` table and service token assignments.

### Roles Table Schema

```mermaid
erDiagram
    roles {
        TEXT name PK
        TEXT description
        JSONB_ARRAY policies "List of policy objects"
        BOOLEAN immutable "Prevent modification"
    }
    
    access_token {
        TEXT user_name
        TEXT token_name
        TEXT_ARRAY roles "Assigned roles"
    }
    
    roles ||--o{ access_token : "assigned_to"
```

**Built-in Roles:**

| Role | Description | Immutable |
|------|-------------|-----------|
| `osmo-backend` | Backend operator service role | Yes |
| `osmo-admin` | Administrative access | Yes |
| `osmo-user` | Standard user access | Yes |

**Sources:** [src/utils/connectors/postgres.py:548-558](), [src/utils/connectors/postgres.py:982]()

### Policy Structure

Policies define allowed actions on specific resources:

```json
{
  "resource": "workflow",
  "actions": ["submit", "cancel", "list"],
  "conditions": {
    "owner": "${user}"
  }
}
```

**Sources:** [src/utils/connectors/postgres.py:554]()

---

## Security Best Practices

### Credential Management

1. **Rotation:** Regularly rotate MEK and service tokens
2. **Expiration:** Set appropriate `expires_at` for service tokens
3. **Least Privilege:** Assign minimal roles required for each service token
4. **Encryption at Rest:** All credentials stored in PostgreSQL are encrypted

### Token Security

1. **Storage:** 
   - Browser: HMAC-signed cookies (HttpOnly, Secure)
   - CLI: Local config file with restricted permissions (0600)
   - Backend: Kubernetes secrets

2. **Validation:**
   - JWT signature verification using JWKS
   - Audience claim validation
   - Expiration time checks

3. **Refresh Tokens:**
   - Task refresh tokens are single-use and expire with task completion
   - Stored as hashed values in database

### Network Security

1. **TLS/HTTPS:** All external communication uses TLS
2. **Envoy Sidecars:** Act as authentication gatekeepers
3. **Internal Traffic:** Service-to-service communication within Kubernetes cluster

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:116-323](), [src/utils/connectors/postgres.py:475-507]()

---

## Development Mode

For local development, OSMO supports a `dev` authentication mode that bypasses Keycloak:

```python
dev_user: str = pydantic.Field(
    command_line='dev_user',
    default='testuser',
    description='If method is set to "dev", the browser flow to the service will use this user name.'
)
```

**Configuration:**

```bash
# Set dev mode
--method=dev --dev_user=testuser
```

**Behavior:**
- Envoy sidecars disabled
- No JWT validation
- Fixed user identity (`testuser`)
- Local MEK file used (`src/utils/secret_manager/mek.yaml`)

**⚠️ Warning:** Development mode should **never** be used in production environments.

**Sources:** [src/utils/connectors/postgres.py:167-172](), [src/utils/connectors/postgres.py:254-257]()

---

