<!-- source: DeepWiki mcp.deepwiki.com · repo makenotion/notion-cookbook · page 3 Examples · fetched 2026-10-26 -->

# Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/README.md](examples/README.md)
- [examples/javascript/README.md](examples/javascript/README.md)

</details>



## Purpose and Scope

This document provides an overview of all working code examples in the Notion Cookbook repository, organized by programming language and complexity level. These examples demonstrate practical integrations with Notion's API, from basic operations to advanced multi-service integrations.

For detailed documentation of specific examples, see:
- [Introduction to Notion API](#3.1) - Basic and intermediate Notion API operations
- [Database Email Update](#3.2) - Database monitoring with email notifications
- [Generate Random Data](#3.3) - Synthetic data population utilities
- [Additional JavaScript Examples](#3.4) - GitHub sync, web forms, and text parsing

For initial setup instructions, see [Getting Started](#2). For contribution guidelines, see [Contributing](#6).

**Sources:** [examples/README.md:1-43]()

## Example Organization

All examples are located in the `examples/` directory and organized by programming language. Currently, all available examples are in JavaScript and utilize the official `@notionhq/client` SDK.

### Directory Structure

```mermaid
graph TB
    ROOT["examples/"]
    README["README.md<br/>Example overview"]
    JS["javascript/"]
    JSREADME["javascript/README.md<br/>JavaScript-specific guide"]
    
    ROOT --> README
    ROOT --> JS
    JS --> JSREADME
    
    subgraph "Getting Started"
        INTRO["intro-to-notion-api/<br/>Basic & intermediate examples"]
    end
    
    subgraph "Integration Examples"
        DBEMAIL["database-email-update/<br/>Database monitoring + SendGrid"]
        GENDATA["generate-random-data/<br/>Faker data generation"]
        GHSYNC["notion-github-sync/<br/>GitHub issues sync"]
        TASKPR["notion-task-github-pr-sync/<br/>Task-PR linking"]
        WEBFORM["web-form-with-express/<br/>Express.js form submission"]
    end
    
    subgraph "Utility Examples"
        PARSETEXT["parse-text-from-any-block-type/<br/>Text extraction utility"]
    end
    
    JS --> INTRO
    JS --> DBEMAIL
    JS --> GENDATA
    JS --> GHSYNC
    JS --> TASKPR
    JS --> WEBFORM
    JS --> PARSETEXT
    
    INTRO --> BASIC["basic/<br/>1-add-block.ts<br/>2-add-linked-block.ts<br/>3-add-styled-block.ts"]
    INTRO --> INTER["intermediate/<br/>1-create-a-database.ts<br/>2-add-page-to-database.ts<br/>3-query-database.ts<br/>4-sort-database.ts<br/>5-upload-file.ts<br/>6-create-page-with-template.ts"]
```

**Sources:** [examples/README.md:1-43](), [examples/javascript/README.md:1-62]()

## Example Categories

### Getting Started Examples

| Example | Purpose | Complexity | Key Concepts |
|---------|---------|------------|--------------|
| **intro-to-notion-api** | Learn fundamental Notion API operations | Basic → Intermediate | Blocks, pages, databases, file uploads, templates |

The `intro-to-notion-api` example serves as the entry point for developers new to Notion's API. It includes two subdirectories: `basic/` for fundamental operations and `intermediate/` for more complex interactions.

**Sources:** [examples/README.md:11](), [examples/javascript/README.md:15]()

### Integration Examples

| Example | Purpose | External Services | Key Concepts |
|---------|---------|-------------------|--------------|
| **database-email-update** | Monitor database changes and send notifications | SendGrid | Database queries, change detection, email delivery |
| **generate-random-data** | Populate databases with synthetic test data | Faker.js | Data generation, batch operations, database population |
| **notion-github-sync** | Sync GitHub issues to Notion database | GitHub API | Bidirectional sync, issue tracking, webhooks |
| **notion-task-github-pr-sync** | Link Notion tasks with GitHub pull requests | GitHub API | Task management, PR tracking, status updates |
| **web-form-with-express** | Submit web form data to Notion | Express.js | HTTP routing, form processing, page creation |

These examples demonstrate real-world integration patterns that combine Notion's API with external services.

**Sources:** [examples/README.md:12-17](), [examples/javascript/README.md:19-24]()

### Utility Examples

| Example | Purpose | Key Concepts |
|---------|---------|--------------|
| **parse-text-from-any-block-type** | Extract text content from various block types | Block traversal, type handling, text extraction |

This utility demonstrates how to handle Notion's diverse block types when extracting textual content.

**Sources:** [examples/README.md:16](), [examples/javascript/README.md:27]()

## Learning Progression

The examples are designed to support a progressive learning path, starting with fundamental concepts and advancing to complex integrations.

```mermaid
graph LR
    START["Developer"]
    
    START --> PHASE1["Phase 1:<br/>Basic Operations"]
    
    PHASE1 --> B1["1-add-block.ts<br/>Create simple blocks"]
    PHASE1 --> B2["2-add-linked-block.ts<br/>Link blocks together"]
    PHASE1 --> B3["3-add-styled-block.ts<br/>Apply formatting"]
    
    B3 --> PHASE2["Phase 2:<br/>Intermediate Concepts"]
    
    PHASE2 --> I1["1-create-a-database.ts<br/>Database structure"]
    PHASE2 --> I2["2-add-page-to-database.ts<br/>Database pages"]
    PHASE2 --> I3["3-query-database.ts<br/>Query operations"]
    PHASE2 --> I4["4-sort-database.ts<br/>Sorting & filtering"]
    PHASE2 --> I5["5-upload-file.ts<br/>File handling"]
    PHASE2 --> I6["6-create-page-with-template.ts<br/>Templates"]
    
    I6 --> PHASE3["Phase 3:<br/>Advanced Integrations"]
    
    PHASE3 --> A1["database-email-update<br/>Event-driven monitoring"]
    PHASE3 --> A2["notion-github-sync<br/>Third-party sync"]
    PHASE3 --> A3["web-form-with-express<br/>Web server integration"]
    
    PHASE3 --> UTILS["Utility Patterns"]
    UTILS --> U1["parse-text-from-any-block-type<br/>Block type handling"]
    UTILS --> U2["generate-random-data<br/>Data generation"]
```

**Sources:** [examples/README.md:11](), [examples/javascript/README.md:13-28]()

## Common Setup Pattern

All JavaScript examples follow a standardized setup workflow, ensuring consistency and reducing cognitive load when switching between examples.

```mermaid
graph TB
    DEV["Developer"]
    
    DEV --> STEP1["Step 1: Create Integration"]
    STEP1 --> PORTAL["Visit notion.com/my-integrations"]
    PORTAL --> CREATEINT["Create new integration<br/>Obtain NOTION_API_KEY"]
    
    CREATEINT --> STEP2["Step 2: Install Dependencies"]
    STEP2 --> INSTALL["npm install"]
    INSTALL --> DEPS["Dependencies installed:<br/>@notionhq/client<br/>dotenv<br/>Example-specific packages"]
    
    DEPS --> STEP3["Step 3: Configure Environment"]
    STEP3 --> COPYENV["cp .env.example .env"]
    COPYENV --> EDITENV["Edit .env file:<br/>NOTION_API_KEY=secret_xxx<br/>DATABASE_ID=abc123<br/>PAGE_ID=def456"]
    
    EDITENV --> STEP4["Step 4: Share Resources"]
    STEP4 --> SHARE["In Notion:<br/>• Click ••• menu<br/>• Add connections<br/>• Select integration"]
    
    SHARE --> STEP5["Step 5: Run Example"]
    STEP5 --> RUN["npm start<br/>or<br/>npm run ts-run"]
    
    RUN --> OUTPUT["Example executes<br/>Interacts with Notion API"]
```

**Sources:** [examples/README.md:19-28](), [examples/javascript/README.md:29-56]()

## Prerequisites

### System Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Node.js** | 18 or higher | JavaScript runtime |
| **npm** | Included with Node.js | Package management |

**Sources:** [examples/javascript/README.md:7]()

### Notion Requirements

| Requirement | Acquisition Method |
|-------------|-------------------|
| **Notion Integration** | Create at [notion.com/my-integrations](https://www.notion.com/my-integrations) |
| **API Key** | Generated when creating integration (format: `secret_xxx...`) |
| **Shared Resources** | Page or database must be explicitly shared with integration |

All examples require a Notion integration with appropriate capabilities (read content, update content, insert content) depending on the example's operations.

**Sources:** [examples/README.md:23-24](), [examples/javascript/README.md:8-9]()

## Environment Configuration

Each example includes an `.env.example` file that serves as a template for required environment variables. The common pattern is:

```mermaid
graph LR
    EXAMPLE[".env.example<br/>Template file"]
    COPY["Copy to .env"]
    EDIT["Edit variables"]
    LOAD["Loaded by dotenv"]
    
    EXAMPLE --> COPY
    COPY --> EDIT
    EDIT --> LOAD
    LOAD --> CODE["Example code accesses<br/>process.env.NOTION_API_KEY"]
    
    subgraph "Common Variables"
        VAR1["NOTION_API_KEY<br/>Integration token"]
        VAR2["DATABASE_ID<br/>Target database"]
        VAR3["PAGE_ID<br/>Target page"]
    end
    
    subgraph "Service-Specific Variables"
        VAR4["SENDGRID_API_KEY<br/>(database-email-update)"]
        VAR5["GITHUB_TOKEN<br/>(notion-github-sync)"]
        VAR6["PORT<br/>(web-form-with-express)"]
    end
```

**Sources:** [examples/javascript/README.md:39-46]()

## Common Dependencies

All JavaScript examples share core dependencies, with additional packages required for specific integrations:

| Package | Purpose | Used In |
|---------|---------|---------|
| **@notionhq/client** | Official Notion SDK | All examples |
| **dotenv** | Environment variable management | All examples |
| **typescript** | Type checking and compilation | All examples |
| **@sendgrid/mail** | Email delivery | database-email-update |
| **@faker-js/faker** | Synthetic data generation | generate-random-data |
| **@octokit/rest** | GitHub API client | notion-github-sync, notion-task-github-pr-sync |
| **express** | Web server framework | web-form-with-express |

**Sources:** [examples/README.md:1-43](), [examples/javascript/README.md:1-62]()

## Running Examples

### Standard Execution

Most examples provide an `npm start` script that executes the main entry point:

```bash
npm install
npm start
```

For TypeScript examples with a custom runner:

```bash
npm run ts-run
```

### Resource Sharing

Before running any example, the target Notion page or database must be shared with the integration:

1. Navigate to the page/database in Notion
2. Click the `•••` menu (top right)
3. Select "Add connections"
4. Choose your integration from the list

Without this step, the API will return authorization errors when attempting operations.

**Sources:** [examples/README.md:19-27](), [examples/javascript/README.md:48-56]()

## Example Structure

Each example follows a consistent directory structure:

```
example-name/
├── README.md           # Specific setup and usage instructions
├── package.json        # Dependencies and npm scripts
├── tsconfig.json       # TypeScript configuration
├── .env.example        # Environment variable template
├── index.ts or index.js # Main entry point
└── src/                # Additional source files (if needed)
```

This standardization ensures developers can quickly navigate and understand any example in the repository.

**Sources:** [examples/README.md:33-38]()

## Contributing Examples

The repository welcomes new examples that demonstrate additional integration patterns or programming languages. When contributing an example, ensure it includes:

| Requirement | Purpose |
|-------------|---------|
| **Clear README** | Explains purpose, setup steps, and usage |
| **Configuration files** | `package.json`, `tsconfig.json`, `.env.example` |
| **Working code** | Tested and verified functionality |
| **Focused scope** | Demonstrates a specific technique or integration |

For complete contribution guidelines, see [Contributing](#6).

**Sources:** [examples/README.md:29-42]()

## Additional Resources

| Resource | Location |
|----------|----------|
| **Notion API Reference** | [developers.notion.com/reference](https://developers.notion.com/reference) |
| **JavaScript SDK Documentation** | [github.com/makenotion/notion-sdk-js](https://github.com/makenotion/notion-sdk-js) |
| **Getting Started Guide** | [developers.notion.com/docs/getting-started](https://developers.notion.com/docs/getting-started) |

**Sources:** [examples/javascript/README.md:58-62]()

---

