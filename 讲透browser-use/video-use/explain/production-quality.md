# production-quality.md — 出厂验收清单：把"好看"拆成可勾选的硬指标

> 源码：`skills/manim-video/references/production-quality.md`（191 行 Markdown，纯提示词资产、零代码）。行号锚均从源文件逐一核实。

## ① 角色定位

在 manim-video 技能的 14 份 references 里，大部分文件回答"怎么用某个 API"（animations/mobjects/equations…），本文档回答更上游的问题：**"这段动画达到能交付的水准了吗"**。它是技能的验收闸门——SKILL.md L241 给它的定位是 "Pre-code, pre-render, post-render checklists, spatial layout, color, tempo"：三道时间闸门（写码前/渲染前/渲染后）加三组空间/色彩/节奏标准。

它的读者不是人而是 LLM agent。这决定了文体：所有标准都压成**可判定的数值规则**（buff ≥ 0.5、字号下限 18、同屏元素 ≤ 6、透明度三层 1.0/0.4/0.15），并用 GOOD/BAD 代码对照给出可执行先例。对抗的是 agent 的两个天然缺陷：写长代码时的规则遗忘，和"看起来差不多"的模糊自评——checklist 化让 agent 渲染前逐项自查，而不是渲染后靠运气发现字幕被裁掉。

它与主仓库（video-use 剪辑线）SKILL.md 第 7 步 "Self-eval (before showing the user)" 构成跨技能同构：两条流水线都在终点前设一道"先自己验收、再给人看"的闸门——一个用 timeline_view 看渲染帧，一个用本文档的 checklist 看动画。

## ② 内部结构

全文按生产时间线排布，两个 checklist 簇夹着四组质量标准：

**Pre-Code Checklist（L5-13）**：写任何 Manim 代码前的五项——旁白先行并标视觉节拍（L9）、场景清单含目的/时长/布局（L10）、调色板带语义分配（L11，`PRIMARY` = 主概念）、`MONO = "Menlo"` 定为字体常量（L12）、目标分辨率与画幅（L13）。这与 paper-explainer.md 的三道闸（narration→scene list→style constants）同构，是"先编剧后编程"方法论的操作化。

**Text Quality（L15-58）** 三条子规则：
- 重叠预防（L17-30）：边缘文本 `buff >= 0.5`（L21 GOOD vs L22 BAD——0.3 可能裁切）；同位置换内容必须 `ReplacementTransform` 而非裸 `Write`（L25-26）；可见文本 > 4 个时字号降 20（L28-30）。
- 宽度强制（L32-41）：任何可能长的 Text 先量 `text.width > config.frame_width - 1.0` 再 `set_width` 钳制（L38-40）。
- 字体一致性（L43-58）：`MONO = "Menlo"` 定义一次全文件复用（L47），L49-57 给正反示例。背后原因在 visual-design.md L63：Manim 的 Pango 渲染器对比例字体在所有字号下产生破碎字距——Pango 的根本限制而非 Manim bug。

**Spatial Layout（L60-87）**：坐标预算（L64-70）——默认 16:9 画框约 14.2 宽 × 8.0 高，扣边距后可用区 x ∈ [-6.5, 6.5]、y ∈ [-3.5, 3.5]，顶 y ∈ [2.5, 3.5] 标题区、底 y ∈ [-3.5, -2.5] 注释区、主内容 y ∈ [-2.5, 2.5]。"Fill the frame"（L73-79）要求空场景加背景网格/标题/出处/低透明装饰填充。最硬一条 L83：**同屏活跃元素上限 6 个**，超出只能三选一——旧元素降 0.3 透明度、删已完成使命的元素、拆两个场景（L84-86）。

**Animation Quality（L89-117）**：多样性审计（L90-96）要求相邻场景在动画类型、强调色、布局、节奏四维度至少不全同；节奏曲线（L98-110）五幕模板"慢→中→快(高潮)→慢(收束)"；转场三律（L112-117）：干净退场（`FadeOut(Group(*self.mobjects))`）、退场后 `wait(0.3)` 呼吸、**永远不要硬切**。

**Color Quality（L119-143）**：深底（#0D1117/#1C1C1C）上颜色要亮要饱和（L127 好例 #58C4DD/#83C167/#FFFF00；L128 坏例 #666666 隐形、#2244AA 过暗）；透明度三层法（L131-133）——结构元素（轴/网格）0.15、上下文 0.3-0.4、主体 1.0；色彩语义一致性（L135-143）：颜色一旦绑定含义就全片不变。

**Data Visualization（L145-163）**：图表最低要求（L147-152）——每轴有标签、Y 轴从 0 起、颜色对图例、至少标注最大值与对照点；数字变化用 `DecimalNumber` + `rate_func=rush_from` 平滑动画（L159-161），禁止 Text 跳变（L162）。

**Pre-Render（L165-179）与 Post-Render（L181-191）**：渲染前 11 项（先 `-ql` 全过再碰 `-qh`、文字场景 `-qm` 看字距、每场景设背景色、显著动画配 subcaption、字号 ≥ 18、全等宽、buff ≥ 0.5、干净退场、reveal 后 wait、颜色常量化、全片同一质量 flag）；缝合后 6 项人审（1x 速看全程、查同时动画混淆、文本阅读时间、转场无黑帧、音画同步、L190"前 5 秒决定观众走不走"）。

## ③ 外部连接

- **SKILL.md 主线**：L241 references 表收录；工作流 Step 6 REVIEW（SKILL.md L63）与 L183-187 的 preview still 命令是 Pre-Render 簇的执行入口；L111 的等宽字体铁律与本文档 L44-58 互为表里。
- **rendering.md**：L169-170 的 `-ql` 全过 / `-qm` 查字距依赖其 L25-27 质量预设表（-ql 854x480/15fps、-qm 1280x720/30fps、-qh 1920x1080/60fps）；L29 明说 -ql 文字字距差到不可用，这正是"文字场景必须 -qm 预览"的原因。
- **visual-design.md**：字体物理（Pango 等宽限制 L63）、推荐字体表（L71：默认 Menlo，替代 Courier New / DejaVu Sans Mono）、大标题短文本可用比例字体的例外（L88）——L44-58 的规则细化都在那边。
- **paper-explainer.md / scene-planning.md**：本文档 L9-13 的 Pre-Code 五项是这两个工作流文档产出的验收面。
- **跨技能同构**：主仓 SKILL.md 第 7 步自检（渲染输出逐切点回看）与本文档 Post-Render 簇是同一设计哲学的两条流水线实例。

## ④ 数据流

文档型资产，其"数据流"是 agent 在生产管线各时点的读取时序：

```
plan 阶段   ← L5-13 Pre-Code（验收 plan.md 是否齐备五要素）
code 阶段   ← L15-58 Text + L60-87 Layout + L89-117 Animation + L119-143 Color
             （写 scene.py 时作为内联规则约束代码生成）
render 前   ← L165-179 Pre-Render 11 项（-ql 全绿 → -qm 抽查字距 → 才许 -qh）
stitch 后   ← L181-191 Post-Render 6 项（人/agent 看片自查）
```

它不产生产物，而是给每一步产物发放行许可证——这正是"验收标准外部化"：判断好坏的依据固定在文档里，不随 agent 每次生成的自评措辞漂移。

## ⑤ 设计决策与取舍

**数值化一切**：把审美判断翻译成 buff ≥ 0.5、6 元素上限、透明度 0.15/0.4/1.0、字号 18 下限这样的硬数字。LLM 对"保持留白优雅"这类模糊指令执行一致性差，对数值断言高——这是把设计 review 变成单元测试的思路。

**GOOD/BAD 双栏先例**：几乎每条规则配正反代码对照（L21-22、L25-26、L49-57）。对代码模型，一个反例的约束力常常胜过三句描述——BAD 行同时充当"生成时绕开这个模式"的负样本。

**闸门前移**：Pre-Code 排在写码之前（L5），Pre-Render 排在 `-qh` 之前（L167-169 顺序写死"先 -ql 全过"）。渲染是管线最贵的操作（1080p60 一幕可达分钟级），把验收尽早塞进廉价阶段，是典型的"左移测试"。

**规则而非解释**：本文档几乎不讲"为什么"（为什么 6 个元素？为什么 tempo 要曲线？），原理层外包给 visual-design.md 和 animation-design-thinking.md——本文档因此可以极短极密，供 agent 渲染前快速通读；代价是单独读它学不到设计思想。

**"前 5 秒"条目（L190）**：把传播学经验（Hook 决定留存）塞进工程 checklist 末尾——这份文档最终服务的不是"渲染正确的视频"而是"有人看完的视频"。

## ⑥ 新人提示（坑/勘误）

1. **坐标预算只对默认 16:9 成立**：L64 的 14.2 × 8.0 来自 Manim 默认 `frame_height = 8`、宽 = 8 × 16/9 ≈ 14.22。若项目改了 `config.frame_height` 或做竖屏（video-use 主线就常出竖屏），L66-70 的可用区数字全部失效，需按比例重算。
2. **MONO = "Menlo" 是 macOS 专属**：Menlo 只预装在 macOS（visual-design.md L92-93：Linux 是 DejaVu/Liberation）。Linux 渲染环境照抄 `font=MONO` 会静默回退默认字体——跨平台项目应按 L71 替代列选 DejaVu Sans Mono。
3. **L29 的 -ql 陷阱有文档背书**：渲染前清单 L170 要求文字密集场景用 `-qm` 抽查 kerning，不是官僚主义——rendering.md L29 实证 -ql 的文字渲染"noticeably poor"，480p 下看着没问题的布局到 1080p 可能溢出。
4. **6 元素上限数的是"活跃"元素**：L83 说的是 actively visible——0.15 的背景网格按分层约定（L131）不计入注意预算，但 0.3-0.4 上下文层算不算要自己拿捏。
5. **L190 的 "Gibbs-like first impression" 措辞**：原文 "Is the Gibbs-like 'first impression' good?"——这个类比生僻（指 Gibbs 采样初始值决定整链分布的意味），不必深究，条目本意就是"前 5 秒定留存"。
6. **checklist 不含 Manim 版本差异项**：如 `BarChart`、`always_redraw` 等 API 在 Manim CE 不同版本间签名有漂移，本文档的示例片段（L159-161）按 CE 撰写；排障要转 troubleshooting.md，本文档只管"达没达标"不管"为什么报错"。
7. **与 SKILL.md 的红线部分重叠但措辞不同**：SKILL.md 讲 "buff≥0.5、替换前先 FadeOut" 作为实现红线，本文档把它们散布在 L21/L25——两处一致无冲突，但改规则时是双份维护点。

---
*下一篇：paper-explainer.md（论文转动画纪录片的编导手册）。*
