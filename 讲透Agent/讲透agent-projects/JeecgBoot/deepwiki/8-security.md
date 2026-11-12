<!-- source: DeepWiki mcp.deepwiki.com · repo jeecgboot/JeecgBoot · page 8 Security · fetched 2026-10-29 -->

# Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jeecg-boot/jeecg-boot-base-core/pom.xml](jeecg-boot/jeecg-boot-base-core/pom.xml)
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/common/util/encryption/AesEncryptUtil.java](jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/common/util/encryption/AesEncryptUtil.java)
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/JeecgBaseConfig.java](jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/JeecgBaseConfig.java)
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java](jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java)
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java](jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java)
- [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/pom.xml](jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/pom.xml)
- [jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/config/init/CodeTemplateInitListener.java](jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/config/init/CodeTemplateInitListener.java)
- [jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/LoginController.java](jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/LoginController.java)
- [jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/SysRoleIndexController.java](jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/SysRoleIndexController.java)
- [jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysRoleIndex.java](jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysRoleIndex.java)
- [jeecg-boot/pom.xml](jeecg-boot/pom.xml)

</details>



## Purpose and Scope

This document describes JeecgBoot's comprehensive multi-layered security architecture, covering authentication mechanisms (JWT, Shiro, OAuth, CAS SSO), authorization models (RBAC with data permissions), and data protection strategies (encryption, SQL injection prevention). For AI-specific security features like MCP authentication, see [AI Platform (AIGC)](#3). For deployment security configurations, see [Production Deployment Best Practices](#9.3).

---

## Overview

JeecgBoot implements a defense-in-depth security model with four primary layers:

```mermaid
graph TB
    Request["HTTP Request"]
    
    subgraph Layer1 ["Layer 1: Network & Transport"]
        ShiroFilter["ShiroFilterFactoryBean<br/>Filter Chain"]
        JwtFilter["JwtFilter<br/>JWT Token Validation"]
        ExcludedURLs["Excluded URL Patterns<br/>/sys/login, /druid/**, etc"]
    end
    
    subgraph Layer2 ["Layer 2: Authentication"]
        TokenValidation["Token Validation<br/>JwtUtil.verify()"]
        ShiroRealm["ShiroRealm<br/>doGetAuthenticationInfo()"]
        ThirdPartyAuth["Third-party OAuth<br/>JustAuth"]
        CASAuth["CAS SSO<br/>/sys/cas/client"]
        AKSKAuth["AK/SK OpenAPI<br/>/openapi/call/**"]
    end
    
    subgraph Layer3 ["Layer 3: Authorization"]
        PermissionCheck["Permission Check<br/>@RequiresPermissions"]
        RBACModel["RBAC Model<br/>User-Role-Menu"]
        DataPermission["Data Permission Engine<br/>SysPermissionDataRule"]
        ButtonPermission["Button-level Control<br/>perms in Menu"]
    end
    
    subgraph Layer4 ["Layer 4: Data Protection"]
        AESEncrypt["AES Encryption<br/>AesEncryptUtil"]
        SQLInjection["SQL Injection Prevention<br/>DictTableWhiteListHandler"]
        FileUpload["File Upload Validation<br/>Size/Type Checks"]
    end
    
    Response["HTTP Response"]
    
    Request --> ShiroFilter
    ShiroFilter --> ExcludedURLs
    ShiroFilter --> JwtFilter
    
    ExcludedURLs -.bypass.-> Response
    
    JwtFilter --> TokenValidation
    TokenValidation --> ShiroRealm
    TokenValidation --> ThirdPartyAuth
    TokenValidation --> CASAuth
    TokenValidation --> AKSKAuth
    
    ShiroRealm --> PermissionCheck
    PermissionCheck --> RBACModel
    PermissionCheck --> DataPermission
    PermissionCheck --> ButtonPermission
    
    DataPermission --> AESEncrypt
    DataPermission --> SQLInjection
    DataPermission --> FileUpload
    
    SQLInjection --> Response
```

**Sources:** [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java:1-400]()

---

## Authentication System

### JWT and Shiro Integration

JeecgBoot uses **Apache Shiro 3.0.0** [jeecg-boot/pom.xml:76]() with **JWT tokens** for stateless authentication. The integration is configured in `ShiroConfig` [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java:47]() with Redis-backed caching.

#### Key Components

| Component | Class/File | Purpose |
|-----------|-----------|---------|
| Security Manager | `DefaultWebSecurityManager` | Core security coordinator [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java:14]() |
| JWT Filter | `JwtFilter` | Validates JWT tokens on each request [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/filters/JwtFilter.java:1-100]() |
| Shiro Realm | `ShiroRealm` | Authenticates users and loads permissions [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java:41]() |
| Cache Manager | `RedisCacheManager` | Caches user permissions in Redis [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java:15]() |

```mermaid
sequenceDiagram
    participant Client
    participant JwtFilter
    participant ShiroRealm
    participant Redis
    participant Database
    
    Client->>JwtFilter: Request with X-ACCESS-TOKEN
    JwtFilter->>JwtFilter: Extract token from header
    
    alt Token Valid
        JwtFilter->>ShiroRealm: doGetAuthenticationInfo(token)
        ShiroRealm->>ShiroRealm: checkUserTokenIsEffect(token)
        ShiroRealm->>Redis: Check cached user
        
        alt Cache Hit
            Redis-->>ShiroRealm: Return cached LoginUser
        else Cache Miss
            ShiroRealm->>Database: Query user via CommonAPI
            Database-->>ShiroRealm: User entity
            ShiroRealm->>Redis: Cache LoginUser
        end
        
        ShiroRealm-->>JwtFilter: AuthenticationInfo
        JwtFilter->>ShiroRealm: doGetAuthorizationInfo()
        ShiroRealm->>Redis: Get cached permissions (roles/auths)
        ShiroRealm-->>JwtFilter: AuthorizationInfo
        JwtFilter-->>Client: Request proceeds
    else Token Invalid
        JwtFilter-->>Client: 401 Unauthorized
    end
```

**Token Generation:**
- Login endpoint: `/sys/login` (excluded from authentication) [jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/LoginController.java:84]()
- Token secret: Configured in `EncryptedString.key`
- Token includes: username, timestamp, signature [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java:126]()

For details, see [Authentication System](#8.1).

**Sources:** 
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java:67-200]()
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java:99-147]()

---

### Shiro Filter Chain Configuration

The `ShiroFilterFactoryBean` defines a comprehensive filter chain with excluded URL patterns for public resources and authentication endpoints [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java:68]().

#### Excluded URL Patterns

```mermaid
graph LR
    subgraph PublicAccess ["Public Access - anon filter"]
        Login["/sys/login<br/>/sys/logout<br/>/sys/thirdLogin/**"]
        Static["/**.js, /**.css<br/>/**.png, /druid/**"]
        Swagger["/doc.html<br/>/swagger**/**<br/>/v3/**"]
        JimuReport["/jmreport/**<br/>/drag/view"]
    end
    
    subgraph Protected ["Protected - jwt filter"]
        API["/** <br/>All other paths"]
    end
    
    Request["HTTP Request"]
    
    Request --> Login
    Request --> Static
    Request --> Swagger
    Request --> JimuReport
    Request --> API
    
    Login -.bypass.-> Response["Response"]
    Static -.bypass.-> Response
    Swagger -.bypass.-> Response
    JimuReport -.bypass.-> Response
    
    API --> JwtValidation["JWT Token Validation"]
    JwtValidation --> Response
```

**Sources:** 
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java:85-150]()

---

## Authorization & Permissions

### RBAC Model

JeecgBoot implements a standard **Role-Based Access Control (RBAC)** model. Permissions are verified during `doGetAuthorizationInfo` [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java:66]().

**Permission Components:**
- **User-Role Hierarchy:** Users are assigned roles [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java:78]().
- **Role-Menu/Button Permissions:** Roles are granted string-based permissions [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java:83]().
- **Role-Based Routing:** Users can be assigned dynamic homepages based on roles via `SysRoleIndex` [jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/entity/SysRoleIndex.java:30]().

For details, see [Authorization & Permissions](#8.2).

---

### Data Permissions & Row-Level Security

JeecgBoot provides fine-grained data permissions through dynamic SQL rule injection. Rules are defined in `SysPermissionDataRuleModel` and processed by the `QueryGenerator` to filter result sets based on user context (e.g., department, user ID).

For details, see [Data Permissions & Row-Level Security](#8.3).

---

## Data Protection

### Password Encryption (AES Dual-Mode)

JeecgBoot implements **backward-compatible AES encryption** supporting both legacy `NoPadding` and modern `PKCS5Padding` modes [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/common/util/encryption/AesEncryptUtil.java:15]().

```mermaid
graph TB
    Input["Encrypted Password Input"]
    
    ResolvePassword["AesEncryptUtil.resolvePassword()"]
    
    subgraph DecryptionStrategy ["Decryption Strategy"]
        TryPKCS5["Try PKCS5Padding<br/>AES/CBC/PKCS5Padding"]
        TryNoPadding["Fallback NoPadding<br/>AES/CBC/NoPadding"]
        PlainText["Return Raw Input<br/>if both fail"]
    end
    
    Clean["Clean Control Characters<br/>regex: p{Cntrl}"]
    Output["Decrypted Password"]
    
    Input --> ResolvePassword
    ResolvePassword --> TryPKCS5
    
    TryPKCS5 -->|Success| Clean
    TryPKCS5 -->|Exception| TryNoPadding
    
    TryNoPadding -->|Success| Clean
    TryNoPadding -->|Exception| PlainText
    
    PlainText --> Output
    Clean --> Output
```

**Sources:** 
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/common/util/encryption/AesEncryptUtil.java:42-64]()

For details, see [Encryption & Data Protection](#8.4).

---

### SQL Injection Prevention

The system utilizes `DictTableWhiteListHandler` to prevent SQL injection by enforcing a whitelist for dynamic table and field queries. This is especially critical for low-code features where table names are passed as parameters.

For details, see [SQL Injection Prevention](#8.5).

---

### File Upload Security

File uploads are secured through size limits, type restrictions, and configurable storage backends (Local, MinIO, OSS). Upload configurations are managed via `JeecgBaseConfig` [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/JeecgBaseConfig.java:35]().

For details, see [File Upload Security](#8.6).

---

**Page Sources:**
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroConfig.java:1-400]()
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/shiro/ShiroRealm.java:1-180]()
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/common/util/encryption/AesEncryptUtil.java:1-107]()
- [jeecg-boot/jeecg-boot-base-core/src/main/java/org/jeecg/config/JeecgBaseConfig.java:1-205]()
- [jeecg-boot/jeecg-module-system/jeecg-system-biz/src/main/java/org/jeecg/modules/system/controller/LoginController.java:84-135]()
- [jeecg-boot/pom.xml:75-78]()

---

