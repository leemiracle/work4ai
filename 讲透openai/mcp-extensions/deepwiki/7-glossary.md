<!-- source: DeepWiki mcp.deepwiki.com · repo openai/mcp-extensions · page 7 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json)
- [README.md](README.md)
- [docs/spec.md](docs/spec.md)

</details>



This page provides detailed technical definitions and explanations of key terms and concepts used in the OpenAI MCP Extensions codebase. It targets developers working with the MCP Extensions, detailing how these concepts are implemented, interconnected, and represented in code. It includes references to relevant files and sections in the repository for in-depth study.

---

## MCP (Model Context Protocol)

MCP is a specification and protocol that enables structured communication between chat models and their host environments. It defines schemas and message flows for interacting with threads, messages, and other model context elements.

OpenAI MCP Extensions build on top of the MCP spec by adding capabilities specific to ChatGPT platforms (Work, Desktop, Mobile), enabling richer plugin integrations.

- The MCP core schema types are referenced in the code as `MCP.<Type>`.
- The MCP Extensions are layered on top of MCP via special metadata namespaces `_meta`.

MCP defines the foundational messaging and data structures that MCP Extensions augment with richer UI and integration capabilities.

Sources: `docs/spec.md:1-131`()

---

## MCP Apps

MCP Apps are applications built on top of MCP to provide integrated user experiences inside ChatGPT. They are the extension containers for toolsets, UI, and interaction flows.

- MCP Apps can be started or invoked via entrypoints such as global entrypoint in the sidebar, thread tabs, or as file viewers.
- MCP Apps use MCP messages and the extensions protocol to render UI and return data.
- MCP Apps manifest tool metadata, entrypoints, and settings via `_meta` namespaces inside their `tools/list` API response.

Examples:
- "Bits & Bolts" plugin is an example MCP App demonstrating CAD parts management.
- MCP Apps declare sidebar visibility, icons, and titles in tool metadata for proper UI rendering.

The MCP Apps spec is codified in sections such as MCP app entrypoints, UI extensions, and resource handling.

Sources: `docs/spec.md:34-131` `plugins/bits-and-bolts/src/server/register.ts:1-40`()

---

## Entrypoints

Entrypoints are static ways to launch MCP Apps independent of a model conversation, allowing direct access to an app's UI.

There are three major types:

1. **Global Entrypoint**  
   - Available in the primary sidebar navigation, opens the app in a full UI.  
   - Registered in `_meta["openai/ui"]["entrypoints"]` with `"type": "global"`.  
   - Example tool definition includes a tool entrypoint array with global type.

2. **Thread Entrypoint**  
   - A tab within a conversation thread allowing contextual app views.  
   - Also listed under `_meta["openai/ui"]["entrypoints"]` with `"type": "thread"`.

3. **File Entrypoint**  
   - Hooks to render custom viewers for specific file extensions within threads.  
   - Registered similarly with `"type": "file"` and file extensions to handle.

Entrypoint-specific metadata defines icons, titles, and behavior as detailed in the spec.

```mermaid
flowchart TB
  "ToolListEntry[_meta['openai/ui']['entrypoints']]" -->|has| "GlobalEntryPoint[{'type':'global'}]"
  "ToolListEntry[_meta['openai/ui']['entrypoints']]" -->|has| "ThreadEntryPoint[{'type':'thread'}]"
  "ToolListEntry[_meta['openai/ui']['entrypoints']]" -->|has| "FileEntryPoint[{'type':'file','file_extensions':[]}]"
```

This design allows MCP servers to expose multiple UIs for an app in different contexts.

Sources: `docs/spec.md:34-131` `typescript/src/shared/file-entrypoint.ts:1-50`()

---

## _meta Namespaces

The `_meta` field is a crucial part of the MCP Extensions metadata system. It encapsulates extension-specific information that can be embedded inside the standard MCP schema data.

- Data inside `_meta` is hierarchical, allowing nested namespaces.
- OpenAI-specific extensions reside in namespaces such as `_meta["openai/ui"]` and `_meta["openai/form"]`.
- UI entrypoints, visibility, icons, resource URIs, and tool properties are all represented here.
- This field is deeply used when servers return tool metadata in the `tools/list` API or when emitting UI updates.

For example, MCP Apps define their entrypoints and icons inside `_meta["openai/ui"]["entrypoints"]` as arrays of entrypoint objects.

```json
{
  "_meta": {
    "openai": {
      "ui": {
        "entrypoints": [
          { "type": "global" },
          { "type": "thread" }
        ]
      }
    }
  }
}
```

This meta-data based extension allows for backward compatibility and incremental feature addition without breaking MCP core schemas.

Sources: `docs/spec.md:40-130` `typescript/src/shared/file-entrypoint.ts:25-60`()

---

## Elicitation (OpenAI Form Elicitation Protocol)

Elicitation defines an interface for rich form input from users inside ChatGPT, allowing for schema-driven data collection, resource pickers, thumbnail selects, and suggested values.

- Defined in the extension namespace `_meta["openai/form"]`.
- Elicitation forms support complex user interactions including pickers for resources (like parts in Bits & Bolts).
- The schema is JSON Schema-based, allowing validations and structured data flow.
- Extensions can specify input types, thumbnails, suggestions, etc.

The form elicitation protocol is implemented in the Python SDK (`openai_mcp_form_protocol`) and in TypeScript under `typescript/src/server/forms`.

```mermaid
flowchart TD
  "UserInput" --> "ElicitationForm[_meta['openai/form']]"
  "ElicitationForm" --> "FormSchema[JSONSchema]"
  "ElicitationForm" --> "ResourcePicker[Thumbnails, suggestedValues]"
  "FormSubmission" --> "MCPServer[Processes data]"
```

This protocol enables plugin developers to prompt users for structured inputs, improving UX.

Sources: `docs/spec.md:27-34` `python/openai_mcp_extensions/form/_elicitation.py:1-80` `typescript/src/server/forms/index.ts:1-90`()

---

## Keycap Legends

Keycap legends refer to the small SVG icons and mesh JSON files representing keyboard key images used for UI hinting and visual clarity.

- Stored under the `plugins/bits-and-bolts/assets/keycap-legends/` directory.
- Include SVGs and 3D mesh JSON files.
- Scripts such as `prepare-legends.py` automate building keycap legend assets.
- These legends are used inside the Bits & Bolts example plugin to illustrate shortcut keys and UI hints.

Keycap legends support consistent UI iconography across different parts of the MCP Extension Apps.

Sources: `plugins/bits-and-bolts/assets/keycap-legends/` `plugins/bits-and-bolts/scripts/prepare-legends.py:1-50`()

---

## release-please Components

`release-please` is the tool used to automate GitHub releases and versioning for this repository.

- The release automation flows are defined in `.github/workflows/release.yml`.
- The repo contains `release-please` configs and manifests specifying components for npm and PyPI publishing.
- The `rehearse_releases.mjs` dry-run harness is used to verify release processes.
- The automation supports multi-language publishing (TypeScript `@openai/mcp-extensions`, Python `openai-mcp-extensions`) with trusted publishes.

The release process integrates with CI pipelines (`ci.yml`, `checks.yml`) and validation scripts (`check_packages.py`).

Sources: `ci/release.yml` `scripts/rehearse_releases.mjs` `python/check_packages.py:1-65` `typescript/release-please-config.json`()

---

## Marketplace Policies

Marketplace policies govern plugin availability, installation, authentication, and categorization within the MCP/ChatGPT marketplace environment.

- Defined in `.agents/plugins/marketplace.json`.
- Policies include flags such as `"installation": "AVAILABLE"` and `"authentication": "ON_INSTALL"`.
- Each plugin is assigned a `category` like `"Developer Tools"`.
- Marketplace manifests specify plugin source, e.g., local paths for development.
- The marketplace manifest drives packaging and publishing via agent packaging scripts in `package_marketplace.py`.

```json
{
  "name": "mcp-extensions-early-access",
  "plugins": [
    {
      "name": "bits-and-bolts",
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

Policies regulate how plugins are surfaced and managed in the ecosystem.

Sources: `.agents/plugins/marketplace.json:1-20` `python/package_marketplace.py:1-120`()

---

# Diagrams Connecting Natural Language Concepts to Code Entities

### Diagram 1: MCP Extensions Core Concepts to Code Entities

```mermaid
flowchart LR
  "MCP Protocol" -->|"Extended by"| "MCP Extensions (docs/spec.md)"
  "MCP Extensions" --> "MCP Apps"
  "MCP Apps" --> "Entrypoints (_meta['openai/ui']['entrypoints'])"
  "MCP Apps" --> "Elicitation Forms (_meta['openai/form'])"
  "MCP Apps" --> "Keycap Legends (plugins/bits-and-bolts/assets/keycap-legends)"
  "Entrypoints" --> "Global / Thread / File entrypoints (docs/spec.md:34-131)"
  "Elicitation Forms" --> "Server-side form handlers (typescript/src/server/forms)"
  "Elicitation Forms" --> "Python Form Protocol (python/openai_mcp_form_protocol)"
  "Keycap Legends" --> "Legend build script (plugins/bits-and-bolts/scripts/prepare-legends.py)"
```

---

### Diagram 2: MCP Extensions Marketplace and Release Pipeline

```mermaid
flowchart TB
  "Marketplace Manifest (.agents/plugins/marketplace.json)" --> "Plugin Policy & Metadata"
  "Plugin Policy & Metadata" --> "Marketplace Packaging (python/package_marketplace.py)"
  "Marketplace Packaging" --> "Plugin ZIP Artifacts"
  "CI Workflows (ci/ci.yml, checks.yml)" --> "Package Validation (check_packages.py)"
  "Release Automation (ci/release.yml)" --> "release-please (rehearse_releases.mjs)"
  "release-please" --> "Multi-language Publish (npm, PyPI)"
```

---

# Summary Table of Key Concepts and Locations

| Term                | Description                                               | Example Locations                                           |
|---------------------|-----------------------------------------------------------|------------------------------------------------------------|
| MCP                 | Base Model Context Protocol                                | `docs/spec.md:1-20`                                         |
| MCP Apps            | Applications built on MCP with extensions                 | `docs/spec.md:34-131`, `plugins/bits-and-bolts/src/server/register.ts` |
| Entrypoints         | Static app launch points (global/thread/file)             | `docs/spec.md:34-131`, `typescript/src/shared/file-entrypoint.ts` |
| _meta namespaces    | Metadata system for extensions data                        | `docs/spec.md:40-130`, `typescript/src/shared/file-entrypoint.ts` |
| Elicitation         | OpenAI form protocol for structured user input             | `python/openai_mcp_form_protocol/`, `typescript/src/server/forms` |
| Keycap Legends      | SVG and 3D mesh icons for UI key hints                     | `plugins/bits-and-bolts/assets/keycap-legends`, `scripts/prepare-legends.py` |
| release-please      | GitHub release automation tool                             | `ci/release.yml`, `scripts/rehearse_releases.mjs`           |
| Marketplace Policies| Plugin availability, auth, and categories                  | `.agents/plugins/marketplace.json`, `python/package_marketplace.py` |

---

# Conclusion

This glossary outlines the core networking and organizational concepts in the OpenAI MCP Extensions ecosystem, bridging conceptual understanding to concrete code artifacts. The precise metadata-driven design, extensible form elicitation, and structured release and marketplace policies are key to developing robust MCP Extensions and plugins.

---

Sources:  
- `docs/spec.md:1-131`  
- `typescript/src/shared/file-entrypoint.ts:1-65`  
- `plugins/bits-and-bolts/assets/keycap-legends/`  
- `plugins/bits-and-bolts/scripts/prepare-legends.py:1-50`  
- `.agents/plugins/marketplace.json:1-20`  
- `python/package_marketplace.py:1-120`  
- `python/openai_mcp_form_protocol/`  
- `typescript/src/server/forms/index.ts:1-90`  
- `ci/release.yml`  
- `scripts/rehearse_releases.mjs`  
- `python/check_packages.py:1-65`