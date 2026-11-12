<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/s2orc-doc2json · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [doc2json/grobid2json/__init__.py](doc2json/grobid2json/__init__.py)
- [doc2json/grobid2json/grobid/__init__.py](doc2json/grobid2json/grobid/__init__.py)
- [doc2json/spp2json/spp/__init__.py](doc2json/spp2json/spp/__init__.py)
- [doc2json/tex2json/__init__.py](doc2json/tex2json/__init__.py)

</details>



The s2orc-doc2json repository provides tools to convert scientific papers from various formats (PDF, LaTeX, JATS XML) into a standardized JSON format used by the Semantic Scholar Open Research Corpus (S2ORC). This document introduces the repository's purpose, main components, and high-level architecture.

For detailed information about repository structure, see [Repository Structure](#1.1). For installation instructions, see [Installation and Setup](#1.2). For information about the S2ORC data format, see [S2ORC Data Model](#2).

## Purpose and Scope

The s2orc-doc2json system serves as a document conversion framework for the S2ORC project, extracting structured information from scientific papers into a unified JSON schema. This schema is also used in the COVID-19 Open Research Dataset (CORD-19) project.

The repository supports multiple document formats through specialized conversion pipelines:
- **grobid2json**: Converts PDFs to JSON using Grobid
- **tex2json**: Processes LaTeX documents (primarily from arXiv)
- **jats2json**: Processes JATS XML files (primarily from PubMed Central)
- **spp2json**: Alternative PDF processing using ScienceParsePlus

A web interface (Flask application) is also provided for easy document conversion through a browser or API calls.

Sources: [README.md:1-9]()

## System Architecture Overview

```mermaid
graph TD
    subgraph "Input Formats"
        PDF["PDF Files"]
        LaTeX["LaTeX Files (.gz)"]
        JATS["JATS XML Files (.nxml)"]
    end

    subgraph "Processing Pipelines"
        Grobid2json["process_pdf.py"]
        Tex2json["process_tex.py"]
        Jats2json["process_jats.py"]
        Spp2json["spp2json"]
    end

    subgraph "External Tools"
        Grobid["Grobid Service (Port 8070)"]
        Latexpand["latexpand"]
        Tralics["tralics"]
        SPP["ScienceParsePlus"]
    end

    subgraph "Web Interface"
        Flask["app.py (Flask App)"]
    end

    subgraph "Output Format"
        S2ORC["S2ORC JSON (s2orc.py)"]
    end

    PDF --> Grobid2json
    PDF --> Spp2json
    LaTeX --> Tex2json
    JATS --> Jats2json
    
    Grobid2json --> Grobid
    Grobid --> Grobid2json
    
    Tex2json --> Latexpand
    Tex2json --> Tralics
    Tex2json --> Grobid
    
    Spp2json --> SPP
    
    Grobid2json --> S2ORC
    Tex2json --> S2ORC
    Jats2json --> S2ORC
    Spp2json --> S2ORC
    
    PDF --> Flask
    LaTeX --> Flask
    JATS --> Flask
    Flask --> Grobid2json
    Flask --> Tex2json
    Flask --> Jats2json
```

Sources: [README.md:27-45](), [README.md:65-82](), [README.md:84-92](), [README.md:98-120]()

## Document Conversion Pipelines

### PDF Processing with Grobid

The primary PDF processing pipeline uses Grobid to extract structured information from PDFs:

```mermaid
flowchart TD
    PDF["PDF File"] --> ProcessPDF["process_pdf.py::process_pdf()"]
    ProcessPDF --> GrobidClient["grobid_client.py::process_pdf()"]
    GrobidClient --> TEIXML["TEI XML Output"]
    TEIXML --> ConvertTEI["teixml_to_s2orc.py::convert_tei_xml_to_s2orc_json()"]
    ConvertTEI --> S2ORCJSON["S2ORC JSON"]
```

Sources: [README.md:27-64]()

### LaTeX Processing

The LaTeX processing pipeline handles compressed LaTeX files, typically from arXiv:

```mermaid
flowchart TD
    LaTeX[".gz LaTeX File"] --> ProcessTex["process_tex.py::process_tex()"]
    ProcessTex --> ExtractLatex["extract_latex()"]
    ExtractLatex --> NormalizeLatex["normalize_latex()"]
    NormalizeLatex --> LatexToXml["norm_latex_to_xml() via tralics"]
    LatexToXml --> XML["XML Output"]
    XML --> ConvertXML["tex_to_s2orc.py::convert_latex_xml_to_s2orc_json()"]
    ConvertXML --> S2ORCJSON["S2ORC JSON"]
    
    subgraph "Citation Processing"
        ConvertXML --> GrobidClient["grobid_client.py"]
        GrobidClient --> StructuredCitations["Structured Citations"]
        StructuredCitations --> S2ORCJSON
    end
```

Sources: [README.md:65-82]()

### JATS XML Processing

The JATS XML processing pipeline handles PubMed Central XML files:

```mermaid
flowchart TD
    JATS["JATS XML (.nxml)"] --> ProcessJATS["process_jats.py::process_jats_file()"]
    ProcessJATS --> ConvertJATS["jats_to_s2orc.py::convert_jats_to_s2orc_json()"]
    ConvertJATS --> S2ORCJSON["S2ORC JSON"]
```

Sources: [README.md:84-92]()

## Web Interface

The repository includes a Flask web application that provides an easy-to-use interface for document conversion:

```mermaid
flowchart TD
    subgraph "Client"
        Browser["Web Browser"] -->|"Access localhost:8080"| WebForm["Web Form (/)"]
        CURL["cURL or API Client"] -->|"POST Request"| APIEndpoint["/"]
    end
    
    subgraph "Flask App (app.py)"
        WebForm --> UploadFile["upload_file()"]
        APIEndpoint --> UploadFile
        UploadFile --> FileTypeCheck{"File type?"}
        FileTypeCheck -->|".pdf"| ProcessPDF["process_pdf_stream()"]
        FileTypeCheck -->|".gz"| ProcessTEX["process_tex_stream()"]
        FileTypeCheck -->|".nxml"| ProcessJATS["process_jats_stream()"]
    end
    
    ProcessPDF --> Grobid2json["grobid2json.process_pdf"]
    ProcessTEX --> Tex2json["tex2json.process_tex"]
    ProcessJATS --> Jats2json["jats2json.process_jats"]
    
    Grobid2json --> S2ORCJSON["S2ORC JSON"]
    Tex2json --> S2ORCJSON
    Jats2json --> S2ORCJSON
    
    S2ORCJSON --> JSONResponse["JSON Response"]
    JSONResponse --> Browser
    JSONResponse --> CURL
```

Sources: [README.md:98-120]()

## S2ORC JSON Data Model

The repository converts scientific papers into a standardized JSON format defined in `s2orc.py`. This format captures:

- Paper metadata (title, authors, year, venue)
- Abstract paragraphs
- Body text paragraphs with citations, references, and equations
- Bibliography entries
- Reference entries for figures, tables, and equations

```mermaid
classDiagram
    class Paper {
        +string paper_id
        +string pdf_hash
        +Metadata metadata
        +List~Paragraph~ abstract
        +List~Paragraph~ body_text
        +List~Paragraph~ back_matter
        +Dict~string, BibEntry~ bib_entries
        +Dict~string, RefEntry~ ref_entries
    }
    
    class Metadata {
        +string title
        +List~Author~ authors
        +string year
        +string venue
    }
    
    class Paragraph {
        +string text
        +List cite_spans
        +List ref_spans
        +List eq_spans
        +List section
    }
    
    class BibEntry {
        +string title
        +List authors
        +string year
        +string venue
    }
    
    Paper "1" *-- "1" Metadata
    Paper "1" *-- "many" Paragraph
    Paper "1" *-- "many" BibEntry
    Paper "1" *-- "many" RefEntry
```

For detailed information on the S2ORC data model, see [S2ORC Data Model](#2).

Sources: [README.md:5-7](), [README.md:93-96]()

## Key Dependencies

The s2orc-doc2json system relies on several external tools and libraries:

| Pipeline | Input Format | External Dependencies | Purpose |
|----------|-------------|------------------------|---------|
| grobid2json | PDF | Grobid (Java) | Extract structured information from PDFs |
| tex2json | LaTeX (.gz) | latexpand, tralics, Grobid | Process LaTeX files and extract citations |
| jats2json | JATS XML (.nxml) | None | Process JATS XML from PubMed Central |
| spp2json | PDF | ScienceParsePlus | Alternative PDF processor |

Grobid (version 0.7.3) runs as a service on port 8070 and is a critical component for both PDF and LaTeX processing. For LaTeX processing, `latexpand` and `tralics` are required to expand and convert LaTeX to XML.

Sources: [README.md:31-51](), [README.md:65-71]()

## Summary

The s2orc-doc2json repository provides a comprehensive framework for converting scientific papers from different formats into a standardized JSON format. By supporting multiple input formats and providing both command-line tools and a web interface, the system enables efficient processing of scientific literature for large-scale corpus creation and analysis.

The standardized JSON format facilitates downstream tasks such as information extraction, citation network analysis, and knowledge discovery across the scientific literature, supporting the broader goals of the S2ORC project.

Sources: [README.md:1-9](), [README.md:123-137]()

---

