# KernelMem 知识图谱摘要

- 生成：2026-09-03（understand --language zh 全链路）· git commit `8b57ccc9adc2`
- 规模：**129 节点 / 258 边 / 6 架构层 / 12 步导览**
- 校验：内联校验 0 issue（详见 FINAL-REPORT）
- 交互：在本体仓（/data/usershare/ai/KernelMem）运行 /understand-dashboard 或 /understand-chat 查询

## 节点类型分布

| 类型 | 数量 |
|---|---|
| function | 93 |
| file | 22 |
| class | 8 |
| config | 4 |
| document | 2 |

## 边类型分布

| 类型 | 数量 |
|---|---|
| contains | 101 |
| exports | 101 |
| calls | 25 |
| imports | 18 |
| configures | 4 |
| documents | 4 |
| depends_on | 3 |
| inherits | 1 |
| related | 1 |

## 架构层

- **编排与剖析层**（4 节点）：KernelMem 系统主控：main_memory_latest.py 驱动 生成→编译评测→NCU/nsys 剖析→judger 修复/优化→记忆回灌 的自
- **记忆化提示词层**（13 节点）：面向 LLM 的提示词资产：generate/judger/optimization/error 各阶段记忆化提示词、few-shot 示例与 GPU 硬件规格
- **LLM 后端接口层**（2 节点）：封装本地推理与查询服务式的大模型调用接口（query_server→llm_local），为生成与裁判环节提供统一推理通道。
- **编译评测与工具层**（3 节点）：CUDA kernel 的编译执行与子进程隔离评测、kernel 文件 IO 与打印工具，是性能真值采集的底层基础设施。
- **长期记忆资产层**（2 节点）：跨任务沉淀的长期记忆库：瓶颈先验 YAML 与 gate 取值表，向机器检查与优化裁判注入历史经验（configures→machine_check_ver2/
- **配置与文档层**（4 节点）：NCU 剖析采集配置（configures→run_ncu_memory.py）、项目 README 及知识图谱分析工具配置等工程支撑文件。

## 导览步骤

1. 项目概览：KernelMem 是什么
2. 主编排入口：main() 与单任务循环
3. 进化个体与 kernel I/O
4. 种子生成提示词
5. 编译评测：地面真值与子进程隔离
6. NCU 剖析：性能指标采集
7. nsys 剖析：启动次数证据
8. 修复链：错误记忆与 judger 诊断
9. 长期记忆：memorybank 与机器检查
10. 优化裁判与优化提示词
11. LLM 后端：统一推理网关
12. 汇总输出与成本核算
