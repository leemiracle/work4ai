<!-- source: DeepWiki mcp.deepwiki.com · repo coderabbitai/skills · page 5 Repository Operations · fetched 2026-10-26 -->

# Repository Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.coderabbit.yaml](.coderabbit.yaml)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/workflows/required-approver.yml](.github/workflows/required-approver.yml)

</details>



This page provides a high-level overview of repository operations, continuous integration, review policies, governance workflows, contribution guidelines, and evaluation tooling for `coderabbitai/skills`. 

Repository operations ensure that portable agent skills, manifests, and subagents remain secure, compliant, and behaviorally consistent across all host environments. For deep technical details, refer to the child pages linked throughout this document.

---

## 5.1 CodeRabbit Review Policy (.coderabbit.yaml)

The repository enforces a strict, versioned review policy via `[.coderabbit.yaml:1-127]`. This policy uses an `assertive` review profile (`[.coderabbit.yaml:6-7]()`) combined with custom pre-merge checks (`[.coderabbit.yaml:13-38]()`) to guarantee that all changes to skills, agent guidance, and manifests remain accurate, portable, and aligned with upstream specifications.

Key aspects of the review policy include:
- **Pre-Merge Validation**: Enforces strict checks on PR titles, descriptions, issue assessments, and an "Agent guidance structure" custom check (`[.coderabbit.yaml:13-38]()`).
- **Tool Integration**: Automatically enables `actionlint`, `zizmor`, and `skillspector` (`[.coderabbit.yaml:57-64]()`).
- **Path-Specific Instructions**: Implements granular constraints for `skills/**/SKILL.md`, `commands/**`, `agents/**/*.md`, and plugin manifests (`[.coderabbit.yaml:65-99]()`).

```mermaid
graph TD
    PR[PullRequestEvent] --> CR[.coderabbit.yaml]
    CR --> PMC[PreMergeChecks]
    PMC --> AGS["Agent guidance structure (custom_checks)"]
    PMC --> TLS[Tools: actionlint, zizmor, skillspector]
    CR --> PI[Path Instructions]
    PI --> SML["skills/SKILL.md"]
    PI --> CMD["commands/"]
    PI --> AGT["agents/"]
    PI --> MFT["Plugin Manifests"]

    subgraph "Code Entity Space"
        CR
        PMC
        AGS
        TLS
        PI
        SML
        CMD
        AGT
        MFT
    end

    Sources: [.coderabbit.yaml:1-99]
```

For full details on assertions, tooling configuration, and custom check instructions, see [CodeRabbit Review Policy (.coderabbit.yaml)](#5.1).

*Sources: [.coderabbit.yaml:1-99]*

---

## 5.2 GitHub Workflows & Governance

Governance and security gates are enforced via GitHub Actions workflows and repository configuration files. The `required-approver.yml` workflow acts as a security gate on pull requests, ensuring that designated repository owners approve changes before merging.

Key components include:
- **Approver Gate Logic**: Evaluates pull request reviews via the GitHub GraphQL API to verify that an approval from authorized maintainers (`nehal-a2z` or `juanpflores`) is present on the latest head commit (`[.github/workflows/required-approver.yml:21-92]()`).
- **Code Ownership**: Defines repository ownership boundaries and review requirements (`[.github/CODEOWNERS:1]()`).
- **Release Automation**: Manages archives, checksums, and release manifests.

```mermaid
graph TD
    GH[GitHubWebhook] --> RA["required-approver.yml (verify job)"]
    RA --> API["gh api graphql"]
    API --> PR[PullRequest Object]
    PR --> RV[Reviews Collection]
    RV --> CHK{Approved by nehal-a2z or juanpflores?}
    CHK -->|Yes| PASS[Pass Workflow]
    CHK -->|No| FAIL[Fail with ::error::]

    subgraph "Code Entity Space"
        RA
        API
        PR
        RV
        CHK
    end

    Sources: [.github/workflows/required-approver.yml:21-93], [.github/CODEOWNERS:1-2]
```

For details on workflow triggers, API query structures, and release pipelines, see [GitHub Workflows & Governance](#5.2).

*Sources: [.github/workflows/required-approver.yml:1-93], [.github/CODEOWNERS:1-2]*

---

## 5.3 Contributing, Templates & Licensing

To maintain high code quality and smooth collaboration, the repository supplies standardized templates and licensing guidelines. These files ensure that all contributions follow uniform structures and adhere to open-source licensing constraints.

Refer to the child page for details regarding:
- **Contributing Guidelines**: Instructions on submitting issues, running tests, and preparing pull requests (`CONTRIBUTING.md`).
- **Issue & PR Templates**: Structured forms for bug reports, feature requests, and pull request metadata.
- **Licensing**: Terms governed by the MIT License.

For details, see [Contributing, Templates & Licensing](#5.3).

---

## 5.4 Evaluations (evals/)

The `evals/` directory houses an offline evaluation harness tailored for testing agent skills and plugin behavior (such as Claude Code integrations). It validates plugin responses against expected outcomes using modular grading mechanisms.

Key characteristics of the evaluation harness:
- **Case Schema**: Declarative `case.yaml` files defining input prompts, execution context, and expected behaviors.
- **Graders**: Automated evaluation arms including regex matching, LLM-based assertions, and tool usage verification.
- **CLI Parity**: Canonical test cases designed to verify consistency across multiple agent host runtimes.

For information on running evaluations, interpreting results, and writing custom test cases, see [Evaluations (evals/)](#5.4).

---

