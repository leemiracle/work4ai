# taste-skill 上手指南（ONBOARDING）

> 仓：Leonxlnx/taste-skill（本地 `/usr-data/data2/repos/ai-trending/taste-skill`，commit 1a6dc0a5）。**纯提示词资产库**：13 个 SKILL.md 即被安装物，全仓唯一可执行代码是 26 行 skill.sh。理解钥匙是提示词工程（指令层级/负面约束/输出强制），不是代码逻辑。

## 1. 库定位与分发机制

定位 "The Anti-Slop Frontend Framework for AI Agents"（README.md:8）：反 slop 前端品味升级库，图像 skills 产参考图交 coding agent 落地（README.md:23）。三个分发约定：①**安装即复制**——`npx skills add`（README.md:51）扫描 skills/，实现类与图像类同一入口（README.md:48）；②**install name ≠ 目录名**——`--skill` 取 frontmatter `name:`（README.md:54），目录 taste-skill 的 install name 是 design-taste-frontend（skills/taste-skill/SKILL.md:2）；③**两级索引**——skills/llms.txt 每 skill 一行供 LLM 枚举，本地 `source ./skill.sh <name>` 查路径（skill.sh:20-25）。`.github/copilot-instructions.md:5-11` 另以五条反 slop 宣言注入 Copilot。

## 2. 资产清单地图

37 文件四层：门面层（README/CHANGELOG/copilot-instructions/llms.txt）；skills/ 13 个 SKILL.md+stitch 的 DESIGN.md（选型表 README.md:86-107，决策指南 :109-118）；research/ 12 个 md（第 6 节）；资产层 logo+floria 三图。体量极不均（宪法 1206 行/output-skill 49 行）——"重量"在提示词文本本身。

## 3. 核心宪法 taste-skill v2 解剖

`skills/taste-skill/SKILL.md`（14 节+3 附录）按**生成时序**组织：§0 读题（六信号 :17→一行 Design Read :25→只问一问 :33→反默认 :38）；§1 三刻度盘基线 8/6/4+推断表+预设矩阵（:43-78）；§2 设计系统映射——12 官方系统装包（:86）vs 8 美学族手写（:106），铁律"不复刻官方 CSS/一项目一系统"（:102-104）；§3 默认栈 RSC+Tailwind v4+Motion（:132）+依赖核验（:156）；§4 最厚——serif 纪律点名封禁 Fraunces/Instrument_Serif（:180）、米色+黄铜调色板禁令（:192）、eyebrow 三节一现（:253）、Copy Self-Audit（:321）；§5 GSAP Sticky-Stack/Horizontal-Pan 规范骨架（:365）+硬禁 scroll 监听（:509）；§9 AI Tells（:595-701）——§9.G em-dash 全面封禁为最高频违规，措辞二值化"binary: zero"（:701）；§10 词汇表（:705）/§12 Block 契约（:835）；§11 重设计三模式+永不静默变更（:783-831）；§13 范围外（:896）；§14 Pre-Flight 六十余项（:910-979，单项不能诚实打勾=未完成）；附录 A/B/C 安装命令/文档链接/Liquid Glass 近似（:987-1206）。v1 完整保留（README.md:72-76）：无读题/无映射/无 Pre-Flight，用 LAYOUT_VARIANCE 别名（skills/taste-skill-v1/SKILL.md:60，v2 :78 明禁即针对它）。CHANGELOG.md:89-93：v1 易被略读、Tells 反复复发，故 v2 设默认。

## 4. 变体矩阵（平台×工作流×风格）

- **平台 gpt-tasteskill**（gpt-taste）：Python 伪随机（prompt 字符数为种子）打破"永远选第一项"（skills/gpt-tasteskill/SKILL.md:13-20）+H1 两行铁律（:31-34）+gapless bento（:42-44）+design_plan 核验（:67-74）。
- **工作流**：image-to-code 强制三步"生成图→分析→写码"（skills/image-to-code-skill/SKILL.md:63-69；"image is the design source" :128），九盘双 10（:73-92）；redesign-skill 三步序 Scan/Diagnose/Fix（skills/redesign-skill/SKILL.md:10-14）+九类审计（:18-130）+修复优先级字体第一（:159-169）。
- **风格三支**（方向已定后叠加，README.md:116）：soft 15 万美元代理风——"绝对零"禁令（skills/soft-skill/SKILL.md:13-19）、三氛围×三布局掷骰（:21-35）、Double-Bezel（:41-44）；minimalist Notion/Linear 极简——四色淡化粉彩（skills/minimalist-skill/SKILL.md:36-40）、1px #EAEAEA 铁律（:45）；brutalist 双视觉原型二选一禁混用（skills/brutalist-skill/SKILL.md:13）——零圆角（:71）、警示红（:57）、扫描线劣化（:82-87）。
- **输出与适配**：output-skill（第 6 节）；stitch-skill 译成 Google Stitch 语义设计系统（skills/stitch-skill/SKILL.md:9-11），示例 DESIGN.md（skills/stitch-skill/DESIGN.md:9-14）。

## 5. 图像生成线

三支"只产图不写码"（README.md:124-126）：**imagegen-frontend-web**——硬规则"每节一张独立横图，8 节页=8 图绝不合并"（skills/imagegen-frontend-web/SKILL.md:6-22），hero 反"左文右图"九种替代（:25-42）；**imagegen-frontend-mobile**——19 刻度盘六盘满值 10（skills/imagegen-frontend-mobile/SKILL.md:86-127）+mockup 纪律（:349）+反克隆屏（:713）；**brandkit**——九类"类别→符号"映射表（skills/brandkit/SKILL.md:117-121），默认 3×3 网格 4:3（:77-78），五种 logo 概念方法（:161-246）。

## 6. 懒惰研究三件套

research/（README.md:180 明言研究塑造 skills，导读 research/laziness/README.md）分根因/补救/发现：**根因四篇**——①RLHF 算力经济学：每 token 约 $0.0001 逼出简洁偏好（rlhf-and-compute.md:5）；②训练数据偏差：占位符模式被内化（training-data-bias.md:5-10）；③认知捷径：LazyBench 证模型主动降计算深度（cognitive-shortcuts.md:5-10）+"It is May"逆调节（:19-23）；④输出上限：200 万输入对 8 千输出不对称+消费级 32K 截断（output-limits.md:5）。**补救四篇**——温度概率对照表（parameter-tuning.md:21-23）、心理刺激表"$200 tip +45%"（prompt-engineering.md:5-13）、**SKILL.md 懒加载：frontmatter ~100 token 发现钩子+正文按需加载，35% 上下文节省，描述具体度 68%→90% 发现率**（architectural-patterns.md:5-17，本仓 skills/ 架构的理论自证）、五模板（reference-prompts.md:7）。**发现**——2025-12 三实验，结论"懒惰是对齐训练的行为伪影而非能力失败"（empirical-results.md:32-38）。**output-skill 是产品落地**（skills/output-skill/SKILL.md）：占位符硬失败清单（:12-20）+三步回对（:22-26）+断点续写（:28-41）。

## 7. 设计哲学

1. **负面约束优先、措辞二值化**：每 skill 有禁令清单；em-dash 从"少用"升为"zero"（skills/taste-skill/SKILL.md:701）。
2. **可机械执行的检查表收尾**：v2 §14/soft §8/gpt design_plan——把品味翻成可数谓词（eyebrow ≤ ceil(节数/3)，skills/taste-skill/SKILL.md:933）。
3. **随机化对抗路径依赖**：gpt 伪随机、soft 掷骰、image-to-code 组合引擎——承认统计默认，用显式随机源打破。
4. **诚实规则+上下文经济学**：不手写官方 CSS（:102）、Liquid Glass 必标近似（:1113-1118）；SKILL.md"精头重身"与 llms.txt 枚举层皆出自懒加载研究。

## 8. 新人上手路径

①README.md:80-126 选型表建地图→②精读 skills/taste-skill/SKILL.md，对照 CHANGELOG.md:16-105 当导读→③对比三支风格禁令表做"同一 brief 三语言"实验→④读 research/laziness/README.md+根因四篇，再回读 output-skill 49 行→⑤看 examples/floria-*.webp 对照 §14 验证闭环。

## 勘误（与图谱摘要/任务书不符处，以文件为准）

1. soft 检查矩阵：图谱称"八项"，实际 §8 清单 **11 项**（skills/soft-skill/SKILL.md:88-98）。
2. output-skill 暂停标记：图谱写作连字符，文件实际 **em-dash**（skills/output-skill/SKILL.md:38）；封禁射程是产出页面非 skill 文件。
3. imagegen-mobile 刻度盘名：图谱误拼 "DISCIPLITY"，实际 **MIN_TEXT_SIZE_DISCIPLINE**（skills/imagegen-frontend-mobile/SKILL.md:126）。
4. 跨 skill serif 矛盾：stitch-skill/SKILL.md:51 与 DESIGN.md:52 把 Fraunces/Instrument Serif 列**推荐**，宪法 :180 明令**封禁**。
5. skill.sh 键命名：唯 [gpt-taste]（skill.sh:7）取 install name，其余 12 键取目录名，照抄去 npx 会失败。
6. "84 小节"口径：imagegen-web `##` 主节实测 **21 个**（skills/imagegen-frontend-web/SKILL.md:78）。
7. v1 别名遗留：LAYOUT_VARIANCE（skills/taste-skill-v1/SKILL.md:60）被 v2 :78 明禁。
8. brutalist 状态：llms.txt:12 标 "(Beta)"，README.md:96 未标。

*产出：understand-anything 讲透流水线 · 2026-11-02 · 图谱 37n/81e/10 层/14 步 · 源仓只读*
