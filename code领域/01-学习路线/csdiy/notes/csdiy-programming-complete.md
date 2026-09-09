# CSdiy 编程入门篇 · 课程完全解析

> 本文档对 csdiy.wiki「课程地图-编程入门」部分的 16 门课程做完全解析。
> 颗粒度：课程元数据 + 核心教学主题 + 在 CS 中的定位 + 学习建议。
> 数据来源：csdiy.wiki 课程详情 + 课程官网 + 学科知识。

> **csdiy 核心观点**：*"Languages are tools, you choose the right tool to do the right thing. Since there's no universally perfect tool, there's no universally perfect language."*（语言是工具，没有完美的语言，只有合适的语言。）

---

# 课程总览（16 门，按子类）

| 子类 | 课程 | 语言 | 难度 |
|------|------|------|------|
| **General（工具）** | MIT-Missing-Semester | shell | 🌟🌟 |
| | UCB Sysadmin DeCal | shell | 🌟🌟🌟 |
| **C 语言** | Harvard CS50 | C/Python/SQL/JS/... | 🌟🌟 |
| | Duke Introductory C | C | 🌟🌟🌟🌟 |
| **Python** | CS50P | Python | 🌟🌟 |
| | UCB CS61A ⭐ | Python/Scheme/SQL | 🌟🌟🌟 |
| | MIT 6.100L | Python | 🌟🌟 |
| **Java** | MIT 6.092 | Java | 🌟🌟 |
| **C++** | Stanford CS106B/X | C++ | 🌟🌟 |
| | Stanford CS106L | C++ | 🌟🌟🌟 |
| | AmirKabir AP1400-2 | C++ | 🌟🌟🌟🌟🌟 |
| **Rust** | Stanford CS110L | Rust | 🌟🌟🌟 |
| | KAIST CS220 | Rust | 🌟🌟🌟 |
| | KAIST CS431 | Rust | 🌟🌟🌟🌟 |
| **函数式** | Cornell CS3110 ⭐ | OCaml | 🌟🌟🌟 |
| | Helsinki Haskell MOOC | Haskell | 🌟🌟 |

---

# 第一子类 · General（工具类 · 所有 CS 学生的必修基础设施）

> csdiy 强调：在学编程语言之前，**先掌握工具链**。"磨刀不误砍柴工"。

---

## 课程 #1 · MIT-Missing-Semester：计算机教育中缺失的学期 ⭐ 必学

### 课程元数据
| 字段 | 内容 |
|------|------|
| 课程名 | **The Missing Semester of Your CS Education** |
| 开课 | MIT CSAIL |
| 先修 | 无（但建议有编程基础后学）|
| 语言 | Shell |
| 难度 | 🌟🌟 |
| 学时 | 10 小时 |
| 课程网站 | https://missing.csail.mit.edu/2020/ |
| 中文网站 | https://missing-semester-cn.github.io/ |
| 视频YouTube(IAP 2020) | https://www.youtube.com/playlist?list=PLyzOVJj3bHQuloKGG59rS43e29ro7I57J |
| 视频YouTube(IAP 2026) | https://www.youtube.com/playlist?list=PLyzOVJj3bHQunmnnTXrNbZnBaCA-ieK4L |

**课程宣言**：*"计算机教学中消失的一个学期"*——大学课堂不涉及但每个 CSer 必须掌握的工具与知识点。

### 📑 核心教学主题（11 讲）

| 讲次 | 主题 | 核心内容 |
|------|------|---------|
| 1 | **Shell 工具与脚本** ⭐ | Bash 基础；管道、重定向；常用命令（grep/find/sed/awk）；shell 脚本编程 |
| 2 | **Shell 工具进阶** | 文件操作；作业控制；终端多路复用（tmux）；别名与配置（dotfiles）|
| 3 | **Vim 编辑器** ⭐ | Vim 模式（normal/insert/visual）；高效编辑；自定义配置 |
| 4 | **数据整理** | 文本处理流水线；正则表达式；数据清洗 |
| 5 | **命令行环境** | SSH 配置与端口转发；tmux；别名；远程开发 |
| 6 | **版本控制（Git）** ⭐⭐ | Git 基础；分支/合并/rebase；GitHub 协作；高级技巧 |
| 7 | **调试与性能分析** | 调试器（gdb/pdb）；性能分析（profiling）；监控工具 |
| 8 | **元编程（构建）** | Make/CMake；依赖管理；持续集成 |
| 9 | **安全与密码学** | 密钥管理；加密基础；安全开发习惯 |
| 10 | **大杂烩** | 修改键盘映射； daemon 服务；虚拟机与容器 |
| 11 | **问答与总结** | 综合答疑 |

### 🎯 在 CS 学习中的定位
- **csdiy 必学工具章节的精华**：Shell/Vim/Git/GitHub/tmux/ssh 等全在这门课里
- **后续所有课程的底层依赖**：没有这些工具，后续的 OS/网络/系统课会非常吃力
- **建议学习时机**：学完计算机导论级课程（如 CS50）之后

**学习建议**：10 小时投入回报极高。配合 csdiy 必学工具章节一起学。

---

## 课程 #2 · UCB Sysadmin DeCal：Linux 系统管理入门

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley OCF |
| 先修 | 无 |
| 语言 | Shell |
| 难度 | 🌟🌟🌟 |
| 学时 | 20 小时 |
| 课程网站 | https://decal.ocf.berkeley.edu/ |
| B站视频 | https://space.bilibili.com/483435468/video |

**定位**：比 Missing Semester 更系统、更清晰，**面向零基础**的 Linux 入门。csdiy 推荐。

### 📑 核心教学主题（12 周）

| 周 | 主题 |
|----|------|
| 1-2 | **Linux 基础**（安装、文件系统、基本命令）|
| 3-4 | **Shell 编程**（bash、tmux、vim）|
| 5 | **包管理**（apt/yum/pip）|
| 6 | **服务（Services）**（systemd、守护进程）|
| 7 | **基础计算机网络** |
| 8 | **网络服务**（Web 服务器、数据库服务）|
| 9 | **安全**（密钥管理、防火墙）|
| 10 | **Git** |
| 11 | **Docker & Kubernetes** |
| 12 | **Puppet & CUDA** |

**学习建议**：部分作业需 UCB 内部账号，可用虚拟机替代。csdiy 推荐 [bandit](https://overthewire.org/wargames/bandit/) 作为远程操作练习的补充。

---

# 第二子类 · C 语言（系统编程的根基）

---

## 课程 #3 · Harvard CS50：This is CS50x ⭐ 最受欢迎的 CS 入门课

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Harvard |
| 主讲 | **Prof. David J. Malan**（激情四射，撕黄页讲二分法）|
| 先修 | 无 |
| 语言 | **C, Python, SQL, HTML, CSS, JavaScript**（多语言全栈！）|
| 难度 | 🌟🌟 |
| 学时 | 20 小时 |
| 课程网站(2025) | https://cs50.harvard.edu/x/2025/ |
| B站中文字幕 | https://www.bilibili.com/video/BV1HW4y1A7Yi/ |
| 资源汇总 | https://github.com/mancuoj/CS50x |

**csdiy 评价**：连续多年被哈佛学生评为**最受欢迎的公选课**。难度温和但作业质量极高，全部免费开源。适合小白入门或大佬休闲。

### 📑 核心教学主题（11 周）

| 周 | 主题 | 核心内容 |
|----|------|---------|
| 0 | **Scratch** | 图形化编程入门（建立编程思维）|
| 1 | **C 语言基础** ⭐ | 变量、类型、运算符；编译；命令行 |
| 2 | **数组** | 一维/多维数组；字符串；命令行参数 |
| 3 | **算法** ⭐ | 线性搜索、二分搜索；冒泡/选择/插入/归并排序；复杂度 Big-O |
| 4 | **内存** ⭐⭐ | 十六进制；指针；内存布局（stack/heap）；内存泄漏 |
| 5 | **数据结构** ⭐ | 链表；树（BST）；哈希表；Trie |
| 6 | **Python** ⭐ | 从 C 转向 Python；对比低级与高级语言 |
| 7 | **SQL** ⭐ | 关系数据库；SQL 基础；多表查询 |
| 8 | **HTML/CSS/JavaScript** | Web 前端基础；DOM；事件 |
| 9 | **Flask** | Python Web 后端；MVC 模式 |
| 10 | **Final Project** | 自选主题完成一个项目 |

### 🎯 在 CS 学习中的定位
- **多语言全栈入门**：一门课体验 C/Python/SQL/Web 全栈
- **Malan 的教学**：现场拆解、视觉化演示，让概念"看得见"
- **适合**：零基础小白；想快速建立 CS 全景图的人

---

## 课程 #4 · Duke University：Introductory C Programming Specialization

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Duke University（Coursera）|
| 先修 | 无 |
| 语言 | C |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | **110 小时**（重型）|
| 课程网站 | https://www.coursera.org/specializations/c-programming |

**csdiy 评价**：课名"入门"但**兼具广度和深度**。侧重基础概念，指针训练好，GDB/Valgrind 上手训练充分。

### 📑 核心教学主题（4 门子课程）

| 子课程 | 核心内容 |
|--------|---------|
| **Programming Fundamentals** | C 基础；**frame/stack/heap memory** 讲得很透 |
| **Writing/Running/Fixing Code** | 编译/链接；GDB 调试；Valgrind 内存检查 |
| **Pointers/Arrays/Strings** ⭐ | **指针深入**（C 最难部分）；数组与指针关系；字符串 |
| **Linux Tools** | Emacs/Vim；Git 基础；Linux 开发环境 |

**⚠️ 提示**：可能需要付费（Coursera），但 csdiy 评价"值得"。

---

# 第三子类 · Python（AI/数据时代的首选语言）

---

## 课程 #5 · CS50P：CS50's Introduction to Programming with Python

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Harvard |
| 主讲 | David J. Malan |
| 先修 | 无 |
| 语言 | Python |
| 难度 | 🌟🌟 |
| 学时 | 30-40 小时 |
| 课程网站(2022) | https://cs50.harvard.edu/python/2022/ |
| B站视频 | https://www.bilibili.com/video/BV1z5411X7wX |
| 资源汇总 | https://github.com/mancuoj/CS50P |

**定位**：CS50 番外篇。学 Python 基础 + 进阶语法 + **Pythonic** 编程方法。无需编程基础，平易近人。

### 📑 核心教学主题
- Python 基础语法（变量/类型/控制流/函数）
- **Pythonic 编程**（列表推导、生成器、装饰器）
- Python 特色库（标准库深入）
- 代码测试与错误处理
- 文件 I/O 与正则表达式

---

## 课程 #6 · UCB CS61A：Structure and Interpretation of Computer Programs ⭐⭐ 强推

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | 无（但零基础建议先学 CS10/CS50）|
| 语言 | **Python, Scheme, SQL**（三语言！）|
| 难度 | 🌟🌟🌟 |
| 学时 | 50 小时 |
| 课程网站 | https://cs61a.org |
| 课程教材 | https://www.composingprograms.com/（教材中文翻译 https://composingprograms.netlify.app/）|
| B站视频(2024) | https://www.bilibili.com/video/BV1sy411z7nA/ |
| 资源汇总 | https://github.com/PKUFlyingPig/CS61A |

**csdiy 评价**：这**不仅是一门编程语言课**，而是深入程序构造与运行原理。最后会用 Python 实现一个 **Scheme 解释器**。

### 📑 核心教学主题（四大主题）

| 主题 | 核心内容 |
|------|---------|
| **函数式编程** ⭐ | 高阶函数；lambda；闭包；递归与迭代 |
| **数据抽象** ⭐ | 抽象数据类型；面向对象（OOP）；继承与多态 |
| **程序解释器** ⭐⭐ | **用 Python 实现 Scheme 解释器**（Project 4，本课巅峰）——理解语言如何运行 |
| **分布式计算** | MapReduce；并行；SQL 查询 |

### 四大 Project（高质量实战）
1. **Hog**：骰子游戏（高阶函数、策略）
2. **Cats**：拼写正确性（字符串处理）
3. **Ants**：塔防游戏（OOP、状态管理）⭐
4. **Scheme Interpreter** ⭐⭐：用 Python 写 Scheme 解释器（本课巅峰，学完理解语言实现）

### 🎯 在 CS 学习中的定位
- csdiy 作者的 **Python 入门课**
- CS61 系列第一门（CS61A 抽象 → CS61B 数据结构 → CS61C 体系结构）
- **抽象是核心主题**：函数式/OOP/数据抽象让代码更模块化、易读

**⚠️ 学习建议**：零基础直接上可能吃力，建议先学 CS10 或 CS50。

---

## 课程 #7 · MIT 6.100L：Introduction to CS and Programming using Python

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT（EECS 系入门必修，2022 改革后）|
| 主讲 | **Ana Bell 教授** |
| 先修 | 无 |
| 语言 | Python |
| 难度 | 🌟🌟 |
| 学时 | 50h+ |
| 课程网站 | https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/pages/material-by-lecture/ |
| B站中文精翻 | https://www.bilibili.com/video/BV1WE421V7bL |

**定位**：MIT 6.3（CS）/6.4（AI）/6.5（EE）专业的入门必修。26 节课，难度平滑。

### 📑 核心教学主题
- 计算基本概念
- Python 编程语言
- 简单算法与数据结构
- 测试与调试 ⭐
- 算法复杂度 ⭐（Big-O 分析入门）

---

# 第四子类 · Java（企业级开发主力）

---

## 课程 #8 · MIT 6.092：Introduction To Programming In Java

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 先修 | 无 |
| 语言 | Java |
| 难度 | 🌟🌟 |
| 学时 | **< 15 小时**（7 节课，一天可完成）|
| 课程网站(IAP 2010) | https://ocw.mit.edu/courses/6-092-introduction-to-programging-in-java-january-iap-2010/pages/syllabus/ |
| 教材 | *How to Think Like a Computer Scientist*（https://greenteapress.com/wp/think-java/）|

**定位**：适合新手的 Java 快速入门。每节课 = 1h Lec + 1h Lab。

### 📑 核心教学主题（7 节）
1. Java 编译原理；Hello World；八大基础类型
2. 控制流；数组
3. **代码风格**（命名规范、缩进、空格）⭐
4. OOP 基础（类、对象、方法）
5. 继承与多态
6. **Debug**（Eclipse warning、Assertion）⭐
7. **异常处理**（Exception）⭐

**进阶建议**：学完后可接 MIT 6.031（软件构造）。

---

# 第五子类 · C++（系统/性能/竞赛的利器）

---

## 课程 #9 · Stanford CS106B/X：Programming Abstractions in C++

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 先修 | CS50/CS106A/CS61A 或同等 |
| 语言 | C++ |
| 难度 | 🌟🌟 |
| 学时 | 50-70 小时 |
| 课程网站(B) | https://web.stanford.edu/class/cs106b/ |
| 课程网站(X) | https://web.stanford.edu/class/cs106x/ |
| 教材 | https://web.stanford.edu/class/cs106x/res/reader/CS106BX-Reader.pdf |
| 视频(YouTube 2015) | https://www.youtube.com/watch?v=FIroM06V2MA&list=PL-h0BZdG_K4kAmsfvAik-Za826pNbQd0d |
| 视频(B站 2018) | https://www.bilibili.com/video/BV1G7411k7jG |

**定位**：Stanford 进阶编程课。CS106X 比 B 在难度深度上更高，但主体类似。培养**通过编程抽象解决实际问题**的能力。

### 📑 核心教学主题

| 主题 | 核心内容 |
|------|---------|
| **抽象数据类型（ADT）** | collections；封装；信息隐藏 |
| **递归** ⭐ | 递归思维；回溯；递归树 |
| **BFS/DFS** ⭐ | 广度/深度优先搜索；图遍历 |
| **排序** | 多种排序算法实现与对比 |
| **哈希** | 哈希函数；哈希表实现 |
| **指针与内存** ⭐ | 指针；链表；**stack vs heap allocation**；内存管理 |
| **BST** | 二叉搜索树；平衡树简介 |
| **OOP** | 类、继承、多态在 C++ 中的实现 |
| **Debugger 使用** | 实战排错技巧 |

### 9 个 Assignment（高质量实战，含 GUI 可视化）
- 每个 assignment 有详细文档 + starter code + GUI 展示效果
- 代表性作业：**Huffman 编码压缩文件**（最后一个 assignment）⭐

**学习建议**：推荐 YouTube spring 2015 版本（授课激情，师生互动精彩）。

---

## 课程 #10 · Stanford CS106L：Standard C++ Programming

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 先修 | 最好掌握至少一门编程语言 |
| 语言 | C++ |
| 难度 | 🌟🌟🌟 |
| 学时 | 20 小时 |
| 课程网站 | http://web.stanford.edu/class/cs106l/ |
| 教材 | http://web.stanford.edu/class/cs106l/full_course_reader.pdf |
| 视频 | https://www.youtube.com/channel/UCSqr6y-eaQT_qZJVUm_4QxQ/playlists |
| 资源汇总 | https://github.com/PKUFlyingPig/CS106L |

**csdiy 感悟**：*"我从大一直写 C++，直到学完这门课才意识到，我写的只是 C + cin/cout。"*——深入标准 C++ 特性，编写高质量代码。

### 📑 核心教学主题（现代 C++ 特性）⭐

| 主题 | 核心内容 |
|------|---------|
| **auto binding** | 类型自动推导 |
| **Uniform Initialization** | 统一初始化语法 |
| **Lambda Function** ⭐ | 匿名函数；闭包；std::function |
| **Move Semantics** ⭐⭐ | 右值引用；std::move；移动构造——**C++11 最重要的特性** |
| **RAII** ⭐ | 资源获取即初始化——C++ 资源管理的核心范式 |
| **Templates** | 模板编程；泛型；SFINAE 简介 |
| **Iterator** | 迭代器模式；自定义迭代器 |

### 两个 Assignment
1. **WikiRacer**：小游戏（页面跳转）
2. **HashMap** ⭐：实现类似 STL `unordered_map`——**串联整门课**，特别考验 iterator 实现

**定位**：Stanford 后续 CS 课程（CS144 网络、CS143 编译器）的 C++ Project 基础。

---

## 课程 #11 · AmirKabir University AP1400-2：Advanced Programming

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Amirkabir University of Technology |
| 先修 | 无 |
| 语言 | C++ |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 50 小时 |
| 课程代码 | https://github.com/courseworks |

**定位**：无意发现的宝藏 C++ 课程。**homework 质量极高**，每个独立、结构简单、单元测试完善。

### 📑 7 个 Homework
1. **Matrix 类**实现
2. **加密货币客户端/服务端**模拟 ⭐
3. **Binary Search Tree (BST)** 实现
4. **SharedPtr 和 UniquePtr** 智能指针实现 ⭐⭐（深入理解 C++ 内存管理）
5. **继承与多态**（多个类）
6. **STL 库**实战（4 个问题）
7. Python 项目（附加）

---

# 第六子类 · Rust（内存安全的系统编程新王）

> csdiy 观点：Rust 以"C 的速度 + 内存安全"在系统编程领域崛起。学 Rust 也能让你**用 C 写出更安全的系统代码**。

---

## 课程 #12 · Stanford CS110L：Safety in Systems Programming ⭐ Rust 入门首选

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 先修 | 最好有编程背景 + 对系统有初步认识 |
| 语言 | Rust |
| 难度 | 🌟🌟🌟 |
| 学时 | 30 小时 |
| 课程网站 | https://reberhardt.com/cs110l/spring-2020/ |
| 视频 | https://youtu.be/j7AQrtLevUE |
| 资源汇总 | https://github.com/PKUFlyingPig/CS110L |

**核心主题**：Rust 语言 + **并发编程**。

### 📑 核心教学主题

| 主题 | 核心内容 |
|------|---------|
| **Rust 基础** ⭐ | 所有权（Ownership）；借用（Borrowing）；生命周期（Lifetime）|
| **Rust 类型系统** | 泛型；Trait；错误处理（Result/Option）|
| **并发基础** ⭐ | 多进程；多线程；基于事件驱动的并发 |
| **Futures** ⭐ | Rust 的异步编程模型（async/await 基础）|

### 2 个高质量 Project
1. **用 Rust 实现 GDB 式 debugger** ⭐
2. **用 Rust 实现负载均衡器** ⭐

**学习建议**：清华 rCore 操作系统实验也用 Rust，参见 https://rcore-os.github.io/rCore-Tutorial-Book-v3/index.html

---

## 课程 #13 · KAIST CS220：Programming Principles

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | KAIST（Jeehoon Kang 教授，Rust 拥趸）|
| 先修 | 一门编程语言 |
| 语言 | Rust |
| 难度 | 🌟🌟🌟 |
| 学时 | 40 小时 |
| 课程网站 | https://github.com/kaist-cp/cs220 |
| 教材 | 推荐 [Rust Book](https://doc.rust-lang.org/book/) + [slides](https://docs.google.com/presentation/d/17G3SwkE_tq0H3lTt9N0ysIbHhqDZBfHkoWD5LwwAKSo/edit) |

**定位**：CS110L 的**习题补充**。完善测试系统，适合作为 Rust 练手课。

---

## 课程 #14 · KAIST CS431：Concurrent Programming

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | KAIST |
| 先修 | Rust 基础 + 并发初步了解 |
| 语言 | Rust |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 50 小时 |
| 课程网站 | https://github.com/kaist-cp/cs431 |
| 视频 | https://www.youtube.com/playlist?list=PL5aMzERQ_OZ9j40DJNlsem2qAGoFbfwb4 |

**核心主题**：**并发编程的深度课程**——比预期深得多。

### 📑 核心教学主题

| 主题 | 核心内容 |
|------|---------|
| **并发编程模型** ⭐ | 理论建模；promising semantics；**访存模型**（memory model）|
| **锁机制** ⭐ | 自旋锁、互斥锁的实现原理 |
| **无锁数据结构** ⭐⭐ | 无锁哈希表；**hazard pointer**；lock-free 编程 |
| **Rust 并发库** | 锁与无锁数据结构的实现剖析 |

### 高质量作业（代码量不大但不简单）
- 基于锁的并发安全缓存
- 基于锁的并发链表
- 无锁哈希表 ⭐
- hazard pointer 实现 ⭐

---

# 第七子类 · 函数式编程（思维范式的升级）

---

## 课程 #15 · Cornell CS3110：OCaml Programming ⭐⭐ "modern SICP"

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Cornell |
| 主讲 | **Michael Ryan Clarkson**（表述清晰、剖析一针见血）|
| 先修 | 了解一门命令式语言（类 C）|
| 语言 | OCaml |
| 难度 | 🌟🌟🌟 |
| 学时 | 40 小时 |
| 视频YouTube | https://www.youtube.com/playlist?list=PLre5AT9JnKShBOPeuiD9b-I4XROIJhkIU |
| 视频B站 | https://www.bilibili.com/video/BV1dv4y127Ui/ |
| 教材 | https://cs3110.github.io/textbook |

**csdiy 评价**：*"如果说编程入门最好的课是 SICP，在其之后就是 CS3110。"*——**modern SICP**，打磨 20 余年的经典。

### 📑 核心教学主题（理论 + 实用充分结合）

| 主题 | 核心内容 |
|------|---------|
| **OCaml 语言基础** ⭐ | 类型推断；模式匹配；不可变性 |
| **数据结构与算法** | 用函数式方式实现经典数据结构 |
| **测试开发** ⭐ | 单元测试；随机测试；规范 |
| **形式证明** ⭐ | 用 Coq/数学证明程序正确性——**其他入门课罕见** |
| **语言特性实现** | 解释器实现；类型检查器实现 |

### 课程简史
- 源自 MIT 6.001 SICP
- 2008 年改用 OCaml，命名 CS3110
- 2018 年编写[教材](https://cs3110.github.io/textbook)
- 2021 年 YouTube 公开[视频](https://www.youtube.com/playlist?list=PLre5AT9JnKShBOPeuiD9b-I4XROIJhkIU)

---

## 课程 #16 · University of Helsinki：Haskell MOOC

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | University of Helsinki |
| 先修 | 无 |
| 语言 | Haskell |
| 难度 | 🌟🌟 |
| 课程网站 | https://haskell.mooc.fi/ |
| 作业仓库 | https://github.com/moocfi/haskell-mooc |
| 社区 | https://t.me/haskell_mooc_fi |

**核心主张**：学 Haskell 但**重点不在语言，而在函数式编程思想**——理解 Java Streams / JS Promises 等特性背后的设计思想。

### 📑 核心教学主题（函数式核心思想）
- **Pure Function**（纯函数，无副作用）
- **Lazy Evaluation**（惰性求值）
- **Strongly Typed**（强类型）
- **Type Inferred**（类型推断）
- **Curry**（柯里化）
- **Monoid / Functor / Monad / Applicative** ⭐（函数式的"魔咒"概念）

**学习建议**：有编程经验的话 Part1 简单，**难度集中在 Part2 第十三章之后**。练习质量高，提交后有标准答案。

---

# 🎯 编程入门 · 选课指南（按目标方向）

## 🎓 套餐 A：零基础小白入门
```
CS50(#3) → MIT-Missing-Semester(#1) → CS50P(#5) 或 MIT 6.100L(#7)
```
- CS50 建立全景图 + Missing Semester 掌握工具链 + Python 课深入一门语言

## 🎓 套餐 B：CS 专业系统入门（csdiy 推荐）
```
Missing-Semester(#1) → CS61A(#6) ⭐ → CS106B(#9)
```
- CS61A 是 csdiy 作者的 Python 入门课（强推）
- CS61A 之后可直接接 CS61B（数据结构）→ CS61C（体系结构）

## 🎓 套餐 C：系统编程方向（C/C++/Rust）
```
CS50(#3) → Duke C(#4) 或 CS106B(#9) → CS106L(#10) → CS110L(#12 Rust)
```
- C/C++ 打底 → 现代 C++ → Rust 内存安全

## 🎓 套餐 D：函数式思维升级
```
CS61A(#6) → CS3110(#15 OCaml) 或 Haskell MOOC(#16)
```

## 🎓 套餐 E：AI/数据方向（Python 优先）
```
CS50P(#5) 或 MIT 6.100L(#7) → CS61A(#6) → 进阶数据结构/算法
```

---

## ⚠️ 关键提醒

1. **Missing Semester 必学**：10 小时换一辈子的效率，所有 CS 学生的底层依赖。
2. **CS61A 不是简单 Python 课**：它深入程序构造原理，最后实现 Scheme 解释器——**csdiy 最强推的入门课**。
3. **CS50 多语言全栈**：一门课体验 C/Python/SQL/Web，适合建立全景图。
4. **C++ 学两门**：CS106B（抽象/算法）+ CS106L（现代 C++ 特性），缺一不可。
5. **Rust 是趋势**：学 Rust 不仅为用 Rust，更能让你用 C 写出更安全的系统代码。
6. **函数式正在融入主流**：Java Streams、JS Promises、React Hooks 都基于函数式思想——学一门函数式课能"降维打击"。

---

## 📚 按课程编号索引

| # | 课程 | 语言 | 难度 | 学时 | 先修 |
|---|------|------|------|------|------|
| 1 | MIT-Missing-Semester | Shell | 🌟🌟 | 10h | 无 |
| 2 | UCB DeCal | Shell | 🌟🌟🌟 | 20h | 无 |
| 3 | Harvard CS50 | C/Py/SQL/JS | 🌟🌟 | 20h | 无 |
| 4 | Duke Intro C | C | 🌟🌟🌟🌟 | 110h | 无 |
| 5 | CS50P | Python | 🌟🌟 | 30-40h | 无 |
| 6 | UCB CS61A ⭐ | Py/Scheme/SQL | 🌟🌟🌟 | 50h | 无(建议先CS50) |
| 7 | MIT 6.100L | Python | 🌟🌟 | 50h+ | 无 |
| 8 | MIT 6.092 | Java | 🌟🌟 | <15h | 无 |
| 9 | Stanford CS106B/X | C++ | 🌟🌟 | 50-70h | CS基础 |
| 10 | Stanford CS106L | C++ | 🌟🌟🌟 | 20h | 一门语言 |
| 11 | AmirKabir AP1400 | C++ | 🌟🌟🌟🌟🌟 | 50h | 无 |
| 12 | Stanford CS110L ⭐ | Rust | 🌟🌟🌟 | 30h | 编程+系统基础 |
| 13 | KAIST CS220 | Rust | 🌟🌟🌟 | 40h | 一门语言 |
| 14 | KAIST CS431 | Rust | 🌟🌟🌟🌟 | 50h | Rust+并发 |
| 15 | Cornell CS3110 ⭐ | OCaml | 🌟🌟🌟 | 40h | 命令式语言 |
| 16 | Helsinki Haskell | Haskell | 🌟🌟 | 因人 | 无 |

---

**文档版本**：v1.0 完整版
**数据来源**：csdiy.wiki 课程详情 + 课程官网 + 学科知识
**最后更新**：2026-07-07
