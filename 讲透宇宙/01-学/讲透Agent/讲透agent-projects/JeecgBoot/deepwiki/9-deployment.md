<!-- source: DeepWiki mcp.deepwiki.com · repo jeecgboot/JeecgBoot · page 9 Deployment · fetched 2026-10-29 -->

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker-compose-cloud.yml](docker-compose-cloud.yml)
- [docker-compose.yml](docker-compose.yml)
- [jeecg-boot/docker-compose.yml](jeecg-boot/docker-compose.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/Dockerfile](jeecg-boot/jeecg-module-system/jeecg-system-start/Dockerfile)
- [jeecg-boot/jeecg-server-cloud/docker-compose.yml](jeecg-boot/jeecg-server-cloud/docker-compose.yml)
- [jeecg-boot/jeecg-server-cloud/jeecg-cloud-gateway/Dockerfile](jeecg-boot/jeecg-server-cloud/jeecg-cloud-gateway/Dockerfile)
- [jeecg-boot/jeecg-server-cloud/jeecg-cloud-nacos/Dockerfile](jeecg-boot/jeecg-server-cloud/jeecg-cloud-nacos/Dockerfile)
- [jeecg-boot/jeecg-server-cloud/jeecg-demo-cloud-start/Dockerfile](jeecg-boot/jeecg-server-cloud/jeecg-demo-cloud-start/Dockerfile)
- [jeecg-boot/jeecg-server-cloud/jeecg-system-cloud-start/Dockerfile](jeecg-boot/jeecg-server-cloud/jeecg-system-cloud-start/Dockerfile)
- [jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/Dockerfile](jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/Dockerfile)
- [jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/pom.xml](jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/pom.xml)
- [jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-xxljob/Dockerfile](jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-xxljob/Dockerfile)
- [jeecgboot-vue3/.env.docker](jeecgboot-vue3/.env.docker)
- [jeecgboot-vue3/.env.dockercloud](jeecgboot-vue3/.env.dockercloud)
- [jeecgboot-vue3/Dockerfile.cloud](jeecgboot-vue3/Dockerfile.cloud)

</details>



## Purpose and Scope

This page documents the deployment strategies and configurations for JeecgBoot applications. It covers Docker-based deployment for both monolithic and microservices architectures, container configuration, environment setup, and production deployment best practices.

For information about the microservices architecture itself, see [Microservices Architecture](#2.4). For security hardening in production environments, see [Production Deployment Best Practices](#9.3). For initial environment setup during development, see [System Requirements & Environment Setup](#1.3).

---

## Deployment Architecture Overview

JeecgBoot supports two primary deployment modes:

| Deployment Mode | Use Case | Complexity | Components |
|----------------|----------|------------|------------|
| **Monolithic** | Development, small-scale production | Low | Single backend JAR, MySQL, Redis, pgvector, Nginx |
| **Microservices Cloud** | Production, distributed systems | High | Nacos, Gateway, System Service, Demo Service, Sentinel, XXL-Job, MySQL, Redis, pgvector, Nginx |

```mermaid
graph TB
    subgraph "Monolithic Deployment"
        M_Client["Web Client<br/>Port 80"]
        M_Backend["jeecg-boot-system<br/>Port 8080<br/>jeecg-system-start-3.9.3.jar"]
        M_MySQL["jeecg-boot-mysql<br/>Port 13306"]
        M_Redis["jeecg-boot-redis"]
        M_PG["jeecg-boot-pgvector<br/>Port 5432"]
        
        M_Client -->|"nginx proxy"| M_Backend
        M_Backend --> M_MySQL
        M_Backend --> M_Redis
        M_Backend --> M_PG
    end
    
    subgraph "Microservices Cloud Deployment"
        C_Client["Web Client<br/>Port 80"]
        C_Gateway["jeecg-boot-gateway<br/>Port 9999<br/>jeecg-cloud-gateway-3.9.3.jar"]
        C_Nacos["jeecg-boot-nacos<br/>Port 8848<br/>jeecg-cloud-nacos-3.9.3.jar"]
        C_System["jeecg-system-start<br/>jeecg-system-cloud-start-3.9.3.jar"]
        C_Demo["jeecg-demo-start<br/>jeecg-demo-cloud-start-3.9.3.jar"]
        C_Sentinel["jeecg-boot-sentinel<br/>Port 9000<br/>jeecg-cloud-sentinel-3.9.3.jar"]
        C_XXLJob["jeecg-boot-xxljob<br/>Port 9080<br/>jeecg-cloud-xxljob-3.9.3.jar"]
        C_MySQL["jeecg-boot-mysql<br/>Port 13306"]
        C_Redis["jeecg-boot-redis"]
        C_PG["jeecg-boot-pgvector<br/>Port 5432"]
        
        C_Client -->|"nginx proxy"| C_Gateway
        C_Gateway --> C_Nacos
        C_System --> C_Nacos
        C_Demo --> C_Nacos
        C_Gateway --> C_System
        C_Gateway --> C_Demo
        C_System --> C_MySQL
        C_System --> C_Redis
        C_System --> C_PG
        C_Sentinel --> C_Nacos
        C_XXLJob --> C_MySQL
    end
```

**Sources:** [docker-compose.yml:1-77](), [docker-compose-cloud.yml:1-171]()

---

## Docker Deployment

### Monolithic Deployment

The monolithic deployment uses `docker-compose.yml` to orchestrate a single backend service with supporting infrastructure.

```mermaid
graph LR
    DC["docker-compose.yml"]
    
    DC -->|"builds"| MySQL_Build["jeecg-boot/db<br/>Dockerfile + SQL"]
    DC -->|"builds"| System_Build["jeecg-module-system/jeecg-system-start<br/>Dockerfile"]
    DC -->|"builds"| Vue_Build["jeecgboot-vue3<br/>Dockerfile"]
    DC -->|"pulls image"| Redis_Image["registry.cn-hangzhou.aliyuncs.com/jeecgdocker/redis:5.0"]
    DC -->|"pulls image"| PG_Image["registry.cn-hangzhou.aliyuncs.com/jeecgdocker/pgvector"]
    
    MySQL_Build -->|"creates"| MySQL_Container["jeecg-boot-mysql:13306"]
    System_Build -->|"creates"| System_Container["jeecg-boot-system:8080"]
    Vue_Build -->|"creates"| Vue_Container["jeecgboot-vue3-nginx:80"]
    Redis_Image -->|"creates"| Redis_Container["jeecg-boot-redis:6379"]
    PG_Image -->|"creates"| PG_Container["jeecg-boot-pgvector:5432"]
```

#### Container Definitions

**1. jeecg-boot-mysql**

Configuration for the MySQL database container:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `container_name` | `jeecg-boot-mysql` | Container identifier |
| `image` | `jeecg-boot-mysql` | Custom built image |
| `build.context` | `./jeecg-boot/db` | Database initialization scripts [docker-compose.yml:4-5]() |
| `ports` | `13306:3306` | External port 13306 maps to internal 3306 [docker-compose.yml:21]() |
| `environment.MYSQL_ROOT_PASSWORD` | `root` | Root user password [docker-compose.yml:7]() |
| `character-set-server` | `utf8mb4` | Character encoding [docker-compose.yml:14]() |
| `max_allowed_packet` | `128M` | Maximum packet size [docker-compose.yml:18]() |

**2. jeecg-boot-redis**

Redis 5.0 container for caching and session management:

| Parameter | Value |
|-----------|-------|
| `container_name` | `jeecg-boot-redis` |
| `image` | `registry.cn-hangzhou.aliyuncs.com/jeecgdocker/redis:5.0` [docker-compose.yml:26]() |
| `hostname` | `jeecg-boot-redis` |

**3. jeecg-boot-pgvector**

PostgreSQL with pgvector extension for AI embeddings:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `container_name` | `jeecg-boot-pgvector` | Container identifier |
| `image` | `registry.cn-hangzhou.aliyuncs.com/jeecgdocker/pgvector` [docker-compose.yml:62]() |
| `environment.POSTGRES_DB` | `vector_db` | Default database name [docker-compose.yml:67]() |
| `environment.POSTGRES_USER` | `postgres` | Database user |
| `environment.POSTGRES_PASSWORD` | `postgres` | Database password |

**4. jeecg-boot-system**

Main application backend container:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `container_name` | `jeecg-boot-system` | Container identifier |
| `build.context` | `./jeecg-boot/jeecg-module-system/jeecg-system-start` [docker-compose.yml:37]() | Application build context |
| `ports` | `8080:8080` | Backend API port [docker-compose.yml:46]() |
| `depends_on` | `jeecg-boot-mysql`, `jeecg-boot-redis` [docker-compose.yml:39-41]() | Startup order dependencies |

The Dockerfile at [jeecg-boot/jeecg-module-system/jeecg-system-start/Dockerfile:1-29]() uses Java 17-anolis and includes a 60-second startup delay to ensure dependencies are ready:

```dockerfile
CMD sleep 60 && exec java -Djava.security.egd=file:/dev/./urandom -jar jeecg-system-start-3.9.3.jar
```

**5. jeecg-vue**

Frontend Nginx container:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `container_name` | `jeecgboot-vue3-nginx` | Container identifier |
| `build.context` | `./jeecgboot-vue3` [docker-compose.yml:51]() | Frontend build context |
| `ports` | `80:80` | Web server port [docker-compose.yml:59]() |
| `depends_on` | `jeecg-boot-system` | Ensures backend is running |

**Sources:** [docker-compose.yml:1-77](), [jeecg-boot/jeecg-module-system/jeecg-system-start/Dockerfile:1-29]()

---

### Microservices Cloud Deployment

The microservices deployment uses `docker-compose-cloud.yml` to orchestrate a distributed system with service discovery, API gateway, and monitoring.

```mermaid
graph TB
    subgraph "Infrastructure Layer"
        MySQL["jeecg-boot-mysql<br/>Port 13306<br/>context: ./jeecg-boot/db"]
        Redis["jeecg-boot-redis<br/>image: redis:5.0"]
        PG["jeecg-boot-pgvector<br/>Port 5432<br/>image: pgvector"]
    end
    
    subgraph "Service Registry & Config"
        Nacos["jeecg-boot-nacos<br/>Port 8848<br/>context: jeecg-cloud-nacos<br/>jar: jeecg-cloud-nacos-3.9.3.jar"]
    end
    
    subgraph "Business Services"
        System["jeecg-system-cloud-start<br/>context: jeecg-system-cloud-start<br/>jar: jeecg-system-cloud-start-3.9.3.jar"]
        Demo["jeecg-demo-start<br/>context: jeecg-demo-cloud-start<br/>jar: jeecg-demo-cloud-start-3.9.3.jar"]
    end
    
    subgraph "Gateway & Management"
        Gateway["jeecg-boot-gateway<br/>Port 9999<br/>context: jeecg-cloud-gateway<br/>jar: jeecg-cloud-gateway-3.9.3.jar"]
        Sentinel["jeecg-boot-sentinel<br/>Port 9000<br/>context: jeecg-cloud-sentinel<br/>jar: jeecg-cloud-sentinel-3.9.3.jar"]
        XXLJob["jeecg-boot-xxljob<br/>Port 9080<br/>context: jeecg-cloud-xxljob<br/>jar: jeecg-cloud-xxljob-3.9.3.jar"]
    end
    
    subgraph "Frontend"
        Vue["jeecgboot-vue3-nginx-cloud<br/>Port 80<br/>Dockerfile.cloud"]
    end
    
    Nacos -.->|"depends_on"| MySQL
    System -.->|"depends_on"| Nacos
    Demo -.->|"depends_on"| Nacos
    Gateway -.->|"depends_on"| Nacos
    Gateway -.->|"depends_on"| System
    Sentinel -.->|"depends_on"| Nacos
    Sentinel -.->|"depends_on"| System
    Sentinel -.->|"depends_on"| Demo
    Sentinel -.->|"depends_on"| Gateway
```

#### Service Startup Sequence and Dependencies

The `depends_on` directives and custom `command` scripts in [docker-compose-cloud.yml:1-171]() define the following startup logic:

1. **Infrastructure**:
   - `jeecg-boot-mysql`
   - `jeecg-boot-redis`
   - `jeecg-boot-pgvector`

2. **Service Registry**:
   - `jeecg-boot-nacos`: Builds from `./jeecg-boot/jeecg-server-cloud/jeecg-cloud-nacos` [docker-compose-cloud.yml:48](). Waits for MySQL [docker-compose-cloud.yml:53-54]().

3. **Business Services**:
   - `jeecg-boot-system`: Depends on Nacos [docker-compose-cloud.yml:60-61](). Waits 60s via [jeecg-boot/jeecg-server-cloud/jeecg-system-cloud-start/Dockerfile:25]().
   - `jeecg-boot-demo`: Depends on Nacos [docker-compose-cloud.yml:74-75](). Waits 60s via [jeecg-boot/jeecg-server-cloud/jeecg-demo-cloud-start/Dockerfile:25]().

4. **Gateway Layer**:
   - `jeecg-boot-gateway`: Actively polls Nacos until `jeecg-system` is healthy before starting the Java process [docker-compose-cloud.yml:100-109]().

5. **Monitoring Services**:
   - `jeecg-boot-xxljob`: Distributed task scheduler on port 9080 [docker-compose-cloud.yml:35-43]().
   - `jeecg-boot-sentinel`: (Optional/Commented) Dashboard for flow control [docker-compose-cloud.yml:125-140]().

#### Container Configuration Details

**Nacos Service Registry**
Uses Java 21-anolis [jeecg-boot/jeecg-server-cloud/jeecg-cloud-nacos/Dockerfile:1](). Includes a 30s delay [jeecg-boot/jeecg-server-cloud/jeecg-cloud-nacos/Dockerfile:25]().

**Gateway Service**
Implements a health check loop in the container `command` to ensure it only starts after the System module is registered in Nacos [docker-compose-cloud.yml:105-107]().

**Sentinel Dashboard**
The Maven project at [jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/pom.xml:1-127]() includes Sentinel Dashboard v1.8.10 and Nacos data source integration [jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/pom.xml:22-32]().

**Sources:** [docker-compose-cloud.yml:1-171](), [jeecg-boot/jeecg-server-cloud/jeecg-cloud-nacos/Dockerfile:1-25](), [jeecg-boot/jeecg-server-cloud/jeecg-cloud-gateway/Dockerfile:1-25](), [jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/pom.xml:1-127]()

---

## Frontend Container Configuration

### Monolithic Mode Frontend
Uses `Dockerfile` with backend proxy to `jeecg-boot-system:8080`. Environment variables are sourced from `.env.docker`.

### Microservices Mode Frontend
Uses `Dockerfile.cloud` [docker-compose-cloud.yml:145]() and environment variables from `.env.dockercloud`.

**Nginx Proxy Configuration (Cloud)**:
The gateway acts as the single entry point for all API calls. The frontend container maps port 80 [docker-compose-cloud.yml:153]() and routes traffic to `jeecg-boot-gateway:9999`.

**Sources:** [docker-compose-cloud.yml:142-154](), [jeecgboot-vue3/Dockerfile.cloud:1-25]()

---

## Environment-Specific Build Profiles

Microservices utilize Maven profiles to manage environment-specific configurations. Example from Sentinel [jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/pom.xml:77-125]():

| Profile ID | Nacos Server | Namespace |
|------------|--------------|-----------|
| `dev` | `jeecg-boot-nacos:8848` | (Empty) |
| `test` | `jeecg-boot-nacos:8848` | (Empty) |
| `docker` | `jeecg-boot-nacos:8848` | (Empty) |
| `prod` | `jeecg-boot-nacos:8848` | (Empty) |

These profiles define `${config.server-addr}` and other properties used during the build process to target specific environments.

**Sources:** [jeecg-boot/jeecg-server-cloud/jeecg-visual/jeecg-cloud-sentinel/pom.xml:77-125]()

---

## Service Ports Reference

### Microservices Cloud Mode

| Service | Container Name | Port | Build Context |
|---------|----------------|------|---------------|
| Nacos | `jeecg-boot-nacos` | 8848, 18080 | `jeecg-cloud-nacos` |
| Gateway | `jeecg-boot-gateway` | 9999 | `jeecg-cloud-gateway` |
| System | `jeecg-system-cloud-start` | 7001 | `jeecg-system-cloud-start` |
| Demo | `jeecg-demo-start` | 7002 | `jeecg-demo-cloud-start` |
| XXL-Job | `jeecg-boot-xxljob` | 9080 | `jeecg-cloud-xxljob` |
| MySQL | `jeecg-boot-mysql` | 13306 | `../db` |
| Frontend | `jeecgboot-vue3-nginx-cloud`| 80 | `jeecgboot-vue3` |

**Sources:** [docker-compose-cloud.yml:1-171](), [jeecg-boot/jeecg-server-cloud/docker-compose.yml:1-150]()

---

## Production Deployment Considerations

For production deployments, see the following child pages for detailed technical instructions:

- [Docker Deployment](#9.1) — Detailed orchestration for both architectures.
- [Environment Configuration](#9.2) — Managing `application.yml` and Nacos profiles.
- [Production Deployment Best Practices](#9.3) — Security hardening and Swagger protection.
- [Server Configuration](#9.4) — Tuning the Undertow server and JVM parameters.

---

