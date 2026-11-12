# 04 · productivity 群与自举机制：teach、write-a-skill 与 grilling 家族

> 对象：`/usr-data/data2/repos/ai-trending/skills/skills/productivity/`（5 skill，9 文件）：teach（5 文件 357 行）、write-a-skill（117 行）、grill-me（10 行）、caveman（49 行）、handoff（15 行）；并延伸讨论整库的自举（self-hosting）现象。

## 一、角色定位

productivity 桶的公共标签是"非代码工作流"，但五个 skill 的实质各不相同，构成一个从**通用对齐**到**垂直深耕**的光谱：

- `grill-me` 是起点：10 行纯对齐原语（`skills/productivity/grill-me/SKILL.md:6-10`）。README:59 称 grill-with-docs="same as grill-me, but adds more goodies"——先做最简形式再加层，是库的设计方法论。
- `teach` 是垂直深耕的极点：把 agent 变成跨会话的家教，用整个目录做学习状态机。
- `write-a-skill` 是**元层**：用 skill 教 agent 写 skill，库的自我繁殖器官。
- `caveman`/`handoff` 是会话经济学工具：一个压输出（省 ~75% token），一个压上下文（跨会话交接）。

## 二、内部结构

**teach 五文件**是 productivity 桶唯一的"SKILL.md+四格式文档"重组件（与 grill-with-docs、setup 同构）：

- `SKILL.md`（113 行）开宗明义"This is a stateful request - they intend to learn the topic over multiple sessions"（L8）。六载体（L14-19）：`MISSION.md` 动机锚、`reference/*.html` 速查（压缩沉淀可复访）、`RESOURCES.md` 信源、`learning-records/*.md` 学习记录（"loosely equivalent to architectural decision records"——ADR 的教学移植，L17）、`lessons/*.html` 课程（一次教 ONE THING 且给 tangible win，L35-43）、`NOTES.md` 偏好。
- 哲学三层（L23-31）：**知识**（高信源采集，"Never trust your parametric knowledge" L29）+**技能**（交互课+最紧反馈环 L77-83）+**智慧**（真实社区 L87-93，用户拒绝社区要尊重）。
- **最近发展区**（L55-65）：每课"challenged 'just enough'"；用户点名照办，否则读 learning-records+任务书推断；自称已懂就记录。
- 任务书缺失先追问动机（L47-53）；任务书漂移须更新 MISSION.md 并记 learning record（L53）。
- 四份格式文档皆轻量：`MISSION-FORMAT.md`（Why 真实目标/Success 可观察/Constraints/Out of scope 四节 L11-22；"Concrete over abstract"L28；过一屏"就从指南退化成计划"L32）；`LEARNING-RECORD-FORMAT.md`（单段即合法 L15；四触发 L31-36 含"误解被纠正——预测未来绊脚石"；不触发 L39-42"Coverage is not learning. Wait for evidence."；取代标记不删除 L44-46）；`GLOSSARY-FORMAT.md`（三元组同 CONTEXT-FORMAT；"Add a term only when the user understands it"L29）；`RESOURCES-FORMAT.md`（Knowledge/Wisdom 两组 L3；"A bare link is useless in three months"L28；"Prune ruthlessly"L31）。

**write-a-skill**（117 行）三步流程（L10-24 gather→draft→review）+规范：结构（L28-35）；**description 契约**（L62-88"The description is **the only thing your agent sees**"——≤1024 字符、第三人称、次句 "Use when [triggers]"；坏例"Helps with documents."L88）；加脚本判据（L90-98"Scripts save tokens and improve reliability vs generated code"）；拆文件判据（L102-106）；六项收尾清单（L108-116"References one level deep"）。

**caveman**（49 行）：规则（L18 砍冠词/填充词/客套/对混，"X -> Y"箭头；技术词代码块逐字保留 L20）；持久性（L14 触发后每次响应生效，仅明说停止才关）；**Auto-Clarity Exception**（L37-43 安全警告/不可逆确认/顺序敏感多步临时退出——压缩永不牺牲安全边界）。正文即用 caveman 语体写成（L10）——形式即示范。

**handoff**（15 行）：写 OS 临时目录不进工作区（L7）；必含"suggested skills"节（L9）；不重复已工件化内容只引路径（L11）；敏感信息必须脱敏（L13）；参数=下会话聚焦（L15）。

## 三、外部连接

- **grill-me→grill-with-docs** 是全库最重要的血缘：前者是通用对齐原语，后者加域文档层；README:59 明示派生关系。`.out-of-scope/question-limits.md` 拒绝给 grilling 家族加问题上限，L7-14 的理由保护的是这个家族的公共性格（开放式走完决策树）。
- **teach 格式文档是 CONTEXT/ADR 的家族变体**：GLOSSARY≈CONTEXT-FORMAT（三元组同构）、LEARNING-RECORD≈ADR-FORMAT（编号单段+supersede）——"记录即语言"哲学在工程域与学习域的两个投影。
- **write-a-skill 是全库规范的成文宪法**：description 的 "Use when" 契约解释了为什么全部 29 个 SKILL.md 的 frontmatter 都长那样；"References one level deep"解释了为什么参考文档都在 skill 目录内平铺。**但注意勘误**：其"SKILL.md under 100 lines"（L113）与存量不符——setup 121/diagnose 117/teach 113/write-a-skill 自身 117/triage 103 均超限，该数字是写新 skill 的指导而非存量门槛。
- **handoff 的"suggested skills"节**把技能发现带进交接——新 agent 冷启动即知该调哪些命令。
- **caveman/handoff/zoom-out**：三个最小 skill（49/15/7 行）印证"小而可组合"信条（README:19）——沟通模式/交接动作/视角切换各占一个命令位。

## 四、数据流

teach 是**学习状态读写环**：读 MISSION+learning-records→推断 ZPD→产出 lesson→用户表现产生证据→触发 learning record 写入（抬升下限）/glossary 晋升（真懂才收）/mission 修订→下课输入随之变。整个目录=跨会话学习状态机；RESOURCES.md 的 Gaps 节驱动后续搜索。

write-a-skill 是**规范生成流**：需求→问答→草稿→过稿→L108-116 清单自检；新 skill 立即进入生态——自增长。

handoff 是**单向蒸馏**：对话→去重（已工件化只留引用）→脱敏→加技能建议→落临时目录→新 agent 消费。caveman 无任何文件产出，只改响应编码——全库唯一"纯模式"技能。

## 五、设计决策

1. **为什么 teach 坚持多会话+目录状态？** L8：真学习跨会话发生，agent 会话记忆易失；状态外置到文件才能让第 10 次课知道前 9 次发生了什么——与 grill-with-docs 外置 CONTEXT.md 同一架构决策。
2. **为什么"绝不信任参数化知识"？** L29：参数化知识不可审计无出处；注释义务让每论断可链回信源（L71"Lessons should be littered with citations"）——教学对幻觉零容忍。
3. **为什么词条"真懂才收"？** GLOSSARY-FORMAT L29：词汇表是**掌握的证据**而非输入设备——把概念压进一句紧凑定义本身即理解的证明，提前收录=自欺工具。
4. **为什么 learning record 拒绝日志？** L41-42"not a journal — decision-grade insights"——只记会改变下一步教学决策的事，噪音让 ZPD 推断失真。
5. **为什么 description 是唯一契约面？** write-a-skill L62：选技能时系统提示词里只有 description 一行——含糊即永不选中；"Use when"句式=给检索器喂关键词。
6. **为什么 caveman 要写"自动清晰例外"？** L37-39：压缩语体在安全警告、不可逆确认、顺序敏感指令上会提高误读风险——用规范把"何时必须放弃压缩"固化，而不是留给现场判断，模式才敢持久生效。
7. **为什么 handoff 不落工作区？** L7：交接文档是一次性消费品，进仓即垃圾；新会话常在不同目录启动，临时目录中立。

## 六、新人提示

- 试用 `/teach` 先建空目录当工作区；它会反问"为什么学"——认真答，"具体压倒抽象"（L28）决定后面每课的相关性。
- 用户说"这个我会了"别只点头——记 learning record（连同深度），否则下节课重教。
- 写自己的 skill 时把 80% 心思花在 description 上（write-a-skill L62-88），先写"Use when"句再写正文，方向不会跑偏。
- 给 caveman 加规则前先读 L37-43：压缩不能越过安全边界；永久模式类 skill 都该有退出与例外条款。
- handoff 文档记得从临时目录取走（重启即失）；要留档的交接改用 ADR 或 issue。
- 观察自举三例可以最快理解本库气质：仓库自己的 CONTEXT.md（用域词汇表治仓）、docs/adr/0001（用 ADR 记录技能架构决策）、.out-of-scope/ 三文件（用拒绝知识库管自己的 feature request）——作者相信这些机制到愿意用自己的仓当试验田的程度。

*锚 30 处，全部 sed 现场核验 · understand-anything · 2026-11-02*
