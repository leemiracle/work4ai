# 编程语言（17 门）深度展开

> **来源**：csdiy.wiki 编程入门分类
> **判定基准**：飞腾 D3000 NEON 算子优化项目（主体 C，SDK 化需 C++，并发可参考 Rust）

---

## Python（3 门）

### 1. UCB CS61A: Structure and Interpretation of Computer Programs ｜ 弱
- **讲师**：John DeNero
- **难度**：🌟🌟🌟🌟 ｜ **学时**：80h
- **官网**：https://cs61a.org/
- **教材**：[composingprograms.com](https://www.composingprograms.com/)（基于 SICP 用 Python 改编，开源）
- Python 入门经典（csdiy 作者的"梦开始的地方"）

### 2. CS50P: CS50's Introduction to Programming with Python ｜ 弱
- **官网**：https://cs50.harvard.edu/python/
- Harvard Python 入门

### 3. MIT 6.100L: Introduction to CS and Programming using Python ｜ 弱
- **官网**：MIT OCW
- MIT Python 入门

---

## C 语言（2 门）

### 4. ⭐⭐ Harvard CS50: This is CS50x ｜ 中等
- **讲师**：David Malan
- **难度**：🌟🌟🌟 ｜ **学时**：100h+
- **官网**：https://cs50.harvard.edu/x/
- **视频**：[YouTube](https://www.youtube.com/playlist?list=PLhQjrBD2T382_R182iC2gNZI9HzWFMC_8)
- C 语言入门经典，项目主体语言的入门

### 5. Duke University: Introductory C Programming Specialization ｜ 弱
- Coursera C 专项

---

## C++（3 门）

### 6. ⭐⭐ Stanford CS106L: Standard C++ Programming ｜ 中等（lens 10 SDK 化）
- **讲师**：Stanford
- **难度**：🌟🌟🌟🌟
- **官网**：https://web.stanford.edu/class/cs106l/
- 现代 C++（move semantics / templates / ABI）
- **项目价值**：SDK 化（lens 10）需要 C++，理解 ABI 稳定性

### 7. Stanford CS106B/X: Programming Abstractions ｜ 弱
- **官网**：https://web.stanford.edu/class/cs106b/
- C++ 数据结构

### 8. AP1400-2: Advanced Programming (AmirKabir UT) ｜ 弱
- C++ 进阶

---

## Rust（3 门）⭐ 系统编程安全

### 9. ⭐⭐ Stanford CS110L: Safety in Systems Programming ｜ 中等（lens 09 安全）
- **讲师**：Stanford
- **难度**：🌟🌟🌟🌟
- **官网**：https://web.stanford.edu/class/cs110l/
- Rust + 系统编程安全
- **项目价值**：lens 09 安全视角的"内存安全"现代化方向

### 10. KAIST CS220: Programming Principles ｜ 弱
- Rust 进阶

### 11. ⭐⭐⭐ KAIST CS431: Concurrent Programming ｜ 核心（lens 03 并发）
- **讲师**：KAIST
- **难度**：🌟🌟🌟🌟🌟
- **官网**：https://github.com/kaist-cp/cs431
- **GitHub**：[kaist-cp/cs431](https://github.com/kaist-cp/cs431)
- **项目价值**：**并发编程**（OpenMP lens 03 的现代替代视角），Rust async/await + OS thread

---

## Java（1 门）

### 12. MIT 6.092: Introduction To Programming In Java ｜ 弱
- Java 入门（Android NDK 视角）

---

## 函数式（2 门）

### 13. Cornell CS3110: OCaml Programming ｜ 弱
- **官网**：https://cs3110.github.io/textbook/
- 函数式编程（编译器视角）

### 14. Haskell MOOC ｜ 弱
- 类型系统

---

## 其他（2 门）

### 15. ⭐⭐⭐ MIT Missing Semester ｜ 核心（命令行元技能）
- **官网**：https://missing.csail.mit.edu/
- **视频**：[2020 Bilibili](https://www.bilibili.com/video/BV1x711y7GB)
- shell/Git/调试/性能分析等程序员必备元技能

### 16. Sysadmin DeCal ｜ 弱
- 系统管理入门

---

## 项目相关性总览

| 等级 | 课程 | 项目价值 |
|---|---|---|
| ⭐⭐⭐ 核心 | KAIST CS431 (Rust 并发), MIT Missing Semester | OpenMP 替代 + 命令行元技能 |
| ⭐⭐ 中等 | Harvard CS50 (C), Stanford CS106L (C++), Stanford CS110L (Rust 安全) | 项目主体语言 + SDK 化 + 内存安全 |
| ⭐ 弱 | 其余 11 门 | 编程基础或通识 |
