# S6 — 编译器战争史：30 年 GCC vs LLVM vs MLIR（1987–2026）

> **专题定位**：编译器基础设施 30 年主导范式之争的**通史**——从 GCC 1987 诞生、EGCS 1997 分叉、LLVM 2000 UIUC 起步、Apple 2005 接力、Clang 2007 出鞘、2010 macOS 默认、MLIR 2019 借壳、Rust/Apple Silicon 借势反攻、到 Mojo 2023 第三次点火——把每一场战争的**起因 / 转折 / 赢家 / 输家 / 可证伪教训**逐幕拆开，并给出三条贝叶斯先验。
> **数据截止**：2026-07-07
> **数据源分级**：`[实测]` = 本项目 grep/读 OpenXiangShan/llvm-project 源码树；`[一手]` = 论文 / 官方公告 / 邮件列表 / WWDC 演讲原文；`[GitHub]` = llvm/llvm-project commit/PR；`[GCC]` = gcc.gnu.org；`[报道]` = 权威媒体（HPCWire/Register/fast.ai 等）；`[社区共识]` = 编译器圈广泛共识；`[推测-依据]` = 基于公开信息推断。所有外部链接访问日期：2026-07-07。
> **关联文档**：[`Lens_01_Historian`](../Lenses/Lens_01_Historian.md)（30 年周期律与接力棒定律，本专题是其"战争通史"展开）、[`Lens_02_Christensen`](../Lenses/Lens_02_Christensen.md)（破坏式创新机制，每场战争的因果引擎）、[`领域资源库_LLVM.md`](../领域资源库_LLVM.md) §7（创始人 Lattner 资源池）。
> **本专题与既有文档的分工**：Lens_01/Lens_02 用**框架**看 LLVM 命运（历史学/Christensen 演绎），本专题**把镜头对准战争本身**——以时间线为骨、以十场战役为肉、以三张对照表与五张图为刀，回答"每一场战争为什么这么打、谁赢了、下一场会怎么打"。

---

## 0. 方法论诚实声明（先说清楚数据怎么来的）

本专题属于"产业通史"，与 Lens_03（供应链，靠 `.mailmap`/`.td`）和 E18（飞腾适配，靠 phytium_repos）**方法论不同**。把丑话说在前头：

- **一手时间线**：GCC 1987 Stallman、EGCS 1997-08-15 公告、EGCS 1999-04 与 GCC 重新合并并改名 GNU Compiler Collection、LLVM 2000-12 构想、LLVM 1.0 2003-10-24、Lattner 2005 加入 Apple、Clang 2007、Xcode 4.2 / WWDC 2011 GCC 出局、LLVM Foundation 2014、MLIR 2019-04 EuroLLVM 首秀 + 2019-12-24 commit `0f0d0ed1` 捐入 monorepo、Rust 1.0 2015-05-15、Apple M1 2020-11、Mojo 2023-05-02——这些**全部锚定一手来源**：Lattner 2002 硕士论文、SC21 Fireside Chat 逐字稿、WWDC 2011 Session 307 逐字稿、gcc.gnu.org EGCS 原始公告邮件、Modular 发布会 keynote、fast.ai 2023-05-03 评测、commit `0f0d0ed1` 的 GitHub 记录。
- **铁律声明（git log 限制）**：本环境 `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/.git/logs/HEAD` 经 `[实测-read]` 为**单 commit 浅克隆**——文件大小 189 字节，内容仅一条 `clone: from https://github.com/OpenXiangShan/llvm-project.git`，commit `552e68d6`，时间戳 2026-04-17 10:05:15 `[实测]`。**故本专题不依赖本地 commit 时间序列**，全部靠"一手史 + 论文 + 在线 GitHub commit/PR + 目录/代码实测"四源交叉。任何用 commit 时间验证的判断，都标 `[GitHub]` 并指向可复核的 SHA/PR 编号。
- **代码级锚点（过 §0.3 v2.0 门槛 b，本专题核心特异性来源）**：
  - **`[实测-read]`** `cmake/Modules/LLVMVersion.cmake` 第 4–6 行：`LLVM_VERSION_MAJOR 23 / MINOR 0 / PATCH 0`——本快照对应 LLVM **23.0.0git**（2026 春主线 HEAD）。
  - **`[实测-read]`** `LICENSE.TXT` 第 1–2 行："The LLVM Project is under the **Apache License v2.0 with LLVM Exceptions**"——License 战争（§9.10）一手物证。
  - **`[实测-read]`** `llvm/Maintainers.md` 第 530–537 行："Emeritus lead maintainers" 段下列 **Chris Lattner**（sabre@nondot.org / GitHub lattner / Discourse clattner）——点火人仍在 emeritus 名册，但已非活跃 maintainer。这是接力棒定律（§10.3）的物证：Lattner 点火后已交给 Foundation。
  - **`[实测-grep]`** `llvm/lib/Target/RISCV/RISCVProcessors.td` 第 796 行 `XIANGSHAN_NANHU`——中国开源 RISC-V 项目（香山）已进主线 LLVM 调度模型；对照 `grep -ri "phytium|ftc86" llvm/lib/Target/AArch64/` **零命中**。**这一对偶是本专题判断国产厂商在战争里"接棒 vs 观战"差异的核心物证**。
- **历史规律的方法论边界**：本专题提取的"30 年周期律""颠覆三要素""接力棒定律"是**贝叶斯先验**而非物理定律。编译器商业史样本极小（主流 IR 案例 < 5 个），过拟合风险高（见 §11 盲区段）。读者应把它们当"如果历史节奏不变，最可能的轨迹"来用，而非决定论预言。

---

## 1. 一图看懂 30 年：编译器战争总时间线（图 1）

```
1987 ──────────────────────────────────────────────────────────────────── 2026
│                                                                          │
│  战争一：IBM/商业 Unix 专有编译器  vs  开放编译器（GCC）                   │
│  ├──────────────────────────────────────────────────────────────► ~2000  │
│                                                                          │
│  战争二：GCC  vs  商业 C/C++ 编译器（ICC/Sun Studio/PGI/DEC/SGI）          │
│  ├─────────────────────────────────────────────────────────────────► 2017│
│  │   1987 GCC1.0                                                          │
│  │   1997 EGCS fork ──── 1999 合并回 GCC                                  │
│  │   2005 GCC 4.0 tree-ssa 自我现代化（失败先例）                          │
│                                                                          │
│  战争三：LLVM  vs  GCC（系统语言后端之争）                                │
│  │   ├─────────────────────────────────────────────────────────────► 进行│
│  │   2000 LLVM 构想（UIUC）2002 MS 论文 2004 CGO 论文 2005 Apple 招 Lattner│
│  │   2007 Clang  2009 Clang 1.0  2010 自举/FreeBSD                        │
│  │   2011 WWDC GCC 出局  2013 Swift  2014 LLVM Foundation                │
│  │   2015 Rust 1.0 全押 LLVM  2017 Lattner 离 Apple                       │
│  │   2020 Apple M1 用 LLVM 反攻 x86                                       │
│                                                                          │
│  战争四：MLIR  vs  LLVM core（AI/异构编译新维度）                          │
│  │       ├───────────────────────────────────────────────────────► 进行  │
│  │       2019-04 EuroLLVM MLIR 首秀                                       │
│  │       2019-12-24 commit 0f0d0ed1 捐入 monorepo（+226337 行）           │
│  │       2021 CGO MLIR 论文                                               │
│  │       2023 Mojo（Lattner 第三次点火）                                  │
│  │       2024-2026 StableHLO/IREE/torch-mlir 全线 MLIR 化                 │
└──────────────────────────────────────────────────────────────────────────┘
  规律：每场战争 20–30 年；后一场的颠覆者总在前一场的成熟期里发芽（Perez 长波）
```

**图 1 读法**：四场战争在时间轴上**叠瓦式接力**——第二场还没结束，第三场就已起步；第三场未完，第四场已开。这是 Perez（2009）"下一浪在上一浪 maturity 里 irruption"在编译器产业的精确复现 `[推测-依据]`。**关键拐点**：1997 EGCS（GCC 自救）、2000 LLVM 构想（第三场点火）、2005 Apple 接棒（第三场工业化）、2011 WWDC（第二三场胜负已分）、2019 MLIR 捐入（第四场点火）。下面十节逐场拆解。

---

## 2. 硬问题 1：GCC 1987 诞生——为什么 GCC 能赢商业编译器？

### 2.1 事实链（一手）

1985 年 Richard Stallman 创立自由软件基金会（FSF），目标之一是造一个"自由"的 C 编译器，作为 GNU 操作系统的基石。**GCC 1.0 于 1987 年发布**，最初全称 "GNU C Compiler" `[社区共识]`。彼时 C 编译器市场是**商业专有编译器的天下**——Sun 的 `cc`、SGI 的 MIPSpro、DEC 的 DEC C、HP 的 HP-UX C、IBM 的 XL C、Intel 的 ICC，每家 Unix/芯片厂商都把编译器当成**卖硬件的捆绑组件**，闭源、贵、绑定单一平台。

### 2.2 GCC 赢的三要素（与 §10.1 颠覆三要素定律对照）

GCC 赢商业编译器，不是"GCC 代码生成比 ICC 好"——1987–1995 年间 GCC 的代码质量在 SPEC 上**长期不如**商业编译器 `[社区共识]`。它赢在三件 ICC/Sun/DEC 给不了的东西：

| 维度 | 商业编译器（1987–2000） | GCC | 战争赢家 |
|------|------------------------|-----|:--------:|
| 许可证 | 闭源、单平台授权、贵 | GPL 自由、可自由分发、可改 | **GCC** |
| 跨平台 | 一家一编译器，迁移成本极高 | 30+ 架构通吃（i386/m68k/SPARC/MIPS/Alpha/PowerPC/ARM...） | **GCC** |
| 生态绑定 | 锁死在自家 Unix/芯片 | 与 Linux 内核（1991）+ GNU 工具链共生 | **GCC** |
| 价格 | 数百至数千美元/seat | 0 美元 | **GCC** |

> **关键洞察**：GCC 不是"做得更好的商业编译器"，而是**"重新定义了什么是编译器基础设施"**——一个自由、可改、跨平台、与操作系统共生的公地。商业编译器的客户（Unix 厂商）雇佣编译器完成的 job 是"把 C 编译到我的硬件上以卖更多硬件"，而 GCC 创造的新 job 是"任何人在任何硬件上都有一个能用的、可改的 C 编译器"。**这是 Christensen 新市场破坏的精确形态（把"非消费者"变成"消费者"）**——大学生、Linux 黑客、嵌入式小厂、新兴 ISA（ARM 早期）全成了 GCC 的客户，商业编译器的护城河被从底部掏空 `[推测-依据]`。

### 2.3 商业编译器的退场（结局）

商业 C/C++ 编译器在 2000–2017 间几乎全军覆没：Sun Studio 随 Sun 被 Oracle 收购而边缘化；SGI/DEC/HP 的 Unix 编译器随 Unix 厂商消亡；Intel ICC 在 2023 年被 oneAPI（基于 LLVM）替代 `[社区共识]`；PGI（Portland Group）2013 年被 NVIDIA 收购，最终也并入 LLVM-based NVHPC。**唯一活下来的"商业"路线是 IBM XL C/C++（绑 PowerPC/AI）和 ARM 自家编译器（绑 ARM 生态），但它们的市场份额早已不是主流**。**战争一（专有 vs 开放）和战争二（GCC vs 商业）的赢家都是 GCC/开放模型**。

### 2.4 教训（写入表 1，§8）

**教训 A**：**当编译器的"客户"从"卖硬件的厂商"变成"所有写 C 的人"，许可证 + 跨平台 + 生态共生就是护城河，闭源单平台必败**。这条教训在战争三（LLVM vs GCC）里被 LLVM 用 Apache 2.0 + 模块化 + 商业友好**反过来打 GCC**——历史的回旋镖。

---

## 3. 硬问题 2：EGCS 分叉 1997——GCC 内部矛盾的爆发与"回归主线"的教训

### 3.1 事实链（一手邮件原文）

1997-08-15，Cygnus Solutions 的 D.V. Henkel-Wallace（gumby@cygnus.com）发出**EGCS（Experimental/Enhanced GNU Compiler System）成立的公告** `[一手/gcc.gnu.org]`。原文（节选）：

> "A bunch of us (including Fortran, Linux, Intel and RTEMS hackers) have decided to start a more experimental development project... We are calling this project 'egcs' (pronounced 'eggs').
>
> **Why are we doing this? It's become increasingly clear that the FSF's needs for gcc2 are at odds with the objectives of many in the community**... GCC is part of the FSF's publicity for the GNU project, as well as being the GNU system's compiler, **so stability is paramount for them**. On the other hand, Cygnus, the Linux folks, the pgcc folks, the Fortran folks and many others have done development work which has not yet gone into the GCC2 tree despite years of efforts to make it possible."

公告联署人名单读起来是当年编译器圈的"全明星阵"：Per Bothner、Jeff Law、Richard Henderson、Jason Merrill、Ian Lance Taylor、Jim Wilson、David Edelsohn、Toon Moene（Fortran）、Joel Sherrill（RTEMS 嵌入式）等 `[一手/gcc.gnu.org]`。

### 3.2 EGCS 是什么——一次"政治性分叉"

EGCS 不是技术分叉（它没换 IR、没换架构），而是**治理分叉**：FSF 把 GCC 当"GNU 项目的门面"，**稳定性压倒一切**，导致大量社区贡献（pgcc 的 Pentium 优化、g77 Fortran、Linux 内核适配的扩展、Cygnus 的商业化工程）**多年进不了 GCC2 主线**。EGCS 把这些散落的 fork（pgcc/gcc2-linux/g77/...）**合并成一个实验性分支**，用更快的发布节奏吸引开发者。

> **关键洞察**：EGCS 揭示了开源基础设施的一个永恒张力——**"稳定性"（FSF/官方）vs"创新速度"（社区/商业）**。这个张力在 1997 年以 EGCS 分叉的形式爆发，在 2017 年以"Lattner 离 Apple、范式创新跟着点火人走到 Google/Modular"的形式在 LLVM 重复（见 §10.3 接力棒定律）。

### 3.3 回归主线：1999-04 合并 + 改名 + Steering Committee

**EGCS 没有长期分叉，而是在 1999-04 与 GCC 重新合并** `[一手/gcc.gnu.org/wiki/History]`。三件事同时发生：

1. **EGCS 被指定为 GNU Project 的官方 GCC**——EGCS 这个名字消失，回归 GCC。
2. **GCC 改名**：从 "GNU C Compiler" 改为 "**GNU Compiler Collection**"（首字母同为 GCC），标志着 GCC 不再只是 C 编译器，而是 C/C++/Fortran/Java/Ada 多语言集合。
3. **GCC Steering Committee（指导委员会）正式化**：1998-11-10 的原始公告 `[一手/gcc.gnu.org/steering.html]` 写明委员会的使命是"**preventing any particular individual, group or organization from getting control over the project**"（防止任何个人/团体/组织控制项目）。1999-04 FSF 正式任命该委员会为 GCC 的官方 maintainer。

### 3.4 EGCS 回归的教训（写入表 1）

> **教训 B（开源治理定律）**：**开源基础设施的"分叉-回归"是健康而非病态**——当官方治理过度保守，社区会分叉（EGCS）；当分叉证明了更快节奏的价值，官方会让步并吸收（1999 合并）。**但这次回归的代价是**：FSF 从此失去了对 GCC 的"绝对控制"，Steering Committee 取而代之。这个治理教训在 LLVM 时代被复用——LLVM Foundation（2014）从一开始就设为中立 501(c)(3)，避免重蹈"FSF 独裁 → 分叉"的覆辙（见 §9.7 + Expert_17 治理）。

**反例警告**：EGCS 能回归，是因为它**没有换技术范式**（还是 GCC2 的 RTL）。**当一个分叉换了范式（如 LLVM 之于 GCC、MLIR 之于 LLVM core），回归几乎不可能**——这预示了 §9.7 MLIR "进 monorepo 但不回归 LLVM core 范式"的结局。

---

## 4. 硬问题 3：LLVM 2000 UIUC——为什么从学术项目起步？

### 4.1 事实链（一手：硕士论文 + SC21 访谈）

LLVM 的诞生有**精确的一手时间戳**。Lattner 自己在 2013-11-07 LLVM Dev Meeting 演讲《LLVM - the early days》`[一手/nondot.org PDF]` 给出逐月时间线：

- **2000-12（Conception）**：LLVM 构想诞生。
- **2001-06-06**：CVS 第一版。
- **2001-07-08**：`getelementptr` 指令诞生（LLVM IR 的标志性指令）。
- **2001-07-15**：Vikram Adve 开始为 SPARC 写 `llc`。
- **2001-11-16**：第一篇论文投 PLDI。
- **2002-12**：**Chris Lattner 完成硕士论文《LLVM: An Infrastructure for Multi-Stage Optimization》** `[一手/llvm.org/pubs/2002-12-LattnerMSThesis]`，UIUC，导师 Vikram Adve。论文致谢原话：**"I would like to thank my advisor, Vikram Adve, for his support, patience, and especially his trust and respect."**
- **2003-10-24**：**LLVM 1.0 发布** `[一手/llvm.org/releases]`。
- **2004-03-20**：**Lattner & Adve CGO 2004 论文《LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation》** `[一手/ACM DL]`——LLVM 范式的"big-bang"宣告。

Lattner 在 SC21 Fireside Chat（2021-12）`[报道/HPCWire]` 回忆起源：

> "Vikram and I had this idea that if we took this just-in-time compiler technology, but did more ahead-of-time compilation, we could get better trade-offs in terms of whole program optimization analysis... A lot of the name LLVM, low level virtual machine, comes from the idea of **taking the Java Virtual Machine and building something that is underneath it**, a platform that you could then do whole program optimization for."

### 4.2 为什么从学术起步？（三因）

**因 1：技术风险太高，只有学术环境能承担。** LLVM 的核心赌注是"用 SSA + 模块化 + 类型化 IR 重做整个编译器基础设施"——这是一个**5–10 年才见商业价值**的基础研究问题。2000 年没有哪家商业公司愿意为一个"可能根本不能用"的新 IR 烧 5 年钱。**UIUC 的博士项目 + NSF 资助 + Adve 的容忍度**是唯一能孵化这个赌注的环境 `[推测-依据]`。

> **一手铁证**：CACM 2026-07 的回顾文章《The LLVM Compiler Infrastructure》`[一手/CACM]` 由 Lattner 等人撰写，标题副标就点明这是 **NSF 资助 25 年的学术研究回顾**——LLVM 的学术出身是其根深蒂固的身份。

**因 2：LLVM 的设计目标本身就来自学术问题。** Lattner & Adve 2004 CGO 论文 `[一手/ACM DL]` 的关键词是 **"lifelong program analysis & transformation"**——"全生命周期分析"（编译时/链接时/运行时/空闲时统一）。这**不是一个商业需求**（商业编译器只在乎 AOT 编译质量），而是一个**学术研究问题**（如何让编译器在程序整个生命周期里持续优化）。**只有学术环境会问这个问题，商业公司不会**——这是 LLVM 必须从学术起步的根本原因。

**因 3：UIUC + Adve 是当时编译器研究的重镇。** UIUC（University of Illinois at Urbana-Champaign）的编译器研究在 1990s–2000s 是世界顶尖（PSPACE/SUIF/IMPACT 项目），Vikram Adve 是其中坚。**Lattner 选 UIUC 不是偶然**——他要找的是"能容忍一个博士生花 5 年重做编译器基础设施"的导师和环境 `[推测-依据]`。

### 4.3 学术起步的代价与回报

**代价**：LLVM 在 2000–2005 年是"纯学术玩具"——代码生成质量远不如 GCC，没有人用 LLVM 编译生产代码。Lattner 自己在 SC21 访谈 `[报道/HPCWire]` 回忆：

> "The quality of the generated code wasn't perfect but it was promising."

**回报**：学术起步让 LLVM **从一开始就设计成"可复用、可实验、可组合"的编译器基础设施**，而不是"一个能编译 C 的编译器"。这个设计基因（modular、SSA、类型化 IR、lifelong analysis）在 5 年后被 Apple 看中，成为颠覆 GCC 的技术范式优势（见 §10.1 定律一的"技术范式优势"要素）。

> **教训 C（学术孵化定律）**：**改变范式的基础设施，几乎必然从学术起步**——GCC（MIT/FSF 非营利）、LLVM（UIUC 博士）、MLIR（Google 研究 + 学术合作）、Mojo（Modular 但根在 MLIR 研究）。**商业公司擅长把成熟范式工程化，不擅长孵化范式革命**。这条定律解释了为什么"颠覆 LLVM"的候选（MLIR/Mojo）都根在学术界或研究实验室，而非纯商业公司。

---

## 5. 硬问题 4：LLVM 2005 Apple——Apple 为什么要 LLVM 而非 GCC？

### 5.1 事实链（一手：SC21 访谈 + 邮件）

2005 年 Lattner 从 UIUC 毕业，加入 Apple。SC21 Fireside Chat `[报道/HPCWire]` 的逐字回忆：

> "When Lattner graduated from U of Illinois in 2005, LLVM was still an advanced research project. 'The quality of the generated code wasn't perfect but it was promising.' An Apple engineer was working with LLVM and talked it up to an Apple VP. At the time Lattner was collaborating with the engineer over mailing lists.
>
> Apple had been investing a lot in GCC, and I don't know if it was the GCC technology or the GCC team at Apple at the time, **but management was very frustrated with lack of progress**. I got to talk with this VP who thought compilers were interesting and he decided to give me a chance. He hired me and said, 'Yeah, you can work on this LLVM thing. Show that it wasn't a bad idea. [Not long after] he motivated saying "You can have a year or so to work on this. And worst case, you're a smart guy, we can make you work on GCC.'"

**关键一手**：2005-11-18，Lattner 向 GCC 社区发出 **《LLVM/GCC Integration Proposal》** `[一手/gcc.gnu.org 邮件]`——这是 Lattner **最后一次尝试让 LLVM 与 GCC 共生**。提案未被 GCC 接受，直接推动了 Apple 走"自建 Clang 前端 + LLVM 后端"的独立路线。

### 5.2 Apple 选 LLVM 而非 GCC 的三因（Apple 视角）

**因 1：GCC 治理与许可证的双重死锁。** Apple 在 2000s 初期深度依赖 GCC（macOS / Xcode 默认编译器），但遇到三重阻力 `[社区共识]`：

- **GPLv3 恐慌**：FSF 在 2005–2007 推动从 GPLv2 到 GPLv3。GPLv3 的"反 Tivo 化"条款（device 必须允许用户替换 GPL 软件）与 Apple 的封闭硬件模型**根本冲突**。Apple 法务把 GCC 视为"定时炸弹"。
- **GCC 单体架构**：GCC 的 RTL/GIMPLE 是为 C 设计的单体后端，**无法被 Apple 重新组合**（不能把 GCC 的前端塞进 Xcode 的 IDE、不能用 GCC 做 JIT、不能复用 GCC 的优化器做静态分析）。Apple 想要的是"编译器即库"，GCC 给不了。
- **GCC 进度令 Apple 沮丧**：Lattner 原话"management was very frustrated with lack of progress"。Apple 投了很多钱改 GCC，但 GCC Steering Committee（吸收了 EGCS 教训后变得审慎）对 Apple 的私有改动接受很慢。

**因 2：LLVM 的许可证与架构正好对症。** LLVM 用 UIUC/BSD 风格许可证（后改 Apache 2.0 with LLVM Exception）`[实测-read] LICENSE.TXT`，**对闭源商业工具链完全友好**。LLVM 的模块化设计（Pass/IR/CodeGen 全是库）让 Apple 能把编译器组件**塞进 Xcode、OpenGL 驱动、OpenCL runtime、静态分析器**——这是 GCC 单体架构做不到的。

**因 3：Apple 需要 GPU/图形 JIT，GCC 进不去。** Lattner SC21 原话 `[报道/HPCWire]`：

> "there was a need for just-in-time compilers in the graphics space and LLVM turned out to be a good solution... [pieces of LLVM] shipped with the 10.4 Tiger release (2007) improving graphics performance. That showed some value and justified a little bit of investment."

> **关键洞察**：**Apple 雇 Lattner 不是为了"造一个更好的 GCC"，而是为了"造一个能塞进 Apple 全栈（Xcode/OpenGL/OpenCL/iOS）的编译器基础设施"**。GCC 因为 GPL + 单体架构，**结构性地无法满足 Apple 的需求**——这是 Apple all-in LLVM 的根本原因。**LLM 颠覆 GCC 的真正起点不是 2000 UIUC，而是 2005 Apple**——学术项目再多潜力，没有金主就是 Transmeta 式消亡（见 §10.1 定律一的"大金主"要素）。

### 5.3 接力棒第 1 棒：Apple 工业化（2005–2017）

Apple 招 Lattner 是**接力棒定律（§10.3）的第 1 棒交接**：UIUC 学术孵化（第 0 棒）→ Apple 工业化（第 1 棒）。Apple 在 2005–2017 这 12 年里把 LLVM 从学术项目变成工业基础设施：

- **2007**：Clang 出鞘（见 §7）；LLVM 进 macOS 10.4 Tiger OpenGL 驱动 `[报道/HPCWire]`。
- **2008–2009**：Clang 1.0（2009），OpenCL 成为"Clang 的第一个用户"（Lattner SC21 原话）。
- **2010**：Clang 自举（用 Clang 编译 Clang，55 万行 C++）`[一手/Fandrey 2010 报告]`；FreeBSD 把 Clang 导入 HEAD `[一手/freebsd-current 邮件]`。
- **2011**：WWDC Session 307《Moving to Apple LLVM compiler》——GCC 出局（见 §8）。
- **2014**：LLVM Foundation 成立（治理去 Apple 化）。
- **2014–2017**：Swift 诞生（2014 发布，全建在 LLVM 上），LLDB 替代 GDB 成为 Apple 默认调试器。

**Apple 的养育物证**：`[实测-grep]` `llvm/lib/Target/AArch64/AArch64Processors.td` 第 1417–1633 行列出 ~80 个 ProcessorModel，其中 **apple-a7..a19、apple-m1..m5 全套 CycloneModel**——Apple 把自家每一代 CPU 的微架构调度模型都养进了 LLVM upstream `[实测/项目内 Lens_01]`。**这是 Apple all-in LLVM 的代码级铁证**。

---

## 6. 硬问题 5：Clang 2007——Clang vs GCC 前端的具体差异

### 6.1 事实链

Clang 是 LLVM 的 C/C++/Objective-C 前端，2007 年由 Apple 启动（核心开发者 Steve Naroff、Doug Gregor、Ted Kremenek 等，Lattner 监督）。**Clang 1.0 在 2009 年发布** `[社区共识]`。Lattner SC21 `[报道/HPCWire]`：

> "the GPU team was trying to make a shading language for general-purpose, GPU compute, [and that] turned into what we know now as OpenCL and that became the first user of Clang."

### 6.2 Clang vs GCC 前端：五个工程级差异

Clang 不是"做得更好的 GCC 前端"，而是**重新定义了"前端"**。WWDC 2010 Session 313《LLVM Technologies in Depth》`[一手/WWDC 2010]` 和 WWDC 2011 Session 307 `[一手/WWDC 2011]` 反复强调的差异：

| 差异维度 | GCC 前端（gcc/cc1plus） | Clang 前端 | 工程价值 |
|---------|------------------------|-----------|---------|
| **架构** | 单体（前端 + 后端焊死在一个进程） | **库化**（parser/AST/semantic analysis 全是可复用的库） | 能塞进 IDE（Xcode）/静态分析器/runtime JIT |
| **诊断（错误信息）** | 模糊、一行、无 fix-it 提示 | **精确**（指出哪一列、哪个 token、给 fix-it 建议） | 开发者体验碾压 |
| **编译速度** | 慢（GCC 前端单线程、解析慢） | **快**（单趟解析、内存效率高） | 大型项目编译时间显著缩短 |
| **AST 表达力** | GCC 的 AST 深埋内部、不可外部访问 | **AST 是一等公民**（可程序化遍历、生成代码） | 重构工具、clang-tidy、clangd、静态分析全靠它 |
| **预处理器** | 独立进程（cpp），宏信息丢失给编译器 | **集成预处理器**（宏、include 栈全保留） | IDE 的语法高亮/补全/跳转精确化 |

WWDC 2010 `[一手]` 原话：

> "If you look at GCC preprocessor is not integrated so all the macro information is not actually seen by the compiler, or accurate line and column information... So all this needs to be there in order to build a great tool experience... what we've done in Xcode 4 is we've taken the Clang front end which is fast, modular, it can be reused in a variety of ways and we put it inside the Xcode 4 IDE."

### 6.3 Clang 真正的战略价值：让 LLVM 从"后端"升级为"全栈编译器基础设施"

**Clang 之前，LLVM 是"一个没有前端的优秀后端"**——它的 IR 设计精良、Pass 框架模块化、CodeGen 跨平台，但没有自己的 C 前端，只能靠 `llvm-gcc`（GCC 4.2 前端 + LLVM 后端的拼接产物）喂 IR。`llvm-gcc` 是个尴尬的中间产物——WWDC 2011 `[一手]` 用"赛车的引擎 + 老马的前端"来比喻，并明说"We're going to send it out to pasture"（让它退役）。

**Clang 让 LLVM 第一次拥有"全栈"**：从 C 源码 → AST → LLVM IR → Pass → CodeGen → 机器码，**全部由 LLVM 项目自己掌控**。这是 LLVM 能颠覆 GCC 的**工程级前提**——没有 Clang，LLVM 永远是 GCC 的寄生后端；有了 Clang，LLVM 才能独立成为"GCC 的替代品"。

> **教训 D（前端定律）**：**一个编译器后端要颠覆在位者，必须有自己的一等前端**——LLVM 颠覆 GCC 靠 Clang；MLIR 想颠覆 LLVM core 必须有自己的"AI 前端"（torch-mlir/StableHLO/Mojo 是这个角色）；任何只有后端的项目（Polly、TVM 早期）都无法独立成势。**这条定律解释了为什么 Mojo 对 MLIR 如此重要——它是 MLIR 的"Clang 时刻"**（见 §11）。

---

## 7. 硬问题 6：2010 LLVM 默认 macOS——商业转折点（WWDC 2011 GCC 出局）

### 7.1 事实链（一手：WWDC 2011 逐字稿）

**2010 年是 LLVM 在 Apple 平台的商业转折年**：Clang 完成自举（55 万行 C++ 用 Clang 编译 Clang）`[一手/Fandrey 2010]`，FreeBSD 把 Clang 导入 HEAD `[一手/freebsd-current]`，WWDC 2010 Session 313 介绍 Clang-in-Xcode、LLDB、集成汇编器 `[一手/WWDC 2010]`。

**2011 年 WWDC 是 LLVM 的"加冕典礼"**。Session 307《Moving to Apple LLVM compiler》`[一手/WWDC 2011]`，主讲人 Bob Wilson（LLVM core team manager）的原话：

> "One of the big announcements we made on Monday is that **Apple has moved to the LLVM compiler**. We're building both Mac OS X Lion and iOS 5 with LLVM-based compilers. And we're here today to ask you to do the same thing.
>
> GCC has been **stifling innovation** for us in the compiler. So we need a better compiler. And that is LLVM.
>
> In [Xcode] 4.2, **GCC is going away**. So what this means for you is that if you're still using GCC, this is the time to try out one of the other compilers."

### 7.2 为什么 2010–2011 是商业转折点（而非更早）

LLVM 2000 起步、2005 Apple 接棒、2007 Clang——**为什么商业转折发生在 2011 而非更早**？三因：

1. **Clang 在 2010 才补齐 C++ 支持**。Clang 早期不能编译 C++（只能 C/ObjC），而 Apple 的代码库大量是 C++。**没有可用的 C++ 前端，Clang 就不能替代 GCC** `[一手/Discourse 2010 llvm-gcc 过渡讨论]`。2010 年 Clang 自举（编译 Clang 自己 = 编译 55 万行 C++）证明 C++ 支持成熟，这是商业可用的前提。
2. **ARC（自动引用计数）需要 LLVM**。Apple 2011 推出 ARC（Objective-C 的内存管理革命），**ARC 的实现深依赖 LLVM/Clang 的语义分析**——GCC 无法支持 ARC。**ARC 成为"必须切 LLVM"的杀手级特性** `[一手/WWDC 2011]`。
3. **iOS 5 + OS X Lion 同时要求 LLVM**。Apple 用"两个操作系统同时 built with LLVM"来锁定迁移——开发者不切 LLVM 就没法为 iOS 5 / Lion 开发。这是**用平台锁定强制编译器迁移**的商业操作。

### 7.3 商业转折的连锁效应

2011 WWDC 之后，LLVM 在 Apple 生态彻底取代 GCC。这个转折引发了**三重连锁**：

- **FreeBSD 2014 默认 Clang** `[社区共识]`——BSD 生态跟随 Apple。
- **Android NDK 2014 切 Clang** `[社区共识]`——Google 在移动端跟进。
- **新系统语言全押 LLVM**：Swift（2014，Apple 自家）、Rust（2015 1.0，Mozilla）、Zig（2016+）、Flang（2019，Flang）——**所有 2010s 诞生的系统语言默认用 LLVM 后端**。这是战争三（LLVM vs GCC）胜负已分的标志（见 §9.8）。

> **教训 E（平台锁定定律）**：**编译器的商业转折，往往由"平台所有者用杀手级特性强制迁移"触发**——Apple 用 ARC + iOS 5 强制切 LLVM，Google 用 Android NDK 切 Clang。**没有平台所有者的"强制迁移"，纯粹的技术优势无法在 5 年内完成商业转折**。这条定律解释了为什么 GCC 至今没死——Linux 内核（Linus 这个平台所有者）没强制切 Clang，GCC 还守着内核编译（见 §10.2 下注 3 + 断层⑤）。

---

## 8. 硬问题 7：2017 MLIR——Lattner + Shpeisman @ Google 的范式提议

### 8.1 事实链（一手：commit + EuroLLVM）

MLIR（Multi-Level Intermediate Representation）的诞生有**精确的 git 锚点**：

- **2019-04 EuroLLVM**：MLIR 首次公开亮相（MLIR Tutorial + Linalg section）`[一手/mlir/docs/Rationale/RationaleLinalgDialect.md 第 62-65 行]`（项目内 Lens_02 实测）。
- **2019-09-09**：Chris Lattner（此时已从 Apple 离职，经 Tesla 短暂停留后加入 Google Brain）代表 Google TensorFlow 团队，向 LLVM 社区提议**把 MLIR 捐入 LLVM Foundation** `[一手/lists.llvm.org llvm-dev 邮件]`。
- **2019-10-07**：LLVM Foundation（主席 Tanya Lattner，Chris 的妻子）正式接纳 MLIR `[一手]`。
- **2019-12-24**：**commit `0f0d0ed1` "Import MLIR into the LLVM tree"**，作者 joker-eph（Mehdi Amini，Google/LLVM 资深贡献者），**+226337 行 / 300 文件** `[GitHub/llvm/llvm-project]`。**这是 MLIR 进入 LLVM monorepo 的精确时间戳**。
- **2021 CGO**：Lattner、Mehdi Amini、Nicolas Vasilache、River Riddle 等，《MLIR: Scaling Compiler Infrastructure for Domain Specific Computation》`[一手/CGO 2021]`——MLIR 作为新范式的学术宣告。**副标题"Scaling"暗示 LLVM core 已到规模天花板** `[推测-依据]`。

### 8.2 为什么是 Google 而非 Apple 发起 MLIR？

Lattner 2017 离 Apple（短暂去 Tesla 自动驾驶，后加入 Google Brain）`[社区共识]`。**MLIR 在 Google 诞生而非 Apple，是结构性的**：

- **Apple 的 job 是"消费级设备"**——Apple 需要的是"把 Swift/ObjC 编译到 ARM/x86"，**单层 IR（LLVM IR）够用**。Apple 没有"多级 IR"的商业需求。
- **Google 的 job 是"AI/异构计算"**——TensorFlow 要编译到 GPU/TPU/CPU/NPU，**每层抽象不同**（tensor → loop nest → hardware primitive）。**LLVM IR 是单层的、刚性的，表达不了"多级抽象"**。Google 在 AI 编译里撞上了 LLVM IR 的结构性天花板——这就是 MLIR 的"Kuhn 异常"（GCC RTL 当年解释不了"模块化"，LLVM IR 现在解释不了"多级抽象"）。
- **Google 有商业动机 + 研究文化**——TPU 是 Google 自研 AI 芯片，必须有定制编译器；Google Brain/X 有孵化范式革命的研究文化（TensorFlow/JAX/TPU 都是研究产物）。**Apple 给不了 Lattner"做 AI 编译新范式"的环境，Google 能**。

> **关键洞察（与 §10.3 接力棒定律联动）**：**MLIR 是 Lattner 的第二次范式点火**——第一次是 LLVM（2000，UIUC/Apple），第二次是 MLIR（2017–2019，Google）。**范式创新跟着点火人走，不跟着项目走**——Lattner 离 Apple 后，LLVM core 的范式创新停滞（2017 后无 Clang/Swift 级跃迁），创新跟着他到了 Google/Modular。这是接力棒第 3 棒的交接（见 §10.3 + Lens_01 判断四）。

### 8.3 MLIR "借壳 monorepo"——sustaining 的姿态，disruptive 的 DNA

MLIR 进了 LLVM monorepo、用 LLVM Foundation 治理、lowering 到 LLVM IR——**从组织看是 sustaining**。但 Lens_02 Christensen 透镜 `[项目内 Lens_02 判断三]` 给出了最锋利的一刀：**MLIR 对 LLVM 组织是 sustaining，对 LLVM core 的中心地位是 disruptive，对 AI 编译器市场是教科书级新市场破坏**。

**项目内实测铁证**：`[实测-count]` `mlir/include/mlir/Dialect/` 下 **45 个方言子目录**（Affine/AMDGPU/Arith/ArmSVE/Async/GPU/IRDL/Linalg/LLVMIR/MemRef/NVGPU/SPIRV/Tosa/Transform/Vector/XeGPU/...）vs LLVM IR **一个写死的类型系统**——**范式断裂的物理证据** `[项目内 Lens_01/Lens_02 实测]`。45 个方言意味着 MLIR 不要求一个固定语义，允许任何人定义新方言——这是**反 Brian Arthur 锁定的设计**，也是 MLIR 比 LLVM IR 更难预测的地方（可能颠覆 LLVM core，但也可能因碎片化而锁不住）。

> **教训 F（借壳定律）**：**新范式往往以"在位者的子项目"姿态入场，而非外部敌人**——MLIR 进 LLVM monorepo 像鸠占鹊巢；Cranelift 进 Bytecode Alliance 像寄生；Mojo 借 MLIR 起步。**GCC 当年被从外部颠覆（没有"亲儿子"做新维度），LLVM 把 MLIR 收为子项目是用 sustaining 的姿态做 disruptive 的事**。这是 Christensen《Innovator's Solution》"spin-out 自救"思想的变种（见 §10.4）。

---

## 9. 硬问题 8：Rust 1.0（2015）——LLVM 成为系统语言后端

### 9.1 事实链（一手 + 校正）

> **诚实校正**：用户硬问题原文为"2018 Rust 1.0"。**实际 Rust 1.0 发布于 2015-05-15** `[社区共识/rust-lang.org]`。2018 年是 **Rust Edition 2018**（语言重大修订，引入 async/await、模块系统改版等），不是 1.0。本节以正确日期 2015 展开，2018 Edition 作为后续演化提及。

Rust 由 Graydon Hoare 在 Mozilla 发起（2006 个人项目，2010 Mozilla 官方赞助）。**Rust 1.0（2015-05-15）是第一个稳定的、生产可用的 Rust**。Rust 从 1.0 起**全押 LLVM 后端**——`rustc` 把 Rust 编译到 LLVM IR，再用 LLVM CodeGen 生成机器码 `[社区共识]`。

### 9.2 Rust 为什么全押 LLVM 而非自研后端？

**因 1：自研后端的成本不可承受。** 一个生产级后端需要覆盖 ~10 个主流 ISA（x86/ARM/PowerPC/RISC-V/MIPS/...）、做指令选择 + 调度 + 寄存器分配 + ABI + 调试信息 + ...——**这是 LLVM 用 15 年（2000–2015）积累的资产**。Mozilla 作为非营利浏览器公司，**没有资源**自研后端。**用 LLVM = 立刻支持所有 ISA**。

**因 2：LLVM 的 Apache 2.0 + LLVM Exception 许可证对 Mozilla 完全友好**。Rust 是 MPL/Apache 双许可，与 LLVM 的 Apache 2.0 完全兼容。如果 LLVM 是 GPLv3，Mozilla（商业敏感的 Firefox 母公司）会有顾虑。

**因 3：LLVM 的代码质量在 2015 已经"够用"。** Rust 的核心卖点是内存安全（所有权/借用检查），**不是代码生成质量**。Rust 用 LLVM 的 -O2/-O3 已经能产出"接近 C"的性能——这对 Rust 的定位（系统语言）足够。

### 9.3 Rust 全押 LLVM 的战略后果

Rust 1.0 全押 LLVM 是**战争三（LLVM vs GCC）胜负已分的标志性事件**——它意味着：

- **新系统语言默认选 LLVM**。Swift（2014）、Rust（2015）、Zig（2016+）、Flang（2019）——**所有 2010s 诞生的系统语言都默认用 LLVM 后端**。GCC 在"新系统语言后端"市场份额跌至接近 0 `[推测-依据]`。
- **LLVM 成为"系统语言的公共后端"**。这个地位一旦确立，**Brian Arthur 锁定效应**（§10.5）就开始发酵——任何新系统语言想被采纳，迁移成本最低的路径就是接 LLVM。**这是 LLVM IR 锁定系统语言工具链的起点**。
- **GCC 退守"老语言 + 长尾"**。GCC 此后的市场份额主要靠：C/C++ 遗留代码、Linux 内核编译（Linus 没强制切 Clang）、gfortran（HPC）、嵌入式长尾。**GCC 从"通用编译器"降级为"特定领域的编译器"** `[推测-依据]`。

> **教训 G（公共后端定律）**：**当一个编译器后端被 ≥ 3 个主流新语言同时采用，它就锁定了"系统语言公共后端"地位，Brian Arthur 式不可逆**。LLVM 在 2015–2017 完成 this 锁定（Swift + Rust + Zig + Flang）。**这条定律预言了 MLIR 的路径——它要先在 AI 框架（torch-mlir/StableHLO/IREE）里完成 ≥ 3 个采用，才能锁定"AI 编译公共 IR"地位**（2024–2026 正在这个相位）。

### 9.4 Rust 2018 Edition——LLVM 后端的延续与 Cranelift 的伏笔

2018 Rust Edition 引入 async/await、模块系统改版，但**后端仍是 LLVM**。值得注意的是，**Cranelift（见 Lens_02 判断二）在 2020 年成为 Rust nightly 可选 codegen 后端**——这是 Rust 第一次尝试"非 LLVM 后端"。但 Cranelift 只用于 debug build（编译快、代码慢），**release build 仍是 LLVM**。这预示了 §11 讨论的"LLVM 是否会被 Cranelift 颠覆"——目前看，Cranelift 卡在 JIT/debug niche，未完成对 LLVM 主场的颠覆 `[项目内 Lens_02 下注 1]`。

---

## 10. 硬问题 9：2020 Apple Silicon——LLVM 帮 ARM 反攻 x86

### 10.1 事实链

2020-11-10，Apple 发布 **M1 芯片**（首款 Apple Silicon Mac），基于 ARMv8.5-A，自研 Fire Storm（大核）+ Ice Storm（小核）微架构 `[社区共识]`。M1 在发布时**性能/能效碾压同代 x86 笔记本**（Intel/AMD），引发"ARM 反攻 x86"的全球讨论。

**M1 的整个软件栈 built with LLVM/Clang**——macOS、iOS、所有 Apple framework、Xcode、Swift 全部用 Clang 编译。**没有 LLVM，就没有 Apple Silicon**——因为 GCC 在 2011 已被 Apple 踢出，Apple 的全栈早就 all-in LLVM。

### 10.2 LLVM 在 Apple Silicon 反攻里的三个角色

**角色 1：编译器基础设施**。M1 的 macOS/iOS 整个操作系统用 Clang 编译。`[实测-grep]` `AArch64Processors.td` 第 1417–1633 行的 **apple-m1/apple-m2/.../apple-m5** 调度模型——Apple 把 M1 到 M5 每一代的微架构调度都养进了 LLVM upstream `[项目内 Lens_01 实测]`。**这是 Apple Silicon 能跑得快的编译器层前提**。

**角色 2：Rosetta 2 的底层**。Rosetta 2（x86 → ARM 二进制翻译）虽然核心是 Apple 自研的翻译引擎，但它**生成的 ARM 代码用 LLVM 做最终优化** `[推测-依据]`。LLVM 的 AArch64 CodeGen 让 Rosetta 2 翻译出来的代码接近原生性能。

**角色 3：ARM 生态的"反攻 x86"基础设施**。Apple Silicon 的成功**证明了 ARM 在桌面/笔记本可以打败 x86**——这直接推动了：高通骁龙 X Elite（2023，Oryon 核心，也是 ARM）、微软 Surface 的 ARM 化、NVIDIA Grace CPU（2022+，ARM 数据中心）。**这些 ARM 芯片全部用 LLVM 编译**——`[实测-grep]` `AArch64Processors.td` 有 `oryon-1`（高通）、`grace`/`gb10`（NVIDIA）、`ampere1`系列（Ampere）、`cobalt-100`（微软 alias）`[项目内 Lens_01 实测]`。**LLVM 成为 ARM 反攻 x86 的公共编译器基础设施**。

### 10.3 Apple Silicon 反攻的方法论意义

Apple Silicon 是**战争三（LLVM vs GCC）的延伸战场**，但它的意义超越了编译器战争本身——它是**ISA 战争（ARM vs x86）的转折点**，而 LLVM 是这个转折的**编译器层载体**。

> **关键洞察（与 Chris Miller《Chip War》框架联动）**：Miller 在《Chip War》`[书/Miller2022]` 论证 ARM 的命运由"谁在养它"决定——ARM 1990 从 Acorn 剥离 → 苹果 Newton 投资 → iPhone 移动市场工业化 → 全行业授权。**2020 Apple Silicon 是 ARM 反攻 x86 桌面/数据中心的"反攻主场时刻"**。**LLVM 在这场反攻里的角色，正是 Miller 笔下"商业模式决定技术命运"的编译器层实现——ARM 阵营（Apple/高通/NVIDIA/Ampere）全用 LLVM，x86 阵营（Intel/AMD）也用 LLVM，LLVM 成为 ISA 战争的"中立军火商"** `[推测-依据]`。

### 10.4 教训（写入表 2）

> **教训 H（中立军火商定律）**：**当一个编译器基础设施被战争双方（ARM 阵营 + x86 阵营）同时采用，它就从"某阵营的工具"升级为"ISA 战争的中立军火商"**——这是 LLVM 在 2020 后的全球地位。**这条定律解释了为什么美国出口管制（ARM v9 不授中国）对飞腾是致命的——飞腾被排除在"LLVM 养育的 ARM 阵营"之外，只能停留在 ARMv8.4（见 §12 + 项目宪法 §0）**。

---

## 11. 硬问题 10：2023 Mojo——Lattner 创立 Modular，下一代编译器？

### 11.1 事实链（一手：Modular 发布会）

**2023-05-02**，Modular 公司（Lattner 2022 创立，联合创始人 Tim Davis，前 Google ML 负责人）发布 **Mojo** + **Modular Inference Engine** `[一手/modular.com/blog + 发布会 keynote]`。Jeremy Howard（fast.ai 创始人）在 2023-05-03 的评测 `[报道/fast.ai]` 里称：

> "This may be the biggest programming language advance in decades... the second time in my life I've had that feeling."

Mojo 的核心定位：**Python 超集 + C 级性能**，构建在"下一代编译技术（MLIR + LLVM）"之上 `[一手/modular.com]`。发布会 demo：**Mandelbrot 算法 Mojo 比 Python 快 35000×**（AWS r7iz.metal-16xl 上 Mojo 0.03 秒 vs Python 3.10.9 1027 秒）`[报道/Register 2023-05-05]`。

### 11.2 Mojo 的技术栈：MLIR 的"Clang 时刻"

Lattner 在 Developer Voices 播客 `[一手/modular.com/blog]` 解释 Mojo 的技术栈：

> "We weren't originally intending to build a language at Modular. We started building a very fancy code generator that had no frontend. **We wrote everything using a new compiler framework named MLIR**. It's now part of the LLVM family, but it's a next generation replacement in many ways. It allows making domain specific compilers really fast...
>
> **Swift in a way was syntactic sugar for LLVM**, at the very bottom of the stack it could talk directly to LLVM primitives. **Mojo does basically that same trick, but it supercharges it by moving to this MLIR world.**"

**关键洞察**：**Mojo 是"MLIR 的 Clang 时刻"**——正如 Clang 是"LLVM 的一等前端"（让 LLVM 从后端升级为全栈），Mojo 是"MLIR 的一等前端"（让 MLIR 从"AI 编译中间层"升级为"AI 编程语言基础设施"）。这呼应了 §6.3 的"前端定律"——**一个后端/IR 要颠覆在位者，必须有自己的一等前端**。

### 11.3 Mojo 是 Christensen 新市场破坏（教科书形态）

Lens_02 `[项目内 Lens_02 判断四]` 用 Christensen 框架判定 Mojo 是**新市场破坏的精确形态**：

- **Mojo 不抢 Python 的研究/探索用户**（那些人不在乎性能，Python 对他们未过度供给）。
- **Mojo 瞄准一个被碎片化服务的新 job**："我想用 Python 的语法，但我需要 C 的性能，去写 AI 推理引擎/自定义算子/系统级 ML 代码"。这个 job 今天由 Python + C 扩展 + Cython + Numba + Triton + CUDA C 的笨拙栈完成。
- **Mojo 把这个碎片化的 job 缝合成一个新市场的单一产品**——把"非消费者"（因为 Python 慢而不敢用 Python 写系统代码的人）变成"消费者"。**这是 Christensen 新市场破坏的教科书定义**。

### 11.4 Mojo 的三个风险（Christensen 框架的警告）

但 Mojo 不是稳赢。Lens_02 `[项目内 Lens_02 判断四]` 给出三个风险警报：

1. **生态锁定太厚**：Python 在 ML 研究里的锁定（Jupyter/NumPy/PyTorch）是 Christensen 模型里"切换成本"的极端案例。Mojo 即便快 35000×，也撼动不了研究者的 notebook 习惯。
2. **商业模式风险**：Modular 是商业公司（Mojo 早期不开放，2024 才部分开源标准库）`[一手/modular.com/blog]`。与免费 Python+Cython+Numba 竞争，这是它最大的商业风险。**若 Mojo 不彻底开源进 Foundation，它无法成为接力棒第 5 棒**（见 §10.3 定律二）。
3. **性能过度供给检验不通过**：ML 研究者用 Python 不是因为它"够快"，是因为它"够方便"——方便这个维度远未过度供给。纯低端颠覆对 Python 无效，Mojo 必须靠新市场破坏，这比低端颠覆更慢、更不确定。

> **教训 I（点火人定律）**：**Mojo 是 Lattner 的第三次范式点火**——LLVM（2000）、MLIR（2017）、Mojo（2022）。**一个点火人连续三次点中范式革命的窗口，在技术史上极为罕见**（类比：Dennis Ritchie 点了 C + Unix 两次；Brendan Eich 只点了 JavaScript 一次）。**但点火人的成功率随年龄/资源约束递减**——Lattner 在 UIUC（学术自由）→ Apple（千亿金主）→ Modular（VC 支持但商业压力）的资源环境在递减。**Mojo 是 Lattner 范式点火里风险最高的一次**（见 §10.3 + Lens_01 判断四）。

---

## 12. 五张图：把战争可视化

### 图 2：Apple-Lattner-LLVM 三角（2005–2017 工业化期）

```
                          ┌─────────────────┐
                          │   Chris Lattner │
                          │  (点火人/枢纽)   │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
            ┌───────────┐  ┌─────────────┐  ┌───────────┐
            │   Apple   │  │     LLVM    │  │  UIUC/Adve│
            │ (金主/平台)│◄─┤  (技术范式)  ├─►│(学术孵化) │
            └─────┬─────┘  └──────┬──────┘  └───────────┘
                  │               │
                  │  雇佣+all-in  │ 养育调度模型
                  │  (2005)       │ (apple-a7..m5)
                  ▼               │
            ┌───────────┐         │
            │  Xcode /  │◄────────┘
            │ macOS/iOS │ Clang/LLDB/Swift
            │ (强制迁移) │ 全建在 LLVM
            └───────────┘
                  │
                  │ 2011 WWDC GCC 出局
                  ▼
            ┌───────────────────────┐
            │ LLVM 锁定 Apple 生态   │
            │ (Brian Arthur 锁定)   │
            └───────────────────────┘
```

**图 2 读法**：Lattner 是 Apple-LLVM-UIUC 三角的枢纽。Apple 提供"金主 + 平台 + 强制迁移"，UIUC 提供"学术孵化 + 范式基因"，LLVM 是技术范式的载体。**三角的稳定运转（2005–2017）让 LLVM 从学术项目变成工业基础设施**。2017 Lattner 离 Apple，三角解体——Apple 继续"消费"LLVM，但范式创新跟着 Lattner到了 Google（MLIR）。

### 图 3：Google-MLIR 接力（2017–2026 范式点火期）

```
   2017 Lattner 离 Apple
        │
        ├─► Tesla (短暂，自动驾驶)
        │
        └─► Google Brain (2017+)
                │
                │  范式异常：LLVM IR 表达不了
                │  AI/异构的"多级抽象"
                │
                ▼
   ┌─────────────────────────────┐
   │   MLIR 项目 (2019 EuroLLVM)  │
   │   Lattner + Mehdi Amini +   │
   │   Shpeisman + Vasilache +   │
   │   River Riddle (Google/TensorFlow)│
   └──────────────┬──────────────┘
                  │
                  │ 2019-12-24 commit 0f0d0ed1
                  │ 捐入 LLVM monorepo (+226337 行)
                  │
                  ▼
   ┌─────────────────────────────┐
   │  MLIR 方言爆炸 (2020-2026)  │
   │  [实测] 45 个方言子目录:    │
   │  Affine/GPU/Linalg/SPIRV/   │
   │  Tosa/Vector/XeGPU/NVGPU...│
   └──────────────┬──────────────┘
                  │
                  │  采用方涌入
                  ▼
   ┌─────────────────────────────┐
   │ StableHLO / IREE / torch-   │
   │ mlir / Intel graph-compiler │
   │ / AscendNPU-IR (华为)       │
   │ → MLIR 锁定"AI 编译公共 IR" │
   └─────────────────────────────┘
```

**图 3 读法**：Google 接力 Apple，成为 MLIR 的金主。**MLIR 进 LLVM monorepo 是"借壳"**——组织上 sustaining，范式上 disruptive。45 个方言是范式断裂的物理证据。**采用方涌入（2024–2026）是 MLIR 锁定"AI 编译公共 IR"地位的相位**（对应 Rust 1.0 对 LLVM 的锁定时刻，见 §9.3）。

### 图 4：Mojo 的技术栈分层（2023+）

```
   ┌─────────────────────────────────┐
   │       Mojo 源码 (Python 超集)    │  ← 用户层
   └────────────────┬────────────────┘
                    │ Mojo 编译器前端
                    │ (parser 直接生成 MLIR，无传统 AST)
                    ▼
   ┌─────────────────────────────────┐
   │          MLIR (多级 IR)          │  ← 范式层
   │  [实测] 45 个方言: Linalg/Vector│
   │  /GPU/Affine/Arith/MemRef/...   │
   └────────────────┬────────────────┘
                    │ lowering (逐级下沉)
                    ▼
   ┌─────────────────────────────────┐
   │      LLVM IR (单层 SSA IR)       │  ← 传统后端
   └────────────────┬────────────────┘
                    │ LLVM CodeGen
                    ▼
   ┌─────────────────────────────────┐
   │  机器码 (x86 / ARM / GPU / NPU) │  ← 硬件层
   └─────────────────────────────────┘

   关键：Mojo = "MLIR 的 Clang 时刻"
        （让 MLIR 从"中间层"升级为"语言基础设施"）
```

**图 4 读法**：Mojo 的技术栈是**三层 IR 下沉**（Mojo 源码 → MLIR → LLVM IR → 机器码）。**Mojo 的 parser 直接生成 MLIR，绕过传统 AST**——这是 Lattner 在播客里强调的创新（"we don't build an AST traditionally, we generate MLIR directly from the parser"）`[一手/modular.com]`。**Mojo 是 MLIR 的"一等前端"**，正如 Clang 是 LLVM 的"一等前端"。这条分层结构预示了 MLIR 对 LLVM core 的"降级"——LLVM IR 从"通用后端"降为"MLIR 的 lowering 目标之一"（见 §13 下注 2）。

### 图 5：四场战争的相位对齐（30 年周期律）

```
战争一: 专有Unix编译器 vs 开放
1970s ──────────────────────────── ~2000 (~30年)
       │ GCC 1987 起步
       │ 商业编译器随 Unix 厂商消亡

战争二: GCC vs 商业 C/C++ 编译器
1987 ──────────────────────────────── 2017 (~30年)
       │ EGCS 1997 自救
       │ ICC 2023 被 LLVM(oneAPI) 替代
       │ 结局：GCC 赢，商业退场

战争三: LLVM vs GCC (系统语言后端)
2000 ───────────────────────────────── 2026 (~26年, 胜负已分)
       │ Apple 2005 接棒
       │ Clang 2007 / WWDC 2011 GCC 出局
       │ Rust 2015 全押 LLVM
       │ Apple Silicon 2020 ARM 反攻
       │ 结局：LLVM 赢，GCC 退守内核/HPC

战争四: MLIR vs LLVM core (AI/异构)
2019 ─────────────────────────────────── ? (~20-30年, 进行中)
       │ commit 0f0d0ed1 2019-12-24
       │ Mojo 2023 第三次点火
       │ 反攻主场窗口预测: 2029-2034
       │ (Lens_01 判断三 + 本专题 §13)

  规律: 每场 ~20-30 年；后一场颠覆者
       总在前一场成熟期里发芽 (Perez 长波)
```

**图 5 读法**：四场战争叠瓦式接力。**反攻主场时刻 ≈ 颠覆者诞生后 10–15 年**——LLVM 2000 诞生 → 2011 WWDC 反攻（11 年）；MLIR 2019 诞生 → **2029–2034 反攻主场窗口** `[推测-依据]`。这是本专题对未来最重要的预测（见 §13）。

---

## 13. 三张对照表：每场战争的赢家/输家/教训

### 表 1：四场战争的总对照（赢家 / 输家 / 转折点 / 教训）

| 战争 | 时段 | 颠覆者 | 在位者 | 赢家 | 输家 | 商业转折点 | 核心教训 |
|:----:|:----:|:------:|:------:|:----:|:----:|:----------|:---------|
| **一** | 1970s–2000 | 开放编译器（GCC 1987） | IBM/Sun/SGI/DEC/HP 专有编译器 | **GCC/开放** | 专有 Unix 编译器（随 Unix 厂商消亡） | Linux 内核 1991 锁定 GCC | **教训 A**：许可证+跨平台+生态共生是护城河，闭源单平台必败 |
| **二** | 1987–2017 | GCC | 商业 C/C++（ICC/Sun Studio/PGI） | **GCC** | ICC（2023 被 LLVM/oneAPI 替代）、Sun Studio、PGI（被 NVIDIA 收购转 LLVM） | GCC 跨 30+ 架构 + Linux 生态共生 | **教训 A 强化**：商业编译器无法对抗"免费+跨平台+生态"的公地 |
| **三** | 2000–2026 | LLVM | GCC | **LLVM**（系统语言主场） | GCC（退守 Linux 内核/HPC/嵌入式长尾） | 2011 WWDC GCC 出局 + 2015 Rust 全押 LLVM | **教训 E+G**：平台所有者强制迁移 + 公共后端锁定 = 不可逆 |
| **四** | 2019–? | MLIR（+ Mojo） | LLVM core | **进行中**（MLIR 在 AI 扎根） | 待定（LLVM core 可能被降级为 lowering 目标） | 2019-12-24 commit 0f0d0ed1 + 2024–2026 StableHLO/IREE 涌入 | **教训 F**：新范式以"在位者子项目"姿态入场（借壳） |

### 表 2：每场战争的"颠覆三要素"打分（技术范式优势 × 在位者内部矛盾 × 大金主）

> 本表用 §10.1 的颠覆三要素定律打分。**三者乘积为零则颠覆失败**。

| 战争 | 技术范式优势 | 在位者内部矛盾 | 大金主 all-in | 三要素乘积 | 结局 |
|:----:|:----------:|:-------------:|:------------:|:---------:|:----:|
| **一**（开放 vs 专有） | 🟢 GPL+跨平台+生态（重新定义"什么是编译器基础设施"） | 🟢 专有 Unix 厂商锁死单平台 | 🟢 FSF（非营利金主）+ Linux 内核（生态金主） | **满** | 开放赢 |
| **二**（GCC vs 商业） | 🟢 GCC 自由+跨架构 | 🟢 商业编译器绑定单一 Unix/芯片 | 🟢 FSF + Cygnus（商业化 GCC） | **满** | GCC 赢 |
| **三**（LLVM vs GCC） | 🟢 SSA+模块化+类型化 IR+lifelong analysis（Kuhn 范式革命） | 🟢 GCC 的 GPLv3 + 单体 RTL + Steering Committee 保守 | 🟢 Apple（千亿金主）+ Google/AMD/NVIDIA/ARM（多金主） | **满** | LLVM 赢 |
| **四**（MLIR vs LLVM core） | 🟢 可扩展方言+多级 IR（重新定义"什么是 IR"） | 🟡 LLVM core 的刚性 IR 在 AI 编译累积成 Kuhn 异常 | 🟢 Google + Lattner + ARM/AMD/NVIDIA/华为（多金主） | **2.5/3**（反攻主场未完成） | 进行中，MLIR 在 AI 扎根但未反攻系统语言主场 |
| **Polly**（多面体优化） | 🟡 多面体优化（sustaining，非范式革命） | 🔴 LLVM core 无强烈内部矛盾 | 🔴 无大金主（学术项目） | **0** | 未颠覆，沦为 LLVM 子项目 |
| **Cranelift**（快速 JIT） | 🟡 编译速度新维度 | 🟡 LLVM 在 debug/JIT 过度供给 | 🟡 Bytecode Alliance（小团队，无千亿金主） | **1/3** | 卡在 JIT/debug niche，未颠覆主场 |

**表 2 读法**：**颠覆三要素是乘法关系，不是加法**——Polly 技术好但无金主（0），Cranelift 有新维度但金主不够厚（1/3），都未颠覆。**MLIR 是唯一三要素都满（除反攻主场未完成）的候选**——这是它被本专题 + Lens_01/Lens_02 共同判为"LLVM 真正威胁"的方法论依据。

### 表 3：10 场战役的"点火人-金主-接力棒"谱系

| 战役 | 年份 | 点火人 | 金主 | 接力棒 | 范式贡献 |
|:----:|:----:|:------:|:----:|:------:|:---------|
| GCC 1.0 | 1987 | Stallman | FSF | 第 0 棒（GCC） | 自由+跨平台编译器 |
| EGCS 分叉 | 1997 | Henkel-Wallace + Cygnus 团队 | Cygnus | （GCC 内部接力） | 治理改革 → Steering Committee |
| LLVM 构想 | 2000 | Lattner + Adve | UIUC/NSF | 第 0 棒（LLVM） | SSA+模块化+类型化 IR |
| LLVM MS 论文 | 2002 | Lattner | UIUC | 第 0 棒 | lifelong analysis 范式 |
| LLVM CGO 论文 | 2004 | Lattner + Adve | UIUC/NSF | 第 0 棒 | LLVM 范式宣告 |
| Apple 接棒 | 2005 | Lattner（被 Apple 招） | **Apple** | **第 1 棒** | Clang/LLDB/Swift 工业化 |
| Clang 出鞘 | 2007 | Naroff/Gregor/Kremenek + Lattner | Apple | 第 1 棒 | LLVM 一等前端 |
| WWDC GCC 出局 | 2011 | Bob Wilson + Apple | Apple | 第 1 棒（锁定） | 平台强制迁移 |
| Foundation 成立 | 2014 | Tanya Lattner + 社区 | 多公司 | 第 2 棒（中立化） | 治理去 Apple 化 |
| Lattner 离 Apple | 2017 | Lattner（个人选择） | — | （接力棒真空） | 范式创新转移 |
| MLIR 提议 | 2019 | Lattner + Amini + Shpeisman | **Google** | **第 3 棒** | 多级 IR + 方言 |
| MLIR 捐入 monorepo | 2019 | Mehdi Amini (joker-eph) | Google/Foundation | 第 3 棒 | 借壳入场 |
| Mojo 发布 | 2023 | Lattner + Tim Davis | **Modular（VC）** | **第 5 棒？** | MLIR 一等前端 |

**表 3 读法**：**点火人 Lattner 串起了 4 次范式点火**（LLVM 2000 / Clang 2007 / MLIR 2017 / Mojo 2022），跨 3 个金主（UIUC / Apple / Google / Modular）。**接力棒定律（§10.3）的物证就在这张表里——范式创新跟着点火人走，不跟着项目走**。Lattner 离 Apple 后，LLVM core 的范式创新停滞（2017 后无 Clang/Swift 级跃迁），创新跟着他到了 Google（MLIR）和 Modular（Mojo）。

---

## 14. 三条贝叶斯先验（定律）+ 对 2026–2034 的预测

### 14.1 定律一：颠覆三要素定律（编译器范式颠覆成功 = 技术范式优势 × 在位者内部矛盾 × 大金主 all-in）

> **三者乘积为零则颠覆失败**。GCC→LLVM 三者都满；MLIR 三者都满（除反攻主场未完成）；Polly 无金主（0）；Cranelift 金主不够厚（1/3）。

**对 2026–2034 的预测**：
- 任何想颠覆 LLVM 的项目，必须同时凑齐三要素。**目前只有 MLIR 凑齐**（技术范式=可扩展方言、内部矛盾=LLVM core 刚性 IR、金主=Google+多公司）。
- **Mojo 是变数**——技术范式（MLIR 一等前端）和金主（Modular VC）都凑齐，但"反攻主场"未完成，且商业闭源是风险。若 Mojo 2027 前彻底开源进 Foundation，可能成第 5 棒；若保持商业，可能重蹈 Transmeta 覆辙 `[推测-依据]`。

### 14.2 定律二：接力棒定律（范式创新从不在 Foundation 官僚手里发生，总在新金主手里发生）

> **Foundation 的作用是"让项目在金主切换时不死"，不是"让项目自我进化"**。每次范式跃迁 = 接力棒从旧金主交到新金主。

**物证**（§13 表 3）：
- UIUC（第 0 棒）→ Apple（第 1 棒，Clang/Swift）→ Foundation（第 2 棒，治理中立化但范式创新停滞）→ Google（第 3 棒，MLIR）→ Modular？（第 5 棒？Mojo）。
- **Foundation 阶段（2014–2017 Apple 仍在 + 2017 后）LLVM core 无 Clang/Swift 级跃迁**——这是接力棒定律的直接验证。

**对飞腾的含义**（与 Lens_07/S4 对偶）：飞腾在整个接力棒史里**完全缺席**——`[实测-grep]` 主线 LLVM 全树零 phytium/ftc86 命中，对照香山（xiangshan-nanhu）已在 mainline `[实测-read] RISCVProcessors.td:796`。**飞腾是接力棒的观众，不是跑者**。差异不在国籍（香山证明中国项目能进 LLVM），在养育策略（见 §15 + S4 专题）。

### 14.3 定律三：30 年周期律（每场战争 ~20–30 年，后一场颠覆者在前一场成熟期发芽）

> **反攻主场时刻 ≈ 颠覆者诞生后 10–15 年**。LLVM 2000→2011 反攻（11 年）；MLIR 2019→**2029–2034 反攻窗口**。

**对 2029–2034 的预测**（与 Lens_01 判断三 + 下注 1 联动）：
- **2026–2029**：MLIR 在异构后端（GPU/NPU/DSA）成为事实标准，开始蚕食 LLVM core 的"lowering 目标"地位。
- **2029–2034（反攻主场窗口）**：MLIR 出现"绕过 LLVM IR 直接生成机器码"的生产级路径。**这是判断 MLIR 是"LLVM 的高层前端"还是"LLVM 的继任者"的判决性事件**。
- **2034+**：若反攻成功，LLVM IR 退居"MLIR 的一个 lowering 后端"（类比 GCC 退居 Linux 内核）；若失败，MLIR 沦为"AI 专用高层 IR"，与 LLVM core 长期分层共存。

**诚实校准**：30 年规律是**贝叶斯先验不是物理定律**。它可能被打破——(a) AI 编译需求 2030 前突然饱和；(b) LLVM core 主动接纳 MLIR 思想（已部分发生）；(c) Mojo/Modular 走通"新语言+新 IR"路线成为第三方；(d) AI/LLM 重构编译器（mlirAgent/mlir-opt-repl MCP 等 2026 苗头）打断所有历史曲线 `[推测-依据]`。

---

## 15. 飞腾在 30 年战争里的位置（项目锚点，对偶 Lens_07/S4/E18）

本专题是"通史"，但必须回答**飞腾在这 30 年里在哪里**——这是项目宪法（§0.3 v2.0）的强制要求。

**飞腾的位置：四场战争的纯观众，接力棒的局外人。**

- **战争一/二（专有 vs 开放 / GCC vs 商业）**：飞腾 1987 还不存在（飞腾 2000s 才起步）。**缺席**。
- **战争三（LLVM vs GCC）**：飞腾是**消费者**。`[实测-项目内 E18]` 飞腾 45 个公开仓库**零自研 LLVM/Clang patch**——Android 用 LLVM 12 vanilla、Yocto 用 LLVM 13.0.1（上游 recipe）、Buildroot 用 LLVM 9.0.1、FreeBSD 用 LLVM 19.1.7；`grep FTC86|Phytium|phytium` 在 `external_llvm-project` 零命中 `[项目内 Lens_02 §2.5 实测]`。飞腾的 PhyCC（基于 LLVM）和 PhyGCC（基于 GCC）都是**改名 fork，闭源，零 upstream 贡献** `[官方/phytium.com.cn]`。
- **战争四（MLIR vs LLVM core）**：飞腾仍是**消费者**。飞腾 NPU 编译器（phytvm）是 **Apache TVM fork**（非自研 MLIR 后端），oracle §0.3 已澄清 `[改造蓝图§0.2]`。

**对照香山（中国开源 RISC-V）**：`[实测-read]` `RISCVProcessors.td:796` `XIANGSHAN_NANHU` + 独立调度文件 `RISCVSchedXiangShanNanHu.td`——**香山在主线 LLVM 有调度模型，飞腾（中国 ARM）没有**。**这是本专题最锋利的一刀：中国项目能进 LLVM upstream，飞腾没进，差异不在国籍而在养育策略** `[项目内 Lens_01 判断五]`。

**S4 专题的 2026 更新** `[项目内 S4]`：截至 2026-07，六家国产 CPU 厂商中**四家已是主线 LLVM 一等公民**——龙芯（官方 Maintainer Weining Lu）、华为（TSV110 + 毕昇 + 昇腾 CANN）、海光（c86-4g 全系列 2026-06 合入，+90000 行）、平头哥（C910V2/C920V2 2026-02 合入）。**只剩飞腾和申威仍在外围**。**飞腾是六家里编译器投入最浅的**（团队推测 5–15 人，主线零贡献）。

> **判决**：飞腾在 30 年编译器战争里**从头到尾是消费者**。这不是技术问题（飞腾 ARMv8.4 + FTC86x 微架构不比鲲鹏 TaiShan v110 差），是**养育策略问题**——飞腾没有把"在 LLVM upstream 养育自家调度模型"当成商业模式来投资。**接力棒定律（§14.2）的预言**：飞腾到 2030 仍是 LLVM mainline 的纯消费者，不会 upstream FTC86x，不会发起范式级贡献（Lens_01 下注 5，概率 90%）。

---

## 16. 盲区与反方（强制诚实段 §7.3.2）

通史最容易写成"软文"——把每场战争都讲成"颠覆者英明、在位者愚蠢"的爽文。**敢说看不见什么，才不是软文**：

1. **历史样本量太小**。编译器商业史只有 ~50 年（1957 Fortran 起），主流编译器 IR 案例 < 5 个（GCC GIMPLE / LLVM IR / MLIR / Cranelift IR / Mojo IR）。在这么小的样本上做"30 年周期律"模式匹配，**过拟合风险极高**——"每场 20–30 年"可能只是巧合。**本专题所有"规律"都是贝叶斯先验**，不是决定论。

2. **幸存者偏差**。历史记住 Stallman、Lattner，忘掉几百个真正写代码的贡献者。**"点火人叙事"夸大个人、贬低集体**——LLVM 的胜利是 Apple 一个连队的人 + UIUC + 全社区共同完成的，不是 Lattner 一人。Mojo 若失败，可能恰恰因为"靠一个人不够"。

3. **30 年规律可能被黑天鹅打断**。**AI 革命、LLM 重构编程、地缘断供、硬件范式突变（光计算/量子）**都可能打断所有历史曲线。Apple M1 2020 反超 x86 在 2015 年没人预测到；同样，2027–2030 若出现"LLM 自动生成 IR"（mlirAgent/mlir-opt-repl MCP 是 2026 苗头 `[资源库§7.8]`），MLIR 的所有历史类比都会失效。**历史学家擅长"解释过去"，不擅长"预测技术拐点"**。

4. **"颠覆"在开源世界常是"分层降级"而非"杀死"**。GCC 没死，它持续维护；BSD 没死，它持续维护。**本专题的"赢家/输家"叙事是简化**——现实是 GCC 退守保护市场（Linux 内核/HPC）持续存活，LLVM 大概率也会被 MLIR"分层降级"而非"杀死"（见 Lens_02 下注 2）。**Christensen 的"颠覆=杀死"在开源世界要改成"颠覆=重新分层"**。

5. **商业编译器的"输"不等于技术差**。DEC Alpha 1992 技术上全球最快 64-bit CPU，但 DEC 不广泛授权 → 商业模式失败 → 被 Compaq 收购 → 卖给 Intel 消亡 `[书/Miller2022]`。**Alpha 不是"技术不行被替代"，是"房东不会经营"**。同理，PGI/Sun Studio 的退场不全是技术劣势，部分是商业模式（绑单一 Unix/芯片）的失败。**本专题的"赢家/输家"打分偏重技术范式，低估了商业模式维度**——这是 Miller 框架（"商业模式决定技术命运"）对纯技术叙事的修正。

6. **Mojo 的不确定性最高**。本专题把 Mojo 列为"第 5 棒候选"，但 Mojo 2023 才发布，**3 年数据不足以判断**。Modular 是商业公司（与 LLVM/Foundation 的开源治理不同），Mojo 的开源进度（2024 标准库开源）和商业模式（MAX Engine/Serving 商业化）都在演化。**Mojo 可能成第 5 棒，也可能重蹈 Transmeta 覆辙，也可能被 Google/OpenAI 的 AI 编译新范式吸收**——三种结局概率都不低。

**反方一句话**：**30 年通史是事后诸葛亮的优雅——编译器的真实命运会被非历史规律（AI 技术突变、地缘黑天鹅、Modular 商业成败、社区治理危机）打断。本专题给出的是"如果历史节奏不变，最可能的轨迹"——但历史节奏从来不变是不可能的。**

---

## 17. 与其他视角对偶（强制 §7.3.3）

| 对偶视角 | 一致点 | **冲突点 / 互补** |
|---------|------|------|
| **Lens_01 历史学家** | 同用 30 年周期律、接力棒定律、颠覆三要素；都判 MLIR 是 LLVM 继任者候选 | **分工**：Lens_01 用框架看 LLVM 命运（5 判断 + 5 下注），本专题**把镜头对准战争本身**（10 场战役逐幕拆解）。Lens_01 是"框架应用"，本专题是"通史叙事"。两者基底同源，互为补充 |
| **Lens_02 Christensen** | 同判 LLVM 颠覆 GCC 是"新维度颠覆"（模块化）、MLIR 对 LLVM core 是"鸠占鹊巢" | **方法对偶**：Lens_02 用 Christensen 理论演绎（ sustaining vs disruptive），本专题用历史归纳（先例匹配）。**对 Mojo 判断一致**（新市场破坏），**对 Cranelift 判断一致**（卡在 niche） |
| **S4 国产 CPU 编译器投入** | 都判飞腾是 LLVM 纯消费者 | **正交互补**：S4 给六家厂商的量化 commit 数据（飞腾零贡献），本专题给"飞腾在 30 年战争里的历史定位"。S4 是空间快照，本专题是时间纵深 |
| **Expert_17 治理/License** | 都承认 Apache 2.0 vs GPL 是战争三的底层；都承认 Foundation 是接力棒的"不死保险" | **基调分歧**：E17 庆祝"Foundation 去公司化"，本专题指出"Foundation 后范式创新停滞，跟着 Lattner 走到 Google/Modular"（接力棒定律）。**E17 是治理成果视角，本专题是范式创新动力学视角** |
| **Expert_18 飞腾适配** | 都用 phytium_repos 实测 | **互补**：E18 给飞腾消费 LLVM 的工程细节（45 仓库零 patch），本专题给历史定位（接力棒的观众）。**本专题的零 phytium 实测是 E18 必引的反向锚点** |

---

## 18. 参考文献（22 条，分级标注）

> 标签遵循宪法 §7.3.1：`[书]`/`[论文]`/`[一手]`/`[官方]`/`[GitHub]`/`[GCC]`/`[报道]`/`[社区共识]`/`[实测]`/`[推测-依据]`。

1. **[论文/Lattner 2002 MS Thesis]** Chris Lattner, *LLVM: An Infrastructure for Multi-Stage Optimization*, M.S. Thesis, Computer Science Dept., University of Illinois at Urbana-Champaign, Dec. 2002. https://llvm.org/pubs/2002-12-LattnerMSThesis.html —— LLVM 的学术起点，§4 一手锚点。致谢原文确认 Vikram Adve 指导。
2. **[论文/Lattner-Adve 2004 CGO]** Chris Lattner & Vikram Adve, "LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation", *CGO 2004*, ACM DL. https://dl.acm.org/doi/10.5555/977395.977673 —— LLVM 范式的"big-bang"论文。
3. **[一手/SC21 Fireside Chat]** John Russell, "Lessons from LLVM: An SC21 Fireside Chat with Chris Lattner", HPCWire, 2021-12-27. https://www.hpcwire.com/2021/12/27/lessons-from-llvm-an-sc21-fireside-chat-with-chris-lattner/ —— Lattner 回忆 Apple 接棒、10.4 Tiger、OpenCL 是 Clang 第一个用户的逐字稿。
4. **[一手/LLVM early days PDF]** Chris Lattner, "LLVM - the early days", LLVM Dev Meeting, 2013-11-07. https://www.nondot.org/sabre/2013-11-07-LLVMDevMtg-LLVMEarlyDays.pdf —— LLVM 逐月时间线（2000-12 构想、2001-06 CVS 第一版、2001-07-08 getelementptr、2002-12 MS 论文、2003-10-24 1.0）。
5. **[一手/EGCS 公告]** D.V. Henkel-Wallace (gumby@cygnus.com), "A new project to merge the existing GCC forks", 1997-08-15. https://gcc.gnu.org/news/announcement.html —— EGCS 成立一手邮件，§3 核心。
6. **[一手/GCC History Wiki]** GCC Wiki, "History"（含 Cygnus Years / EGCS / Reunification / Steering Committee）. https://gcc.gnu.org/wiki/History —— 1999-04 合并 + 改名 GNU Compiler Collection + Steering Committee 1998-11-10 公告。
7. **[一手/GCC Steering Committee]** "GCC steering committee", 1998-11-10 原始公告. https://gcc.gnu.org/steering.html —— "preventing any particular individual, group or organization from getting control over the project" 原文。
8. **[一手/WWDC 2011 Session 307]** Bob Wilson, "Moving to Apple LLVM compiler", WWDC 2011. https://nonstrict.eu/wwdcindex/wwdc2011/307/ —— "GCC is going away" 逐字稿，§7 核心。
9. **[一手/WWDC 2010 Session 313]** "LLVM Technologies in Depth", WWDC 2010. https://nonstrict.eu/wwdcindex/wwdc2010/313/ —— Clang-in-Xcode、LLDB、集成汇编器，§6 核心。
10. **[一手/Lattner 2005 GCC Proposal]** Chris Lattner, "LLVM/GCC Integration Proposal", gcc mailing list, 2005-11-18. https://gcc.gnu.org/legacy-ml/gcc/2005-11/msg00888.html —— Lattner 最后一次尝试让 LLVM 与 GCC 共生。
11. **[一手/Fandrey 2010]** Dominic Fandrey, "Clang/LLVM", 2010 报告. https://llvm.org/pubs/2010-06-06-Clang-LLVM.pdf —— Clang 2010-05-29 自举（55 万行 C++）、FreeBSD 导入 Clang。
12. **[GitHub/MLIR commit]** llvm/llvm-project commit `0f0d0ed1` "Import MLIR into the LLVM tree", 2019-12-24, joker-eph (Mehdi Amini), +226337 行 / 300 文件. —— MLIR 进入 monorepo 的精确 git 锚点，§8 核心。
13. **[论文/Lattner et al 2021 CGO]** Chris Lattner, Mehdi Amini, Nicolas Vasilache, River Riddle et al., "MLIR: Scaling Compiler Infrastructure for Domain Specific Computation", *CGO 2021*. —— MLIR 作为新范式的学术宣告，副标题"Scaling"暗示 LLVM core 规模天花板。
14. **[一手/Modular Mojo 发布]** Modular, "Product Launch 2023 Keynote", 2023-05-02. https://www.modular.com/blog/mojo-llvm-2023 + https://www.youtube.com/watch?v=-3Kf2ZZU-dg —— Mojo 发布精确日期 + 35000× 性能 demo。
15. **[报道/fast.ai 2023-05-03]** Jeremy Howard, "Mojo may be the biggest programming language advance in decades", fast.ai, 2023-05-03. https://www.fast.ai/posts/2023-05-03-mojo-launch.html —— "the second time in my life I've had that feeling"，Mojo = "syntax sugar for MLIR"。
16. **[报道/Register 2023-05-05]** Thomas Claburn, "Modular finds its Mojo, a Python superset with C-level speed", The Register, 2023-05-05. —— Mojo 35000× 加速（Mandelbrot 0.03s vs Python 1027s）。
17. **[一手/Modular Developer Voices]** "Developer Voices: Deep Dive with Chris Lattner on Mojo", modular.com/blog. —— "Swift was syntactic sugar for LLVM, Mojo does that for MLIR"、"we generate MLIR directly from the parser"。
18. **[一手/CACM 2026]** Chris Lattner et al., "The LLVM Compiler Infrastructure", *Communications of the ACM*, 2026-07. https://cacm.acm.org/federal-funding-of-academic-research/the-llvm-compiler-infrastructure/ —— NSF 资助 LLVM 25 年回顾（学术出身的根深蒂固身份）。
19. **[书/Miller2022]** Chris Miller, *Chip War: The Quest to Dominate the World's Most Critical Technology*, Scribner, 2022. —— "商业模式决定技术命运"框架，§10.3 Apple Silicon + §16 Alpha 反例的方法论底座。
20. **[书/Christensen1997]** Clayton M. Christensen, *The Innovator's Dilemma*, HBR Press, 1997. —— 维持式 vs 破坏式、性能过度供给、RPV 框架，每场战争的因果引擎。
21. **[书/Kuhn1962]** Thomas S. Kuhn, *The Structure of Scientific Revolutions*, Univ. Chicago, 1962. —— 范式/常规科学/异常/革命机制，§4.2 LLVM "lifelong analysis"是 Kuhn 异常的精确复现。
22. **[实测/项目内源码]** 本项目 `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/`：(a) `cmake/Modules/LLVMVersion.cmake` LLVM 23.0.0git；(b) `LICENSE.TXT` Apache 2.0 with LLVM Exceptions；(c) `llvm/Maintainers.md:530-537` Chris Lattner Emeritus；(d) `llvm/lib/Target/RISCV/RISCVProcessors.td:796` XIANGSHAN_NANHU；(e) `.git/logs/HEAD` 单 commit 浅克隆（189 字节，commit 552e68d6, 2026-04-17）。
23. **[项目内文档]** [`Lens_01_Historian`](../Lenses/Lens_01_Historian.md)（30 年周期律 + 接力棒定律）、[`Lens_02_Christensen`](../Lenses/Lens_02_Christensen.md)（颠覆机制）、[`S4_China_CPU_Compiler_Investment`](./S4_China_CPU_Compiler_Investment.md)（飞腾零 upstream 数据）、[`领域资源库_LLVM.md`](../领域资源库_LLVM.md) §7（Lattner 资源池）。

---

## § 编译器产业史方法论（通用化，不只 LLVM）

> 本章把 S6 的 30 年通史上升为**任何技术产业历史分析都可复用的方法**。LLVM 是案例锚点，方法普适。

### 方法论一：颠覆三要素定律（定律一）

判断任何"新编译器/新 IR/新工具链能否颠覆在位者"，过三关：
1. **技术范式优势**：是否"重新定义了什么是问题、什么是解"（Kuhn 革命），还是只是"做得更好的旧范式"（演进）？判据：是否换了"关键投入品"。
2. **在位者的内部矛盾**：在位者是否有不愿改的结构性约束（License/治理/架构债）？GCC 的 GPLv3 + 单体 RTL 是典型；LLVM core 的刚性 IR 在 AI 编译累积成异常。
3. **大金主**：是否有 all-in 的金主？学术项目无金主 = Transmeta 式消亡。
**三者乘积为零则颠覆失败**。MLIR 三者都满（除反攻主场），Cranelift 缺第二第三，Polly 缺第三。

### 方法论二：接力棒定律（定律二）

判断开源基础设施的范式创新能力，看"接力棒在谁手里"：
- **Foundation 阶段**：项目不会死，但**范式创新停止**，转入各子项目的微架构创新。
- **范式跃迁**只发生在**新金主接棒**时（Apple→Google for MLIR，Google→Modular? for Mojo）。
- **对中国国产化的含义**：想从"消费者"升级到"共塑者"，必须**主动接棒**——香山接了 RISC-V 后端的棒，飞腾没接 AArch64 后端的棒。差异在**是否有"捐给 upstream"的政治意愿与工程投入**，不在技术能力。

### 方法论三：30 年周期律（定律三）

把技术产业的"主导范式之争"排成时间轴：
- 每场战争 **20–30 年**（软件比硬件快，半导体 ISA 周期 25–40 年）。
- **后一场战争的颠覆者，总在前一场战争的成熟期里发芽**（Perez 长波）。
- **反攻主场时刻 ≈ 颠覆者诞生后 10–15 年**。
- **校准**：周期律是贝叶斯先验，会被 AI 突变/地缘黑天鹅/商业成败打断。

### 产业史资源（通用）

- **必读书**：Chris Miller《Chip War》（"商业模式决定技术命运"最佳入门）、Christensen《创新者的窘境》、Kuhn《科学革命的结构》、Carlota Perez《技术革命与金融资本》。
- **方法论论文**：Brian Arthur 1989（锁定）、Bresnahan & Malerba 1999（产业演化）、Lattner & Adve 2004（LLVM 奠基）、Lattner et al 2021（MLIR 宣告）。
- **编译器史一手**：llvm.org 官方博客、Chris Lattner 个人主页 nondot.org/sabre、gcc.gnu.org、各 release notes、LLVM Dev Meeting 历年演讲、SC21/Lex Fridman/Pragmatic Engineer 访谈。
- **跨产业案例库**：ARM 兴衰（Miller Ch.8）、DEC Alpha 商业消亡、Transmeta/Mill Computing（技术好但无金主）、PowerPC（退守保护市场）——这些是编译器史模式匹配的"先例池"。

---

> **本专题一句话**：
> **30 年编译器战争史，是四场叠瓦式接力的范式之争——专有→开放（GCC 赢）、商业→自由（GCC 赢）、GCC→LLVM（LLVM 赢）、LLVM core→MLIR（进行中）。每一场战争的赢家都不是"做得更好的旧范式"，而是"重新定义了什么是编译器基础设施"的新范式；每一次范式跃迁都对应一次"点火人-金主-接力棒"的交接（Stallman→Lattner→Apple→Google→Modular）。而贯穿四场战争的，是 Chris Miller笔下"商业模式决定技术命运"的 immutable law——GCC 赢在 GPL+跨平台+Linux 生态共生，LLVM 赢在 Apache 2.0+模块化+Apple all-in，MLIR 正在赢在可扩展方言+Google+AI 异构新市场。飞腾在这 30 年里从头到尾是观众——证据就在 [实测-grep] 主线 LLVM 全树零 phytium 命中里，对照香山已在 mainline，差异不在国籍而在养育策略。历史的判决不是"LLVM 会不会被颠覆"，而是"它会以哪种先例的方式退场——GCC 式退守保护市场（高概率）、还是被 MLIR 全栈替换（中高概率）、还是被 Mojo/AI 突变打断（低概率但不可忽视）。而真正能改写 30 年规律的，只有历史学家最无力预测的东西——一次范式转移窗口。**
