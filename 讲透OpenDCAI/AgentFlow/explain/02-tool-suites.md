# 02 · 工具面：四工具集、六域 schema 与 MCP client

## 角色定位

`sandbox/server/backends/tools/`（四工具集）+ `sandbox/tool_schemas/`（六域 prompt schema + MCP manifest）+ `sandbox/server/backends/resources/mcp/`（MCP stdio client 与 backend）共同构成 AgentFlow 的「工具面」：agent 能调用的一切能力都在这三处落位。工具集是**执行端**（真正干活），tool_schemas 是**告知端**（把能力翻译成 LLM 可读的 function calling schema），MCP 线则把外部 438 个工具桥接进同一命名空间。执行端与告知端物理分离是这个仓最值得学习的组织方式——同一个工具的两份真相（实现与描述）各有归口。

## 内部结构

**四工具集**（backends/tools/，全部走 BaseApiTool 系）：

- **websearch.py**（592 行）：两个门面工具 `search`（L376）与 `visit`（L421），底下四件套客户端——`SerperClient`（L39，retry_times 默认 5）做 Google 搜索、`JinaClient`（L280）抓网页正文、`Crawl4AiClient`（L314）本地爬取、`LLMSummarizer`（L337）做超长内容摘要。search 支持多 query 并发（ThreadPoolExecutor，L398）；visit 的抓取策略由 `visit_method` 配置切换（jina/crawl4ai，L451），content_limit 默认 50000 字符（L470）。
- **doc_tool.py**（829 行）：DocDancer 线的文档问答工具。核心 `DocTool`（L338）加载 seed 目录下的 `outline.xml`+`all_content.xml`（L353-354）构建 section 索引（L366-369），提供图片/整页图/表格图三种视觉资源取回（L382/L401/L422，均优先 `_compressed.jpg`）；`SearchTool`（L504）做 XML 关键词检索，`ReadTool`（L569）按 section_id 读全文并可调 VLMClient（L217）理解图表，超 20000 字符截断（L602-604）。注意 `seed_path` 的取值优先级：kwargs（来自 seed.jsonl）> 实例配置（L525）。
- **ds_tool.py**（602 行）：数据分析三件套 `InspectDataTool`（L424）/`ReadCsvTool`（L472）/`RunPythonTool`（L485）。RunPythonTool 有一段颇具争议的兜底逻辑：code 为空时执行一段内置的 KMeans 聚类分析脚本（L495-531）并返回 summary——「空代码也出结果」对评测是方便，对调试是噪音。输出可带图片 base64（L539-550），超长输出可走 LLM 摘要（L552-575）。
- **text2sql_tool.py**（118 行）：三工具 `list_databases`/`get_schema`/`execute`（L29/L38/L77）。安全设计有两处硬闸：连接一律只读 URI `file:{abs_path}?mode=ro`（L25-26）；execute 只放行 SELECT/WITH/PRAGMA 开头的语句（L82-84）且 fetchmany(100) 截断（L89）。PRAGMA 表信息与外键通过两条 PRAGMA 查询拼 schema（L57-59）。

**六域 tool_schemas**（tool_schemas/）：rag/web/vm/doc/ds/sql 各一个模块，`__init__.py` L11-17 汇入 `get_tool_schemas()`（L40）。该函数做三件事：拼接六域（L59-66）；**MCP 门控**（L64-73）——438 条 MCP schema 太贵，只有 allowed_tools 显式含 `mcp:` 前缀项（或不过滤）才追加；**通配与别名展开**（L76-88）——`vm:*` 类通配收集前缀集合，普通名字经 `_tool_name_aliases`（L19-25）展开。别名函数里藏着本篇最精妙的一处短路：名字以 `mcp:` 开头直接原样返回（L21-24），注释写明原因——MCP 工具名内含字面 `.`（server.tool 分隔符），若再做连字符改写会把 server 名改坏。`test_mcp_tool_schemas.py` L69-90 固化了反例：请求 `mcp:yahoo-finance.*` 时，若别名展开把 `-` 换成 `_`，前缀会同时匹配 `mcp:yahoo_finance.fake_tool`（另一个 server 的工具）——yahoo 假阳性。`get_tools_by_resource`（L116-131）则按冒号/下划线/连字符三种前缀筛工具。

**MCP client**（resources/mcp/client.py，308 行）：不依赖任何 MCP SDK，手写 JSON-RPC over stdio。配置解析 `load_mcp_process_config`（L83）支持 yaml/yml 文件名直配、按 YAML 内 `name` 字段反查（L118-135，多命中即报冲突）、`toolathlon_root` 旧参兼容（L94-100）；占位符只认三个：`${local_servers_paths}/${agent_workspace}/${task_dir}`（L18，L50-54）。`build_server_env`（L57）有段 PG 桥接——把 PGHOST 等别名转 PG_HOST（L68-74），适配那些只认后者的 MCP server。`MCPStdioClient`（L172）实现 initialize（协议版本 2024-11-05，L198）/list_tools/call_tool；读循环 `_read_response`（L270-299）跳过无 id 行（通知）与非 JSON 行（server 日志误入 stdout，L287-294 只 warning 不崩）；close 先 terminate 再等 5 秒、超时 kill（L227-244）。

**MCP backend**（toolathlon_gym.py，257 行）：`ToolathlonGymBackend`（L27）的 `bind_server`（L44-52）把 manifest 里全部 438 个工具名注册为桥接函数——每个 `mcp:server.tool` 名对应 `_make_bridge_tool`（L170-175）闭包；真正的 stdio 进程按会话惰性启动：`initialize` 只拉起 `enabled_mcp_servers` 列出的客户端（L139-164）。`_dispatch`（L177）三段防御：server 未启用→5011、客户端不在→4007、超时→5006（L187-228）。

**manifest 本体**：`tool_schemas/mcp/toolathlon_gym_manifest.json`——实测 438 条工具、25 个 server（canvas 69 个最多），每条含 name/description/parameters/server/tool 五键，名字形如 `mcp:arxiv-latex.get_paper_abstract`。`toolathlon_gym.py`（schema 侧，16 行）只是 json.load 这个落盘文件——静态快照而非运行时 list_tools，理由写在 `__init__.py` L64-66 注释：manifest 太贵，不能进每个 prompt。

## 外部连接

四工具集由 `tools/__init__.py` L221-225 触发注册、由 config_loader 的 `_load_api_tools`（config_loader.py L368）按 `config_key` 注入配置（配置在 configs/sandbox-server/*.json 的 apis 节）。tool_schemas 被 rollout 的 `AgentRunner._load_tool_schemas`（runner.py L129-142）消费翻译成 OpenAI 格式。MCP backend 的 YAML 配置在 resources/mcp/configs/（25 个 server 一仓一档：12306/arxiv-latex/canvas/emails/excel/filesystem/google_calendar 等），与 Toolathlon-GYM 评测生态对接；workspace 默认 `/tmp/agentflow_mcp`（toolathlon_gym.py L38）。doc 工具的 seed 由 seeds/doc 的 seed.jsonl kwargs 注入 seed_path；ds 同理由 seeds/ds 注入。

## 数据流

以一次 MCP 调用为例：LLM 产出 tool_call `mcp:emails.send_email` → ToolExecutor 归一化前缀得 resource_type="mcp" → get_or_create_session 触发 backend.initialize → 按 YAML spawn stdio 子进程、JSON-RPC initialize 握手 → `_dispatch` 解析 `mcp:emails.send_email` → server="emails"、tool="send_email"（L253-256）→ `client.call_tool` 写 stdin 读 stdout → 结果包进标准响应回传。schema 侧则相反：manifest 静态进 prompt（经 mcp 门控），执行时按名桥接——描述与执行最终在名字字符串上会师。

## 设计决策（含批判）

- **执行/告知分离**：实现改了不必动 schema 文件、schema 调措辞不必碰代码，代价是两处可能失同步——schema 里的参数名与函数签名没有编译期校验，只能靠评测兜底。这是全仓最值得警惕的隐式契约。
- **手写 MCP client**：零 SDK 依赖、代码 308 行可全审计；但只支持 stdio、无 capability 协商、单请求锁串行（L177），高并发场景每个 server 只能流水线执行。
- **438 工具静态 manifest**：启动零开销、评测可复现；代价是 server 升级加工具后 manifest 过期，运行时新工具对 LLM 不可见。
- **惰性起进程**：每会话只拉启启用的 server，未启用的调用返回结构化 5011 而非崩溃——对 agent 友好，它会读错误信息自行换路。
- **ds_tool 空代码兜底脚本**（L495-531）：救场设计实为行为不一致源——空 code 不报错反而跑聚类，模型可能学会「懒得写代码」。批判性地看，`INVALID_INPUT` 才是更诚实的响应。
- **text2sql 只读 URI + 语句白名单**：双保险防御 agent 越权写库，PRAGMA 放行是为了查 schema，属最小必要妥协。

## 新人提示

1. 先读 tool_schemas/__init__.py 的 90 行——别名/通配/mcp 门控三逻辑是全工具面路由的心脏，读懂它再看六域 schema 文件会非常顺。
2. 新接一个 MCP server：resources/mcp/configs/ 加 YAML → manifest 若无该 server 工具则需另行生成 → 配置 `enabled_mcp_servers`。三步缺一都会得到 5011。
3. doc 工具排障先看 seed_path 是否传入（错误信息会明说 "must be provided in kwargs"），再看 outline.xml/all_content.xml 是否存在——90% 的 doc 工具失败在这两处。
4. 改工具函数签名时，务必同步 tool_schemas 的 parameters 与 docstring 首行（description 的来源），三处不一致时 LLM 会稳定地传错参数。
