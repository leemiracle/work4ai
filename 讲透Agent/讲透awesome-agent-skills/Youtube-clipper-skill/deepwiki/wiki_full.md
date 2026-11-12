# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/REPOSITORY_SETTINGS.md](.github/REPOSITORY_SETTINGS.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)

</details>



## Purpose and Scope

The YouTube Clipper Skill is an AI-powered video processing system designed for the Claude Code environment. The system downloads YouTube videos, performs semantic content analysis using Claude AI, extracts video segments based on meaningful chapter boundaries, translates subtitles into bilingual formats, and optionally burns subtitles into video files. The skill operates as a natural language interface, accepting user commands through Claude Code and orchestrating a multi-stage processing pipeline.

This document provides an architectural overview of the system, its execution environment, core components, and processing workflow. For detailed feature descriptions, see [Key Features](#1.1). For system dependencies and installation requirements, see [System Requirements](#1.2). For operational usage patterns, see [Getting Started](#2). For in-depth technical implementation details, see [Architecture](#3) and [Core Scripts](#4).

**Sources:** [README.md:1-13](), [.github/REPOSITORY_SETTINGS.md:1-14]()

## Claude Code Skill Architecture

The YouTube Clipper Skill operates within the Claude Code execution environment, installed at `~/.claude/skills/youtube-clipper/`. The skill exposes functionality through natural language commands, with Claude Code interpreting user intent and invoking the appropriate Python scripts.

### Skill Deployment Model

```mermaid
graph TB
    User["User Natural Language Command"]
    Claude["Claude Code CLI"]
    SkillDir["~/.claude/skills/youtube-clipper/"]
    
    subgraph "Skill Installation"
        Install["install_as_skill.sh"]
        EnvTemplate[".env.example"]
        EnvFile[".env"]
    end
    
    subgraph "Python Script Layer"
        DownloadScript["scripts/download_video.py"]
        AnalyzeScript["scripts/analyze_subtitles.py"]
        ClipScript["scripts/clip_video.py"]
        ExtractScript["scripts/extract_subtitle_clip.py"]
        BurnScript["scripts/burn_subtitles.py"]
        UtilsModule["scripts/utils.py"]
    end
    
    subgraph "External Dependencies"
        YtDlp["yt-dlp CLI"]
        FFmpeg["ffmpeg binary"]
        PythonPkgs["Python packages:<br/>yt_dlp, pysrt, dotenv"]
    end
    
    User -->|"Clip this video: URL"| Claude
    Claude -->|"Invokes scripts"| SkillDir
    Install -->|"Creates"| SkillDir
    Install -->|"Copies"| EnvTemplate
    EnvTemplate -->|"User customizes"| EnvFile
    
    SkillDir --> DownloadScript
    SkillDir --> AnalyzeScript
    SkillDir --> ClipScript
    SkillDir --> ExtractScript
    SkillDir --> BurnScript
    
    DownloadScript --> UtilsModule
    AnalyzeScript --> UtilsModule
    ClipScript --> UtilsModule
    ExtractScript --> UtilsModule
    BurnScript --> UtilsModule
    
    DownloadScript --> YtDlp
    DownloadScript --> PythonPkgs
    ClipScript --> FFmpeg
    BurnScript --> FFmpeg
    ExtractScript --> PythonPkgs
```

The `install_as_skill.sh` script performs initial setup, creating the skill directory structure, installing Python dependencies (`yt-dlp`, `pysrt`, `python-dotenv`), verifying external tools (`yt-dlp`, `ffmpeg`), and generating the `.env` configuration file from `.env.example`.

**Sources:** [README.md:24-47](), [README.zh-CN.md:24-47]()

## Core Script Components

The skill's functionality is implemented across five primary Python scripts, each handling a specific processing stage. All scripts share common functionality through `utils.py`.

### Script Dependency Matrix

```mermaid
graph LR
    subgraph "Entry Points"
        DV["download_video.py"]
        AS["analyze_subtitles.py"]
        CV["clip_video.py"]
        ES["extract_subtitle_clip.py"]
        BS["burn_subtitles.py"]
    end
    
    subgraph "Shared Layer"
        Utils["utils.py"]
    end
    
    subgraph "Configuration"
        EnvFile[".env"]
        DotenvLib["python-dotenv"]
    end
    
    subgraph "External Libraries"
        YtDlpLib["yt_dlp module"]
        PysrtLib["pysrt module"]
    end
    
    subgraph "System Binaries"
        YtDlpBin["yt-dlp executable"]
        FFmpegBin["ffmpeg executable"]
    end
    
    DV --> Utils
    AS --> Utils
    CV --> Utils
    ES --> Utils
    BS --> Utils
    
    DV --> DotenvLib
    AS --> DotenvLib
    DV --> YtDlpLib
    ES --> PysrtLib
    
    DotenvLib --> EnvFile
    
    DV --> YtDlpBin
    CV --> FFmpegBin
    BS --> FFmpegBin
```

| Script | Primary Responsibility | Key Dependencies |
|--------|----------------------|------------------|
| `download_video.py` | Video acquisition, subtitle download | `yt_dlp`, `yt-dlp` binary, `utils.py` |
| `analyze_subtitles.py` | Subtitle parsing, data preparation for AI | `utils.py`, `.env` |
| `clip_video.py` | Video segment extraction | `ffmpeg`, `utils.py` |
| `extract_subtitle_clip.py` | Subtitle segment extraction, timestamp adjustment | `pysrt`, `utils.py` |
| `burn_subtitles.py` | Subtitle rendering into video | `ffmpeg` with libass, `utils.py` |
| `utils.py` | Time conversion, file operations, validation | Standard library only |

**Sources:** [README.md:50-66](), Diagram 3 from high-level systems

## Processing Pipeline

The skill executes a six-stage pipeline when processing a YouTube video:

### End-to-End Workflow

```mermaid
flowchart TB
    Start["User Command:<br/>Natural Language Input"]
    
    Stage1["Stage 1: Environment Detection<br/>Verify yt-dlp, ffmpeg, Python"]
    Stage2["Stage 2: Video Download<br/>download_video.py<br/>yt-dlp downloads MP4 + VTT"]
    Stage3["Stage 3: Subtitle Analysis<br/>analyze_subtitles.py<br/>Prepare data for Claude AI"]
    
    AIAnalysis["Claude AI Semantic Analysis<br/>Topic identification<br/>Chapter boundary detection<br/>Title & summary generation"]
    
    Stage4["Stage 4: User Selection<br/>Present chapters<br/>Gather processing options"]
    
    Stage5["Stage 5: Processing"]
    
    subgraph "Parallel Operations"
        Clip["clip_video.py<br/>FFmpeg extraction"]
        ExtractSub["extract_subtitle_clip.py<br/>Time-bound segment"]
        TransBatch["Batch Translation<br/>20-25 lines per call"]
        GenBilingual["Generate bilingual SRT"]
        BurnOp["burn_subtitles.py<br/>FFmpeg + libass"]
    end
    
    Stage6["Stage 6: Output Organization<br/>./youtube-clips/TIMESTAMP/<br/>Chapter_Title/"]
    
    End["Completion:<br/>Up to 4 files per chapter"]
    
    Start --> Stage1
    Stage1 --> Stage2
    Stage2 --> Stage3
    Stage3 --> AIAnalysis
    AIAnalysis --> Stage4
    Stage4 --> Stage5
    
    Stage5 --> Clip
    Stage5 --> ExtractSub
    ExtractSub --> TransBatch
    TransBatch --> GenBilingual
    Stage5 --> BurnOp
    
    Clip --> Stage6
    GenBilingual --> Stage6
    BurnOp --> Stage6
    Stage6 --> End
```

**Stage 1 (Environment Detection):** Validates presence of `python`, `yt-dlp`, and `ffmpeg` binaries. Checks for `libass` support in FFmpeg by testing filter availability.

**Stage 2 (Video Download):** Invokes `download_video.py`, which uses `yt_dlp` Python library to download video in MP4 format (max 1080p) and English subtitles in VTT format.

**Stage 3 (Subtitle Analysis):** Executes `analyze_subtitles.py` to parse VTT subtitles and format data for Claude AI analysis. Estimates target chapter count based on video duration and configured `TARGET_CHAPTER_DURATION`.

**Stage 4 (User Selection):** Claude AI analyzes subtitle content to generate semantic chapters (2-5 minutes each). User selects chapters for processing and specifies options (subtitle translation, burning, summary generation).

**Stage 5 (Processing):** 
- `clip_video.py` extracts video segments using FFmpeg with `-c copy` for lossless extraction
- `extract_subtitle_clip.py` extracts time-bound subtitle segments and adjusts timestamps
- Batch translation groups 20-25 subtitle lines per API call
- Bilingual SRT generation combines English and translated text
- `burn_subtitles.py` applies subtitles using FFmpeg `subtitles` filter

**Stage 6 (Output Organization):** Creates timestamped session directory (`YYYYMMDD_HHMMSS`) containing chapter subdirectories, each with up to four files: `*_clip.mp4`, `*_with_subtitles.mp4`, `*_bilingual.srt`, `*_summary.md`.

**Sources:** [README.md:103-111](), [README.zh-CN.md:103-111](), Diagram 2 from high-level systems

## Configuration System

The skill uses environment variables loaded from `.env` for runtime configuration. All scripts import `python-dotenv` and call `load_dotenv()` to access configuration.

### Configuration Categories

| Category | Key Variables | Affected Components |
|----------|--------------|---------------------|
| **Paths** | `FFMPEG_PATH`, `OUTPUT_DIR`, `TEMP_DIR` | All scripts |
| **Video** | `MAX_VIDEO_HEIGHT`, `YT_DLP_PROXY`, `YT_DLP_RATE_LIMIT` | `download_video.py` |
| **Subtitles** | `SUBTITLE_FONT_SIZE`, `SUBTITLE_MARGIN_V`, `TARGET_LANGUAGE` | `burn_subtitles.py`, translation logic |
| **Processing** | `TRANSLATION_BATCH_SIZE`, `TARGET_CHAPTER_DURATION`, `KEEP_TEMP_FILES` | `analyze_subtitles.py`, translation, cleanup |
| **Logging** | `LOG_LEVEL` | All scripts |

The `.env.example` template provides default values. The `install_as_skill.sh` script copies this to `.env` during installation. Scripts implement fallback defaults when variables are undefined.

**Sources:** [README.md:127-154](), [README.zh-CN.md:127-154](), Diagram 5 from high-level systems

## Output Structure

The skill generates a three-level directory hierarchy for organized output:

```
./youtube-clips/
└── YYYYMMDD_HHMMSS/          # Timestamped session
    ├── Chapter_1_Title/
    │   ├── Chapter_1_Title_clip.mp4              # Original segment (no subtitles)
    │   ├── Chapter_1_Title_with_subtitles.mp4    # Burned subtitles
    │   ├── Chapter_1_Title_bilingual.srt         # English + target language
    │   └── Chapter_1_Title_summary.md            # Social media content
    └── Chapter_2_Title/
        ├── Chapter_2_Title_clip.mp4
        ├── Chapter_2_Title_with_subtitles.mp4
        ├── Chapter_2_Title_bilingual.srt
        └── Chapter_2_Title_summary.md
```

The `utils.py` module provides `sanitize_filename()` to clean chapter titles for use as directory names, removing special characters (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`), replacing spaces with underscores, and limiting length to 100 characters.

**Sources:** [README.md:112-123](), [README.zh-CN.md:112-123](), Diagram 6 from high-level systems

## External Tool Integration

The skill integrates two external command-line tools as critical dependencies:

### yt-dlp Integration

`download_video.py` uses both the `yt_dlp` Python library and the `yt-dlp` command-line executable. The script constructs a format string for video quality selection (e.g., `"bestvideo[height<=1080]+bestaudio/best[height<=1080]"`), downloads subtitles with `writeautomaticsub=True`, and handles proxy configuration via `YT_DLP_PROXY`.

**Sources:** [README.md:50-66]()

### FFmpeg with libass Integration

`clip_video.py` invokes `ffmpeg` with stream copying (`-c copy`) for lossless video extraction. `burn_subtitles.py` requires `ffmpeg` compiled with `libass` support for the `subtitles` filter. The script detects FFmpeg variant (standard vs. `ffmpeg-full` on macOS) and verifies filter availability using `ffmpeg -filters`. Due to path handling issues with spaces, the script implements a temporary directory workaround, copying subtitle files to a temp location before processing.

**Sources:** [README.md:67-84](), [README.zh-CN.md:67-84]()

## AI-Powered Intelligence

The skill differentiates itself through two AI-powered capabilities:

### Semantic Chapter Analysis

Claude AI analyzes subtitle content to identify topic boundaries, generating chapters with:
- **Titles:** 10-20 characters, descriptive of content
- **Summaries:** 50-100 characters, core message
- **Keywords:** 3-5 terms for searchability
- **Time boundaries:** Natural transition points, not arbitrary time intervals

This contrasts with mechanical splitting (e.g., fixed 5-minute segments) by understanding semantic content flow.

**Sources:** [README.md:14-20, 193-209](), Diagram 4 from high-level systems

### Batch Translation Optimization

Instead of translating subtitles individually, the skill groups 20-25 subtitle lines into a single API call. This batch strategy achieves 95% reduction in API calls compared to one-by-one translation, reduces processing time by 10x, and maintains translation consistency through context preservation across batches.

**Sources:** [README.md:211-217](), [README.zh-CN.md:211-217](), Diagram 4 from high-level systems

## Technology Stack Summary

| Layer | Technologies | Purpose |
|-------|--------------|---------|
| **Runtime** | Python 3.8+ | Script execution |
| **Hosting** | Claude Code | Natural language interface, AI analysis |
| **Download** | yt-dlp (CLI + library) | YouTube video/subtitle acquisition |
| **Video Processing** | FFmpeg with libass | Clipping, subtitle burning |
| **Subtitle Parsing** | pysrt | SRT format manipulation |
| **Configuration** | python-dotenv | Environment variable management |
| **AI Services** | Claude AI API | Semantic analysis, translation |

**Sources:** [README.md:50-66](), [README.zh-CN.md:50-66]()

---

# Page: Key Features

# Key Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [SKILL.md](SKILL.md)

</details>



This document details the five distinguishing features that differentiate the YouTube Clipper Skill from simpler video processing tools. Each feature leverages AI intelligence, external tool integration, or optimization strategies to provide professional-grade video processing capabilities within the Claude Code environment.

For installation and setup procedures, see [Installation](#2.1). For understanding how these features fit into the overall processing workflow, see [Understanding the Workflow](#2.3).

---

## Feature Overview

The YouTube Clipper Skill provides five core capabilities:

| Feature | Implementation | Key Benefit |
|---------|---------------|-------------|
| **AI Semantic Chapter Generation** | Claude AI + `analyze_subtitles.py` | Content-aware segmentation vs mechanical time splitting |
| **Precise Video Clipping** | FFmpeg + `clip_video.py` | Frame-accurate extraction with quality preservation |
| **Batch-Optimized Bilingual Subtitles** | `extract_subtitle_clip.py` + translation batching | 95% API call reduction, 10x speed improvement |
| **Subtitle Burning** | FFmpeg libass + `burn_subtitles.py` | Hardcoded dual-language subtitles with custom styling |
| **Social Media Content Generation** | AI-powered summary generation | Platform-optimized copy for Xiaohongshu, Douyin, WeChat |

Sources: [README.md:14-21](), [SKILL.md:96-221]()

---

## 1. AI Semantic Chapter Generation

### Overview

The system uses Claude AI to analyze subtitle content semantically and generate meaningful 2-5 minute chapters based on topic boundaries, rather than arbitrary time intervals. This is the core differentiating feature that distinguishes this tool from mechanical video splitters.

### Technical Implementation

```mermaid
flowchart TB
    Input["YouTube Video<br/>Subtitles (.vtt)"]
    
    subgraph "analyze_subtitles.py"
        Parser["VTT Parser<br/>webvtt library"]
        Formatter["Subtitle Data Formatter"]
        Output["Structured JSON<br/>timestamps + text"]
    end
    
    subgraph "Claude AI Analysis"
        ContentUnderstanding["Content Understanding<br/>Semantic parsing"]
        TopicDetection["Topic Boundary Detection<br/>Transition identification"]
        MetadataGen["Chapter Metadata Generation<br/>titles, summaries, keywords"]
    end
    
    subgraph "Chapter Output"
        ChapterList["Chapter Array"]
        Metadata["For each chapter:<br/>- Title (10-20 chars)<br/>- Time range (MM:SS)<br/>- Summary (50-100 chars)<br/>- Keywords (3-5 terms)"]
    end
    
    Input --> Parser
    Parser --> Formatter
    Formatter --> Output
    Output --> ContentUnderstanding
    ContentUnderstanding --> TopicDetection
    TopicDetection --> MetadataGen
    MetadataGen --> ChapterList
    ChapterList --> Metadata
```

**Diagram: AI Semantic Chapter Analysis Pipeline - Code Entity Mapping**

The process involves two primary phases:

1. **Subtitle Parsing** ([scripts/analyze_subtitles.py]()): Converts VTT format to structured data
2. **AI Analysis** (Claude AI via SKILL.md workflow): Generates semantic chapters

### Chapter Generation Principles

The system follows specific guidelines for chapter creation as defined in [SKILL.md:122-127]():

| Principle | Specification | Reasoning |
|-----------|--------------|-----------|
| **Granularity** | 2-5 minutes per chapter | Balance between detail and usability |
| **Completeness** | 100% video coverage, no gaps | Ensures all content is accessible |
| **Semantic Coherence** | One topic per chapter | Each chapter is independently meaningful |
| **Natural Boundaries** | Topic transition points | Avoids mid-sentence or mid-thought cuts |

### Example Output Format

```
📊 Analysis Complete - 8 Chapters Generated:

1. [00:00 - 03:15] AGI as an exponential curve, not a point in time
   Core: AI model capabilities double every 4-12 months, engineers already using Claude Code
   Keywords: AGI, exponential growth, Claude Code

2. [03:15 - 06:30] China's gap in AI development
   Core: Chip embargo constrains China, DeepSeek benchmark optimization ≠ real capability
   Keywords: China, chip embargo, DeepSeek
```

This format is defined in [SKILL.md:128-143]() and provides users with sufficient context to make informed chapter selection decisions.

Sources: [SKILL.md:96-144](), [scripts/analyze_subtitles.py](), [README.md:16,193-209]()

---

## 2. Precise Video Clipping

### Overview

The system uses FFmpeg's stream copy capabilities to extract video segments with frame-level precision while preserving original quality. No re-encoding occurs unless subtitle burning is requested.

### Technical Implementation

```mermaid
flowchart LR
    Input["Original Video<br/>video.mp4"]
    
    subgraph "clip_video.py"
        TimeParser["Time String Parser<br/>utils.parse_time_to_seconds()"]
        FFmpegCmd["FFmpeg Command Builder<br/>-ss start -to end -c copy"]
        Executor["subprocess.run()"]
    end
    
    subgraph "FFmpeg Processing"
        SeekStart["-ss: Seek to start time<br/>Fast seek before decode"]
        CopyStreams["-c copy: Stream copy<br/>No re-encoding"]
        PreciseEnd["-to: End time<br/>Frame-accurate cutoff"]
    end
    
    Output["Chapter Clip<br/>chapter_clip.mp4<br/>Original quality"]
    
    Input --> TimeParser
    TimeParser --> FFmpegCmd
    FFmpegCmd --> Executor
    Executor --> SeekStart
    SeekStart --> CopyStreams
    CopyStreams --> PreciseEnd
    PreciseEnd --> Output
```

**Diagram: Video Clipping Process with FFmpeg Stream Copy**

### Key Implementation Details

The [scripts/clip_video.py]() script uses FFmpeg with the following command structure:

```bash
ffmpeg -ss <start_time> -to <end_time> -i <input_video> -c copy <output_clip>
```

**Critical Parameters**:

- `-ss` (start seek): Fast seek to chapter start position before decoding
- `-to` (end time): Precise end boundary using frame timestamps
- `-c copy`: Stream copy mode - no re-encoding, preserving original bitrate and codec
- `-avoid_negative_ts make_zero`: Ensures timestamps start at 0:00:00

### Quality Preservation

| Aspect | Original Video | Clipped Segment |
|--------|---------------|-----------------|
| Video codec | H.264/VP9 | Identical (stream copied) |
| Audio codec | AAC/Opus | Identical (stream copied) |
| Bitrate | As downloaded | Unchanged |
| Resolution | Up to 1080p | Unchanged |
| Processing speed | N/A | ~50x real-time (no decode) |

Sources: [scripts/clip_video.py](), [SKILL.md:170-176](), [README.md:17]()

---

## 3. Batch-Optimized Bilingual Subtitle Translation

### Overview

The system implements a batch translation strategy that groups 20-25 subtitle lines per API call, reducing API usage by 95% compared to line-by-line translation while maintaining context consistency.

### Translation Pipeline Architecture

```mermaid
flowchart TB
    OriginalSubs["Original Chapter Subtitles<br/>chapter_original.srt"]
    
    subgraph "extract_subtitle_clip.py"
        TimeFilter["Time-Bound Filter<br/>Extract segment range"]
        Adjuster["Timestamp Adjuster<br/>Rebase to 00:00:00"]
        SRTWriter["SRT Format Writer<br/>pysrt.SubRipFile"]
    end
    
    subgraph "Batch Translation Optimization"
        Grouper["Batch Grouper<br/>20-25 lines per batch"]
        APICall["Single Claude API Call<br/>Per batch translation"]
        ContextPreserve["Context Consistency<br/>Batch maintains flow"]
    end
    
    subgraph "Bilingual SRT Generator"
        Merger["Subtitle Merger<br/>EN line + CN line"]
        Formatter["Bilingual Format<br/>Two-line per entry"]
        Output["chapter_bilingual.srt<br/>English\\n中文"]
    end
    
    Metrics["Performance Metrics<br/>400 lines ÷ 20 = 20 calls<br/>vs. 400 calls (95% reduction)"]
    
    OriginalSubs --> TimeFilter
    TimeFilter --> Adjuster
    Adjuster --> SRTWriter
    SRTWriter --> Grouper
    Grouper --> APICall
    APICall --> ContextPreserve
    ContextPreserve --> Merger
    Merger --> Formatter
    Formatter --> Output
    
    Grouper -.-> Metrics
```

**Diagram: Batch Translation Pipeline with Optimization Strategy**

### Batch Translation Configuration

The batch size is configurable via [.env.example:15]():

```bash
# Translation batch size (20-25 recommended)
TRANSLATION_BATCH_SIZE=20
```

**Performance Comparison**:

| Approach | API Calls | Translation Time | Cost Impact |
|----------|-----------|------------------|-------------|
| Line-by-line | 400 calls (400 lines) | ~8 minutes | Baseline (100%) |
| Batch (size=20) | 20 calls (20 batches) | ~48 seconds | 5% of baseline |

### Bilingual Subtitle Format

The output format follows SRT standard with dual-language content as shown in [README.md:222-232]():

```srt
1
00:00:00,000 --> 00:00:03,500
This is the English subtitle
这是中文字幕

2
00:00:03,500 --> 00:00:07,000
Another English line
另一行中文
```

### Implementation Components

- **Subtitle Extraction**: [scripts/extract_subtitle_clip.py]() - Time-based filtering and timestamp adjustment
- **Format Conversion**: [scripts/utils.py]() - VTT to SRT conversion with `pysrt` library
- **Translation Strategy**: Defined in [SKILL.md:185-194]() and [SKILL.md:293-300]()
- **Target Language**: Configurable via `TARGET_LANGUAGE` environment variable

Sources: [scripts/extract_subtitle_clip.py](), [README.md:18,211-217,222-232](), [SKILL.md:185-194,293-300]()

---

## 4. Subtitle Burning with Advanced Styling

### Overview

The system uses FFmpeg with libass support to hardcode bilingual subtitles directly into video frames. This feature requires `ffmpeg-full` on macOS or `libass-dev` on Ubuntu, as standard FFmpeg builds lack subtitle filter support.

### Subtitle Burning Architecture

```mermaid
flowchart TB
    Inputs["Inputs:<br/>chapter_clip.mp4<br/>chapter_bilingual.srt"]
    
    subgraph "burn_subtitles.py"
        LibassCheck["libass Support Detection<br/>ffmpeg -filters | grep subtitles"]
        PathResolver["FFmpeg Path Resolution<br/>1. .env FFMPEG_PATH<br/>2. ffmpeg-full path<br/>3. system ffmpeg"]
        TempWorkaround["Temporary Directory Workaround<br/>Copies files to /tmp/<br/>Avoids space-in-path bug"]
    end
    
    subgraph "FFmpeg Subtitle Filter"
        SubtitlesFilter["subtitles filter<br/>Requires libass"]
        StyleConfig["Style Configuration:<br/>FontSize=24<br/>MarginV=30<br/>PrimaryColour=white<br/>OutlineColour=black"]
        VideoEncode["Video Encoding<br/>libx264 codec<br/>CRF=18 (high quality)"]
    end
    
    Output["chapter_with_subtitles.mp4<br/>Burned subtitles"]
    
    Inputs --> LibassCheck
    LibassCheck --> PathResolver
    PathResolver --> TempWorkaround
    TempWorkaround --> SubtitlesFilter
    SubtitlesFilter --> StyleConfig
    StyleConfig --> VideoEncode
    VideoEncode --> Output
```

**Diagram: Subtitle Burning Process with FFmpeg libass Integration**

### FFmpeg Variant Detection

The [scripts/burn_subtitles.py]() script implements a fallback chain for FFmpeg detection:

1. **Environment Variable**: `FFMPEG_PATH` from [.env.example:4-5]()
2. **ffmpeg-full Path** (macOS): `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
3. **System FFmpeg**: Standard `ffmpeg` in PATH

**libass Verification** ([SKILL.md:36-44]()):
```bash
ffmpeg -filters 2>&1 | grep subtitles
# Expected output: subtitles    V->V  (...)
```

### Critical Path Handling Issue

The subtitle burning process encounters a known FFmpeg bug where the `subtitles` filter cannot parse file paths containing spaces. The workaround is documented in [SKILL.md:285-292]():

**Problem**: 
```bash
# Fails if path contains spaces
ffmpeg -i "/path with spaces/video.mp4" -vf "subtitles=/path with spaces/subs.srt"
```

**Solution**: [scripts/burn_subtitles.py]() copies files to a temporary directory without spaces:
```python
# Create temporary directory
temp_dir = tempfile.mkdtemp()  # e.g., /tmp/tmpXXXXXX

# Copy files
shutil.copy(video_path, temp_dir)
shutil.copy(subtitle_path, temp_dir)

# Execute FFmpeg with temp paths
# Move output back to original destination
```

### Subtitle Styling Configuration

Configurable via [.env.example:17-19]():

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `SUBTITLE_FONT_SIZE` | 24 | Text size in points |
| `SUBTITLE_MARGIN_V` | 30 | Bottom margin in pixels |
| Primary text color | White | Main text color |
| Outline color | Black | Text border for readability |

### FFmpeg Command Structure

```bash
ffmpeg -i <video> -vf "subtitles=<srt>:force_style='FontSize=24,MarginV=30'" \
       -c:v libx264 -crf 18 -c:a copy <output>
```

**Parameters**:
- `-vf subtitles=<srt>`: Apply subtitle filter (requires libass)
- `force_style=`: Override default ASS/SSA styling
- `-c:v libx264`: Re-encode video with H.264
- `-crf 18`: Constant Rate Factor (18 = visually lossless)
- `-c:a copy`: Copy audio stream without re-encoding

Sources: [scripts/burn_subtitles.py](), [SKILL.md:202-212,285-292](), [README.md:19,67-83,242-250]()

---

## 5. Social Media Content Generation

### Overview

The system automatically generates platform-optimized content summaries for Xiaohongshu (小红书), Douyin (抖音), and WeChat (微信公众号) based on chapter metadata (title, summary, keywords).

### Content Generation Process

```mermaid
flowchart LR
    Input["Chapter Metadata:<br/>- Title (10-20 chars)<br/>- Summary (50-100 chars)<br/>- Keywords (3-5 terms)"]
    
    subgraph "AI Content Generation"
        Analyzer["Content Analyzer<br/>Extract key points"]
        ToneAdapter["Tone Adaptation<br/>Platform-specific style"]
        Formatter["Format Generator<br/>Markdown output"]
    end
    
    subgraph "Platform-Specific Outputs"
        XHS["Xiaohongshu Format:<br/>Emoji-rich<br/>Hashtags<br/>Short paragraphs"]
        Douyin["Douyin Format:<br/>Casual tone<br/>Call-to-action<br/>Trending topics"]
        WeChat["WeChat Format:<br/>Formal structure<br/>Longer content<br/>Section headers"]
    end
    
    Output["chapter_summary.md<br/>Multi-platform copy"]
    
    Input --> Analyzer
    Analyzer --> ToneAdapter
    ToneAdapter --> Formatter
    Formatter --> XHS
    Formatter --> Douyin
    Formatter --> WeChat
    XHS --> Output
    Douyin --> Output
    WeChat --> Output
```

**Diagram: Social Media Content Generation Pipeline**

### Generated Content Structure

Each `<chapter_title>_summary.md` file contains:

1. **Chapter Overview**: Title and time range
2. **Core Message**: Main takeaway in 1-2 sentences
3. **Platform-Specific Copy**:
   - Xiaohongshu version (emoji-rich, casual)
   - Douyin version (short-form, trending)
   - WeChat version (formal, detailed)
4. **Hashtag Suggestions**: Derived from keywords
5. **Publishing Tips**: Platform-specific guidance

### Target Language Configuration

The content generation respects the `TARGET_LANGUAGE` setting from [.env.example:21]():

```bash
# Target language for translation and summaries
TARGET_LANGUAGE=中文
```

This ensures all generated content matches the target audience language.

### Integration with Workflow

Content generation is triggered during [SKILL.md:213-221]() as optional processing:

```bash
python3 scripts/generate_summary.py <chapter_info>
```

**Input Format**:
```json
{
  "title": "AGI as an exponential curve",
  "summary": "AI capabilities double every 4-12 months...",
  "keywords": ["AGI", "exponential", "Claude Code"]
}
```

Sources: [README.md:20](), [SKILL.md:213-221](), [.env.example:21]()

---

## Feature Integration Matrix

The following table shows how multiple features combine during typical processing workflows:

| Use Case | AI Chapters | Clipping | Translation | Burning | Summary |
|----------|-------------|----------|-------------|---------|---------|
| **Quick Preview** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Bilingual Sharing** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Social Media Package** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Archive/Reference** | ✅ | ✅ | ✅ | ❌ | ✅ |

Each feature can be toggled independently via user selection in [SKILL.md:148-162]().

Sources: [SKILL.md:148-162](), [README.md:14-21]()

---

# Page: System Requirements

# System Requirements

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [install_as_skill.sh](install_as_skill.sh)

</details>



## Purpose and Scope

This page documents all software dependencies required to run the YouTube Clipper Skill. It covers system-level binaries, Python runtime requirements, and Python package dependencies. For installation procedures using these requirements, see [Installation](#2.1). For detailed configuration of these dependencies, see [Configuration](#6).

---

## Overview of Dependencies

The YouTube Clipper Skill requires three layers of dependencies that work together to process videos:

```mermaid
graph TB
    subgraph "Layer 1: System Binaries"
        Python["python3<br/>(3.8+)"]
        YtDlp["yt-dlp<br/>(CLI tool)"]
        FFmpeg["ffmpeg<br/>(with libass)"]
    end
    
    subgraph "Layer 2: Python Packages"
        YtDlpLib["yt_dlp<br/>(Python library)"]
        PySRT["pysrt<br/>(SRT parser)"]
        DotEnv["python-dotenv<br/>(Config loader)"]
    end
    
    subgraph "Layer 3: Core Scripts"
        Download["download_video.py"]
        Analyze["analyze_subtitles.py"]
        Clip["clip_video.py"]
        Burn["burn_subtitles.py"]
        Extract["extract_subtitle_clip.py"]
    end
    
    Python --> YtDlpLib
    Python --> PySRT
    Python --> DotEnv
    
    YtDlpLib --> Download
    PySRT --> Extract
    DotEnv --> Download
    DotEnv --> Analyze
    
    YtDlp --> Download
    FFmpeg --> Clip
    FFmpeg --> Burn
    
    Download --> Analyze
    Analyze --> Clip
    Clip --> Extract
    Extract --> Burn
```

**Diagram 1: Dependency Layer Architecture**

Sources: [README.md:50-66](), [install_as_skill.sh:109-191]()

---

## System Binaries

### Python 3.8+

**Requirement**: Python 3.8 or higher

**Purpose**: Executes all core processing scripts in the `scripts/` directory

**Verification**:
```bash
python3 --version
# Expected: Python 3.8.0 or higher
```

The installation script checks for Python at [install_as_skill.sh:110-117]():

```bash
if ! command_exists python3; then
    print_error "未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi
```

**Installation**:
- **macOS**: Pre-installed, or `brew install python@3.11`
- **Ubuntu/Debian**: `sudo apt install python3 python3-pip`
- **All platforms**: [python.org/downloads](https://www.python.org/downloads/)

Sources: [README.md:56](), [install_as_skill.sh:110-117]()

---

### yt-dlp (Command-Line Tool)

**Requirement**: Latest version of yt-dlp binary

**Purpose**: Downloads YouTube videos and subtitle tracks. Used by `download_video.py` to fetch content.

**Verification**:
```bash
yt-dlp --version
# Expected: 2023.XX.XX or later
```

The installation script verifies yt-dlp at [install_as_skill.sh:140-150]():

```bash
if command_exists yt-dlp; then
    YT_DLP_VERSION=$(yt-dlp --version)
    print_success "yt-dlp 已安装: $YT_DLP_VERSION"
else
    print_warning "yt-dlp 命令行工具未安装"
fi
```

**Installation**:

| Platform | Installation Command |
|----------|---------------------|
| **macOS** | `brew install yt-dlp` |
| **Ubuntu/Debian** | `sudo apt install yt-dlp` |
| **Arch Linux** | `sudo pacman -S yt-dlp` |
| **pip (all platforms)** | `pip install -U yt-dlp` |

**Note**: Both the CLI tool and Python library (`yt_dlp`) are required. They serve different purposes.

Sources: [README.md:57](), [install_as_skill.sh:140-150]()

---

### FFmpeg with libass Support

**Requirement**: FFmpeg compiled with libass filter support

**Purpose**: 
- **Video clipping**: Precise frame-accurate segment extraction ([clip_video.py]())
- **Subtitle burning**: Hardcoding subtitles into video frames ([burn_subtitles.py]())

**Critical**: The `libass` library is **required** for subtitle burning functionality. Standard FFmpeg installations on macOS do **not** include libass support.

**Verification**:

```bash
# Check FFmpeg version
ffmpeg -version

# Verify libass support (CRITICAL)
ffmpeg -filters 2>&1 | grep subtitles
# Expected output: subtitles    V->V  Render text subtitles onto input video using the libass library.
```

The installation script performs a comprehensive FFmpeg check at [install_as_skill.sh:153-191]():

```mermaid
flowchart TD
    Start["Check FFmpeg"]
    
    CheckFull1["Check /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg<br/>(Apple Silicon)"]
    CheckFull2["Check /usr/local/opt/ffmpeg-full/bin/ffmpeg<br/>(Intel Mac)"]
    CheckStd["Check standard ffmpeg command"]
    CheckLibass["ffmpeg -filters | grep subtitles"]
    
    FoundFull["FFMPEG_FOUND=true<br/>LIBASS_SUPPORTED=true"]
    FoundStd["FFMPEG_FOUND=true"]
    CheckLibassResult{"libass<br/>found?"}
    LibassTrue["LIBASS_SUPPORTED=true"]
    LibassFalse["LIBASS_SUPPORTED=false<br/>Warn user"]
    NotFound["FFMPEG_FOUND=false<br/>Error"]
    
    Start --> CheckFull1
    CheckFull1 -->|Exists| FoundFull
    CheckFull1 -->|Not found| CheckFull2
    CheckFull2 -->|Exists| FoundFull
    CheckFull2 -->|Not found| CheckStd
    CheckStd -->|Exists| FoundStd
    CheckStd -->|Not found| NotFound
    FoundStd --> CheckLibass
    CheckLibass --> CheckLibassResult
    CheckLibassResult -->|Yes| LibassTrue
    CheckLibassResult -->|No| LibassFalse
```

**Diagram 2: FFmpeg Detection Logic**

Sources: [install_as_skill.sh:153-191]()

---

#### Platform-Specific FFmpeg Installation

**macOS**:

The standard Homebrew `ffmpeg` package **does not include libass**. You must install `ffmpeg-full`:

```bash
# Remove standard ffmpeg if installed
brew uninstall ffmpeg

# Install ffmpeg-full with libass support
brew install ffmpeg-full
```

**Paths**:
- **Apple Silicon**: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
- **Intel Mac**: `/usr/local/opt/ffmpeg-full/bin/ffmpeg`

**Ubuntu/Debian**:

```bash
sudo apt install ffmpeg libass-dev
```

**Arch Linux**:

```bash
sudo pacman -S ffmpeg
# libass is included by default
```

Sources: [README.md:67-83](), [install_as_skill.sh:158-191](), [SKILL.md:310-318]()

---

## Python Package Dependencies

The following Python packages are automatically installed by `install_as_skill.sh` but can also be installed manually:

### yt_dlp (Python Library)

**Package**: `yt_dlp`

**Version**: Latest

**Purpose**: Python interface to yt-dlp functionality. Used by `download_video.py` to programmatically download videos.

**Installation**: 
```bash
pip install yt-dlp
```

**Usage in Code**: [scripts/download_video.py]() imports `yt_dlp` to configure download options.

---

### pysrt

**Package**: `pysrt`

**Version**: Latest

**Purpose**: Parse and manipulate SRT subtitle files. Used by `extract_subtitle_clip.py` to extract subtitle segments and adjust timestamps.

**Installation**:
```bash
pip install pysrt
```

**Usage in Code**: [scripts/extract_subtitle_clip.py]() uses `pysrt.open()` to read SRT files and manipulate subtitle timing.

---

### python-dotenv

**Package**: `python-dotenv`

**Version**: Latest

**Purpose**: Load environment variables from `.env` file. Used across all scripts to read configuration.

**Installation**:
```bash
pip install python-dotenv
```

**Usage in Code**: Scripts import `load_dotenv()` and `os.getenv()` to access configuration variables like `FFMPEG_PATH`, `MAX_VIDEO_HEIGHT`, etc.

---

### Installation of Python Packages

All three packages are installed by the setup script at [install_as_skill.sh:126-137]():

```bash
#尝试使用 pip3，如果不存在则使用 pip
if command_exists pip3; then
    pip3 install -q yt-dlp pysrt python-dotenv
else
    pip install -q yt-dlp pysrt python-dotenv
fi
```

**Manual Installation**:
```bash
pip install yt-dlp pysrt python-dotenv
```

Sources: [README.md:60-65](), [install_as_skill.sh:126-137]()

---

## Dependency Verification Matrix

The installation script systematically verifies all requirements. Here is the complete verification workflow:

```mermaid
graph TB
    Start["install_as_skill.sh"]
    
    subgraph "Python Verification"
        CheckPy["command_exists python3"]
        PyVer["python3 --version"]
        CheckPip["command_exists pip3/pip"]
    end
    
    subgraph "Package Installation"
        InstallPkg["pip install yt-dlp pysrt python-dotenv"]
        VerifyImport["python3 -c 'import yt_dlp'<br/>python3 -c 'import pysrt'"]
    end
    
    subgraph "Binary Verification"
        CheckYtDlp["command_exists yt-dlp"]
        YtDlpVer["yt-dlp --version"]
        CheckFFmpeg["Check ffmpeg-full paths<br/>or standard ffmpeg"]
        FFmpegVer["ffmpeg -version"]
        CheckLibass["ffmpeg -filters | grep subtitles"]
    end
    
    subgraph "Results"
        CreateEnv["Copy .env.example to .env"]
        Summary["Print installation summary<br/>with warnings if needed"]
    end
    
    Start --> CheckPy
    CheckPy -->|Pass| PyVer
    PyVer --> CheckPip
    CheckPip -->|Pass| InstallPkg
    InstallPkg --> VerifyImport
    VerifyImport --> CheckYtDlp
    CheckYtDlp --> YtDlpVer
    YtDlpVer --> CheckFFmpeg
    CheckFFmpeg --> FFmpegVer
    FFmpegVer --> CheckLibass
    CheckLibass --> CreateEnv
    CreateEnv --> Summary
```

**Diagram 3: Complete Dependency Verification Workflow**

Sources: [install_as_skill.sh:56-241]()

---

## Minimum Requirements Summary

| Component | Minimum Version | Verification Command | Installation Detection |
|-----------|----------------|---------------------|----------------------|
| **Python** | 3.8+ | `python3 --version` | [install_as_skill.sh:110-117]() |
| **pip** | Any | `pip3 --version` | [install_as_skill.sh:120-124]() |
| **yt-dlp (CLI)** | Latest | `yt-dlp --version` | [install_as_skill.sh:140-150]() |
| **FFmpeg** | Latest | `ffmpeg -version` | [install_as_skill.sh:153-179]() |
| **libass support** | Required | `ffmpeg -filters \| grep subtitles` | [install_as_skill.sh:173-178]() |
| **yt_dlp (Python)** | Latest | `python3 -c "import yt_dlp"` | [install_as_skill.sh:132-135]() |
| **pysrt** | Latest | `python3 -c "import pysrt"` | [install_as_skill.sh:132-135]() |
| **python-dotenv** | Latest | `python3 -c "import dotenv"` | [install_as_skill.sh:132-135]() |

Sources: [README.md:50-66](), [install_as_skill.sh:109-191]()

---

## Critical Dependency: libass

The `libass` library deserves special attention as it is the most common source of installation issues.

### Why libass is Required

The `burn_subtitles.py` script uses FFmpeg's `subtitles` filter to hardcode subtitle text onto video frames. This filter requires the `libass` library to render text with proper font rendering, positioning, and styling.

Without libass:
- Video clipping works normally
- Subtitle extraction works normally  
- **Subtitle burning fails** with error: `Option not found: subtitles`

### Detection Logic

The script checks for libass support at [install_as_skill.sh:173-178]():

```bash
# 检查 libass 支持
if ffmpeg -filters 2>&1 | grep -q "subtitles"; then
    print_success "FFmpeg 支持 libass（字幕烧录可用）"
    LIBASS_SUPPORTED=true
else
    print_warning "FFmpeg 不支持 libass（字幕烧录不可用）"
fi
```

### macOS-Specific Issue

Standard Homebrew FFmpeg (`brew install ffmpeg`) is compiled **without libass** on macOS. Users must install `ffmpeg-full`:

| Package | libass Support | Installation |
|---------|---------------|--------------|
| `ffmpeg` | ❌ No | `brew install ffmpeg` |
| `ffmpeg-full` | ✅ Yes | `brew install ffmpeg-full` |

The installation script explicitly checks for `ffmpeg-full` first at [install_as_skill.sh:158-166]():

```bash
# 检查 ffmpeg-full（macOS 推荐）
if [ -f "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg" ]; then
    print_success "ffmpeg-full 已安装（Apple Silicon）"
    FFMPEG_FOUND=true
    LIBASS_SUPPORTED=true
elif [ -f "/usr/local/opt/ffmpeg-full/bin/ffmpeg" ]; then
    print_success "ffmpeg-full 已安装（Intel Mac）"
    FFMPEG_FOUND=true
    LIBASS_SUPPORTED=true
```

Sources: [README.md:67-83](), [install_as_skill.sh:153-191](), [SKILL.md:34-44](), [SKILL.md:310-318]()

---

## Environment Variable for FFmpeg Path

If FFmpeg is installed in a non-standard location, you can specify the path via `.env`:

```bash
# In ~/.claude/skills/youtube-clipper/.env
FFMPEG_PATH=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
```

If `FFMPEG_PATH` is empty, scripts will use `ffmpeg` from `PATH`. This configuration is documented at [.env.example]().

For more on configuration options, see [Environment Variables Reference](#6.1).

Sources: [README.md:134-135]()

---

## Common Requirement Issues

### Missing Python
**Symptom**: `command not found: python3`

**Solution**: Install Python 3.8+ from [python.org](https://www.python.org/downloads/) or via package manager

---

### Missing yt-dlp CLI
**Symptom**: `command not found: yt-dlp`

**Solution**: Install via package manager or pip (see [yt-dlp Installation](#yt-dlp-command-line-tool))

---

### FFmpeg without libass
**Symptom**: `Option not found: subtitles` when burning subtitles

**Solution**: 
- **macOS**: Install `ffmpeg-full` (see [FFmpeg with libass Support](#ffmpeg-with-libass-support))
- **Linux**: Install `libass-dev` package

**Verification**: `ffmpeg -filters 2>&1 | grep subtitles` should produce output

---

### Package Import Errors
**Symptom**: `ModuleNotFoundError: No module named 'pysrt'`

**Solution**: Reinstall Python packages:
```bash
pip install --force-reinstall yt-dlp pysrt python-dotenv
```

For more troubleshooting, see [Installation Issues](#8.1).

Sources: [README.md:236-250](), [install_as_skill.sh:140-191]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [install_as_skill.sh](install_as_skill.sh)

</details>



This page provides a quick start guide for installing and using the YouTube Clipper Skill for the first time. It covers the essential steps to get the skill operational within the Claude Code environment, perform a first video clipping operation, and understand the basic workflow.

For detailed installation procedures, see [Installation](#2.1). For comprehensive usage patterns, see [Basic Usage](#2.2). For in-depth workflow mechanics, see [Understanding the Workflow](#2.3).

## Prerequisites Overview

Before installing the YouTube Clipper Skill, verify that your system meets the required dependencies. The skill requires both system-level tools and Python packages.

### Required System Dependencies

| Dependency | Minimum Version | Purpose | Verification Command |
|------------|----------------|---------|---------------------|
| Python | 3.8+ | Script execution runtime | `python3 --version` |
| yt-dlp | Latest stable | YouTube video/subtitle download | `yt-dlp --version` |
| FFmpeg with libass | Latest stable | Video processing and subtitle burning | `ffmpeg -filters 2>&1 \| grep subtitles` |

### Critical Dependency: libass Support

The standard `ffmpeg` package on macOS (via Homebrew) does **not** include libass support, which is required for subtitle burning functionality. Users must install `ffmpeg-full` instead:

```bash
brew uninstall ffmpeg
brew install ffmpeg-full
```

The installation script [install_as_skill.sh:153-191]() performs automatic detection of FFmpeg variants and verifies libass support.

**Diagram: Dependency Detection Flow**

```mermaid
flowchart TB
    Start["install_as_skill.sh execution"]
    
    CheckPython["Check Python 3.8+<br/>(line 111)"]
    CheckPip["Check pip availability<br/>(line 120)"]
    InstallPyPkgs["pip3 install yt-dlp pysrt python-dotenv<br/>(line 132)"]
    
    CheckYtDlp["Check yt-dlp command<br/>(line 141)"]
    
    CheckFFmpegFull["Check /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg<br/>(line 159)"]
    CheckFFmpegStd["Check ffmpeg command<br/>(line 167)"]
    CheckLibass["ffmpeg -filters | grep subtitles<br/>(line 173)"]
    
    CreateEnv["Copy .env.example to .env<br/>(line 198)"]
    Complete["Installation complete"]
    
    Start --> CheckPython
    CheckPython --> CheckPip
    CheckPip --> InstallPyPkgs
    InstallPyPkgs --> CheckYtDlp
    CheckYtDlp --> CheckFFmpegFull
    
    CheckFFmpegFull -->|"Found"| CreateEnv
    CheckFFmpegFull -->|"Not found"| CheckFFmpegStd
    CheckFFmpegStd -->|"Found"| CheckLibass
    CheckFFmpegStd -->|"Not found"| Complete
    CheckLibass --> CreateEnv
    CreateEnv --> Complete
```

Sources: [install_as_skill.sh:109-191]()

## Installation Quick Start

The YouTube Clipper Skill provides two installation methods. The recommended approach uses `npx skills` for automatic installation.

### Method 1: npx skills (Recommended)

```bash
npx skills add https://github.com/op7418/Youtube-clipper-skill
```

This command automatically:
1. Clones the repository
2. Copies files to `~/.claude/skills/youtube-clipper/`
3. Executes [install_as_skill.sh]()
4. Installs Python dependencies
5. Creates configuration files

### Method 2: Manual Installation

```bash
git clone https://github.com/op7418/Youtube-clipper-skill.git
cd Youtube-clipper-skill
bash install_as_skill.sh
```

The [install_as_skill.sh:56-241]() script performs the following operations:

1. **Directory Setup** [install_as_skill.sh:60-79](): Creates `~/.claude/skills/youtube-clipper/` directory structure
2. **File Copy** [install_as_skill.sh:82-107](): Copies all source files, excluding `.git/`, `venv/`, `__pycache__/`, and `youtube-clips/`
3. **Python Package Installation** [install_as_skill.sh:127-137](): Installs `yt-dlp`, `pysrt`, `python-dotenv` via pip
4. **Dependency Verification** [install_as_skill.sh:139-191](): Checks yt-dlp and FFmpeg availability
5. **Configuration Generation** [install_as_skill.sh:194-208](): Creates `.env` from `.env.example`

For detailed installation procedures including troubleshooting, see [Installation](#2.1).

Sources: [README.md:24-47](), [install_as_skill.sh:1-241]()

## Directory Structure After Installation

The installation process creates the following directory structure at `~/.claude/skills/youtube-clipper/`:

```mermaid
graph TB
    Root["~/.claude/skills/youtube-clipper/"]
    
    Scripts["scripts/<br/>Python modules"]
    DownloadPy["download_video.py"]
    AnalyzePy["analyze_subtitles.py"]
    ClipPy["clip_video.py"]
    BurnPy["burn_subtitles.py"]
    ExtractPy["extract_subtitle_clip.py"]
    UtilsPy["utils.py"]
    
    Config[".env<br/>User configuration"]
    ConfigEx[".env.example<br/>Configuration template"]
    
    Docs["Documentation"]
    SkillMd["SKILL.md<br/>Workflow instructions"]
    ReadmeMd["README.md<br/>User guide"]
    TechMd["TECHNICAL_NOTES.md<br/>Implementation details"]
    
    Refs["references/<br/>Technical references"]
    
    Root --> Scripts
    Root --> Config
    Root --> ConfigEx
    Root --> Docs
    Root --> Refs
    
    Scripts --> DownloadPy
    Scripts --> AnalyzePy
    Scripts --> ClipPy
    Scripts --> BurnPy
    Scripts --> ExtractPy
    Scripts --> UtilsPy
    
    Docs --> SkillMd
    Docs --> ReadmeMd
    Docs --> TechMd
```

The `.env` file contains runtime configuration variables that control video quality, subtitle settings, and processing parameters. See [Configuration](#6) for complete variable reference.

Sources: [install_as_skill.sh:82-107](), [README.md:129-153]()

## First Run Example

After installation, invoke the skill through Claude Code using natural language commands. The skill responds to commands in both English and Chinese.

### Basic Invocation

```
Clip this YouTube video: https://youtube.com/watch?v=VIDEO_ID
```

or in Chinese:

```
剪辑这个 YouTube 视频：https://youtube.com/watch?v=VIDEO_ID
```

**Diagram: Natural Language to Code Entity Mapping**

```mermaid
flowchart LR
    UserCmd["User natural language:<br/>'Clip this YouTube video: URL'"]
    
    SkillEntry["SKILL.md workflow<br/>Claude Code parser"]
    
    Phase1["Phase 1: Environment Detection<br/>Verify dependencies"]
    Phase2["Phase 2: download_video.py<br/>Download video + subtitles"]
    Phase3["Phase 3: analyze_subtitles.py<br/>AI semantic analysis"]
    Phase4["Phase 4: User selection<br/>AskUserQuestion tool"]
    Phase5["Phase 5: Processing<br/>clip_video.py, burn_subtitles.py"]
    Phase6["Phase 6: Output<br/>./youtube-clips/TIMESTAMP/"]
    
    UserCmd --> SkillEntry
    SkillEntry --> Phase1
    Phase1 --> Phase2
    Phase2 --> Phase3
    Phase3 --> Phase4
    Phase4 --> Phase5
    Phase5 --> Phase6
```

The skill follows the workflow defined in [SKILL.md:21-278](), which specifies six distinct processing phases. Each phase invokes specific Python scripts from the `scripts/` directory.

For complete usage patterns and command variations, see [Basic Usage](#2.2).

Sources: [README.md:87-111](), [SKILL.md:21-49]()

## Six-Stage Processing Workflow Overview

The YouTube Clipper Skill executes a six-stage sequential workflow. Each stage is clearly defined in [SKILL.md]() and corresponds to specific Python scripts.

**Diagram: Workflow Stage to Script Mapping**

```mermaid
flowchart TB
    Stage1["Stage 1: Environment Detection<br/>SKILL.md:25-63"]
    Stage2["Stage 2: Video Download<br/>SKILL.md:68-93"]
    Stage3["Stage 3: AI Chapter Analysis<br/>SKILL.md:98-143"]
    Stage4["Stage 4: User Selection<br/>SKILL.md:148-161"]
    Stage5["Stage 5: Processing<br/>SKILL.md:166-234"]
    Stage6["Stage 6: Output Organization<br/>SKILL.md:238-278"]
    
    EnvCheck["Bash commands:<br/>yt-dlp --version<br/>ffmpeg -filters"]
    DownloadScript["scripts/download_video.py<br/>Uses yt_dlp library"]
    AnalyzeScript["scripts/analyze_subtitles.py<br/>Parses VTT subtitles"]
    ClaudeAI["Claude AI API<br/>Semantic content analysis"]
    
    ClipScript["scripts/clip_video.py<br/>FFmpeg video extraction"]
    ExtractScript["scripts/extract_subtitle_clip.py<br/>pysrt time adjustment"]
    BurnScript["scripts/burn_subtitles.py<br/>FFmpeg libass filter"]
    
    OutputDir["./youtube-clips/<br/>YYYYMMDD_HHMMSS/<br/>Chapter_Title/"]
    
    Stage1 --> EnvCheck
    Stage2 --> DownloadScript
    Stage3 --> AnalyzeScript
    AnalyzeScript --> ClaudeAI
    Stage4 --> |"AskUserQuestion tool"| Stage5
    
    Stage5 --> ClipScript
    Stage5 --> ExtractScript
    Stage5 --> BurnScript
    
    Stage6 --> OutputDir
```

### Stage Summary

1. **Environment Detection** [SKILL.md:25-63](): Verifies yt-dlp, FFmpeg with libass, and Python dependencies
2. **Video Download** [SKILL.md:68-93](): Invokes [scripts/download_video.py]() to download video (max 1080p) and English subtitles (VTT format)
3. **AI Chapter Analysis** [SKILL.md:98-143](): Uses [scripts/analyze_subtitles.py]() to parse subtitles, then applies Claude AI to generate semantic chapters (2-5 minutes each)
4. **User Selection** [SKILL.md:148-161](): Prompts user to select chapters and processing options (subtitles, burning, summary)
5. **Processing** [SKILL.md:166-234](): Executes [scripts/clip_video.py](), [scripts/extract_subtitle_clip.py](), [scripts/burn_subtitles.py]() for each selected chapter
6. **Output Organization** [SKILL.md:238-278](): Creates timestamped directory structure in `./youtube-clips/`

For detailed workflow mechanics, see [Understanding the Workflow](#2.3).

Sources: [SKILL.md:21-278](), [README.md:103-111]()

## Output Files Generated

For each processed chapter, the skill generates up to four file types in the output directory structure.

**Diagram: Output File Generation Pipeline**

```mermaid
flowchart LR
    ClipVideo["scripts/clip_video.py"]
    ExtractSub["scripts/extract_subtitle_clip.py"]
    TranslateSub["Translation via Claude AI<br/>Batch processing: 20-25 lines"]
    BurnSub["scripts/burn_subtitles.py"]
    GenSummary["Summary generation<br/>via Claude AI"]
    
    OutputClip["Chapter_Title_clip.mp4<br/>Original video segment"]
    OutputBilingual["Chapter_Title_bilingual.srt<br/>English + Target language"]
    OutputBurned["Chapter_Title_with_subtitles.mp4<br/>Hardcoded subtitles"]
    OutputSummary["Chapter_Title_summary.md<br/>Social media content"]
    
    ClipVideo --> OutputClip
    ExtractSub --> TranslateSub
    TranslateSub --> OutputBilingual
    OutputBilingual --> BurnSub
    BurnSub --> OutputBurned
    GenSummary --> OutputSummary
```

### Output Directory Structure

```
./youtube-clips/20260122_143022/
└── Chapter_Title/
    ├── Chapter_Title_clip.mp4              # Original clip (no subtitles)
    ├── Chapter_Title_with_subtitles.mp4    # Burned subtitles version
    ├── Chapter_Title_bilingual.srt         # Bilingual subtitle file
    └── Chapter_Title_summary.md            # Social media summary
```

The directory naming follows the pattern defined in [SKILL.md:242-261]():
- Timestamp format: `YYYYMMDD_HHMMSS`
- Chapter titles sanitized: special characters removed, spaces replaced with underscores
- Maximum filename length: 100 characters

Sources: [README.md:113-123](), [SKILL.md:242-261](), [SKILL.md:340-350]()

## Verification Steps

After installation, verify that the skill is properly configured by checking the following:

### 1. Verify Installation Directory

```bash
ls -la ~/.claude/skills/youtube-clipper/
```

Expected output should include:
- `scripts/` directory with Python modules
- `.env` configuration file
- `SKILL.md`, `README.md`, `TECHNICAL_NOTES.md`

### 2. Verify Python Dependencies

```bash
cd ~/.claude/skills/youtube-clipper
python3 -c "import yt_dlp; print('✅ yt-dlp available')"
python3 -c "import pysrt; print('✅ pysrt available')"
python3 -c "import dotenv; print('✅ python-dotenv available')"
```

### 3. Verify FFmpeg libass Support

```bash
ffmpeg -filters 2>&1 | grep subtitles
```

Expected output: `subtitles    V->V  (...)`

If this test fails, the subtitle burning functionality will not work. Install `ffmpeg-full` as described in [System Requirements](#1.2).

### 4. Test Script Execution

```bash
cd ~/.claude/skills/youtube-clipper
python3 scripts/download_video.py --help
```

This should display usage information without errors.

Sources: [install_as_skill.sh:139-191](), [SKILL.md:25-63]()

## Configuration File Location

The skill configuration is stored in `~/.claude/skills/youtube-clipper/.env`. This file is created by copying [.env.example]() during installation [install_as_skill.sh:196-208]().

Key configuration variables include:

```bash
FFMPEG_PATH=                    # Auto-detected if empty
OUTPUT_DIR=./youtube-clips      # Relative to working directory
MAX_VIDEO_HEIGHT=1080           # 720, 1080, 1440, or 2160
TRANSLATION_BATCH_SIZE=20       # Optimize API calls
TARGET_LANGUAGE=中文            # Translation target
TARGET_CHAPTER_DURATION=180     # Seconds (2-5 min recommended)
```

For complete configuration reference, see [Configuration](#6) and [Environment Variables Reference](#6.1).

Sources: [README.md:129-153](), [install_as_skill.sh:194-208]()

## Next Steps

After successful installation and verification:

1. **Run First Clipping Operation**: See [Basic Usage](#2.2) for command examples
2. **Understand Workflow Stages**: See [Understanding the Workflow](#2.3) for detailed stage explanations
3. **Configure Advanced Settings**: See [Configuration](#6) for customization options
4. **Explore AI Features**: See [AI Semantic Analysis](#7.2) and [Batch Translation Optimization](#7.1)
5. **Troubleshoot Issues**: See [Troubleshooting](#8) for common problems and solutions

The skill is now ready to use. Invoke it through Claude Code with a YouTube URL to begin processing.

Sources: [README.md:87-189](), [SKILL.md:364-373]()

---

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [install_as_skill.sh](install_as_skill.sh)

</details>



This document details the installation process for the YouTube Clipper Skill, including both automated installation methods, dependency setup, directory structure creation, and verification procedures. For system requirements and prerequisite software versions, see [System Requirements](#1.2). For troubleshooting installation problems, see [Installation Issues](#8.1).

## Installation Methods

The YouTube Clipper Skill provides two installation methods: automated installation via `npx skills` and manual installation via the `install_as_skill.sh` script. Both methods install the skill to `~/.claude/skills/youtube-clipper/` and set up all required dependencies.

### Method 1: npx skills (Recommended)

```bash
npx skills add https://github.com/op7418/Youtube-clipper-skill
```

This command automatically clones the repository and executes the installation script, placing the skill in the Claude Code skills directory at `~/.claude/skills/youtube-clipper/`.

**Sources:** [README.md:26-32]()

### Method 2: Manual Installation

```bash
git clone https://github.com/op7418/Youtube-clipper-skill.git
cd Youtube-clipper-skill
bash install_as_skill.sh
```

The manual method provides more visibility into the installation process and is useful for debugging or custom installations.

**Sources:** [README.md:34-46]()

## Installation Process Flow

The installation process consists of multiple phases executed by the `install_as_skill.sh` script. The following diagram maps each installation phase to specific functions and code sections in the installation script:

```mermaid
flowchart TB
    Start["Installation Start<br/>(bash install_as_skill.sh)"]
    
    DetermineDir["Phase 1: Determine Target Directory<br/>SKILL_DIR=$HOME/.claude/skills/youtube-clipper<br/>[install_as_skill.sh:60]"]
    
    CheckExisting["Phase 2: Check Existing Installation<br/>if [ -d $SKILL_DIR ]<br/>[install_as_skill.sh:64-74]"]
    
    Decision{Directory<br/>Exists?}
    
    Prompt["Prompt User: Overwrite?<br/>read -p 'y/N'<br/>[install_as_skill.sh:66-71]"]
    
    Remove["Remove Old Installation<br/>rm -rf $SKILL_DIR<br/>[install_as_skill.sh:73]"]
    
    CreateDir["Phase 3: Create Skill Directory<br/>mkdir -p $SKILL_DIR<br/>[install_as_skill.sh:78]"]
    
    CopyFiles["Phase 4: Copy Project Files<br/>cp -r $SCRIPT_DIR/* $SKILL_DIR/<br/>[install_as_skill.sh:82-106]"]
    
    Cleanup["Cleanup: Remove Unwanted Files<br/>.git, venv, __pycache__, youtube-clips<br/>[install_as_skill.sh:91-105]"]
    
    CheckPython["Phase 5: Check Python 3<br/>command_exists python3<br/>[install_as_skill.sh:110-117]"]
    
    CheckPip["Phase 6: Check pip<br/>command_exists pip3/pip<br/>[install_as_skill.sh:120-124]"]
    
    InstallPython["Phase 7: Install Python Dependencies<br/>pip3 install yt-dlp pysrt python-dotenv<br/>[install_as_skill.sh:127-137]"]
    
    CheckYtDlp["Phase 8: Verify yt-dlp CLI<br/>command_exists yt-dlp<br/>[install_as_skill.sh:140-150]"]
    
    CheckFFmpeg["Phase 9: Verify FFmpeg + libass<br/>ffmpeg -filters 2>&1 | grep subtitles<br/>[install_as_skill.sh:153-191]"]
    
    CreateEnv["Phase 10: Create .env File<br/>cp .env.example .env<br/>[install_as_skill.sh:194-208]"]
    
    Complete["Installation Complete<br/>print_header 'Installation Complete!'<br/>[install_as_skill.sh:211-234]"]
    
    Start --> DetermineDir
    DetermineDir --> CheckExisting
    CheckExisting --> Decision
    Decision -->|Yes| Prompt
    Decision -->|No| CreateDir
    Prompt -->|Yes| Remove
    Prompt -->|No| Complete
    Remove --> CreateDir
    CreateDir --> CopyFiles
    CopyFiles --> Cleanup
    Cleanup --> CheckPython
    CheckPython --> CheckPip
    CheckPip --> InstallPython
    InstallPython --> CheckYtDlp
    CheckYtDlp --> CheckFFmpeg
    CheckFFmpeg --> CreateEnv
    CreateEnv --> Complete
```

**Sources:** [install_as_skill.sh:1-242]()

## Dependency Installation Details

The installation script manages three categories of dependencies: Python runtime, Python packages, and system binaries.

### Python Packages

The following Python packages are installed via `pip3` or `pip`:

| Package | Purpose | Installation Line |
|---------|---------|-------------------|
| `yt-dlp` | YouTube video downloading (Python library) | [install_as_skill.sh:132-135]() |
| `pysrt` | SRT subtitle file parsing | [install_as_skill.sh:132-135]() |
| `python-dotenv` | Environment variable loading from `.env` | [install_as_skill.sh:132-135]() |

The installation uses the `-q` flag for quiet installation and attempts `pip3` first, falling back to `pip` if unavailable.

**Sources:** [install_as_skill.sh:127-137](), [README.md:62-65]()

### System Binary Detection

The script verifies but does not install system binaries. Detection logic:

```mermaid
flowchart TB
    CheckYtDlp["Check yt-dlp Binary<br/>command_exists yt-dlp"]
    
    YtDlpFound{Found?}
    
    ShowVersion["Display Version<br/>yt-dlp --version<br/>[install_as_skill.sh:142]"]
    
    ShowInstall["Display Installation Instructions<br/>macOS: brew install yt-dlp<br/>Ubuntu: sudo apt-get install yt-dlp<br/>[install_as_skill.sh:146-149]"]
    
    CheckFFmpegFull["Check ffmpeg-full (macOS)<br/>/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg<br/>[install_as_skill.sh:159-166]"]
    
    FFmpegFullFound{Found?}
    
    CheckStandard["Check Standard ffmpeg<br/>command_exists ffmpeg<br/>[install_as_skill.sh:167-170]"]
    
    StandardFound{Found?}
    
    CheckLibass["Check libass Support<br/>ffmpeg -filters 2>&1 | grep subtitles<br/>[install_as_skill.sh:173]"]
    
    LibassSupported{Supported?}
    
    FullSupport["LIBASS_SUPPORTED=true<br/>FFMPEG_FOUND=true"]
    
    PartialSupport["FFMPEG_FOUND=true<br/>LIBASS_SUPPORTED=false<br/>Warning: subtitle burning unavailable"]
    
    NoFFmpeg["FFMPEG_FOUND=false<br/>Display installation instructions<br/>[install_as_skill.sh:182-190]"]
    
    CheckYtDlp --> YtDlpFound
    YtDlpFound -->|Yes| ShowVersion
    YtDlpFound -->|No| ShowInstall
    ShowVersion --> CheckFFmpegFull
    ShowInstall --> CheckFFmpegFull
    
    CheckFFmpegFull --> FFmpegFullFound
    FFmpegFullFound -->|Yes| FullSupport
    FFmpegFullFound -->|No| CheckStandard
    
    CheckStandard --> StandardFound
    StandardFound -->|Yes| CheckLibass
    StandardFound -->|No| NoFFmpeg
    
    CheckLibass --> LibassSupported
    LibassSupported -->|Yes| FullSupport
    LibassSupported -->|No| PartialSupport
```

**Sources:** [install_as_skill.sh:140-191]()

### FFmpeg libass Detection Logic

The script prioritizes `ffmpeg-full` on macOS because it includes libass support by default. Detection order:

1. Check `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` (Apple Silicon)
2. Check `/usr/local/opt/ffmpeg-full/bin/ffmpeg` (Intel Mac)
3. Check standard `ffmpeg` in PATH and verify libass support via filter listing

The libass verification command:
```bash
ffmpeg -filters 2>&1 | grep subtitles
```

If this command finds the `subtitles` filter, libass support is confirmed. Without libass, the `burn_subtitles.py` script cannot function.

**Sources:** [install_as_skill.sh:153-191](), [README.md:67-83]()

## Directory Structure Created

The installation creates the following directory structure at `~/.claude/skills/youtube-clipper/`:

```mermaid
graph TB
    Root["~/.claude/skills/youtube-clipper/<br/>(SKILL_DIR variable)"]
    
    Scripts["scripts/<br/>Python modules"]
    Refs["references/<br/>Technical documentation"]
    GitHub[".github/<br/>Repository metadata"]
    
    EnvExample[".env.example<br/>Configuration template"]
    Env[".env<br/>User configuration<br/>(created from .env.example)"]
    
    Readme["README.md"]
    ReadmeCN["README.zh-CN.md"]
    SkillMd["SKILL.md"]
    TechNotes["TECHNICAL_NOTES.md"]
    
    InstallScript["install_as_skill.sh<br/>(installation script)"]
    
    Root --> Scripts
    Root --> Refs
    Root --> GitHub
    Root --> EnvExample
    Root --> Env
    Root --> Readme
    Root --> ReadmeCN
    Root --> SkillMd
    Root --> TechNotes
    Root --> InstallScript
```

**Excluded from installation** (removed by cleanup phase):
- `.git/` directory ([install_as_skill.sh:91-93]())
- `venv/` directory ([install_as_skill.sh:94-96]())
- `__pycache__/` directories ([install_as_skill.sh:97-99]())
- `youtube-clips/` directory ([install_as_skill.sh:100-102]())
- Existing `.env` file (to prevent overwriting user configuration) ([install_as_skill.sh:103-105]())

**Sources:** [install_as_skill.sh:82-106]()

## Environment Configuration File Creation

The installation script creates a `.env` file from the `.env.example` template:

```mermaid
flowchart LR
    Template[".env.example<br/>(Template with defaults)"]
    
    Check["Check Template Exists<br/>if [ -f .env.example ]<br/>[install_as_skill.sh:196]"]
    
    Copy["Copy Template<br/>cp .env.example .env<br/>[install_as_skill.sh:198]"]
    
    Result[".env<br/>(User configuration file)"]
    
    Template --> Check
    Check -->|Exists| Copy
    Copy --> Result
```

The `.env` file location: `~/.claude/skills/youtube-clipper/.env`

Users can customize this file to override default settings. For detailed configuration options, see [Configuration](#6).

**Sources:** [install_as_skill.sh:194-208]()

## Installation Output and Verification

The installation script uses color-coded output functions to indicate status:

| Function | Purpose | Used For |
|----------|---------|----------|
| `print_info()` | Blue info messages | Progress updates ([install_as_skill.sh:26-28]()) |
| `print_success()` | Green success messages | Completion confirmations ([install_as_skill.sh:30-32]()) |
| `print_warning()` | Yellow warnings | Non-critical issues ([install_as_skill.sh:34-36]()) |
| `print_error()` | Red error messages | Critical failures ([install_as_skill.sh:38-40]()) |
| `print_header()` | Section headers | Phase separators ([install_as_skill.sh:42-48]()) |

### Successful Installation Output

A successful installation displays:

1. Installation location: `~/.claude/skills/youtube-clipper/`
2. Python version detected
3. Installed Python packages: `yt-dlp`, `pysrt`, `python-dotenv`
4. yt-dlp version (if installed)
5. FFmpeg version and libass support status
6. `.env` file creation confirmation
7. Usage instructions and documentation links

### Verification Steps

After installation, verify the following:

**Check Skill Directory:**
```bash
ls -la ~/.claude/skills/youtube-clipper/
```

Expected files: `scripts/`, `.env`, `README.md`, `SKILL.md`, etc.

**Verify Python Dependencies:**
```bash
python3 -c "import yt_dlp, pysrt, dotenv; print('All packages installed')"
```

**Verify yt-dlp CLI:**
```bash
yt-dlp --version
```

**Verify FFmpeg with libass:**
```bash
ffmpeg -filters 2>&1 | grep subtitles
```

Expected output: `subtitles    V->V  (...)`

**Sources:** [install_as_skill.sh:211-234]()

## Error Handling

The installation script includes error handling via the `trap` command:

```bash
trap 'print_error "安装过程中发生错误"; exit 1' ERR
```

This ensures that any command failure (with `set -e` enabled at [install_as_skill.sh:16]()) triggers an error message and clean exit.

The `set -e` flag causes the script to exit immediately if any command returns a non-zero status, preventing partial installations.

**Sources:** [install_as_skill.sh:16](), [install_as_skill.sh:238]()

## Post-Installation Next Steps

After successful installation:

1. **Review Configuration**: Edit `~/.claude/skills/youtube-clipper/.env` to customize settings (see [Configuration](#6))
2. **Verify System Dependencies**: Ensure yt-dlp and FFmpeg are properly installed if warnings were displayed
3. **Test the Skill**: Follow the usage instructions in [Basic Usage](#2.2)
4. **Review Documentation**: Read `SKILL.md` for detailed workflow information

If installation issues occur, consult [Installation Issues](#8.1) for troubleshooting guidance.

**Sources:** [README.md:87-110](), [install_as_skill.sh:224-233]()

---

# Page: Basic Usage

# Basic Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [SKILL.md](SKILL.md)

</details>



This page explains how to invoke the YouTube Clipper Skill through Claude Code using natural language commands and describes what to expect during execution. For detailed information about the six-stage processing pipeline, see [Understanding the Workflow](#2.3). For installation instructions, see [Installation](#2.1).

## Purpose and Scope

This document covers the basic interaction patterns for using the YouTube Clipper Skill: invoking the skill with natural language commands, responding to interactive prompts, and understanding the output files. It does not cover internal architecture details (see [Architecture](#3)), individual script implementations (see [Core Scripts](#4)), or advanced configuration options (see [Configuration](#6)).

---

## Skill Invocation

The YouTube Clipper Skill is invoked through Claude Code using natural language commands. The skill is registered with the Claude Code platform via the skill definition file at [SKILL.md:1-15]().

### Natural Language Commands

Users can invoke the skill with various natural language patterns:

**English commands:**
```
Clip this YouTube video: https://youtube.com/watch?v=VIDEO_ID
```

**Chinese commands:**
```
剪辑这个 YouTube 视频：https://youtube.com/watch?v=VIDEO_ID
```

**Variations:**
```
Extract clips from this video: <URL>
Download and clip this YouTube video: <URL>
Create short clips from this lecture: <URL>
```

The skill recognizes keywords like "clip", "剪辑", "YouTube", and "video" to trigger activation. The skill definition at [SKILL.md:3-6]() specifies the description and keywords used for skill matching.

### Command Flow Diagram

```mermaid
flowchart LR
    User["User"]
    CC["Claude Code CLI"]
    SkillMatcher["Skill Matcher"]
    SkillEntry["SKILL.md<br/>Skill Entry Point"]
    
    subgraph "Python Scripts Layer"
        Download["scripts/download_video.py"]
        Analyze["scripts/analyze_subtitles.py"]
        Clip["scripts/clip_video.py"]
        Burn["scripts/burn_subtitles.py"]
        Extract["scripts/extract_subtitle_clip.py"]
    end
    
    User -->|"Natural Language Command"| CC
    CC --> SkillMatcher
    SkillMatcher -->|"Matches keywords"| SkillEntry
    SkillEntry -->|"Stage 1: Environment Check"| SkillEntry
    SkillEntry -->|"Stage 2: Download"| Download
    SkillEntry -->|"Stage 3: Analyze"| Analyze
    SkillEntry -->|"Stage 4: User Selection"| User
    User -->|"Chapter choices"| SkillEntry
    SkillEntry -->|"Stage 5: Clip"| Clip
    SkillEntry -->|"Stage 5: Extract/Translate"| Extract
    SkillEntry -->|"Stage 5: Burn"| Burn
    SkillEntry -->|"Stage 6: Output"| User
```

**Sources:** [SKILL.md:1-15](), [README.md:87-111]()

---

## Six-Stage Execution Flow

When invoked, the skill executes a six-stage workflow. Users interact at specific decision points while Claude Code handles the technical execution.

### Stage Overview Diagram

```mermaid
flowchart TB
    Start["User Command"]
    
    Stage1["Stage 1: Environment Detection<br/>Verify yt-dlp, FFmpeg, Python"]
    Stage2["Stage 2: Video Download<br/>scripts/download_video.py"]
    Stage3["Stage 3: AI Chapter Analysis<br/>scripts/analyze_subtitles.py + Claude AI"]
    Stage4["Stage 4: User Selection<br/>AskUserQuestion tool"]
    Stage5["Stage 5: Processing<br/>scripts/clip_video.py, burn_subtitles.py, etc."]
    Stage6["Stage 6: Output Organization<br/>./youtube-clips/TIMESTAMP/"]
    
    End["Completion"]
    
    Start --> Stage1
    Stage1 -->|"Dependencies OK"| Stage2
    Stage1 -->|"Missing deps"| Error1["Error: Install missing tools"]
    
    Stage2 -->|"Download success"| Stage3
    Stage2 -->|"Network error"| Error2["Error: Check URL/network"]
    
    Stage3 -->|"Analysis complete"| Stage4
    
    Stage4 -->|"User confirms chapters"| Stage5
    Stage4 -->|"User cancels"| End
    
    Stage5 -->|"Processing complete"| Stage6
    Stage5 -->|"FFmpeg error"| Error3["Error: Check FFmpeg libass"]
    
    Stage6 --> End
```

**Sources:** [SKILL.md:21-279](), [README.md:104-111]()

---

## Interactive Prompts

The skill requires user input at two key points during execution.

### Chapter Selection Prompt

After AI analysis (Stage 3), Claude Code presents generated chapters and asks the user to select which ones to clip.

**Example interaction:**
```
📊 分析完成，生成 8 个章节：

1. [00:00 - 03:15] AGI 不是时间点，是指数曲线
   核心: AI 模型能力每 4-12 月翻倍，工程师已用 Claude 写代码
   关键词: AGI、指数增长、Claude Code

2. [03:15 - 06:30] 中国在 AI 上的差距
   核心: 芯片禁运卡住中国，DeepSeek benchmark 优化不代表实力
   关键词: 中国、芯片禁运、DeepSeek

[... more chapters ...]

Which chapters would you like to clip? (e.g., 1,3,5 or all)
```

The chapter analysis logic is implemented in [SKILL.md:96-144](), which uses Claude AI to perform semantic analysis rather than mechanical time-based splitting.

### Processing Options Prompt

After chapter selection, the skill asks about optional processing steps:

**Example interaction:**
```
Processing options:
- Generate bilingual subtitles? (English + Chinese) [Y/n]
- Burn subtitles into video? (hardcoded) [Y/n]
- Generate social media summary? [Y/n]
```

These options control which processing scripts are invoked:
- Bilingual subtitles: [scripts/extract_subtitle_clip.py]() + translation
- Subtitle burning: [scripts/burn_subtitles.py]()
- Summary generation: `scripts/generate_summary.py` (if implemented)

**Sources:** [SKILL.md:148-162](), [SKILL.md:164-221]()

---

## Progress Monitoring

During Stage 5 (Processing), the skill displays real-time progress for each chapter being processed.

### Progress Display Format

```
🎬 开始处理章节 1/3: AGI 不是时间点，是指数曲线

1/6 剪辑视频片段... ✅
2/6 提取字幕片段... ✅
3/6 翻译字幕为中文... [=====>    ] 50% (26/52)
4/6 生成双语字幕文件... ✅
5/6 烧录字幕到视频... ✅
6/6 生成总结文案... ✅

✨ 章节 1 处理完成
```

### Processing Steps Mapping

| Progress Step | Script Invoked | Purpose |
|--------------|----------------|---------|
| 1/6 剪辑视频片段 | [scripts/clip_video.py]() | Extract video segment with FFmpeg |
| 2/6 提取字幕片段 | [scripts/extract_subtitle_clip.py]() | Extract and adjust subtitle timestamps |
| 3/6 翻译字幕 | Translation logic in skill | Batch translate subtitles (20-25 lines per API call) |
| 4/6 生成双语字幕 | Subtitle merging logic | Combine English and Chinese into single SRT |
| 5/6 烧录字幕 | [scripts/burn_subtitles.py]() | Hardcode subtitles using FFmpeg with libass |
| 6/6 生成总结 | Summary generation logic | Create social media content |

**Sources:** [SKILL.md:164-235](), [README.md:104-111]()

---

## Output Structure

All processed files are organized in a timestamped directory structure under `./youtube-clips/` in the current working directory.

### Directory Layout

```
./youtube-clips/
└── YYYYMMDD_HHMMSS/                    # Timestamp of processing session
    ├── Chapter_Title_1/                 # Sanitized chapter title
    │   ├── Chapter_Title_1_clip.mp4              # Original clip (no subtitles)
    │   ├── Chapter_Title_1_with_subtitles.mp4    # Video with burned subtitles
    │   ├── Chapter_Title_1_bilingual.srt         # Bilingual subtitle file
    │   └── Chapter_Title_1_summary.md            # Social media content
    ├── Chapter_Title_2/
    │   └── [same file structure]
    └── Chapter_Title_3/
        └── [same file structure]
```

### Output File Types

| File Type | Naming Convention | Description | Always Generated? |
|-----------|------------------|-------------|-------------------|
| Clipped Video | `*_clip.mp4` | Original video segment without subtitles | ✅ Yes |
| Burned Subtitles | `*_with_subtitles.mp4` | Video with hardcoded bilingual subtitles | ⚠️ Optional |
| Bilingual SRT | `*_bilingual.srt` | Subtitle file with English + target language | ⚠️ Optional |
| Summary | `*_summary.md` | Social media content and chapter summary | ⚠️ Optional |

### File Naming Sanitization

The skill automatically sanitizes chapter titles for use as filenames by:
- Removing special characters: `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`
- Replacing spaces with underscores
- Limiting length to 100 characters

This logic is referenced in [SKILL.md:340-350]() and [README.md:270-277]().

**Sources:** [SKILL.md:238-275](), [README.md:112-123]()

---

## File Path and Execution Context

### Skill Installation Location

The skill is installed at `~/.claude/skills/youtube-clipper/` with the following structure:

```
~/.claude/skills/youtube-clipper/
├── SKILL.md                  # Skill definition and workflow
├── .env                      # Configuration file
├── .env.example             # Configuration template
└── scripts/                 # Python processing scripts
    ├── download_video.py
    ├── analyze_subtitles.py
    ├── clip_video.py
    ├── burn_subtitles.py
    ├── extract_subtitle_clip.py
    └── utils.py
```

### Script Execution Pattern

All Python scripts are executed from the skill directory context:

```bash
cd ~/.claude/skills/youtube-clipper
python3 scripts/<script_name>.py <arguments>
```

This execution pattern is consistent throughout the skill workflow as seen in [SKILL.md:74-77]() for video download and similar patterns for other scripts.

**Sources:** [SKILL.md:74-77](), [SKILL.md:100-102](), [README.md:32-46]()

---

## Example Session

### Complete Usage Example

**User command:**
```
Clip this YouTube video: https://youtube.com/watch?v=Ckt1cj0xjRM
```

**Stage 1 output:**
```
✓ Checking dependencies...
  ✓ yt-dlp: 2024.12.6
  ✓ FFmpeg: 6.1.1 (with libass support)
  ✓ Python packages: yt_dlp, pysrt, python-dotenv
```

**Stage 2 output:**
```
📥 Downloading video...
  Title: "AGI and the Future of AI Development"
  Duration: 42:30
  Resolution: 1920x1080
  
✓ Downloaded: Ckt1cj0xjRM.mp4 (156 MB)
✓ Subtitles: Ckt1cj0xjRM.en.vtt (52 KB)
```

**Stage 3 output:**
```
📊 AI 章节分析完成，生成 12 个章节：

1. [00:00 - 03:15] AGI definition and exponential growth
2. [03:15 - 06:30] China's AI development gap
3. [06:30 - 09:45] Impact of chip bans
[... 9 more chapters ...]

✓ All content covered, no gaps
```

**Stage 4 prompts:**
```
Which chapters would you like to clip? > 1,2,3

Processing options:
- Generate bilingual subtitles? (English + 中文) [Y/n] > Y
- Burn subtitles into video? [Y/n] > Y
- Generate social media summary? [Y/n] > Y
```

**Stage 5 progress:**
```
🎬 Processing chapter 1/3: AGI_definition_and_exponential_growth

1/6 Clipping video segment... ✅
2/6 Extracting subtitle segment... ✅
3/6 Translating subtitles... [=========>] 100% (52/52)
4/6 Creating bilingual subtitle file... ✅
5/6 Burning subtitles to video... ✅
6/6 Generating summary... ✅

✨ Chapter 1 complete (18.4 MB)

[Progress for chapters 2 and 3...]
```

**Stage 6 output:**
```
✨ Processing complete!

📁 Output directory: ./youtube-clips/20260122_143022/

Files generated:
  📂 AGI_definition_and_exponential_growth/
     🎬 AGI_definition_and_exponential_growth_clip.mp4 (14.2 MB)
     🎬 AGI_definition_and_exponential_growth_with_subtitles.mp4 (18.4 MB)
     📄 AGI_definition_and_exponential_growth_bilingual.srt (2.3 KB)
     📝 AGI_definition_and_exponential_growth_summary.md (1.8 KB)
  
  [... chapters 2 and 3 ...]

Preview command:
  open ./youtube-clips/20260122_143022/
```

**Sources:** [README.md:157-189](), [SKILL.md:21-279]()

---

## Command-Line Tool Mapping

The skill invokes several external tools through Python scripts. Understanding this mapping helps when troubleshooting.

### Tool Invocation Chain

```mermaid
flowchart TB
    SkillMD["SKILL.md<br/>Claude Code Execution"]
    
    subgraph "Python Scripts"
        DL["download_video.py"]
        AS["analyze_subtitles.py"]
        CV["clip_video.py"]
        BS["burn_subtitles.py"]
        ESC["extract_subtitle_clip.py"]
    end
    
    subgraph "External Binaries"
        YtDlp["yt-dlp<br/>Video download"]
        FFmpegClip["ffmpeg<br/>Stream copy"]
        FFmpegBurn["ffmpeg-full<br/>with libass"]
    end
    
    subgraph "Python Libraries"
        YtDlpLib["yt_dlp library"]
        Pysrt["pysrt library"]
    end
    
    SkillMD -->|"python3 scripts/download_video.py"| DL
    SkillMD -->|"python3 scripts/analyze_subtitles.py"| AS
    SkillMD -->|"python3 scripts/clip_video.py"| CV
    SkillMD -->|"python3 scripts/burn_subtitles.py"| BS
    SkillMD -->|"python3 scripts/extract_subtitle_clip.py"| ESC
    
    DL --> YtDlpLib
    YtDlpLib --> YtDlp
    
    AS --> Pysrt
    ESC --> Pysrt
    
    CV --> FFmpegClip
    BS --> FFmpegBurn
```

### Environment Detection Commands

During Stage 1, the skill executes these verification commands:

| Check | Command | Expected Output |
|-------|---------|----------------|
| yt-dlp version | `yt-dlp --version` | Version number (e.g., 2024.12.6) |
| FFmpeg version | `ffmpeg -version` | Version and configuration |
| FFmpeg libass | `ffmpeg -filters 2>&1 \| grep subtitles` | `subtitles V->V` filter listed |
| Python yt_dlp | `python3 -c "import yt_dlp"` | No error |
| Python pysrt | `python3 -c "import pysrt"` | No error |

These checks are specified in [SKILL.md:25-50]().

**Sources:** [SKILL.md:25-63](), [README.md:50-66]()

---

## Configuration Impact on Usage

While basic usage works with default settings, users can customize behavior through the `.env` file at `~/.claude/skills/youtube-clipper/.env`.

### Key Settings for Basic Usage

| Setting | Default | Impact on Usage |
|---------|---------|-----------------|
| `OUTPUT_DIR` | `./youtube-clips` | Changes where output files are saved |
| `MAX_VIDEO_HEIGHT` | `1080` | Limits video download resolution |
| `TARGET_LANGUAGE` | `中文` | Changes translation target language |
| `TRANSLATION_BATCH_SIZE` | `20` | Affects translation speed and API usage |
| `TARGET_CHAPTER_DURATION` | `180` | Guides AI chapter length (seconds) |

For complete configuration details, see [Configuration](#6).

**Sources:** [README.md:127-153](), [.env.example]()

---

## Error Scenarios and User Response

### Common Error Messages

**Missing dependencies:**
```
❌ Error: yt-dlp not found
Please install: brew install yt-dlp
```

**FFmpeg without libass:**
```
❌ Error: FFmpeg does not support subtitle burning
Your FFmpeg installation is missing libass support.

macOS: brew install ffmpeg-full
Ubuntu: sudo apt install ffmpeg libass-dev
```

**Network error during download:**
```
❌ Error: Failed to download video
Check your internet connection and YouTube URL
```

**Invalid URL:**
```
❌ Error: Invalid YouTube URL
Expected format: https://youtube.com/watch?v=VIDEO_ID
```

### User Actions for Errors

The skill provides actionable error messages with installation commands. Users typically need to:

1. **For dependency errors:** Run the suggested installation command, then retry
2. **For network errors:** Check connection, proxy settings in `.env`, then retry
3. **For URL errors:** Verify the YouTube URL format and retry

Error handling logic is described in [SKILL.md:321-337]().

**Sources:** [SKILL.md:321-337](), [README.md:236-278]()

---

## Next Steps

After completing a basic usage session, users may want to:

- **Understand the detailed workflow:** See [Understanding the Workflow](#2.3) for in-depth explanation of each stage
- **Customize configuration:** See [Configuration](#6) for all available settings
- **Learn about AI features:** See [AI Semantic Analysis](#7.2) and [Batch Translation Optimization](#7.1)
- **Troubleshoot issues:** See [Troubleshooting](#8) for common problems and solutions
- **Understand output formats:** See [Bilingual Subtitle Format](#7.3)

**Sources:** [README.md:1-320](), [SKILL.md:1-374]()

---

# Page: Understanding the Workflow

# Understanding the Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [SKILL.md](SKILL.md)

</details>



This document walks through the six-stage processing pipeline that executes when you ask Claude Code to clip a YouTube video. Each stage is explained with its purpose, key operations, involved scripts, and expected outputs. This provides a practical understanding of what happens behind the scenes when the skill runs.

For detailed technical implementation of each script, see [Core Scripts](#4). For AI integration specifics, see [AI Integration](#3.3). For configuration of workflow behavior, see [Configuration](#6).

---

## Workflow Overview

The YouTube Clipper Skill executes as a sequential six-stage pipeline. Each stage depends on the successful completion of the previous stage, with user interaction at strategic decision points.

```mermaid
flowchart TD
    Start["User Command:<br/>\"Clip this YouTube video: URL\""]
    
    Stage1["Stage 1: Environment Detection<br/>verify_dependencies()"]
    Stage2["Stage 2: Video Download<br/>download_video.py"]
    Stage3["Stage 3: AI Semantic Analysis<br/>analyze_subtitles.py + Claude AI"]
    Stage4["Stage 4: User Selection<br/>AskUserQuestion tool"]
    Stage5["Stage 5: Processing Execution<br/>clip_video.py, extract_subtitle_clip.py<br/>burn_subtitles.py"]
    Stage6["Stage 6: Output Organization<br/>File structure creation"]
    
    End["Complete:<br/>./youtube-clips/TIMESTAMP/"]
    
    Start --> Stage1
    Stage1 -->|Dependencies OK| Stage2
    Stage1 -->|Missing deps| Error1["Installation guidance"]
    
    Stage2 -->|Video + Subs downloaded| Stage3
    Stage2 -->|Download failed| Error2["Network/URL error"]
    
    Stage3 -->|Chapters generated| Stage4
    Stage3 -->|Analysis failed| Error3["Subtitle parsing error"]
    
    Stage4 -->|Chapters selected| Stage5
    Stage4 -->|User cancelled| End
    
    Stage5 -->|Processing complete| Stage6
    Stage5 -->|FFmpeg error| Error5["Processing failure"]
    
    Stage6 --> End
    
    Error1 -.->|User fixes| Stage1
    Error2 -.->|Retry| Stage2
    Error3 -.->|Retry| Stage3
    Error5 -.->|Troubleshoot| Stage5
```

**Sources:** [SKILL.md:22-275](), [README.md:103-110]()

---

## Stage 1: Environment Detection

**Purpose:** Verify all required dependencies are available before attempting any processing.

The skill checks three categories of dependencies:

### System Binaries

```mermaid
graph LR
    Check["Environment Detection"]
    
    subgraph "Binary Checks"
        YtDlp["yt-dlp --version"]
        FFmpeg1["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -version"]
        FFmpeg2["ffmpeg -version"]
        Libass["ffmpeg -filters 2>&1 | grep subtitles"]
    end
    
    subgraph "Python Imports"
        Import1["import yt_dlp"]
        Import2["import pysrt"]
        Import3["import dotenv"]
    end
    
    Check --> YtDlp
    Check --> FFmpeg1
    Check --> FFmpeg2
    Check --> Libass
    Check --> Import1
    Check --> Import2
    Check --> Import3
    
    YtDlp -->|Exists| Pass1["✅ Video downloader OK"]
    YtDlp -->|Missing| Fail1["❌ Install yt-dlp"]
    
    FFmpeg1 -->|Exists + libass| Pass2["✅ ffmpeg-full OK"]
    FFmpeg1 -->|Missing| FFmpeg2
    FFmpeg2 -->|Exists + libass| Pass2
    FFmpeg2 -->|No libass| Fail2["❌ Install ffmpeg-full"]
    
    Import1 -->|Success| Pass3["✅ Python deps OK"]
    Import1 -->|Failed| Fail3["❌ pip install yt-dlp"]
```

### Key Detection Commands

| Component | Detection Command | Expected Output |
|-----------|------------------|-----------------|
| yt-dlp | `yt-dlp --version` | Version string |
| FFmpeg (preferred) | `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -version` | FFmpeg version with libass |
| FFmpeg (fallback) | `ffmpeg -version` | FFmpeg version |
| libass support | `ffmpeg -filters 2>&1 \| grep subtitles` | `subtitles V->V` filter listing |
| yt_dlp module | `python3 -c "import yt_dlp"` | No output (success) |
| pysrt module | `python3 -c "import pysrt"` | No output (success) |

### Critical Requirement: libass

The standard Homebrew `ffmpeg` package does **not** include libass support, which is required for [burn_subtitles.py]() to function. The skill specifically checks for `ffmpeg-full` at [/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg]() on macOS systems.

**Sources:** [SKILL.md:25-63](), [README.md:67-83](), [README.md:239-250]()

---

## Stage 2: Video Download

**Purpose:** Acquire the video file and English subtitles from YouTube.

This stage is handled by [scripts/download_video.py](), which wraps the `yt-dlp` library with specific configuration for quality and subtitle handling.

```mermaid
flowchart LR
    Input["YouTube URL"]
    Script["download_video.py"]
    
    subgraph "yt-dlp Operations"
        Format["Format Selection:<br/>bestvideo[height<=1080]+bestaudio/best[height<=1080]"]
        VideoDownload["Download MP4<br/>video_id.mp4"]
        SubDownload["Download Subtitles<br/>Priority: Manual EN > Auto EN"]
        SubFormat["Convert to VTT<br/>video_id.en.vtt"]
    end
    
    Output1["video_id.mp4<br/>(Video file)"]
    Output2["video_id.en.vtt<br/>(Subtitle file)"]
    Metadata["Video metadata:<br/>- Title<br/>- Duration<br/>- File size"]
    
    Input --> Script
    Script --> Format
    Format --> VideoDownload
    Format --> SubDownload
    SubDownload --> SubFormat
    
    VideoDownload --> Output1
    SubFormat --> Output2
    Script --> Metadata
```

### Download Configuration

The script applies these constraints:

- **Video quality:** Maximum 1080p (configurable via `MAX_VIDEO_HEIGHT`)
- **Format:** MP4 container with H.264 video and AAC audio
- **Subtitle language:** English (manual subtitles preferred, auto-generated as fallback)
- **Subtitle format:** VTT (WebVTT) with timestamps
- **Filename:** Uses video ID to avoid special character issues (e.g., `dQw4w9WgXcQ.mp4`)

### Output Files

| File | Pattern | Purpose |
|------|---------|---------|
| Video | `{video_id}.mp4` | Source video for clipping |
| Subtitles | `{video_id}.en.vtt` | English subtitles for analysis |

**Sources:** [SKILL.md:67-93](), [README.md:57](), [.env.example:15-22]()

---

## Stage 3: AI Semantic Analysis

**Purpose:** Generate meaningful chapters based on content understanding, not mechanical time splitting.

This is the **core differentiator** of the skill. It involves two components:

1. [scripts/analyze_subtitles.py]() - Parses VTT format and prepares subtitle data
2. Claude AI - Performs semantic analysis to identify topic boundaries

```mermaid
flowchart TB
    VTT["video_id.en.vtt<br/>(VTT format)"]
    Parser["analyze_subtitles.py<br/>VTT parser"]
    
    subgraph "Subtitle Data Preparation"
        Parse["Parse VTT entries"]
        Extract["Extract:<br/>- Timestamps<br/>- Text content<br/>- Cue identifiers"]
        Format["Format as structured JSON"]
    end
    
    subgraph "Claude AI Analysis"
        Read["Read full subtitle text"]
        Understand["Understand semantics:<br/>- Topic identification<br/>- Theme transitions<br/>- Natural breakpoints"]
        Generate["Generate chapters:<br/>2-5 minutes each"]
    end
    
    subgraph "Chapter Metadata"
        Title["Title (10-20 chars)"]
        Time["Time range (MM:SS)"]
        Summary["Summary (50-100 chars)"]
        Keywords["Keywords (3-5 terms)"]
    end
    
    VTT --> Parser
    Parser --> Parse
    Parse --> Extract
    Extract --> Format
    
    Format --> Read
    Read --> Understand
    Understand --> Generate
    
    Generate --> Title
    Generate --> Time
    Generate --> Summary
    Generate --> Keywords
```

### Chapter Generation Principles

The AI analysis follows these guidelines defined in [SKILL.md:122-127]():

| Principle | Specification |
|-----------|---------------|
| **Granularity** | 2-5 minutes per chapter (target: 180-300 seconds) |
| **Completeness** | All video content covered, no gaps |
| **Meaningfulness** | Each chapter represents a coherent topic |
| **Natural boundaries** | Split at semantic transitions, not arbitrary timestamps |

### Chapter Structure

Each generated chapter contains:

```
Chapter N:
├── Title: "AGI as exponential curve"
├── Time Range: "00:00 - 03:15"
├── Core Summary: "AI models double in capability every 4-12 months..."
└── Keywords: ["AGI", "exponential growth", "Claude Code"]
```

### Example Output

From [README.md:167-172]():

```
1. [00:00 - 03:15] AGI as an exponential curve, not a point in time
2. [03:15 - 06:30] China's gap in AI development
3. [06:30 - 09:45] The impact of chip bans
```

**Sources:** [SKILL.md:96-144](), [README.md:16](), [README.md:193-209]()

---

## Stage 4: User Selection

**Purpose:** Allow user to choose which chapters to process and what processing options to apply.

This stage uses Claude Code's `AskUserQuestion` tool to interact with the user. No Python scripts are directly involved; this is pure orchestration by Claude Code.

```mermaid
graph TD
    Chapters["Generated Chapters<br/>(from Stage 3)"]
    
    subgraph "User Interaction"
        Display["Display chapter list<br/>with metadata"]
        Select["User selects chapters<br/>(multi-select supported)"]
        Options["Processing options"]
    end
    
    subgraph "Option Choices"
        Opt1["Generate bilingual subtitles?<br/>(English + TARGET_LANGUAGE)"]
        Opt2["Burn subtitles into video?<br/>(requires ffmpeg-full + libass)"]
        Opt3["Generate summary for social media?<br/>(Xiaohongshu, Douyin, WeChat)"]
    end
    
    Plan["Processing Plan:<br/>- Selected chapters<br/>- Enabled options<br/>- Estimated time"]
    
    Chapters --> Display
    Display --> Select
    Select --> Options
    
    Options --> Opt1
    Options --> Opt2
    Options --> Opt3
    
    Opt1 --> Plan
    Opt2 --> Plan
    Opt3 --> Plan
```

### Selection Format

Users can select chapters by:
- Single number: `1`
- Multiple numbers: `1,3,5`
- Range: `1-3`
- Combination: `1,3-5,7`

### Processing Options

| Option | Script Involved | Dependencies |
|--------|----------------|--------------|
| Bilingual subtitles | [extract_subtitle_clip.py]() + translation | Claude AI API |
| Burn subtitles | [burn_subtitles.py]() | FFmpeg with libass |
| Generate summary | Claude AI | None (built-in) |

**Sources:** [SKILL.md:146-161](), [README.md:109]()

---

## Stage 5: Processing Execution

**Purpose:** Execute selected processing tasks for each chosen chapter.

This stage orchestrates multiple Python scripts in a coordinated sequence. Each chapter undergoes up to six sub-stages depending on user-selected options.

```mermaid
flowchart TB
    Start["For each selected chapter"]
    
    Sub1["5.1: clip_video.py<br/>Extract video segment"]
    Sub2["5.2: extract_subtitle_clip.py<br/>Extract subtitle segment"]
    Sub3["5.3: Batch translation<br/>20-25 lines per API call"]
    Sub4["5.4: Generate bilingual SRT<br/>Merge EN + translated text"]
    Sub5["5.5: burn_subtitles.py<br/>Embed subtitles in video"]
    Sub6["5.6: Generate summary<br/>Social media content"]
    
    Decision1{Bilingual<br/>subtitles?}
    Decision2{Burn<br/>subtitles?}
    Decision3{Generate<br/>summary?}
    
    Output["Chapter output files"]
    
    Start --> Sub1
    Sub1 --> Sub2
    Sub2 --> Decision1
    
    Decision1 -->|Yes| Sub3
    Decision1 -->|No| Decision2
    Sub3 --> Sub4
    Sub4 --> Decision2
    
    Decision2 -->|Yes| Sub5
    Decision2 -->|No| Decision3
    Sub5 --> Decision3
    
    Decision3 -->|Yes| Sub6
    Decision3 -->|No| Output
    Sub6 --> Output
```

### Sub-Stage 5.1: Video Clipping

**Script:** [scripts/clip_video.py]()

Extracts precise video segment using FFmpeg stream copying:

```bash
python3 scripts/clip_video.py <video_path> <start_time> <end_time> <output_path>
```

- **Method:** FFmpeg `-ss` (seek start) and `-to` (seek end) with `-c copy`
- **Quality:** Lossless (no re-encoding)
- **Precision:** Frame-accurate timing
- **Output:** `{chapter_title}_clip.mp4`

### Sub-Stage 5.2: Subtitle Extraction

**Script:** [scripts/extract_subtitle_clip.py]()

Filters subtitles by time range and adjusts timestamps:

- Extract entries within `[start_time, end_time]`
- Adjust timestamps: `new_timestamp = original_timestamp - start_time`
- Convert VTT to SRT format
- Output: `{chapter_title}_original.srt`

### Sub-Stage 5.3: Batch Translation

**Optimization:** Translates 20-25 subtitle lines per API call instead of one-by-one.

Translation strategy from [SKILL.md:188-193]():
- Maintain technical term accuracy
- Use conversational language for short-form video
- Keep translations concise and fluid
- Batch size configurable via `TRANSLATION_BATCH_SIZE` in [.env.example:37]()

**API Call Reduction:** 95% fewer calls compared to line-by-line translation

### Sub-Stage 5.4: Bilingual Subtitle Generation

Merges original and translated subtitles into dual-language SRT format:

```srt
1
00:00:00,000 --> 00:00:03,500
This is the English subtitle
这是中文字幕

2
00:00:03,500 --> 00:00:07,000
Another English line
另一行中文
```

Output: `{chapter_title}_bilingual.srt`

### Sub-Stage 5.5: Subtitle Burning

**Script:** [scripts/burn_subtitles.py]()

Hardcodes subtitles into video using FFmpeg's `subtitles` filter:

```bash
python3 scripts/burn_subtitles.py <video_path> <subtitle_path> <output_path>
```

**Critical Implementation Detail:** The script uses a temporary directory workaround to handle paths with spaces, as FFmpeg's subtitles filter cannot properly parse escaped spaces. See [SKILL.md:287-291]() for details.

Subtitle styling from [.env.example:24-32]():
- Font size: 24
- Bottom margin: 30
- Color: White text with black outline

Output: `{chapter_title}_with_subtitles.mp4`

### Sub-Stage 5.6: Summary Generation

Uses Claude AI to generate social media content:
- Platform-specific formatting (Xiaohongshu, Douyin, WeChat)
- Based on chapter title, summary, and keywords
- Includes: headline, key points, hashtags

Output: `{chapter_title}_summary.md`

**Sources:** [SKILL.md:164-235](), [README.md:16-20](), [README.md:212-217]()

---

## Stage 6: Output Organization

**Purpose:** Create organized directory structure and present results to user.

```mermaid
graph TB
    Base["./youtube-clips/"]
    Session["YYYYMMDD_HHMMSS/<br/>(Timestamped session)"]
    
    subgraph "Per Chapter Directory"
        ChapterDir["Chapter_Title/<br/>(Sanitized filename)"]
        
        File1["chapter_clip.mp4<br/>(Always created)"]
        File2["chapter_bilingual.srt<br/>(If translation enabled)"]
        File3["chapter_with_subtitles.mp4<br/>(If burning enabled)"]
        File4["chapter_summary.md<br/>(If summary enabled)"]
    end
    
    Base --> Session
    Session --> ChapterDir
    
    ChapterDir --> File1
    ChapterDir --> File2
    ChapterDir --> File3
    ChapterDir --> File4
```

### Directory Structure

The output follows a three-level hierarchy:

```
./youtube-clips/                          # Base output directory
└── 20260122_143022/                      # Session timestamp
    ├── AGI_as_exponential_curve/         # Chapter 1
    │   ├── AGI_as_exponential_curve_clip.mp4
    │   ├── AGI_as_exponential_curve_bilingual.srt
    │   ├── AGI_as_exponential_curve_with_subtitles.mp4
    │   └── AGI_as_exponential_curve_summary.md
    └── China_gap_in_AI/                  # Chapter 2
        ├── China_gap_in_AI_clip.mp4
        └── ...
```

### Filename Sanitization

Chapter titles are sanitized to create valid filenames (from [SKILL.md:347-350]()):

- Remove special characters: `/ \ : * ? " < > |`
- Replace spaces with underscores
- Limit length to 100 characters

### Output Presentation

The skill displays to the user:

1. **Output directory path** - Full path to session directory
2. **File listing** - All generated files with sizes
3. **Quick preview command** - OS-specific command to open files
4. **Continuation prompt** - Option to process more chapters

Example output from [SKILL.md:262-274]():

```
✨ Processing complete!

📁 Output directory: ./youtube-clips/20260121_143022/

Files:
  🎬 AGI_exponential_curve_with_subtitles.mp4 (14 MB)
  📄 AGI_exponential_curve_bilingual.srt (2.3 KB)
  📝 AGI_exponential_curve_summary.md (3.2 KB)

Quick preview:
open ./youtube-clips/20260121_143022/AGI_exponential_curve_with_subtitles.mp4
```

**Sources:** [SKILL.md:238-278](), [README.md:112-123]()

---

## Error Handling Flow

Each stage has specific error handling and recovery mechanisms:

```mermaid
flowchart LR
    subgraph "Stage 1 Errors"
        E1["Missing yt-dlp"]
        E2["Missing FFmpeg"]
        E3["No libass support"]
        E4["Python deps missing"]
    end
    
    subgraph "Stage 2 Errors"
        E5["Invalid URL"]
        E6["Network timeout"]
        E7["No subtitles available"]
    end
    
    subgraph "Stage 5 Errors"
        E8["FFmpeg execution failed"]
        E9["Path with spaces issue"]
        E10["Translation API error"]
        E11["Disk space insufficient"]
    end
    
    subgraph "Resolution Actions"
        R1["Display install commands"]
        R2["Retry with auto-subs"]
        R3["Use temp directory workaround"]
        R4["Retry up to 3 times"]
        R5["Prompt user to free space"]
    end
    
    E1 --> R1
    E2 --> R1
    E3 --> R1
    E4 --> R1
    
    E5 --> R1
    E6 --> R4
    E7 --> R2
    
    E8 --> R1
    E9 --> R3
    E10 --> R4
    E11 --> R5
```

### Common Error Scenarios

| Error Type | Detection | Resolution |
|------------|-----------|------------|
| Missing dependencies | Command not found / Import error | Display platform-specific install commands |
| No libass support | grep returns empty | Guide to install ffmpeg-full |
| Network issues | yt-dlp timeout | Automatic retry, suggest proxy configuration |
| Translation failures | API error | Retry up to 3 times, reduce batch size |
| Path issues | FFmpeg subtitles filter error | Temporary directory workaround (automatic) |

**Sources:** [SKILL.md:322-337](), [README.md:236-278]()

---

## Workflow Execution Context

The entire workflow executes within the Claude Code environment with the skill installed at `~/.claude/skills/youtube-clipper/`. All scripts are invoked with:

```bash
cd ~/.claude/skills/youtube-clipper
python3 scripts/<script_name>.py <arguments>
```

### Key Environment Variables

These variables from [.env.example]() affect workflow behavior:

| Variable | Impact on Workflow | Default |
|----------|-------------------|---------|
| `FFMPEG_PATH` | FFmpeg binary location for stages 5.1, 5.5 | Auto-detected |
| `OUTPUT_DIR` | Base directory for stage 6 output | `./youtube-clips` |
| `MAX_VIDEO_HEIGHT` | Video quality in stage 2 | 1080 |
| `TARGET_CHAPTER_DURATION` | AI chapter target in stage 3 | 180 seconds |
| `TRANSLATION_BATCH_SIZE` | Batch size in stage 5.3 | 20-25 |
| `TARGET_LANGUAGE` | Translation language in stage 5.3 | 中文 |

**Sources:** [.env.example](), [README.md:129-152]()

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)

</details>



This document explains the internal architecture of the YouTube Clipper Skill, including its component relationships, layer model, and core design decisions. The architecture is designed around modularity, with each processing phase encapsulated in a dedicated Python script that can be invoked independently or as part of the complete workflow.

For specific implementation details of individual scripts, see [Core Scripts](#4). For configuration options that affect architectural behavior, see [Configuration](#6). For troubleshooting architectural issues like FFmpeg integration problems, see [Troubleshooting](#8).

---

## System Overview

The YouTube Clipper Skill operates as a Claude Code skill with a multi-layer architecture. The system is structured around five core Python scripts located in [`scripts/`](), each responsible for a distinct processing phase, coordinated through the skill entry point defined in [`SKILL.md`]().

```mermaid
graph TB
    subgraph ClaudeCode["Claude Code Environment"]
        SkillEntry["SKILL.md<br/>Workflow Orchestration"]
    end
    
    subgraph PythonLayer["Python Script Layer"]
        Download["download_video.py<br/>Video Acquisition"]
        Analyze["analyze_subtitles.py<br/>Subtitle Parsing"]
        Clip["clip_video.py<br/>Video Segmentation"]
        ExtractSub["extract_subtitle_clip.py<br/>Subtitle Extraction"]
        Burn["burn_subtitles.py<br/>Subtitle Embedding"]
        Utils["utils.py<br/>Shared Utilities"]
    end
    
    subgraph ExternalTools["External Tool Layer"]
        YtDlpBin["yt-dlp binary<br/>System PATH"]
        FFmpegBin["ffmpeg binary<br/>with libass support"]
    end
    
    subgraph Config["Configuration Layer"]
        EnvFile[".env<br/>Runtime Configuration"]
        EnvExample[".env.example<br/>Template"]
    end
    
    subgraph Storage["Storage Layer"]
        TempDir["tempfile.mkdtemp()<br/>Temporary Processing"]
        OutputDir["./youtube-clips/<br/>Final Output"]
    end
    
    SkillEntry --> Download
    SkillEntry --> Analyze
    SkillEntry --> Clip
    SkillEntry --> ExtractSub
    SkillEntry --> Burn
    
    Download --> Utils
    Analyze --> Utils
    Clip --> Utils
    ExtractSub --> Utils
    Burn --> Utils
    
    Download -.->|uses| YtDlpBin
    Clip -.->|subprocess.run| FFmpegBin
    Burn -.->|subprocess.run| FFmpegBin
    
    Download -->|reads| EnvFile
    Analyze -->|reads| EnvFile
    Burn -->|reads| EnvFile
    
    Burn -->|creates| TempDir
    Burn -->|writes to| OutputDir
    Clip -->|writes to| OutputDir
```

**Sources:** [README.md:1-319](), [SKILL.md:1-374](), [TECHNICAL_NOTES.md:1-490]()

---

## Component Layer Model

The system is organized into four distinct architectural layers, each with specific responsibilities and isolation boundaries:

| Layer | Components | Responsibility | Isolation Mechanism |
|-------|-----------|----------------|---------------------|
| **Orchestration** | `SKILL.md` | Workflow definition, phase sequencing, user interaction | Claude Code skill specification |
| **Processing** | `scripts/*.py` | Business logic, data transformation, external tool invocation | Independent Python modules |
| **Integration** | `yt-dlp`, `ffmpeg` | Platform-specific operations, format conversion | Subprocess execution with error capture |
| **Storage** | `.env`, `tempfile`, output directories | Configuration persistence, temporary data, final artifacts | File system isolation |

```mermaid
graph LR
    subgraph Layer1["Orchestration Layer"]
        A["SKILL.md<br/>Phase 1-6 Workflow"]
    end
    
    subgraph Layer2["Processing Layer"]
        B1["download_video.py"]
        B2["analyze_subtitles.py"]
        B3["clip_video.py"]
        B4["extract_subtitle_clip.py"]
        B5["burn_subtitles.py"]
        B6["utils.py"]
    end
    
    subgraph Layer3["Integration Layer"]
        C1["yt_dlp Python module"]
        C2["yt-dlp CLI"]
        C3["FFmpeg subprocess"]
    end
    
    subgraph Layer4["Storage Layer"]
        D1[".env configuration"]
        D2["tempfile.mkdtemp()"]
        D3["./youtube-clips/"]
    end
    
    A -->|"invokes via subprocess"| B1
    A -->|"invokes via subprocess"| B2
    A -->|"invokes via subprocess"| B3
    A -->|"invokes via subprocess"| B4
    A -->|"invokes via subprocess"| B5
    
    B1 -->|"imports"| C1
    B3 -->|"subprocess.run"| C3
    B5 -->|"subprocess.run"| C3
    
    B1 -->|"reads"| D1
    B5 -->|"creates"| D2
    B3 -->|"writes"| D3
```

**Sources:** [SKILL.md:20-281](), [README.md:104-110]()

---

## Core Design Decisions

### 1. Modular Script Architecture

Each processing phase is implemented as a standalone Python script that can be invoked independently via command-line arguments. This design enables:

- **Independent testing**: Each script can be tested in isolation
- **Debugging**: Failed phases can be re-run without repeating entire workflow
- **Reusability**: Scripts can be used outside the Claude Code environment

**Implementation Pattern:**
```python
# All scripts follow this pattern:
if __name__ == '__main__':
    if len(sys.argv) < required_args:
        print(f"Usage: {sys.argv[0]} <args>")
        sys.exit(1)
    
    # Parse arguments
    # Execute processing
    # Output results
```

Scripts communicate through:
- **Input**: Command-line arguments (file paths, parameters)
- **Output**: File system artifacts (processed files)
- **Status**: stdout/stderr messages, exit codes

**Sources:** [scripts/download_video.py](), [scripts/clip_video.py](), [scripts/burn_subtitles.py]()

---

### 2. Temporary Directory Pattern for Path Safety

FFmpeg's `subtitles` filter cannot correctly parse file paths containing spaces, even with proper escaping ([TECHNICAL_NOTES.md:82-162]()). The system solves this with a temporary directory pattern implemented in `burn_subtitles.py`:

```mermaid
graph LR
    A["Input Files<br/>/path/with spaces/video.mp4<br/>/path/with spaces/sub.srt"] --> B["tempfile.mkdtemp()"]
    B --> C["Temp Directory<br/>/tmp/youtube_clipper_xyz/"]
    C --> D["shutil.copy()<br/>video.mp4<br/>subtitle.srt"]
    D --> E["FFmpeg Processing<br/>No spaces in paths"]
    E --> F["shutil.move()"]
    F --> G["Output File<br/>/path/with spaces/output.mp4"]
    B -.->|"finally: cleanup"| H["shutil.rmtree()"]
```

**Key Implementation Details:**
- `tempfile.mkdtemp(prefix='youtube_clipper_')` ensures paths without spaces
- Files are copied into temp directory before processing
- Cleanup occurs in `finally` block to ensure removal even on errors
- This approach is transparent to users who can use arbitrary paths

**Sources:** [TECHNICAL_NOTES.md:82-162](), [scripts/burn_subtitles.py]()

---

### 3. Dual FFmpeg Detection Strategy

The system implements a two-tier detection strategy for FFmpeg to handle the common issue of missing `libass` support:

```mermaid
graph TD
    Start["detect_ffmpeg_variant()"] --> MacCheck{"platform.system()<br/>== 'Darwin'?"}
    
    MacCheck -->|Yes| FullPath["Check /opt/homebrew/opt/<br/>ffmpeg-full/bin/ffmpeg"]
    FullPath --> FullExists{"Path.exists()"}
    FullExists -->|Yes| ReturnFull["Return ffmpeg-full path"]
    FullExists -->|No| StdPath
    
    MacCheck -->|No| StdPath["shutil.which('ffmpeg')"]
    StdPath --> StdExists{"Found?"}
    StdExists -->|Yes| LibassCheck["Check libass support<br/>ffmpeg -filters"]
    LibassCheck --> HasLibass{"'subtitles' filter<br/>present?"}
    HasLibass -->|Yes| ReturnStd["Return standard ffmpeg"]
    HasLibass -->|No| Error["Raise error with<br/>installation guide"]
    StdExists -->|No| Error
```

This strategy handles three scenarios:
1. **macOS with ffmpeg-full**: Optimal, full subtitle support
2. **Standard ffmpeg with libass**: Works on most Linux systems
3. **No libass support**: Clear error with installation instructions

**Sources:** [TECHNICAL_NOTES.md:1-79](), [scripts/burn_subtitles.py]()

---

### 4. Batch Translation Optimization

Instead of making one API call per subtitle line, the system batches 20-25 lines per call, achieving 95% reduction in API calls. This is implemented through a grouping strategy:

| Approach | Subtitle Count | API Calls | Reduction |
|----------|---------------|-----------|-----------|
| Individual | 600 lines | 600 calls | Baseline |
| Batched (20/batch) | 600 lines | 30 calls | 95% |
| Batched (25/batch) | 600 lines | 24 calls | 96% |

**Batch Size Selection Rationale:**
- **< 20 lines**: Too many API calls, negates benefit
- **20-25 lines**: Optimal balance of efficiency and translation quality
- **> 30 lines**: Single request becomes too large, translation quality degrades

**Sources:** [TECHNICAL_NOTES.md:260-305](), [SKILL.md:185-193](), [README.md:211-216]()

---

## Module Dependency Graph

This diagram shows the concrete import relationships between Python modules using actual module and function names:

```mermaid
graph TD
    subgraph Scripts["scripts/"]
        DV["download_video.py<br/>main()<br/>download_with_ytdlp()"]
        AS["analyze_subtitles.py<br/>main()<br/>parse_vtt()"]
        CV["clip_video.py<br/>main()<br/>clip_with_ffmpeg()"]
        ESC["extract_subtitle_clip.py<br/>main()<br/>extract_and_adjust()"]
        BS["burn_subtitles.py<br/>main()<br/>detect_ffmpeg_variant()<br/>burn_with_temp_dir()"]
        U["utils.py<br/>time_to_seconds()<br/>seconds_to_time()<br/>sanitize_filename()<br/>ensure_directory()"]
    end
    
    subgraph External["External Libraries"]
        YtDlp["yt_dlp<br/>YoutubeDL class"]
        PySRT["pysrt<br/>SubRipFile<br/>SubRipItem"]
        DotEnv["dotenv<br/>load_dotenv()"]
        Subprocess["subprocess<br/>run()<br/>Popen()"]
        Tempfile["tempfile<br/>mkdtemp()"]
        Shutil["shutil<br/>which()<br/>copy()<br/>move()"]
    end
    
    DV -->|"import"| U
    DV -->|"import"| YtDlp
    DV -->|"import"| DotEnv
    
    AS -->|"import"| U
    AS -->|"import"| DotEnv
    
    CV -->|"import"| U
    CV -->|"import"| Subprocess
    
    ESC -->|"import"| U
    ESC -->|"import"| PySRT
    
    BS -->|"import"| U
    BS -->|"import"| Subprocess
    BS -->|"import"| Tempfile
    BS -->|"import"| Shutil
    BS -->|"import"| DotEnv
```

**Key Shared Utilities in `utils.py`:**

| Function | Purpose | Used By |
|----------|---------|---------|
| `time_to_seconds(time_str)` | Parse HH:MM:SS to seconds | `analyze_subtitles.py`, `extract_subtitle_clip.py` |
| `seconds_to_time(seconds)` | Format seconds to HH:MM:SS | `clip_video.py`, `extract_subtitle_clip.py` |
| `sanitize_filename(name)` | Remove invalid path characters | All output-generating scripts |
| `ensure_directory(path)` | Create directory if missing | `download_video.py`, `clip_video.py` |

**Sources:** [scripts/utils.py](), [scripts/download_video.py](), [scripts/burn_subtitles.py]()

---

## Data Flow Through System

This diagram traces actual data artifacts as they flow through the system, showing file formats and transformation points:

```mermaid
graph TB
    Input["YouTube URL<br/>User Input"] --> DL["download_video.py<br/>yt_dlp.YoutubeDL"]
    
    DL --> VidFile["video_id.mp4<br/>H.264, up to 1080p"]
    DL --> SubFile["video_id.en.vtt<br/>WebVTT format"]
    
    SubFile --> Parse["analyze_subtitles.py<br/>parse_vtt()"]
    Parse --> SubData["Structured subtitle data<br/>List of time/text pairs"]
    
    SubData -.->|"AI Analysis"| Chapters["Chapter definitions<br/>JSON structure:<br/>{title, start, end, summary}"]
    
    Chapters -->|"User selects"| Process["Processing Phase"]
    
    VidFile --> ClipScript["clip_video.py<br/>subprocess.run(['ffmpeg'])"]
    Chapters --> ClipScript
    ClipScript --> ClipOut["chapter_clip.mp4<br/>-c copy stream copy"]
    
    SubFile --> ExtractScript["extract_subtitle_clip.py<br/>pysrt.SubRipFile"]
    Chapters --> ExtractScript
    ExtractScript --> SrtSeg["chapter_segment.srt<br/>Time-adjusted SRT"]
    
    SrtSeg -.->|"AI Translation"| TransSrt["chapter_bilingual.srt<br/>English + Chinese"]
    
    ClipOut --> BurnScript["burn_subtitles.py<br/>tempfile + ffmpeg -vf subtitles"]
    TransSrt --> BurnScript
    BurnScript --> FinalVid["chapter_with_subtitles.mp4<br/>Hardcoded subtitles"]
    
    FinalVid --> Output["./youtube-clips/<br/>TIMESTAMP/Chapter_Title/"]
    TransSrt --> Output
```

**File Format Transformations:**

| Stage | Input Format | Output Format | Tool |
|-------|-------------|---------------|------|
| Download | YouTube URL | MP4 + VTT | `yt_dlp.YoutubeDL` |
| Analysis | VTT | Parsed data structure | Custom `parse_vtt()` |
| Clipping | MP4 | MP4 segment | `ffmpeg -ss -to -c copy` |
| Extraction | VTT | SRT (time-adjusted) | `pysrt` library |
| Burning | MP4 + SRT | MP4 (subtitles embedded) | `ffmpeg -vf subtitles` |

**Critical Format Requirements:**
- **VTT to SRT conversion**: Time separator must change from `.` to `,` ([TECHNICAL_NOTES.md:166-213]())
- **Time adjustment**: Subtitle timestamps must be offset by chapter start time
- **Path safety**: All paths used with FFmpeg `subtitles` filter must not contain spaces

**Sources:** [SKILL.md:66-93](), [SKILL.md:164-235](), [TECHNICAL_NOTES.md:166-258]()

---

## Configuration System Architecture

The configuration system uses a three-tier fallback mechanism to ensure the system operates with sensible defaults while allowing customization:

```mermaid
graph LR
    EnvExample[".env.example<br/>Template values<br/>Documentation"] -.->|"User copies"| EnvFile[".env<br/>User configuration"]
    
    EnvFile -->|"python-dotenv<br/>load_dotenv()"| Runtime["Runtime Configuration"]
    
    HardCoded["Hard-coded defaults<br/>in Python scripts<br/>MAX_VIDEO_HEIGHT=1080<br/>BATCH_SIZE=20"] -.->|"Fallback"| Runtime
    
    Runtime --> DV["download_video.py<br/>Uses MAX_VIDEO_HEIGHT"]
    Runtime --> BS["burn_subtitles.py<br/>Uses SUBTITLE_FONT_SIZE"]
    Runtime --> Trans["Translation logic<br/>Uses TRANSLATION_BATCH_SIZE"]
```

**Configuration Categories and Their Impact:**

| Category | Variables | Affects Scripts | Default Fallback |
|----------|-----------|-----------------|------------------|
| **Paths** | `FFMPEG_PATH`, `OUTPUT_DIR` | `clip_video.py`, `burn_subtitles.py` | Auto-detection, `./youtube-clips` |
| **Video Quality** | `MAX_VIDEO_HEIGHT` | `download_video.py` | `1080` |
| **Subtitle Style** | `SUBTITLE_FONT_SIZE`, `SUBTITLE_MARGIN_V` | `burn_subtitles.py` | `24`, `30` |
| **Processing** | `TRANSLATION_BATCH_SIZE`, `TARGET_CHAPTER_DURATION` | Translation logic, Analysis | `20`, `180` |

**Sources:** [.env.example](), [README.md:127-153](), [scripts/download_video.py](), [scripts/burn_subtitles.py]()

---

## Error Handling Architecture

The system implements layered error handling with user-friendly messages at each level:

```mermaid
graph TD
    UserAction["User Invokes Skill"] --> EnvCheck["Phase 1: Environment Check<br/>SKILL.md lines 25-63"]
    
    EnvCheck -->|"Fail"| EnvError["Missing Dependencies Error<br/>Installation instructions<br/>Specific to missing tool"]
    EnvCheck -->|"Pass"| Download["Phase 2: Download<br/>download_video.py"]
    
    Download -->|"Network error"| DownloadError["Retry logic<br/>Proxy suggestion<br/>URL validation"]
    Download -->|"Success"| Process["Phase 3-5: Processing"]
    
    Process --> FFmpegCall["FFmpeg subprocess.run()"]
    FFmpegCall -->|"returncode != 0"| FFmpegError["Capture stderr<br/>Display command<br/>Suggest fixes"]
    FFmpegCall -->|"Success"| Output["Phase 6: Output"]
    
    Process --> LibassCheck["burn_subtitles.py<br/>detect_ffmpeg_variant()"]
    LibassCheck -->|"No libass"| LibassError["Clear error message<br/>brew install ffmpeg-full<br/>Or sudo apt install libass-dev"]
```

**Error Handling Patterns:**

1. **Environment Detection**: Fail fast with installation instructions before processing begins
2. **Subprocess Execution**: Capture both stdout and stderr, display full command for debugging
3. **File Operations**: Use `try/finally` blocks to ensure cleanup (especially for temp directories)
4. **External API**: Implement retry logic with exponential backoff

**Sources:** [SKILL.md:321-336](), [TECHNICAL_NOTES.md:444-474](), [README.md:236-278]()

---

## Summary

The YouTube Clipper Skill architecture achieves several key design goals:

1. **Modularity**: Each processing phase is isolated in a dedicated script with clear interfaces
2. **Robustness**: Multiple layers of error detection and workarounds for common issues (path spaces, missing libass)
3. **Efficiency**: Batch processing optimizations reduce API calls by 95%
4. **Flexibility**: Configuration system allows customization without code changes
5. **Maintainability**: Clear separation of concerns makes testing and debugging straightforward

The architecture's key innovation is its transparent handling of common system integration issues (FFmpeg path problems, missing dependencies) while maintaining a simple user-facing interface through Claude Code's natural language interaction.

**Sources:** [README.md:1-319](), [SKILL.md:1-374](), [TECHNICAL_NOTES.md:1-490]()

---

# Page: System Components

# System Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [scripts/__init__.py](scripts/__init__.py)

</details>



This document provides a comprehensive reference for all major components in the YouTube Clipper Skill codebase. It describes the purpose, location, and interactions of Python scripts, external tools, utilities, and configuration systems.

For information about how these components work together in the processing pipeline, see [Processing Pipeline](#3.2). For details on Claude AI integration specifically, see [AI Integration](#3.3).

## Component Categories

The YouTube Clipper Skill is organized into five primary component categories:

| Category | Purpose | Location |
|----------|---------|----------|
| **Core Scripts** | Python modules that execute specific processing stages | `scripts/*.py` |
| **External Tools** | Command-line utilities for video/subtitle processing | System PATH (yt-dlp, FFmpeg) |
| **Shared Utilities** | Common functions used across all scripts | `scripts/utils.py` |
| **Configuration** | Environment variables and settings | `.env`, `.env.example` |
| **Installation** | Setup automation and dependency verification | `install_as_skill.sh` |

Sources: [README.md:1-320](), Diagram 1 and Diagram 3 from high-level architecture

---

## Component Hierarchy

```mermaid
graph TB
    subgraph "Entry Point"
        Skill["Skill Entry<br/>~/.claude/skills/youtube-clipper/"]
    end
    
    subgraph "Core Processing Scripts"
        DV["download_video.py<br/>Video Acquisition"]
        AS["analyze_subtitles.py<br/>Semantic Analysis"]
        CV["clip_video.py<br/>Video Segmentation"]
        ESC["extract_subtitle_clip.py<br/>Subtitle Extraction"]
        BS["burn_subtitles.py<br/>Subtitle Embedding"]
    end
    
    subgraph "Shared Components"
        Utils["utils.py<br/>Time/File/Format Utilities"]
        Config[".env<br/>Configuration Variables"]
    end
    
    subgraph "External Dependencies"
        YtDlpBin["yt-dlp CLI<br/>System Binary"]
        YtDlpLib["yt_dlp<br/>Python Library"]
        FFmpegBin["ffmpeg + libass<br/>System Binary"]
        PySRT["pysrt<br/>SRT Parser"]
        DotEnv["python-dotenv<br/>Config Loader"]
    end
    
    subgraph "Installation"
        Install["install_as_skill.sh<br/>Setup Automation"]
    end
    
    Skill --> DV
    Skill --> AS
    Skill --> CV
    Skill --> ESC
    Skill --> BS
    
    DV --> Utils
    DV --> Config
    DV --> YtDlpLib
    
    AS --> Utils
    AS --> Config
    
    CV --> Utils
    CV --> FFmpegBin
    
    ESC --> Utils
    ESC --> PySRT
    
    BS --> Utils
    BS --> FFmpegBin
    
    Install -.->|"Verifies"| YtDlpBin
    Install -.->|"Verifies"| FFmpegBin
    Install -.->|"Installs"| YtDlpLib
    Install -.->|"Installs"| PySRT
    Install -.->|"Installs"| DotEnv
    Install -.->|"Creates"| Config
```

Sources: [README.md:42-66](), [TECHNICAL_NOTES.md:1-490](), Diagram 3 from high-level architecture

---

## Core Processing Scripts

The system implements five specialized Python scripts in the `scripts/` directory, each responsible for a discrete processing stage.

### download_video.py

**Purpose**: Downloads YouTube videos and subtitles using yt-dlp.

**Key Responsibilities**:
- Configures yt-dlp with quality limits (default 1080p max)
- Downloads video in mp4 format with best audio
- Extracts English subtitles (VTT format)
- Supports proxy configuration and rate limiting
- Provides download progress monitoring

**External Dependencies**:
- `yt_dlp` Python library
- `yt-dlp` CLI tool (fallback)

**Configuration Variables**:
- `MAX_VIDEO_HEIGHT` - Video quality limit (720/1080/1440/2160)
- `YT_DLP_PROXY` - Proxy server URL
- `YT_DLP_RATE_LIMIT` - Download speed limit

Sources: [README.md:54-66](), [TECHNICAL_NOTES.md:306-354]()

---

### analyze_subtitles.py

**Purpose**: Prepares subtitle data for AI semantic analysis.

**Key Responsibilities**:
- Parses VTT subtitle files
- Formats subtitle data for Claude AI analysis
- Provides chapter duration guidelines
- Structures data for semantic understanding

**Data Flow**:
1. Reads VTT file from download stage
2. Extracts text content and timestamps
3. Formats for AI consumption
4. Returns structured subtitle data

**Configuration Variables**:
- `TARGET_CHAPTER_DURATION` - Suggested chapter length (180-300 seconds)

Sources: [README.md:105-110](), Diagram 2 from high-level architecture

---

### clip_video.py

**Purpose**: Extracts precise video segments using FFmpeg.

**Key Responsibilities**:
- Performs frame-accurate video clipping
- Uses FFmpeg stream copying (no re-encoding)
- Supports multiple chapter extraction
- Preserves original video quality

**FFmpeg Strategy**:
```bash
ffmpeg -ss START_TIME -i INPUT -t DURATION -c copy OUTPUT
```

The `-c copy` flag ensures stream copying without quality loss.

**Input Parameters**:
- Video file path
- Start timestamp (seconds)
- End timestamp (seconds)
- Output file path

Sources: [README.md:109](), [TECHNICAL_NOTES.md:83-163]()

---

### extract_subtitle_clip.py

**Purpose**: Extracts and time-adjusts subtitle segments for clipped videos.

**Key Responsibilities**:
- Filters subtitles within time range
- Adjusts timestamps relative to clip start (offset = 0)
- Converts VTT to SRT format
- Handles boundary cases (partial overlaps)

**Time Adjustment Logic**:
```python
adjusted_time = original_time - clip_start_time
adjusted_time = max(0.0, adjusted_time)  # Ensure non-negative
```

**Dependencies**:
- `pysrt` library for SRT parsing and manipulation

Sources: [TECHNICAL_NOTES.md:215-258](), [TECHNICAL_NOTES.md:166-213]()

---

### burn_subtitles.py

**Purpose**: Embeds subtitles directly into video files using FFmpeg with libass.

**Key Responsibilities**:
- Detects FFmpeg variant (standard vs ffmpeg-full)
- Verifies libass support for `subtitles` filter
- Applies subtitle styling (font size, margins)
- Handles file paths with spaces using temporary directories

**Critical Implementation Details**:

The script uses a temporary directory workaround to handle paths with spaces, as FFmpeg's `subtitles` filter cannot parse them correctly:

```python
# Creates temp directory without spaces
temp_dir = tempfile.mkdtemp(prefix='youtube_clipper_')
# Copies files to temp location
# Processes with FFmpeg
# Moves output back to target location
```

**FFmpeg Detection Logic**:
1. Checks for `ffmpeg-full` on macOS (`/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`)
2. Falls back to standard `ffmpeg` if libass supported
3. Provides installation guidance if libass missing

**Configuration Variables**:
- `FFMPEG_PATH` - Override FFmpeg binary path
- `SUBTITLE_FONT_SIZE` - Font size (default: 24 for 1080p)
- `SUBTITLE_MARGIN_V` - Bottom margin in pixels (default: 30)

Sources: [README.md:67-84](), [TECHNICAL_NOTES.md:1-82](), [TECHNICAL_NOTES.md:83-163]()

---

## Component Dependency Matrix

```mermaid
graph LR
    subgraph "scripts/"
        DV["download_video.py"]
        AS["analyze_subtitles.py"]
        CV["clip_video.py"]
        ESC["extract_subtitle_clip.py"]
        BS["burn_subtitles.py"]
        U["utils.py"]
    end
    
    subgraph "Python Packages"
        YL["yt_dlp"]
        SR["pysrt"]
        DE["python-dotenv"]
    end
    
    subgraph "System Binaries"
        YB["yt-dlp"]
        FF["ffmpeg"]
    end
    
    subgraph "Config"
        ENV[".env"]
    end
    
    DV -->|"imports"| U
    DV -->|"imports"| YL
    DV -->|"calls"| YB
    DV -->|"reads"| ENV
    
    AS -->|"imports"| U
    AS -->|"reads"| ENV
    
    CV -->|"imports"| U
    CV -->|"subprocess"| FF
    
    ESC -->|"imports"| U
    ESC -->|"imports"| SR
    
    BS -->|"imports"| U
    BS -->|"subprocess"| FF
    
    U -->|"imports"| DE
```

Sources: [scripts/__init__.py:1-8](), Diagram 3 from high-level architecture

---

## Shared Utilities Module

### utils.py

**Purpose**: Provides common functions used across all processing scripts.

**Function Categories**:

| Category | Functions | Purpose |
|----------|-----------|---------|
| **Time Conversion** | Time string parsing/formatting | Convert between HH:MM:SS and seconds |
| **File Management** | Path validation, sanitization | Handle filenames with special characters |
| **Format Utilities** | VTT/SRT conversions | Subtitle format transformations |
| **Validation** | Existence checks, format verification | Ensure inputs are valid |

**Common Operations**:
- Sanitizing filenames by removing special characters `/ \ : * ? " < > |`
- Converting timestamp strings to float seconds
- Creating output directory structures
- Validating video/subtitle file formats

**Design Pattern**: All scripts import utilities to avoid code duplication and ensure consistent behavior across the system.

Sources: Diagram 1 and Diagram 3 from high-level architecture, [README.md:274-277]()

---

## External Tools Integration

### yt-dlp

**Type**: External command-line tool + Python library

**Integration Points**:
1. **CLI Tool** - System binary for direct video downloads
2. **Python Library** (`yt_dlp`) - Programmatic control with custom options

**Usage in download_video.py**:
```python
ydl_opts = {
    'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best',
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['en'],
    'subtitlesformat': 'vtt',
    'outtmpl': '%(title)s [%(id)s].%(ext)s'
}
```

**Format Selection Logic**:
- Prioritizes mp4 video up to 1080p
- Merges with best m4a audio
- Falls back to best available format
- Downloads English subtitles (manual or automatic)

Sources: [README.md:54-58](), [TECHNICAL_NOTES.md:306-354]()

---

### FFmpeg with libass

**Type**: External command-line tool

**Critical Requirements**:
- FFmpeg must be compiled with `libass` support
- libass enables the `subtitles` filter for burning subtitles
- Standard Homebrew FFmpeg on macOS lacks libass

**Integration Points**:

| Script | FFmpeg Operation | Required Features |
|--------|------------------|-------------------|
| `clip_video.py` | Stream copy extraction | Basic FFmpeg |
| `burn_subtitles.py` | Subtitle rendering | libass support |

**Detection Strategy** (in burn_subtitles.py):
1. Check for macOS-specific `ffmpeg-full` at `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
2. Verify libass support by checking available filters
3. Exit with installation instructions if unsupported

**Filter Syntax**:
```bash
ffmpeg -i video.mp4 -vf "subtitles=subtitle.srt:force_style='FontSize=24,MarginV=30'" output.mp4
```

Sources: [README.md:67-84](), [TECHNICAL_NOTES.md:1-82]()

---

## Configuration System

### .env File Structure

The configuration system uses environment variables loaded from `.env` at the skill root directory.

**Configuration Categories**:

```mermaid
graph TB
    ENV[".env file"]
    
    subgraph "Path Configuration"
        P1["FFMPEG_PATH"]
        P2["OUTPUT_DIR"]
        P3["TEMP_DIR"]
    end
    
    subgraph "Video Settings"
        V1["MAX_VIDEO_HEIGHT"]
        V2["YT_DLP_PROXY"]
        V3["YT_DLP_RATE_LIMIT"]
    end
    
    subgraph "Subtitle Settings"
        S1["SUBTITLE_FONT_SIZE"]
        S2["SUBTITLE_MARGIN_V"]
        S3["TARGET_LANGUAGE"]
    end
    
    subgraph "Processing Settings"
        PR1["TRANSLATION_BATCH_SIZE"]
        PR2["TARGET_CHAPTER_DURATION"]
        PR3["KEEP_TEMP_FILES"]
    end
    
    ENV --> P1
    ENV --> P2
    ENV --> P3
    ENV --> V1
    ENV --> V2
    ENV --> V3
    ENV --> S1
    ENV --> S2
    ENV --> S3
    ENV --> PR1
    ENV --> PR2
    ENV --> PR3
    
    P1 -.-> BS["burn_subtitles.py<br/>clip_video.py"]
    P2 -.-> All["All scripts"]
    V1 -.-> DV["download_video.py"]
    V2 -.-> DV
    S1 -.-> BS
    S2 -.-> BS
    S3 -.-> Trans["Translation Pipeline"]
    PR1 -.-> Trans
    PR2 -.-> AS["analyze_subtitles.py"]
```

Sources: [README.md:128-154](), Diagram 5 from high-level architecture

---

### .env.example Template

**Purpose**: Provides template and default values for user configuration.

**Creation**: Generated by `install_as_skill.sh` during installation.

**Key Variables**:

| Variable | Default | Used By |
|----------|---------|---------|
| `FFMPEG_PATH` | (auto-detect) | `burn_subtitles.py`, `clip_video.py` |
| `OUTPUT_DIR` | `./youtube-clips` | All scripts |
| `MAX_VIDEO_HEIGHT` | `1080` | `download_video.py` |
| `TRANSLATION_BATCH_SIZE` | `20` | Translation pipeline |
| `TARGET_CHAPTER_DURATION` | `180` | `analyze_subtitles.py` |
| `SUBTITLE_FONT_SIZE` | `24` | `burn_subtitles.py` |
| `SUBTITLE_MARGIN_V` | `30` | `burn_subtitles.py` |
| `TARGET_LANGUAGE` | `中文` | Translation pipeline |

**Loading Mechanism**: Scripts use `python-dotenv` to load variables at runtime.

Sources: [README.md:128-154]()

---

## Installation and Setup

### install_as_skill.sh

**Purpose**: Automates installation and dependency verification.

**Installation Steps**:
1. Creates target directory: `~/.claude/skills/youtube-clipper/`
2. Copies all source files
3. Installs Python dependencies via pip
4. Verifies system dependencies (Python, yt-dlp, FFmpeg)
5. Creates `.env` from `.env.example`
6. Provides status report and troubleshooting guidance

**Dependency Checks**:
- **Python 3.8+**: Verifies version compatibility
- **yt-dlp**: Checks PATH for binary
- **FFmpeg**: Checks PATH and optionally verifies libass support
- **Python Packages**: Installs `yt-dlp`, `pysrt`, `python-dotenv`

**Installation Methods**:
1. **npx skills** (recommended): `npx skills add https://github.com/op7418/Youtube-clipper-skill`
2. **Manual**: Clone repository and run `bash install_as_skill.sh`

Sources: [README.md:24-47](), [README.md:42-46]()

---

## Component Interaction Summary

The following table summarizes how components interact during typical operations:

| Operation | Components Involved | Data Flow |
|-----------|---------------------|-----------|
| **Video Download** | `download_video.py` → `yt-dlp` → `utils.py` | URL → Video file + VTT subtitles |
| **Chapter Analysis** | `analyze_subtitles.py` → Claude AI → `utils.py` | VTT → Semantic chapters JSON |
| **Video Clipping** | `clip_video.py` → FFmpeg → `utils.py` | Video + timestamps → Clipped video |
| **Subtitle Extraction** | `extract_subtitle_clip.py` → `pysrt` → `utils.py` | VTT + timestamps → Time-adjusted SRT |
| **Subtitle Burning** | `burn_subtitles.py` → FFmpeg + libass → `utils.py` | Video + SRT → Video with burned subs |
| **Configuration** | All scripts → `.env` → `python-dotenv` | Environment variables → Runtime settings |

Sources: Diagram 1 and Diagram 2 from high-level architecture

---

## File Structure Overview

```
~/.claude/skills/youtube-clipper/
├── scripts/
│   ├── __init__.py                  # Package initialization
│   ├── download_video.py            # yt-dlp integration
│   ├── analyze_subtitles.py         # Subtitle preparation
│   ├── clip_video.py                # FFmpeg video clipping
│   ├── extract_subtitle_clip.py     # Subtitle time adjustment
│   ├── burn_subtitles.py            # FFmpeg subtitle burning
│   └── utils.py                     # Shared utilities
├── .env                              # User configuration (created by install)
├── .env.example                      # Configuration template
├── install_as_skill.sh               # Installation script
├── README.md                         # User documentation
├── TECHNICAL_NOTES.md                # Implementation details
└── references/                       # Technical guides
```

Sources: [README.md:1-320](), Diagram 6 from high-level architecture

---

# Page: Processing Pipeline

# Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [SKILL.md](SKILL.md)

</details>



This page documents the end-to-end data processing pipeline of the YouTube Clipper Skill, detailing how data flows from a YouTube URL input through multiple processing stages to produce clipped videos with bilingual subtitles. The pipeline consists of six sequential stages with conditional processing paths based on user selections.

For information about individual script implementations, see [Core Scripts](#4). For details on AI semantic analysis mechanisms, see [AI Integration](#3.3). For output file organization, see [File Organization](#3.4).

## Pipeline Overview

The YouTube Clipper Skill implements a linear six-stage pipeline with optional processing branches. Each stage transforms data from one format to another, with validation and error handling at stage boundaries.

```mermaid
flowchart TB
    Input["YouTube URL<br/>(user input)"]
    
    Stage1["Stage 1: Environment Detection<br/>Validate: yt-dlp, ffmpeg, Python deps"]
    Stage2["Stage 2: Video Download<br/>download_video.py"]
    Stage3["Stage 3: Semantic Analysis<br/>analyze_subtitles.py + AI"]
    Stage4["Stage 4: User Selection<br/>AskUserQuestion tool"]
    Stage5["Stage 5: Parallel Processing<br/>clip_video.py, translate, burn"]
    Stage6["Stage 6: Output Organization<br/>File structure creation"]
    
    Output["Organized Output Files<br/>./youtube-clips/TIMESTAMP/"]
    
    Input --> Stage1
    Stage1 -->|"✅ All deps available"| Stage2
    Stage1 -->|"❌ Missing deps"| Error1["Installation guidance"]
    
    Stage2 -->|"video.mp4 + subtitles.vtt"| Stage3
    Stage2 -->|"❌ Download failed"| Error2["Network/URL error"]
    
    Stage3 -->|"Structured chapters list"| Stage4
    Stage3 -->|"❌ No subtitles"| Error3["Manual subtitle upload"]
    
    Stage4 -->|"Selected chapters + options"| Stage5
    
    Stage5 -->|"Per-chapter files"| Stage6
    Stage5 -->|"❌ Processing error"| Error5["Retry/skip chapter"]
    
    Stage6 --> Output
    
    Error1 -.->|"User fixes"| Stage1
    Error2 -.->|"Retry"| Stage2
    Error3 -.->|"Alternative source"| Stage3
    Error5 -.->|"Continue"| Stage6
```

**Sources:** [SKILL.md:22-52](), [README.md:103-110]()

## Stage 1: Environment Detection

The first stage validates all required system dependencies before proceeding. This is a gating stage that prevents execution with incomplete environments.

### Validation Checklist

| Dependency | Validation Command | Expected Output | Fallback Action |
|------------|-------------------|-----------------|-----------------|
| `yt-dlp` CLI | `yt-dlp --version` | Version string | Install via pip/brew |
| `ffmpeg` binary | `ffmpeg -version` | Version with configuration | Install via package manager |
| `libass` support | `ffmpeg -filters 2>&1 \| grep subtitles` | Filter list containing "subtitles" | Install ffmpeg-full (macOS) |
| Python `yt_dlp` | `python3 -c "import yt_dlp"` | No error | `pip install yt-dlp` |
| Python `pysrt` | `python3 -c "import pysrt"` | No error | `pip install pysrt` |

### FFmpeg Path Resolution Strategy

```mermaid
flowchart LR
    Start["Environment Check"]
    
    CheckFull["Check /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
    CheckStd["Check system ffmpeg"]
    CheckEnv["Check FFMPEG_PATH env var"]
    ValidateLibass["Validate libass support<br/>ffmpeg -filters | grep subtitles"]
    
    UseFull["Use ffmpeg-full path"]
    UseStd["Use system ffmpeg"]
    UseEnv["Use configured path"]
    Fail["Error: libass not available"]
    
    Success["✅ FFmpeg validated"]
    
    Start --> CheckEnv
    CheckEnv -->|"Set"| UseEnv
    CheckEnv -->|"Not set"| CheckFull
    
    CheckFull -->|"Exists"| UseFull
    CheckFull -->|"Not found"| CheckStd
    
    CheckStd -->|"Exists"| UseStd
    CheckStd -->|"Not found"| Fail
    
    UseFull --> ValidateLibass
    UseStd --> ValidateLibass
    UseEnv --> ValidateLibass
    
    ValidateLibass -->|"Has subtitles filter"| Success
    ValidateLibass -->|"Missing filter"| Fail
```

**Sources:** [SKILL.md:25-63](), [README.md:67-83]()

## Stage 2: Video Download

This stage downloads the YouTube video and subtitle files using `yt-dlp`. The download process prioritizes quality while respecting configuration limits.

### Download Process Flow

```mermaid
flowchart TB
    Input["YouTube URL"]
    
    Script["download_video.py"]
    YtDlp["yt_dlp Python API"]
    
    FormatSelect["Format Selection Logic<br/>bestvideo[height<=MAX_VIDEO_HEIGHT]<br/>+bestaudio/best[height<=MAX_VIDEO_HEIGHT]"]
    
    VideoDownload["Download Video Stream<br/>Format: MP4"]
    SubtitleDownload["Download Subtitles<br/>Priority: en, en-US, en-GB<br/>Format: VTT"]
    
    VideoFile["video_id.mp4"]
    SubtitleFile["video_id.en.vtt"]
    
    AutoSubs["Fallback: Auto-generated subtitles"]
    
    Input --> Script
    Script --> YtDlp
    YtDlp --> FormatSelect
    
    FormatSelect --> VideoDownload
    FormatSelect --> SubtitleDownload
    
    SubtitleDownload -->|"Manual subs available"| SubtitleFile
    SubtitleDownload -->|"No manual subs"| AutoSubs
    AutoSubs --> SubtitleFile
    
    VideoDownload --> VideoFile
    
    VideoFile --> NextStage["Stage 3"]
    SubtitleFile --> NextStage
```

### Data Specifications

**Input:**
- YouTube URL (format: `https://youtube.com/watch?v=VIDEO_ID`)
- Configuration from `.env`: `MAX_VIDEO_HEIGHT`, `YT_DLP_PROXY`, `YT_DLP_RATE_LIMIT`

**Output:**
- Video file: `<video_id>.mp4` (H.264 codec, AAC audio)
- Subtitle file: `<video_id>.en.vtt` (WebVTT format)
- Metadata: Video title, duration, file size

**Script Invocation:**
```bash
cd ~/.claude/skills/youtube-clipper
python3 scripts/download_video.py <youtube_url>
```

**Sources:** [SKILL.md:68-93](), [README.md:106]()

## Stage 3: Semantic Analysis

This stage transforms raw subtitle data into structured semantic chapters through VTT parsing and AI-powered content analysis.

### Data Transformation Pipeline

```mermaid
flowchart LR
    VTT["video_id.en.vtt<br/>(WebVTT format)"]
    
    Parse["analyze_subtitles.py<br/>VTT Parser"]
    
    Structured["Structured Subtitle Data<br/>{timestamp, text}[]"]
    
    AI["Claude AI Analysis<br/>Semantic understanding"]
    
    Chapters["Chapter Metadata<br/>{title, start, end,<br/>summary, keywords}[]"]
    
    VTT --> Parse
    Parse --> Structured
    Structured --> AI
    AI --> Chapters
```

### Analysis Process

The semantic analysis follows this sequence:

1. **VTT Parsing** - `analyze_subtitles.py` extracts subtitle entries
2. **Data Preparation** - Formats subtitle data with timestamps for AI consumption
3. **AI Analysis** - Claude processes content to identify:
   - Topic boundaries and transitions
   - Natural breakpoints between subjects
   - Semantic coherence within segments
4. **Chapter Generation** - Produces structured chapter metadata

### Chapter Structure

Each generated chapter contains:

```python
{
    "title": str,           # 10-20 characters, topic summary
    "start_time": str,      # Format: "MM:SS" or "HH:MM:SS"
    "end_time": str,        # Format: "MM:SS" or "HH:MM:SS"
    "summary": str,         # 50-100 characters, core content
    "keywords": List[str]   # 3-5 key concepts
}
```

**Target Duration:** 180-300 seconds per chapter (configurable via `TARGET_CHAPTER_DURATION`)

**Script Invocation:**
```bash
python3 scripts/analyze_subtitles.py <subtitle_path>
```

**Sources:** [SKILL.md:96-144](), [README.md:16](), [README.md:194-209]()

## Stage 4: User Selection

This stage presents generated chapters to the user and collects processing options through the `AskUserQuestion` tool. User choices determine which conditional processing branches execute in Stage 5.

### Selection Interface

The system presents:
- Enumerated chapter list with titles, time ranges, and summaries
- Multi-selection prompt for chapter indices
- Boolean prompts for processing options

### Decision Matrix

```mermaid
flowchart TB
    Chapters["Generated Chapters List"]
    
    Select["User Selects Chapters<br/>(Multi-select by index)"]
    
    Q1["Generate bilingual subtitles?"]
    Q2["Burn subtitles into video?"]
    Q3["Generate summary content?"]
    
    Plan["Processing Plan<br/>{chapters[], options{}}"]
    
    Chapters --> Select
    Select --> Q1
    Q1 -->|"Yes/No"| Q2
    Q2 -->|"Yes/No"| Q3
    Q3 -->|"Yes/No"| Plan
    
    Plan --> Stage5["Stage 5: Execute Plan"]
```

**Output Structure:**
```python
{
    "selected_chapters": List[int],  # Chapter indices
    "options": {
        "bilingual_subtitles": bool,
        "burn_subtitles": bool,
        "generate_summary": bool
    }
}
```

**Sources:** [SKILL.md:146-161]()

## Stage 5: Parallel Processing

Stage 5 executes multiple processing operations per selected chapter. Operations may execute in parallel or sequentially depending on dependencies.

### Processing Dependency Graph

```mermaid
flowchart TB
    Start["Selected Chapter"]
    
    ClipVideo["clip_video.py<br/>Extract video segment"]
    ExtractSubs["extract_subtitle_clip.py<br/>Extract subtitle segment"]
    
    VideoClip["chapter_clip.mp4"]
    OriginalSRT["chapter_original.srt"]
    
    TranslateCheck{{"Bilingual option<br/>enabled?"}}
    
    TranslateBatch["Batch Translation<br/>20-25 lines per API call"]
    TranslatedSRT["chapter_translated.srt"]
    
    MergeSubs["Merge EN + Translated<br/>Bilingual format"]
    BilingualSRT["chapter_bilingual.srt"]
    
    BurnCheck{{"Burn subtitles<br/>enabled?"}}
    
    BurnSubs["burn_subtitles.py<br/>FFmpeg subtitles filter"]
    BurnedVideo["chapter_with_subtitles.mp4"]
    
    SummaryCheck{{"Generate summary<br/>enabled?"}}
    
    GenSummary["generate_summary.py<br/>Social media content"]
    SummaryMD["chapter_summary.md"]
    
    Complete["Chapter Complete"]
    
    Start --> ClipVideo
    Start --> ExtractSubs
    
    ClipVideo --> VideoClip
    ExtractSubs --> OriginalSRT
    
    OriginalSRT --> TranslateCheck
    TranslateCheck -->|"Yes"| TranslateBatch
    TranslateCheck -->|"No"| BurnCheck
    
    TranslateBatch --> TranslatedSRT
    TranslatedSRT --> MergeSubs
    OriginalSRT --> MergeSubs
    MergeSubs --> BilingualSRT
    
    BilingualSRT --> BurnCheck
    VideoClip --> BurnCheck
    
    BurnCheck -->|"Yes"| BurnSubs
    BurnCheck -->|"No"| SummaryCheck
    
    BurnSubs --> BurnedVideo
    BurnedVideo --> SummaryCheck
    
    SummaryCheck -->|"Yes"| GenSummary
    SummaryCheck -->|"No"| Complete
    
    GenSummary --> SummaryMD
    SummaryMD --> Complete
```

### Core Processing Operations

#### 5.1: Video Clipping

**Script:** `clip_video.py`

**Input:**
- Source video path: `<video_id>.mp4`
- Time range: `start_time`, `end_time` (seconds)
- Output path specification

**Process:**
```bash
python3 scripts/clip_video.py <video_path> <start_time> <end_time> <output_path>
```

**Output:** Clipped video segment with original quality (stream copy, no re-encoding)

#### 5.2: Subtitle Extraction

**Script:** `extract_subtitle_clip.py`

**Process:**
1. Parse complete SRT/VTT subtitle file using `pysrt`
2. Filter entries where `start_time` falls within chapter range
3. Adjust timestamps by subtracting chapter start time
4. Convert to SRT format
5. Write time-adjusted subtitle segment

**Output:** `<chapter>_original.srt` with timestamps starting at 00:00:00

#### 5.3: Batch Translation

**Optimization Strategy:**
- Group 20-25 subtitle entries per API call
- Single translation request per batch
- Maintains context consistency across batches

**API Call Reduction:**
- Traditional: N API calls for N subtitle lines
- Optimized: N/20 API calls (95% reduction)

**Translation Parameters:**
- Target language: From `TARGET_LANGUAGE` config
- Style: Conversational, concise
- Technical term handling: Preserve accuracy

#### 5.4: Bilingual Subtitle Generation

**Format Specification:**
```srt
1
00:00:00,000 --> 00:00:03,500
English text line
中文翻译文本

2
00:00:03,500 --> 00:00:07,000
Next English line
下一行中文
```

Each entry contains original English on first line, translation on second line.

#### 5.5: Subtitle Burning

**Script:** `burn_subtitles.py`

**Critical Implementation Detail:** Uses temporary directory workaround for path handling

**Process Flow:**
```mermaid
flowchart LR
    Input["video + subtitle files<br/>(may have spaces in path)"]
    
    TempDir["Create temp directory<br/>(no spaces)"]
    Copy["Copy files to temp"]
    
    FFmpeg["ffmpeg with subtitles filter<br/>-vf subtitles=file.srt:force_style=..."]
    
    Move["Move output to target path"]
    Cleanup["Remove temp directory"]
    
    Output["video_with_subtitles.mp4"]
    
    Input --> TempDir
    TempDir --> Copy
    Copy --> FFmpeg
    FFmpeg --> Move
    Move --> Cleanup
    Cleanup --> Output
```

**FFmpeg Command Structure:**
```bash
ffmpeg -i video.mp4 -vf "subtitles=subtitle.srt:force_style='FontSize=24,MarginV=30'" -c:a copy output.mp4
```

**Style Parameters:**
- `FontSize`: 24 (configurable via `SUBTITLE_FONT_SIZE`)
- `MarginV`: 30 (configurable via `SUBTITLE_MARGIN_V`)
- Color: White text with black outline (default)

#### 5.6: Summary Generation

**Script:** `generate_summary.py`

**Input:** Chapter metadata (title, summary, keywords)

**Output:** Markdown file with platform-specific social media content

**Platforms Targeted:**
- Xiaohongshu (小红书)
- Douyin (抖音)
- WeChat (微信公众号)

**Sources:** [SKILL.md:164-234](), [README.md:109](), [README.md:213-216]()

## Stage 6: Output Organization

The final stage organizes processed files into a structured directory hierarchy.

### Directory Structure Creation

```mermaid
flowchart TB
    Root["./youtube-clips/"]
    
    Session["YYYYMMDD_HHMMSS/<br/>(timestamp-based session)"]
    
    Ch1["Chapter_1_Title/<br/>(sanitized name)"]
    Ch2["Chapter_2_Title/"]
    ChN["Chapter_N_Title/"]
    
    Files1["- chapter_clip.mp4<br/>- chapter_bilingual.srt<br/>- chapter_with_subtitles.mp4<br/>- chapter_summary.md"]
    
    Files2["(same file types)"]
    FilesN["(same file types)"]
    
    Root --> Session
    Session --> Ch1
    Session --> Ch2
    Session --> ChN
    
    Ch1 --> Files1
    Ch2 --> Files2
    ChN --> FilesN
```

### File Naming Convention

All output files follow the pattern: `<sanitized_chapter_title>_<type>.<ext>`

**Sanitization Rules:**
- Remove characters: `/ \ : * ? " < > |`
- Replace spaces with underscores
- Truncate to 100 characters maximum
- Preserve Unicode characters for non-English titles

**File Types Per Chapter:**

| File Type | Suffix | Always Present | Condition |
|-----------|--------|----------------|-----------|
| Clipped video | `_clip.mp4` | Yes | Always generated |
| Bilingual subtitles | `_bilingual.srt` | No | If bilingual option enabled |
| Video with subtitles | `_with_subtitles.mp4` | No | If burn option enabled |
| Summary content | `_summary.md` | No | If summary option enabled |

**Sources:** [SKILL.md:236-279](), [README.md:115-123]()

## Error Handling and Recovery

The pipeline implements error handling at stage boundaries with recovery mechanisms.

### Error Categories and Responses

```mermaid
flowchart TD
    Error["Error Detected"]
    
    Type{"Error Type"}
    
    Env["Environment Error<br/>(Stage 1)"]
    Network["Network Error<br/>(Stage 2)"]
    Parse["Parse Error<br/>(Stage 3)"]
    Process["Processing Error<br/>(Stage 5)"]
    
    EnvAction["Display installation guidance<br/>Block pipeline progress"]
    NetworkAction["Retry with exponential backoff<br/>Max 3 attempts"]
    ParseAction["Request manual subtitle upload<br/>Or skip chapter"]
    ProcessAction["Log error, continue with next chapter<br/>Partial completion allowed"]
    
    Error --> Type
    
    Type -->|"Missing dependencies"| Env
    Type -->|"Download failed"| Network
    Type -->|"Invalid subtitle format"| Parse
    Type -->|"FFmpeg/translation failed"| Process
    
    Env --> EnvAction
    Network --> NetworkAction
    Parse --> ParseAction
    Process --> ProcessAction
```

### Retry Mechanisms

**Network Operations (Stage 2):**
- Initial timeout: 30 seconds
- Retry count: 3
- Backoff: Exponential (1s, 2s, 4s)

**Translation API (Stage 5.3):**
- Retry count: 3
- Batch size reduction on failure
- Continue with untranslated on exhaustion

**FFmpeg Operations (Stage 5):**
- No automatic retry
- Log full error output
- Skip to next chapter on failure

**Sources:** [SKILL.md:322-337]()

## Performance Characteristics

### Pipeline Execution Times

Approximate durations for a 30-minute source video:

| Stage | Duration | Scaling Factor |
|-------|----------|----------------|
| Environment Detection | 2-5 seconds | Constant |
| Video Download | 1-10 minutes | Video length × quality |
| Semantic Analysis | 10-30 seconds | Subtitle count |
| User Selection | Variable | User interaction |
| Processing (per chapter) | 1-3 minutes | Chapter length × options |
| Output Organization | <5 seconds | File count |

### Batch Translation Performance

**Traditional approach:** 400 subtitle lines → 400 API calls → ~20 minutes

**Optimized approach:** 400 subtitle lines → 20 API calls → ~2 minutes

**Improvement:** 90% time reduction, 95% API call reduction

**Sources:** [README.md:213-216](), [SKILL.md:293-300]()

## Data Flow Summary

### Complete Pipeline Data Transformation

```mermaid
flowchart LR
    URL["YouTube URL<br/>(string)"]
    
    Video["video_id.mp4<br/>(H.264/AAC)"]
    VTT["video_id.en.vtt<br/>(WebVTT)"]
    
    Structured["Structured Subtitle Data<br/>(Python dict list)"]
    
    Chapters["Chapter Metadata<br/>(JSON structure)"]
    
    Selection["User Selections<br/>(indices + options)"]
    
    Clip["chapter_clip.mp4<br/>(H.264/AAC segment)"]
    SRT["chapter_bilingual.srt<br/>(SRT format)"]
    Burned["chapter_with_subtitles.mp4<br/>(H.264 with burned subs)"]
    Summary["chapter_summary.md<br/>(Markdown)"]
    
    URL -->|"download_video.py"| Video
    URL -->|"download_video.py"| VTT
    
    VTT -->|"analyze_subtitles.py"| Structured
    Structured -->|"Claude AI"| Chapters
    
    Chapters -->|"AskUserQuestion"| Selection
    
    Selection -->|"clip_video.py"| Clip
    Selection -->|"extract + translate"| SRT
    Clip -->|"burn_subtitles.py"| Burned
    Chapters -->|"generate_summary.py"| Summary
```

**Sources:** [SKILL.md:22-279](), README diagrams

---

# Page: AI Integration

# AI Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [SKILL.md](SKILL.md)

</details>



This document explains how Claude AI is integrated into the YouTube Clipper Skill system to provide intelligent video processing capabilities. The AI integration occurs at two critical points in the processing pipeline: semantic chapter analysis and batch subtitle translation.

For detailed information about the batch translation optimization strategy, see [Batch Translation Optimization](#7.1). For specifics on the semantic analysis algorithm, see [AI Semantic Analysis](#7.2). For implementation details of the subtitle analysis script, see [analyze_subtitles.py](#4.2).

---

## Overview

The YouTube Clipper Skill uses Claude AI as its intelligence layer for two core differentiating features:

| Feature | Purpose | Optimization | API Reduction |
|---------|---------|--------------|---------------|
| **Semantic Chapter Analysis** | Generate meaningful 2-5 minute chapters based on content understanding | Single AI call per video | N/A |
| **Batch Translation** | Translate subtitle segments to target language | Group 20-25 lines per API call | 95% reduction |

Both AI integration points are designed to minimize API calls while maximizing output quality through context preservation and intelligent batching.

Sources: [README.md:14-20](), [SKILL.md:96-144](), [SKILL.md:185-194]()

---

## AI Integration Architecture

### System-Level AI Integration Points

```mermaid
graph TB
    subgraph "Input Data Layer"
        Video["YouTube Video<br/>download_video.py"]
        VTT["VTT Subtitles<br/>*.en.vtt"]
    end
    
    subgraph "AI Processing Layer"
        AnalyzeScript["analyze_subtitles.py<br/>Parse VTT → Structured Data"]
        
        ClaudeAnalysis["Claude AI Semantic Analysis<br/>model: claude-sonnet-4-5-20250514"]
        
        TranslateScript["translate_subtitles.py<br/>Batch Grouping"]
        
        ClaudeTranslate["Claude AI Translation<br/>Batch API Calls"]
    end
    
    subgraph "Processing Logic"
        ChapterGen["Chapter Generation Logic<br/>Target: 180-300s per chapter"]
        BatchLogic["Batch Processing Logic<br/>Size: 20-25 lines/batch"]
    end
    
    subgraph "Output Layer"
        Chapters["Semantic Chapters<br/>JSON Structure"]
        BilingualSRT["Bilingual Subtitles<br/>*.srt format"]
    end
    
    Video --> VTT
    VTT --> AnalyzeScript
    AnalyzeScript --> ClaudeAnalysis
    ClaudeAnalysis --> ChapterGen
    ChapterGen --> Chapters
    
    VTT --> TranslateScript
    TranslateScript --> BatchLogic
    BatchLogic --> ClaudeTranslate
    ClaudeTranslate --> BilingualSRT
    
    style ClaudeAnalysis fill:#f9f9f9
    style ClaudeTranslate fill:#f9f9f9
```

**AI Integration Points in Codebase**

This diagram maps the natural language workflow to specific code entities. The `analyze_subtitles.py` script parses VTT format subtitles and prepares structured data for Claude AI analysis. The Claude AI model specified in [SKILL.md:14]() is `claude-sonnet-4-5-20250514`, which performs both semantic analysis and translation tasks. The `translate_subtitles.py` script implements the batching logic that groups subtitle lines before sending them to the AI.

Sources: [SKILL.md:96-110](), [SKILL.md:185-194](), [README.md:140-150]()

---

## Semantic Chapter Analysis

### Purpose and Methodology

The semantic chapter analysis is the system's core differentiating feature. Unlike mechanical time-based video splitting (e.g., every 30 minutes), this system uses Claude AI to understand video content and identify natural topic boundaries.

**Analysis Objectives:**
- Parse complete subtitle transcripts with timestamps
- Identify semantic topic transitions and natural breakpoints
- Generate chapters with duration between 2-5 minutes (configurable via `TARGET_CHAPTER_DURATION`)
- Ensure complete video coverage with no gaps or overlaps
- Create meaningful metadata for each chapter

Sources: [README.md:194-209](), [SKILL.md:96-127]()

### Implementation Flow

```mermaid
sequenceDiagram
    participant User
    participant ClaudeCode as "Claude Code<br/>Main Process"
    participant AnalyzeScript as "analyze_subtitles.py"
    participant ClaudeAI as "Claude AI<br/>Sonnet 4.5"
    participant ChapterOutput as "Chapter Data<br/>JSON Structure"
    
    User->>ClaudeCode: "Clip this video: <URL>"
    ClaudeCode->>AnalyzeScript: python3 scripts/analyze_subtitles.py <subtitle.vtt>
    
    AnalyzeScript->>AnalyzeScript: Parse VTT format
    AnalyzeScript->>AnalyzeScript: Extract timestamps + text
    AnalyzeScript->>ClaudeCode: Return structured subtitle data
    
    Note over ClaudeCode: Prepare analysis context<br/>Include full transcript + timestamps
    
    ClaudeCode->>ClaudeAI: Analyze semantic content<br/>Target: 180-300s chapters<br/>Full subtitle text provided
    
    Note over ClaudeAI: Content understanding<br/>Topic transition detection<br/>Boundary identification
    
    ClaudeAI->>ChapterOutput: Generate chapters with:<br/>- Title (10-20 chars)<br/>- Time range (start/end)<br/>- Summary (50-100 chars)<br/>- Keywords (3-5 terms)
    
    ChapterOutput->>ClaudeCode: Return chapter list
    ClaudeCode->>User: Display chapters for selection
```

**Key Implementation Details:**

The `analyze_subtitles.py` script handles VTT parsing and data preparation. It outputs structured subtitle data including:
- Full subtitle text with timestamps
- Total video duration
- Subtitle entry count

Claude Code then performs the AI analysis by reading the complete subtitle content and applying semantic understanding. The analysis is not performed within the Python script itself but rather in the Claude Code execution environment, allowing Claude AI to read and understand the full context.

Sources: [SKILL.md:100-110](), [SKILL.md:111-127]()

### Chapter Generation Principles

The semantic analysis follows specific principles defined in [SKILL.md:122-127]():

| Principle | Target | Purpose |
|-----------|--------|---------|
| **Granularity** | 2-5 minutes per chapter | Avoid too-short clips or 30+ minute segments |
| **Completeness** | 100% video coverage | No gaps, no overlaps |
| **Semantic Meaning** | One topic per chapter | Each chapter is a coherent unit |
| **Natural Boundaries** | Topic transition points | Not mechanical time-based splitting |

**Chapter Metadata Structure:**

Each generated chapter contains:
- **Title**: Concise topic summary (10-20 characters)
- **Time Range**: `MM:SS` or `HH:MM:SS` format start and end times
- **Core Summary**: 1-2 sentence description (50-100 characters)
- **Keywords**: 3-5 core concepts for that segment

Example output format from [SKILL.md:128-143]():

```
1. [00:00 - 03:15] AGI as an exponential curve, not a point in time
   Core: AI model capabilities double every 4-12 months
   Keywords: AGI, exponential growth, Claude Code

2. [03:15 - 06:30] China's gap in AI development
   Core: Chip bans impact Chinese AI capabilities
   Keywords: China, chip ban, DeepSeek
```

Sources: [SKILL.md:122-143](), [README.md:203-209]()

---

## Batch Translation System

### The Optimization Problem

Traditional subtitle translation approaches translate each subtitle line individually, resulting in:
- High API call volume (one call per subtitle line)
- Slow processing (network latency per call)
- Potential context loss between lines
- Expensive API usage

For a typical video with 400+ subtitle entries, individual translation would require 400+ API calls.

Sources: [README.md:211-216](), [SKILL.md:291-299]()

### Batching Strategy

The system implements an intelligent batching strategy defined in [SKILL.md:185-194]():

**Batch Parameters:**
- **Batch Size**: 20-25 subtitle lines per API call (configurable via `TRANSLATION_BATCH_SIZE` in `.env`)
- **API Call Reduction**: 95% reduction (e.g., 400 lines → 20 API calls)
- **Context Preservation**: All lines in a batch are translated together, maintaining semantic consistency

```mermaid
graph LR
    subgraph "Input: Subtitle Segment"
        SRT1["Subtitle 1<br/>00:00:00,000 → 00:00:03,500"]
        SRT2["Subtitle 2<br/>00:00:03,500 → 00:00:07,000"]
        SRT3["..."]
        SRT20["Subtitle 20<br/>00:01:30,000 → 00:01:33,500"]
    end
    
    subgraph "Batch Processing"
        Group["Group 20-25 Lines<br/>translate_subtitles.py"]
        Batch["Single Batch Request<br/>All lines as context"]
    end
    
    subgraph "Claude AI Translation"
        Context["Maintain Context<br/>Understand relationships"]
        Translate["Translate All Lines<br/>Consistent terminology"]
    end
    
    subgraph "Output: Translated Batch"
        Trans1["Translation 1<br/>这是第一行字幕"]
        Trans2["Translation 2<br/>这是第二行字幕"]
        Trans3["..."]
        Trans20["Translation 20<br/>这是第二十行字幕"]
    end
    
    SRT1 --> Group
    SRT2 --> Group
    SRT3 --> Group
    SRT20 --> Group
    
    Group --> Batch
    Batch --> Context
    Context --> Translate
    
    Translate --> Trans1
    Translate --> Trans2
    Translate --> Trans3
    Translate --> Trans20
```

**Translation Strategy Details:**

The `translate_subtitles.py` script implements the batching logic:
1. Groups subtitle lines into batches of 20-25 entries
2. Sends entire batch to Claude AI in a single API call
3. Receives all translations in a single response
4. Maintains line ordering and timestamp associations

Translation quality guidelines from [SKILL.md:189-193]():
- Preserve technical terminology accuracy
- Use conversational tone (suitable for short-form video)
- Produce concise and fluent output
- Maintain consistency within each batch

Sources: [SKILL.md:185-194](), [README.md:144](), [SKILL.md:291-299]()

### Context Preservation and Consistency

Batching provides semantic advantages beyond API efficiency:

| Aspect | Individual Translation | Batch Translation |
|--------|----------------------|-------------------|
| **Context Awareness** | No context between lines | Full batch context available |
| **Terminology Consistency** | May vary between calls | Consistent within batch |
| **Semantic Flow** | Disconnected | Natural conversation flow |
| **API Calls (400 lines)** | 400 calls | 20 calls (95% reduction) |
| **Processing Time** | ~400 × latency | ~20 × latency (10x faster) |

The Claude AI model can understand the relationships between subtitle lines within a batch, producing more natural and contextually appropriate translations.

Sources: [README.md:211-216](), [SKILL.md:291-299]()

---

## Configuration and Customization

AI integration behavior can be customized through environment variables in the `.env` file:

**Semantic Analysis Configuration:**
```bash
# Target chapter duration in seconds (default: 180-300s range)
TARGET_CHAPTER_DURATION=180
```

**Translation Configuration:**
```bash
# Batch size for subtitle translation (default: 20)
TRANSLATION_BATCH_SIZE=20

# Target language for translation (default: 中文)
TARGET_LANGUAGE=中文
```

These parameters are read by the processing scripts to adjust AI call patterns and output characteristics.

Sources: [README.md:144-150](), [SKILL.md:14]()

---

## API Call Flow and Error Handling

### Semantic Analysis API Flow

```mermaid
graph TD
    Start["User Request:<br/>Clip video URL"]
    
    VTTParse["analyze_subtitles.py<br/>Parse VTT file"]
    
    PrepareContext["Prepare AI Context<br/>- Full transcript<br/>- Timestamps<br/>- Duration<br/>- Target chapter length"]
    
    AICall["Single Claude AI Call<br/>Model: claude-sonnet-4-5-20250514"]
    
    Generate["Generate All Chapters<br/>- Semantic boundaries<br/>- Metadata<br/>- Coverage validation"]
    
    Output["Output Chapter List<br/>Present to user"]
    
    Start --> VTTParse
    VTTParse --> PrepareContext
    PrepareContext --> AICall
    AICall --> Generate
    Generate --> Output
    
    AICall -->|Network Error| Retry["Retry up to 3 times"]
    Retry --> AICall
```

**Error Handling:**
- Network failures: Automatic retry up to 3 times
- Invalid response: Log error and prompt user for manual intervention
- Timeout: Extend timeout for long videos (handled by Claude Code environment)

Sources: [SKILL.md:96-144](), [SKILL.md:329-336]()

### Batch Translation API Flow

```mermaid
graph TD
    Start["Extracted Subtitle Segment<br/>*.srt file"]
    
    LoadSRT["translate_subtitles.py<br/>Load SRT file"]
    
    CreateBatches["Create Batches<br/>Size: TRANSLATION_BATCH_SIZE"]
    
    LoopStart{More Batches?}
    
    TranslateBatch["Claude AI Call<br/>Translate batch[i]"]
    
    ParseResponse["Parse Translation Response<br/>Maintain line order"]
    
    Progress["Update Progress<br/>Display: X/Y lines translated"]
    
    LoopStart --> |Yes| TranslateBatch
    TranslateBatch --> ParseResponse
    ParseResponse --> Progress
    Progress --> LoopStart
    
    LoopStart --> |No| Merge["Merge All Translations<br/>Create bilingual SRT"]
    
    Merge --> Output["Output: *_bilingual.srt"]
    
    Start --> LoadSRT
    LoadSRT --> CreateBatches
    CreateBatches --> LoopStart
    
    TranslateBatch -->|API Error| RetryBatch["Retry batch<br/>Max 3 attempts"]
    RetryBatch --> TranslateBatch
```

**Progress Display:**

The system provides real-time progress updates during translation, as shown in [SKILL.md:223-234]():

```
3/6 Translating subtitles... [=====>    ] 50% (26/52)
```

This shows the number of lines translated out of the total, giving users visibility into the batch processing progress.

Sources: [SKILL.md:185-194](), [SKILL.md:223-234](), [SKILL.md:329-336]()

---

## Integration with Claude Code Platform

The AI integration is designed specifically for the Claude Code environment, specified in [SKILL.md:14]():

```yaml
model: claude-sonnet-4-5-20250514
```

This model specification ensures:
- Consistent AI capabilities across all installations
- Access to advanced semantic understanding features
- Optimal performance for subtitle analysis and translation tasks

The skill uses Claude Code's native AI capabilities, meaning:
- No separate API key configuration required
- Direct access to Claude AI within the execution environment
- Seamless integration with Claude Code's tool system (`AskUserQuestion`, `Read`, `Write`, `Bash`)

Sources: [SKILL.md:1-15](), [README.md:3-4]()

---

## Performance Characteristics

### Semantic Analysis Performance

| Metric | Typical Value | Notes |
|--------|---------------|-------|
| **Videos per Analysis** | 1 | Single AI call per video |
| **Analysis Time** | 5-15 seconds | Depends on video length |
| **Chapters Generated** | Video duration ÷ 3 minutes | Target: 2-5 min per chapter |
| **Coverage** | 100% | No gaps in video timeline |

### Batch Translation Performance

| Metric | Without Batching | With Batching (20-line) | Improvement |
|--------|------------------|------------------------|-------------|
| **API Calls (400 lines)** | 400 | 20 | 95% reduction |
| **Estimated Time** | ~400 × 1.5s = 10 min | ~20 × 1.5s = 30s | 20x faster |
| **Context Quality** | Independent lines | Contextual batches | Higher quality |
| **API Cost** | Baseline | 5% of baseline | 95% cost reduction |

These performance improvements make the system practical for processing long-form content while maintaining high translation quality through context preservation.

Sources: [README.md:211-216](), [SKILL.md:291-299]()

---

# Page: File Organization

# File Organization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [SKILL.md](SKILL.md)

</details>



This document describes the file organization structure of the YouTube Clipper Skill, including both the repository source structure and the runtime output directory structure. For information about the processing scripts themselves, see [Core Scripts](#4). For configuration file details, see [Configuration](#6).

## Purpose and Scope

This page documents:
- Repository source code organization
- Output directory hierarchy and structure
- File naming conventions for generated content
- Types of files produced per chapter
- Temporary file management strategies

## Repository Structure

The YouTube Clipper Skill repository follows a clean separation of concerns with source code, documentation, configuration, and installation automation in distinct locations.

```mermaid
graph TB
    Root["Repository Root"]
    
    Root --> Scripts["scripts/<br/>Python modules"]
    Root --> Refs["references/<br/>Technical guides"]
    Root --> GitHub[".github/<br/>Repository metadata"]
    Root --> Env[".env<br/>User configuration"]
    Root --> EnvEx[".env.example<br/>Configuration template"]
    Root --> Install["install_as_skill.sh<br/>Installation script"]
    Root --> Readme["README.md<br/>User documentation"]
    Root --> ReadmeCN["README.zh-CN.md<br/>Chinese documentation"]
    Root --> Skill["SKILL.md<br/>Workflow specification"]
    Root --> Tech["TECHNICAL_NOTES.md<br/>Implementation details"]
    
    Scripts --> DownloadPy["download_video.py"]
    Scripts --> AnalyzePy["analyze_subtitles.py"]
    Scripts --> ClipPy["clip_video.py"]
    Scripts --> BurnPy["burn_subtitles.py"]
    Scripts --> ExtractPy["extract_subtitle_clip.py"]
    Scripts --> Utils["utils.py"]
    
    style Scripts fill:#f9f9f9
    style Root fill:#e8e8e8
```

**Sources:** [README.md:1-320](), [SKILL.md:1-374]()

### Key Directories and Files

| Path | Type | Purpose |
|------|------|---------|
| `scripts/` | Directory | Contains all Python processing scripts |
| `references/` | Directory | Technical reference documentation for FFmpeg, yt-dlp |
| `.github/` | Directory | GitHub repository metadata and configuration |
| `.env` | File | User-specific configuration (created during installation) |
| `.env.example` | File | Configuration template with default values |
| `install_as_skill.sh` | File | Automated installation script for Claude Code |
| `README.md` | File | Primary user documentation in English |
| `README.zh-CN.md` | File | User documentation in Chinese |
| `SKILL.md` | File | Detailed workflow specification for Claude Code |
| `TECHNICAL_NOTES.md` | File | Implementation notes and design decisions |

**Sources:** [README.md:24-47](), [SKILL.md:19-65]()

## Installation Location

When installed as a Claude Code skill, the repository is copied to the user's home directory:

```
~/.claude/skills/youtube-clipper/
├── scripts/
│   ├── download_video.py
│   ├── analyze_subtitles.py
│   ├── clip_video.py
│   ├── burn_subtitles.py
│   ├── extract_subtitle_clip.py
│   └── utils.py
├── .env
├── .env.example
└── SKILL.md
```

The installation script [install_as_skill.sh:1-100]() handles copying files to this location and installing Python dependencies.

**Sources:** [README.md:32-46](), [SKILL.md:19-20]()

## Output Directory Structure

The YouTube Clipper Skill generates organized output in a three-level hierarchy: root directory → timestamped session → chapter directories.

```mermaid
graph TB
    subgraph "Current Working Directory"
        CWD["Current Working Directory"]
    end
    
    CWD --> OutputRoot["youtube-clips/"]
    
    OutputRoot --> Session1["20260122_143022/<br/>Session timestamp"]
    OutputRoot --> Session2["20260123_095500/<br/>Another session"]
    
    Session1 --> Chapter1["AGI_as_exponential_curve/<br/>Sanitized chapter title"]
    Session1 --> Chapter2["Chinas_AI_development_gap/<br/>Another chapter"]
    
    Chapter1 --> Clip1["AGI_as_exponential_curve_clip.mp4"]
    Chapter1 --> Burned1["AGI_as_exponential_curve_with_subtitles.mp4"]
    Chapter1 --> SRT1["AGI_as_exponential_curve_bilingual.srt"]
    Chapter1 --> Summary1["AGI_as_exponential_curve_summary.md"]
    
    style OutputRoot fill:#f9f9f9
    style Session1 fill:#e8e8e8
    style Chapter1 fill:#d8d8d8
```

**Sources:** [README.md:112-123](), [SKILL.md:242-262]()

### Directory Hierarchy Levels

#### Level 1: Output Root Directory

The root output directory is configurable via the `OUTPUT_DIR` environment variable, defaulting to `./youtube-clips/` in the current working directory.

**Path:** `./youtube-clips/`

This directory contains all video processing sessions and is created automatically if it doesn't exist.

**Sources:** [README.md:138](), [SKILL.md:244]()

#### Level 2: Session Timestamp Directory

Each video processing session creates a timestamped subdirectory using the format `YYYYMMDD_HHMMSS`:

- **Format:** `20260122_143022` (Year-Month-Day_Hour-Minute-Second)
- **Purpose:** Prevents file conflicts across multiple sessions
- **Example:** `20260122_143022/` for a session started on January 22, 2026 at 14:30:22

This timestamp-based naming ensures that:
- Multiple processing sessions never conflict
- Output files are chronologically organized
- Session provenance is clear from the directory name

**Sources:** [README.md:117](), [SKILL.md:244]()

#### Level 3: Chapter Directory

Each selected chapter creates a subdirectory named after the sanitized chapter title:

**Path:** `./youtube-clips/20260122_143022/Chapter_Title/`

Chapter directory names undergo sanitization to ensure filesystem compatibility:
- Special characters removed: `/ \ : * ? " < > |`
- Spaces replaced with underscores
- Length limited to 100 characters

**Sources:** [README.md:118](), [SKILL.md:342-350]()

## File Types Generated

Each chapter directory can contain up to four distinct file types, depending on user-selected processing options:

```mermaid
graph LR
    subgraph "Chapter Directory"
        ChapterDir["Chapter_Title/"]
    end
    
    ChapterDir --> ClipFile["*_clip.mp4<br/>Original video segment"]
    ChapterDir --> BurnedFile["*_with_subtitles.mp4<br/>Video with burned subtitles"]
    ChapterDir --> SRTFile["*_bilingual.srt<br/>Bilingual subtitle file"]
    ChapterDir --> SummaryFile["*_summary.md<br/>Social media content"]
    
    ClipFile -.-> Always["Always generated"]
    BurnedFile -.-> Optional1["Generated if user selects<br/>subtitle burning"]
    SRTFile -.-> Optional2["Generated if user selects<br/>bilingual subtitles"]
    SummaryFile -.-> Optional3["Generated if user selects<br/>content summary"]
```

**Sources:** [README.md:114-123](), [SKILL.md:248-255]()

### File Type Reference

| File Type | Naming Pattern | Always Generated | Purpose | Script |
|-----------|----------------|------------------|---------|--------|
| Video Clip | `{title}_clip.mp4` | ✅ Yes | Original extracted video segment without subtitles | [scripts/clip_video.py]() |
| Burned Subtitles | `{title}_with_subtitles.mp4` | ❌ Optional | Video with hardcoded bilingual subtitles | [scripts/burn_subtitles.py]() |
| Bilingual SRT | `{title}_bilingual.srt` | ❌ Optional | Subtitle file with English and target language | [scripts/extract_subtitle_clip.py]() |
| Summary | `{title}_summary.md` | ❌ Optional | Social media content and chapter summary | Generated by Claude AI |

**Sources:** [README.md:114-123](), [SKILL.md:170-220]()

### File Content Details

#### Video Clip File (`*_clip.mp4`)

- **Format:** MP4 container with H.264 video codec
- **Quality:** Preserved from source (up to 1080p)
- **Audio:** Original audio track maintained
- **Generation:** FFmpeg stream copy for lossless extraction
- **Script:** [scripts/clip_video.py:1-100]()

The video clip is always generated and represents the precise time-bounded segment extracted from the source video.

**Sources:** [SKILL.md:170-176]()

#### Burned Subtitles File (`*_with_subtitles.mp4`)

- **Format:** MP4 with hardcoded subtitle overlay
- **Subtitle Style:** White text with black outline, customizable font size and margins
- **Encoding:** Re-encoded to embed subtitles (not stream copy)
- **Requirements:** FFmpeg with libass support
- **Script:** [scripts/burn_subtitles.py:1-200]()

This file is only generated if the user selects the subtitle burning option. It embeds the bilingual subtitles permanently into the video frames.

**Sources:** [README.md:69-83](), [SKILL.md:202-211]()

#### Bilingual SRT File (`*_bilingual.srt`)

- **Format:** SubRip (SRT) text format
- **Structure:** Each subtitle entry contains both English and target language
- **Encoding:** UTF-8
- **Line Order:** English text followed by translated text

Example format:
```srt
1
00:00:00,000 --> 00:00:03,500
This is the English subtitle
这是中文字幕

2
00:00:03,500 --> 00:00:07,000
Another English line
另一行中文
```

**Sources:** [README.md:218-232](), [SKILL.md:195-199]()

#### Summary File (`*_summary.md`)

- **Format:** Markdown
- **Contents:** Chapter title, core summary, keywords, social media copy
- **Platforms:** Optimized for Xiaohongshu, Douyin, WeChat
- **Generation:** Claude AI based on chapter metadata

This file provides ready-to-use content for social media sharing and video description.

**Sources:** [README.md:20](), [SKILL.md:213-220]()

## File Naming Convention

The YouTube Clipper Skill applies consistent naming rules to ensure filesystem compatibility and readability.

### Sanitization Rules

All generated filenames undergo the following transformations:

```mermaid
graph LR
    Original["Original Title:<br/>'China's AI: Gap?'"]
    Remove["Remove Special Chars:<br/>' * ? \" < > | / \\ :'"]
    Replace["Replace Spaces:<br/>' ' → '_'"]
    Limit["Limit Length:<br/>Max 100 characters"]
    Final["Final Name:<br/>'Chinas_AI_Gap'"]
    
    Original --> Remove
    Remove --> Replace
    Replace --> Limit
    Limit --> Final
```

**Sources:** [README.md:270-277](), [SKILL.md:342-350]()

### Character Handling

| Input | Action | Reason |
|-------|--------|--------|
| `/` `\` `:` `*` `?` `"` `<` `>` `|` | Removed | Filesystem reserved characters |
| Space ` ` | Replaced with `_` | Improves command-line usability |
| Length > 100 chars | Truncated | Prevents filesystem path length limits |
| Unicode characters | Preserved | Supports international titles |

### Naming Pattern Components

Each generated file follows this pattern:

```
{sanitized_chapter_title}_{file_type}.{extension}
```

Where:
- `{sanitized_chapter_title}`: Chapter title after sanitization rules
- `{file_type}`: One of `clip`, `with_subtitles`, `bilingual`, `summary`
- `{extension}`: File extension (`.mp4`, `.srt`, `.md`)

**Example transformations:**

| Original Chapter Title | Sanitized Filename Base |
|------------------------|-------------------------|
| `AGI as an exponential curve, not a point in time` | `AGI_as_an_exponential_curve_not_a_point_in_time` |
| `China's gap in AI development` | `Chinas_gap_in_AI_development` |
| `The impact of chip bans: consequences?` | `The_impact_of_chip_bans_consequences` |

**Sources:** [SKILL.md:342-350]()

## Temporary File Management

The YouTube Clipper Skill creates temporary files during processing to handle path compatibility issues and intermediate data.

### Temporary Directory Strategy

```mermaid
graph TB
    subgraph "Processing Workflow"
        Input["Input Files<br/>(may have spaces in path)"]
        TempCreate["Create temp directory<br/>(/tmp/youtube_clipper_*)"]
        TempCopy["Copy input files<br/>to temp location"]
        Process["Run FFmpeg<br/>(no path issues)"]
        MoveBack["Move output<br/>to final location"]
        Cleanup["Delete temp directory"]
    end
    
    Input --> TempCreate
    TempCreate --> TempCopy
    TempCopy --> Process
    Process --> MoveBack
    MoveBack --> Cleanup
```

**Sources:** [SKILL.md:284-291]()

### Why Temporary Files Are Needed

**Problem:** FFmpeg's subtitle filter (`subtitles=`) cannot correctly parse file paths containing spaces, even with proper quoting or escaping.

**Solution:** [scripts/burn_subtitles.py:1-200]() implements a temporary directory workaround:

1. Create a temporary directory without spaces: `/tmp/youtube_clipper_{random}/`
2. Copy input video and subtitle files to temporary location
3. Execute FFmpeg using space-free paths
4. Move the output file back to the target location
5. Clean up temporary directory

This approach ensures reliable subtitle burning regardless of the user's directory structure.

**Sources:** [SKILL.md:284-291]()

### Temporary File Configuration

The `KEEP_TEMP_FILES` environment variable controls temporary file retention:

- `KEEP_TEMP_FILES=false` (default): Temporary files deleted after processing
- `KEEP_TEMP_FILES=true`: Temporary files preserved for debugging

When debugging subtitle burning issues, setting `KEEP_TEMP_FILES=true` allows inspection of the intermediate files and FFmpeg command arguments.

**Sources:** [README.md:129-154]()

## Complete Output Example

Here is a complete example of the output directory structure after processing a video with all options enabled:

```
./youtube-clips/
└── 20260122_143022/
    ├── AGI_as_exponential_curve/
    │   ├── AGI_as_exponential_curve_clip.mp4            (14 MB)
    │   ├── AGI_as_exponential_curve_with_subtitles.mp4  (15 MB)
    │   ├── AGI_as_exponential_curve_bilingual.srt       (2.3 KB)
    │   └── AGI_as_exponential_curve_summary.md          (1.2 KB)
    │
    ├── Chinas_gap_in_AI_development/
    │   ├── Chinas_gap_in_AI_development_clip.mp4            (12 MB)
    │   ├── Chinas_gap_in_AI_development_with_subtitles.mp4  (13 MB)
    │   ├── Chinas_gap_in_AI_development_bilingual.srt       (1.8 KB)
    │   └── Chinas_gap_in_AI_development_summary.md          (980 B)
    │
    └── The_impact_of_chip_bans/
        ├── The_impact_of_chip_bans_clip.mp4            (16 MB)
        ├── The_impact_of_chip_bans_with_subtitles.mp4  (17 MB)
        ├── The_impact_of_chip_bans_bilingual.srt       (2.1 KB)
        └── The_impact_of_chip_bans_summary.md          (1.1 KB)
```

**Sources:** [README.md:112-123](), [SKILL.md:242-274]()

## File Organization Benefits

This hierarchical organization provides several advantages:

1. **Session Isolation:** Timestamped directories prevent conflicts between multiple processing runs
2. **Provenance:** Clear timestamp indicates when content was generated
3. **Logical Grouping:** All files for a chapter are contained in one directory
4. **Flexible Options:** Users can choose which file types to generate per chapter
5. **Easy Cleanup:** Delete entire session directories to remove old content
6. **Command-Line Friendly:** Sanitized names work well with shell commands and scripts

The structure balances organizational clarity with practical filesystem constraints, ensuring reliable operation across different platforms and directory configurations.

**Sources:** [README.md:112-123](), [SKILL.md:242-262]()

---

# Page: Core Scripts

# Core Scripts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [scripts/__init__.py](scripts/__init__.py)

</details>



This document provides an overview of the Python scripts in the `scripts/` directory that implement the YouTube Clipper Skill's core processing capabilities. Each script is a standalone executable module responsible for a specific phase of the video processing pipeline. For detailed information about the overall system architecture, see [Architecture](#3). For specific implementation details of each script, see their respective subsections ([4.1](#4.1)-[4.6](#4.6)).

---

## Script Inventory

The YouTube Clipper Skill consists of five primary processing scripts and one shared utilities module located in the `scripts/` directory:

| Script | Primary Responsibility | Input | Output | External Tools |
|--------|----------------------|-------|--------|----------------|
| `download_video.py` | Video and subtitle acquisition from YouTube | YouTube URL | `.mp4` video, `.vtt` subtitle | yt-dlp (CLI & library) |
| `analyze_subtitles.py` | Subtitle parsing and data preparation for AI | `.vtt` subtitle file | Structured subtitle data (JSON) | None |
| `clip_video.py` | Time-based video segment extraction | `.mp4` + start/end times | `.mp4` clip | FFmpeg |
| `burn_subtitles.py` | Hardcode subtitles into video | `.mp4` + `.srt` subtitle | `.mp4` with burned subtitles | FFmpeg (libass) |
| `extract_subtitle_clip.py` | Extract and adjust subtitle segments | `.srt/.vtt` + time range | `.srt` segment | pysrt |
| `utils.py` | Shared utility functions | N/A | N/A | N/A |

All scripts are designed to be invoked from the command line and follow a consistent pattern of reading configuration from `.env` files and writing structured output to stdout/stderr.

**Sources:** [README.md:1-320](), [SKILL.md:1-374](), [scripts/__init__.py:1-8]()

---

## Script Invocation Model

```mermaid
graph TB
    subgraph "Claude Code Environment"
        CC["Claude Code CLI"]
        Skill["SKILL.md Orchestration Logic"]
    end
    
    subgraph "scripts/ Directory"
        DV["download_video.py"]
        AS["analyze_subtitles.py"]
        CV["clip_video.py"]
        BS["burn_subtitles.py"]
        ESC["extract_subtitle_clip.py"]
        Utils["utils.py"]
    end
    
    subgraph "External Binaries"
        YtDlpCLI["yt-dlp CLI"]
        FFmpegBin["ffmpeg"]
    end
    
    subgraph "Python Libraries"
        YtDlpLib["yt_dlp module"]
        PySRT["pysrt module"]
        DotEnv["python-dotenv"]
    end
    
    CC -->|"User command"| Skill
    Skill -->|"python3 scripts/download_video.py URL"| DV
    Skill -->|"python3 scripts/analyze_subtitles.py FILE"| AS
    Skill -->|"python3 scripts/clip_video.py ARGS"| CV
    Skill -->|"python3 scripts/burn_subtitles.py ARGS"| BS
    Skill -->|"python3 scripts/extract_subtitle_clip.py ARGS"| ESC
    
    DV --> Utils
    DV --> YtDlpLib
    DV --> DotEnv
    AS --> Utils
    AS --> DotEnv
    CV --> Utils
    CV --> FFmpegBin
    BS --> Utils
    BS --> FFmpegBin
    ESC --> Utils
    ESC --> PySRT
    
    DV -.->|"Falls back to"| YtDlpCLI
```

**Description:** Scripts are invoked as separate Python processes by the SKILL.md orchestration logic running within Claude Code. Each script is a standalone executable module (`#!/usr/bin/env python3`) that can be run directly from the command line. The scripts share common functionality through `utils.py` and configuration through `.env` files loaded via `python-dotenv`.

**Sources:** [SKILL.md:21-279](), [README.md:42-46]()

---

## Processing Pipeline Data Flow

```mermaid
flowchart LR
    URL["YouTube URL"]
    
    subgraph "Phase 1: Download"
        DV["download_video.py"]
        VidFile["VIDEO_ID.mp4<br/>Max 1080p"]
        SubFile["VIDEO_ID.en.vtt<br/>English subtitles"]
    end
    
    subgraph "Phase 2: Analysis"
        AS["analyze_subtitles.py"]
        SubData["Structured subtitle data<br/>JSON to stdout"]
        AI["Claude AI Analysis<br/>(external to scripts)"]
        Chapters["Chapter definitions<br/>with timestamps"]
    end
    
    subgraph "Phase 3: Extraction"
        ESC["extract_subtitle_clip.py"]
        CV["clip_video.py"]
        ClipFile["CHAPTER_clip.mp4"]
        ClipSub["CHAPTER.srt<br/>Time-adjusted"]
    end
    
    subgraph "Phase 4: Enhancement"
        Trans["Translation<br/>(via Claude API)"]
        BiSub["CHAPTER_bilingual.srt<br/>EN + TARGET_LANGUAGE"]
        BS["burn_subtitles.py"]
        BurnedFile["CHAPTER_with_subtitles.mp4"]
    end
    
    URL --> DV
    DV --> VidFile
    DV --> SubFile
    
    SubFile --> AS
    AS --> SubData
    SubData --> AI
    AI --> Chapters
    
    VidFile --> CV
    Chapters --> CV
    Chapters --> ESC
    SubFile --> ESC
    
    CV --> ClipFile
    ESC --> ClipSub
    
    ClipSub --> Trans
    Trans --> BiSub
    
    ClipFile --> BS
    BiSub --> BS
    BS --> BurnedFile
```

**Description:** This diagram shows the actual data artifacts (file names and formats) produced and consumed by each script. The scripts operate in a sequential pipeline where output files from one script become input files for subsequent scripts. Video files maintain the `.mp4` container format throughout, while subtitle files transition from `.vtt` (download) to `.srt` (processing) format.

**Sources:** [SKILL.md:66-279](), [README.md:112-123]()

---

## Script Execution Characteristics

### Command-Line Interface

All scripts follow a consistent CLI pattern:

```bash
# Positional arguments pattern
python3 scripts/download_video.py <youtube_url>
python3 scripts/analyze_subtitles.py <subtitle_path>
python3 scripts/clip_video.py <video_path> <start_time> <end_time> <output_path>
python3 scripts/burn_subtitles.py <video_path> <subtitle_path> <output_path>
python3 scripts/extract_subtitle_clip.py <subtitle_path> <start_time> <end_time> <output_path>
```

Scripts accept arguments via `sys.argv` and are invoked from the `~/.claude/skills/youtube-clipper/` directory as specified in [SKILL.md:74-76]().

**Sources:** [SKILL.md:74-220]()

### Configuration Loading

All scripts load configuration from the `.env` file in the skill directory using the `python-dotenv` library. Configuration variables affect:

- File paths (`FFMPEG_PATH`, `OUTPUT_DIR`, `TEMP_DIR`)
- Processing parameters (`MAX_VIDEO_HEIGHT`, `TRANSLATION_BATCH_SIZE`)
- Subtitle styling (`SUBTITLE_FONT_SIZE`, `SUBTITLE_MARGIN_V`)
- Target language (`TARGET_LANGUAGE`)

The scripts implement a fallback pattern: `.env` values → hard-coded defaults. See [Configuration](#6) for full variable reference.

**Sources:** [README.md:129-154](), [SKILL.md:286-309]()

### Output and Logging

Scripts write structured output to stdout and stderr:

- **stdout**: Structured data (JSON, file paths) for consumption by Claude Code
- **stderr**: Progress information, warnings, and error messages
- **Exit codes**: 0 for success, non-zero for failures

This separation allows the orchestration logic in Claude Code to parse results while displaying human-readable progress to users.

**Sources:** [SKILL.md:80-89](), [README.md:105-110]()

---

## Dependency Relationships

```mermaid
graph TB
    subgraph "Core Scripts"
        DV["download_video.py"]
        AS["analyze_subtitles.py"]
        CV["clip_video.py"]
        BS["burn_subtitles.py"]
        ESC["extract_subtitle_clip.py"]
    end
    
    subgraph "Shared Module"
        Utils["utils.py<br/>• Time conversion<br/>• File sanitization<br/>• Validation<br/>• Format utilities"]
    end
    
    subgraph "Python Packages"
        YtDlp["yt_dlp"]
        PySRT["pysrt"]
        DotEnv["python-dotenv"]
    end
    
    subgraph "System Binaries"
        YtDlpBin["yt-dlp CLI"]
        FFmpeg["ffmpeg"]
    end
    
    subgraph "Configuration"
        Env[".env file"]
    end
    
    DV --> Utils
    DV --> YtDlp
    DV --> DotEnv
    DV -.->|fallback| YtDlpBin
    
    AS --> Utils
    AS --> DotEnv
    
    CV --> Utils
    CV --> FFmpeg
    
    BS --> Utils
    BS --> FFmpeg
    
    ESC --> Utils
    ESC --> PySRT
    
    DV --> Env
    AS --> Env
    CV --> Env
    BS --> Env
    ESC --> Env
```

**Description:** The `utils.py` module serves as the central shared dependency, providing common functionality used by all processing scripts. External dependencies are partitioned into Python packages (imported as modules) and system binaries (invoked via subprocess). The `.env` configuration file is read by all scripts through the `python-dotenv` library.

**Sources:** [README.md:50-66](), [SKILL.md:46-50]()

---

## Shared Utilities Module

The `utils.py` module provides cross-cutting functionality used by multiple scripts:

| Function Category | Purpose | Used By |
|-------------------|---------|---------|
| Time conversion | Parse and format timestamps (`MM:SS`, `HH:MM:SS` ↔ seconds) | All scripts with time parameters |
| File management | Path sanitization, directory creation, file validation | All scripts |
| Filename sanitization | Remove special characters (`/ \ : * ? " < > \|`), limit length | Scripts generating output files |
| Format utilities | VTT ↔ SRT conversion, encoding detection | `analyze_subtitles.py`, `extract_subtitle_clip.py` |
| Validation | Check file existence, verify tools availability | All scripts |

For detailed documentation of utility functions, see [Utilities Module](#4.6).

**Sources:** [README.md:271-277](), [SKILL.md:340-350]()

---

## Error Handling Patterns

Scripts implement consistent error handling across three categories:

### Environment Errors

Scripts verify prerequisites before execution:

```bash
# Example: FFmpeg libass detection
ffmpeg -filters 2>&1 | grep subtitles
```

If tools are missing, scripts exit with non-zero status and emit installation instructions to stderr.

**Sources:** [SKILL.md:26-63](), [README.md:50-84]()

### Processing Errors

- **Download failures**: Retry with exponential backoff, fallback to auto-generated subtitles
- **FFmpeg failures**: Display full error output, suggest common fixes (path spaces, libass)
- **Translation failures**: Retry up to 3 times, reduce batch size on persistent failures

**Sources:** [SKILL.md:322-337](), [README.md:236-278]()

### File Path Issues

Special handling for paths containing spaces or special characters:

- `burn_subtitles.py` implements temporary directory workaround for FFmpeg subtitle filter path parsing limitations
- All scripts sanitize output filenames by removing `/ \ : * ? " < > |` and replacing spaces with underscores

**Sources:** [SKILL.md:286-291](), [README.md:271-277]()

---

## Script Integration Points

```mermaid
graph LR
    subgraph "Input Layer"
        YouTube["YouTube Platform"]
        UserInput["User Selections"]
    end
    
    subgraph "Core Scripts"
        direction TB
        DV["download_video.py"]
        AS["analyze_subtitles.py"]
        CV["clip_video.py"]
        ESC["extract_subtitle_clip.py"]
        BS["burn_subtitles.py"]
    end
    
    subgraph "AI Layer"
        ClaudeAPI["Claude AI API<br/>(external to scripts)"]
    end
    
    subgraph "Output Layer"
        Files["./youtube-clips/<br/>Organized output"]
    end
    
    YouTube --> DV
    DV -->|".vtt file"| AS
    AS -->|"JSON data"| ClaudeAPI
    ClaudeAPI -->|"Chapter specs"| UserInput
    
    UserInput -->|"Selected chapters"| CV
    UserInput -->|"Selected chapters"| ESC
    
    CV --> Files
    ESC -->|".srt file"| ClaudeAPI
    ClaudeAPI -->|"Translations"| BS
    BS --> Files
```

**Description:** Scripts interface with three external systems: YouTube (via `download_video.py`), Claude AI API (for analysis and translation, invoked by SKILL.md logic), and the user (via Claude Code interface). The scripts themselves do not directly call the Claude API; instead, they prepare data structures that the SKILL.md orchestration logic passes to Claude and consume the results.

**Sources:** [SKILL.md:96-144](), [SKILL.md:183-194]()

---

## Script Execution Context

### Working Directory

All scripts are invoked from `~/.claude/skills/youtube-clipper/` as specified in [SKILL.md:75](). This ensures:

- Relative imports work correctly (`from utils import ...`)
- Configuration file (`.env`) is found at a predictable location
- Output paths are relative to the skill directory unless overridden by `OUTPUT_DIR`

**Sources:** [SKILL.md:74-77](), [README.md:32-46]()

### Environment Detection

Before processing begins, scripts verify the execution environment:

1. **Python version check**: Require Python 3.8+ for `yt_dlp` library compatibility
2. **Binary availability**: Test `yt-dlp --version` and `ffmpeg -version`
3. **Library imports**: Attempt to `import yt_dlp`, `import pysrt`
4. **FFmpeg capabilities**: Check for libass support via `ffmpeg -filters | grep subtitles`

Failures at this stage prevent processing from starting and emit actionable error messages.

**Sources:** [SKILL.md:25-63](), [README.md:50-84]()

---

## Performance Characteristics

| Script | Bottleneck | Typical Duration | Optimization Strategy |
|--------|------------|------------------|----------------------|
| `download_video.py` | Network I/O | 30s-5min (depends on video length) | Resume support, proxy configuration |
| `analyze_subtitles.py` | File parsing | <1s | Minimal; parsing is fast |
| `clip_video.py` | FFmpeg encoding | 5-30s per clip | Stream copy (no re-encoding) |
| `burn_subtitles.py` | FFmpeg rendering | 30s-2min per clip | Hardware acceleration (when available) |
| `extract_subtitle_clip.py` | File I/O | <1s | In-memory processing |

The `download_video.py` and `burn_subtitles.py` scripts are the primary bottlenecks. Download speed can be improved via proxy configuration (`YT_DLP_PROXY`). Subtitle burning performance depends on FFmpeg hardware acceleration support.

**Sources:** [SKILL.md:164-235](), [README.md:253-260]()

---

## File Format Conversions

Scripts perform several format conversions during processing:

| Conversion | Performed By | Reason |
|------------|--------------|--------|
| VTT → JSON | `analyze_subtitles.py` | Structure data for AI analysis |
| VTT → SRT | `extract_subtitle_clip.py` | SRT is simpler format for FFmpeg |
| Single-language SRT → Bilingual SRT | (External translation logic) | Combine English + target language |
| SRT → Hardcoded video | `burn_subtitles.py` | Embed subtitles permanently |

VTT (Web Video Text Tracks) is YouTube's native subtitle format, while SRT (SubRip) is more widely supported by video processing tools. All conversions preserve timestamp precision and handle encoding properly (UTF-8).

**Sources:** [SKILL.md:101-110](), [README.md:219-233]()

---

## Next Steps

For detailed information about each script's implementation:

- [download_video.py](#4.1) - yt-dlp integration and video acquisition
- [analyze_subtitles.py](#4.2) - VTT parsing and data preparation  
- [clip_video.py](#4.3) - FFmpeg video extraction
- [burn_subtitles.py](#4.4) - Subtitle rendering with libass
- [extract_subtitle_clip.py](#4.5) - Subtitle segment extraction
- [Utilities Module](#4.6) - Shared helper functions

For configuration options that affect script behavior, see [Configuration](#6).

**Sources:** [README.md:1-320](), [SKILL.md:1-374]()

---

# Page: download_video.py

# download_video.py

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/yt-dlp-guide.md](references/yt-dlp-guide.md)
- [scripts/download_video.py](scripts/download_video.py)

</details>



## Purpose and Scope

The `download_video.py` script is responsible for downloading YouTube videos and their English subtitles using the yt-dlp library. This script implements the **Phase 2: Video Download** stage of the processing pipeline, handling video format selection, quality limits (1080p maximum), subtitle extraction, and download progress monitoring.

For information about analyzing downloaded subtitles, see [analyze_subtitles.py](#4.2). For information about yt-dlp command-line usage and configuration details, see [yt-dlp Integration](#5.1).

**Sources:** [scripts/download_video.py:1-211]()

---

## Module Overview

### Entry Point and Dependencies

The script requires the `yt_dlp` Python package and imports utility functions from the shared `utils` module. If yt-dlp is not installed, the script exits with a clear error message directing the user to install it.

```mermaid
graph TB
    MainFunc["main()<br/>CLI Entry Point"]
    DownloadFunc["download_video()<br/>Core Function"]
    ProgressHook["_progress_hook()<br/>Callback"]
    
    subgraph "External Dependencies"
        YtDlp["yt_dlp<br/>YouTube Downloader"]
        Utils["utils module<br/>validate_url()<br/>sanitize_filename()<br/>format_file_size()<br/>get_video_duration_display()<br/>ensure_directory()"]
    end
    
    subgraph "System Libraries"
        SysLib["sys, json, pathlib"]
    end
    
    MainFunc --> DownloadFunc
    DownloadFunc --> YtDlp
    DownloadFunc --> Utils
    DownloadFunc --> ProgressHook
    ProgressHook --> Utils
    
    MainFunc --> SysLib
    DownloadFunc --> SysLib
```

**Diagram: Module Dependency Structure for download_video.py**

**Sources:** [scripts/download_video.py:1-24]()

---

## Core Function: download_video()

### Function Signature and Parameters

```python
def download_video(url: str, output_dir: str = None) -> dict
```

The `download_video()` function is the primary interface for downloading videos. It accepts a YouTube URL and optional output directory, returning a dictionary with download results.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | str | Required | YouTube video URL |
| `output_dir` | str | None | Output directory path (defaults to current directory) |

**Return Value Structure:**
```python
{
    'video_path': str,      # Absolute path to downloaded video
    'subtitle_path': str,   # Absolute path to subtitle file (or None)
    'title': str,           # Video title from metadata
    'duration': int,        # Video duration in seconds
    'file_size': int,       # Video file size in bytes
    'video_id': str         # YouTube video ID
}
```

**Sources:** [scripts/download_video.py:27-47]()

---

### Processing Flow

```mermaid
flowchart TD
    Start["download_video() called"]
    
    Validate["validate_url(url)<br/>Check URL format"]
    SetupDir["ensure_directory()<br/>Create output directory"]
    ConfigOpts["Configure ydl_opts<br/>Format, subtitles, output template"]
    
    ExtractInfo["ydl.extract_info()<br/>download=False<br/>Retrieve metadata"]
    DisplayInfo["Display title, duration,<br/>video_id to console"]
    
    DownloadVideo["ydl.extract_info()<br/>download=True<br/>Download video + subtitles"]
    
    GetPaths["ydl.prepare_filename()<br/>Get video_path"]
    FindSubs["Search for subtitle files:<br/>.en.vtt, .vtt"]
    
    GetSize["video_path.stat().st_size<br/>Get file size"]
    
    CheckExists{"video_path.exists()"}
    
    ReturnDict["Return result dict:<br/>video_path, subtitle_path,<br/>title, duration, file_size"]
    
    RaiseError["Raise Exception:<br/>'Video file not found'"]
    
    Start --> Validate
    Validate --> SetupDir
    SetupDir --> ConfigOpts
    ConfigOpts --> ExtractInfo
    ExtractInfo --> DisplayInfo
    DisplayInfo --> DownloadVideo
    DownloadVideo --> GetPaths
    GetPaths --> FindSubs
    FindSubs --> GetSize
    GetSize --> CheckExists
    CheckExists -->|True| ReturnDict
    CheckExists -->|False| RaiseError
```

**Diagram: Execution Flow of download_video() Function**

**Sources:** [scripts/download_video.py:48-153]()

---

## yt-dlp Configuration

### ydl_opts Dictionary Structure

The `ydl_opts` dictionary configures yt-dlp behavior. This configuration is defined at [scripts/download_video.py:65-87]().

```mermaid
graph LR
    subgraph "Video Format Selection"
        Format["format:<br/>'bestvideo[height<=1080][ext=mp4]<br/>+bestaudio[ext=m4a]<br/>/best[height<=1080][ext=mp4]<br/>/best'"]
    end
    
    subgraph "Output Configuration"
        Template["outtmpl:<br/>'%(id)s.%(ext)s'"]
        Thumbnail["writethumbnail: False"]
    end
    
    subgraph "Subtitle Settings"
        WriteSub["writesubtitles: True"]
        AutoSub["writeautomaticsub: True"]
        SubLang["subtitleslangs: ['en']"]
        SubFormat["subtitlesformat: 'vtt'"]
    end
    
    subgraph "Progress Monitoring"
        ProgressHook["progress_hooks:<br/>[_progress_hook]"]
    end
    
    Format --> YtDlp["yt_dlp.YoutubeDL"]
    Template --> YtDlp
    Thumbnail --> YtDlp
    WriteSub --> YtDlp
    AutoSub --> YtDlp
    SubLang --> YtDlp
    SubFormat --> YtDlp
    ProgressHook --> YtDlp
```

**Diagram: yt-dlp Configuration Options in ydl_opts**

**Sources:** [scripts/download_video.py:64-87]()

---

### Format Selection Logic

The `format` string implements a fallback chain to ensure successful downloads across different video types:

| Priority | Format String | Description |
|----------|---------------|-------------|
| 1 | `bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]` | Best video ≤1080p (mp4) + best audio (m4a), merged |
| 2 | `best[height<=1080][ext=mp4]` | Best combined stream ≤1080p (mp4) |
| 3 | `best` | Any best available format |

**Rationale for 1080p Limit:**
- File size management (4K videos can exceed 5-10GB)
- Processing performance (FFmpeg operations are faster on smaller files)
- Target platforms (short-form video platforms primarily use 1080p or lower)
- Storage efficiency

**Sources:** [scripts/download_video.py:66-67](), [TECHNICAL_NOTES.md:98-104](), [references/yt-dlp-guide.md:98-104]()

---

### Output Template and File Naming

The `outtmpl` value is set to `'%(id)s.%(ext)s'` at [scripts/download_video.py:70](), which results in files named by their YouTube video ID:

```
Video:    Ckt1cj0xjRM.mp4
Subtitle: Ckt1cj0xjRM.en.vtt
```

This naming strategy avoids issues with:
- Special characters in video titles
- Filesystem path length limits
- File name collisions
- Non-ASCII characters

The video ID ensures uniqueness and provides traceability to the source video.

**Sources:** [scripts/download_video.py:70](), [TECHNICAL_NOTES.md:340-353]()

---

## Subtitle Handling

### Subtitle Download Configuration

The script requests English subtitles in VTT format with automatic fallback:

```python
'writesubtitles': True,        # Request manual subtitles
'writeautomaticsub': True,     # Fallback to auto-generated
'subtitleslangs': ['en'],      # English only
'subtitlesformat': 'vtt',      # WebVTT format
```

**Priority Order:**
1. Manual/human-created English subtitles (if available)
2. Auto-generated English subtitles (YouTube's automatic captions)

**Sources:** [scripts/download_video.py:72-76]()

---

### Subtitle File Detection

After download, the script searches for subtitle files using multiple patterns at [scripts/download_video.py:112-124]():

```mermaid
flowchart TD
    Start["After ydl.extract_info()"]
    
    InitSearch["subtitle_path = None<br/>subtitle_exts = ['.en.vtt', '.vtt']"]
    
    Loop["For each ext in subtitle_exts"]
    
    CheckDirect["potential_sub =<br/>video_path.with_suffix(ext)"]
    DirectExists{"potential_sub.exists()"}
    
    CheckAlt["stem = video_path.stem<br/>potential_sub =<br/>video_path.parent / f'{stem}.en.vtt'"]
    AltExists{"potential_sub.exists()"}
    
    SetPath["subtitle_path = potential_sub<br/>break"]
    
    Continue["Continue to next ext"]
    
    Done["subtitle_path is set or None"]
    
    Start --> InitSearch
    InitSearch --> Loop
    Loop --> CheckDirect
    CheckDirect --> DirectExists
    DirectExists -->|Yes| SetPath
    DirectExists -->|No| CheckAlt
    CheckAlt --> AltExists
    AltExists -->|Yes| SetPath
    AltExists -->|No| Continue
    Continue --> Loop
    SetPath --> Done
```

**Diagram: Subtitle File Detection Logic**

**File Pattern Examples:**
- `Ckt1cj0xjRM.en.vtt` (language-specific)
- `Ckt1cj0xjRM.vtt` (generic)

**Sources:** [scripts/download_video.py:112-124]()

---

## Progress Monitoring

### _progress_hook() Callback

The `_progress_hook()` function at [scripts/download_video.py:156-182]() is registered in `ydl_opts['progress_hooks']` and receives download status updates from yt-dlp.

**Callback Status Types:**

| Status | Information Available | Display Behavior |
|--------|----------------------|------------------|
| `downloading` | `downloaded_bytes`, `total_bytes`, `speed` | Progress bar with percentage, data transferred, and speed |
| `downloading` (no total) | `downloaded_bytes`, `speed` | Simple progress counter with speed |
| `finished` | None | Print newline to complete progress display |

**Progress Bar Rendering:**

```python
bar_length = 30
filled = int(bar_length * percent / 100)
bar = '█' * filled + '░' * (bar_length - filled)
```

Example output:
```
   [████████████░░░░░░░░░░░░░░░░] 42.3% - 15.2 MB/36.0 MB - 2.1 MB/s
```

The progress display uses `\r` (carriage return) to overwrite the same line, creating an animated progress bar effect.

**Sources:** [scripts/download_video.py:156-182]()

---

## Error Handling

### Validation and Exceptions

```mermaid
graph TD
    ValidateURL{"validate_url(url)"}
    RaiseValueError["Raise ValueError:<br/>'Invalid YouTube URL'"]
    
    ExtractInfo["yt_dlp.YoutubeDL.<br/>extract_info()"]
    
    CatchException["except Exception as e"]
    PrintError["Print error message:<br/>'下载失败'"]
    RaiseException["Raise exception"]
    
    CheckFile{"video_path.exists()"}
    RaiseNotFound["Raise Exception:<br/>'Video file not found<br/>after download'"]
    
    Success["Return result dict"]
    
    ValidateURL -->|False| RaiseValueError
    ValidateURL -->|True| ExtractInfo
    ExtractInfo --> CheckFile
    CheckFile -->|False| RaiseNotFound
    CheckFile -->|True| Success
    
    ExtractInfo -.->|Error| CatchException
    CatchException --> PrintError
    PrintError --> RaiseException
```

**Diagram: Error Handling Flow in download_video()**

**Exception Types:**
- `ValueError`: Invalid URL format (raised by `validate_url()`)
- `Exception`: yt-dlp download failures (network errors, unavailable video, etc.)
- `Exception`: Missing video file after download (filesystem issue)

**Sources:** [scripts/download_video.py:49-50](), [scripts/download_video.py:130-132](), [scripts/download_video.py:151-153]()

---

## Command-Line Interface

### main() Function

The `main()` function at [scripts/download_video.py:184-210]() provides a command-line interface for standalone script execution.

**Usage Patterns:**

```bash
# Basic usage (downloads to current directory)
python download_video.py https://youtube.com/watch?v=Ckt1cj0xjRM

# Specify output directory
python download_video.py https://youtube.com/watch?v=Ckt1cj0xjRM ~/Downloads
```

**Argument Processing:**

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| URL | `sys.argv[1]` | Yes | YouTube video URL |
| Output directory | `sys.argv[2]` | No | Target directory for downloaded files |

**Output Format:**

After successful download, the script prints a JSON summary:

```json
{
  "video_path": "/path/to/Ckt1cj0xjRM.mp4",
  "subtitle_path": "/path/to/Ckt1cj0xjRM.en.vtt",
  "title": "Anthropic's Amodei on AI",
  "duration": 1543,
  "file_size": 145728432,
  "video_id": "Ckt1cj0xjRM"
}
```

This JSON output enables integration with other scripts in the processing pipeline.

**Sources:** [scripts/download_video.py:184-210]()

---

## Integration with Utilities Module

### Utility Function Usage

The script leverages shared utilities from `utils.py` (see [Utilities Module](#4.6) for details):

```mermaid
graph LR
    subgraph "download_video.py Functions"
        DownloadFunc["download_video()"]
        ProgressFunc["_progress_hook()"]
    end
    
    subgraph "utils.py Functions"
        ValidateURL["validate_url(url)<br/>Check YouTube URL format"]
        SanitizeFile["sanitize_filename(name)<br/>Clean special characters"]
        FormatSize["format_file_size(bytes)<br/>Human-readable size"]
        GetDuration["get_video_duration_display(secs)<br/>Format HH:MM:SS"]
        EnsureDir["ensure_directory(path)<br/>Create if missing"]
    end
    
    DownloadFunc --> ValidateURL
    DownloadFunc --> SanitizeFile
    DownloadFunc --> FormatSize
    DownloadFunc --> GetDuration
    DownloadFunc --> EnsureDir
    
    ProgressFunc --> FormatSize
```

**Diagram: Utility Function Dependencies in download_video.py**

**Function Call Locations:**
- `validate_url()`: [scripts/download_video.py:49]()
- `ensure_directory()`: [scripts/download_video.py:58]()
- `get_video_duration_display()`: [scripts/download_video.py:100]()
- `format_file_size()`: [scripts/download_video.py:134](), [scripts/download_video.py:162-163](), [scripts/download_video.py:165](), [scripts/download_video.py:177]()

**Sources:** [scripts/download_video.py:18-24]()

---

## Output Files and Structure

### Generated Files

For a given YouTube video with ID `Ckt1cj0xjRM`, the download operation produces:

| File | Pattern | Purpose |
|------|---------|---------|
| Video | `Ckt1cj0xjRM.mp4` | Downloaded video file (≤1080p) |
| Subtitle | `Ckt1cj0xjRM.en.vtt` | English subtitles in WebVTT format |

**File Location:**
Both files are placed in the directory specified by `output_dir` parameter, or the current working directory if not specified.

**Storage Characteristics:**
- Video files typically range from 50MB (short videos) to 500MB+ (longer 1080p content)
- VTT subtitle files are text-based, typically <1MB
- File naming by video ID prevents conflicts when downloading multiple videos

**Sources:** [scripts/download_video.py:70](), [scripts/download_video.py:108-124]()

---

## Console Output Format

### Download Progress Display

The script provides structured console output with clear visual indicators:

**Phase 1: Information Retrieval**
```
🎬 开始下载视频...
   URL: https://youtube.com/watch?v=Ckt1cj0xjRM
   输出目录: /Users/username/videos

📊 获取视频信息...
   标题: Anthropic's Amodei on AI
   时长: 25:43
   视频ID: Ckt1cj0xjRM
```

**Phase 2: Download Progress**
```
📥 开始下载...
   [██████████████████████░░░░░░░] 75.3% - 108.5 MB/144.2 MB - 3.2 MB/s
```

**Phase 3: Completion**
```
✅ 视频下载完成: Ckt1cj0xjRM.mp4
   大小: 144.2 MB
✅ 字幕下载完成: Ckt1cj0xjRM.en.vtt
```

**Emoji Legend:**
- 🎬 Download initialization
- 📊 Metadata extraction
- 📥 Active download
- ✅ Success
- ⚠️ Warning (e.g., missing subtitles)
- ❌ Error

**Sources:** [scripts/download_video.py:60-153]()

---

## Common Usage Patterns

### Standalone Script Execution

```bash
# Download to current directory
python scripts/download_video.py "https://youtube.com/watch?v=VIDEO_ID"

# Download to specific directory
python scripts/download_video.py "https://youtube.com/watch?v=VIDEO_ID" ./downloads
```

### Programmatic API Usage

```python
from scripts.download_video import download_video

result = download_video(
    url="https://youtube.com/watch?v=Ckt1cj0xjRM",
    output_dir="/path/to/output"
)

video_path = result['video_path']
subtitle_path = result['subtitle_path']
duration = result['duration']
```

### Integration with Pipeline

The script is typically invoked as the first stage of the processing pipeline:

1. **download_video.py** → Downloads video and subtitles
2. [analyze_subtitles.py](#4.2) → Analyzes subtitle content for chapters
3. [clip_video.py](#4.3) → Extracts chapter segments
4. [extract_subtitle_clip.py](#4.5) → Extracts subtitle segments
5. [burn_subtitles.py](#4.4) → Burns subtitles into video

**Sources:** [scripts/download_video.py:27-153]()

---

# Page: analyze_subtitles.py

# analyze_subtitles.py

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [scripts/analyze_subtitles.py](scripts/analyze_subtitles.py)

</details>



## Purpose and Scope

This document describes the `analyze_subtitles.py` script, which is responsible for parsing VTT subtitle files downloaded from YouTube and preparing structured data for AI semantic analysis. This script serves as the bridge between raw subtitle data and Claude AI's chapter generation capabilities.

For information about the video download process that produces the VTT files, see [download_video.py](#4.1). For details on how Claude AI uses the prepared data to generate chapters, see [AI Semantic Analysis](#7.2).

**Sources:** [scripts/analyze_subtitles.py:1-252]()

---

## Overview

The `analyze_subtitles.py` script performs two primary functions:

1. **VTT Parsing**: Reads WebVTT subtitle files and extracts timestamps and text into a structured format
2. **Data Preparation**: Formats the parsed subtitles into a text representation that Claude AI can analyze to identify semantic boundaries and generate meaningful chapters

The script does **not** perform the actual AI analysis; it only prepares the data. The actual chapter generation is performed by Claude Code reading the prepared subtitle text and applying semantic understanding.

**Sources:** [scripts/analyze_subtitles.py:1-5](), [SKILL.md:96-145]()

---

## Input/Output Specifications

### Input

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `vtt_file` | File path | VTT subtitle file from YouTube download | Required |
| `target_duration` | Integer | Target chapter duration in seconds | 180 (3 min) |
| `output_json` | File path | Optional JSON output file for analysis data | None |

### Output

The script produces two types of output:

1. **Console Output**: Formatted subtitle text with timestamps for AI analysis
2. **JSON File** (optional): Structured analysis data including:
   - `subtitle_text`: Full timestamped subtitle content
   - `total_duration`: Video duration in seconds
   - `subtitle_count`: Number of subtitle entries
   - `target_chapter_duration`: Target chapter length
   - `estimated_chapters`: Calculated chapter estimate
   - `subtitles_raw`: Original parsed subtitle array

**Sources:** [scripts/analyze_subtitles.py:186-248]()

---

## Architecture and Data Flow

```mermaid
flowchart TB
    Input["VTT File<br/>(YouTube subtitle)"]
    
    subgraph "analyze_subtitles.py"
        ParseVTT["parse_vtt()<br/>Line 20-114"]
        PrepareData["prepare_analysis_data()<br/>Line 117-163"]
        SaveData["save_analysis_data()<br/>Line 166-183"]
        Main["main()<br/>Line 186-248"]
        
        Main --> ParseVTT
        ParseVTT --> PrepareData
        PrepareData --> SaveData
    end
    
    subgraph "Utilities"
        TimeUtils["time_to_seconds()<br/>seconds_to_time()<br/>from utils.py"]
    end
    
    subgraph "Outputs"
        Console["Console Output<br/>Timestamped subtitle text"]
        JSONFile["JSON File<br/>Structured analysis data"]
    end
    
    subgraph "Next Phase"
        ClaudeAI["Claude AI<br/>Semantic Chapter Analysis"]
    end
    
    Input --> ParseVTT
    ParseVTT --> TimeUtils
    PrepareData --> TimeUtils
    
    PrepareData --> Console
    SaveData --> JSONFile
    
    Console --> ClaudeAI
    JSONFile --> ClaudeAI
    
    style ParseVTT fill:#f9f9f9
    style PrepareData fill:#f9f9f9
```

**Sources:** [scripts/analyze_subtitles.py:1-252](), [scripts/utils.py]()

---

## Core Functions

### parse_vtt()

Parses WebVTT subtitle files into structured Python dictionaries.

**Function Signature:**
```python
def parse_vtt(vtt_path: str) -> List[Dict]
```

**Processing Steps:**

1. **Header Removal**: Strips WEBVTT header and STYLE blocks using regex
2. **Block Splitting**: Separates subtitle entries by double newlines
3. **Timestamp Extraction**: Parses `HH:MM:SS.mmm --> HH:MM:SS.mmm` format
4. **Text Cleaning**: Removes HTML tags and special characters
5. **Time Conversion**: Converts timestamp strings to seconds using `time_to_seconds()`

**VTT Parsing Logic:**

```mermaid
flowchart LR
    VTTFile["VTT File Content"]
    RemoveHeader["Remove WEBVTT Header<br/>& STYLE blocks<br/>Line 50-51"]
    SplitBlocks["Split by double newline<br/>Line 54"]
    
    subgraph "For Each Block"
        FindTimestamp["Find timestamp line<br/>(contains '-->')<br/>Line 68-69"]
        ExtractText["Extract text lines<br/>(skip digits)<br/>Line 70-71"]
        ParseTime["Parse start/end times<br/>time_to_seconds()<br/>Line 85-86"]
        CleanText["Remove HTML tags<br/>& special chars<br/>Line 92-95"]
        AppendSub["Append to subtitles list<br/>Line 98-102"]
    end
    
    Result["List[Dict]<br/>{start, end, text}"]
    
    VTTFile --> RemoveHeader
    RemoveHeader --> SplitBlocks
    SplitBlocks --> FindTimestamp
    FindTimestamp --> ExtractText
    ExtractText --> ParseTime
    ParseTime --> CleanText
    CleanText --> AppendSub
    AppendSub --> Result
```

**Data Structure Output:**
```python
[
    {'start': 0.0, 'end': 3.5, 'text': 'Hello world'},
    {'start': 3.5, 'end': 7.2, 'text': 'This is a test'},
    ...
]
```

**Error Handling**: The function uses try-except blocks to skip malformed subtitle entries rather than failing the entire parse operation [scripts/analyze_subtitles.py:104-106]().

**Sources:** [scripts/analyze_subtitles.py:20-114]()

---

### prepare_analysis_data()

Formats parsed subtitles into a timestamped text representation for AI consumption.

**Function Signature:**
```python
def prepare_analysis_data(subtitles: List[Dict], target_chapter_duration: int = 180) -> Dict
```

**Key Operations:**

1. **Text Formatting**: Converts each subtitle to `[HH:MM:SS] text` format
2. **Duration Calculation**: Extracts total duration from last subtitle's end time
3. **Chapter Estimation**: Calculates `estimated_chapters = total_duration / target_duration`

**Chapter Estimation Algorithm:**

| Total Duration | Target Duration (180s) | Estimated Chapters |
|----------------|------------------------|-------------------|
| 900s (15 min) | 180s (3 min) | 5 chapters |
| 1800s (30 min) | 180s (3 min) | 10 chapters |
| 3600s (60 min) | 180s (3 min) | 20 chapters |

Formula: `max(1, int(total_duration / target_chapter_duration))`

**Output Format Example:**
```
[00:00:00] Welcome to this video
[00:00:03] Today we'll discuss AI development
[00:00:07] Let's start with the basics
...
```

**Sources:** [scripts/analyze_subtitles.py:117-163]()

---

### save_analysis_data()

Serializes analysis data to JSON format for persistence or further processing.

**Function Signature:**
```python
def save_analysis_data(data: Dict, output_path: str)
```

**Features:**
- Creates parent directories if they don't exist
- Saves with UTF-8 encoding and proper indentation
- Uses `ensure_ascii=False` to preserve Unicode characters (important for Chinese text)

**Sources:** [scripts/analyze_subtitles.py:166-183]()

---

## Data Structures

### Subtitle Entry Format

Each parsed subtitle is represented as:

```python
{
    'start': float,    # Start time in seconds (e.g., 0.0)
    'end': float,      # End time in seconds (e.g., 3.5)
    'text': str        # Cleaned subtitle text
}
```

### Analysis Data Format

The complete analysis data structure:

```python
{
    'subtitle_text': str,              # Full timestamped text for AI
    'total_duration': float,           # Total video duration (seconds)
    'subtitle_count': int,             # Number of subtitle entries
    'target_chapter_duration': int,    # Target chapter length (seconds)
    'estimated_chapters': int,         # Calculated chapter estimate
    'subtitles_raw': List[Dict]        # Original parsed subtitles
}
```

**Sources:** [scripts/analyze_subtitles.py:117-163]()

---

## Integration with System Components

```mermaid
flowchart TB
    subgraph "Phase 2: Download"
        DownloadVideo["download_video.py"]
        VTTFile["video_id.en.vtt"]
    end
    
    subgraph "Phase 3: Analysis (This Script)"
        AnalyzeSubtitles["analyze_subtitles.py"]
        ParseVTT["parse_vtt()"]
        PrepareData["prepare_analysis_data()"]
        
        AnalyzeSubtitles --> ParseVTT
        ParseVTT --> PrepareData
    end
    
    subgraph "Utilities"
        Utils["utils.py<br/>time_to_seconds()<br/>seconds_to_time()<br/>get_video_duration_display()"]
    end
    
    subgraph "Phase 3: AI Processing"
        ClaudeCode["Claude Code<br/>Reads subtitle_text"]
        SemanticAnalysis["Semantic Chapter Generation<br/>Topic boundaries<br/>Titles & summaries"]
    end
    
    subgraph "Configuration"
        EnvFile[".env<br/>TARGET_CHAPTER_DURATION"]
    end
    
    DownloadVideo --> VTTFile
    VTTFile --> AnalyzeSubtitles
    
    ParseVTT -.-> Utils
    PrepareData -.-> Utils
    
    EnvFile -.-> PrepareData
    
    PrepareData --> ClaudeCode
    ClaudeCode --> SemanticAnalysis
    
    style AnalyzeSubtitles fill:#f9f9f9
```

**Sources:** [scripts/analyze_subtitles.py:1-252](), [SKILL.md:96-145](), [scripts/utils.py]()

---

## Command-Line Interface

### Usage Patterns

**Basic Usage:**
```bash
python3 scripts/analyze_subtitles.py video.en.vtt
```

**With Custom Chapter Duration:**
```bash
python3 scripts/analyze_subtitles.py video.en.vtt 240
```

**With JSON Output:**
```bash
python3 scripts/analyze_subtitles.py video.en.vtt 240 analysis.json
```

### Arguments

| Position | Argument | Type | Description | Default |
|----------|----------|------|-------------|---------|
| 1 | `vtt_file` | String | Path to VTT subtitle file | Required |
| 2 | `target_duration` | Integer | Target chapter duration (seconds) | 180 |
| 3 | `output_json` | String | Output JSON file path | None |

### Output Format

The script prints structured output to console:

1. **Parsing Progress**: File name and subtitle count
2. **Preview**: First 50 lines of timestamped text
3. **Summary Statistics**: JSON-formatted metadata

**Sources:** [scripts/analyze_subtitles.py:186-248]()

---

## Regular Expressions and Text Processing

The script uses several regex patterns for VTT parsing:

| Pattern | Purpose | Location |
|---------|---------|----------|
| `r'^WEBVTT.*?\n\n'` | Remove WEBVTT header | Line 50 |
| `r'STYLE.*?-->'` | Remove STYLE blocks | Line 51 |
| `r'align:.*\|position:.*'` | Strip position metadata | Line 79 |
| `r'<[^>]+>'` | Remove HTML tags | Line 92 |

### VTT Format Handling

VTT files may contain various metadata that must be stripped:

```
WEBVTT
Kind: captions
Language: en

STYLE
::cue {
  background-color: transparent;
}

00:00:00.000 --> 00:00:03.500 align:start position:0%
Welcome to this video
```

The parser removes all metadata and extracts only timestamps and text.

**Sources:** [scripts/analyze_subtitles.py:49-95]()

---

## Time Conversion and Utilities

The script relies heavily on utility functions from `utils.py`:

### Time Conversion Functions

```mermaid
flowchart LR
    VTTTimestamp["VTT Timestamp<br/>'00:03:45.500'"]
    TimeToSeconds["time_to_seconds()"]
    Seconds["Float<br/>225.5"]
    SecondsToTime["seconds_to_time()"]
    FormattedTime["Formatted String<br/>'[00:03:45]'"]
    
    VTTTimestamp --> TimeToSeconds
    TimeToSeconds --> Seconds
    Seconds --> SecondsToTime
    SecondsToTime --> FormattedTime
```

**Function Usage:**

- `time_to_seconds(time_str)`: Converts VTT timestamps to float seconds [scripts/analyze_subtitles.py:85-86]()
- `seconds_to_time(seconds)`: Converts seconds back to formatted time strings [scripts/analyze_subtitles.py:143]()
- `get_video_duration_display(seconds)`: Formats duration for display [scripts/analyze_subtitles.py:112]()

**Sources:** [scripts/analyze_subtitles.py:13-17](), [scripts/utils.py]()

---

## Error Handling and Robustness

### File Validation

The script checks for file existence before parsing:

```python
if not vtt_path.exists():
    raise FileNotFoundError(f"Subtitle file not found: {vtt_path}")
```

**Source:** [scripts/analyze_subtitles.py:39-40]()

### Malformed Entry Handling

Rather than failing on invalid subtitle blocks, the parser skips them:

```python
except Exception as e:
    # Skip unparseable blocks
    continue
```

This ensures that a few malformed entries don't prevent the entire file from being processed.

**Source:** [scripts/analyze_subtitles.py:104-106]()

### Empty Subtitle Protection

The script validates that subtitles exist before proceeding:

```python
if not subtitles:
    raise ValueError("No subtitles to analyze")
```

**Source:** [scripts/analyze_subtitles.py:134-135]()

---

## Performance Characteristics

### Processing Metrics

For a typical YouTube video:

| Metric | Example Value |
|--------|--------------|
| Input file size | 50-200 KB |
| Subtitle entries | 300-1000 |
| Parsing time | < 1 second |
| Memory usage | Minimal (subtitles held in memory) |
| Output text size | Similar to input |

### Scalability

The script processes subtitles sequentially in a single pass. Memory usage scales linearly with subtitle count, but even hour-long videos produce manageable data sizes (typically < 5000 subtitle entries).

**Sources:** [scripts/analyze_subtitles.py:20-114]()

---

## Example Execution Flow

```mermaid
sequenceDiagram
    participant User as "User/Claude Code"
    participant Main as "main()"
    participant Parse as "parse_vtt()"
    participant Utils as "utils.py"
    participant Prepare as "prepare_analysis_data()"
    participant Save as "save_analysis_data()"
    
    User->>Main: python analyze_subtitles.py video.en.vtt 180
    Main->>Parse: parse_vtt("video.en.vtt")
    
    loop For each subtitle block
        Parse->>Utils: time_to_seconds(start_str)
        Utils-->>Parse: start_seconds
        Parse->>Utils: time_to_seconds(end_str)
        Utils-->>Parse: end_seconds
    end
    
    Parse-->>Main: subtitles: List[Dict]
    
    Main->>Prepare: prepare_analysis_data(subtitles, 180)
    
    loop For each subtitle
        Prepare->>Utils: seconds_to_time(start)
        Utils-->>Prepare: "[HH:MM:SS]"
    end
    
    Prepare->>Prepare: Calculate estimated_chapters
    Prepare-->>Main: analysis_data: Dict
    
    Main->>Save: save_analysis_data(data, "analysis.json")
    Save-->>Main: Success
    
    Main->>User: Print subtitle_text preview
    Main->>User: Print analysis summary
```

**Sources:** [scripts/analyze_subtitles.py:186-248]()

---

## Relationship to AI Chapter Generation

This script is part of **Phase 3: AI Semantic Analysis** in the overall workflow. The prepared subtitle text is consumed by Claude Code, which:

1. Reads the timestamped subtitle text
2. Identifies semantic topic boundaries
3. Generates chapter titles and summaries
4. Ensures 2-5 minute chapter granularity

The `estimated_chapters` calculation provides a guidance value to Claude AI about how many chapters are expected based on the target duration, but the AI is free to adjust this based on actual content semantics.

**Estimation Formula:**
```python
estimated_chapters = max(1, int(total_duration / target_chapter_duration))
```

For `TARGET_CHAPTER_DURATION=180` (3 minutes), a 30-minute video yields `estimated_chapters=10`.

**Sources:** [scripts/analyze_subtitles.py:149](), [SKILL.md:96-145](), [README.md:193-209]()

---

## Configuration Integration

The script accepts `target_chapter_duration` as a parameter, which can be configured via environment variables:

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `TARGET_CHAPTER_DURATION` | 180 | Target chapter length in seconds |

When invoked by Claude Code, the skill reads this value from `.env` and passes it to the script.

**Sources:** [scripts/analyze_subtitles.py:117](), [.env.example]()

---

# Page: clip_video.py

# clip_video.py

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/ffmpeg-guide.md](references/ffmpeg-guide.md)
- [scripts/clip_video.py](scripts/clip_video.py)

</details>



This document covers the `clip_video.py` script, which performs precise video segment extraction using FFmpeg. The script provides a Python wrapper around FFmpeg's clipping functionality with time format conversion, validation, and quality-preserving stream copying. For subtitle burning onto clipped videos, see [burn_subtitles.py](#4.4). For subtitle-only extraction with timestamp adjustment, see [extract_subtitle_clip.py](#4.5).

Sources: [scripts/clip_video.py:1-237]()

## Overview

The `clip_video.py` script implements time-based video segmentation by invoking FFmpeg with precise start/end timestamps. It uses stream copying (`-c copy`) rather than re-encoding to maintain original video quality and achieve fast processing speeds. The script also provides utility functions for extracting corresponding subtitle segments with timestamp adjustment.

**Key responsibilities:**
- Convert time formats (string to seconds, seconds to formatted strings)
- Validate input files and time ranges
- Execute FFmpeg with optimized clipping parameters
- Extract subtitle segments matching video time ranges
- Adjust subtitle timestamps relative to clip start time
- Generate SRT format subtitle files

Sources: [scripts/clip_video.py:1-10](), [scripts/clip_video.py:21-123]()

## Function: clip_video()

The primary entry point for video clipping operations. This function accepts flexible time inputs (either numeric seconds or time strings like "01:30:00") and produces a clipped video segment.

### Function Signature

```python
def clip_video(
    video_path: str,
    start_time: Union[str, float],
    end_time: Union[str, float],
    output_path: str,
    ffmpeg_path: str = None
) -> str
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `video_path` | `str` | Path to input video file |
| `start_time` | `Union[str, float]` | Start timestamp (seconds or "HH:MM:SS" format) |
| `end_time` | `Union[str, float]` | End timestamp (seconds or "HH:MM:SS" format) |
| `output_path` | `str` | Destination path for clipped video |
| `ffmpeg_path` | `str` (optional) | Custom FFmpeg executable path; auto-detected if `None` |

**Returns:** `str` - Path to the created output file

**Raises:**
- `FileNotFoundError` - Input video file does not exist
- `ValueError` - Invalid time range (start >= end)
- `RuntimeError` - FFmpeg execution failure or missing FFmpeg binary

Sources: [scripts/clip_video.py:21-44]()

### Processing Flow

```mermaid
flowchart TD
    Start["clip_video() called"]
    ValidateInput["Validate input file exists<br/>[clip_video.py:48-50]"]
    ConvertTime["Convert time formats to seconds<br/>time_to_seconds() from utils"]
    ValidateRange["Validate start < end<br/>[clip_video.py:64-65]"]
    CalcDuration["Calculate duration = end - start<br/>[clip_video.py:67]"]
    DetectFFmpeg["Detect FFmpeg binary<br/>shutil.which('ffmpeg')"]
    PrintInfo["Print clip information<br/>[clip_video.py:75-80]"]
    CreateDir["Create output directory<br/>[clip_video.py:83]"]
    BuildCmd["Build FFmpeg command<br/>-ss START -i INPUT -t DURATION -c copy"]
    RunFFmpeg["Execute subprocess.run()<br/>[clip_video.py:101-105]"]
    CheckReturn["Check returncode == 0<br/>[clip_video.py:107]"]
    ValidateOutput["Validate output file exists<br/>[clip_video.py:113-114]"]
    PrintSuccess["Print file size and path<br/>[clip_video.py:116-120]"]
    ReturnPath["Return output_path"]
    
    RaiseNotFound["Raise FileNotFoundError"]
    RaiseValueError["Raise ValueError"]
    RaiseRuntimeError["Raise RuntimeError"]
    
    Start --> ValidateInput
    ValidateInput -->|exists| ConvertTime
    ValidateInput -->|not exists| RaiseNotFound
    ConvertTime --> ValidateRange
    ValidateRange -->|valid| CalcDuration
    ValidateRange -->|invalid| RaiseValueError
    CalcDuration --> DetectFFmpeg
    DetectFFmpeg -->|found| PrintInfo
    DetectFFmpeg -->|not found| RaiseRuntimeError
    PrintInfo --> CreateDir
    CreateDir --> BuildCmd
    BuildCmd --> RunFFmpeg
    RunFFmpeg --> CheckReturn
    CheckReturn -->|success| ValidateOutput
    CheckReturn -->|failed| RaiseRuntimeError
    ValidateOutput -->|exists| PrintSuccess
    ValidateOutput -->|missing| RaiseRuntimeError
    PrintSuccess --> ReturnPath
```

Sources: [scripts/clip_video.py:45-122]()

## FFmpeg Command Construction

The script constructs an FFmpeg command optimized for fast, lossless video clipping using stream copying.

### Command Structure

The FFmpeg command follows this pattern:

```
ffmpeg -ss <start_seconds> -i <input_video> -t <duration> -c copy -y <output_video>
```

**Command breakdown:**

| Flag | Value | Purpose |
|------|-------|---------|
| `-ss` | `start_seconds` | Seek to start position (input seeking for accuracy) |
| `-i` | `video_path` | Input file path |
| `-t` | `duration` | Duration to extract (calculated as `end - start`) |
| `-c` | `copy` | Copy streams without re-encoding (fast, lossless) |
| `-y` | - | Overwrite output file if exists |

Sources: [scripts/clip_video.py:85-96]()

### Stream Copying Strategy

The `-c copy` parameter instructs FFmpeg to copy video and audio streams directly without transcoding. This approach:

- **Preserves quality**: No generation loss from re-encoding
- **Maximizes speed**: No computational overhead from codec operations
- **Maintains format**: Original codec, bitrate, and container properties preserved
- **Limitations**: Cannot modify resolution, apply filters, or burn subtitles

For operations requiring re-encoding (e.g., subtitle burning), see [burn_subtitles.py](#4.4).

Sources: [scripts/clip_video.py:87-93](), [TECHNICAL_NOTES.md:33-48]()

### Execution and Error Handling

```mermaid
flowchart LR
    Build["Build command list<br/>[clip_video.py:88-96]"]
    Execute["subprocess.run()<br/>capture_output=True, text=True"]
    CheckCode["result.returncode"]
    Success["Validate output file exists<br/>Return path"]
    Failure["Print stderr<br/>Raise RuntimeError"]
    
    Build --> Execute
    Execute --> CheckCode
    CheckCode -->|0| Success
    CheckCode -->|non-zero| Failure
```

The script captures both stdout and stderr from FFmpeg for diagnostic purposes. On failure, the full error output is displayed to aid troubleshooting.

Sources: [scripts/clip_video.py:100-114]()

## Function: extract_subtitle_segment()

Extracts subtitle entries within a specified time range and optionally adjusts timestamps to be relative to the segment start time.

### Function Signature

```python
def extract_subtitle_segment(
    subtitles: list,
    start_time: float,
    end_time: float,
    adjust_timestamps: bool = True
) -> list
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `subtitles` | `list` | List of subtitle dicts with keys: `start`, `end`, `text` |
| `start_time` | `float` | Segment start time in seconds |
| `end_time` | `float` | Segment end time in seconds |
| `adjust_timestamps` | `bool` | If `True`, subtract `start_time` from all timestamps |

**Returns:** `list` - Filtered subtitle entries

Sources: [scripts/clip_video.py:125-142]()

### Timestamp Adjustment Logic

When `adjust_timestamps=True`, the function transforms subtitle timestamps to be relative to the clip's start time:

```
Original subtitle: [120s - 125s] "Hello world"
Clip range: [100s - 200s]
Adjusted subtitle: [20s - 25s] "Hello world"
```

**Three cases handled:**

1. **Subtitle fully within range**: Include and adjust
2. **Subtitle fully outside range**: Exclude
3. **Subtitle partially overlapping**: Include with boundary clamping

Sources: [scripts/clip_video.py:143-171]()

### Overlap Handling Diagram

```mermaid
flowchart TD
    CheckSub["For each subtitle in subtitles"]
    FullyInside{"sub.start >= start_time AND<br/>sub.end <= end_time"}
    PartialOverlap{"sub.start < end_time AND<br/>sub.end > start_time"}
    
    AdjustFull["Adjust timestamps:<br/>start' = start - start_time<br/>end' = end - start_time"]
    AdjustPartial["Clamp to boundaries:<br/>start' = max(0, start - start_time)<br/>end' = min(duration, end - start_time)"]
    
    AppendFull["Append adjusted subtitle"]
    AppendPartial["Append clamped subtitle"]
    Skip["Skip subtitle"]
    
    CheckSub --> FullyInside
    FullyInside -->|yes| AdjustFull
    FullyInside -->|no| PartialOverlap
    PartialOverlap -->|yes| AdjustPartial
    PartialOverlap -->|no| Skip
    
    AdjustFull --> AppendFull
    AdjustPartial --> AppendPartial
```

Sources: [scripts/clip_video.py:145-170]()

## Function: save_subtitles_as_srt()

Writes subtitle data to disk in SRT (SubRip) format with proper formatting and encoding.

### Function Signature

```python
def save_subtitles_as_srt(subtitles: list, output_path: str)
```

**Parameters:**
- `subtitles`: List of subtitle dictionaries with `start`, `end`, `text` keys
- `output_path`: Destination file path (directory created if needed)

### SRT Format Structure

The function generates SRT files following this structure:

```
1
00:00:00,000 --> 00:00:03,500
First subtitle text

2
00:00:03,500 --> 00:00:07,000
Second subtitle text
```

**Format requirements:**
- Sequential numbering starting from 1
- Timestamp format: `HH:MM:SS,mmm` (comma separator for milliseconds)
- Arrow separator: ` --> ` (space-arrow-space)
- Blank line between entries

Sources: [scripts/clip_video.py:174-201](), [TECHNICAL_NOTES.md:169-185]()

### Implementation Details

The function uses `seconds_to_time()` from `utils.py` with specific flags:

```python
start_time = seconds_to_time(sub['start'], include_hours=True, use_comma=True)
end_time = seconds_to_time(sub['end'], include_hours=True, use_comma=True)
```

**Key parameters:**
- `include_hours=True`: Always include hour field (required by SRT spec)
- `use_comma=True`: Use comma instead of period for milliseconds (SRT vs VTT format)

The file is written with UTF-8 encoding to support international characters in subtitle text.

Sources: [scripts/clip_video.py:185-201]()

## Command-Line Interface

When executed as a standalone script, `clip_video.py` provides a CLI for direct video clipping.

### Usage

```bash
python clip_video.py <video> <start_time> <end_time> <output>
```

**Arguments:**
- `video`: Input video file path
- `start_time`: Start time (numeric seconds or "HH:MM:SS" format)
- `end_time`: End time (numeric seconds or "HH:MM:SS" format)
- `output`: Output video file path

**Examples:**

```bash
# Using numeric seconds
python clip_video.py input.mp4 0 195 output.mp4

# Using time strings
python clip_video.py input.mp4 00:00:00 00:03:15 output.mp4
python clip_video.py input.mp4 01:30:00 01:33:15 output.mp4
```

Sources: [scripts/clip_video.py:204-217]()

### Error Handling

The CLI wrapper catches all exceptions and provides formatted error output:

```python
try:
    result_path = clip_video(video_path, start_time, end_time, output_path)
    print(f"\n✨ 完成！输出文件: {result_path}")
except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
```

Exit codes:
- `0`: Success
- `1`: Error (invalid arguments, FFmpeg failure, etc.)

Sources: [scripts/clip_video.py:224-232]()

## Integration with System Components

The `clip_video.py` script integrates with multiple system components in the processing pipeline.

```mermaid
flowchart TB
    subgraph "Input Sources"
        DownloadedVideo["Downloaded video<br/>(from download_video.py)"]
        ChapterData["Chapter timestamps<br/>(from analyze_subtitles.py)"]
    end
    
    subgraph "clip_video.py Functions"
        ClipVideoFunc["clip_video()<br/>Main clipping function"]
        ExtractSubFunc["extract_subtitle_segment()<br/>Subtitle extraction"]
        SaveSRTFunc["save_subtitles_as_srt()<br/>SRT file writer"]
    end
    
    subgraph "Utilities (utils.py)"
        TimeToSec["time_to_seconds()"]
        SecToTime["seconds_to_time()"]
        FormatSize["format_file_size()"]
        GetDuration["get_video_duration_display()"]
    end
    
    subgraph "External Tools"
        FFmpegBin["FFmpeg binary<br/>(-ss -i -t -c copy)"]
    end
    
    subgraph "Output Artifacts"
        ClippedVideo["Chapter_Title/*_clip.mp4<br/>Video segment"]
        SubtitleSRT["Chapter_Title/*.srt<br/>Subtitle segment"]
    end
    
    subgraph "Downstream Processing"
        BurnSubs["burn_subtitles.py<br/>Add hardcoded subtitles"]
        TranslateSubs["Translation pipeline<br/>Bilingual subtitles"]
    end
    
    DownloadedVideo --> ClipVideoFunc
    ChapterData --> ClipVideoFunc
    
    ClipVideoFunc --> TimeToSec
    ClipVideoFunc --> SecToTime
    ClipVideoFunc --> FormatSize
    ClipVideoFunc --> GetDuration
    ClipVideoFunc --> FFmpegBin
    
    ExtractSubFunc --> SecToTime
    SaveSRTFunc --> SecToTime
    
    ClipVideoFunc --> ClippedVideo
    ExtractSubFunc --> SubtitleSRT
    SaveSRTFunc --> SubtitleSRT
    
    ClippedVideo --> BurnSubs
    SubtitleSRT --> TranslateSubs
    SubtitleSRT --> BurnSubs
```

Sources: [scripts/clip_video.py:1-237](), [TECHNICAL_NOTES.md:1-490]()

### Dependency Table

| Component | Type | Purpose | Import/Call |
|-----------|------|---------|-------------|
| `utils.time_to_seconds()` | Function | Convert "HH:MM:SS" to seconds | [clip_video.py:14]() |
| `utils.seconds_to_time()` | Function | Convert seconds to formatted string | [clip_video.py:15]() |
| `utils.format_file_size()` | Function | Human-readable file size | [clip_video.py:16]() |
| `utils.get_video_duration_display()` | Function | Format duration for display | [clip_video.py:17]() |
| `shutil.which()` | Function | Detect FFmpeg binary path | [clip_video.py:71]() |
| `subprocess.run()` | Function | Execute FFmpeg command | [clip_video.py:101]() |
| `pathlib.Path` | Class | Cross-platform path handling | [clip_video.py:10,45-46]() |

Sources: [scripts/clip_video.py:7-18](), [scripts/clip_video.py:70-105]()

## Performance Characteristics

The stream copying approach provides significant performance advantages:

**Typical performance (1080p video):**
- **With `-c copy` (stream copy)**: 1-3 seconds per clip (I/O bound)
- **With re-encoding**: 30-120 seconds per clip (CPU bound)

**Speed multiplier**: 10-40x faster than re-encoding

**Quality**: Bit-perfect copy of original streams (no generation loss)

**Limitations**: Cannot apply filters, burn subtitles, or change resolution. For subtitle burning, the clipped video must be passed to `burn_subtitles.py` which performs re-encoding with the `subtitles` filter.

Sources: [TECHNICAL_NOTES.md:33-57](), [references/ffmpeg-guide.md:33-48]()

---

# Page: burn_subtitles.py

# burn_subtitles.py

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/ffmpeg-guide.md](references/ffmpeg-guide.md)
- [scripts/burn_subtitles.py](scripts/burn_subtitles.py)

</details>



## Purpose and Scope

The `burn_subtitles.py` script hardcodes (burns) subtitles into video files using FFmpeg's `subtitles` filter. This creates a single video file with permanently embedded subtitles that cannot be disabled or removed. The script handles two critical technical challenges: detecting FFmpeg installations with libass support and working around FFmpeg's inability to process file paths containing spaces.

For video clipping without subtitle burning, see [clip_video.py](#4.3). For subtitle extraction and time adjustment, see [extract_subtitle_clip.py](#4.5). For general FFmpeg integration details, see [FFmpeg Integration](#5.2).

Sources: [scripts/burn_subtitles.py:1-16]()

## Core Responsibilities

The script performs four primary functions:

1. **FFmpeg Variant Detection** - Identifies available FFmpeg installations and verifies libass support
2. **libass Support Verification** - Ensures the `subtitles` filter is available for subtitle burning
3. **Path Space Workaround** - Uses temporary directories to bypass FFmpeg's path handling limitations
4. **Subtitle Rendering** - Applies customizable subtitle styles (font size, margin) during video encoding

Sources: [scripts/burn_subtitles.py:1-288](), [TECHNICAL_NOTES.md:1-489]()

## System Architecture

### Component Interaction Flow

```mermaid
graph TB
    User["User/Calling Code"]
    BurnFunc["burn_subtitles()"]
    DetectFFmpeg["detect_ffmpeg_variant()"]
    CheckLibass["check_libass_support()"]
    TempDir["tempfile.mkdtemp()"]
    FFmpegExec["FFmpeg Binary"]
    
    User -->|"video_path, subtitle_path, output_path"| BurnFunc
    BurnFunc -->|"1. Detect FFmpeg"| DetectFFmpeg
    DetectFFmpeg -->|"2. Check filters"| CheckLibass
    CheckLibass -->|"3. Return FFmpeg info"| DetectFFmpeg
    DetectFFmpeg -->|"ffmpeg_path, has_libass"| BurnFunc
    BurnFunc -->|"4. Create temp directory"| TempDir
    TempDir -->|"temp_dir path (no spaces)"| BurnFunc
    BurnFunc -->|"5. Copy files to temp_dir"| TempDir
    BurnFunc -->|"6. Execute with temp paths"| FFmpegExec
    FFmpegExec -->|"7. Generate output video"| TempDir
    BurnFunc -->|"8. Move to final location"| User
    
    style BurnFunc fill:#f9f9f9
    style DetectFFmpeg fill:#f9f9f9
    style TempDir fill:#f9f9f9
```

Sources: [scripts/burn_subtitles.py:123-244]()

### FFmpeg Detection Strategy

```mermaid
graph TD
    Start["detect_ffmpeg_variant()"]
    CheckOS{"platform.system() == 'Darwin'?"}
    CheckFullARM["Check /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
    CheckFullIntel["Check /usr/local/opt/ffmpeg-full/bin/ffmpeg"]
    FoundFull{"ffmpeg-full exists?"}
    CheckStandard["shutil.which('ffmpeg')"]
    FoundStandard{"standard ffmpeg exists?"}
    VerifyLibass["check_libass_support(ffmpeg_path)"]
    ReturnFull["Return: type='full', path=..., has_libass=True/False"]
    ReturnStandard["Return: type='standard'/'full', path=..., has_libass=True/False"]
    ReturnNone["Return: type='none', path=None, has_libass=False"]
    
    Start --> CheckOS
    CheckOS -->|"Yes (macOS)"| CheckFullARM
    CheckFullARM --> FoundFull
    FoundFull -->|"No"| CheckFullIntel
    CheckFullIntel --> FoundFull
    FoundFull -->|"Yes"| VerifyLibass
    VerifyLibass --> ReturnFull
    CheckOS -->|"No"| CheckStandard
    FoundFull -->|"No (both paths)"| CheckStandard
    CheckStandard --> FoundStandard
    FoundStandard -->|"Yes"| VerifyLibass
    VerifyLibass --> ReturnStandard
    FoundStandard -->|"No"| ReturnNone
    
    style Start fill:#f9f9f9
    style VerifyLibass fill:#f9f9f9
```

Sources: [scripts/burn_subtitles.py:19-70]()

## Function Reference

### `detect_ffmpeg_variant()`

Detects available FFmpeg installations with a priority-based search strategy.

**Detection Priority:**
1. macOS `ffmpeg-full` on Apple Silicon: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
2. macOS `ffmpeg-full` on Intel: `/usr/local/opt/ffmpeg-full/bin/ffmpeg`
3. Standard `ffmpeg` in system PATH

**Return Structure:**
```python
{
    'type': 'full' | 'standard' | 'none',
    'path': str,  # FFmpeg executable path or None
    'has_libass': bool  # Whether subtitles filter is available
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | `str` | `'full'` if libass supported, `'standard'` if found but no libass, `'none'` if not found |
| `path` | `str` or `None` | Absolute path to FFmpeg binary |
| `has_libass` | `bool` | Result of `check_libass_support()` check |

Sources: [scripts/burn_subtitles.py:19-70]()

### `check_libass_support(ffmpeg_path)`

Verifies whether a specific FFmpeg installation supports the `subtitles` filter by checking available filters.

**Implementation:**
```python
# Executes: ffmpeg -filters
# Searches stdout for 'subtitles' keyword
```

**Parameters:**
- `ffmpeg_path` (str): Path to FFmpeg executable

**Returns:**
- `bool`: `True` if `subtitles` filter found in output, `False` otherwise

**Technical Details:**
- Runs `ffmpeg -filters` command
- Timeout set to 5 seconds to prevent hangs
- Case-insensitive search for `'subtitles'` in filter list
- Returns `False` on any exception (missing binary, timeout, etc.)

Sources: [scripts/burn_subtitles.py:73-96]()

### `install_ffmpeg_full_guide()`

Displays platform-specific installation instructions when libass support is missing.

**Output Content:**

| Platform | Instruction |
|----------|-------------|
| macOS (Darwin) | `brew install ffmpeg-full` |
| Other | Compile from source with `--enable-libass` |

**Displayed Information:**
- Installation commands
- Expected binary paths (Apple Silicon vs Intel)
- Verification command: `ffmpeg -filters 2>&1 | grep subtitles`

Sources: [scripts/burn_subtitles.py:99-121]()

### `burn_subtitles()`

Main function that orchestrates the subtitle burning process using FFmpeg.

**Function Signature:**
```python
def burn_subtitles(
    video_path: str,
    subtitle_path: str,
    output_path: str,
    ffmpeg_path: str = None,
    font_size: int = 24,
    margin_v: int = 30
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_path` | `str` | Required | Input video file path |
| `subtitle_path` | `str` | Required | SRT subtitle file path |
| `output_path` | `str` | Required | Output video file path |
| `ffmpeg_path` | `str` | `None` | FFmpeg binary path (auto-detected if None) |
| `font_size` | `int` | `24` | Subtitle font size in pixels |
| `margin_v` | `int` | `30` | Vertical margin from bottom in pixels |

**Returns:**
- `str`: Path to the output video file

**Raises:**
- `FileNotFoundError`: Input video or subtitle file not found
- `RuntimeError`: FFmpeg not found, no libass support, or execution failure

Sources: [scripts/burn_subtitles.py:123-244]()

## Temporary Directory Workaround

### The Path Space Problem

FFmpeg's `subtitles` filter cannot correctly parse file paths containing spaces, even when quoted or escaped. This is a known FFmpeg limitation.

**Failed Approaches:**
```bash
# All of these fail:
-vf "subtitles='/path/with spaces/sub.srt'"
-vf "subtitles=/path/with\ spaces/sub.srt"
-vf subtitles="'/path/with spaces/sub.srt'"
```

**Error Message:**
```
[Parsed_subtitles_0 @ 0x...] Unable to find '/path/with'
```

Note that the path is truncated at the first space character.

Sources: [TECHNICAL_NOTES.md:83-113]()

### Solution Implementation

```mermaid
sequenceDiagram
    participant Caller
    participant BurnFunc as "burn_subtitles()"
    participant TempFile as "tempfile.mkdtemp()"
    participant FileSystem
    participant FFmpeg
    
    Caller->>BurnFunc: "video_path='/my files/video.mp4'"
    BurnFunc->>TempFile: "Create temp dir"
    TempFile-->>BurnFunc: "/tmp/youtube_clipper_abc123"
    
    Note over BurnFunc: Temp dir has no spaces
    
    BurnFunc->>FileSystem: "shutil.copy(video_path, '/tmp/.../video.mp4')"
    BurnFunc->>FileSystem: "shutil.copy(subtitle_path, '/tmp/.../subtitle.srt')"
    
    BurnFunc->>FFmpeg: "ffmpeg -i /tmp/.../video.mp4 -vf subtitles=/tmp/.../subtitle.srt ..."
    FFmpeg-->>BurnFunc: "Success (no path space issues)"
    
    BurnFunc->>FileSystem: "shutil.move('/tmp/.../output.mp4', final_path)"
    BurnFunc->>FileSystem: "shutil.rmtree('/tmp/...')"
    BurnFunc-->>Caller: "output_path"
```

Sources: [scripts/burn_subtitles.py:179-243](), [TECHNICAL_NOTES.md:114-163]()

### Temporary Directory Lifecycle

**Step-by-Step Process:**

1. **Creation** - `tempfile.mkdtemp(prefix='youtube_clipper_')` creates directory in `/tmp/` with guaranteed space-free path
2. **File Copy** - Original video and subtitle files copied to temporary directory with simple names (`video.mp4`, `subtitle.srt`)
3. **FFmpeg Execution** - All paths passed to FFmpeg are within the temporary directory
4. **Output Retrieval** - Generated video moved from temporary directory to final output location
5. **Cleanup** - Temporary directory deleted with `shutil.rmtree(temp_dir, ignore_errors=True)`

**Code Locations:**
- Temp directory creation: [scripts/burn_subtitles.py:180-181]()
- File copying: [scripts/burn_subtitles.py:184-191]()
- FFmpeg execution: [scripts/burn_subtitles.py:193-219]()
- Output move: [scripts/burn_subtitles.py:225-228]()
- Cleanup: [scripts/burn_subtitles.py:238-243]()

Sources: [scripts/burn_subtitles.py:179-244]()

## FFmpeg Command Construction

### Subtitle Filter Configuration

The script constructs an FFmpeg filter string with customizable style parameters:

```python
subtitle_filter = f"subtitles={temp_subtitle}:force_style='FontSize={font_size},MarginV={margin_v}'"
```

**Default Style Parameters:**

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `FontSize` | `24` | Font size in pixels (suitable for 1080p) |
| `MarginV` | `30` | Vertical margin from bottom edge in pixels |

**Recommended Values by Resolution:**

| Resolution | FontSize | MarginV |
|------------|----------|---------|
| 720p | 20 | 20 |
| 1080p | 24 | 30 |
| 4K (2160p) | 48 | 60 |

Sources: [scripts/burn_subtitles.py:193-196](), [TECHNICAL_NOTES.md:357-388]()

### Complete FFmpeg Command

```python
cmd = [
    ffmpeg_path,
    '-i', temp_video,                # Input video
    '-vf', subtitle_filter,          # Video filter: subtitles
    '-c:a', 'copy',                  # Audio codec: copy (no re-encoding)
    '-y',                            # Overwrite output file
    temp_output                      # Output path
]
```

**Command Breakdown:**

| Flag | Value | Purpose |
|------|-------|---------|
| `-i` | `temp_video` | Input video file |
| `-vf` | `subtitle_filter` | Apply subtitles filter to video stream |
| `-c:a` | `copy` | Copy audio stream without re-encoding (faster, lossless) |
| `-y` | (flag) | Automatically overwrite output file if exists |

**Performance Characteristics:**
- **Video**: Re-encoded (subtitle burning requires processing pixels)
- **Audio**: Copied directly (no quality loss, faster)
- **Speed**: Slower than clipping (see [clip_video.py](#4.3)) due to video re-encoding

Sources: [scripts/burn_subtitles.py:197-204](), [references/ffmpeg-guide.md:52-69]()

## Command-Line Interface

### Usage Pattern

```bash
python burn_subtitles.py <video> <subtitle> <output> [font_size] [margin_v]
```

**Arguments:**

| Position | Parameter | Required | Default | Description |
|----------|-----------|----------|---------|-------------|
| 1 | `video` | Yes | - | Input video file path |
| 2 | `subtitle` | Yes | - | SRT subtitle file path |
| 3 | `output` | Yes | - | Output video file path |
| 4 | `font_size` | No | `24` | Font size in pixels |
| 5 | `margin_v` | No | `30` | Vertical margin in pixels |

### Example Invocations

**Basic Usage:**
```bash
python burn_subtitles.py input.mp4 subtitle.srt output.mp4
```

**Custom Styling:**
```bash
python burn_subtitles.py input.mp4 subtitle.srt output.mp4 28 40
```

**With Spaces in Paths:**
```bash
python burn_subtitles.py "my video.mp4" "my subtitle.srt" "my output.mp4"
# Script handles spaces automatically via temporary directory workaround
```

Sources: [scripts/burn_subtitles.py:247-283]()

## Error Handling

### Common Failure Scenarios

```mermaid
graph TD
    Start["burn_subtitles() called"]
    ValidateInput{"Input files exist?"}
    DetectFFmpeg["detect_ffmpeg_variant()"]
    HasFFmpeg{"FFmpeg found?"}
    HasLibass{"has_libass == True?"}
    Execute["Execute FFmpeg"]
    Success{"returncode == 0?"}
    ValidateOutput{"Output file created?"}
    Return["Return output_path"]
    
    ErrorFileNotFound["Raise FileNotFoundError:<br/>'Video/Subtitle file not found'"]
    ErrorNoFFmpeg["install_ffmpeg_full_guide()<br/>Raise RuntimeError:<br/>'FFmpeg not found'"]
    ErrorNoLibass["install_ffmpeg_full_guide()<br/>Raise RuntimeError:<br/>'FFmpeg does not support libass'"]
    ErrorExecution["Raise RuntimeError:<br/>'FFmpeg failed with return code X'"]
    ErrorNoOutput["Raise RuntimeError:<br/>'Output file not created'"]
    
    Start --> ValidateInput
    ValidateInput -->|"No"| ErrorFileNotFound
    ValidateInput -->|"Yes"| DetectFFmpeg
    DetectFFmpeg --> HasFFmpeg
    HasFFmpeg -->|"No"| ErrorNoFFmpeg
    HasFFmpeg -->|"Yes"| HasLibass
    HasLibass -->|"No"| ErrorNoLibass
    HasLibass -->|"Yes"| Execute
    Execute --> Success
    Success -->|"No"| ErrorExecution
    Success -->|"Yes"| ValidateOutput
    ValidateOutput -->|"No"| ErrorNoOutput
    ValidateOutput -->|"Yes"| Return
    
    style ErrorFileNotFound fill:#ffe6e6
    style ErrorNoFFmpeg fill:#ffe6e6
    style ErrorNoLibass fill:#ffe6e6
    style ErrorExecution fill:#ffe6e6
    style ErrorNoOutput fill:#ffe6e6
```

Sources: [scripts/burn_subtitles.py:154-228]()

### Exception Types

| Exception | Trigger | User Action |
|-----------|---------|-------------|
| `FileNotFoundError` | Input video or subtitle file missing | Verify file paths exist |
| `RuntimeError` (FFmpeg not found) | No FFmpeg in PATH or standard locations | Install FFmpeg or ffmpeg-full |
| `RuntimeError` (no libass) | FFmpeg lacks `subtitles` filter | Install ffmpeg-full or recompile with libass |
| `RuntimeError` (execution failed) | FFmpeg returns non-zero exit code | Check FFmpeg stderr output for details |
| `RuntimeError` (no output) | Output file not created despite success code | Check disk space, permissions |

Sources: [scripts/burn_subtitles.py:154-224]()

## Integration with Processing Pipeline

### Position in Workflow

The `burn_subtitles.py` script is invoked during **Phase 4: Processing Options** after video clipping and subtitle extraction have completed. It is an optional step selected by the user.

**Typical Call Chain:**
1. `download_video.py` - Downloads video and subtitles
2. `analyze_subtitles.py` - Generates semantic chapters
3. `clip_video.py` - Extracts video segments
4. `extract_subtitle_clip.py` - Extracts and adjusts subtitle segments
5. **`burn_subtitles.py`** - Burns subtitles into video (optional)

Sources: [scripts/burn_subtitles.py:1-288]()

### Expected Input Files

| File Type | Source | Format Requirements |
|-----------|--------|---------------------|
| Video | Output from `clip_video.py` | MP4 container, H.264 video |
| Subtitle | Output from `extract_subtitle_clip.py` (translated) | SRT format with adjusted timestamps |

**Output Location:**
```
./youtube-clips/YYYYMMDD_HHMMSS/Chapter_Title/*_with_subtitles.mp4
```

Sources: [scripts/burn_subtitles.py:123-244]()

## Platform-Specific Considerations

### macOS FFmpeg Variants

**Apple Silicon (M1/M2/M3):**
- Standard path: `/opt/homebrew/bin/ffmpeg` (often lacks libass)
- Full path: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` (recommended)

**Intel Mac:**
- Standard path: `/usr/local/bin/ffmpeg` (often lacks libass)
- Full path: `/usr/local/opt/ffmpeg-full/bin/ffmpeg` (recommended)

**Detection Order:**
1. Check `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` (Apple Silicon)
2. Check `/usr/local/opt/ffmpeg-full/bin/ffmpeg` (Intel)
3. Check `shutil.which('ffmpeg')` (system PATH)

Sources: [scripts/burn_subtitles.py:33-48](), [TECHNICAL_NOTES.md:5-80]()

### Linux Considerations

On Linux systems, FFmpeg is typically installed via package managers with libass support included:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg libass-dev

# Verification
ffmpeg -filters 2>&1 | grep subtitles
```

The script checks standard `ffmpeg` in PATH and verifies libass support automatically.

Sources: [TECHNICAL_NOTES.md:46-57](), [references/ffmpeg-guide.md:16-29]()

## Dependencies

### Python Modules

| Module | Purpose | Import Location |
|--------|---------|-----------------|
| `sys` | Exit codes, command-line args | [scripts/burn_subtitles.py:7]() |
| `os` | Path operations | [scripts/burn_subtitles.py:8]() |
| `shutil` | File operations, FFmpeg detection | [scripts/burn_subtitles.py:9]() |
| `subprocess` | FFmpeg execution | [scripts/burn_subtitles.py:10]() |
| `tempfile` | Temporary directory creation | [scripts/burn_subtitles.py:11]() |
| `platform` | OS detection (macOS vs others) | [scripts/burn_subtitles.py:12]() |
| `pathlib.Path` | Cross-platform path handling | [scripts/burn_subtitles.py:13]() |
| `typing` | Type hints | [scripts/burn_subtitles.py:14]() |
| `utils.format_file_size` | File size formatting utility | [scripts/burn_subtitles.py:16]() |

### External Dependencies

| Tool | Required Version | Purpose |
|------|------------------|---------|
| FFmpeg | Any with libass | Subtitle burning via `subtitles` filter |
| libass | (via FFmpeg) | Subtitle rendering library |

Sources: [scripts/burn_subtitles.py:7-16]()

---

# Page: extract_subtitle_clip.py

# extract_subtitle_clip.py

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/subtitle-formatting.md](references/subtitle-formatting.md)
- [scripts/extract_subtitle_clip.py](scripts/extract_subtitle_clip.py)

</details>



## Purpose and Scope

This document covers the `extract_subtitle_clip.py` script, which extracts time-bounded subtitle segments from VTT subtitle files and converts them to SRT format with adjusted timestamps. This script is a critical component in the video clipping workflow, ensuring that subtitle files match the temporal boundaries of their corresponding video clips.

For information about video clipping operations, see [clip_video.py](#4.3). For subtitle burning (hardcoding subtitles into video), see [burn_subtitles.py](#4.4). For general subtitle format conversion details, see [Subtitle Format Conversion](#7.4).

---

## System Role and Integration

The `extract_subtitle_clip.py` script operates as part of the subtitle processing pipeline, working in coordination with video clipping operations. When a video segment is extracted, this script ensures that the accompanying subtitle file contains only the relevant subtitle entries with timestamps adjusted to match the new zero-based timeline of the clip.

**Primary Responsibilities:**
- Parse VTT (WebVTT) subtitle files
- Filter subtitles within specified time boundaries
- Adjust timestamps relative to clip start time
- Convert VTT format to SRT format
- Output synchronized subtitle files for video clips

Sources: [scripts/extract_subtitle_clip.py:1-115]()

### Integration Architecture

```mermaid
flowchart TB
    subgraph "Video Processing"
        CV["clip_video.py<br/>FFmpeg video extraction"]
        VideoClip["Video Clip<br/>start_time to end_time"]
    end
    
    subgraph "Subtitle Processing"
        ESC["extract_subtitle_clip.py<br/>Subtitle extraction"]
        VTTFile["Original VTT File<br/>Full video subtitles"]
        SRTFile["Extracted SRT File<br/>Clip-specific subtitles"]
    end
    
    subgraph "Time Conversion"
        ParseVTT["parse_vtt_time()<br/>VTT to seconds"]
        FormatSRT["format_srt_time()<br/>Seconds to SRT"]
    end
    
    subgraph "Output Integration"
        BS["burn_subtitles.py<br/>Optional subtitle burning"]
        FinalOutput["Chapter Output Directory"]
    end
    
    CV --> VideoClip
    VTTFile --> ESC
    ESC --> ParseVTT
    ParseVTT --> ESC
    ESC --> FormatSRT
    FormatSRT --> SRTFile
    
    VideoClip --> FinalOutput
    SRTFile --> BS
    SRTFile --> FinalOutput
    BS --> FinalOutput
    
    style ESC fill:#f9f9f9
    style ParseVTT fill:#f9f9f9
    style FormatSRT fill:#f9f9f9
```

Sources: [scripts/extract_subtitle_clip.py:33-101](), [scripts/clip_video.py](), [scripts/burn_subtitles.py]()

---

## Time Format Conversion

The script handles conversion between VTT (WebVTT) and SRT (SubRip) time formats, which differ in their millisecond separator character and optional hour component.

### Time Format Specifications

| Format | Structure | Millisecond Separator | Example |
|--------|-----------|----------------------|---------|
| VTT    | `HH:MM:SS.mmm` or `MM:SS.mmm` | Period (`.`) | `00:02:35.500` |
| SRT    | `HH:MM:SS,mmm` | Comma (`,`) | `00:02:35,500` |

### VTT Time Parsing

The `parse_vtt_time()` function converts VTT timestamp strings to floating-point seconds, handling both two-part (MM:SS.mmm) and three-part (HH:MM:SS.mmm) formats.

**Function Signature:**
```python
def parse_vtt_time(time_str) -> float
```

**Algorithm:**
1. Split timestamp string by colon (`:`) delimiter
2. If 3 parts: extract hours, minutes, and seconds with milliseconds
3. If 2 parts: extract minutes and seconds with milliseconds
4. Convert to total seconds: `hours*3600 + minutes*60 + seconds`

**Time Parsing Logic Diagram:**

```mermaid
flowchart TD
    Input["Time String Input<br/>e.g., '00:02:35.500'"]
    Split["Split by ':'"]
    Check{Parts Count}
    
    ThreePart["Parse HH:MM:SS.mmm<br/>hours = parts[0]<br/>minutes = parts[1]<br/>seconds = parts[2]"]
    TwoPart["Parse MM:SS.mmm<br/>minutes = parts[0]<br/>seconds = parts[1]"]
    
    CalcThree["Calculate:<br/>hours*3600 + minutes*60 + seconds"]
    CalcTwo["Calculate:<br/>minutes*60 + seconds"]
    
    Output["Return total_seconds<br/>e.g., 155.5"]
    
    Input --> Split
    Split --> Check
    Check -->|"len == 3"| ThreePart
    Check -->|"len == 2"| TwoPart
    ThreePart --> CalcThree
    TwoPart --> CalcTwo
    CalcThree --> Output
    CalcTwo --> Output
```

Sources: [scripts/extract_subtitle_clip.py:10-22]()

### SRT Time Formatting

The `format_srt_time()` function converts floating-point seconds to SRT timestamp format with comma-separated milliseconds.

**Function Signature:**
```python
def format_srt_time(seconds) -> str
```

**Conversion Process:**
1. Create `timedelta` object from total seconds
2. Extract hours: `total_seconds // 3600`
3. Extract minutes: `(total_seconds % 3600) // 60`
4. Extract seconds: `total_seconds % 60`
5. Extract milliseconds: `(total_seconds % 1) * 1000`
6. Format as: `HH:MM:SS,mmm`

**Example Conversions:**

| Input (seconds) | Output (SRT format) |
|----------------|---------------------|
| `0.0` | `00:00:00,000` |
| `3.5` | `00:00:03,500` |
| `155.5` | `00:02:35,500` |
| `3725.678` | `01:02:05,678` |

Sources: [scripts/extract_subtitle_clip.py:24-31](), [TECHNICAL_NOTES.md:166-212]()

---

## Subtitle Extraction Algorithm

The `extract_subtitle_clip()` function implements the core logic for extracting subtitle segments within specified time boundaries and converting them to SRT format.

**Function Signature:**
```python
def extract_subtitle_clip(vtt_file, start_time, end_time, output_file) -> list
```

### Extraction Workflow

```mermaid
flowchart TB
    Start["Function Entry<br/>extract_subtitle_clip()"]
    ParseTimes["Parse start_time and end_time<br/>Using parse_vtt_time()"]
    ReadVTT["Read VTT file<br/>encoding='utf-8'"]
    
    ParseLoop["Parse VTT Lines<br/>Sequential iteration"]
    FindTimestamp{Line contains<br/>'-->' ?}
    
    ExtractTimes["Extract timestamp strings<br/>Split by '-->'"]
    ParseSubTimes["Parse sub_start and sub_end<br/>Using parse_vtt_time()"]
    
    CheckBounds{sub_start >= start_seconds<br/>AND<br/>sub_end <= end_seconds}
    
    CollectText["Collect subtitle text lines<br/>Until blank line"]
    AdjustTime["Adjust timestamps:<br/>adjusted_start = sub_start - start_seconds<br/>adjusted_end = sub_end - start_seconds"]
    AppendSub["Append to subtitles list"]
    
    Skip["Skip to next line"]
    
    WriteSRT["Write SRT format:<br/>1. Sequence number<br/>2. Timestamp line<br/>3. Text content<br/>4. Blank line"]
    
    Return["Return subtitles list"]
    
    Start --> ParseTimes
    ParseTimes --> ReadVTT
    ReadVTT --> ParseLoop
    ParseLoop --> FindTimestamp
    FindTimestamp -->|Yes| ExtractTimes
    FindTimestamp -->|No| Skip
    ExtractTimes --> ParseSubTimes
    ParseSubTimes --> CheckBounds
    CheckBounds -->|Yes| CollectText
    CheckBounds -->|No| Skip
    CollectText --> AdjustTime
    AdjustTime --> AppendSub
    AppendSub --> Skip
    Skip --> ParseLoop
    ParseLoop -->|End of file| WriteSRT
    WriteSRT --> Return
```

Sources: [scripts/extract_subtitle_clip.py:33-101]()

### Line-by-Line Parsing Process

The script uses a sequential line parser to identify and extract subtitle entries from VTT files:

1. **Timestamp Line Detection**: Searches for lines containing `-->` separator
2. **Timestamp Extraction**: Splits timestamp line to extract start and end times
3. **Text Collection**: Accumulates subsequent non-empty lines as subtitle text
4. **Boundary Filtering**: Retains only subtitles fully contained within target time range

**Timestamp Line Parsing:**
```python
# Example from scripts/extract_subtitle_clip.py:55-59
time_parts = line.split('-->')
sub_start_str = time_parts[0].strip().split()[0]  # Remove position metadata
sub_end_str = time_parts[1].strip().split()[0]    # Remove position metadata
```

This parsing approach handles VTT position metadata (e.g., `align:start position:0%`) by extracting only the first whitespace-separated token from each timestamp component.

Sources: [scripts/extract_subtitle_clip.py:44-85](), [references/subtitle-formatting.md:1-53]()

---

## Timestamp Adjustment Logic

A critical function of this script is adjusting subtitle timestamps to align with the zero-based timeline of extracted video clips. When a video segment is clipped from `start_time` to `end_time`, the corresponding subtitles must have their timestamps shifted so that they begin at `00:00:00,000`.

### Adjustment Calculation

**Formula:**
```
adjusted_time = original_time - clip_start_time
```

**Example Scenario:**

| Context | Original Video | Extracted Clip |
|---------|---------------|----------------|
| Clip range | - | 02:00 to 02:10 |
| Subtitle 1 start | 02:00 (120s) | 00:00 (0s) |
| Subtitle 1 end | 02:03 (123s) | 00:03 (3s) |
| Subtitle 2 start | 02:05 (125s) | 00:05 (5s) |
| Subtitle 2 end | 02:08 (128s) | 00:08 (8s) |

### Implementation Details

```mermaid
flowchart LR
    subgraph "Original Timeline"
        OS["Original Subtitle<br/>start: 02:00:00<br/>end: 02:03:00"]
    end
    
    subgraph "Clip Parameters"
        CP["Clip Start: 02:00:00<br/>start_seconds = 120"]
    end
    
    subgraph "Adjustment Calculation"
        Calc["adjusted_start = 120 - 120 = 0<br/>adjusted_end = 123 - 120 = 3"]
    end
    
    subgraph "Adjusted Timeline"
        AS["Adjusted Subtitle<br/>start: 00:00:00<br/>end: 00:00:03"]
    end
    
    OS --> Calc
    CP --> Calc
    Calc --> AS
```

**Code Implementation:**
```python
# From scripts/extract_subtitle_clip.py:75-77
adjusted_start = sub_start - start_seconds
adjusted_end = sub_end - start_seconds
```

### Boundary Conditions

The script enforces strict boundary filtering to ensure subtitle integrity:

**Inclusion Criteria:**
- Subtitle start time must be >= clip start time
- Subtitle end time must be <= clip end time
- Both conditions must be satisfied (logical AND)

**Filtering Logic:**
```python
# From scripts/extract_subtitle_clip.py:65
if sub_start >= start_seconds and sub_end <= end_seconds:
    # Include subtitle
```

This strict filtering prevents partial subtitle entries that would extend beyond the video clip boundaries, avoiding synchronization issues.

Sources: [scripts/extract_subtitle_clip.py:75-83](), [TECHNICAL_NOTES.md:215-258](), [references/subtitle-formatting.md:243-301]()

---

## SRT Output Format

The script generates SRT files conforming to the SubRip format specification:

**SRT Structure:**
```
<sequence_number>
<start_timestamp> --> <end_timestamp>
<subtitle_text>
<blank_line>
```

### Output Generation

```mermaid
flowchart TD
    SubList["Subtitles List<br/>[{start, end, text}, ...]"]
    Enumerate["Enumerate with index<br/>Starting from 1"]
    
    WriteSeq["Write sequence number:<br/>idx"]
    WriteTime["Write timestamp line:<br/>format_srt_time(start) --> format_srt_time(end)"]
    WriteText["Write text content:<br/>subtitle text"]
    WriteBlank["Write blank line"]
    
    NextSub{More subtitles?}
    Complete["Complete SRT file"]
    
    SubList --> Enumerate
    Enumerate --> WriteSeq
    WriteSeq --> WriteTime
    WriteTime --> WriteText
    WriteText --> WriteBlank
    WriteBlank --> NextSub
    NextSub -->|Yes| Enumerate
    NextSub -->|No| Complete
```

**Output Example:**
```srt
1
00:00:00,000 --> 00:00:03,500
This is the first subtitle

2
00:00:03,500 --> 00:00:07,000
This is the second subtitle
```

**File Writing Implementation:**
```python
# From scripts/extract_subtitle_clip.py:90-95
with open(output_file, 'w', encoding='utf-8') as f:
    for idx, sub in enumerate(subtitles, 1):
        f.write(f"{idx}\n")
        f.write(f"{format_srt_time(sub['start'])} --> {format_srt_time(sub['end'])}\n")
        f.write(f"{sub['text']}\n")
        f.write("\n")
```

All SRT files are written with UTF-8 encoding to ensure proper handling of multilingual content.

Sources: [scripts/extract_subtitle_clip.py:89-99](), [references/subtitle-formatting.md:56-91]()

---

## Command-Line Interface

The script provides a command-line interface for standalone execution outside of the main YouTube Clipper workflow.

**Usage Syntax:**
```bash
python extract_subtitle_clip.py <vtt_file> <start_time> <end_time> <output_file>
```

**Parameters:**

| Parameter | Type | Format | Description |
|-----------|------|--------|-------------|
| `vtt_file` | Path | File path | Input VTT subtitle file |
| `start_time` | String | `HH:MM:SS` or `MM:SS` | Clip start time |
| `end_time` | String | `HH:MM:SS` or `MM:SS` | Clip end time |
| `output_file` | Path | File path | Output SRT subtitle file |

**Example Command:**
```bash
python extract_subtitle_clip.py input.vtt 00:05:47 00:09:19 output.srt
```

**Console Output:**
```
📝 提取字幕片段...
   输入: input.vtt
   时间范围: 00:05:47 - 00:09:19
   时间范围（秒）: 347.0s - 559.0s
   找到 28 条字幕
✅ 字幕提取完成
   输出文件: output.srt
   字幕条数: 28
```

**Argument Validation:**
```python
# From scripts/extract_subtitle_clip.py:104-107
if len(sys.argv) != 5:
    print("用法: python extract_subtitle_clip.py <vtt_file> <start_time> <end_time> <output_file>")
    print("示例: python extract_subtitle_clip.py input.vtt 00:05:47 00:09:19 output.srt")
    sys.exit(1)
```

Sources: [scripts/extract_subtitle_clip.py:103-114]()

---

## Data Structures and Return Values

The `extract_subtitle_clip()` function returns a list of subtitle dictionaries for potential programmatic use.

**Return Value Structure:**
```python
[
    {
        'start': 0.0,           # Adjusted start time in seconds
        'end': 3.5,             # Adjusted end time in seconds
        'text': 'Subtitle text' # Subtitle content
    },
    {
        'start': 3.5,
        'end': 7.0,
        'text': 'Another subtitle'
    },
    # ...
]
```

**Internal Data Flow:**

```mermaid
flowchart LR
    VTT["VTT File<br/>time1 --> time2<br/>text"]
    
    Parse["Parsing<br/>{sub_start: float<br/>sub_end: float<br/>text: str}"]
    
    Filter["Filtering<br/>Boundary check"]
    
    Adjust["Adjustment<br/>{start: adjusted_start<br/>end: adjusted_end<br/>text: text}"]
    
    List["Subtitles List<br/>[{start, end, text}, ...]"]
    
    SRT["SRT File<br/>idx<br/>start --> end<br/>text"]
    
    VTT --> Parse
    Parse --> Filter
    Filter --> Adjust
    Adjust --> List
    List --> SRT
    List -.->|"Return value"| Return["Return List"]
```

This return value enables integration with translation pipelines or other subtitle processing scripts that may need programmatic access to the extracted subtitle data.

Sources: [scripts/extract_subtitle_clip.py:79-83](), [scripts/extract_subtitle_clip.py:101]()

---

## Error Handling and Edge Cases

The script handles several edge cases to ensure robust subtitle extraction:

### Edge Case: Empty Time Range

If the specified time range contains no subtitles, the script generates an empty SRT file:
```
   找到 0 条字幕
✅ 字幕提取完成
   输出文件: output.srt
   字幕条数: 0
```

### Edge Case: Partial Subtitle Overlap

Subtitles that partially overlap the time boundaries are excluded. Only subtitles fully contained within the range are included:

```python
# Strict boundary check - scripts/extract_subtitle_clip.py:65
if sub_start >= start_seconds and sub_end <= end_seconds:
    # Include
```

**Example:**
- Clip range: `02:00 - 02:10`
- Subtitle: `01:58 - 02:02` → **Excluded** (starts before range)
- Subtitle: `02:08 - 02:12` → **Excluded** (ends after range)
- Subtitle: `02:03 - 02:07` → **Included** (fully within range)

### Edge Case: Malformed VTT Lines

The script skips lines that don't contain the `-->` separator, tolerating:
- Header lines (`WEBVTT`)
- Style blocks
- Comment lines
- Empty lines

### Text Collection Robustness

The text collection loop terminates on blank lines, joining multiple text lines with spaces:

```python
# From scripts/extract_subtitle_clip.py:68-73
text_lines = []
while i < len(lines) and lines[i].strip() != '':
    text_lines.append(lines[i].strip())
    i += 1
text = ' '.join(text_lines)
```

This handles multi-line subtitle entries correctly while preventing array index errors at file end.

Sources: [scripts/extract_subtitle_clip.py:64-85](), [scripts/extract_subtitle_clip.py:87-99]()

---

## Performance Characteristics

**Time Complexity:**
- **O(n)** where n is the number of lines in the VTT file
- Single-pass sequential parsing
- No sorting or complex operations required

**Space Complexity:**
- **O(m)** where m is the number of subtitles in the output range
- Full file read into memory initially
- Filtered subtitles stored in list

**Typical Performance:**
- 30-minute video (~600 subtitle entries): < 1 second processing time
- Minimal memory footprint (<10 MB for typical subtitle files)

**Optimization Considerations:**
The script prioritizes simplicity and correctness over performance optimization, as subtitle extraction is not a performance bottleneck in the overall video processing pipeline.

Sources: [scripts/extract_subtitle_clip.py:33-101]()

---

## Integration with Translation Pipeline

While this script outputs single-language SRT files, the extracted subtitles serve as input for the translation pipeline, which generates bilingual subtitle files.

**Workflow Integration:**

```mermaid
flowchart LR
    ESC["extract_subtitle_clip.py<br/>Extract & convert to SRT"]
    SRT["English SRT<br/>Clip-specific"]
    Trans["Translation Pipeline<br/>Batch translation"]
    BiSRT["Bilingual SRT<br/>EN + Target Language"]
    Burn["burn_subtitles.py<br/>Optional burning"]
    
    ESC --> SRT
    SRT --> Trans
    Trans --> BiSRT
    BiSRT --> Burn
```

The bilingual subtitle format places English text on the first line and translated text on the second line of each subtitle entry, maintaining the timestamp structure generated by this script.

**Example Bilingual Output:**
```srt
1
00:00:00,000 --> 00:00:03,500
This is English subtitle
这是中文字幕

2
00:00:03,500 --> 00:00:07,000
Another English line
另一行中文
```

Sources: [references/subtitle-formatting.md:178-213](), [TECHNICAL_NOTES.md:259-305]()

---

## Related Documentation

For comprehensive information on related topics:

- **VTT Format Details**: See [references/subtitle-formatting.md:1-53]()
- **SRT Format Specification**: See [references/subtitle-formatting.md:56-91]()
- **Format Conversion Technical Details**: See [TECHNICAL_NOTES.md:166-212]()
- **Timestamp Adjustment Implementation**: See [TECHNICAL_NOTES.md:215-258]()
- **Video Clipping Coordination**: See [clip_video.py](#4.3)
- **Subtitle Burning Integration**: See [burn_subtitles.py](#4.4)
- **Batch Translation Optimization**: See [Batch Translation Optimization](#7.1)

---

# Page: Utilities Module

# Utilities Module

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/__init__.py](scripts/__init__.py)
- [scripts/clip_video.py](scripts/clip_video.py)
- [scripts/download_video.py](scripts/download_video.py)

</details>



## Purpose and Scope

The Utilities Module (`scripts/utils.py`) provides shared helper functions used across all core scripts in the YouTube Clipper Skill. This module centralizes common operations such as time conversion, file management, data formatting, and validation to ensure consistency and reduce code duplication.

This page documents the utility functions and their usage patterns. For documentation on individual scripts that use these utilities, see [Core Scripts](#4).

---

## Overview

The utilities module serves as a foundational layer that supports all video processing operations. It provides five categories of functionality:

| Category | Functions | Primary Purpose |
|----------|-----------|-----------------|
| Time Conversion | `time_to_seconds()`, `seconds_to_time()` | Convert between time formats for FFmpeg and display |
| File Management | `ensure_directory()`, `sanitize_filename()` | Handle file paths and directory creation |
| Formatting | `format_file_size()`, `get_video_duration_display()` | Format data for user-friendly display |
| Validation | `validate_url()` | Validate user inputs |
| Video Information | `get_video_duration_display()` | Extract and display video metadata |

**Sources:** [scripts/clip_video.py:13-18](), [scripts/download_video.py:18-24]()

---

## Module Architecture

```mermaid
graph TB
    subgraph "Utility Categories"
        TimeUtils["Time Conversion<br/>time_to_seconds()<br/>seconds_to_time()"]
        FileUtils["File Management<br/>ensure_directory()<br/>sanitize_filename()"]
        FormatUtils["Formatting<br/>format_file_size()<br/>get_video_duration_display()"]
        ValidateUtils["Validation<br/>validate_url()"]
    end
    
    subgraph "Core Scripts"
        Download["download_video.py"]
        Analyze["analyze_subtitles.py"]
        Clip["clip_video.py"]
        Burn["burn_subtitles.py"]
        Extract["extract_subtitle_clip.py"]
    end
    
    Download --> ValidateUtils
    Download --> FileUtils
    Download --> FormatUtils
    
    Clip --> TimeUtils
    Clip --> FormatUtils
    
    Extract --> TimeUtils
    
    Burn --> TimeUtils
    Burn --> FileUtils
    
    Analyze --> FileUtils
```

**Sources:** [scripts/clip_video.py:13-18](), [scripts/download_video.py:18-24]()

---

## Time Conversion Functions

### time_to_seconds()

Converts time strings or numeric values to floating-point seconds. This function handles multiple input formats to provide flexibility for both programmatic and user inputs.

**Function Signature (inferred):**
```python
def time_to_seconds(time_input: Union[str, int, float]) -> float
```

**Supported Input Formats:**
- Numeric seconds: `195` → `195.0`
- Time strings with hours: `"01:30:45"` → `5445.0`
- Time strings without hours: `"03:15"` → `195.0`
- Time strings with decimal seconds: `"00:03:15.500"` → `195.5`

**Usage Example:**

[scripts/clip_video.py:53-61]() demonstrates conversion of start and end times:
```python
# Accepts both string and numeric inputs
if isinstance(start_time, str):
    start_seconds = time_to_seconds(start_time)
else:
    start_seconds = float(start_time)
```

**Sources:** [scripts/clip_video.py:14](), [scripts/clip_video.py:53-61]()

---

### seconds_to_time()

Converts numeric seconds to formatted time strings suitable for display or FFmpeg commands.

**Function Signature (inferred):**
```python
def seconds_to_time(
    seconds: float,
    include_hours: bool = False,
    use_comma: bool = False
) -> str
```

**Parameters:**
- `seconds`: Numeric seconds to convert
- `include_hours`: Force HH:MM:SS format even for durations under 1 hour
- `use_comma`: Use comma separator for milliseconds (SRT format requirement)

**Output Formats:**
- Standard: `"03:15"` (MM:SS)
- With hours: `"00:03:15"` (HH:MM:SS)
- SRT format: `"00:03:15,500"` (HH:MM:SS,mmm with comma)

**Usage Examples:**

[scripts/clip_video.py:77-79]() shows display formatting:
```python
print(f"   起始时间: {seconds_to_time(start_seconds)} ({start_seconds}s)")
print(f"   结束时间: {seconds_to_time(end_seconds)} ({end_seconds}s)")
```

[scripts/clip_video.py:191-192]() demonstrates SRT subtitle timestamp generation:
```python
start_time = seconds_to_time(sub['start'], include_hours=True, use_comma=True)
end_time = seconds_to_time(sub['end'], include_hours=True, use_comma=True)
```

**Sources:** [scripts/clip_video.py:15](), [scripts/clip_video.py:77-79](), [scripts/clip_video.py:191-192]()

---

## Time Conversion Flow

```mermaid
flowchart LR
    subgraph "Input Sources"
        UserInput["User Input<br/>'01:30:45' or 195"]
        FFmpegOutput["FFmpeg Metadata<br/>5445.0 seconds"]
        SubtitleData["Subtitle Timestamps<br/>195.5 seconds"]
    end
    
    subgraph "time_to_seconds()"
        Parse["Parse Format"]
        Convert["Convert to Float"]
    end
    
    subgraph "seconds_to_time()"
        CalcHours["Calculate Hours"]
        CalcMins["Calculate Minutes"]
        CalcSecs["Calculate Seconds"]
        Format["Format String"]
    end
    
    subgraph "Output Formats"
        Display["Display Format<br/>'03:15'"]
        SRT["SRT Format<br/>'00:03:15,500'"]
        FFmpegCmd["FFmpeg Command<br/>'00:03:15'"]
    end
    
    UserInput --> Parse
    Parse --> Convert
    Convert --> CalcHours
    
    FFmpegOutput --> CalcHours
    SubtitleData --> CalcHours
    
    CalcHours --> CalcMins
    CalcMins --> CalcSecs
    CalcSecs --> Format
    
    Format --> Display
    Format --> SRT
    Format --> FFmpegCmd
```

**Sources:** [scripts/clip_video.py:53-61](), [scripts/clip_video.py:191-192]()

---

## File Management Functions

### ensure_directory()

Creates directory structures if they don't exist, with support for nested paths.

**Function Signature (inferred):**
```python
def ensure_directory(path: Union[str, Path]) -> Path
```

**Behavior:**
- Creates parent directories as needed (`parents=True`)
- Silently succeeds if directory already exists (`exist_ok=True`)
- Returns `Path` object for chaining operations

**Usage Example:**

[scripts/download_video.py:58]() uses this to prepare output directories:
```python
output_dir = ensure_directory(output_dir)
```

**Sources:** [scripts/download_video.py:24](), [scripts/download_video.py:58]()

---

### sanitize_filename()

Removes or replaces characters that are invalid in filenames across different operating systems.

**Function Signature (inferred):**
```python
def sanitize_filename(filename: str, replacement: str = '_') -> str
```

**Character Handling:**
- Removes: `< > : " / \ | ? *`
- Replaces with: underscore or specified replacement character
- Preserves: alphanumerics, spaces, hyphens, periods

**Platform Considerations:**
- Windows: Removes reserved characters and device names (CON, PRN, etc.)
- Unix/Linux: Primarily removes `/` and null bytes
- macOS: Removes `:` and `/`

**Usage Context:**

Used in [scripts/download_video.py:20]() when processing video titles to create safe filenames for output directories and files.

**Sources:** [scripts/download_video.py:20]()

---

## Formatting Functions

### format_file_size()

Converts byte counts to human-readable file size strings with appropriate units.

**Function Signature (inferred):**
```python
def format_file_size(bytes: int, decimal_places: int = 2) -> str
```

**Unit Conversion:**
- Bytes: `< 1024` → `"512 B"`
- Kilobytes: `< 1024²` → `"1.5 KB"`
- Megabytes: `< 1024³` → `"25.3 MB"`
- Gigabytes: `≥ 1024³` → `"1.2 GB"`

**Usage Examples:**

[scripts/download_video.py:134]() formats downloaded file size:
```python
print(f"   大小: {format_file_size(file_size)}")
```

[scripts/download_video.py:162-163]() displays download progress:
```python
downloaded = format_file_size(d['downloaded_bytes'])
total = format_file_size(d['total_bytes'])
```

[scripts/clip_video.py:120]() shows clipped video size:
```python
print(f"   文件大小: {format_file_size(output_size)}")
```

**Sources:** [scripts/download_video.py:22](), [scripts/clip_video.py:16](), [scripts/download_video.py:134](), [scripts/download_video.py:162-163](), [scripts/clip_video.py:120]()

---

### get_video_duration_display()

Formats video duration in seconds to a human-readable string.

**Function Signature (inferred):**
```python
def get_video_duration_display(duration_seconds: float) -> str
```

**Output Examples:**
- `195` seconds → `"3:15"` or `"3分15秒"`
- `3661` seconds → `"1:01:01"` or `"1小时1分1秒"`

**Implementation Note:**
This function may return localized strings based on system locale or configuration settings.

**Usage Examples:**

[scripts/download_video.py:100]() displays total video duration:
```python
print(f"   时长: {get_video_duration_display(duration)}")
```

[scripts/clip_video.py:79]() shows segment duration:
```python
print(f"   片段时长: {get_video_duration_display(duration)}")
```

**Sources:** [scripts/download_video.py:22](), [scripts/clip_video.py:17](), [scripts/download_video.py:100](), [scripts/clip_video.py:79]()

---

## Validation Functions

### validate_url()

Validates that a given string is a properly formatted YouTube URL.

**Function Signature (inferred):**
```python
def validate_url(url: str) -> bool
```

**Accepted URL Formats:**
- Standard: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short: `https://youtu.be/VIDEO_ID`
- Mobile: `https://m.youtube.com/watch?v=VIDEO_ID`
- Embedded: `https://www.youtube.com/embed/VIDEO_ID`
- With timestamps: `https://youtube.com/watch?v=VIDEO_ID&t=123s`

**Validation Logic:**
- Checks domain matches YouTube patterns
- Validates presence of video ID
- Accepts both HTTP and HTTPS protocols

**Usage Example:**

[scripts/download_video.py:49-50]() validates URL before download:
```python
if not validate_url(url):
    raise ValueError(f"Invalid YouTube URL: {url}")
```

**Sources:** [scripts/download_video.py:19](), [scripts/download_video.py:49-50]()

---

## Cross-Script Dependencies

The following diagram maps specific utility functions to the scripts that depend on them, bridging natural language descriptions to actual code entities:

```mermaid
graph LR
    subgraph "utils.py Functions"
        time_to_seconds["time_to_seconds()"]
        seconds_to_time["seconds_to_time()"]
        format_file_size["format_file_size()"]
        get_video_duration_display["get_video_duration_display()"]
        validate_url["validate_url()"]
        sanitize_filename["sanitize_filename()"]
        ensure_directory["ensure_directory()"]
    end
    
    subgraph "download_video.py"
        download_video_func["download_video()"]
        _progress_hook["_progress_hook()"]
    end
    
    subgraph "clip_video.py"
        clip_video_func["clip_video()"]
        extract_subtitle_segment["extract_subtitle_segment()"]
        save_subtitles_as_srt["save_subtitles_as_srt()"]
    end
    
    validate_url --> download_video_func
    sanitize_filename --> download_video_func
    ensure_directory --> download_video_func
    format_file_size --> download_video_func
    format_file_size --> _progress_hook
    get_video_duration_display --> download_video_func
    
    time_to_seconds --> clip_video_func
    seconds_to_time --> clip_video_func
    seconds_to_time --> save_subtitles_as_srt
    format_file_size --> clip_video_func
    get_video_duration_display --> clip_video_func
```

**Sources:** [scripts/download_video.py:18-24](), [scripts/clip_video.py:13-18]()

---

## Common Usage Patterns

### Pattern 1: Time Parameter Flexibility

Scripts accept both string and numeric time inputs, using `time_to_seconds()` for normalization:

[scripts/clip_video.py:53-61]()
```python
# Convert time to seconds
if isinstance(start_time, str):
    start_seconds = time_to_seconds(start_time)
else:
    start_seconds = float(start_time)
```

This pattern enables both programmatic usage (passing numeric seconds) and user-friendly command-line usage (passing time strings like `"01:30:00"`).

**Sources:** [scripts/clip_video.py:53-61]()

---

### Pattern 2: Safe Path Creation

All file operations use `ensure_directory()` to guarantee output paths exist:

[scripts/download_video.py:58]()
```python
output_dir = ensure_directory(output_dir)
```

[scripts/clip_video.py:83]()
```python
output_path.parent.mkdir(parents=True, exist_ok=True)
```

**Sources:** [scripts/download_video.py:58](), [scripts/clip_video.py:83]()

---

### Pattern 3: User-Friendly Progress Display

File sizes and durations are consistently formatted for display using `format_file_size()` and `get_video_duration_display()`:

[scripts/download_video.py:162-172]()
```python
downloaded = format_file_size(d['downloaded_bytes'])
total = format_file_size(d['total_bytes'])
speed_str = format_file_size(speed) + '/s' if speed else 'N/A'
print(f"\r   [{bar}] {percent:.1f}% - {downloaded}/{total} - {speed_str}", end='', flush=True)
```

**Sources:** [scripts/download_video.py:162-172]()

---

### Pattern 4: SRT Timestamp Generation

The `seconds_to_time()` function with specific parameters generates SRT-compliant timestamps:

[scripts/clip_video.py:191-193]()
```python
start_time = seconds_to_time(sub['start'], include_hours=True, use_comma=True)
end_time = seconds_to_time(sub['end'], include_hours=True, use_comma=True)
f.write(f"{start_time} --> {end_time}\n")
```

The `include_hours=True` ensures three-component timestamps (HH:MM:SS), and `use_comma=True` uses comma separators for milliseconds as required by the SRT specification.

**Sources:** [scripts/clip_video.py:191-193]()

---

## Design Rationale

### Centralization Benefits

By centralizing common operations in a utilities module:

1. **Consistency**: All scripts use identical formatting logic for file sizes, durations, and timestamps
2. **Maintainability**: Bug fixes and improvements in one location benefit all scripts
3. **Testability**: Utility functions can be tested independently of script logic
4. **Reusability**: New scripts can immediately leverage existing utilities

### Type Flexibility

Utility functions accept multiple input types (e.g., `Union[str, float]` for time parameters) to support:

- **Command-line usage**: Users can pass `"01:30:00"` as strings
- **Programmatic usage**: Scripts can pass `5400.0` as floats
- **API integration**: External systems can use either format

### Error Handling

Utility functions follow consistent error handling patterns:

- Invalid inputs raise `ValueError` with descriptive messages
- File operations raise `FileNotFoundError` or `IOError` as appropriate
- Type coercion failures are caught and re-raised with context

**Sources:** [scripts/clip_video.py:64-65](), [scripts/download_video.py:49-50]()

---

## Integration Points

### With FFmpeg

Time conversion functions generate FFmpeg-compatible timestamp formats:

[scripts/clip_video.py:88-96]()
```python
cmd = [
    ffmpeg_path,
    '-ss', str(start_seconds),  # FFmpeg accepts numeric seconds
    '-i', str(video_path),
    '-t', str(duration),
    '-c', 'copy',
    '-y',
    str(output_path)
]
```

FFmpeg accepts numeric seconds directly, so `time_to_seconds()` output can be passed as strings without additional formatting.

**Sources:** [scripts/clip_video.py:88-96]()

---

### With yt-dlp

File management utilities prepare directories and sanitize filenames for yt-dlp output:

[scripts/download_video.py:58-70]()
```python
output_dir = ensure_directory(output_dir)

ydl_opts = {
    'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
    # ... other options
}
```

The output template uses video ID directly to avoid filename sanitization issues, but `sanitize_filename()` is available for processing video titles.

**Sources:** [scripts/download_video.py:58-70]()

---

### With Subtitle Processing

Time conversion and formatting utilities support subtitle manipulation:

[scripts/clip_video.py:125-172]() demonstrates subtitle segment extraction using `time_to_seconds()` for boundary checking and `seconds_to_time()` for SRT output generation.

**Sources:** [scripts/clip_video.py:125-172](), [scripts/clip_video.py:174-202]()

---

## File Location

The utilities module is located at:
- **Path**: `scripts/utils.py`
- **Imported by**: All core processing scripts in `scripts/` directory
- **Dependencies**: Python standard library only (no external packages)

**Sources:** [scripts/clip_video.py:13](), [scripts/download_video.py:18]()

---

# Page: External Tools

# External Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [install_as_skill.sh](install_as_skill.sh)

</details>



The YouTube Clipper Skill relies on two critical external command-line tools: **yt-dlp** for downloading YouTube videos and subtitles, and **FFmpeg** for video processing and subtitle rendering. These tools are invoked as subprocesses from Python scripts and form the foundation of the system's video processing capabilities. This page documents how these tools are integrated, configured, and verified within the skill.

For configuration options that control these tools' behavior, see [Configuration](#6). For troubleshooting common issues with these tools, see [Troubleshooting](#8).

---

## External Tool Architecture

The system integrates external tools through subprocess execution, with Python scripts acting as orchestrators that prepare arguments, invoke commands, and process results.

```mermaid
graph TB
    subgraph "Python Scripts Layer"
        DV["download_video.py"]
        CV["clip_video.py"]
        BS["burn_subtitles.py"]
    end
    
    subgraph "External Tools"
        YtDlpCLI["yt-dlp CLI<br/>(system binary)"]
        YtDlpLib["yt_dlp Python Library<br/>(pip package)"]
        FFmpegBin["ffmpeg binary<br/>(system binary)"]
        LibASS["libass library<br/>(FFmpeg filter)"]
    end
    
    subgraph "Data Sources"
        YouTube["YouTube Platform"]
    end
    
    subgraph "Output"
        VideoFiles["MP4 Video Files"]
        SubFiles["VTT/SRT Subtitle Files"]
    end
    
    DV -->|"subprocess.run()"| YtDlpCLI
    DV -->|"import yt_dlp"| YtDlpLib
    YtDlpCLI --> YouTube
    YtDlpLib --> YouTube
    
    CV -->|"subprocess.run()"| FFmpegBin
    BS -->|"subprocess.run()"| FFmpegBin
    FFmpegBin --> LibASS
    
    YtDlpCLI --> VideoFiles
    YtDlpCLI --> SubFiles
    YtDlpLib --> VideoFiles
    YtDlpLib --> SubFiles
    
    FFmpegBin --> VideoFiles
    LibASS --> VideoFiles
    
    CV -.->|"reads"| VideoFiles
    BS -.->|"reads"| VideoFiles
    BS -.->|"reads"| SubFiles
```

**Sources:** [README.md:54-84](), [TECHNICAL_NOTES.md:1-80](), Diagram 1 from high-level architecture

---

## yt-dlp Integration

### Purpose and Usage

yt-dlp is used exclusively for downloading YouTube videos and subtitles. The system uses both the Python library (`yt_dlp`) for programmatic access and verifies the CLI tool's presence during installation.

### Implementation in download_video.py

The download script uses the `yt_dlp` Python library with extensive configuration options:

```mermaid
graph LR
    Input["YouTube URL"]
    Config["yt_dlp Options Dict"]
    YtDlp["yt_dlp.YoutubeDL()"]
    Download["download() method"]
    Files["Output Files:<br/>- video.mp4<br/>- subtitles.en.vtt"]
    
    Input --> Config
    Config --> YtDlp
    YtDlp --> Download
    Download --> Files
```

**Format Selection Logic:**

The format string prioritizes quality while limiting file size: `bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best`

This selection strategy [TECHNICAL_NOTES.md:309-319]():
1. Attempts to combine best video (≤1080p, MP4) with best audio (M4A)
2. Falls back to single best file (≤1080p, MP4)
3. Final fallback to any best available format

**Subtitle Configuration:**

```python
'writesubtitles': True,
'writeautomaticsub': True,  # Fallback to auto-generated
'subtitleslangs': ['en'],
'subtitlesformat': 'vtt',
```

Priority order [TECHNICAL_NOTES.md:328-338]():
1. Human-authored subtitles (if available)
2. YouTube automatic subtitles (fallback)

**Sources:** [TECHNICAL_NOTES.md:306-353](), [README.md:54-58]()

---

### Configuration Options

The following environment variables control yt-dlp behavior:

| Variable | Default | Purpose | Example |
|----------|---------|---------|---------|
| `MAX_VIDEO_HEIGHT` | 1080 | Maximum video resolution | `720`, `1080`, `1440`, `2160` |
| `YT_DLP_PROXY` | None | HTTP/SOCKS5 proxy | `http://proxy:8080` |
| `YT_DLP_RATE_LIMIT` | None | Download speed limit | `5M` (5 MB/s) |

**Sources:** [README.md:133-151]()

---

### Installation Detection

The installation script verifies yt-dlp presence in two forms:

```mermaid
graph TD
    Start["Installation Script"]
    CheckCLI{"yt-dlp command<br/>exists?"}
    CheckLib{"yt_dlp Python<br/>module installed?"}
    InstallLib["pip3 install yt-dlp"]
    WarnCLI["Print warning:<br/>CLI tool recommended"]
    Success["Continue installation"]
    
    Start --> CheckCLI
    CheckCLI -->|"No"| WarnCLI
    CheckCLI -->|"Yes"| CheckLib
    WarnCLI --> CheckLib
    CheckLib -->|"No"| InstallLib
    CheckLib -->|"Yes"| Success
    InstallLib --> Success
```

Detection logic [install_as_skill.sh:139-150]():
- Uses `command -v yt-dlp` to check CLI availability
- Installs Python package via `pip3 install yt-dlp`
- Warns if CLI tool is missing but continues installation

**Sources:** [install_as_skill.sh:139-150]()

---

### Output File Naming

yt-dlp generates files using this template pattern:

```
'outtmpl': '%(title)s [%(id)s].%(ext)s'
```

Example output [TECHNICAL_NOTES.md:341-348]():
```
Anthropic's Amodei on AI [Ckt1cj0xjRM].mp4
Anthropic's Amodei on AI [Ckt1cj0xjRM].en.vtt
```

The video ID inclusion provides:
- **Uniqueness:** Prevents filename collisions
- **Traceability:** Enables reverse-lookup to original video

**Sources:** [TECHNICAL_NOTES.md:340-353]()

---

## FFmpeg Integration

### Purpose and Usage

FFmpeg performs two critical operations:
1. **Video clipping:** Frame-accurate segment extraction ([clip_video.py]())
2. **Subtitle burning:** Hardcoding subtitles into video ([burn_subtitles.py]())

### Video Clipping Implementation

The `clip_video.py` script executes FFmpeg with precise time-based extraction:

```mermaid
graph LR
    InputVideo["video.mp4"]
    StartTime["start_time<br/>(seconds)"]
    EndTime["end_time<br/>(seconds)"]
    FFmpegCmd["ffmpeg -ss START -to END<br/>-i video.mp4 -c copy"]
    OutputClip["chapter_clip.mp4"]
    
    InputVideo --> FFmpegCmd
    StartTime --> FFmpegCmd
    EndTime --> FFmpegCmd
    FFmpegCmd --> OutputClip
```

**Command Structure:**
```bash
ffmpeg -ss <start_seconds> -to <end_seconds> -i <input_video> \
       -c copy -avoid_negative_ts make_zero <output_video>
```

Key arguments:
- `-ss`: Start timestamp (seeks to position)
- `-to`: End timestamp (duration limit)
- `-c copy`: Stream copy (no re-encoding, preserves quality)
- `-avoid_negative_ts make_zero`: Ensures valid timestamps

**Sources:** [README.md:16-17](), Diagram 2 from high-level architecture

---

### Subtitle Burning Implementation

The `burn_subtitles.py` script uses FFmpeg's `subtitles` filter with critical workarounds:

```mermaid
graph TD
    InputVideo["video.mp4<br/>(original clip)"]
    InputSRT["bilingual.srt<br/>(may have path spaces)"]
    TempDir["Create temp directory<br/>(guaranteed no spaces)"]
    CopyFiles["Copy to temp:<br/>- temp/video.mp4<br/>- temp/subtitle.srt"]
    FFmpegCmd["ffmpeg -i temp/video.mp4<br/>-vf subtitles=temp/subtitle.srt:force_style=...<br/>temp/output.mp4"]
    MoveOutput["Move temp/output.mp4<br/>to final location"]
    Cleanup["Remove temp directory"]
    
    InputVideo --> TempDir
    InputSRT --> TempDir
    TempDir --> CopyFiles
    CopyFiles --> FFmpegCmd
    FFmpegCmd --> MoveOutput
    MoveOutput --> Cleanup
```

**Critical Issue: Path Space Handling**

FFmpeg's `subtitles` filter cannot process file paths containing spaces [TECHNICAL_NOTES.md:83-163](). All quote/escape attempts fail:
- ❌ `subtitles="/path/with spaces/sub.srt"`
- ❌ `subtitles='/path/with spaces/sub.srt'`
- ❌ `subtitles=/path/with\ spaces/sub.srt`

**Solution:** Temporary directory workaround [TECHNICAL_NOTES.md:117-148]():
1. Create temp directory with `tempfile.mkdtemp()` (no spaces guaranteed)
2. Copy input files to temp directory
3. Execute FFmpeg with space-free paths
4. Move output back to original location
5. Clean up temporary files

**Subtitle Styling:**

```bash
subtitles=subtitle.srt:force_style='FontSize=24,MarginV=30'
```

Style parameters [TECHNICAL_NOTES.md:372-388]():
- `FontSize=24`: Text size (scaled for 1080p)
- `MarginV=30`: Bottom margin in pixels
- Default rendering: White text with black outline

| Resolution | FontSize | MarginV |
|------------|----------|---------|
| 720p       | 20       | 20      |
| 1080p      | 24       | 30      |
| 4K         | 48       | 60      |

**Sources:** [TECHNICAL_NOTES.md:83-163](), [TECHNICAL_NOTES.md:356-388](), [README.md:18-19]()

---

### FFmpeg Path Detection

Both scripts detect FFmpeg location through environment variable or system PATH:

```python
ffmpeg_path = os.getenv('FFMPEG_PATH') or shutil.which('ffmpeg')
```

If `FFMPEG_PATH` is set in `.env`, it takes precedence. Otherwise, the system searches PATH.

**Sources:** [README.md:134-135]()

---

## libass Requirement

### Purpose and Critical Nature

The `libass` library enables FFmpeg's `subtitles` filter, which is essential for burning subtitles into video. Without libass support, subtitle burning fails completely.

### Detection and Validation

```mermaid
graph TD
    Start["FFmpeg Validation"]
    CheckOS{"Operating System?"}
    CheckFull["Check /opt/homebrew/opt/<br/>ffmpeg-full/bin/ffmpeg"]
    CheckIntel["Check /usr/local/opt/<br/>ffmpeg-full/bin/ffmpeg"]
    CheckStd["Check standard ffmpeg<br/>(from PATH)"]
    TestLibass["Run: ffmpeg -filters 2>&1<br/>| grep subtitles"]
    HasSubtitles{"Output contains<br/>'subtitles'?"}
    Success["libass supported"]
    Fail["libass NOT supported<br/>Print installation guide"]
    
    Start --> CheckOS
    CheckOS -->|"macOS"| CheckFull
    CheckOS -->|"Other"| CheckStd
    CheckFull -->|"Exists"| Success
    CheckFull -->|"Not found"| CheckIntel
    CheckIntel -->|"Exists"| Success
    CheckIntel -->|"Not found"| CheckStd
    CheckStd --> TestLibass
    TestLibass --> HasSubtitles
    HasSubtitles -->|"Yes"| Success
    HasSubtitles -->|"No"| Fail
```

Detection implementation [TECHNICAL_NOTES.md:66-79]():

**macOS Specific Paths:**
- Apple Silicon: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
- Intel Mac: `/usr/local/opt/ffmpeg-full/bin/ffmpeg`

**libass Test Command:**
```bash
ffmpeg -filters 2>&1 | grep subtitles
# Expected output: "subtitles    V->V  (...)"
```

**Sources:** [TECHNICAL_NOTES.md:5-80](), [install_as_skill.sh:152-191]()

---

### Platform-Specific Installation

#### macOS

**Problem:** Homebrew's standard `ffmpeg` formula excludes libass to reduce package size.

**Solution:** Install `ffmpeg-full` [TECHNICAL_NOTES.md:28-43]():

```bash
# Remove standard ffmpeg (if present)
brew uninstall ffmpeg

# Install ffmpeg-full (includes libass)
brew install ffmpeg-full

# Verify
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -filters 2>&1 | grep subtitles
```

#### Ubuntu/Debian

```bash
sudo apt-get install ffmpeg libass-dev
```

#### Generic/Source Build

```bash
# Install libass development files
sudo apt-get install libass-dev

# Build FFmpeg with libass support
./configure --enable-libass
make
sudo make install
```

**Sources:** [TECHNICAL_NOTES.md:28-57](), [README.md:67-84]()

---

### Installation Script Validation

The installation script performs comprehensive FFmpeg/libass validation [install_as_skill.sh:152-191]():

1. **Check ffmpeg-full** (macOS only)
   - Apple Silicon path: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
   - Intel Mac path: `/usr/local/opt/ffmpeg-full/bin/ffmpeg`

2. **Check standard FFmpeg** (all platforms)
   - Uses `command -v ffmpeg`
   - Extracts version with `ffmpeg -version`

3. **Validate libass support**
   - Executes `ffmpeg -filters 2>&1 | grep -q "subtitles"`
   - Sets `LIBASS_SUPPORTED=true/false` flag

4. **Report results**
   - ✅ FFmpeg with libass: All features available
   - ⚠️ FFmpeg without libass: Clipping works, burning fails
   - ❌ No FFmpeg: Installation incomplete

**Sources:** [install_as_skill.sh:152-191]()

---

## Subprocess Execution Pattern

Both tools follow a consistent subprocess execution pattern in Python scripts:

```mermaid
graph TD
    BuildCmd["Build command list:<br/>['ffmpeg', '-i', 'input.mp4', ...]"]
    RunSubprocess["subprocess.run(cmd,<br/>capture_output=True,<br/>text=True,<br/>check=False)"]
    CheckReturn{"return_code == 0?"}
    ParseOutput["Parse stdout/stderr"]
    Success["Return success"]
    Error["Print error details:<br/>- Command<br/>- Return code<br/>- stderr output"]
    Raise["Raise RuntimeError"]
    
    BuildCmd --> RunSubprocess
    RunSubprocess --> CheckReturn
    CheckReturn -->|"Yes"| ParseOutput
    CheckReturn -->|"No"| Error
    ParseOutput --> Success
    Error --> Raise
```

**Common subprocess parameters:**
- `capture_output=True`: Capture stdout/stderr
- `text=True`: Decode output as strings
- `check=False`: Manual return code checking for better error messages

**Error handling best practice [TECHNICAL_NOTES.md:445-475]():**
```python
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Command failed:")
    print(f"   Command: {' '.join(cmd)}")
    print(f"   Return code: {result.returncode}")
    print(f"   Error output:")
    print(result.stderr)
    raise RuntimeError("Command failed")
```

**Sources:** [TECHNICAL_NOTES.md:444-475]()

---

## Dependency Matrix

Summary of which Python scripts depend on which external tools:

| Script | yt-dlp CLI | yt_dlp Library | FFmpeg | libass |
|--------|------------|----------------|--------|--------|
| `download_video.py` | Optional¹ | **Required** | - | - |
| `analyze_subtitles.py` | - | - | - | - |
| `clip_video.py` | - | - | **Required** | - |
| `burn_subtitles.py` | - | - | **Required** | **Required** |
| `extract_subtitle_clip.py` | - | - | - | - |

¹ CLI tool recommended but library can work standalone

**Sources:** Diagram 3 from high-level architecture, [README.md:54-66]()

---

## Version Requirements

| Tool | Minimum Version | Recommendation | Notes |
|------|----------------|----------------|-------|
| Python | 3.8+ | 3.10+ | Required for scripts |
| yt-dlp | Latest | Update frequently | YouTube changes require updates |
| FFmpeg | 4.0+ | Latest | Version 4.0+ has stable `subtitles` filter |
| libass | 0.13+ | Latest | Bundled with FFmpeg-full |

**Sources:** [README.md:50-66]()

---

## Configuration Summary

Environment variables controlling external tool behavior:

```bash
# FFmpeg binary path (auto-detected if empty)
FFMPEG_PATH=

# yt-dlp network settings
YT_DLP_PROXY=http://proxy:8080
YT_DLP_RATE_LIMIT=5M

# Video quality constraints
MAX_VIDEO_HEIGHT=1080

# Subtitle rendering style
SUBTITLE_FONT_SIZE=24
SUBTITLE_MARGIN_V=30
```

For complete configuration reference, see [Configuration](#6).

**Sources:** [README.md:129-154]()

---

# Page: yt-dlp Integration

# yt-dlp Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/yt-dlp-guide.md](references/yt-dlp-guide.md)
- [scripts/download_video.py](scripts/download_video.py)

</details>



## Purpose and Scope

This document details how the YouTube Clipper Skill integrates with yt-dlp for video and subtitle acquisition. The integration is implemented in [scripts/download_video.py]() and uses the yt-dlp Python library to download YouTube videos with quality constraints, subtitle extraction, and progress monitoring.

For FFmpeg-based video processing, see [FFmpeg Integration](#5.2). For subtitle format conversion after download, see [Subtitle Format Conversion](#7.4).

---

## Installation Requirements

yt-dlp is installed as a Python package dependency during system setup. The [install_as_skill.sh]() script installs it via pip, and [scripts/download_video.py:12-16]() verifies its availability at runtime:

```python
try:
    import yt_dlp
except ImportError:
    print("❌ Error: yt-dlp not installed")
    print("Please install: pip install yt-dlp")
    sys.exit(1)
```

Installation methods:
- **Homebrew**: `brew install yt-dlp`
- **pip**: `pip install yt-dlp`
- **System package managers**: `apt-get install yt-dlp`

**Sources**: [scripts/download_video.py:12-16](), [references/yt-dlp-guide.md:6-28]()

---

## Integration Architecture

The following diagram shows how yt-dlp integrates with the download module:

```mermaid
graph TB
    subgraph "scripts/download_video.py"
        main["main()<br/>CLI entry point"]
        download_video["download_video()<br/>Core function"]
        progress_hook["_progress_hook()<br/>Progress callback"]
        
        subgraph "Utilities"
            validate_url["validate_url()"]
            sanitize_filename["sanitize_filename()"]
            format_file_size["format_file_size()"]
            ensure_directory["ensure_directory()"]
        end
    end
    
    subgraph "yt_dlp Library"
        YoutubeDL["yt_dlp.YoutubeDL<br/>Main class"]
        extract_info["extract_info()<br/>Fetch metadata/download"]
        prepare_filename["prepare_filename()<br/>Get output path"]
    end
    
    subgraph "Configuration"
        ydl_opts["ydl_opts dict<br/>format, outtmpl, writesubtitles, etc"]
    end
    
    subgraph "Output Files"
        video_file["video_id.mp4<br/>Video file"]
        subtitle_file["video_id.en.vtt<br/>Subtitle file"]
    end
    
    main --> download_video
    download_video --> validate_url
    download_video --> ensure_directory
    download_video --> ydl_opts
    
    ydl_opts --> YoutubeDL
    download_video --> YoutubeDL
    
    YoutubeDL --> extract_info
    YoutubeDL --> prepare_filename
    
    extract_info --> progress_hook
    extract_info --> video_file
    extract_info --> subtitle_file
    
    download_video --> format_file_size
    download_video --> sanitize_filename
```

**Sources**: [scripts/download_video.py:27-154](), [scripts/utils.py]()

---

## Configuration Dictionary

The `download_video()` function configures yt-dlp through the `ydl_opts` dictionary at [scripts/download_video.py:65-87]():

| Option | Value | Purpose |
|--------|-------|---------|
| `format` | `bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best` | Format selection with 1080p limit |
| `outtmpl` | `%(id)s.%(ext)s` | Output filename template using video ID |
| `writesubtitles` | `True` | Download manual subtitles if available |
| `writeautomaticsub` | `True` | Fallback to auto-generated subtitles |
| `subtitleslangs` | `['en']` | English subtitles only |
| `subtitlesformat` | `'vtt'` | VTT format (converted to SRT later) |
| `writethumbnail` | `False` | Skip thumbnail download |
| `quiet` | `False` | Show download messages |
| `progress_hooks` | `[_progress_hook]` | Progress callback function |

The configuration prioritizes compatibility (mp4 format), reasonable file sizes (1080p limit), and reliable subtitle acquisition (auto-generated as fallback).

**Sources**: [scripts/download_video.py:65-87](), [TECHNICAL_NOTES.md:307-354]()

---

## Format Selection Logic

The format string at [scripts/download_video.py:67]() implements a fallback chain:

```mermaid
graph LR
    A["Format String"] --> B["Primary:<br/>bestvideo[height<=1080][ext=mp4]<br/>+<br/>bestaudio[ext=m4a]"]
    B -->|"If unavailable"| C["Fallback 1:<br/>best[height<=1080][ext=mp4]"]
    C -->|"If unavailable"| D["Fallback 2:<br/>best<br/>(any format/resolution)"]
    
    style B text-align:left
    style C text-align:left
    style D text-align:left
```

### Format String Components

```
bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best
│         │              │        │         │       │                           │
│         │              │        │         │       │                           └─ Final fallback
│         │              │        │         │       └─ Fallback: single stream 1080p mp4
│         │              │        │         └─ Merge with best audio (m4a)
│         │              │        └─ Combine operator
│         │              └─ Prefer mp4 container
│         └─ Limit resolution to 1080p maximum
└─ Best video quality
```

### Resolution Limit Rationale

The 1080p constraint serves multiple purposes (documented in [TECHNICAL_NOTES.md:321-325]()):

1. **File Size**: 4K videos can exceed 5-10GB
2. **Processing Speed**: FFmpeg operations on 4K are significantly slower
3. **Output Target**: Short video platforms primarily use 1080p or lower
4. **Storage Efficiency**: Reduces disk space requirements

**Sources**: [scripts/download_video.py:67](), [TECHNICAL_NOTES.md:307-354](), [references/yt-dlp-guide.md:62-104]()

---

## Subtitle Download Process

The subtitle extraction workflow follows this pattern:

```mermaid
flowchart TD
    A["Start Download"] --> B["yt_dlp.YoutubeDL<br/>with writesubtitles=True"]
    B --> C["extract_info(url, download=True)"]
    
    C --> D{"Manual English<br/>subtitles exist?"}
    D -->|"Yes"| E["Download *.en.vtt"]
    D -->|"No"| F{"Auto-generated<br/>available?"}
    
    F -->|"Yes"| G["Download auto *.en.vtt<br/>(writeautomaticsub=True)"]
    F -->|"No"| H["No subtitles downloaded"]
    
    E --> I["Search for subtitle file"]
    G --> I
    H --> I
    
    I --> J["Check patterns:<br/>video_id.en.vtt<br/>video_id.vtt"]
    
    J --> K{"File found?"}
    K -->|"Yes"| L["Return subtitle_path"]
    K -->|"No"| M["Return subtitle_path=None"]
```

### Subtitle File Location

The subtitle search logic at [scripts/download_video.py:112-124]() checks multiple patterns:

```python
subtitle_exts = ['.en.vtt', '.vtt']
for ext in subtitle_exts:
    potential_sub = video_path.with_suffix(ext)
    if not potential_sub.exists():
        stem = video_path.stem
        potential_sub = video_path.parent / f"{stem}.en.vtt"
    if potential_sub.exists():
        subtitle_path = potential_sub
        break
```

Expected subtitle filenames for video ID `abc123`:
- `abc123.en.vtt` (language-specific)
- `abc123.vtt` (generic)

**Sources**: [scripts/download_video.py:72-76](), [scripts/download_video.py:112-124](), [references/yt-dlp-guide.md:45-59]()

---

## Progress Monitoring

The `_progress_hook()` function at [scripts/download_video.py:156-182]() provides real-time download feedback:

```mermaid
graph TD
    A["_progress_hook(d)"] --> B{"d['status']"}
    
    B -->|"'downloading'"| C{"Has total_bytes?"}
    B -->|"'finished'"| D["Print newline<br/>Complete progress bar"]
    
    C -->|"Yes"| E["Calculate:<br/>percent = downloaded/total * 100<br/>speed = d['speed']"]
    C -->|"No"| F["Show downloaded bytes only<br/>No percentage"]
    
    E --> G["Generate progress bar:<br/>filled = int(30 * percent / 100)<br/>bar = '█' * filled + '░' * (30-filled)"]
    
    G --> H["Print with \\r:<br/>[████████░░░] 45.2% - 234MB/520MB - 5.2MB/s"]
    F --> I["Print with \\r:<br/>下载中... 234MB - 5.2MB/s"]
    
    H --> J["Overwrite same line"]
    I --> J
```

### Progress Display Format

When `total_bytes` is available:
```
[██████████████████░░░░░░░░░░] 62.4% - 324MB/520MB - 4.8MB/s
```

When only `downloaded_bytes` is available:
```
下载中... 324MB - 4.8MB/s
```

The `\r` carriage return character enables in-place updates without scrolling.

**Sources**: [scripts/download_video.py:156-182](), [scripts/utils.py]()

---

## Output File Management

### Filename Template

The `outtmpl` parameter at [scripts/download_video.py:70]() uses video ID for filenames:

```python
'outtmpl': str(output_dir / '%(id)s.%(ext)s')
```

This produces:
- Video: `Ckt1cj0xjRM.mp4`
- Subtitle: `Ckt1cj0xjRM.en.vtt`

### Benefits of ID-based Naming

Using video IDs instead of titles (documented in [TECHNICAL_NOTES.md:340-353]()):

1. **Uniqueness**: IDs are globally unique, preventing collisions
2. **Special Characters**: Avoids issues with spaces, Unicode, or special characters in titles
3. **Traceability**: Can locate original video using ID
4. **Path Safety**: No escaping or sanitization needed

### Return Value Structure

The `download_video()` function returns a dictionary at [scripts/download_video.py:142-149]():

```python
{
    'video_path': str,      # Absolute path to .mp4 file
    'subtitle_path': str,   # Absolute path to .vtt file (or None)
    'title': str,           # Original video title
    'duration': int,        # Duration in seconds
    'file_size': int,       # Video file size in bytes
    'video_id': str         # YouTube video ID
}
```

**Sources**: [scripts/download_video.py:70](), [scripts/download_video.py:142-149](), [TECHNICAL_NOTES.md:340-353]()

---

## Download Workflow

This diagram shows the complete execution flow through `download_video()`:

```mermaid
sequenceDiagram
    participant Caller
    participant download_video
    participant validate_url
    participant ensure_directory
    participant YoutubeDL
    participant extract_info
    participant _progress_hook
    participant filesystem
    
    Caller->>download_video: url, output_dir
    download_video->>validate_url: url
    validate_url-->>download_video: True/False
    
    download_video->>ensure_directory: output_dir
    ensure_directory->>filesystem: create if needed
    ensure_directory-->>download_video: Path object
    
    download_video->>YoutubeDL: ydl_opts
    download_video->>extract_info: url, download=False
    Note over extract_info: Fetch metadata only
    extract_info-->>download_video: info dict (title, duration, id)
    
    download_video->>extract_info: url, download=True
    Note over extract_info: Actual download
    
    loop Download Progress
        extract_info->>_progress_hook: status='downloading'
        _progress_hook->>Caller: Print progress bar
    end
    
    extract_info->>_progress_hook: status='finished'
    extract_info-->>download_video: info dict
    
    download_video->>filesystem: Check video_id.mp4
    download_video->>filesystem: Search for *.en.vtt
    
    filesystem-->>download_video: File paths
    download_video-->>Caller: result dict
```

**Sources**: [scripts/download_video.py:27-154]()

---

## Error Handling

The integration implements error handling at multiple levels:

### 1. URL Validation

[scripts/download_video.py:49-50]() checks URL validity before attempting download:

```python
if not validate_url(url):
    raise ValueError(f"Invalid YouTube URL: {url}")
```

### 2. Import Verification

[scripts/download_video.py:12-16]() verifies yt-dlp availability at module load:

```python
try:
    import yt_dlp
except ImportError:
    print("❌ Error: yt-dlp not installed")
    print("Please install: pip install yt-dlp")
    sys.exit(1)
```

### 3. Download Exceptions

[scripts/download_video.py:151-153]() catches and reports download failures:

```python
except Exception as e:
    print(f"\n❌ 下载失败: {str(e)}")
    raise
```

### 4. File Verification

[scripts/download_video.py:130-131]() validates that files were created:

```python
if not video_path.exists():
    raise Exception("Video file not found after download")
```

**Sources**: [scripts/download_video.py:12-16](), [scripts/download_video.py:49-50](), [scripts/download_video.py:130-131](), [scripts/download_video.py:151-153]()

---

## Common Issues and Solutions

### Issue 1: Subtitles Not Found

**Symptom**: [scripts/download_video.py:138-140]() prints warning:
```
⚠️  未找到英文字幕
提示：某些视频可能没有字幕或需要自动生成
```

**Causes**:
- Video has no English subtitles
- Subtitles disabled by uploader
- Private/restricted video

**Solutions**:
1. Check with `yt-dlp --list-subs URL`
2. Try different language: modify `subtitleslangs` in config
3. Enable auto-subtitles: `writeautomaticsub: True` (already enabled)

### Issue 2: Format Not Available

**Symptom**: yt-dlp falls back to lower quality

**Causes**:
- Requested format (1080p mp4) not available
- Video only available in WEBM or other formats

**Solutions**:
- The format string includes fallbacks: `/best[height<=1080][ext=mp4]/best`
- System automatically selects best available format
- Check available formats: `yt-dlp -F URL`

### Issue 3: Download Speed Throttling

**Symptom**: Very slow download speeds

**Causes** (from [references/yt-dlp-guide.md:259-265]()):
- YouTube rate limiting
- Network congestion
- Geographic restrictions

**Solutions**:
1. Use proxy: Set `YT_DLP_PROXY` in `.env` file
2. Rate limit: Set `YT_DLP_RATE_LIMIT` to avoid triggering throttling
3. Retry after delay: YouTube may reset limits

### Issue 4: Region Restrictions

**Symptom**: "Video unavailable" error

**Solutions**:
1. Use proxy from allowed region
2. Check video availability: `yt-dlp --geo-bypass URL`
3. Use cookies if logged in: `--cookies-from-browser chrome`

**Sources**: [scripts/download_video.py:138-140](), [references/yt-dlp-guide.md:244-283](), [TECHNICAL_NOTES.md:307-354]()

---

## Configuration via Environment Variables

While most yt-dlp settings are hardcoded in [scripts/download_video.py:65-87](), some aspects can be configured via `.env` file:

| Variable | Effect | Usage |
|----------|--------|-------|
| `YT_DLP_PROXY` | HTTP/SOCKS5 proxy | Bypass geographic restrictions |
| `YT_DLP_RATE_LIMIT` | Download speed limit | Avoid throttling (e.g., `4.2M`) |
| `MAX_VIDEO_HEIGHT` | Resolution limit | Override default 1080p |
| `OUTPUT_DIR` | Download destination | Change output directory |

These are loaded by the configuration system and can influence download behavior if the scripts are modified to read them.

**Sources**: [.env.example](), [references/yt-dlp-guide.md:130-148]()

---

## Python API vs CLI Usage

The system uses yt-dlp's Python API exclusively (not the CLI):

| Aspect | Python API | CLI |
|--------|------------|-----|
| Import | `import yt_dlp` | N/A (subprocess) |
| Usage | `YoutubeDL(opts).download(url)` | `yt-dlp [options] URL` |
| Progress | `progress_hooks` callback | STDOUT parsing |
| Error Handling | Python exceptions | Exit codes |
| Integration | Direct function calls | Subprocess management |

### Why Python API?

1. **Type Safety**: Direct access to info dictionaries with type hints
2. **Error Handling**: Python exceptions vs parsing stderr
3. **Progress Monitoring**: Callback functions vs STDOUT parsing
4. **No Subprocess**: Avoids shell escaping and platform differences
5. **Better Integration**: Can import and reuse across multiple scripts

**Sources**: [scripts/download_video.py:12](), [scripts/download_video.py:90-105](), [references/yt-dlp-guide.md:199-241]()

---

# Page: FFmpeg Integration

# FFmpeg Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/ffmpeg-guide.md](references/ffmpeg-guide.md)
- [scripts/burn_subtitles.py](scripts/burn_subtitles.py)

</details>



This document explains how FFmpeg is integrated into the YouTube Clipper Skill for video processing operations. FFmpeg is the primary external tool used for two critical functions: precise video clipping and subtitle burning to video. 

For information about FFmpeg's libass dependency, see [libass Requirement](#5.3). For the video clipping script implementation, see [clip_video.py](#4.3). For the subtitle burning script implementation, see [burn_subtitles.py](#4.4).

## Overview

FFmpeg is invoked as a subprocess from Python scripts to perform video processing operations. The system uses two distinct FFmpeg command patterns depending on the operation.

```mermaid
graph TB
    subgraph "Python Scripts"
        ClipScript["clip_video.py"]
        BurnScript["burn_subtitles.py"]
    end
    
    subgraph "FFmpeg Operations"
        ClipOp["Video Clipping<br/>Stream Copy Mode"]
        BurnOp["Subtitle Burning<br/>Video Re-encoding"]
    end
    
    subgraph "FFmpeg Binary Detection"
        DetectFunc["detect_ffmpeg_variant()"]
        CheckLibass["check_libass_support()"]
    end
    
    subgraph "FFmpeg Binaries"
        FFmpegFull["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg<br/>(macOS, with libass)"]
        FFmpegStd["ffmpeg<br/>(Standard, may lack libass)"]
    end
    
    ClipScript --> ClipOp
    BurnScript --> DetectFunc
    DetectFunc --> CheckLibass
    CheckLibass --> FFmpegFull
    CheckLibass --> FFmpegStd
    
    ClipOp --> FFmpegStd
    BurnOp --> FFmpegFull
    
    ClipOp -.->|"-ss -t -c copy"| Output1["Clipped Video<br/>(no re-encoding)"]
    BurnOp -.->|"-vf subtitles"| Output2["Video with burned subs<br/>(re-encoded)"]
```

**Sources:** [scripts/clip_video.py](), [scripts/burn_subtitles.py:19-97](), [TECHNICAL_NOTES.md:5-80]()

## Video Clipping Commands

Video clipping uses FFmpeg's stream copy mode (`-c copy`) to extract segments without re-encoding. This ensures fast processing and zero quality loss.

### Command Structure

The basic clipping command pattern is constructed in [scripts/clip_video.py]():

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `-ss` | Start time (seek position) | `120.5` (2 minutes, 0.5 seconds) |
| `-i` | Input video file | `video.mp4` |
| `-t` | Duration to extract | `180` (3 minutes) |
| `-c copy` | Copy streams without re-encoding | (flag, no value) |
| `-y` | Overwrite output file | (flag, no value) |

### Implementation

The clipping function constructs and executes the FFmpeg command:

```mermaid
flowchart TB
    Input["Input Parameters<br/>video_path, start_time, duration, output_path"]
    
    ValidateInputs["Validate Inputs<br/>Check file exists, times are valid"]
    
    BuildCmd["Build Command List<br/>cmd = ['ffmpeg', '-ss', start, '-i', video, '-t', duration, '-c', 'copy', '-y', output]"]
    
    Execute["subprocess.run(cmd)<br/>capture_output=True, text=True"]
    
    CheckRC["Check Return Code<br/>result.returncode == 0"]
    
    ValidateOutput["Validate Output File<br/>Path(output).exists()"]
    
    Success["Return output_path"]
    Error["Raise RuntimeError<br/>Print stderr"]
    
    Input --> ValidateInputs
    ValidateInputs --> BuildCmd
    BuildCmd --> Execute
    Execute --> CheckRC
    CheckRC -->|Success| ValidateOutput
    CheckRC -->|Failure| Error
    ValidateOutput --> Success
```

**Example command generated:**
```bash
ffmpeg -ss 120.5 -i input.mp4 -t 180 -c copy -y output.mp4
```

**Sources:** [scripts/clip_video.py](), [references/ffmpeg-guide.md:33-48]()

### Time Format Handling

The system accepts time in seconds as a float and passes it directly to FFmpeg. FFmpeg's `-ss` parameter supports multiple formats:

| Format | Example | Description |
|--------|---------|-------------|
| Seconds | `90.5` | 90.5 seconds |
| `HH:MM:SS` | `01:30:00` | 1 hour, 30 minutes |
| `HH:MM:SS.mmm` | `01:30:00.500` | With milliseconds |

The Python scripts use seconds (float) internally and rely on FFmpeg's automatic conversion.

**Sources:** [scripts/utils.py](), [scripts/clip_video.py]()

## Subtitle Burning Commands

Subtitle burning requires FFmpeg with libass support and uses the `subtitles` video filter. Unlike clipping, this operation re-encodes the video.

### Command Structure

The subtitle burning command is constructed in [scripts/burn_subtitles.py:194-204]():

```python
subtitle_filter = f"subtitles={temp_subtitle}:force_style='FontSize={font_size},MarginV={margin_v}'"

cmd = [
    ffmpeg_path,
    '-i', temp_video,
    '-vf', subtitle_filter,
    '-c:a', 'copy',
    '-y',
    temp_output
]
```

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `-i` | Input video file | `temp_video.mp4` |
| `-vf` | Video filter specification | `subtitles=sub.srt:force_style='FontSize=24,MarginV=30'` |
| `-c:a copy` | Copy audio stream without re-encoding | (flag with value) |
| `-y` | Overwrite output file | (flag, no value) |

### Subtitle Filter Parameters

The `subtitles` filter accepts style options via `force_style`:

| Style Parameter | Purpose | Default | Recommended Range |
|----------------|---------|---------|-------------------|
| `FontSize` | Subtitle font size in points | 24 | 20-28 (1080p) |
| `MarginV` | Vertical margin from bottom (pixels) | 30 | 20-40 |
| `FontName` | Font family name | System default | Any installed font |
| `Bold` | Bold text | 0 | 0 or 1 |

**Sources:** [scripts/burn_subtitles.py:123-244](), [references/ffmpeg-guide.md:109-133](), [TECHNICAL_NOTES.md:356-388]()

### Temporary Directory Workaround

FFmpeg's `subtitles` filter cannot handle file paths containing spaces, even when quoted or escaped. The solution is to copy files to a temporary directory with a guaranteed space-free path.

```mermaid
sequenceDiagram
    participant Script as "burn_subtitles.py"
    participant TempDir as "tempfile.mkdtemp()"
    participant FileSystem as "File System"
    participant FFmpeg as "FFmpeg Binary"
    
    Script->>TempDir: Create temp directory
    Note over TempDir: /tmp/youtube_clipper_abc123
    TempDir-->>Script: temp_dir (no spaces in path)
    
    Script->>FileSystem: shutil.copy(video_path, temp_video)
    Script->>FileSystem: shutil.copy(subtitle_path, temp_subtitle)
    
    Note over Script: Build command with temp paths
    Script->>FFmpeg: Run command with temp paths
    FFmpeg->>FileSystem: Read temp_video, temp_subtitle
    FFmpeg->>FileSystem: Write temp_output
    
    Script->>FileSystem: shutil.move(temp_output, output_path)
    Script->>FileSystem: shutil.rmtree(temp_dir)
```

**Implementation in [scripts/burn_subtitles.py:179-244]():**

1. Create temporary directory: `tempfile.mkdtemp(prefix='youtube_clipper_')`
2. Copy input files to temporary directory with simple names
3. Execute FFmpeg with space-free temporary paths
4. Move output file to final destination
5. Clean up temporary directory in `finally` block

This approach is transparent to users—they can use paths with spaces for input and output.

**Sources:** [scripts/burn_subtitles.py:179-244](), [TECHNICAL_NOTES.md:82-163]()

## FFmpeg Variant Detection

The system must detect whether FFmpeg has libass support, which is required for subtitle burning. On macOS, the standard Homebrew FFmpeg lacks libass, requiring `ffmpeg-full` instead.

### Detection Flow

```mermaid
flowchart TD
    Start["detect_ffmpeg_variant()"]
    
    CheckOS{"platform.system()<br/>== 'Darwin'"}
    
    CheckFullARM["Check Path<br/>/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
    CheckFullIntel["Check Path<br/>/usr/local/opt/ffmpeg-full/bin/ffmpeg"]
    
    TestLibassFull["check_libass_support(full_path)"]
    
    FindStd["shutil.which('ffmpeg')"]
    
    TestLibassStd["check_libass_support(standard_path)"]
    
    ReturnFull["Return<br/>{type: 'full', path: full_path, has_libass: true}"]
    ReturnStd["Return<br/>{type: 'standard'/'full', path: std_path, has_libass: bool}"]
    ReturnNone["Return<br/>{type: 'none', path: None, has_libass: false}"]
    
    Start --> CheckOS
    CheckOS -->|Yes macOS| CheckFullARM
    CheckFullARM -->|exists| TestLibassFull
    CheckFullARM -->|not exists| CheckFullIntel
    CheckFullIntel -->|exists| TestLibassFull
    CheckFullIntel -->|not exists| FindStd
    
    TestLibassFull -->|has libass| ReturnFull
    TestLibassFull -->|no libass| FindStd
    
    CheckOS -->|Not macOS| FindStd
    
    FindStd -->|found| TestLibassStd
    FindStd -->|not found| ReturnNone
    
    TestLibassStd --> ReturnStd
```

**Sources:** [scripts/burn_subtitles.py:19-70](), [TECHNICAL_NOTES.md:5-80]()

### libass Support Check

The `check_libass_support()` function verifies libass by checking for the `subtitles` filter:

**Implementation in [scripts/burn_subtitles.py:73-96]():**

```python
def check_libass_support(ffmpeg_path: str) -> bool:
    result = subprocess.run(
        [ffmpeg_path, '-filters'],
        capture_output=True,
        text=True,
        timeout=5
    )
    return 'subtitles' in result.stdout.lower()
```

The command `ffmpeg -filters` outputs all available filters. If `subtitles` appears in the output, FFmpeg was compiled with libass support.

**Sources:** [scripts/burn_subtitles.py:73-96](), [TECHNICAL_NOTES.md:59-79]()

### Installation Guidance

When libass support is missing, the system displays platform-specific installation instructions via `install_ffmpeg_full_guide()` in [scripts/burn_subtitles.py:99-121]():

| Platform | Installation Command | FFmpeg Path |
|----------|---------------------|-------------|
| macOS (Apple Silicon) | `brew install ffmpeg-full` | `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` |
| macOS (Intel) | `brew install ffmpeg-full` | `/usr/local/opt/ffmpeg-full/bin/ffmpeg` |
| Ubuntu/Debian | `sudo apt-get install ffmpeg libass-dev` | `/usr/bin/ffmpeg` |
| From source | `./configure --enable-libass && make install` | Varies |

**Sources:** [scripts/burn_subtitles.py:99-121](), [references/ffmpeg-guide.md:6-29]()

## Performance Optimization

### Stream Copy vs Re-encoding

The system uses different processing strategies based on the operation:

| Operation | Mode | Speed | Quality Impact | Command Flag |
|-----------|------|-------|----------------|--------------|
| Video clipping | Stream copy | Very fast (10-50x realtime) | None (lossless) | `-c copy` |
| Subtitle burning | Re-encoding | Slow (0.5-2x realtime) | Slight (re-compression) | `-vf subtitles` |

Stream copy (`-c copy`) is fast because it copies compressed video/audio streams directly without decoding and re-encoding. Re-encoding is necessary for subtitle burning because the video frames must be modified.

**Sources:** [scripts/clip_video.py](), [scripts/burn_subtitles.py:194-204](), [references/ffmpeg-guide.md:33-48]()

### Hardware Acceleration

FFmpeg supports hardware-accelerated encoding, though the current implementation does not use it. Potential acceleration options documented in [references/ffmpeg-guide.md:135-144]():

| Platform | Acceleration Type | FFmpeg Flag | Typical Speedup |
|----------|------------------|-------------|-----------------|
| macOS | VideoToolbox | `-hwaccel videotoolbox` | 2-4x |
| NVIDIA GPU | CUDA | `-hwaccel cuda` | 3-10x |
| Intel GPU | QSV | `-hwaccel qsv` | 2-5x |

Hardware acceleration could be added to the subtitle burning command for faster processing on supported systems.

**Sources:** [references/ffmpeg-guide.md:135-144]()

### Multi-threading

FFmpeg automatically uses multiple CPU threads, but the number can be controlled:

```bash
ffmpeg -threads 4 -i input.mp4 ...
```

The current implementation relies on FFmpeg's auto-detection (typically uses all available cores).

**Sources:** [references/ffmpeg-guide.md:147-151]()

## Common Command Patterns

### Video Clipping (Stream Copy)

**Generated by [scripts/clip_video.py]():**

```bash
ffmpeg -ss 120.5 -i input.mp4 -t 180 -c copy -y output.mp4
```

- Starts at 120.5 seconds
- Extracts 180 seconds (3 minutes)
- No re-encoding
- Fast and lossless

### Subtitle Burning (Re-encoding)

**Generated by [scripts/burn_subtitles.py:197-204]():**

```bash
ffmpeg -i video.mp4 \
  -vf "subtitles=subtitle.srt:force_style='FontSize=24,MarginV=30'" \
  -c:a copy \
  -y output.mp4
```

- Burns SRT subtitles onto video
- Re-encodes video stream
- Copies audio stream (no audio re-encoding)
- Custom subtitle style

### Bilingual Subtitle Burning

**Used for bilingual SRT files:**

```bash
ffmpeg -i video.mp4 \
  -vf "subtitles=bilingual.srt:force_style='FontSize=24,MarginV=30'" \
  -c:a copy \
  -y output.mp4
```

Each subtitle entry in the SRT contains two lines (English and target language), both rendered by FFmpeg.

**Sources:** [scripts/burn_subtitles.py:194-204](), [references/ffmpeg-guide.md:109-118](), [TECHNICAL_NOTES.md:356-388]()

## Error Handling

### Command Execution Pattern

All FFmpeg commands follow this error handling pattern:

```mermaid
flowchart TD
    BuildCmd["Build command list<br/>cmd = [ffmpeg_path, ...]"]
    
    Execute["result = subprocess.run(cmd, capture_output=True, text=True)"]
    
    CheckRC{"result.returncode<br/>== 0"}
    
    CheckOutput{"Output file<br/>exists()"}
    
    Success["Return output path"]
    
    Error1["Print command, return code, stderr<br/>Raise RuntimeError"]
    Error2["Raise RuntimeError<br/>'Output file not created'"]
    
    BuildCmd --> Execute
    Execute --> CheckRC
    CheckRC -->|Success| CheckOutput
    CheckRC -->|Failure| Error1
    CheckOutput -->|Exists| Success
    CheckOutput -->|Missing| Error2
```

**Key error information captured:**
- Command that was executed
- FFmpeg's exit code
- FFmpeg's stderr output (error messages)
- Whether output file was created

**Sources:** [scripts/clip_video.py](), [scripts/burn_subtitles.py:210-223]()

### Common Error Scenarios

| Error | Cause | Detection | Solution |
|-------|-------|-----------|----------|
| "No such filter: 'subtitles'" | FFmpeg lacks libass | `check_libass_support()` returns `False` | Install `ffmpeg-full` or compile with libass |
| "Unable to find '/path/with'" | Path contains spaces | FFmpeg stderr shows truncated path | Use temporary directory workaround |
| Return code 1 | Invalid time range | FFmpeg stderr shows error | Validate start time and duration |
| Output file not created | FFmpeg failed silently | `Path(output).exists()` returns `False` | Check FFmpeg stderr for details |

**Sources:** [scripts/burn_subtitles.py:19-97](), [TECHNICAL_NOTES.md:5-163](), [references/ffmpeg-guide.md:154-173]()

---

# Page: libass Requirement

# libass Requirement

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [install_as_skill.sh](install_as_skill.sh)
- [scripts/burn_subtitles.py](scripts/burn_subtitles.py)

</details>



This page documents the critical libass library dependency for FFmpeg-based subtitle burning functionality. libass is a subtitle rendering library that enables FFmpeg's `subtitles` filter, which is required for hardcoding subtitles into video files.

For general FFmpeg usage and integration patterns, see [FFmpeg Integration](#5.2). For the script that uses libass, see [burn_subtitles.py](#4.4). For troubleshooting subtitle burning failures, see [FFmpeg and libass Problems](#8.2).

## Purpose and Critical Role

libass is a portable subtitle renderer for the ASS (Advanced SubStation Alpha) and SSA (SubStation Alpha) subtitle formats. In the YouTube Clipper Skill, libass is essential because:

1. **Subtitle Burning Dependency**: The `subtitles` filter in FFmpeg requires libass to render subtitles onto video frames
2. **Not Included by Default**: Many FFmpeg distributions exclude libass to reduce package size
3. **No Workaround**: Without libass, subtitle burning cannot be performed—there is no alternative filter

**Key Limitation**: Standard Homebrew FFmpeg on macOS does not include libass support. Users must install `ffmpeg-full` or compile from source.

Sources: [TECHNICAL_NOTES.md:5-24]()

## System Architecture: libass in the Processing Pipeline

```mermaid
graph TB
    subgraph "User Request Layer"
        UserCmd["User Command:<br/>Burn subtitles to video"]
    end
    
    subgraph "burn_subtitles.py"
        BurnMain["burn_subtitles()<br/>Main function"]
        DetectFFmpeg["detect_ffmpeg_variant()<br/>FFmpeg detection"]
        CheckLibass["check_libass_support()<br/>libass verification"]
        InstallGuide["install_ffmpeg_full_guide()<br/>Installation instructions"]
    end
    
    subgraph "FFmpeg Variants"
        FFmpegFull["ffmpeg-full<br/>/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg<br/>✅ Includes libass"]
        FFmpegStd["ffmpeg (standard)<br/>System PATH<br/>❓ May or may not have libass"]
        FFmpegNone["No FFmpeg<br/>❌ Not installed"]
    end
    
    subgraph "libass Library"
        Libass["libass<br/>Subtitle rendering engine"]
        SubtitlesFilter["subtitles filter<br/>FFmpeg video filter"]
    end
    
    subgraph "Outputs"
        Success["Video with<br/>burned subtitles"]
        Failure["RuntimeError:<br/>FFmpeg does not support libass"]
    end
    
    UserCmd --> BurnMain
    BurnMain --> DetectFFmpeg
    DetectFFmpeg --> FFmpegFull
    DetectFFmpeg --> FFmpegStd
    DetectFFmpeg --> FFmpegNone
    
    FFmpegFull --> CheckLibass
    FFmpegStd --> CheckLibass
    FFmpegNone --> InstallGuide
    
    CheckLibass -->|"has_libass: true"| Libass
    CheckLibass -->|"has_libass: false"| InstallGuide
    
    Libass --> SubtitlesFilter
    SubtitlesFilter --> Success
    InstallGuide --> Failure
    
    style Libass fill:#f9f9f9
    style SubtitlesFilter fill:#f9f9f9
```

**Diagram: libass Dependency Chain**

This diagram shows how `burn_subtitles.py` detects FFmpeg variants and verifies libass support before attempting subtitle burning operations.

Sources: [scripts/burn_subtitles.py:19-70](), [scripts/burn_subtitles.py:123-172]()

## Detection Logic

The system implements a multi-stage detection process in `burn_subtitles.py` to locate FFmpeg with libass support:

### Detection Function Flow

```mermaid
flowchart TD
    Start["detect_ffmpeg_variant()<br/>Entry point"]
    
    CheckOS{"platform.system()<br/>== 'Darwin'?"}
    
    CheckARM["Check path:<br/>/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
    CheckIntel["Check path:<br/>/usr/local/opt/ffmpeg-full/bin/ffmpeg"]
    
    FoundFull{"Path exists?"}
    
    CheckStd["shutil.which('ffmpeg')<br/>Find in PATH"]
    
    FoundStd{"Found?"}
    
    VerifyLibass["check_libass_support(path)<br/>Run: ffmpeg -filters"]
    
    GrepSubtitles["Search output for<br/>'subtitles' filter"]
    
    HasLibass{"Filter found?"}
    
    ReturnFull["Return:<br/>{type: 'full', path: path, has_libass: true}"]
    ReturnStdYes["Return:<br/>{type: 'full', path: path, has_libass: true}"]
    ReturnStdNo["Return:<br/>{type: 'standard', path: path, has_libass: false}"]
    ReturnNone["Return:<br/>{type: 'none', path: null, has_libass: false}"]
    
    Start --> CheckOS
    CheckOS -->|Yes| CheckARM
    CheckOS -->|No| CheckStd
    
    CheckARM --> FoundFull
    CheckIntel --> FoundFull
    FoundFull -->|Yes| VerifyLibass
    FoundFull -->|No| CheckIntel
    CheckIntel --> FoundFull
    
    FoundFull -->|No from Intel| CheckStd
    
    CheckStd --> FoundStd
    FoundStd -->|Yes| VerifyLibass
    FoundStd -->|No| ReturnNone
    
    VerifyLibass --> GrepSubtitles
    GrepSubtitles --> HasLibass
    
    HasLibass -->|Yes, from full| ReturnFull
    HasLibass -->|Yes, from std| ReturnStdYes
    HasLibass -->|No| ReturnStdNo
```

**Diagram: FFmpeg Detection Algorithm**

This flowchart maps directly to the `detect_ffmpeg_variant()` function logic, showing platform-specific paths and verification steps.

Sources: [scripts/burn_subtitles.py:19-70](), [scripts/burn_subtitles.py:73-96]()

### Detection Implementation Details

The detection process consists of three key functions:

| Function | Purpose | Key Logic |
|----------|---------|-----------|
| `detect_ffmpeg_variant()` | Locate FFmpeg executable | Checks platform-specific paths, then PATH |
| `check_libass_support()` | Verify libass availability | Runs `ffmpeg -filters`, searches for "subtitles" |
| `install_ffmpeg_full_guide()` | Provide installation help | Displays platform-specific instructions |

**Priority Order (macOS)**:
1. `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` (Apple Silicon)
2. `/usr/local/opt/ffmpeg-full/bin/ffmpeg` (Intel)
3. `ffmpeg` in system PATH
4. Error if none found

**Priority Order (Other Platforms)**:
1. `ffmpeg` in system PATH
2. Error if not found

Sources: [scripts/burn_subtitles.py:32-48](), [scripts/burn_subtitles.py:50-62]()

### libass Verification Method

The `check_libass_support()` function verifies libass by checking for the `subtitles` filter:

```python
# Simplified logic from burn_subtitles.py:84-93
subprocess.run([ffmpeg_path, '-filters'], capture_output=True, text=True)
return 'subtitles' in result.stdout.lower()
```

This works because:
- The `subtitles` filter is only available when FFmpeg is compiled with libass
- Running `ffmpeg -filters` lists all available filters
- Searching for "subtitles" confirms libass support

Sources: [scripts/burn_subtitles.py:73-96]()

## Platform-Specific Installation

### macOS Installation

On macOS, the recommended approach is to install `ffmpeg-full` via Homebrew, which includes libass and other subtitle-related libraries.

```bash
# Install ffmpeg-full
brew install ffmpeg-full

# Verify installation (Apple Silicon)
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -filters 2>&1 | grep subtitles

# Verify installation (Intel)
/usr/local/opt/ffmpeg-full/bin/ffmpeg -filters 2>&1 | grep subtitles
```

**Installation Paths by Architecture**:

| Architecture | FFmpeg Path |
|-------------|-------------|
| Apple Silicon (M1/M2/M3) | `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` |
| Intel (x86_64) | `/usr/local/opt/ffmpeg-full/bin/ffmpeg` |

**Why not standard FFmpeg?**
- `brew install ffmpeg` excludes libass to minimize package size
- Standard FFmpeg cannot burn subtitles
- `ffmpeg-full` is required for this functionality

Sources: [TECHNICAL_NOTES.md:28-43](), [install_as_skill.sh:159-166]()

### Linux Installation

On Linux systems, install libass development libraries before compiling FFmpeg or use distribution packages with libass support.

#### Ubuntu/Debian

```bash
# Option 1: Install pre-built FFmpeg with libass
sudo apt-get update
sudo apt-get install ffmpeg

# Option 2: Build from source
sudo apt-get install libass-dev
./configure --enable-libass
make
sudo make install
```

#### Verification

```bash
# Check for subtitles filter
ffmpeg -filters 2>&1 | grep subtitles
```

Expected output when libass is available:
```
 ... subtitles          V->V       Render text subtitles onto input video using libass.
```

Sources: [TECHNICAL_NOTES.md:46-57]()

### Installation During Skill Setup

The installation script `install_as_skill.sh` performs automatic detection during setup:

```mermaid
graph TB
    Start["Installation Script<br/>install_as_skill.sh"]
    
    CheckPlatform{"Platform check<br/>Darwin vs Linux"}
    
    subgraph "macOS Detection"
        CheckFullARM["Check:<br/>/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
        CheckFullIntel["Check:<br/>/usr/local/opt/ffmpeg-full/bin/ffmpeg"]
        SuccessFull["✅ ffmpeg-full found<br/>LIBASS_SUPPORTED=true"]
    end
    
    subgraph "Standard FFmpeg Detection"
        CheckStdFFmpeg["command_exists ffmpeg"]
        RunFilters["ffmpeg -filters 2>&1 | grep -q 'subtitles'"]
        SuccessStd["✅ FFmpeg with libass<br/>LIBASS_SUPPORTED=true"]
        WarningStd["⚠️ FFmpeg without libass<br/>LIBASS_SUPPORTED=false"]
    end
    
    subgraph "Installation Guidance"
        ErrorMsg["❌ FFmpeg not found"]
        WarningMsg["⚠️ libass not supported"]
        ShowInstructions["Display platform-specific<br/>installation commands"]
    end
    
    Start --> CheckPlatform
    
    CheckPlatform -->|macOS| CheckFullARM
    CheckFullARM -->|Exists| SuccessFull
    CheckFullARM -->|Not found| CheckFullIntel
    CheckFullIntel -->|Exists| SuccessFull
    CheckFullIntel -->|Not found| CheckStdFFmpeg
    
    CheckPlatform -->|Linux| CheckStdFFmpeg
    
    CheckStdFFmpeg -->|Found| RunFilters
    CheckStdFFmpeg -->|Not found| ErrorMsg
    
    RunFilters -->|Match| SuccessStd
    RunFilters -->|No match| WarningStd
    
    SuccessFull --> End["Continue installation"]
    SuccessStd --> End
    WarningStd --> WarningMsg
    ErrorMsg --> ShowInstructions
    WarningMsg --> ShowInstructions
    ShowInstructions --> End
```

**Diagram: Installation Script Detection Flow**

The installation script provides immediate feedback about FFmpeg and libass availability, guiding users to install the correct variant.

Sources: [install_as_skill.sh:152-191]()

## Verification Methods

### Command-Line Verification

The most reliable verification method is to check for the `subtitles` filter:

```bash
# List all filters and search for subtitles
ffmpeg -filters 2>&1 | grep subtitles

# Expected output with libass:
# ... subtitles          V->V       Render text subtitles onto input video using libass.
#
# No output = libass not available
```

### Programmatic Verification

The `check_libass_support()` function in `burn_subtitles.py` provides programmatic verification:

```python
# From burn_subtitles.py:73-96
def check_libass_support(ffmpeg_path: str) -> bool:
    result = subprocess.run(
        [ffmpeg_path, '-filters'],
        capture_output=True,
        text=True,
        timeout=5
    )
    return 'subtitles' in result.stdout.lower()
```

This function:
1. Executes `ffmpeg -filters`
2. Captures stdout
3. Searches for "subtitles" string (case-insensitive)
4. Returns boolean result

Sources: [scripts/burn_subtitles.py:73-96]()

### Error Messages

When libass is not available, the system provides clear error messages:

| Scenario | Error Message | Location |
|----------|---------------|----------|
| FFmpeg not found | `FFmpeg not found` | [burn_subtitles.py:165]() |
| No libass support | `FFmpeg does not support libass (subtitles filter)` | [burn_subtitles.py:169]() |
| Installation needed | Displays `install_ffmpeg_full_guide()` output | [burn_subtitles.py:99-121]() |

The installation guide includes platform-specific instructions and verification commands.

Sources: [scripts/burn_subtitles.py:163-172](), [scripts/burn_subtitles.py:99-121]()

## Common Issues and Solutions

### Issue: "No such filter: 'subtitles'"

**Symptom**: FFmpeg fails with error message indicating the `subtitles` filter is not available.

**Root Cause**: FFmpeg was compiled without libass support.

**Solution**:
- **macOS**: Install `ffmpeg-full` instead of standard `ffmpeg`
- **Linux**: Install `libass-dev` and recompile FFmpeg with `--enable-libass`

Sources: [TECHNICAL_NOTES.md:10-13](), [TECHNICAL_NOTES.md:21-24]()

### Issue: Path Detection Fails on macOS

**Symptom**: Script cannot find `ffmpeg-full` even though it's installed.

**Diagnosis**: Check both possible installation paths:

```bash
# Apple Silicon
ls -la /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg

# Intel Mac
ls -la /usr/local/opt/ffmpeg-full/bin/ffmpeg
```

**Solution**: Ensure Homebrew installed to the correct location for your architecture.

Sources: [scripts/burn_subtitles.py:34-40]()

### Issue: Standard FFmpeg Reports No libass

**Symptom**: Installed FFmpeg doesn't have `subtitles` filter.

**Verification**:
```bash
ffmpeg -filters 2>&1 | grep subtitles
# No output = no libass
```

**Solutions by Platform**:

| Platform | Command |
|----------|---------|
| macOS | `brew uninstall ffmpeg && brew install ffmpeg-full` |
| Ubuntu/Debian | `sudo apt-get install libass-dev` then recompile |
| From source | Add `--enable-libass` to configure flags |

Sources: [TECHNICAL_NOTES.md:46-57](), [install_as_skill.sh:186-191]()

## Integration with burn_subtitles.py

The `burn_subtitles()` function integrates libass detection at the beginning of its execution:

```mermaid
sequenceDiagram
    participant User
    participant burn_subtitles
    participant detect_ffmpeg_variant
    participant check_libass_support
    participant FFmpeg
    participant install_guide
    
    User->>burn_subtitles: Call with video, subtitle paths
    burn_subtitles->>detect_ffmpeg_variant: Locate FFmpeg
    
    detect_ffmpeg_variant->>detect_ffmpeg_variant: Check platform-specific paths
    detect_ffmpeg_variant->>check_libass_support: Verify libass
    check_libass_support->>FFmpeg: Run: ffmpeg -filters
    FFmpeg-->>check_libass_support: Filter list
    check_libass_support-->>detect_ffmpeg_variant: has_libass: bool
    detect_ffmpeg_variant-->>burn_subtitles: {type, path, has_libass}
    
    alt libass available
        burn_subtitles->>FFmpeg: Execute subtitle burning
        FFmpeg-->>User: Video with subtitles
    else libass not available
        burn_subtitles->>install_guide: Show installation help
        install_guide-->>User: RuntimeError with instructions
    end
```

**Diagram: Runtime libass Verification Sequence**

This sequence diagram shows the function call chain when `burn_subtitles()` verifies libass availability before attempting to burn subtitles.

Sources: [scripts/burn_subtitles.py:160-172](), [scripts/burn_subtitles.py:19-70]()

### Function Call Chain

1. **User calls `burn_subtitles()`** with video and subtitle paths
2. **`detect_ffmpeg_variant()`** executes to locate FFmpeg
3. **`check_libass_support()`** verifies the `subtitles` filter exists
4. **Decision point**:
   - If libass available: proceed with FFmpeg subtitle burning
   - If libass missing: call `install_ffmpeg_full_guide()` and raise `RuntimeError`

Sources: [scripts/burn_subtitles.py:123-172]()

## Configuration Options

While libass itself has no user-configurable options in this system, the environment variables affect how FFmpeg with libass is used:

| Environment Variable | Purpose | Effect on libass |
|---------------------|---------|------------------|
| `FFMPEG_PATH` | Override FFmpeg executable path | Can point to specific FFmpeg build with libass |
| `SUBTITLE_FONT_SIZE` | Font size for burned subtitles | Passed to libass via `force_style` |
| `SUBTITLE_MARGIN_V` | Bottom margin for subtitles | Passed to libass via `force_style` |

The `burn_subtitles()` function uses these parameters when constructing the FFmpeg filter:

```python
# From burn_subtitles.py:195
subtitle_filter = f"subtitles={temp_subtitle}:force_style='FontSize={font_size},MarginV={margin_v}'"
```

These style parameters are interpreted by libass when rendering subtitles onto video frames.

Sources: [scripts/burn_subtitles.py:195]()

## Summary

libass is a non-optional dependency for subtitle burning functionality in the YouTube Clipper Skill. The system implements robust detection and provides clear installation guidance when libass is unavailable. On macOS, users must install `ffmpeg-full` rather than standard FFmpeg. The detection logic in `burn_subtitles.py` verifies libass support before attempting any subtitle burning operations, preventing cryptic FFmpeg errors.

Sources: [TECHNICAL_NOTES.md:1-57](), [scripts/burn_subtitles.py:1-287](), [install_as_skill.sh:152-191]()

---

# Page: Configuration

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)

</details>



This document describes the YouTube Clipper Skill's configuration system, which allows users to customize system behavior through environment variables. The configuration system controls video download quality, subtitle styling, translation parameters, output directories, and processing options without requiring code modifications.

For detailed reference of all available configuration variables, see [Environment Variables Reference](#6.1). For specific configuration domains, see [Video Download Settings](#6.2), [Subtitle and Translation Settings](#6.3), and [Processing and Output Settings](#6.4).

## Configuration System Overview

The YouTube Clipper Skill uses a three-tier configuration system: a template file ([.env.example:1-86]()), a user-editable file (`.env`), and hard-coded defaults in Python scripts. This design ensures the system operates correctly even without explicit configuration while allowing extensive customization for advanced users.

```mermaid
graph TB
    subgraph "Configuration Sources"
        Template[".env.example<br/>(Template)"]
        UserEnv[".env<br/>(User Configuration)"]
        Defaults["Hard-coded Defaults<br/>in Python Scripts"]
    end
    
    subgraph "Loading Mechanism"
        DotEnv["python-dotenv<br/>load_dotenv()"]
        OsGetEnv["os.getenv()<br/>with fallback"]
    end
    
    subgraph "Runtime Systems"
        Download["download_video.py"]
        Analyze["analyze_subtitles.py"]
        Clip["clip_video.py"]
        Burn["burn_subtitles.py"]
        Extract["extract_subtitle_clip.py"]
    end
    
    Template -.->|"User copies to"| UserEnv
    Defaults -.->|"Fallback if not in"| UserEnv
    
    UserEnv --> DotEnv
    DotEnv --> OsGetEnv
    
    OsGetEnv --> Download
    OsGetEnv --> Analyze
    OsGetEnv --> Clip
    OsGetEnv --> Burn
    OsGetEnv --> Extract
```

**Configuration Flow in YouTube Clipper Skill**

The configuration system loads environment variables using the `python-dotenv` library, which reads the `.env` file at skill initialization. Each Python script accesses configuration through `os.getenv()` calls with fallback default values.

**Sources:** [.env.example:1-86](), [README.md:127-154]()

## Configuration File Location

After installation, the configuration file is located at:

```
~/.claude/skills/youtube-clipper/.env
```

The installation script creates this file by copying [.env.example:1-86]() to the skill directory. Users can edit this file directly or allow Claude Code to modify it through natural language commands.

| Configuration File | Purpose | Modification |
|-------------------|---------|--------------|
| `.env.example` | Template with all available options and documentation | Read-only reference |
| `.env` | Active configuration used by scripts | User-editable |
| Python script defaults | Fallback values when `.env` entry is missing | Requires code modification |

**Sources:** [README.md:127-154](), [.env.example:1-86]()

## Configuration Categories

The configuration system organizes variables into five functional categories, each controlling specific aspects of the processing pipeline.

```mermaid
graph LR
    subgraph "Configuration Categories"
        Paths["File Paths<br/>FFMPEG_PATH<br/>OUTPUT_DIR<br/>TEMP_DIR"]
        
        Video["Video Settings<br/>MAX_VIDEO_HEIGHT<br/>YT_DLP_PROXY<br/>YT_DLP_RATE_LIMIT"]
        
        Subtitles["Subtitle Settings<br/>SUBTITLE_FONT_SIZE<br/>SUBTITLE_MARGIN_V<br/>TARGET_LANGUAGE<br/>TRANSLATION_BATCH_SIZE"]
        
        Processing["Processing Settings<br/>TARGET_CHAPTER_DURATION<br/>KEEP_TEMP_FILES"]
        
        Logging["Logging Settings<br/>LOG_LEVEL"]
    end
    
    subgraph "Python Scripts"
        DownloadPy["download_video.py"]
        AnalyzePy["analyze_subtitles.py"]
        ClipPy["clip_video.py"]
        BurnPy["burn_subtitles.py"]
        ExtractPy["extract_subtitle_clip.py"]
    end
    
    Paths --> DownloadPy
    Paths --> BurnPy
    Paths --> ClipPy
    
    Video --> DownloadPy
    
    Subtitles --> BurnPy
    Subtitles --> ExtractPy
    
    Processing --> AnalyzePy
    Processing --> DownloadPy
    
    Logging --> DownloadPy
    Logging --> AnalyzePy
    Logging --> ClipPy
    Logging --> BurnPy
    Logging --> ExtractPy
```

**Configuration Category to Script Mapping**

Each configuration category affects specific Python scripts. For example, `SUBTITLE_FONT_SIZE` and `SUBTITLE_MARGIN_V` are only used by `burn_subtitles.py`, while `MAX_VIDEO_HEIGHT` is exclusively consumed by `download_video.py`.

**Sources:** [.env.example:1-86](), Diagram 5 from high-level architecture

### File Paths Configuration

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `FFMPEG_PATH` | Explicit path to FFmpeg binary | Auto-detected | `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` |
| `OUTPUT_DIR` | Base directory for all outputs | `./youtube-clips` | `/Users/username/Videos/clips` |
| `TEMP_DIR` | Temporary file storage (workaround for path spaces) | System temp directory | `/tmp/youtube-clipper` |

**Sources:** [.env.example:8-23]()

### Video Settings Configuration

| Variable | Purpose | Default | Valid Values |
|----------|---------|---------|--------------|
| `MAX_VIDEO_HEIGHT` | Maximum video resolution for download | `1080` | `720`, `1080`, `1440`, `2160` |
| `YT_DLP_PROXY` | Proxy server for yt-dlp downloads | Empty (no proxy) | `http://proxy:port`, `socks5://proxy:port` |
| `YT_DLP_RATE_LIMIT` | Download speed limit | Empty (unlimited) | `50K`, `4.2M` |

**Sources:** [.env.example:25-28](), [.env.example:50-59]()

### Subtitle and Translation Configuration

| Variable | Purpose | Default | Valid Values |
|----------|---------|---------|--------------|
| `SUBTITLE_FONT_SIZE` | Font size for burned subtitles | `24` | Any positive integer |
| `SUBTITLE_MARGIN_V` | Vertical margin from bottom (pixels) | `30` | Any positive integer |
| `TARGET_LANGUAGE` | Translation target language | `中文` (Chinese) | Any language name |
| `TRANSLATION_BATCH_SIZE` | Number of subtitle lines per API call | `20` | `15-25` recommended |

**Sources:** [.env.example:14-16](), [.env.example:32-39]()

### Processing Configuration

| Variable | Purpose | Default | Valid Values |
|----------|---------|---------|--------------|
| `TARGET_CHAPTER_DURATION` | Desired chapter length in seconds | `180` (3 minutes) | `180-300` recommended |
| `KEEP_TEMP_FILES` | Retain temporary files for debugging | `false` | `true`, `false` |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

**Sources:** [.env.example:44-47](), [.env.example:63-75]()

## Configuration Template Structure

The [.env.example:1-86]() file serves as both a template and documentation reference. Its structure demonstrates the organization and available options:

```mermaid
graph TB
    EnvExample[".env.example"]
    
    subgraph "File Structure"
        Header["Header Comments<br/>Lines 1-2"]
        
        FFmpegSection["FFmpeg Configuration<br/>Lines 4-17"]
        OutputSection["Output Configuration<br/>Lines 19-27"]
        TranslationSection["Subtitle Translation<br/>Lines 29-39"]
        ChapterSection["Chapter Analysis<br/>Lines 41-47"]
        YtDlpSection["yt-dlp Configuration<br/>Lines 49-59"]
        AdvancedSection["Advanced Configuration<br/>Lines 61-75"]
        NotesSection["Usage Notes<br/>Lines 77-86"]
    end
    
    EnvExample --> Header
    EnvExample --> FFmpegSection
    EnvExample --> OutputSection
    EnvExample --> TranslationSection
    EnvExample --> ChapterSection
    EnvExample --> YtDlpSection
    EnvExample --> AdvancedSection
    EnvExample --> NotesSection
    
    FFmpegSection -.->|"Used by"| BurnScript["burn_subtitles.py"]
    OutputSection -.->|"Used by"| AllScripts["All scripts"]
    TranslationSection -.->|"Used by"| ExtractScript["extract_subtitle_clip.py"]
    ChapterSection -.->|"Used by"| AnalyzeScript["analyze_subtitles.py"]
    YtDlpSection -.->|"Used by"| DownloadScript["download_video.py"]
```

**Configuration Template Organization**

Each section in `.env.example` groups related variables and includes:
- Descriptive comments explaining purpose
- Default values or "leave empty" guidance
- Valid value ranges or examples
- Platform-specific path examples

**Sources:** [.env.example:1-86]()

## Configuration Loading Mechanism

The configuration system uses a two-stage loading process implemented through the `python-dotenv` library:

```mermaid
sequenceDiagram
    participant Script as "Python Script<br/>(e.g., download_video.py)"
    participant DotEnv as "python-dotenv<br/>load_dotenv()"
    participant EnvFile as ".env File"
    participant OsEnv as "os.getenv()"
    participant Default as "Fallback Default"
    
    Script->>DotEnv: Import and call load_dotenv()
    DotEnv->>EnvFile: Read ~/.claude/skills/youtube-clipper/.env
    EnvFile->>DotEnv: Return KEY=VALUE pairs
    DotEnv->>OsEnv: Load into environment
    
    Script->>OsEnv: os.getenv('MAX_VIDEO_HEIGHT', '1080')
    
    alt Variable exists in .env
        OsEnv->>Script: Return configured value
    else Variable not in .env
        OsEnv->>Default: Use fallback value
        Default->>Script: Return default ('1080')
    end
```

**Configuration Loading Sequence**

Each Python script imports `python-dotenv` and calls `load_dotenv()` early in execution. This reads the `.env` file and populates environment variables. Subsequent `os.getenv()` calls retrieve values with fallback defaults if the variable is not defined.

**Sources:** [.env.example:1-86](), README context

## Modifying Configuration

Configuration changes require editing the `.env` file. Changes take effect on the next skill invocation, as configuration is loaded at script startup.

### Edit Configuration Manually

```bash
# Open configuration file in editor
nano ~/.claude/skills/youtube-clipper/.env

# Or use your preferred editor
code ~/.claude/skills/youtube-clipper/.env
```

### Edit Through Claude Code

Users can request configuration changes through natural language:

```
Change the maximum video quality to 720p
```

```
Set the translation batch size to 25
```

Claude Code will modify the `.env` file accordingly and confirm the change.

### Configuration Syntax Rules

The `.env` file follows these syntax conventions:

| Rule | Example | Notes |
|------|---------|-------|
| No quotes needed for values | `MAX_VIDEO_HEIGHT=1080` | Values are read as-is |
| Empty values are valid | `FFMPEG_PATH=` | Triggers auto-detection or uses default |
| Comments start with `#` | `# This is a comment` | Ignored by parser |
| Tilde expansion supported | `OUTPUT_DIR=~/Videos/clips` | Expands to user home directory |
| No spaces around `=` | `LOG_LEVEL=INFO` (correct) | `LOG_LEVEL = INFO` may cause issues |

**Sources:** [.env.example:77-86]()

## Configuration Validation and Defaults

The system implements a robust default mechanism ensuring operation without explicit configuration:

```mermaid
graph TD
    Start["Script Execution Starts"]
    LoadEnv["Load .env file<br/>using load_dotenv()"]
    
    CheckVar{"Variable<br/>defined in .env?"}
    UseConfigured["Use configured value"]
    UseDefault["Use hard-coded default"]
    
    ValidateType{"Type validation<br/>passes?"}
    ValidateRange{"Value in<br/>valid range?"}
    
    ApplyValue["Apply configuration value"]
    LogWarning["Log warning message"]
    FallbackDefault["Fall back to default"]
    
    Start --> LoadEnv
    LoadEnv --> CheckVar
    
    CheckVar -->|Yes| UseConfigured
    CheckVar -->|No| UseDefault
    
    UseConfigured --> ValidateType
    ValidateType -->|Yes| ValidateRange
    ValidateType -->|No| LogWarning
    
    ValidateRange -->|Yes| ApplyValue
    ValidateRange -->|No| LogWarning
    
    LogWarning --> FallbackDefault
    UseDefault --> ApplyValue
    FallbackDefault --> ApplyValue
```

**Configuration Validation Flow**

Scripts perform type checking and range validation on configuration values. Invalid values trigger warning messages and fall back to defaults, ensuring the system continues operating even with malformed configuration.

### Example Default Values

Common defaults used throughout the system:

```python
# Example from download_video.py (conceptual)
max_height = os.getenv('MAX_VIDEO_HEIGHT', '1080')
output_dir = os.getenv('OUTPUT_DIR', './youtube-clips')
proxy = os.getenv('YT_DLP_PROXY', '')  # Empty string means no proxy

# Example from burn_subtitles.py (conceptual)
font_size = int(os.getenv('SUBTITLE_FONT_SIZE', '24'))
margin_v = int(os.getenv('SUBTITLE_MARGIN_V', '30'))

# Example from analyze_subtitles.py (conceptual)
target_duration = int(os.getenv('TARGET_CHAPTER_DURATION', '180'))
```

**Sources:** [.env.example:1-86](), script module descriptions from architecture

## Configuration Impact Summary

The table below summarizes which configuration variables affect which processing stages:

| Processing Stage | Configuration Variables Used | Critical Variables |
|------------------|----------------------------|-------------------|
| Environment Detection | `FFMPEG_PATH`, `LOG_LEVEL` | `FFMPEG_PATH` (if not auto-detected) |
| Video Download | `MAX_VIDEO_HEIGHT`, `YT_DLP_PROXY`, `YT_DLP_RATE_LIMIT`, `OUTPUT_DIR` | `MAX_VIDEO_HEIGHT`, `OUTPUT_DIR` |
| AI Chapter Analysis | `TARGET_CHAPTER_DURATION`, `LOG_LEVEL` | `TARGET_CHAPTER_DURATION` |
| Video Clipping | `OUTPUT_DIR`, `TEMP_DIR`, `LOG_LEVEL` | `OUTPUT_DIR` |
| Subtitle Translation | `TRANSLATION_BATCH_SIZE`, `TARGET_LANGUAGE` | `TARGET_LANGUAGE` |
| Subtitle Burning | `FFMPEG_PATH`, `SUBTITLE_FONT_SIZE`, `SUBTITLE_MARGIN_V`, `TEMP_DIR` | `SUBTITLE_FONT_SIZE`, `SUBTITLE_MARGIN_V` |
| Output Organization | `OUTPUT_DIR`, `KEEP_TEMP_FILES` | `OUTPUT_DIR` |

Variables marked as "Critical" have the most significant impact on output quality or functionality. Non-critical variables primarily affect performance, logging, or convenience features.

**Sources:** [.env.example:1-86](), Diagram 5 from high-level architecture, [README.md:127-154]()

---

For detailed documentation of each configuration variable, proceed to [Environment Variables Reference](#6.1). For domain-specific configuration guidance, see [Video Download Settings](#6.2), [Subtitle and Translation Settings](#6.3), or [Processing and Output Settings](#6.4).

---

# Page: Environment Variables Reference

# Environment Variables Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)

</details>



This page provides a comprehensive reference for all environment variables used by the YouTube Clipper Skill. These variables are configured in the `.env` file located at `~/.claude/skills/youtube-clipper/.env` and control various aspects of video processing, subtitle handling, output management, and external tool integration.

For conceptual information about specific configuration categories, see:
- [Video Download Settings](#6.2) for video quality and download behavior
- [Subtitle and Translation Settings](#6.3) for subtitle styling and translation
- [Processing and Output Settings](#6.4) for chapter duration and file management

**Sources:** [.env.example:1-86]()

---

## Configuration Loading Mechanism

```mermaid
flowchart TB
    EnvExample[".env.example<br/>Template File"]
    EnvFile[".env<br/>User Configuration"]
    DotenvLib["python-dotenv<br/>Library"]
    
    subgraph "Python Scripts"
        Download["download_video.py"]
        Analyze["analyze_subtitles.py"]
        Clip["clip_video.py"]
        Burn["burn_subtitles.py"]
        Extract["extract_subtitle_clip.py"]
    end
    
    subgraph "Configuration Access"
        OsEnviron["os.environ.get()"]
        Defaults["Hard-coded Defaults"]
    end
    
    EnvExample -.->|"Template for"| EnvFile
    EnvFile --> DotenvLib
    DotenvLib --> OsEnviron
    Defaults -.->|"Fallback when<br/>variable not set"| OsEnviron
    
    OsEnviron --> Download
    OsEnviron --> Analyze
    OsEnviron --> Clip
    OsEnviron --> Burn
    OsEnviron --> Extract
```

All scripts use `python-dotenv` to load environment variables from the `.env` file. If a variable is not defined, scripts fall back to hard-coded default values. The `.env.example` file serves as a template showing all available configuration options.

**Sources:** [.env.example:1-86](), [README.md:127-153]()

---

## Variable Reference by Category

### FFmpeg Configuration

```mermaid
graph LR
    subgraph "FFmpeg Variables"
        FFMPEG_PATH["FFMPEG_PATH"]
        SUBTITLE_FONT_SIZE["SUBTITLE_FONT_SIZE"]
        SUBTITLE_MARGIN_V["SUBTITLE_MARGIN_V"]
    end
    
    subgraph "Scripts Using FFmpeg Config"
        ClipVideo["clip_video.py"]
        BurnSubs["burn_subtitles.py"]
    end
    
    FFMPEG_PATH --> ClipVideo
    FFMPEG_PATH --> BurnSubs
    SUBTITLE_FONT_SIZE --> BurnSubs
    SUBTITLE_MARGIN_V --> BurnSubs
```

**Sources:** [.env.example:4-17]()

#### FFMPEG_PATH

| Attribute | Value |
|-----------|-------|
| **Purpose** | Specifies the path to the FFmpeg executable |
| **Type** | String (file path) |
| **Default** | Auto-detected by searching system PATH |
| **Valid Values** | Absolute path to FFmpeg binary |
| **Used By** | `clip_video.py`, `burn_subtitles.py` |
| **Example** | `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` (macOS Apple Silicon)<br>`/usr/local/opt/ffmpeg-full/bin/ffmpeg` (macOS Intel)<br>`/usr/bin/ffmpeg` (Linux) |

**When to Set:** Only required if FFmpeg is not in the system PATH or if you need to use a specific FFmpeg installation (e.g., `ffmpeg-full` on macOS for libass support).

**Sources:** [.env.example:8-12]()

#### SUBTITLE_FONT_SIZE

| Attribute | Value |
|-----------|-------|
| **Purpose** | Controls the font size of burned-in subtitles |
| **Type** | Integer |
| **Default** | `24` |
| **Valid Values** | Any positive integer (recommended: 18-30) |
| **Used By** | `burn_subtitles.py` |
| **Example** | `24` |

**Impact:** Larger values make subtitles more readable but take up more screen space. Smaller values reduce visibility on high-resolution videos.

**Sources:** [.env.example:14-15]()

#### SUBTITLE_MARGIN_V

| Attribute | Value |
|-----------|-------|
| **Purpose** | Sets the vertical margin (bottom padding) for burned-in subtitles |
| **Type** | Integer (pixels) |
| **Default** | `30` |
| **Valid Values** | Any positive integer (recommended: 20-50) |
| **Used By** | `burn_subtitles.py` |
| **Example** | `30` |

**Impact:** Higher values move subtitles further from the bottom edge of the video. Useful to avoid overlapping with video content.

**Sources:** [.env.example:14-16]()

---

### Output Configuration

```mermaid
graph LR
    subgraph "Output Variables"
        OUTPUT_DIR["OUTPUT_DIR"]
        MAX_VIDEO_HEIGHT["MAX_VIDEO_HEIGHT"]
    end
    
    subgraph "Scripts Using Output Config"
        Download["download_video.py"]
        AllScripts["All processing scripts"]
    end
    
    OUTPUT_DIR --> AllScripts
    MAX_VIDEO_HEIGHT --> Download
```

**Sources:** [.env.example:18-28]()

#### OUTPUT_DIR

| Attribute | Value |
|-----------|-------|
| **Purpose** | Defines the base directory for all output files |
| **Type** | String (directory path) |
| **Default** | `./youtube-clips` (relative to current working directory) |
| **Valid Values** | Any valid directory path (absolute or relative) |
| **Used By** | All scripts that generate output files |
| **Example** | `./youtube-clips`<br>`~/Videos/youtube-clips`<br>`/tmp/clips` |

**Directory Structure:** Each processing session creates a timestamped subdirectory under `OUTPUT_DIR` in the format `YYYYMMDD_HHMMSS/`.

**Sources:** [.env.example:22-23]()

#### MAX_VIDEO_HEIGHT

| Attribute | Value |
|-----------|-------|
| **Purpose** | Limits the maximum video resolution for downloads |
| **Type** | Integer (pixels) |
| **Default** | `1080` |
| **Valid Values** | `720`, `1080`, `1440`, `2160` |
| **Used By** | `download_video.py` |
| **Example** | `1080` |

**Impact:** Higher values download better quality but larger files. The actual resolution depends on what YouTube provides; this is an upper limit.

**Sources:** [.env.example:25-27]()

---

### Translation Configuration

```mermaid
graph TB
    subgraph "Translation Variables"
        BATCH_SIZE["TRANSLATION_BATCH_SIZE"]
        TARGET_LANG["TARGET_LANGUAGE"]
    end
    
    subgraph "Translation Pipeline"
        Extract["extract_subtitle_clip.py"]
        AITranslate["Claude AI Translation"]
        BilingualSRT["Bilingual SRT Output"]
    end
    
    BATCH_SIZE --> AITranslate
    TARGET_LANG --> AITranslate
    Extract --> AITranslate
    AITranslate --> BilingualSRT
```

**Sources:** [.env.example:29-40]()

#### TRANSLATION_BATCH_SIZE

| Attribute | Value |
|-----------|-------|
| **Purpose** | Number of subtitle lines to translate in a single API call |
| **Type** | Integer |
| **Default** | `20` |
| **Valid Values** | 1-50 (recommended: 20-25) |
| **Used By** | Translation batching logic in subtitle processing |
| **Example** | `20` |

**Optimization:** The batch translation strategy reduces API calls by ~95%. Larger batches are more efficient but may hit API limits. Smaller batches provide better error recovery.

**Trade-offs:**
- **Smaller (10-15):** More API calls, slower processing, better error isolation
- **Recommended (20-25):** Optimal balance of efficiency and reliability
- **Larger (30-50):** Fewer API calls, but higher risk of timeout or context loss

**Sources:** [.env.example:33-35]()

#### TARGET_LANGUAGE

| Attribute | Value |
|-----------|-------|
| **Purpose** | Specifies the target language for subtitle translation |
| **Type** | String |
| **Default** | `中文` (Chinese) |
| **Valid Values** | Any language name that Claude AI understands |
| **Used By** | Translation prompt construction in subtitle processing |
| **Example** | `中文`, `日语`, `韩语`, `西班牙语`, `Français` |

**Format:** The bilingual subtitle output always includes English as the first line and the target language as the second line for each subtitle entry.

**Sources:** [.env.example:37-39]()

---

### Chapter Analysis Configuration

```mermaid
graph LR
    subgraph "Chapter Variables"
        TARGET_DURATION["TARGET_CHAPTER_DURATION"]
    end
    
    subgraph "Analysis Pipeline"
        AnalyzeScript["analyze_subtitles.py"]
        ClaudeAI["Claude AI<br/>Semantic Analysis"]
        ChapterOutput["Chapter JSON"]
    end
    
    TARGET_DURATION --> AnalyzeScript
    AnalyzeScript --> ClaudeAI
    ClaudeAI --> ChapterOutput
```

**Sources:** [.env.example:41-48]()

#### TARGET_CHAPTER_DURATION

| Attribute | Value |
|-----------|-------|
| **Purpose** | Guides the AI to generate chapters of approximately this duration |
| **Type** | Integer (seconds) |
| **Default** | `180` (3 minutes) |
| **Valid Values** | 60-600 (recommended: 180-300) |
| **Used By** | `analyze_subtitles.py` |
| **Example** | `180` (3 minutes)<br>`240` (4 minutes)<br>`300` (5 minutes) |

**Behavior:** This is a target, not a strict limit. The AI will prioritize semantic coherence over exact duration, creating chapters at natural topic boundaries.

**Impact:**
- **Shorter (60-120s):** More granular chapters, suitable for highlight reels
- **Medium (180-300s):** Balanced chapters, good for general content
- **Longer (300-600s):** Fewer, more comprehensive chapters

**Sources:** [.env.example:45-47]()

---

### yt-dlp Configuration

```mermaid
graph LR
    subgraph "yt-dlp Variables"
        PROXY["YT_DLP_PROXY"]
        RATE_LIMIT["YT_DLP_RATE_LIMIT"]
    end
    
    subgraph "Download Process"
        DownloadScript["download_video.py"]
        YtDlpLib["yt_dlp library"]
        YouTube["YouTube"]
    end
    
    PROXY --> DownloadScript
    RATE_LIMIT --> DownloadScript
    DownloadScript --> YtDlpLib
    YtDlpLib -->|"Through proxy"| YouTube
```

**Sources:** [.env.example:49-60]()

#### YT_DLP_PROXY

| Attribute | Value |
|-----------|-------|
| **Purpose** | Routes download traffic through a proxy server |
| **Type** | String (URL) |
| **Default** | Empty (no proxy) |
| **Valid Values** | `http://host:port`<br>`https://host:port`<br>`socks5://host:port` |
| **Used By** | `download_video.py` |
| **Example** | `http://proxy.example.com:8080`<br>`socks5://127.0.0.1:1080` |

**Use Cases:**
- Bypass geographic restrictions
- Improve download speeds in restricted networks
- Route through corporate proxies

**Sources:** [.env.example:53-55]()

#### YT_DLP_RATE_LIMIT

| Attribute | Value |
|-----------|-------|
| **Purpose** | Limits the download speed to avoid network congestion or rate limiting |
| **Type** | String (bandwidth) |
| **Default** | Empty (unlimited) |
| **Valid Values** | Format: `<number><unit>` where unit is `K` (KB/s) or `M` (MB/s) |
| **Used By** | `download_video.py` |
| **Example** | `50K` (50 KB/s)<br>`4.2M` (4.2 MB/s)<br>`1M` (1 MB/s) |

**Use Cases:**
- Prevent bandwidth saturation on slow connections
- Comply with network usage policies
- Background downloading without disrupting other activities

**Sources:** [.env.example:57-59]()

---

### Advanced Configuration

```mermaid
graph TB
    subgraph "Advanced Variables"
        TEMP_DIR["TEMP_DIR"]
        KEEP_TEMP["KEEP_TEMP_FILES"]
        LOG_LEVEL["LOG_LEVEL"]
    end
    
    subgraph "System Behavior"
        TempFiles["Temporary File<br/>Management"]
        Logging["Logging System"]
        Cleanup["File Cleanup"]
    end
    
    TEMP_DIR --> TempFiles
    KEEP_TEMP --> Cleanup
    LOG_LEVEL --> Logging
    
    TempFiles --> Cleanup
```

**Sources:** [.env.example:61-76]()

#### TEMP_DIR

| Attribute | Value |
|-----------|-------|
| **Purpose** | Specifies a custom directory for temporary files (workaround for paths with spaces) |
| **Type** | String (directory path) |
| **Default** | System default temporary directory |
| **Valid Values** | Any valid directory path without spaces |
| **Used By** | `burn_subtitles.py` |
| **Example** | `/tmp/youtube-clipper`<br>`~/temp` |

**Critical Use Case:** On systems where the default temporary directory path contains spaces, FFmpeg's subtitle filter may fail. Setting a space-free `TEMP_DIR` resolves this issue.

**Sources:** [.env.example:65-67]()

#### KEEP_TEMP_FILES

| Attribute | Value |
|-----------|-------|
| **Purpose** | Controls whether temporary files are retained after processing |
| **Type** | Boolean |
| **Default** | `false` |
| **Valid Values** | `true`, `false` |
| **Used By** | All scripts that create temporary files |
| **Example** | `false` |

**Debugging:** Set to `true` to inspect intermediate processing files when troubleshooting issues. Remember to manually clean up temporary files when debugging is complete.

**Sources:** [.env.example:69-71]()

#### LOG_LEVEL

| Attribute | Value |
|-----------|-------|
| **Purpose** | Controls the verbosity of logging output |
| **Type** | String (log level name) |
| **Default** | `INFO` |
| **Valid Values** | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| **Used By** | All scripts (if logging is implemented) |
| **Example** | `INFO` |

**Log Levels:**
- **DEBUG:** Detailed diagnostic information, useful for development and troubleshooting
- **INFO:** Confirmation that things are working as expected (default)
- **WARNING:** Indication of potential issues that don't prevent operation
- **ERROR:** Serious problems that may prevent some functionality

**Sources:** [.env.example:73-75]()

---

## Environment Variable Usage Map

This diagram shows which scripts access which environment variables:

```mermaid
graph TB
    subgraph "Scripts"
        DV["download_video.py"]
        AS["analyze_subtitles.py"]
        CV["clip_video.py"]
        BS["burn_subtitles.py"]
        ESC["extract_subtitle_clip.py"]
    end
    
    subgraph "Path Variables"
        FFMPEG["FFMPEG_PATH"]
        OUTPUT["OUTPUT_DIR"]
        TEMP["TEMP_DIR"]
    end
    
    subgraph "Video Variables"
        HEIGHT["MAX_VIDEO_HEIGHT"]
        PROXY["YT_DLP_PROXY"]
        RATE["YT_DLP_RATE_LIMIT"]
    end
    
    subgraph "Subtitle Variables"
        FONTSIZE["SUBTITLE_FONT_SIZE"]
        MARGIN["SUBTITLE_MARGIN_V"]
        BATCHSIZE["TRANSLATION_BATCH_SIZE"]
        LANG["TARGET_LANGUAGE"]
    end
    
    subgraph "Processing Variables"
        DURATION["TARGET_CHAPTER_DURATION"]
        KEEP["KEEP_TEMP_FILES"]
        LOGLEVEL["LOG_LEVEL"]
    end
    
    HEIGHT --> DV
    PROXY --> DV
    RATE --> DV
    OUTPUT --> DV
    
    DURATION --> AS
    OUTPUT --> AS
    
    FFMPEG --> CV
    OUTPUT --> CV
    
    FFMPEG --> BS
    FONTSIZE --> BS
    MARGIN --> BS
    TEMP --> BS
    OUTPUT --> BS
    
    BATCHSIZE --> ESC
    LANG --> ESC
    OUTPUT --> ESC
    
    KEEP -.-> DV
    KEEP -.-> CV
    KEEP -.-> BS
    KEEP -.-> ESC
    
    LOGLEVEL -.-> DV
    LOGLEVEL -.-> AS
    LOGLEVEL -.-> CV
    LOGLEVEL -.-> BS
    LOGLEVEL -.-> ESC
```

**Note:** Dashed lines indicate optional variables that may be checked but have universal fallback defaults.

**Sources:** [.env.example:1-86](), [README.md:127-153]()

---

## Configuration File Structure

The `.env` file follows a standard key-value format with sections for organizational clarity:

| Section | Variables | Purpose |
|---------|-----------|---------|
| **FFmpeg Configuration** | `FFMPEG_PATH`, `SUBTITLE_FONT_SIZE`, `SUBTITLE_MARGIN_V` | Video processing and subtitle rendering |
| **Output Configuration** | `OUTPUT_DIR`, `MAX_VIDEO_HEIGHT` | File destinations and video quality |
| **Translation Configuration** | `TRANSLATION_BATCH_SIZE`, `TARGET_LANGUAGE` | Subtitle translation behavior |
| **Chapter Analysis Configuration** | `TARGET_CHAPTER_DURATION` | AI chapter generation guidance |
| **yt-dlp Configuration** | `YT_DLP_PROXY`, `YT_DLP_RATE_LIMIT` | Download behavior and network routing |
| **Advanced Configuration** | `TEMP_DIR`, `KEEP_TEMP_FILES`, `LOG_LEVEL` | System behavior and debugging |

**Syntax Rules:**
- One variable per line in the format `KEY=value`
- No quotes needed around values
- Empty values are treated as unset (system will use defaults)
- Lines starting with `#` are comments and ignored
- Tilde (`~`) expands to user home directory in paths

**Sources:** [.env.example:1-86]()

---

## Default Values Summary

| Variable | Default Value | Fallback Behavior |
|----------|--------------|-------------------|
| `FFMPEG_PATH` | Auto-detected | Searches system PATH for `ffmpeg` |
| `SUBTITLE_FONT_SIZE` | `24` | Hard-coded in `burn_subtitles.py` |
| `SUBTITLE_MARGIN_V` | `30` | Hard-coded in `burn_subtitles.py` |
| `OUTPUT_DIR` | `./youtube-clips` | Uses current working directory |
| `MAX_VIDEO_HEIGHT` | `1080` | Hard-coded in `download_video.py` |
| `TRANSLATION_BATCH_SIZE` | `20` | Hard-coded in translation logic |
| `TARGET_LANGUAGE` | `中文` | Hard-coded in translation prompt |
| `TARGET_CHAPTER_DURATION` | `180` | Hard-coded in `analyze_subtitles.py` |
| `YT_DLP_PROXY` | Empty | No proxy used |
| `YT_DLP_RATE_LIMIT` | Empty | No speed limit |
| `TEMP_DIR` | System default | Uses Python's `tempfile.gettempdir()` |
| `KEEP_TEMP_FILES` | `false` | Temporary files deleted after processing |
| `LOG_LEVEL` | `INFO` | Standard logging verbosity |

**Sources:** [.env.example:1-86](), [README.md:133-151]()

---

## Platform-Specific Recommendations

### macOS (Apple Silicon)

```bash
# Recommended FFmpeg path
FFMPEG_PATH=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg

# Typical output directory
OUTPUT_DIR=~/Videos/youtube-clips

# Higher quality on newer hardware
MAX_VIDEO_HEIGHT=1080
```

### macOS (Intel)

```bash
# Recommended FFmpeg path
FFMPEG_PATH=/usr/local/opt/ffmpeg-full/bin/ffmpeg

# Typical output directory
OUTPUT_DIR=~/Videos/youtube-clips

# Higher quality on newer hardware
MAX_VIDEO_HEIGHT=1080
```

### Linux (Ubuntu/Debian)

```bash
# Default FFmpeg path (usually auto-detected)
FFMPEG_PATH=/usr/bin/ffmpeg

# Typical output directory
OUTPUT_DIR=~/Videos/youtube-clips

# Adjust based on system resources
MAX_VIDEO_HEIGHT=1080
```

**Sources:** [.env.example:8-12](), [README.md:54-83]()

---

## Configuration Validation

The system does not perform explicit validation of environment variables at startup. Invalid values may cause runtime errors during processing. Common issues:

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Invalid `FFMPEG_PATH` | "FFmpeg not found" error | Verify path exists and is executable |
| Invalid `MAX_VIDEO_HEIGHT` | Download fails or uses wrong quality | Use only: 720, 1080, 1440, 2160 |
| Invalid `TRANSLATION_BATCH_SIZE` | API errors or slow translation | Keep between 10-30 |
| Invalid `LOG_LEVEL` | No effect or errors | Use: DEBUG, INFO, WARNING, ERROR |
| Spaces in `TEMP_DIR` | Subtitle burning fails | Use path without spaces |

**Sources:** [README.md:236-278]()

---

# Page: Video Download Settings

# Video Download Settings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [scripts/download_video.py](scripts/download_video.py)

</details>



This document describes the configuration options that control video downloading behavior in the YouTube Clipper Skill. These settings affect video quality, network routing, and download speed management.

For general environment variable configuration, see [Environment Variables Reference](#6.1). For subtitle-related configuration, see [Subtitle and Translation Settings](#6.3). For output directory and processing settings, see [Processing and Output Settings](#6.4).

## Configuration Overview

The video download system uses three primary environment variables to control the download process executed by `download_video.py`. These variables are read from the `.env` file and passed to the yt-dlp library.

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `MAX_VIDEO_HEIGHT` | Integer | 1080 | Maximum video resolution height in pixels |
| `YT_DLP_PROXY` | String | Empty | HTTP/SOCKS5 proxy server for network requests |
| `YT_DLP_RATE_LIMIT` | String | Empty | Download speed limit (e.g., "50K", "4.2M") |

**Sources:** [.env.example:25-59]()

## Video Quality Control

### MAX_VIDEO_HEIGHT

The `MAX_VIDEO_HEIGHT` variable controls the maximum vertical resolution of downloaded videos. This setting is implemented in the format selection string passed to yt-dlp.

**Valid Values:**
- `720` - HD (1280x720)
- `1080` - Full HD (1920x1080)
- `1440` - 2K (2560x1440)
- `2160` - 4K (3840x2160)

**Configuration:**
```bash
# .env file
MAX_VIDEO_HEIGHT=1080
```

### Implementation

The quality setting is translated into a yt-dlp format selector in the `download_video.py` script. The format string specifies:

1. Best video stream with height ≤ MAX_VIDEO_HEIGHT in mp4 format
2. Best audio stream in m4a format
3. Fallback to best combined format if separate streams unavailable

```
Format selection logic:
bestvideo[height<=MAX_VIDEO_HEIGHT][ext=mp4]+bestaudio[ext=m4a]/best[height<=MAX_VIDEO_HEIGHT][ext=mp4]/best
```

**Sources:** [scripts/download_video.py:64-67]()

### Format Selection Diagram

```mermaid
flowchart TD
    Start["download_video() function"]
    Config["Read MAX_VIDEO_HEIGHT from .env"]
    BuildFormat["Build format string:<br/>bestvideo[height&lt;=MAX_VIDEO_HEIGHT][ext=mp4]<br/>+bestaudio[ext=m4a]"]
    YdlOpts["ydl_opts dict<br/>format field"]
    YdlDownload["yt_dlp.YoutubeDL<br/>extract_info()"]
    
    VideoAvail{"Video streams<br/>available?"}
    SeparateStreams["Download video + audio separately<br/>Merge automatically"]
    CombinedFormat["Download best combined format<br/>≤ MAX_VIDEO_HEIGHT"]
    FallbackBest["Download best available<br/>regardless of height"]
    
    Start --> Config
    Config --> BuildFormat
    BuildFormat --> YdlOpts
    YdlOpts --> YdlDownload
    YdlDownload --> VideoAvail
    VideoAvail -->|"Separate available"| SeparateStreams
    VideoAvail -->|"Only combined"| CombinedFormat
    VideoAvail -->|"No match"| FallbackBest
```

**Sources:** [scripts/download_video.py:64-67]()

### Quality vs. File Size Trade-offs

| Resolution | Typical File Size (per minute) | Use Case |
|------------|-------------------------------|----------|
| 720p | 8-15 MB | Mobile viewing, faster downloads |
| 1080p | 15-30 MB | Standard high quality (default) |
| 1440p | 30-50 MB | High-detail content, large screens |
| 2160p (4K) | 50-100 MB | Professional use, archival |

Higher resolutions require:
- More storage space
- Longer download times
- More processing power for clipping and burning
- More bandwidth for subsequent sharing

**Sources:** [README.md:140-141]()

## Network Proxy Configuration

### YT_DLP_PROXY

The `YT_DLP_PROXY` variable routes all yt-dlp network requests through a specified proxy server. This is useful for:
- Bypassing geographic restrictions
- Network environments requiring proxy access
- Rate limiting and traffic management

**Supported Protocols:**
- HTTP: `http://proxy-server:port`
- HTTPS: `https://proxy-server:port`
- SOCKS5: `socks5://proxy-server:port`

**Configuration:**
```bash
# HTTP proxy
YT_DLP_PROXY=http://proxy.example.com:8080

# SOCKS5 proxy
YT_DLP_PROXY=socks5://127.0.0.1:1080

# Proxy with authentication
YT_DLP_PROXY=http://username:password@proxy.example.com:8080
```

### Implementation Details

The proxy setting is passed to yt-dlp through the `ydl_opts` configuration dictionary. When set, yt-dlp uses this proxy for all HTTP(S) requests including:
- Video metadata fetching
- Video stream downloads
- Subtitle downloads
- Thumbnail requests (if enabled)

**Sources:** [.env.example:53-55](), [README.md:254-259]()

## Download Rate Limiting

### YT_DLP_RATE_LIMIT

The `YT_DLP_RATE_LIMIT` variable throttles download speed to a specified maximum bandwidth. This prevents the download process from consuming all available bandwidth.

**Format:**
- Numeric value + unit suffix
- Units: `K` (kilobytes), `M` (megabytes), `G` (gigabytes)
- Per second measurement

**Examples:**
```bash
# Limit to 50 kilobytes per second
YT_DLP_RATE_LIMIT=50K

# Limit to 4.2 megabytes per second
YT_DLP_RATE_LIMIT=4.2M

# Limit to 1 gigabyte per second
YT_DLP_RATE_LIMIT=1G
```

### Use Cases

| Scenario | Recommended Limit | Reasoning |
|----------|------------------|-----------|
| Shared network | 1-2M | Prevents bandwidth monopolization |
| Metered connection | 500K-1M | Conserves data usage |
| Background processing | 500K | Allows foreground tasks priority |
| Unrestricted | Empty/unset | Maximum speed available |

**Sources:** [.env.example:57-59]()

## yt-dlp Configuration Flow

The following diagram shows how environment variables flow into the yt-dlp library configuration:

```mermaid
flowchart LR
    subgraph EnvFile[".env file"]
        MaxHeight["MAX_VIDEO_HEIGHT=1080"]
        Proxy["YT_DLP_PROXY=..."]
        RateLimit["YT_DLP_RATE_LIMIT=..."]
    end
    
    subgraph DownloadScript["download_video.py"]
        LoadEnv["Load environment variables<br/>python-dotenv"]
        BuildOpts["Build ydl_opts dict"]
        
        FormatStr["format: bestvideo[height&lt;=1080]..."]
        ProxyOpt["proxy: http://..."]
        RateLimitOpt["ratelimit: 4.2M"]
        
        YdlClass["yt_dlp.YoutubeDL(ydl_opts)"]
    end
    
    subgraph YtDlpLib["yt-dlp library"]
        ExtractInfo["extract_info(url)"]
        NetworkReq["HTTP requests"]
        StreamDownload["Stream download"]
    end
    
    MaxHeight --> LoadEnv
    Proxy --> LoadEnv
    RateLimit --> LoadEnv
    
    LoadEnv --> BuildOpts
    BuildOpts --> FormatStr
    BuildOpts --> ProxyOpt
    BuildOpts --> RateLimitOpt
    
    FormatStr --> YdlClass
    ProxyOpt --> YdlClass
    RateLimitOpt --> YdlClass
    
    YdlClass --> ExtractInfo
    ExtractInfo --> NetworkReq
    NetworkReq --> StreamDownload
```

**Sources:** [scripts/download_video.py:64-87]()

## ydl_opts Configuration Dictionary

The `download_video()` function constructs a configuration dictionary that controls all aspects of the download operation:

### Core Configuration Structure

```python
ydl_opts = {
    'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
    'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['en'],
    'subtitlesformat': 'vtt',
    'writethumbnail': False,
    'quiet': False,
    'no_warnings': False,
    'progress_hooks': [_progress_hook],
}
```

### Configuration Fields

| Field | Value | Purpose |
|-------|-------|---------|
| `format` | Dynamic string with MAX_VIDEO_HEIGHT | Video quality and format selection |
| `outtmpl` | `%(id)s.%(ext)s` | Output filename pattern using video ID |
| `writesubtitles` | `True` | Download available subtitles |
| `writeautomaticsub` | `True` | Fallback to auto-generated subtitles |
| `subtitleslangs` | `['en']` | English subtitles only |
| `subtitlesformat` | `'vtt'` | WebVTT subtitle format |
| `writethumbnail` | `False` | Skip thumbnail download |
| `progress_hooks` | `[_progress_hook]` | Progress callback function |

**Sources:** [scripts/download_video.py:64-87]()

## Progress Monitoring

The `_progress_hook()` callback function provides real-time download progress information:

```mermaid
sequenceDiagram
    participant YtDlp as "yt_dlp.YoutubeDL"
    participant Hook as "_progress_hook()"
    participant Console as "Console Output"
    
    YtDlp->>Hook: status='downloading'<br/>downloaded_bytes=X<br/>total_bytes=Y<br/>speed=Z
    Hook->>Hook: Calculate percent = X/Y * 100
    Hook->>Hook: Format progress bar
    Hook->>Hook: Format sizes and speed
    Hook->>Console: Print progress line with \r
    
    loop "Every chunk"
        YtDlp->>Hook: Updated progress data
        Hook->>Console: Update same line
    end
    
    YtDlp->>Hook: status='finished'
    Hook->>Console: Print newline
```

### Progress Hook Implementation

The progress callback handles two status types:

1. **Downloading**: Shows progress bar with percentage, downloaded/total size, and speed
2. **Finished**: Outputs newline to complete progress display

Progress output format:
```
[████████████████░░░░░░░░░░░░░░] 55.3% - 12.5 MB/22.6 MB - 2.1 MB/s
```

**Sources:** [scripts/download_video.py:156-182]()

## Output File Naming

Downloaded files use the YouTube video ID as the filename to avoid issues with special characters in video titles:

### Naming Convention

```
{video_id}.{extension}
{video_id}.en.vtt
```

**Example:**
```
Ckt1cj0xjRM.mp4
Ckt1cj0xjRM.en.vtt
```

### File Discovery Logic

After download, the script locates subtitle files using multiple patterns:

```mermaid
flowchart TD
    Start["Video downloaded:<br/>video_id.mp4"]
    CheckExt1["Check for:<br/>video_id.en.vtt"]
    Exists1{"File exists?"}
    CheckExt2["Check for:<br/>video_id.vtt"]
    Exists2{"File exists?"}
    Found["subtitle_path = path"]
    NotFound["subtitle_path = None"]
    
    Start --> CheckExt1
    CheckExt1 --> Exists1
    Exists1 -->|"Yes"| Found
    Exists1 -->|"No"| CheckExt2
    CheckExt2 --> Exists2
    Exists2 -->|"Yes"| Found
    Exists2 -->|"No"| NotFound
```

**Sources:** [scripts/download_video.py:111-124]()

## Return Data Structure

The `download_video()` function returns a dictionary containing all metadata about the downloaded content:

```python
{
    'video_path': str,       # Absolute path to video file
    'subtitle_path': str,    # Absolute path to subtitle file (or None)
    'title': str,            # Original video title
    'duration': int,         # Duration in seconds
    'file_size': int,        # File size in bytes
    'video_id': str          # YouTube video identifier
}
```

This structure is consumed by subsequent processing scripts in the pipeline, including:
- `analyze_subtitles.py` - Uses subtitle_path and duration
- `clip_video.py` - Uses video_path and duration
- Output organization logic - Uses title for directory naming

**Sources:** [scripts/download_video.py:36-43](), [scripts/download_video.py:142-149]()

## Configuration Best Practices

### Performance Optimization

1. **Video Quality**: Set `MAX_VIDEO_HEIGHT=1080` for balance between quality and file size
2. **Proxy Usage**: Only set `YT_DLP_PROXY` when required (adds latency overhead)
3. **Rate Limiting**: Leave `YT_DLP_RATE_LIMIT` empty unless bandwidth management is needed

### Network Environment Considerations

```mermaid
graph TD
    NetworkEnv["Network Environment"]
    
    subgraph Unrestricted["Unrestricted Access"]
        UnrestConfig["MAX_VIDEO_HEIGHT=1080<br/>YT_DLP_PROXY=<br/>YT_DLP_RATE_LIMIT="]
        UnrestResult["Fast downloads<br/>High quality"]
    end
    
    subgraph GeoBlocked["Geographic Restrictions"]
        GeoConfig["MAX_VIDEO_HEIGHT=1080<br/>YT_DLP_PROXY=socks5://proxy:1080<br/>YT_DLP_RATE_LIMIT="]
        GeoResult["Access enabled<br/>Moderate speed"]
    end
    
    subgraph Metered["Metered/Shared Network"]
        MeteredConfig["MAX_VIDEO_HEIGHT=720<br/>YT_DLP_PROXY=<br/>YT_DLP_RATE_LIMIT=2M"]
        MeteredResult["Controlled bandwidth<br/>Lower quality"]
    end
    
    NetworkEnv --> Unrestricted
    NetworkEnv --> GeoBlocked
    NetworkEnv --> Metered
    
    Unrestricted --> UnrestConfig --> UnrestResult
    GeoBlocked --> GeoConfig --> GeoResult
    Metered --> MeteredConfig --> MeteredResult
```

### Storage Considerations

Different quality settings produce different storage requirements for typical processing workflows:

**Example: 25-minute video split into 5 chapters (5 minutes each)**

| Quality | Video Size | 5 Clips | With Burned Subs | Total Storage |
|---------|-----------|---------|------------------|---------------|
| 720p | 200 MB | 200 MB | 400 MB | 600 MB |
| 1080p | 400 MB | 400 MB | 800 MB | 1.2 GB |
| 1440p | 750 MB | 750 MB | 1.5 GB | 2.25 GB |
| 2160p | 1.5 GB | 1.5 GB | 3 GB | 4.5 GB |

Storage multipliers:
- Original video: 1x
- Clipped segments: ~1x (sum of all clips)
- With burned subtitles: ~2x (doubles clip storage)

**Sources:** [README.md:140-141]()

## Error Handling

The download system handles several error conditions related to configuration:

### Invalid Quality Settings

If `MAX_VIDEO_HEIGHT` is set to an unsupported value, yt-dlp falls back to best available format. The system does not validate this value before passing it to yt-dlp.

### Proxy Failures

If the configured proxy is unreachable or returns errors, yt-dlp raises an exception caught by `download_video()`. The error message includes proxy-specific details.

### Rate Limit Format Errors

Invalid `YT_DLP_RATE_LIMIT` values (e.g., missing unit suffix) cause yt-dlp to ignore the setting and proceed without rate limiting.

**Sources:** [scripts/download_video.py:151-153]()

---

# Page: Subtitle and Translation Settings

# Subtitle and Translation Settings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)

</details>



This document covers the configuration variables related to subtitle rendering and translation in the YouTube Clipper Skill. These settings control both the visual appearance of burned subtitles and the efficiency of the translation pipeline.

For general environment variable setup and structure, see [Environment Variables Reference](#6.1). For advanced details on the batch translation algorithm, see [Batch Translation Optimization](#7.1). For the structure of generated bilingual subtitle files, see [Bilingual Subtitle Format](#7.3).

---

## Configuration Variables Overview

The subtitle and translation settings are defined in the `.env` file and control two distinct aspects of the system:

1. **Subtitle Styling** - Visual appearance when subtitles are burned into video files
2. **Translation Processing** - Target language and batch optimization parameters

```mermaid
graph TB
    subgraph "Configuration Source"
        EnvFile[".env file"]
    end
    
    subgraph "Subtitle Styling Variables"
        FontSize["SUBTITLE_FONT_SIZE<br/>Default: 24"]
        MarginV["SUBTITLE_MARGIN_V<br/>Default: 30"]
    end
    
    subgraph "Translation Variables"
        TargetLang["TARGET_LANGUAGE<br/>Default: 中文"]
        BatchSize["TRANSLATION_BATCH_SIZE<br/>Default: 20"]
    end
    
    subgraph "Script Usage"
        BurnScript["burn_subtitles.py<br/>Uses styling variables"]
        TransPipeline["Translation Pipeline<br/>Uses translation variables"]
    end
    
    EnvFile --> FontSize
    EnvFile --> MarginV
    EnvFile --> TargetLang
    EnvFile --> BatchSize
    
    FontSize --> BurnScript
    MarginV --> BurnScript
    
    TargetLang --> TransPipeline
    BatchSize --> TransPipeline
```

**Sources**: [.env.example:14-40](), [README.md:143-147]()

---

## Subtitle Styling Settings

These variables control how subtitles appear when burned into video files using FFmpeg's `subtitles` filter.

### SUBTITLE_FONT_SIZE

Defines the font size in points for rendered subtitles.

| Property | Value |
|----------|-------|
| Variable Name | `SUBTITLE_FONT_SIZE` |
| Default Value | `24` |
| Valid Range | `8` to `72` (practical range) |
| Used By | `burn_subtitles.py` |
| FFmpeg Mapping | `force_style='FontSize=<value>'` parameter |

**Example Configuration**:
```bash
# Small subtitles for high-resolution videos
SUBTITLE_FONT_SIZE=18

# Default size for 1080p videos
SUBTITLE_FONT_SIZE=24

# Large subtitles for accessibility
SUBTITLE_FONT_SIZE=32
```

**Sources**: [.env.example:14-15]()

### SUBTITLE_MARGIN_V

Defines the vertical margin in pixels from the bottom of the video frame.

| Property | Value |
|----------|-------|
| Variable Name | `SUBTITLE_MARGIN_V` |
| Default Value | `30` |
| Valid Range | `0` to `100` (practical range) |
| Used By | `burn_subtitles.py` |
| FFmpeg Mapping | `force_style='MarginV=<value>'` parameter |

**Example Configuration**:
```bash
# Subtitles closer to bottom edge
SUBTITLE_MARGIN_V=15

# Default positioning
SUBTITLE_MARGIN_V=30

# Subtitles higher up (avoid overlap with video content)
SUBTITLE_MARGIN_V=60
```

**Usage Note**: The margin is measured from the bottom of the frame upward. Larger values move subtitles higher on screen.

**Sources**: [.env.example:16]()

---

## Translation Settings

These variables control the translation pipeline that converts English subtitles to the target language using Claude AI.

### TARGET_LANGUAGE

Specifies the target language for subtitle translation.

| Property | Value |
|----------|-------|
| Variable Name | `TARGET_LANGUAGE` |
| Default Value | `中文` (Chinese) |
| Valid Values | Any language name in the format Claude AI understands |
| Used By | Translation pipeline in batch processing |
| Common Values | `中文`, `日语`, `韩语`, `西班牙语`, `法语`, `德语` |

**Example Configuration**:
```bash
# Chinese (default)
TARGET_LANGUAGE=中文

# Japanese
TARGET_LANGUAGE=日语

# Korean
TARGET_LANGUAGE=韩语

# Spanish
TARGET_LANGUAGE=西班牙语
```

**Implementation Detail**: The language name is passed directly to Claude AI's translation prompt. The system does not validate language names; Claude AI interprets the request.

**Sources**: [.env.example:37-39](), [README.md:147]()

### TRANSLATION_BATCH_SIZE

Defines how many subtitle lines are grouped together for a single translation API call.

| Property | Value |
|----------|-------|
| Variable Name | `TRANSLATION_BATCH_SIZE` |
| Default Value | `20` |
| Recommended Range | `20` to `25` |
| Used By | Batch translation logic |
| Performance Impact | Reduces API calls by ~95% compared to line-by-line translation |

**Example Configuration**:
```bash
# Conservative batching (more API calls, safer)
TRANSLATION_BATCH_SIZE=15

# Default batching (recommended)
TRANSLATION_BATCH_SIZE=20

# Aggressive batching (fewer API calls)
TRANSLATION_BATCH_SIZE=25
```

**Performance Trade-offs**:

| Batch Size | API Calls (400 lines) | Speed | Context Quality |
|------------|----------------------|-------|-----------------|
| 1 (no batching) | 400 | Baseline (slowest) | N/A |
| 15 | ~27 | ~15x faster | Good |
| 20 | ~20 | ~20x faster | Excellent |
| 25 | ~16 | ~25x faster | Very good |
| 50+ | <10 | Fastest | May lose context |

**Warning**: Batch sizes above 30 may cause:
- Context overflow in API requests
- Reduced translation quality for context-dependent phrases
- Potential API timeouts

**Sources**: [.env.example:33-35](), [README.md:144]()

---

## Configuration Flow Through the System

This diagram shows how subtitle and translation settings flow from the `.env` file through the processing pipeline to final outputs.

```mermaid
flowchart TB
    subgraph "Configuration Layer"
        DotEnv[".env file"]
        LoadEnv["python-dotenv<br/>Environment variable loading"]
    end
    
    subgraph "Configuration Values"
        FontSize["SUBTITLE_FONT_SIZE"]
        MarginV["SUBTITLE_MARGIN_V"]
        TargetLang["TARGET_LANGUAGE"]
        BatchSize["TRANSLATION_BATCH_SIZE"]
    end
    
    subgraph "Processing Scripts"
        ExtractSub["extract_subtitle_clip.py<br/>Extracts time-bounded segments"]
        TransBatch["Batch Translation Logic<br/>Groups lines by BATCH_SIZE"]
        ClaudeAPI["Claude AI API<br/>Translates batches"]
        BurnSub["burn_subtitles.py<br/>Applies styles to video"]
    end
    
    subgraph "Intermediate Files"
        ExtractedSRT["*_segment.srt<br/>Time-adjusted subtitles"]
        BilingualSRT["*_bilingual.srt<br/>EN + Target language"]
    end
    
    subgraph "Final Outputs"
        BurnedVideo["*_with_subtitles.mp4<br/>Video with burned subtitles"]
        StandaloneSRT["*_bilingual.srt<br/>Standalone subtitle file"]
    end
    
    DotEnv --> LoadEnv
    LoadEnv --> FontSize
    LoadEnv --> MarginV
    LoadEnv --> TargetLang
    LoadEnv --> BatchSize
    
    ExtractSub --> ExtractedSRT
    ExtractedSRT --> TransBatch
    
    TargetLang --> ClaudeAPI
    BatchSize --> TransBatch
    TransBatch --> ClaudeAPI
    ClaudeAPI --> BilingualSRT
    
    BilingualSRT --> BurnSub
    BilingualSRT --> StandaloneSRT
    
    FontSize --> BurnSub
    MarginV --> BurnSub
    
    BurnSub --> BurnedVideo
```

**Sources**: [.env.example:1-86](), [README.md:113-123]()

---

## How Styling Settings Are Applied

The `SUBTITLE_FONT_SIZE` and `SUBTITLE_MARGIN_V` variables are converted into FFmpeg's ASS subtitle styling format when burning subtitles.

```mermaid
graph LR
    subgraph "Configuration"
        EnvVars["SUBTITLE_FONT_SIZE=24<br/>SUBTITLE_MARGIN_V=30"]
    end
    
    subgraph "burn_subtitles.py"
        BuildStyle["Build force_style string:<br/>FontSize=24,MarginV=30"]
        FFmpegCmd["FFmpeg command with<br/>subtitles filter"]
    end
    
    subgraph "FFmpeg Processing"
        LibAss["libass library<br/>Renders styled subtitles"]
        VideoStream["Video stream with<br/>burned subtitles"]
    end
    
    EnvVars --> BuildStyle
    BuildStyle --> FFmpegCmd
    FFmpegCmd --> LibAss
    LibAss --> VideoStream
```

**FFmpeg Command Structure**:
```
ffmpeg -i input.mp4 -vf "subtitles=file.srt:force_style='FontSize=24,MarginV=30'" output.mp4
```

The `force_style` parameter overrides the default subtitle styling with custom values from the configuration.

**Sources**: [.env.example:14-16]()

---

## How Translation Settings Are Applied

The `TARGET_LANGUAGE` and `TRANSLATION_BATCH_SIZE` variables control the batch translation pipeline that converts English subtitles to bilingual format.

```mermaid
flowchart TB
    subgraph "Input"
        EnglishSRT["English subtitles<br/>400 lines example"]
    end
    
    subgraph "Configuration"
        TargetLangConfig["TARGET_LANGUAGE=中文"]
        BatchSizeConfig["TRANSLATION_BATCH_SIZE=20"]
    end
    
    subgraph "Batch Processing"
        GroupLines["Group into batches:<br/>400 lines ÷ 20 = 20 batches"]
        Batch1["Batch 1: Lines 1-20"]
        Batch2["Batch 2: Lines 21-40"]
        BatchN["Batch 20: Lines 381-400"]
    end
    
    subgraph "Translation"
        API1["Claude API Call 1<br/>Translate batch 1 to 中文"]
        API2["Claude API Call 2<br/>Translate batch 2 to 中文"]
        APIN["Claude API Call 20<br/>Translate batch 20 to 中文"]
    end
    
    subgraph "Output"
        BilingualOutput["Bilingual SRT:<br/>Line 1: English<br/>Line 1: 中文<br/>Line 2: English<br/>Line 2: 中文<br/>..."]
    end
    
    EnglishSRT --> GroupLines
    BatchSizeConfig --> GroupLines
    
    GroupLines --> Batch1
    GroupLines --> Batch2
    GroupLines --> BatchN
    
    Batch1 --> API1
    Batch2 --> API2
    BatchN --> APIN
    
    TargetLangConfig --> API1
    TargetLangConfig --> API2
    TargetLangConfig --> APIN
    
    API1 --> BilingualOutput
    API2 --> BilingualOutput
    APIN --> BilingualOutput
```

**Optimization Impact**: Without batching (batch size = 1), the same 400-line subtitle would require 400 API calls instead of 20, increasing processing time by ~20x and API costs proportionally.

**Sources**: [README.md:211-216]()

---

## Common Configuration Patterns

### Pattern 1: High-Quality Output for Social Media

Optimized for professional appearance with readable subtitles.

```bash
# Larger font for mobile viewing
SUBTITLE_FONT_SIZE=28

# Higher margin to avoid UI elements
SUBTITLE_MARGIN_V=50

# Chinese for target audience
TARGET_LANGUAGE=中文

# Standard batching
TRANSLATION_BATCH_SIZE=20
```

**Use Case**: Creating clips for Xiaohongshu, Douyin, or WeChat

**Sources**: [README.md:14-20]()

### Pattern 2: Fast Processing for Long Videos

Optimized for speed when processing lengthy content.

```bash
# Standard font
SUBTITLE_FONT_SIZE=24

# Standard margin
SUBTITLE_MARGIN_V=30

# Target language
TARGET_LANGUAGE=中文

# Aggressive batching for speed
TRANSLATION_BATCH_SIZE=25
```

**Use Case**: Processing multi-hour lectures or interviews where speed is prioritized

**Sources**: [.env.example:33-35]()

### Pattern 3: Multi-Language Support

Configuration for creating outputs in multiple languages (requires manual .env updates between runs).

```bash
# Standard styling
SUBTITLE_FONT_SIZE=24
SUBTITLE_MARGIN_V=30

# Change this between runs for different languages
TARGET_LANGUAGE=日语  # First run: Japanese
# TARGET_LANGUAGE=韩语  # Second run: Korean
# TARGET_LANGUAGE=西班牙语  # Third run: Spanish

# Standard batching
TRANSLATION_BATCH_SIZE=20
```

**Use Case**: Creating the same video clip with subtitles in different languages for international audiences

**Sources**: [.env.example:37-39]()

---

## Variable Defaults and Fallback Behavior

When subtitle and translation variables are not explicitly set in `.env`, the system uses the following default values:

| Variable | Default Value | Fallback Source |
|----------|---------------|-----------------|
| `SUBTITLE_FONT_SIZE` | `24` | Hard-coded in `burn_subtitles.py` |
| `SUBTITLE_MARGIN_V` | `30` | Hard-coded in `burn_subtitles.py` |
| `TARGET_LANGUAGE` | `中文` | Hard-coded in translation logic |
| `TRANSLATION_BATCH_SIZE` | `20` | Hard-coded in batch processing |

**Behavior**: The system runs successfully even without a `.env` file, using these defaults. This ensures immediate usability while allowing customization for advanced users.

**Sources**: [.env.example:1-86]()

---

## Validation and Error Handling

### Font Size Validation

The system does not validate `SUBTITLE_FONT_SIZE` values at the configuration level. Invalid values are caught by FFmpeg during subtitle burning:

- **Too small** (< 8): Subtitles may be invisible
- **Too large** (> 100): May extend beyond frame boundaries
- **Non-numeric**: FFmpeg error, subtitle burning fails

### Margin Validation

Similar to font size, `SUBTITLE_MARGIN_V` validation occurs at FFmpeg execution:

- **Negative values**: FFmpeg error
- **Extremely large** (> frame height): Subtitles positioned off-screen
- **Non-numeric**: FFmpeg error

### Target Language Validation

`TARGET_LANGUAGE` is not validated. Claude AI interprets the value:

- **Valid language name**: Translates correctly
- **Invalid/typo**: Claude AI may ask for clarification or default to English
- **Empty**: May default to English or fail translation

### Batch Size Validation

`TRANSLATION_BATCH_SIZE` impacts only performance and quality:

- **Too small** (< 10): Excessive API calls, slow processing
- **Too large** (> 30): Context overflow, quality degradation
- **Non-numeric**: Runtime error during batch grouping

**Sources**: [.env.example:1-86]()

---

## Integration Points Summary

```mermaid
graph TB
    subgraph "Configuration Files"
        EnvExample[".env.example<br/>Template with defaults"]
        EnvFile[".env<br/>User configuration"]
    end
    
    subgraph "Scripts Reading Subtitle Settings"
        BurnScript["burn_subtitles.py<br/>Reads: FONT_SIZE, MARGIN_V"]
    end
    
    subgraph "Scripts Reading Translation Settings"
        TransScript["Translation Pipeline<br/>Reads: TARGET_LANGUAGE, BATCH_SIZE"]
    end
    
    subgraph "External Dependencies"
        FFmpeg["FFmpeg + libass<br/>Applies subtitle styles"]
        ClaudeAI["Claude AI API<br/>Performs translations"]
    end
    
    EnvExample -.->|"Template for"| EnvFile
    EnvFile --> BurnScript
    EnvFile --> TransScript
    
    BurnScript --> FFmpeg
    TransScript --> ClaudeAI
```

**Key Integration Points**:
1. **burn_subtitles.py** - Reads styling variables, constructs FFmpeg commands
2. **Translation Pipeline** - Reads language/batch settings, calls Claude AI
3. **FFmpeg** - Renders subtitles with configured styles via libass
4. **Claude AI** - Translates batches to target language

**Sources**: [.env.example:1-86](), [README.md:127-153]()

---

# Page: Processing and Output Settings

# Processing and Output Settings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



This document covers configuration settings that control chapter processing behavior, output file organization, temporary file management, and logging verbosity. For video quality and download settings, see [6.2](#6.2). For subtitle and translation settings, see [6.3](#6.3).

## Overview

Processing and output settings control how the system generates chapters, organizes output files, manages temporary data, and logs operations. These settings are defined in the `.env` file and affect the behavior of multiple scripts throughout the processing pipeline.

**Key Configuration Variables:**
- `TARGET_CHAPTER_DURATION` - Guides AI chapter segmentation
- `OUTPUT_DIR` - Determines output file location
- `TEMP_DIR` - Temporary storage for path workarounds
- `KEEP_TEMP_FILES` - Controls cleanup behavior
- `LOG_LEVEL` - Controls logging verbosity

Sources: [.env.example:1-86](), [README.md:129-154]()

---

## Target Chapter Duration

### Configuration

The `TARGET_CHAPTER_DURATION` setting guides the AI semantic analysis to generate chapters of approximately the specified length.

| Variable | Type | Default | Range | Purpose |
|----------|------|---------|-------|---------|
| `TARGET_CHAPTER_DURATION` | integer | `180` | `120-300` | Target chapter length in seconds |

**Recommended Values:**
- `180` (3 minutes) - Balanced for social media clips
- `240` (4 minutes) - Longer-form content
- `300` (5 minutes) - Maximum recommended length

Sources: [.env.example:42-47](), [README.md:149-150]()

### Usage in Chapter Analysis

The `analyze_subtitles.py` script uses this value as guidance when preparing data for AI analysis. The actual chapter boundaries are determined semantically by Claude AI based on content structure, not mechanically by time.

```mermaid
flowchart TB
    EnvFile[".env file<br/>TARGET_CHAPTER_DURATION=180"]
    AnalyzeScript["analyze_subtitles.py<br/>Parse VTT subtitles"]
    AIAnalysis["Claude AI<br/>Semantic Analysis"]
    Chapters["Generated Chapters<br/>2-5 min each"]
    
    EnvFile -->|"Duration guidance"| AnalyzeScript
    AnalyzeScript -->|"Subtitle data +<br/>duration target"| AIAnalysis
    AIAnalysis -->|"Topic-based<br/>segmentation"| Chapters
    
    note1["Note: AI uses this as<br/>guidance, not strict rule"]
    AIAnalysis -.->|"Considers"| note1
```

**Diagram: Chapter Duration Configuration Flow**

The duration value informs the AI's decision-making but does not override semantic boundaries. If a natural topic transition occurs at 4 minutes, the AI will create a chapter boundary there rather than forcing a 3-minute split mid-topic.

Sources: [SKILL.md:96-144]()

### Effect on Chapter Generation

**Example: 25-minute video with different duration targets**

| Target Duration | Expected Chapters | Actual Behavior |
|-----------------|-------------------|-----------------|
| `120` (2 min) | 12-13 chapters | 10-15 chapters (adjusted for topic boundaries) |
| `180` (3 min) | 8-9 chapters | 7-10 chapters (semantic optimization) |
| `300` (5 min) | 5 chapters | 5-7 chapters (broader topics) |

The AI balances the target duration with content semantics:
- Shorter durations: More granular topic splitting
- Longer durations: Broader topic grouping
- Always: Natural transition points respected

Sources: [SKILL.md:122-127](), [README.md:196-209]()

---

## Output Directory Configuration

### OUTPUT_DIR Setting

The `OUTPUT_DIR` variable specifies where processed files are written.

| Variable | Type | Default | Example Values |
|----------|------|---------|----------------|
| `OUTPUT_DIR` | string | `./youtube-clips` | `~/Videos/clips`<br/>`/tmp/output` |

**Path Resolution:**
- Relative paths: Resolved from current working directory
- Absolute paths: Used as-is
- Tilde expansion: `~` expands to user home directory

Sources: [.env.example:20-23](), [README.md:137-138]()

### Output Directory Structure

The system creates a three-level hierarchy to organize output files:

```mermaid
graph TB
    Root["OUTPUT_DIR<br/>(e.g., ./youtube-clips)"]
    Session["Session Directory<br/>YYYYMMDD_HHMMSS"]
    Chapter1["Chapter Directory<br/>Sanitized_Chapter_Title"]
    Chapter2["Another_Chapter"]
    
    Files["Output Files:<br/>*_clip.mp4<br/>*_with_subtitles.mp4<br/>*_bilingual.srt<br/>*_summary.md"]
    
    Root --> Session
    Session --> Chapter1
    Session --> Chapter2
    Chapter1 --> Files
    
    note1["Timestamp prevents<br/>session conflicts"]
    note2["Sanitized names<br/>remove special chars"]
    
    Session -.-> note1
    Chapter1 -.-> note2
```

**Diagram: Output Directory Hierarchy**

**Directory Creation Example:**
```
./youtube-clips/
└── 20260122_143022/           # Session timestamp
    ├── AGI_Definition/          # Chapter 1
    │   ├── AGI_Definition_clip.mp4
    │   ├── AGI_Definition_with_subtitles.mp4
    │   ├── AGI_Definition_bilingual.srt
    │   └── AGI_Definition_summary.md
    └── China_AI_Landscape/      # Chapter 2
        ├── China_AI_Landscape_clip.mp4
        └── China_AI_Landscape_bilingual.srt
```

Sources: [SKILL.md:239-262](), [README.md:112-124]()

### File Naming Convention

Chapter directory names are derived from chapter titles with sanitization:

**Sanitization Rules:**
1. Remove special characters: `/ \ : * ? " < > |`
2. Replace spaces with underscores
3. Limit length to 100 characters
4. Preserve alphanumeric and underscore characters

**Sanitization Examples:**

| Original Chapter Title | Sanitized Directory Name |
|------------------------|--------------------------|
| `"AGI: A New Era"` | `AGI_A_New_Era` |
| `"China's AI Gap"` | `Chinas_AI_Gap` |
| `"Impact of Chip Bans (2023)"` | `Impact_of_Chip_Bans_2023` |

This sanitization occurs in utility functions used across multiple scripts.

Sources: [SKILL.md:347-350](), [README.md:270-277]()

---

## Temporary File Management

### Purpose of Temporary Files

The system uses temporary files to work around FFmpeg's inability to handle file paths containing spaces when using the `subtitles` filter. This is a critical workaround implemented in `burn_subtitles.py`.

```mermaid
flowchart LR
    Input["Input Files<br/>(may have spaces in path)"]
    TempDir["Temporary Directory<br/>(no spaces in path)"]
    FFmpeg["FFmpeg Processing<br/>subtitles filter"]
    Output["Output File<br/>(original location)"]
    Cleanup["Cleanup<br/>(if KEEP_TEMP_FILES=false)"]
    
    Input -->|"Copy to"| TempDir
    TempDir -->|"Process from"| FFmpeg
    FFmpeg -->|"Write to"| TempDir
    TempDir -->|"Move to"| Output
    Output -->|"Remove temp"| Cleanup
```

**Diagram: Temporary File Lifecycle**

Sources: [SKILL.md:285-291]()

### TEMP_DIR Configuration

| Variable | Type | Default | Behavior |
|----------|------|---------|----------|
| `TEMP_DIR` | string | (empty) | Empty: Use system default temp directory<br/>Specified: Use provided path |

**System Default Temporary Directories:**
- macOS/Linux: `/tmp/` or `$TMPDIR`
- Windows: `%TEMP%` directory

**Custom TEMP_DIR Usage:**
```bash
# Example 1: Use specific directory
TEMP_DIR=/var/tmp/youtube-clipper

# Example 2: Use user temp space
TEMP_DIR=~/.cache/youtube-clipper
```

Sources: [.env.example:65-67]()

### KEEP_TEMP_FILES Configuration

| Variable | Type | Default | Values |
|----------|------|---------|--------|
| `KEEP_TEMP_FILES` | boolean | `false` | `true` - Keep temporary files<br/>`false` - Delete after processing |

**When to Use:**
- `false` (default): Normal operation, saves disk space
- `true`: Debugging subtitle burning issues, inspecting intermediate files

**Files Created in Temporary Directory:**
- Copied video file (during subtitle burning)
- Copied subtitle file (during subtitle burning)
- Intermediate output file (before moving to final location)

Sources: [.env.example:69-71]()

### Implementation in burn_subtitles.py

The temporary file mechanism is implemented in the subtitle burning script to avoid FFmpeg path parsing issues:

**Process Flow:**
1. Check if `TEMP_DIR` is configured, otherwise use system temp
2. Create unique temporary directory
3. Copy input video and subtitle files to temp directory
4. Execute FFmpeg using temp directory paths
5. Move output file to final destination
6. Clean up temp directory (unless `KEEP_TEMP_FILES=true`)

This workaround is necessary because FFmpeg's `subtitles` filter cannot reliably parse paths with spaces, even when properly escaped or quoted.

Sources: [SKILL.md:205-211](), [SKILL.md:285-291]()

---

## Logging Configuration

### LOG_LEVEL Setting

The `LOG_LEVEL` variable controls the verbosity of logging output across all Python scripts.

| Variable | Type | Default | Valid Values |
|----------|------|---------|--------------|
| `LOG_LEVEL` | string | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

Sources: [.env.example:73-75]()

### Logging Levels Explained

```mermaid
graph TB
    subgraph "Log Level Hierarchy"
        DEBUG["DEBUG<br/>Most Verbose"]
        INFO["INFO<br/>Standard"]
        WARNING["WARNING<br/>Issues Only"]
        ERROR["ERROR<br/>Failures Only"]
    end
    
    DEBUG -->|"Includes"| INFO
    INFO -->|"Includes"| WARNING
    WARNING -->|"Includes"| ERROR
    
    note1["DEBUG: Variable values,<br/>function calls,<br/>intermediate results"]
    note2["INFO: Operation progress,<br/>completion status"]
    note3["WARNING: Recoverable issues,<br/>retries"]
    note4["ERROR: Fatal failures,<br/>exceptions"]
    
    DEBUG -.-> note1
    INFO -.-> note2
    WARNING -.-> note3
    ERROR -.-> note4
```

**Diagram: Logging Level Hierarchy**

### Log Output by Level

**DEBUG Level:**
- Function entry/exit
- Variable values during processing
- FFmpeg command construction
- API request/response details
- File operation details

**INFO Level (Default):**
- Processing stage start/completion
- Video download progress
- Chapter generation results
- Translation batch progress
- File creation notifications

**WARNING Level:**
- Subtitle download fallback to auto-generated
- Translation retry attempts
- Temporary file cleanup issues
- Non-critical configuration warnings

**ERROR Level:**
- Missing dependencies
- FFmpeg execution failures
- API call failures (after retries)
- File I/O errors
- Invalid configuration values

Sources: [.env.example:73-75]()

### Logging Configuration Usage

**Example Configurations:**

```bash
# Development/Debugging
LOG_LEVEL=DEBUG

# Production/Normal Use
LOG_LEVEL=INFO

# Minimal Output
LOG_LEVEL=WARNING
```

**Effect on Operations:**

| Operation | DEBUG Output | INFO Output | WARNING Output |
|-----------|--------------|-------------|----------------|
| Video Download | yt-dlp command, format selection | Download progress, completion | Errors only |
| Chapter Analysis | Full subtitle text, AI prompts | Chapter count, titles | Failures only |
| Subtitle Burning | FFmpeg command, temp paths | Start/completion | FFmpeg errors |
| Translation | Each batch, API calls | Batch progress percentage | Retry attempts |

The logging system uses Python's standard `logging` module, configured through `python-dotenv` loading of the `.env` file.

Sources: [.env.example:73-75]()

---

## Configuration Integration

### How Settings Flow Through the System

```mermaid
flowchart TB
    EnvFile[".env File<br/>User Configuration"]
    DotEnv["python-dotenv<br/>Load Environment"]
    
    subgraph "Python Scripts"
        Download["download_video.py"]
        Analyze["analyze_subtitles.py<br/>Uses: TARGET_CHAPTER_DURATION"]
        Clip["clip_video.py"]
        Burn["burn_subtitles.py<br/>Uses: TEMP_DIR, KEEP_TEMP_FILES"]
        Utils["utils.py<br/>Uses: OUTPUT_DIR, LOG_LEVEL"]
    end
    
    Runtime["Runtime Behavior:<br/>- Chapter segmentation<br/>- Output organization<br/>- Temp file handling<br/>- Log verbosity"]
    
    EnvFile -->|"Parse"| DotEnv
    DotEnv -->|"Environment variables"| Download
    DotEnv -->|"Environment variables"| Analyze
    DotEnv -->|"Environment variables"| Clip
    DotEnv -->|"Environment variables"| Burn
    DotEnv -->|"Environment variables"| Utils
    
    Analyze --> Runtime
    Burn --> Runtime
    Utils --> Runtime
```

**Diagram: Configuration Variable Flow from .env to Scripts**

Sources: [.env.example:1-86](), [README.md:127-154]()

### Configuration Defaults

When environment variables are not set, the system uses built-in defaults:

| Setting | Default Value | Fallback Behavior |
|---------|---------------|-------------------|
| `TARGET_CHAPTER_DURATION` | `180` | Used if not specified in `.env` |
| `OUTPUT_DIR` | `./youtube-clips` | Creates in current directory |
| `TEMP_DIR` | (empty) | Uses system temp directory |
| `KEEP_TEMP_FILES` | `false` | Cleans up after processing |
| `LOG_LEVEL` | `INFO` | Standard verbosity |

These defaults ensure the system works without explicit configuration while allowing customization for advanced use cases.

Sources: [.env.example:1-86](), [README.md:127-154]()

---

## Practical Configuration Examples

### Basic Configuration

Minimal `.env` for typical usage:

```bash
# Standard settings - most users don't need to change these
TARGET_CHAPTER_DURATION=180
OUTPUT_DIR=./youtube-clips
LOG_LEVEL=INFO
```

### Development/Debugging Configuration

For troubleshooting issues:

```bash
# Maximum verbosity and temp file preservation
TARGET_CHAPTER_DURATION=180
OUTPUT_DIR=./youtube-clips
TEMP_DIR=/tmp/youtube-clipper-debug
KEEP_TEMP_FILES=true
LOG_LEVEL=DEBUG
```

### Production Configuration

For automated processing:

```bash
# Specific output location, minimal logging
TARGET_CHAPTER_DURATION=240
OUTPUT_DIR=/var/www/clips
TEMP_DIR=/fast-ssd/temp
KEEP_TEMP_FILES=false
LOG_LEVEL=WARNING
```

### Short-Form Content Configuration

Optimized for social media:

```bash
# Shorter chapters for TikTok/Reels/Shorts
TARGET_CHAPTER_DURATION=120
OUTPUT_DIR=~/Videos/social-media
LOG_LEVEL=INFO
```

Sources: [.env.example:1-86](), [README.md:127-154]()

---

## Summary Table

| Configuration | Controls | Used By | Impact |
|---------------|----------|---------|--------|
| `TARGET_CHAPTER_DURATION` | AI chapter length guidance | `analyze_subtitles.py` | Chapter granularity (2-5 min) |
| `OUTPUT_DIR` | Output file location | All scripts via `utils.py` | Where files are saved |
| `TEMP_DIR` | Temporary file location | `burn_subtitles.py` | Workaround for path issues |
| `KEEP_TEMP_FILES` | Cleanup behavior | `burn_subtitles.py` | Debugging capability |
| `LOG_LEVEL` | Logging verbosity | All scripts | Console output detail |

Sources: [.env.example:1-86](), [SKILL.md:1-374]()

---

# Page: Advanced Topics

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)

</details>



This page documents the advanced features and optimization strategies that distinguish the YouTube Clipper Skill from simpler video processing tools. These capabilities leverage AI for intelligent content analysis and employ algorithmic optimizations to reduce computational overhead and API costs.

For basic usage patterns, see [Basic Usage](#2.2). For configuration of advanced features, see [Configuration](#6). For the underlying architecture, see [Architecture](#3).

---

## Batch Translation Optimization

### Problem Statement

Naive subtitle translation processes each subtitle line individually through separate API calls. For a typical 30-minute video with 600 subtitle entries, this results in 600 API requests, leading to:

- Slow processing time (serial API calls)
- High API costs (per-request overhead)
- Rate limiting issues
- Poor translation consistency (no shared context)

### Batching Strategy

The system groups 20-25 consecutive subtitle lines into a single batch and translates them in one API call. This achieves a **95% reduction in API calls** (600 calls → 30 calls).

**Batch Size Selection**: The 20-25 line range is empirically optimized:
- **< 20 lines**: Insufficient API call reduction
- **20-25 lines**: Optimal balance of efficiency and quality
- **> 30 lines**: Token limits and reduced translation quality

```mermaid
flowchart TB
    Input["Subtitle Array<br/>600 entries"]
    
    subgraph "Batching Algorithm"
        Split["Split into batches<br/>batch_size=20"]
        B1["Batch 1<br/>lines 1-20"]
        B2["Batch 2<br/>lines 21-40"]
        B3["Batch 3<br/>lines 41-60"]
        BN["Batch 30<br/>lines 581-600"]
    end
    
    subgraph "Translation Layer"
        API1["Claude API Call 1<br/>Translate batch 1"]
        API2["Claude API Call 2<br/>Translate batch 2"]
        API3["Claude API Call 3<br/>Translate batch 3"]
        APIN["Claude API Call 30<br/>Translate batch 30"]
    end
    
    subgraph "Output Processing"
        Parse["Parse JSON responses<br/>Extract translations"]
        Assign["Assign translations<br/>to original subtitles"]
        Output["Bilingual Subtitles<br/>600 entries with translations"]
    end
    
    Input --> Split
    Split --> B1
    Split --> B2
    Split --> B3
    Split --> BN
    
    B1 --> API1
    B2 --> API2
    B3 --> API3
    BN --> APIN
    
    API1 --> Parse
    API2 --> Parse
    API3 --> Parse
    APIN --> Parse
    
    Parse --> Assign
    Assign --> Output
```

**Sources**: [README.md:211-216](), [TECHNICAL_NOTES.md:261-305]()

### Implementation Details

The batching algorithm groups consecutive subtitles while preserving:
1. **Context continuity**: Batches maintain temporal proximity
2. **Order preservation**: Translation order matches input order
3. **Boundary integrity**: No subtitle is split across batches

Configuration parameter:
- `TRANSLATION_BATCH_SIZE`: Controls batch size (default: 20)

Referenced in: [.env.example]() configuration file

### Translation Quality Assurance

The batch translation prompt instructs Claude to:
- Translate each line independently (maintain line-level granularity)
- Preserve context across the batch
- Return a JSON array where index N contains the translation of input line N
- Maintain consistent terminology throughout the batch

**Sources**: [TECHNICAL_NOTES.md:273-304]()

---

## AI Semantic Analysis

### Semantic Chapter Generation

Unlike mechanical time-based video splitters that divide content at arbitrary intervals, this system uses Claude AI to understand content semantics and identify natural topic boundaries.

```mermaid
graph TB
    subgraph "Input Processing"
        Video["YouTube Video"]
        Download["download_video.py<br/>Download subtitles"]
        VTT["Subtitle File<br/>*.en.vtt format"]
        Parse["Parse VTT<br/>Extract text + timestamps"]
    end
    
    subgraph "AI Analysis Phase"
        Prep["analyze_subtitles.py<br/>Prepare prompt data"]
        
        subgraph "Content Understanding"
            Topics["Identify Topics<br/>Semantic clustering"]
            Transitions["Detect Transitions<br/>Topic boundaries"]
            Duration["Apply Duration Targets<br/>TARGET_CHAPTER_DURATION"]
        end
        
        Claude["Claude AI API<br/>Semantic analysis"]
        
        subgraph "Metadata Generation"
            Titles["Generate Titles<br/>10-20 characters"]
            Summaries["Core Summaries<br/>50-100 characters"]
            Keywords["Keywords<br/>3-5 terms per chapter"]
        end
    end
    
    subgraph "Output"
        Chapters["Chapter Array<br/>Semantic boundaries"]
        Metadata["Chapter Metadata<br/>titles, summaries, keywords"]
    end
    
    Video --> Download
    Download --> VTT
    VTT --> Parse
    Parse --> Prep
    
    Prep --> Claude
    Claude --> Topics
    Topics --> Transitions
    Transitions --> Duration
    Duration --> Claude
    
    Claude --> Titles
    Claude --> Summaries
    Claude --> Keywords
    
    Titles --> Chapters
    Summaries --> Chapters
    Keywords --> Chapters
    Transitions --> Chapters
    
    Chapters --> Metadata
```

**Sources**: [README.md:192-209](), [scripts/analyze_subtitles.py]()

### Analysis Process

The semantic analysis pipeline operates in phases:

#### 1. Content Understanding
Claude analyzes the complete subtitle transcript to:
- Identify distinct topics and themes
- Understand narrative structure
- Recognize speaker transitions (if applicable)
- Detect conceptual clusters

#### 2. Boundary Detection
Topic boundaries are identified by:
- Semantic discontinuities (topic shifts)
- Natural pauses in dialogue
- Transition phrases ("moving on to...", "next we'll discuss...")
- Context switches

#### 3. Duration Optimization
Chapters are constrained by:
- `TARGET_CHAPTER_DURATION`: 180-300 seconds (configurable)
- Minimum viable duration (prevents excessive fragmentation)
- Complete thought boundaries (doesn't truncate mid-topic)

**Example Output**:
```
Mechanical splitting (30 min video → 6 chapters of 5 minutes):
[00:00-05:00], [05:00-10:00], [10:00-15:00], ...
❌ Topic may be cut mid-sentence

AI semantic analysis (30 min video → 8-12 variable-length chapters):
[00:00-03:15] "AGI as exponential curve"
[03:15-07:30] "China's AI development gap"  
[07:30-11:45] "Impact of chip restrictions"
✅ Each chapter is a complete topic
```

**Sources**: [README.md:196-209](), [TECHNICAL_NOTES.md:1-5]()

### Chapter Metadata Structure

Each generated chapter contains:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | Concise chapter title (10-20 chars) | "AGI Definition" |
| `start_time` | float | Start timestamp in seconds | 0.0 |
| `end_time` | float | End timestamp in seconds | 195.5 |
| `summary` | string | Core content summary (50-100 chars) | "Discussion of AGI as continuous exponential curve" |
| `keywords` | array | Key terms (3-5 items) | ["AGI", "exponential", "timeline"] |

**Sources**: [scripts/analyze_subtitles.py]()

---

## Bilingual Subtitle Format

### Structure

The system generates bilingual subtitle files where each subtitle entry contains both the original English text and the translated target language (default: Chinese) on separate lines.

**Standard SRT Format**:
```srt
1
00:00:00,000 --> 00:00:03,500
This is the English subtitle
这是中文字幕

2
00:00:03,500 --> 00:00:07,000
Another English line
另一行中文
```

```mermaid
graph LR
    subgraph "Bilingual Subtitle Structure"
        Entry["Subtitle Entry"]
        
        subgraph "Components"
            Index["Sequence Index<br/>Integer starting at 1"]
            Time["Timestamp Range<br/>HH:MM:SS,mmm format"]
            Line1["Original Text<br/>English line"]
            Line2["Translation<br/>Target language line"]
        end
        
        Entry --> Index
        Entry --> Time
        Entry --> Line1
        Entry --> Line2
    end
    
    subgraph "Rendering"
        Burn["burn_subtitles.py<br/>FFmpeg + libass"]
        Style["Force Style<br/>FontSize + MarginV"]
        Video["Output Video<br/>Hardcoded subtitles"]
    end
    
    Line1 --> Burn
    Line2 --> Burn
    Burn --> Style
    Style --> Video
```

**Sources**: [README.md:218-232](), [TECHNICAL_NOTES.md:356-388]()

### File Generation

Bilingual subtitle files are created by:
1. Extracting subtitle segment from original VTT file ([scripts/extract_subtitle_clip.py]())
2. Converting VTT format to SRT format
3. Adjusting timestamps relative to clip start time
4. Batch translating English lines
5. Interleaving English and translated lines in SRT entries

Output location: `./youtube-clips/<timestamp>/<chapter_name>/<chapter_name>_bilingual.srt`

**Sources**: [scripts/extract_subtitle_clip.py](), [README.md:115-123]()

### Subtitle Styling and Burning

When subtitles are burned into video, FFmpeg applies styling through the `libass` library:

**Style Parameters**:
| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `FontSize` | 24 | Text size (optimized for 1080p) |
| `MarginV` | 30 | Bottom margin in pixels |
| `Font` | System default | Font family |
| `Color` | White (`&HFFFFFF`) | Text color |
| `OutlineColor` | Black (`&H000000`) | Outline/shadow color |

**Resolution-Specific Recommendations**:
| Resolution | FontSize | MarginV |
|------------|----------|---------|
| 720p | 20 | 20 |
| 1080p | 24 | 30 |
| 4K (2160p) | 48 | 60 |

Configuration: Set via `SUBTITLE_FONT_SIZE` and `SUBTITLE_MARGIN_V` in [.env]()

**FFmpeg Command Structure**:
```bash
ffmpeg -i input.mp4 -vf "subtitles=subtitle.srt:force_style='FontSize=24,MarginV=30'" output.mp4
```

Implementation: [scripts/burn_subtitles.py]()

**Sources**: [TECHNICAL_NOTES.md:356-388](), [scripts/burn_subtitles.py]()

---

## Subtitle Format Conversion

### VTT to SRT Differences

YouTube provides subtitles in WebVTT (`.vtt`) format, which must be converted to SubRip (`.srt`) format for broader compatibility and FFmpeg subtitle burning.

**Format Comparison**:

| Feature | VTT | SRT |
|---------|-----|-----|
| Header | `WEBVTT` required | No header |
| Sequence numbers | Optional | Required (1, 2, 3...) |
| Timestamp separator | Period (`.`) | Comma (`,`) |
| Styling support | Yes (CSS-like) | No |
| Positioning | Yes (align, position) | No |
| Cue settings | Supported | Not supported |

**Example Comparison**:
```
VTT:
WEBVTT

00:00:00.000 --> 00:00:03.500 align:start position:0%
This is a subtitle

SRT:
1
00:00:00,000 --> 00:00:03,500
This is a subtitle
```

**Sources**: [TECHNICAL_NOTES.md:166-213]()

### Conversion Algorithm

```mermaid
flowchart TD
    Input["VTT File<br/>*.en.vtt"]
    
    subgraph "Parsing Phase"
        Read["Read file content"]
        RemoveHeader["Remove WEBVTT header"]
        RemoveStyle["Remove STYLE blocks"]
        RemovePos["Remove positioning<br/>align:, position: etc"]
    end
    
    subgraph "Timestamp Conversion"
        FindTimes["Regex: Match timestamps<br/>HH:MM:SS.mmm"]
        Replace["Replace . with ,<br/>Period to comma"]
    end
    
    subgraph "Structure Normalization"
        AddIndex["Add sequence numbers<br/>if missing"]
        Validate["Validate format<br/>Check timestamp order"]
    end
    
    Output["SRT File<br/>*.srt"]
    
    Input --> Read
    Read --> RemoveHeader
    RemoveHeader --> RemoveStyle
    RemoveStyle --> RemovePos
    
    RemovePos --> FindTimes
    FindTimes --> Replace
    
    Replace --> AddIndex
    AddIndex --> Validate
    Validate --> Output
```

**Sources**: [TECHNICAL_NOTES.md:186-206]()

### Implementation Details

The conversion process is implemented in [scripts/extract_subtitle_clip.py]() and uses the following transformations:

#### 1. Header Removal
Strip the `WEBVTT` header and any metadata blocks:
```python
content = content.replace('WEBVTT\n\n', '')
content = re.sub(r'STYLE.*?-->', '', content, flags=re.DOTALL)
```

#### 2. Timestamp Format Conversion
Replace period with comma in timestamps (critical for SRT compatibility):
```python
content = re.sub(
    r'(\d{2}:\d{2}:\d{2})\.(\d{3})',  # Match HH:MM:SS.mmm
    r'\1,\2',                           # Replace with HH:MM:SS,mmm
    content
)
```

#### 3. Positioning and Styling Removal
VTT cue settings are removed as they are not supported in SRT:
- `align:start`, `align:middle`, `align:end`
- `position:X%`
- `line:X%`
- `size:X%`

#### 4. Sequence Number Generation
If VTT entries lack sequence numbers, generate them sequentially starting from 1.

**Sources**: [scripts/extract_subtitle_clip.py](), [TECHNICAL_NOTES.md:188-206]()

### Timestamp Adjustment for Clips

When extracting a subtitle segment for a video clip, timestamps must be adjusted relative to the clip's start time:

```mermaid
graph TB
    subgraph "Original Video Timeline"
        O1["00:02:00<br/>Subtitle 1"]
        O2["00:02:03<br/>Subtitle 2"]
        O3["00:02:06<br/>Subtitle 3"]
    end
    
    subgraph "Clipping Operation"
        Clip["Extract segment<br/>02:00 - 02:10"]
        Offset["offset = 120 seconds"]
    end
    
    subgraph "Adjusted Clip Timeline"
        A1["00:00:00<br/>Subtitle 1<br/>(120 - 120 = 0)"]
        A2["00:00:03<br/>Subtitle 2<br/>(123 - 120 = 3)"]
        A3["00:00:06<br/>Subtitle 3<br/>(126 - 120 = 6)"]
    end
    
    O1 --> Clip
    O2 --> Clip
    O3 --> Clip
    
    Clip --> Offset
    Offset --> A1
    Offset --> A2
    Offset --> A3
```

**Adjustment Formula**:
```python
adjusted_time = original_time_seconds - clip_start_time_seconds
adjusted_time = max(0.0, adjusted_time)  # Ensure non-negative
```

**Boundary Handling**:
1. **Subtitle fully within range**: Include with adjusted timestamps
2. **Subtitle fully outside range**: Exclude from output
3. **Subtitle crosses start boundary**: Adjust start to 0.0
4. **Subtitle crosses end boundary**: Adjust end to clip duration

Implementation: [scripts/extract_subtitle_clip.py](), utility functions in [scripts/utils.py]()

**Sources**: [TECHNICAL_NOTES.md:215-258](), [scripts/extract_subtitle_clip.py]()

---

## Integration with Core Scripts

The advanced features documented on this page are implemented across multiple core scripts:

| Feature | Primary Script | Supporting Scripts |
|---------|----------------|-------------------|
| Batch Translation | [scripts/analyze_subtitles.py]() | [scripts/utils.py]() |
| Semantic Analysis | [scripts/analyze_subtitles.py]() | None |
| Bilingual Formatting | [scripts/extract_subtitle_clip.py]() | [scripts/utils.py]() |
| VTT→SRT Conversion | [scripts/extract_subtitle_clip.py]() | [scripts/utils.py]() |
| Subtitle Burning | [scripts/burn_subtitles.py]() | [scripts/utils.py]() |

For detailed documentation of individual scripts, see [Core Scripts](#4).

**Sources**: [README.md:1-320](), [TECHNICAL_NOTES.md:1-490]()

---

# Page: Batch Translation Optimization

# Batch Translation Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [SKILL.md](SKILL.md)

</details>



This page documents the batch translation optimization strategy that reduces Claude AI API calls by approximately 95% when translating subtitles. This optimization groups 20-25 subtitle lines into a single API request instead of processing them individually, significantly improving translation speed while maintaining context consistency.

For information about the overall AI integration architecture, see [AI Integration](#3.3). For details on the bilingual subtitle output format, see [Bilingual Subtitle Format](#7.3). For configuration options, see [Subtitle and Translation Settings](#6.3).

---

## Problem Statement

When translating subtitle files containing hundreds of entries, making individual API calls for each subtitle line creates several issues:

| Issue | Impact |
|-------|--------|
| **High API Call Volume** | A typical video with 400+ subtitle entries requires 400+ individual API calls |
| **Translation Latency** | Each API call adds network overhead and processing time |
| **Cost Inefficiency** | Claude API pricing is based on tokens; small requests waste the overhead budget |
| **Context Loss** | Individual translations lack awareness of surrounding dialogue |
| **Rate Limiting Risk** | Hundreds of rapid API calls may trigger rate limiting |

**Example Scenario**: A 25-minute video with 450 subtitle entries:
- **Without optimization**: 450 API calls × ~1 second = 7.5 minutes
- **With batch optimization**: 23 API calls × ~2 seconds = 46 seconds

Sources: [README.md:18](), [README.md:213-216](), [SKILL.md:188-193]()

---

## Solution Overview

The batch translation system groups 20-25 consecutive subtitle lines into a single batch and submits them together to the Claude AI API. This approach achieves:

- **95% reduction in API calls** (450 calls → 23 calls)
- **10x faster translation** (7.5 minutes → <1 minute)
- **Better context preservation** (Claude sees surrounding dialogue)
- **Improved translation consistency** (terminology usage stays coherent)

### Batch Translation vs Single Translation

```mermaid
graph TB
    subgraph "Single Translation Approach (400+ API calls)"
        S1["Subtitle 1<br/>00:00:00 - 00:00:03"]
        S2["Subtitle 2<br/>00:00:03 - 00:00:06"]
        S3["Subtitle 3<br/>00:00:06 - 00:00:09"]
        SDot["..."]
        S450["Subtitle 450<br/>00:24:57 - 00:25:00"]
        
        API1["Claude API<br/>Call 1"]
        API2["Claude API<br/>Call 2"]
        API3["Claude API<br/>Call 3"]
        APIDot["..."]
        API450["Claude API<br/>Call 450"]
        
        S1 --> API1
        S2 --> API2
        S3 --> API3
        SDot --> APIDot
        S450 --> API450
    end
    
    subgraph "Batch Translation Approach (23 API calls)"
        B1["Batch 1<br/>Lines 1-20"]
        B2["Batch 2<br/>Lines 21-40"]
        B3["Batch 3<br/>Lines 41-60"]
        BDot["..."]
        B23["Batch 23<br/>Lines 441-450"]
        
        APIB1["Claude API<br/>Call 1"]
        APIB2["Claude API<br/>Call 2"]
        APIB3["Claude API<br/>Call 3"]
        APIBDot["..."]
        APIB23["Claude API<br/>Call 23"]
        
        B1 --> APIB1
        B2 --> APIB2
        B3 --> APIB3
        BDot --> APIBDot
        B23 --> APIB23
    end
```

Sources: [README.md:213-216](), [SKILL.md:188-193]()

---

## Configuration

The batch size is controlled by the `TRANSLATION_BATCH_SIZE` environment variable, which determines how many subtitle lines are grouped together per API call.

### Environment Variable

| Variable | Default | Range | Purpose |
|----------|---------|-------|---------|
| `TRANSLATION_BATCH_SIZE` | 20 | 15-25 | Number of subtitle lines per API call |

**Configuration Location**: `~/.claude/skills/youtube-clipper/.env`

```bash
# Translation batch size (20-25 recommended)
TRANSLATION_BATCH_SIZE=20
```

### Recommended Values

| Batch Size | Use Case | Trade-offs |
|------------|----------|------------|
| **15** | Short subtitles (few words per line) | More API calls, lower latency per call |
| **20** | Standard (recommended) | Balanced performance and context |
| **25** | Long subtitles (many words per line) | Fewer API calls, but risks token limit |

**Warning**: Setting the batch size too high (>30) may:
- Exceed Claude API token limits per request
- Reduce translation quality due to information overload
- Increase latency per individual batch

Sources: [README.md:144](), [SKILL.md:188](), [.env.example reference in README.md:153]()

---

## Translation Workflow

The batch translation process integrates into the overall video processing pipeline during the subtitle generation phase.

### End-to-End Batch Translation Flow

```mermaid
flowchart TB
    Start["Original Subtitle File<br/>(VTT or SRT format)"]
    
    Extract["extract_subtitle_clip.py<br/>Extract time segment<br/>Adjust timestamps"]
    
    Parse["Parse subtitle entries<br/>Load into memory"]
    
    Group["Group into batches<br/>Size: TRANSLATION_BATCH_SIZE"]
    
    subgraph "Batch Processing Loop"
        Batch["Next batch of 20-25 lines"]
        Format["Format batch for API<br/>Include context instructions"]
        API["Claude API Call<br/>Translate entire batch"]
        Parse2["Parse batch response<br/>Extract individual translations"]
        Validate["Validate line count<br/>matches input"]
    end
    
    Merge["Merge all translated batches"]
    Bilingual["Generate bilingual SRT<br/>Original + Translation"]
    Output["Output: *_bilingual.srt"]
    
    Start --> Extract
    Extract --> Parse
    Parse --> Group
    Group --> Batch
    Batch --> Format
    Format --> API
    API --> Parse2
    Parse2 --> Validate
    Validate -->|More batches?| Batch
    Validate -->|Complete| Merge
    Merge --> Bilingual
    Bilingual --> Output
```

Sources: [SKILL.md:185-199]()

---

## Implementation Details

### Batch Grouping Strategy

The system divides subtitle entries into consecutive batches to maintain temporal and semantic coherence:

```mermaid
graph LR
    subgraph "Subtitle List (52 entries)"
        L1["1-20"]
        L2["21-40"]
        L3["41-52"]
    end
    
    subgraph "Batch 1 (20 lines)"
        B1T["Timestamps preserved<br/>Context maintained"]
    end
    
    subgraph "Batch 2 (20 lines)"
        B2T["Timestamps preserved<br/>Context maintained"]
    end
    
    subgraph "Batch 3 (12 lines)"
        B3T["Timestamps preserved<br/>Context maintained"]
    end
    
    L1 --> B1T
    L2 --> B2T
    L3 --> B3T
    
    B1T --> API1["API Call 1"]
    B2T --> API2["API Call 2"]
    B3T --> API3["API Call 3"]
    
    API1 --> R1["20 translations"]
    API2 --> R2["20 translations"]
    API3 --> R3["12 translations"]
    
    R1 --> Final["Final bilingual SRT<br/>52 entries"]
    R2 --> Final
    R3 --> Final
```

**Key Principles**:
1. **Sequential grouping**: Batches contain consecutive subtitle entries
2. **Preserve timestamps**: Each line retains its original timing
3. **Maintain order**: Translation order matches input order
4. **Handle remainders**: Last batch may contain fewer than `TRANSLATION_BATCH_SIZE` entries

Sources: [SKILL.md:188-193]()

---

## API Request Format

Each batch is formatted as a single Claude API request with context instructions to ensure high-quality, consistent translations.

### Translation Prompt Structure

The system constructs a prompt that includes:

1. **Translation instructions**: Guidelines for tone, terminology, and style
2. **Context preservation**: Directive to maintain dialogue coherence
3. **Batch entries**: All 20-25 subtitle lines with line numbers
4. **Output format**: Specifications for the response structure

**Translation Strategy** (from SKILL.md):
- Maintain technical terminology accuracy
- Use conversational language (suitable for short-form video)
- Keep translations concise and fluent
- Avoid verbose translations

### Request-Response Cycle

```mermaid
sequenceDiagram
    participant Script as translate_subtitles.py
    participant Batch as Batch Processor
    participant API as Claude API
    participant Parser as Response Parser
    
    Script->>Batch: Load subtitle file
    Batch->>Batch: Group lines (size=20)
    
    loop For each batch
        Batch->>API: Submit batch (20 lines)<br/>+ translation instructions
        API->>API: Process entire batch<br/>with context awareness
        API->>Parser: Return 20 translations<br/>in structured format
        Parser->>Parser: Validate line count
        Parser->>Batch: Store translations
    end
    
    Batch->>Script: Return all translations
    Script->>Script: Generate bilingual SRT
```

Sources: [SKILL.md:185-193]()

---

## Error Handling and Retry Logic

The batch translation system implements robust error handling to deal with API failures, network issues, and malformed responses.

### Retry Mechanism

| Error Type | Retry Strategy | Max Retries |
|------------|----------------|-------------|
| **Network timeout** | Exponential backoff | 3 |
| **API rate limiting** | Wait and retry | 3 |
| **Malformed response** | Resubmit batch | 2 |
| **Partial translation** | Request missing lines | 1 |

**Retry Behavior**:
- **Attempt 1**: Immediate retry after 2 seconds
- **Attempt 2**: Retry after 5 seconds
- **Attempt 3**: Retry after 10 seconds
- **After 3 failures**: Report error to user, skip batch

### Validation Steps

After each API response, the system validates:

1. **Line count matching**: Response contains same number of translations as input lines
2. **Format correctness**: Each translation is properly structured
3. **Content presence**: No empty or null translations
4. **Encoding validity**: Translations use correct character encoding

**Fallback Strategy**: If a batch consistently fails after retries, the system can fall back to single-line translation for that specific batch to ensure completion.

Sources: [README.md:261-268](), [SKILL.md:333-336]()

---

## Performance Characteristics

### Timing Analysis

For a typical 25-minute video with 450 subtitle entries:

| Metric | Single Translation | Batch Translation (20/batch) | Improvement |
|--------|-------------------|------------------------------|-------------|
| **API Calls** | 450 | 23 | 95.1% reduction |
| **Total Time** | ~450 seconds | ~46 seconds | 10x faster |
| **Network Overhead** | 450 round-trips | 23 round-trips | 19.5x reduction |
| **Context Quality** | Low (isolated lines) | High (surrounding dialogue) | Qualitative improvement |

### API Call Reduction Formula

```
Number of API Calls = ceil(Total Subtitle Lines / TRANSLATION_BATCH_SIZE)

Example with 450 lines and batch size 20:
API Calls = ceil(450 / 20) = ceil(22.5) = 23 calls

Reduction = 1 - (23 / 450) = 0.949 = 94.9% reduction
```

### Resource Usage

```mermaid
graph LR
    subgraph "Single Translation Resource Usage"
        S1["450 API calls"]
        S2["450 network round-trips"]
        S3["450 × overhead tokens"]
        S4["~7.5 minutes"]
    end
    
    subgraph "Batch Translation Resource Usage"
        B1["23 API calls"]
        B2["23 network round-trips"]
        B3["23 × overhead tokens"]
        B4["~46 seconds"]
    end
    
    S1 -.->|"95% reduction"| B1
    S2 -.->|"95% reduction"| B2
    S3 -.->|"95% reduction"| B3
    S4 -.->|"90% reduction"| B4
```

Sources: [README.md:213-216]()

---

## Integration with Subtitle Pipeline

The batch translation optimization is invoked as part of the broader subtitle processing workflow.

### Subtitle Processing Stage Integration

```mermaid
flowchart TB
    VideoClip["clip_video.py<br/>Extract video segment"]
    
    ExtractSub["extract_subtitle_clip.py<br/>Extract subtitle segment<br/>Adjust timestamps to 00:00:00"]
    
    Decision{User wants<br/>translation?}
    
    BatchTranslate["translate_subtitles.py<br/>BATCH TRANSLATION<br/>Group: TRANSLATION_BATCH_SIZE<br/>API: Claude"]
    
    Bilingual["Generate bilingual SRT<br/>Format: EN + Translation<br/>Style: Original + Translated"]
    
    BurnDecision{User wants<br/>burned subtitles?}
    
    Burn["burn_subtitles.py<br/>Embed subtitles in video<br/>FFmpeg + libass"]
    
    Output["Output files:<br/>*_clip.mp4<br/>*_bilingual.srt<br/>*_with_subtitles.mp4"]
    
    VideoClip --> ExtractSub
    ExtractSub --> Decision
    Decision -->|Yes| BatchTranslate
    Decision -->|No| Output
    BatchTranslate --> Bilingual
    Bilingual --> BurnDecision
    BurnDecision -->|Yes| Burn
    BurnDecision -->|No| Output
    Burn --> Output
```

**Script Reference**: The translation is invoked via `python3 scripts/translate_subtitles.py <subtitle_path>` as documented in [SKILL.md:185-193]().

Sources: [SKILL.md:168-212]()

---

## Code Entity Mapping

The following table maps conceptual components to their implementation locations:

| Concept | Implementation | File Reference |
|---------|----------------|----------------|
| **Batch size configuration** | `TRANSLATION_BATCH_SIZE` env var | `.env` file |
| **Translation script** | `translate_subtitles.py` | `scripts/translate_subtitles.py` |
| **Subtitle extraction** | `extract_subtitle_clip.py` | `scripts/extract_subtitle_clip.py` |
| **SRT parsing** | `pysrt` library | Python dependency |
| **API invocation** | Claude AI API calls | Within translation script |
| **Bilingual format generation** | SRT file creation with dual lines | Translation script output |

**Workflow Invocation**: The batch translation is triggered during [阶段 5.3 翻译字幕](SKILL.md:185)() of the main processing pipeline.

Sources: [SKILL.md:185-193](), [README.md:144]()

---

## Context Preservation Benefits

Batch translation provides superior context awareness compared to single-line translation.

### Context Window Comparison

```mermaid
graph TB
    subgraph "Single Translation: No Context"
        S1["Line 47: 'It'"]
        S2["Translation: '它'<br/>(ambiguous)"]
    end
    
    subgraph "Batch Translation: 20-line Context"
        B1["Lines 40-59<br/>Full conversation context"]
        B2["Line 47 in context:<br/>Previous: 'AGI development'<br/>Current: 'It'<br/>Next: 'will change everything'"]
        B3["Translation: 'AGI'<br/>(context-aware)"]
    end
    
    S1 --> S2
    B1 --> B2
    B2 --> B3
```

**Context Benefits**:
- **Pronoun resolution**: "it", "they", "this" correctly mapped to antecedents
- **Technical terms**: Consistent terminology across related lines
- **Tone preservation**: Conversational flow maintained
- **Idiomatic expressions**: Multi-line idioms translated as units

Sources: [README.md:213-216]()

---

## Summary

The batch translation optimization is a critical performance feature that:

1. **Reduces API calls by 95%** by grouping 20-25 subtitle lines per request
2. **Accelerates translation by 10x** through reduced network overhead
3. **Improves translation quality** via context-aware processing
4. **Configurable via `TRANSLATION_BATCH_SIZE`** environment variable
5. **Integrates seamlessly** into the subtitle processing pipeline

This optimization distinguishes the YouTube Clipper Skill from naive implementations that process subtitles individually, making it practical to translate hundreds of subtitle entries in under a minute while maintaining high translation quality.

For the broader AI architecture, see [AI Integration](#3.3). For bilingual output format details, see [Bilingual Subtitle Format](#7.3).

Sources: [README.md:18](), [README.md:213-216](), [SKILL.md:188-193]()

---

# Page: AI Semantic Analysis

# AI Semantic Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document explains how the YouTube Clipper Skill uses Claude AI to perform semantic analysis of video subtitles to generate meaningful chapter boundaries. This is the core differentiating feature that transforms raw subtitle text into structured, topic-based video segments.

**Scope**: This page covers the semantic chapter generation process, including subtitle data preparation, AI-driven content understanding, topic boundary identification, and chapter metadata creation. For the batch translation optimization that occurs after chapters are selected, see [Batch Translation Optimization](#7.1). For subtitle format handling, see [Subtitle Format Conversion](#7.4).

---

## Overview

AI Semantic Analysis is the process by which Claude AI analyzes subtitle content to identify natural topic boundaries and generate chapters based on semantic meaning rather than arbitrary time intervals. This approach produces chapters that correspond to coherent topics or discussion points, typically 2-5 minutes in duration.

### Semantic vs. Mechanical Splitting

The key distinction between semantic analysis and mechanical splitting:

| Approach | Method | Result | Example |
|----------|--------|--------|---------|
| **Mechanical Splitting** | Fixed time intervals | Arbitrary boundaries that may cut mid-topic | `[0:00-30:00]`, `[30:00-60:00]` |
| **Semantic Analysis** | AI-driven topic understanding | Natural topic boundaries with meaningful titles | `[00:00-03:15] AGI definition`, `[03:15-07:30] China's AI landscape` |

The semantic approach ensures each chapter represents a complete, coherent discussion segment that can stand alone as meaningful content.

**Sources**: [README.md:194-209](), [SKILL.md:96-143]()

---

## Pipeline Position

```mermaid
flowchart LR
    Download["download_video.py<br/>Downloads video + VTT subtitles"]
    Parse["analyze_subtitles.py<br/>Parses VTT format"]
    AI["Claude AI<br/>Semantic Analysis"]
    UserSelect["User Selection<br/>Choose chapters"]
    Process["Processing<br/>Clip, translate, burn"]
    
    Download --> Parse
    Parse --> AI
    AI --> UserSelect
    UserSelect --> Process
    
    style AI fill:#f9f9f9
```

**Diagram**: Semantic analysis occurs after subtitle parsing and before user selection

Semantic analysis is executed in **Stage 3** of the six-stage processing pipeline, immediately after video and subtitle download but before any user interaction.

**Sources**: [SKILL.md:95-143](), High-level system diagrams

---

## Subtitle Data Preparation

Before AI analysis can begin, raw VTT subtitle files must be parsed and structured into a format suitable for semantic processing.

### The `analyze_subtitles.py` Script

The `analyze_subtitles.py` script is responsible for:

1. **VTT Format Parsing**: Reading the VTT subtitle file downloaded by `download_video.py`
2. **Data Extraction**: Extracting timestamp and text content from each subtitle entry
3. **Structure Generation**: Organizing subtitles into a sequential format with timing information
4. **Metadata Computation**: Calculating total duration and subtitle count

```mermaid
flowchart TB
    VTT["VTT Subtitle File<br/>video_id.en.vtt"]
    Script["analyze_subtitles.py"]
    
    subgraph "Parse Process"
        Read["Read VTT file"]
        Extract["Extract entries<br/>timestamp + text"]
        Format["Format structured data"]
        Meta["Compute metadata<br/>duration, count"]
    end
    
    Output["Structured Subtitle Data<br/>+ Total duration<br/>+ Subtitle count"]
    
    VTT --> Script
    Script --> Read
    Read --> Extract
    Extract --> Format
    Format --> Meta
    Meta --> Output
```

**Diagram**: VTT parsing workflow in `analyze_subtitles.py`

### Script Invocation

The script is invoked from the SKILL workflow as follows:

```bash
python3 scripts/analyze_subtitles.py <subtitle_path>
```

Where `<subtitle_path>` points to the downloaded `.vtt` file.

### Output Structure

The script outputs structured data containing:
- **Complete subtitle text**: All subtitle entries with timestamps
- **Total duration**: Video length in seconds or HH:MM:SS format
- **Subtitle count**: Total number of subtitle entries

This structured data becomes the input for Claude AI's semantic analysis.

**Sources**: [SKILL.md:100-109](), [scripts/analyze_subtitles.py]()

---

## Semantic Analysis Process

Once subtitle data is prepared, Claude AI performs a multi-stage semantic analysis to identify topic boundaries and generate chapter metadata.

```mermaid
flowchart TB
    Input["Structured Subtitle Data<br/>from analyze_subtitles.py"]
    
    subgraph "AI Analysis Stages"
        Read["1. Read Complete Content<br/>Consume all subtitle text"]
        Understand["2. Content Understanding<br/>Identify topics, concepts, themes"]
        Boundaries["3. Topic Transition Detection<br/>Find natural switching points"]
        Segment["4. Chapter Segmentation<br/>Create 2-5 min segments"]
        Generate["5. Metadata Generation<br/>Title, summary, keywords"]
    end
    
    Output["Chapter List<br/>with metadata"]
    
    Input --> Read
    Read --> Understand
    Understand --> Boundaries
    Boundaries --> Segment
    Segment --> Generate
    Generate --> Output
```

**Diagram**: Five-stage semantic analysis process

### Stage 1: Read Complete Content

Claude AI receives and processes the entire subtitle transcript as context. This holistic view enables understanding of:
- Overall video structure
- Recurring themes
- Long-form narrative arcs
- Topic relationships

### Stage 2: Content Understanding

The AI analyzes subtitle content to identify:
- **Topics**: Main subjects discussed in each section
- **Concepts**: Key ideas and terminology
- **Themes**: Overarching discussion points
- **Speaker intent**: Purpose of each segment

This understanding is semantic rather than syntactic—the AI grasps meaning, not just keywords.

### Stage 3: Topic Transition Detection

The AI identifies natural boundaries where topics shift by detecting:
- **Explicit transitions**: Phrases like "Now let's talk about...", "Moving on to..."
- **Implicit transitions**: Changes in vocabulary, context, or discussion focus
- **Semantic shifts**: When the subject matter fundamentally changes

These transition points become candidate chapter boundaries.

### Stage 4: Chapter Segmentation

Using detected transitions, the AI segments the video into chapters according to these principles:

| Principle | Target | Rationale |
|-----------|--------|-----------|
| **Duration** | 2-5 minutes per chapter | Long enough to be meaningful, short enough to be digestible |
| **Completeness** | 100% coverage, no gaps | Every second of video belongs to exactly one chapter |
| **Meaningfulness** | Each chapter = one coherent topic | Chapters should represent complete discussion units |
| **Natural boundaries** | Align with topic transitions | Avoid cutting mid-topic |

The AI may adjust boundaries to ensure chapters meet these criteria, potentially splitting long topics or merging very short segments.

### Stage 5: Metadata Generation

For each chapter, the AI generates:

1. **Title** (10-20 characters): Concise topic summary
   - Example: `"AGI as exponential curve"`

2. **Time Range** (MM:SS or HH:MM:SS format): Start and end timestamps
   - Example: `[00:00 - 03:15]`

3. **Core Summary** (50-100 characters): 1-2 sentence description
   - Example: `"AI model capabilities double every 4-12 months; engineers already use Claude for coding"`

4. **Keywords** (3-5 terms): Key concepts for searchability
   - Example: `AGI, exponential growth, Claude Code`

**Sources**: [SKILL.md:110-143](), [README.md:194-209]()

---

## Chapter Output Format

The semantic analysis produces a structured list of chapters presented to the user for selection.

### Display Format

```
📊 分析完成，生成 X 个章节：

1. [00:00 - 03:15] AGI 不是时间点，是指数曲线
   核心: AI 模型能力每 4-12 月翻倍，工程师已用 Claude 写代码
   关键词: AGI、指数增长、Claude Code

2. [03:15 - 06:30] 中国在 AI 上的差距
   核心: 芯片禁运卡住中国，DeepSeek benchmark 优化不代表实力
   关键词: 中国、芯片禁运、DeepSeek

... (all chapters)

✓ 所有内容已覆盖，无遗漏
```

### Data Structure

Each chapter contains:

```
Chapter {
  index: integer,
  start_time: "HH:MM:SS" or "MM:SS",
  end_time: "HH:MM:SS" or "MM:SS",
  title: string (10-20 characters),
  summary: string (50-100 characters),
  keywords: list[string] (3-5 items)
}
```

This structured format enables:
- **User selection**: Easy browsing and choosing of chapters
- **Processing pipeline**: Automated clipping based on time ranges
- **Metadata enrichment**: Titles and summaries used for file naming and social media content

**Sources**: [SKILL.md:128-143]()

---

## Analysis Principles

The semantic analysis adheres to strict principles that differentiate it from simpler approaches.

```mermaid
flowchart TB
    Principle1["Duration Target<br/>2-5 minutes per chapter"]
    Principle2["Complete Coverage<br/>No gaps or overlaps"]
    Principle3["Meaningful Segmentation<br/>One topic per chapter"]
    Principle4["Natural Boundaries<br/>Align with content transitions"]
    
    Input["Raw Subtitles"] --> Principle1
    Input --> Principle2
    Input --> Principle3
    Input --> Principle4
    
    Principle1 --> Quality["High-Quality Chapters"]
    Principle2 --> Quality
    Principle3 --> Quality
    Principle4 --> Quality
    
    Quality --> UserValue["Usable, Shareable<br/>Video Segments"]
```

**Diagram**: Four principles guiding semantic chapter generation

### Principle 1: Duration Target (2-5 Minutes)

**Target**: `TARGET_CHAPTER_DURATION=180` seconds (3 minutes) as default, with acceptable range of 2-5 minutes

**Rationale**:
- Short enough for social media consumption (TikTok, YouTube Shorts, Instagram Reels)
- Long enough to convey a complete idea
- Avoids micro-chapters (< 1 min) that lack substance
- Avoids macro-chapters (> 10 min) that are too long for focused content

**Implementation**: The AI may adjust boundaries slightly to ensure topic completeness while staying within the 2-5 minute range.

### Principle 2: Complete Coverage

**Requirement**: Every timestamp from `00:00:00` to video end must belong to exactly one chapter

**Checks**:
- No gaps: End time of chapter N = start time of chapter N+1
- No overlaps: Chapters never share timestamps
- Full span: First chapter starts at `00:00:00`, last chapter ends at video duration

This ensures users can clip the entire video without missing content.

### Principle 3: Meaningful Segmentation

**Definition**: Each chapter represents a relatively independent, coherent topic or discussion point

**Anti-patterns to avoid**:
- ❌ Cutting mid-sentence or mid-thought
- ❌ Chapters that span multiple unrelated topics
- ❌ Arbitrary time-based splits (e.g., every 5 minutes regardless of content)

**Desired pattern**:
- ✅ Each chapter = one main topic
- ✅ Clear beginning and ending of the topic
- ✅ Can be understood independently (with minimal context)

### Principle 4: Natural Boundaries

**Approach**: Identify where speakers naturally transition between topics

**Indicators of natural boundaries**:
- Explicit transitions: "Now let's move on to...", "Another important point is..."
- Topic shifts: Change from discussing X to discussing Y
- Pauses or breaks in speaking
- Introductions of new concepts

**Counter-example**: Splitting at 00:30:00 simply because it's the midpoint, even if it cuts through a single topic explanation

**Sources**: [SKILL.md:122-127](), [README.md:194-209]()

---

## Integration with Workflow

The semantic analysis integrates with other system components through a defined interface.

```mermaid
flowchart LR
    subgraph "Stage 2: Download"
        DV["download_video.py"]
        VideoFile["video_id.mp4"]
        SubFile["video_id.en.vtt"]
    end
    
    subgraph "Stage 3: Semantic Analysis"
        AS["analyze_subtitles.py<br/>Parse VTT"]
        ClaudeAI["Claude AI<br/>Semantic Analysis"]
        ChapterList["Chapter List"]
    end
    
    subgraph "Stage 4: User Selection"
        AskUser["AskUserQuestion<br/>Select chapters"]
        UserChoice["Selected chapters"]
    end
    
    subgraph "Stage 5: Processing"
        CV["clip_video.py"]
        ESC["extract_subtitle_clip.py"]
        Translate["translate_subtitles.py"]
    end
    
    DV --> VideoFile
    DV --> SubFile
    SubFile --> AS
    AS --> ClaudeAI
    ClaudeAI --> ChapterList
    ChapterList --> AskUser
    VideoFile --> CV
    SubFile --> ESC
    UserChoice --> CV
    UserChoice --> ESC
    UserChoice --> Translate
```

**Diagram**: Semantic analysis in the broader workflow context

### Input Dependencies

Semantic analysis requires:
- **VTT subtitle file**: Downloaded by `download_video.py` [scripts/download_video.py]()
- **Python environment**: With `pysrt` package for subtitle parsing
- **Claude AI API**: Available through the Claude Code environment

### Output Consumers

The generated chapter list is consumed by:
- **User selection interface**: Via `AskUserQuestion` tool in Stage 4
- **Clipping script** (`clip_video.py`): Uses start/end times for video extraction
- **Subtitle extraction** (`extract_subtitle_clip.py`): Uses time ranges to filter subtitles
- **File naming**: Chapter titles become part of output filenames

**Sources**: [SKILL.md:21-373](), High-level system diagrams

---

## Configuration Options

Several configuration variables affect semantic analysis behavior:

### `TARGET_CHAPTER_DURATION`

**Location**: `.env` file  
**Default**: `180` seconds (3 minutes)  
**Range**: Recommended 120-300 seconds (2-5 minutes)  
**Effect**: Guides the AI's target duration for each chapter

```bash
# .env configuration
TARGET_CHAPTER_DURATION=180
```

While this is a target, not a hard constraint, the AI uses it to balance between:
- Creating enough chapters to granularly segment content
- Avoiding excessive fragmentation

### `TARGET_LANGUAGE`

**Location**: `.env` file  
**Default**: `中文` (Chinese)  
**Effect**: While primarily used for translation, may influence how chapter titles and summaries are generated for non-English speaking users

**Sources**: [README.md:134-151](), [SKILL.md configuration references]()

---

## Model Specification

The semantic analysis is performed by Claude AI, specifically using the model defined in the SKILL.md manifest.

### Model Selection

```yaml
model: claude-sonnet-4-5-20250514
```

**Specified in**: [SKILL.md:14]()

This model version is selected for its:
- **Semantic understanding capabilities**: Ability to grasp topic transitions and content structure
- **Context window**: Can process long subtitle transcripts (typically 400+ entries)
- **Multilingual support**: Handles English subtitles and generates chapters suitable for global audiences
- **Instruction following**: Reliably adheres to the chapter generation principles

### Analysis Execution

The analysis is not executed by calling an external script; instead, the Claude Code environment directly invokes Claude AI with the structured subtitle data and generation instructions defined in the SKILL workflow.

**Sources**: [SKILL.md:14](), [SKILL.md:110-143]()

---

## Example Analysis Result

To illustrate the semantic analysis output, here's an example from a tech interview video:

### Input
- **Video**: 58-minute interview about AI development
- **Subtitle entries**: 437 VTT subtitle entries
- **Total words**: ~8,500 words

### Output

```
📊 分析完成，生成 18 个章节：

1. [00:00 - 03:15] AGI as an exponential curve, not a point
   核心: AI capabilities double every 4-12 months; already transforming engineering
   关键词: AGI, exponential growth, Claude Code

2. [03:15 - 06:30] China's gap in AI development
   核心: Chip bans limiting China; DeepSeek benchmark optimization != real capability
   关键词: China, chip ban, DeepSeek

3. [06:30 - 09:45] The impact of chip bans
   核心: H100 restrictions forcing workarounds; training at scale requires cutting-edge hardware
   关键词: H100, chip ban, GPU shortage

4. [09:45 - 12:20] Open source AI model strategy
   核心: Open source enables ecosystem growth but requires significant compute
   关键词: open source, model weights, training costs

...

18. [54:30 - 58:00] Future predictions and wrap-up
    核心: 2025 will see AGI-level capabilities in specialized domains
    关键词: predictions, 2025, specialized AGI

✓ 所有内容已覆盖，无遗漏
```

### Analysis Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Chapters generated | 18 | ~3.2 minutes average |
| Shortest chapter | 2:15 | Still conveyed complete topic |
| Longest chapter | 5:40 | Complex topic requiring more time |
| Coverage | 100% | No gaps from 00:00 to 58:00 |
| Semantic coherence | High | Each chapter = distinct topic |

This example demonstrates how semantic analysis produces actionable, meaningful video segments rather than arbitrary time slices.

**Sources**: [README.md:159-174](), [SKILL.md example outputs]()

---

## Comparison with Alternative Approaches

To highlight the value of semantic analysis, consider alternative chapter generation approaches:

```mermaid
flowchart TB
    Input["58-minute video<br/>8,500 words"]
    
    subgraph "Approach 1: Fixed Interval"
        Fixed["Split every 5 minutes"]
        FixedResult["12 chapters<br/>Many mid-topic cuts<br/>Low usefulness"]
    end
    
    subgraph "Approach 2: Manual Timestamps"
        Manual["Human watches video<br/>Takes notes<br/>Marks timestamps"]
        ManualResult["High quality<br/>Time-intensive (2-3 hours)<br/>Not scalable"]
    end
    
    subgraph "Approach 3: Semantic Analysis"
        Semantic["AI analyzes subtitles<br/>Identifies topic boundaries<br/>Generates metadata"]
        SemanticResult["18 chapters<br/>Natural boundaries<br/>Automated (30 seconds)<br/>High quality"]
    end
    
    Input --> Fixed
    Input --> Manual
    Input --> Semantic
    
    Fixed --> FixedResult
    Manual --> ManualResult
    Semantic --> SemanticResult
    
    style SemanticResult fill:#f9f9f9
```

**Diagram**: Comparison of chapter generation approaches

### Fixed Interval Splitting

**Method**: Divide video into equal time segments (e.g., every 5 minutes)

**Problems**:
- Cuts through topics arbitrarily
- No consideration of content
- Chapters have no meaningful titles
- Requires manual post-processing to be useful

**Use case**: Only suitable when content structure is irrelevant (e.g., surveillance footage)

### Manual Timestamping

**Method**: Human watches video and manually marks chapter boundaries

**Advantages**:
- Can achieve very high quality
- Human understanding of nuance

**Problems**:
- Time-intensive (often 2-3x video length)
- Not scalable
- Requires subject matter expertise
- Prone to human error and inconsistency

**Use case**: Professional video editing where cost is not a constraint

### AI Semantic Analysis

**Method**: This system's approach using Claude AI

**Advantages**:
- Automated (completes in ~30 seconds)
- Scalable to any video length
- Consistent quality
- Generates rich metadata (titles, summaries, keywords)
- Natural topic boundaries

**Trade-offs**:
- Requires English subtitles (or supported subtitle language)
- Quality depends on subtitle accuracy
- May occasionally need minor boundary adjustments

**Use case**: Content creators processing multiple videos, social media managers creating clips, educators extracting lecture segments

**Sources**: [README.md:192-209](), general system design rationale

---

## Error Handling and Edge Cases

The semantic analysis process handles several edge cases:

### Missing or Poor Quality Subtitles

**Issue**: VTT file is incomplete, has significant gaps, or contains errors

**Handling**:
- `analyze_subtitles.py` reports subtitle count and warns if unusually low
- AI analysis may generate fewer, longer chapters to accommodate gaps
- User is informed if chapter quality may be affected

### Very Short Videos (< 5 minutes)

**Issue**: Insufficient content to generate multiple 2-5 minute chapters

**Handling**:
- AI generates 1-2 chapters covering the full video
- Principles 2 (completeness) and 3 (meaningfulness) take precedence over principle 1 (duration target)

### Very Long Videos (> 3 hours)

**Issue**: Subtitle transcript may exceed context window limits

**Handling**:
- System processes in segments if necessary
- Maintains chapter boundaries across segments
- Ensures no duplicate coverage

### Non-English Content

**Issue**: Video has subtitles in languages other than English

**Current limitation**: Analysis optimized for English subtitles

**Workaround**: If non-English VTT subtitles are available and sufficiently complete, analysis may still work but quality may vary

### Rapid Topic Changes

**Issue**: Video rapidly switches between many topics (e.g., news summary)

**Handling**:
- AI may generate more, shorter chapters
- Ensures each chapter still meets minimum meaningful length
- May group very short related topics into single chapters

**Sources**: [SKILL.md:322-337]() error handling section

---

## Performance Characteristics

Understanding the performance of semantic analysis helps set user expectations.

### Time Complexity

| Video Duration | Subtitle Count | Analysis Time | Notes |
|----------------|----------------|---------------|-------|
| 10 minutes | ~75 entries | ~10 seconds | Fast processing |
| 30 minutes | ~225 entries | ~20 seconds | Normal case |
| 60 minutes | ~450 entries | ~30 seconds | Standard long-form |
| 120 minutes | ~900 entries | ~45 seconds | Extended content |

**Factors affecting speed**:
- Claude AI API response time
- Subtitle entry count (more entries = more context to process)
- Complexity of content (technical content may take slightly longer)

### Quality Metrics

Semantic analysis quality can be evaluated on:

1. **Boundary accuracy**: Are chapter breaks at natural topic transitions?
   - Target: >90% of boundaries aligned with topic shifts

2. **Title relevance**: Do chapter titles accurately reflect content?
   - Target: >95% accuracy

3. **Duration distribution**: Are chapters within 2-5 minute range?
   - Target: >80% of chapters within range

4. **Coverage completeness**: Is the entire video covered?
   - Target: 100% (hard requirement)

These metrics are not automatically computed but can be assessed through user feedback and manual review.

**Sources**: Performance characteristics inferred from system design and typical usage

---

## Summary

AI Semantic Analysis is the cornerstone feature that distinguishes the YouTube Clipper Skill from simple time-based video splitters. By leveraging Claude AI's natural language understanding capabilities, the system transforms raw subtitle data into meaningful, topic-aligned video chapters that are immediately useful for content creators, educators, and social media managers.

**Key Takeaways**:
- Semantic analysis operates on VTT subtitle data prepared by `analyze_subtitles.py`
- Claude AI (model: claude-sonnet-4-5-20250514) performs multi-stage analysis: content understanding → topic boundary detection → chapter segmentation → metadata generation
- Chapters adhere to four principles: duration target (2-5 min), complete coverage, meaningful segmentation, natural boundaries
- Output includes title, time range, summary, and keywords for each chapter
- The process is automated, scalable, and produces high-quality results in ~30 seconds for typical videos

This semantic approach enables the creation of shareable video clips that respect content structure rather than imposing arbitrary divisions.

**Sources**: [README.md](), [SKILL.md](), High-level system architecture diagrams

---

# Page: Bilingual Subtitle Format

# Bilingual Subtitle Format

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)
- [references/subtitle-formatting.md](references/subtitle-formatting.md)

</details>



This document describes the structure, generation, and usage of bilingual subtitle files in the YouTube Clipper Skill. Bilingual subtitles contain both the original English text and translated target language text within a single SRT file, enabling viewers to see both languages simultaneously when burned into videos.

**Scope**: This page covers the specific bilingual subtitle format implementation, including SRT structure, merging strategy, and rendering considerations. For details on the translation optimization strategy, see [Batch Translation Optimization](#7.1). For subtitle format conversion between VTT and SRT, see [Subtitle Format Conversion](#7.4). For the burning process itself, see [burn_subtitles.py](#4.4).

---

## Format Structure

Bilingual subtitles use the standard SRT format with a specific multi-line text convention: each subtitle entry contains two lines of text, with the original English line first, followed by the translated target language line.

### SRT Structure

```
Sequence Number
Start Timestamp --> End Timestamp
English Text Line
Target Language Text Line

[blank line separator]
```

**Example**:

```srt
1
00:00:00,000 --> 00:00:03,500
This is the English subtitle
这是中文字幕

2
00:00:03,500 --> 00:00:07,000
Another English line
另一行中文

3
00:00:07,000 --> 00:00:10,500
Technical terms remain accurate
技术术语保持准确性
```

### Format Characteristics

| Aspect | Specification |
|--------|---------------|
| **File Extension** | `.srt` |
| **Encoding** | UTF-8 without BOM |
| **Timestamp Format** | `HH:MM:SS,mmm` (comma separator) |
| **Text Lines per Entry** | 2 (English first, target language second) |
| **Line Order** | English (line 1), Target Language (line 2) |
| **Separator** | Single blank line between entries |

**Sources**: [references/subtitle-formatting.md:178-210](), [README.md:218-232]()

---

## Bilingual Subtitle Format Structure

```mermaid
graph TB
    subgraph "SRT Entry Format"
        SeqNum["Sequence Number<br/>(integer)"]
        TimeRange["Timestamp Range<br/>HH:MM:SS,mmm --> HH:MM:SS,mmm"]
        EnglishLine["English Text Line<br/>(original)"]
        TargetLine["Target Language Line<br/>(translated)"]
        BlankLine["Blank Line Separator"]
    end
    
    SeqNum --> TimeRange
    TimeRange --> EnglishLine
    EnglishLine --> TargetLine
    TargetLine --> BlankLine
    
    subgraph "Example Entry"
        Ex1["1"]
        Ex2["00:00:00,000 --> 00:00:03,500"]
        Ex3["This is English"]
        Ex4["这是中文"]
        Ex5["[blank]"]
    end
    
    Ex1 --> Ex2
    Ex2 --> Ex3
    Ex3 --> Ex4
    Ex4 --> Ex5
```

**Sources**: [references/subtitle-formatting.md:184-194]()

---

## Generation Pipeline

The bilingual subtitle file is generated through a multi-stage process that extracts, translates, and merges subtitle segments.

### Bilingual Subtitle Generation Process

```mermaid
flowchart TD
    Start["Video Downloaded<br/>with English VTT"]
    
    Extract["extract_subtitle_clip.py<br/>Extract segment subtitles"]
    
    TimeAdjust["Adjust timestamps<br/>Relative to clip start"]
    
    VTTtoSRT["Convert VTT to SRT<br/>Replace . with ,"]
    
    BatchTranslate["Batch Translation<br/>20-25 lines per API call"]
    
    Merge["Merge English + Translated<br/>Create bilingual entries"]
    
    Validate["Validate format<br/>UTF-8 encoding, timing"]
    
    Output["Output File<br/>chapter_title_bilingual.srt"]
    
    Start --> Extract
    Extract --> TimeAdjust
    TimeAdjust --> VTTtoSRT
    VTTtoSRT --> BatchTranslate
    BatchTranslate --> Merge
    Merge --> Validate
    Validate --> Output
```

**Sources**: [SKILL.md:168-199]()

---

## Generation Process Details

### Stage 1: Subtitle Extraction

The `extract_subtitle_clip.py` script extracts the subtitle segment corresponding to the video clip's time range.

**Process**:
1. Parse the full VTT subtitle file
2. Filter entries within the clip's start and end times
3. Adjust timestamps relative to clip start (subtract start time)
4. Convert VTT format to SRT format

**Key Operations**:
- **Time filtering**: Only include subtitles where `start_time >= clip_start AND end_time <= clip_end`
- **Timestamp adjustment**: `new_time = original_time - clip_start_time`
- **Format conversion**: Change `.` millisecond separator to `,`

**Sources**: [SKILL.md:178-183](), [scripts/extract_subtitle_clip.py]()

### Stage 2: Batch Translation

The subtitle lines are translated using Claude AI with an optimized batching strategy to reduce API calls by 95%.

**Batch Configuration**:
- **Batch size**: 20-25 subtitle lines per API request
- **Configuration variable**: `TRANSLATION_BATCH_SIZE` in `.env`
- **Default target language**: Chinese (中文)

**Translation Strategy**:
- Preserve technical terminology accuracy
- Use colloquial expressions suitable for short videos
- Maintain concise, fluent phrasing
- Preserve context consistency across batches

For detailed information on the batch translation optimization, see [Batch Translation Optimization](#7.1).

**Sources**: [SKILL.md:185-193](), [README.md:213-216]()

### Stage 3: Bilingual Merging

After translation completes, the English and translated lines are merged into a single bilingual SRT file.

**Merging Algorithm**:
```
For each subtitle entry:
    1. Copy sequence number
    2. Copy timestamp range (unchanged)
    3. Line 1: English text (original)
    4. Line 2: Target language text (translated)
    5. Add blank line separator
```

**Output Format**:
```srt
[sequence]
[timestamp]
[English line]
[Target language line]

```

**Sources**: [SKILL.md:194-199](), [references/subtitle-formatting.md:184-194]()

---

## Rendering and Styling

Bilingual subtitles are burned into videos using FFmpeg's `subtitles` filter with the libass library.

### FFmpeg Burning Process

```mermaid
flowchart LR
    Input["Video Clip<br/>chapter_clip.mp4"]
    BilingualSRT["Bilingual SRT<br/>chapter_bilingual.srt"]
    
    FFmpegFilter["FFmpeg subtitles filter<br/>with libass"]
    
    StyleParams["Style Parameters<br/>FontSize, MarginV, Colors"]
    
    Output["Video with Burned Subtitles<br/>chapter_with_subtitles.mp4"]
    
    Input --> FFmpegFilter
    BilingualSRT --> FFmpegFilter
    StyleParams --> FFmpegFilter
    FFmpegFilter --> Output
```

**Sources**: [SKILL.md:202-212](), [scripts/burn_subtitles.py]()

### Default Style Configuration

The `burn_subtitles.py` script applies consistent styling to bilingual subtitles:

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `FontSize` | 24 | Readable on 1080p video |
| `MarginV` | 30 | Bottom margin in pixels |
| `PrimaryColour` | White | Main text color |
| `OutlineColour` | Black | Text outline for contrast |
| `BorderStyle` | 1 | Outline around text |
| `Alignment` | 2 | Bottom center |

**Configuration Source**: These values can be customized via environment variables:
- `SUBTITLE_FONT_SIZE` in `.env` (default: 24)
- `SUBTITLE_MARGIN_V` in `.env` (default: 30)

**Example FFmpeg Command** (from burn_subtitles.py):
```bash
ffmpeg -i video.mp4 \
  -vf "subtitles=bilingual.srt:force_style='FontSize=24,MarginV=30'" \
  -c:a copy \
  output_with_subtitles.mp4
```

**Sources**: [references/subtitle-formatting.md:196-210](), [SKILL.md:206-211]()

---

## File Organization and Naming

Bilingual subtitle files follow a consistent naming convention and are organized within the chapter-specific output directory.

### Output Directory Structure

```
./youtube-clips/
└── YYYYMMDD_HHMMSS/
    └── Chapter_Title/
        ├── Chapter_Title_clip.mp4
        ├── Chapter_Title_bilingual.srt      # Bilingual subtitle file
        ├── Chapter_Title_with_subtitles.mp4
        └── Chapter_Title_summary.md
```

### File Naming Convention

**Pattern**: `<sanitized_chapter_title>_bilingual.srt`

**Sanitization Rules**:
1. Remove special characters: `/ \ : * ? " < > |`
2. Replace spaces with underscores
3. Limit length to 100 characters
4. Preserve alphanumeric and basic punctuation

**Example Transformations**:
```
"AI Development: China's Gap" → "AI_Development_Chinas_Gap_bilingual.srt"
"What is AGI?" → "What_is_AGI_bilingual.srt"
```

**Sources**: [SKILL.md:242-254](), [README.md:113-123]()

---

## Bilingual Subtitle File Lifecycle

```mermaid
graph TD
    Download["download_video.py<br/>Downloads original VTT"]
    
    Analyze["analyze_subtitles.py<br/>Parses full subtitle"]
    
    UserSelect["User selects chapters<br/>and processing options"]
    
    ExtractClip["extract_subtitle_clip.py<br/>Extracts time segment"]
    
    TranslateBatch["Batch translation<br/>via Claude AI"]
    
    MergeBilingual["Merge process<br/>Creates bilingual SRT"]
    
    BurnOptional["burn_subtitles.py<br/>(if user requests)"]
    
    SaveToDir["Save to output directory<br/>youtube-clips/timestamp/chapter/"]
    
    Download --> Analyze
    Analyze --> UserSelect
    UserSelect --> ExtractClip
    ExtractClip --> TranslateBatch
    TranslateBatch --> MergeBilingual
    MergeBilingual --> SaveToDir
    MergeBilingual --> BurnOptional
    BurnOptional --> SaveToDir
```

**Sources**: [SKILL.md:163-254]()

---

## Technical Considerations

### Encoding Requirements

**Mandatory Encoding**: UTF-8 without BOM (Byte Order Mark)

**Why UTF-8 without BOM**:
- FFmpeg's libass library expects UTF-8
- BOM characters can cause parsing errors in subtitle filters
- Ensures proper display of non-ASCII characters (Chinese, etc.)

**Encoding Verification**:
```bash
file -i bilingual.srt
# Expected output: bilingual.srt: text/plain; charset=utf-8
```

**Sources**: [references/subtitle-formatting.md:307-327]()

### Timestamp Synchronization

Bilingual subtitles maintain the same timing as the original English subtitles. The timestamp adjustment process ensures synchronization with the clipped video segment.

**Timing Rules**:
1. **Start time**: Must match or slightly precede the spoken content
2. **End time**: Must match or slightly exceed the spoken content duration
3. **No overlap**: Adjacent subtitle end/start times should not overlap
4. **Adjustment**: All timestamps are relative to clip start (0:00:00,000)

**Example Adjustment**:
```
Original VTT (full video):
00:02:30.000 --> 00:02:33.500
Text content

After extraction (clip starts at 00:02:00):
00:00:30,000 --> 00:00:33,500
Text content
```

**Sources**: [references/subtitle-formatting.md:243-301]()

### Display Characteristics

When bilingual subtitles are rendered on video:

**Visual Layout**:
```
┌─────────────────────────────────┐
│                                 │
│         Video Frame             │
│                                 │
│                                 │
│    [English text line]          │ ← Line 1 (smaller vertical space)
│    [Target language line]       │ ← Line 2 (immediately below)
└─────────────────────────────────┘
  ↑ MarginV=30px from bottom
```

**Line Spacing**: FFmpeg libass automatically calculates appropriate spacing between the two lines based on font size. The two lines are rendered as a single subtitle unit with automatic vertical stacking.

**Sources**: [references/subtitle-formatting.md:196-210]()

---

## Common Issues and Solutions

### Issue: Subtitles Display as Gibberish

**Cause**: Incorrect encoding (not UTF-8)

**Solution**: Convert to UTF-8 without BOM
```bash
iconv -f GBK -t UTF-8 input.srt > output.srt
sed -i '1s/^\xEF\xBB\xBF//' output.srt  # Remove BOM if present
```

**Sources**: [references/subtitle-formatting.md:397-411]()

### Issue: Chinese Text Too Crowded

**Cause**: Font size too small for bilingual display

**Solution**: Increase font size and bottom margin in `.env`:
```bash
SUBTITLE_FONT_SIZE=28
SUBTITLE_MARGIN_V=40
```

**Sources**: [references/subtitle-formatting.md:417-422]()

### Issue: Timestamp Format Errors

**Cause**: VTT format (`.` separator) used instead of SRT (`,` separator)

**Solution**: The conversion process in `extract_subtitle_clip.py` handles this automatically by replacing `.` with `,` in timestamp strings.

**Sources**: [references/subtitle-formatting.md:94-104]()

---

## Integration with Other Components

### Relationship to Batch Translation

The bilingual subtitle format is the output product of the batch translation process. The [Batch Translation Optimization](#7.1) system groups 20-25 subtitle lines together for translation, and the results are merged line-by-line with the original English text to create the bilingual format.

### Relationship to Subtitle Burning

The bilingual SRT file serves as input to the `burn_subtitles.py` script (see [burn_subtitles.py](#4.4)), which uses FFmpeg to hardcode the subtitles into the video file. The burning process applies the style configuration to render both lines simultaneously.

### Relationship to Format Conversion

The bilingual subtitle generation process includes VTT-to-SRT conversion as a preliminary step. For details on the conversion logic, see [Subtitle Format Conversion](#7.4).

**Sources**: [SKILL.md:163-234]()

---

# Page: Subtitle Format Conversion

# Subtitle Format Conversion

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/subtitle-formatting.md](references/subtitle-formatting.md)
- [scripts/extract_subtitle_clip.py](scripts/extract_subtitle_clip.py)

</details>



This document describes the subtitle format conversion system used in YouTube Clipper Skill, specifically the transformation from VTT (WebVTT) format to SRT (SubRip) format. The conversion process handles timestamp format differences, time adjustment for video segments, and encoding normalization.

For information about how subtitles are downloaded, see [Video Download Settings](#6.2). For subtitle burning and styling, see [Bilingual Subtitle Format](#7.3).

## Purpose and Scope

The subtitle format conversion system serves two primary functions:

1. **Format Normalization**: Converts YouTube's native VTT subtitle format to the widely-compatible SRT format used by FFmpeg's subtitle burning filters
2. **Time Adjustment**: Recalculates subtitle timestamps relative to extracted video clip boundaries, ensuring subtitles align with clipped segments

The conversion is implemented in [scripts/extract_subtitle_clip.py]() and processes subtitle data during the video clipping workflow.

Sources: [scripts/extract_subtitle_clip.py:1-115](), [TECHNICAL_NOTES.md:166-213]()

## Format Specifications

### VTT Format Structure

VTT (Web Video Text Tracks) is YouTube's default subtitle format with the following characteristics:

| Component | Specification |
|-----------|--------------|
| File Header | Mandatory `WEBVTT` line |
| Timestamp Delimiter | Period (`.`) for milliseconds |
| Style Support | Yes (CSS-like cues) |
| Position Control | Yes (align, position, line) |
| Sequence Numbers | Optional |

**Example VTT Structure:**
```
WEBVTT

1
00:00:00.000 --> 00:00:03.500
First subtitle text

2
00:00:03.500 --> 00:00:07.000
Second subtitle text
```

Sources: [references/subtitle-formatting.md:7-53](), [TECHNICAL_NOTES.md:166-176]()

### SRT Format Structure

SRT (SubRip) is the conversion target format with these characteristics:

| Component | Specification |
|-----------|--------------|
| File Header | None |
| Timestamp Delimiter | Comma (`,`) for milliseconds |
| Style Support | No (but FFmpeg can override) |
| Position Control | No |
| Sequence Numbers | Mandatory (sequential from 1) |

**Example SRT Structure:**
```
1
00:00:00,000 --> 00:00:03,500
First subtitle text

2
00:00:03,500 --> 00:00:07,000
Second subtitle text
```

Sources: [references/subtitle-formatting.md:55-91](), [TECHNICAL_NOTES.md:166-176]()

### Format Comparison Matrix

| Attribute | VTT | SRT |
|-----------|-----|-----|
| Millisecond Separator | `.` (period) | `,` (comma) |
| Header Required | `WEBVTT` | None |
| Metadata Support | Yes (STYLE, NOTE) | No |
| Speaker Tags | `<v Name>text</v>` | Plain text only |
| FFmpeg Compatibility | Limited | Full |

Sources: [references/subtitle-formatting.md:94-104]()

## Conversion Pipeline

### Overall Process Flow

```mermaid
flowchart TB
    Input["VTT File<br/>(YouTube download)"]
    Parse["parse_vtt_time()<br/>Extract timestamps"]
    Filter["Time Range Filter<br/>(start_seconds - end_seconds)"]
    Adjust["Time Adjustment<br/>(subtract offset)"]
    Format["format_srt_time()<br/>Convert to SRT format"]
    Output["SRT File<br/>(FFmpeg-compatible)"]
    
    Input --> Parse
    Parse --> Filter
    Filter --> Adjust
    Adjust --> Format
    Format --> Output
    
    subgraph "extract_subtitle_clip.py"
        Parse
        Filter
        Adjust
        Format
    end
```

**Conversion Pipeline Flow**

Sources: [scripts/extract_subtitle_clip.py:33-102]()

### Code Entity Mapping

```mermaid
flowchart LR
    subgraph "Input Processing"
        VTT["VTT File"]
        ReadLines["open(vtt_file, 'r')"]
        Lines["lines list"]
    end
    
    subgraph "Core Functions"
        ParseTime["parse_vtt_time(time_str)"]
        FormatTime["format_srt_time(seconds)"]
        ExtractClip["extract_subtitle_clip()"]
    end
    
    subgraph "Data Structures"
        SubDict["subtitles dict<br/>{start, end, text}"]
        AdjustedTime["adjusted_start<br/>adjusted_end"]
    end
    
    subgraph "Output Generation"
        SRTWrite["f.write() loops"]
        SRTFile["output_file.srt"]
    end
    
    VTT --> ReadLines
    ReadLines --> Lines
    Lines --> ExtractClip
    ExtractClip --> ParseTime
    ExtractClip --> SubDict
    SubDict --> AdjustedTime
    AdjustedTime --> FormatTime
    FormatTime --> SRTWrite
    SRTWrite --> SRTFile
```

**Function and Data Structure Relationships**

Sources: [scripts/extract_subtitle_clip.py:10-102]()

## Implementation Details

### Time Parsing Function

The `parse_vtt_time()` function converts VTT timestamp strings to seconds:

**Implementation:** [scripts/extract_subtitle_clip.py:10-22]()

**Parsing Logic:**
1. Splits timestamp by `:` delimiter
2. Handles two formats:
   - `HH:MM:SS.mmm` (3 parts): hours, minutes, seconds
   - `MM:SS.mmm` (2 parts): minutes, seconds only
3. Returns total seconds as float

**Example Transformations:**
- `00:02:30.500` → `150.5` seconds
- `05:47.250` → `347.25` seconds
- `01:23:45.678` → `5025.678` seconds

The function accepts period-delimited milliseconds (VTT format) in input and performs direct numeric conversion.

Sources: [scripts/extract_subtitle_clip.py:10-22](), [TECHNICAL_NOTES.md:177-184]()

### Time Formatting Function

The `format_srt_time()` function converts seconds back to SRT timestamp format:

**Implementation:** [scripts/extract_subtitle_clip.py:24-31]()

**Formatting Process:**

```mermaid
flowchart LR
    Input["seconds (float)"]
    TD["timedelta(seconds)"]
    Hours["hours = total // 3600"]
    Minutes["minutes = (total % 3600) // 60"]
    Seconds["secs = total % 60"]
    Millis["millis = (fraction * 1000)"]
    Format["f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'"]
    
    Input --> TD
    TD --> Hours
    TD --> Minutes
    TD --> Seconds
    TD --> Millis
    Hours --> Format
    Minutes --> Format
    Seconds --> Format
    Millis --> Format
```

**Key Transformation:**
- Uses `timedelta` for reliable time arithmetic
- Extracts components via modulo operations
- Formats with zero-padding (`:02d`, `:03d`)
- **Changes delimiter from `.` to `,` for milliseconds**

**Example Output:**
- `150.5` seconds → `00:02:30,500`
- `5025.678` seconds → `01:23:45,678`

Sources: [scripts/extract_subtitle_clip.py:24-31](), [TECHNICAL_NOTES.md:177-184]()

### Main Extraction Algorithm

The `extract_subtitle_clip()` function implements the complete conversion:

**Implementation:** [scripts/extract_subtitle_clip.py:33-102]()

**Algorithm Steps:**

| Step | Operation | Code Location |
|------|-----------|---------------|
| 1. Parse time range | Convert start/end strings to seconds | Lines 36-37 |
| 2. Read VTT file | Load all lines into memory | Lines 45-46 |
| 3. Scan for timestamps | Find lines containing `-->` | Lines 55 |
| 4. Extract time boundaries | Parse start/end for each subtitle | Lines 58-62 |
| 5. Filter by range | Check if `start >= range_start AND end <= range_end` | Lines 65 |
| 6. Collect text | Gather non-empty lines after timestamp | Lines 67-73 |
| 7. Adjust timestamps | Subtract clip start time from all timestamps | Lines 76-77 |
| 8. Write SRT format | Generate sequence numbers and formatted output | Lines 90-95 |

**Range Filtering Logic:**
```python
if sub_start >= start_seconds and sub_end <= end_seconds:
    # Include subtitle in output
```

Only subtitles fully contained within the specified time range are included. Partial overlaps are excluded to prevent truncated content.

Sources: [scripts/extract_subtitle_clip.py:33-102](), [TECHNICAL_NOTES.md:214-258]()

## Time Adjustment for Clipped Segments

### Adjustment Necessity

When a video segment is extracted (e.g., 2:00-2:10 from original video), subtitle timestamps must be recalculated relative to the new zero point.

**Problem Scenario:**

```mermaid
flowchart TB
    subgraph "Original Video Timeline"
        O1["00:00:00<br/>Video Start"]
        O2["00:02:00<br/>Clip Start"]
        O3["00:02:05<br/>Subtitle X"]
        O4["00:02:10<br/>Clip End"]
        O5["00:30:00<br/>Video End"]
    end
    
    subgraph "Clipped Segment Timeline"
        C1["00:00:00<br/>New Start"]
        C2["00:00:05<br/>Subtitle X (adjusted)"]
        C3["00:00:10<br/>New End"]
    end
    
    O2 -.->|"Extract segment"| C1
    O3 -.->|"Adjust: 2:05 - 2:00 = 0:05"| C2
    O4 -.->|"Maps to"| C3
```

**Timeline Adjustment Logic**

Sources: [TECHNICAL_NOTES.md:214-258]()

### Adjustment Implementation

**Code Location:** [scripts/extract_subtitle_clip.py:76-77]()

```python
adjusted_start = sub_start - start_seconds
adjusted_end = sub_end - start_seconds
```

**Mathematical Formula:**
- `adjusted_time = original_time - clip_start_time`
- Result is clamped to `max(0.0, adjusted_time)` to prevent negative timestamps

**Example Calculation:**

| Original Timestamp | Clip Start | Calculation | Adjusted Timestamp |
|--------------------|------------|-------------|-------------------|
| 00:02:00 | 00:02:00 | 120 - 120 | 00:00:00 |
| 00:02:05 | 00:02:00 | 125 - 120 | 00:00:05 |
| 00:02:10 | 00:02:00 | 130 - 120 | 00:00:10 |

Sources: [scripts/extract_subtitle_clip.py:76-77](), [TECHNICAL_NOTES.md:233-250]()

### Boundary Case Handling

**Edge Cases:**

1. **Subtitle starts before clip**: Excluded by range filter `sub_start >= start_seconds`
2. **Subtitle ends after clip**: Excluded by range filter `sub_end <= end_seconds`
3. **Subtitle partially overlaps**: Excluded (conservative approach prevents truncation)
4. **Empty time range**: Results in zero subtitles extracted

The implementation uses strict boundary checking to ensure only complete, fully-contained subtitles are included in the output.

Sources: [scripts/extract_subtitle_clip.py:65](), [TECHNICAL_NOTES.md:251-258]()

## Encoding and Special Character Handling

### Character Encoding

**Standard:** UTF-8 without BOM (Byte Order Mark)

**Reading:** [scripts/extract_subtitle_clip.py:45]()
```python
open(vtt_file, 'r', encoding='utf-8')
```

**Writing:** [scripts/extract_subtitle_clip.py:90]()
```python
open(output_file, 'w', encoding='utf-8')
```

All file operations explicitly specify UTF-8 encoding to ensure consistent handling of international characters in subtitle text.

Sources: [scripts/extract_subtitle_clip.py:45,90](), [references/subtitle-formatting.md:305-328]()

### VTT Metadata Removal

During conversion, the following VTT-specific elements are stripped:

| Element | Pattern | Reason |
|---------|---------|--------|
| WEBVTT Header | Line 1 of file | SRT has no header |
| Position Tags | `align:start position:0%` | SRT doesn't support positioning |
| Speaker Tags | `<v SpeakerName>` | SRT uses plain text |
| Style Blocks | `STYLE { ... }` | SRT has no style support |
| NOTE Sections | `NOTE comment text` | SRT has no comment syntax |

The current implementation in `extract_subtitle_clip.py` handles these implicitly by:
- Not copying the WEBVTT header
- Ignoring metadata in timestamp lines (splits on `-->` and takes only time portions)
- Preserving only the text content lines

Sources: [scripts/extract_subtitle_clip.py:55-73](), [references/subtitle-formatting.md:112-145](), [TECHNICAL_NOTES.md:207-211]()

## Integration with Workflow

### Usage in Processing Pipeline

The `extract_subtitle_clip.py` script is invoked during video clipping operations when subtitle extraction is requested:

**Command-Line Interface:**
```bash
python extract_subtitle_clip.py <vtt_file> <start_time> <end_time> <output_file>
```

**Example:**
```bash
python extract_subtitle_clip.py video.en.vtt 00:05:47 00:09:19 chapter_01.srt
```

**Parameters:**
- `vtt_file`: Downloaded VTT subtitle from yt-dlp
- `start_time`: Chapter start timestamp (HH:MM:SS format)
- `end_time`: Chapter end timestamp (HH:MM:SS format)
- `output_file`: Output SRT file path

Sources: [scripts/extract_subtitle_clip.py:103-114]()

### Workflow Integration Diagram

```mermaid
flowchart TB
    Download["download_video.py<br/>Downloads VTT subtitles"]
    Analyze["analyze_subtitles.py<br/>Identifies chapter boundaries"]
    Clip["clip_video.py<br/>Extracts video segments"]
    ExtractSub["extract_subtitle_clip.py<br/>Converts VTT → SRT<br/>Adjusts timestamps"]
    Translate["Translation module<br/>Optional bilingual generation"]
    Burn["burn_subtitles.py<br/>Embeds SRT into video"]
    
    Download --> Analyze
    Analyze --> Clip
    Download -.->|"VTT file"| ExtractSub
    Analyze -.->|"Chapter times"| ExtractSub
    Clip --> ExtractSub
    ExtractSub --> Translate
    ExtractSub --> Burn
    Translate --> Burn
    
    style ExtractSub fill:#f0f0f0
```

**Position in Processing Pipeline**

The conversion occurs after video clipping but before optional translation and subtitle burning, ensuring SRT files are available for downstream processing.

Sources: [scripts/extract_subtitle_clip.py:1-115](), Architecture Diagrams

## Output Format Validation

### SRT Structure Requirements

Generated SRT files must conform to the following structure:

**Sequential Block Format:**
```
<sequence_number>
<start_time> --> <end_time>
<text_line_1>
[<text_line_n>]
<blank_line>
```

**Implementation:** [scripts/extract_subtitle_clip.py:90-95]()

```python
for idx, sub in enumerate(subtitles, 1):
    f.write(f"{idx}\n")
    f.write(f"{format_srt_time(sub['start'])} --> {format_srt_time(sub['end'])}\n")
    f.write(f"{sub['text']}\n")
    f.write("\n")
```

**Validation Points:**
1. Sequence numbers start at 1 and increment sequentially
2. Timestamps use comma delimiter: `HH:MM:SS,mmm`
3. Each subtitle block ends with blank line separator
4. Text preserves original formatting (single line in this implementation)

Sources: [scripts/extract_subtitle_clip.py:90-95](), [references/subtitle-formatting.md:60-91]()

### Output Verification

The script prints conversion statistics:

**Console Output:** [scripts/extract_subtitle_clip.py:39-43,87,97-99]()

```
📝 提取字幕片段...
   输入: video.en.vtt
   时间范围: 00:05:47 - 00:09:19
   时间范围（秒）: 347.0s - 559.0s
   找到 42 条字幕
✅ 字幕提取完成
   输出文件: chapter_01.srt
   字幕条数: 42
```

This feedback enables verification that the correct time range was processed and the expected number of subtitles was extracted.

Sources: [scripts/extract_subtitle_clip.py:39-43,87,97-99]()

---

# Page: Troubleshooting

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FIXES_AND_IMPROVEMENTS.md](FIXES_AND_IMPROVEMENTS.md)
- [README.md](README.md)
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)

</details>



This page provides solutions to common problems encountered during installation, configuration, and operation of the YouTube Clipper Skill. Each section includes diagnostic steps, error message patterns, and verified solutions.

For configuration options to prevent issues, see [Configuration](#6). For installation procedures, see [Installation](#2.1). For detailed technical background on specific problems, see [FFmpeg Integration](#5.2) and [libass Requirement](#5.3).

---

## Problem Diagnosis Flowchart

```mermaid
flowchart TD
    Start["Issue Encountered"]
    
    Start --> Type{Issue Type?}
    
    Type -->|Installation| InstallCheck["Check dependency presence"]
    Type -->|Runtime| RuntimeCheck["Check error message"]
    Type -->|Output| OutputCheck["Check file generation"]
    
    InstallCheck --> PythonMissing{Python 3.8+?}
    InstallCheck --> DepMissing{Dependencies installed?}
    
    PythonMissing -->|No| InstallPython["Install Python 3.8+"]
    DepMissing -->|No| InstallDeps["Run install_as_skill.sh"]
    
    RuntimeCheck --> ErrorType{Error Pattern?}
    
    ErrorType -->|ModuleNotFoundError| Section81["See 8.1: Installation Issues"]
    ErrorType -->|"No such filter: subtitles"| Section82["See 8.2: FFmpeg Problems"]
    ErrorType -->|Download failed| Section83["See 8.3: Network Issues"]
    ErrorType -->|"Unable to find"| Section84["See 8.4: Path Issues"]
    
    OutputCheck --> FilesMissing{Files created?}
    FilesMissing -->|No| CheckLogs["Check error output"]
    FilesMissing -->|Partial| CheckPhase["Identify failed phase"]
    
    CheckPhase --> Phase1["download_video.py"]
    CheckPhase --> Phase2["analyze_subtitles.py"]
    CheckPhase --> Phase3["clip_video.py"]
    CheckPhase --> Phase4["burn_subtitles.py"]
    
    style Section81 fill:#f9f9f9
    style Section82 fill:#f9f9f9
    style Section83 fill:#f9f9f9
    style Section84 fill:#f9f9f9
```

Sources: [README.md:236-278](), [FIXES_AND_IMPROVEMENTS.md:1-293](), [TECHNICAL_NOTES.md:1-490]()

---

## Installation Issues

### Python Dependency Missing

**Error Pattern:**
```
ModuleNotFoundError: No module named 'yt_dlp'
ModuleNotFoundError: No module named 'pysrt'
ModuleNotFoundError: No module named 'dotenv'
```

**Diagnostic Check:**
```bash
python3 -c "import yt_dlp; import pysrt; from dotenv import load_dotenv"
```

**Root Cause:**
Python environment is externally-managed (common on macOS) and blocks `pip install` without flags.

**Solution:**

| Platform | Command | Notes |
|----------|---------|-------|
| macOS | `pip3 install --break-system-packages yt-dlp pysrt python-dotenv` | Bypasses external management restriction |
| Ubuntu/Debian | `pip3 install yt-dlp pysrt python-dotenv` | Usually no restriction |
| Virtual Environment | `pip install yt-dlp pysrt python-dotenv` | Recommended approach |

**Alternative: Use Virtual Environment:**
```bash
cd ~/.claude/skills/youtube-clipper
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install yt-dlp pysrt python-dotenv
```

Sources: [FIXES_AND_IMPROVEMENTS.md:9-25](), [README.md:60-66]()

---

### System Dependency Verification

**Dependency Check Script:**

```mermaid
flowchart LR
    Check["Dependency Verification"]
    
    Check --> Python["python3 --version"]
    Check --> YtDlp["yt-dlp --version"]
    Check --> FFmpeg["ffmpeg -version"]
    
    Python --> PythonVer{">= 3.8?"}
    YtDlp --> YtDlpExists{"Installed?"}
    FFmpeg --> FFmpegExists{"Installed?"}
    
    PythonVer -->|No| InstallPy["Install Python 3.8+"]
    YtDlpExists -->|No| InstallYt["Install yt-dlp"]
    FFmpegExists -->|No| InstallFF["Install FFmpeg"]
    
    FFmpegExists -->|Yes| LibassCheck["ffmpeg -filters 2>&1 | grep subtitles"]
    LibassCheck --> HasLibass{"Has libass?"}
    HasLibass -->|No| InstallFull["Install ffmpeg-full (macOS)<br/>or libass-dev (Linux)"]
    
    PythonVer -->|Yes| Ready["Ready"]
    YtDlpExists -->|Yes| Ready
    HasLibass -->|Yes| Ready
```

**Verification Commands:**

| Dependency | Check Command | Expected Output |
|------------|--------------|-----------------|
| Python | `python3 --version` | `Python 3.8.x` or higher |
| yt-dlp | `yt-dlp --version` | Version number (e.g., `2024.01.01`) |
| FFmpeg | `ffmpeg -version` | Version and configuration info |
| libass | `ffmpeg -filters 2>&1 \| grep subtitles` | Line containing `subtitles` filter |

Sources: [README.md:50-84](), [install_as_skill.sh]()

---

## FFmpeg and libass Problems

### Missing libass Filter Support

**Error Patterns:**
```
[AVFilterGraph @ 0x...] No such filter: 'subtitles'
Option not found: subtitles
```

**Diagnostic Check:**
```bash
ffmpeg -filters 2>&1 | grep subtitles
# Expected output: subtitles    V->V  Render text subtitles onto input video
# No output = libass not supported
```

**Component Dependency Chain:**

```mermaid
flowchart TB
    BurnScript["burn_subtitles.py"]
    
    BurnScript --> DetectFunc["detect_ffmpeg_variant()"]
    
    DetectFunc --> CheckMac{"macOS?"}
    
    CheckMac -->|Yes| FullPath["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
    CheckMac -->|No| StdPath["shutil.which('ffmpeg')"]
    
    FullPath --> FullExists{"Exists?"}
    StdPath --> StdExists{"Exists?"}
    
    FullExists -->|Yes| CheckLibassFull["check_libass_support(full_path)"]
    FullExists -->|No| StdPath
    
    StdExists -->|Yes| CheckLibassStd["check_libass_support(std_path)"]
    StdExists -->|No| Error["Error: FFmpeg not found"]
    
    CheckLibassFull --> HasLibass1{"Has libass?"}
    CheckLibassStd --> HasLibass2{"Has libass?"}
    
    HasLibass1 -->|Yes| UseFFmpeg["Use FFmpeg for burning"]
    HasLibass1 -->|No| ErrorLibass["Error: libass not supported"]
    
    HasLibass2 -->|Yes| UseFFmpeg
    HasLibass2 -->|No| ErrorLibass
```

**Platform-Specific Solutions:**

| Platform | Issue | Solution |
|----------|-------|----------|
| macOS (Homebrew) | Standard `ffmpeg` lacks libass | `brew uninstall ffmpeg && brew install ffmpeg-full` |
| macOS (Apple Silicon) | Path not found | FFmpeg at `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` |
| macOS (Intel) | Path not found | FFmpeg at `/usr/local/opt/ffmpeg-full/bin/ffmpeg` |
| Ubuntu/Debian | Missing library | `sudo apt install ffmpeg libass-dev` |
| From source | Not configured | Compile with `--enable-libass` flag |

**Code References:**
- FFmpeg variant detection: [scripts/burn_subtitles.py:67-79]()
- libass verification: [scripts/burn_subtitles.py:43-65]()

Sources: [TECHNICAL_NOTES.md:5-80](), [README.md:67-84](), [scripts/burn_subtitles.py]()

---

### File Path with Spaces Issue

**Error Pattern:**
```
[Parsed_subtitles_0 @ 0x...] Unable to find '/path/with'
```

**Problem:** FFmpeg `subtitles` filter truncates paths at first space character, even with quoting or escaping.

**Failed Attempts:**
- ❌ `subtitles="/path/with spaces/sub.srt"`
- ❌ `subtitles='/path/with spaces/sub.srt'`
- ❌ `subtitles=/path/with\ spaces/sub.srt`
- ❌ `subtitles="'/path/with spaces/sub.srt'"`

**Solution: Temporary Directory Workaround**

```mermaid
flowchart LR
    Input["Input Files<br/>(May have spaces)"]
    
    Input --> CreateTemp["tempfile.mkdtemp()<br/>prefix='youtube_clipper_'"]
    
    CreateTemp --> TempDir["Temp Directory<br/>(No spaces)<br/>/tmp/youtube_clipper_abc123"]
    
    TempDir --> Copy["shutil.copy()<br/>video.mp4<br/>subtitle.srt"]
    
    Copy --> FFmpegCmd["FFmpeg Command<br/>subtitles=temp_dir/subtitle.srt"]
    
    FFmpegCmd --> Process["FFmpeg Processing"]
    
    Process --> MoveOut["shutil.move()<br/>to output_path"]
    
    MoveOut --> Cleanup["shutil.rmtree(temp_dir)"]
    
    Cleanup --> Output["Output File<br/>(Original path restored)"]
```

**Implementation:**
[scripts/burn_subtitles.py:115-175]() implements the temporary directory solution:

1. Creates temp directory with `tempfile.mkdtemp(prefix='youtube_clipper_')`
2. Copies input files to temp directory
3. Runs FFmpeg with space-free paths
4. Moves output back to original path
5. Cleans up temp directory in `finally` block

Sources: [TECHNICAL_NOTES.md:82-163](), [scripts/burn_subtitles.py:115-175]()

---

## Download and Network Issues

### Download Progress Errors

**Error Pattern:**
```python
TypeError: unsupported operand type(s) for /: 'int' and 'NoneType'
```

**Root Cause:**
Some videos do not provide `total_bytes` during download, causing division by `None` in progress calculation at [scripts/download_video.py:161]().

**Fix Applied:**
```python
# Before (causes error)
if 'downloaded_bytes' in d and 'total_bytes' in d:
    percent = d['downloaded_bytes'] / d['total_bytes'] * 100

# After (null-safe)
if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes']:
    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
else:
    # Fallback: show downloaded size without percentage
    downloaded_mb = d.get('downloaded_bytes', 0) / 1024 / 1024
    print(f"  Downloaded: {downloaded_mb:.1f} MB")
```

**Code Reference:** [scripts/download_video.py:156-178]()

Sources: [FIXES_AND_IMPROVEMENTS.md:28-55]()

---

### Network and Proxy Configuration

**Slow Download Issues:**

| Symptom | Cause | Solution |
|---------|-------|----------|
| Very slow download (<100 KB/s) | Network throttling | Set `YT_DLP_PROXY` in `.env` |
| Intermittent failures | Region restrictions | Use proxy in target region |
| Connection timeout | Network instability | Increase timeout in yt-dlp options |

**Proxy Configuration:**

Edit `~/.claude/skills/youtube-clipper/.env`:

```bash
# HTTP proxy
YT_DLP_PROXY=http://proxy-server:port

# SOCKS5 proxy (better for video streaming)
YT_DLP_PROXY=socks5://proxy-server:port

# With authentication
YT_DLP_PROXY=http://username:password@proxy-server:port
```

**Rate Limiting:**

```bash
# Limit download speed (in bytes/second)
# Example: 1MB/s = 1048576
YT_DLP_RATE_LIMIT=1048576
```

Sources: [README.md:253-259](), [.env.example]()

---

### Subtitle Translation Failures

**Error Patterns:**
```
API rate limiting exceeded
Network connection timeout
Translation request failed after 3 retries
```

**Troubleshooting Decision Tree:**

```mermaid
flowchart TD
    TransError["Translation Error"]
    
    TransError --> CheckNet["Check network connectivity"]
    
    CheckNet --> NetOK{"Network OK?"}
    
    NetOK -->|No| FixNet["Fix network connection"]
    NetOK -->|Yes| CheckAPI["Check Claude API status"]
    
    CheckAPI --> APIOK{"API accessible?"}
    
    APIOK -->|No| WaitAPI["Wait for API service<br/>Check status.anthropic.com"]
    APIOK -->|Yes| CheckBatch["Check TRANSLATION_BATCH_SIZE"]
    
    CheckBatch --> BatchSize{"Current size?"}
    
    BatchSize -->|"> 25"| ReduceBatch["Set TRANSLATION_BATCH_SIZE=20<br/>in .env"]
    BatchSize -->|"<= 25"| CheckRate["Check rate limiting"]
    
    CheckRate --> TooMany{"Too many<br/>requests?"}
    
    TooMany -->|Yes| AddDelay["Add delay between batches<br/>or reduce batch size"]
    TooMany -->|No| CheckContent["Review subtitle content<br/>for special characters"]
    
    ReduceBatch --> Retry["Retry translation"]
    AddDelay --> Retry
    CheckContent --> Retry
```

**Configuration Adjustments:**

| Issue | Current Value | Recommended Change |
|-------|--------------|-------------------|
| Large batch timeouts | `TRANSLATION_BATCH_SIZE=25` | Reduce to `20` |
| Frequent rate limits | `TRANSLATION_BATCH_SIZE=20` | Reduce to `15` |
| Special character errors | Default encoding | Check subtitle encoding |

**Code Reference:**
- Batch translation logic: [scripts/extract_subtitle_clip.py]()
- Retry mechanism: Automatic (3 attempts)

Sources: [README.md:261-269](), [TECHNICAL_NOTES.md:261-305]()

---

## File Path and Encoding Issues

### Special Characters in Filenames

**Problem:**
YouTube video titles may contain characters invalid for file systems: `/ \ : * ? " < > |`

**Original Issue:**
```
Anthropic's Amodei on AI： Power and Risk [Ckt1cj0xjRM].mp4
                      ↑ Full-width colon (invalid)
       ↑ Apostrophe (can cause shell issues)
```

**Solution Applied:**
Changed output template to use video ID only at [scripts/download_video.py:67]():

```python
# Before (uses title with special characters)
'outtmpl': '%(title)s [%(id)s].%(ext)s'

# After (uses video ID only)
'outtmpl': '%(id)s.%(ext)s'
```

**File Naming Pattern:**

| File Type | Naming Convention | Example |
|-----------|------------------|---------|
| Downloaded video | `{video_id}.mp4` | `Ckt1cj0xjRM.mp4` |
| Downloaded subtitle | `{video_id}.{lang}.vtt` | `Ckt1cj0xjRM.en.vtt` |
| Clipped segment | `{sanitized_title}_clip.mp4` | `Chapter_Title_clip.mp4` |
| Bilingual subtitle | `{sanitized_title}_bilingual.srt` | `Chapter_Title_bilingual.srt` |

**Filename Sanitization Function:**

[scripts/utils.py]() implements `sanitize_filename()`:
- Removes characters: `/ \ : * ? " < > |`
- Replaces spaces with underscores
- Limits length to 100 characters
- Preserves video ID for traceability

Sources: [FIXES_AND_IMPROVEMENTS.md:58-93](), [scripts/download_video.py:67](), [scripts/utils.py]()

---

### Subtitle Format and Encoding Issues

**VTT to SRT Conversion Issues:**

```mermaid
flowchart LR
    VTT["VTT Format<br/>WEBVTT header<br/>Timestamp: HH:MM:SS.mmm"]
    
    VTT --> Convert["vtt_to_srt()"]
    
    Convert --> RemoveHeader["Remove 'WEBVTT' header"]
    RemoveHeader --> RemoveStyle["Remove STYLE blocks"]
    RemoveStyle --> ConvertTime["Convert . to , in timestamps"]
    ConvertTime --> AddNumbers["Add sequence numbers"]
    
    AddNumbers --> SRT["SRT Format<br/>No header<br/>Timestamp: HH:MM:SS,mmm"]
    
    SRT --> Validate["Validate encoding"]
    Validate --> Output["UTF-8 SRT file"]
```

**Common Conversion Problems:**

| Issue | Symptom | Solution |
|-------|---------|----------|
| Wrong delimiter | `00:00:01.500` instead of `00:00:01,500` | Regex replace `.` with `,` in timestamps |
| Missing sequence numbers | Subtitles not numbered | Add sequential numbers (1, 2, 3...) |
| Style tags included | `<c.white>Text</c>` in output | Strip all HTML/XML tags |
| Encoding errors | Garbled characters | Ensure UTF-8 encoding when writing |

**Timestamp Adjustment:**

After clipping video segment from `start_time` to `end_time`:

1. Filter subtitles within time range: [scripts/extract_subtitle_clip.py]()
2. Adjust timestamps: `new_time = original_time - start_time`
3. Ensure no negative timestamps: `max(0.0, adjusted_time)`
4. Verify end time doesn't exceed clip duration

**Code References:**
- VTT parsing: [scripts/analyze_subtitles.py]()
- Timestamp adjustment: [scripts/extract_subtitle_clip.py]()
- Encoding handling: [scripts/utils.py]()

Sources: [TECHNICAL_NOTES.md:165-213](), [TECHNICAL_NOTES.md:215-258]()

---

## Output Directory Issues

### Incorrect Output Location

**Expected vs Actual:**

| Configuration | Expected Output | Common Issue |
|--------------|----------------|--------------|
| Default | `./youtube-clips/` (current working directory) | May create in `/tmp/` or `~/Videos/` |
| Custom `OUTPUT_DIR` | Path specified in `.env` | Path not recognized |

**Solution:**

1. Verify current working directory:
   ```bash
   pwd
   ```

2. Check `.env` configuration:
   ```bash
   cat ~/.claude/skills/youtube-clipper/.env | grep OUTPUT_DIR
   ```

3. Set explicit output directory:
   ```bash
   # In .env file
   OUTPUT_DIR=/absolute/path/to/output
   
   # Or relative to current directory
   OUTPUT_DIR=./my-clips
   ```

**Default Behavior:**
[scripts/utils.py:131-148]() defines `create_output_dir()`:
- If `OUTPUT_DIR` not set: uses `Path.cwd() / "youtube-clips"`
- Creates timestamped subdirectory: `YYYYMMDD_HHMMSS/`
- Returns absolute path for all operations

Sources: [FIXES_AND_IMPROVEMENTS.md:96-135](), [scripts/utils.py:131-148]()

---

## Common Error Messages Reference

| Error Message | Script | Section | Quick Fix |
|--------------|--------|---------|-----------|
| `ModuleNotFoundError: No module named 'yt_dlp'` | All | [8.1](#installation-issues) | `pip3 install --break-system-packages yt-dlp` |
| `No such filter: 'subtitles'` | `burn_subtitles.py` | [8.2](#ffmpeg-and-libass-problems) | `brew install ffmpeg-full` (macOS) |
| `Unable to find '/path/with'` | `burn_subtitles.py` | [8.2](#ffmpeg-and-libass-problems) | Fixed via temp directory (automatic) |
| `TypeError: unsupported operand type(s) for /` | `download_video.py` | [8.3](#download-and-network-issues) | Fixed in latest version |
| `Translation request failed after 3 retries` | `extract_subtitle_clip.py` | [8.3](#download-and-network-issues) | Check network, reduce `TRANSLATION_BATCH_SIZE` |
| Special characters in filename | `download_video.py` | [8.4](#file-path-and-encoding-issues) | Fixed via video ID naming |

Sources: [README.md:236-278](), [FIXES_AND_IMPROVEMENTS.md:1-293](), [TECHNICAL_NOTES.md:1-490]()

---

## Verification After Fixes

**System Health Check:**

```mermaid
flowchart TD
    Start["Run Health Check"]
    
    Start --> Test1["python3 -c 'import yt_dlp, pysrt'"]
    Test1 --> Test1OK{"Success?"}
    Test1OK -->|No| FixDeps["Install Python packages"]
    Test1OK -->|Yes| Test2
    
    Test2["ffmpeg -filters 2>&1 | grep subtitles"]
    Test2 --> Test2OK{"Output found?"}
    Test2OK -->|No| FixFFmpeg["Install ffmpeg-full or libass"]
    Test2OK -->|Yes| Test3
    
    Test3["yt-dlp --version"]
    Test3 --> Test3OK{"Success?"}
    Test3OK -->|No| FixYtDlp["Install yt-dlp"]
    Test3OK -->|Yes| Test4
    
    Test4["Test with sample video"]
    Test4 --> Test4OK{"All files<br/>created?"}
    Test4OK -->|No| ReviewLogs["Review error logs"]
    Test4OK -->|Yes| Success["System Ready"]
    
    FixDeps --> Retest["Rerun health check"]
    FixFFmpeg --> Retest
    FixYtDlp --> Retest
    ReviewLogs --> Identify["Identify specific issue"]
```

**Test Command:**
```bash
# Navigate to any directory
cd ~/Desktop

# Test basic clip (in Claude Code)
Clip this YouTube video: https://youtube.com/watch?v=test_VIDEO_ID
```

**Expected Output Structure:**
```
./youtube-clips/
└── 20260122_143022/
    └── Chapter_Title/
        ├── Chapter_Title_clip.mp4
        ├── Chapter_Title_with_subtitles.mp4 (if subtitle burning enabled)
        ├── Chapter_Title_bilingual.srt
        └── Chapter_Title_summary.md
```

Sources: [README.md:112-124](), [SKILL.md]()

---

# Page: Installation Issues

# Installation Issues

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FIXES_AND_IMPROVEMENTS.md](FIXES_AND_IMPROVEMENTS.md)
- [README.md](README.md)
- [install_as_skill.sh](install_as_skill.sh)

</details>



This page documents common problems encountered during the installation of the YouTube Clipper Skill and provides solutions. Installation issues typically occur when running [install_as_skill.sh]() or when system dependencies are missing or misconfigured.

For runtime issues related to FFmpeg and subtitle burning, see [FFmpeg and libass Problems](#8.2). For download-related problems, see [Download and Network Issues](#8.3). For general system requirements, see [System Requirements](#1.2).

---

## Overview of Installation Process

The YouTube Clipper Skill installation involves multiple verification and setup steps. Understanding this flow helps diagnose where failures occur.

```mermaid
flowchart TB
    Start["User runs install_as_skill.sh"]
    
    CheckDir["Check ~/.claude/skills/youtube-clipper/"]
    DirExists{Directory exists?}
    Confirm["Prompt user for overwrite confirmation"]
    UserConfirm{User confirms?}
    DeleteOld["Delete existing directory"]
    
    CreateDir["Create skill directory<br/>mkdir -p $SKILL_DIR"]
    CopyFiles["Copy project files<br/>cp -r $SCRIPT_DIR/* $SKILL_DIR/"]
    CleanFiles["Remove .git, venv, __pycache__, etc."]
    
    CheckPython["Check python3 command"]
    PythonExists{Python 3 found?}
    InstallPython["ERROR: Install Python 3.8+"]
    
    CheckPip["Check pip3/pip command"]
    PipExists{pip found?}
    InstallPipError["ERROR: Install pip"]
    
    InstallDeps["pip3 install yt-dlp pysrt python-dotenv"]
    DepInstall{Installation success?}
    DepError["ERROR: Dependency installation failed"]
    
    CheckYtdlp["Check yt-dlp command"]
    YtdlpExists{yt-dlp CLI found?}
    WarnYtdlp["WARNING: yt-dlp CLI not installed"]
    
    CheckFFmpeg["Check ffmpeg command"]
    FFmpegExists{ffmpeg found?}
    WarnFFmpeg["WARNING: FFmpeg not installed"]
    
    CheckLibass["Check libass support<br/>ffmpeg -filters | grep subtitles"]
    LibassExists{libass supported?}
    WarnLibass["WARNING: libass not supported"]
    
    CreateEnv["Copy .env.example to .env"]
    Complete["Installation complete"]
    
    Start --> CheckDir
    CheckDir --> DirExists
    DirExists -->|Yes| Confirm
    DirExists -->|No| CreateDir
    Confirm --> UserConfirm
    UserConfirm -->|Yes| DeleteOld
    UserConfirm -->|No| InstallPython
    DeleteOld --> CreateDir
    
    CreateDir --> CopyFiles
    CopyFiles --> CleanFiles
    CleanFiles --> CheckPython
    
    CheckPython --> PythonExists
    PythonExists -->|No| InstallPython
    PythonExists -->|Yes| CheckPip
    
    CheckPip --> PipExists
    PipExists -->|No| InstallPipError
    PipExists -->|Yes| InstallDeps
    
    InstallDeps --> DepInstall
    DepInstall -->|No| DepError
    DepInstall -->|Yes| CheckYtdlp
    
    CheckYtdlp --> YtdlpExists
    YtdlpExists -->|No| WarnYtdlp
    YtdlpExists -->|Yes| CheckFFmpeg
    WarnYtdlp --> CheckFFmpeg
    
    CheckFFmpeg --> FFmpegExists
    FFmpegExists -->|No| WarnFFmpeg
    FFmpegExists -->|Yes| CheckLibass
    WarnFFmpeg --> CreateEnv
    
    CheckLibass --> LibassExists
    LibassExists -->|No| WarnLibass
    LibassExists -->|Yes| CreateEnv
    WarnLibass --> CreateEnv
    
    CreateEnv --> Complete
```

**Installation Flow Diagram**: Shows the complete verification and setup process implemented in install_as_skill.sh.

**Sources**: [install_as_skill.sh:56-241]()

---

## Python Environment Issues

### Externally-Managed Python Environment (macOS)

**Problem**: On modern macOS systems, Python is marked as "externally-managed" by the operating system, preventing standard `pip install` commands.

**Error Message**:
```
error: externally-managed-environment

This environment is externally managed
To install Python packages system-wide, try brew install xyz
```

**Solution**: Use the `--break-system-packages` flag with pip:

```bash
pip3 install --break-system-packages yt-dlp pysrt python-dotenv
```

**Why This Happens**: macOS Sonoma (14+) and Homebrew-installed Python use PEP 668 to prevent accidental modifications to system Python environments.

**Implementation in install_as_skill.sh**: The current script does not include the `--break-system-packages` flag. Users encountering this error must manually install dependencies with this flag.

**Locations**:
- Dependency installation: [install_as_skill.sh:127-137]()

**Sources**: [FIXES_AND_IMPROVEMENTS.md:9-25](), [install_as_skill.sh:127-137]()

---

### Missing Python 3

**Problem**: The system lacks Python 3.8 or higher.

**Error Message**:
```
❌ 未找到 Python 3，请先安装 Python 3.8+
```

**Detection Logic**: [install_as_skill.sh:110-117]()

```bash
if ! command_exists python3; then
    print_error "未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi
```

**Solutions by Platform**:

| Platform | Installation Command |
|----------|---------------------|
| **macOS** | `brew install python3` |
| **Ubuntu/Debian** | `sudo apt-get install python3 python3-pip` |
| **Windows** | Download from [python.org](https://www.python.org/downloads/) |
| **From Source** | [python.org/downloads/source](https://www.python.org/downloads/source/) |

**Verification**:
```bash
python3 --version
# Should output: Python 3.8.x or higher
```

**Sources**: [install_as_skill.sh:110-117](), [README.md:56-57]()

---

### Missing pip

**Problem**: Python is installed but pip (package manager) is missing.

**Error Message**:
```
❌ 未找到 pip，请先安装 pip
```

**Detection Logic**: [install_as_skill.sh:120-124]()

```bash
if ! command_exists pip3 && ! command_exists pip; then
    print_error "未找到 pip，请先安装 pip"
    exit 1
fi
```

**Solutions by Platform**:

| Platform | Installation Command |
|----------|---------------------|
| **macOS** | `python3 -m ensurepip --upgrade` |
| **Ubuntu/Debian** | `sudo apt-get install python3-pip` |
| **Manual** | `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`<br>`python3 get-pip.py` |

**Sources**: [install_as_skill.sh:120-124]()

---

## Python Package Installation Failures

### ModuleNotFoundError at Runtime

**Problem**: Installation script completes, but scripts fail with missing module errors.

**Error Messages**:
```python
ModuleNotFoundError: No module named 'yt_dlp'
ModuleNotFoundError: No module named 'pysrt'
ModuleNotFoundError: No module named 'dotenv'
```

**Cause**: Python packages were not successfully installed during setup.

**Diagnosis**:
```bash
# Check if packages are installed
python3 -c "import yt_dlp; print('yt_dlp OK')"
python3 -c "import pysrt; print('pysrt OK')"
python3 -c "import dotenv; print('dotenv OK')"
```

**Solution**: Manually install packages:
```bash
# Standard installation
pip3 install yt-dlp pysrt python-dotenv

# macOS externally-managed environment
pip3 install --break-system-packages yt-dlp pysrt python-dotenv

# Install to user directory (alternative)
pip3 install --user yt-dlp pysrt python-dotenv
```

**Package Purposes**:

| Package | Purpose | Used By |
|---------|---------|---------|
| `yt-dlp` | YouTube video/subtitle downloading | [scripts/download_video.py]() |
| `pysrt` | SRT subtitle parsing and manipulation | [scripts/extract_subtitle_clip.py]() |
| `python-dotenv` | Load configuration from .env file | All scripts |

**Sources**: [FIXES_AND_IMPROVEMENTS.md:9-25](), [install_as_skill.sh:127-137](), [README.md:60-65]()

---

## System Dependency Issues

### yt-dlp Command Not Found

**Problem**: The yt-dlp CLI tool is not installed, even though the Python package may be.

**Warning Message**:
```
⚠️  yt-dlp 命令行工具未安装
```

**Detection Logic**: [install_as_skill.sh:140-150]()

```bash
if command_exists yt-dlp; then
    YT_DLP_VERSION=$(yt-dlp --version)
    print_success "yt-dlp 已安装: $YT_DLP_VERSION"
else
    print_warning "yt-dlp 命令行工具未安装"
fi
```

**Important Distinction**: The Python package `yt_dlp` (installed by pip) and the CLI tool `yt-dlp` are different:
- **Python package**: Used by [scripts/download_video.py:25]() via `import yt_dlp`
- **CLI tool**: Can be invoked as standalone command

**Installation Options**:

| Method | Command | Provides |
|--------|---------|----------|
| **Homebrew (macOS)** | `brew install yt-dlp` | Both CLI and Python package |
| **APT (Ubuntu)** | `sudo apt-get install yt-dlp` | Both CLI and Python package |
| **pip** | `pip3 install yt-dlp` | Primarily Python package, may provide CLI |

**Recommended**: Use system package manager (brew/apt) for complete installation.

**Sources**: [install_as_skill.sh:140-150](), [README.md:57]()

---

### FFmpeg Not Installed

**Problem**: FFmpeg binary is not found on the system.

**Error Message**:
```
❌ FFmpeg 未安装
```

**Detection Logic**: [install_as_skill.sh:155-186]()

The installation script checks multiple locations:
1. `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` (Apple Silicon Mac with ffmpeg-full)
2. `/usr/local/opt/ffmpeg-full/bin/ffmpeg` (Intel Mac with ffmpeg-full)
3. `ffmpeg` command in PATH (standard installation)

**Installation by Platform**:

| Platform | Command | Notes |
|----------|---------|-------|
| **macOS** | `brew install ffmpeg-full` | Includes libass support |
| **Ubuntu/Debian** | `sudo apt-get install ffmpeg libass-dev` | Install both packages |
| **From Source** | See [FFmpeg compilation guide](https://trac.ffmpeg.org/wiki/CompilationGuide) | Advanced users |

**Why FFmpeg is Required**:
- Video clipping: [scripts/clip_video.py]()
- Subtitle burning: [scripts/burn_subtitles.py]()

**Note**: For subtitle burning functionality, FFmpeg must have libass support. See [FFmpeg and libass Problems](#8.2) for libass-specific issues.

**Sources**: [install_as_skill.sh:155-191](), [README.md:58]()

---

## Platform-Specific Installation Differences

```mermaid
graph TB
    subgraph macOS_Installation["macOS Installation"]
        MacBrew["Homebrew Package Manager"]
        MacPython["brew install python3"]
        MacYtdlp["brew install yt-dlp"]
        MacFFmpeg["brew install ffmpeg-full"]
        MacNote["NOTE: Use ffmpeg-full for libass"]
        
        MacBrew --> MacPython
        MacBrew --> MacYtdlp
        MacBrew --> MacFFmpeg
        MacFFmpeg -.-> MacNote
    end
    
    subgraph Ubuntu_Installation["Ubuntu Installation"]
        UbuntuAPT["APT Package Manager"]
        UbuntuPython["apt-get install python3 python3-pip"]
        UbuntuYtdlp["apt-get install yt-dlp"]
        UbuntuFFmpeg["apt-get install ffmpeg libass-dev"]
        UbuntuNote["NOTE: Install libass-dev separately"]
        
        UbuntuAPT --> UbuntuPython
        UbuntuAPT --> UbuntuYtdlp
        UbuntuAPT --> UbuntuFFmpeg
        UbuntuFFmpeg -.-> UbuntuNote
    end
    
    subgraph Pip_Installation["pip-only Installation"]
        PipOnly["pip Package Manager"]
        PipPython["Python already installed"]
        PipYtdlp["pip3 install yt-dlp"]
        PipFFmpegWarn["WARNING: Cannot install FFmpeg"]
        PipNote["NOTE: FFmpeg requires separate installation"]
        
        PipOnly --> PipPython
        PipOnly --> PipYtdlp
        PipOnly -.-> PipFFmpegWarn
        PipFFmpegWarn -.-> PipNote
    end
    
    subgraph Verification["Common Verification Steps"]
        CheckPython["python3 --version"]
        CheckYtdlp["yt-dlp --version"]
        CheckFFmpeg["ffmpeg -version"]
        CheckLibass["ffmpeg -filters 2>&1 | grep subtitles"]
    end
    
    MacFFmpeg --> Verification
    UbuntuFFmpeg --> Verification
    PipYtdlp --> Verification
```

**Platform Installation Comparison**: Different platforms require different installation approaches, particularly for FFmpeg.

**Sources**: [README.md:54-84](), [install_as_skill.sh:140-191]()

---

## Dependency Verification Code Mapping

Understanding how the installation script verifies dependencies helps diagnose failures.

```mermaid
flowchart LR
    subgraph InstallScript["install_as_skill.sh Functions"]
        command_exists["command_exists()<br/>line 51-53"]
        check_python["Python check<br/>line 110-117"]
        check_pip["pip check<br/>line 120-124"]
        install_deps["Install deps<br/>line 127-137"]
        check_ytdlp["yt-dlp check<br/>line 140-150"]
        check_ffmpeg["FFmpeg check<br/>line 155-179"]
        check_libass["libass check<br/>line 173-178"]
    end
    
    subgraph SystemCommands["System Commands"]
        python3_cmd["python3 --version"]
        pip3_cmd["pip3 install"]
        ytdlp_cmd["yt-dlp --version"]
        ffmpeg_cmd["ffmpeg -version"]
        ffmpeg_filters["ffmpeg -filters"]
    end
    
    subgraph FileSystem["File System Checks"]
        homebrew_apple["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
        homebrew_intel["/usr/local/opt/ffmpeg-full/bin/ffmpeg"]
    end
    
    command_exists --> |"python3"| python3_cmd
    command_exists --> |"pip3"| pip3_cmd
    command_exists --> |"yt-dlp"| ytdlp_cmd
    command_exists --> |"ffmpeg"| ffmpeg_cmd
    
    check_python --> command_exists
    check_pip --> command_exists
    check_ytdlp --> command_exists
    check_ffmpeg --> homebrew_apple
    check_ffmpeg --> homebrew_intel
    check_ffmpeg --> command_exists
    check_libass --> ffmpeg_filters
    
    install_deps --> pip3_cmd
```

**Dependency Verification Mapping**: Shows how install_as_skill.sh functions map to system commands and file checks.

**Key Functions**:

| Function | Purpose | Lines |
|----------|---------|-------|
| `command_exists()` | Check if command is available in PATH | [install_as_skill.sh:51-53]() |
| `print_info()` | Display informational messages | [install_as_skill.sh:26-28]() |
| `print_success()` | Display success messages | [install_as_skill.sh:30-32]() |
| `print_warning()` | Display warning messages | [install_as_skill.sh:34-36]() |
| `print_error()` | Display error messages | [install_as_skill.sh:38-40]() |

**Sources**: [install_as_skill.sh:51-191]()

---

## Manual Installation Verification

If automatic installation fails, verify each component manually:

### Step 1: Verify Python Installation

```bash
# Check Python version
python3 --version
# Expected: Python 3.8.0 or higher

# Check Python import paths
python3 -c "import sys; print('\n'.join(sys.path))"
```

### Step 2: Verify pip Installation

```bash
# Check pip version
pip3 --version
# Expected: pip 20.0 or higher

# Check pip installation location
which pip3
```

### Step 3: Verify Python Packages

```bash
# Check yt_dlp
python3 -c "import yt_dlp; print(f'yt_dlp: {yt_dlp.version.__version__}')"

# Check pysrt
python3 -c "import pysrt; print('pysrt: OK')"

# Check dotenv
python3 -c "import dotenv; print('dotenv: OK')"
```

### Step 4: Verify System Tools

```bash
# Check yt-dlp CLI
yt-dlp --version

# Check FFmpeg
ffmpeg -version

# Check FFmpeg libass support
ffmpeg -filters 2>&1 | grep subtitles
# Expected output: subtitles    V->V  (...)
```

### Step 5: Verify Skill Directory

```bash
# Check directory exists
ls -la ~/.claude/skills/youtube-clipper/

# Check required files
ls ~/.claude/skills/youtube-clipper/scripts/
# Expected: download_video.py, analyze_subtitles.py, clip_video.py, etc.

# Check .env file
cat ~/.claude/skills/youtube-clipper/.env
```

**Sources**: [install_as_skill.sh:110-191]()

---

## Common Installation Failures Table

| Symptom | Probable Cause | Solution | Reference |
|---------|---------------|----------|-----------|
| `externally-managed-environment` error | macOS PEP 668 protection | Use `--break-system-packages` flag | [FIXES_AND_IMPROVEMENTS.md:9-25]() |
| `ModuleNotFoundError: yt_dlp` | Package not installed | Run `pip3 install yt-dlp` | [install_as_skill.sh:132]() |
| `ModuleNotFoundError: pysrt` | Package not installed | Run `pip3 install pysrt` | [install_as_skill.sh:132]() |
| `command not found: python3` | Python not installed | Install Python 3.8+ | [README.md:56]() |
| `command not found: pip3` | pip not installed | Install pip via ensurepip or get-pip.py | [install_as_skill.sh:120-124]() |
| `command not found: yt-dlp` | CLI tool not installed | Use brew/apt to install | [install_as_skill.sh:140-150]() |
| `command not found: ffmpeg` | FFmpeg not installed | Install FFmpeg | [install_as_skill.sh:155-179]() |
| Skill directory already exists | Previous installation | Confirm overwrite or cancel | [install_as_skill.sh:64-74]() |

**Sources**: [install_as_skill.sh:56-241](), [FIXES_AND_IMPROVEMENTS.md:9-25](), [README.md:50-84]()

---

## Installation Script Error Handling

The installation script uses Bash error handling to ensure clean failures:

**Error Trap**: [install_as_skill.sh:16]()
```bash
set -e  # Exit immediately on error
```

**Custom Error Handler**: [install_as_skill.sh:238]()
```bash
trap 'print_error "安装过程中发生错误"; exit 1' ERR
```

This means:
- Any command failure causes immediate exit
- Error message is printed before exit
- Exit code 1 indicates installation failure

**Consequences**:
- Partial installations are prevented
- User knows exactly where failure occurred
- Re-running script is safe (overwrites incomplete installation)

**Sources**: [install_as_skill.sh:16](), [install_as_skill.sh:238]()

---

## Post-Installation Verification

After successful installation, verify the complete setup:

```bash
# Run from any directory
cd /tmp

# Test Python imports
python3 -c "
import sys
sys.path.insert(0, '$HOME/.claude/skills/youtube-clipper')
from scripts.utils import ensure_dir_exists
print('Utils import: OK')
"

# Check .env file created
test -f ~/.claude/skills/youtube-clipper/.env && echo ".env exists: OK"

# Check all scripts present
for script in download_video.py analyze_subtitles.py clip_video.py burn_subtitles.py extract_subtitle_clip.py utils.py; do
    test -f ~/.claude/skills/youtube-clipper/scripts/$script && echo "$script: OK"
done
```

**Expected Output**:
```
Utils import: OK
.env exists: OK
download_video.py: OK
analyze_subtitles.py: OK
clip_video.py: OK
burn_subtitles.py: OK
extract_subtitle_clip.py: OK
utils.py: OK
```

**Sources**: [install_as_skill.sh:194-209]()

---

# Page: FFmpeg and libass Problems

# FFmpeg and libass Problems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/ffmpeg-guide.md](references/ffmpeg-guide.md)
- [scripts/burn_subtitles.py](scripts/burn_subtitles.py)

</details>



This page documents FFmpeg-related issues encountered during subtitle burning operations, specifically the missing libass support problem and the file path space problem. It covers detection logic, root causes, and implemented solutions.

For general FFmpeg integration patterns, see [FFmpeg Integration](#5.2). For libass installation requirements, see [libass Requirement](#5.3). For broader troubleshooting topics, see [Troubleshooting](#8).

## Missing libass Support

### Problem Description

Standard FFmpeg installations, particularly through Homebrew on macOS, do not include the libass library required for the `subtitles` filter. This prevents subtitle burning operations from functioning.

**Error Manifestation:**
```
No such filter: 'subtitles'
```

The error occurs when [scripts/burn_subtitles.py:195]() attempts to execute the FFmpeg command with the subtitles filter.

**Detection Command:**
```bash
ffmpeg -filters 2>&1 | grep subtitles
# Returns empty if libass is not supported
```

### Root Cause

| Component | Issue | Impact |
|-----------|-------|--------|
| Homebrew `ffmpeg` formula | Excludes non-core libraries to reduce package size | No `subtitles` filter available |
| libass library | Not compiled into standard builds | Cannot render subtitles to video frames |
| `subtitles` filter | Requires libass at compile time | Filter registration fails without libass |

Sources: [TECHNICAL_NOTES.md:5-24]()

### FFmpeg Variant Detection Flow

The system implements a multi-stage detection process in [scripts/burn_subtitles.py:19-70]() to locate a compatible FFmpeg installation:

```mermaid
flowchart TD
    Start["detect_ffmpeg_variant()"]
    
    CheckOS{"platform.system()<br/>== 'Darwin'?"}
    
    CheckARM["Check Apple Silicon path:<br/>/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
    CheckIntel["Check Intel path:<br>/usr/local/opt/ffmpeg-full/bin/ffmpeg"]
    
    TestLibassARM["check_libass_support(full_path)"]
    TestLibassIntel["check_libass_support(full_path)"]
    
    ReturnFull["Return:<br/>type='full'<br/>path=full_path<br/>has_libass=True"]
    
    CheckStandard["shutil.which('ffmpeg')"]
    
    TestLibassStd["check_libass_support(standard_path)"]
    
    ReturnStandard["Return:<br/>type='standard'/'full'<br/>path=standard_path<br/>has_libass=result"]
    
    ReturnNone["Return:<br/>type='none'<br/>path=None<br/>has_libass=False"]
    
    Start --> CheckOS
    
    CheckOS -->|Yes| CheckARM
    CheckARM -->|exists| TestLibassARM
    TestLibassARM --> ReturnFull
    
    CheckARM -->|not exists| CheckIntel
    CheckIntel -->|exists| TestLibassIntel
    TestLibassIntel --> ReturnFull
    
    CheckOS -->|No| CheckStandard
    CheckIntel -->|not exists| CheckStandard
    
    CheckStandard -->|found| TestLibassStd
    TestLibassStd --> ReturnStandard
    
    CheckStandard -->|not found| ReturnNone
```

Sources: [scripts/burn_subtitles.py:19-70]()

### libass Support Verification

The `check_libass_support()` function at [scripts/burn_subtitles.py:73-96]() verifies libass availability:

```python
# Executes: ffmpeg -filters
# Searches stdout for 'subtitles' string
# Returns: bool indicating libass support
```

| Verification Step | Implementation | Purpose |
|-------------------|----------------|---------|
| Execute `-filters` | `subprocess.run([ffmpeg_path, '-filters'])` | List all available filters |
| Search output | `'subtitles' in result.stdout.lower()` | Check for subtitles filter |
| Timeout protection | `timeout=5` | Prevent hanging |
| Exception handling | `return False` on exception | Graceful degradation |

Sources: [scripts/burn_subtitles.py:73-96]()

### Platform-Specific Installation Solutions

#### macOS

The system recommends `ffmpeg-full` which includes libass by default:

```bash
brew install ffmpeg-full
```

**Installation Paths:**
- Apple Silicon: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
- Intel: `/usr/local/opt/ffmpeg-full/bin/ffmpeg`

The `install_ffmpeg_full_guide()` function at [scripts/burn_subtitles.py:99-120]() provides platform-specific installation instructions when libass is missing.

Sources: [TECHNICAL_NOTES.md:26-43](), [references/ffmpeg-guide.md:7-13]()

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get install libass-dev
# Then compile FFmpeg from source with --enable-libass
./configure --enable-libass
make
sudo make install
```

Sources: [TECHNICAL_NOTES.md:45-56]()

#### Verification After Installation

```bash
ffmpeg -filters 2>&1 | grep subtitles
# Expected output: subtitles V->V (Render text subtitles onto input video.)
```

Sources: [references/ffmpeg-guide.md:28-29]()

## File Path Space Problem

### Problem Description

The FFmpeg `subtitles` filter fails to parse file paths containing spaces, even when properly quoted or escaped. This is a known FFmpeg limitation in the filter path parser.

**Error Manifestation:**
```
[Parsed_subtitles_0 @ 0x...] Unable to find '/path/with'
```

The path is truncated at the first space character (`/path/with spaces` becomes `/path/with`).

### Failed Escaping Attempts

| Method | Example | Result |
|--------|---------|--------|
| Double quotes | `subtitles="/path/with spaces/sub.srt"` | ❌ Fails |
| Single quotes | `subtitles='/path/with spaces/sub.srt'` | ❌ Fails |
| Backslash escape | `subtitles=/path/with\ spaces/sub.srt` | ❌ Fails |
| Mixed quotes | `subtitles="'/path/with spaces/sub.srt'"` | ❌ Fails |
| `-filter_complex` | Same issue across all filter options | ❌ Fails |

Sources: [TECHNICAL_NOTES.md:83-112](), [TECHNICAL_NOTES.md:155-162]()

### Temporary Directory Workaround

The system implements a temporary directory strategy in [scripts/burn_subtitles.py:123-244]() to eliminate spaces from all file paths during processing:

```mermaid
flowchart TB
    Input["Input:<br/>video_path (may have spaces)<br/>subtitle_path (may have spaces)<br/>output_path (may have spaces)"]
    
    CreateTemp["tempfile.mkdtemp(prefix='youtube_clipper_')<br/>Creates: /tmp/youtube_clipper_XXXXX"]
    
    CopyFiles["shutil.copy() operations:<br/>video → temp_dir/video.mp4<br/>subtitle → temp_dir/subtitle.srt"]
    
    BuildCmd["FFmpeg command with space-free paths:<br/>subtitles=temp_dir/subtitle.srt"]
    
    Execute["subprocess.run(cmd)<br/>Output: temp_dir/output.mp4"]
    
    MoveOutput["shutil.move(temp_output, output_path)<br/>Restore original destination"]
    
    Cleanup["shutil.rmtree(temp_dir)<br/>Remove temporary files"]
    
    Success["Return: output_path<br/>(may have spaces)"]
    
    Input --> CreateTemp
    CreateTemp --> CopyFiles
    CopyFiles --> BuildCmd
    BuildCmd --> Execute
    Execute --> MoveOutput
    MoveOutput --> Cleanup
    Cleanup --> Success
    
    Exception["Exception during processing"]
    Execute -.->|Error| Exception
    Exception --> Cleanup
    Cleanup -.->|Always executed| FinallyBlock["finally block ensures cleanup"]
```

Sources: [scripts/burn_subtitles.py:179-244](), [TECHNICAL_NOTES.md:113-148]()

### Implementation Details

The `burn_subtitles()` function implements the workaround:

**Temporary Directory Creation:**
```python
# Line 180: Creates directory with guaranteed space-free path
temp_dir = tempfile.mkdtemp(prefix='youtube_clipper_')
# Example result: /tmp/youtube_clipper_a1b2c3d4
```

**File Path Mapping:**

| Original Path | Temporary Path | Rationale |
|---------------|----------------|-----------|
| `video_path` (any) | `temp_dir/video.mp4` | Fixed filename, no spaces |
| `subtitle_path` (any) | `temp_dir/subtitle.srt` | Fixed filename, no spaces |
| `output_path` (any) | `temp_dir/output.mp4` | Fixed filename, no spaces |

**FFmpeg Command Construction:**
```python
# Lines 195-204: All paths are space-free
subtitle_filter = f"subtitles={temp_subtitle}:force_style='FontSize={font_size},MarginV={margin_v}'"

cmd = [
    ffmpeg_path,
    '-i', temp_video,
    '-vf', subtitle_filter,
    '-c:a', 'copy',
    '-y',
    temp_output
]
```

**Cleanup Guarantee:**
```python
# Lines 239-244: finally block ensures cleanup even on failure
finally:
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass
```

Sources: [scripts/burn_subtitles.py:179-244]()

### Why This Approach Works

| Aspect | Explanation |
|--------|-------------|
| `tempfile.mkdtemp()` | Generates paths in `/tmp/` directory without spaces |
| Platform independence | Works on macOS, Linux, Windows (`tempfile` is cross-platform) |
| User transparency | Input/output paths can contain any characters |
| No FFmpeg patches | Avoids need to modify or wait for FFmpeg fixes |
| Atomic operations | File copies and moves are atomic on most filesystems |

Sources: [TECHNICAL_NOTES.md:150-154]()

## Detection and Error Handling

### Error Flow in burn_subtitles()

```mermaid
flowchart TD
    Start["burn_subtitles() invoked"]
    
    ValidateInputs{"video_path.exists()?<br/>subtitle_path.exists()?"}
    
    RaiseNotFound["raise FileNotFoundError"]
    
    CheckFFmpeg{"ffmpeg_path provided?"}
    
    CallDetect["ffmpeg_info = detect_ffmpeg_variant()"]
    
    CheckType{"ffmpeg_info['type']<br/>== 'none'?"}
    
    CheckLibass{"ffmpeg_info['has_libass']<br/>== False?"}
    
    ShowGuide["install_ffmpeg_full_guide()<br/>Display installation instructions"]
    
    RaiseNoFFmpeg["raise RuntimeError:<br/>'FFmpeg not found'"]
    
    RaiseNoLibass["raise RuntimeError:<br/>'FFmpeg does not support libass'"]
    
    UseProvided["Use provided ffmpeg_path"]
    
    SetPath["ffmpeg_path = ffmpeg_info['path']"]
    
    ProceedBurn["Proceed with subtitle burning"]
    
    Start --> ValidateInputs
    ValidateInputs -->|No| RaiseNotFound
    ValidateInputs -->|Yes| CheckFFmpeg
    
    CheckFFmpeg -->|No| CallDetect
    CheckFFmpeg -->|Yes| UseProvided
    
    CallDetect --> CheckType
    CheckType -->|Yes| ShowGuide
    ShowGuide --> RaiseNoFFmpeg
    
    CheckType -->|No| CheckLibass
    CheckLibass -->|Yes| ShowGuide
    ShowGuide --> RaiseNoLibass
    
    CheckLibass -->|No| SetPath
    SetPath --> ProceedBurn
    UseProvided --> ProceedBurn
```

Sources: [scripts/burn_subtitles.py:148-171]()

### Installation Guide Output

When libass support is missing, the system provides platform-specific guidance via [scripts/burn_subtitles.py:99-120]():

**macOS:**
```
⚠️  需要安装 ffmpeg-full 才能烧录字幕

macOS 安装方法:
  brew install ffmpeg-full

安装后，FFmpeg 路径:
  /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg  (Apple Silicon)
  /usr/local/opt/ffmpeg-full/bin/ffmpeg     (Intel)

验证安装:
  ffmpeg -filters 2>&1 | grep subtitles
```

**Other Platforms:**
```
其他系统:
  请从源码编译 FFmpeg，确保包含 libass 支持
  参考: https://trac.ffmpeg.org/wiki/CompilationGuide
```

Sources: [scripts/burn_subtitles.py:99-120]()

## Subtitle Style Application

When libass is available, the system applies custom styles through the `force_style` parameter:

**Style Configuration:**

| Parameter | Default | Purpose | Range |
|-----------|---------|---------|-------|
| `FontSize` | 24 | Text size in points | 16-48 (depends on resolution) |
| `MarginV` | 30 | Vertical margin from bottom (pixels) | 20-60 |

**Command Construction:**
```python
# Line 195
subtitle_filter = f"subtitles={temp_subtitle}:force_style='FontSize={font_size},MarginV={margin_v}'"
```

**Example FFmpeg Command:**
```bash
ffmpeg -i video.mp4 \
  -vf "subtitles=/tmp/youtube_clipper_xyz/subtitle.srt:force_style='FontSize=24,MarginV=30'" \
  -c:a copy \
  output.mp4
```

Sources: [scripts/burn_subtitles.py:195](), [TECHNICAL_NOTES.md:356-388]()

## Summary of Solutions

| Problem | Detection Method | Solution | Implementation |
|---------|------------------|----------|----------------|
| Missing libass | `check_libass_support()` checks filter list | Install `ffmpeg-full` (macOS) or compile with `--enable-libass` | `detect_ffmpeg_variant()` |
| Path contains spaces | N/A (FFmpeg limitation) | Copy files to temp directory without spaces | `tempfile.mkdtemp()` workaround |
| Wrong FFmpeg variant | Platform-specific path detection | Auto-detect `ffmpeg-full` paths on macOS | Priority check in `detect_ffmpeg_variant()` |
| Installation verification | Run `ffmpeg -filters` and search output | Provide verification command in error message | `install_ffmpeg_full_guide()` |

Sources: [TECHNICAL_NOTES.md:478-489](), [scripts/burn_subtitles.py:19-244]()

---

# Page: Download and Network Issues

# Download and Network Issues

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FIXES_AND_IMPROVEMENTS.md](FIXES_AND_IMPROVEMENTS.md)
- [references/yt-dlp-guide.md](references/yt-dlp-guide.md)
- [scripts/download_video.py](scripts/download_video.py)

</details>



## Purpose and Scope

This document addresses issues related to downloading videos from YouTube, including network connectivity problems, proxy configuration, rate limiting, progress reporting failures, and subtitle download issues. These problems occur during the video acquisition phase handled by [scripts/download_video.py]().

For issues with FFmpeg or video processing, see [FFmpeg and libass Problems](#8.2). For problems with file paths or special characters in filenames, see [File Path and Encoding Issues](#8.4).

---

## Download Workflow and Failure Points

The following diagram shows the download process and where failures typically occur:

**Diagram: Download Process with Failure Points**

```mermaid
flowchart TD
    Start["download_video(url, output_dir)"]
    ValidateURL["validate_url(url)"]
    ExtractInfo["ydl.extract_info(url, download=False)"]
    DisplayInfo["Display video metadata"]
    Download["ydl.extract_info(url, download=True)"]
    LocateFiles["Locate video and subtitle files"]
    Verify["Verify file existence"]
    Return["Return file paths and metadata"]
    
    Start --> ValidateURL
    ValidateURL -->|Invalid URL| ErrorInvalidURL["ValueError: Invalid YouTube URL"]
    ValidateURL -->|Valid| ExtractInfo
    
    ExtractInfo -->|Network Error| ErrorNetwork["Network timeout or connection failure"]
    ExtractInfo -->|Video Unavailable| ErrorUnavailable["Video deleted, private, or restricted"]
    ExtractInfo -->|Success| DisplayInfo
    
    DisplayInfo --> Download
    
    Download -->|Network Error| ErrorDownload["Download interrupted"]
    Download -->|Disk Space| ErrorDisk["Insufficient disk space"]
    Download -->|Success| LocateFiles
    
    LocateFiles --> Verify
    Verify -->|Missing Video| ErrorMissingVideo["Video file not found after download"]
    Verify -->|Missing Subtitle| WarnSubtitle["Warning: Subtitle not available"]
    Verify -->|Success| Return
    
    style ErrorInvalidURL fill:#f9f9f9
    style ErrorNetwork fill:#f9f9f9
    style ErrorUnavailable fill:#f9f9f9
    style ErrorDownload fill:#f9f9f9
    style ErrorDisk fill:#f9f9f9
    style ErrorMissingVideo fill:#f9f9f9
    style WarnSubtitle fill:#f9f9f9
```

Sources: [scripts/download_video.py:27-153]()

---

## Common Download Failures

### Video Unavailable

**Symptoms:**
- Error message: `Video unavailable`
- Error message: `This video is private`
- Error message: `This video has been removed`

**Causes:**
1. Video has been deleted by the uploader
2. Video is set to private or unlisted
3. Video requires authentication (membership/subscription)
4. Video is region-restricted

**Solutions:**

| Cause | Solution |
|-------|----------|
| Deleted video | Cannot be recovered; obtain alternate URL |
| Private/unlisted video | Use `--cookies-from-browser` option with yt-dlp |
| Membership required | Export browser cookies and configure yt-dlp |
| Region restriction | Configure proxy using `YT_DLP_PROXY` environment variable |

**Manual Testing:**
```bash
# Test if video is accessible
yt-dlp --print-json https://youtube.com/watch?v=VIDEO_ID

# Test with browser cookies
yt-dlp --cookies-from-browser chrome https://youtube.com/watch?v=VIDEO_ID
```

Sources: [references/yt-dlp-guide.md:243-283]()

### Network Connection Failures

**Symptoms:**
- Error message: `HTTP Error 403: Forbidden`
- Error message: `Unable to download webpage`
- Error message: `Connection timeout`
- Download hangs indefinitely

**Diagnostic Steps:**

1. **Test basic connectivity:**
```bash
# Test if yt-dlp can reach YouTube
yt-dlp --simulate https://youtube.com/watch?v=Ckt1cj0xjRM
```

2. **Check for rate limiting:**
- YouTube may throttle requests from certain IPs
- Symptoms: Very slow download speeds or intermittent failures

3. **Verify DNS resolution:**
```bash
# Test if YouTube domain resolves
ping youtube.com
```

Sources: [references/yt-dlp-guide.md:243-265](), [scripts/download_video.py:89-153]()

---

## Network Configuration

### Proxy Configuration

The system supports proxy configuration through the `YT_DLP_PROXY` environment variable. This is essential for users behind corporate firewalls or in regions with YouTube access restrictions.

**Diagram: Proxy Configuration Flow**

```mermaid
flowchart LR
    EnvFile[".env file"]
    EnvVar["YT_DLP_PROXY"]
    DownloadScript["download_video.py"]
    YdlOpts["ydl_opts dictionary"]
    YtDlp["yt_dlp.YoutubeDL"]
    Network["Network Request"]
    Proxy["Proxy Server"]
    YouTube["YouTube Server"]
    
    EnvFile -->|"Loads"| EnvVar
    EnvVar -->|"Read by"| DownloadScript
    DownloadScript -->|"Configures"| YdlOpts
    YdlOpts -->|"Passed to"| YtDlp
    YtDlp -->|"Routes through"| Proxy
    Proxy -->|"Forwards to"| YouTube
    
    EnvVar -.->|"If not set"| Network
    Network -.->|"Direct connection"| YouTube
```

**Configuration Example:**

Create or edit `.env` file in the skill directory:
```bash
# HTTP proxy
YT_DLP_PROXY=http://proxy.example.com:8080

# HTTPS proxy
YT_DLP_PROXY=https://proxy.example.com:8080

# SOCKS5 proxy
YT_DLP_PROXY=socks5://proxy.example.com:1080

# Proxy with authentication
YT_DLP_PROXY=http://username:password@proxy.example.com:8080
```

**Manual Testing:**
```bash
# Test with HTTP proxy
yt-dlp --proxy http://proxy:port https://youtube.com/watch?v=VIDEO_ID

# Test with SOCKS5 proxy
yt-dlp --proxy socks5://proxy:port https://youtube.com/watch?v=VIDEO_ID
```

Sources: [references/yt-dlp-guide.md:130-148](), Configuration documentation in [6.2](#6.2)

### Rate Limiting

The `YT_DLP_RATE_LIMIT` environment variable controls download speed. This is useful to avoid network congestion or comply with institutional bandwidth policies.

**Configuration:**
```bash
# Limit to 50 KB/s
YT_DLP_RATE_LIMIT=50K

# Limit to 4.2 MB/s
YT_DLP_RATE_LIMIT=4.2M

# No limit (default)
YT_DLP_RATE_LIMIT=
```

**Effect on Download:**

| Rate Limit | 100 MB Video | 500 MB Video |
|------------|--------------|--------------|
| 50K/s | ~34 minutes | ~2.8 hours |
| 500K/s | ~3.4 minutes | ~17 minutes |
| 4.2M/s | ~24 seconds | ~2 minutes |
| Unlimited | Depends on network speed | Depends on network speed |

**Manual Testing:**
```bash
# Test with rate limit
yt-dlp --rate-limit 50K https://youtube.com/watch?v=VIDEO_ID
```

Sources: [references/yt-dlp-guide.md:140-148]()

---

## Progress Reporting Issues

### Division by Zero Error (Fixed)

**Historical Issue:**

Prior to the fix documented in [FIXES_AND_IMPROVEMENTS.md:28-54](), the download progress hook in [scripts/download_video.py:156-182]() would crash when `total_bytes` was `None`:

```python
# Problematic code (before fix)
if 'downloaded_bytes' in d and 'total_bytes' in d:
    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
    # If d['total_bytes'] is None, this raises TypeError
```

**Root Cause:**
Some videos do not provide `total_bytes` information during download. This occurs with:
- Live streams or premieres
- Videos being processed by YouTube
- Certain adaptive formats

**Fix Applied:**

The `_progress_hook` function in [scripts/download_video.py:156-182]() now validates that `total_bytes` is not `None` before performing division:

```python
# Fixed code (current)
if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes']:
    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
    # Safe: d['total_bytes'] is guaranteed to be a non-None, non-zero value
```

**Fallback Behavior:**

When `total_bytes` is unavailable, the progress hook displays downloaded bytes and speed without percentage:

```python
elif 'downloaded_bytes' in d:
    downloaded = format_file_size(d['downloaded_bytes'])
    speed = d.get('speed', 0)
    speed_str = format_file_size(speed) + '/s' if speed else 'N/A'
    print(f"\r   下载中... {downloaded} - {speed_str}", end='', flush=True)
```

**Diagram: Progress Hook Error Handling**

```mermaid
flowchart TD
    Hook["_progress_hook(d)"]
    CheckStatus{"d['status'] == 'downloading'?"}
    CheckBytes{"'downloaded_bytes' in d AND<br/>'total_bytes' in d AND<br/>d['total_bytes'] is not None?"}
    CalcPercent["percent = downloaded / total * 100<br/>Display progress bar with percentage"]
    CheckDownloaded{"'downloaded_bytes' in d?"}
    DisplaySimple["Display downloaded size and speed only"]
    Finished{"d['status'] == 'finished'?"}
    Newline["Print newline"]
    Return["Return"]
    
    Hook --> CheckStatus
    CheckStatus -->|Yes| CheckBytes
    CheckStatus -->|No| Finished
    
    CheckBytes -->|Yes| CalcPercent
    CheckBytes -->|No| CheckDownloaded
    
    CheckDownloaded -->|Yes| DisplaySimple
    CheckDownloaded -->|No| Return
    
    CalcPercent --> Return
    DisplaySimple --> Return
    
    Finished -->|Yes| Newline
    Finished -->|No| Return
    Newline --> Return
```

Sources: [scripts/download_video.py:156-182](), [FIXES_AND_IMPROVEMENTS.md:28-54]()

### Missing Progress Information

**Symptoms:**
- Progress bar shows only `下载中... X MB - Y MB/s` without percentage
- No total size displayed
- Progress appears stuck but download is actually proceeding

**Explanation:**
This is normal behavior when YouTube does not provide total file size in advance. The download is still functioning correctly.

**Verification:**
Check that the downloaded bytes are increasing over time. If bytes increase consistently, the download is working.

Sources: [scripts/download_video.py:173-178]()

---

## Subtitle Download Failures

### No Subtitles Available

**Symptoms:**
- Warning: `⚠️  未找到英文字幕`
- `subtitle_path` is `None` in return value

**Common Causes:**

| Scenario | Explanation | Solution |
|----------|-------------|----------|
| No human subtitles | Video has no manually created subtitles | Auto-generated subtitles are automatically attempted |
| No English subtitles | Video has subtitles but not in English | Modify `subtitleslangs` in ydl_opts or use different language |
| Live stream | Live streams don't have pre-generated subtitles | Wait for video to finish processing after stream ends |
| Recent upload | YouTube hasn't generated auto-captions yet | Wait 10-30 minutes and retry |

**Current Configuration:**

The download script in [scripts/download_video.py:72-76]() uses the following subtitle settings:

```python
ydl_opts = {
    'writesubtitles': True,          # Download manual subtitles
    'writeautomaticsub': True,       # Fallback to auto-generated
    'subtitleslangs': ['en'],        # English only
    'subtitlesformat': 'vtt',        # VTT format
}
```

**Manual Testing:**

```bash
# List available subtitles
yt-dlp --list-subs https://youtube.com/watch?v=VIDEO_ID

# Download with auto-generated subtitles
yt-dlp --write-auto-sub --sub-lang en https://youtube.com/watch?v=VIDEO_ID

# Try different subtitle format
yt-dlp --write-sub --sub-format srt https://youtube.com/watch?v=VIDEO_ID
```

Sources: [scripts/download_video.py:72-76](), [scripts/download_video.py:111-141](), [references/yt-dlp-guide.md:163-195]()

### Subtitle File Location Issues

The script searches for subtitle files with multiple naming patterns:

**Search Pattern:**

```python
subtitle_exts = ['.en.vtt', '.vtt']
for ext in subtitle_exts:
    potential_sub = video_path.with_suffix(ext)
    if not potential_sub.exists():
        # Try <filename>.en.vtt format
        stem = video_path.stem
        potential_sub = video_path.parent / f"{stem}.en.vtt"
    
    if potential_sub.exists():
        subtitle_path = potential_sub
        break
```

**Common Naming Patterns:**
- `VIDEO_ID.en.vtt` (with language code)
- `VIDEO_ID.vtt` (without language code)
- `VIDEO_ID.en-US.vtt` (with locale)

If subtitles are not found, check the output directory for files matching these patterns manually.

Sources: [scripts/download_video.py:111-124]()

---

## Timeout and Hanging Downloads

### Symptoms
- Download appears to freeze
- No progress updates for extended period
- No error message displayed

### Diagnostic Approach

**Step 1: Verify Network Activity**
```bash
# On macOS/Linux, monitor network connections
netstat -an | grep ESTABLISHED | grep youtube

# Monitor disk I/O
iostat -w 5
```

**Step 2: Enable Verbose Logging**

Modify [scripts/download_video.py:82-83]() temporarily:

```python
# Change from:
'quiet': False,
'no_warnings': False,

# To:
'quiet': False,
'no_warnings': False,
'verbose': True,  # Add this line
```

This will display detailed yt-dlp debugging output.

**Step 3: Test with Simplified Options**

Run manual test with minimal options:
```bash
yt-dlp --format best https://youtube.com/watch?v=VIDEO_ID
```

If this succeeds, the issue is likely with specific format selection or post-processing.

### Common Solutions

| Issue | Solution |
|-------|----------|
| Network congestion | Configure `YT_DLP_RATE_LIMIT` to reduce bandwidth usage |
| Firewall blocking | Configure `YT_DLP_PROXY` to route through allowed proxy |
| YouTube throttling | Wait 15-30 minutes and retry; consider using different IP |
| Disk I/O slow | Ensure sufficient disk space; check disk health |
| Format unavailable | Modify format selection in ydl_opts to use broader format string |

Sources: [scripts/download_video.py:64-87](), [references/yt-dlp-guide.md:259-265]()

---

## Error Messages and Solutions

### Error Code Reference

**Diagram: Error Message to Code Location Mapping**

```mermaid
flowchart TD
    subgraph "Error Messages"
        E1["'Invalid YouTube URL'"]
        E2["'yt-dlp not installed'"]
        E3["'Video file not found after download'"]
        E4["'下载失败' + exception message"]
    end
    
    subgraph "Code Locations"
        V1["validate_url() returns False<br/>Line 49-50"]
        I1["ImportError: yt_dlp<br/>Line 11-16"]
        V2["video_path.exists() is False<br/>Line 130-131"]
        E5["Exception in ydl.extract_info()<br/>Line 151-153"]
    end
    
    E1 --> V1
    E2 --> I1
    E3 --> V2
    E4 --> E5
    
    V1 -.->|Fix| F1["Verify URL format<br/>Must match youtube.com/watch?v= pattern"]
    I1 -.->|Fix| F2["pip install yt-dlp"]
    V2 -.->|Fix| F3["Check disk space<br/>Verify download completed<br/>Check file permissions"]
    E5 -.->|Fix| F4["Check network connectivity<br/>Verify video exists<br/>Check proxy settings"]
```

Sources: [scripts/download_video.py:11-16](), [scripts/download_video.py:49-50](), [scripts/download_video.py:130-131](), [scripts/download_video.py:151-153]()

### Detailed Error Solutions

#### `ModuleNotFoundError: No module named 'yt_dlp'`

**Cause:** yt-dlp Python package is not installed

**Solution:**
```bash
# Standard installation
pip install yt-dlp

# macOS with externally-managed Python
pip3 install --break-system-packages yt-dlp

# Or use system package manager
brew install yt-dlp  # macOS
```

Sources: [FIXES_AND_IMPROVEMENTS.md:9-24](), [scripts/download_video.py:11-16]()

#### `TypeError: unsupported operand type(s) for /: 'int' and 'NoneType'`

**Status:** Fixed in current version

**Historical Cause:** Division by `None` in progress hook when `total_bytes` unavailable

**Verification:** Ensure using current version of [scripts/download_video.py:160-178]() with the fix applied

Sources: [FIXES_AND_IMPROVEMENTS.md:28-54]()

#### `HTTP Error 403: Forbidden`

**Possible Causes:**
1. IP address blocked by YouTube
2. Too many requests from same IP
3. Region restriction
4. Missing user agent

**Solutions:**
```bash
# Try with proxy
yt-dlp --proxy http://proxy:port URL

# Wait and retry (if rate limited)
# Wait 15-30 minutes before next attempt

# Use different format selection
yt-dlp --format worst URL  # Test with lowest quality first
```

#### `Unable to extract video data`

**Possible Causes:**
1. Video ID invalid or malformed
2. YouTube changed their API
3. yt-dlp version outdated

**Solutions:**
```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Or with homebrew
brew upgrade yt-dlp

# Verify video ID manually
yt-dlp --print-json https://youtube.com/watch?v=VIDEO_ID
```

Sources: [references/yt-dlp-guide.md:20-28]()

---

## Debugging Workflow

Follow this systematic approach to diagnose download issues:

**Diagram: Download Issue Debugging Workflow**

```mermaid
flowchart TD
    Start["Download fails"]
    
    Q1{"Can access<br/>youtube.com<br/>in browser?"}
    Q2{"Error mentions<br/>'yt-dlp' or<br/>'ImportError'?"}
    Q3{"Error mentions<br/>'Video unavailable'<br/>or 'private'?"}
    Q4{"Error mentions<br/>'HTTP' or<br/>'Network'?"}
    Q5{"Progress shows<br/>but hangs?"}
    Q6{"Subtitle missing<br/>but video OK?"}
    
    S1["Check network connection<br/>Verify DNS resolution<br/>Test with ping"]
    S2["Install yt-dlp:<br/>pip install yt-dlp"]
    S3["Video deleted/private<br/>or region restricted<br/>Try different URL"]
    S4["Configure proxy in .env:<br/>YT_DLP_PROXY=http://proxy:port"]
    S5["Check disk space<br/>Monitor I/O<br/>Configure rate limit"]
    S6["Check --list-subs output<br/>Video may have no subtitles<br/>Enable auto-generated subs"]
    
    Manual["Run manual yt-dlp test:<br/>yt-dlp --simulate URL"]
    Verbose["Enable verbose logging:<br/>verbose: True in ydl_opts"]
    
    Start --> Q1
    Q1 -->|No| S1
    Q1 -->|Yes| Q2
    Q2 -->|Yes| S2
    Q2 -->|No| Q3
    Q3 -->|Yes| S3
    Q3 -->|No| Q4
    Q4 -->|Yes| S4
    Q4 -->|No| Q5
    Q5 -->|Yes| S5
    Q5 -->|No| Q6
    Q6 -->|Yes| S6
    Q6 -->|No| Manual
    
    S1 --> Manual
    S2 --> Manual
    S3 --> Manual
    S4 --> Manual
    S5 --> Manual
    S6 --> Manual
    
    Manual --> Verbose
```

**Manual Testing Commands:**

```bash
# 1. Test video accessibility
yt-dlp --simulate https://youtube.com/watch?v=VIDEO_ID

# 2. List available formats
yt-dlp -F https://youtube.com/watch?v=VIDEO_ID

# 3. Test download with minimal options
yt-dlp --format best https://youtube.com/watch?v=VIDEO_ID

# 4. Test with proxy
yt-dlp --proxy http://proxy:port https://youtube.com/watch?v=VIDEO_ID

# 5. Test subtitle availability
yt-dlp --list-subs https://youtube.com/watch?v=VIDEO_ID

# 6. Enable verbose output
yt-dlp --verbose https://youtube.com/watch?v=VIDEO_ID
```

Sources: [scripts/download_video.py:27-153](), [references/yt-dlp-guide.md:107-149](), [references/yt-dlp-guide.md:243-284]()

---

## Configuration Reference

Environment variables in `.env` that affect download behavior:

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `YT_DLP_PROXY` | HTTP/HTTPS/SOCKS5 proxy for downloads | None (direct) | `http://proxy.example.com:8080` |
| `YT_DLP_RATE_LIMIT` | Maximum download speed | None (unlimited) | `4.2M` (4.2 MB/s) |
| `MAX_VIDEO_HEIGHT` | Maximum video resolution | 1080 | `720` or `1080` |
| `OUTPUT_DIR` | Base directory for downloads | `./youtube-clips` | `/path/to/output` |
| `TEMP_DIR` | Temporary file storage | System temp | `/path/to/temp` |

See [Environment Variables Reference](#6.1) for complete configuration documentation.

Sources: Configuration system documented in [6.1](#6.1) and [6.2](#6.2)

---

# Page: File Path and Encoding Issues

# File Path and Encoding Issues

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FIXES_AND_IMPROVEMENTS.md](FIXES_AND_IMPROVEMENTS.md)
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)
- [references/subtitle-formatting.md](references/subtitle-formatting.md)

</details>



This document addresses common problems related to file paths and character encoding encountered when processing YouTube videos. These issues can cause failures during video download, subtitle processing, or FFmpeg operations.

For issues specifically related to FFmpeg and libass installation, see [FFmpeg and libass Problems](#8.2). For general download problems, see [Download and Network Issues](#8.3).

## Overview of Path and Encoding Problems

The YouTube Clipper Skill encounters file path and encoding issues in three main areas:

1. **Special characters in video titles** causing filename problems
2. **Spaces in file paths** breaking FFmpeg subtitle filters
3. **Subtitle encoding** issues preventing proper text display

These problems can manifest during different stages of the processing pipeline and require specific workarounds.

Sources: [FIXES_AND_IMPROVEMENTS.md:58-93](), [TECHNICAL_NOTES.md:83-163]()

## File Path Special Characters Problem

### Problem Description

YouTube video titles often contain special characters that create problems when used in filenames:

| Character Type | Examples | Issues Caused |
|---------------|----------|---------------|
| Special punctuation | `'` `"` `:` `?` `*` | Shell command parsing errors |
| Unicode characters | `：` (full-width colon) | Path resolution failures |
| Spaces | Multiple consecutive spaces | Inconsistent path handling |
| Slashes | `/` `\` | Directory separator conflicts |

**Real-world example**: A video titled `Anthropic's Amodei on AI： Power and Risk` contains:
- Single quote (`'`) causing shell escaping issues
- Full-width colon (`：`) instead of regular colon
- Multiple spaces

Sources: [FIXES_AND_IMPROVEMENTS.md:58-69]()

### Original Implementation Issue

The initial implementation used video titles in output filenames:

```python
# Original approach (problematic)
'outtmpl': str(output_dir / '%(title)s [%(id)s].%(ext)s')
# Result: "Anthropic's Amodei on AI： Power and Risk [Ckt1cj0xjRM].mp4"
```

This caused:
- File not found errors when paths were passed to other scripts
- Shell command failures when quotes weren't properly escaped
- Inconsistent behavior across different operating systems

Sources: [FIXES_AND_IMPROVEMENTS.md:73-82](), [scripts/download_video.py:67]()

### Solution: Video ID-Based Filenames

The system now uses YouTube video IDs instead of titles for filenames:

```python
# Fixed approach
'outtmpl': str(output_dir / '%(id)s.%(ext)s')
# Result: "Ckt1cj0xjRM.mp4"
```

**Advantages**:
- Video IDs contain only alphanumeric characters, hyphens, and underscores
- Guaranteed uniqueness (no filename conflicts)
- Consistent length and format (typically 11 characters)
- Safe for all operating systems and shell commands
- Traceable back to original video

Sources: [FIXES_AND_IMPROVEMENTS.md:83-92](), [scripts/download_video.py:67]()

### Filename Sanitization Flow

```mermaid
flowchart TB
    VideoURL["YouTube Video URL"]
    Extract["yt-dlp extracts metadata"]
    
    subgraph "Filename Decision"
        Title["Video Title<br/>(contains special chars)"]
        VideoID["Video ID<br/>(alphanumeric only)"]
    end
    
    subgraph "Output Template"
        Template["outtmpl parameter"]
        SafeName["%(id)s.%(ext)s"]
    end
    
    subgraph "Result Files"
        VideoFile["Ckt1cj0xjRM.mp4"]
        SubFile["Ckt1cj0xjRM.en.vtt"]
    end
    
    VideoURL --> Extract
    Extract --> Title
    Extract --> VideoID
    
    Title -.->|"Not used"| Template
    VideoID --> Template
    Template --> SafeName
    SafeName --> VideoFile
    SafeName --> SubFile
    
    style VideoID fill:#f0f0f0
    style SafeName fill:#f0f0f0
    style VideoFile fill:#e8f5e9
    style SubFile fill:#e8f5e9
```

Sources: [scripts/download_video.py:45-92]()

## FFmpeg Path Space Limitation

### The Core Problem

FFmpeg's `subtitles` filter has a known bug where it cannot correctly parse file paths containing spaces, regardless of quoting or escaping attempts.

**Failed attempts** (all produce the same error):

```bash
# Attempt 1: Double quotes
ffmpeg -i video.mp4 -vf "subtitles='/path/with spaces/sub.srt'" output.mp4

# Attempt 2: Escaped spaces
ffmpeg -i video.mp4 -vf "subtitles=/path/with\ spaces/sub.srt" output.mp4

# Attempt 3: Mixed quoting
ffmpeg -i video.mp4 -vf subtitles="'/path/with spaces/sub.srt'" output.mp4

# Error (all cases):
# [Parsed_subtitles_0 @ 0x...] Unable to find '/path/with'
```

Note how the path is **truncated at the first space** (`/path/with spaces` → `/path/with`).

Sources: [TECHNICAL_NOTES.md:83-110]()

### Temporary Directory Workaround

The only reliable solution is to copy files to a temporary directory with a space-free path:

```mermaid
flowchart LR
    subgraph "User Space (May Have Spaces)"
        OrigVideo["Original Video<br/>/Users/John Doe/video.mp4"]
        OrigSub["Original Subtitle<br/>/Users/John Doe/sub.srt"]
        FinalOutput["Final Output<br/>/Users/John Doe/output.mp4"]
    end
    
    subgraph "Temporary Directory (No Spaces)"
        TempDir["mkdtemp()<br/>/tmp/youtube_clipper_abc123"]
        TempVideo["video.mp4"]
        TempSub["subtitle.srt"]
        TempOutput["output.mp4"]
    end
    
    subgraph "FFmpeg Processing"
        FFmpegCmd["ffmpeg -i video.mp4<br/>-vf subtitles=subtitle.srt<br/>output.mp4"]
    end
    
    OrigVideo -->|"shutil.copy"| TempVideo
    OrigSub -->|"shutil.copy"| TempSub
    TempVideo --> FFmpegCmd
    TempSub --> FFmpegCmd
    FFmpegCmd --> TempOutput
    TempOutput -->|"shutil.move"| FinalOutput
    
    style TempDir fill:#fff3e0
    style FFmpegCmd fill:#e3f2fd
    style FinalOutput fill:#e8f5e9
```

Sources: [TECHNICAL_NOTES.md:113-148](), [scripts/burn_subtitles.py:1-150]()

### Implementation in burn_subtitles.py

The temporary directory solution is implemented in [scripts/burn_subtitles.py:60-150]():

**Key steps**:

1. **Create temporary directory** with guaranteed space-free path:
   ```python
   temp_dir = tempfile.mkdtemp(prefix='youtube_clipper_')
   # Result: /tmp/youtube_clipper_xyz789
   ```

2. **Copy input files** to temporary directory with simple names:
   ```python
   temp_video = os.path.join(temp_dir, 'video.mp4')
   temp_subtitle = os.path.join(temp_dir, 'subtitle.srt')
   ```

3. **Run FFmpeg** with space-free paths:
   ```python
   cmd = [ffmpeg_path, '-i', temp_video, '-vf', 
          f'subtitles={temp_subtitle}:force_style=...', temp_output]
   ```

4. **Move result** back to original output location:
   ```python
   shutil.move(temp_output, output_path)
   ```

5. **Clean up** temporary directory:
   ```python
   shutil.rmtree(temp_dir, ignore_errors=True)
   ```

Sources: [scripts/burn_subtitles.py:60-150](), [TECHNICAL_NOTES.md:113-163]()

### Why This Approach Works

| Aspect | Details |
|--------|---------|
| `tempfile.mkdtemp()` | Creates directories like `/tmp/youtube_clipper_xyz789` (no spaces) |
| Platform compatibility | Works on Linux, macOS, Windows (uses OS temp directory) |
| User transparency | Original input/output paths can contain any characters |
| Performance | Copy overhead is minimal compared to FFmpeg processing time |
| Cleanup | `finally` block ensures temp files are removed even on error |

Sources: [TECHNICAL_NOTES.md:150-163]()

## Subtitle Encoding Issues

### Common Encoding Problems

Subtitle files from various sources may have encoding issues:

| Problem | Symptoms | Common Sources |
|---------|----------|----------------|
| Non-UTF-8 encoding | Garbled text, mojibake characters | Chinese/Japanese subtitles (GBK, Shift-JIS) |
| UTF-8 BOM | First subtitle displays incorrectly | Windows text editors |
| Mixed encoding | Some lines display correctly, others don't | Manual subtitle editing |
| Invalid characters | FFmpeg parsing errors | Corrupted downloads |

Sources: [references/subtitle-formatting.md:305-328]()

### Encoding Detection and Conversion

The system expects **UTF-8 encoding without BOM** for all subtitle files.

```mermaid
flowchart TB
    Download["Downloaded VTT<br/>(encoding unknown)"]
    
    subgraph "Encoding Verification"
        Check["Check file encoding"]
        IsUTF8{"UTF-8?"}
        HasBOM{"Has BOM?"}
    end
    
    subgraph "Conversion Steps"
        ConvertUTF8["Convert to UTF-8<br/>iconv -f SOURCE -t UTF-8"]
        RemoveBOM["Remove BOM<br/>sed to strip \\xEF\\xBB\\xBF"]
    end
    
    Clean["Clean UTF-8 file"]
    Process["Process in scripts"]
    
    Download --> Check
    Check --> IsUTF8
    
    IsUTF8 -->|"No"| ConvertUTF8
    IsUTF8 -->|"Yes"| HasBOM
    
    ConvertUTF8 --> HasBOM
    
    HasBOM -->|"Yes"| RemoveBOM
    HasBOM -->|"No"| Clean
    
    RemoveBOM --> Clean
    Clean --> Process
    
    style Clean fill:#e8f5e9
    style Process fill:#e8f5e9
```

Sources: [references/subtitle-formatting.md:307-328]()

### Encoding Verification Commands

**Check current encoding**:
```bash
file -i subtitle.srt
# Output: subtitle.srt: text/plain; charset=utf-8
```

**Convert GBK to UTF-8**:
```bash
iconv -f GBK -t UTF-8 input.srt > output.srt
```

**Remove UTF-8 BOM**:
```bash
sed -i '1s/^\xEF\xBB\xBF//' subtitle.srt
```

**Python encoding detection**:
```python
# Open with explicit UTF-8 (will fail if not UTF-8)
with open(subtitle_path, 'r', encoding='utf-8') as f:
    content = f.read()
```

Sources: [references/subtitle-formatting.md:312-328]()

### Why UTF-8 Without BOM

| Requirement | Reason |
|------------|--------|
| UTF-8 encoding | Supports all languages (English, Chinese, Japanese, etc.) |
| No BOM | BOM (`\xEF\xBB\xBF`) causes FFmpeg to display incorrectly in first subtitle |
| Consistent encoding | All scripts assume UTF-8, avoiding conversion overhead |
| Standard compliance | SRT and VTT specifications recommend UTF-8 |

Sources: [references/subtitle-formatting.md:305-328]()

## Cross-Platform Path Handling

### Using pathlib for Portability

The codebase uses Python's `pathlib` module to ensure cross-platform compatibility:

```python
from pathlib import Path

# ✅ Correct: Platform-independent
video_path = Path('/path/to/video.mp4')
output_path = output_dir / 'video.mp4'

# ❌ Avoid: Platform-specific
video_path = '/path/to/video.mp4'  # Unix-style
output_path = output_dir + '\\video.mp4'  # Windows-style
```

Sources: [TECHNICAL_NOTES.md:416-441](), [scripts/utils.py:1-200]()

### Path Construction Patterns

| Pattern | Example | Notes |
|---------|---------|-------|
| Join paths | `base_dir / 'video.mp4'` | Use `/` operator with Path objects |
| Check existence | `path.exists()` | Returns True/False |
| Get parent | `path.parent` | Returns parent directory as Path |
| Get filename | `path.name` | Returns filename with extension |
| Get stem | `path.stem` | Returns filename without extension |
| Convert to string | `str(path)` | When passing to external commands |

Sources: [TECHNICAL_NOTES.md:416-441]()

### Platform-Specific Considerations

```mermaid
flowchart TB
    subgraph "Script Execution"
        PathOp["Path Operation"]
    end
    
    subgraph "Platform Detection"
        Mac["macOS<br/>platform.system() == 'Darwin'"]
        Linux["Linux<br/>platform.system() == 'Linux'"]
        Win["Windows<br/>platform.system() == 'Windows'"]
    end
    
    subgraph "Path Characteristics"
        MacPath["/Users/name/file.mp4<br/>Case-insensitive<br/>Allows spaces"]
        LinuxPath["/home/name/file.mp4<br/>Case-sensitive<br/>Allows spaces"]
        WinPath["C:\\Users\\name\\file.mp4<br/>Case-insensitive<br/>Different separators"]
    end
    
    PathOp --> Mac
    PathOp --> Linux
    PathOp --> Win
    
    Mac --> MacPath
    Linux --> LinuxPath
    Win --> WinPath
    
    MacPath --> CommonHandling["pathlib.Path abstracts differences"]
    LinuxPath --> CommonHandling
    WinPath --> CommonHandling
    
    style CommonHandling fill:#e8f5e9
```

Sources: [scripts/burn_subtitles.py:20-45]()

### FFmpeg Path Handling

When passing paths to FFmpeg:

1. **Convert Path objects to strings**: `str(path)`
2. **Use list-style subprocess calls**: Avoids shell escaping issues
3. **Use temporary directory for spaces**: As described above

```python
# ✅ Correct: List-style command
cmd = [
    str(ffmpeg_path),
    '-i', str(input_path),
    '-vf', f'subtitles={str(subtitle_path)}',
    str(output_path)
]
subprocess.run(cmd, check=True)

# ❌ Avoid: String-style command (requires manual escaping)
cmd = f'{ffmpeg_path} -i {input_path} -vf subtitles={subtitle_path} {output_path}'
subprocess.run(cmd, shell=True)  # Unsafe
```

Sources: [scripts/burn_subtitles.py:90-150](), [scripts/clip_video.py:1-100]()

## Troubleshooting Steps

### Diagnosing File Path Problems

```mermaid
flowchart TD
    Error["Error: File not found or<br/>FFmpeg subtitles filter fails"]
    
    CheckExists{"File exists?"}
    CheckPath{"Path has<br/>spaces?"}
    CheckChars{"Special<br/>characters?"}
    CheckEnc{"Encoding<br/>UTF-8?"}
    
    Error --> CheckExists
    
    CheckExists -->|"No"| FixPath["Check video download<br/>Verify output_dir setting"]
    CheckExists -->|"Yes"| CheckPath
    
    CheckPath -->|"Yes"| UseTempDir["Issue: FFmpeg space bug<br/>Solution: Implemented in<br/>burn_subtitles.py"]
    CheckPath -->|"No"| CheckChars
    
    CheckChars -->|"Yes"| SanitizeFile["Issue: Special chars in title<br/>Solution: Using video ID<br/>in download_video.py"]
    CheckChars -->|"No"| CheckEnc
    
    CheckEnc -->|"No"| ConvertEnc["Convert to UTF-8:<br/>iconv -f SOURCE -t UTF-8"]
    CheckEnc -->|"Yes"| OtherIssue["Check FFmpeg logs<br/>Verify libass support"]
    
    style UseTempDir fill:#fff3e0
    style SanitizeFile fill:#fff3e0
    style ConvertEnc fill:#fff3e0
    style OtherIssue fill:#e3f2fd
```

Sources: [FIXES_AND_IMPROVEMENTS.md:1-293](), [TECHNICAL_NOTES.md:1-490]()

### Common Error Messages and Solutions

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `Unable to find '/path/with'` | Path contains spaces | Automatic: `burn_subtitles.py` uses temp directory |
| `File not found: 'video_title.mp4'` | Special characters in filename | Fixed: Video IDs used in `download_video.py:67` |
| `UnicodeDecodeError` | Non-UTF-8 subtitle encoding | Convert: `iconv -f GBK -t UTF-8 input.srt > output.srt` |
| First subtitle garbled | UTF-8 BOM present | Remove: `sed -i '1s/^\xEF\xBB\xBF//' subtitle.srt` |
| `No such file or directory` | Path object not converted to string | Convert: `str(path)` before passing to subprocess |

Sources: [FIXES_AND_IMPROVEMENTS.md:1-293](), [TECHNICAL_NOTES.md:83-163](), [references/subtitle-formatting.md:395-423]()

### Verification Commands

**Test file path handling**:
```bash
# Create test file with spaces
mkdir -p "/tmp/test path/youtube-clips"
touch "/tmp/test path/youtube-clips/test.srt"

# Python pathlib should handle this correctly
python3 -c "from pathlib import Path; p = Path('/tmp/test path/youtube-clips/test.srt'); print(p.exists())"
```

**Test subtitle encoding**:
```bash
# Check encoding
file -i subtitle.srt

# Test UTF-8 validity
iconv -f UTF-8 -t UTF-8 subtitle.srt > /dev/null && echo "Valid UTF-8"
```

**Test FFmpeg with subtitle**:
```bash
# This should work (no spaces)
ffmpeg -i video.mp4 -vf subtitles=/tmp/test.srt -t 5 test_output.mp4

# This will fail (spaces in path)
ffmpeg -i video.mp4 -vf "subtitles=/tmp/test path/test.srt" -t 5 test_output.mp4
```

Sources: [TECHNICAL_NOTES.md:1-490]()

### Prevention Best Practices

The codebase implements these preventive measures:

1. **Video IDs for downloads** [scripts/download_video.py:67]()
   - Eliminates special character problems at the source

2. **Temporary directory for FFmpeg** [scripts/burn_subtitles.py:60-150]()
   - Automatically handles space-in-path issues

3. **Path objects throughout** [scripts/utils.py:1-200]()
   - Ensures cross-platform compatibility

4. **Explicit UTF-8 encoding** [scripts/extract_subtitle_clip.py:1-100]()
   - Prevents encoding-related failures

5. **Error messages with context** [TECHNICAL_NOTES.md:444-475]()
   - Helps users diagnose issues quickly

Sources: [FIXES_AND_IMPROVEMENTS.md:207-237](), [TECHNICAL_NOTES.md:444-490]()

---

# Page: Development

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [FIXES_AND_IMPROVEMENTS.md](FIXES_AND_IMPROVEMENTS.md)
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)

</details>



This document provides technical guidance for developers working with the YouTube Clipper Skill codebase. It covers the repository structure, development practices, testing procedures, and contribution guidelines. For architectural details about how components interact, see [Architecture](#3). For detailed documentation of individual scripts, see [Core Scripts](#4).

## Development Environment

### Prerequisites

The YouTube Clipper Skill requires a specific development environment with both Python dependencies and external binary tools.

**Python Requirements:**
- Python 3.8 or higher
- Package dependencies: `yt-dlp`, `pysrt`, `python-dotenv`

**External Tools:**
- `yt-dlp` CLI tool for video downloading
- `FFmpeg` with `libass` support for video processing and subtitle burning
- Standard Unix utilities (`which`, `grep`, `mktemp`)

**Platform Considerations:**

```mermaid
graph TB
    subgraph "macOS Development"
        MacPy["Python 3.8+<br/>externally-managed"]
        FFmpegFull["ffmpeg-full<br/>/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
        YtDlpMac["yt-dlp<br/>Homebrew or pip"]
    end
    
    subgraph "Linux Development"
        LinuxPy["Python 3.8+<br/>system or virtualenv"]
        FFmpegLinux["ffmpeg<br/>with libass-dev"]
        YtDlpLinux["yt-dlp<br/>pip or package manager"]
    end
    
    subgraph "Installation Script"
        InstallSh["install_as_skill.sh"]
    end
    
    InstallSh -->|"Verifies"| MacPy
    InstallSh -->|"Detects"| FFmpegFull
    InstallSh -->|"Checks"| YtDlpMac
    
    InstallSh -->|"Verifies"| LinuxPy
    InstallSh -->|"Detects"| FFmpegLinux
    InstallSh -->|"Checks"| YtDlpLinux
    
    FFmpegFull -.->|"Required filter"| Libass["libass support<br/>subtitles filter"]
    FFmpegLinux -.->|"Required filter"| Libass
```

Sources: [install_as_skill.sh](), [TECHNICAL_NOTES.md:1-79]()

### Installing Dependencies

On macOS with externally-managed Python environments, use the `--break-system-packages` flag:

```bash
pip3 install --break-system-packages yt-dlp pysrt python-dotenv
```

For FFmpeg with libass support on macOS:

```bash
brew install ffmpeg-full
```

The standard Homebrew `ffmpeg` formula does not include libass. The `detect_ffmpeg_variant()` function in `burn_subtitles.py` checks for the appropriate FFmpeg installation.

Sources: [FIXES_AND_IMPROVEMENTS.md:9-24](), [TECHNICAL_NOTES.md:5-79]()

## Repository Organization

The repository follows a modular structure with clear separation between source code, documentation, configuration, and outputs.

```mermaid
graph TB
    Root["Repository Root"]
    
    subgraph "Source Code"
        Scripts["scripts/<br/>Python modules"]
        Download["download_video.py"]
        Analyze["analyze_subtitles.py"]
        Clip["clip_video.py"]
        Burn["burn_subtitles.py"]
        Extract["extract_subtitle_clip.py"]
        Utils["utils.py"]
    end
    
    subgraph "Configuration & Setup"
        EnvExample[".env.example<br/>Configuration template"]
        EnvFile[".env<br/>User configuration"]
        Install["install_as_skill.sh<br/>Setup automation"]
    end
    
    subgraph "Documentation"
        ReadmeEN["README.md"]
        ReadmeCN["README.zh-CN.md"]
        SkillDoc["SKILL.md"]
        TechNotes["TECHNICAL_NOTES.md"]
        Fixes["FIXES_AND_IMPROVEMENTS.md"]
    end
    
    subgraph "Development Files"
        GitIgnore[".gitignore<br/>Exclusion patterns"]
        GitHub[".github/<br/>Repository metadata"]
        Refs["references/<br/>Technical guides"]
    end
    
    subgraph "Runtime Generated"
        Output["youtube-clips/<br/>Output directory"]
        Temp["temp/<br/>Temporary files"]
    end
    
    Root --> Scripts
    Scripts --> Download
    Scripts --> Analyze
    Scripts --> Clip
    Scripts --> Burn
    Scripts --> Extract
    Scripts --> Utils
    
    Root --> EnvExample
    Root --> EnvFile
    Root --> Install
    
    Root --> ReadmeEN
    Root --> ReadmeCN
    Root --> SkillDoc
    Root --> TechNotes
    Root --> Fixes
    
    Root --> GitIgnore
    Root --> GitHub
    Root --> Refs
    
    Root -.->|"Creates"| Output
    Root -.->|"Creates"| Temp
    
    Utils -.->|"Imported by"| Download
    Utils -.->|"Imported by"| Analyze
    Utils -.->|"Imported by"| Clip
    Utils -.->|"Imported by"| Burn
    Utils -.->|"Imported by"| Extract
```

Sources: [.gitignore:1-52]()

### Key Directories and Files

| Path | Purpose | Generated? |
|------|---------|-----------|
| `scripts/` | All Python processing modules | No |
| `scripts/utils.py` | Shared utility functions across all scripts | No |
| `.env` | User-specific configuration (not committed) | Yes |
| `.env.example` | Configuration template with defaults | No |
| `TECHNICAL_NOTES.md` | Technical pitfalls and solutions | No |
| `FIXES_AND_IMPROVEMENTS.md` | Development history and bug fixes | No |
| `youtube-clips/` | Output directory for processed videos | Yes |
| `temp/` | Temporary files during processing | Yes |

The `.gitignore` file excludes runtime-generated content to keep the repository clean:

- Python artifacts: `__pycache__/`, `*.pyc`, `.eggs/`
- Configuration: `.env`, `.env.local`
- Outputs: `youtube-clips/`, `outputs/`, `downloads/`, `temp/`
- Media files: `*.mp4`, `*.vtt`, `*.srt`
- Test files: `test_*.py`, `*_test.py`

Sources: [.gitignore:1-52]()

## Script Interdependencies

Understanding the dependency relationships between scripts is essential for development work.

```mermaid
graph TB
    subgraph "Core Processing Scripts"
        DV["download_video.py<br/>Video acquisition"]
        AS["analyze_subtitles.py<br/>AI semantic analysis"]
        CV["clip_video.py<br/>Video segmentation"]
        ESC["extract_subtitle_clip.py<br/>Subtitle extraction"]
        BS["burn_subtitles.py<br/>Subtitle embedding"]
    end
    
    subgraph "Shared Utilities"
        Utils["utils.py"]
        TimeUtils["parse_timestamp()<br/>timestamp_to_seconds()<br/>format_timestamp()"]
        FileUtils["sanitize_filename()<br/>create_output_dir()"]
        ValidationUtils["validate_video_file()<br/>validate_subtitle_file()"]
    end
    
    subgraph "External Dependencies"
        YtDlpLib["yt_dlp<br/>Python library"]
        PySRT["pysrt<br/>SRT parsing"]
        DotEnv["python-dotenv<br/>Config loading"]
        Subprocess["subprocess<br/>FFmpeg execution"]
    end
    
    DV -->|"imports"| Utils
    DV -->|"imports"| YtDlpLib
    DV -->|"imports"| DotEnv
    
    AS -->|"imports"| Utils
    AS -->|"imports"| DotEnv
    
    CV -->|"imports"| Utils
    CV -->|"uses"| Subprocess
    
    ESC -->|"imports"| Utils
    ESC -->|"imports"| PySRT
    
    BS -->|"imports"| Utils
    BS -->|"uses"| Subprocess
    
    Utils --> TimeUtils
    Utils --> FileUtils
    Utils --> ValidationUtils
    
    TimeUtils -.->|"used by all"| DV
    TimeUtils -.->|"used by all"| AS
    TimeUtils -.->|"used by all"| CV
    TimeUtils -.->|"used by all"| ESC
    TimeUtils -.->|"used by all"| BS
```

Sources: [scripts/utils.py](), [scripts/download_video.py](), [scripts/analyze_subtitles.py](), [scripts/clip_video.py](), [scripts/burn_subtitles.py](), [scripts/extract_subtitle_clip.py]()

### Module Responsibilities

The `utils.py` module serves as the foundation for all processing scripts. It provides:

- **Time Conversion**: `parse_timestamp()`, `timestamp_to_seconds()`, `format_timestamp()`
- **File Management**: `sanitize_filename()`, `create_output_dir()`, `ensure_directory_exists()`
- **Validation**: `validate_video_file()`, `validate_subtitle_file()`, `check_file_exists()`
- **Path Handling**: Cross-platform path resolution using `pathlib.Path`

Each script imports from `utils.py` rather than duplicating functionality. This centralization simplifies maintenance and ensures consistent behavior across the system.

Sources: [scripts/utils.py]()

## Development Workflow

The typical development cycle involves modifying scripts, testing with real YouTube videos, and documenting any issues or improvements.

```mermaid
graph LR
    subgraph "Development Cycle"
        Edit["Modify Scripts"]
        Test["Test with<br/>YouTube Videos"]
        Debug["Debug Issues"]
        Document["Update Docs"]
        Commit["Git Commit"]
    end
    
    subgraph "Testing Artifacts"
        Logs["Error logs<br/>stdout/stderr"]
        Outputs["Generated files<br/>youtube-clips/"]
        Traces["Stack traces"]
    end
    
    subgraph "Documentation Updates"
        TechNotes["TECHNICAL_NOTES.md<br/>Technical pitfalls"]
        Fixes["FIXES_AND_IMPROVEMENTS.md<br/>Bug fixes & history"]
        Comments["Code comments<br/>docstrings"]
    end
    
    Edit --> Test
    Test --> Debug
    Test -.->|"generates"| Logs
    Test -.->|"generates"| Outputs
    Debug -.->|"produces"| Traces
    Debug --> Document
    Document --> TechNotes
    Document --> Fixes
    Document --> Comments
    Document --> Commit
    Commit --> Edit
```

### Iterative Testing Process

Development follows an iterative testing approach documented in `FIXES_AND_IMPROVEMENTS.md`. The file records:

- **Problem Description**: Detailed error messages and symptoms
- **Root Cause**: Analysis of why the issue occurred
- **Solution**: Code changes with before/after examples
- **Verification**: Testing results confirming the fix

For example, the division by zero error in the download progress hook was fixed by adding a null check:

```python
# Before (line 161):
if 'downloaded_bytes' in d and 'total_bytes' in d:
    percent = d['downloaded_bytes'] / d['total_bytes'] * 100

# After:
if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes']:
    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
```

Sources: [FIXES_AND_IMPROVEMENTS.md:28-54](), [scripts/download_video.py:156-178]()

## Recent Fixes and Improvements

The development history is thoroughly documented in `FIXES_AND_IMPROVEMENTS.md`, which tracks all significant bugs and improvements. Understanding this history helps avoid reintroducing solved problems.

### Major Fixes Implemented

| Issue | Impact | Solution | Status |
|-------|--------|----------|--------|
| Missing Python dependencies | Module import failures | Install with `--break-system-packages` | ✅ Fixed |
| Download progress division by zero | Crash during download | Null check for `total_bytes` | ✅ Fixed |
| Special characters in filenames | Path handling failures | Use video ID instead of title | ✅ Fixed |
| Output directory location | User confusion | Changed from `~/Videos` to `./youtube-clips` | ✅ Fixed |

### Special Characters in Filenames

The original implementation used video titles in output filenames via the template `'outtmpl': str(output_dir / '%(title)s [%(id)s].%(ext)s')`. This caused problems when titles contained:

- Single quotes (`'`)
- Full-width colons (`：` instead of `:`)
- Special Unicode characters

The fix changed to using only the video ID, which contains only safe characters (letters, numbers, hyphens, underscores):

```python
# Fixed template (line 67):
'outtmpl': str(output_dir / '%(id)s.%(ext)s')
```

This produces clean filenames like `Ckt1cj0xjRM.mp4` instead of `Anthropic's Amodei on AI： Power and Risk [Ckt1cj0xjRM].mp4`.

Sources: [FIXES_AND_IMPROVEMENTS.md:58-93](), [scripts/download_video.py:67]()

### Output Directory Change

User feedback indicated confusion about output location. The original default was `~/Videos/youtube-clips/`, which users didn't expect. The fix changed the default to `./youtube-clips/` (current working directory):

```python
# In utils.py (line 146):
# Before:
if base_dir is None:
    base_dir = Path.home() / "Videos" / "youtube-clips"

# After:
if base_dir is None:
    base_dir = Path.cwd() / "youtube-clips"
```

This aligns with user expectations and makes output files easier to locate.

Sources: [FIXES_AND_IMPROVEMENTS.md:96-134](), [scripts/utils.py:131-148]()

## Technical Pitfalls

The `TECHNICAL_NOTES.md` file documents critical technical challenges encountered during development. Developers modifying the codebase should review these to avoid common mistakes.

### FFmpeg libass Support Detection

Standard FFmpeg installations often lack libass support, which is required for the `subtitles` filter used in subtitle burning. The system implements a detection strategy:

```mermaid
graph TD
    Start["detect_ffmpeg_variant()"]
    
    CheckMac{"Platform == Darwin?"}
    CheckFull["Check /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
    FullExists{"Exists?"}
    ReturnFull["Return ffmpeg-full path"]
    
    CheckStandard["Find standard ffmpeg with which()"]
    StandardExists{"Found?"}
    
    CheckLibass["Run ffmpeg -filters | grep subtitles"]
    HasLibass{"Has libass?"}
    
    ReturnStandard["Return standard ffmpeg"]
    ReturnError["Return error: no libass support"]
    
    Start --> CheckMac
    CheckMac -->|"Yes"| CheckFull
    CheckFull --> FullExists
    FullExists -->|"Yes"| ReturnFull
    FullExists -->|"No"| CheckStandard
    CheckMac -->|"No"| CheckStandard
    
    CheckStandard --> StandardExists
    StandardExists -->|"Yes"| CheckLibass
    StandardExists -->|"No"| ReturnError
    
    CheckLibass --> HasLibass
    HasLibass -->|"Yes"| ReturnStandard
    HasLibass -->|"No"| ReturnError
```

Sources: [TECHNICAL_NOTES.md:5-79](), [scripts/burn_subtitles.py]()

### Temporary Directory Workaround for Path Spaces

FFmpeg's `subtitles` filter cannot handle file paths containing spaces, even with proper quoting or escaping. The solution uses a temporary directory with guaranteed space-free paths:

```python
# Pattern used in burn_subtitles.py:
temp_dir = tempfile.mkdtemp(prefix='youtube_clipper_')  # e.g., /tmp/youtube_clipper_abc123
try:
    # Copy files to temp_dir
    temp_video = os.path.join(temp_dir, 'video.mp4')
    temp_subtitle = os.path.join(temp_dir, 'subtitle.srt')
    shutil.copy(video_path, temp_video)
    shutil.copy(subtitle_path, temp_subtitle)
    
    # Process with space-free paths
    # ...
    
finally:
    shutil.rmtree(temp_dir, ignore_errors=True)
```

This approach is transparent to the user while working around FFmpeg's limitation.

Sources: [TECHNICAL_NOTES.md:82-163](), [scripts/burn_subtitles.py]()

### VTT to SRT Conversion

YouTube provides subtitles in VTT format, but FFmpeg's subtitle filter works better with SRT format. The key differences:

| Aspect | VTT | SRT |
|--------|-----|-----|
| Header | `WEBVTT` required | No header |
| Time separator | `.` (dot) | `,` (comma) |
| Sequence numbers | Optional | Required |
| Styling | Supported | Not supported |

The conversion must handle these differences while preserving subtitle content and timing.

Sources: [TECHNICAL_NOTES.md:166-213]()

### Batch Translation Optimization

A 30-minute video typically has 600 subtitle entries. Translating each individually would require 600 API calls. Batching 20-25 subtitles per call reduces this to ~30 calls, saving 95% of API usage while maintaining translation quality through context preservation.

The batch size of 20-25 is empirically determined:
- **Too small (< 20)**: Unnecessary API overhead
- **Too large (> 30)**: Translation quality degrades
- **Optimal (20-25)**: Best balance of efficiency and quality

Sources: [TECHNICAL_NOTES.md:260-305]()

## Testing and Verification

The system has been validated through real-world testing with actual YouTube videos. The test case documented in `FIXES_AND_IMPROVEMENTS.md` provides a comprehensive verification of all features.

### Test Video Specifications

```mermaid
graph TB
    TestVideo["Test Video:<br/>Ckt1cj0xjRM"]
    
    VideoProps["Video Properties"]
    VideoSize["Size: 368 MB"]
    VideoDuration["Duration: 25:25"]
    VideoFormat["Format: MP4 1080p"]
    
    SubProps["Subtitle Properties"]
    SubSize["Size: 41 KB"]
    SubCount["Count: 405 entries"]
    SubFormat["Format: VTT"]
    
    TestVideo --> VideoProps
    VideoProps --> VideoSize
    VideoProps --> VideoDuration
    VideoProps --> VideoFormat
    
    TestVideo --> SubProps
    SubProps --> SubSize
    SubProps --> SubCount
    SubProps --> SubFormat
    
    subgraph "Verified Outputs"
        Chapters["10 semantic chapters<br/>2-5 min granularity"]
        Clips["Video clips<br/>precise extraction"]
        Translations["Bilingual subtitles<br/>batch translation"]
        BurnedSubs["Subtitle burning<br/>libass rendering"]
        SocialCopy["Social media content<br/>3 platform variants"]
    end
    
    TestVideo -.->|"produces"| Chapters
    TestVideo -.->|"produces"| Clips
    TestVideo -.->|"produces"| Translations
    TestVideo -.->|"produces"| BurnedSubs
    TestVideo -.->|"produces"| SocialCopy
```

Sources: [FIXES_AND_IMPROVEMENTS.md:240-272]()

### Verified Functionality

The complete workflow has been tested end-to-end:

1. **Environment Detection**: yt-dlp and FFmpeg libass support confirmed
2. **Video Download**: 368 MB video with 405 subtitles downloaded successfully
3. **AI Chapter Analysis**: 10 semantic chapters generated (not mechanical time-based splits)
4. **Video Clipping**: Precise 2-minute segment extracted using FFmpeg
5. **Subtitle Processing**: 35 subtitles extracted, time-adjusted, and translated
6. **Subtitle Burning**: Bilingual subtitles embedded using libass filter
7. **Content Generation**: Three platform-specific social media variants created

Each stage produced the expected outputs with correct formatting and no data loss.

Sources: [FIXES_AND_IMPROVEMENTS.md:153-204]()

### Testing Approach

When making changes to the codebase:

1. **Unit-level testing**: Test individual functions with known inputs
2. **Integration testing**: Run complete workflows with test videos
3. **Error scenario testing**: Verify error handling for missing dependencies, invalid inputs, network failures
4. **Cross-platform testing**: Verify behavior on both macOS and Linux
5. **Documentation**: Update `FIXES_AND_IMPROVEMENTS.md` and `TECHNICAL_NOTES.md` with findings

The `.gitignore` file excludes test files (`test_*.py`, `*_test.py`) from version control, allowing developers to create local test scripts without cluttering the repository.

Sources: [.gitignore:39-47](), [FIXES_AND_IMPROVEMENTS.md:153-204]()

## Code Quality Practices

### Error Handling

All scripts implement comprehensive error handling with informative messages:

- Check for missing dependencies at import time
- Validate input files before processing
- Capture subprocess output for debugging
- Provide actionable error messages with installation instructions

### Path Handling

Use `pathlib.Path` exclusively for cross-platform compatibility. The codebase avoids string concatenation for paths, which fails on Windows.

### Documentation

Code should be self-documenting with:
- Clear function names describing purpose
- Docstrings explaining parameters and return values
- Inline comments for non-obvious logic
- Updates to `TECHNICAL_NOTES.md` for complex solutions

Sources: [TECHNICAL_NOTES.md:444-475]()

## Configuration Management

The `.env.example` file serves as the template for user configuration. When adding new configuration options:

1. Add the variable to `.env.example` with a descriptive comment
2. Set a reasonable default value
3. Document the option in the Configuration section of the wiki
4. Implement fallback logic if the variable is not set

The `.env` file is excluded from version control to protect user-specific settings and API keys.

Sources: [.env.example](), [.gitignore:15-18]()

## Contributing Guidelines

### Before Submitting Changes

1. Test changes with real YouTube videos
2. Verify no regressions in existing functionality
3. Update documentation files (`TECHNICAL_NOTES.md`, `FIXES_AND_IMPROVEMENTS.md`)
4. Ensure `.gitignore` patterns cover any new generated files
5. Follow existing code style and patterns

### Documentation Standards

When documenting fixes or improvements:

- Include the full error message
- Explain the root cause
- Show before/after code with line numbers
- Document verification steps
- Mark status (✅ Fixed, ⚠️ Workaround, ❌ Unsolved)

Sources: [FIXES_AND_IMPROVEMENTS.md:1-292](), [TECHNICAL_NOTES.md:1-490]()

---

# Page: Project Structure

# Project Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [scripts/__init__.py](scripts/__init__.py)

</details>



This document describes the physical organization of the YouTube Clipper Skill repository, including directory layout, file purposes, and the role of each component. For installation procedures, see [Installation](#2.1). For detailed information about individual Python scripts, see [Core Scripts](#4).

The repository follows a flat structure with most source code in the `scripts/` directory, documentation at the root level, and configuration managed through `.env` files. The skill is designed to be installed into `~/.claude/skills/youtube-clipper/` for use within the Claude Code environment.

---

## Repository Root Structure

The repository root contains three primary categories of files: documentation, configuration templates, and the installation script. All Python source code resides in the `scripts/` subdirectory.

```mermaid
graph TB
    Root["Repository Root<br/>(~/.claude/skills/youtube-clipper/)"]
    
    Root --> Scripts["scripts/<br/>Python modules"]
    Root --> Refs["references/<br/>Technical guides"]
    Root --> GitHub[".github/<br/>Metadata"]
    
    Root --> ConfigFiles["Configuration Files"]
    Root --> DocFiles["Documentation Files"]
    Root --> InstallFiles["Installation Files"]
    
    ConfigFiles --> EnvExample[".env.example<br/>Configuration template"]
    ConfigFiles --> GitIgnore[".gitignore<br/>Git exclusions"]
    
    DocFiles --> ReadmeEN["README.md<br/>English documentation"]
    DocFiles --> ReadmeCN["README.zh-CN.md<br/>Chinese documentation"]
    DocFiles --> SkillMD["SKILL.md<br/>Detailed usage guide"]
    DocFiles --> TechNotes["TECHNICAL_NOTES.md<br/>Implementation notes"]
    DocFiles --> Fixes["FIXES_AND_IMPROVEMENTS.md<br/>Changelog"]
    DocFiles --> License["LICENSE<br/>MIT License"]
    
    InstallFiles --> InstallScript["install_as_skill.sh<br/>Setup automation"]
    
    Scripts --> InitPy["__init__.py"]
    Scripts --> DownloadPy["download_video.py"]
    Scripts --> AnalyzePy["analyze_subtitles.py"]
    Scripts --> ClipPy["clip_video.py"]
    Scripts --> BurnPy["burn_subtitles.py"]
    Scripts --> ExtractPy["extract_subtitle_clip.py"]
    Scripts --> UtilsPy["utils.py"]
```

**Directory Tree Structure:**
```
youtube-clipper/
├── .github/                    # GitHub metadata
├── references/                 # Technical reference documents
├── scripts/                    # Python source code
│   ├── __init__.py            # Package initialization
│   ├── download_video.py      # Video acquisition
│   ├── analyze_subtitles.py   # AI chapter analysis
│   ├── clip_video.py          # Video segmentation
│   ├── burn_subtitles.py      # Subtitle embedding
│   ├── extract_subtitle_clip.py # Subtitle extraction
│   └── utils.py               # Shared utilities
├── .env.example               # Configuration template
├── .gitignore                 # Git exclusions
├── install_as_skill.sh        # Installation script
├── LICENSE                    # MIT License
├── README.md                  # English documentation
├── README.zh-CN.md           # Chinese documentation
├── SKILL.md                   # Detailed usage guide
├── TECHNICAL_NOTES.md        # Implementation notes
└── FIXES_AND_IMPROVEMENTS.md # Changelog
```

Sources: [README.md:1-320](), [.gitignore:1-52](), [scripts/__init__.py:1-8]()

---

## Source Code Directory: scripts/

All Python source code resides in the `scripts/` directory, which is structured as a Python package. Each script has a single, well-defined responsibility in the video processing pipeline.

### Core Processing Scripts

| File | Purpose | Primary Dependencies |
|------|---------|---------------------|
| `download_video.py` | Downloads YouTube videos and subtitles using yt-dlp | `yt_dlp`, `utils.py` |
| `analyze_subtitles.py` | Analyzes subtitle content to generate semantic chapters | Claude AI, `utils.py` |
| `clip_video.py` | Extracts video segments using FFmpeg | FFmpeg, `utils.py` |
| `burn_subtitles.py` | Burns subtitles into video files | FFmpeg with libass, `utils.py` |
| `extract_subtitle_clip.py` | Extracts and adjusts subtitle segments | `pysrt`, `utils.py` |
| `utils.py` | Provides shared utility functions for time conversion, file management, and validation | `python-dotenv`, `os`, `re` |

### Script Dependency Graph

```mermaid
graph LR
    subgraph "scripts/"
        download_video.py["download_video.py"]
        analyze_subtitles.py["analyze_subtitles.py"]
        clip_video.py["clip_video.py"]
        burn_subtitles.py["burn_subtitles.py"]
        extract_subtitle_clip.py["extract_subtitle_clip.py"]
        utils.py["utils.py"]
    end
    
    subgraph "External Libraries"
        yt_dlp["yt_dlp<br/>(Python library)"]
        pysrt["pysrt<br/>(SRT parser)"]
        dotenv["python-dotenv<br/>(Config loader)"]
    end
    
    subgraph "System Binaries"
        yt_dlp_bin["yt-dlp<br/>(CLI)"]
        ffmpeg["FFmpeg<br/>(CLI)"]
    end
    
    subgraph "AI Services"
        claude["Claude AI<br/>(via Claude Code)"]
    end
    
    download_video.py --> utils.py
    download_video.py --> yt_dlp
    download_video.py --> dotenv
    download_video.py -.->|subprocess| yt_dlp_bin
    
    analyze_subtitles.py --> utils.py
    analyze_subtitles.py --> dotenv
    analyze_subtitles.py -.->|API calls| claude
    
    clip_video.py --> utils.py
    clip_video.py -.->|subprocess| ffmpeg
    
    burn_subtitles.py --> utils.py
    burn_subtitles.py -.->|subprocess| ffmpeg
    
    extract_subtitle_clip.py --> utils.py
    extract_subtitle_clip.py --> pysrt
```

### Package Initialization

The `scripts/__init__.py` file defines the package metadata:

- `__version__`: "1.0.0"
- `__author__`: "Claude Code"

[scripts/__init__.py:1-8]()

Sources: [README.md:42-46](), [README.md:60-66](), [scripts/__init__.py:1-8]()

---

## Configuration Files

### .env.example

The configuration template located at [.env.example]() provides default values and documentation for all environment variables. During installation, this file is copied to `.env` where users can customize settings. Key configuration categories include:

- File paths (FFmpeg location, output directories)
- Video download settings (quality limits, proxy configuration)
- Subtitle settings (font size, margins, target language)
- Processing settings (batch sizes, chapter duration targets)
- Logging levels

For complete configuration reference, see [Environment Variables Reference](#6.1).

### .gitignore

The [.gitignore:1-52]() file excludes several categories of files from version control:

**Python Artifacts:**
- `__pycache__/`, `*.py[cod]`, `*.egg-info/`
- Virtual environments: `venv/`, `env/`, `ENV/`

**Configuration:**
- `.env`, `.env.local`, `.env.*.local`

**Output Directories:**
- `youtube-clips/`, `outputs/`, `downloads/`, `temp/`, `tmp/`

**Media Files:**
- `*.mp4`, `*.webm`, `*.mkv`, `*.avi`, `*.vtt`, `*.srt`

**Development Files:**
- IDE configurations: `.vscode/`, `.idea/`
- Test files: `test_*.py`, `*_test.py`
- Logs: `*.log`, `logs/`

Sources: [.gitignore:1-52](), [README.md:129-154]()

---

## Documentation Structure

Documentation is organized into multiple files targeting different audiences and use cases:

### Primary Documentation

```mermaid
graph TB
    Users["End Users"]
    Developers["Developers"]
    Contributors["Contributors"]
    
    Users --> ReadmeEN["README.md<br/>Quick start, features, installation"]
    Users --> ReadmeCN["README.zh-CN.md<br/>中文版快速开始"]
    Users --> SkillMD["SKILL.md<br/>Detailed workflow and usage"]
    
    Developers --> TechNotes["TECHNICAL_NOTES.md<br/>Implementation details"]
    Developers --> Refs["references/<br/>External tool guides"]
    
    Contributors --> Fixes["FIXES_AND_IMPROVEMENTS.md<br/>Recent changes and fixes"]
    Contributors --> License["LICENSE<br/>MIT License terms"]
```

| File | Target Audience | Contents |
|------|----------------|----------|
| `README.md` | End users | Features overview, installation instructions, basic usage, troubleshooting |
| `README.zh-CN.md` | Chinese-speaking users | Full Chinese translation of README |
| `SKILL.md` | Advanced users | Complete workflow documentation, detailed usage patterns |
| `TECHNICAL_NOTES.md` | Developers | Architecture decisions, implementation notes, design rationale |
| `FIXES_AND_IMPROVEMENTS.md` | Developers/Contributors | Changelog, bug fixes, lessons learned |
| `LICENSE` | Legal compliance | MIT License text |

### References Directory

The `references/` directory contains technical reference materials for external dependencies and file format specifications. This typically includes:

- FFmpeg command reference
- yt-dlp usage patterns
- Subtitle format specifications (VTT, SRT)
- libass filter documentation

Sources: [README.md:282-287]()

---

## Installation Script: install_as_skill.sh

The [install_as_skill.sh]() script automates the installation process by performing these operations:

1. **Directory Creation**: Creates `~/.claude/skills/youtube-clipper/`
2. **File Copying**: Copies all necessary files to the skill directory
3. **Dependency Installation**: Installs Python packages (`yt-dlp`, `pysrt`, `python-dotenv`)
4. **Dependency Verification**: Checks for system dependencies (Python 3.8+, yt-dlp, FFmpeg)
5. **Configuration Setup**: Creates `.env` file from `.env.example` template
6. **Permission Setting**: Makes scripts executable

The script provides status messages throughout the process and reports any missing dependencies.

Sources: [README.md:36-47]()

---

## Output Directory Structure

Video processing outputs are written to `./youtube-clips/` by default (configurable via `OUTPUT_DIR` in `.env`). The output follows a three-level hierarchy to prevent file conflicts and maintain clear provenance.

### Output Hierarchy

```mermaid
graph TB
    Root["./youtube-clips/"]
    
    Root --> Session1["20260122_143022/<br/>(Timestamp)"]
    Root --> Session2["20260123_091500/<br/>(Timestamp)"]
    
    Session1 --> Chapter1["Chapter_1_Title/<br/>(Sanitized name)"]
    Session1 --> Chapter2["Chapter_2_Title/<br/>(Sanitized name)"]
    
    Chapter1 --> ClipFile["Chapter_1_Title_clip.mp4<br/>(Original segment)"]
    Chapter1 --> BurnedFile["Chapter_1_Title_with_subtitles.mp4<br/>(Burned subtitles)"]
    Chapter1 --> SRTFile["Chapter_1_Title_bilingual.srt<br/>(Dual language)"]
    Chapter1 --> SummaryFile["Chapter_1_Title_summary.md<br/>(Social media copy)"]
```

**Directory Structure:**
```
./youtube-clips/
└── 20260122_143022/              # Timestamp: YYYYMMDD_HHMMSS
    ├── Chapter_1_AGI_Definition/
    │   ├── Chapter_1_AGI_Definition_clip.mp4
    │   ├── Chapter_1_AGI_Definition_with_subtitles.mp4
    │   ├── Chapter_1_AGI_Definition_bilingual.srt
    │   └── Chapter_1_AGI_Definition_summary.md
    └── Chapter_2_China_AI_Landscape/
        ├── Chapter_2_China_AI_Landscape_clip.mp4
        ├── Chapter_2_China_AI_Landscape_with_subtitles.mp4
        ├── Chapter_2_China_AI_Landscape_bilingual.srt
        └── Chapter_2_China_AI_Landscape_summary.md
```

### File Types Per Chapter

Each processed chapter can generate up to four file types:

1. **`*_clip.mp4`**: Video segment extracted from source (always generated)
2. **`*_with_subtitles.mp4`**: Video with burned-in bilingual subtitles (optional)
3. **`*_bilingual.srt`**: Separate bilingual subtitle file (optional)
4. **`*_summary.md`**: Social media content summary (optional)

The actual files generated depend on user selections during the workflow.

Sources: [README.md:112-124](), [.gitignore:32-37]()

---

## Files by Functional Category

The following diagram categorizes repository files by their primary function, showing the relationship between code, configuration, documentation, and output.

```mermaid
graph TB
    subgraph "Execution Layer"
        install_as_skill.sh["install_as_skill.sh<br/>Bootstrap installation"]
        
        subgraph "scripts/"
            download_video.py["download_video.py"]
            analyze_subtitles.py["analyze_subtitles.py"]
            clip_video.py["clip_video.py"]
            burn_subtitles.py["burn_subtitles.py"]
            extract_subtitle_clip.py["extract_subtitle_clip.py"]
            utils.py["utils.py"]
        end
    end
    
    subgraph "Configuration Layer"
        env_example[".env.example<br/>Template"]
        env[".env<br/>User settings"]
        gitignore[".gitignore<br/>VCS exclusions"]
    end
    
    subgraph "Documentation Layer"
        README.md["README.md"]
        SKILL.md["SKILL.md"]
        TECHNICAL_NOTES.md["TECHNICAL_NOTES.md"]
        FIXES_AND_IMPROVEMENTS.md["FIXES_AND_IMPROVEMENTS.md"]
        references["references/"]
    end
    
    subgraph "Output Layer"
        youtube_clips["youtube-clips/<br/>Generated content"]
    end
    
    install_as_skill.sh -.->|creates| env
    install_as_skill.sh -.->|copies| env_example
    
    env --> download_video.py
    env --> analyze_subtitles.py
    env --> burn_subtitles.py
    
    utils.py --> download_video.py
    utils.py --> analyze_subtitles.py
    utils.py --> clip_video.py
    utils.py --> burn_subtitles.py
    utils.py --> extract_subtitle_clip.py
    
    download_video.py --> clip_video.py
    clip_video.py --> extract_subtitle_clip.py
    extract_subtitle_clip.py --> burn_subtitles.py
    
    burn_subtitles.py --> youtube_clips
```

### Category Breakdown

**Execution Layer:**
- Installation automation: `install_as_skill.sh`
- Core processing: All Python scripts in `scripts/`
- Shared utilities: `utils.py`

**Configuration Layer:**
- Template: `.env.example`
- User configuration: `.env` (created during installation)
- Version control: `.gitignore`

**Documentation Layer:**
- User guides: `README.md`, `README.zh-CN.md`, `SKILL.md`
- Technical documentation: `TECHNICAL_NOTES.md`, `FIXES_AND_IMPROVEMENTS.md`
- Reference materials: `references/` directory
- Legal: `LICENSE`

**Output Layer:**
- Generated content: `youtube-clips/` directory (excluded from VCS)
- Temporary files: Cleaned up after processing by default

Sources: [README.md:1-320](), [.gitignore:1-52](), [scripts/__init__.py:1-8]()

---

## Installation Target Directory

When installed via `install_as_skill.sh` or `npx skills`, the entire repository is copied to:

```
~/.claude/skills/youtube-clipper/
```

This location allows Claude Code to discover and invoke the skill. The directory structure remains identical to the source repository, with the addition of a `.env` file created from `.env.example`.

The skill is invoked by Claude Code when users provide natural language commands related to YouTube video clipping. For workflow details, see [Understanding the Workflow](#2.3).

Sources: [README.md:28-47]()

---

# Page: Recent Fixes and Improvements

# Recent Fixes and Improvements

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FIXES_AND_IMPROVEMENTS.md](FIXES_AND_IMPROVEMENTS.md)
- [README.md](README.md)
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md)

</details>



## Purpose and Scope

This document details the bug fixes, architectural improvements, and optimization changes made to the YouTube Clipper Skill during initial testing and subsequent development. Each fix is documented with the problem encountered, root cause analysis, solution implemented, and verification results.

For information about core script functionality, see [Core Scripts](#4). For FFmpeg integration details, see [FFmpeg Integration](#5.2). For troubleshooting user-facing issues, see [Troubleshooting](#8).

---

## Overview of Major Fixes

The YouTube Clipper Skill underwent comprehensive testing that revealed five critical issues and several optimization opportunities. All core functionality has been verified and is production-ready.

### Fix Implementation Timeline

```mermaid
graph TB
    Testing["Initial Testing<br/>Video: Ckt1cj0xjRM<br/>Duration: 25:25"]
    
    subgraph "Critical Fixes"
        Dep["Python Dependencies<br/>ModuleNotFoundError"]
        Progress["Progress Hook Error<br/>Division by NoneType"]
        Filename["Filename Special Characters<br/>Path handling failures"]
        OutputDir["Output Directory<br/>Location mismatch"]
    end
    
    subgraph "FFmpeg Improvements"
        LibassDetect["libass Detection<br/>ffmpeg-full support"]
        PathSpaces["Path Space Handling<br/>Temporary directory workaround"]
    end
    
    subgraph "Optimizations"
        BatchTrans["Batch Translation<br/>95% API reduction"]
        FileNaming["Video ID Naming<br/>Avoid special chars"]
    end
    
    Testing --> Dep
    Testing --> Progress
    Testing --> Filename
    Testing --> OutputDir
    
    Dep --> LibassDetect
    Progress --> BatchTrans
    Filename --> FileNaming
    OutputDir --> PathSpaces
    
    style Testing fill:#f9f9f9
    style Dep fill:#ffe6e6
    style Progress fill:#ffe6e6
    style Filename fill:#ffe6e6
    style OutputDir fill:#ffe6e6
```

**Sources:** [FIXES_AND_IMPROVEMENTS.md:1-293]()

---

## Critical Bug Fixes

### Python Dependency Installation

#### Problem

`ModuleNotFoundError` was raised when attempting to import `yt_dlp` and `pysrt` modules on macOS systems.

```
ModuleNotFoundError: No module named 'yt_dlp'
ModuleNotFoundError: No module named 'pysrt'
```

#### Root Cause

macOS Python environments are marked as "externally-managed" (PEP 668), preventing standard `pip install` commands from modifying system Python packages without explicit override flags.

#### Solution

The installation script was updated to use `--break-system-packages` flag for pip installations on systems with externally-managed Python environments.

```bash
# install_as_skill.sh implementation
pip3 install --break-system-packages yt-dlp pysrt python-dotenv
```

#### Verification

All three required packages (`yt-dlp`, `pysrt`, `python-dotenv`) installed successfully and passed import verification tests.

**Sources:** [FIXES_AND_IMPROVEMENTS.md:9-25](), [install_as_skill.sh:1-100]()

---

### Download Progress Hook Division Error

#### Problem

A `TypeError` occurred during video download progress reporting:

```
TypeError: unsupported operand type(s) for /: 'int' and 'NoneType'
```

The error originated from calculating download percentage when `total_bytes` was `None`.

#### Code Location

The bug was in the `_progress_hook` function within `download_video.py`.

```mermaid
graph LR
    Hook["_progress_hook(d)"]
    Check["d['total_bytes'] exists?"]
    Calc["percent = downloaded / total_bytes * 100"]
    Error["TypeError: int / None"]
    
    Hook --> Check
    Check -->|"Yes, but None value"| Calc
    Calc --> Error
    
    style Error fill:#ffe6e6
```

#### Solution Implementation

Added null-value checking before performing division operation:

[scripts/download_video.py:156-178]()

```python
# Before fix (line 161)
if 'downloaded_bytes' in d and 'total_bytes' in d:
    percent = d['downloaded_bytes'] / d['total_bytes'] * 100

# After fix
if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes']:
    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
else:
    # Fallback: display only downloaded size and speed
    downloaded_mb = d.get('downloaded_bytes', 0) / (1024 * 1024)
    speed_mb = d.get('speed', 0) / (1024 * 1024) if d.get('speed') else 0
    # Display without percentage
```

The fix also implements fallback display logic showing downloaded size and speed when total size is unavailable.

**Sources:** [FIXES_AND_IMPROVEMENTS.md:28-55](), [scripts/download_video.py:156-178]()

---

### Filename Special Character Handling

#### Problem

Downloaded video files contained special characters that caused path handling failures:

```
Anthropic's Amodei on AI： Power and Risk [Ckt1cj0xjRM].mp4
                           ^                              
                    Full-width colon (U+FF1A)
```

Issues included:
- Single quotes in filenames
- Full-width colons (：) vs ASCII colons (:)
- Shell command parsing failures
- Path construction errors

#### Root Cause Analysis

The `yt-dlp` output template used video titles directly:

```python
'outtmpl': str(output_dir / '%(title)s [%(id)s].%(ext)s')
```

YouTube video titles frequently contain problematic characters that are valid in titles but cause filesystem or shell issues.

#### Solution: Video ID-Based Naming

Modified the output template to use only the video ID, which is guaranteed to contain only alphanumeric characters, hyphens, and underscores:

[scripts/download_video.py:67]()

```python
# Before
'outtmpl': str(output_dir / '%(title)s [%(id)s].%(ext)s')

# After
'outtmpl': str(output_dir / '%(id)s.%(ext)s')
```

#### Benefits

| Aspect | Title-Based | ID-Based |
|--------|-------------|----------|
| **Special Characters** | High risk (quotes, colons, slashes) | None (alphanumeric + `-_`) |
| **Uniqueness** | Not guaranteed | Guaranteed unique |
| **Length** | Variable (can be very long) | Fixed (11 characters) |
| **Shell Safety** | Requires escaping | No escaping needed |
| **Example** | `Anthropic's Amodei on AI： Power and Risk [Ckt1cj0xjRM].mp4` | `Ckt1cj0xjRM.mp4` |

**Sources:** [FIXES_AND_IMPROVEMENTS.md:59-93](), [scripts/download_video.py:67]()

---

### Output Directory Location Fix

#### Problem

During testing, output files were saved to `/tmp/youtube_clipper_output/` instead of the user's current working directory. User feedback indicated expectation that outputs would appear in the currently opened folder.

#### Root Cause

The default base directory in `create_output_dir()` was set to `~/Videos/youtube-clips`:

[scripts/utils.py:146]()

```python
# Before fix
if base_dir is None:
    base_dir = Path.home() / "Videos" / "youtube-clips"
```

This design assumed a centralized video storage location, but violated user expectations for CLI tools that typically use the current working directory.

#### Solution Implementation

Changed default base directory to current working directory:

[scripts/utils.py:131-148]()

```python
# After fix
if base_dir is None:
    base_dir = Path.cwd() / "youtube-clips"
```

#### Directory Structure Comparison

```mermaid
graph TB
    subgraph "Before Fix"
        HomeOld["/Users/username"]
        VideosOld["Videos/"]
        ClipsOld["youtube-clips/"]
        SessionOld["20260122_143022/"]
        
        HomeOld --> VideosOld
        VideosOld --> ClipsOld
        ClipsOld --> SessionOld
    end
    
    subgraph "After Fix"
        CwdNew["/current/working/directory"]
        ClipsNew["youtube-clips/"]
        SessionNew["20260122_143022/"]
        
        CwdNew --> ClipsNew
        ClipsNew --> SessionNew
    end
    
    style SessionOld fill:#ffe6e6
    style SessionNew fill:#e6ffe6
```

#### Documentation Updates

Corresponding documentation changes were made throughout the repository:

- `SKILL.md`: Updated output path references from `~/Videos/youtube-clips/` to `./youtube-clips/`
- `README.md`: Updated example output paths
- Added clarification that output directory is relative to current working directory

**Sources:** [FIXES_AND_IMPROVEMENTS.md:96-135](), [scripts/utils.py:131-148](), [README.md:110-123]()

---

## FFmpeg Integration Improvements

### libass Detection and Support

#### Problem Statement

The `subtitles` filter in FFmpeg requires `libass` library support, which is not included in the standard Homebrew FFmpeg package on macOS. This caused subtitle burning to fail with:

```
No such filter: 'subtitles'
```

#### Detection Logic Flow

```mermaid
graph TD
    Start["burn_subtitles.py called"]
    
    DetectOS["Detect Operating System"]
    
    CheckMac{"platform.system() == 'Darwin'?"}
    CheckFull["Check /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"]
    ExistsFull{"Path exists?"}
    VerifyFull["Verify libass with<br/>ffmpeg -filters | grep subtitles"]
    HasLibass{"Has libass?"}
    
    CheckStd["Check standard ffmpeg path<br/>shutil.which('ffmpeg')"]
    ExistsStd{"Path exists?"}
    VerifyStd["Verify libass support"]
    
    UseFull["Use ffmpeg-full<br/>type='full'"]
    UseStd["Use standard ffmpeg<br/>type='standard'"]
    Error["Raise RuntimeError<br/>Install ffmpeg-full"]
    
    Start --> DetectOS
    DetectOS --> CheckMac
    
    CheckMac -->|Yes macOS| CheckFull
    CheckFull --> ExistsFull
    ExistsFull -->|Yes| VerifyFull
    VerifyFull --> HasLibass
    HasLibass -->|Yes| UseFull
    HasLibass -->|No| CheckStd
    ExistsFull -->|No| CheckStd
    
    CheckMac -->|No| CheckStd
    CheckStd --> ExistsStd
    ExistsStd -->|Yes| VerifyStd
    VerifyStd -->|Has libass| UseStd
    VerifyStd -->|No libass| Error
    ExistsStd -->|No| Error
```

#### Implementation

The detection logic in `burn_subtitles.py` implements a multi-tier fallback strategy:

[scripts/burn_subtitles.py:50-120]()

1. **Priority 1**: Check for `ffmpeg-full` on macOS at `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
2. **Priority 2**: Check standard `ffmpeg` in system PATH
3. **Verification**: Test each candidate for `subtitles` filter availability
4. **Error Handling**: Provide installation instructions if no suitable FFmpeg found

#### Platform-Specific Paths

| Platform | Package | Path | Command |
|----------|---------|------|---------|
| **macOS (Apple Silicon)** | ffmpeg-full | `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` | `brew install ffmpeg-full` |
| **macOS (Intel)** | ffmpeg-full | `/usr/local/opt/ffmpeg-full/bin/ffmpeg` | `brew install ffmpeg-full` |
| **Ubuntu/Debian** | ffmpeg + libass-dev | `/usr/bin/ffmpeg` | `apt install ffmpeg libass-dev` |
| **From Source** | Custom build | `/usr/local/bin/ffmpeg` | `./configure --enable-libass` |

**Sources:** [TECHNICAL_NOTES.md:5-80](), [scripts/burn_subtitles.py:50-120](), [README.md:67-83]()

---

### Temporary Directory Workaround for Path Spaces

#### Problem Description

FFmpeg's `subtitles` filter fails to parse file paths containing spaces, even with proper quoting or escaping:

```bash
# All of these fail:
ffmpeg -i video.mp4 -vf "subtitles='/path/with spaces/sub.srt'" out.mp4
ffmpeg -i video.mp4 -vf "subtitles=/path/with\ spaces/sub.srt" out.mp4
ffmpeg -i video.mp4 -vf subtitles="'/path/with spaces/sub.srt'" out.mp4

# Error: Unable to find '/path/with'
#        (path truncated at first space)
```

This is a known FFmpeg limitation in the libass subtitle filter's path parser.

#### Solution Architecture

```mermaid
graph TB
    Input["Input Files<br/>May contain spaces in path"]
    
    CreateTemp["tempfile.mkdtemp()<br/>prefix='youtube_clipper_'<br/>Result: /tmp/youtube_clipper_abc123"]
    
    Copy["Copy to Temporary Directory<br/>video.mp4, subtitle.srt"]
    
    Process["FFmpeg Processing<br/>subtitles=/tmp/.../subtitle.srt<br/>(No spaces in path)"]
    
    Move["Move output to<br/>Original destination path"]
    
    Cleanup["shutil.rmtree(temp_dir)"]
    
    Output["Output File<br/>At user-specified location"]
    
    Input --> CreateTemp
    CreateTemp --> Copy
    Copy --> Process
    Process --> Move
    Move --> Cleanup
    Cleanup --> Output
    
    style CreateTemp fill:#e6f3ff
    style Process fill:#e6ffe6
```

#### Implementation Details

[scripts/burn_subtitles.py:200-280]()

The implementation follows this pattern:

1. **Create**: Generate temporary directory with `tempfile.mkdtemp(prefix='youtube_clipper_')` which produces paths like `/tmp/youtube_clipper_a8f3d9/`
2. **Copy**: Use `shutil.copy()` to copy input video and subtitle files to temporary directory with simple names (`video.mp4`, `subtitle.srt`)
3. **Process**: Execute FFmpeg with space-free paths
4. **Retrieve**: Move processed output back to original user-specified path (which may contain spaces)
5. **Cleanup**: Remove temporary directory with `shutil.rmtree(temp_dir, ignore_errors=True)`

#### Why This Works

| Approach | Result | Reason |
|----------|--------|--------|
| **Quoting paths** | ❌ Fails | libass parser doesn't respect quotes |
| **Escaping spaces** | ❌ Fails | libass parser doesn't process escapes |
| **URL encoding** | ❌ Fails | libass expects filesystem paths |
| **Temporary directory** | ✅ Works | Path guaranteed to have no spaces |

The `tempfile.mkdtemp()` function creates directories in system temp locations (typically `/tmp/` on Unix-like systems) which are guaranteed not to contain spaces in the path.

**Sources:** [TECHNICAL_NOTES.md:82-163](), [scripts/burn_subtitles.py:200-280]()

---

## Optimization Improvements

### Batch Translation Implementation

#### Performance Analysis

The batch translation optimization addresses API call volume for subtitle translation:

**Before Optimization:**
- 600 subtitle lines in typical 30-minute video
- 1 API call per subtitle line
- **Total: 600 API calls**
- Processing time: ~10 minutes
- API cost: $X per call × 600

**After Optimization:**
- Same 600 subtitle lines
- Batch size: 20-25 lines per call
- **Total: 24-30 API calls**
- Processing time: ~1 minute
- **95% reduction in API calls**
- **90% reduction in processing time**

#### Batch Processing Flow

```mermaid
graph LR
    Subtitles["Subtitle Array<br/>[sub1, sub2, ..., sub600]"]
    
    Batch1["Batch 1<br/>Lines 1-20"]
    Batch2["Batch 2<br/>Lines 21-40"]
    BatchN["Batch N<br/>Lines 581-600"]
    
    API1["Claude API Call 1<br/>Translate 20 lines"]
    API2["Claude API Call 2<br/>Translate 20 lines"]
    APIN["Claude API Call N<br/>Translate 20 lines"]
    
    Result["Translated Subtitles<br/>[trans1, trans2, ..., trans600]"]
    
    Subtitles --> Batch1
    Subtitles --> Batch2
    Subtitles --> BatchN
    
    Batch1 --> API1
    Batch2 --> API2
    BatchN --> APIN
    
    API1 --> Result
    API2 --> Result
    APIN --> Result
```

#### Batch Size Selection

Configuration parameter `TRANSLATION_BATCH_SIZE` controls grouping:

| Batch Size | API Calls (600 lines) | Translation Quality | Recommended |
|------------|----------------------|---------------------|-------------|
| **1** | 600 | ⭐⭐⭐⭐⭐ Excellent | ❌ Too slow |
| **10** | 60 | ⭐⭐⭐⭐⭐ Excellent | ⚠️ Acceptable |
| **20** | 30 | ⭐⭐⭐⭐⭐ Excellent | ✅ **Optimal** |
| **25** | 24 | ⭐⭐⭐⭐ Very Good | ✅ Good |
| **40** | 15 | ⭐⭐⭐ Good | ⚠️ Quality degradation |
| **100** | 6 | ⭐⭐ Fair | ❌ Poor context |

The 20-25 range provides optimal balance between API efficiency and translation quality by maintaining sufficient context while avoiding token limit issues.

#### Implementation Details

The translation batch process:

1. **Group**: Split subtitle array into chunks of `TRANSLATION_BATCH_SIZE` lines
2. **Format**: Combine each batch into numbered text format
3. **Translate**: Single API call with instruction to maintain line-by-line correspondence
4. **Parse**: Extract individual translations from API response
5. **Validate**: Verify translation count matches input count
6. **Assign**: Map translations back to original subtitle objects

**Sources:** [TECHNICAL_NOTES.md:262-305](), [README.md:211-216](), [FIXES_AND_IMPROVEMENTS.md:198-204]()

---

## Configuration File Updates

### Environment Variable Defaults

Several `.env` defaults were updated based on testing results:

| Variable | Old Default | New Default | Reason |
|----------|-------------|-------------|--------|
| `OUTPUT_DIR` | `~/Videos/youtube-clips` | `./youtube-clips` | User expectation for CLI tools |
| `TRANSLATION_BATCH_SIZE` | `1` | `20` | 95% API call reduction |
| `TARGET_CHAPTER_DURATION` | Not set | `180` | Optimal clip length (3 minutes) |
| `KEEP_TEMP_FILES` | `true` | `false` | Disk space management |

**Sources:** [.env.example:1-50](), [scripts/utils.py:131-148]()

---

## Verified Functionality

### Test Video Specifications

Complete workflow tested with:
- **URL**: `https://www.youtube.com/watch?v=Ckt1cj0xjRM`
- **Title**: "Anthropic's Amodei on AI: Power and Risk"
- **Duration**: 25:25
- **Video Size**: 368 MB (1080p)
- **Subtitle Count**: 405 VTT entries (41 KB)

### Successful Operations

```mermaid
graph TB
    subgraph "Stage 1: Acquisition"
        Download["✅ Video Download<br/>368 MB, 1080p, 25:25"]
        SubDown["✅ Subtitle Download<br/>405 entries, VTT format"]
    end
    
    subgraph "Stage 2: AI Analysis"
        Analyze["✅ Semantic Chapter Analysis<br/>10 chapters generated<br/>2-5 minute granularity"]
    end
    
    subgraph "Stage 3: User Selection"
        Select["✅ Chapter Selection<br/>Chapter 2: 02:40-04:40<br/>'Enterprise vs Consumer'"]
    end
    
    subgraph "Stage 4: Processing"
        Clip["✅ Video Clipping<br/>2:00 duration, 29.6 MB"]
        Extract["✅ Subtitle Extraction<br/>35 lines, time-adjusted"]
        Translate["✅ Batch Translation<br/>35 lines in 2 API calls"]
        SRT["✅ Bilingual SRT<br/>English + Chinese"]
    end
    
    subgraph "Stage 5: Output"
        Burn["✅ Subtitle Burning<br/>30.3 MB with hardcoded subs"]
        Summary["✅ Content Generation<br/>Xiaohongshu, Douyin, WeChat"]
    end
    
    Download --> Analyze
    SubDown --> Analyze
    Analyze --> Select
    Select --> Clip
    Select --> Extract
    Extract --> Translate
    Translate --> SRT
    Clip --> Burn
    SRT --> Burn
    Analyze --> Summary
```

All processing stages completed successfully with correct output files generated.

**Sources:** [FIXES_AND_IMPROVEMENTS.md:154-205]()

---

## Documentation Updates

Following the fixes, documentation was updated across multiple files:

1. **SKILL.md**: Updated output directory paths, workflow examples
2. **README.md**: Added troubleshooting section, updated configuration examples
3. **TECHNICAL_NOTES.md**: New document created to capture technical gotchas
4. **FIXES_AND_IMPROVEMENTS.md**: Comprehensive test report and fix documentation

**Sources:** [FIXES_AND_IMPROVEMENTS.md:120-135](), [README.md:236-278]()

---

## Future Enhancement Opportunities

### Identified But Not Yet Implemented

The following enhancements were identified during testing but are not currently prioritized:

#### Automatic Temporary File Cleanup

**Current Behavior**: Intermediate files (original clips, pre-burned videos, extracted subtitles) are retained in output directories.

**Proposed Enhancement**: Add `KEEP_INTERMEDIATE_FILES` configuration option:
- `false` (default): Delete intermediate files after final output generation
- `true`: Retain all intermediate files for debugging

**File Reference**: Would affect [scripts/clip_video.py:100-150](), [scripts/burn_subtitles.py:200-280]()

#### Output Format Selection

**Current Behavior**: Fixed output format is MP4.

**Proposed Enhancement**: Add `OUTPUT_VIDEO_FORMAT` configuration:
- `mp4` (default): H.264 codec, broad compatibility
- `webm`: VP9 codec, smaller file size
- `mkv`: Matroska container, lossless quality

#### Batch Chapter Processing

**Current Behavior**: User selects and processes one chapter at a time.

**Proposed Enhancement**: Allow selection of multiple chapters for parallel processing:
- Checkbox-based multi-selection
- Parallel FFmpeg processes
- Progress tracking per chapter

#### Customizable Subtitle Styling

**Current Behavior**: Fixed font size (24) and margin (30).

**Proposed Enhancement**: Add subtitle style configuration:
```bash
SUBTITLE_FONT_NAME=Arial
SUBTITLE_FONT_SIZE=24
SUBTITLE_PRIMARY_COLOR=&H00FFFFFF  # White
SUBTITLE_OUTLINE_COLOR=&H00000000  # Black
SUBTITLE_MARGIN_V=30
```

**Sources:** [FIXES_AND_IMPROVEMENTS.md:216-237]()

---

## Summary Statistics

### Fixes Applied

| Category | Count | Status |
|----------|-------|--------|
| **Critical Bugs** | 4 | ✅ All resolved |
| **FFmpeg Issues** | 2 | ✅ All resolved |
| **Optimizations** | 2 | ✅ Implemented |
| **Documentation Updates** | 4 files | ✅ Complete |

### Testing Results

| Metric | Value |
|--------|-------|
| **Test Video Duration** | 25:25 |
| **Chapters Generated** | 10 |
| **Chapters Tested** | 1 (representative) |
| **Subtitle Lines Processed** | 35 |
| **API Calls (translation)** | 2 (vs 35 without batching) |
| **Output Files Generated** | 4 per chapter |
| **Success Rate** | 100% |

All core functionality is verified and production-ready. The skill successfully processes YouTube videos from download through final output generation.

**Sources:** [FIXES_AND_IMPROVEMENTS.md:275-293]()

---

# Page: Testing and Verification

# Testing and Verification

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FIXES_AND_IMPROVEMENTS.md](FIXES_AND_IMPROVEMENTS.md)
- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



This document describes the testing workflow, verification procedures, and test data examples for the YouTube Clipper Skill. It covers manual integration testing of the complete processing pipeline, verification of individual components, and documented test results from production runs.

**Scope**: This page focuses on manual integration testing and functional verification. For information about specific bug fixes and improvements, see [9.2 Recent Fixes and Improvements](#9.2). For architectural details about the processing pipeline, see [3.2 Processing Pipeline](#3.2).

---

## Testing Approach

The YouTube Clipper Skill employs **manual integration testing** as its primary verification method. There are currently no automated unit tests or test suites. Testing is performed by executing the complete workflow against real YouTube videos and verifying outputs at each stage.

### Testing Philosophy

| Aspect | Approach |
|--------|----------|
| **Test Type** | End-to-end integration testing |
| **Automation** | Manual execution with real videos |
| **Verification** | Output inspection and functionality checks |
| **Test Data** | Real YouTube videos with various characteristics |
| **Coverage** | All six processing stages from download to output |

The testing methodology relies on the skill's modular architecture, where each Python script can be invoked independently to isolate and verify specific functionality.

Sources: [README.md:88-110](), [SKILL.md:22-280](), [FIXES_AND_IMPROVEMENTS.md:1-293]()

---

## Complete Test Workflow

### Test Execution Flow

```mermaid
flowchart TD
    Start["Start Test"] --> SelectVideo["Select Test Video<br/>(YouTube URL with subtitles)"]
    
    SelectVideo --> Stage1["Stage 1: Environment Detection<br/>yt-dlp --version<br/>ffmpeg -version<br/>python3 -c 'import yt_dlp'"]
    
    Stage1 --> CheckStage1{Environment<br/>Valid?}
    CheckStage1 -->|No| FixEnv["Fix Dependencies"]
    FixEnv --> Stage1
    CheckStage1 -->|Yes| Stage2
    
    Stage2["Stage 2: Video Download<br/>python3 scripts/download_video.py"] --> VerifyFiles["Verify Files:<br/>- video.mp4<br/>- subtitle.vtt"]
    
    VerifyFiles --> Stage3["Stage 3: AI Chapter Analysis<br/>python3 scripts/analyze_subtitles.py<br/>+ Manual Claude Analysis"]
    
    Stage3 --> VerifyChapters["Verify Chapters:<br/>- 2-5 min duration<br/>- Semantic boundaries<br/>- Complete coverage"]
    
    VerifyChapters --> Stage4["Stage 4: User Selection<br/>(Pick chapters to process)"]
    
    Stage4 --> Stage5["Stage 5: Processing<br/>- clip_video.py<br/>- extract_subtitle_clip.py<br/>- Translation<br/>- burn_subtitles.py"]
    
    Stage5 --> Stage6["Stage 6: Output Verification<br/>Check ./youtube-clips/"]
    
    Stage6 --> VerifyOutputs["Verify Each Chapter:<br/>- clip.mp4 exists<br/>- bilingual.srt correct<br/>- with_subtitles.mp4 plays<br/>- summary.md generated"]
    
    VerifyOutputs --> CheckSuccess{All Tests<br/>Pass?}
    CheckSuccess -->|No| LogIssue["Log Issue in<br/>FIXES_AND_IMPROVEMENTS.md"]
    CheckSuccess -->|Yes| Complete["Test Complete"]
    
    LogIssue --> AnalyzeFix["Analyze & Fix"]
    AnalyzeFix --> Stage1
```

Sources: [SKILL.md:22-280](), [FIXES_AND_IMPROVEMENTS.md:153-204]()

---

## Environment Detection Tests

### Verification Commands

The environment detection phase ensures all dependencies are properly installed and configured. This is the first critical verification point.

```mermaid
graph TB
    subgraph "Environment Detection Scripts"
        EnvCheck["Environment Check<br/>(Manual bash commands)"]
    end
    
    subgraph "System Dependencies"
        YtDlp["yt-dlp<br/>yt-dlp --version"]
        FFmpeg["FFmpeg with libass<br/>ffmpeg -version<br/>ffmpeg -filters | grep subtitles"]
        Python["Python 3.8+<br/>python3 --version"]
    end
    
    subgraph "Python Packages"
        YtDlpLib["yt_dlp module<br/>import yt_dlp"]
        Pysrt["pysrt module<br/>import pysrt"]
        DotEnv["python-dotenv module<br/>import dotenv"]
    end
    
    EnvCheck --> YtDlp
    EnvCheck --> FFmpeg
    EnvCheck --> Python
    
    Python --> YtDlpLib
    Python --> Pysrt
    Python --> DotEnv
    
    YtDlp -.->|Required| Download[download_video.py]
    FFmpeg -.->|Required| Clip[clip_video.py]
    FFmpeg -.->|Required| Burn[burn_subtitles.py]
    YtDlpLib -.->|Required| Download
    Pysrt -.->|Required| Extract[extract_subtitle_clip.py]
```

### Test Commands

| Component | Verification Command | Expected Output |
|-----------|---------------------|-----------------|
| **yt-dlp** | `yt-dlp --version` | Version number (e.g., `2024.12.23`) |
| **FFmpeg** | `ffmpeg -version` | Version with configuration details |
| **libass Support** | `ffmpeg -filters 2>&1 \| grep subtitles` | `subtitles    V->V  (...)` |
| **Python yt_dlp** | `python3 -c "import yt_dlp; print('✅')"` | `✅` |
| **Python pysrt** | `python3 -c "import pysrt; print('✅')"` | `✅` |
| **Python dotenv** | `python3 -c "import dotenv; print('✅')"` | `✅` |

### Critical: FFmpeg libass Detection

The `burn_subtitles.py` script requires FFmpeg with libass support. The detection logic checks multiple FFmpeg variants:

1. **ffmpeg-full** (macOS): `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`
2. **Standard ffmpeg**: System PATH lookup

Test command: `ffmpeg -filters 2>&1 | grep subtitles`

If this fails, subtitle burning will not work. See [5.3 libass Requirement](#5.3) for installation instructions.

Sources: [SKILL.md:25-63](), [README.md:50-84](), [FIXES_AND_IMPROVEMENTS.md:7-25]()

---

## Download Functionality Tests

### Test Script: download_video.py

```mermaid
graph LR
    Input["YouTube URL"] --> Script["download_video.py"]
    
    Script --> YtDlpCall["yt_dlp.YoutubeDL"]
    
    YtDlpCall --> VideoFile["OUTPUT: video_id.mp4"]
    YtDlpCall --> SubFile["OUTPUT: video_id.en.vtt"]
    
    Script --> Progress["_progress_hook<br/>(download_video.py:156-178)"]
    
    Progress --> Display["Display Progress:<br/>- Downloaded bytes<br/>- Total bytes<br/>- Speed<br/>- ETA"]
    
    VideoFile -.->|Check| Exists1{File exists?}
    SubFile -.->|Check| Exists2{File exists?}
    
    Exists1 -->|Yes| CheckSize1["Verify size > 0"]
    Exists2 -->|Yes| CheckSize2["Verify size > 0"]
```

### Verification Checklist

**Pre-conditions:**
- Valid YouTube URL with available video
- Network connectivity
- Sufficient disk space

**Test Execution:**
```bash
cd ~/.claude/skills/youtube-clipper
python3 scripts/download_video.py "https://youtube.com/watch?v=VIDEO_ID"
```

**Expected Outputs:**

| File | Format | Typical Size | Verification |
|------|--------|--------------|--------------|
| `VIDEO_ID.mp4` | MP4 video | 100-500 MB (for 20-30 min video at 1080p) | Play file, check duration |
| `VIDEO_ID.en.vtt` | WebVTT subtitles | 20-50 KB | Open in text editor, verify timestamps |

**Known Issues Fixed:**

1. **Progress Hook Division Error** [download_video.py:156-178]()
   - Issue: `TypeError` when `total_bytes` is `None`
   - Fix: Added null check: `if d['total_bytes'] and d['total_bytes']:`
   - Test: Download video and verify progress display doesn't crash

2. **Filename Special Characters** [download_video.py:67]()
   - Issue: Video titles contain `:`, `'`, `/` causing path errors
   - Fix: Changed output template from `%(title)s [%(id)s]` to `%(id)s`
   - Test: Download video with special characters in title, verify filename is clean

Sources: [FIXES_AND_IMPROVEMENTS.md:28-93](), [README.md:86-110]()

---

## AI Chapter Analysis Verification

### Analysis Components

```mermaid
graph TB
    subgraph "Input Processing"
        VTT["video_id.en.vtt<br/>(WebVTT format)"]
        Parser["analyze_subtitles.py<br/>Parse VTT"]
        
        VTT --> Parser
        Parser --> SubData["Structured Subtitle Data<br/>- Timestamps<br/>- Text content<br/>- Total duration"]
    end
    
    subgraph "AI Analysis (Manual)"
        SubData --> Read["Read Complete Subtitles"]
        Read --> Understand["Understand Semantics<br/>- Identify topics<br/>- Find transitions<br/>- Recognize boundaries"]
        
        Understand --> Generate["Generate Chapters<br/>- Title (10-20 chars)<br/>- Time range<br/>- Summary (50-100 chars)<br/>- Keywords (3-5)"]
    end
    
    subgraph "Validation"
        Generate --> Check1["Check Duration<br/>(2-5 minutes each)"]
        Generate --> Check2["Check Coverage<br/>(No gaps)"]
        Generate --> Check3["Check Semantics<br/>(Meaningful boundaries)"]
    end
    
    Check1 --> Output["Chapter List JSON"]
    Check2 --> Output
    Check3 --> Output
```

### Test Data: Actual Analysis Results

From the documented test run using `https://youtube.com/watch?v=Ckt1cj0xjRM`:

**Video Info:**
- Title: "Anthropic's Amodei on AI: Power and Risk"
- Duration: 25:25
- Subtitles: 405 VTT entries

**Generated Chapters (10 total):**

| # | Time Range | Duration | Title | Verification |
|---|------------|----------|-------|--------------|
| 1 | 00:00 - 02:40 | 2:40 | AI 竞赛不是赛跑，是不同方向 | ✅ Semantic boundary |
| 2 | 02:40 - 04:40 | 2:00 | 企业 vs 消费者：战略选择 | ✅ Topic transition |
| 3 | 04:40 - 07:20 | 2:40 | AI 泡沫？投资回报需要时间 | ✅ Coherent discussion |
| 4 | 07:20 - 10:00 | 2:40 | 就业影响：不会大规模失业 | ✅ New topic |
| 5 | 10:00 - 12:30 | 2:30 | 税收与 UBI：解决分配问题 | ✅ Policy shift |
| 6 | 12:30 - 15:00 | 2:30 | 安全风险：生物武器与网络攻击 | ✅ Risk discussion |
| 7 | 15:00 - 18:00 | 3:00 | 国际合作与中国竞争 | ✅ Geopolitics |
| 8 | 18:00 - 21:00 | 3:00 | 模型能力评估与安全测试 | ✅ Technical details |
| 9 | 21:00 - 23:30 | 2:30 | Claude 的特点与应用场景 | ✅ Product focus |
| 10 | 23:30 - 25:25 | 1:55 | 未来展望与结语 | ✅ Conclusion |

**Validation Results:**
- ✅ Duration range: All chapters 1:55 - 3:00 (within 2-5 minute target)
- ✅ Complete coverage: 00:00 - 25:25 (no gaps)
- ✅ Semantic boundaries: Each chapter represents coherent topic
- ✅ No mechanical splitting: Not divided by fixed time intervals

### Quality Criteria

**Good Chapter Analysis:**
```
✅ [02:40 - 04:40] 企业 vs 消费者：战略选择
   Summary: Anthropic 选择企业市场而非消费者，避免直接竞争
   Keywords: 战略, 企业市场, 差异化
```

**Poor Chapter Analysis (mechanical splitting):**
```
❌ [00:00 - 30:00] First half of video
   Summary: Various topics discussed
   Keywords: AI, technology
```

Sources: [FIXES_AND_IMPROVEMENTS.md:167-204](), [SKILL.md:96-144]()

---

## Video Clipping Accuracy Tests

### Test Script: clip_video.py

```mermaid
graph LR
    subgraph "Inputs"
        Video["video_id.mp4"]
        Start["start_time<br/>(seconds)"]
        End["end_time<br/>(seconds)"]
    end
    
    subgraph "clip_video.py"
        ValidateTime["validate_time_format<br/>(utils.py:54-84)"]
        FFmpegCmd["FFmpeg Command<br/>-ss START -t DURATION<br/>-c copy"]
    end
    
    subgraph "Verification"
        ClipOut["chapter_clip.mp4"]
        CheckDur["ffprobe -show_entries<br/>format=duration"]
        CheckQual["Visual inspection<br/>Stream copy = lossless"]
    end
    
    Video --> ValidateTime
    Start --> ValidateTime
    End --> ValidateTime
    
    ValidateTime --> FFmpegCmd
    FFmpegCmd --> ClipOut
    
    ClipOut --> CheckDur
    ClipOut --> CheckQual
```

### Test Execution Example

**Test Case:** Extract chapter 2 from test video

```bash
# Input parameters
VIDEO_PATH="/path/to/Ckt1cj0xjRM.mp4"
START_TIME=160  # 02:40 in seconds
END_TIME=280    # 04:40 in seconds
OUTPUT_PATH="./chapter2_clip.mp4"

# Execute clipping
python3 scripts/clip_video.py "$VIDEO_PATH" "$START_TIME" "$END_TIME" "$OUTPUT_PATH"
```

**Expected Results:**

| Metric | Expected Value | Verification Method |
|--------|---------------|---------------------|
| **Duration** | 120 seconds (2:00) | `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 chapter2_clip.mp4` |
| **File Size** | ~29.6 MB (for 1080p) | `ls -lh chapter2_clip.mp4` |
| **Quality** | Identical to source | Stream copy (`-c copy` flag) |
| **Start Frame** | Matches 02:40 timestamp | Visual verification |
| **End Frame** | Matches 04:40 timestamp | Visual verification |

**Actual Test Results (from documented run):**
- Input video: 368 MB, 25:25 duration
- Clip output: 29.6 MB, 2:00 duration
- Quality: Lossless (stream copy)
- Accuracy: ✅ Exact frame-level precision

### FFmpeg Command Verification

The script uses `ffmpeg -ss START_TIME -t DURATION -c copy` for optimal performance:
- `-ss`: Seek to start time (fast seek before decoding)
- `-t`: Duration to extract
- `-c copy`: Stream copy (no re-encoding, preserves quality)

Sources: [FIXES_AND_IMPROVEMENTS.md:175-179]()

---

## Subtitle Processing Tests

### Subtitle Extraction and Time Adjustment

```mermaid
graph TB
    subgraph "extract_subtitle_clip.py"
        Input["Full VTT Subtitle<br/>(405 entries)"]
        Parse["pysrt.open()<br/>Parse SRT format"]
        
        Input --> Convert["VTT to SRT conversion<br/>(utils.py)"]
        Convert --> Parse
        
        Parse --> Filter["Filter by time range<br/>start_time <= entry <= end_time"]
        
        Filter --> Adjust["Adjust timestamps<br/>new_time = old_time - start_time"]
        
        Adjust --> Output["Segment SRT<br/>(35 entries)<br/>Starting at 00:00:00"]
    end
    
    subgraph "Translation"
        Output --> Batch["Batch Translation<br/>(20-25 lines per API call)"]
        Batch --> Translated["Chinese Translation<br/>(35 entries)"]
    end
    
    subgraph "Bilingual Generation"
        Output --> EN["English Lines"]
        Translated --> CN["Chinese Lines"]
        
        EN --> Merge["Merge Bilingual SRT<br/>EN line<br/>CN line<br/>(empty line)"]
        CN --> Merge
        
        Merge --> BilingualOut["chapter_bilingual.srt"]
    end
```

### Test Case: Chapter 2 Subtitle Extraction

**Input:**
- Full subtitle: 405 VTT entries (00:00 - 25:25)
- Chapter time range: 02:40 - 04:40 (160s - 280s)

**Execution:**
```bash
python3 scripts/extract_subtitle_clip.py \
  "Ckt1cj0xjRM.en.vtt" \
  160 \
  280 \
  "chapter2_original_en.srt"
```

**Expected Output:**

| Metric | Value |
|--------|-------|
| **Entries Extracted** | 33-35 entries |
| **Time Range** | 00:00:00 - 00:02:00 (adjusted from 02:40-04:40) |
| **Format** | SRT with proper timestamps |
| **Encoding** | UTF-8 |

**Verification Commands:**
```bash
# Count subtitle entries
grep -c "^[0-9]\+$" chapter2_original_en.srt

# Check first timestamp (should be near 00:00:00)
head -n 3 chapter2_original_en.srt

# Check last timestamp (should be near 00:02:00)
tail -n 4 chapter2_original_en.srt
```

### Batch Translation Test

**Optimization Strategy:**
- Group 20-25 subtitle lines per API call
- Reduces API calls by 95% compared to line-by-line translation
- Example: 35 entries = 2 API calls instead of 35

**Test Results (from documented run):**
- Input: 35 English subtitle entries
- API calls: 2 batches
- Output: 35 Chinese translations
- Quality: ✅ Context-aware, consistent terminology

**Bilingual Format Example:**
```srt
1
00:00:00,000 --> 00:00:03,500
This is the English subtitle
这是中文字幕

2
00:00:03,500 --> 00:00:07,000
Another English line
另一行中文
```

Sources: [FIXES_AND_IMPROVEMENTS.md:180-185](), [README.md:211-233]()

---

## Subtitle Burning Tests

### Test Script: burn_subtitles.py

```mermaid
graph TB
    subgraph "Input Validation"
        Video["chapter_clip.mp4"]
        SRT["chapter_bilingual.srt"]
        FFmpegPath["FFmpeg with libass<br/>(burn_subtitles.py:30-54)"]
    end
    
    subgraph "Path Handling"
        CheckSpaces["Check for spaces in paths<br/>(burn_subtitles.py:80-90)"]
        
        CheckSpaces -->|Has Spaces| TempDir["Create temp directory<br/>/tmp/ffmpeg_RANDOM"]
        CheckSpaces -->|No Spaces| DirectExec["Execute directly"]
        
        TempDir --> CopyFiles["Copy video & SRT<br/>to temp dir"]
        CopyFiles --> FFmpegTemp["FFmpeg in temp dir<br/>No path spaces"]
        FFmpegTemp --> MoveBack["Move output back"]
    end
    
    subgraph "FFmpeg Execution"
        DirectExec --> FFmpegDirect["ffmpeg -i video -vf subtitles=file"]
        FFmpegTemp --> SubFilter["subtitles filter<br/>FontSize=24<br/>MarginV=30"]
        FFmpegDirect --> SubFilter
        
        SubFilter --> Encode["H.264 encode<br/>AAC audio"]
    end
    
    Video --> CheckSpaces
    SRT --> CheckSpaces
    FFmpegPath --> CheckSpaces
    
    Encode --> Output["chapter_with_subtitles.mp4"]
```

### Critical: Temporary Directory Workaround

The `burn_subtitles.py` script implements a workaround for FFmpeg's inability to handle spaces in subtitle file paths when using the `subtitles` filter.

**Issue:** FFmpeg command fails when subtitle path contains spaces:
```bash
# Fails with path like "/my folder/subtitle.srt"
ffmpeg -i video.mp4 -vf "subtitles='/my folder/subtitle.srt'" output.mp4
```

**Solution:** [burn_subtitles.py:80-120]()
1. Detect spaces in video or subtitle paths
2. Create temporary directory with no spaces: `/tmp/ffmpeg_XXXXXX/`
3. Copy files to temp directory
4. Execute FFmpeg in temp directory
5. Move output back to original location
6. Clean up temp directory

**Test Verification:**
```bash
# Test with spaces in path
mkdir "test folder"
python3 scripts/burn_subtitles.py \
  "test folder/video.mp4" \
  "test folder/subtitle.srt" \
  "test folder/output.mp4"

# Verify output exists and plays correctly
ffplay "test folder/output.mp4"
```

### Subtitle Style Verification

**Default Style Parameters:**
- Font Size: 24 (configurable via `.env`: `SUBTITLE_FONT_SIZE`)
- Vertical Margin: 30 (configurable via `.env`: `SUBTITLE_MARGIN_V`)
- Colors: White text with black outline (default libass style)

**Visual Verification Checklist:**
- [ ] Subtitles visible at bottom of video
- [ ] English text readable (top line)
- [ ] Chinese text readable (bottom line)
- [ ] Proper spacing between lines
- [ ] No overlap with video content
- [ ] Synchronized with audio

**Test Results (from documented run):**
- Input: 29.6 MB clip, 35 bilingual subtitle entries
- Output: 30.3 MB with hardcoded subtitles (+0.7 MB)
- Quality: ✅ Clear, readable, properly positioned

Sources: [FIXES_AND_IMPROVEMENTS.md:186-190](), [SKILL.md:202-213]()

---

## Output Organization Tests

### File Structure Verification

```mermaid
graph TB
    subgraph "Output Directory Structure"
        Root["./youtube-clips/"]
        Session["YYYYMMDD_HHMMSS/<br/>(Timestamp directory)"]
        
        Root --> Session
        
        Session --> Chapter1["Chapter_Title_1/"]
        Session --> Chapter2["Chapter_Title_2/"]
        
        Chapter1 --> Files1["Output Files"]
        
        subgraph "Per-Chapter Files"
            Files1 --> Clip1["Chapter_Title_clip.mp4<br/>(Original, no subtitles)"]
            Files1 --> Burned1["Chapter_Title_with_subtitles.mp4<br/>(Hardcoded subtitles)"]
            Files1 --> SRT1["Chapter_Title_bilingual.srt<br/>(Subtitle file)"]
            Files1 --> Summary1["Chapter_Title_summary.md<br/>(Social media content)"]
        end
    end
    
    subgraph "Filename Sanitization"
        Raw["Raw Chapter Title<br/>(may contain : / \\ etc)"]
        Sanitize["sanitize_filename()<br/>(utils.py:20-52)"]
        Clean["Clean Filename<br/>(underscores, max 100 chars)"]
        
        Raw --> Sanitize
        Sanitize --> Clean
        Clean -.-> Clip1
        Clean -.-> Burned1
        Clean -.-> SRT1
        Clean -.-> Summary1
    end
```

### Test Execution

**Setup Test Output:**
```bash
cd /path/to/test/directory
# Run skill - output should appear here
```

**Expected Directory Structure:**
```
./youtube-clips/
└── 20260121_143022/
    ├── AGI_指数曲线/
    │   ├── AGI_指数曲线_clip.mp4
    │   ├── AGI_指数曲线_with_subtitles.mp4
    │   ├── AGI_指数曲线_bilingual.srt
    │   └── AGI_指数曲线_summary.md
    └── 企业vs消费者/
        ├── 企业vs消费者_clip.mp4
        ├── 企业vs消费者_with_subtitles.mp4
        ├── 企业vs消费者_bilingual.srt
        └── 企业vs消费者_summary.md
```

### Verification Script

```bash
#!/bin/bash
# verify_output.sh - Check output structure

OUTPUT_DIR="./youtube-clips"

# Check base directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ Output directory not found"
    exit 1
fi

# Find latest session directory
LATEST_SESSION=$(ls -t "$OUTPUT_DIR" | head -n 1)
SESSION_DIR="$OUTPUT_DIR/$LATEST_SESSION"

echo "Checking session: $LATEST_SESSION"

# Count chapter directories
CHAPTER_COUNT=$(find "$SESSION_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "Chapters found: $CHAPTER_COUNT"

# For each chapter directory
for CHAPTER_DIR in "$SESSION_DIR"/*/; do
    CHAPTER_NAME=$(basename "$CHAPTER_DIR")
    echo "Verifying chapter: $CHAPTER_NAME"
    
    # Check required files
    [ -f "$CHAPTER_DIR"/*_clip.mp4 ] && echo "  ✅ clip.mp4" || echo "  ❌ clip.mp4 missing"
    [ -f "$CHAPTER_DIR"/*_with_subtitles.mp4 ] && echo "  ✅ with_subtitles.mp4" || echo "  ❌ with_subtitles.mp4 missing"
    [ -f "$CHAPTER_DIR"/*_bilingual.srt ] && echo "  ✅ bilingual.srt" || echo "  ❌ bilingual.srt missing"
    [ -f "$CHAPTER_DIR"/*_summary.md ] && echo "  ✅ summary.md" || echo "  ❌ summary.md missing"
done
```

### Filename Sanitization Tests

The `sanitize_filename()` function [utils.py:20-52]() removes problematic characters:

| Input | Output | Reason |
|-------|--------|--------|
| `AI: Power & Risk` | `AI_Power_Risk` | Removed `:`, `&` |
| `企业 vs 消费者` | `企业_vs_消费者` | Spaces to underscores |
| `Very Long Title That Exceeds...` | `Very_Long_Title_That_Exceeds_...` | Truncated to 100 chars |
| `Question?` | `Question` | Removed `?` |
| `Path/With/Slashes` | `PathWithSlashes` | Removed `/` |

**Test Command:**
```python
from utils import sanitize_filename

test_cases = [
    "AI: Power & Risk",
    "企业 vs 消费者",
    "Question?",
    "Very Long Title " * 10  # Over 100 chars
]

for case in test_cases:
    print(f"{case} -> {sanitize_filename(case)}")
```

Sources: [FIXES_AND_IMPROVEMENTS.md:96-134](), [README.md:270-278]()

---

## Documented Test Run Results

### Complete Test Execution

The following results are from a complete documented test run performed on 2026-01-21.

**Test Video:** `https://www.youtube.com/watch?v=Ckt1cj0xjRM`

### Input Video Characteristics

| Attribute | Value |
|-----------|-------|
| **Title** | Anthropic's Amodei on AI: Power and Risk |
| **Duration** | 25:25 |
| **Video Size** | 368 MB (1080p) |
| **Subtitle Size** | 41 KB (VTT) |
| **Subtitle Entries** | 405 entries |
| **Language** | English |

### Processing Results

**Stage 1: Environment Detection** ✅
- yt-dlp: Available
- FFmpeg with libass: Confirmed
- Python packages: Installed

**Stage 2: Video Download** ✅
- Download time: ~2-3 minutes (varies by network)
- Video file: `Ckt1cj0xjRM.mp4` (368 MB)
- Subtitle file: `Ckt1cj0xjRM.en.vtt` (41 KB)

**Stage 3: AI Chapter Analysis** ✅
- Generated: 10 semantic chapters
- Duration range: 1:55 - 3:00 per chapter
- Coverage: Complete (00:00 - 25:25)
- Quality: Meaningful topic boundaries

**Stage 4: User Selection** ✅
- Selected: Chapter 2 ("企业 vs 消费者")
- Time range: 02:40 - 04:40
- Options: All enabled (clip, translate, burn, summary)

**Stage 5: Processing** ✅

| Task | Status | Details |
|------|--------|---------|
| Video clipping | ✅ | 29.6 MB, 2:00 duration |
| Subtitle extraction | ✅ | 35 entries, timestamps adjusted |
| Translation | ✅ | 35 lines, 2 API calls (batched) |
| Bilingual SRT | ✅ | English + Chinese format |
| Subtitle burning | ✅ | 30.3 MB output, clear rendering |
| Summary generation | ✅ | 7.5 KB markdown file |

**Stage 6: Output Organization** ✅
- Directory: `./youtube-clips/20260121_143022/`
- Chapter folder: `企业vs消费者/`
- Files generated: 4 (clip, burned, srt, summary)

### File Size Verification

```
./youtube-clips/20260121_143022/企业vs消费者/
├── 企业vs消费者_clip.mp4              29.6 MB
├── 企业vs消费者_with_subtitles.mp4   30.3 MB
├── 企业vs消费者_bilingual.srt        2.3 KB
└── 企业vs消费者_summary.md           7.5 KB
```

**Total processing time:** ~8-10 minutes (including download)

Sources: [FIXES_AND_IMPROVEMENTS.md:240-272](), [FIXES_AND_IMPROVEMENTS.md:153-204]()

---

## Functional Verification Checklist

### Pre-Test Setup

- [ ] Python 3.8+ installed
- [ ] yt-dlp available (`yt-dlp --version`)
- [ ] FFmpeg with libass (`ffmpeg -filters | grep subtitles`)
- [ ] Python packages installed (`pip list | grep -E 'yt-dlp|pysrt|dotenv'`)
- [ ] Skill installed at `~/.claude/skills/youtube-clipper/`
- [ ] `.env` file configured (if custom settings needed)

### Stage-by-Stage Verification

**Stage 1: Environment Detection**
- [ ] yt-dlp command executes without error
- [ ] FFmpeg version displays
- [ ] libass support detected (`subtitles` filter found)
- [ ] Python imports succeed (yt_dlp, pysrt, dotenv)

**Stage 2: Video Download**
- [ ] Download starts without errors
- [ ] Progress display updates correctly
- [ ] Video file created with expected size
- [ ] Subtitle file created (VTT format)
- [ ] Files named using video ID (no special characters)

**Stage 3: AI Chapter Analysis**
- [ ] Subtitle parsing succeeds
- [ ] Total duration calculated correctly
- [ ] Chapter count is reasonable (typically 5-15 for 20-30 min video)
- [ ] Each chapter duration is 2-5 minutes
- [ ] No time gaps between chapters
- [ ] Chapter titles are descriptive and concise
- [ ] Summaries capture main topic

**Stage 4: User Selection**
- [ ] Chapter list displays clearly
- [ ] User can select chapters
- [ ] Processing options presented
- [ ] Confirmation shows selected chapters and options

**Stage 5: Processing**

*For each selected chapter:*

- [ ] Video clipping completes
  - [ ] Output file exists
  - [ ] Duration matches chapter length
  - [ ] File size is reasonable
  - [ ] Video plays without errors
  
- [ ] Subtitle extraction completes
  - [ ] Entry count is reasonable
  - [ ] First timestamp near 00:00:00
  - [ ] Last timestamp matches chapter duration
  
- [ ] Translation completes (if selected)
  - [ ] All entries translated
  - [ ] Chinese text is readable
  - [ ] Context is preserved
  
- [ ] Bilingual SRT generated (if selected)
  - [ ] Format is correct (EN line, CN line, blank)
  - [ ] File opens in media player
  
- [ ] Subtitle burning completes (if selected)
  - [ ] Output file exists
  - [ ] File size slightly larger than clip
  - [ ] Subtitles visible when playing
  - [ ] Both English and Chinese readable
  - [ ] Proper positioning (bottom of frame)
  
- [ ] Summary generated (if selected)
  - [ ] Markdown file created
  - [ ] Contains multiple platform versions
  - [ ] Text is coherent and relevant

**Stage 6: Output Organization**
- [ ] Output directory created in working directory (`./youtube-clips/`)
- [ ] Timestamp directory named correctly (`YYYYMMDD_HHMMSS`)
- [ ] Chapter directories created with sanitized names
- [ ] All expected files present in each chapter directory
- [ ] Filenames use consistent naming convention
- [ ] No special characters in filenames

### Quality Verification

**Video Quality:**
- [ ] Clip quality identical to source (stream copy)
- [ ] Burned subtitle version maintains quality
- [ ] No audio sync issues
- [ ] No visual artifacts

**Subtitle Quality:**
- [ ] Timestamps accurate
- [ ] Translation natural and contextual
- [ ] Bilingual format readable
- [ ] Burned subtitles legible at various screen sizes

**Chapter Quality:**
- [ ] Semantic boundaries (not mechanical time splits)
- [ ] Complete coverage of selected time ranges
- [ ] Meaningful titles and summaries
- [ ] Appropriate granularity (2-5 min)

Sources: [SKILL.md:22-280](), [FIXES_AND_IMPROVEMENTS.md:275-293]()

---

## Common Test Failures and Diagnostics

### Download Stage Failures

**Symptom:** `ModuleNotFoundError: No module named 'yt_dlp'`

**Diagnosis:**
```bash
python3 -c "import yt_dlp"
```

**Fix:**
```bash
pip3 install --break-system-packages yt-dlp pysrt python-dotenv
```

**Symptom:** `TypeError: unsupported operand type(s) for /: 'int' and 'NoneType'`

**Diagnosis:** Progress hook crash in [download_video.py:156-178]()

**Fix:** Already fixed in current version - check for null `total_bytes` before division

**Symptom:** Filename contains special characters causing errors

**Diagnosis:** Check downloaded filename for `:`, `'`, `/`, etc.

**Fix:** Already fixed - uses video ID for filename [download_video.py:67]()

### Subtitle Burning Failures

**Symptom:** `Option not found: subtitles` or `filter not found`

**Diagnosis:**
```bash
ffmpeg -filters 2>&1 | grep subtitles
# If no output, libass not available
```

**Fix:**
```bash
# macOS
brew uninstall ffmpeg
brew install ffmpeg-full

# Ubuntu
sudo apt install ffmpeg libass-dev
```

**Symptom:** Subtitle file path error with spaces

**Diagnosis:** FFmpeg fails with message about subtitle path

**Fix:** Already implemented - temporary directory workaround in [burn_subtitles.py:80-120]()

### Output Location Issues

**Symptom:** Output directory not in expected location

**Diagnosis:** Check where `./youtube-clips/` was created

**Fix:** Ensure you're in the correct working directory when running the skill. Output is relative to current directory, not user home.

### Translation Failures

**Symptom:** API timeout or rate limiting

**Diagnosis:** Check network connectivity and Claude API status

**Fix:**
- Retry processing (automatic retry up to 3 times)
- Reduce batch size in `.env`: `TRANSLATION_BATCH_SIZE=15`
- Check for Claude API outages

Sources: [FIXES_AND_IMPROVEMENTS.md:7-93](), [README.md:236-278]()

---

## Test Data Repository

### Recommended Test Videos

For comprehensive testing, use videos with these characteristics:

| Characteristic | Recommendation | Reason |
|----------------|----------------|---------|
| **Duration** | 20-30 minutes | Tests chapter granularity |
| **Subtitles** | English available | Required for analysis |
| **Content** | Interview or lecture | Multiple distinct topics |
| **Title** | Contains special characters | Tests filename sanitization |
| **Quality** | 1080p available | Tests quality preservation |

**Known Good Test Video:**
- URL: `https://youtube.com/watch?v=Ckt1cj0xjRM`
- Characteristics: 25:25 duration, interview format, technical content, generates 10 semantic chapters

### Test Matrix

| Test Case | Video Type | Expected Chapters | Special Considerations |
|-----------|------------|-------------------|------------------------|
| **Short video** | 5-10 min | 2-4 | Edge case for chapter generation |
| **Medium video** | 20-30 min | 8-12 | Ideal test case |
| **Long video** | 60+ min | 20-30 | Stress test, large file sizes |
| **No subtitles** | Any | N/A | Should fail gracefully |
| **Auto-generated subs** | Any | Varies | Lower quality transcription |
| **Special characters** | Title with `:/?*` | Any | Tests sanitization |

### Performance Benchmarks

Based on test video (368 MB, 25:25 duration, 1080p):

| Stage | Time | Notes |
|-------|------|-------|
| **Download** | 2-3 min | Network dependent |
| **Analysis** | 30-60 sec | Claude API call |
| **Clipping** (per chapter) | 5-10 sec | FFmpeg stream copy |
| **Translation** (35 lines) | 10-20 sec | 2 API calls (batched) |
| **Burning** (2 min clip) | 30-45 sec | H.264 re-encoding |
| **Summary** | 15-30 sec | Claude API call |

**Total for 1 chapter:** ~5-7 minutes (including download)

Sources: [FIXES_AND_IMPROVEMENTS.md:240-272]()

---

## Integration with Claude Code

### Test Invocation

When testing within Claude Code, the skill is invoked through natural language:

```
Clip this YouTube video: https://youtube.com/watch?v=VIDEO_ID
```

or

```
剪辑这个 YouTube 视频：https://youtube.com/watch?v=VIDEO_ID
```

### Expected Tool Usage

During execution, Claude Code will use these tools:

```mermaid
graph LR
    User["User Input:<br/>YouTube URL"] --> Claude["Claude Code<br/>Skill Orchestration"]
    
    Claude --> Bash["Bash Tool<br/>- Run Python scripts<br/>- Check dependencies<br/>- Execute FFmpeg"]
    
    Claude --> Read["Read Tool<br/>- Read .env config<br/>- Read subtitle files<br/>- Read script outputs"]
    
    Claude --> Write["Write Tool<br/>- Create output dirs<br/>- Write SRT files<br/>- Write summaries"]
    
    Claude --> Glob["Glob Tool<br/>- Find video files<br/>- Locate subtitles<br/>- Check outputs"]
    
    Claude --> Ask["AskUserQuestion Tool<br/>- Select chapters<br/>- Choose options<br/>- Confirm actions"]
    
    Bash --> Scripts["Python Scripts<br/>download_video.py<br/>analyze_subtitles.py<br/>clip_video.py<br/>burn_subtitles.py<br/>extract_subtitle_clip.py"]
```

### Verification of Tool Permissions

The skill requires these tools as specified in [SKILL.md:8-13]():

```yaml
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
```

**Test:** Ensure Claude Code doesn't request additional tool permissions during execution.

Sources: [SKILL.md:1-20](), [README.md:88-102]()

---

## Continuous Verification

### Post-Fix Verification

After any code changes, re-run the complete test workflow:

1. Select a known test video (e.g., `Ckt1cj0xjRM`)
2. Execute all six stages
3. Compare outputs to documented test results
4. Verify no regressions in:
   - File naming
   - Output location
   - Progress display
   - Subtitle burning
   - File organization

### Regression Test Checklist

- [ ] Download progress displays without crashes
- [ ] Filenames use video ID (no special characters)
- [ ] Output directory is `./youtube-clips/` (relative to working dir)
- [ ] Subtitle burning works with spaces in paths
- [ ] All four output files generated per chapter
- [ ] Bilingual SRT format is correct
- [ ] Summary markdown is well-formatted

### Documentation Updates

When tests reveal issues or new patterns:

1. Document the issue in `FIXES_AND_IMPROVEMENTS.md`
2. Include reproduction steps
3. Document the fix with file references
4. Update this testing guide if verification steps change

Sources: [FIXES_AND_IMPROVEMENTS.md:1-293]()

---

# Page: License and Contributing

# License and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/REPOSITORY_SETTINGS.md](.github/REPOSITORY_SETTINGS.md)
- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This page provides information about the project's license terms and guidelines for contributing to the YouTube Clipper Skill codebase. It covers the MIT License details, contribution workflow, development setup for contributors, and the process for submitting issues and pull requests.

For information about the project structure and file organization, see [Project Structure](#9.1). For testing procedures, see [Testing and Verification](#9.3).

---

## License Information

The YouTube Clipper Skill is released under the **MIT License**, a permissive open-source license that allows free use, modification, and distribution of the software.

### License Terms

The full license text is located in [LICENSE:1-22]().

| **Permission** | **Details** |
|----------------|-------------|
| **Use** | Commercial and private use permitted |
| **Modify** | Modification and derivative works permitted |
| **Distribute** | Distribution of original or modified versions permitted |
| **Sublicense** | Sublicensing permitted |
| **Liability** | No warranty provided; use at your own risk |

### Copyright

**Copyright (c) 2026 op7418**

The copyright notice and permission notice must be included in all copies or substantial portions of the software, as specified in [LICENSE:7-11]().

### License Display

The license is displayed in the README with a badge:

```markdown
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
```

This badge appears at [README.md:5]().

**Sources:** [LICENSE:1-22](), [README.md:5]()

---

## Contributing Overview

Contributions to the YouTube Clipper Skill are welcome and encouraged. The project accepts various forms of contributions as outlined in [README.md:290-295]().

### Contribution Types

```mermaid
graph TB
    Contrib["Contribution Entry Points"]
    
    Contrib --> BugReport["Bug Reports<br/>GitHub Issues"]
    Contrib --> Feature["Feature Requests<br/>GitHub Issues"]
    Contrib --> Code["Code Contributions<br/>Pull Requests"]
    Contrib --> Docs["Documentation<br/>Pull Requests"]
    
    BugReport --> IssueTemplate["Issue Creation"]
    Feature --> IssueTemplate
    
    Code --> Fork["Fork Repository"]
    Docs --> Fork
    
    Fork --> DevSetup["Development Setup<br/>install_as_skill.sh"]
    DevSetup --> Changes["Make Changes<br/>scripts/"]
    Changes --> Test["Test Changes<br/>Local Verification"]
    Test --> PR["Submit Pull Request"]
    
    IssueTemplate --> Discussion["Community Discussion"]
    Discussion --> Implementation["Implementation"]
    Implementation --> Fork
    
    PR --> Review["Code Review"]
    Review --> Merge["Merge to Main"]
```

**Sources:** [README.md:290-295]()

---

## Reporting Issues

Issues are tracked on GitHub at the project repository. Both bug reports and feature requests follow the same submission process.

### Bug Report Guidelines

When reporting a bug, include the following information:

| **Field** | **Description** | **Example** |
|-----------|-----------------|-------------|
| **Environment** | Operating system, Python version, FFmpeg version | macOS 14.0, Python 3.10, FFmpeg 6.0 |
| **Steps to Reproduce** | Exact commands or actions that trigger the bug | Ran `clip video: URL` with specific video ID |
| **Expected Behavior** | What should have happened | Video should clip with subtitles burned |
| **Actual Behavior** | What actually happened | FFmpeg error: "subtitles filter not found" |
| **Error Messages** | Complete error output or logs | Full traceback from terminal |
| **Configuration** | Relevant `.env` settings | `FFMPEG_PATH`, `MAX_VIDEO_HEIGHT` values |

### Feature Request Guidelines

Feature requests should include:

1. **Use Case**: Describe the problem or need
2. **Proposed Solution**: Outline the desired functionality
3. **Alternatives Considered**: Other approaches you've thought about
4. **Impact**: Who would benefit and how

### Issue Submission

```bash
# Navigate to the issues page
# https://github.com/op7418/Youtube-clipper-skill/issues
```

As referenced in [README.md:292]().

**Sources:** [README.md:290-295]()

---

## Development Setup

Contributors need to set up a local development environment to work on the codebase.

### Development Environment Setup Flow

```mermaid
flowchart TD
    Start["Fork Repository"]
    
    Start --> Clone["Clone Fork Locally<br/>git clone"]
    
    Clone --> SysDeps["Install System Dependencies"]
    
    SysDeps --> Python["Python 3.8+"]
    SysDeps --> YtDlp["yt-dlp"]
    SysDeps --> FFmpeg["FFmpeg with libass"]
    
    Python --> Install["Run install_as_skill.sh"]
    YtDlp --> Install
    FFmpeg --> Install
    
    Install --> InstallPyPkg["Install Python Packages<br/>yt-dlp, pysrt, python-dotenv"]
    InstallPyPkg --> CreateEnv["Create .env File<br/>from .env.example"]
    CreateEnv --> VerifyDeps["Verify Dependencies"]
    
    VerifyDeps --> DevReady["Development Environment Ready"]
    
    DevReady --> EditCode["Edit Files in scripts/"]
    EditCode --> LocalTest["Test Locally"]
    LocalTest --> Decision{Tests Pass?}
    
    Decision -->|No| Debug["Debug Issues"]
    Debug --> EditCode
    
    Decision -->|Yes| Commit["Commit Changes"]
    Commit --> Push["Push to Fork"]
    Push --> PR["Create Pull Request"]
```

### Installation Commands

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Youtube-clipper-skill.git
cd Youtube-clipper-skill

# 3. Install system dependencies
# macOS:
brew install python yt-dlp ffmpeg-full

# Ubuntu:
sudo apt install python3 yt-dlp ffmpeg libass-dev

# 4. Run installation script
bash install_as_skill.sh

# 5. Verify installation
python3 --version  # Should be 3.8+
yt-dlp --version
ffmpeg -filters 2>&1 | grep subtitles  # Verify libass support
```

The [install_as_skill.sh]() script handles dependency installation as documented in [Installation](#2.1).

### Development Directory Structure

After setup, the development directory contains:

```
Youtube-clipper-skill/
├── scripts/
│   ├── download_video.py          # Edit to modify download logic
│   ├── analyze_subtitles.py       # Edit for chapter analysis
│   ├── clip_video.py              # Edit for clipping logic
│   ├── burn_subtitles.py          # Edit for subtitle burning
│   ├── extract_subtitle_clip.py   # Edit for subtitle extraction
│   └── utils.py                   # Edit for shared utilities
├── .env                           # Local configuration
├── .env.example                   # Configuration template
└── install_as_skill.sh            # Installation script
```

See [Project Structure](#9.1) for detailed directory documentation.

**Sources:** [README.md:36-46](), [README.md:50-84]()

---

## Code Contribution Guidelines

When contributing code changes, follow these guidelines to maintain consistency and quality.

### Code Style and Standards

| **Aspect** | **Standard** | **Rationale** |
|------------|--------------|---------------|
| **Language** | Python 3.8+ | Compatibility with Claude Code environment |
| **Imports** | Standard library first, then third-party, then local | PEP 8 convention |
| **Error Handling** | Try-except with specific exceptions | Graceful degradation |
| **Logging** | Use `print()` for user-facing messages | Claude Code CLI integration |
| **Configuration** | Use `.env` variables via `python-dotenv` | Separation of config from code |
| **File Paths** | Use `pathlib.Path` where possible | Cross-platform compatibility |

### Script Organization Pattern

All scripts in `scripts/` follow a common pattern:

```mermaid
graph TD
    Script["Python Script<br/>(*.py)"]
    
    Script --> Imports["Import Section<br/>stdlib → 3rd party → local"]
    Script --> EnvLoad["Load Environment<br/>load_dotenv()"]
    Script --> Constants["Define Constants<br/>from env vars"]
    Script --> Functions["Helper Functions<br/>specific to script"]
    Script --> Main["Main Function<br/>script logic"]
    Script --> Entry["Entry Point<br/>if __name__ == '__main__'"]
    
    EnvLoad --> DotEnv[".env file<br/>Configuration"]
    Constants --> EnvVars["Environment Variables<br/>FFMPEG_PATH, etc."]
    
    Functions --> Utils["utils.py<br/>Shared utilities"]
    
    Main --> ExtTools["External Tools<br/>yt-dlp, ffmpeg"]
    
    style Utils fill:#f9f9f9
    style DotEnv fill:#f9f9f9
    style ExtTools fill:#f9f9f9
```

For example, [download_video.py]() follows this pattern, as do all other scripts in `scripts/`.

### Utility Function Guidelines

When adding shared functionality:

1. **Add to `utils.py`**: Place reusable functions in [scripts/utils.py]()
2. **Document parameters**: Include docstrings with parameter types and return values
3. **Error handling**: Return `None` or raise specific exceptions
4. **Examples**: Add inline usage examples in comments

Example from `utils.py`:

```python
def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
```

See [Utilities Module](#4.6) for documentation of existing utility functions.

### Configuration Changes

When adding new configuration options:

1. **Add to `.env.example`**: Include the new variable with a descriptive comment
2. **Set default value**: Provide a sensible default in the script
3. **Document**: Update [Configuration](#6) documentation
4. **Validate**: Add validation logic for the new setting

Example pattern:

```python
from dotenv import load_dotenv
import os

load_dotenv()

# New configuration with default
NEW_SETTING = os.getenv('NEW_SETTING', 'default_value')
```

**Sources:** [scripts/download_video.py](), [scripts/utils.py](), [.env.example]()

---

## Pull Request Process

### Pull Request Workflow

```mermaid
sequenceDiagram
    participant Contributor
    participant Fork as "Forked Repository"
    participant Origin as "Origin Repository<br/>op7418/Youtube-clipper-skill"
    participant Maintainer
    
    Contributor->>Fork: 1. Make changes locally
    Contributor->>Fork: 2. Test changes
    Contributor->>Fork: 3. Commit changes
    Contributor->>Fork: 4. Push to fork
    Fork->>Origin: 5. Create Pull Request
    
    Origin->>Maintainer: 6. Notify maintainer
    Maintainer->>Origin: 7. Review code
    
    alt Changes Requested
        Maintainer->>Contributor: 8a. Request changes
        Contributor->>Fork: 9a. Make updates
        Fork->>Origin: 10a. Update PR
        Maintainer->>Origin: 11a. Review again
    end
    
    alt Approved
        Maintainer->>Origin: 8b. Approve PR
        Maintainer->>Origin: 9b. Merge to main
        Origin->>Fork: 10b. Close PR
    end
```

### Pull Request Checklist

Before submitting a pull request:

- [ ] **Code changes tested locally**: Run the modified scripts with test videos
- [ ] **No new dependencies added**: Unless discussed in an issue first
- [ ] **Configuration documented**: If `.env` variables added, update `.env.example`
- [ ] **Error handling present**: Scripts should not crash on expected failures
- [ ] **File paths work cross-platform**: Test on macOS/Linux if possible
- [ ] **Existing functionality preserved**: No breaking changes without discussion
- [ ] **Comments added**: Complex logic should be explained

### Pull Request Description Template

```markdown
## Description
Brief description of changes

## Motivation
Why this change is needed (link to issue if applicable)

## Changes Made
- List of specific changes
- File modifications
- New functionality added

## Testing
- How you tested the changes
- Test video URLs used (if applicable)
- Configuration used

## Related Issues
Closes #123 (if applicable)
```

### Review Process

1. **Automated checks**: Ensure no syntax errors
2. **Manual review**: Maintainer reviews code logic and style
3. **Testing**: Maintainer may test with various video configurations
4. **Discussion**: Feedback provided via PR comments
5. **Merge**: Once approved, PR is merged to main branch

**Sources:** [README.md:290-295]()

---

## Community and Support

### Communication Channels

| **Channel** | **Purpose** | **Link** |
|-------------|-------------|----------|
| **GitHub Issues** | Bug reports, feature requests | [github.com/op7418/Youtube-clipper-skill/issues](https://github.com/op7418/Youtube-clipper-skill/issues) |
| **Pull Requests** | Code contributions | [github.com/op7418/Youtube-clipper-skill/pulls](https://github.com/op7418/Youtube-clipper-skill/pulls) |
| **README** | User documentation | [README.md]() |

As referenced in [README.md:292]().

### Project Maintenance

The project is maintained by **[op7418](https://github.com/op7418)**, as indicated in [README.md:315]().

### Acknowledgements

The project builds upon several open-source tools:

- **Claude Code**: AI-powered CLI environment ([README.md:307]())
- **yt-dlp**: YouTube download engine ([README.md:308]())
- **FFmpeg**: Video processing framework ([README.md:309]())

**Sources:** [README.md:305-310](), [README.md:315]()

---

## Additional Resources

### Documentation References

For contributors, these documentation pages provide essential context:

- **[Project Structure](#9.1)**: Repository organization and file purposes
- **[Recent Fixes and Improvements](#9.2)**: Recent changes and lessons learned
- **[Testing and Verification](#9.3)**: Testing workflows and verification steps
- **[Core Scripts](#4)**: Detailed documentation of each Python script
- **[Architecture](#3)**: System design and component relationships

### External Documentation

- **[SKILL.md]()**: Complete workflow and technical details
- **[TECHNICAL_NOTES.md]()**: Implementation notes and design decisions
- **[FIXES_AND_IMPROVEMENTS.md]()**: Changelog and bug fixes
- **[references/]()**: FFmpeg, yt-dlp, and subtitle formatting guides

These files provide technical depth for understanding the implementation.

**Sources:** [README.md:281-286]()