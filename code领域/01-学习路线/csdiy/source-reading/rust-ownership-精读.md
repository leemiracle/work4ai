# Rust 所有权精读：编译期内存安全的工程艺术

> Rust 不需要 GC，也不需要手动 free——所有权系统在编译期保证内存安全。
>
> 配套：[patterns §6 单例红线](../notes/patterns-程序员视角-真实代码里的模式.md) + [os §一 OOM](../notes/os-程序员视角-从bug到原理.md)
> csdiy 对应：csapp Ch9(虚拟内存/堆) + os §四(page cache)

---

## 一、问题：C/C++ 的内存安全噩梦

```c
// C 的经典 bug
char *p = malloc(100);
free(p);
*p = 42;        // use-after-free → 未定义行为
char *q = malloc(100);
free(q);
free(q);        // double-free → 堆损坏

// C++ 的悬空引用
int& dangling() {
    int x = 42;
    return x;    // 返回栈变量的引用 → 悬空指针
}
```

**三种解法**：
1. **GC（Java/Go/Python）**：runtime 自动回收 → 暂停/开销
2. **引用计数（Swift/Python C API）**：实时计数 → 循环引用泄漏
3. **Rust 所有权**：**编译期**确定 → 零 runtime 开销

---

## 二、所有权三原则

```rust
// Rust 的三条铁律：
// 1. 每个值有且只有一个所有者
// 2. 当所有者离开作用域，值被销毁
// 3. 赋值/传参 = 所有权转移（move）
```

### 规则 1+2：作用域即生命周期

```rust
{
    let s = String::from("hello");  // s 是所有者
    // ... 使用 s
}   // ← s 离开作用域 → String 的内存自动释放（drop）

// 等价于 C++ 的 RAII（参照 csapp Ch9：栈展开）
```

**对比 C**：你忘了 free → 内存泄漏。Rust 编译器**保证不会忘**。

### 规则 3：Move 语义

```rust
let s1 = String::from("hello");
let s2 = s1;  // ← 所有权从 s1 转移到 s2（move）

// println!("{}", s1);  // ❌ 编译错误！s1 已失效
println!("{}", s2);     // ✅ s2 是新的所有者
```

**为什么**：String 包含堆指针。如果 s1 和 s2 都指向同一块堆内存 → double-free。Rust 的 move 语义让旧引用失效 → **编译期消除 double-free**。

### Clone（显式拷贝）

```rust
let s1 = String::from("hello");
let s2 = s1.clone();  // ← 深拷贝（显式）
// s1 和 s2 各有自己的堆内存
println!("{} {}", s1, s2);  // ✅
```

### Copy（栈类型自动拷贝）

```rust
let x = 42;       // i32 是 Copy 类型（完全在栈上）
let y = x;        // ← 自动拷贝（不是 move）
println!("{}", x); // ✅ x 仍然有效
```

Copy 类型：`i32`, `f64`, `bool`, `char`, `(i32, i32)` 等栈上类型。
非 Copy 类型：`String`, `Vec`, `HashMap` 等包含堆数据的类型。

---

## 三、借用（Borrowing）

如果不想转移所有权，用**引用**：

```rust
fn calculate_len(s: &String) -> usize {  // & = 借用（不获取所有权）
    s.len()
}   // s 是引用，不 drop 原始数据

let s1 = String::from("hello");
let len = calculate_len(&s1);  // 借用 s1
println!("{} has length {}", s1, len);  // ✅ s1 仍有效
```

### 不可变借用 vs 可变借用

```rust
let mut s = String::from("hello");

let r1 = &s;           // 不可变借用
let r2 = &s;           // 多个不可变借用 OK
println!("{} {}", r1, r2);

let r3 = &mut s;       // ❌ 可变借用 + 不可变借用 = 编译错误！
// Rust 规则：要么多个不可变借用，要么一个可变借用
```

**为什么**：
- 多个不可变借用：安全的（只读）
- 一个可变借用：安全的（唯一写者）
- 混用：data race！（不可变借用可能读到半修改的数据）

**这就是 Rust 编译期消除 data race 的核心机制。**

---

## 四、生命周期（Lifetimes）

### 问题：悬空引用

```rust
// 这个函数有 bug
fn dangle() -> &String {
    let s = String::from("hello");
    &s   // ← 返回 s 的引用，但 s 在函数结束时被 drop！
}       // 悬空引用！
```

### Rust 的编译期检查

```rust
// ❌ 编译器拒绝：missing lifetime specifier
fn dangle() -> &String { ... }

// 修复方案 1：返回所有权（不是引用）
fn no_dangle() -> String {
    let s = String::from("hello");
    s   // ← move 出去，不 drop
}

// 修复方案 2：标注生命周期
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
// 'a 表示：返回值的生命周期 = x 和 y 中较短的那个
```

### 生命周期省略规则

Rust 编译器能自动推导 3 种常见情况（不需要显式标注）：
```rust
// 省略的
fn first_word(s: &str) -> &str { ... }
// 编译器理解为：
fn first_word<'a>(s: &'a str) -> &'a str { ... }
```

csdiy 交叉：[patterns §6 单例红线](../notes/patterns-程序员视角-真实代码里的模式.md) — Rust 的所有权系统让全局可变状态更安全，但仍有 `unsafe` 逃生舱。

---

## 五、智能指针（超出引用的范围）

| 类型 | 何时 drop | 用途 |
|------|----------|------|
| `&T` / `&mut T` | 不 drop（借用） | 临时引用 |
| `Box<T>` | 离开作用域 | 堆分配（单一所有者） |
| `Rc<T>` | 最后一个引用 drop | 引用计数（多所有者，不可变） |
| `Arc<T>` | 最后一个引用 drop | 原子引用计数（线程安全） |
| `RefCell<T>` | 离开作用域 | 运行时借用检查（内部可变性） |
| `Mutex<T>` | 离开作用域 | 线程安全可变 |

### Box（堆分配）

```rust
let x = Box::new(42);  // 在堆上分配
println!("{}", x);      // 自动解引用
// x 离开作用域 → 自动 free（不需要手动）
```

### Rc（引用计数）

```rust
use std::rc::Rc;

let a = Rc::new(String::from("hello"));  // count=1
let b = Rc::clone(&a);                   // count=2
let c = Rc::clone(&a);                   // count=3

// 三个变量共享同一块内存
// 最后一个离开作用域时才 free
```

**注意**：Rc 不是线程安全的（参照 os §五 并发）。多线程用 `Arc`（Atomic Rc）。

### RefCell（运行时借用检查）

```rust
use std::cell::RefCell;

let data = RefCell::new(vec![1, 2, 3]);

{
    let mut borrow = data.borrow_mut();  // 运行时检查：没有其他借用
    borrow.push(4);
}   // borrow 离开作用域 → 释放借用

let read = data.borrow();  // ✅ 之前的可变借用已结束
println!("{:?}", *read);
```

**对比编译期借用检查**：RefCell 把检查推迟到运行时（panic on violation）。用于"编译器无法证明安全但实际安全"的场景。

---

## 六、Rust vs C vs Go 的内存管理对比

| 维度 | C/C++ | Go | Rust |
|------|-------|-----|------|
| 机制 | 手动 malloc/free | GC | 所有权+借用 |
| 安全性 | ❌ 容易 UAF/double-free | ✅ GC 保证 | ✅ 编译期保证 |
| 开销 | 零 | GC 暂停(1-10ms) | 零 runtime |
| 控制 | 完全手动 | 黑盒 | 编译器辅助 |
| 学习曲线 | 高（踩坑多） | 低 | **高**（与借用检查器搏斗） |

---

## 七、和 csdiy 的交叉

### csapp Ch9（虚拟内存）

Rust 的 `Box::new(42)` 等价于 C 的 `malloc(sizeof(int))`，但 **drop 时自动 free**。

```rust
// Rust
{
    let x = Box::new(42);
}   // ← 自动 free

// C
{
    int *x = malloc(sizeof(int));
    *x = 42;
    free(x);  // ← 必须手动 free！忘了 = 内存泄漏
}
```

### os §一（OOM）

Rust 的所有权系统 **减少了** 内存泄漏（但不完全消除——循环引用的 Rc 仍会泄漏）。

### os §五（并发）

Rust 的 `Send`/`Sync` trait 在编译期消除 data race：
```rust
// Send：类型可以安全地跨线程转移所有权
// Sync：类型可以安全地被多线程共享引用

use std::thread;
let data = vec![1, 2, 3];
thread::spawn(move || {     // move 转移所有权到新线程
    println!("{:?}", data);
});
// 编译器保证：不会有两个线程同时写 data
```

---

## 八、一句话总结

> Rust 的所有权系统 = 编译期 GC。三条铁律（唯一所有者/离开作用域 drop/move 语义）消除了 use-after-free/double-free/data race 三大 bug。
>
> 代价：学习曲线陡峭（与借用检查器搏斗）。收益：零 runtime 开销的内存安全。

---

*配套：[csapp-程序员视角 Ch9](../notes/csapp-程序员视角.md) | [os §一 §五](../notes/os-程序员视角-从bug到原理.md)*
