# 02 · 质量反馈双环：tdd 与 diagnose

> 对象：`/usr-data/data2/repos/ai-trending/skills/skills/engineering/tdd/`（6 文件，303 行）与 `/usr-data/data2/repos/ai-trending/skills/skills/engineering/diagnose/`（SKILL.md 117 行 + hitl-loop.template.sh 41 行）。两者共同回答 README 失败模式 #3"代码不工作"——解法是 agent 时代的反馈环纪律。

## 一、角色定位

`/tdd` 是**建设环**（红绿重构建功能），`/diagnose` 是**修复环**（硬 bug/性能回归排查纪律化）。公共哲学在 README:110-116：没有对真实运行的反馈 agent 就是盲飞；测试给一致反馈，调试交给诊断环。

体量反差有深意：tdd 用 6 文件 303 行讲可查阅的规范，diagnose 用单个 117 行讲必须每次全读内化的纪律。

## 二、内部结构

**tdd 六文件**是全库参考文档最多的 skill：

- `skills/engineering/tdd/SKILL.md`（109 行）：核心信条 "Tests should verify behavior through public interfaces, not implementation details."（L10）；好测试读起来像规格（L12）；**水平切片反模式**（L18-41）——"DO NOT write all tests first"（L20），批量测试测想象中的行为、测形状不测行为、行为破时通过行为好时失败；正解 tracer bullet 垂直切片（L29"One test → one implementation → repeat"，L31-41 对照伪码）。工作流：规划六项确认（L45-60，"You can't test everything"）→tracer bullet 首发（L62-71）→增量循环四规则（L73-87）→GREEN 后重构（L89-99"Never refactor while RED"）。每循环五项检查（L101-107）。
- `tests.md`（61 行）：好测试五特征（L17-24）；坏红信号六条（L38-45）；L47-60 createUser 对照最有教育价值——坏例直查库 `SELECT`，好例用 `getUser` 从接口验证。
- `mocking.md`（59 行）：只在系统边界 mock（L3-14，不 mock "anything you control"）；为可 mock 设计（L16-58）=依赖注入（L25-35）+**SDK 式接口优于通用 fetcher**（L37-58，每 mock 单一返回形状）。
- `deep-modules.md`（33 行）Ousterhout 深模块 ASCII 图解卡（L5-27）+接口三问（L29-33）。
- `interface-design.md`（31 行）可测试性三原则（L5-29）：接受依赖不创建/返回结果不副作用/小表面积——正反例全是 TypeScript。
- `refactoring.md`（10 行）六类重构候选速查。

**diagnose 两文件**：

- `skills/engineering/diagnose/SKILL.md`（117 行）六阶段，每阶段都有不可跳过的门。**Phase 1 建反馈环**（L12-51）是全文核心——"**This is the skill.** Everything else is mechanical."（L14）：有了快速、确定、agent 可跑的 pass/fail 信号，二分、假设检验、插桩都只是消费该信号；没有它"no amount of staring at code will save you"。十种构造手段按序尝试（L18-29）：失败测试→curl/HTTP 脚本→CLI 快照对比→无头浏览器→trace 重放→弃用 harness→属性/模糊循环→git bisect 自动化→差分环→HITL bash 模板。然后**把环当产品迭代**（L33-41）：更快/信号更锐/更确定——"A 30-second flaky loop is barely better than no loop. A 2-second deterministic loop is a debugging superpower."（L41）。非确定 bug 的目标不是干净复现而是**提高复现率**（L43-45："50%-flake bug is debuggable; 1% is not"）。真造不出环就停下明说（L47-49），要三样东西之一：环境访问/捕获工件/临时生产插桩许可——"Do not proceed to Phase 2 until you have a loop you believe in"。
- Phase 2 复现三确认（L57-61：复现的是用户描述的那个失败/可重复/症状已捕获）。Phase 3 假设（L65-75）：**3-5 条排序**再测（L67 防锚定）、逐条可证伪（L71"If <X> is the cause, then <changing Y> will..."）、**测试前给用户看**（L75，一句"刚部署过 #3"能瞬间重排）。Phase 4 插桩（L77-89）：一断点胜十日志、一次一变量、**debug 日志带前缀 `[DEBUG-a4f2]`**（L87 清理=一次 grep）、性能先测量后 bisect（L89）。Phase 5（L91-105）：回归测试**只在有正确缝时**写（L93-95），"If no correct seam exists, that itself is the finding"（L97）。Phase 6（L107-117）：五项清单+胜出假设进 commit+预防性发现移交 `/improve-codebase-architecture`（L117）。
- `scripts/hitl-loop.template.sh`（41 行）是第十种环：`step`（L17）与 `capture`（L22）驱动用户按步操作，L39-41 以 `KEY=VALUE` 回传给 agent——人手点的复现也进结构化循环。

## 三、外部连接

- **共享域语言层**：tdd L47 用域词汇命名测试与接口、diagnose L10 读词汇表与 ADR；两者均为 ADR-0001 定义的软依赖（`/usr-data/data2/repos/ai-trending/skills/docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md:8`）。
- **diagnose→架构技能移交**：其 SKILL.md L117 把"无正确缝/调用者纠缠"类发现移交 improve-codebase-architecture，且在修复落地**之后**——那时你比开工时知道得多。
- **tdd↔to-issues**：垂直切片/tracer bullet 概念在两处同现（tdd L29 与 to-issues L24），后者的 issue 拆分粒度即前者的测试推进粒度。
- **tdd/deep-modules.md↔improve-codebase-architecture/LANGUAGE.md**：同一 Ousterhout 思想的两个投影，tdd 版是 33 行入门图解，后者是 53 行完整词汇宪法。
- **diagnose 的 replay/harness 理念**与 prototype skill 的"throwaway harness"（弃用环境验证设计）共享"最小可运行环境"方法论。

## 四、数据流

tdd 是**单调递增的规格流**：行为清单→首测（tracer bullet）→最小实现→下测响应上循环所学……每圈产出行为代码+一条永不撒谎的规格。关键是**序列性**——规格必须从真实实现里长出来，不能批量预写。

diagnose 是**信号驱动漏斗**：现象→反馈环→复现确认→假设列表→逐假设插桩→定位→回归测试→清理移交。每阶段输出是下阶段门禁：没环不许复现、没复现不许假设、不可证伪不许插桩；HITL 模板让"人在环里"的数据也结构化回流。

## 五、设计决策

1. **为什么封杀水平切片？** L20-27 四条：测想象行为/测形状不测行为/对真实变化不敏感/未理解实现就承诺测试结构。"You outrun your headlights"（L27）是 agent 时代过度生成的精准隐喻。
2. **为什么 mock 只在系统边界？** 判据是控制权：自己控制的东西 mock 掉=测试与实现锁死（重命名内部函数就挂）；边界外（Stripe/时间）本就不可控。SDK 式接口（L37-58）让边界 mock 变享受。
3. **为什么假设 3-5 条且先给用户看？** L67 防单假设锚定；L75 经济学——用户一条部署信息胜过半小时插桩，且不阻塞 AFK。
4. **为什么 debug 日志带前缀？** L87"Untagged logs survive; tagged logs die."——清理=一次 grep，插桩不泄漏。
5. **为什么"无正确缝"是发现？** L95-97：bug 触发链无法在任何接口复现=架构在阻止回归测试——不是流程失败而是架构诊断结论。
6. **为什么性能回归禁日志优先？** L89：日志改变时序、只给点不给分布；先基线测量再 bisect——"Measure first, fix second."
7. **tdd 为什么 GREEN 前禁重构？** L99：重构需要全绿的安全网；红灯下重构是在无反馈状态下改代码，违反本 skill 的一切前提。

## 六、新人提示

- 最快吸收路径：tdd/SKILL.md L18-41（水平切片反模式）→tests.md createUser 对照（L47-60）→diagnose Phase 1 全节（L12-51）——三段读完灵魂到手。
- 用 `/tdd` 时先做规划六问（L51-58），特别是"哪些行为最该测"——L60 明说不能测一切，把火力集中在关键路径与复杂逻辑。
- 用 `/diagnose` 前自查：有 pass/fail 信号吗？没有先在十种手段里找（L18-29），别急着读代码——L14 说其余一切都是机械的。
- 复现步进类 bug 别追求 100% 复现：L43-45 教你 loop 100 次/并行/加压/注 sleep 把 1% 抬到 50%。
- 写 mock 前先问"这东西我控制吗？"——控制就别 mock（L10-14）；真要 mock 边界，先看 mocking.md L37-58 把接口改成 SDK 式再 mock，会舒服一个数量级。
- 两者都主动读 CONTEXT.md 与 ADR（tdd L47、diagnose L10）——想让他们说项目的话，先 `/grill-with-docs` 建词汇表。

*锚 33 处，全部 sed 现场核验 · understand-anything · 2026-11-02*
