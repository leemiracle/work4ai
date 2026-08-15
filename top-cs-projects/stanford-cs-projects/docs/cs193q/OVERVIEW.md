# CS193Q: Python Programming

> Stanford University, Autumn 2026
> 领域: Python 进阶
> Prerequisites: CS106A 或同等编程基础
> Units: 1-2
> Difficulty: ⭐⭐

---

## 📚 定位

从"会写 Python"到"写好 Python"——掌握装饰器、生成器、上下文管理器等 Pythonic 核心特性。

---

## 🎯 学习目标

- 掌握 Python 高级特性（装饰器、生成器、上下文管理器）
- 理解 Python 数据模型与魔法方法
- 能编写 Pythonic、可维护的代码
- 熟悉常用标准库与开发工具

---

## 📅 核心模块

### Module 1: Python 数据模型
- 一切皆对象
- 魔法方法（dunder methods）
- `__init__` / `__repr__` / `__eq__` / `__hash__`
- 序列与映射协议

### Module 2: 函数式特性
- 一等函数与高阶函数
- Lambda 表达式
- map / filter / reduce
- 函数式编程模式

### Module 3: 装饰器
- 函数即对象
- 装饰器原理（闭包 + 包装）
- functools.wraps
- 常用装饰器（property、staticmethod）

### Module 4: 生成器与迭代器
- 迭代器协议（`__iter__` / `__next__`）
- 生成器函数（yield）
- 生成器表达式
- 惰性求值与内存效率

### Module 5: 上下文管理与并发
- with 语句与上下文管理器
- contextlib 装饰器
- asyncio 异步编程
- 类型提示（type hints）

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs193q_demo`

**实现内容**:
1. ✅ 自定义装饰器（timing 计时器）
2. ✅ 无限生成器（fibonacci）
3. ✅ Context Manager 概念说明
4. ✅ 三大 Pythonic 特性实战演示

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
装饰器示例:
  slow_sum 耗时 2.50ms
  sum(0..100000) = 4999950000

生成器示例:
  前 10 个斐波那契: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

Context Manager:
  with open(...) as f: 自动关闭
  @contextmanager 装饰器
```

---

## 📊 关键概念

| 特性 | 用途 | 示例 |
|------|------|------|
| **装饰器** | 横切关注点 | `@timing`、`@property` |
| **生成器** | 惰性序列 | `yield`、无限流 |
| **上下文管理** | 资源安全 | `with open() as f:` |
| **类型提示** | 可维护性 | `def f(x: int) -> str:` |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **CS106A 后进阶** | 从 Java/基础到 Pythonic |
| **数据科学方向** | Python 是核心语言 |
| **AI/ML 方向** | Python 生态必备 |
| **全栈开发** | 后端 + 脚本自动化 |

---

## 🚀 扩展方向

1. 阅读 *Fluent Python* (Luciano Ramalho)
2. 阅读 *Effective Python* (Brett Slatkin)
3. 学习类型检查工具（mypy / pyright）
4. 探索异步框架（FastAPI / aiohttp）

---

**对应代码**: `supplementary/undergrad_projects.py::cs193q_demo`
