<!-- source: DeepWiki mcp.deepwiki.com · repo op7418/Youtube-clipper-skill · page 7 Advanced Topics · fetched 2026-10-26 -->

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

