# DeepWiki 分析 Bolt 最佳提示词

## 分析流程概述

DeepWiki通过以下核心步骤分析BOLT二进制：

1. **热力图生成** - 识别代码热点
2. **二进制安全分析** - pac-ret安全扫描
3. **控制流图重构** - CFG分析
4. **地址转换分析** - BAT section分析
5. **优化效果对比** - 前后性能对比

---

## 步骤1：生成性能热力图

### 最佳提示词

```
你是一个专业的编译器性能分析专家。你的任务是分析BOLT（Binary Optimization and Layout Tool）优化前后的代码性能热点。

### 分析目标
1. 使用perf工具收集采样数据
2. 使用llvm-bolt-heatmap生成可视化热力图
3. 识别性能瓶颈和热点函数
4. 对比优化前后的性能差异

### 输入信息
- 二进制文件路径: {binary_path}
- 优化类型: {optimization_type} (BOLT / 非BOLT)
- 采样时长: {duration}
- 热力图选项: {heatmap_options}

### 分析要求
1. 生成热力图的命令
2. 解释热力图的含义
3. 识别top 10热点函数
4. 分析性能数据（cycles, instructions, cache misses）
5. 提供优化建议

### 输出格式
```json
{
  "commands": [...],
  "hotspots": [
    {
      "function": "函数名",
      "address": "地址",
      "cycles": "CPU周期数",
      "instructions": "指令数",
      "percentage": "占比"
    }
  ],
  "analysis": "性能分析总结",
  "recommendations": ["优化建议1", "优化建议2"]
}
```

### 示例提示词

```
请帮我分析这个BOLT优化后的二进制文件的性能热点。

二进制文件: /path/to/bolted/binary
优化类型: BOLT
采样时长: 30秒
热力图选项: --line-size 128 --max-address 4GB

请提供：
1. 生成热力图的完整perf命令
2. 转换为热力图的llvm-bolt-heatmap命令
3. 分析热力图中的top 10热点函数
4. 解释这些热点函数为什么慢（cache miss、branch misprediction、内存访问等）
5. 提供针对性的优化建议
```

---

## 步骤2：pac-ret安全分析

### 最佳提示词

```
你是一个专业的二进制安全分析专家，专注于pac-ret（Position-Independent Code）攻击检测。

### 分析目标
1. 识别二进制中潜在的pac-ret gadget
2. 检查ROP（Return-Oriented Programming）攻击面
3. 验证地址加载的安全性
4. 分析控制流图的合法性

### 输入信息
- 二进制文件路径: {binary_path}
- 工具链: {toolchain} (GCC/Clang)
- 优化级别: {optimization_level}
- 分析范围: {analysis_scope}

### 安全属性检查
对于每个函数，检查以下属性：
1. 返回地址安全性
   - 地址是否经过认证（PAC）
   - 是否来自只读段
   - 是否包含指针认证代码（PAC）
2. 堆栈操作
   - 是否有明显的栈喷射模式
   - 返回地址是否指向可写内存
3. 寄存器操作
   - 是否正确保存和恢复callee-save寄存器
   - 是否有不可预测的控制流

### 输出格式
```json
{
  "scan_results": [
    {
      "function": "函数名",
      "address": "地址",
      "vulnerabilities": ["vuln_type1", "vuln_type2"],
      "risk_level": "high/medium/low",
      "details": "详细说明"
    }
  ],
  "summary": {
    "total_functions": 100,
    "vulnerable_functions": 5,
    "safe_functions": 95,
    "risk_assessment": "整体风险评估"
  }
}
```

### 示例提示词

```
请对这个BOLT优化后的二进制文件进行pac-ret安全分析。

二进制文件: /path/to/binary
优化级别: -O3
工具链: GCC 9.0

请执行以下分析：

1. 使用llvm-bolt-binary-analysis工具进行pac-ret扫描：
   $ llvm-bolt-binary-analysis --scanners=pac-ret /path/to/binary

2. 对于每个报告的漏洞，分析：
   - 漏洞类型（非认证ret、数据泄露、堆栈喷射等）
   - 涉及的函数和地址
   - 漏洞的严重程度（高/中/低）
   - 是否存在攻击利用路径

3. 提供修复建议：
   - 如何消除pac-ret gadget
   - 建议的编译器选项
   - 代码级别的修复方法

4. 生成安全评估报告
```

---

## 步骤3：控制流图(CFG)分析

### 最佳提示词

```
你是一个专业的编译器专家，擅长分析二进制的控制流图(CFG)。

### 分析目标
1. 重建函数的CFG
2. 识别基本块(Basic Block)
3. 分析分支和循环结构
4. 检测异常的控制流模式

### CFG分析要点

#### 基本块识别
- 每个基本块以分支/跳转指令结束
- 基本块内部是线性执行的指令序列
- 基本块之间的边表示控制流

#### 控制流结构
- 条件分支
- 循环（for, while, do-while）
- 函数调用
- 异常处理

#### 异常模式检测
- 不可达代码
- 间接跳转
- 尾递归
- 异常的CFG结构

### 输出格式
```json
{
  "functions": [
    {
      "name": "函数名",
      "address": "起始地址",
      "basic_blocks": [
        {
          "id": "BB_0",
          "address": "地址",
          "size": "大小(字节)",
          "instructions": ["指令1", "指令2"],
          "successors": ["BB_1", "BB_2"],
          "predecessors": ["BB_-1"]
        }
      ],
      "loops": [...],
      "complexity": {
        "cyclomatic_complexity": 5,
        "num_basic_blocks": 10,
        "edges": 15
      }
    }
  ],
  "anomalies": ["异常模式1", "异常模式2"]
}
```

### 示例提示词

```
请分析这个BOLT优化后二进制文件的main函数的控制流图。

二进制文件: /path/to/binary
函数名: main

请提供：

1. CFG重建：
   - 识别所有基本块
   - 绘制CFG的边
   - 标注循环结构

2. 复杂度分析：
   - 圈复杂度(Cyclomatic Complexity)
   - 基本块数量
   - 分支数量

3. 控制流分析：
   - 分支是否容易预测
   - 是否有复杂的嵌套结构
   - 循环是否会提前退出

4. BOLT优化影响：
   - BOLT是否添加了跳转表
   - 是否存在间接跳转
   - 对CFG重建的影响

5. 生成CFG的可视化表示（文本或Graphviz）
```

---

## 步骤4：BAT（地址转换）分析

### 最佳提示词

```
你是一个专业的编译器专家，精通BOLT的BAT（BOLT Address Translation）section分析。

### 分析目标
1. 解析BAT section的格式和内容
2. 理解地址转换机制
3. 分析翻译表的效率
4. 评估delta编码的压缩效果

### BAT Section组成

#### Hot/Cold Functions Tables
- 函数名和地址
- 输入地址范围
- 输出地址范围

#### Address Translation Tables
- 翻译表条目数量
- 基于delta编码的优化
- 地址对齐策略

#### Secondary Entry Points
- 二级入口点
- 用于函数内跳转

### 分析要点

#### Delta编码分析
- delta值的大小范围
- 连续性（连续地址的delta更小）
- 编码效率（节省了多少字节）

#### 函数碎片化
- 热函数的分割策略
- 片段对齐的影响
- 跳转频率

### 输出格式
```json
{
  "bat_section": {
      "hot_functions_count": 50,
      "cold_functions_count": 30,
      "total_functions": 80
  },
  "translation_efficiency": {
      "delta_encoding_ratio": "0.35",
      "compression_ratio": "0.28",
      "space_saved": "1234 bytes"
  },
  "fragmentation": {
      "average_fragments_per_function": 2.3,
      "max_fragments": 5,
      "indirect_jump_frequency": "low/medium/high"
  }
}
```

### 示例提示词

```
请分析这个BOLT优化后二进制文件的BAT section。

二进制文件: /path/to/binary
包含BAT section: 是
perf2bolt可用: 是

请提供：

1. BAT section解析：
   - 热函数表的内容
   - 冷函数表的内容
   - 地址翻译表的详细信息

2. delta编码分析：
   - delta值的统计信息（最小、最大、平均）
   - 连续地址的比例
   - 编码效率评估

3. 函数碎片化分析：
   - 函数被分割成多少片段
   - 片段大小分布
   - 对性能的影响（跳转开销）

4. 效果评估：
   - 相比非BOLT版本节省了多少空间
   - delta编码的压缩比
   - 对I-Cache的影响

5. 使用perf2bolt工具进行验证：
   - 生成对比报告
   - 识别潜在问题
```

---

## 步骤5：优化效果对比分析

### 最佳提示词

```
你是一个专业的性能分析专家，擅长对比优化前后的性能差异。

### 对比维度

#### 执行性能
- 运行时间
- CPU周期数
- 指令执行数
- 缓存命中率
- 分支预测准确率

#### 代码大小
- 代码段大小
- 函数大小分布
- 整体二进制大小
- 符号表大小

#### 二进制特性
- 代码段数量
- 重定位数量
- 跳转指令数量
- 间接跳转数量

### 输出格式

```json
{
  "performance_comparison": {
      "runtime_speedup": "1.15x",
      "cycle_reduction": "12%",
      "instruction_reduction": "8%",
      "cache_hit_rate": {
          "bolted": "95%",
          "unbolted": "87%"
      }
  },
  "code_size": {
      "before": "1024000 bytes",
      "after": "980000 bytes",
      "reduction": "4.3%"
  },
  "binary_characteristics": {
      "relocations": {
          "before": 1500,
          "after": "1200,
          "change": "-20%"
      },
      "jumps": {
          "indirect_before": 50,
          "indirect_after": 200,
          "change": "+300%"
      }
  },
  "analysis": "BOLT优化的整体评估和权衡"
}
```

### 示例提示词

```
请对比分析BOLT优化前后的二进制性能。

优化前二进制: /path/to/binary_opt
优化后二进制: /path/to/binary_bolted

请提供：

1. 性能对比：
   - 使用perf进行基准测试
   - 对比CPU周期数
   - 分析缓存性能差异
   - 测量分支预测准确率

2. 代码大小对比：
   - 使用size工具查看段大小
   - 统计函数大小分布
   - 计算整体代码膨胀率

3. 二进制特性分析：
   - 使用objdump/llvm-objdump分析
   - 统计重定位和跳转指令
   - 分析间接跳转的增加

4. 权衡分析：
   - 性能提升是否值得代码膨胀
   - 哪些场景下BOLT效果最好
   - 有哪些负面影响（如调试困难）

5. 生成对比报告
```

---

## 步骤6：函数调用图(CG)分析

### 最佳提示词

```
你是一个专业的编译器专家，擅长分析二进制的函数调用图。

### 分析目标
1. 重建整个程序的函数调用图
2. 识别调用关系
3. 分析调用深度和广度
4. 检测递归调用

### CG分析要点

#### 调用关系
- 直接调用（直接call指令）
- 间接调用（通过函数指针）
- 虚函数调用

#### 递归检测
- 尾递归
- 间接递归
- 递归深度限制

#### 调用链分析
- 最长调用链
- 热点路径
- 关键函数

### 输出格式

```json
{
  "call_graph": {
      "nodes": [
          {
              "function": "函数名",
              "address": "地址",
              "is_leaf": false,
              "callers": ["caller1", "caller2"],
              "callees": ["callee1", "callee2"]
          }
      ],
      "edges": [...],
      "metrics": {
          "total_functions": 200,
          "average_depth": 3.5,
          "max_depth": 10,
          "recursive_functions": 5
      }
  }
}
```

### 示例提示词

```
请分析这个BOLT优化后二进制文件的函数调用图。

二进制文件: /path/to/binary

请提供：

1. CG重建：
   - 识别所有函数及其地址
   - 分析函数之间的调用关系
   - 构建完整的调用图

2. 调用链分析：
   - 最长调用链是哪个？
   - 热点函数有哪些？
   - 是否存在长调用路径？

3. 递归检测：
   - 是否有尾递归？
   - 递归深度是否安全？
   - 是否存在递归爆炸风险？

4. BOLT影响：
   - BOLT是否改变了调用关系？
   - 是否添加了新的调用？
   - 对CG重建的影响

5. 使用llvm-bolt-binary-analysis工具验证CG
```

---

## 步骤7：代码段布局分析

### 最佳提示词

```
你是一个专业的二进制布局分析专家，擅长分析代码段的布局和优化。

### 分析目标
1. 分析代码段的分布
2. 识别段对齐和填充
3. 分析函数在段中的布局
4. 评估局部性原理的应用

### 段布局要点

#### 段类型
- .text - 代码段
- .data - 数据段
- .rodata - 只读数据段
- .bss - 未初始化数据段

#### 局局策略
- 热函数分组
- 冷函数分组
- 基于类型的分组
- 基于调用关系的分组

#### 对齐和填充
- 函数对齐边界
- 段内填充
- TLB优化

### 输出格式

```json
{
  "section_layout": {
      ".text": {
          "size": "0x4000",
          "functions": ["func1", "func2"],
          "alignment": "16字节",
          "fragmentation": "moderate"
      },
      ".data": {
          "size": "0x1000",
          "global_variables": ["var1", "经常访问的变量"],
          "locality_score": 0.85
      }
  },
  "locality_analysis": {
      "hot_hot_locality": 0.9,
      "hot_cold_locality": 0.3,
      "cold_cold_locality": 0.7
      "overall_locality": 0.78
  }
}
```

### 示例提示词

```
请分析这个BOLT优化后二进制文件的代码段布局。

二进制文件: /path/to/binary

请提供：

1. 段布局分析：
   - 使用readelf/llvm-objdump查看段信息
   - 分析.text段中的函数分布
   - .data段中的变量布局

2. 局部性原理分析：
   - 热函数是否集中在一起？
   - 冷函数如何布局？
   - 是否遵循了空间局部性原理？

3. 对齐和填充分析：
   - 函数边界是否对齐？
   - 是否有大量填充？
   - 对齐粒度是多少？

4. BOLT优化策略：
   - BOLT使用了什么分组策略？
   - 是否基于profile数据？
   - 策略是否有效？

5. 使用llvm-bolt-binary分析工具验证布局
```

---

## 步骤8：指令级优化分析

### 最佳提示词

```
你是一个专业的编译器优化专家，擅长分析指令级优化。

### 分析目标
1. 分析指令序列
2. 识别优化机会
3. 检测反优化模式
4. 分析指令调度

### 指令优化要点

#### 指令选择
- 指令长度（1/2/3字节）
- 访问模式优化
- 特殊指令的使用（SSE/AVX）

#### 代码生成
- 指令重排序
- 消除冗余指令
- 常量合并

#### 循环展开
- 循环是否展开
- 展开因子是多少
- 代码大小vs性能权衡

### 输出格式

```json
{
  "optimization_techniques": [
      {
          "technique": "指令重排序",
          "function": "函数名",
          "before": "原始指令序列",
          "after": "优化后指令序列",
          "improvement": "描述"
      }
  ],
  "anti_patterns": [
      {
          "pattern": "反优化模式",
          "function": "函数名",
          "severity": "high/medium/low",
          "suggestion": "改进建议"
      }
  ],
  "instruction_mix": {
      "total_instructions": 5000,
      "legacy_mode_instructions": 400,
      "sse_avx_instructions": 800,
      "branch_instructions": 300
  }
}
```

### 示例提示词

```
请分析这个BOLT优化后二进制文件的指令级优化。

二进制文件: /path/to/binary
反汇编工具: objdump/llvm-objdump

请提供：

1. 指令优化分析：
   - 对比优化前后的指令序列
   - 识别优化技术（指令重排序、常量传播、死代码消除）
   - 评估优化效果

2. SIMD优化分析：
   - 是否使用了SSE/AVX指令？
   - 向量化了哪些操作？
   - 加速比是多少？

3. 循环展开分析：
   - 循环是否被展开？
   - 展开因子是多少？
   - 是否有代码膨胀？

4. 反优化检测：
   - 是否有明显的反优化？
   - 指令调度是否合理？
   - 是否有性能陷阱？

5. 使用llvm-bolt-binary-analysis和反汇编工具
```

---

## 步骤9：综合性能优化报告

### 最佳提示词

```
你是一个专业的编译器性能分析专家，需要生成完整的BOLT优化效果评估报告。

### 报告结构

#### 执行摘要
- 二进制文件信息
- 优化类型和级别
- 测试环境

#### 性能数据
- 优化前后基准测试结果
- 不同workload下的性能
- 性能提升百分比

#### 代码影响
- 代码大小变化
- 二进制大小变化
- 段布局变化

#### 安全分析
- pac-ret分析结果
- 安全漏洞风险评估

#### 详细分析
- 热点函数分析
- 控制流图分析
- 指令级优化
- 局部性分析

### 输出格式

```json
{
  "summary": {
      "binary": "二进制文件",
      "optimization": "BOLT -O3",
      "performance_improvement": "15.3%"
  },
  "performance": {
      "runtime_before": "5.23s",
      "runtime_after": "4.53s",
      "speedup": "1.15x",
      "confidence": "95%"
  },
  "code_size": {
      "text_before": "0x4000",
      "text_after": "0x4200",
      "increase": "5%"
  },
  "security": {
      "vulnerabilities": 0,
      "risk_level": "low"
  },
  "recommendations": [
      "建议1",
      "建议2"
  ]
}
```

### 示例提示词

```
请生成BOLT优化效果的综合评估报告。

优化前二进制: /path/to/binary_opt
优化后二进制: /path/to/binary_bolted
测试环境: Intel i7-9700K, Ubuntu 22.04

请提供：

1. 执行摘要：
   - 测试的workload类型
   - 测试次数
   - 环境信息

2. 性能分析：
   - 使用perf进行基准测试
   - 生成性能报告
   - 计算speedup百分比
   - 分析性能差异的原因

3. 代码大小分析：
   - 比较优化前后的代码大小
   - 分析代码膨胀率
   - 识别膨胀的主要来源

4. 安全分析：
   - 进行pac-ret安全扫描
   - 评估安全风险
   - 识别潜在问题

5. 综合评估：
   - BOLT优化是否值得？
   - 在什么场景下效果最好？
   - 有哪些建议和注意事项？

6. 生成Markdown格式的详细报告
```

---

## 通用分析提示词模板

### 基础信息收集

```
请分析这个BOLT优化相关的二进制文件，并提供详细的技术分析报告。

二进制文件路径: {binary_path}
优化类型: {optimization_type} (BOLT / 非BOLT)
优化级别: {optimization_level}

请提供以下信息：

1. 基本信息
   - 文件类型（ELF/PE/Mach-O）
   - 架构（x86_64/ARM64等）
   - 段列表和大小

2. BOLT相关信息
   - 是否包含BAT section
   - 是否经过perf2bolt采样
   - 优化配置（如果可获取）

3. 分析维度
   - 性能热点分析
   - 代码段布局
   - 控制流和CFG
   - 安全性扫描
   - 指令级优化
   - 优化效果对比

4. 输出要求
   - 使用Markdown格式
   - 包含代码示例和图表
   - 提供清晰的结论和建议
```

### 高级分析提示词

```
作为资深编译器专家，请深入分析这个BOLT优化案例，并从多个角度进行评估：

技术背景：
- 编译器：{compiler}
- 优化级别：{optimization_level}
- 目标架构：{target_architecture}

分析要求：
1. 使用llvm-bolt-binary-analysis工具进行系统化分析
2. 结合perf和llvm-objdump工具进行深入挖掘
3. 重点关注以下方面：
   - 性能热点的成因分析
   - BOLT特有的优化技术
   - 代码膨胀和质量权衡
   - 安全性影响评估
   - 与其他优化技术的对比

4. 提供可操作的建议：
   - 如何进一步提升性能
   - 如何平衡代码大小和性能
   - 如何避免潜在问题
   - 最佳实践和注意事项

5. 输出技术深度：
   - 深入到汇编/机器码级别
   - 理解编译器和链接器的工作原理
   - 展示专业性的技术分析能力
```

---

## 工具使用提示词

### llvm-bolt-binary-analysis 工具

```
你熟练掌握llvm-bolt-binary-analysis工具，请使用它来分析BOLT优化后的二进制。

工具命令：llvm-bolt-binary-analysis [options] <binary>

常用选项：
- --scanners=<scanner_list> - 运行指定的分析器
- --format=<format> - 输出格式
- --output=<file> - 输出到文件

可用的分析器：
- pac-ret - pac-ret攻击检测
- cfg - 控制流图分析
- bat - BAT section分析
- layout - 布局分析

请执行：
1. 运行多个分析器以获得全面视图
2. 解析工具输出
3. 识别关键发现
4. 生成结构化的分析报告
```

### perf工具

```
你熟练掌握Linux perf性能分析工具，请用它来分析BOLT优化前后的性能差异。

常用命令：
- perf stat - 查看性能事件统计
- perf record - 记录性能数据
- perf report - 生成报告

BOLT相关命令：
- perf record -e cycles:u -j any -- <binary>
- llvm-bolt-heatmap -p perf.data <binary>

请执行：
1. 设计合理的perf测试方案
2. 收集性能数据（cycles, instructions, cache misses, branches）
3. 生成性能对比报告
4. 识别性能差异的根本原因
```

### 反汇编工具

```
你熟练掌握反汇编工具，请使用它们来分析BOLT优化的代码变换。

工具选择：
- objdump - GNU binutils反汇编
- llvm-objdump - LLVM反汇编工具
- ndismasm - Netwide反汇编器

重点分析：
1. 对比优化前后的指令序列
2. 识别BOLT特有的代码变换
3. 分析地址重定位和跳转
4. 评估优化质量

请提供：
1. 关键函数的反汇编对比
2. 优化技术的识别和解释
3. 性能影响评估
4. 代码质量评价
```

---

## 综合分析提示词（最终版）

```
作为DeepWiki的核心分析引擎，请对BOLT优化的二进制进行全面深入的技术分析，并生成专业的技术文档。

输入二进制：{binary_path}
优化类型：BOLT

请执行以下完整的分析流程：

## 第一阶段：性能分析
1. 使用perf生成采样数据：`perf record -e cycles:u,cache-misses,instructions -j any -- {binary}`
2. 转换为热力图：`llvm-bolt-heatmap -p perf.data {binary}`
3. 分析热力图，识别top 10热点函数及其特征

## 第二阶段：安全分析
1. 执行pac-ret安全扫描：`llvm-bolt-binary-analysis --scanners=pac-ret {binary}`
2. 分析pac-ret gadget和攻击面
3. 评估安全风险等级

## 第三阶段：结构分析
1. 使用反汇编工具分析关键热点函数
2. 重建控制流图(CFG)
3. 分析BAT section（如果存在）
4. 评估代码段布局和局部性

## 第四阶段：代码对比
1. 对比优化前后的指令序列
2. 识别BOLT优化技术：
   - 函数重排序
   - 热冷代码分离
   - delta编码
   - 跳转表添加
3. 评估优化效果和代码膨胀

## 第五阶段：综合评估
1. 性能提升：基于热力图数据
2. 代码膨胀：基于段大小对比
3. 安全性：基于pac-ret扫描结果
4. 权衡分析：性能vs代码vs安全性
5. 改进建议：针对性的优化建议

## 输出要求
- 使用Markdown格式，包含代码示例
- 提供清晰的图表和表格
- 深入技术原理，适合技术人员阅读
- 结构清晰，便于导航
- 包含具体的数据和指标

最终输出应是一份专业的BOLT优化技术分析报告，能够帮助开发者深入理解BOLT优化机制和效果。
```

---

## 最佳实践提示词

### 提示词设计原则

1. **明确性** - 清晰定义分析目标和范围
2. **结构化** - 提供结构化的输出格式
3. **技术深度** - 深入到汇编和机器码级别
4. **可操作性** - 提供可执行的分析命令
5. **全面性** - 覆盖性能、安全、结构等多个维度
6. **对比性** - 始终对比优化前后的差异
7. **专业性** - 使用准确的技术术语和概念

### 提示词优化技巧

- 添加具体的工具命令示例
- 包含JSON/Markdown输出格式说明
- 提供分析维度和检查清单
- 使用角色定位（专家、分析师等）
- 要求深入解释技术原理
- 引用具体的文档或资源

### 常见分析任务

1. 性能热点识别和优化
2. 安全漏洞扫描和评估
3. 控制流图重建和分析
4. 代码布局和局部性评估
5. 指令级优化分析
6. BAT section解析和理解
7. 优化效果综合评估

---

**版本**: 1.0  
**最后更新**: 2026-02-13
