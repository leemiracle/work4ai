# 11 · scripts 工具线：hello 冒烟家族、seed 语料与 markdown.js

> 对象：`datamind/scripts/`（14 个文件）+ 仓根 `scripts/`（4 个）+ `static/markdown.js`。这条线是"装完第一分钟"与"演示前五分钟"的操作面：冒烟脚本验栈通不通，seed 脚本造可问的数据，markdown.js 让浏览器端能渲染结果。

## 一、角色定位

DataMind 的 hello 家族解决新人最痛的两件事：**装完不知道能不能用**、**想试没有数据**。它分成三代入口——v0.x 时代各能力各有入口（hello_db/hello_kb/...），1.2/2.0 转向统一 Codex host 后 `hello_codex.py` 成为真入口，旧入口名降级为兼容 shim；`seed_enterprise_demo.py` 专门造一个跨 KB/图/SQL 三后端的"企业"数据集，让多跳问题（如"哪些 Q4 事故打到了高绩效员工负责的团队？"——docstring L10-12 原话）真的需要三个后端协同才能答。仓根 `scripts/` 则是 CI 与插件安装的操作脚本（10/09 篇已覆盖 ci_required_tests/ci_smoke_installed/install_codex_plugin，本篇聚焦 start_ccr.sh 之外的工具线全貌）。

## 二、内部结构

**入口代际**：`hello_codex.py`（15 行）是真入口——L4-5 `from datamind.config import DataSettings` + `from datamind.host import CodexHost`，L7 `host=CodexHost(DataSettings())`，L10 `host.query('Reply with exactly pong. Do not call tools.')` 并断言回答含 pong（L11-12），finally 里 `aclose()`。**四个 3 行同构 shim**——`hello_agent.py`、`hello_agent_sdk.py`、`hello_sdk.py`、`hello_sdk_native.py`——内容一字不差：`from datamind.scripts.hello_codex import main`，docstring 都是 "Compatibility command name; now runs the official main Codex host"。这四个名字对应已删除的历史后端（native loop、Claude SDK、CCR 适配器），是 v2.0 删 StoreAgent/RetrieveAgent 时代的入口化石。`hello_enterprise.py`（13 行）是第五个小变体：L6 `cfg.data.profile='enterprise_demo'` 后用同一个 CodexHost 问企业数据。

**六冒烟（全 `_main` 延迟 import）**：`hello_db.py`（150 行）、`hello_kb.py`（136 行）、`hello_hooks.py`（150 行）、`hello_memory.py`（125 行）、`hello_graph.py`（105 行）、`hello_skills.py`（86 行）。统一骨架：模块顶层只 import stdlib，`async def _main()` 内部才 import 重依赖——hello_db L38-44（anthropic+db 构建+safeguard+Settings+logging+ToolRegistry）、hello_kb L54-59、hello_graph L28-31、hello_hooks L41-49、hello_memory L37-42、hello_skills L37-40。**这样 `python -m datamind.scripts.hello_skills` 在缺 anthropic 的环境也能先打印用法/凭据检查再优雅退出**（hello_db L34-36 的 API_KEY 检查在 import anthropic 之前）。每个脚本自带一次性 profile：hello_db L29-32 把 `DATAMIND__DATA__PROFILE` 设成 `hello_db_demo`、方言 sqlite、并 pop 掉外部 DSN，保证不污染真实 profile。hello_db 的演练序列最有代表性：L66-97 用服务持有的同一 engine 建 employees/projects 两表插种子数据 → L104 db_list_tables → L108 db_describe_table → L113 聚合 SQL → **L120-126 断言 `DELETE FROM employees` 被 DestructiveSQLError 拒绝**（safeguard 的冒烟级验证）→ L130 db_query_nl 走真网关 → L138 `tools.as_anthropic_tools()` 快照工具 schema。

**seed_enterprise_demo.py（1019 行）**：头部 docstring 声明规模（L5-8：KB 18 篇 markdown 六类中英混合、图约 60 节点 110 边、DB 6 表 180 行带外键）与动机（原 hello_agent_demo 只有 2 文档 4 边 3 行，撑不起多跳推理）。`_main()`（L957）的装配动作：L959-964 把 LLM 凭据镜像给 embedding（仅当后者未设）；L966 设 `DATAMIND__DATA__PROFILE=enterprise_demo`；**L968 `from datamind.data_plane import build_data_plane`**——千行脚本的核心 import 就这一条，同样延迟到 _main 内；L980 `_reset_profile` 清场（L900 的清理清单：`chroma`、`chroma_skills`、`demo.db`、`graph.json`、`memory.db` 五个名字——幂等重跑的保证）；L984 起依次写 KB 文档、图三元组、DB 表。`verify_sqlite_demo.py`（123 行）是其无网络对照面：不碰任何 API，纯 SQLite 确定性检查（CI test job L38 每次必跑）。

**markdown.js（136 行 UMD）**：L1-4 标准 UMD 头——`(function (root, factory) {... module.exports = api; root.DataMindMarkdown = api; })`，CommonJS 与浏览器全局双兼容；核心两个函数 `escapeHtml`（L8-14）与 `renderMarkdown`，尾行 `return { escapeHtml, renderMarkdown }`。它服务 app.html 的回答渲染。**tree-sitter 对它零提取**：整文件是一对无 import/export 语句的 IIFE，静态扫描器提取不到任何依赖边——知识图谱里该文件的连接关系全靠人工补录（本 explain 系列即补录产物）。

## 三、外部连接

- hello_codex/hello_enterprise → `datamind/host.py`（CodexHost）；六冒烟 → 各 capabilities 的 build_* 工厂；seed → `datamind/data_plane.py`（build_data_plane）→ runtime 装配（08 篇）。
- `verify_sqlite_demo` 被 CI test job 收编（python-ci.yml L38）；六冒烟不入 CI——它们要真凭据，属于手工验收层。
- 仓根 `benchmark.py` shim 与 `datamind/scripts/__init__.py`（1 行）保证 `python -m datamind.scripts.hello_db` 包路径成立。
- markdown.js 同时存在于仓根 `static/` 与 `datamind/static/`（两份相同，见 07 篇），wheel 只打包后者。

## 四、数据流

冒烟流（hello_db 型）：env 引导一次性 profile → 凭据预检 → 延迟 import → build service/ToolRegistry → 演练工具序列 → 打印结果与 OK。seed 流：清空 enterprise_demo profile → 写 18 篇 md 到 data 目录 → 写 4 个三元组文件 → 建 6 表插数据 → 提示跑 `DATAMIND__DATA__PROFILE=enterprise_demo python -m datamind ingest`（docstring L16-18）把源灌进 KB/图/DB → 之后 `datamind chat` 或 hello_enterprise 即可提问。markdown.js 流：app.html 收到流式回答 → 调 `DataMindMarkdown.renderMarkdown(text)` → escapeHtml 先行防注入 → 输出安全 HTML 片段。

## 五、设计决策（含批判）

1. **shim 保名不保义**：四个 3 行 shim 让旧文档/肌肉记忆不 404，但代价是 grep `hello_sdk` 会命中三个"根本不同的历史后端"的同名壳——docstring 一句话交代去向已经是最低成本方案。批判：没有 deprecation warning 输出，用户跑 hello_sdk 得到的其实是 codex 行为，静默语义漂移。
2. **冒烟脚本里的断言是真测试**（hello_db L11-12/L120-126）：连 destructive 拒绝都验——批判上它又不在 CI 里（需凭据），形成"最像 e2e 的代码不在 e2e 里"的错位；verify_sqlite_demo 是对此的部分补救。
3. **seed 语料设计为"必须跨后端"**：语料把同一实体（人物/项目/事故）同时写进 md（KB）、三元组（图）、表（DB），让单后端检索必然答不全——这是评测意识的体现。批判：1019 行手写语料内嵌 py 字符串，改一次规模要动核心逻辑；且 `--profile` 等参数没有 CLI 化，重跑必须依赖 env。
4. **凭据镜像**（L959-964）是贴心的默认，但也意味着 embedding 可能默默吃到 LLM 的 key——排障时要记得这层隐式继承。
5. markdown.js 手写渲染器而不引 marked/markdown-it：零依赖、体积极小、escape 先行安全可控；代价是方言覆盖有限（表格/代码块的边角行为需自查）。

## 六、新人提示

- 装完先跑 `python -m datamind.scripts.hello_codex`（要凭据）；没凭据跑 `python -m datamind.scripts.verify_sqlite_demo`（不要）。
- 想本地复现"企业演示"：`python -m datamind.scripts.seed_enterprise_demo` → `DATAMIND__DATA__PROFILE=enterprise_demo python -m datamind ingest` → `hello_enterprise`。重跑 seed 会清 profile（L980），别在 enterprise_demo 里存真数据。
- 遇到 `ModuleNotFoundError: anthropic` 再看报错行：六冒烟的 import 都在 _main 里，报错说明凭据预检已过、是环境缺包——`pip install anthropic` 即可。
- 给新能力加冒烟请复制 hello_graph.py 的骨架（env 预设 → 凭据检查 → 延迟 import → ToolRegistry 演练 → 返回码），并保持"顶层零重依赖"的约定。
- 改 app.html 渲染相关行为时，markdown.js 是同步纯函数，直接在浏览器 console 用 `DataMindMarkdown.renderMarkdown('**x**')` 即可调试，不必起服务。

行号锚：hello_codex.py:4-5/7/10-12 · hello_agent.py（3 行 shim 全文） · hello_enterprise.py:6 · hello_db.py:28-32/34-36/38-44/66-97/104-135/120-126/138 · hello_graph.py:19/28-31 · hello_hooks.py:28/41-49 · hello_kb.py:30/54-59 · hello_memory.py:23/37-42 · hello_skills.py:21/37-40 · seed_enterprise_demo.py:5-12/900/957/959-964/966/968/980/984 · static/markdown.js:1-4/8-14/135 · datamind/static/markdown.js（wheel 副本）
