<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/skills · extra page XLSX Skill · fetched 2026-10-30 -->

# XLSX Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/xlsx/scripts/recalc.py](skills/xlsx/scripts/recalc.py)

</details>



## Purpose and Scope

The XLSX Skill is a source-available, production-grade document processing skill that enables Claude to manipulate Excel spreadsheet files (`.xlsx`, `.xlsm`, `.xltx`, `.csv`, `.tsv`). This skill powers Claude's spreadsheet capabilities and serves as a reference implementation for complex spreadsheet operations, formatting, charting, cleaning messy data, and formula recalculation.

The primary capability provided by this skill is **formula recalculation** and error detection using LibreOffice headless integration, alongside robust handling of `openpyxl` quirks and formula compatibility rules.

For information about other document processing skills, see:
- DOCX Skill ([3.1.1]())
- PDF Skill ([3.1.2]())
- PPTX Skill ([3.1.3]())

Sources: [skills/xlsx/SKILL.md:1-5](), [skills/xlsx/scripts/recalc.py:1-4]()

## Skill Structure

The XLSX skill follows the standard skill directory structure:

```
skills/xlsx/
├── SKILL.md           # Skill definition, prompt guidelines, and gotchas
└── scripts/
    └── recalc.py      # Formula recalculation and external link safety engine
```

Sources: [skills/xlsx/SKILL.md:1-19](), [skills/xlsx/scripts/recalc.py:1-193]()

## Core Capabilities

### Formula Recalculation & Execution

The skill's primary automated function is to recalculate all formulas in an Excel file using LibreOffice's native calculation engine. Because `openpyxl` writes formulas as strings with no cached values, raw files read back as `None` for data readers until recalculated [skills/xlsx/SKILL.md:32-34]().

The recalculation engine is implemented in `recalc()` and supporting functions within [skills/xlsx/scripts/recalc.py:124-193]().

**Key Features:**
- Executes LibreOffice in headless mode via a StarBasic macro to trigger `calculateAll()` [skills/xlsx/scripts/recalc.py:33-37](), [skills/xlsx/scripts/recalc.py:174-181]().
- Rewrites the workbook in-place with freshly evaluated formula values [skills/xlsx/SKILL.md:40]().
- Scans calculated outputs for standard Excel formula errors (`#VALUE!`, `#DIV/0!`, `#REF!`, `#NAME?`, `#NULL!`, `#NUM!`, `#N/A`).
- Protects against destructive external reference stripping (`external_links_at_risk()`) [skills/xlsx/scripts/recalc.py:81-121]().

Sources: [skills/xlsx/SKILL.md:30-47](), [skills/xlsx/scripts/recalc.py:30-121]()

## Architecture Overview

The following diagram bridges natural language spreadsheet workflows to specific Python code entities in `recalc.py`.

**Diagram: Natural Language to Code Entity Mapping**

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        UserRequest[""Spreadsheet Recalculation Request""]
        SafetyValidation[""External Link Safety Validation""]
    end
    
    subgraph "CodeEntitySpace"
        RecalcEntry[""recalc(filename, timeout, force)""]
        LinkCheck[""external_links_at_risk(filename)""]
        ProfileSetup[""setup_libreoffice_macro(profile_dir)""]
        ProfileRecalc[""_recalc_with_profile(filename, abs_path, timeout, profile_dir)""]
    end

    UserRequest --> RecalcEntry
    RecalcEntry --> LinkCheck
    LinkCheck -.-> SafetyValidation
    RecalcEntry --> ProfileRecalc
    ProfileRecalc --> ProfileSetup
```

Sources: [skills/xlsx/SKILL.md:1-79](), [skills/xlsx/scripts/recalc.py:81-193]()

## LibreOffice Integration & Macro Execution

### Macro-Based Recalculation

To force LibreOffice to recalculate and save workbooks programmatically without user prompts, `recalc.py` injects a StarBasic macro into a temporary user profile directory [skills/xlsx/scripts/recalc.py:30-78]().

**Macro Definition (`RECALCULATE_MACRO`):**
Defined at [skills/xlsx/scripts/recalc.py:30-38]():

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">
    Sub RecalculateAndSave()
      ThisComponent.calculateAll()
      ThisComponent.store()
      ThisComponent.close(True)
    End Sub
</script:module>
```

### Macro Setup and Invocation Architecture

The diagram below maps macro initialization constants and temporary directories to the execution functions.

**Diagram: Macro Setup and Invocation Flow**

```mermaid
graph LR
    subgraph "MacroAndProfileSpace"
        MacroConst[""RECALCULATE_MACRO (Module1.xba)""]
        ProfileDir[""tempfile.TemporaryDirectory(prefix='recalc-lo-profile-')""]
    end
    
    subgraph "ExecutionSpace"
        SetupMacro[""setup_libreoffice_macro()""]
        SubprocessRun[""subprocess.run(cmd)""]
        SofficeBin[""soffice / gtimeout / timeout""]
    end

    MacroConst --> SetupMacro
    ProfileDir --> SetupMacro
    SetupMacro --> SubprocessRun
    SubprocessRun --> SofficeBin
```

The function `setup_libreoffice_macro()` prepares a temporary profile directory and writes `Module1.xba` [skills/xlsx/scripts/recalc.py:56-78](). The script then executes LibreOffice via `subprocess.run()` using the script URL [skills/xlsx/scripts/recalc.py:174-192]().

Sources: [skills/xlsx/scripts/recalc.py:30-78](), [skills/xlsx/scripts/recalc.py:158-192]()

## External Link Safety Checks

Workbooks linking to external files present a risk during recalculation. Because `openpyxl` strips cached values of external references upon saving, recalculating without the source workbook causes LibreOffice to evaluate them to `#NAME?` and permanently destroy the external links [skills/xlsx/SKILL.md:52-59]().

The function `external_links_at_risk(filename)` inspects `xl/externalLinks/` via `zipfile` and scans defined names and formulas for external references [skills/xlsx/scripts/recalc.py:81-121](). If at-risk cells are detected and `force=False`, `recalc()` refuses to run unless `--force` is passed [skills/xlsx/scripts/recalc.py:143-156]().

Sources: [skills/xlsx/SKILL.md:52-59](), [skills/xlsx/scripts/recalc.py:81-121]()

## Platform-Specific Handling & Timeouts

To prevent headless LibreOffice instances from hanging indefinitely, `recalc.py` wraps execution with timeout commands based on the host operating system [skills/xlsx/scripts/recalc.py:41-48](), [skills/xlsx/scripts/recalc.py:183-187]().

| Platform | Timeout Wrapper Utility | Detection Function |
|----------|-------------------------|--------------------|
| Linux | `timeout` | `shutil.which("timeout")` [skills/xlsx/scripts/recalc.py:183-184]() |
| macOS | `gtimeout` | `has_gtimeout()` [skills/xlsx/scripts/recalc.py:41-48](), [skills/xlsx/scripts/recalc.py:185-186]() |
| Fallback | None (relies on subprocess timeout) | N/A |

Sources: [skills/xlsx/scripts/recalc.py:41-48](), [skills/xlsx/scripts/recalc.py:183-187]()

## SKILL.md Guidelines & openpyxl Gotchas

When writing scripts or building spreadsheets via `SKILL.md` instructions, Claude must adhere to core tabular standards and account for `openpyxl` limitations:

1. **Two-Load Requirement:** Reading a model requires two passes—`data_only=True` for cached values (formulas gone) and default loading for formula strings [skills/xlsx/SKILL.md:73]().
2. **Destructive Saves:** Saving after `data_only=True` permanently replaces formulas with literal values [skills/xlsx/SKILL.md:74]().
3. **Formula Compatibility:** 
   - Prefer Excel-2007 era functions (`SUMIFS`, `INDEX`, `MATCH`, `IFERROR`, `SUMPRODUCT`) [skills/xlsx/SKILL.md:66]().
   - Post-2007 functions require an `_xlfn.` prefix (`_xlfn.TEXTJOIN`, `_xlfn.IFS`, `_xlfn.MAXIFS`, etc.) [skills/xlsx/SKILL.md:67]().
   - Never use `XLOOKUP`, `XMATCH`, `SORT`, `FILTER`, `UNIQUE`, or `SEQUENCE` because LibreOffice cannot evaluate them or encounters spill errors [skills/xlsx/SKILL.md:68]().
4. **Merged Cells:** Write only to the top-left anchor cell; other cells in the range are read-only `MergedCell` instances [skills/xlsx/SKILL.md:76]().
5. **Macro Preservation:** Pass `keep_vba=True` when loading `.xlsm` files to avoid stripping macros [skills/xlsx/SKILL.md:77]().
6. **Sheet Name Quoting:** Sheet names containing spaces must be quoted in cross-sheet references (e.g., `='Assumptions Inputs'!$B$5`) [skills/xlsx/SKILL.md:78]().

Sources: [skills/xlsx/SKILL.md:20-79]()

---

