<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/science-parse · page 3 Server Module · fetched 2026-10-26 -->

# Server Module

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cli/README.md](cli/README.md)
- [core/README.md](core/README.md)
- [core/src/main/java/org/allenai/scienceparse/BibRecord.java](core/src/main/java/org/allenai/scienceparse/BibRecord.java)
- [core/src/main/java/org/allenai/scienceparse/CitationRecord.java](core/src/main/java/org/allenai/scienceparse/CitationRecord.java)
- [core/src/main/scala/org/allenai/scienceparse/JsonProtocol.scala](core/src/main/scala/org/allenai/scienceparse/JsonProtocol.scala)
- [core/src/main/scala/org/allenai/scienceparse/LabeledData.scala](core/src/main/scala/org/allenai/scienceparse/LabeledData.scala)
- [core/src/test/scala/org/allenai/scienceparse/JsonProtocolSpec.scala](core/src/test/scala/org/allenai/scienceparse/JsonProtocolSpec.scala)
- [server/README.md](server/README.md)
- [server/src/main/scala/org/allenai/scienceparse/FeedbackStore.scala](server/src/main/scala/org/allenai/scienceparse/FeedbackStore.scala)
- [server/src/main/scala/org/allenai/scienceparse/SPServer.scala](server/src/main/scala/org/allenai/scienceparse/SPServer.scala)

</details>



## Purpose and Scope

The Server Module provides a RESTful HTTP API wrapper around the Science Parse Core library, enabling PDF parsing as a web service. It runs on port 8080 and exposes endpoints for parsing papers by Semantic Scholar ID or direct PDF upload, with optional user feedback/correction storage in PostgreSQL.

This document covers the server's architecture, request handling, endpoints, and deployment. For details about the underlying parsing logic, see [Core Library](#2). For command-line batch processing, see [CLI Module](#4). For feedback system database schema details, see [Feedback System](#3.2).

## Architecture Overview

The server is implemented as a Jetty-based HTTP service in [server/src/main/scala/org/allenai/scienceparse/SPServer.scala](). The main entry point is the `SPServer` object which configures and starts the service.

```mermaid
graph TB
    Main["SPServer.main()"]
    Config["Config case class<br/>modelFile, bibModelFile, gazetteerFile<br/>paperDirectory, enableFeedback, useS2Bucket"]
    ParserInit["Parser initialization<br/>new Parser(modelFile, gazetteerFile, bibModelFile)"]
    PaperSourceInit["PaperSource setup<br/>FallbackPaperSource or ScholarBucketPaperSource"]
    JettyServer["Jetty Server<br/>Port 8080<br/>maxFormContentSize: 10000000"]
    Handler["SPServer handler<br/>extends AbstractHandler"]
    
    Main --> Config
    Config --> ParserInit
    Config --> PaperSourceInit
    ParserInit --> Handler
    PaperSourceInit --> Handler
    Handler --> JettyServer
    
    JettyServer --> Start["server.start()<br/>server.join()"]
```

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:24-103]()

### Core Components

The `SPServer` class constructor takes three parameters:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `paperSource` | `PaperSource` | Abstraction for retrieving PDFs by ID or from local storage |
| `scienceParser` | `Parser` | Shared singleton instance for parsing PDFs |
| `enableFeedback` | `Boolean` | Whether to enable PostgreSQL-backed feedback endpoints |

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:106-110]()

## Request/Response Flow

The server uses a custom routing system with two route types: `StringRoute` for exact path matches and `RegexRoute` for pattern-based matching with capture groups.

```mermaid
graph LR
    HTTP["HTTP Request"]
    JettyHandler["AbstractHandler.handle()"]
    SPRequestBuilder["SPRequest.apply()<br/>Parse target, method, queryParams"]
    RouteIterator["routes.iterator.flatMap()<br/>Try each route sequentially"]
    
    StringRoute["StringRoute<br/>Exact path match"]
    RegexRoute["RegexRoute<br/>Regex with capture groups"]
    
    RouteHandle["route.handle()<br/>Returns Option[SPResponse]"]
    NotFound["404 or 405<br/>Based on path/method"]
    WriteResponse["Write SPResponse<br/>status, contentType, headers, content"]
    
    HTTP --> JettyHandler
    JettyHandler --> SPRequestBuilder
    SPRequestBuilder --> RouteIterator
    
    RouteIterator --> StringRoute
    RouteIterator --> RegexRoute
    
    StringRoute --> RouteHandle
    RegexRoute --> RouteHandle
    
    RouteHandle --> WriteResponse
    RouteIterator --> NotFound
    NotFound --> WriteResponse
```

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:233-278]()

### Route Definitions

The server defines routes in order of precedence:

```mermaid
graph TB
    Root["Root route<br/>^$|^/$<br/>Returns usage instructions"]
    PaperIdGET["RegexRoute<br/>^/v1/([a-f0-9]{40})$<br/>paperId capture group<br/>GET method<br/>handlePaperId()"]
    PostPDF["StringRoute<br/>/v1<br/>POST method<br/>handlePost()"]
    
    FeedbackCondition{"enableFeedback<br/>== true?"}
    
    FeedbackRoutes["Feedback routes:<br/>GET /v1/corrections<br/>GET /v1/corrections/{paperId}<br/>PUT /v1/corrections/{paperId}"]
    
    Root --> PaperIdGET
    PaperIdGET --> PostPDF
    PostPDF --> FeedbackCondition
    FeedbackCondition -->|Yes| FeedbackRoutes
    FeedbackCondition -->|No| NoFeedback["No feedback routes"]
```

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:217-231]()

### Route Types Implementation

The routing system is implemented with two case classes:

| Route Type | Path Matching | Handler Signature |
|------------|---------------|-------------------|
| `StringRoute` | Exact string equality | `SPRequest => SPResponse` |
| `RegexRoute` | Regex pattern with named groups | `(SPRequest, Map[String, String]) => SPResponse` |

Both extend a common `Route` trait with methods: `canHandleTarget()`, `canHandle()`, and `handle()`.

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:167-213]()

## Parsing Endpoints

The server provides two primary parsing endpoints that delegate to the shared `Parser` instance.

### GET /v1/{paperId}

Retrieves and parses a paper by its 40-character hexadecimal Semantic Scholar ID.

**Query Parameters:**

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `format` | `LabeledData`, `ExtractedMetadata` | `LabeledData` | Output format |
| `skipFields` | Comma-separated field names | (none) | Fields to omit from `LabeledData` output |

**Implementation Flow:**

```mermaid
graph TD
    Request["GET /v1/{paperId}?format=...&skipFields=..."]
    ExtractParams["Extract paperId from regex groups<br/>Extract format from queryParams<br/>Extract skipFields from queryParams"]
    
    FormatCheck{"format ==<br/>LabeledData?"}
    
    LabeledPath["LabeledPapersFromScienceParse.get()<br/>paperSource.getPdf(paperId)<br/>scienceParser.doParse()"]
    ExtractedPath["scienceParser.doParse()<br/>paperSource.getPdf(paperId)"]
    
    SkipFieldsCheck{"skipFields<br/>non-empty?"}
    
    StripFields["Strip fields from JSON:<br/>labeledDataJson.asJsObject.fields - field"]
    SkipError["Throw SPServerException(400)<br/>'skipFields' only works with LabeledData"]
    
    ToJSON["Convert to JSON<br/>content.prettyPrint"]
    Response["SPResponse(200, 'application/json', bytes)"]
    
    Request --> ExtractParams
    ExtractParams --> FormatCheck
    
    FormatCheck -->|Yes| LabeledPath
    FormatCheck -->|No| ExtractedPath
    
    LabeledPath --> SkipFieldsCheck
    ExtractedPath --> SkipFieldsCheck
    
    SkipFieldsCheck -->|Yes, format=LabeledData| StripFields
    SkipFieldsCheck -->|Yes, format=ExtractedMetadata| SkipError
    SkipFieldsCheck -->|No| ToJSON
    
    StripFields --> ToJSON
    ToJSON --> Response
```

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:285-306]()

### POST /v1

Accepts a PDF via HTTP POST and parses it directly.

**Request Requirements:**
- Content-Type: `application/pdf` (not validated in code, but recommended)
- Body: Raw PDF bytes

**Query Parameters:**

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `format` | `LabeledData`, `ExtractedMetadata` | `LabeledData` | Output format |

**Implementation:**

```mermaid
graph TD
    Request["POST /v1?format=..."]
    ReadBytes["DigestInputStream wrapping request.inputStream()<br/>Calculate SHA-1 hash<br/>IOUtils.toByteArray()"]
    
    FormatCheck{"format ==<br/>LabeledData?"}
    
    LabeledParse["LabeledPapersFromScienceParse.get()<br/>new ByteArrayInputStream(bytes)<br/>scienceParser"]
    ExtractedParse["scienceParser.doParse()<br/>new ByteArrayInputStream(bytes)"]
    
    ToJSON["toJson.prettyPrint"]
    Response["SPResponse(200, 'application/json', bytes)"]
    
    Request --> ReadBytes
    ReadBytes --> FormatCheck
    FormatCheck -->|Yes| LabeledParse
    FormatCheck -->|No| ExtractedParse
    LabeledParse --> ToJSON
    ExtractedParse --> ToJSON
    ToJSON --> Response
```

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:308-327]()

## Paper Source Abstraction

The `PaperSource` interface provides flexible PDF retrieval strategies. The server configures it based on command-line options:

```mermaid
graph TB
    Config["Command-line config<br/>--paperDirectory<br/>--useS2Bucket"]
    
    CheckS2{"useS2Bucket<br/>== true?"}
    
    DefaultS2["ScholarBucketPaperSource.getInstance()<br/>Internal S3 bucket"]
    DefaultPublic["PaperSource.getDefault<br/>Public S3 bucket"]
    
    CheckDir{"paperDirectory<br/>provided?"}
    
    DirSource["DirectoryPaperSource(dir)<br/>Local filesystem"]
    FallbackSource["FallbackPaperSource<br/>Try directory first, then S3"]
    
    FinalSource["paperSource"]
    
    Config --> CheckS2
    CheckS2 -->|Yes| DefaultS2
    CheckS2 -->|No| DefaultPublic
    
    DefaultS2 --> CheckDir
    DefaultPublic --> CheckDir
    
    CheckDir -->|Yes| DirSource
    CheckDir -->|No| FinalSource
    
    DirSource --> FallbackSource
    FallbackSource --> FinalSource
```

**Configuration:**

| Option | Effect |
|--------|--------|
| `--paperDirectory <dir>` | Creates `FallbackPaperSource` that tries local directory first, then falls back to S3 |
| `--useS2Bucket` | Uses internal Semantic Scholar S3 bucket instead of public bucket |
| (neither) | Uses public S3 bucket via `PaperSource.getDefault` |

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:81-95]()

## JSON Serialization

All responses use the spray-json library with custom formats defined in `JsonProtocol`. The serialization layer handles:

```mermaid
graph LR
    subgraph "Core Data Structures"
        ExtractedMetadata["ExtractedMetadata<br/>title, authors, year, abstractText<br/>sections, references, referenceMentions"]
        BibRecord["BibRecord<br/>title, author, venue<br/>citeRegEx, shortCiteRegEx, year"]
        CitationRecord["CitationRecord<br/>referenceID, context<br/>startOffset, endOffset"]
        Section["Section<br/>heading, text"]
    end
    
    subgraph "LabeledData Structures"
        LabeledData["LabeledData<br/>id, title, authors, venue, year<br/>abstractText, sections, references, mentions"]
        LDAuthor["LabeledData.Author<br/>name, email, affiliations"]
        LDSection["LabeledData.Section<br/>heading, text"]
        LDReference["LabeledData.Reference<br/>label, title, authors, venue<br/>year, volume, pageRange"]
        LDMention["LabeledData.Mention<br/>reference, text, inContext"]
    end
    
    JsonProtocol["JsonProtocol object<br/>Implicit JsonFormats"]
    
    ExtractedMetadata --> JsonProtocol
    BibRecord --> JsonProtocol
    CitationRecord --> JsonProtocol
    Section --> JsonProtocol
    
    LabeledData --> JsonProtocol
    LDAuthor --> JsonProtocol
    LDSection --> JsonProtocol
    LDReference --> JsonProtocol
    LDMention --> JsonProtocol
    
    JsonProtocol --> JSON["JSON output<br/>.toJson.prettyPrint"]
```

**Key Format Implementations:**

| Format | File Location |
|--------|---------------|
| `ExtractedMetadataJsonFormat` | [core/src/main/scala/org/allenai/scienceparse/JsonProtocol.scala:125-178]() |
| `BibRecordJsonFormat` | [core/src/main/scala/org/allenai/scienceparse/JsonProtocol.scala:63-99]() |
| `CitationRecordJsonFormat` | [core/src/main/scala/org/allenai/scienceparse/JsonProtocol.scala:101-123]() |
| `LabeledData` formats | [core/src/main/scala/org/allenai/scienceparse/JsonProtocol.scala:180-187]() |

**Sources:** [core/src/main/scala/org/allenai/scienceparse/JsonProtocol.scala:1-188](), [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:18-19]()

## Feedback System

The feedback system is an optional feature (disabled by default via `enableFeedback = false`) that stores user corrections in PostgreSQL. For detailed schema information, see [Feedback System](#3.2).

### Feedback Routes

When enabled, three additional routes become available:

```mermaid
graph TB
    GetAll["GET /v1/corrections<br/>correctionsGetAll()"]
    GetOne["GET /v1/corrections/{paperId}<br/>correctionsGet()"]
    PutOne["PUT /v1/corrections/{paperId}<br/>correctionsPut()"]
    
    QueryParams1["Query params:<br/>onOrAfter: epoch millis<br/>before: epoch millis"]
    QueryParams2["Query params:<br/>format: LabeledData (only)"]
    QueryParams3["Query params:<br/>format: LabeledData or ExtractedMetadata<br/>Body: JSON"]
    
    Store["FeedbackStore"]
    
    GetAll --> QueryParams1
    GetOne --> QueryParams2
    PutOne --> QueryParams3
    
    QueryParams1 --> Store
    QueryParams2 --> Store
    QueryParams3 --> Store
    
    Store --> getAllFeedback["getAllFeedback(onOrAfter, before)<br/>Returns all latest feedback"]
    Store --> getFeedback["getFeedback(paperId)<br/>Returns latest for one paper"]
    Store --> addFeedback["addFeedback(paperId, data)<br/>Stores new correction"]
```

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:217-221](), [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:332-393]()

### FeedbackStore Initialization

The `FeedbackStore` object initializes on first access:

```mermaid
graph TD
    Init["FeedbackStore object initialization"]
    LoadDriver["Class.forName('org.postgresql.Driver')"]
    LoadConfig["ConfigFactory.load()<br/>org.allenai.scienceparse.Server.db"]
    
    ConfigKeys["Config keys:<br/>url, user, password, logging"]
    
    ConnectionPool["ConnectionPool.singleton(url, user, password)"]
    
    RootConfig["Load db-as-root config<br/>for schema migrations"]
    RootPool["ConnectionPool.add('rootConnectionPool')"]
    
    SchemaCheck{"Current schema<br/>version?"}
    UpgradeFn["Execute schema upgrade function<br/>Version 0->1: CREATE TABLE feedback"]
    UpdateVersion["INSERT INTO settings (key, value)<br/>VALUES ('version', 1)"]
    
    Init --> LoadDriver
    LoadDriver --> LoadConfig
    LoadConfig --> ConfigKeys
    ConfigKeys --> ConnectionPool
    ConnectionPool --> RootConfig
    RootConfig --> RootPool
    RootPool --> SchemaCheck
    SchemaCheck --> UpgradeFn
    UpgradeFn --> UpdateVersion
```

**Schema Version Management:**

The system uses a `settings` table to track schema versions and applies upgrade functions sequentially:

| Version | Upgrade Function |
|---------|------------------|
| 0 → 1 | Creates `feedback` table with columns: `paperId CHAR(40)`, `timeAdded TIMESTAMP`, `value JSONB` |

**Sources:** [server/src/main/scala/org/allenai/scienceparse/FeedbackStore.scala:11-86]()

## Command-Line Configuration

The server accepts the following command-line arguments:

| Option | Argument | Purpose |
|--------|----------|---------|
| `-m`, `--model` | File path | Custom Parser CRF model (defaults to production model) |
| `-b`, `--bibModel` | File path | Custom bibliography parsing model |
| `-g`, `--gazetteer` | File path | Custom gazetteer file |
| `-p`, `--paperDirectory` | Directory path | Local directory for PDF storage/fallback |
| `--enableFeedback` | (flag) | Enables PostgreSQL feedback endpoints |
| `--useS2Bucket` | (flag) | Uses internal S2 S3 bucket instead of public bucket |
| `--downloadModelOnly` | (flag) | Downloads models and exits without starting server |
| `--help` | (flag) | Prints help text |

**Configuration Example:**

```bash
java -Xmx6g -jar science-parse-server.jar \
  --model custom-model.dat \
  --paperDirectory /data/pdfs \
  --enableFeedback \
  --useS2Bucket
```

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:35-67]()

## Error Handling

The server uses a custom exception type `SPServerException` with HTTP status codes:

```mermaid
graph TD
    Handler["handle() method"]
    TryBlock["Try block:<br/>Route matching & execution"]
    
    Success["SPResponse generated"]
    SPServerEx["Catch SPServerException<br/>status + message"]
    NonFatal["Catch NonFatal<br/>500 + exception message"]
    
    WriteStatus["response.setStatus()"]
    WriteContent["response.setContentType()<br/>response.getWriter().println()"]
    SetHandled["baseRequest.setHandled(true)"]
    
    Handler --> TryBlock
    TryBlock --> Success
    TryBlock --> SPServerEx
    TryBlock --> NonFatal
    
    Success --> WriteStatus
    SPServerEx --> WriteStatus
    NonFatal --> WriteStatus
    
    WriteStatus --> WriteContent
    WriteContent --> SetHandled
```

**Common Error Status Codes:**

| Status | Trigger |
|--------|---------|
| 400 | Invalid query parameters, unrecognized format, invalid JSON in PUT |
| 403 | Feedback endpoints accessed when `enableFeedback = false` |
| 404 | No route matches path, or no feedback found for paper ID |
| 405 | Route matches path but not HTTP method |
| 500 | Uncaught exceptions during parsing or processing |

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:116-118](), [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:239-277]()

## Deployment Options

The Server Module supports multiple deployment strategies. For detailed deployment instructions, see [Server Deployment](#3.3).

### Docker Deployment

Build Docker image:
```bash
./makeDocker.sh
```

Run container:
```bash
docker run -p 8080:8080 -m 8g allenai/science-parse
```

**Sources:** [README.md:26]()

### Fat JAR Deployment

Build executable JAR:
```bash
sbt server/assembly
```

Run directly:
```bash
java -Xmx6g -jar server/target/scala-2.12/science-parse-server-assembly-3.0.1.jar
```

**Memory Recommendations:**
- Minimum heap: 6GB (`-Xmx6g`)
- Additional off-heap memory: 2GB recommended
- Some documents may require more memory

**Sources:** [server/README.md:20-24]()

### SBT Run (Development)

For development, start directly from SBT:
```bash
sbt server/run
```

This avoids the assembly step and enables faster iteration.

**Sources:** [README.md:73]()

## Performance Characteristics

### Model Loading

On first startup, the server downloads and caches model files:

```mermaid
graph LR
    Start["Server startup"]
    LoadModels["Parser initialization<br/>Downloads from S3 if not cached"]
    Timing["Logged: 'Loaded science parser in Xms'"]
    Bind["Bind to port 8080"]
    
    Start --> LoadModels
    LoadModels --> Timing
    Timing --> Bind
```

Typical load time: ~5-15 seconds on first run, ~1-3 seconds on subsequent runs (cached).

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:70-76]()

### Request Processing

- Uses a shared `Parser` singleton across all requests
- Parser instance is thread-safe for concurrent requests
- Memory usage scales with PDF complexity (especially images and tables)
- Jetty's max form content size: 10,000,000 bytes (~10MB)

**Sources:** [server/src/main/scala/org/allenai/scienceparse/SPServer.scala:98]()

---

