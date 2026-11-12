<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/wikirace-llms · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [api.py](api.py)
- [src/App.tsx](src/App.tsx)
- [yarn.lock](yarn.lock)

</details>



This document provides a comprehensive overview of the WikiRacing LLMs system architecture, covering the deployment infrastructure, application components, and their interactions. The system is designed as a full-stack web application that enables users to play WikiRacing games with AI language models and analyze their performance through interactive visualizations.

For detailed information about specific frontend components, see [Frontend Application](#4). For backend API implementation details, see [Backend Services](#5). For AI model integration specifics, see [AI Model Integration](#6).

## System Overview

The WikiRacing LLMs application is a containerized web application built with modern technologies to provide an interactive platform for testing language models on navigation tasks through Wikipedia-like article networks.

```mermaid
graph TB
    subgraph "Docker Container"
        subgraph "Frontend Layer"
            App["App.tsx<br/>Main React Application"]
            ViewerTab["ViewerTab<br/>Results Analysis"]
            PlayTab["PlayTab<br/>Game Interface"]
            AboutTab["AboutTab<br/>Information Pages"]
        end
        
        subgraph "Backend Layer"
            FastAPI["api.py<br/>FastAPI Application"]
            SQLiteDB["SQLiteDB class<br/>Database Abstraction"]
            StaticFiles["StaticFiles mount<br/>Serves dist/"]
        end
        
        subgraph "Data Layer"
            WikihopDB[("wikihop.db<br/>SQLite Database")]
            DistFolder["dist/<br/>Built Frontend Assets"]
        end
    end
    
    subgraph "External Services"
        HFAuth["Hugging Face OAuth<br/>Client ID: a67ef241-..."]
        HFInference["Hugging Face Inference API"]
        HFDatasets["Hugging Face Datasets<br/>simplewiki-pruned-text-350k"]
    end
    
    App --> FastAPI
    FastAPI --> SQLiteDB
    SQLiteDB --> WikihopDB
    FastAPI --> StaticFiles
    StaticFiles --> DistFolder
    
    App --> HFAuth
    App --> HFInference
    WikihopDB --> HFDatasets
    
    FastAPI --> HFAuth
```

**Core System Architecture**

Sources: [Dockerfile:1-67](), [src/App.tsx:1-82](), [api.py:1-152]()

## Deployment Architecture

The application uses Docker containerization for consistent deployment across environments, with Hugging Face Spaces as the target production platform.

```mermaid
graph LR
    subgraph "Build Process"
        BaseImage["python:3.9<br/>Base Container"]
        NodeJS["Node.js 22.x<br/>Frontend Build Tools"]
        PythonDeps["requirements.txt<br/>Python Dependencies"]
        YarnBuild["yarn build<br/>Frontend Compilation"]
        DatabaseDownload["curl wikihop.db<br/>from HF Datasets"]
    end
    
    subgraph "Runtime Environment"
        UvicornServer["uvicorn api:app<br/>--host 0.0.0.0<br/>--port 7860"]
        EnvVars["Environment Variables<br/>HUGGINGFACE_CLIENT_SECRET<br/>VITE_ENV=production<br/>HF_TOKEN"]
        DatabasePath["WIKISPEEDIA_DB_PATH<br/>/home/user/app/wikihop.db"]
    end
    
    BaseImage --> NodeJS
    NodeJS --> PythonDeps
    PythonDeps --> YarnBuild
    YarnBuild --> DatabaseDownload
    DatabaseDownload --> UvicornServer
    
    EnvVars --> UvicornServer
    DatabasePath --> UvicornServer
```

**Container Build and Runtime Process**

The Docker container follows a multi-stage approach where frontend assets are built during container creation, and the backend serves both API endpoints and static files.

Sources: [Dockerfile:1-67]()

## Frontend Application Architecture

The React application uses a tab-based interface with sophisticated visualization capabilities for analyzing model performance and game interactions.

```mermaid
graph TD
    subgraph "Main Application Structure"
        App["App.tsx<br/>Main Component"]
        TabsComponent["Tabs from @radix-ui/react-tabs"]
        TabsList["TabsList<br/>Navigation Controls"]
        
        App --> TabsComponent
        TabsComponent --> TabsList
    end
    
    subgraph "Tab Components"
        ViewerTabContent["ViewerTab<br/>handleTryRun prop"]
        PlayTabContent["PlayTab<br/>startArticle & destinationArticle props"]
        AboutTabContent["AboutTab<br/>Static Information"]
        
        TabsComponent --> ViewerTabContent
        TabsComponent --> PlayTabContent
        TabsComponent --> AboutTabContent
    end
    
    subgraph "State Management"
        SelectedTab["selectedTab: 'view' | 'play' | 'about'"]
        StartArticle["startArticle: string"]
        DestinationArticle["destinationArticle: string"]
        IsSmallScreen["isSmallScreen: boolean"]
        
        App --> SelectedTab
        App --> StartArticle
        App --> DestinationArticle
        App --> IsSmallScreen
    end
    
    subgraph "Authentication"
        HFButton["SignInWithHuggingFaceButton"]
        App --> HFButton
    end
```

**React Component Hierarchy and State Flow**

The application maintains a centralized state in the root `App` component and passes data down through props to specialized tab components.

Sources: [src/App.tsx:1-82](), [yarn.lock:1-2999]()

## Backend Services Architecture

The FastAPI backend provides a clean separation between API endpoints, database operations, and static file serving, with integrated OAuth authentication for Hugging Face services.

```mermaid
graph TB
    subgraph "FastAPI Application"
        AppInstance["app = FastAPI(title='WikiSpeedia API')"]
        CORSMiddleware["CORSMiddleware<br/>allow_origins=['*']"]
        StaticMount["app.mount('/', StaticFiles(directory='dist'))"]
        
        AppInstance --> CORSMiddleware
        AppInstance --> StaticMount
    end
    
    subgraph "API Endpoints"
        HealthEndpoint["/health<br/>HealthResponse"]
        ArticlesEndpoint["/get_all_articles<br/>List[str]"]
        ArticleEndpoint["/get_article_with_links/{article_title}<br/>ArticleResponse"]
        AuthCallback["/auth/callback<br/>OAuth Handler"]
        
        AppInstance --> HealthEndpoint
        AppInstance --> ArticlesEndpoint
        AppInstance --> ArticleEndpoint
        AppInstance --> AuthCallback
    end
    
    subgraph "Database Layer"
        SQLiteDBClass["SQLiteDB class"]
        LRUCache["@lru_cache(maxsize=8192)<br/>get_article_with_links"]
        DatabaseConnection["sqlite3.connect(db_path)<br/>conn.row_factory = sqlite3.Row"]
        
        SQLiteDBClass --> LRUCache
        SQLiteDBClass --> DatabaseConnection
    end
    
    subgraph "Data Models"
        ArticleResponse["ArticleResponse<br/>title: str, links: List[str]"]
        HealthResponse["HealthResponse<br/>status: str, article_count: int"]
    end
    
    HealthEndpoint --> SQLiteDBClass
    ArticlesEndpoint --> SQLiteDBClass
    ArticleEndpoint --> SQLiteDBClass
    ArticleEndpoint --> ArticleResponse
    HealthEndpoint --> HealthResponse
```

**Backend Service Architecture with Database Integration**

The `SQLiteDB` class provides cached access to article data, while FastAPI handles HTTP routing and response serialization through Pydantic models.

Sources: [api.py:1-152]()

## Database Schema and Access Patterns

The SQLite database uses a simple schema optimized for fast article and link retrieval with JSON serialization for link storage.

```mermaid
graph LR
    subgraph "Database Operations"
        CoreArticlesTable[("core_articles table<br/>title: TEXT<br/>links_json: TEXT")]
        GetArticleCount["_get_article_count()<br/>SELECT COUNT(*) FROM core_articles"]
        GetAllArticles["get_all_articles()<br/>SELECT title FROM core_articles"]
        GetArticleWithLinks["get_article_with_links(article_title)<br/>SELECT title, links_json WHERE title = ?"]
        
        CoreArticlesTable --> GetArticleCount
        CoreArticlesTable --> GetAllArticles
        CoreArticlesTable --> GetArticleWithLinks
    end
    
    subgraph "Caching Strategy"
        LRUCacheDecorator["@lru_cache(maxsize=8192)"]
        CachedLookups["Cached Article Lookups"]
        
        GetArticleWithLinks --> LRUCacheDecorator
        LRUCacheDecorator --> CachedLookups
    end
    
    subgraph "Data Source"
        HFDataset["HuggingFace Dataset<br/>HuggingFaceTB/simplewiki-pruned-text-350k"]
        WikihopDB["wikihop.db<br/>Downloaded at build time"]
        
        HFDataset --> WikihopDB
        WikihopDB --> CoreArticlesTable
    end
```

**Database Access Pattern with Performance Optimization**

The database uses LRU caching to optimize repeated article lookups, which is essential for the interactive nature of the WikiRacing game.

Sources: [api.py:40-75](), [Dockerfile:56-56]()

## Authentication and External Service Integration

The system integrates with Hugging Face services for both user authentication and AI model inference through OAuth 2.0 flow.

```mermaid
graph TB
    subgraph "OAuth Configuration"
        ClientID["CLIENT_ID<br/>a67ef241-fb7e-4300-a6bd-8430a7565c9a"]
        ClientSecret["HUGGINGFACE_CLIENT_SECRET<br/>Environment Variable"]
        RedirectURI["redirect_uri<br/>localhost:8000 (dev)<br/>hf.space (prod)"]
    end
    
    subgraph "Authentication Flow"
        AuthCallback["/auth/callback endpoint"]
        TokenExchange["requests.post(OAUTH_API_BASE)<br/>Authorization: Basic base64(client_id:secret)"]
        TokenResponse["access_token, id_token<br/>expires_in: 28799"]
        RedirectHome["RedirectResponse<br/>/?access_token=...&id_token=..."]
        
        AuthCallback --> TokenExchange
        TokenExchange --> TokenResponse
        TokenResponse --> RedirectHome
    end
    
    subgraph "Environment Detection"
        EnvCheck["IS_PROD = os.getenv('VITE_ENV') == 'production'"]
        ProdURL["https://huggingfacetb-wikiracing-llms.hf.space"]
        DevURL["http://localhost:8000"]
        
        EnvCheck --> ProdURL
        EnvCheck --> DevURL
    end
    
    ClientID --> AuthCallback
    ClientSecret --> TokenExchange
    RedirectURI --> TokenExchange
```

**Hugging Face OAuth Integration Flow**

The authentication system handles both development and production environments with different redirect URIs, and exchanges authorization codes for access tokens that enable AI model inference.

Sources: [api.py:99-144](), [api.py:26-29]()

## Technology Stack and Dependencies

The application leverages modern web technologies with specific focus on data visualization and AI model integration capabilities.

| Component | Technology | Key Libraries | Purpose |
|-----------|------------|---------------|---------|
| Frontend | React 19.0.0 | @radix-ui, d3@7.9.0, @huggingface/inference | UI components and data visualization |
| Build System | Vite 6.3.1 | @tailwindcss/vite, @vitejs/plugin-react | Development and build tooling |
| Backend | FastAPI | uvicorn, pydantic | API server and data validation |
| Database | SQLite3 | Built-in Python sqlite3 | Article and link storage |
| Visualization | D3.js + React | force-graph, @tanstack/react-virtual | Interactive network graphs |
| Authentication | OAuth 2.0 | Hugging Face OAuth endpoints | User authentication |
| Containerization | Docker | python:3.9, Node.js 22.x | Deployment packaging |

Sources: [yarn.lock:1-2999](), [api.py:1-14](), [Dockerfile:1-67]()

---

