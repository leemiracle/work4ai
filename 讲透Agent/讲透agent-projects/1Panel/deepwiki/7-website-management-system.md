<!-- source: DeepWiki mcp.deepwiki.com · repo 1Panel-dev/1Panel · page 7 Website Management System · fetched 2026-10-29 -->

# Website Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/dto/request/website.go](agent/app/dto/request/website.go)
- [agent/app/dto/response/website.go](agent/app/dto/response/website.go)
- [agent/app/service/website.go](agent/app/service/website.go)
- [agent/app/service/website_utils.go](agent/app/service/website_utils.go)
- [frontend/src/api/interface/website.ts](frontend/src/api/interface/website.ts)
- [frontend/src/api/modules/website.ts](frontend/src/api/modules/website.ts)

</details>



The Website Management System is the core web server management component of 1Panel, providing comprehensive Nginx/OpenResty-based website hosting capabilities. This system handles website creation, configuration, domain management, SSL certificates, reverse proxy setup, and various advanced features like load balancing, anti-leech protection, and authentication.

This document covers website operations and Nginx configuration. For SSL certificate lifecycle management details, see the SSL subsections within this page. For application deployment that creates websites automatically, see [Application Management System](#6).

---

## System Overview

The Website Management System is implemented in the Agent backend service and operates as a high-level abstraction over Nginx/OpenResty. It supports six website types, each with distinct configurations and use cases.

### Core Components

The system is built around three primary service interfaces:

- **`IWebsiteService`** [agent/app/service/website.go:49-132]() - Main website operations interface with 40+ methods
- **Nginx Parser System** - Custom configuration parser for manipulating Nginx config files programmatically
- **WAF Integration** - Web Application Firewall configuration synchronized with website changes
- **Task Execution System** - Asynchronous operations for complex website creation workflows

**Website Types:**

| Type | Constant | Description | Primary Use Case |
|------|----------|-------------|------------------|
| Static | `constant.Static` | Pure HTML/CSS/JS hosting | Static websites, SPAs |
| Runtime | `constant.Runtime` | Language runtime integration | PHP, Node.js, Python, Java, Go, .NET applications |
| Deployment | `constant.Deployment` | App Store application linking | WordPress, Halo, GitLab, etc. |
| Proxy | `constant.Proxy` | Reverse proxy configuration | Microservices, API gateways |
| Stream | `constant.Stream` | TCP/UDP load balancing | Database proxies, game servers |
| Subsite | `constant.Subsite` | Subdirectory within parent site | Multi-tenant hosting |

Sources: [agent/app/service/website.go:49-132](), [agent/app/dto/request/website.go:16-42](), [frontend/src/api/interface/website.ts:3-32]()

---

## Website Type Architecture

```mermaid
graph TB
    subgraph "Website Type Hierarchy"
        Static["Static<br/>constant.Static"]
        Runtime["Runtime<br/>constant.Runtime"]
        Deployment["Deployment<br/>constant.Deployment"]
        Proxy["Proxy<br/>constant.Proxy"]
        Stream["Stream<br/>constant.Stream"]
        Subsite["Subsite<br/>constant.Subsite"]
    end
    
    subgraph "Runtime Subtypes"
        PHP["PHP<br/>constant.RuntimePHP"]
        Node["Node.js<br/>constant.RuntimeNode"]
        Java["Java<br/>constant.RuntimeJava"]
        Go["Go<br/>constant.RuntimeGo"]
        Python["Python<br/>constant.RuntimePython"]
        DotNet[".NET<br/>constant.RuntimeDotNet"]
    end
    
    subgraph "Configuration Components"
        NginxServer["Server Block<br/>components.Server"]
        NginxLocation["Location Block<br/>components.Location"]
        NginxUpstream["Upstream Block<br/>components.Upstream"]
        ProxyPass["proxy_pass Directive"]
        Root["root Directive"]
        PHPProxy["FastCGI PHP Config"]
    end
    
    subgraph "File System Structure"
        SiteDir["/www/sites/{alias}/"]
        IndexDir["/www/sites/{alias}/index/"]
        LogDir["/www/sites/{alias}/log/"]
        SSLDir["/www/sites/{alias}/ssl/"]
        ProxyDir["/www/sites/{alias}/proxy/"]
        RewriteDir["/www/sites/{alias}/rewrite/"]
    end
    
    Static --> NginxServer
    Runtime --> NginxServer
    Deployment --> NginxServer
    Proxy --> NginxServer
    Stream --> NginxUpstream
    Subsite --> NginxServer
    
    Runtime --> PHP
    Runtime --> Node
    Runtime --> Java
    Runtime --> Go
    Runtime --> Python
    Runtime --> DotNet
    
    Static --> Root
    PHP --> PHPProxy
    Node --> ProxyPass
    Java --> ProxyPass
    Go --> ProxyPass
    Python --> ProxyPass
    DotNet --> ProxyPass
    Deployment --> ProxyPass
    Proxy --> ProxyPass
    
    NginxServer --> SiteDir
    SiteDir --> IndexDir
    SiteDir --> LogDir
    SiteDir --> SSLDir
    SiteDir --> ProxyDir
    SiteDir --> RewriteDir
```

**Type-Specific Configurations:**

- **Static**: Uses `server.UpdateRoot()` to point to `/www/sites/{alias}/index` [agent/app/service/website_utils.go:262-264]()
- **Runtime (PHP)**: Configures FastCGI with `server.UpdatePHPProxy()` supporting Unix socket or TCP [agent/app/service/website_utils.go:271-280]()
- **Runtime (Others)**: Reverse proxy to runtime port with `server.UpdateRootProxy()` [agent/app/service/website_utils.go:281-283]()
- **Deployment**: Proxies to app install's `HttpPort` [agent/app/service/website_utils.go:260-261]()
- **Stream**: Creates TCP/UDP upstream blocks without HTTP server context [agent/app/service/website_utils.go:194-232]()
- **Subsite**: Inherits parent website's proxy/runtime configuration [agent/app/service/website_utils.go:285-312]()

Sources: [agent/app/service/website_utils.go:182-325](), [agent/app/service/website.go:241-536]()

---

## Website Creation Workflow

The website creation process uses a task-based system with subtasks for different operations, enabling atomic rollback on failure.

```mermaid
sequenceDiagram
    participant API as "API Handler"
    participant Service as "WebsiteService"
    participant Task as "Task System<br/>task.Task"
    participant FS as "File System"
    participant Nginx as "Nginx Parser"
    participant OpenResty as "OpenResty Container"
    participant DB as "agent.db"
    
    API->>Service: CreateWebsite(req)
    Service->>Service: Validate alias uniqueness
    Service->>Service: Check port availability
    
    Service->>Task: NewTaskWithOps("create", website)
    Task-->>Service: createTask
    
    alt Create Database (if req.CreateDb)
        Service->>Task: AddSubTask("createDatabase")
        Task->>DB: Create MySQL/PostgreSQL DB
        Task->>Service: website.DbID = dbID
    end
    
    alt Install New App (if Deployment + NewApp)
        Service->>Task: Install app via AppService
        Task->>Service: website.AppInstallID = installID
    end
    
    Service->>Task: AddSubTask("ConfigOpenresty")
    Task->>FS: createWebsiteFolder(website)
    FS->>FS: mkdir /www/sites/{alias}
    FS->>FS: Create log/, index/, ssl/ dirs
    FS->>FS: Write index.html or index.php
    
    Task->>Nginx: configDefaultNginx(website, domains)
    Nginx->>Nginx: Parse template (website_default.conf)
    Nginx->>Nginx: Configure server block
    Nginx->>Nginx: Set listen ports + domains
    Nginx->>Nginx: Configure proxy/root/php
    Nginx->>FS: Write /www/server/openresty/conf.d/{alias}.conf
    
    Task->>OpenResty: nginx -t (validate config)
    OpenResty-->>Task: Config OK
    Task->>OpenResty: nginx -s reload
    
    Task->>Task: createWafConfig(website)
    Task->>FS: Update 1pwaf/data/conf/sites.json
    Task->>FS: Copy WAF rules to 1pwaf/data/sites/{alias}
    
    Task->>DB: websiteRepo.Create(website)
    Task->>DB: websiteDomainRepo.BatchCreate(domains)
    DB-->>Task: website.ID
    
    alt Enable SSL (if req.EnableSSL)
        Task->>Task: AddSubTask("EnableSSL")
        Task->>Service: applySSL(website, websiteSSL)
        Task->>Nginx: Configure ssl_certificate paths
        Task->>Nginx: Add HTTPS listen directives
        Task->>OpenResty: nginx -s reload
    end
    
    alt Create FTP User
        Task->>Task: AddSubTask("ConfigFTP")
        Task->>Service: NewIFtpService().Create()
        Task->>Service: website.FtpID = ftpID
    end
    
    Task->>Service: Execute() all subtasks
    Service-->>API: Success / Error
```

**Key Functions:**

- `CreateWebsite()` [agent/app/service/website.go:241-536]() - Main orchestration function
- `configDefaultNginx()` [agent/app/service/website_utils.go:182-325]() - Generates initial Nginx configuration
- `createWebsiteFolder()` [agent/app/service/website_utils.go:133-180]() - Creates directory structure
- `createWafConfig()` [agent/app/service/website_utils.go:410-480]() - Synchronizes WAF settings
- `createIndexFile()` [agent/app/service/website_utils.go:50-98]() - Creates default index.html/index.php

**Rollback Mechanism:**

Each subtask can define a rollback function. If any step fails, `deleteWebsite()` is called to clean up:
```go
deleteWebsite := func(t *task.Task) {
    _ = deleteWebsiteFolder(website)
}
createTask.AddSubTask(i18n.GetMsgByKey("ConfigOpenresty"), configNginx, deleteWebsite)
```

Sources: [agent/app/service/website.go:241-536](), [agent/app/service/website_utils.go:133-325](), [agent/app/service/website_utils.go:410-480]()

---

## Nginx Configuration Management System

1Panel uses a custom Nginx parser that provides programmatic manipulation of Nginx configuration files while preserving formatting and comments.

### Configuration Parser Architecture

```mermaid
graph TB
    subgraph "Parser Layer"
        StringParser["parser.NewStringParser()"]
        FileParser["parser.NewParser(filepath)"]
        ParseResult["components.Config"]
    end
    
    subgraph "Component Types"
        Config["components.Config"]
        Server["components.Server"]
        Location["components.Location"]
        Upstream["components.Upstream"]
        Directive["components.Directive"]
    end
    
    subgraph "Manipulation Operations"
        UpdateListen["server.UpdateListen(port)"]
        UpdateServerName["server.UpdateServerName(domains)"]
        UpdateRoot["server.UpdateRoot(path)"]
        UpdateProxy["server.UpdateRootProxy(proxy)"]
        UpdatePHP["server.UpdatePHPProxy(proxy, path)"]
        UpdateDirective["server.UpdateDirective(name, params)"]
        DeleteDirective["server.RemoveDirective(name)"]
    end
    
    subgraph "Write Operations"
        WriteConfig["nginx.WriteConfig(config, style)"]
        Validate["nginxCheckAndReload()"]
        Rollback["Restore from OldContent"]
    end
    
    FileParser --> ParseResult
    StringParser --> ParseResult
    ParseResult --> Config
    
    Config --> Server
    Server --> Location
    Config --> Upstream
    Server --> Directive
    
    UpdateListen --> Server
    UpdateServerName --> Server
    UpdateRoot --> Server
    UpdateProxy --> Server
    UpdatePHP --> Server
    UpdateDirective --> Server
    DeleteDirective --> Server
    
    Server --> WriteConfig
    WriteConfig --> Validate
    Validate -->|"nginx -t fails"| Rollback
    Validate -->|"nginx -t OK"| OpenResty["nginx -s reload"]
```

**Key Components:**

| Component | Purpose | File Reference |
|-----------|---------|----------------|
| `parser.NewParser()` | Parse existing Nginx config file | [agent/app/service/website_utils.go:619]() |
| `components.Server` | Represents server {} block | [agent/app/service/website_utils.go:244-312]() |
| `components.Location` | Represents location {} block | [agent/app/service/website_utils.go:120-129]() |
| `components.Upstream` | Represents upstream {} block | [agent/app/service/website_utils.go:224-231]() |
| `nginx.WriteConfig()` | Serialize config to file | [agent/app/service/website_utils.go:315-316]() |

### Configuration Scopes and Updates

The system organizes configuration by "scopes" that map to Nginx contexts:

```go
// Example scope-based update
func UpdateNginxConfigByScope(req request.NginxConfigUpdate) error {
    keys := dto.ScopeKeyMap[req.Scope]  // e.g., "gzip" -> ["gzip", "gzip_comp_level"]
    website := websiteRepo.GetFirst(repo.WithByID(req.WebsiteID))
    
    if req.Operate == constant.ConfigDel {
        return deleteNginxConfig(constant.NginxScopeServer, nginxParams, &website)
    }
    
    params := getNginxParams(req.Params, keys)
    return updateNginxConfig(constant.NginxScopeServer, params, &website)
}
```

**Scope Constants:**

- `constant.NginxScopeServer` - Server block directives
- `constant.NginxScopeLocation` - Location block directives
- `constant.NginxScopeUpstream` - Upstream block directives

**Validation with Rollback:**

Every configuration change follows this pattern [agent/app/service/website_utils.go:1061-1076]():

1. Save original config content to `nginxConfig.OldContent`
2. Modify configuration objects in memory
3. Write new config with `nginx.WriteConfig()`
4. Test with `nginx -t` via `nginxCheckAndReload()`
5. On failure: restore original content and reload
6. On success: reload with `nginx -s reload`

Sources: [agent/app/service/website.go:774-820](), [agent/app/service/website_utils.go:182-325](), [agent/app/service/website_utils.go:1061-1076]()

---

## Domain Management

Websites support multiple domains with independent port and SSL configurations per domain.

### Domain Data Model

```mermaid
erDiagram
    Website ||--o{ WebsiteDomain : "has"
    Website {
        uint ID
        string PrimaryDomain
        string Alias
        string Type
        string Protocol
        uint WebsiteSSLID
        bool IPV6
        bool DefaultServer
    }
    WebsiteDomain {
        uint ID
        uint WebsiteID
        string Domain
        int Port
        bool SSL
    }
```

**Domain Operations:**

| Operation | Method | Description |
|-----------|--------|-------------|
| Create | `CreateWebsiteDomain()` [agent/app/service/website_domain.go:11-90]() | Add domains with port/SSL flags |
| Delete | `DeleteWebsiteDomain()` [agent/app/service/website_domain.go:92-141]() | Remove domain and Nginx listen |
| Update | `UpdateWebsiteDomain()` [agent/app/service/website.go:742-772]() | Toggle SSL on specific domain |
| List | `GetWebsiteDomain()` [agent/app/service/website_domain.go:143-148]() | Retrieve all domains for website |

### Domain-Specific SSL Configuration

Each domain can have independent SSL settings. When updating domain SSL status [agent/app/service/website.go:742-772]():

```go
func UpdateWebsiteDomain(req request.WebsiteDomainUpdate) error {
    domain := websiteDomainRepo.GetFirst(repo.WithByID(req.ID))
    domain.SSL = req.SSL
    
    // Update Nginx listen directives
    server := config.FindServers()[0]
    server.DeleteListen(strconv.Itoa(domain.Port))
    
    http3 := isHttp3(server)
    setListen(server, strconv.Itoa(domain.Port), website.IPV6, http3, 
              website.DefaultServer, domain.SSL && website.Protocol == constant.ProtocolHTTPS)
    
    nginx.WriteConfig(config, nginx.IndentedStyle)
    nginxCheckAndReload(...)
}
```

**Listen Directive Generation:**

The `setListen()` function [agent/app/service/website_utils.go:638-654]() creates Nginx listen directives based on:
- Port number
- IPv6 support (`listen [::]:443 ssl`)
- HTTP/3 support (`listen 443 quic`)
- Default server flag (`listen 443 default_server ssl`)
- SSL status (`listen 443 ssl`)

### Multi-Domain Examples

**Scenario 1: Multiple domains, same port, shared SSL**
```
Domain: example.com, Port: 80, SSL: false
Domain: www.example.com, Port: 80, SSL: false
```
Generates:
```nginx
listen 80;
server_name example.com www.example.com;
```

**Scenario 2: Different ports per domain**
```
Domain: api.example.com, Port: 8080, SSL: false
Domain: admin.example.com, Port: 8081, SSL: true
```
Generates:
```nginx
listen 8080;
listen 8081 ssl;
server_name api.example.com admin.example.com;
```

Sources: [agent/app/service/website_domain.go:11-148](), [agent/app/service/website.go:742-772](), [agent/app/service/website_utils.go:588-654]()

---

## SSL Certificate Management

The system integrates ACME protocol support for automated certificate issuance via Let's Encrypt and ZeroSSL, with DNS validation through 50+ providers.

### SSL Configuration Flow

```mermaid
sequenceDiagram
    participant User as "User/API"
    participant Service as "WebsiteService"
    participant SSL as "WebsiteSSL Model"
    participant Parser as "Nginx Parser"
    participant FS as "File System"
    participant Nginx as "OpenResty"
    
    User->>Service: OpWebsiteHTTPS(req)
    
    alt Enable HTTPS
        Service->>Service: Get/Create WebsiteSSL
        Service->>Service: getHttpsPort(websiteID)
        Note over Service: Determine which ports need SSL
        
        Service->>FS: createPemFile(website, websiteSSL)
        FS->>FS: Write fullchain.pem
        FS->>FS: Write privkey.pem
        
        Service->>Parser: applySSL(website, websiteSSL, req)
        Parser->>Parser: Update listen directives with "ssl"
        Parser->>Parser: Set ssl_certificate paths
        Parser->>Parser: Set ssl_protocols [TLSv1.2, TLSv1.3]
        Parser->>Parser: Set ssl_ciphers
        
        alt HTTP Config: HTTPToHTTPS
            Parser->>Parser: Add HTTP->HTTPS redirect
            Parser->>Parser: Keep port 80 listen
            Parser->>Parser: AddHTTP2HTTPS(sslPort)
        end
        
        alt HTTP Config: HTTPSOnly
            Parser->>Parser: Remove port 80 listen
            Parser->>Parser: Remove HTTP redirect
        end
        
        alt HTTP Config: HTTPAlso
            Parser->>Parser: Keep port 80 listen
            Parser->>Parser: Remove HTTP redirect
        end
        
        alt HSTS Enabled
            Parser->>Parser: Add "Strict-Transport-Security" header
        end
        
        alt HTTP/3 Enabled
            Parser->>Parser: Add "listen 443 quic"
            Parser->>Parser: Add "Alt-Svc" header
        end
        
        Service->>Nginx: nginx -t
        Service->>Nginx: nginx -s reload
        Service->>Service: website.Protocol = "https"
        Service->>Service: website.WebsiteSSLID = sslID
        
    else Disable HTTPS
        Service->>Parser: Remove SSL listen directives
        Service->>Parser: Delete ssl_certificate directives
        Service->>Parser: Delete SSL headers
        Service->>Service: website.Protocol = "http"
        Service->>Service: website.WebsiteSSLID = 0
    end
    
    Service->>DB: websiteRepo.Save(website)
```

**SSL/HTTPS Components:**

| Component | Purpose | Storage Location |
|-----------|---------|------------------|
| `fullchain.pem` | Certificate + intermediate chain | `/www/sites/{alias}/ssl/fullchain.pem` |
| `privkey.pem` | Private key | `/www/sites/{alias}/ssl/privkey.pem` |
| `WebsiteSSL` model | Certificate metadata in database | `agent.db` `website_ssl` table |
| SSL configuration | Nginx directives | Within server block in site config |

### HTTPS Configuration Modes

**HttpConfig Options** [agent/app/service/website_utils.go:788-809]():

1. **`HTTPToHTTPS`**: Redirect all HTTP to HTTPS
   ```nginx
   if ($scheme = http) {
       return 301 https://$host:443$request_uri;
   }
   ```

2. **`HTTPSOnly`**: Disable HTTP entirely (remove port 80 listen)

3. **`HTTPAlso`**: Allow both HTTP and HTTPS without redirect

### SSL Protocol Configuration

The system supports configurable SSL protocols and cipher suites [agent/app/service/website_utils.go:832-863]():

**Default SSL Protocols:** `TLSv1.3`, `TLSv1.2`

**Default Cipher Suite:**
```
ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:
ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:
ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:
DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:
ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:
!aNULL:!eNULL:!EXPORT:!DSS:!DES:!RC4:!3DES:!MD5:!PSK:!KRB5:!SRP:!CAMELLIA:!SEED
```

### HSTS Configuration

HTTP Strict Transport Security can be enabled with subdomain support [agent/app/service/website_utils.go:864-875]():

```go
if req.Hsts {
    var hstsValue string
    if req.HstsIncludeSubDomains {
        hstsValue = "\"max-age=31536000; includeSubDomains\""
    } else {
        hstsValue = "\"max-age=31536000\""
    }
    nginxParams = append(nginxParams, dto.NginxParam{
        Name:   "add_header",
        Params: []string{"Strict-Transport-Security", hstsValue},
    })
}
```

### HTTP/3 Support

When HTTP/3 is enabled [agent/app/service/website_utils.go:876-881]():
- Adds `listen 443 quic` directive
- Adds `Alt-Svc: 'h3=":443"; ma=2592000'` header
- Requires OpenResty with QUIC support

Sources: [agent/app/service/website.go:842-1013](), [agent/app/service/website_utils.go:678-887](), [agent/app/service/website_ssl.go]()

---

## Advanced Features

### Reverse Proxy Configuration

The Proxy website type and proxy configuration feature support flexible reverse proxy setups with caching, header manipulation, and CORS.

**Proxy Configuration Structure:**

```mermaid
graph TB
    Website["Website Model"]
    ProxyDir["/www/sites/{alias}/proxy/"]
    RootConf["root.conf<br/>(root location)"]
    NamedConfs["named configs<br/>(custom locations)"]
    
    Website --> ProxyDir
    ProxyDir --> RootConf
    ProxyDir --> NamedConfs
    
    subgraph "Proxy Location Block"
        Location["location {modifier} {match}"]
        ProxyPass["proxy_pass {target}"]
        ProxyHost["proxy_set_header Host"]
        Cache["proxy_cache settings"]
        CORS["CORS headers"]
        SNI["proxy_ssl_name (SNI)"]
    end
    
    RootConf --> Location
    NamedConfs --> Location
    Location --> ProxyPass
    Location --> ProxyHost
    Location --> Cache
    Location --> CORS
    Location --> SNI
```

**Proxy Operations** [agent/app/service/website_proxy.go]():

| Method | Purpose | File Reference |
|--------|---------|----------------|
| `OperateProxy()` | Create/update/enable/disable proxy config | Line 16-200 |
| `GetProxies()` | List all proxy configurations | Line 202-281 |
| `UpdateProxyFile()` | Direct file edit | Line 283-324 |
| `DeleteProxy()` | Remove proxy configuration | Line 412-460 |
| `GetProxyCache()` | Get cache settings | Line 326-365 |
| `UpdateProxyCache()` | Update cache settings | Line 367-410 |

**CORS Configuration:**

Proxy locations can enable CORS with configurable origins, methods, and headers [agent/app/dto/request/website.go:275-282]():

```go
type CorsConfig struct {
    Cors             bool   `json:"cors"`
    AllowOrigins     string `json:"allowOrigins"`     // e.g., "https://example.com"
    AllowMethods     string `json:"allowMethods"`     // e.g., "GET,POST,PUT"
    AllowHeaders     string `json:"allowHeaders"`     // e.g., "Content-Type,Authorization"
    AllowCredentials bool   `json:"allowCredentials"`
    Preflight        bool   `json:"preflight"`        // Handle OPTIONS requests
}
```

### Load Balancing (Upstream)

Websites can configure Nginx upstream blocks for load balancing across multiple backend servers.

**Upstream Configuration:**

```go
type NginxUpstream struct {
    Name      string                    // Upstream block name
    Algorithm string                    // "default", "ip_hash", "least_conn", "random"
    Servers   []NginxUpstreamServer
}

type NginxUpstreamServer struct {
    Server          string  // "192.168.1.10:8080"
    Weight          int     // Load balancing weight
    MaxFails        int     // Max failed attempts before marking down
    FailTimeout     int     // Time to mark server as down
    FailTimeoutUnit string  // "s", "m", "h"
    MaxConns        int     // Max concurrent connections
    Flag            string  // "down", "backup"
}
```

**Load Balancing Methods** [agent/app/service/website_load_balance.go:13-166]():

- **default** (round-robin): Distribute evenly
- **ip_hash**: Client IP-based sticky sessions
- **least_conn**: Route to server with fewest connections
- **random**: Random distribution

### Anti-Leech Protection

Prevents hotlinking by validating referrer headers [agent/app/service/website_anti_leech.go:11-120]():

```go
type LeechConfig struct {
    Enable      bool
    Cache       bool
    CacheTime   int
    CacheUnit   string
    Extends     string      // File extensions: "jpg|png|gif"
    Return      string      // Return code or redirect URL
    ServerNames []string    // Allowed referrer domains
    NoneRef     bool        // Block empty referrer
    LogEnable   bool
    Blocked     bool        // Block or allow listed domains
}
```

Generates Nginx configuration:
```nginx
location ~* \.(jpg|png|gif)$ {
    valid_referers none blocked example.com *.example.com;
    if ($invalid_referer) {
        return 403;
    }
}
```

### Basic Authentication

HTTP Basic Auth at server or path level [agent/app/service/website_auth.go:11-200]():

**Server-Level Auth:**
```nginx
auth_basic "Restricted Area";
auth_basic_user_file /www/sites/{alias}/auth/.htpasswd;
```

**Path-Level Auth:**
```nginx
location /admin {
    auth_basic "Admin Area";
    auth_basic_user_file /www/sites/{alias}/auth/admin/.htpasswd;
}
```

Operations:
- `GetAuthBasics()` - Retrieve auth users for website
- `UpdateAuthBasic()` - Create/update/delete users
- `GetPathAuthBasics()` - List path-specific auth configs
- `UpdatePathAuthBasic()` - Manage path auth

### Rewrite Rules

URL rewriting using Nginx rewrite directives [agent/app/service/website_rewrite.go:10-130]():

The system provides predefined rewrite templates for common CMSes:
- WordPress
- Laravel
- ThinkPHP
- Discuz
- And custom rewrites

Custom rewrite files stored in `/www/sites/{alias}/rewrite/{alias}.conf`

### Redirect Configuration

Manages 301/302 redirects with domain and path matching [agent/app/service/website_redirect.go:13-315]():

**Redirect Types:**
- **Domain**: Redirect entire domain to another
- **Path**: Redirect specific paths
- **Path with regex**: Pattern-based redirects

Example configuration:
```go
type RedirectConfig struct {
    Enable       bool
    Name         string
    Type         string    // "domain", "path"
    Redirect     string    // "301", "302"
    Domains      []string  // Source domains
    Path         string    // Source path
    Target       string    // Destination URL
    KeepPath     bool      // Preserve original path
    RedirectRoot bool      // Apply to root location
}
```

Sources: [agent/app/service/website_proxy.go:16-460](), [agent/app/service/website_load_balance.go:13-166](), [agent/app/service/website_anti_leech.go:11-120](), [agent/app/service/website_auth.go:11-200](), [agent/app/service/website_rewrite.go:10-130](), [agent/app/service/website_redirect.go:13-315]()

---

## Website Operation Lifecycle

### Start/Stop Operations

Websites can be started or stopped without deletion [agent/app/service/website_utils.go:964-1059]():

**Stop Website:**
```go
if operate == constant.StopWeb {
    // Remove proxy includes
    server.RemoveDirective("include", []string{proxyInclude})
    server.RemoveDirective("include", []string{rewriteInclude})
    server.RemoveDirective("include", []string{redirectInclude})
    
    // Remove application location blocks
    server.RemoveDirective("location", []string{"/"})
    
    // Point to stop page
    server.UpdateRoot("/usr/share/nginx/html/stop")
    website.Status = constant.WebStopped
}
```

**Start Website:**
```go
if operate == constant.StartWeb {
    // Restore includes
    server.UpdateDirective("include", []string{proxyInclude})
    server.UpdateDirective("include", []string{rewriteInclude})
    
    // Restore root/proxy configuration based on type
    switch website.Type {
    case constant.Deployment:
        server.UpdateRootProxy([]string{proxy})
    case constant.Static:
        server.UpdateRoot(rootIndex)
    case constant.Runtime:
        server.UpdatePHPProxy([]string{website.Proxy}, localPath)
    }
    
    website.Status = constant.WebRunning
}
```

### Log Management

Each website maintains separate access and error logs [agent/app/service/website.go:1078-1160]():

**Log Operations:**
- `GetLog`: Read log file with pagination
- `EnableLog`: Re-enable logging (writes path to nginx config)
- `DisableLog`: Disable logging (access_log off / error_log /dev/null)
- `DeleteLog`: Truncate log file

Log files located at:
- Access: `/www/sites/{alias}/log/access.log`
- Error: `/www/sites/{alias}/log/error.log`

### Batch Operations

Multiple websites can be operated simultaneously using tasks [agent/app/service/website_op.go:10-165]():

**Supported Batch Operations:**
- Start: `batchOpWebsite("start")`
- Stop: `batchOpWebsite("stop")`
- Restart: `batchOpWebsite("restart")`
- Set Group: `BatchSetGroup()`
- Set HTTPS: `BatchSetHttps()`

Each operation creates a task with subtasks for each website, enabling parallel execution and individual error handling.

Sources: [agent/app/service/website_utils.go:964-1059](), [agent/app/service/website.go:1078-1160](), [agent/app/service/website_op.go:10-165]()

---

## Data Models and Storage

### Core Database Schema

```mermaid
erDiagram
    Website ||--o{ WebsiteDomain : "has domains"
    Website ||--o| WebsiteSSL : "has SSL"
    Website }o--|| WebsiteGroup : "belongs to"
    Website ||--o| AppInstall : "links to (deployment type)"
    Website ||--o| Runtime : "uses (runtime type)"
    Website ||--o| Website : "parent (subsite type)"
    Website ||--o| DatabaseMysql : "links to DB"
    Website ||--o| DatabasePostgresql : "links to DB"
    
    Website {
        uint ID PK
        string Type
        string Alias UK
        string PrimaryDomain
        string Protocol
        string Status
        uint WebsiteGroupID FK
        uint WebsiteSSLID FK
        uint AppInstallID FK
        uint RuntimeID FK
        uint ParentWebsiteID FK
        uint DbID FK
        string DbType
        string Proxy
        string ProxyType
        string SiteDir
        string StreamPorts
        bool IPV6
        bool AccessLog
        bool ErrorLog
        bool DefaultServer
        bool Favorite
        time ExpireDate
    }
    
    WebsiteDomain {
        uint ID PK
        uint WebsiteID FK
        string Domain
        int Port
        bool SSL
    }
    
    WebsiteSSL {
        uint ID PK
        string PrimaryDomain
        string Pem
        string PrivateKey
        string Type
        string Provider
        time ExpireDate
        bool AutoRenew
        uint AcmeAccountID FK
        uint DnsAccountID FK
    }
```

### File System Structure

Each website creates a dedicated directory structure:

```
/www/
├── sites/
│   └── {alias}/                    # Website root (SiteDir)
│       ├── index/                  # Document root (SiteIndexDir)
│       │   ├── index.html          # Default index
│       │   ├── 404.html            # Error page
│       │   └── .user.ini           # PHP open_basedir (if PHP)
│       ├── log/                    # Logs (SiteLogDir)
│       │   ├── access.log
│       │   └── error.log
│       ├── ssl/                    # SSL certificates (SiteSSLDir)
│       │   ├── fullchain.pem
│       │   └── privkey.pem
│       ├── proxy/                  # Proxy configs (SiteProxyDir)
│       │   ├── root.conf
│       │   └── {name}.conf
│       ├── rewrite/                # Rewrite rules (SiteReWriteDir)
│       │   └── {alias}.conf
│       ├── redirect/               # Redirect rules (SiteRedirectDir)
│       │   └── {alias}.conf
│       └── php-pool/               # PHP-FPM socket (if local PHP)
│           └── php-fpm.sock
│
└── server/
    └── openresty/
        └── conf.d/
            ├── {alias}.conf        # Main site config (SiteConf)
            └── stream/
                └── {alias}.conf    # Stream config (StreamConf)
```

**Path Resolution Functions** [agent/app/service/path.go:16-82]():

```go
const (
    SiteDir           = "siteDir"
    SiteIndexDir      = "siteIndexDir"
    SiteLogDir        = "siteLogDir"
    SiteSSLDir        = "siteSSLDir"
    SiteProxyDir      = "siteProxyDir"
    SiteReWriteDir    = "siteRewriteDir"
    SiteRedirectDir   = "siteRedirectDir"
    SiteConf          = "siteConf"
    StreamConf        = "streamConf"
    // ... and more
)

func GetSitePath(website model.Website, pathType string) string {
    // Returns absolute path for requested path type
}
```

### WAF Integration

Web Application Firewall configuration synchronized with website changes [agent/app/service/website_utils.go:352-480]():

**WAF Directory Structure:**
```
/www/server/openresty/1pwaf/
└── data/
    ├── conf/
    │   ├── sites.json          # All websites registry
    │   └── siteConfig.json     # Default rules
    ├── rules/                  # Global rule templates
    │   ├── acl.json
    │   ├── args.json
    │   ├── cookie.json
    │   └── ...
    ├── sites/                  # Per-site configs
    │   └── {alias}/
    │       ├── config.json
    │       └── rules/
    │           ├── acl.json
    │           └── ...
    └── db/                     # Runtime data
        └── sites/
            └── {alias}/
```

**WAF Sync Operations:**
- `createWafConfig()` - Initialize WAF for new website
- `delWafConfig()` - Clean up WAF when deleting website
- `createAllWebsitesWAFConfig()` - Rebuild WAF for all websites

Sources: [agent/app/model/website.go](), [agent/app/service/path.go:16-82](), [agent/app/service/website_utils.go:327-480]()

---

## Frontend API Integration

The frontend communicates with the Website Management System through a comprehensive TypeScript API client.

### API Client Structure

```mermaid
graph LR
    subgraph "Frontend API Layer"
        WebsiteAPI["website.ts<br/>API functions"]
        Interfaces["interface/website.ts<br/>TypeScript types"]
        HTTPClient["http client<br/>Axios wrapper"]
    end
    
    subgraph "Backend Endpoints"
        CreateEndpoint["/websites<br/>POST"]
        SearchEndpoint["/websites/search<br/>POST"]
        OpEndpoint["/websites/operate<br/>POST"]
        DomainEndpoint["/websites/domains<br/>POST"]
        SSLEndpoint["/websites/ssl/*<br/>GET/POST"]
        ConfigEndpoint["/websites/config/*<br/>GET/POST"]
    end
    
    WebsiteAPI --> Interfaces
    WebsiteAPI --> HTTPClient
    
    HTTPClient --> CreateEndpoint
    HTTPClient --> SearchEndpoint
    HTTPClient --> OpEndpoint
    HTTPClient --> DomainEndpoint
    HTTPClient --> SSLEndpoint
    HTTPClient --> ConfigEndpoint
```

### Key API Functions

**Website CRUD** [frontend/src/api/modules/website.ts:9-53]():
```typescript
searchWebsites(req: Website.WebSiteSearch)
createWebsite(req: Website.WebSiteCreateReq)
updateWebsite(req: Website.WebSiteUpdateReq)
deleteWebsite(req: Website.WebSiteDel)
getWebsite(id: number)
opWebsite(req: Website.WebSiteOp)  // start/stop/restart
```

**Domain Management** [frontend/src/api/modules/website.ts:55-69]():
```typescript
listDomains(id: number)
createDomain(req: Website.DomainCreate)
updateDomain(req: Website.DomainUpdate)
deleteDomain(req: Website.DomainDelete)
```

**SSL/HTTPS** [frontend/src/api/modules/website.ts:111-153]():
```typescript
searchSSL(req: ReqPage)
createSSL(req: Website.SSLCreate)
getHTTPSConfig(id: number)
updateHTTPSConfig(req: Website.HTTPSReq)
getDnsResolve(req: Website.DNSResolveReq)  // For DNS validation
```

**Configuration** [frontend/src/api/modules/website.ts:71-77]():
```typescript
getNginxConfig(req: Website.NginxScopeReq)
updateNginxConfig(req: Website.NginxConfigReq)
updateNginxFile(req: Website.NginxUpdate)  // Direct file edit
```

**Advanced Features** [frontend/src/api/modules/website.ts:183-233]():
```typescript
// Proxy
getProxyConfig(req: Website.ProxyReq)
operateProxyConfig(req: Website.ProxyReq)
updateProxyConfigFile(req: Website.ProxyFileUpdate)

// Load Balancing
getLoadBalances(id: number)
createLoadBalance(req: Website.LoadBalanceReq)
updateLoadBalance(req: Website.LoadBalanceReq)

// Authentication
getAuthConfig(req: Website.AuthReq)
operateAuthConfig(req: Website.NginxAuthConfig)

// Redirects
getRedirectConfig(req: Website.WebsiteReq)
operateRedirectConfig(req: Website.WebsiteReq)
```

### Request/Response Types

**Create Request** [frontend/src/api/interface/website.ts:87-112]():
```typescript
interface WebSiteCreateReq {
    type: string                    // Website type
    alias: string                   // Unique identifier
    webSiteGroupId: number
    domains: SubDomain[]
    
    // App deployment
    appType: string                 // "new" | "installed"
    appInstallId: number
    
    // Runtime
    runtimeID: number
    proxyType: string
    
    // Database
    createDB?: boolean
    dbName?: string
    dbPassword?: string
    dbHost?: string
    
    // SSL
    enableSSL: boolean
    SSLID?: number
    
    // Stream
    streamPorts?: string
    algorithm: string
    servers: NginxUpstreamServer[]
}
```

**Website Response** [frontend/src/api/interface/website.ts:34-44]():
```typescript
interface WebsiteDTO extends Website {
    errorLogPath: string
    accessLogPath: string
    sitePath: string
    appName: string
    runtimeName: string
    runtimeType: string
    openBaseDir: boolean
    algorithm: string
    servers: NginxUpstreamServer[]
}
```

### Multi-Node Support

API functions support cross-node operations via `operateNode` parameter [frontend/src/api/modules/website.ts:9-11]():

```typescript
export const searchWebsites = (req: Website.WebSiteSearch, node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.post<ResPage<Website.WebsiteRes>>(`/websites/search${params}`, req);
};
```

This enables managing websites on remote agent nodes from the master node's UI.

Sources: [frontend/src/api/modules/website.ts:1-384](), [frontend/src/api/interface/website.ts:1-738]()

---

## Summary

The Website Management System provides a comprehensive abstraction layer over Nginx/OpenResty with:

- **6 website types** supporting static hosting, language runtimes, app deployments, reverse proxy, TCP/UDP load balancing, and subsites
- **Custom Nginx parser** enabling programmatic configuration manipulation with automatic validation and rollback
- **Multi-domain support** with per-domain SSL configuration
- **Automated SSL** via ACME protocol with 50+ DNS providers
- **Advanced features** including load balancing, proxy caching, CORS, authentication, anti-leech, redirects, and rewrites
- **Task-based creation** with atomic rollback on failure
- **WAF integration** for web application firewall protection
- **Multi-node operation** for distributed deployments
- **Comprehensive API** with TypeScript type safety

The system manages the complete lifecycle from creation through operation to deletion, handling all Nginx configuration, file system setup, certificate management, and runtime integration automatically.

---

