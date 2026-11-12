<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/healthcare · extra page SMART on FHIR Authorization · fetched 2026-10-26 -->

# SMART on FHIR Authorization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [fhir-developer-skill/SKILL.md](fhir-developer-skill/SKILL.md)
- [fhir-developer-skill/references/bundles.md](fhir-developer-skill/references/bundles.md)
- [fhir-developer-skill/references/pagination.md](fhir-developer-skill/references/pagination.md)
- [fhir-developer-skill/references/resource-examples.md](fhir-developer-skill/references/resource-examples.md)
- [fhir-developer-skill/references/smart-auth.md](fhir-developer-skill/references/smart-auth.md)

</details>



## Purpose and Scope

This document covers OAuth 2.0-based authorization for FHIR APIs using the SMART on FHIR framework. It explains how to implement authorization flows, enforce scope-based access control, and handle authentication tokens. For information about FHIR resource structures and validation, see [FHIR R4 Resource Structures](#3.3.1). For RESTful endpoint patterns and error handling, see [FHIR API Patterns](#3.3.2).

SMART on FHIR is the standard authorization framework for healthcare APIs, enabling patient-facing apps, provider-facing clinical tools, and automated backend services to securely access FHIR data with granular permissions.

**Sources:** [fhir-developer-skill/references/smart-auth.md:1-4]()

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Client Applications"
        EHR["EHR Launch App"]
        SA["Standalone App"]
        BACKEND["Backend Service"]
    end
    
    subgraph "Discovery"
        WELL_KNOWN["/.well-known/smart-configuration"]
        METADATA["/metadata<br/>(CapabilityStatement)"]
    end
    
    subgraph "Authorization Server"
        AUTH_EP["/authorize endpoint"]
        TOKEN_EP["/token endpoint"]
    end
    
    subgraph "FHIR Server"
        PATIENT_EP["/Patient"]
        OBS_EP["/Observation"]
        ENC_EP["/Encounter"]
    end
    
    subgraph "Scope Enforcement"
        PARSE["parse_smart_scopes()"]
        CHECK["check_scope()"]
    end
    
    EHR -->|"1. Discover endpoints"| WELL_KNOWN
    SA -->|"1. Discover endpoints"| WELL_KNOWN
    BACKEND -->|"1. Discover endpoints"| WELL_KNOWN
    
    WELL_KNOWN -->|"authorization_endpoint<br/>token_endpoint"| AUTH_EP
    WELL_KNOWN -->|"authorization_endpoint<br/>token_endpoint"| TOKEN_EP
    
    METADATA -->|"security.extension<br/>oauth-uris"| AUTH_EP
    METADATA -->|"security.extension<br/>oauth-uris"| TOKEN_EP
    
    EHR -->|"2. Authorize with<br/>launch + scope"| AUTH_EP
    SA -->|"2. Authorize with<br/>launch/patient + scope"| AUTH_EP
    BACKEND -->|"2. JWT assertion +<br/>client_credentials"| TOKEN_EP
    
    AUTH_EP -->|"3. auth code"| EHR
    AUTH_EP -->|"3. auth code"| SA
    
    EHR -->|"4. Exchange code"| TOKEN_EP
    SA -->|"4. Exchange code"| TOKEN_EP
    
    TOKEN_EP -->|"5. access_token +<br/>patient context"| EHR
    TOKEN_EP -->|"5. access_token +<br/>patient context"| SA
    TOKEN_EP -->|"5. access_token"| BACKEND
    
    EHR -->|"6. Bearer token"| PATIENT_EP
    SA -->|"6. Bearer token"| OBS_EP
    BACKEND -->|"6. Bearer token"| ENC_EP
    
    PATIENT_EP --> PARSE
    OBS_EP --> PARSE
    ENC_EP --> PARSE
    
    PARSE --> CHECK
    CHECK -->|"401 invalid_token<br/>403 insufficient_scope"| EHR
    CHECK -->|"401 invalid_token<br/>403 insufficient_scope"| SA
    CHECK -->|"401 invalid_token<br/>403 insufficient_scope"| BACKEND
```

**Diagram: SMART on FHIR Authorization Architecture**

The system uses two discovery mechanisms: `/.well-known/smart-configuration` ([smart-auth.md:13-31]()) provides OAuth endpoint URLs, while `/metadata` returns a `CapabilityStatement` with embedded authorization URIs ([resource-examples.md:175-184]()). Client apps obtain access tokens through different flows depending on their launch context, and the FHIR server enforces scopes using `parse_smart_scopes()` and `check_scope()` functions ([smart-auth.md:167-195]()).

**Sources:** [fhir-developer-skill/references/smart-auth.md:13-31](), [fhir-developer-skill/references/resource-examples.md:175-184](), [fhir-developer-skill/SKILL.md:24-25]()

---

## Discovery and Configuration

### Well-Known Configuration Endpoint

Servers MUST publish authorization configuration at `/.well-known/smart-configuration`:

| Field | Description |
|-------|-------------|
| `authorization_endpoint` | URL for OAuth authorize requests |
| `token_endpoint` | URL for token exchange |
| `token_endpoint_auth_methods_supported` | Supported client authentication methods |
| `scopes_supported` | List of supported scopes |
| `capabilities` | Feature flags (e.g., `launch-ehr`, `permission-v2`) |

**Example response structure:**

```json
{
  "authorization_endpoint": "https://auth.example.org/authorize",
  "token_endpoint": "https://auth.example.org/token",
  "token_endpoint_auth_methods_supported": ["client_secret_basic", "private_key_jwt"],
  "scopes_supported": ["openid", "fhirUser", "launch", "launch/patient",
                       "patient/*.rs", "user/*.cruds", "offline_access"],
  "capabilities": ["launch-ehr", "launch-standalone", "client-public",
                   "client-confidential-symmetric", "permission-v2", "sso-openid-connect"]
}
```

**Sources:** [fhir-developer-skill/references/smart-auth.md:13-31]()

### CapabilityStatement Integration

The `/metadata` endpoint returns a `CapabilityStatement` with OAuth URIs embedded in the `security.extension` field using the `http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris` extension. This provides an alternative discovery mechanism integrated with FHIR's standard metadata endpoint.

**Sources:** [fhir-developer-skill/references/resource-examples.md:162-196]()

---

## Scope Syntax

### SMART v2 (Current Standard)

The v2 scope syntax uses granular permissions with explicit CRUD actions:

```
<context>/<resource>.<permissions>

context: patient | user | system
resource: Patient | Observation | * (wildcard)
permissions: c (create) | r (read) | u (update) | d (delete) | s (search)
```

| Scope | Meaning |
|-------|---------|
| `patient/Patient.rs` | Read and search Patient for current patient context |
| `patient/Observation.rs` | Read and search Observations for current patient |
| `patient/*.rs` | Read and search all resources for current patient |
| `user/Encounter.cruds` | Full CRUD + search on Encounters the user can access |
| `system/*.rs` | Backend service: read/search all resources |

**Sources:** [fhir-developer-skill/references/smart-auth.md:35-52]()

### SMART v1 (Legacy)

The v1 syntax uses coarser permissions:

```
<context>/<resource>.<read|write|*>
```

| v1 Scope | Equivalent v2 |
|----------|---------------|
| `patient/Patient.read` | `patient/Patient.rs` |
| `patient/Patient.write` | `patient/Patient.cud` |
| `patient/Patient.*` | `patient/Patient.cruds` |

FHIR servers should support both v1 and v2 scopes during the transition period. The `parse_smart_scopes()` function handles conversion from v1 to v2 format ([smart-auth.md:167-181]()).

**Sources:** [fhir-developer-skill/references/smart-auth.md:53-62]()

### Context Types

| Scope Type | Use Case | Context Required |
|------------|----------|------------------|
| `patient/` | Patient-facing apps | `patient` launch context |
| `user/` | Provider-facing apps | User's access permissions |
| `system/` | Backend services | Pre-configured policy |

**Sources:** [fhir-developer-skill/references/smart-auth.md:63-70]()

---

## Launch Context Scopes

```mermaid
graph LR
    subgraph "Launch Scopes"
        LAUNCH["launch"]
        LAUNCH_PAT["launch/patient"]
        LAUNCH_ENC["launch/encounter"]
    end
    
    subgraph "Identity Scopes"
        OPENID["openid"]
        FHIR_USER["fhirUser"]
    end
    
    subgraph "Token Lifetime"
        OFFLINE["offline_access"]
        ONLINE["online_access"]
    end
    
    subgraph "Token Response"
        PAT_CLAIM["patient claim"]
        ENC_CLAIM["encounter claim"]
        ID_TOKEN["id_token with fhirUser"]
        REFRESH["refresh_token"]
    end
    
    LAUNCH -->|"Provides"| PAT_CLAIM
    LAUNCH -->|"Provides"| ENC_CLAIM
    LAUNCH_PAT -->|"Provides"| PAT_CLAIM
    LAUNCH_ENC -->|"Provides"| ENC_CLAIM
    OPENID -->|"Provides"| ID_TOKEN
    FHIR_USER -->|"Provides"| ID_TOKEN
    OFFLINE -->|"Provides"| REFRESH
    ONLINE -->|"Provides"| REFRESH
```

**Diagram: Launch Context Scope to Token Claim Mapping**

| Scope | Provides | In Token Response |
|-------|----------|-------------------|
| `launch` | EHR launch context | `patient`, `encounter` fields |
| `launch/patient` | Standalone patient selection | `patient` field |
| `launch/encounter` | Standalone encounter selection | `encounter` field |
| `openid fhirUser` | User identity | `id_token` with `fhirUser` claim |
| `offline_access` | Refresh token (persistent) | `refresh_token` |
| `online_access` | Refresh token (session-bound) | `refresh_token` |

**Sources:** [fhir-developer-skill/references/smart-auth.md:72-81]()

---

## EHR Launch Flow

```mermaid
sequenceDiagram
    participant EHR as "EHR System"
    participant App as "Client App"
    participant Well as "/.well-known/smart-configuration"
    participant Auth as "/authorize"
    participant Token as "/token"
    participant User as "End User"
    
    EHR->>App: "GET /launch?iss=https://fhir.hospital.org<br/>&launch=abc123"
    App->>Well: "GET /.well-known/smart-configuration"
    Well-->>App: "{authorization_endpoint, token_endpoint}"
    
    App->>Auth: "GET /authorize?<br/>response_type=code&<br/>client_id=my-app&<br/>redirect_uri=https://app.example.com/callback&<br/>scope=launch patient/Patient.rs&<br/>state=xyz789&<br/>aud=https://fhir.hospital.org&<br/>launch=abc123"
    
    Auth->>User: "Authenticate & Authorize"
    User-->>Auth: "Approved"
    
    Auth-->>App: "GET /callback?code=auth_code&state=xyz789"
    
    App->>Token: "POST /token<br/>grant_type=authorization_code&<br/>code=auth_code&<br/>redirect_uri=https://app.example.com/callback&<br/>client_id=my-app"
    
    Token-->>App: "{access_token, patient: 123, encounter: 456}"
```

**Diagram: EHR Launch Sequence with OAuth Parameters**

### Step-by-Step Process

1. **EHR launches app** with `iss` (FHIR server base URL) and `launch` token
2. **App discovers endpoints** from `/.well-known/smart-configuration`
3. **App requests authorization** with:
   - `response_type=code` (authorization code flow)
   - `client_id` (registered app identifier)
   - `redirect_uri` (callback URL)
   - `scope` (requested permissions including `launch`)
   - `state` (CSRF protection token)
   - `aud` (FHIR server base URL)
   - `launch` (opaque token from EHR)
4. **User authenticates and authorizes** the requested scopes
5. **Authorization server redirects** with authorization code
6. **App exchanges code for token** using `grant_type=authorization_code`
7. **Token response includes context**: `access_token`, `patient`, `encounter`

**Sources:** [fhir-developer-skill/references/smart-auth.md:82-124]()

---

## Backend Services Authentication

```mermaid
graph TD
    subgraph "Backend Service"
        CLIENT["Client Application"]
        KEYS["Private Key<br/>(RS384, ES384)"]
        JWT_CREATE["jwt.encode()"]
    end
    
    subgraph "JWT Claims"
        ISS["iss: CLIENT_ID"]
        SUB["sub: CLIENT_ID"]
        AUD["aud: TOKEN_ENDPOINT"]
        EXP["exp: now + 300"]
        JTI["jti: uuid"]
    end
    
    subgraph "Token Endpoint"
        TOKEN_EP["/token"]
        VALIDATE["Validate JWT signature"]
    end
    
    subgraph "Grant Parameters"
        GRANT["grant_type:<br/>client_credentials"]
        SCOPE["scope: system/*.rs"]
        ASSERTION_TYPE["client_assertion_type:<br/>jwt-bearer"]
        ASSERTION["client_assertion:<br/>signed JWT"]
    end
    
    CLIENT --> KEYS
    KEYS --> JWT_CREATE
    
    ISS --> JWT_CREATE
    SUB --> JWT_CREATE
    AUD --> JWT_CREATE
    EXP --> JWT_CREATE
    JTI --> JWT_CREATE
    
    JWT_CREATE --> ASSERTION
    
    GRANT --> TOKEN_EP
    SCOPE --> TOKEN_EP
    ASSERTION_TYPE --> TOKEN_EP
    ASSERTION --> TOKEN_EP
    
    TOKEN_EP --> VALIDATE
    VALIDATE -->|"Valid"| ACCESS_TOKEN["access_token"]
    VALIDATE -->|"Invalid"| ERROR["401 invalid_client"]
```

**Diagram: Backend Services JWT Assertion Flow with Code Entities**

Backend services use the `client_credentials` grant type with JWT assertions for system-to-system authentication. The implementation creates a signed JWT with specific claims and exchanges it for an access token without user interaction.

### Implementation Pattern

The backend service implementation follows this pattern from [smart-auth.md:130-158]():

1. **Create JWT assertion** with claims:
   - `iss` and `sub`: both set to `CLIENT_ID`
   - `aud`: set to `TOKEN_ENDPOINT`
   - `exp`: expiration (typically 5 minutes)
   - `jti`: unique identifier (UUID)

2. **Sign JWT** using `RS384` or `ES384` algorithm with private key

3. **POST to token endpoint** with parameters:
   - `grant_type=client_credentials`
   - `scope=system/*.rs` (or other system/ scopes)
   - `client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`
   - `client_assertion=<signed_jwt>`

4. **Receive access token** in response

**Sources:** [fhir-developer-skill/references/smart-auth.md:126-158]()

---

## Scope Enforcement Implementation

```mermaid
graph TB
    subgraph "Incoming Request"
        REQ["Request with<br/>Authorization: Bearer token"]
        TOKEN_SCOPES["token_scopes string<br/>(e.g., 'patient/Patient.rs user/Observation.cruds')"]
    end
    
    subgraph "parse_smart_scopes Function"
        SPLIT["Split by whitespace"]
        REGEX["Regex match:<br/>(patient|user|system)/(\w+|\*).([cruds]+|read|write|\*)"]
        V1_CONVERT["Convert v1 to v2:<br/>read → rs<br/>write → cud<br/>* → cruds"]
        BUILD_DICT["Build permissions dict:<br/>{resource: set(permissions)}"]
    end
    
    subgraph "check_scope Function"
        ACTION_MAP["action_map:<br/>{'create': 'c', 'read': 'r',<br/>'update': 'u', 'delete': 'd',<br/>'search': 's'}"]
        CHECK_RESOURCE["Check resource in permissions"]
        CHECK_WILDCARD["Check '*' in permissions"]
        VERIFY["Verify required permission"]
    end
    
    subgraph "Response"
        ALLOW["200 OK / 201 Created"]
        ERR_401["401 Unauthorized<br/>invalid_token"]
        ERR_403["403 Forbidden<br/>insufficient_scope"]
    end
    
    REQ --> TOKEN_SCOPES
    TOKEN_SCOPES --> SPLIT
    SPLIT --> REGEX
    REGEX --> V1_CONVERT
    V1_CONVERT --> BUILD_DICT
    
    BUILD_DICT --> CHECK_RESOURCE
    BUILD_DICT --> CHECK_WILDCARD
    CHECK_RESOURCE --> VERIFY
    CHECK_WILDCARD --> VERIFY
    
    ACTION_MAP --> VERIFY
    
    VERIFY -->|"Permission found"| ALLOW
    VERIFY -->|"Token invalid"| ERR_401
    VERIFY -->|"Permission missing"| ERR_403
```

**Diagram: Scope Parsing and Enforcement Flow with Function Names**

### parse_smart_scopes Function

The `parse_smart_scopes()` function ([smart-auth.md:167-181]()) converts a space-delimited scope string into a structured permissions dictionary:

```python
def parse_smart_scopes(token_scopes: str) -> dict:
    """Parse SMART scopes into a permissions structure."""
    permissions = {}
    for scope in token_scopes.split():
        match = re.match(r'(patient|user|system)/(\w+|\*)\.([cruds]+|read|write|\*)', scope)
        if match:
            context, resource, perms = match.groups()
            if perms == 'read': perms = 'rs'
            elif perms == 'write': perms = 'cud'
            elif perms == '*': perms = 'cruds'

            if resource not in permissions:
                permissions[resource] = set()
            permissions[resource].update(perms)
    return permissions
```

**Key operations:**
- Regex captures context (`patient`/`user`/`system`), resource type, and permissions
- Converts v1 syntax (`read`, `write`, `*`) to v2 (`rs`, `cud`, `cruds`)
- Returns dict like `{'Patient': {'r', 's'}, 'Observation': {'c', 'r', 'u', 'd', 's'}}`

**Sources:** [fhir-developer-skill/references/smart-auth.md:167-181]()

### check_scope Function

The `check_scope()` function ([smart-auth.md:183-195]()) verifies that a token has the required permission for an action:

```python
async def check_scope(request: Request, resource_type: str, action: str):
    """Verify the token has required scope for the action."""
    token_scopes = request.state.token_scopes
    permissions = parse_smart_scopes(token_scopes)

    action_map = {'create': 'c', 'read': 'r', 'update': 'u', 'delete': 'd', 'search': 's'}
    required = action_map.get(action, action)

    allowed = permissions.get(resource_type, set()) | permissions.get('*', set())

    if required not in allowed:
        raise HTTPException(status_code=403, detail=f"Insufficient scope. Required: {resource_type}.{required}")
```

**Key operations:**
- Maps action names to single-letter permission codes
- Checks both specific resource type and wildcard (`*`) permissions
- Raises `403 Forbidden` if permission not found

**Sources:** [fhir-developer-skill/references/smart-auth.md:183-195]()

---

## Authorization Error Handling

### HTTP Status Codes

The FHIR server returns specific status codes for authorization failures as defined in [SKILL.md:24-25]():

| Status | Error Code | When |
|--------|------------|------|
| `401 Unauthorized` | `invalid_token` | Token expired, malformed, revoked, or missing (RFC 6750) |
| `403 Forbidden` | `insufficient_scope` | Valid token but missing required scope |
| `403 Forbidden` | `access_denied` | Resource outside patient compartment |

### Error Response Format

All authorization errors MUST return an `OperationOutcome` resource:

```json
{
  "resourceType": "OperationOutcome",
  "issue": [{
    "severity": "error",
    "code": "security",
    "diagnostics": "Insufficient scope. Required: Patient.r"
  }]
}
```

**Sources:** [fhir-developer-skill/references/smart-auth.md:197-204](), [fhir-developer-skill/SKILL.md:24-25]()

### Token Validation Sequence

```mermaid
graph TD
    REQ["Incoming FHIR Request"]
    HEADER["Extract Authorization header"]
    BEARER["Verify Bearer format"]
    DECODE["Decode JWT / validate"]
    EXPIRED["Check expiration"]
    REVOKED["Check revocation"]
    PARSE["parse_smart_scopes()"]
    CHECK["check_scope()"]
    COMPARTMENT["Check patient compartment"]
    
    REQ --> HEADER
    HEADER -->|"Missing"| ERR_401_MISSING["401: Missing token"]
    HEADER -->|"Present"| BEARER
    BEARER -->|"Invalid format"| ERR_401_MALFORMED["401: Malformed token"]
    BEARER -->|"Valid"| DECODE
    DECODE -->|"Invalid signature"| ERR_401_INVALID["401: Invalid token"]
    DECODE -->|"Valid"| EXPIRED
    EXPIRED -->|"Expired"| ERR_401_EXPIRED["401: Token expired"]
    EXPIRED -->|"Valid"| REVOKED
    REVOKED -->|"Revoked"| ERR_401_REVOKED["401: Token revoked"]
    REVOKED -->|"Valid"| PARSE
    PARSE --> CHECK
    CHECK -->|"Insufficient scope"| ERR_403_SCOPE["403: Insufficient scope"]
    CHECK -->|"Valid scope"| COMPARTMENT
    COMPARTMENT -->|"Outside compartment"| ERR_403_ACCESS["403: Access denied"]
    COMPARTMENT -->|"Valid"| SUCCESS["Process request"]
```

**Diagram: Token Validation and Error Flow**

The validation flow ensures that:
1. Authorization header is present and properly formatted
2. Token signature is valid and not expired or revoked
3. Token scopes include the required permission for the action
4. Resource is within the authorized patient compartment (for `patient/` scopes)

**Sources:** [fhir-developer-skill/references/smart-auth.md:197-204](), [fhir-developer-skill/SKILL.md:24-25]()

---

## Token Lifecycle Management

### Access Token Properties

| Property | Typical Value | Notes |
|----------|---------------|-------|
| `access_token` | JWT string | Bearer token for API requests |
| `token_type` | `Bearer` | Always "Bearer" for SMART |
| `expires_in` | `3600` | Seconds until expiration (typically 1 hour) |
| `scope` | Space-delimited string | Actual granted scopes (may differ from requested) |
| `patient` | Patient ID | Present when `launch` or `launch/patient` used |
| `encounter` | Encounter ID | Present when `launch` scope used |

### Refresh Token Flow

For long-lived sessions, clients request `offline_access` or `online_access` scope to receive a `refresh_token`:

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=<refresh_token_value>&
client_id=my-app
```

**Response:**
```json
{
  "access_token": "new_token_here",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "new_refresh_token"
}
```

**Differences:**
- `offline_access`: Refresh token persists beyond session (for long-term access)
- `online_access`: Refresh token expires when user session ends

**Sources:** [fhir-developer-skill/references/smart-auth.md:115-123]()

---

## Integration with FHIR API Patterns

Authorization integrates with FHIR RESTful operations as documented in [FHIR API Patterns](#3.3.2):

### Authorization Header

All FHIR requests MUST include the `Authorization` header:

```
GET /Patient/123
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Scope-to-Operation Mapping

| HTTP Method | FHIR Operation | Required Permission |
|-------------|----------------|---------------------|
| `POST /Patient` | Create | `c` (create) |
| `GET /Patient/123` | Read | `r` (read) |
| `PUT /Patient/123` | Update | `u` (update) |
| `DELETE /Patient/123` | Delete | `d` (delete) |
| `GET /Patient?name=Smith` | Search | `s` (search) |

### Middleware Integration

FastAPI middleware validates authorization before processing requests:

```python
from fastapi import Request, HTTPException

async def auth_middleware(request: Request, call_next):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = auth_header[7:]  # Strip "Bearer "
    # Validate token, extract scopes
    request.state.token_scopes = extract_scopes(token)
    
    response = await call_next(request)
    return response
```

This middleware runs before endpoint handlers, ensuring all requests are authenticated.

**Sources:** [fhir-developer-skill/references/smart-auth.md:162-195](), [fhir-developer-skill/SKILL.md:24-25]()

---

