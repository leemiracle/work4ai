# Project 07 — VM Translator I：把栈式 VM 翻译成 Hack 汇编

> **一句话目标**：实现一个 **VM → 汇编** 的翻译器，**处理栈运算（push/pop/arithmetic）**。
> 这是 Nand2Tetris 的"编译器栈"第一步——也是理解 JVM / Python bytecode / WebAssembly 的关键。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch7.1-7.3**（Virtual Machine I）|
| 🎥 Coursera | [Unit 7.1-7.7](https://www.coursera.org/learn/nand2tetris2) |
| 🛠 工具 | Python 3 + CPUEmulator（验证用）|
| ⏱ 预计工时 | 10–15 小时 |

---

## 1. 为什么需要 VM？

**VM（Virtual Machine）是高级语言和汇编之间的中间层**：

```
Jack 源码              ← P09-P11 你写编译器
   ↓
VM bytecode            ← P07-P08 你写 VM 翻译器（本目录）
   ↓
Hack 汇编              ← P06 你写过汇编器
   ↓
Hack 机器码            ← 已有的 HardwareSimulator
   ↓
Hack CPU 执行
```

### 1.1 VM 的两个核心好处

1. **解耦前后端**：Jack 编译器只需翻译到 VM，不必关心底层 ISA 是 Hack 还是 ARM
2. **跨平台**：同一份 VM bytecode 可跑在任何实现了 VM 的硬件上（这就是 JVM、WASM 的核心思想）

### 1.2 Nand2Tetris 的 VM 是什么风格

**栈式 VM（Stack-based VM）**——和 JVM bytecode、Python `dis` 输出是同一类。

特点：
- **没有寄存器**，所有操作通过栈完成
- 数据用 `push`/`pop` 显式管理
- 运算符总是**从栈顶取操作数**，结果**压回栈**

---

## 2. VM 指令系统（P07 部分共 9 种）

### 2.1 内存段（Memory Segments）

VM 有 8 个逻辑段，每个段映射到 Hack RAM 的不同区域：

| 段名 | 用途 | Hack RAM 映射 |
|------|------|---------------|
| `argument` | 函数参数 | RAM[ARG] 指向 |
| `local` | 局部变量 | RAM[LCL] 指向 |
| `static` | 静态变量 | RAM[16–255] |
| `constant` | 常量（虚拟）| 不真实存在，push 时直接装载 |
| `this` | 对象字段 | RAM[THIS] 指向 |
| `that` | 数组元素 | RAM[THAT] 指向 |
| `pointer` | THIS/THAT 寄存器本身 | RAM[3–4] |
| `temp` | 临时寄存器 | RAM[5–12] |

### 2.2 P07 要实现的 9 种指令

| 指令 | 形式 | 语义 |
|------|------|------|
| `push` | `push segment i` | segment[i] 压栈 |
| `pop` | `pop segment i` | 弹栈到 segment[i] |
| `add` | `add` | 栈顶两数相加，结果压栈 |
| `sub` | `sub` | 弹出 y, x，压 x - y |
| `neg` | `neg` | 栈顶取负 |
| `eq` | `eq` | 弹出 y, x，压 (x == y ? -1 : 0) |
| `gt` | `gt` | 弹出 y, x，压 (x > y ? -1 : 0) |
| `lt` | `lt` | 弹出 y, x，压 (x < y ? -1 : 0) |
| `and` | `and` | 按位与 |
| `or` | `or` | 按位或 |
| `not` | `not` | 按位非 |

### 2.3 VM 程序示例

```
// 计算 7 + 3
push constant 7
push constant 3
add
```

执行后栈顶是 10。

```
// 计算 (a + b) - (c + d)
push local 0   // a
push local 1   // b
add            // a+b
push local 2   // c
push local 3   // d
add            // c+d
sub            // (a+b) - (c+d)
```

这种风格叫**后缀表示**（Postfix），与函数式编程类似。

---

## 3. Hack RAM 的约定布局

```
RAM[0]    = SP    ← 栈指针（栈底从 RAM[256] 开始）
RAM[1]    = LCL   ← local 段基址
RAM[2]    = ARG   ← argument 段基址
RAM[3]    = THIS  ← this 段基址
RAM[4]    = THAT  ← that 段基址
RAM[5–12] = temp 段
RAM[13–15]= 通用（VM 翻译器用作临时寄存器 R13, R14, R15）
RAM[16–255] = static 段
RAM[256–2047] = 栈
RAM[2048–16383] = 堆（对象、数组）
RAM[16384–24575] = 屏幕
RAM[24576] = 键盘
```

**VM 翻译器需要严格按这个布局使用 RAM**。

---

## 4. 翻译模板（核心）

### 4.1 `push constant i`

```
// VM: push constant 7
// ASM:
@7
D=A        // D = 7
@SP
A=M        // A = SP
M=D        // RAM[SP] = 7
@SP
M=M+1      // SP++
```

### 4.2 `push local i`

```
// VM: push local 3
// ASM:
@LCL
D=M        // D = LCL
@3
A=D+A      // A = LCL + 3
D=M        // D = RAM[LCL+3]
@SP
A=M
M=D        // RAM[SP] = D
@SP
M=M+1
```

### 4.3 `pop local i`

```
// VM: pop local 1
// ASM:
@SP
AM=M-1     // SP--, A = SP（即指向要弹的元素）
D=M        // D = 弹出的值
@LCL
D=M+D      // 错了！应该是 D = LCL + 1（即目标地址）
...
```

**正确做法**：先用 `R13` 暂存目标地址：

```
// VM: pop local 1
// ASM:
@SP
AM=M-1
D=M        // D = 弹出的值（要写回的）
@LCL
D=M+1      // D = LCL + 1 = 目标地址（错误，应为 D = LCL，A = 1，AD = D+A）
@R13
M=D        // R13 = 目标地址
@R13
A=M
M=D        // 写回
```

→ **`pop` 比 `push` 难**——需要小心地址计算。

### 4.4 `add`

```
// VM: add
// ASM:
@SP
AM=M-1     // SP--
D=M        // D = y（栈顶）
A=A-1      // A = SP-1（指向 x）
M=D+M      // RAM[SP-1] = x + y（SP 不变，因为少了 1 个元素）
```

**精妙**：加减法只用 5 条指令，不需要临时寄存器。

### 4.5 `eq` / `gt` / `lt`（有跳转，需要标号）

```
// VM: eq
// ASM:
@SP
AM=M-1
D=M        // D = y
A=A-1
D=M-D      // D = x - y
@EQ_TRUE_N // N 是唯一编号，避免重复
D;JEQ      // 如果 x == y 跳转
@SP
A=M-1
M=0        // false
@EQ_END_N
0;JMP
(EQ_TRUE_N)
@SP
A=M-1
M=-1       // true（Hack 用 -1 表示 true，0 表示 false）
(EQ_END_N)
```

**关键**：每次 `eq/gt/lt` 都需要一个**全局唯一标号**，否则跳转目标会冲突。

→ **翻译器需要维护一个计数器 `label_counter`**，每次比较操作 `+1`。

---

## 5. Python 翻译器骨架

```python
#!/usr/bin/env python3
"""VM → ASM 翻译器（P07 部分）"""

class VMTranslator:
    def __init__(self):
        self.label_counter = 0
        self.output = []
    
    def emit(self, asm: str):
        self.output.append(asm)
    
    def new_label(self, prefix: str) -> str:
        label = f'{prefix}_{self.label_counter}'
        self.label_counter += 1
        return label
    
    def translate(self, vm_line: str):
        parts = vm_line.split()
        cmd = parts[0]
        
        if cmd == 'push':
            self._push(parts[1], int(parts[2]))
        elif cmd == 'pop':
            self._pop(parts[1], int(parts[2]))
        elif cmd in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'):
            self._arithmetic(cmd)
        else:
            raise ValueError(f'未知指令：{vm_line}')
    
    def _push(self, segment: str, index: int):
        # TODO: 实现 push constant / push local / push argument / ...
        pass
    
    def _pop(self, segment: str, index: int):
        # TODO
        pass
    
    def _arithmetic(self, op: str):
        # TODO: add/sub/neg/eq/gt/lt/and/or/not
        pass


if __name__ == '__main__':
    import sys
    translator = VMTranslator()
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.split('//')[0].strip()
            if line:
                translator.translate(line)
    print('\n'.join(translator.output))
```

---

## 6. 测试

nand2tetris 提供 4 个测试用例（P07）：

| 文件 | 测试 |
|------|------|
| `SimpleAdd` | 单一 add |
| `StackTest` | 全部 9 种算术指令 |
| `BasicTest` | push/pop 全部 7 个段 |
| `PointerTest` | pointer 段操作 |
| `StaticTest` | static 段操作 |

**测试流程**：
1. 你的翻译器把 `.vm` 翻成 `.asm`
2. 用 P06 的汇编器（或官方汇编器）把 `.asm` 翻成 `.hack`
3. 在 CPUEmulator 里跑 `.hack`
4. 与 `.cmp` 文件对比 RAM 状态

---

## 7. 常见坑

### 坑 1：比较指令需要唯一标号

```asm
@TRUE      ← 重复使用 TRUE 会冲突
@TRUE
```

→ 用计数器：`@TRUE_0`, `@TRUE_1`, ...

### 坑 2：`pop` 顺序

`pop` 必须先 `SP--`，再读栈顶（用 `A=M` 而不是 `A=M-1`）。

### 坑 3：static 段符号

`static i` 翻译为 `@Foo.i`（Foo 是当前文件名）。

### 坑 4：pointer 段特殊

`pointer 0` = THIS，`pointer 1` = THAT，不是 RAM[0]/RAM[1]。

### 坑 5：constant 段不真实存在

`push constant 5` 是把数字 5 压栈，**不查任何 RAM**。

---

## 8. 与本项目其他模块的连接

### 8.1 与 [`View_01_Compiler`](../../View_01_Compiler/) 的连接

P07 是**最简单的字节码翻译器**。真实工业 VM 翻译器例子：
- **JVM JIT**（HotSpot）：Java bytecode → x86/ARM 机器码，**带优化**
- **Python CPython**：`dis` 看到的就是字节码，由解释器循环执行
- **WebAssembly**：浏览器把 wasm 字节码 JIT 为本机码
- **.NET CLR**：IL → 本机码
- **LuaJIT**：Lua 字节码 → 本机码

→ P07 的栈式 VM 思想**就是 JVM bytecode 的简化版**。学完 P07 后看 JVM 字节码会觉得"套路一样"。

### 8.2 与 [`Expert_11_Compiler_Research`](../../Expert_11_Compiler_Research/) 的连接

GCC 和 LLVM 都使用 **IR（中间表示）** 作为前后端的桥梁——
LLVM IR 与 VM bytecode 是同一思想，只是更底层（SSA 形式 + 寄存器）。

### 8.3 与 [`背景知识/Great_Ideas`](../../背景知识/Great_Ideas_体系结构思想.md) 的连接

- **Great Idea #1：Abstraction（抽象）** ← VM 是抽象的极致
- **Great Idea #8：Interface（接口）** ← VM 是软硬件之间的另一层接口

---

## 9. 扩展挑战

1. **支持单步调试**：在每条 VM 指令后插入"打印 SP 和栈顶"
2. **加优化**：连续两个 push + add 合并为直接装载
3. **寄存器式 VM**：把栈式 VM 改为寄存器式（LuaJIT 风格），对比性能
4. **加 GC**：用 `this`/`that` 段实现 mark-and-sweep 垃圾回收

---

## 10. 检查清单

- [ ] 能解释栈式 VM 与寄存器式 VM 的区别
- [ ] 理解 8 个段的 Hack RAM 映射
- [ ] 能默写 `push constant` 和 `add` 的 ASM 模板
- [ ] 理解 `pop` 为什么需要 R13 等临时寄存器
- [ ] 完成 P07 全部 5 个测试

---

## 📌 下一步

完成 P07 后，进 [`Project_08_VMTranslator_II/`](../Project_08_VMTranslator_II/)。
你将扩展翻译器，支持**分支（goto/if）和函数（call/return）**——
这是 VM 的另一半，也是最考验"理解"的部分。
