# 01 · 核心宪法 taste-skill v2：门面与规则体系

> 对象：`skills/taste-skill/SKILL.md`（install name design-taste-frontend，1206 行，14 节+3 附录）+ CHANGELOG.md 导读。全仓设计思想源头，理解其余 12 个 skill 的参照系。

## 一、角色定位

这是**反 slop 前端宪法**：把"AI 生成的前端都长同一张脸"当对抗目标，用规则体系强制 agent 走出默认分布。三重身份：①默认安装物——frontmatter `name: design-taste-frontend`（skills/taste-skill/SKILL.md:2）即 install name 定义处（README.md:54）；②图谱最大枢纽（fanIn 11），三刻度盘被 image-to-code/stitch/imagegen 系列各自扩展；③v2 实验版（README.md:88，actively iterating toward v2.0.0 stable），CHANGELOG.md:89-93 专门论证"为何把实验版设为默认"——v1 方向对但易被 agent 略读，生产测试同一批 Tells（em-dash/节号 eyebrow/假截图/坏 GSAP 触发）反复复发，v2 用硬规则+规范骨架+强制检查表补缺。射程开头即限定："Landing pages, portfolios, and redesigns. Not dashboards, not data tables"（:8），§13 再展开劝退六类场景并指路（:896-906）。

## 二、内部结构

14 节按**生成时序**排布：§0 读题（:13-39）→§1 三刻度盘（:43-78）→§2 设计系统映射（:82-118）→§3 默认栈（:122-157）→§4 设计工程指令（:161-348）→§5 动效与 GSAP 骨架（:352-515）→§6 性能无障碍（:519-548）→§7 刻度盘定义/§8 暗色协议（:552-591）→§9 AI Tells 禁令（:595-701）→§10 词汇表（:705-779）→§11 重设计协议（:783-831）→§12 Block Library 契约（:835-892）→§13 范围外（:896-906）→§14 Pre-Flight（:910-979）。三个机关值得细看：

**§0 一行 Design Read**：生成前必须宣告 "Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <design system or aesthetic family>"（:25-26，附三示例 :28-31）；歧义只问一个问题（:33-36），能推断就不问。这是把需求澄清压成最小仪式——省 token 又逼 agent 显式表态。§0.D Anti-Default 随后点名六大 LLM 默认（AI 紫渐变/暗色 mesh 居中 hero/三等宽卡/全局玻璃拟态/到处无限微动画/Inter+slate-900，:38-39）。

**§2 诚实规则**：12 个官方系统（Fluent/Material/Carbon/Polaris/Atlaskit/Primer/GOV.UK/USWDS/Bootstrap/Radix/shadcn/Tailwind，:86-100）必须装官方包，三铁律"不复刻官方 CSS/不 import 后 override 90%/一项目一系统"（:102-104）；反向 8 个美学族明说"没有官方库"用 web 标准手写并诚实标注（:106-118）；Liquid Glass 单列强调无官方包（:118，附录 C :1113-1118 展开）。

**§9.G em-dash 全面封禁**：最高频违规 Tell（:685），覆盖标题/eyebrow/pill/正文/引言/署名/按钮/alt text，连 en-dash 作分隔也禁（:693），只留普通连字符与数学负号（:695-697）。收尾自我解释：旧版"use sparingly"被历史性忽视，"The phrasing here is binary: zero em-dashes"（:701）——全仓"禁令二值化"哲学的原型。

## 三、外部连接

上游：README.md:86-97 选型表、llms.txt:1 机器摘要、CHANGELOG.md:24-32 逐节解释七大新节（§0/§2/§8/§11/§12/§13/§14）。下游：三刻度盘被 image-to-code 扩成九盘（skills/image-to-code-skill/SKILL.md:73-92）、stitch 译成语义档（skills/stitch-skill/SKILL.md:29-35）、imagegen-mobile 扩成十九盘；§9 清单被 redesign-skill 反向复用为审计项（skills/redesign-skill/SKILL.md:37）；§11 与 redesign-skill 分工——前者给三模式判定（Greenfield/Preserve/Overhaul，:787-790），后者给完整审计工具箱。历史：skills/taste-skill-v1/SKILL.md 完整保留（README.md:72-76 钉版命令），v1 无 §0/§2/§14 且用 LAYOUT_VARIANCE 别名（v1:60）——v2 :78 "never invent aliases like LAYOUT_VARIANCE" 正针对它；v1 独有 Creative Arsenal（v1:128）与 Motion-Engine Bento（v1:192），v2 改组为 §10 词汇表+§12 契约。

## 四、数据流（指令如何被消费）

安装后消费路径=全文注入+两处运行时强制：①npx 复制 SKILL.md 进项目，agent 先读 frontmatter（~100 token）决定加载正文——正是 research/laziness/remediation/architectural-patterns.md:5-17 描述的懒加载架构（精确描述换 90% 发现率）。②正文加载后 §0 读题→§1 定盘→§2 选基座，输出一行 Design Read 供用户纠偏。③生成中 §4/§5 正指令（含两段 GSAP 规范骨架 :365-473）与 §9 负指令同时生效；§5.D 硬禁 `window.addEventListener('scroll')`（:509-515）。④交付前 §14 是最后一道过滤器（:912），多项检查设计成机械可数——eyebrow 计数 ≤ ceil(节数/3)（:933）、"ZERO em-dashes" 单项（:920）——收尾"单个方框不能诚实打勾=页面没完成"（:979）。附录 A/B/C（:987-1206）是 vendored 的 reality anchors：真实 npm 命令（:989-1031）、官方文档链接（:1033-1109）、Liquid Glass 近似 CSS（:1142-1200），对抗训练数据里的虚构 API。

## 五、设计决策

- **时序化而非分类化**：规则按"读题→定参→选型→写码→验收"排列，agent 顺读即执行序；redesign-skill 的 Scan/Diagnose/Fix（skills/redesign-skill/SKILL.md:10-14）是同一思想在存量场景的重演。
- **正负约束配对**：几乎每条禁令有 override 路径（Inter 禁令配 public-sector 出口 :170；米色调色板配"品牌明说则可用" :207）——禁令是默认值修正而非审美洁癖（:234"failing any of these is shipping broken work"）。
- **禁令二值化**：em-dash"zero"（:701）取代"少用"、eyebrow 用公式而非形容词（:256）——v1→v2 最重要的措辞演进，CHANGELOG.md:36 单列。
- **宪法+契约分离**：§10 只给模式名（"a vocabulary, not a library" :707），§12 定 block schema（dial_compatibility 区间 :864-876、八节 body :878-887）但明说"schema defined here, blocks added iteratively"（:839）——防 agent 自由发挥坏实现。
- **代价**：1206 行全文注入不便宜；v2 用可数谓词的检查表对抗略读，本质是接受"长 prompt 会被跳读"并兜底。

## 六、新人提示

1. 先读 README.md:88 与 CHANGELOG.md:16-32 建"v2 新增什么"的框架再进正文，否则 14 节易迷路。
2. §14 检查表（:910-979）是最好的速查索引——每项回链节号，可反向定位规则原文。
3. 改文件前看 §12 契约：新 block 按 schema 落 blocks/ 目录，不是往正文加代码。
4. em-dash 封禁只约束**产出页面**（:699"anywhere visible to the user"）；本仓自己的文档（CHANGELOG/stitch 线）大量用 em-dash，不算违规但易误读。
5. 依赖 v1 精确行为的项目按 README.md:75 钉版 `--skill "design-taste-frontend-v1"`。

*下一篇：02 变体矩阵——宪法如何按平台、工作流与风格语言调参。*
