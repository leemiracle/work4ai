<!-- source: DeepWiki mcp.deepwiki.com · repo op7418/Youtube-clipper-skill · page 8 Troubleshooting · fetched 2026-10-26 -->

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

