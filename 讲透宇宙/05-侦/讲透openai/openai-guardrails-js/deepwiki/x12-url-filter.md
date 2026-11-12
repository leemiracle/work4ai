<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-guardrails-js · extra page URL Filter · fetched 2026-10-26 -->

# URL Filter

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/ref/checks/urls.md](docs/ref/checks/urls.md)
- [src/__tests__/unit/checks/keywords-urls.test.ts](src/__tests__/unit/checks/keywords-urls.test.ts)
- [src/checks/keywords.ts](src/checks/keywords.ts)
- [src/checks/urls.ts](src/checks/urls.ts)

</details>



The URL Filter guardrail provides advanced URL detection and filtering in user inputs and LLM outputs. It uses robust regex patterns and URL parsing to prevent credential injection, typosquatting, and scheme-based attacks while enforcing domain access policies through configurable allowlists.

## Purpose and Use Cases

The URL Filter guardrail addresses security and compliance requirements by:

- **Restricting allowed domains**: Permitting only approved external websites or IP addresses via `url_allow_list` [src/checks/urls.ts:66]().
- **Preventing credential injection**: Blocking URLs containing userinfo (e.g., `user:pass@domain`) by default [src/checks/urls.ts:71-72]().
- **Restricting dangerous schemes**: Blocking protocols like `javascript:`, `data:`, or `vbscript:` unless explicitly allowed [src/checks/urls.ts:18]().
- **Enforcing HTTPS**: Defaulting to HTTPS-only communication for security [src/checks/urls.ts:70]().
- **Managing subdomains**: Controlling whether subdomains of allowed domains (e.g., `api.example.com`) are automatically permitted [src/checks/urls.ts:74]().

Typical deployment scenarios include customer-facing chatbots that should only reference official documentation and enterprise assistants restricted to internal IP ranges or CIDR blocks [docs/ref/checks/urls.md:5-11]().

Sources: [src/checks/urls.ts:1-7](), [src/checks/urls.ts:64-75](), [docs/ref/checks/urls.md:1-11]()

## Configuration Structure

The URL Filter is configured via the `UrlsConfig` schema, which utilizes Zod for validation and preprocessing of schemes.

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url_allow_list` | `string[]` | `[]` | List of allowed domains, IP addresses, CIDR ranges, or full URLs. |
| `allowed_schemes` | `Set<string>` | `['https']` | Set of allowed URL protocols. Preprocessed to normalize formats like `http://` to `http` [src/checks/urls.ts:20-59](). |
| `block_userinfo` | `boolean` | `true` | If `true`, blocks URLs with embedded credentials to prevent injection attacks [src/checks/urls.ts:72](). |
| `allow_subdomains` | `boolean` | `false` | If `true`, allowing `example.com` also allows `api.example.com` [src/checks/urls.ts:74](). |

**Behavioral Rules:**
- **Deny-by-default**: If `url_allow_list` is empty (default), all detected URLs are blocked [docs/ref/checks/urls.md:30]().
- **Scheme Enforcement**: Any URL with a scheme not in `allowed_schemes` is automatically blocked, even if the domain is in the allowlist [src/checks/urls.ts:316-321]().
- **IP & CIDR Support**: Supports validation against specific IP addresses and CIDR network ranges [src/checks/urls.ts:285-300]().

Sources: [src/checks/urls.ts:64-75](), [docs/ref/checks/urls.md:27-43]()

## Implementation and Data Flow

The `urls` check function follows a multi-pass detection and validation pipeline.

### URL Detection Pipeline

```mermaid
graph TD
    Text["Input Text"] --> P1["Pattern 1: Schemed URLs<br/>(http, ftp, data, etc.)"]
    Text --> P2["Pattern 2: Domain-like<br/>(www.example.com)"]
    Text --> P3["Pattern 3: IP Addresses<br/>(192.168.1.1)"]
    
    P1 --> Dedup["Advanced Deduplication<br/>Remove domains already<br/>covered by full URLs"]
    P2 --> Dedup
    P3 --> Dedup
    
    Dedup --> Validate["Validation Loop<br/>(For each detected URL)"]
    
    subgraph "Security Checks"
        Validate --> SchemeCheck["Scheme in allowed_schemes?"]
        SchemeCheck --> UserInfo["block_userinfo enabled<br/>& contains @?"]
        UserInfo --> AllowList["Domain/IP in<br/>url_allow_list?"]
    end
    
    AllowList --> Result["GuardrailResult"]
```

1.  **Detection**: The engine uses three distinct regex patterns to identify URLs with schemes, domain-like strings (e.g., `www.test.com`), and raw IP addresses [src/checks/urls.ts:129-192]().
2.  **Deduplication**: It performs a second pass to ensure that a domain-only match (e.g., `example.com`) is not reported if it is already part of a full URL match (e.g., `https://example.com/path`) [src/checks/urls.ts:194-220]().
3.  **Validation**: Each URL is parsed and checked against:
    *   **Schemes**: Normalized and compared against `allowed_schemes` [src/checks/urls.ts:316-321]().
    *   **UserInfo**: Checked for the presence of `@` symbols in the authority section [src/checks/urls.ts:323-328]().
    *   **Allowlist**: Compared using exact match, subdomain logic, or CIDR range checks [src/checks/urls.ts:333-352]().

Sources: [src/checks/urls.ts:129-230](), [src/checks/urls.ts:302-365]()

## Code Entity Map

The following diagram maps the logical filtering components to their specific code implementations.

```mermaid
classDiagram
    class UrlsConfig {
        +url_allow_list: string[]
        +allowed_schemes: Set
        +block_userinfo: boolean
        +allow_subdomains: boolean
    }
    
    class UrlsCheck {
        <<Function>>
        +urls(ctx, text, config)
    }
    
    class URLHelpers {
        +detectUrls(text)
        +extractHostCandidate(url)
        +isIpInCidr(ip, cidr)
        +normalizeAllowedSchemes(val)
    }
    
    UrlsCheck ..> UrlsConfig : validates with
    UrlsCheck ..> URLHelpers : uses for parsing
    URLHelpers ..> CIDRLogic : ipToInt()
```

Sources: [src/checks/urls.ts:64-75](), [src/checks/urls.ts:129-130](), [src/checks/urls.ts:241-242](), [src/checks/urls.ts:302-305]()

## GuardrailResult Structure

The `urls` check returns a `GuardrailResult` with a detailed `info` object containing detection and blocking metadata.

| Field | Type | Description |
|-------|------|-------------|
| `detected` | `string[]` | All URLs found in the text [src/checks/urls.ts:369](). |
| `allowed` | `string[]` | URLs that passed all security and allowlist checks [src/checks/urls.ts:370](). |
| `blocked` | `string[]` | URLs that failed any check [src/checks/urls.ts:371](). |
| `blocked_reasons` | `string[]` | Detailed explanations for each blocked URL (e.g., "Contains userinfo", "Not in allow list") [src/checks/urls.ts:372](). |

### Example Violation Output
```json
{
  "tripwireTriggered": true,
  "info": {
    "detected": ["https://user:pass@malicious.com"],
    "allowed": [],
    "blocked": ["https://user:pass@malicious.com"],
    "blocked_reasons": ["https://user:pass@malicious.com: Contains userinfo (potential credential injection)"]
  }
}
```

Sources: [src/checks/urls.ts:366-376](), [docs/ref/checks/urls.md:52-69]()

## Integration with GuardrailsOpenAI

The URL Filter is registered in the `defaultSpecRegistry` and can be used in `pre_flight`, `input`, or `output` stages.

```typescript
import { GuardrailsOpenAI } from '@openai/guardrails';

const client = await GuardrailsOpenAI.create({
  version: 1,
  output: {
    version: 1,
    guardrails: [
      {
        name: 'URL Filter',
        config: {
          url_allow_list: ['trusted-docs.com'],
          allowed_schemes: ['https'],
          allow_subdomains: true
        }
      }
    ]
  }
});
```

**Performance Note**: The URL Filter uses deterministic regex and string parsing, making it extremely fast compared to LLM-based guardrails. It is highly suitable for streaming responses where low latency is critical [docs/ref/checks/urls.md:44-50]().

Sources: [src/checks/urls.ts:382-390](), [docs/ref/checks/urls.md:13-25]()

## Testing Behavior

The implementation is verified against various edge cases including:
- **Trailing Punctuation**: The filter strips characters like `.,;:!?` from the end of URLs to prevent false negatives caused by sentence structure [src/checks/urls.ts:131]().
- **Partial Matches**: Similar to the `keywordsCheck` [src/checks/keywords.ts:52](), the URL detector avoids partial matches on domains to prevent bypasses [src/__tests__/unit/checks/keywords-urls.test.ts:36-44]().
- **Scheme Normalization**: Schemes are cleaned of trailing colons and slashes (e.g., `https://` becomes `https`) before comparison [src/checks/urls.ts:45-48]().

Sources: [src/checks/urls.ts:148-150](), [src/checks/urls.ts:41-52](), [src/__tests__/unit/checks/keywords-urls.test.ts:11-23]()

---

