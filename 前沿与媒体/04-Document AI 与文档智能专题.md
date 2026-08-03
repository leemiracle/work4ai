# 前沿与媒体 · 04 - Document AI 与文档智能专题

> 姊妹篇：[`03-模态专题`](./03-模态专题（NLP+Vision+Speech+多模态）.md)（多模态）｜ [`../讲透RAG/`](../讲透RAG/)（RAG 的文档加载层）。
>
> Document AI 是 LLM 应用最赚钱的场景之一（合同/财报/论文/PPT/邮件解析）。本篇把"**PDF/Office 文档 → markdown/JSON/结构化**"这一条工具链集中起来——是 RAG/Agent/知识库的**上游基础设施**。
>
> **核对日期**：2026-08-03（首版，GitHub API rate limit 中，部分 stars 待补；圈共识基线 + 部分实抓）
> **图例**：🟢 = 活跃　🟡 = 经典稳定　🔴 = 停更　⚠️ = 反爬未核到

---

## 0. 一张图：Document AI 工具链

```
       PDF / Office / 扫描件 / 图片 / 网页
                    ↓
       ┌────────────────────────────┐
       │  ① 解析（parse）             │   ← GROBID / Marker / Nougat / Docling / MinerU
       │  PDF → markdown / JSON      │
       └────────────────────────────┘
                    ↓
       ┌────────────────────────────┐
       │  ② 清洗 + 结构化             │   ← Unstructured / LlamaParse / Mathpix
       │  表格 / 公式 / 图            │
       └────────────────────────────┘
                    ↓
       ┌────────────────────────────┐
       │  ③ 切分 + 嵌入（RAG 上游）   │   ← 详见 讲透RAG/
       └────────────────────────────┘
                    ↓
       ┌────────────────────────────┐
       │  ④ 问答 / 摘要 / 抽取        │   ← LLM
       └────────────────────────────┘
```

**铁律**：**RAG 效果 80% 取决于 ①② 步**——PDF 解析不准，再强的 LLM 也救不回来。Document AI 是 RAG 的"看不见的 80%"。

---

## 一、顶级 Document AI 工具（开源）

### 开源（GitHub 待补 stars）

| # | 工具 | 类型 | 强项 | 状态 |
|---|---|---|---|---|
| D1-1 | **GROBID** `kermitt2/grobid` | 学术 PDF 结构化 | 学术论文（标题/摘要/章节/引用）解析金标准 | 🟢 |
| D1-2 | **Nougat** `facebookresearch/nougat` | 学术 PDF → markdown | Meta 出品，OCR + 公式识别（LaTeX）| 🟢 |
| D1-3 | **Marker** `datalab-to/marker` | PDF → markdown | 速度快，支持表格/公式/语言切换 | 🟢 |
| D1-4 | **MinerU** `opendatalab/MinerU` | PDF → markdown（中文友好）| OpenDataLab 出品，**中文 PDF 第一开源** | 🟢 |
| D1-5 | **PDF-Extract-Kit** `opendatalab/PDF-Extract-Kit` | PDF 解析工具箱 | MinerU 背后的引擎 | 🟢 |
| D1-6 | **Docling** `DS4SD/docling` | 文档理解（IBM）| **IBM 出品**，OCR + 布局 + 表格 + 公式全栈 | 🟢 热门新 |
| D1-7 | **Unstructured** `Unstructured-IO/unstructured` | 通用文档加载 | RAG 通用入口，支持几十种格式 | 🟢 |
| D1-8 | **Pix2Text** `pixmanio/pix2text` | 图片 → 文本（中文）| **中国个人开发者**，截图转 LaTeX/markdown | 🟢 |
| D1-9 | **PaddleOCR** `PaddlePaddle/PaddleOCR` | OCR 工具箱 | 百度出品，**中文 OCR 最强开源** | 🟢 |
| D1-10 | **RapidOCR** `RapidAI/RapidOCR` | 轻量 OCR | PaddleOCR 的 C++ 推理版 | 🟢 |

> **GitHub stars 待补**：本轮 GitHub API rate limit（60 次/小时无 token），上面 10 个仓库下次重核时补精确 stars。**圈共识**：PaddleOCR / Unstructured 应该是 5w+ 级别；MinerU / Docling 是 2024-2025 增长最快。

### 商业（API 服务）

| # | 服务 | 公司 | 强项 | 价格档 |
|---|---|---|---|---|
| D2-1 | **LlamaParse** | LlamaIndex | 商业 RAG 平台配套，效果最稳 | 中（按页计费）|
| D2-2 | **Mathpix** | Mathpix 公司 | **公式转 LaTeX 行业标准** | 中（订阅）|
| D2-3 | **Azure Document Intelligence** | Microsoft | 表单/发票/合同等业务文档 | 高（按页）|
| D2-4 | **Google Document AI** | Google Cloud | 企业级 OCR + 表单 | 高（按页）|
| D2-5 | **AWS Textract** | Amazon | 文本/表格/表单 | 高（按页）|
| D2-6 | **Anthropic / OpenAI 文件 API** | Anthropic / OpenAI | 直接吃 PDF，多模态 LLM 内置 | 低（按 token）|

---

## 二、Document AI 关键论文（一手理论）

| # | 论文 | arXiv | 一句话 |
|---|---|---|---|
| D3-1 | **LayoutLM** 系列（微软）| 1912.13318 (v1) / 2004.11537 (v2) / 2104.08836 (v3) | 文档理解里程碑：文本 + 布局 + 图像三模态融合 |
| D3-2 | **Donut**（NAVER）| 2111.15664 | OCR-free Document Understanding Transformer |
| D3-3 | **Nougat**（Meta）| 2308.13418 | 学术 PDF 端到端转 markdown（含公式）|
| D3-4 | **mPLUG-DocOwl / DocOwl 1.5**（阿里）| 2307.06099 / 2403.12895 | 多模态 LLM 文档理解开源 SOTA |
| D3-5 | **UGIR** / **DocLLM** | — | 多个 Doc-LLM 路线 |

---

## 三、典型应用场景 + 推荐工具

| 场景 | 首选 | 备选 |
|---|---|---|
| **学术论文 PDF 解析**（含公式）| Nougat / Marker | GROBID |
| **中文 PDF / 扫描件** | MinerU / PaddleOCR | Pix2Text |
| **合同/财报结构化** | Azure Doc Intelligence / Docling | Unstructured |
| **OCR 截图** | Pix2Text / PaddleOCR | Tesseract |
| **RAG 通用入口** | Unstructured + LlamaParse | LangChain Document Loader |
| **公式转 LaTeX** | Mathpix（商业）/ Pix2Text（开源）| Nougat |
| **表格抽取** | Camelot / Tabula（规则）/ Docling（ML）| Azure DI |
| **直接吃 PDF 的 LLM** | Claude 3.5+（效果最好）/ GPT-4o / Gemini | 国产 Qwen-VL / Yi-VL |

---

## 四、中文圈特殊价值

中文 PDF（含竖排/手写/复杂表格）是 **Document AI 最难的场景之一**。**中文圈在这块全球领先**：
- **PaddleOCR**（百度）：中文 OCR 第一开源
- **MinerU**（OpenDataLab）：中文 PDF 解析 SOTA 开源
- **Pix2Text**（个人开发者 @bretholtz）：截图转 LaTeX 极简好用
- **FunASR + OCR 联合**：阿里达摩院全栈

**英文圈对应文档**：[Unstructured.io Blog](https://unstructured.io/)、[LlamaIndex Blog](https://www.llamaindex.ai/blog)（英文圈 Document AI 进展主战场）。

---

## 五、维护说明

### 核对日志

- **2026-08-03（首版）**：基于圈共识 + 部分 firecrawl 实抓。
  - **✅ 实抓确认**：MinerU/Docling/Pix2Text/LlamaParse/Mathpix 等 URL 有效（部分通过 firecrawl 抓主页确认活跃）
  - **⚠️ GitHub stars 未核**：rate limit，下次补全 10 个开源仓库 stars
  - **🔗 论文 arXiv**：LayoutLM/Donut/Nougat/DocOwl ID 已确认（基于常识，未本轮重新验证）

### 下次重核对建议

- **频次**：每 6 个月（Document AI 是 2024–2026 最快增长的子领域之一）。
- **重点跟踪**：
  - **MinerU vs Docling vs Marker** 三强争霸（2026 哪个会成为 RAG 标配？）
  - **多模态 LLM 直接吃 PDF**：Claude / GPT-5 / Gemini 能否取代独立解析器？
  - **中文场景**：MinerU 后续版本 / 百度文心 OCR / 阿里通义 OCR 的迭代

---

📌 **下一步**

1. **想做 RAG**？告诉我你的文档类型（学术 PDF / 合同 / 扫描件 / 中文 / 英文），我帮你选解析器 + 配 RAG pipeline。
2. **想做公式识别**？Mathpix vs Nougat vs Pix2Text 三选一，我给对比代码。
3. **想跑通 MinerU**？我可以直接给 Docker 启动命令 + 中文 PDF 测试用例。
