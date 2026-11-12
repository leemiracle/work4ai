<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/sinonym · page 4 Data and Type System · fetched 2026-10-26 -->

# Data and Type System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pyproject.toml](pyproject.toml)
- [sinonym/coretypes/results.py](sinonym/coretypes/results.py)
- [sinonym/detector.py](sinonym/detector.py)
- [sinonym/services/formatting.py](sinonym/services/formatting.py)
- [uv.lock](uv.lock)

</details>



This page provides an overview of sinonym's data structures and type system design. It covers the immutability guarantees, functional composition patterns, and how data flows through the processing pipeline. For details on the linguistic databases (surnames, given names, compounds), see [Name Data Structures](#4.1). For configuration details, see [Configuration System](#4.3).

## Design Philosophy

Sinonym's type system is built around three core principles:

1. **Immutability**: All data structures are frozen dataclasses, ensuring thread safety and preventing accidental mutation
2. **Functional Composition**: Result types provide Scala-compatible operations (`map`, `flat_map`) for error handling
3. **Dual Views**: Names are represented in both semantic order (given-surname) and original input order

These design choices enable safe concurrent processing and seamless integration with Scala codebases.

**Sources:** [sinonym/coretypes/results.py:1-192](), [sinonym/detector.py:1-163]()

## Core Type Hierarchy

```mermaid
graph TB
    subgraph "Result Types"
        PR["ParseResult<br/>(frozen dataclass)<br/>success: bool<br/>result: str | tuple<br/>error_message: str?<br/>map(f)<br/>flat_map(f)"]
        PN["ParsedName<br/>(frozen dataclass)<br/>surname: str<br/>given_name: str<br/>surname_tokens: list[str]<br/>given_tokens: list[str]<br/>middle_name: str<br/>middle_tokens: list[str]<br/>order: list[str]"]
        CI["CacheInfo<br/>(frozen dataclass)<br/>cache_built: bool<br/>cache_size: int<br/>pickle_file_exists: bool"]
    end
    
    subgraph "Batch Processing Types"
        BPR["BatchParseResult<br/>(frozen dataclass)<br/>names: list[str]<br/>results: list[ParseResult]<br/>format_pattern: BatchFormatPattern<br/>individual_analyses: list[IndividualAnalysis]<br/>improvements: list[int]"]
        BFP["BatchFormatPattern<br/>(frozen dataclass)<br/>dominant_format: NameFormat<br/>confidence: float<br/>surname_first_count: int<br/>given_first_count: int<br/>total_count: int<br/>threshold_met: bool"]
        IA["IndividualAnalysis<br/>(frozen dataclass)<br/>raw_name: str<br/>candidates: list[ParseCandidate]<br/>best_candidate: ParseCandidate?<br/>confidence: float"]
        PC["ParseCandidate<br/>(frozen dataclass)<br/>surname_tokens: list[str]<br/>given_tokens: list[str]<br/>score: float<br/>format: NameFormat<br/>original_compound_format: str?"]
    end
    
    subgraph "Enumeration Types"
        NF["NameFormat<br/>(Enum)<br/>SURNAME_FIRST<br/>GIVEN_FIRST<br/>MIXED"]
    end
    
    subgraph "Intermediate Types"
        NI["NormalizedInput<br/>(frozen dataclass)<br/>roman_tokens: list[str]<br/>norm_map: dict[str,str]<br/>compound_metadata: dict[str,CompoundMetadata]"]
        CM["CompoundMetadata<br/>(frozen dataclass)<br/>compound_target: str<br/>format_type: str"]
    end
    
    PR --> PN
    PR --> PN
    BPR --> PR
    BPR --> BFP
    BPR --> IA
    IA --> PC
    PC --> NF
    BFP --> NF
    NI --> CM
    
    style PR fill:#e1f5ff
    style PN fill:#fff4e1
    style BPR fill:#e8f5e9
    style NI fill:#ffe1e1
```

**Type Immutability Contract**

All dataclasses use `@dataclass(frozen=True)`, which prevents field reassignment after construction:

| Type | Frozen | Purpose |
|------|--------|---------|
| `ParseResult` | ✓ | Either-like result container with success/failure states |
| `ParsedName` | ✓ | Structured name components with dual order views |
| `NormalizedInput` | ✓ | Intermediate normalized tokens and metadata |
| `CompoundMetadata` | ✓ | Format authority for compound surnames |
| `CacheInfo` | ✓ | Read-only cache statistics |
| `BatchParseResult` | ✓ | Complete batch analysis with pattern detection |

**Sources:** [sinonym/coretypes/results.py:1-192](), [sinonym/services/normalization.py:1-50]()

## Data Flow Through Type Transformations

```mermaid
flowchart LR
    Input["str<br/>'Zhang Wei'"]
    
    Input --> Norm["NormalizationService.apply()"]
    Norm --> NI["NormalizedInput<br/>roman_tokens: ['zhang','wei']<br/>norm_map: {'zhang':'zhang'}<br/>compound_metadata: {}"]
    
    NI --> Parse["NameParsingService<br/>.parse_name_order()"]
    Parse --> PRInt["ParseResult<br/>success=True<br/>result=(['zhang'],['wei'])<br/>parsed: ParsedName tokens"]
    
    PRInt --> Format["NameFormattingService<br/>.format_name_output_with_tokens()"]
    Format --> PRFinal["ParseResult<br/>success=True<br/>result='Wei Zhang'<br/>parsed: ParsedName<br/>  surname='Zhang'<br/>  given_name='Wei'<br/>  order=['given','surname']<br/>parsed_original_order: ParsedName<br/>  surname='Wei'<br/>  given_name='Zhang'<br/>  order=['surname','given']"]
    
    PRFinal --> API["ChineseNameDetector<br/>.normalize_name()"]
    API --> Output["ParseResult<br/>(returned to caller)"]
    
    style NI fill:#e1f5ff
    style PRInt fill:#fff4e1
    style PRFinal fill:#e8f5e9
```

**Key Transformation Points:**

1. **Normalization** [sinonym/services/normalization.py:150-200](): Raw string → `NormalizedInput` with tokens and metadata
2. **Parsing** [sinonym/services/parsing.py:1-100](): `NormalizedInput` → `ParseResult` with token pairs
3. **Formatting** [sinonym/services/formatting.py:42-180](): Token pairs → `ParseResult` with formatted string and `ParsedName`
4. **API Return** [sinonym/detector.py:249-496](): Final `ParseResult` with dual `ParsedName` views

**Sources:** [sinonym/detector.py:249-496](), [sinonym/services/normalization.py:150-200](), [sinonym/services/formatting.py:181-333]()

## ParsedName: Dual View Design

The `ParsedName` dataclass provides two simultaneous views of the same name:

```mermaid
graph TB
    subgraph "Input: '张伟' (Han characters)"
        Input["'张伟'"]
    end
    
    subgraph "After Processing"
        PR["ParseResult"]
        
        Parsed["parsed (semantic view)<br/>ParsedName<br/>surname: 'Zhang'<br/>given_name: 'Wei'<br/>order: ['given','surname']<br/><br/>Interpretation:<br/>'Wei' is the given name<br/>'Zhang' is the surname"]
        
        ParsedOrig["parsed_original_order<br/>ParsedName<br/>surname: 'Wei'<br/>given_name: 'Zhang'<br/>order: ['surname','given']<br/><br/>Interpretation:<br/>First part was 'Zhang' (surname)<br/>Second part was 'Wei' (given)"]
    end
    
    Input --> PR
    PR --> Parsed
    PR --> ParsedOrig
    
    Note1["Semantic view: Always normalized<br/>to 'Given Surname' format.<br/>Labels match semantic roles."]
    Note2["Original order view: Labels indicate<br/>position in input, not semantic role.<br/>'surname' field = first part of input.<br/>'given_name' field = second part of input."]
    
    Parsed -.-> Note1
    ParsedOrig -.-> Note2
    
    style Parsed fill:#e8f5e9
    style ParsedOrig fill:#fff4e1
```

**Field Interpretation:**

| View | `surname` field | `given_name` field | `order` field | Use Case |
|------|----------------|-------------------|---------------|----------|
| `parsed` | Always the surname (semantic) | Always the given name (semantic) | Normalized order: `['given','surname']` | Downstream processing, display |
| `parsed_original_order` | First component (positional) | Second component (positional) | Original order: `['surname','given']` or `['given','surname']` | Format preservation, round-tripping |

**Example Scenarios:**

```python
# Scenario 1: Surname-first input
result = detector.normalize_name("张伟")  # "Zhang Wei" in pinyin
result.parsed.surname              # "Zhang" (semantic)
result.parsed.given_name           # "Wei" (semantic)
result.parsed.order                # ["given", "surname"]

result.parsed_original_order.surname    # "Wei" (first part was Wei? No!)
# Actually, for all-Chinese input, original order is surname-first:
result.parsed_original_order.order      # ["surname", "given"]
# So the labels are swapped to reflect positional interpretation

# Scenario 2: Given-first input
result = detector.normalize_name("Wei Zhang")
result.parsed.surname              # "Zhang" (semantic)
result.parsed.given_name           # "Wei" (semantic)
result.parsed_original_order.order # ["given", "surname"]
# Original order matches semantic order, labels align
```

**Sources:** [sinonym/coretypes/results.py:14-31](), [sinonym/detector.py:324-363]()

## Functional Composition: ParseResult Operations

`ParseResult` implements Scala-compatible monadic operations for error handling:

```mermaid
graph TB
    subgraph "ParseResult Structure"
        PR["ParseResult<br/>(Either-like)<br/>success: bool<br/>result: str | tuple<br/>error_message: str?"]
        
        Success["Success Path<br/>success=True<br/>result='Wei Zhang'<br/>error_message=None"]
        
        Failure["Failure Path<br/>success=False<br/>result=''<br/>error_message='surname not recognised'"]
    end
    
    subgraph "Functional Operations"
        Map["map(f: str -> str)<br/>-> ParseResult<br/><br/>Transforms result on success<br/>Preserves failure state"]
        
        FlatMap["flat_map(f: str -> ParseResult)<br/>-> ParseResult<br/><br/>Chains operations that may fail<br/>Short-circuits on failure"]
    end
    
    PR --> Success
    PR --> Failure
    
    Success --> Map
    Success --> FlatMap
    Failure --> Map
    Failure --> FlatMap
    
    Map -.->|"success: transform"| Success
    Map -.->|"failure: passthrough"| Failure
    FlatMap -.->|"success: chain"| Success
    FlatMap -.->|"failure: passthrough"| Failure
    
    style Success fill:#e8f5e9
    style Failure fill:#ffcccc
    style Map fill:#e1f5ff
    style FlatMap fill:#fff4e1
```

**Implementation Details:**

| Method | Signature | Behavior on Success | Behavior on Failure |
|--------|-----------|---------------------|---------------------|
| `map(f)` | `(str -> str) -> ParseResult` | Apply `f` to `result`, wrap in new `ParseResult` | Return `self` unchanged |
| `flat_map(f)` | `(str -> ParseResult) -> ParseResult` | Apply `f`, preserve compound metadata | Return `self` unchanged |

**Code Example:**

```python
# map: Transform formatted name
result = detector.normalize_name("Zhang Wei")
uppercased = result.map(lambda name: name.upper())
# ParseResult(success=True, result="WEI ZHANG")

# flat_map: Chain operations that may fail
def validate_and_format(name: str) -> ParseResult:
    if len(name) > 20:
        return ParseResult.failure("name too long")
    return ParseResult.success_with_name(name.title())

result = detector.normalize_name("Zhang Wei")
chained = result.flat_map(validate_and_format)
```

**Sources:** [sinonym/coretypes/results.py:101-133]()

## CompoundMetadata: Format Authority Pattern

`CompoundMetadata` serves as the single source of truth for compound surname formatting, threading through the entire pipeline:

```mermaid
flowchart TD
    Input["Input: 'AuYeung Wei'<br/>(camelCase compound)"]
    
    Input --> Detect["CompoundDetector<br/>.detect_compounds()"]
    Detect --> Meta["CompoundMetadata<br/>key: 'AuYeung'<br/>compound_target: 'au yeung'<br/>format_type: 'camelCase'"]
    
    Meta --> NI["NormalizedInput<br/>roman_tokens: ['au','yeung','wei']<br/>compound_metadata:<br/>  'AuYeung' -> metadata<br/>  'au' -> metadata<br/>  'yeung' -> metadata"]
    
    NI --> Parse["NameParsingService<br/>Uses metadata to recognize<br/>compound boundaries"]
    Parse --> ParseRes["ParseResult<br/>surname_tokens: ['au','yeung']<br/>given_tokens: ['wei']"]
    
    ParseRes --> Format["NameFormattingService<br/>._format_compound_with_metadata()"]
    Format --> Output["Output: 'Wei AuYeung'<br/>(preserves camelCase)"]
    
    style Meta fill:#fff4e1
    style NI fill:#e1f5ff
    style Format fill:#e8f5e9
```

**CompoundMetadata Fields:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `compound_target` | `str` | Normalized form for matching | `"ou yang"` |
| `format_type` | `str` | Original format style | `"camelCase"`, `"hyphenated"`, `"spaced"`, `"compact"` |

**Format Type Decision Tree:**

```mermaid
graph TD
    Start["Compound surname detected<br/>tokens: ['au','yeung']"]
    
    Start --> Check["Check format_type<br/>from metadata"]
    
    Check -->|"camelCase"| Camel["Format as 'AuYeung'<br/>capitalize first letter of each part"]
    Check -->|"hyphenated"| Hyph["Format as 'Au-Yeung'<br/>join with hyphens"]
    Check -->|"spaced"| Space["Format as 'Au Yeung'<br/>join with spaces"]
    Check -->|"compact"| Compact["Format as 'Auyeung'<br/>find original token, capitalize"]
    
    Camel --> Output["Output with preserved format"]
    Hyph --> Output
    Space --> Output
    Compact --> Output
    
    style Check fill:#fff4e1
    style Output fill:#e8f5e9
```

**Sources:** [sinonym/services/normalization.py:30-80](), [sinonym/services/formatting.py:339-437]()

## Batch Processing Type System

Batch processing introduces additional types for analyzing multiple names together:

```mermaid
graph TB
    subgraph "Input"
        Names["list[str]<br/>['Zhang Wei', 'Li Ming', 'Bei Yu']"]
    end
    
    subgraph "Analysis Types"
        IA["IndividualAnalysis<br/>Per-name analysis<br/>raw_name: str<br/>candidates: list[ParseCandidate]<br/>best_candidate: ParseCandidate?<br/>confidence: float"]
        
        PC["ParseCandidate<br/>surname_tokens: list[str]<br/>given_tokens: list[str]<br/>score: float<br/>format: NameFormat<br/>original_compound_format: str?"]
        
        BFP["BatchFormatPattern<br/>Detected pattern<br/>dominant_format: NameFormat<br/>confidence: float<br/>surname_first_count: int<br/>given_first_count: int<br/>total_count: int<br/>threshold_met: bool"]
    end
    
    subgraph "Output"
        BPR["BatchParseResult<br/>names: list[str]<br/>results: list[ParseResult]<br/>format_pattern: BatchFormatPattern<br/>individual_analyses: list[IndividualAnalysis]<br/>improvements: list[int]"]
    end
    
    Names --> Analyze["BatchAnalysisService<br/>.analyze_name_batch()"]
    Analyze --> IA
    Analyze --> BFP
    IA --> PC
    IA --> BPR
    BFP --> BPR
    BPR --> Results["list[ParseResult]<br/>One per input name"]
    
    style BFP fill:#fff4e1
    style IA fill:#e1f5ff
    style BPR fill:#e8f5e9
```

**Batch Processing Flow:**

1. **Individual Analysis**: Each name generates multiple `ParseCandidate` objects with scores
2. **Pattern Detection**: `BatchFormatPattern` identifies dominant format (surname-first vs given-first)
3. **Result Assembly**: `BatchParseResult` combines individual results with pattern metadata
4. **Improvement Tracking**: `improvements` field lists indices where batch context changed the parse

**NameFormat Enum:**

| Value | Meaning | Example |
|-------|---------|---------|
| `SURNAME_FIRST` | Chinese style ordering | "Zhang Wei" |
| `GIVEN_FIRST` | Western style ordering | "Wei Zhang" |
| `MIXED` | No clear pattern | Mixed list |

**Sources:** [sinonym/coretypes/results.py:147-192](), [sinonym/services/batch_analysis.py:1-200]()

## Configuration Data Flow

Configuration data flows through the system via the `ServiceContext` pattern:

```mermaid
graph LR
    subgraph "Configuration Source"
        Config["ChineseNameConfig<br/>.create_default()"]
    end
    
    subgraph "Data Loading"
        Data["NameDataStructures<br/>surnames: dict<br/>given_names: dict<br/>compound_variants: dict<br/>ethnicity_markers: dict"]
        
        DataInit["DataInitializationService<br/>.initialize_data_structures()"]
    end
    
    subgraph "Service Context Bundle"
        SC["ServiceContext<br/>config: ChineseNameConfig<br/>normalizer: NormalizationService<br/>data: NameDataStructures"]
    end
    
    subgraph "Services"
        Eth["EthnicityClassificationService(context)"]
        Parse["NameParsingService(context)"]
        Format["NameFormattingService(context)"]
    end
    
    Config --> DataInit
    Config --> SC
    DataInit --> Data
    Data --> SC
    
    SC --> Eth
    SC --> Parse
    SC --> Format
    
    style Config fill:#fff4e1
    style SC fill:#e1f5ff
    style Data fill:#e8f5e9
```

**ServiceContext Benefits:**

- **Reduced Constructor Complexity**: Services receive one bundled context instead of three separate parameters
- **Consistent Dependencies**: All context-dependent services have the same foundational data
- **Testing Simplification**: Mock the context once, use across all services

**Sources:** [sinonym/services/context.py:1-50](), [sinonym/detector.py:193-242]()

## Thread Safety and Immutability Guarantees

All core types are designed for safe concurrent access:

| Type | Thread Safety Mechanism | Mutation Prevention |
|------|------------------------|---------------------|
| `ParseResult` | `@dataclass(frozen=True)` | Cannot reassign fields after construction |
| `ParsedName` | `@dataclass(frozen=True)` | Immutable surname/given name components |
| `NormalizedInput` | `@dataclass(frozen=True)` | Read-only token lists and mappings |
| `CompoundMetadata` | `@dataclass(frozen=True)` | Format metadata cannot change |
| `NameDataStructures` | Loaded once at init | Shared read-only across threads |
| `ChineseNameConfig` | Static configuration | No mutable state |

**Concurrent Processing Example:**

```python
detector = ChineseNameDetector()  # Initialize once

# Safe to call from multiple threads
from concurrent.futures import ThreadPoolExecutor

names = ["Zhang Wei", "Li Ming", "Wang Xiaoli"]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(detector.normalize_name, names))
# All ParseResult objects are immutable and thread-safe
```

**Sources:** [sinonym/coretypes/results.py:1-192](), [pyproject.toml:10-35]()

## Type System Summary Table

| Type Category | Types | Purpose | Frozen |
|--------------|-------|---------|--------|
| Result Containers | `ParseResult` | Either-like success/failure wrapper | ✓ |
| Structured Output | `ParsedName` | Name components with dual views | ✓ |
| Intermediate Data | `NormalizedInput`, `CompoundMetadata` | Pipeline state between stages | ✓ |
| Batch Analysis | `BatchParseResult`, `BatchFormatPattern`, `IndividualAnalysis`, `ParseCandidate` | Multi-name processing metadata | ✓ |
| Enumerations | `NameFormat` | Format classification | N/A |
| Statistics | `CacheInfo` | Cache metrics | ✓ |

All types follow immutable design principles, enabling safe concurrent processing and functional composition patterns suitable for both Python and Scala consumers.

**Sources:** [sinonym/coretypes/results.py:1-192](), [sinonym/services/normalization.py:1-80]()

---

