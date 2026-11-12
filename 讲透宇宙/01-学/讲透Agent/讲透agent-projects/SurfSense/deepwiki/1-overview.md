<!-- source: DeepWiki mcp.deepwiki.com · repo MODSetter/SurfSense · page 1 Overview · fetched 2026-10-29 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.es.md](README.es.md)
- [README.hi.md](README.hi.md)
- [README.md](README.md)
- [README.pt-BR.md](README.pt-BR.md)
- [README.zh-CN.md](README.zh-CN.md)
- [VERSION](VERSION)
- [surfsense_backend/app/services/auto_model_pin_service.py](surfsense_backend/app/services/auto_model_pin_service.py)
- [surfsense_backend/pyproject.toml](surfsense_backend/pyproject.toml)
- [surfsense_backend/tests/unit/services/test_auto_model_pin_service.py](surfsense_backend/tests/unit/services/test_auto_model_pin_service.py)
- [surfsense_backend/uv.lock](surfsense_backend/uv.lock)
- [surfsense_browser_extension/package.json](surfsense_browser_extension/package.json)
- [surfsense_desktop/package.json](surfsense_desktop/package.json)
- [surfsense_mcp/README.md](surfsense_mcp/README.md)
- [surfsense_web/app/(home)/mcp-server/page.tsx](surfsense_web/app/(home)/mcp-server/page.tsx)
- [surfsense_web/app/docs/layout.tsx](surfsense_web/app/docs/layout.tsx)
- [surfsense_web/app/globals.css](surfsense_web/app/globals.css)
- [surfsense_web/app/layout.config.tsx](surfsense_web/app/layout.config.tsx)
- [surfsense_web/app/layout.tsx](surfsense_web/app/layout.tsx)
- [surfsense_web/changelog/content/2026-07-05.mdx](surfsense_web/changelog/content/2026-07-05.mdx)
- [surfsense_web/components/assistant-ui/image.tsx](surfsense_web/components/assistant-ui/image.tsx)
- [surfsense_web/components/homepage/github-stars-badge.tsx](surfsense_web/components/homepage/github-stars-badge.tsx)
- [surfsense_web/components/homepage/hero-section.tsx](surfsense_web/components/homepage/hero-section.tsx)
- [surfsense_web/components/homepage/persona-paths.tsx](surfsense_web/components/homepage/persona-paths.tsx)
- [surfsense_web/components/homepage/use-cases-grid.tsx](surfsense_web/components/homepage/use-cases-grid.tsx)
- [surfsense_web/components/markdown-viewer.tsx](surfsense_web/components/markdown-viewer.tsx)
- [surfsense_web/components/pricing/pricing-section.tsx](surfsense_web/components/pricing/pricing-section.tsx)
- [surfsense_web/components/seo/json-ld.tsx](surfsense_web/components/seo/json-ld.tsx)
- [surfsense_web/components/ui/expanded-gif-overlay.tsx](surfsense_web/components/ui/expanded-gif-overlay.tsx)
- [surfsense_web/components/ui/hero-carousel.tsx](surfsense_web/components/ui/hero-carousel.tsx)
- [surfsense_web/content/docs/connectors/index.mdx](surfsense_web/content/docs/connectors/index.mdx)
- [surfsense_web/content/docs/connectors/native/amazon.mdx](surfsense_web/content/docs/connectors/native/amazon.mdx)
- [surfsense_web/content/docs/connectors/native/indeed.mdx](surfsense_web/content/docs/connectors/native/indeed.mdx)
- [surfsense_web/content/docs/connectors/native/index.mdx](surfsense_web/content/docs/connectors/native/index.mdx)
- [surfsense_web/content/docs/connectors/native/instagram.mdx](surfsense_web/content/docs/connectors/native/instagram.mdx)
- [surfsense_web/content/docs/connectors/native/meta.json](surfsense_web/content/docs/connectors/native/meta.json)
- [surfsense_web/content/docs/connectors/native/walmart.mdx](surfsense_web/content/docs/connectors/native/walmart.mdx)
- [surfsense_web/content/docs/how-to/mcp-server.mdx](surfsense_web/content/docs/how-to/mcp-server.mdx)
- [surfsense_web/lib/chat/example-prompts.ts](surfsense_web/lib/chat/example-prompts.ts)
- [surfsense_web/package.json](surfsense_web/package.json)
- [surfsense_web/pnpm-lock.yaml](surfsense_web/pnpm-lock.yaml)
- [surfsense_web/public/announcements/competitive-intelligence.png](surfsense_web/public/announcements/competitive-intelligence.png)
- [surfsense_web/public/homepage/hero_tutorial/video_gen_gif.gif](surfsense_web/public/homepage/hero_tutorial/video_gen_gif.gif)
- [surfsense_web/public/homepage/hero_tutorial/video_gen_surf.mp4](surfsense_web/public/homepage/hero_tutorial/video_gen_surf.mp4)

</details>



SurfSense is an open-source, self-hostable AI research and knowledge management system that connects large language models (LLMs) to internal knowledge sources and the live web. It provides real-time search, document chat with citations, team collaboration, and automated research capabilities. Originally built as a NotebookLM alternative, it has evolved into an agentic platform that researches the live web using structured data from platforms like Reddit, YouTube, and Amazon via a unified REST API or MCP server. [README.md:23-32]()

## System Purpose

SurfSense enables organizations and individuals to:

- **Connect LLMs to Knowledge**: Integrate 100+ LLM models with 28+ data connectors (Google Drive, Slack, Notion, GitHub, etc.). [README.md:67](), [surfsense_backend/pyproject.toml:72-73]()
- **Live Web Research**: Research the live web with structured data from Reddit, YouTube, Instagram, TikTok, Amazon, Walmart, Google Maps, Google Search, and Indeed. [README.md:53-66]()
- **Intelligent Search**: Hybrid search combining semantic vector search (pgvector) and full-text search with RRF fusion and reranking. [surfsense_backend/pyproject.toml:26-29]()
- **Conversational Knowledge Base**: Chat with documents using RAG (Retrieval-Augmented Generation) with transparent source attribution via citations. [README.md:25-26]()
- **Agentic Workflows**: Use the built-in LangGraph-based agent or expose tools to external agents (Claude, Cursor) via the **Model Context Protocol (MCP)**. [README.md:49-50](), [surfsense_backend/pyproject.toml:51](), [surfsense_backend/pyproject.toml:68]()
- **Content Generation**: Generate AI-powered podcasts, reports, and presentations from findings. [README.md:144-150]()

**Sources**: [README.md:23-66](), [README.md:132-161](), [surfsense_backend/pyproject.toml:1-90]()

## Three-Tier Architecture

SurfSense implements a three-tier architecture with a FastAPI backend, a Next.js frontend, and a PostgreSQL/Redis data layer.

Title: "SurfSense 3-Tier System Architecture"
```mermaid
graph TB
    subgraph "ClientLayer" ["Client Layer"]
        "BrowserExt" ["Browser Extension<br/>surfsense_browser_extension/"]
        "WebApp" ["Next.js Web Application<br/>surfsense_web/"]
        "DesktopApp" ["Electron Desktop App<br/>surfsense_desktop/"]
    end
    
    subgraph "ApplicationLayer" ["Application Layer"]
        "FastAPI" ["FastAPI Backend<br/>surfsense_backend/app/main.py"]
        "CeleryWorker" ["Celery Workers<br/>celery_worker.py"]
        "ZeroCache" ["Zero-Cache<br/>Real-time Data Sync"]
    end
    
    subgraph "DataLayer" ["Data Layer"]
        "PostgreSQL" ["PostgreSQL + pgvector<br/>DATABASE_URL<br/>Vector & Text Search"]
        "Redis" ["Redis<br/>REDIS_URL<br/>Task Queue & Broker"]
    end
    
    subgraph "ExternalServices" ["External & Proprietary Services"]
        "LLMs" ["LLM Providers<br/>LiteLLM Gateway"]
        "Scrapers" ["Native Scrapers<br/>Reddit, TikTok, etc."]
        "ETL" ["ETL Services<br/>Docling, Unstructured"]
        "MCP" ["MCP Server<br/>surfsense_mcp/"]
    end
    
    "BrowserExt" -->|"REST API"| "FastAPI"
    "WebApp" -->|"HTTP/SSE"| "FastAPI"
    "WebApp" <-->|"Sync"| "ZeroCache"
    "DesktopApp" --> "WebApp"
    
    "FastAPI" --> "PostgreSQL"
    "FastAPI" --> "Redis"
    "FastAPI" --> "LLMs"
    "FastAPI" --> "Scrapers"
    
    "CeleryWorker" --> "Redis"
    "CeleryWorker" --> "PostgreSQL"
    "CeleryWorker" --> "ETL"
    
    "ZeroCache" <--> "PostgreSQL"
    "FastAPI" --> "MCP"
```

**Sources**: [README.md:248-318](), [surfsense_backend/pyproject.toml:1-89](), [surfsense_web/package.json:1-160](), [surfsense_desktop/package.json:1-47]()

## Component-to-Code Mapping

This section maps high-level system logic to specific code entities and directory structures.

Title: "SurfSense Code Entity Mapping"
```mermaid
graph TB
    subgraph "BackendCode" ["Backend (surfsense_backend)"]
        "APIRouter" ["app/routes/__init__.py<br/>Endpoint Registration"]
        "Models" ["app/db.py<br/>SQLAlchemy Models"]
        "ScraperLayer" ["app/capabilities/<br/>reddit, tiktok, youtube"]
        "AgentCore" ["app/agents/new_chat/agent.py<br/>LangGraph State Machine"]
    end
    
    subgraph "FrontendCode" ["Frontend (surfsense_web)"]
        "Layout" ["app/layout.tsx<br/>Providers & Root Shell"]
        "HeroSection" ["components/homepage/hero-section.tsx<br/>Interactive Demo UI"]
        "PricingSection" ["components/pricing/pricing-section.tsx<br/>Plans & FAQ"]
    end
    
    subgraph "DesktopCode" ["Desktop (surfsense_desktop)"]
        "MainProcess" ["dist/main.js<br/>Electron Entry"]
    end

    "APIRouter" --> "AgentCore"
    "APIRouter" --> "ScraperLayer"
    "AgentCore" --> "Models"
    "Layout" --> "HeroSection"
    "MainProcess" --> "Layout"
```

**Sources**: [surfsense_backend/app/routes/__init__.py:1-140](), [surfsense_web/app/layout.tsx:1-158](), [surfsense_web/components/homepage/hero-section.tsx:1-222](), [surfsense_desktop/package.json:1-6]()

## Core Subsystems

### 1. Advanced RAG & Search
- **Hybrid Search**: Combines semantic vector search (via `pgvector`) with full-text search, fused via Reciprocal Rank Fusion (RRF). [surfsense_backend/pyproject.toml:26-29]()
- **Hierarchical Indexing**: Uses a two-tier RAG approach with document-level summaries and chunk-level embeddings.
- **Chunking Strategy**: Employs the `Chonkie` library for semantic and structural document splitting. [surfsense_backend/pyproject.toml:48]()

### 2. Multi-LLM & Provider Gateway
- **LiteLLM Integration**: Supports 100+ models from 28 providers (OpenAI, Anthropic, Gemini, Groq, etc.) via a unified interface. [surfsense_backend/pyproject.toml:72-73]()
- **Dynamic Selection**: Supports latest models like GPT-4o, Claude 3.5 Sonnet, and Gemini 1.5 Pro. [README.md:178]()

### 3. Native Platform Scrapers
- **Proprietary Connectors**: High-performance scrapers for Reddit, TikTok, Instagram, Amazon, Walmart, YouTube, Indeed, Google Search, and Google Maps that bypass official API limitations. [README.md:53-66]()
- **Unified Interface**: Every connector is a REST endpoint returning structured JSON (posts, comments, transcripts, reviews). [README.md:48]()

### 4. Team Collaboration & RBAC
- **SearchSpaces**: Logical containers for multi-tenancy, isolating data and permissions between teams. [README.md:161]()
- **RBAC**: Role-based access control with predefined roles (Owner, Admin, Editor, Viewer). [README.md:161]()

### 5. Deployment & Operations
- **Docker-First**: Production-ready setup for rapid deployment. [README.md:118-132]()
- **Zero-Cache**: Uses `@rocicorp/zero` for real-time data synchronization between the backend and frontend. [surfsense_web/package.json:85]()
- **Alembic**: Handles database schema migrations for the PostgreSQL backend. [surfsense_backend/pyproject.toml:7]()

**Sources**: [README.md:44-70](), [README.md:134-161](), [surfsense_backend/pyproject.toml:1-90]()

## Technology Stack Summary

| Layer | Technologies |
|---|---|
| **Backend** | FastAPI, SQLAlchemy, LangGraph, LiteLLM, Celery, pgvector, Chonkie, Pydantic, Docling, Unstructured |
| **Frontend** | Next.js 16, React 19, Tailwind CSS v4, Jotai, TanStack Query, Zero-Cache, Radix UI, Framer Motion |
| **Data** | PostgreSQL 17, Redis, Redis (Broker), Local/Cloud Storage (S3, Azure) |
| **Infrastructure** | Docker, Docker Compose, Caddy, Watchtower, OpenTelemetry |
| **Desktop/Ext** | Electron, Plasmo (Browser Extension), Obsidian Plugin |

**Sources**: [surfsense_backend/pyproject.toml:6-89](), [surfsense_web/package.json:31-185](), [surfsense_desktop/package.json:26-47]()

---

