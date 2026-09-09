# CSdiy 系统类课程完全解析（体系结构 + 系统基础 + 操作系统 + 并行分布式）

> 本文档覆盖 csdiy 课程地图中系统类的四大类，共 12 门课程。
> 数据来源：csdiy.wiki 课程详情 + 课程官网 + 学科知识。

---

# 第一大类 · 体系结构（4 门）

> **csdiy 观点**：从 01 开始理解计算机。"计算机的世界由 01 构成"——建立对整个计算机体系的鸟瞰图。

---

## 课程 #1 · Coursera: Nand2Tetris ⭐ 零基础造计算机

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | 希伯来大学（Coursera）|
| 先修 | **无**（面向零基础，目标让高中生都能理解）|
| 语言 | 任选 |
| 难度 | 🌟🌟🌟 |
| 学时 | 40 小时 |
| Nand2Tetris I | https://www.coursera.org/learn/build-a-computer/home/week/1 |
| Nand2Tetris II | https://www.coursera.org/learn/nand2tetris2/home/welcome |
| 教材 | *计算机系统要素：从零开始构建现代计算机* |
| 资源汇总 | https://github.com/PKUFlyingPig/NandToTetris |

**csdiy 评价**：Coursera 满分课程，全球 400+ 高校采用。**从与非门开始造一台计算机，并在上面运行俄罗斯方块**。

### 📑 核心教学主题（硬件 + 软件两大部）

**Part I（硬件）**：
- 用与非门构造逻辑电路
- 逐步搭建 ALU → CPU
- 运行课程自定义的简易汇编

**Part II（软件）**：
- 编写编译器（Jack 高级语言 → 字节码 → 汇编）
- 开发简易 OS（支持 I/O 和图形界面）
- **用 Jack 开发俄罗斯方块，运行在你造的 CPU 上** ⭐

**特点**：麻雀虽小五脏俱全，提取计算机本质，不陷于现代计算机复杂细节。

---

## 课程 #2 · UCB CS61C：Great Ideas in Computer Architecture ⭐ csdiy 最爱

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley（CS61 系列最后一门）|
| 先修 | CS61A, CS61B |
| 语言 | **C** |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | https://cs61c.org/ |
| B站(Su20) | https://www.bilibili.com/video/BV1fC4y147iZ/ |
| 资源汇总 | https://github.com/PKUFlyingPig/CS61C-summer20 |

**csdiy 评价**：*"这是我个人上过的最好的计算机体系结构课程。"* 深入硬件细节，理解 C → RISC-V 汇编 → CPU 执行的全过程。

### 📑 核心教学主题 + 4 大 Project

| 主题 | 核心内容 |
|------|---------|
| **C 语言深入** | 指针、内存管理 |
| **汇编（RISC-V）** ⭐ | C → 汇编转换；调用约定 |
| **CPU 设计** | 流水线；数据通路 |
| **Cache** ⭐ | 局部性；缓存层次；命中率分析 |
| **虚拟内存** ⭐ | 页表；TLB；缺页处理 |
| **并发** | 线程；锁；数据竞争 |

**4 大 Project（CS61C 亮点）**：
1. **Project 1**：用 C 写小游戏（如 *Game of Life*）
2. **Project 2** ⭐：用 RISC-V 汇编编写**神经网络识别 MNIST**（极致锻炼汇编理解）
3. **Project 3** ⭐：用 Logisim 搭建**二级流水线 CPU**，运行 RISC-V 汇编
4. **Project 4**：用 OpenMP/SIMD 并行优化矩阵运算（实现简易 NumPy）

**定位**：UCB 是 RISC-V 架构发源地，体系结构领域首屈一指。

---

## 课程 #3 · ETH Zurich：Digital Design and Computer Architecture (DDCA)

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | ETH Zurich |
| 主讲 | **Onur Mutlu**（体系结构大牛）|
| 先修 | CS50 或同等，最好有 C 基础 |
| 语言 | C, Verilog, MIPS 汇编, LC3 汇编 |
| 难度 | 🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站(2023) | https://safari.ethz.ch/digitaltechnik/spring2023/ |
| YouTube | https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrloMa2fUYWPGiZUBQo2 |
| 教材 | *Digital Design and Computer Architecture* (Harris & Harris, MIPS Edition)|

**定位**：从计算机设计角度出发，从晶体管/逻辑门到微架构/缓存/虚拟内存，还介绍**最新研究进展**。

### 📑 核心教学主题 + 9 个 Lab
- 组合电路 + 时序电路
- Verilog 硬件描述语言
- MIPS 单周期/多周期/流水线 CPU 设计与性能分析
- 缓存、虚拟内存
- 使用 **Basys 3 FPGA 开发板** + Vivado 软件
- 9 个 Lab 从零设计 MIPS CPU

---

## 课程 #4 · ETH Zurich：Computer Architecture (CA)

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | ETH Zurich |
| 主讲 | **Onur Mutlu** |
| 先修 | DDCA |
| 语言 | C/C++, Verilog |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 70h+ |
| 课程网站 | https://safari.ethz.ch/architecture/fall2022/doku.php?id=start |

**定位**：DDCA 的进阶。**难度高于 CS61C**，内容前沿，相当于听一学期讲座。

### 📑 核心教学主题（前沿研究导向）
- **内存系统**：DRAM、新型非易失性内存、内存控制器、闪存
- **存内计算（Processing-in-Memory）** ⭐
- **并行计算**：多核、一致性、GPU
- **异构计算**
- **互联网络**
- **专用系统**：图分析、生物信息、机器学习 ⭐
- 5 个 Project（多与内存和 cache 相关），Verilog 设计类 MIPS 流水线处理器

---

# 第二大类 · 计算机系统基础（2 门）

> **csdiy 观点**：在深入某个细分领域前，对系统宏观理解 + 通用设计原则的把握，让你后续不断强化最核心乃至哲学的概念。

---

## 课程 #5 · CMU 15-213: CSAPP ⭐⭐ 镇系神课

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | CMU |
| 先修 | CS61A, CS61B |
| 语言 | **C** |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | **150 小时**（重型）|
| 课程网站 | http://csapp.cs.cmu.edu/ |
| B站视频 | https://www.bilibili.com/video/BV1iW411d7hd |
| 中文讲解(九曲阑干) | https://www.bilibili.com/video/BV1cD4y1D7uR |
| 教材 | *Computer Systems: A Programmer's Perspective, 3/E*（Bryant，CMU 计算机系主任）|
| Lab 代码框架 | http://csapp.cs.cmu.edu/3e/labs.html |

**csdiy 评价**：CMU **大名鼎鼎的镇系神课**，以内容庞杂、Project 巨难闻名。覆盖汇编、体系结构、OS、编译链接、并行、网络，**兼具深度和广度**。

### 📑 核心教学主题 + 11 个 Lab

| 主题 | 核心内容 |
|------|---------|
| **信息的位级表示** | 整数/浮点编码；位运算技巧 |
| **程序的机器级表示** ⭐ | 汇编；栈帧；控制结构 |
| **处理器架构** | 流水线；指令执行 |
| **优化程序性能** | 编译器优化；循环展开 |
| **存储器层次** ⭐ | Cache 原理；局部性利用；cache-friendly 代码 |
| **链接** ⭐ | 静态/动态链接；ELF 文件；共享库 |
| **异常控制流** ⭐ | 进程；信号；非本地跳转 |
| **虚拟内存** ⭐⭐ | 地址翻译；页表；内存映射 |
| **动态内存分配** | malloc/free 实现 |
| **系统级 I/O** | 文件；Unix I/O |
| **网络编程** | socket；客户端/服务器 |
| **并发编程** ⭐ | 线程；同步；锁 |

### 11 个 Lab（业界闻名，全部开源）⭐
- **Data Lab**：位运算难题
- **Bomb Lab** ⭐⭐：拆弹（逆向工程汇编，最经典）
- **Attack Lab**：代码注入攻击
- **Arch Lab**：流水线优化
- **Cache Lab**：实现缓存模拟器
- **Tsh Lab**：实现 Unix shell
- **Malloc Lab** ⭐：实现自己的 malloc（最难之一）
- **Proxy Lab**：实现 Web 代理

**csdiy 警告**：Project 答案网上唾手可得，但**想锻炼代码能力就不要借鉴**。认真学完对计算机系统的理解绝对上升一个台阶。

---

## 课程 #6 · Stanford CS110：Principles of Computer Systems

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 先修 | 编程基础、Unix、GDB、Valgrind |
| 语言 | C/C++ |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 150 小时 |
| 课程网站(winter20) | https://web.stanford.edu/class/archive/cs/cs110/cs110.1204/ |
| 视频(spring19) | https://www.youtube.com/playlist?list=PLai-xIlqf4JmTNR9aPCwIAOySs1GOm8sQ |
| 教材 | CSAPP（同 CSAPP）|
| 资源汇总 | https://github.com/xuzheng465/Stanford_CS110 |

**定位**：在 CS107 基础上深入研究系统和程序构建。专注**大型系统设计、跨机器软件、并行计算**。

### 📑 核心教学主题
- 程序如何映射到系统组件
- 程序行为与执行理解
- 大型系统设计与权衡
- 跨多台机器的软件
- 单机并行任务

**作业**：7 labs + 8 assignments，每周 lab 给项目增加新功能，配有完整测试框架。

---

# 第三大类 · 操作系统（4 门）⭐ csdiy 灵魂

> **csdiy 观点**：*"没有什么能比自己写个内核更能加深对操作系统的理解了。"* 做系统不是靠 PPT 念出来的，是几万行代码一点点累起来的。

---

## 课程 #7 · MIT 6.S081：Operating System Engineering ⭐ 强推

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT PDOS 实验室 |
| 先修 | 体系结构 + 扎实 C + RISC-V 汇编 |
| 语言 | C, RISC-V |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 150 小时 |
| 课程网站(2021) | https://pdos.csail.mit.edu/6.828/2021/schedule.html |
| YouTube | https://www.youtube.com/watch?v=L6YqHxYHa7A |
| 中文翻译文档 | https://mit-public-courses-cn-translatio.gitbook.io/mit6-s081/ |
| 教材（xv6 book）| https://pdos.csail.mit.edu/6.828/2021/xv6/book-riscv-rev2.pdf |
| 资源汇总 | https://github.com/PKUFlyingPig/MIT6.S081-2020fall |

**csdiy 评价**：MIT PDOS 实验室出品，前身是著名的 6.828。教授之一 **Robert Morris** 曾是顶尖黑客，世界上第一个蠕虫病毒 Morris 出自他手。

**核心特色**：基于 RISC-V 的教学操作系统 **xv6**（比 x86 的 JOS 更轻便，专注 OS 层面开发）。教授专门写了[教程](https://pdos.csail.mit.edu/6.828/2021/xv6/book-riscv-rev2.pdf)。

### 📑 核心教学主题 + 11 个 Lab

| 主题 | 核心内容 |
|------|---------|
| **OS 基础** | 系统调用；用户态/内核态 |
| **页表与虚拟内存** ⭐ | RISC-V Sv39 页表 |
| **陷阱与中断** | 陷入内核；上下文切换 |
** ** traps, system calls** |  |
| **进程调度** | 时间片；调度算法 |
| **锁与并发** ⭐ | 自旋锁；睡眠锁；死锁 |
| **文件系统** ⭐ | inode；日志；目录 |
| **网络与套接字** | 网络栈 |
| **经典论文精读** ⭐ | 后半程读 OS 领域经典论文 |

**11 个 Lab（在 xv6 上增加新机制，每周一个，测试框架完善）**：
- 系统调用、页表、陷阱、copy-on-write、多线程、锁、网络、文件系统等

---

## 课程 #8 · UCB CS162：Operating System ⭐ Pintos（最难）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS61A/B/C，扎实 C + GDB |
| 语言 | C, x86 汇编 |
| 难度 | 🌟🌟🌟🌟🌟🌟（超满星）|
| 学时 | **200 小时+，上不封顶** |
| 课程网站 | https://cs162.org/ |
| B站(2022Spring) | https://www.bilibili.com/video/BV1L541117gr |
| 教材 | *Operating Systems: Principles and Practice (2nd Edition)*（四卷，深入浅出）|
| Pintos 文档（北大） | https://pkuflyingpig.gitbook.io/pintos |

**csdiy 评价**：csdiy 作者（北大 2022/2023 OS 实验班助教）引入并改善了 Pintos Project。**与 xv6 小而精不同，Pintos 更注重 Design and Implementation**。

### 📑 核心教学主题 + 3 大 Project（Pintos）

**教材亮点**：*OSPP* 四卷写得很深入浅出，生动甚至幽默，弥补 MIT6.S081 理论空白。

**3 个 Project（Pintos，每个学生留很大设计空间，总代码量 ~2000 行，人均耗时 40h+）**：
1. **User Programs**：参数解析传递；进程系统调用（fork 等）；文件系统调用
2. **Threads** ⭐：timer_sleep；严格优先级调度；多线程支持；简化版 pthread
3. **File Systems** ⭐：Buffer Cache；可扩容文件；子目录

**6 个 Homework**（工作量等同其他课的 Project）：
- List, Shell（重定向/管道/信号）, HTTP 服务器, Memory（malloc 实现）, MapReduce

**定位**：Stanford、Berkeley、JHU 等顶尖名校都用 Pintos。本科阶段能设计、实现、debug 一个大型系统是非常珍贵的经历。

---

## 课程 #9 · NJU OS：蒋炎岩（中文首选）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | 南京大学（蒋炎岩老师）|
| 先修 | 体系结构 + 扎实 C |
| 语言 | C |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 150 小时 |
| 课程网站 | https://jyywiki.cn/OS/2022/index.html |
| B站视频 | https://space.bilibili.com/202224425/channel/collectiondetail?sid=192498 |
| 教材 | *OSTEP*（http://pages.cs.wisc.edu/~remzi/OSTEP/）|

**csdiy 评价**：csdiy 收录的**第一门国内高校自主开设的计算机课程**。蒋老师有丰富一线代码经验，**Hacker 风格**，课上"一言不合"就在命令行写代码。

### 教学特色（独此一家）
- **"程序就是状态机"** 视角 → 并发程序状态机转化模型
- OS = 一系列对象（进程/地址空间/文件/设备）+ API（系统调用）
- 可持久化：从 1-bit 存储介质 → 各类存储设备 → 设备驱动 → 文件系统
- 培养**阅读源码、查阅手册**的能力

### 作业体系
- **5 个 MiniLab**（可本地测试）
- **4 个 OSLab**（评测机不对外开放）

---

## 课程 #10 · HIT OS：李治军（中文经典）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | 哈尔滨工业大学（李治军老师）|
| 先修 | C 语言 |
| 语言 | C, 汇编 |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 100h+ |
| 课程网站 | https://www.icourse163.org/course/HIT-1002531008 |
| B站视频 | https://www.bilibili.com/video/BV19r4y1b7Aw/ |
| 教材 | 《Linux 内核完全注释》+《操作系统原理、实现与实践》|
| 实验 | https://www.lanqiao.cn/courses/115 |

**csdiy 评价**：知乎"操作系统推荐"高赞常客。**站在学生角度循循善诱**，基于 **Linux 0.11 源码**（约 2 万行）。

### 📑 核心教学主题
- 从"什么是操作系统"引入
- CPU 管理 → 进程
- 内存管理
- 文件系统
- 设备驱动

**8 个小实验 + 4 个大实验**（基于 Linux 0.11）

---

# 第四大类 · 并行与分布式系统（2 门）

> **csdiy 观点**：摩尔定律终结，多核/众核如日中天。深度学习对算力/存储需求达前所未有高度，**大规模集群部署成为热门**。

---

## 课程 #11 · CMU 15-418 / Stanford CS149：Parallel Computing ⭐

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | CMU + Stanford |
| 主讲 | **Kayvon Fatahalian** |
| 先修 | 体系结构，熟悉 C++ |
| 语言 | C++ |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 150 小时 |
| CMU15418 | https://www.cs.cmu.edu/afs/cs/academic/class/15418-s18/www/index.html |
| CS149 | https://gfxcourses.stanford.edu/cs149/fall21 |
| 资源汇总 | https://github.com/PKUFlyingPig/CS149-parallel-computing |

**定位**：深入理解现代并行计算架构的**设计原则与必要权衡**，学会利用硬件 + 软件框架（CUDA/MPI/OpenMP）编写高性能并行程序。

**csdiy 建议**：15-418 内容更丰富有回放，CS149 作业更 fashion。推荐看 15-418 视频 + 做 CS149 作业。

### 📑 核心教学主题 + 5 个 Project

| 主题 | 核心内容 |
|------|---------|
| **并行硬件** | 多核；SIMD；GPU；多处理器 |
| **并行软件** | 多线程；数据并行；任务并行 |
| **同步** | 锁；无锁；事务内存 |
| **CUDA 编程** ⭐ | GPU 编程模型 |
| **MPI** | 分布式内存并行 |
| **OpenMP** | 共享内存并行 |
| **Spark** ⭐ | 大数据并行框架 |
| **性能分析** | roofline 模型；瓶颈分析 |

**5 个编程作业**：分析并行瓶颈；多线程同步；CUDA；OpenMP；Spark

---

## 课程 #12 · MIT 6.824：Distributed System ⭐⭐ 分布式神课

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT PDOS 实验室 |
| 主讲 | **Robert Morris**（Morris 蠕虫病毒作者）|
| 先修 | 体系结构 + 操作系统 + 扎实 Go 语言 |
| 语言 | **Go** |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 150 小时 |
| 课程网站 | https://pdos.csail.mit.edu/6.824/ |

**csdiy 评价**：和 6.S081 一样出品自 MIT PDOS。每节课精读一篇**分布式系统经典论文**，传授设计与实现的重要原则和关键技术。

### 📑 核心教学主题 + 4 个 Project

| 主题 | 核心内容 |
|------|---------|
| **分布式基础** | 一致性；容错；CAP |
| **RPC** | 远程过程调用 |
| **Raft 共识算法** ⭐⭐ | 领导选举；日志复制；安全性 |
| **分布式事务** | 两阶段提交；MVCC |
| **容错与备份** | 复制状态机 |
| **一致性模型** | 线性一致性；因果一致性 |
| **经典论文** ⭐ | MapReduce、GFS、Spanner 等 |

**4 个 Project（以难度闻名，基于 Raft 实现分布式 KV-store）** ⭐⭐：
1. MapReduce
2. Raft（领导选举 + 日志复制）
3. Raft（持久化 + 快照）
4. 分片 KV-store

**csdiy 警告**：在痛苦的 debug 中体会并行与分布式带来的随机性和复杂性。

---

# 📊 系统类课程总结（12 门）

| 大类 | 课程数 | 核心课 | 亮点 |
|------|--------|--------|------|
| 体系结构 | 4 | CS61C(#2) | 从与非门到 CPU（N2T），RISC-V（CS61C）|
| 系统基础 | 2 | **CSAPP(#5)** | 11 个经典 Lab（Bomb/Malloc 等）|
| 操作系统 | 4 | **MIT6.S081(#7)** + CS162(#8) | xv6 11 Lab / Pintos 3 大 Project |
| 并行分布式 | 2 | **MIT6.824(#12)** | Raft 分布式 KV-store |

## 选课套餐

### 系统入门（必经之路）
```
Nand2Tetris(#1) → CS61C(#2) → CSAPP(#5)
```

### 操作系统（四选一/二）
```
MIT 6.S081(#7) ⭐ 强推（xv6，11 Lab，完善测试）
NJU OS(#9) 中文首选（蒋炎岩，Hacker 风格）
CS162(#8) 最难（Pintos，Design 导向）
HIT OS(#10) 中文经典（李治军，Linux 0.11）
```

### 并行分布式
```
CS149(#11) → MIT 6.824(#12) ⭐
```

### 中文学习路径
```
CS61C(英) 或 DDCA(英) → NJU OS(中) 或 HIT OS(中) → MIT 6.824(英)
```

## ⚠️ 关键提醒

1. **CSAPP 是系统课的基石**：150 小时但回报极高，11 个 Lab（尤其 Bomb/Malloc）是业界传奇
2. **操作系统四门各有侧重**：6.S081（xv6 实战）/ CS162（Pintos 设计）/ NJU（视角独特）/ HIT（中文友好）
3. **MIT 6.824 难度极大**：4 个 Project 在痛苦 debug 中理解分布式
4. **先修严格**：系统课层层递进，跳级会很痛苦

---

**文档版本**：v1.0
**最后更新**：2026-07-07
