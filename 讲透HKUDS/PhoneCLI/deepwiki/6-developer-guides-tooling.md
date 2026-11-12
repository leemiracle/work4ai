<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/PhoneCLI · page 6 Developer Guides & Tooling · fetched 2026-11-09 -->

# Developer Guides & Tooling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)

</details>



This page provides a high-level overview of the auxiliary documentation, scripts, and assets that support the development and extension of the PhoneCLI codebase. It serves as a parent page, linking to more detailed child pages for specific topics. The goal is to equip developers with the knowledge to understand the project's structure, extend its capabilities, and utilize various development tools effectively.

## Extending the Harness

The PhoneCLI harness is designed to be extensible, allowing developers to integrate new mobile applications, define new tasks, and build corresponding app maps. This section introduces the core concepts and resources for expanding the system's coverage. For detailed instructions on how to add new apps, tasks, and app maps, including the use of templates and app data assets, refer to the dedicated child page.

For details, see [Extending the Harness (docs/)](#6.1).

Sources:
- [docs/modify_androidlab.md]()
- [docs/new_apps.md]()
- [templates/]()
- [app_data/]()

## Test Scripts and Utilities

The codebase includes various scripts and utilities to aid in testing, debugging, and general development workflows. This section provides an overview of the batch execution scripts, helper tools, logging conventions, and `.gitignore` practices. Understanding these resources is crucial for efficient development and maintenance.

For details, see [Test Scripts and Utilities](#6.2).

### Logging Layout

The system generates various log files during execution. These logs are typically organized under the `logs/` directory, providing a structured way to review execution traces, errors, and other diagnostic information.

Sources:
- [logs/]()

### .gitignore Conventions

The `.gitignore` file [/.gitignore:1-6]() specifies patterns for files and directories that should be ignored by Git. This includes common operating system files like `.DS_Store` [/.gitignore:2-2]() and Python-specific artifacts such as `__pycache__/` [/.gitignore:5-5]() and compiled bytecode files (`*.py[cod]`) [/.gitignore:6-6](). Adhering to these conventions helps maintain a clean repository and prevents unnecessary files from being committed.

Sources:
- [/.gitignore:1-6]()

---

