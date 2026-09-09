> 来源: [https://deepwiki.com/modelcontextprotocol/servers](https://deepwiki.com/modelcontextprotocol/servers)
> DeepWiki modelcontextprotocol/servers

# Introduction to Model Context Protocol Servers

  Relevant source files 
 - [.github/pull_request_template.md](https://github.com/modelcontextprotocol/servers/blob/599dafc1/.github/pull_request_template.md?plain=1)
 - [CONTRIBUTING.md](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1)
 - [README.md](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1)
 - [SECURITY.md](https://github.com/modelcontextprotocol/servers/blob/599dafc1/SECURITY.md?plain=1)
 - [package-lock.json](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package-lock.json)
 - [package.json](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package.json)
 - [src/everything/package.json](https://github.com/modelcontextprotocol/servers/blob/599dafc1/src/everything/package.json)
 - [src/filesystem/package.json](https://github.com/modelcontextprotocol/servers/blob/599dafc1/src/filesystem/package.json)
 - [src/memory/package.json](https://github.com/modelcontextprotocol/servers/blob/599dafc1/src/memory/package.json)
 - [src/sequentialthinking/package.json](https://github.com/modelcontextprotocol/servers/blob/599dafc1/src/sequentialthinking/package.json)
 
  
## Purpose and Scope

 This document provides an overview of the `modelcontextprotocol/servers` repository, which serves as a collection of **reference implementations** for the Model Context Protocol (MCP). This page introduces the repository's purpose, explains the distinction between reference servers and production servers, and contextualizes how these implementations fit into the broader MCP ecosystem.

 For detailed information about the MCP protocol architecture and primitives, see [MCP Protocol and Architecture](https://deepwiki.com/modelcontextprotocol/servers/1.1-mcp-protocol-and-architecture). For specifics on individual reference servers, see [Reference Servers Overview](https://deepwiki.com/modelcontextprotocol/servers/2-reference-servers-overview). For guidance on contributing to this repository, see [Development and Contribution](https://deepwiki.com/modelcontextprotocol/servers/3-development-and-contribution).

 
## Repository Overview

 The `modelcontextprotocol/servers` repository maintains a small, curated set of reference server implementations that demonstrate MCP features and SDK usage patterns. These servers are **educational examples** designed to help developers understand how to build their own MCP servers, not production-ready solutions meant for direct deployment [README.md8-11](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L8-L11) [SECURITY.md7-9](https://github.com/modelcontextprotocol/servers/blob/599dafc1/SECURITY.md?plain=1#L7-L9)

 
### Code Entity to System Mapping

 The following diagram maps high-level repository concepts to specific code entities and file structures.

 
```

```

 Sources: [README.md25-36](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L25-L36) [package.json11-13](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package.json#L11-L13) [package-lock.json11-19](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package-lock.json#L11-L19)

 **Repository Contents Summary**

 
| Component | Location | Purpose |
|---|---|---|
| Active TypeScript Servers | src/everything/, src/filesystem/, src/memory/, src/sequentialthinking/ | Reference implementations using TypeScript SDK package.json22-25 |
| Active Python Servers | src/git/, src/fetch/, src/time/ | Reference implementations using Python SDK README.md30-35 |
| Documentation | README.md, CONTRIBUTING.md, SECURITY.md | Repository documentation and policies |
| Development Infrastructure | package.json, .github/ | CI/CD and monorepo workspace configuration package.json15-20 |

 
## Reference Implementations vs Production Servers

 A critical distinction exists between the **reference servers** maintained in this repository and **production servers** that should be published to the [MCP Server Registry](https://registry.modelcontextprotocol.io/).

 
### Reference Server Characteristics

 Reference servers in this repository are:

 
 - **Educational tools** that demonstrate MCP SDK usage patterns [README.md9-11](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L9-L11) [SECURITY.md7-9](https://github.com/modelcontextprotocol/servers/blob/599dafc1/SECURITY.md?plain=1#L7-L9)
 - **Protocol showcases** illustrating how to implement Tools, Resources, Prompts, and Roots [CONTRIBUTING.md15-18](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1#L15-L18)
 - **Simplified implementations** meant to inspire the community rather than provide highly opinionated features [CONTRIBUTING.md20-22](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1#L20-L22)
 - **Maintained by the MCP steering group** as part of the official MCP project [README.md6-7](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L6-L7)
 
 
### Contribution Policy

 The repository has a selective contribution policy that reinforces its role as a reference collection:

 **Accepted Contributions:**

 
 - **Bug fixes**: Resolving issues in existing reference servers [CONTRIBUTING.md16](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1#L16-L16)
 - **Usability improvements**: Enhancing ergonomics for humans and agents [CONTRIBUTING.md17](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1#L17-L17)
 - **Feature demonstrations**: Enhancements that illustrate protocol features like Resources, Prompts, or Roots [CONTRIBUTING.md18](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1#L18-L18)
 
 **Rejected Contributions:**

 
 - **New server implementations**: These should be published to the Registry instead [CONTRIBUTING.md23-24](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1#L23-L24) [.github/pull_request_template.md7-9](https://github.com/modelcontextprotocol/servers/blob/599dafc1/.github/pull_request_template.md?plain=1#L7-L9)
 - **Server listings in README**: The README no longer lists third-party servers [CONTRIBUTING.md8-11](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1#L8-L11)
 
 Sources: [CONTRIBUTING.md1-24](https://github.com/modelcontextprotocol/servers/blob/599dafc1/CONTRIBUTING.md?plain=1#L1-L24) [.github/pull_request_template.md1-44](https://github.com/modelcontextprotocol/servers/blob/599dafc1/.github/pull_request_template.md?plain=1#L1-L44)

 
## The MCP Ecosystem

 The reference servers exist within a broader ecosystem of MCP components, including SDKs, clients, and the Registry.

 
### Ecosystem Integration

 The following diagram illustrates how the code entities in this repository interact with the broader protocol ecosystem via standard transports.

 
```

```

 Sources: [README.md80-132](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L80-L132) [src/everything/package.json25-27](https://github.com/modelcontextprotocol/servers/blob/599dafc1/src/everything/package.json#L25-L27) [src/everything/package.json15-17](https://github.com/modelcontextprotocol/servers/blob/599dafc1/src/everything/package.json#L15-L17)

 
### SDK Support

 The repository demonstrates usage of the official TypeScript and Python SDKs, but MCP supports a wide range of programming languages [README.md12-23](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L12-L23):

 
| Language | SDK Reference / Dependency |
|---|---|
| TypeScript | @modelcontextprotocol/sdk src/everything/package.json33 |
| Python | python-mcp-sdk README.md19 |
| Others | C#, Go, Java, Kotlin, PHP, Ruby, Rust, Swift README.md14-22 |

 
### Reference Servers as Educational Resources

 The active reference servers serve specific educational purposes:

 **Educational/Protocol Demonstration Servers:**

 
 - **Everything** (`src/everything/`) - Comprehensive demonstration of all MCP protocol features including stdio, SSE, and streamableHttp transports [README.md29](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L29-L29) [src/everything/package.json4](https://github.com/modelcontextprotocol/servers/blob/599dafc1/src/everything/package.json#L4-L4)
 - **Sequential Thinking** (`src/sequentialthinking/`) - Demonstrates dynamic problem-solving through thought sequences [README.md34](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L34-L34)
 
 **Practical Utility Servers:**

 
 - **Filesystem** (`src/filesystem/`) - Secure file operations with configurable access controls [README.md31](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L31-L31)
 - **Git** (`src/git/`) - Tools to read, search, and manipulate Git repositories [README.md32](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L32-L32)
 - **Fetch** (`src/fetch/`) - Web content fetching and conversion for LLM usage [README.md30](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L30-L30)
 - **Memory** (`src/memory/`) - Knowledge graph-based persistent memory system [README.md33](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L33-L33)
 - **Time** (`src/time/`) - Time and timezone conversion capabilities [README.md35](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L35-L35)
 
 Sources: [README.md29-35](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L29-L35) [src/everything/package.json4](https://github.com/modelcontextprotocol/servers/blob/599dafc1/src/everything/package.json#L4-L4)

 
### Archived Servers

 Previously maintained reference servers (e.g., Brave Search, GitHub, Slack, SQLite) have been moved to the [`servers-archived`](https://github.com/modelcontextprotocol/servers-archived) repository. These are no longer actively maintained here as many have been replaced by official or community-maintained versions [README.md37-53](https://github.com/modelcontextprotocol/servers/blob/599dafc1/README.md?plain=1#L37-L53)

 
## Repository Structure and Organization

 The repository is managed as a monorepo using npm workspaces for TypeScript projects.

 
### TypeScript Monorepo Structure

 The root `package.json` defines the `workspaces` that include all sub-projects in `src/*` [package.json11-13](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package.json#L11-L13)

 
 - **Build Orchestration**: Root scripts allow building all workspaces simultaneously using `npm run build --workspaces` [package.json16](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package.json#L16-L16)
 - **Dependency Management**: Shared overrides for packages like `hono` and `qs` are managed at the root to ensure consistency across reference servers [package.json27-30](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package.json#L27-L30)
 
 Sources: [package.json1-31](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package.json#L1-L31) [package-lock.json7-20](https://github.com/modelcontextprotocol/servers/blob/599dafc1/package-lock.json#L7-L20)

 For detailed information on the build systems and development workflows, see [Repository Structure and Package Management](https://deepwiki.com/modelcontextprotocol/servers/1.2-repository-structure-and-package-management).

 
## Next Steps

 This introduction provides context for understanding the reference servers. To dive deeper:

 
 - **Understand MCP fundamentals**: See [MCP Protocol and Architecture](https://deepwiki.com/modelcontextprotocol/servers/1.1-mcp-protocol-and-architecture)
 - **Explore repository organization**: See [Repository Structure and Package Management](https://deepwiki.com/modelcontextprotocol/servers/1.2-repository-structure-and-package-management)
 - **Learn about specific servers**: See [Reference Servers Overview](https://deepwiki.com/modelcontextprotocol/servers/2-reference-servers-overview)
 - **Contribute to the repository**: See [Contribution Guidelines and Review Process](https://deepwiki.com/modelcontextprotocol/servers/3.1-contribution-guidelines-and-review-process)
