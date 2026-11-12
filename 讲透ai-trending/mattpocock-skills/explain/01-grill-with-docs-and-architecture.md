# 01 · 域语言双旗舰：grill-with-docs 与 improve-codebase-architecture

> 对象：`/usr-data/data2/repos/ai-trending/skills/skills/engineering/grill-with-docs/`（3 文件，195 行）与 `/usr-data/data2/repos/ai-trending/skills/skills/engineering/improve-codebase-architecture/`（5 文件，338 行）。两者合计占 engineering 桶文件数的 47%，是全库理念密度最高的两个目录。

## 一、角色定位

这两个 skill 是 README 四大失败模式中三个的正面回答：#1"没懂我要什么"→grilling（`/usr-data/data2/repos/ai-trending/skills/README.md:54`）、#2"太啰嗦"→共享语言（`:73`）、#4"烂泥球"→关注设计。README 评价共享语言"可能是全库最酷的技术"（`/usr-data/data2/repos/ai-trending/skills/README.md:91`）。

`grill-with-docs` 是**生产者**：拷问计划中把术语沉淀进 CONTEXT.md、把难逆转决策沉淀进 ADR。`improve-codebase-architecture` 是**最重的消费者**：以域词汇+ADR 为输入做架构评审，"ADRs record decisions the skill should not re-litigate"。分工即 DDD 的"语言先于结构"。

## 二、内部结构

**grill-with-docs 三文件**是"主指令+两份格式契约"的典型布局：

- `SKILL.md`（88 行）用 `<what-to-do>`（L6-14）与 `<supporting-info>`（L16-88）XML 标签组织；核心指令四条：走完设计树每支、一次一问、每问附推荐答案、代码库能答的自己探索（`skills/engineering/grill-with-docs/SKILL.md:12`）。
- 会话五个动作（L54-86）：对质词汇表冲突（L58）、收敛模糊词（L62）、场景压测域关系（L66）、陈述与代码交叉验证（L70）、术语解决当场写盘不攒批（L74"Don't batch these up"）。
- 文件布局感知：根 CONTEXT-MAP.md 存在即多上下文仓（L36），所有文档惰性创建（L52"only when you have something to write"）。
- `ADR-FORMAT.md` 的激进主张在 L15："An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why* — not in filling out sections."（单段落即合法 ADR）；编号规则是扫目录取最大值加一（L27）。L39-47 列七类合格决策（架构形态/跨上下文集成/带锁定技术选型/边界归属/刻意偏离/代码外约束/非显然否决）。
- `CONTEXT-FORMAT.md` 定义术语三元组：`**术语**+1-2 句定义+_Avoid_ 别名黑名单`（L12-23）；规则第一条"Be opinionated"（L27）；L54-58 单/多上下文推断顺序。

**improve-codebase-architecture 五文件**是全库最大 skill（338 行），四份参考文档各管一段：

- `SKILL.md`（81 行）三段：①Explore 子代理漫游记摩擦点（L37）+对可疑模块做**删除测试**（L25"If complexity vanishes, it was a pass-through"）；②HTML 报告写系统临时目录（L49）；③选定候选后 grilling 循环，术语落 CONTEXT.md、被拒理由落 ADR（L72-80）。
- `LANGUAGE.md` 是架构词汇宪法：**Seam** 词条（L21-23）特别注明弃用 "boundary"（与 DDD bounded context 撞名）；**Rejected framings** 节（L49-53）明确否决 Ousterhout 的"实现行数/接口行数"深度定义——理由是"rewards padding the implementation"，改用深度=接口处杠杆率。
- `HTML-REPORT.md`（123 行）：Tailwind+Mermaid 双 CDN；前后对比图是候选卡**重心**（L55"the centrepiece"）；L61 Mermaid=graph 形关系主力；文末语气守则只用 LANGUAGE.md 词汇（L110-112）。
- `INTERFACE-DESIGN.md` 基于 "Design It Twice"（Ousterhout，L3）：先写面向用户的问题空间框定，再并行派 3+ 子代理各带互斥设计约束（L25-28：最小接口/最大灵活/最常见调用者/端口适配器），每个产出接口+用法+缝后隐藏+权衡，最后按 depth/locality/seam 对比。
- `DEEPENING.md` 按依赖四分类（L9-26）给深化安全策略：in-process 恒可深化、local-substitutable 用本地替身（PGLite）、remote-but-owned 走端口适配器、true-external 用 mock。

## 三、外部连接

- **SKILL.md 跨目录引用**是本库少见的显式跨 skill 依赖：其 SKILL.md L78 引 `../grill-with-docs/CONTEXT-FORMAT.md`、L80 引 `../grill-with-docs/ADR-FORMAT.md`——架构评审的文档副作用直接复用 grill-with-docs 的格式契约，不另立标准。
- **triage 是下游**：`skills/engineering/triage/SKILL.md:69` issue 需补 flesh 时跑 grilling。
- **setup 是配置面**：domain.md 种子模板（`skills/engineering/setup-matt-pocock-skills/domain.md:11`）教消费技能"缺席则静默，生产者惰性创建"。
- **ADR-0001 划其为软依赖**：文档缺席仍能工作、只是不够锐（`/usr-data/data2/repos/ai-trending/skills/docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md:8`）。
- **演进化石**：deprecated/ubiquitous-language 是 grill-with-docs 的前身（批式提取 UBIQUITOUS_LANGUAGE.md vs 现行内联沉淀），deprecated/design-an-interface 是 INTERFACE-DESIGN.md 的前身（同样 3+ 并行子代理+互斥约束）。

## 四、数据流

grill-with-docs 是**会话→文档的在线流**：术语决议立即 patch 进 CONTEXT.md（L74）→难逆转决策经三条件过滤（L80-84）→少数落 ADR。CONTEXT.md 被约束为纯词汇表——"totally devoid of implementation details. It is a glossary and nothing else"（L76）。

improve-codebase-architecture 是**文档→报告→文档的环**：读 CONTEXT.md+ADR→Explore 摩擦点→HTML 报告（临时目录）→用户选候选→grilling 中新术语回写 CONTEXT.md、否决理由回写 ADR——评审也在喂养语言层。输出永不直接改代码：SKILL.md L70 只问"Which of these would you like to explore?"。

## 五、设计决策

1. **为什么单段 ADR？** ADR-FORMAT.md:15：价值密度而非仪式感——多数决策一句话能说清，强制模板只会让人不写；可选节只在真有价值时出现。
2. **为什么术语必须带 _Avoid_？** CONTEXT-FORMAT.md:27：一概念多词时选最佳、其余列禁用——README:83 的"materialization cascade"一词替一段描述是 token 经济学，README:96-99 列三条连带收益（命名一致/库更可导航/思考更省 token）。
3. **为什么否决行数比深度？** LANGUAGE.md:51：行数比会奖励堆实现行数；改为"接口处杠杆率"（多少行为藏在多小的接口后），不可刷指标。
4. **为什么报告写临时目录？** SKILL.md L49：架构评审是一次性产物，落仓就是垃圾；时间戳文件名让每次运行拿到新文件。
5. **为什么 ADR 不许 re-litigate？** SKILL.md L66：ADR 冲突候选只在摩擦真实到值得重开时出现并明确标注——不断重提已定决策等于失去"知情"资格。
6. **为什么 3+ 子代理各带互斥约束？** INTERFACE-DESIGN.md:25-28："radically different"只能靠结构性互斥约束（最小 vs 最大 vs 默认最简）撑开方案空间。

## 六、新人提示

- 阅读顺序：grill-with-docs/SKILL.md（88 行）→CONTEXT-FORMAT.md→improve-codebase-architecture 五件套；LANGUAGE.md 是四份参考文档的地基，跳过它读 HTML-REPORT 守则会不知所云。
- 实操入口：任何一次改动前跑 `/grill-with-docs`；README 建议 `/improve-codebase-architecture` 每几天对代码库跑一次（`/usr-data/data2/repos/ai-trending/skills/README.md:137`）。
- 不要把 CONTEXT.md 当 spec 或 scratch pad 用（L76 明令禁止）；实现细节属于 ADR 或代码注释。
- ADR 三条件（难逆转/无上下文会惊讶/真实权衡）是**与门**，缺一跳过——给易逆转决策写 ADR 会把 docs/adr/ 变流水账。
- 多上下文仓的判断只看一个信号：根目录有没有 CONTEXT-MAP.md（L36）；写文件前先判断结构，避免把术语写错地方。
- GLOSSARY 与 CONTEXT-FORMAT 的同构证明"术语+定义+_Avoid_"三元组可迁移到任何项目。

*锚 34 处，全部 sed 现场核验 · understand-anything · 2026-11-02*
