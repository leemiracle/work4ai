# RL 算法知识库 · DeepWiki 素材索引 + 算法族谱

> 素材底座：`.research/deepwiki-rl/`（DeepWiki 抓取，2026-08-20 完成，torchrl 40/40 + cleanrl 33/33，零失败）
> 本文件是它们的**挂网点**与选读顺序——孤儿素材 = 死亡内容，此处即网。

## 一、选读路径（按任务类型）

| 你要做什么 | 先读 | 再读 | 跳过 |
|---|---|---|---|
| 手写算法入门 | cleanrl §3.1-3.3（PPO/DQN/SAC 单文件实现）| cleanrl §1-2（跑通流程）| §4 JAX（后置）|
| 选训练框架 | torchrl §1-2（TensorDict 哲学）| torchrl §7（损失模块架构）| §11 教程 |
| 分布式/吞吐 | torchrl §4.2（分布式收集）| cleanrl §8（云部署）| — |
| 环境接入 | torchrl §3（EnvBase/Transforms）| cleanrl §5（Atari/MuJoCo/Procgen）| — |
| LLM×RL | torchrl §9（LLM 训练目标/环境）| — | — |
| 多智能体 | torchrl §10 | cleanrl §5.5 | — |
| 评测与调参 | cleanrl §7（benchmark/optuna）| torchrl §8 | — |

## 二、算法族谱（两库视角对照）

```
                 ┌─ 值方法：DQN ─────────── cleanrl §3.2（含 Double/Dueling/Noisy 变体）
                 │
    RL ──────────┼─ 策略梯度：REINFORCE ─→ PPO ─── cleanrl §3.1（单文件）；torchrl §7.2
                 │                    └→ TRPO/A2C
                 ├─ 离线策略 AC：DDPG → TD3 → SAC ─ cleanrl §3.3-3.4；torchrl §7.3
                 ├─ 分布式：IMPALA/Ape-X ───────── torchrl §4.2（收集侧基建）
                 └─ LLM 侧：GRPO/RLVR ─────────── torchrl §9.3（训练目标抽象）
```

**库哲学对照**（选型根本依据）：
- **CleanRL**：单文件可读性 > 一切。每个算法一个 ~300-1000 行独立 .py，高级特性（wandb/seed/vector env）都是装饰性可选。**教学与魔改首选**。
- **TorchRL**：TensorDict 数据基建（§2.1）统一一切——环境/模块/损失/回放全走同一张"嵌套张量字典"。**生产组合首选**，但学习曲线在 §2。

## 三、本项目金字塔与两库的接口

| 层 | 本插件工具 | 两库对应物 |
|---|---|---|
| L3 训练冒烟 | `tools/rl_smoke.py`（方向性断言）| cleanrl 的 `--track` 前 100 步逻辑等价物 |
| L4 复现 | `tools/rl_repro.sh` | cleanrl 的 seed 体系（§2.2 的 seed-xxx tag 约定）|
| 反 Goodhart | `governance/goodhart_guards.py` | 无对应——RL 库不做 reward 审计，这是研究级缺口 |

## 四、素材清单（.research/deepwiki-rl/ 完整目录）

- `torchrl/1-overview.md` … `12.2-documentation-system.md`（40 件，TensorDict→环境→收集→回放→模块→算法→训练器→**LLM 集成**→多智能体→构建）
- `cleanrl/1-overview.md` … `12-glossary.md`（33 件，含 JAX 线 §4 与云部署 §8）
- 抓取器与校验：`fetch_deepwiki.py`（限速 1.2s + 429 退避 + 穷举核对）

## 五、RL 研究的三大坑（知识库层级的预防针）

1. **静默不学习**：循环在跑、reward 恒常数——L3 冒烟的存在理由。
2. **reward hacking**：agent 找到 reward 的 bug 而非任务（= 本插件 Goodhart 三查的领域形态）：环境可被写文件伪造 / eval 集泄漏进 train / 终止条件被利用。
3. **不可复现的"提升"**：seed 未固定/GPU 非确定/环境版本漂移——L4 的存在理由；对比实验前先证基线可复现。
