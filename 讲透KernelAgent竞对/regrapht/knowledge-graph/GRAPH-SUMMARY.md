# ReGraphT 知识图谱摘要

- 生成：2026-09-03（understand --language zh 全链路）· git commit `d1ea9b4e91e5`
- 规模：**48 节点 / 84 边 / 6 架构层 / 9 步导览**
- 校验：内联校验 0 issue（详见 FINAL-REPORT）
- 交互：在本体仓（/data/usershare/ai/ReGraphT）运行 /understand-dashboard 或 /understand-chat 查询

## 节点类型分布

| 类型 | 数量 |
|---|---|
| file | 18 |
| function | 17 |
| class | 11 |
| document | 1 |
| config | 1 |

## 边类型分布

| 类型 | 数量 |
|---|---|
| contains | 28 |
| exports | 22 |
| imports | 21 |
| calls | 7 |
| depends_on | 2 |
| inherits | 2 |
| documents | 1 |
| related | 1 |

## 架构层

- **入口与编排层**（1 节点）：评测主入口 run.py：按 --method 组装七种推理器（ReGraphT 系从本地 JSON 加载推理图注入 reasoner），再按数据集创建 Exe
- **推理图核心层**（3 节点）：ReGraphT 方法的心脏：ReGraph.py 定义 ReGraphNode/ReGraphEdge/ReGraph 数据结构（节点=优化方法、边=状态迁移
- **提示词层**（3 节点）：集中管理驱动大模型行为的系统提示词模板：ReGraph.py 提供图构建用的分步优化与重标注两套提示词，agent.py 提供 STANDARD/COT 消融基
- **推理后端层**（4 节点）：LLM 推理后端抽象与实现：inference_engine.py 定义 EngineType 枚举、注册表与 InferenceEngine 抽象基类，loc
- **执行器与推理器占位层**（7 节点）：评测执行的骨架与待补实现：executor/base.py 提供执行器注册机制与持有 Reasoner 的抽象基类；reasoner 侧 base.py 定义持
- **文档与配置层**（2 节点）：项目级文档与仓库配置：README.md 交代论文主旨（From Large to Small: 经推理图把大模型 CUDA 优化专长迁移给小模型，ICLR 2

## 导览步骤

1. 项目概览
2. 评测主入口
3. 离线构图流水线
4. 推理图数据结构
5. 提示词模板库
6. 推理后端抽象
7. 本地与远程引擎实现
8. 推理器与执行器抽象
9. 占位现状与工程启示
