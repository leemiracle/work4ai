# HerReplayBuffer：Hindsight Experience Replay 的虚拟重标注引擎

> 源码：her/her_replay_buffer.py（409 行）+ goal_selection_strategy.py + __init__.py

## 一、角色定位

先钉一个高频误解：**HER 在 SB3 里不是算法，是 replay buffer 方案**——`her/` 只有 her_replay_buffer.py、goal_selection_strategy.py、__init__.py 三个文件，无独立算法文件；__init__.py:L1-4 只导出两个公共名：`GoalSelectionStrategy` 与 `HerReplayBuffer`。用法是作为 `replay_buffer_class` 传给任意 off-policy 算法（TD3/DDPG/SAC），OffPolicyAlgorithm 注入 env（off_policy_algorithm.py:L205-207）——重标注完全发生在采样管道内部。

它解决 **sparse reward**：goal-conditioned 环境常用二值奖励——achieved_goal 精确等于 desired_goal 才给 0，随机探索下 transition 几乎全 -1。HER（arXiv:1707.01495，her_replay_buffer.py:L17-18）的洞见：失败轨迹是**相对别的 goal 的成功轨迹**——把 desired_goal 替换成轨迹**实际到达**的 achieved_goal 再重算 reward，失败经验就被事后（hindsight）改写成成功教材。

## 二、内部结构

**目标选择策略**（goal_selection_strategy.py）：三值 Enum——FUTURE=0（L12，当前步**之后**同 episode 某状态）、FINAL=1（L15 末状态）、EPISODE=2（L17 全 episode 均匀），加字符串映射 KEY_TO_GOAL_STRATEGY（L22-26）；构造函数字符串小写查表（her_replay_buffer.py:L77-80）+ assert（L83-85）。

**继承与新增状态**：HerReplayBuffer 继承 DictReplayBuffer（her_replay_buffer.py:L15），新增——①`self.env`（L73，重算 reward 须问环境）；②`her_ratio = 1 - 1/(n_sampled_goal+1)`（L90），默认 n=4（L60）即 80% minibatch 是虚拟 transition；③infos 的 object 数组（L92）；④**episode 簿记三件套**（L97-99）：`ep_start`/`ep_length` 记每条 transition 所属 episode 起点与总长、`_current_ep_start` 记进行中起点——episode 边界即重标注坐标系。

**环形覆盖防护与 episode 收尾**：buffer 回绕会从旧 episode 中间覆盖产生残缺 episode；写入前把旧 episode 整段 ep_length 清零（L144-154），采样以 `ep_length > 0` 为有效判据（L196）。done 时 `_compute_episode_length`（L169-184）处理回绕（L177-180）并整段写 ep_length（L181-182）。**pickle 协议**与 VecNormalize 同套路：`__getstate__` 剔除 env（L101-110），`set_env` 只许一次（L124-133），加载侧回接（off_policy_algorithm.py:L262-264）。

## 三、外部连接

**GoalEnv 协议**（硬约定）：环境须是 Gymnasium-Robotics / panda-gym 风格：观测含 `desired_goal`/`achieved_goal` 键（硬编码于 L312-314/L384）且实现 `compute_reward(achieved_goal, desired_goal, info)`；重算走 `env.env_method(..., indices=[0])`（L320-334）——只用第 0 个子环境，**假设所有子环境同构**（L332-333）。

**与 VecNormalize 的三明治协作**：①存入 buffer 存 raw obs/reward（off_policy_algorithm.py:L485-487）；②采样 `sample(env=VecNormalize)` 在**采样时刻**归一化（her_replay_buffer.py:L264-267/L336-337/L352）。虚拟样本微妙：compute_reward 收到 raw goal——L320 在 L336 之前，reward 在原始空间算、归一化只在出口做。

**timeout 语义**（handle_timeout_termination=True 默认，L59）：TimeLimit 截断的 done 并非吸收态；两处采样出口都做 `dones * (1 - timeouts)` 剥离（L281-283、L349-351），让截断步参与 bootstrap（issue #284，L35-37）。

**truncate_last_trajectory**（L386-408）：load 旧 buffer 时最后一条轨迹可能未完结（ep_length 全 0）；把 `dones[pos-1]` 强制 True（L402）并补算长度（L405），handle_timeout_termination 开着还把 `timeouts[pos-1]` 置 True（L407-408）——注释直言："not an actual timeout, but it allows bootstrapping"：人工截断非真终止，标成 timeout 恰好让剥离逻辑还原成非终止、Q bootstrap 延续——**语义借用**。

## 四、数据流

**写入流**（add，her_replay_buffer.py:L135-163）：清残缺旧 episode → 记 episode 起点（L157）→ 可选存 infos（L159-160）→ 父类落盘（L162）→ done 则收尾（L165-167）。

**采样流**（sample，L186-246）是 HER 心脏：①`is_valid = ep_length > 0`（L196），全无效则 RuntimeError（L197-201，文案即文档）；②`np.random.choice`（L212）+ `np.unravel_index` 拆回 (batch_idx, env_idx)（L215）；③`nb_virtual = int(her_ratio*batch_size)`（L218），`np.split` 一刀两段（L219-220）——同批索引前 80% 重标注、后 20% 保真；④真实样本（L248-285）：取数→归一化→to_torch→剥 timeout；⑤虚拟样本（L287-353）：`_sample_goals` 抽新目标（L311）→ **新 goal 双写** obs 与 next_obs 的 desired_goal 同值（L312-314）→ **重算 reward**：第一个参数是 **next_obs** 的 achieved_goal（L328；L322-327 注释：r_t = reward(next_achieved_goal, desired_goal)）→ 归一化（L336-337）→ 剥 timeout（L349-351）→ th.cat 拼回（L228-238）。

**三策略几何**（_sample_goals，L355-384）：FINAL 取 `ep_length-1` 即末态（L366-368）；FUTURE 先算当前步 episode 内序号再 `randint(current, ep_length)`（L370-374）；EPISODE 直接 `randint(0, ep_length)`（L376-378）。都经 `(idx+ep_start) % buffer_size` 回环形下标（L383），取 **next**_observations 的 achieved_goal（L384）。FUTURE 是 **inclusive** 的（含当前步，L374、L22-25 note 标注与其它实现不同）。

## 五、设计决策

**权衡一：sample-time 重标注 vs add-time 重写 vs online sampling**。原论文的 offline（replay 时重标注）/online（执行时按新 goal 选动作）两变体中，SB3 只实现前者，且**每次 sample 重新抽 goal**（而非 add 时物化虚拟 transition）——一条物理轨迹被反复以不同 goal 采出，数据利用率倍增。代价：compute_reward 高频调用（SubprocVecEnv 下是 IPC 往返，L320）；且 minibatch 内 80% 样本共享同一批物理 transition（L219-220 同批 split 非独立采样）。online 变体需策略按虚拟 goal 前向，与 off-policy 循环结构不兼容，未实现。

**权衡二：env_method(indices=[0]) 的同构假设**（L332-333）。标准场景正确且省 n-1 倍调用；但 domain randomization 或异构并行下 reward 重算系统性有偏，且**无任何警告**——常见情形优化到极致，长尾静默丢弃。

**权衡三：infos 无条件预分配**（L92）。即使 copy_info_dict=False（默认）也构造 (buffer_size×n_envs) object 数组（1e6×8 即八百万个空 dict）；惰性分配本可实现，现状是简单性压过内存纪律。her_ratio 公式（L90）把"重标注比例"与"重采样次数"焊死，50% 虚拟消融只能改源码；残缺 episode 清零（L144-154）同理——选正确性，代价是回绕时整段旧 episode 作废。

## 六、新人提示

1. **learning_starts 必须 > 最长 episode 步数**——首个 episode 结束前 sample 必 RuntimeError（her_replay_buffer.py:L197-201）；n_sampled_goal 调大更稠密但 compute_reward 调用线性变多。
2. 环境必须实现 `compute_reward` 且观测 Dict 必含 `desired_goal`/`achieved_goal`——L312/L384 硬编码，缺了直接 KeyError。
3. load 旧 buffer 内含 env=None，须经 `model.load_replay_buffer(path)` 回接（off_policy_algorithm.py:L262-264）；truncate_last_traj（L248-251）决定最后轨迹截断还是续写。
4. 读环形 buffer 盯住 `% self.buffer_size`：episode 可横跨 pos=0 回绕点，L153/L181/L373/L383 四处取模缺一不可；与 VecNormalize 组合时重标注在 raw 空间算（L320 先于 L336），魔改 sample 保持此顺序。
5. FUTURE 是 inclusive 的，与 baselines/CleanRL 对比时这半步之差足以影响样本效率结论。

> 元数据：4737 字（不计空格）｜锚 87｜her_replay_buffer@b2878f4｜2026-10-14
