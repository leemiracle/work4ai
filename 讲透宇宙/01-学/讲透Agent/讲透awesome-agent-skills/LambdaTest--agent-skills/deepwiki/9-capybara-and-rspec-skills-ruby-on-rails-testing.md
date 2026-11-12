<!-- source: DeepWiki mcp.deepwiki.com · repo LambdaTest/agent-skills · page 9 Capybara and RSpec Skills — Ruby on Rails Testing · fetched 2026-10-26 -->

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

