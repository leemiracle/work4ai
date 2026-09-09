# Project 01 — Boolean Logic：从一个 Nand 拼出全部布尔逻辑

> **一句话目标**：用**唯一原语 Nand**，搭出 Not / And / Or / Xor / Mux / DMux 及其多位/多路版本——**15 个 .hdl 文件**。
>
> 这是整个 Nand2Tetris 的入口，也是"从硅到 App"长跑的第一步。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements of Computing Systems* 2nd ed. **Ch1**（Boolean Logic） |
| 📙 中文书 | 《计算机系统要素》第 1 章 |
| 🎥 Coursera | [Unit 1.1-1.6](https://www.coursera.org/learn/build-a-computer) |
| 🛠 工具 | **HardwareSimulator**（nand2tetris 软件套件）|
| ⏱ 预计工时 | 8–15 小时（零基础） / 3–5 小时（有数字电路基础）|

---

## 1. 你将构建的 15 个芯片

> 全部用 Nand 搭，**不允许使用书里没教过的原语**。

| # | 芯片名 | 输入 → 输出 | 难度 | 备注 |
|---|--------|------------|------|------|
| 1 | `Not` | in → out | ⭐ | Nand(in, in) |
| 2 | `And` | a, b → out | ⭐ | De Morgan |
| 3 | `Or` | a, b → out | ⭐ | De Morgan |
| 4 | `Xor` | a, b → out | ⭐⭐ | 4 个 Nand |
| 5 | `Mux` | a, b, sel → out | ⭐⭐ | 2 选 1 |
| 6 | `DMux` | in, sel → a, b | ⭐⭐ | 1 分 2 |
| 7 | `Not16` | 16 位 Not | ⭐ | 多位版 |
| 8 | `And16` | 16 位 And | ⭐ | 多位版 |
| 9 | `Or16` | 16 位 Or | ⭐ | 多位版 |
| 10 | `Mux16` | 16 位 Mux | ⭐⭐ | 多位版 |
| 11 | `Or8Way` | 8 位 → 1 位 Or | ⭐ | 8 路归约 |
| 12 | `Mux4Way16` | 4 选 1（16 位）| ⭐⭐⭐ | 三级 Mux |
| 13 | `Mux8Way16` | 8 选 1（16 位）| ⭐⭐⭐ | 三级 Mux |
| 14 | `DMux4Way` | 1 分 4 | ⭐⭐⭐ | 二级 DMux |
| 15 | `DMux8Way` | 1 分 8 | ⭐⭐⭐ | 三级 DMux |

---

## 2. 关键概念速览

### 2.1 为什么是 Nand？

**Nand = Not And**，真值表：

| a | b | Nand(a,b) |
|---|---|-----------|
| 0 | 0 | 1 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | **0** |

**Nand 是函数完备的**（functionally complete）——任何布尔函数都能仅用 Nand 表达。
这就是为什么 Nand 是 Nand2Tetris 的**唯一原语**：所有更高层的逻辑都能从它"长"出来。

> 💡 **工业现实**：CMOS 工艺里，Nand 比 And 更容易直接实现（4 个晶体管 vs 6 个）。
> 这也是为什么真实芯片里 Nand/Nor/Not 这种"非"型门用得多。本项目用 Nand 作原语既教学又贴近工业。

### 2.2 关键恒等式（你应该熟记）

```
Not(x)     = Nand(x, x)
And(a, b)  = Not(Nand(a, b))
Or(a, b)   = Nand(Not(a), Not(b))           ← De Morgan
Xor(a, b)  = And(Or(a,b), Nand(a,b))         ← 4 Nand 实现
Mux(a,b,s) = Or(And(a, Not(s)), And(b, s))
DMux(i,s)  = (And(i, Not(s)), And(i, s))     ← 输出 a, b
```

### 2.3 HDL 是什么

Nand2Tetris 的 HDL 是**文本硬件描述语言**，类似简化版 Verilog。一个 HDL 文件描述一个芯片：

```hdl
CHIP Not {
    IN  in;        // 输入端口
    OUT out;       // 输出端口

    PARTS:         // 内部用其他芯片拼出来
    Nand(a=in, b=in, out=out);
}
```

**关键语法**：
- `IN` / `OUT`：声明端口
- `PARTS:`：内部实现（用其他芯片搭）
- 用 `;` 结束每个 part
- 内部线（wire）自动创建，名字对应即可
- 多位总线用 `a[0..15]` 或 `a[2]` 索引

---

## 3. 骨架代码（部分核心芯片）

> 我们提供 **Not / And / Or / Xor / Mux / DMux** 的**完整答案**作为入门样本。
> 其余 10 个芯片需要你自己写——这是 P01 的真正练习。

### 3.1 `Not.hdl`（最简单，入门）

```hdl
// 文件：hdl/Not.hdl
// 实现：Not(in) = Nand(in, in)

CHIP Not {
    IN in;
    OUT out;
    PARTS:
    Nand(a=in, b=in, out=out);
}
```

### 3.2 `And.hdl`

```hdl
// 文件：hdl/And.hdl
// 实现：And(a,b) = Not(Nand(a,b))

CHIP And {
    IN a, b;
    OUT out;
    PARTS:
    Nand(a=a, b=b, out=c);
    Not(in=c, out=out);
}
```

### 3.3 `Or.hdl`（De Morgan）

```hdl
// 文件：hdl/Or.hdl
// 实现：Or(a,b) = Nand(Not a, Not b)

CHIP Or {
    IN a, b;
    OUT out;
    PARTS:
    Not(in=a, out=na);
    Not(in=b, out=nb);
    Nand(a=na, b=nb, out=out);
}
```

### 3.4 `Xor.hdl`

```hdl
// 文件：hdl/Xor.hdl
// 实现：4 个 Nand 的经典实现

CHIP Xor {
    IN a, b;
    OUT out;
    PARTS:
    Nand(a=a, b=b, out=c1);    // c1 = Nand(a, b)
    And(a=a, b=c1, out=c2);    // c2 = And(a, Nand(a,b)) = a & ¬(a&b)
    And(a=b, b=c1, out=c3);    // c3 = b & ¬(a&b)
    Or(a=c2, b=c3, out=out);   // a&¬(a&b) | b&¬(a&b) = a ^ b
}
```

> 💡 **更优雅的 4-Nand 实现**：
> ```
> Nand(a,b) → c
> Nand(a,c) → d
> Nand(b,c) → e
> Nand(d,e) → out
> ```
> 用 HardwareSimulator 自己验证这两种实现等价。

### 3.5 `Mux.hdl`（2 选 1）

```hdl
// 文件：hdl/Mux.hdl
// 实现：Mux(a,b,sel) = a if sel=0 else b

CHIP Mux {
    IN a, b, sel;
    OUT out;
    PARTS:
    Not(in=sel, out=nsel);
    And(a=a, b=nsel, out=x);   // x = a & ¬sel
    And(a=b, b=sel, out=y);    // y = b & sel
    Or(a=x, b=y, out=out);
}
```

### 3.6 `DMux.hdl`（1 分 2）

```hdl
// 文件：hdl/DMux.hdl
// 实现：sel=0 → a=in, b=0；sel=1 → a=0, b=in

CHIP DMux {
    IN in, sel;
    OUT a, b;
    PARTS:
    Not(in=sel, out=nsel);
    And(a=in, b=nsel, out=a);
    And(a=in, b=sel,  out=b);
}
```

---

## 4. 运行与测试

### 4.1 准备工作

1. 下载 [nand2tetris Software Suite](https://www.nand2tetris.org/software)
2. 解压到任意目录，进入 `tools/`
3. 启动 **HardwareSimulator**：
   ```bash
   # Linux/Mac
   sh HardwareSimulator.sh
   # Windows
   HardwareSimulator.bat
   ```

### 4.2 测试一个芯片

1. 在 HardwareSimulator 里：`File → Load Script` 加载测试脚本（`Xor.tst`）
2. 或 `File → Load Chip` 加载你的 `.hdl`
3. 按 `Run → Run to end` 或 Ctrl-R

### 4.3 测试脚本长什么样（以 `Xor.tst` 为例）

```tst
// Xor.tst
load Xor.hdl,
output-list a b out;
set a 0, set b 0, eval, output;
set a 0, set b 1, eval, output;
set a 1, set b 0, eval, output;
set a 1, set b 1, eval, output;
```

期望输出 `Xor.cmp`：
```
| a | b | out |
| 0 | 0 |  0  |
| 0 | 1 |  1  |
| 1 | 0 |  1  |
| 1 | 1 |  0  |
```

### 4.4 一键跑完 P01 全部 15 个测试

```bash
cd Nand2Tetris/Project_01_BooleanLogic
# 假设 nand2tetris 工具在 /opt/nand2tetris/tools/
for tst in Not And Or Xor Mux DMux Not16 And16 Or16 Mux16 Or8Way \
           Mux4Way16 Mux8Way16 DMux4Way DMux8Way; do
    echo "=== Testing $tst ==="
    /opt/nand2tetris/tools/HardwareSimulator.sh $tst.tst
done
```

---

## 5. 常见坑

### 坑 1：HDL 是**结构性**的，不是**行为性**的

```hdl
// ❌ 错：HDL 不支持表达式
out = a & b;        // 这不是 HDL！

// ✅ 对：要"用芯片搭"
And(a=a, b=b, out=out);
```

### 坑 2：端口名必须严格匹配

```hdl
CHIP Mux {
    IN a, b, sel;          // sel 是端口名
    OUT out;
    PARTS:
    And(a=a, b=selector)   // ❌ selector 不存在！必须叫 sel
}
```

### 坑 3：总线位宽要匹配

```hdl
// ❌ 错：1 位连到 16 位
And16(a=true, b=true, out=out);   // a 应该是 16 位

// ✅ 对
And16(a[0..15]=true, b[0..15]=true, out=out);
```

### 坑 4：忘了一个 part 不能定义输入

```hdl
// ❌ 错：Nand 的输入必须来自 IN 或之前的 wire
Nand(a=x, b=y, out=z);  // x 和 y 还没定义
```

### 坑 5：未使用输出会警告

```hdl
Mux(a=a, b=b, sel=s, out=result, out=extra);  // extra 没用上
```

→ HardwareSimulator 会报错。要么删掉，要么让它在 CHIP 的 OUT 里出现。

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Expert_03_HW_Designer/rtl/alu.v`](../../Expert_03_HW_Designer/rtl/) 的对比

| 方面 | Nand2Tetris HDL | 工业级 Verilog |
|------|-----------------|----------------|
| 风格 | **结构化**（永远用芯片搭芯片）| **混合**（可用 `assign a = b & c;`）|
| 时钟 | 隐式（DFF 自动接 clock）| 显式 `always @(posedge clk)` |
| 参数化 | 不支持 | 支持 `parameter WIDTH = 16` |
| 仿真 | 自带 HardwareSimulator | iverilog / ModelSim / VCS |
| 综合 | ❌ 不可综合 | ✅ 可综合为真实电路 |
| 学完 Nand2Tetris 看 Verilog | "原来如此简单" | 直接看 [`Expert_03`](../../Expert_03_HW_Designer/rtl/) 的 ALU 源码 |

### 6.2 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

P01 完成后，你已经造出了 **L1 物理实现** 的抽象（用 HDL 描述逻辑门），
也开始了 **L2 微架构** 的旅程（用门搭出更高层模块）。

### 6.3 与 [`背景知识/Great_Ideas_体系结构思想.md`](../../背景知识/Great_Ideas_体系结构思想.md) 的连接

- **Great Idea #1：Abstraction（抽象）** ← P01 最直接的体现
- **Great Idea #8：Interface（接口）** ← 每个 CHIP 的 IN/OUT 就是接口

---

## 7. 扩展挑战

完成 15 个芯片后，可以挑战：

1. **手画 4-Nand Xor** 的电路图（在纸上，验证 HDL）
2. **用 Nor 作原语**重新搭 15 个芯片（Nor 也函数完备）
3. **用最少 Nand 实现 Xor** —— 已知下界是 4 个，你能用 3 个吗？（提示：不能）
4. **Mux 是万能的** —— 用 Mux 搭出 Not / And / Or / Xor
5. **加法器优化** —— 阅读 *Harris & Harris* 《数字设计和计算机体系结构》关于 Carry-Lookahead Adder 的章节，思考如何用 Nand 搭 CLA

---

## 8. 检查清单（学完应该会）

- [ ] 能解释"为什么 Nand 是函数完备的"
- [ ] 能默写 Not / And / Or / Xor 的 Nand 实现
- [ ] 理解 **De Morgan 律**（Or 怎么用 Nand 表达）
- [ ] 能解释 **Mux 和 DMux 的对偶关系**
- [ ] 能在 30 分钟内用 Nand 搭出 Xor（不看答案）
- [ ] 理解 HDL **结构化**与 Verilog **行为化**的区别
- [ ] 能跑通全部 15 个测试，HardwareSimulator 不报错

---

## 📌 下一步

完成 P01 后，进 [`Project_02_BooleanArithmetic/`](../Project_02_BooleanArithmetic/)。
你将用 P01 的逻辑门搭出 **HalfAdder → FullAdder → 16 位 Adder → ALU**——
**ALU 是 P02 的高潮，也是 CPU 的第一个核心组件**。

> 💡 完成 P01-P02 后，回头读本项目 [`Lab01 §3.4`](../../Lab01_ISA与汇编/)——
> 看飞腾真机的整数算术延迟实测值（div 10.4 cyc、fadd 2.0 cyc），
> 你会理解"教学 ALU 简单结构" vs "工业 ALU 高速流水" 的差距。
