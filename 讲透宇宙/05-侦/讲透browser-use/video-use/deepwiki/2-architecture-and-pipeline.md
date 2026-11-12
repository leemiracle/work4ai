<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/video-use · page 2 Architecture and Pipeline · fetched 2026-10-30 -->

# Architecture and Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [poster.html](poster.html)

</details>



The **video-use** pipeline is designed around a "Text-First, Visuals-on-Demand" philosophy. Rather than forcing an LLM to process thousands of raw video frames, the system converts video into a structured, searchable text format (`takes_packed.md`) and provides high-density visual composites (`timeline_view.py`) only when specific visual decisions are required [README.md:67-89]().

The pipeline follows a linear progression from raw footage ingestion to a self-evaluated final render.

### System Data Flow

The following diagram illustrates the transformation of data from raw source files through the internal representations to the final output.

**Data Transformation Pipeline**
```mermaid
graph TD
    subgraph "Ingestion Phase"
        [Source_Footage] --> ["transcribe_batch.py"]
        ["transcribe_batch.py"] --> ["ElevenLabs_Scribe_API"]
        ["ElevenLabs_Scribe_API"] --> [Raw_JSON_Transcripts]
        [Raw_JSON_Transcripts] --> ["pack_transcripts.py"]
        ["pack_transcripts.py"] --> ["takes_packed.md"]
    end

    subgraph "Reasoning Phase"
        ["takes_packed.md"] --> [LLM_Editor_Agent]
        [LLM_Editor_Agent] --> ["timeline_view.py"]
        ["timeline_view.py"] --> [Visual_Composites_PNG]
        [Visual_Composites_PNG] --> [LLM_Editor_Agent]
        [LLM_Editor_Agent] --> ["edl.json"]
    end

    subgraph "Execution Phase"
        ["edl.json"] --> ["render.py"]
        ["render.py"] --> ["grade.py"]
        ["grade.py"] --> [Final_Render_MP4]
    end

    subgraph "Verification Phase"
        [Final_Render_MP4] --> [Self_Evaluation_Loop]
        [Self_Evaluation_Loop] --> ["timeline_view.py"]
        [Self_Evaluation_Loop] --> |"Issues found"| [LLM_Editor_Agent]
    end
```
**Sources:** [README.md:92-96](), [SKILL.md:83-91]()

---

### 1. Transcription and Ingestion
The pipeline begins by inventorying all source files and submitting them for transcription. This stage uses the **ElevenLabs Scribe API** to generate word-level timestamps, speaker diarization, and audio event tags like `(laughter)` [README.md:75-81](). Results are cached locally in the `edit/transcripts/` directory to prevent redundant API costs [SKILL.md:30-30]().

*   **Key Entities:** `transcribe.py`, `transcribe_batch.py`
*   **Output:** `edit/transcripts/<name>.json`
*   **For details, see [Transcription and Ingestion](#2.1)**

**Sources:** [SKILL.md:74-75](), [SKILL.md:48-48]()

### 2. Transcript Packing
Raw JSON transcripts are too verbose for LLM context windows. The packing stage processes these into `takes_packed.md`, a Markdown-formatted "reading view" [README.md:75-81](). It segments speech into phrases based on silence thresholds (default ≥ 0.5s) and labels speakers, making the footage searchable by text [SKILL.md:76-76]().

*   **Key Entities:** `pack_transcripts.py`
*   **Output:** `edit/takes_packed.md`
*   **For details, see [Transcript Packing (takes_packed.md)](#2.2)**

**Sources:** [SKILL.md:46-46](), [SKILL.md:76-76]()

### 3. Timeline View (Visual Drill-down)
When the LLM needs to see the video (e.g., to check a facial expression or verify a cut point), it calls `timeline_view.py` [README.md:83-84](). This generates a composite image containing a filmstrip, audio waveform, and word labels. This allows the LLM to "see" seconds of footage in a single token-efficient PNG [poster.html:42-46]().

*   **Key Entities:** `timeline_view.py`
*   **Usage:** On-demand during reasoning and self-evaluation [SKILL.md:77-77]().
*   **For details, see [Timeline View (Visual Composite Generator)](#2.3)**

**Sources:** [README.md:71-73](), [SKILL.md:77-77]()

### 4. Rendering Pipeline
The LLM expresses its editing decisions in an `edl.json` (Edit Decision List). The `render.py` script executes this list using a high-performance heuristic: it extracts segments individually, applies 30ms audio fades to prevent pops, and then performs a lossless concatenation [SKILL.md:23-24]().

*   **Key Entities:** `render.py`, `edl.json`
*   **Hard Rules:** 30ms fades, PTS shifting for overlays, subtitles applied last [SKILL.md:18-29]().
*   **For details, see [Rendering Pipeline (render.py)](#2.4)**

**Sources:** [SKILL.md:78-78](), [SKILL.md:47-47]()

### 5. Color Grading
Color grading is integrated into the segment extraction phase. The system can automatically analyze footage or apply named presets like `warm_cinematic` or `neutral_punch` [README.md:14-14](). It uses `ffmpeg` filter chains to perform the grade [SKILL.md:79-79]().

*   **Key Entities:** `grade.py`
*   **Presets:** `warm_cinematic`, `neutral_punch`, `subtle` [SKILL.md:79-79]().
*   **For details, see [Color Grading (grade.py)](#2.5)**

**Sources:** [SKILL.md:79-79](), [README.md:14-14]()

---

### Pipeline Logic: Code Entity Space

The following diagram maps the logical stages of the pipeline to the specific Python scripts and data structures defined in the codebase.

**Code Entity Relationship Diagram**
```mermaid
graph LR
    subgraph "CLI / Entry Points"
        ["transcribe_batch.py"]
        ["pack_transcripts.py"]
        ["render.py"]
    end

    subgraph "Core Logic"
        ["transcribe.py"] --> |"calls"| ["ElevenLabs Scribe"]
        ["render.py"] --> |"imports"| ["grade.py"]
        ["render.py"] --> |"executes"| ["edl.json"]
    end

    subgraph "Project State (edit)"
        ["takes_packed.md"]
        ["project.md"]
        ["master.srt"]
    end

    ["transcribe_batch.py"] --> ["transcribe.py"]
    ["pack_transcripts.py"] --> ["takes_packed.md"]
    ["render.py"] --> ["master.srt"]
    ["render.py"] --> ["final.mp4"]
```
**Sources:** [SKILL.md:37-56](), [SKILL.md:74-79]()

---

