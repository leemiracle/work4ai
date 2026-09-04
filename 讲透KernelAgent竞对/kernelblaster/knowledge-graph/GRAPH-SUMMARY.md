# KernelBlaster 知识图谱摘要

- 生成：2026-09-03（understand --language zh 全链路）· git commit `84237f91a391`
- 规模：**269 节点 / 589 边 / 10 架构层 / 15 步导览**
- 校验：内联校验 0 issue（详见 FINAL-REPORT）
- 交互：在本体仓（/data/usershare/ai/KernelBlaster）运行 /understand-dashboard 或 /understand-chat 查询

## 节点类型分布

| 类型 | 数量 |
|---|---|
| function | 150 |
| class | 55 |
| file | 52 |
| config | 5 |
| document | 5 |
| service | 2 |

## 边类型分布

| 类型 | 数量 |
|---|---|
| contains | 206 |
| exports | 195 |
| imports | 96 |
| calls | 61 |
| documents | 11 |
| depends_on | 6 |
| inherits | 5 |
| configures | 5 |
| related | 3 |
| deploys | 1 |

## 架构层

- **入口与实验脚本层**（6 节点）：驱动整个 MAIC-RL 优化管线的 CLI 入口：run_RL 批量实验调度（Semaphore 并发+知识库注入）、eager/torch.compile 
- **Agent 核心层**（7 节点）：MAIC-RL 优化 agent 本体：单发 NCU 优化 agent（opt_ncu_minimal）、RL 探索 agent（opt_ncu_rl）、反思迭
- **Agent 基础设施层**（10 节点）：agent 的支撑设施：LLM 查询/重试路由、异步批量队列、本地量化推理（transformers），以及 NCU 报告解析与标注、GPU server 远程
- **图编排与工作流层**（7 节点）：LangGraph 图执行引擎：图构建与路由（graph）、TypedDict 状态定义（state）、RL+NCU 优化图节点（optimization_rl
- **编译与 GPU 服务层**（9 节点）：FastAPI 无状态服务集群：CompileServer（CUDA 编译 worker 队列）、GPUServer（GPU 执行）、统一 serve_api 
- **资源管理层**（3 节点）：服务端资源的客户端治理：带连接池的 HTTP 客户端单例（client）与 CompileServer/GPUServer 进程包装生命周期管理（servers
- **数据与优化知识库层**（7 节点）：KernelBench 数据集加载器（dataset 基类、kernelbench 及 CUDA artifacts 变体、精度过滤）与出厂优化知识库（opti
- **配置与共享基础层**（8 节点）：被所有模块依赖的地基（config 包 fan-in 全库最高）：环境配置（config.py）、GPU 硬件枚举检测（gpu_config）、共享 CLI 参
- **容器基础设施层**（4 节点）：Docker 部署定义：NVIDIA NGC 基础镜像与 PyTorch build-stage 双 Dockerfile、容器入口脚本（用户管理）与容器内 P
- **文档层**（3 节点）：项目级文档：MAIC-RL 框架总览 README、贡献指南（DCO）与论文图表资产说明。

## 导览步骤

1. 项目概览：MAIC-RL 是什么
2. 一键入口：shell 包装与共享 GPU 服务
3. 批量实验调度：run_RL 主入口
4. 配置地基：全库 fan-in 之冠
5. 数据层：KernelBench 与策展 CUDA 工件
6. 工作流编排：LangGraph 图与状态契约
7. 图核心节点：optimization_rl_ncu
8. 反馈迭代基座：FeedbackAgent 模板
9. RL 主循环：RLNCUAgent 探索与奖励
10. RL 组件：轨迹、ReplayBuffer 与策略更新
11. 持久优化知识库：预测-实测对账账本
12. 评测设施：双基线与 NCU 重剖析
13. Agent 基础设施：LLM 路由与 NCU 解析
14. 编译与 GPU 服务集群
15. 服务化与容器部署：收官
