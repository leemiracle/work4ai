<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/community · page 4 Contributing · fetched 2026-11-02 -->

# Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING_zh.md](CONTRIBUTING_zh.md)
- [COPYRIGHT](COPYRIGHT)
- [COPYRIGHT_zh](COPYRIGHT_zh)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [README_CN.md](README_CN.md)
- [contribute/README.md](contribute/README.md)
- [contribute/style-guide/openJiuwen-JavaScript-coding-style-guide.md](contribute/style-guide/openJiuwen-JavaScript-coding-style-guide.md)

</details>



## Purpose and Scope

This page provides a high-level overview of the contribution process for the openJiuwen AI Agent platform ecosystem. Participating in the openJiuwen community requires adhering to specific legal, procedural, and technical standards to ensure high code quality, compliance, and stable multi-agent operations. Developers can contribute code, documentation, and issues by following established workflows.

For detailed instructions, refer to the child pages:
- Contribution Workflow & Commit Conventions: [Contribution Workflow & Commit Conventions](#4.1)
- CLA Signing Requirements: [CLA Signing](#4.2)
- Licensing & Copyright Policy: [Licensing & Copyright Policy](#4.3)

Sources: [README.md:1-14](), [README_CN.md:1-14]()

---

## 4.1 Contribution Workflow & Commit Conventions

The openJiuwen code contribution workflow is built on GitCode (or compatible Git platforms) and requires a structured path from forking repositories to passing Continuous Integration (CI) gates. Developers must work within dedicated feature branches, format commit messages according to the [Conventional Commits](https://www.conventionalcommits.org/) specification, and ensure cryptographic sign-off (`-sm`) [CONTRIBUTING_zh.md:100-106]. Pull Requests (PRs) must be linked to a community issue using the `#+Issue ID` syntax and pass all static analysis, compilation, and functional test pipelines before merge consideration [CONTRIBUTING_zh.md:137-156].

For detailed information on the fork/clone/rebase cycle, commit message requirements, sign-off procedures, issue linking syntax, community bot commands, and merge rules, see [Contribution Workflow & Commit Conventions](#4.1).

### Git & Pull Request Lifecycle

```mermaid
graph TD
    A["RemoteMainRepo"] -->| "git clone" | B["LocalWorkingDirectory"]
    B -->| "git branch myfeature" | C["LocalFeatureBranch"]
    C -->| "git commit -sm" | D["ConventionalCommit"]
    D -->| "git push -f origin" | E["ForkRepository"]
    E -->| "Create PR & Link #Issue" | F["PullRequestValidation"]
    F -->| "CI Gates Pass" | G["MergeToMain"]
```
Sources: [CONTRIBUTING_zh.md:38-156]()

---

## 4.2 CLA Signing

Before contributing code, documentation, or other assets to any openJiuwen repository, contributors must execute the community Contributor License Agreement (CLA). The CLA establishes the legal framework for intellectual property contributions, protecting both individual developers and enterprise stakeholders. The openJiuwen community provides separate tracks and documentation for individual and corporate contributors across multiple language versions within the `cla/` directory [README_CN.md:112-118].

For step-by-step signing instructions, guidance on handling corporate vs. individual agreements, and troubleshooting common CLA check failures, see [CLA Signing](#4.2).

### Contribution Compliance & Validation Pipeline

```mermaid
graph LR
    A["Contributor"] -->| "Sign CLA" | B["OSInfraCLASign"]
    B -->| "Commit Code" | C["ConventionalCommits"]
    C -->| "Open PR" | D["CIStaticCheck"]
    D -->| "Review Gate" | E["MaintainerApproval"]
    E -->| "Merge" | F["AgentPlatformBuild"]
```
Sources: [README_CN.md:112-118](), [CONTRIBUTING_zh.md:100-156]()

---

## 4.3 Licensing & Copyright Policy

All contributions made to openJiuwen are governed by the Apache License 2.0 (`Apache-2.0`) and accompanying copyright notices [CONTRIBUTING_zh.md:7-15]. Contributors must ensure all submitted content is original and non-infringing [CONTRIBUTING_zh.md:11-13]. When introducing third-party open-source libraries, code snippets, or dependencies, developers must follow strict review workflows and third-party notice requirements outlined in the governance guidelines [CONTRIBUTING_zh.md:13-15].

For complete details on license selection, copyright header requirements, third-party code review workflows, and compliance file structures (`LICENSE`, `COPYRIGHT`), see [Licensing & Copyright Policy](#4.3).

Sources: [CONTRIBUTING_zh.md:7-15](), [LICENSE:1-10](), [COPYRIGHT:1-1]()

---

