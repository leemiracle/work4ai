# 03 · 教程线、SDK 文档与官方公告：规范的学习路径层

> 区域：`docs/tutorials/python/`（8 步）+ `docs/sdk/` + `docs/blog/` + `scripts/build_docs.sh` / `scripts/build_sdk_docs.sh` 构建链
> 仓根：`/usr-data/data2/repos/aaif-projects/repos/A2A`。本文所有行号锚均经 grep/Read 从源文件核实（2026-10-24）。

## 角色定位

在知识图谱的 8 层架构里，本篇覆盖 L03「Python 教程线」（9 节点 = 教程 8 页 + `tutorials/index.md`）与 L04「SDK 文档与官方公告」（8 节点 = `docs/sdk/` 4 文件 + `docs/blog/` 4 文件）。它们与 L01 协议规范本体（`docs/specification.md`，3639 行 211 节）构成一个精确的三级学习漏斗：

1. **规范本体**（L01，normative）：只规定"是什么、必须怎样"，不管你怎么学；
2. **教程线**（L03，学习路径）：把规范里的对象按"先能跑起来、再讲清楚"的顺序重排成 8 步，是规范唯一官方认可的导览入口——`docs/llms.txt:36` 明确写它 "Eight-step tutorial that builds a working A2A agent from scratch"；
3. **SDK API 参考**（L04，生成物）：`docs/sdk/python/api/` 整个目录被 `.gitignore:214` 排除在版本库外，是 `build_sdk_docs.sh` 构建时从 PyPI 安装的 `a2a-sdk` 包自动生成的 Sphinx 文档——规范讲协议、教程讲用法、API 参考讲签名，三者互不重复。

关键的分工设计是**代码与文档彻底分离**：教程 8 步没有一行示例代码存在本仓。第 2 步就让读者 `git clone https://github.com/a2aproject/a2a-samples.git`（`2-setup.md:15`），后续所有代码展示全部用 `--8<--` 语法按命名锚从 a2a-samples 的 raw.githubusercontent.com 地址远程嵌入（共 10 处，见"外部连接"节）。`docs/sdk/index.md:14` 同样把聚合示例仓指向 a2a-samples。也就是说：本仓 = 协议 + 文档骨架，a2a-samples = 全部可运行代码。

blog 子区（L04 后半）是时间线叙事层：3 篇公告对应项目三个里程碑。**勘误**：任务书预期"4 篇官方公告"，实测 `docs/blog/posts/` 只有 3 个文件（`announcing-1.0.md` / `a2a-joins-aaif.md` / `introducing-a2a-cli.md`，ls 实证），第 4 篇不存在。

## 内部结构

### 教程 8 步的递进设计

8 步的编排遵循"环境→静态描述→逻辑→服务端→客户端→进阶能力"的认知曲线，`1-introduction.md:23-30` 的编号清单与 `mkdocs.yml:47-54` 的 nav 一一对应：

| 步 | 文件 | 职责 | 关键锚 |
|---|---|---|---|
| 1 | `1-introduction.md` | 导言 + 7 条学习目标 + 全目录 | `:5` 声明"echo"A2A server 起点；`:7-15` 目标清单 |
| 2 | `2-setup.md` | Python 3.10+、clone a2a-samples、装 SDK | `:5` 版本要求；`:44` `pip install -r samples/python/requirements.txt`；`:52` `import a2a` 验证 |
| 3 | `3-agent-skills-and-card.md` | 静态自描述：AgentSkill + AgentCard | `:11` 属性"defined in `a2a.types`"；`:31` `.well-known/agent-card.json` |
| 4 | `4-agent-executor.md` | 业务逻辑接口 | `:3` 抽象基类 `a2a.server.agent_execution.AgentExecutor`；`:9-10` `execute`/`cancel` 两方法 |
| 5 | `5-start-server.md` | 组装并启动服务端 | `:21` `DefaultRequestHandler` 三件套；`:29-30` 两类路由工厂 |
| 6 | `6-interact-with-server.md` | 客户端全流程（本批最长页） | `:46` `A2ACardResolver`；`:64` `streaming=True` |
| 7 | `7-streaming-and-multiturn.md` | LangGraph 进阶：LLM/状态/流式/多轮 | `:3` 指向 langgraph 示例；`:79-86` INPUT_REQUIRED 多轮 |
| 8 | `8-next-steps.md` | 总结 + 去向 | `:21` 链回 `../../specification.md`；`:23-26` 四个专题页 |

递进的精妙处在于第 4 步的五步事件流（`4-agent-executor.md:44-54`）：建任务 → `TASK_STATE_WORKING` → `agent.invoke()` → `TaskArtifactUpdateEvent` 结果 → `TASK_STATE_COMPLETED` 收尾，恰好是第 6 步客户端"流式四块"期望输出（`6-interact-with-server.md:74`）的镜像——服务端怎么 enqueue，客户端就怎么收。第 4 步结尾一句定位（`:56`）"bridge between the A2A protocol and your agent's specific logic" 是理解整个 SDK 分层的钥匙。

### SDK 文档结构与生成链

`docs/sdk/` 只有 4 个源文件：`index.md` 是六语言 SDK 仓库表（`:5-12`，Python/Go/Java/JS/C#/.NET/Rust 六行外链）；`python.md` 全文仅 7 行，front-matter `redirect: python/api/index.html`（`:2`）把读者送去生成产物；`python/conf.py` + `python/index.rst` 是 Sphinx 源头——conf.py 声明 `project = 'a2a-sdk'`、`copyright = '2026, The Linux Foundation'`（`:3-5`），启用 autodoc/autosummary/napoleon/myst_parser 四扩展（`:10-13`），`autosummary_generate = True`（`:17`），主题 furo（`:31`），成员排序 alphabetical（`:33`）；index.rst 一行 `pip install a2a-sdk`（`:8`）加 `modules` toctree（`:10-13`）。

生成链两级串联：外层 `build_docs.sh` 先做 schema 新鲜度检查——比较 `specification/a2a.proto` 与 `specification/json/a2a.json` 的 mtime（`:16-29` 的 `regen_needed()`，兼容 Darwin/Linux 两种 stat 语法），陈旧则调 `proto_to_json_schema.sh` 重生成（`:31-43`），再把 schema 与 proto 拷进 `docs/spec/` 供 MkDocs 引用（`:46-60`）；随后调用内层 `build_sdk_docs.sh`（`:63-69`）；最后 `mike deploy` 或 `mkdocs build`（`:76-83`），收尾把仓外 `adrs/` 拷进 site（`:85-96`）。内层脚本值得细读：它**新建干净 venv 后从 PyPI 安装 `a2a-sdk`**（`build_sdk_docs.sh:17-18` venv、`:26` `uv pip install "${PYPI_PACKAGE_NAME}"`），再对安装路径跑 `sphinx-apidoc -f -e`（`:39`），同时产出 html 与 text 两种格式（`:44-49`），最后把 html 拷进 `docs/sdk/python/api/`（`:53-57`）——所以 mkdocs nav 里挂的 `sdk/python/api/index.html`（`mkdocs.yml:43`）在源仓 checkout 里根本不存在，不跑构建 MkDocs 会缺页。

### blog 时间线叙事

三篇公告按日期构成项目编年：**2026-03-12** `announcing-1.0.md`（`:2`）宣布 v1.0 稳定版，核心卖点是"maturity rather than reinvention"（`:16`）；**2026-08-27** `a2a-joins-aaif.md`（`:2`）宣布加入 AAIF 成为 Growth Stage 项目；**2026-10-01** `introducing-a2a-cli.md`（`:2`）发布 CLI。三篇全部归入 Announcements 分类，`mkdocs.yml:165-167` 的 blog 插件配置 `post_url_format: "{date}/{slug}"` + 每页 2 篇分页，`mkdocs.yml:173` 还保留着 `"announcing-1.0.md": "blog/posts/announcing-1.0.md"` 的历史 URL 重定向（说明该文曾住在仓根）。nav 里 Blog 区只挂 Overview 与外链 Release Notes（`mkdocs.yml:60-62`），单篇靠插件自动进目录。

## 外部连接

**教程→规范的对象锚（批 10 发现复验）**：知识图谱录得 6 条 `related` 边，从教程第 3/4/5/6/7/8 页指向 `document:docs/specification.md`（仅 1、2 两页无此边——环境准备页确实不含协议对象）。批 10 报告的"AgentCard 59 处"口径本次复验为：`grep -c 'AgentCard' docs/specification.md` = **59 行**（子串口径 68 处、词边界口径 30 处——三条口径差异须钉明）。教程所教对象在规范中的落点：Task `specification.md:774`（4.1.1）、TaskState `:786`（4.1.3）、Message `:792`（4.1.4）、Artifact `:810`（4.1.7）、TaskStatusUpdateEvent `:818`（4.2.1）、TaskArtifactUpdateEvent `:824`（4.2.2）、AgentCard `:895`（4.4.1）、AgentSkill `:919`（4.4.5）。教程第 4 步教的事件流顺序，正对应规范 `:210` 的强约束——"stream MUST close when the task reaches a terminal state"。

**`--8<--` 远程 snippet（10 处，全部外指 a2a-samples）**：分布为 3 步 2 处（`:24` `:AgentSkill` 锚、`:44` `:AgentCard` 锚）、4 步 3 处（`:22` `:HelloWorldAgent`、`:33` `:HelloWorldAgentExecutor_init`、`:41` `:HelloWorldAgentExecutor_execute`）、5 步 1 处（`:14` 整文件嵌入 `__main__.py`，无锚）、6 步 3 处（`:43` `:A2ACardResolver`、`:51` `:message_send`、`:61` `:message_stream`）、7 步 1 处（`:63` `:DefaultRequestHandler`）。10 条 URL 全部是 `https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/...`——文档站每次构建都从 a2a-samples 主干实时拉取。

**announcing-1.0 → proto 的 documents 边**：知识图谱录得 `document:docs/blog/posts/announcing-1.0.md -> schema:specification/a2a.proto`（type=documents）。源头实据是 `announcing-1.0.md:33`"The standard builds on industry-proven protocols, including JSON+HTTP, gRPC, and JSON-RPC"与 `:45` 讲 AgentCard 双版本兼容——公告在叙述规范本身，批分析因此把它归为 proto 的文档化伴生。

**sdk_repos.html 同步注释（批 13）**：`.mkdocs/overrides/partials/sdk_repos.html:5` 注释原文"Keep in sync with docs/sdk/index.md."——顶栏七链接行（A2A 本仓 + 六 SDK 仓，`:7-36`）与 `docs/sdk/index.md:5-12` 的表格是手工双维护关系；`mkdocs.yml:65-66` 还注释掉了 repo_url，理由即"the A2A repo is now shown in the SDK links row"。

**其余外部接线**：`docs/llms.txt:12`（Quickstart 条目）、`:25`（CLI 条目直接指回 `docs/blog/posts/introducing-a2a-cli.md`）、`:64-66`（Tutorials/SDKs/Python API 三条目）、`:107`（Blog 条目）把本区全部挂进 LLM 检索清单；`a2a-joins-aaif.md:28` 链回教程第 1 步、`introducing-a2a-cli.md:206` 同时链回 `topics/what-is-a2a.md` 与教程——blog 是教程的流量入口之一。`mkdocs.yml:193-202` 的重定向映射暴露了教程自身的重构史：旧版 10 步 URL（`3-create-project`、`5-add-agent-card`、`9-ollama-agent` 等）被压缩归并到现行 8 步。

## 数据流

一个新人从零到能写流式多轮 agent 的完整数据流（页码即停留顺序）：

1. **入口**：经 `docs/index.md` 或 blog（`a2a-joins-aaif.md:28`）或 llms.txt 进入 `1-introduction.md`，读 7 条目标（`:7-15`）知道终点在哪；
2. **获得代码**：第 2 步 clone a2a-samples（`:15`）并装依赖（`:44`）——从这一刻起，学习者的工作目录是外部仓，本仓只作为文档被阅读；
3. **静态层**：第 3 步读 helloworld 的 `__main__.py` 里 AgentSkill/AgentCard 定义（远程锚 `:24`/`:44`），掌握"agent 如何自描述"——产物是 `/.well-known/agent-card.json` 端点（`:31`）；
4. **逻辑层**：第 4 步实现 `AgentExecutor.execute()`（`4-agent-executor.md:9`），学会往 `EventQueue` 塞五步事件；
5. **组装层**：第 5 步 `DefaultRequestHandler(executor, task_store, agent_card, extended_agent_card)`（`5-start-server.md:21`）+ `create_agent_card_routes`/`create_jsonrpc_routes`（`:29-30`）挂进 Starlette，`uvicorn.run` 起 9999 端口（`:36` 特意强调端口须与 AgentCard 的 `supported_interfaces` 一致）；
6. **消费层**：第 6 步双开终端跑 `test_client.py`，先 `A2ACardResolver.get_agent_card()` 拉卡（`6-interact-with-server.md:46`），再 `create_client` 出非流式/流式两个客户端——非流式 `send_message` 返回单个最终 Task（`:56`），流式同方法名但 ClientConfig 带 `streaming=True`（`:64`），输出四块事件（`:74`），格式是 protobuf text 而非 JSON（`:112` 起 `task { id: ... }`）；
7. **进阶层**：第 7 步换 LangGraph Currency Agent（Gemini，`7-streaming-and-multiturn.md:5`），新增两能力：流式中途 `lastChunk` 标记的 artifact（`:75`）与 `TASK_STATE_INPUT_REQUIRED` 驱动的多轮——客户端带 `taskId`/`contextId` 续发第二消息（`:86`）；
8. **出口**：第 8 步给出分叉路径：深读规范（`:21`）、四个专题页（`:23-26`）、自建 agent（`:29` 实现 AgentExecutor 接口）、社区（`:36-39`）。

教程代码块与 SDK API 的对应是严格 1:1 的：教程第 3 步说属性"defined in `a2a.types`"（`3-agent-skills-and-card.md:11`），第 4 步的 `a2a.server.agent_execution.AgentExecutor`（`:3`），第 5 步的 `create_agent_card_routes`/`create_jsonrpc_routes`/`create_rest_routes` 三工厂（`5-start-server.md:5`）——这些符号的权威定义就在生成产物 `sdk/python/api/` 里（`mkdocs.yml:43` 挂载），教程讲"何时用"、API 参考讲"参数表"，闭环但不重复。

## 设计决策

**教程只做 Python 单语言深线**：`mkdocs.yml:46` nav 里唯一站内教程是 "Quickstart (Python)"，`tutorials/index.md` 的表格虽然还有 Java 等语言区块，但除第 1 行（`:7`）链到站内 8 步外，其余行（如 `:8` ADK facts、`:10` Multi-agent collaboration）全部直链 a2a-samples 外部目录；nav 另挂 DeepLearning.AI 课程外链（`mkdocs.yml:55`）。取舍逻辑（推断，原文未直说）：Python 是 SDK 最成熟的语言线，把一种语言写透比六种语言各写浅表更符合漏斗定位，其余语言用外部示例仓承接。

**远程 snippet 保持单源**：`--8<--` 机制使 a2a-samples 的代码是唯一事实源，教程永远展示主干最新代码，不存在"文档代码落后于示例仓"的漂移（机制是 mkdocs snippet 语法的事实；"为避免漂移而选它"属意图推断，原文无此论述）。代价是构建依赖外网可达 raw.githubusercontent.com，且示例仓重构锚名（如 `:HelloWorldAgentExecutor_execute`）会静默弄空教程代码块——本仓无任何守护。

**SDK API 参考从 PyPI 生成而非本地源码**：`build_sdk_docs.sh:26` 安装的是 PyPI 上的 `a2a-sdk` 包而非仓内代码——本仓根本没有 Python SDK 源码（SDK 在独立的 a2a-python 仓，`docs/sdk/index.md:7`）。这保证文档反映"用户实际 pip install 到的版本"，同时产物目录不入库（`.gitignore:213-214`），仓库不背生成物的版本管理包袱。

**blog 独立于 docs nav 的正文体系**：nav 只挂 `blog/index.md` 与外部 Release Notes（`mkdocs.yml:60-62`），三篇帖子靠 blog 插件自动发现（`:165-167`）。公告因此可按日期自由增删而不动 nav——与教程/SDK 每页手挂 nav 形成对照（事实性对照；"为降低维护成本"为推断）。

**规范对象表用宏渲染**：`specification.md:917-921` 显示 AgentSkill 小节正文仅一行 `{{ proto_to_table("AgentSkill") }}`——规范的数据对象表从 proto 直接生成，与教程的远程 snippet 同属"单源生成"哲学。

## 新人提示

1. **严格按序读**：8 步有硬依赖——第 6 步双终端跑 client 前提是第 5 步服务器还活着（`6-interact-with-server.md:13` 要求"new terminal window"）；跳步最常见的报错就是没先 clone a2a-samples（第 2 步 `:15`）。
2. **分清两个仓**：本仓（A2A）= 规范 + 文档；a2a-samples = 所有能跑的代码。报错在示例代码里，提 issue 去示例仓；协议语义问题才回本仓。
3. **坑：`build_docs.ps1` 不存在（批 14 勘误实锤）**：`specification/json/README.md:179` 的 Windows 段落教你运行 `.\scripts\build_docs.ps1`，但 `scripts/` 目录 ls 实测只有 `.sh` 文件（`build_docs.sh` 等 9 个），全仓 `grep '\.ps1'` 仅命中该 README 自身——Windows 用户照做必失败，实际只有 bash 脚本，需在 WSL/Git Bash 里跑。
4. **坑：教程内部安装口径自相矛盾**：第 2 步教的是 `pip install -r samples/python/requirements.txt`（`2-setup.md:44`），第 7 步却假设"When you installed the SDK from the a2a-samples root using `pip install -e .[dev]`"（`7-streaming-and-multiturn.md:23`）——第 7 步引用了一个从未教过的命令。langgraph 示例缺依赖时，按第 7 步的口径回根目录补装。
5. **坑：SDK API 页面源仓缺失**：`mkdocs.yml:43` 挂的 `sdk/python/api/index.html` 被 `.gitignore:214` 排除，本地不跑 `scripts/build_docs.sh` 就没有这个页面；`sdk/python.md:2` 的 redirect 会指向 404。
6. **坑：blog 只有 3 篇**：任何"4 篇公告"的预期（含本任务书）都应对齐实测 3 篇；Release Notes 在 GitHub 外链（`mkdocs.yml:62`）而非 blog。
7. **提速技巧**：读完第 6 步先看 `:74` 的期望输出再回头看客户端代码，四块事件（task/status_update/artifact_update/status_update）与第 4 步五步 enqueue 的对应关系会一次看懂；第 7 步只想跑多轮 demo 可跳过 LLM 集成细节直读 `:79-86`。深挖协议时，用"外部连接"节的对象行号映射表（spec `:774`-`:919`）从教程直接跳规范对应小节，比通读 3639 行规范快一个量级。
