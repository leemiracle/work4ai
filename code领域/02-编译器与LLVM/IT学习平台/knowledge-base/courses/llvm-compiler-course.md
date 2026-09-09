# LLVM编译器技术课程

## 课程概述

本课程全面介绍LLVM编译器基础设施，从基础概念到高级优化技术，帮助学员深入理解现代编译器原理和实践。

## 课程信息

- **课程名称**: LLVM编译器技术
- **难度**: Advanced
- **预计学时**: 40小时
- **模块数量**: 8

## 学习目标

完成本课程后，您将能够：

1. 理解LLVM的核心架构和设计理念
2. 掌握LLVM IR（中间表示）的基本概念
3. 编写LLVM Pass进行代码分析和优化
4. 使用Clang工具链进行编译器前端开发
5. 理解LLVM的后端代码生成机制

## 前置知识

- C/C++编程经验
- 计算机组成原理基础
- 编译原理基础知识
- 命令行使用经验

## 课程大纲

### 模块1: LLVM简介 (4小时)

**内容**:
- LLVM历史和发展
- LLVM生态系统概览
- 安装和配置LLVM工具链
- 第一个LLVM程序

**实践**:
- 安装LLVM
- 编译第一个程序
- 查看LLVM IR

---

### 模块2: LLVM IR基础 (8小时)

**内容**:
- SSA（Static Single Assignment）形式
- LLVM IR类型系统
- 基本指令集
- 控制流图
- 函数调用约定

**实践**:
- 手写简单的LLVM IR
- 使用opt工具分析IR
- 对比不同优化级别的IR

**知识点**:
- % - 寄存器命名
- 基本块（Basic Block）
- phi节点
- 类型转换指令

---

### 模块3: Clang工具链 (6小时)

**内容**:
- Clang架构
- AST（抽象语法树）
- Clang工具开发
- 代码分析工具

**实践**:
- 使用Clang AST导出
- 编写简单的Clang工具
- 使用Clang-format和Clang-tidy

---

### 模块4: 编写LLVM Pass (10小时)

**内容**:
- Pass管理器
- FunctionPass, ModulePass
- Pass注册和运行
- 常用Pass示例
- Pass编写最佳实践

**实践**:
- 编写FunctionPass统计指令数
- 编写ModulePass查找全局变量
- 实现简单的优化Pass
- 使用PassManager运行自定义Pass

**代码示例**:
```cpp
// 简单的FunctionPass示例
struct HelloPass : public FunctionPass {
  static char ID;
  HelloPass() : FunctionPass(ID) {}

  bool runOnFunction(Function &F) override {
    errs() << "Function: " << F.getName() << "\n";
    return false;
  }
};
```

---

### 模块5: 常见优化Pass (6小时)

**内容**:
- Mem2Reg Pass
- Dead Code Elimination
- Loop Optimization
- Inlining
- Interprocedural Analysis

**实践**:
- 观察优化前后的IR差异
- 使用opt运行标准Pass
- 分析Pass依赖关系

---

### 模块6: 后端代码生成 (4小时)

**内容**:
- LLVM后端架构
- 目标描述（Target Description）
- 指令选择
- 寄存器分配
- 代码发射

**实践**:
- 查看目标机器信息
- 使用llc生成汇编代码
- 分析生成代码的质量

---

### 模块7: JIT编译 (2小时)

**内容**:
- MCJIT（Modular Compile-Time JIT）
- ORC JIT
- JIT的应用场景
- JIT性能考虑

**实践**:
- 编写简单的JIT程序
- 动态编译和执行代码

---

### 模块8: 高级主题 (0小时)

**内容**:
- TableGen配置语言
- 调试技术
- 性能分析
- 贡献LLVM项目

**资源**:
- LLVM官方文档
- LLVM DevM会议视频
- 开源项目案例

---

## 学习资源

### 官方文档
- [LLVM Language Reference](https://llvm.org/docs/LangRef.html)
- [LLVM Programmer's Manual](https://llvm.org/docs/ProgrammersManual.html)
- [Writing an LLVM Pass](https://llvm.org/docs/WritingAnLLVMPass.html)

### 推荐书籍
- 《LLVM Cookbook》
- 《The LLVM Compiler Infrastructure》

### 在线资源
- [LLVM Weekly](https://llvmweekly.org/)
- [LLVM Discourse](https://discourse.llvm.org/)

## 实践项目

### 项目1: 优化Pass实现

**目标**: 实现一个简单的优化Pass

**要求**:
- 选择一个简单的优化目标
- 编写FunctionPass
- 测试Pass的正确性
- 评估优化效果

### 项目2: Clang工具开发

**目标**: 开发一个代码分析工具

**要求**:
- 使用Clang AST
- 实现代码检查功能
- 输出分析报告

### 项目3: 自定义后端

**目标**: 为虚拟CPU添加LLVM后端

**要求**:
- 定义目标指令集
- 实现指令选择
- 测试代码生成

## 评估方式

- 模块测验: 30%
- 实践项目: 50%
- 最终项目: 20%

## 常见问题

### Q: LLVM和GCC有什么区别？

A: LLVM采用模块化设计，更容易扩展和定制。GCC使用单一后端，LLVM支持多种后端。

### Q: 如何调试LLVM Pass？

A: 使用`-debug`选项，添加`errs()`输出，使用gdb调试器。

### Q: 学习LLVM需要多久？

A: 基础概念2-3周，编写Pass需要1-2个月实践。

## 进阶学习路径

完成本课程后，可以继续学习：

1. 编译器高级优化技术
2. 静态分析工具开发
3. 动态分析和instrumentation
4. 新语言前端开发

---

**创建日期**: 2026-02-13
**最后更新**: 2026-02-13
**课程维护**: LLVM社区
