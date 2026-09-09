# CSdiy 选修课程完全解析（编译原理 + PL设计分析 + 图形学 + Web开发 + 数据科学）

> 本文档覆盖 csdiy 课程地图中五大选修类，共 21 门课程。
> 数据来源：csdiy.wiki 课程详情 + 课程官网 + 学科知识。

---

# 第一大类 · 编译原理（6 门）

> **核心**：理解高级语言如何变成机器可执行代码——从词法到目标代码的完整流水线。

---

## 课程 #1 · Stanford CS143：Compilers ⭐ 经典

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 先修 | 计算机体系结构 |
| 语言 | Java 或 C++ |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 150 小时 |
| 课程网站 | http://web.stanford.edu/class/cs143/ |
| B站视频 | https://www.bilibili.com/video/BV17K4y147Bz |
| 教材 | **龙书** *Compilers: Principles, Techniques, and Tools* |
| 作业 | 5 书面 + 5 编程（实现 COOL 语言编译器）|

**核心**：为课程设计的 **COOL 语言**（Classroom Object-Oriented-Language）实现完整编译器，编译到 MIPS 汇编，在 Spim 模拟器执行。

### 📑 完整教学大纲（龙书经典顺序，逐阶段解析）

#### 🔵 前端：分析阶段（源码 → AST）

| 阶段 | 核心内容 | 关键概念 |
|------|---------|---------|
| **1. 词法分析（Lexical Analysis）** ⭐ | 源码 → token 流；**正则表达式**；**有限自动机**（DFA/NFA）；NFA→DFA 转换（子集构造法）；Lex 工具 | token、正则、DFA/NFA |
| **2. 语法分析（Syntax Analysis）** ⭐⭐ | token 流 → **AST（抽象语法树）**；上下文无关文法（CFG）；**自顶向下**（递归下降/LL）；**自底向上**（**LR/SLR/LALR** ⭐）；Yacc 工具；错误恢复 | CFG、FIRST/FOLLOW、LR 分析 |
| **3. 语义分析（Semantic Analysis）** ⭐ | 类型检查；**符号表**；作用域；类型系统；COOL 的类型推断 | 类型检查、符号表 |

#### 🟢 中端：中间表示与优化

| 阶段 | 核心内容 |
|------|---------|
| **4. 运行时环境** ⭐ | 活动记录（栈帧）；调用约定；堆管理；静态/动态作用域 |
| **5. 中间代码生成（IR）** | 三地址码；语法树/有向无环图；翻译方案 |
| **6. 代码优化** ⭐ | 基本块/流图；**数据流分析**（到达定值/可用表达式/活跃变量）；常量折叠；死代码消除；循环优化 |

#### 🟡 后端：目标代码生成

| 阶段 | 核心内容 |
|------|---------|
| **7. 目标代码生成** ⭐ | 寄存器分配（**图着色算法** ⭐）；指令选择；peephole 优化 |
| **8. 链接与加载**（简介）| 静态/动态链接（联系 CSAPP 第 7 章）|

### 📑 5 个编程作业（PA，实现 COOL 编译器，难度递进）⭐

| PA | 阶段 | 任务 |
|----|------|------|
| **PA1** | 词法分析 | 用 JLex/CoolLex 写 COOL 词法分析器 |
| **PA2** | 语法分析 | 用 CUP/Javacc 写 COOL 语法分析器 |
| **PA3** | 语义分析 | 类型检查 + 符号表 |
| **PA4** | 代码生成 | COOL → MIPS 汇编 |
| **PA5** | 优化 | 寄存器分配 + 代码优化 |

**学习建议**：5 个 PA 循序渐进，最终你的 COOL 程序能编译运行。优化部分留有很大设计空间。

### 🎯 在 CS/AI 中的应用
- **解析器** → SQL 解析、JSON/XML 解析、DSL 设计
- **正则/自动机** → 文本处理、搜索引擎、NLP 分词
- **数据流分析** → 程序优化、静态分析（联系 NJU 软件分析）
- **类型系统** → Rust/Haskell 的类型安全、ML 类型推断

---

## 课程 #2 · PKU 编译原理实践 ⭐ 中文强推

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | 北京大学 |
| 先修 | 系统基础 + 数据结构 + 编程基础 |
| 语言 | **C/C++/Rust 任选** |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 60 小时 |
| 助教 | [@MaxXing](https://github.com/MaxXingSoft)（设计 Koopa IR + 保姆级文档）|

**核心**：实现精简版 C 语言（**SysY**）→ RISC-V 汇编的编译器。**无框架代码，从空文件夹开始**——极致锻炼。

### 📑 9 步保姆级拆分（Koopa IR 中间表示）⭐

csdiy 评价：*"让任何愿意花时间的同学都可以更容易实现自己的编译器。"* 助教设计了 **Koopa IR**（类似 LLVM IR，简化版）+ 配套运行时库 + 9 步文档。

| 步骤 | 核心任务 |
|------|---------|
| 1 | **环境配置 + Hello World**（快速正反馈）|
| 2 | **词法分析 + 语法分析**（SysY → AST）|
| 3 | **语义分析**（类型检查）|
| 4 | **AST → Koopa IR**（生成中间表示）|
| 5 | **Koopa IR 优化**（常量折叠/死代码消除）|
| 6 | **Koopa IR → 水寄存器分配** |
| 7 | **Koopa IR → RISC-V 汇编**（栈式）|
| 8 | **寄存器分配优化** |
| 9 | **完整编译 + 测试** |

### Koopa IR 亮点
- 类似 **LLVM IR** 的设计（学习 Koopa 有助理解 LLVM）
- 配套运行时库：轻松解析/生成/修改/输出 Koopa IR
- 专注实践需要的部分，剔除无用细节

### 🎯 在 CS 中的应用
- **SysY → RISC-V** 是真实编译器的完整流程
- **Koopa IR** 助你理解 LLVM（工业级编译器框架）
- 从零开始构建大型系统的能力

---

## 课程 #3 · NJU 编译原理（中文，ANTLR 辅助）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | 南京大学 |
| 先修 | 离散数学 |
| 语言 | Java |
| 难度 | 🌟🌟🌟 |
| 学时 | 80 小时 |

**特色**：用 **ANTLR v4**（LL 解析器生成器）辅助教学，可视化语法树。幽默风趣，**先实践后理论**。

### 📑 核心教学主题
- ANTLR v4 基础（即时的可视化语法树）
- 词法分析 + 语法分析（用 ANTLR 自动生成）
- 语义分析
- C 语言的"神秘面纱"（揭开编译过程）
- 代码生成

---

## 课程 #4 · KAIST CS420：Compiler Design ⭐ Rust 版

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | KAIST |
| 先修 | 数据结构 + 系统基础 + Rust |
| 语言 | **Rust** |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 80 小时 |
| 课程网站 | https://github.com/kaist-cp/cs420 |
| YouTube | https://www.youtube.com/playlist?list=PL5aMzERQ_OZ8RWqn-XiZLXm1IJuaQbXp0 |

**特色**：基于 Rust 的 **KECC**（KAIST Educational C Compiler）框架，面向**真实 C 语言**（非玩具语言），用 **Csmith** Fuzzing 测试。

### 📑 核心教学主题（偏中后端）
| 主题 | 核心内容 |
|------|---------|
| **抽象语法树遍历** | 从 AST 开始（不手动写前端）|
| **SSA 中间代码生成** ⭐ | 静态单赋值形式（LLVM 核心）|
| **中间代码优化** | CFG 简化；**GVN**（全局值编号）|
| **目标代码生成** | RISC-V 汇编 |
| **LLVM 理解** | KECC 的 IR 设计类似 LLVM |

**定位**：对理解和学习 **LLVM**（工业级编译器框架）很有帮助。

## 课程 #5-6 · SJTU / USTC 编译原理
两所国内高校的编译原理课程，详见 csdiy 网站。

---

# 第二大类 · 编程语言设计与分析（4 门）

---

## 课程 #7 · Stanford CS242：Programming Languages ⭐ 理论+系统

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 主讲 | **Will Crichton** |
| 先修 | 系统 + PL 理论基础 |
| 语言 | **OCaml, Rust** |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 60 小时 |

**核心**：**从理论走向系统**。主讲将课程设计写成[论文](https://arxiv.org/abs/1904.06750)。

### 📑 核心教学主题（6 个作业主题）

| 作业 | 主题 | 核心内容 |
|------|------|---------|
| **A1** | **JSON 形式化与证明** | 用形式化方法描述 JSON |
| **A2** | **Lambda 演算** ⭐ | PL 的数学根基；β-归约；Church 编码 |
| **A3** | **OCaml 函数式编程** | 模式匹配；不可变性；高阶函数 |
| **A4** ⭐ | **类型检查器 + 解释器** | 用 OCaml 实现函数式语言的类型检查和解释执行 |
| **A5** | **WebAssembly** | WASM 理论与实践 |
| **A6** ⭐ | **Linear Type + Rust 所有权** | 线性类型；Rust 所有权机制的理论基础 |

### 🎯 在 CS 中的应用
- **Lambda 演算** → 函数式编程的理论根基
- **类型系统** → Rust/Haskell/TypeScript 的类型安全
- **Linear Type** → Rust 所有权、内存安全的理论基础
- **WASM** → Web 的未来

---

## 课程 #8 · NJU 软件分析 ⭐⭐ 中文首选

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | 南京大学（**李樾、谭添**）|
| 先修 | 数据结构 + 一门语言 |
| 语言 | Java |
| 难度 | 🌟🌟🌟 |
| 学时 | 60 小时 |
| 作业框架 | **太阿**（自创 Java 分析框架）|
| 特色 | **所有人可用的在线评测系统** ⭐ |

**核心**：**静态程序分析**——不运行程序，分析源代码获得程序性质的**近似**结论。

### 📑 完整教学大纲 + 8 个作业（太阿框架）

#### 🔵 基础（L1-L3）
| 主题 | 核心内容 |
|------|---------|
| **程序的表示** | AST、**控制流图（CFG）**、中间表示 |
| **数据流分析基础** ⭐ | 前向/后向分析；may/must 分析；传播规则 |

#### 🟢 数据流分析（L4-L6）→ 3 个作业
| 作业 | 分析技术 | 应用 |
|------|---------|------|
| **A1** | **活跃变量分析** | 编译优化 |
| **A2** | **常量传播** | 编译优化 |
| **A3** | **死代码检测** | 编译优化 |

#### 🟡 指针分析（L7-L9）⭐⭐ → 3 个作业
| 作业 | 分析技术 | 应用 |
|------|---------|------|
| **A4** | **程序调用图（CG）构建** | 程序理解 |
| **A5** ⭐ | **上下文不敏感指针分析** | 别名分析 |
| **A6** ⭐ | **上下文敏感指针分析**（C.S.）| 精度更高的别名 |

#### 🟣 高级主题（L10-L11）→ 2 个作业
| 作业 | 分析技术 | 应用 |
|------|---------|------|
| **A7** | **IFDS**（数据流分析框架）| 理论进阶 |
| **A8** ⭐ | **污点分析（Taint Analysis）** | 软件安全 |

### 🎯 在 CS/AI 中的应用
- **编译优化**（活跃变量/常量传播/死代码）→ 提升代码性能
- **指针分析** → 别名分析、C/C++ 内存安全
- **污点分析** ⭐ → **漏洞挖掘**（SQL 注入、XSS 等安全检测）
- **静态分析** → IDE 智能提示、代码审查工具

**csdiy 评价**：两位老师**讲得尤其细致入微**，课上带你一步一步走算法流程。

## 课程 #9-10 · PKU 软件分析 / Cambridge 语义
详见 csdiy 网站。

---

# 第三大类 · 计算机图形学（6 门）

> **csdiy 观点**：图形学不等于 OpenGL，不等于光线追踪，而是一套**生成整个虚拟世界**的方法——从基础原理到前沿研究。

---

## 课程 #11 · GAMES101 ⭐⭐ 中文首选入门课

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UCSB（**闫令琪**，实时光线追踪技术推动者）|
| 先修 | 线性代数 + 高等数学 + C++ |
| 语言 | C++ |
| 难度 | 🌟🌟🌟 |
| 学时 | 80 小时 |
| 课程网站 | http://games-cn.org/intro-graphics/ |
| 课程网站(UCSB) | https://sites.cs.ucsb.edu/~lingqi/teaching/games101.html |
| B站视频 | https://www.bilibili.com/video/BV1X7411F744 |
| PPT+视频 | http://games-cn.org/graphics-intro-ppt-video/ |
| 教材 | *Fundamentals of Computer Graphics* |
| 作业 | [8 个 Project](http://games-cn.org/forums/topic/allhw/) |
| 资源汇总 | https://github.com/ysj1173886760/Learning/tree/master/graphics/GAMES101 |

**csdiy 评价**：国内最有名的图形学公开课。以**十分生动**的方式带入门。每个 Project 代码量不多但都很有趣。

### 📑 完整教学大纲（四大组成部分，逐讲解析）

#### 🔵 Part 1：光栅化成像（Rasterization）⭐

| 讲次 | 主题 | 核心内容 |
|------|------|---------|
| 1 | **计算机图形学概述** | 图形学 vs 计算机视觉 vs 图像处理；图形学的应用（游戏/电影/CAD/可视化）|
| 2 | **线性代数复习** ⭐ | 向量点积/叉积；矩阵变换；图形学 = 线代的可视化应用 |
| 3 | **变换（Transformation）** ⭐ | 缩放/旋转/平移；齐次坐标；**仿射变换**的组合 |
| 4 | **三维变换与视图** ⭐ | 3D 旋转；视图变换（view）；**投影变换**（正交/透视）|
| 5 | **光栅化（视图变换续）** | 视口变换；屏幕像素采样 |
| 6 | **光栅化（深度测试与抗锯齿）** ⭐ | Z-buffer；**反走样/抗锯齿**（MSAA）；傅里叶变换视角 |
| 7 | **着色（Shading）** ⭐⭐ | Blinn-Phong 反射模型（环境光+漫反射+镜面）；着色频率（Flat/Gouraud/Phong）|
| 8 | **着色（纹理映射）** ⭐ | 纹理 = 表面上的属性；双线性插值；mipmap；

#### 🟢 Part 2：几何与曲线（Geometry）

| 讲次 | 主题 | 核心内容 |
|------|------|---------|
| 9 | **几何（基本表示）** | 隐式表示（代数/CSG/距离函数/分形）；显式表示（点云/多边形网格）|
| 10 | **几何（曲线与曲面）** ⭐ | Bézier 曲线（de Casteljau 算法）；B样条；曲面细分 |
| 11 | **几何（阴影映射）** | Shadow Mapping；**硬阴影 vs 软阴影** |

#### 🟡 Part 3：光线追踪（Ray Tracing）⭐⭐ 核心难点

| 讲次 | 主题 | 核心内容 |
|------|------|---------|
| 12 | **光线追踪（基础）** ⭐⭐ | Whitted-style 光线追踪；递归反射/折射；vs 光栅化 |
| 13 | **辐射度量学（Radiometry）** ⭐⭐ | 辐射通量/强度/辐照度/辐射度；**本课最抽象** |
| 14 | **光线追踪（路径追踪 Path Tracing）** ⭐⭐⭐ | 渲染方程；蒙特卡洛积分；**路径追踪**——现代渲染引擎基础 |
| 15 | **材质与外观** | BRDF；微面元模型；各向异性材质 |

#### 🟣 Part 4：动画与模拟（Animation）

| 讲次 | 主题 | 核心内容 |
|------|------|---------|
| 16 | **动画（基础）** | 关键帧；物理模拟；运动学（前向/反向）|
| 17 | **动画（质点弹簧系统）** | 质点弹簧；**显式/隐式欧拉法**；稳定性 |
| 18 | **动画（粒子系统与碰撞）** | 粒子；空间哈希；碰撞检测 |

### 📑 8 个 Project（高质量实战）

| Project | 核心任务 | 难度 |
|---------|---------|------|
| **Assignment 1** | 旋转与投影矩阵实现 | 🌟 |
| **Assignment 2** ⭐ | **三角形光栅化 + Z-buffer + 抗锯齿** | 🌟🌟 |
| **Assignment 3** ⭐ | **Blinn-Phong 着色 + 纹理映射 + 凹凸/位移贴图 + 阴影** | 🌟🌟🌟 |
| **Assignment 4** ⭐ | **Whitted 风格光线追踪 + 反射/折射** | 🌟🌟🌟 |
| **Assignment 5** ⭐⭐ | **路径追踪 Path Tracing**（含蒙特卡洛积分） | 🌟🌟🌟🌟 |
| **Assignment 6-8** | 进阶拓展 | - |

**csdiy 评价**：每个 Project 代码量不多但都很有趣。每个 Project 都有选做拓展（更好的质量、更快的速度）。

### 🎯 在 CS/AI 中的应用
- **变换矩阵** → 神经网络的几何理解、3D 视觉
- **光栅化** → 游戏引擎、GPU 编程
- **路径追踪** → 电影特效、照片级渲染
- **物理模拟** → 游戏、机器人仿真
- **辐射度量学** → 神经渲染（NeRF/可微渲染）

---

## 课程 #12 · GAMES202：高质量实时渲染（GAMES101 进阶）⭐

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UCSB（**闫令琪**）|
| 先修 | GAMES101 + 线代 + 高数 + C++ |
| 语言 | C++ |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 60 小时 |
| 课程网站 | http://games-cn.org/games202/ |

**核心**：**实时高质量渲染**（>30 FPS），在苛刻时间限制下打破速度与质量的权衡。

### 📑 核心教学主题（专题形式，前沿内容）
1. **实时软阴影** ⭐
2. **环境光照**
3. **基于预计算/无预计算的全局光照**
4. **基于物理的着色模型**
5. **实时光线追踪** ⭐
6. **抗锯齿与超采样**（TAA/DLSS 原理）
7. **常见加速方式**（LBVH/纹理预计算）

---

## 课程 #13 · GAMES103：基础动画与物理模拟

**定位**：物理模拟基础。刚体动力学、碰撞、布料模拟、流体。

---

## 课程 #14 · CMU 15-462：Computer Graphics ⭐ 最全面（28 讲真实结构）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 课程编号 | 15-462/662 |
| 开课 | CMU |
| 主讲（Fall 2022） | **Jim McCann** |
| 贡献者 | Keenan Crane, Kayvon Fatahalian, Stelian Coros, Nancy Pollard 等 |
| 先修 | 向量微积分 + 线代 + C/C++ |
| 语言 | C/C++ |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | http://15462.courses.cs.cmu.edu/fall2022/ |
| YouTube | https://www.youtube.com/watch?v=W6yEALqsD7k |
| B站 | https://www.bilibili.com/video/BV1QZ4y1K7ga |
| 教材 | *Fundamentals of Computer Graphics* + *PBRT*（无唯一教材）|
| Project 框架 | [**Scotty3D**](https://github.com/CMU-Graphics/Scotty3D)（完整 3D 包，建模+渲染+动画）|
| Scotty3D 文档 | https://cmu-graphics.github.io/Scotty3D-docs/ |

**核心**：全面介绍图形学，聚焦**基本概念与技术**以及它们与多个问题领域（渲染、动画、几何、成像）的交叉。

### 📑 完整教学大纲（Fall 2022 真实结构，28 讲）⭐

#### 🔵 数学基础 + 光栅化（L1-L8）
| Lecture | 主题 | 核心内容 |
|---------|------|---------|
| **L1** (8/30) | **Introduction to Computer Graphics** | 图形学全景；为什么学；Scotty3D 介绍 |
| **L2** (9/1) | **Math Review I: Linear Algebra** ⭐ | 向量空间；线性变换；特征分解；图形学的数学根基 |
| **L3** (9/6) | **Math Review II: Vector Calculus** | 梯度/散度/旋度；雅可比/海森；多元微积分 |
| **L4** (9/8) | **Rasterization and Sampling** ⭐⭐ | 画三角形；**采样理论**；混叠（aliasing）|
| **L5** (9/13) | **Spatial Transformations** | 2D/3D 变换；齐次坐标 |
| **L6** (9/15) | **3D Rotations and Complex Transformations** ⭐ | 欧拉角/轴角；**四元数**；旋转的复杂性 |
| **L7** (9/20) | **Perspective Projection and Texture Mapping** | 透视投影；纹理；UV 映射 |
| **L8** (9/22) | **Depth and Transparency** | Z-buffer；透明度；混合 |

📝 **A1: Rasterizer（光栅化器）** ⭐——实现软件光栅化器

#### 🟢 几何（L9-L13）
| Lecture | 主题 | 核心内容 |
|---------|------|---------|
| **L9** (9/27) | **Introduction to Geometry** | 几何表示法谱系；隐式 vs 显式 |
| **L10** (9/29) | **Meshes and Manifolds** ⭐ | 三角网格；**流形**（manifold）；拓扑 |
| **L11** (10/4) | **Digital Geometry Processing** ⭐ | 网格细分；简化；重网格化 |
| L12 (10/6) | Midterm Review | |
| L13 (10/11) | **MIDTERM** | |
| **L14** (10/13) | **Geometric Queries** | 最近点；光线-物体相交；距离查询 |

📝 **A2: Mesh Editing（网格编辑）** ⭐——实现网格编辑器（含局部/全局操作）

#### 🟡 渲染（L15-L21）⭐⭐ 本课巅峰
| Lecture | 主题 | 核心内容 |
|---------|------|---------|
| L15 (10/25) | **Spatial Data Structures** ⭐ | BVH；KD-Tree；加速结构（加速渲染）|
| L16 (10/27) | **Color** | 色彩空间（sRGB/Lab）；色域；色彩感知 |
| **L17** (11/1) | **Radiometry** ⭐⭐ | 辐射度量学：辐射通量/强度/辐照度/辐射度（**本课最抽象**）|
| **L18** (11/3) | **The Rendering Equation** ⭐⭐⭐ | **渲染方程**（Kajiya）——所有现代渲染算法的统一基础 |
| **L19** (11/8) | **Numerical Integration** | 数值积分；蒙特卡洛基础（联系 18.01/18.330）|
| **L20** (11/10) | **Monte Carlo Rendering** ⭐⭐⭐ | 蒙特卡洛路径追踪；重要性采样 |
| **L21** (11/15) | **Variance Reduction** | 降低方差；俄罗斯轮盘赌；直接光照 |

📝 **A3: Path Tracing（路径追踪）** ⭐⭐⭐——实现物理正确的路径追踪器（本课巅峰）

#### 🟣 动画 + 优化（L22-L28）
| Lecture | 主题 | 核心内容 |
|---------|------|---------|
| **L22** (11/17) | **Introduction to Animation** | 动画原理；关键帧；运动学 |
| **L23** (11/22) | **Dynamics and Time Integration** ⭐ | 物理模拟；显式/隐式欧拉；稳定性 |
| **L24** (11/29) | **Introduction to Optimization** | 梯度下降；拉格朗日乘数（联系 EE364A 凸优化）|
| **L25** (12/1) | **Physically-Based Animation and PDEs** | 偏微分方程的数值解（流体、弹性体）|
| L26 (12/6) | **The Latest from SIGGRAPH** ⭐ | 最新 SIGGRAPH 研究（前沿讲座）|
| L27 (12/8) | Exam Review | |
| L28 (12/12) | **FINAL EXAM** | |

📝 **A4: Animation（动画）**——实现 IK（逆运动学）+ 物理模拟

### 🎯 在 CS/AI 中的应用（极高价值）
| 15-462 主题 | 在 AI/CS 中的应用 |
|-----------|------------------|
| **采样理论** | 信号处理、Nyquist、抗锯齿 |
| **变换/四元数** | 3D 视觉、机器人姿态、SLAM |
| **BVH/空间结构** ⭐ | 光线追踪、碰撞检测、近邻搜索（KD-Tree 在 ML 中也用）|
| **辐射度量学** | 神经渲染（**NeRF**、可微渲染）|
| **渲染方程** | 图形学的"圣杯"，所有渲染算法的基础 |
| **路径追踪** | 电影特效、照片级渲染、**可微渲染** |
| **物理模拟** | 游戏、机器人仿真、数字孪生 |
| **优化** | 拉格朗日乘数法（联系 EE364A）|

**⚠️ 学习建议**：
- **Scotty3D 是核心**：A1-A4 串联整个课程，实现完整 3D 包
- **A3 路径追踪是巅峰**：辐射度量学 + 蒙特卡洛 + 渲染方程的综合
- 数学要求高：线代 + 向量微积分必备（呼应 18.02）

---

## 课程 #15 · Stanford CS148
Stanford 图形学入门，偏实用，适合作为 15-462/GAMES101 的补充。

## 课程 #16 · USTC CG
中科大图形学课程，中文资源。

---

# 第四大类 · Web 开发（4 门）

---

## 课程 #17 · University of Helsinki：Full Stack Open ⭐ 强推全栈

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | University of Helsinki |
| 先修 | 编程 + 网络 + 数据库 + Git 基础 |
| 语言 | JavaScript/HTML/CSS/NoSQL/SQL |
| 难度 | 🌟🌟 |
| 中文网站 | https://fullstackopen.com/zh/ |
| Discord | https://study.cs.helsinki.fi/discord/join/fullstack/ |
| Telegram | https://t.me/fullstackcourse/ |

**核心**：用 JavaScript 开发现代 Web 应用。聚焦 **React 单页应用（SPA）** + **Node.js REST API** + GraphQL + 测试 + MongoDB。

### 📑 完整教学大纲（13 章，逐章深入）

#### 🔵 Part 0：Web 基础
- **HTTP 协议**：请求/响应模型；GET/POST；状态码（200/404/500）
- **DOM**：文档对象模型；浏览器渲染流程
- **传统 Web 应用** vs **SPA（单页应用）**：MVC vs 前端分离
- **AJAX**：异步请求；Fetch API；为什么 SPA 体验更好

#### 🟢 Part 1：React 入门 ⭐
- **JSX**：JavaScript + HTML 的混合语法
- **组件（Component）**：函数组件；props 传参
- **State（状态）** ⭐：`useState` Hook；状态更新触发重新渲染
- **事件处理**：onClick/onChange；表单受控组件
- **副作用（Effect）**：`useEffect` Hook；依赖数组；清理函数
- **条件渲染** 与 **列表渲染**（`map` + `key`）

#### 🟡 Part 2：与服务器通信
- **REST API**：资源模型；CRUD 操作
- **Fetch**：从服务器获取数据；async/await
- **Effect 中的数据获取** ⭐：避免竞态条件；loading/error 状态
- **自定义 Hook**：封装数据获取逻辑
- **CSS 样式**：内联/类名/CSS Modules

#### 🟣 Part 3：Node.js 后端 ⭐
- **Node.js 基础**：事件循环；非阻塞 I/O；为什么 JS 适合网络编程
- **Express** 框架：路由；中间件（middleware）链
- **REST API 实现**：GET/POST/PUT/DELETE；JSON 响应
- **CORS**：跨域资源共享；预检请求
- **环境变量**：dotenv；配置管理

#### 🔴 Part 4：Express + 测试
- **Express 应用结构**：控制器/模型分层
- **MongoDB + Mongoose** ⭐：NoSQL 文档数据库；Schema 定义；CRUD
- **单元测试**：Jest；测试驱动开发（TDD）
- **async/await 错误处理**：try/catch；next(error)

#### 🟠 Part 5：端到端测试
- **React 组件测试**：React Testing Library
- **端到端（E2E）测试**：Cypress ⭐；模拟用户操作
- **测试策略**：测试金字塔

#### 🟤 Part 6：状态管理（Redux）⭐
- **Redux 核心概念** ⭐：store / action / reducer / dispatch；单向数据流
- **Redux Toolkit**：现代 Redux 写法；`createSlice`
- **连接 React 与 Redux**：`useSelector` / `useDispatch`
- **何时用 Redux**：不是所有状态都需要 Redux

#### ⚫ Part 7：进阶 React
- **React Router**：客户端路由；嵌套路由
- **自定义 Hooks 进阶**：`useAuth` / `useResource`
- **性能优化**：`useMemo` / `useCallback` / `React.memo`
- **Webpack/Babel 简介**：构建工具

#### Part 8：GraphQL ⭐
- **GraphQL vs REST**：单一端点；客户端决定数据结构
- **Schema**：类型定义；Query/Mutation
- **Apollo**：客户端 + 服务器
- **解析器（Resolver）**：字段级数据获取

#### Part 9：TypeScript ⭐
- **静态类型**：编译期类型检查
- **类型注解**：interface / type / 泛型
- **React + TypeScript**：组件 props 类型化
- **类型守卫** 与 **类型断言**

#### Part 10：React Native
- 跨平台移动开发；React Native vs 原生
- 核心组件（View/Text/FlatList）
- Expo 工作流

#### Part 11：CI/CD
- GitHub Actions；自动化测试/部署
- 环境管理（dev/staging/prod）

#### Part 12：容器化（Docker）⭐
- Docker 基础：镜像/容器/Dockerfile
- Docker Compose：多容器编排
- 部署到云

#### Part 13：关系型数据库
- PostgreSQL；SQL 查询
- 与 MongoDB 的对比

### 🎯 在 CS 学习中的定位
- **现代全栈 Web 开发的最完整教程**——前端到后端到部署的完整链路
- csdiy 强推：内容与时俱进，每年更新

---

## 课程 #18 · Stanford CS142：Web Applications

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 先修 | 编程经验 |
| 语言 | JavaScript/HTML/CSS |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | https://web.stanford.edu/class/cs142/ |
| 视频 | https://web.stanford.edu/class/cs142/lectures.html |
| 作业 | https://web.stanford.edu/class/cs142/projects.html |

**核心**：HTML/CSS/JS/React/Node/Express/Web 安全。**8 个 Project**。

### 📑 核心教学主题
- **HTML/CSS**：语义化标签；Flexbox/Grid 布局；响应式设计
- **JavaScript**：闭包；原型链；异步（Promise/async-await）；ES6+
- **DOM 操作**：事件；事件委托；冒泡与捕获
- **React** ⭐：组件；状态；生命周期；Hooks
- **Node.js + Express**：后端 API
- **数据库**：MongoDB/SQL
- **Web 安全** ⭐：XSS/CSRF/SQL 注入；身份认证（session/JWT）
- **构建工具**：Webpack/Vite

### 📑 8 个 Project（实战为主）
构建一个完整的 Web 应用（如社交媒体），每个 Project 增加新功能。

## 课程 #19-20 · MIT Web / CS571
详见 csdiy 网站。

---

# 第五大类 · 数据科学（1 门）

---

## 课程 #21 · UCB Data100：Principles and Techniques of Data Science ⭐

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | Data8, CS61A, 线性代数 |
| 语言 | Python |
| 难度 | 🌟🌟🌟 |
| 学时 | 80 小时 |
| 课程网站 | https://ds100.org/ |
| 教材 | https://www.textbook.ds100.org/intro.html |

**核心**：数据科学全流程——数据清洗、特征提取、可视化、机器学习与推理基础。**Pandas/NumPy/Matplotlib** 工具链。

### 📑 完整教学大纲（按数据科学生命周期组织）⭐

#### 🔵 Phase 1：数据获取与清洗

| 主题 | 核心内容 | 关键概念/函数 |
|------|---------|--------------|
| **Pandas 基础** ⭐ | DataFrame/Series；索引；切片 | `pd.DataFrame`, `loc`, `iloc`, `groupby` |
| **数据清洗** | 缺失值处理；类型转换；异常值检测 | `fillna`, `dropna`, `isnull` |
| **正则表达式** | 文本提取与清洗 | `re.match`, `str.extract`, `str.replace` |
| **数据格式** | CSV/JSON/HTML 表格；爬虫基础 | `pd.read_csv`, `pd.read_json`, `BeautifulSoup` |

#### 🟢 Phase 2：探索性数据分析（EDA）

| 主题 | 核心内容 | 关键概念/函数 |
|------|---------|--------------|
| **数据可视化** ⭐ | 分布；关系；趋势 | Matplotlib/Seaborn；直方图/散点图/箱线图 |
| **描述统计** | 均值/中位数/方差/分位数；偏度/峰度 | `df.describe()` |
| **降维**：**PCA（主成分分析）** ⭐⭐ | 协方差矩阵的特征分解；投影到低维；信息保留率 | `sklearn.decomposition.PCA`；联系 18.06 SVD |

#### 🟡 Phase 3：建模基础

| 主题 | 核心内容 | 数学/公式 |
|------|---------|----------|
| **简单线性回归** ⭐ | 最小二乘法；$y = \beta_0 + \beta_1 x$ | $\hat{\beta} = (X^TX)^{-1}X^Ty$（联系 18.06 L17 投影/最小二乘）|
| **多元线性回归** | 多特征；设计矩阵；解释系数 | 同上 |
| **特征工程** ⭐ | 数值化类别；多项式特征；交互项；分箱 | `pd.get_dummies`, `PolynomialFeatures` |
| **损失函数** | MSE $\frac{1}{n}\sum(y_i - \hat{y}_i)^2$；MAE；Huber | |

#### 🟣 Phase 4：模型评估与正则化

| 主题 | 核心内容 | 关键概念 |
|------|---------|---------|
| **训练/测试划分** | 防止过拟合；泛化误差估计 | `train_test_split` |
| **交叉验证（Cross-Validation）** ⭐ | K 折 CV；超参数调优 | `KFold`, `cross_val_score` |
| **偏差-方差权衡** ⭐⭐ | 模型复杂度的权衡；过拟合 vs 欠拟合 | $E[(y-\hat{f})^2] = \text{Bias}^2 + \text{Var} + \sigma^2$ |
| **正则化** ⭐ | **Lasso（L1）**；**Ridge（L2）**；弹性网 | $\min \|y-X\beta\|^2 + \lambda\|\beta\|_p$（联系 EE364A 凸优化）|

#### 🔴 Phase 5：进阶方法

| 主题 | 核心内容 |
|------|---------|
| **逻辑回归** | 分类；Sigmoid；交叉熵损失（联系 6.050J 信息论）|
| **决策树** ⭐ | 信息增益；ID3/CART；剪枝 |
| **随机森林** ⭐ | 集成学习；Bagging；降低方差 |
| **梯度提升（Boosting）** | XGBoost/LightGBM；前向分步加性建模 |
| **聚类（K-Means）** | 无监督；肘部法则 |
| **SQL 查询** | SELECT/JOIN/GROUP BY；窗口函数 |

### 🎯 在 CS/AI 学习中的应用映射（极高价值）
| Data100 主题 | 在 AI/ML 中的延伸 |
|-------------|-------------------|
| **Pandas** | 所有数据科学/ML 工作的基础工具 |
| **PCA** ⭐⭐ | 直接 = 18.06 SVD 的应用；ML 降维标配 |
| **线性回归 + 最小二乘** ⭐⭐ | = 18.06 L17 投影矩阵的 ML 应用；统计学习根基 |
| **交叉验证** | 所有 ML 模型评估的标准流程 |
| **偏差-方差权衡** ⭐⭐ | 理解过拟合/欠拟合的核心理论框架 |
| **正则化 L1/L2** ⭐ | 现代深度学习 weight decay 的理论基础 |
| **交叉熵损失** | 深度学习分类任务的标准损失（联系 6.050J 熵）|
| **决策树/随机森林** | 经典 ML；特征重要性工具 |

**⚠️ 学习建议**：
- **Data100 是 ML 的最佳前置**——掌握数据全流程后，再学 CS229/深度学习会非常顺
- **数学映射**：PCA↔18.06 SVD，最小二乘↔18.06 投影，正则化↔EE364A，交叉熵↔6.050J 熵
- csdiy 评价：丰富的编程作业是亮点

---

# 📊 选课套餐

### 编译原理
```
CS143(#1) 经典（COOL 语言）或 PKU(#2) 中文强推（SysY→RISC-V）
进阶：CS420(#4) Rust 版（真实 C 语言）
```

### 程序分析
```
NJU 软件分析(#8) ⭐ 中文首选（静态分析，8 作业 + 在线评测）
```

### 图形学
```
GAMES101(#11) ⭐ 中文入门首选 → GAMES202(#12) 实时渲染进阶
英文：CMU 15-462(#14) 最全面
```

### Web 开发
```
Full Stack Open(#17) ⭐ 全栈（React+Node） 或 CS142(#18) Stanford
```

### 数据科学
```
Data100(#21) Python 数据科学入门
```

---

**文档版本**：v1.0
**最后更新**：2026-07-07
