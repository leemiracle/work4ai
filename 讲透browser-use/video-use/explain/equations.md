# equations.md — 公式与 LaTeX：MathTex 速查与变换匹配的三级控制旋钮

> 源码：`skills/manim-video/references/equations.md`（217 行 Markdown，提示词资产）。行号锚均从源文件逐一核实。

## ① 角色定位

这是 manim-video 技能里数学排版线的主参考——SKILL.md L231 给它的一句话定位："LaTeX in Manim, derivations patterns"。用例路由表里它承接 "Equation derivation" 类任务（SKILL.md L34：`references/equations.md`），即"动画证明勾股定理"这类最经典的 Manim 场景。

Manim 之所以存在（3Blue1Brown 的起源场景就是数学动画），核心就在 MathTex：它把 LaTeX 源码编译成可动画的矢量图元，使"一个等式变形为另一个等式"成为一等公民的动画原语。本文档围绕这一个类展开，重心明显偏向**最难用对的 API——TransformMatchingTex**：217 行里近三分之一（L133-216）讲它的三个控制旋钮（substrings_to_isolate / key_map / matched_keys），是有意的篇幅分配（见⑤）。

它同时是 SKILL.md 第一条实现红线（SKILL.md L191 "Raw Strings for LaTeX"）的展开现场：L10 铁律 "**Always use raw strings (`r""`).**"——不写 r 前缀时 `\frac` 会被 Python 先吃成转义序列，LaTeX 收到残缺串。

## ② 内部结构

全文十六节，归为四簇：

**基础排版簇（L1-66）**：Basic LaTeX（L5-10）——单式 `MathTex(r"E = mc^2")` 与多行 `\\` 分行（L7）、raw string 铁律（L10）。Step-by-Step（L12-19）：Write → wait → `TransformMatchingTex(step1, step2)` 变形（L19），推导动画的最小完整单元。Selective Color（L22-27）：表达式拆成多参数传入（L25），每个参数是独立子图元，`eq[0].set_color(RED)` 按索引上色（L26-27）。Building Incrementally（L29-38）：泰勒展开五段构造、`Write(parts[0:2])` → `Write(parts[2])` 分批显式。Highlighting（L41-46）：`SurroundingRectangle` 画框 + `Indicate` 原地脉冲。Annotation（L49-54）：`Brace(eq, DOWN)` 花括号。Common LaTeX（L57-66）：分式/希腊/求和/积分/向量/极限六件套速查。

**环境簇（L68-117）**：Matrices（L68-86）——四种矩阵环境 `bmatrix`（方括号，L75）/`pmatrix`（圆括号，L77）/`vmatrix`（行列式竖线，L80）/`matrix`（裸矩阵，L83），amsmath 默认加载（L70）；L86 是关键分流提示：**要逐元素动画或给单个矩阵元上色，别用 MathTex 环境，改用 `IntegerMatrix`/`DecimalMatrix`/`MobjectMatrix`**——环境渲出的是一整块图元，没有元素结构。Cases（L88-97）：`\begin{cases}` 分段函数。Aligned（L99-117）：麦克斯韦方程组四行对齐（L104-111）；L114 钉版 "MathTex wraps content in `align*` by default"，其他环境用 `tex_environment="gather*"` 覆盖（L116-117）。

**推导模式簇（L119-131）**：DerivationScene 完整骨架——首式 Write 后 `s1.animate.set_opacity(0.4)` 压暗旧式、再 `TransformMatchingTex(s1.copy(), s2)` 在下方生成新式（L125-130）。`.copy()` 保留暗淡旧式的同时拿副本去变形，"推导史"留在屏幕上。

**变换控制簇（L133-216，全文重心）**：三个逐级精细的旋钮——
- `substrings_to_isolate`（L133-153）：稠密公式（QED 拉格朗日量例，L139-141）默认是"一整团"（one blob），传隔离清单（L143-147）后每个命名子串成为独立子图元（L149-150 逐项上色）。L153 钉死必要性："Essential for TransformMatchingTex on complex equations — without isolation, matching fails on dense expressions."
- `key_map`（L171-184）：源式与目标式间符号映射——`{"+": "-"}` 让加号碎片飞去变减号（L179-183），配 `path_arc=PI/2` 走弧线。
- `matched_keys`（L195-216）：公共子串歧义时显式指定对齐键（L208-213），配套 `t2c` 保持三行推导式颜色一致（L200-205）。L216 最终警告：不指定时按最长公共子串匹配，复杂等式上会跨项粘连（例："^2 = C^2" 匹配跨越项边界）。
- 另有 `set_color_by_tex` 独立节（L186-193）与多行分离参数法（L155-169：每行一个参数 + `.arrange(DOWN)`，各行独立 `Write(maxwell[0])`）。

## ③ 外部连接

- **SKILL.md**：L34 用例路由（Equation derivation → 本文）；L231 总表；L191 Raw String 红线源于 L10。
- **troubleshooting.md**：LaTeX 编译错误排障在那边，本文只管"怎么用对"。
- **mobjects.md**：L86 的矩阵元素级操作显式转介——MathTex 环境与 MobjectMatrix 的分工边界由本文划定。
- **paper-explainer.md**：其 equation reveal 策略（L123-138：整式淡入再逐项高亮 Q/K/V）是本文 Selective Color（L22-27）与 set_color_by_tex（L186-193）的组合应用。
- **animations.md / updaters-and-trackers.md**：动画类型与 tracker 动态公式细节。
- **主仓 video-use**：manim 技能是剪辑线的动画 overlay 子系统（主 SKILL.md L211：Manim 负责 "equation derivations" 等），公式推导是其四大主战场之一。

## ④ 数据流

```
LaTeX 源串（必须 r"" raw string）
 → MathTex(参数化的多段子串 / 单串+substrings_to_isolate)
    ↳ LaTeX 编译（amsmath 默认；包在 align* 环境）
    ↳ 每个参数/隔离子串 = 一个可独立操作的 submobject
 → 三类消费：
    着色：eq[i].set_color / eq.set_color_by_tex("E", BLUE)
    增量：Write(parts[0:2]) → Write(parts[2]) 分批入场
    变换：TransformMatchingTex(eq1, eq2
            [, substrings_to_isolate]  [, key_map={"+": "-"}]
            [, matched_keys=["A^2",...]]  [, path_arc=PI/2])
 → 渲染（rendering.md）→ 纠错走 troubleshooting.md
```

核心心智模型：**MathTex 的图元结构 = 构造时喂给它的参数结构**。想要"这一项单独动"，就必须在构造时让它成为独立参数或隔离子串——事后无法从一整团里拆出来。

## ⑤ 设计决策与取舍

**为什么把三分之一篇幅给 TransformMatchingTex 的三个旋钮**：它是 Manim 最惊艳（碎片飞舞重组）也最不可预测的 API——默认按最长公共子串匹配，稠密公式上几乎必然产生意外分组。文档的应对是把控制粒度分三级：隔离（构造期解决"什么是独立单元"）→ key_map（变换期解决"谁飞向谁"）→ matched_keys（对齐期解决"歧义时听谁的"），层层兜底。

**参数化构造优先于后处理**：Selective Color（L25）与 Multi-Line（L160-163）示范同一哲学——构造点就把逻辑结构写进参数列表，而非事后切子图元。构造期一次麻烦换操作期全部自由。

**速查式而非教程式**：每节都是"代码块 + 一句规则"，零叙述——给 agent 的检索友好格式，SKILL.md 引导按需跳节，通读需求为零；代价是人类新手初读干燥，需配 3Blue1Brown 视频建立直觉。

**环境知识显式钉版**：L70 "amsmath loaded by default"、L114 "wraps in align* by default"、L116 覆盖法——Manim 的 LaTeX 默认配置是隐性知识，文档显式化它，避免 `\begin{align}` 嵌套双重包裹报错。

**失败前置警告**：L153 与 L216 都是预防性钉版——展示用法的同时立刻声明失败模式，把 troubleshooting 工作量前移到 API 选型时刻。

## ⑥ 新人提示（坑/勘误）

1. **raw string 铁律的坑最阴**：L10 只说必须 r""，没展示反例——忘 r 时 `\frac` 不是合法转义会直接报错，但 `\n`/`\t` 开头的命令（如 `\tan`）会**静默**变成换行/制表符再传给 LaTeX，报错离案发现场很远。公式渲染出怪断行，先查 r 前缀。
2. **矩阵环境 = 不可拆的整块**：L86 的分流最易被忽视——`\begin{bmatrix}` 渲出的矩阵无法对单个矩阵元做动画或上色；要元素级操作立刻换 MobjectMatrix 家族（见 mobjects.md）。
3. **默认 align* 环境**：L114——多行公式里 `&`/`\\` 之所以能直接用，是 MathTex 自动包了 `align*`；内容自带环境（cases/aligned）嵌套其中合法，但再写 `\begin{align}` 会双重包裹报错。
4. **三旋钮选用顺序**：先 isolate（构造期，一劳永逸）→ 符号语义变化加 key_map → 仍错位才上 matched_keys。跳过第一级直接 matched_keys 会把隔离问题伪装成对齐问题，越调越乱。
5. **`.copy()` 是推导模式的暗手**：L130 的 `TransformMatchingTex(s1.copy(), s2)` 中 copy 不可省——该动画消耗源对象，不 copy 推导史就凭空消失。
6. **t2c 与 set_color_by_tex 是两个入口**：L200 的 `t2c={"A": BLUE}` 是构造期参数（颜色参与图元结构），L189 的是事后方法——变换动画里构造期着色更稳（颜色跟着碎片走），事后着色 Transform 后可能错位。
7. **公式不受等宽字体铁律约束**：MathTex 走 LaTeX 而非 Pango 渲染（visual-design.md L73），别给公式套 MONO；片段默认 `from manim import *` 才有 RED/Write 可用。

---
*下一篇：test_render_captions.md（字幕逻辑的动态加载单测）。*
