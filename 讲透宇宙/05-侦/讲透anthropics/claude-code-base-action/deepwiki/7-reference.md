<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-code-base-action · page 7 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bun.lock](bun.lock)
- [package.json](package.json)
- [src/validate-env.ts](src/validate-env.ts)
- [test/validate-env.test.ts](test/validate-env.test.ts)

</details>



This page provides technical reference documentation for environment variables, configuration files, and project structure used by the Claude Code Base Action. For getting started information, see [Getting Started](#2), and for detailed configuration guidance, see [Action Configuration](#3).

## Environment Variables Reference

The action uses environment variables for authentication, configuration, and runtime behavior control. The `validateEnvironmentVariables` function validates these based on the selected provider.

### Provider Control Variables

| Variable | Type | Description | Validation |
|----------|------|-------------|------------|
| `CLAUDE_CODE_USE_BEDROCK` | Flag | Set to `"1"` to enable AWS Bedrock | Mutually exclusive with Vertex AI |
| `CLAUDE_CODE_USE_VERTEX` | Flag | Set to `"1"` to enable Google Vertex AI | Mutually exclusive with Bedrock |

### Direct Anthropic API Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `ANTHROPIC_API_KEY` | String | Anthropic API key | When using direct API without OAuth |
| `CLAUDE_CODE_OAUTH_TOKEN` | String | Claude Code OAuth token | Alternative to API key |

### AWS Bedrock Variables

| Variable | Type | Description | Required | Default Behavior |
|----------|------|-------------|----------|------------------|
| `AWS_REGION` | String | AWS region for Bedrock service | Yes | Used to construct base URL |
| `AWS_ACCESS_KEY_ID` | String | AWS access key | Yes | - |
| `AWS_SECRET_ACCESS_KEY` | String | AWS secret access key | Yes | - |
| `AWS_SESSION_TOKEN` | String | AWS session token | No | For temporary credentials |
| `ANTHROPIC_BEDROCK_BASE_URL` | String | Custom Bedrock endpoint | No | Defaults to `https://bedrock-runtime.{region}.amazonaws.com` |

### Google Vertex AI Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `ANTHROPIC_VERTEX_PROJECT_ID` | String | GCP project ID | Yes |
| `CLOUD_ML_REGION` | String | GCP Cloud ML region | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | String | Path to GCP service account JSON | No |
| `ANTHROPIC_VERTEX_BASE_URL` | String | Custom Vertex AI endpoint | No |

### Environment Validation Logic

The `validateEnvironmentVariables` function implements these rules:

```mermaid
graph TD
    start[validateEnvironmentVariables] --> checkMutex["Check CLAUDE_CODE_USE_BEDROCK && CLAUDE_CODE_USE_VERTEX"]
    checkMutex -->|Both set| error1["Error: Cannot use both providers"]
    checkMutex -->|Valid| checkProvider{Provider Type}
    
    checkProvider -->|Neither| directAPI["Direct API"]
    checkProvider -->|Bedrock| bedrockValidation["Bedrock Validation"]
    checkProvider -->|Vertex| vertexValidation["Vertex Validation"]
    
    directAPI --> checkAuth{"ANTHROPIC_API_KEY || CLAUDE_CODE_OAUTH_TOKEN"}
    checkAuth -->|Missing| error2["Error: API key or OAuth token required"]
    checkAuth -->|Present| success[Valid]
    
    bedrockValidation --> checkAWS["Check AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"]
    checkAWS -->|Missing| error3["Error: Missing AWS variables"]
    checkAWS -->|Present| success
    
    vertexValidation --> checkGCP["Check ANTHROPIC_VERTEX_PROJECT_ID, CLOUD_ML_REGION"]
    checkGCP -->|Missing| error4["Error: Missing GCP variables"]
    checkGCP -->|Present| success
    
    error1 --> throw[Throw validation error]
    error2 --> throw
    error3 --> throw
    error4 --> throw
```

Sources: [src/validate-env.ts:5-54](), [test/validate-env.test.ts:6-214]()

## Project Configuration Reference

### Package Configuration

The project uses Bun as the primary runtime and package manager:

| File | Description | Key Properties |
|------|-------------|----------------|
| `package.json` | Project metadata and dependencies | Runtime: Bun, TypeScript support |
| `bun.lock` | Dependency lockfile | Ensures consistent installs |
| `tsconfig.json` | TypeScript configuration | Type checking and compilation |

#### Dependencies Structure

```mermaid
graph TD
    package["package.json"] --> runtime["@anthropic-ai/claude-code-base-action"]
    
    subgraph Production["Production Dependencies"]
        core["@actions/core@^1.10.1"]
    end
    
    subgraph Development["Development Dependencies"]
        bunTypes["@types/bun@^1.2.12"]
        nodeTypes["@types/node@^20.0.0"] 
        prettier["prettier@3.5.3"]
        typescript["typescript@^5.8.3"]
    end
    
    runtime --> core
    runtime --> bunTypes
    runtime --> nodeTypes
    runtime --> prettier
    runtime --> typescript
    
    subgraph Scripts["NPM Scripts"]
        format["format: prettier --write ."]
        formatCheck["format:check: prettier --check ."]
        test["test: bun test"]
        typecheck["typecheck: tsc --noEmit"]
    end
```

Sources: [package.json:1-21](), [bun.lock:1-44]()

## Validation Error Handling

The validation system provides detailed error messages for debugging configuration issues.

### Error Message Format

Error messages follow this structure:
```
Environment variable validation failed:
  - {specific error 1}
  - {specific error 2}
  - {specific error N}
```

### Common Validation Errors

| Error Type | Example Error Message | Fix |
|------------|----------------------|-----|
| Missing API authentication | `Either ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN is required when using direct Anthropic API.` | Set one of the required API credentials |
| Provider conflict | `Cannot use both Bedrock and Vertex AI simultaneously. Please set only one provider.` | Remove one of the provider flags |
| Missing AWS variables | `AWS_REGION is required when using AWS Bedrock.` | Set all required AWS environment variables |
| Missing GCP variables | `ANTHROPIC_VERTEX_PROJECT_ID is required when using Google Vertex AI.` | Set all required GCP environment variables |

### Validation Test Coverage

The validation logic is comprehensively tested across multiple scenarios:

```mermaid
graph TD
    testSuite["validate-env.test.ts"] --> scenarios["Test Scenarios"]
    
    scenarios --> directAPI["Direct Anthropic API Tests"]
    scenarios --> bedrock["AWS Bedrock Tests"]  
    scenarios --> vertex["Google Vertex AI Tests"]
    scenarios --> multiProvider["Multiple Provider Tests"]
    scenarios --> errorFormat["Error Message Format Tests"]
    
    directAPI --> apiKeyPass["✓ ANTHROPIC_API_KEY provided"]
    directAPI --> apiKeyFail["✗ Missing API credentials"]
    
    bedrock --> bedrockPass["✓ All AWS variables provided"]
    bedrock --> bedrockOptional["✓ Optional AWS variables"]
    bedrock --> bedrockMissing["✗ Missing required AWS variables"]
    bedrock --> bedrockAll["✗ All AWS variables missing"]
    
    vertex --> vertexPass["✓ All GCP variables provided"]
    vertex --> vertexOptional["✓ Optional GCP variables"]
    vertex --> vertexMissing["✗ Missing required GCP variables"]
    vertex --> vertexAll["✗ All GCP variables missing"]
    
    multiProvider --> conflictTest["✗ Both providers enabled"]
    
    errorFormat --> multiError["Multiple errors formatting"]
```

Sources: [test/validate-env.test.ts:32-214]()

## Project Structure Reference

### Core Implementation Files

| File Path | Purpose | Key Exports/Functions |
|-----------|---------|----------------------|
| `src/validate-env.ts` | Environment validation logic | `validateEnvironmentVariables()` |
| `src/index.ts` | Main action entry point | Action execution logic |

### Test Infrastructure

| File Path | Purpose | Test Coverage |
|-----------|---------|---------------|
| `test/validate-env.test.ts` | Environment validation tests | 14 test scenarios across 5 categories |

### Configuration Files

| File Path | Purpose | Key Settings |
|-----------|---------|-------------|
| `action.yml` | GitHub Action definition | Inputs, outputs, execution steps |
| `tsconfig.json` | TypeScript configuration | Compilation and type checking |
| `.prettierrc` | Code formatting rules | Consistent code style |

### Development Tools

| File Path | Purpose | Usage |
|-----------|---------|-------|
| `package.json` | Project dependencies and scripts | `bun test`, `prettier`, `tsc` |
| `bun.lock` | Dependency version lock | Ensures reproducible builds |

### Runtime Dependencies Map

```mermaid
graph TD
    subgraph External["External Dependencies"]
        actionsCore["@actions/core"]
        actionsExec["@actions/exec"] 
        actionsIO["@actions/io"]
        actionsHttp["@actions/http-client"]
        undici["undici"]
        tunnel["tunnel"]
        fastifyBusboy["@fastify/busboy"]
    end
    
    subgraph DevDeps["Development Dependencies"]
        bunTypesMain["@types/bun"]
        bunTypesPackage["bun-types"]
        nodeTypes["@types/node"]
        undiciTypes["undici-types"]
        prettierMain["prettier"]
        typescriptMain["typescript"]
    end
    
    actionsCore --> actionsExec
    actionsCore --> actionsHttp
    actionsExec --> actionsIO
    actionsHttp --> tunnel
    actionsHttp --> undici
    undici --> fastifyBusboy
    
    bunTypesMain --> bunTypesPackage
    bunTypesPackage --> nodeTypes
    nodeTypes --> undiciTypes
```

Sources: [package.json:12-20](), [bun.lock:17-42]()

## Environment Variables Flow

The diagram below shows how environment variables are used in the authentication and execution flow:

```mermaid
flowchart LR
    subgraph InputSources["Input Sources"]
        actionInputs["Action Inputs"]
        envVars["Environment Variables"]
    end

    subgraph EnvProcessing["Environment Processing"]
        validateEnv["Environment Validator"]
        prepConfig["Configuration Preparer"]
    end

    subgraph Execution["Execution"]
        claudeRun["Claude Code Execution"]
    end

    actionInputs -->|Sets core env vars| validateEnv
    envVars -->|Provides auth env vars| validateEnv

    validateEnv -->|Validates auth method| prepConfig
    prepConfig -->|Prepares execution config| claudeRun

```

Sources: [action.yml:101-129]()

## MCP Configuration Reference

MCP (Modular Computation Platform) allows defining custom server configurations that Claude Code can interact with. The MCP configuration can be provided as a JSON file path or directly as a JSON string.

### MCP Configuration Structure

```mermaid
flowchart TD
  subgraph MCP_Configuration["MCP Configuration"]
    mcpConfig["MCP Config JSON"]
    mcpConfig --> mcpServers["mcpServers Object"]
    mcpServers --> serverDef["Server Definition"]
    serverDef --> serverName["Server Name"]
    serverDef --> command["Command"]
    serverDef --> args["Arguments Array"]
    serverDef --> env["Environment Variables"]
    serverName --> tools["MCP Tool References"]
    tools --> toolFormat["mcp__server-name__tool_name"]
  end

```

### MCP Configuration Format

The MCP configuration should follow this structure:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "executable",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR1": "value1",
        "ENV_VAR2": "value2"
      }
    }
  }
}
```

To use a custom MCP tool, reference it in the `allowed_tools` input with the format: `mcp__server-name__tool_name`.

Sources: [README.md:64-106]()

## Tool Reference

The action supports various tools that Claude can use during execution:

### Standard Tools

| Tool | Description | Example Usage |
|------|-------------|--------------|
| `Bash` | Executes bash commands | `Bash(git:*)` or `Bash(ls -la)` |
| `View` | Views file contents | Used automatically by Claude |
| `GlobTool` | Lists files matching a pattern | Used automatically by Claude |
| `GrepTool` | Searches files for patterns | Used automatically by Claude |
| `BatchTool` | Processes multiple files | Used automatically by Claude |
| `Write` | Writes to files | `Write` |

### Custom MCP Tools

Custom MCP tools are referenced using the format `mcp__server-name__tool_name` in the `allowed_tools` input.

Sources: [README.md:11-36](), [README.md:102-104]()

## Execution Log Reference

The action produces an execution log file in JSON format, accessible via the `execution_file` output.

### Execution Log Structure

```mermaid
graph TD
  subgraph executionLog[Execution Log]
    log[JSON Log Array]
    messages[Conversation Messages]
    humanMsg[Human Messages]
    humanRole[role: human]
    humanContent[content: string]
    assistantMsg[Assistant Messages]
    assistantRole[role: assistant]
    assistantContent[content: string]
    toolMsg[Tool Messages]
    toolRole[role: tool]
    toolName[name: string]
    toolContent[content: string]

    log --> messages
    messages --> humanMsg
    humanMsg --> humanRole
    humanMsg --> humanContent
    messages --> assistantMsg
    assistantMsg --> assistantRole
    assistantMsg --> assistantContent
    messages --> toolMsg
    toolMsg --> toolRole
    toolMsg --> toolName
    toolMsg --> toolContent
  end

```

The execution log is an array of message objects, each with a `role` field (`human`, `assistant`, or `tool`) and content information. This log captures the entire conversation history with Claude, including tool usage.

Sources: [README.md:139-162]()

## Model Reference

Different authentication methods require different model name formats:

| Provider | Model Name Format | Example |
|----------|-------------------|---------|
| Direct Anthropic API | `claude-{version}` | `claude-3-7-sonnet-20250219` |
| AWS Bedrock | `anthropic.claude-{version}` | `anthropic.claude-3-7-sonnet-20250219-v1:0` |
| Google Vertex AI | `claude-{version}@{date}` | `claude-3-7-sonnet@20250219` |

Sources: [README.md:184-222]()

## Security Considerations

When using the Claude Code Base Action, follow these security best practices:

1. **Never commit API keys directly** in your repository or workflows
2. Always use GitHub Actions secrets for sensitive information
3. Use `${{ secrets.SECRET_NAME }}` syntax to reference secrets
4. Use short-lived tokens when possible, especially with OIDC authentication
5. Limit the allowed tools to only those necessary for your workflow

Sources: [README.md:264-299]()

---

