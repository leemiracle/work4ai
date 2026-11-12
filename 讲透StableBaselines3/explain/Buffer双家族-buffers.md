# Buffer 双家族：Replay 与 Rollout 的 2×2 矩阵 —— stable_baselines3/common/buffers.py 精讲

> 源码：`stable_baselines3/common/buffers.py`（955 行）· 交叉：type_aliases.py、off/on_policy_algorithm.py

## 角色定位

全库经验存储的单一事实源：`BaseBuffer`（buffers.py:L27）加五个具体类构成 2×2 矩阵——{ReplayBuffer（buffers.py:L158）× RolloutBuffer（buffers.py:L343）}算法家族轴 × {平面向量 × Dict}（buffers.py:L525、buffers.py:L697）观测形态轴，外加 `NStepReplayBuffer`（buffers.py:L847）。

两家族语义差异是第一性的：**ReplayBuffer 是环形覆盖的长期记忆**——容量百万级、旧数据滚动覆盖、训练时无限次有放回重采样；**RolloutBuffer 是用完即弃的短窗口**——`buffer_size` 即 on-policy 算法（A2C/PPO）的 `n_steps`，攒满算完 GAE、喂完 epoch 后 `reset()`。两类同名 `buffer_size` 而语义完全不同。消费端由基类自动选型（off_policy_algorithm.py:L190-199、on_policy_algorithm.py:L119-123）。

## 内部结构

**BaseBuffer（buffers.py:L27-155）**：`pos`/`full` 游标（L57-58）、`device`（L59）、`n_envs`；`swap_and_flatten`（L62-75）；模板方法对 `sample → _get_samples`（L106-115 与抽象 L117）——基类用 `np.random.randint` 抽**有放回**索引（L114），取数细节留给子类；`to_torch`（L128-140）默认 `copy=True`；L142-155 是归一化挂点。

**ReplayBuffer（buffers.py:L158-340）**：L213-228 六族预分配数组（obs/next_obs/actions/rewards/dones/timeouts），形状统一 `[buffer_size, n_envs, ...]`；构造期做 n_envs 折算（L198）、psutil 内存告警（L230-245）、两开关互斥 raise（L206-210）。

**RolloutBuffer（buffers.py:L343-522）**：多存 `values/log_probs`（策略快照）、`advantages/returns`（GAE 产物）与 `episode_starts`（L391-399），持有 `gae_lambda/gamma`（L386-387）；灵魂方法是 `compute_returns_and_advantage`（L403-438）与生成器 `get`（L481-506）。**Dict 双胞胎**（L525/L697）把单 ndarray 换成 dict（L571-578、L746-751）；**NStepReplayBuffer**（L847）零额外存储，在 `_get_samples`（L886-954）现场算 n-step return。

## 外部连接

- **生产端**：on-policy 每步调 `rollout_buffer.add(obs, action, reward, episode_start, value, log_prob)`（on_policy_algorithm.py:L247），结尾用 V(last_obs) 收尾 GAE（on_policy_algorithm.py:L262）；off-policy 调五元组 `add`——两个签名即两家族的接口宣言。
- **产物契约**：`_get_samples` 返回 type_aliases.py 的 namedtuple——`RolloutBufferSamples`（L32）、`ReplayBufferSamples`（L50），后者带可选字段 `discounts`（type_aliases.py:L57），TD3 在 td3.py:L172-173 消费（n-step 注入点）。
- **VecNormalize**：归一化只发生在读出时（L317/L323），buffer 永远存原始值，统计漂移后旧样本自动按新统计重归一；`HerReplayBuffer`（重写 `add`）与 `save/load_replay_buffer`（off_policy_algorithm.py:L229-266）是扩展生态。

## 数据流

**Replay 写入** `add()`（buffers.py:L247-283）：观测与 action 先 reshape（L258-263）；逐字段 `np.array(...)` 拷贝防引用篡改（L266-275）；`timeouts` 从 `info["TimeLimit.truncated"]` 提取（L277-278）；游标环形推进（L280-283）。`extend()`（buffers.py:L91-97）实为 `zip` 循环逐条调 `add` 的兼容壳。

**Replay 读出**（buffers.py:L285-325）：`randint` 有放回抽行索引（L114），再随机抽 env 维（L309，各环境转移同权混采）；`dones * (1 - timeouts)`（L322）把超时截断改判非终止；`map(self.to_torch, data)` 转 tensor（L325）。

**Rollout 写入**（buffers.py:L440-479）：六元组 `add` 把 `value/log_prob` 从 GPU 拉回 numpy（L475-476）；游标到顶只置 `full` 不回零（L478-479），`assert self.full`（L482）是 `get()` 的完整性闸门。

**GAE 逆序单趟**（buffers.py:L403-438）：`last_values` 转 numpy（L423），`reversed(range(self.buffer_size))` 倒走（L426）。边界判定：末步用外部 `dones` 与 `last_values`（L427-429）——`dones` 语义是"buffer 之后首步是否 episode start"（on_policy_algorithm.py:L262 传 collect 结尾的 dones）；其余步用 `episode_starts[step+1]` 当 non-terminal mask、`values[step+1]` 当 bootstrap（L430-432）。两行递推 $\delta_t = r_t + \gamma V(s_{t+1})(1{-}d_{t+1}) - V(s_t)$（L433）、$A_t = \delta_t + \gamma\lambda(1{-}d_{t+1})A_{t+1}$（L434）；趟末 `returns = advantages + values`（L438）。逆序是必然：$A_t$ 依赖 $A_{t+1}$，单趟把 $O(n^2)$ 压成 $O(n)$。

**Rollout 读出** `get()`（buffers.py:L481-506）：`np.random.permutation` 无放回打乱（L483），首个 minibatch 触发六张量 `swap_and_flatten`（L485-497），按 batch_size 切片 yield。

## 设计决策

**1. numpy CPU 存储 + 采样期转 torch 的三重拷贝。** 一次 `sample` 产生三份拷贝：fancy indexing（numpy 语义决定）、可选归一化、`to_torch` 默认 `copy=True`（buffers.py:L128-140 自认：非 CPU 设备时 copy 参数无效）。批判：buffer 驻 GPU 则百万级图像观测击穿显存、与 vec env 接口错位；"CPU 常驻、按批传输"是正确折中，代价是每个 gradient step 重复 H2D 传输、无 pinned memory 异步化——对大 batch 的 SAC 这是最现实的瓶颈位。

**2. optimize_memory_usage：省一半内存，默认关。** 该变体砍掉整个 `next_observations` 数组，next_obs 复用 `observations[(pos+1) % buffer_size]`（buffers.py:L268-271），代价链三条：与 `handle_timeout_termination` 互斥（L206-210）；`self.pos` 槽位转移恒无效、采样须绕开（L301-304）；DictReplayBuffer 干脆禁用（L566）。默认 False——技术上可行、工程上不值的裁决：省内存，付三处隐性约束的长期维护成本。

**3. 两种采样语义不可互换 + 修正放读端。** Replay 有放回 `randint`（buffers.py:L114）vs Rollout 无放回 `permutation`（L483）——算法要求而非风格：off-policy 的 SGD 需近 i.i.d. 重采样；PPO 多 epoch 要求每条数据恰用一次，clip ratio 校正只对同批 `old_log_prob` 有效。连带：`timeouts` 与 `dones` 分列（L224/L228），修正放读端 `dones*(1-timeouts)`（L322）——TimeLimit 截断非 MDP 终止，读端合成让 `add()` 照单全收。另须警惕 Dict 变体的"跳父类"继承：`super(ReplayBuffer, self).__init__`（L557）、`super(ReplayBuffer, self).sample`（L662）、`super(RolloutBuffer, self)`（L736/L760）借 MRO 跳过直接父类直达 BaseBuffer——复用模板又不触发父类平面向量分配，代价是 IDE 跳转失效、父类改签名时隐式契约静默破裂。

## 新人提示

- **同参数不同义**：RolloutBuffer 的 `buffer_size` 是"每次更新的 rollout 长度"（= PPO 的 `n_steps`），ReplayBuffer 的才是"记忆容量"。
- **n_envs 折算**（L198）：`buffer_size=1_000_000` 且 `n_envs=8` 时每环境只存 125k，总量守恒但直觉常错。
- 自定义 buffer 三条正路：传 `replay_buffer_class`、只 override `_get_samples`（NStepReplayBuffer 范本，注意 L941 采样后还原 `timeouts` 临时改动）、HER 式重写 `add`；改公共基类波及全部算法。
- GAE 出 NaN 或 advantage 全零，先查 `episode_starts` 喂入（L431 的 mask 全 0 会压扁优势），再查 `dones` 语义——应传"下一段首步是否新 episode"而非"本步 done"，传反不报错只算错。
- `add()` 的 `np.array()` 包装（buffers.py:L266）是防引用共享的写拷贝，别为性能删——否则外部数组原地更新会污染历史样本。
- `assert self.full`（buffers.py:L482）离病因很远：少 add 或多 add 一步都只在这里爆，排查回到 collect 循环。

---
> 元数据：字数（不计空格）4799 | 行号锚 28 处文件限定 + 56 处裸 L 引用（buffers.py 为主，交叉 type_aliases.py / off_policy_algorithm.py / on_policy_algorithm.py / td3.py）| 六节自查：角色定位✓ 内部结构✓ 外部连接✓ 数据流✓ 设计决策（3 组批判性权衡）✓ 新人提示✓ | 源码基线 commit b2878f4
