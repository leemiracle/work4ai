<!-- source: DeepWiki mcp.deepwiki.com · repo op7418/NanoBanana-PPT-Skills · page 6 Style System · fetched 2026-10-26 -->

# Style System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [generate_ppt.py](generate_ppt.py)
- [styles/gradient-glass.md](styles/gradient-glass.md)
- [styles/vector-illustration.md](styles/vector-illustration.md)

</details>



## Purpose and Scope

This document describes the style system architecture, which defines visual aesthetics for generated presentations. The style system implements a template-based prompt engineering framework that separates visual design from content generation logic.

For information about using styles in practice, see [Command Line Usage](#4.2). For details on the generation pipeline that consumes these styles, see [Prompt Engineering](#5.2).

---

## Architecture Overview

The style system is a hierarchical template inheritance system where base visual definitions are combined with page-type-specific templates and content to generate complete AI prompts.

### Style System Flow

```mermaid
graph TB
    StyleFile["styles/STYLE_NAME.md<br/>Markdown File"]
    LoadFunc["load_style_template()<br/>generate_ppt.py:15-32"]
    BaseTemplate["基础提示词模板<br/>Base Visual Language"]
    PageTypes["Page Type Logic<br/>generate_ppt.py:35-59"]
    
    CoverType["Cover Page<br/>page_type='cover'"]
    ContentType["Content Page<br/>page_type='content'"]
    DataType["Data Page<br/>page_type='data'"]
    
    PromptGen["generate_prompt()<br/>Combines template + type + content"]
    CompletePrompt["Complete Prompt<br/>Ready for Gemini API"]
    
    StyleFile --> LoadFunc
    LoadFunc --> BaseTemplate
    BaseTemplate --> PageTypes
    
    PageTypes --> CoverType
    PageTypes --> ContentType
    PageTypes --> DataType
    
    CoverType --> PromptGen
    ContentType --> PromptGen
    DataType --> PromptGen
    
    PromptGen --> CompletePrompt
```

**Sources:** [generate_ppt.py:15-59]()

### Style Selection and Loading

```mermaid
graph LR
    CLI["Command Line<br/>--style argument"]
    StylePath["styles/gradient-glass.md<br/>or styles/vector-illustration.md"]
    ReadFile["File I/O<br/>open() with utf-8"]
    ParseSections["Section Extraction<br/>find '## 基础提示词模板'"]
    Template["Base Template String<br/>Stored in memory"]
    
    CLI --> StylePath
    StylePath --> ReadFile
    ReadFile --> ParseSections
    ParseSections --> Template
    
    Template --> PromptLoop["For each slide in slides_plan.json"]
```

**Sources:** [generate_ppt.py:15-32](), [generate_ppt.py:189-190]()

---

## Style File Structure

Each style file is a Markdown document with standardized sections that define visual language and page-specific templates.

### Required Sections

| Section Header | Purpose | Used By |
|----------------|---------|---------|
| `## 风格ID` | Unique identifier | File naming, documentation |
| `## 风格名称` | Human-readable name | Documentation, user selection |
| `## 适配模型` | Compatible AI models | Compatibility checking |
| `## 风格描述` | Visual aesthetic summary | User guidance |
| `## 基础提示词模板` | Base prompt template | `load_style_template()` extracts this |
| `## 页面类型模板` | Page type variations | Documentation reference |
| `## 技术参数` | Model configuration | Documentation reference |

**Sources:** [styles/gradient-glass.md:1-91](), [styles/vector-illustration.md:1-132]()

### Template Extraction Logic

The `load_style_template()` function extracts only the base prompt template section between two marker strings:

```mermaid
graph TB
    FileContent["Full Markdown File"]
    FindStart["Find: '## 基础提示词模板'<br/>start_idx"]
    FindEnd["Find: '## 页面类型模板'<br/>end_idx"]
    Extract["content[start_idx+len(marker):end_idx]"]
    Strip["template.strip()"]
    Return["Return base template string"]
    Fallback["Fallback: Return entire content<br/>if markers not found"]
    
    FileContent --> FindStart
    FindStart --> FindEnd
    FindEnd -->|Markers found| Extract
    FindEnd -->|Markers missing| Fallback
    Extract --> Strip
    Strip --> Return
```

**Sources:** [generate_ppt.py:15-32]()

**Implementation:**

```
start_marker = "## 基础提示词模板"
end_marker = "## 页面类型模板"
start_idx = content.find(start_marker)
end_idx = content.find(end_marker)
template = content[start_idx + len(start_marker):end_idx].strip()
```

This extraction ensures only the base visual language definition is used, leaving page-specific logic to the code.

---

## Prompt Generation Process

The `generate_prompt()` function combines the base style template with page-type-specific instructions and slide content.

### Prompt Assembly Flow

```mermaid
graph TB
    Inputs["Function Inputs:<br/>style_template, page_type,<br/>content_text, slide_number,<br/>total_slides"]
    
    BasePrompt["prompt = f'{style_template}\n\n'"]
    
    CheckType{"Determine Page Type"}
    
    IsCover{"slide_number == 1<br/>OR page_type == 'cover'"}
    IsData{"page_type == 'data'<br/>OR slide_number == total_slides"}
    IsContent["Default: Content Page"]
    
    CoverInstr["Add Cover Instructions:<br/>'在中心放置一个巨大的复杂3D玻璃物体'"]
    DataInstr["Add Data Instructions:<br/>'使用分屏设计，左侧排版文字'"]
    ContentInstr["Add Content Instructions:<br/>'使用Bento网格布局'"]
    
    AppendContent["Append: {content_text}"]
    ReturnPrompt["Return: Complete Prompt String"]
    
    Inputs --> BasePrompt
    BasePrompt --> CheckType
    CheckType --> IsCover
    CheckType --> IsData
    CheckType --> IsContent
    
    IsCover -->|True| CoverInstr
    IsData -->|True| DataInstr
    IsContent --> ContentInstr
    
    CoverInstr --> AppendContent
    DataInstr --> AppendContent
    ContentInstr --> AppendContent
    
    AppendContent --> ReturnPrompt
```

**Sources:** [generate_ppt.py:35-59]()

### Page Type Decision Logic

The system automatically determines page type using position-based heuristics:

| Condition | Page Type | Template Applied |
|-----------|-----------|------------------|
| `slide_number == 1` OR `page_type == "cover"` | Cover | Hero layout with 3D glass object |
| `slide_number == total_slides` OR `page_type == "data"` | Data/Summary | Split-screen with visualization |
| All other slides | Content | Bento grid layout |

**Sources:** [generate_ppt.py:39-57]()

---

## Built-In Styles Comparison

The system includes two production-ready styles with distinct visual languages.

### Gradient Glass Style

```mermaid
graph TB
    subgraph "Visual Elements"
        Glass["Glassmorphism<br/>Frosted glass containers<br/>with blur effects"]
        Objects["3D Objects<br/>Polished metal, acrylic,<br/>holographic materials"]
        Lighting["Volumetric Lighting<br/>Soft ray-traced reflections"]
    end
    
    subgraph "Layout System"
        Bento["Bento Grid<br/>Modular rounded rectangles"]
        Spacing["Forced White Space<br/>Avoid crowding"]
    end
    
    subgraph "Color Palette"
        Base["Base: Void Black<br/>or Ceramic White"]
        Accent["Aurora Gradients:<br/>Neon purple, electric blue,<br/>coral orange, cyan"]
    end
    
    subgraph "Typography"
        Font["Sans-serif<br/>High contrast"]
    end
    
    Glass --> UseCase1["Tech Presentations"]
    Objects --> UseCase1
    Bento --> UseCase1
    Accent --> UseCase1
    
    UseCase1 --> Output1["Modern SaaS<br/>Product Demos<br/>Data Reports"]
```

**Key Characteristics:**
- **Style ID:** `gradient-glass`
- **File:** [styles/gradient-glass.md]()
- **Aesthetic:** Apple Keynote minimalism + glassmorphism
- **Rendering Quality:** Unreal Engine 5, 8K textures
- **Typical Use Cases:** Product demonstrations, technical sharing, creative proposals

**Sources:** [styles/gradient-glass.md:1-91]()

### Vector Illustration Style

```mermaid
graph TB
    subgraph "Visual Style"
        Flat["Flat Vector Illustration<br/>No gradients or 3D"]
        Lines["Black Outline<br/>Uniform stroke weight<br/>(Monoline)"]
        Geometry["Geometric Simplification<br/>Toy-like aesthetic"]
    end
    
    subgraph "Layout System"
        Panorama["Panoramic Banner<br/>Top 1/3 of slide"]
        Blocks["Colored Rectangle Blocks<br/>Content separation"]
    end
    
    subgraph "Color Palette"
        Base2["Base: Cream/Off-white<br/>Paper texture"]
        Vintage["Retro Colors:<br/>Coral red, mint green,<br/>mustard yellow, stone blue"]
    end
    
    subgraph "Typography"
        Serif["Retro Serif<br/>for main titles"]
        Sans["Geometric Sans-serif<br/>for body text"]
    end
    
    Flat --> UseCase2["Educational Content"]
    Lines --> UseCase2
    Geometry --> UseCase2
    Vintage --> UseCase2
    
    UseCase2 --> Output2["Education<br/>Creative Proposals<br/>Brand Showcases"]
```

**Key Characteristics:**
- **Style ID:** `vector-illustration`
- **File:** [styles/vector-illustration.md]()
- **Aesthetic:** Flat design + retro coloring + black outlines
- **Visual Feel:** Warm, cute, nostalgic
- **Typical Use Cases:** Educational presentations, creative proposals, children's content, brand showcases

**Sources:** [styles/vector-illustration.md:1-132]()

### Side-by-Side Comparison

| Aspect | Gradient Glass | Vector Illustration |
|--------|----------------|---------------------|
| **Visual Language** | 3D, glassmorphism, futuristic | Flat, geometric, retro |
| **Materials** | Glass, metal, holographic | Vector shapes with outlines |
| **Colors** | Neon gradients, high contrast | Vintage pastels, muted tones |
| **Layout System** | Bento grid, modular containers | Panoramic banner + blocks |
| **Typography** | Sans-serif, high contrast | Retro serif + geometric sans |
| **Rendering Complexity** | High (Unreal Engine 5 quality) | Low (simple vector graphics) |
| **Best For** | Tech/Business/SaaS | Education/Creative/Branding |

**Sources:** [styles/gradient-glass.md:13-30](), [styles/vector-illustration.md:17-50]()

---

## Technical Specifications

### API Configuration

Both styles use identical technical parameters for the Gemini API:

```mermaid
graph LR
    Model["model:<br/>'gemini-3-pro-image-preview'"]
    Modality["response_modalities:<br/>['IMAGE']"]
    Aspect["aspect_ratio:<br/>'16:9'"]
    Resolution["image_size:<br/>'2K' or '4K'"]
    
    Model --> Config["GenerateContentConfig"]
    Modality --> Config
    Aspect --> ImageConfig["ImageConfig"]
    Resolution --> ImageConfig
    ImageConfig --> Config
```

**Sources:** [generate_ppt.py:84-94]()

### Resolution Options

| Resolution | Dimensions | Use Case | Generation Time |
|------------|------------|----------|-----------------|
| **2K** (Recommended) | 2752 x 1536 pixels | Standard presentations, balanced quality | ~30s per slide |
| **4K** | 5504 x 3072 pixels | High-quality exports, print materials | ~60s+ per slide |

The resolution is specified via the `--resolution` command-line argument and passed to the `generate_slide()` function.

**Sources:** [generate_ppt.py:62](), [generate_ppt.py:167-172](), [styles/gradient-glass.md:82-90]()

### Model Configuration Code

The API call configuration in `generate_slide()`:

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=['IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size=resolution  # "2K" or "4K"
        )
    )
)
```

**Sources:** [generate_ppt.py:84-94]()

---

## Extension Points

The style system is designed for extensibility through custom style files.

### Creating a Custom Style

```mermaid
graph TB
    Create["Create: styles/custom-name.md"]
    Required["Add Required Sections:<br/>风格ID, 风格名称, 风格描述"]
    BaseTemplate["Define: ## 基础提示词模板<br/>Your visual language rules"]
    PageTypes["Define: ## 页面类型模板<br/>Cover, Content, Data templates"]
    Technical["Define: ## 技术参数<br/>Model configuration"]
    
    Usage["Use: --style styles/custom-name.md"]
    
    Create --> Required
    Required --> BaseTemplate
    BaseTemplate --> PageTypes
    PageTypes --> Technical
    Technical --> Usage
```

**Requirements:**
1. **File Location:** Place in `styles/` directory
2. **Encoding:** UTF-8
3. **Marker Strings:** Must include `## 基础提示词模板` and `## 页面类型模板` sections
4. **Content:** Base template must define complete visual language (materials, colors, typography, layout rules)

**Sources:** [generate_ppt.py:15-32](), [generate_ppt.py:163-166]()

### Style Template Anatomy

A minimal custom style structure:

```
# Custom Style Name

## 风格ID
custom-name

## 风格名称
My Custom Style

## 适配模型
- Nano Banana Pro (gemini-3-pro-image-preview)

## 风格描述
Brief description of visual aesthetic.

## 基础提示词模板

[Your complete visual language definition here]
- Visual style rules
- Color palette
- Typography specifications
- Material definitions
- Layout principles
- Rendering quality requirements

## 页面类型模板

### 封面页模板
[Cover page composition rules]

### 内容页模板
[Content page composition rules]

### 数据页模板
[Data page composition rules]

## 技术参数
[Same as built-in styles]
```

The `load_style_template()` function will extract only the text between `## 基础提示词模板` and `## 页面类型模板`, ensuring consistent behavior.

**Sources:** [styles/gradient-glass.md:1-91](), [styles/vector-illustration.md:1-132]()

---

## Integration with Generation Pipeline

The style system integrates with the generation pipeline at the prompt engineering stage:

```mermaid
graph LR
    SlidePlan["slides_plan.json<br/>Content structure"]
    StyleFile["styles/STYLE.md<br/>Visual definitions"]
    
    LoadStyle["load_style_template()<br/>Extract base template"]
    
    Loop["For each slide"]
    GenPrompt["generate_prompt()<br/>Combine: style + type + content"]
    
    APICall["generate_slide()<br/>Send to Gemini API"]
    SaveImage["Save: slide-XX.png"]
    
    SlidePlan --> Loop
    StyleFile --> LoadStyle
    LoadStyle --> GenPrompt
    Loop --> GenPrompt
    GenPrompt --> APICall
    APICall --> SaveImage
```

**Pipeline Stages:**
1. **Pre-generation:** Style template loaded once at startup
2. **Per-slide:** `generate_prompt()` combines template with content
3. **Generation:** Complete prompt sent to Gemini API
4. **Post-processing:** Images saved with consistent naming

**Sources:** [generate_ppt.py:185-257]()

---

## Prompt Audit Trail

All generated prompts are logged to `prompts.json` for debugging and iteration:

```json
{
  "metadata": {
    "title": "Presentation Title",
    "total_slides": 10,
    "resolution": "2K",
    "style": "styles/gradient-glass.md",
    "generated_at": "2024-01-15T10:30:00"
  },
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "content": "Slide content text",
      "prompt": "Complete generated prompt...",
      "image_path": "outputs/TIMESTAMP/images/slide-01.png"
    }
  ]
}
```

This audit trail enables:
- **Debugging:** Inspect exact prompts sent to API
- **Iteration:** Identify prompts needing refinement
- **Documentation:** Understand what visual instructions produced which outputs

**Sources:** [generate_ppt.py:136-142](), [generate_ppt.py:243-249]()

---

