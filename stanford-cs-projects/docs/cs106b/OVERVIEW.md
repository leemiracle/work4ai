# CS106B: Programming Abstractions

> **课程官网**: https://web.stanford.edu/class/cs106b/
> **讲师**: Sean Szumlanski（Summer 2026）
> **Head TA**: Butch Nasser
> **学期**: Summer Quarter 2026
> **上课时间**: 周一至周四 13:30-14:45，NVIDIA Auditorium
> **前置课程**: CS106A（Python 编程方法论）
> **核心语言**: **C++**（这是学生第一次接触 C++ 的课程）
> **评分构成**: 编程作业 + Section + 考试
> **项目代码**: `topic12-intro/sorting_visualizer.py`（Python 版算法可视化）

---

## 📚 课程定位

CS106B 是斯坦福计算机科学入门序列的**第二门课**，衔接 CS106A（Python 编程方法论）。如果说 CS106A 教你"如何编程"，那么 CS106B 教你"**如何用编程解决复杂问题**"。

课程的核心使命是：

1. **引入 C++**——学生从 Python 过渡到工业级语言 C++
2. **递归思维**——CS106B 最核心的主题，贯穿整个课程
3. **经典数据结构与算法**——链表、栈、队列、树、哈希表、图
4. **算法分析**——大 O 符号、时空复杂度权衡
5. **问题分解**——将复杂问题拆解为可管理的子问题

### 教学风格

Sean Szumlanski 的教学以**热情、清晰、关怀**著称。课程强调：

- **递归优先**：不是简单介绍递归，而是用一整个模块深入训练递归思维
- **C++ STL**：大量使用 `Vector`、`Map`、`Set`、`Stack`、`Queue`（Stanford C++ Library）
- **从抽象到实现**：先理解 ADT（抽象数据类型），再学习底层实现
- **大量编码**：每周一个 substantial 的编程作业

### Stanford C++ Library

CS106B 使用斯坦福自研的 **Stanford C++ Library**（`libstanfordcpplib`），提供简化的容器类（`Vector<T>`, `Grid<T>`, `Map<K,V>`, `Set<T>`, `Stack<T>`, `Queue<T>` 等），让学生在掌握底层指针和内存管理之前，先专注于**算法思维**。

---

## 🎯 学习目标

完成本课程后，你将能够：

1. **熟练使用 C++**——从 Python 平滑过渡，掌握 C++ 语法、内存模型、STL
2. **掌握递归**——能够自然地用递归思维解决回溯、分治、树形问题
3. **理解并实现核心数据结构**——链表、二叉搜索树、哈希表、优先队列、图
4. **分析算法复杂度**——大 O 分析、最好/最坏/平均情况
5. **运用经典算法**——排序、搜索、图遍历（BFS/DFS）、动态规划入门
6. **将问题拆解为可管理的子问题**——这是"编程抽象"（Programming Abstractions）的本质

---

## 📅 完整模块（按周/讲）

### 第 1-2 周：C++ 基础与过渡

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L1 | From Python to C++ | 静态类型、编译 vs 解释、C++ 基本语法 |
| L2 | Stanford C++ Library | `Vector`, `Grid`, `string`, I/O |
| L3 | Functions & pass-by-reference | 值传递 vs 引用传递、`const` |
| L4 | Streams & file I/O | `ifstream`/`ofstream`、文本处理 |

**作业**: 熟悉 C++ 开发环境，完成 Python→C++ 的翻译练习

### 第 3-4 周：递归入门（核心模块）

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L5 | Recursion fundamentals | 基本情况、递归关系、调用栈 |
| L6 | Recursive backtracking | 八皇后、排列组合、子集枚举 |
| L7 | Backtracking applications | 迷宫求解、数独、着色问题 |
| L8 | Recursive problem-solving patterns | 选择/包含模式、决策树 |

**作业**: 递归回溯题——经典如"生成所有排列"、"数独求解器"

> 💡 **递归模块是 CS106B 的灵魂**。Sean 设计了大量递归训练，让学生真正"像递归一样思考"。

### 第 5-6 周：数据结构基础

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L9 | Big-O notation | 时间复杂度、空间复杂度、增长率对比 |
| L10 | ADTs & Stanford collections | 抽象数据类型的概念、`Stack`/`Queue` |
| L11 | Linked lists | 节点、指针、插入/删除/遍历 |
| L12 | Linked list deep dive | 双向链表、哨兵节点、内存管理 |

**作业**: 实现链表操作（反转、合并、环检测）

### 第 7-8 周：高级数据结构

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L13 | Binary trees | 二叉树、遍历（前/中/后/层序）|
| L14 | Binary search trees (BST) | BST 性质、插入/删除/查找 |
| L15 | Hashing & hash tables | 哈希函数、冲突处理（链地址/开放寻址）|
| L16 | Maps & Sets | `Map<K,V>` 实现、负载因子、重哈希 |

**作业**: 实现 BST 操作 + 哈希表

### 第 9-10 周：排序与图算法

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L17 | Sorting algorithms | 冒泡/选择/插入（O(n²)）+ 归并/快排（O(n log n)）|
| L18 | Sorting analysis | 稳定性、原地性、比较排序下界 Ω(n log n) |
| L19 | Graph representations | 邻接矩阵 vs 邻接表 |
| L20 | Graph traversal | BFS（广度优先）、DFS（深度优先）、连通分量 |

**作业**: 排序算法实现 + 图遍历应用（如社交网络分析）

### 第 11 周：高级主题与总结

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L21 | Dynamic programming intro | 记忆化、最优子结构、重叠子问题 |
| L22 | Greedy algorithms | 贪心策略、正确性证明 |
| L23 | Huffman encoding | 数据压缩实战（结合树 + 贪心 + 优先队列）|
| L24 | Course wrap-up | 知识串联、后续课程展望 |

---

## 🧮 核心算法/数学

### 1. 递归思维框架

每一个递归解法必须回答三个问题：

```
1. 基本情况（Base Case）: 最小的输入是什么？直接返回答案。
2. 递归关系（Recursive Step）: 如何把大问题分解为更小的同类问题？
3. 组合（Combine）: 子问题的解如何组合成原问题的解？
```

**经典示例——阶乘**：
```python
def factorial(n):
    if n <= 1:        # 基本情况
        return 1
    return n * factorial(n - 1)  # 递归关系 + 组合
```

**经典示例——递归回溯（八皇后）**：
```
solve(row):
    if row == N: 找到一个解，记录
    for col in 0..N:
        if 放置皇后(row, col) 合法:
            放置皇后
            solve(row + 1)    # 递归深入
            移除皇后           # 回溯！
```

### 2. 五大排序算法对比

本项目的 `sorting_visualizer.py` 实现了以下五种排序，并自动统计比较/交换次数：

| 算法 | 时间复杂度 | 空间 | 稳定 | 关键思想 |
|------|-----------|------|------|----------|
| 冒泡排序 | O(n²) | O(1) | ✓ | 相邻元素比较交换，最大值"冒泡"到末尾 |
| 选择排序 | O(n²) | O(1) | ✗ | 每轮选最小值放到前面 |
| 插入排序 | O(n²) | O(1) | ✓ | 像理牌一样，逐个插入正确位置 |
| 归并排序 | O(n log n) | O(n) | ✓ | 分治：排序两半 → 合并有序数组 |
| 快速排序 | O(n log n) | O(log n) | ✗ | 分治：选 pivot → 分区 → 递归排序 |

**分治递归（归并排序）**：
```
merge_sort(arr):
    if len(arr) <= 1: return arr          # 基本情况
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])           # 递归：排序左半
    right = merge_sort(arr[mid:])          # 递归：排序右半
    return merge(left, right)              # 合并两个有序数组
```

### 3. 大 O 符号速查

```
O(1)       常数      — 哈希表查找
O(log n)   对数      — 二分搜索、平衡 BST
O(n)       线性      — 数组遍历
O(n log n) 线性对数  — 归并排序、快排（平均）
O(n²)      平方      — 冒泡/选择/插入排序
O(2ⁿ)      指数      — 纯递归求斐波那契（无记忆化）
```

### 4. 数据结构操作复杂度

| 数据结构 | 访问 | 搜索 | 插入 | 删除 | 空间 |
|----------|------|------|------|------|------|
| 数组 | O(1) | O(n) | O(n) | O(n) | O(n) |
| 链表 | O(n) | O(n) | O(1)* | O(1)* | O(n) |
| 哈希表 | — | O(1) | O(1) | O(1) | O(n) |
| BST（平衡）| O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| 栈/队列 | O(n) | O(n) | O(1) | O(1) | O(n) |

*已知位置的插入/删除

---

## 💻 项目代码

### `topic12-intro/sorting_visualizer.py`

**实现内容**：Python 教学版算法可视化器，涵盖 CS106B 核心数据结构与算法。

| 模块 | 类/函数 | 功能 |
|------|---------|------|
| 排序统计 | `SortStats` (dataclass) | 跟踪比较次数 + 交换次数 |
| 冒泡排序 | `bubble_sort()` | O(n²) 相邻交换 |
| 选择排序 | `selection_sort()` | O(n²) 选最小值 |
| 插入排序 | `insertion_sort()` | O(n²) 逐个插入 |
| 归并排序 | `merge_sort()` | O(n log n) 分治 |
| 快速排序 | `quick_sort()` + `partition()` | O(n log n) 分区 |
| 排序对比 | `compare_sorts(n=100)` | 统一测试 + 性能对比 |
| 链表 | `LinkedList` (Node) | push_front / pop_front / to_list |
| 栈 | `Stack` | push / pop（基于 list） |
| 队列 | `Queue` | enqueue / dequeue |
| 二叉搜索树 | `BST` (TreeNode) | insert / search / inorder |
| 递归可视化 | `recursion_demo()` | 斐波那契递归树展示 |

**运行命令**:
```bash
cd topic12-intro
python3 sorting_visualizer.py
# 输出: 5 种排序的对比次数 + 执行时间 + 数据结构演示
```

**关键输出示例**:
```
📋 排序算法对比 (n=100):
   Bubble    :     4950 cmp,     740 swp,   2.31ms ✓
   Selection :     4950 cmp,      99 swp,   1.12ms ✓
   Insertion :     740 cmp,     740 swp,   0.89ms ✓
   Merge     :      541 cmp,     594 swp,   0.45ms ✓
   Quick     :      612 cmp,     304 swp,   0.38ms ✓
```

### 对应的课程作业（CS106B 原版 C++）

| 作业 | 名称 | 核心概念 | 难度 |
|------|------|----------|------|
| HW1 | Welcome to C++ | Python→C++ 过渡、Stanford Lib | ⭐ |
| HW2 | Recursion warmup | 递归基础、回溯入门 | ⭐⭐ |
| HW3 | Recursion & Backtracking | 迷宫/数独/排列 | ⭐⭐⭐ |
| HW4 | Linked Lists | 链表实现、指针操作 | ⭐⭐⭐ |
| HW5 | Binary Trees | 树遍历、BST 操作 | ⭐⭐⭐ |
| HW6 | Hashing | 哈希表实现 | ⭐⭐⭐⭐ |
| HW7 | Sorting | 多种排序实现 + 分析 | ⭐⭐⭐ |
| HW8 | Graphs | 图遍历、BFS/DFS 应用 | ⭐⭐⭐⭐ |
| **Final** | **综合项目** | **Huffman 编码 / 路径规划等** | ⭐⭐⭐⭐⭐ |

---

## 📊 关键论文/教材

### 教材

- **Julie Zelenski & Jerry Cain**. *Thinking Recursively in C++*.（CS106B 传统教材）
- **Eric Roberts**. *Programming Abstractions in C++*.（CS106B 经典教材，基于早期版本）
- **Cormen, Leiserson, Rivest, Stein (CLRS)**. *Introduction to Algorithms*.（算法圣经，用于深入参考）

### 关键资源

- **Stanford C++ Library 文档**: https://stanford.edu/~stepp/cppdoc/
- **CS106B 课程录像**: 通过 SCPD/Canvas 获取（Sean Szumlanski 的讲解极为清晰）
- **Practice Problems**: CS106B 网站提供大量历年练习题（尤其是递归回溯题）

### 经典算法论文（历史参考）

- **Hoare (1962)**. *Quicksort*. — 快排的起源论文
- **Dijkstra (1959)**. [A Note on Two Problems in Connexion with Graphs](https://www-m3.ma.tum.de/twiki/pub/MNMS/SS18/NumMath/Dijkstra.pdf). — 最短路径算法
- **Huffman (1952)**. *A Method for the Construction of Minimum-Redundancy Codes*. — Huffman 编码

---

## 🎯 学习路径

```
Week 1-2  ┌─ C++ 基础（从 Python 过渡）
          │   └─ 不要纠结指针语法，先掌握 Stanford C++ Lib
          │
Week 3-4  ├─ 递归与回溯（⚠️ 全课最核心模块）
          │   └─ 多做练习题，直到递归成为本能
          │   └─ 口诀："信任递归"——假设子问题已解决
          │
Week 5-6  ├─ 链表 + Big-O（从抽象到实现）
          │   └─ 链表是指针训练的最好材料
          │
Week 7-8  ├─ 树 + 哈希表（高级数据结构）
          │   └─ BST 是递归思维的又一次实践
          │
Week 9-10 ├─ 排序 + 图算法（经典算法实战）
          │   └─ 跑 sorting_visualizer.py 理解复杂度差异
          │
Week 11   └─ DP 入门 + 综合项目
              └─ Huffman 编码：树 + 贪心 + 优先队列的集大成
```

### 给自学者的建议

1. **先跑 Python 版**（`sorting_visualizer.py`）理解算法逻辑，再转 C++ 实现
2. **递归靠刷题**——CS106B 网站的 "Recursion Section Handout" 是黄金练习
3. **画图辅助**——链表和树的指针操作一定要画图
4. **掌握"信任递归"**——不要试图展开整个调用栈，假设递归调用返回正确结果
5. **用 CLRS 深入**——当你想理解"为什么归并排序是 O(n log n)"时，CLRS 的证明无可替代

---

## 💡 反思

### 为什么 CS106B 是斯坦福最受欢迎的课之一

1. **递归训练营**：很少有课程把递归作为核心训练长达数周。Sean 的递归教学是现象级的——他设计的练习从简单到复杂，层层递进，让你真正"内化"递归思维。
2. **Python→C++ 平滑过渡**：Stanford C++ Library 是天才般的设计——它让你用 Python 般简洁的语法写 C++，同时为后续的 CS107（裸指针、内存管理）打下基础。
3. **Section 制度**：每 6-8 人一个 Section，由 Section Leader 每周带领做练习——这种亲密的小组教学是斯坦福 CS 教育的标志。
4. **LaIR（辅导时间）**：凌晨还有 SL 在线帮你 debug——这种支持力度在世界范围内罕见。

### 常见学习陷阱

- **递归恐惧**：很多学生第一次接触递归就"宕机"。解法是多做简单递归题建立信心。
- **指针地狱**：链表实现是指针操作的第一关，画图是最好的 debug 工具。
- **忽视 Big-O**：学生常觉得复杂度分析"无用"，但它是算法选择的决策基础。
- **过早追求 C++ 高级特性**：CS106B 不需要模板元编程、移动语义——专注于算法思维。

---

## 🚀 扩展

### 深入方向

| 方向 | 推荐课程 |
|------|----------|
| 高级 C++ / 系统编程 | Stanford **CS107**（计算机组织与系统）|
| 算法设计与分析 | Stanford **CS161**（算法基础，大 O 的严谨训练）|
| 数据结构进阶 | Stanford **CS166**（高级数据结构：跳表、B 树、并查集...）|
| 竞赛编程 | Stanford **CS97SI**（ACM-ICPC 训练）|
| 人工智能 | Stanford **CS221**（CS106B 是 CS221 的前置之一）|

### 实战项目建议

1. **用 C++ 实现一个简化版 HashMap**——不用 Stanford Lib，纯指针操作
2. **实现 A* 寻路算法**——结合图 + 优先队列 + 启发式搜索
3. **实现 LZW 压缩**——比 Huffman 更高级的压缩算法
4. **参加 Stanford Local Programming Contest**——CS106B 是最佳准备
5. **写一个递归下降解析器**——递归思维的终极练习

### 与其他课程的关系

```
CS106A (Python 编程基础)
    │
    ▼
CS106B (C++ + 递归 + 数据结构)  ◄── 你在这里
    │
    ├──> CS107 (系统编程: C/汇编/内存)
    ├──> CS161 (算法设计与分析)
    ├──> CS221 (AI: 需要递归+搜索基础)
    └──> CS110 (操作系统: 需要C++能力)
```

CS106B 是整个斯坦福 CS 课程体系的**基石**——几乎所有后续课程都以 CS106B 为前置，因为它同时教授了**语言能力（C++）**和**思维方法（递归+数据结构+算法分析）**。

---

> *"Recursive thinking is the single most important skill a computer scientist can develop."* — CS106B 精神
