<!-- source: DeepWiki mcp.deepwiki.com · repo plandex-ai/plandex · page 4 Server Architecture · fetched 2026-10-27 -->

# Server Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/api/clients.go](app/cli/api/clients.go)
- [app/server/db/user_helpers.go](app/server/db/user_helpers.go)
- [app/server/handlers/sessions.go](app/server/handlers/sessions.go)
- [app/server/main.go](app/server/main.go)
- [app/server/routes/routes.go](app/server/routes/routes.go)
- [app/server/setup/setup.go](app/server/setup/setup.go)

</details>



This document covers the server-side components of Plandex, including the HTTP API server, request handlers, middleware, routing, and core server infrastructure. For information about plan execution logic and AI model integration, see [Plan Execution Engine](#4.3). For database schema and data models, see [Data Models and Shared Types](#4.2).

## Overview

The Plandex server is a Go-based HTTP API server that provides REST endpoints for plan management, context operations, and real-time plan execution. The server follows a layered architecture with clear separation between HTTP handling, business logic, and data persistence.

```mermaid
graph TD
    subgraph "Server Initialization"
        MainFunc["main()"] --> RegisterRoutes["routes.RegisterHandlePlandex()"]
        RegisterRoutes --> LiteLLM["model.EnsureLiteLLM(2)"]
        LiteLLM --> RouterSetup["mux.NewRouter()"]
        RouterSetup --> LoadIP["setup.MustLoadIp()"]
        LoadIP --> InitDB["setup.MustInitDb()"]
        InitDB --> StartServer["setup.StartServer()"]
    end
    
    subgraph "Route Categories"
        HealthRoutes["routes.AddHealthRoutes()<br/>/health, /version"]
        ApiRoutes["routes.AddApiRoutes()<br/>Standard operations"]
        ProxyRoutes["routes.AddProxyableApiRoutes()<br/>Real-time operations"]
    end
    
    subgraph "Middleware Stack"
        LogMiddleware["loggingMiddleware()<br/>Request/response logging"]
        MaxBytes["maxBytesMiddleware()<br/>1GB request limit"]
        Auth["Authenticate()<br/>Per-handler JWT validation"]
    end
    
    subgraph "Handler Types"
        SessionHandlers["handlers/sessions.go<br/>CreateEmailVerificationHandler<br/>SignInHandler<br/>SignOutHandler"]
        UserHandlers["db/user_helpers.go<br/>GetUser<br/>GetUserByEmail<br/>CreateUser"]
        PlanHandlers["Plan execution handlers<br/>TellPlanHandler<br/>BuildPlanHandler"]
    end
    
    subgraph "External Dependencies"
        PostgreSQL[("PostgreSQL Database<br/>User data & plans")]
        LiteLLMProxy["LiteLLM Proxy Server<br/>AI model abstraction"]
        GitRepositories[("Git Repositories<br/>Plan file storage")]
    end
    
    StartServer --> HealthRoutes
    StartServer --> ApiRoutes
    StartServer --> ProxyRoutes
    
    RouterSetup --> LogMiddleware
    LogMiddleware --> MaxBytes
    MaxBytes --> Auth
    
    Auth --> SessionHandlers
    Auth --> UserHandlers  
    Auth --> PlanHandlers
    
    InitDB --> PostgreSQL
    LiteLLM --> LiteLLMProxy
    PlanHandlers --> GitRepositories
```

**Sources:** [app/server/main.go:14-38](), [app/server/setup/setup.go:66-185](), [app/server/routes/routes.go:20-203]()
</thinking>

## HTTP Server Configuration

The server configuration in `setup.go` implements comprehensive middleware, graceful shutdown, and database initialization. The `StartServer` function orchestrates the complete HTTP server lifecycle:

```mermaid
graph LR
    subgraph "Server Configuration"
        StartServer["StartServer()"] --> EnvCheck["GOENV development check"]
        EnvCheck --> ShutdownCtx["shutdown.ShutdownCtx setup"]
        ShutdownCtx --> PortConfig["PORT env var<br/>default: 8099"]
        PortConfig --> MiddlewareStack["Middleware application"]
    end
    
    subgraph "Middleware Pipeline"
        LoggingMW["loggingMiddleware()<br/>Skip /health, /version"] --> MaxBytesMW["maxBytesMiddleware()<br/>1GB limit, 1MB headers"]
        MaxBytesMW --> ConfigureFn["configureFn()<br/>Optional configuration"]
    end
    
    subgraph "HTTP Server Specs"
        ServerConfig["http.Server<br/>Addr: :PORT<br/>MaxHeaderBytes: 1MB<br/>ReadHeaderTimeout: 5s"] --> ListenServe["ListenAndServe()<br/>Goroutine"]
    end
    
    subgraph "Shutdown Handling"
        SignalCapture["signal.Notify()<br/>SIGTERM, SIGINT"] --> WaitActivePlans["waitForActivePlans()<br/>1s ticker polling<br/>plan.NumActivePlans()"]
        WaitActivePlans --> CleanupLocks["db.CleanupActiveLocks()"] 
        CleanupLocks --> HTTPShutdown["server.Shutdown()<br/>30s timeout"]
        HTTPShutdown --> ShutdownHooks["Execute shutdown hooks<br/>model.ShutdownLiteLLMServer()"]
    end
    
    MiddlewareStack --> ServerConfig
    ListenServe --> SignalCapture
```

The middleware stack includes several critical components:
- `loggingMiddleware`: Logs request method, path, and duration while excluding monitoring endpoints
- `maxBytesMiddleware`: Uses `http.MaxBytesReader` to enforce the 1GB request body limit
- Database connection cleanup with deferred `db.Conn.Close()`
- Graceful shutdown with 60-second active plan timeout followed by 30-second HTTP shutdown timeout

**Sources:** [app/server/setup/setup.go:66-185](), [app/server/setup/setup.go:50-64](), [app/server/setup/setup.go:187-214]()

## Route Organization

Routes are organized using the `mux.Router` from Gorilla Mux with a configurable handler registration system. The `routes.go` file defines three distinct route categories:

| Route Function | Purpose | Handler Registration |
|---|---|---|
| `AddHealthRoutes` | System monitoring | `/health`, `/version` endpoints |
| `AddApiRoutes` | Standard CRUD operations | Plan, context, user management |
| `AddProxyableApiRoutes` | Real-time operations | Active plan streaming, status |

```mermaid
graph TD
    subgraph "Route Registration Pattern"
        RegisterFn["routes.RegisterHandlePlandex()"] --> HandlePlandexFn["HandlePlandexFn variable<br/>Function pointer"]
        HandlePlandexFn --> RouteDefinition["router.HandleFunc(path, handler)"]
    end
    
    subgraph "Health Routes"
        HealthCheck["/health --> hooks.ExecHook(hooks.HealthCheck)"]
        VersionCheck["/version --> Read version.txt<br/>Handle IS_CLOUD env"]
    end
    
    subgraph "Standard API Routes (89 total)"
        AccountRoutes["/accounts/email_verifications<br/>/accounts/sign_in<br/>/accounts/sign_out"]
        OrgRoutes["/orgs<br/>/orgs/session<br/>/users"]
        PlanRoutes["/plans<br/>/plans/{planId}<br/>/plans/{planId}/{branch}/context"]
        ModelRoutes["/custom_models<br/>/model_sets<br/>/default_settings"]
    end
    
    subgraph "Proxyable API Routes"
        ConnectRoute["/plans/{planId}/{branch}/connect<br/>ConnectPlanHandler<br/>isStreaming: true"]
        StopRoute["/plans/{planId}/{branch}/stop<br/>StopPlanHandler"]
        StatusRoute["/plans/{planId}/{branch}/build_status<br/>GetBuildStatusHandler"]
    end
    
    RouteDefinition --> HealthCheck
    RouteDefinition --> VersionCheck
    RouteDefinition --> AccountRoutes
    RouteDefinition --> OrgRoutes
    RouteDefinition --> PlanRoutes
    RouteDefinition --> ModelRoutes
    RouteDefinition --> ConnectRoute
    RouteDefinition --> StopRoute
    RouteDefinition --> StatusRoute
```

The route registration uses a function pointer pattern where `HandlePlandexFn` is set during server initialization in `main.go`, allowing for flexible handler configuration while maintaining type safety through the `PlandexHandler` type alias.

**Sources:** [app/server/routes/routes.go:15-28](), [app/server/routes/routes.go:89-190](), [app/server/routes/routes.go:192-203](), [app/server/main.go:18-20]()

## Authentication and Session Management

The server implements a comprehensive authentication system with email verification, sign-in codes, and JWT token management handled primarily in `handlers/sessions.go`:

```mermaid
graph TD
    subgraph "Email Verification Flow"
        CreateVerification["CreateEmailVerificationHandler"] --> CheckUser["GetUserByEmail()<br/>HasAccount determination"]
        CheckUser --> GeneratePin["GetRandomAlphanumeric(6)<br/>SHA256 hash"]
        GeneratePin --> StoreVerification["db.CreateEmailVerification()"]
        StoreVerification --> SendEmail["email.SendVerificationEmail()"]
    end
    
    subgraph "Sign-In Process"
        SignInRequest["SignInHandler"] --> ValidatePin["CheckEmailPinHandler<br/>db.ValidateEmailVerification()"]
        ValidatePin --> ValidateAndSignIn["ValidateAndSignIn()<br/>Create JWT token"]
        ValidateAndSignIn --> SetCookies["Set auth cookies<br/>for browser clients"]
    end
    
    subgraph "Cross-Client Authentication"
        CreateSignInCode["CreateSignInCodeHandler<br/>Authenticated endpoint"] --> GenerateCode["GetRandomAlphanumeric(6)<br/>SHA256 hash"]
        GenerateCode --> StoreCode["db.CreateSignInCode()"]
        StoreCode --> ShareCode["Return plain code<br/>for client transfer"]
    end
    
    subgraph "Session Management"
        SignOut["SignOutHandler"] --> InvalidateToken["UPDATE auth_tokens<br/>SET deleted_at = NOW()"]
        InvalidateToken --> ClearCookies["ClearAuthCookieIfBrowser()<br/>ClearAccountFromCookies()"]
    end
    
    subgraph "User Configuration"
        GetOrgConfig["GetOrgUserConfigHandler"] --> LoadConfig["db.GetOrgUserConfig()"]
        UpdateOrgConfig["UpdateOrgUserConfigHandler"] --> SaveConfig["db.UpdateOrgUserConfig()"]
    end
```

Key authentication features include:
- Local development mode bypass with `GOENV=development` and `LOCAL_MODE=1`
- PIN-based email verification with 6-character alphanumeric codes
- Cross-client sign-in codes for UI-to-CLI authentication transfer
- JWT token invalidation on sign-out with database cleanup
- Per-organization user configuration management

**Sources:** [app/server/handlers/sessions.go:18-136](), [app/server/handlers/sessions.go:176-209](), [app/server/handlers/sessions.go:252-285](), [app/server/handlers/sessions.go:287-346]()

## Database Integration and User Management

Database operations are centralized in the `db` package with comprehensive user and organization management in `user_helpers.go`:

```mermaid
graph TD
    subgraph "Database Connection Flow"
        MustInitDb["setup.MustInitDb()"] --> DbConnect["db.Connect()"]
        DbConnect --> Migrations["db.MigrationsUp()"]
        Migrations --> CacheRoles["db.CacheOrgRoleIds()"]
    end
    
    subgraph "User Operations"
        GetUser["GetUser(userId)<br/>Single user lookup"] --> UserQuery["SELECT * FROM users<br/>WHERE id = $1"]
        GetUserByEmail["GetUserByEmail(email)"] --> EmailQuery["SELECT * FROM users<br/>WHERE email = $1"]
        CreateUser["CreateUser(name, email, tx)<br/>Domain extraction"] --> InsertUser["INSERT INTO users<br/>RETURNING id"]
    end
    
    subgraph "Organization User Management"
        GetOrgUser["GetOrgUser(userId, orgId)"] --> OrgUserQuery["SELECT * FROM orgs_users<br/>WHERE user_id = $1 AND org_id = $2"]
        ListOrgUsers["ListOrgUsers(orgId)"] --> ListUsers["ListUsers(orgId)<br/>JOIN with users table"]
        GetOrgUserConfig["GetOrgUserConfig()"] --> ConfigQuery["SELECT config FROM orgs_users"]
    end
    
    subgraph "Error Handling"
        SqlNoRows["sql.ErrNoRows<br/>Returns nil"] --> NonUniqueErr["IsNonUniqueErr()<br/>Duplicate handling"]
        NonUniqueErr --> PqArray["pq.Array() for bulk operations"]
    end
    
    UserQuery --> SqlNoRows
    EmailQuery --> SqlNoRows
    InsertUser --> NonUniqueErr
    ListUsers --> PqArray
```

The database layer includes sophisticated error handling and transaction management:
- `sql.ErrNoRows` handling to distinguish between missing records and errors
- Domain extraction from email addresses for user categorization
- Bulk operations using PostgreSQL array parameters via `pq.Array()`
- Transaction support with `*sqlx.Tx` parameter passing
- Role-based access control with `NumUsersWithRole()` validation

**Sources:** [app/server/db/user_helpers.go:13-26](), [app/server/db/user_helpers.go:28-41](), [app/server/db/user_helpers.go:132-155](), [app/server/db/user_helpers.go:98-130](), [app/server/setup/setup.go:27-42]()

## Server Lifecycle and LiteLLM Integration

The server initialization process in `main.go` includes critical AI model proxy setup and graceful shutdown handling:

```mermaid
graph LR
    subgraph "Initialization Sequence"
        MainStart["main()"] --> LogConfig["log.SetFlags()<br/>LstdFlags | Lmicroseconds | Lshortfile"]
        LogConfig --> RouteReg["routes.RegisterHandlePlandex()<br/>Function pointer setup"]
        RouteReg --> LiteLLMSetup["model.EnsureLiteLLM(2)<br/>AI proxy startup"]
        LiteLLMSetup --> ShutdownReg["setup.RegisterShutdownHook()<br/>model.ShutdownLiteLLMServer()"]
    end
    
    subgraph "Router Configuration"
        RouterCreate["mux.NewRouter()"] --> HealthRoutes["routes.AddHealthRoutes(r)"]
        HealthRoutes --> ApiRoutes["routes.AddApiRoutes(r)"]
        ApiRoutes --> ProxyRoutes["routes.AddProxyableApiRoutes(r)"]
    end
    
    subgraph "Server Startup"
        IPLoad["setup.MustLoadIp()"] --> DBInit["setup.MustInitDb()"]
        DBInit --> ServerStart["setup.StartServer(r, nil, nil)"]
        ServerStart --> OsExit["os.Exit(0)"]
    end
    
    ShutdownReg --> RouterCreate
    ProxyRoutes --> IPLoad
```

Key lifecycle components include:
- LiteLLM proxy server management with retry count parameter (2 retries)
- Comprehensive logging configuration with microsecond timestamps and short file names  
- Shutdown hook registration for clean AI model proxy termination
- Fatal error handling with `panic()` for critical startup failures
- Graceful exit with `os.Exit(0)` after server shutdown completion

**Sources:** [app/server/main.go:14-38](), [app/server/main.go:22-28](), [app/server/setup/setup.go:44-48]()

## Client-Server Communication

The CLI communicates with the server through a sophisticated HTTP client architecture with retry logic, authentication, and timeout management:

```mermaid
graph TD
    subgraph "Client Architecture"
        ApiStruct["Api struct<br/>implements types.ApiClient"] --> GetApiHost["GetApiHost()<br/>Cloud vs self-hosted"]
        GetApiHost --> ClientTypes["Multiple HTTP clients<br/>Fast, Slow, Streaming"]
    end
    
    subgraph "Transport Layer"
        BaseTransport["baseTransport<br/>net.Dialer timeout: 10s"] --> RetryTransport["retryTransport<br/>MaxRetries: 3<br/>BaseDelay: 500ms<br/>MaxDelay: 5s<br/>Jitter: 300ms"]
        RetryTransport --> AuthTransports["authenticatedTransport<br/>vs unauthenticatedTransport"]
    end
    
    subgraph "Client Configurations"
        UnauthClient["unauthenticatedClient<br/>fastReqTimeout: 30s"] --> PublicEndpoints["Health, version checks"]
        AuthFastClient["authenticatedFastClient<br/>fastReqTimeout: 30s"] --> QuickOps["List, get operations"]
        AuthSlowClient["authenticatedSlowClient<br/>slowReqTimeout: 5min"] --> LongOps["Apply, build operations"]
        AuthStreamClient["authenticatedStreamingClient<br/>No timeout"] --> StreamOps["Tell, connect operations"]
    end
    
    subgraph "Retry Logic"
        RetryCheck["retryTransport.RoundTrip()"] --> StatusCheck["RetryStatuses map<br/>502, 503, 504"]
        StatusCheck --> BackoffCalc["Exponential backoff<br/>math.Pow(2, attempt)"]
        BackoffCalc --> JitterAdd["Jitter randomization<br/>rand.Int63n()"]
    end
    
    AuthTransports --> UnauthClient
    AuthTransports --> AuthFastClient
    AuthTransports --> AuthSlowClient
    AuthTransports --> AuthStreamClient
    
    RetryTransport --> RetryCheck
```

The client system includes sophisticated error handling and environment configuration:
- Dynamic API host selection based on `auth.Current.IsCloud` flag
- Development environment support via `PLANDEX_ENV` and `PLANDEX_API_HOST` variables
- Network timeout detection with `net.Error` interface checking
- Exponential backoff with jitter to prevent thundering herd problems
- Authentication header injection via `auth.SetAuthHeader()` and `auth.SetVersionHeader()`

**Sources:** [app/cli/api/clients.go:23-42](), [app/cli/api/clients.go:66-117](), [app/cli/api/clients.go:136-161](), [app/cli/api/clients.go:44-64]()
</old_str>
<new_str>
## HTTP Server Configuration

The server configuration in `setup.go` implements comprehensive middleware, graceful shutdown, and database initialization. The `StartServer` function orchestrates the complete HTTP server lifecycle:

```mermaid
graph LR
    subgraph "Server Configuration"
        StartServer["StartServer()"] --> EnvCheck["GOENV development check"]
        EnvCheck --> ShutdownCtx["shutdown.ShutdownCtx setup"]
        ShutdownCtx --> PortConfig["PORT env var<br/>default: 8099"]
        PortConfig --> MiddlewareStack["Middleware application"]
    end
    
    subgraph "Middleware Pipeline"
        LoggingMW["loggingMiddleware()<br/>Skip /health, /version"] --> MaxBytesMW["maxBytesMiddleware()<br/>1GB limit, 1MB headers"]
        MaxBytesMW --> ConfigureFn["configureFn()<br/>Optional configuration"]
    end
    
    subgraph "HTTP Server Specs"
        ServerConfig["http.Server<br/>Addr: :PORT<br/>MaxHeaderBytes: 1MB<br/>ReadHeaderTimeout: 5s"] --> ListenServe["ListenAndServe()<br/>Goroutine"]
    end
    
    subgraph "Shutdown Handling"
        SignalCapture["signal.Notify()<br/>SIGTERM, SIGINT"] --> WaitActivePlans["waitForActivePlans()<br/>1s ticker polling<br/>plan.NumActivePlans()"]
        WaitActivePlans --> CleanupLocks["db.CleanupActiveLocks()"] 
        CleanupLocks --> HTTPShutdown["server.Shutdown()<br/>30s timeout"]
        HTTPShutdown --> ShutdownHooks["Execute shutdown hooks<br/>model.ShutdownLiteLLMServer()"]
    end
    
    MiddlewareStack --> ServerConfig
    ListenServe --> SignalCapture
```

The middleware stack includes several critical components:
- `loggingMiddleware`: Logs request method, path, and duration while excluding monitoring endpoints
- `maxBytesMiddleware`: Uses `http.MaxBytesReader` to enforce the 1GB request body limit
- Database connection cleanup with deferred `db.Conn.Close()`
- Graceful shutdown with 60-second active plan timeout followed by 30-second HTTP shutdown timeout

**Sources:** [app/server/setup/setup.go:66-185](), [app/server/setup/setup.go:50-64](), [app/server/setup/setup.go:187-214]()

## Route Organization

Routes are organized using the `mux.Router` from Gorilla Mux with a configurable handler registration system. The `routes.go` file defines three distinct route categories:

| Route Function | Purpose | Handler Registration |
|---|---|---|
| `AddHealthRoutes` | System monitoring | `/health`, `/version` endpoints |
| `AddApiRoutes` | Standard CRUD operations | Plan, context, user management |
| `AddProxyableApiRoutes` | Real-time operations | Active plan streaming, status |

```mermaid
graph TD
    subgraph "Route Registration Pattern"
        RegisterFn["routes.RegisterHandlePlandex()"] --> HandlePlandexFn["HandlePlandexFn variable<br/>Function pointer"]
        HandlePlandexFn --> RouteDefinition["router.HandleFunc(path, handler)"]
    end
    
    subgraph "Health Routes"
        HealthCheck["/health --> hooks.ExecHook(hooks.HealthCheck)"]
        VersionCheck["/version --> Read version.txt<br/>Handle IS_CLOUD env"]
    end
    
    subgraph "Standard API Routes (89 total)"
        AccountRoutes["/accounts/email_verifications<br/>/accounts/sign_in<br/>/accounts/sign_out"]
        OrgRoutes["/orgs<br/>/orgs/session<br/>/users"]
        PlanRoutes["/plans<br/>/plans/{planId}<br/>/plans/{planId}/{branch}/context"]
        ModelRoutes["/custom_models<br/>/model_sets<br/>/default_settings"]
    end
    
    subgraph "Proxyable API Routes"
        ConnectRoute["/plans/{planId}/{branch}/connect<br/>ConnectPlanHandler<br/>isStreaming: true"]
        StopRoute["/plans/{planId}/{branch}/stop<br/>StopPlanHandler"]
        StatusRoute["/plans/{planId}/{branch}/build_status<br/>GetBuildStatusHandler"]
    end
    
    RouteDefinition --> HealthCheck
    RouteDefinition --> VersionCheck
    RouteDefinition --> AccountRoutes
    RouteDefinition --> OrgRoutes
    RouteDefinition --> PlanRoutes
    RouteDefinition --> ModelRoutes
    RouteDefinition --> ConnectRoute
    RouteDefinition --> StopRoute
    RouteDefinition --> StatusRoute
```

The route registration uses a function pointer pattern where `HandlePlandexFn` is set during server initialization in `main.go`, allowing for flexible handler configuration while maintaining type safety through the `PlandexHandler` type alias.

**Sources:** [app/server/routes/routes.go:15-28](), [app/server/routes/routes.go:89-190](), [app/server/routes/routes.go:192-203](), [app/server/main.go:18-20]()

## HTTP Server Configuration

The server is configured in `setup.go` with specific timeouts, middleware, and graceful shutdown handling. The `StartServer` function sets up the complete HTTP server stack:

```mermaid
graph LR
    subgraph "Server Setup Flow"
        Start["StartServer()"] --> LoadConfig["Load Configuration<br/>PORT env var"]
        LoadConfig --> Middleware["Apply Middleware<br/>loggingMiddleware<br/>maxBytesMiddleware"]
        Middleware --> HTTPServer["http.Server<br/>MaxHeaderBytes: 1MB<br/>ReadHeaderTimeout: 5s"]
        HTTPServer --> Listen["ListenAndServe<br/>on configured port"]
    end
    
    subgraph "Shutdown Handling"
        SigTerm["SIGTERM/SIGINT"] --> WaitPlans["waitForActivePlans()<br/>60s timeout"]
        WaitPlans --> CleanupLocks["db.CleanupActiveLocks()"]
        CleanupLocks --> ServerShutdown["server.Shutdown()<br/>30s timeout"]
    end
    
    Listen --> SigTerm
```

The server includes several key middleware components:
- `loggingMiddleware`: Logs all requests except `/health` and `/version` endpoints
- `maxBytesMiddleware`: Limits request body size to 1GB
- Authentication middleware: Handled per-route basis in handlers

**Sources:** [app/server/setup/setup.go:66-185](), [app/server/setup/setup.go:50-64](), [app/server/setup/setup.go:206-214]()

## Route Organization

Routes are organized into two main categories defined in `routes.go`:

| Route Category | Function | Purpose |
|---|---|---|
| `AddApiRoutes` | Standard API endpoints | Plan management, context, settings |
| `AddProxyableApiRoutes` | Real-time endpoints | Active plan operations, streaming |

```mermaid
graph TD
    subgraph "API Route Categories"
        Standard["Standard API Routes<br/>addApiRoutes()"]
        Proxyable["Proxyable API Routes<br/>addProxyableApiRoutes()"]
    end
    
    subgraph "Standard Endpoints"
        Plans["/plans - ListPlansHandler<br/>/plans/{id} - GetPlanHandler<br/>/plans/{id}/{branch}/context - LoadContextHandler"]
        Auth["/accounts/sign_in - SignInHandler<br/>/orgs - ListOrgsHandler"]
        Settings["/plans/{id}/settings - GetSettingsHandler<br/>/model_sets - ListModelPacksHandler"]
    end
    
    subgraph "Proxyable Endpoints"
        Connect["/plans/{id}/{branch}/connect - ConnectPlanHandler"]
        Stop["/plans/{id}/{branch}/stop - StopPlanHandler"]
        Status["/plans/{id}/{branch}/build_status - GetBuildStatusHandler"]
    end
    
    Standard --> Plans
    Standard --> Auth
    Standard --> Settings
    
    Proxyable --> Connect
    Proxyable --> Stop
    Proxyable --> Status
```

**Sources:** [app/server/routes/routes.go:73-185](), [app/server/routes/routes.go:187-198]()

## Authentication and Session Management

The server implements a comprehensive authentication system with email verification, sign-in codes, and JWT token management handled primarily in `handlers/sessions.go`:

```mermaid
graph TD
    subgraph "Email Verification Flow"
        CreateVerification["CreateEmailVerificationHandler"] --> CheckUser["GetUserByEmail()<br/>HasAccount determination"]
        CheckUser --> GeneratePin["GetRandomAlphanumeric(6)<br/>SHA256 hash"]
        GeneratePin --> StoreVerification["db.CreateEmailVerification()"]
        StoreVerification --> SendEmail["email.SendVerificationEmail()"]
    end
    
    subgraph "Sign-In Process"
        SignInRequest["SignInHandler"] --> ValidatePin["CheckEmailPinHandler<br/>db.ValidateEmailVerification()"]
        ValidatePin --> ValidateAndSignIn["ValidateAndSignIn()<br/>Create JWT token"]
        ValidateAndSignIn --> SetCookies["Set auth cookies<br/>for browser clients"]
    end
    
    subgraph "Cross-Client Authentication"
        CreateSignInCode["CreateSignInCodeHandler<br/>Authenticated endpoint"] --> GenerateCode["GetRandomAlphanumeric(6)<br/>SHA256 hash"]
        GenerateCode --> StoreCode["db.CreateSignInCode()"]
        StoreCode --> ShareCode["Return plain code<br/>for client transfer"]
    end
    
    subgraph "Session Management"
        SignOut["SignOutHandler"] --> InvalidateToken["UPDATE auth_tokens<br/>SET deleted_at = NOW()"]
        InvalidateToken --> ClearCookies["ClearAuthCookieIfBrowser()<br/>ClearAccountFromCookies()"]
    end
    
    subgraph "User Configuration"
        GetOrgConfig["GetOrgUserConfigHandler"] --> LoadConfig["db.GetOrgUserConfig()"]
        UpdateOrgConfig["UpdateOrgUserConfigHandler"] --> SaveConfig["db.UpdateOrgUserConfig()"]
    end
```

Key authentication features include:
- Local development mode bypass with `GOENV=development` and `LOCAL_MODE=1`
- PIN-based email verification with 6-character alphanumeric codes
- Cross-client sign-in codes for UI-to-CLI authentication transfer
- JWT token invalidation on sign-out with database cleanup
- Per-organization user configuration management

**Sources:** [app/server/handlers/sessions.go:18-136](), [app/server/handlers/sessions.go:176-209](), [app/server/handlers/sessions.go:252-285](), [app/server/handlers/sessions.go:287-346]()

## Database Integration and User Management

Database operations are centralized in the `db` package with comprehensive user and organization management in `user_helpers.go`:

```mermaid
graph TD
    subgraph "Database Connection Flow"
        MustInitDb["setup.MustInitDb()"] --> DbConnect["db.Connect()"]
        DbConnect --> Migrations["db.MigrationsUp()"]
        Migrations --> CacheRoles["db.CacheOrgRoleIds()"]
    end
    
    subgraph "User Operations"
        GetUser["GetUser(userId)<br/>Single user lookup"] --> UserQuery["SELECT * FROM users<br/>WHERE id = $1"]
        GetUserByEmail["GetUserByEmail(email)"] --> EmailQuery["SELECT * FROM users<br/>WHERE email = $1"]
        CreateUser["CreateUser(name, email, tx)<br/>Domain extraction"] --> InsertUser["INSERT INTO users<br/>RETURNING id"]
    end
    
    subgraph "Organization User Management"
        GetOrgUser["GetOrgUser(userId, orgId)"] --> OrgUserQuery["SELECT * FROM orgs_users<br/>WHERE user_id = $1 AND org_id = $2"]
        ListOrgUsers["ListOrgUsers(orgId)"] --> ListUsers["ListUsers(orgId)<br/>JOIN with users table"]
        GetOrgUserConfig["GetOrgUserConfig()"] --> ConfigQuery["SELECT config FROM orgs_users"]
    end
    
    subgraph "Error Handling"
        SqlNoRows["sql.ErrNoRows<br/>Returns nil"] --> NonUniqueErr["IsNonUniqueErr()<br/>Duplicate handling"]
        NonUniqueErr --> PqArray["pq.Array() for bulk operations"]
    end
    
    UserQuery --> SqlNoRows
    EmailQuery --> SqlNoRows
    InsertUser --> NonUniqueErr
    ListUsers --> PqArray
```

The database layer includes sophisticated error handling and transaction management:
- `sql.ErrNoRows` handling to distinguish between missing records and errors
- Domain extraction from email addresses for user categorization
- Bulk operations using PostgreSQL array parameters via `pq.Array()`
- Transaction support with `*sqlx.Tx` parameter passing
- Role-based access control with `NumUsersWithRole()` validation

**Sources:** [app/server/db/user_helpers.go:13-26](), [app/server/db/user_helpers.go:28-41](), [app/server/db/user_helpers.go:132-155](), [app/server/db/user_helpers.go:98-130](), [app/server/setup/setup.go:27-42]()

## Server Lifecycle and LiteLLM Integration

The server initialization process in `main.go` includes critical AI model proxy setup and graceful shutdown handling:

```mermaid
graph LR
    subgraph "Initialization Sequence"
        MainStart["main()"] --> LogConfig["log.SetFlags()<br/>LstdFlags | Lmicroseconds | Lshortfile"]
        LogConfig --> RouteReg["routes.RegisterHandlePlandex()<br/>Function pointer setup"]
        RouteReg --> LiteLLMSetup["model.EnsureLiteLLM(2)<br/>AI proxy startup"]
        LiteLLMSetup --> ShutdownReg["setup.RegisterShutdownHook()<br/>model.ShutdownLiteLLMServer()"]
    end
    
    subgraph "Router Configuration"
        RouterCreate["mux.NewRouter()"] --> HealthRoutes["routes.AddHealthRoutes(r)"]
        HealthRoutes --> ApiRoutes["routes.AddApiRoutes(r)"]
        ApiRoutes --> ProxyRoutes["routes.AddProxyableApiRoutes(r)"]
    end
    
    subgraph "Server Startup"
        IPLoad["setup.MustLoadIp()"] --> DBInit["setup.MustInitDb()"]
        DBInit --> ServerStart["setup.StartServer(r, nil, nil)"]
        ServerStart --> OsExit["os.Exit(0)"]
    end
    
    ShutdownReg --> RouterCreate
    ProxyRoutes --> IPLoad
```

Key lifecycle components include:
- LiteLLM proxy server management with retry count parameter (2 retries)
- Comprehensive logging configuration with microsecond timestamps and short file names  
- Shutdown hook registration for clean AI model proxy termination
- Fatal error handling with `panic()` for critical startup failures
- Graceful exit with `os.Exit(0)` after server shutdown completion

**Sources:** [app/server/main.go:14-38](), [app/server/main.go:22-28](), [app/server/setup/setup.go:44-48]()

## Request Processing Pipeline

Each request goes through a standardized processing pipeline with middleware, authentication, and business logic layers:

```mermaid
graph TD
    subgraph "Middleware Layer"
        IncomingReq["HTTP Request"] --> LogMiddleware["loggingMiddleware()<br/>Log method & path"]
        LogMiddleware --> MaxBytesMiddleware["maxBytesMiddleware()<br/>1GB body limit"]
        MaxBytesMiddleware --> RouterMatch["mux.Router<br/>Path matching"]
    end
    
    subgraph "Handler Execution"
        RouterMatch --> HandlerType{Handler Type}
        HandlerType -->|Authentication Required| AuthFlow["Authenticate(w, r, true)<br/>JWT validation"]
        HandlerType -->|Public Endpoint| DirectHandler["Health/Version handlers"]
        AuthFlow --> ParseBody["Parse Request Body<br/>json.Unmarshal()"]
        ParseBody --> BizLogic["Handler-specific Logic"]
    end
    
    subgraph "Response Generation"
        BizLogic --> ProcessResult["Process Result"]
        ProcessResult --> MarshalResp["json.Marshal(response)"]
        MarshalResp --> WriteResponse["w.Write(bytes)"]
        DirectHandler --> WriteResponse
    end
    
    subgraph "Error Handling"
        AuthFlow -->|Auth Failure| AuthError["http.Error()<br/>401/403 status"]
        ParseBody -->|Parse Error| ParseError["http.Error()<br/>400 status"]
        BizLogic -->|Logic Error| BizError["http.Error()<br/>5xx status"]
    end
```

The pipeline includes comprehensive error handling at each stage:
- Middleware errors return early with appropriate HTTP status codes
- Authentication failures use standard HTTP error responses
- JSON parsing errors return 400 Bad Request
- Business logic errors map to appropriate 4xx/5xx status codes

**Sources:** [app/server/setup/setup.go:50-64](), [app/server/handlers/sessions.go:179-183](), [app/server/handlers/sessions.go:223-237]()

## Client-Server Communication

The CLI communicates with the server through HTTP clients with sophisticated retry and authentication logic:

```mermaid
graph TD
    subgraph "Client Architecture"
        ApiStruct["Api struct<br/>Implements ApiClient"] --> Clients["HTTP Clients<br/>Fast, Slow, Streaming"]
        Clients --> Transport["Transport Layer<br/>Retry & Auth"]
    end
    
    subgraph "Transport Types"
        AuthTransport["authenticatedTransport<br/>Adds auth headers"] --> RetryTransport["retryTransport<br/>Exponential backoff<br/>502/503/504 retries"]
        UnauthTransport["unauthenticatedTransport<br/>No auth required"]
    end
    
    subgraph "Client Types"
        FastClient["authenticatedFastClient<br/>30s timeout"] --> QuickOps["Quick operations<br/>List, Get, Delete"]
        SlowClient["authenticatedSlowClient<br/>5min timeout"] --> LongOps["Long operations<br/>Apply, Build"]
        StreamClient["authenticatedStreamingClient<br/>No timeout"] --> RealTime["Real-time ops<br/>Tell, Connect"]
    end
    
    Transport --> AuthTransport
    Transport --> UnauthTransport
    Clients --> FastClient
    Clients --> SlowClient
    Clients --> StreamClient
```

**Sources:** [app/cli/api/clients.go:18-160]()

## Server Lifecycle Management

The server implements graceful startup and shutdown procedures:

```mermaid
graph LR
    subgraph "Startup Sequence"
        Start["main()"] --> LoadIP["MustLoadIp()<br/>Host configuration"]
        LoadIP --> InitDB["MustInitDb()<br/>Connect & migrate"]
        InitDB --> StartServer["StartServer()<br/>HTTP listener"]
    end
    
    subgraph "Shutdown Sequence"
        Signal["SIGTERM/SIGINT"] --> WaitPlans["Wait for Active Plans<br/>60s timeout"]
        WaitPlans --> CleanupLocks["Cleanup Repository Locks<br/>db.CleanupActiveLocks"]
        CleanupLocks --> HTTPShutdown["HTTP Server Shutdown<br/>30s timeout"]
        HTTPShutdown --> DBClose["Close Database<br/>db.Conn.Close()"]
    end
    
    StartServer --> Signal
```

**Sources:** [app/server/main.go:12-28](), [app/server/setup/setup.go:20-42](), [app/server/setup/setup.go:119-185]()

---

