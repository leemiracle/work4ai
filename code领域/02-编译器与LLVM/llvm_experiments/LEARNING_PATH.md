# LLVM 实验学习路径指南

## 已完成的实验

### 1. 基础编译流程实验 (`run_experiments.sh`)
✓ 生成了LLVM IR文件
✓ 对比了优化前后的代码差异
✓ 查看了从C代码到汇编的完整转换
✓ 理解了调试信息的生成

### 2. 调试和分析实验 (`debug_experiments.sh`)
✓ 使用objdump分析可执行文件
✓ 对比了不同优化级别的编译结果
✓ 观察了SIMD向量化优化
✓ 分析了函数内联效果
✓ 理解了位码文件格式

### 3. 计算机系统层次实验 (`system_levels.c`)
✓ 理解了栈、堆、数据段的内存布局
✓ 学习了x86_64调用约定
✓ 观察了分支预测的性能影响
✓ 研究了数据对齐和内存布局
✓ 理解了volatile关键字的作用

## 学到的核心概念

### LLVM IR层
- **SSA (Static Single Assignment)**: 每个变量只赋值一次
- **基本块**: 代码的基本控制流单位
- **类型系统**: i32, i64, float, double, pointer等
- **内存模型**: alloca, load, store指令

### 优化Pass层
- **常量传播**: 将常量值传播到使用点
- **死代码消除**: 移除不可达或无用的代码
- **函数内联**: 将函数调用展开
- **循环优化**: 循环展开、向量化
- **寄存器分配**: 将SSA值映射到物理寄存器

### 代码生成层
- **指令选择**: 选择目标机器指令
- **寄存器分配**: 处理寄存器溢出
- **指令调度**: 优化指令执行顺序
- **Prolog/Epilog生成**: 处理栈帧

### 系统层
- **内存布局**: 栈、堆、数据段、BSS段
- **调用约定**: 参数传递、返回值、栈帧
- **数据对齐**: 提高内存访问效率
- **分支预测**: 影响流水线效率

## 进一步学习的方向

### 1. 构建完整LLVM工具链
```bash
cd /path/to/llvm-project
mkdir build && cd build
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release \
      -DLLVM_ENABLE_PROJECTS="clang;lld" \
      -DLLVM_TARGETS_TO_BUILD="X86" \
      ..
ninja
```
这将提供：opt, llc, llvm-dis, lli等工具

### 2. 编写自定义Pass
创建一个简单的优化Pass：
```cpp
// MyPass.cpp
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"

struct MyPass : llvm::PassInfoMixin<MyPass> {
  llvm::PreservedAnalyses run(llvm::Function &F,
                              llvm::FunctionAnalysisManager &) {
    for (auto &BB : F) {
      for (auto &I : BB) {
        // 在这里添加优化逻辑
      }
    }
    return llvm::PreservedAnalyses::all();
  }
};

extern "C" llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return {LLVM_PLUGIN_API_VERSION, "MyPass", LLVM_VERSION_STRING,
          [](llvm::PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](llvm::StringRef Name, llvm::FunctionPassManager &FPM,
                   llvm::ArrayRef<llvm::PassBuilder::PipelineElement>) {
                  if (Name == "my-pass") {
                    FPM.addPass(MyPass());
                    return true;
                  }
                  return false;
                });
          }};
}
```

### 3. 研究特定优化算法
- **死代码消除 (DCE)**: 移除死代码
- **常量传播**: 传播常量值
- **公共子表达式消除 (CSE)**: 识别和消除重复计算
- **循环不变代码外提**: 将循环内的不变代码移到循环外
- **归纳变量简化**: 优化循环变量

### 4. 使用分析工具
```bash
# 查看优化管道
opt -passes='print<my-pass>' simple.ll

# 生成控制流图
opt -dot-cfg simple.ll

# 查看寄存器分配结果
opt -passes=print-regalloc simple.ll

# 性能分析
llvm-mca simple.s
```

### 5. 理解LLVM后端
研究目标描述文件：
- `llvm/lib/Target/X86/X86.td`: 指令定义
- `llvm/lib/Target/X86/X86ISelLowering.cpp`: 指令选择
- `llvm/lib/Target/X86/X86RegisterInfo.cpp`: 寄存器信息
- `llvm/lib/Target/X86/X86FrameLowering.cpp`: 栈帧管理

## 推荐学习顺序

### 阶段1: 理解基础 (当前阶段)
- [x] 运行基础实验
- [x] 理解IR语法
- [x] 观察优化效果
- [x] 学习调试技术

### 阶段2: 深入LLVM
- [ ] 构建LLVM工具链
- [ ] 使用opt进行优化分析
- [ ] 学习Pass框架
- [ ] 编写简单Pass

### 阶段3: 代码生成
- [ ] 研究指令选择
- [ ] 学习寄存器分配
- [ ] 理解目标描述
- [ ] 阅读后端代码

### 阶段4: 高级主题
- [ ] JIT编译
- [ ] 自定义目标后端
- [ ] Profile Guided Optimization
- [ ] Link Time Optimization

## 实用调试技巧

### 查看所有优化Pass
```bash
clang -S -emit-llvm -O3 -mllvm -print-after-all simple.c 2>&1 | less
```

### 单独运行特定Pass
```bash
opt -passes=mem2reg,sroa simple.ll -o optimized.ll
```

### 生成可视化CFG
```bash
opt -dot-cfg simple.ll
xdot *.dot
```

### 使用GDB调试Clang
```bash
gdb --args clang -S -emit-llvm simple.c
(gdb) break llvm::FunctionPass::run
(gdb) run
```

### 性能分析
```bash
# 使用perf分析
clang -O3 simple.c -o simple
perf stat -e cycles,instructions,cache-misses ./simple

# 使用valgrind分析内存
valgrind --tool=massif ./simple
```

## 参考文档

- [LLVM Language Reference](https://llvm.org/docs/LangRef.html)
- [Writing an LLVM Pass](https://llvm.org/docs/WritingAnLLVMPass.html)
- [LLVM Programmer's Manual](https://llvm.org/docs/ProgrammersManual.html)
- [Kaleidoscope Tutorial](https://llvm.org/docs/tutorial/)
- [LLVM Passes](https://llvm.org/docs/Passes.html)

## 推荐阅读

- **"LLVM Essentials"**: 快速入门
- **"The LLVM Compiler Infrastructure"**: 全面介绍
- **"Engineering a Compiler"**: 编译器原理
- **"Computer Systems: A Programmer's Perspective"**: 系统基础

## 实践项目建议

1. **简单的字节码解释器**: 使用LLVM IR作为中间表示
2. **专用领域语言**: 为特定领域创建语言
3. **自定义优化Pass**: 实现领域特定的优化
4. **目标后端**: 为简单CPU添加支持
5. **JIT编译器**: 为脚本语言添加即时编译

## 总结

通过这些实验，你已经：

1. 理解了从源码到机器码的完整流程
2. 观察了不同优化级别的效果
3. 学习了LLVM IR的基本语法
4. 理解了计算机系统的底层原理
5. 掌握了调试和分析技术

下一步：构建LLVM工具链，开始编写自定义Pass，深入探索LLVM的更多功能！
