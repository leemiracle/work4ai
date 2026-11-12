<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/RAG-Anything · page 12 Troubleshooting · fetched 2026-11-09 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/multimodal_rag_failure_modes.md](docs/multimodal_rag_failure_modes.md)
- [raganything/asset_urls.py](raganything/asset_urls.py)
- [raganything/parser.py](raganything/parser.py)
- [tests/test_asset_urls.py](tests/test_asset_urls.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



This page provides an overview of common issues encountered when using RAG-Anything and guidance for diagnosing and resolving them. The troubleshooting process is organized into three main categories: parser installation issues, document processing errors, and query/storage problems.

For detailed troubleshooting of specific issues, see:
- **Parser Installation Issues**: See [Parser Installation Issues](#12.1)
- **Processing Errors**: See [Processing Errors](#12.2)
- **Query and Storage Issues**: See [Query and Storage Issues](#12.3)

For initial setup guidance, see [Installation](#2.1) and [Environment Configuration](#2.3).

---

## Error Propagation Architecture

Understanding where errors originate in the system helps diagnose problems efficiently. The following diagram shows the major error sources and their propagation paths through the RAG-Anything pipeline.

```mermaid
graph TD
    subgraph "User Input Layer"
        DOC_INPUT["file_path parameter"]
        CONFIG_INPUT["RAGAnythingConfig object"]
        ENV_INPUT[".env file variables"]
    end
    
    subgraph "Validation Layer - parser.py"
        FILE_CHECK["Path.exists() check"]
        EXT_CHECK["Extension validation<br/>OFFICE_FORMATS / IMAGE_FORMATS / TEXT_FORMATS"]
        CONFIG_CHECK["config.parser validation<br/>get_parser()"]
    end
    
    subgraph "Parser Layer - parser.py"
        GET_PARSER["get_parser(parser_type)<br/>line 2165"]
        MINERU_PARSER["MineruParser()<br/>line 597"]
        DOCLING_PARSER["DoclingParser()<br/>line 1343"]
        PADDLEOCR_PARSER["PaddleOCRParser()<br/>line 1837"]
        
        FORMAT_CONVERT["Format conversion methods"]
        CONVERT_OFFICE["convert_office_to_pdf()<br/>line 194"]
        CONVERT_TEXT["convert_text_to_pdf()<br/>line 334"]
        CONVERT_IMAGE["PIL Image.open() + convert<br/>line 1109"]
    end
    
    subgraph "External Dependencies"
        MINERU_CMD["mineru CLI subprocess<br/>subprocess.Popen()"]
        DOCLING_API["Docling Python API<br/>DocumentConverter"]
        LIBREOFFICE["soffice / libreoffice<br/>subprocess.run()"]
        PIL_LIB["from PIL import Image<br/>Image.open()"]
        REPORTLAB["from reportlab.platypus<br/>SimpleDocTemplate"]
        PADDLEOCR_LIB["from paddleocr import PaddleOCR"]
        PYPDFIUM["import pypdfium2 as pdfium"]
    end
    
    subgraph "Error Types"
        FILE_ERR["FileNotFoundError"]
        VALUE_ERR["ValueError"]
        RUNTIME_ERR["RuntimeError"]
        MINERU_ERR["MineruExecutionError<br/>line 57"]
        IMPORT_ERR["ImportError"]
    end
    
    DOC_INPUT --> FILE_CHECK
    CONFIG_INPUT --> CONFIG_CHECK
    
    FILE_CHECK -->|"not exists"| FILE_ERR
    FILE_CHECK -->|"exists"| EXT_CHECK
    
    EXT_CHECK -->|"valid"| GET_PARSER
    EXT_CHECK -->|"invalid"| VALUE_ERR
    
    CONFIG_CHECK -->|"invalid"| VALUE_ERR
    CONFIG_CHECK -->|"valid"| GET_PARSER
    
    GET_PARSER --> MINERU_PARSER
    GET_PARSER --> DOCLING_PARSER
    GET_PARSER --> PADDLEOCR_PARSER
    
    MINERU_PARSER --> FORMAT_CONVERT
    DOCLING_PARSER --> FORMAT_CONVERT
    PADDLEOCR_PARSER --> FORMAT_CONVERT
    
    FORMAT_CONVERT --> CONVERT_OFFICE
    FORMAT_CONVERT --> CONVERT_TEXT
    FORMAT_CONVERT --> CONVERT_IMAGE
    
    CONVERT_OFFICE --> LIBREOFFICE
    CONVERT_TEXT --> REPORTLAB
    CONVERT_IMAGE --> PIL_LIB
    
    MINERU_PARSER --> MINERU_CMD
    DOCLING_PARSER --> DOCLING_API
    PADDLEOCR_PARSER --> PADDLEOCR_LIB
    PADDLEOCR_PARSER --> PYPDFIUM
    
    LIBREOFFICE -->|"command not found"| RUNTIME_ERR
    REPORTLAB -->|"not installed"| IMPORT_ERR
    PIL_LIB -->|"not installed"| RUNTIME_ERR
    PADDLEOCR_LIB -->|"not installed"| IMPORT_ERR
    PYPDFIUM -->|"not installed"| IMPORT_ERR
    
    MINERU_CMD -->|"exit code != 0"| MINERU_ERR
```

**Sources:** [raganything/parser.py:57-66](), [raganything/parser.py:194-228](), [raganything/parser.py:334-568](), [raganything/parser.py:597-615](), [raganything/parser.py:1343-1356](), [raganything/parser.py:1837-1847](), [raganything/parser.py:2165-2176]()

---

## Common Error Categories

The system encounters errors in three primary areas, each with distinct diagnostic approaches.

| Error Category | Typical Symptoms | Primary Source Code | Detailed Guide |
|---------------|------------------|---------------------|----------------|
| **Parser Installation** | `FileNotFoundError` for `mineru`, subprocess failures, Docling API missing | `get_parser()` [raganything/parser.py:2165-2176](), `check_installation()` [raganything/parser.py:1309-1340, 1803-1834]() | [Parser Installation Issues](#12.1) |
| **Format Dependencies** | `ImportError` for PIL/Pillow/ReportLab/PaddleOCR, LibreOffice conversion failures | `convert_office_to_pdf()` [raganything/parser.py:194-331](), `convert_text_to_pdf()` [raganything/parser.py:334-568]() | [Parser Installation Issues](#12.1) |
| **Processing Errors** | `MineruExecutionError` [raganything/parser.py:57-66](), empty `content_list`, invalid JSON output | `_run_mineru_command()` [raganything/parser.py:617-845](), `_read_output_files()` [raganything/parser.py:847-962]() | [Processing Errors](#12.2) |
| **Multimodal Failure** | OCR corruption, table structure loss, image-caption misalignment | `docs/multimodal_rag_failure_modes.md` [docs/multimodal_rag_failure_modes.md:1-85]() | [Processing Errors](#12.2) |
| **Asset URL Issues** | Images not loading in UI, path mismatch | `attach_public_media_urls()` [raganything/asset_urls.py:65-118]() | [Query and Storage Issues](#12.3) |
| **Storage Errors** | Connection timeouts, database initialization failures | LightRAG storage backends | [Query and Storage Issues](#12.3) |

**Sources:** [raganything/parser.py:57-66](), [raganything/parser.py:617-845](), [raganything/asset_urls.py:65-118](), [docs/multimodal_rag_failure_modes.md:9-72]()

---

## Diagnostic Workflow

Use this decision tree to quickly identify the appropriate troubleshooting section for your issue.

```mermaid
graph TD
    START["Encountering Error"]
    
    PHASE{"Which phase<br/>is failing?"}
    
    INSTALL_CHECK["Installation/<br/>Setup Phase"]
    PROCESS_CHECK["Document<br/>Processing Phase"]
    QUERY_CHECK["Query/<br/>Retrieval Phase"]
    
    INSTALL_TYPE{"Error type?"}
    PROCESS_TYPE{"Error type?"}
    QUERY_TYPE{"Error type?"}
    
    CMD_NOT_FOUND["Command not found:<br/>mineru/soffice"]
    DEP_MISSING["Missing dependency:<br/>PIL/ReportLab/Docling"]
    
    PARSE_FAIL["Parser execution<br/>failed"]
    CONVERT_FAIL["Format conversion<br/>failed"]
    OCR_CORRUPT["OCR/Layout<br/>corruption"]
    
    EMPTY_RESULT["Empty query<br/>results"]
    IMG_NOT_LOAD["Images not loading<br/>in UI"]
    
    GOTO_121["See 12.1:<br/>Parser Installation"]
    GOTO_122["See 12.2:<br/>Processing Errors"]
    GOTO_123["See 12.3:<br/>Query/Storage Issues"]
    
    START --> PHASE
    
    PHASE -->|Setup| INSTALL_CHECK
    PHASE -->|Processing| PROCESS_CHECK
    PHASE -->|Querying| QUERY_CHECK
    
    INSTALL_CHECK --> INSTALL_TYPE
    PROCESS_CHECK --> PROCESS_TYPE
    QUERY_CHECK --> QUERY_TYPE
    
    INSTALL_TYPE --> CMD_NOT_FOUND
    INSTALL_TYPE --> DEP_MISSING
    
    PROCESS_TYPE --> PARSE_FAIL
    PROCESS_TYPE --> CONVERT_FAIL
    PROCESS_TYPE --> OCR_CORRUPT
    
    QUERY_TYPE --> EMPTY_RESULT
    QUERY_TYPE --> IMG_NOT_LOAD
    
    CMD_NOT_FOUND --> GOTO_121
    DEP_MISSING --> GOTO_121
    
    PARSE_FAIL --> GOTO_122
    CONVERT_FAIL --> GOTO_122
    OCR_CORRUPT --> GOTO_122
    
    EMPTY_RESULT --> GOTO_123
    IMG_NOT_LOAD --> GOTO_123
```

**Sources:** [docs/multimodal_rag_failure_modes.md:1-85](), [raganything/parser.py:617-845]()

---

## Quick Diagnostic Commands

### Check Parser Installation

```python
from raganything.parser import get_parser

# Check MinerU installation
mineru_parser = get_parser("mineru")
if mineru_parser.check_installation():
    print("✅ MinerU installed properly")

# Check Docling installation (Python API check)
docling_parser = get_parser("docling")
if docling_parser.check_installation():
    print("✅ Docling installed properly")
```

The `check_installation()` method verifies parser availability:
- `MineruParser.check_installation()` [raganything/parser.py:1309-1340]() runs `mineru --version`.
- `DoclingParser.check_installation()` [raganything/parser.py:1803-1834]() checks for the `docling` package.

**Sources:** [raganything/parser.py:1309-1340](), [raganything/parser.py:1803-1834]()

### Verify Public Asset Mapping

If images are missing in your UI, verify the environment variables for asset URL mapping:

```python
import os
base = os.environ.get("RAGANYTHING_PUBLIC_ASSET_BASE_URL")
strip = os.environ.get("RAGANYTHING_PUBLIC_ASSET_STRIP_PREFIX")
print(f"Base URL: {base}, Strip Prefix: {strip}")
```

If only one is set, the system logs a warning and skips attachment [raganything/asset_urls.py:83-100]().

**Sources:** [raganything/asset_urls.py:77-100]()

---

## Subprocess Execution Monitoring (MinerU)

MinerU runs as a subprocess with real-time logging. Errors are captured via `stdout_queue` and `stderr_queue` [raganything/parser.py:745-746]().

```mermaid
graph LR
    subgraph "Main Thread"
        MAIN["_run_mineru_command()<br/>line 617"]
        POPEN["subprocess.Popen(cmd)<br/>line 742"]
        RETURN_CHECK["if return_code != 0<br/>line 824"]
    end
    
    subgraph "Worker Threads"
        THREAD_OUT["stdout_thread<br/>line 749"]
        THREAD_ERR["stderr_thread<br/>line 752"]
    end
    
    subgraph "Logging Output"
        LOG_INFO["logger.info('[MinerU] ...')<br/>line 769"]
        LOG_WARN["logger.warning('[MinerU] ...')<br/>line 779"]
        LOG_ERROR["logger.error('[MinerU] ...')<br/>line 781"]
    end
    
    MAIN --> POPEN
    POPEN --> THREAD_OUT
    POPEN --> THREAD_ERR
    THREAD_OUT --> LOG_INFO
    THREAD_ERR --> LOG_WARN
    THREAD_ERR --> LOG_ERROR
    LOG_ERROR --> RETURN_CHECK
    RETURN_CHECK -->|"Error"| RAISE["raise MineruExecutionError"]
```

**Sources:** [raganything/parser.py:731-826]()

---

## Next Steps

1. **[Parser Installation Issues](#12.1)** - Solutions for LibreOffice, MinerU, and dependency conflicts.
2. **[Processing Errors](#12.2)** - Debugging OCR corruption, table loss, and `MineruExecutionError`.
3. **[Query and Storage Issues](#12.3)** - Fixing VLM path validation, retrieval bias, and public URL mapping.

**Sources:** [docs/multimodal_rag_failure_modes.md:1-85](), [raganything/asset_urls.py:1-118]()

---

