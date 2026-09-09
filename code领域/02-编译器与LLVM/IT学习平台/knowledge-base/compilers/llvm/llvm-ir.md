# LLVM IR

## 基本信息
- **分类**: 编译器 -> 中间表示
- **语言**: SSA (Static Single Assignment)
- **扩展**: .ll / .bc

## 核心概念
LLVM IR 是编译器基础设施的核心，连接前端和后端，支持跨语言优化。

## IR 结构层级
```
Module (模块)
  └── Function (函数)
        └── Basic Block (基本块)
              └── Instruction (指令)
```

## 基本指令

### 算术运算
```llvm
; 整数加法
%result = add i32 %a, %b

; 浮点数乘法
%result = fmul double %x, %y

; 有符号除法
%result = sdiv i32 %a, %b
```

### 内存操作
```llvm
; 分配栈内存
%ptr = alloca i32

; 存储到内存
store i32 42, i32* %ptr

; 从内存加载
%value = load i32, i32* %ptr

; GEP (GetElementPtr) 指针运算
%array_ptr = getelementptr [10 x i32], [10 x i32]* %arr, i64 0, i64 %index
```

### 控制流
```llvm
; 无条件跳转
br label %next_block

; 条件跳转
%cond = icmp slt i32 %a, %b
br i1 %cond, label %then_block, label %else_block

; 函数调用
call void @print(i32 %value)

; 返回
ret i32 %result
```

## 完整示例

### C 源代码
```c
int sum(int n) {
    int total = 0;
    for (int i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}
```

### LLVM IR
```llvm
define i32 @sum(i32 %n) {
entry:
  %total = alloca i32
  %i = alloca i32
  store i32 0, i32* %total
  store i32 1, i32* %i
  br label %for.cond

for.cond:
  %i_val = load i32, i32* %i
  %cmp = icmp sle i32 %i_val, %n
  br i1 %cmp, label %for.body, label %for.end

for.body:
  %total_val = load i32, i32* %total
  %add = add i32 %total_val, %i_val
  store i32 %add, i32* %total
  %i_next = add i32 %i_val, 1
  store i32 %i_next, i32* %i
  br label %for.cond

for.end:
  %result = load i32, i32* %total
  ret i32 %result
}
```

## SSA 形式

### PHI 节点
```llvm
; 变量定义前使用 PHI 节点合并值
define i32 @test(i1 %cond) {
entry:
  br i1 %cond, label %then, label %else

then:
  %x1 = add i32 1, 2
  br label %merge

else:
  %x2 = mul i32 3, 4
  br label %merge

merge:
  %x = phi i32 [ %x1, %then ], [ %x2, %else ]
  ret i32 %x
}
```

## 类型系统
```llvm
; 基本类型
i1, i8, i16, i32, i64      ; 整数
float, double              ; 浮点数
void                       ; 无返回值

; 派生类型
i32*                       ; 指针
[10 x i32]                ; 固定数组
{i32, i8*}                ; 结构体
<4 x i32>                 ; 向量 (SIMD)
```

## 内置函数
```llvm
; 内存操作
call void @llvm.memcpy.p0i8.p0i8.i64(i8* %dest, i8* %src, i64 %size, i1 %false)

; 数学运算
%result = call double @llvm.pow.f64(double %base, double %exp)

; 位操作
%count = call i32 @llvm.cttz.i32(i32 %value)
```

## 优化 Pass

### 常量传播
```llvm
; 优化前
%a = add i32 10, 20
%b = mul i32 %a, 2

; 优化后
%b = mul i32 30, 2
```

### 死代码消除
```llvm
; 优化前
%unused = add i32 1, 2
%used = add i32 3, 4

; 优化后
%used = add i32 3, 4
```

### 内联
```llvm
; 优化前
%result = call i32 @small_func(i32 %x)

; 优化后 (直接插入函数体)
%result = add i32 %x, 10
```

## 实用工具

### 生成 IR
```bash
clang -S -emit-llvm input.c -o output.ll
clang -S -emit-llvm -O2 input.c -o optimized.ll
```

### 优化 IR
```bash
opt -S -O2 input.ll -o optimized.ll
opt -passes='instcombine' input.ll -S
opt -passes='mem2reg' input.ll -S  ; 寄存器分配
```

### 分析 IR
```bash
opt -passes='print<scalar-evolution>' -S input.ll
opt -passes='print<domtree>' -S input.ll
```

### 转换为汇编
```bash
llc -O2 input.ll -o output.s
llc -filetype=obj input.ll -o output.o
```

## 调试技巧
```llvm
; 打印调试信息
call void @llvm.dbg.value(metadata i32 %x, metadata !1, metadata !DIExpression())

; 断点
call void @llvm.debugtrap()

; 断言
call void @llvm.assume(i1 %condition)
```

## 应用场景
- 跨语言编译（C/C++/Rust/Swift）
- JIT 编译
- 程序分析
- 自定义语言开发

## 相关概念
- [[Clang AST]]
- [[代码生成]]
- [[MLIR]]

## 参考资源
- LLVM LangRef: https://llvm.org/docs/LangRef.html
- LLVM Cookbook: https://www.packtpub.com/product/llvm-cookbook/9781785286982
- 《LLVM权威指南》

## 实践项目
- 编写简单的 LLVM Pass
- 实现 LLVM IR 优化器
- 开发基于 LLVM 的解释器
```