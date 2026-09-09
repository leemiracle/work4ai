# Project 08 — VM Translator II：分支、函数调用与完整 VM

> **一句话目标**：在 P07 基础上扩展，支持 **goto / if-goto / label / function / call / return**——
> 完成完整的 VM 翻译器。**这一关之后，你的 VM 能跑任何 Jack 程序**。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch7.4-7.7**（Virtual Machine II）|
| 🎥 Coursera | [Unit 8.1-8.5](https://www.coursera.org/learn/nand2tetris2) |
| ⏱ 预计工时 | 10–15 小时 |

---

## 1. P08 要加的 6 种指令

| 指令 | 形式 | 语义 |
|------|------|------|
| `label` | `label L` | 定义标号 L |
| `goto` | `goto L` | 无条件跳转到 L |
| `if-goto` | `if-goto L` | 弹栈，若非零则跳转 |
| `function` | `function f nLocals` | 声明函数 f，有 nLocals 个局部变量 |
| `call` | `call f nArgs` | 调用函数 f，传入 nArgs 个参数 |
| `return` | `return` | 返回当前函数 |

---

## 2. 函数调用的本质：栈帧

### 2.1 函数调用前后的栈状态

```
调用前：              调用中（function f 启动）：       返回后：
                      ┌────────────┐
                      │ local vars │ ← LCL 指向
                      ├────────────┤
                      │ arg vars   │ ← ARG 指向
                      ├────────────┤
                      │ RETURN addr│ ← 重要的"返回地址"
[栈]                  ├────────────┤                   [栈]
   ↓                  │ saved LCL  │                    ↓
                      │ saved ARG  │                   arg[0]
                      │ saved THIS │                   arg[1]
                      │ saved THAT │                   = return value
                      │ saved SP   │
                      ├────────────┤
                      │ caller 栈  │
                      └────────────┘
```

### 2.2 call 的完整步骤

`call f nArgs` 翻译为：

```
1. 把返回地址压栈
2. 把当前 LCL / ARG / THIS / THAT 压栈（保存现场）
3. ARG = SP - nArgs - 5
4. LCL = SP
5. goto f
6. （返回地址标号）
```

**返回地址**是一个**编译时生成的唯一标号**（如 `return_addr_f_call_3`），用于函数返回时跳回。

### 2.3 function 的完整步骤

`function f nLocals` 翻译为：

```
(f)                      ← 函数入口标号
# 初始化 nLocals 个局部变量为 0
@nLocals
D=A
(LOOP_f_init)
@END_f_init
D;JEQ
@SP
A=M
M=0
@SP
M=M+1
@LOOP_f_init
D=D-1
M=D
@LOOP_f_init
0;JMP
(END_f_init)
```

### 2.4 return 的完整步骤

```
1. endFrame = LCL          ← 栈帧末尾
2. retAddr = RAM[endFrame-5]  ← 返回地址
3. ARG[0] = pop            ← 返回值放回 ARG（即原 caller 的栈顶）
4. SP = ARG + 1            ← 恢复 caller 的栈
5. 恢复 THAT = RAM[endFrame-1]
6. 恢复 THIS = RAM[endFrame-2]
7. 恢复 ARG  = RAM[endFrame-3]
8. 恢复 LCL  = RAM[endFrame-4]
9. goto retAddr            ← 跳回 caller
```

→ **栈帧是函数调用的核心抽象**，JVM、x86 都用类似机制。

---

## 3. Bootstrap（启动代码）

VM 程序启动时，必须先执行一段 bootstrap 代码：

```asm
@256
D=A
@SP
M=D              // SP = 256（栈底）
@Sys.init
0;JMP            // 调用 Sys.init
```

`Sys.init` 是约定的入口函数（类似 C 的 `main`），它会进一步调用用户的 `Main.main`。

---

## 4. Python 翻译器扩展

```python
class VMTranslator:
    def __init__(self, input_filename: str):
        self.input_filename = input_filename
        self.output = []
        self.call_counter = 0
        self.current_function = ''  # 用于生成 static 符号
    
    def translate(self, vm_line: str):
        parts = vm_line.split()
        cmd = parts[0]
        
        if cmd in ('push', 'pop'):
            ...  # P07 已实现
        elif cmd in ('add', 'sub', ...):
            ...  # P07 已实现
        elif cmd == 'label':
            self._label(parts[1])
        elif cmd == 'goto':
            self._goto(parts[1])
        elif cmd == 'if-goto':
            self._if_goto(parts[1])
        elif cmd == 'function':
            self._function(parts[1], int(parts[2]))
        elif cmd == 'call':
            self._call(parts[1], int(parts[2]))
        elif cmd == 'return':
            self._return()
    
    def _label(self, label: str):
        # 标号需要包含当前函数名前缀，避免跨文件冲突
        self.emit(f'({self.current_function}${label})')
    
    def _goto(self, label: str):
        self.emit(f'@{self.current_function}${label}')
        self.emit('0;JMP')
    
    def _if_goto(self, label: str):
        # 弹栈，非零则跳转
        self.emit('@SP')
        self.emit('AM=M-1')
        self.emit('D=M')
        self.emit(f'@{self.current_function}${label}')
        self.emit('D;JNE')
    
    def _function(self, name: str, n_locals: int):
        self.current_function = name
        self.emit(f'({name})')
        for _ in range(n_locals):
            # push constant 0
            self.emit('@SP')
            self.emit('A=M')
            self.emit('M=0')
            self.emit('@SP')
            self.emit('M=M+1')
    
    def _call(self, name: str, n_args: int):
        ret_label = f'{name}$ret.{self.call_counter}'
        self.call_counter += 1
        # 1. 压返回地址
        self.emit(f'@{ret_label}')
        self.emit('D=A')
        self._push_d()
        # 2-5. 压 LCL/ARG/THIS/THAT
        for seg in ('LCL', 'ARG', 'THIS', 'THAT'):
            self.emit(f'@{seg}')
            self.emit('D=M')
            self._push_d()
        # 6. ARG = SP - nArgs - 5
        self.emit('@SP')
        self.emit('D=M')
        self.emit(f'@{n_args + 5}')
        self.emit('D=D-A')
        self.emit('@ARG')
        self.emit('M=D')
        # 7. LCL = SP
        self.emit('@SP')
        self.emit('D=M')
        self.emit('@LCL')
        self.emit('M=D')
        # 8. goto name
        self.emit(f'@{name}')
        self.emit('0;JMP')
        # 9. 返回地址标号
        self.emit(f'({ret_label})')
    
    def _return(self):
        # endFrame = LCL
        self.emit('@LCL')
        self.emit('D=M')
        self.emit('@R13')   # endFrame
        self.emit('M=D')
        # retAddr = RAM[endFrame-5]
        self.emit('@5')
        self.emit('A=D-A')
        self.emit('D=M')
        self.emit('@R14')   # retAddr
        self.emit('M=D')
        # ARG[0] = pop（*ARG = *--SP）
        self.emit('@SP')
        self.emit('AM=M-1')
        self.emit('D=M')
        self.emit('@ARG')
        self.emit('A=M')
        self.emit('M=D')
        # SP = ARG+1
        self.emit('@ARG')
        self.emit('D=M+1')
        self.emit('@SP')
        self.emit('M=D')
        # 恢复 THAT/THIS/ARG/LCL
        for i, seg in enumerate(('THAT', 'THIS', 'ARG', 'LCL')):
            self.emit('@R13')
            self.emit(f'D=M-{i+1}')   # 简化，实际需要两步
            # TODO
        # goto retAddr
        self.emit('@R14')
        self.emit('A=M')
        self.emit('0;JMP')
    
    def _push_d(self):
        """把 D 寄存器压栈"""
        self.emit('@SP')
        self.emit('A=M')
        self.emit('M=D')
        self.emit('@SP')
        self.emit('M=M+1')
```

→ **`_return` 是最复杂的，仔细实现**。建议先在纸上画好栈帧图再写代码。

---

## 5. 测试

P08 提供 4 个测试用例：

| 测试 | 内容 |
|------|------|
| `ProgramFlow` | 测试 goto / if-goto |
| `FunctionCalls` | 测试 call / return |
| `StaticCall` | 测试 static 段跨文件调用 |
| `FibonacciElement` | 综合测试（递归调用）|

### 5.1 多文件 VM

P08 引入**多文件 VM 项目**——一个目录下多个 `.vm` 文件一起编译：

```
project/
├── Main.vm
├── Foo.vm
└── Bar.vm
```

你的翻译器需要：
1. 输入是目录时，扫描所有 `.vm`
2. 把所有文件合并为一个 `.asm`
3. `static` 段需要带文件名前缀（`@Foo.3`）

---

## 6. 常见坑

### 坑 1：bootstrap 代码忘了加

如果你的翻译器没输出 bootstrap（设 SP=256 + 调用 Sys.init），程序不会启动。

### 坑 2：return 时寄存器恢复顺序

必须**先 THAT 再 THIS 再 ARG 再 LCL**，因为它们在栈帧里就是按这个顺序排列的。

### 坑 3：static 段符号要带文件名

`Foo.vm` 里的 `static 3` → `@Foo.3`（不是 `@3`）。

### 坑 4：标号要带函数名前缀

```
function Main.foo 0
label LOOP
goto LOOP
```

如果 Main.foo 和 Bar.foo 都有 `label LOOP`，会冲突。
**正确做法**：标号翻译为 `Main.foo$LOOP`。

### 坑 5：递归调用

`FibonacciElement` 用递归实现 Fibonacci——每次 call 都要保存现场，return 时正确恢复。
**漏一个寄存器恢复，整个程序就崩**。

---

## 7. 与本项目其他模块的连接

### 7.1 与 [`Expert_04_OS_Kernel`](../../Expert_04_OS_Kernel/) 的连接

P08 的函数调用机制（栈帧 + saved registers + return address）就是 **真实 CPU 调用约定的简化版**。

ARM64 的调用约定（AAPCS64，[`Lab01 §2.2`](../../Lab01_ISA与汇编/)）：
- 前 8 个参数走 X0–X7（**寄存器传参**，比 VM 快）
- X19–X28 是 callee-saved（**编译器自动保存**，类似 VM 的 saved LCL/ARG）
- LR=X30 保存返回地址（**专用寄存器**，比 VM 简单）
- 栈帧由 FP/SP 管理

→ **VM 调用约定 vs ARM 调用约定**：VM 全栈式（简单慢），ARM 寄存器+栈混合（复杂快）。

### 7.2 与 [`View_01_Compiler`](../../View_01_Compiler/) 的连接

学完 P07-P08 后，看 GCC -O0 vs -O2 编译出的 ARM64 汇编，你会发现：
- -O0 像 VM：每次操作都进栈
- -O2 像优化器：尽量用寄存器，避免访存

### 7.3 与 [`Lab04_超标量乱序`](../../Lab04_超标量乱序/) 的连接

VM 是**顺序执行**；现代 CPU 是**乱序执行**——
但 VM 的栈帧约定仍然**在最终提交时按序**（这是 ISA 层契约）。
→ Lab04 学到的"乱序 + 提交顺序"正好对应"VM 顺序 vs CPU 内部乱序"的对比。

---

## 8. 扩展挑战

1. **Tail Call Optimization**：识别尾调用，避免新建栈帧
2. **Inline Cache**：缓存虚函数调用目标
3. **JIT**：把 VM bytecode 编译为 x86/ARM 本机码（参考 PyPy）
4. **GC**：标记-清除式 GC，使用 `this`/`that` 段管理堆

---

## 9. 检查清单

- [ ] 能默写 `call` 的 9 步流程
- [ ] 能默写 `return` 的 5 步恢复 + 1 步跳转
- [ ] 理解栈帧布局（LCL/ARG/THIS/THAT/retAddr/参数/局部变量的相对位置）
- [ ] 实现 bootstrap 代码
- [ ] 支持多文件 VM 项目
- [ ] 跑通 FibonacciElement（递归测试）

---

## 📌 下一步

完成 P08 后，进 [`Project_09_HighLevelLanguage/`](../Project_09_HighLevelLanguage/)。
你将**用 Jack 语言写一个交互式 App**——
这是从"造工具"到"用工具"的转折点。
