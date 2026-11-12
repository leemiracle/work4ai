<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/pdffigures2 · page 3 Core Processing Pipeline · fetched 2026-10-26 -->

# Core Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala](src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala)

</details>



This page covers the core processing pipeline that orchestrates figure extraction from PDF documents. The pipeline consists of 11 sequential steps that transform a raw PDF document into extracted figures with metadata. For information about specific processing components like text extraction and caption detection, see [Text Extraction and Processing](#3.1), [Caption Detection and Building](#3.3), and [Graphics and Figure Detection](#3.4).

The pipeline is orchestrated by the `FigureExtractor` class, which provides multiple output formats including basic figures, rasterized images, and documents with sectioned text. This page focuses on the overall architecture and data flow rather than the details of individual processing steps.

## Pipeline Architecture

The core pipeline transforms PDF documents through a series of intermediate representations, each adding more structured information about the document's content and layout.

### Processing Steps Overview

```mermaid
graph TD
    subgraph "Input"
        PDF["PDDocument"]
    end
    
    subgraph "Text Processing Steps"
        TE["TextExtractor.extractText()"]
        FTE["FormattingTextExtractor.extractFormattingText()"]
        DL["DocumentLayout()"]
    end
    
    subgraph "Optional Preprocessing"
        PR["ParagraphRebuilder.rebuildParagraphs()"]
        STE["SectionTitleExtractor.stripSectionTitlesFromTextPage()"]
    end
    
    subgraph "Caption and Graphics Processing"
        CD["CaptionDetector.findCaptions()"]
        GE["GraphicsExtractor.extractGraphics()"]
        CB["CaptionBuilder.buildCaptions()"]
    end
    
    subgraph "Classification and Detection"
        RC["RegionClassifier.classifyRegions()"]
        FD["FigureDetector.locatedFigures()"]
    end
    
    subgraph "Output Generation"
        FR["FigureRenderer.rasterizeFigures()"]
        STB["SectionedTextBuilder.buildSectionedText()"]
    end
    
    PDF --> TE
    TE --> FTE
    FTE --> DL
    DL --> PR
    PR --> STE
    STE --> CD
    CD --> GE
    GE --> CB
    CB --> RC
    RC --> FD
    FD --> FR
    FD --> STB
    
    style TE fill:#f9f9f9
    style FD fill:#f0f8ff
    style FR fill:#f5f5dc
```

**Pipeline Data Flow and Component Responsibilities**

Sources: [README.md:92-118](), [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:130-198]()

### Data Structure Evolution

The pipeline progressively enriches data structures as documents move through processing steps:

```mermaid
graph LR
    subgraph "Page Representations"
        PTxt["PageWithText"]
        PFmt["PageWithFormattingText"] 
        PClass["PageWithClassifiedText"]
        PGraph["PageWithGraphics"]
        PCap["PageWithCaptions"]
        PBody["PageWithBodyText"]
        PFig["PageWithFigures"]
    end
    
    subgraph "Document Representations"
        DContent["DocumentContent"]
        Doc["Document"]
        DocRaster["DocumentWithRasterizedFigures"]
        DocSaved["DocumentWithSavedFigures"]
    end
    
    subgraph "Figure Representations"
        Fig["Figure"]
        RastFig["RasterizedFigure"]
        SavedFig["SavedFigure"]
    end
    
    PTxt --> PFmt
    PFmt --> PClass
    PClass --> PGraph
    PGraph --> PCap
    PCap --> PBody
    PBody --> PFig
    
    PFig --> DContent
    DContent --> Doc
    DContent --> DocRaster
    DocRaster --> DocSaved
    
    PFig --> Fig
    Fig --> RastFig
    RastFig --> SavedFig
    
    style PFig fill:#e8f4f8
    style DContent fill:#f0f8ff
    style Fig fill:#f5f5dc
```

**Progressive Data Enrichment Through Pipeline Stages**

Sources: [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:207-226](), [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:232-260]()

## FigureExtractor Orchestration

The `FigureExtractor` class serves as the main orchestrator, providing multiple public interfaces while managing the internal processing pipeline.

### Core Processing Method

The `parseDocument` method implements the complete pipeline:

| Step | Component | Input Type | Output Type | Purpose |
|------|-----------|------------|-------------|---------|
| 1 | `TextExtractor` | `PDDocument` | `PageWithText` | Extract raw text from PDF |
| 2 | `FormattingTextExtractor` | `PageWithText` | `PageWithFormattingText` | Remove headers, page numbers |
| 3 | `DocumentLayout` | `PageWithFormattingText` | `DocumentLayout` | Analyze fonts, spacing, layout |
| 4 | `ParagraphRebuilder` | `PageWithFormattingText` | `PageWithFormattingText` | Rebuild paragraph structure (optional) |
| 5 | `SectionTitleExtractor` | `PageWithFormattingText` | `PageWithFormattingText` | Extract section titles (optional) |
| 6 | `CaptionDetector` | `PageWithFormattingText` | `CaptionStart` | Identify caption locations |
| 7 | `GraphicsExtractor` | `PageWithFormattingText` | `PageWithGraphics` | Extract graphical elements |
| 8 | `CaptionBuilder` | `PageWithGraphics` | `PageWithCaptions` | Build complete captions |
| 9 | `RegionClassifier` | `PageWithCaptions` | `PageWithBodyText` | Classify text regions |
| 10 | `FigureDetector` | `PageWithBodyText` | `PageWithFigures` | Locate figure regions |
| 11 | `FigureRenderer` | `PageWithFigures` | `RasterizedFigure` | Render figures to images (optional) |

Sources: [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:130-198](), [README.md:92-118]()

### Configuration and Behavior Control

The `FigureExtractor` constructor accepts configuration parameters that control pipeline behavior:

```mermaid
graph TB
    subgraph "FigureExtractor Configuration"
        AO["allowOcr: Boolean<br/>Process OCR PDFs"]
        IWG["ignoreWhiteGraphics: Boolean<br/>Skip colorless graphics"]  
        DSTF["detectSectionTitlesFirst: Boolean<br/>Extract sections before figures"]
        RP["rebuildParagraphs: Boolean<br/>Rebuild paragraph structure"]
        CRFR["cleanRasterizedFigureRegions: Boolean<br/>Post-process figure regions"]
    end
    
    subgraph "Pipeline Steps Affected"
        GE2["GraphicsExtractor"]
        PR2["ParagraphRebuilder"] 
        STE2["SectionTitleExtractor"]
        FR2["FigureRenderer"]
    end
    
    AO -.-> GE2
    IWG --> GE2
    DSTF --> STE2
    RP --> PR2
    CRFR --> FR2
    
    style AO fill:#fff3cd
    style IWG fill:#d4edda
    style DSTF fill:#d1ecf1
    style RP fill:#f8d7da
    style CRFR fill:#e2e3e5
```

**FigureExtractor Configuration Parameters and Their Effects**

Sources: [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:15-21](), [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:266-298]()

## Public Interface Methods

The `FigureExtractor` provides multiple methods for different use cases, all built on the same core pipeline:

### Output Format Methods

```mermaid
graph LR
    subgraph "Core Pipeline"
        PD["parseDocument()"]
    end
    
    subgraph "Public Interface Methods"
        GF["getFigures()"]
        GRF["getRasterizedFigures()"]
        GFWE["getFiguresWithErrors()"]
        GRFWE["getRasterizedFiguresWithErrors()"]
        GFWT["getFiguresWithText()"]
        GRFWT["getRasterizedFiguresWithText()"]
    end
    
    subgraph "Output Types"
        Fig2["Iterable[Figure]"]
        RastFig2["Iterable[RasterizedFigure]"]
        FigDoc["FiguresInDocument"]
        RastFigDoc["RasterizedFiguresInDocument"]
        Doc2["Document"]
        DocRast2["DocumentWithRasterizedFigures"]
    end
    
    PD --> GF
    PD --> GRF
    PD --> GFWE
    PD --> GRFWE
    PD --> GFWT
    PD --> GRFWT
    
    GF --> Fig2
    GRF --> RastFig2
    GFWE --> FigDoc
    GRFWE --> RastFigDoc
    GFWT --> Doc2
    GRFWT --> DocRast2
    
    style PD fill:#e8f4f8
    style GFWT fill:#f0f8ff
    style GRFWT fill:#f5f5dc
```

**Public Interface Methods and Their Output Types**

Sources: [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:22-97]()

### Error Handling and Interruption

The pipeline includes robust error handling and supports interruption:

- **Thread Interruption**: The pipeline checks `Thread.interrupted()` at key points and can be safely cancelled
- **Failed Captions**: Captions that cannot be processed are tracked in `failedCaptions` collections
- **OCR Detection**: PDFs requiring OCR processing can be detected and optionally rejected
- **Layout Validation**: Documents without sufficient layout information skip figure detection

Sources: [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:138-141](), [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:161](), [README.md:88]()

## DocumentContent Structure

The `DocumentContent` case class represents the complete processing result:

```mermaid
graph TD
    subgraph "DocumentContent Structure"
        DC["DocumentContent"]
        Layout["layout: Option[DocumentLayout]"]
        PWF["pagesWithFigures: Seq[PageWithFigures]"]
        PWOF["pagesWithoutFigures: Seq[PageWithClassifiedText]"]
    end
    
    subgraph "Derived Properties"
        Pages["pages: Seq[PageWithClassifiedText]<br/>(sorted combination)"]
        Figs["figures: Seq[Figure]<br/>(flattened from pages)"]
        FailedCaps["failedCaptions: Seq[CaptionStart]<br/>(processing failures)"]
    end
    
    subgraph "Validation Requirements"
        StartZero["Must start with page 0"]
        Consecutive["Page numbers must be consecutive"]
    end
    
    DC --> Layout
    DC --> PWF
    DC --> PWOF
    
    PWF --> Pages
    PWOF --> Pages
    PWF --> Figs
    PWF --> FailedCaps
    
    Pages --> StartZero
    Pages --> Consecutive
    
    style DC fill:#e8f4f8
    style Pages fill:#f0f8ff
    style Figs fill:#f5f5dc
```

**DocumentContent Structure and Validation Requirements**

Sources: [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:207-226]()

## Section and Abstract Processing

The pipeline includes additional processing for document structure:

### Section Processing Logic

```mermaid
graph TD
    subgraph "Section Processing Decision"
        HasLayout{"layout.isDefined"}
        DSTF2{"detectSectionTitlesFirst"}
        SimpleText["Simple text sections<br/>from paragraphs"]
        SectionStrip["SectionTitleExtractor.<br/>stripSectionTitlesFromTextPage()"]
        SectionBuild["SectionedTextBuilder.<br/>buildSectionedText()"]
    end
    
    HasLayout -->|false| SimpleText
    HasLayout -->|true| DSTF2
    DSTF2 -->|true| SectionBuild
    DSTF2 -->|false| SectionStrip
    SectionStrip --> SectionBuild
    
    style HasLayout fill:#fff3cd
    style SimpleText fill:#d4edda
    style SectionBuild fill:#d1ecf1
```

**Section Processing Decision Logic**

### Abstract Extraction

The `getAbstract` method locates abstract text by finding the first page with classified abstract text and wrapping it in a `PdfText` structure.

Sources: [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:99-127](), [src/main/scala/org/allenai/pdffigures2/FigureExtractor.scala:115-127]()

---

