# tinysymtab · 符号表

> 作用域栈 + 符号解析，编译器核心数据结构。参照 **LLVM SymbolTable / ELF .symtab**。

## 概述

`tinysymtab` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **符号表** 的核心机制。

## 核心概念

- Symbol(name/type/scope/kind)
- Scope 嵌套（enter/exit）
- 符号解析 = 沿作用域栈向上找
- 用于类型检查 + 代码生成

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 59 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinysymtab
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinysymtab` | LLVM SymbolTable / ELF .symtab |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
