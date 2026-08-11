# CS106L: Standard C++ Programming Lab

> Stanford University, Autumn 2026
> 领域: C++ 进阶 / 系统编程
> Prerequisites: CS106B（或同等编程经验）
> Units: 1-2（实验课）
> Difficulty: ⭐⭐⭐

---

## 📚 定位

CS106B 的 C++ 深度补充——聚焦现代 C++（C++17/20）的标准库、模板与最佳实践。

---

## 🎯 学习目标

- 深入掌握 C++ 标准库（STL）
- 理解现代 C++ 核心特性（移动语义、智能指针）
- 能编写类型安全、资源安全的 C++ 代码
- 理解模板编程与泛型设计

---

## 📅 核心模块

### Module 1: STL 容器与迭代器
- vector / map / set / unordered_map
- 迭代器类别与 range-based for
- 容器选择策略

### Module 2: 内存管理
- 原始指针的问题
- 智能指针（unique_ptr / shared_ptr / weak_ptr）
- RAII 资源管理

### Module 3: 移动语义
- 左值与右值
- std::move 与移动构造
- 完美转发（perfect forwarding）

### Module 4: 模板编程
- 函数模板与类模板
- 类型推导（auto / decltype）
- SFINAE 与 concepts（C++20）

### Module 5: 现代 C++ 实践
- Lambda 表达式与捕获
- const correctness / constexpr
- 异常安全与异常处理
- 并发基础（std::thread / async）

---

## 💻 项目代码

📁 `supplementary/final_projects.py::cs106l_demo`

**实现内容**:
1. ✅ 8 大现代 C++ 核心概念概览
2. ✅ STL 容器、智能指针、移动语义等代码示例
3. ✅ RAII / Lambda / Const Correctness 实践要点

**运行**:
```bash
cd supplementary
python3 final_projects.py
```

**输出示例**:
```
• STL Containers: vector, map, set, unordered_map
• Iterators: begin(), end(), range-based for
• Smart Pointers: unique_ptr, shared_ptr, weak_ptr
• Move Semantics: std::move, rvalue references, &&
• Templates: template<typename T> void f(T x)
• RAII: Resource Acquisition Is Initialization
• Lambda: [capture](params) -> return_type { body }
• Const Correctness: const T&, constexpr, mutable
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **RAII** | 资源获取即初始化 |
| **移动语义** | 避免拷贝，转移所有权 |
| **智能指针** | 自动内存管理 |
| **模板** | 编译期泛型编程 |
| **Lambda** | 内联函数对象 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **CS106B 学生** | 深化 C++ 理解 |
| **系统编程方向** | 性能与控制力的基础 |
| **竞赛编程** | STL 是必备工具 |
| **游戏引擎开发** | C++ 是行业标准 |

---

## 🚀 扩展方向

1. 阅读 *Effective Modern C++* (Scott Meyers)
2. 阅读 *C++ Primer* (Lippman)
3. 探索 C++20/23 新特性（concepts, ranges, modules）
4. 进阶：CS107（计算机组织）、CS110（系统）

---

**对应代码**: `supplementary/final_projects.py::cs106l_demo`
