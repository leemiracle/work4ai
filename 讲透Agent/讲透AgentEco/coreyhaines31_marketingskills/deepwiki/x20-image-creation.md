<!-- source: DeepWiki mcp.deepwiki.com · repo coreyhaines31/marketingskills · extra page Image Creation · fetched 2026-10-27 -->

# Image Creation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/image/SKILL.md](skills/image/SKILL.md)
- [skills/image/references/ai-image-prompting.md](skills/image/references/ai-image-prompting.md)
- [skills/video/SKILL.md](skills/video/SKILL.md)
- [skills/video/evals/evals.json](skills/video/evals/evals.json)
- [skills/video/references/edit-anatomy.md](skills/video/references/edit-anatomy.md)

</details>



The `image` skill provides a comprehensive framework for creating and optimizing marketing visuals using a combination of AI generation models, professional design tools, and technical optimization techniques. It enables the production of blog heroes, social graphics, product mockups, and brand assets while ensuring technical performance (e.g., WebP compression) and brand consistency.

## System Overview

The image creation pipeline transitions from natural language requirements to specific model selection and prompting strategies. It distinguishes between generative tasks (new visuals) and design tasks (templated/brand-constrained visuals). Before execution, the system checks for existing context in `.agents/product-marketing.md` to ensure brand alignment [skills/image/SKILL.md:14-16]().

### Logic Flow: Model Selection

The system follows a decision tree to select the optimal AI model based on specific creative requirements such as text accuracy, brand consistency, or visual style.

```mermaid
graph TD
    "User_Request"["User Request"] --> "Check_Text_Requirement"["Need text in image?"]
    "Check_Text_Requirement" -- "Yes" --> "Ideogram_3.0"["Ideogram 3.0 (Best)"]
    "Check_Text_Requirement" -- "No" --> "Check_Consistency"["Need brand consistency?"]
    
    "Check_Consistency" -- "Yes" --> "Flux_Model"["Flux (Multi-image Reference)"]
    "Check_Consistency" -- "No" --> "Check_Edit"["Need to edit existing?"]
    
    "Check_Edit" -- "Yes" --> "Gemini_Nano"["Gemini / Nano Banana"]
    "Check_Edit" -- "No" --> "General_Gen"["GPT Image / Midjourney"]

    subgraph "Natural Language Space"
    "User_Request"
    end

    subgraph "Code & Tool Entity Space"
    "Ideogram_3.0"
    "Flux_Model"
    "Gemini_Nano"
    "General_Gen"
    end
```

**Sources:** [skills/image/SKILL.md:54-93](), [skills/image/references/ai-image-prompting.md:129-176]()

## AI Image Generation

The skill documents a multi-model approach to generation, prioritizing different engines based on their technical strengths. Note that DALL-E 3 is fully deprecated in favor of the `gpt-image-1` family [skills/image/SKILL.md:66]().

### Model Comparison Matrix

| Model | Primary Strength | API Availability | Text Capability |
| :--- | :--- | :--- | :--- |
| **Gemini (Nano Banana)** | All-around, native editing, multi-image ref | [Gemini API](https://ai.google.dev/gemini-api/docs/image-generation) | Good |
| **Flux (BFL)** | Photorealism, brand consistency (Kontext) | [BFL API](https://docs.bfl.ai/) | Limited |
| **Ideogram 3.0** | Typography & Branded graphics | [Ideogram API](https://developer.ideogram.ai/) | Best |
| **GPT Image** | General purpose, native ChatGPT | [OpenAI API](https://platform.openai.com/docs/guides/image-generation) | Decent |
| **Recraft V3** | Vector & Illustrative assets | [Recraft API](https://www.recraft.ai/docs) | Strong |

**Sources:** [skills/image/SKILL.md:56-66]()

### Prompting Formula

Effective generation relies on a structured prompting formula [skills/image/SKILL.md:97-103]():
`[Subject] + [Setting/Context] + [Visual Style] + [Lighting] + [Composition] + [Technical Specs]`

**Example Prompt:**
> "A laptop on a minimal white desk showing a dashboard UI, soft directional lighting from the left, shallow depth of field, clean commercial photography style, 16:9 aspect ratio, 4K" [skills/image/SKILL.md:99-103]()

**Sources:** [skills/image/SKILL.md:97-103](), [skills/image/references/ai-image-prompting.md:9-13]()

## Design & Optimization

For tasks requiring exact brand adherence or technical performance, the skill moves beyond pure generation into design tools and optimization.

### Design Tool Selection

| Scenario | Tool | Reasoning |
| :--- | :--- | :--- |
| **Non-designer speed** | Canva | Massive template library, Magic Resize, Brand Kit [skills/image/SKILL.md:123](). |
| **Design Systems** | Figma | Component-based, Auto Layout, MCP server for reading designs [skills/image/SKILL.md:132-136](). |
| **Programmatic OG** | Vercel OG | Dynamic generation via HTML/CSS (Satori) [skills/image/SKILL.md:144](). |

**Sources:** [skills/image/SKILL.md:119-136]()

### Technical Optimization Standards

The skill enforces specific technical standards for web performance:
1.  **Format**: Prefer **WebP** for web (25-34% smaller than JPEG).
2.  **Compression**: Recommendation for `imagemin` or `sharp` for automated pipelines.
3.  **OG Images**: Standardize on **1200x630** pixels.

**Sources:** [skills/image/references/ai-image-prompting.md:207-215]()

## Implementation Data Flow

This diagram illustrates how a request for a marketing asset (like a blog hero) is processed through the skill's logic into a final optimized asset, incorporating the `product-marketing.md` context check.

```mermaid
sequenceDiagram
    participant U as "User"
    participant S as "Image Skill (SKILL.md)"
    participant PMC as ".agents/product-marketing.md"
    participant AI as "AI Model (Flux/Ideogram)"
    participant OPT as "Optimization (WebP/Sharp)"

    U->>S: "Create a blog hero for our new feature"
    S->>PMC: Read brand colors & ICP
    S->>S: Apply Prompt Formula (Subject + Style + ...)
    S->>AI: Generate Image (Aspect Ratio 1200x630)
    AI-->>S: Raw PNG/JPEG
    S->>OPT: Convert to WebP & Compress
    OPT-->>S: Optimized Asset
    S-->>U: Final Marketing Image
```

**Sources:** [skills/image/SKILL.md:14-33](), [skills/image/references/ai-image-prompting.md:194-204]()

## Video and Motion Integration

While `image` handles static assets, it closely integrates with the `video` skill for motion content. The `video` skill introduces a **Reverse-Engineering** workflow for replicating edit styles without copying creative content [skills/video/references/edit-anatomy.md:1-6]().

### Edit Anatomy Decomposition

When matching a reference video, the system extracts the "editing grammar" across nine dimensions:

```mermaid
graph LR
    "Ref_Video"["Reference Video"] --> "Watch_Video"["watch-video (Multimodal)"]
    "Watch_Video" --> "Decomposition"["Extract Anatomy"]
    
    subgraph "The Beat Sheet (edit-anatomy.md)"
    "Decomposition" --> "Shot_Framing"["Shot & Framing"]
    "Decomposition" --> "Cut_Rhythm"["Cut Rhythm"]
    "Decomposition" --> "Caption_Style"["Caption Style"]
    "Decomposition" --> "Sound_Design"["Sound Design"]
    end

    "Shot_Framing" --> "Execution"["Execute with Remotion/Hyperframes"]
    "Cut_Rhythm" --> "Execution"
    "Caption_Style" --> "Execution"
    "Sound_Design" --> "Execution"
```

**Sources:** [skills/video/references/edit-anatomy.md:27-41](), [skills/video/SKILL.md:54-76]()

## Aspect Ratio Quick Reference

| Placement | Ratio | Dimensions (px) |
| :--- | :--- | :--- |
| **Blog Hero / OG Image** | 1.91:1 | 1200 x 630 |
| **Instagram / LinkedIn Square** | 1:1 | 1080 x 1080 |
| **TikTok / Reels / Shorts** | 9:16 | 1080 x 1920 |
| **Twitter (X) Header** | 3:1 | 1500 x 500 |
| **Product Hunt Gallery** | 1.67:1 | 1270 x 760 |

**Sources:** [skills/image/references/ai-image-prompting.md:209-225]()

## Related Skills
- **ad-creative**: Specifically for paid ad specifications and bulk creative generation [skills/image/SKILL.md:3]().
- **video**: For motion content and programmatic video using `Hyperframes` or `Remotion` [skills/video/SKILL.md:3]().
- **social-content**: For the strategy of where and when to post these images [skills/image/SKILL.md:3]().

**Sources:** [skills/image/SKILL.md:3](), [skills/video/SKILL.md:3]()

---

