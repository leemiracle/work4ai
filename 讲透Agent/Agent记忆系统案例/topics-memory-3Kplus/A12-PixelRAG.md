# A-12 `StarTrail-org/PixelRAG`（9.5K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\StarTrail-org__PixelRAG
> Python（另含 Next.js web）/ 约 42.8k 行 / Apache-2.0 ｜ 论文官方代码库（arXiv:2606.28344，Berkeley SkyLab）："Web Screenshots Beat Text for RAG"——把文档渲染成截图、在图像上直接建检索索引的**像素原生检索引擎**

## 1. 架构总览（目录地图，标出核心目录的职责）

```
render/src/pixelrag_render/   # 渲染层：Chrome CDP 截图 → 8192px 高的 JPEG tile
│   ├─ backends/cdp.py, fast_cdp.py, pdf.py        # CDP（含 turbo 捕获）/ PDF 渲染后端
│   └─ strategies/cdp_*.py ×14                     # 14 种截图策略（oneshot/multitab/pipelined/overlap…）
index/src/pixelrag_index/     # 编排层：source(kiwix/web/pdf/local) → render → chunk → embed → build 四阶段
embed/src/pixelrag_embed/     # chunk.py（1024px 切条）、embed.py（vLLM/sglang GPU）、index.py（FAISS/Qdrant）
serve/src/pixelrag_serve/     # FastAPI 检索服务：FAISS 视觉索引 + 文本/图像查询 + base64 回图
train/                        # 双塔编码器训练：BiQwen3（Qwen3-VL 单向量 bi-encoder）+ SFT 数据管线
eval/                         # 论文 Table 1 复现 harness（nq/nqt/sqa/mms/evqa/livevqa 六基准）
web/ plugin/ skill/           # Next.js 演示、Claude Code 插件（pixelbrowse 技能）
src/pixelrag/cli.py           # 轻量 CLI 入口（pixelshot 截图命令独立分发）
```

核心原语只有两个（README 定位）：`render`（页面→截图 tile）与 `search`（视觉索引查询）。hosted 服务预建 **8.28M Wikipedia 页面索引**（README.md:44-47）。

## 2. 记忆机制深读（本笔记核心，每个论断钉 `相对路径:行号`）

> **主题相关性判定先行**：全仓 grep `agent memory|memory system|记忆` **零命中**（仅 eval/serve 代码注释里的无关单词）。PixelRAG 没有任何记忆写入/遗忘/演化机制——它是**检索引擎（RAG 基建）**，不是 Agent 记忆层。若强行映射到记忆主题，它对应的是"外部知识库的记忆表示格式"（像素而非文本），与 mem0/EverOS 的对话记忆管线没有交集。以下按"渲染→索引→检索管线"深读。

### 2.1 渲染管线（render：文档如何变成像素）

- `render_urls`：CDP 后端（默认）连真实 Chrome，按 `tile_height=8192 / viewport_width=875 / JPEG quality=85` 输出 `{stem}.png.tiles/` 目录；`stems` 参数支持外部指定顺序 ID（`render/src/pixelrag_render/render.py:59-100`）。
- 14 种截图策略按吞吐取舍：oneshot/multitab/pipelined_tabs/pipelined_dc/overlap/parallel…（`render/src/pixelrag_render/strategies/` 目录，14 个 `cdp_*.py`）；吞吐优化有专文（`docs/screenshot-throughput-optimization.md`）。
- 多源接入：kiwix（离线 Wikipedia ZIM）、web、PDF、local（md/txt/图片）；**md/txt 会先套 GitHub 风格 CSS 模板转 HTML 再截图**（`index/src/pixelrag_index/pipelines.py:166-239`，内联 `_HTML_TEMPLATE` 含表格/代码块样式）；图片则白底合成+缩到 ≤4000px 宽（`pipelines.py:253-298`）。
- 增量渲染防串档：tile 目录的 manifest 记录 `source` 身份，源集合变化导致位置漂移时拒绝复用旧像素（防"A 文档的像素配 B 文档的元数据"，`pipelines.py:17-53`）；manifest 写入用 tmp+`os.replace` 原子替换（`pipelines.py:323-327`）。

### 2.2 切块与嵌入（index：像素如何变成向量）

- 两级切块：8192px tile → **1024px 高 × 875px 宽的 2D 网格 chunk**；小于一个 Qwen3-VL patch（28px）的残条丢弃（`embed/src/pixelrag_embed/chunk.py:49-50`、`:159-222`）；chunks.json 记录每个 chunk 的 `x_offset/y_offset/width/height` 与 tile MD5 哈希用于变更检测（`chunk.py:229-245`）。
- 嵌入模型：`Qwen/Qwen3-VL-Embedding-2B`（serve 侧默认，`serve/src/pixelrag_serve/api.py:16`）；自训 LoRA 版是 **BiQwen3**——Qwen3VL 单向量双塔，last-token pooling + L2 归一（`train/models/biqwen3.py:40-41`）。
- 嵌入产物 npz schema（原文摘录，`embed/src/pixelrag_embed/embed.py:27-38`）：`embeddings float16[N,D] / article_ids int64 / tile_indices / chunk_indices / y_offsets / tile_heights / page_heights / viewport_widths / image_hashes / tile_paths`；查询键 `(article_id, tile_index, chunk_index)`。chunk 级嵌入比整 tile 嵌入"视觉 token 数降 ~8×"（`embed.py:13-17`）。
- GPU 侧 vLLM/sglang 后端、多卡 `--gpu-ids 0,1,2,3`、持久 worker 池防 atexit 挂死（`embed.py:1-11`、`:50-56`）。

### 2.3 索引与检索（serve：查询如何命中像素）

- 索引后端 FAISS（IVF，`nlist=min(4096, vectors//40)`，`index/src/pixelrag_index/pipelines.py:440-453`）或 Qdrant；论文级索引 28.2M 向量 / ~217G（`eval/README.md:31`、`:84`）。
- `/search` 流程：文本或 base64 图像查询 → 现场编码（禁止混用预计算向量与原始查询，`api.py:469-477`）→ FAISS 检索（nprobe 可覆写）→ 命中还原为 `(article_id, tile_index, chunk_index)` 并可选 base64 回传原图块（`api.py:464-563`）。
- 过滤是**真预过滤**：department 过滤走 FAISS IDSelector（只打分该部门向量）而非后过滤，保证 n_docs 兑付；articles_only/min_tile_height 时按 10×/5× 超采再过滤（`api.py:484-508`）。
- 按需渲染模式：serve 不落 4T tile 库时，检索命中现场渲染该页再回图（`api.py:533-537`，offload 到线程避免 `asyncio.run` 死锁；实现在 `serve/src/pixelrag_serve/render_ondemand.py`）。
- 防泄漏细节：返回相对 tile 路径而非服务器绝对路径（`api.py:538-545`）；请求 ID 中间件 + 查询日志 jsonl（`api.py:105-155`）。

### 2.4 遗忘·整合·演化

**无**。索引只有 build（全量/append/recreate，`pipelines.py:422-438`）与 chunk 层 MD5 哈希变更检测重切（`chunk.py:120-132`）；没有 decay、没有合并、没有记忆更新——再次印证这是检索引擎而非记忆系统。

### 2.5 注入上下文的方式

- 检索结果（图像块 base64）直接作为 VLM reader 的证据输入：`run_bench.py --retrieval-top-k 5 --reader-top-k 3`（`eval/README.md:113-118`）——**注入的是图像 token 而非文本片段**，这是与文本 RAG 的本质差异。
- Claude Code 插件路径：`pixelbrowse` skill 让 Claude 用 `pixelshot` 截图并"读图"代替抓 HTML（README.md:56-70；`plugin/skills/pixelbrowse/SKILL.md`）。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

**① 四阶段管线总装**（`index/src/pixelrag_index/pipelines.py:78-82`）：
```python
def build(config: dict, limit: int | None = None, force: bool = False) -> Path:
    """Build a searchable FAISS index from a document source.

    Stages: source → ingest (render) → chunk → embed → build index
    """
```

**② 2D 网格切块（1024×875，丢弃 <28px 残条）**（`embed/src/pixelrag_embed/chunk.py:49-50` + `:189-199`）：
```python
CHUNK_HEIGHT = 1024
MIN_CHUNK_HEIGHT = 28  # one Qwen3-VL patch; merge tiny tails into previous
...
        while y < h:
            ch = min(CHUNK_HEIGHT, h - y)
            # Discard tiny height tail (< 28px = one Qwen3-VL patch)
            if ch < MIN_CHUNK_HEIGHT:
                break
            x = 0
            while x < w:
                cw = min(viewport_width, w - x)
                if cw < MIN_CHUNK_HEIGHT:  # discard tiny right-edge sliver
                    break
```

**③ 嵌入 npz schema（图像块的"记忆记录"格式）**（`embed/src/pixelrag_embed/embed.py:27-40`）：
```python
    Output npz arrays per chunk:
        embeddings      float16  [N, D]   — embedding vector
        article_ids     int64    [N]      — Wikipedia article ID
        tile_indices    int32    [N]      — which 8192px tile (0-based)
        chunk_indices   int32    [N]      — which 1024px strip within tile (0-based)
        y_offsets       int32    [N]      — Y position of chunk top edge in page (px)
        ...
    Lookup key: (article_id, tile_index, chunk_index) — lexsorted in output.
```

**④ 检索主路径：预过滤 + nprobe + 超采**（`serve/src/pixelrag_serve/api.py:484-506`）：
```python
    if req.articles_only:
        fetch_k = req.n_docs * 10
    elif req.min_tile_height:
        fetch_k = req.n_docs * 5
    else:
        fetch_k = req.n_docs
    ...
    if req.department:
        # Department pre-filter: the backend scores only that department's
        # vectors (FAISS: IDSelector; Qdrant: payload filter) — a real
        # pre-filter, not post-filtering, so n_docs results are guaranteed
        raw = backend.raw_search(query_vectors, fetch_k, ...)
```

**⑤ 双塔编码器定义**（`train/models/biqwen3.py:40-41`）：
```python
class BiQwen3(Qwen3VLModel):
    """Single-vector bi-encoder with last-token pooling + L2 normalization."""
```

## 4. 基准/评测声明（反虚荣视角：自封 or 第三方？可复现？数字与口径）

- 论文 Table 1（Qwen3.5-4B reader, k=3）在 `eval/README.md:140-147` 完整列出：如 SimpleQA naive 7.0 → pixel-LoRA 78.8、EVQA 27.2 → 45.1、NQ 30.4 → 58.7——**基线（naive/Trafilatura 文本抽取）与像素法同表对照** [自封-论文，但复现资产开源]。
- 复现链路异常扎实：`eval/README.md` 给出锁定环境（uv sync --frozen、vLLM 0.19.0、H100）、四服务拓扑表、数据来源表（FAISS 索引/4T tiles/训练数据全在 HF `StarTrail-org/*`）、preflight 检查、逐 cell 的 think/max_tokens/judge 配置（`eval/README.md:10-134`）；并诚实披露"NQ 严格精确匹配比论文低 ~20pp，因论文用 gpt-4.1 LLM judge"（`eval/README.md:151-154`）——**口径透明度罕见地高**。
- 自报"H100 上 pixel 各 cell 复现误差 ~1pp"（`eval/README.md:149`）[自封-复现声明]；训练侧有 v8 消融文档（`train/docs/v8_ablation_results.md`）。
- 无第三方独立复现收录；8.28M 页 hosted API 公开可打（README.md:44-47），实测门槛低。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）

1. **像素作为记忆的一等表示**：表格/图表/版式在文本抽取中必然失真，PixelRAG 证明"存截图+按块嵌入"可检索；对 Agent 记忆的启示是——多模态经历（网页、UI 轨迹）可以不转录为文本而直接以图像块入索引。
2. **(article_id, tile_index, chunk_index) 三级坐标寻址**：命中可精确定位回原文档物理位置（`embed.py:40`），比"chunk → 段落文本"的文本 RAG 寻址更刚性。
3. **增量渲染的 manifest 身份校验**（source 漂移即重渲染，`pipelines.py:17-53`）+ tile MD5 哈希变更检测（`chunk.py:120-132`）——对外部语料库的"内容变更→索引失效"问题给了朴素但正确的解。
4. **预过滤而非后过滤**的部门/元数据过滤（FAISS IDSelector，`api.py:493-506`）——保证 n_docs 兑付，文本记忆库的 metadata 过滤同样适用。
5. eval harness 的工程范式：环境锁定 + 服务拓扑表 + preflight + 逐 cell judge 口径披露，值得所有"带数字的仓库"效仿（`eval/README.md` 全篇）。

## 6. 局限与风险（失败模式、安全隐患、工程债）

- **与"Agent 记忆"主题基本无关**：无记忆写入/遗忘/个性化，无 per-user 隔离（查询日志默认全量落盘 `logs/queries.jsonl`，`api.py:98-120`，多租户场景有隐私风险）；作为"记忆系统案例"只能当**知识表示格式的对照组**。
- 存储成本极端：论文复现需 ~217G FAISS 索引 + ~4T tiles（`eval/README.md:51-54`）、~220G RAM（`:84-85`）；按需渲染模式单页渲染延迟高（需把超时调到 7200s，`eval/README.md:91-93`）。
- 纯向量单塔检索：无重排、无混合检索（BM25/关键词路径缺席；对照 MemOS/EverOS 的混合管线，这是检索质量的已知短板，靠 LoRA 对齐弥补）。
- 嵌入模型绑定 Qwen3-VL patch 语义（28px 残条规则、875px 原生宽度均为该模型分布特化，`chunk.py:50`、`:182-186`），换模型需重调全部切块常数并重建索引。
- CDP 依赖真实 Chrome（自带 chromium 构建，`render/chrome-build/BUILD.md`），渲染层是最大运维脆弱点。

## 7. 一句话对比 mem0

mem0 管的是"模型该记住关于你的什么"（抽取-更新-遗忘的对话记忆闭环）；PixelRAG 管的是"世界长什么样"（把文档变成可检索的像素块）——它是 RAG 检索引擎而非记忆层，其对本主题的真实价值在于证明了**多模态记忆可以跳过文本转录、以原生图像块直接入索引**这一表示路线。
