# VecNormalize 与 RunningMeanStd：向量化环境的在线统计归一化

> 源码：common/vec_env/vec_normalize.py（333 行）+ common/running_mean_std.py（56 行）

## 一、角色定位

RL 对尺度极敏感：网络假设输入近零均值单位方差，value loss 量纲随 reward 尺度线性放大，MuJoCo 观测各维量纲可差 7 个数量级。VecNormalize 是 SB3 的总答案：**在线估计 running 统计、归一化观测与奖励的 VecEnvWrapper**（vec_normalize.py:L15），让策略永远看到近似 N(0,1) 的世界。

统计引擎 RunningMeanStd 在 `common/running_mean_std.py` 而**不在** `common/vec_env/` 下（vec_normalize.py:L11 的 import 是实证），56 行实现 Chan et al. 并行方差合并算法（running_mean_std.py:L8），即 Welford 在线算法的批量版本。

内部维护**两套统计**：`obs_rms` 逐维归一化观测（vec_normalize.py:L58 dict 分支 / L71 扁平分支）；`ret_rms` 是**标量**（L88），归一化的不是单步 reward 而是 gamma 折扣回报 R_t（与普通 reward scaling 的本质区别）。它也是 SB3 唯一内置 save/load 持久化的 wrapper（L310-322/L324-332）。

## 二、内部结构

**构造参数即全部超参**（vec_normalize.py:L35-46）：`training`、`norm_obs`/`norm_reward`（默认都开）、`clip_obs=clip_reward=10.0`（L41-42）、`gamma=0.99`、`epsilon=1e-8`（L44，防除零）、`norm_obs_keys`（L45，Dict 观测选择性归一化）。

**Dict 观测**：每个 key 建独立 RunningMeanStd（vec_normalize.py:L58）；`_sanity_checks`（L100-126）要求被归一化 key 必须 Box（L109-116），flat Box 传 norm_obs_keys 报 ValueError（L119-120），不传默认全归一化（L106-107）。**图像特判**：image space 会把 observation_space 改写为 `Box(-clip_obs, clip_obs, float32)`（L61-68/L80-86）——与 policy 侧 normalize_images 的冲突见 L74-79 注释（GH#1214）。

**RunningMeanStd 本体**（running_mean_std.py）：状态仅三个——`mean=0`、`var=1`、`count=1e-4` 伪计数（L13-15），防除零且让最初几步变换近恒等。核心 `update_from_moments`（L41-55）是 Chan 合并：`delta = batch_mean - mean`（L42），`new_mean = mean + delta*batch_count/tot`（L45），`m_2 = var*count + batch_var*batch_count + delta²*count*batch_count/tot`（L46-48），`new_var = m_2/tot`（L49）——O(1) 内存、数值稳定、天然批量（`update` L35-39 一次吃 (batch, dim)），统计全程 float64（L13-14）。

**pickle 协议**：`__getstate__` 剔除 venv/class_attributes/returns（vec_normalize.py:L128-139）；`__setstate__` 向后兼容，旧 pickle 无 norm_obs_keys 时回填全部 key（L149-150）；`set_venv` 只许一次（L163-164）。

## 三、外部连接

**向上**：继承 VecEnvWrapper，只覆写 `step_wait`/`reset`（vec_normalize.py:L174/L292），算法层无感。

**与 off-policy replay buffer 的协作**是条关键暗线：buffer 永远存**未归一化**原始数据——`_store_transition` 经 `get_original_obs()`/`get_original_reward()`（vec_normalize.py:L279-290，存于 L183-184）取 raw 入库，terminal_observation 显式 `unnormalize_obs`（off_policy_algorithm.py:L502/L510）；采样时 `sample(env=self.env)` 调回 `normalize_obs/normalize_reward`（L232/L250，经 buffers.py:L143-155）。即**归一化推迟到采样时刻、用最新统计**。

**评估工作流**：`VecNormalize.load(path, venv)`（vec_normalize.py:L310-322）；配套 `unwrap_vec_normalize`（common/vec_env/__init__.py:L35）与 `sync_envs_normalization`（同文件 L56）。RL Zoo 标准三连：`training=False; norm_obs=True; norm_reward=False`。

**与 Gymnasium NormalizeObservation 的差异**：Gym 版单 env 逐条更新、观测归一化**无 clip**（离群观测直接击穿下游网络）、无 norm_obs_keys、无统计持久化、无 terminal_observation 同步，其 NormalizeReward 同用折扣回报但同样缺 clip；VecNormalize 批量更新、与 SubprocVecEnv 兼容——教学实现 vs 工程实现。

## 四、数据流

`step_wait`（vec_normalize.py:L174-207）顺序即语义：①L181 拿 raw 四元组；②L183-184 存 old_obs/old_reward（必须在归一化前）；③L186-191 `training and norm_obs` 才更新 obs 统计——**先更新后变换**；④L193 normalize_obs；⑤L195-196 `if training` 更新 reward 统计——**只看 training 不看 norm_reward**；⑥L197 normalize_reward；⑦L199-204 把 done 环境的 `terminal_observation` 也过 normalize_obs——Q(s',a) bootstrap 需要它，漏掉则 next_obs 分布在末尾突变；⑧L206 `returns[dones]=0`，episode 边界重置累积器。

`_update_reward`（vec_normalize.py:L209-212）两行承载全部语义：`returns = returns*gamma + reward` 得每环境 R_t，`ret_rms.update(self.returns)`——**喂统计的是折扣回报向量而非单步 reward**，故 normalize_reward（L250-259）除 `sqrt(Var[R_t]+ε)`（L256）：value target 尺度由回报决定，归一化 R_t 才能让 value loss 跨环境稳定。正逆变换对称：obs 侧 `clip((x-mean)/sqrt(var+ε), ±clip_obs)`（L221）/乘回加 mean（L230），reward 侧除 std（L256）/乘回（L276），出口统一 `astype(float32)`（L244/L247/L259）。

**训练/评估开关矩阵**：

| training | norm_obs | norm_reward | 行为 |
|---|---|---|---|
| True | True | True | 全速：双统计持续更新（L186/L195） |
| True | True | False | obs 归一化；**ret_rms 仍在累积**（L195 不查 norm_reward） |
| False | True | False | 标准 eval：统计冻结，reward 原样返回真实值 |
| False | True | True | eval + 归一化 reward（看真实性能须关掉） |

## 五、设计决策

**权衡一：reward 统计更新与 norm_reward 解耦**（vec_normalize.py:L195 vs L255）。obs 更新被双条件门控（L186），reward 只看 training。收益：中途开 norm_reward 立即有统计；代价：显式传 `norm_reward=False` 却仍付每步统计更新的计算，语义反直觉且无文档提示。

**权衡二：归一化折扣回报而非单步 reward**。收益：value target 尺度不随环境漂移。批判地看：与 gamma 耦合，换 gamma 等于换归一化基准；且只做输入侧归一化、没有 PopArt 式 value 头输出侧同步 rescaling——统计漂移的训练早期 value 网络在追移动目标，正是 PopArt 论文指出的一类性能损失。SB3 选了简单够用的一端。

**权衡三：pickle 整个对象而非只存统计数组**（vec_normalize.py:L324-332 一行 dump）。好处：统计与超参原子绑定、eval 一条命令；坏处：跨版本脆弱（L149-150 兼容垫片即补丁证据）与 pickle.load 任意代码执行风险。

**权衡四：buffer 存 raw、采样时归一化**。历史数据在不同时刻被**不同统计**重新解释——好处是自动享受更准的归一化；代价是 off-policy 分布严格非平稳，terminal_observation 还需往返补偿（见外部连接）。

**数值边界**：epsilon=1e-8 只防除零不防 var 抖动——早期 var 估计高方差，第一道防线是 ±10 双闸（vec_normalize.py:L41-42）；初始 var=1+伪计数（running_mean_std.py:L14-15）保证起步近恒等。

## 六、新人提示

1. **eval 三件套缺一不可**：`VecNormalize.load` → `training=False` → `norm_reward=False`——忘关 norm_reward 看到的是被除过 std 的缩水回报。
2. `norm_obs_keys` 是 Dict 环境（HER/Fetch 类）关键旋钮，goal 键归不归一化要显式决定（不传默认全归一化，vec_normalize.py:L106-107）。
3. `get_original_obs()` 只返回**最近一次** step/reset 的原始观测（L279-284）；`model.save` 不含归一化统计，必须单独 `vec_normalize.save(...)`，否则 eval 统计从零开始。
4. 读代码盯住不变式：**old_obs 永远 raw（L183/L299 在归一化前赋值），算法看到的永远 normalized**，全文件围绕这对镜像组织。

> 元数据：4727 字（不计空格）｜锚 68｜vec_normalize+running_mean_std@b2878f4｜2026-10-14
