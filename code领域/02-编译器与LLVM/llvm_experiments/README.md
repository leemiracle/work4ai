# LLVM 实验项目

通过这些实验深入理解LLVM编译器和计算机系统原理。

## 实验目录

### 1. 基础实验 (run_experiments.sh)
展示从源代码到机器码的完整编译流程：

- **实验1**: 生成LLVM IR - 理解中间表示
- **实验2**: 优化前后对比 - 观察编译器优化效果
- **实验3**: 生成汇编代码 - 理解机器码生成
- **实验4**: 编译并运行 - 完整的编译流程
- **实验5**: 调试信息生成 - 理解调试信息如何存储
- **实验6**: IR差异分析 - 对比不同优化级别

### 2. 调试实验 (debug_experiments.sh)
深入分析生成的代码：

- **实验1**: 符号表分析 - 理解函数和变量的存储
- **实验2**: 优化级别影响 - 对比O0/O1/O2/O3/Os
- **实验3**: 高级优化分析 - 查看SIMD、循环展开等
- **实验5**: 汇编代码差异 - 理解优化对机器码的影响
- **实验6**: 函数内联 - 观察内联优化
- **实验7**: 位码文件 - 理解LLVM的序列化格式

## 学习要点

### 1. LLVM IR (Intermediate Representation)
- SSA (Static Single Assignment) 形式
- 类型系统: i32, i64, float, double, pointer
- 基本块: 控制流图的基本单位
- Phi节点: 处理控制流汇聚

### 2. 优化Pass
- 常量传播
- 死代码消除
- 函数内联
- 循环优化
- SIMD向量化

### 3. 代码生成
- 指令选择
- 寄存器分配
- 指令调度
- 寄存器溢出

### 4. 调试信息
- DWARF格式
- 源代码到机器码的映射
- 符号表

## 扩展实验建议

### 高级主题
1. **编写自定义LLVM Pass**: 学习如何添加自己的优化
2. **JIT编译**: 使用LLVM的JIT引擎
3. **交叉编译**: 为不同目标平台生成代码
4. **分析工具**: 使用llvm-mca分析代码性能
5. **Profile Guided Optimization (PGO)**: 使用运行时信息优化

### 调试技巧
```bash
# 查看完整的优化管道
clang -S -emit-llvm -O3 -mllvm -print-after-all simple.c

# 使用gdb调试clang
gdb --args clang -S -emit-llvm simple.c

# 查看IR的dot图
opt -dot-cfg simple.ll
```

## 参考资源

- [LLVM Language Reference](https://llvm.org/docs/LangRef.html)
- [Writing an LLVM Pass](https://llvm.org/docs/WritingAnLLVMPass.html)
- [LLVM Optimization Passes](https://llvm.org/docs/Passes.html)
- [Kaleidoscope Tutorial](https://llvm.org/docs/tutorial/)

## 下一步

1. 构建完整的LLVM工具链以使用opt、llc等工具
2. 实现一个简单的自定义Pass
3. 研究特定优化算法的实现
4. 探索LLVM后端的目标描述
