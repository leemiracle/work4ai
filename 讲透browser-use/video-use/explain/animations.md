# skills/manim-video/references/animations.md 精讲 — Manim 动画 API 的作战手册

## 一、角色定位：14 篇参考里的"动词表"

manim-video 技能的结构是"宪法 + 图书馆"：SKILL.md 定标准与流程，references/ 14 篇分领域供查。其中 `animations.md`（283 行）被列在 SKILL.md References 表**第一行**（228 行："Core animations, rate functions, composition, `.animate` syntax, timing patterns"）——动画是 Manim 的"动词"层：mobjects.md 管名词（画什么），本篇管动作（怎么动）。子代理写 script.py 时，节奏、缓动、编排、时序模式全部从这里取。

它的存在价值是防御性的：LLM 对 Manim API 的记忆混乱且版本敏感（SKILL.md:27 锚定 CE v0.20.1），把经验证的用法片段固化在提示词侧，子代理照抄即可，无需依赖参数记忆。

## 二、内部结构：概念 → 词法分类 → 缓动 → 编排 → 高级模式

**核心概念（3-7 行）**一句话定调："An animation is a Python object that computes intermediate visual states of a mobject over time. Animations are objects passed to `self.play()`, not functions."（5 行）——动画是**对象不是函数**，这是理解 Manim 一切 API 的钥匙：`Create(circle)` 构造一个动画实例交给 play 调度。7 行立即补一条纪律：run_time 默认 1 秒，重要动画必须显式指定。

**词法分类（9-85 行）**按语义分五族，每族 3-5 个最常用成员配一行代码：
- 创建族（11-17 行）：`Create`（描轮廓）、`Write`（模拟手写，用于 Text/MathTex）、`FadeIn`、`GrowFromCenter`、`DrawBorderThenFill`；
- 消除族（21-25 行）：`FadeOut`、`Uncreate`（Create 逆过程）、`ShrinkToCenter`；
- 变换族（29-44 行）是重头戏，44 行的 Critical 注记是全篇最重要的坑位知识："After `Transform(A, B)`, variable `A` references the on-screen mobject. Variable `B` is NOT on screen."——Transform 原地改 A，B 从未上屏；后续操作 B 必须用 `ReplacementTransform`（35 行）；41 行另有公式智能变形 `TransformMatchingTex`；
- `.animate` 语法（48-51 行）：属性动画的现代写法，支持链式 `circle.animate.shift(RIGHT * 2).scale(0.5)`；
- 运动族（64-76 行）：`MoveAlongPath`（沿任意 VMobject 路径，76 行注明位置由 `point_from_proportion()` 计算）、`Rotate`（支持 about_point）、`Rotating`（连续旋转）；强调族（80-85 行）：`Indicate`/`Circumscribe`/`Flash`/`Wiggle`。

**Rate functions（88-95 行）**是节奏的数学：`smooth`（默认缓入缓出）、`linear`、`rush_into`/`rush_from`、`there_and_back`。239-258 行续表：`running_start`"pulls back before going forward (anticipation)"（250-251 行，动画十二原则的预期感）、`not_quite_there(0.7)`（只走到七成）。224-237 行的 `squish_rate_func` 是精确编排利器：把任意 rate function 压进时间窗子区间（230-234 行三个元素分别在 0-50%、25-75%、50-100% 窗口入场），237 行注明重叠控制比 LaggedStart 更精确。

**编排（97-111 行）**四件套：一个 play 多动画即同时（101 行）；`AnimationGroup(lag_ratio=0.2)` 错峰（104 行）；`LaggedStart` 逐个启动（107 行）；`Succession` 单 play 串行（110 行）。

**字幕（121-132 行）**双写法：独立 `self.add_subcaption("Key insight", duration=2)`（125 行）或内联 `subcaption=`（129 行），132 行指出 Manim 自动生成 .srt——呼应 SKILL.md:161"Subtitles on every animation"。

**Timing patterns（134-147 行）**三个成品节奏模板，与 SKILL.md:89-97 速度表互为表里：pause-after-reveal（关键公式后 wait 2 秒）、dim-and-focus（旧内容压 0.3 透明度同时新内容入场，SKILL.md:19 透明度分层的实操）、clean exit（`FadeOut(Group(*self.mobjects))` 清场，对应 SKILL.md:164）。

**高级模式（149-282 行）**六个专题：`always_redraw`（149-169 行）每帧重建 mobject，166 行成本注记"recreates the mobject every frame. For simple property tracking, use `add_updater` instead (cheaper)"；`TracedPath`（171-186 行）轨迹追踪，183 行 `dissipating_time=0.5` 消散拖尾，186 行列适用场景（梯度下降、行星轨道）；`FadeTransform`（188-207 行）解决 Transform 中间态扭曲——193-194 行对比"UGLY: Transform warps circle into square through a blob"vs 197 行"SMOOTH"，207 行的推荐原则值得背诵：**异形之间用 FadeTransform，同形（圆→椭圆、公式→公式）才用 Transform**；`ApplyMatrix`（209-222 行）线性变换可视化，222 行指向 camera-and-3d.md；`ShowIncreasingSubsets`（260-271 行）算法可视化逐元素揭示；`ShowPassingFlash`（273-282 行）光沿路径流动，281 行点名适合数据流/电信号。Updaters 预告（114-119 行）ValueTracker 联动，完整版在 updaters-and-trackers.md。

## 三、外部连接：SKILL.md 路由入口 + 平行参考互链

上游：SKILL.md References 表第一行（228 行）是唯一登记入口；SKILL.md:128 的入场动画多样化要求（"vary between Write, FadeIn, GrowFromCenter, Create"）直接点名本篇词法表。横向互链两处显式：222 行指向 camera-and-3d.md 的 LinearTransformationScene；updaters 专题由 updaters-and-trackers.md 承接。隐式依赖 mobjects.md（动画的作用对象）与 scene-planning.md（节奏在叙事中的位置）。

跨技能呼应最有趣：根 video-use SKILL.md:234-239 为 PIL/Remotion 动画定义了 `ease_out_cubic`/`ease_in_out_cubic` 两个 Python 缓动函数并断言"never `linear`, it looks robotic"（230 行）——本篇 91 行的 `rate_func=linear` 同样只作对照项存在。**同一缓动哲学在两个引擎各自实现**：Manim 用内置 rate_func，PIL 路径手写三次函数——"never linear"是 video-use 全仓级动画律，不隶属单一引擎。

## 四、数据流：本篇不流通运行时数据，它流通"验证过的代码片段"

作为提示词侧参考，输入输出都在 token 空间：子代理读 SKILL.md 被路由至此 → 摘取片段进 script.py → 片段成为 Scene 方法体。唯一会被下游消费的运行时副产物是 132 行的自动 .srt——但进入 video-use 剪辑管线后字幕以 render.py 的 master.srt 为准，Manim 字幕只服务独立成片场景。

片段的"验证过"属性是数据质量关键：全部示例对齐 Manim CE v0.20.1（SKILL.md:27），44 行 Critical 注记这类坑位知识恰是 LLM 记忆最不可靠、运行时最难调试的一类——错误不报异常，只是画面上"少了个东西"。

## 五、设计决策与取舍

**按动词语义而非字母/类层次组织**：五族分类（创建/消除/变换/运动/强调）直接映射叙事意图——"让它出现""让它消失""让它变成"，子代理从意图到 API 零翻译成本，比官方文档的类继承树更适合 LLM 检索。

**每段配一行行为注释而非完整场景**：12 行 `self.play(Create(circle))  # traces outline`——注释承载语义差异，拒绝 30 行可跑样板，信息密度最高；代价是新手需回 SKILL.md:141-158 看完整骨架。

**坑位知识显式加粗（Critical/Recommendation/Note）**：44、166、207 行三处粗体判断句都是"默认做法在此场景是错的"的反直觉知识——文档把最贵的那类错误（静默的画面错误）前置标注。**高级专题收在尾部**：149 行以后是二读材料，一读只看 3-147 行就够写合格场景。

## 六、新人提示：坑与勘误

1. **Transform 的变量陷阱是第一大坑**（44 行）：`Transform(A, B)` 后继续操作 B 是 None 操作——画面上没有 B。要继续用新对象就用 ReplacementTransform；SKILL.md:203-206 的红线（替换文字用 ReplacementTransform）正是这条的推论。
2. **linear 缓动全仓禁用**：本篇 91 行与根 SKILL.md:230 双重钉版，机器人感来源。
3. **always_redraw 有每帧重建成本**（166 行）：简单跟随用 add_updater，只有"几何本身依赖动画对象"（Brace 跟随缩放中的方块）才值得 always_redraw。
4. **subcaption 优先内联写法**（123-130 行）：内联 `subcaption=` 保证字幕与动画严格同拍；独立 add_subcaption 要自己排 duration，快节奏场景容易踩到上一条还没消失。
5. **squish_rate_func 与 LaggedStart 别混用**（237 行）：两者都做错峰，嵌套得到复合延迟；精确重叠控制选 squish，整体节奏感选 LaggedStart。
6. **本篇不覆盖 3D 相机动画**：ThreeDScene 相机控制在 camera-and-3d.md（SKILL.md:233）；版本漂移提醒——示例锚定 CE v0.20.1（SKILL.md:27），升级环境后 `subcaption_duration` 等参数名历史上有过变动，遇到 AttributeError 先核版本再怀疑用法。
