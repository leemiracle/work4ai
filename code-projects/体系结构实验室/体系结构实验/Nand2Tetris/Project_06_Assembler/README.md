# Project 06 — Assembler：用 Python 写一个 Hack 汇编器

> **一句话目标**：用 Python（或 Java）写一个**两遍扫描（two-pass）汇编器**，
> 把 `.asm` 文件翻译成 `.hack` 二进制文件。**这是 Part II 的起点**——
> 也是你第一次自己造"语言翻译工具"。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch6**（Assembler）|
| 🎥 Coursera | [Unit 6.1-6.6](https://www.coursera.org/learn/build-a-computer) |
| 🛠 工具 | 任意文本编辑器 + Python 3 |
| ⏱ 预计工时 | 8–15 小时 |

---

## 1. 汇编器是什么

**汇编器**（Assembler）是把汇编语言（人可读）翻译成机器码（机器可读）的工具：

```
.asm (人读)               .hack (机器读)
─────────────              ────────────────
@R0                  →     0000000000000000
D=M                  →     1111110000010000
@END                 →     0000000000001010
D;JGT                →     1110001100000001
(END)                →     (注释，不生成代码)
@END                 →     0000000000001010
0;JMP                →     1110101010000111
```

### 1.1 为什么需要"两遍"

考虑：
```asm
@END       ← 此处引用 END，但 END 还没定义
...
(END)      ← END 标号在这里
```

→ 第一次扫描时，不知道 `@END` 应该填什么地址。
**解决方法**：先扫描一遍**收集所有标号地址**，第二遍再生成代码。

---

## 2. 汇编器的 5 个核心步骤

```
.asm 文件
    │
    ▼
[1. 预处理]   去注释、去空行、去空白
    │
    ▼
[2. 第一遍]   收集所有 (LABEL) 的地址
    │
    ▼
[3. 第二遍]   逐条翻译指令：
              ├─ A 指令：@value 或 @SYMBOL
              │   ├─ 数字 → 直接转 15 位二进制
              │   └─ 符号 → 查 symbol table
              └─ C 指令：dest=comp;jump
                  ├─ comp → 6 位（含 a 位）
                  ├─ dest → 3 位
                  └─ jump → 3 位
    │
    ▼
[4. 输出]    每行一个 16 位二进制 → .hack
```

### 2.1 符号表（Symbol Table）

汇编器维护一个 dict：

```python
symbol_table = {
    # 预定义符号
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
    'SCREEN': 16384, 'KBD': 24576,
    'R0': 0, 'R1': 1, ..., 'R15': 15,
    # 用户标号（第一遍填）
    'END': 10, 'LOOP': 4, ...
    # 用户变量（第二遍填，从 RAM[16] 开始）
    'sum': 16, 'i': 17, ...
}
```

### 2.2 三种符号的区分

| 符号 | 出现方式 | 处理时机 | 例子 |
|------|---------|---------|------|
| **预定义** | ISA 固定 | 初始化时 | R0, SP, SCREEN |
| **标号** | `(LABEL)` | 第一遍 | `(END)` |
| **变量** | `@VAR`（VAR 不是预定义也不是标号）| 第二遍，自动分配地址 | `@sum` |

---

## 3. C 指令的二进制编码

```
1 1 1  a  c1 c2 c3 c4 c5 c6  d1 d2 d3  j1 j2 j3
└预定义  └┬┘ └──────┬──────┘ └──┬──┘ └──┬──┘
        a位   comp（6位）        dest    jump
```

### 3.1 comp 表

| comp | a | c1..c6 | 含义 |
|------|---|--------|------|
| 0    | 0 | 101010 | 0 |
| 1    | 0 | 111111 | 1 |
| -1   | 0 | 111010 | -1 |
| D    | 0 | 001100 | D |
| A    | 0 | 110000 | A |
| !D   | 0 | 001101 | ~D |
| !A   | 0 | 110001 | ~A |
| -D   | 0 | 001111 | -D |
| -A   | 0 | 110011 | -A |
| D+1  | 0 | 011111 | D+1 |
| A+1  | 0 | 110111 | A+1 |
| D-1  | 0 | 001110 | D-1 |
| A-1  | 0 | 110010 | A-1 |
| D+A  | 0 | 000010 | D+A |
| D-A  | 0 | 010011 | D-A |
| A-D  | 0 | 000111 | A-D |
| D&A  | 0 | 000000 | D&A |
| D\|A | 0 | 010101 | D\|A |
| M    | 1 | 110000 | M (= RAM[A]) |
| !M   | 1 | 110001 | ~M |
| ...  | 1 | ...    | (其他 M 版本与 A 版本一一对应) |

### 3.2 dest 表

| dest | d1 d2 d3 | 含义 |
|------|----------|------|
| null | 000      | 不写 |
| M    | 001      | 只写 M |
| D    | 010      | 只写 D |
| MD   | 011      | 写 M+D |
| A    | 100      | 只写 A |
| AM   | 101      | 写 A+M |
| AD   | 110      | 写 A+D |
| AMD  | 111      | 写 A+M+D |

### 3.3 jump 表

| jump | j1 j2 j3 | 含义 |
|------|----------|------|
| null | 000      | 不跳 |
| JGT  | 001      | > 0 |
| JEQ  | 010      | == 0 |
| JGE  | 011      | >= 0 |
| JLT  | 100      | < 0 |
| JNE  | 101      | != 0 |
| JLE  | 110      | <= 0 |
| JMP  | 111      | 无条件 |

---

## 4. Python 汇编器骨架

> 下面是**完整的可运行骨架**，主要翻译逻辑（`translate_c_instruction`）留给你完成。

### 4.1 `src/assembler.py`

```python
#!/usr/bin/env python3
"""
Hack 汇编器：把 .asm 翻译成 .hack
用法：python3 assembler.py input.asm [output.hack]
"""

import sys
from pathlib import Path


# ============= 表 =============
PREDEFINED_SYMBOLS = {
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
    'SCREEN': 16384, 'KBD': 24576,
    **{f'R{i}': i for i in range(16)},
}

COMP_TABLE = {
    '0':   '0101010', '1':   '0111111', '-1':  '0111010',
    'D':   '0001100', 'A':   '0110000', 'M':   '1110000',
    '!D':  '0001101', '!A':  '0110001', '!M':  '1110001',
    '-D':  '0001111', '-A':  '0110011', '-M':  '1110011',
    'D+1': '0011111', 'A+1': '0110111', 'M+1': '1110111',
    'D-1': '0001110', 'A-1': '0110010', 'M-1': '1110010',
    'D+A': '0000010', 'D+M': '1000010',
    'D-A': '0010011', 'D-M': '1010011',
    'A-D': '0000111', 'M-D': '1000111',
    'D&A': '0000000', 'D&M': '1000000',
    'D|A': '0010101', 'D|M': '1010101',
}

DEST_TABLE = {
    '':    '000', 'M':   '001', 'D':   '010', 'MD':  '011',
    'A':   '100', 'AM':  '101', 'AD':  '110', 'AMD': '111',
}

JUMP_TABLE = {
    '':    '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
    'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111',
}


# ============= 步骤 1：预处理 =============
def clean_line(line: str) -> str:
    """去除注释和首尾空白。注意：不能去掉整行内的合法注释位置（如有）"""
    # 去掉 // 注释
    if '//' in line:
        line = line.split('//', 1)[0]
    return line.strip()


# ============= 步骤 2：第一遍——收集标号 =============
def first_pass(lines: list[str]) -> dict[str, int]:
    symbol_table = dict(PREDEFINED_SYMBOLS)
    pc = 0   # 当前指令地址（标号不占地址）
    for line in lines:
        line = clean_line(line)
        if not line:
            continue
        if line.startswith('(') and line.endswith(')'):
            label = line[1:-1]
            symbol_table[label] = pc
        else:
            pc += 1
    return symbol_table


# ============= 步骤 3：第二遍——翻译 =============
def translate_a_instruction(symbol: str, symbol_table: dict, next_var_addr: list) -> str:
    """翻译 @value 或 @SYMBOL 为 16 位二进制"""
    if symbol.isdigit():
        addr = int(symbol)
    elif symbol in symbol_table:
        addr = symbol_table[symbol]
    else:
        # 新变量，从 RAM[16] 起分配
        addr = next_var_addr[0]
        symbol_table[symbol] = addr
        next_var_addr[0] += 1
    return f'{addr:016b}'


def translate_c_instruction(instruction: str) -> str:
    """翻译 dest=comp;jump 为 16 位二进制
    示例：
      'MD=D+1'       → dest='MD', comp='D+1', jump=''
      'D;JGT'        → dest='', comp='D', jump='JGT'
      '0;JMP'        → dest='', comp='0', jump='JMP'
      'M=D+M;JNE'    → dest='M', comp='D+M', jump='JNE'
    """
    # TODO: 解析 dest、comp、jump 三段
    # 提示：
    #   - 用 '=' 分隔 dest 和 comp+jump（如果有的话）
    #   - 用 ';' 分隔 comp 和 jump（如果有的话）
    #   - 查表得到 dest_bits, comp_bits, jump_bits
    #   - 返回 '111' + comp_bits + dest_bits + jump_bits
    raise NotImplementedError('留给你完成')


def second_pass(lines: list[str], symbol_table: dict) -> list[str]:
    output = []
    next_var_addr = [16]   # 用 list 包装可变变量
    for line in lines:
        line = clean_line(line)
        if not line:
            continue
        if line.startswith('('):
            continue
        if line.startswith('@'):
            symbol = line[1:]
            output.append(translate_a_instruction(symbol, symbol_table, next_var_addr))
        else:
            output.append(translate_c_instruction(line))
    return output


# ============= 主入口 =============
def assemble(input_path: str, output_path: str = None):
    input_file = Path(input_path)
    if output_path is None:
        output_path = str(input_file.with_suffix('.hack'))
    
    lines = input_file.read_text(encoding='utf-8').splitlines()
    
    symbol_table = first_pass(lines)
    binary_lines = second_pass(lines, symbol_table)
    
    Path(output_path).write_text('\n'.join(binary_lines) + '\n', encoding='utf-8')
    print(f'汇编完成：{input_path} → {output_path} ({len(binary_lines)} 条指令)')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法：python3 assembler.py input.asm [output.hack]')
        sys.exit(1)
    assemble(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
```

### 4.2 完成它

你需要补全 `translate_c_instruction` 函数。提示：

```python
def translate_c_instruction(instruction: str) -> str:
    dest = ''
    comp = instruction
    jump = ''
    
    if '=' in comp:
        dest, comp = comp.split('=', 1)
    if ';' in comp:
        comp, jump = comp.split(';', 1)
    
    return '111' + COMP_TABLE[comp] + DEST_TABLE[dest] + JUMP_TABLE[jump]
```

---

## 5. 测试

### 5.1 用官方测试文件

nand2tetris 提供 6 个测试用例（在 nand2tetris/tools/projects/06/）：

| 文件 | 内容 |
|------|------|
| `add/Add.asm` | 加法（最简单）|
| `max/Max.asm` | 求最大值 |
| `max/MaxL.asm` | Max 的长版本 |
| `rect/Rect.asm` | 画矩形 |
| `rect/RectL.asm` | Rect 的长版本 |
| `pong/Pong.asm` | 乒乓球游戏（最长）|

### 5.2 跑测试

```bash
cd Nand2Tetris/Project_06_Assembler

# 跑你自己的汇编器
python3 src/assembler.py tests/add/Add.asm tests/add/Add.hack

# 与官方 .hack 对比
diff tests/add/Add.hack tests/add/Add_expected.hack
```

如果 diff 输出为空，**你的汇编器是对的**。

### 5.3 用 P04 写的 Mult.asm 自测

```bash
python3 src/assembler.py ../Project_04_MachineLanguage/asm/Mult.asm Mult.hack
# 然后在 CPUEmulator 里跑 Mult.hack
```

---

## 6. 常见坑

### 坑 1：注释处理过激

```asm
D=M // this is M = RAM[A]
```

如果用 `line.split('//')[0]`，会得到 `D=M ` —— OK。
但如果注释里有 `=` 或 `;`，可能误判 C 指令格式。

→ **正确做法**：先去注释，再解析。

### 坑 2：标号不占指令地址

```asm
@END      ← pc=0
(END)     ← 不占 pc，但 END=1
@sum      ← pc=1
```

第一遍扫描时，遇到 `(LABEL)` 不增加 pc。

### 坑 3：变量地址分配顺序

`@x @y @x @y` 应该让 x 和 y 都映射到固定地址（不能每次都新分配）。

→ **检查符号是否已在表里**，再决定要不要新分配。

### 坑 4：大写/小写

Hack 规范约定符号**区分大小写**——`Loop` 和 `LOOP` 是不同符号。

### 坑 5：C 指令格式可能省略部分

| 写法 | dest | comp | jump |
|------|------|------|------|
| `M=D` | M | D | '' |
| `D;JGT` | '' | D | JGT |
| `D` | '' | D | '' |
| `0;JMP` | '' | 0 | JMP |
| `M=D+M;JNE` | M | D+M | JNE |

→ 解析时**三种情况都要考虑**。

---

## 7. 与本项目其他模块的连接

### 7.1 与 [`Capstone/cpu_simulator/assembler.py`](../../Capstone/cpu_simulator/assembler.py) 的对照

本项目 Capstone 有一个 **RV32I 汇编器**。直接对比两个文件：

| 方面 | Hack 汇编器（P06）| RV32I 汇编器（Capstone）|
|------|-------------------|--------------------------|
| 指令数 | 2 种（A + C）| 37 条基础 |
| 编码长度 | 16 位固定 | 32 位固定 |
| 立即数处理 | 15 位（A 指令）| 12 位 + 移位 / LUI+ADDI |
| 符号表 | 简单 dict | 简单 dict（一样）|
| 伪指令 | 无 | `li`, `mv`, `nop` 等 |
| 重定位 | 不支持 | 不支持（教学版）|
| **结构相似度** | — | **~85%** |

→ **学完 P06 后看 RV32I 汇编器，你会觉得"套路完全一样，只是指令集不同"**。

### 7.2 与 [`Expert_11_Compiler_Research`](../../Expert_11_Compiler_Research/) 的连接

P06 是**最简汇编器**。真实工业汇编器（GNU `as`、LLVM `llvm-mc`）多得多：
- 支持几十种伪指令
- 支持宏
- 支持重定位（链接器使用）
- 支持条件汇编
- 支持 ELF/DWARF 调试信息

但**核心思想与 P06 完全一致**：扫两遍 + 符号表 + 查表翻译。

### 7.3 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

汇编器是**横跨 L4（ABI）和 L3（ISA）的工具**：
- 它输出 ISA 层的机器码
- 但它要遵守 ABI 层的某些约定（如调用约定导致的符号分配）

---

## 8. 扩展挑战

1. **加宏支持**：让 `@R0` 等价于 `@0`（其实预定义符号已经做了类似事）
2. **加 `.word` 伪指令**：直接插入一个 16 位数据
3. **加 ELF 输出**：让你的汇编器能生成可被 Linux 加载的 ELF（要求支持重定位）
4. **写反汇编器**：把 `.hack` 翻回 `.asm`（用于调试）
5. **写 RV32I 汇编器**：参考 Capstone，把 RISC-V RV32I 的 37 条指令都支持

---

## 9. 检查清单

- [ ] 能解释"两遍扫描"为什么必要
- [ ] 理解符号表的三类条目（预定义、标号、变量）
- [ ] 能默写 Hack C 指令的 16 位编码格式
- [ ] 完成 `translate_c_instruction` 函数
- [ ] 跑通全部 6 个官方测试，与期望输出 byte-for-byte 一致
- [ ] 能用你的汇编器跑你 P04 写的 Mult.asm

---

## 📌 下一步

完成 P06 后，进 [`Project_07_VMTranslator_I/`](../Project_07_VMTranslator_I/)。
你将实现**栈式虚拟机**——
**VM 是 Jack 编译器和 Hack 汇编之间的中间层**，是现代编译器（如 Java JVM、Python bytecode、WebAssembly）的核心思想。
