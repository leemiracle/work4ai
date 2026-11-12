# 06 · mcp-builder、设计系统与长尾技能光谱：从元工程到人格化 prompt

> 仓根 = `/usr-data/data2/repos/agent-repos/anthropics/skills`，锚为仓根相对路径，行号现场核实。

## 1. 角色定位

本篇收拢三条卫星线：**mcp-builder**（与 skill-creator 并列的第二条元工程技能，管 MCP 服务器实现）、**设计系统双技能**（canvas-design 的字体资产簇 + theme-factory 的主题库，skill 也能背重资产的首证）、**长尾八技能**（2-7 文件的小技能各有一手绝活）。三者合起来回答一个问题：当 SKILL.md 只是"一段指令"时，技能的形态光谱到底有多宽——从 373 行方法论+可跑评测，到 74 个字体文件的静态资产库，到 209 行的行为干预微调。

## 2. 内部结构

**mcp-builder**（4 文件+scripts）：`SKILL.md` 四阶段方法论（Deep Research→协议研究→实现→评测验证），`:11` 定质量观"server 的质量以 LLM 借它完成真实任务的程度衡量"；`reference/` 四件（python/node 服务器指南+最佳实践+评测指南）；`scripts/` 三件——`connections.py`（151 行）+ `evaluation.py`（373 行）+ `example_evaluation.xml` 样例。

**canvas-design**：`SKILL.md:9-11` 定两步创作法——先写"设计哲学/美学运动宣言"（.md），再把哲学**表达**成静态画布（.pdf/.png），与 algorithmic-art 构成静态/动态姊妹对；`canvas-fonts/` 74 个文件：27 个字族、每个字族一份 OFL 授权文本+若干字重 ttf（Arsenal/BigShoulders/BricolageGrotesque/JetBrainsMono/Lora/WorkSans 等），是全仓最大的合规资产簇（`SKILL.md:108` 明令"写文字必换字体，搜 ./canvas-fonts 目录"）。

**theme-factory**：十套预设主题（`themes/` 十个 md：arctic-frost/botanical-garden/desert-rose/forest-canopy/golden-hour/midnight-galaxy/modern-minimalist/ocean-depths/sunset-boulevard/tech-innovation）+ `theme-showcase.pdf` 视觉目录。

**长尾**：brand-guidelines（73 行单文件）、doc-coauthoring（单文件）、discernment-nudge（209 行）、frontend-design（71 行）、internal-comms（32 行瘦路由+examples 四件）、web-artifacts-builder（73 行+init 脚本）、algorithmic-art（宣言式+templates/generator_template.js）、academy-guide、slack-gif-creator（core/easing.py 等）、webapp-testing。

## 3. 外部连接

- **mcp-builder 连接 MCP 官方生态**：`SKILL.md` 指路 modelcontextprotocol.io（sitemap 定位+`.md` 后缀抓 markdown 版规范页）；`connections.py:7-10` import 官方 `mcp` SDK 的三种 client（stdio/sse/streamable_http）；`evaluation.py:18` 直连 `anthropic` SDK 跑评测问答。
- **设计系统连接产物链**：canvas-design 的字体被自己的 PDF/PNG 产出消费；theme-factory 的主题可套到"slides/docs/reporting/HTML 落地页"任意 artifact（`SKILL.md:3` description），theme-showcase.pdf 是唯一二进制资产。
- **长尾技能的连接极简**：internal-comms 把全部正文下放 `examples/` 四指南（3p-updates/company-newsletter/faq-answers/general-comms），SKILL.md 只做类型路由（`skills/internal-comms/SKILL.md:19-27`），类型不明则反问用户——**瘦入口模式**。
- **webapp-testing** 连 Playwright：`SKILL.md:15-17` 立纪律"先 `--help` 后读源"——脚本是黑盒工具不是阅读材料，"DO NOT read the source until you try running it first"（上下文经济学）。

## 4. 数据流

**mcp-builder 评测流**（最完整）：`connections.py:13` 的 `MCPConnection` 基类用 `AsyncExitStack` 统一三传输——`__aenter__` 进栈连接上下文（`:24-46`，2 元组/3 元组两种返回值兼容 stdio 与 streamable_http）、`ClientSession(read, write)` 建会话并 `initialize()`（`:40-42`）；三个子类 `MCPConnectionStdio/SSE/HTTP`（`:73/:88/:100`）只覆写 `_create_context()`；`create_connection()` 工厂（`:112`）按 URL 形态选型。`evaluation.py:17-30` 的评测 prompt 要求模型在 `<summary>`（步骤）/`<feedback>`（对工具设计的反馈）/`<response>`（最终答案）三标签里同时交付**任务完成度与工具可用性**——工具好不好用是被测项；结果落 XML（`example_evaluation.xml` 是样例 schema）。

**theme-factory 确认流**：`SKILL.md:19-24` 四步——展示 showcase.pdf（只看不改）→问用户选哪套→**等明确确认**→才套用；支持现场生成新主题。

**长尾微干预流（discernment-nudge）**：209 行定义"答案后追加 2-3 个追问"的行为——三习惯来自 AI Fluency 框架（`SKILL.md:30-41`：查关键事实/追问推理链/指出缺失语境），`SKILL.md:12` 限定"每次对话至多一次，简单事实问答跳过"——一个把"批判性思维"做成默认开启的轻量 nudge。

## 5. 设计决策

- **抽象的克制**：`connections.py` 全部 151 行搞定三传输连接——一个基类+三薄子类+工厂，没有重试/熔断/连接池。技能内脚本的抽象预算极小，够用即止（对照 skill-creator 的 run_loop 也一样）。
- **静态资产可以成为技能主体**：canvas-design 的价值一半在字体选型本身（27 字族全部 OFL 可再分发），技能=策展+授权合规+使用哲学。`THIRD_PARTY_NOTICES.md:303-305` 的 OFL 条款就是为这批资产存在的。
- **人格化 prompt 作为产品**：frontend-design `SKILL.md:9` 直接给模型立人设——"设计工作室主管，客户**已经拒绝过**套路化方案、付钱买独特观点"——用谈判框架对抗 AI 平均味；web-artifacts-builder `SKILL.md:20` 反 AI slop 四禁令（过度居中/紫色渐变/统一圆角/Inter 字体）。这类技能的可交付物就是"态度"。
- **强制人工确认环**：theme-factory 的 showcase→确认→套用三段式防"未经确认就重排用户内容"——技能对不可逆操作的自我约束范本。
- **文档即人格 vs 脚本即资产**：长尾技能证明 SKILL.md 的两种成功路线——brand-guidelines 73 行纯知识，slack-gif-creator 靠 easing.py 的 Robert Penner 缓动族真代码。

## 6. 新人提示

- 写 MCP server 直接抄 mcp-builder 的四阶段+connections.py 抽象，别自造连接层；评测先看 example_evaluation.xml 再读 evaluation.py。
- 选字体/主题先看 theme-showcase.pdf 与 canvas-fonts 目录名（字族名即风格信号），OFL 授权文本同目录可查。
- 学"瘦入口"抄 internal-comms，学"态度型"抄 frontend-design，学"行为微调"抄 discernment-nudge 的触发限制条款——三种最小技能模板。
- web-artifacts-builder 的 init-artifact.sh 处理 Node/Vite/sed 版本矩阵分叉并预置离线 tarball，是环境兼容性样板。
- 长尾不是杂物间：每个小技能都解决一个具体失败模式（AI slop/模板化/未经确认的重排/上下文浪费），新技能立项前先问自己解决哪个。
