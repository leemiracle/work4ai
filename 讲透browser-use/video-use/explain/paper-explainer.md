# paper-explainer.md — 论文转动画：写给 LLM 编导的纪录片手册

> 源码：`skills/manim-video/references/paper-explainer.md`（256 行 Markdown，提示词资产）。行号锚均从源文件逐一核实。

## ① 角色定位

在 manim-video 技能的 references 里，本文档是个异类：其他文件是 API 速查（animations/equations/graphs-and-data…），它是**唯一一份完整的工作流指南**——回答的不是"某个类怎么用"，而是"一篇 30 页的论文如何变成一段 5 分钟的动画"。SKILL.md L239 给它的定位是 "Turning research papers into animations — workflow, templates, domain patterns"：工作流、模板、领域模式三层。

核心命题在开头两段钉死（L7-9）：论文的任务是**证明结论为真**，视频的任务是**让观众理解为什么真、以及为什么重要**——所以翻译绝不是"把论文念出来配图"（L7 "The translation is NOT 'read the paper aloud with pictures'"），而是"提取核心洞见，用视觉叙事让它变得显然"。这个定位句是全文的价值观锚点，后面所有模板都由它推导。

值得注意的档案学事实：SKILL.md L33-39 用例路由表里 "Paper explainer" 一行（L38）指向的是 `references/scene-planning.md` 而非本文档——本文档只出现在 L239 参考总表。按用例表走流程的 agent 不会自动读到这份更专门的指南（见⑥勘误 1）。

## ② 内部结构

全文按制作时间线展开，七段结构：

**为什么/animate 的本质（L5-9）**：如上，两种媒介两种任务。

**受众三档（L11-21）**：动笔前先决定观众——公众（慢速、多类比、只讲直觉、跳过证明）/ 本科生（中速、关键方程、跳过推导）/ 研究者（快速、完整方程、证明草图）。L21 点明"这决定了词汇、节奏、哪些节要动画、展示多少数学"——受众选择是所有后续参数的根。

**5 分钟模板（L23-49）**：六段式时间表（L27-34）：Hook 0:00-0:30（惊人结果或挑衅问题）→ Problem 0:30-1:30（此前缺什么）→ Key insight 1:30-3:00（核心想法，占最大时长）→ How it works 3:00-4:00 → Evidence 4:00-4:30 → Implications 4:30-5:00。配套取舍清单：跳过项（L37-42）——相关工作一句话带过、实现细节除非是贡献本身、消融最多一张图、证明只展示关键一步、超参调优全跳；放大项（L44-48）——核心洞见拿最多屏幕时间、几何直觉（"论文有数学就展示它意味着什么"）、前后对照是最有力证据。

**三道前置闸（L50-98）**：Gate 1 旁白（L52-65）——**先写全旁白再写任何代码**，每句对应一个视觉节拍；L54 是全文最硬的一句："If you can't write the narration, you don't understand the paper well enough to animate it"（写不出旁白=没读懂论文）。L56-64 给带 `[VISUAL: ...]` 标记的旁白示例（Chinchilla 数据/参数比例）。Gate 2 场景清单（L67-78）：旁白切成一个 Scene 一个类。Gate 3 风格常量（L80-98）：style.py 先行，L94-97 演示色彩语义映射——`MODEL_COLOR = PRIMARY`（"模型"）、`DATA_COLOR = SECONDARY`（"训练数据"）、`BASELINE_COLOR = HIGHLIGHT`（"以前的做法"）、`RESULT_COLOR = ACCENT`（"我们的结果"），与 production-quality.md L135-143"色彩语义全片一致"首尾呼应。

**方程的第一性讲法（L100-138）**："What would you do?" 五步模式（L104-110）：白话提出问题 → 问最简单的解法 → 动画展示它为何失败（L107 "animate the failure"）→ 引入论文方案作为修复 → **这时**才亮方程——"it now feels earned"（L110，方程是挣来的不是塞给观众的）。L112-119 用注意力机制举例（朴素全连接 O(n²) 信息过载 → 让每个词自己选择看谁）。配套 equation reveal 策略（L121-138）：先 `set_opacity(0.15)` 淡入完整目标式（L126-127），再逐项 `set_color_by_tex` 高亮 Q/K/V 配人称化标签（L130-137："Query: what am I looking for?"）。

**架构图渐进构建（L140-181）**：progressive build 四步（L143-149）：组件单独出现讲解 → 箭头生长 → 下一组件出现 → 重复直至完整。L153-161 给 `make_box` 工厂（RoundedRectangle + 文字 Group），L163-167 演示 encoder→GrowArrow→decoder 节奏（每个 FadeIn 后 wait(1)）。数据流动画（L170-181）：构建完图后让 ACCENT 小圆点沿管线走（L176-181 `MoveAlongPath` + `Flash`）。

**结果动画与领域模式（L183-247）**：柱状图前后对照是最常见证据形态（L189-210）——先揭示 baseline 图、wait(1.5)、再揭示 ours 图，`+35% avg` 高亮落在两者之上（L201-209）；训练曲线（L211-226）用 `ValueTracker` + `always_redraw` 让曲线随 epoch 标签实时生长（L215-225）。领域模式三分（L228-247）：ML 论文（数据流管线/训练曲线/注意力热图/嵌入散点/损失曲面）、物理数学（LinearTransformationScene/向量场/相空间轨迹）、系统论文（渐进管线/ShowPassingFlash/ZoomedScene/延迟吞吐对照）。

**五大常见错误（L249-255）**：想覆盖全文（L251："5 分钟讲透一个洞见，覆盖一切=什么都没讲"）、拿摘要当旁白（学术写作给读者不给听者）、符号先于意义（"从不在展示符号前先展示它代表什么"）、跳过动机（Problem 段是让观众在乎的原因）、全程同速（Hook 和 Key insight 需要最多视觉能量，大数字后要停顿）。

## ③ 外部连接

- **SKILL.md**：L239 参考总表收录；五步工作流的 plan.md 阶段（L133-135）是三道闸的宿主；用例表 L38 的路由与本文档的关系见勘误。
- **equations.md**：L130-137 的逐项高亮依赖其 `set_color_by_tex`（L186-192）；公式推导动画细节全部外包。
- **updaters-and-trackers.md / graphs-and-data.md**：L215-225 训练曲线是 ValueTracker 三步模式的应用实例，API 细节在那两份。
- **mobjects.md**：L153-161 的 Group/RoundedRectangle/next_to 定位。
- **production-quality.md**：L9-13 Pre-Code 五项是三道闸产物的验收面；L190"前 5 秒"与本文档 Hook 段互证。
- **主仓 video-use**：manim 动画在剪辑线上作为 overlay 资产被并行子代理生产（主 SKILL.md L89），本文档是那些子代理的创意方法库。

## ④ 数据流

```
research paper（PDF/arXiv）
 → 受众决策（L15-19 三选一：决定词汇/节奏/深度）
 → Gate 1：全文旁白（每句一视觉节拍，[VISUAL] 标记）
 → Gate 2：场景清单（一句旁白 → 一个 Scene 类）
 → Gate 3：style.py 色彩语义常量
 → 场景代码（方程五步法 / 架构渐进构建 / 结果对照图，按需取用）
 → 渲染缝合（rendering.md）→ 出厂验收（production-quality.md）
```

数据流的铁律是**单向闸门**：不过旁白闸不许写场景，不过风格闸不许写代码；每级产物是下级的唯一输入，返工成本沿箭头递增。

## ⑤ 设计决策与取舍

**旁白先行的硬闸**：L54 把"写不出旁白"定性为"没读懂论文"——把理解问题前置到最廉价的阶段（写文字）来暴露。直接写代码的话，理解缺口会隐藏到渲染后才发现，返工最贵。

**"一个视频一个洞见"的减法哲学**：L251 明说覆盖一切等于什么都没讲。5 分钟模板里 Key insight 独占 90 秒最大段（L31），skip 清单比 expand 清单更长——**删减定义质量**。

**失败动画（L107）**：展示朴素解法为何失败而非直接给正确答案——认知上先制造缺口再填，比"正确答案演示"多叙事张力，代价是多写一个场景。

**色彩语义在写码前绑定（L94-97）**：颜色含义映射发生在 style.py 而非场景代码，使"全片一致"（production-quality.md L135-143）有机械保障——场景代码只引用常量，改语义只改一处。

**模板化而非自由创作**：六段时间表、五步方程法、四步渐进构建、两图对照——全是可复用骨架。LLM 在骨架上填空的产出稳定性远高于自由发挥；这是给机器用的编导手册，不是给人的艺术论。

## ⑥ 新人提示（坑/勘误）

1. **用例表路由缝隙（源码级勘误）**：SKILL.md L38 把 "Paper explainer" 路由到 `references/scene-planning.md`，本文档仅在 L239 参考总表登记——按用例表走的 agent 会错过这份专门指南。做论文动画应显式让 agent 读 paper-explainer.md，两者互补（scene-planning 给叙事弧，本文档给论文特化流程）。
2. **示例代码不可直接运行**：L56-64 是 markdown 旁白块；L161 的 `DIM`、L176 的 `ACCENT` 在各自片段外未定义——都是节选，拼装 script.py 时需自行补 style.py。
3. **L58-64 的 Chinchilla 数字是虚构示例**："7B 胜 70B"是叙事示例非引用数据，照抄进真实视频会变成事实错误。
4. **5 分钟时长表是锚不是律**：L25 说 "scale times proportionally for longer videos"——但 Hook 的 30 秒不宜随视频变长翻倍（注意力窗口不随长度增长），经验上保持 30-45 秒。
5. **受众三档没有"同行评审"档**：L15-19 最深到"研究生/研究者"（证明可 sketch）；要给评审人看补全证明，得自己加第四档并回 equations.md 的推导模式。
6. **BarChart 示例的 y_range 硬编码 [0,100]（L193-196）**：换数据集记得改，否则超 100 的柱子被裁顶——这正是 production-quality.md L150"Y 轴从 0 起"规则的暗面。
7. **L190 与 production-quality.md L190 同条**：两份文档都写"前 5 秒定留存"，是技能级共识——Hook 段永远值得最多迭代轮次。

---
*下一篇：equations.md（MathTex 速查与变换匹配旋钮）。*
