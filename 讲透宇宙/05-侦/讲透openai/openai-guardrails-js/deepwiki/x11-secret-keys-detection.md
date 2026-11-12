<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-guardrails-js · extra page Secret Keys Detection · fetched 2026-10-26 -->

# Secret Keys Detection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/ref/checks/keywords.md](docs/ref/checks/keywords.md)
- [docs/ref/checks/moderation.md](docs/ref/checks/moderation.md)
- [docs/ref/checks/secret_keys.md](docs/ref/checks/secret_keys.md)
- [src/checks/secret-keys.ts](src/checks/secret-keys.ts)

</details>



The Secret Keys guardrail is a data protection module designed to identify potential API keys, credentials, and tokens within text. It utilizes a combination of common prefix matching, Shannon entropy analysis, character diversity metrics, and custom regular expressions to detect sensitive information before it is sent to or received from an LLM.

## Architecture and Data Flow

The detection process follows a multi-step validation logic. When text is passed to the `secretKeysCheck` function, it is tokenized and evaluated against specific criteria based on the configured sensitivity threshold.

### Secret Detection Logic Flow

This diagram illustrates the internal decision logic within `isSecretCandidate` and `detectSecretKeys`.

```mermaid
graph TD
    "InputText"["Input Text"] --> "Tokenize"["Tokenize by whitespace"]
    "Tokenize" --> "Clean"["Remove markdown symbols (#, *)"]
    "Clean" --> "Iterate"["For each Word"]
    
    subgraph "isSecretCandidate Logic [src/checks/secret-keys.ts]"
        "Iterate" --> "CustomRegex"{"Matches custom_regex?"}
        "CustomRegex" -- "Yes" --> "FlagSecret"["Mark as Secret"]
        "CustomRegex" -- "No" --> "StrictMode"{"Strict Mode?"}
        
        "StrictMode" -- "No" --> "AllowedPattern"{"Is URL or File Ext?"}
        "AllowedPattern" -- "Yes" --> "Ignore"["Ignore Word"]
        "AllowedPattern" -- "No" --> "PrefixCheck"{"Common Prefix?"}
        
        "StrictMode" -- "Yes" --> "PrefixCheck"
        
        "PrefixCheck" -- "Yes" --> "FlagSecret"
        "PrefixCheck" -- "No" --> "Metrics"{"Length & Diversity OK?"}
        
        "Metrics" -- "No" --> "Ignore"
        "Metrics" -- "Yes" --> "EntropyCheck"{"Entropy >= Threshold?"}
        
        "EntropyCheck" -- "Yes" --> "FlagSecret"
        "EntropyCheck" -- "No" --> "Ignore"
    end
    
    "FlagSecret" --> "Masking"["Replace with &lt;SECRET&gt;"]
    "Masking" --> "Result"["Return GuardrailResult"]
```
**Sources:** [src/checks/secret-keys.ts:196-234](), [src/checks/secret-keys.ts:239-264]()

## Configuration

The guardrail is configured via the `SecretKeysConfig` object. It supports three sensitivity levels and optional custom pattern matching.

### Sensitivity Thresholds
The `threshold` parameter selects a preset from the `CONFIGS` constant [src/checks/secret-keys.ts:109-136]().

| Level | `min_length` | `min_entropy` | `min_diversity` | `strict_mode` | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `strict` | 10 | 3.0 | 2 | `true` | Most sensitive; flags high-entropy filenames and code. |
| `balanced` | 10 | 3.8 | 3 | `false` | Default; balances sensitivity with false positive reduction. |
| `permissive` | 20 | 3.5 | 2 | `false` | Least sensitive; requires longer strings to trigger. |

### Implementation Details
*   **Shannon Entropy**: Calculated in the `entropy` function to measure the randomness of a string [src/checks/secret-keys.ts:141-156]().
*   **Character Diversity**: Measured by `charDiversity`, which checks for the presence of four categories: lowercase, uppercase, digits, and special characters [src/checks/secret-keys.ts:161-169]().
*   **Common Prefixes**: The system automatically flags strings starting with known patterns like `sk-`, `pk-`, `ghp_`, `AKIA`, and `Bearer ` [src/checks/secret-keys.ts:35-52]().
*   **File Extension Filtering**: In non-strict modes, common file extensions (e.g., `.py`, `.js`, `.pdf`) are ignored to prevent false positives in technical discussions [src/checks/secret-keys.ts:57-104]().

**Sources:** [src/checks/secret-keys.ts:16-21](), [src/checks/secret-keys.ts:109-136](), [src/checks/secret-keys.ts:35-52]()

## Code Entity Map

This diagram maps the natural language concepts of "Secret Detection" to the specific code entities in the TypeScript implementation.

```mermaid
classDiagram
    class SecretKeysGuardrail {
        <<Module>>
        +secretKeysCheck(ctx, data, config)
        +detectSecretKeys(text, cfg, customRegex)
        +isSecretCandidate(s, cfg, customRegex)
    }

    class Configuration {
        +SecretKeysConfig threshold
        +SecretKeysConfig custom_regex
        +CONFIGS presets
    }

    class Helpers {
        +entropy(s)
        +charDiversity(s)
        +containsAllowedPattern(text)
    }

    SecretKeysGuardrail ..> Configuration : uses
    SecretKeysGuardrail ..> Helpers : calls
    Configuration ..> "src/checks/secret-keys.ts" : defined in
    SecretKeysGuardrail ..> "src/checks/secret-keys.ts" : defined in
    Helpers ..> "src/checks/secret-keys.ts" : defined in
```
**Sources:** [src/checks/secret-keys.ts:16-21](), [src/checks/secret-keys.ts:109-136](), [src/checks/secret-keys.ts:277-284]()

## Usage and Masking

When a secret is detected, the guardrail returns a `GuardrailResult` where `tripwireTriggered` is `true`. The `info` object contains the list of detected secrets and a `masked_text` version of the input where secrets are replaced by the `<SECRET>` token [src/checks/secret-keys.ts:248-263]().

### Example Configuration
```json
{
  "name": "Secret Keys",
  "config": {
    "threshold": "strict",
    "custom_regex": ["internal-key-[0-9]{5}"]
  }
}
```

### Result Structure
The `info` property of the result follows this schema:
*   `guardrail_name`: "Secret Keys"
*   `detected_secrets`: An array of strings found to be candidates [src/checks/secret-keys.ts:260]().
*   `masked_text`: The original text with sensitive tokens replaced [src/checks/secret-keys.ts:261]().

**Sources:** [src/checks/secret-keys.ts:256-263](), [docs/ref/checks/secret_keys.md:32-40]()

---

