<!-- source: DeepWiki mcp.deepwiki.com · repo theagentrouter/agent-router · page 5 API Schemas and Translation · fetched 2026-10-21 -->

# API Schemas and Translation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/endpointspec/endpointspec.go](internal/endpointspec/endpointspec.go)
- [internal/endpointspec/endpointspec_test.go](internal/endpointspec/endpointspec_test.go)
- [internal/tracing/span.go](internal/tracing/span.go)
- [internal/tracing/tracer.go](internal/tracing/tracer.go)
- [internal/tracing/tracing.go](internal/tracing/tracing.go)
- [internal/tracing/tracingapi/api.go](internal/tracing/tracingapi/api.go)
- [internal/translator/translator.go](internal/translator/translator.go)
- [site/docs/capabilities/llm-integrations/supported-endpoints.md](site/docs/capabilities/llm-integrations/supported-endpoints.md)
- [site/docs/capabilities/llm-integrations/supported-providers.md](site/docs/capabilities/llm-integrations/supported-providers.md)

</details>



The API Schemas and Translation layer serves as the core mapping engine for the Envoy AI Gateway (`agent-router`). It ingests standard AI API requests—primarily OpenAI-compatible and Anthropic-compatible schemas—parses and validates them through typed endpoint specifications, and translates them on-the-fly into native vendor backend formats (such as AWS Bedrock Converse, GCP Vertex AI Gemini, and Azure OpenAI) [internal/apischema/openai/openai.go:6-9](), [internal/endpointspec/endpointspec.go:6-46](), [internal/translator/openai_gcpvertexai.go:74-76]().

This is a **PARENT page**. Below is a high-level overview of the schema and translator subsystems. For deep technical implementation details, consult the child pages:
- [OpenAI Schema and Endpoint Specs](#5.1)
- [AWS Bedrock and Anthropic Translators](#5.2)
- [GCP Vertex AI, Azure and Other Providers](#5.3)

---

### Request Processing and Translator Routing Pipeline

The following diagram bridges the abstract request space to concrete code entities in the `endpointspec` and `apischema` packages during request ingestion and parsing:

```mermaid
title "API Request Translation Pipeline"
graph TD
    ClientRequest[""Incoming HTTP Request /v1/chat/completions""] --> SpecRouter[""endpointspec.ChatCompletionsEndpointSpec""]
    SpecRouter --> ParseCall[""ParseBody(body []byte, costConfigured bool)""]
    ParseCall --> UnmarshalOpenAI[""json.Unmarshal(body, &openai.ChatCompletionRequest)""]
    UnmarshalOpenAI --> StreamMutate[""Stream Options Mutation (IncludeUsage=true)""]
    StreamMutate --> GetTrans[""GetTranslator(schema filterapi.VersionedAPISchema, override string)""]
    GetTrans --> TranslatorInst[""translator.Translator[ReqT, Span]""]

    subschk[""internal/endpointspec/endpointspec.go:36-142""]
```
Sources: [internal/endpointspec/endpointspec.go:36-142](), [internal/apischema/openai/openai.go:6-9]()

---

## 5.1 OpenAI Schema and Endpoint Specs

The gateway manages OpenAI-compatible structures manually via native Go structs [internal/apischema/openai/openai.go:6-9]() rather than heavy OpenAPI code generators. Union unmarshaling logic handles complex polymorphic fields like chat message content parts (`ChatCompletionContentPartUserUnionParam`), response formats (`ChatCompletionResponseFormatUnion`), and tool calls [internal/apischema/openai/openai_test.go:23-196]().

The `endpointspec.Spec` interface defines methods for request parsing, multipart handling, sensitive info redaction, and translator selection [internal/endpointspec/endpointspec.go:36-97](). Specific endpoint handlers like `ChatCompletionsEndpointSpec`, `EmbeddingsEndpointSpec`, and `CompletionsEndpointSpec` implement these rules and inject mandatory parameters (e.g., forcing `stream_options.include_usage = true` when cost tracking is active) [internal/endpointspec/endpointspec.go:98-142]().

For details, see [OpenAI Schema and Endpoint Specs](#5.1).

Sources: [internal/apischema/openai/openai.go:6-9](), [internal/endpointspec/endpointspec.go:36-142](), [internal/apischema/openai/openai_test.go:23-196]()

---

## 5.2 AWS Bedrock and Anthropic Translators

To target non-OpenAI vendor backends, the translator layer maps `openai.ChatCompletionRequest` structures directly into vendor APIs. The AWS Bedrock translator (`openAIToAWSBedrockTranslatorV1ChatCompletion`) converts chat parameters into the AWS Bedrock Converse API (`/model/{modelId}/converse` or `/model/{modelId}/converse-stream`) [internal/translator/openai_awsbedrock.go:36-44](), [internal/translator/openai_awsbedrock.go:103-121]().

It handles system message aggregation, reasoning/thinking configurations, tool definitions, and event stream folding for chunked SSE responses [internal/translator/openai_awsbedrock.go:57-169](). Similar translation paths exist for native Anthropic Messages APIs on AWS and GCP.

For details, see [AWS Bedrock and Anthropic Translators](#5.2).

---

### Vendor Translator Routing Architecture

The following diagram maps high-level provider targets to specific translator implementations within the `internal/translator` package:

```mermaid
title "Provider Translator Selection and Routing"
graph TD
    Selector[""EndpointSpec.GetTranslator()""] --> CheckSchema{""VersionedAPISchema.Name""}
    CheckSchema -->|APISchemaAWSBedrock| BedrockTrans[""translator.NewChatCompletionOpenAIToAWSBedrockTranslator()""]
    CheckSchema -->|APISchemaGCPVertexAI| GeminiTrans[""translator.NewChatCompletionOpenAIToGCPVertexAITranslator()""]
    CheckSchema -->|APISchemaAzureOpenAI| AzureTrans[""translator.NewChatCompletionOpenAIToAzureOpenAITranslator()""]
    CheckSchema -->|APISchemaOpenAI| DefaultTrans[""translator.NewChatCompletionOpenAIToOpenAITranslator()""]

    BedrockTrans --> BedrockImpl[""openAIToAWSBedrockTranslatorV1ChatCompletion""]
    GeminiTrans --> GeminiImpl[""openAIToGCPVertexAITranslatorV1ChatCompletion""]

    subschk[""internal/translator/openai_awsbedrock.go:31-40"", ""internal/translator/openai_gcpvertexai.go:68-76""]
```
Sources: [internal/translator/openai_awsbedrock.go:31-40](), [internal/translator/openai_gcpvertexai.go:68-76](), [internal/endpointspec/endpointspec.go:62-72]()

---

## 5.3 GCP Vertex AI, Azure and Other Providers

Google Cloud Vertex AI Gemini endpoints are supported through `openAIToGCPVertexAITranslatorV1ChatCompletion` [internal/translator/openai_gcpvertexai.go:70-76](). This translator converts OpenAI message chains, tool declarations, safety settings, and generation configs into native Google GenAI content structures (`genai.Content`, `genai.Part`) [internal/translator/gemini_helper.go:56-127](), [internal/translator/openai_gcpvertexai.go:119-123]().

Other supported capabilities include Azure OpenAI API version routing, Cohere rerank specifications, embedding transformations, image generations (`/v1/images/generations`), audio speech/transcription endpoints, and tokenization utilities [internal/endpointspec/endpointspec.go:102-124]().

For details, see [GCP Vertex AI, Azure and Other Providers](#5.3).

Sources: [internal/translator/openai_gcpvertexai.go:70-126](), [internal/translator/gemini_helper.go:56-127](), [internal/endpointspec/endpointspec.go:102-124]()

---

