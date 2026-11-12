<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/fineVideo · page 6 Content Annotation · fetched 2026-10-26 -->

# Content Annotation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contentannotation/gemini_prompt.txt](contentannotation/gemini_prompt.txt)
- [contentannotation/video2annotation.py](contentannotation/video2annotation.py)

</details>



The **Content Annotation** subsystem is the most compute-intensive and sophisticated stage of the FineVideo pipeline. It transforms raw video files into rich, structured JSON metadata. This stage leverages a dual-LLM approach: **Gemini 1.5 Pro** provides multimodal analysis of the video content, while **GPT-4o** (via the `instructor` library) enforces a strict schema on the resulting analysis.

### System Overview

The annotation process is orchestrated by the `VideoProcessor` class within `video2annotation.py` [[contentannotation/video2annotation.py:119-120]](). It follows a sequential flow from S3 retrieval to multimodal inference and finally structured data extraction.

**Key Components:**
*   **Multimodal Analysis:** Uses `gemini-1.5-pro-latest` to "watch" the video and generate a comprehensive natural language description based on a detailed prompt [[contentannotation/video2annotation.py:165-167]]().
*   **Schema Enforcement:** Uses the `instructor` library to wrap the OpenAI client, ensuring that the final output strictly adheres to a complex hierarchy of `TypedDict` objects [[contentannotation/video2annotation.py:38-115]]().
*   **Scalability:** The system uses a "worker/chunk" pattern, allowing multiple instances of the script to process different segments of a video list in parallel [[contentannotation/video2annotation.py:17-21]]().

### Annotation Workflow

The diagram below illustrates the flow of data from the S3 bucket through the two-stage LLM pipeline.

**Video Annotation Data Flow**
```mermaid
graph TD
    subgraph "Storage & Input"
        S3[("S3 Bucket: videos_minioracle/")]
        VList["--video-list (JSON)"]
    end

    subgraph "video2annotation.py (VideoProcessor)"
        DP["S3 Download"]
        GU["Gemini File Upload"]
        GP["Gemini 1.5 Pro Inference"]
        GS["instructor (GPT-4o) Structuring"]
    end

    subgraph "External APIs"
        GAPI["Google Generative AI API"]
        OAPI["OpenAI API"]
    end

    VList --> DP
    S3 -- "MP4 File" --> DP
    DP --> GU
    GU -- "genai.upload_file()" --> GAPI
    GAPI -- "video_file.state == 'PROCESSING'" --> GU
    GU --> GP
    GP -- "model.generate_content()" --> GAPI
    GAPI -- "gemini_text (Unstructured)" --> GP
    GP --> GS
    GS -- "instructor.patch(OpenAI)" --> OAPI
    OAPI -- "JSON (Schema TypedDict)" --> GS
    GS -- "Save Result" --> S3_Out[("S3: videos_minioracle_results/")]

    Sources: [contentannotation/video2annotation.py:119-204]()
```

### The Annotation Pipeline (`video2annotation.py`)
The pipeline is designed for robustness, implementing exponential backoff for Gemini API failures [[contentannotation/video2annotation.py:188-193]()] and recursive retries for GPT-4o when it encounters `IncompleteOutputException`. It manages the lifecycle of video files by uploading them to Google's servers, waiting for processing, and deleting them immediately after inference to maintain workspace hygiene [[contentannotation/video2annotation.py:132-143, 184-184]()] .

For a deep dive into the `VideoProcessor` implementation, CLI arguments, and retry logic, see **[Video Annotation Pipeline (`video2annotation.py`)](#6.1)**.

### Gemini Prompt & Output Schema
The quality of the annotation depends on a 24-line structured prompt found in `gemini_prompt.txt` [[contentannotation/gemini_prompt.txt:1-24]()] . This prompt instructs the model to identify characters, delineate scenes, calculate dynamism scores, and assess audio-visual correlation. The resulting data is mapped into a complex schema including:
*   **CharacterList:** Visual descriptions for identification [[contentannotation/video2annotation.py:38-41]()] .
*   **Scenes:** Timestamps, activities, props, and mood taxonomy [[contentannotation/video2annotation.py:75-90]()] .
*   **Storylines:** Narrative progression and climax identification [[contentannotation/video2annotation.py:95-99]()] .

For details on the prompt template and the specific attributes of the metadata schema, see **[Gemini Annotation Prompt & Output Schema](#6.2)**.

### Logical Entity Mapping
The following diagram bridges the high-level metadata concepts defined in the prompt to the specific code entities used to enforce them.

**Metadata Entity Mapping**
```mermaid
classDiagram
    class Schema {
        +List~Character~ characterList
        +List~Scene~ scenes
        +Storyline storylines
        +List~QAndA~ qAndA
    }
    class Scene {
        +Timestamps timestamps
        +List~Activity~ activities
        +List~Prop~ props
        +Mood mood
        +float dynamismScore
    }
    class Mood {
        +string description
        +List~KeyMoment~ keyMoments
    }
    class Storyline {
        +string description
        +List~int~ scenes
        +Climax climax
    }

    Schema *-- Character
    Schema *-- Scene
    Schema *-- Storyline
    Schema *-- QAndA
    Scene *-- Activity
    Scene *-- Prop
    Scene *-- Mood
    Mood *-- KeyMoment
    Storyline *-- Climax

    Sources: [contentannotation/video2annotation.py:38-115]()
```

---
**Sources:**
*   [contentannotation/video2annotation.py:1-204]()
*   [contentannotation/gemini_prompt.txt:1-24]()

---

