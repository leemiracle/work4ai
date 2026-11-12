# SAC 实现：sac.py——最大熵 RL 的四重优化循环

## 角色定位

`stable_baselines3/sac/sac.py` 全文 336 行，实现 Soft Actor-Critic（Haarnoja et al., 1801.01290，见 sac.py:L27），是 SB3 中样本效率最高的连续控制算法。`class SAC(OffPolicyAlgorithm)`（sac.py:L19）继承离线策略基类，环境交互与 replay buffer 读写全在基类，本文件核心是 `train()`（sac.py:L205-305）——一个每梯度步串行执行 **alpha 优化 → critic 优化 → actor 优化 → polyak 更新** 的四重循环。注意这是 SAC v2 形态：文件开头注明 "we use double q target and not value target"（sac.py:L30-31，issue #270），没有原论文的独立 V 网络，双 Q 直接充当 value function；且 `ent_coef="auto"` 是默认（sac.py:L111），自动温度调节不是可选项而是默认行为。类头属性注解（sac.py:L89-92：`actor: Actor`、`critic: ContinuousCritic`、`critic_target: ContinuousCritic`）声明了与 PPO 单网络架构的根本区别：**三组参数、两个独立 optimizer**（sac.py:L209），外加可选的 alpha optimizer。

## 内部结构

**构造（sac.py:L94-163）**：默认超参 `buffer_size=1_000_000`（sac.py:L99）、`learning_starts=100`（sac.py:L100）、`batch_size=256`（sac.py:L101）、`tau=0.005`（sac.py:L102）、`train_freq=1` + `gradient_steps=1`（sac.py:L104-105，每采 1 步做 1 次梯度更新）、`target_update_interval=1`（sac.py:L112）、`target_entropy="auto"`（sac.py:L113）。动作空间限定 `spaces.Box`（sac.py:L150）——这是 tanh squashing 架构的直接后果（见设计决策 4）。

**_setup_model（sac.py:L165-198）**：先 `_create_aliases()`（sac.py:L167，实现在 L200-203）；抓出 critic 里 `running_` 开头的 batch norm 统计（sac.py:L169-170）供硬拷贝；然后展开两个 "auto"——`target_entropy="auto"` 固定为 `-prod(action_dim)`（sac.py:L172-174，每维动作配 -1 熵预算，SAC v2 论文启发式）；`ent_coef="auto"` 初始化 `log_ent_coef = log(init_value)` 并 `requires_grad_(True)`（sac.py:L192，默认 init=1.0，`"auto_0.1"` 语法可改，sac.py:L184-188），配独立 Adam（sac.py:L193）。传 float 则退化为常量 `ent_coef_tensor`（sac.py:L198）。

**train()（sac.py:L205-305）**：入口把三个 optimizer 的学习率按 schedule 对齐（sac.py:L209-214），随后 `for gradient_step in range(gradient_steps)`（sac.py:L219）进入主循环，逐段执行数据流的四步。

## 外部连接

- **上游**：`OffPolicyAlgorithm.learn()` 主循环（common/off_policy_algorithm.py:L346-367）每轮 `collect_rollouts()` 存 transition（`_store_transition`，off_policy_algorithm.py:L595），再解析 `gradient_steps`（-1 表示"更新次数=本轮采集步数"，off_policy_algorithm.py:L363-364）并调用 `self.train(...)`（off_policy_algorithm.py:L366）。
- **网络侧**：actor 采样与 log_prob 来自 `Actor.action_log_prob`（sac/policies.py:L172-175），分布是 `SquashedDiagGaussianDistribution`（sac/policies.py:L101）；`polyak_update` 来自 common/utils.py:L530（docstring 明确 tau=1 即硬拷贝）。
- **缓冲侧**：`ReplayBuffer.sample`（common/buffers.py:L285-305）均匀采样并在读出时屏蔽 timeout 截断的 done（buffers.py:L320-322），使截断处正确 bootstrap。
- **下游**：五项日志（sac.py:L300-305），`train/ent_coef` 是判断训练健康的关键曲线。

## 数据流

一个 gradient step 内的严格顺序（顺序本身就是语义）：

1. **采样**：`replay_buffer.sample(batch_size)`（sac.py:L221）；启用 NStepReplayBuffer 时还带 `discounts`（sac.py:L222-223，n-step 折扣 γⁿ 由 buffers.py:L926/L953 预计算）。
2. **actor 重采样**：当前 actor 对 replay 旧状态重新出动作 `actions_pi, log_prob`（sac.py:L230-231）——重参数化采样（reparameterization trick），梯度穿过采样噪声直达网络参数；gSDE 模式下每次梯度步先 `reset_noise()`（sac.py:L226-227），因为上一步优化刚改过 `log_std`。
3. **alpha 步**：`ent_coef = exp(log_ent_coef.detach())`（sac.py:L238）——detach 是关键，alpha 对其余损失是常数；`ent_coef_loss = -(log_ent_coef * (log_prob + target_entropy).detach()).mean()`（sac.py:L240，注释 L235-237 引 softlearning #60），梯度方向 = `H(π) - target_entropy`：熵不足则升 alpha，熵过剩则降。先于 critic 更新执行（sac.py:L249-252）。
4. **critic 步**：`th.no_grad()` 块（sac.py:L254）内算 TD 目标——actor 对 `next_observations` 出动作，喂给**两个 critic_target**，cat 后取 min（sac.py:L258-259），减熵项 `ent_coef * next_log_prob`（sac.py:L261），组装 `target_q_values = rewards + (1-dones) * discounts * next_q_values`（sac.py:L263）。两个在线 critic 各自对 replay 中的**旧动作**算 MSE，`critic_loss = 0.5 * sum(...)`（sac.py:L267-270），单独优化（sac.py:L275-277）。
5. **actor 步**：用第 2 步的 `actions_pi` 喂**在线** critic（非 target），取 min 得 `min_qf_pi`（sac.py:L282-283），`actor_loss = (ent_coef * log_prob - min_qf_pi).mean()`（sac.py:L284）——最大化 Q 同时最大化熵。actor 的 backward（sac.py:L289）会把梯度写进 critic 参数，但下一轮 `critic.optimizer.zero_grad()`（sac.py:L275）先于 critic.step 清场，不会污染。
6. **polyak**：`gradient_step % target_update_interval == 0` 时对 critic→critic_target 做 τ 插值（sac.py:L293-294），batch norm running stats 以 tau=1.0 硬拷贝（sac.py:L295-296）。

## 设计决策

**1. alpha 用 log 空间 + detach 的 "entropic fallback" 结构**。SB3 默认 `ent_coef="auto"`，理由在 docstring：固定 ent_coef "equivalent to inverse of reward scale in the original SAC paper"（sac.py:L60-61）——v1 论文要为每个环境手调 reward scale，工程上不可扩展，v2 对偶优化把它自动化。优化 `log_ent_coef` 而非 α 本身（注释 sac.py:L190-191 引 softlearning #37）既保证 α>0，又让更新天然乘法性、对 α 数量级不敏感。批判地看：这是一阶滞后的交替优化——alpha 用的是上一步策略样本算熵（L240 的 log_prob 被 detach），且塌缩风险真实存在：Q 被过度优化时策略迅速变尖，alpha 追不上或被对偶压力压向 0，日志里 `train/ent_coef`（sac.py:L301）单调滑向 0 就是信号，此时可显式传固定 `ent_coef=0.2` 或调低 `target_entropy` 兜底。fallback 的另一半是常量路径 `ent_coef_tensor`（sac.py:L198）：同一份代码两条路径，差异只在有无 `ent_coef_optimizer`。

**2. `target_update_interval` 与 tau 的双旋钮 polyak 节拍**。默认 interval=1、tau=0.005，即每个 gradient step 做一次 0.5% 插值（sac.py:L293-294）。调大 interval 而不动 tau，等效目标网络时间常数拉长 interval 倍（有效刷新率 τ/interval）——SB3 把两个旋钮独立暴露，不像某些实现联动保持速率不变，这是易踩的坑。更隐蔽的是计数语义：`gradient_step` 是 `train()` 调用内的局部变量（sac.py:L219），跨调用不累计——若 `gradient_steps=1` 且 interval=2，每次调用 gradient_step 恒为 0，`0 % 2 == 0` 恒真，target **每次都更新**，"每 2 步一更"的直觉落空。batch norm 统计另走 tau=1.0 硬拷贝（sac.py:L295-296，GH #996）：running mean/var 本身已是滑动平均，再做 polyak 会双重平滑、语义错误——"统一接口"与"参数正确性"冲突时 SB3 选了正确性。

**3. 双 Q 取 min 的悲观下界**。TD 目标与 actor loss 都取两个 critic 的 min（sac.py:L259、L283），即 Clipped Double Q（源自 TD3）：取 min 系统性压低价值估计，抑制 Q-learning 的正偏差爆炸。代价是反向的低估偏差——min 天然偏向更悲观的网络，若两网络差距大，actor 会追着较差的 critic 跑。SB3 不提供 mean/min 开关，等于替用户锁定了这个权衡。

**4. tanh squashing 修正与 Box-only 限制**。actor 输出经 tanh 压到 [-1,1]（`unscale_action` 再映射回环境边界，common/policies.py:L402），但 tanh 是非线性变量替换，log_prob 必须加修正：`log_prob -= Σ log(1 - tanh(x)² + eps)`（common/distributions.py:L577，公式在 L665-667）。squash 也使解析熵不存在（distributions.py:L580-584 返回 None）——这正是 alpha 自动调节更必要的深层原因，熵只能靠 `-log_prob` 数值估计。squashing 架构同时决定了 `supported_action_spaces=(spaces.Box,)`（sac.py:L150）：离散动作的 SAC 需要类别分布上的熵目标，本实现不支持。

## 新人提示

- **连续动作专用**；离散任务换 DQN 或 sb3-contrib。
- `learning_starts=100` 默认值对多数任务太小（RL Zoo 常用 10000）：先让随机策略填 buffer 能显著改善早期稳定性。
- 盯两条曲线：`train/ent_coef`（sac.py:L301）塌向 0 见设计决策 1；`train/critic_loss` 持续增长且 actor 不动，多半是 reward scale 失配或 target_entropy 过高（默认 `-dim(A)`，sac.py:L172-174，可传如 `-dim(A)/2` 的 float 降温）。
- 内存账：1e6 buffer 存 obs+next_obs 双份 float32，图像任务很快爆 RAM；`optimize_memory_usage=True`（sac.py:L53-55）省一份但引入指针回绕复杂度。n-step return 直接由 `n_steps` 参数开启（sac.py:L56-59），自动换入 NStepReplayBuffer。
- 存档结构特殊：actor/critic/critic_target 别名被排除出 pickle（sac.py:L325-326），`log_ent_coef` 与 alpha optimizer 单独按 torch state_dict 存取（sac.py:L328-335）——自定义保存/加载时要记得这三类。
- 与 PPO 对照读收益最大：单网络单 optimizer 单损失（ppo.py:L256）vs 三网络两 optimizer 四段循环（sac.py:L209/L219-296），正是 on-policy 简单性与 off-policy 样本效率的两个极端。

> 元数据：字符数（不计空格）4598 ｜ 行号锚：引用 74 次、去重 64 处（sac.py 为主，交叉 sac/policies.py、common/{buffers,distributions,policies,utils,off_policy_algorithm}.py）｜ 源码 stable_baselines3/sac/sac.py@master(b2878f4) ｜ 撰写 2026-10-14
