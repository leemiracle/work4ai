# 07 · Legacy 考古层：config.py + modules/ LlamaIndex 原型与两代控制台

> 对象：仓根 `config.py`、`modules/`（8 个 .py + 7 个空 `__init__.py`）、`benchmark/` vendored 三件、仓根 `static/index.html` vs `app.html`。这是 DataMind v0.1 原型的化石层——`requirements-legacy.txt` 开头注释明说："Legacy v0.1 compatibility dependencies only ... the original main.py / server.py / modules/* prototype can still be reproduced"。

## 一、角色定位

DataMind 现在的主干是 `datamind/` 包（v2.1.0 统一 Codex host），而仓根还躺着一代完全不同的前身：**一套基于 LlamaIndex 的单进程 RAG 原型**。它的入口、配置、UI 与新栈零共享——新人若从仓根开始读，会以为这是个 LlamaIndex 项目，然后发现 `datamind/` 里另有一整套 232 行的 MCP server、LanceDB/Chroma 双栈和 CodexHost。本篇把化石层逐块标定，防止把两代代码混读。

注意一个易错点：仓根 `main.py`（L1 兼容启动器，L5 `from datamind.cli import app`）与 `server.py`（L15 `from datamind.server import app`）**已经不再是原型本体**，而是转发到新栈的 shim。真正的 v0.1 遗物是 `config.py` + `modules/` + `static/index.html`。

## 二、内部结构

**config.py（86 行）**：一个 pydantic-settings 的 `Settings` 类（L26），字段覆盖 LLM（L28-30）、Embedding（L33-37，默认 `text-embedding-3-small`）、Retriever（L40-42，`retriever_mode` 可选 simple/multi_query）、Memory（L45-46）、多模态（L49-53，clip/vlm_describe 两模式）、Data Profile（L56）。路径全部用 `@property` 从 `base_dir` 推导：`data_dir`（L64-66）落在 `data/profiles/{data_profile}/`、`storage_dir`（L74-76）按 profile 隔离。L86 `settings = Settings()` 模块级单例。

**modules/ 七包**：agent / database / graphrag / memory / rag / skills 六个子包加 `modules` 自身，**七个 `__init__.py` 全部是 0 字节空文件**——纯命名空间标记，没有任何 re-export。真实代码在各子包的模块文件里：`agent/agent.py`（192 行，L15-18 import `FunctionAgent`/`QueryEngineTool`/`RetrieverQueryEngine`）、`rag/indexer.py`（393 行）与 `rag/retriever.py`（144 行）、`graphrag/graph_rag.py`（202 行，L19-21 用 `SimpleLLMPathExtractor` + `SimplePropertyGraphStore`）、`skills/knowledge.py`（95 行，L20 `from llama_index.vector_stores.chroma import ChromaVectorStore`）、`database/database.py`（158 行，L16-17 `SQLDatabase` + `NLSQLTableQueryEngine`）、`memory/memory.py`（仅 20 行，L8 `from llama_index.core.memory import Memory`）。

**关键特征**：所有模块用 `from config import settings`（agent.py:20、database.py:19、graph_rag.py:23、memory.py:10、indexer.py:31、retriever.py:23、knowledge.py:22）——裸模块名 `config`，要求以仓根为工作目录运行（或仓根在 `sys.path`），这与新栈 `from datamind.config import ...` 的包内绝对导入是两个世界。

**benchmark/ 的三层混居**：不是整个目录都是 legacy——`run.py` 是新栈 runner（L21 `from datamind.host import CodexHost`）；`evaluate.py` 是独立的 EM/F1 评估；真正的 vendored 是 `metrics/golden_answer_metrics.py` + `models/embedding_models.py` + `models/llm_judges.py` 三件，拷贝自 VMware 的 open-rag-eval 项目。

## 三、外部连接

- **vendored 互引走外部包名**：`benchmark/metrics/golden_answer_metrics.py` L15-17 三条导入是 `from open_rag_eval.metrics.base_metrics import GoldenAnswerMetric`、`from open_rag_eval.models.embedding_models import EmbeddingModel`、`from open_rag_eval.models.llm_judges import LLMJudgeModel`——尽管 `models/embedding_models.py` 就在它隔壁两级的本仓目录里，导入路径却指向**外部包** `open_rag_eval.*`。这意味着：不 pip 安装 open-rag-eval，这三个文件谁的代码也跑不起来；本仓拷贝是"参考副本"，不是接线实现。`models/llm_judges.py` 顶部还要求 openai/google-genai/anthropic/together 四家 SDK（L8-12），依赖面远超本仓。
- **legacy 依赖清单独立**：`requirements-legacy.txt` 列 llama-index-core、llama-index-llms-openai、llama-index-vector-stores-chroma、chromadb 等 14 项，与 `pyproject.toml` 的 v1.0 栈完全分离——装新栈不需要 LlamaIndex。
- **UI 静态的双份拷贝**：仓根 `static/` 与 `datamind/static/` 里的 `app.html`、`markdown.js` 经 diff 完全相同；`datamind/static/` 是随 wheel 打包的正本（`datamind/server.py` L94 用 `_STATIC_DIR / "app.html"` 服务），仓根那份是历史位置的残留拷贝。
- 仓根 `benchmark.py` 是 32 行 shim：L25 `sys.path.insert(0, ...)` 补路径、L27 `from benchmark.run import main`、L30-31 打印迁移 WARN 提示改用 `python -m benchmark.run`。

## 四、数据流

v0.1 原型的数据流可从 `static/index.html`（23KB 旧控制台）的 fetch 调用反推：L190/191/223/230/238 打 `/api/skills*`（技能知识与上传重建）、L247/267 打 `/api/memory`（会话记忆读写）、L273/297/304 打 `/api/rag*`（文档列表/上传/删除）——对应 modules/skills + modules/memory + modules/rag 三块，由 LlamaIndex 的 FastAPI 服务端承接，Chroma 做向量库，profile 目录存数据。

新栈 `static/app.html`（47KB）完全不同：主体只打一个 `/api/upload`（L1303），问答走统一 host 的流式端点，upload→evidence→receipt 是三段式 UI。**两代控制台并存于同一个 `static/` 目录，标题都叫 `<title>DataMind</title>`（index.html:6 与 app.html:6），只有看 fetch 端点才能分辨年代**——`/api/skills/knowledge` 是 v0.1 的化石指纹，`/api/upload` 是 2.x 的活体指纹。

## 五、设计决策（含批判）

1. **保留化石而非删除**：作者刻意留下 v0.1 原型 + 独立 requirements，动机是"可复现"。代价是仓根目录严重污染——新人第一眼看到的 `config.py`/`modules/` 与 `pyproject.toml` 声明的包毫无关系。
2. **vendored 不接线**：open-rag-eval 三件拷进来了但 import 仍指外部包名，等于"想用还没用"。批判：要么改成相对导入真正收编，要么删掉拷贝在 README 里给上游链接——现在这样最迷惑。
3. **shim 层统一模式**：main.py/server.py/benchmark.py 全是"兼容名 → 新实现"的转发（`docs/LEGACY_RUNTIME.md` 给出完整迁移表：`build_datamind(Settings())` → `CodexHost(DataSettings())`），这是 v2.0 删除 StoreAgent/RetrieveAgent（CHANGELOG 2.0.0 节）时留下的迁移缓冲。
4. **两代 Settings 同名不同物**：仓根 `config.py` 的 Settings 与 `datamind/config.py` 的 Settings 字段几乎不重叠，仅 env 风格呼应。批判：`from config import settings` 这种顶层裸导入在包安装场景下极易与其它包的 config 冲突，也是它只能活在"仓根运行" niche 的原因。

## 六、新人提示

- 读新栈代码请直接进 `datamind/`，**忽略仓根 `config.py` 和 `modules/`**，除非你专门考古 v0.1。
- 想跑 legacy 原型：`pip install -r requirements-legacy.txt` 后在仓根目录运行（裸 `import config` 依赖 cwd）；它与新栈的 `datamind/` 数据目录可能重叠（都往 `data/profiles/` 写），建议隔离环境。
- 判断一个 HTML/端点属于哪代：找 `/api/skills/knowledge`（v0.1）或 `/api/upload`+receipt（2.x）。
- `benchmark/models/`、`benchmark/metrics/golden_answer_metrics.py` 在没有安装 `open-rag-eval` 时 import 即炸，别被 CI 未跑它们迷惑——CI 的 pytest 只收集 `datamind/tests` 与 `plugins/datamind-context/tests`（`python-ci.yml` L35）。
- 修改 `datamind/static/app.html` 后记得同步仓根 `static/` 那份（或干脆确认它已无人引用再删），两份现在是手工保持一致的。

行号锚：config.py:26/64-76/86 · modules/agent/agent.py:15-20 · modules/skills/knowledge.py:20-22 · modules/memory/memory.py:8-10 · benchmark/metrics/golden_answer_metrics.py:15-17 · benchmark/run.py:21 · benchmark.py:25-31 · static/index.html:6/190-304 · static/app.html:6/1303 · datamind/server.py:94 · main.py:1-9 · server.py:14-20 · requirements-legacy.txt:1-6 · docs/LEGACY_RUNTIME.md（迁移表）
