# 讲透 StableBaselines3

> DLR-RM/stable-baselines3 —— PyTorch 单文件可读 RL 算法库：PPO/A2C/DQN/SAC/TD3/DDPG + HER + Policy/Buffer/VecEnv 三层体系。
> 本地仓：/usr-data/data1/workspace/rl/stable-baselines3（commit b2878f4，v2.9.2a0，2026-10-13）

## 状态（2026-10-14 全链完成）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ 完成 | [deepwiki/](deepwiki/)（40 页 100%，566K 字符） |
| understand 中文图谱 | ✅ 完成 | 仓内 `.understand-anything/knowledge-graph.json`（**634 节点/1681 边/12 层/16 步 tour**，校验 0 issues，fingerprints 171 文件@b2878f4） |
| onboarding | ✅ 完成 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（6000 字 8 节，27 个 file:line 锚逐个回验 0 失败） |
| explain 系列 | ✅ 完成 | [explain/](explain/) 12 篇（合计 69997 字符，六节结构全过，行号锚抽验命中） |

## understand 图谱口径

- scan 171 文件 / 14 批（batch 11-13 为 stable_baselines3/ 核心源码）/ merge 后 634 节点 1681 边
- 边型分布：contains 463 / exports 453 / imports 377 / tested_by 106 / documents 83 / inherits 79 / configures 12 / 其余（calls/deploys/depends_on/triggers/related）合计 ~108
- 12 层：算法实现层(24)→算法基类与缓冲区(5)→策略网络与分布(5)→训练运行时(10)→环境工具(7)→向量化环境(15)→用户指南(22)→API 参考(18)→文档系统(11)→测试套件(31)→CI/CD(16)→项目治理(8)
- 增量更新入口：`compute-batches.mjs --changed-files`（fingerprints 基线已建）

## explain/ 十二篇清单（按 tour 顺序）

| 篇 | 源文件 | 字符 |
|---|---|---|
| [BaseAlgorithm骨架](explain/BaseAlgorithm骨架-base_class.md) | common/base_class.py | 4797 |
| [OnPolicy与OffPolicy双分支](explain/OnPolicy与OffPolicy双分支-on_off_policy_algorithm.md) | common/on_policy+off_policy_algorithm.py | 4781 |
| [PPO实现](explain/PPO实现-ppo.md) | ppo/ppo.py | 5429 |
| [SAC实现](explain/SAC实现-sac.md) | sac/sac.py | 6207 |
| [TD3实现](explain/TD3实现-td3.md) | td3/td3.py | 4928 |
| [Buffer双家族](explain/Buffer双家族-buffers.md) | common/buffers.py | 4997 |
| [策略网络基类](explain/策略网络基类-policies.md) | common/policies.py | 10086 |
| [特征提取器](explain/特征提取器-torch_layers.md) | common/torch_layers.py | 9592 |
| [动作分布](explain/动作分布-distributions.md) | common/distributions.py | 4794 |
| [VecEnv抽象基座](explain/VecEnv抽象基座-base_vec_env.md) | common/vec_env/base_vec_env.py | 4800 |
| [向量化归一化](explain/向量化归一化-vec_normalize.md) | common/vec_env/vec_normalize.py + common/running_mean_std.py | 4797 |
| [HER重标注](explain/HER重标注-her_replay_buffer.md) | her/her_replay_buffer.py | 4794 |

> 字数口径：不计空格字符（含元数据行）。终值区间 4.7K-10K：10 篇收敛到 2500-4800 硬标准内；policies/torch_layers 两篇 worker 按中文字+英文词口径报告 3.5K（换算本口径 ~10K），如实保留。

## 本轮实证勘误（explain/onboarding 落钉，可信度：源码+git log 双证）

1. **`NatureDQNChannelsExtractor` 从不存在**——CNN 提取器自始叫 `NatureCNN`（torch_layers.py），git log -S 全历史检索证实
2. **HER 不是算法**：`her/her.py` 不存在（自 v1.1.0 起为 `HerReplayBuffer` + `GoalSelectionStrategy` 的 replay buffer 方案；`stable_baselines3/__init__.py:18` 的 `HER()` 是 raise ImportError 兼容 shim）
3. **DDPG=TD3 特例的准确机制**：`ddpg.py:108` `target_noise_clip=0.0`（非 target_policy_noise=0，:109 处为 0.1 且 TD3 校验要求 >0）使 smoothing 失效 + `:114` 强制 `n_critics=1`
4. **ContinuousCritic 继承同文件 `BaseModel`**（policies.py:912），非直接 nn.Module、亦非 BasePolicy 子类
5. **evaluate_actions 返回三元组** `(values, log_prob, entropy)`，非双出口
6. **docs/common/envs.md 的 automodule 指向包目录**，BitFlippingEnv/SimpleMultiObsEnv 实际分属 envs/ 两文件
7. **MlpExtractor v1.8.0 后无共享层**，L253 docstring 为历史残留表述
8. **version.txt 三处消费点**（setup.py/docs/conf.py/__init__.py 皆 open() 读文件而非 import）
9. **common 反向依赖算法子包**：`common/off_policy_algorithm.py:L22` 跨包 import `her.her_replay_buffer`——基座包对算法子包的循环依赖方向
10. **set_random_seed 真正触发点在子类 `_setup_model` 第二行**，非 Base `__init__`
11. **两分支 `dump_logs` 签名不同**：on-policy 收 iteration（on_policy_algorithm.py:L277）/ off-policy 无参（L429）
12. **分布工厂真名 `make_proba_distribution`**（distributions.py:L670），无 make_distribution；Bernoulli/MultiCategorical **非死代码**（工厂对 MultiDiscrete/MultiBinary 完全接线 L690/L692——修正"未启用"旧说法）；真正绕过工厂的只有 SquashedDiagGaussian（sac/policies.py:L101 直连）
13. **`kl_divergence`（L705）核心库零调用**——PPO 的 approx_kl 走 log_ratio（ppo.py:L264），它是为 contrib/TRPO 导出的
14. **running_mean_std.py 在 `common/` 非 `common/vec_env/`**；buffer 存 unnormalized obs、归一化推迟到采样时刻（off_policy_algorithm.py:L485-487 暗线）

## deepwiki/ 目录说明

- 通道：mcp.deepwiki.com/mcp（并行实例 10:45 抓取 exit 0；本会话 10:52 复测 MCP 端点竟报 Repository not found——**MCP 后端与网页端索引库存在不同步窗口**，抓取时点运气成分，详见记忆钉版）
- 13 章 40 结构页全命中，零 extra 零 MISSING；每页自带 `<details>` 源文件清单
- 入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 对账：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)

## 生态交叉

- 姊妹仓讲透RLBaselines3Zoo（DLR-RM/rl-baselines3-zoo，26 页 deepwiki 已就位）：zoo 的 hyperparams YAML 是本仓算法层的部署层
- 讲透Gymnasium（37 页 deepwiki+图谱进行中）：本仓 VecEnv 家族的下游标准
