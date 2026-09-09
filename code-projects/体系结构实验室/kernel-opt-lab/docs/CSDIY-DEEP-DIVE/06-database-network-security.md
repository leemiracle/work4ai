# 数据库 + 网络 + 编程语言分析 + 系统安全 深度展开（19 门）

> **来源**：csdiy.wiki + librarian delegate（calm-jade-tiger）实际 webfetch 验证
> **判定基准**：飞腾 D3000 NEON 算子优化 / CXL 远端内存项目

---

## 一、数据库系统（5 门）

### ⭐ CMU 15-445 —— Database Systems ｜ 相关度：核心
- **大学/讲师**：CMU · **Andy Pavlo**（数据库大牛）
- **难度**：🌟🌟🌟🌟
- **学时**：100 小时
- **课程官网**：https://15445.courses.cs.cmu.edu/fall2022/schedule.html
- **视频**：https://www.youtube.com/playlist?list=PLSE8ODhjZXjaKScG3l0nuOiDTTqpfnWFf
- **GitHub**：教学数据库 **bustub** https://github.com/cmu-db/bustub
- **作业**：4 个 Project：**Buffer Pool Manager / B+Tree / Query Executor / 并发控制**
- **核心价值**：**Project #1 的 Buffer Pool Manager 直接对应 CXL 远端内存的页管理 / 换页 / pin-unpin 机制**——这正是 kernel-opt-lab 中"内存层级调度"的底层心智模型

### UCB CS186 —— Introduction to Database Systems ｜ 中等
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：https://cs186berkeley.net/
- **视频**：https://www.bilibili.com/video/BV13a411c7Qo
- **GitHub**：https://github.com/PKUFlyingPig/CS186
- **作业**：6 个 Project（Java 实现支持 SQL 并发查询、B+ 树索引、故障恢复的关系型数据库）
- **价值**：B+ 树存储引擎 + 并发控制涉及 cache locality 与锁粒度

### Caltech CS122 ｜ 弱
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：http://courses.cms.caltech.edu/cs122/
- 侧重 SQL 层实现（查询解析、Join、代价估计），含 NanoDB Buffer Pool 实验

### Stanford CS346 (RedBase) ｜ 弱
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：https://web.stanford.edu/class/cs346/2015/
- **GitHub**：https://github.com/junkumar/redbase
- C++ 实现简易 DB（记录管理 / B+ 索引 / DDL / RQL）

### CMU 15-799 —— Special Topics ｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：80h
- **官网**：https://15799.courses.cs.cmu.edu/spring2022/（Self-Driving DBMS）
- fall2013 版讲 **NVM（非易失内存）** 与 CXL memory semantics 有理论呼应

---

## 二、计算机网络（4 门）

### ⭐ UCB CS168 —— Introduction to the Internet ｜ 核心（CXL 视角）
- **难度**：🌟🌟🌟 ｜ **学时**：~140h
- **官网**：https://sp25.cs168.io/
- **教材**：https://textbook.cs168.io/（自研教材，"简洁生动"）
- **GitHub**：https://github.com/PKUFlyingPig/UCB-CS168
- **作业**：3 个 Python Project（Traceroute / 路由 / TCP 传输）
- **核心价值**：**CXL.memory over fabric 的本质是"远端内存的可靠传输 + 拥塞/流量控制"**。CS168 的路由、可靠传输、拥塞控制章节，是理解 CXL fabric 调度、远端内存访问延迟/带宽权衡的理论基石

### Stanford CS144 ｜ 中等
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：100h
- **讲师**：**Nick McKeown**（SDN/OpenFlow 之父）
- **官网**：https://cs144.github.io/
- **视频**：https://www.youtube.com/watch?v=r2WZNaFyrbQ
- **GitHub**：https://github.com/CS144/minnow（⚠️ 每年清空重置）
- **作业**：8 checkpoint 用现代 C++ 从零搭建 TCP/IP 协议栈
- **价值**：可靠 Byte Stream 与拥塞控制；极佳的 C++ 系统编程训练

### Top-Down Book（Kurose & Ross）｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：40h
- **官网**：https://gaia.cs.umass.edu/kurose_ross/index.php
- **GitHub**：https://github.com/PKUFlyingPig/Computer-Network-A-Top-Down-Approach
- Wireshark 抓包实验，理论入门首选

### USTC 自顶向下（郑烇、杨坚）｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：40h
- **官网**：http://staff.ustc.edu.cn/~qzheng/teaching.html
- **视频**：https://www.bilibili.com/video/BV1JV411t7ow/（本人上传，评论区长期答疑）
- 中文互联网最火的计网课

---

## 三、编程语言设计与分析（4 门）

### Stanford CS242 —— Programming Languages ｜ 弱
- **难度**：🌟🌟🌟🌟 ｜ **学时**：60h
- **讲师**：**Will Crichton**
- **官网**：https://stanford-cs242.github.io/f19/
- **GitHub**：https://github.com/stanford-cs242/f19-assignments
- Lambda 演算 / 类型系统 → OCaml 解释器 → **Rust 所有权与线性类型** → 用 Rust 设计状态机/TCP 库
- 论文：arXiv:1904.06750
- **价值**：Rust 的所有权机制对内核/unsafe 内存安全有参考价值

### NJU 软件分析（李樾、谭添）｜ 弱（但项目相关：lens 09/14）
- **难度**：🌟🌟🌟 ｜ **学时**：60h
- **官网**：https://tai-e.pascal-lab.net/lectures.html
- **OJ**：https://oj.pascal-lab.net/problem
- **视频**：https://www.bilibili.com/video/BV1b7411K7P4/
- 静态程序分析（数据流 / 指针分析 / 污点分析），自研 Java 框架**太阿**，8 作业
- **项目价值**：对 lens 09 安全（CWE 检测）+ lens 14 规范（MISRA Rule）有思路启发

### PKU 软件分析（熊英飞）｜ 弱
- **难度**：🌟🌟🌟🌟 ｜ **学时**：60h
- **官网**：https://xiongyingfei.github.io/SA/2020/main.htm
- **视频**：https://liveclass.org.cn/cloudCourse/#/courseDetail/8mI06L2eRqk8GcsW
- 抽象解释 + 约束求解（SAT/SMT/符号执行）+ 应用（程序合成、缺陷修复）

### Cambridge Semantics ｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：20-30h
- **官网**：https://www.cl.cam.ac.uk/teaching/2324/Semantics/
- **视频**：https://www.youtube.com/playlist?list=PL-2hPK7m5S3hVagseKDPxCBZEqg0PqZhs
- 操作语义 → 指称语义，结构归纳法证明

---

## 四、系统安全（6 门）

### MIT 6.858 —— Computer System Security ｜ 核心（lens 09）
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：100h+
- **官网**：https://css.csail.mit.edu/6.858/2024/
- **视频**：见官网（B 站有搬运）
- **教材**：SSL 实验室笔记 + Build Secure Systems
- **Lab**：基于 **BicycleShop** 的 6 个 security lab（含 SQL 注入、XSS、CSRF、密码学攻击）
- **核心价值**：**Lec on Side Channels / Spectre / Speculative Attacks**——直接对应 lens 09 安全（NEON 时序侧信道、Spec store bypass）

### MIT 6.1600 —— Foundations of Computer Security ｜ 中等
- **难度**：🌟🌟🌟🌟 ｜ **学时**：60h
- **官网**：https://sec-61600.github.io/
- 安全入门：威胁模型 / 密码学 / 系统安全 / 网络安全

### UCB CS161 —— Computer Security ｜ 中等（入门）
- **难度**：🌟🌟🌟🌟 ｜ **学时**：100h
- **官网**：https://cs161.org/
- Crypto + Software security + Network security 三大块

### ASU CSE365 —— Introduction to Cybersecurity ｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：60h
- **官网**：https://pwn.college/
- 网安入门，pwn.college 平台（CTF 风格）

### ASU CSE466 —— Computer Systems Security ｜ 中等（lens 09 fuzz）
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：100h+
- **官网**：https://pwn.college/cse466/
- CTF 实战，含 fuzz / exploit / sandbox escape

### SU SEED Labs ｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：因人而异
- **官网**：https://seedsecuritylabs.org/
- 一套完整的网络安全实验室（含缓冲区溢出、return-to-libc、Spectre 等）
