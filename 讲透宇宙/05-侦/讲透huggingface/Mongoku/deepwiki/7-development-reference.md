<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/Mongoku · page 7 Development Reference · fetched 2026-10-26 -->

# Development Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/package-lock.json](app/package-lock.json)
- [app/package.json](app/package.json)
- [package-lock.json](package-lock.json)

</details>



This document provides technical reference material for developers who want to understand, modify, or contribute to Mongoku. It covers the development technology stack, dependency architecture, build systems, and key code entities that comprise the application.

For deployment and configuration information, see [Deployment and Configuration](#6). For user-facing feature documentation, see [User Features](#4).

## Technology Stack Overview

Mongoku is built as a full-stack web application using a modern JavaScript/TypeScript technology stack with clear separation between frontend and backend concerns.

### Core Technologies Architecture

```mermaid
graph TB
    subgraph "Runtime Environment"
        NodeJS["Node.js Runtime"]
        V8["V8 JavaScript Engine"]
    end
    
    subgraph "Backend Stack"
        Express["express@4.17.2<br/>Web Server Framework"]
        MongoDB["mongodb@5.9.2<br/>Database Driver"]
        AWS["@aws-sdk/credential-providers@3.592.0<br/>Cloud Integration"]
        NeDB["nedb@1.8.0<br/>Local Config Storage"]
    end
    
    subgraph "Frontend Stack"
        Angular["@angular/core@13.4.0<br/>SPA Framework"]
        Bootstrap["bootstrap@4.1.3<br/>UI Framework"]
        CodeMirror["codemirror@5.65.0<br/>Code Editor"]
        RxJS["rxjs@7.5.1<br/>Reactive Programming"]
    end
    
    subgraph "Build System"
        AngularCLI["@angular/cli@13.3.11<br/>Frontend Build"]
        TypeScript["typescript@4.5.4<br/>Type System"]
        Webpack["webpack@5.76.1<br/>Module Bundler"]
        Sass["sass@1.49.9<br/>CSS Preprocessor"]
    end
    
    subgraph "Development Tools"
        TSNode["ts-node@10.4.0<br/>TypeScript Execution"]
        Jasmine["jasmine-core@4.0.0<br/>Testing Framework"]
        Karma["karma@6.3.10<br/>Test Runner"]
        TSLint["tslint@6.1.3<br/>Code Linting"]
    end
    
    NodeJS --> Express
    NodeJS --> Angular
    Express --> MongoDB
    Express --> AWS
    Express --> NeDB
    Angular --> Bootstrap
    Angular --> CodeMirror
    Angular --> RxJS
    
    AngularCLI --> Angular
    AngularCLI --> Webpack
    TypeScript --> Angular
    TypeScript --> Express
    Sass --> Bootstrap
    
    TSNode --> TypeScript
    Jasmine --> Karma
    TSLint --> TypeScript
```

Sources: [package.json:11-21](), [app/package.json:14-34](), [app/package.json:35-54]()

## Dependency Architecture

The application dependencies are organized into distinct categories based on their function within the development and runtime environments.

### Runtime Dependencies Structure

```mermaid
graph LR
    subgraph "Core Server Dependencies"
        express["express"]
        bodyparser["body-parser"]
        mongodb["mongodb"]
        nedb["nedb"]
    end
    
    subgraph "AWS Integration"
        awssdk["@aws-sdk/credential-providers"]
        aws4["aws4"]
    end
    
    subgraph "CLI Framework"
        commander["commander"]
        figlet["figlet"]
        chalk["chalk"]
    end
    
    subgraph "Angular Runtime"
        angularcore["@angular/core"]
        angularcommon["@angular/common"]
        angularrouter["@angular/router"]
        angularforms["@angular/forms"]
    end
    
    subgraph "UI Components"
        bootstrap["bootstrap"]
        ngbootstrap["@ng-bootstrap/ng-bootstrap"]
        codemirror["codemirror"]
        ngxcodemirror["@ctrl/ngx-codemirror"]
    end
    
    subgraph "Utility Libraries"
        rxjs["rxjs"]
        corejs["core-js"]
        esprima["esprima"]
        zonejs["zone.js"]
    end
    
    express --> bodyparser
    express --> mongodb
    express --> nedb
    express --> awssdk
    express --> aws4
    express --> commander
    
    angularcore --> angularcommon
    angularcore --> angularrouter
    angularcore --> angularforms
    angularcore --> bootstrap
    angularcore --> rxjs
    
    bootstrap --> ngbootstrap
    codemirror --> ngxcodemirror
    angularcore --> corejs
    angularcore --> zonejs
```

Sources: [package.json:11-21](), [app/package.json:14-34]()

## Build System Architecture

Mongoku uses a dual-build system approach with separate build processes for the backend Node.js application and the frontend Angular application.

### Build Process Flow

| Component | Build Tool | Input | Output | Configuration |
|-----------|------------|--------|--------|---------------|
| **Backend** | `tsc` (TypeScript Compiler) | `src/**/*.ts` | `dist/**/*.js` | `tsconfig.json` |
| **Frontend** | `@angular/cli` | `app/src/**/*.ts` | `app/dist/**/*.js` | `app/angular.json` |
| **Styles** | `sass-loader` | `app/src/**/*.scss` | CSS bundles | Webpack config |
| **Assets** | `copy-webpack-plugin` | Static files | `app/dist/assets/` | Angular build config |

### Development vs Production Builds

The build system supports different optimization levels:

**Development Mode:**
- Source maps enabled for debugging
- Hot module replacement for frontend
- Unminified code for easier debugging
- Development server with live reload

**Production Mode:**
- Code minification via `terser@5.14.2`
- Tree shaking for dead code elimination
- Asset optimization and compression
- Ahead-of-time (AOT) compilation for Angular

Sources: [app/package.json:35-54](), [package.json:25-30]()

## Key Development Dependencies

### Frontend Development Tools

The Angular application uses a comprehensive set of development tools:

```mermaid
graph TD
    subgraph "Angular Toolchain"
        AngularCLI["@angular/cli@13.3.11"]
        AngularDevkit["@angular-devkit/build-angular@13.3.11"]
        AngularCompiler["@angular/compiler-cli@13.4.0"]
    end
    
    subgraph "Testing Infrastructure"
        Jasmine["jasmine-core@4.0.0"]
        Karma["karma@6.3.10"]
        KarmaChrome["karma-chrome-launcher@3.1.0"]
        KarmaJasmine["karma-jasmine@4.0.1"]
        Protractor["protractor@7.0.0"]
    end
    
    subgraph "Code Quality"
        TSLint["tslint@6.1.3"]
        Codelyzer["codelyzer@6.0.2"]
        TypeScript["typescript@4.5.4"]
    end
    
    subgraph "Build Pipeline"
        TSNode["ts-node@10.4.0"]
        Webpack["webpack@5.76.1"]
        SassLoader["sass-loader@12.4.0"]
        CSSLoader["css-loader@6.5.1"]
    end
    
    AngularCLI --> AngularDevkit
    AngularDevkit --> AngularCompiler
    AngularDevkit --> Webpack
    
    Karma --> Jasmine
    Karma --> KarmaChrome
    Karma --> KarmaJasmine
    
    TSLint --> TypeScript
    TSLint --> Codelyzer
    
    Webpack --> SassLoader
    Webpack --> CSSLoader
    TSNode --> TypeScript
```

Sources: [app/package.json:35-54]()

### Backend Development Dependencies

The backend uses TypeScript definitions and development utilities:

- `@types/express@4.17.13`: TypeScript definitions for Express.js
- `@types/figlet@1.5.4`: TypeScript definitions for ASCII art library
- `@types/mongodb@4.0.7`: TypeScript definitions for MongoDB driver  
- `@types/nedb@1.8.12`: TypeScript definitions for NeDB

Sources: [package.json:25-30]()

## Development Workflow

### Local Development Setup

1. **Backend Development**: TypeScript files in `/src` are compiled to `/dist` using the TypeScript compiler
2. **Frontend Development**: Angular application in `/app` uses Angular CLI development server with hot reload
3. **Concurrent Development**: Both backend and frontend can be developed simultaneously using separate terminal sessions

### Testing Strategy

| Test Type | Framework | Location | Purpose |
|-----------|-----------|----------|---------|
| **Unit Tests** | Jasmine + Karma | `app/src/**/*.spec.ts` | Component and service testing |
| **E2E Tests** | Protractor | `app/e2e/` | End-to-end user workflows |
| **Backend Tests** | Custom (if any) | `src/**/*.test.ts` | Server logic testing |

### Code Quality Tools

- **TSLint**: Enforces TypeScript coding standards
- **Codelyzer**: Angular-specific linting rules
- **TypeScript**: Static type checking for both frontend and backend

Sources: [app/package.json:5-12](), [app/package.json:40-53]()

## File Structure and Module Organization

### Backend Module Structure

The backend follows a modular architecture with these key areas:

- **Express Server**: Web server and routing logic
- **MongoDB Manager**: Database connection and operations management
- **Host Manager**: Configuration and connection string management  
- **API Layer**: REST endpoint definitions and request handling
- **CLI Interface**: Command-line interface and process management

### Frontend Module Structure  

The Angular application is organized into feature modules:

- **Core Module**: Shared services and singleton providers
- **Shared Module**: Reusable components and directives
- **Feature Modules**: Page-specific components and logic
- **Routing Module**: Navigation and route configuration

Sources: Based on system architecture diagrams and dependency analysis

This development reference provides the foundation for understanding Mongoku's technical architecture. For specific build instructions and environment setup, see [Build and Development Setup](#7.2). For dependency details and system requirements, see [Dependencies and Requirements](#7.1).

---

