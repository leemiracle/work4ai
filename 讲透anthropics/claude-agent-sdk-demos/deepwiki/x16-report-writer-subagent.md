<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-agent-sdk-demos · extra page Report Writer Subagent · fetched 2026-10-26 -->

# Report Writer Subagent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [research-agent/research_agent/prompts/lead_agent.txt](research-agent/research_agent/prompts/lead_agent.txt)
- [research-agent/research_agent/prompts/report_writer.txt](research-agent/research_agent/prompts/report_writer.txt)

</details>



## Purpose and Scope

The Report Writer Subagent is the final stage in the Research Agent's sequential pipeline, responsible for synthesizing research findings, data analysis, and visualizations into a professional PDF report using the reportlab library. This subagent reads artifacts created by researcher subagents ([5.2.2](#5.2.2)) and the data analyst subagent ([5.2.3](#5.2.3)), then generates a comprehensive 1-2 page PDF document with proper formatting, embedded charts, citations, and sources.

For information about how the Lead Agent coordinates this subagent in the overall workflow, see [Lead Agent Orchestration](#5.2.1). For details on the subagent tracking system that monitors report writer execution, see [Subagent Tracking System](#5.3).

## Role in the Multi-Agent Pipeline

The Report Writer operates as the synthesis phase after all research and analysis is complete:

```mermaid
graph TB
    subgraph "Sequential Pipeline"
        Researchers["RESEARCHER-1 to RESEARCHER-N<br/>files/research_notes/*.md"]
        DataAnalyst["DATA-ANALYST-1<br/>files/data/data_summary.md<br/>files/charts/*.png"]
        ReportWriter["REPORT-WRITER-1<br/>files/reports/*.pdf"]
    end
    
    subgraph "Lead Agent Coordination"
        LeadStep5["Lead Agent Step 5<br/>Spawn report-writer with Task tool"]
        TaskTool["Task tool invocation<br/>subagent_type: 'report-writer'"]
    end
    
    subgraph "Report Writer Tools"
        Glob["Glob tool<br/>Find artifacts in files/"]
        Read["Read tool<br/>Load markdown files"]
        Skill["Skill tool<br/>Invoke 'pdf' skill"]
        Bash["Bash tool<br/>Execute Python/reportlab"]
        Write["Write tool<br/>Save intermediate files"]
    end
    
    subgraph "File System I/O"
        InputNotes["INPUT<br/>files/research_notes/"]
        InputData["INPUT<br/>files/data/"]
        InputCharts["INPUT<br/>files/charts/"]
        OutputReports["OUTPUT<br/>files/reports/"]
    end
    
    subgraph "reportlab Components"
        SimpleDoc["SimpleDocTemplate<br/>PDF document structure"]
        Styles["getSampleStyleSheet<br/>Paragraph styles"]
        Platypus["Platypus elements<br/>Paragraph, Spacer, Image"]
        Builder["doc.build()<br/>Generate PDF"]
    end
    
    Researchers --> DataAnalyst
    DataAnalyst --> ReportWriter
    
    LeadStep5 --> TaskTool
    TaskTool --> ReportWriter
    
    ReportWriter --> Glob
    ReportWriter --> Read
    ReportWriter --> Skill
    ReportWriter --> Bash
    ReportWriter --> Write
    
    Glob --> InputNotes
    Glob --> InputData
    Glob --> InputCharts
    Read --> InputNotes
    Read --> InputData
    
    Bash --> SimpleDoc
    SimpleDoc --> Styles
    Styles --> Platypus
    Platypus --> Builder
    Builder --> OutputReports
    
    InputCharts --> Platypus
```

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:1-113](), [research-agent/research_agent/prompts/lead_agent.txt:51-56]()

## Subagent Configuration

The Report Writer is spawned by the Lead Agent using the Task tool with specific parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `subagent_type` | `"report-writer"` | Identifies agent type for tracking |
| `description` | `"Synthesize research into PDF report"` | Brief summary for logs |
| `prompt` | Full report writer instructions | Loaded from `report_writer.txt` |

The prompt instructs the subagent to read all research notes, incorporate charts and data analysis, and create a professional PDF report using reportlab.

**Sources:** [research-agent/research_agent/prompts/lead_agent.txt:105-109]()

## Prompt Definition and Role

The Report Writer's behavior is defined by [research-agent/research_agent/prompts/report_writer.txt:1-113](). Key role characteristics:

```mermaid
graph LR
    subgraph "Role Definition"
        ReadNotes["Read from<br/>files/research_notes/"]
        ReadData["Read from<br/>files/data/"]
        ReadCharts["Reference<br/>files/charts/"]
        Synthesize["Synthesize findings"]
        CreatePDF["Create PDF with reportlab"]
        SaveReport["Save to<br/>files/reports/"]
    end
    
    subgraph "Critical Constraints"
        NoResearch["Does NOT conduct research"]
        NoWebSearch["No web searches"]
        OnlyRead["Only reads existing notes"]
        OnlyWrite["Only writes reports"]
    end
    
    ReadNotes --> Synthesize
    ReadData --> Synthesize
    ReadCharts --> Synthesize
    Synthesize --> CreatePDF
    CreatePDF --> SaveReport
    
    NoResearch -.->|"enforced by"| ReadNotes
    NoWebSearch -.->|"enforced by"| ReadNotes
    OnlyRead -.->|"enforced by"| ReadNotes
    OnlyWrite -.->|"enforced by"| SaveReport
```

The prompt explicitly states at [research-agent/research_agent/prompts/report_writer.txt:3](): `**CRITICAL: You MUST read research notes from files/research_notes/ folder and generate PDF reports.**`

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:5-12]()

## Execution Workflow

The Report Writer follows a six-step workflow defined in [research-agent/research_agent/prompts/report_writer.txt:22-30]():

```mermaid
graph TD
    Step1["Step 1: Glob<br/>Find all files/research_notes/*.md"]
    Step2["Step 2: Glob<br/>Find files/data/* and files/charts/*.png"]
    Step3["Step 3: Read<br/>Load each research note and data summary"]
    Step4["Step 4: Skill<br/>Invoke 'pdf' skill for reportlab guidance"]
    Step5["Step 5: Bash<br/>Generate Python script with reportlab"]
    Step6["Step 6: Write<br/>Save PDF to files/reports/topic_report_YYYYMMDD.pdf"]
    
    Chart["Include charts/<br/>embed in PDF"]
    
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5
    Step2 --> Chart
    Chart --> Step5
    Step5 --> Step6
```

**Workflow Details:**

1. **Discovery Phase**: Uses `Glob` tool to locate all research artifacts
2. **Loading Phase**: Uses `Read` tool to load markdown content
3. **Guidance Phase**: Optionally invokes the `pdf` skill for reportlab usage patterns
4. **Generation Phase**: Creates Python script using reportlab API via `Bash` tool
5. **Output Phase**: Saves final PDF to `files/reports/` with standardized naming

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:22-30]()

## reportlab PDF Generation

The Report Writer generates PDFs using the reportlab library. The complete pattern is provided in [research-agent/research_agent/prompts/report_writer.txt:32-96]():

### Core reportlab Structure

```mermaid
graph TB
    subgraph "Import Layer"
        Pagesizes["reportlab.lib.pagesizes<br/>letter"]
        Styles["reportlab.lib.styles<br/>getSampleStyleSheet, ParagraphStyle"]
        Units["reportlab.lib.units<br/>inch"]
        Platypus["reportlab.platypus<br/>SimpleDocTemplate, Paragraph,<br/>Spacer, Image, PageBreak"]
        Enums["reportlab.lib.enums<br/>TA_CENTER, TA_JUSTIFY"]
    end
    
    subgraph "Document Setup"
        MkDir["os.makedirs<br/>'files/reports', exist_ok=True"]
        DocTemplate["SimpleDocTemplate<br/>pagesize=letter<br/>margins=72pt"]
        StyleSheet["getSampleStyleSheet()"]
        CustomStyle["ParagraphStyle<br/>name='Justify'<br/>alignment=TA_JUSTIFY"]
    end
    
    subgraph "Content Building"
        Story["story = []<br/>List of flowables"]
        Title["Paragraph + styles['Title']"]
        Heading["Paragraph + styles['Heading1']"]
        Body["Paragraph + styles['Justify']"]
        ImageElem["Image<br/>width=5*inch, height=3*inch"]
        SpacerElem["Spacer<br/>vertical spacing"]
    end
    
    subgraph "PDF Generation"
        Build["doc.build(story)<br/>Generate PDF file"]
    end
    
    Pagesizes --> DocTemplate
    Styles --> StyleSheet
    Units --> ImageElem
    Units --> SpacerElem
    Platypus --> DocTemplate
    Platypus --> Story
    Enums --> CustomStyle
    
    MkDir --> DocTemplate
    DocTemplate --> Story
    StyleSheet --> CustomStyle
    CustomStyle --> Body
    
    Title --> Story
    Heading --> Story
    Body --> Story
    ImageElem --> Story
    SpacerElem --> Story
    
    Story --> Build
```

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:35-96]()

### Document Configuration

The `SimpleDocTemplate` is configured with standard parameters at [research-agent/research_agent/prompts/report_writer.txt:48-53]():

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `pagesize` | `letter` | US Letter (8.5" × 11") |
| `rightMargin` | `72` | 1 inch (72 points) |
| `leftMargin` | `72` | 1 inch (72 points) |
| `topMargin` | `72` | 1 inch (72 points) |
| `bottomMargin` | `72` | 1 inch (72 points) |

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:48-53]()

### Style System

The Report Writer uses reportlab's style system with custom additions:

```python
# Get base styles
styles = getSampleStyleSheet()

# Add custom Justify style
styles.add(ParagraphStyle(
    name='Justify',
    alignment=TA_JUSTIFY,
    fontSize=11,
    leading=14
))
```

Available style names used in reports:
- `styles['Title']` - Document title
- `styles['Heading1']` - Section headings
- `styles['Heading2']` - Subsection headings
- `styles['Justify']` - Custom justified body text
- `styles['Normal']` - Default body text

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:56-62]()

### Content Elements (Platypus Flowables)

Reports are built using Platypus flowable elements added to a `story` list:

```mermaid
graph LR
    subgraph "Element Types"
        Para["Paragraph(text, style)<br/>Text content"]
        Space["Spacer(width, height)<br/>Vertical spacing"]
        Img["Image(path, width, height)<br/>Embedded charts"]
        Break["PageBreak()<br/>Force new page"]
    end
    
    subgraph "Usage Pattern"
        Story["story = []"]
        Append["story.append(element)"]
        Build["doc.build(story)"]
    end
    
    Para --> Append
    Space --> Append
    Img --> Append
    Break --> Append
    
    Story --> Append
    Append --> Build
```

**Typical element sequence:**
1. `Paragraph` with `Title` style
2. `Spacer(1, 0.25*inch)` - Title spacing
3. `Paragraph` with `Heading1` style
4. `Paragraph` with `Justify` style - Content
5. `Spacer(1, 0.2*inch)` - Section spacing
6. `Image` - Embedded chart from `files/charts/`
7. Repeat for additional sections

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:64-86]()

## Report Structure Requirements

The Report Writer must adhere to strict structural requirements defined in [research-agent/research_agent/prompts/report_writer.txt:98-112]():

### Mandatory Components

| Component | Requirement | Location |
|-----------|-------------|----------|
| **Output Format** | PDF with `.pdf` extension | N/A |
| **Save Location** | `files/reports/` directory | Must exist, created with `os.makedirs` |
| **File Naming** | `{topic}_report_YYYYMMDD.pdf` | Standardized format |
| **Length** | 1-2 pages (500-1000 words) | Content constraint |
| **Title and Date** | Required header elements | Top of first page |
| **Executive Summary** | 2-3 sentences | After title |
| **Key Findings** | With citations | Main body section |
| **Data Visualizations** | Embed charts from `files/charts/` | If available |
| **Sources Section** | URLs and references | End of report |

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:98-112]()

### Section Breakdown

```mermaid
graph TD
    Header["1. Title + Date<br/>Paragraph with styles['Title']"]
    ExecSum["2. Executive Summary<br/>styles['Heading1'] + 2-3 sentence summary"]
    KeyFind["3. Key Findings<br/>styles['Heading1'] + bullet points with citations"]
    Charts["4. Data Visualizations<br/>Image elements from files/charts/"]
    Sources["5. Sources<br/>styles['Heading2'] + numbered list with URLs"]
    
    Header --> ExecSum
    ExecSum --> KeyFind
    KeyFind --> Charts
    Charts --> Sources
```

**Critical requirement from [research-agent/research_agent/prompts/report_writer.txt:110]():** "Every claim must have a citation (source/URL when available)"

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:103-111]()

## Chart Embedding Pattern

The Report Writer embeds charts generated by the Data Analyst subagent. The pattern at [research-agent/research_agent/prompts/report_writer.txt:75-80]() demonstrates conditional chart inclusion:

```python
# Check if chart exists
chart_path = "files/charts/chart_name.png"
if os.path.exists(chart_path):
    # Create Image flowable with fixed dimensions
    img = Image(chart_path, width=5*inch, height=3*inch)
    story.append(img)
    story.append(Spacer(1, 0.2*inch))
```

**Chart integration steps:**
1. Use `Glob` tool to discover chart files in `files/charts/`
2. Check existence with `os.path.exists()` before embedding
3. Create `Image` flowable with dimensions (typically 5" × 3")
4. Append to story list
5. Add spacing after chart for visual separation

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:75-80]()

## File System Integration

The Report Writer reads from and writes to specific directories in the `files/` structure:

```mermaid
graph LR
    subgraph "Input Directories"
        ResearchNotes["files/research_notes/<br/>*.md files<br/>From RESEARCHER subagents"]
        DataDir["files/data/<br/>data_summary.md<br/>From DATA-ANALYST subagent"]
        ChartsDir["files/charts/<br/>*.png files<br/>From DATA-ANALYST subagent"]
    end
    
    subgraph "Report Writer Operations"
        GlobOp["Glob tool<br/>Discover files"]
        ReadOp["Read tool<br/>Load markdown content"]
        BashOp["Bash tool<br/>Execute Python script"]
    end
    
    subgraph "Output Directory"
        ReportsDir["files/reports/<br/>topic_report_YYYYMMDD.pdf<br/>Created by REPORT-WRITER"]
    end
    
    ResearchNotes --> GlobOp
    DataDir --> GlobOp
    ChartsDir --> GlobOp
    
    GlobOp --> ReadOp
    ReadOp --> BashOp
    ChartsDir --> BashOp
    
    BashOp --> ReportsDir
```

**File paths accessed:**
- **Read**: `files/research_notes/*.md` - All research findings
- **Read**: `files/data/data_summary.md` - Quantitative analysis
- **Read**: `files/charts/*.png` - Generated visualizations
- **Write**: `files/reports/{topic}_report_YYYYMMDD.pdf` - Final output

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:6-10](), [research-agent/research_agent/prompts/report_writer.txt:23-29]()

## Python Script Generation Pattern

The Report Writer generates a Python script that uses reportlab to create the PDF. The execution flow:

```mermaid
graph TD
    Analyze["Analyze all research notes<br/>and data summaries"]
    Plan["Plan report structure<br/>sections, findings, charts"]
    Generate["Generate Python script<br/>using reportlab API"]
    Execute["Execute via Bash tool<br/>node generate_pdf.py"]
    Verify["Verify PDF created<br/>files/reports/*.pdf"]
    
    Analyze --> Plan
    Plan --> Generate
    Generate --> Execute
    Execute --> Verify
    
    subgraph "Script Contents"
        Imports["Import reportlab modules"]
        Setup["Create SimpleDocTemplate"]
        BuildStory["Build story list"]
        EmbedCharts["Conditionally embed charts"]
        BuildPDF["doc.build(story)"]
    end
    
    Generate --> Imports
    Imports --> Setup
    Setup --> BuildStory
    BuildStory --> EmbedCharts
    EmbedCharts --> BuildPDF
    BuildPDF --> Execute
```

The script follows the template pattern provided in [research-agent/research_agent/prompts/report_writer.txt:35-95](), which includes:
- Import statements for all necessary reportlab modules
- Directory creation with `os.makedirs`
- `SimpleDocTemplate` initialization with margins
- Style system setup with custom styles
- Story list construction with all content elements
- Conditional chart embedding
- Final PDF generation with `doc.build()`

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:32-96]()

## Example Report Structure

A typical report generated by the Report Writer has this structure:

| Section | Content | Style | Spacing |
|---------|---------|-------|---------|
| **Title** | Research topic name | `styles['Title']` | `0.25*inch` after |
| **Executive Summary** | 2-3 sentence overview of key findings | `styles['Heading1']` + `styles['Justify']` | `0.2*inch` after |
| **Key Finding 1** | First major finding with citation | `styles['Justify']` | `0.1*inch` after |
| **Key Finding 2** | Second major finding with citation | `styles['Justify']` | `0.1*inch` after |
| **Chart 1** | Embedded visualization from `files/charts/` | `Image` flowable | `0.2*inch` after |
| **Key Finding 3** | Third major finding with data | `styles['Justify']` | `0.1*inch` after |
| **Chart 2** | Second embedded visualization | `Image` flowable | `0.2*inch` after |
| **Sources** | Numbered list of URLs and references | `styles['Heading2']` + `styles['Normal']` | End of document |

**Typical page count:** 1-2 pages depending on number of findings and charts

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:67-91](), [research-agent/research_agent/prompts/report_writer.txt:101-102]()

## Tools Available to Report Writer

The Report Writer has access to five tools defined in [research-agent/research_agent/prompts/report_writer.txt:14-20]():

| Tool | Purpose | Usage Pattern |
|------|---------|---------------|
| **Glob** | Find files matching patterns | Discover `files/research_notes/*.md`, `files/data/*`, `files/charts/*.png` |
| **Read** | Read file contents | Load markdown files and data summaries |
| **Skill** | Access domain knowledge | Invoke `pdf` skill for reportlab guidance |
| **Bash** | Execute commands | Run Python scripts to generate PDFs |
| **Write** | Create files | Save intermediate files if needed |

**Tool restrictions:** The Report Writer does NOT have access to:
- `WebSearch` - Cannot conduct new research
- `WebFetch` - Cannot retrieve external content
- `Task` - Cannot spawn additional subagents

**Sources:** [research-agent/research_agent/prompts/report_writer.txt:14-20]()

---

