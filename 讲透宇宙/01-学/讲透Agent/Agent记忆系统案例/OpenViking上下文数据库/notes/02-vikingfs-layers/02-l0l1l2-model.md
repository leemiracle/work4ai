# 02 · L0/L1/L2 三层信息模型——目录级 sidecar、自底向上生成与 token 经济学

> **一句话总结**：OpenViking 给**每个目录**（而非每个文件）挂两个语义 sidecar——L0 `.abstract.md`（默认 ≤256 字符，供向量召回）与 L1 `.overview.md`（默认 ≤4000 字符，供 rerank 与导航），L2 是原始文件本体；二者由 SemanticProcessor 在写入后**异步、自底向上**用 LLM 生成，L0 直接从 L1 正文提取，检索时按 L0→L1→L2 逐级加载，用「宁可多读一次目录摘要，不可把整个子树塞进上下文」的方式控制 token 预算。

**基准**：本地 clone HEAD = `c66b9155`。对照 docs/zh/concepts/03-context-layers.md、06-extraction.md；行号均已在本地源码核实。

---

## 1. 三层定义与存储形态

| 层级 | 名称 | 存储形式 | 默认正文上限 | 配置键 | 用途 |
|---|---|---|---|---|---|
| L0 | abstract | 目录内 `.abstract.md` | 256 字符 | `semantic.abstract_max_chars` | 向量召回、快速过滤 |
| L1 | overview | 目录内 `.overview.md` | 4000 字符 | `semantic.overview_max_chars` | rerank、内容导航 |
| L2 | detail | 原始文件/子目录 | 无统一上限 | — | 完整内容、按需加载 |

默认值钉版：`openviking_cli/utils/config/parser_config.py` L759 `abstract_max_chars: int = 256`、L762 `overview_max_chars: int = 4000`、L753 `overview_sample_limit: int = 32`。枚举定义在 `openviking/core/context.py` L34-39：`ContextLevel.ABSTRACT=0 / OVERVIEW=1 / DETAIL=2`——向量库里每条 Context 记录自带 level 字段，同一路径最多占 3 个向量位。

一个**关键澄清**（docs/zh/concepts/03 L13）：L0/L1 是**目录级** sidecar，不是 per-file 伴生文件。文件摘要先聚合进所在目录的 L1，目录树再逐级向上聚合。普通 `ls` 默认隐藏它们（L76），且二者**允许只存在一个**——`mkdir(description=...)` 只建 L0 也是合法状态（L15）。

目录形态：

```text
viking://resources/docs/auth/
├── .abstract.md     # L0，隐藏 sidecar
├── .overview.md     # L1，隐藏 sidecar
├── oauth.md         # L2
└── jwt.md           # L2
```

## 2. 生成机制：写入时异步，不是读时惰性

### 2.1 三段流水线

```mermaid
flowchart LR
    A["输入文件<br/>PDF/HTML/代码..."] -->|"Parser（无 LLM）<br/>智能分割 ≤1024 tok"| B["viking://temp/xxx"]
    B -->|"TreeBuilder.finalize_from_temp<br/>5 阶段：移动+入队"| C["viking://resources/..."
    C -->|"SemanticMsg 入队"| D["SemanticQueue<br/>（LLM 异步）"]
    D -->|"自底向上"| E["叶子目录 L1 → L0<br/>→ 父目录 → 根边界"]
    E -->|"EmbeddingQueue"| F["向量库<br/>L0/L1/文件向量"]
```

设计原则（docs/zh/concepts/06 L14）：**解析与语义分离**——Parser 纯 CPU 不调 LLM，用户 `add_resource` 的同步路径只到入队为止，LLM 成本全部移到后台。所以「生成时机」的准确回答是：**写入时排队、队列中异步生成**；`--wait` 只是轮询任务状态，不改变异步本质。

### 2.2 单目录的 6 步处理（semantic_processor.py）

`SemanticProcessor`（`openviking/storage/queuefs/semantic_processor.py`，类 docstring L79："generates .abstract.md and .overview.md bottom-up"）对每个目录：

1. 并发生成文件摘要（限并发 10）；
2. 收集子目录已生成的 `.abstract.md`（只取正文，frontmatter 不进 prompt——docs/zh/concepts/03 L124）；
3. LLM 生成 L1 `.overview.md`；
4. **从 L1 提取 L0**；
5. 以 OKF Markdown（YAML frontmatter + 正文）写入；
6. 向量化入 EmbeddingQueue。

步骤 4 的实现是 `_extract_abstract_from_overview`（semantic_processor.py **L1102-1124**）：跳过头部 `#` 行，取 H1 之后到第一个 `##` 之前的非空行——L0 是 L1 的结构化切片，**不是独立调用 LLM**。这决定了 L0/L1 天然一致，也节省一半生成成本。尺寸强制在 `_enforce_size_limits`（**L1132-1139**）：超限时走 `_truncate_generated_text`（**L1072-1100**）——按句子边界截断（中英文句末符都在正则 L1081），绝不截半个句子。

### 2.3 队列侧的合流与降级

`on_dequeue`（semantic_processor.py L315-454）有两个值得记录的防御：

- **陈旧消息降级**（L346-359）：同目录新消息已入队时，旧消息不整体跳过，而是**降级为仅文件工作**（`aggregate_directory=False`）——目录聚合让最新消息做，但旧消息改过的文件仍要单独摘要/向量化，避免丢文件级处理。
- **熔断**（L370-382）：LLM API 已知故障时消息重新入队而非丢弃。

### 2.4 Freshness、稳定采样与父级冒泡

- 每次生成记录 `freshness`（`abstract_overview.py` L340 `freshness_metadata`）：`total/sampled/unsampled_entries` + `pending_child_changes`，**只统计直接子项**，不是递归子树（docs/zh/concepts/03 L142-147）；
- 直接子项 > `overview_sample_limit`(32) 时用 `deterministic_sample`（abstract_overview.py L327）做**确定性保序采样**——同目录反复刷新选相同样本，避免正文和 git diff 抖动；
- 处理成功后 `_enqueue_parent_refresh`（semantic_processor.py **L245-313**）向上冒泡：以 `generation_trigger="parent_refresh"` 给父目录入队新 SemanticMsg（L292-312），直到 namespace 根边界（L257-260 的 `{"viking://", "viking:"}` 停止条件）。

docs/zh/concepts/03 L155-157 与 06 L132-134 都留着同一条 **TODO：当前每次成功任务都无条件冒泡**，热点深层目录会重复刷新+向上写放大；计划用 freshness 数据做合并/阈值/时间窗节流。读源码确认属实——这是当前实现的已知债。

## 3. OKF sidecar 格式与读写保护

新生成的 L0/L1 是"最小 OKF Markdown"：YAML frontmatter（`directory` / `source` / `generated_by` / `freshness` 四个已知字段）+ 可见正文。解析/渲染在 `abstract_overview.py`：`parse_abstract_overview`（**L165**）、`render_abstract_overview`（**L213**）。未知字段**静默丢弃**，YAML 损坏/缺 `directory`/类型错误显式失败（docs/zh/concepts/03 L110）。

**不同读取表面返回不同视图**（这是最容易踩的坑）：

| 访问方式 | 返回 |
|---|---|
| `client.abstract()/overview()` | 仅正文 |
| find / rerank preview | 仅正文 |
| `ls output=agent` / tree | 仅正文 |
| 直接 `read(".abstract.md")` | 完整 frontmatter+正文 |

**写保护**（docs/zh/concepts/03 L159-168，代码在 `prepare_abstract_overview_write` abstract_overview.py L241 + `write_abstract_overview` L364）：

- 公共 `write` **不能创建**新 sidecar，只能更新已存在的；
- 只提交正文 → 保留旧 metadata 重拼 canonical OKF；
- 提交完整 OKF → 已知字段必须与现值一致，改受保护字段即失败；
- 正文更新只重建向量、**不触发语义重生成**——防止刚写的正文被后台任务覆盖。

**embedding 输入白名单**（abstract_overview.py L293-318 `body_for_embedding`/`embedding_text_for_body`）：只有正文 + `directory` 一个元数据字段进向量；`source/generated_by/freshness` 一律不进（docs/zh/concepts/03 L126-138）。正常向量化与 admin `vectors_only` reindex 同策略，保证重建索引不改变检索输入。

## 4. 检索中的按需加载与 token 经济学

检索路径上三层各司其职：

1. **L0 进向量库**：召回阶段 query 向量 vs L0 向量，一个目录只花 ~100 tokens 的嵌入成本（docs/zh/concepts/04 L349-350 以 token 计：L0 ≈100 tok、L1 ≈2k tok；concepts/03 以字符计 256/4000——两处口径并存，中文场景 256 字符 ≈ 256+ tokens，英文 ≈ 64 tokens，实际介于两者之间）；
2. **L1 做 rerank**：候选目录用 4000 字符概览进 rerank 模型（rerank scalar 是纯 L1 正文，docs/zh/concepts/03 L138），决定"要不要下钻"；
3. **L2 按需 read**：只有最终选中的文件才 `read()` 全文。

`ls output=agent` 的目录浏览走 `_batch_fetch_abstracts`（`openviking/storage/viking_fs/_ops.py` **L662-715**）：固定 worker 池批量取 L0，目录没生成好时返回占位符 `"[.abstract.md is not ready]"`（L706）而非报错；截断到 `abs_limit`（默认 256，L733）。

**经济账**：一个 1000 文件、5 层深的资源树，全量 L2 塞进上下文是 10⁶ tokens 级；而「L0 树导航」只需每目录 100 tok——Agent 先 `tree`/`ls -a` 看 L0 定位，再读选中目录 L1，最后 read 单文件 L2。这正是 04-viking-uri.md L51 所说"摒弃扁平数据库思维"的落点：**确定性路径导航（零向量成本）+ 语义召回（L0）+ 深阅读（L2）三段式**。

**多模态**：图片/音视频不建 per-file sidecar，只生成文本摘要后作为普通文件摘要参与目录聚合（docs/zh/concepts/03 L178）。

## 5. 设计权衡与坑

- **为什么 sidecar 挂目录不挂文件**：向量检索的最小决策单元是"目录值不值得下钻"，不是"文件第 7 段说了什么"。目录级聚合把 sidecar 数量从 O(files) 降到 O(dirs)，冒泡成本可控；代价是**单文件精度让位给目录粒度**——精确到文件的语义必须靠 L2 文件向量补。
- **为什么 L0 从 L1 提取而不是独立生成**：省一半 LLM 调用 + 层间天然一致；代价是 L1 写得差（H1 后没简介段）时 L0 会空——`_extract_abstract_from_overview` 对格式不良输入返回空串（L1102-1124 无 fallback）。
- **坑 1：不要假设每个目录都有双 sidecar**。`mkdir` 先建 L0、语义任务失败只剩 L2、采样降级——都是合法状态。读侧代码要处理"层不存在"（`_ops.py` L706 的占位符就是干这个的）。
- **坑 2：无条件父级冒泡是真实的写放大源**。深层目录高频写入时，祖先目录会被反复重新摘要直到根。TODO（docs L155-157）未落地前，热点路径要自己控制写入频率。
- **坑 3：写 sidecar 的 metadata 是受保护契约**。想通过公共 write 改 `freshness`/`generated_by` 会失败；运维侧改 sidecar 只能动正文，元数据只能由 SemanticProcessor 写。
- **坑 4：字符上限 ≠ token 上限**。中文目录的 256 字符 L0 实际 token 数可能是英文的 3-4 倍，做上下文预算时按语言实测，别按"100 tokens"想当然。

## 6. 与其他模块的关系

- **viking:// URI**（`01-viking-uri.md`）：sidecar 是目录 URI 下的隐藏特殊文件；`VikingURI.parent` 驱动冒泡链。
- **ragfs pathlock**（`04`/`05`）：sidecar 写回前取目录 ExactPathLock + `coalesce_version` 淘汰旧任务（docs/zh/concepts/09 L177-195），是"派生文件并发保护"的专门一层。
- **快照/多版本**（`05-transactions-snapshots.md`）：restore 后 `.abstract.md`/`.overview.md` 被归类为"目录标记"，只重算该目录 L0/L1 向量（_snapshot.py L210-214）。
- **上下文编译**（`03-context-compilation.md`）：compile 产物是新的 L2 目录树，其 L0/L1 由本机制的常规流水线自动补齐——编译不自带摘要逻辑。

## 📌 下一步阅读

1. `03-context-compilation.md`——把 L0/L1/L2 树当作"编译目标"的高阶用法；
2. `openviking/storage/abstract_overview.py` 全文（634 行）——OKF 解析/渲染/白名单的唯一实现；
3. docs/zh/concepts/07-retrieval.md——`MatchedContext.abstract`（L172）如何把 L0 直接作为检索结果的一等字段。
