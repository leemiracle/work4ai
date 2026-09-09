# Project 09 — High-Level Language：用 Jack 写一个交互式 App

> **一句话目标**：用 Jack 语言（Nand2Tetris 的高级语言）写一个完整的交互式 App——
> 俄罗斯方块、贪吃蛇、Pong、2048、计算器……你自己选。
>
> **这是 P10-P12 的前置**：你写的 App 将成为 P11 编译器测试的目标程序。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch9**（High-Level Language）|
| 🎥 Coursera | [Unit 9.1-9.8](https://www.coursera.org/learn/nand2tetris2) |
| 🛠 工具 | **JackCompiler** + **VMEmulator** |
| ⏱ 预计工时 | 15–40 小时（取决于 App 复杂度）|

---

## 1. Jack 语言速览

Jack 是教学用的 OO 语言，类似简化版 Java。

### 1.1 基本结构

```jack
// Hello.jack
class Hello {
    field int x;             // 实例字段
    static int count;        // 静态字段
    
    constructor Hello new() {
        let x = 0;
        let count = count + 1;
        return this;
    }
    
    method int getX() {
        return x;
    }
    
    function void main() {
        var Hello h;
        let h = Hello.new();
        do Output.printString("x = ");
        do Output.printInt(h.getX());
        do Output.println();
        return;
    }
}
```

### 1.2 类型系统

| 类型 | 说明 |
|------|------|
| `int` | 16 位有符号整数（与 Hack 字长一致）|
| `boolean` | true(-1) / false(0) |
| `char` | 字符（Unicode 字符） |
| `void` | 无返回值 |
| `ClassName` | 对象引用 |

### 1.3 语句

| 语句 | 例子 |
|------|------|
| `let` | `let x = 5;` |
| `if` | `if (x > 0) { ... } else { ... }` |
| `while` | `while (x > 0) { let x = x - 1; }` |
| `do` | `do Output.println();`（调用 void 方法）|
| `return` | `return x;` 或 `return;` |
| 数组 | `let arr[i] = 5; let y = arr[0];` |

### 1.4 表达式

```
+, -, *, /, &, |, ~        // 算术/位
<, >, =, <=, >=, ~=        // 比较
true, false, null, this    // 字面量
arr[expr], foo.bar(args)   // 数组访问、方法调用
```

### 1.5 Jack 标准库（P12 你要实现的）

| 类 | 功能 |
|----|------|
| `Math` | 数学（除法、开方、绝对值）|
| `String` | 字符串 |
| `Array` | 数组 |
| `Output` | 屏幕输出 |
| `Screen` | 图形绘制 |
| `Keyboard` | 键盘输入 |
| `Memory` | 内存操作 |
| `Sys` | 系统（halt, wait, error）|

---

## 2. 选什么 App？

### 2.1 难度分级

| 等级 | App | 估计工时 |
|------|-----|---------|
| ⭐ | 计算器 | 10 小时 |
| ⭐⭐ | Pong（弹球）| 15–20 小时 |
| ⭐⭐ | 贪吃蛇 | 20–25 小时 |
| ⭐⭐⭐ | 2048 | 25–30 小时 |
| ⭐⭐⭐ | 俄罗斯方块（Tetris）| 30–40 小时 |
| ⭐⭐⭐⭐ | 简易 Paint | 35 小时+ |

**官方推荐**：俄罗斯方块（这是 "Tetris" 的来源，nand2tetris.org 的名字）。

### 2.2 Pong 的最简实现思路

```jack
class PongGame {
    field int ballX, ballY;       // 球位置
    field int ballDx, ballDy;     // 球速度
    field int batX;               // 球拍位置
    field int score;
    
    constructor PongGame new() {
        let ballX = 250; let ballY = 200;
        let ballDx = 5; let ballDy = 3;
        let batX = 250;
        let score = 0;
        return this;
    }
    
    method void step() {
        // 清旧位置
        do Screen.drawCircle(ballX, ballY, 3, false);
        // 移动
        let ballX = ballX + ballDx;
        let ballY = ballY + ballDy;
        // 碰撞检测
        if (ballX < 0 | ballX > 511) { let ballDx = -ballDx; }
        if (ballY < 0 | ballY > 200) { let ballDy = -ballDy; }
        // 画新位置
        do Screen.drawCircle(ballX, ballY, 3, true);
        // 球拍
        do drawBat();
        return;
    }
    
    method void moveBat(int dir) {
        let batX = batX + dir;
        return;
    }
}
```

### 2.3 主循环

```jack
class Main {
    function void main() {
        var PongGame game;
        var char key;
        
        let game = PongGame.new();
        
        while (true) {
            // 处理输入
            let key = Keyboard.keyPressed();
            if (key = 130) { do game.moveBat(-5); }   // 左
            if (key = 132) { do game.moveBat(5);  }   // 右
            if (key = 140) { return; }                 // Esc 退出
            
            // 更新游戏
            do game.step();
            
            // 控制帧率
            do Sys.wait(30);   // ~33 FPS
        }
    }
}
```

---

## 3. 项目结构

```
Project_09_HighLevelLanguage/
└── jack/
    └── Pong/                    ← 你的 App 目录
        ├── Main.jack
        ├── PongGame.jack
        ├── Bat.jack
        └── Ball.jack
```

每个 `.jack` 文件是一个类。文件名必须与类名一致。

---

## 4. 测试

### 4.1 用官方 JackCompiler

```bash
# 编译整个目录
JackCompiler.sh jack/Pong/

# 输出：jack/Pong/Main.vm, PongGame.vm, Bat.vm, Ball.vm
```

### 4.2 在 VMEmulator 里跑

```bash
VMEmulator.sh
# 1. Load Program: jack/Pong/  （注意：整个目录）
# 2. Animate → No animation（加速）
# 3. Run
```

---

## 5. 常见坑

### 坑 1：Jack 没有浮点

所有运算都是 `int`（16 位）。`1/2 = 0`。需要浮点时用定点（如 ×1024 表示 10.24）。

### 坑 2：数组必须用 `Array.new(length)`

```jack
var Array arr;
let arr = Array.new(100);   // 长度 100
```

不能像 C 一样 `int arr[100]`。

### 坑 3：Jack 的 `=` 是比较，不是赋值

```jack
if (x = 0) { ... }    // 等同 C 的 (x == 0)
let x = 0;            // 赋值也用 =，但前面有 let
```

→ **赋值必须有 `let`**。

### 坑 4：do 用于 void 方法调用

```jack
do Output.println();     // ✅ void 调用
let x = foo.bar();       // ✅ 非 void 用 let
foo.bar();               // ❌ 没有 do 也没有 let
```

### 坑 5：字符串是对象

```jack
var String s;
let s = "hello";         // 实际是 String.new(5).appendChar(...)
let s = "hello" + 1;     // ❌ 不能这么写
```

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Lab06_内存模型与并发`](../../Lab06_内存模型与并发/) 的连接

Jack 是**单线程**语言，没有并发问题。
工业语言（Java、Go、Rust）的并发模型在 P09 不涉及——这是后续学习内容。

### 6.2 与 [`Expert_22_OpenSource_Ecosystem`](../../Expert_22_OpenSource_Ecosystem/) 的连接

Jack 是教学语言，**没有真实生态**。学完 Jack 后看 Java / Kotlin / Swift 的标准库，
你会发现 Jack 的 `Math/String/Array` 都是这些工业标准库的极简版本。

### 6.3 与 [`背景知识/Great_Ideas`](../../背景知识/Great_Ideas_体系结构思想.md) 的连接

- **Great Idea #1：Abstraction（抽象）** ← OO 的精髓
- **Great Idea #8：Interface（接口）** ← 方法签名就是契约

---

## 7. 扩展挑战

1. **加 GUI 编辑器**：用 Jack 自己写一个文本编辑器
2. **加网络协议栈**：用 Jack 实现 TCP（理论练习，没真实网卡）
3. **加文件系统**：用剩余的 RAM 实现文件存储
4. **加多线程**：用 VM 的 yield 模式实现协程
5. **AI**：写一个简单的下棋 AI（4 子棋）

---

## 8. 检查清单

- [ ] 选定一个 App（推荐 Pong 起步）
- [ ] 实现 3+ 个类（如 Main + Game + Bat + Ball）
- [ ] 实现键盘输入响应
- [ ] 实现屏幕渲染
- [ ] 用官方 JackCompiler 编译通过
- [ ] 在 VMEmulator 里能玩

---

## 📌 下一步

完成 P09 后，进 [`Project_10_Compiler_I/`](../Project_10_Compiler_I/)。
你将**自己实现 Jack 编译器的前端**（Tokenizer + Parser）——
让 P09 写的 Jack 程序能被你自己的编译器处理。
