<!-- source: DeepWiki mcp.deepwiki.com · repo op7418/Youtube-clipper-skill · page 3 Architecture · fetched 2026-10-26 -->

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

