# TD3 实现：三项修正如何压进 55 行 train() —— stable_baselines3/td3/td3.py 精讲

> 源码：`stable_baselines3/td3/td3.py`（245 行）· 论文：Fujimoto et al., *Addressing Function Approximation Error in Actor-Critic Methods*（arXiv:1802.09477）

## 角色定位

这个文件是 SB3 中 TD3（Twin Delayed DDPG）的**算法编排层**，不是网络定义层——四个网络的构造在 `td3/policies.py` 的 `TD3Policy` 里，本文件只做三件事：收拢超参（td3.py:L83-136）、建网后摘别名（td3.py:L145-158）、把论文的三项修正逐行落进 `train()`（td3.py:L160-219），算法真身只有其中约 55 行。

继承树上它处于中间层：向上继承 `OffPolicyAlgorithm`，拿到 replay buffer 管理、`train_freq`/`gradient_steps` 调度、`collect_rollouts` 等全部 off-policy 设施；向下被 `DDPG` 继承（ddpg.py:L14）——SB3 刻意选择"DDPG 是 TD3 关掉三件套的特例"这一方向（ddpg.py:L22 明言 "we treat DDPG as a special case of its successor TD3"），本文件因此是两条算法的公共真身，这约束深刻影响了 `train()` 的写法（见设计决策）。

## 内部结构

**构造层**：`__init__`（td3.py:L83）的参数表几乎全量透传基类，TD3 专属的只有三个超参，默认值来自论文：`policy_delay=2`（td3.py:L100）、`target_policy_noise=0.2`（td3.py:L101）、`target_noise_clip=0.5`（td3.py:L102）。两个声明式约束值得注意：`sde_support=False`（td3.py:L133）表明确定性策略无分布可采样；`supported_action_spaces=(spaces.Box,)`（td3.py:L134）把离散动作空间挡在构造期而非训练期。

**别名层**：`_setup_model`（td3.py:L145）建网后，`_create_aliases`（td3.py:L154-158）把 `policy.actor` 等四个引用提为实例属性（`self.actor` 即 `self.policy.actor`）。同函数还按 `"running_"` 前缀筛出 batch norm 的 running statistics（td3.py:L149-152），为后文 `tau=1.0` 的特殊更新埋点。

**训练层**：`train()`（td3.py:L160）分四块——`th.no_grad()` 包裹的 TD target 计算（td3.py:L175-184）、critic 更新（td3.py:L186-197）、`policy_delay` 门控的 actor 更新（td3.py:L199-208）、同被门控的四次 `polyak_update`（td3.py:L210-214）。`learn`（td3.py:L221）与存盘排除（td3.py:L239-244）是薄透传。

## 外部连接

- **buffer 侧**：td3.py:L171 调 `replay_buffer.sample(batch_size, env=...)`；L172-173 的 `discounts` 是 n-step 注入点——普通 ReplayBuffer 返回 `None` 时回落 `self.gamma`，`NStepReplayBuffer` 返回按有效步数折算的 $\gamma^n$。
- **torch 工具侧**：`polyak_update` 来自 common/utils.py:L530，原地 `mul_(1-tau)` 加 `th.add(..., alpha=tau, out=...)`，不建计算图。`q1_forward` 来自 common/policies.py:L979；`ContinuousCritic`（common/policies.py:L912）把 `n_critics` 个 Q 网络放进同一个 optimizer，故 td3.py:L165 只列两项。
- **策略侧**：`TD3Policy` 默认 `n_critics=2`（td3/policies.py:L126）；`actor_target` 建网时 `load_state_dict` 硬拷初值（td3/policies.py:L176-178）。关键细节：`Actor.forward` 输出未经截断的原始 $\mu$（td3/policies.py:L75-78）。
- **下游**：DDPG 不重写 `train()`，仅靠构造参数退化（ddpg.py:L107-115）；logger 在 td3.py:L216-219 记录三项指标。

## 数据流

一次 `train(gradient_steps, batch_size)` 的走线：

1. `set_training_mode(True)`（td3.py:L162）切换 batch norm；按 lr schedule 同步两个 optimizer（td3.py:L165）。
2. 每个 gradient step：`_n_updates += 1`（td3.py:L169，实例级持久计数器）→ buffer 采样（td3.py:L171）。
3. **target 块**（td3.py:L175-184，全程 no_grad）：`replay_data.actions.clone().data.normal_(0, 0.2)` 造平滑噪声并钳 $\pm 0.5$（L177-178）；target actor 输出加噪后整体 `clamp(-1, 1)` 得 `next_actions`（L179）；双 target critic 前向、`th.cat` 后沿 critic 维取 `min`（L182-183）；合成 TD target $y = r + (1-d)\gamma\min_{i=1,2}Q'_i(s',a')$（L184）。
4. **critic 更新**：主 critic 前向得两个 $Q_i(s,a)$（td3.py:L187），损失为两个 MSE 之和（td3.py:L190），单 optimizer 一步（td3.py:L195-197）。
5. **延迟门**：`_n_updates % policy_delay == 0`（td3.py:L200）时更新 actor——损失 $-\mathbb{E}[Q_1(s,\mu_\theta(s))]$ 只用第一个 critic（td3.py:L202）；随后四次 polyak：critic、actor 各一次 `tau=0.005` 软更新（td3.py:L210-211），加两组 batch norm stats 的 `tau=1.0` 硬拷贝（td3.py:L213-214）。

节拍不对称：critic 每 gradient step 更新，actor 与全部 target 网络每 2 步一次。

## 设计决策

**1. 噪声复用动作张量与三层钳位的隐含假设。** td3.py:L177 用 `actions.clone().data.normal_()` 而非 `th.randn`：`clone()` 防 buffer 数据被原地污染，`.data` 脱图（no_grad 内属冗余防御）。噪声先钳 $\pm 0.5$ 再随动作整体钳 $[-1,1]$（L178-179）。批判三点：其一，$0.5=2.5\sigma$，高斯仅约 1.2% 尾部被截，clip 的作用是**限制最坏偏移**而非塑造分布——新人常误当它是分布参数；其二，外层 `clamp(-1,1)` 隐含动作空间已归一化，而 `Actor.forward` 本身不截断（td3/policies.py:L75-78），Box 上下界非 $[-1,1]$ 的环境会静默拿到错误动作；其三，平滑噪声与 min 都只在 target 侧，两项修正收益耦合，消融难归因。

**2. 无分支的 min 与 DDPG 特例化路径。** `th.cat + th.min(dim=1)`（td3.py:L182-183）在 `n_critics=1` 时数学上退化为恒等——DDPG 复用同一 `train()` 无需任何分支。代价是 min 天然保守：它压 overestimation 的机制恰是宁可低估，论文认为确定性策略对高估的利用是非对称的，代价因此可接受。DDPG 的退化（ddpg.py:L105-115）用三个不对称开关：`policy_delay=1` 拆延迟、`target_noise_clip=0.0` 靠钳位把噪声归零（却仍传 `target_policy_noise=0.1`，注释自述"避免报错"——实测当前 PyTorch `normal_(0,0)` 返回全零不报错，属历史防御）、`n_critics=1` 在建网层拆双 critic。批判：这让"DDPG = TD3 − 三件套"成为可执行事实，但三个开关分落两处文件、三种机制（计数、钳位、建网参数），须交叉阅读才能拼出完整语义——以复用率换可读性。

**3. 延迟罩住的是 actor + 全部 target 整体。** td3.py:L200 的 if 块同时覆盖 actor 梯度步与四次 polyak（L210-214）——target 跟 actor 一起每 2 步动，是论文 Algorithm 1 原设计：critic target 若高频漂移，价值估计的抖动会直接灌进低频追逐它的策略梯度。动机上，critic 需高频追新数据，actor 太快会 premature 地利用 critic 的残差高估——这正是论文标题里的 function approximation error。反面：`_n_updates` 跨 `train()` 调用持久累计，中途改 `gradient_steps`/`train_freq` 会让 actor 更新的环境步间隔漂移，长跑实验里是隐性变量。batch norm stats 用 `tau=1.0` 硬拷贝（L213-214）而非软平均，因 running mean/var 不是可学习参数、对其做指数滑动没有统计意义（GH issue #996）。

## 新人提示

- **两套噪声别混淆**：`target_policy_noise` 只进 TD target（td3.py:L177），是正则化；探索噪声是 `action_noise`，由基类在环境采样时注入，与本文件无关。
- 默认值（0.2 / ±0.5 / 2 / tau=0.005）是论文推荐值；发散时先查动作空间归一化与共用 lr=1e-3，再动三件套。
- `train/n_updates`（td3.py:L216）计的是 **gradient step** 不是环境步，对照 ep_rew_mean 时记得换算。
- actor 损失只用 $Q_1$（td3.py:L202）不是 min——策略上升方向不需保守估计，是论文设计而非笔误。
- 存盘时四个别名被显式排除（td3.py:L240），权重真身在 `policy` 里随其序列化；另存 `actor.state_dict()` 会与加载路径错配。
- 读 TD3 建议按 `train()`（td3.py:L160）→ `TD3Policy`（td3/policies.py）→ `ContinuousCritic`（common/policies.py:L912）横跳；只看本文件会漏掉"actor 输出从未被截断"这类关键事实。

---
> 元数据：字数（不计空格）4771 | 行号锚 54 处（td3.py 为主，交叉 ddpg.py / td3/policies.py / common/policies.py / common/utils.py，另含裸 L 引用若干）| 六节自查：角色定位✓ 内部结构✓ 外部连接✓ 数据流✓ 设计决策（3 组批判性权衡）✓ 新人提示✓ | 源码基线 commit b2878f4
