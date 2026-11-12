# ============================================================================ #
# 【文件】SAC 价值网络（Critic）——SAC 算法的"评委"：给 (状态,动作) 对打分。
# Q 值（action-value，动作价值）：从状态 s 做动作 a 后可期望拿到的折扣累计回报。
# 双 Q（Double Q-learning）设计：两个独立 Q 网络取较小值当学习目标，抑制 Q-learning
# 固有的过估计偏差（overestimation bias，噪声被 max 操作放大）——TD3/SAC 的招牌技巧。
# 流程位置：SAC.py 里 critic(obs,action) 同时返回 q1/q2；TD 目标取
# min(target_Q1, target_Q2) − α·logπ；critic 损失 = 两路 TD 误差的均方之和。
# ============================================================================ #
import torch  # PyTorch：张量运算（cat 拼接）与自动微分
from torch import nn  # 神经网络基类

import robot_nav.models.SAC.SAC_utils as utils  # 工具模块：mlp() 工厂 + weight_init() 正交初始化


# ============================== 类：DoubleQCritic ============================== #
# 职责：同时学习两个 Q 函数 Q1(s,a)、Q2(s,a)——同构不同参的两套 MLP，输出标量打分。
# 输入：obs (batch, obs_dim) 与 action (batch, action_dim)；输出：q1/q2 各 (batch, 1)。
# 为什么双份：单 Q 会系统性高估（max/噪声混叠），取 min 砍掉乐观偏差，训练更稳。
class DoubleQCritic(nn.Module):  # PyTorch 模块基类：两套 MLP 参数统一注册管理
    """
    Double Q-learning critic network.

    Implements two independent Q-functions (Q1 and Q2) to mitigate overestimation bias in value estimates,
    as introduced in the Twin Delayed Deep Deterministic Policy Gradient (TD3) and Soft Actor-Critic (SAC) algorithms.

    Args:
        obs_dim (int): Dimension of the observation space.
        action_dim (int): Dimension of the action space.
        hidden_dim (int): Number of units in each hidden layer.
        hidden_depth (int): Number of hidden layers.
    """

    # 构造：两个结构相同、权重独立的 MLP；输入维 = obs_dim+action_dim（s 与 a 拼接后喂入），
    # 输出维 = 1——Q 值是给"这一个动作"打的分数，一个标量就够。
    def __init__(self, obs_dim, action_dim, hidden_dim, hidden_depth):  # 结构超参含义见类 docstring
        """
        Initialize the Double Q-critic network with two MLPs.

        Q1 and Q2 share the same architecture but have separate weights.
        """
        super().__init__()  # 初始化 nn.Module 基类
        # 第一个 Q 网络：Linear 堆叠 obs_dim+action_dim → hidden×depth → 1
        self.Q1 = utils.mlp(obs_dim + action_dim, hidden_dim, 1, hidden_depth)
        # 第二个 Q 网络：与 Q1 同构但独立初始化、独立训练——"独立性"正是去偏关键
        self.Q2 = utils.mlp(obs_dim + action_dim, hidden_dim, 1, hidden_depth)

        self.outputs = dict()  # 缓存最近一次 q1/q2，供 log() 画直方图
        self.apply(utils.weight_init)  # 两套网络一起做正交权重+零偏置初始化

    # 前向：把 (s,a) 沿特征维拼接后分别喂给两套 MLP。
    # obs:(B,obs_dim) + action:(B,action_dim) → obs_action:(B,obs+act) → q1/q2 各 (B,1)。
    def forward(self, obs, action):  # critic(obs, action) 即调用本方法
        """
        Compute Q-values for the given observation-action pairs.

        Args:
            obs (Tensor): Observations of shape (batch_size, obs_dim).
            action (Tensor): Actions of shape (batch_size, action_dim).

        Returns:
            Tuple[Tensor, Tensor]: Q1 and Q2 values, each of shape (batch_size, 1).
        """
        assert obs.size(0) == action.size(0)  # 防御检查：观测与动作批量维必须一致，否则拼接错位

        obs_action = torch.cat([obs, action], dim=-1)  # 最后一维拼接：(B,obs_dim)+(B,action_dim)→(B,obs+act)
        q1 = self.Q1(obs_action)  # 评委 1 打分：(B,obs+act) → (B,1)
        q2 = self.Q2(obs_action)  # 评委 2 打分：(B,obs+act) → (B,1)

        self.outputs["q1"] = q1  # 缓存供可视化
        self.outputs["q2"] = q2  # 缓存供可视化

        return q1, q2  # 成对返回：目标取 min 抗过估，损失两路各算 TD 误差

    # 训练可视化：把 q1/q2 画成直方图，观察 Q 值量级是否健康（爆炸/塌缩一眼可见）。
    def log(self, writer, step):  # writer=TensorBoard 写入器；step=全局训练步数
        """
        Log histograms of Q-value distributions to TensorBoard.

        Args:
            writer (SummaryWriter): TensorBoard writer instance.
            step (int): Current training step (global).
        """
        for k, v in self.outputs.items():  # 遍历 {"q1":…, "q2":…}
            writer.add_histogram(f"train_critic/{k}_hist", v, step)  # 写直方图到 train_critic/ 命名空间
