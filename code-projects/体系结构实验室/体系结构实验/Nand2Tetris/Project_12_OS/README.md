# Project 12 — Operating System：用 Jack 写一个完整 OS

> **一句话目标**：用 Jack 语言实现 **8 个 OS 类**——
> 数学库、字符串、数组、内存、屏幕、键盘、输出、系统。
> **完成后，你的 Hack 计算机拥有完整的操作系统**——从硬件到 OS 全部自造。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch12**（Operating System）|
| 🎥 Coursera | [Unit 12.1-12.6](https://www.coursera.org/learn/nand2tetris2) |
| ⏱ 预计工时 | 30–50 小时（最难、最长的 project）|

---

## 1. 你将写的 8 个 OS 类

| 类名 | 功能 | 复杂度 |
|------|------|--------|
| `Math` | 数学（multiply / divide / sqrt / abs / min / max）| ⭐⭐ |
| `String` | 字符串（创建/拼接/转换）| ⭐⭐⭐ |
| `Array` | 数组（new / dispose）| ⭐ |
| `Memory` | 内存（peek / poke / alloc / deAlloc）| ⭐⭐⭐ |
| `Screen` | 屏幕（clear / drawPixel / drawLine / drawRect / drawCircle）| ⭐⭐⭐⭐ |
| `Keyboard` | 键盘（keyPressed / readChar / readLine / readInt）| ⭐⭐⭐ |
| `Output` | 文本输出（printString / printInt / printChar / println）| ⭐⭐⭐ |
| `Sys` | 系统（init / halt / wait / error）| ⭐⭐ |

---

## 2. 为什么 OS 要用高级语言写？

**Nand2Tetris 的反直觉设计**：OS 不是"硬件的延伸"，而是**用 Jack 写的普通类库**。

```
应用层（P09 写的俄罗斯方块）
   │ 调用
   ▼
OS 层（P12 写的 Math/String/...）  ← 也是 Jack 代码
   │ 调用
   ▼
VM 层（P07-P08 翻译器）
   │
   ▼
Hack 汇编（P06 汇编器）
   │
   ▼
Hack 机器码（P05 Computer.hdl 执行）
```

**关键洞察**：OS 与应用的区别不在"语言"，而在**它管什么资源**：
- 应用：调用 OS 提供的服务
- OS：直接操作硬件（屏幕 RAM、键盘 RAM、内存位）

---

## 3. 核心类的设计要点

### 3.1 `Math`（数学库）

Jack 没有 `*` 和 `/` 的硬件支持——**ALU 只有加法和位运算**！
**所以乘除法必须用 Jack 软件实现**。

```jack
class Math {
    function void init() { return; }    // 占位（未来可加查找表）
    
    function int multiply(int a, int b) {
        // 用位运算实现：a × b = sum of (a << i) if b[i]=1
        var int result, i, ai;
        let result = 0;
        let ai = a;
        for (let i = 0; i < 16; let i = i + 1) {
            if (~(b & 1) = 0) {           // b 的最低位为 1
                let result = result + ai;
            }
            let ai = ai + ai;             // ai × 2（左移）
            let b = b / 2;                // ❌ 不能用除法！
            // ✅ 正确做法：用 ~ 运算 + 右移位
        }
        return result;
    }
    
    function int divide(int a, int b) {
        // 用"长除法"实现，类似硬件 SRT 算法
        ...
    }
    
    function int sqrt(int x) {
        // 牛顿迭代法
        var int g, last;
        let g = x;
        while (true) {
            let last = g;
            let g = (g + x / g) / 2;
            if (~(g < last) & (g = last)) { return g; }
            // ... 边界条件
        }
    }
}
```

→ **"软件乘法器"是 P12 最有教学价值的一环**——
让你理解 [`Lab01 §3.4`](../../Lab01_ISA与汇编/) 里"飞腾 mul 指令 3 cyc"背后的硬件乘法器（Booth 算法）有多重要。

### 3.2 `Memory`（内存管理）

```jack
class Memory {
    static Array freeList;   // 空闲链表头
    
    function int peek(int address) {
        return Memory.peek(address);   // 通过 Jack 编译器的特殊处理
        // 实际：return address[0]
    }
    
    function void poke(int address, int value) {
        let address[0] = value;
        return;
    }
    
    function int alloc(int size) {
        // 实现 first-fit 自由链表分配
        ...
    }
    
    function void deAlloc(Array o) {
        // 把对象放回 freeList
        ...
    }
}
```

### 3.3 `Screen`（屏幕驱动）

```
RAM[16384] ← 屏幕第 0 行的左 16 个像素（每像素 1 位）
RAM[16385] ← 屏幕第 0 行的右 16 个像素
...
RAM[24575] ← 屏幕最右下角的 16 像素
```

```jack
class Screen {
    function void drawPixel(int x, int y) {
        var int addr, bit;
        let addr = 16384 + (y * 32) + (x / 16);   // 字地址
        let bit = x mod 16;                        // 位偏移
        // RAM[addr] |= (1 << bit)
        do Memory.poke(addr, Memory.peek(addr) | Screen.bitMask(bit));
        return;
    }
    
    function void drawLine(int x1, int y1, int x2, int y2) {
        // Bresenham 算法（整数运算，无浮点）
        ...
    }
    
    function void drawCircle(int x, int y, int r) {
        // 中点圆算法
        ...
    }
}
```

### 3.4 `Keyboard`（键盘驱动）

```
RAM[24576] ← 当前按下的键码，0 表示无键
```

| 键码 | 含义 |
|------|------|
| 0 | 无键 |
| 1–10 | 1–9 + 0 |
| 11–36 | A–Z |
| 33–64 | ! " # ... ? @ |
| 129 | ←（左箭头）|
| 130 | ↑ |
| 131 | → |
| 132 | ↓ |
| 133 | , |
| 134 | . |
| 135 | - |
| 140 | F1 |
| 141 | F2 |
| ... | ... |

```jack
class Keyboard {
    function char keyPressed() {
        return Memory.peek(24576);
    }
    
    function char readChar() {
        var char c;
        while (Keyboard.keyPressed() = 0) {}   // 等待按键
        let c = Keyboard.keyPressed();
        while (~(Keyboard.keyPressed() = 0)) {} // 等待松开
        do Output.printChar(c);                 // 回显
        return c;
    }
    
    function String readLine(String message) {
        var String s;
        var char c;
        do Output.printString(message);
        let s = String.new(50);
        let c = Keyboard.readChar();
        while (~(c = 10)) {    // 10 = 换行（NewLine）
            do s.appendChar(c);
            let c = Keyboard.readChar();
        }
        return s;
    }
}
```

### 3.5 `Output`（文本输出）

屏幕 512×256 像素，每个字符 11 行 × 8 列 = 88 像素。
**屏幕可显示 64 列 × 22 行字符**。

```jack
class Output {
    static Array charMaps;   // 字符位图（22 个字符 × 11 行）
    
    function void init() {
        // 初始化所有 ASCII 字符的位图（写死）
        let charMaps = Array.new(127);
        // ... 为每个字符创建 11 字位图
    }
    
    function void printChar(char c) {
        var Array bitmap;
        var int row, col;
        let bitmap = charMaps[c];
        for (let row = 0; row < 11; let row = row + 1) {
            let col = 0;
            while (col < 8) {
                // 检查 bitmap[row] 的第 col 位，置屏幕对应像素
                ...
            }
        }
    }
}
```

### 3.6 `String`（字符串）

字符串是**可变长数组**——用 `Memory.alloc` 分配，支持拼接、转换：

```jack
class String {
    field Array chars;
    field int length, maxLength;
    
    constructor String new(int maxLength) {
        let chars = Array.new(maxLength);
        let length = 0;
        let maxLength = maxLength;
        return this;
    }
    
    method void dispose() {
        do chars.dispose();
        return;
    }
    
    method char charAt(int i) { return chars[i]; }
    
    method void setCharAt(int i, char c) {
        let chars[i] = c;
        return;
    }
    
    method String appendChar(char c) {
        let chars[length] = c;
        let length = length + 1;
        return this;
    }
    
    method int intValue() {
        // 字符串 → 整数
        ...
    }
    
    method void setInt(int n) {
        // 整数 → 字符串
        ...
    }
}
```

### 3.7 `Array`

```jack
class Array {
    function Array new(int size) {
        return Memory.alloc(size);
    }
    method void dispose() {
        do Memory.deAlloc(this);
        return;
    }
}
```

### 3.8 `Sys`

```jack
class Sys {
    function void init() {
        do Memory.init();
        do Math.init();
        do Screen.init();
        do Output.init();
        do Keyboard.init();
        do String.init();
        // 调用用户 main
        do Main.main();
        do Sys.halt();
        return;
    }
    
    function void halt() {
        while (true) {}    // 死循环
        return;
    }
    
    function void wait(int duration) {
        // 用空循环模拟延迟
        var int i;
        for (let i = 0; i < duration; let i = i + 1) {}
        return;
    }
    
    function void error(int errorCode) {
        do Output.printString("ERROR ");
        do Output.printInt(errorCode);
        do Sys.halt();
        return;
    }
}
```

---

## 4. 测试

P12 测试比较特殊——你写的 OS 要**与其他 OS 类协同工作**：

| 测试 | 内容 |
|------|------|
| `MathTest` | multiply / divide / sqrt 边界 |
| `StringTest` | 字符串操作 |
| `MemoryTest` | alloc / deAlloc 不泄漏 |
| `ScreenTest` | drawPixel / drawLine / drawRect / drawCircle |
| `KeyboardTest` | keyPressed / readChar |
| `OutputTest` | printString / printInt |

**测试流程**：在 VMEmulator 里运行测试 + 屏幕键盘模拟器，目视检查图形输出。

---

## 5. 常见坑

### 坑 1：乘除法用 Jack 自己实现，**不能用 `*` 和 `/`**

Jack 编译器遇到 `a * b` 会**调用 `Math.multiply`**——
而你在实现 `Math.multiply`，不能用 `*`！

→ **用位运算实现**（左移 = ×2，右移 = /2，按位与判断最低位）。

### 坑 2：字符串字面量展开为 `String.new().appendChar()...`

Jack 编译器看到 `"hello"` 会**展开为**：
```
push constant 5
call String.new 1
push constant 104   // 'h'
call String.appendChar 1
... 5 次
```

**所以 `String` 类必须先实现**——否则任何包含字符串字面量的程序都无法运行。

### 坑 3：内存泄漏

```jack
let s = "hello";
let s = "world";     // 旧 s 泄漏！
```

必须：
```jack
let s = "hello";
do s.dispose();      // 显式释放
let s = "world";
```

### 坑 4：alloc 的 freeList 实现

`freeList` 是一个链表，每个空闲块的开头存下一个空闲块的地址。
**alloc 必须 first-fit 或 best-fit**，deAlloc 必须 coalesce（合并相邻空闲块）。

### 坑 5：Bresenham 算法必须用整数

Jack 没有浮点。所有图形算法必须用整数实现——这就是 Bresenham 算法（整数 DDA）的存在意义。

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Expert_04_OS_Kernel`](../../Expert_04_OS_Kernel/) 的连接

P12 的 OS 是**单用户、单任务、无虚拟内存、无中断**的极简 OS。
真实 Linux/Windows 内核多了：
- 多任务调度（[`Expert_04`](../../Expert_04_OS_Kernel/) §syscall_bench）
- 虚拟内存 + 页表 + TLB（[`Lab03`](../../Lab03_存储层次/)）
- 中断处理 + 异常
- 文件系统
- 进程间通信（IPC）
- 权限隔离

但**核心思想（OS = 资源管理 + 接口）**与 P12 完全一致。

### 6.2 与 [`Lab06_内存模型与并发`](../../Lab06_内存模型与并发/) 的连接

P12 的 OS 是**单线程**，没有内存模型问题。
真实多核 OS 必须解决：
- 缓存一致性（MESI 协议）
- 内存屏障（[`Lab06`](../../Lab06_内存模型与并发/)）
- 锁、原子操作

### 6.3 与 [`Expert_14_Process_Manufacturing`](../../Expert_14_Process_Manufacturing/) 的连接

P12 的 `Memory.alloc` 算法（first-fit）和**现代 malloc** 相比太简单。
真实 malloc（glibc `ptmalloc` / `jemalloc` / `tcmalloc`）：
- 多线程安全
- size-class 分桶
- slab allocator

但**freeList 思想是所有 malloc 的基础**。

### 6.4 与 [`Expert_20_Green_Compute`](../../Expert_20_Green_Compute/) 的连接

P12 的 `Sys.wait` 是**忙等空循环**——浪费 CPU、浪费电。
现代 OS 用 `HLT` 指令（x86）/ `WFI`（ARM）让 CPU 进入睡眠，省电。
→ 飞腾 D3000M 的 cpuidle 驱动（[`Expert_20`](../../Expert_20_Green_Compute/)）就是干这个的。

---

## 7. 扩展挑战

1. **加多任务**：实现协作式调度器（yield 模式）
2. **加文件系统**：用剩余 RAM 实现简易 FS
3. **加中断**：在 Hack 上加中断控制器（需要修改 P05 的 CPU）
4. **加 TCP/IP 栈**：理论练习（无真实网卡）
5. **加 GUI**：实现按钮、文本框、滚动条等控件

---

## 8. 检查清单

- [ ] 实现 8 个 OS 类
- [ ] 软件乘除法（不能用 `*` 和 `/`）
- [ ] 屏幕字符渲染（含位图字体）
- [ ] 键盘轮询 + 按键缓冲
- [ ] freeList 内存分配
- [ ] 字符串字面量正常工作
- [ ] **能跑 P09 写的俄罗斯方块**（最终验证！）

---

## 📌 下一步

🎉🎉🎉 **完成 P12 后，你已经走完了整个 Nand2Tetris 旅程！**

**从 Nand 到俄罗斯方块**——你拥有的：
- 一台完整的计算机（P01-P05）
- 一套完整的工具链：汇编器 + VM + 编译器（P06-P11）
- 一个完整的操作系统（P12）

**所有这些都是你自己写的，没有任何黑盒**。

### 后续建议

1. **复习总结**：写一份"Nand2Tetris 笔记"，把你学到的每层抽象用自己的话讲一遍
2. **回到本项目 Lab**：用 perf 观测飞腾真机，你会**真切感受到**工业 CPU 比你的 Hack 复杂 100 倍
3. **Capstone**：用 Python 实现 RV32I 5 级流水线（比 Hack 多 1 个数量级复杂度）
4. **挑战**：用 Verilog 把你的 Hack CPU 真正综合到 FPGA（参考 [`Expert_03_HW_Designer`](../../Expert_03_HW_DesignER/)）
5. **教学**：找一个零基础朋友，把你学到的讲给他听（费曼学习法）

> 💡 "如果你不能把它讲给一个 8 岁小孩听，那说明你还没真正理解。" —— Albert Einstein
>
> 学完 Nand2Tetris 后，你应该能向任何人讲清楚"计算机是怎么工作的"——
> 这就是 Shimon Schocken 在 TED 演讲里说的"从此再没有魔法"的境界。
