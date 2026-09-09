# Project 02 — Boolean Arithmetic：从逻辑门到能算加减的 ALU

> **一句话目标**：用 P01 的逻辑门搭出 **HalfAdder → FullAdder → Add16 → ALU16**——
> **ALU 是 CPU 的第一个核心组件**，P02 也是 Nand2Tetris 硬件部分的概念高潮。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch2**（Boolean Arithmetic）|
| 🎥 Coursera | [Unit 2.1-2.7](https://www.coursera.org/learn/build-a-computer) |
| 🛠 工具 | **HardwareSimulator** |
| ⏱ 预计工时 | 6–10 小时 |

---

## 1. 你将构建的 4 个芯片

| # | 芯片 | 功能 | 难度 |
|---|------|------|------|
| 1 | `HalfAdder` | 2 位加法（a+b → sum, carry）| ⭐ |
| 2 | `FullAdder` | 3 位加法（a+b+c → sum, carry）| ⭐ |
| 3 | `Add16` | 16 位加法（16 个 FullAdder 级联）| ⭐⭐ |
| 4 | `Inc16` | 16 位 +1 | ⭐ |
| 5 | **`ALU`** | Hack ALU（6 个控制位 × 2 输入）| ⭐⭐⭐⭐⭐ |

---

## 2. 关键概念

### 2.1 二进制加法（5 分钟回顾）

| 运算 | 例子 | 结果 |
|------|------|------|
| 半加器 | 1 + 1 | sum=0, carry=1 |
| 全加器 | 1 + 1 + 1（进位）| sum=1, carry=1 |
| 16 位加法器 | 级联 16 个全加器 | 进位链 |
| **行波进位加法器（Ripple Carry Adder）** | Hack 用这个 | 慢，但简单 |
| 先行进位加法器（Carry-Lookahead）| 工业用 | 快，但复杂 |

### 2.2 Hack ALU 的精巧设计

Hack 的 ALU 用 **6 个控制位**操控，**没有真正的算术逻辑**——所有运算都用 **Nand 派生**的逻辑门做。其哲学是：

> "ALU 应该是**最少的算术** + **最多的选择**" —— Nisan

6 个控制位：

```
zx  nx  zy  ny  f  no
```

- `zx/nx`：把 x 输入**强制置零**再**按位取反**（两步可以任意组合出 0/1/x/~x）
- `zy/ny`：同理对 y
- `f`：选 x+y（`f=1`）还是 x&y（`f=0`）
- `no`：输出按位取反

**6 位控制位 = 64 种功能**，但常用的就 ~18 种：

| zx | nx | zy | ny | f | no | 输出 | 含义 |
|----|----|----|----|---|----|------|------|
| 1  | 0  | 1  | 0  | 1 | 0  | 0    | 常数 0 |
| 1  | 1  | 1  | 1  | 1 | 1  | 1    | 常数 1 |
| 1  | 1  | 1  | 0  | 1 | 1  | -1   | 常数 -1 |
| 0  | 0  | 1  | 1  | 0 | 0  | x    | 恒等 |
| 1  | 1  | 0  | 0  | 0 | 0  | y    | 恒等 |
| 0  | 0  | 1  | 1  | 0 | 1  | !x   | 按位非 |
| 1  | 1  | 0  | 0  | 0 | 1  | !y   | 按位非 |
| 0  | 0  | 1  | 1  | 1 | 1  | -x   | 负数 |
| 1  | 1  | 0  | 0  | 1 | 1  | -y   | 负数 |
| 0  | 1  | 1  | 1  | 1 | 1  | x+1  | 自增 |
| 1  | 1  | 0  | 1  | 1 | 1  | y+1  | 自增 |
| 0  | 0  | 1  | 1  | 1 | 0  | x-1  | 自减 |
| 1  | 1  | 0  | 1  | 1 | 0  | y-1  | 自减 |
| 0  | 0  | 0  | 0  | 1 | 0  | x+y  | 加法 |
| 1  | 1  | 0  | 0  | 1 | 1  | y-x  | 减法 |
| 0  | 1  | 0  | 0  | 1 | 1  | x-y  | 减法 |
| 0  | 0  | 0  | 0  | 0 | 0  | x&y  | 按位与 |
| 0  | 1  | 0  | 1  | 0 | 1  | x\|y | 按位或 |

**两个标志位输出**：
- `zr`：out 是否为 0？（全 16 位按位 Or，再 Not）
- `ng`：out 是否为负？（MSB 是否为 1）

### 2.3 二进制补码（速读）

```
原码 1:  0000 0000 0000 0001
反码 -1: 1111 1111 1111 1110   (按位取反)
补码 -1: 1111 1111 1111 1111   (反码 + 1)
```

**取相反数的算法**：`~x + 1`，这就是为什么 `-x` 在 ALU 表里需要 `nx=1, f=1, no=1`（取反 + 1 + 按位非）。

---

## 3. 骨架代码

### 3.1 `HalfAdder.hdl`

```hdl
CHIP HalfAdder {
    IN a, b;
    OUT sum, carry;
    PARTS:
    Xor(a=a, b=b, out=sum);          // 和
    And(a=a, b=b, out=carry);        // 进位
}
```

### 3.2 `FullAdder.hdl`

```hdl
CHIP FullAdder {
    IN a, b, c;          // c 是上一位的进位
    OUT sum, carry;
    PARTS:
    HalfAdder(a=a, b=b, sum=s1, carry=c1);
    HalfAdder(a=s1, b=c, sum=sum, carry=c2);
    Or(a=c1, b=c2, out=carry);
}
```

### 3.3 `Add16.hdl`（16 位行波进位加法器）

```hdl
CHIP Add16 {
    IN a[16], b[16];
    OUT out[16];
    PARTS:
    FullAdder(a=a[0],  b=b[0],  c=false, sum=out[0],  carry=c1);
    FullAdder(a=a[1],  b=b[1],  c=c1,    sum=out[1],  carry=c2);
    FullAdder(a=a[2],  b=b[2],  c=c2,    sum=out[2],  carry=c3);
    FullAdder(a=a[3],  b=b[3],  c=c3,    sum=out[3],  carry=c4);
    FullAdder(a=a[4],  b=b[4],  c=c4,    sum=out[4],  carry=c5);
    FullAdder(a=a[5],  b=b[5],  c=c5,    sum=out[5],  carry=c6);
    FullAdder(a=a[6],  b=b[6],  c=c6,    sum=out[6],  carry=c7);
    FullAdder(a=a[7],  b=b[7],  c=c7,    sum=out[7],  carry=c8);
    FullAdder(a=a[8],  b=b[8],  c=c8,    sum=out[8],  carry=c9);
    FullAdder(a=a[9],  b=b[9],  c=c9,    sum=out[9],  carry=c10);
    FullAdder(a=a[10], b=b[10], c=c10,   sum=out[10], carry=c11);
    FullAdder(a=a[11], b=b[11], c=c11,   sum=out[11], carry=c12);
    FullAdder(a=a[12], b=b[12], c=c12,   sum=out[12], carry=c13);
    FullAdder(a=a[13], b=b[13], c=c13,   sum=out[13], carry=c14);
    FullAdder(a=a[14], b=b[14], c=c14,   sum=out[14], carry=c15);
    FullAdder(a=a[15], b=b[15], c=c15,   sum=out[15], carry=c16);
}
```

### 3.4 `Inc16.hdl`

```hdl
CHIP Inc16 {
    IN in[16];
    OUT out[16];
    PARTS:
    Add16(a=in, b[0]=true, b[1..15]=false, out=out);
}
```

### 3.5 `ALU.hdl`（核心！）

> 这是 P02 的灵魂。我们**只给骨架**，关键部分留给你完成。

```hdl
/**
 * Hack ALU. 6 个控制位：zx nx zy ny f no
 * 计算 18 种常用功能（见 §2.2 表格）
 */
CHIP ALU {
    IN
        x[16], y[16],   // 16 位输入
        zx,             // x 输入置零
        nx,             // x 输入取反
        zy,             // y 输入置零
        ny,             // y 输入取反
        f,              // f=1 → x+y, f=0 → x&y
        no;             // 输出取反

    OUT
        out[16],        // 16 位输出
        zr,             // out == 0 ?
        ng;             // out < 0 ?

    PARTS:
    // ---- 第 1 步：处理 x 输入 ----
    Mux16(a=x, b=false, sel=zx, out=x1);     // x1 = zx ? 0 : x
    Not16(in=x1, out=notx1);
    Mux16(a=x1, b=notx1, sel=nx, out=x2);    // x2 = nx ? ~x1 : x1

    // ---- 第 2 步：处理 y 输入 ----
    // TODO: 类似 x，你自己写

    // ---- 第 3 步：选择 x+y 还是 x&y ----
    // TODO: Add16 + And16 + Mux16，按 f 选择

    // ---- 第 4 步：处理 no（输出取反）----
    // TODO

    // ---- 第 5 步：计算 zr 和 ng 标志 ----
    // ng = out[15]
    Or8Way(in[0..7]=out[0..7],  out=lowOr);
    Or8Way(in[0..7]=out[8..15], out=highOr);
    Or(a=lowOr, b=highOr, out=anyOne);
    Not(in=anyOne, out=zr);                  // zr = (out == 0)
}
```

---

## 4. 测试

```bash
# 在 HardwareSimulator 里依次跑
HardwareSimulator.sh hdl/HalfAdder.tst
HardwareSimulator.sh hdl/FullAdder.tst
HardwareSimulator.sh hdl/Add16.tst
HardwareSimulator.sh hdl/Inc16.tst
HardwareSimulator.sh hdl/ALU.tst
```

ALU 测试集（`ALU.cmp`）会跑 **30+ 组控制位 + 输入**，覆盖全部 18 种功能 + 边界（0、-1、MAX_INT、MIN_INT）。

---

## 5. 常见坑

### 坑 1：补码取负漏了 `+1`

```python
# ❌ 错（这是反码）
-x = ~x

# ✅ 对（补码）
-x = ~x + 1
```

在 ALU 里实现 `-x` 时，你需要：`zx=1, nx=1, zy=1, ny=0, f=1, no=1`
意思：y 跳过（zy=1→ny=0 → y 变为 0），x 取反再 +1（这是 f=1 把 ~x 和 0 相加），最后整体取反 = -x。
**如果你忘了 +1，所有减法都会少 1**。

### 坑 2：zr 和 ng 必须同时正确

```hdl
// ❌ 错：只算 zr 没算 ng
Or16(in=out, out=anyOne);
Not(in=anyOne, out=zr);
// 忘了 ng = out[15]
```

CPU 的条件跳转指令**完全依赖 zr/ng**——一个错就全错。

### 坑 3：Hack ALU 不区分有符号/无符号

Hack 假设所有数都是补码有符号 16 位整数。`x+y` 在溢出时不会报错，而是 wrap around。这是设计选择（简化），工业 CPU（ARM/x86）有专门的溢出标志（V flag）。

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Lab01 §3.4`](../../Lab01_ISA与汇编/) 的连接

读完 P02 的 ALU 后，去看本项目 Lab01 的实测数据：

| 操作 | Hack ALU（理论）| 飞腾 D3000M（`[实测]`）| 差距 |
|------|----------------|-------------------------|------|
| 整数 add | ~16 个 FullAdder 行波 → ~32 门延迟 | **1 cyc @ 2.5GHz = 0.4 ns** | 飞腾用 CLA + 流水线 + 前递 |
| 整数 mul | 软件（多次移位加）| **3 cyc** | 飞腾有硬件乘法器（Booth 算法）|
| 整数 div | 软件（长除法）| **10.4 cyc** | 飞腾有 SRT 除法器 |

→ **P02 的 ALU 是单周期组合逻辑，飞腾是流水线 + 硬件乘除法器**。

### 6.2 与 [`Expert_03_HW_Designer/rtl/alu.v`](../../Expert_03_HW_DesignER/rtl/alu.v) 的对比

直接打开 `Expert_03_HW_Designer/rtl/alu.v` 看 Verilog 版本：
- 10 条 RV32I ALU 操作
- 用 `always @(*) case ... endcase` 行为级描述
- 比 Hack ALU **简单**（因为不用凑 Nand）

### 6.3 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

P02 的 ALU 完成了 **L2 微架构** 的第一个组件。
你现在已经造出了"CPU 的左膀"（运算器）——右膀"控制器 + 寄存器"会在 P03、P05 完成。

---

## 7. 扩展挑战

1. **MIPS 风格 ALU**：用 Verilog 重写一个 32 位 ALU，支持 SLT（Set-Less-Than）、shift、bool——见 [`Expert_03/rtl/alu.v`](../../Expert_03_HW_Designer/rtl/alu.v)
2. **Carry-Lookahead Adder**：阅读 Harris & Harris §5.3，把 `Add16` 换成 CLA，看延迟差多少
3. **Booth 乘法器**：实现 16×16 → 32 位有符号乘法（Hack 不要求，但工业必需）
4. **用最少的 Nand 实现 -x** —— 应该是 16 个（每个 Not = 1 Nand）+ 1 个 Add16（约 16×9=144 个）≈ 160 Nand。你能更少吗？

---

## 8. 检查清单

- [ ] 能默写 HalfAdder / FullAdder 的逻辑方程
- [ ] 理解 Hack ALU 的 6 个控制位含义
- [ ] 能在 1 小时内用 HDL 拼出 ALU（不看答案）
- [ ] 理解为什么 `-x = ~x + 1`（补码）
- [ ] 知道 zr 和 ng 怎么计算（且为什么 CPU 跳转指令需要它们）
- [ ] ALU 测试 30+ 组全部通过

---

## 📌 下一步

完成 P02 后，进 [`Project_03_SequentialLogic/`](../Project_03_SequentialLogic/)。
你将引入**时钟和状态**（DFF → Bit → Register → RAM）——
**没有时序，CPU 就只能算单次运算；有时序，CPU 才能存程序、存数据、跨周期运算**。
