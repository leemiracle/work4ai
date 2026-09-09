# LLVM 实验项目概览

## 项目结构

```
llvm_experiments/
├── README.md                  # 实验说明和学习要点
├── LEARNING_PATH.md           # 完整学习路径指南
│
├── run_experiments.sh         # 基础编译流程实验
├── debug_experiments.sh       # 调试和分析实验
├── system_analysis.sh         # 系统层次分析实验
│
├── simple.c                   # 基础测试程序
├── manual.ll                  # 手写的LLVM IR示例
├── system_levels.c            # 系统层次实验程序
│
└── [生成的文件]              # 各种IR、汇编、可执行文件
```

## 快速开始

### 1. 运行基础实验
```bash
./run_experiments.sh
```
**学习内容**:
- LLVM IR生成和语法
- 优化前后对比
- 汇编代码生成
- 调试信息

### 2. 运行调试实验
```bash
./debug_experiments.sh
```
**学习内容**:
- 符号表分析
- 优化级别对比
- 函数内联
- 位码文件格式

### 3. 运行系统分析实验
```bash
./system_analysis.sh
```
**学习内容**:
- 内存布局（栈、堆、数据段）
- 调用约定
- 分支预测
- 数据对齐

## 关键文件说明

### 源文件
| 文件 | 用途 | 涵盖主题 |
|------|------|----------|
| `simple.c` | 基础测试 | 函数、递归、基本优化 |
| `system_levels.c` | 系统层次 | 内存、调用约定、分支预测、结构体 |

### 脚本文件
| 文件 | 用途 | 主要工具 |
|------|------|----------|
| `run_experiments.sh` | 编译流程 | clang -emit-llvm, clang -S |
| `debug_experiments.sh` | 调试分析 | objdump, file, wc |
| `system_analysis.sh` | 系统分析 | gdb, perf, time |

### 生成的文件
| 文件类型 | 扩展名 | 内容 |
|----------|--------|------|
| LLVM IR | `.ll` | 可读的中间表示 |
| 位码 | `.bc` | 二进制格式的IR |
| 汇编 | `.s` | 目标机器汇编代码 |
| 可执行 | (无) | 链接后的程序 |

## 实验成果

### 理解的概念
- ✅ LLVM IR (SSA形式)
- ✅ 基本块和控制流图
- ✅ 优化Pass (常量传播、死代码消除)
- ✅ 代码生成 (指令选择、寄存器分配)
- ✅ 内存布局 (栈、堆、数据段)
- ✅ 调用约定 (x86_64 ABI)
- ✅ 数据对齐和内存布局
- ✅ 分支预测和性能

### 学会的技能
- ✅ 生成和分析LLVM IR
- ✅ 对比不同优化级别
- ✅ 使用调试工具 (objdump, gdb)
- ✅ 分析汇编代码
- ✅ 理解编译器优化效果

## 扩展学习建议

### 立即可以做的
1. 修改`simple.c`，添加新功能，观察IR变化
2. 使用`-mllvm -print-after-all`查看所有优化
3. 使用`gdb`调试编译过程
4. 对比不同目标架构的生成代码

### 需要构建LLVM后的实验
1. 使用`opt`运行特定Pass
2. 使用`llc`从IR生成汇编
3. 使用`lli`执行IR代码
4. 编写自定义Pass

### 高级项目
1. 实现一个简单的语言前端
2. 为特定领域编写优化Pass
3. 添加自定义目标后端支持
4. 研究JIT编译

## 常用命令参考

### 生成LLVM IR
```bash
clang -S -emit-llvm source.c -o source.ll
clang -S -emit-llvm -O2 source.c -o source_opt.ll
```

### 生成汇编
```bash
clang -S source.c -o source.s
clang -S -O3 source.c -o source_opt.s
```

### 分析可执行文件
```bash
objdump -d executable      # 反汇编
objdump -t executable      # 符号表
objdump -h executable      # section信息
```

### 调试
```bash
gdb ./executable
gdb -x commands.txt ./executable
```

### 性能分析
```bash
time ./executable
perf stat ./executable
valgrind ./executable
```

## 关键观察点

### 1. IR特征
- SSA: 每个变量只赋值一次
- 基本块: 以label开始，以br或ret结束
- Phi节点: 合并来自不同路径的值
- 类型安全: 所有操作都有明确的类型

### 2. 优化效果
- O0: 直接映射，保留所有中间变量
- O2: 启用标准优化，内联、常量传播
- O3: 激进优化，循环展开、向量化
- Os: 代码大小优化

### 3. 系统细节
- 栈帧: 每个函数的局部变量空间
- 调用约定: 参数如何传递，返回值如何返回
- 数据对齐: 提高内存访问效率
- 分支预测: 影响流水线性能

## 故障排除

### 问题: clang命令找不到
```bash
# 检查clang是否安装
which clang

# Ubuntu/Debian安装
sudo apt-get install clang
```

### 问题: 生成IR失败
```bash
# 检查语法错误
clang -fsyntax-only source.c

# 查看详细错误
clang -S -emit-llvm -v source.c
```

### 问题: gdb无法调试
```bash
# 确保用-g编译
clang -g source.c -o executable

# 使用gdb
gdb ./executable
```

## 资源链接

### 官方文档
- [LLVM Website](https://llvm.org/)
- [LLVM Docs](https://llvm.org/docs/)
- [Clang Docs](https://clang.llvm.org/docs/)

### 学习资源
- [Kaleidoscope Tutorial](https://llvm.org/docs/tutorial/)
- [Writing an LLVM Pass](https://llvm.org/docs/WritingAnLLVMPass.html)
- [LLVM Language Reference](https://llvm.org/docs/LangRef.html)

### 社区
- [LLVM Dev List](https://lists.llvm.org/)
- [Discourse](https://discourse.llvm.org/)
- [GitHub](https://github.com/llvm/llvm-project)

## 总结

这套实验提供了：

1. **从入门到深入**的完整路径
2. **理论与实践**相结合的学习方式
3. **多角度**的编译器和系统理解
4. **可扩展**的学习框架

通过这些实验，你将：
- 理解编译器的完整工作流程
- 掌握LLVM IR的基本语法
- 学会分析生成的代码
- 理解计算机系统的底层原理

**下一步**: 阅读`LEARNING_PATH.md`，构建完整LLVM工具链，开始编写自定义Pass！
