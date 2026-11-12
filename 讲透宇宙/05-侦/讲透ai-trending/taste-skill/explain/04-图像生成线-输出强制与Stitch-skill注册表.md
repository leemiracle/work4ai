# 04 · 图像生成线、输出强制与 Stitch 适配

> 对象：三支只产图不写码的 skill（imagegen-frontend-web/mobile/brandkit）、输出端的 output-skill 与 stitch-skill（附 DESIGN.md），以及全仓唯一可执行代码 skill.sh。共同覆盖宪法射程外的两类交付物：**图**与**受约束的完整输出**。

## 一、角色定位

图像线是"图像模型可当设计引擎"环境的产物：README.md:23 把三支 imagegen 与 ChatGPT Images 等配对，产出参考图交 Codex/Cursor/Claude Code 实现（README.md:124-126）。三支 frontmatter 即声明"generates images only...Does not write code"（skills/imagegen-frontend-mobile/SKILL.md:3-4），与实现类的分工靠交付物类型切分（README.md:82）。output-skill 与 stitch-skill 是**输出端的两类强制**：前者管"交付必须完整"（流程级），后者管"规则翻译进另一个生成器"（平台适配级）。skill.sh 是 26 行本地注册表，属维护者自用基础设施。

## 二、内部结构

**imagegen-frontend-web（987 行 21 主节）**：顶部两条 READ FIRST 压阵——①硬输出规则"Generate one separate horizontal image PER section. Always. No exceptions."（skills/imagegen-frontend-web/SKILL.md:6-13），landing 默认 6 节=6 图（:16-17）；②hero 构图偏置"left-text / right-image is the most overused AI pattern"（:27），九种替代构图（:29-39）。正文：§1 刻度盘（:78）、§2 变异引擎（:165）、§5 页面切片（:397）、§8 反 slop 五类（:521）、§15 站点包（:789）。

**imagegen-frontend-mobile（1465 行 38 节）**全仓最长：**19 刻度盘**（skills/imagegen-frontend-mobile/SKILL.md:86-127）在三盘上加 PLATFORM_AWARENESS/TEXT_READABILITY_PRIORITY 等，六个满值 10 把可读性与一致性钉成不可协商项。结构规则：§2 平台模式 iOS/Android（:152-193）、§9 默认 mockup 在场（:349-369）、§10 设备框纪律（:371-407）、§21 反 AI tells（:713-759：假金融图表/克隆引导屏/假品牌名 NovaCore）；scope 不服务网站/落地页/代码（:41-50）。

**brandkit（798 行）**：**策略先于视觉**——# BRAND STRATEGY FIRST 先推断 category/audience/symbolic metaphor（skills/brandkit/SKILL.md:97-108），配九类"类别→符号逻辑"映射表（:117-121：Developer tool→cursor/bolt；Security→shield/eye/seal），落款"Do not pick symbols randomly"（:123）。默认 3×3 网格 4:3 概览板（:73-94）；五种 logo 概念方法（:161-246）×八种视觉模式（:339）构成变异空间。

**output-skill（49 行）**四件套：基线"A partial output is a broken output"（skills/output-skill/SKILL.md:10）；占位符黑名单（:12-20）；三步回对（:22-26）；断点续写（:28-41，详见 03 篇）。

**stitch-skill+DESIGN.md**：Google Stitch 翻译层——把反 slop 规则转写成 Stitch 能解释的自然语言 Visual Descriptions（skills/stitch-skill/SKILL.md:9-11），产 DESIGN.md 单一事实源。九步指令 Atmosphere→Palette→Typography→Hero→Components→Layout→Responsive→Motion→Anti-Patterns（:29-113），每步"Stitch 语汇+精确数值"双轨（"Descriptive Name + Hex Code + Functional Role" :38）。DESIGN.md 是完整实例：四盘配置表（skills/stitch-skill/DESIGN.md:9-14）+九节设计系统，含四选一强调色（:32-36）与响应式五档实测（:89）。**skill.sh**：`declare -A SKILLS` 13 条名→路径（skill.sh:4-18），纯只读查表无副作用。

## 三、外部连接

安装面：三支 imagegen 与实现类同住 skills/ 顶层同一 npx 入口（README.md:193-194），install name 与目录名一致。管线上下游：imagegen 产图→image-to-code 消费写码（README.md:126）；image-to-code §4"每节一图"（skills/image-to-code-skill/SKILL.md:162-179）与 imagegen-web 硬输出规则（:6-22）是同一思想两端——生成端定数量纪律，消费端定提取纪律。stitch-skill 有**双消费者**：DESIGN.md 先喂 Stitch 出静态屏，§8 动效意图节再服务下游编码 agent（DESIGN.md:92"Stitch generates static screens"），一份文档两个读者。output-skill 是横向补丁可与任何 skill 组合（README.md:117）。skill.sh 孤立：不被文档引用，键名与 install name 不一致见 onboarding 勘误 5。

## 四、数据流（图像线的生成纪律）

三支 imagegen 共享**四段式纪律链**：①**数量先行**——web"每节一图"（:6-22）、mobile §4"generate enough screens"（:211-238）、brandkit 固定一张板，都在文件最前锁死产出数量，对抗"一张压缩大图糊弄"默认（web :23 首条即"one single giant compressed image"）。②**组合变异**——web §2 七维引擎（:165）、mobile §22（:761）、brandkit 概念方法×视觉模式，与 gpt-taste 的 RNG 同源，防屏幕克隆。③**一致性约束**——web §16（:823）、mobile §7"one clear product system"（:287-322）：结构变、系统不变。④**反模式收口**——三张清单（web §8/mobile §21/brandkit :689）禁的多数是**图像模型特有** slop（假仪表盘 spam/玻璃卡片堆叠），与代码线 AI Tells（em-dash/节号 eyebrow）几乎不重叠——两类生成器指纹不同，禁令清单就不同。stitch 链则是"规则→语义翻译→结构化文档→双端消费"：宪法规则→Stitch 语汇（"generously rounded corners"而非"rounded-xl"，stitch-skill/SKILL.md:179）→DESIGN.md 固化→双端消费。

## 五、设计决策

- **交付物类型做第一分割**：图像三支同目录同安装命令，但 frontmatter 显式声明"Does not write code"（llms.txt:5-7）——用描述层而非目录结构告知 agent 能力边界。
- **刻度盘谱系扩散**：三盘（宪法）→九盘（image-to-code）→四盘（stitch）→十九盘（mobile）——刻度盘是本仓参数化原语，各 skill 按需增删。
- **stitch 线的滞后**：stitch-skill/SKILL.md:51 与 DESIGN.md:52 仍推荐 Fraunces/Instrument Serif，而宪法 v2 已封禁（skills/taste-skill/SKILL.md:180）——全仓唯一跨线冲突，以宪法为准。
- **output-skill 极简主义**：49 行对比宪法 1206 行——输出强制只要黑名单+流程+协议；"每个 skill 只做一件事"（README.md:82）执行得很彻底。

## 六、新人提示

1. 三支用法看 README.md:105-107 即可选对：web=站点 comp 图、mobile=App 屏与流程、brandkit=品牌板。
2. mobile 的 19 盘别全记：六个满值 10 盘代表不可协商项，其余可调。
3. stitch-skill 的正确读法是把 DESIGN.md 当填空模板：先改四盘配置表，再按九节替换项目值（"给 agent 的文档要带精确数值"，stitch-skill/SKILL.md:168）。
4. output-skill 只管文本/代码截断，图像数量纪律由 imagegen 自己管——两类"不完整"需要两套约束。
5. 想加新 skill：复制 SKILL.md 改 frontmatter→补 llms.txt/README 表/skill.sh 三处注册；缺一处会让某种消费方式漏掉它。

*本系列四篇完。配套：onboarding/ONBOARDING.md（全仓 8 节导览+勘误 8 条）。*
