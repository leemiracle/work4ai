# DeepWiki 索引 — huggingface/fineVideo

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 22 页 · 全文 136400 字符

- [1 FineVideo: Project Overview](1-finevideo-project-overview.md)
  - [1.1 Pipeline Architecture & Data Flow](1.1-pipeline-architecture-data-flow.md)
  - [1.2 Scalability & Distributed Execution Model](1.2-scalability-distributed-execution-model.md)
- [2 Raw Dataset Ingestion](2-raw-dataset-ingestion.md)
  - [2.1 YouTube Commons Filter (`filter-yt-commons.py`)](2.1-youtube-commons-filter-filter-yt-commons.py.md)
  - [2.2 Video Downloader Service (`ytdlps3`)](2.2-video-downloader-service-ytdlps3.md)
- [3 Dynamic Filters](3-dynamic-filters.md)
  - [3.1 Video Dynamism Filter (`check_static.py`)](3.1-video-dynamism-filter-check-static.py.md)
  - [3.2 Word Density Filter (`worddensityfiltering.py`)](3.2-word-density-filter-worddensityfiltering.py.md)
- [4 Video Categorization](4-video-categorization.md)
  - [4.1 Content Taxonomy & Prompt Generation](4.1-content-taxonomy-prompt-generation.md)
  - [4.2 TGI Inference Client & Slurm Deployment](4.2-tgi-inference-client-slurm-deployment.md)
- [5 Content Selection](5-content-selection.md)
  - [5.1 Oracle Selection Algorithm (`oracle.py`)](5.1-oracle-selection-algorithm-oracle.py.md)
  - [5.2 Content Taxonomy Reference](5.2-content-taxonomy-reference.md)
- [6 Content Annotation](6-content-annotation.md)
  - [6.1 Video Annotation Pipeline (`video2annotation.py`)](6.1-video-annotation-pipeline-video2annotation.py.md)
  - [6.2 Gemini Annotation Prompt & Output Schema](6.2-gemini-annotation-prompt-output-schema.md)
- [7 Fine Alignment](7-fine-alignment.md)
  - [7.1 Scene Boundary Adjustment (`video_alignment.py`)](7.1-scene-boundary-adjustment-video-alignment.py.md)
  - [7.2 Timestamp Normalization & Continuity Enforcement](7.2-timestamp-normalization-continuity-enforcement.md)
- [8 Glossary](8-glossary.md)
