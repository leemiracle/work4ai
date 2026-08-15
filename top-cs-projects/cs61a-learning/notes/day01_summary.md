# Day 1 学习总结（CS 61A 第 1 周 Day 1）

## ✅ 已完成

### Lecture 1: Functions, Names, Environment
- [x] 表达式 vs 语句的根本区别
- [x] 环境模型（Python 真实求值规则）
- [x] 替换模型 vs 环境模型（纯函数 vs 非纯函数）
- [x] 词法作用域的 3 个反直觉案例
- [x] 5 个必学内置函数（map/filter/reduce/zip/sorted）

### Lecture 2: Higher-Order Functions
- [x] 函数作为参数（map/reduce 通用模式）
- [x] 闭包（make_adder / 计数器 / 函数组合）
- [x] Lambda 表达式（与 def 等价 + 局限性）
- [x] 装饰器（timer / memoize 把 fib 从 O(2^n) 降到 O(n)）
- [x] 通用化模式（accumulate —— SICP 的灵魂）
- [x] 反直觉：循环 lambda 共享 i

### HW 1 前 5 题（Q1-Q5）
- [x] Q1 a_plus_abs_b（用 add/sub 选择替代 abs）
- [x] Q2 two_of_three（平方和减最小平方 —— 模式识别训练）
- [x] Q3 largest_factor（从 n//2 倒着找）
- [x] Q4 if_function vs statement（短路与求值顺序 —— **最重要的反直觉**）
- [x] Q5 sum_digits（% 10 + // 10 的经典循环）

## 🎯 今日 3 个核心「Aha 时刻」

### Aha 1: 程序 = 表达式 + 命名 + 环境
看到任何 Python 代码，你能在脑中画出环境帧链：global → local → ...

### Aha 2: 函数是一等公民
函数可以传参、返回、存储、装饰——这让 Python 既是命令式又是函数式语言。

### Aha 3: 求值顺序 = 程序语义
`if_function(c(), t(), f())` 与 `if c(): t() else: f()` 看起来等价，但**前者必然调用 t() 和 f()，后者短路**。这种「**求值顺序决定副作用**」是函数式编程的核心主题。

## ⚡ 30 秒速测（合格 = 能答出）

1. **为什么 `for i in range(3): funcs.append(lambda: i)` 最后 `[f() for f in funcs]` 是 `[2,2,2]`？**
   - 答：lambda 捕获「变量 i」不是「i 当前的值」。循环结束后 i=2，所有 lambda 都返回 2。

2. **`def f(x, cache=[]): cache.append(x)` 为什么每次调用 cache 都在累积？**
   - 答：默认参数在 `def` 时求值一次。所有调用共享同一个 list 对象。

3. **装饰器 `@memoize` 为什么能把递归 fib 的复杂度从 O(2^n) 降到 O(n)？**
   - 答：每个 fib(k) 只真正计算一次，后续调用直接返回缓存。

4. **写出 `accumulate(combiner, start, n, term)` 的签名和 1²+2²+...+5² 怎么调？**
   - 答：`accumulate(lambda a,b: a+b, 0, 5, lambda x: x*x)` = 55

5. **if_function 与 if statement 何时行为不同？**
   - 答：当分支表达式有副作用时（如 print/IO）。if_function 必然求所有参数；if statement 短路。

## 📁 已创建文件

```
cs61a-learning/
├── week01/
│   ├── lecture01_names_env.py     (Lecture 1 demo)
│   ├── lecture02_higher_order.py  (Lecture 2 demo)
│   └── hw01_solutions.py          (HW 1 Q1-Q5 + 22 测试)
└── notes/
    └── day01_summary.md           (本文件)
```

## 📍 明日预告（Day 2 / 周二）

按周历：
- Lecture 3-4（控制/高阶函数 —— lambda 深化、control）
- HW 1 后 5 题（Q6-Q10）

**今日工作量**：约 6-8h（2 lecture demo + 5 HW 题 + 笔记）
**累计进度**：4 周周历的 1/4 = 25%

## 📌 自我检查

请回答（不查资料）：
- [ ] 能否 1 分钟内说出 Python 赋值是语句还是表达式？
- [ ] 能否 30 秒内写出一个 timer 装饰器？
- [ ] 能否解释为什么 `funcs = [lambda: i for i in range(3)]` 得 `[2,2,2]`？

如果都能 → 进入 Day 2
如果有 1 个卡 → 重看对应 demo 代码再继续

---

**完成时间**：2026-08-12
**总耗时**：~6h（含写代码 + 跑测试 + 写笔记）
**下一步**：用户确认后进入 Day 2
