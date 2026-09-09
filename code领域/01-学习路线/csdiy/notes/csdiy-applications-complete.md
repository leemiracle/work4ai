# CSdiy 应用层课程完全解析（系统安全 + 计算机网络 + 数据库系统）

> 本文档覆盖 csdiy 课程地图中三大应用类，共 15 门课程。
> 数据来源：csdiy.wiki 课程详情 + 课程官网 + 学科知识。

---

# 第一大类 · 系统安全（6 门）

> **csdiy 观点**：现实是成为黑客道阻且长。掌握理论后，还需在实践中培养"黑客素养"。

---

## 课程 #1 · UCB CS161：Computer Security ⭐ 综合性最强

| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS61A/B/C |
| 语言 | C, Go |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 150h |
| 网站 | https://su20.cs161.org/ |
| 教材 | https://textbook.cs161.org/ |
| 作业 | 7 HW + 3 Lab + 3 Project |

### 📑 五大核心主题
1. **Security principles**：如何设计安全系统
2. **Memory safety**：**缓冲区溢出攻击** ⭐
3. **Cryptography**：对称/非对称加密、MAC、数字签名
4. **Web**：SQL 注入、XSS、XSRF
5. **Networking**：各层攻击

**Project 2 亮点** ⭐：用 Go 设计实现**安全的文件分享系统**（3k+ 行代码，csdiy 作者花了整整三天）

---

## 课程 #2 · MIT 6.858：Computer System Security

| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 先修 | 体系结构 + 系统基础 |
| 语言 | C, Python |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 150h |
| 网站 | http://css.csail.mit.edu/6.858/2022/ |
| 作业 | 4 Lab + Final Project |

### 📑 核心 Lab（基于 Zoobar Web App）
- **Lab 1**：缓冲区溢出攻击破坏 Zoobar
- **Lab 2**：权限分离改进 Zoobar
- **Lab 3** ⭐：基于**符号执行**的程序分析工具（找 Python bug）
- **Lab 4**：防御浏览器攻击
- **Final Project**：实现 [SecFS](https://github.com/mit-pdos/secfs-skeleton)（不可信服务器上的安全文件系统，参考 SUNDR 论文）

---

## 课程 #3 · SU SEEDLabs ⭐ 实践环境最完善

| 字段 | 内容 |
|------|------|
| 开课 | 雪城大学（NSF 130 万美元资助）|
| 先修 | 无 |
| 语言 | C, 汇编 |
| 难度 | 🌟🌟🌟🌟 | 学时 | 150h |
| 网站 | https://seedsecuritylabs.org/index.html |
| 讲义 | https://github.com/seed-labs/seed-labs |

**csdiy 评价**：全球 **1050 家研究机构**使用。理论 + 实践并重，开源讲义 + 视频 + 教科书 + **开箱即用的 VM/Docker 攻防环境**。

### 📑 覆盖主题
软件安全、网络安全、Web 安全、操作系统安全、移动应用安全。**40+ 个 Lab**，环境可由定制 VM 和 Docker 快速搭建。

---

## 课程 #4 · ASU CSE365：Introduction to Cybersecurity（CTF 导论）

| 字段 | 内容 |
|------|------|
| 开课 | Arizona State University |
| 先修 | 无 |
| 语言 | C, Python, x86 汇编 |
| 难度 | 🌟🌟🌟🌟 |
| 网站 | https://pwn.college/cse365-s2025/ |
| 作业 | 8 模块（444 个 challenges）|

### 📑 核心主题（CTF 形式，难度递增）
- Program Misuse（Linux 命令行、权限提升）
- Web fundamentals（HTTP、server、intercept）
- Assembly（寄存器、内存、控制流）
- Cryptography（对称/非对称、哈希、信任）
- Web security（Command/HTML/SQL/Stack 注入）

---

## 课程 #5 · ASU CSE466：Computer Systems Security（CTF 进阶）

| 字段 | 内容 |
|------|------|
| 开课 | ASU |
| 先修 | 无 |
| 语言 | C, Python, x86 汇编 |
| 难度 | 🌟🌟🌟🌟🌟 |
| 网站 | https://dojo.pwn.college/cse466/ |
| 作业 | 13 模块（358 个 challenge）|

### 📑 核心主题（更深入的 CTF）
- Linux commandline（Program misuse、interaction）
- **Shellcoding**（汇编、shellcode 注入、防御）
- **Reverse Engineering**（函数帧、静态/动态逆向）
- **Program Exploitation**（hijacking to shellcode、JIT spray）
- **System Exploitation**（内核模块、权限提升）⭐ 最难
- Miscellaneous（沙箱、内存错误、竞态条件）

---

## 课程 #6 · MIT 6.1600：Foundations of Computer Security（MIT 本科）

| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 先修 | 离散数学 + 编程 + 系统基础 |
| 语言 | Python3 |
| 难度 | 🌟🌟🌟 | 学时 | 50h |
| 网站 | https://61600.csail.mit.edu/2023/ |
| 资源 | https://github.com/PKUFlyingPig/MIT6.1600 |
| 作业 | 6 个实验 |

### 📑 五大模块
1. **Authentication**：如何证明"你"是"你"
2. **Transport security**：通信加密/解密、密钥交换
3. **Platform security**：运行平台安全
4. **Software security**：代码本身安全
5. **Human/End-user security**：隐私安全（社会学层面）

---

# 第二大类 · 计算机网络（4 门）

> **csdiy 观点**：*"没有什么能比自己写个 TCP/IP 协议栈更能加深对计算机网络的理解了。"*

---

## 课程 #7 · Stanford CS144：Computer Network ⭐⭐ 强推

| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 主讲 | **Nick McKeown**（网络界巨擘，学界业界双巨佬）|
| 先修 | 系统基础, CS106L |
| 语言 | **C++** |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 100h |
| 网站 | https://cs144.github.io/ |

**csdiy 评价**：*"与其说是计算机网络课，我更愿意称其为一门年轻人最好的现代 C++ 入门课。"*——8 个 checkpoint 循序渐进搭建**整个 TCP/IP 协议栈**。

### 📑 8 个 Checkpoint（搭建完整 TCP/IP）⭐⭐
| CP | 核心内容 |
|----|---------|
| 0 | webget 网络爬虫 + In-Memory Reliable Byte Stream |
| 1-3 | **实现 TCP Protocol**（Sender/Receiver，可与工业级 TCP 互通）⭐⭐ |
| 4 | 用自己实现的 TCP 替换内核 TCP（TCPMinnowSocket）|
| 5 | 实现 **NetworkInterface**（ARP 协议）⭐ |
| 6 | 实现 **IP Router**（IP Datagram 转发）|
| 7 | 端到端串联，通过中继服务器实现实时通信 ⭐ |

**亮点**：每章末采访业界高管/学界高人，开阔眼界。

---

## 课程 #8 · UCB CS168：Introduction to the Internet

| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS61B（推荐 CS61C）+ Python + Unix |
| 语言 | Python, Unix shell |
| 难度 | 🌟🌟🌟 | 学时 | 140h |
| 网站 | https://sp25.cs168.io/ |
| 教材 ⭐ | https://textbook.cs168.io/（写得极好，简洁生动）|
| 资源 | https://github.com/PKUFlyingPig/UCB-CS168 |

### 📑 核心教学主题
分层结构、寻址、域内/域间路由、可靠传输、拥塞控制、TCP/UDP/IP/DNS/HTTP、以太网、无线。

**3 个 Python Project**：Traceroute、路由、TCP 传输（相对简单）。

---

## 课程 #9 · Computer Networking: A Top-Down Approach（经典教材）

| 字段 | 内容 |
|------|------|
| 作者 | Jim Kurose & Keith Ross（马萨诸塞大学）|
| 先修 | 系统基础 |
| 难度 | 🌟🌟🌟 | 学时 | 40h |
| 网站 | https://gaia.cs.umass.edu/kurose_ross/index.php |
| 视频 | https://gaia.cs.umass.edu/kurose_ross/lectures.php |
| 作业 | WireShark 抓包 Lab |

**定位**：经典教材，配套在线课程 + 视频 + 交互测试 + WireShark Lab。**无硬核编程作业**（CS144 可弥补）。

### 📑 自顶向下结构（应用层→物理层）
- 应用层（HTTP/DNS）
- 传输层（TCP/UDP/拥塞控制）⭐
- 网络层（IP/路由）
- 链路层（以太网/ARP）
- 物理层

---

## 课程 #10 · USTC 计算机网络（中文经典）⭐ 中文首选

| 字段 | 内容 |
|------|------|
| 开课 | 中国科学技术大学（郑烇、杨坚）|
| 先修 | 操作系统（非必需）|
| 难度 | 🌟🌟🌟 | 学时 | 40h |
| 网站 | http://staff.ustc.edu.cn/~qzheng/teaching.html |
| B站 | https://www.bilibili.com/video/BV1JV411t7ow/ |
| 教材 | 《计算机网络：自顶向下方法》第 7 版 |

**csdiy 评价**：中文互联网上**比较火的计算机网络课**。郑烇老师从 2020 年至今坚持在 B 站评论区答疑，负责认真。偏实际而非纯理论。

---

# 第三大类 · 数据库系统（5 门）

> **csdiy 观点**：*"没有什么能比自己写个关系型数据库更能加深对数据库系统的理解了。"*

---

## 课程 #11 · CMU 15-445：Database Systems ⭐⭐ 强推

| 字段 | 内容 |
|------|------|
| 开课 | CMU |
| 主讲 | **Andy Pavlo**（"这个世界我只在乎两件事：老婆和数据库"）|
| 先修 | C++ + 数据结构 + CSAPP |
| 语言 | **C++** |
| 难度 | 🌟🌟🌟🌟 | 学时 | 100h |
| 网站 | https://15445.courses.cs.cmu.edu/fall2022/schedule.html |
| YouTube(Fa22) | https://www.youtube.com/playlist?list=PLSE8ODhjZXjaKScG3l0nuOiDTTqpfnWFf |
| 教学数据库 | [bustub](https://github.com/cmu-db/bustub) |

**csdiy 评价**：质量极高、资源极齐全的 Database 入门课。CMU Database Group 专门开发了教学用关系型数据库 **bustub**，4 个 Project 改造其关键组件。

### 📑 4 个 Project（面向磁盘的关系型数据库 Bustub）⭐
1. **Buffer Pool Manager**（内存管理）
2. **B+ Tree**（存储引擎）⭐
3. **Query Executors & Optimizer**（算子 & 优化器）
4. **Concurrency Control**（并发控制）⭐

**亮点**：编译 `bustub-shell` 实时观测实现正确性，**正反馈非常足**。bustub 也是优秀的 C++ 中小型开源项目。

---

## 课程 #12 · UCB CS186：Introduction to Database System

| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS61A/B/C |
| 语言 | **Java** |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 150h |
| 网站 | https://cs186berkeley.net/ |
| B站 | https://www.bilibili.com/video/BV13a411c7Qo |
| 资源 | https://github.com/PKUFlyingPig/CS186 |

### 📑 核心主题 + 6 个 Project
SQL 查询、查询优化、磁盘查询、高并发、故障恢复、NoSQL。**6 个 Project 用 Java 实现**支持 SQL 并发查询、B+ 树 Index、故障恢复的关系型数据库。

---

## 课程 #13 · Caltech CS122：Database System Implementation

| 字段 | 内容 |
|------|------|
| 开课 | Caltech |
| 先修 | 无 |
| 语言 | Java |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 150h |

**定位**：不同于 15-445（无 SQL 层），**CS122 侧重 SQL 层实现**——查询优化器各模块。适合学完 15-445 后对查询优化有兴趣的同学。

### 📑 核心实验
- SQL 解析、Translate
- Join 实现、统计信息、代价估计
- 子查询、Agg、Group By
- B+ 树、WAL

---

## 课程 #14 · Stanford CS346：Database System Implementation

| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 先修 | 无 |
| 语言 | C++ |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 150h |
| 网站 | https://web.stanford.edu/class/cs346/2015/ |
| 代码 | https://github.com/junkumar/redbase.git |

### 📑 RedBase 项目（4 Lab + 1 Extension）
1. **Record Management**（记录管理）
2. **B+ Index**（索引管理）
3. **System Management**（DDL、命令行、元数据）
4. **Query Language**（RQL：select/insert/delete/update）
5. **Extension**（Blob/网络/Join/CBO/OLAP/事务）

---

## 课程 #15 · CMU 15-799：Special Topics in Database Systems（前沿）

| 字段 | 内容 |
|------|------|
| 开课 | CMU |
| 先修 | 15-445 |
| 语言 | C++ |
| 难度 | 🌟🌟🌟 | 学时 | 80h |
| 网站(sp22) | https://15799.courses.cs.cmu.edu/spring2022/ |

**定位**：数据库前沿主题。fall2013 讨论 Streaming/Graph DB/NVM；spring2022 讨论 **Self-Driving DBMS** ⭐。

---

# 📊 选课套餐

### 安全方向
```
CS161(#1) 综合入门 → MIT 6.858(#2) 系统安全 → SEEDLabs(#3) 实战
进阶 CTF：CSE365(#4) → CSE466(#5)
```

### 网络方向
```
CS144(#7) ⭐ 强推（实现 TCP/IP）
或 CS168(#8) + Top-Down(#9)（理论 + 教材）
中文：USTC(#10)
```

### 数据库方向
```
15-445(#11) ⭐ 强推（bustub，C++）
进阶：CS186(#12) Java / CS346(#14) RedBase / CS122(#13) SQL 优化
前沿：15-799(#15) Self-Driving DBMS
```

---

**文档版本**：v1.0
**最后更新**：2026-07-07
