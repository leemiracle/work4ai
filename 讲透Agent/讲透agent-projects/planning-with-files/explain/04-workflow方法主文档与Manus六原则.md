# 04 · workflow 主文档、quickstart 五步与 Manus 六原则（方法论教学层）

> 对应图谱 L7「实战示例与理论参考」+ L8「方法主文档四件」，tour t04/t08/t09。核心文件：`docs/workflow.md`（210 行）、`docs/quickstart.md`（164 行）、`skills/planning-with-files/reference.md`（219 行，理论根基）。

## ① 角色定位

这三个文件构成"从图到手到理"的教学层：`docs/workflow.md` 用两张 ASCII 图把三件套+钩子的运行时关系画成闭环，是理解整个系统的最短路径；`docs/quickstart.md` 是五步上手教程（README.md:246 点名入口）；`skills/planning-with-files/reference.md` 是理论出处——Manus 上下文工程六原则+三策略+七步循环的完整转写，末尾附一手链接（skills/planning-with-files/reference.md:215-218）。三者都不执行任何东西，但决定了用户"信不信这套方法"。

## ② 内部结构

**workflow.md** 三大块：① Visual Workflow 全流程 ASCII 图（docs/workflow.md:9-111）——任务开始(>5 工具调用)→STEP1 建 task_plan（图内大写 "NEVER skip this step!"，docs/workflow.md:17-19）→建 findings/progress→进入 WORK LOOP 循环体：PreToolUse 重读→干活→PostToolUse 提醒→2-Action Rule 落盘→阶段更新→错误记录→循环判定→Stop 钩子校验全阶段完成否则回环；② Key Interactions 表（docs/workflow.md:115-157）——四钩子触发表（docs/workflow.md:119-124）、2-Action Rule 的 4 操作示例（docs/workflow.md:130-135）、Phase Completion 双文件更新（docs/workflow.md:137-148）、Error Handling 四步（docs/workflow.md:150-157）；③ File Relationships 拓扑图（docs/workflow.md:161-188）——task_plan 居顶被 PreToolUse 逐次读取，findings/progress 分列两翼。

**quickstart.md** 五步：Step1 触发技能建三文件+手动备选 init-session.sh（docs/quickstart.md:11-24）；Step2 拆 3-7 阶段（docs/quickstart.md:28-48）；Step3 工作与记录的"事件→文件→写什么"七行映射表（docs/quickstart.md:52-66，本篇是全仓最实用的一张表）；Step4 决策前重读（docs/quickstart.md:80-88，说明有钩子时自动、无钩子时手动）；Step5 完成校验 check-complete.sh（docs/quickstart.md:92-107）。附三文件更新时机速查框（docs/quickstart.md:111-143）与五条 Common Mistakes（docs/quickstart.md:147-155）。

**reference.md** 四部分：六原则逐条（skills/planning-with-files/reference.md:5-74）——P1 Design Around KV-Cache（100:1 token 比、缓存 $0.30 vs 未缓存 $3/MTok 十倍价差，skills/planning-with-files/reference.md:11-14）、P2 Mask Don't Remove（skills/planning-with-files/reference.md:21-25）、P3 Filesystem as External Memory（skills/planning-with-files/reference.md:27-40，含"压缩必须可恢复：留 URL 留路径"三条，skills/planning-with-files/reference.md:37-40）、P4 Manipulate Attention Through Recitation（skills/planning-with-files/reference.md:42-54，"lost in the middle"与 ~50 次调用遗忘曲线）、P5 Keep the Wrong Stuff In（skills/planning-with-files/reference.md:56-63）、P6 Don't Get Few-Shotted（skills/planning-with-files/reference.md:65-74）；三策略（skills/planning-with-files/reference.md:78-127）——压缩/多智能体隔离/**卸载**（<20 原子工具，skills/planning-with-files/reference.md:120-127）；七步 Agent Loop（skills/planning-with-files/reference.md:130-164）；统计表（skills/planning-with-files/reference.md:189-197：~50 次调用/任务、100:1、$2B、8 个月 $100M）。

## ③ 外部连接

workflow.md 图内的 PreToolUse/PostToolUse/Stop 节点直接对应 skills/planning-with-files/SKILL.md:6-24 的 frontmatter hooks；2-Action Rule 与 Stop 校验分别落在 scripts/check-complete.sh 与 findings.md 模板；quickstart 尾链 troubleshooting.md 与 examples/README.md（docs/quickstart.md:159-163）。reference.md 是 upstream——六原则全部来自 Manus 官方博客（skills/planning-with-files/reference.md:218 链接），Lance Martin 的架构分析是三策略来源（skills/planning-with-files/reference.md:80）；README 的 Manus Principles 对照表（README.md:219-227）是 reference 的营销缩写版。examples.md（同目录）则用四场景把规则演成剧本。

## ④ 数据流

方法的信息流三环：**注意力环**（钩子驱动）——每次工具调用前 task_plan 头 30 行进上下文→目标始终在注意力窗口末端（skills/planning-with-files/reference.md:50-54 的示意图）；**持久化环**（规则驱动）——发现/决策/错误在产生当下写盘，上下文可丢而文件不丢；**恢复环**——/clear 后 5-Question 自检（docs/workflow.md:192-203）从三文件重建状态。教学层的贡献是把三环从 SKILL.md 的规则清单变成可视因果链：docs/quickstart.md:52-66 的表是"事件→写哪个文件"的编译器，docs/workflow.md:9-111 的图是"钩子何时介入"的时序编译器。

## ⑤ 设计决策与陷阱

- **workflow.md 钩子表滞后于实现**：表列 SessionStart "Notifies skill is ready"（docs/workflow.md:121），但正本 frontmatter 根本没有 SessionStart——v2.23.0 把会话级钩子改成了 UserPromptSubmit（CHANGELOG.md:11 记录了这次跨 7 份 SKILL.md 的替换）。文档画的钩子集合是 v2.22 及以前的形态，读图时须对照 frontmatter 修正。
- **方法与出处的张力**：skills/planning-with-files/reference.md:118 记录 Manus 自己发现"~33% 动作耗在更新 todo.md"后转向专职 planner agent+子代理（Strategy 2，skills/planning-with-files/reference.md:100-118），而本技能恰恰仍是单 agent 手写 todo 文件路线——六原则是它引用的，三策略里它只完整实现了卸载与压缩，隔离策略留给了社区 fork（README.md:27 的 plan-cascade 多智能体编排）。
- **KV-cache 原则与逐次重注入的暗冲突**：P1 要求 prompt 前缀稳定（skills/planning-with-files/reference.md:17-19），而 PreToolUse 每回合注入内容会随 task_plan 更新而变化——技能用注意力收益换掉了部分缓存收益，这是 +68% token 成本（docs/evals.md:98）之外的隐性代价。
- docs/quickstart.md:105 说 Stop 钩子"会阻止停下"，正文的实际行为是输出劝阻文本而非硬阻断（check-complete.sh 永远 exit 0）——"强制力"在 Claude Code 线弱于 Cursor 线（docs/cursor.md:119 自评 Cursor 版更强大）。
- skills/planning-with-files/reference.md:46 的 "~50 tool calls" 与 skills/planning-with-files/SKILL.md:3 的 ">5 tool calls" 是两个不同阈值：前者是遗忘拐点（为何要规划），后者是触发门槛（何时启用）——引用时别混。

## ⑥ 新人提示

阅读顺序钉死：先 docs/workflow.md 两张图（10 分钟）→ 再 docs/quickstart.md 陪跑一个假想任务 → 最后 reference.md 六原则补理论。docs/quickstart.md:52-66 的映射表值得打印贴手边——它是三件套的"使用手册压缩包"。学 reference 时把 P4（复诵）与 P5（留错误）当成本技能的直系血统，P1/P2/P6 是"知道但没完全做"的远亲；想看六原则原始语境直接去 skills/planning-with-files/reference.md:218 的 Manus 博客。写自己的规划技能时，workflow.md 的 ASCII 图法（阶段盒+循环体+钩子节点）是很好的设计文档范式。
