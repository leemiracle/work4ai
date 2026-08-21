# cleanrl 核心文件精讲（1/3）：核心算法 PyTorch 栈

> 覆盖 13 个核心算法脚本 + 2 个官方文档，共 15 文件。讲解顺序：on-policy 家族（PPO×4）→ value-based 家族（DQN/C51/Rainbow）→ off-policy 连续控制（DDPG/TD3/SAC/RPO）→ 高级混合（PQN）→ 文档。
> 元数据来源：`.understand-anything/knowledge-graph.json`（487 节点/1052 边，13 个算法脚本全部位于 `layer:core-algorithms 核心算法脚本层`）；行号锚点全部对源码实测。

**阅读前提：CleanRL 的"单文件哲学"**。每个算法 = 一个自包含脚本，从命令行参数到训练循环全部在一个 `.py` 里，复制即改。全库共享的骨架是五段式：`Args dataclass（tyro CLI）→ make_env 闭包 → 网络定义 → 存储预分配 → if __name__ == "__main__" 训练主循环`。理解了 `ppo.py` 这一个，其余 12 个都是"在同一骨架上做差分"。单文件原则有两个公认的例外：`cleanrl_utils/buffers.py`（ReplayBuffer）和 `cleanrl_utils/atari_wrappers.py`（Atari 预处理栈），被 off-policy/Atari 脚本 import——用两处可控共享换取避免每个文件膨胀 300 行。所有脚本用 `# TRY NOT TO MODIFY` 注释标出跨算法一致的环境交互样板，用 `# ALGO LOGIC` 标出算法差异点——这是 CleanRL 给读者的"导览系统"。

---

## cleanrl/ppo.py

**知识图谱**：`file:cleanrl/ppo.py`，complexity=complex，tags=[reinforcement-learning, ppo, entry-point, single-file, training-script, tested]。图谱 summary 称其为"全库其余 PPO 变体的参考模板"；入边显示它被 `tests/test_classic_control.py`、`tuner_example.py`、benchmark 脚本、Dockerfile、7 个文档页引用——是全库被依赖最多的脚本。

### 架构角色

`ppo.py` 是整个 CleanRL 的" Hello World"与母版：CartPole 级离散动作环境上的 PPO，312 行，无任何外部算法依赖（连 `cleanrl_utils` 都不用）。它教的不是 PPO 的高级用法，而是**PPO 的最小完备实现**——包含 openai/baselines 的全部 13 条核心 code-level 优化（正交初始化、Adam eps、lr 退火、GAE、minibatch、优势归一化、clip surrogate、value clip、熵奖金、全局梯度裁剪、调试变量、分离 MLP、向量化环境）。官方文档 `docs/rl-algorithms/ppo.md` 明确说所有 PPO 变体"augmented with the same code-level optimizations"，指的就是这份母版里的细节。后面每个变体都只讲"与它的差异"。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L17-78 | 通用实验参数（exp_name/seed/cuda/track/capture_video，L17-34）+ 算法超参（L36-70）+ 运行时填充占位（L72-78） |
| ② make_env | L81-91 | 返回 thunk 闭包；`idx==0` 才挂 RecordVideo；统一挂 RecordEpisodeStatistics |
| ③ Agent | L94-126 | `layer_init`（L94-97，正交初始化）+ Actor/Critic 分离双头 MLP |
| ④ 缓冲 | L171-176 | 预分配 `(num_steps, num_envs, …)` 六张量：obs/actions/logprobs/rewards/dones/values |
| ⑤ 训练循环 | L129-312 | tyro 解析→wandb/SummaryWriter→seed→SyncVectorEnv→rollout(L192-215)→GAE(L217-231)→flatten(L233-239)→minibatch 更新(L241-293)→日志(L295-309) |

几个非显然的细节：`Args` 里 `batch_size/minibatch_size/num_iterations` 默认 0，在 L131-133 由 `num_envs×num_steps` 推导——tyro 会把这些也暴露成 CLI 参数但运行时覆盖；`layer_init` 默认 `std=√2`（隐藏层），Actor 输出头显式传 `std=0.01`（L115，输出小 logits≈近均匀初始策略）、Critic 输出头 `std=1.0`（L108）；优化器是 `Adam(lr=2.5e-4, eps=1e-5)`（L168），小 eps 是 baselines 的"实现细节#3"。

### 算法要点

**（1）GAE（L217-231）**：先算 TD 残差再反向递推：

$$\delta_t = r_t + \gamma V(s_{t+1})(1-\text{done}_{t+1}) - V(s_t),\qquad \hat A_t = \delta_t + \gamma\lambda(1-\text{done}_{t+1})\,\hat A_{t+1}$$

代码对 `t` 倒序循环（L222），`lastgaelam` 滚动累积；序列末尾（t == num_steps-1）用 `next_value` bootstrap（L219、L223-225），`nextnonterminal = 1 - next_done` 把 termination 和 truncation 一视同仁地切断价值传播。`returns = advantages + values`（L231）回收 V 得回报目标。

**（2）PPO-clip 策略损失（L250-267）**：

$$L^{CLIP} = \mathbb{E}\big[\max(-\hat A\,r_t,\; -\hat A\,\mathrm{clip}(r_t, 1-\epsilon, 1+\epsilon))\big],\qquad r_t = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$$

`logprobs` 在 rollout 时以 `no_grad` 记录（L199-202）充当 θ_old；`get_action_and_value` 接受旧 action 重算新 logprob（L121-126 同一函数两用——采样与评估）。

**（3） clipped value loss（L271-280）**：$L^V = \frac12\mathbb{E}[\max((V-R)^2,\;(V_{clip}-R)^2)]$，其中 $V_{clip} = V_{old} + \mathrm{clip}(V - V_{old}, -\epsilon, +\epsilon)$。防止 value 头在多 epoch 下朝回报目标猛冲（PPO 论文附录的实现细节）。

**（4）诊断量（L254-258）**：k3 近似 KL $=\mathbb{E}[(r-1)-\log r]$（非负、低方差，链接 joschu 博客）；clipfrac = 越界比例；`target_kl` 提前终止 epoch（L292-293）。总损失 `loss = pg_loss - ent_coef·entropy + vf_coef·v_loss`（L285），全局梯度裁剪 0.5（L289）。

**（5）优势归一化按 minibatch（L261-262）**：`(mb_advantages - mean)/(std + 1e-8)` 在每个 minibatch 内归一化——与 baselines 的 batch 级归一化不同，是 CleanRL 的一个已知偏差点。

### 与其他变体的差异

- vs `ppo_atari.py`：MLP→共享 CNN；clip 0.2→0.1；num_envs 4→8；无 Atari wrapper、无 /255 归一化；500k→10M 步。
- vs `ppo_continuous_action.py`：Categorical→Normal（可学习 logstd）；无观测/奖励归一化 wrapper；ent_coef 0.01 vs 0.0；无 save_model 段。
- 本文件独有：它是唯一零 `cleanrl_utils` 依赖的 PPO 变体（图谱 OUT 边只有 contains/exports/tested_by）。

### 模式与坑

- **存储语义**：`dones[step] = next_done`（L195）存的是"进入 s_t 之前是否刚结束"，`values[step]` 存的是 $V(s_t)$——GAE 里 `dones[t+1]` 判 $s_{t+1}$ 是否 terminal，索引错一位是手写 PPO 最常见 bug。
- `b_actions.long()`（L250）离散专属 cast；连续版不需要。
- 六张量全部常驻 GPU（`.to(device)`），batch=512 时无所谓，若把 num_steps 调大 100 倍会吃显存。
- `explained_variance = 1 - Var(R-V)/Var(R)`（L295-297）是 value 头健康度最实用的免费指标：接近 1 好，负数说明 value 比均值预测还差。
- rollout 里 `envs.step(action.cpu().numpy())`（L205）每步都有 D2H 同步——SyncVectorEnv 下 GPU 利用率注定不高，这是"清晰优先"的代价。

---

## cleanrl/ppo_atari.py

**知识图谱**：`file:cleanrl/ppo_atari.py`，complexity=complex，tags 含 atari/pytorch/tested。OUT 边 `[imports]->file:cleanrl_utils/atari_wrappers.py`（本组 4 个 PPO 中它与 LSTM 版唯二 import 该库）；被 `tests/test_atari.py` 测试；11 个文档页（含 envpool/multigpu 等衍生 benchmark 页）documents 它。

### 架构角色

PPO 的 Atari 标准变体：教的是"**视觉输入下 PPO 需要什么**"——Nature DQN 三层 CNN 共享主干 + Atari 预处理 wrapper 栈。它是 CleanRL 被引用最多的入门脚本之一（图谱 summary 原话），也是官方 benchmark 覆盖最全的变体（ppo_atari/envpool/envpool_xla_jax/scan/multigpu 全部由它派生）。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L25-86 | 与 ppo.py 完全同构；差异值见下节 |
| ② make_env | L89-108 | thunk + RecordEpisodeStatistics + **7 层 Atari wrapper 栈**（L97-105） |
| ③ Agent | L111-143 | `layer_init`（L111-114）+ 共享 CNN `self.network`（L120-130）+ actor/critic 两个线性头（L131-132） |
| ④ 缓冲 | L188-193 | 同 ppo.py 六张量 |
| ⑤ 训练循环 | L146-329 | 与 ppo.py 逐行同构（GAE L234-248 / 更新 L258-310 与 ppo.py 行号几乎平移） |

Agent 的关键结构：CNN 主干输出 512 维隐向量，actor 头 `Linear(512, n)` std=0.01、critic 头 `Linear(512, 1)` std=1——**共享主干、分离头**，与 ppo.py 的"整网分离"不同。`get_value/get_action_and_value` 都先 `self.network(x / 255.0)`（L135、L138）——把 uint8 像素压到 [0,1] 放在网络内做，保证 eval 复用时不会忘。

### 算法要点

算法数学与 ppo.py 完全一致（GAE/clip/value-clip 公式同上），本文件的新知识全在**环境侧**：

- **Wrapper 栈（L97-105，自内向外套）**：`NoopResetEnv(noop_max=30)` 重置后随机 no-op 1-30 帧去确定性；`MaxAndSkipEnv(skip=4)` 每 4 帧取像素 max 消除 Atari 闪烁、动作重复 4 次；`EpisodicLifeEnv` 把掉命当回合结束（密集化终止信号）；`FireResetEnv` 条件启用——若动作表含 FIRE（如 Breakout 需按 FIRE 发球，L100-101）；`ClipRewardEnv` 奖励压到 {-1,0,1}；`ResizeObservation(84×84)`→`GrayScaleObservation`→`FrameStack(4)`。这套栈 = DQN Nature 论文标准协议，与 CNN 输入通道数 4（L121 `Conv2d(4, 32, 8, 4)`）严格对应。
- **超参差分**：`clip_coef=0.1`（L67，Atari 惯例减半）、`num_envs=8`（L51）、`total_timesteps=10M`（L47）、默认环境 `BreakoutNoFrameskip-v4`（L45，选 NoFrameskip 版是为了让 wrapper 栈全权负责帧处理）。
- `ClipRewardEnv` + `EpisodicLifeEnv` 改变了 GAE 看到的 MDP：回报被压到 ±1 粒度、episode 变短——这就是为什么 value 头和 lr 可以沿用：信号尺度被 wrapper 归一化了。

### 与其他变体的差异

- vs `ppo.py`：唯一差异是 Agent（CNN vs MLP）+ wrapper 栈 + 3 个超参值；训练循环 100% 相同（diff 级验证：GAE 段 L234-248 与 ppo.py L217-231 逐行一致）。
- vs `ppo_atari_lstm.py`：`FrameStack(4)` vs `FrameStack(1)`；`Conv2d(4,..)` vs `Conv2d(1,..)`；无 LSTM 状态管理。
- 图谱独有入边：`docs/rl-algorithms/ppo.md` 与 `overview.md` 都 documents 它，且是 envpool 系列文档的对照基准。

### 模式与坑

- `EpisodicLifeEnv` 下 `RecordEpisodeStatistics` 记录的 episodic_return 是**每命回报**而非整局；整局统计只在真结束时打出来——对照官方数字时容易看错。
- `x / 255.0` 写在网络 forward 里而非 wrapper 里，是刻意选择：让 checkpoint 与环境预处理解耦。
- import 用了 `# isort:skip`（L16）压住 lint 顺序——第三方 wrapper 库排序后会被放到 gym 之前，属工程小痕迹。
- SyncVectorEnv×8 串行跑 8 个 Atari 模拟器，CPU 是瓶颈；要提速的正解是 envpool 变体（本文件是清晰度与速度的交换基准）。

---

## cleanrl/ppo_continuous_action.py

**知识图谱**：`file:cleanrl/ppo_continuous_action.py`，complexity=complex，tags=[continuous-action, mujoco, tested]，被 `tests/test_mujoco.py` 覆盖，OUT 边含 exports（Args/make_env/layer_init/Agent 被 eval 脚本复用）。

### 架构角色

PPO 的 MuJoCo 连续动作变体：教两件事——**高斯策略如何参数化**与**连续控制的环境侧归一化**。文档称其"implemented Mujoco-specific code-level optimizations"（对应 Andrychowicz et al. 2021《What Matters In On-Policy RL》的结论：obs/reward 归一化对 MuJoCo PPO 收益巨大）。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L17-84 | 通用段多出 save_model/upload_model/hf_entity（L35-40）；算法段差异值见下 |
| ② make_env | L87-103 | thunk + **8 层连续控制 wrapper 链**（L94-100），签名多一个 `gamma` |
| ③ Agent | L106-141 | `layer_init` + critic MLP + `actor_mean` MLP + **`actor_logstd` 状态无关可学习参数**（L129） |
| ④ 缓冲 | L186-191 | 同 ppo.py |
| ⑤ 训练循环 | L144-353 | rollout/GAE/更新与 ppo.py 同构（L200-312）；多出 save_model→evaluate→HF 上传段（L326-350） |

### 算法要点

**（1）高斯策略**：$\pi(a|s) = \mathcal N(\mu_\theta(s),\; e^{\sigma})$。μ 由 MLP 输出；σ 不是逐状态网络头，而是 `nn.Parameter(torch.zeros(1, act_dim))`（L129）——**全局共享、随梯度学习**的对数标准差。`get_action_and_value` 里 `expand_as` 广播（L136）。logprob/entropy 都 `.sum(1)`（L141）——多维独立高斯联合密度按维求和。

**（2）环境归一化链（L94-100，注意套用顺序）**：`FlattenObservation`（兼容 dm_control 的 Dict obs）→ `RecordEpisodeStatistics` → `ClipAction`（把网络输出的越界动作截断到合法区间，**策略侧不做 tanh squash**）→ `NormalizeObservation`（运行均值方差归一）→ `TransformObservation(clip ±10)` → `NormalizeReward(gamma)`（折扣回报尺度归一）→ `TransformReward(clip ±10)`。这是 Andrychowicz 2021 的推荐配方，公式上即 $\tilde o = \frac{o-\mu_o}{\sqrt{\sigma_o^2+\varepsilon}},\; \tilde r = \frac{r}{\sqrt{\text{Var}[\sum \gamma^k r_k]}}$，两层 clip 防离群值污染运行统计。

**（3）超参差分**：`num_envs=1, num_steps=2048`（L49-51）→ batch=2048、minibatch=64；`update_epochs=10`（L61）；`ent_coef=0.0`（L69，连续控制不需要熵奖金，σ 本身就是探索旋钮）；`lr=3e-4`；默认 `HalfCheetah-v4`。

**（4）保存评估段（L326-350）**：`save_model` 时把 state_dict 存为 `.cleanrl_model`，再 import `cleanrl_utils.evals.ppo_eval.evaluate` 跑 10 回合无探索评估，可选推 HF Hub——这段是 CleanRL "可复现实验交付物"理念的样板。

### 与其他变体的差异

- vs `ppo.py`：Categorical→Normal；`b_actions` 不 cast long；logprob/entropy 求和；多归一化 wrapper 与 save_model 段；**策略输出不 squash**（靠 ClipAction 截断）——与 SAC 的 tanh 方案形成路线对照。
- vs `rpo_continuous_action.py`：除 Agent 的 `rpo_alpha` 五行差异外逐行相同（详见 RPO 节）。

### 模式与坑

- **σ 参数化的陷阱**：logstd 初始 0（std=1）对 MuJoCo 原始动作尺度（多为 ±1）合理，但若环境动作尺度很大且未归一化，初始策略会过于尖锐/平坦；本实现靠 obs/reward 归一化间接规避。
- `make_env` 签名带 `gamma`（L87）传给 `NormalizeReward`——**换了 gamma 必须换归一化尺度**，复制代码时最容易漏。
- 归一化 wrapper 的运行统计存在环境对象里，`evaluate` 重建环境后统计从零开始——CleanRL 的 ppo_eval 会重建并冻结统计，但自写 eval 时若忘冻结，评估期 obs 分布会漂移。
- `assert isinstance(..., gym.spaces.Box)`（L180）：连续版守门，防止拿它跑离散环境报出难懂的张量错误。

---

## cleanrl/ppo_atari_lstm.py

**知识图谱**：`file:cleanrl/ppo_atari_lstm.py`，complexity=complex，tags=[lstm, recurrent, atari, tested]。图谱 summary 精准点出其两大机制：get_states 按时间步重排序列、done 处隐藏态置零。

### 架构角色

PPO 的记忆变体：教的是**部分可观测（POMDP）下 on-policy 训练的三件难事**——循环状态如何穿越 rollout 与更新两个阶段、episode 边界如何清零、minibatch 如何在保持时间序列完整的前提下切分。它是 4 个 PPO 中对"训练循环骨架"改动最大的一个。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L25-86 | 与 ppo_atari.py 完全一致（clip 0.1/num_envs 8/128 步） |
| ② make_env | L89-108 | 同 Atari 栈，唯一差异 `FrameStack(1)`（L105） |
| ③ Agent | L111-170 | CNN（输入通道 1，L121）→ `nn.LSTM(512,128)`（L131）→ 双头；新增 `get_states`（L140-158） |
| ④ 缓冲 | L215-220 | 六张量 + **dones 必须也 flatten 进 batch**（b_dones L290） |
| ⑤ 训练循环 | L173-375 | rollout 携带 `next_lstm_state`（L228-231 初始化、L248 更新）；**minibatch 按环境分组**（L296-306）；其余同构 |

### 算法要点

**（1）`get_states` 的逐步循环（L140-158）**——本文件的灵魂：

```python
hidden = hidden.reshape((-1, batch_size, self.lstm.input_size))   # L145 (T*B, 512) -> (T, B, 512)
for h, d in zip(hidden, done):                                     # L148 逐时间步
    h, lstm_state = self.lstm(h.unsqueeze(0), (
        (1.0 - d).view(1, -1, 1) * lstm_state[0],                  # L152 done 则 hidden 清零
        (1.0 - d).view(1, -f, 1) * lstm_state[1]))
```

数学上即 $\text{LSTM}$ 状态递推 $(h_t, c_t) = f(x_t, d_t\cdot 0 + (1-d_t)\cdot(h_{t-1}, c_{t-1}))$：$d_t=1$（刚终止）时用零状态进入新回合，否则继承。**不这么做，回合边界的信息会跨回合泄漏，策略会"作弊"**。L157 `torch.flatten(torch.cat(new_hidden), 0, 1)` 把 (T,B,128) 拍回 (T·B,128) 与扁平 batch 对齐。

**（2）rollout 侧状态管理（L228-231、L234）**：`next_lstm_state` 在 envs 维度持有 8 份 (h,c)；每个 iteration 开始 `initial_lstm_state = clone`（L234）——更新阶段重放整段序列时必须从**这段 rollout 的初始状态**出发，而不是当前状态。

**（3）序列保持的 minibatch 切分（L296-306）**：

```python
envsperbatch = num_envs // num_minibatches          # L297
mb_inds = flatinds[:, mbenvinds].ravel()            # L306 先切时间全保留、再挑环境
```

普通 PPO 对 `batch_size` 个 transition 随机打乱；这里必须**按环境整列取**（`flatinds` 是 (num_steps, num_envs) 索引阵），一个 minibatch = 若干环境的完整 128 步序列。`assert num_envs % num_minibatches == 0`（L296）保证整除。更新时把该组环境的初始 LSTM 状态一并取出（L310 `initial_lstm_state[...][:, mbenvinds]`），与 `b_dones[mb_inds]` 一起喂给 `get_action_and_value` 完整重放（L308-313）。

**（4）FrameStack(1) 的含义（L105）**：堆帧是"把历史塞进观测"的暴力记忆；LSTM 版本把记忆责任交还给循环网络，单帧灰度图足以让 CNN 提取瞬时特征——`Conv2d(1, 32, 8, stride=4)`（L121）输入通道从 4 改 1 是与此配套的唯一网络改动。LSTM 自身初始化：bias 全 0、weight 正交 std=1（L132-136）。

### 与其他变体的差异

- vs `ppo_atari.py`：+LSTM 与状态管理；minibatch 切分彻底重写（随机 transition vs 按环境分组）；`get_action_and_value` 返回值多一个 `lstm_state`（L170），签名多 `lstm_state, done` 两参。
- vs `ppo.py/ppo_continuous_action.py`：是四者中唯一"batch 维度语义改变"的变体。

### 模式与坑

- L306 注释 `# be really careful about the index` 是作者自己标的雷区：`flatinds[:, mbenvinds].ravel()` 的顺序必须与 `b_obs[mb_inds]` 的 reshape 顺序一致（时间在外、环境在内），错序不报错但学不动。
- 逐步 for 循环调 LSTM（L148-156）放弃了 cuDNN 融合内核，速度换正确性；向量化做法是把 done-mask 做进 batch 维，但极易写错。
- `get_value` 同样要走 `get_states`（L160-162）——bootstrap 值必须用与 rollout 一致的隐藏态演化，漏掉 done mask 的 value 评估是常见静默 bug。
- target_kl、advantage 归一化、value clip 全部照旧（L317-345）——循环结构改变不改变 PPO 数学。

---

## cleanrl/dqn.py

**知识图谱**：`file:cleanrl/dqn.py`，complexity=complex，tags=[dqn, classic-control, tested]。OUT 边首次出现 `[imports]->file:cleanrl_utils/buffers.py` 与 `[calls]->ReplayBuffer`；还依赖 evals/dqn_eval.py 与 huggingface.py。被 `tests/test_classic_control_gymnasium.py` 覆盖。

### 架构角色

off-policy 世界的 `ppo.py`：**value-based 家族的母版**。它教的范式转换是：从"rollout 一批→多 epoch 更新"（on-policy）换成"**单步交互→存 replay→随机采历史→单步梯度**"（off-policy）。与 PPO 组对照阅读是理解两大范式差异的最快路径——文件骨架相同（Args/make_env/网络/主循环），但循环的时间结构完全不同。

### 文件解剖（标准五段，off-policy 版）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L19-72 | 通用段 + save_model 段；算法段换成 DQN 专属：buffer_size/tau/target_network_frequency/start_e/end_e/exploration_fraction/learning_starts/train_frequency |
| ② make_env | L75-87 | thunk + RecordEpisodeStatistics + `action_space.seed(seed)`（L83，ε-greedy 需要可复现的随机动作源） |
| ③ QNetwork | L91-103 | 120-84 双隐层 MLP，**无 layer_init**（用 PyTorch 默认初始化）；输出 |A| 维 Q 值 |
| ④ 缓冲 | L152-158 | `cleanrl_utils.buffers.ReplayBuffer`（唯一共享模块），`handle_timeout_termination=False` |
| ⑤ 训练循环 | L111-248 | `linear_schedule`（L106-108）+ 逐步 for 循环：ε-greedy 选动作(L165-170)→step→存 buffer(L183-191)→每 train_frequency 步训一次(L194-212)→每 target_network_frequency 步更新目标网(L215-219) |

结构上与 PPO 组的三大不同：**无向量化**（`assert num_envs == 1`，L113，replay 本身就是"并行"的替代品）；**无存储张量预分配**（交给 ReplayBuffer）；**训练频率与交互频率解耦**（train_frequency=10：每 10 个环境步做 1 次梯度）。

### 算法要点

**（1）TD 目标与损失（L196-201）**——整族 value-based 方法的心脏：

$$y = r + \gamma\,(1-\text{done})\max_{a'} Q_{\bar\theta}(s', a'),\qquad L = \text{MSE}\big(Q_\theta(s,a),\; y\big)$$

`target_network` 参数带横线 $\bar\theta$ 表示**梯度阻断**（`with torch.no_grad():` L197）。在线网取值用 `gather(1, actions)`（L200）——按 batch 里实际执行的动作索引 Q 列。

**（2）目标网络更新（L215-219）**：$\bar\theta \leftarrow \tau\theta + (1-\tau)\bar\theta$，本文件 `tau=1.0`（L57）退化为**硬拷贝**，每 500 步执行一次（L59）。这个公式的意义：目标网是"缓慢移动的锚"，防止自举目标跟着在线网一起跑飞（moving target 问题）。

**（3）ε-greedy 线性退火（L106-108、L165-170）**：$\epsilon(t) = \max(\text{slope}\cdot t + \epsilon_0,\ \epsilon_{end})$，从 1.0 线性降到 0.05，用掉总步数的一半（exploration_fraction=0.5）。以 `random.random() < ε` 掷硬币决定随机动作或 argmax Q。

**（4）truncation 修正（L184-188）**：`real_next_obs` 把截断（超时）步的下一观测替换为 `infos["final_observation"]`。原因：gymnasium 向量环境在 truncation 时返回 reset 后的新观测，直接存进 buffer 会把"新回合首帧"当成"上回合尾帧的下一状态"，TD 目标被污染。

### 与其他变体的差异

- vs `ppo.py`：见"架构角色"——这是本组内范式差异最大的对照对。
- vs `dqn_atari.py`：仅网络（MLP→CNN）、wrapper 栈、超参刻度不同；算法行 L196-219 逐行相同。
- 注意 `tau` 的双语义：本文件 tau=1.0=硬更新；DDPG/TD3/SAC 组 tau=0.005=软更新。**同名参数、同一公式、相反用法**。

### 模式与坑

- **tau=1.0 的隐蔽性**：L216-219 写的是软更新公式，但 tau=1 时 `copy_` 直接覆盖——初学者改成 0.005 又不把 `target_network_frequency` 调成 1，目标网几乎永远不动，训练死亡。
- MLP 用 120-84 这种"历史尺寸"（源自早期教程）且不做正交初始化——**DQN 家族不享受 PPO 的 13 条优化**，这是有意的（对齐原始 DQN 论文设定），不是疏忽。
- `learning_starts=10000` 恰等于 buffer_size（L53、L69）：开始训练时 buffer 已满且全是随机策略数据——经典配置但值得知道。
- L190 注释 `# CRUCIAL step easy to overlook`：`obs = next_obs` 忘写会让 buffer 里全是第一步的观测，这种 bug 不报错、只表现为学不动。
- 每步 `data = rb.sample()` 在 GPU 上采 batch 128×10 维张量：小问题无碍，Atari 版本才会感受到瓶颈。

---

## cleanrl/dqn_atari.py

**知识图谱**：`file:cleanrl/dqn_atari.py`，complexity=complex，tags=[dqn, atari, entry-point, tested]。图谱 summary 特别指出：该文件的 QNetwork **被 qdagger 教师蒸馏脚本 import 复用为教师模型**（入边 `qdagger_dqn_atari_impalacnn.py ->[imports]`）——全库少见的"算法脚本被另一个算法脚本当库用"。

### 架构角色

DQN 的"回归原文"版：用 **Nature 2015 论文的 CNN 结构与超参刻度**在 Atari 上复现原始 DQN。它教的是"经典 benchmark 配方长什么样"——网络、预处理、超参三件套全部对齐 2015 年论文，是后来 C51/Rainbow 的对照组。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L26-79 | 与 dqn.py 同名同序；差异值：lr 1e-4、buffer 1e6、batch 32、target 1000、train_freq 4、end_e 0.01、exploration_fraction 0.10、learning_starts 80000 |
| ② make_env | L82-104 | 与 ppo_atari.py 完全相同的 7 层 wrapper 栈（L91-99）+ `action_space.seed` |
| ③ QNetwork | L107-126 | Nature CNN：Conv(4,32,8,4)→Conv(32,64,4,2)→Conv(64,64,3,1)→FC(3136,512)→FC(512,n)；forward 内 `x/255.0`（L125） |
| ④ 缓冲 | L174-181 | ReplayBuffer + **`optimize_memory_usage=True`**（L179） |
| ⑤ 训练循环 | L133-271 | 与 dqn.py 逐行同构（ε-greedy L188-193 / TD L218-235 / 目标网 L238-242） |

### 算法要点

数学与 dqn.py 完全一致（同一条 TD 公式与目标网公式），本文件的增量知识是**刻度与内存工程**：

- **Nature 超参刻度**：1M 转移的 replay、batch 32、每 4 步训一次（train_frequency=4，即 8 帧一次）、目标网每 1000 步硬同步、ε 从 1 线性退到 **0.01**（Atari 惯例比经典控制低 5 倍）且只用总步数 10%、前 80k 步纯随机填充。这些数字不是调出来的，是论文表 1 的直接转录——复现实验的意义就在于此。
- **`optimize_memory_usage=True` 的省显存技巧**：ReplayBuffer 不存 `next_observations`，采样时动态取 `idx+1` 的 obs 充当下一状态（buffer 环形连续时成立）。Atari 观测 84×84×4 uint8 ≈ 28KB/条，1M 条双份 = 56GB → 单份 28GB，**省一半内存**。代价是边界处（环形回绕/回合切断）的正确性依赖 buffer 实现细节，所以经典控制版（内存无压力）不开。
- lr=1e-4（L56）：Nature 用 RMSProp 1e-4，这里换 Adam 同 lr——CleanRL 的实用替换，文档 benchmark 显示不影响结论。

### 与其他变体的差异

- vs `dqn.py`：网络/wrapper/刻度三换，算法零改动（diff 集中在 L107-126 与 Args 默认值）。
- vs `c51.py`：同环境同 MLP 骨架，但输出头从 |A| 维变 |A|×n_atoms 维、损失从 MSE 变交叉熵。
- vs `ppo_atari.py`：**同一环境同一 CNN，两种范式**——PPO 8 envs×128 步批量 rollout，DQN 单 env 逐步+replay；这是本组最有教学价值的并排对照。

### 模式与坑

- `real_next_obs` 修正（L207-210）在 `FrameStack(4)` 下还叠加一层 subtlety：truncation 时 `final_observation` 是完整 4 帧栈的最终态，修正逻辑与经典控制版相同但更难在脑内模拟。
- `EpisodicLifeEnv` + DQN 的组合：done 被密集化，buffer 里大量"假终止"样本把 γ 截断提前——DQN 论文本来就是这套协议，对照学习价值大于性能价值。
- 被 qdagger 复用意味着**改这个文件会破坏另一个算法**——单文件哲学在这里打了个补丁：脚本既是入口又是库。
- `assert num_envs == 1`（L135）：DQN 的 ε-greedy 与 replay 都是单流设计，向量化需要重写动作逻辑，CleanRL 选择不做。

---

## cleanrl/c51.py

**知识图谱**：`file:cleanrl/c51.py`，complexity=complex，tags=[c51, dqn-family, tested]。OUT 边与 dqn.py 同构（buffers/evals/huggingface）；被 `test_classic_control_gymnasium.py` 覆盖。

### 架构角色

**分布强化学习（Distributional RL）的入门实现**：把"估计 Q 值的期望"换成"估计回报 Z(s,a) 的完整离散分布"。C51 = 51/101 个原子（atom）上的分类问题。它教的核心新概念只有一个——**分布贝尔曼目标无法直接表示，必须做"投影"（projection）**。其余一切（replay/ε-greedy/目标网）与 dqn.py 逐字相同。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L18-75 | dqn.py 基础上 +n_atoms=101/v_min=-100/v_max=100（L52-57）；**删掉了 tau**（目标网只有硬更新） |
| ② make_env | L78-90 | 与 dqn.py 相同 |
| ③ QNetwork | L93-116 | MLP 同 dqn.py 但输出 `n × n_atoms` 维（L106）；`register_buffer("atoms", linspace(v_min, v_max, 101))`（L99）；`get_action`（L109-116） |
| ④ 缓冲 | L165-171 | 同 dqn.py |
| ⑤ 训练循环 | L124-279 | ε-greedy/存储与 dqn.py 相同（L178-204）；**训练段换成投影+交叉熵**（L207-242）；目标网 `load_state_dict` 硬同步（L245-246） |

`get_action` 的关键三行（L112-116）：`logits.view(B, n, n_atoms)` → softmax(dim=2) 得每个动作的 PMF → `q_values = (pmfs * self.atoms).sum(2)` 即 $Q(s,a) = \sum_i p_i z_i$（分布的期望），argmax 照旧。选动作用期望、学习用分布——这是 C51 的双面性。

### 算法要点

**（1）分布式贝尔曼算子与投影（L210-227）**——本文件的核心 20 行：

目标分布是把目标网选出的 PMF 经贝尔曼算子变换：每个原子 $z_i \mapsto r + \gamma z_i(1-\text{done})$。但结果位置 $T z_i$ 几乎不会落在原子网格上，必须把概率质量**线性插值拆给相邻两个原子**：

$$b = \frac{\mathrm{clip}(Tz,\ v_{min},\ v_{max}) - v_{min}}{\Delta z},\qquad l = \lfloor b \rfloor,\ u = \lceil b \rceil$$
$$d^l_i = (u + \mathbb{1}[l=u] - b)\,p_i \to z_l,\qquad d^u_i = (b - l)\,p_i \to z_u$$

代码 L214-227：`(l == u).float()` 修正 b 恰为整数时上下原子相同的质量分配（注释 L220-221 给了例子）；`index_add_` 逐样本把质量累加进 `target_pmfs`（L225-227 的 for 循环——batch 内逐条做，牺牲速度换清晰）。

**（2）交叉熵损失（L229-230）**：$\mathcal L = -\mathbb{E}\big[\sum_i \hat p_i(z_i)\,\log p_\theta(z_i|s,a)\big]$。目标 PMF 不求梯度（no_grad 块内），`clamp(min=1e-5, max=1-1e-5)` 防 log(0)。因为 Σtarget=1，这等价于最小化 $\mathrm{KL}(\hat p \| p_\theta)$——**把 TD 回归问题变成了分类问题**。

**（3）Adam eps 特设（L161）**：`eps=0.01/batch_size`（≈7.8e-5）——分布 RL 论文的专用细节（DQdA 论文推荐），比默认 1e-8 大百倍，抑制分类交叉熵下二阶矩估计的病态。

**（4）v_min/v_max 的选择（L54-57）**：[-100, 100] 针对 CartPole（γ=0.99 时回报上界≈100）。支持集必须罩住真实回报范围，否则投影把尾部质量堆积在边界原子上（clipping bias）。

### 与其他变体的差异

- vs `dqn.py`：输出头 ×101 维、损失 MSE→CE、Adam eps、无 tau；网络主干/ε-greedy/replay/主循环骨架全部相同——**是理解"分布 RL 只改价值学习方式"的最佳 diff**。
- vs `rainbow_atari.py`：C51 是它的"分布投影"组件单件版；Rainbow 再叠 NoisyNet/Dueling/n-step/PER/Double。

### 模式与坑

- 投影代码的 `(l==u)` 与 rainbow 版的 `(l==b)`（rainbow L490）写法不同但等价——两处独立实现都处理了整数格点边界，说明这是投影代码的头号坑；自己从 c51 抄到新环境时最常错的是 `delta_z` 用了在线网而 support 用了目标网（本实现统一用 `target_network.atoms`，L212-214）。
- 逐样本 for 循环（L225-227）在 batch 128×101 上尚可，Atari 版需向量化（scatter_add）否则训练慢一个量级。
- 目标网硬更新频率 500 沿用 dqn.py，但分布 RL 论文常用 1000/10000——复现论文时别把"与 dqn.py 对齐"误当"与 C51 论文对齐"。
- `get_action` 返回的 `pmfs[arange(len(x)), action]`（L116）——注意它返回的是**被选动作**的 PMF，训练时传 `data.actions` 取旧动作分布，与 PPO 的"重算旧 logprob"精神同构。

---

## cleanrl/rainbow_atari.py

**知识图谱**：`file:cleanrl/rainbow_atari.py`，complexity=complex，tags=[rainbow, dqn, prioritized-replay, atari, tested]。OUT 边 contains 六个类：NoisyLinear / NoisyDuelingDistributionalNetwork / SumSegmentTree / MinSegmentTree / PrioritizedReplayBuffer——**唯一把数据结构与网络都内联进单文件的算法脚本**（连 ReplayBuffer 都自带，不用 cleanrl_utils）。529 行是本组最长。

### 架构角色

DQN 家族的"集大成"变体：把 2017 年 Rainbow 论文的六大组件中五个（NoisyNet 探索、Dueling 网络、分布价值、n-step 回报、优先回放 PER）+ Double DQN 打包进一个文件。它教的是**组件级组合**：每个组件独立可拆，代码上以"网络换头 + buffer 换实现 + 目标计算换公式"的方式叠加。也正因如此，它是本组工程量最大的文件。

### 文件解剖（五段 + 两个内联数据结构段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L28-94 | DQN Atari 刻度 + Rainbow 专属：n_step=3、PER α/β/eps、n_atoms=51、v_min/max=±10、lr=6.25e-5 |
| ② make_env | L97-119 | 同 dqn_atari.py 的 wrapper 栈 |
| ③ 网络 | L122-202 | `NoisyLinear`（L122-157）+ `NoisyDuelingDistributionalNetwork`（L161-202） |
| ③' 数据结构 | L205-367 | `PrioritizedBatch` namedtuple（L205-207）、`SumSegmentTree`（L211-241）、`MinSegmentTree`（L245-262）、`PrioritizedReplayBuffer`（L266-367，含 n-step 逻辑 L292-330） |
| ④⑤ 主循环 | L370-529 | β 退火（L427-430）→**无 ε-greedy** 的噪声网选动作（L433-436）→训练段（L459-521：Double+投影+PER 加权） |

### 算法要点

**（1）NoisyLinear（L122-157）**——探索的内生化。权重 $w = \mu_w + \sigma_w \odot \epsilon_w$，其中 ε 为每次 `reset_noise()`（L146-148）重抽的随机噪声（代码用独立高斯；注释 L135 标注 factorized 版本需 ε=f(ε₁)ε₂，本实现是简化）。**训练时（L151-153）用噪声权重，eval 时（L154-156）只用 μ**。效果：策略天然带随机性，ε-greedy 被整体替代——注意主循环 L433-436 直接 `argmax`，Args 里的 `start_e/end_e/exploration_fraction`（L71-76）是**遗留死参数**，改它们没有任何效果。

**（2）Dueling + 分布头（L182-194）**：价值流 $V$（1×n_atoms）与优势流 $A$（n_actions×n_atoms）在原子维合成：$Q(s,a,z) = V(s,z) + A(s,a,z) - \frac{1}{|A|}\sum_j A(s,j,z)$（L192 的 `advantage.mean(dim=1, keepdim=True)`），再 softmax(dim=2) 归一化成每个动作的 PMF（L193）。两个流都用 NoisyLinear 堆叠（L182-186）——**探索、Dueling、分布三个组件在同一对头里融合**。

**（3）n-step 回报（L292-330）**：`deque(maxlen=n_step)` 滑窗聚合，转移入库时 $\;R^{(n)} = \sum_{i=0}^{n-1}\gamma^i r_i$，下一状态取窗口末端，done 提前截断（L297-302）。训练时的折扣相应变 $\gamma^n$（L478：`gamma_n = args.gamma**args.n_step`）。

**（4）PER（L266-367）**：优先级 $p_i$，采样概率 $P(i) = p_i^\alpha / \sum_j p_j^\alpha$（α=0.5 折中贪心程度）；重要性权重 $w_i = (N \cdot P(i))^{-\beta}/\max_j w_j$（L352-355）修正分布偏置，β 从 0.4 线性退火到 1（L427-430，训练后期偏置消失）。`SumSegmentTree`（L211-241）以 O(log N) 支持按累积概率二分采样（`retrieve` L231-241：根下行，左子装得下就走左，否则扣掉再走右）；`MinSegmentTree`（L245-262）O(1) 取最小优先级算 max 权重。新样本以当前 max priority 入库（L322-324）保证至少被采一次。

**（5）Double DQN + 分布投影（L466-496）**：动作选择与评估分离——**在线网 argmax 选动作**（L472-474），**目标网取该动作的分布**（L475：`next_dist[arange(B), best_actions]`）；随后 n-step 贝尔曼 + C51 投影（公式同 c51.py 节，γ 换 γⁿ，L477-496）。

**（6）损失与优先级（L498-507）**：$\mathcal L = \mathbb E_w[\mathrm{KL}(target \| pred)]$——逐样本 KL（L502）乘 PER 权重（L503）再平均；**逐样本 KL 直接充当新优先级**（L506-507，|loss|+eps 后 ^α）——分布版 PER 用损失而非 TD error 定优先级。

### 与其他变体的差异

- vs `dqn_atari.py`：同环境同 CNN 前端，但（a）QNetwork→NoisyDueling 分布网络；（b）cleanrl_utils.ReplayBuffer→内联 PrioritizedReplayBuffer（uint8 存储，L276-277）；（c）TD 训练段全换；（d）无 ε-greedy。
- vs `c51.py`：投影公式几乎逐行同源（c51 L214-227 vs rainbow L480-496，仅 `(l==u)` 与 `(l==b)` 写法之别与 γⁿ 之别）；c51 是"纯分布"，rainbow 是"分布+四件套"。

### 模式与坑

- **死参数**：Args 里的 ε 三参数（L71-76）与 `save_model/upload_model`（L46-51）在本文件主循环中均未使用——从 dqn_atari.py 复制骨架后的遗留。单文件哲学的副作用：每个变体自带完整参数表，读代码时要分辨"活参数"与"化石"。
- buffer 存 `np.uint8`（L276-277）：84×84×4 的栈帧省 4 倍内存；但 `buffer_rewards` 用 float32（L279），n-step 聚合后奖励精度重要。
- `target_network_frequency=8000` + tau=1.0：Rainbow 论文的慢目标网刻度，比 dqn_atari 的 1000 更慢——组件多了，目标越稳定越好。
- `reset_noise()` 在**每次训练前对两个网络都重抽**（L462-463）——不是每步 rollout 前重抽；探索噪声的更新粒度是 train_frequency=4 环境步。
- 每次训练 `data = rb.sample()` 里 weights/indices 跟着 batch 走（L355-356），随后 `update_priorities` 写回（L507）——漏掉写回，PER 退化为固定偏置采样且 max_priority 冻结。

---

## cleanrl/ddpg_continuous_action.py

**知识图谱**：`file:cleanrl/ddpg_continuous_action.py`，complexity=complex，tags=[ddpg, continuous-control, tested]。OUT 边同 dqn.py 模式（buffers/evals/huggingface），`docs/contribution.md` 也引用它（作为贡献者模板示例）。

### 架构角色

off-policy 连续控制的基线：**确定性策略 + Q(s,a) critic** 的最小组合。它在教学上的位置是"连续控制的 DQN"——把 argmax 换成可微的 actor 网络来逼近 $\arg\max_a Q$。同时它是 TD3/SAC 的对照组：后续两个文件的全部改进都针对它的已知病灶（Q 过估计、探索低效）。

### 文件解剖（标准五段，off-policy 连续版）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L19-64 | 通用段 + DDPG 专属：tau=0.005/batch 256/exploration_noise=0.1/learning_starts=25e3/policy_frequency=2（**注意：L63 注释明说 delayed，这是借 TD3 的稳定化**） |
| ② make_env | L67-78 | 纯净版：仅 RecordEpisodeStatistics + action_space.seed——**无归一化 wrapper**（与 PPO 连续版对照鲜明） |
| ③ 网络 | L82-115 | `QNetwork`（L82-94）：cat(s,a)→256-256→1；`Actor`（L97-115）：256-256→tanh→**动作缩放** `x*scale+bias`（L104-109 注册 buffer，L114-115 前向） |
| ④ 缓冲 | L160-167 | `envs.single_observation_space.dtype = np.float32` hack（L160）+ ReplayBuffer |
| ⑤ 训练循环 | L118-265 | warm-up 随机（L174-175）→噪声探索（L177-180）→每步训练（L204-229）→save_model（L238-262） |

Actor 的动作缩放是连续控制的通用技：$\pi(s) = \tanh(W h + b)\cdot\frac{a_{high}-a_{low}}{2} + \frac{a_{high}+a_{low}}{2}$，用 `register_buffer` 让 scale/bias 随模型走（TD3 的目标平滑还要引用它，L179）。

### 算法要点

**（1）探索（L174-180）**：前 25k 步均匀随机动作（warm-up 填充 buffer）；此后 $a = \mu_\theta(s) + \mathcal N(0, 0.1\cdot\text{scale})$ 再 clip 到合法区间——**高斯噪声叠加在确定性策略上**，是最朴素的连续探索。

**（2）critic/actor 目标（L206-223）**：

$$y = r + \gamma(1-d)\,Q_{\bar\theta}(s', \mu_{\bar\phi}(s')),\qquad \mathcal L_Q = \text{MSE}(Q_\theta(s,a),\,y)$$
$$\mathcal L_\pi = -\mathbb E\big[Q_\theta(s, \mu_\phi(s))\big]$$

两个目标网 $\bar\theta,\bar\phi$ 都软更新（L226-229）：$\bar\theta \leftarrow \tau\theta + (1-\tau)\bar\theta$，tau=0.005。actor 损失的负号即"沿 Q 上升方向调策略"——确定性策略梯度 $\nabla_\phi J = \mathbb E[\nabla_a Q \cdot \nabla_\phi \mu]$ 的自动微分写法。

**（3）延迟策略更新（L219）**：`policy_frequency=2`——actor 与目标网每 2 步才更新一次（critic 每步），降低 actor 追逐移动目标的速度。**这是 TD3 的技巧回流**：原版 DDPG 每步全更新，CleanRL 版做了实用化改造（文档亦如实呈现）。注意目标网的软更新也被放在这个 if 里——critic 目标网同样每 2 歳才动，这是与 TD3 实现的微妙差别。

**（4）训练频率**：无 train_frequency 参数——`global_step > learning_starts` 后**每个环境步都做一次梯度**（L204-205），与 DQN 组的"每 4/10 步一次"不同，连续控制惯例是 1:1。

### 与其他变体的差异

- vs `dqn.py`：argmax→actor 网；ε-greedy→高斯噪声；离散头→tanh 缩放头；tau 1.0→0.005（软更新首次登场）。
- vs `td3_continuous_action.py`：单 Q→双 Q、无目标噪声→目标策略平滑——TD3 的两个补丁正是冲着本文件的过估计来的；结构 diff 极小（见下节）。
- vs `sac_continuous_action.py`：确定性+加噪 vs 随机+tanh squash；无熵正则 vs 最大熵。

### 模式与坑

- L160 `envs.single_observation_space.dtype = np.float32`：MuJoCo 向量环境 obs dtype 标注修复，让 ReplayBuffer 分配 float32——不写这行会分配 float64 双倍内存。这是环境库的坑，不是算法的。
- L234 logging 引用 `actor_loss`：它只在 `policy_frequency` 分支里赋值（L220）；由于 learning_starts=25e3 ≫ 100，首次打日志前必然已赋值——但如果把 learning_starts 调小于 100，会 NameError。**日志变量引用未定义路径**是这类脚本的通病。
- 单 Q 的过估计：$y$ 里的 max 被 Q 网的乐观偏差污染，训练后期 Q 值飞涨而策略停滞——这是看 DDPG 学习曲线时的经典症状，也是理解 TD3 动机的事实基础。
- warm-up 与 `learning_starts` 同名同值（L61-62）：25k 步纯随机对这个简单基线够用；SAC 只用 5e3（随机策略本来就有覆盖力）。

---

## cleanrl/td3_continuous_action.py

**知识图谱**：`file:cleanrl/td3_continuous_action.py`，complexity=complex，tags=[td3, continuous-control, tested]。结构与 DDPG 几乎镜像（OUT 边同模式），被 `tests` 系列与 benchmark/td3*.sh 引用。

### 架构角色

DDPG 的"三补丁"修复版，教学价值在于**展示学术迭代如何以最小 diff 落地**：与 ddpg_continuous_action.py 相比，算法差异浓缩为三处共约 15 行，其余（网络定义、环境、主循环骨架）逐行相同。三个补丁——clipped double Q、目标策略平滑、延迟更新——分别打在"目标计算"、"目标动作"、"更新频率"三个点上。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L19-70 | DDPG 版 + 两个新参数：`policy_noise=0.2`（L61）、`noise_clip=0.5`（L69） |
| ② make_env | L73-84 | 与 DDPG 逐字相同 |
| ③ 网络 | L87-132 | QNetwork/Actor 与 DDPG 相同（仅 Actor 的 scale/bias 取自 `single_action_space`，L113-126——支持多 env 的写法差异） |
| ④ 缓冲 | L183-191 | 同 DDPG + `n_envs=args.num_envs`（L189） |
| ⑤ 训练循环 | L135-317 | 探索段同 DDPG（L198-204）；**目标计算换新（L231-242）**；双 Q 损失（L244-248）；延迟更新+三网软更新（L255-267） |

### 算法要点

TD3 = DDPG + 以下三式，全部落在 L231-267：

**（1）Clipped Double Q（L239-241、L244-248）**：

$$y = r + \gamma(1-d)\,\min_{i=1,2} Q_{\bar\theta_i}(s', \tilde a')$$

两个独立初始化的 critic 独立训练（$\mathcal L_{Q_i} = \text{MSE}(Q_i, y)$，L246-247，总损失相加 L248），目标取 min。原理：过估计偏差 $\mathbb E[\max(Q_1,Q_2)] \ge \mathbb E[\min(Q_1,Q_2)]$，取 min 系统性悲观一点，抵消 max 自带的乐观。

**（2）目标策略平滑（L232-238）**：

$$\tilde a' = \mathrm{clip}\big(\mu_{\bar\phi}(s') + \mathrm{clip}(\mathcal N(0,\sigma_p), -c, c)\cdot\text{scale},\ a_{low}, a_{high}\big)$$

对目标动作加**裁剪过的高斯噪声**（σ_p=0.2、c=0.5，均乘 action_scale，L232-234）再 clip 回动作区间（L236-238，用 `low[0]/high[0]`）。原理：Q(s,a) 对 a 的尖锐峰值往往是过拟合假象，平滑目标迫使 critic 学局部平均， akin 对状态-动作加正则。**注意与探索噪声的区别**：exploration_noise=0.1 作用于环境交互动作（L203），policy_noise=0.2 只存在于 TD 目标里——两者不可混用。

**（3）延迟策略更新（L255-267）**：actor/目标网每 policy_frequency=2 步更新——同 DDPG 版结构，但现在三套参数（actor + qf1 + qf2）一起软更新（L262-267）。

**（4）actor 损失只用 qf1（L256）**：$\mathcal L_\pi = -\mathbb E[Q_1(s,\mu(s))]$——不用 min，论文设计如此（一个 Q 足以引导策略，min 的偏差反而没必要带进策略梯度）。

### 与其他变体的差异

- vs `ddpg_continuous_action.py`：+qf2/qf2_target 两网（L173-175、L179）；目标段 L231-242 全新；损失变双份。**实测 diff 约 20 行**——是本组"最小算法增量"的最佳示范。
- vs `sac_continuous_action.py`：同为双 Q+延迟更新骨架，但确定性策略 vs 随机策略、目标平滑噪声 vs 熵正则——两者是"稳定 off-policy"的两条路线。

### 模式与坑

- 噪声单位问题：`policy_noise=0.2` 与 `noise_clip=0.5` 都以"归一化动作区间 [-1,1]"为尺度（乘 action_scale，L234），而 clip 到 `low[0]/high[0]`（L236-237）——若动作区间不是对称的 [-1,1]，噪声尺度与 clip 边界会不一致，复用到非标准环境时要统一。
- `writer.add_scalar("losses/qf_loss", qf_loss.item() / 2.0)`（L274）——日志里除 2 让数值与单 Q 版可比，tiny detail 但对照曲线时要知道。
- 双 Q 各自过估计仍会在两者"同错"时失效（min 挡不住系统性偏差）——SAC 保留双 Q 但换掉噪声机制，两者都不是银弹。
- L212 `if info is not None` 与 DDPG 版 L187 `if info and "episode" in info` 写法不同——同库两文件对同一 info 判空的两种风格，复制时注意保持一致避免 KeyError。

---

## cleanrl/sac_continuous_action.py

**知识图谱**：`file:sac_continuous_action.py`，complexity=complex，tags=[sac, continuous-control, tested]。被 `tests/test_mujoco.py` 覆盖；benchmark/sac*.sh 与 td3_plot.sh 都依赖它（曲线对照）。

### 架构角色

最大熵强化学习的标准实现：把"回报最大"换成"**回报 + 策略熵**最大"，用一个可学习温度 α 自动权衡。它与 TD3 共享"双 Q + 延迟更新"骨架，但把 TD3 的两个抗过估计补丁（目标噪声、min 的悲观修正）替换为**随机策略 + 熵正则**的原理性方案。CleanRL 实现对齐 Denis Yarats 的版本（代码注释 L61、L135 两处 credit），是学术界最常对标的 SAC 参考实现之一。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L19-66 | 双学习率 `policy_lr=3e-4/q_lr=1e-3`（L55-58）、`alpha=0.2`+`autotune=True`（L63-66）、无 save_model 段（本文件不存模型） |
| ② make_env | L69-80 | 与 DDPG/TD3 相同的纯净版 |
| ③ 网络 | L84-151 | `SoftQNetwork`（L84-99，同 DDPG 的 QNetwork 换名）+ `Actor`（L106-151，含 `get_action` 的 tanh-squash 采样） |
| ④ 缓冲+α | L202-219 | ReplayBuffer；autotune 初始化：`target_entropy=-dim(A)`、可学习 `log_alpha`、独立 `a_optimizer`（L203-207） |
| ⑤ 训练循环 | L154-324 | Q 目标（L257-262）→双 Q 损失（L264-273）→延迟但补偿的 actor+α 更新（L275-297）→目标网软更新（L300-304） |

`Actor` 的三段式：`forward` 输出 (mean, log_std)（L129-137），其中 log_std 经 tanh 压缩到 [LOG_STD_MIN, LOG_STD_MAX]=[-5,2]（L102-103、L134-135，SpinUp/Yarats 技巧防 std 爆炸/塌缩）；`get_action`（L139-151）完成 tanh-squash 重参数化采样。

### 算法要点

**（1）tanh 高斯与 log-prob 修正（L139-151）**——连续最大熵的核心数学：

$$u \sim \mathcal N(\mu_\theta(s), \sigma_\theta(s)),\qquad a = \tanh(u)\cdot\text{scale}+\text{bias}$$
$$\log \pi(a|s) = \log \mathcal N(u;\mu,\sigma) - \sum_j \log\big(\text{scale}_j(1-\tanh^2 u_j)+\varepsilon\big)$$

`rsample()`（L143）走重参数化路径（$\mu + \sigma\odot\epsilon$，梯度直达分布参数）；L148 的减项就是 change-of-variables 的雅可比修正——**漏掉它，熵会被系统性高估，策略过早确定性化**。L150 同时返回 tanh 后的确定性均值（eval 用）。

**（2）软贝尔曼目标（L257-262）**：

$$y = r + \gamma(1-d)\Big[\min_{i=1,2} Q_{\bar\theta_i}(s', a') - \alpha \log \pi(a'|s')\Big],\qquad a'\sim\pi(\cdot|s')$$

熵项出现在**目标里**——这就是"软"的含义：价值函数学的是含熵回报的期望。

**（3）actor 损失与温度（L279-297）**：

$$\mathcal L_\pi = \mathbb E\big[\alpha\log\pi(a|s) - \min_i Q_i(s,a)\big],\qquad a\sim\pi\ \text{(rsample)}$$
$$\mathcal L_\alpha = \mathbb E\big[-e^{\log\alpha}(\log\pi(a|s) + \mathcal H_0)\big],\qquad \mathcal H_0 = -\dim(\mathcal A)$$

α 的对偶梯度：熵高于目标则 α 降（熵约束放松）、低于则 α 升。实现细节两处：①α 损失里的 `log_pi` 用 `no_grad` **重新采样**（L290-291）——梯度只流向 log_alpha，不回传给 actor；②直接学 `log_alpha` 而非 α，保证 α>0。

**（4）延迟但补偿的更新（L275-287）**：`policy_frequency=2` 下 actor 每 2 步更新一次，但内层 `for _ in range(policy_frequency)`（L276-278）一次做 **2 梯度步**——注释明言"compensate for the delay"：更新频率降一半、每次强度加倍，总梯度量与每步更新持平。目标网更新频率 `target_network_frequency=1`（L61，注释指出 Yarats 版会 delay 2）。

**（5）无目标 actor**：SAC 目标里的动作来自**当前策略** π（非目标网），只需 Q 目标网——与 DDPG/TD3 的结构差异，也是熵正则带来的稳定性红利。

### 与其他变体的差异

- vs `td3_continuous_action.py`：同双 Q/延迟骨架；策略确定性+目标噪声 vs 随机+熵；双优化器双 lr（vs 单 lr）；无 save_model（vs 有）。
- vs `ddpg_continuous_action.py`：过估计防线从"无"到"min+熵"两级差。
- 本文件独有：可学习温度与软目标中的熵项——其余变体都没有这个自由度。

### 模式与坑

- **α 的双重身份**：target 里的 α（L261）用当前标量值；autotune 关闭时 α 是常数 `args.alpha`（L209）——两条代码路径（L203-209）共享后续所有逻辑，改代码时别只改一边。
- L290-291 重新采样而非复用 L279 的样本：α 损失需要的是"当前策略的熵的独立样本"，复用会让 α 梯度与 actor 梯度相关——细节但影响收敛性。
- `q_lr=1e-3` 大于 `policy_lr=3e-4`：critic 要追的目标比 actor 复杂，这是 SAC 社区的标准配置而非笔误。
- `get_action` 返回三元组 `(action, log_prob, mean)`（L151）——交互时只需要 action（L229-230 的 `_, _`），训练时三样都用；这个接口设计让同一方法服务两个阶段，与 PPO 的 `get_action_and_value(x, action=None)` 双用途同构。
- log_std 压缩窗口 [-5,2]：σ ∈ [e⁻⁵, e²]，遇到动作尺度极端的环境需要调——默认假设归一化动作区间。

---

## cleanrl/rpo_continuous_action.py

**知识图谱**：`file:rpo_continuous_action.py`，complexity=complex，tags=[rpo, robust-policy, tested]，被 `tests/test_mujoco.py` 覆盖。图谱 summary 点名其核心机制："在 Normal 均值上叠加 ±rpo_alpha 均匀扰动再重采样"（AAAI 2023）。

### 架构角色

**"一行思想"变体的范本**：Robust Policy Optimization 的全部算法增量是 Agent.get_action_and_value 里的 5 行——对策略均值加均匀扰动再评估旧动作。它证明 CleanRL 单文件哲学的另一面：不仅支持大型组件组合（Rainbow），也支持论文级微小改动的即插即用。它教的知识点是**对抗性/鲁棒性视角的 policy gradient**：训练目标不是单一高斯的似然，而是均值在 ±α 邻域内最坏情形的似然下界。

### 文件解剖（标准五段）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L17-80 | 与 ppo_continuous_action.py 逐项相同 + `rpo_alpha=0.5`（L71-72） |
| ② make_env | L83-99 | 与 ppo_continuous_action.py 逐字相同（8 层归一化链） |
| ③ Agent | L102-144 | 同款 critic/actor_mean/actor_logstd；**唯一差异 L138-142**：`else` 分支（评估旧 action 时）加扰动 |
| ④ 缓冲 | L189-194 | 同 ppo_continuous_action.py |
| ⑤ 训练循环 | L147-332 | 与 ppo_continuous_action.py 同构（GAE L236-250 / 更新 L260-309） |

### 算法要点

**（1）RPO 扰动（L136-143）**——全部算法内容：

```python
if action is None:            # rollout 采样：与 PPO 完全一致
    action = probs.sample()
else:                         # 更新期评估旧 action：
    z = torch.FloatTensor(action_mean.shape).uniform_(-self.rpo_alpha, self.rpo_alpha).to(device)
    action_mean = action_mean + z          # 扰动均值，不动旧 action！
    probs = Normal(action_mean, action_std)
```

数学：把策略定义为均值在 $[\mu-\alpha, \mu+\alpha]$ 均匀混合的混合分布 $\tilde\pi(a|s) = \frac{1}{2\alpha}\int_{-\alpha}^{\alpha}\mathcal N(a;\mu+\delta,\sigma)d\delta$。精确积分难算，RPO 用"采一个 δ 后用 $\mathcal N(\mu+\delta,\sigma)$ 的似然"作蒙特卡洛近似，配合 PPO 的 clip 保证稳定。效果：梯度推动策略在**均值邻域内一致地**提高旧动作似然，等价于对 μ 的扰动鲁棒化——α 是"鲁棒半径"超参。

**（2）时序语义**：扰动只发生在 `action is not None` 的分支——即 update 阶段每次重算 `newlogprob` 时，每个 minibatch 的每个 epoch 都重新采 δ（随机化近似最坏情形）。rollout 采样与存储完全不变。**改动被隔离在一个函数的一个分支里**。

**（3）其余一切同 PPO 连续版**：GAE、clip、value clip、优势归一化、target_kl、lr 退火、超参（num_envs=1/num_steps=2048/epochs 10/ent_coef 0.0）全部原样；`total_timesteps=8M`（L39，论文刻度）。

### 与其他变体的差异

- vs `ppo_continuous_action.py`：diff = L71-72 一个参数 + L109 构造函数传参 + L138-142 五行——**本组最小算法 diff（约 8 行）**。
- vs `sac_continuous_action.py`：同为"对分布施加鲁棒化约束"，RPO 在 on-policy 侧扰动均值，SAC 在 off-policy 侧最大化熵——两条鲁棒路线的对照。

### 模式与坑

- **`device` 的全局引用（L140）**：`Agent.get_action_and_value` 里直接用了外部全局变量 `device`（`.to(device)`）——类方法依赖全局态，是 CleanRL 少见的代码卫生瑕疵；把 Agent 类复制到别的项目会 NameError。对比：ppo.py 家族其它文件的 Agent 不引用任何全局。
- `torch.FloatTensor(shape).uniform_()` 在 **CPU 上生成再搬 GPU**（L140）——多一次同步拷贝；逐 epoch 逐 minibatch 调用时是小的性能税。
- 扰动加在**归一化后的动作空间**（wrapper 链把 obs/reward 归一了，但动作靠 ClipAction 截断）——rpo_alpha=0.5 的量纲是原始动作单位，环境动作尺度不同时要重调。
- 论文复现细节：官方默认 ent_coef=0.0 沿用 PPO 连续版——RPO 的均匀扰动本身就在增加探索多样性，不需要额外熵奖金。

---

## cleanrl/pqn.py

**知识图谱**：`file:pqn.py`，complexity=complex，tags=[pqn, q-learning, training-script, single-file]。OUT 边显示它**不依赖** cleanrl_utils（无 buffers/evals 依赖）——离线家族中唯一自包含到"零 import 算法模块"的成员；图谱 summary 精准概括："把 DQN 改造成 PPO 式的 minibatch 多 epoch 更新，用 Q(λ) 折扣优势目标"。

### 架构角色

**两大范式的杂交实验**：Phasic Q-Network 用 PPO 的优化协议（向量化 rollout → 短暂存储 → minibatch 多 epoch）跑 value-based 的学习目标（Q 回归 + ε-greedy），发现**不需要 replay buffer、不需要目标网络**也能稳定——"phasic"即指 rollout 收集与参数更新两阶段分离。它在 CleanRL 知识体系里的位置是"打破 on-policy/off-policy 二分法"的第三物种，也是理解"PPO 的稳定性到底来自哪"（优化协议 or 算法数学？）的对照实验。

### 文件解剖（标准五段，混合范式版）

| 段 | 行号 | 内容 |
|---|---|---|
| ① Args | L17-64 | **PPO 侧参数**（num_envs=4/num_steps=128/num_minibatch=4/update_epochs=4/anneal_lr/max_grad_norm）+ **DQN 侧参数**（start_e/end_e/exploration_fraction）+ 混合参数 `q_lambda=0.65`（L63-64） |
| ② make_env | L67-79 | 经典控制版（RecordEpisodeStatistics + action_space.seed） |
| ③ QNetwork | L82-104 | `layer_init` 正交初始化 MLP 120-84 + **每层后接 `nn.LayerNorm`**（L95、L98）再 ReLU——无目标网时代替其稳定作用的关键部件 |
| ④ 缓冲 | L155-159 | PPO 式六张量减到五个（无 logprobs——value 学习不需要旧行为概率！） |
| ⑤ 训练循环 | L112-248 | rollout（L175-202，ε-greedy 版）→ **Q(λ) 目标**（L205-218）→ flatten（L221-223）→ minibatch 多 epoch MSE（L226-240） |

优化器是 **RAdam**（L152，非 Adam）——PQN 论文的选择，方差修正的 Adam 对无目标网的 Q 回归更稳。

### 算法要点

**（1）ε-greedy 的向量化写法（L180-189）**——与 DQN 的 if/else 不同，PPO 式多环境需要并行掷硬币：

```python
random_actions = torch.randint(0, n, (num_envs,))          # L181
q_values = q_network(next_obs); max_actions = argmax(...)  # L183-184
explore = torch.rand((num_envs,)) < epsilon                # L187
action = torch.where(explore, random_actions, max_actions) # L188
```

注意 `values[step]` 存的是 **greedy 价值** $\max_a Q(s_t,a)$（L185，不管实际执行的是不是 greedy 动作）——这是 Q(λ) 目标的伏笔。

**（2）Q(λ) 目标（L205-218）**——Peng 式衰减 λ-return 递推：

$$G_t = r_t + \gamma(1-d_{t+1})\big[\lambda\, G_{t+1} + (1-\lambda)\, V(s_{t+1})\big],\qquad V(s) = \max_a Q(s,a)$$

倒序循环，序列末端 bootstrap $\max_a Q(s_{T},a)$（L208-211）。与 GAE 的形式对照：GAE 递推的是优势（δ 的加权和），Q(λ) 直接递推**回报目标**；λ=0 退化为一步 TD（DQN 目标），λ=1 退化为蒙特卡洛。q_lambda=0.65 是两端的折中——**没有目标网络时，λ<1 等效于给自举加了偏差、降了方差**，与 LayerNorm/RAdam/grad-clip(max 10.0, L61) 共同构成"无 target net"的稳定器组合。

**（3）损失与更新（L233-240）**：纯 MSE 回归 $Q_\theta(s_t,a_t) \to G_t$（无 clip、无熵、无 ratio），gather 取执行动作列；PPO 式 minibatch 多 epoch（4 epochs × 4 minibatch × batch 512 = 每 iteration 16 次梯度）。

**（4）lr 退火照抄 PPO（L169-173）**：on-policy 协议的一部分被完整继承——PQN 的核心论点正是"这套优化协议本身贡献了 PPO 的大部分稳定性"。

### 与其他变体的差异

- vs `dqn.py`：replay buffer→on-policy 短暂存储；目标网→无（LayerNorm+RAdam+λ 折中代替）；逐步训练→批量多 epoch；MLP 加 LayerNorm。
- vs `ppo.py`：网络 actor-critic→单 Q 网；GAE→Q(λ)；ratio/clip/entropy 全删；存储无 logprobs；ε-greedy 探索替代随机策略。**骨架是 PPO 的、灵魂是 DQN 的**。
- 独有部件：LayerNorm（全组唯一）、RAdam（全组唯一）、`values` 存 greedy max（全组唯一）。

### 模式与坑

- **没有 target network 的 Q 学习是反直觉的**：教科书说必须有，PQN 证明配合多 epoch 短 rollout + 归一化技巧可以不需要——但把这套搬到 off-policy（长 replay）会立刻发散；"稳定器组合"是绑定的，不能只拿走一半。
- `values` 语义与 PPO 完全不同：PPO 存 $V_\pi(s)$（critic 输出），PQN 存 $\max_a Q$（greedy 价值）——两者都叫 values 变量，复制代码时极易混淆。
- ε-greedy 里 `epsilon` 在 rollout 内层每步重算（L180），而 PPO 家族的超参都在 iteration 级生效——探索退火的粒度是步级的。
- `max_grad_norm=10.0`（L61）远大于 PPO 的 0.5——value 回归的梯度尺度与 policy gradient 不同，沿袭论文值；对照调参时别套 PPO 习惯。
- 无 save_model/evals 依赖（OUT 边无 huggingface）——PQN 在 CleanRL 里是较新的实验性成员，工程配套不如老算法全。

---

## docs/rl-algorithms/overview.md + docs/rl-algorithms/ppo.md（官方文档简讲）

**知识图谱**：两节点均属 `layer:documentation 文档层`。`overview.md`（simple）是总索引表；`ppo.md`（complex，1180 行，本批最大文件）documents 边指向全部 10 个 PPO 变体文件。

### overview.md（33 行）讲什么

一张"算法 × 变体"总表：PPO（11 个变体，L5-15：cartpole/atari/continuous/lstm/envpool/×2 JAX/procgen/multigpu/pettingzoo/isaacgym）、DQN（4）、C51（4）、SAC（2）、DDPG（2）、TD3（2）、PPG（1）、RND（1）、Qdagger（2）。每行 = 论文 arXiv 链接 + GitHub 脚本链接 + docs 锚点。用法：它是 mkdocs 站点导航的数据源，也是"我想跑 X 算法该用哪个文件"的速查表——注意它按**算法**而非按**环境**组织，查"MuJoCo 有哪些选择"要横向扫表。

### ppo.md（1180 行）讲什么

PPO 主文档，结构是总述 + 10 个变体小节（`## ppo.py` L39 / `## ppo_atari.py` L139 / `## ppo_continuous_action.py` L226 / `## ppo_atari_lstm.py` L409 / envpool L488 / xla_jax L565 / scan L690 / procgen L763 / multigpu L849 / pettingzoo）。总述给出三份关键参考文献，其中 ⭐《The 37 Implementation Details of PPO》（ICLR blog track 2022）是 CleanRL 的精神源头——文档明确说所有 PPO 实现"matched the implementation details"于该文。每个变体小节五段式：

1. **Usage**（uv/pip 双 tab 的命令行示例）；
2. **Logged metrics 解释**（L64-78）——最有教学价值的段落：逐条解释 `episodic_return/SPS/value_loss/clipfrac/explained_variance`，并明确 `old_approx_kl` 是 k1 估计 $(-\log r)$ 均值、`approx_kl` 是 k3 估计 $(r-1)-\log r$（对照 Schulman 博客）——与代码 L254-257 一一对应；
3. **Implementation details**（L81-97）——13 条核心细节逐条给出 openai/baselines 的源码行号链接（如正交初始化 ↔ baselines/a2c/utils.py#L58），是"论文算法→工程实现"的对照表；
4. **Experiment results**——与 baselines 的对照数字（如 ppo.py 在 CartPole-v1：490.04±6.12 vs baselines 497.54±4.02，L109-113）+ benchmark 脚本 + 学习曲线；
5. **Video tutorial**（部分变体）。

**一句话**：overview.md 是地图，ppo.md 是 PPO 家族的"实现辩护书"——它把代码里每一行"魔法数字"（Adam eps=1e-5、std=0.01、clip 0.1…）都追溯到 baselines 的源码级出处，这正是 CleanRL"可审计的单文件实现"理念在文档侧的镜像。

---

## 全组横评：15 文件的模式总结

**（1）共享骨架的"差分编程"**。13 个算法脚本共享 90% 的骨架（Args→make_env→网络→存储→主循环），算法身份由三处 diff 决定：网络定义段（L80-170 区域）、主循环的训练段（ALGO LOGIC 注释块）、Args 默认值。跨文件 diff 阅读是本仓库最高效的读法——建议顺序：ppo.py 全读 → ppo_atari/continuous 只看 diff → dqn.py 全读 → c51/rainbow 只看训练段 → ddpg→td3→sac 链式 diff → rpo/pqn 收尾。

**（2）`# TRY NOT TO MODIFY` / `# ALGO LOGIC` 双注释系统**。前者标环境交互样板（seed/reset/step/final_info/real_next_obs 五件套在所有文件逐字相同），后者标算法差异点——这是 CleanRL 给"复制修改"工作流设计的导览。

**（3）跨家族的三个不变式**。①truncation 修正：off-policy 家族的 `real_next_obs` 模式（dqn L184-188 等）与 on-policy 家族的 `next_done = terminations | truncations`（ppo L206）处理的是同一问题——时间限制不是真实终止；②SPS 指标：所有脚本都打 `charts/SPS`，跨算法性能对比先看它；③`run_name = env__exp__seed__timestamp` 的目录约定支撑 runs/ 与 videos/ 的产物管理。

**（4）单文件哲学的边界**。本组可见三处松动：`cleanrl_utils/buffers.py`（8 个脚本共享）、`atari_wrappers.py`（5 个）、`dqn_atari.py 的 QNetwork 被 qdagger import`（脚本当库用）。教训：单文件的代价在"共享数据结构"处最先撑不住。

**（5）坑的分布规律**。本组最常见的四类坑：索引错位（LSTM minibatch 的 `flatinds`、GAE 的 dones[t+1]）；同名参数双语义（tau 的 1.0 vs 0.005、两种噪声）；死参数（rainbow 的 ε 三件套）；日志变量在条件分支外引用（ddpg 的 actor_loss）。前三类源于"复制骨架改差异"的开发模式，第四类源于性能优化（避免每步 logging）——都是单文件哲学的结构性副产品，读任何 CleanRL 风格代码时都值得先扫这四类。

---

*生成：understand-explain 工作流（知识图谱 487 节点 + 15 源文件全文精读）。姊妹篇：CORE-FILES-EXPLAIN-part2.md（其余核心文件）。*


---

# cleanrl 核心文件精讲（2/3）：高级变体与 JAX 栈

> 本文续接 part1（基础算法族）。覆盖 15 个文件：**性能优化变体**（EnvPool / 多GPU）→ **高级算法**（RND / Procgen / PPG / QDagger）→ **JAX 栈**（XLA PPO 两版 / DQN / TD3 / GAE 测试）→ **项目叙事**（README / pyproject / CONTRIBUTING）。
> 所有行号锚点均实测自本地仓库 `~/ai/cleanrl/`（master 分支工作区）；知识图谱节点信息来自 `.understand-anything/knowledge-graph.json`（487 节点 / 1052 边）。
> 前置阅读：`CORE-FILES-EXPLAIN-part1.md`（ppo.py / dqn.py 等基础版逐行讲解，本文多处与其做差异对照）。

---

## cleanrl/ppo_atari_envpool.py

**知识图谱**：`file:cleanrl/ppo_atari_envpool.py` · tags: `ppo/atari/envpool/training-script/tested` · complexity: complex · 出边 `tested_by → tests/test_envpool.py`，入边被 `benchmark/ppo.sh`、`docs/benchmark/ppo_atari_envpool.md` 引用。

### 架构角色

PPO Atari 的**吞吐优化第一站**：用 EnvPool（C++ 实现的向量化环境库）替代 `gym.vector.SyncVectorEnv + atari_wrappers` 预处理链，把帧跳过、灰度化、缩放、生命终止、奖励裁剪全部下沉到 C++ 侧，官方宣称 **3-4x 无痛加速**（README.md:111-116，同时警告"样本效率可能下降"的副作用）。它是后续 RND 版（`ppo_rnd_envpool.py`）和两个 JAX 版的**共同底座**——读通这一个文件，envpool 系四个文件的环境接入代码全部通关。

### 文件解剖（344 行）

| 行号 | 内容 |
|---|---|
| 19-80 | `Args` dataclass：PPO 标准超参（lr=2.5e-4, num_envs=8, num_steps=128, clip=0.1）+ 运行时字段（batch_size/minibatch_size/num_iterations 占位 0，74-80） |
| 83-114 | `RecordEpisodeStatistics(gym.Wrapper)`：**手写的**回合统计包装器（见要点） |
| 117-120 | `layer_init`：orthogonal 初始化 + bias 常量 |
| 123-149 | `Agent`：Nature CNN（4→32→64→64 卷积 + 512 FC）双头，与 `ppo_atari.py` 完全一致 |
| 152-157 | CLI 解析 + 派生尺寸计算（`batch_size = num_envs × num_steps` 等） |
| 176-182 | 播种 + device 选择 |
| 185-197 | **envpool.make 接入**（核心差异段）：`episodic_life=True, reward_clip=True`，随后三行 monkey-patch |
| 203-209 | 六个 rollout 缓冲区张量（预分配在 GPU）+ `avg_returns` deque(20) |
| 217-226 | 外层 iteration 循环：学习率线性退火（219-222） |
| 224-247 | 内层 step 循环：采样（230-234）→ `envs.step`（237）→ 回合日志（241-247） |
| 249-263 | GAE 反向递推（bootstrap next_value 251） |
| 266-271 | 展平 batch |
| 274-325 | PPO 更新：shuffle + 4 epoch × 4 minibatch，ratio/clip/pg_loss/clip_vloss/target_kl 全家桶 |
| 327-341 | explained_variance + TensorBoard 日志 + SPS |

### 算法/工程要点

1. **EnvPool 接入三步曲（185-197）**：
   - `envpool.make(env_id, env_type="gym", num_envs=..., episodic_life=True, reward_clip=True, seed=...)` —— 一行顶基础版 `make_env` 里 9 层包装器（NoopReset/MaxAndSkip/EpisodicLife/FireReset/ClipReward/Resize/GrayScale/FrameStack，见 `ppo_atari_multigpu.py:113-121` 对照）；
   - **monkey-patch（193-195）**：`envs.num_envs`、`envs.single_action_space`、`envs.single_observation_space` 三个属性是手动赋值的——envpool 对象不原生提供 vector-env 接口，这三行让它"长得像" `gym.vector.Env`，后续 `Agent(envs)` 构造和 storage 形状推断代码就不用改；
   - envpool 返回**老 gym 四元组** `(obs, reward, done, info)`（237），而非 gymnasium 五元组——这是本文件还在 `import gym`（而非 gymnasium）的原因。

2. **手写 RecordEpisodeStatistics（83-114）**：envpool 的 info 是**逐环境的数组字典**（`info["reward"]`、`info["terminated"]` 形状均为 `[num_envs]`），gymnasium 自带的 `RecordEpisodeStatistics` 处理不了这种结构，于是重写：累加 `episode_returns += info["reward"]`（101），用 `*= 1 - terminated` 在终止时清零（105-106），并把**最后完成的回合值**缓存在 `returned_episode_returns` 里（103）——因为一个 step 内只有部分环境终止，`infos["r"]` 对未终止环境返回的是"上一次完成回合"的旧值。

3. **真回合结束判定（241-242）**：`if d and info["lives"][idx] == 0`——`episodic_life=True` 时 `done` 在**掉一条命**时就置位（用于价值截断），但只有 `lives==0` 才是游戏真结束，此时打印/记录的才是完整回合回报。这行是 envpool 版独有的细节，基础版由 `EpisodicLifeEnv` 包装器语义 + gymnasium 的 `final_info` 机制隐式处理。

4. **`avg_returns` 平滑（209, 244-245）**：deque(maxlen=20) 维护近 20 个回合均值，比单回合值稳定得多——envpool 高吞吐下回合结束非常频繁，逐条打印会很吵。

### 与基础版（ppo_atari.py）差异

| 维度 | ppo_atari.py | ppo_atari_envpool.py |
|---|---|---|
| 环境构造 | `SyncVectorEnv` + 9 层 Python 包装器 | `envpool.make` 一行（C++ 内置预处理） |
| API 风格 | gymnasium 五元组 `(obs, r, term, trunc, info)` | 老 gym 四元组 + 数组型 info |
| 回合统计 | `gym.wrappers.RecordEpisodeStatistics` + `final_info` | 手写 Wrapper（83-114） |
| 算法本体 | 完全相同（NatureCNN + GAE + clip PPO） | 完全相同（123-325 逐行可对照） |

**cleanrl 的变体哲学在这里最典型**：文件间算法代码故意复制而非抽象——每个文件自包含全部细节，代价是重复，收益是"读一个文件=理解一个完整变体"。

### 模式与坑

- **envpool 仅 Linux**（pyproject.toml:35 无平台标记但官方文档明确）；安装走 `pip install ".[envpool]"`。
- **副作用是真实存在的**：README:115 明言样本效率可能降低——envpool 的 sticky action 概率等默认参数与 ALE 包装器链不完全一致。
- **`torch_deterministic` 注释反直觉（25-26）**：docstring 写 "if toggled, `cudnn.deterministic=False`"，但代码 L180 是 `= args.torch_deterministic`（默认 True 开确定性）——文档与代码语义相反，cleanrl 全库统一沿用此（误导性）措辞。
- `envs.step` 接收 numpy（237: `action.cpu().numpy()`），返回值又 `torch.Tensor()` 回 GPU（239）——每步两次 H2D/D2H 拷贝，这是 envpool 版仍留有的 Python 端开销（JAX 版用 `envs.xla()` 根治，见后文）。

---

## cleanrl/ppo_atari_multigpu.py

**知识图谱**：tags: `ppo/distributed/multi-gpu/atari/tested` · 出边 `imports → cleanrl_utils/atari_wrappers.py`（它反而回到了包装器路线，因为要每个 rank 独立建环境）· `tested_by → tests/test_atari_multigpu.py`。

### 架构角色

PPO Atari 的**多 GPU 数据并行**变体：`torchrun` 启动 N 个进程，每进程（rank）持有 `local_num_envs` 个环境子集各自采样，梯度经 **手写的 all_reduce 平均**后同步，数学上等效于 `num_envs × world_size` 个环境的大 batch 训练。它是观察"cleanrl 如何用 60 行代码手搓 DDP"的最佳标本——没有 `DistributedDataParallel` 封装，同步机制完全裸露。

### 文件解剖（403 行）

| 行号 | 内容 |
|---|---|
| 29-102 | `Args`：新增 `device_ids: List[int]`（83-84）、`backend: Literal["gloo","nccl","mpi"]="gloo"`（85-86）；运行时字段扩为 local/global 两套（88-102） |
| 105-124 | `make_env`：gymnasium + cleanrl_utils.atari_wrappers 完整预处理链 |
| 127-159 | `layer_init` + `Agent`：与基础版逐字相同 |
| 163-183 | 启动段：torchrun 用法注释（163）、`LOCAL_RANK/WORLD_SIZE` 环境变量（166-167）、尺寸换算（168-173）、`dist.init_process_group`（174-175）、单进程警告（176-183） |
| 184-204 | run_name / wandb / writer：**只有 `local_rank==0` 建写入器**（186） |
| 206-212 | **播种段（精髓）**：`args.seed += local_rank`（208）后 `random/np.seed(seed)`，但 `torch.manual_seed(args.seed - local_rank)`（211） |
| 214-222 | device 路由三分支：显式 device_ids 列表 / GPU 数足够按 local_rank / GPU 数不足共享 |
| 224-240 | 每 rank 建 `local_num_envs` 个环境，storage 尺寸按 local 维度 |
| 242-301 | rollout + GAE：与单机版相同逻辑，只是维度换成 local |
| 284-286 | 调试打印：`action.sum()` / `actor.weight.sum()` 用于人肉验证各 rank 是否同步 |
| 311-380 | 更新段：local batch 更新（312-358 backward）→ **手写梯度 all_reduce（360-374）** → clip → step |
| 387-397 | 仅 rank0 写日志 |

### 算法/工程要点

1. **播种的差分设计（206-212）**——分布式 RL 最容易踩的坑被三行解决：
   - 环境侧：`seed += local_rank` 让每个 rank 的 np/random 流不同 → **采样数据多样化**；
   - 模型侧：`torch.manual_seed(seed - local_rank)`（即原始种子）让所有 rank **网络初始化完全相同** → all_reduce 之前各 rank 参数本来就一致，这是梯度平均语义成立的前提。
   如果两侧用同一种子，各 rank 会采到完全相同的数据，等于 1 份数据算 N 遍梯度。

2. **手写 all_reduce（360-374）**，全文件最核心的 15 行：
   ```python
   all_grads_list = [param.grad.view(-1) for param in ...]   # 362-365 拍平
   all_grads = torch.cat(all_grads_list)                     # 366 拼成一条大向量
   dist.all_reduce(all_grads, op=dist.ReduceOp.SUM)          # 367 一次集合通信
   param.grad.copy_(all_grads[切片].view_as(...) / world_size)  # 368-374 除 N 拷回
   ```
   注释（361）指向 entity-neural-network/incubator PR#220：**把所有参数的梯度拼接后一次 all_reduce**，代替逐参数 N 次通信——大张量少次 RPC 优于小张量多次 RPC。这正是 `DistributedDataParallel` 的 bucket 机制的手工版。

3. **clip 位置（376）**：`clip_grad_norm_` 在 all_reduce **之后**执行——同步后的平均梯度统一裁剪，保证各 rank 后续 `optimizer.step()` 走完全相同的更新（裁剪也是同步的）。若在 all_reduce 前各自裁剪，范数不同会导致各 rank 梯度发散。

4. **global_step 计数（257）**：`global_step += args.num_envs`（全局环境数），但 rollout 本身只用 local 的——步数语义对齐"等效大 batch"。

5. **minibatch 顺序各 rank 不同**：shuffle 用的是 np.random（已被 rank 化种子），所以每个 rank 的 minibatch 划分不同——无所谓，因为梯度会被平均，反而等效于更大的有效 batch 内部随机性。

### 与基础版差异

| 维度 | ppo_atari.py | ppo_atari_multigpu.py |
|---|---|---|
| 启动 | `python ppo_atari_multigpu.py` | `torchrun --standalone --nnodes=1 --nproc_per_node=2 ...`（163） |
| 环境后端 | envpool | `SyncVectorEnv` + 包装器（回到 Python 侧，因 envpool 的多进程集成复杂） |
| 梯度 | 单卡 backward | backward + 手写 all_reduce 平均（360-374） |
| 日志 | 无条件写 | 仅 rank0 写（186, 387） |
| 默认 env | Breakout-v5（ALE 新 API） | BreakoutNoFrameskip-v4（老 API，配包装器链） |

### 模式与坑

- **默认 backend=gloo**（85）：CPU 也能跑通分布式（CI 友好），生产用 `--backend nccl`。
- **非 distributed 模式有退化警告**（176-183）：单进程直接跑不会 all_reduce，但代码路径一致——方便本地调试。
- **`global_step` 会重复计数吗**：不会，257 每步只加一次全局 num_envs；但注意 SPS 统计（396）的 start_time 是各 rank 自己的——rank0 的 SPS 才是可信值。
- **为什么不用 DDP**：cleanrl 的选择是教育性的——DDP 把梯度 bucket 化/重叠通信藏进黑盒，手写版让"数据并行=梯度平均"这一行数学显式可见。性能上 DDP 通常更快（通信/计算重叠），这是可读性换性能的又一例。

---

## cleanrl/ppo_rnd_envpool.py

**知识图谱**：tags: `ppo/rnd/exploration/atari/tested` · 被 `benchmark/rnd.sh` 与 `docs/rl-algorithms/ppo-rnd.md`（含实验曲线）引用 · `tested_by → tests/test_envpool.py`。

### 架构角色

**Random Network Distillation（RND，arXiv:1810.12894）+ PPO** 在 Atari 稀疏奖励游戏（默认 MontezumaRevenge）上的实现：固定随机"目标网络"与可训练"预测器"对同一观测的特征差（MSE）作为**内在好奇心奖励**，与外部奖励加权合成总优势；内外两套价值头、两套 GAE、两套归一化器并行运转。这是全库**算法增量最大**的 PPO 变体（539 行，比 envpool 版多出约 200 行 RND 机制）。

### 文件解剖（539 行）

| 行号 | 内容 |
|---|---|
| 21-94 | `Args`：RND 专有段 76-86（`update_proportion=0.25 / int_coef=1.0 / ext_coef=2.0 / int_gamma=0.99 / num_iterations_obs_norm_init=50`）；默认总量 **2e9 步、128 环境**（43-47）——探索型任务的胃口 |
| 97-128 | `RecordEpisodeStatistics`（与 envpool 版相同的手写 Wrapper） |
| 138-181 | `Agent`：骨干输出 **448 维**（149-152 两层 FC），`extra_layer`（154），actor 升为两层（155-159），**critic_ext / critic_int 双价值头**（160-161），价值输入 `features + hidden` 残差式拼接（174-175） |
| 184-229 | `RNDModel`：predictor（194-207，1 通道 CNN→3 层 512 FC）+ target（210-219，更浅：CNN→1 层 512），target 参数 `requires_grad=False`（221-223） |
| 232-242 | `RewardForwardFilter`：折扣奖励滑动累加器 |
| 278-291 | envpool.make：多一个 `repeat_action_probability=0.25`（285，sticky action，Montezuma 标准配置） |
| 293-304 | **联合优化器**（295-300）：agent + rnd.predictor 的参数塞进同一个 Adam |
| 302-315 | 三个归一化器/滤波器 + 双份 storage（curiosity_rewards/ext_values/int_values，311-314） |
| 324-335 | **观测归一化预热**：随机动作跑 `128×128×50` 步，收集最新帧（第 3 通道）更新 `obs_rms` |
| 344-388 | rollout：每步现算 RND 内在奖励（365-373） |
| 390-400 | 内在奖励归一化：RewardForwardFilter → `update_from_moments` → 除以 std |
| 402-430 | **双 GAE**：外部用 done 屏蔽；内部 `int_nextnonterminal = 1.0` 恒成立（413, 418） |
| 442 | 优势合并：`b_int_advantages * int_coef + b_ext_advantages * ext_coef` |
| 449-472 | RND 前向损失：`MSE(reduction="none").mean(-1)` + **25% 随机 mask**（468-472） |
| 494-512 | 双价值损失（ext 用 clip_vloss，int 不 clip，509）+ 总损失（512） |
| 516-520 | 梯度裁剪对象是 `combined_parameters`（含 predictor） |

### 算法/工程要点

1. **好奇心奖励的生成（365-373）**，每个环境步一次：
   - 取 `next_obs[:, 3, :, :]`——4 帧堆叠里的**最新帧**（RND 论文用单帧而非堆叠）；
   - 用预热的 `obs_rms` 标准化并 clip(-5,5)（367-369）——RND 对未归一化输入极其敏感；
   - `curiosity = ‖target(s′) − predictor(s′)‖²/2`（371-373）：**预测器没见过的状态 → 特征差大 → 内在奖励大**。target 永远冻结，所以这是一个"新颖性探测器"。

2. **内在奖励的两级归一化（390-400）**：先按环境跑 `RewardForwardFilter`（折扣累计，衡量"该环境近期好奇心总量"），再对 128 个环境的折扣和做跨环境矩估计（`reward_rms.update_from_moments`），最后整体除 std。直觉：Montezuma 里有的环境分支好奇心爆炸，有的枯竭，不归一化则策略被个别环境的好奇心洪流淹没。

3. **双折扣率体系（53-54, 83-84）**：`gamma=0.999`（外部，长视界）而 `int_gamma=0.99`（内部，短视界）——好奇心是"燃料"，不值得远期规划；GAE 里体现为两套独立的 lastgaelam 递推（408-428）。

4. **内在 GAE 无终止屏蔽（413, 418）**：`int_nextnonterminal = 1.0`——回合死了好奇心价值也不截断。哲学：环境 reset 是外部世界的属性，与"状态新颖性"无关。

5. **update_proportion=0.25（77-78, 468-472）**：每个 minibatch 只用随机 25% 的样本更新 predictor——RND 论文技巧，防止 predictor 过快拟合 target 导致好奇心信号消失（也省算力）。

6. **观测归一化预热（324-335）**：正式训练前用随机策略收集 ~82 万帧建立 obs_rms 统计——否则训练初期 RND 输入分布漂移，好奇心信号全是噪声。训练中 `obs_rms.update` 继续在线更新（444）。

### 与基础版（ppo_atari_envpool.py）差异

- **骨干**：512 维单头 → 448 维 + extra_layer + 双价值头 + 残差拼接（138-181）——网络结构直接抄自 RND 官方 openai/baselines 实现；
- **损失**：`loss = pg − ent + v·vf + forward_loss`（512）——RND 前向损失直接加在总损失里，predictor 与策略共享优化器和裁剪（516-520）；
- **采样时前向两次**（351-356）：`get_value` 与 `get_action_and_value` 分开调，各跑一遍骨干——低效但清晰（envpool 版一次前向拿到全部）；
- **默认超参面向难探索游戏**：lr=1e-4、ent_coef=0.001、gamma=0.999、2e9 步。

### 模式与坑

- **docstring 交叉写反（79-82）**：`int_coef` 的注释写 "coefficient of extrinsic reward"，`ext_coef` 反之——看 L442 的实际用法才是真相（`int_coef` 乘内在优势）。上游已知笔误，读代码勿信注释的典型案例。
- ** curiosity_rewards 在 rollout 时 no_grad 计算（371-373）**，训练时重新前向（463）并带梯度——两次计算结果数值相同（同参数），前者存的是"经验内在奖励"，后者用于 predictor 更新。
- **`values` 没有 storage 复用**：ext/int 双份 values 各占 `[128 步, 128 env]`，加上 curiosity_rewards，显存占用约为 envpool 版 2 倍。
- **torch 版 RND 的 target 网络也要 `.to(device)`**（294）——`requires_grad=False` 不影响前向计算位置。

---

## cleanrl/ppo_procgen.py

**知识图谱**：tags: `ppo/procgen/impala-cnn/training-script/tested` · `tested_by → tests/test_procgen.py` · benchmark 脚本 `ppo.sh` 引用。

### 架构角色

PPO 在 **Procgen**（OpenAI 2020 程序化生成环境族，16 个游戏）上的变体：核心增量是把 Nature CNN 换成 **Impala 风格残差 CNN**（深度可扩展，适合 64×64 RGB + 泛化需求），以及"无限关卡"模式采样。它是 `ppg_procgen.py` 与 `qdagger_*_impalacnn.py` 的网络结构来源（三个文件共享 ResidualBlock/ConvSequence 代码，注释 L88 标明出处 AIcrowd neurips2020 starter kit）。

### 文件解剖（346 行）

| 行号 | 内容 |
|---|---|
| 18-79 | `Args`：procgen 调参（lr=5e-4, num_envs=64, num_steps=256, gamma=0.999, clip=0.2, update_epochs=3, **anneal_lr=False** 默认关） |
| 82-85 | `layer_init` |
| 89-101 | `ResidualBlock`：pre-act 风格（先 ReLU 再卷积 ×2）+ 跳跃连接 `x + inputs`（101） |
| 104-123 | `ConvSequence`：Conv3×3 → MaxPool3×3/2 → 2×ResidualBlock；`get_output_shape` 给出 (h+1)//2 减半公式（121-123），forward 里 assert 形状（118） |
| 126-155 | `Agent`：3 个 ConvSequence（16/32/32 通道，132-135）→ Flatten → FC 256；**输入 permute "bhwc"→"bchw"（147, 150）** |
| 190-201 | 环境链：`ProcgenEnv(num_levels=0, ...)` → `TransformObservation(obs["rgb"])` → 手动设属性（193-195）→ RecordEpisodeStatistics → NormalizeReward → TransformReward clip(±10) |
| 220-265 | 标准 PPO rollout + GAE（与 envpool 版逐字几乎相同） |
| 244-249 | info 是 **list[dict]**（procgen 老接口），遍历找到含 "episode" 的条目打印 |
| 276-327 | 标准更新段 |

### 算法/工程要点

1. **Impala CNN vs Nature CNN**：
   - Nature CNN（Atari 标配）：3 层大步长卷积"压"分辨率——参数少，但深层梯度通路短；
   - Impala CNN：每级"卷积 + 池化 + **2 个残差块**"（104-119），网络可以深且梯度通畅——Procgen 追求**跨关卡泛化**，需要更强表征，残差结构是标配。
   - ConvSequence 的 `get_output_shape`（121-123）让 Agent 构造时能链式推断形状（132-135），forward 里 assert（118）是廉价的形状保险。

2. **`num_levels=0`（191）**：程序生成无限训练关卡——Procgen benchmark 的核心设定（train=test 关卡分离测泛化），`distribution_mode="easy"` 是标准难度档。

3. **环境端奖励处理（199-200）**：`NormalizeReward(gamma)` 维护 running discounted return 归一化奖励，再 `clip(±10)`——procgen 各游戏奖励量纲差异大，这两层包装保证一套超参通吃 16 游戏。注意这与 Atari 的做法（ClipRewardEnv 二值化）完全不同。

4. **HWC 原生格式（147, 150）**：procgen 输出 64×64×3 的 HWC 张量，而 torch 卷积要 CHW，所以在模型前向里 permute 而不是在环境侧转换（减少数据拷贝）。

### 与基础版差异

| 维度 | ppo_atari_envpool.py | ppo_procgen.py |
|---|---|---|
| 环境 | envpool（C++） | ProcgenEnv（C++ 但独立库） |
| 预处理 | envpool.make 参数内置 | TransformObservation 取 rgb + NormalizeReward + clip |
| 骨干 | Nature CNN（512） | Impala 残差 CNN（256） |
| 奖励 | reward_clip（二值化倾向） | running 归一化 + clip±10 |
| 观测 | 84×84×4 灰度帧堆 | 64×64×3 RGB 单帧 |
| episode info | 数组字典 | list[dict] |

### 模式与坑

- **`envs.is_vector_env = True`（195）**：procgen 包装链需要告知 RecordEpisodeStatistics 这是向量化环境，否则回合统计行为不对——手动赋值这种"接口缝合"在 cleanrl 环境适配层很常见（envpool 版 193-195 同款）。
- **NormalizeReward 的 gamma 与 PPO gamma 共用 args.gamma（199）**——语义上这两个 gamma 应该一致（归一器模拟折扣回报），改动时注意联动。
- ResidualBlock 的 pre-activation（97：先 relu）与经典 ResNet（后激活）不同——Impala 原文设计，照抄时别"顺手修正"。

---

## cleanrl/ppg_procgen.py

**知识图谱**：tags: `ppg/procgen/single-file/tested` · `tested_by → tests/test_procgen.py` · 被 `docs/rl-algorithms/ppg.md`（PPG 论文逐节对照文档）引用。

### 架构角色

**Phasic Policy Gradient（PPG，arXiv:2009.04416，OpenAI Procgen 论文）** 的单文件实现：把 PPO 的"策略与价值联合优化"拆成**两个阶段**——策略阶段（N_pi 次 PPO 更新，价值头对骨干 detach）+ 辅助阶段（冻结行为 KL 蒸馏 + 辅助价值头回归，把价值表征"塞进"共享骨干而不扰动策略）。核心动机：策略优化要"保守"（别破坏已有行为），价值回归要"贪婪"（充分利用样本）——两件事在标准 PPO 里互相拖后腿。

### 文件解剖（480 行）

| 行号 | 内容 |
|---|---|
| 19-98 | `Args`：PPG 专有（73-86）`n_iteration=32`（N_pi）/ `e_policy=1` / `v_value=1` / `e_auxiliary=6` / `beta_clone=1.0` / `num_aux_rollouts=4` / `n_aux_grad_accum=1`；`adv_norm_fullbatch=True`（57-58） |
| 101-105 | `layer_init_normed`：**按范数缩放**初始化（非 orthogonal）——照抄 PPG 官方代码 |
| 108-120 | `flatten01/unflatten01` + **自检函数** `flatten_unflatten_test`（116-120，L241 运行时真的会跑一次 assert） |
| 124-165 | ResidualBlock/ConvSequence 带 `scale` 参数逐级传递（128：`scale=np.sqrt(scale)`，151：再除 √nblocks） |
| 168-211 | `Agent` **三头**：actor（190, scale=0.1）/ critic（191）/ **aux_critic**（192）；关键方法 `get_pi_value_and_aux_value`（206-208） |
| 215-221 | 派生尺寸：`num_phases = num_iterations // n_iteration`（219）、`aux_batch_rollouts = num_envs × n_iteration`（220）、`assert v_value==1`（221） |
| 268-277 | storage + **aux_obs 以 uint8 存储**（274-276，注释 "Saves lot system RAM"） |
| 285-418 | **POLICY PHASE**：内层 32 次 PPO 迭代（288），单 epoch（e_policy=1, 350），全 batch 优势归一化（344-345） |
| 415-418 | 每 rollout 存入 aux buffer：`storage_slice = num_envs×(update-1) … num_envs×update`——**保持 [步,环境] 结构不展平** |
| 420-434 | 辅助阶段预处理：用**当前**策略对 aux buffer 全量前向，缓存 logits 到 `aux_pi`（431-433 no_grad）——"旧策略"快照 |
| 436-474 | **AUXILIARY PHASE**：e_auxiliary=6 轮，每次抽 4 条**完整 rollout**（439-441，L445 注释强调不用随机索引）；损失组装（449-461）；梯度累积（464-467）；OOM 兜底提示（469-472） |
| 475-477 | aux 损失日志 |

### 算法/工程要点

1. **detach 的方向性（200 vs 208）**——PPG 的灵魂在两行 detach 上：
   - 策略阶段 `get_action_and_value`：`self.critic(hidden.detach())`（200）——价值损失**不回传到共享骨干**，骨干只被策略梯度驱动（保持"行为保守"）；
   - 辅助阶段 `get_pi_value_and_aux_value`：critic 依然 detach，但 **aux_critic(hidden) 不 detach**（208）——辅助价值损失的梯度灌进骨干（此时有 KL 锚，不怕跑偏）。
   PPG = "什么时候允许价值梯度碰骨干"的调度协议。

2. **辅助阶段损失（449-461）**：
   ```python
   kl_loss        = KL(old_pi ‖ new_pi).mean()          # 455 行为锚：策略别漂
   aux_value_loss = MSE(aux_critic(s), returns)          # 458 辅助价值头回归（动骨干）
   real_value_loss= MSE(critic(s), returns)              # 457 主价值头校准（不动骨干，detach）
   joint_loss = aux_value_loss + beta_clone * kl_loss    # 459
   loss = (joint_loss + real_value_loss) / n_aux_grad_accum  # 461
   ```
   直觉：骨干在这 6 个 epoch 里"补课学价值"，同时 KL 项保证学完表征后策略行为与快照一致——表征变了，行为没变。

3. **完整 rollout 采样（439-447）**：`flatten01(aux_obs[:, aux_minibatch_ind])`——按环境维抽 4 条完整轨迹（256 步 × 4 env），而非 PPO 的随机索引 minibatch。PPG 论文发现辅助阶段用完整序列更稳（价值回归对时间连续性敏感）。

4. **梯度累积的 zero_grad 位置（464-467）**：`if (i+1) % n_aux_grad_accum == 0: clip → step → zero_grad`——zero_grad 必须在 step 之后、且在循环**内**（L467 注释原文 "This cannot be outside, else gradients won't accumulate"）。OOM 时换更大的 n_aux_grad_accum（469-472 的 RuntimeError 转译成人话）。

5. **aux buffer 内存工程（274-277, 417）**：`aux_batch_rollouts = 64 env × 32 iter = 2048 条` rollout × 256 步 × 64×64×3 uint8 ≈ 9.7 GB（uint8 若存 float32 要 ×4=39GB 不可行）——所以 275 行显式 `dtype=torch.uint8`，用时再 `.to(torch.float32)`（428, 443）。

### 与基础版（ppo_procgen.py）差异

- 更新结构：单一循环 → **phase（285）→ policy update（288）→ step 循环（295）→ aux phase（436）** 三层嵌套；
- 归一化：minibatch 级 `norm_adv` → **全 batch 级** `adv_norm_fullbatch`（344-345，L343 注释 "PPG code does full batch advantage normalization"）；
- epoch 数：update_epochs=3 → e_policy=1（策略阶段故意少次，配合 32 轮 phase）；
- 初始化：orthogonal → **norm-based scaling**（101-105，逐级 scale 递减 128/151/175——作者自己承认 L175 "Not fully sure about the logic" 照抄官方）；
- assert v_value==1（221）：多价值 epoch 官方也没实现，诚实声明。

### 模式与坑

- **flatten/unflatten 自检（116-120, 241）**：作者被形状 bug 咬过之后加的防呆 assert——训练启动时若 reshape 逻辑被改坏立即爆炸而非默默错位。值得抄的模式。
- **aux_pi 的内存**：`[256 步, 2048 rollout, n_actions]` 的 float32 logits（424）——Breakout 4 动作约 8.4 GB，走 CPU 分批计算（425-434 每 4 条一批）。
- **aux 阶段结束后 aux buffer 不清空**（下一 phase 直接覆盖 417），依赖 slice 索引正确性——`storage_slice`（416）的算术 (update-1)*num_envs 是唯一正确写法，改动顺序会静默错位（所以有自检函数）。
- **kl_loss 日志在循环外引用循环变量（475）**：若 e_auxiliary 循环体从未执行（不可能但理论上），会 NameError——cleanrl 式"实用主义"代码。

---

## cleanrl/qdagger_dqn_atari_impalacnn.py

**知识图谱**：tags: `entry-point/dagger/distillation/impalacnn/tested` · 出边最多的高级变体：`imports → dqn_atari.py（教师模型）/ cleanrl_utils/buffers.py / cleanrl_utils/evals/dqn_eval.py / atari_wrappers.py` · 有 JAX 姊妹版 `qdagger_dqn_atari_jax_impalacnn.py`。

### 架构角色

**QDagger（arXiv:2206.12894，"DQfD 式在线蒸馏"）**：把 HuggingFace 上训练好的 DQN 教师下载下来，**教师在线采样填充 replay buffer**，学生（ImpalaCNN Q 网络）以 **TD 损失 + KL 蒸馏损失** 联合训练，蒸馏权重随学生水平自适应退火。它是 cleanrl 里"**RL+模仿学习混合**"与"**HF 模型生态复用**"（`cleanrl/{env}-dqn_atari-seed1` 直接当教师用）的代表。三段式流程：教师 buffer 填充 → 离线蒸馏 → 在线联合训练。

### 文件解剖（466 行）

| 行号 | 内容 |
|---|---|
| 19-28 | **跨文件 import**：`from cleanrl.dqn_atari import QNetwork as TeacherModel`（19）——教师结构直接复用 dqn_atari |
| 31-98 | `Args`：QDagger 专有（86-98）`teacher_policy_hf_repo / teacher_steps=5e5 / offline_steps=5e5 / temperature=1.0` |
| 101-122 | make_env：gymnasium + 完整 atari 预处理链 |
| 126-160 | ResidualBlock/ConvSequence（ImpalaCNN，同 procgen） |
| 164-184 | `QNetwork`：ImpalaCNN 骨干 + 256 FC → Q 值 |
| 192-195 | `kl_divergence_with_logits`：手写 KL(teacher‖student)（softmax·(log_softmax 差) 求和） |
| 199-202 | `assert num_envs == 1`（200）；教师 repo 默认名拼接（201-202） |
| 241-247 | 教师加载：`hf_hub_download` → `TeacherModel` 实例 → `load_state_dict` → `.eval()` |
| 249-260 | 教师评估 10 回合，记录 baseline 回报 |
| 262-288 | **阶段① 教师 buffer 填充**：教师 ε-greedy（线性退火 276）在线跑 50 万步，`teacher_rb.add(...)` |
| 290-339 | **阶段② 离线蒸馏**：从 teacher_rb 采样，`loss = q_loss + 1.0 × distill_loss`（306），每 10 万步存档+评估（322-339） |
| 341-357 | 学生自建 rb，重建环境 |
| 358-437 | **阶段③ 在线联合训练**：学生 ε-greedy 采样；`distill_coeff` 自适应（399-402）；`loss = q_loss + distill_coeff × distill_loss`（415） |
| 439-463 | save/evaluate/push_to_hub |

### 算法/工程要点

1. **教师是"黑盒 + 权重"而非 buffer（262-264 注释）**：代码假设拿不到教师的 replay buffer（现实约束），于是教师亲自下场跑 50 万步重新采集——注释指向论文 Fig. A.19 的实验设定。教师的 ε 从 1.0 退火到 0.01（276），保证 buffer 覆盖面。

2. **温度化蒸馏（297, 303）**：`teacher_q / temperature` 后做 logit 级 KL——温度 1.0 默认，理论上可调软硬。KL 用手写版而非 `F.kl_div`（192-195）：`Σ softmax(t)·(log_softmax(s) − log_softmax(t))`，方向是 **KL(teacher‖student)**（on-policy 蒸馏的标准方向，mode-covering）。

3. **自适应蒸馏退火（399-402）**，阶段③ 的灵魂：
   ```python
   if len(episodic_returns) < 10: distill_coeff = 1.0
   else: distill_coeff = max(1 − mean(学生近10回合) / mean(教师回报), 0)
   ```
   学生远逊教师 → coeff≈1（全力模仿）；学生追平教师 → coeff→0（纯 RL 自我改进）；**超过教师后 max(·,0) 钳住不为负**。教师评估 baseline（249-260）在这里派上用场。

4. **异构蒸馏**：教师是 NatureCNN（dqn_atari 的 QNetwork），学生是 ImpalaCNN——**结构不同，蒸馏发生在 Q 值 logits 层**，与架构无关。这是 logit 蒸馏相对 feature 蒸馏的工程优势。

5. **三段共用一套 TD 骨架（294-301 vs 403-410）**：离线/在线两阶段的 TD 损失代码几乎相同（target_network max → td_target → MSE），差别仅在数据来源（teacher_rb vs rb）与蒸馏系数（常数 1.0 vs 自适应）——cleanrl 用复制而非参数化保持每段自明。

### 与基础版（dqn_atari.py）差异

- 网络：NatureCNN → **ImpalaCNN**（名字里的 impalacnn）；
- 损失：纯 TD → **TD + KL 蒸馏**双项；
- 数据：单 rb → **teacher_rb（离线段）+ rb（在线段）**；
- 流程：单循环 → **三段式**（填 teacher buffer → 离线 → 在线）；
- `import gymnasium`（8）+ 五元组 API——与 ppo_atari_multigpu 同代的 gymnasium 系文件。

### 模式与坑

- **🚨 global_step 计步 bug（358-359）**：`for global_step in track(range(args.total_timesteps)): global_step += args.offline_steps`——循环变量每轮 +1 的同时又手动 +50 万，第一轮迭代后 global_step 就跳到 ~100 万，`linear_schedule`（361）的 ε 立即贴地板（退火期 `0.1×1e7=1e6` 步在两次迭代内"过完"）。本意显然是把 offline 步数计入全局步（`global_step` 从 50 万起步），但 `for range(1e7)` 的循环次数并未相应缩短，日志横轴严重失真。上游已知瑕疵，读者复现时注意日志解释。
- **裸 `except:`（25-28）**：HF 下载失败统一转 RuntimeError——吞掉所有异常类型（含 KeyboardInterrupt），cleanrl 代码卫生的减分项。
- **默认 `num_envs=1` 强制 assert（200）**：蒸馏逻辑按单环境写死。
- **教师 repo 命名约定（202）**：`cleanrl/{env_id}-{exp_name}-seed1`——依赖 cleanrl 官方 HF 组织的模型命名规范，换教师需显式传 `--teacher-policy-hf-repo`。

---

## cleanrl/ppo_atari_envpool_xla_jax.py

**知识图谱**：tags: `ppo/jax/flax/xla/tested` · `tested_by → tests/test_envpool.py` · 有 benchmark 页 `docs/benchmark/ppo_atari_envpool_xla_jax.md`。

### 架构角色

PPO Atari envpool 的 **JAX/Flax 移植版**，cleanrl JAX 栈的入门文件：模型用 flax.linen 写，rollout/GAE/更新全部 `@jax.jit` 编译，学习率退火经 `optax.inject_hyperparams` 进编译图，envpool 通过 **`envs.xla()` 接口**把环境步进也编译进 XLA 计算图。范式从 PyTorch 的"eager 每步调度"换轨到"整段编译一次调度"。它也是 `ppo_atari_envpool_xla_jax_scan.py`（下节）的对照基线——两文件的差异恰好是 **"jit 内 Python 循环展开" vs "lax.scan 结构化循环"** 的教科书对比。

### 文件解剖（452 行）

| 行号 | 内容 |
|---|---|
| 21-25 | 三个环境变量：`XLA_PYTHON_CLIENT_MEM_FRACTION=0.6`（OOM workaround，注释链接 jax#6332）、deterministic reductions、cudnn deterministic |
| 28-89 | `Args`：与 envpool 版超参一致（tyro 生态不变） |
| 92-141 | **三个分离模块**：`Network`（92-127，NHWC 卷积，95 行 transpose NCHW→NHWC）、`Critic`（130-133）、`Actor`（136-141，action_dim 作为 dataclass 字段） |
| 144-168 | 三个 `@flax.struct.dataclass`：`AgentParams`（144-148，参数三包）、`Storage`（151-160，九字段 rollout 缓冲）、`EpisodeStatistics`（163-168）——**pytree 节点，可整体进出 jit** |
| 195-199 | 播种：`jax.random.PRNGKey` + `split(key, 4)`（显式随机键，对照 torch 的全局种子） |
| 202-220 | envpool.make + `handle, recv, send, step_env = envs.xla()`（220，**XLA 接口四件套**） |
| 222-237 | `step_env_wrappeed`（原文拼写）：episode 统计全部用 jnp 运算改写（226-236）——因为它要被编译 |
| 241-245 | `linear_schedule(count)`：**按 optimizer 步计数**（count // (num_minibatches×update_epochs)），交由 optax 调用 |
| 247-267 | `TrainState.create`：`apply_fn=None`（245），`tx=optax.chain(clip_by_global_norm, inject_hyperparams(adam)(lr=schedule))`（258-263）；265-267 monkey-patch `network.apply = jax.jit(...)` |
| 281-307 | `get_action_and_value`（jit）：**Gumbel-softmax 采样**（293-297）+ `storage.replace(...at[step].set(...))`（300-306） |
| 309-325 | `get_action_and_value2`（jit）：手工 entropy（320-323，logsumexp 归一化 + p·log_p） |
| 327-350 | `compute_gae`（jit）：**Python reversed 循环**（339-348）——trace 时逐步展开 |
| 352-401 | `update_ppo`（jit）：`jax.value_and_grad(has_aux=True)`（385）+ Python 双层循环（386-399）+ `jax.random.permutation`（388） |
| 409-418 | `rollout`（jit）：num_steps 循环展开（411-417） |
| 420-449 | 主循环：`rollout → compute_gae → update_ppo` 三行（422-430）+ 日志；439 行从 `opt_state[1].hyperparams` 里**读回当前学习率** |

### 算法/工程要点：JAX vs PyTorch 范式差异清单

1. **模型即函数**：没有 `nn.Module` 实例状态，`Network` 只是"参数→输出"的纯函数描述；参数存在 `AgentParams` 里显式传递（291-299 每次 apply 都带 params）——与 PyTorch `agent(x)` 隐式持参对照。

2. **采样不用 Categorical（293-297）**：`argmax(logits − log(−log(u)))` 是 Gumbel-max 技巧——jax 里没有 `torch.distributions` 的 sample，用均匀噪声+变换实现同分布采样（注释链接 stats.stackexchange）。logprob 则用 `log_softmax` 手工索引（298）。

3. **学习率退火进图（241-245, 258-263）**：PyTorch 版每 iteration 手改 `optimizer.param_groups[0]["lr"]`；JAX 版把 schedule 函数交给 `optax.inject_hyperparams`，学习率成为 **optimizer state 的可微/可追踪字段**，日志时从 `agent_state.opt_state[1].hyperparams["learning_rate"]` 读回（439）——退火逻辑编译期就定了，运行期零 Python 干预。

4. **`envs.xla()` 的意义（220）**：envpool 提供 XLA 自定义算子封装——`step_env(handle, action)` 返回的 (handle, 四元组) 都是 jnp 数组，环境步进成为计算图节点。于是 **"采样→存储→更新"可以整段 jit**（409-418 的 rollout 里 `step_env_wrappeed` 与网络前向交错执行）。代价：`recv/send` 两件套在此版未用（scan 版也不直接用，它们是外部异步接口）。

5. **jit 内的 Python for = 编译期展开**：`compute_gae` 的 reversed 循环（339）、`update_ppo` 的 4 epoch×4 minibatch 双层循环（386-399）、`rollout` 的 128 步循环（411）——trace 时全部静态展开成一张大图。**编译几分钟，运行飞快**；代价是编译时间与循环长度的乘积关系。

6. **随机性显式键控（295-297, 387-388）**：所有随机操作传 `key` 并 `split` 出子键；采样位置、permutation 各持独立键，key 作为函数返回值传出（307, 401）延续链——可复现性精确到每次随机调用。

### 与基础版（ppo_atari_envpool.py）差异

| 维度 | PyTorch 版 | JAX 版 |
|---|---|---|
| 网络组织 | Agent 单模块（actor/critic 子层） | Network/Actor/Critic **三模块** + AgentParams 参数包 |
| 采样 | `Categorical.sample()` | Gumbel-max 手工采样（293-297） |
| 优化器 | Adam + 手动改 lr | optax.chain(clip, adam) + inject_hyperparams |
| 梯度 | `loss.backward()` + `optimizer.step()` | `jax.value_and_grad` 一次返回 (loss, grads)，`apply_gradients` 纯函数式更新 |
| 环境 | CPU↔GPU 每步拷贝 | `envs.xla()` 进图，数据不出设备 |
| 循环 | Python 每步调度 | jit 整段编译，主循环 3 行（422-430） |
| 随机性 | 全局种子 | PRNGKey 显式传递 |
| 简化 | clip_vloss 分支（303-314） | **没有 clip_vloss 分支**（379 直接 MSE）；**没有 target_kl 早停**（jit 图内无法 break） |

### 模式与坑

- **`apply_fn=None`（252）**：TrainState 本应持有 apply_fn，但这里网络三模块分立、apply_fn 无单一归属，干脆置 None、直接 jit 各模块 apply（265-267）——非典型用法，`apply_gradients` 不依赖它。
- **`step_env_wrappeed` 拼写错误**（222）——上游原文如此，双重封装的 wrapper 拼错成 wrappeed，已成 cleanrl 名梗。
- **Args 里 `clip_vloss=True`、`torch_deterministic=True` 是摆设**：JAX 版既无 clip_vloss 分支也无 torch——字段保留只为命令行兼容，勿被 docstring 误导。
- **`agent_state.opt_state[1]`（439）**：optax.chain 的 state 是元组，[1] 索引 adam 那一环——链条顺序改变时此索引会错位，改动 optax.chain 时同步检查。
- **三模块分离的动机**：actor/critic 各自独立参数包使得后续（如 Brax 系、PNP）对"冻结某头"类实验友好；代价是 init 时要三段接力（250-257，actor.init 需要 network 的输出作输入）。

---

## cleanrl/ppo_atari_envpool_xla_jax_scan.py

**知识图谱**：tags: `ppo/jax/lax-scan/xla/tested` · **双测试**：`tested_by → tests/test_envpool.py` **和** `tests/test_jax_compute_gae.py`（GAE scan 重构有专门等价性护栏，见第 12 节）· `benchmark/zoo.sh` 引用。

### 架构角色

XLA JAX 版的 **`jax.lax.scan` 重构版**，全库吞吐最高的 PPO 实现之一：把 rollout 步进、GAE 反向递推、epoch/minibatch 更新三层循环**全部改成 `lax.scan`**（结构化的可融合循环），替代 jit 内的 Python for 展开。与上一节合起来看：`xla_jax.py` 证明"能编译"，`xla_jax_scan.py` 证明"能编译得更好"。它还是 JAX 系里唯一带 `save_model/evaluate/push_to_hub` 完整闭环的 PPO（485-519）。

### 文件解剖（522 行）

与 `xla_jax.py` 相同的部分（模块 118-195、`step_env_wrappeed` 237-252、schedule 256-260、TrainState 262-282、`make_env` 99-115 抽成函数供 evaluate 复用）不再重复，只列**差异结构**：

| 行号 | 内容 |
|---|---|
| 99-115 | `make_env` 提升为独立函数（thunk 工厂）——save_model 后 evaluate 要重建环境（505 传入） |
| 320-329 | `compute_gae_once(carry, inp, gamma, gae_lambda)`：**单步转移函数** + `partial` 固定超参（329） |
| 331-352 | `compute_gae`（jit）：dones/values 与 next 拼接后切片配对（343-344），`jax.lax.scan(..., reverse=True)` **反向扫描**（345-347） |
| 354-375 | `ppo_loss` / `ppo_loss_grad_fn` 提到**模块级**（不再嵌套在 update_ppo 里）——scan 的 scan_fn 里不能闭包 jit |
| 377-419 | `update_ppo`（jit）：三层嵌套结构 |
| 383-414 | `update_epoch`（scan_fn）：`jax.tree_map(flatten/shuffle)` 整树重排（396-397） |
| 390-394 | `convert_data`：整树 permutation + reshape `(num_minibatches, -1)`（brax 技巧，390 注释） |
| 399-413 | `update_minibatch`（scan_fn）：梯度计算+apply_gradients |
| 411-413 | 内层 `scan(update_minibatch, agent_state, shuffled_storage)`——**Storage pytree 沿首维广播成 minibatch 序列** |
| 416-418 | 外层 `scan(update_epoch, (agent_state,key), (), length=update_epochs)` |
| 427-443 | `step_once`：单步 rollout 转移函数（evojax 出处注释 427），返回单步 Storage 切片 |
| 445-451 | `rollout = lax.scan(step_once, carry, (), max_steps)` + 双层 partial 固定 env_step_fn/max_steps |
| 474-478 | 日志取 `[-1,-1]`——scan 输出是 `[epochs, minibatches]` 矩阵，取最后一个 |
| 485-519 | save_model：`flax.serialization.to_bytes([vars(args), [三包参数]])`（487-499）+ evaluate + push_to_hub |

### 算法/工程要点

1. **scan 的心智模型**：`lax.scan(fn, init_carry, xs)` = "把 fn 沿 xs 首维跑 N 次，carry 链式传递，输出堆叠成 `[N, ...]`"。它和 jit 内 Python for 的区别：for 是**编译期展开**（图大小 ∝ 循环次数），scan 是**图里真的循环结构**（图大小恒定，XLA 可做循环融合/软件流水）。本文件三个应用：
   - **rollout（445-449）**：carry = (agent_state, episode_stats, obs, done, key, handle) 六元组链，xs=`()` + `max_steps` 纯计数；
   - **GAE 反向（345-347）**：`reverse=True` 从 t=T-1 往回扫，carry=上一步的 lastgaelam；
   - **更新双层 scan（411-418）**：外层 epoch 计数、内层 minibatch 序列。

2. **GAE 的 scan 化数学（342-347）**：把 `next_done/next_value` 拼在 dones/values 尾部后，`(dones[1:], values[1:], values[:-1], rewards)` 四个数组**按 t 对齐**成转移五元组（nextdone_t, nextvalue_t, value_t, r_t）——`values[:-1]` 是当前值、`values[1:]` 是下一值。单步函数（320-327）于是与 Python 版循环体逐字对应：`delta = r + γV(s′)(1−done) − V(s)`，`A_t = δ_t + γλ(1−done)·A_{t+1}`。carry 就是 lastgaelam。**这个对齐技巧是 scan 化时序递推的通用范式**（也出现在 Brax/PPO 等所有 JAX RL 库）。

3. **整树 shuffle 的 minibatch（387-397）**：不用索引数组切 minibatch，而是 `jax.tree_map(λx: permutation(x).reshape(num_minibatches, -1, ...), flatten(storage))`——整棵 Storage pytree 用**同一个 subkey** 重排（保证 obs/actions/logprobs 对齐），reshape 后首维即 minibatch 序列，直接喂 scan。比索引版本对 XLA 更友好（无 gather 索引张量）。

4. **grads 也进 scan 输出（409, 413）**：`update_minibatch` 把 grads 一起返回（调试用），于是日志矩阵里能看每步梯度——代价是内存（堆叠全部梯度）；生产可删。

5. **save 格式（487-499）**：`[vars(args), [network_params, actor_params, critic_params]]` 整体序列化——**超参与权重同文件**，enjoy/evaluate 时能完整重建（对照 ppo_trxl/enjoy.py:33-35 的同类设计）。

### 与 xla_jax.py（非 scan 版）差异

| 维度 | xla_jax.py | xla_jax_scan.py |
|---|---|---|
| rollout | jit 内 Python for 展开（411） | `lax.scan(step_once)`（446-448） |
| GAE | Python reversed 循环展开（339） | `lax.scan(reverse=True)`（345） |
| 更新 | 双层 Python for（386-399） | 双层嵌套 scan（411-418） |
| minibatch | 索引切片 `b_inds[start:end]` | 整树 permutation+reshape（391-397） |
| storage 更新 | `storage.replace(...at[step].set(...))` 逐槽 | step_once 构造单步 Storage，scan 自动堆叠（433-442） |
| get_action_and_value | 更新 storage 并返回（281-307） | 纯函数返回 action/logprob/value（284-300） |
| ppo_loss 位置 | 嵌套在 update_ppo 内（364） | 模块级（354-373） |
| save/eval/HF | 无 | 有（485-519） |
| 日志取值 | 标量 | `[-1,-1]` 矩阵索引（474-478） |
| 编译产物 | 图大（展开∝步数×epoch） | 图小（循环结构），编译更快、运行同等快 |

### 模式与坑

- **scan 的输出形状陷阱**：内层 scan 输出 `[num_minibatches, ...]`，外层再堆一层 `[update_epochs, num_minibatches, ...]`——所以 `loss[-1,-1]`（478）取最后 epoch 最后 minibatch；写成 `loss[-1]` 会得到向量，`.item()` 直接爆炸。
- **`()` 作 xs（417, 447）**：scan 允许 `length=` 显式指定循环次数、xs 传空元组——纯计数循环的惯用写法（brax/evojax 同款）。
- **双层 partial（451）**：`rollout = partial(rollout, step_once_fn=partial(step_once, env_step_fn=step_env_wrappeed), max_steps=args.num_steps)`——用偏函数把配置烘进函数签名，等效于"编译期常量"；JAX 里替代闭包的手法（闭包会导致重复 trace）。
- **为什么 GAE 有专门单测**：scan 版 GAE 改写了循环结构，等价性并非显然——`tests/test_jax_compute_gae.py` 用 `==.all()`（不是 allclose！）断言与 Python 循环**逐位一致**，因为两者浮点运算顺序完全相同（先算 delta 再乘加，无融合重排）。这依赖 XLA 不做重结合优化——是激进的强断言（见第 12 节）。
- **Storage 的 returns/advantages 初始化为 `zeros_like(reward)`（440-441）**：scan 堆叠的"占位字段"，真正值由后续 compute_gae 的 replace 填充——pytree 字段必须形状一致才能堆叠，占位是必要仪式。

---

## cleanrl/dqn_jax.py

**知识图谱**：tags: `dqn/jax/flax/single-file-implementation/tested` · 出边：`imports/calls → cleanrl_utils/buffers.py:ReplayBuffer`（**JAX 版仍用 torch 实现的 buffer**）、`depends_on → cleanrl_utils/evals/dqn_jax_eval.py + huggingface.py` · `tested_by → tests/test_classic_control_jax_gymnasium.py` · 被 `benchmark/zoo.sh` 引用。

### 架构角色

DQN 的 JAX/Flax 版（默认 CartPole-v1，classic control 系）：单文件展示 **off-policy + JAX 的最小组合**——Q 网络是 linen 模块，TD 损失经 `jax.value_and_grad` 一步求梯度，目标网络参数**寄生在扩展的 TrainState 字段里**（`class TrainState(TrainState): target_params`，102-104——cleanrl JAX 系最著名的惯用法）。与两个 PPO JAX 版相比，它保留了 Python 主循环（每步调度），代表"**JAX 求梯度 + Python 控制流**"的中间形态。

### 文件解剖（269 行）

| 行号 | 内容 |
|---|---|
| 21-70 | `Args`：DQN 标准超参（buffer=1e4, batch=128, target_freq=500, lr=2.5e-4, ε: 1→0.05 over 50%） |
| 73-85 | `make_env`：gymnasium 单环境 + RecordEpisodeStatistics |
| 89-99 | `QNetwork(action_dim)`：`@nn.compact` 三层 MLP（120→84→action_dim）——action_dim 走 dataclass 字段 |
| 102-104 | `class TrainState(TrainState): target_params: flax.core.FrozenDict`——**继承扩展** |
| 106-108 | `linear_schedule`（与 dqn.py 逐字相同） |
| 133-137 | 播种：`jax.random.PRNGKey` + split |
| 140-157 | 建环境 / QNetwork / `TrainState.create(apply_fn=q_network.apply, params=..., target_params=..., tx=optax.adam)`（147-152） |
| 154-156 | `q_network.apply = jax.jit(...)` monkey-patch；156 行注释解释 target 初始化无需复制（同 key 同 obs 的 init 确定性） |
| 158-164 | `ReplayBuffer(..., "cpu", ...)`——torch 张量 buffer（复用 cleanrl_utils） |
| 166-179 | **`update`（jit）**：目标网前向→max→td_target（168-170）；`mse_loss` 内 gather（174）；`value_and_grad(has_aux)` → `apply_gradients`（177-178） |
| 185-240 | 主循环：ε-greedy（187-193，`jax.device_get` 取回 CPU 才能喂 env）→ env.step → rb.add → 每 10 步 `update`（218-228）→ 每 500 步目标网替换（237-240） |
| 242-266 | save_model（`flax.serialization.to_bytes(q_state.params)`，245）+ evaluate + push_to_hub |

### 算法/工程要点

1. **目标网络的 TrainState 寄生（102-104, 147-152, 237-240）**——本文件最重要的一行代码：
   ```python
   class TrainState(TrainState):
       target_params: flax.core.FrozenDict
   ```
   flax 的 `TrainState` 是 pytree dataclass，子类加一个字段即把目标参数**并入同一棵树**——好处：(a) target_params 随 q_state 一起进 jit 函数，无需单独传参；(b) 一次 `q_state.replace(...)` 更新两者，状态一致性由类型系统保证。TD3 版（113-114）同款，三个 TrainState 各带 target。
   更新时 `optax.incremental_update(params, target_params, tau)`（239）：`update = target + τ·(params − target)`，τ=1.0 即硬替换——比 PyTorch 版逐参数 `copy_` 循环简洁得多。

2. **一次 jit 完成整步优化（166-179）**：PyTorch 的 `loss.backward(); optimizer.step()` 两阶段在 JAX 里是 `value_and_grad` 返回 grads → `apply_gradients` 纯函数式产出**新** q_state（函数式更新，无原地副作用）。`has_aux=True` 让 mse_loss 顺便带出 q_pred 用于日志（175, 179）。

3. **gather 的 jnp 写法（174）**：`q_pred[jnp.arange(q_pred.shape[0]), actions.squeeze()]`——jnp 没有 `torch.gather` 的布局灵活性，用 fancy indexing 等价实现"取已执行动作的 Q 值"。

4. **torch buffer × jax 模型的混血（158-164, 219-228）**：ReplayBuffer 是 torch 实现（数据在 CPU torch 张量），喂 jit 函数前 `.numpy()`（222-227）。这是 cleanrl JAX 系的务实选择——重写 buffer 无教学价值，复用降低维护面。代价是每步 numpy 转换的边界开销（对 CartPole 这种轻环境无所谓）。

### 与基础版（dqn.py）差异

| 维度 | dqn.py | dqn_jax.py |
|---|---|---|
| 网络 | `nn.Module`（120-84-A） | linen `@nn.compact` + dataclass 字段传 action_dim |
| 目标网 | 独立实例 + `load_state_dict` | **TrainState.target_params 字段** + incremental_update |
| 优化步 | backward + step 分离 | jit 函数内 value_and_grad + apply_gradients 一步 |
| buffer | torch ReplayBuffer | 同一个 torch ReplayBuffer（.numpy() 过桥） |
| 随机数 | random.random() | 同（ε-greedy 仍在 Python 侧，187-189） |
| save | torch.save(state_dict) | flax.serialization.to_bytes |

### 模式与坑

- **156 行的反直觉注释**："This step is not necessary as init called on same observation and key will always lead to same initializations"——`incremental_update(params, target, 1)` 在这里**确实被调用**但注释说明其冗余性（init 确定性保证两包参数已相同）。读者困惑点：为什么不删？——保留这行让"target 同步机制"在代码里可见，教学优先。
- **ε-greedy 的 `random.random()`（188）不走 PRNGKey**：探索决策在 Python 侧，JAX 只管前向——控制流留在 host 是 cleanrl JAX 系的普遍边界（对比 xla_jax 版把采样也搬进图）。
- **`q_values.argmax(axis=-1)` 后必须 `jax.device_get`（192-193）**：jnp 数组不能直接喂 gymnasium 的 env.step——忘掉这步会在 num_envs>1 时静默出错。
- **CI 对应 `test_classic_control_jax_gymnasium.py`**：跑 CartPole 数千步验证不崩——DQN 的 JAX 冒烟测试。

---

## cleanrl/td3_continuous_action_jax.py

**知识图谱**：tags: `td3/jax/flax/single-file-implementation/tested` · 出边同 dqn_jax（buffers/evals/huggingface）· `tested_by → tests/test_mujoco.py` · benchmark 页 `docs/benchmark/td3.md`。

### 架构角色

TD3（Twin Delayed DDPG，arXiv:1802.09477）的 JAX/Flax 版（默认 Hopper-v4，MuJoCo 连续控制）：三网络（actor + 双 critic）× 各自 target = **六个参数包**，组织为三个扩展 TrainState；目标策略平滑噪声在 jit 内用 `jax.random` 生成。它是观察"**多智能体组件（多价值网络）在 JAX 函数式范式下如何编排**"的最佳样本——update_critic/update_actor 两个 jit 函数的签名即数据流图。

### 文件解剖（361 行）

| 行号 | 内容 |
|---|---|
| 21-66 | `Args`：TD3 超参（lr=3e-4, τ=0.005, batch=256, policy_noise=0.2, exploration_noise=0.1, noise_clip=0.5, policy_frequency=2） |
| 84-93 | `QNetwork`：`__call__(x, a)` 拼接 obs+action → 256-256-1 |
| 96-110 | `Actor(action_dim, action_scale, action_bias)`：tanh 输出 × scale + bias（109）——**动作边界作为 dataclass 静态字段** |
| 113-114 | TrainState 子类（target_params 字段，同 dqn_jax） |
| 148-149 | `max_action`；**`envs.single_observation_space.dtype = np.float32`**（149，hack：修正 buffer dtype） |
| 161-184 | **三个 TrainState**：actor_state（166-171）、qf1_state/qf2_state（172-184），init 时 obs 与 `envs.action_space.sample()` 双输入 |
| 185-186 | `actor.apply = jax.jit(...)`、`qf.apply = jax.jit(...)`（**注意：qf 是同一个类的两个 state 共享一个 jit 化 apply**） |
| 188-230 | **`update_critic`（jit）**：噪声生成（202-210）→ 目标动作（211-215）→ 双 Q min（216-219）→ mse_loss → 双 value_and_grad → 双 apply_gradients（221-228） |
| 232-254 | **`update_actor`（jit）**：actor_loss = −Q1(s,π(s)).mean()（239-240）→ 梯度更新 actor → **三个 target 一起软更新**（244-253） |
| 259-270 | 探索策略：learning_starts 前均匀随机；之后 actor + N(0, max_action×0.1) + clip（262-270，**numpy 噪声在 Python 侧**） |
| 294-315 | 训练段：每步 update_critic；`policy_frequency=2` 才 update_actor（309-315）——延迟策略更新 |
| 326-358 | save（三包参数 list 序列化，330-336）+ evaluate + push_to_hub |

### 算法/工程要点

1. **TD3 三件套在 jit 签名里的映射**：
   - **目标策略平滑（203-215）**：`clip(N(0, policy_noise)·, ±noise_clip) × action_scale` 加到目标动作上再 clip 到动作界——注意噪声乘了 `actor.action_scale`（209），让噪声尺度随动作幅度缩放（MuJoCo 各维动作界不同）。**噪声在 jit 内用 jax.random 生成**（202），key 显式传递——对照 dqn_jax 的 Python 侧 random：噪声参与梯度计算目标，必须进图。
   - **双 Q 取 min（216-218）**：`jnp.minimum(qf1_next_target, qf2_next_target)`——对抗价值高估。
   - **延迟更新（309-315 + 244-253）**：actor 每 2 步更新一次；**三个 target 的软更新全部挂在 update_actor 里**（244-253）——巧妙：软更新频率自动跟随 policy_frequency，语义上 TD3 的 target 属于"慢时钟"。
2. **共享 mse_loss 闭包（221-226）**：两个 critic 的损失函数完全相同（同一 next_q_value 目标），写一个闭包对 qf1/qf2 的 params 各调一次 `value_and_grad`——代码无重复，梯度各自独立（225-226）。
3. **actor 的动作边界（96-110, 161-165）**：tanh 域 [-1,1] × scale + bias 映射到 [low, high]；scale/bias 是 `jnp.array` 的 dataclass 字段——**pytree 里的静态值**（jit 编译期常量），所以 jit 函数内可裸引用 `actor.action_scale`（209）。

### 与基础版（td3_continuous_action.py）差异

| 维度 | PyTorch 版 | JAX 版 |
|---|---|---|
| 状态组织 | 6 个模块对象（actor/qf1/qf2 + 3 target） | 3 个 TrainState（target_params 内嵌） |
| 目标噪声 | torch.randn（eager，每次 python 调用） | jax.random + key 传递（jit 内，200-202 有 TODO 想预生成 key） |
| 软更新 | 手写 lerp 循环 | `optax.incremental_update(params, target, τ)` ×3（244-253） |
| actor 梯度 | `-(qf1(obs, actor(obs))).mean()` 手动 freeze critic（`torch.no_grad`/requires_grad 开关） | 同一公式，但 critic 的 params 来自 qf1_state（闭包捕获），JAX 无需 freeze——**params 是纯输入，不更新就不动** |
| 探索噪声 | numpy（相同） | numpy（相同，267） |

### 模式与坑

- **`envs.single_observation_space.dtype = np.float32`（149）**：MuJoCo 观测空间默认 float64 声明，ReplayBuffer 按空间 dtype 建张量会导致 float64 buffer × float32 jnp 参数的 dtype 冲突——这行 monkey-patch 是 JAX 系适配 gymnasium 的经典 hack。
- **actor_loss 里只用了 qf1（240）**：TD3 原文用 Q1 更新策略即可（min 只用于 TD 目标）——正确实现，但读代码时常有人以为漏了 min。
- **update_actor 里同时更新 critic 的 target（248-253）**：三个软更新捆在一起，若把 policy_frequency 改成 1 会静默改变 critic target 更新频率——改动参数时留意耦合。
- **TODO 注释（200-201）**：作者自己标注"可预生成随机 key 提效"——每次 update_critic split 一次 key 的开销在长训练里可测。

---

## cleanrl/ppo_trxl/enjoy.py

**知识图谱**：tags: `entry-point/evaluation/inference/pretrained-model` · complexity: moderate（15 文件里最低）· 出边：`imports → cleanrl/ppo_trxl/ppo_trxl.py`、`calls → make_env / Agent` · 被 `docs/rl-algorithms/ppo-trxl.md` documents。

### 架构角色

**PPO + Transformer-XL**（记忆健身房 Memory Gym，长时序记忆任务）的**推理/可视化入口**：从本地或 HF Hub 加载 checkpoint，重建 Agent 与 TrXL 的**片段记忆机制**（memory 槽、因果 mask、滑窗索引），人肉观看一个完整评估回合。它是 cleanrl 里罕见的"纯消费端"文件——零训练逻辑，但把训练侧最复杂的记忆索引机制原样复现一遍，是理解 `ppo_trxl.py` 记忆管理的钥匙。

### 文件解剖（91 行）

| 行号 | 内容 |
|---|---|
| 9-14 | `Args`：`hub: bool`（HF 还是本地）、`name`（模型文件名，默认 Endless-MortarMayhem-v0_12.nn） |
| 20-30 | 模型路径解析：`hf_hub_download(repo_id="LilHairdy/cleanrl_memory_gym")`（24）或直接用本地路径（30） |
| 33-35 | `checkpoint = torch.load(path)`；`args = checkpoint["args"]`；**`type("Args", (), args)` 动态造命名空间对象**（35）——从 dict 恢复属性访问 |
| 38-48 | `make_env(..., "human")` 渲染模式建环境；`max_episode_steps` 三级兜底（spec → env → 1024，43-47，Memory Gym 的 -1 需手动指定） |
| 51-55 | action_space_shape 按 Discrete/MultiDiscrete 分叉（52）；`Agent(args, obs_space, act_shape, max_steps)` + `load_state_dict`（54-55） |
| 58-66 | **TrXL 记忆三件套重建**：memory `[1, T, L, D]`（58）；`memory_mask = tril(…, diagonal=-1)` 严格下三角（59）；`repetitions`（60-62）+ `memory_indices` 滑窗（63-65）拼接（66） |
| 69-85 | 单回合循环：取第 t 步的记忆窗口（74）；`t_` 钳制处理序列开头（75）；前向拿 action 和 new_memory（79）；写回 memory 槽（80）；env.step + render |
| 87-90 | 打印回合回报（兼容两种 info 结构，87-90） |

### 算法/工程要点

1. **checkpoint 自包含设计（33-35, 54-55）**：权重 + 训练超参存一个文件——enjoy 侧 `type("Args", (), args)` 一行动态恢复 `args.trxl_num_layers` 等字段访问（58-59 直接使用）。对照 xla_jax_scan 的 save（487-499 存 `[vars(args), params]`）——cleanrl 的模型档案哲学：**离开超参的权重无意义**。
2. **TrXL 记忆机制三件套（58-66）**，本文件的硬核部分：
   - **memory 槽 `[1, max_episode_steps, num_layers, dim]`**：每个时间步保存**每层**的 K/V 表征（Transformer-XL 的片段级递归记忆）；
   - **memory_mask（59）**：`tril(diagonal=-1)` 严格下三角——注意力只能看**之前**的段，不含当前（防泄漏）；
   - **memory_indices（63-66）**：`[t, t+L)` 滑窗 + 前置 `repetitions`（把序列开头不足 L 长度的位置用索引 0 填充对齐）——`memory[0, indices[t]]` 取出第 t 步可见的 L 段历史。
   推理循环里 `t_ = max(0, min(t, L-1))`（75）为序列头几步选对 mask 行——这三行的索引体操与训练侧 `ppo_trxl.py` 必须严格一致，否则记忆错位、策略崩溃。
3. **`agent.get_action_and_value(obs, memory_window, mask, indices)`（79）**：签名暴露了 TrXL 版与普通 PPO 的全部差异——网络额外吃三个记忆参数。

### 与基础版差异

没有"基础版"对照（enjoy.py 是配套脚本），对照物是**训练侧 `ppo_trxl.py`**：训练时记忆在 rollout 循环里随 state 传递；enjoy.py 把同样的索引逻辑抽出来逐步执行——因为推理没有向量化 batch，只有单环境单步。

### 模式与坑

- **裸 `except:`（25）**：HF 下载失败统一转 RuntimeError——与 qdagger 同款代码卫生问题。
- **`env.render()` 双调用（40, 83）**："human" 模式下 step 自带渲染，显式 render 是保险写法（部分 gymnasium 版本行为差异）。
- **`max_episode_steps` 兜底链（43-47）**：Memory Gym 环境把 max_episode_steps 设为 -1（无限回合），文件头注释（47-48）提醒"位置编码依赖此值，必须设对"——TrXL 的位置编码长度在 Agent 构造时就固定（54 行传入 max_episode_steps）。
- **模型默认来自个人 HF 账号 `LilHairdy/cleanrl_memory_gym`**（24）——社区贡献的预训练模型，可用性依赖第三方。

---

## tests/test_jax_compute_gae.py

**知识图谱**：tags: `test/unit-test/gae/jax/ppo` · complexity: moderate · 入边：`pipeline:.github/workflows/tests.yaml triggers`（CI 触发）+ `file:cleanrl/ppo_atari_envpool_xla_jax_scan.py tested_by`——**它专门守护 scan 版的 GAE 重构**。

### 架构角色

GAE 的**实现等价性单元测试**：在随机 rollout 数据上，断言 `jax.lax.scan(reverse=True)` 版 GAE 与纯 Python 循环版 GAE 的 advantages/returns **逐位相等**（`==.all()`，不是 allclose）。它是 scan 版重构（第 8 节 345-347 行）的正确性护栏——时序反向递推改成 scan 后，最容易出的错是索引错位/边界 off-by-one，而这类错在随机数据上会立刻放大为数值差异。

### 文件解剖（91 行）

| 行号 | 内容 |
|---|---|
| 11 | `def test_compute_gae():` 单测试函数（pytest 约定：test_ 前缀自动发现，无 class） |
| 12-18 | 局部 `Storage` flax dataclass（字段是 scan 版的子集：dones/values/advantages/returns/rewards） |
| 20-27 | `compute_gae_once(carry, inp, gamma, gae_lambda)`：单步转移函数——**与训练脚本 320-327 行逐字一致** |
| 29-46 | `compute_gae_scan`：拼接 next 值 + 切片对齐 + `lax.scan(reverse=True)`——**与训练脚本 331-352 行逐字一致**（jsr 复制进测试） |
| 48-64 | `compute_gae_python_loop`：经典 reversed 循环版——**与 PyTorch 系（ppo_atari_envpool.py:250-263）逻辑一致** |
| 66-75 | 常量：`num_steps=123, num_envs=7`（故意用非 2 的幂，逼出形状泛化 bug）、gamma=0.99、λ=0.95、seed=42；两个实现各自 `partial` 固定超参 + `jax.jit`（72-75） |
| 76-87 | 随机数据：dones∈{0,1}（randint 0-2）、values~U(0,1)、rewards~U(-1,1)（含负奖励！）、next_value/next_done；`storage2 = deepcopy(storage1)`（85） |
| 88-91 | 两实现各跑一遍，`assert (storage1.advantages == storage2.advantages).all()` + returns 同断言 |

### 算法/工程要点

1. **等价性测试的方法论**：不测"GAE 是否等于理论公式"（那是另一个层级的测试），而是测"**新实现 ≡ 旧实现**"——旧实现（Python 循环）已被 PyTorch 系多年验证。这是重构测试的经典模式：**锚定已知良好实现**。
2. **`==.all()` 的强度（90-91）**：逐位相等而非 allclose——成立的前提是两个版本的浮点运算**顺序完全一致**（scan 反向扫与 reversed 循环每步都是"先 delta 后乘加"，XLA 不做破坏结合律的重排）。这是非常强的断言，若未来 XLA 改变融合策略可能误报——但对捕捉索引错位，逐位断言比 allclose 灵敏得多。
3. **随机数据的设计（78-87）**：dones 随机置 1 检验终止屏蔽分支；rewards 有负值检验符号处理；非 2 幂形状（123×7）检验切片对齐（`dones[1:]` vs `values[:-1]` 的长度 122 是否咬合）。
4. **jit 也被测试（72-75）**：两个实现均以 jit 形式运行——**连编译路径一起验证**（jit 化可能引入 dtype 提升、shape 广播等非显性问题）。

### 与基础版差异 / 在测试体系中的位置

- 其他测试（`test_envpool.py`、`test_procgen.py` 等）跑**完整训练脚本几百步**做冒烟；本测试是唯一一个**纯函数级单元测试**——因为 scan 重构的风险在函数内部而非集成层。
- 与 `test_ppo_procgen.py` 等的关系：冒烟测试证明"能跑"，本测试证明"算得对"——两级互补。

### 模式与坑

- **`deepcopy(storage1)`（85）**：flax struct 是不可变的（replace 返回新对象），deepcopy 似乎多余——但它防御的是**未来改回可变版本**时的交叉污染，廉价的保险。
- **测试代码复制实现（20-46）**：把训练脚本的函数逐字复制进测试而非 import——cleanrl 单文件哲学的延伸：测试独立于训练文件演进（改训练代码不会静默改掉测试基准）。代价是双份维护，注释里没有说明这一点，读者需自行领会。
- **CI 挂在 `.github/workflows/tests.yaml`**（知识图谱 triggers 边）——JAX 栈的回归防线在每次 PR 上自动执行。

---

## README.md（简讲）

**知识图谱**：`document:README.md` · tags: `documentation/entry-point/overview/rl-algorithms/getting-started` · 入边 30+ 条——全库几乎每个训练脚本都被它 documents，是知识图谱的中心枢纽。

### 架构角色

项目门面 + 算法索引 + 快速上手三合一。核心内容：

| 行号 | 内容 |
|---|---|
| 15-27 | 六大特性宣言：**单文件实现**（19-21，"ppo_atari.py 仅 340 行含全部细节，适合不想读整个模块化库的人"）、benchmark、TensorBoard、种子可复现、视频捕获、wandb/AWS |
| 29 | JMLR 论文链接（Huang et al. 2022）——学术身份 |
| 33-34 | 生态卫星：**CORL**（离线 RL 的 cleanrl 风格）与 **LeanRL**（CUDAGraphs 加速版）——单文件哲学的外溢 |
| 40 | ⚠️ **最重要的定位声明**：CleanRL **不是模块化库、不可 import**——"以重复代码为代价换取全部实现细节的可理解性"；适用人群：想理解算法每个细节的人 / 想快速原型化模块化库不支持的高级特性的人 |
| 42-93 | Get started：uv 0.7.9+ / Python>=3.7.1,<3.11；`uv pip install .` 或 requirements-*.txt 分组安装 |
| 111-116 | envpool 3-4x 加速宣传 + **副作用声明**（"样本效率可能降低"）+ Pong 5-10 分钟配方 |
| 132-167 | 算法表：**9 算法族 / 30 变体**（PPO 独占 12 变体——本文 2/3 的文件都在此表） |
| 169-177 | Open RL Benchmark：跨库（SB3/baselines/jaxrl）可查询实验数据集 |
| 184-199 | BibTeX 引用块 |
| 202-208 | 致谢：贡献者自费算力 + Google TRC（TPU）+ HuggingFace GPU——社区项目的资源现实 |

### 要点

- **L40 的警告是理解全库的钥匙**：本文讲的 15 个文件里大量"复制粘贴"的相似代码不是技术债，是**设计决策**。
- 算法表（132-167）每行三链：本地文件链接 + 论文 arXiv 链接 + docs.cleanrl.dev 文档链接——三位一体的导航。
- gymnasium 迁移声明（37）仍指向 PR#277——迁移是渐进式的（所以 envpool 系还是老 gym API，multigpu/qdagger 已是 gymnasium）。

---

## pyproject.toml（简讲）

**知识图谱**：`config:pyproject.toml` · tags: `configuration/dependencies/packaging/build-system/optional-extras`。

### 架构角色

打包与依赖清单——**可复现性优先于灵活性**的配置哲学样本。

| 行号 | 内容 |
|---|---|
| 1-13 | 元信息：`cleanrl` v**2.0.0b1**（beta）、Python `>=3.8,<3.11`（上限锁死，因 gym/procgen 等老库兼容性） |
| 14-26 | 核心依赖：**`torch==2.4.1`、`gym==0.23.1`、`gymnasium==0.29.1` 双 gym 并存**（两代 API 共存期）、tensorboard、wandb、moviepy（视频）、pygame、huggingface-hub、**tyro**（CLI，Args dataclass 的搭档）、rich、tenacity |
| 28-75 | **12 组 optional extras**：atari / envpool / procgen / mujoco / dm_control / pettingzoo / **jax（钉死 jax==0.4.8 + jaxlib==0.4.7 + flax==0.6.8 + optax==0.1.4 + chex==0.1.5 + scipy<1.13）** / optuna / docs / cloud / plot / pytest——按环境族按需安装，`pip install ".[envpool,jax]"` |
| 77-78 | `[dependency-groups] dev = pre-commit`——uv 风格开发组 |
| 80-94 | hatch 打包：sdist/wheel 只含 `cleanrl/` + `cleanrl_utils/`（tests/benchmark/docs 不进包） |

### 要点

- **单文件脚本的库为什么还要打包**：`cleanrl_utils/`（buffer/evals/wrappers）和 `tests/` 需要 import 路径稳定——打包是为了**测试与工具函数复用**，不是为了让用户 `import cleanrl`（README:40 明确反对）。
- **jax extras 全族钉死旧版**（0.4.8 时代 API）——JAX API 演进快，cleanrl 选择锁版本保可复现，代价是 JAX 新特性不跟进（社区后续在 LeanRL/EvoJAX 方向迭代）。
- **torch==2.4.1 精确钉死**：与 multigpu 的 all_reduce、DDP 行为强相关——RL 复现里框架小版本差异足以改变 benchmark 曲线（cleanrl JMLR 论文的核心主张之一）。

---

## CONTRIBUTING.md（简讲）

**知识图谱**：`document:CONTRIBUTING.md` · tags: `documentation/contributing/placeholder` · summary 直言"占位文件"。

### 架构角色

**1 行的占位文件**（全文即 L1：`## Please check out https://docs.cleanrl.dev/contribution/ for more detail.`）。

### 要点

- **贡献流程文档不在 repo 而在文档站**（docs.cleanrl.dev/contribution，由 `docs/contribution.md` 经 MkDocs 构建）——cleanrl 的文档分工策略：代码仓库放代码，流程文档放站点（站点可热更新，不受发版节奏约束）。
- 实际贡献规范（文档站内容概括）：新算法实现须走单文件模板（Args/Agent/main 三段式）、须配 benchmark 实验、须配 tests 冒烟——本文 15 个文件的统一结构正是这套模板的产物。
- 教训样本：**占位文件也是架构决策**——GitHub 会自动在 PR 界面展示 CONTRIBUTING.md，这一行保证了新贡献者第一眼被导流到最新规范，而不是读到 repo 里过时的流程副本。

---

## 收束：15 文件的全景坐标

```
性能优化轴（沿 ppo_atari.py 向外）
  ppo_atari_envpool.py ──── C++ 环境向量化（采样端加速）
  ppo_atari_multigpu.py ─── 手写 all_reduce（训练端扩展）
  ppo_atari_envpool_xla_jax.py ── JAX 整段编译（调度端消除）
  ppo_atari_envpool_xla_jax_scan.py ── lax.scan（编译端优化）⇐ test_jax_compute_gae.py 护栏

算法增量轴（沿 ppo/dqn 向外）
  ppo_rnd_envpool.py ── 内在奖励 + 双价值头（探索）
  ppo_procgen.py / ppg_procgen.py ── ImpalaCNN + 两阶段（泛化/表征）
  qdagger_dqn_atari_impalacnn.py ── 教师蒸馏（ imitation×RL ）

JAX 算法栈（off-policy 侧）
  dqn_jax.py ── TrainState 寄生 target_params 惯用法
  td3_continuous_action_jax.py ── 三 TrainState 编排 + jit 内噪声

叙事层
  README.md（定位宪法）/ pyproject.toml（复现优先）/ CONTRIBUTING.md（流程外置）
```

三条主线交叉处的惯用法谱系：**monkey-patch 接口缝合**（envpool 属性、dtype 修正）→ **手写机制显式化**（all_reduce、RecordEpisodeStatistics）→ **函数式状态管理**（TrainState 扩展、pytree Storage、PRNGKey 链）→ **checkpoint 自包含**（args+权重同档）。part3 将覆盖其余基础变体与 cleanrl_utils 工具层。


---

# cleanrl 核心文件精讲（3/3）：共享工具、基建与测试

> 本文续接 part1（基础算法族）、part2（高级变体与 JAX 栈）。覆盖 13 个文件：**共享工具库 cleanrl_utils**（Atari 预处理 / 缓冲区 / 模型回放 / 复现 / HF 上传 / Optuna 调参 / benchmark 启动器 / 评估回调）→ **测试层**（四组冒烟测试）→ **依赖版图**（requirements.txt）。
> 所有行号锚点均实测自本地仓库 `~/ai/cleanrl/`（master 分支工作区）；知识图谱信息来自 `.understand-anything/knowledge-graph.json`。
> 前置阅读：`CORE-FILES-EXPLAIN-part1.md`、`CORE-FILES-EXPLAIN-part2.md`。

## 单文件哲学的边界：为什么会有 cleanrl_utils

part1/part2 反复强调 CleanRL 的宪法是"**一个算法 = 一个自包含文件**"，算法代码宁可复制也不抽象。那 `cleanrl_utils/` 这个 16 个 py 文件的包为什么存在？答案是它划出了一条精确的例外边界：

- **算法代码不共享**（ppo.py 与 ppo_atari.py 的网络、GAE、更新循环各自复制一份）——这是可读性的代价与收益；
- **与算法无关的"环境侧"和"工程侧"代码共享**——Atari 预处理链是 DeepMind 2015 以来的社区标准件，replay buffer 是 SB3 的成熟实现，HF 上传/Optuna 调参/SLURM 投递是纯工程问题。这些代码**改一行等于改 16 个算法**，复制它们只会引入漂移 bug，不会带来任何可读性收益。

知识图谱把这一层标为 `layer:shared-utilities`（共享工具库层），与算法脚本层、测试层（`layer:tests`）、配置层（`layer:project-config`）并列——图谱的四层结构本身就是对这条边界的确认。下文每个文件都会标注它在图谱中的入边（谁用它），你会发现入边数量恰是该文件"共享价值"的量化：atari_wrappers 11 个算法导入、buffers 16 个、huggingface 8 个、reproduce 0 个（孤立的独立工具）。

---

## cleanrl_utils/atari_wrappers.py

**知识图谱**：`file:cleanrl_utils/atari_wrappers.py` · tags: `environment-wrappers/atari/preprocessing/共享库` · complexity: complex · 入边：**11 个算法脚本导入**（c51_atari、c51_atari_jax、ppo_atari、ppo_atari_lstm、ppo_atari_multigpu、rainbow_atari、sac_atari、dqn_atari_jax、dqn_atari、qdagger 两个变体）——全仓库入边最多的工具文件。

### 架构角色

整个 Atari 分支的**观测管道标准件**。文件头（1-18 行）明确声明改编自 stable-baselines3 的 `common/atari_wrappers.py`（MIT 协议），所以这个文件本质上是"SB3 的 Atari 预处理链按需裁剪后内嵌进 CleanRL"——又一个"不重复造轮子，但把轮子搬回家"的案例。它把 2013-2015 年 DQN 系列论文的预处理约定（Noop 起始、帧跳过、max 池化、生命终止、灰度缩放、奖励裁剪）编码为 8 个可独立使用的小包装器，再加一个一键组合的工厂。**为什么它成为共享库的样板**：预处理是算法无关的——DQN、PPO、SAC、Rainbow 面对的是同一条管道，任何一处行为差异都会直接毁掉跨算法可比性。

### 内部结构（325 行，8 个类）

| 行号 | 类 | 一句话职责 |
|---|---|---|
| 36-59 | `StickyActionEnv` | 以概率 p 重复上一动作（ALE 难度模式，论文 arXiv:1709.06009，见 40-41 行注释） |
| 62-91 | `NoopResetEnv` | reset 时先执行 1~noop_max 次随机 NOOP 再返回起始帧 |
| 94-114 | `FireResetEnv` | reset 时自动按 FIRE 跳过等待画面（Breakout 类游戏） |
| 117-165 | `EpisodicLifeEnv` | 掉一条命 = 回合结束，只有真 game over 才物理 reset |
| 168-210 | `MaxAndSkipEnv` | 每 4 帧执行一次动作，对最后两帧取 max |
| 213-230 | `ClipRewardEnv` | 奖励按符号裁剪为 {-1, 0, +1} |
| 233-266 | `WarpFrame` | cv2 灰度化 + 84×84 缩放（Nature 论文标准） |
| 269-325 | `AtariWrapper` | 上述组件的**一键组合工厂** |

### 逐个深讲经典包装器

**① NoopResetEnv（62-91）——起始状态多样化**。Atari 游戏每局开局画面几乎相同，若直接从第 0 帧训练，价值网络只需记住极少的起始状态。解法：reset 后先随机走 1~30 步 NOOP（83 行 `self.unwrapped.np_random.integers(1, self.noop_max + 1)`）。三个细节：`noop_max=30` 默认值来自 DQN 论文；80-82 行的 `override_num_noops` 是测试用的注入点（生产不传）；87-90 行若 NOOP 期间游戏结束则重新 reset，避免返回死亡画面。

**② MaxAndSkipEnv（168-210）——帧间去闪烁**。Atari 硬件出于性能用"奇偶帧交替绘制精灵"，部分游戏物体每隔一帧才显示一次——若只采单帧，物体会凭空消失。解法分两半：**帧跳过**（196 行 `for i in range(self._skip)`，同一动作重复 4 次、奖励求和 203 行）把 60fps 降到 agent 视角的 15fps；**max 池化**只对**最后两帧**做（199-202 行把倒数第二帧和最后一帧存入 `_obs_buffer`，208 行 `max(axis=0)`），保证闪烁物体至少在一帧中出现。206-207 行注释点破一个反直觉细节：`done=True` 那一帧的观测**无所谓**——反正外层会 reset。183 行预分配 `(2, H, W)` 缓冲区避免每步分配。

**③ EpisodicLifeEnv（117-165）——训练信号密度化的双面技巧**。DeepMind DQN 的做法：掉命即置 `terminated=True`（135-141 行，通过 `env.unwrapped.ale.lives()` 读取剩余生命），让价值估计不必跨越"掉命"这个剧烈状态突变；但**物理 reset 只在真 game over 时发生**（153-154 行 `if self.was_real_done`）。掉命后继续玩时（156-163 行），用一个 NOOP step 推进画面，且要再查一次 terminated——162-163 行注释提到这是为了防 `RuntimeError: Tried to step environment that needs reset`。137-139 行的 Qbert 特例注释（生命值会在 0 停留几帧）解释了为何用 `0 < lives < self.lives` 而非简单不等式：只在**真的掉命**那一刻置 done 一次。**代价**：训练时的"回合"≠真回合，回报统计变短——所以评估脚本（enjoy/evals）通常不用这个包装器。

**④ FireResetEnv（94-114）**。构造时两个断言（103-104 行）：动作 1 必须是 FIRE 且总动作数 ≥3——即只对 Breakout/Pong 等需要开火的游戏生效。reset 时连按 FIRE(1) 和 RIGHT(2)（108-111 行），每步后检查是否已结束需再 reset。

**⑤ ClipRewardEnv（213-230）与 WarpFrame（233-266）**。前者继承 `gym.RewardWrapper`，只需覆写 `reward()` 方法（223 行 `np.sign(float(reward))`），是"子类化点最小化"的典范；奖励符号化让 57 个游戏（Pong 得分 21、Breakout 得分 350+）能共享**同一组超参数**。后者 `observation()` 用 cv2 的 `RGB2GRAY` + `INTER_AREA` 插值缩放（264-265 行），并在构造器里**重写 observation_space**（249-254 行）为 `(84, 84, 1)`——包装器协议的要点：改观测必须同步改空间声明，否则下游网络形状推断全错。263 行的断言给出缺 cv2 时的自愈提示。

**⑥ AtariWrapper（269-325）——组合顺序即语义**。300-323 行的构造器就是全部逻辑：按 **Sticky → Noop → MaxAndSkip → EpisodicLife → FireReset → WarpFrame → ClipReward** 的顺序层层包裹（310-323 行），每个环节可用参数关闭。顺序不可乱：FireReset 的启用判定（319 行 `"FIRE" in env.unwrapped.get_action_meanings()`）必须发生在最外层查询时仍能看到底层动作表；WarpFrame 必须在 MaxAndSkip **之后**（先对原始帧 max 池化再缩放，反过来会让去闪烁失效）；ClipReward 在最外层保证训练代码拿到的就是符号奖励。docstring 里的关键警告（287-288 行）：**只配 `*NoFrameskip-v4` 环境用**——环境自带跳帧的话再叠 MaxAndSkip 就是双重跳帧。

### 外部连接与要点

- **使用者**（图谱入边 11 条）：全部 Atari 算法脚本。典型用法见 `ppo_atari.py:97-105`：`AtariWrapper(env)` 之后**再补一层 `gym.wrappers.FrameStack(env, 4)`**（`ppo_atari.py:105`、`dqn_atari.py:99`）。
- **一个常见误解要澄清**：本文件**没有 FrameStack**。帧堆叠是 gymnasium 自带包装器，由各算法脚本自行叠加（因为 jax 版用 `batched_ptr`、LSTM 版根本不堆叠——帧堆叠与记忆结构是算法决策，不属于"环境标准件"）。图谱摘要里提到的 frame_stack 选项在当前快照源码中不存在，以源码为准。
- cv2 是**可选依赖**（28-33 行 try/except，仅 WarpFrame 真正需要），且 31 行 `cv2.ocl.setUseOpenCL(False)` 关掉 OpenCL 避免 0 大小数组上传的驱动 bug。

### 模式与坑

- **洋葱协议**：每个包装器只改一个维度（reset 语义 / step 频率 / 奖励 / 观测），通过 `gym.Wrapper` 委托其余一切——组合的表达力来自顺序。
- 坑 1：`EpisodicLifeEnv` 会污染回合统计。训练日志里的 "episodic_return" 实为"每命回报"，做 benchmark 对比时须知此语义（part2 讲 envpool 版时同样的 `lives==0` 判定问题再次出现）。
- 坑 2：`MaxAndSkipEnv` 预分配缓冲区用 `observation_space.dtype`（183 行），若上游空间未声明 dtype 会在 181 行断言失败——链式包装器对空间声明的契约要求是刚性的。
- 坑 3：StickyActionEnv 默认不启用（`action_repeat_probability=0.0`，308 行），要用 ALE 难度模式必须显式传参——多数论文复现其实是"关粘性"的 v4 设定。

---

## cleanrl_utils/buffers.py

**知识图谱**：`file:cleanrl_utils/buffers.py` · tags: `replay-buffer/rollout-buffer/off-policy/on-policy/shared-library` · complexity: complex · 入边：**16 个算法脚本导入**（全仓库最高）。与 atari_wrappers 同源——文件头（1-18 行）声明改编自 SB3 的 `common/buffers.py`。

### 架构角色

**off-policy 家族的公共记忆体**。DQN/C51/DDPG/TD3/SAC（含各自 jax 版）全部从这里导入 ReplayBuffer。但有一个**必须先纠正的预期**：任务清单里说"讲 SumTree/SegmentTree 优先级回放"——**它们不在这个文件里**。实测（grep 全仓）优先级回放的实现 `SumSegmentTree`（`rainbow_atari.py:211`）、`MinSegmentTree`（`:245`）、`PrioritizedReplayBuffer`（`:266`）全部内嵌在 rainbow_atari.py 单文件中。这恰恰是单文件哲学的体现：**均匀采样缓冲区是 16 个算法的公共件 → 进共享库；优先级采样是 Rainbow 一家的算法组件 → 留在算法文件里**。 buffers.py 里只有最朴素的两种：均匀 ReplayBuffer 和 on-policy RolloutBuffer。

还有一个图谱看不出的死角：**16 个导入者全部只导入 `ReplayBuffer`**（如 `dqn.py:16`、`td3_continuous_action.py:16`，grep 实测无一例外）。`RolloutBuffer` 类（433-610 行）是 SB3 拷贝过来的"搭售品"——所有 on-policy 脚本（ppo 系）为保持自包含仍用文件内联的 numpy 数组。也就是说这 610 行里有约 180 行在仓库内零调用，纯粹作为 SB3 的完整性保留。

### 内部结构（610 行）

| 行号 | 组件 | 职责 |
|---|---|---|
| 47-61 | `RolloutBufferSamples` / `ReplayBufferSamples` | NamedTuple 采样容器（字段即 on/off-policy 的信息差异） |
| 64-86 | `get_action_dim()` | 从动作空间推断维度，分派 Box/Discrete/MultiDiscrete/MultiBinary |
| 89-113 | `get_obs_shape()` | 观测空间形状推断，Dict 空间递归展开（110 行） |
| 116-136 | `get_device()` | "auto" → cuda 可用性检测（127-134 行） |
| 139-247 | `BaseBuffer` (ABC) | 抽象基类：pos/full 环形指针、均匀采样索引、numpy→torch |
| 250-430 | `ReplayBuffer` | off-policy 均匀环形缓冲（本文件真正的主角） |
| 433-610 | `RolloutBuffer` | on-policy + GAE（仓库内零调用的搭售品） |

### ReplayBuffer 深讲（250-430 行）

**内存布局与环形写入**。构造器预分配六个 numpy 数组（305-320 行）：`observations/next_observations/actions/rewards/dones/timeouts` 形状均为 `[buffer_size, n_envs, ...]`。290 行 `buffer_size = max(buffer_size // n_envs, 1)` 是个容易被忽略的语义决定：**用户传的是总转移数，存储按每环境行数切分**。`add()`（339-375 行）写入后 `pos += 1`，到顶回卷并置 `full=True`（372-375 行）。350-355 行的两个 reshape 处理 Discrete 观测/动作的广播死角（numpy 无法把 `(n,)` 广播成 `(n,1)`）。

**三处防御性设计**，每处都对应 SB3 的一个历史 issue：

1. **内存预算检查**（292-337 行）：psutil 可用时，把全部数组的 `nbytes` 加总与 `virtual_memory().available` 比较，超了就 warning——因为 Atari 的 replay buffer 常以 GB 计，写满才 OOM 太晚。
2. **`optimize_memory_usage` 与 `handle_timeout_termination` 互斥**（298-302 行直接 raise ValueError）：省内存方案把 next_obs 存在 `observations[pos+1]`（360-361 行），采样时排除 `pos` 位置（391-394 行）防止取到被覆盖的脏转移；而 timeout 处理需要独立的 next_obs 语义，两者组合会出 bug（SB3 issue #934）。
3. **timeout 区分**——本文件最值得学的算法细节。gymnasium 把"自然结束"（terminated）和"时间片用完"（truncated）分开，但 Q-learning 的 bootstrap 语义完全不同：自然结束时 `done=1` 正确截断 `r + γ·maxQ(s')`；时间截断时 s' 之后还有价值，若也截断会系统性低估。做法：`add()` 从 info 里抄 `TimeLimit.truncated` 到 `timeouts` 数组（369-370 行），采样时 `_get_samples` 的 done 打折——412 行 `dones * (1 - timeouts)`。一行乘法修正了一个曾普遍存在的 off-policy 偏差（SB3 issue #284）。

**采样路径**。`sample()` → 父类 218-225 行 `np.random.randint` 均匀抽索引 → `_get_samples()`（397-415 行）：399 行**再随机抽一个环境列** `env_indices`（多环境存 [T, N, ...]，批内每个时间点来自随机环境）→ 六元组经 `to_torch`（235-247 行，默认 copy=True 防引用别名）转成 `ReplayBufferSamples` NamedTuple 返回。`_maybe_cast_dtype`（417-430 行）把 float64 动作降为 float32（MuJoCo 环境动作是 float64，与网络权重不一致的隐坑）。

### RolloutBuffer 速讲（433-610 行，零调用）

虽无调用者，作为 GAE 参考实现值得一看：`compute_returns_and_advantage`（493-528 行）是教科书级 GAE(λ) 倒序递推——523 行 TD 残差 `δ = r + γ·V(s')·(1-done) - V(s)`，524 行 `last_gae_lam = δ + γλ·(1-done)·last_gae_lam`，528 行 `returns = advantages + values`（TD(λ) 目标）。`get()`（571-596 行）用生成器按 batch_size 切 minibatch，586 行的 `swap_and_flatten` 把 `[T, N, ...]` 变 `[T×N, ...]` 且保持时间序（175-187 行实现：先 swapaxes 再 reshape）。与 part1 讲的 ppo.py 内联版逐行等价——再次印证"算法代码不共享"的纪律。

### 模式与坑

- 模式：**模板方法**（BaseBuffer 定 skeleton，子类只填 `add/_get_samples`）+ **数据 NamedTuple**（采样结果的字段自文档化）。
- 坑 1：找优先级回放别来这——去 `rainbow_atari.py:211-430`（SumSegmentTree 用完全二叉树数组实现前缀和，`tree_size = 2*capacity - 1`，213 行）。
- 坑 2：`sample()` 的 `np.random.randint` 是全局 RNG——复现实验时 buffer 采样与网络初始化共用一条种子流，顺序敏感。
- 坑 3：jax 算法（dqn_jax 等）也用这个 numpy buffer——只有网络在 jax，经验回放留在 numpy/torch 世界，属刻意取舍（jax 对动态形状的集合类型支持弱）。

---

## cleanrl_utils/enjoy.py

**知识图谱**：`file:cleanrl_utils/enjoy.py` · tags: `entry-point/evaluation/huggingface-hub/inference` · complexity: simple · 入边：被 `docs/get-started/zoo.md` 文档引用；自身 `tested_by → tests/test_enjoy.py`；出边 imports → `evals/__init__.py`。

### 架构角色

**模型动物园的播放器**：43 行的薄入口，把"HF Hub 上的检查点 → 重建网络 → 环境里跑 N 回合"串成一条命令。它是 zoo 生态（benchmark/zoo.sh 批量上传 ↔ enjoy 单个回放）的消费端，也是 push_to_hub（huggingface.py）的逆操作。

### 内部结构（43 行）

| 行号 | 组件 |
|---|---|
| 8-25 | `parse_args()`：--exp-name（默认 dqn_atari）/ --seed / --hf-entity（默认 cleanrl 官方）/ --hf-repository / --env-id / --eval-episodes（默认 10） |
| 28-43 | `__main__`：注册表查找 → 仓库名推导 → 下载 → 评估 |

四步主流程（30-43 行）：

1. **注册表分派**（30 行）：`MODELS[args.exp_name]()` 返回三元组 `(Model, make_env, evaluate)`。`MODELS` 定义在 `evals/__init__.py:72-82`，只收 dqn/c51 各 4 个变体 + ppo_atari_envpool_xla_jax_scan 共 9 个实验名；每个工厂函数（如 1-5 行的 `dqn()`）**延迟导入**对应算法模块——这条设计让 enjoy 不用装齐 jax/atari 全家桶就能跑 torch 模型。
2. **仓库名约定**（31-32 行）：未显式给仓库时按 `{entity}/{env_id}-{exp_name}-seed{seed}` 推导——与 benchmark/zoo.sh 的上传命名严格对偶，命名约定本身就是接口。
3. **下载**（34 行）：`hf_hub_download(repo_id, filename=f"{args.exp_name}.cleanrl_model")`——`.cleanrl_model` 后缀是 CleanRL 检查点的社区标识。
4. **评估**（35-43 行）：把三元组塞进通用 `evaluate()`。

### 模式与坑

- 模式：**注册表 + 惰性导入工厂**，9 个算法后端互不拖累，新增算法只需在 `__init__.py` 加一个 6 行工厂函数。
- 坑 1（实测 bug）：42 行 `capture_video=args.capture_video` 引用了 **parse_args 从未定义的属性**（8-25 行的参数表里没有 --capture-video）——直接 `python -m cleanrl_utils.enjoy` 会在 42 行抛 AttributeError。而 `tests/test_enjoy.py` 调的命令是 `python enjoy.py`（根目录脚本，已不存在）且该测试**未接入** `.github/workflows/tests.yaml`（grep 实测无 enjoy 条目）——坏的入口 + 过期的测试互相掩护，是"孤儿基建无人踩"的活标本。
- 坑 2：三元组里 Model 是**类**而非实例，因为网络形状要从环境推断（`evaluate` 内 `Model(envs)` 构造，ppo_eval.py:19）——跨文件传类是 CleanRL 的常规操作。

---

## cleanrl_utils/reproduce.py

**知识图谱**：`file:cleanrl_utils/reproduce.py` · tags: `reproducibility/wandb/experiment-management` · complexity: simple · **入边 0 条、出边 0 条**——图谱上的孤立节点，纯独立命令行工具。

### 架构角色

**可复现性的"逃生舱"**：给定一个 wandb run 路径，把当初训练的完整环境（依赖 + 代码 + 命令行）从 wandb 服务器上捞回来，打印重建脚本。它体现 CleanRL 对复现的态度：复现单位不是论文表格，而是**每一次 run**——wandb 在训练时自动记录 `wandb-metadata.json`（含 argv、程序路径）和冻结的 requirements.txt，reproduce.py 只是把这些存档变回可执行命令。

### 内部结构（54 行，单 main 块）

| 行号 | 逻辑 |
|---|---|
| 9-23 | 两个参数：--run（默认官方示例 `cleanrl/cleanrl.benchmark/runs/thq5rgnz`）、--remove-entity |
| 24-28 | 拼 wandb 文件 API URL（`https://api.wandb.ai/files/{uri}/...`）并 GET metadata |
| 30-41 | 从 argv 里剔除 `--wandb-entity` 参数对（避免复现者误传他人 entity） |
| 45-53 | 打印四行复现流水：venv 创建 → `pip install -r {wandb上的requirements}` → `curl` 下载代码 → 原命令行拼接 |

### 要点与坑

- **零边的设计即定位**：它不服务任何脚本，服务人——所以图谱孤立不是问题，但按"孤儿=死亡内容"的口径，它靠 docs 复现章节的文字引用存活。
- 坑 1：2 行用 `distutils.util.strtobool`——distutils 在 Python 3.12 被移除，此文件是仓库里少数未迁移到自研 `torch.float`/tyro bool 惯例的老代码。
- 坑 2：依赖 wandb 的文件保留策略与 API 未变更，wandb 服务端行为变化会静默破坏它（无测试覆盖）。

---

## cleanrl_utils/huggingface.py

**知识图谱**：`file:cleanrl_utils/huggingface.py` · tags: `huggingface-hub/model-publishing/serialization/integration` · complexity: moderate · 入边：**8 个算法 depends_on**（dqn/dqn_jax/c51/c51_jax/ddpg/ddpg_jax/td3/td3_jax）——即 zoo 的生产端，与 enjoy.py（消费端）成对。

### 架构角色

**一站式模型发布函数**：整个文件就是一个 `push_to_hub`（15-145 行）。算法脚本在训练结束时（如 `dqn.py` 尾部）算完评估回报就调它，把检查点、视频、训练代码、超参数、评估指标打包成一个规范的 HF 模型仓库。它是 CleanRL "RL 模型动物园"（huggingface.co/cleanrl）的机械化通道——几百个检查点不是手工上传的，是这个函数的产物。

### 内部结构（145 行）

| 行号 | 步骤 |
|---|---|
| 14 | `@retry(stop=stop_after_attempt(10), wait=wait_fixed(3))`——tenacity 装饰器，网络抖动自动重试 |
| 27-38 | Step 1：**惰性导入** hf_hub（重依赖不拖累 import 时）+ `create_repo(exist_ok=True)` + 从返回 URL 解析真实 entity |
| 42-46 | Step 2：删旧——把仓库里已有的 `.tfevents` 和 `.mp4` 列成 CommitOperationDelete（保证最新 commit 干净） |
| 49-83 | Step 3：生成 model card（Markdown 文本） |
| 88-110 | Step 4：metadata——`metadata_eval_result` 把评估结果写成 HF 标准的 yaml 元数据块 |
| 113-121 | Step 5：视频——全部 mp4 提交 + **最新一个**复制到根目录改名 `replay.mp4`（Hub 仓库首页预览位） |
| 124-135 | Step 6：检查点文件夹 + **训练源码本身**（sys.argv[0]）+ pyproject.toml/poetry.lock |
| 137-144 | Step 7：`create_commit` 一次性提交全部 CommitOperation |

### 要点

1. **model card 的复现闭环**（50-83 行）：卡片直接写明复现命令 `curl -OL .../raw/main/{算法文件}` + `python {文件} {原命令行}`（72-77 行）——因为 Step 6 把**训练时的那份源码**一并提交了，所以复现者拿到的代码与产生该检查点的代码严格同版本，不受仓库后续演进影响。第 81 行 `pformat(vars(args))` 把 argparse 命名空间整个 dump 进卡片，超参数零遗漏。
2. **指标入库**（96-105 行）：`metrics_value=f"{np.average(...):.2f} +/- {np.std(...):.2f}"`（102 行）写进 HF 元数据，使模型可被 Hub 按 mean_reward 检索——把 RL 检查点纳入 HF 的模型评估生态。
3. **最新视频判定**（118 行）：`max(video_files, key=lambda f: int("".join(filter(str.isdigit, f.stem))))`——从文件名里抠出所有数字取最大。依赖 CleanRL 视频命名含步数的约定，换个命名习惯就失效。
4. **幂等性设计**：删旧文件（Step 2）+ `exist_ok=True`（33 行）+ retry（14 行）三者合起来支持同一仓库反复推送而不留垃圾。

### 模式与坑

- 模式：**CommitOperation 批量提交**——不是逐文件 upload，而是一次 `create_commit`（137 行）原子完成十几个增删，这是 huggingface_hub 的正确姿势（省 API 调用且中间态不可见）。
- 坑 1：134-135 行上传 `poetry.lock`，但依赖体系已迁到 uv（requirements.txt 头两行 `uv export` 生成）——锁文件与实际依赖工具脱节，model card 里的 `poetry install --all-extras`（75 行）对当前代码树已不再准确。
- 坑 2：49 行用 `sys.argv[0].split("/")[-1]` 推断算法文件名——函数依赖调用方的 argv 形态，从 notebook 或包装器调用会传错文件。

---

## cleanrl_utils/tuner.py

**知识图谱**：`file:cleanrl_utils/tuner.py` · tags: `hyperparameter-tuning/optuna/experiment-tracking` · complexity: complex · 入边：`tests/test_tuner.py` 导入、根目录 `tuner_example.py` 导入、`requirements-optuna.txt` configures；出边 `tested_by → tests/test_tuner.py`。

### 架构角色

**不侵入算法的调参器**：基于 Optuna，但最大设计问题是"如何调一个对此毫无感知的脚本"。答案是一套**文件系统握手协议**——超参通过 `sys.argv` 注入，结果从 TensorBoard event 文件读回。算法脚本唯一要满足的契约是：tyro/argparse CLI + TensorBoard 记录 metric。这使它对所有 CleanRL 算法（及任何同构脚本）即插即用，是"算法不感知基建"的极致案例。

### 内部结构（146 行）

| 行号 | 组件 | 职责 |
|---|---|---|
| 14-21 | `HiddenPrints` | 上下文管理器：把 sys.stdout 重定向 devnull——因为调参要在**同进程**里跑算法脚本 |
| 24-69 | `Tuner.__init__` | 配置校验与聚合函数分派 |
| 71-146 | `Tuner.tune` | Optuna study 创建 + objective 定义 + optimize |

**构造器（24-69 行）三处校验/分派**：多环境时 target_scores 不许有 None（43-47 行，否则归一化无意义）；聚合方式 average/median/max/min 映射到 `np.average/median/max/min`（52-61 行）；storage 默认 `sqlite:///cleanrl_hpopt.db`（36 行）——断点续调：进程死了 study 在盘上，重跑同 study_name 继续。

**tune/objective（71-146 行）逐层拆**：

1. **超参采样与命令拼装**（73-85 行）：`params_fn(trial)` 让用户用 Optuna 原语（suggest_float/suggest_categorical）声明搜索空间，返回 dict；85 行把 dict 拼成 `--key=value` CLI 风格——注意这里没有用 shlex 转义，值直接 str() 拼接。
2. **同进程执行**（90-92 行）：`sys.argv = algo_command + [f"--env-id=...", f"--seed=..."]` 后 `runpy.run_path(path_name=self.script, run_name="__main__")`。选 runpy 而非 subprocess 的收益：省进程开销、可直接拿到脚本全局变量（92 行取 `experiment['run_name']` 来定位日志目录）；代价是全局状态污染风险与必须屏蔽 stdout（91 行 HiddenPrints）。
3. **指标读回**（94-99 行）：`event_accumulator.EventAccumulator(f"runs/{experiment['run_name']}")` 加载 TensorBoard 事件，98 行 `ea.Scalars(self.metric)[-window:]` 取**最后 N 个 episode 的窗口均值**——用尾部均值而非全程均值，因为 RL 学习曲线前段是噪声，尾部才代表收敛水平。
4. **归一化**（103-109 行）：`(avg - lo) / (hi - lo)`——target_scores 给每个环境一个 [随机基线, 专家基线] 区间，把不同量级的回报（CartPole 0-500 vs Acrobot -500-0）折到同一尺度才可跨环境聚合。**不设 target_scores 则原样返回**（108-109 行），单环境调参可偷懒。
5. **逐 seed 上报与剪枝**（116-122 行）：每算完一个 seed 就 `trial.report(score, step=seed)`，Optuna 的 MedianPruner 可以在 seed 循环**中途**杀掉劣势 trial（119-122 行）——多 seed 调参时这是主要算力节省来源：烂超参跑 1 个 seed 就出局。
6. **收尾**（126-128 行）：最终目标 = 各 seed 聚合分再平均（注释 "we alaways return the average"——原文拼错 always，146 行前）。

### 要点

- **归一化得分的语义**：tuner 优化的不是原始回报而是 normalized score（1.0 = 达到专家区间上界，0 = 随机基线）——与 RL 论文常用 reporting 对齐，也使 `target_scores` 字典实质上等价于一张 benchmark 对照表（test_tuner.py 里 CartPole [0,500]、Acrobot [-500,0] 即官方已知区间）。
- **与 wandb 的可选联动**（75-83、110-111、117-118 行）：传 wandb_kwargs 则每个 trial 一个 run、按 study 分组，trial 被 prune 也能 `run.finish(quiet=True)` 善终。
- 137-140 行打印续跑命令 `python -m cleanrl_utils.tuner --study-name ...`——但本文件并没有 `__main__` 入口/argparse，这个提示更像是留给根目录 `tuner_example.py` 的手工模板（图谱边：tuner_example.py imports tuner.py）。

### 模式与坑

- 模式：**黑板协议**（argv 进、TensorBoard 出）解耦调参器与算法；**嵌套 objective 闭包**让 study 逻辑自包含在一个方法里。
- 坑 1：HiddenPrints 重定向的是 Python 层 sys.stdout，C 扩展（mujoco、CUDA 库）直接写 fd1 的输出**拦不住**，调参日志仍可能被污染。
- 坑 2：同进程 runpy 反复执行算法脚本，若脚本有全局副作用（改环境变量、占 GPU 显存不还）会跨 trial 累积；算法脚本的 `runs/` 目录按 run_name 累积，重复调参需手动清理否则 EventAccumulator 读到旧文件。
- 坑 3：86 行变量名 `normalized_scoress` 多了一个 s——功能无误但提示这段代码的一次性脚本气质。

---

## cleanrl_utils/benchmark.py

**知识图谱**：`file:cleanrl_utils/benchmark.py` · tags: `benchmark/runner/slurm/experiment-management/entry-point` · complexity: moderate · 入边：**15 个 `benchmark/*.sh` depends_on** + 2 篇文档（contribution.md、benchmark-utility.md）；出边 depends_on → `benchmark/cleanrl_1gpu.slurm_template`。

### 架构角色

**基准实验网格启动器**：把"一条命令模板 × N 环境 × M 种子"展开成任务网格，按三种模式执行——打印（dry run）/ 本地线程池并行 / 渲染成 SLURM 作业数组。CleanRL 官方 benchmark（docs/benchmark/ 下几十张表）就是 benchmark/*.sh（每个算法一个 shell 包装）→ 本文件 → wandb → plot 系列脚本这条流水线跑出来的。它在图谱中的 15 条入边说明：**shell 脚本是用户界面，本文件是引擎**。

### 内部结构（152 行）

| 行号 | 组件 | 职责 |
|---|---|---|
| 13-36 | `Args` dataclass | tyro CLI：env_ids/command/num_seeds(3)/start_seed/workers/auto_tag + 5 个 SLURM 参数 |
| 39-51 | `run_experiment()` | shlex 切分 → Popen 捕获输出 → returncode 断言 |
| 54-87 | `autotag()` | git 信息 + GitHub PR 号 → wandb 标签 |
| 90-152 | `__main__` | 标签注入 → 网格展开 → 本地/SLURM 双路径 |

**autotag（54-87 行）——实验的可追溯性机械化**：三层降级取 git 标签——`git describe --tags`（58-60）→ 失败则 `no-tag-{commit数}-g{短hash}`（63-70）→ 再拼接 GitHub API 反查该 commit 关联的 PR 号（74-85 行，`api.github.com/search/issues?q=repo:vwxyzjn/cleanrl+is:pr+{commit}`）。92-99 行把结果并入 `WANDB_TAGS` 环境变量——wandb 会自动把 env 里的 tag 贴到每个 run 上。**净效果**：benchmark 曲线图上每个点都能追溯到"哪个 commit、哪个 PR"——版本控制与实验追踪的缝合点。

**主流程双路径**：

- **网格展开**（101-104 行）：双层循环 seed × env_id，把 `--env-id/--seed` 追加到用户命令尾部。`workers=0` 时**只打印不执行**（117-118 行）——dry run 是一等公民，先检查将跑什么再花卡时。
- **本地并行**（110-116 行）：`ThreadPoolExecutor(max_workers=args.workers)` submit 全部命令。注意用的是**线程池跑子进程**——子进程是真正的并行单位，线程只做等待，GIL 无碍。
- **SLURM 路径**（121-152 行）：读模板文件 → 字符串替换 9 个占位符。最讲究的两处：129 行 `{{array}}` 填成 `0-{N-1}%{workers}`——SLURM 数组语法里 `%workers` 限制**同时运行**的作业数（并发上限）；138-140 行 `cpus_per_gpu = ceil(total_cpus / (gpus_per_task × ntasks))`——把集群总 CPU 配额换算成每 GPU 的 CPU 数，资源代数替用户算。生成 `slurm/{uuid}.slurm` 后 150-152 行 `sbatch --parsable` 投递拿回 Job ID。

### 模式与坑

- 模式：**模板 + 占位符替换**（朴素但透明，模板 `benchmark/cleanrl_1gpu.slurm_template` 本身可读可改）；**一条命令横跨笔记本到集群**的扩展路径。
- 坑 1：76 行 GitHub 查询**硬编码 `repo:vwxyzjn/cleanrl`**——fork 用户跑 benchmark 时 PR 反查查的是上游仓库，标签可能张冠李戴；且 79 行 `prs["items"]` 为空时 83 行打印 `pr_number` 会 NameError（被 84 行裸 except 吞掉只 print 异常——静默降级但掩盖了控制流瑕疵）。
- 坑 2：本地并行路径**不检查** `args.workers > 0 and slurm_template_path is not None` 同时给出的情形（110 行条件使 ThreadPool 只在无模板时启用，但同时给了模板与 workers 时本地不跑、直接走到 sbatch——语义不直观）。

---

## cleanrl_utils/evals/ppo_eval.py

**知识图谱**：`file:cleanrl_utils/evals/ppo_eval.py` · tags: `evaluation/ppo/pytorch` · complexity: simple · 图谱入边 0（它被 `ppo_continuous_action.py:330` **函数内惰性导入**，import 边不在模块顶层所以图谱没抓到——以 grep 实测为准）。

### 架构角色

**评估回调的 PPO/PyTorch 样板**：evals/ 目录下 11 个同构文件（dqn_eval/c51_eval/td3_eval/…各算法一个）中最短的一个。它不进 `MODELS` 注册表（那 9 个名额给了 DQN/C51/envpool 系），而是被 `ppo_continuous_action.py` 在训练尾部的评估块（330 行 `from cleanrl_utils.evals.ppo_eval import evaluate`）惰性调用——**训练完顺手评 10 回合**，配合 `--upload-model` 时再喂给 push_to_hub。

### 内部结构（56 行）

| 行号 | 逻辑 |
|---|---|
| 7-16 | `evaluate()` 签名：model_path/make_env/env_id/eval_episodes/run_name/Model/device(cpu)/capture_video/gamma |
| 18-21 | 重建：单环境 SyncVectorEnv → `Model(envs)` 按环境形状建网 → `load_state_dict` 恢复权重 → `agent.eval()` |
| 23-34 | 评估主循环 |
| 39-56 | `__main__` 演示：下载第三方（sdpkjc）Hopper 模型并评估 |

主循环三个细节：26 行 `agent.get_action_and_value(obs)` 返回四元组后**只取 actions**（训练时还要 value/log_prob，评估复用同一前向接口）；28-33 行从 `infos["final_info"]` 里逐环境抠 `episode` 字典——这是 gymnasium 向量环境的回合统计约定（`RecordEpisodeStatistics` 在回合结束时挂 final_info），`if "episode" not in info: continue`（30-31 行）跳过未终止环境；33 行打印+收集，攒够 eval_episodes 个即返回列表。

### 要点与坑

- **协议约定**：`evaluate` 与算法脚本解耦的全部契约是 `Model(envs)` 可构造 + `get_action_and_value` 四元组接口 + checkpoint 是 `state_dict`——各算法 eval 文件（dqn_eval 等）差异只在网络前向方法名。**新算法接 zoo：写一个 50 行 eval 文件 + 注册 MODELS**，工作量被协议钉死。
- 坑 1：26 行用的是**采样分支**的动作（get_action_and_value 内部是 multinomial 采样）而非 argmax——评估的是随机策略的期望表现。PPO 论文惯例确实常用随机策略评估，但与"确定性评估"结果有系统差异，对比数字时须知口径。
- 坑 2：评估无视频时的 `capture_video=False`（55 行演示）以外，录制依赖 make_env 闭包里的 RecordVideo——评估与录制的设备/包装器由算法脚本的 make_env 决定，本文件只穿针引线。

---

## tests/test_atari.py + tests/test_classic_control.py

**知识图谱**：两者均 tags: `test/smoke-test/ppo`，complexity: simple，入边同为 `pipeline:.github/workflows/tests.yaml triggers`；test_atari 的 tested_by 边指向 ppo_atari.py + ppo_atari_lstm.py，test_classic_control 指向 ppo.py。

### 架构角色（两文件合并讲：测试策略之"冒烟"）

CleanRL 测试层的**第一道门**：17 行 + 9 行，四个测试函数，全部同构——`subprocess.run("python cleanrl/xxx.py <最小参数>", shell=True, check=True)`。合并讲它们是因为二者共享同一个测试哲学，而这份哲学值得单独命名：**跑通即通过**。

- test_atari.py:4-9 `test_ppo`：`ppo_atari.py --num-envs 1 --num-steps 64 --total-timesteps 256`
- test_atari.py:12-17 `test_ppo_lstm`：`ppo_atari_lstm.py --num-envs 4 --num-steps 64 --total-timesteps 256`（LSTM 版用 4 环境顺带覆盖时序 batch 维度）
- test_classic_control.py:4-9 `test_ppo`：`ppo.py --num-envs 1 --num-steps 64 --total-timesteps 256`

**参数不是随手填的**：256 步 = `num_envs(1) × num_steps(64) × 4 个 iteration`——恰好让 PPO 完整走 4 轮"采样→GAE→4 epoch 更新"闭环；再小（如 128）有些分支（学习率退火、第二iteration）走不到。同理 part1 的 ppo.py 默认 `num-minibatches=4`，256 步下 minibatch=16，梯度更新真的会执行。

**断言策略要诚实说明**：任务提示里说"epoch 断言"——**实测没有**。唯一的断言是 `check=True`（子进程退出码非 0 即 fail）。没有回报阈值、没有梯度检查、没有数值断言。这在 CI 语境下是刻意取舍：RL 训练效果断言既慢又脆（坏种子就能挂），而 256 步跑通已经能拦截最常见的整类回归——argparse 改名、dataclass 字段删除、张量形状改错、导入坏掉、CUDA 路径编译错。**它测的是"管道没断"，不是"水是甜的"**。真正做数值断言的另有其人：`tests/test_jax_compute_gae.py`（单测 GAE 与参考实现对拍，见 part2）。

**subprocess 而非 import 调用的深层理由**：测试的就是**用户真实执行路径**（CLI 入口 + tyro 解析 + `if __name__ == "__main__"`），连"脚本作为模块导入时是否有副作用"这类问题都被屏蔽；代价是每个测试分钟级、且失败时只有退出码没有 traceback（需去翻 stdout）。

### 外部连接

`.github/workflows/tests.yaml` 把两者放进**不同 job**：classic_control 在 core job（matrix python 3.8/3.9/3.10，12-13 行，`uv pip install ".[pytest]"`，29 行跑 pytest）；atari 在独立 job（`".[pytest, atari]"`，64-66 行）——依赖分舱：core 测试不要求装 atari 模拟器，atari 破坏不阻塞 classic CI。

---

## tests/test_mujoco.py + tests/test_tuner.py

**知识图谱**：test_mujoco tags: `test/smoke-test/mujoco/continuous-control`，complexity: moderate，tested_by 边 7 条（ddpg/td3/sac/ppo/rpo 各连续控制版含 jax）；test_tuner tags: `test/smoke-test/hyperparameter-tuning`，imports → cleanrl_utils/tuner.py，depends_on → cleanrl/ppo.py；两者同被 tests.yaml triggers。

### 架构角色（合并讲：冒烟策略的两个变奏）

**test_mujoco.py（77 行）——同一策略在依赖最重家族的展开**：

| 行号 | 测试 | 命令要点 |
|---|---|---|
| 4-14 | `test_ddpg` | torch + jax 两版；`--learning-starts 100 --batch-size 32 --total-timesteps 105` |
| 17-27 | `test_td3` | 同上两版 |
| 30-35 | `test_sac` | 仅 torch 版；`--batch-size 128 --total-timesteps 135` |
| 38-48 | `test_ppo` | **双环境后端**：Hopper-v4 与 `dm_control/cartpole-balance-v0` |
| 51-61 | `test_rpo` | 同样双后端 |
| 64-76 | `test_mujoco_eval` | 加 `--save-model`，验证检查点保存路径 |

三处策略升级值得记：① **参数学**——`learning-starts 100` + `total-timesteps 105`：off-policy 算法前 100 步只采样不学习，105 步意味着**恰好执行 1 次梯度更新**（105-100=5 步学习期）——把"学习分支是否可跑"压到最小代价；SAC 没有显式 learning-starts（默认 5e3 被覆盖为…其实是 `--total-timesteps 135` + 默认 learning_starts=5e3 时本不该学习，但 SAC 脚本在 timestep≥batch_size 后即开始更新，故 batch 128 + 135 步保证至少一次更新）。② **双环境后端**（44-47 行）——同一段算法代码跑 MuJoCo 原生与 dm_control 两种物理引擎包装，回归任何一个后端的适配层都被抓到。③ **--save-model 单独成测**（64-76 行）——保存路径/序列化是独立故障面，值得自己的绿灯。

CI 接线（tests.yaml:102-131）：mujoco job 安装 `".[pytest, mujoco, dm_control, jax]"` 一次性拉齐三套重依赖——这也是为什么 mujoco 测试不能并进 core job（装一次 MuJoCo 要几分钟）。

**test_tuner.py（33 行）——冒烟策略对基建代码的应用**：不 mock、不 patch，直接构造真实 `Tuner`（7-29 行）跑 `tune(num_trials=1, num_seeds=1)`（30-33 行）。配置即文档：`params_fn`（16-25 行）示范了搜索空间声明惯例——`suggest_float(log=True)` 给学习率（对数尺度是 RL 超参的标准做法）、`suggest_categorical` 给离散选择，并钉死 `total-timesteps=1200/num-envs=1` 压时长；`target_scores` 给 CartPole/Acrobot 双环境（12-15 行）——多环境迫使归一化路径执行；`MedianPruner(n_startup_trials=5)` + `TPESampler()`（26-27 行）是官方推荐的 sampler/pruner 组合（5 个启动 trial 内不剪枝——所以 1 trial 的冒烟里剪枝分支实际**未覆盖**，这是有意的省略：剪枝要 5+ trial 才触发，冒烟测不起）。它本质上是 tuner_example.py 的精简版，一条测试同时充当**使用示例文档**。

### 模式与坑（测试组合讲）

- 模式：**E2E 冒烟为主、数值单测为辅**（唯一单测 test_jax_compute_gae.py）——与 CleanRL "算法文件即单元"的结构对齐：测文件就是测整个闭环。
- 坑 1：subprocess 测试的失败诊断成本高——CI 红了常只是"退出码 1"，要开完整日志才见 traceback。
- 坑 2：所有测试 `shell=True` + 字符串命令（非列表），路径含空格时会炸——仓库内路径无空格所以从未触发，但属已知脆弱点。
- 坑 3：测试间共享 `runs/` 与 wandb 离线目录，本地连跑可能互相污染（tuner 测试读 event 文件时尤甚，见 tuner 坑 2）。

---

## requirements/requirements.txt

**知识图谱**：`document:requirements/requirements.txt` · tags: `dependencies/lockfile/core/build-system` · complexity: complex · 出边 configures → ppo.py/dqn.py（代表全部算法脚本）；入边 related ← docs/get-started/installation.md。

### 依赖版图（简讲）

这是 **12 份分舱锁文件**（requirements/ 目录：atari/cloud/dm_control/docs/envpool/jax/memory_gym/mujoco/optuna/pettingzoo/procgen + 本文件）中的**核心舱**。头两行（1-2 行）声明由 `uv export --no-hashes` 从根 pyproject.toml 生成——**单一事实源在 pyproject，本文件是导出物**，对应 part2 讲过的 `pip install "cleanrl[atari]"` extras 体系：核心舱装完即可跑 classic control，重依赖按环境族分舱按需加。

**直接依赖（`# via cleanrl` 标记）**——单文件算法们的公共运行时，共 11 个：

| 包 | 版本 | 用途归属 |
|---|---|---|
| torch | 2.4.1（225 行） | 全部算法 |
| gymnasium | 0.29.1（68 行） | 环境标准 API（新栈） |
| gym | 0.23.1（64 行） | 部分脚本仍用老 API（envpool 系，见 part2） |
| wandb | 0.13.11（257 行） | 实验追踪 |
| tensorboard | 2.11.2（219 行） | 日志（tuner 的指标读回依赖它，tuner.py:11） |
| tyro | 0.5.10（248 行） | dataclass→CLI 的参数解析 |
| moviepy | 1.0.3（93 行） | 训练视频合成（capture_video） |
| pygame | 2.1.0（172 行） | classic control 渲染 |
| rich | 11.2.0（190 行） | 终端美化输出 |
| huggingface-hub | 0.11.1（70 行） | enjoy/上传（enjoy.py:3） |
| tenacity | 8.2.3（217 行） | push_to_hub 重试（huggingface.py:8） |

其余 60+ 项是传递依赖的**精确锁定**：`# via xxx` 注释给出依赖链（如 absl-py via tensorboard，5 行）。两处版本版图细节值得看：**CUDA 全家桶**（112-146 行，nvidia-cublas/cudnn/nccl 等十余个 wheel，均带 `platform_machine == 'x86_64' and sys_platform == 'linux'` 环境标记——mac/Windows CPU 安装不会拖进这些）；**Python 版本分舱标记**（fsspec/sympy/networkx/typing-extensions 等按 `python_full_version` 分 3.8/3.9/3.10+ 给不同版本，48-50、213-215 行）——这是 uv export 对 CI matrix（3.8/3.9/3.10）的配套，一份锁文件覆盖三个解释器版本。开发工具 pre-commit（157 行）也锁在核心舱。

**与 huggingface.py 的呼应坑**：本文件体系是 uv/pyproject，但模型卡片仍教用户 `poetry install`（huggingface.py:75）——依赖工具的换代留下了这处叙事不一致（前文已点）。

---

## 收尾：三篇合起来的全景

至此 39 个核心文件讲完。本篇的 13 个文件构成 CleanRL 的**"算法之外的一切"**：atari_wrappers（观测标准化）与 buffers（经验存储）是算法脚本的左膀右臂——图谱上 11 条与 16 条入边是共享价值的直接计量；enjoy/huggingface 组成模型动物园的**生产-消费闭环**（push_to_hub 上传 ↔ enjoy 回放，`.cleanrl_model` 后缀与命名约定是接口）；reproduce/benchmark/tuner 是**实验管理三件套**（单次复现 / 批量网格 / 超参搜索），共同特征是"算法脚本零感知"——argv 进、文件系统出；四组冒烟测试用 256 步的最小闭环守住 CI；requirements 的 12 分舱锁文件让"装得起"与"跑得起"解耦。

把这层基建放回 part1 的单文件哲学：CleanRL 真正的设计命题从来不是"不共享"，而是**精确划出哪 5% 值得共享**——环境标准件、通用缓冲、工程流水线进库，一切算法语义留在文件里。这个边界感，比任何一处代码实现更值得搬走。
