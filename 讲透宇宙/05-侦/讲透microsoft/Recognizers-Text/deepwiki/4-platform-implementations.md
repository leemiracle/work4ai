<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Recognizers-Text · page 4 Platform Implementations · fetched 2026-10-26 -->

# Platform Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.NET/Microsoft.Recognizers.Definitions.Common/Swedish/QuotedTextDefinitions.cs](.NET/Microsoft.Recognizers.Definitions.Common/Swedish/QuotedTextDefinitions.cs)
- [.NET/Microsoft.Recognizers.Definitions.Common/packages.config](.NET/Microsoft.Recognizers.Definitions.Common/packages.config)
- [.NET/Microsoft.Recognizers.Text.NumberWithUnit/Japanese/Extractors/TemperatureExtractorConfiguration.cs](.NET/Microsoft.Recognizers.Text.NumberWithUnit/Japanese/Extractors/TemperatureExtractorConfiguration.cs)
- [.NET/Microsoft.Recognizers.Text.NumberWithUnit/Japanese/Parsers/TemperatureParserConfiguration.cs](.NET/Microsoft.Recognizers.Text.NumberWithUnit/Japanese/Parsers/TemperatureParserConfiguration.cs)
- [Java/README.md](Java/README.md)
- [Java/libraries/recognizers-text-date-time/pom.xml](Java/libraries/recognizers-text-date-time/pom.xml)
- [Java/libraries/recognizers-text/src/main/java/com/microsoft/recognizers/text/utilities/StringUtility.java](Java/libraries/recognizers-text/src/main/java/com/microsoft/recognizers/text/utilities/StringUtility.java)
- [Java/libraries/resource-generator/pom.xml](Java/libraries/resource-generator/pom.xml)
- [Java/linting-excluded-files.xml](Java/linting-excluded-files.xml)
- [Java/linting-rules.xml](Java/linting-rules.xml)
- [Java/pom.xml](Java/pom.xml)
- [Java/samples/simple-console/pom.xml](Java/samples/simple-console/pom.xml)
- [Java/samples/simple-console/src/main/java/com/microsoft/recognizers/text/samples/simpleconsole/Sample.java](Java/samples/simple-console/src/main/java/com/microsoft/recognizers/text/samples/simpleconsole/Sample.java)
- [Java/tests/pom.xml](Java/tests/pom.xml)
- [JavaScript/lerna.json](JavaScript/lerna.json)
- [JavaScript/package-lock.json](JavaScript/package-lock.json)
- [JavaScript/package.json](JavaScript/package.json)
- [JavaScript/packages/datatypes-date-time/package-lock.json](JavaScript/packages/datatypes-date-time/package-lock.json)
- [JavaScript/packages/datatypes-date-time/package.json](JavaScript/packages/datatypes-date-time/package.json)
- [JavaScript/packages/recognizers-choice/package-lock.json](JavaScript/packages/recognizers-choice/package-lock.json)
- [JavaScript/packages/recognizers-choice/package.json](JavaScript/packages/recognizers-choice/package.json)
- [JavaScript/packages/recognizers-date-time/package-lock.json](JavaScript/packages/recognizers-date-time/package-lock.json)
- [JavaScript/packages/recognizers-date-time/package.json](JavaScript/packages/recognizers-date-time/package.json)
- [JavaScript/packages/recognizers-number-with-unit/package-lock.json](JavaScript/packages/recognizers-number-with-unit/package-lock.json)
- [JavaScript/packages/recognizers-number-with-unit/package.json](JavaScript/packages/recognizers-number-with-unit/package.json)
- [JavaScript/packages/recognizers-number/package-lock.json](JavaScript/packages/recognizers-number/package-lock.json)
- [JavaScript/packages/recognizers-number/package.json](JavaScript/packages/recognizers-number/package.json)
- [JavaScript/packages/recognizers-sequence/package.json](JavaScript/packages/recognizers-sequence/package.json)
- [JavaScript/packages/recognizers-text-suite/package.json](JavaScript/packages/recognizers-text-suite/package.json)
- [JavaScript/packages/recognizers-text/package.json](JavaScript/packages/recognizers-text/package.json)
- [Python/.pre-commit-config.yaml](Python/.pre-commit-config.yaml)
- [Python/build.ci.cmd](Python/build.ci.cmd)
- [Python/build.sh](Python/build.sh)
- [Python/libraries/recognizers-choice/recognizers_choice/choice/english/__init__.py](Python/libraries/recognizers-choice/recognizers_choice/choice/english/__init__.py)
- [Python/libraries/recognizers-choice/recognizers_choice/resources/__init__.py](Python/libraries/recognizers-choice/recognizers_choice/resources/__init__.py)
- [Python/libraries/recognizers-choice/resource-definitions.json](Python/libraries/recognizers-choice/resource-definitions.json)
- [Python/libraries/recognizers-choice/setup.py](Python/libraries/recognizers-choice/setup.py)
- [Python/libraries/recognizers-text/recognizers_text/parser.py](Python/libraries/recognizers-text/recognizers_text/parser.py)
- [Python/requirements.txt](Python/requirements.txt)
- [Python/setup.py](Python/setup.py)
- [Python/tests/requirements.txt](Python/tests/requirements.txt)
- [README.md](README.md)
- [Script/Utils/countNotSupportedCases.py](Script/Utils/countNotSupportedCases.py)
- [Script/Utils/deleteNotSupportedPlatform.py](Script/Utils/deleteNotSupportedPlatform.py)
- [Script/Utils/getNotSupportedInput.py](Script/Utils/getNotSupportedInput.py)

</details>



This document covers how Microsoft Recognizers Text is implemented across four different platforms (.NET, JavaScript, Python, and Java) while maintaining consistent APIs and shared recognition logic. It details the platform-specific packaging, build processes, and resource generation systems that enable cross-platform functionality.

For information about the core recognition algorithms and entity types, see [Entity Recognition Domains](#2). For language-specific pattern definitions, see [Language-Specific Implementations](#3).

## Platform Architecture Overview

Microsoft Recognizers Text implements a hub-and-spoke architecture where .NET serves as the primary platform, with contributions and improvements propagating to JavaScript, Python, and Java implementations.

```mermaid
graph TB
    subgraph "Core Pattern System"
        YAMLPatterns["YAML Pattern Files<br/>Patterns/*/"]
        Specs["Test Specifications<br/>Specs/*/"]
    end
    
    subgraph "Primary Platform"
        DotNet[".NET Implementation<br/>Microsoft.Recognizers.Text.*<br/>NuGet Packages"]
        T4Templates["T4 Templates<br/>Code Generation"]
    end
    
    subgraph "Secondary Platforms"
        JavaScript["JavaScript/TypeScript<br/>@microsoft/recognizers-text-*<br/>NPM Packages"]
        Python["Python<br/>recognizers-text-*<br/>PyPI Packages"]
        Java["Java<br/>com.microsoft.recognizers.text.*<br/>Maven Packages"]
    end
    
    subgraph "Resource Generation"
        JSResourceGen["resource-generator<br/>TypeScript"]
        PyResourceGen["resource-generator<br/>Python"]
        JavaResourceGen["resource-generator<br/>Java Maven Plugin"]
    end
    
    subgraph "Package Distribution"
        NuGet["NuGet.org<br/>Microsoft.Recognizers.*"]
        NPM["npmjs.com<br/>@microsoft/recognizers-*"]
        PyPI["PyPI.org<br/>recognizers-text-*"]
        Maven["Maven Central<br/>com.microsoft.recognizers.*"]
    end
    
    YAMLPatterns --> T4Templates
    YAMLPatterns --> JSResourceGen
    YAMLPatterns --> PyResourceGen
    YAMLPatterns --> JavaResourceGen
    
    T4Templates --> DotNet
    JSResourceGen --> JavaScript
    PyResourceGen --> Python
    JavaResourceGen --> Java
    
    DotNet --> NuGet
    JavaScript --> NPM
    Python --> PyPI
    Java --> Maven
    
    DotNet -.->|"Contributions<br/>Propagate"| JavaScript
    DotNet -.->|"Contributions<br/>Propagate"| Python
    DotNet -.->|"Contributions<br/>Propagate"| Java
```

Sources: [README.md:12-21](), [JavaScript/package.json:1-105](), [Java/pom.xml:1-60](), [Python/build.ci.cmd:1-73]()

## Cross-Platform Resource Generation

Each platform implements its own resource generation system to convert YAML pattern definitions into platform-specific code:

```mermaid
graph LR
    subgraph "Pattern Sources"
        EnglishYAML["English-DateTime.yaml<br/>English-Numbers.yaml<br/>English-Choice.yaml"]
        OtherYAML["Spanish-*.yaml<br/>Chinese-*.yaml<br/>German-*.yaml"]
    end
    
    subgraph "Resource Generators"
        DotNetGen["T4 Templates<br/>.NET Framework"]
        JSGen["TypeScript Generator<br/>resource-generator/"]
        PyGen["Python Generator<br/>index.py"]
        JavaGen["ResourcesGenerator.java<br/>Maven Plugin"]
    end
    
    subgraph "Generated Resources"
        DotNetRes["*Definitions.cs<br/>Microsoft.Recognizers.Definitions.*"]
        JSRes["*.ts Resource Files<br/>packages/*/src/resources/"]
        PyRes["*_*.py Resource Files<br/>*/resources/"]
        JavaRes["*.java Resource Files<br/>*/src/main/java/*/resources/"]
    end
    
    EnglishYAML --> DotNetGen
    EnglishYAML --> JSGen
    EnglishYAML --> PyGen
    EnglishYAML --> JavaGen
    
    OtherYAML --> DotNetGen
    OtherYAML --> JSGen
    OtherYAML --> PyGen
    OtherYAML --> JavaGen
    
    DotNetGen --> DotNetRes
    JSGen --> JSRes
    PyGen --> PyRes
    JavaGen --> JavaRes
```

Sources: [JavaScript/packages/recognizers-number/package.json:29](), [Python/build.ci.cmd:18-25](), [Java/libraries/resource-generator/pom.xml:58-66]()

## JavaScript/TypeScript Implementation

The JavaScript implementation uses a monorepo structure managed by Lerna with individual NPM packages for each recognition domain.

### Package Structure

| Package | NPM Name | Purpose |
|---------|----------|---------|
| Base | `@microsoft/recognizers-text` | Core interfaces and utilities |
| Numbers | `@microsoft/recognizers-text-number` | Number recognition |
| DateTime | `@microsoft/recognizers-text-date-time` | Date/time recognition |
| NumberWithUnit | `@microsoft/recognizers-text-number-with-unit` | Currency, dimensions, etc. |
| Sequence | `@microsoft/recognizers-text-sequence` | Phone numbers, URLs, emails |
| Choice | `@microsoft/recognizers-text-choice` | Boolean choices |
| Suite | `@microsoft/recognizers-text-suite` | All recognizers bundled |
| Timex | `@microsoft/recognizers-text-data-types-timex-expression` | TIMEX data types |

### Build Process

The JavaScript build process follows this sequence for each package:

```mermaid
graph TB
    ResourceGen["npm run build-resources<br/>ts-node resource-generator/"]
    CleanBuild["npm run clean-build<br/>rimraf dist && rimraf compiled"]
    TypeScript["tsc<br/>TypeScript Compilation"]
    Rollup["rollup -c<br/>Bundle Generation"]
    
    ResourceGen --> CleanBuild
    CleanBuild --> TypeScript
    TypeScript --> Rollup
    
    subgraph "Output Artifacts"
        UMD["*.umd.js<br/>Universal Module"]
        ES5["*.es5.js<br/>ES5 Module"]
        Browser["*.browser.js<br/>Browser Bundle"]
        Types["*.d.ts<br/>TypeScript Definitions"]
    end
    
    Rollup --> UMD
    Rollup --> ES5
    Rollup --> Browser
    TypeScript --> Types
```

Sources: [JavaScript/packages/recognizers-number/package.json:28-32](), [JavaScript/packages/recognizers-text-suite/package.json:30-33](), [JavaScript/lerna.json:1-9]()

## Python Implementation

The Python implementation distributes packages via PyPI with a setup.py-based build system and pytest for testing.

### Package Structure and Dependencies

```mermaid
graph TB
    subgraph "Core Packages"
        RecognizersText["recognizers-text<br/>Base classes and interfaces"]
        RecognizersNumber["recognizers-text-number<br/>Number recognition"]
        RecognizersChoice["recognizers-text-choice<br/>Boolean recognition"]
    end
    
    subgraph "Advanced Packages"
        RecognizersNumberWithUnit["recognizers-text-number-with-unit<br/>Currency, dimensions"]
        RecognizersDateTime["recognizers-text-date-time<br/>DateTime recognition"]
        RecognizersSequence["recognizers-text-sequence<br/>Sequence recognition"]
    end
    
    subgraph "Meta Packages"
        RecognizersSuite["recognizers-text-suite<br/>All recognizers bundled"]
        TimexExpression["datatypes-timex-expression<br/>TIMEX support"]
    end
    
    RecognizersNumber --> RecognizersText
    RecognizersChoice --> RecognizersText
    RecognizersNumberWithUnit --> RecognizersNumber
    RecognizersDateTime --> RecognizersNumber
    RecognizersDateTime --> RecognizersNumberWithUnit
    RecognizersSequence --> RecognizersText
    RecognizersSuite --> RecognizersDateTime
    RecognizersSuite --> RecognizersSequence
    RecognizersSuite --> RecognizersChoice
```

### Build and Test Process

The Python build process uses pip for dependency management and pytest for testing:

```mermaid
graph TB
    ResourceGenPy["python index.py<br/>Generate resources from YAML"]
    InstallDeps["pip install -e ./libraries/*/"]
    RunTests["pytest --tb=line<br/>Execute test suite"]
    CreatePackages["CreateAllPackages.cmd<br/>Package distribution"]
    
    ResourceGenPy --> InstallDeps
    InstallDeps --> RunTests
    RunTests --> CreatePackages
    
    subgraph "Quality Checks"
        Flake8["flake8 . --config=./setup.cfg<br/>PEP8 validation"]
        PreCommit["pre-commit install<br/>Git hooks"]
    end
    
    InstallDeps --> Flake8
    Flake8 --> RunTests
```

Sources: [Python/build.ci.cmd:1-73](), [Python/build.sh:1-43](), [Python/libraries/recognizers-choice/setup.py:1-38]()

## Java Implementation

The Java implementation uses Maven for build management and follows standard Java packaging conventions.

### Maven Module Structure

```mermaid
graph TB
    subgraph "Parent POM"
        ParentPOM["recognizers-text-java<br/>com.microsoft.recognizers.text<br/>pom.xml"]
    end
    
    subgraph "Core Libraries"
        RecognizersTextJava["recognizers-text<br/>com.microsoft.recognizers.text"]
        RecognizersNumber["recognizers-text-number<br/>com.microsoft.recognizers.text.number"]
        RecognizersDateTime["recognizers-text-date-time<br/>com.microsoft.recognizers.text.datetime"]
    end
    
    subgraph "Extended Libraries"
        RecognizersNumberWithUnit["recognizers-text-number-with-unit<br/>com.microsoft.recognizers.text.numberwithunit"]
        RecognizersSequence["recognizers-text-sequence<br/>com.microsoft.recognizers.text.sequence"]
        RecognizersChoice["recognizers-text-choice<br/>com.microsoft.recognizers.text.choice"]
        TimexExpression["recognizers-text-datatypes-timex-expression<br/>com.microsoft.recognizers.text.datatypes.timex.expression"]
    end
    
    subgraph "Build Tools"
        ResourceGenerator["resource-generator<br/>com.microsoft.recognizers.text.resourcegenerator"]
    end
    
    subgraph "Testing"
        Tests["tests<br/>com.microsoft.recognizers.text.tests"]
        Samples["simple-console<br/>com.microsoft.recognizers.text.samples.simpleconsole"]
    end
    
    ParentPOM --> RecognizersTextJava
    ParentPOM --> ResourceGenerator
    RecognizersTextJava --> RecognizersNumber
    RecognizersNumber --> RecognizersNumberWithUnit
    RecognizersNumber --> RecognizersDateTime
    RecognizersTextJava --> RecognizersSequence
    RecognizersTextJava --> RecognizersChoice
    RecognizersDateTime --> TimexExpression
```

### Maven Build Process

The Java build integrates resource generation with standard Maven lifecycle phases:

```mermaid
graph TB
    ResourceGenJava["exec:java<br/>ResourcesGenerator.main()"]
    Validate["validate<br/>CheckStyle linting"]
    Compile["compile<br/>Java source compilation"]
    Test["test<br/>JUnit test execution"]
    Package["package<br/>JAR artifact creation"]
    Install["install<br/>Local .m2 repository"]
    
    ResourceGenJava --> Validate
    Validate --> Compile
    Compile --> Test
    Test --> Package
    Package --> Install
    
    subgraph "Quality Gates"
        CheckStyle["CheckStyle Plugin<br/>linting-rules.xml"]
        JUnit["JUnit 4.13.1<br/>Test framework"]
    end
    
    Validate --> CheckStyle
    Test --> JUnit
```

Sources: [Java/pom.xml:16-27](), [Java/libraries/resource-generator/pom.xml:57-67](), [Java/samples/simple-console/pom.xml:1-110](), [Java/tests/pom.xml:1-114]()

## API Consistency Across Platforms

All platforms implement the same core recognition API pattern with platform-specific adaptations:

### Core Recognition Methods

| Recognition Type | .NET | JavaScript | Python | Java |
|------------------|------|------------|---------|------|
| Numbers | `NumberRecognizer.RecognizeNumber()` | `NumberRecognizer.recognizeNumber()` | `recognize_number()` | `NumberRecognizer.recognizeNumber()` |
| DateTime | `DateTimeRecognizer.RecognizeDateTime()` | `DateTimeRecognizer.recognizeDateTime()` | `recognize_datetime()` | `DateTimeRecognizer.recognizeDateTime()` |
| Currency | `NumberWithUnitRecognizer.RecognizeCurrency()` | `NumberWithUnitRecognizer.recognizeCurrency()` | `recognize_currency()` | `NumberWithUnitRecognizer.recognizeCurrency()` |

### Model Result Structure

Each platform returns results using a consistent `ModelResult` structure containing:

- `start`: Starting position in input text
- `length`: Length of recognized text
- `text`: Original recognized text
- `typeName`: Type of entity recognized
- `resolution`: Parsed and normalized values

```mermaid
graph LR
    subgraph "Input Processing"
        InputText["Input Text<br/>'I need 5 dollars tomorrow'"]
    end
    
    subgraph "Recognition Pipeline"
        Extractor["Extractor<br/>Pattern matching"]
        Parser["Parser<br/>Value resolution"]
        Model["Model<br/>Result formatting"]
    end
    
    subgraph "ModelResult Output"
        Result1["Currency: '$5'<br/>start: 7, length: 9"]
        Result2["DateTime: 'tomorrow'<br/>start: 17, length: 8"]
    end
    
    InputText --> Extractor
    Extractor --> Parser
    Parser --> Model
    Model --> Result1
    Model --> Result2
```

Sources: [Java/samples/simple-console/src/main/java/com/microsoft/recognizers/text/samples/simpleconsole/Sample.java:66-132](), [Python/libraries/recognizers-text/recognizers_text/parser.py:9-26]()

---

