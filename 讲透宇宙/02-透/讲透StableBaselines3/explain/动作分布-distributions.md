# 动作分布 distributions.py：策略网络的最后一公里

## 一、角色定位

distributions.py 把策略网络的 latent features 变成环境能吃的动作：将网络输出参数化为概率分布，供给采样、log_prob、entropy。738 行、依赖仅 torch/gymnasium；被 ActorCriticPolicy 挂在 `action_dist` 槽位（policies.py:L533），服务 PPO/A2C 全部 on-policy 家族，也是 SAC 采样器的底层。定位即"动作头工厂 + 采样语义规范"。

## 二、内部结构

骨架是 `Distribution` ABC（distributions.py:L26），8 个抽象成员两两成对：`proba_distribution_net` 建网络与参数、`proba_distribution` 填参物化 torch 分布；`sample` 对 `mode`；`actions_from_params` 对 `log_prob_from_params`；`log_prob` 与 `entropy`（后者返回 `| None`，squash 后无解析形式）（distributions.py:L35、L42、L66、L74、L94、L103、L49、L58）。唯一具体方法 `get_actions`（distributions.py:L82）按 deterministic 二选一 mode/sample。`sum_independent_dims`（distributions.py:L112）把"对角协方差⇒各维独立⇒沿动作维求和"固化成三行，供全部连续分布复用。

六个具体分布：`DiagGaussianDistribution`（distributions.py:L127）是 Box 默认，`proba_distribution_net` 返回 mean 头 `nn.Linear` 加与状态无关的 `log_std` 参数（distributions.py:L150-152），TODO 注释明示动作相关 std 不支持。`SquashedDiagGaussianDistribution`（distributions.py:L209）继承之，加 tanh 界定与 pre-tanh 旁路 `gaussian_actions`（distributions.py:L220-221）。`CategoricalDistribution`（distributions.py:L265）单 logits 头；`MultiCategoricalDistribution`（distributions.py:L318）的 `distribution` 是 `list[Categorical]`，由 `th.split` 按子空间切扁平 logits（distributions.py:L325、L348）；`BernoulliDistribution`（distributions.py:L377）走 Bernoulli logits。`StateDependentNoiseDistribution`（distributions.py:L429）实现 gSDE（arXiv:2005.05719），参数含 full_std/use_expln/squash_output/learn_features（distributions.py:L432、L459、L475）。`TanhBijector`（distributions.py:L627）提供 forward/稳定 atanh/带 clamp 的 inverse/雅可比修正（distributions.py:L640-665）。收尾是工厂 make_proba_distribution 与 kl_divergence（distributions.py:L670、L705）。

## 三、外部连接

上游：`ActorCriticPolicy.__init__` 调工厂，use_sde 时打包 dist_kwargs 并断言 squash_output 必须搭配 use_sde（policies.py:L519、L533）；`_build` 与 `_get_action_dist_from_latent` 均按 isinstance 分派，SDE 分支是唯一需要 latent_pi 本身的（policies.py:L600、L704）——噪声方差依赖特征。`reset_noise`（断言 SDE，policies.py:L567）由 on_policy_algorithm.py:L190 每 rollout 调一次，sac.py:L227 采样时也调。

下游关键分叉：工厂对 Box 只在 SDE 与 DiagGaussian 间二选一（distributions.py:L685-687），从不返回 SquashedDiagGaussian——SACPolicy 绕过工厂直接实例化它，`actions_from_params/log_prob_from_params` 也只有 SAC 消费（sac/policies.py:L101、L170-175）。工厂其余路由：Discrete→Categorical、MultiDiscrete→MultiCategorical、MultiBinary→Bernoulli、其余 NotImplementedError（distributions.py:L688-697）。

两处勘误。其一，"Bernoulli/MultiCategorical 存在但默认未启用"只在主流 benchmark（MuJoCo Box、CartPole Discrete）意义上成立——它们在工厂里完全接线，接入对应 action space 即激活，并非死代码；真正绕过工厂的只有 SquashedDiagGaussian。疵点：Bernoulli 构造参数名 `action_dims` 与兄弟类不一致（distributions.py:L386）；MultiCategorical 的 list 包装喂不进 torch KL，逼出 `kl_divergence` 手写特判（distributions.py:L718-731）。其二，`kl_divergence` 核心库零调用——PPO 的 approx_kl 走 log_ratio 估计（ppo.py:L264），它是给 contrib 导出的 API。

## 四、数据流

采样流：obs → latent_pi → action_net 得 mean/logits → `proba_distribution` 物化 `self.distribution` → `get_actions`。DiagGaussian 的 sample 用 `rsample`（重参数化以传梯度）、mode 取 mean（distributions.py:L185、L188）。SDE 更深一层：sample = mean + noise（distributions.py:L587-592），noise 由 `get_noise` 双路分发——batch 为 1 或长度不匹配时全体 env 共享 `exploration_mat`（`th.mm`），并行探索对齐时逐 env `th.bmm`（distributions.py:L600-609）。噪声矩阵由 `sample_weights` 预采样、reset_noise 每 rollout 重采样（distributions.py:L506-519）：rollout 内恒定、跨 rollout 换新，即 gSDE 时序语义。分布本体 variance = `th.mm(latent_sde², std²)` → `Normal(mean, sqrt(var+ε))`，latent_sde 默认 detach（distributions.py:L548-563）。

训练流（evaluate_actions）：用存储动作重新物化分布再取 log_prob。SquashedDiag 关键在旁路：sample 时把 pre-tanh 动作存入 `gaussian_actions`，`log_prob_from_params` 复用它避免有损反演（distributions.py:L251-262）；只有外部拿 tanh 后动作来问才走 `TanhBijector.inverse`，其先 clamp 到 ±(1−eps)（distributions.py:L661-663）。log_prob 的 tanh 修正项 −Σlog(1−a²+ε) 即变量替换雅可比，取自 SAC 原版（distributions.py:L241）。带 squash 的两分布 entropy 均返回 None（distributions.py:L244、L581），上层须容忍。

## 五、设计决策

**权衡一：有状态分布对象。** 物化后 log_prob/entropy 才可用，docstring 明确警告顺序（distributions.py:L172）。换来极简调用面——policy 持一个实例反复填参；代价是顺序错误全是隐性 bug，SquashedDiag 把"最近一次采样"藏进 `gaussian_actions`（distributions.py:L221），正确性依赖"先 sample 后 log_prob"时序。

**权衡二：薄封装 torch.distributions。** log_prob/entropy 全部委托 torch（distributions.py:L177、L181），省实现且继承数值稳定性；但 `mode` 是 SB3 自有概念，MultiCategorical 的 list 包装又破坏"一切皆 torch 分布"抽象，逼出 kl_divergence 类型分叉（distributions.py:L718）。

**权衡三：rsample 全库统一。** 采样一律 rsample（distributions.py:L185、L517-519）：对 PPO 的 Gaussian 本不必要，但 SAC 必需——动作要穿 tanh 反传到分布参数。为一个消费者统一全库，是"减分支"压倒"最小开销"。

**权衡四：SDE 的 std 参数化。** 默认 `exp` 够用（distributions.py:L498）；use_expln 分段保方差恒正且增长受控，代价是分段点梯度不连续（distributions.py:L488-495）；full_std=False 广播 `(latent_sde_dim,1)` 砍参数（distributions.py:L504）。暗坑：log_std_init 双默认——DiagGaussian 为 0.0、SDE 为 −2.0（distributions.py:L140、L522），跨分布迁移超参易踩空。

## 六、新人提示

先物化再取值：对未物化的分布调 log_prob 拿到 AttributeError 或脏值。deterministic 只切换 mode/sample（distributions.py:L82-91）。mode 是硬选择：Categorical 取 argmax(probs)、Bernoulli 取 round(probs)（distributions.py:L305、L416），不可导仅评估。squash_output=True 必须搭配 use_sde=True（policies.py:L519）。SDE 排查记三层：log_std 可学习 → sample_weights 生成噪声矩阵 → get_noise 按批分发（distributions.py:L506、L600），忘调 reset_noise 会让同一噪声矩阵贯穿全程。

> 元数据：非空格字符 4794 ｜ 锚 51 组/去重 79 个（主 distributions.py，交叉 5 文件）｜ 六节齐/4 组权衡 ｜ @master(b2878f4)
