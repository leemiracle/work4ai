<!-- source: DeepWiki mcp.deepwiki.com · repo yusufkaraaslan/Skill_Seekers · extra page HTML Scraping & BFS Traversal · fetched 2026-10-26 -->

# HTML Scraping & BFS Traversal

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/features/UNIFIED_SCRAPING.md](docs/features/UNIFIED_SCRAPING.md)
- [src/skill_seekers/cli/doc_scraper.py](src/skill_seekers/cli/doc_scraper.py)
- [src/skill_seekers/cli/scraper_utils.py](src/skill_seekers/cli/scraper_utils.py)
- [src/skill_seekers/cli/unified_scraper.py](src/skill_seekers/cli/unified_scraper.py)
- [src/skill_seekers/cli/unified_skill_builder.py](src/skill_seekers/cli/unified_skill_builder.py)
- [tests/test_c3_integration.py](tests/test_c3_integration.py)
- [tests/test_multi_source.py](tests/test_multi_source.py)
- [tests/test_scraper_utils.py](tests/test_scraper_utils.py)
- [tests/test_unified.py](tests/test_unified.py)
- [tests/test_unified_scraper_orchestration.py](tests/test_unified_scraper_orchestration.py)

</details>



This page covers the BFS URL traversal algorithm, URL filtering, HTML content extraction pipeline, rate limiting, concurrency modes, retry logic, and page state management implemented in `DocToSkillConverter`. It focuses specifically on how the scraper discovers and processes documentation pages from HTML sources. For the higher-level `DocToSkillConverter` architecture (initialization, llms.txt detection, checkpoint system, and `build_skill` output), see page [5.1](). For language detection from code blocks, see [5.1.3](). For smart page categorization, see [5.1.4]().

---

## BFS Queue Structure & State Management

The scraper uses a breadth-first search strategy to crawl documentation websites. All traversal state is held on the `DocToSkillConverter` instance, tracking pending work, visited URLs, accumulated pages, and rate limits.

| Attribute | Type | Purpose |
|---|---|---|
| `pending_urls` | `collections.deque` | FIFO frontier queue for BFS traversal |
| `visited_urls` | `set[str]` | Prevents re-processing identical URLs |
| `pages` | `list[dict]` | In-memory accumulator for extracted page data |
| `pages_scraped` | `int` | Counter used to enforce the `max_pages` limit |

The queue is initialized from configuration options at construction time:

[src/skill_seekers/cli/doc_scraper.py:240-241]()

```python
start_urls = config.get("start_urls", [self.base_url])
self.pending_urls = deque(start_urls)
```

When no `start_urls` key is present in configuration, `base_url` is used as the sole seed. Multiple starting points are fully supported by pre-populating the deque before traversal begins.

**BFS traversal execution flow:**

```mermaid
flowchart TD
    A["pending_urls\n(deque)"] --> B["Pop URL from left\n(FIFO / BFS)"]
    B --> C{"URL in\nvisited_urls?"}
    C -- "Yes" --> B
    C -- "No" --> D["Add to visited_urls"]
    D --> E["scrape_page(url)"]
    E --> F["extract_content() or\n_extract_markdown_content()"]
    F --> G["Collect page links"]
    G --> H{"is_valid_url(link)\nfor each link?"}
    H -- "Pass" --> I["Append to\npending_urls (right)"]
    H -- "Fail" --> J["Discard link"]
    I --> K{"pages_scraped\n>= max_pages?"}
    K -- "No" --> B
    K -- "Yes" --> L["Stop traversal"]
    E --> M["save_page() to\ndata_dir/pages/*.json"]
    E --> N["Append to\nself.pages list"]
```

Sources: [src/skill_seekers/cli/doc_scraper.py:203-263](), [src/skill_seekers/cli/doc_scraper.py:648-707]()

---

## URL Filtering & Normalization

Every candidate URL—whether discovered from link extraction or pre-loaded via `llms.txt`—passes through `is_valid_url` before entering `pending_urls`. Tracking parameters are stripped beforehand using `_normalize_url`.

[src/skill_seekers/cli/doc_scraper.py:218-237]()
[src/skill_seekers/cli/doc_scraper.py:105-119]()

The validation logic applies three sequential checks:
1. **Base URL prefix check** — The URL must start with `self.base_url` to constrain the crawl scope.
2. **Include pattern check** — If `url_patterns.include` is non-empty, the URL must match at least one inclusion substring.
3. **Exclude pattern check** — The URL must not match any exclusion substring in `url_patterns.exclude`.

```mermaid
flowchart LR
    url["URL string"] --> step1{"starts with\nbase_url?"}
    step1 -- "No" --> reject1["return False"]
    step1 -- "Yes" --> step2{"url_patterns.include\nnon-empty?"}
    step2 -- "No" --> step3{"any exclude\npattern matches?"}
    step2 -- "Yes" --> check_inc{"any include\npattern in URL?"}
    check_inc -- "No" --> reject2["return False"]
    check_inc -- "Yes" --> step3
    step3 -- "Yes" --> reject3["return False"]
    step3 -- "No" --> accept["return True"]
```

Sources: [src/skill_seekers/cli/doc_scraper.py:218-237]()

Anchor fragments are stripped from URLs during link collection:

[src/skill_seekers/cli/doc_scraper.py:350-355]()

```python
href = href.split("#")[0]
if self.is_valid_url(href) and href not in page["links"]:
    page["links"].append(href)
```

Sources: [src/skill_seekers/cli/doc_scraper.py:350-355]()

---

## Content Extraction Pipeline

When a URL is fetched, the scraper invokes either the Markdown extraction path or the default HTML extraction path (`extract_content`).

[src/skill_seekers/cli/doc_scraper.py:294-357]()

The extraction routine parses the response with `BeautifulSoup` and targets the main content area using `selectors.main_content` or `FALLBACK_MAIN_SELECTORS` (`main`, `article`, `div[role="main"]`, etc.) [src/skill_seekers/cli/doc_scraper.py:61-69](). Extracted dictionaries contain titles, headings, code samples, patterns, filtered paragraph text, and absolute links.

```mermaid
flowchart TD
    raw["HTTP response body"] --> bs["BeautifulSoup(content, 'html.parser')"]
    bs --> title_sel["soup.select_one(selectors.title)\n→ page['title']"]
    bs --> main_sel["soup.select_one(selectors.main_content)\n→ main element"]
    main_sel --> headings["main.find_all(h1..h6)\n→ page['headings']"]
    main_sel --> code_sel["main.select(selectors.code_blocks)\n→ detect_language() for each\n→ page['code_samples']"]
    main_sel --> patterns["extract_patterns(main, code_samples)\n→ page['patterns']"]
    main_sel --> paragraphs["main.find_all('p')\n(len > 20 chars only)\n→ page['content']"]
    bs --> links["soup.find_all('a', href=True)\n→ urljoin + strip #fragment\n→ is_valid_url filter\n→ page['links']"]
```

Sources: [src/skill_seekers/cli/doc_scraper.py:294-357](), [src/skill_seekers/cli/doc_scraper.py:61-69]()

---

## Scraping Execution Modes, Rate Limiting & Retry Logic

`DocToSkillConverter` supports synchronous single-threaded, multi-threaded, and asynchronous execution modes controlled by `workers` and `async_mode` configuration parameters.

| Mode | Trigger | Implementation Details |
|---|---|---|
| Single-threaded | `workers == 1` (default) | Sequential `scrape_page()` execution |
| Multi-threaded | `workers > 1` | `threading.Lock` protection on shared collections |
| Async | `async_mode == True` | `scrape_page_async()` with `asyncio.Semaphore` and `httpx.AsyncClient` |

### Retry Logic & Rate Limiting

Network requests incorporate automatic resilience via decorators (`retry_with_backoff` and `retry_with_backoff_async`) imported from `skill_seekers.cli.utils` [src/skill_seekers/cli/utils.py:52-53](). 

Rate limiting is enforced at the conclusion of each page processing block:

[src/skill_seekers/cli/doc_scraper.py:697-699]()

```python
rate_limit = self.config.get("rate_limit", DEFAULT_RATE_LIMIT)
if rate_limit > 0:
    time.sleep(rate_limit)
```

Sources: [src/skill_seekers/cli/doc_scraper.py:697-699](), [src/skill_seekers/cli/utils.py:52-53]()

---

## Page State Persistence & Checkpoints

Successfully parsed pages are saved to disk via `save_page()`. Pages with content lengths under 50 characters are filtered out.

[src/skill_seekers/cli/doc_scraper.py:631-646]()

Valid pages are stored as JSON files under `output/{name}_data/pages/` using a filename hash derived from the target URL: `{safe_title}_{url_hash}.json`. This provides the foundation for the checkpoint and resumption system described in Section [13.2]().

Sources: [src/skill_seekers/cli/doc_scraper.py:631-646]()

---

## Code Entity Map

```mermaid
flowchart LR
    subgraph "State Management"
        PU["pending_urls\n(deque)"]
        VU["visited_urls\n(set)"]
        PG["pages\n(list[dict])"]
    end

    subgraph "Filtering"
        IVU["is_valid_url()\n_normalize_url()"]
    end

    subgraph "Execution & Resilience"
        SP["scrape_page()\nrequests.get()"]
        SPA["scrape_page_async()\nhttpx.AsyncClient"]
        RBO["retry_with_backoff()\nretry_with_backoff_async()"]
        RL["rate_limit\ntime.sleep / asyncio.sleep"]
    end

    subgraph "Extraction & Parsing"
        EC["extract_content()\nBeautifulSoup"]
        EMC["_extract_markdown_content()"]
        EP["extract_patterns()"]
    end

    subgraph "Persistence"
        SVP["save_page()\noutput/{name}_data/pages/"]
    end

    PU --> SP
    PU --> SPA
    SP --> RBO
    SPA --> RBO
    SP --> IVU
    SP --> EC
    SP --> EMC
    EC --> EP
    SP --> SVP
    SVP --> PG
    PU -.->|"new links"| IVU
```

Sources: [src/skill_seekers/cli/doc_scraper.py:105-357](), [src/skill_seekers/cli/doc_scraper.py:631-754](), [src/skill_seekers/cli/utils.py:52-53]()

---

