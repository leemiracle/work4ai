# 11 · Chart 可视化与 skill-creator 评测体系深读

## 角色定位

本篇深读两个最有"产品级完成度"的技能。**chart-visualization** 是数据可视化技能：26 份图表规格文档 + 一个 Node 脚本，把"模型选图型、抽参数"与"实际渲染"解耦——渲染交给远端 antvis 可视化服务，脚本只做参数转发。**skill-creator** 是"造技能的技能"，其精华在评测子系统：三个 markdown 角色卡（grader/comparator/analyzer）加一组 Python 脚本，构成一套完整的盲评流水线——它是全仓最能体现"用 LLM 评 LLM"工程纪律的样本。

重要甄别先钉版：skill-creator 的评测实为**两条独立线**。触发率线（run_eval.py 测 description 能否让模型正确触发技能）与质量线（benchmark + 三角色卡评产出质量）在代码上零交集——run_eval.py 的九个参数（`run_eval.py:261-269`）全是触发语义（--trigger-threshold 等），不消费 agents/ 目录任何文件；把"评测三件套"与 run_eval 视为同一子系统是假关联。

## 内部结构

**chart-visualization**：`SKILL.md`（frontmatter 声明 `nodejs: ">=18.0.0"`，`SKILL.md:5`）+ `scripts/generate.js`（173 行）+ `references/` 26 份规格 md。脚本核心是 `CHART_TYPE_MAP`（`generate.js:6-32`）：25 个 `generate_*_chart` → antvis 图型名的映射表，area 到 word-cloud（`generate.js:25` 最后一键）。调用入口查表（`generate.js:131`），地图类走独立 `generateMap`（`generate.js:79`）；模块导出四符号（`generate.js:173`）。渲染服务地址经 `VIS_REQUEST_SERVER` 环境变量解析。

**skill-creator**：`SKILL.md` 485 行主工作流 + `agents/` 三角色卡 + `scripts/`（init/package/run_eval/run_loop/improve_description/aggregate_benchmark/quick_validate）+ `eval-viewer/`（无框架单文件 HTML 报告器）。

## 外部连接

**chart 的三方契约链**：SKILL.md 工作流指引模型读 references 规格 → 模型按规格调 generate.js → 脚本 POST antvis 服务。`generate.js:5` 注释明示映射表"与 frontend 的 src/utils/callTool.ts 保持一致"——**跨层契约靠一行注释维系**，前端文件不在本仓扫描面内，改映射表时须双向核对（SKILL.md:3 自称 "26 available options" 而映射表 25 键，正是这种松耦合的代差产物）。

**评测线的进程外依赖**：run_eval/improve_description 都以子进程调 `claude -p`，并刻意剔除 CLAUDECODE 环境变量以允许在 Claude Code 会话内嵌套调用（`run_eval.py:80-83`，improve_description.py 同款复制）；复用宿主会话认证，无独立 API key。grader 则被要求"不依赖 transcript 自述、亲自检查产物文件"（`grader.md:30`）——角色卡把"证据要一手"写成了流程步骤。

## 数据流

**chart 一次出图**：用户给数据 → 模型按 SKILL.md 选 26 个工具名之一 → Read 对应 references 规格（如 `generate_bar_chart.md`）→ 抽取参数组 JSON → bash 调 generate.js → 脚本查 CHART_TYPE_MAP 转 antvis 图型 → POST 返回图表 URL/图片。

**评测一轮迭代（质量线）**：run_loop.py 跑 benchmark → 每轮 spawn grader（按 `agents/grader.md`）产 grading.json → aggregate_benchmark 汇总 benchmark.json → comparator 盲评 A/B 产出 → analyzer 揭盲分析。**揭盲链**是关键设计：comparator 全程只见 A/B 标签不知来源（`comparator.md:7`），裁决后才由 analyzer "unblids"（`analyzer.md:7` 原文拼写）关联回 skill 与 transcript 做归因。

**防窥机制**：run_loop 每轮改进 description 前，把 history 里所有 `test_` 前缀的分数剥掉再传给 improve_description（`run_loop.py:195-198` 的 blinded_history 列表推导，`run_loop.py:204` 注入）——改进模型看不到测试集成绩，防止它朝着测试集过拟合改写文案。

## 设计决策

**① 死规格：文档超前于实现。** references 目录 26 个 md 齐全含 `generate_spreadsheet.md`，SKILL.md:3 也宣传 26 选项，但 CHART_TYPE_MAP 实测 25 键、零 spreadsheet/pivot 映射——按文档指引调用必报 Unknown tool。这是"文档即规格先行、实现滞后"的活标本，也证明 references 是手写而非从实现生成。

**② bar/column 默认值镜像相反。** bar 的 group 默认 false、stack 默认 true（`generate_bar_chart.md:11-12`）；column 恰好反过来 group 默认 true、stack 默认 false（`generate_column_chart.md:11-12`）。两开关互斥且都要求补 group 字段。这不是 bug 而是领域语义：水平条形图堆叠更易读、垂直柱状图并排更常见——但模型极易记反，规格文档的存在价值正在于此。

**③ 三地图仅中国行政体系。** district-map/path-map/pin-map 三键（`generate.js:11`、`:22`、`:24`）走 generateMap 独立通道：title 必填且 ≤16 字（`generate_district_map.md:8`）、默认 1600x1000 远大于图表类（`generate_district_map.md:21-22`）、地名须精确到省/市/区/县行政层级——antvis 地图服务的中国行政区划数据源决定了能力边界。

**④ grading.json 字段名是硬契约。** expectations 数组强制 `text/passed/evidence` 三字段，SKILL.md 明文禁 name/met/details 变体（`SKILL.md:225`）——因为 eval-viewer 按字段名精确读取，写错 viewer 显示空值。配套纪律：能程序化检查的断言写脚本跑，"scripts are faster, more reliable"（同条内文）。

**⑤ analyzer 双角色 + 职责防火墙。** 同一文件两个 H1：主段做揭盲归因（`analyzer.md:1`），`# Analyzing Benchmark Results` 段（`analyzer.md:187`）做跨轮模式分析且明令 "not suggest skill improvements"（`analyzer.md:189`）——改进建议只属于 improve 阶段，防止分析者顺手改文案破坏盲评闭环。

**⑥ grader 反幻觉双职责。** grader 不只判 pass/fail，还兼任评测质量批评者："弱断言的通过比无用更糟——它制造虚假信心"（`grader.md:7`），并被要求主动提取输出中的隐含主张做核实（`grader.md:45` 起）。把"评评测"内置进评测者是少见的自省设计。

## 新人提示

- 调 chart 技能报 Unknown tool 时先查 generate.js:6 的 25 键映射表而非文档目录——spreadsheet 是已知死规格，26 选 1 的宣传口径信一半。
- 给技能写 description 参考 skill-creator 的实践：undertrigger 是主要失败模式，文案要 pushy；改进循环有 blinded_history 防过拟合，别绕过它直接看 test 分数调文案。
- 复用三角色卡到自己的评测：comparator 的 Stay blind 铁律（`comparator.md:196`）与 rubric 按任务类型自适应改写（`comparator.md:51-58`，PDF 表单→字段对齐、数据输出→schema 正确性）是最可移植的两段。
- timing 类数据（total_tokens/duration_ms）只在 subagent 任务通知里出现、事后不可恢复，schemas.md 提醒须立即落盘——写自己的 runner 时注意同类一次性信号。
- eval-viewer 是零构建单文件 HTML（仅 Google Fonts + 带 SRI 的 SheetJS CDN），把它当"评测报告最低可行形态"的模板看，别急着上前端框架。
