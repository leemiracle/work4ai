# skills/manim-video/SKILL.md 精讲 — Manim 动画子技能的完整提示词契约

## 一、角色定位：被 vendor 的独立子技能，不是 helpers 的编排者

先钉一个容易搞错的事实：本仓有两个 SKILL.md。仓库根的 `SKILL.md`（frontmatter `name: video-use`）才是主技能——对话式视频剪辑的总指挥，也是 `helpers/` 六个 Python 脚本的唯一编排者（根 SKILL.md:70-79 逐一列出 helper 用法）。而 `skills/manim-video/SKILL.md`（frontmatter `name: manim-video`，version 1.0.0，见 1-5 行）是被主技能"vendor"（内嵌分发）的**独立子技能**，专职动画四引擎之一。grep 全文可证：manim-video/SKILL.md 里 `helpers/` 零引用——它自包含，不碰剪辑流水线。

挂接点两处：根 SKILL.md:68 明言"This skill vendors `skills/manim-video/`. Read its SKILL.md when building a Manim slot."；根 SKILL.md:211 在动画引擎选型表把 Manim 定位为"formal diagrams, state machines, equation derivations, graph morphs"——正式图示、状态机、公式推导、图变形这四类才轮到它，产品 UI 动效归 HyperFrames/Remotion，简单贴片归 PIL。架构上：根 SKILL.md 决定"要不要用 Manim"，本文件决定"用 Manim 时怎么做"。

它的职责是把"写一段 Manim 代码"这件高风险的事变成可复制的工序：创意标准、模式路由、参考文档索引、实现红线，全部预先写死在提示词里，让执行 slot 的子代理无需即兴发挥审美判断。

## 二、内部结构：创意标准 → 模式表 → 管线 → 红线 → 参考索引

文件 265 行，是典型的"宪法+路由表+索引"三层结构。

**创意标准（Creative Standard，9-23 行）**是价值主张层，六条原则每条都是可执行判断：13 行要求写代码前先讲清叙事弧（纠正什么误解、"aha moment" 在哪）；15 行"Geometry before algebra"——先看形状后见公式；17 行"First-render excellence is non-negotiable"——首渲染即出品；19 行透明度分层是全篇最具体的美学规则：主体 1.0、上下文 0.4、结构元素（坐标轴/网格）0.15；21 行强制每个动画后 `self.wait()`；23 行全片共享色板与字号体系。19 行的三档透明度在 references/visual-design.md 里展开成完整布局理论。

**模式表（Modes，29-39 行）**是路由层：七种模式（概念讲解、公式推导、算法可视化、数据故事、架构图、论文讲解、3D 可视化）各自映射到一篇 reference。37 行 Architecture diagram 指向 `references/mobjects.md`，38 行 Paper explainer 指向 scene-planning.md——路由目标按"产出物由什么构成"选。

**技术栈与管线（41-63 行）**：Stack 表锁定四个依赖——Manim CE（引擎）、LaTeX（MathTex 公式渲染）、ffmpeg（拼接/混音）、ElevenLabs 或 Qwen3-TTS（可选旁白）。52-56 行管线六步 `PLAN --> CODE --> RENDER --> STITCH --> AUDIO --> REVIEW`，58 行规定先写 plan.md 再写 script.py——把"想清楚再写码"流程化。

**可复制的规格表（79-129 行）**是这份提示词最"工程"的部分：四套命名色板（83 行 Classic 3B1B：背景 `#1C1C1C`、主 `#58C4DD`、副 `#83C167`、强调 `#FFFF00`）；89-97 行动画速度表给出 run_time 与后续 wait 的配对值（标题 1.5s+1.0s，关键公式 2.0s+2.0s，"aha moment" 2.5s+3.0s）；99-107 行字号五级（Title 48 / Heading 36 / Body 30 / Label 24 / Caption 20）。这些数字的价值在于**把审美决策变成查表**——子代理照抄即达及格线以上的成品质量。

**字体红线（109-121 行）**：111 行断言 Manim 的 Pango 渲染器对比例字体产生破碎字距，故全部文本必须等宽字体，114 行给出 `MONO = "Menlo"` 定义一次文件顶部共享的模式，121 行规定最小 `font_size=18`。

**工作流代码骨架（141-158 行）**给出 Scene1_Introduction 完整可跑样例，160-164 行提炼四个关键模式：每个动画挂 `add_subcaption` 字幕（161 行）、文件顶部共享色常量（163 行）、每场景设 `self.camera.background_color`（164 行）、结尾 `FadeOut(Group(*self.mobjects))` 清场退出。

**实现红线（189-212 行）**四条全是 Manim 高频坑：LaTeX 必须原始字符串 `r"\frac{1}{2}"`（192-196 行）；贴边文字 `buff >= 0.5`（198-201 行）；替换文字用 `ReplacementTransform` 而非叠写（203-206 行）；绝不动画未 add 的 mobject（208-212 行）。

**性能预算（214-222 行）**：-ql 草稿 854x480@15 每场景 5-15 秒，-qh 出品 1920x1080@60 每场景 30-120 秒，222 行"Always iterate at -ql. Only render -qh for final"——先低成本迭代再付高清渲染税。

**参考索引（224-242 行）**列全 14 篇 references/；**创意分歧附录（245-264 行）**只在用户明确要"实验性/创意"输出时启用 SCAMPER 或假设反转，默认关闭。

## 三、外部连接：一个 vendor 指令 + 14 篇参考 + scripts/setup.sh

上游只有根 SKILL.md 的两处引用（68 行 vendor 声明、211 行引擎选型行）。根 SKILL.md:257-268 的并行子代理简报模板（"each animation is one sub-agent spawned via the Agent tool"）是它的实际调用语境：本文件整份会被塞进那个自包含 prompt。

下游分三支：一是 `references/` 14 篇（228-241 行表格逐一登记），animations.md 与 mobjects.md 是 API 主参考，visual-design.md 与 production-quality.md 是质量守门，troubleshooting.md 排障；二是 `scripts/setup.sh`（27 行 Prerequisites 指到它，验证 Python 3.10+、Manim CE v0.20+、LaTeX、ffmpeg，文档实测锚定 v0.20.1）；三是 Manim 库本身——文件里所有 API（Scene、MathTex、add_subcaption）以 v0.20 为准。

产物去向由根 SKILL.md 决定：Manim 渲染出的 mp4 作为 overlay 进 EDL 的 `overlays` 数组（根 SKILL.md:299-301），最终被 `helpers/render.py` 的 PTS-shift 合成吃掉。本文件管"从需求到一个 mp4"，mp4 之后的命运归主技能。

## 四、数据流：用户意图 → plan.md → script.py → media/ → slot mp4

输入是自然语言需求（模式表 31-39 行左侧），输出是完整项目目录（65-75 行）：`project-name/` 下 plan.md（叙事弧+场景清单）、script.py（一文件全场景，一类一场景各自可独立渲染，60 行）、concat.txt、final.mp4、`media/videos/script/480p15/`（Manim 自动生成，74 行）。

在 video-use 语境下，"project-name" 实际就是 `edit/animations/slot_<id>/`（根 SKILL.md:50），场景片段经 176-181 行 concat 流程产出 slot 的 render.mp4，再由 EDL 登记为 overlay。数据流单向无回路；REVIEW 步骤（186-187 行 `manim -ql --format=png -s` 出预览静帧）是唯一的校验点。

## 五、设计决策与取舍

**提示词即规格书**。89-107 行的速查表把"节奏感""层级感"翻译成具体秒数和字号，牺牲灵活性换取子代理产出的下限——这正是 first-render excellence（17 行）能成立的机制：审美预先固化，运行时不再现场决策。

**单文件单脚本（43 行"Single Python script per project. No browser, no Node.js"）**是关键排他性选择：与 HyperFrames/Remotion（Node.js 生态）拉开距离，Manim slot 保持纯 Python 可渲染，降低 slot 目录依赖足迹；代价是交互式 UI 动效做不了——根 SKILL.md:209-210 把那些场景分给 web 系引擎。

**版本锚定（27 行"tested against Manim CE v0.20.1"）**：Manim CE API 迭代快，文档全部校准到具体小版本，避免参考页与实际库行为漂移。

**附录式创意工具（245-264 行）**：SCAMPER 与假设反转默认休眠、仅明确请求时启用，防止"每次都发散"——与根 SKILL.md:14"艺术自由是默认"互补：主线给自由，工具箱给收敛。

## 六、新人提示：坑与勘误

1. **最大勘误：别把它当主技能**。helpers/ 的编排者是根 SKILL.md；本文件只管 Manim slot。在 manim slot 里找转录/剪辑能力，方向就错了。
2. **setup.sh 路径坑**：`skills/manim-video/README.md` 末行写着 `bash skills/creative/manim-video/scripts/setup.sh`——`skills/creative/` 是历史目录残留，实际路径是 `skills/manim-video/scripts/setup.sh`（仓内已核实该文件存在）。照 README 抄命令会找不到文件。
3. **字幕双轨制**：本文件的 `add_subcaption`（154 行）让 Manim 自动生成 .srt（animations.md:132）；但成品进 video-use 剪辑管线后，最终字幕以 render.py 从 Scribe 转录生成的 master.srt 为准（Hard Rule 5），Manim 自带字幕与剪辑后时间轴可能对不上。
4. **-qh 渲染税**：222 行的告诫要当真——60fps 1080p 渲染一个中等场景可能两分钟起，迭代期一律 -ql。
5. **subcaption 是无障碍硬要求**（161 行"Subtitles on every animation"），不是可选项；漏了它 references/production-quality.md 的 post-render 清单会拦。
6. **版本敏感**：文档锚定 v0.20.1，若环境装了更新版 Manim，遇到 API 不符先查 references/troubleshooting.md 再怀疑自己。
