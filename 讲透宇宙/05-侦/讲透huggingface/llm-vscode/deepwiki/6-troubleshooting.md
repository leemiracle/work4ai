<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/llm-vscode · page 6 Troubleshooting · fetched 2026-10-26 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [package.json](package.json)
- [src/extension.ts](src/extension.ts)

</details>



This page provides a comprehensive guide to diagnosing and resolving common issues with the `llm-vscode` extension. It covers configuration problems, request failures, authentication issues, and other common errors that might occur during usage.

For general usage instructions, see [Getting Started](#1.2) or [Architecture](#2) for technical details about how the extension works.

## Common Issues and Solutions

### Extension Not Starting or Crashing

If the extension fails to activate or crashes during operation:

1. Check the VS Code output panel for error messages (View → Output, select "LLM VS Code" from dropdown)
2. Verify the extension is properly installed and enabled
3. Restart VS Code after any configuration changes
4. Check if the language server (`llm-ls`) is properly installed and accessible

```mermaid
flowchart TD
    A["Extension Fails to Start"] --> B{"Check Output Panel"}
    B --> C["Error in Output Panel?"]
    C -- "Yes" --> D["Identify Error Type"]
    C -- "No" --> E["Check Extension Version"]
    D --> F["Language Server Error"]
    D --> G["Configuration Error"]
    D --> H["Authentication Error"]
    F --> I["Check llm-ls binary path"]
    G --> J["Reset to default configuration"]
    H --> K["Re-authenticate with HF token"]
    E --> L["Update Extension"]
```

Sources: [src/extension.ts:35-87](), [package.json:48-51]()

### Authentication Problems

#### Token-Related Issues

```mermaid
flowchart TD
    A["Authentication Problems"] --> B{"Check Token Status"}
    B --> C["Not Logged In"]
    B --> D["Token Invalid/Expired"]
    B --> E["Permission Issues"]
    
    C --> F["Run 'Llm: Login' Command"]
    D --> G["Generate New Token at hf.co/settings/token"]
    E --> H["Verify Model Access Permissions"]
    
    F --> I["Enter Token in Prompt"]
    G --> F
    H --> J["Request Access to Gated Model"]
    
    I --> K["Test with Simple Completion"]
    J --> K
```

If you encounter authentication issues:

1. Verify you're logged in by running the `Llm: Login` command from the command palette
2. Check if your Hugging Face token is valid at [hf.co/settings/token](https://hf.co/settings/token)
3. If the extension says "Already logged in" but requests still fail, run `Llm: Logout` and login again
4. For models requiring specific access permissions, verify you have access to the model on Hugging Face

Error message: `"You're not logged in, please login"` indicates you need to provide your Hugging Face API token.

Sources: [src/extension.ts:101-136](), [README.md:49-57]()

### Configuration Issues

#### Model and Backend Configuration

Most configuration issues happen when there's a mismatch between your selected model, backend, and configuration parameters:

```mermaid
flowchart TD
    A["Configuration Issue"] --> B{"Identify Problem Type"}
    
    B --> C["Invalid Model ID"]
    B --> D["Backend Misconfiguration"]
    B --> E["Context Window Overflow"]
    B --> F["Tokenizer Issue"]
    
    C --> G["Check llm.modelId setting"]
    D --> H["Verify llm.backend & llm.url"]
    E --> I["Reduce context or increase llm.contextWindow"]
    F --> J["Verify tokenizer configuration"]
    
    G --> K["Use predefined template"]
    H --> L["Set correct endpoint for backend"]
    I --> M["Adjust max_new_tokens parameter"]
    J --> N["Configure tokenizer correctly"]
    
    K --> O["Select from llm.configTemplate dropdown"]
    L --> P["Check URL path construction"]
```

Common configuration errors:

1. **Model ID issues**: Incorrect model ID in `llm.modelId` setting
   - Solution: Select an appropriate model template from `llm.configTemplate` dropdown

2. **Backend issues**: Incorrect backend specified or URL not provided
   - Solution: Set `llm.backend` appropriately and provide `llm.url` when needed

3. **Context window issues**: Input too large for model's context window
   - Error message: `"Input is too long, model's context window is X tokens"`
   - Solution: Reduce input size or increase `llm.contextWindow` setting

4. **Tokenizer issues**: Incorrect tokenizer configuration
   - Error message: `"Failed to tokenize input"`
   - Solution: Verify your tokenizer settings match your model

Sources: [package.json:71-228](), [src/extension.ts:223-236](), [README.md:58-167]()

### Request Failures

When code completion requests fail:

```mermaid
flowchart TD
    A["Request Failure"] --> B{"Error Message Type"}
    
    B --> C["Rate Limit Exceeded"]
    B --> D["Model is Currently Loading"]
    B --> E["Connection Error"]
    B --> F["Invalid Response Format"]
    
    C --> G["Subscribe to Pro tier or wait"]
    D --> H["Wait for model to load"]
    E --> I["Check network connectivity"]
    F --> J["Validate backend configuration"]
    
    I --> K["Verify URL and TLS settings"]
    J --> L["Ensure compatible API format"]
```

1. **Rate limiting**: `"Rate limit exceeded"` or similar message
   - Solution: Subscribe to a Pro tier on Hugging Face or adjust request frequency

2. **Model loading**: `"Model is currently loading"` message
   - Solution: Wait for the model to finish loading on the backend

3. **Connection issues**: Network-related errors 
   - Solution: Check network connectivity, proxy settings, or try `llm.tlsSkipVerifyInsecure` for TLS issues

4. **Response format issues**: Unexpected response from backend
   - Solution: Ensure the backend returns the expected format for completions

Sources: [src/extension.ts:179-207](), [README.md:10-15]()

### Slow or No Completions

If completions are slow to appear or don't appear at all:

1. Check `llm.requestDelay` setting (default: 150ms) - increasing may improve performance
2. Verify `llm.enableAutoSuggest` is set to `true` for automatic suggestions
3. Check if the current file matches the `llm.documentFilter` pattern
4. Try manually triggering completions with `Alt+Shift+L`

```mermaid
sequenceDiagram
    participant User as "User"
    participant VSCode as "VS Code"
    participant Extension as "llm-vscode"
    participant LSP as "llm-ls"
    participant Backend as "LLM Backend"
    
    User->>VSCode: Type code
    VSCode->>Extension: Trigger completion
    Note over Extension: Check enableAutoSuggest
    Note over Extension: Apply requestDelay
    Note over Extension: Check documentFilter
    Extension->>LSP: Send completion request
    LSP->>Backend: Forward to LLM service
    
    alt Successful case
        Backend->>LSP: Return generated code
        LSP->>Extension: Return completion
        Extension->>VSCode: Show ghost text
    else Error case
        Backend->>LSP: Error response
        LSP->>Extension: Forward error
        Extension->>VSCode: Show error message
    else Timeout case
        Backend--xLSP: Request timeout
        LSP--xExtension: Timeout propagated
        Extension->>VSCode: No completion shown
    end
```

Sources: [src/extension.ts:142-213](), [package.json:75-79](), [package.json:80-84]()

### Language Server Issues

Problems with the `llm-ls` language server:

1. **Binary path issues**: If using a custom binary, verify `llm.lsp.binaryPath` points to a valid executable
2. **Port conflicts**: If using `llm.lsp.port`, ensure the port isn't in use by another application
3. **Log level**: Adjust `llm.lsp.logLevel` to `"debug"` for more detailed logs
4. **Binary not found**: On some platforms, the bundled binary might not work

```mermaid
flowchart TD
    A["Language Server Issue"] --> B{"Error Type"}
    
    B --> C["Binary not found"]
    B --> D["Communication error"]
    B --> E["Server crashes"]
    
    C --> F["Check llm.lsp.binaryPath"]
    D --> G["Verify port settings"]
    E --> H["Set llm.lsp.logLevel to debug"]
    
    F --> I["Build llm-ls from source"]
    G --> J["Check if port is in use"]
    H --> K["Check logs for error details"]
```

Sources: [package.json:184-204](), [src/extension.ts:39-70](), [README.md:125-127]()

## Error Message Reference Table

Below is a reference table of common error messages and their resolutions:

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "Failed to start language server" | Binary path incorrect or incompatible | Check `llm.lsp.binaryPath` or build from source |
| "Model is currently loading" | The model is being loaded by backend | Wait for the model to load completely |
| "You're not logged in" | Missing Hugging Face API token | Use `Llm: Login` command to provide token |
| "Rate limit exceeded" | Too many requests to free tier | Subscribe to Pro tier or reduce requests |
| "Input is too long" | Context window exceeded | Reduce input size or increase window setting |
| "Failed to tokenize input" | Incorrect tokenizer configuration | Verify tokenizer settings for your model |
| "Error connecting to URL" | Network or URL configuration issue | Check URL and network connectivity |
| "Timed out waiting for response" | Backend server too slow or overloaded | Try again later or use different backend |

Sources: [src/extension.ts:179-207](), [README.md:10-15]()

## Advanced Troubleshooting

### Debugging Request/Response Cycle

To debug the request/response cycle:

1. Set `llm.lsp.logLevel` to `"debug"`
2. Open the VS Code output panel and select "LLM VS Code"
3. Trigger a completion and review the logs

The request/response data flow follows this pattern:

```mermaid
flowchart LR
    A["VS Code Editor"] --> B["Extension"]
    B --> C["Language Client"]
    C --> D["llm-ls Server"]
    D --> E["LLM Backend API"]
    E --> D
    D --> C
    C --> B
    B --> A
```

Sources: [package.json:200-204](), [src/extension.ts:73-87]()

### Building Language Server from Source

If the bundled `llm-ls` binary doesn't work on your platform, you can build it from source:

1. Clone the repository: `git clone https://github.com/huggingface/llm-ls`
2. Build the binary: `cd llm-ls && cargo build --release`
3. Set `llm.lsp.binaryPath` to the path of the built binary

Sources: [README.md:189-197]()

### Troubleshooting Fill-in-the-Middle (FIM) Issues

If completions are not appearing in the middle of existing code:

1. Check that `llm.fillInTheMiddle.enabled` is set to `true`
2. Verify that the model supports FIM (not all models do)
3. Ensure the FIM tokens (`prefix`, `middle`, `suffix`) match the model's expected tokens

Sources: [package.json:123-142](), [README.md:78-80]()

### Ollama-Specific Issues

When using Ollama as a backend:

1. Ensure Ollama is running locally
2. Verify the model is pulled with `ollama pull codellama:7b` or similar
3. Set `llm.url` to `http://localhost:11434/api` if not automatically detected

Sources: [package.json:93](), [README.md:66]()