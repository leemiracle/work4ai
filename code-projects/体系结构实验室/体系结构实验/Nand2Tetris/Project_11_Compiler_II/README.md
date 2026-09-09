# Project 11 — Compiler II：从 AST 到 VM bytecode（代码生成）

> **一句话目标**：在 P10 的 Parser 上添加**代码生成器**，把 Jack AST 翻译为 **VM bytecode**。
> 完成后，你的 Jack 编译器**能完整编译 P09 写的 App**，并在你 P07-P08 的 VM 上跑起来。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch10.5-10.8**（Compiler II）|
| 🎥 Coursera | [Unit 11.1-11.7](https://www.coursera.org/learn/nand2tetris2) |
| ⏱ 预计工时 | 15–25 小时 |

---

## 1. 代码生成的本质：约束满足

编译器要把抽象的 Jack 语义翻译为**有限的 VM 指令**。每个 Jack 构造对应固定的 VM 模板：

| Jack 构造 | 翻译为 |
|-----------|-------|
| `let x = 5;` | `push constant 5; pop local X` |
| `let a[i] = x;` | 算出 a+i 地址，写回 |
| `if (cond) {...}` | cond 计算 + `if-goto L1; goto L2; label L1; ...; label L2` |
| `while (cond) {...}` | `label L1; cond; if-goto L2; ...; goto L1; label L2` |
| `do f();` | `call f 0` |
| `return e;` | 算 e；`return` |
| `x + y` | `push x; push y; add` |

---

## 2. 关键概念

### 2.1 符号表（Symbol Table）

编译器要追踪每个变量的：

| 信息 | 例子 |
|------|------|
| name | `x` |
| type | `int` / `String` / `Foo` |
| kind | `static` / `field` / `argument` / `local` |
| index | `0, 1, 2, ...` |

每个作用域有一个符号表：

```
class 级：static + field
    └ method/function 级：argument + local
```

### 2.2 子程序类型与 this 指针

| 类型 | 隐含参数 | VM 函数名 |
|------|---------|-----------|
| `constructor` | 无 | `ClassName.new` |
| `method` | `argument 0 = this` | `ClassName.methodName` |
| `function` | 无 | `ClassName.functionName` |

→ **method 的所有参数 index 要 +1**（argument 0 留给 this）。

### 2.3 表达式翻译

```
Jack 表达式树 → VM 栈式计算

例如：x + (y * 2)
    +
   / \
  x   *
     / \
    y   2

后缀：x y 2 * +

VM 翻译：
push local X       ← x
push local Y       ← y
push constant 2
mul                ← 计算 y * 2
add                ← 计算 x + (y*2)
```

**核心规则**：递归遍历表达式树，按**后序**输出 VM 指令。

### 2.4 字符串字面量

```jack
do Output.printString("hello");
```

翻译为：
```
push constant 5        ← 字符串长度
call String.new 1      ← 创建 String 对象
push constant 104      ← 'h'
call String.appendChar 1
push constant 101      ← 'e'
call String.appendChar 1
... 重复 5 次
call Output.printString 1
```

**Jack 的字符串字面量展开为一系列函数调用**——这就是为什么 Jack VM 必须有 String 类。

---

## 3. Python 代码生成器骨架

```python
class CodeGenerator:
    def __init__(self):
        self.class_name = ''
        self.class_symbols = {}    # 类级符号表
        self.sub_symbols = {}      # 子程序级符号表
        self.field_count = 0
        self.static_count = 0
        self.arg_count = 0
        self.local_count = 0
        self.output = []
    
    def emit(self, vm_instruction: str):
        self.output.append(vm_instruction)
    
    def compile_class(self, ast):
        self.class_name = ast.name
        for var in ast.vars:
            self._add_symbol(self.class_symbols, var, kind='static|field')
        for sub in ast.subroutines:
            self.compile_subroutine(sub)
    
    def compile_subroutine(self, sub):
        # 重置子程序级符号表
        self.sub_symbols = {}
        self.arg_count = 0
        self.local_count = 0
        
        if sub.kind == 'method':
            # argument 0 = this
            self._add_symbol(self.sub_symbols, 'this', 'ClassName', 'argument', 0)
            self.arg_count = 1
        
        for param in sub.params:
            self._add_symbol(self.sub_symbols, param.name, param.type,
                             'argument', self.arg_count)
            self.arg_count += 1
        
        for var in sub.body.vars:
            self._add_symbol(self.sub_symbols, var.name, var.type,
                             'local', self.local_count)
            self.local_count += 1
        
        # 输出 function 声明
        func_name = f'{self.class_name}.{sub.name}'
        self.emit(f'function {func_name} {self.local_count}')
        
        if sub.kind == 'constructor':
            # 分配 field_count 个字
            self.emit(f'push constant {self.field_count}')
            self.emit('call Memory.alloc 1')
            self.emit('pop pointer 0')        # this = 新对象
        elif sub.kind == 'method':
            self.emit('push argument 0')
            self.emit('pop pointer 0')        # this = argument 0
        
        # 编译函数体
        for stmt in sub.body.statements:
            self.compile_statement(stmt)
    
    def compile_statement(self, stmt):
        if stmt.type == 'let':
            self._compile_let(stmt)
        elif stmt.type == 'if':
            self._compile_if(stmt)
        elif stmt.type == 'while':
            self._compile_while(stmt)
        elif stmt.type == 'do':
            self._compile_do(stmt)
        elif stmt.type == 'return':
            self._compile_return(stmt)
    
    def _compile_let(self, stmt):
        if stmt.array_index:        # let a[i] = e
            # 复杂：算 a + i 地址，pop 到 that，写 e
            ...
        else:                       # let x = e
            self.compile_expression(stmt.value)
            kind, idx = self._lookup(stmt.var_name)
            self.emit(f'pop {kind} {idx}')
    
    def _compile_if(self, stmt):
        else_label = self._new_label()
        end_label = self._new_label()
        self.compile_expression(stmt.cond)
        self.emit(f'if-goto {else_label}' if stmt.else_branch else '')
        # if-goto 的语义是"非零跳"，所以条件真时跳过 else
        # ... 你需要正确处理
        ...
    
    def compile_expression(self, expr):
        if expr.is_leaf:
            self._compile_term(expr)
        else:
            # 二元运算
            self.compile_expression(expr.left)
            self.compile_expression(expr.right)
            op_vm = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2',
                     '/': 'call Math.divide 2', '&': 'and', '|': 'or',
                     '<': 'lt', '>': 'gt', '=': 'eq'}[expr.op]
            self.emit(op_vm)
    
    def _compile_term(self, term):
        if term.type == 'int':
            self.emit(f'push constant {term.value}')
        elif term.type == 'string':
            self._compile_string(term.value)
        elif term.type == 'var':
            kind, idx = self._lookup(term.name)
            self.emit(f'push {kind} {idx}')
        elif term.type == 'subroutine_call':
            self._compile_call(term)
        # ...
```

---

## 4. 关键模板速查

### 4.1 `if-else`

```
push cond
not               ← 反转（因为 if-goto 是"非零跳"）
if-goto ELSE_L
# if-body
goto END_L
label ELSE_L
# else-body
label END_L
```

或更直接：
```
push cond
if-goto TRUE_L    ← cond 真 → 跳到 if-body
goto ELSE_L
label TRUE_L
# if-body
goto END_L
label ELSE_L
# else-body
label END_L
```

### 4.2 `while`

```
label LOOP_START
push cond
if-goto LOOP_BODY
goto LOOP_END
label LOOP_BODY
# body
goto LOOP_START
label LOOP_END
```

### 4.3 `let a[i] = x`

```
push a              ← 数组基址
push i              ← 索引
add                 ← 算出地址 a+i
push x              ← 要存的值
pop temp 0          ← 暂存值
pop pointer 1       ← that = a+i
push temp 0
pop that 0          ← RAM[that] = x
```

### 4.4 `return`

```
push return_value   ← 如果有
return
```

或：
```
push constant 0     ← void 函数返回 0
return
```

---

## 5. 测试

P11 测试集（同一份代码 P10 + P11）：

| 测试 | 内容 |
|------|------|
| `Seven` | 简单计算 |
| `ConvertToBin` | 二进制转换 |
| `Square` | 平方游戏（含 this）|
| `Average` | 数组平均 |
| `Pong` | 乒乓球（最难）|
| `ComplexArrays` | 复杂数组测试 |

**测试流程**：
1. 你的编译器把 `.jack` 编译为 `.vm`
2. 你的 VM 翻译器（P07-P08）把 `.vm` 编译为 `.asm`
3. 你的汇编器（P06）把 `.asm` 编译为 `.hack`
4. 在 CPUEmulator 里跑

→ **整个工具链都是你写的！这是 Nand2Tetris 之旅的第二个高潮**。

---

## 6. 常见坑

### 坑 1：method 调用漏 push this

```jack
do foo.bar();    ← foo 是对象，bar 是 method
```

必须先 push foo，让 bar 接收 this=foo。

### 坑 2：constructor 必须 return this

constructor 末尾必须 `return this;`（VM：`push pointer 0; return`）。

### 坑 3：method 的 arg index 偏移

```jack
method void foo(int x, int y) { ... }
```

参数表：this=arg 0, x=arg 1, y=arg 2。
**编译时要为每个参数 index 加 1**。

### 坑 4：static 段符号

`static int count;` 翻译为 `static 0`（编译器内部分配），但 VM 翻译器把它翻译为 `@ClassName.0`。
**编译器只需给 static 分配 index 0, 1, 2...**，VM 翻译器负责加文件名前缀。

### 坑 5：void 函数的隐式 return

Jack 编译器**必须在每个子程序末尾插入 `return 0;`**（防止漏写 return 导致栈错乱）。

---

## 7. 与本项目其他模块的连接

### 7.1 与 [`View_01_Compiler`](../../View_01_Compiler/) 的连接

学完 P11 后，看 GCC `-O2` 优化级别编译出的 ARM64 汇编，你会理解：
- **寄存器分配**（GCC 把局部变量分配到 X0-X30，P11 全用栈）
- **指令调度**（GCC 重排指令填流水线空泡）
- **死代码消除**（GCC 删除无用的赋值）

P11 不做这些优化，但**核心翻译思路与 GCC 完全一致**。

### 7.2 与 [`Expert_11_Compiler_Research`](../../Expert_11_Compiler_Research/) 的连接

飞腾的 PhyGCC 就是 GCC 的 ARM 后端微调。学完 P11 后看 PhyGCC 的 `-ftree-vectorize`（自动向量化），
你会发现：
- P11 把 Jack 数组循环翻译为标量 VM 指令
- PhyGCC 把 ARM 数组循环翻译为 NEON SIMD（[`Lab01 §3.3`](../../Lab01_ISA与汇编/)）

### 7.3 与 [`Lab05_并行与SIMD`](../../Lab05_并行与SIMD/) 的连接

SIMD 是编译器的**自动向量化**能力。学完 P11 后，把一个 Jack 数组循环用 NEON 重写——
对比 P11 编译器（无向量化）和 PhyGCC（自动向量化）的差距。

---

## 8. 扩展挑战

1. **加寄存器分配**：把 local 变量尽量用 Hack 的 D 寄存器（虽然 Hack 只有 2 个寄存器，限制大）
2. **加优化**：常数折叠（`5 + 3` 直接编译为 `push constant 8`）
3. **加类型检查**：检测未定义变量、类型不匹配
4. **加泛型、Lambda、异常**（难度跳跃）
5. **JIT**：把 VM bytecode 直接编译为 x86/ARM（参考 LuaJIT）

---

## 9. 检查清单

- [ ] 实现符号表（class 级 + subroutine 级）
- [ ] 正确处理 method 的 this 指针（argument 0）
- [ ] 实现 if/while/do/return/let 5 种语句的代码生成
- [ ] 实现表达式的栈式翻译
- [ ] 实现数组访问 `a[i] = x` 和 `x = a[i]`
- [ ] 实现字符串字面量展开
- [ ] **用 P11 的编译器跑 P09 的 App**（最关键的检查！）

---

## 📌 下一步

🎉 完成后，你**已经能用自己写的编译器跑自己写的 App**——
这是 Nand2Tetris 的最后一个核心成就。

[`Project_12_OS/`](../Project_12_OS/)：用 Jack 自己写一个 OS（数学库、字符串库、屏幕驱动、键盘驱动……）。
**完成后，从 Nand 到俄罗斯方块的全部 12 个 project 都跑通了**。
