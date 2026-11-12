<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/finepdfs · page 8 Third-Party Dependencies · fetched 2026-10-26 -->

# Third-Party Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

</details>



This document provides a comprehensive overview of all third-party dependencies used in the FinePDFs repository. It covers the major external libraries, vendored code, and their associated licenses. The focus is on dependencies that are critical to the pipeline's operation, including PDF extraction, document layout analysis, OCR, and data streaming.

For information about how models and datasets are stored and managed, see [Model Artifacts and Storage](#5). For details on the main processing pipeline and its internal logic, see [Main Processing Pipeline](#2).

---

## Purpose and Scope

This page documents:

- All major third-party libraries and vendored code included in the repository.
- The license terms under which these dependencies are used.
- The mapping between system components and their corresponding code entities.
- The location of license files and relevant upstream references.

This page does **not** cover the internal utility functions or the repository's own licensing (see the `LICENSE` file for that).

Sources:  
[THIRD_PARTY_NOTICES.md:1-29]()

---

## Summary Table of Major Third-Party Dependencies

| Dependency Name         | Code Location(s)                                   | License         | Upstream Reference / Notes                                 |
|------------------------|----------------------------------------------------|-----------------|-----------------------------------------------------------|
| Docling                | `docling_code/docling/`, `docling_code/docling-core/` | MIT             | [docling_code/docling/LICENSE](), [docling_code/docling-core/LICENSE]() |
| Docling IBM Models     | `docling_code/docling-ibm-models/`                 | See upstream    | [docling_code/docling-ibm-models/LICENSE]()               |
| Docling Eval Tooling   | `models/model_prep_code/docling_quant/docling_eval/` | MIT             | Follows Docling's MIT license                             |
| PyMuPDF                | Used in extraction utilities and Docling backends  | AGPL-3.0        | [PyMuPDF Documentation](https://pymupdf.readthedocs.io)  |
| DataTrove              | External, used for data streaming                  | Apache-2.0      | [https://github.com/huggingface/datatrove]()              |
| Other Python Packages  | Various                                            | Various         | Governed by their respective PyPI licenses                |

Sources:  
[THIRD_PARTY_NOTICES.md:1-29]()

---

## System-to-Code Mapping Diagram

**Diagram: "FinePDFs Third-Party Dependency Mapping"**

```mermaid
flowchart TD
    "Docling"["docling_code/docling/"]
    "DoclingCore"["docling_code/docling-core/"]
    "DoclingIBMModels"["docling_code/docling-ibm-models/"]
    "DoclingEval"["models/model_prep_code/docling_quant/docling_eval/"]
    "PyMuPDF"["PyMuPDF (imported in extraction utilities)"]
    "DataTrove"["datatrove (external)"]

    "PDFExtractionSystem"["blocks/extractors/docling.py"]
    "OCRProcessing"["blocks/extractors/ocr.py"]
    "MainPipeline"["run_finepdfs_pipeline.py"]

    "PDFExtractionSystem" --> "Docling"
    "PDFExtractionSystem" --> "DoclingCore"
    "PDFExtractionSystem" --> "DoclingIBMModels"
    "PDFExtractionSystem" --> "PyMuPDF"
    "PDFExtractionSystem" --> "DoclingEval"
    "OCRProcessing" --> "PyMuPDF"
    "MainPipeline" --> "DataTrove"
```

**Legend:**  
- Boxes represent code directories or files.
- Arrows indicate direct usage or import relationships.

Sources:  
[THIRD_PARTY_NOTICES.md:1-29]()

---

## Dependency Details

### Docling

- **Purpose:** PDF text and layout extraction, including advanced document structure analysis.
- **Code Locations:**  
  - `docling_code/docling/` (main library, vendored)
  - `docling_code/docling-core/` (core components, vendored)
- **License:** MIT  
- **Upstream:** Copyright (c) IBM and contributors  
- **License Files:**  
  - [docling_code/docling/LICENSE]()
  - [docling_code/docling-core/LICENSE]()

### Docling IBM Models

- **Purpose:** Pretrained models for layout and structure analysis, used by Docling.
- **Code Location:** `docling_code/docling-ibm-models/`
- **License:** See upstream license in [docling_code/docling-ibm-models/LICENSE]()

### Docling Eval Tooling

- **Purpose:** Evaluation scripts and quantization tools for Docling models.
- **Code Location:** `models/model_prep_code/docling_quant/docling_eval/`
- **License:** MIT (inherits Docling's license)

### PyMuPDF

- **Purpose:** PDF rendering and OCR support, both directly and as a backend for Docling.
- **Usage:**  
  - Imported in extraction utilities and Docling backend extensions.
- **License:** GNU Affero General Public License v3.0 (AGPL-3.0)
- **Upstream:**  
  - [PyMuPDF Documentation](https://pymupdf.readthedocs.io)
  - [PyMuPDF GitHub](https://github.com/pymupdf/PyMuPDF)

### DataTrove

- **Purpose:** High-performance data streaming and sharding for large-scale dataset processing.
- **Usage:**  
  - Pulled from [https://github.com/huggingface/datatrove]() (branch "finepdfs")
- **License:** Apache License 2.0

### Other Python Packages

- **Purpose:** Standard and third-party Python packages from PyPI.
- **License:** Governed by their respective licenses as published on PyPI.

Sources:  
[THIRD_PARTY_NOTICES.md:1-29]()

---

## License File Locations

| Component                | License File Location                                 |
|--------------------------|------------------------------------------------------|
| FinePDFs (main repo)     | [LICENSE]()                                          |
| Docling                  | [docling_code/docling/LICENSE]()                     |
| Docling Core             | [docling_code/docling-core/LICENSE]()                |
| Docling IBM Models       | [docling_code/docling-ibm-models/LICENSE]()          |

Sources:  
[THIRD_PARTY_NOTICES.md:1-29]()  
[LICENSE:1-59]()

---

## License Relationship Diagram

**Diagram: "License Relationships in FinePDFs"**

```mermaid
graph TD
    "FinePDFsRepo"["LICENSE (AGPL-3.0)"]
    "Docling"["docling_code/docling/LICENSE (MIT)"]
    "DoclingCore"["docling_code/docling-core/LICENSE (MIT)"]
    "DoclingIBMModels"["docling_code/docling-ibm-models/LICENSE (see upstream)"]
    "PyMuPDF"["PyMuPDF (AGPL-3.0)"]
    "DataTrove"["datatrove (Apache-2.0)"]

    "FinePDFsRepo" --> "Docling"
    "FinePDFsRepo" --> "DoclingCore"
    "FinePDFsRepo" --> "DoclingIBMModels"
    "FinePDFsRepo" --> "PyMuPDF"
    "FinePDFsRepo" --> "DataTrove"
```

Sources:  
[THIRD_PARTY_NOTICES.md:1-29]()  
[LICENSE:1-59]()

---

## Notes and Compliance

- All vendored code includes its original license file in the corresponding directory.
- The main repository is licensed under AGPL-3.0, which is compatible with MIT and Apache-2.0 dependencies.
- Users and contributors should review the upstream license files for any additional terms or obligations.
- For a full list of all third-party Python packages, consult your environment's `pip freeze` or equivalent.

Sources:  
[THIRD_PARTY_NOTICES.md:1-29]()  
[LICENSE:1-59]()

---

## See Also

- [Model Artifacts and Storage](#5) — for information on model storage and Git LFS.
- [Main Processing Pipeline](#2) — for the overall system architecture and how these dependencies are used in context.

---

---

