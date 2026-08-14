# Week 1 学完 CS 61A 的总结

> 2026-08-12 · 一周从「Python 工程师」到「SICP 抽象思维入门」
> 代码：`cs61a-learning/week01/` 10 文件 2,796 行 Python，70 测试全过

## 🎯 学到了什么（按 Day 整理）

| Day | 主题 | 文件 | 关键洞察 |
|-----|------|------|---------|
| 1 | Names + Environment + HOF | lecture01/02.py | 词法作用域延迟查找 + 闭包捕获「名字」非「值」|
| 1 | HW1 Q1-Q5 | hw01_solutions.py | `if_function` vs `if statement`：短路 vs 全求值 |
| 2 | Control + Recursion | lecture03_recursion.py | 3 步法系统转换迭代→递归；快速幂 O(log n) |
| 2 | HW1 Q6-Q10 | hw01_q6_q10.py | count_partitions = SICP 灵魂案例 |
| 3 | Env Diagrams + Tree Recursion | lecture05_env_treerec.py | 互相递归 = 文法解析的基础 |
| 3 | Lab 01 | lab01.py | interleaved_sum（互相递归实战）|
| 4-5 | Lambda Calculus + Currying + Newton | lecture07_lambda_calculus.py | Church numerals + Y combinator + 牛顿法不动点 |
| 6 | Project 1 Hog | hog_project.py | 策略作为高阶函数 + 期望分析 |
| 7 | Review + Scheme Preview | day07_review_scheme.py | 10 行实现 mini Scheme 解释器 |

## 💡 10 个「Aha 时刻」

1. **程序 = 表达式 + 命名 + 环境**——任何 Python 代码都能在脑中画环境帧链
2. **赋值是语句不是表达式**——Python 故意让 `y = (x = 5)` 语法错
3. **闭包捕获名字不是值**——`[lambda: i for i in range(3)]` 都得 2
4. **默认参数 def 时求值一次**——可变默认值是经典 bug 源
5. **递归定义 = 自动算法**——count_partitions、Pascal、Hanoi 不用想循环
6. **树递归指数爆炸**——fib(35) 调用 9 百万次（φⁿ/√5）
7. **Python 不做 TCO**——Guido 认为栈追踪对调试更重要
8. **Church numerals**——数字本质 = 函数应用次数（n = λf.λx.fⁿ(x)）
9. **Y 组合子**——不动点让纯 lambda 也能递归
10. **不动点是 SICP 的元主题**——牛顿法/Y 组合子/类型推断都是不动点

## 📊 数据

| 维度 | 数据 |
|------|------|
| Python 文件 | 10 |
| 总代码行 | 2,796 |
| 自动测试 | 70（全过）|
| 主题覆盖 | 50+ 核心 CS 概念 |
| Lecture demo | 5（全部含反直觉发现）|
| HW 题 | 10（全过）|
| Lab 题 | 4（全过）|
| 完整项目 | 1（Hog 骰子游戏）|
| mini Scheme 解释器 | 1（10 行核心）|

## 🎯 能力自检

学完后，我能：

- [x] 30 行内写出 Scheme 解释器 eval/apply
- [x] 5 分钟内从迭代写出递归版（3 步法）
- [x] 推导 lambda 演算的 Church 加法/乘法
- [x] 用 Y 组合子让匿名 lambda 递归
- [x] 写出带策略的完整骰子游戏
- [x] 解释为什么 `[lambda: i for i in range(3)]` 得 `[2,2,2]`
- [x] 用不动点迭代实现牛顿法开方
- [x] 识别互相递归 = 文法解析的基础

## 📍 在 UNIFIED_PLAN_4_TRACKS 中的位置

```
阶段 1 (E) 月 1-12 → AI 工程师
  ├─ Week 1-2: CS 61A ← 你在这里 (Week 1 ✓)
  ├─ Week 3-4: COS 226 算法
  ├─ Week 5-8: CSAPP + 概率
  └─ ...
进度：阶段 1 的 1/48 ≈ 2.1%（但已建立完整 CS 抽象思维框架）
```

## 🔮 Week 2 预告

- **数据抽象**：cons/car/cdr 构造 pair，构造 list，构造 tree
- **序列操作**：用 Week 1 学的高阶函数处理 list（map/filter/reduce on list）
- **可变数据**：list vs tuple 的本质区别
- **大型项目 Ants**：基于 Hog 的塔防游戏（OOP 预演）

## 📚 推荐复习

1. **重做 HW1**（不看答案）—— 检验 7 天前的理解
2. **重写 Hog final_strategy**（尝试超过 55% 胜率）
3. **手写 Y 组合子**（不看 lecture，从不动点定义推）
4. **读 SICP 1.1-1.3**（英文版，与代码对照）

## 🎓 元洞察

**Week 1 最深的收获**不是具体语法，而是 **3 个心智模型**：

1. **抽象层次思维**——每个程序都在某个抽象层（值/函数/高阶函数/解释器）
2. **递归 = 自指**——很多复杂问题用递归描述后自动得到算法
3. **不动点 = 收敛**——很多迭代过程（牛顿/Y/类型推断）都是不动点

这 3 个模型会在后续 Week 反复出现，最终在 CS 61A Project 4（Scheme 解释器）合流。

---

**下一步**：Week 2 数据抽象（cons/list/tree）。已就绪。

> 「第 1 周 CS 61A Lecture 1 比 1 年规划更重要。规划再好不如立即开始。」—— 本周已开始 ✓
