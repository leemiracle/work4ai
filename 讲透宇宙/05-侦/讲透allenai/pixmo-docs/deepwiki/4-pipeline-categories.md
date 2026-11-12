<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/pixmo-docs · page 4 Pipeline Categories · fetched 2026-10-26 -->

# Pipeline Categories

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [pipeline/all_pipelines.py](pipeline/all_pipelines.py)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the pipeline categories in the PixMo-Docs system. These pipelines are the core mechanisms for generating synthetic text-rich images used to train multimodal models like Molmo. The document covers all 25 pipelines organized into 8 main categories, explaining their purposes, technologies, and characteristics. For details on how these pipelines are executed in the overall system, see [System Architecture](#3) and [DataDreamer Session](#3.1).

Sources: [README.md:65-109]()

## Pipeline Category Overview

The PixMo-Docs system organizes its 25 pipelines into 8 distinct categories, each specialized for generating specific types of text-rich visual content. Each pipeline uses a particular renderer or programming language to generate the synthetic data.

```mermaid
graph TD
    subgraph "Pipeline Categories"
        P["All Pipelines"] --> C["Chart Pipelines"]
        P --> T["Table Pipelines"]
        P --> D["Document Pipelines"]
        P --> DG["Diagram Pipelines"]
        P --> CR["Circuit Pipelines"]
        P --> S["Specialized Graphics Pipelines"]
        P --> W["Web Screen Pipelines"]
        P --> PT["Pointing Pipelines"]
    end
    
    subgraph "Pipeline Implementation"
        C --> |"implements"| C1["MatplotlibChartPipeline"]
        C --> |"implements"| C2["PlotlyChartPipeline"]
        C --> |"implements"| C3["VegaLiteChartPipeline"]
        C --> |"implements"| C4["LaTeXChartPipeline"]
        C --> |"implements"| C5["HTMLChartPipeline"]
        
        T --> |"implements"| T1["LaTeXTablePipeline"]
        T --> |"implements"| T2["MatplotlibTablePipeline"]
        T --> |"implements"| T3["PlotlyTablePipeline"]
        T --> |"implements"| T4["HTMLTablePipeline"]
        
        D --> |"implements"| D1["LaTeXDocumentPipeline"]
        D --> |"implements"| D2["HTMLDocumentPipeline"]
        D --> |"implements"| D3["DOCXDocumentPipeline"]
        
        DG --> |"implements"| DG1["GraphvizDiagramPipeline"]
        DG --> |"implements"| DG2["MermaidDiagramPipeline"]
        DG --> |"implements"| DG3["LaTeXDiagramPipeline"]
        
        CR --> |"implements"| CR1["SchemDrawCircuitPipeline"]
        CR --> |"implements"| CR2["LaTeXCircuitPipeline"]
        
        S --> |"implements"| S1["DALLEImagePipeline"]
        S --> |"implements"| S2["RdkitChemicalPipeline"]
        S --> |"implements"| S3["LaTeXMathPipeline"]
        S --> |"implements"| S4["LilyPondMusicPipeline"]
        S --> |"implements"| S5["SVGGraphicPipeline"]
        S --> |"implements"| S6["AsymptoteGraphicPipeline"]
        
        W --> |"implements"| W1["HTMLScreenPipeline"]
        
        PT --> |"implements"| PT1["HTMLDocumentPointPipeline"]
    end
```

Sources: [README.md:66-109](), [pipeline/all_pipelines.py:9-40]()

## Pipeline Selection and Execution

In the PixMo-Docs system, pipelines are selected and executed via the `run_datadreamer_session` function. This function initializes the DataDreamer framework, configures the selected LLMs, and executes the chosen pipelines based on the command-line arguments.

```mermaid
sequenceDiagram
    participant User
    participant Main as "main.py"
    participant RDS as "run_datadreamer_session"
    participant Pipeline as "Selected Pipeline"
    participant LLM as "LLM (GPT-4o/Claude)"
    
    User->>Main: Execute with CLI arguments
    Main->>RDS: Pass pipeline arguments
    RDS->>RDS: Initialize DataDreamer
    RDS->>RDS: Configure LLM(s)
    
    loop For each selected pipeline
        RDS->>Pipeline: Initialize pipeline with arguments
        Pipeline->>LLM: Generate content
        LLM-->>Pipeline: Return generated content
        Pipeline->>Pipeline: Render content to image
        Pipeline-->>RDS: Return processed results
    end
    
    RDS->>RDS: Combine results from all pipelines
    RDS->>RDS: Publish to Hugging Face Hub
    RDS-->>Main: Complete execution
    Main-->>User: Finish
```

Sources: [pipeline/all_pipelines.py:42-147]()

## 1. Chart Pipelines

Chart pipelines generate various types of data visualizations like bar charts, line charts, scatter plots, and more complex chart types.

| Pipeline | Technology | Capabilities | Limitations |
|----------|------------|--------------|-------------|
| MatplotlibChartPipeline | Matplotlib | Wide range of chart types with detailed customization | Python-based, requires script execution |
| PlotlyChartPipeline | Plotly | Interactive charts with rich features | Complex structure for simple charts |
| VegaLiteChartPipeline | Vega-Lite | Declarative JSON-based grammar of graphics | Requires vl-convert for rendering |
| LaTeXChartPipeline | TikZ/LaTeX | Precise vector graphics | Limited to simpler chart types |
| HTMLChartPipeline | HTML/CSS | Browser-rendered charts | Limited to basic chart types |

```mermaid
graph TD
    subgraph "Chart Pipeline Flow"
        step1["GenerateChartTopics"] --> step2["GenerateChartData"]
        step2 --> step3["GenerateChart"]
        step3 --> step4["GenerateChartQA"]
    end
    
    subgraph "Rendering Technologies"
        step3 --> |"Matplotlib"| r1["matplotlib.pyplot"]
        step3 --> |"Plotly"| r2["plotly.graph_objects"]
        step3 --> |"Vega-Lite"| r3["vl-convert"]
        step3 --> |"LaTeX"| r4["LaTeX Compiler + pdf2image"]
        step3 --> |"HTML"| r5["Playwright Browser"]
    end
```

Sources: [README.md:69-74](), [pipeline/all_pipelines.py:9-14](), [pipeline/all_pipelines.py:77-81]()

## 2. Table Pipelines

Table pipelines are specialized for generating tabular data visualizations with various formatting options and complexity levels.

| Pipeline | Technology | Capabilities | Limitations |
|----------|------------|--------------|-------------|
| LaTeXTablePipeline | LaTeX | Complex table structures with precise formatting | Requires LaTeX compiler |
| MatplotlibTablePipeline | Matplotlib | Tables rendered within figures | Limited formatting options |
| PlotlyTablePipeline | Plotly | Simple tabular data | Best for single-header tables |
| HTMLTablePipeline | HTML/CSS | Style-rich tables | Best for simpler table structures |

```mermaid
graph TD
    subgraph "Table Pipeline Flow"
        step1["GenerateTableTopics"] --> step2["GenerateTableData"]
        step2 --> step3["GenerateTable"]
        step3 --> step4["GenerateTableQA"]
    end
    
    subgraph "Rendering Technologies"
        step3 --> |"LaTeX"| r1["LaTeX Compiler + pdf2image"]
        step3 --> |"Matplotlib"| r2["matplotlib.pyplot.table"]
        step3 --> |"Plotly"| r3["plotly.graph_objects.Table"]
        step3 --> |"HTML"| r4["Playwright Browser"]
    end
```

Sources: [README.md:76-80](), [pipeline/all_pipelines.py:16-19](), [pipeline/all_pipelines.py:82-85]()

## 3. Document Pipelines

Document pipelines generate multi-page or complex layout text documents with various formatting and structure.

| Pipeline | Technology | Capabilities | Limitations |
|----------|------------|--------------|-------------|
| LaTeXDocumentPipeline | LaTeX | Professional documents with complex formatting | Requires LaTeX compiler |
| HTMLDocumentPipeline | HTML/CSS | Web-style documents with diverse styles | Browser-dependent rendering |
| DOCXDocumentPipeline | docx | Microsoft Word-compatible documents | Limited formatting compared to LaTeX |

```mermaid
graph TD
    subgraph "Document Pipeline Flow"
        step1["GenerateDocumentTopics"] --> step2["GenerateDocumentContent"]
        step2 --> step3["GenerateDocument"]
        step3 --> step4["GenerateDocumentQA"]
    end
    
    subgraph "Rendering Technologies"
        step3 --> |"LaTeX"| r1["LaTeX Compiler + pdf2image"]
        step3 --> |"HTML"| r2["Playwright Browser"]
        step3 --> |"DOCX"| r3["python-docx + rendering"]
    end
```

Sources: [README.md:82-85](), [pipeline/all_pipelines.py:20-22](), [pipeline/all_pipelines.py:86-88]()

## 4. Diagram Pipelines

Diagram pipelines produce various types of schematic visualizations like flowcharts, entity-relationship diagrams, trees, and other structured representations.

| Pipeline | Technology | Capabilities | Limitations |
|----------|------------|--------------|-------------|
| GraphvizDiagramPipeline | Graphviz | Directed graphs, trees, networks | Limited stylistic options |
| MermaidDiagramPipeline | Mermaid | Flowcharts, sequence diagrams, gantt charts | Simpler syntax but fewer features than Graphviz |
| LaTeXDiagramPipeline | TikZ/LaTeX | Precise control over diagram layout | Steeper learning curve |

```mermaid
graph TD
    subgraph "Diagram Pipeline Flow"
        step1["GenerateDiagramTopics"] --> step2["GenerateDiagramData"]
        step2 --> step3["GenerateDiagram"]
        step3 --> step4["GenerateDiagramQA"]
    end
    
    subgraph "Rendering Technologies"
        step3 --> |"Graphviz"| r1["graphviz dot command"]
        step3 --> |"Mermaid"| r2["mermaid-cli"]
        step3 --> |"LaTeX"| r3["TikZ + LaTeX Compiler + pdf2image"]
    end
```

Sources: [README.md:87-90](), [pipeline/all_pipelines.py:24-26](), [pipeline/all_pipelines.py:89-91]()

## 5. Circuit Pipelines

Circuit pipelines are specialized for generating electrical and electronic circuit diagrams with appropriate symbols and connections.

| Pipeline | Technology | Capabilities | Limitations |
|----------|------------|--------------|-------------|
| SchemDrawCircuitPipeline | SchemDraw | Python-based electrical circuit diagrams | Limited to specific circuit types |
| LaTeXCircuitPipeline | TikZ/CircuiTikZ | Precise control over circuit layout | Requires LaTeX knowledge |

```mermaid
graph TD
    subgraph "Circuit Pipeline Flow"
        step1["GenerateCircuitTopics"] --> step2["GenerateCircuitData"]
        step2 --> step3["GenerateCircuit"]
        step3 --> step4["GenerateCircuitQA"]
    end
    
    subgraph "Rendering Technologies"
        step3 --> |"SchemDraw"| r1["schemdraw Python library"]
        step3 --> |"LaTeX"| r2["CircuiTikZ + LaTeX Compiler + pdf2image"]
    end
```

Sources: [README.md:92-94](), [pipeline/all_pipelines.py:33-34](), [pipeline/all_pipelines.py:96-97]()

## 6. Specialized Graphics Pipelines

Specialized graphics pipelines generate domain-specific visualizations that don't fit into other categories, including AI-generated images, chemical structures, mathematical expressions, music notation, and vector graphics.

| Pipeline | Technology | Capabilities | Limitations |
|----------|------------|--------------|-------------|
| DALLEImagePipeline | DALL·E API | AI-generated images from text prompts | Requires OpenAI API access |
| RdkitChemicalPipeline | RDKit | Chemical structure diagrams | Limited to chemical notation |
| LaTeXMathPipeline | LaTeX math | Mathematical expressions and equations | Requires LaTeX compiler |
| LilyPondMusicPipeline | LilyPond | Music notation and sheet music | Requires LilyPond compiler |
| SVGGraphicPipeline | SVG | Vector graphics in web-standard format | Limited to SVG capabilities |
| AsymptoteGraphicPipeline | Asymptote | Technical vector graphics | Requires Asymptote compiler |

```mermaid
graph TD
    subgraph "Specialized Graphics Pipeline Flow"
        step1["GenerateSpecificTopics"] --> step2["GenerateSpecificData"]
        step2 --> step3["GenerateGraphic"]
        step3 --> step4["GenerateSpecificQA"]
    end
    
    subgraph "Rendering Technologies"
        step3 --> |"DALL·E"| r1["OpenAI DALL·E API"]
        step3 --> |"Chemical"| r2["RDKit Python library"]
        step3 --> |"Math"| r3["LaTeX Compiler + pdf2image"]
        step3 --> |"Music"| r4["LilyPond Compiler"]
        step3 --> |"SVG"| r5["cairosvg"]
        step3 --> |"Asymptote"| r6["Asymptote CLI"]
    end
```

Sources: [README.md:96-102](), [pipeline/all_pipelines.py:28-32](), [pipeline/all_pipelines.py:35-37](), [pipeline/all_pipelines.py:92-95](), [pipeline/all_pipelines.py:98-99]()

## 7. Web Screen Pipelines

Web screen pipelines generate realistic screenshots of web interfaces and applications.

| Pipeline | Technology | Capabilities | Limitations |
|----------|------------|--------------|-------------|
| HTMLScreenPipeline | HTML/CSS/Playwright | Complete web screen layouts | Requires Playwright and Chrome/Chromium |

```mermaid
graph TD
    subgraph "Web Screen Pipeline Flow"
        step1["GenerateScreenTopics"] --> step2["GenerateScreenContent"]
        step2 --> step3["GenerateScreen"]
        step3 --> step4["GenerateScreenQA"]
    end
    
    subgraph "Rendering Technologies"
        step3 --> |"HTML Screen"| r1["Playwright Browser"]
    end
```

Sources: [README.md:104-105](), [pipeline/all_pipelines.py:40](), [pipeline/all_pipelines.py:101]()

## 8. Pointing Pipelines

Pointing pipelines generate documents with structured point references, useful for training models on reference resolution tasks.

| Pipeline | Technology | Capabilities | Limitations |
|----------|------------|--------------|-------------|
| HTMLDocumentPointPipeline | HTML/CSS | Documents with structured point references | Limited to HTML-based pointing |

```mermaid
graph TD
    subgraph "Pointing Pipeline Flow"
        step1["GeneratePointTopics"] --> step2["GeneratePointContent"]
        step2 --> step3["GeneratePointingDocument"]
        step3 --> step4["GeneratePointingQA"]
    end
    
    subgraph "Rendering Technologies"
        step3 --> |"HTML Pointing"| r1["Playwright Browser"]
    end
```

Sources: [README.md:108-109](), [pipeline/all_pipelines.py:39](), [pipeline/all_pipelines.py:100]()

## Pipeline Integration in System Architecture

The pipelines are executed as part of the overall data generation flow, which is managed by the `run_datadreamer_session` function. This function orchestrates the creation of synthetic data by selecting and configuring the appropriate pipelines based on user input.

```mermaid
graph TD
    subgraph "System Architecture"
        mainpy["main.py"] --> rds["run_datadreamer_session()"]
        rds --> dd["DataDreamer Framework"]
        rds --> llm["LLM Configuration"]
        rds --> pl["Pipeline Selection"]
        
        llm --> gpt["OpenAI/GPT-4o"]
        llm --> claude["Anthropic/Claude"]
        
        pl --> cat1["Chart Pipelines"]
        pl --> cat2["Table Pipelines"]
        pl --> cat3["Document Pipelines"]
        pl --> cat4["Diagram Pipelines"]
        pl --> cat5["Circuit Pipelines"]
        pl --> cat6["Specialized Graphics Pipelines"]
        pl --> cat7["Web Screen Pipelines"]
        pl --> cat8["Pointing Pipelines"]
        
        cat1 & cat2 & cat3 & cat4 & cat5 & cat6 & cat7 & cat8 --> process["Pipeline Processing"]
        
        process --> dataset["Dataset Creation"]
        dataset --> publish["Publish to Hugging Face Hub"]
    end
```

Sources: [pipeline/all_pipelines.py:42-147]()

## Common Pipeline Structure

Most pipelines in the system follow a similar four-step structure, which ensures consistency across different pipeline categories while allowing for specialized implementation details.

```mermaid
graph LR
    subgraph "Typical Pipeline Structure"
        step1["GenerateTopics"] --> step2["GenerateData"]
        step2 --> step3["GenerateContent"]
        step3 --> step4["GenerateQA"]
    end
    
    subgraph "Input/Output Flow"
        llm1["LLM"] -.-> step1
        llm1 -.-> step2
        llm2["code_LLM"] -.-> step3
        llm1 -.-> step4
        
        step1 -- "metadata, topic" --> step2
        step2 -- "metadata, topic, data" --> step3
        step3 -- "metadata, topic, data, code, image" --> step4
        step4 -- "metadata, topic, data, code, image, qa" --> output["Final Output"]
    end
```

This structure illustrates how each pipeline processes data through sequential steps:
1. Topic generation
2. Data preparation based on topics
3. Content generation (code + image rendering)
4. Question-answer pair generation (optional)

Sources: [pipeline/all_pipelines.py:119-134]()

## Conclusion

The Pipeline Categories in PixMo-Docs provide a flexible and extensible framework for generating a wide variety of text-rich images for training multimodal models. Each pipeline category specializes in a particular type of visual content, and the system architecture ensures that these pipelines can be easily selected, configured, and executed to generate synthetic datasets. For more details on how to execute these pipelines from the command line, see [Command Line Usage](#7).

---

