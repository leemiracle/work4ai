# CS105: Introduction to Computers

> Stanford University, Autumn 2026
> 领域: 计算机通识
> Prerequisites: 无（面向非 CS 专业）
> Units: 3-4
> Difficulty: ⭐

---

## 📚 定位

面向所有人的计算机通识——从晶体管到 AI，理解数字世界的运作方式，无需编程经验。

---

## 🎯 学习目标

- 理解计算机从硬件到应用的分层抽象
- 掌握基本计算思维（算法、数据表示）
- 了解网络、数据库、AI 的基本概念
- 能批判性讨论技术的社会影响

---

## 📅 核心模块

### Module 1: 计算机的层次抽象
- 从应用到物理的 10 层抽象
- 每层解决什么问题
- 抽象的力量与局限

### Module 2: 数据表示
- 二进制与位运算
- 整数、浮点数、字符编码
- 图像、音频、视频的数字表示

### Module 3: 编程入门
- 算法与流程图
- 基础编程概念（变量、循环、条件）
- Python / JavaScript 实践

### Module 4: 系统与网络
- 操作系统的作用
- 互联网如何工作（TCP/IP、DNS、HTTP）
- 云计算与数据中心

### Module 5: AI 与社会
- 机器学习基础概念
- AI 的能力与局限
- 隐私、安全、伦理
- 技术与社会的共同演化

---

## 💻 项目代码

📁 `supplementary/final_projects.py::cs105_demo`

**实现内容**:
1. ✅ 计算机层次抽象完整展示（10 层）
2. ✅ 从 Application 到 Physics 的逐层说明
3. ✅ 每层抽象的代表性技术

**运行**:
```bash
cd supplementary
python3 final_projects.py
```

**输出示例**:
```
计算机的层次抽象（从上到下）:
  Application               : Chrome, Word, ChatGPT
  High-level Lang           : Python, JavaScript
  Compiler/Interpreter      : gcc, CPython
  Assembly                  : x86, ARM
  Machine Code              : 01101011...
  ISA                       : Instruction Set Architecture
  Microarchitecture         : ALU, Registers, Cache
  Logic Gates               : AND, OR, NOT, XOR
  Transistors               : CMOS, FinFET
  Physics                   : Quantum effects, electrons
```

---

## 📊 关键概念

| 层级 | 核心问题 |
|------|----------|
| **应用层** | 用户能做什么 |
| **编程语言** | 人如何指挥机器 |
| **ISA** | 软件/硬件的契约 |
| **逻辑门** | 布尔运算的物理实现 |
| **晶体管** | 数字世界的物理基础 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **非 CS 专业** | 理解数字世界必备 |
| **技术管理者** | 全栈理解做决策 |
| **人文 / 社科** | 技术素养基础 |
| **编程零基础** | CS106A 前的通识铺垫 |

---

## 🚀 扩展方向

1. 进阶：CS106A（编程方法论）
2. 阅读 *Code* (Charles Petzold) — 从零理解计算机
3. 探索 *The Information* (James Gleick)
4. CS106S（编程向善）—— 应用 CS 解决社会问题

---

**对应代码**: `supplementary/final_projects.py::cs105_demo`
