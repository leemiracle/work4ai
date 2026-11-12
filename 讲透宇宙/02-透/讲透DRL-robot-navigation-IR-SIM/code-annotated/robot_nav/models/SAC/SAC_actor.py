# ============================================================================ #
# 【文件】SAC 策略网络（Actor）——SAC（Soft Actor-Critic，最大熵 Actor-Critic）
# 算法的"演员"：读观测、吐动作分布。SAC 在最大化回报之外还最大化策略熵（保持探索），
# 因此策略输出的是"分布"而非单个动作；本文件实现其核心组件 tanh 压缩对角高斯策略。
# 流程位置：SAC.py 中 self.actor(obs) 返回下方的 SquashedNormal；dist.rsample() 采出
# 动作∈(−1,1) 并反传梯度，dist.log_prob(a) 取修正后的对数概率，评测时用 dist.mean。
# ============================================================================ #
import torch  # PyTorch 主库：张量运算 + 自动微分（策略梯度全靠它反传）
import math  # 标准数学库：下文用 math.log(2.0) 构造数值稳定的 log-prob 修正项
from torch import nn  # 神经网络模块库：nn.Module 基类、层定义、容器
import torch.nn.functional as F  # 函数式算子库：下文用 F.softplus 组装稳定公式
from torch import distributions as pyd  # 概率分布库：Normal 高斯、Transform 变换、TransformedDistribution

import robot_nav.models.SAC.SAC_utils as utils  # 本仓工具模块：mlp() 搭网络 + weight_init() 正交初始化


# ============================== 类：TanhTransform ============================== #
# 职责：把实数轴上的样本压进 [−1,1] 的可逆（双射）变换——tanh。
# 为什么需要：连续动作空间有界（本项目线/角速度归一化到 [−1,1]），高斯直接采样会越界；
# 而 tanh 会扭曲概率密度，故配套实现逆变换与雅可比修正，log_prob 才算得对。
# 流程位置：被 SquashedNormal 挂在基础高斯之后，构成"先采高斯、再 tanh 压缩"的采样链。
class TanhTransform(pyd.transforms.Transform):  # 继承 PyTorch 的 Transform 基类，按协议实现 _call/_inverse/雅可比
    """
    A bijective transformation that applies the hyperbolic tangent function.

    This is used to squash the output of a normal distribution to be within [-1, 1],
    making it suitable for bounded continuous action spaces.

    Attributes:
        domain: The input domain (real numbers).
        codomain: The output codomain (interval between -1 and 1).
        bijective: Whether the transform is bijective (True).
        sign: The sign of the Jacobian determinant (positive).
    """

    domain = pyd.constraints.real  # 变换前支撑集：整条实数轴 R（高斯能取到的全部值）
    codomain = pyd.constraints.interval(-1.0, 1.0)  # 变换后值域：[−1,1]（tanh 的输出范围）
    bijective = True  # 声明双射（一一对应）：能用变量替换公式修正 log_prob 的前提
    sign = +1  # 雅可比行列式符号：tanh 单调递增恒为 +1（供分布框架做体积换算）

    # 构造：cache_size=1 缓存最近一次 (输入,输出)——rsample 之后紧接 log_prob 时
    # 复用同一个 x，避开 tanh 边界 ±1 处 atanh 的数值发散（见 _inverse 的英文注释）。
    def __init__(self, cache_size=1):  # cache_size：缓存容量，默认 1 恰好覆盖"采样→算概率"成对调用
        """
        Initialize the TanhTransform.

        Args:
            cache_size (int): Size of the cache for storing intermediate values.
        """
        super().__init__(cache_size=cache_size)  # 调父类 Transform 构造器，启用其缓存机制

    # 静态工具：反双曲正切 atanh——tanh 的逆函数，把 (−1,1) 映射回实数轴；逐元素作用。
    @staticmethod  # 静态方法：不依赖实例状态，可 TanhTransform.atanh(x) 直接调用
    def atanh(x):  # x：任意形状张量
        """
        Inverse hyperbolic tangent function.

        Args:
            x (Tensor): Input tensor.

        Returns:
            Tensor: atanh(x)
        """
        return 0.5 * (x.log1p() - (-x).log1p())  # 稳定公式 atanh(x)=½[ln(1+x)−ln(1−x)]；log1p 对小 x 精度高，形状不变

    # 相等判断：变换框架内部按对象做比较/缓存时需要；同类型即视为相等。
    def __eq__(self, other):  # other：待比较的另一对象
        """
        Equality check for the transform.

        Returns:
            bool: True if the other object is also a TanhTransform.
        """
        return isinstance(other, TanhTransform)  # 只要是 TanhTransform 就相等（不比较参数）

    # 正向变换：高斯样本 u → 动作 a=tanh(u)；x 任意形状（如 (batch, action_dim)）。
    def _call(self, x):  # Transform 协议：分布采样后调用本方法套变换（前向）
        """
        Forward transformation.

        Args:
            x (Tensor): Input tensor.

        Returns:
            Tensor: tanh(x)
        """
        return x.tanh()  # 逐元素 tanh：R → (−1,1)，形状不变

    # 逆向变换：动作 a∈(−1,1) → 高斯样本 u=atanh(a)；log_prob 内部先逆回 u 查高斯密度。
    def _inverse(self, y):  # Transform 协议：y 是压缩后的动作
        """
        Inverse transformation.

        Args:
            y (Tensor): Input tensor in [-1, 1].

        Returns:
            Tensor: atanh(y)
        """
        # 【译注】此处故意不对 y 做边界截断（clamp）——截断会损害部分算法的性能；
        # 正确做法是改用 cache_size=1 缓存，保证算 log_prob 用的就是采样时的那个 x。
        # We do not clamp to the boundary here as it may degrade the performance of certain algorithms.
        # one should use `cache_size=1` instead
        return self.atanh(y)  # 直接 atanh：(−1,1) → R，形状不变

    # ★ 全文件最核心：log-prob 的雅可比修正项（对数行列式绝对值）。
    # 变量替换公式：π(a)=π(u)·|du/da| ⇒ logπ(a)=logπ(u)−log|det J|；tanh 逐维作用时
    # |du/da|=1−tanh(u)²，故本函数返回 log(1−tanh(x)²)。若漏掉这项，策略熵会被高估、
    # SAC 的最大熵目标失真——这是 squash 策略最经典的坑。
    def log_abs_det_jacobian(self, x, y):  # x=变换前样本，y=变换后样本（本式未用到）；返回同形状修正项
        """
        Log absolute determinant of the Jacobian of the transformation.

        Args:
            x (Tensor): Input tensor.
            y (Tensor): Output tensor.

        Returns:
            Tensor: log|det(Jacobian)|
        """
        # 【译注】用恒等式 log(1−tanh²x)=2(log2−x−softplus(−2x)) 的数值稳定形式：
        # 直接算 1−tanh²x 在 |x| 大时下溢为 0、log 变 −inf；此式恒有界不炸。
        # We use a formula that is more numerically stable, see details in the following link
        # https://github.com/tensorflow/probability/commit/ef6bb176e0ebd1cf6e25c6b5cecdd2428c22963f#diff-e120f70e92e6741bca649f04fcd907b7
        return 2.0 * (math.log(2.0) - x - F.softplus(-2.0 * x))  # 即 log(1−tanh(x)²)；形状同 x


# ============================== 类：SquashedNormal ============================== #
# 职责：把"对角高斯 + tanh 压缩"打包成一个可采样、可算熵、可反传梯度的分布对象。
# 输入：loc=均值 μ、scale=标准差 σ，形状均 (batch, action_dim)；"对角"指各维独立。
# 能力：rsample()=重参数化采样（梯度能穿过随机节点流回网络，策略梯度必需）、
# log_prob()=自动走 _inverse+雅可比修正、mean=tanh(μ) 确定性动作（评测用）。
class SquashedNormal(pyd.transformed_distribution.TransformedDistribution):  # 继承"基础分布+变换链"的组合分布
    """
    A squashed (tanh-transformed) diagonal Gaussian distribution.

    This is used for stochastic policies where actions must be within bounded intervals.
    """

    # 构造：先建逐维独立的 Normal，再挂上 tanh 变换链，组装成完整分布。
    def __init__(self, loc, scale):  # 注意 pyd.Normal 约定第二个参数是 σ（标准差）而非方差
        """
        Initialize the squashed normal distribution.

        Args:
            loc (Tensor): Mean of the Gaussian.
            scale (Tensor): Standard deviation of the Gaussian.
        """
        self.loc = loc  # 保存 tanh 前的高斯均值，供 mean 属性复用
        self.scale = scale  # 保存标准差：探索幅度，训练中受 log_std 边界约束

        self.base_dist = pyd.Normal(loc, scale)  # 基础分布 N(μ,σ²)：各维独立，形状 (batch, action_dim)
        transforms = [TanhTransform()]  # 变换链：仅 tanh 一环（对张量逐元素作用，多维无需逐维展开）
        super().__init__(self.base_dist, transforms)  # 组装 TransformedDistribution：u~N(μ,σ²)，a=tanh(u)

    # 分布均值=确定性动作：把 μ 依次过变换链得 tanh(μ)。
    # 输出 (batch, action_dim)；SAC.act(obs, sample=False) 评测时用它（不采样、更稳）。
    @property  # 属性化：像 dist.mean 一样访问，而非方法调用
    def mean(self):  # 无参；返回压缩后的均值张量
        """
        Compute the mean of the transformed distribution.

        Returns:
            Tensor: Mean of the squashed distribution.
        """
        mu = self.loc  # 从 tanh 前的高斯均值出发
        for tr in self.transforms:  # 依次过变换链（本实现只有 tanh 一层）
            mu = tr(mu)  # mu ← tr(mu)：逐层前向，形状不变
        return mu  # tanh 后的均值动作 ∈ (−1,1)^action_dim


# ============================== 类：DiagGaussianActor ============================== #
# 职责：SAC 的策略网络 π(a|s)——注意返回的是"分布对象"而不是单个动作。
# 输入：obs (batch, obs_dim)；trunk 一次前向输出 2×action_dim 维（μ 与 logσ 拼接）。
# 流程位置：SAC.py 的 update_actor 里 dist.rsample() 取动作、dist.log_prob(a) 取熵项，
# 动作喂 DoubleQCritic 得 Q，构成 actor_loss=(α·logπ−Q).mean()：熵奖励 vs 高价值的权衡。
class DiagGaussianActor(nn.Module):  # PyTorch 模块基类：参数自动注册、支持 .to(device)/.train()
    """
    Diagonal Gaussian policy network with tanh squashing.

    This network outputs a squashed Gaussian distribution given an observation,
    suitable for continuous control tasks.

    Args:
        obs_dim (int): Dimension of the observation space.
        action_dim (int): Dimension of the action space.
        hidden_dim (int): Number of units in hidden layers.
        hidden_depth (int): Number of hidden layers.
        log_std_bounds (list): Min and max bounds for log standard deviation.
    """

    # 构造：MLP 主干一次输出 2×action_dim——前半当 μ、后半当 logσ。
    # 参数化 logσ 而非 σ：logσ 无下界、优化面更平滑，是 SAC 的通行做法。
    def __init__(self, obs_dim, action_dim, hidden_dim, hidden_depth, log_std_bounds):  # 超参含义见类 docstring
        """
        Initialize the actor network.
        """
        super().__init__()  # 初始化 nn.Module 基类（参数容器/钩子），PyTorch 固定第一步

        self.log_std_bounds = log_std_bounds  # logσ 的 [min,max]：防 σ 塌缩到 0（丢探索）或爆炸
        # 主干 MLP：obs_dim → hidden×depth → 2×action_dim（μ 与 logσ 拼在同一次输出里）
        self.trunk = utils.mlp(obs_dim, hidden_dim, 2 * action_dim, hidden_depth)

        self.outputs = dict()  # 缓存最近一次前向的 μ/std，供 log() 画 TensorBoard 直方图
        self.apply(utils.weight_init)  # 递归初始化所有子层：正交权重+零偏置，训练更稳

    # 前向：obs (B, obs_dim) → trunk → (B, 2×action_dim) → chunk 对半拆成
    # μ:(B, action_dim) 与 logσ:(B, action_dim)，组装成 SquashedNormal 返回。
    def forward(self, obs):  # PyTorch 协议：actor(obs) 即调用本方法
        """
        Forward pass through the network.

        Args:
            obs (Tensor): Observation input.

        Returns:
            SquashedNormal: Action distribution with mean and std tracked in `self.outputs`.
        """
        # 沿最后一维对半切：(B, 2×A) → μ:(B,A) + logσ:(B,A)
        mu, log_std = self.trunk(obs).chunk(2, dim=-1)

        # 【译注】下面三行把 logσ"软约束"进 [min,max]：先 tanh 压到 (−1,1) 再仿射拉伸——
        # 处处可导（优于硬 clamp），保证 σ 永远落在合法区间。
        # constrain log_std inside [log_std_min, log_std_max]
        log_std = torch.tanh(log_std)  # 第一步：压进 (−1,1)，形状不变
        log_std_min, log_std_max = self.log_std_bounds  # 解包边界（配置给定，如 [−20, 2]）
        log_std = log_std_min + 0.5 * (log_std_max - log_std_min) * (log_std + 1)  # 第二步仿射：t=−1→min，t=+1→max

        std = log_std.exp()  # σ=exp(logσ)：还原成标准差 (B, action_dim)，恒为正

        self.outputs["mu"] = mu  # 记录 μ：观察策略输出是否收敛
        self.outputs["std"] = std  # 记录 σ：策略熵的化身——训练后期应收缩（探索→利用）

        dist = SquashedNormal(mu, std)  # 组装策略分布 π(a|s)=tanh(N(μ,σ²))
        return dist  # 返回分布：rsample/log_prob/mean 怎么用由调用方 SAC.py 决定

    # 训练可视化：把缓存的 μ/std 写成 TensorBoard 直方图；无返回值。
    def log(self, writer, step):  # writer=TensorBoard 写入器；step=全局训练步数
        """
        Log network outputs (mu and std histograms) to TensorBoard.

        Args:
            writer (SummaryWriter): TensorBoard writer instance.
            step (int): Current global training step.
        """
        for k, v in self.outputs.items():  # 遍历 {"mu":…, "std":…}
            writer.add_histogram(f"train_actor/{k}_hist", v, step)  # 画直方图：μ 的范围、σ 的收缩过程一目了然
