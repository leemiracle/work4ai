"""
CS 61A Day 1 - Lecture 1: Functions, Names, Environment
======================================================
覆盖主题（对应 composingprograms.com Ch 1.1-1.3）：
- 表达式与语句
- 命名与环境（环境模型 vs 替换模型）
- 纯函数 vs 非纯函数
- 函数定义与调用

核心论文/教材：
- Abelson & Sussman "SICP" 2nd ed MIT Press 1996（精神源头）
- John DeNero "composingprograms.com" 2024（CS 61A 配套教材）
- Pierce "Software Foundations" Vol 1（操作语义的形式化）

本文件实现：
- 替换模型 vs 环境模型的对比 demo
- 词法作用域的反直觉案例
- EnvironmentFrame 类（可视化名字绑定）

运行：
    python3 lecture01_names_env.py
"""

from __future__ import annotations
import math
from typing import Any, Callable


# ============ 1. 表达式与求值 ============

def demo_expressions():
    """表达式 vs 语句的根本区别"""
    print("📋 1. 表达式 vs 语句")
    
    # 表达式：有值，能写 = x
    expr1 = 3 + 4 * 2          # 11
    expr2 = max(1, 2, 3)       # 3
    expr3 = "a" * 3            # "aaa"
    
    # 语句：没有值，做某事（如赋值、def、if）
    x = 5                       # 赋值语句
    
    print(f"   表达式 3 + 4 * 2 = {expr1}")
    print(f"   表达式 max(1,2,3) = {expr2}")
    print(f"   表达式 'a' * 3    = {expr3!r}")
    print(f"   语句  x = 5        → x 现在绑定到 {x}")
    
    # 反直觉：Python 中表达式都能求值
    print(f"\n   💡 反直觉 1: 赋值在 Python 中是「语句」不是「表达式」")
    print(f"      你不能写 y = (x = 5)  ← 语法错！")
    print(f"      这与 C/Rust 不同——Python 故意让赋值无返回值")


# ============ 2. 命名与环境（核心）============

class EnvironmentFrame:
    """可视化一个环境帧（frame）= 一组名字→值的绑定"""
    
    def __init__(self, name: str = "global", parent: 'EnvironmentFrame | None' = None):
        self.name = name
        self.bindings: dict[str, Any] = {}
        self.parent = parent
    
    def bind(self, name: str, value: Any):
        self.bindings[name] = value
    
    def lookup(self, name: str) -> Any:
        """沿作用域链查找——这就是 Python 的真实查找规则"""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise NameError(f"name '{name}' is not defined")
    
    def visualize(self, indent: int = 0):
        """ASCII 可视化环境链"""
        prefix = "  " * indent
        print(f"{prefix}┌─ Frame: {self.name}")
        for k, v in self.bindings.items():
            print(f"{prefix}│   {k} → {v!r}")
        print(f"{prefix}└─→ parent: {self.parent.name if self.parent else 'None'}")
        if self.parent:
            self.parent.visualize(indent + 1)


def demo_environment_model():
    """环境模型：Python 实际怎么求值"""
    print("\n📋 2. 环境模型（Python 真实求值规则）")
    
    # 构造一个典型的环境链
    global_frame = EnvironmentFrame("global")
    global_frame.bind("x", 10)
    global_frame.bind("y", 5)
    global_frame.bind("square", lambda v: v * v)
    
    # 函数调用创建新的 local frame
    local_frame = EnvironmentFrame("square<call>", parent=global_frame)
    local_frame.bind("v", 3)
    
    print("   调用 square(3) 时的环境链：")
    local_frame.visualize()
    
    print(f"\n   在 local frame 查找 v: {local_frame.lookup('v')}")
    print(f"   在 local frame 查找 x（沿链向上）: {local_frame.lookup('x')}")


# ============ 3. 替换模型 vs 环境模型 ============

def substitution_model(expr_fn, arg):
    """替换模型：把参数直接代入函数体（适用于纯函数）"""
    print(f"\n📋 3. 替换模型 vs 环境模型")
    
    # 纯函数：替换模型 = 环境模型
    def square_pure(x): return x * x
    print(f"   纯函数 square(3):")
    print(f"     替换模型: square(3) → 3 * 3 → 9")
    print(f"     环境模型: local frame x=3, return 3*3 = {square_pure(3)}")
    print(f"   ✓ 两者结果一致")
    
    # 非纯函数：替换模型失效
    counter = [0]
    def increment():
        counter[0] += 1
        return counter[0]
    
    print(f"\n   非纯函数 increment()（每次调用都改变 counter）：")
    print(f"     第 1 次: {increment()}")
    print(f"     第 2 次: {increment()}")
    print(f"     第 3 次: {increment()}")
    print(f"   ✗ 替换模型无法描述——同样的'输入'()，不同输出")


# ============ 4. 词法作用域的反直觉 ============

def demo_closure_counterintuitive():
    """词法作用域最常见的 3 个反直觉案例"""
    print("\n📋 4. 词法作用域的 3 个反直觉")
    
    # 案例 1：延迟查找（late binding）
    x = 3
    def f1(y):
        return x + y
    x = 10  # 重新绑定！
    print(f"   案例 1: 延迟查找")
    print(f"     x=3; def f(y): return x+y; x=10; f(1) = {f1(1)}")
    print(f"     💡 期望 4，实际 11——因为 x 在调用时才查找")
    print(f"     （闭包捕获的是「名字」不是「值」）")
    
    # 案例 2：循环闭包陷阱
    print(f"\n   案例 2: 循环闭包陷阱")
    funcs = [lambda: i for i in range(3)]
    results = [f() for f in funcs]
    print(f"     funcs = [lambda: i for i in range(3)]")
    print(f"     [f() for f in funcs] = {results}")
    print(f"     💡 期望 [0,1,2]，实际 [2,2,2]——所有 lambda 共享同一个 i")
    print(f"     修复：funcs = [lambda i=i: i for i in range(3)]  → {[0,1,2]}")
    
    # 案例 3：默认参数是函数定义时求值（不是调用时）
    def f2(x, cache=[]):
        cache.append(x)
        return cache
    print(f"\n   案例 3: 默认参数的「记忆」")
    print(f"     def f(x, cache=[]): cache.append(x); return cache")
    print(f"     f(1) = {f2(1)}")
    print(f"     f(2) = {f2(2)}")
    print(f"     f(3) = {f2(3)}")
    print(f"     💡 默认参数在 def 时求值一次，所有调用共享——常见 bug 源")


# ============ 5. 纯函数 vs 非纯函数 ============

def demo_pure_vs_nonpure():
    """纯函数（FP 圣杯）vs 非纯函数（命令式必备）"""
    print("\n📋 5. 纯函数 vs 非纯函数")
    
    # 纯函数：相同输入永远得相同输出，不修改任何东西
    def pure_add(a, b):
        return a + b
    
    # 非纯函数：有副作用（修改全局/IO/print）
    log = []
    def impure_add(a, b):
        result = a + b
        log.append(f"added {a}+{b}={result}")  # 副作用：修改 log
        return result
    
    print(f"   纯函数 pure_add(2,3) = {pure_add(2,3)}")
    print(f"   纯函数 pure_add(2,3) = {pure_add(2,3)}  （永远相同）")
    print(f"   非纯函数 impure_add(2,3) = {impure_add(2,3)}")
    print(f"   非纯函数 impure_add(2,3) = {impure_add(2,3)}  （结果相同但 log 变了）")
    print(f"   log 现在有 {len(log)} 条记录")
    print(f"\n   💡 反直觉：纯函数更容易测试/并行/缓存（memoize）/形式化推导")
    print(f"      但命令式编程（如 PyTorch）必须用非纯——梯度是状态")


# ============ 6. 必须掌握的 5 个内置函数 ============

def demo_essential_builtins():
    """CS 61A 第 1 周必学的 5 个内置函数"""
    print("\n📋 6. 必学 5 个内置函数（CS 61A HW 常用）")
    
    nums = [3, 1, 4, 1, 5, 9, 2, 6]
    
    # 1. map: 对每个元素应用函数
    squared = list(map(lambda x: x * x, nums))
    print(f"   1. map(lambda x: x*x, {nums})")
    print(f"      = {squared}")
    
    # 2. filter: 保留满足条件的
    evens = list(filter(lambda x: x % 2 == 0, nums))
    print(f"\n   2. filter(even, {nums})")
    print(f"      = {evens}")
    
    # 3. reduce (functools): 累积
    from functools import reduce
    total = reduce(lambda a, b: a + b, nums)
    print(f"\n   3. reduce(+, {nums})")
    print(f"      = {total}")
    
    # 4. zip: 配对
    names = ["a", "b", "c"]
    pairs = list(zip(names, nums))
    print(f"\n   4. zip({names}, {nums[:3]})")
    print(f"      = {pairs}")
    
    # 5. sorted: 排序（带 key）
    sorted_by_close_to_5 = sorted(nums, key=lambda x: abs(x - 5))
    print(f"\n   5. sorted({nums}, key=|x-5|)")
    print(f"      = {sorted_by_close_to_5}")
    
    print(f"\n   💡 反直觉：map/filter 返回迭代器（不立即计算）")
    print(f"      map(lambda x: x*x, nums)  # 不立即算")
    print(f"      list(...)  # 这才触发计算（惰性求值）")


# ============ main ============

def main():
    print("=" * 60)
    print("CS 61A Day 1 - Lecture 1: Functions, Names, Environment")
    print("=" * 60)
    
    demo_expressions()
    demo_environment_model()
    substitution_model(None, None)
    demo_closure_counterintuitive()
    demo_pure_vs_nonpure()
    demo_essential_builtins()
    
    print("\n" + "=" * 60)
    print("💡 反直觉发现汇总：")
    print("   1. Python 赋值是语句不是表达式（与 C/Rust 不同）")
    print("   2. 词法作用域「延迟查找」: f 在 x 重绑定后调用会用新值")
    print("   3. 循环 lambda 共享 i —— [lambda: i for i in range(3)] 全得 2")
    print("   4. 默认参数 def 时求值一次 —— 可变默认值是经典 bug")
    print("   5. 纯函数 = 可缓存/并行/推导；非纯 = PyTorch 训练必须用")
    print("=" * 60)


if __name__ == "__main__":
    main()
