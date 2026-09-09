# 领域资源库（LLVM Expert 共享通用资源）

> **目的**：避免 18 个 Expert 各自重复铺陈通用资源（顶会/工具/教材/标准/网络社区）。这些跨视角共享的资源集中在此，各 Expert 引用本文件 + 只写**本视角专属**内容。
>
> **采集与刷新**：初版 2026-07-07。本文档是飞腾项目 `../体系结构实验/领域资源库.md`（`../体系结构实验/领域资源库.md`） 的 LLVM 专属补丁，**通用计算机体系结构资源（教材/顶会/分析机构）请直接引用飞腾项目资源库**，本文件只写 LLVM 专属。
>
> **可信度标记**：`[官网]`官方一手 · `[报道]`权威媒体 · `[社区]`中文社区/公众号 · `[BBS]`技术论坛 · `[B站]`视频 · `[豆瓣]`书评/评分 · `[GitHub]`开源项目 · `[Discourse]`LLVM 论坛 · `[HN/Reddit]`英文社区 · `[实测]`本项目实测 · `[推测-依据]`基于公开信息推断。所有外部链接均为公开网络资源，访问日期：2026-07-07。
> **质量等级**：⭐ 必读（奠基性）/ 🔥 进阶（深度）/ 📎 参考（按需查阅）。

---

## 0. 资源地图速览（一页看全）

| 维度 | 最高优先级入口 | 一句话定位 |
|------|--------------|----------|
| 圣经教材 | 龙书（Aho 2nd）/ Engineering a Compiler (Cooper 3rd) | 编译原理双璧 |
| LLVM 专属书 | LLVM 编译器实战教程（Lopes & Auler）/ 深入理解 LLVM：代码生成（彭成寒） | LLVM 入门 + 后端深度 |
| 中文入门 | Evian-Zhang LLVM IR 入门指南 / 小彭老师 LLVM | GitHub 高 star 中文教程 |
| 中文视频 | VectorizeOrz C++&LLVM Tutorial / 先进编译实验室 MLIR | B 站系统教程 |
| 官方一手 | llvm.org / LLVM Discourse / LLVM Doxygen | 三大官方入口 |
| 创始人 | Chris Lattner [@clattner_llvm](https://twitter.com/clattner_llvm) / [nondot.org/sabre](http://nondot.org/sabre/) | LLVM/Clang/Swift/Mojo 之父 |
| 英文社区 | LLVM Discourse / r/LLVM / Discord / Hacker News | 四大讨论阵地 |
| 编译顶会 | PLDI/POPL/CC/CGO/PPoPP | 编译器研究顶会 |
| LLVM 自办会议 | US LLVM Dev Mtg / EuroLLVM / LLVM Dev Tokyo | 每年三场官方会 |
| 在线工具 | Compiler Explorer (godbolt.org) | 在线看汇编必备 |
| AI 编译器 | StableHLO / IREE / MLIR / Mojo | 异构/AI 编译未来 |
| 飞腾专属 | PhyCC / PhyGCC / 飞腾开发者平台 | 飞腾 LLVM 工程实证 |

---

## 1. 编译器顶会地图（投稿 / 跟进前沿）

| 会议 | 全称 | 领域偏好 | 备注 |
|------|------|---------|------|
| **PLDI** | Programming Language Design and Implementation | 编译器/编程语言实现顶会（SIGPLAN） | 录用率 ~20% |
| **POPL** | Principles of Programming Languages | 编程语言理论（SIGPLAN） | 偏理论 |
| **CC** | Compiler Construction | 编译构造（SIGPLAN） | 实操性强 |
| **CGO** | Code Generation and Optimization | 代码生成与优化 | LLVM 后端论文常出没 |
| **PPoPP** | Principles and Practice of Parallel Programming | 并行编程 | LLVM auto-vec/OpenMP |
| **LCTES** | Languages, Compilers, Tools for Embedded Systems | 嵌入式编译 | 飞腾嵌入式相关 |
| **ASPLOS** | Architectural Support for Programming Languages and OS | 软硬交叉，竞争最烈 | 录用率 ~10% |
| **MLSys** | ML Systems | ML 编译器（XLA/MLIR） | AI 编译器主战场 |
| **SC** | Supercomputing | HPC（Flang/OpenMP） | 飞腾 HPC 命脉 |
| **USENIX ATC** | Annual Technical Conf | 系统/存储 | 含 JIT/runtime |
| **ISCA/MICRO/HPCA** | 体系结构顶会 | 偶有编译-架构协同 | 见飞腾项目资源库 |
| **SIGPLAN SL** | Morgan & Claypool Synthesis Lectures | 编译器专题短篇 | 高质量综述 |

**LLVM 自办会议（最重要）**：
- **US LLVM Developers' Meeting**（每年秋，Cupertino/San Jose）—— 演讲视频/PDF 必看
- **EuroLLVM**（每年春，欧洲轮换）—— 欧洲开发者会
- **LLVM Dev Meeting Tokyo**（2025-06 已办，Chris Lattner keynote）[官方](https://llvm.org/devmtg/2025-06/slides/keynote/lattner-keynote.pdf)

**CFP/前沿跟踪**：各会议官网 + LLVM Discourse + [LLVM Weekly](https://llvmweekly.org/)（Alex Denner 编辑的周报）。

---

## 2. 通用工具栈（开发/调试/分析/形式化）

| 类别 | 工具 | 用途 | 备注 |
|------|------|------|------|
| **核心 bin 工具** | `opt` `llc` `lli` `llvm-as` `llvm-dis` `llvm-link` `llvm-ar` `llvm-nm` `llvm-objdump` `llvm-readelf` | LLVM 工具链全家桶 | 替代 GNU binutils |
| **Pass 开发** | `opt -passes=` `opt -load-pass-plugin=` `opt -print-passes` | Pass 编写/加载/查看 | New PM 用 `-passes=` |
| **代码生成** | `llc -march= -mcpu= -print-after-all` `llvm-mca` | 后端调试、调度分析 | `llvm-mca` 静态调度 |
| **测试框架** | `FileCheck` `lit` `llvm-lit` | LLVM 测试基础设施 | regression test 必备 |
| **调试** | `bugpoint` `llvm-reduce` | 自动 bug 最小化 | miscompilation 必用 |
| **性能分析** | `llvm-profdata` `llvm-cov` `llvm-profgen` | PGO、代码覆盖 | ThinLTO 配套 |
| **在线工具** | [Compiler Explorer (godbolt.org)](https://godbolt.org/) | 在线对比多编译器/多版本汇编 | ⭐ 必备 |
| **形式化验证** | [Alive2](https://github.com/AliveToolkit/alive2) | 验证 LLVM Pass 正确性 | Nuno Lopes 团队 |
| **教学样板** | [llvm-tutor](https://github.com/banach-space/llvm-tutor) | 现代 Pass 教程（HelloWorld/DominatorTree 等） | Banach-Space 维护 |
| **可视化** | `opt -view-cfg` `opt -view-dom` | 控制流图、支配树可视化 | graphviz 出图 |

---

## 3. 经典教材与论文库（含豆瓣评分）

### 3.1 ⭐ 必读：编译原理圣经

| 教材 | 作者 | 版本 | 豆瓣 | 一句话定位 |
|------|------|------|------|----------|
| **Compilers: Principles, Techniques, and Tools (龙书)** | Aho, Lam, Sethi, Ullman | 2nd (2006) | [9.x](https://book.douban.com/subject/5409835/) 公认 | 编译原理圣经，所有编译器工程师必读 |
| **Engineering a Compiler** | Cooper & Torczon | 3rd (2022, MK) | — | 现代 Pass Pipeline 设计的标准教材 |
| **Computer Systems: A Programmer's Perspective (CSAPP)** | Bryant & O'Hallaron | 3rd (2015) | 9.8 | CMU 15-213 教材，连接软硬 |
| **Advanced Compiler Design and Implementation (鲸书)** | Muchnick | 1997, MK | — | 后端优化（调度、RegAlloc）权威 |

### 3.2 ⭐ 必读：LLVM 专属

| 教材 | 作者/译者 | 版本 | 豆瓣 | 一句话定位 |
|------|---------|------|------|----------|
| **LLVM 编译器实战教程**（*Getting Started with LLVM Core Libraries*） | Bruno Cardoso Lopes & Rafael Auler / 过敏意 冷静文 译 | 机械工业 2019 | [6.5](https://book.douban.com/subject/34802579/)（21 人评价） | LLVM 入门唯一中译本；评分偏低但仍是首选 |
| **深入理解 LLVM：代码生成** | 彭成寒 / 李灵 / 戴贤泽 / 王志磊 / 俞佳嘉 | 机械工业 2024-9 | [豆瓣](https://book.douban.com/subject/37078652/) 评价人数不足 | "近些年最详细、最准确的编译器原理和实现图书"；以 LLVM 15 为基线讲后端 |
| **LLVM 编译器原理与实践** | 吴建明 / 吴一昊 | 机械工业 2024-10 | [豆瓣](https://book.douban.com/subject/37107379/) 差评 | ⚠️ 豆瓣有"避雷吴建明"评论，谨慎 |
| **LLVM Cookbook** | Mayur Pandey | 2015, Packt | — | 老但实操 |
| **Learn LLVM 17** | xiaoweiChen 译 | [GitHub](https://github.com/xiaoweiChen/Learn-LLVM-17) | — | 中文译本，LLVM 17 |

### 3.3 🔥 进阶：编译优化与 IR 设计

| 教材 | 作者 | 豆瓣 | 一句话定位 |
|------|------|------|----------|
| **Modern Compiler Implementation in C (虎书)** | Andrew W. Appel | [8.4 人邮 2006 版](https://book.douban.com/subject/1806974/) / [8.9 图灵版](https://book.douban.com/subject/30191414/) | 虎书 C 版，编译器实现三语言对照（C/ML/Java） |
| **Advanced Compiler Design and Implementation (鲸书)** | Steven S. Muchnick | [8.8 (51 人评价)](https://www.douban.com/doulist/47594/) | 鲸书，编译器后端优化权威，适合研究生 |
| **Optimizing Compilers for Modern Architectures** | Allen & Kennedy | — | 循环变换、依赖分析奠基（2001, MK） |
| **SSA Book**（*Static Single Assignment Book*） | INRIA | — | [ssabook.gforge.inria.fr](http://ssabook.gforge.inria.fr/) SSA 形式权威在线书 |
| **Modern Processor Design** | Shen & Lipasti | — | 2013 重印，指令级并行工程圣经 |
| **Performance Analysis and Tuning on Modern CPUs** | Denis Bakhvalov | — | 2020，现代乱序 CPU 性能调优 |
| **Learn LLVM 12**（中文译本） | Kai Nacke / xiaoweiChen 译 | [2021 书评](https://book.douban.com/review/13878106/) | LLVM Cookbook 第 12 版中译，PDF 下载 |

### 3.3.1 编译原理三大经典对照（豆瓣 [书单](https://www.douban.com/doulist/47594/)）

| 俗名 | 英文名 | 作者 | 中文译名 | 豆瓣 | 定位 |
|------|--------|------|---------|:----:|------|
| **龙书** | Compilers: Principles, Techniques, and Tools | Aho, Lam, Sethi, Ullman | 编译原理（机械工业） | 9.4 | 入门+核心 |
| **虎书** | Modern Compiler Implementation in C | Andrew W. Appel | 现代编译原理（人邮/图灵） | 8.4-8.9 | 实现导向 |
| **鲸书** | Advanced Compiler Design and Implementation | Steven S. Muchnick | 高级编译器设计与实现（机械工业） | 8.8-8.9 | 后端优化研究生 |

### 3.4 ⭐ 必读：免费年度更新讲义

| 讲义 | 作者 | 链接 | 一句话定位 |
|------|------|------|----------|
| **CMU 15-411 Compiler Design** | CMU | [cs.cmu.edu/1511](https://www.cs.cmu.edu/~janh/courses/411/) | 编译器设计名课，LLVM 实战 |
| **MIT 6.035 Computer Language Engineering** | MIT | [6.035 web](https://6350.csail.mit.edu/) | Sussman/Harold，老牌编译课 |
| **Cornell CS 6120: Advanced Compilers** | Adrian Sampson (Cornell) | [cs.cornell.edu/courses/cs6120](https://www.cs.cornell.edu/courses/cs6120/2020fa/) | ⭐ 现代编译器课，全部视频开源，用 LLVM |
| **LLVM Kaleidoscope Tutorial**（官方） | Chris Lattner | [llvm.org/docs/tutorial](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/index.html) | 从零写编译器的经典教程 |

### 3.5 经典论文谱系（溯源法素材）

```
Cytron 1991 (SSA 构造 dominance frontier)
   ↓
Chaitin 1981 (图着色 RegAlloc) → Briggs 1994 (optimistic coloring)
   ↓
Poletto & Sarkar 1999 (Linear Scan RegAlloc)
   ↓
Lattner & Adve 2004 CGO (LLVM 奠基论文)
   ↓
Larsen & Amarasinghe 2000 (SLP 向量化)
   ↓
Allen & Kennedy 2001 (循环变换 + 多面体) → Grosser 2012 (Polly)
   ↓
Lattner et al 2021 (MLIR: Scaling Compiler Infrastructure)
   ↓
Lopes et al 2022 (Alive2: Verifying LLVM Passes)
   ↓
2024-2026 (StableHLO / IREE / Mojo / Cranelift)
```

### 3.6 论文检索

| 资源 | 链接 | 一句话定位 |
|------|------|----------|
| **DBLP** | [dblp.org](https://dblp.org/) | 任意公司/作者论文可复核 |
| **CSrankings.org** | [csrankings.org](https://csrankings.org/) | 按机构/领域（含 PL）检索论文 |
| **The Morning Paper** (停更) | blog.acolyer.org | 经典论文导读，每天 1 篇 |
| **Papers We Love** | paperswelove.org | 经典论文社区导读 |
| **AK @_akhaliq** | Twitter/X | 每日 arXiv 速递（偏 ML，含 MLIR/XLA） |
| **arXiv cs.PL/cs.LG** | arxiv.org/list/cs.PL/recent | 编译器/PL 每日 |
| **SIGPLAN Blog** | [sigplan.org/Blog](https://sigplan.blog/) | PL 社区综述 |

---

## 4. 标准与官方文档索引

| 领域 | 标准/文档 | 用途 |
|------|----------|------|
| **LLVM IR** | [LLVM Language Reference Manual](https://llvm.org/docs/LangRef.html) | IR 指令集权威（必读） |
| **LLVM Pass** | [Writing an LLVM Pass (legacy)](https://llvm.org/docs/WritingAnLLVMPass.html) / [New PM](https://llvm.org/docs/WritingAnLLVMNewPMPass.html) | Pass 编写 |
| **Pass Manager** | [New Pass Manager](https://llvm.org/docs/NewPassManager.html) | New PM 文档 |
| **后端开发** | [Writing an LLVM Backend](https://llvm.org/docs/WritingAnLLVMBackend.html) / [TableGen](https://llvm.org/docs/TableGen/index.html) | 后端 .td 描述 |
| **代码生成** | [Code Generator](https://llvm.org/docs/CodeGenerator.html) | SelectionDAG/GlobalISel |
| **API 参考** | [LLVM Doxygen](https://llvm.org/doxygen/) | C++ API 全文档 |
| **Getting Started** | [Getting Started with LLVM](https://llvm.org/docs/GettingStarted.html) | 编译/贡献 |
| **Developer Policy** | [llvm.org/docs/DeveloperPolicy](https://llvm.org/docs/DeveloperPolicy.html) | 贡献规范 |
| **C++ 标准** | ISO C++ Committee / [open-std.org](http://www.open-std.org/jtc1/sc22/wg21/) | libcxx 实现 |
| **DWARF** | [dwarfstd.org](http://dwarfstd.org/) | LLDB 调试信息标准 |
| **AArch64 ARM ARM** | DDI 0487（飞腾项目资源库 §4） | AArch64 后端必读 |
| **RISC-V** | [riscv.org/technical/specifications](https://riscv.org/technical/specifications/) | RISC-V 后端必读 |

---

## 5. 各 Expert 引用规范

写到上述通用资源时：
> **正确**："本视角的代码生成讨论用 `llc -print-after-all` 调试（见 [`领域资源库_LLVM.md`](./领域资源库_LLVM.md) §2），本视角补充 SelectionDAG Legalize 的 AArch64 实战……"
>
> **禁止**：在 18 个 Expert 里各自重新铺一份顶会/工具/教材库——那是新的重复。通用资源**只在此定义一次**。

**引用格式建议**：
- 文中：「见 [`领域资源库_LLVM.md`](./领域资源库_LLVM.md) §X.Y」
- 末尾参考文献：`[LLVM-资源库-§X.Y] 资源名. 链接. 访问 2026-07-07.`

---

## 6. 📚 中文网络资源（社区 / 知乎 / B 站 / CSDN / 博客园 / 公众号）

### 6.1 ⭐ GitHub 高 star 中文教程

| 资源 | 链接 | 一句话定位 | 可信度 |
|------|------|----------|:----:|
| **Evian-Zhang/llvm-ir-tutorial** | [github.com/Evian-Zhang/llvm-ir-tutorial](https://github.com/Evian-Zhang/llvm-ir-tutorial) | ⭐⭐⭐⭐⭐ LLVM IR 入门指南（中文，接近 1000 star，LLVM 16） | [GitHub] |
| **小彭老师带你学 LLVM** | [parallel101.github.io/cppguidebook/llvm_intro](https://parallel101.github.io/cppguidebook/llvm_intro/) | ⭐⭐⭐⭐⭐ parallel101（小彭大典），C++ 名师小彭老师 | [社区] |
| **urlyy/llvm-new-pass-tutor** | [github.com/urlyy/llvm-new-pass-tutor](https://github.com/urlyy/llvm-new-pass-tutor) | ⭐⭐⭐⭐ 基于 LLVM-18 New PM Pass 教程（含 B 站视频 BV1Bf3neVEnN） | [GitHub] |
| **Learn LLVM 17** | [github.com/xiaoweiChen/Learn-LLVM-17](https://github.com/xiaoweiChen/Learn-LLVM-17) | ⭐⭐⭐ xiaoweiChen 中文译本 | [GitHub] |
| **LLVM Kaleidoscope 中文** | [llvm-tutorial-cn.readthedocs.io](https://llvm-tutorial-cn.readthedocs.io/) | ⭐⭐⭐⭐ 连城译，Chris Lattner 原著中译 | [社区] |
| **Getting Started with LLVM Core Libraries 中文版** | [getting-started-with-llvm-core-libraries-zh-cn.readthedocs.io](https://getting-started-with-llvm-core-libraries-zh-cn.readthedocs.io/) | ⭐⭐⭐ 教材中译 | [社区] |

### 6.2 ⭐ B 站视频课程

| 课程 | UP 主 / 链接 | 一句话定位 | 可信度 |
|------|------------|----------|:----:|
| **C++&LLVM 入门项目（手把手 LLVM Tutorial）** | [VectorizeOrz BV1UQU7BHEs2](https://www.bilibili.com/video/BV1UQU7BHEs2/) | ⭐⭐⭐⭐⭐ 7 集 LLVM Tutorial 全套（2025-11 起更） | [B站] |
| **LLVM 编译器入门（三）：IR 优化** | [先进编译实验室 BV1fX4y1x79Y](https://www.bilibili.com/video/BV1fX4y1x79Y/) | ⭐⭐⭐⭐ 高校实验室 | [B站] |
| **人工智能编译器 MLIR 官方入门教程讲解** | [先进编译实验室 BV1Hd4y1U7mb](https://www.bilibili.com/video/BV1Hd4y1U7mb/) | ⭐⭐⭐⭐ 3.1 万播放，MLIR 入门首选 | [B站] |
| **如何使用 LLVM 和 MLIR 来构建一个编译器（全 20 集）** | [ZOMI酱 BV1CG4y1V7Dn](https://www.bilibili.com/video/BV1CG4y1V7Dn/) | ⭐⭐⭐⭐ 4.4 万播放 | [B站] |
| **手把手带你入门实践 LLVM** | iiicp（B 站专栏） | ⭐⭐⭐⭐ 2024 录制，LLVM 17，零基础 | [B站] |
| **【硬核开课】从零带你写出自己的编程语言和编译器** | [硬核子牙 BV1C3gSzsEUn](https://www.bilibili.com/video/BV1C3gSzsEUn/) | ⭐⭐⭐ 偏付费课程 | [B站] |
| **编译原理 — 中科大**（B 站搜） | 中科大 | ⭐⭐⭐⭐ 高校公开课 | [B站] |

### 6.3 ⭐ CSDN 专栏（精选，质量参差需甄别）

| 专栏 / 文章 | 作者 | 一句话定位 | 可信度 |
|-----------|------|----------|:----:|
| **LLVM 学习入门（Kaleidoscope）系列** | [m0_43400575 专栏](https://blog.csdn.net/m0_43400575/category_11971122.html) | ⭐⭐⭐ 8 篇 LLVM Kaleidoscope 中文笔记 | [社区] |
| **LLVM 系列**（写 FunctionPass 等 20+ 篇） | Zhanglin_Wu | ⭐⭐⭐⭐ 实战 Pass 开发 | [社区] |
| **LLVM11 实战教程：用最简单的方式运行自定义 Pass** | [QingYun2077](https://blog.csdn.net/QingYun2077/article/details/143599148) | ⭐⭐⭐ 最小可运行示例 | [社区] |
| **LLVM Pass 开发实战：从 IR 遍历到指令级优化** | [2301_81410839](https://blog.csdn.net/2301_81410839/article/details/162446069) | ⭐⭐⭐ 2026-06 最新 | [社区] |
| **LLVM 入门教程之 Pass 编写** | [Yuuoniy](https://blog.yuuoniy.cn/posts/llvm-pass-1/) | ⭐⭐⭐⭐ 经典老文 | [社区] |
| **从零开始的 LLVM+Clang（下载、配置到第一个 Pass）** | [qq_41048815](https://blog.csdn.net/qq_41048815/article/details/108556465) | ⭐⭐⭐ Ubuntu 编译 LLVM 实操 | [社区] |
| **llvm19.0 源码树外编译 Pass（New PM）** | [weixin_43890959](https://blog.csdn.net/weixin_43890959/article/details/144483164) | ⭐⭐⭐⭐ LLVM 19 最新 | [社区] |

### 6.4 ⭐ 博客园（深度原创）

| 资源 | 作者 / 链接 | 一句话定位 | 可信度 |
|------|-----------|----------|:----:|
| **LLVM 和 MLIR 编译器构建笔记（全）** | [绝不原创的飞龙（ApacheCN）](https://www.cnblogs.com/apachecn/p/19789972) | ⭐⭐⭐⭐⭐ 长篇翻译整理，含 Serene 语言视频系列 | [社区] |
| **从零教你写一个 LLVM Pass** | [BobHuang](https://www.cnblogs.com/BobHuang/p/17640378.html) | ⭐⭐⭐⭐ LLVM 15.0.7 实战（AMDGPUResourceUsageAnalysis 案例） | [社区] |
| **toolchain » LLVM** | [antkillerfarm（沈渊）](https://antkillerfarm.github.io/toolchain/2024/03/12/LLVM.html) | ⭐⭐⭐⭐ 长期更新的 LLVM 笔记（含 ADT/TableGen/FileCheck/Pass） | [社区] |

### 6.5 ⭐ 个人博客

| 博客 | 作者 / 链接 | 一句话定位 | 可信度 |
|------|-----------|----------|:----:|
| **LLVM 简明教程** | [Gality（藏器于身）](https://gality.cn/llvm/llvm-tutorial/) | ⭐⭐⭐⭐ 新手视角笔记 | [社区] |
| **LeadroyaL — LLVM New PM 适配** | [leadroyal.cn/p/221](https://leadroyal.cn/p/221/) | ⭐⭐⭐⭐ iOS 越狱圈 LLVM Pass 实战 | [社区] |
| **小彭大典** | [parallel101.github.io](https://parallel101.github.io/) | ⭐⭐⭐⭐⭐ 小彭老师全栈 C++ 教程 | [社区] |
| **Yuuoniy blog** | [blog.yuuoniy.cn](https://blog.yuuoniy.cn/) | ⭐⭐⭐⭐ LLVM/JVM 编译器学习笔记 | [社区] |
| **qfrost** | [qfrost.com/posts/llvm](http://www.qfrost.com/posts/llvm/) | ⭐⭐⭐⭐ Windows 下优雅使用 LLVM Pass | [社区] |

### 6.6 ⭐ 洛谷 / SegmentFault / 其他

| 资源 | 链接 | 一句话定位 | 可信度 |
|------|------|----------|:----:|
| **LLVM 从入门到迷惑** | [洛谷 zi2ven](https://www.luogu.com.cn/article/tl31i8gc) | ⭐⭐⭐⭐ 2025-02，LLVM 19.1.6 全栈 | [社区] |
| **基于飞腾 CPU 的高性能编译器 PhyGCC 安装及配置说明** | [SegmentFault](https://segmentfault.com/a/1190000044680095) | ⭐⭐⭐⭐ 飞腾 PhyGCC 10.3.1 实操（飞腾专属） | [社区] |
| **从零开始的 LLVM 中文教程** | [GitCode 博客](https://blog.gitcode.com/eb87f4924ccef473f89efa8c1db9a540.html) | ⭐⭐⭐ 中文教程索引 | [社区] |

### 6.7 ⭐ CSDN 老专栏（编译器圈资深博主，2018-2024 持续更新）

| 专栏 | 作者 | 一句话定位 | 可信度 |
|------|------|----------|:----:|
| **LLVM 每日谈** | [史宁宁 snsn1984](https://blog.csdn.net/snsn1984/category_9261370.html) | ⭐⭐⭐⭐⭐ HelloGCC 社区活跃成员，38+ 篇 LLVM 持续更新（含 LLVM 博客专栏汇总） | [社区] |
| **LLVM_Yurii.Huang** | [Yurii.Huang](https://blog.csdn.net/qq_24423085/category_9313711.html) | ⭐⭐⭐⭐ libClang/前端语法解析/AST 深度教程 | [社区] |
| **LLVM_翔哥@LLVM** | [翔哥](https://blog.csdn.net/zhangxiang0503/category_11126963.html) | ⭐⭐⭐⭐ 后端开发（PGO/红区/物理寄存器/LLD COFF/ELF） | [社区] |
| **编译器_zhugl0** | [zhugl0](https://blog.csdn.net/qq_36287943/category_9614491.html) | ⭐⭐⭐⭐ GCC/ICC/AOCC/LLVM 多编译器对比 + GIMPLE Pass | [社区] |
| **LLVM Cpu0 新后端系列** | [lml435035844](https://blog.csdn.net/lml435035844/article/details/139560889) | ⭐⭐⭐⭐ 陳鍾樞《Tutorial: Creating an LLVM Backend for the Cpu0》中文笔记 | [社区] |

### 6.8 ⭐ LLVM 后端开发专属教程（Cpu0 + 真实后端）

| 资源 | 作者 / 链接 | 一句话定位 | 可信度 |
|------|-----------|----------|:----:|
| **Tutorial: Creating an LLVM Backend for the Cpu0 Architecture** | 陳鍾樞（台湾） | ⭐⭐⭐⭐⭐ 写新 LLVM 后端的经典教程（中文笔记见 §6.7 lml435035844） | [社区] |
| **P2Tree/LLVM_for_cpu0** | [github.com/P2Tree/LLVM_for_cpu0](https://github.com/P2Tree/LLVM_for_cpu0) | ⭐⭐⭐⭐ Cpu0 教程基于 LLVM 8/9 的复现，知乎专栏同步 | [GitHub] |
| **jourluohua 转换无极限（博客园）** | [cnblogs.com/jourluohua](https://www.cnblogs.com/jourluohua) | ⭐⭐⭐⭐ 异构编译器 + 编程，LLVM Function/BasicBlock/PHINode/Pass 系列 | [社区] |

### 6.9 ⭐ 中文播客 + 极客时间专栏（深度长内容）

| 资源 | 主讲 / 链接 | 一句话定位 | 可信度 |
|------|-----------|----------|:----:|
| **RustTalk 播客 008：与小福聊聊编译器那些事** | [Jiacai Liu / 韦清福](https://rusttalk.github.io/podcast/008/) | ⭐⭐⭐⭐⭐ 字节 JVM → NVIDIA 编译器后端，2 小时深度访谈 | [社区] |
| **极客时间《编译原理之美》（第一季）** | [宫文学（北京原点代码 CEO）](https://time.geekbang.org/column/intro/219) | ⭐⭐⭐⭐ 付费 56 讲，前端+后端+实战（含 LLVM） | [社区] |
| **极客时间《编译原理实战课》（第二季）** | [宫文学](https://time.geekbang.org/column/article/243248) | ⭐⭐⭐⭐⭐ 付费，解析 Java/Graal/Python/Julia/Go/华为方舟/V8 等真实编译器源码 | [社区] |
| **PlayWithCompiler**（极客时间课程练习） | [github.com/leizongmin/PlayWithCompiler](https://github.com/leizongmin/PlayWithCompiler) | ⭐⭐⭐ 宫文学课程配套代码 | [GitHub] |

### 6.10 微信公众号（编译器圈）

| 公众号 | 定位 | 备注 |
|--------|------|------|
| **飞腾信息技术有限公司**（官方） | PhyCC/PhyGCC 第一手 | 必关注（飞腾项目） |
| **操作系统研发** / **编译器研发**（飞腾） | 飞腾技术专栏 | — |
| **AI 编译** / **oneflow** | AI 编译器（MLIR/XLA） | ⭐⭐⭐⭐ |
| **bilibili 先进编译实验室** | MLIR/LLVM 视频 | ⭐⭐⭐⭐ |
| **机器之心** / **半导体行业观察** | 综合 AI + 芯片 | 见飞腾项目资源库 |

---

## 7. 🌐 英文社区 / 博客 / 创始人

### 7.1 ⭐ LLVM 官方一手

| 资源 | 链接 | 一句话定位 |
|------|------|----------|
| **LLVM Project 主页** | [llvm.org](https://llvm.org/) | 官方入口 |
| **LLVM GitHub Monorepo** | [github.com/llvm/llvm-project](https://github.com/llvm/llvm-project) | 22 子项目源码 |
| **LLVM Doxygen C++ API** | [llvm.org/doxygen](https://llvm.org/doxygen/) | C++ 类/函数权威文档 |
| **LLVM Discussion Forums (Discourse)** | [discourse.llvm.org](https://discourse.llvm.org/) | ⭐⭐⭐⭐⭐ 主讨论区（2022 起取代 mailing list） |
| **LLVM Discord** | [discord.gg/xS7Z362](https://discord.gg/xS7Z362) | 实时聊天，按子项目分频道 |
| **LLVM Mailing List Archives** | [lists.llvm.org/pipermail](https://lists.llvm.org/pipermail/) | 2022 前历史归档 |
| **LLVM Weekly** | [llvmweekly.org](https://llvmweekly.org/) | ⭐⭐⭐⭐⭐ Alex Denner 周报（必订） |
| **LLVM Bugzilla**（旧） / GitHub Issues | github.com/llvm/llvm-project/issues | bug 追踪 |
| **LLVM Blog** | [blog.llvm.org](https://blog.llvm.org/) | 官方博客 |
| **LLVM Foundation** | [foundation.llvm.org](https://foundation.llvm.org/) | 501(c)(3) 非营利 |

### 7.2 ⭐ LLVM 自办活动

| 活动 | 频率 | 链接 | 价值 |
|------|------|------|:----:|
| **US LLVM Developers' Meeting** | 每年秋 | [llvm.org/devmtg](https://llvm.org/devmtg/) | ⭐⭐⭐⭐⭐ 演讲/PDF 必看 |
| **EuroLLVM** | 每年春 | 同上 | ⭐⭐⭐⭐ |
| **LLVM Dev Mtg Tokyo** | 不定期 | [2025-06](https://llvm.org/devmtg/2025-06/slides/keynote/lattner-keynote.pdf) | ⭐⭐⭐⭐ |
| **Women in Compilers and Tools (WiCT)** | 年度 | WiCT 社区 | ⭐⭐⭐ |
| **Google Summer of Code (LLVM)** | 每年 | [llvm.org/GSoC](https://llvm.org/gsoc/) | ⭐⭐⭐ 学生入门 |

### 7.3 ⭐ 创始人 / 关键贡献者

| 人物 | 链接 | 一句话定位 |
|------|------|----------|
| **Chris Lattner**（LLVM/Clang/Swift/Mojo 之父） | [nondot.org/sabre](http://www.nondot.org/sabre/) / [LinkedIn](https://linkedin.com/in/chris-lattner-5664498a) / [GitHub @lattner](https://github.com/lattner) / [@clattner_llvm](https://twitter.com/clattner_llvm) | ⭐⭐⭐⭐⭐ LLVM 单一最大贡献者，现 Modular CEO |
| **Chris Lattner Lex Fridman 访谈** | [Lex #21 (2019)](https://lexfridman.com/chris-lattner/) / [Lex #381 (2023)](https://www.youtube.com/watch?v=pdJQ8iVTwj8) / [The PrimeTime 2024](https://www.youtube.com/watch?v=ovYbgbrQ-v8) | ⭐⭐⭐⭐⭐ LLVM/Swift/Mojo 创业史 |
| **Chris Lattner SC21 Fireside Chat** | [hpcwire.com](https://www.hpcwire.com/2021/12/27/lessons-from-llvm-an-sc21-fireside-chat-with-chris-lattner/) | ⭐⭐⭐⭐ LLVM 历史回顾 |
| **Chris Lattner Pragmatic Engineer 访谈** | [newsletter.pragmaticengineer.com](https://newsletter.pragmaticengineer.com/p/from-swift-to-mojo-and-high-performance) | ⭐⭐⭐⭐ 2025-11 Swift/Mojo/编译器 |
| **Vikram Adve**（LLVM 共同创建者，Lattner 博导） | [cs.illinois.edu/~vadve](https://cs.illinois.edu/people/faculty/vikram-s-adve) | Lattner 博士导师 |
| **Tanya Lattner**（LLVM Foundation 主席，前 Apple） | [foundation.llvm.org](https://foundation.llvm.org/) | LLVM Foundation 治理 |

### 7.4 ⭐ 大众社区

| 平台 | 链接 | 一句话定位 |
|------|------|----------|
| **Reddit r/LLVM** | [reddit.com/r/LLVM](https://www.reddit.com/r/LLVM/) | ⭐⭐⭐⭐ 大众讨论 |
| **Hacker News** | [news.ycombinator.com](https://news.ycombinator.com/) | ⭐⭐⭐⭐⭐ 重磅编译器新闻首发讨论 |
| **Stack Overflow [llvm] [clang] [llvm-llvm]** | stackoverflow.com | ⭐⭐⭐⭐ 实操 Q&A |

**HN 经典讨论（必读）**：
- ["How to learn compilers: LLVM Edition"](https://news.ycombinator.com/item?id=29112482) — 221 points，最佳入门路线图
- ["Ask HN: How to learn LLVM and why?"](https://news.ycombinator.com/item?id=11582943)
- ["A Gentle Introduction to LLVM IR" (mcyoung.xyz)](https://news.ycombinator.com/item?id=36964327)
- ["LLVM: The bad parts"](https://news.ycombinator.com/item?id=46588837)
- ["Rust: The New LLVM"](https://news.ycombinator.com/item?id=12147843)
- ["i could easily google it but, what's LLVM?"](https://news.ycombinator.com/item?id=35809261)
- ["How is LLVM tested?"](https://news.ycombinator.com/item?id=11359414) — LLVM 测试基础设施讨论

### 7.5 ⭐ 个人权威博客

| 博客 | 作者 / 链接 | 一句话定位 |
|------|-----------|----------|
| **LLVM Project Blog** | [blog.llvm.org](https://blog.llvm.org/) | 官方博客 |
| **Alex Denisov**（lowlevelbits） | [lowlevelbits.org](https://lowlevelbits.org/) | ⭐⭐⭐⭐⭐ LLVM 深度教程 |
| **Marc-André Cournoyer (mcyoung)** | [mcyoung.xyz](https://mcyoung.xyz/) | "A Gentle Introduction to LLVM IR" 作者 |
| **Eli Bendersky** | [eli.thegreenplace.net](https://eli.thegreenplace.net/) | ⭐⭐⭐⭐ 编译器/Go 长期博客 |
| **Bruce Hoult**（RISC-V / LLVM） | News/RWC 社区活跃 | — |
| **Nuno Lopes**（Alive2） | [web.ist.utl.pt/nuno-lopes](http://web.ist.utl.pt/~nuno-lopes/) | ⭐⭐⭐⭐ LLVM Pass 形式化验证 |
| **Adrian Sampson**（Cornell CS 6120） | [www.cs.cornell.edu/~asampson](https://www.cs.cornell.edu/~asampson/) | ⭐⭐⭐⭐ 现代编译器课 |

### 7.6 学术圈博客 / 协会

| 平台 | 链接 | 一句话定位 |
|------|------|----------|
| **ACM SIGPLAN Blog** | [sigplan.org/Blog](https://sigplan.blog/) | PL 社区综述 |
| **ACM SIGPLAN** | [sigplan.org](https://www.sigplan.org/) | PL 顶会组织 |
| **ACM POPL** | [popl.host](https://popl.host/) | POPL 顶会 |
| **CACM: The LLVM Compiler Infrastructure**（2026-07） | [cacm.acm.org/.../the-llvm-compiler-infrastructure](https://cacm.acm.org/federal-funding-of-academic-research/the-llvm-compiler-infrastructure/) | ⭐⭐⭐⭐⭐ NSF 资助 LLVM 25 年回顾（Lattner 等撰） |

### 7.7 ⭐ LLVM Discourse 经典讨论（必读，按主题）

| 主题 | 链接 | 一句话定位 |
|------|------|----------|
| **Enabling loop-interchange**（2024-10） | [discourse.llvm.org/t/enabling-loop-interchange/82589](https://discourse.llvm.org/t/enabling-loop-interchange/82589) | ⭐⭐⭐⭐⭐ LLVM Loop 优化 RFC，揭示 LLVM IR 不适合 loop 优化的根本问题 |
| **Writing loop transformations on the right representation**（2020-01） | [discourse.llvm.org/t/.../54110](https://discourse.llvm.org/t/writing-loop-transformations-on-the-right-representation-is-more-productive/54110) | ⭐⭐⭐⭐⭐ Michael Kruse 经典 RFC，Lattner 评论"MLIR 才是 loop 优化的正确抽象" |
| **Best way to implement a fully custom optimization + codegen pipeline using NPM** | [discourse.llvm.org/t/.../86621](https://discourse.llvm.org/t/best-way-to-implement-a-fully-custom-optimization-codegen-pipeline-using-npm/86621) | ⭐⭐⭐⭐ New PM 在 codegen 还没完成的实证（断层 ④） |
| **Automated review with agents: ~30 bugs on 207 PRs**（2026-03） | [discourse.llvm.org/t/.../90093](https://discourse.llvm.org/t/automated-review-with-agents-30-bugs-on-207-prs/90093) | ⭐⭐⭐⭐⭐ AI 代理审查 LLVM PR，每 PR $2，30+ 真 bug | 
| **Building an LLVM cross-compiler** | [discourse.llvm.org/t/.../56881](https://discourse.llvm.org/t/building-an-llvm-cross-compiler/56881) | ⭐⭐⭐⭐ LLVM 交叉编译的鸡生蛋问题（compiler-rt/libc 互依） |
| **RFC: MLIR Project Lighthouse** | [discourse.llvm.org/t/.../86738](https://discourse.llvm.org/t/rfc-mlir-project-lighthouse/86738) | ⭐⭐⭐⭐ MLIR 官方测试集 / ingress-scheduler-egress 框架 |

### 7.8 ⭐ LLVM × AI/LLM 前沿项目（2024-2026 新趋势）

| 项目 | 链接 | 一句话定位 |
|------|------|----------|
| **mlir-opt-repl**（LLVM PR #203796, 2026-06） | [github.com/llvm/llvm-project/pull/203796](https://github.com/llvm/llvm-project/pull/203796) | ⭐⭐⭐⭐⭐ MLIR Pass 流水线交互式 REPL + **MCP server**（Claude Code 集成），AI 辅助编译器开发 |
| **mlirAgent**（UC Berkeley） | [github.com/ucb-bar/mlirAgent](https://github.com/ucb-bar/mlirAgent) | ⭐⭐⭐⭐⭐ LLM 引导的 MLIR/LLVM 优化，binary size -8.78%（匹敌 Magellan/ICML 2025，10× 更少迭代）；"LLM 不能替代编译器 Pass"实证（Gemini 2.5 Pro -11.9%） |
| **Intel graph-compiler** | [github.com/intel/graph-compiler](https://github.com/intel/graph-compiler) | ⭐⭐⭐⭐ Intel MLIR-based DL 编译器，对标 IREE |
| **LLVM Lighthouse Project** | [github.com/llvm/lighthouse](https://github.com/llvm/lighthouse/tree/kb) | ⭐⭐⭐⭐ MLIR 官方 ingress-scheduler-runtime 框架，对标 Clang 之于 LLVM |
| **Torch-MLIR** | [github.com/llvm/torch-mlir](https://github.com/llvm/torch-mlir) | ⭐⭐⭐⭐⭐ PyTorch → MLIR 桥接，1794 star，LLVM 孵化器项目 |

---

## 8. 🎥 视频课程（完整版）

### 8.1 ⭐ 经典英文公开课

| 课程 | 学校 / 讲师 | 链接 | 一句话定位 |
|------|-----------|------|----------|
| **CS 6120: Advanced Compilers** | Adrian Sampson (Cornell) | [cs.cornell.edu/courses/cs6120](https://www.cs.cornell.edu/courses/cs6120/2020fa/) | ⭐⭐⭐⭐⭐ 现代编译器课，全视频开源，用 LLVM |
| **15-411 Compiler Design** | CMU | [cs.cmu.edu/1511](https://www.cs.cmu.edu/~janh/courses/411/) | ⭐⭐⭐⭐⭐ LLVM 实战名课 |
| **6.035 Computer Language Engineering** | MIT | [6350.csail.mit.edu](https://6350.csail.mit.edu/) | ⭐⭐⭐⭐ 老牌编译课 |
| **CS 241: Foundations of Sequential Programs** | UWaterloo | [student.cs.uwaterloo.ca/~cs241](https://student.cs.uwaterloo.ca/~cs241/) | ⭐⭐⭐⭐ 含 LLVM 后端实验 |
| **Stanford CS143: Compilers** | Stanford | [web.stanford.edu/class/cs143](https://web.stanford.edu/class/cs143/) | ⭐⭐⭐⭐ 经典（COOL 语言） |

### 8.2 ⭐ LLVM 官方视频

| 资源 | 链接 | 一句话定位 |
|------|------|----------|
| **LLVM Developer Meeting Videos** | [youtube.com/@LLVMPROJ](https://www.youtube.com/@LLVMPROJ) | ⭐⭐⭐⭐⭐ 官方 YouTube 频道 |
| **LLVM Dev Mtg 历年 PPT** | [llvm.org/devmtg](https://llvm.org/devmtg/) | 演讲 PDF/PPT，部分有视频 |

### 8.3 ⭐ AI 编译器专属（MLIR/StableHLO/IREE/Mojo）

| 资源 | 链接 | 一句话定位 |
|------|------|----------|
| **IREE / MLIR / Linalg tutorial** | [iree.dev/community/blog/2024-01-29-iree-mlir-linalg-tutorial](https://iree.dev/community/blog/2024-01-29-iree-mlir-linalg-tutorial/) | ⭐⭐⭐⭐⭐ IREE 官方 Linalg 教程 |
| **StableHLO Specification** | [openxla.org/stablehlo/spec](https://openxla.org/stablehlo/spec) | ⭐⭐⭐⭐ StableHLO 规范（OpenXLA） |
| **StableHLO 项目** | [openxla.org/stablehlo](https://openxla.org/stablehlo) / [GitHub openxla/stablehlo](https://github.com/openxla/stablehlo) | ⭐⭐⭐⭐ ML 模型可移植层 |
| **MLIR 官方文档** | [mlir.llvm.org](https://mlir.llvm.org/) | ⭐⭐⭐⭐⭐ MLIR 一手 |
| **IREE 项目** | [iree.dev](https://iree.dev/) | ⭐⭐⭐⭐⭐ Google AI 编译器运行时 |
| **torch-mlir** | [github.com/llvm/torch-mlir](https://github.com/llvm/torch-mlir) | ⭐⭐⭐⭐ PyTorch → MLIR |
| **Mojo**（Chris Lattner 新语言） | [modular.com/mojo](https://www.modular.com/mojo) | ⭐⭐⭐⭐⭐ AI 编程语言，Python+性能 |
| **Modular**（Chris Lattner 公司） | [modular.com](https://www.modular.com/) | ⭐⭐⭐⭐⭐ AI 基础设施公司 |

---

## 9. 📊 数据 / 行业报告来源

### 9.1 LLVM 项目状态数据

| 数据 | 来源 | 一句话定位 |
|------|------|----------|
| **LLVM 6 个月 release** | [releases.llvm.org](https://releases.llvm.org/) | 每年 3/9 月新版本 |
| **GitHub commit 统计** | [github.com/llvm/llvm-project/graphs/contributors](https://github.com/llvm/llvm-project/graphs/contributors) | 公司化贡献结构 |
| **LLVM Weekly 历史** | [llvmweekly.org](https://llvmweekly.org/) | 每周 commit 速报 |
| **Open Hub LLVM stats** | [openhub.net/p/llvm](https://www.openhub.net/p/llvm) | 历史代码统计 |
| **LLVM Releases Timeline** | [en.wikipedia.org/wiki/LLVM](https://en.wikipedia.org/wiki/LLVM) | 版本时间线 |

### 9.2 编译器市场/产业

| 来源 | 链接 | 一句话定位 |
|------|------|----------|
| **LLVM Foundation Annual Report** | [foundation.llvm.org](https://foundation.llvm.org/) | 财报/赞助 |
| **RedMonk 编译器圈分析** | redmonk.com | 偶尔深度 |
| **Phoronix 编译器测试** | [phoronix.com/scan.php?page=...](https://www.phoronix.com/) | ⭐⭐⭐⭐ GCC vs Clang 性能对比 |
| **Linaro**（ARM 编译器圈） | [linaro.org](https://www.linaro.org/) | ⭐⭐⭐⭐ ARM 生态 |
| **Agner Fog**（指令吞吐表） | [agner.org/optimize](https://www.agner.org/optimize/) | ⭐⭐⭐⭐⭐ x86/ARM 微架构指令表（飞腾项目也用） |

---

## 10. LLVM 22 子项目专属资源（按 `OpenXiangShan/llvm-project/` 实际目录）

> 本节是 22 子项目的"项目入口 + 官方文档 + 关键社区资源"。5 个"只索引"子项目（libclc / libc / llvm-libgcc / runtimes / cross-project-tests）只写定位，不单独成文。

### 10.1 ⭐ 核心子项目（有独立 Expert）

| 子项目 | 用途 | 官方入口 | 本项目 Expert |
|--------|------|---------|----------|
| **llvm**（core） | IR/Pass/CodeGen/RegAlloc/MC | [llvm.org/docs](https://llvm.org/docs/) | E02/E03/E04/E05/E06/E07 |
| **clang** | C/C++/ObjC 前端 | [clang.llvm.org](https://clang.llvm.org/) / [clang.llvm.org/docs](https://clang.llvm.org/docs/) | E01 |
| **clang-tools-extra** | clang-tidy/clangd/clang-format | 同 clang | 合并 E01 |
| **mlir** | 多级 IR（AI/异构编译） | [mlir.llvm.org](https://mlir.llvm.org/) | E04（融合裂痕断层） |
| **lld** | 链接器 | [lld.llvm.org](https://lld.llvm.org/) | E12 |
| **lldb** | 调试器 | [lldb.llvm.org](https://lldb.llvm.org/) | E13 |
| **compiler-rt** | 运行时/sanitizers | [compiler-rt.llvm.org](https://compiler-rt.llvm.org/) | E14 |
| **libcxx** | C++ 标准库 | [libcxx.llvm.org](https://libcxx.llvm.org/) | E15 |
| **libcxxabi** | C++ ABI | 同 libcxx | E15 |
| **libunwind** | stack unwinder | 同 libcxx | E15 |
| **openmp** | OpenMP runtime | [openmp.llvm.org](https://openmp.llvm.org/) | E15 |
| **flang** + **flang-rt** | Fortran 前端 | [flang.llvm.org](https://flang.llvm.org/) | E16 |
| **bolt** | 后链接二进制优化器 | [github.com/llvm/llvm-project/tree/main/bolt](https://github.com/llvm/llvm-project/tree/main/bolt) | 合并 E12 |
| **orc-rt** | JIT runtime | [github.com/.../orc-rt](https://github.com/llvm/llvm-project/tree/main/orc-rt) | 合并 E14 |
| **polly** | 多面体优化 | [polly.llvm.org](https://polly.llvm.org/) | 合并 E04 |
| **offload** | OpenMP target offload | 同 openmp | 合并 E11 |
| **libsycl**（llvm-libc++-support for SYCL） | SYCL/CUDA | [sycl.tech](https://sycl.tech/) / [intel.github.io/llvm-docs](https://intel.github.io/llvm-docs/) | 合并 E11 |
| **libc** | 实验性 C 运行时 | [libc.llvm.org](https://libc.llvm.org/) | 只索引 |
| **libclc** | OpenCL C | [libclc.llvm.org](https://libclc.llvm.org/) | 只索引 |
| **llvm-libgcc** | GCC 兼容层 | github 同上 | 只索引 |
| **runtimes** | 元构建 | [llvm.org/docs/...runtimes](https://llvm.org/docs/BuildingADistribution.html#runtimes-build) | 只索引 |
| **cross-project-tests** | 跨项目测试 | github 同上 | 只索引 |

### 10.2 ⭐ 5 个"只索引"子项目定位

#### libc（实验性 C 运行库）
- 路径：`OpenXiangShan/llvm-project/libc/`
- 定位：LLVM 实验性 C 标准库实现，目标替代 glibc/musl。**飞腾当前用 glibc**，本项目只索引其存在与路线图，不单独成文。
- 入口：[libc.llvm.org](https://libc.llvm.org/) | [libc-dev mailing list → Discourse Runtimes/C](https://discourse.llvm.org/c/runtimes/libc/22)

#### libclc（OpenCL C 库）
- 路径：`OpenXiangShan/llvm-project/libclc/`
- 定位：OpenCL 1.2/2.0 C 库实现。小众，本项目只索引。
- 入口：[libclc.llvm.org](https://libclc.llvm.org/)

#### llvm-libgcc（GCC 兼容层）
- 路径：`OpenXiangShan/llvm-project/llvm-libgcc/`
- 定位：用 compiler-rt 重新导出 libgcc_s 符号，让 LLVM-only 系统能跑 GCC 编译的二进制。小，本项目只索引。
- 入口：github 同上

#### runtimes（元构建）
- 路径：`OpenXiangShan/llvm-project/runtimes/`
- 定位：libunwind/libcxx/libcxxabi/libc/compiler-rt/libclc 等的元构建系统（runtimes-build），不是学科，是工程。
- 入口：[llvm.org/docs/BuildingADistribution.html#runtimes-build](https://llvm.org/docs/BuildingADistribution.html#runtimes-build)

#### cross-project-tests（跨项目测试）
- 路径：`OpenXiangShan/llvm-project/cross-project-tests/`
- 定位：跨子项目的集成测试套件。非学科。
- 入口：github 同上

---

## 11. 🛡️ 飞腾 / Phytium 专属资源（飞腾 LLVM 工程实证）

### 11.1 飞腾官方编译器（一手）

| 资源 | 链接 | 一句话定位 |
|------|------|----------|
| **飞腾开发者平台 - 编译器** | [phytium.com.cn/developer/36](https://www.phytium.com.cn/developer/36/) | PhyCC 1.0/2.0 + PhyGCC 二进制下载 |
| **PhyCC 2.0 发布页** | [飞腾开发者平台 - 独立软件 36](https://www.phytium.com.cn/developer/independent_software/detail/36/28/) | **"PhyCC 2.0 基于 LLVM 研发"** —— 这是飞腾唯一直接说"基于 LLVM"的官方编译器 [官方] |
| **PhyGCC 10.3.2 发布页** | 同上 | PhyGCC 10.3.2（兼容 GCC，针对 FTC86X 微架构）[官方] |
| **PhyCC 1.0 商业仓库** | [phytium.com.cn/developer/repository/view/?id=320](https://www.phytium.com.cn/developer/repository/view/?id=320) | **"PhyCC 1.0 基于 LLVM 研发"** + 集成高性能 malloc/math 库 [官方] |
| **飞腾招聘 NPU 编译器工程师** | [phytium.com.cn/recruitment](https://www.phytium.com.cn/recruitment/) | JD 明文："1.从事飞腾 NPU 编译器开发工作，**在 llvm 基础上移植一个新的后端**，并支持新的指令集" —— 这是飞腾自研 LLVM 后端的唯一实锤 [官方] |

### 11.2 PhyGCC 安装与配置（社区）

| 资源 | 链接 | 一句话定位 |
|------|------|----------|
| **基于飞腾 CPU 的高性能编译器 PhyGCC 的安装及配置说明** | [SegmentFault 2024-03](https://segmentfault.com/a/1190000044680095) | PhyGCC 10.3.1 安装实操（含 `-mtune=ftc66x` 选项）[社区] |

### 11.3 飞腾 phytium_repos 本地资源（路径锚点）

> 这是本项目护城河的实证池（45 目录），每个 Expert 写"飞腾工程实证"段都要从这里找证据。

| 资源 | 路径 | 用途 |
|------|------|------|
| **飞腾 Linux 内核** | `/data/usershare/ai/飞腾/phytium_repos/phytium-linux-kernel/` | 内核编译（GCC/Clang） |
| **飞腾 Yocto** | `/data/usershare/ai/飞腾/phytium_repos/phytium-linux-yocto/` | **含 LLVM 13.0.1 recipe**（飞腾嵌入式用） |
| **飞腾 Android 11 设备树** | `/data/usershare/ai/飞腾/phytium_repos/e2000-android11-device/` | **含 LLVM 精简版（external_llvm-project）** |
| **飞腾 FreeBSD** | `/data/usershare/ai/飞腾/phytium_repos/freebsd/` | **含 LLVM ports**（clang/lld/lldb/compiler-rt/libcxx） |
| **飞腾 Buildroot** | `/data/usershare/ai/飞腾/phytium_repos/buildroot*/` | 嵌入式交叉编译 |
| **飞腾 NPU SDK**（TVM fork） | `/data/usershare/ai/飞腾/phytium_repos/opt-npu/ncsdk/common/phytvm/` | ⚠️ **是 Apache TVM fork**（非飞腾自研 LLVM 后端，oracle §0.3 已澄清） |
| **OpenXiangShan LLVM** | `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/` | 完整 LLVM monorepo（22 子项目），本项目代码级实例主源 |

### 11.4 国产 CPU 厂商 LLVM/GCC 生态（开源可查部分）

| 厂商 | 指令集 | LLVM/GCC 状态 | 来源 |
|------|--------|-------------|------|
| **飞腾** | ARMv8.4（FTC862） | PhyCC（基于 LLVM）+ PhyGCC（基于 GCC），**主线 LLVM 无 FTC86x 调度模型** | [飞腾官方] / [实测-待 E18 确认] |
| **华为鲲鹏** | ARMv8（TaiShan v110） | openEuler GCC fork；是否有 LLVM fork 待查 | [推测-依据] |
| **华为昇腾**（NPU） | 自研 | **CANN 编译器**（基于 LLVM/TVM/MLIR） | [社区] |
| **平头哥（玄铁）** | RISC-V | 玄铁 C 系列；T-Head RISC-V LLVM fork | [推测-依据] |
| **龙芯** | LoongArch | 主线 LLVM ≥ 18 已支持 LoongArch | [推测-依据] |
| **海光** | x86 (Zen) | 用主线 GCC/LLVM | [推测-依据] |
| **申威** | SW64 | 主线 LLVM ≥ 17 支持 SW64 | [推测-依据] |

---

## 12. 刷新机制与可信度标注

### 12.1 资源时效性

| 资源类型 | 刷新频率 | 备注 |
|---------|---------|------|
| LLVM 6 月 release | 每年 3 月 + 9 月 | 主版本号 N.1.0 / N.1.x |
| LLVM Weekly | 每周 | Alex Denner 编辑，必订 |
| LLVM Discourse | 实时 | 主讨论 |
| LLVM Dev Meeting | 每年（US 春秋 + Euro） | 视频会后公开 |
| 教材 | 3-5 年/版 | 龙书 2006，Cooper 2022 |
| 教程（GitHub） | 持续 | Evian-Zhang 等持续更新 |
| 飞腾 SDK | 不定期 | 关注飞腾公众号 |

### 12.2 可信度分级（与飞腾项目资源库 §11.2 对齐）

| 标签 | 含义 | 示例 |
|------|------|------|
| `[实测]` | 本项目 grep/diff 实测 | `主线 LLVM 无 FTC86x` |
| `[官方]` | 厂商一手（官网/产品页/白皮书） | PhyCC 2.0 基于 LLVM |
| `[GitHub]` | 开源项目 README/code | Evian-Zhang/llvm-ir-tutorial |
| `[Discourse]` | LLVM 官方论坛 | discourse.llvm.org |
| `[HN/Reddit]` | 英文社区讨论 | HN 上的 "How to learn LLVM" |
| `[社区]` | 中文社区（知乎/CSDN/豆瓣/博客园） | SegmentFault PhyGCC 安装 |
| `[B站]` | B 站视频课程 | 先进编译实验室 MLIR |
| `[豆瓣]` | 豆瓣书评/评分 | LLVM 编译器实战教程 6.5 |
| `[报道]` | 权威媒体新闻报道 | Phoronix GCC vs Clang |
| `[推测-依据]` | 基于公开信息推断 | 华为可能有 LLVM fork |

### 12.3 使用建议

1. **数字优先看一手**：性能数字优先 `[实测] > [官方] > [报道]`；社区内容 `[GitHub] > [Discourse] > [社区]`。
2. **博客/CSDN 验证**：博客/CSDN/知乎内容**必须找到原始论文/官方文档/GitHub 才能引用进 Expert**。
3. **链接失效**：网络资源链接可能失效，引用时同时记录**资源名 + 主题**，未来可重新搜索。
4. **跨语言互证**：LLVM 中文资源丰富，但深度内容仍以英文（Discourse/论文/官方文档）为主，相互补充。
5. **版本敏感性**：LLVM 每 6 月 release，6 月前的 API 教程可能过时；优先用 **≥ LLVM 18** 的资料。

---

📌 **下一步**：
1. 各 Expert 在 `## 参考文献` 末尾，对通用资源添加 `[LLVM-资源库-§X.Y]` 引用，**避免在 18 篇里重复列举**。
2. 每年（如 2027-07）刷新 §1 顶会时间、§3.4 免费讲义新版、§10.2 LLVM 子项目状态。
3. 项目内重要新闻（如 LLVM 新版本发布、Modular/Mojo 进展）应及时追加到对应章节。
