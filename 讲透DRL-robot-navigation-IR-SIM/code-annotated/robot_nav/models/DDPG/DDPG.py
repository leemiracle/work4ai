from pathlib import Path  # 路径工具：checkpoint 目录创建与模型文件路径拼接

import numpy as np  # NumPy：激光雷达数组处理、探索噪声采样
import torch  # PyTorch：张量运算 + 自动微分，RL 训练的核心引擎
import torch.nn as nn  # 神经网络模块：Linear/Tanh 等可学习层都来自这里
import torch.nn.functional as F  # 函数式接口：leaky_relu/mse_loss 等无状态运算
from numpy import inf  # 正无穷：作 max_Q 初始值（任何 Q 都大于 -inf，首次比较必被替换）
from torch.utils.tensorboard import SummaryWriter  # TensorBoard 写入器：把训练曲线落盘可视化

from robot_nav.utils import get_max_bound  # 本仓工具：按机器人运动学推导 Q 值物理上界（max-bound 正则用）


# 【Actor·策略网络】DDPG 的"演员"：确定性策略 π(s)——同一状态总输出同一动作，探索靠外加噪声
# 【输入输出】s: (B, state_dim) → a: (B, action_dim)，经 tanh 压缩到 (-1,1)
# 【流程位置】被实例化两次：在线 actor（被优化）+ actor_target（算 TD 目标、慢速跟随）
# 【教学】Actor-Critic（演员-评论家）架构：演员决策，评论家给动作打分（估 Q 值）指导演员改进
class Actor(nn.Module):  # 继承 nn.Module：获得参数注册/保存/迁移能力
    """
    Actor network for the DDPG algorithm.

    This network maps input states to actions using a fully connected feedforward architecture.
    It uses Leaky ReLU activations in the hidden layers and a tanh activation at the output
    to ensure the output actions are in the range [-1, 1].

    Architecture:
        - Linear(state_dim → 400) + LeakyReLU
        - Linear(400 → 300) + LeakyReLU
        - Linear(300 → action_dim) + Tanh

    Args:
        state_dim (int): Dimension of the input state.
        action_dim (int): Dimension of the output action space.
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
        Forward pass of the actor network.

        Args:
            s (torch.Tensor): Input state tensor of shape (batch_size, state_dim).

        Returns:
            (torch.Tensor): Output action tensor of shape (batch_size, action_dim), scaled to [-1, 1].
        """
        s = F.leaky_relu(self.layer_1(s))  # 层1+LeakyReLU；(B, state_dim)→(B, 400)
        s = F.leaky_relu(self.layer_2(s))  # 层2+LeakyReLU；(B, 400)→(B, 300)
        a = self.tanh(self.layer_3(s))  # 输出层+tanh；(B, 300)→(B, action_dim)
        return a  # 返回确定性动作


# 【Critic·单 Q 网络】DDPG 的"评论家"：只有一个 Q 估计器（TD3 在此基础上加倍并取 min）
# 【职责】评估状态-动作对的价值 Q(s,a)，为 actor 提供"往哪个方向改动作"的梯度
# 【输入输出】s: (B, state_dim)、a: (B, action_dim) → q: (B,1)
# 【教学】Q 值=在状态 s 执行动作 a 后的期望累计回报；单 Q 自举易高估（正向噪声只增不减、
#        误差被指数放大），这正是 TD3 引入孪生 critic 取 min 的动机
class Critic(nn.Module):  # 继承 nn.Module：单 Q 独立成模块
    """
    Critic network for the DDPG algorithm.

    This network evaluates the Q-value of a given state-action pair. It separately processes
    state and action inputs through linear layers, combines them, and passes the result through
    another linear layer to predict a scalar Q-value.

    Architecture:
        - Linear(state_dim → 400) + LeakyReLU
        - Linear(400 → 300) [state branch]
        - Linear(action_dim → 300) [action branch]
        - Combine both branches, apply LeakyReLU
        - Linear(300 → 1) for Q-value output

    Args:
        state_dim (int): Dimension of the input state.
        action_dim (int): Dimension of the input action.
    """

    # 【__init__】搭建单个 Q 网络：状态/动作两分支在 300 维处融合
    # 【要点】与 TD3 版的区别：无第二套 layer_4~6（即无孪生 Q）
    def __init__(self, state_dim, action_dim):  # 构造函数：状态 state_dim + 动作 action_dim 进，一个标量 Q 出
        super(Critic, self).__init__()  # 初始化 nn.Module 基类

        self.layer_1 = nn.Linear(state_dim, 400)  # 状态入层：(B, state_dim)→(B, 400)
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # 入层 Kaiming 初始化
        self.layer_2_s = nn.Linear(400, 300)  # 状态分支第二层：(B, 400)→(B, 300)
        torch.nn.init.kaiming_uniform_(self.layer_2_s.weight, nonlinearity="leaky_relu")  # 状态分支初始化
        self.layer_2_a = nn.Linear(action_dim, 300)  # 动作分支：(B, action_dim)→(B, 300)，与状态分支同维以便相加融合
        torch.nn.init.kaiming_uniform_(self.layer_2_a.weight, nonlinearity="leaky_relu")  # 动作分支初始化
        self.layer_3 = nn.Linear(300, 1)  # 输出头：(B, 300)→(B, 1) 标量 Q 值
        torch.nn.init.kaiming_uniform_(self.layer_3.weight, nonlinearity="leaky_relu")  # 输出头初始化

    # 【forward】前向传播：状态+动作→Q 值
    # 【输入】s: (B, state_dim)、a: (B, action_dim)；【输出】q: (B,1)
    def forward(self, s, a):  # 前向传播入口：状态与动作同时输入
        """
        Forward pass of the critic network.

        Args:
            s (torch.Tensor): State tensor of shape (batch_size, state_dim).
            a (torch.Tensor): Action tensor of shape (batch_size, action_dim).

        Returns:
            (torch.Tensor): Q-value tensor of shape (batch_size, 1).
        """
        s1 = F.leaky_relu(self.layer_1(s))  # 状态编码：(B, state_dim)→(B, 400)
        self.layer_2_s(s1)  # 调用层做前向但丢弃返回值：遗留写法，无副作用的冗余计算
        self.layer_2_a(a)  # 同上；真正的融合计算在下面三行手工完成
        s11 = torch.mm(s1, self.layer_2_s.weight.data.t())  # 状态分支投影 (B,400)×(400,300)→(B,300)；.data 使 layer_2 权重脱离计算图、不收梯度
        s12 = torch.mm(a, self.layer_2_a.weight.data.t())  # 动作分支投影：(B, action_dim)→(B, 300)
        s1 = F.leaky_relu(s11 + s12 + self.layer_2_a.bias.data)  # 两分支相加融合（只加一个偏置）再激活：(B, 300)
        q = self.layer_3(s1)  # Q 输出：(B, 300)→(B, 1)

        return q  # 返回单个 Q 估计（TD3 则返回 q1、q2 元组）


# DDPG network  # DDPG 智能体主类：算法编排层（英文原注保留）
# 【DDPG 类】Deep Deterministic Policy Gradient——连续控制 RL 的开山确定性策略梯度算法
# 【职责】单 critic 版 actor-critic：本实现已借用 TD3 的目标策略平滑与延迟更新，唯缺孪生 critic
# 【对外接口】get_action（交互）、train（训练）、save/load（存取）、prepare_state（特征工程）
# 【流程位置】训练脚本每 episode 调一次 train()（内含 iterations 次梯度步），环境交互走 get_action()
class DDPG(object):  # 纯 Python 编排类（非 nn.Module）：聚合网络、优化器与训练逻辑
    """
    Deep Deterministic Policy Gradient (DDPG) agent implementation.

    This class encapsulates the actor-critic learning framework using DDPG, which is suitable
    for continuous action spaces. It supports training, action selection, model saving/loading,
    and state preparation for a reinforcement learning agent, specifically designed for robot navigation.

    Args:
        state_dim (int): Dimension of the input state.
        action_dim (int): Dimension of the action space.
        max_action (float): Maximum action value allowed.
        device (torch.device): Computation device (CPU or GPU).
        lr (float): Learning rate for the optimizers. Default is 1e-4.
        save_every (int): Frequency of saving the model in training iterations. 0 means no saving. Default is 0.
        load_model (bool): Flag indicating whether to load a model from disk. Default is False.
        save_directory (Path): Directory to save the model checkpoints. Default is "robot_nav/models/DDPG/checkpoint".
        model_name (str): Name used for saving and TensorBoard logging. Default is "DDPG".
        load_directory (Path): Directory to load model checkpoints from. Default is "robot_nav/models/DDPG/checkpoint".
        use_max_bound (bool): Whether to enforce a learned upper bound on the Q-value. Default is False.
        bound_weight (float): Weight of the upper bound loss penalty. Default is 0.25.
    """

    # 【__init__】建网络、配优化器、存超参
    # 【输入】state_dim/action_dim/max_action/device 必填，其余为带默认值超参
    # 【要点】4 个网络（actor/critic 及各自 target）+ 2 个 Adam 优化器 + TensorBoard 写入器
    def __init__(  # 构造函数开始（多行签名）
        self,  # 实例自身
        state_dim,  # 状态维数：雷达分箱数 + 距离/cos/sin/线速度/角速度共 5 个附加量
        action_dim,  # 动作维数 = 2（线速度、角速度）
        max_action,  # 动作幅值上界，用于把网络输出裁剪回合法区间
        device,  # torch.device："cpu" 或 "cuda"
        lr=1e-4,  # 学习率：actor 与 critic 共用
        save_every=0,  # 每隔多少次 train() 调用自动存盘；0 表示不自动存
        load_model=False,  # 是否构造时从磁盘恢复已有权重
        save_directory=Path("robot_nav/models/DDPG/checkpoint"),  # 存盘目录
        model_name="DDPG",  # 模型名：存盘文件名前缀 + TensorBoard 注释
        load_directory=Path("robot_nav/models/DDPG/checkpoint"),  # 加载目录
        use_max_bound=False,  # 是否启用 Q 值物理上界正则（本仓特色功能）
        bound_weight=0.25,  # 上界正则项权重系数
    ):  # 构造参数列表结束
        # Initialize the Actor network  # 初始化策略网络（英文原注保留）
        self.device = device  # 保存设备引用，供张量搬运
        self.actor = Actor(state_dim, action_dim).to(self.device)  # 在线策略网络：真正被训练的演员
        self.actor_target = Actor(state_dim, action_dim).to(self.device)  # 目标策略网络：为 TD 目标提供稳定基线
        self.actor_target.load_state_dict(self.actor.state_dict())  # 初始时 target 与在线网络完全同权重
        self.actor_optimizer = torch.optim.Adam(params=self.actor.parameters(), lr=lr)  # actor 专属 Adam 优化器

        # Initialize the Critic networks  # 初始化评论家网络（英文原注保留）
        self.critic = Critic(state_dim, action_dim).to(self.device)  # 在线 Q 网络（单 Q）
        self.critic_target = Critic(state_dim, action_dim).to(self.device)  # 目标 Q 网络：只用来算 TD 目标
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
        Selects an action based on the observation.

        Args:
            obs (np.array): The current state observation.
            add_noise (bool): Whether to add exploration noise to the action.

        Returns:
            (np.array): Action selected by the actor network.
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
        Computes the action for a given state using the actor network.

        Args:
            state (np.array): Environment state.

        Returns:
            (np.array): Action values as output by the actor network.
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
        policy_noise=0.2,  # 目标策略平滑：给目标动作加噪的标准差（TD3 技巧，本仓 DDPG 一并沿用）
        noise_clip=0.5,  # 目标噪声裁剪幅度，防平滑噪声过大（同为 TD3 技巧）
        policy_freq=2,  # 延迟更新频率：每 2 次 critic 更新才做 1 次 actor 更新（同为 TD3 技巧）
        max_lin_vel=0.5,  # 最大线速度（max-bound 上界估计用）
        max_ang_vel=1,  # 最大角速度（同上）
        goal_reward=100,  # 到达目标的奖励（同上）
        distance_norm=10,  # 距离归一化尺度（同上）
        time_step=0.3,  # 仿真步长/秒（同上）
    ):  # 训练参数列表结束
        """
        Trains the actor and critic networks using a replay buffer and soft target updates.

        Args:
            replay_buffer (ReplayBuffer): Replay buffer object with a sample_batch method.
            iterations (int): Number of training iterations.
            batch_size (int): Size of each training batch.
            discount (float): Discount factor for future rewards.
            tau (float): Soft update factor for target networks.
            policy_noise (float): Standard deviation of noise added to target policy.
            noise_clip (float): Maximum value to clip target policy noise.
            policy_freq (int): Frequency of actor and target updates.
            max_lin_vel (float): Maximum linear velocity, used in Q-bound calculation.
            max_ang_vel (float): Maximum angular velocity, used in Q-bound calculation.
            goal_reward (float): Reward given upon reaching goal.
            distance_norm (float): Distance normalization factor.
            time_step (float): Time step used in max bound calculation.
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
            target_Q = self.critic_target(next_state, next_action)  # 单 Q 目标值 (B,1)——TD3 在此取双 Q 的 min

            av_Q += torch.mean(target_Q)  # 累计批均值供监控
            max_Q = max(max_Q, torch.max(target_Q))  # 刷新历史最大 Q
            # Calculate the final Q value from the target network parameters by using Bellman equation  # Bellman 目标
            target_Q = reward + ((1 - done) * discount * target_Q).detach()  # y=r+γ(1-done)·Q'；终止步不自举；detach 切断梯度

            # Get the Q values of the basis networks with the current parameters  # 在线 critic 对旧 (s,a) 的估计
            current_Q = self.critic(state, action)  # (B,1)，带梯度

            # Calculate the loss between the current Q value and the target Q value  # TD 误差
            loss = F.mse_loss(current_Q, target_Q)  # 当前 Q 向 Bellman 目标回归的均方误差

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
                max_excess_Q = F.relu(current_Q - max_bound)  # Q 超出上界的部分（未超则恒 0）
                max_bound_loss = (max_excess_Q**2).mean()  # 超额部分的平方惩罚（hinge²）
                # Add loss for Q values exceeding maximum possible upper bound  # 把超额惩罚并入总损失（英文原注保留）
                loss += self.bound_weight * max_bound_loss  # 加权后累加进 critic 损失

            # Perform the gradient descent  # 执行 critic 的反向传播与参数更新
            self.critic_optimizer.zero_grad()  # 清零旧梯度（PyTorch 梯度默认累加）
            loss.backward()  # 反传；detach 过的 target_Q 不产生梯度（目标只是回归靶）
            self.critic_optimizer.step()  # Adam 走一步，只更新 critic 参数

            if it % policy_freq == 0:  # 延迟策略更新：每 policy_freq 次 critic 更新才进一次本分支
                # Maximize the actor output value by performing gradient descent on negative Q values  # actor 更新目标
                # (essentially perform gradient ascent)  # 对 -Q 下降=对 Q 上升（英文原注保留）
                actor_grad = self.critic(state, self.actor(state))  # Q(s,π(s))：单 Q 无需解包元组（TD3 为 q1,q2）
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
        Saves the model parameters to disk.

        Args:
            filename (str): Base filename for saving the model components.
            directory (str or Path): Directory where the model files will be saved.
        """
        Path(directory).mkdir(parents=True, exist_ok=True)  # 递归建目录，已存在不报错
        torch.save(self.actor.state_dict(), "%s/%s_actor.pth" % (directory, filename))  # 存在线 actor 权重
        torch.save(  # 存目标 actor 权重
            self.actor_target.state_dict(),  # 目标 actor 的 state_dict
            "%s/%s_actor_target.pth" % (directory, filename),  # 目标 actor 文件路径
        )  # 目标 actor 存盘调用结束
        torch.save(self.critic.state_dict(), "%s/%s_critic.pth" % (directory, filename))  # 存在线 critic 权重
        torch.save(  # 存目标 critic 权重
            self.critic_target.state_dict(),  # 目标 critic 的 state_dict
            "%s/%s_critic_target.pth" % (directory, filename),  # 目标 critic 文件路径
        )  # 目标 critic 存盘调用结束

    # 【load】从磁盘恢复 4 个网络的权重
    # 【输入】filename/directory 与 save 时一致
    # 【流程位置】load_model=True 时在 __init__ 自动调用；也可手动调用以评估
    def load(self, filename, directory):  # 加载入口
        """
        Loads model parameters from disk.

        Args:
            filename (str): Base filename used for loading model components.
            directory (str or Path): Directory to load the model files from.
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
        Processes raw sensor input and additional information into a normalized state representation.

        Args:
            latest_scan (list or np.array): Raw LIDAR or laser scan data.
            distance (float): Distance to the goal.
            cos (float): Cosine of the angle to the goal.
            sin (float): Sine of the angle to the goal.
            collision (bool): Whether a collision has occurred.
            goal (bool): Whether the goal has been reached.
            action (list or np.array): The action taken in the previous step.

        Returns:
            (tuple): (state vector, terminal flag)
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

        assert len(state) == self.state_dim  # 维数自检，防配置错位
        terminal = 1 if collision or goal else 0  # 碰撞或到达目标都算终止（done=1，训练时不再自举）

        return state, terminal  # 返回状态向量与终止标志
