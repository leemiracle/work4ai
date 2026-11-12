# Page: Overview — TestMu AI Agent Skills

# Overview — TestMu AI Agent Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [skills_index.json](skills_index.json)
- [testng-skill/SKILL.md](testng-skill/SKILL.md)
- [testng-skill/reference/advanced-patterns.md](testng-skill/reference/advanced-patterns.md)

</details>



TestMu AI Agent Skills is a curated repository of production-grade instructions and code patterns designed for AI coding assistants (such as Claude Code, Cursor, and GitHub Copilot). It transforms generic AI responses into expert-level test automation architectures across 46 frameworks and over 15 programming languages [README.md:1-15]().

By providing structured context through the **Agent Skills Standard**, this repository ensures that AI agents follow industry best practices, implement robust Page Object Models (POM), integrate with cloud execution environments like LambdaTest, and configure reliable CI/CD pipelines [README.md:17-23]().

## System Architecture: From Natural Language to Test Code

The repository acts as a bridge between a user's high-level intent (Natural Language Space) and specific, runnable test entities (Code Entity Space). When a user asks an AI assistant to "Write Playwright tests for login," the agent consumes the relevant skill to produce structured code [README.md:54-65]().

### Intent Mapping Diagram
The following diagram illustrates how user requests are mapped to specific skill entities and their corresponding output files.

**Diagram: Intent to Code Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space (User Intent)"
        A["'Write Playwright tests'"]
        B["'Add JUnit 5 with Mockito'"]
    end

    subgraph "Skill Registry (agent-skills)"
        direction LR
        S1["playwright-skill"]
        S2["junit-5-skill"]
        Idx["skills_index.json"]
    end

    subgraph "Code Entity Space (Output)"
        C1["playwright.config.ts"]
        C2["BasePage.ts"]
        C3["LoginTest.java"]
        C4["pom.xml (Surefire)"]
    end

    A --> Idx
    B --> Idx
    Idx --> S1
    Idx --> S2
    
    S1 --> C1
    S1 --> C2
    S2 --> C3
    S2 --> C4
```
**Sources:** [skills_index.json:1-160](), [README.md:54-65]()

## The Agent Skills Standard (`SKILL.md`)

Each skill in the repository follows a strict structural format defined by the **Agent Skills Standard**. This ensures consistency across different frameworks and allows AI tools to easily parse the capabilities and triggers for each skill [README.md:69-82]().

### Skill File Structure
A skill is composed of a primary entry point and supplementary reference files to manage context window limits through progressive disclosure:
*   **`SKILL.md`**: The primary entry point containing YAML frontmatter (name, description, triggers) and core patterns [CONTRIBUTING.md:16-32]().
*   **`reference/playbook.md`**: Detailed implementation guides, project structures, and debugging tables [CONTRIBUTING.md:46-46]().
*   **`reference/advanced-patterns.md`**: Complex use cases, such as parallel execution or custom listeners [testng-skill/reference/advanced-patterns.md:1-118]().

### Component Interaction Diagram
This diagram shows how the internal components of a skill (e.g., `testng-skill`) interact to provide a complete automation solution.

**Diagram: Skill Component Architecture**
```mermaid
graph LR
    subgraph "Skill Package (e.g., testng-skill/)"
        SM["SKILL.md (Triggers & Core)"]
        PB["reference/playbook.md (Setup)"]
        ADV["reference/advanced-patterns.md"]
        CI["reference/cloud-integration.md"]
    end

    subgraph "External Integration"
        LT["TestMu AI / LambdaTest Cloud"]
        GHA["GitHub Actions (YAML)"]
    end

    SM -- "Progressive Disclosure" --> PB
    PB --> ADV
    ADV -- "Cloud Capabilities" --> CI
    CI -- "RemoteWebDriver / LT:Options" --> LT
    PB -- "Workflow Templates" --> GHA
```
**Sources:** [CONTRIBUTING.md:43-57](), [testng-skill/SKILL.md:141-158](), [testng-skill/reference/advanced-patterns.md:92-109]()

## Skill Categories and Registry

The repository contains 46 skills organized into 7 primary categories to cover the entire software testing lifecycle [skills_index.json:6-15]().

| Category | Description | Key Frameworks |
| :--- | :--- | :--- |
| **E2E / Browser** | Web automation across all major browsers. | Selenium, Playwright, Cypress [README.md:89-89]() |
| **Unit Testing** | Component and logic testing across 15+ languages. | Jest, JUnit 5, pytest, xUnit [README.md:90-90]() |
| **Mobile Testing** | Native and cross-platform mobile automation. | Appium, Espresso, XCUITest [README.md:91-91]() |
| **BDD Testing** | Behavior-driven development using Gherkin. | Cucumber, SpecFlow, Behave [README.md:92-92]() |
| **Visual / Cloud** | Visual regression and high-speed orchestration. | SmartUI, HyperExecute [README.md:93-94]() |
| **Migration** | Tooling to switch between frameworks. | Selenium ↔ Playwright [README.md:95-95]() |
| **DevOps** | Pipeline configurations for continuous testing. | GitHub Actions, Jenkins [README.md:96-96]() |

For a full list of all 46 skills and their supported languages, see the [Skill Registry — All 46 Skills by Category](#1.3).

## Core Functionality

### 1. Progressive Disclosure Model
To avoid overwhelming the AI's context window, skills are designed to be consumed in stages. The `SKILL.md` file is kept under 500 lines, focusing on "decision trees" and "quick-reference patterns," while deep technical details are offloaded to the `reference/` directory [CONTRIBUTING.md:34-49]().

### 2. Cloud and Local Execution
Every E2E and Mobile skill is "Cloud Ready." They include patterns for local execution (e.g., `chromedriver`) and cloud execution via LambdaTest using `LT:Options` and `RemoteWebDriver` [README.md:1-10](), [CONTRIBUTING.md:53-53]().

### 3. Validation and Quality Assurance
The repository includes a validation suite (`scripts/validate_skills.py`) that enforces frontmatter correctness, line counts, and the presence of required reference files like the `playbook.md` [CONTRIBUTING.md:36-41]().

## Child Pages

*   [Getting Started — Installation and Usage](#1.1): How to install these skills into your AI assistant (Claude, Cursor, etc.) and start generating tests.
*   [Skill Architecture — SKILL.md Format and Structure](#1.2): Detailed breakdown of the Agent Skills Standard and how to contribute new skills.
*   [Skill Registry — All 46 Skills by Category](#1.3): A complete index of every framework supported by the repository.

**Sources:** [README.md:1-140](), [skills_index.json:1-40](), [CONTRIBUTING.md:1-61]()

---

# Page: Getting Started — Installation and Usage

# Getting Started — Installation and Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [shared/testmu-cloud-reference.md](shared/testmu-cloud-reference.md)

</details>



This guide provides step-by-step instructions for integrating TestMu AI Agent Skills into various AI coding assistants. It covers installation paths, credential configuration for cloud execution, and natural language patterns for triggering test generation across 46 supported frameworks.

### 1. Installation Overview

Agent Skills are distributed as a collection of `SKILL.md` files and supporting reference directories. These skills follow the **Agent Skills Standard**, allowing them to be consumed by CLI tools, IDE extensions, and web-based AI interfaces [README.md:8-15]().

#### Installation Paths by Tool
The following table defines where to clone or copy the repository based on your preferred AI assistant [README.md:73-81]().

| Tool | Installation Path | Type |
| :--- | :--- | :--- |
| **Claude Code** | `.claude/skills/` | CLI |
| **Cursor** | `.cursor/skills/` | IDE |
| **GitHub Copilot** | `.github/skills/` | Extension |
| **Gemini CLI** | `.gemini/skills/` | CLI |
| **Universal** | `.agent/skills/` | General |

---

### 2. Installation Methods

Users can choose between installing a specific skill to minimize context overhead or installing the entire registry for full framework coverage.

#### Option A: Install a Single Skill
To install only a specific skill (e.g., Selenium or Playwright), clone the repository and copy the relevant directory to your tool's skill path [README.md:27-36]().

```bash
# Example: Installing Selenium skill for Claude Code
git clone https://github.com/LambdaTest/agent-skills.git
cp -r agent-skills/selenium-skill .claude/skills/

# Example: Installing Playwright skill for Cursor
cp -r agent-skills/playwright-skill .cursor/skills/
```

#### Option B: Install All Skills (Recommended)
To give your AI agent access to all 46 skills, clone the entire repository directly into the skill directory of your tool [README.md:38-52]().

```bash
# For Claude Code
git clone https://github.com/LambdaTest/agent-skills.git .claude/skills/agent-skills

# For Cursor
git clone https://github.com/LambdaTest/agent-skills.git .cursor/skills/agent-skills
```

**Sources:** [README.md:27-52](), [README.md:73-81]()

---

### 3. Setting Up Credentials

For skills that support cloud execution (E2E, Mobile, Visual), you must configure LambdaTest/TestMu AI credentials. These are passed to the agent via environment variables [shared/testmu-cloud-reference.md:18-25]().

#### Environment Variables
The agent looks for these variables to authenticate with the cloud hub or CDP endpoint [shared/testmu-cloud-reference.md:20-25]().

```bash
export LT_USERNAME="your_username"
export LT_ACCESS_KEY="your_access_key"
```

#### Data Flow: Local Assistant to Cloud Infrastructure
The following diagram illustrates how the AI assistant uses the installed skills and credentials to communicate with the LambdaTest/TestMu AI cloud.

**System Connectivity Diagram**
```mermaid
graph TD
    subgraph "Local Environment"
        A["AI Assistant (Claude/Cursor)"] -- "Reads" --> B[".skills/agent-skills/"]
        B -- "Provides" --> C["SKILL.md & reference/"]
        A -- "Injects" --> D["LT_USERNAME & LT_ACCESS_KEY"]
    end

    subgraph "TestMu AI Cloud"
        E["hub.lambdatest.com/wd/hub"]
        F["cdp.lambdatest.com/playwright"]
    end

    A -- "Selenium/Appium Traffic" --> E
    A -- "Playwright/Puppeteer CDP" --> F
```
**Sources:** [README.md:20-23](), [shared/testmu-cloud-reference.md:29-41]()

---

### 4. Natural Language Usage Patterns

Once installed, you do not need to provide manual instructions on how to write tests. Simply ask the assistant to perform a task using natural language. The agent will automatically reference the appropriate `SKILL.md` file to determine project structure, dependency versions, and cloud capabilities [README.md:17-23]().

#### Common Prompt Examples
| Goal | Example Prompt |
| :--- | :--- |
| **Cloud Execution** | "Write Playwright tests for the login page and run them on TestMu AI cloud (Chrome + Firefox)" [README.md:57]() |
| **Component Testing** | "Set up Cypress component tests for the React dashboard and upload screenshots on failure" [README.md:59]() |
| **Unit Testing** | "Create JUnit 5 tests for the payments service with Mockito and GitHub Actions CI" [README.md:61]() |
| **Local Debugging** | "Run Playwright tests locally against http://localhost:3000 with trace and video enabled" [README.md:63]() |

---

### 5. Technical Implementation of Cloud Routing

When a skill is triggered for cloud execution, the agent uses the `shared/testmu-cloud-reference.md` to construct the connection strings and capability objects.

#### Connection Logic
The agent selects the endpoint based on the framework type [shared/testmu-cloud-reference.md:29-41]():
1.  **CDP-based (Playwright/Puppeteer):** Uses `wss://cdp.lambdatest.com/playwright?capabilities={encoded_json}`.
2.  **WebDriver-based (Selenium/Appium):** Uses `https://{LT_USERNAME}:{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`.

#### Status Reporting Logic
The agent implements explicit status reporting because cloud tests are marked "Completed" by default. It injects code to update the status to "passed" or "failed" based on assertion outcomes [shared/testmu-cloud-reference.md:125-160]().

**Code Entity Mapping: Status Reporting**
```mermaid
graph LR
    subgraph "Natural Language Space"
        NL["'Report test status to LambdaTest'"]
    end

    subgraph "Code Entity Space"
        JS["page.evaluate() with 'setTestStatus'"]
        JAVA["((JavascriptExecutor) driver).executeScript('lambda-status=passed')"]
        PY["driver.execute_script('lambda-status=passed')"]
    end

    NL --> JS
    NL --> JAVA
    NL --> PY
```
**Sources:** [shared/testmu-cloud-reference.md:125-160]()

---

### 6. Summary of Capabilities

The agent-skills repository covers 46 frameworks across 15+ languages [README.md:6-7]().

| Category | Skills Count | Key Frameworks |
| :--- | :--- | :--- |
| **E2E Browser** | 15 | Selenium, Playwright, Cypress, WebdriverIO [README.md:89]() |
| **Unit Testing** | 15 | Jest, JUnit 5, pytest, TestNG, Vitest [README.md:90]() |
| **Mobile** | 5 | Appium, Espresso, XCUITest, Flutter, Detox [README.md:91]() |
| **BDD** | 7 | Cucumber, SpecFlow, Serenity BDD [README.md:92]() |
| **Specialized** | 4 | Migration, HyperExecute, SmartUI, CI/CD [README.md:93-96]() |

**Sources:** [README.md:85-97]()

---

# Page: Skill Architecture — SKILL.md Format and Structure

# Skill Architecture — SKILL.md Format and Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [scripts/rename_skills.py](scripts/rename_skills.py)
- [scripts/validate_skills.py](scripts/validate_skills.py)
- [skills_index.json](skills_index.json)
- [testng-skill/SKILL.md](testng-skill/SKILL.md)
- [testng-skill/reference/advanced-patterns.md](testng-skill/reference/advanced-patterns.md)

</details>



This page defines the **Agent Skills Standard**, the architectural blueprint used by the TestMu AI Agent to consume, process, and execute testing tasks across 46+ frameworks. The architecture relies on a structured metadata layer (Frontmatter) and a progressive-disclosure content model to balance high-level context with deep technical implementation details.

## The Progressive-Disclosure Model

To prevent context-window saturation in AI models, the repository implements a tiered documentation structure. This allows an AI agent to first understand the "what" and "when" of a skill before diving into the "how."

1.  **`SKILL.md` (Entry Point):** Contains core workflows, decision trees, and quick-reference patterns. It is strictly limited to 500 lines [scripts/validate_skills.py:11-11]().
2.  **`reference/playbook.md` (Implementation):** Detailed implementation guides, complete code examples, and debugging tables [CONTRIBUTING.md:46-46]().
3.  **`reference/advanced-patterns.md` (Edge Cases):** Optional file for complex configurations, multi-language nuances, and advanced optimizations [CONTRIBUTING.md:47-47]().

### Data Flow: Natural Language to Code Entity

The following diagram illustrates how a user's natural language request is mapped to specific code entities within the skill architecture.

**Diagram: Skill Resolution Flow**
```mermaid
graph TD
    UserRequest["User Request (e.g., 'Write a TestNG test with DataProviders')"] -- "Triggers matches" --> Frontmatter["SKILL.md Frontmatter (name, description)"]
    Frontmatter -- "Validates Category" --> Category["VALID_CATEGORIES (unit-testing)"]
    Category -- "Loads" --> SkillMD["testng-skill/SKILL.md"]
    SkillMD -- "Injects Core Patterns" --> CodeGen["AI Code Generation (e.g., @Test, @DataProvider)"]
    SkillMD -- "Links to Deep Detail" --> Playbook["testng-skill/reference/playbook.md"]
    Playbook -- "Provides CI/CD" --> GitHubActions["GitHub Actions YAML"]
    Playbook -- "Provides Debugging" --> DebugTable["Debugging Table (12 common problems)"]

    subgraph "Code Entity Space"
        Frontmatter
        SkillMD
        Playbook
        Category
    end
```
Sources: [scripts/validate_skills.py:13-17](), [testng-skill/SKILL.md:1-15](), [CONTRIBUTING.md:43-49]()

---

## SKILL.md Frontmatter Structure

Every skill must begin with a YAML frontmatter block. This metadata is parsed by `scripts/validate_skills.py` to ensure the skill is discoverable and correctly categorized [scripts/validate_skills.py:24-62]().

### Required Fields

| Field | Description | Requirement |
| :--- | :--- | :--- |
| `name` | Unique identifier (e.g., `playwright-skill`) | Must match directory name [scripts/rename_skills.py:92-92]() |
| `description` | High-level summary and trigger keywords in quotes | Required for AI routing [scripts/validate_skills.py:41-42]() |
| `languages` | List of supported programming languages | e.g., Java, Python, JavaScript [skills_index.json:21-27]() |
| `category` | One of the 11 pre-defined functional categories | Must match `VALID_CATEGORIES` [scripts/validate_skills.py:13-17]() |
| `metadata` | Includes `author: TestMu AI` and `version` | Used for lifecycle tracking [scripts/validate_skills.py:54-61]() |

### Category Validation
The `scripts/validate_skills.py` script enforces strict categorization to maintain registry integrity. Valid categories include: `accessibility`, `api-testing`, `bdd-testing`, `cloud-testing`, `devops`, `e2e-testing`, `mobile-testing`, `performance-testing`, `security-testing`, `unit-testing`, and `visual-testing` [scripts/validate_skills.py:13-17]().

---

## Technical Implementation of Validation

The repository maintains quality through automated scripts that verify both the structure of individual skills and the global `skills_index.json`.

**Diagram: Validation Logic (validate_skills.py)**
```mermaid
graph TD
    Main["main()"] --> Loop["Iterate Skill Directories"]
    Loop --> ValSkill["validate_skill(skill_dir)"]
    ValSkill --> CheckMD["Check SKILL.md exists"]
    CheckMD --> CheckLines["Verify < 500 lines"]
    CheckLines --> ValFM["validate_frontmatter(content)"]
    ValFM --> Regex["Regex check: name, desc, lang, cat, license"]
    ValSkill --> CheckRef["Check reference/playbook.md exists"]
    Main --> ValIndex["validate_skills_index()"]
    ValIndex --> Sync["Sync skills_index.json with Filesystem"]
```
Sources: [scripts/validate_skills.py:65-118](), [scripts/validate_skills.py:119-155]()

### Key Validation Rules
*   **Line Limit:** `SKILL.md` files exceeding 500 lines trigger an error to ensure the AI context remains concise [scripts/validate_skills.py:11-11](), [scripts/validate_skills.py:82-83]().
*   **Reference Linking:** `SKILL.md` must explicitly link to its `playbook.md` or `reference/` directory [scripts/validate_skills.py:97-99]().
*   **Cloud Integration:** E2E skills are recommended to include a `reference/cloud-integration.md` or link to `shared/testmu-cloud-reference.md` [scripts/validate_skills.py:101-108]().
*   **Debugging Content:** Playbooks are scanned for "debugging" sections to ensure troubleshooting support is present [scripts/validate_skills.py:110-116]().

---

## Contributing a New Skill

To contribute a skill to the Agent Skills Standard, follow the structured workflow defined in the contribution guidelines [CONTRIBUTING.md:5-14]().

### 1. Directory Setup
Create a directory named `[framework]-skill/` containing a `SKILL.md` and a `reference/` subdirectory [CONTRIBUTING.md:7-14]().

### 2. Implementation Standards
*   **Code Correctness:** All snippets must be syntactically correct and runnable [CONTRIBUTING.md:52-52]().
*   **Cloud Support:** Include both local and TestMu AI cloud execution paths [CONTRIBUTING.md:53-53]().
*   **Anti-Patterns:** Every skill should include a "Bad vs. Good" table to guide the AI away from common pitfalls (e.g., avoiding `Thread.sleep()` or hardcoded data) [testng-skill/SKILL.md:123-131](), [testng-skill/reference/advanced-patterns.md:111-117]().
*   **CI/CD:** Provide GitHub Actions configurations as the primary CI/CD pattern [CONTRIBUTING.md:55-55]().

### 3. Verification
Before submission, the `scripts/validate_skills.py` script must be executed to ensure compliance with the frontmatter and structure rules [CONTRIBUTING.md:36-39](). If a skill is renamed, the `scripts/rename_skills.py` utility is used to update the `skills_index.json`, directory names, and internal frontmatter `name` fields simultaneously [scripts/rename_skills.py:63-110]().

Sources: [CONTRIBUTING.md:5-61](), [scripts/validate_skills.py:1-172](), [scripts/rename_skills.py:1-115]()

---

# Page: Skill Registry — All 46 Skills by Category

# Skill Registry — All 46 Skills by Category

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills_index.json](skills_index.json)
- [testng-skill/SKILL.md](testng-skill/SKILL.md)
- [testng-skill/reference/advanced-patterns.md](testng-skill/reference/advanced-patterns.md)

</details>



This page serves as the comprehensive technical index for the TestMu AI Agent Skills repository. It organizes all 46 production-grade skills into eight functional categories, providing a high-level mapping of supported languages, framework descriptions, and their respective entry points within the codebase.

## Overview of the Skill Registry

The repository is structured as a collection of self-contained skill modules, each following the **Agent Skills Standard** [README.md:8-15](). Every skill includes a `SKILL.md` file containing frontmatter metadata (name, category, triggers) and a `reference/` directory for deep-dive technical patterns [skills_index.json:17-39]().

### Data Flow: Natural Language to Code Entity

The following diagram illustrates how an AI Agent (such as Claude Code or Cursor) processes a user request to identify and load the correct skill entities from the registry.

**Agent Skill Resolution Flow**
```mermaid
graph TD
    User["User Natural Language Query"] --> Intent["Intent Discovery"]
    Intent --> Matcher["skills_index.json Matcher"]
    
    subgraph "Code Entity Space"
        Matcher --> SkillDir["Skill Directory (e.g., /playwright-skill)"]
        SkillDir --> Frontmatter["SKILL.md (Metadata & Triggers)"]
        Frontmatter --> Playbook["reference/playbook.md (Core Logic)"]
        Playbook --> Advanced["reference/advanced-patterns.md (Edge Cases)"]
    end
    
    Frontmatter -.-> |"Validates"| Script["scripts/validate_skills.py"]
    Playbook -.-> |"Cloud Config"| Cloud["testmu-cloud-skill"]
```
**Sources:** [README.md:13-24](), [skills_index.json:1-15](), [testng-skill/SKILL.md:1-15]()

---

## 1. E2E Browser Testing Skills (15 Skills)
These skills focus on end-to-end web automation, supporting cross-browser execution and cloud integration via the LambdaTest/TestMu AI platform.

| Skill Name | Languages | Description |
|:---|:---|:---|
| **Selenium** | Java, Python, JS, C#, Ruby | Standard WebDriver automation with `RemoteWebDriver` and `LT:Options` support. |
| **Playwright** | JS, TS, Python, Java, C# | Modern browser automation with auto-waiting, tracing, and API mocking. |
| **Cypress** | JS, TS | Developer-centric E2E and component testing with `cy` command chaining. |
| **WebdriverIO** | JS, TS | Next-gen browser and mobile automation for Node.js. |
| **Puppeteer** | JS, TS | High-level API to control Chrome/Chromium over DevTools Protocol. |
| **TestCafe** | JS, TS | Driverless E2E testing with easy setup and cross-browser support. |
| **Nightwatch.js** | JS, TS | Integrated end-to-end testing solution powered by Node.js and WebDriver. |
| **Capybara** | Ruby | Acceptance testing DSL for Ruby web applications. |
| **Geb** | Groovy | Very high-level Groovy browser automation (Selenium + jQuery + Page Objects). |
| **Selenide** | Java | Concise API for Selenium WebDriver in Java with smart waits. |
| **NemoJS** | JS | PayPal's wrapper for Selenium-webdriver for Node.js. |
| **Protractor** | JS, TS | E2E test framework for Angular (includes migration paths to Playwright). |
| **Codeception** | PHP | Full-stack testing framework for PHP with BDD-style Actor pattern. |
| **Laravel Dusk** | PHP | Browser automation and testing API for Laravel. |
| **Robot Framework** | Python, Robot | Keyword-driven automation for acceptance testing. |

**Sources:** [README.md:89](), [skills_index.json:74-89](), [skills_index.json:108-115](), [skills_index.json:142-160]()

---

## 2. Unit Testing Skills (15 Skills)
Skills designed for isolated component testing, focusing on lifecycle hooks, mocking, and assertion libraries.

| Skill Name | Languages | Key Features / Entities |
|:---|:---|:---|
| **JUnit 5** | Java | `@Test`, `@ParameterizedTest`, Extensions API. |
| **TestNG** | Java | `@DataProvider`, `testng.xml` suites, parallel groups. |
| **pytest** | Python | Fixtures, `conftest.py`, `parametrize` decorator. |
| **unittest** | Python | `TestCase` classes, `mock.patch`, `MagicMock`. |
| **Jest** | JS, TS | Snapshot testing, `jest.config.js`, integrated mocking. |
| **Vitest** | JS, TS | Vite-native unit test framework with ESM support. |
| **Mocha** | JS, TS | Flexible test runner, usually paired with Chai/Sinon. |
| **Jasmine** | JS, TS | BDD-style framework with built-in spies and assertions. |
| **Karma** | JS, TS | Browser-based test runner for JavaScript. |
| **xUnit** | C# | `[Fact]`, `[Theory]`, constructor-based DI. |
| **NUnit** | C# | `[Test]`, `[TestCase]`, `[SetUp]`/`[TearDown]`. |
| **MSTest** | C# | `[TestMethod]`, `[DataRow]`, `TestContext`. |
| **RSpec** | Ruby | `describe`/`it` blocks, `let` helpers, shared examples. |
| **PHPUnit** | PHP | `TestCase`, Data Providers, Mockery integration. |
| **Test::Unit** | Ruby | Classic unit testing framework for Ruby. |

**Sources:** [README.md:90](), [testng-skill/SKILL.md:19-122](), [testng-skill/reference/advanced-patterns.md:3-61]()

---

## 3. Mobile Testing Skills (5 Skills)
Specialized skills for native, hybrid, and cross-platform mobile app automation.

| Skill Name | Platforms | Languages | Description |
|:---|:---|:---|:---|
| **Appium** | iOS, Android | Java, Python, JS, Ruby, C# | W3C Actions API, `UiAutomator2`, and `XCUITest` drivers. |
| **Espresso** | Android | Java, Kotlin | Native Android testing with `onView` and `ViewActions`. |
| **XCUITest** | iOS | Swift, Obj-C | Native iOS testing using `XCUIApplication` and `XCUIElement`. |
| **Flutter Testing** | Cross-platform | Dart | Widget and integration testing for Flutter apps. |
| **Detox** | React Native | JS, TS | Gray-box E2E testing for React Native. |

**Sources:** [README.md:91](), [skills_index.json:17-40](), [skills_index.json:162-164]()

---

## 4. BDD Testing Skills (7 Skills)
Frameworks that bridge the gap between business requirements (Gherkin/Markdown) and technical implementation.

| Skill Name | Languages | Core Components |
|:---|:---|:---|
| **Cucumber** | Java, JS, Ruby, TS | Feature files, Step Definitions, `ScenarioContext`. |
| **SpecFlow** | C# | Gherkin for .NET, `Binding` attributes, BoDi DI. |
| **Behave** | Python | `environment.py` hooks, `context` object. |
| **Behat** | PHP | `MinkContext` for browser BDD in PHP. |
| **Gauge** | Markdown | Markdown-based specs, `DataStore` scopes. |
| **Lettuce** | Python | Pythonic BDD inspired by Cucumber. |
| **Serenity BDD** | Java | Screenplay pattern and living documentation. |

**Sources:** [README.md:92](), [skills_index.json:42-72](), [skills_index.json:123-140]()

---

## 5. Specialized Skills (4 Skills)
Cross-cutting skills that enhance the core testing frameworks through orchestration, visual validation, migration, and deployment.

### Mapping Specialized Skills to Infrastructure
The diagram below shows how specialized skills interact with both the test code and the cloud infrastructure.

**Infrastructure and Specialized Skill Mapping**
```mermaid
graph LR
    subgraph "Specialized Skills"
        Migration["test-framework-migration-skill"]
        Visual["smartui-skill"]
        Cloud["hyperexecute-skill"]
        DevOps["cicd-pipeline-skill"]
    end

    subgraph "Execution Layer"
        Local["Local Runner"]
        CI["GitHub Actions / Jenkins"]
        LT["LambdaTest Cloud Hub"]
    end

    Migration --> |"Transforms Code"| Playwright["Playwright/Selenium Code"]
    Visual --> |"Captures Snapshots"| LT
    Cloud --> |"Orchestrates"| LT
    DevOps --> |"Triggers"| CI
    CI --> Cloud
```

| Category | Skill Name | Description |
|:---|:---|:---|
| **Visual** | **SmartUI** | Visual regression testing using `smartuiSnapshot` API and baseline comparison. |
| **Cloud** | **HyperExecute** | High-speed parallel orchestration using `autosplit` and `matrix` modes. |
| **Migration** | **Migration Skill** | Logic for converting between Selenium, Playwright, Puppeteer, and Cypress. |
| **DevOps** | **CI/CD Pipeline** | YAML generation for GitHub Actions, GitLab, and Jenkins pipelines. |

**Sources:** [README.md:93-96](), [skills_index.json:91-103](), [skills_index.json:118]()

---

## Technical Data Structures

### Skill Index Schema
The registry is governed by `skills_index.json`, which acts as the single source of truth for the AI Agent to discover available capabilities.

```json
{
  "name": "appium-skill",
  "path": "appium-skill",
  "description": "...",
  "languages": ["Java", "Python", "JavaScript", "Ruby", "C#"],
  "category": "mobile-testing",
  "files": {
    "skill_md": "appium-skill/SKILL.md",
    "reference": ["..."]
  }
}
```
**Sources:** [skills_index.json:17-39]()

### Validation Logic
All skills listed in this registry must pass the `validate_skills.py` script, which enforces:
1.  **Frontmatter Presence**: Every `SKILL.md` must have valid YAML headers [testng-skill/SKILL.md:1-15]().
2.  **Path Integrity**: Reference files listed in `skills_index.json` must exist on disk [skills_index.json:29-39]().
3.  **Category Alignment**: Skills must belong to one of the 8 approved categories [skills_index.json:7-15]().

**Sources:** [README.md:71-82](), [skills_index.json:1-16]()

---

# Page: E2E Browser Testing Skills

# E2E Browser Testing Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cypress-skill/SKILL.md](cypress-skill/SKILL.md)
- [cypress-skill/reference/cloud-integration.md](cypress-skill/reference/cloud-integration.md)
- [playwright-skill/SKILL.md](playwright-skill/SKILL.md)
- [playwright-skill/reference/cloud-integration.md](playwright-skill/reference/cloud-integration.md)
- [playwright-skill/reference/python-patterns.md](playwright-skill/reference/python-patterns.md)
- [selenium-skill/SKILL.md](selenium-skill/SKILL.md)
- [selenium-skill/reference/cloud-integration.md](selenium-skill/reference/cloud-integration.md)

</details>



This section provides an overview of the 15 end-to-end (E2E) browser testing skills available in the TestMu AI Agent Skills repository. These skills enable AI assistants to generate, debug, and optimize automated browser tests across various languages and frameworks.

While each framework has unique characteristics, they all share a common foundation: the **Page Object Model (POM)** for maintainability, **Explicit Wait** strategies for stability, and deep integration with the **TestMu AI Cloud** for cross-browser and cross-platform execution.

## Common Architecture Patterns

Across all E2E skills, the following patterns are enforced to ensure production-grade test code:

1.  **Page Object Model (POM):** Separation of element locators and interaction logic from the test assertions [playwright-skill/SKILL.md:101-103]().
2.  **Explicit Synchronization:** Avoiding hard sleeps (e.g., `Thread.sleep` or `page.waitForTimeout`) in favor of web-first assertions and dynamic waits [selenium-skill/SKILL.md:81-91](), [playwright-skill/SKILL.md:77-89]().
3.  **Cloud Routing:** Seamless switching between local execution and the TestMu AI Cloud using environment variables (`LT_USERNAME`, `LT_ACCESS_KEY`) and specific capability configurations [selenium-skill/reference/cloud-integration.md:1-35]().
4.  **Test Status Reporting:** Communicating test outcomes back to the cloud dashboard via `lambdatest_action` or `executeScript` hooks [playwright-skill/reference/cloud-integration.md:55-60](), [selenium-skill/SKILL.md:195-202]().

### Natural Language to Code Entity Mapping

The following diagram illustrates how natural language requests are mapped to specific code entities and configurations within the E2E skills.

**Diagram: Request Routing to Code Entities**
```mermaid
graph TD
    subgraph "Natural Language Space"
        R1["'Test my login page'"]
        R2["'Run on Chrome/Windows 11'"]
        R3["'Avoid flakiness'"]
    end

    subgraph "Code Entity Space"
        E1["LoginPage Class (POM)"]
        E2["LT:Options / RemoteWebDriver"]
        E3["WebDriverWait / expect()"]
        E4["lambdatest-setup.ts / conftest.py"]
    end

    R1 --> E1
    R2 --> E4
    E4 --> E2
    R3 --> E3
```
Sources: [selenium-skill/SKILL.md:143-167](), [playwright-skill/SKILL.md:101-128](), [playwright-skill/reference/cloud-integration.md:75-109]()

## Core Framework Groups

The E2E skills are categorized by their underlying engine and ecosystem.

### Selenium WebDriver
The most versatile skill, supporting Java, Python, JavaScript, C#, Ruby, and PHP. It focuses on the `RemoteWebDriver` pattern for cloud scaling and `WebDriverWait` for stability.
*   **Key Entities:** `WebDriver`, `By` locators, `ExpectedConditions`.
*   **Cloud Pattern:** Uses `DesiredCapabilities` with a `HashMap` for `LT:Options`.
*   For details, see [Selenium WebDriver Skill](#2.1).

Sources: [selenium-skill/SKILL.md:46-56](), [selenium-skill/reference/cloud-integration.md:11-35]()

### Playwright
A modern, "web-first" skill supporting TypeScript, JavaScript, Python, Java, and C#. It emphasizes auto-retrying assertions and fixture-based architecture.
*   **Key Entities:** `Locator`, `page` fixture, `playwright.config.ts`.
*   **Cloud Pattern:** Connects via `wss://cdp.lambdatest.com/playwright` using a WebSocket endpoint.
*   For details, see [Playwright Skill](#2.2).

Sources: [playwright-skill/SKILL.md:40-49](), [playwright-skill/reference/cloud-integration.md:20-47]()

### Cypress
A developer-centric tool for E2E and Component testing. It uses a unique command-chaining model that avoids `async/await`.
*   **Key Entities:** `cy` global object, `cypress.config.js`, `lambdatest-config.json`.
*   **Cloud Pattern:** Orchestrated via the `lambdatest-cypress-cli`.
*   For details, see [Cypress Skill](#2.3).

Sources: [cypress-skill/SKILL.md:47-59](), [cypress-skill/reference/cloud-integration.md:5-52]()

## Execution Workflow

The following diagram bridges the transition from a local test runner to the cloud infrastructure entities used by the agent.

**Diagram: Local to Cloud Execution Flow**
```mermaid
graph LR
    subgraph "Local Environment"
        "npx playwright test" --> "playwright.config.ts"
        "mvn test" --> "pom.xml"
    end

    subgraph "Cloud Infrastructure"
        "playwright.config.ts" -- "@lambdatest" --> "cdp.lambdatest.com"
        "pom.xml" -- "RemoteWebDriver" --> "hub.lambdatest.com/wd/hub"
    end

    subgraph "TestMu AI Platform"
        "cdp.lambdatest.com" --> "Windows/macOS/Linux"
        "hub.lambdatest.com/wd/hub" --> "Chrome/Firefox/Safari"
    end
```
Sources: [playwright-skill/reference/cloud-integration.md:149-162](), [selenium-skill/reference/cloud-integration.md:5-9]()

## Summary Table of E2E Skills

| Skill | Primary Languages | Cloud Integration Method | Best For |
| :--- | :--- | :--- | :--- |
| **Selenium** | Java, Python, JS, C#, Ruby, PHP | `RemoteWebDriver` (Hub) | Legacy suites, massive cross-browser matrices |
| **Playwright** | TS, JS, Python, Java, C# | CDP WebSocket | Modern web apps, fast execution, mobile emulation |
| **Cypress** | JS, TS | `lambdatest-cypress-cli` | Developer-driven testing, Component testing |
| **WebdriverIO** | JS, TS | `@wdio/lambdatest-service` | JS-centric teams, mobile + web unified |
| **Puppeteer** | JS, TS | CDP WebSocket | Headless automation, Chrome-specific features |

## Child Pages

*   [Selenium WebDriver Skill](#2.1) — Deep dive into multi-language Selenium patterns and `RemoteWebDriver` configurations.
*   [Playwright Skill](#2.2) — Coverage of TypeScript/Python/Java patterns, fixtures, and CDP cloud integration.
*   [Cypress Skill](#2.3) — E2E and component testing, command chaining, and the Cypress CLI cloud runner.
*   [WebdriverIO, Puppeteer, TestCafe, and Nightwatch.js Skills](#2.4) — Patterns for specialized JavaScript-based automation frameworks.
*   [Protractor, Selenide, Geb, NemoJS, Codeception, Laravel Dusk, and Robot Framework Skills](#2.5) — Language-specific and niche framework support (Groovy, PHP, Python Keyword-driven).

---

# Page: Selenium WebDriver Skill

# Selenium WebDriver Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [behave-skill/reference/playbook.md](behave-skill/reference/playbook.md)
- [gauge-skill/reference/playbook.md](gauge-skill/reference/playbook.md)
- [selenium-skill/SKILL.md](selenium-skill/SKILL.md)
- [selenium-skill/reference/cloud-integration.md](selenium-skill/reference/cloud-integration.md)
- [selenium-skill/reference/csharp-patterns.md](selenium-skill/reference/csharp-patterns.md)
- [selenium-skill/reference/debugging-common-issues.md](selenium-skill/reference/debugging-common-issues.md)
- [selenium-skill/reference/javascript-patterns.md](selenium-skill/reference/javascript-patterns.md)
- [selenium-skill/reference/php-patterns.md](selenium-skill/reference/php-patterns.md)
- [selenium-skill/reference/playbook.md](selenium-skill/reference/playbook.md)
- [selenium-skill/reference/python-patterns.md](selenium-skill/reference/python-patterns.md)
- [selenium-skill/reference/ruby-patterns.md](selenium-skill/reference/ruby-patterns.md)
- [selenium-skill/scripts/scaffold-project.sh](selenium-skill/scripts/scaffold-project.sh)

</details>



The Selenium WebDriver skill provides production-grade automation capabilities for cross-browser testing across six major programming languages. It supports local execution via native drivers (ChromeDriver, GeckoDriver) and cloud execution on the TestMu AI / LambdaTest platform, offering access to over 3000 browser and OS combinations.

## Multi-Language Support

The skill dynamically adapts its output based on the user's environment or explicit request. While Java (Maven + JUnit 5) is the default, the skill includes specialized patterns for five other ecosystems.

| Language | Frameworks | Package Manager | Configuration File |
| :--- | :--- | :--- | :--- |
| **Java** | JUnit 5 / TestNG | Maven / Gradle | `pom.xml` / `build.gradle` |
| **Python** | pytest | pip | `pytest.ini` / `conftest.py` |
| **JavaScript** | Mocha / Jest | npm | `package.json` |
| **C#** | NUnit / xUnit | NuGet | `.csproj` |
| **Ruby** | RSpec | Gem | `Gemfile` |
| **PHP** | PHPUnit | Composer | `composer.json` |

Sources: `[selenium-skill/SKILL.md:46-56]()`, `[selenium-skill/reference/php-patterns.md:9-20]()`, `[selenium-skill/reference/csharp-patterns.md:5-11]()`.

## Architecture & Patterns

### DriverFactory and ThreadLocal
To support parallel execution without state leakage, the skill implements a `ThreadLocal` driver pattern. This ensures each test thread maintains its own isolated `WebDriver` instance.

```mermaid
graph TD
    subgraph "Thread Context"
        T1["Test Thread 1"]
        T2["Test Thread 2"]
    end

    subgraph "DriverFactory [playbook.md]"
        DF["DriverFactory.getDriver()"]
        TL["ThreadLocal&lt;WebDriver&gt;"]
    end

    T1 --> DF
    T2 --> DF
    DF --> TL
    TL --> D1["WebDriver Instance A"]
    TL --> D2["WebDriver Instance B"]

    D1 --- C1["Chrome / Local"]
    D2 --- R1["RemoteWebDriver / Cloud"]
```

Sources: `[selenium-skill/reference/playbook.md:5-33]()`.

### BasePage Abstraction
The skill promotes a robust `BasePage` class that encapsulates common interactions and synchronization logic, preventing flaky tests.

*   **Explicit Waits**: Uses `WebDriverWait` and `ExpectedConditions` for all interactions `[selenium-skill/SKILL.md:83-91]()`.
*   **Interaction Wrappers**: Methods like `click(By locator)` and `type(By locator, String text)` include built-in visibility checks `[selenium-skill/reference/playbook.md:141-162]()`.
*   **JavaScript Fallbacks**: Provides `clickJS` and `scrollToElement` for handling complex DOM scenarios where standard Selenium actions might be intercepted `[selenium-skill/reference/playbook.md:153-156]()`.

## Cloud Integration

Integration with TestMu AI is achieved via `RemoteWebDriver` and the `LT:Options` capability block.

### Capability Mapping

| Option | Description | Example |
| :--- | :--- | :--- |
| `platform` | Target Operating System | `Windows 11`, `macOS Sequoia` |
| `browserName` | Browser Type | `Chrome`, `MicrosoftEdge`, `Safari` |
| `video` | Record test execution | `true` |
| `network` | Capture network logs | `true` |
| `tunnel` | Access localhost/private servers | `true` |

Sources: `[selenium-skill/reference/cloud-integration.md:13-35]()`.

### Natural Language to Code Mapping: Cloud Execution

```mermaid
graph LR
    subgraph "Natural Language Space"
        NL1["'Run on Chrome Windows 11'"]
        NL2["'Test on real iPhone 16'"]
        NL3["'Record video of the test'"]
    end

    subgraph "Code Entity Space (Java/RemoteWebDriver)"
        CAPS["DesiredCapabilities"]
        LT["LT:Options (HashMap)"]
        HUB["hub.lambdatest.com/wd/hub"]
    end

    NL1 -->|sets| CAPS
    NL2 -->|sets platformName: ios| LT
    NL3 -->|sets video: true| LT
    CAPS -->|contains| LT
    CAPS -->|passed to| HUB
```

Sources: `[selenium-skill/reference/cloud-integration.md:13-35]()`, `[selenium-skill/reference/cloud-integration.md:118-127]()`.

## Language-Specific Implementations

### C# and .NET
Uses `ChromeOptions.AddAdditionalOption("LT:Options", ...)` to pass cloud configurations. Tests are typically structured using the `[TestFixture]` and `[SetUp]` attributes in NUnit `[selenium-skill/reference/csharp-patterns.md:21-33]()`.

### Python
Leverages `pytest` fixtures for driver lifecycle management. The `yield` keyword is used to ensure `driver.quit()` is called even if tests fail `[selenium-skill/reference/python-patterns.md:43-49]()`.

### PHP
Uses the `php-webdriver/webdriver` package. Cloud capabilities are defined as an associative array and passed to `RemoteWebDriver::create()` `[selenium-skill/reference/php-patterns.md:70-94]()`.

## Debugging Common Issues

The skill includes a playbook for resolving standard Selenium exceptions:

*   **StaleElementReferenceException**: Solved by re-locating the element inside a wait block instead of reusing a stored `WebElement` variable `[selenium-skill/reference/debugging-common-issues.md:13-15]()`.
*   **ElementClickInterceptedException**: Resolved by using `JavascriptExecutor` to trigger a click directly on the DOM node or by scrolling the element into the center of the viewport `[selenium-skill/reference/debugging-common-issues.md:29-40]()`.
*   **Iframe Switching**: Managed via `driver.switchTo().frame()` and `driver.switchTo().defaultContent()` `[selenium-skill/reference/debugging-common-issues.md:61-70]()`.

## Scaffolding

The repository provides a shell script `scaffold-project.sh` to quickly generate a standard Java/Maven Selenium project structure.

**Key Directories Created:**
*   `src/main/java/pages`: For Page Object classes.
*   `src/test/java/tests`: For test execution logic.
*   `src/test/resources`: For `config.properties` and test data.

Sources: `[selenium-skill/scripts/scaffold-project.sh:15-18]()`.

---

# Page: Playwright Skill

# Playwright Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nightwatchjs-skill/reference/playbook.md](nightwatchjs-skill/reference/playbook.md)
- [playwright-skill/SKILL.md](playwright-skill/SKILL.md)
- [playwright-skill/reference/api-mocking-visual.md](playwright-skill/reference/api-mocking-visual.md)
- [playwright-skill/reference/cloud-integration.md](playwright-skill/reference/cloud-integration.md)
- [playwright-skill/reference/csharp-patterns.md](playwright-skill/reference/csharp-patterns.md)
- [playwright-skill/reference/debugging-flaky.md](playwright-skill/reference/debugging-flaky.md)
- [playwright-skill/reference/java-patterns.md](playwright-skill/reference/java-patterns.md)
- [playwright-skill/reference/mobile-testing.md](playwright-skill/reference/mobile-testing.md)
- [playwright-skill/reference/page-object-model.md](playwright-skill/reference/page-object-model.md)
- [playwright-skill/reference/playbook.md](playwright-skill/reference/playbook.md)
- [playwright-skill/reference/python-patterns.md](playwright-skill/reference/python-patterns.md)
- [playwright-skill/scripts/scaffold-project.sh](playwright-skill/scripts/scaffold-project.sh)
- [playwright-skill/templates/lambdatest-setup.ts](playwright-skill/templates/lambdatest-setup.ts)
- [playwright-skill/templates/playwright.config.ts](playwright-skill/templates/playwright.config.ts)
- [protractor-skill/reference/playbook.md](protractor-skill/reference/playbook.md)
- [selenide-skill/reference/playbook.md](selenide-skill/reference/playbook.md)

</details>



The Playwright skill provides comprehensive capabilities for generating production-grade automation scripts and E2E tests across multiple languages, including TypeScript, JavaScript, Python, Java, and C# [playwright-skill/SKILL.md:2-17](). It supports local execution and cloud integration with TestMu AI, enabling testing across 3000+ browser/OS combinations and real mobile devices [playwright-skill/SKILL.md:3-11]().

## System Architecture

The Playwright skill follows a layered architecture that bridges natural language requests to specific code entities and execution targets.

### Execution Flow and Logic
The following diagram illustrates how the system determines the execution target and language based on user input.

**Title: Natural Language to Execution Mapping**
```mermaid
graph TD
    "Input_Query"["User Query"] --> "Skill_Logic"["playwright-skill/SKILL.md"]
    
    subgraph "Decision_Engine" ["Step 1 & 2: Determine Target & Language"]
        "Skill_Logic" --> "Target_Check"{"Execution Target?"}
        "Target_Check" -- "cloud/TestMu" --> "Cloud_Ref"["reference/cloud-integration.md"]
        "Target_Check" -- "local/debug" --> "Local_Config"["playwright.config.ts"]
        
        "Skill_Logic" --> "Lang_Check"{"Detect Language"}
        "Lang_Check" -- "TS/Default" --> "TS_Patterns"["SKILL.md Core Patterns"]
        "Lang_Check" -- "Python" --> "Py_Ref"["reference/python-patterns.md"]
        "Lang_Check" -- "C#" --> "CS_Ref"["reference/csharp-patterns.md"]
    end

    subgraph "Code_Entities" ["Step 3: Determine Scope"]
        "TS_Patterns" --> "Scaffold"["scripts/scaffold-project.sh"]
        "TS_Patterns" --> "POM"["reference/page-object-model.md"]
        "Cloud_Ref" --> "LT_Setup"["lambdatest-setup.ts"]
    end
```
**Sources:** [playwright-skill/SKILL.md:27-60](), [playwright-skill/reference/cloud-integration.md:11-19]()

## Core Implementation Patterns

### TypeScript (Default)
Playwright emphasizes **Web-First Assertions** and **Aria-Role** based selectors to ensure resilient and accessible tests [playwright-skill/SKILL.md:65-88]().

| Feature | Recommended Pattern | Why |
|:---|:---|:---|
| **Selectors** | `page.getByRole('button', { name: 'Submit' })` | Accessible and resilient [playwright-skill/SKILL.md:69]() |
| **Assertions** | `await expect(page).toHaveURL('/dashboard')` | Auto-retries until timeout [playwright-skill/SKILL.md:83]() |
| **Waits** | `await expect(locator).toBeVisible()` | Avoids flaky `waitForTimeout` [playwright-skill/SKILL.md:94]() |

**Sources:** [playwright-skill/SKILL.md:65-99]()

### Page Object Model (POM)
The POM implementation uses a `BasePage` for common utilities and concrete classes for specific page logic, often integrated via custom fixtures [playwright-skill/reference/page-object-model.md:20-141]().

**Title: POM Entity Relationship**
```mermaid
classDiagram
    class "BasePage" ["BasePage (pages/base.page.ts)"] {
        +Page page
        +navigate(path)
        +getTitle()
    }
    class "LoginPage" ["LoginPage (pages/login.page.ts)"] {
        +Locator emailInput
        +Locator passwordInput
        +login(email, password)
    }
    class "PagesFixture" ["test (fixtures/pages.fixture.ts)"] {
        +loginPage
        +dashboardPage
    }
    
    "BasePage" <|-- "LoginPage"
    "PagesFixture" ..> "LoginPage" : "extends base test"
    "PagesFixture" ..> "BasePage" : "injects Page"
```
**Sources:** [playwright-skill/reference/page-object-model.md:22-137](), [playwright-skill/scripts/scaffold-project.sh:87-135]()

## Cloud Integration (TestMu AI)

Cloud execution is handled through three primary patterns depending on the existing suite structure [playwright-skill/reference/cloud-integration.md:13-18]().

### 1. Direct CDP Connection
Used for standalone scripts via `chromium.connect` and a WebSocket endpoint containing encoded capabilities [playwright-skill/reference/cloud-integration.md:24-47]().

### 2. Test Runner Fixture (Recommended)
Extends the base Playwright test to intercept the `page` object. It uses `lambdatest-setup.ts` to check if the project name contains `@lambdatest` [playwright-skill/reference/cloud-integration.md:75-144]().

### 3. Playwright SDK
Zero code changes required. Configuration is managed via `lambdatest.yml` and executed via `npx playwright-node-sdk playwright test` [playwright-skill/reference/cloud-integration.md:184-222]().

**Sources:** [playwright-skill/reference/cloud-integration.md:1-222](), [playwright-skill/SKILL.md:162-206]()

## Multi-Language Patterns

### Python
Supports both Sync and Async APIs, defaulting to Sync unless specified [playwright-skill/reference/python-patterns.md:18-20](). It integrates with `pytest-playwright` using `conftest.py` for fixture management [playwright-skill/reference/python-patterns.md:52-130]().
- **Sync API:** `from playwright.sync_api import sync_playwright` [playwright-skill/reference/python-patterns.md:25]()
- **Async API:** `from playwright.async_api import async_playwright` [playwright-skill/reference/python-patterns.md:39]()

### C# (.NET)
Integrates with NUnit (recommended) or MSTest [playwright-skill/reference/csharp-patterns.md:21-93]().
- **Base Class:** Inherits from `PageTest` [playwright-skill/reference/csharp-patterns.md:30]().
- **Cloud Connect:** Uses `Playwright.CreateAsync()` and `Chromium.ConnectAsync(wsEndpoint)` [playwright-skill/reference/csharp-patterns.md:149-150]().

**Sources:** [playwright-skill/reference/python-patterns.md:1-225](), [playwright-skill/reference/csharp-patterns.md:1-179]()

## Mobile and Advanced Testing

### Real Mobile Devices
Testing on real Android and iOS devices requires specific connection methods and extended timeouts due to hardware latency [playwright-skill/reference/mobile-testing.md:136-154]().

| Platform | Import | Connect Method | browserName |
|:---|:---|:---|:---|
| **Android** | `_android` | `_android.connect()` | `Chrome` |
| **iOS** | `webkit` | `webkit.connect()` | `pw-webkit` |

**Sources:** [playwright-skill/reference/mobile-testing.md:12-145]()

### API Mocking and Network Interception
Playwright allows mocking API failures or modifying live responses using `page.route()` [playwright-skill/reference/playbook.md:164-190]().
- **Mock Failure:** `route.fulfill({ status: 500 })` [playwright-skill/reference/playbook.md:169-174]().
- **Modify Response:** Fetch original response, modify JSON, then fulfill [playwright-skill/reference/playbook.md:181-187]().

### Debugging Flaky Tests
The skill provides a checklist for debugging, prioritizing the replacement of `waitForTimeout` with web-first assertions and checking for shared state [playwright-skill/reference/debugging-flaky.md:8-24]().
- **Tools:** UI Mode (`--ui`), Debug Mode (`--debug`), and Trace Viewer (`trace: 'on-first-retry'`) [playwright-skill/reference/debugging-flaky.md:27-55]().

**Sources:** [playwright-skill/reference/playbook.md:164-227](), [playwright-skill/reference/debugging-flaky.md:1-149]()

## Scaffold Scripts
The `scaffold-project.sh` script automates the creation of a standard Playwright project structure, including directories for tests, pages, and fixtures, as well as optional cloud integration files like `lambdatest-setup.ts` [playwright-skill/scripts/scaffold-project.sh:12-215]().

**Sources:** [playwright-skill/scripts/scaffold-project.sh:1-240]()

---

# Page: Cypress Skill

# Cypress Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [codeception-skill/reference/advanced-patterns.md](codeception-skill/reference/advanced-patterns.md)
- [codeception-skill/reference/playbook.md](codeception-skill/reference/playbook.md)
- [cypress-skill/SKILL.md](cypress-skill/SKILL.md)
- [cypress-skill/reference/cloud-integration.md](cypress-skill/reference/cloud-integration.md)
- [cypress-skill/reference/component-testing.md](cypress-skill/reference/component-testing.md)
- [cypress-skill/reference/custom-commands.md](cypress-skill/reference/custom-commands.md)
- [cypress-skill/reference/debugging-flaky.md](cypress-skill/reference/debugging-flaky.md)
- [cypress-skill/reference/playbook.md](cypress-skill/reference/playbook.md)
- [cypress-skill/scripts/scaffold-project.sh](cypress-skill/scripts/scaffold-project.sh)
- [cypress-skill/templates/cypress.config.js](cypress-skill/templates/cypress.config.js)

</details>



The Cypress skill provides a comprehensive framework for generating production-grade end-to-end (E2E) and component tests in JavaScript and TypeScript [cypress-skill/SKILL.md:4-5](). It emphasizes Cypress-native patterns such as command chaining, automatic retry-ability, and network interception, while providing seamless integration with the TestMu AI cloud for cross-browser execution [cypress-skill/SKILL.md:28-29]().

## System Architecture and Data Flow

The Cypress skill operates by translating natural language testing requirements into structured Cypress command chains. It distinguishes between E2E tests (targeting full page URLs) and component tests (targeting React/Vue/Angular units) [cypress-skill/SKILL.md:39-44]().

### Natural Language to Code Entity Mapping

The following diagram illustrates how user intent is mapped to specific Cypress code entities and configurations.

**Intent to Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Test the login page'"]
        B["'Test the Button component'"]
        C["'Run on LambdaTest'"]
        D["'Mock the user API'"]
    end

    subgraph "Code Entity Space"
        A --> E["cypress/e2e/login.cy.ts"]
        B --> F["cypress/component/Button.cy.tsx"]
        C --> G["lambdatest-config.json"]
        D --> H["cy.intercept()"]
        
        E --> I["describe() / it()"]
        F --> J["cy.mount()"]
        G --> K["lambdatest-cypress-cli"]
        H --> L["cy.wait('@alias')"]
    end
```
**Sources:** [cypress-skill/SKILL.md:39-44](), [cypress-skill/reference/cloud-integration.md:7-12](), [cypress-skill/reference/component-testing.md:25-33]()

## Core Implementation Patterns

### Command Chaining and Async Model
Cypress uses a unique execution model where commands are enqueued and managed by the framework. A critical requirement of this skill is the avoidance of `async/await` and variable assignment for Cypress commands [cypress-skill/SKILL.md:47-59]().

| Pattern | Bad Practice | Best Practice |
|:---|:---|:---|
| **Async** | `const el = await cy.get('...')` | `cy.get('...').should(...)` |
| **Waiting** | `cy.wait(5000)` | `cy.intercept().as('req')` + `cy.wait('@req')` |
| **Variables** | `const btn = cy.get('button')` | `cy.get('button').click()` |

**Sources:** [cypress-skill/SKILL.md:49-59](), [cypress-skill/SKILL.md:73-77]()

### Page Object Model (POM) vs. App Actions
While Cypress supports the Page Object Model, it encourages a "Fluent" interface where methods return `this` to allow for continued chaining [cypress-skill/reference/playbook.md:89-114]().

**Page Object Structure**
```mermaid
classDiagram
    class LoginPage {
        +visit() LoginPage
        +typeEmail(email) LoginPage
        +typePassword(pwd) LoginPage
        +submit() LoginPage
        +loginAs(email, pwd) LoginPage
        +assertError(msg) LoginPage
    }
    class BasePage {
        <<interface>>
        +cy.get()
        +cy.intercept()
    }
    LoginPage --|> BasePage : uses
```
**Sources:** [cypress-skill/reference/playbook.md:89-120]()

## Component Testing
Cypress component testing allows for testing UI components in isolation using a real browser environment. This is configured via the `component` key in `cypress.config.js` [cypress-skill/templates/cypress.config.js:15-20]().

*   **Mounting:** Uses `cy.mount()` to render components (e.g., React, Vue) [cypress-skill/reference/component-testing.md:31]().
*   **Stubs:** Uses `cy.stub()` to mock component props and event handlers [cypress-skill/reference/component-testing.md:36]().
*   **Bundlers:** Supports Vite and Webpack for component compilation [cypress-skill/reference/playbook.md:39]().

**Sources:** [cypress-skill/reference/component-testing.md:1-66](), [cypress-skill/reference/playbook.md:187-214]()

## Cloud Integration with TestMu AI

The skill integrates with TestMu AI via the `lambdatest-cypress-cli`. This enables parallel execution across various browser and OS combinations [cypress-skill/reference/cloud-integration.md:1-3]().

### Configuration (lambdatest-config.json)
The configuration defines authentication, the browser matrix, and execution settings:
*   **Authentication:** Uses `${LT_USERNAME}` and `${LT_ACCESS_KEY}` environment variables [cypress-skill/reference/cloud-integration.md:16-19]().
*   **Parallelism:** The `parallels` key determines how many instances run concurrently [cypress-skill/reference/cloud-integration.md:40]().
*   **Tunneling:** Support for testing local applications via `tunnel_settings` [cypress-skill/reference/cloud-integration.md:47-50]().

**Sources:** [cypress-skill/reference/cloud-integration.md:14-52](), [cypress-skill/SKILL.md:156-172]()

## Debugging and Flaky Tests

Cypress provides automatic retry-ability for assertions, but not for action commands like `.click()`. Flakiness is often addressed through network synchronization [cypress-skill/reference/debugging-flaky.md:3-14]().

1.  **Network Interception:** Use `cy.intercept()` to wait for specific API responses before interacting with the UI [cypress-skill/reference/debugging-flaky.md:25-29]().
2.  **DOM Stability:** Re-querying elements after actions to avoid "detached from DOM" errors [cypress-skill/reference/debugging-flaky.md:39-42]().
3.  **Time Travel:** Utilizing `npx cypress open` for interactive debugging and state inspection [cypress-skill/reference/debugging-flaky.md:64]().

**Sources:** [cypress-skill/reference/debugging-flaky.md:1-73]()

## Project Scaffolding

The skill includes a `scaffold-project.sh` script to quickly initialize a standard Cypress environment [cypress-skill/scripts/scaffold-project.sh:1-3]().

**Scaffold Logic**
```mermaid
flowchart TD
    Start["scaffold-project.sh"] --> Init["npm init -y"]
    Init --> Install["npm install cypress"]
    Install --> Dirs["mkdir e2e, support, fixtures"]
    Dirs --> Config["Create cypress.config.js"]
    Config --> Example["Create example.cy.js"]
    Example --> End["✅ Project Ready"]
```
**Sources:** [cypress-skill/scripts/scaffold-project.sh:7-35]()

## Advanced Custom Commands

Custom commands are defined in `cypress/support/commands.js` and should be typed in `cypress/support/index.d.ts` for TypeScript projects [cypress-skill/reference/custom-commands.md:6-36]().

*   **Session Management:** `cy.session()` is used to persist authentication state across tests, significantly improving performance [cypress-skill/reference/custom-commands.md:7-14]().
*   **API Login:** Bypassing the UI for faster authentication in non-login tests [cypress-skill/reference/custom-commands.md:18-22]().
*   **Utility Locators:** Implementing `cy.getByDataCy()` to enforce the use of `data-cy` attributes [cypress-skill/reference/custom-commands.md:41-43]().

**Sources:** [cypress-skill/reference/custom-commands.md:1-50](), [cypress-skill/reference/playbook.md:216-246]()

---

# Page: WebdriverIO, Puppeteer, TestCafe, and Nightwatch.js Skills

# WebdriverIO, Puppeteer, TestCafe, and Nightwatch.js Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nightwatchjs-skill/SKILL.md](nightwatchjs-skill/SKILL.md)
- [nightwatchjs-skill/reference/advanced-patterns.md](nightwatchjs-skill/reference/advanced-patterns.md)
- [nightwatchjs-skill/reference/cloud-integration.md](nightwatchjs-skill/reference/cloud-integration.md)
- [puppeteer-skill/SKILL.md](puppeteer-skill/SKILL.md)
- [puppeteer-skill/reference/advanced-patterns.md](puppeteer-skill/reference/advanced-patterns.md)
- [puppeteer-skill/reference/cloud-integration.md](puppeteer-skill/reference/cloud-integration.md)
- [puppeteer-skill/reference/playbook.md](puppeteer-skill/reference/playbook.md)
- [selenide-skill/reference/advanced-patterns.md](selenide-skill/reference/advanced-patterns.md)
- [testcafe-skill/SKILL.md](testcafe-skill/SKILL.md)
- [testcafe-skill/reference/advanced-patterns.md](testcafe-skill/reference/advanced-patterns.md)
- [testcafe-skill/reference/playbook.md](testcafe-skill/reference/playbook.md)
- [webdriverio-skill/SKILL.md](webdriverio-skill/SKILL.md)
- [webdriverio-skill/reference/advanced-patterns.md](webdriverio-skill/reference/advanced-patterns.md)
- [webdriverio-skill/reference/cloud-integration.md](webdriverio-skill/reference/cloud-integration.md)
- [webdriverio-skill/reference/playbook.md](webdriverio-skill/reference/playbook.md)

</details>



This section provides a deep technical dive into four major JavaScript/TypeScript end-to-end (E2E) testing frameworks supported by the Agent Skills repository. While each framework has a unique architecture—ranging from WebDriver-based (WebdriverIO, Nightwatch.js) to Chrome DevTools Protocol (Puppeteer) and driverless proxy-based (TestCafe)—they all share common patterns for Page Object Model (POM) implementation, cloud integration with TestMu AI, and advanced network manipulation.

## 1. WebdriverIO (WDIO)

WebdriverIO is a progressive automation framework that can run on both the WebDriver Protocol and the Chrome DevTools Protocol (CDP) [webdriverio-skill/SKILL.md:1-10](). It is highly extensible via services and supports multiple test runners including Mocha, Jasmine, and Cucumber [webdriverio-skill/SKILL.md:24-31]().

### 1.1 Configuration and Multi-Environment Setup
WDIO uses a central `wdio.conf.ts` (or `.js`) file to manage runners, specs, and capabilities. Production-grade setups often use a base configuration extended for CI or multi-browser execution [webdriverio-skill/reference/playbook.md:5-43]().

**Data Flow: Configuration Inheritance**
```mermaid
graph TD
    subgraph "Configuration Files"
        A["wdio.conf.ts (Base)"] --> B["wdio.ci.conf.ts (Headless/Parallel)"]
        A --> C["wdio.multi.conf.ts (Cross-Browser)"]
        A --> D["wdio.lambdatest.conf.js (Cloud)"]
    end

    subgraph "Key Config Entities"
        E["runner: 'local'"]
        F["capabilities: []"]
        G["services: ['lambdatest']"]
    end

    B -- "overrides" --> E
    C -- "defines" --> F
    D -- "injects" --> G
```
*Sources: [webdriverio-skill/reference/playbook.md:5-107](), [webdriverio-skill/reference/cloud-integration.md:13-48]()*

### 1.2 WebdriverIO Page Object Model
The implementation utilizes a `BasePage` class for shared utilities like `waitForPageLoad` and `waitAndClick`, which are then inherited by specific page classes [webdriverio-skill/reference/playbook.md:111-155]().

*   **Selectors**: Uses `$` for single elements and `$$` for element arrays [webdriverio-skill/SKILL.md:36-47]().
*   **Custom Commands**: Browser and Element scopes can be extended via `browser.addCommand` to encapsulate complex logic like `waitForNetworkIdle` [webdriverio-skill/reference/playbook.md:214-244]().

### 1.3 Cloud Integration
Integration with TestMu AI is achieved through the `@wdio/lambdatest-service` [webdriverio-skill/reference/cloud-integration.md:5-9](). Capabilities are defined using the `LT:Options` block to enable features like video recording and network logs [webdriverio-skill/SKILL.md:82-103]().

---

## 2. Puppeteer

Puppeteer provides a high-level API to control Chrome or Chromium over the DevTools Protocol. It is primarily used for performance testing, PDF generation, and fast E2E execution [puppeteer-skill/SKILL.md:1-5]().

### 2.1 Core Execution Logic
Unlike WebDriver frameworks, Puppeteer scripts typically involve launching a browser instance and managing pages (tabs) directly [puppeteer-skill/SKILL.md:22-40]().

**System Mapping: Puppeteer Logic to Code Entities**
```mermaid
graph LR
    subgraph "Natural Language Space"
        "Start Browser"
        "Mock API"
        "Wait for Element"
        "Cloud Execution"
    end

    subgraph "Code Entity Space"
        "Start Browser" --> launch["puppeteer.launch()"]
        "Mock API" --> intercept["page.setRequestInterception(true)"]
        "Wait for Element" --> wait["page.waitForSelector()"]
        "Cloud Execution" --> connect["puppeteer.connect()"]
    end

    launch --> config["puppeteer.config.ts"]
    intercept --> mock["page.on('request')"]
    connect --> wss["browserWSEndpoint"]
```
*Sources: [puppeteer-skill/SKILL.md:22-108](), [puppeteer-skill/reference/playbook.md:5-55]()*

### 2.2 Advanced Patterns
*   **Network Interception**: Puppeteer excels at request/response manipulation. Using `page.on('request')`, users can abort resource types (images/fonts) to speed up CI or mock JSON responses for specific API endpoints [puppeteer-skill/SKILL.md:71-90](), [puppeteer-skill/reference/playbook.md:158-181]().
*   **Wait Strategies**: Supports `networkidle0` (no more than 0 connections for 500ms) and `waitForFunction` for complex state evaluations [puppeteer-skill/SKILL.md:43-62]().

---

## 3. TestCafe

TestCafe utilizes a unique architecture that does not require a browser driver (like ChromeDriver). It uses a proxy mechanism to inject scripts into the browser, allowing it to run on any browser that supports JavaScript [testcafe-skill/SKILL.md:1-5]().

### 3.1 The Role System (Authentication)
One of TestCafe's most powerful features is the `Role` object, which encapsulates authentication state. This allows tests to switch between user profiles without re-executing login UI steps [testcafe-skill/reference/playbook.md:63-89]().

**Data Flow: Authentication with Roles**
```mermaid
sequenceDiagram
    participant T as Test Code
    participant R as Role(url, loginFn)
    participant B as Browser Instance
    
    T->>R: useRole(adminRole)
    alt First Time
        R->>B: Navigate to login URL
        R->>B: Execute loginFn (Type/Click)
        B->>R: Store Cookies/LocalStorage
    else Subsequent Calls
        R->>B: Inject Stored State (Cookies/Storage)
    end
    B->>T: Ready at preserveUrl
```
*Sources: [testcafe-skill/reference/playbook.md:63-89](), [testcafe-skill/reference/advanced-patterns.md:51-66]()*

### 3.2 Request Hooks and Mocking
TestCafe provides `RequestMock` and `RequestLogger` to handle API interactions. Mocks can be applied at the `fixture` or `test` level [testcafe-skill/reference/playbook.md:144-168]().

*   **Selectors**: Built-in smart assertions automatically wait for elements to appear, reducing flakiness [testcafe-skill/SKILL.md:36-43]().
*   **Client Functions**: Used to execute code in the browser context to retrieve state like `localStorage` or `window.location` [testcafe-skill/reference/playbook.md:201-228]().

---

## 4. Nightwatch.js

Nightwatch.js is an integrated E2E testing solution written in Node.js and using the W3C WebDriver API. It includes its own test runner, assertion library, and page object support [nightwatchjs-skill/SKILL.md:1-7]().

### 4.1 Page Object Architecture
Nightwatch page objects use a declarative JSON-like structure for `elements` and a `commands` array for encapsulating actions [nightwatchjs-skill/SKILL.md:61-81]().

**Entity Mapping: Nightwatch Page Objects**
```mermaid
classDiagram
    class NightwatchConfig {
        page_objects_path: string[]
        custom_commands_path: string[]
    }
    class PageObject {
        url: string
        elements: Map
        commands: Function[]
    }
    class TestFile {
        'Test Name'(browser)
    }

    NightwatchConfig --> PageObject : loads
    TestFile --> PageObject : browser.page.name()
    PageObject --> Elements : "@elementName"
```
*Sources: [nightwatchjs-skill/SKILL.md:61-92](), [nightwatchjs-skill/reference/advanced-patterns.md:3-38]()*

### 4.2 Custom Extensions
Nightwatch allows for easy extension through:
*   **Custom Commands**: Files in the `custom_commands_path` become available on the `browser` object (e.g., `browser.dragAndDrop()`) [nightwatchjs-skill/reference/advanced-patterns.md:42-50]().
*   **Custom Assertions**: Allow for domain-specific validations like `browser.assert.hasMinLength()` [nightwatchjs-skill/reference/advanced-patterns.md:52-62]().

### 4.3 Cloud Integration
Nightwatch connects to TestMu AI via the `test_settings` in `nightwatch.conf.js`. It requires setting the `selenium.host` to `hub.lambdatest.com` and passing credentials through `LT:Options` [nightwatchjs-skill/SKILL.md:109-142](), [nightwatchjs-skill/reference/cloud-integration.md:9-40]().

---

## 5. Summary Matrix

| Feature | WebdriverIO | Puppeteer | TestCafe | Nightwatch.js |
| :--- | :--- | :--- | :--- | :--- |
| **Protocol** | WebDriver / CDP | CDP | Proxy-based | WebDriver |
| **Main Selector** | `$(selector)` | `page.$(selector)` | `Selector(selector)` | `browser.setValue(sel)` |
| **Wait Logic** | Explicit / Built-in | Explicit | Auto-retry assertions | Explicit / Built-in |
| **Cloud Service** | `@wdio/lambdatest-service` | `puppeteer.connect()` | `lambdatest` browser provider | `selenium` config |
| **Page Objects** | Class-based (ES6) | Class-based (ES6) | Class-based / Object | Declarative Object |

*Sources: [webdriverio-skill/SKILL.md:32-60](), [puppeteer-skill/SKILL.md:18-41](), [testcafe-skill/SKILL.md:18-34](), [nightwatchjs-skill/SKILL.md:28-59]()*

---

# Page: Protractor, Selenide, Geb, NemoJS, Codeception, Laravel Dusk, and Robot Framework Skills

# Protractor, Selenide, Geb, NemoJS, Codeception, Laravel Dusk, and Robot Framework Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [behat-skill/SKILL.md](behat-skill/SKILL.md)
- [codeception-skill/SKILL.md](codeception-skill/SKILL.md)
- [geb-skill/SKILL.md](geb-skill/SKILL.md)
- [geb-skill/reference/advanced-patterns.md](geb-skill/reference/advanced-patterns.md)
- [geb-skill/reference/playbook.md](geb-skill/reference/playbook.md)
- [laravel-dusk-skill/SKILL.md](laravel-dusk-skill/SKILL.md)
- [laravel-dusk-skill/reference/advanced-patterns.md](laravel-dusk-skill/reference/advanced-patterns.md)
- [laravel-dusk-skill/reference/playbook.md](laravel-dusk-skill/reference/playbook.md)
- [nemojs-skill/SKILL.md](nemojs-skill/SKILL.md)
- [nemojs-skill/reference/advanced-patterns.md](nemojs-skill/reference/advanced-patterns.md)
- [nemojs-skill/reference/playbook.md](nemojs-skill/reference/playbook.md)
- [nightwatchjs-skill/reference/playbook.md](nightwatchjs-skill/reference/playbook.md)
- [playwright-skill/reference/debugging-flaky.md](playwright-skill/reference/debugging-flaky.md)
- [playwright-skill/reference/playbook.md](playwright-skill/reference/playbook.md)
- [protractor-skill/SKILL.md](protractor-skill/SKILL.md)
- [protractor-skill/reference/advanced-patterns.md](protractor-skill/reference/advanced-patterns.md)
- [protractor-skill/reference/playbook.md](protractor-skill/reference/playbook.md)
- [robot-framework-skill/SKILL.md](robot-framework-skill/SKILL.md)
- [robot-framework-skill/reference/advanced-patterns.md](robot-framework-skill/reference/advanced-patterns.md)
- [robot-framework-skill/reference/playbook.md](robot-framework-skill/reference/playbook.md)
- [selenide-skill/SKILL.md](selenide-skill/SKILL.md)
- [selenide-skill/reference/playbook.md](selenide-skill/reference/playbook.md)

</details>



This section covers the specialized E2E browser testing skills within the Agent Skills repository. These skills support a diverse range of ecosystems, from legacy Angular applications (Protractor) and modern Java fluent APIs (Selenide) to PHP-specific frameworks (Laravel Dusk, Codeception) and keyword-driven automation (Robot Framework).

## 1. Protractor (Angular & Migration)

Protractor is a legacy framework for Angular and AngularJS applications. While officially deprecated, the skill provides patterns for maintaining existing suites and migrating them to modern alternatives like Playwright.

### Core Implementation
Protractor utilizes a `protractor.conf.js` file to manage browser capabilities and test execution. It extends WebDriverJS and provides Angular-specific locators such as `by.model` and `by.repeater` `[protractor-skill/reference/playbook.md:9-56]()`.

### Data Flow and Synchronization
Protractor's primary value was its automatic synchronization with Angular's `$http` and `$timeout` services via `browser.waitForAngularEnabled(true)` `[protractor-skill/reference/playbook.md:39-40]()`. For non-Angular pages, this must be explicitly disabled `[protractor-skill/reference/playbook.md:213-219]()`.

**Protractor Entity Mapping**
Title: Protractor Code Entity Relationship
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Wait for Angular'"]
        B["'Angular Locator'"]
        C["'Page Object'"]
    end

    subgraph "Code Entity Space"
        A --> D["browser.waitForAngularEnabled(true)"]
        B --> E["by.model('user.name')"]
        B --> F["by.repeater('item in items')"]
        C --> G["BasePage class"]
        G --> H["ElementFinder"]
    end
    
    D --- [protractor-skill/reference/playbook.md:40-40]
    E --- [protractor-skill/reference/playbook.md:237-237]
    G --- [protractor-skill/reference/playbook.md:88-88]
```
Sources: `[protractor-skill/reference/playbook.md:9-243]()`

---

## 2. Selenide (Java Fluent API)

Selenide is a wrapper around Selenium WebDriver that provides a fluent API, smart waiting, and simplified configuration for Java.

### Implementation Details
*   **Selectors**: Uses `$` for single elements and `$$` for collections `[selenide-skill/reference/playbook.md:118-151]()`.
*   **Smart Waits**: Assertions like `.shouldBe(visible)` or `.shouldHave(text(...))` automatically retry until the timeout is reached `[selenide-skill/reference/playbook.md:122-130]()`.
*   **Configuration**: Managed via `selenide.properties` or the `Configuration` class `[selenide-skill/reference/playbook.md:87-98]()`.

### Key Functions
| Function | Description |
| :--- | :--- |
| `open(url)` | Opens the browser to the specified URL `[selenide-skill/reference/playbook.md:115-115]()` |
| `$(selector)` | Returns a `SelenideElement` (Proxy) `[selenide-skill/reference/playbook.md:118-118]()` |
| `$$(selector)` | Returns a `ElementsCollection` `[selenide-skill/reference/playbook.md:151-151]()` |
| `.shouldBe(condition)`| Performs a "Smart Wait" assertion `[selenide-skill/reference/playbook.md:122-122]()` |

Sources: `[selenide-skill/reference/playbook.md:102-177]()`

---

## 3. Geb (Groovy & Spock)

Geb brings together the power of WebDriver, the elegance of jQuery content selection, and the expressiveness of the Groovy language.

### Implementation Pattern
Geb uses a Domain Specific Language (DSL) for Page Objects. The `static content` block defines elements using jQuery-style selectors `[geb-skill/reference/playbook.md:149-156]()`.

### Geb Configuration
The `GebConfig.groovy` file defines environments and driver logic, including cloud integration with LambdaTest using `RemoteWebDriver` and `LT:Options` `[geb-skill/reference/playbook.md:41-111]()`.

**Geb to Spock Integration**
Title: Geb and Spock Interaction
```mermaid
sequenceDiagram
    participant S as Spock Spec
    participant B as Geb Browser
    participant P as Page Object
    participant D as WebDriver

    S->>B: to LoginPage
    B->>P: at() check
    P->>D: check title/elements
    S->>P: login(user, pass)
    P->>D: emailInput.value(user)
    P->>D: submitBtn.click()
```
Sources: `[geb-skill/reference/playbook.md:145-171]()`, `[geb-skill/reference/playbook.md:118-120]()`

---

## 4. Nemo.js (PayPal Framework)

Nemo.js is a Node.js framework developed by PayPal. Its standout feature is the separation of locators into JSON files.

### View Pattern
Locators are stored in `locators/*.json` files `[nemojs-skill/reference/playbook.md:12-27]()`. These are automatically loaded into the `nemo.view` object, allowing for clean test code: `await nemo.view.login.emailInput().sendKeys(...)` `[nemojs-skill/reference/playbook.md:42-44]()`.

### Plugin Architecture
Nemo is highly extensible through plugins like `nemo-view` (for JSON locators) and `nemo-drivex` (for extended search methods) `[nemojs-skill/reference/playbook.md:184-201]()`.

Sources: `[nemojs-skill/SKILL.md:27-67]()`, `[nemojs-skill/reference/playbook.md:3-58]()`

---

## 5. Laravel Dusk & Codeception (PHP)

These two skills cover the PHP ecosystem, with Dusk focusing on Laravel-specific features and Codeception providing a general-purpose BDD actor pattern.

### Laravel Dusk
Dusk provides an expressive API for browser testing without requiring Selenium. It uses a `DuskTestCase` base class and a `browse` closure to execute tests `[laravel-dusk-skill/SKILL.md:32-44]()`.
*   **Authentication**: Supports `loginAs($user)` to bypass login forms in tests `[laravel-dusk-skill/reference/playbook.md:158-159]()`.
*   **Database**: Integrates with Laravel's `DatabaseMigrations` trait to reset state between tests `[laravel-dusk-skill/reference/playbook.md:106-106]()`.

### Codeception
Codeception uses an "Actor" pattern (usually `$I`) to describe test steps in a readable way `[codeception-skill/SKILL.md:27-42]()`.
*   **Suites**: Organizes tests into `Acceptance`, `Functional`, and `Unit` suites `[codeception-skill/SKILL.md:120-137]()`.
*   **Cest Format**: Uses the `Cest` format where each class method is a test case `[codeception-skill/SKILL.md:23-27]()`.

Sources: `[laravel-dusk-skill/SKILL.md:23-58]()`, `[codeception-skill/SKILL.md:21-53]()`

---

## 6. Robot Framework (Keyword-Driven)

Robot Framework is a generic open-source automation framework that uses a tabular, keyword-driven approach.

### Implementation Structure
*   **Settings**: Import libraries (e.g., `SeleniumLibrary`, `RequestsLibrary`) and resource files `[robot-framework-skill/reference/playbook.md:100-106]()`.
*   **Keywords**: Custom business-level keywords are defined in `.resource` files to abstract low-level interactions `[robot-framework-skill/reference/playbook.md:148-173]()`.
*   **Variables**: Environment-specific data is stored in YAML or Python files `[robot-framework-skill/reference/playbook.md:51-67]()`.

**Robot Framework Entity Mapping**
Title: Robot Framework Keyword Mapping
```mermaid
graph LR
    subgraph "Natural Language Space"
        A["'Login with Credentials'"]
        B["'Verify Dashboard'"]
    end

    subgraph "Code Entity Space"
        A --> C["Keywords: Login With Credentials"]
        C --> D["Input Text | id:email"]
        C --> E["Input Password | id:password"]
        B --> F["Keywords: Verify Dashboard Is Displayed"]
        F --> G["Wait Until Location Contains | /dashboard"]
    end

    C --- [robot-framework-skill/reference/playbook.md:156-156]
    F --- [robot-framework-skill/reference/playbook.md:165-165]
```
Sources: `[robot-framework-skill/reference/playbook.md:98-173]()`

---

# Page: Unit Testing Skills

# Unit Testing Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cicd-pipeline-skill/SKILL.md](cicd-pipeline-skill/SKILL.md)
- [cicd-pipeline-skill/reference/playbook.md](cicd-pipeline-skill/reference/playbook.md)
- [jest-skill/reference/advanced-patterns.md](jest-skill/reference/advanced-patterns.md)
- [jest-skill/reference/playbook.md](jest-skill/reference/playbook.md)
- [junit-5-skill/SKILL.md](junit-5-skill/SKILL.md)
- [junit-5-skill/reference/advanced-patterns.md](junit-5-skill/reference/advanced-patterns.md)
- [junit-5-skill/reference/playbook.md](junit-5-skill/reference/playbook.md)
- [phpunit-skill/reference/playbook.md](phpunit-skill/reference/playbook.md)
- [testunit-skill/reference/playbook.md](testunit-skill/reference/playbook.md)
- [unittest-skill/SKILL.md](unittest-skill/SKILL.md)
- [unittest-skill/reference/playbook.md](unittest-skill/reference/playbook.md)

</details>



The **Unit Testing Skills** category encompasses 15 distinct skills designed to generate production-grade unit tests across major programming ecosystems. These skills enable AI agents to author tests that include complex mocking, lifecycle management, parameterized data sets, and coverage enforcement.

While End-to-End (E2E) testing focuses on user journeys, these unit testing skills target individual code entities (functions, classes, and services) to ensure logic correctness at the most granular level.

## Language Ecosystems

The unit testing category is divided into five primary sub-groups based on the language runtime and framework architecture.

| Ecosystem | Primary Frameworks | Key Capabilities |
|-----------|--------------------|------------------|
| **Java** | JUnit 5, TestNG | Extension models, Mockito integration, Parallel execution. |
| **JavaScript/TS** | Jest, Vitest, Mocha, Jasmine, Karma | Snapshot testing, JSDOM, ESM support, Spies. |
| **Python** | pytest, unittest | Fixtures, MagicMock, Parametrization, Coverage.py. |
| **.NET** | NUnit, xUnit, MSTest | Attributes/Traits, Theories, IClassFixture. |
| **Ruby & PHP** | RSpec, Test::Unit, PHPUnit | Shared examples, Mockery, Data providers, RR mocking. |

For details on specific implementations, see the child pages:
*   [Java Unit Testing — JUnit 5 and TestNG Skills](#3.1)
*   [JavaScript/TypeScript Unit Testing — Jest, Vitest, Mocha, Jasmine, and Karma Skills](#3.2)
*   [Python Unit Testing — pytest and unittest Skills](#3.3)
*   [.NET Unit Testing — NUnit, xUnit, and MSTest Skills](#3.4)
*   [Ruby and PHP Unit Testing — RSpec, Test::Unit, and PHPUnit Skills](#3.5)

---

## Shared Concepts & Architecture

Across all supported languages, the unit testing skills follow a standardized architecture for test structure and dependency isolation.

### 1. Test Lifecycle Hooks
Every skill implements a variation of the Setup/Teardown pattern to ensure test isolation. For example, Java's `@BeforeEach` [junit-5-skill/SKILL.md:43-46]() maps directly to Python's `setUp()` [unittest-skill/SKILL.md:27-29]() and PHPUnit's `setUp(): void` [phpunit-skill/reference/playbook.md:243-248]().

### 2. Mocking and Dependency Injection
To isolate the Unit Under Test (UUT), skills utilize industry-standard mocking libraries.
*   **Java:** Uses `Mockito` with `@Mock` and `@InjectMocks` [junit-5-skill/SKILL.md:128-132]().
*   **JavaScript:** Uses `jest.mock()` for module-level isolation [jest-skill/reference/playbook.md:44-48]().
*   **Python:** Uses `unittest.mock.patch` to intercept calls at the import site [unittest-skill/SKILL.md:93-96]().

### 3. Data-Driven Testing (Parameterized)
To avoid "dry" test suites, all skills support injecting multiple data sets into a single test logic.
*   **PHPUnit:** Uses `#[DataProvider]` attributes [phpunit-skill/reference/playbook.md:127-128]().
*   **JUnit 5:** Uses `@CsvSource` or `@MethodSource` [junit-5-skill/SKILL.md:97-101]().
*   **Ruby (Test::Unit):** Uses the `data` method for named test cases [testunit-skill/reference/playbook.md:212-223]().

---

## Mapping Natural Language to Code Entities

The following diagrams illustrate how the AI Agent translates high-level requirements into specific code structures within the unit testing domain.

### Requirement Translation Flow
This diagram shows how a user request for "mocking a service" is mapped to framework-specific code entities.

```mermaid
graph TD
    User["User Request: 'Test UserService with Mocked Repository'"] --> Intent["Intent: Unit Test + Mocking"]
    
    subgraph "Java (JUnit 5 + Mockito)"
    Intent --> J1["@ExtendWith(MockitoExtension.class)"]
    J1 --> J2["@Mock UserRepository userRepo"]
    J2 --> J3["@InjectMocks UserService userService"]
    end

    subgraph "Python (unittest + mock)"
    Intent --> P1["class TestUserService(unittest.TestCase)"]
    P1 --> P2["@patch('myapp.repo.UserRepository')"]
    P2 --> P3["def test_create(self, MockRepo):"]
    end

    subgraph "JavaScript (Jest)"
    Intent --> JS1["jest.mock('./repository')"]
    JS1 --> JS2["import { UserRepository } from './repository'"]
    JS2 --> JS3["test('service uses repo', async () => { ... })"]
    end
```
**Sources:** [junit-5-skill/SKILL.md:128-132](), [unittest-skill/SKILL.md:93-96](), [jest-skill/reference/playbook.md:44-48]()

### Test Project Structure Mapping
This diagram bridges the conceptual "Project Setup" to the actual file system entities defined in the playbooks.

```mermaid
graph LR
    subgraph "Logic Space"
        Source["Source Code"]
        Tests["Test Suite"]
        Deps["Dependencies"]
        Conf["Config"]
    end

    subgraph "Code Entity Space (PHPUnit Example)"
        Source --> PSR4["src/ (PSR-4 Autoload)"]
        Tests --> PHPUnitTests["tests/Unit/ & tests/Feature/"]
        Deps --> Composer["composer.json (require-dev)"]
        Conf --> XML["phpunit.xml"]
    end

    subgraph "Code Entity Space (Python Example)"
        Source --> SrcDir["src/myapp/"]
        Tests --> PyTests["tests/unit/test_*.py"]
        Deps --> TOML["pyproject.toml"]
        Conf --> Coverage[".coveragerc"]
    end
```
**Sources:** [phpunit-skill/reference/playbook.md:5-29](), [phpunit-skill/reference/playbook.md:82-108](), [unittest-skill/reference/playbook.md:5-38](), [unittest-skill/reference/playbook.md:40-68]()

---

## CI/CD Integration & Coverage

Unit tests are designed to be executed within CI/CD pipelines to enforce quality gates. The `cicd-pipeline-skill` provides the infrastructure to run these tests and collect coverage reports.

*   **GitHub Actions:** Automates execution via `npm test` or `mvn test` [cicd-pipeline-skill/SKILL.md:24-44]().
*   **Coverage Enforcement:** Tools like `SimpleCov` (Ruby) [testunit-skill/reference/playbook.md:47-54](), `Xdebug` (PHP) [phpunit-skill/reference/playbook.md:25](), and `coverage.py` (Python) [unittest-skill/reference/playbook.md:55-68]() are used to set minimum thresholds (e.g., 80%) which fail the build if not met.
*   **Reporting:** Test results are often uploaded as artifacts in JUnit XML format to provide visibility in the CI dashboard [cicd-pipeline-skill/SKILL.md:104-106]().

For more information on pipeline design, see [CI/CD Pipeline and DevOps Skill](#7).

**Sources:**
* `junit-5-skill/SKILL.md`
* `unittest-skill/SKILL.md`
* `phpunit-skill/reference/playbook.md`
* `jest-skill/reference/playbook.md`
* `testunit-skill/reference/playbook.md`
* `cicd-pipeline-skill/SKILL.md`

---

# Page: Java Unit Testing — JUnit 5 and TestNG Skills

# Java Unit Testing — JUnit 5 and TestNG Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cicd-pipeline-skill/SKILL.md](cicd-pipeline-skill/SKILL.md)
- [cicd-pipeline-skill/reference/playbook.md](cicd-pipeline-skill/reference/playbook.md)
- [jest-skill/reference/advanced-patterns.md](jest-skill/reference/advanced-patterns.md)
- [jest-skill/reference/playbook.md](jest-skill/reference/playbook.md)
- [junit-5-skill/reference/advanced-patterns.md](junit-5-skill/reference/advanced-patterns.md)
- [junit-5-skill/reference/playbook.md](junit-5-skill/reference/playbook.md)
- [skills_index.json](skills_index.json)
- [testng-skill/SKILL.md](testng-skill/SKILL.md)
- [testng-skill/reference/advanced-patterns.md](testng-skill/reference/advanced-patterns.md)
- [testng-skill/reference/playbook.md](testng-skill/reference/playbook.md)

</details>



This page provides a technical deep dive into the Java unit testing skills available in the `agent-skills` repository, specifically focusing on **JUnit 5** and **TestNG**. These skills enable AI agents to generate production-grade test suites featuring advanced lifecycle management, dependency injection, mocking, and cloud-integrated parallel execution.

## 1. JUnit 5 (Jupiter) Skill Implementation

The JUnit 5 skill focuses on the modern "Jupiter" programming model, moving away from the legacy JUnit 4 architecture. It emphasizes the use of the Extension model and modular test construction.

### 1.1. Core Lifecycle and Annotations
JUnit 5 uses a hierarchical lifecycle. By default, a new test instance is created for every test method, but this can be overridden to `PER_CLASS` to share state across methods within the same class [junit-5-skill/reference/playbook.md:44-45]().

| Annotation | Function |
| :--- | :--- |
| `@BeforeAll` / `@AfterAll` | Static methods executed once per class (unless `PER_CLASS` is set) [junit-5-skill/reference/playbook.md:56-89](). |
| `@BeforeEach` / `@AfterEach` | Executed before/after every individual `@Test` [junit-5-skill/reference/playbook.md:61-84](). |
| `@Nested` | Allows grouping tests into inner classes for better organization [junit-5-skill/reference/playbook.md:214-229](). |
| `@Tag` | Filters tests for specific execution environments (e.g., "smoke", "regression") [junit-5-skill/reference/playbook.md:69](). |

### 1.2. Data-Driven Testing
JUnit 5 provides several ways to inject data into tests via the `junit-jupiter-params` artifact.

*   **CsvSource**: For simple inline comma-separated values [junit-5-skill/reference/playbook.md:97-106]().
*   **MethodSource**: For complex objects generated by a static factory method [junit-5-skill/reference/playbook.md:117-133]().
*   **ArgumentsProvider**: A reusable class-based provider for dynamic data generation [junit-5-skill/reference/advanced-patterns.md:34-43]().

### 1.3. Extension Model and Mockito Integration
The JUnit 5 extension model replaces the `Runner` and `Rule` APIs from JUnit 4. The `MockitoExtension` is the primary method for integrating mocking [junit-5-skill/reference/playbook.md:153-158]().

**Data Flow: Mockito Injection**
The following diagram illustrates how the `MockitoExtension` processes annotations to prepare the test instance.

Title: JUnit 5 Mockito Extension Data Flow
```mermaid
graph TD
    subgraph "JUnit_5_Engine"
        A["TestInstanceFactory"] --> B["MockitoExtension::postProcessTestInstance"]
    end

    subgraph "Mockito_Processing"
        B --> C{"Scan Annotations"}
        C -->|@Mock| D["Instantiate Mock Proxy"]
        C -->|@Spy| E["Wrap Real Instance"]
        C -->|@InjectMocks| F["Inject Dependencies into Target"]
    end

    D --> G["OrderServiceTest instance"]
    E --> G
    F --> G
    G --> H["@Test Method Execution"]
```
Sources: [junit-5-skill/reference/playbook.md:153-172](), [junit-5-skill/reference/advanced-patterns.md:121-140]()

---

## 2. TestNG Skill Implementation

TestNG is designed for more complex integration testing scenarios, offering powerful features like native XML-based suite configuration and method-level dependency management.

### 2.1. Suite Configuration (testng.xml)
Unlike JUnit, TestNG relies heavily on an XML configuration file to define execution logic, parallelization strategies, and global parameters [testng-skill/reference/playbook.md:49-84]().

*   **Parallelization**: Can be set at the `methods`, `classes`, or `tests` level [testng-skill/SKILL.md:88-91]().
*   **Listeners**: Intercept test events for custom reporting or retries (e.g., `IRetryAnalyzer`) [testng-skill/reference/advanced-patterns.md:66-73]().

### 2.2. Thread-Safe Driver Management
For parallel browser testing, the TestNG skill implements a `ThreadLocal` pattern within a `BaseTest` class to ensure that each thread maintains its own `WebDriver` instance [testng-skill/reference/playbook.md:103-147]().

Title: TestNG Thread-Safe Execution Flow
```mermaid
sequenceDiagram
    participant XML as testng.xml
    participant Engine as TestNG Executor
    participant Base as BaseTest (@BeforeMethod)
    participant TL as ThreadLocal<WebDriver>
    participant Test as TestClass (@Test)

    XML->>Engine: parallel="methods", thread-count="4"
    Engine->>Base: setUp(browser, env)
    Base->>TL: set(new ChromeDriver())
    Engine->>Test: execute test method
    Test->>TL: get() driver instance
    Test->>Test: Perform Actions
    Engine->>Base: tearDown()
    Base->>TL: remove()
```
Sources: [testng-skill/reference/playbook.md:50-55](), [testng-skill/reference/playbook.md:103-147]()

### 2.3. Advanced Data Providers
TestNG's `@DataProvider` supports parallel execution and can return an `Iterator<Object[]>`, allowing for memory-efficient processing of large datasets from CSV or Excel [testng-skill/reference/playbook.md:182-219]().

---

## 3. Comparison of Core Capabilities

| Feature | JUnit 5 Implementation | TestNG Implementation |
| :--- | :--- | :--- |
| **Parallelism** | `junit-platform.properties` [junit-5-skill/reference/playbook.md:39-45]() | `testng.xml` suite attributes [testng-skill/SKILL.md:88-91]() |
| **Data Driving** | `@ParameterizedTest` + `@MethodSource` [junit-5-skill/reference/playbook.md:117-125]() | `@Test(dataProvider = "name")` [testng-skill/SKILL.md:51-67]() |
| **Dependencies** | Not natively supported (uses `@Nested`) | `dependsOnMethods` or `dependsOnGroups` [testng-skill/SKILL.md:36-39]() |
| **Assertions** | AssertJ or `Assertions.assertAll` [junit-5-skill/reference/playbook.md:74-79]() | `SoftAssert` (collects multiple failures) [testng-skill/SKILL.md:95-101]() |

---

## 4. LambdaTest Cloud Integration

Both skills support routing tests to the LambdaTest cloud. This is achieved by configuring a `RemoteWebDriver` (for Selenium-based tests) or utilizing environment variables for authentication.

### 4.1. Implementation via CI/CD
The `cicd-pipeline-skill` provides the YAML structure for injecting `LT_USERNAME` and `LT_ACCESS_KEY` into the test environment [cicd-pipeline-skill/SKILL.md:45-50]().

Title: Cloud Integration Architecture
```mermaid
graph LR
    subgraph "Local/CI Environment"
        Runner["Maven / Surefire"]
        Env["Secrets (LT_USERNAME, LT_ACCESS_KEY)"]
    end

    subgraph "Test Code"
        BT["BaseTest / Setup"]
        Caps["LT:Options (Platform, Browser)"]
    end

    subgraph "LambdaTest Cloud"
        Hub["hub.lambdatest.com/wd/hub"]
        VM["Remote Browser / Device"]
    end

    Runner --> BT
    Env --> BT
    BT --> Caps
    Caps --> Hub
    Hub --> VM
```
Sources: [cicd-pipeline-skill/SKILL.md:24-56](), [testng-skill/reference/playbook.md:103-136]()

### 4.2. Reporting and Listeners
In production environments, both frameworks use listeners to report results back to the cloud dashboard:
*   **JUnit 5**: Uses `TestExecutionListener` to update test status via the LambdaTest API.
*   **TestNG**: Uses `ITestListener` to capture screenshots on failure and attach them to Allure reports [testng-skill/reference/playbook.md:149-156]().

Sources:
- [junit-5-skill/reference/playbook.md:1-235]()
- [testng-skill/SKILL.md:1-158]()
- [testng-skill/reference/playbook.md:1-219]()
- [junit-5-skill/reference/advanced-patterns.md:1-191]()
- [cicd-pipeline-skill/SKILL.md:1-122]()
- [testng-skill/reference/advanced-patterns.md:1-118]()

---

# Page: JavaScript/TypeScript Unit Testing — Jest, Vitest, Mocha, Jasmine, and Karma Skills

# JavaScript/TypeScript Unit Testing — Jest, Vitest, Mocha, Jasmine, and Karma Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cicd-pipeline-skill/SKILL.md](cicd-pipeline-skill/SKILL.md)
- [cicd-pipeline-skill/reference/playbook.md](cicd-pipeline-skill/reference/playbook.md)
- [jasmine-skill/SKILL.md](jasmine-skill/SKILL.md)
- [jasmine-skill/reference/advanced-patterns.md](jasmine-skill/reference/advanced-patterns.md)
- [jasmine-skill/reference/playbook.md](jasmine-skill/reference/playbook.md)
- [jest-skill/SKILL.md](jest-skill/SKILL.md)
- [jest-skill/reference/advanced-patterns.md](jest-skill/reference/advanced-patterns.md)
- [jest-skill/reference/playbook.md](jest-skill/reference/playbook.md)
- [junit-5-skill/reference/advanced-patterns.md](junit-5-skill/reference/advanced-patterns.md)
- [junit-5-skill/reference/playbook.md](junit-5-skill/reference/playbook.md)
- [karma-skill/SKILL.md](karma-skill/SKILL.md)
- [karma-skill/reference/advanced-patterns.md](karma-skill/reference/advanced-patterns.md)
- [karma-skill/reference/playbook.md](karma-skill/reference/playbook.md)
- [mocha-skill/SKILL.md](mocha-skill/SKILL.md)
- [mocha-skill/reference/advanced-patterns.md](mocha-skill/reference/advanced-patterns.md)
- [mocha-skill/reference/playbook.md](mocha-skill/reference/playbook.md)
- [vitest-skill/SKILL.md](vitest-skill/SKILL.md)
- [vitest-skill/reference/advanced-patterns.md](vitest-skill/reference/advanced-patterns.md)
- [vitest-skill/reference/playbook.md](vitest-skill/reference/playbook.md)

</details>



This page provides technical documentation for the JavaScript and TypeScript unit testing skills within the `agent-skills` repository. It covers the configuration, mocking APIs, and advanced testing patterns for five major frameworks: Jest, Vitest, Mocha, Jasmine, and Karma.

## 1. Jest Skill

Jest is a comprehensive testing framework focusing on simplicity and support for large-scale projects. It includes a built-in runner, assertion library, and mocking support.

### Implementation and Configuration
Jest configuration is typically handled via `jest.config.js`. Key settings include `testEnvironment` (e.g., `node` or `jsdom`), `transform` (for TypeScript support via `ts-jest` or `@swc/jest`), and `coverageThreshold` for quality gates [jest-skill/reference/playbook.md:6-25]().

### Mocking and Spies
Jest provides a powerful mocking API to isolate units of code:
*   **Module Mocking:** `jest.mock()` allows for full or partial replacement of modules [jest-skill/reference/playbook.md:44-54]().
*   **Manual Mocks:** Located in `__mocks__/` directories for consistent behavior across tests [jest-skill/reference/playbook.md:56-61]().
*   **Timer Mocking:** `jest.useFakeTimers()` allows controlling time-dependent logic like debouncing [jest-skill/reference/advanced-patterns.md:52-60]().

### React Testing Library (RTL) Integration
For UI testing, Jest integrates with RTL to test components from a user's perspective.
*   **Setup:** Requires `jsdom` and `@testing-library/jest-dom` [jest-skill/reference/playbook.md:31-32]().
*   **Patterns:** Uses `screen` for querying elements and `userEvent` for simulating interactions [jest-skill/reference/advanced-patterns.md:142-154]().

### Snapshot Testing
Jest captures the serialized state of a component or object to detect regressions.
*   **File Snapshots:** `toMatchSnapshot()` [jest-skill/SKILL.md:135-138]().
*   **Inline Snapshots:** `toMatchInlineSnapshot()` where the expectation is written back into the source code [jest-skill/reference/advanced-patterns.md:113-118]().

**Sources:** [jest-skill/SKILL.md:1-179](), [jest-skill/reference/playbook.md:1-100](), [jest-skill/reference/advanced-patterns.md:1-218]()

---

## 2. Vitest Skill

Vitest is a Vite-native testing framework that provides a Jest-compatible API with faster execution and native ESM support.

### Core Features
*   **Vite-Native:** Reuses Vite's configuration and transformers [vitest-skill/SKILL.md:3-7]().
*   **In-Source Testing:** Allows writing tests directly within the source files using `import.meta.vitest` [vitest-skill/SKILL.md:73-82]().
*   **Workspace Support:** Manages monorepos via `vitest.workspace.ts` [vitest-skill/reference/playbook.md:44-52]().

### Mocking API
While Jest uses the `jest` namespace, Vitest uses `vi`.
*   **Mocking:** `vi.mock()` and `vi.fn()` [vitest-skill/SKILL.md:45-56]().
*   **Globals:** `vi.stubGlobal()` for mocking browser APIs like `fetch` or `IntersectionObserver` [vitest-skill/reference/playbook.md:68-83]().

### Performance and Parallelism
Vitest supports concurrent test execution within a single file using `describe.concurrent` and configurable worker pools (`threads`, `forks`, or `vmThreads`) [vitest-skill/reference/advanced-patterns.md:60-76]().

**Sources:** [vitest-skill/SKILL.md:1-145](), [vitest-skill/reference/playbook.md:1-235](), [vitest-skill/reference/advanced-patterns.md:1-167]()

---

## 3. Jasmine and Karma Skills

Jasmine is a Behavior-Driven Development (BDD) framework, while Karma is a test runner that executes Jasmine tests in real browsers.

### Jasmine Spies
Jasmine relies heavily on "spies" to track calls and mock behavior:
*   `spyOn(obj, 'method')`: Tracks an existing method [jasmine-skill/reference/playbook.md:79-88]().
*   `jasmine.createSpyObj('name', ['methods'])`: Creates a full mock object [jasmine-skill/reference/playbook.md:125-137]().
*   **Clock Control:** `jasmine.clock().install()` for mocking `setTimeout` and `Date` [jasmine-skill/reference/playbook.md:206-233]().

### Karma Configuration
Karma's `karma.conf.js` manages the browser lifecycle.
*   **Launchers:** Supports `ChromeHeadless`, `Firefox`, and custom launchers for CI environments [karma-skill/reference/playbook.md:73-84]().
*   **Reporters:** Generates coverage (via `karma-coverage`) and JUnit results for CI integration [karma-skill/reference/playbook.md:35-65]().

### Angular Testing Pattern
Karma is the default runner for Angular, utilizing `TestBed` for component compilation and `fakeAsync` for handling zone-based asynchronous tasks [karma-skill/reference/playbook.md:114-145]().

**Sources:** [jasmine-skill/reference/playbook.md:1-258](), [karma-skill/reference/playbook.md:1-94](), [karma-skill/reference/advanced-patterns.md:1-101]()

---

## 4. Code Entity Space Mapping

The following diagrams bridge natural language concepts to specific code entities within the repository.

### Diagram 1: Mocking and Spying Entity Mapping
This diagram maps common testing actions to the specific framework functions.

```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Create Mock Function"]
        B["Mock Entire Module"]
        C["Control Time/Timers"]
        D["Spy on Method"]
    end

    subgraph "Code Entity Space (Jest/Vitest/Jasmine)"
        A --> E["jest.fn()"]
        A --> F["vi.fn()"]
        A --> G["jasmine.createSpy()"]
        
        B --> H["jest.mock('./path')"]
        B --> I["vi.mock('./path')"]
        
        C --> J["jest.useFakeTimers()"]
        C --> K["vi.useFakeTimers()"]
        C --> L["jasmine.clock().install()"]
        
        D --> M["jest.spyOn(obj, 'method')"]
        D --> N["vi.spyOn(obj, 'method')"]
        D --> O["spyOn(obj, 'method')"]
    end
```
**Sources:** [jest-skill/SKILL.md:60-86](), [vitest-skill/SKILL.md:45-68](), [jasmine-skill/reference/playbook.md:68-121]()

### Diagram 2: Configuration and Lifecycle Mapping
This diagram maps the setup and execution phases to specific files and hooks.

```mermaid
graph LR
    subgraph "System Setup"
        Config["Configuration File"]
        Setup["Setup/Global Hooks"]
    end

    subgraph "Files/Functions"
        Config --- CF1["jest.config.js"]
        Config --- CF2["vitest.config.ts"]
        Config --- CF3["karma.conf.js"]
        
        Setup --- H1["beforeEach()"]
        Setup --- H2["afterEach()"]
        Setup --- H3["setupFilesAfterSetup"]
    end

    subgraph "Execution"
        Runner["Test Runner CLI"]
    end

    Runner --- R1["npx jest"]
    Runner --- R2["npx vitest"]
    Runner --- R3["npx karma start"]
```
**Sources:** [jest-skill/reference/playbook.md:6-25](), [vitest-skill/reference/playbook.md:6-39](), [karma-skill/reference/playbook.md:5-94]()

---

## 5. Summary Table: Framework Comparison

| Feature | Jest | Vitest | Jasmine |
| :--- | :--- | :--- | :--- |
| **Runner** | Built-in | Built-in | Requires Karma (for browser) |
| **Mocking Namespace** | `jest` | `vi` | `jasmine` / `spyOn` |
| **TypeScript Support** | via `ts-jest` / `@swc/jest` | Native (Vite) | via `jasmine-ts` |
| **Snapshots** | Built-in | Built-in | Requires plugins |
| **Async Support** | `async/await`, `done` | `async/await` | `async/await`, `done` |

**Sources:** [jest-skill/SKILL.md:144-149](), [vitest-skill/SKILL.md:115-120](), [jasmine-skill/reference/playbook.md:5-11]()

## 6. CI/CD Integration

All frameworks are designed to run in CI/CD pipelines. A common pattern involves:
1.  **Sharding:** Splitting tests across multiple runners using `--shard` [cicd-pipeline-skill/reference/playbook.md:48]().
2.  **Coverage Gates:** Enforcing a minimum percentage (e.g., 80%) via `coverageThreshold` [jest-skill/reference/playbook.md:15]().
3.  **Artifacts:** Uploading JUnit XML and HTML coverage reports for visibility [cicd-pipeline-skill/reference/playbook.md:49-52]().

**Sources:** [cicd-pipeline-skill/reference/playbook.md:34-53](), [jest-skill/reference/playbook.md:12-16]()

---

# Page: Python Unit Testing — pytest and unittest Skills

# Python Unit Testing — pytest and unittest Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [junit-5-skill/SKILL.md](junit-5-skill/SKILL.md)
- [phpunit-skill/reference/playbook.md](phpunit-skill/reference/playbook.md)
- [pytest-skill/SKILL.md](pytest-skill/SKILL.md)
- [pytest-skill/reference/advanced-patterns.md](pytest-skill/reference/advanced-patterns.md)
- [pytest-skill/reference/playbook.md](pytest-skill/reference/playbook.md)
- [testunit-skill/reference/playbook.md](testunit-skill/reference/playbook.md)
- [unittest-skill/SKILL.md](unittest-skill/SKILL.md)
- [unittest-skill/reference/playbook.md](unittest-skill/reference/playbook.md)

</details>



This page provides a technical deep dive into the Python unit testing ecosystem within the `agent-skills` repository. It covers the two primary frameworks: `pytest` (the modern, fixture-based standard) and `unittest` (the Python standard library's xUnit-style framework). The documentation includes implementation details for fixtures, mocking, parameterized testing, and CI/CD integration.

## 1. Framework Comparison and Selection

The repository maintains two distinct skills for Python unit testing, triggered by specific natural language cues or code signatures.

| Feature | `pytest` | `unittest` |
| :--- | :--- | :--- |
| **Style** | Functional (functions/fixtures) | Object-Oriented (`TestCase` classes) |
| **Assertions** | Plain `assert` (via bytecode rewriting) | `self.assert*` methods |
| **Fixtures** | Dependency Injection (scoped) | `setUp`/`tearDown` hooks |
| **Parametrization** | `@pytest.mark.parametrize` | `self.subTest` or `parameterized` lib |
| **Mocking** | `pytest-mock` (mocker fixture) | `unittest.mock` (patch/MagicMock) |

Sources: [pytest-skill/SKILL.md:1-15](), [unittest-skill/SKILL.md:1-15]()

---

## 2. Pytest Implementation

`pytest` is the recommended framework for modern Python projects due to its powerful fixture system and simplified assertion syntax.

### 2.1. Fixture Lifecycle and Scoping
Fixtures in `pytest` use a dependency injection model. They are defined using the `@pytest.fixture` decorator and can be scoped to `function` (default), `class`, `module`, or `session`.

**Fixture Data Flow:**
The diagram below illustrates how a session-scoped database engine is shared across multiple function-scoped sessions.

**Title: Pytest Fixture Dependency Graph**
```mermaid
graph TD
    subgraph "Session Scope"
        A["db_engine fixture"] --> B["create_engine()"]
    end

    subgraph "Function Scope (Test 1)"
        C["db_session fixture"] --> A
        D["test_user_creation(db_session)"] --> C
    end

    subgraph "Function Scope (Test 2)"
        E["db_session fixture (new)"] --> A
        F["test_user_deletion(db_session)"] --> E
    end

    A -- "yield engine" --> G["Base.metadata.create_all"]
    G -- "teardown" --> H["Base.metadata.drop_all"]
```
Sources: [pytest-skill/reference/playbook.md:51-69](), [pytest-skill/reference/advanced-patterns.md:10-27]()

### 2.2. Advanced Patterns
*   **Factory Fixtures**: Used to create multiple instances of a model within a single test while ensuring cleanup [pytest-skill/reference/playbook.md:71-85]().
*   **Indirect Parametrization**: Allows passing parameters to a fixture rather than the test function directly [pytest-skill/reference/advanced-patterns.md:49-58]().
*   **Conftest.py**: Centralized location for shared fixtures and custom hooks like `pytest_addoption` [pytest-skill/reference/advanced-patterns.md:124-133]().

---

## 3. Python unittest Implementation

`unittest` follows the xUnit pattern, requiring tests to be wrapped in classes inheriting from `unittest.TestCase`.

### 3.1. Core Structure and Lifecycle
The framework relies on specific method names for lifecycle management:
*   `setUp()`: Runs before every test method [unittest-skill/SKILL.md:112]().
*   `tearDown()`: Runs after every test method [unittest-skill/SKILL.md:114]().
*   `setUpClass()` / `tearDownClass()`: Class-level hooks for expensive resources [unittest-skill/SKILL.md:111-115]().

### 3.2. Mocking and Patching
`unittest` uses the `unittest.mock` library. A critical pattern is patching "at the destination": patching the reference where the object is *imported*, not where it is *defined*.

**Title: Natural Language to unittest Mocking Entities**
```mermaid
graph LR
    subgraph "Natural Language Space"
        NL1["'Mock the user repository'"]
        NL2["'Patch the external API call'"]
        NL3["'Verify the email was sent'"]
    end

    subgraph "Code Entity Space (unittest.mock)"
        E1["@patch('myapp.services.user_service.UserRepository')"]
        E2["mock_get.return_value.json.return_value = {...}"]
        E3["mock_email.send_welcome.assert_called_once_with(...)"]
    end

    NL1 --> E1
    NL2 --> E2
    NL3 --> E3
```
Sources: [unittest-skill/reference/playbook.md:191-204](), [unittest-skill/SKILL.md:90-106]()

---

## 4. Data-Driven Testing Patterns

Both frameworks support data-driven testing, though the implementation differs significantly.

| Pattern | pytest Implementation | unittest Implementation |
| :--- | :--- | :--- |
| **Basic** | `@pytest.mark.parametrize` [pytest-skill/SKILL.md:78-89]() | `self.subTest()` context manager [unittest-skill/SKILL.md:80-86]() |
| **Matrix** | Stacked decorators (Cartesian product) [pytest-skill/reference/playbook.md:127-132]() | Nested loops with `self.subTest` |
| **External** | Fixture reading CSV/JSON [pytest-skill/reference/playbook.md:94-99]() | `parameterized` library or manual loading |

**Title: Parameterized Test Flow (pytest)**
```mermaid
graph LR
    subgraph "Input Matrix"
        P1["('hello', 5)"]
        P2["('', 0)"]
        P3["('pytest', 6)"]
    end

    subgraph "Execution Engine"
        M["@pytest.mark.parametrize"]
    end

    subgraph "Test Function"
        F["test_string_length(input, expected)"]
    end

    P1 --> M
    P2 --> M
    P3 --> M
    M --> F
```
Sources: [pytest-skill/SKILL.md:78-82](), [pytest-skill/reference/playbook.md:107-115]()

---

## 5. Configuration and CI/CD Integration

### 5.1. Project Configuration
Modern Python projects utilize `pyproject.toml` to centralize testing configuration, including markers, coverage thresholds, and default options.

**Example `pyproject.toml` for pytest:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --strict-markers --tb=short"
markers = [
    "slow: marks tests as slow",
    "integration: integration tests"
]
```
Sources: [pytest-skill/reference/playbook.md:23-41](), [pytest-skill/SKILL.md:172-177]()

### 5.2. Coverage Enforcement
The `coverage.py` tool is used across both frameworks to enforce quality gates. Configuration is typically stored in `.coveragerc` or `pyproject.toml`.

*   **Source**: Defines which directories to measure [unittest-skill/reference/playbook.md:56]().
*   **Fail Under**: Sets the minimum percentage for CI to pass [unittest-skill/reference/playbook.md:61]().
*   **Branch Coverage**: Tracks whether both branches of conditional statements are executed [unittest-skill/reference/playbook.md:58]().

### 5.3. Execution Commands
| Task | pytest | unittest |
| :--- | :--- | :--- |
| **Run All** | `pytest` | `python -m unittest discover` |
| **Specific File** | `pytest tests/test_api.py` | `python -m unittest tests/test_api.py` |
| **By Marker/Name**| `pytest -m smoke` | N/A (Standard) |
| **With Coverage** | `pytest --cov=src` | `coverage run -m unittest` |

Sources: [pytest-skill/SKILL.md:157-168](), [unittest-skill/SKILL.md:118-119]()

---
**Sources:**
* `pytest-skill/SKILL.md`
* `pytest-skill/reference/playbook.md`
* `pytest-skill/reference/advanced-patterns.md`
* `unittest-skill/SKILL.md`
* `unittest-skill/reference/playbook.md`

---

# Page: .NET Unit Testing — NUnit, xUnit, and MSTest Skills

# .NET Unit Testing — NUnit, xUnit, and MSTest Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mstest-skill/SKILL.md](mstest-skill/SKILL.md)
- [mstest-skill/reference/advanced-patterns.md](mstest-skill/reference/advanced-patterns.md)
- [mstest-skill/reference/playbook.md](mstest-skill/reference/playbook.md)
- [nunit-skill/SKILL.md](nunit-skill/SKILL.md)
- [nunit-skill/reference/advanced-patterns.md](nunit-skill/reference/advanced-patterns.md)
- [nunit-skill/reference/playbook.md](nunit-skill/reference/playbook.md)
- [testunit-skill/reference/advanced-patterns.md](testunit-skill/reference/advanced-patterns.md)
- [unittest-skill/reference/advanced-patterns.md](unittest-skill/reference/advanced-patterns.md)
- [xunit-skill/SKILL.md](xunit-skill/SKILL.md)
- [xunit-skill/reference/advanced-patterns.md](xunit-skill/reference/advanced-patterns.md)
- [xunit-skill/reference/playbook.md](xunit-skill/reference/playbook.md)

</details>



This page provides a technical deep dive into the three primary .NET unit testing frameworks supported by the Agent Skills repository. It covers framework-specific attributes, lifecycle management, data-driven testing patterns, and advanced integration with mocking libraries like `Moq` and assertion libraries like `FluentAssertions`.

## Framework Comparison and Mapping

While all three frameworks target the .NET ecosystem, they differ in their approach to test discovery, lifecycle hooks, and parallelization.

### Natural Language to Code Entity Mapping

The following diagram maps common testing concepts to their specific implementations across the three frameworks.

**Diagram: .NET Framework Entity Mapping**
```mermaid
graph TD
    subgraph "Testing Concept"
        TC1["Test Class Container"]
        TC2["Individual Test"]
        TC3["Parameterized Test"]
        TC4["Per-Test Setup"]
        TC5["Shared Context"]
    end

    subgraph "NUnit Entities"
        N1["[TestFixture]"]
        N2["[Test]"]
        N3["[TestCase]"]
        N4["[SetUp]"]
        N5["[OneTimeSetUp]"]
    end

    subgraph "xUnit Entities"
        X1["Public Class"]
        X2["[Fact]"]
        X3["[Theory]"]
        X4["Constructor"]
        X5["IClassFixture<T>"]
    end

    subgraph "MSTest Entities"
        M1["[TestClass]"]
        M2["[TestMethod]"]
        M3["[DataTestMethod]"]
        M4["[TestInitialize]"]
        M5["[ClassInitialize]"]
    end

    TC1 --> N1
    TC1 --> X1
    TC1 --> M1
    
    TC2 --> N2
    TC2 --> X2
    TC2 --> M2
    
    TC3 --> N3
    TC3 --> X3
    TC3 --> M3
    
    TC4 --> N4
    TC4 --> X4
    TC4 --> M4
    
    TC5 --> N5
    TC5 --> X5
    TC5 --> M5
```
**Sources:** [nunit-skill/SKILL.md:129-137](), [xunit-skill/SKILL.md:123-135](), [mstest-skill/SKILL.md:93-103]()

---

## NUnit 3 Testing Skill

NUnit uses a constraint-based assertion model (`Assert.That`) and provides extensive attributes for controlling test execution and lifecycle.

### Lifecycle and Configuration
NUnit tests are organized within classes marked with the `[TestFixture]` attribute [nunit-skill/SKILL.md:26-27](). Setup and teardown are handled via `[SetUp]` and `[TearDown]` for individual tests, and `[OneTimeSetUp]` / `[OneTimeTearDown]` for the entire fixture [nunit-skill/reference/playbook.md:219-230]().

### Data-Driven Testing
NUnit supports multiple ways to parameterize tests:
*   **`[TestCase]`**: For simple inline values [nunit-skill/reference/playbook.md:111-115]().
*   **`[TestCaseSource]`**: For complex data sets generated by a method or property [nunit-skill/reference/playbook.md:121-132]().
*   **`[Combinatorial]`**: To test all possible combinations of provided values [nunit-skill/reference/advanced-patterns.md:30-38]().

### Constraint Model (Assert.That)
The modern NUnit syntax emphasizes readability through the constraint model:
```csharp
Assert.That(actual, Is.EqualTo(expected));
Assert.That(list, Has.Exactly(5).Items.And.Is.Ordered);
Assert.That(() => service.Do(), Throws.TypeOf<ArgumentException>());
```
**Sources:** [nunit-skill/reference/playbook.md:163-180](), [nunit-skill/reference/playbook.md:197-203]()

---

## xUnit.net Testing Skill

xUnit is designed for maximum test isolation. Unlike NUnit or MSTest, it creates a **new instance of the test class** for every single test execution [xunit-skill/reference/advanced-patterns.md:119-122]().

### Architecture and Data Flow
The following diagram illustrates how xUnit manages shared state via `IClassFixture`.

**Diagram: xUnit IClassFixture Data Flow**
```mermaid
sequenceDiagram
    participant Runner as xUnit Runner
    participant Fixture as DatabaseFixture : IAsyncLifetime
    participant TestClass as UserRepositoryTests
    
    Runner->>Fixture: InitializeAsync()
    Note over Fixture: Start Docker Container / Migrate DB
    
    loop For Each [Fact]
        Runner->>TestClass: New Instance(Fixture)
        TestClass->>TestClass: Execute Test Logic
        Runner->>TestClass: Dispose() (if IDisposable)
    end
    
    Runner->>Fixture: DisposeAsync()
```
**Sources:** [xunit-skill/reference/playbook.md:157-186](), [xunit-skill/reference/advanced-patterns.md:47-57]()

### Key Patterns
*   **`[Fact]` vs `[Theory]`**: `[Fact]` is for invariant tests; `[Theory]` is for data-driven tests using `[InlineData]`, `[MemberData]`, or `[ClassData]` [xunit-skill/SKILL.md:30-74]().
*   **Shared Context**: Use `IClassFixture<T>` for sharing state within a class and `[CollectionDefinition]` with `ICollectionFixture<T>` for sharing across multiple classes [xunit-skill/reference/playbook.md:155-208]().
*   **Async Testing**: Prefers `IAsyncLifetime` over `IDisposable` for asynchronous setup/teardown [xunit-skill/reference/advanced-patterns.md:47-57]().

---

## MSTest Testing Skill

MSTest is Microsoft's official testing framework. It is often preferred in enterprise environments due to its tight integration with Visual Studio.

### Core Implementation
MSTest requires the `[TestClass]` attribute on classes and `[TestMethod]` on test methods [mstest-skill/SKILL.md:26-34](). It uses static methods for assembly and class-level initialization [mstest-skill/SKILL.md:96-102]().

### Data-Driven Features
*   **`[DataRow]`**: Standard inline data [mstest-skill/reference/playbook.md:152-156]().
*   **`[DynamicData]`**: Loads data from a method or property [mstest-skill/reference/playbook.md:190-192]().
*   **`[CsvDataSource]`**: MSTest has built-in support for external files like CSVs [mstest-skill/reference/advanced-patterns.md:28-30]().

### Advanced Integration
MSTest often utilizes `FluentAssertions` to improve its native assertion library:
```csharp
// Native
Assert.AreEqual(expected, actual);
// Fluent
actual.Should().Be(expected).And.NotBeNull();
```
**Sources:** [mstest-skill/reference/playbook.md:208-216](), [mstest-skill/SKILL.md:78-91]()

---

## Shared .NET Patterns and CI/CD

Regardless of the framework, several patterns are standard across the .NET ecosystem.

### Project Dependencies (.csproj)
All frameworks require the `Microsoft.NET.Test.Sdk` and their respective test adapters for execution via `dotnet test`.
```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
  <PackageReference Include="FluentAssertions" Version="6.12.0" />
  <PackageReference Include="Moq" Version="4.20.70" />
  <PackageReference Include="coverlet.collector" Version="6.0.0" />
</ItemGroup>
```
**Sources:** [nunit-skill/reference/playbook.md:15-25](), [xunit-skill/reference/playbook.md:15-27](), [mstest-skill/reference/playbook.md:15-28]()

### Execution and Parallelization
Parallelization is typically configured via a `.runsettings` file or framework-specific attributes.
*   **NUnit**: Uses `[Parallelizable]` attribute [nunit-skill/reference/advanced-patterns.md:112-113]().
*   **xUnit**: Parallelizes by test collection (class) by default [xunit-skill/reference/playbook.md:31-41]().
*   **MSTest**: Configured in `.runsettings` under the `<Parallelize>` tag [mstest-skill/reference/playbook.md:36-39]().

### Code Coverage
Code coverage is enforced using `coverlet.collector`. The configuration in `.runsettings` allows excluding generated code or specific namespaces [nunit-skill/reference/playbook.md:39-48](), [mstest-skill/reference/playbook.md:43-55]().

**Sources:**
* `nunit-skill/reference/playbook.md`
* `xunit-skill/reference/playbook.md`
* `mstest-skill/reference/playbook.md`
* `nunit-skill/SKILL.md`
* `xunit-skill/SKILL.md`
* `mstest-skill/SKILL.md`
* `nunit-skill/reference/advanced-patterns.md`
* `xunit-skill/reference/advanced-patterns.md`
* `mstest-skill/reference/advanced-patterns.md`

---

# Page: Ruby and PHP Unit Testing — RSpec, Test::Unit, and PHPUnit Skills

# Ruby and PHP Unit Testing — RSpec, Test::Unit, and PHPUnit Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [capybara-skill/SKILL.md](capybara-skill/SKILL.md)
- [capybara-skill/reference/advanced-patterns.md](capybara-skill/reference/advanced-patterns.md)
- [capybara-skill/reference/cloud-integration.md](capybara-skill/reference/cloud-integration.md)
- [capybara-skill/reference/playbook.md](capybara-skill/reference/playbook.md)
- [nunit-skill/reference/advanced-patterns.md](nunit-skill/reference/advanced-patterns.md)
- [phpunit-skill/SKILL.md](phpunit-skill/SKILL.md)
- [phpunit-skill/reference/advanced-patterns.md](phpunit-skill/reference/advanced-patterns.md)
- [phpunit-skill/reference/playbook.md](phpunit-skill/reference/playbook.md)
- [protractor-skill/reference/cloud-integration.md](protractor-skill/reference/cloud-integration.md)
- [rspec-skill/SKILL.md](rspec-skill/SKILL.md)
- [rspec-skill/reference/advanced-patterns.md](rspec-skill/reference/advanced-patterns.md)
- [rspec-skill/reference/playbook.md](rspec-skill/reference/playbook.md)
- [testunit-skill/SKILL.md](testunit-skill/SKILL.md)
- [testunit-skill/reference/advanced-patterns.md](testunit-skill/reference/advanced-patterns.md)
- [testunit-skill/reference/playbook.md](testunit-skill/reference/playbook.md)
- [unittest-skill/reference/advanced-patterns.md](unittest-skill/reference/advanced-patterns.md)
- [unittest-skill/reference/playbook.md](unittest-skill/reference/playbook.md)

</details>



This section provides a technical deep dive into the unit testing skills for Ruby and PHP within the TestMu AI Agent Skills repository. It covers the implementation of BDD-style testing with RSpec, classic xUnit patterns with Ruby's `Test::Unit`, and enterprise-grade PHP testing with PHPUnit.

## 1. RSpec Skill (Ruby)

RSpec is a Behavior-Driven Development (BDD) framework for Ruby. The skill focuses on using the `expect().to` syntax, lazy-loaded `let` blocks, and sophisticated mocking with `instance_double`.

### 1.1 Core Architecture and DSL
RSpec tests are structured using `describe` and `context` blocks to create a readable hierarchy of behaviors [rspec-skill/SKILL.md:24-46]().

| Feature | Code Entity | Purpose |
| :--- | :--- | :--- |
| **Lazy Loading** | `let(:user) { ... }` | Memoized helper method; only evaluates when called [rspec-skill/SKILL.md:94-96](). |
| **Subject** | `subject(:calc) { ... }` | Defines the primary object under test [rspec-skill/SKILL.md:25](). |
| **Hooks** | `before(:each)`, `after(:all)` | Lifecycle management for setup/teardown [rspec-skill/SKILL.md:98-104](). |
| **Doubles** | `instance_double(Class)` | Verifying doubles that check if methods exist on the real class [rspec-skill/reference/playbook.md:98-99](). |

### 1.2 Advanced Patterns: Shared Examples
Shared examples allow for dry testing of polymorphic interfaces or common behaviors across different classes.

**Data Flow for Shared Examples**
The following diagram illustrates how `it_behaves_like` injects test logic into different resource specs.

Title: RSpec Shared Examples Logic
```mermaid
graph TD
    subgraph "Shared Space"
        SE["shared_examples 'searchable'"]
    end

    subgraph "User Spec"
        U["RSpec.describe User"]
        IBL_U["it_behaves_like 'searchable'"]
    end

    subgraph "Product Spec"
        P["RSpec.describe Product"]
        IBL_P["it_behaves_like 'searchable'"]
    end

    SE --> IBL_U
    SE --> IBL_P
    U --> IBL_U
    P --> IBL_P
```
Sources: [rspec-skill/reference/playbook.md:193-224]()

## 2. Test::Unit Skill (Ruby)

`Test::Unit` follows the classic xUnit architecture, utilizing class inheritance and specific method naming conventions (`test_*`).

### 2.1 Implementation Details
Tests inherit from `Test::Unit::TestCase`. Unlike RSpec, it relies on instance variables defined in `setup` and explicit assertion methods [testunit-skill/SKILL.md:24-50]().

*   **Data-Driven Testing**: The `data` method allows running the same test logic against multiple inputs [testunit-skill/reference/playbook.md:212-228]().
*   **Sub-Test Grouping**: Use `sub_test_case` to group related assertions within a single test class [testunit-skill/reference/playbook.md:277-278]().
*   **Mocking**: Integrated via `test-unit-rr` for double-entry mocking [testunit-skill/reference/playbook.md:12]().

### 2.2 Project Structure and Lifecycle
Title: Test::Unit Entity Mapping
```mermaid
classDiagram
    class TestSuite {
        +startup()
        +shutdown()
    }
    class TestCase {
        +setup()
        +teardown()
        +test_method()
    }
    class TestHelpers {
        +fixture_path()
        +load_fixture()
    }
    TestSuite <|-- TestCase
    TestCase ..> TestHelpers : includes
```
Sources: [testunit-skill/reference/playbook.md:46-85](), [testunit-skill/SKILL.md:81-102]()

## 3. PHPUnit Skill (PHP)

PHPUnit is the standard testing framework for PHP. The skill implements modern PHP 8+ features including Attributes for metadata and Generators for data providers.

### 3.1 Modern Configuration (PHP 8.2+)
The skill promotes the use of Attributes over legacy DocBlock annotations for better static analysis support.

| Attribute | Purpose |
| :--- | :--- |
| `#[Test]` | Marks a method as a test case [phpunit-skill/reference/playbook.md:125](). |
| `#[CoversClass(X::class)]` | Specifies which class is being tested for coverage [phpunit-skill/reference/playbook.md:126](). |
| `#[DataProvider('method')]` | Links a test to a data source [phpunit-skill/reference/playbook.md:127](). |

### 3.2 Mocking and Test Doubles
The skill supports both PHPUnit's native `createMock()` and the more expressive `Mockery` library.

**PHPUnit Mocking Implementation:**
1.  **Creation**: `$this->createMock(Interface::class)` [phpunit-skill/SKILL.md:104]().
2.  **Expectation**: `expects($this->once())` [phpunit-skill/SKILL.md:105]().
3.  **Constraint**: `with($this->isInstanceOf(User::class))` [phpunit-skill/SKILL.md:107]().
4.  **Action**: `willReturn($value)` [phpunit-skill/SKILL.md:108]().

### 3.3 Data Providers with Generators
Using `\Generator` for data providers is recommended for large datasets to reduce memory consumption.
```php
public static function invalidEmailProvider(): \Generator
{
    yield 'no @ symbol' => ['invalid', 'missing @'];
    yield 'no domain' => ['user@', 'missing domain'];
}
```
Sources: [phpunit-skill/reference/playbook.md:180-188]()

## 4. CI/CD and Coverage Integration

All three skills emphasize automated coverage enforcement and environment isolation.

### 4.1 Coverage Tooling
*   **Ruby (RSpec/Test::Unit)**: Uses `SimpleCov`. Configuration typically sets a `minimum_coverage` threshold (e.g., 80-90%) [rspec-skill/reference/playbook.md:31-39](), [testunit-skill/reference/playbook.md:48-54]().
*   **PHP**: Uses `Xdebug` in `coverage` mode. The `phpunit.xml` file defines the `source` directory and the `report` output format (HTML/Clover) [phpunit-skill/reference/playbook.md:31-79]().

### 4.2 Pipeline Architecture
Title: Unit Test Pipeline Data Flow
```mermaid
graph LR
    subgraph "CI Environment"
        VA["vendor/autoload.php"]
        ENV["PHPUnit/RSpec ENV Vars"]
    end

    subgraph "Execution"
        TR["Test Runner"]
        DB["Test Database / Mockery"]
    end

    subgraph "Artifacts"
        COV["Coverage Report (Clover/LCOV)"]
        JUNIT["JUnit XML Results"]
    end

    VA --> TR
    ENV --> TR
    TR --> DB
    TR --> COV
    TR --> JUNIT
```
Sources: [phpunit-skill/reference/playbook.md:23-27](), [rspec-skill/reference/playbook.md:5-19](), [testunit-skill/reference/playbook.md:87-111]()

## 5. Summary Table of Assertions

| Assertion Type | RSpec (Expect) | Test::Unit (Assert) | PHPUnit (Assert) |
| :--- | :--- | :--- | :--- |
| **Equality** | `expect(a).to eq(b)` | `assert_equal(a, b)` | `$this->assertEquals(a, b)` |
| **Identity** | `expect(a).to be(b)` | `assert_same(a, b)` | `$this->assertSame(a, b)` |
| **Exceptions** | `expect {}.to raise_error` | `assert_raise(E) {}` | `$this->expectException(E)` |
| **Regex** | `expect(s).to match(/r/)` | `assert_match(/r/, s)` | `$this->assertMatchesRegularExpression()` |
| **Nullity** | `expect(a).to be_nil` | `assert_nil(a)` | `$this->assertNull(a)` |

Sources: [rspec-skill/SKILL.md:52-89](), [testunit-skill/SKILL.md:55-77](), [phpunit-skill/SKILL.md:80-97]()

---

# Page: BDD Testing Skills

# BDD Testing Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [behat-skill/reference/advanced-patterns.md](behat-skill/reference/advanced-patterns.md)
- [behat-skill/reference/playbook.md](behat-skill/reference/playbook.md)
- [behave-skill/SKILL.md](behave-skill/SKILL.md)
- [behave-skill/reference/playbook.md](behave-skill/reference/playbook.md)
- [cucumber-skill/SKILL.md](cucumber-skill/SKILL.md)
- [cucumber-skill/reference/playbook.md](cucumber-skill/reference/playbook.md)
- [gauge-skill/SKILL.md](gauge-skill/SKILL.md)
- [gauge-skill/reference/playbook.md](gauge-skill/reference/playbook.md)
- [selenium-skill/reference/playbook.md](selenium-skill/reference/playbook.md)
- [specflow-skill/SKILL.md](specflow-skill/SKILL.md)

</details>



Behavior-Driven Development (BDD) skills in the Agent Skills repository provide a structured approach to bridge the gap between business requirements and executable code. These skills leverage Gherkin or Markdown to define specifications that are then bound to automated test code across various languages and frameworks.

## Architecture of BDD Skills

All BDD skills in this repository follow a common four-layer architecture that separates business logic from technical implementation.

### 1. Specification Layer
The entry point where scenarios are defined using natural language.
*   **Gherkin:** Used by Cucumber, SpecFlow, Behave, and Behat. Uses `Given/When/Then` keywords [cucumber-skill/SKILL.md:26-59]().
*   **Markdown:** Used by Gauge. Uses headings for scenarios and bullet points for steps [gauge-skill/SKILL.md:28-55]().

### 2. Step Definition / Binding Layer
The "glue" code that maps natural language steps to executable functions.
*   **Attributes/Annotations:** Frameworks use decorators like `@Given` (Java/Python) [cucumber-skill/SKILL.md:71-75]() or `[Given]` (C#) [specflow-skill/SKILL.md:73-77]() to link Gherkin text to methods.
*   **Regex/Cucumber Expressions:** Used to extract parameters from steps, such as strings or numbers [behave-skill/SKILL.md:69-73]().

### 3. Page Object / Domain Layer
Encapsulates the technical details of the system under test (SUT).
*   **UI Testing:** Uses Page Objects to interact with WebDrivers [behat-skill/reference/playbook.md:81-83]().
*   **API Testing:** Uses client libraries (e.g., `requests` in Python, `Guzzle` in PHP) to perform REST actions [behave-skill/reference/playbook.md:184-210]().

### 4. Infrastructure Layer
Handles lifecycle, state, and external integrations.
*   **Hooks:** `Before` and `After` routines for setup (e.g., starting a browser) and teardown [cucumber-skill/SKILL.md:130-147]().
*   **Context Injection:** Sharing state between steps using objects like `ScenarioContext` [cucumber-skill/reference/playbook.md:197-210]() or `context` in Behave [behave-skill/SKILL.md:105-107]().

## System Mapping: Natural Language to Code

The following diagrams illustrate how BDD frameworks translate human-readable specifications into technical execution.

### Gherkin Execution Flow (Cucumber/SpecFlow/Behave)
This diagram shows how a Gherkin feature file triggers specific code entities.

```mermaid
graph TD
    subgraph "Natural Language Space (Feature File)"
        SF["Scenario: Successful login"]
        G1["Given I am on the login page"]
        W1["When I enter 'user@test.com'"]
    end

    subgraph "Code Entity Space (Step Definitions & Hooks)"
        H1["@Before / BeforeScenario"]
        SD1["@Given('I am on the login page')<br/>step_on_login(context)"]
        SD2["@When('I enter {string}')<br/>step_enter_email(context, text)"]
        PO1["LoginPage.navigate()"]
        PO2["LoginPage.enterEmail(email)"]
    end

    SF --> H1
    G1 -.-> SD1
    W1 -.-> SD2
    SD1 --> PO1
    SD2 --> PO2
```
Sources: [cucumber-skill/SKILL.md:26-102](), [behave-skill/SKILL.md:21-98](), [specflow-skill/SKILL.md:21-109]()

### Gauge Markdown Execution Flow
Gauge uses Markdown for specifications and maintains state via DataStores.

```mermaid
graph TD
    subgraph "Specification Space (.spec / .cpt)"
        MS["## Scenario Heading"]
        ST["* Navigate to '/login'"]
        CP["* Log in as 'admin'"]
    end

    subgraph "Implementation Space (Java/Python/JS)"
        IM1["@Step('Navigate to <url>')<br/>navigateTo(url)"]
        DS["ScenarioDataStore / context"]
        DRV["DriverFactory.getDriver()"]
    end

    MS --> DS
    ST -.-> IM1
    CP -.-> IM1
    IM1 --> DRV
```
Sources: [gauge-skill/SKILL.md:26-90](), [gauge-skill/reference/playbook.md:165-231]()

## BDD Framework Comparison

| Framework | Primary Language | Spec Format | Dependency Injection | Key Config File |
| :--- | :--- | :--- | :--- | :--- |
| **Cucumber** | Java, JS, Ruby | Gherkin | PicoContainer (Java) | `cucumber.xml` / `pom.xml` |
| **SpecFlow** | C# (.NET) | Gherkin | BoDi | `specflow.json` |
| **Behave** | Python | Gherkin | `context` object | `behave.ini` |
| **Behat** | PHP | Gherkin | Symfony Container | `behat.yml` |
| **Gauge** | Multi-language | Markdown | Built-in DataStores | `manifest.json` |

Sources: [cucumber-skill/reference/playbook.md:5-31](), [specflow-skill/SKILL.md:140-145](), [behave-skill/reference/playbook.md:37-54](), [behat-skill/reference/playbook.md:20-72](), [gauge-skill/reference/playbook.md:54-71]()

## Cloud Integration (TestMu AI)

All BDD skills support cloud execution via the `LT:Options` capability. This is typically configured in the **Hooks** or **Infrastructure** layer to ensure every scenario runs in a clean remote environment.

*   **Java (Cucumber):** Configured in `CucumberHooks.java` using `RemoteWebDriver` [cucumber-skill/SKILL.md:185-197]().
*   **Python (Behave):** Configured in `environment.py` within the `before_scenario` hook [behave-skill/SKILL.md:140-161]().
*   **C# (SpecFlow):** Configured in `Hooks.cs` using `AddAdditionalOption("LT:Options", ...)` [specflow-skill/SKILL.md:156-175]().

## Detailed BDD Skill Pages

For specific implementation details, directory structures, and advanced patterns for each framework, see the child pages:

*   **[Cucumber Skill — Java, JavaScript, and Ruby](#4.1)**: Deep dive into Gherkin, PicoContainer, and parallel execution.
*   **[SpecFlow Skill — .NET BDD with Gherkin](#4.2)**: Covers C# bindings, BoDi injection, and LivingDoc.
*   **[Behave, Behat, Gauge, Lettuce, and Serenity BDD Skills](#4.3)**: Covers Python, PHP, and Markdown-based BDD testing.

---

# Page: Cucumber Skill — Java, JavaScript, and Ruby

# Cucumber Skill — Java, JavaScript, and Ruby

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cucumber-skill/SKILL.md](cucumber-skill/SKILL.md)
- [cucumber-skill/reference/advanced-patterns.md](cucumber-skill/reference/advanced-patterns.md)
- [cucumber-skill/reference/playbook.md](cucumber-skill/reference/playbook.md)
- [specflow-skill/SKILL.md](specflow-skill/SKILL.md)

</details>



The Cucumber skill provides a standardized approach for implementing Behavior-Driven Development (BDD) across multiple language ecosystems. It focuses on the separation of business requirements (Gherkin) from technical implementation (Step Definitions), utilizing dependency injection for state management and integrating with cloud platforms like LambdaTest for scalable execution.

## 1. System Architecture

The Cucumber implementation follows a four-layer architecture that translates natural language specifications into executable browser actions.

### Natural Language to Code Mapping
The following diagram illustrates how Gherkin elements in `.feature` files map to specific code entities in Java and JavaScript.

**Diagram: Gherkin to Code Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language (Gherkin)"
        A["Feature: User Login"] --> B["Scenario: Successful login"]
        B --> C["Given I am on the login page"]
        B --> D["When I enter 'user@test.com'"]
    end

    subgraph "Code Entity Space (Java/JS)"
        C -.-> E["@Given('I am on the login page')<br/>iAmOnTheLoginPage()"]
        D -.-> F["@When('I enter {string}')<br/>iEnterEmail(String email)"]
        
        E --> G["LoginPage.navigate()"]
        F --> H["LoginPage.enterEmail(email)"]
        
        I["ScenarioContext"] -- "Injects" --> E
        I -- "Injects" --> F
    end

    subgraph "Infrastructure"
        G --> J["WebDriver / Playwright"]
        H --> J
    end
```
**Sources:** [cucumber-skill/SKILL.md:27-59](), [cucumber-skill/SKILL.md:67-101](), [cucumber-skill/reference/playbook.md:145-160]()

## 2. Java Implementation Patterns

The Java implementation leverages **PicoContainer** for Dependency Injection and **TestNG** for parallel execution.

### 2.1 Dependency Injection & State Sharing
To share state between different Step Definition classes without using static variables, the `ScenarioContext` class is injected via PicoContainer [cucumber-skill/reference/playbook.md:145-147]().

*   **ScenarioContext**: Manages a `ThreadLocal<WebDriver>` to ensure thread safety during parallel execution [cucumber-skill/reference/playbook.md:198-205]().
*   **Context Map**: A `ConcurrentHashMap` within `ScenarioContext` allows sharing arbitrary data (e.g., a `productId` created via API) across steps [cucumber-skill/reference/playbook.md:200-209]().

### 2.2 Test Runner & Parallelism
Parallel execution is achieved by overriding the `scenarios()` method in the `TestRunner` class [cucumber-skill/reference/playbook.md:67-73]().

| Component | Configuration | Purpose |
| :--- | :--- | :--- |
| **Runner Class** | `AbstractTestNGCucumberTests` | Integrates Cucumber with the TestNG engine [cucumber-skill/reference/playbook.md:67](). |
| **Parallelism** | `@DataProvider(parallel = true)` | Enables scenario-level parallel execution [cucumber-skill/reference/playbook.md:69-70](). |
| **Thread Count** | `dataproviderthreadcount` | Controlled via `maven-surefire-plugin` in `pom.xml` [cucumber-skill/reference/playbook.md:41-43](). |

**Sources:** [cucumber-skill/reference/playbook.md:5-48](), [cucumber-skill/reference/playbook.md:52-82](), [cucumber-skill/reference/playbook.md:197-210]()

## 3. Lifecycle Hooks

Hooks manage the setup and teardown of the test environment. They are categorized by their execution scope.

**Diagram: Cucumber Lifecycle Flow**
```mermaid
sequenceDiagram
    participant C as Cucumber Runner
    participant H as Hooks.java
    participant S as StepDefinitions.java
    participant D as WebDriver

    C->>H: @Before (order = 0)
    H->>D: new RemoteWebDriver()
    C->>H: @Before("@database")
    H->>H: seedDatabase()
    
    loop Every Step
        C->>H: @BeforeStep
        C->>S: Execute Step
        C->>H: @AfterStep
    end
    
    C->>H: @After
    alt Scenario Failed
        H->>D: takeScreenshot()
        H->>C: scenario.attach(screenshot)
    end
    H->>D: quit()
```
**Sources:** [cucumber-skill/SKILL.md:133-148](), [cucumber-skill/reference/advanced-patterns.md:115-134]()

## 4. Advanced Gherkin Patterns

Cucumber supports complex data structures and reusable logic through specific Gherkin constructs.

*   **Scenario Outlines**: Use `Examples` tables to run the same scenario with different data sets [cucumber-skill/SKILL.md:48-59]().
*   **DataTables**: Used within a single step to pass lists or maps of data to the underlying code [cucumber-skill/reference/playbook.md:119-128]().
*   **Background**: Defines steps that run before every scenario in a feature file to maintain DRY (Don't Repeat Yourself) principles [cucumber-skill/SKILL.md:32-33]().
*   **Custom Parameter Types**: In Java, the `@ParameterType` annotation allows transforming Gherkin strings directly into custom objects like a `Page` object [cucumber-skill/reference/advanced-patterns.md:31-34]().

**Sources:** [cucumber-skill/SKILL.md:24-59](), [cucumber-skill/reference/playbook.md:183-191](), [cucumber-skill/reference/advanced-patterns.md:81-110]()

## 5. Cloud Integration (TestMu AI / LambdaTest)

Cloud execution is configured by initializing a `RemoteWebDriver` with `LT:Options` capabilities.

### Capability Configuration
Capabilities are passed as a `HashMap` in Java or a nested object in JavaScript to the LambdaTest hub [cucumber-skill/SKILL.md:186-197]().

| Language | Key Function/Class | Endpoint |
| :--- | :--- | :--- |
| **Java** | `RemoteWebDriver` | `https://hub.lambdatest.com/wd/hub` [cucumber-skill/SKILL.md:196]() |
| **JavaScript** | `Builder().usingServer()` | `https://{user}:{key}@hub.lambdatest.com/wd/hub` [cucumber-skill/SKILL.md:201-202]() |

### Environment Variables
The following variables must be set for authentication:
*   `LT_USERNAME`: Your LambdaTest account username [cucumber-skill/SKILL.md:182]().
*   `LT_ACCESS_KEY`: Your LambdaTest access key [cucumber-skill/SKILL.md:182]().

**Sources:** [cucumber-skill/SKILL.md:180-207](), [specflow-skill/SKILL.md:151-175]()

## 6. Reporting and Debugging

The skill implements multiple reporting plugins to provide visibility into test results.

1.  **Allure Reports**: Configured via the `io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm` plugin [cucumber-skill/reference/playbook.md:60]().
2.  **Rerun Plugin**: Generates a `rerun.txt` file containing the locations of failed scenarios, which can be consumed by a `RerunRunner` [cucumber-skill/reference/playbook.md:61](), [cucumber-skill/reference/playbook.md:76-81]().
3.  **HTML/JSON Reports**: Standard Cucumber plugins for CI/CD integration [cucumber-skill/reference/playbook.md:58-59]().

**Sources:** [cucumber-skill/reference/playbook.md:52-82](), [cucumber-skill/reference/playbook.md:228-229]()

---

# Page: SpecFlow Skill — .NET BDD with Gherkin

# SpecFlow Skill — .NET BDD with Gherkin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cucumber-skill/SKILL.md](cucumber-skill/SKILL.md)
- [cucumber-skill/reference/playbook.md](cucumber-skill/reference/playbook.md)
- [detox-skill/SKILL.md](detox-skill/SKILL.md)
- [detox-skill/reference/playbook.md](detox-skill/reference/playbook.md)
- [lettuce-skill/reference/playbook.md](lettuce-skill/reference/playbook.md)
- [selenium-skill/reference/page-object-model.md](selenium-skill/reference/page-object-model.md)
- [specflow-skill/SKILL.md](specflow-skill/SKILL.md)
- [specflow-skill/reference/advanced-patterns.md](specflow-skill/reference/advanced-patterns.md)
- [specflow-skill/reference/playbook.md](specflow-skill/reference/playbook.md)

</details>



SpecFlow is the standard BDD framework for the .NET ecosystem, enabling the bridge between natural language business requirements (Gherkin) and C# executable code. This skill focuses on high-quality test generation using the Page Object Model (POM), dependency injection via BoDi, and seamless integration with the LambdaTest cloud for cross-browser execution.

## System Architecture

The SpecFlow skill implements a multi-layered architecture to separate concerns between business logic, test orchestration, and browser automation.

### Natural Language to Code Mapping

The following diagram illustrates how Gherkin elements in `.feature` files map to specific C# attributes and classes within the SpecFlow framework.

**Gherkin to C# Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space (.feature)"
        A["Feature: User Login"] --> B["Scenario: Successful login"]
        B --> C["Given I am on the login page"]
        B --> D["When I enter 'user@test.com'"]
        B --> E["Then I should see the dashboard"]
    end

    subgraph "Code Entity Space (.cs)"
        F["[Binding] class LoginSteps"]
        G["[Given(@'I am on the login page')]"]
        H["[When(@'I enter '(.*)'')]"]
        I["[Then(@'I should see the dashboard')]"]
        
        F --> G
        F --> H
        F --> I
    end

    C -.-> G
    D -.-> H
    E -.-> I
    B -.-> F
```
Sources: [specflow-skill/SKILL.md:21-53](), [specflow-skill/SKILL.md:57-110]()

## Implementation Details

### Dependency Injection (BoDi)
SpecFlow uses an internal DI container (BoDi) to manage object lifecycles. Instead of static drivers, the skill promotes injecting `ScenarioContext` or custom Page Objects directly into step definition constructors.

*   **ScenarioContext**: Used to share state between steps (e.g., storing a generated user ID) [specflow-skill/SKILL.md:67-71]().
*   **Context Injection**: SpecFlow automatically instantiates and injects classes like `LoginPage` if they are included in the constructor [specflow-skill/SKILL.md:139-146]().

### Lifecycle Management (Hooks)
The `WebDriverHooks` class manages the browser lifecycle using SpecFlow's hook attributes.

| Attribute | Execution Timing | Typical Use Case |
|-----------|------------------|------------------|
| `[BeforeScenario]` | Before every scenario | Driver initialization [specflow-skill/SKILL.md:122-127]() |
| `[AfterScenario]` | After every scenario | `driver.Quit()` and screenshot capture [specflow-skill/SKILL.md:129-134]() |
| `[BeforeTestRun]` | Once before the entire suite | Database migrations or global config [specflow-skill/reference/advanced-patterns.md:89-91]() |

### DriverFactory and Cloud Integration
To support local and cloud execution, the skill utilizes a `DriverFactory` pattern. For LambdaTest, `LT:Options` are passed via `ChromeOptions` to the `RemoteWebDriver`.

**Data Flow: Cloud Driver Initialization**
```mermaid
sequenceDiagram
    participant H as Hooks.cs
    participant DF as DriverFactory
    participant LT as LambdaTest Hub
    
    H->>H: Get LT_USERNAME & LT_ACCESS_KEY
    H->>DF: CreateRemoteDriver(scenarioName)
    DF->>DF: Build Dictionary<string, object> ltOptions
    DF->>LT: POST /wd/hub (with Capabilities)
    LT-->>DF: WebDriver Instance
    DF-->>H: Return IWebDriver
    H->>H: Store in ScenarioContext["driver"]
```
Sources: [specflow-skill/SKILL.md:153-175](), [specflow-skill/reference/playbook.md:48-50]()

## Advanced Gherkin Patterns

### Step Argument Transformation
To keep step definitions clean, `[StepArgumentTransformation]` is used to convert Gherkin strings or tables into strongly-typed C# objects.

*   **Table Conversion**: Use `table.CreateSet<T>()` or `table.CreateInstance<T>()` from the `TechTalk.SpecFlow.Assist` namespace [specflow-skill/reference/advanced-patterns.md:54-63]().
*   **Date Transformation**: Converting "5 days ago" into a `DateTime` object [specflow-skill/reference/advanced-patterns.md:65-67]().

### Scoped Bindings
Bindings can be restricted to specific features or scenarios using tags, preventing step definition collisions.
```csharp
[Binding, Scope(Tag = "smoke")]
public class SmokeSteps { ... }
```
Sources: [specflow-skill/reference/playbook.md:67-68](), [specflow-skill/reference/advanced-patterns.md:75-78]()

## Project Configuration

### .csproj and specflow.json
The project requires specific NuGet packages and configuration for the test runner (NUnit or xUnit) and the LivingDoc generator.

*   **Key Packages**: `SpecFlow.NUnit`, `SpecFlow.Plus.LivingDocPlugin`, `Selenium.WebDriver` [specflow-skill/reference/playbook.md:14-25]().
*   **specflow.json**: Configures the feature language, binding culture, and step assemblies [specflow-skill/reference/playbook.md:57-73]().

## CI/CD and Reporting

### LivingDoc Generation
SpecFlow LivingDoc turns test results into documentation. In CI/CD pipelines, the following command is executed after `dotnet test`:
```bash
livingdoc test-assembly SpecFlowProject.dll -t TestExecution.json
```
Sources: [specflow-skill/SKILL.md:176](), [specflow-skill/reference/playbook.md:17]()

### GitHub Actions Integration
Workflows typically follow a pattern of setting up the .NET environment, installing the LivingDoc CLI, running tests with environment variables for cloud access, and uploading the resulting HTML report.

| Step | Command/Action |
|------|----------------|
| Setup .NET | `actions/setup-dotnet@v4` |
| Install Tools | `dotnet tool install --global SpecFlow.Plus.LivingDoc.CLI` |
| Run Tests | `dotnet test --logger "console;verbosity=normal"` |
| Publish | `actions/upload-artifact@v4` |

Sources: [specflow-skill/reference/playbook.md:230-231](), [specflow-skill/reference/playbook.md:5-26]()

---

# Page: Behave, Behat, Gauge, Lettuce, and Serenity BDD Skills

# Behave, Behat, Gauge, Lettuce, and Serenity BDD Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [behat-skill/reference/advanced-patterns.md](behat-skill/reference/advanced-patterns.md)
- [behat-skill/reference/playbook.md](behat-skill/reference/playbook.md)
- [behave-skill/SKILL.md](behave-skill/SKILL.md)
- [behave-skill/reference/advanced-patterns.md](behave-skill/reference/advanced-patterns.md)
- [behave-skill/reference/playbook.md](behave-skill/reference/playbook.md)
- [gauge-skill/SKILL.md](gauge-skill/SKILL.md)
- [gauge-skill/reference/playbook.md](gauge-skill/reference/playbook.md)
- [lettuce-skill/SKILL.md](lettuce-skill/SKILL.md)
- [lettuce-skill/reference/advanced-patterns.md](lettuce-skill/reference/advanced-patterns.md)
- [lettuce-skill/reference/playbook.md](lettuce-skill/reference/playbook.md)
- [selenium-skill/reference/playbook.md](selenium-skill/reference/playbook.md)
- [serenity-bdd-skill/SKILL.md](serenity-bdd-skill/SKILL.md)
- [serenity-bdd-skill/reference/advanced-patterns.md](serenity-bdd-skill/reference/advanced-patterns.md)
- [serenity-bdd-skill/reference/playbook.md](serenity-bdd-skill/reference/playbook.md)
- [specflow-skill/reference/advanced-patterns.md](specflow-skill/reference/advanced-patterns.md)

</details>



This page provides a technical deep dive into the implementation of five distinct Behavior-Driven Development (BDD) frameworks supported by the Agent Skills ecosystem. It covers the transition from natural language specifications (Gherkin/Markdown) to executable code across Python, PHP, Java, and multi-language environments.

## 1. Behave (Python BDD)

Behave is the primary Python BDD framework, utilizing Gherkin feature files and a `context` object for state management across steps.

### 1.1 Implementation Architecture
The framework relies on a specific directory structure where `features/` contains `.feature` files and a `steps/` subdirectory contains Python implementations.

*   **Context Object**: A shared state container passed to every step definition [behave-skill/SKILL.md:66-67]().
*   **Environment Hooks**: Defined in `environment.py`, these manage the lifecycle of the test runner, such as initializing browsers in `before_scenario` [behave-skill/SKILL.md:105-116]().
*   **Type Registration**: Custom types can be registered using `register_type` to simplify step matching logic [behave-skill/reference/playbook.md:149-153]().

### 1.2 Data Flow and Hooks
The `environment.py` file acts as the orchestration hub for the framework.

| Hook Name | Purpose | Code Entity |
| :--- | :--- | :--- |
| `before_all` | Global setup (e.g., Base URL) | `def before_all(context)` [behave-skill/SKILL.md:105-106]() |
| `before_scenario` | Driver initialization | `context.browser = webdriver.Chrome()` [behave-skill/SKILL.md:108-110]() |
| `after_scenario` | Cleanup and failure handling | `context.browser.quit()` [behave-skill/SKILL.md:112-115]() |

**Sources:** [behave-skill/SKILL.md:100-116](), [behave-skill/reference/playbook.md:15-35]()

---

## 2. Behat (PHP BDD)

Behat is the standard for PHP BDD, frequently integrated with the **Mink** extension for browser automation and **Symfony** for application-level testing.

### 2.1 Mink Integration and Profiles
Behat uses `behat.yml` to define suites and extension settings. Mink allows switching between different drivers (e.g., `selenium2`, `browserkit`) through configuration profiles [behat-skill/reference/playbook.md:20-57]().

### 2.2 Context and Helpers
*   **FeatureContext**: Inherits from `MinkContext` to gain access to built-in browser interactions like `visit()`, `fillField()`, and `pressButton()` [behat-skill/reference/playbook.md:198-222]().
*   **DatabaseHelper**: A common pattern for resetting and seeding the database before scenarios [behat-skill/reference/playbook.md:203-212]().

**Sources:** [behat-skill/reference/playbook.md:5-18](), [behat-skill/reference/playbook.md:20-57](), [behat-skill/reference/playbook.md:198-222]()

---

## 3. Gauge (Markdown Specs)

Gauge differs from Gherkin-based frameworks by using **Markdown** for specifications and supporting multiple language runners (Java, Python, JS, C#, Ruby).

### 3.1 Concepts and DataStores
*   **Concepts (.cpt)**: Reusable groups of steps defined in Markdown, allowing high-level abstractions [gauge-skill/SKILL.md:112-120]().
*   **DataStores**: Gauge provides three scopes for sharing data: `ScenarioDataStore`, `SpecDataStore`, and `SuiteDataStore` [gauge-skill/SKILL.md:157]().

### 3.2 Implementation Mapping
The following diagram bridges the Markdown specification space to the Java implementation space.

**Gauge: Markdown to Java Mapping**
```mermaid
graph TD
    subgraph "Natural Language (Markdown)"
        SPEC["login.spec"]
        CPT["login_actions.cpt"]
    end

    subgraph "Code Entity (Java)"
        STEP_IMPL["LoginSteps.java"]
        FACTORY["DriverFactory.java"]
    end

    SPEC -- "Calls Concept" --> CPT
    SPEC -- "Matches @Step" --> STEP_IMPL
    CPT -- "Matches @Step" --> STEP_IMPL
    STEP_IMPL -- "getDriver()" --> FACTORY
```
**Sources:** [gauge-skill/SKILL.md:26-55](), [gauge-skill/SKILL.md:59-90](), [gauge-skill/reference/playbook.md:129-145]()

---

## 4. Serenity BDD (Screenplay Pattern)

Serenity BDD is a Java-based framework that emphasizes "living documentation" and the **Screenplay Pattern**.

### 4.1 Screenplay vs. Step Library
*   **Step Library**: Uses `@Steps` and `ScenarioSteps` for a simplified Page Object approach [serenity-bdd-skill/reference/playbook.md:181-213]().
*   **Screenplay Pattern**: Focuses on **Actors**, **Tasks**, and **Actions**. An Actor "attemptsTo" perform Tasks using their "Abilities" [serenity-bdd-skill/SKILL.md:80-109]().

### 4.2 Living Documentation
Serenity generates detailed HTML reports that include screenshots for every step, requirement coverage, and test results [serenity-bdd-skill/SKILL.md:111-117]().

**Serenity Screenplay Data Flow**
```mermaid
graph LR
    subgraph "Natural Language"
        GHERKIN["login.feature"]
    end

    subgraph "Screenplay Code"
        ACTOR["Actor (User)"]
        TASK["Task (Login.withCredentials)"]
        ACTION["Action (Enter.theValue)"]
        TARGET["Target (LoginPage.EMAIL_FIELD)"]
    end

    GHERKIN -- "Triggers" --> ACTOR
    ACTOR -- "attemptsTo" --> TASK
    TASK -- "performs" --> ACTION
    ACTION -- "interacts with" --> TARGET
```
**Sources:** [serenity-bdd-skill/SKILL.md:80-109](), [serenity-bdd-skill/reference/playbook.md:90-103]()

---

## 5. Lettuce (Legacy Python BDD)

Lettuce is a legacy Python BDD framework. While similar to Behave, it uses a global `world` object for state and a `terrain.py` file for hooks.

### 5.1 Key Differences from Behave
*   **State**: Uses `lettuce.world` instead of Behave's `context` [lettuce-skill/SKILL.md:45-52]().
*   **Hooks**: Defined in `terrain.py` using decorators like `@before.all` and `@after.each_scenario` [lettuce-skill/SKILL.md:82-100]().
*   **Step Matching**: Uses regex-based decorators `@step(r'...')` [lettuce-skill/SKILL.md:49-50]().

### 5.2 Migration Path
Due to its unmaintained status, a migration path to Behave is recommended, mapping `world` to `context` and `terrain.py` to `environment.py` [lettuce-skill/reference/playbook.md:157-168]().

**Sources:** [lettuce-skill/SKILL.md:19-21](), [lettuce-skill/SKILL.md:79-100](), [lettuce-skill/reference/playbook.md:157-168]()

---

## 6. Framework Comparison Table

| Feature | Behave | Behat | Gauge | Serenity BDD |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python | PHP | Multi (Java/Py/JS) | Java |
| **Spec Format** | Gherkin | Gherkin | Markdown | Gherkin / JUnit |
| **State Mgmt** | `context` | Context Class | DataStores | Actors / Context |
| **Browser Ext** | Selenium | Mink | Screenshot Plugin | Screenplay/WebDriver |
| **Reporting** | Allure/HTML | JUnit/HTML | HTML/XML | Living Doc (HTML) |

**Sources:** [behave-skill/SKILL.md:8-10](), [behat-skill/reference/playbook.md:5-15](), [gauge-skill/SKILL.md:9-14](), [serenity-bdd-skill/SKILL.md:8-10]()

---

# Page: Mobile Testing Skills

# Mobile Testing Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [appium-skill/SKILL.md](appium-skill/SKILL.md)
- [appium-skill/reference/cloud-integration.md](appium-skill/reference/cloud-integration.md)
- [appium-skill/reference/ios-specific.md](appium-skill/reference/ios-specific.md)
- [appium-skill/reference/playbook.md](appium-skill/reference/playbook.md)
- [espresso-skill/SKILL.md](espresso-skill/SKILL.md)
- [espresso-skill/reference/advanced-patterns.md](espresso-skill/reference/advanced-patterns.md)
- [espresso-skill/reference/cloud-integration.md](espresso-skill/reference/cloud-integration.md)
- [espresso-skill/reference/playbook.md](espresso-skill/reference/playbook.md)
- [xcuitest-skill/SKILL.md](xcuitest-skill/SKILL.md)
- [xcuitest-skill/reference/advanced-patterns.md](xcuitest-skill/reference/advanced-patterns.md)
- [xcuitest-skill/reference/playbook.md](xcuitest-skill/reference/playbook.md)

</details>



The Mobile Testing category provides a comprehensive set of skills for automating applications across Android and iOS platforms. These skills cover the full spectrum of mobile automation: from high-level cross-platform frameworks like Appium and Detox to low-level native engines like Espresso and XCUITest, as well as specialized tooling for Flutter.

The ecosystem is built around the **TestMu AI Cloud**, providing access to over 100+ real devices [appium-skill/SKILL.md:34-35](), while maintaining full support for local development using emulators and simulators [appium-skill/SKILL.md:37-38]().

## Automation Ecosystem Overview

Mobile testing in this repository is categorized by the "closeness" to the application code and the underlying automation engine used.

### Conceptual Mapping: Natural Language to Code Entities

This diagram illustrates how user intent and platform requirements map to specific code implementations and drivers within the repository.

Title: Mobile Intent to Code Mapping
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserIntent["'Test Android app'"]
        CloudIntent["'Run on real device farm'"]
        NativeIntent["'Fast, native Android tests'"]
        IOSIntent["'Test iPhone 16'"]
    end

    subgraph "Code Entity Space"
        AndroidDriver["AndroidDriver (Appium)"]
        IOSDriver["IOSDriver (Appium)"]
        EspressoRunner["AndroidJUnitRunner (Espresso)"]
        XCUIRunner["XCUIApplication (XCUITest)"]
        TestMuCloud["mobile-hub.lambdatest.com"]
    end

    UserIntent --> AndroidDriver
    UserIntent --> EspressoRunner
    CloudIntent --> TestMuCloud
    NativeIntent --> EspressoRunner
    IOSIntent --> IOSDriver
    IOSIntent --> XCUIRunner

    %% File Citations
    style AndroidDriver stroke-dasharray: 5 5
    style IOSDriver stroke-dasharray: 5 5
```
Sources: [appium-skill/SKILL.md:82-101](), [espresso-skill/SKILL.md:201-205](), [xcuitest-skill/SKILL.md:193-201]()

## Core Mobile Testing Skills

### Appium Skill — Cross-Platform Mobile Automation
Appium is the primary tool for cross-platform automation, supporting Java, Python, JavaScript, Ruby, and C# [appium-skill/SKILL.md:11-16](). It utilizes the **W3C Actions API** for complex gestures like long presses and swipes [appium-skill/SKILL.md:148-177]().

*   **Android Engine:** `UiAutomator2` [appium-skill/SKILL.md:50]().
*   **iOS Engine:** `XCUITest` [appium-skill/SKILL.md:53]().
*   **Key Pattern:** Thread-safe `AppiumDriver` management using `ThreadLocal` [appium-skill/reference/playbook.md:69-71]().

For details, see [Appium Skill — Cross-Platform Mobile Automation](#5.1).

### Espresso and XCUITest Skills — Native Testing
Native frameworks provide the fastest execution by running within the application process or having direct access to the OS accessibility layer.

*   **Espresso:** Targeted at Android (Kotlin/Java). It uses `onView` matchers and `ViewActions` [espresso-skill/SKILL.md:49-58](). It features automatic synchronization via `IdlingResource` [espresso-skill/reference/playbook.md:181-189]().
*   **XCUITest:** The native Swift framework for iOS. It uses `XCUIApplication` and `XCUIElement` queries [xcuitest-skill/SKILL.md:43-64](). It handles system-level interruptions like permission dialogs via `addUIInterruptionMonitor` [xcuitest-skill/reference/playbook.md:230-240]().

For details, see [Espresso and XCUITest Skills — Native Android and iOS Testing](#5.2).

### Flutter and Detox Skills — Specialized Frameworks
These skills address the unique needs of modern cross-platform development frameworks.

*   **Flutter:** Focuses on `WidgetTester` for unit-style widget tests and integration tests for end-to-end flows.
*   **Detox:** A gray-box testing library for React Native that aims to eliminate flakiness through automatic synchronization.

For details, see [Flutter Testing and Detox Skills — Cross-Platform Mobile](#5.3).

## Shared Mobile Concepts

### Execution Targets: Local vs. Cloud
All mobile skills distinguish between local execution (emulators/simulators) and cloud execution (real devices).

| Feature | Local (Emulator/Simulator) | Cloud (TestMu AI Real Devices) |
| :--- | :--- | :--- |
| **Endpoint** | `http://localhost:4723` [appium-skill/SKILL.md:83]() | `mobile-hub.lambdatest.com/wd/hub` [appium-skill/reference/cloud-integration.md:44]() |
| **Setup** | Android Studio / Xcode [xcuitest-skill/SKILL.md:208-209]() | `LT:Options` Capabilities [appium-skill/reference/cloud-integration.md:33-41]() |
| **App Source** | Local file path [appium-skill/SKILL.md:76]() | `lt://APP_ID` (after upload) [appium-skill/reference/cloud-integration.md:30]() |

### W3C Actions & Gestures
While native frameworks have their own gesture APIs, Appium standardizes mobile interactions using the **PointerInput** and **Sequence** classes [appium-skill/SKILL.md:154-177](). This allows for precise control over touch coordinates and durations for complex interactions like "swipe to delete" or "pinch to zoom".

### Locator Strategy Priority
To maintain maintainable tests across platforms, a strict locator hierarchy is recommended [appium-skill/SKILL.md:103-111]():
1.  **AccessibilityId:** The gold standard for cross-platform stability.
2.  **ID / Resource-ID:** Platform-specific unique identifiers.
3.  **iOS Predicates / Android UiAutomator:** Advanced OS-specific selectors.
4.  **XPath:** Discouraged due to performance overhead and fragility.

### Automation Engine Architecture
The following diagram bridges the high-level framework classes to the low-level drivers that interact with the mobile hardware.

Title: Mobile Driver Architecture
```mermaid
graph LR
    subgraph "Appium Framework"
        AD["AndroidDriver"]
        ID["IOSDriver"]
    end

    subgraph "Native Engines"
        UA2["UiAutomator2 Server"]
        WDA["WebDriverAgent (WDA)"]
    end

    subgraph "Hardware/OS"
        AndroidOS["Android OS"]
        iOS["iOS/iPadOS"]
    end

    AD --> UA2
    ID --> WDA
    UA2 --> AndroidOS
    WDA --> iOS

    %% File Citations
    %% [appium-skill/SKILL.md:50-53]
    %% [appium-skill/reference/playbook.md:35-64]
```
Sources: [appium-skill/SKILL.md:50-53](), [appium-skill/reference/playbook.md:35-64]()

---
**Next Steps:**
- For cross-platform Appium patterns, see [Appium Skill — Cross-Platform Mobile Automation](#5.1).
- For native Android/iOS performance, see [Espresso and XCUITest Skills — Native Android and iOS Testing](#5.2).
- For React Native or Flutter specific testing, see [Flutter Testing and Detox Skills — Cross-Platform Mobile](#5.3).

---

# Page: Appium Skill — Cross-Platform Mobile Automation

# Appium Skill — Cross-Platform Mobile Automation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [appium-skill/SKILL.md](appium-skill/SKILL.md)
- [appium-skill/reference/cloud-integration.md](appium-skill/reference/cloud-integration.md)
- [appium-skill/reference/hybrid-apps.md](appium-skill/reference/hybrid-apps.md)
- [appium-skill/reference/ios-specific.md](appium-skill/reference/ios-specific.md)
- [appium-skill/reference/javascript-patterns.md](appium-skill/reference/javascript-patterns.md)
- [appium-skill/reference/playbook.md](appium-skill/reference/playbook.md)
- [appium-skill/reference/python-patterns.md](appium-skill/reference/python-patterns.md)

</details>



The Appium skill provides a comprehensive framework for generating production-grade mobile automation scripts for Android and iOS. It supports multiple languages including Java, Python, and JavaScript, targeting both local emulators/simulators and the TestMu AI cloud infrastructure with over 100 real devices [appium-skill/SKILL.md:4-10]().

## System Architecture and Flow

The Appium skill transitions from natural language requirements to platform-specific execution engines. It differentiates between Android (UiAutomator2) and iOS (XCUITest) while maintaining a unified Page Object Model (POM) approach where possible [appium-skill/SKILL.md:46-56]().

### Request to Execution Mapping
The following diagram illustrates how user intent is mapped to specific code entities and drivers within the Appium skill.

**Intent to Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Test Android app'"]
        B["'Automate iOS'"]
        C["'Run on Cloud'"]
    end

    subgraph "Code Entity Space (appium-skill)"
        D["UiAutomator2Options"]
        E["XCUITestOptions"]
        F["AndroidDriver"]
        G["IOSDriver"]
        H["LT:Options (HashMap)"]
        I["mobile-hub.lambdatest.com"]
    end

    A --> D
    D --> F
    B --> E
    E --> G
    C --> H
    H --> I
```
Sources: [appium-skill/SKILL.md:46-56](), [appium-skill/reference/cloud-integration.md:25-45](), [appium-skill/reference/cloud-integration.md:51-68]()

## Core Implementation Patterns

### 1. Thread-Safe Driver Management
To support parallel execution, the skill implements a `ThreadLocal` pattern within a `BaseTest` class. This ensures that each test thread maintains its own `AppiumDriver` instance [appium-skill/reference/playbook.md:69-110]().

*   **`BaseTest`**: Manages the lifecycle of the driver using `@BeforeMethod` and `@AfterMethod` [appium-skill/reference/playbook.md:69-71]().
*   **`driverThread`**: A `ThreadLocal<AppiumDriver>` variable that prevents race conditions during parallel runs [appium-skill/reference/playbook.md:70]().
*   **`getDriver()`**: Provides a safe way for Page Objects to access the current thread's driver [appium-skill/reference/playbook.md:109]().

### 2. Cross-Platform Page Objects
The skill utilizes `AppiumFieldDecorator` and specialized annotations to handle element location across different platforms within a single class [appium-skill/reference/playbook.md:129-177]().

| Annotation | Purpose |
| :--- | :--- |
| `@AndroidFindBy` | Locates elements using Android-specific strategies like `accessibility` or `id` [appium-skill/reference/playbook.md:133](). |
| `@iOSXCUITFindBy` | Locates elements using iOS strategies like `iOSNsPredicate` or `accessibility` [appium-skill/reference/playbook.md:134](). |
| `AppiumFieldDecorator` | Enables lazy loading of elements and supports the platform-specific annotations [appium-skill/reference/playbook.md:152](). |

### 3. W3C Actions API (GestureHelper)
Standard `click()` and `sendKeys()` are often insufficient for mobile. The `GestureHelper` class abstracts the complex W3C Actions API for common gestures [appium-skill/reference/playbook.md:182-205]().

**Gesture Implementation Flow**
```mermaid
sequenceDiagram
    participant GH as GestureHelper
    participant PI as PointerInput
    participant SEQ as Sequence
    participant D as AppiumDriver

    GH->>PI: createPointerMove(Duration, Origin, x, y)
    GH->>PI: createPointerDown(MouseButton)
    GH->>SEQ: addAction(move)
    GH->>SEQ: addAction(down)
    GH->>SEQ: addAction(pause)
    GH->>D: perform(List.of(SEQ))
```
Sources: [appium-skill/SKILL.md:154-177](), [appium-skill/reference/playbook.md:182-205]()

## Platform Specifics

### Android (UiAutomator2)
Android automation relies on the `UiAutomator2` engine. Key features include:
*   **Locators**: Priority is given to `AccessibilityId`, followed by `id` (resource-id) and `androidUIAutomator` [appium-skill/SKILL.md:106-126]().
*   **Capabilities**: `setAutoGrantPermissions(true)` is commonly used to bypass system permission popups [appium-skill/reference/playbook.md:41]().

### iOS (XCUITest)
iOS automation uses the `XCUITest` driver, which has unique lifecycle requirements:
*   **WDA (WebDriverAgent)**: Requires specific timeouts like `wdaLaunchTimeout` and `wdaConnectionTimeout` [appium-skill/reference/ios-specific.md:14-15]().
*   **Locators**: Supports `iOSNsPredicateString` and `iOSClassChain` for high-performance element queries [appium-skill/reference/ios-specific.md:22-30]().
*   **Biometrics**: Supports Face ID/Touch ID simulation via `mobile: enrollBiometric` and `mobile: sendBiometricMatch` scripts [appium-skill/reference/ios-specific.md:72-79]().

### Hybrid App Context Switching
For apps containing WebViews, the skill manages transitions between `NATIVE_APP` and `WEBVIEW` contexts [appium-skill/reference/hybrid-apps.md:5-13]().
*   **`getContextHandles()`**: Retrieves all available contexts [appium-skill/reference/hybrid-apps.md:9]().
*   **`context(String name)`**: Switches the driver's focus to the specified WebView or Native view [appium-skill/reference/hybrid-apps.md:13-18]().

## TestMu AI Cloud Integration

Integration with TestMu AI cloud allows tests to run on real mobile devices by routing the `RemoteWebDriver` to the LambdaTest hub [appium-skill/reference/cloud-integration.md:43-45]().

### Data Flow for Cloud Execution
```mermaid
graph LR
    subgraph "Local Environment"
        A["Test Script"] -- "App Upload (curl)" --> B["TestMu App Storage"]
    end
    subgraph "TestMu AI Cloud"
        B -- "lt://APP_ID" --> C["Real Device"]
        D["LT:Options"] -- "Capabilities" --> C
        C -- "lambda-status" --> E["Cloud Dashboard"]
    end
    A -- "RemoteWebDriver(hub_url)" --> C
```
Sources: [appium-skill/reference/cloud-integration.md:7-21](), [appium-skill/reference/cloud-integration.md:33-45](), [appium-skill/reference/cloud-integration.md:99-108]()

### Key Cloud Capabilities (`LT:Options`)
*   **`isRealMobile`**: Must be set to `true` for real device access [appium-skill/reference/cloud-integration.md:37]().
*   **`video` / `network` / `devicelog`**: Enables debugging artifacts on the cloud dashboard [appium-skill/reference/cloud-integration.md:38-40]().
*   **`lambda-status`**: A JavaScript executor command used to report the final test result (passed/failed) to the platform [appium-skill/reference/cloud-integration.md:101-107]().

## Multi-Language Patterns

While Java is the primary reference, the skill provides native patterns for Python and JavaScript.

*   **Python**: Uses `Appium-Python-Client` with `pytest` fixtures for driver setup and teardown [appium-skill/reference/python-patterns.md:6-30]().
*   **JavaScript**: Utilizes `WebdriverIO` as the client, featuring the `~` shorthand for `accessibilityId` locators [appium-skill/reference/javascript-patterns.md:12-34]().

Sources:
- [appium-skill/SKILL.md:4-10]()
- [appium-skill/SKILL.md:46-56]()
- [appium-skill/SKILL.md:106-126]()
- [appium-skill/SKILL.md:154-177]()
- [appium-skill/reference/playbook.md:41]()
- [appium-skill/reference/playbook.md:69-110]()
- [appium-skill/reference/playbook.md:129-177]()
- [appium-skill/reference/playbook.md:182-205]()
- [appium-skill/reference/cloud-integration.md:7-21]()
- [appium-skill/reference/cloud-integration.md:25-45]()
- [appium-skill/reference/cloud-integration.md:51-68]()
- [appium-skill/reference/cloud-integration.md:99-108]()
- [appium-skill/reference/python-patterns.md:6-30]()
- [appium-skill/reference/javascript-patterns.md:12-34]()
- [appium-skill/reference/ios-specific.md:14-15]()
- [appium-skill/reference/ios-specific.md:22-30]()
- [appium-skill/reference/ios-specific.md:72-79]()
- [appium-skill/reference/hybrid-apps.md:5-18]()

---

# Page: Espresso and XCUITest Skills — Native Android and iOS Testing

# Espresso and XCUITest Skills — Native Android and iOS Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [espresso-skill/SKILL.md](espresso-skill/SKILL.md)
- [espresso-skill/reference/advanced-patterns.md](espresso-skill/reference/advanced-patterns.md)
- [espresso-skill/reference/cloud-integration.md](espresso-skill/reference/cloud-integration.md)
- [espresso-skill/reference/playbook.md](espresso-skill/reference/playbook.md)
- [xcuitest-skill/SKILL.md](xcuitest-skill/SKILL.md)
- [xcuitest-skill/reference/advanced-patterns.md](xcuitest-skill/reference/advanced-patterns.md)
- [xcuitest-skill/reference/playbook.md](xcuitest-skill/reference/playbook.md)

</details>



This page provides a technical deep dive into native mobile automation using Espresso for Android and XCUITest for iOS. These skills focus on "gray-box" testing, where tests run inside the application process, providing high synchronization and reliability compared to black-box alternatives.

## 1. Espresso (Android Native)

Espresso is the native testing framework for Android, running as part of the instrumentation process. It provides automatic synchronization between the test actions and the UI thread.

### 1.1 Core Architecture and Lifecycle
Espresso tests are typically written in Kotlin or Java and utilize `ActivityScenarioRule` to manage the lifecycle of the Activity under test.

Title: Espresso Test Flow and Code Entities
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Verify login button is visible'"]
        B["'Type user@test.com into email field'"]
        C["'Wait for network request'"]
    end

    subgraph "Code Entity Space"
        A --> Matcher["onView(withId(R.id.loginButton))"]
        Matcher --> Assertion["check(matches(isDisplayed()))"]
        
        B --> Action["perform(typeText('user@test.com'))"]
        
        C --> Idling["IdlingRegistry.register(countingIdlingResource)"]
    end

    subgraph "Execution Layer"
        Assertion --> Instrumentation["AndroidJUnitRunner"]
        Action --> Instrumentation
        Idling --> Sync["UI Thread Sync"]
    end
```
Sources: [espresso-skill/SKILL.md:39-64](), [espresso-skill/reference/playbook.md:36-57]()

### 1.2 ViewMatchers, ViewActions, and ViewAssertions
The Espresso API is built on three pillars:
*   **ViewMatchers**: Locate views in the hierarchy (e.g., `withId`, `withText`, `withContentDescription`) [espresso-skill/SKILL.md:81-105]().
*   **ViewActions**: Interact with views (e.g., `click()`, `typeText()`, `scrollTo()`, `swipeLeft()`) [espresso-skill/SKILL.md:107-122]().
*   **ViewAssertions**: Verify state (e.g., `matches(isDisplayed())`, `doesNotExist()`) [espresso-skill/SKILL.md:124-134]().

### 1.3 Advanced RecyclerView and Intent Testing
For complex views like `RecyclerView`, Espresso requires the `espresso-contrib` library.
*   **RecyclerViewActions**: Allows scrolling to positions or performing actions on items at specific positions [espresso-skill/reference/playbook.md:142-175]().
*   **Intents**: Using `IntentsTestRule` to validate outgoing intents (e.g., sharing, opening a browser) [espresso-skill/reference/advanced-patterns.md:3-24]().

### 1.4 Synchronization with Idling Resources
To handle asynchronous operations (API calls, animations), Espresso uses `IdlingResource`. The `CountingIdlingResource` is the standard implementation for tracking active background tasks [espresso-skill/reference/playbook.md:177-201]().

Sources: [espresso-skill/reference/playbook.md:90-140](), [espresso-skill/reference/advanced-patterns.md:27-43]()

---

## 2. XCUITest (iOS Native)

XCUITest is Apple's first-party framework for UI testing, integrated directly into Xcode. It uses the `XCTest` framework and communicates with the application via the Accessibility hierarchy.

### 2.1 XCUIApplication and Element Queries
The entry point for any test is `XCUIApplication`. Elements are queried through various collections like `buttons`, `textFields`, and `staticTexts`.

Title: XCUITest Query and Interaction Model
```mermaid
graph LR
    subgraph "Code Entity Space"
        APP["XCUIApplication()"]
        QUERY["app.secureTextFields['passwordInput']"]
        WAIT["waitForExistence(timeout: 5)"]
        ACT["tap() / typeText()"]
    end

    subgraph "System Layer"
        WDA["WebDriverAgent"]
        AX["Accessibility Hierarchy"]
    end

    APP --> QUERY
    QUERY --> WAIT
    WAIT --> ACT
    ACT --> WDA
    WDA --> AX
```
Sources: [xcuitest-skill/SKILL.md:39-77](), [xcuitest-skill/reference/playbook.md:12-57]()

### 2.2 Page Object (Screen) Pattern in Swift
The repository promotes a `Screen` protocol to encapsulate element definitions and common interactions, improving maintainability.

| Entity | Role | Key Function/Property |
| :--- | :--- | :--- |
| `Screen` Protocol | Base interface for page objects | `verifyOnScreen()` [xcuitest-skill/reference/playbook.md:65-74]() |
| `LoginScreen` | Encapsulates login UI | `login(email:password:)` [xcuitest-skill/reference/playbook.md:76-131]() |
| `XCUIElement` Ext | Utility for common actions | `clearAndType(_:)` [xcuitest-skill/reference/playbook.md:168-198]() |

### 2.3 Handling System Alerts
XCUITest provides `addUIInterruptionMonitor` to handle asynchronous system dialogs (e.g., location permissions) that appear during test execution [xcuitest-skill/SKILL.md:127-139](), [xcuitest-skill/reference/playbook.md:224-242]().

---

## 3. Cloud Integration (TestMu AI)

Both Espresso and XCUITest skills support execution on LambdaTest/TestMu AI real device clouds. This involves a three-step process: building the artifacts, uploading them, and triggering the execution via API.

### 3.1 Espresso Cloud Workflow
1.  **Build**: Generate the app APK and the test instrumentation APK using `./gradlew assembleDebug assembleDebugAndroidTest` [espresso-skill/SKILL.md:181-182]().
2.  **Upload**: Send both files to the `realDevice` upload endpoint [espresso-skill/reference/cloud-integration.md:5-19]().
3.  **Execute**: Post a JSON payload to the Espresso build endpoint specifying `app` URL, `testSuite` URL, and target `device` list [espresso-skill/reference/cloud-integration.md:21-37]().

### 3.2 XCUITest Cloud Workflow
1.  **Build**: Create an `.ipa` for the app and a Test Runner `.ipa` (Product → Archive in Xcode) [xcuitest-skill/SKILL.md:181-189]().
2.  **Upload**: Upload both `.ipa` files to LambdaTest [xcuitest-skill/SKILL.md:183-189]().
3.  **Execute**: Trigger the build via the `/xcui/build` endpoint [xcuitest-skill/SKILL.md:191-202]().

### 3.3 Implementation Comparison

| Feature | Espresso | XCUITest |
| :--- | :--- | :--- |
| **Language** | Kotlin / Java | Swift / Objective-C |
| **Artifacts** | App APK + Test APK | App IPA + Runner IPA |
| **Sync** | Automatic (Idling Resources) | Manual (`waitForExistence`) |
| **Wait API** | `IdlingRegistry` | `XCTWaiter` / `NSPredicate` |
| **Gestures** | `ViewActions` (click, swipe) | `XCUIElement` (tap, pinch, rotate) |

Sources: [espresso-skill/SKILL.md:178-206](), [xcuitest-skill/SKILL.md:178-202](), [espresso-skill/reference/cloud-integration.md:1-45]()

---

# Page: Flutter Testing and Detox Skills — Cross-Platform Mobile

# Flutter Testing and Detox Skills — Cross-Platform Mobile

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [detox-skill/SKILL.md](detox-skill/SKILL.md)
- [detox-skill/reference/advanced-patterns.md](detox-skill/reference/advanced-patterns.md)
- [detox-skill/reference/playbook.md](detox-skill/reference/playbook.md)
- [evals/flutter-testing-skill-evals.json](evals/flutter-testing-skill-evals.json)
- [evals/xcuitest-skill-evals.json](evals/xcuitest-skill-evals.json)
- [flutter-testing-skill/SKILL.md](flutter-testing-skill/SKILL.md)
- [flutter-testing-skill/reference/advanced-patterns.md](flutter-testing-skill/reference/advanced-patterns.md)
- [flutter-testing-skill/reference/playbook.md](flutter-testing-skill/reference/playbook.md)
- [selenium-skill/reference/page-object-model.md](selenium-skill/reference/page-object-model.md)
- [specflow-skill/reference/playbook.md](specflow-skill/reference/playbook.md)

</details>



This page provides a technical deep dive into the cross-platform mobile testing capabilities of the TestMu AI Agent. It covers **Flutter** (Dart) for high-performance UI and integration testing, and **Detox** (JavaScript/TypeScript) for gray-box React Native automation. Both frameworks are integrated with the TestMu AI cloud for real-device execution.

---

## 1. Flutter Testing

Flutter testing is divided into three primary tiers: Widget tests (component-level), Integration tests (app-level), and Golden tests (visual regression).

### 1.1 Implementation Architecture
The agent utilizes the `flutter_test` and `integration_test` packages to drive the application. For unit and widget testing, the agent implements mocking using `mockito` or `mocktail` to isolate dependencies.

**Data Flow: Flutter Test Execution**
The following diagram illustrates how the test code interacts with the Flutter framework and the TestMu AI Cloud.

Title: Flutter Test Entity Mapping
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Write a widget test'"]
        B["'Run on real device'"]
        C["'Check visual regression'"]
    end

    subgraph "Code Entity Space (Dart)"
        D["testWidgets()"]
        E["WidgetTester"]
        F["find.byKey()"]
        G["matchesGoldenFile()"]
        H["IntegrationTestWidgetsFlutterBinding"]
    end

    subgraph "Infrastructure"
        I["pubspec.yaml"]
        J["TestMu AI Cloud"]
    end

    A --> D
    A --> E
    D --> F
    C --> G
    B --> H
    H --> J
    D -.-> I
```
Sources: [flutter-testing-skill/SKILL.md:42-86](), [flutter-testing-skill/reference/playbook.md:130-160](), [evals/flutter-testing-skill-evals.json:7-14]()

### 1.2 Key Testing Patterns

| Pattern | Code Entity | Purpose |
|:---|:---|:---|
| **Widget Testing** | `testWidgets(description, callback)` | Renders a widget in a virtual environment for fast UI validation. [flutter-testing-skill/SKILL.md:50-58]() |
| **Finder Strategy** | `find.byKey(Key('id'))` | Best practice for stable selectors over `find.text()`. [flutter-testing-skill/SKILL.md:91-93]() |
| **Frame Pumping** | `tester.pumpAndSettle()` | Advances the clock until no more frames are scheduled (waits for animations). [flutter-testing-skill/SKILL.md:124-128]() |
| **Integration** | `IntegrationTestWidgetsFlutterBinding` | Initializes the binding required for E2E tests on real devices. [flutter-testing-skill/SKILL.md:139-140]() |
| **Golden Tests** | `matchesGoldenFile('path.png')` | Performs pixel-by-pixel comparison against a baseline image. [flutter-testing-skill/SKILL.md:165-174]() |

### 1.3 Dependency Mocking
The agent supports both code-generation (`mockito`) and no-generation (`mocktail`) approaches for mocking services and repositories.

*   **Mockito:** Requires `@GenerateMocks([Class])` and `build_runner`. [flutter-testing-skill/reference/playbook.md:46-52]()
*   **Mocktail:** Uses `Mock` class inheritance and `registerFallbackValue`. [flutter-testing-skill/reference/playbook.md:97-108]()

Sources: [flutter-testing-skill/reference/playbook.md:5-26](), [flutter-testing-skill/reference/playbook.md:46-94](), [flutter-testing-skill/reference/advanced-patterns.md:5-48]()

---

## 2. Detox (React Native) Testing

Detox is a gray-box testing framework for React Native that provides automatic synchronization, eliminating the need for manual `sleep()` or `wait()` calls by monitoring the app's internal state (network, main thread, etc.).

### 2.1 Implementation Architecture
Detox tests are typically written in JavaScript/TypeScript using Jest as the runner. The agent configures `.detoxrc.js` to define build paths and device targets.

Title: Detox Entity Mapping
```mermaid
graph LR
    subgraph "Natural Language Space"
        NL1["'Detox login test'"]
        NL2["'Swipe to delete'"]
        NL3["'Launch with permissions'"]
    end

    subgraph "Code Entity Space (JS/TS)"
        CE1["device.launchApp()"]
        CE2["element(by.id())"]
        CE3["expect().toBeVisible()"]
        CE4["element().swipe()"]
        CE5[".detoxrc.js"]
    end

    subgraph "Native Runners"
        NR1["Espresso (Android)"]
        NR2["XCUITest (iOS)"]
    end

    NL1 --> CE1
    NL1 --> CE2
    NL2 --> CE4
    NL3 --> CE1
    CE1 -.-> CE5
    CE5 --> NR1
    CE5 --> NR2
```
Sources: [detox-skill/SKILL.md:27-52](), [detox-skill/SKILL.md:121-146](), [detox-skill/reference/advanced-patterns.md:59-83]()

### 2.2 Core Detox Operations

*   **Matchers:** The agent prioritizes `by.id('testID')` for stability. [detox-skill/SKILL.md:57-69]()
*   **Actions:** Includes `tap()`, `longPress()`, `typeText()`, and `replaceText()`. Note that `replaceText()` is preferred over `typeText()` for pre-filled fields to avoid appending. [detox-skill/SKILL.md:73-84](), [detox-skill/reference/advanced-patterns.md:111-111]()
*   **Synchronization:** Detox automatically waits for the app to be idle. Manual `waitFor()` is only used for specific timeouts or while-scrolling conditions. [detox-skill/reference/playbook.md:223-227]()
*   **Device Control:** Supports `device.reloadReactNative()`, `device.setOrientation()`, and `device.openURL()` for deep links. [detox-skill/SKILL.md:99-108](), [detox-skill/reference/advanced-patterns.md:67-81]()

### 2.3 Page Object Model (POM) in Detox
The agent implements a `BasePage` and `Screen Object` pattern to encapsulate element selectors and common interactions.

```javascript
class BasePage {
  async tapById(testID) {
    await element(by.id(testID)).tap();
  }
}

class LoginPage extends BasePage {
  get emailInput() { return element(by.id('email_input')); }
  async login(email, password) {
    await this.emailInput.replaceText(email);
    // ...
  }
}
```
Sources: [detox-skill/reference/playbook.md:90-149](), [detox-skill/reference/advanced-patterns.md:5-35]()

---

## 3. Cloud Execution on TestMu AI

Both Flutter and Detox tests can be offloaded to the TestMu AI real-device cloud.

### 3.1 Flutter Cloud Execution
Integration tests are built as native artifacts and uploaded to LambdaTest.
1.  **Build:** `flutter build apk --debug` (Android) or `flutter build ios --simulator` (iOS). [flutter-testing-skill/SKILL.md:230-231]()
2.  **Upload:** Artifacts are sent via the `app/upload/realDevice` endpoint. [flutter-testing-skill/SKILL.md:234-237]()

### 3.2 Detox Cloud Execution
Detox translates tests into native runners (**Espresso** for Android, **XCUITest** for iOS). The agent generates the necessary `curl` commands to trigger these builds.

*   **Android:** Requires `app-debug.apk` and `app-debug-androidTest.apk`. [detox-skill/SKILL.md:154-171]()
*   **iOS:** Requires `.ipa` artifacts for the app and the test runner. [detox-skill/SKILL.md:189-201]()
*   **Trigger:** A POST request to `mobile-api.lambdatest.com/framework/v1/[espresso|xcui]/build` starts the execution. [detox-skill/SKILL.md:173-184](), [detox-skill/SKILL.md:203-214]()

Sources: [detox-skill/SKILL.md:148-214](), [flutter-testing-skill/SKILL.md:225-240](), [evals/xcuitest-skill-evals.json:16-24]()

---

# Page: Cloud Testing and Visual Regression Skills

# Cloud Testing and Visual Regression Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [hyperexecute-skill/SKILL.md](hyperexecute-skill/SKILL.md)
- [shared/testmu-cloud-reference.md](shared/testmu-cloud-reference.md)
- [smartui-skill/SKILL.md](smartui-skill/SKILL.md)
- [smartui-skill/reference/playbook.md](smartui-skill/reference/playbook.md)

</details>



This section provides a high-level overview of the cloud-native capabilities provided by the TestMu AI / LambdaTest platform. These skills enable high-speed parallel test orchestration, automated visual regression testing, and a standardized approach to cloud infrastructure across all supported testing frameworks.

## Cloud Ecosystem Overview

The cloud testing suite is divided into three primary functional areas: shared infrastructure references, high-speed orchestration via HyperExecute, and visual regression via SmartUI.

### Conceptual Architecture: Natural Language to Cloud Entities

The following diagram maps natural language requirements to the specific code entities and configurations used in the cloud skills.

**Cloud Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        NL1["'Run tests in parallel on the cloud'"]
        NL2["'Check for visual UI changes'"]
        NL3["'Test on iPhone 15 and Windows 11'"]
    end

    subgraph "Code Entity Space"
        direction TB
        HE_YAML["hyperexecute.yaml"]
        SUI_CFG["smartui.config.json"]
        LT_OPT["LT:Options Capability"]
        SUI_API["smartuiSnapshot() / smartui.takeScreenshot"]
        HE_CLI["./hyperexecute CLI"]
    end

    NL1 --> HE_YAML
    NL1 --> HE_CLI
    NL2 --> SUI_CFG
    NL2 --> SUI_API
    NL3 --> LT_OPT

    HE_YAML -.->|"defines"| HE_CLI
    SUI_CFG -.->|"configures"| SUI_API
```
**Sources:** [hyperexecute-skill/SKILL.md:22-58](), [smartui-skill/SKILL.md:69-80](), [shared/testmu-cloud-reference.md:102-123]()

---

## 6.1 TestMu AI Cloud Integration — Shared Reference

The **Shared Reference** serves as the foundational configuration guide for every cloud-enabled skill in the repository. It defines the standard authentication methods, browser/platform matrices, and the `LT:Options` capability structure required to route tests to the LambdaTest Selenium Hub or Playwright CDP WebSocket.

*   **Authentication**: Requires `LT_USERNAME` and `LT_ACCESS_KEY` [shared/testmu-cloud-reference.md:18-27]().
*   **Endpoints**: Connects via `wss://cdp.lambdatest.com/playwright` or `https://hub.lambdatest.com/wd/hub` [shared/testmu-cloud-reference.md:29-41]().
*   **Capabilities**: Standardized `LT:Options` for network logs, video recording, and geo-location [shared/testmu-cloud-reference.md:102-123]().
*   **Status Reporting**: Explicitly marking tests as `passed` or `failed` via `lambdatest_action` or `lambda-status` [shared/testmu-cloud-reference.md:125-159]().

For details, see [TestMu AI Cloud Integration — Shared Reference](#6.1).

**Sources:** [shared/testmu-cloud-reference.md:1-201]()

---

## 6.2 HyperExecute Skill — High-Speed Parallel Orchestration

**HyperExecute** is a framework-agnostic test orchestration platform that provides faster execution than standard grids by moving the orchestration logic closer to the execution environment.

*   **Orchestration Modes**: Supports `autosplit` (dynamic test distribution), `matrix` (cross-browser/OS), and `hybrid` modes [hyperexecute-skill/SKILL.md:33-79]().
*   **Discovery**: Uses `testDiscovery` commands to find test files dynamically at runtime [hyperexecute-skill/SKILL.md:43-46]().
*   **Execution**: Controlled via the `hyperexecute.yaml` file and the HyperExecute CLI [hyperexecute-skill/SKILL.md:22-58](), [hyperexecute-skill/SKILL.md:102-110]().

For details, see [HyperExecute Skill — High-Speed Parallel Test Orchestration](#6.2).

**Sources:** [hyperexecute-skill/SKILL.md:1-169]()

---

## 6.3 SmartUI Skill — Visual Regression Testing

**SmartUI** provides automated visual regression testing by capturing screenshots and comparing them against established baselines using AI-driven pixel-to-pixel and DOM-aware comparisons.

*   **Integration**: Works with Playwright, Selenium, Cypress, and Puppeteer [smartui-skill/SKILL.md:3-9]().
*   **SDK Usage**: Uses `smartuiSnapshot(page, name)` for Playwright [smartui-skill/SKILL.md:27-43]() or `smartui.takeScreenshot` script injection for Selenium [smartui-skill/SKILL.md:47-52]().
*   **Configuration**: Managed via `smartui.config.json` (formerly `.smartui.json`), defining browsers and viewports [smartui-skill/reference/playbook.md:33-56](), [smartui-skill/SKILL.md:69-80]().
*   **Workflow**: Follows a "Baseline → Comparison → Approval" workflow managed in the SmartUI dashboard [smartui-skill/SKILL.md:88-94]().

For details, see [SmartUI Skill — Visual Regression Testing](#6.3).

**Sources:** [smartui-skill/SKILL.md:1-148](), [smartui-skill/reference/playbook.md:1-216]()

---

## Skill Relationship Matrix

The following table describes how these skills interact during a typical CI/CD execution.

| Feature | Shared Reference | HyperExecute | SmartUI |
| :--- | :--- | :--- | :--- |
| **Primary Goal** | Connectivity & Metadata | Execution Speed | Visual Accuracy |
| **Config File** | Code-based (Capabilities) | `hyperexecute.yaml` | `smartui.config.json` |
| **Trigger** | `RemoteWebDriver` init | `./hyperexecute` CLI | `smartuiSnapshot` API |
| **Cloud Asset** | Video/Network Logs | Parallel Runner Nodes | Diff Screenshots |

**Interaction Flow**
```mermaid
sequenceDiagram
    participant Dev as Developer / CI
    participant HE as HyperExecute CLI
    participant LT as LambdaTest Cloud
    participant SUI as SmartUI Engine

    Dev->>HE: ./hyperexecute --config hyperexecute.yaml
    HE->>LT: Provision parallel nodes
    LT->>LT: Initialize Driver (using Shared Reference caps)
    LT->>SUI: Capture screenshots (smartuiSnapshot)
    SUI->>SUI: Compare against Baseline
    LT->>Dev: Return Test Results & Visual Diffs
```
**Sources:** [hyperexecute-skill/SKILL.md:102-110](), [smartui-skill/SKILL.md:88-94](), [shared/testmu-cloud-reference.md:102-123]()

---

# Page: TestMu AI Cloud Integration — Shared Reference

# TestMu AI Cloud Integration — Shared Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [playwright-skill/scripts/validate-config.py](playwright-skill/scripts/validate-config.py)
- [shared/scripts/check-tunnel.sh](shared/scripts/check-tunnel.sh)
- [shared/scripts/validate-capabilities.py](shared/scripts/validate-capabilities.py)
- [shared/testmu-cloud-reference.md](shared/testmu-cloud-reference.md)

</details>



This page serves as the centralized technical reference for all cloud-enabled skills within the `agent-skills` repository. It defines the authentication protocols, connection endpoints, platform matrices, and specialized capabilities required to execute automated tests on the TestMu AI / LambdaTest cloud infrastructure [shared/testmu-cloud-reference.md:1-3]().

## Cloud Architecture & Connectivity

The integration bridges local test execution with remote cloud environments using two primary communication protocols depending on the framework type.

### Connection Endpoints
*   **CDP WebSocket:** Modern frameworks like Playwright, Puppeteer, and Cypress connect via the Chrome DevTools Protocol (CDP) [shared/testmu-cloud-reference.md:29-35]().
*   **Selenium Hub:** Traditional WebDriver-based frameworks (Selenium, Appium, WebdriverIO) use the standard JSON Wire Protocol / W3C endpoint [shared/testmu-cloud-reference.md:37-41]().

### Connectivity Flow Diagram

The following diagram illustrates how local test runners authenticate and establish sessions with the cloud grid.

**Cloud Session Initiation Flow**
```mermaid
graph TD
    subgraph "Local Environment"
        A["Test Runner (Playwright/Selenium)"] --> B{"Auth Check"}
        B -- "LT_USERNAME" --> C["Credentials"]
        B -- "LT_ACCESS_KEY" --> C
    end

    subgraph "LambdaTest Cloud Grid"
        D["CDP Gateway (wss://cdp.lambdatest.com)"]
        E["Selenium Hub (https://hub.lambdatest.com)"]
    end

    C -->|"Capabilities JSON"| D
    C -->|"RemoteWebDriver"| E

    D --> F["Remote Browser/Device"]
    E --> F
```
**Sources:** [shared/testmu-cloud-reference.md:18-41](), [shared/scripts/validate-capabilities.py:56-63]()

## Authentication

All cloud-enabled skills expect two mandatory environment variables for authentication [shared/testmu-cloud-reference.md:20-25]().

| Variable | Description |
| :--- | :--- |
| `LT_USERNAME` | Your LambdaTest account username |
| `LT_ACCESS_KEY` | Your unique API access key |

The `validate-capabilities.py` script specifically checks for these keys within the `LT:Options` block and returns an error if they are missing or set to `"None"` [shared/scripts/validate-capabilities.py:56-63]().

## Platform and Browser Matrix

### Desktop Browsers
TestMu AI supports a variety of browsers, with specific identifiers for Playwright-optimized builds [shared/testmu-cloud-reference.md:45-54]().

| Browser | Value | Supported Frameworks |
| :--- | :--- | :--- |
| Chrome | `Chrome` | All |
| Edge | `MicrosoftEdge` | All |
| Playwright Chromium | `pw-chromium` | Playwright |
| Playwright Firefox | `pw-firefox` | Playwright |
| Playwright WebKit | `pw-webkit` | Playwright |
| Firefox | `Firefox` | Selenium |
| Safari | `Safari` | Selenium (macOS only) |

### Desktop Operating Systems
Desktop tests must specify a `platform` within `LT:Options` [shared/testmu-cloud-reference.md:55-67](). Validated platforms include Windows 10/11 and macOS versions from Catalina to Sequoia [shared/scripts/validate-capabilities.py:19-23]().

## Mobile Device Catalog

Mobile testing requires `platformName` (`android` or `ios`) and `isRealMobile: true` [shared/testmu-cloud-reference.md:70-88]().

### Android Devices
| Device | `deviceName` | OS Versions |
| :--- | :--- | :--- |
| Pixel 8 | `Pixel 8` | 14 |
| Galaxy S24 | `Galaxy S24` | 14 |
| OnePlus 11 | `OnePlus 11` | 13 |

### iOS Devices
**Critical Requirement:** iOS devices always use the `webkit` browser. Attempting to use `chromium` on iOS will trigger a validation error [shared/testmu-cloud-reference.md:90](), [shared/scripts/validate-capabilities.py:74-75]().

| Device | `deviceName` | OS Versions |
| :--- | :--- | :--- |
| iPhone 16 Pro Max | `iPhone 16 Pro Max` | 18 |
| iPhone 15 | `iPhone 15` | 17, 18 |
| iPad Pro 12.9 | `iPad Pro 12.9 (2022)` | 16, 17 |

**Sources:** [shared/testmu-cloud-reference.md:68-101](), [shared/scripts/validate-capabilities.py:65-75]()

## LT:Options Capability Reference

The `LT:Options` object is the primary configuration block for cloud behavior.

| Capability | Type | Role |
| :--- | :--- | :--- |
| `build` | string | Groups tests in the dashboard [shared/testmu-cloud-reference.md:107]() |
| `network` | boolean | Captures network logs [shared/testmu-cloud-reference.md:111]() |
| `video` | boolean | Records execution video [shared/testmu-cloud-reference.md:112]() |
| `tunnel` | boolean | Enables Lambda Tunnel for localhost [shared/testmu-cloud-reference.md:114]() |
| `geoLocation` | string | Sets country code (e.g., `US`, `GB`) [shared/testmu-cloud-reference.md:116]() |

**Sources:** [shared/testmu-cloud-reference.md:102-124](), [shared/scripts/validate-capabilities.py:26-32]()

## Implementation: Test Status Reporting

Cloud tests are marked as "Completed" by default. To reflect actual assertion results in the dashboard, frameworks must explicitly send a status update [shared/testmu-cloud-reference.md:127]().

### Logic Mapping: Language to Cloud Action

```mermaid
graph LR
    subgraph "Language Execution"
        JS["JavaScript/TypeScript"]
        JV["Java/C#/Python/Ruby"]
    end

    subgraph "Cloud Action Entity"
        LTA["lambdatest_action"]
        LST["lambda-status"]
    end

    JS -->| "page.evaluate()" | LTA
    JV -->| "execute_script()" | LST

    LTA --> Result["Dashboard Status: Passed/Failed"]
    LST --> Result
```

*   **JS/TS (Playwright/Cypress):** Uses `page.evaluate` to send a JSON string containing `setTestStatus` [shared/testmu-cloud-reference.md:130-137]().
*   **Selenium/Appium (Java/Python/Ruby/C#):** Uses `executeScript` with the string `"lambda-status=passed"` [shared/testmu-cloud-reference.md:139-159]().

**Sources:** [shared/testmu-cloud-reference.md:125-160]()

## Localhost Testing via Lambda Tunnel

To test applications running on `localhost`, a secure tunnel must be established using the `LT` binary [shared/testmu-cloud-reference.md:161-169]().

### Validation Workflow
The repository provides `shared/scripts/check-tunnel.sh` to verify tunnel availability before test execution.

1.  **Binary Check:** Verifies `./LT` or `LT` is in the path [shared/scripts/check-tunnel.sh:9-14]().
2.  **Process Check:** Uses `pgrep` to find running tunnel processes [shared/scripts/check-tunnel.sh:17-18]().
3.  **Name Verification:** Ensures the `tunnelName` in the running process matches the one provided in capabilities [shared/scripts/check-tunnel.sh:22-30]().

**Sources:** [shared/testmu-cloud-reference.md:161-176](), [shared/scripts/check-tunnel.sh:1-39]()

## Validation Scripts

The repository includes scripts to ensure configurations adhere to cloud requirements.

### `validate-capabilities.py`
This script performs schema validation on the capabilities JSON [shared/scripts/validate-capabilities.py:1-12]().
*   **Errors:** Missing `browserName`, invalid `platform`, missing `user`/`accessKey`, or incorrect browser for iOS [shared/scripts/validate-capabilities.py:39-83]().
*   **Warnings:** Missing `build` tags, or disabled `video`/`network` logs [shared/scripts/validate-capabilities.py:85-90]().

### `validate-config.py` (Playwright)
Specifically for Playwright, this script checks `playwright.config.ts` [playwright-skill/scripts/validate-config.py:1-10]().
*   **Cloud Project Format:** Ensures project names follow `browserName:version:platform@lambdatest` [playwright-skill/scripts/validate-config.py:44-51]().
*   **Anti-Patterns:** Flags the use of `waitForTimeout` [playwright-skill/scripts/validate-config.py:32-33]().

**Sources:** [shared/scripts/validate-capabilities.py:1-128](), [playwright-skill/scripts/validate-config.py:1-106]()

---

# Page: HyperExecute Skill — High-Speed Parallel Test Orchestration

# HyperExecute Skill — High-Speed Parallel Test Orchestration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [hyperexecute-skill/SKILL.md](hyperexecute-skill/SKILL.md)
- [hyperexecute-skill/reference/playbook.md](hyperexecute-skill/reference/playbook.md)

</details>



HyperExecute is a high-speed test orchestration platform provided by LambdaTest that allows for blazing-fast test execution through intelligent sharding and parallelization. This skill enables the generation of `hyperexecute.yaml` configurations, CLI execution patterns, and framework-specific optimizations for Playwright, Selenium, Cypress, and more [hyperexecute-skill/SKILL.md:1-8]().

## §1 Core Configuration & Orchestration Modes

HyperExecute operates using a YAML configuration file that defines how tests are discovered, distributed, and executed. It supports three primary orchestration modes: **Autosplit**, **Matrix**, and **Hybrid**.

### Configuration Schema
The `hyperexecute.yaml` file controls the execution lifecycle, including environment setup (`pre`), test identification (`testDiscovery`), and execution (`testRunnerCommand`) [hyperexecute-skill/reference/playbook.md:6-46]().

| Key | Description | Example |
|:---|:---|:---|
| `version` | Configuration version | `0.1` |
| `runson` | Execution OS (linux, win, mac) | `linux` |
| `concurrency` | Number of parallel machines/containers | `15` |
| `autosplit` | Enable automatic test distribution | `true` |
| `testDiscovery` | Command to find test files/methods | `grep -rn 'test\(' ...` |
| `testRunnerCommand`| Command to execute a single test unit | `npx playwright test $test` |

### Orchestration Modes

1.  **Autosplit Mode**: Automatically distributes tests across available concurrency slots. It uses `testDiscovery` to find tests and `$test` as a placeholder in the runner command [hyperexecute-skill/SKILL.md:26-58]().
2.  **Matrix Mode**: Executes the same set of tests across multiple combinations of browsers, OS, or environments [hyperexecute-skill/reference/playbook.md:118-128]().
3.  **Hybrid Mode**: Combines static test suite definitions with dynamic discovery [hyperexecute-skill/SKILL.md:79-98]().

### Data Flow: Natural Language to HyperExecute YAML
This diagram maps natural language requirements to the specific YAML entities used in the HyperExecute skill.

"HyperExecute Configuration Logic"
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Run 20 tests in parallel'"]
        B["'Retry flaky tests'"]
        C["'Run on Chrome and Firefox'"]
        D["'Install dependencies first'"]
    end

    subgraph "Code Entity Space (hyperexecute.yaml)"
        A --> A1["concurrency: 20"]
        A --> A2["autosplit: true"]
        B --> B1["retryOnFailure: true"]
        B --> B2["maxRetries: 2"]
        C --> C1["matrix:"]
        C1 --> C2["browser: ['chrome', 'firefox']"]
        D --> D1["pre:"]
        D1 --> D2["- npm install"]
    end
```
Sources: [hyperexecute-skill/SKILL.md:26-77](), [hyperexecute-skill/reference/playbook.md:157-162]()

---

## §2 Framework-Specific Implementations

HyperExecute is framework-agnostic but requires specific `testDiscovery` and `testRunnerCommand` patterns to extract the maximum performance for different ecosystems.

### Playwright Implementation
Playwright configurations typically use `grep` for discovery and the `$test` variable for sharding [hyperexecute-skill/reference/playbook.md:6-31]().

```yaml
testDiscovery:
  type: raw
  mode: dynamic
  command: grep -rn 'test\(' tests/ --include='*.spec.ts' -l

testRunnerCommand: npx playwright test $test --reporter=list
```

### Selenium Java Implementation
For Maven-based Selenium projects, the discovery command parses Java files to identify `@Test` annotations [hyperexecute-skill/reference/playbook.md:81-104]().

```yaml
pre:
  - mvn -Dmaven.test.skip=true clean install

testDiscovery:
  type: raw
  mode: dynamic
  command: grep -rn '@Test' src/test --include='*.java' -l | sed 's/.*\///' | sed 's/\.java//'

testRunnerCommand: mvn test -Dtest=$test -pl module-name
```

### Cypress Implementation
Cypress requires the installation of the binary in the `pre` step and utilizes the `--spec` flag for execution [hyperexecute-skill/reference/playbook.md:48-72]().

```yaml
pre:
  - npm ci
  - npx cypress install

testDiscovery:
  type: raw
  mode: dynamic
  command: find cypress/e2e -name '*.cy.ts' -o -name '*.cy.js'

testRunnerCommand: npx cypress run --spec $test
```

Sources: [hyperexecute-skill/reference/playbook.md:5-111](), [hyperexecute-skill/SKILL.md:114-145]()

---

## §3 Advanced Features & CLI Usage

### Smart Features
HyperExecute provides built-in resilience and performance features:
*   **Smart Ordering**: Runs recently failed tests first to shorten the feedback loop [hyperexecute-skill/reference/playbook.md:159]().
*   **Artifact Management**: Automatically uploads logs, videos, and reports using the `uploadArtefacts` key [hyperexecute-skill/reference/playbook.md:32-35]().
*   **Caching**: Speeds up the `pre` step by caching `node_modules` or `.m2` directories using `cacheKey` and `cacheDirectories` [hyperexecute-skill/reference/playbook.md:36-38]().
*   **Tunnels**: Enables testing of private/local environments by setting `tunnel: true` [hyperexecute-skill/reference/playbook.md:147-155]().

### CLI Execution
The `hyperexecute` binary is used to trigger jobs from local machines or CI/CD runners [hyperexecute-skill/reference/playbook.md:214-256]().

"CLI Execution Flow"
```mermaid
graph LR
    subgraph "CLI Entity Space"
        CLI["hyperexecute binary"]
        YAML["hyperexecute.yaml"]
        VARS["--vars 'KEY=VAL'"]
    end

    subgraph "Execution Process"
        START["./hyperexecute"] --> AUTH["--user & --key"]
        AUTH --> CFG["--config hyperexecute.yaml"]
        CFG --> DISCOVERY["testDiscovery Command"]
        DISCOVERY --> SHARD["Orchestration Engine"]
        SHARD --> RUN["Parallel Execution"]
    end
```
Sources: [hyperexecute-skill/reference/playbook.md:230-256](), [hyperexecute-skill/SKILL.md:100-110]()

### CLI Installation Commands
| OS | Command |
|:---|:---|
| Linux | `curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute` |
| macOS | `curl -O https://downloads.lambdatest.com/hyperexecute/darwin/hyperexecute` |
| Windows | `curl -O https://downloads.lambdatest.com/hyperexecute/windows/hyperexecute.exe` |

Sources: [hyperexecute-skill/reference/playbook.md:216-228]()

---

## §4 CI/CD Pipeline Integration

HyperExecute is designed to be triggered from CI/CD pipelines, offloading the heavy lifting of test execution from the CI runner to the HyperExecute cloud.

### GitHub Actions Example
Integration involves downloading the CLI and executing it with repository secrets [hyperexecute-skill/reference/playbook.md:262-289]().

```yaml
jobs:
  hyperexecute:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run HyperExecute
        run: |
          curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute
          chmod +x hyperexecute
          ./hyperexecute \
            --user ${{ secrets.LT_USERNAME }} \
            --key ${{ secrets.LT_ACCESS_KEY }} \
            --config hyperexecute.yaml
```

Sources: [hyperexecute-skill/reference/playbook.md:260-305]()

---

# Page: SmartUI Skill — Visual Regression Testing

# SmartUI Skill — Visual Regression Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [smartui-skill/SKILL.md](smartui-skill/SKILL.md)
- [smartui-skill/reference/playbook.md](smartui-skill/reference/playbook.md)

</details>



The SmartUI skill provides automated visual regression testing capabilities by capturing screenshots and performing pixel-by-pixel comparisons on the LambdaTest cloud. It is framework-agnostic, supporting integration with Playwright, Selenium, Cypress, and Puppeteer, as well as standalone static URL crawling and Storybook component testing [smartui-skill/SKILL.md:3-9]().

## System Architecture and Data Flow

The SmartUI workflow transitions from local test execution to cloud-based visual analysis. Tests are executed via the `@lambdatest/smartui-cli`, which orchestrates the screenshot capture and uploads them to the SmartUI dashboard for comparison against baselines.

### Visual Regression Lifecycle

| Phase | Description | Key Entity |
| :--- | :--- | :--- |
| **Initialization** | Creation of `smartui.config.json` defining browsers and viewports. | `smartui config:create` [smartui-skill/SKILL.md:139-139]() |
| **Execution** | Wrapper command `smartui exec` runs the underlying test suite. | `npx smartui exec` [smartui-skill/SKILL.md:64-66]() |
| **Capture** | Screenshots are triggered via SDK or JavaScript injection. | `smartuiSnapshot` / `smartui.takeScreenshot` [smartui-skill/SKILL.md:29-52]() |
| **Comparison** | LambdaTest engine compares new screenshots against baseline. | SmartUI Dashboard [smartui-skill/SKILL.md:92-93]() |
| **Approval** | User reviews diffs and approves/rejects to update baselines. | Approval Workflow [smartui-skill/SKILL.md:88-95]() |

### Code-to-Cloud Interaction Diagram
This diagram illustrates how local code entities interact with the LambdaTest SmartUI cloud infrastructure.

Title: SmartUI Execution and Upload Flow
```mermaid
graph TD
    subgraph "Local Environment"
        A["CLI: npx smartui exec"] --> B["Test Runner (Playwright/Selenium)"]
        B --> C["SDK: smartuiSnapshot()"]
        B --> D["JS: smartui.takeScreenshot"]
        E[".smartui.json / smartui.config.json"] -.-> A
    end

    subgraph "LambdaTest Cloud"
        F["SmartUI Rendering Engine"]
        G["Baseline Storage"]
        H["Pixel Diff Engine"]
        I["Dashboard Reporting"]
    end

    C --> F
    D --> F
    F --> H
    G --> H
    H --> I
```
Sources: [smartui-skill/SKILL.md:27-67](), [smartui-skill/reference/playbook.md:102-111]()

## Configuration and Setup

### Project Configuration
The `smartui.config.json` (or `.smartui.json`) file defines the matrix of environments where screenshots will be rendered.

```json
{
  "web": {
    "browsers": ["chrome", "firefox", "safari", "edge"],
    "viewports": [
      [1920, 1080],
      [375, 812]
    ]
  },
  "waitForPageRender": 5000,
  "waitForTimeout": 1000,
  "enableJavaScript": true
}
```
Sources: [smartui-skill/SKILL.md:71-80](), [smartui-skill/reference/playbook.md:34-56]()

### Environment Variables
Authentication requires three primary keys set in the environment:
* `PROJECT_TOKEN`: Unique identifier for the SmartUI project [smartui-skill/SKILL.md:110-110]().
* `LT_USERNAME`: LambdaTest account username [smartui-skill/SKILL.md:111-111]().
* `LT_ACCESS_KEY`: LambdaTest account access key [smartui-skill/SKILL.md:112-112]().

## Integration Patterns

### Playwright Integration
Playwright users can utilize the `smartuiSnapshot` function from `@lambdatest/smartui-cli` for high-level capture or use `page.evaluate` to send custom `lambdatest_action` commands.

Title: Playwright SmartUI Integration Mapping
```mermaid
graph LR
    subgraph "Code Entities"
        P1["smartuiSnapshot(page, 'name')"]
        P2["lambdatest_action: smartui.takeScreenshot"]
    end

    subgraph "Configuration Parameters"
        C1["fullPage: true"]
        C2["element: '.selector'"]
        C3["ignoreDOM: { id, class }"]
    end

    P1 -->|Uses| C1
    P2 -->|Supports| C2
    P2 -->|Supports| C3
```
Sources: [smartui-skill/SKILL.md:27-43](), [smartui-skill/reference/playbook.md:162-214]()

### Selenium Integration
Selenium integration typically involves executing JavaScript directly on the driver instance. For cloud-native execution, SmartUI options are passed via `LT:Options` [smartui-skill/SKILL.md:121-132]().

**JavaScript Injection:**
```java
((JavascriptExecutor) driver).executeScript("smartui.takeScreenshot=Login Page");
```
Sources: [smartui-skill/SKILL.md:45-52]()

## Specialized Testing Modes

### Static URL Crawl Mode
For applications without a complex test suite, SmartUI can crawl a list of URLs defined in a JSON file.
* **Command**: `npx smartui capture urls.json` [smartui-skill/reference/playbook.md:104-104]().
* **Structure**: `urls.json` contains objects with `name`, `url`, and optional `waitForTimeout` [smartui-skill/reference/playbook.md:71-99]().

### Storybook Integration
SmartUI can automatically capture all stories from a running Storybook instance.
* **Command**: `npx smartui storybook <url> --config smartui.config.json` [smartui-skill/SKILL.md:85-85]().

## Advanced Capture Controls

SmartUI allows for fine-grained control over the screenshot process to reduce noise and handle dynamic content:

| Feature | Implementation | Purpose |
| :--- | :--- | :--- |
| **Full Page** | `fullPage: true` | Captures the entire scrollable height [smartui-skill/reference/playbook.md:167-167](). |
| **Element Capture** | `element: '.hero-section'` | Focuses only on a specific DOM element [smartui-skill/reference/playbook.md:184-184](). |
| **DOM Masking** | `ignoreDOM: { id: [...], class: [...] }` | Masks dynamic elements (ads, timestamps) to prevent false positives [smartui-skill/reference/playbook.md:207-212](). |
| **Wait Strategies** | `waitForPageRender` / `waitForTimeout` | Ensures assets/animations are loaded before capture [smartui-skill/SKILL.md:77-78](). |

## Approval Workflow and Dashboard

The visual regression process follows a strict approval loop:
1.  **Baseline Generation**: The first execution on a branch creates the "Gold Standard" screenshots [smartui-skill/SKILL.md:90-90]().
2.  **Comparison**: Subsequent runs generate "Diffs" highlighted in the dashboard [smartui-skill/SKILL.md:91-92]().
3.  **Review**: Users visit `https://smartui.lambdatest.com` to inspect changes [smartui-skill/SKILL.md:142-142]().
4.  **Action**: 
    *   **Approve**: The new screenshot becomes the new baseline [smartui-skill/SKILL.md:94-94]().
    *   **Reject**: The build is marked as failed, indicating a visual regression [smartui-skill/SKILL.md:93-93]().

Sources: [smartui-skill/SKILL.md:88-95](), [smartui-skill/SKILL.md:134-142]()

---

# Page: CI/CD Pipeline and DevOps Skill

# 7. CI/CD Pipeline and DevOps Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [behave-skill/reference/playbook.md](behave-skill/reference/playbook.md)
- [capybara-skill/SKILL.md](capybara-skill/SKILL.md)
- [capybara-skill/reference/advanced-patterns.md](capybara-skill/reference/advanced-patterns.md)
- [capybara-skill/reference/cloud-integration.md](capybara-skill/reference/cloud-integration.md)
- [capybara-skill/reference/playbook.md](capybara-skill/reference/playbook.md)
- [cicd-pipeline-skill/SKILL.md](cicd-pipeline-skill/SKILL.md)
- [cicd-pipeline-skill/reference/playbook.md](cicd-pipeline-skill/reference/playbook.md)
- [gauge-skill/reference/playbook.md](gauge-skill/reference/playbook.md)
- [jest-skill/reference/advanced-patterns.md](jest-skill/reference/advanced-patterns.md)
- [jest-skill/reference/playbook.md](jest-skill/reference/playbook.md)
- [junit-5-skill/reference/advanced-patterns.md](junit-5-skill/reference/advanced-patterns.md)
- [junit-5-skill/reference/playbook.md](junit-5-skill/reference/playbook.md)
- [protractor-skill/reference/cloud-integration.md](protractor-skill/reference/cloud-integration.md)
- [rspec-skill/reference/playbook.md](rspec-skill/reference/playbook.md)
- [selenium-skill/reference/playbook.md](selenium-skill/reference/playbook.md)

</details>



The **CI/CD Pipeline and DevOps Skill** provides a standardized approach for integrating automated testing into modern software delivery lifecycles. It focuses on creating robust, "fail-fast" pipelines that balance execution speed with comprehensive quality gates. This skill encompasses configuration patterns for major CI providers, efficient resource management through sharding, and the enforcement of quality standards via coverage aggregation.

### System Architecture Overview

The following diagram illustrates the relationship between CI/CD configuration entities and the execution environment.

**CI/CD Entity Mapping**
```mermaid
graph TD
  subgraph "Natural Language Space"
    A["Pipeline Definition"]
    B["Quality Gate"]
    C["Infrastructure"]
  end

  subgraph "Code Entity Space"
    A --> D["workflow.yaml"]
    A --> E["gitlab-ci.yml"]
    A --> F["Jenkinsfile"]
    
    B --> G["coverageThreshold"]
    B --> H["junit_report"]
    
    C --> I["services: postgres"]
    C --> J["strategy: matrix"]
  end

  D -- "defines" --> J
  G -- "enforced in" --> D [cicd-pipeline-skill/reference/playbook.md:15-101]()
  I -- "spins up" --> K["Service Containers"] [cicd-pipeline-skill/reference/playbook.md:60-68]()
```
**Sources:** [cicd-pipeline-skill/reference/playbook.md:6-144](), [cicd-pipeline-skill/reference/playbook.md:197-271]()

---

### Core Components

#### 1. Multi-Stage Pipeline Design
The skill advocates for a tiered execution strategy to optimize developer feedback loops:
*   **Linting/Type-Checking:** Initial fast-fail stage to catch syntax and style issues [cicd-pipeline-skill/reference/playbook.md:24-32]().
*   **Unit Testing:** Parallelized execution of isolated tests with coverage collection [cicd-pipeline-skill/reference/playbook.md:34-52]().
*   **E2E Testing:** Integration tests requiring service containers (PostgreSQL, Redis) and browser binaries [cicd-pipeline-skill/reference/playbook.md:54-86]().
*   **Quality Gates:** Aggregation of results and enforcement of coverage thresholds [cicd-pipeline-skill/reference/playbook.md:87-99]().

#### 2. Test Sharding and Parallelization
To reduce total execution time, the skill implements matrix strategies and sharding:
*   **GitHub Actions Matrix:** Running tests across multiple Node.js versions and browser engines simultaneously [cicd-pipeline-skill/reference/playbook.md:37-40]().
*   **Manual Sharding:** Splitting test suites into chunks (e.g., `--shard=1/3`) to distribute load across multiple runners [cicd-pipeline-skill/reference/playbook.md:48]().
*   **GitLab Parallelism:** Using the `parallel` keyword to instantiate multiple job instances [cicd-pipeline-skill/reference/playbook.md:224]().

#### 3. Service Containers and Environment Management
Complex E2E tests often require sidecar services. The skill provides patterns for:
*   **Ephemeral Databases:** Defining PostgreSQL or Redis services with health checks within the CI runner [cicd-pipeline-skill/reference/playbook.md:60-68]().
*   **OIDC and Secrets:** Securely injecting credentials like `LT_USERNAME` and `LT_ACCESS_KEY` for cloud execution [capybara-skill/reference/playbook.md:54](), [cicd-pipeline-skill/reference/playbook.md:96]().

**CI Execution Flow**
```mermaid
sequenceDiagram
    participant Dev as "Developer (Git Push)"
    participant CI as "CI Runner (GHA/GitLab)"
    participant Svc as "Service Containers (DB/Redis)"
    participant Cloud as "LambdaTest/TestMu AI"

    Dev->>CI: Trigger Pipeline
    CI->>CI: npm ci (Restore Cache)
    CI->>Svc: Initialize (Health Check)
    CI->>CI: Run Sharded Tests
    CI->>Cloud: Remote Execution (RemoteWebDriver)
    CI->>CI: Aggregate Artifacts (JUnit/Coverage)
    CI->>Dev: Feedback (Quality Gate Status)
```
**Sources:** [cicd-pipeline-skill/reference/playbook.md:6-86](), [selenium-skill/reference/playbook.md:35-47]()

---

### Child Pages

#### [GitHub Actions Integration Patterns](#7.1)
Detailed implementation guide for GitHub Actions. Covers advanced `concurrency` control to `cancel-in-progress` workflows [cicd-pipeline-skill/reference/playbook.md:14-16](), dependency caching for various languages (npm, pip, bundler, nuget) [cicd-pipeline-skill/reference/playbook.md:150-173](), and Playwright-specific browser caching [cicd-pipeline-skill/reference/playbook.md:175-183]().

#### [Coverage Enforcement and Quality Gates](#7.2)
Focuses on the "Quality Gate" stage of the pipeline. Explains how to collect coverage from sharded runs [cicd-pipeline-skill/reference/playbook.md:49-52](), merge them using tools like Codecov [cicd-pipeline-skill/reference/playbook.md:94-98](), and enforce minimum thresholds (e.g., 80% branches/lines) in `jest.config.js` or `spec_helper.rb` [jest-skill/reference/playbook.md:15](), [rspec-skill/reference/playbook.md:38]().

---

### Best Practices Summary

| Category | Recommendation | Code Pointer |
| :--- | :--- | :--- |
| **Optimization** | Use `actions/cache` for dependencies and browser binaries | [cicd-pipeline-skill/reference/playbook.md:150-183]() |
| **Stability** | Implement `cancel-in-progress` to prevent redundant builds | [cicd-pipeline-skill/reference/playbook.md:14-16]() |
| **Isolation** | Use `services` for databases instead of manual installation | [cicd-pipeline-skill/reference/playbook.md:60-68]() |
| **Observability** | Always upload test artifacts (reports/screenshots) on failure | [cicd-pipeline-skill/reference/playbook.md:81-85]() |
| **Security** | Use OIDC/Workload Identity over long-lived secrets where possible | [cicd-pipeline-skill/reference/playbook.md:103-112]() |

**Sources:** [cicd-pipeline-skill/reference/playbook.md:6-191](), [jest-skill/reference/playbook.md:15](), [rspec-skill/reference/playbook.md:32-39]()

---

# Page: GitHub Actions Integration Patterns

# GitHub Actions Integration Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [behat-skill/reference/advanced-patterns.md](behat-skill/reference/advanced-patterns.md)
- [behat-skill/reference/playbook.md](behat-skill/reference/playbook.md)
- [behave-skill/SKILL.md](behave-skill/SKILL.md)
- [capybara-skill/SKILL.md](capybara-skill/SKILL.md)
- [capybara-skill/reference/advanced-patterns.md](capybara-skill/reference/advanced-patterns.md)
- [capybara-skill/reference/cloud-integration.md](capybara-skill/reference/cloud-integration.md)
- [capybara-skill/reference/playbook.md](capybara-skill/reference/playbook.md)
- [cicd-pipeline-skill/SKILL.md](cicd-pipeline-skill/SKILL.md)
- [cicd-pipeline-skill/reference/playbook.md](cicd-pipeline-skill/reference/playbook.md)
- [gauge-skill/SKILL.md](gauge-skill/SKILL.md)
- [jest-skill/reference/advanced-patterns.md](jest-skill/reference/advanced-patterns.md)
- [jest-skill/reference/playbook.md](jest-skill/reference/playbook.md)
- [junit-5-skill/reference/advanced-patterns.md](junit-5-skill/reference/advanced-patterns.md)
- [junit-5-skill/reference/playbook.md](junit-5-skill/reference/playbook.md)
- [protractor-skill/reference/cloud-integration.md](protractor-skill/reference/cloud-integration.md)
- [rspec-skill/reference/playbook.md](rspec-skill/reference/playbook.md)

</details>



This page documents the standardized integration patterns for GitHub Actions within the `agent-skills` repository. It covers the end-to-end lifecycle of a CI/CD pipeline, from workflow triggers and concurrency management to advanced testing strategies like sharding, service containers, and automated reporting.

## Workflow Orchestration and Triggers

Production-grade workflows in this ecosystem utilize a multi-stage approach to ensure code quality before deployment. This includes linting, type-checking, unit testing, and finally E2E browser testing.

### Concurrency and Fail-Fast
To optimize runner usage, workflows implement concurrency control to cancel outdated runs on the same branch when new commits are pushed [cicd-pipeline-skill/reference/playbook.md:14-16]().

### Trigger Strategy
Workflows are typically triggered on `push` to primary branches (`main`, `develop`) and on any `pull_request` targeting those branches [cicd-pipeline-skill/reference/playbook.md:7-12]().

**Workflow Execution Flow**

```mermaid
graph TD
    subgraph "Trigger Space"
        A["push to main/develop"] --> C["GitHub Actions Workflow"]
        B["pull_request"] --> C
    end

    subgraph "Code Entity Space: workflow.yml"
        C --> D["Job: lint"]
        D --> E["Job: unit (matrix)"]
        E --> F["Job: e2e (matrix)"]
        F --> G["Job: build/deploy"]
    end

    subgraph "Execution Logic"
        D -- "npm run lint" --> D1["ESLint/TypeCheck"]
        E -- "npm test -- --shard" --> E1["Sharded Runners"]
        F -- "npx playwright test" --> F1["Browser Testing"]
    end
```
Sources: [cicd-pipeline-skill/reference/playbook.md:7-35]()

---

## Service Containers and Environment Injection

For integration and E2E testing, GitHub Actions provides "Services" to host ephemeral databases and caches.

### Database and Cache Setup
Common service patterns include:
*   **PostgreSQL**: Configured with health checks to ensure the database is ready before the test steps begin [cicd-pipeline-skill/reference/playbook.md:61-65]().
*   **Redis**: Used for session or caching layer testing [cicd-pipeline-skill/reference/playbook.md:66-68]().

### Environment Variable Injection
Sensitive credentials and service URLs are injected via the `env` block, often referencing secrets or service aliases (e.g., `localhost` for services mapped to host ports) [cicd-pipeline-skill/reference/playbook.md:78-80]().

| Service | Image | Default Port | Usage |
| :--- | :--- | :--- | :--- |
| PostgreSQL | `postgres:16` | 5432 | Relational data storage for E2E/Unit tests |
| Redis | `redis:7` | 6379 | Distributed caching and pub/sub testing |
| Selenium | `selenium/standalone-chrome` | 4444 | Local browser grid for Selenium/Capybara |

Sources: [cicd-pipeline-skill/reference/playbook.md:60-80](), [behat-skill/reference/playbook.md:41-57]()

---

## Test Sharding and Matrix Strategies

To reduce execution time, tests are distributed across multiple parallel runners using the GitHub Actions `strategy.matrix`.

### Sharding Pattern
Tests are split using framework-specific sharding flags (e.g., `jest --shard=1/3` or `playwright test --shard=1/3`) [cicd-pipeline-skill/reference/playbook.md:37-48]().

### Data Flow for Sharded Execution

```mermaid
sequenceDiagram
    participant G as GitHub Runner (Controller)
    participant M1 as Matrix Runner 1
    participant M2 as Matrix Runner 2
    participant A as Artifact Storage

    G->>M1: Start Shard 1/2
    G->>M2: Start Shard 2/2
    M1->>M1: Run npm test --shard=1/2
    M2->>M2: Run npm test --shard=2/2
    M1->>A: Upload coverage-1.json
    M2->>A: Upload coverage-2.json
    G->>G: Download All Artifacts
    G->>G: Merge Coverage Reports
```
Sources: [cicd-pipeline-skill/reference/playbook.md:37-53](), [cicd-pipeline-skill/reference/playbook.md:87-98]()

---

## Artifact Management and Reporting

Post-execution steps focus on preserving test results, screenshots, and coverage data.

### Artifact Uploads
*   **Screenshots/Videos**: Captured on failure in frameworks like Capybara [capybara-skill/reference/playbook.md:30]() or Behave [behave-skill/SKILL.md:113-114]().
*   **Test Reports**: HTML or JUnit XML reports are uploaded as artifacts for debugging [cicd-pipeline-skill/reference/playbook.md:81-86]().

### Coverage Enforcement
Coverage artifacts from sharded runs are merged in a final `coverage` job. Tools like `Codecov` are used to provide PR comments and enforce quality gates [cicd-pipeline-skill/reference/playbook.md:94-98](). Frameworks like Jest [jest-skill/reference/playbook.md:12-15]() and RSpec [rspec-skill/reference/playbook.md:32-39]() are configured to generate `json-summary` or `lcov` formats compatible with these actions.

| Artifact Type | Source Path | Action | Retention |
| :--- | :--- | :--- | :--- |
| Coverage | `coverage/` | `actions/upload-artifact` | Defined in workflow |
| E2E Reports | `playwright-report/` | `actions/upload-artifact` | if: always() |
| Screenshots | `tmp/screenshots/` | `actions/upload-artifact` | if: failure() |

Sources: [cicd-pipeline-skill/reference/playbook.md:49-53](), [cicd-pipeline-skill/reference/playbook.md:81-86](), [capybara-skill/reference/playbook.md:30]()

---

## Caching and Optimization

To minimize "cold start" times, workflows utilize aggressive caching for dependencies and browser binaries.

*   **Package Managers**: `actions/setup-node`, `actions/setup-python`, and `ruby/setup-ruby` include built-in caching for `npm`, `pip`, and `bundle` respectively [cicd-pipeline-skill/reference/playbook.md:150-163]().
*   **Playwright Browsers**: Browser binaries are cached separately to avoid multi-gigabyte downloads on every run [cicd-pipeline-skill/reference/playbook.md:175-183]().
*   **Docker Layers**: Uses `type=gha` cache backend for faster container builds [cicd-pipeline-skill/reference/playbook.md:185-191]().

Sources: [cicd-pipeline-skill/reference/playbook.md:148-191]()

---

# Page: Coverage Enforcement and Quality Gates

# Coverage Enforcement and Quality Gates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cicd-pipeline-skill/SKILL.md](cicd-pipeline-skill/SKILL.md)
- [cicd-pipeline-skill/reference/playbook.md](cicd-pipeline-skill/reference/playbook.md)
- [jest-skill/reference/advanced-patterns.md](jest-skill/reference/advanced-patterns.md)
- [jest-skill/reference/playbook.md](jest-skill/reference/playbook.md)
- [junit-5-skill/reference/advanced-patterns.md](junit-5-skill/reference/advanced-patterns.md)
- [junit-5-skill/reference/playbook.md](junit-5-skill/reference/playbook.md)
- [phpunit-skill/reference/playbook.md](phpunit-skill/reference/playbook.md)
- [pytest-skill/SKILL.md](pytest-skill/SKILL.md)
- [pytest-skill/reference/advanced-patterns.md](pytest-skill/reference/advanced-patterns.md)
- [pytest-skill/reference/playbook.md](pytest-skill/reference/playbook.md)
- [testunit-skill/reference/playbook.md](testunit-skill/reference/playbook.md)
- [unittest-skill/reference/playbook.md](unittest-skill/reference/playbook.md)

</details>



This page details the implementation of code coverage tracking and enforcement across multiple language ecosystems within the `agent-skills` framework. It covers the configuration of language-specific tooling, the logic for threshold enforcement, and the integration of these checks into CI/CD pipelines to ensure code quality standards are met before deployment.

## Language-Specific Coverage Tooling

The repository leverages standard industry tools for each supported language to generate coverage artifacts (e.g., LCOV, Clover XML, JSON).

### Tooling Matrix

| Language | Tool | Configuration File | Key Artifacts |
| :--- | :--- | :--- | :--- |
| **Python** | `coverage.py` | `.coveragerc` / `pyproject.toml` | `coverage.xml`, `.coverage` |
| **JavaScript** | `Istanbul` (via Jest) | `jest.config.js` | `lcov.info`, `clover.xml` |
| **PHP** | `Xdebug` / `php-code-coverage` | `phpunit.xml` | `clover.xml`, `coverage-html/` |
| **Ruby** | `SimpleCov` | `.simplecov` | `coverage/.resultset.json` |
| **Java** | `JaCoCo` | `pom.xml` | `target/site/jacoco/` |

### Python (coverage.py)
Python skills utilize `coverage.py` configured via `pyproject.toml` [unittest-skill/reference/playbook.md:40-68](). It tracks branch coverage and excludes boilerplate such as `pragma: no cover` or `NotImplementedError` [unittest-skill/reference/playbook.md:58-67]().

### JavaScript (Jest/Istanbul)
Jest projects define coverage thresholds directly in `jest.config.js` [jest-skill/reference/playbook.md:12-16](). This includes global thresholds for branches, functions, lines, and statements, typically set at a minimum of 80% [jest-skill/reference/playbook.md:15-15]().

### PHP (Xdebug/PHPUnit)
PHP coverage requires the `Xdebug` extension set to `XDEBUG_MODE=coverage` [phpunit-skill/reference/playbook.md:25-25](). The `phpunit.xml` file defines the source directories to include (e.g., `src/`) and excludes migrations or external dependencies [phpunit-skill/reference/playbook.md:65-72]().

### Ruby (SimpleCov)
Ruby skills use `SimpleCov`, initialized in a `test_helper.rb` [testunit-skill/reference/playbook.md:47-54](). It groups coverage by application layer (Models, Services) and enforces a `minimum_coverage` threshold [testunit-skill/reference/playbook.md:51-53]().

**Sources:**
- [unittest-skill/reference/playbook.md:40-80]()
- [jest-skill/reference/playbook.md:5-26]()
- [phpunit-skill/reference/playbook.md:31-80]()
- [testunit-skill/reference/playbook.md:46-54]()

---

## Threshold Enforcement and Quality Gates

Quality gates are enforced at two levels: local execution via CLI flags and CI/CD pipeline blocking.

### Threshold Configuration
Thresholds are defined in project metadata files to ensure consistency across developer environments and build servers.

| Entity | Implementation | File Reference |
| :--- | :--- | :--- |
| **Python Fail Under** | `fail_under = 80` | [pytest-skill/reference/playbook.md:39-41]() |
| **Jest Global Threshold** | `coverageThreshold: { global: { lines: 80 } }` | [jest-skill/reference/playbook.md:15-15]() |
| **Ruby Minimum** | `minimum_coverage 80` | [testunit-skill/reference/playbook.md:53-53]() |

### Data Flow: From Execution to Enforcement

The following diagram illustrates how coverage data flows from test execution through the quality gate check.

**Coverage Enforcement Flow**
```mermaid
graph TD
    subgraph "Test Execution Space"
        A["Test Runner (pytest/jest/phpunit)"] --> B["Coverage Collector"]
        B --> C["Raw Coverage Data (.coverage/json)"]
    end

    subgraph "Processing Space"
        C --> D["Report Generator"]
        D --> E["Clover/LCOV Artifacts"]
    end

    subgraph "Quality Gate Space"
        E --> F{"Threshold Check"}
        F -- "Below %" --> G["Exit Code 1 (Fail Build)"]
        F -- "Above %" --> H["Exit Code 0 (Pass Build)"]
    end

    subgraph "CI Integration"
        G --> I["GitHub Actions/GitLab Status Fail"]
        H --> J["Upload to Codecov/Artifacts"]
    end
```

**Sources:**
- [cicd-pipeline-skill/reference/playbook.md:87-99]()
- [pytest-skill/reference/playbook.md:162-166]()
- [jest-skill/reference/playbook.md:12-16]()

---

## Sharded Coverage Merging

In high-scale CI pipelines, tests are often sharded across multiple runners to reduce execution time. This requires a "merge" step to aggregate coverage from all shards before evaluating the quality gate.

### Sharding Strategy
Pipelines use a matrix strategy to split tests. For example, a Node.js project might use `npm test -- --coverage --shard=${{ matrix.shard }}/3` [cicd-pipeline-skill/reference/playbook.md:48-48]().

### Merging Logic
1.  **Upload:** Each shard uploads its partial coverage directory as a named artifact (e.g., `coverage-1`, `coverage-2`) [cicd-pipeline-skill/reference/playbook.md:49-52]().
2.  **Download:** A downstream `coverage` job downloads all artifacts using a pattern match [cicd-pipeline-skill/reference/playbook.md:92-93]().
3.  **Aggregate:** Tools like `codecov-action` or language-specific merge commands (e.g., `coverage combine` for Python) unify the data [cicd-pipeline-skill/reference/playbook.md:94-98]().

**Natural Language to Code Entity Mapping: Sharding**
```mermaid
graph LR
    subgraph "Natural Language Concepts"
        NL1["Parallel Execution"]
        NL2["Partial Coverage"]
        NL3["Consolidated Report"]
    end

    subgraph "Code Entities (cicd-pipeline-skill)"
        CE1["matrix: shard [1, 2, 3]"]
        CE2["upload-artifact (name: coverage-shard)"]
        CE3["download-artifact (merge-multiple: true)"]
        CE4["codecov-action"]
    end

    NL1 --- CE1
    NL2 --- CE2
    NL3 --- CE3
    CE3 --- CE4
```

**Sources:**
- [cicd-pipeline-skill/reference/playbook.md:37-52]()
- [cicd-pipeline-skill/reference/playbook.md:87-99]()
- [cicd-pipeline-skill/reference/playbook.md:224-234]()

---

## CI Pipeline Integration

Coverage checks are integrated into GitHub Actions and GitLab CI to act as blocking quality gates.

### GitHub Actions Workflow
The pipeline is designed with a `needs` dependency where the `coverage` job depends on the completion of `unit` test shards [cicd-pipeline-skill/reference/playbook.md:87-88](). The `fail_ci_if_error: true` flag ensures that a failure to upload or process coverage results in a failed build [cicd-pipeline-skill/reference/playbook.md:97-97]().

### GitLab CI Configuration
GitLab uses regex-based coverage parsing and Cobertura report artifacts [cicd-pipeline-skill/reference/playbook.md:228-234]().
*   **Regex Extraction:** `coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'` [cicd-pipeline-skill/reference/playbook.md:228-228]().
*   **Artifact Path:** `coverage/cobertura-coverage.xml` [cicd-pipeline-skill/reference/playbook.md:234-234]().

### Quality Gate Summary Table

| CI Platform | Gate Mechanism | Configuration Key |
| :--- | :--- | :--- |
| **GitHub Actions** | Action Failure | `fail_ci_if_error: true` |
| **GitLab CI** | Artifact Reporting | `artifacts: reports: coverage_report` |
| **Local CLI** | Process Exit Code | `fail_under` (Python) / `coverageThreshold` (JS) |

**Sources:**
- [cicd-pipeline-skill/reference/playbook.md:87-99]()
- [cicd-pipeline-skill/reference/playbook.md:220-235]()
- [cicd-pipeline-skill/SKILL.md:51-56]()

---

# Page: Test Framework Migration Skill

# Test Framework Migration Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [test-framework-migration-skill/SKILL.md](test-framework-migration-skill/SKILL.md)
- [test-framework-migration-skill/reference/overview.md](test-framework-migration-skill/reference/overview.md)
- [test-framework-migration-skill/reference/playwright-to-puppeteer.md](test-framework-migration-skill/reference/playwright-to-puppeteer.md)
- [test-framework-migration-skill/reference/playwright-to-selenium.md](test-framework-migration-skill/reference/playwright-to-selenium.md)
- [test-framework-migration-skill/reference/puppeteer-to-playwright.md](test-framework-migration-skill/reference/puppeteer-to-playwright.md)
- [test-framework-migration-skill/reference/puppeteer-to-selenium.md](test-framework-migration-skill/reference/puppeteer-to-selenium.md)
- [test-framework-migration-skill/reference/selenium-to-playwright.md](test-framework-migration-skill/reference/selenium-to-playwright.md)
- [test-framework-migration-skill/reference/selenium-to-puppeteer.md](test-framework-migration-skill/reference/selenium-to-puppeteer.md)

</details>



The **Test Framework Migration Skill** provides a structured methodology for converting test automation suites between major E2E testing frameworks: **Selenium**, **Playwright**, **Puppeteer**, and **Cypress**. It focuses on mapping API commands, adjusting synchronization strategies (e.g., explicit waits vs. auto-waiting), and adapting test lifecycle patterns to the target framework's architecture [test-framework-migration-skill/SKILL.md:4-11]().

## Migration Overview

Migrating between frameworks often involves shifting not just syntax, but the underlying execution model and language ecosystem.

### Framework Comparison Matrix
The following matrix compares the core architectural differences between the supported frameworks:

| Aspect | Selenium | Playwright | Puppeteer | Cypress |
|--------|----------|------------|-----------|---------|
| **Protocol** | WebDriver (W3C) | CDP / WebDriver BiDi | CDP | Proprietary |
| **Waits** | Explicit (Required) | Auto-wait | Manual | Built-in Retry |
| **Multi-tab** | Yes | Yes | Yes | No (True) |
| **Cross-browser**| All (via Drivers) | Chromium, FF, WebKit | Chrome/Chromium | Most (Limited) |

Sources: [test-framework-migration-skill/reference/overview.md:5-12]()

### Language Support Matrix
When migrating, the target language is often dictated by the framework's primary ecosystem. For example, migrating from Selenium (Java) to Playwright frequently implies a rewrite into TypeScript [test-framework-migration-skill/reference/overview.md:36-38]().

| Framework | Java | Python | JS/TS | C# | Ruby/PHP |
|-----------|------|--------|-------|----|----------|
| **Selenium** | Yes | Yes | Yes | Yes | Yes |
| **Playwright** | Yes | Yes | Yes | Yes | No |
| **Puppeteer** | No | No | Yes | No | No |
| **Cypress** | No | No | Yes | No | No |

Sources: [test-framework-migration-skill/reference/overview.md:29-34]()

## Migration Workflow

The migration process follows a 5-step workflow to ensure architectural consistency:

### System Interaction Diagram: Migration Logic
This diagram illustrates how the `test-framework-migration-skill` processes a migration request by routing through specific reference entities.

```mermaid
graph TD
    User["User Request ('migrate selenium to playwright')"] --> Detect["Step 1 & 2: Detect Source/Target Frameworks"]
    Detect --> Lang["Step 3: Detect Language Matrix"]
    Lang --> Router["Step 4: Route to Reference File"]
    
    subgraph "Reference Entity Space"
        Router --> S2PL["selenium-to-playwright.md"]
        Router --> PL2S["playwright-to-selenium.md"]
        Router --> PUP2PL["puppeteer-to-playwright.md"]
        Router --> Other["Other Directional Refs..."]
    end
    
    S2PL --> Apply["Step 5: Apply Mappings"]
    PL2S --> Apply
    PUP2PL --> Apply
    
    Apply --> Output["Generated Migrated Code"]
```
Sources: [test-framework-migration-skill/SKILL.md:29-85]()

### Mapping Code Entities
Migration involves mapping specific code symbols from the source framework to the equivalent entity in the target framework.

```mermaid
graph LR
    subgraph "Selenium Code Entities"
        S_By["By.id() / By.cssSelector()"]
        S_Wait["WebDriverWait / ExpectedConditions"]
        S_Action["element.sendKeys() / element.click()"]
        S_Assert["Assertions.assertTrue()"]
    end

    subgraph "Playwright Code Entities"
        P_Loc["page.locator() / page.getByRole()"]
        P_Wait["Auto-wait / expect().toBeVisible()"]
        P_Action["locator.fill() / locator.click()"]
        P_Assert["expect(page).toHaveTitle()"]
    end

    S_By -- "Map to" --> P_Loc
    S_Wait -- "Convert to" --> P_Wait
    S_Action -- "Map to" --> P_Action
    S_Assert -- "Map to" --> P_Assert
```
Sources: [test-framework-migration-skill/reference/selenium-to-playwright.md:5-46](), [test-framework-migration-skill/reference/playwright-to-selenium.md:5-47]()

## Supported Migration Paths

There are 10 bidirectional migration paths supported by this skill. These are grouped into two detailed child pages based on the involvement of the Playwright framework.

### Playwright Migration Paths
This category covers migrations where Playwright is either the source or the target. These paths often focus on moving from manual/explicit waiting to Playwright's auto-wait model and utilizing `Locators` instead of `ElementHandles` [test-framework-migration-skill/reference/puppeteer-to-playwright.md:85-89]().

*   **Selenium ↔ Playwright**: Mapping `WebDriver` lifecycle to Playwright `fixtures`.
*   **Puppeteer ↔ Playwright**: Transitioning from CDP-based manual waits to high-level Playwright APIs.
*   **Cypress ↔ Playwright**: Converting Cypress command chains to async/await Playwright locators.

For detailed API mapping tables and code snippets, see **[Playwright Migration Paths — To and From Playwright (#8.1)]**.

### Selenium and Puppeteer Migration Paths
This category covers migrations between Selenium, Puppeteer, and Cypress that do not involve Playwright. These paths often require maintaining explicit synchronization logic (like `WebDriverWait`) or specific browser-driven protocols [test-framework-migration-skill/reference/puppeteer-to-selenium.md:88-92]().

*   **Puppeteer ↔ Selenium**: Moving from Chrome-only CDP to multi-browser W3C WebDriver.
*   **Cypress ↔ Selenium**: Converting proprietary Cypress runner patterns to standard WebDriver scripts.
*   **Selenium ↔ Puppeteer**: Transitioning from enterprise multi-language drivers to JS-native Chrome automation.

For detailed conversion guides and "Gotchas," see **[Selenium and Puppeteer Migration Paths (#8.2)]**.

## Cloud Integration (TestMu)
Regardless of the framework, all migrated tests can be routed to the LambdaTest/TestMu AI cloud. Migration requires updating the connection logic:
*   **Selenium**: Uses `RemoteWebDriver` with `LT:Options` [test-framework-migration-skill/reference/selenium-to-playwright.md:86-88]().
*   **Playwright**: Uses CDP connection via `wss://cdp.lambdatest.com/playwright` [test-framework-migration-skill/reference/playwright-to-selenium.md:84-87]().
*   **Puppeteer**: Connects via a specific LambdaTest WebSocket endpoint [test-framework-migration-skill/reference/puppeteer-to-selenium.md:83-84]().

Sources: [test-framework-migration-skill/SKILL.md:98-106](), [shared/testmu-cloud-reference.md]()

---

# Page: Playwright Migration Paths — To and From Playwright

# Playwright Migration Paths — To and From Playwright

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [test-framework-migration-skill/SKILL.md](test-framework-migration-skill/SKILL.md)
- [test-framework-migration-skill/reference/cypress-to-playwright.md](test-framework-migration-skill/reference/cypress-to-playwright.md)
- [test-framework-migration-skill/reference/overview.md](test-framework-migration-skill/reference/overview.md)
- [test-framework-migration-skill/reference/playwright-to-cypress.md](test-framework-migration-skill/reference/playwright-to-cypress.md)
- [test-framework-migration-skill/reference/playwright-to-selenium.md](test-framework-migration-skill/reference/playwright-to-selenium.md)
- [test-framework-migration-skill/reference/puppeteer-to-playwright.md](test-framework-migration-skill/reference/puppeteer-to-playwright.md)
- [test-framework-migration-skill/reference/selenium-to-playwright.md](test-framework-migration-skill/reference/selenium-to-playwright.md)

</details>



This page provides technical guidance for migrating test automation suites between Playwright and other major frameworks (Selenium, Puppeteer, and Cypress). It covers API mapping, locator strategy conversion, wait mechanics, and lifecycle management.

## 1. Migration Strategy Overview

The `test-framework-migration-skill` facilitates bidirectional transitions by mapping source framework signals to target framework implementations [test-framework-migration-skill/SKILL.md:29-83]().

### Framework Capability Comparison
| Aspect | Selenium | Playwright | Puppeteer | Cypress |
|--------|----------|------------|-----------|---------|
| **Protocol** | WebDriver (W3C) | CDP / BiDi | CDP | Proprietary |
| **Wait Strategy** | Explicit (`WebDriverWait`) | Auto-wait | Manual (`waitForSelector`) | Retry-ability |
| **Multi-Tab** | Yes | Yes | Yes | No |
| **Languages** | Java, PY, JS, C#, RB, PHP | JS, TS, PY, Java, C# | JS, TS | JS, TS |

**Sources:** [test-framework-migration-skill/reference/overview.md:5-12](), [test-framework-migration-skill/reference/overview.md:29-34]()

---

## 2. Selenium ↔ Playwright Migration

### 2.1 Selenium to Playwright (The Modernization Path)
Migration from Selenium often targets a reduction in flakiness via Playwright's auto-wait mechanism [test-framework-migration-skill/reference/overview.md:18-18]().

#### API Mapping Table
| Feature | Selenium (Java/JS) | Playwright (TS/JS) |
|---------|--------------------|--------------------|
| **Locator** | `By.id("x")` | `page.locator('#x')` |
| **Semantic** | N/A | `page.getByRole('button', { name: 'Submit' })` |
| **Wait** | `wait.until(EC.visibilityOf(...))` | `await expect(locator).toBeVisible()` |
| **Input** | `element.sendKeys("text")` | `await locator.fill('text')` |
| **Frame** | `driver.switchTo().frame("n")` | `page.frameLocator('iframe[name="n"]')` |
| **Alert** | `driver.switchTo().alert()` | `page.on('dialog', d => d.accept())` |

**Sources:** [test-framework-migration-skill/reference/selenium-to-playwright.md:7-37](), [test-framework-migration-skill/reference/selenium-to-playwright.md:95-95]()

#### Data Flow: Selenium to Playwright Logic
The following diagram illustrates how the `test-framework-migration-skill` transforms a Selenium command into a Playwright action.

**Title: Selenium to Playwright Command Transformation**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Migrate Selenium login test'"] --> B["Detect Source: Selenium"]
        B --> C["Detect Target: Playwright"]
    end

    subgraph "Code Entity Space"
        C --> D["Read selenium-to-playwright.md"]
        D --> E["Map By.id to page.locator"]
        D --> F["Map sendKeys to .fill()"]
        D --> G["Replace WebDriverWait with auto-wait"]
        E & F & G --> H["Generate playwright.config.ts"]
    end
```
**Sources:** [test-framework-migration-skill/SKILL.md:29-54](), [test-framework-migration-skill/reference/selenium-to-playwright.md:3-37]()

---

### 2.2 Playwright to Selenium (The Enterprise Path)
Used when a project requires integration with legacy Selenium Grid or specific language support (Ruby/PHP) not natively prioritized by Playwright [test-framework-migration-skill/reference/overview.md:20-20]().

**Key Requirement:** Playwright's implicit auto-waits must be replaced with explicit `WebDriverWait` and `ExpectedConditions` in Selenium [test-framework-migration-skill/reference/playwright-to-selenium.md:91-91]().

**Sources:** [test-framework-migration-skill/reference/playwright-to-selenium.md:19-27](), [test-framework-migration-skill/reference/playwright-to-selenium.md:91-95]()

---

## 3. Puppeteer ↔ Playwright Migration

### 3.1 Puppeteer to Playwright
Since both frameworks use CDP, the transition is structural. Playwright introduces `Locators` which are lazily evaluated, whereas Puppeteer uses `ElementHandles` which can become stale [test-framework-migration-skill/reference/puppeteer-to-playwright.md:87-87]().

| Puppeteer | Playwright | Note |
|-----------|------------|------|
| `page.$('#x')` | `page.locator('#x')` | Locator re-resolves on action |
| `page.waitForNavigation()` | N/A | Usually redundant in Playwright |
| `page.type()` | `locator.fill()` | `fill()` clears existing text |
| `page.setViewport()` | `context.setViewportSize()` | Set at context level |

**Sources:** [test-framework-migration-skill/reference/puppeteer-to-playwright.md:7-34](), [test-framework-migration-skill/reference/puppeteer-to-playwright.md:85-87]()

---

## 4. Cypress ↔ Playwright Migration

### 4.1 Cypress to Playwright
The primary shift is from Cypress's custom "command queue" (synchronous-looking) to standard JavaScript `async/await` [test-framework-migration-skill/reference/cypress-to-playwright.md:83-83]().

#### Technical Mapping
| Cypress Command | Playwright Equivalent |
|-----------------|-----------------------|
| `cy.get('[data-cy="x"]')` | `page.getByTestId('x')` |
| `cy.intercept('GET', '/api')` | `page.route('**/api', ...)` |
| `cy.visit('/path')` | `await page.goto('/path')` |
| `cy.url().should('include', 'd')` | `await expect(page).toHaveURL(/d/)` |

**Sources:** [test-framework-migration-skill/reference/cypress-to-playwright.md:7-38](), [test-framework-migration-skill/reference/cypress-to-playwright.md:86-86]()

#### Entity Mapping: Cypress Runner vs Playwright Fixtures
This diagram bridges the execution models between the two frameworks.

**Title: Cypress Runner to Playwright Fixture Mapping**
```mermaid
graph LR
    subgraph "Cypress Space"
        CR["cypress.config.js"]
        CY["cy object (Global)"]
        CI["cy.intercept()"]
    end

    subgraph "Playwright Space"
        PC["playwright.config.ts"]
        PF["{ page } fixture"]
        PR["page.route()"]
    end

    CR -.-> PC
    CY -.-> PF
    CI -.-> PR
```
**Sources:** [test-framework-migration-skill/reference/cypress-to-playwright.md:71-74](), [test-framework-migration-skill/reference/playwright-to-cypress.md:81-86]()

---

## 5. Cloud Migration (LambdaTest/TestMu)

Regardless of the framework path, cloud integration must be updated to the target framework's connection method.

| Target Framework | Connection Method | Endpoint / Tool |
|------------------|-------------------|-----------------|
| **Playwright** | CDP WebSocket | `wss://cdp.lambdatest.com/playwright` |
| **Selenium** | RemoteWebDriver | `hub.lambdatest.com/wd/hub` |
| **Cypress** | CLI / Plugin | `lambdatest-cypress` CLI |

**Sources:** [test-framework-migration-skill/reference/selenium-to-playwright.md:87-88](), [test-framework-migration-skill/reference/cypress-to-playwright.md:78-79](), [test-framework-migration-skill/reference/playwright-to-selenium.md:85-87]()

---

# Page: Selenium and Puppeteer Migration Paths

# Selenium and Puppeteer Migration Paths

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [test-framework-migration-skill/reference/cypress-to-selenium.md](test-framework-migration-skill/reference/cypress-to-selenium.md)
- [test-framework-migration-skill/reference/playwright-to-puppeteer.md](test-framework-migration-skill/reference/playwright-to-puppeteer.md)
- [test-framework-migration-skill/reference/puppeteer-to-selenium.md](test-framework-migration-skill/reference/puppeteer-to-selenium.md)
- [test-framework-migration-skill/reference/selenium-to-cypress.md](test-framework-migration-skill/reference/selenium-to-cypress.md)
- [test-framework-migration-skill/reference/selenium-to-puppeteer.md](test-framework-migration-skill/reference/selenium-to-puppeteer.md)

</details>



This page covers technical migration paths for end-to-end testing frameworks that do not involve Playwright as a primary target or source. It provides detailed API mapping, pattern conversion guides, and lifecycle management for transitions between **Selenium**, **Puppeteer**, and **Cypress**.

## 1. Puppeteer to Selenium Migration

Migrating from Puppeteer to Selenium typically involves moving from a JavaScript-only, Chrome-specific environment to a multi-language, multi-browser ecosystem.

### API Mapping Table
| Category | Puppeteer (JS) | Selenium (Java/JS) |
| :--- | :--- | :--- |
| **Locators** | `await page.$('#x')` | `driver.findElement(By.id("x"))` [test-framework-migration-skill/reference/puppeteer-to-selenium.md:9-9]() |
| **Waits** | `await page.waitForSelector('.sel')` | `wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".sel")))` [test-framework-migration-skill/reference/puppeteer-to-selenium.md:20-20]() |
| **Actions** | `await page.type('#x', 'text')` | `el.sendKeys("text")` [test-framework-migration-skill/reference/puppeteer-to-selenium.md:29-29]() |
| **Navigation** | `await page.goto(url)` | `driver.get(url)` [test-framework-migration-skill/reference/puppeteer-to-selenium.md:49-49]() |
| **Alerts** | `page.on('dialog', d => d.accept())` | `driver.switchTo().alert().accept()` [test-framework-migration-skill/reference/puppeteer-to-selenium.md:32-32]() |

### Key Differences and Implementation
*   **Explicit Waits:** Unlike Puppeteer's `waitForSelector`, Selenium requires the use of `WebDriverWait` combined with `ExpectedConditions` for almost every interaction to ensure DOM readiness [test-framework-migration-skill/reference/puppeteer-to-selenium.md:88-88]().
*   **Element Handles:** Puppeteer returns `ElementHandle`, while Selenium returns `WebElement`. It is recommended to store `By` locators and re-find elements to avoid `StaleElementReferenceException` [test-framework-migration-skill/reference/puppeteer-to-selenium.md:91-91]().
*   **Network Idle:** Puppeteer's `networkidle0` has no direct Selenium equivalent. Migration requires waiting for specific URL changes or element visibilities [test-framework-migration-skill/reference/puppeteer-to-selenium.md:92-92]().

### Conversion Diagram: Puppeteer JS to Selenium Java
The following diagram illustrates the translation of a login flow from Puppeteer's asynchronous JS to Selenium's synchronous Java pattern.

"Natural Language Space to Code Entity Space: Puppeteer vs Selenium"
```mermaid
graph TD
    subgraph "Puppeteer (JS)"
        P_Nav["page.goto()"] --> P_Wait["waitForNavigation()"]
        P_Wait --> P_Type["page.type()"]
        P_Type --> P_Click["page.click()"]
    end

    subgraph "Selenium (Java)"
        S_Nav["driver.get()"] --> S_Wait["WebDriverWait.until()"]
        S_Wait --> S_Send["WebElement.sendKeys()"]
        S_Send --> S_Click["ExpectedConditions.elementToBeClickable()"]
    end

    P_Nav -.->|"maps to"| S_Nav
    P_Type -.->|"maps to"| S_Send
    P_Click -.->|"maps to"| S_Click
```
Sources: [test-framework-migration-skill/reference/puppeteer-to-selenium.md:55-74]()

## 2. Selenium to Puppeteer Migration

This path is common when teams prioritize execution speed in Chromium-based browsers and want to leverage the Chrome DevTools Protocol (CDP) directly.

### API Mapping Table
| Category | Selenium | Puppeteer |
| :--- | :--- | :--- |
| **Locators** | `By.xpath("//button")` | `page.$('xpath///button')` [test-framework-migration-skill/reference/selenium-to-puppeteer.md:11-11]() |
| **Input** | `element.clear()` | `page.evaluate(s => { document.querySelector(s).value = ''; })` [test-framework-migration-skill/reference/selenium-to-puppeteer.md:32-32]() |
| **Frames** | `driver.switchTo().frame(name)` | `page.frames().find(f => f.name() === name)` [test-framework-migration-skill/reference/selenium-to-puppeteer.md:35-35]() |
| **Window** | `driver.manage().window().maximize()` | `page.setViewport({ width: 1920, height: 1080 })` [test-framework-migration-skill/reference/selenium-to-puppeteer.md:52-52]() |

### Implementation Gotchas
*   **Language Shift:** Moving to Puppeteer usually requires rewriting tests in JavaScript or TypeScript [test-framework-migration-skill/reference/selenium-to-puppeteer.md:86-86]().
*   **No Auto-Wait:** Like Selenium, Puppeteer does not auto-wait (unlike Playwright). You must explicitly call `page.waitForSelector()` [test-framework-migration-skill/reference/selenium-to-puppeteer.md:87-87]().
*   **Browser Limitation:** Migration to Puppeteer implies a move to Chrome/Chromium-only testing [test-framework-migration-skill/reference/selenium-to-puppeteer.md:85-85]().

Sources: [test-framework-migration-skill/reference/selenium-to-puppeteer.md:1-90]()

## 3. Cypress to Selenium Migration

This migration is often driven by requirements for multi-tab support, native mobile automation via Appium, or the need for a non-JavaScript language.

### API Mapping Table
| Category | Cypress | Selenium (Java) |
| :--- | :--- | :--- |
| **Locators** | `cy.contains('Submit')` | `By.xpath("//*[contains(text(),'Submit')]")` [test-framework-migration-skill/reference/cypress-to-selenium.md:12-12]() |
| **Assertions** | `should('be.visible')` | `ExpectedConditions.visibilityOfElementLocated()` [test-framework-migration-skill/reference/cypress-to-selenium.md:22-22]() |
| **Network** | `cy.intercept()` | No direct equivalent; use DevTools or app-level mocks [test-framework-migration-skill/reference/cypress-to-selenium.md:36-36]() |
| **API** | `cy.request()` | Use `HttpClient` or `OkHttp` [test-framework-migration-skill/reference/cypress-to-selenium.md:37-37]() |

### Pattern Conversion: Cypress Chain to Selenium Block
Cypress uses a command queue (non-async/await), whereas Selenium uses standard imperative control flow.

"Cypress Command Queue to Selenium Imperative Flow"
```mermaid
graph LR
    subgraph "Cypress Space"
        C_Chain["cy.get().type().click()"]
    end

    subgraph "Selenium Space"
        S_Find["driver.findElement()"]
        S_Wait["WebDriverWait"]
        S_Action["WebElement.click()"]
        
        S_Wait --> S_Find --> S_Action
    end

    C_Chain -.->|"transformed to"| S_Wait
```
Sources: [test-framework-migration-skill/reference/cypress-to-selenium.md:49-66](), [test-framework-migration-skill/reference/cypress-to-selenium.md:80-80]()

## 4. Selenium to Cypress Migration

This path is chosen for developers who prefer the "all-in-one" test runner experience and built-in retry-ability.

### API Mapping Table
| Category | Selenium | Cypress |
| :--- | :--- | :--- |
| **Wait for URL** | `ExpectedConditions.urlContains()` | `cy.url().should('include', ...)` [test-framework-migration-skill/reference/selenium-to-cypress.md:23-23]() |
| **Alerts** | `driver.switchTo().alert()` | `cy.on('window:confirm', ...)` [test-framework-migration-skill/reference/selenium-to-cypress.md:33-33]() |
| **Lifecycle** | `@BeforeEach` | `beforeEach(() => { cy.visit('/'); })` [test-framework-migration-skill/reference/selenium-to-cypress.md:50-50]() |

### Key Migration Considerations
*   **Retry-ability:** Selenium's `WebDriverWait` logic should be replaced with Cypress's `.should()` assertions, which automatically retry until the timeout [test-framework-migration-skill/reference/selenium-to-cypress.md:89-89]().
*   **No Async/Await:** Cypress commands are serial and managed by a internal runner; using `async/await` inside `it` blocks is an anti-pattern [test-framework-migration-skill/reference/selenium-to-cypress.md:87-87]().
*   **Single Tab:** Cypress does not support switching between multiple browser tabs, a common pattern in Selenium [test-framework-migration-skill/reference/selenium-to-cypress.md:90-90]().

Sources: [test-framework-migration-skill/reference/selenium-to-cypress.md:1-91]()

## 5. Playwright to Puppeteer Migration

While less common, this path may be required for projects needing specific Puppeteer plugins or lighter-weight execution for simple scraping tasks.

### API Mapping Table
| Category | Playwright | Puppeteer |
| :--- | :--- | :--- |
| **Locators** | `page.getByTestId('btn')` | `page.$('[data-testid="btn"]')` [test-framework-migration-skill/reference/playwright-to-puppeteer.md:12-12]() |
| **Filling** | `locator.fill('text')` | `element.type('text')` or `page.evaluate()` [test-framework-migration-skill/reference/playwright-to-puppeteer.md:30-30]() |
| **New Tabs** | `context.waitForEvent('page')` | `page.once('popup', ...)` [test-framework-migration-skill/reference/playwright-to-puppeteer.md:35-35]() |

### Critical Changes
*   **Auto-wait Removal:** Playwright's automatic waiting on actions (like `.click()`) is absent in Puppeteer. Every action must be preceded by an explicit `waitForSelector` [test-framework-migration-skill/reference/playwright-to-puppeteer.md:86-86]().
*   **Selector Logic:** Semantic locators like `getByRole` or `getByLabel` must be converted to standard CSS or XPath selectors [test-framework-migration-skill/reference/playwright-to-puppeteer.md:87-87]().

Sources: [test-framework-migration-skill/reference/playwright-to-puppeteer.md:1-91]()

## 6. Cloud Integration (TestMu/LambdaTest)

All migration paths involve updating the cloud connection logic to utilize the `LambdaTest` infrastructure.

| Framework | Connection Method |
| :--- | :--- |
| **Selenium** | `RemoteWebDriver` via Hub URL + `LT:Options` capabilities [test-framework-migration-skill/reference/puppeteer-to-selenium.md:84-84]() |
| **Puppeteer** | `puppeteer.connect()` via LambdaTest WebSocket endpoint [test-framework-migration-skill/reference/selenium-to-puppeteer.md:81-81]() |
| **Cypress** | Execution via `lambdatest-cypress` CLI [test-framework-migration-skill/reference/selenium-to-cypress.md:82-82]() |

Sources: [test-framework-migration-skill/reference/puppeteer-to-selenium.md:81-85](), [test-framework-migration-skill/reference/selenium-to-puppeteer.md:78-82]()

---

# Page: Capybara and RSpec Skills — Ruby on Rails Testing

# Capybara and RSpec Skills — Ruby on Rails Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [capybara-skill/SKILL.md](capybara-skill/SKILL.md)
- [capybara-skill/reference/advanced-patterns.md](capybara-skill/reference/advanced-patterns.md)
- [capybara-skill/reference/cloud-integration.md](capybara-skill/reference/cloud-integration.md)
- [capybara-skill/reference/playbook.md](capybara-skill/reference/playbook.md)
- [protractor-skill/reference/cloud-integration.md](protractor-skill/reference/cloud-integration.md)
- [rspec-skill/SKILL.md](rspec-skill/SKILL.md)
- [rspec-skill/reference/advanced-patterns.md](rspec-skill/reference/advanced-patterns.md)
- [rspec-skill/reference/playbook.md](rspec-skill/reference/playbook.md)

</details>



This page provides a high-level overview of the Ruby on Rails testing ecosystem within the Agent Skills framework. It focuses on the integration of **Capybara** for end-to-end feature testing and **RSpec** for unit and integration testing. These skills enable AI agents to generate robust, maintainable test suites using industry-standard Ruby patterns.

## Overview of Ruby Testing Skills

The Ruby testing stack in this repository is designed to cover the entire testing pyramid, from low-level model validations to complex multi-step browser interactions.

| Skill | Primary Purpose | Key Technologies |
|-------|-----------------|------------------|
| **Capybara** | Feature & Acceptance Testing | Selenium, SitePrism, Chrome Headless, TestMu AI |
| **RSpec** | Unit, Functional & Request Testing | Shoulda Matchers, FactoryBot, Mockito-style doubles |

### Natural Language to Code Entity Mapping (E2E)

The following diagram illustrates how natural language testing requirements are mapped to specific Ruby code entities and configurations.

**E2E Testing Entity Map**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Verify login flow'"]
        B["'Handle async loading'"]
        C["'Run on Cloud'"]
    end

    subgraph "Code Entity Space"
        A --> D["spec/features/login_spec.rb"]
        D --> E["LoginPage < SitePrism::Page"]
        B --> F["config.default_max_wait_time"]
        C --> G["Capybara.register_driver :lambdatest"]
    end

    subgraph "Infrastructure"
        G --> H["hub.lambdatest.com/wd/hub"]
        E --> I["#email, #password (CSS)"]
    end
```
**Sources:** [capybara-skill/reference/playbook.md:20-57](), [capybara-skill/reference/playbook.md:189-204](), [capybara-skill/reference/advanced-patterns.md:72-78]()

---

## Capybara Skill — Feature and Acceptance Testing

The Capybara skill focuses on high-level "Feature Specs" that simulate user behavior in a browser. It leverages `Selenium::WebDriver` for browser automation and `SitePrism` for implementing the Page Object Model (POM).

### Key Features
*   **SitePrism Integration:** Encapsulates UI elements into reusable Page and Section classes [capybara-skill/reference/playbook.md:189-218]().
*   **Wait Mechanics:** Utilizes Capybara's automatic waiting to handle asynchronous content without `sleep` calls [capybara-skill/reference/advanced-patterns.md:91-97]().
*   **Database Isolation:** Employs `DatabaseCleaner` with transaction and truncation strategies to ensure test hermeticity [capybara-skill/reference/playbook.md:14-15]().
*   **Cloud Execution:** Native support for LambdaTest via custom driver registration using `LT:Options` [capybara-skill/reference/cloud-integration.md:14-34]().

For detailed implementation patterns, including JavaScript modal handling and screenshot capture, see **[Capybara Skill — Feature and Acceptance Testing](#9.1)**.

---

## RSpec Skill — Ruby Unit and Integration Testing

The RSpec skill provides the foundation for testing Ruby logic. It covers unit tests for Models and Services, as well as Request specs for API testing.

### Key Features
*   **Expressive DSL:** Uses `describe`, `context`, and `it` blocks to create readable test hierarchies [rspec-skill/SKILL.md:21-47]().
*   **Verification Doubles:** Uses `instance_double` to create strict mocks that verify interface consistency [rspec-skill/reference/playbook.md:97-110]().
*   **Shared Logic:** Implements `shared_examples` and `shared_context` to reduce duplication across the test suite [rspec-skill/reference/advanced-patterns.md:3-25]().
*   **Rails Integration:** Deep integration with `rspec-rails` for testing controllers, models (via Shoulda Matchers), and routing [rspec-skill/reference/playbook.md:59-89]().

### Natural Language to Code Entity Mapping (Unit/Logic)

**Logic Testing Entity Map**
```mermaid
graph TD
    subgraph "Natural Language Space"
        NL1["'Test user validation'"]
        NL2["'Mock external API'"]
        NL3["'Reuse auth setup'"]
    end

    subgraph "Code Entity Space"
        NL1 --> C1["it { is_expected.to validate_presence_of }"]
        NL2 --> C2["instance_double(PaymentGateway)"]
        NL3 --> C3["shared_context 'authenticated user'"]
    end

    subgraph "Support Files"
        C1 --> S1["spec/models/user_spec.rb"]
        C2 --> S2["spec/services/order_service_spec.rb"]
        C3 --> S3["spec/support/auth_helper.rb"]
    end
```
**Sources:** [rspec-skill/reference/playbook.md:161-169](), [rspec-skill/reference/advanced-patterns.md:15-19](), [rspec-skill/reference/advanced-patterns.md:59-62]()

For details on advanced matchers, FactoryBot traits, and service object testing, see **[RSpec Skill — Ruby Unit and Integration Testing](#9.2)**.

---

## Cloud Integration with TestMu AI

Both Capybara and RSpec (via request specs) can be integrated with cloud environments. For browser-based tests, Capybara registers a `:lambdatest` driver that points to the remote hub.

| Component | Configuration Key | Purpose |
|-----------|-------------------|---------|
| **Hub URL** | `hub.lambdatest.com/wd/hub` | Remote WebDriver endpoint [capybara-skill/reference/playbook.md:54-55]() |
| **Capabilities** | `LT:Options` | Sets platform, build name, and video recording [capybara-skill/reference/cloud-integration.md:18-26]() |
| **Auth** | `LT_USERNAME` / `LT_ACCESS_KEY` | Environment variables for secure access [capybara-skill/reference/cloud-integration.md:31-34]() |

**Sources:** [capybara-skill/reference/playbook.md:43-57](), [capybara-skill/reference/cloud-integration.md:1-39]()

---

# Page: Capybara Skill — Feature and Acceptance Testing

# Capybara Skill — Feature and Acceptance Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [capybara-skill/SKILL.md](capybara-skill/SKILL.md)
- [capybara-skill/reference/advanced-patterns.md](capybara-skill/reference/advanced-patterns.md)
- [capybara-skill/reference/cloud-integration.md](capybara-skill/reference/cloud-integration.md)
- [capybara-skill/reference/playbook.md](capybara-skill/reference/playbook.md)
- [protractor-skill/reference/cloud-integration.md](protractor-skill/reference/cloud-integration.md)
- [rspec-skill/reference/playbook.md](rspec-skill/reference/playbook.md)

</details>



Capybara is a Ruby-based acceptance testing framework that simulates how a real user would interact with a web application. This page details the integration of Capybara with RSpec, the use of SitePrism for Page Object modeling, and configuration for both local headless execution and LambdaTest cloud execution.

## §1 Driver Configuration and Selenium Setup

Capybara requires a driver to interface with browsers. While it supports multiple drivers, `selenium-webdriver` is the standard for modern web applications.

### Local Headless Configuration
For CI/CD and local development, a headless Chrome driver is typically registered to run tests without a GUI [capybara-skill/reference/playbook.md:34-41]().

```ruby
Capybara.register_driver :selenium_chrome_headless do |app|
  options = Selenium::WebDriver::Chrome::Options.new
  options.add_argument('--headless=new')
  options.add_argument('--no-sandbox')
  options.add_argument('--window-size=1920,1080')
  Capybara::Selenium::Driver.new(app, browser: :chrome, options: options)
end
```
**Sources:** [capybara-skill/reference/playbook.md:34-41](), [capybara-skill/reference/advanced-patterns.md:80-86]()

### LambdaTest Cloud Integration
To run tests on the LambdaTest cloud, a remote driver must be registered using the `LT:Options` capability block [capybara-skill/reference/playbook.md:44-56](). This requires `LT_USERNAME` and `LT_ACCESS_KEY` environment variables [capybara-skill/reference/cloud-integration.md:22-23]().

**Driver Registration Flow**
The following diagram illustrates how the Capybara driver connects to the LambdaTest Hub.

Title: Capybara to LambdaTest Driver Registration
```mermaid
graph TD
    subgraph "Local Environment"
        A["Capybara.register_driver :lambdatest"] --> B["Selenium::WebDriver::Chrome::Options"]
        B --> C["LT:Options Capability Map"]
    end
    
    subgraph "Code Entities"
        C --> D["ENV['LT_USERNAME']"]
        C --> E["ENV['LT_ACCESS_KEY']"]
    end
    
    subgraph "Cloud Infrastructure"
        F["hub.lambdatest.com/wd/hub"]
    end
    
    C --> F
    F --> G["Remote Browser Instance"]
```
**Sources:** [capybara-skill/reference/playbook.md:44-56](), [capybara-skill/reference/cloud-integration.md:14-34]()

## §2 SitePrism Page Objects

SitePrism provides a DSL for defining Page Objects in Capybara, allowing for better abstraction of UI elements and sections [capybara-skill/reference/playbook.md:189-218]().

### Elements and Sections
*   **Elements:** Single UI components defined by CSS or XPath selectors [capybara-skill/reference/playbook.md:193-197]().
*   **Sections:** Reusable groups of elements (e.g., a Sidebar or Navbar) [capybara-skill/reference/playbook.md:213]().
*   **Loaders:** Methods like `load` and `be_displayed` that manage navigation and URL matching [capybara-skill/reference/playbook.md:207-208](), [capybara-skill/reference/playbook.md:226-228]().

**Page Object Structure**
Title: SitePrism Class Hierarchy and Mapping
```mermaid
classDiagram
    class SitePrism_Page {
        +set_url(path)
        +load()
        +displayed?()
    }
    class LoginPage {
        +element email_field
        +element password_field
        +element submit_button
        +login(email, password)
    }
    class DashboardPage {
        +section sidebar
        +elements recent_orders
        +order_count()
    }
    SitePrism_Page <|-- LoginPage
    SitePrism_Page <|-- DashboardPage
    DashboardPage *-- SidebarSection
```
**Sources:** [capybara-skill/reference/playbook.md:189-218](), [capybara-skill/reference/advanced-patterns.md:5-29]()

## §3 Automatic Waiting and Interaction

Capybara's core strength is its automatic waiting mechanism. It synchronizes the test with the browser by retrying finders and matchers until the `default_max_wait_time` is reached [capybara-skill/reference/playbook.md:28]().

### Key Interaction Methods
*   **Navigation:** `visit(path)` [capybara-skill/SKILL.md:50]().
*   **Forms:** `fill_in`, `choose`, `check`, `select` [capybara-skill/SKILL.md:55-59]().
*   **Buttons/Links:** `click_button`, `click_link` [capybara-skill/SKILL.md:61-62]().
*   **Scoping:** `within(selector)` restricts the search scope for all nested commands [capybara-skill/SKILL.md:86-89]().

### JavaScript-Enabled Specs
Specs requiring JavaScript execution must be tagged with `js: true` [capybara-skill/reference/playbook.md:108](). This switches the driver to the `javascript_driver` (usually Selenium) instead of the default `rack_test` [capybara-skill/reference/advanced-patterns.md:88-89]().

**Sources:** [capybara-skill/SKILL.md:49-89](), [capybara-skill/reference/playbook.md:108-151](), [capybara-skill/reference/advanced-patterns.md:73-78]()

## §4 Database Isolation Strategy

When running feature tests, the test runner and the application server often run in different threads or processes, making standard database transactions problematic for data sharing.

### Transaction vs. Truncation
*   **Transactions:** Used for standard RSpec unit/model tests where the database connection is shared [rspec-skill/reference/playbook.md:69]().
*   **Truncation:** Required for JavaScript-enabled feature specs (`js: true`). The `DatabaseCleaner` gem is used to wipe the database between tests to ensure isolation [rspec-skill/reference/playbook.md:77-80]().

| Strategy | Usage Context | Performance |
| :--- | :--- | :--- |
| **Transaction** | Model/Request Specs | Fast |
| **Truncation** | Feature Specs (JS enabled) | Slower |

**Sources:** [rspec-skill/reference/playbook.md:68-81](), [capybara-skill/reference/playbook.md:14-17]()

## §5 Failure Handling and Screenshots

Capybara can be configured to capture the state of the application automatically upon test failure.

*   **Screenshot Capture:** Using `capybara-screenshot`, the system saves the HTML and a PNG of the page when a spec fails [capybara-skill/reference/playbook.md:12]().
*   **Save Path:** The location is defined via `Capybara.save_path` [capybara-skill/reference/playbook.md:30]().
*   **Alert Handling:** For JS alerts, Capybara provides `accept_alert` and `dismiss_confirm` blocks to handle browser dialogs [capybara-skill/reference/playbook.md:175-180](), [capybara-skill/reference/advanced-patterns.md:64-66]()

**Sources:** [capybara-skill/reference/playbook.md:12-30](), [capybara-skill/reference/playbook.md:175-180](), [capybara-skill/reference/advanced-patterns.md:64-66]()

---

# Page: RSpec Skill — Ruby Unit and Integration Testing

# RSpec Skill — Ruby Unit and Integration Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [capybara-skill/SKILL.md](capybara-skill/SKILL.md)
- [capybara-skill/reference/advanced-patterns.md](capybara-skill/reference/advanced-patterns.md)
- [capybara-skill/reference/cloud-integration.md](capybara-skill/reference/cloud-integration.md)
- [capybara-skill/reference/playbook.md](capybara-skill/reference/playbook.md)
- [protractor-skill/reference/cloud-integration.md](protractor-skill/reference/cloud-integration.md)
- [rspec-skill/SKILL.md](rspec-skill/SKILL.md)
- [rspec-skill/reference/advanced-patterns.md](rspec-skill/reference/advanced-patterns.md)
- [rspec-skill/reference/playbook.md](rspec-skill/reference/playbook.md)

</details>



The RSpec skill provides a comprehensive framework for behavior-driven development (BDD) in Ruby. It covers unit testing for models and service objects, integration testing via request specs, and advanced mocking techniques using verification doubles.

## Core Implementation Architecture

RSpec organizes tests into logical blocks (`describe`, `context`, `it`) to define behavior. It utilizes a domain-specific language (DSL) for assertions (`expect().to`) and lifecycle management (`let`, `subject`, `before`).

### Test Structure and Data Flow

The following diagram illustrates the flow from a Natural Language requirement to the RSpec code entities that implement the test logic.

**Requirement to Code Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        REQ["'User should be able to create an account'"]
        SCENARIO_A["'Success: Valid data'"]
        SCENARIO_B["'Failure: Duplicate email'"]
    end

    subgraph "Code Entity Space (RSpec)"
        DESCRIBE["RSpec.describe UserService"]
        CONTEXT_A["context 'with valid data'"]
        CONTEXT_B["context 'with duplicate email'"]
        
        LET_REPO["let(:repo) { instance_double(UserRepository) }"]
        LET_SERVICE["let(:service) { described_class.new(repo) }"]
        
        IT_SAVE["it 'persists to repository'"]
        IT_RAISE["it 'raises ConflictError'"]
    end

    REQ --> DESCRIBE
    SCENARIO_A --> CONTEXT_A
    SCENARIO_B --> CONTEXT_B
    
    CONTEXT_A --> IT_SAVE
    CONTEXT_B --> IT_RAISE
    
    DESCRIBE --> LET_REPO
    DESCRIBE --> LET_SERVICE
```
**Sources:** [rspec-skill/SKILL.md:21-47](), [rspec-skill/reference/playbook.md:97-158]()

## Project Configuration

A standard RSpec setup requires a `Gemfile` for dependency management and configuration files (`.rspec`, `spec_helper.rb`) to define execution behavior.

### Essential Dependencies
The testing environment typically includes `rspec-rails` for Rails integration, `factory_bot_rspec` for test data, and `shoulda-matchers` for concise model assertions.
[rspec-skill/reference/playbook.md:5-19]()

### Configuration Files
- **`.rspec`**: Sets default CLI arguments like `--color` and `--order random` [rspec-skill/reference/playbook.md:21-28]().
- **`spec/spec_helper.rb`**: Configures the RSpec framework, including expectation syntax and mock verification [rspec-skill/reference/playbook.md:30-57]().
- **`spec/rails_helper.rb`**: (Rails only) Loads the Rails environment and configures database cleaning strategies [rspec-skill/reference/playbook.md:59-89]().

## Unit Testing: Models and Services

### Service Object Testing with Doubles
Service objects are tested by isolating them from their dependencies using `instance_double`. This ensures that the test only verifies the logic within the service itself.

| Feature | Code Entity | Purpose |
| :--- | :--- | :--- |
| **Dependency** | `instance_double(UserRepository)` | Creates a verified mock of the repository [rspec-skill/reference/playbook.md:98](). |
| **Subject** | `described_class.new(repo)` | Instantiates the class under test [rspec-skill/reference/playbook.md:100](). |
| **Stubbing** | `allow(repo).to receive(:save)` | Defines the behavior of the mock [rspec-skill/reference/playbook.md:108](). |
| **Verification** | `expect(repo).to have_received(:save)` | Asserts that the dependency was called [rspec-skill/reference/playbook.md:124](). |

### Rails Model Validations
Using `shoulda-matchers`, model tests become declarative, verifying presence, uniqueness, and associations with minimal boilerplate.
[rspec-skill/reference/playbook.md:161-185]()

## Integration Testing: Request Specs

Request specs (API tests) verify the entire stack from the routing layer down to the database. They use `have_http_status` and JSON parsing to validate responses.

**Request Spec Data Flow**
```mermaid
sequenceDiagram
    participant Spec as "RSpec (Request Spec)"
    participant Rails as "Rails App / API"
    participant DB as "Database (ActiveRecord)"

    Spec->>Rails: post "/api/users", params: valid_params
    Rails->>DB: User.create!(...)
    DB-->>Rails: user_record
    Rails-->>Spec: HTTP 201 (Created) + JSON Body
    
    Note over Spec: expect(response).to have_http_status(:created)
    Note over Spec: expect(json_body["name"]).to eq("Alice")
```
**Sources:** [rspec-skill/reference/advanced-patterns.md:88-106](), [capybara-skill/reference/playbook.md:239-252]()

## Advanced Patterns

### Shared Examples and Contexts
To adhere to DRY (Don't Repeat Yourself) principles, RSpec provides mechanisms to share test logic across multiple specs.
- **Shared Examples**: Used to test common behavior across different classes (e.g., "a searchable resource") [rspec-skill/reference/playbook.md:193-224]().
- **Shared Context**: Used to share setup code, such as authentication headers [rspec-skill/reference/playbook.md:227-245]().

### Custom Matchers
Developers can define domain-specific matchers to improve test readability. For example, a `have_json_body_with` matcher can encapsulate JSON parsing and key-value verification [rspec-skill/reference/advanced-patterns.md:111-120]().

### Mocking with Spies
While `instance_double` requires pre-defining expectations, `spy` allows for "act-then-assert" patterns where calls are verified after the action has occurred [rspec-skill/reference/advanced-patterns.md:61-75]().

## CI/CD and Coverage

### SimpleCov Integration
RSpec integrates with `SimpleCov` to generate code coverage reports. Minimum coverage thresholds can be enforced in `spec_helper.rb` to ensure testing rigor.
[rspec-skill/reference/playbook.md:32-39]()

### Database Cleaning Strategy
To maintain test isolation, `DatabaseCleaner` is used to reset the database state between examples. The standard strategy is `:transaction` for speed, with `:truncation` used for the initial suite setup.
[rspec-skill/reference/playbook.md:77-81](), [rspec-skill/reference/advanced-patterns.md:133-135]()

## Summary of Best Practices

| Category | Recommended Pattern | Avoid (Anti-Pattern) |
| :--- | :--- | :--- |
| **Setup** | Use lazy `let` blocks [rspec-skill/SKILL.md:150]() | Using `before` for heavy data setup [rspec-skill/SKILL.md:150]() |
| **Subjects** | Use named subjects: `subject(:service)` [rspec-skill/reference/advanced-patterns.md:141]() | Anonymous `subject { ... }` [rspec-skill/reference/advanced-patterns.md:141]() |
| **Mocking** | Inject dependencies/doubles [rspec-skill/reference/advanced-patterns.md:144]() | Using `allow_any_instance_of` [rspec-skill/reference/advanced-patterns.md:144]() |
| **Syntax** | Use `expect().to` [rspec-skill/SKILL.md:153]() | Using legacy `should` syntax [rspec-skill/SKILL.md:153]() |

**Sources:** [rspec-skill/SKILL.md:147-154](), [rspec-skill/reference/advanced-patterns.md:139-145]()

---

# Page: Evaluation Framework — Skill Quality Assurance

# Evaluation Framework — Skill Quality Assurance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [evals/appium-skill-evals.json](evals/appium-skill-evals.json)
- [evals/cypress-skill-evals.json](evals/cypress-skill-evals.json)
- [evals/detox-skill-evals.json](evals/detox-skill-evals.json)
- [evals/espresso-skill-evals.json](evals/espresso-skill-evals.json)
- [evals/flutter-testing-skill-evals.json](evals/flutter-testing-skill-evals.json)
- [evals/selenium-skill-evals.json](evals/selenium-skill-evals.json)
- [evals/webdriverio-skill-evals.json](evals/webdriverio-skill-evals.json)
- [evals/xcuitest-skill-evals.json](evals/xcuitest-skill-evals.json)
- [flutter-testing-skill/SKILL.md](flutter-testing-skill/SKILL.md)
- [flutter-testing-skill/reference/advanced-patterns.md](flutter-testing-skill/reference/advanced-patterns.md)

</details>



The Evaluation Framework provides a systematic method for validating the quality, accuracy, and behavior of AI agent outputs when using the TestMu AI Agent Skills. By utilizing a structured JSON format, the framework ensures that every skill—ranging from Selenium to Flutter—adheres to the Agent Skills Standard and produces technically sound test code.

## Framework Overview

The core of the evaluation system resides in the `evals/` directory, which contains 45+ JSON files, one for each skill in the repository. These evaluations act as "test cases for the AI," defining specific user queries and the expected code entities or patterns that the AI should generate in response.

### Core Objectives
*   **Validation:** Ensure AI agents use the correct libraries and classes (e.g., `RemoteWebDriver` for cloud vs `WebDriver` for local).
*   **Regression Testing:** Prevent updates to `SKILL.md` files from breaking existing generation patterns.
*   **Negative Triggering:** Verify that skills do not activate for irrelevant queries (e.g., a Cypress skill should not respond to a Selenium query).
*   **Cloud Routing:** Confirm that cloud-specific capabilities like `LT:Options` are suggested when users mention LambdaTest.

### Evaluation Mapping: Natural Language to Code Entity
The following diagram illustrates how the evaluation framework bridges the gap between a user's natural language intent and the required technical implementation defined in the skill files.

**Evaluation Flow: Intent to Code Validation**
```mermaid
graph TD
    UserQuery["User Query (Natural Language)"] --> EvalEngine["Evaluation Engine"]
    EvalEngine --> JSON_Eval["evals/*.json Entry"]
    
    subgraph "Code Entity Space"
        JSON_Eval --> ExpectedPatterns["'expected' Array"]
        ExpectedPatterns --> CodeCheck1["Class Names (e.g., 'UiAutomator2Options')"]
        ExpectedPatterns --> CodeCheck2["Method Calls (e.g., 'pumpAndSettle')"]
        ExpectedPatterns --> CodeCheck3["Cloud Config (e.g., 'hub.lambdatest.com')"]
    end
    
    CodeCheck1 -.-> SkillMD["SKILL.md Patterns"]
    CodeCheck2 -.-> SkillMD
    CodeCheck3 -.-> SkillMD
```
Sources: [evals/appium-skill-evals.json:1-13](), [evals/flutter-testing-skill-evals.json:1-15]()

---

## The Evaluation Format

Each evaluation file follows a strict schema that identifies the skill and lists multiple test scenarios. These scenarios are categorized to cover different aspects of the skill's lifecycle, from basic generation to advanced anti-pattern correction.

### Key Schema Fields
| Field | Description | Example |
| :--- | :--- | :--- |
| `skill` | The unique identifier of the skill being tested. | `selenium-automation-skill` |
| `id` | A unique identifier for the specific evaluation case. | `sel-01` |
| `category` | The type of test (e.g., `cloud-routing`, `pom-structure`). | `cloud-routing` |
| `query` | The natural language prompt sent to the AI agent. | "Run my Selenium tests on LambdaTest" |
| `expected` | An array of strings/tokens that MUST appear in the output. | `["RemoteWebDriver", "LT:Options"]` |

For a deep dive into the available categories and specific examples from Playwright and Appium, see **[Eval File Format and Categories](#10.1)**.

Sources: [evals/selenium-skill-evals.json:1-25](), [evals/appium-skill-evals.json:1-35]()

---

## Validation and Maintenance

The repository includes specialized Python scripts to maintain the integrity of the skills and their corresponding evaluations. These scripts are used during CI/CD and before merging any Pull Requests to ensure that new contributions do not degrade the quality of the registry.

### Repository Quality Workflow
The diagram below shows how the validation scripts interact with the skill files and evaluation definitions.

**Skill Validation Logic**
```mermaid
graph LR
    subgraph "Validation Inputs"
        SKILL_MD["SKILL.md (Frontmatter)"]
        EVAL_JSON["evals/*.json (Schema)"]
        REF_FILES["reference/*.md (Content)"]
    end

    subgraph "Maintenance Scripts"
        VS["validate_skills.py"]
        RS["rename_skills.py"]
    end

    SKILL_MD --> VS
    EVAL_JSON --> VS
    REF_FILES --> VS
    
    VS --> Result{"Pass/Fail"}
    RS --> SKILL_MD
    
    Result -- "Fail" --> Dev["Fix Frontmatter/Links"]
    Result -- "Pass" --> PR["Merge Pull Request"]
```
Sources: [flutter-testing-skill/SKILL.md:1-16](), [evals/cypress-skill-evals.json:1-53]()

### Key Maintenance Utilities
*   **`validate_skills.py`**: Enforces the Agent Skills Standard, including frontmatter fields, line count limits, and the existence of required reference files.
*   **`rename_skills.py`**: A utility for bulk-updating skill identifiers across the registry and evaluation files to maintain consistency.

For details on running these scripts and the specific rules they enforce, see **[Validation Scripts — validate_skills.py and rename_skills.py](#10.2)**.

---

## Child Pages
*   **[Eval File Format and Categories](#10.1)**: Documents the JSON schema, category definitions (basic-generation, cloud-routing, etc.), and negative trigger patterns.
*   **[Validation Scripts — validate_skills.py and rename_skills.py](#10.2)**: Technical guide for using the maintenance scripts to validate frontmatter, line counts, and cross-references.

---

# Page: Eval File Format and Categories

# Eval File Format and Categories

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [evals/appium-skill-evals.json](evals/appium-skill-evals.json)
- [evals/cypress-skill-evals.json](evals/cypress-skill-evals.json)
- [evals/espresso-skill-evals.json](evals/espresso-skill-evals.json)
- [evals/selenium-skill-evals.json](evals/selenium-skill-evals.json)
- [evals/webdriverio-skill-evals.json](evals/webdriverio-skill-evals.json)

</details>



The evaluation framework in the `agent-skills` repository provides a structured method for validating the quality and accuracy of AI agent outputs against the defined skills. Each skill in the repository is accompanied by a corresponding JSON evaluation file located in the `evals/` directory. These files define a series of test cases (queries) and the expected markers that an AI assistant must produce to demonstrate mastery of that specific skill.

## Eval JSON Schema

The evaluation files follow a consistent JSON schema that allows for automated validation of AI responses. Each file is dedicated to a single skill and contains an array of evaluation objects.

### Root Fields
*   `skill`: The unique identifier of the skill being evaluated (e.g., `appium-automation-skill`) [evals/appium-skill-evals.json:2]().
*   `evals`: An array of evaluation test cases [evals/appium-skill-evals.json:3]().

### Evaluation Object Fields
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | String | A unique identifier for the specific test case (e.g., `sel-01`, `app-02`) [evals/selenium-skill-evals.json:5](). |
| `category` | String | The functional area being tested (e.g., `cloud-routing`, `pom-structure`) [evals/selenium-skill-evals.json:6](). |
| `query` | String | The natural language prompt provided to the AI agent [evals/selenium-skill-evals.json:7](). |
| `expected` | Array | A list of strings, code symbols, or constraints that must be present (or absent) in the AI's response [evals/selenium-skill-evals.json:8-13](). |

**Sources:**
* [evals/appium-skill-evals.json:1-76]()
* [evals/selenium-skill-evals.json:1-65]()

## Eval Categories

Evaluations are categorized to ensure comprehensive coverage of the skill's capabilities, ranging from basic code generation to complex architectural patterns and platform-specific routing.

### 1. Basic Generation
Tests the agent's ability to generate fundamental test scripts using the framework's core syntax.
*   **Example (Selenium):** Verifies usage of `WebDriverWait`, `By.id`, and `driver.quit` [evals/selenium-skill-evals.json:6-13]().
*   **Example (Cypress):** Verifies usage of `cy.visit`, `cy.get`, and `.should()` [evals/cypress-skill-evals.json:5-14]().

### 2. Cloud Routing
Ensures the agent correctly configures the connection to the LambdaTest/TestMu AI cloud platform, including authentication and capability management.
*   **Key Markers:** `LT:Options`, `hub.lambdatest.com`, `LT_USERNAME`, and `RemoteWebDriver` [evals/selenium-skill-evals.json:17-24]().
*   **Mobile Specifics:** Use of `mobile-hub.lambdatest.com`, `isRealMobile`, and `lt://` app URLs [evals/appium-skill-evals.json:27-35]().

### 3. Language Detection
Validates that the agent respects the user's requested programming language and does not default to the framework's most common language (e.g., ensuring Python is used instead of Java for Selenium if requested).
*   **Constraint:** Often includes a `"NOT [Language]"` marker to ensure the agent doesn't mix stacks [evals/selenium-skill-evals.json:28-35]().

### 4. POM Structure
Evaluates the agent's understanding of the Page Object Model (POM) architectural pattern.
*   **Expected Elements:** `BasePage` classes, inheritance (e.g., `LoginPage extends`), and locators defined as class fields [evals/selenium-skill-evals.json:39-46]().

### 5. Mobile Specifics (Gestures & Hybrid)
For mobile skills like Appium, specific categories handle complex interactions like touch gestures and WebView switching.
*   **Gestures:** Checks for W3C Actions API components like `PointerInput` and `Sequence` [evals/appium-skill-evals.json:49-56]().
*   **Hybrid:** Validates context switching using `getContextHandles` and `WEBVIEW` [evals/appium-skill-evals.json:59-67]().

### 6. Anti-Patterns and Debugging
Tests if the agent can identify and correct poor testing practices or handle common exceptions.
*   **Anti-Pattern:** Identifying that `cy.wait(5000)` is flaky and suggesting `cy.intercept` instead [evals/cypress-skill-evals.json:37-44]().
*   **Debugging:** Suggesting `ExpectedConditions` and re-locating elements for `StaleElementReferenceException` [evals/selenium-skill-evals.json:49-56]().

### 7. Negative Triggers
Ensures the skill does **not** activate when the query is clearly intended for a different framework.
*   **Marker:** `should NOT activate` [evals/webdriverio-skill-evals.json:27-31]().

**Sources:**
* [evals/appium-skill-evals.json:5-75]()
* [evals/selenium-skill-evals.json:5-64]()
* [evals/cypress-skill-evals.json:5-52]()
* [evals/webdriverio-skill-evals.json:5-32]()

## Data Flow: From Query to Validation

The following diagram illustrates how a natural language query is mapped against the evaluation criteria defined in the JSON files to validate an AI agent's response.

### Logic Flow for Eval Validation
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserQuery["'Run Appium on Pixel 8 at LambdaTest'"]
    end

    subgraph "Eval Definition Space (JSON)"
        EvalID["id: app-03"]
        EvalCat["category: cloud-routing"]
        ExpectedMarkers["expected: ['mobile-hub', 'lt://', 'LT:Options']"]
    end

    subgraph "Code Entity Space (AI Output)"
        OutputCode["Generated Code Block"]
        CheckHub["mobile-hub.lambdatest.com"]
        CheckProtocol["lt://APP_ID"]
        CheckOpts["LT:Options"]
    end

    UserQuery -->|Matches Query Field| EvalID
    EvalID --> EvalCat
    EvalCat --> ExpectedMarkers
    
    ExpectedMarkers -->|Validation Logic| CheckHub
    ExpectedMarkers -->|Validation Logic| CheckProtocol
    ExpectedMarkers -->|Validation Logic| CheckOpts
    
    CheckHub -.->|Found In| OutputCode
    CheckProtocol -.->|Found In| OutputCode
    CheckOpts -.->|Found In| OutputCode
```

**Sources:**
* [evals/appium-skill-evals.json:27-35]()

## Framework Specific Examples

### Appium Mobile Evaluation
Appium evaluations distinguish between Android (`UiAutomator2Options`) and iOS (`XCUITestOptions`) to ensure platform-specific drivers are utilized correctly.

| ID | Category | Query Snippet | Expected Markers |
| :--- | :--- | :--- | :--- |
| `app-01` | basic-android | "Write an Appium test... Android" | `UiAutomator2Options`, `AndroidDriver` |
| `app-02` | basic-ios | "Write an Appium test... iOS" | `XCUITestOptions`, `IOSDriver` |

[evals/appium-skill-evals.json:4-24]()

### Cypress and WebdriverIO Comparison
Evaluations ensure that the agent uses the correct syntax for frameworks that might otherwise appear similar (e.g., both use JavaScript).

```mermaid
graph LR
    subgraph "Cypress Eval (cy-01)"
        CyQuery["'Cypress login'"]
        CyExpect["cy.visit, cy.get, .should()"]
    end

    subgraph "WDIO Eval (wdio-01)"
        WDIOQuery["'WebdriverIO login'"]
        WDIOExpect["browser.url, $, await"]
    end

    CyQuery -->|Matches| CyExpect
    WDIOQuery -->|Matches| WDIOExpect
```

**Sources:**
* [evals/cypress-skill-evals.json:4-14]()
* [evals/webdriverio-skill-evals.json:4-14]()

## Implementation Details

The evaluation files are consumed by testing scripts to perform automated "LLM-as-a-judge" or string-matching validation.

1.  **Loading:** The script iterates through the `evals/` directory.
2.  **Execution:** For each `query` in the JSON, the AI agent is prompted.
3.  **Verification:** The resulting output is scanned for the presence of every string in the `expected` array.
4.  **Negative Constraints:** If a string starts with `NOT `, the validator ensures that specific term is **absent** from the output (e.g., `NOT Java` in a Python eval [evals/selenium-skill-evals.json:34]()).
5.  **Activation Check:** For `negative-trigger` categories, the validator ensures the agent does not provide a detailed implementation for a framework it isn't supposed to handle [evals/appium-skill-evals.json:69-75]().

**Sources:**
* [evals/appium-skill-evals.json:44]()
* [evals/selenium-skill-evals.json:34]()
* [evals/cypress-skill-evals.json:47-52]()

---

# Page: Validation Scripts — validate_skills.py and rename_skills.py

# Validation Scripts — validate_skills.py and rename_skills.py

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/rename_skills.py](scripts/rename_skills.py)
- [scripts/validate_skills.py](scripts/validate_skills.py)

</details>



The `agent-skills` repository includes a suite of maintenance scripts located in the `scripts/` directory. These tools ensure that all 46+ skills adhere to the **Agent Skills Standard**, maintain structural integrity across the `skills_index.json` registry, and provide utilities for bulk refactoring of skill naming conventions.

## Skill Validation — validate_skills.py

The `scripts/validate_skills.py` script is the primary quality gate for the repository. It performs static analysis on `SKILL.md` files, directory structures, and the global index to ensure AI coding assistants can reliably consume the content.

### Validation Logic and Data Flow

The script iterates through the repository root, skipping non-skill directories like `evals`, `scripts`, and `docs` [scripts/validate_skills.py:10-10](). For every directory containing a `SKILL.md` file, it executes a multi-layered validation suite.

#### 1. Frontmatter Validation
The `validate_frontmatter` function uses regular expressions to enforce the presence and format of YAML metadata [scripts/validate_skills.py:24-62]().

| Field | Requirement | Severity |
| :--- | :--- | :--- |
| `name` | Must exist in frontmatter | Error |
| `description` | Must exist in frontmatter | Error |
| `languages` | List of supported languages | Warning |
| `category` | Must be one of the `VALID_CATEGORIES` | Warning |
| `license` | Must specify license (e.g., MIT) | Warning |
| `metadata` | Must include `author: TestMu AI` and `version` | Warning |

The `VALID_CATEGORIES` set includes: `accessibility`, `api-testing`, `bdd-testing`, `cloud-testing`, `devops`, `e2e-testing`, `mobile-testing`, `performance-testing`, `security-testing`, `unit-testing`, `visual-testing` [scripts/validate_skills.py:13-17]().

#### 2. Content and Structural Enforcement
The `validate_skill` function enforces physical constraints and cross-references [scripts/validate_skills.py:65-118]():
*   **Line Count:** `SKILL.md` files are restricted to a maximum of 500 lines to ensure they fit within LLM context windows [scripts/validate_skills.py:11-11](), [scripts/validate_skills.py:82-83]().
*   **Reference Links:** Checks if `SKILL.md` actually links to its internal `reference/playbook.md` [scripts/validate_skills.py:98-99]().
*   **Cloud Integration:** For `e2e-testing` category skills, the script warns if there is no `cloud-integration.md` or link to the `shared/testmu-cloud-reference.md` [scripts/validate_skills.py:104-108]().
*   **Debugging Section:** Inspects `playbook.md` for a "debugging" section, which is a requirement for the standard troubleshooting table [scripts/validate_skills.py:115-116]().

#### 3. Index Synchronization
The `validate_skills_index` function ensures that `skills_index.json` is perfectly synchronized with the filesystem [scripts/validate_skills.py:119-155](). It verifies that every file path listed in the index exists on disk and warns if a Markdown file exists in a `reference/` folder but is missing from the index [scripts/validate_skills.py:152-153]().

### Validation Process Diagram

The following diagram illustrates how `validate_skills.py` maps the physical file structure to the logical validation rules.

**Skill Validation Flow**
```mermaid
graph TD
    subgraph "Filesystem Space"
        ROOT["REPO_ROOT"]
        SK_DIR["Skill Directory (e.g., playwright-skill/)"]
        SK_MD["SKILL.md"]
        REF_DIR["reference/"]
        IDX["skills_index.json"]
    end

    subgraph "Code Entity Space: validate_skills.py"
        MAIN["main()"]
        V_SKILL["validate_skill()"]
        V_FM["validate_frontmatter()"]
        V_IDX["validate_skills_index()"]
    end

    ROOT --> MAIN
    MAIN -->|Iterates| SK_DIR
    SK_DIR --> V_SKILL
    V_SKILL -->|Reads| SK_MD
    V_SKILL --> V_FM
    V_SKILL -->|Checks Existence| REF_DIR
    MAIN --> V_IDX
    V_IDX -->|Parses| IDX
    V_IDX -->|Cross-references| SK_MD
```
**Sources:** [scripts/validate_skills.py:156-168](), [scripts/validate_skills.py:65-75](), [scripts/validate_skills.py:119-130]()

---

## Bulk Renaming — rename_skills.py

The `scripts/rename_skills.py` utility is designed for large-scale refactoring of skill identifiers. It was primarily used to transition from the `-automation-skill` or `-testing-skill` suffix to the simplified `-skill` suffix across the entire repository [scripts/rename_skills.py:11-51]().

### Implementation Details
The script performs a four-step atomic update to ensure consistency:

1.  **Directory Renaming:** Iterates through the `DIR_RENAMES` mapping and renames the physical folders on disk using `os.rename` [scripts/rename_skills.py:64-70]().
2.  **Registry Update:** Loads `skills_index.json`, updates the `name` and `path` keys for each entry, and replaces strings in the `files` object to point to the new locations [scripts/rename_skills.py:72-84]().
3.  **Frontmatter Sync:** Opens every `SKILL.md` in the new directories and uses `re.sub` to update the `name:` field in the YAML frontmatter to match the new directory name [scripts/rename_skills.py:87-94]().
4.  **Eval File Migration:** Renames the corresponding evaluation JSON files in the `evals/` directory (e.g., `selenium-automation-skill-evals.json` becomes `selenium-skill-evals.json`) [scripts/rename_skills.py:102-109]().

### Renaming Logic Diagram

This diagram shows how `rename_skills.py` bridges the "Old Name" space to the "New Name" space across multiple file types.

**Renaming Execution Logic**
```mermaid
graph LR
    subgraph "Input Mapping"
        MAP["DIR_RENAMES Mapping"]
    end

    subgraph "Code Entity Space: rename_skills.py"
        R_MAIN["main()"]
        R_PATH["replace_path()"]
    end

    subgraph "System Targets"
        DIR["Skill Directories"]
        INDEX["skills_index.json"]
        FRONT["SKILL.md Frontmatter"]
        EVALS["evals/*.json"]
    end

    MAP --> R_MAIN
    R_MAIN -->|os.rename| DIR
    R_MAIN -->|json.dump| INDEX
    R_MAIN -->|re.sub| FRONT
    R_MAIN -->|os.rename| EVALS
    INDEX -.-> R_PATH
```
**Sources:** [scripts/rename_skills.py:11-51](), [scripts/rename_skills.py:60-110]()

---

## Usage in Development Workflow

Before submitting a Pull Request (PR) to the `agent-skills` repository, contributors are expected to run the validation script to catch structural errors.

### Running Validation
Execute the script from the repository root:
```bash
python3 scripts/validate_skills.py
```
The script will output a summary of total skills found, errors (which block PRs), and warnings (which are recommendations for better skill quality) [scripts/validate_skills.py:170-172]().

### Validation Constraints Summary

| Metric | Constraint | Source |
| :--- | :--- | :--- |
| **Max Lines** | 500 lines per `SKILL.md` | [scripts/validate_skills.py:11]() |
| **File Structure** | `SKILL.md` must exist in the root of the skill folder | [scripts/validate_skills.py:71-72]() |
| **Reference Structure** | `reference/playbook.md` is expected | [scripts/validate_skills.py:93-95]() |
| **Registry** | All skills must be registered in `skills_index.json` | [scripts/validate_skills.py:119-124]() |

**Sources:** [scripts/validate_skills.py:1-172](), [scripts/rename_skills.py:1-115]()

---

# Page: Glossary — Key Terms, Jargon, and Abbreviations

# Glossary — Key Terms, Jargon, and Abbreviations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [appium-skill/SKILL.md](appium-skill/SKILL.md)
- [appium-skill/reference/cloud-integration.md](appium-skill/reference/cloud-integration.md)
- [appium-skill/reference/ios-specific.md](appium-skill/reference/ios-specific.md)
- [appium-skill/reference/playbook.md](appium-skill/reference/playbook.md)
- [behave-skill/reference/playbook.md](behave-skill/reference/playbook.md)
- [capybara-skill/SKILL.md](capybara-skill/SKILL.md)
- [capybara-skill/reference/advanced-patterns.md](capybara-skill/reference/advanced-patterns.md)
- [capybara-skill/reference/cloud-integration.md](capybara-skill/reference/cloud-integration.md)
- [capybara-skill/reference/playbook.md](capybara-skill/reference/playbook.md)
- [cicd-pipeline-skill/SKILL.md](cicd-pipeline-skill/SKILL.md)
- [cicd-pipeline-skill/reference/playbook.md](cicd-pipeline-skill/reference/playbook.md)
- [cucumber-skill/SKILL.md](cucumber-skill/SKILL.md)
- [cucumber-skill/reference/playbook.md](cucumber-skill/reference/playbook.md)
- [detox-skill/SKILL.md](detox-skill/SKILL.md)
- [detox-skill/reference/playbook.md](detox-skill/reference/playbook.md)
- [gauge-skill/reference/playbook.md](gauge-skill/reference/playbook.md)
- [hyperexecute-skill/SKILL.md](hyperexecute-skill/SKILL.md)
- [jest-skill/reference/advanced-patterns.md](jest-skill/reference/advanced-patterns.md)
- [jest-skill/reference/playbook.md](jest-skill/reference/playbook.md)
- [junit-5-skill/reference/advanced-patterns.md](junit-5-skill/reference/advanced-patterns.md)
- [junit-5-skill/reference/playbook.md](junit-5-skill/reference/playbook.md)
- [playwright-skill/SKILL.md](playwright-skill/SKILL.md)
- [playwright-skill/reference/cloud-integration.md](playwright-skill/reference/cloud-integration.md)
- [playwright-skill/reference/python-patterns.md](playwright-skill/reference/python-patterns.md)
- [protractor-skill/reference/cloud-integration.md](protractor-skill/reference/cloud-integration.md)
- [rspec-skill/reference/playbook.md](rspec-skill/reference/playbook.md)
- [selenium-skill/reference/page-object-model.md](selenium-skill/reference/page-object-model.md)
- [selenium-skill/reference/playbook.md](selenium-skill/reference/playbook.md)
- [shared/testmu-cloud-reference.md](shared/testmu-cloud-reference.md)
- [skills_index.json](skills_index.json)
- [smartui-skill/SKILL.md](smartui-skill/SKILL.md)
- [smartui-skill/reference/playbook.md](smartui-skill/reference/playbook.md)
- [specflow-skill/SKILL.md](specflow-skill/SKILL.md)
- [specflow-skill/reference/playbook.md](specflow-skill/reference/playbook.md)
- [test-framework-migration-skill/SKILL.md](test-framework-migration-skill/SKILL.md)
- [test-framework-migration-skill/reference/overview.md](test-framework-migration-skill/reference/overview.md)
- [testng-skill/SKILL.md](testng-skill/SKILL.md)
- [testng-skill/reference/advanced-patterns.md](testng-skill/reference/advanced-patterns.md)

</details>



This glossary defines the technical terms, framework-specific jargon, and internal abbreviations used throughout the `agent-skills` repository. It serves as a reference for onboarding engineers to understand the implementation details of the **Agent Skills Standard** and the integration patterns for the **TestMu AI** cloud platform.

## Core System Terms

### Agent Skill
A self-contained directory containing instructions (in `SKILL.md`) and reference implementations that enable an AI coding assistant (like Claude Code or Cursor) to generate production-grade test code for a specific framework.
*   **Implementation**: Each skill is a top-level directory containing a `SKILL.md` file and a `reference/` subdirectory [skills_index.json:16-40]().
*   **Validation**: Skills are validated against schema rules defined in maintenance scripts [scripts/validate_skills.py:1-50]().

### SKILL.md
The entry point for an AI agent. It uses a **Progressive Disclosure** model, providing high-level triggers and core patterns while linking to deeper technical playbooks for complex tasks.
*   **Frontmatter**: Contains metadata like `name`, `description`, `languages`, and `category` [playwright-skill/SKILL.md:1-22]().
*   **Triggers**: Natural language strings that help the AI determine when to activate the skill [appium-skill/SKILL.md:8-10]().

### Skill Registry (`skills_index.json`)
A centralized JSON manifest listing all 46 available skills, their metadata, and file paths. This is the primary index consumed by the Evaluation Framework to map queries to specific skill sets.
*   **File**: [skills_index.json:1-100]().

---

## TestMu AI & Cloud Jargon

### LT:Options
A specific capability block used in Selenium, Playwright, and Appium to configure LambdaTest-specific features such as video recording, network logs, and build naming.
*   **Structure**: A dictionary/object passed within the driver capabilities [playwright-skill/reference/cloud-integration.md:30-39]().
*   **Key Keys**: `platform`, `build`, `name`, `user`, `accessKey`, `video`, `network` [playwright-skill/reference/cloud-integration.md:98-108]().

### lambdatest_action
A mechanism to communicate test status or custom commands from the test script to the TestMu AI cloud during execution using `page.evaluate` or `driver.executeScript`.
*   **Usage**: `page.evaluate((_) => {}, 'lambdatest_action: {"action": "setTestStatus", "arguments": {"status": "passed"}}')` [playwright-skill/reference/cloud-integration.md:55-60]().

### SmartUI
The visual regression testing service that captures screenshots and compares them against baselines using AI-driven diffing.
*   **Command**: `smartuiSnapshot` [smartui-skill/SKILL.md:1-20]().

### HyperExecute
A high-speed test orchestration platform that shards and executes tests in parallel across multiple virtual machines.
*   **Config**: Defined via a YAML file containing `testDiscovery` and `testRunnerCommand` [hyperexecute-skill/SKILL.md:1-30]().

---

## Framework-Specific Jargon

### BDD (Behavior Driven Development)
A testing methodology using Gherkin syntax (`Given/When/Then`) to define application behavior.
*   **Entities**:
    *   **Feature File**: Markdown-like `.feature` files containing Scenarios [cucumber-skill/SKILL.md:24-59]().
    *   **Step Definitions**: Code that maps Gherkin strings to executable functions [cucumber-skill/SKILL.md:61-102]().
    *   **Hooks**: Setup/Teardown logic (e.g., `@Before`, `@After`) [cucumber-skill/SKILL.md:130-148]().

### POM (Page Object Model)
A design pattern that abstracts web pages into classes, separating the UI structure (locators) from the test logic.
*   **Implementation**: Often uses a `BasePage` and framework-specific annotations like `@FindBy` [selenium-skill/reference/page-object-model.md:1-50]().

### Gray-Box Testing
A testing approach where the runner has internal knowledge of the application state (e.g., Detox for React Native), allowing for automatic synchronization between the test and the app's asynchronous operations.
*   **Context**: [detox-skill/SKILL.md:3-8]().

---

## Technical Mapping: Natural Language to Code

The following diagrams bridge the gap between user requirements and the specific code entities defined in the repository.

### Diagram 1: Cloud Integration Flow
This diagram maps the "Natural Language Space" of a user request to the "Code Entity Space" of the TestMu AI integration.

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserReq["'Run my Playwright tests on LambdaTest Windows 11'"]
    end

    subgraph "Code Entity Space"
        CapObj["'LT:Options' Capability Block"]
        WSEndpoint["'wss://cdp.lambdatest.com/playwright'"]
        ActionCmd["'lambdatest_action' for status reporting"]
        
        subgraph "Files"
            LTSetup["lambdatest-setup.ts"]
            PWConfig["playwright.config.ts"]
        end
    end

    UserReq -->|Triggers| LTSetup
    LTSetup -->|Constructs| CapObj
    LTSetup -->|Connects to| WSEndpoint
    LTSetup -->|Injects| ActionCmd
    PWConfig -->|Defines Projects| LTSetup
```
**Sources:** [playwright-skill/reference/cloud-integration.md:75-144](), [playwright-skill/reference/cloud-integration.md:27-40]()

### Diagram 2: BDD Execution Architecture
This diagram shows how BDD-related terms map to specific file types and classes within the `cucumber-skill` and `specflow-skill`.

```mermaid
graph LR
    subgraph "Natural Language Space"
        Gherkin["'Scenario: User Login'"]
        Steps["'Given I am on the login page'"]
    end

    subgraph "Code Entity Space"
        subgraph "Cucumber (Java/JS)"
            FeatureFile["'.feature' file"]
            StepDef["'@Given' Annotation / LoginSteps.java"]
            ScenarioCtx["'ScenarioContext' (State Sharing)"]
        end

        subgraph "SpecFlow (.NET)"
            Binding["'[Binding]' Attribute"]
            Hook["'[BeforeScenario]' Hook"]
        end
    end

    Gherkin --> FeatureFile
    Steps --> StepDef
    Steps --> Binding
    StepDef --> ScenarioCtx
    Binding --> Hook
```
**Sources:** [cucumber-skill/SKILL.md:24-102](), [specflow-skill/SKILL.md:21-135](), [specflow-skill/reference/playbook.md:162-237]()

---

## Abbreviations Table

| Abbreviation | Full Term | Context / Code Pointer |
| :--- | :--- | :--- |
| **POM** | Page Object Model | Used in E2E skills [selenium-skill/reference/page-object-model.md:1-10]() |
| **BDD** | Behavior Driven Development | Used in Cucumber, SpecFlow, Behave [cucumber-skill/SKILL.md:2-7]() |
| **CDP** | Chrome DevTools Protocol | Used for Playwright/Puppeteer cloud connection [playwright-skill/reference/cloud-integration.md:44-46]() |
| **WDA** | WebDriverAgent | iOS automation engine for Appium [appium-skill/reference/ios-specific.md:1-20]() |
| **OIDC** | OpenID Connect | Used for secure CI/CD authentication [cicd-pipeline-skill/reference/playbook.md:1-50]() |
| **APK/IPA** | Android/iOS App Package | Mobile application binaries used in Appium/Detox [appium-skill/SKILL.md:49-54]() |
| **DI** | Dependency Injection | Used for state sharing in BDD (e.g., PicoContainer) [cucumber-skill/reference/playbook.md:225-225]() |

**Sources:** [playwright-skill/reference/cloud-integration.md:44-46](), [appium-skill/SKILL.md:49-54](), [cucumber-skill/reference/playbook.md:225-225](), [selenium-skill/reference/page-object-model.md:1-10]()