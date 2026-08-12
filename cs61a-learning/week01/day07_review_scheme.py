"""
CS 61A Day 7 - Week 1 Review + Scheme Interpreter Preview
=========================================================
Day 7 是复习日 + 预告日：
1. Week 1 速测（30 题快检）
2. Scheme 解释器预告（CS 61A 后半学期核心项目）
3. Week 2 预告

本文件实现：
- 30 题速测
- mini Scheme 解释器 demo（10 行核心 eval/apply）
- 反直觉：解释器只有 4 个核心规则

运行：
    python3 day07_review_scheme.py
"""

from __future__ import annotations
import math


# ============ 1. Week 1 速测 ============

def speed_test():
    """Week 1 学到的核心概念的 30 题快检"""
    print("=" * 60)
    print("📋 Week 1 速测（30 题）")
    print("=" * 60)
    
    questions = [
        ("为什么 Python 赋值是语句不是表达式？",
         "Python 故意设计让赋值无返回值（防止 a=b=c 链式 bug）"),
        ("什么是环境帧（environment frame）？",
         "一组名字→值的绑定 + 父帧指针（形成作用域链）"),
        ("词法作用域 vs 动态作用域？",
         "词法：函数记住「定义地」；动态：函数记住「调用地」"),
        ("lambda 和 def 的区别？",
         "lambda 只能单表达式；def 可多语句。两者都是函数对象"),
        ("闭包捕获的是「值」还是「名字」？",
         "名字！所以 [lambda: i for i in range(3)] 都返回 2"),
        ("默认参数何时求值？",
         "在 def 时求值一次，所有调用共享（可变默认值是 bug 源）"),
        ("高阶函数定义？",
         "接收函数为参数 或 返回函数"),
        ("装饰器的本质？",
         "@decorator def f: ... 等价于 f = decorator(f)"),
        ("@memoize 改变了什么？",
         "时间复杂度（如 fib 从 O(2ⁿ) → O(n)），但增加空间"),
        ("迭代 ⟺ 递归？",
         "是。3 步法可系统转换：识别状态变量 / 递归情况 / 基础情况"),
        ("树递归 vs 线性递归的复杂度差异？",
         "树：O(φⁿ) 指数爆炸；线性：O(n)"),
        ("什么是尾递归？",
         "递归调用是函数最后一个动作（可被优化为循环）"),
        ("Python 做 TCO 吗？",
         "不做。Guido 认为栈追踪对调试更重要"),
        ("快速幂的复杂度？",
         "O(log n) —— 利用了 b^n = (b^(n/2))^2"),
        ("count_partitions 的递归定义？",
         "count(n, m) = count(n-m, m) + count(n, m-1)"),
        ("互相递归的典型应用？",
         "语法解析（parse_expr ↔ parse_term ↔ parse_factor）"),
        ("Church numeral 用什么编码数字？",
         "函数应用次数：n = λf.λx. f(f(...f(x)...))（n 次）"),
        ("Y 组合子的作用？",
         "让匿名 lambda 能递归（不动点定理）"),
        ("牛顿法求 sqrt 的核心步骤？",
         "guess ← (guess + x/guess) / 2 直到收敛"),
        ("Continuation-Passing Style（CPS）？",
         "不 return 值，而是把值传给 continuation 函数"),
        ("Lambda 演算和图灵机的关系？",
         "Church-Turing 论题：两者等价，都是可计算的本质"),
        ("print 和 return 的核心区别？",
         "print 显示但不返回（返回 None）；return 真返回值"),
        ("函数组合 compose(f, g) 的定义？",
         "λx. f(g(x))"),
        (" Hog 游戏中 Pig Out 规则？",
         "任一骰子为 1 → 本回合只得 1 分"),
        (" Hog 中的 Swine Swap 规则？",
         "分数 2× 关系时互换（变体不同）"),
        (" Hog 的策略本质是什么？",
         "期望值 vs 方差 + 博弈论 + 自适应"),
        ("max_scoring_num_rolls 通常返回几？",
         "约 6（平均收益最高）"),
        ("为什么 SICP 重视高阶函数？",
         "它们是抽象的「模板」—— 同一模板可处理多种数据"),
        ("「不动点」在 SICP 中的角色？",
         "牛顿法 / Y 组合子 / 类型推断 都是不动点"),
        ("CS 61A 期末项目是什么？",
         "Scheme 解释器——把 Week 1-14 学的融合实现"),
    ]
    
    for i, (q, a) in enumerate(questions, 1):
        print(f"\n   Q{i}: {q}")
        print(f"   A: {a}")


# ============ 2. mini Scheme 解释器（10 行核心）============

def mini_scheme_demo():
    """10 行代码实现 Scheme 解释器核心——这就是 CS 61A 期末项目的预览
    
    Scheme 表达式 4 种：
    1. 数字字面量：42, 3.14
    2. 符号：x, +, factorial
    3. 特殊形式：(if cond then else), (define name val), (lambda (params) body)
    4. 函数调用：(func arg1 arg2 ...)
    """
    print("\n" + "=" * 60)
    print("📋 mini Scheme 解释器（10 行核心 = CS 61A 期末项目预览）")
    print("=" * 60)
    
    # 用 Python tuple/list 表示 Scheme 表达式
    # 例：(if (> x 0) x (- x)) → ('if', ('>', 'x', 0), 'x', ('-', 'x'))
    
    def tokenize(s):
        """字符串 → token 列表"""
        return s.replace('(', ' ( ').replace(')', ' ) ').split()
    
    def parse(tokens):
        """token 列表 → AST（Python 嵌套 list）"""
        if not tokens: raise SyntaxError("unexpected EOF")
        token = tokens.pop(0)
        if token == '(':
            lst = []
            while tokens[0] != ')':
                lst.append(parse(tokens))
            tokens.pop(0)  # consume ')'
            return lst
        elif token == ')':
            raise SyntaxError("unexpected )")
        else:
            # 尝试数字
            try: return int(token)
            except ValueError:
                try: return float(token)
                except ValueError: return token  # 符号
    
    def scheme_eval(expr, env):
        """Scheme 求值规则——整个解释器的灵魂"""
        # 数字字面量
        if isinstance(expr, (int, float)):
            return expr
        # 符号 → 环境查找
        if isinstance(expr, str):
            return env[expr]
        # 列表 → 特殊形式 or 函数调用
        if isinstance(expr, list):
            if not expr:
                return expr  # nil
            
            op = expr[0]
            # 特殊形式
            if op == 'if':
                cond = scheme_eval(expr[1], env)
                if cond:  # truthy
                    return scheme_eval(expr[2], env)
                elif len(expr) > 3:
                    return scheme_eval(expr[3], env)
                return None
            elif op == 'define':
                name, val_expr = expr[1], expr[2]
                env[name] = scheme_eval(val_expr, env)
                return name
            elif op == 'lambda':
                params, body = expr[1], expr[2]
                def closure(*args):
                    local = dict(env)
                    for p, a in zip(params, args):
                        local[p] = a
                    return scheme_eval(body, local)
                return closure
            elif op == 'quote':
                return expr[1]
            
            # 函数调用
            func = scheme_eval(op, env)
            args = [scheme_eval(a, env) for a in expr[1:]]
            return func(*args)
        
        return expr
    
    # 标准环境
    global_env = {
        '+': lambda *a: sum(a),
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        '>': lambda a, b: a > b,
        '<': lambda a, b: a < b,
        '=': lambda a, b: a == b,
        'abs': abs,
        'max': max,
        'min': min,
    }
    
    # 测试用例
    tests = [
        ("(+ 1 2)", 3),
        ("(* 3 4)", 12),
        ("(+ 1 (* 2 3))", 7),
        ("(if (> 5 3) 10 20)", 10),
        ("(if (< 5 3) 10 20)", 20),
        ("(abs -7)", 7),
        ("(max 3 7 2 9 1)", 9),
    ]
    
    print("\n   mini Scheme 解释器测试：")
    for code, expected in tests:
        tokens = tokenize(code)
        ast = parse(tokens[:])
        result = scheme_eval(ast, global_env)
        ok = result == expected
        print(f"   {code:<25} → {result}    {'✓' if ok else '✗ 期望 ' + str(expected)}")
    
    # 用 define 定义函数
    print(f"\n   用 define + lambda：")
    code = "(define square (lambda (x) (* x x)))"
    ast = parse(tokenize(code)[:])
    name = scheme_eval(ast, global_env)
    print(f"   {code}")
    print(f"   → 定义了 '{name}'")
    
    code = "(square 7)"
    result = scheme_eval(parse(tokenize(code)[:]), global_env)
    print(f"   (square 7) → {result}")
    
    # 条件递归
    code = "(define abs2 (lambda (x) (if (> x 0) x (- 0 x))))"
    scheme_eval(parse(tokenize(code)[:]), global_env)
    code = "(abs2 -5)"
    result = scheme_eval(parse(tokenize(code)[:]), global_env)
    print(f"   (abs2 -5) → {result}")
    
    print(f"\n   💡 这就是 Scheme 解释器的核心！只有 4 个规则：")
    print(f"      1. 数字 → 返回自身")
    print(f"      2. 符号 → 环境查找")
    print(f"      3. 特殊形式（if/define/lambda/quote）→ 特殊处理")
    print(f"      4. 列表 → 求值操作符 + 参数 + 调用")
    print(f"\n   🚀 CS 61A Project 4 会要求你扩展这个解释器：")
    print(f"      - 添加 tail call optimization")
    print(f"      - 添加 let / cond / begin")
    print(f"      - 支持动态作用域切换")
    print(f"      - 添加宏系统")
    print(f"      这就是 Week 2-14 的最终目标！")


# ============ 3. Week 2 预告 ============

def week2_preview():
    """Week 2 学什么"""
    print("\n" + "=" * 60)
    print("📋 Week 2 预告")
    print("=" * 60)
    
    print("""
   Week 1 你学会了（高阶函数 + 递归 + lambda 演算）
   
   Week 2-3 学：
   1. 数据抽象（pairs, lists, trees）
      - 用 cons/car/cdr 构造数据
      - 用高阶函数处理（map/filter/reduce on lists）
   
   2. 序列（sequences）
      - 列表迭代 vs 递归
      - 序列的"高效"实现（链表 vs 数组）
   
   3. 可变数据（mutable）
      - list 是可变的——区别于 tuple
      - 函数副作用与状态管理
   
   4. 大型项目：Ants（基于 Hog 的塔防游戏）
      - 多类继承
      - 状态管理
      - 策略实现
   
   Week 4-5 学：
   5. 面向对象编程（OOP）
      - class, instance, method
      - inheritance
      - special methods (__init__, __repr__)
   
   Week 6-7 学：
   6. Scheme 解释器（CS 61A 期末项目）
      - 用 Week 1-5 学的 Python 知识
      - 实现一个完整的 Scheme 解释器
      - 这是 CS 61A 的高潮
   
   Week 8-10 学：
   7. SQL + 异常 + 迭代器 + 生成器
   8. Streams（惰性求值）
   9. Final Project
    """)


# ============ main ============

def main():
    speed_test()
    mini_scheme_demo()
    week2_preview()
    
    print("\n" + "=" * 60)
    print("🎉 CS 61A Week 1 完成！")
    print("=" * 60)
    print("""
   Week 1 你掌握的核心能力：
   ✅ 函数作为一等公民（传参/返回/装饰）
   ✅ 递归思维（线性/树/互相递归）
   ✅ Lambda 演算基础（Church numerals + Y 组合子）
   ✅ 牛顿法 + 不动点（高阶函数做数值）
   ✅ 环境模型（词法作用域 + 闭包）
   ✅ Hog 游戏（完整项目实战）
   ✅ Scheme 解释器预览（Week 2-14 的目标）
   
   累计代码：~2000 行 Python（含项目 + HW + Lab）
   累计概念：~50 个核心 CS 概念
   路径进度：UNIFIED_PLAN_4_TRACKS 阶段 1 (E) 的 1/12 = 8.3%
   
   下一步：Week 2 数据抽象（cons/list/tree）
    """)


if __name__ == "__main__":
    main()
