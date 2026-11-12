<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/VideoAgent · page 8 Repository Maintenance · fetched 2026-11-09 -->

# Repository Maintenance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.DS_Store](.DS_Store)
- [assets/.DS_Store](assets/.DS_Store)

</details>



This page documents repository metadata files, version control hygiene practices, and best practices for maintaining the VideoAgent asset repository. It covers the handling of system-generated metadata files (specifically `.DS_Store` files), proper `.gitignore` configuration, and guidelines for asset organization and version control.

For information about the overall repository structure, see [Asset Repository Structure](#3). For details about specific asset types, see [Content Library](#4), [Evaluation Assets](#5), [Technical Documentation Assets](#6), and [Branding and Identity Assets](#7).

---

## System Metadata Files

The repository currently contains macOS system metadata files that are tracked in version control. These files serve no functional purpose in the repository and should be excluded.

### Current Metadata File Structure

```mermaid
graph TD
    Root[".DS_Store<br/>Root directory metadata"]
    Assets["assets/.DS_Store<br/>Assets directory metadata"]
    
    Root --> |"tracks folder view settings"|RootData["View preferences<br/>Window bounds<br/>Icon positions"]
    Assets --> |"tracks folder view settings"|AssetsData["View preferences<br/>Column settings<br/>Sort preferences"]
    
    style Root fill:#f9f9f9
    style Assets fill:#f9f9f9
```

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

### .DS_Store File Analysis

The `.DS_Store` (Desktop Services Store) files are binary files created by macOS Finder to store custom attributes of folders. The repository contains two instances:

| Location | File | Purpose | Should Track |
|----------|------|---------|--------------|
| Root | `.DS_Store` | Stores Finder view preferences for repository root | No |
| Assets directory | `assets/.DS_Store` | Stores Finder view preferences for assets folder | No |

These files contain serialized data including:
- Window bounds and positions
- Icon view settings (icon size, grid spacing)
- Column view preferences (column widths, sort order)
- Folder background settings
- Label colors

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

---

## .DS_Store File Handling

System metadata files like `.DS_Store` create repository pollution and should be excluded from version control.

### Problem Analysis

```mermaid
graph LR
    Mac["macOS User<br/>Developer"] --> |"browses folders"|Finder["macOS Finder"]
    Finder --> |"automatically creates"|DS1[".DS_Store"]
    Finder --> |"automatically creates"|DS2["assets/.DS_Store"]
    
    DS1 --> |"gets tracked in"|Git["Git Repository"]
    DS2 --> |"gets tracked in"|Git
    
    Git --> |"synced to"|Remote["GitHub Remote"]
    Remote --> |"cloned by"|Other["Other Users"]
    
    Other --> |"see irrelevant"|DS1
    Other --> |"see irrelevant"|DS2
    
    style DS1 fill:#ffcccc
    style DS2 fill:#ffcccc
```

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

### Issues with Tracking Metadata Files

| Issue | Impact | Severity |
|-------|--------|----------|
| Repository pollution | Clutters commit history with non-functional changes | Medium |
| Cross-platform incompatibility | Creates files meaningless to Windows/Linux users | Low |
| Merge conflicts | Can cause unnecessary conflicts in collaborative work | Medium |
| Security/privacy | May expose local directory structure information | Low |
| Binary diff bloat | Cannot generate meaningful diffs for changes | Low |

### Removal and Prevention Workflow

```mermaid
flowchart TD
    A["Identify tracked<br/>.DS_Store files"] --> B["Add to .gitignore"]
    B --> C["Remove from Git index<br/>but keep locally"]
    C --> D["Commit .gitignore<br/>changes"]
    D --> E["Verify exclusion"]
    
    B --> |"create/update"|GI[".gitignore file"]
    C --> |"execute"|CMD1["git rm --cached .DS_Store"]
    C --> |"execute"|CMD2["git rm --cached assets/.DS_Store"]
    D --> |"execute"|CMD3["git commit -m 'Remove .DS_Store files'"]
    E --> |"execute"|CMD4["git status"]
    
    style GI fill:#e1ffe1
    style CMD1 fill:#fff4e1
    style CMD2 fill:#fff4e1
    style CMD3 fill:#fff4e1
    style CMD4 fill:#fff4e1
```

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

---

## .gitignore Configuration

Proper `.gitignore` configuration prevents system metadata files from being tracked in the first place.

### Recommended .gitignore Entries

Create or update a `.gitignore` file in the repository root with the following entries:

```
# macOS system files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes

# Windows system files
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
Desktop.ini

# Linux system files
*~
.directory

# Editor and IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# Python cache (if Python code exists)
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Node modules (if Node.js code exists)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```

### Removal Commands

To remove existing `.DS_Store` files from Git tracking while preserving local copies:

```bash
# Remove specific .DS_Store files from Git index
git rm --cached .DS_Store
git rm --cached assets/.DS_Store

# Or remove all .DS_Store files recursively
find . -name .DS_Store -print0 | xargs -0 git rm --cached

# Commit the removal
git commit -m "Remove .DS_Store files from version control"

# Add .gitignore if not already committed
git add .gitignore
git commit -m "Add .gitignore to exclude system metadata files"
```

### Global Git Configuration

Alternatively, configure Git globally to ignore `.DS_Store` files across all repositories:

```bash
# Create or update global gitignore
echo ".DS_Store" >> ~/.gitignore_global
echo ".DS_Store?" >> ~/.gitignore_global
echo "._*" >> ~/.gitignore_global

# Configure Git to use the global ignore file
git config --global core.excludesfile ~/.gitignore_global
```

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

---

## Asset Management Best Practices

The repository contains extensive visual assets that require organized management.

### Current Asset Organization

```mermaid
graph TD
    Root["Repository Root"]
    Assets["assets/"]
    
    Root --> Assets
    
    Assets --> Logo1["logo.png"]
    Assets --> Logo2["logo_new.png"]
    Assets --> QR["QR.png"]
    Assets --> Cover1["cover_16-9.png"]
    Assets --> Cover2["cover_4-3.png"]
    Assets --> Cover3["cover_3-4.png"]
    Assets --> Framework["framework.jpg"]
    Assets --> Workflow["edit_workflow.png"]
    Assets --> Eval1["eval1_audio_new.png"]
    Assets --> Eval2["eval1_video_new.png"]
    Assets --> Many["... 20+ more files"]
    Assets --> DS["⚠ .DS_Store"]
    
    style DS fill:#ffcccc
    style Assets fill:#e1f5ff
```

**Sources:** [assets/.DS_Store:1-1]()

### Recommended Asset Organization

```mermaid
graph TD
    Root["Repository Root"]
    Assets["assets/"]
    
    Root --> Assets
    Root --> GI[".gitignore"]
    
    Assets --> Brand["branding/"]
    Assets --> Covers["covers/"]
    Assets --> Eval["evaluation/"]
    Assets --> Tech["technical/"]
    
    Brand --> Logo1["logo.png"]
    Brand --> Logo2["logo_new.png"]
    Brand --> QR["QR.png"]
    
    Covers --> Ratios["aspect-ratios/"]
    Covers --> Content["content-series/"]
    
    Ratios --> C1["cover_16-9.png"]
    Ratios --> C2["cover_4-3.png"]
    Ratios --> C3["cover_3-4.png"]
    
    Content --> Dune["dune/"]
    Content --> Cross["crosstalk/"]
    Content --> Inter["interstella/"]
    
    Eval --> Audio["eval1_audio_new.png"]
    Eval --> Video["eval1_video_new.png"]
    Eval --> Eva["eva1.png - eva4.jpg"]
    
    Tech --> Framework["framework.jpg"]
    Tech --> Workflow["edit_workflow.png"]
    Tech --> Audio2["audio_performance.jpg"]
    
    style Brand fill:#ffe1e1
    style Covers fill:#fff4e1
    style Eval fill:#f0e1ff
    style Tech fill:#e1ffe1
    style GI fill:#e1ffe1
```

**Sources:** [assets/.DS_Store:1-1]()

### Asset Naming Conventions

| Asset Type | Convention | Example |
|------------|-----------|---------|
| Logos | `logo_[variant].png` | `logo_new.png` |
| Covers | `[content]_[type]_cover.png` | `dune_original_cover.png` |
| Aspect ratios | `cover_[ratio].png` | `cover_16-9.png` |
| Evaluations | `eval[n]_[type]_[version].png` | `eval1_audio_new.png` |
| Technical diagrams | `[description].jpg/png` | `framework.jpg`, `edit_workflow.png` |

**Sources:** [assets/.DS_Store:1-1]()

---

## Version Control Guidelines

### File Type Tracking Policy

```mermaid
flowchart TD
    File["File added to repo"] --> Check{"File type?"}
    
    Check --> |"Documentation"|Doc["✓ Track<br/>README, LICENSE, .md"]
    Check --> |"Assets"|Asset["✓ Track<br/>images, diagrams"]
    Check --> |"Code"|Code["✓ Track<br/>.py, .js, .json"]
    Check --> |"System metadata"|Meta["✗ Ignore<br/>.DS_Store, Thumbs.db"]
    Check --> |"Build artifacts"|Build["✗ Ignore<br/>dist/, build/"]
    Check --> |"Dependencies"|Deps["✗ Ignore<br/>node_modules/, venv/"]
    Check --> |"IDE settings"|IDE["✗ Ignore<br/>.vscode/, .idea/"]
    
    Doc --> Track["Add to version control"]
    Asset --> Track
    Code --> Track
    
    Meta --> Ignore["Add to .gitignore"]
    Build --> Ignore
    Deps --> Ignore
    IDE --> Ignore
    
    Track --> Commit["git add & commit"]
    Ignore --> Skip["Exclude from tracking"]
    
    style Meta fill:#ffcccc
    style Build fill:#ffcccc
    style Deps fill:#ffcccc
    style IDE fill:#ffcccc
    style Doc fill:#e1ffe1
    style Asset fill:#e1ffe1
    style Code fill:#e1ffe1
```

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

### Large Asset Management

For repositories with many large binary assets, consider:

| Strategy | Use Case | Implementation |
|----------|----------|----------------|
| Git LFS | Large binary files (>1MB) | Install Git LFS, track `*.png`, `*.jpg`, `*.mp4` |
| External storage | Very large files (>100MB) | Use cloud storage, reference via URLs |
| Asset versioning | Multiple versions of assets | Organize by version subdirectories |
| Compression | Space optimization | Use lossless compression before committing |

### Commit Message Standards for Assets

Use descriptive commit messages that identify the asset changes:

```
feat(assets): add new logo variants for brand refresh
fix(assets): correct aspect ratio for cover_16-9.png
docs(assets): update evaluation result images for v2.0
refactor(assets): reorganize covers into subdirectories
chore(assets): remove duplicate content covers
```

**Sources:** [assets/.DS_Store:1-1]()

---

## Repository Health Monitoring

### Health Check Workflow

```mermaid
flowchart LR
    A["Repository"] --> B["Run health checks"]
    
    B --> C1["Check for<br/>.DS_Store files"]
    B --> C2["Validate<br/>.gitignore exists"]
    B --> C3["Scan for<br/>large files"]
    B --> C4["Check for<br/>duplicate assets"]
    
    C1 --> |"found"|R1["Flag for removal"]
    C1 --> |"none"|OK1["✓ Pass"]
    
    C2 --> |"missing"|R2["Create .gitignore"]
    C2 --> |"exists"|OK2["✓ Pass"]
    
    C3 --> |"found >50MB"|R3["Consider Git LFS"]
    C3 --> |"all <50MB"|OK3["✓ Pass"]
    
    C4 --> |"found"|R4["Deduplicate"]
    C4 --> |"none"|OK4["✓ Pass"]
    
    R1 --> Fix["Apply fixes"]
    R2 --> Fix
    R3 --> Fix
    R4 --> Fix
    
    OK1 --> Report["Health report"]
    OK2 --> Report
    OK3 --> Report
    OK4 --> Report
    
    Fix --> Report
    
    style R1 fill:#fff4e1
    style R2 fill:#fff4e1
    style R3 fill:#fff4e1
    style R4 fill:#fff4e1
```

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

### Automated Checks

Implement pre-commit hooks to prevent system metadata files from being committed:

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Check for .DS_Store files
if git diff --cached --name-only | grep -q "\.DS_Store"; then
    echo "Error: Attempting to commit .DS_Store files"
    echo "Please remove them: git rm --cached \$(find . -name .DS_Store)"
    exit 1
fi

# Check for large files
MAX_SIZE=10485760  # 10MB in bytes
for file in $(git diff --cached --name-only); do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt $MAX_SIZE ]; then
            echo "Error: File $file is larger than 10MB"
            echo "Consider using Git LFS for large files"
            exit 1
        fi
    fi
done

exit 0
```

### Repository Statistics

Monitor repository health with these metrics:

| Metric | Current State | Target |
|--------|---------------|--------|
| .DS_Store files tracked | 2 | 0 |
| .gitignore exists | No | Yes |
| Asset organization | Flat structure | Subdirectories |
| Large files (>10MB) | Unknown | Documented/LFS |
| Duplicate assets | Unknown | None |

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

---

## Maintenance Checklist

### Initial Setup

- [ ] Create `.gitignore` file in repository root
- [ ] Add system metadata file patterns to `.gitignore`
- [ ] Remove existing `.DS_Store` files from Git index: `git rm --cached .DS_Store assets/.DS_Store`
- [ ] Commit `.gitignore` and removal changes
- [ ] Verify files are no longer tracked: `git status`

### Regular Maintenance

- [ ] Audit repository for new system metadata files
- [ ] Review and reorganize assets into subdirectories as needed
- [ ] Check for duplicate or outdated assets
- [ ] Validate all large assets are necessary
- [ ] Update `.gitignore` for new file patterns
- [ ] Document asset organization in README

### Asset Updates

- [ ] Follow naming conventions when adding new assets
- [ ] Place assets in appropriate subdirectories
- [ ] Compress images before committing (if applicable)
- [ ] Write descriptive commit messages for asset changes
- [ ] Verify file sizes are reasonable

**Sources:** [.DS_Store:1-1](), [assets/.DS_Store:1-1]()

---

## Related Documentation

- For overall repository structure: [Asset Repository Structure](#3)
- For community engagement files: [Community and Licensing](#2)
- For specific asset categories: [Content Library](#4), [Evaluation Assets](#5)
- For branding materials: [Branding and Identity Assets](#7)