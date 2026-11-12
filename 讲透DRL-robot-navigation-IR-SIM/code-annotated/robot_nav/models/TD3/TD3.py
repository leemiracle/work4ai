from pathlib import Path  # 路径工具：checkpoint 目录创建与模型文件路径拼接

import numpy as np  # NumPy：激光雷达数组处理、探索噪声采样
import torch  # PyTorch：张量运算 + 自动微分，RL 训练的核心引擎
import torch.nn as nn  # 神经网络模块：Linear/Tanh 等可学习层都来自这里
import torch.nn.functional as F  # 函数式接口：leaky_relu/mse_loss 等无状态运算
from numpy import inf  # 正无穷：作 max_Q 初始值（任何 Q 都大于 -inf，首次比较必被替换）
from torch.utils.tensorboard import SummaryWriter  # TensorBoard 写入器：把训练曲线落盘可视化

from robot_nav.utils import get_max_bound  # 本仓工具：按机器人运动学推导 Q 值物理上界（max-bound 正则用）


# 【Actor·策略网络】TD3 的"演员"：确定性策略 π(s)——同一状态总输出同一动作，探索靠外加噪声
# 【输入输出】s: (B, state_dim) → a: (B, action_dim)，经 tanh 压缩到 (-1,1)
# 【流程位置】被实例化两次：在线 actor（被优化）+ actor_target（算 TD 目标、慢速跟随）
# 【教学】Actor-Critic（演员-评论家）架构：演员决策，评论家给动作打分（估 Q 值）指导演员改进
class Actor(nn.Module):  # 继承 nn.Module：获得参数注册/保存/迁移能力
    """
    Actor network for the TD3 algorithm.

    This neural network maps states to actions using a feedforward architecture with
    LeakyReLU activations and a final Tanh output to bound the actions in [-1, 1].

    Architecture:
        Input: state_dim
        Hidden Layer 1: 400 units, LeakyReLU
        Hidden Layer 2: 300 units, LeakyReLU
        Output Layer: action_dim, Tanh

    Args:
        state_dim (int): Dimension of the input state.
        action_dim (int): Dimension of the action output.
    """

    # 【__init__】搭建 400→300 两层隐藏结构并做 Kaiming 初始化
    # 【输入】state_dim=雷达分箱数+5 个附加特征；action_dim=2（线速度+角速度）
    # 【要点】Kaiming 按激活函数增益定方差，防深网前向信号衰减/反向梯度爆炸
    def __init__(self, state_dim, action_dim):  # 构造函数：输入维度 state_dim，输出维度 action_dim
        super(Actor, self).__init__()  # 调用 nn.Module 构造器（注册子层与参数所必需）

        self.layer_1 = nn.Linear(state_dim, 400)  # 隐藏层1：(B, state_dim)→(B, 400)
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # 权重 Kaiming 均匀初始化
        self.layer_2 = nn.Linear(400, 300)  # 隐藏层2：(B, 400)→(B, 300)
        torch.nn.init.kaiming_uniform_(self.layer_2.weight, nonlinearity="leaky_relu")  # 同上，第二层权重初始化
        self.layer_3 = nn.Linear(300, action_dim)  # 输出层：(B, 300)→(B, action_dim)
        self.tanh = nn.Tanh()  # tanh 把输出压进 (-1,1)：与动作空间的界天然匹配

    # 【forward】前向传播：状态→动作
    # 【输入】s: (B, state_dim)；【输出】a: (B, action_dim)∈(-1,1)
    def forward(self, s):  # 前向传播入口（nn.Module 约定的方法名）
        """
        Perform a forward pass through the actor network.

        Args:
            s (torch.Tensor): Input state tensor.

        Returns:
            (torch.Tensor): Action output tensor after Tanh activation.
        """
        s = F.leaky_relu(self.layer_1(s))  # 层1+LeakyReLU；(B, state_dim)→(B, 400)
        s = F.leaky_relu(self.layer_2(s))  # 层2+LeakyReLU；(B, 400)→(B, 300)
        a = self.tanh(self.layer_3(s))  # 输出层+tanh；(B, 300)→(B, action_dim)
        return a  # 返回确定性动作


# 【Critic·双 Q 网络】TD3 的"评论家"：孪生 Q（Twin Critic），TD3 三大改进之一
# 【职责】对同一 (s,a) 输出两个独立 Q 估计；训练时取 min——悲观估计压制 Q 高估
# 【输入输出】s: (B, state_dim)、a: (B, action_dim) → q1: (B,1)、q2: (B,1)
# 【教学】Q 值=在状态 s 执行动作 a 后的期望累计回报；高估为何致命：自举目标对正向噪声只增不减，
#        误差被指数放大（正反馈）把策略带偏——取 min 是最直接的纠偏手段
class Critic(nn.Module):  # 继承 nn.Module：双 Q 打包进同一模块，统一优化与存取
    """
    Critic network for the TD3 algorithm.

    This class defines two Q-value estimators (Q1 and Q2) using separate subnetworks.
    Each Q-network takes both state and action as input and outputs a scalar Q-value.

    Architecture for each Q-network:
        Input: state_dim and action_dim
        - State pathway: Linear + LeakyReLU → 400 → 300
        - Action pathway: Linear → 300
        - Combined pathway: LeakyReLU(Linear(state) + Linear(action) + bias) → 1

    Args:
        state_dim (int): Dimension of the input state.
        action_dim (int): Dimension of the input action.
    """

    # 【__init__】并联两套同构 Q1/Q2 子网络（layer_1~3 属 Q1，layer_4~6 属 Q2）
    # 【要点】两套网络独立初始化、独立学习，估计足够多样，取 min 才有意义
    def __init__(self, state_dim, action_dim):  # 构造函数：状态 state_dim + 动作 action_dim 进，两个标量 Q 出
        super(Critic, self).__init__()  # 初始化 nn.Module 基类

        self.layer_1 = nn.Linear(state_dim, 400)  # Q1 状态入层：(B, state_dim)→(B, 400)
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # Q1 入层 Kaiming 初始化
        self.layer_2_s = nn.Linear(400, 300)  # Q1 状态分支第二层：(B, 400)→(B, 300)
        torch.nn.init.kaiming_uniform_(self.layer_2_s.weight, nonlinearity="leaky_relu")  # Q1 状态分支初始化
        self.layer_2_a = nn.Linear(action_dim, 300)  # Q1 动作分支：(B, action_dim)→(B, 300)，与状态分支同维以便相加融合
        torch.nn.init.kaiming_uniform_(self.layer_2_a.weight, nonlinearity="leaky_relu")  # Q1 动作分支初始化
        self.layer_3 = nn.Linear(300, 1)  # Q1 输出头：(B, 300)→(B, 1) 标量 Q 值
        torch.nn.init.kaiming_uniform_(self.layer_3.weight, nonlinearity="leaky_relu")  # Q1 输出头初始化

        self.layer_4 = nn.Linear(state_dim, 400)  # Q2 状态入层：与 Q1 完全同构的另一套独立估计
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # 疑似笔误：初始化对象仍是 layer_1（layer_4 保持默认初始化）
        self.layer_5_s = nn.Linear(400, 300)  # Q2 状态分支第二层：(B, 400)→(B, 300)
        torch.nn.init.kaiming_uniform_(self.layer_5_s.weight, nonlinearity="leaky_relu")  # Q2 状态分支初始化
        self.layer_5_a = nn.Linear(action_dim, 300)  # Q2 动作分支：(B, action_dim)→(B, 300)
        torch.nn.init.kaiming_uniform_(self.layer_5_a.weight, nonlinearity="leaky_relu")  # Q2 动作分支初始化
        self.layer_6 = nn.Linear(300, 1)  # Q2 输出头：(B, 300)→(B, 1)
        torch.nn.init.kaiming_uniform_(self.layer_6.weight, nonlinearity="leaky_relu")  # Q2 输出头初始化

    # 【forward】并行计算孪生 Q 值
    # 【输入】s: (B, state_dim)、a: (B, action_dim)；【输出】q1/q2: 各 (B,1)
    def forward(self, s, a):  # 前向传播入口：状态与动作同时输入
        """
        Perform a forward pass through both Q-networks.

        Args:
            s (torch.Tensor): Input state tensor.
            a (torch.Tensor): Input action tensor.

        Returns:
            (tuple):
                - q1 (torch.Tensor): Output Q-value from the first critic network.
                - q2 (torch.Tensor): Output Q-value from the second critic network.
        """
        s1 = F.leaky_relu(self.layer_1(s))  # Q1 状态编码：(B, state_dim)→(B, 400)
        self.layer_2_s(s1)  # 调用层做前向但丢弃返回值：遗留写法，无副作用的冗余计算
        self.layer_2_a(a)  # 同上；真正的融合计算在下面三行手工完成
        s11 = torch.mm(s1, self.layer_2_s.weight.data.t())  # 状态分支投影 (B,400)×(400,300)→(B,300)；.data 使 layer_2 权重脱离计算图、不收梯度
        s12 = torch.mm(a, self.layer_2_a.weight.data.t())  # 动作分支投影：(B, action_dim)→(B, 300)
        s1 = F.leaky_relu(s11 + s12 + self.layer_2_a.bias.data)  # 两分支相加融合（只加一个偏置）再激活：(B, 300)
        q1 = self.layer_3(s1)  # Q1 输出：(B, 300)→(B, 1)

        s2 = F.leaky_relu(self.layer_4(s))  # Q2 状态编码：结构与 Q1 完全对称
        self.layer_5_s(s2)  # 调用后丢弃输出（同 Q1 的遗留写法）
        self.layer_5_a(a)  # 调用后丢弃输出
        s21 = torch.mm(s2, self.layer_5_s.weight.data.t())  # Q2 状态分支投影→(B, 300)
        s22 = torch.mm(a, self.layer_5_a.weight.data.t())  # Q2 动作分支投影→(B, 300)
        s2 = F.leaky_relu(s21 + s22 + self.layer_5_a.bias.data)  # Q2 融合+激活：(B, 300)
        q2 = self.layer_6(s2)  # Q2 输出：(B, 300)→(B, 1)
        return q1, q2  # 同时返回两个估计，供调用方取 min（clipped double Q 技巧）


# TD3 network  # TD3 智能体主类：算法编排层（英文原注保留）
# 【TD3 类】Twin Delayed DDPG——本仓连续控制主算法（动作=差速轮的线/角速度）
# 【职责】封装 TD3 三件套：孪生 critic 取 min / 目标策略平滑 / 延迟策略更新
# 【对外接口】get_action（交互）、train（训练）、save/load（存取）、prepare_state（特征工程）
# 【流程位置】训练脚本每 episode 调一次 train()（内含 iterations 次梯度步），环境交互走 get_action()
class TD3(object):  # 纯 Python 编排类（非 nn.Module）：聚合网络、优化器与训练逻辑
    def __init__(  # 构造函数开始（多行签名）
        self,  # 实例自身
        state_dim,  # 状态维数：雷达分箱数 + 距离/cos/sin/线速度/角速度共 5 个附加量
        action_dim,  # 动作维数 = 2（线速度、角速度）
        max_action,  # 动作幅值上界，用于把网络输出裁剪回合法区间
        device,  # torch.device："cpu" 或 "cuda"
        lr=1e-4,  # 学习率：actor 与 critic 共用
        save_every=0,  # 每隔多少次 train() 调用自动存盘；0 表示不自动存
        load_model=False,  # 是否构造时从磁盘恢复已有权重
        save_directory=Path("robot_nav/models/TD3/checkpoint"),  # 存盘目录
        model_name="TD3",  # 模型名：存盘文件名前缀 + TensorBoard 注释
        load_directory=Path("robot_nav/models/TD3/checkpoint"),  # 加载目录
        use_max_bound=False,  # 是否启用 Q 值物理上界正则（本仓特色功能）
        bound_weight=0.25,  # 上界正则项权重系数
    ):  # 构造参数列表结束
        """
        Twin Delayed Deep Deterministic Policy Gradient (TD3) agent.

        This class implements the TD3 reinforcement learning algorithm for continuous control.
        It uses an Actor-Critic architecture with target networks and delayed policy updates.

        Args:
            state_dim (int): Dimension of the input state.
            action_dim (int): Dimension of the action space.
            max_action (float): Maximum allowed value for actions.
            device (torch.device): Device to run the model on (CPU or CUDA).
            lr (float, optional): Learning rate for both actor and critic. Default is 1e-4.
            save_every (int, optional): Save model every `save_every` iterations. Default is 0.
            load_model (bool, optional): Whether to load model from checkpoint. Default is False.
            save_directory (Path, optional): Directory to save model checkpoints.
            model_name (str, optional): Name to use when saving/loading models.
            load_directory (Path, optional): Directory to load model checkpoints from.
            use_max_bound (bool, optional): Whether to apply maximum Q-value bounding during training.
            bound_weight (float, optional): Weight for the max-bound loss penalty.
        """
        self.device = device  # 保存设备引用，供张量搬运
        # Initialize the Actor network  # 初始化策略网络（英文原注保留）
        self.actor = Actor(state_dim, action_dim).to(self.device)  # 在线策略网络：真正被训练的演员
        self.actor_target = Actor(state_dim, action_dim).to(self.device)  # 目标策略网络：为 TD 目标提供稳定基线
        self.actor_target.load_state_dict(self.actor.state_dict())  # 初始时 target 与在线网络完全同权重
        self.actor_optimizer = torch.optim.Adam(params=self.actor.parameters(), lr=lr)  # actor 专属 Adam 优化器

        # Initialize the Critic networks  # 初始化评论家（孪生 Q）网络（英文原注保留）
        self.critic = Critic(state_dim, action_dim).to(self.device)  # 在线双 Q 网络（Q1、Q2 在同一模块内）
        self.critic_target = Critic(state_dim, action_dim).to(self.device)  # 目标双 Q 网络：只用来算 TD 目标
        self.critic_target.load_state_dict(self.critic.state_dict())  # 初始同步权重
        self.critic_optimizer = torch.optim.Adam(params=self.critic.parameters(), lr=lr)  # critic 专属 Adam 优化器

        self.action_dim = action_dim  # 记录动作维数（探索噪声采样时定形状）
        self.max_action = max_action  # 记录动作上界（裁剪时用）
        self.state_dim = state_dim  # 记录状态维数（prepare_state 分箱时用）
        self.writer = SummaryWriter(comment=model_name)  # TensorBoard 日志写入器
        self.iter_count = 0  # train() 调用计数（≈已训练 episode 数）
        if load_model:  # 若指定加载，先恢复权重再继续训练或评估
            self.load(filename=model_name, directory=load_directory)  # 从磁盘加载 4 个网络
        self.save_every = save_every  # 记录自动存盘周期
        self.model_name = model_name  # 记录模型名
        self.save_directory = save_directory  # 记录存盘目录
        self.use_max_bound = use_max_bound  # 记录是否启用 max-bound 正则
        self.bound_weight = bound_weight  # 记录正则权重

    # 【get_action】环境交互入口：带可选探索噪声的动作选择
    # 【输入】obs: (state_dim,) ndarray；add_noise：训练期 True 加噪声、评估期 False 纯策略
    # 【输出】(action_dim,) ndarray，已裁剪到 [-max_action, max_action]
    # 【教学】确定性策略自己不会探索，必须外加噪声试错；本仓用高斯噪声（DDPG 原论文用 OU 噪声——
    #        时间相关的平滑噪声，理论上适配惯性系统，但后续研究普遍发现高斯噪声效果相当甚至更好）
    def get_action(self, obs, add_noise):  # 交互入口：按需加探索噪声
        """
        Get an action from the current policy with optional exploration noise.

        Args:
            obs (np.ndarray): The current state observation.
            add_noise (bool): Whether to add exploration noise.

        Returns:
            (np.ndarray): The chosen action clipped to [-max_action, max_action].
        """
        if add_noise:  # 训练期：加探索噪声
            return (  # 返回"策略动作+噪声"再裁剪的结果
                self.act(obs) + np.random.normal(0, 0.2, size=self.action_dim)  # 加 N(0, 0.2²) 高斯噪声，形状 (action_dim,)
            ).clip(-self.max_action, self.max_action)  # 裁回合法动作区间
        else:  # 评估期：不加噪声
            return self.act(obs)  # 直接用确定性策略

    # 【act】纯确定性推理（无噪声）
    # 【输入】state: (state_dim,) ndarray；【输出】(action_dim,) ndarray
    # 【流程位置】被 get_action 调用；评估脚本也常直接调用
    def act(self, state):  # 确定性推理入口（无噪声）
        """
        Compute the action using the actor network without exploration noise.

        Args:
            state (np.ndarray): The current environment state.

        Returns:
            (np.ndarray): The deterministic action predicted by the actor.
        """
        state = torch.Tensor(state).to(self.device)  # ndarray→张量并搬到计算设备；(state_dim,)
        return self.actor(state).cpu().data.numpy().flatten()  # 前向→回 CPU→转 numpy→展平；(state_dim,)→(action_dim,)

    # training cycle  # 训练周期入口（英文原注保留）
    # 【train】从 replay buffer 采样做 iterations 次梯度更新
    # 【输入】replay_buffer（经验池）、iterations（梯度步数）、batch_size（批大小）+ 一串超参
    # 【输出】无返回值；副作用=更新网络、写 TensorBoard、按周期存盘
    # 【教学】replay buffer（经验回放池）：把交互经历存下来反复随机采样——打破相邻样本的
    #        时间相关性（类似打乱数据集）、一条经验可多次复用，是深度 RL 区别于在线 TD 的关键
    def train(  # 训练入口开始（多行签名）
        self,  # 实例自身
        replay_buffer,  # 经验回放池，提供 sample_batch(batch_size) 方法
        iterations,  # 本次调用要做的梯度更新次数
        batch_size,  # 每步采样的批大小 B
        discount=0.99,  # 折扣因子 γ：未来奖励打折程度，0.99 重视长程回报
        tau=0.005,  # 目标网络软更新速率（每步只吸收 0.5% 新权重）
        policy_noise=0.2,  # 目标策略平滑：给目标动作加噪的标准差
        noise_clip=0.5,  # 目标噪声裁剪幅度，防平滑噪声过大
        policy_freq=2,  # 延迟更新频率：每 2 次 critic 更新才做 1 次 actor 更新
        max_lin_vel=0.5,  # 最大线速度（max-bound 上界估计用）
        max_ang_vel=1,  # 最大角速度（同上）
        goal_reward=100,  # 到达目标的奖励（同上）
        distance_norm=10,  # 距离归一化尺度（同上）
        time_step=0.3,  # 仿真步长/秒（同上）
    ):  # 训练参数列表结束
        """
        Train the TD3 agent using batches sampled from the replay buffer.

        Args:
            replay_buffer (ReplayBuffer): The replay buffer to sample experiences from.
            iterations (int): Number of training iterations to perform.
            batch_size (int): Size of each mini-batch.
            discount (float): Discount factor gamma for future rewards.
            tau (float): Soft update rate for target networks.
            policy_noise (float): Stddev of Gaussian noise added to target actions.
            noise_clip (float): Maximum magnitude of noise added to target actions.
            policy_freq (int): Frequency of policy (actor) updates.
            max_lin_vel (float): Max linear velocity used for upper bound estimation.
            max_ang_vel (float): Max angular velocity used for upper bound estimation.
            goal_reward (float): Reward given for reaching the goal.
            distance_norm (float): Distance normalization factor.
            time_step (float): Time step used in upper bound calculations.
        """
        av_Q = 0  # 批平均 Q 累计器（最后除以 iterations 得均值）
        max_Q = -inf  # 批最大 Q 的历史最大值（监控 Q 是否飞涨）
        av_loss = 0  # critic 损失累计器
        for it in range(iterations):  # 主循环：一轮=采样→算 TD 目标→更新 critic→（延迟）更新 actor
            # sample a batch from the replay buffer  # 从回放池随机采一批转移（英文原注保留）
            (  # 五元组解包开始
                batch_states,  # 当前状态集 (B, state_dim)
                batch_actions,  # 执行过的动作集 (B, action_dim)
                batch_rewards,  # 即时奖励集 (B,)
                batch_dones,  # 终止标志集 (B,)——碰撞或到达目标记 1
                batch_next_states,  # 下一状态集 (B, state_dim)
            ) = replay_buffer.sample_batch(batch_size)  # 均匀随机采 B 条时间上不相关的经历
            state = torch.Tensor(batch_states).to(self.device)  # numpy→张量→设备；(B, state_dim)
            next_state = torch.Tensor(batch_next_states).to(self.device)  # 同理；(B, state_dim)
            action = torch.Tensor(batch_actions).to(self.device)  # 动作张量：(B, action_dim)
            reward = torch.Tensor(batch_rewards).to(self.device).reshape(-1, 1)  # 整列成 (B,1) 便于与 Q 相加
            done = torch.Tensor(batch_dones).to(self.device).reshape(-1, 1)  # (B,1) 浮点 0/1

            # Obtain the estimated action from the next state by using the actor-target  # 用目标策略估计 s' 的动作
            next_action = self.actor_target(next_state)  # 目标策略动作：(B, state_dim)→(B, action_dim)

            # Add noise to the action  # 目标策略平滑（英文原注保留）
            noise = (  # 构造与动作同形的裁剪高斯噪声
                torch.Tensor(batch_actions)  # 借 batch_actions 的形状 (B, action_dim) 建张量
                .data.normal_(0, policy_noise)  # 原地填充 N(0, policy_noise²)；.data 使其不进计算图
                .to(self.device)  # 搬到计算设备
            )  # 噪声张量构造结束
            noise = noise.clamp(-noise_clip, noise_clip)  # 逐元素裁剪到 [-0.5, 0.5]
            next_action = (next_action + noise).clamp(-self.max_action, self.max_action)  # 加噪后裁回动作空间

            # Calculate the Q values from the critic-target network for the next state-action pair  # 目标 critic 评估 (s', ã')
            target_Q1, target_Q2 = self.critic_target(next_state, next_action)  # 孪生目标 Q，各 (B,1)

            # Select the minimal Q value from the 2 calculated values  # 取双 Q 较小者（英文原注保留）
            target_Q = torch.min(target_Q1, target_Q2)  # 取 min：TD3 核心技巧，压制自举带来的 Q 高估
            av_Q += torch.mean(target_Q)  # 累计批均值供监控
            max_Q = max(max_Q, torch.max(target_Q))  # 刷新历史最大 Q
            # Calculate the final Q value from the target network parameters by using Bellman equation  # Bellman 目标
            target_Q = reward + ((1 - done) * discount * target_Q).detach()  # y=r+γ(1-done)·minQ'；终止步不自举；detach 切断梯度

            # Get the Q values of the basis networks with the current parameters  # 在线 critic 对旧 (s,a) 的估计
            current_Q1, current_Q2 = self.critic(state, action)  # 各 (B,1)，带梯度

            # Calculate the loss between the current Q value and the target Q value  # 双 Q 各自的 TD 误差
            loss = F.mse_loss(current_Q1, target_Q) + F.mse_loss(current_Q2, target_Q)  # 两份 MSE 相加共同反传

            if self.use_max_bound:  # 可选：Q 物理上界正则（本仓特色）
                max_bound = get_max_bound(  # 按运动学算出本批每个样本 Q 的理论上限 (B,1)
                    next_state,  # 下一状态
                    discount,  # 折扣 γ
                    max_ang_vel,  # 角速度上界
                    max_lin_vel,  # 线速度上界
                    time_step,  # 仿真步长
                    distance_norm,  # 距离归一化尺度
                    goal_reward,  # 目标奖励
                    reward,  # 本批奖励
                    done,  # 本批终止标志
                    self.device,  # 计算设备
                )  # get_max_bound 调用结束，得 (B,1) 物理上界
                max_excess_Q1 = F.relu(current_Q1 - max_bound)  # Q1 超出上界的部分（未超则恒 0）
                max_excess_Q2 = F.relu(current_Q2 - max_bound)  # Q2 超出上界的部分
                max_bound_loss = (max_excess_Q1**2).mean() + (max_excess_Q2**2).mean()  # 超额部分的平方惩罚（hinge²）
                # Add loss for Q values exceeding maximum possible upper bound  # 把超额惩罚并入总损失（英文原注保留）
                loss += self.bound_weight * max_bound_loss  # 加权后累加进 critic 损失

            # Perform the gradient descent  # 执行 critic 的反向传播与参数更新
            self.critic_optimizer.zero_grad()  # 清零旧梯度（PyTorch 梯度默认累加）
            loss.backward()  # 反传；detach 过的 target_Q 不产生梯度（目标只是回归靶）
            self.critic_optimizer.step()  # Adam 走一步，只更新 critic 参数

            if it % policy_freq == 0:  # 延迟策略更新：每 policy_freq 次 critic 更新才进一次本分支
                # Maximize the actor output value by performing gradient descent on negative Q values  # actor 更新目标
                # (essentially perform gradient ascent)  # 对 -Q 下降=对 Q 上升（英文原注保留）
                actor_grad, _ = self.critic(state, self.actor(state))  # Q(s,π(s))：只取 Q1 传梯度给 actor
                actor_grad = -actor_grad.mean()  # 取负号：最小化 -Q 即最大化 Q
                self.actor_optimizer.zero_grad()  # 清零 actor 梯度
                actor_grad.backward()  # 反传：梯度穿过 critic 到达 actor
                self.actor_optimizer.step()  # 只更新 actor 参数（critic 虽有梯度但不在本优化器内）

                # Use soft update to update the actor-target network parameters by  # actor 目标网软更新
                # infusing small amount of current parameters  # 只注入少量新参数（英文原注保留）
                for param, target_param in zip(  # 在线↔目标参数逐个配对遍历
                    self.actor.parameters(), self.actor_target.parameters()  # 两个参数迭代器 zip 到一起
                ):  # zip 参数配对结束
                    target_param.data.copy_(  # polyak 平均：θ'←τθ+(1-τ)θ'，慢跟随保目标稳定
                        tau * param.data + (1 - tau) * target_param.data  # τ=0.005：每次只吸收 0.5% 新权重
                    )  # 原地写回目标参数完成
                # Use soft update to update the critic-target network parameters by infusing  # critic 目标网软更新
                # small amount of current parameters  # 同样只注入少量新参数（英文原注保留）
                for param, target_param in zip(  # critic 在线↔目标逐参数配对
                    self.critic.parameters(), self.critic_target.parameters()  # 两个参数迭代器 zip 到一起
                ):  # zip 参数配对结束
                    target_param.data.copy_(  # polyak 软更新（与 actor 目标同公式）
                        tau * param.data + (1 - tau) * target_param.data  # 慢速跟随，避免目标剧烈漂移
                    )  # 原地写回目标参数完成

            av_loss += loss  # 累计本步 critic 损失
        self.iter_count += 1  # train() 调用计数 +1（每 episode 一次）
        # Write new values for tensorboard  # 写 TensorBoard 标量（英文原注保留）
        self.writer.add_scalar("train/loss", av_loss / iterations, self.iter_count)  # 平均 critic 损失曲线
        self.writer.add_scalar("train/avg_Q", av_Q / iterations, self.iter_count)  # 平均目标 Q 曲线
        self.writer.add_scalar("train/max_Q", max_Q, self.iter_count)  # 历史最大 Q 曲线（监控高估）
        if self.save_every > 0 and self.iter_count % self.save_every == 0:  # 按周期自动存盘
            self.save(filename=self.model_name, directory=self.save_directory)  # 落盘 4 个网络

    # 【save】把 4 个网络的权重存到磁盘
    # 【输入】filename：文件名前缀；directory：目标目录（不存在则自动创建）
    # 【输出】4 个 .pth 文件（actor/actor_target/critic/critic_target）
    def save(self, filename, directory):  # 存盘入口
        """
        Save the actor and critic networks (and their targets) to disk.

        Args:
            filename (str): Name to use when saving model files.
            directory (Path): Directory where models should be saved.
        """
        Path(directory).mkdir(parents=True, exist_ok=True)  # 递归建目录，已存在不报错
        torch.save(self.actor.state_dict(), "%s/%s_actor.pth" % (directory, filename))  # 存在线 actor 权重
        torch.save(  # 存目标 actor 权重
            self.actor_target.state_dict(),  # 目标 actor 的 state_dict
            "%s/%s_actor_target.pth" % (directory, filename),  # 目标 actor 文件路径
        )  # 目标 actor 存盘调用结束
        torch.save(self.critic.state_dict(), "%s/%s_critic.pth" % (directory, filename))  # 存在线 critic（双 Q）权重
        torch.save(  # 存目标 critic 权重
            self.critic_target.state_dict(),  # 目标 critic 的 state_dict
            "%s/%s_critic_target.pth" % (directory, filename),  # 目标 critic 文件路径
        )  # 目标 critic 存盘调用结束

    # 【load】从磁盘恢复 4 个网络的权重
    # 【输入】filename/directory 与 save 时一致
    # 【流程位置】load_model=True 时在 __init__ 自动调用；也可手动调用以评估
    def load(self, filename, directory):  # 加载入口
        """
        Load the actor and critic networks (and their targets) from disk.

        Args:
            filename (str): Name used when saving the models.
            directory (Path): Directory where models are saved.
        """
        self.actor.load_state_dict(  # 恢复在线 actor
            torch.load("%s/%s_actor.pth" % (directory, filename))  # 读盘
        )  # actor 权重加载结束
        self.actor_target.load_state_dict(  # 恢复目标 actor
            torch.load("%s/%s_actor_target.pth" % (directory, filename))  # 读盘
        )  # actor_target 权重加载结束
        self.critic.load_state_dict(  # 恢复在线 critic
            torch.load("%s/%s_critic.pth" % (directory, filename))  # 读盘
        )  # critic 权重加载结束
        self.critic_target.load_state_dict(  # 恢复目标 critic
            torch.load("%s/%s_critic_target.pth" % (directory, filename))  # 读盘
        )  # critic_target 权重加载结束
        print(f"Loaded weights from: {directory}")  # 打印加载来源便于确认

    # 【prepare_state】把原始传感器观测加工成网络输入向量（特征工程）
    # 【输入】激光雷达序列 + 目标相对量（距离/cos/sin）+ 终止标志 + 上一步动作
    # 【输出】state：长度 state_dim 的列表（雷达最小值分箱 + 5 个附加特征）；terminal：0/1
    # 【教学】分箱取最小值=降维且保留"最近障碍距离"信息，是避障任务的标准特征工程
    def prepare_state(self, latest_scan, distance, cos, sin, collision, goal, action):  # 特征工程入口：原始观测→归一化状态向量
        """
        Prepare the input state vector for training or inference.

        Combines processed laser scan data, goal vector, and past action
        into a normalized state input matching the input dimension.

        Args:
            latest_scan (list or np.ndarray): Laser scan data.
            distance (float): Distance to goal.
            cos (float): Cosine of the heading angle to goal.
            sin (float): Sine of the heading angle to goal.
            collision (bool): Whether a collision occurred.
            goal (bool): Whether the goal has been reached.
            action (list or np.ndarray): Last executed action [linear_vel, angular_vel].

        Returns:
            (tuple):
                - state (list): Prepared and normalized state vector.
                - terminal (int): 1 if episode should terminate (goal or collision), else 0.
        """
        latest_scan = np.array(latest_scan)  # 列表转 numpy 数组，便于向量化处理

        inf_mask = np.isinf(latest_scan)  # 找出超出量程的 inf 读数（无回波=前方开阔）
        latest_scan[inf_mask] = 7.0  # inf 统一替换为最大可感距离 7m

        max_bins = self.state_dim - 5  # 雷达特征可用维数=总维数减去 5 个附加特征
        bin_size = int(np.ceil(len(latest_scan) / max_bins))  # 每箱容纳的射线数（向上取整保证全覆盖）

        # Initialize the list to store the minimum values of each bin  # 各箱最小值列表（英文原注保留）
        min_values = []  # 存放每箱的"最近障碍距离"

        # Loop through the data and create bins  # 分箱循环（英文原注保留）
        for i in range(0, len(latest_scan), bin_size):  # 按 bin_size 步长遍历雷达序列
            # Get the current bin  # 取当前箱切片（英文原注保留）
            bin = latest_scan[i : i + min(bin_size, len(latest_scan) - i)]  # 末箱可能不满，取剩余长度
            # Find the minimum value in the current bin and append it to the min_values list  # 箱内最小值
            min_values.append(min(bin) / 7)  # 除以量程 7，归一化到 [0,1]

        # Normalize to [0, 1] range  # 附加特征同样归一化（英文原注保留）
        distance /= 10  # 距离除以 10（与 distance_norm 对应）
        lin_vel = action[0] * 2  # 线速度 [-0.5,0.5]→[-1,1]（max_lin_vel=0.5）
        ang_vel = (action[1] + 1) / 2  # 角速度 [-1,1]→[0,1]
        state = min_values + [distance, cos, sin] + [lin_vel, ang_vel]  # 拼接：雷达箱 + 3 目标量 + 2 速度量

        assert len(state) == self.state_dim, f"{len(state), self.state_dim}"  # 维数自检，防配置错位
        terminal = 1 if collision or goal else 0  # 碰撞或到达目标都算终止（done=1，训练时不再自举）

        return state, terminal  # 返回状态向量与终止标志
