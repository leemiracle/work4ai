<!-- source: DeepWiki mcp.deepwiki.com · repo coreyhaines31/marketingskills · extra page Schema Markup · fetched 2026-10-26 -->

# Schema Markup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/ai-seo/SKILL.md](skills/ai-seo/SKILL.md)
- [skills/ai-seo/evals/evals.json](skills/ai-seo/evals/evals.json)
- [skills/ai-seo/references/citations-vs-recommendations.md](skills/ai-seo/references/citations-vs-recommendations.md)
- [skills/ai-seo/references/content-patterns.md](skills/ai-seo/references/content-patterns.md)
- [skills/ai-seo/references/content-types.md](skills/ai-seo/references/content-types.md)
- [skills/ai-seo/references/okf.md](skills/ai-seo/references/okf.md)
- [skills/ai-seo/references/platform-ranking-factors.md](skills/ai-seo/references/platform-ranking-factors.md)
- [skills/competitors/SKILL.md](skills/competitors/SKILL.md)

</details>



This page documents the `schema-markup` skill, which provides knowledge and implementation guidance for adding structured data to web pages using schema.org vocabulary in JSON-LD format. Schema markup helps search engines understand page content and enables rich results in search engine result pages (SERPs).

For general SEO auditing including schema detection, see [SEO Audit](4.5.1). For optimizing content for AI search engines that consume structured data, see [AI SEO](4.5.2). For implementing schema at scale across templated pages, see [Programmatic SEO](4.5.3).

**Sources:** [skills/ai-seo/SKILL.md:3-3]()

## Skill Metadata

The `schema-markup` skill is triggered when users request help with structured data implementation, validation, or optimization. The skill is activated by natural language references to "schema markup," "structured data," "JSON-LD," "rich snippets," "schema.org," or specific schema types like "FAQ schema," "product schema," "review schema," or "breadcrumb schema."

| Property | Value |
|----------|-------|
| Skill Name | `schema-markup` |
| Version | 2.2.0 (via AI SEO) |
| Category | SEO & Discovery |
| Related Skills | `seo-audit`, `ai-seo`, `programmatic-seo`, `site-architecture`, `competitors` |
| File Location | `skills/schema-markup/SKILL.md` |

**Sources:** [skills/ai-seo/SKILL.md:1-5](), [skills/ai-seo/references/platform-ranking-factors.md:69-70]()

## Core Principles

The skill operates on four foundational principles that govern all schema implementation recommendations:

### Principle 1: Accuracy First
Schema markup must accurately represent the visible page content. The skill emphasizes that markup should never describe content that doesn't exist on the page, and implementations must be updated when page content changes.

### Principle 2: Use JSON-LD Format
Google recommends JSON-LD (JavaScript Object Notation for Linked Data) as the preferred structured data format. The skill prioritizes JSON-LD because it's easier to implement and maintain compared to Microdata or RDFa, and can be placed in either the `<head>` or end of `<body>` elements.
**Sources:** [skills/ai-seo/references/platform-ranking-factors.md:69-70]()

### Principle 3: Follow Google's Guidelines
Implementations must adhere to Google's structured data guidelines, using only markup types that Google supports, avoiding spam tactics, and reviewing eligibility requirements for specific rich result types.
**Sources:** [skills/ai-seo/SKILL.md:73-82]()

### Principle 4: Validate Everything
All schema implementations must be tested before deployment using validation tools, monitored through Google Search Console, and errors must be fixed promptly.

## Schema Type Reference

The skill provides implementation guidance for the most common schema.org types supported by Google for rich results and AI extraction:

```mermaid
graph TB
    subgraph "Organization & Site Identity"
        ["Organization<br/>Company homepage/about<br/>Required: name, url"]
        ["WebSite<br/>Homepage search box<br/>Required: name, url"]
    end
    
    subgraph "Content Types"
        ["Article/BlogPosting<br/>Blog posts, news<br/>Required: headline, image, datePublished, author"]
        ["FAQPage<br/>FAQ content<br/>Required: mainEntity array"]
        ["HowTo<br/>Tutorials, instructions<br/>Required: name, step"]
    end
    
    subgraph "Product & Commerce"
        ["Product<br/>Product pages<br/>Required: name, image, offers"]
        ["SoftwareApplication<br/>SaaS/app pages<br/>Required: name, offers"]
    end
    
    subgraph "Navigation & Structure"
        ["BreadcrumbList<br/>Page breadcrumbs<br/>Required: itemListElement"]
    end
    
    subgraph "Local & Events"
        ["LocalBusiness<br/>Local business pages<br/>Required: name, address"]
        ["Event<br/>Events, webinars<br/>Required: name, startDate, location"]
    end
```
**Diagram: Supported Schema Types and Required Properties**

**Sources:** [skills/ai-seo/references/platform-ranking-factors.md:30-30](), [skills/ai-seo/references/content-types.md:57-57]()

### Schema Type Summary Table

| Schema Type | Use Case | Required Properties | Recommended Properties |
|-------------|----------|---------------------|----------------------|
| Organization | Company homepage/about | `name`, `url` | `logo`, `sameAs`, `contactPoint` |
| WebSite | Homepage (search box) | `name`, `url` | `potentialAction` |
| Article | Blog posts, news | `headline`, `image`, `datePublished`, `author` | `dateModified`, `publisher`, `description` |
| Product | Product pages | `name`, `image`, `offers` | `sku`, `brand`, `aggregateRating`, `review` |
| SoftwareApplication | SaaS/app pages | `name`, `offers` | `applicationCategory`, `aggregateRating` |
| FAQPage | FAQ content | `mainEntity` (Q&A array) | — |
| HowTo | Tutorials | `name`, `step` | `totalTime`, `supply`, `tool` |
| BreadcrumbList | Breadcrumb navigation | `itemListElement` | — |
| LocalBusiness | Local business | `name`, `address` | `telephone`, `openingHours`, `priceRange` |
| Event | Events, webinars | `name`, `startDate`, `location` | `endDate`, `offers`, `performer` |

**Sources:** [skills/ai-seo/references/platform-ranking-factors.md:30-30](), [skills/ai-seo/references/platform-ranking-factors.md:78-78]()

## Schema and AI SEO (v2.2.0)

Schema markup is a critical component of AI Search Optimization. Beyond traditional rich snippets, structured data acts as a primary extraction signal for AI engines like Perplexity and Google AI Overviews.

- **Perplexity Preference**: Pages with `FAQPage` (JSON-LD) schema get cited noticeably more often by Perplexity. [skills/ai-seo/references/platform-ranking-factors.md:69-70]()
- **Google AI Overviews**: `Article`, `FAQPage`, `HowTo`, and `Product` schemas provide structured context that correlates with a 30-40% visibility boost in AI-generated answers. [skills/ai-seo/references/platform-ranking-factors.md:30-30]()
- **Timestamping**: `Article` schema with `datePublished` and `dateModified` is essential for ChatGPT, which favors content updated within the last 30 days (cited 3.2x more often). [skills/ai-seo/references/platform-ranking-factors.md:47-48](), [skills/ai-seo/references/platform-ranking-factors.md:78-78]()
- **Content-Answer Fit**: While schema is vital, ChatGPT citation likelihood is driven 55% by "content-answer fit"—matching the model's own response format. [skills/ai-seo/references/platform-ranking-factors.md:49-50]()

**Sources:** [skills/ai-seo/references/platform-ranking-factors.md:30-78]()

## Open Knowledge Format (OKF)

In addition to traditional Schema.org markup, the system supports the **Open Knowledge Format (OKF)**, a markdown-based spec for agent-readable site bundles introduced by Google in June 2026. OKF serves as "protocol-layer registration," similar to early schema adoption. [skills/ai-seo/references/okf.md:3-45]()

| Layer | Purpose |
|---|---|
| Schema Markup | Per-page structured data (Article, FAQPage, Product, etc.) |
| `llms.txt` | Points an agent at the handful of pages you most want read |
| `/okf/` bundle | Hands over the content itself as cross-linked concepts |

OKF uses a YAML frontmatter block in markdown files to define concepts:
```markdown
---
type: Article
title: How to Connect the Ahrefs MCP Server
resource: https://yoursite.com/blog/ahrefs-mcp/
tags: [mcp, ahrefs]
---
```
**Sources:** [skills/ai-seo/references/okf.md:19-31](), [skills/ai-seo/references/okf.md:51-60]()

## Validation and Testing Flow

The implementation workflow follows a strict validation cycle to ensure eligibility for rich results and AI extraction.

```mermaid
flowchart LR
    ["Implement<br/>JSON-LD Schema"] --> ["Validate with<br/>Rich Results Test"]
    ["Validate with<br/>Rich Results Test"] --> ["Check Status"]
    ["Check Status"] -->|"Errors"| ["Fix Required<br/>Properties"]
    ["Fix Required<br/>Properties"] --> ["Validate with<br/>Rich Results Test"]
    ["Check Status"] -->|"Valid"| ["Deploy to<br/>Production"]
    ["Deploy to<br/>Production"] --> ["Monitor in<br/>Search Console"]
```
**Diagram: Schema Validation and Deployment Flow**

### Validation Tools
- **Google Rich Results Test**: Primary validation tool for rich result eligibility.
- **Schema.org Validator**: Validates general schema.org compliance.
- **Search Console**: Provides enhancement reports for deployed schema.
- **Suganthan's OKF Generator**: Used to crawl and validate OKF bundles and visualize internal-linking nodes. [skills/ai-seo/references/okf.md:66-68]()

## Integration with Other Skills

Schema markup serves as a foundational layer for several other SEO and technical marketing skills.

```mermaid
graph LR
    ["schema-markup<br/>SKILL.md"]
    
    ["seo-audit<br/>Technical SEO Foundations"]
    ["ai-seo<br/>Optimization for LLMs"]
    ["programmatic-seo<br/>Scaled Page Generation"]
    ["site-architecture<br/>Breadcrumb Structure"]
    ["competitors<br/>Comparison Pages"]
    
    ["seo-audit"] --> ["schema-markup"]
    ["ai-seo"] --> ["schema-markup"]
    ["programmatic-seo"] --> ["schema-markup"]
    ["site-architecture"] --> ["schema-markup"]
    ["competitors"] --> ["schema-markup"]
```
**Diagram: Schema Markup Skill Interdependencies**

**Sources:** [skills/ai-seo/SKILL.md:3-3](), [skills/ai-seo/references/platform-ranking-factors.md:30-30](), [skills/competitors/SKILL.md:107-108]()

## Skill Invocation Flow

Before generating markup, the agent checks for context and assesses requirements:

1. **Context Check**: Read `.agents/product-marketing.md` (or legacy `product-marketing-context.md`) to understand site type and goals. [skills/ai-seo/SKILL.md:14-15]()
2. **Requirement Gathering**:
    - **Current AI Visibility**: Do you appear in AI answers today? [skills/ai-seo/SKILL.md:19-22]()
    - **Page Type**: What is the primary content? (SaaS, blog, product, etc.) [skills/ai-seo/SKILL.md:25-25]()
    - **Existing Data**: Do you have existing schema? [skills/ai-seo/SKILL.md:27-27]()
3. **Implementation**: Generate JSON-LD or OKF bundles. [skills/ai-seo/references/okf.md:63-68]()
4. **Validation**: Use Google's official stance as a guide—prioritize "helpful, reliable, people-first content" while layering on extractable structure. [skills/ai-seo/SKILL.md:80-91]()

**Sources:** [skills/ai-seo/SKILL.md:12-33](), [skills/ai-seo/references/okf.md:35-40]()

---

