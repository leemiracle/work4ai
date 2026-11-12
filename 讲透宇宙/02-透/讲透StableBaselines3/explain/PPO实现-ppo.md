# PPO 实现：ppo.py——PPO-Clip 目标的最小正确实现

## 角色定位

`stable_baselines3/ppo/ppo.py` 全文 319 行，只做一件事：把 PPO-Clip 论文（Schulman et al., 2017，见 ppo.py:L22）的代理目标翻译成 PyTorch 代码。`class PPO(OnPolicyAlgorithm)`（ppo.py:L18）本身不采集数据、不建网络——rollout 在基类 `collect_rollouts()`（common/on_policy_algorithm.py:L162），策略网络由基类创建（`ActorCriticPolicy` 及 CNN/MultiInput 变体，注册于 ppo.py:L74-78）。文件真正拥有的只有超参声明（ppo.py:L80-108）与 `train()`（ppo.py:L184-300）。`learn()`（ppo.py:L302-318）纯转发给基类。读懂论文公式后来这个文件可一一对应找到落地代码；RL 工程胶水都在两个基类里。它支持全部四类动作空间（ppo.py:L130-135），因为 PPO-Clip 目标只依赖 `log_prob` 比值，天然与动作空间解耦——离散动作只需在 ppo.py:L209-211 把 float 转 long 索引。

## 内部结构

**构造与防御检查（ppo.py:L80-171）**：默认值即 Benchmark 推荐值——`n_steps=2048`、`batch_size=64`、`n_epochs=10`、`clip_range=0.2`（ppo.py:L85-90）、`ent_coef=0.0`、`vf_coef=0.5`、`max_grad_norm=0.5`（ppo.py:L93-95）、`target_kl=None`（ppo.py:L100，默认不做 KL 早停）。构造期三道防线：`batch_size > 1`（ppo.py:L140-143，单样本优势归一化 std=0 产生 NaN，GH #440）；`n_steps * n_envs > 1`（ppo.py:L148-151，同理）；buffer 大小不被 batch_size 整除时 warning 提示截断 minibatch（ppo.py:L153-162）。

**调度器（ppo.py:L173-182）**：`_setup_model()` 把 `clip_range` 包成 `FloatSchedule`（ppo.py:L177，实现见 common/utils.py:L80）——接受常数或 `progress_remaining` 的函数，使 clip 区间可随训练进度退火；`clip_range_vf` 同理但默认 None。

**train() 双层循环（ppo.py:L184-300）**：外层 `for epoch in range(self.n_epochs)`（ppo.py:L204），内层 `for rollout_data in self.rollout_buffer.get(self.batch_size)`（ppo.py:L207）——`get()` 是生成器，每次产出一个洗牌 minibatch。每个 minibatch 的顺序：`evaluate_actions`（ppo.py:L213，定义在 common/policies.py:L719）拿到新策略下的 `values/log_prob/entropy` → 逐 minibatch 归一化优势（ppo.py:L216-219）→ 算三项损失 → 合并（ppo.py:L256）→ `zero_grad/backward/clip_grad_norm_/step`（ppo.py:L274-278）。actor 与 critic 共用一个 optimizer、一次 backward——这是与 SAC 三优化器架构（sac.py:L209-211）的根本差异，也是 `vf_coef` 存在的原因。

## 外部连接

- **上游**：`OnPolicyAlgorithm.collect_rollouts()` 填满 `RolloutBuffer` 后调用本 `train()`；`explained_variance`（ppo.py:L284）与 `FloatSchedule` 来自 common/utils.py:L49/L80。
- **下游**：9 项训练日志（ppo.py:L287-300），其中 `train/clip_fraction`、`train/approx_kl`、`train/explained_variance` 是调参时最常盯的三个。
- **生态位**：A2C（a2c/a2c.py，同一基类）是它的退化版（n_epochs=1、无 ratio、无 clip）；sb3-contrib 的 `MaskablePPO` 通过替换 buffer 与损失掩码继承本实现结构。

## 数据流

必须连同 buffer 协议一起读。此处有一处**命名勘误**：任务描述中的 "sample_batches" 与 "last_episode_starts" 在本代码库的真实名字分别是 `RolloutBuffer.get()` 与 `episode_starts`。

1. **写入侧**：`collect_rollouts()` 每步把 `(obs, action, reward, episode_start, value, log_prob)` 六元组 `add()` 进 buffer（common/on_policy_algorithm.py:L247-254）。注意传的是 `self._last_episode_starts`（on_policy_algorithm.py:L251）——上一时刻的 done——之后才更新 `_last_episode_starts = dones`（on_policy_algorithm.py:L256）。所以 buffer 字段语义是"本条样本是否是新 episode 的第一条"，而非"本条是否终止"。timeout 截断会在奖励上 bootstrap（on_policy_algorithm.py:L236-245，`rewards += gamma * V(terminal_obs)`），避免把 TimeLimit 误当真 terminal。
2. **GAE 侧**：`compute_returns_and_advantage()`（common/on_policy_algorithm.py:L262 调用，实现在 common/buffers.py:L403-438）倒序递推 `delta_t = r + gamma * V(t+1) * next_non_terminal - V(t)`（buffers.py:L433），其中 `next_non_terminal = 1 - episode_starts[step+1]`（buffers.py:L431）——上一条协议在这里被消费；`returns = advantages + values`（buffers.py:L438），即 value loss 的回归目标 `rollout_data.returns`（ppo.py:L244）。
3. **读出侧**：`RolloutBuffer.get()`（common/buffers.py:L481-506）断言 buffer 已满（buffers.py:L482），对 `buffer_size * n_envs` 做随机排列（buffers.py:L483），惰性 `swap_and_flatten`（buffers.py:L485-497），按 batch_size 切片 yield（buffers.py:L503-506）。关键点：`get()` 在**每个 epoch 被重新调用**（ppo.py:L207 位于 epoch 循环内），每次执行新的 `np.random.permutation`（buffers.py:L483），而 flatten 只做一次（buffers.py:L485-497 由 `generator_ready` 把守）——各 epoch 的 minibatch 组成互不相同。
4. **用后即弃**：`train()` 结束后 buffer 不清，等下一轮 `collect_rollouts()` 开头 `reset()`（on_policy_algorithm.py:L187）——on-policy 数据单次更新后即失效，这正是 ratio 修正存在的原因。

## 设计决策

**1. 为什么默认不做 KL 早停、且即便启用也只停在 minibatch 粒度**。`target_kl` 默认 None（ppo.py:L100）。启用后（ppo.py:L267-271），每个 minibatch 用 k3 估计器 `mean((exp(log_ratio)-1) - log_ratio)`（ppo.py:L262-264，Schulman blog 近似，逐样本非负）估计 `D_KL(π_old‖π_new)`（代码注释称 reverse KL，出处链 ppo.py:L258-261 指向 issue #417/PR #419）；超过 `1.5 * target_kl` 即 break——检查在 optimizer.step()（ppo.py:L274-278）之前，**违规的那个 minibatch 不更新参数**，然后经 ppo.py:L281-282 熔断整个 epoch 循环。批判地看：这不是自适应 PPO，而是逃生舱——SB3 的立场（docstring ppo.py:L58-61 引 issue #213）是 clip 本身已约束更新幅度，KL 检查只防御超参配错导致的策略坍塌。代价：早停让各 epoch 实际步数不等，破坏 `n_epochs` 语义，且停止时机依赖 minibatch 洗牌顺序，因此默认关闭。

**2. 优势归一化在 minibatch 内而非整个 buffer 上做**。ppo.py:L216-219 对每个 minibatch 独立 `(A - mean)/(std + 1e-8)`。统计上更干净的做法是整个 rollout 归一化一次，但 SB3 选择与 OpenAI baseline 对齐（ppo.py:L219 的 1e-8 防 NaN）。后果是隐性耦合：更新幅度实际由 `batch_size` 决定——batch 越小，minibatch 方差估计越噪，等效学习率越高，这也是 ppo.py:L140-143 与 L35-36 反复强调 batch_size>1 的根因。调参时改 batch_size 引起性能剧变，先怀疑这里。

**3. value clipping 默认关闭且"依赖 reward scale"**。ppo.py:L234-242 实现 OpenAI 版 `values_pred = old_values + clamp(values - old_values, ±clip_range_vf)`（注释 ppo.py:L238-239 自承 depends on reward scaling）。奖励量纲一变 clip 区间就失义——这是继承的历史包袱，SB3 保留兼容但默认走朴素 MSE（ppo.py:L244）。

**4. 熵奖励的近似回退**。`ent_coef` 默认 0（ppo.py:L93）；启用 gSDE 时分布被 tanh squash，解析熵不可得（`entropy()` 对 bijector 情形返回 None），于是 ppo.py:L248-251 退回 `-mean(-log_prob)` 近似——对 squashed 分布是有偏估计，这是 PPO+gSDE 组合的已知理论债。

## 新人提示

- **先看日志再调参**：`train/clip_fraction`（ppo.py:L231）健康区间约 0.1-0.4，长期接近 1 说明 lr 过大或 clip_range 过小；`train/explained_variance` 接近 1 说明 critic 拟合良好，小于 0 还不如直接用 returns 均值（ppo.py:L284-293）。`train/policy_gradient_loss` 带负号（ppo.py:L227），趋势向上是正常的。
- 超参从 RL Zoo 的 tuned 配方起步，别从默认值起步调 MuJoCo。
- 想让 `clip_range` 退火：传 lambda，如 `clip_range=lambda p: 0.2 * p`，`p` 是剩余进度（1→0），由 ppo.py:L193 的 `self._current_progress_remaining` 驱动。
- 读代码时别在本文件找 GAE——在 common/buffers.py:L403；也别找网络定义——在 common/policies.py。本文件与论文公式的对应只有 ppo.py:L222（ratio）、L225-227（clip loss）、L244（value loss）、L248-252（entropy bonus）四段。

> 元数据：字符数（不计空格）4491 ｜ 行号锚：引用 69 次、去重 61 处（ppo.py 为主，交叉 common/buffers.py、common/on_policy_algorithm.py、common/policies.py、common/utils.py、sac.py）｜ 源码 stable_baselines3/ppo/ppo.py@master(b2878f4) ｜ 撰写 2026-10-14
