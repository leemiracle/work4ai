# SkillSpector 新人导读（ONBOARDING）

> 基准：commit `2226747e`（2026-09-29，v2.12.0 未发布档）· 图谱 1497 节点/3170 边 · 16 层/16 步 tour
> 所有路径与行号均经源码逐项核实（2026-11-04），与 DEVELOPMENT.md 不一致处以源码为准。

## 1. 一句话定位

SkillSpector 是 NVIDIA 开源的 **AI agent skill 安装前安全检测器**：在 Claude Code / Codex CLI / Gemini CLI 等安装一个 skill（SKILL.md 及其捆绑产物）之前，用**静态模式、行为分析、MCP 专项、语义 LLM 四条检测线**扫出其中的提示注入、凭据收割、供应链投毒与过度授权，产出 0-100 风险评分与 SARIF 2.1.0 标准报告。README.md:10 给出动机：研究的 31,132 个 skill 数据集中 26.1% 含漏洞、5.2% 疑似恶意——skill 生态"隐式信任、几乎零审查"，本工具就是 NVIDIA Verified Skills 管线的守门员。覆盖面是 17 类 71 种漏洞模式（README.md:27），分析骨架是 LangGraph 工作流（`src/skillspector/graph.py`），语义线可选（`--no-llm` 即纯静态跑）。

三个容易误解的定位点：
- 它**不是**通用 SAST。检测对象是 skill 包（markdown 指令+脚本+依赖声明+MCP 清单），规则族（P/E/PE/SC/TM/MP/RA/LP/TP/RP…）全部围绕"skill 对 agent 及宿主的攻击面"设计。
- 它**既是 CLI 也是 MCP server**。`skillspector mcp`（cli.py:3115）把 `scan_skill` 暴露给 agent 做运行时安装护栏（`src/skillspector/mcp_server.py:226` `build_server` 默认 `allow_local_targets=False` 拒绝本地路径）。
- 语义线走外部 LLM，默认 provider 是 `nv_build`（build.nvidia.com）——不设任何环境变量的 OSS 用户自动落此路径。

## 2. 仓库全貌

git ls-files 共 **403 个文件**，Python 为主、含少量 TS 生态集成。布局五块：

| 区块 | 内容 | 规模（实测） |
|------|------|------|
| `src/skillspector/` | 主包，src-layout | 103 个 .py |
| `tests/` | 测试巨阵 | 129 个 test 文件 + fixtures |
| `contrib/batch_scan/` | 多语言批量扫描子系统 | 21 个 .py + 独立测试体系 |
| `docs/` | 16 篇专题设计文档 + 22 篇逐版本 release notes | 38 个 md |
| `extensions/` `.opencode/` `skills/` | OpenCode/pi 扩展与 skill-inspector 技能 | TS + md |

**主包内部结构**（`src/skillspector/`）四层：包根 30 余个领域模块（models/state/inspection_ledger/input_handler/artifacts 等共享底座）；`nodes/` 是工作流节点（resolve_input/build_context/meta_analyzer/finalize_inspection_ledger/report + `analyzers/`）；`nodes/analyzers/` 33 个文件中 **27 个真分析器**（`grep '^ANALYZER_ID'` 实测 27 个）+ 6 个基础设施（`__init__.py` 注册表、`common.py`、`static_runner.py`、`pattern_defaults.py`、`whitespace_padding.py`、`osv_client.py`）；`providers/` 是 13 个 LLM 供应方子包 + 协议/注册表底座；另有 `yara_rules/` 四族规则文件。

**测试巨阵**是本仓一大奇观：`tests/nodes/analyzers/` 下 49 个测试文件逐条回归检测器边界（围栏边界/JSON 引号归属/正则回溯/假阳性控制），`tests/unit/test_cli.py` 单文件 6205 行 141 个测试函数覆盖全命令面；根目录 17 个端到端验收（如 `tests/test_bundled_execution_surface_acceptance.py` 挂 issue #399）。`tests/fixtures/` 16 个顶层目录是**刻意构造的攻击样本库**：`malicious_skill/`（表面厨艺助手、Step 7 暗藏"加一撮氰化物"+helper.py 收割环境变量外传）、`mcp_poisoned_tool/`（SKILL.md 描述尾注入 SYSTEM 指令、`reаd_data` 用西里尔 а 同形字符）、`sdi/sqp/ssd` 三族语义分析正反例对照——检测器的灵敏度黄金基准全在这里。

`contrib/batch_scan/` 是"研究级运营封装"：对整个技能市场做规模扫描，三层并行 + 多 API key 池 + DeepSeek 猴补丁兼容层，带 164 项测试与 4 篇设计文档（`contrib/batch_scan/docs/DESIGN.md` 论证 graph.invoke() 是纯函数故可三层并发）。

工程配置侧：`Makefile` 是任务入口（install/test-unit/test-provider/lint/langgraph-dev/docker-build 等）；`Dockerfile` digest 锁定双阶段构建，容器即扫描器（ENTRYPOINT=skillspector，WORKDIR=/scan）；`.github/workflows/` 四条流水线（ci/release/scorecard/update-pr-branches），第三方 action 全部 pin 到 commit SHA。

## 3. 核心架构：cli → graph → nodes 管线

全仓心脏是 `src/skillspector/graph.py`（88 行小文件，却是拓扑总装）。`create_graph()`（graph.py:44）装配的主干：

```
START → resolve_input → build_context ─┬→ [27 个分析器并行扇出] ─┬→ meta_analyzer
                                        └────────────────────────┘        ↓
                                                            finalize_inspection_ledger → report → END
```

逐节点职责（全部在 `src/skillspector/nodes/`）：

1. **resolve_input**（`resolve_input.py:42`）：图首节点。调 `input_handler.py` 的 `InputHandler` 把本地路径/URL/git 仓库解析到安全临时目录，捕获 `IngestLimitExceededError` 等转为账本事件，把源身份与 raw file cache 写入 State。
2. **build_context**（`build_context.py:2565`，全仓最重节点，3431 行）：`_walk_skill_files` 安全遍历产出组件清单；`_read_file_cache` 组装外发脱敏的 LLM 可见缓存；`_inspect_excluded_artifacts` 下钻排除制品；`_BoundedManifestLoader`（build_context.py:2026，继承 yaml.SafeLoader 的有界解析器）读 manifest；最后 `prewarm_python_ast_cache`（build_context.py:3301）在扇出前预热共享 Python AST 缓存。
3. **27 个分析器并行扇出**：注册表在 `nodes/analyzers/__init__.py`——`_discover_analyzers()` 用 `pkgutil.iter_modules`+`importlib` 在包导入期扫描本目录，凡模块级有 `ANALYZER_ID` 字符串 + 可调用 `node` 函数即登记进 `ANALYZER_NODE_IDS/ANALYZER_NODES/ANALYZER_MODULES`（导入失败记入 `ANALYZER_LOAD_ERRORS` 不炸全局）。graph.py:59-70 遍历注册表，`is_available()` 过滤后 `guard_analyzer_node(analyzer_id, node)` 包裹进图——包裹器（`inspection_ledger.py:1076`）把分析器异常转成账本事件，保证单个分析器崩溃不拖垮整图。
4. **meta_analyzer**（`meta_analyzer.py`，873 行）：汇合点。`LLMMetaAnalyzer` 以结构化输出对静态发现做 LLM 过滤/增补；LLM 失败时 `_passthrough_with_defaults`（meta_analyzer.py:272）**fail-closed 全量保留确定性规则发现**——"多报比静默丢安全"。
5. **finalize_inspection_ledger**（`finalize_inspection_ledger.py`）：对被引用但未分析覆盖的制品补发发现（引用完整性）、检查尺寸覆盖，合并完整性缺口与分析器加载错误，产出 `analysis_completeness`。
6. **report**（`report.py:1548`）：`_compute_risk_score`（report.py:490）算 0-100 评分与建议档位（阈值 RISK_THRESHOLD=50，constants.py:34）；`_build_sarif`（report.py:597）装配 SARIF 2.1.0（模型在 `sarif_models.py`，15 个 Pydantic 模型映射 OASIS 规范）；渲染 terminal/json/markdown/sarif 四格式。注意 `report.py:1713` 在产报告前调 `deduplicate(active_findings)`——**去重不是独立图节点**，是 report 内部的函数调用（`nodes/deduplicate.py:152`），图谱摘要里"LangGraph 去重阶段"的表述按源码应修正。

**状态契约**是 `state.py` 的 `SkillspectorState` TypedDict——实测 57 个注解字段（输入/产物/发现/账本/预算/LLM 调用记录/传递闭包遍历态/transitive_* 八字段组），findings 用 `merge_findings_by_id` reducer 归并（state.py:273），ledger 用 `merge_inspection_ledger`。`WorkflowResourceBudget` 是工作流级三路预算（时间/字节/产物数）。

**模块级 `graph = create_graph()` 单例**（graph.py:88）在导入时编译——`__init__.py` 直接重导出它，CLI/MCP server/batch_scan 三条入口共享同一份编译产物。`langgraph.json` 指向它，`make langgraph-dev` 即可在 LangSmith Studio 里可视化调试整条管线。

数据模型全家归一在 `models.py`：`Severity` 枚举、`Location/AnalyzerFinding/Finding`、分析器插件协议 `AnalyzerPlugin`——fanIn 70 全仓最高，四条检测线 27 个分析器的产出全部是这几个类型。

## 4. 关键模块深读

### 4.1 `src/skillspector/cli.py`（3245 行）——对人的主接口
Typer app 挂三命令：`scan`（cli.py:414，支持 --format terminal/json/markdown/sarif、--no-llm、--recursive、--baseline、--yara-rules-dir、--fail-on-findings 等）、`mcp`（cli.py:3115，起 FastMCP server）、`baseline`（cli.py:3159，生成误报抑制基线）。文件头 docstring 钉版设计哲学："CLI 是 LangGraph 工作流的薄壳——映射参数到初始 state、invoke 图、映射结果到输出与退出码，无业务逻辑"。内含两台引擎：`_scan_transitive` 沿外部引用逐跳复跑 graph 合并预算化结果（传递闭包扫描）；多 skill 递归批扫（`multi_skill.py` 的 `detect_skills` 以有界 scandir 识别 SKILL.md 子目录）。

### 4.2 `src/skillspector/graph.py` + `nodes/analyzers/__init__.py`——插件式扇出
见第 3 节。要点：分析器发现顺序=文件系统顺序（pkgutil），但因并行扇出顺序无关（graph.py:56 注释明示）；新增分析器零注册成本——在 analyzers/ 放一个带 `ANALYZER_ID` + `node` 的模块即自动入图。

### 4.3 `src/skillspector/nodes/analyzers/static_runner.py`（2713 行）——静态线共享运行器
15 个 `static_patterns_*` 检测器的公共底盘：文件类型推断、`AnalyzerFinding→Finding` 转换、许可证样板/env 文档排除（压误报）、markdown 围栏上下文感知、**空白连续性视图**（对抗"拆词规避"——攻击者用零宽字符拆开恶意词，归一化视图让模式仍可命中）、declared-marker 视图扫描（配合 `security_reconstruction.py` 的投影重构）。`_FindingBudget` 限额 + contextvar 观察者让逐文件扫描可提前叫停。规则文案与 19 类分类元数据集中在 `pattern_defaults.py`（get_explanation/get_remediation/get_category）。

**手写 bash 词法器**——注意它在 `static_patterns_tool_misuse.py`（3735 行，TM1-TM4）而**不在** static_runner：`_ShellToken`（static_patterns_tool_misuse.py:390）+ `_ShellDelimiterFrame`（:417，"迭代式 shell 展开定界符栈帧"）+ `_bounded_shell_tokens`（:2352）构成一个不执行、只静态切词的 bash 分析器，处理参数展开（`_skip_parameter_expansion`:772）、命令替换（`_skip_command_substitution`:2319）、反引号递归跳读（`_skip_backtick_substitution`:1428）、ANSI-C 引号（`_decode_ansi_c_escape`:459）——为的是判断 `rm -rf` 类破坏性命令是否真在命令位而非字符串/文档里。同类手写分词器另有一处：`dependency_sources.py:299` `_raw_shell_words`（解析 heredoc/重定向/sudo 包装识别 npmrc/pip 注册表改写）。

### 4.4 `src/skillspector/llm_analyzer_base.py`（1478 行，包根！）——语义线运行时
`LLMAnalyzerBase` 提供"每文件（超预算时每块）一次调用"的截断安全批处理：全局并发信号量（`DEFAULT_MAX_LLM_CONCURRENCY=10`，:77，env `SKILLSPECTOR_MAX_LLM_CONCURRENCY` 可调）；provider 瞬态错误分类（可重试状态码 frozenset{408,409,425,429}，:153）与 Retry-After 解析重试（连接类 0.5/1/2s、限流类 5/15/30s、上限 60s）；批次级台账事件；行级分块与发现区间过滤（块内发现映射回原文件行号）。meta_analyzer 的 `LLMMetaAnalyzer` 与三个 `semantic_*` 分析器都基于它。

### 4.5 `src/skillspector/providers/`——模型供应方注册表
`providers/__init__.py` 的 `_select_active_provider` 按 `SKILLSPECTOR_PROVIDER` 工厂化构造，实测 **13 个分支**（:113-160）：openai/anthropic/anthropic_proxy/bedrock/ollama/azure_openai/openai_compatible/nv_build/claude_cli/codex_cli/gemini_cli/opencode_cli/antigravity_cli——.env.example 只列 12 个（antigravity 禁用不宣传）。**关键设计：每个 `if name ==` 分支内才 import 子包**（延迟导入，未选中的 provider 依赖完全不加载）。默认 nv_build（不设 env 即落此）。`base.py` 定义四个 Protocol（ModelMetadataProvider/CredentialsProvider/ChatModelProvider/AgentCLICapable），`has_cli_capability` 用鸭子类型探测而非 isinstance。`registry.py` 按各子包捆绑的 `model_registry.yaml` 查 token 预算（context_length/max_output_tokens/structured_output_method），`functools.cache` 进程级缓存 + `SKILLSPECTOR_MODEL_REGISTRY` 用户全局覆盖。`_agent_cli.py` 是 5 个本地 agent CLI 传输的唯一加固执行入口：stdin 传 prompt、shell=False、秘密环境擦除、临时目录 CWD、硬超时与输出上限。

### 4.6 MCP 三分析器——区别于通用 SAST 的特色线
- `mcp_least_privilege.py`（LP1-LP4）：SKILL.md 清单声明的工具/权限 vs 实际调用的差集——通配权限、越权工具、能力面过宽。
- `mcp_tool_poisoning.py`（TP1-TP4）：把工具元数据（名称/描述/参数描述）当一等攻击面——隐藏文本/同形字符（TP1）、描述注入（TP2）、参数默认值投毒（TP3）静态查，TP4 由 LLM 审 markdown 代码块。
- `mcp_rug_pull.py`（RP1-RP3）：对比当前与既往清单，抓"上线后偷改定义"。
- 数据源 `mcp_registry.py`：从 registry.modelcontextprotocol.io 分页拉取，`posture_findings` 查版本钉扎/可变 tag 姿态。

### 4.7 `contrib/batch_scan/`——运营级批量扫描
入口 `batch_scan.py`（`python -m contrib.batch_scan.batch_scan`）三层并行：LangGraph 内 27 分析器扇出 → `LLMAnalyzerBase` 信号量(10) → 跨技能 ThreadPoolExecutor（--workers 默认 4，单技能 90s 超时）。`api_pool.py` 多 key 负载均衡（每 key 5 并发槽、least-loaded、429 指数退避 30s 基数 300s 封顶）。`runner.py` 是枢纽：`set_api_pool` 双补丁替换 skillspector 两处 `get_chat_model` 工厂 + **7 个 DeepSeek/非 OpenAI provider 兼容猴补丁**（Save→Patch→Yield→Restore，`_verify_patch_targets`:307 做上游签名漂移守卫，fail-closed 原子性）。`gap_fill.py` 补扫非英文技能下静态英文关键词规则的召回损失（9 条规则 P5/P6-P8/MP1-MP3/RA1-RA2）。`detection.py` 零依赖语言检测（unicodedata 统计 CJK≥10% 判 zh 等）。

## 5. 数据流走读：一个 skill 从输入到报告的完整旅程

以 `skillspector scan ./malicious_skill.zip --format sarif --no-llm` 为例：

**① 输入获取（resolve_input → InputHandler）**。`input_handler.py`（1629 行）把 zip 解到临时目录，全程设防：zip-slip 路径穿越检查、EOCD/zip64 中央目录**手工测量**（不信任归档自报尺寸）、符号链接拒绝、`O_NOFOLLOW` 打开；预算硬顶 `INGEST_MAX_BYTES=100MiB`（input_handler.py:92）、`INGEST_MAX_ZIP_MEMBERS=10,000`（:97）、`INGEST_MAX_TREE_ENTRIES=10,000`、摄取时限 60s——zip 炸弹在进分析器之前就被掐死。zip-in-zip 由 `nested_artifacts.py` 的 `_inspect_zip_bytes` 递归下钻（成员数/解压字节/深度/时间四预算）。

**② 上下文构建（build_context）**。遍历产物清单 → `artifacts.py:classify_artifact` 按魔数/扩展名分类（ArtifactRecord）→ 三份缓存入 State：`raw_file_cache`（原始字节，静态线用）、`llm_file_cache`（外发脱敏视图，语义线用）、`ast_cache`（Python AST，`python_ast.py` 按内容哈希缓存全 scan 共享）。混淆对抗在这一步前置：`artifacts.py` 对字距拉长/token 桥接/零宽字符做带源 span 映射的归一化安全视图；`unicode_confusables.py`（1527 行纯数据表，UTS #39 v17.0.0）把西里尔 а 折叠回 ASCII a；`security_reconstruction.py`（1835 行）对声明式规避标记（HTML 实体、拆字空格、JSON 字符串走私）做非执行投影重构。

**③ 四线并行分析（27 分析器扇出）**。静态线 15 个 `static_patterns_*` 走 static_runner 多视图扫描（源视图+归一化视图+空白连续性视图）；行为线 `behavioral_ast`（eval/exec/pickle 危险模式）与 `behavioral_taint_tracking`（TT1-TT6 污点源→sink 传播）吃共享 AST 缓存；供应链线 `static_patterns_supply_chain`（SC1-SC10，3276 行）+ `static_yara`（四族规则 agent_skills/cryptominers/hacktools/webshells + malware.yar.b64）+ `osv_client`（OSV.dev 在线查询，网络不可用降级静态 fallback 库）；MCP 线三分析器；语义线三分析器在 `--no-llm` 下发 disabled 账本事件直接跳过。每条 Finding 带 rule_id/severity/location/confidence/occurrences。

**④ 汇聚（meta_analyzer）**。`--no-llm` 时全量直通；LLM 开启时逐文件过滤确认/拒绝/降置信，被拒的保留为 unconfirmed——**永不静默删除确定性发现**。

**⑤ 账本定稿（finalize_inspection_ledger）**。`inspection_ledger.py`（1130 行）是本工具可信度的关键设计：`ledger_event`（:376）是事件唯一安全工厂，每个分析器对每个文件的每种处置（analyzed/skipped/failed/limited+原因）都留痕；`finalize_ledger`（:712）把事件流汇总成 `analysis_completeness`——报告因此能回答"**没报问题是真没问题，还是没扫到**"。引用覆盖检查在此补发"被引用但未分析"的发现（fail-closed：不透明制品宁可报 AE1 不可宣称安全）。

**⑥ 报告（report）**。`deduplicate()`（report.py:1713）三级键聚合保 occurrence → 基线抑制（`suppression.py` 的 sha256 指纹+glob 规则两级）→ `_compute_risk_score` 按发现严重度/置信度算 0-100 分 → `_build_sarif` 产 SARIF 2.1.0（含抑制记录/completeness/invocation 元数据）→ 按 --format 渲染。退出码由 `--fail-on-findings`/`--fail-on` 档位决定，可直接当 CI 门禁。

**清理**：`cleanup.py:remove_temp_tree` 以 onexc 回调重试 Windows 只读文件删除（git clone 的 pack 文件只读），CLI 与 MCP server 两路径复用。

## 6. 设计决策与取舍

**① 注册表工厂 + 延迟 import（providers/__init__.py:113-160）**。13 个 provider 分支全部函数体内 import：未选中的 provider 的 SDK（boto3/langchain-anthropic…）零加载，CLI 冷启动快、依赖缺失不炸。代价是分支不可静态枚举（依赖 grep 而非 import 反射做盘点）。

**② 27 分析器 SADD（Self-Auto-Discovered Directory）注册表**。`nodes/analyzers/__init__.py` 用 pkgutil 扫描自动发现——加分析器零注册成本，但也意味着**目录里每个模块都会被 import**（含 common/pattern_defaults 等基础设施，它们靠"无 ANALYZER_ID+node 组合"被自然排除）；一个模块语法错只进 `ANALYZER_LOAD_ERRORS` 不炸图，但"静默少一个分析器"只能靠账本的 analyzer_status 事件发现。

**③ 模型槽位 + token 预算兜底（constants.py:65-70）**。`_MODEL_SLOTS` 8 槽（default + 3 个 mcp_* + 3 个 semantic_* + meta_analyzer），解析瀑布 `SKILLSPECTOR_MODEL_{SLOT}` env > provider `resolve_model`（其内部又是 SKILLSPECTOR_MODEL env > 槽默认 > DEFAULT_MODEL）。允许"贵模型跑分析器、便宜模型跑 meta 过滤"（anthropic 槽位默认即 Opus 分析/Sonnet meta）。token 预算三层兜底：动态元数据 API → 各 provider `model_registry.yaml` → `DEFAULT_CONTEXT_LENGTH=128_000`（constants.py:32）；输入按 `MAX_INPUT_TOKENS_PCT=0.75` 留 75%、输出 25%。

**④ 语义线走 LLM 的边界——处处 fail-closed**。LLM 不可用时：meta_analyzer 全量直通（meta_analyzer.py:815）、semantic_* 发 disabled 账本事件、`--no-llm` 一键退化纯静态。LLM 的结构化输出畸形时：有界重试（llm_analyzer_base.py:79-84 四组延迟表）→ 批次隔离（v2.8.1 起）→ 记 skipped 而非 failed。设计哲学一句话：**LLM 只做锦上添花（过滤/增补），永不成为发现的安全阀**——确定性规则发现只有"报告"与"unconfirmed"两态，没有"删除"。

**⑤ 图的纯函数性是并发基石**。`graph.invoke()` 确定性映射 state→result（ARCHITECTURE_DEEP_DIVE.md 逐层论证无状态性），batch_scan 才敢在其上叠三层并发互不感知；contrib 的设计纪律是"只在外围加池与标注，绝不改图本身"。

**⑥ 资源上界作为安全边界而非白名单**（docs/ANALYSIS_RESOURCE_BOUNDS.md）。检测器自己处理不可信输入，处处设防：单文件 1MB 文本上限（MAX_FILE_BYTES）、16MiB 完整分析上限、截断文件仍送 LLM 但限 262,144 字符前缀并显式标记未审区域（constants.py:41-46 注释：完全排除截断文件=给载荷藏身处）；分析器各自带 `_*Budget` 类（_BehavioralBudget/_TaintBudget/_LeastPrivilegeBudget…）运行时+产出双预算。触顶不崩：记 limitation 账本事件、输出部分结果。

**⑦ 手写解析器族而非调用重量级工具**。bash 词法器、shell 分词器、JSON 容器游标（security_reconstruction 的 `_JsonContainerCursor`）、EOCD 手工解析——宁可自写有界解析也不引入无界依赖；语言检测用 unicodedata 比率而非 ML 模型。与 pyproject 锁 `typer<0.24`（规避 semgrep click 冲突）同一逻辑：**依赖面即攻击面**。

## 7. 已知坑与勘误（全部源码实证）

1. **DEVELOPMENT.md 三处 llm_analyzer_base 归位错误**：L134 与 L355 两处 markdown 链接指向 `../src/skillspector/nodes/llm_analyzer_base.py`——该路径不存在，真身在包根 `src/skillspector/llm_analyzer_base.py`；L156 的模块表又把它列在 **nodes/** 小节下。同一文件 L134 还写着 "Analyzers | 22 nodes"，实测 27 个（陈旧计数未随分析器扩充更新）。
2. **EVAL_DATASETS.md 承诺零实现**：`docs/EVAL_DATASETS.md` 声称"静态模式分析器跳过 `evals/evals.json` 等 8 个 eval 数据集路径"，但 `src/` 全目录 grep `evals` 零命中——唯一痕迹是 `inspection_ledger.py:53` 的死枚举 `LedgerReason.EVAL_DATASET`（:114 配文案"Evaluation dataset prose is excluded…"）与 `tests/test_inspection_ledger.py:52` 合成的账本事件。**当前版本对 eval 数据集文件照常扫描**，用此文档做依据会误判行为。
3. **release.py 引用已失效**：`docs/release/skillspector-2.5.1.md:44` 记载 `uv run python release.py --version patch …`，仓内无此文件——现行发布脚本是 `scripts/release/public/create_github_release.py`（.github/workflows/release.yml:54 实际调用它）。
4. **test_pool_wiring.py 不是 pytest 测试**：`contrib/batch_scan/tests/test_pool_wiring.py` 全部断言与 print 在**模块级**（无任何 `def test_`），是靠 pytest 收集期 import 副作用执行的冒烟脚本——直接 `python` 运行或纳入测试统计时口径要清楚（TEST_GUIDE.md 自己也称"4 项池接线冒烟"）。
5. **tests-pro 连字符目录**：`contrib/batch_scan/tests/tests-pro/` 目录名含连字符，Python 无法常规 import，5 个测试文件全靠模块级 `sys.path.insert(0, parents[3])` 注入工程根（test_api_pool.py:33 等）——移动目录或改打包方式时这些注入路径会集体失效。
6. **antigravity_cli 注册但禁用（fail-closed）**：`providers/antigravity_cli/provider.py` docstring 钉版——实测 agy 的 `--print` 模式渲染到 TTY、管道捕获为空、prompt 走 argv 而非 stdin，无法安全编程驱动，故 `is_available()` 恒 False、调用即抛错；其后端是 Gemini，官方建议用 `gemini_cli` 替代。.env.example 的 provider 列表因此只列 12 个。
7. **nv_build 注册表意大利语注释与 202749 组合上限坑**：`providers/nv_build/model_registry.yaml:18-25` 是意语注释（贡献者未翻译）：202749 是 endpoint 强制的**输入+输出合并上限**（超限 400 报错原文照录）。曾按名义窗口 1,000,000 登记导致 model_info 算出 250,000 输出预算、**每次调用全失败**——"高估窗口不会优雅降级：直接清零 LLM 阶段。低估安全，高估不安全"。教训：给 `z-ai/glm-5.2` 登记 `context_length: 202749` 是刻意的保守值。
8. **图谱/文档计数漂移**（读二手资料注意）：onboard 图谱与 README 的部分计数与实测不符——providers "14 种"实测 13 分支；"tests/nodes/analyzers 71 个"实测 49 个测试文件（+conftest）；test_cli "168 测试函数"实测 141 个 `def test_`。以 `git ls-files`+grep 现场口径为准。

## 8. 上手路径：结合 16 步 tour 的前三天阅读顺序

**Day 1 上午——骨架（tour t01/t02）**：`README.md`（891 行，先读定位+规则表两节）→ `pyproject.toml`（依赖即技术栈清单）→ `Makefile`（make install-dev && make test-unit 跑通即环境就绪）→ `src/skillspector/graph.py`（88 行，全仓拓扑一页纸）+ `state.py`（57 字段对照第 3 节表格读）。
**Day 1 下午——入口与边界（t03/t14）**：`cli.py` 只读 scan 命令签名与 docstring；`input_handler.py` 读预算常量区（L92-112）感受"检测器先自卫"；跑一次 `skillspector scan tests/fixtures/malicious_skill --no-llm` 对照 terminal 报告与 fixture 源码。
**Day 2——四条检测线（t06/t07/t08/t09 任选纵深）**：静态线从 `static_patterns_prompt_injection.py`（531 行，最小的样本）入手，再读 static_runner 的多视图编排；行为线读 `behavioral_taint_tracking.py`；MCP 线三分析器+`tests/fixtures/mcp_poisoned_tool/` 对照读（理论 docs/B.3.2-mcp-tool-poisoning.md）；供应链线扫 `static_patterns_supply_chain.py` 规则头注释。**改任何检测器前先读 tests/nodes/analyzers/ 下对应测试**（命名同构，如 test_static_patterns.py）。
**Day 3——语义线与汇聚（t10/t11/t12）**：`llm_analyzer_base.py` 读信号量/重试/分块三节 → `meta_analyzer.py` 读 `_passthrough_with_defaults` 的 fail-closed 语义 → `providers/__init__.py`+`registry.py`+ 任一 provider 子包（推荐 anthropic，槽位默认最典型）→ `inspection_ledger.py` 读 `ledger_event`/`finalize_ledger` 理解完备性账本。
**按需专题**：批量扫描（t15，contrib/batch_scan/docs/DESIGN.md 先行）；混淆对抗（t05，artifacts.py+security_reconstruction.py，配 docs/scan-completeness.md）；设计决策权威出处全在 docs/ 16 篇专题+22 篇 release notes（规则编号变更史查 CHANGELOG.md）。

新人首个贡献的最佳切入：fixtures 攻击样本库补样本（每个新样本自动被 CI 的 49 个分析器回归测试覆盖）或 pattern_defaults 文案完善——不需要懂图。

## 附录：勘误与死代码清单

| # | 位置 | 问题 | 实证 | 影响/处置 |
|---|------|------|------|----------|
| 1 | docs/DEVELOPMENT.md:134,355 | 坏链指向 `nodes/llm_analyzer_base.py` | 实际在 `src/skillspector/llm_analyzer_base.py`（包根） | 按坏链找文件会 404；以包根为准 |
| 2 | docs/DEVELOPMENT.md:156 | 模块表把 llm_analyzer_base 列在 **nodes/** 小节 | 同上 | 归位误导 |
| 3 | docs/DEVELOPMENT.md:134 | "Analyzers: 22 nodes" 陈旧计数 | `grep -l '^ANALYZER_ID'` 实测 27 个 | 读文档估工作量会低估 |
| 4 | docs/EVAL_DATASETS.md | 声称跳过 evals/evals.json 等 8 路径 | src/ 零实现；仅 `inspection_ledger.py:53` 死枚举 + 测试合成事件（tests/test_inspection_ledger.py:52） | **承诺未兑现**：eval 文件当前照扫 |
| 5 | docs/release/skillspector-2.5.1.md:44 | 引用根目录 `release.py` | 仓内不存在；现行脚本 `scripts/release/public/create_github_release.py` | 历史命令不可复现 |
| 6 | contrib/batch_scan/tests/test_pool_wiring.py | 模块级断言+print，无 `def test_` | 文件尾三连 assert 与 🎉 print 均在模块级 | 是冒烟脚本非 pytest 测试，统计口径注意 |
| 7 | contrib/batch_scan/tests/tests-pro/ | 连字符目录不可常规 import | 5 个文件靠模块级 sys.path.insert(parents[3])（如 test_api_pool.py:33） | 移动/重构目录时注入路径集体失效 |
| 8 | providers/antigravity_cli/provider.py | 注册但禁用 | agy `--print` 仅 TTY 渲染、管道空、prompt 走 argv；is_available() 恒 False | fail-closed；用 gemini_cli 替代 |
| 9 | providers/nv_build/model_registry.yaml:18-27 | 意大利语注释 + 202749 合并上限 | 名义窗口 1M 登记曾致输出预算 250k、调用全失败；现登记 202749 | **高估 token 窗口=清零 LLM 阶段**，登记模型宁可低估 |
| 10 | 图谱/onboard-input 摘要 | "deduplicate 是 LangGraph 去重阶段" | 实为 report.py:1713 内部函数调用，非图节点 | 图拓扑以 graph.py 为准 |
| 11 | 图谱/文档计数 | providers "14 种"/analyzers 测试 "71 个"/test_cli "168 函数" | 实测 13 分支/49 文件/141 函数 | 二手计数一律现场 grep 复核 |

死代码与准死代码：`LedgerReason.EVAL_DATASET`（无生产者，见 #4）；`malware.yar.b64` 解码后 6 条规则正常在用（非死代码，b64 包装是为防规则明文触发外部扫描器误报，属刻意设计）。

---

*本导读由 understand-anything 流水线生成：16 层架构分层+16 步 tour+30 hub 节点摘要（onboard-input.json）为骨架，全部路径/行号/计数经 SkillSpector@2226747e 源码逐项核实。*
