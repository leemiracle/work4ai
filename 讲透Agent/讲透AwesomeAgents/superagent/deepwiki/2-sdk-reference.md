<!-- source: DeepWiki mcp.deepwiki.com · repo superagent-ai/superagent · page 2 SDK Reference · fetched 2026-10-26 -->

# SDK Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [sdk/python/README.md](sdk/python/README.md)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/src/safety_agent/client.py](sdk/python/src/safety_agent/client.py)
- [sdk/python/src/safety_agent/types.py](sdk/python/src/safety_agent/types.py)
- [sdk/typescript/README.md](sdk/typescript/README.md)
- [sdk/typescript/package.json](sdk/typescript/package.json)
- [sdk/typescript/src/client.ts](sdk/typescript/src/client.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/types.ts](sdk/typescript/src/types.ts)

</details>



This document provides comprehensive reference documentation for the Superagent TypeScript and Python SDKs. Both SDKs maintain feature parity with identical version numbers (0.1.2) and share the same conceptual API surface, differing only in language-specific idioms.

The SDKs provide programmatic access to three core safety operations: `guard()` for security analysis, `redact()` for PII/PHI removal, and `scan()` for repository scanning. For command-line usage, see [CLI](#3). For MCP server integration, see [MCP Server](#4). For REST API access, see [REST API](#5).

**Sources:** [sdk/typescript/package.json:1-52](), [sdk/python/pyproject.toml:1-51]()

## SDK Architecture

The following diagram shows the core classes, methods, and types that comprise the SDK architecture in both languages:

```mermaid
graph TB
    subgraph "Client Layer"
        createClient["createClient()<br/>(Factory Function)"]
        SafetyClient["SafetyClient<br/>(Main Class)"]
    end
    
    subgraph "Core Operations"
        guard["guard()<br/>GuardOptions → GuardResponse"]
        redact["redact()<br/>RedactOptions → RedactResponse"]
        scan["scan()<br/>ScanOptions → ScanResponse"]
    end
    
    subgraph "Processing Pipeline"
        processInput["processInput()<br/>Handles URL, Blob, PDF"]
        chunkText["chunkText()<br/>Split large texts"]
        aggregateGuardResults["aggregateGuardResults()<br/>OR logic merging"]
        parseJsonResponse["parseJsonResponse()<br/>Extract structured data"]
    end
    
    subgraph "Provider System"
        parseModel["parseModel()<br/>provider/model → ParsedModel"]
        callProvider["callProvider()<br/>Unified LLM interface"]
        supportsStructuredOutput["supportsStructuredOutput()<br/>Check JSON schema support"]
    end
    
    subgraph "Type System"
        GuardInput["GuardInput<br/>string | Blob | URL"]
        ProcessedInput["ProcessedInput<br/>text | image | pdf | document"]
        ChatMessage["ChatMessage<br/>role + content"]
        TokenUsage["TokenUsage<br/>prompt/completion/total"]
    end
    
    createClient --> SafetyClient
    SafetyClient --> guard
    SafetyClient --> redact
    SafetyClient --> scan
    
    guard --> processInput
    guard --> chunkText
    guard --> aggregateGuardResults
    guard --> callProvider
    
    redact --> callProvider
    redact --> parseJsonResponse
    
    scan --> callProvider
    
    callProvider --> parseModel
    callProvider --> supportsStructuredOutput
    
    processInput --> ProcessedInput
    guard -.uses.-> GuardInput
    callProvider -.uses.-> ChatMessage
    guard -.returns.-> TokenUsage
```

**Sources:** [sdk/typescript/src/index.ts:1-55](), [sdk/typescript/src/client.ts:1-861](), [sdk/python/src/safety_agent/client.py:1-706]()

## Language-Specific Entry Points

### TypeScript Package Structure

```mermaid
graph LR
    index["index.ts<br/>(Main Export)"]
    client["client.ts<br/>(SafetyClient)"]
    types["types.ts<br/>(Type Definitions)"]
    providers["providers/index.ts<br/>(Model Abstraction)"]
    utils["utils/input-processor.ts<br/>(Input Handling)"]
    schemas["schemas.ts<br/>(JSON Schemas)"]
    prompts["prompts/<br/>(System Prompts)"]
    
    index --> client
    index --> types
    index --> providers
    index --> utils
    index --> schemas
    index --> prompts
    
    client --> types
    client --> providers
    client --> utils
    client --> schemas
    client --> prompts
```

The TypeScript SDK exports from `sdk/typescript/src/index.ts`:
- `createClient()` - Factory function for client creation
- `SafetyClient` - Main client class
- Type exports: `GuardInput`, `GuardOptions`, `RedactOptions`, `ScanOptions`, `GuardResponse`, `RedactResponse`, `ScanResponse`, etc.
- Utility exports: `processInput()`, `isVisionModel()`
- Provider exports: `parseModel()`, `getProvider()`, `providers`
- Schema exports: `GUARD_RESPONSE_FORMAT`, `REDACT_RESPONSE_FORMAT`
- Prompt exports: `buildGuardSystemPrompt()`, `buildRedactSystemPrompt()`, etc.

**Sources:** [sdk/typescript/src/index.ts:1-55]()

### Python Package Structure

```mermaid
graph LR
    init["__init__.py<br/>(Main Export)"]
    client["client.py<br/>(SafetyClient)"]
    types_py["types.py<br/>(Type Definitions)"]
    providers_py["providers.py<br/>(Model Abstraction)"]
    utils_py["utils/input_processor.py<br/>(Input Handling)"]
    schemas_py["schemas.py<br/>(JSON Schemas)"]
    prompts_py["prompts/<br/>(System Prompts)"]
    
    init --> client
    init --> types_py
    
    client --> types_py
    client --> providers_py
    client --> utils_py
    client --> schemas_py
    client --> prompts_py
```

The Python SDK exports from `sdk/python/src/safety_agent/__init__.py`:
- `create_client()` - Factory function for client creation
- `SafetyClient` - Main client class
- Type classes: `GuardInput`, `GuardOptions`, `RedactOptions`, `ScanOptions`, `GuardResponse`, `RedactResponse`, `ScanResponse`, etc.

**Sources:** [sdk/python/pyproject.toml:38-38](), [sdk/python/src/safety_agent/client.py:1-706]()

## Client Creation

Both SDKs provide a factory function for creating client instances.

### TypeScript Client Creation

The `createClient()` function instantiates a `SafetyClient`:

```typescript
function createClient(config?: ClientConfig): SafetyClient
```

Configuration interface:
```typescript
interface ClientConfig {
  apiKey?: string;  // Defaults to SUPERAGENT_API_KEY env var
}
```

The `SafetyClient` constructor validates the API key and stores it for usage tracking:

| Component | Location | Purpose |
|-----------|----------|---------|
| Factory function | [sdk/typescript/src/client.ts:858-860]() | Creates SafetyClient instance |
| Constructor | [sdk/typescript/src/client.ts:417-425]() | Validates API key, initializes client |
| Config interface | [sdk/typescript/src/types.ts:4-7]() | Type definition for client configuration |

**Sources:** [sdk/typescript/src/client.ts:858-860](), [sdk/typescript/src/client.ts:417-425](), [sdk/typescript/src/types.ts:4-7]()

### Python Client Creation

The `create_client()` function instantiates a `SafetyClient`:

```python
def create_client(api_key: str | None = None, *, config: ClientConfig | None = None) -> SafetyClient
```

Configuration dataclass:
```python
@dataclass
class ClientConfig:
    api_key: str | None = None
```

The `SafetyClient.__init__()` method validates the API key and stores it for usage tracking:

| Component | Location | Purpose |
|-----------|----------|---------|
| Factory function | [sdk/python/src/safety_agent/client.py:688-705]() | Creates SafetyClient instance |
| Constructor | [sdk/python/src/safety_agent/client.py:190-210]() | Validates API key, initializes client |
| Config dataclass | [sdk/python/src/safety_agent/types.py:14-20]() | Type definition for client configuration |

**Sources:** [sdk/python/src/safety_agent/client.py:688-705](), [sdk/python/src/safety_agent/client.py:190-210](), [sdk/python/src/safety_agent/types.py:14-20]()

## Guard Operation

The `guard()` method classifies input content as `"pass"` or `"block"` by detecting prompt injections, malicious instructions, and security threats.

### Guard Operation Flow

```mermaid
graph TB
    input["GuardInput<br/>(string | Blob | URL)"]
    processInput["processInput()"]
    processedType{"ProcessedInput.type"}
    
    textPath["Text/Document Path"]
    chunkCheck{"chunkSize > 0<br/>AND text.length > chunkSize"}
    chunkText["chunkText()"]
    guardSingleText["guardSingleText()"]
    parallel["Promise.all<br/>(parallel execution)"]
    aggregate["aggregateGuardResults()"]
    
    imagePath["Image Path"]
    guardImage["guardImage()"]
    
    pdfPath["PDF Path"]
    pdfPages["processed.pages"]
    parallelPages["Promise.all<br/>(parallel per page)"]
    
    response["GuardResponse"]
    postUsage["postUsage()"]
    
    input --> processInput
    processInput --> processedType
    
    processedType -->|"text/document"| textPath
    processedType -->|"image"| imagePath
    processedType -->|"pdf"| pdfPath
    
    textPath --> chunkCheck
    chunkCheck -->|"No"| guardSingleText
    chunkCheck -->|"Yes"| chunkText
    chunkText --> parallel
    parallel --> aggregate
    
    imagePath --> guardImage
    
    pdfPath --> pdfPages
    pdfPages --> parallelPages
    parallelPages --> aggregate
    
    guardSingleText --> response
    guardImage --> response
    aggregate --> response
    response --> postUsage
```

**Sources:** [sdk/typescript/src/client.ts:568-643](), [sdk/python/src/safety_agent/client.py:332-442]()

### Guard Input Types

The `GuardInput` type accepts multiple input formats:

| Input Type | TypeScript | Python | Processing |
|------------|------------|--------|------------|
| Plain text | `string` | `str` | Direct analysis |
| URL | `string` (starts with `http://` or `https://`) | `str` (starts with `http://` or `https://`) | Fetched then analyzed |
| Blob/File | `Blob` | `bytes` | MIME type detection |
| URL object | `URL` | N/A | Fetched then analyzed |

**Sources:** [sdk/typescript/src/types.ts:796-796](), [sdk/python/src/safety_agent/types.py:35-41]()

### Guard Options

TypeScript:
```typescript
interface GuardOptions {
  input: GuardInput;
  systemPrompt?: string;  // Custom system prompt override
  model?: SupportedModel;  // Defaults to "superagent/guard-0.6b"
  chunkSize?: number;      // Default: 8000, set to 0 to disable
}
```

Python:
```python
@dataclass
class GuardOptions:
    input: GuardInput
    system_prompt: str | None = None
    model: SupportedModel | None = None
    chunk_size: int = 8000
```

**Sources:** [sdk/typescript/src/types.ts:833-842](), [sdk/python/src/safety_agent/types.py:110-125]()

### Guard Response Format

Both SDKs return a `GuardResponse` with classification results and token usage:

TypeScript:
```typescript
interface GuardResponse {
  classification: "pass" | "block";
  reasoning: string;
  violation_types: string[];
  cwe_codes: string[];
  usage: TokenUsage;
}
```

Python:
```python
@dataclass
class GuardResponse:
    classification: Literal["pass", "block"]
    reasoning: str
    violation_types: list[str]
    cwe_codes: list[str]
    usage: TokenUsage
```

| Field | Type | Description |
|-------|------|-------------|
| `classification` | `"pass"` or `"block"` | Whether content should be blocked |
| `reasoning` | `string` | Explanation of classification decision |
| `violation_types` | `string[]` | Detected violation categories (e.g., `"prompt_injection"`) |
| `cwe_codes` | `string[]` | CWE identifiers (e.g., `"CWE-94"`, `"CWE-89"`) |
| `usage` | `TokenUsage` | Prompt, completion, and total token counts |

**Sources:** [sdk/typescript/src/types.ts:883-888](), [sdk/python/src/safety_agent/types.py:196-214]()

### Text Chunking Strategy

For large text inputs, the `guard()` method automatically splits content into chunks and processes them in parallel using OR logic (blocks if ANY chunk is blocked).

The chunking implementation:

**TypeScript:**
```typescript
function chunkText(text: string, chunkSize: number): string[] {
  // Splits at word boundaries, not mid-word
}
```
[sdk/typescript/src/client.ts:38-60]()

**Python:**
```python
def _chunk_text(text: str, chunk_size: int) -> list[str]:
    # Splits at word boundaries, not mid-word
```
[sdk/python/src/safety_agent/client.py:37-69]()

Aggregation logic merges results using OR semantics:

**TypeScript:**
```typescript
function aggregateGuardResults(results: GuardResponse[]): GuardResponse {
  const hasBlock = results.some((r) => r.classification === "block");
  // Merges violation_types and cwe_codes, sums token usage
}
```
[sdk/typescript/src/client.ts:66-90]()

**Python:**
```python
def _aggregate_guard_results(results: list[GuardResponse]) -> GuardResponse:
    has_block = any(r.classification == "block" for r in results)
    # Merges violation_types and cwe_codes, sums token usage
```
[sdk/python/src/safety_agent/client.py:72-104]()

**Sources:** [sdk/typescript/src/client.ts:38-90](), [sdk/python/src/safety_agent/client.py:37-104]()

### Vision Model Support

For image inputs, the SDKs automatically use vision-capable models if the processed input type is `"image"`:

**TypeScript:**
```typescript
private async guardImage(
  processed: ProcessedInput,
  systemPrompt: string | undefined,
  model: string
): Promise<GuardResponse>
```
[sdk/typescript/src/client.ts:499-554]()

**Python:**
```python
async def _guard_image(
    self,
    processed: ProcessedInput,
    system_prompt: str | None,
    model: str,
) -> GuardResponse:
```
[sdk/python/src/safety_agent/client.py:276-330]()

The methods construct multimodal content with base64-encoded image data:
```typescript
const imageDataUrl = `data:${processed.mimeType};base64,${processed.imageBase64}`;
const userContent: MultimodalContentPart[] = [
  { type: "image_url", image_url: { url: imageDataUrl } }
];
```

**Sources:** [sdk/typescript/src/client.ts:499-554](), [sdk/python/src/safety_agent/client.py:276-330]()

## Redact Operation

The `redact()` method removes or rewrites sensitive information (PII/PHI) from text.

### Redact Options

TypeScript:
```typescript
interface RedactOptions {
  input: string;
  entities?: string[];   // Custom entity types to redact
  model: SupportedModel; // Required
  rewrite?: boolean;     // Contextual rewriting vs placeholders
}
```

Python:
```python
@dataclass
class RedactOptions:
    input: str
    model: SupportedModel
    entities: list[str] | None = None
    rewrite: bool = False
```

**Sources:** [sdk/typescript/src/types.ts:847-856](), [sdk/python/src/safety_agent/types.py:149-164]()

### Redact Response Format

TypeScript:
```typescript
interface RedactResponse {
  redacted: string;    // Sanitized text output
  findings: string[];  // List of detected entities
  usage: TokenUsage;
}
```

Python:
```python
@dataclass
class RedactResponse:
    redacted: str
    findings: list[str]
    usage: TokenUsage
```

**Sources:** [sdk/typescript/src/types.ts:892-896](), [sdk/python/src/safety_agent/types.py:216-227]()

### Redact Implementation

Both SDKs follow the same implementation pattern:

1. Build system prompt with entity configuration using `buildRedactSystemPrompt(entities, rewrite)`
2. Build user message using `buildRedactUserMessage(input)`
3. Call provider with structured output if supported
4. Parse JSON response to extract `redacted` and `findings`
5. Post usage metrics

**TypeScript:** [sdk/typescript/src/client.ts:650-683]()  
**Python:** [sdk/python/src/safety_agent/client.py:444-514]()

**Sources:** [sdk/typescript/src/client.ts:650-683](), [sdk/python/src/safety_agent/client.py:444-514]()

## Scan Operation

The `scan()` method analyzes git repositories for AI agent-targeted attacks by cloning them into a Daytona sandbox and running OpenCode with a security-focused prompt.

### Scan Operation Architecture

```mermaid
graph TB
    scanMethod["SafetyClient.scan()"]
    validate["Validate repo URL"]
    callDaytonaScan["callDaytonaScan()"]
    
    subgraph "Daytona Sandbox"
        createSandbox["daytona.create()"]
        npmInstall["npm i -g opencode-ai@latest"]
        gitClone["sandbox.git.clone()"]
        openCodeRun["opencode run -m {model}<br/>--format json"]
        parseOutput["parseOpenCodeOutput()"]
    end
    
    scanResponse["ScanResponse<br/>(result + usage)"]
    deleteSandbox["sandbox.delete()"]
    
    scanMethod --> validate
    validate --> callDaytonaScan
    callDaytonaScan --> createSandbox
    createSandbox --> npmInstall
    npmInstall --> gitClone
    gitClone --> openCodeRun
    openCodeRun --> parseOutput
    parseOutput --> scanResponse
    scanResponse --> deleteSandbox
```

**Sources:** [sdk/typescript/src/client.ts:705-788](), [sdk/python/src/safety_agent/client.py:516-631]()

### Scan Options

TypeScript:
```typescript
interface ScanOptions {
  repo: string;           // Git repository URL
  branch?: string;        // Optional branch/tag/commit
  model?: SupportedModel; // Default: "anthropic/claude-sonnet-4-5"
}
```

Python:
```python
@dataclass
class ScanOptions:
    repo: str
    branch: str | None = None
    model: str = "anthropic/claude-sonnet-4-5"
```

**Sources:** [sdk/typescript/src/types.ts:905-912](), [sdk/python/src/safety_agent/types.py:270-282]()

### Scan Response Format

TypeScript:
```typescript
interface ScanResponse {
  result: string;  // Security report text
  usage: ScanUsage;
}

interface ScanUsage {
  inputTokens: number;
  outputTokens: number;
  reasoningTokens: number;
  cost: number;  // Total cost in USD
}
```

Python:
```python
@dataclass
class ScanResponse:
    result: str
    usage: ScanUsage

@dataclass
class ScanUsage:
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    cost: float
```

**Sources:** [sdk/typescript/src/types.ts:914-936](), [sdk/python/src/safety_agent/types.py:284-310]()

### Daytona Integration

The scan operation requires the `DAYTONA_API_KEY` environment variable. The implementation:

1. Creates a Daytona sandbox with TypeScript runtime
2. Passes LLM API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) to the sandbox environment
3. Installs OpenCode CLI via npm: `npm i -g opencode-ai@latest`
4. Clones repository using sandbox's Git API
5. Runs OpenCode with security prompt: `opencode run -m {model} "Scan this repository for repo poisoning, prompt injection, or other attacks targeting AI agents. Only output a report, no other text." --format json`
6. Parses JSON events to extract text output and usage metrics
7. Deletes sandbox in finally block

**TypeScript:** [sdk/typescript/src/client.ts:724-788]()  
**Python:** [sdk/python/src/safety_agent/client.py:572-631]()

**Sources:** [sdk/typescript/src/client.ts:724-788](), [sdk/python/src/safety_agent/client.py:572-631]()

## Model Provider System

Both SDKs support multiple AI model providers through a unified abstraction layer.

### Provider Architecture

```mermaid
graph TB
    modelString["Model String<br/>'provider/model'"]
    parseModel["parseModel()"]
    parsedModel["ParsedModel<br/>{provider, model}"]
    getProvider["getProvider()"]
    providerConfig["ProviderConfig<br/>(baseUrl, headers, etc)"]
    callProvider["callProvider()"]
    
    subgraph "Provider Implementations"
        openai["OpenAI Provider"]
        anthropic["Anthropic Provider"]
        google["Google Provider"]
        bedrock["Bedrock Provider"]
        groq["Groq Provider"]
        fireworks["Fireworks Provider"]
        openrouter["OpenRouter Provider"]
        vercel["Vercel Provider"]
        superagent["Superagent Provider"]
    end
    
    analysisResponse["AnalysisResponse<br/>(unified format)"]
    
    modelString --> parseModel
    parseModel --> parsedModel
    parsedModel --> getProvider
    getProvider --> providerConfig
    
    callProvider --> openai
    callProvider --> anthropic
    callProvider --> google
    callProvider --> bedrock
    callProvider --> groq
    callProvider --> fireworks
    callProvider --> openrouter
    callProvider --> vercel
    callProvider --> superagent
    
    openai --> analysisResponse
    anthropic --> analysisResponse
    google --> analysisResponse
    bedrock --> analysisResponse
    groq --> analysisResponse
    fireworks --> analysisResponse
    openrouter --> analysisResponse
    vercel --> analysisResponse
    superagent --> analysisResponse
```

**Sources:** [sdk/typescript/src/providers/index.ts](), [sdk/python/src/safety_agent/providers.py]()

### Model String Format

All models are specified in `provider/model` format:

| Provider | Format Example | Required Environment Variable |
|----------|----------------|------------------------------|
| Superagent | `superagent/guard-0.6b` | None (default for guard) |
| OpenAI | `openai/gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| Google | `google/gemini-2.0-flash` | `GOOGLE_API_KEY` |
| AWS Bedrock | `bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0` | `AWS_BEDROCK_API_KEY`, `AWS_BEDROCK_REGION` (optional) |
| Groq | `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| Fireworks | `fireworks/accounts/fireworks/models/llama-v3p3-70b-instruct` | `FIREWORKS_API_KEY` |
| OpenRouter | `openrouter/openai/gpt-4o` | `OPENROUTER_API_KEY` |
| Vercel AI | `vercel/openai/gpt-4o` | `AI_GATEWAY_API_KEY` |

**Sources:** [sdk/typescript/README.md:54-68](), [sdk/python/README.md:99-110]()

### Supported Model Types

The SDKs define comprehensive type unions for all supported models:

**TypeScript:**
```typescript
type SupportedModel =
  | OpenAIModel
  | AnthropicModel
  | GoogleModel
  | BedrockModel
  | VercelModel
  | GroqModel
  | FireworksModel
  | OpenRouterModel
  | SuperagentModel;
```
[sdk/typescript/src/types.ts:777-786]()

**Python:**
```python
SupportedModel = str  # "provider/model" format
```
[sdk/python/src/safety_agent/types.py:28-28]()

**Sources:** [sdk/typescript/src/types.ts:777-786](), [sdk/python/src/safety_agent/types.py:28-28]()

### Default Guard Model

Both SDKs use `superagent/guard-0.6b` as the default model for guard operations (TypeScript) or `superagent/guard-1.7b` (Python):

**TypeScript:** [sdk/typescript/src/providers/index.ts]() defines `DEFAULT_GUARD_MODEL`  
**Python:** [sdk/python/src/safety_agent/providers.py]() defines `DEFAULT_GUARD_MODEL`

**Sources:** [sdk/typescript/src/client.ts:19-19](), [sdk/python/src/safety_agent/client.py:30-30]()

### Structured Output Support

The SDKs check whether a model supports structured JSON output (JSON Schema) to enable response format constraints:

**TypeScript:**
```typescript
function supportsStructuredOutput(modelString: string): boolean {
  const { provider, model } = parseModel(modelString);
  
  if (provider === "openai") return true;
  if (provider === "vercel") return true;
  if (provider === "google") return true;
  if (provider === "bedrock") return true;
  
  // Provider-specific model checks for Groq, Fireworks, Anthropic, OpenRouter
  // ...
}
```
[sdk/typescript/src/client.ts:114-408]()

**Python:**
```python
def _supports_structured_output(model_string: str) -> bool:
    parsed = parse_model(model_string)
    provider = parsed.provider
    model = parsed.model
    
    if provider == "openai": return True
    if provider == "vercel": return True
    if provider == "google": return True
    if provider == "bedrock": return True
    
    # Provider-specific model checks
    # ...
```
[sdk/python/src/safety_agent/client.py:130-182]()

This function determines whether to pass `GUARD_RESPONSE_FORMAT` or `REDACT_RESPONSE_FORMAT` to the provider, or rely on prompt-based JSON extraction.

**Sources:** [sdk/typescript/src/client.ts:114-408](), [sdk/python/src/safety_agent/client.py:130-182]()

## Input Processing Pipeline

The SDKs implement a sophisticated input processor that handles URLs, files, PDFs, and images.

### Input Processor Architecture

```mermaid
graph TB
    guardInput["GuardInput<br/>(string | Blob | URL)"]
    processInput["processInput()"]
    
    typeCheck{"Input Type?"}
    
    stringPath["String Input"]
    urlCheck{"Starts with http(s)://?"}
    fetchUrl["fetch(url)"]
    contentType{"Content-Type?"}
    
    blobPath["Blob Input"]
    mimeType{"blob.type"}
    
    pdfExtract["extractPdfText()"]
    imageEncode["base64 encode"]
    textExtract["text extraction"]
    
    processedText["ProcessedInput<br/>{type: 'text', text}"]
    processedImage["ProcessedInput<br/>{type: 'image', imageBase64}"]
    processedPdf["ProcessedInput<br/>{type: 'pdf', pages[]}"]
    processedDoc["ProcessedInput<br/>{type: 'document', text}"]
    
    guardInput --> processInput
    processInput --> typeCheck
    
    typeCheck -->|"string"| stringPath
    typeCheck -->|"Blob"| blobPath
    
    stringPath --> urlCheck
    urlCheck -->|"Yes"| fetchUrl
    urlCheck -->|"No"| processedText
    
    fetchUrl --> contentType
    contentType -->|"application/pdf"| pdfExtract
    contentType -->|"image/*"| imageEncode
    contentType -->|"text/*"| textExtract
    
    blobPath --> mimeType
    mimeType -->|"application/pdf"| pdfExtract
    mimeType -->|"image/*"| imageEncode
    mimeType -->|"text/*"| textExtract
    
    pdfExtract --> processedPdf
    imageEncode --> processedImage
    textExtract --> processedDoc
```

**Sources:** [sdk/typescript/src/utils/input-processor.ts](), [sdk/python/src/safety_agent/utils/input_processor.py]()

### ProcessedInput Type

TypeScript:
```typescript
interface ProcessedInput {
  type: "text" | "image" | "document" | "pdf";
  text?: string;
  imageBase64?: string;
  mimeType?: string;
  pages?: string[];  // For PDF type
}
```

Python:
```python
@dataclass
class ProcessedInput:
    type: Literal["text", "image", "document", "pdf"]
    text: str | None = None
    image_base64: str | None = None
    mime_type: str | None = None
    pages: list[str] | None = None
```

**Sources:** [sdk/typescript/src/types.ts:817-828](), [sdk/python/src/safety_agent/types.py:85-103]()

### PDF Text Extraction

For PDF inputs, the SDKs extract text from each page:

**TypeScript:** Uses `unpdf` package [sdk/typescript/package.json:50-50]()  
**Python:** Uses `pypdf` package [sdk/python/pyproject.toml:24-24]()

Each page is returned as a separate string in the `pages` array, enabling parallel per-page analysis in the guard operation.

**Sources:** [sdk/typescript/package.json:50-50](), [sdk/python/pyproject.toml:24-24]()

### Vision Model Detection

The `isVisionModel()` utility determines if a model supports image inputs:

**TypeScript:**
```typescript
export function isVisionModel(modelString: string): boolean {
  const { provider, model } = parseModel(modelString);
  
  // OpenAI vision models: gpt-4o, gpt-4-turbo, etc.
  // Anthropic vision models: claude-3-*, claude-sonnet-4-*, etc.
  // Google vision models: gemini-*
}
```

**Python:**
```python
def is_vision_model(model_string: str) -> bool:
    parsed = parse_model(model_string)
    provider = parsed.provider
    model = parsed.model
    
    # OpenAI, Anthropic, Google vision model checks
```

**Sources:** [sdk/typescript/src/utils/input-processor.ts](), [sdk/python/src/safety_agent/utils/input_processor.py]()

## Response Schemas

Both SDKs define JSON schemas for structured output when supported by the model provider.

### Guard Response Schema

The `GUARD_RESPONSE_FORMAT` schema defines the expected structure:

**TypeScript:**
```typescript
export const GUARD_RESPONSE_FORMAT: ResponseFormat = {
  type: "json_schema",
  json_schema: {
    name: "guard_response",
    schema: {
      type: "object",
      properties: {
        classification: { type: "string", enum: ["pass", "block"] },
        reasoning: { type: "string" },
        violation_types: { type: "array", items: { type: "string" } },
        cwe_codes: { type: "array", items: { type: "string" } }
      },
      required: ["classification", "reasoning", "violation_types", "cwe_codes"],
      additionalProperties: false
    },
    strict: true
  }
};
```

**Python:**
```python
GUARD_RESPONSE_FORMAT: ResponseFormat = {
    "type": "json_schema",
    "json_schema": {
        "name": "guard_response",
        "schema": {
            "type": "object",
            "properties": {
                "classification": {"type": "string", "enum": ["pass", "block"]},
                "reasoning": {"type": "string"},
                "violation_types": {"type": "array", "items": {"type": "string"}},
                "cwe_codes": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["classification", "reasoning", "violation_types", "cwe_codes"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}
```

**Sources:** [sdk/typescript/src/schemas.ts](), [sdk/python/src/safety_agent/schemas.py]()

### Redact Response Schema

The `REDACT_RESPONSE_FORMAT` schema defines the redaction output structure:

**TypeScript:**
```typescript
export const REDACT_RESPONSE_FORMAT: ResponseFormat = {
  type: "json_schema",
  json_schema: {
    name: "redact_response",
    schema: {
      type: "object",
      properties: {
        redacted: { type: "string" },
        findings: { type: "array", items: { type: "string" } }
      },
      required: ["redacted", "findings"],
      additionalProperties: false
    },
    strict: true
  }
};
```

**Python:**
```python
REDACT_RESPONSE_FORMAT: ResponseFormat = {
    "type": "json_schema",
    "json_schema": {
        "name": "redact_response",
        "schema": {
            "type": "object",
            "properties": {
                "redacted": {"type": "string"},
                "findings": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["redacted", "findings"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}
```

**Sources:** [sdk/typescript/src/schemas.ts](), [sdk/python/src/safety_agent/schemas.py]()

### Fallback JSON Parsing

When structured output is not supported, the SDKs parse JSON from model responses, handling markdown code blocks:

**TypeScript:**
```typescript
function parseJsonResponse<T>(content: string): T {
  const trimmed = content.trim();
  
  // Try direct parse first
  try {
    return JSON.parse(trimmed);
  } catch {
    // Extract from markdown code block
    const match = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/);
    if (match?.[1]) {
      return JSON.parse(match[1].trim());
    }
    throw new Error(`Failed to parse JSON response: ${content}`);
  }
}
```
[sdk/typescript/src/client.ts:95-109]()

**Python:**
```python
def _parse_json_response(content: str) -> dict[str, Any]:
    trimmed = content.strip()
    
    # Try direct parse
    try:
        return json.loads(trimmed)
    except json.JSONDecodeError:
        pass
    
    # Extract from markdown code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", trimmed)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Failed to parse JSON response: {content}")
```
[sdk/python/src/safety_agent/client.py:107-128]()

**Sources:** [sdk/typescript/src/client.ts:95-109](), [sdk/python/src/safety_agent/client.py:107-128]()

## Token Usage Tracking

Both SDKs track token usage and report it to the Superagent dashboard.

### TokenUsage Type

TypeScript:
```typescript
interface TokenUsage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
}
```

Python:
```python
@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
```

**Sources:** [sdk/typescript/src/types.ts:941-945](), [sdk/python/src/safety_agent/types.py:183-189]()

### Usage Reporting

After each operation, the SDKs post usage metrics to `https://superagent.sh/api/billing/usage` with the total token count:

**TypeScript:**
```typescript
private postUsage(usage: TokenUsage): void {
  fetch("https://superagent.sh/api/billing/usage", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": this.apiKey,
    },
    body: JSON.stringify({ token_count: usage.totalTokens }),
  }).catch(() => {}); // Fire and forget
}
```
[sdk/typescript/src/client.ts:430-439]()

**Python:**
```python
def _post_usage(self, usage: TokenUsage) -> None:
    """Post usage metrics to Superagent dashboard (fire and forget)."""
    try:
        httpx.post(
            "https://superagent.sh/api/billing/usage",
            headers={
                "Content-Type": "application/json",
                "x-api-key": self._api_key,
            },
            json={"token_count": usage.total_tokens},
            timeout=5.0,
        )
    except Exception:
        pass  # Fire and forget - ignore errors
```
[sdk/python/src/safety_agent/client.py:212-225]()

This is a fire-and-forget operation that silently ignores errors.

**Sources:** [sdk/typescript/src/client.ts:430-439](), [sdk/python/src/safety_agent/client.py:212-225]()

## Package Distribution

### TypeScript Package

| Property | Value |
|----------|-------|
| Package name | `safety-agent` |
| Version | `0.1.2` |
| Main entry | `./dist/index.js` |
| Types | `./dist/index.d.ts` |
| Build command | `tsc` |
| Test framework | `vitest` |
| Node version | `>=18.0.0` |
| Dependencies | `@daytonaio/sdk`, `ipaddr.js`, `unpdf` |

**Sources:** [sdk/typescript/package.json:1-52]()

### Python Package

| Property | Value |
|----------|-------|
| Package name | `safety-agent` |
| Version | `0.1.2` |
| Main module | `src/safety_agent` |
| Python version | `>=3.10` |
| Build backend | `hatchling` |
| Test framework | `pytest` with `pytest-asyncio` |
| Dependencies | `httpx>=0.27.0`, `pypdf>=5.0.0`, `daytona-sdk>=0.129.0` |

**Sources:** [sdk/python/pyproject.toml:1-51]()

---

