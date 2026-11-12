# 讲透 DRL-robot-navigation-IR-SIM

> [reiniscimurs/DRL-robot-navigation-IR-SIM](https://github.com/reiniscimurs/DRL-robot-navigation-IR-SIM)：基于红外（IR）仿真的机器人导航深度强化学习——PyTorch 实现 TD3/DDPG/CNNTD3/RCPG/SAC/PPO 单智能体 + attention-marlTD3 多智能体，含 Max Upper Bound Loss（Q 高估正则）与预训练/离线学习。
>
> 本地仓：`/usr-data/data1/workspace/rl/DRL-robot-navigation-IR-SIM` @ 31e1a4d（45 py 文件，工作区干净）。

## 全链状态表（2026-10-14）

| 步骤 | 状态 | 产物 | 备注 |
|---|---|---|---|
| ① DeepWiki 全量 | ✅ 完成 | `deepwiki/`（24 页 100%，全文 348K 字符） | MCP 通道 `dw_fetch_mcp.py` 一次过 exit 0，零 extra 零 missing，2026-10-14 |
| ①′ 逐行注释版 | ✅ 完成 | `code-annotated/`（45 文件全量，8126→9367 行） | 2026-10-14：12 批子代理 4 并发；31 文件 AST 全等价+可编译+空行零净减终验 0 坏；12 条源码级实证勘误见 `code-annotated/README.md` |
| ② understand 图谱 | ⏳ 待做 | — | 45 py 小仓，预计 2-3 批 |
| ③ ONBOARDING | ⏳ 待做 | — | 依赖 ② |
| ④ explain 系列 | ⏳ 待做 | — | 依赖 ② |

## deepwiki/ 结构（8 章 16 子页）

- **1 Overview**（1.1 Getting Started）
- **2 Core Training System**（2.1 Simulation Environments · 2.2 Data Management and Replay Buffers）
- **3 Single-Agent Models**（3.1 TD3 and DDPG · 3.2 CNNTD3 · 3.3 RCPG · 3.4 SAC · 3.5 PPO · 3.6 HCM）
- **4 MARL**（4.1 MARL Simulation Environment · 4.2 marlTD3 with Attention Mechanisms）
- **5 Environment Configuration**
- **6 Testing and Validation**（6.1 Model · 6.2 Simulation/Environment · 6.3 Buffer and Utility）
- **7 Advanced Features**（7.1 Max Upper Bound Loss · 7.2 Pretraining and Offline Learning）
- **8 Development and Deployment**

内容亮点：7.1 Max Upper Bound Loss 是该仓独有贡献（critic loss 加惩罚项压制 Q 值超过理论上界，作用于 TD3/DDPG/CNNTD3）；4.2 attention-marlTD3 多智能体；RCPG（recurrent critic? 待 understand 阶段核实全称）。

## 抓取元数据

- 通道：`mcp.deepwiki.com/mcp`（stateless streamable HTTP，工具 `~/ai/pipeline-bin/deepwiki/dw_fetch_mcp.py`）
- 覆盖率对账：`deepwiki/_coverage-check.md`（24/24=100%）；每页头部带源文件 `<details>` 清单+行号锚（`robot_nav/models/...`），understand 阶段交叉对账素材
- 抓取日期：2026-10-14

## 勘误清单（understand 阶段回填）

- （暂无；RCPG 全称待核实）
