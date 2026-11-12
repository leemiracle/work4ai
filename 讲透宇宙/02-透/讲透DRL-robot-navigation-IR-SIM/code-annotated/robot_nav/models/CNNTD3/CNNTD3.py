from pathlib import Path  # 导入 Path：跨平台路径对象，用于创建存档目录、拼接 checkpoint 文件名

import numpy as np  # 导入 numpy：环境侧数组运算、动作探索噪声采样
import torch  # 导入 PyTorch 主库：张量运算 + autograd 自动求导（整个训练的地基）
import torch.nn as nn  # 导入神经网络模块：Linear/Conv1d 等带可学习参数的层
import torch.nn.functional as F  # 导入函数式接口：leaky_relu/mse_loss 等无参数算子
from numpy import inf  # 导入正无穷：作 max_Q 统计的初始最小值
from torch.utils.tensorboard import SummaryWriter  # 导入 TensorBoard 写入器：记录 loss/Q 值训练曲线

from robot_nav.utils import get_max_bound  # 导入"最大回报上界"工具函数：CNNTD3 特有的 Q 值正则项使用（见 train）


# ===================== 类：Actor（演员 / 确定性策略网络） =====================
# 职责：把单帧观测映射为连续动作。TD3 属 DDPG 家族，策略是确定性的（同一输入永远同一输出），
#       探索靠外部加噪声，而非从分布采样。
# 输入输出：s (B, state_dim)，本仓 state_dim=185 = 180 束激光 + 5 维导航量；输出 a (B, action_dim)∈(-1,1)。
# 算法位置：推理时 get_action 调它选动作；训练时朝 critic 估值 Q 的梯度上升方向微调（确定性策略梯度）。
class Actor(nn.Module):  # Actor：确定性策略网络（演员）
    """
    Actor network for the CNNTD3 agent.

    This network takes as input a state composed of laser scan data, goal position encoding,
    and previous action. It processes the scan through a 1D CNN stack and embeds the other
    inputs before merging all features through fully connected layers to output a continuous
    action vector.

    Args:
        action_dim (int): The dimension of the action space.

    Architecture:
        - 1D CNN layers process the laser scan data.
        - Fully connected layers embed the goal vector (cos, sin, distance) and last action.
        - Combined features are passed through two fully connected layers with LeakyReLU.
        - Final action output is scaled with Tanh to bound the values.
    """

    # ===================== __init__：搭建 Actor 的网络层 =====================
    # 三段式结构：3 层 1D 卷积提激光特征 + 2 个小嵌入层（目标/上一步动作）+ 3 层 MLP 输出动作
    def __init__(self, action_dim):  # action_dim：动作维数，本仓为 2（线速度、角速度）
        super(Actor, self).__init__()  # 调父类构造：注册参数/子模块，.to()/.parameters() 才可用

        self.cnn1 = nn.Conv1d(1, 4, kernel_size=8, stride=4)  # 卷积层1：1→4 通道、核宽8/步幅4；(B,1,180)->(B,4,44)，学"近距离有障碍"类局部模式
        self.cnn2 = nn.Conv1d(4, 8, kernel_size=8, stride=4)  # 卷积层2：4→8 通道；(B,4,44)->(B,8,10)，堆叠扩大感受野、压缩序列长度
        self.cnn3 = nn.Conv1d(8, 4, kernel_size=4, stride=2)  # 卷积层3：8→4 通道降维；(B,8,10)->(B,4,4)，防过拟合并让特征紧凑

        self.goal_embed = nn.Linear(3, 10)  # 目标嵌入：3 维[归一化距离,cos,sin]→10 维，与其他特征等宽便于拼接
        self.action_embed = nn.Linear(2, 10)  # 上一步动作嵌入：2 维[线速,角速]→10 维（引入动作记忆，利于输出平滑）

        self.layer_1 = nn.Linear(36, 400)  # 融合层1：36→400；36 = 卷积展平16 + 目标10 + 动作10
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # Kaiming 初始化：按 leaky_relu 的方差保持增益设权重，避免早期梯度消失/爆炸
        self.layer_2 = nn.Linear(400, 300)  # 融合层2：400→300，逐层收窄
        torch.nn.init.kaiming_uniform_(self.layer_2.weight, nonlinearity="leaky_relu")  # 同上，对 layer_2 做 Kaiming 初始化
        self.layer_3 = nn.Linear(300, action_dim)  # 输出层：300→action_dim，产生原始动作值
        self.tanh = nn.Tanh()  # tanh 激活：把动作压到 (-1,1)，外层再乘 max_action 满足物理边界

    # ===================== forward：状态 → 动作的前向传播 =====================
    # 输入：s (B,185) 或单条 (185,)（内部自动补 batch 维）；输出：a (B,action_dim)∈(-1,1)
    # 教学要点：状态切分（reshape）逻辑——末 5 位是导航量，其余全是激光束
    def forward(self, s):  # 前向传播：状态→动作
        """
        Forward pass through the Actor network.

        Args:
            s (torch.Tensor): Input state tensor of shape (batch_size, state_dim).
                              The last 5 elements are [distance, cos, sin, lin_vel, ang_vel].

        Returns:
            (torch.Tensor): Action tensor of shape (batch_size, action_dim),
                          with values in range [-1, 1] due to tanh activation.
        """
        if len(s.shape) == 1:  # 若输入是单条状态 (185,)（无 batch 维）
            s = s.unsqueeze(0)  # 补成 (1,185)，统一按批量张量处理
        laser = s[:, :-5]  # 切出激光段：去掉末 5 位后的全部，(B,185)->(B,180)
        goal = s[:, -5:-2]  # 切出目标段：倒数第 5~3 位 [距离,cos,sin]，(B,3)
        act = s[:, -2:]  # 切出上一步动作段：末 2 位 [线速,角速]，(B,2)
        laser = laser.unsqueeze(1)  # 增加通道维：Conv1d 要求 (B,C,L)，(B,180)->(B,1,180)，激光整体当作 1 个通道的一维信号

        l = F.leaky_relu(self.cnn1(laser))  # 卷积1+leaky_relu（负区斜率0.2，防神经元"死区"）：(B,1,180)->(B,4,44)
        l = F.leaky_relu(self.cnn2(l))  # 卷积2：(B,4,44)->(B,8,10)；大步幅逐层压缩扫描序列，等效多尺度看障碍分布
        l = F.leaky_relu(self.cnn3(l))  # 卷积3：(B,8,10)->(B,4,4)；4 通道×4 位置，感受野已覆盖整圈激光
        l = l.flatten(start_dim=1)  # 从第 1 维起展平（保留 batch 维）：(B,4,4)->(B,16)

        g = F.leaky_relu(self.goal_embed(goal))  # 目标嵌入+激活：3→10 维，(B,3)->(B,10)

        a = F.leaky_relu(self.action_embed(act))  # 上步动作嵌入+激活：2→10 维，(B,2)->(B,10)

        s = torch.concat((l, g, a), dim=-1)  # 三路特征在最后维拼接：16+10+10=36，(B,16)/(B,10)/(B,10)->(B,36)

        s = F.leaky_relu(self.layer_1(s))  # MLP 融合层1：36→400
        s = F.leaky_relu(self.layer_2(s))  # MLP 融合层2：400→300
        a = self.tanh(self.layer_3(s))  # 输出层+tanh：300→action_dim 并压到 (-1,1)
        return a  # 返回动作 (B,action_dim)，供 get_action 加噪或直接执行


# ===================== 类：Critic（评论家 / 双 Q 值网络） =====================
# 职责：给"状态-动作对"打分（Q 值 = 从此状态执行此动作后的期望累计回报）。Q-learning 的核心部件。
# 结构特点：Q1/Q2 两个独立打分头（TD3 的 Twin Q，取 min 抗高估），CNN+嵌入编码器为两
#           头共享；动作不与状态早拼接，而是各自过线性层后相加（TD3 论文推荐）。
# 输入输出：s (B,185)、action (B,action_dim)；输出 q1/q2 各 (B,1)。
class Critic(nn.Module):  # Critic：孪生 Q 值网络（评论家）
    """
    Critic network for the CNNTD3 agent.

    The Critic estimates Q-values for state-action pairs using two separate sub-networks
    (Q1 and Q2), as required by the TD3 algorithm. Each sub-network uses a combination of
    CNN-extracted features, embedded goal and previous action features, and the current action.

    Args:
        action_dim (int): The dimension of the action space.

    Architecture:
        - Shared CNN layers process the laser scan input.
        - Goal and previous action are embedded and concatenated.
        - Each Q-network uses separate fully connected layers to produce scalar Q-values.
        - Both Q-networks receive the full state and current action.
        - Outputs two Q-value tensors (Q1, Q2) for TD3-style training and target smoothing.
    """

    # ===================== __init__：搭建 Critic（共享编码器 + 孪生 Q 头） =====================
    # 共享部分与 Actor 同构（3 卷积+2 嵌入）；Q1 用 layer_1/2/3，Q2 用 layer_4/5/6，互不共享参数
    def __init__(self, action_dim):  # action_dim：动作维数（本仓 2）
        super(Critic, self).__init__()  # 注册 nn.Module 机制
        self.cnn1 = nn.Conv1d(1, 4, kernel_size=8, stride=4)  # 共享卷积1：(B,1,180)->(B,4,44)
        self.cnn2 = nn.Conv1d(4, 8, kernel_size=8, stride=4)  # 共享卷积2：(B,4,44)->(B,8,10)
        self.cnn3 = nn.Conv1d(8, 4, kernel_size=4, stride=2)  # 共享卷积3：(B,8,10)->(B,4,4)

        self.goal_embed = nn.Linear(3, 10)  # 共享目标嵌入：3→10
        self.action_embed = nn.Linear(2, 10)  # 共享上步动作嵌入：2→10（注意：嵌入的是状态里的上一步动作，不是待评估动作）

        self.layer_1 = nn.Linear(36, 400)  # Q1 第 1 层：36→400（输入为共享编码的 36 维拼接特征）
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q1 第 1 层权重
        self.layer_2_s = nn.Linear(400, 300)  # Q1 状态流分支：400→300（"s"=state 流）
        torch.nn.init.kaiming_uniform_(self.layer_2_s.weight, nonlinearity="leaky_relu")  # Kaiming 初始化状态流权重
        self.layer_2_a = nn.Linear(action_dim, 300)  # Q1 动作流分支：action_dim→300（"a"=action 流，待评估动作从这进）
        torch.nn.init.kaiming_uniform_(self.layer_2_a.weight, nonlinearity="leaky_relu")  # Kaiming 初始化动作流权重
        self.layer_3 = nn.Linear(300, 1)  # Q1 输出层：300→1，单个 Q 值
        torch.nn.init.kaiming_uniform_(self.layer_3.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q1 输出层

        self.layer_4 = nn.Linear(36, 400)  # Q2 第 1 层：36→400（与 Q1 结构相同、参数独立）
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # 注意：此处初始化的仍是 layer_1（疑似笔误，按命名本意应是 layer_4），效果是 layer_4 保持默认初始化
        self.layer_5_s = nn.Linear(400, 300)  # Q2 状态流分支：400→300
        torch.nn.init.kaiming_uniform_(self.layer_5_s.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q2 状态流
        self.layer_5_a = nn.Linear(action_dim, 300)  # Q2 动作流分支：action_dim→300
        torch.nn.init.kaiming_uniform_(self.layer_5_a.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q2 动作流
        self.layer_6 = nn.Linear(300, 1)  # Q2 输出层：300→1
        torch.nn.init.kaiming_uniform_(self.layer_6.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q2 输出层

    # ===================== forward：孪生 Q 值前向传播 =====================
    # 输入：s (B,185)、action (B,action_dim)；输出：(q1, q2) 各 (B,1)
    # 教学要点：动作分支用 .data 手工矩阵乘（沿自经典 TD3 参考实现），两流"相加晚融合"
    def forward(self, s, action):  # 前向传播：(s,a)→(q1,q2)
        """
        Forward pass through both Q-networks of the Critic.

        Args:
            s (torch.Tensor): Input state tensor of shape (batch_size, state_dim).
                              The last 5 elements are [distance, cos, sin, lin_vel, ang_vel].
            action (torch.Tensor): Current action tensor of shape (batch_size, action_dim).

        Returns:
            (tuple):
                - q1 (torch.Tensor): First Q-value estimate (batch_size, 1).
                - q2 (torch.Tensor): Second Q-value estimate (batch_size, 1).
        """
        laser = s[:, :-5]  # 切激光段：(B,185)->(B,180)
        goal = s[:, -5:-2]  # 切目标段 [距离,cos,sin]：(B,3)
        act = s[:, -2:]  # 切上一步动作段 [线速,角速]：(B,2)
        laser = laser.unsqueeze(1)  # 加通道维：(B,180)->(B,1,180)

        l = F.leaky_relu(self.cnn1(laser))  # 共享卷积1：(B,1,180)->(B,4,44)
        l = F.leaky_relu(self.cnn2(l))  # 共享卷积2：(B,4,44)->(B,8,10)
        l = F.leaky_relu(self.cnn3(l))  # 共享卷积3：(B,8,10)->(B,4,4)
        l = l.flatten(start_dim=1)  # 展平：(B,4,4)->(B,16)

        g = F.leaky_relu(self.goal_embed(goal))  # 目标嵌入：(B,3)->(B,10)

        a = F.leaky_relu(self.action_embed(act))  # 上步动作嵌入：(B,2)->(B,10)

        s = torch.concat((l, g, a), dim=-1)  # 拼接共享特征：(B,36)，Q1/Q2 都从这里出发

        s1 = F.leaky_relu(self.layer_1(s))  # Q1 第 1 层：36→400
        self.layer_2_s(s1)  # 直接调用但丢弃返回值（沿自经典 TD3 参考实现的遗留写法，真正生效的是下面两行的手工矩阵乘）
        self.layer_2_a(action)  # 同上：结果被丢弃，仅为保持原实现
        s11 = torch.mm(s1, self.layer_2_s.weight.data.t())  # 手工复刻 Linear 前向——状态流：(B,400)x(400,300)->(B,300)；.data 脱离计算图，该权重不接收梯度
        s12 = torch.mm(action, self.layer_2_a.weight.data.t())  # 手工复刻——动作流：(B,action_dim)x(action_dim,300)->(B,300)；梯度仍可经 action 回传到 actor
        s1 = F.leaky_relu(s11 + s12 + self.layer_2_a.bias.data)  # 两流逐元素相加（晚融合，TD3 论文建议：动作不与状态早拼接）+偏置，再激活：->(B,300)
        q1 = self.layer_3(s1)  # Q1 输出：(B,300)->(B,1)

        s2 = F.leaky_relu(self.layer_4(s))  # Q2 第 1 层：36→400（同样输入共享特征）
        self.layer_5_s(s2)  # 同 Q1 模式：调用结果丢弃
        self.layer_5_a(action)  # 同上
        s21 = torch.mm(s2, self.layer_5_s.weight.data.t())  # Q2 状态流：(B,400)->(B,300)
        s22 = torch.mm(action, self.layer_5_a.weight.data.t())  # Q2 动作流：(B,action_dim)->(B,300)
        s2 = F.leaky_relu(s21 + s22 + self.layer_5_a.bias.data)  # Q2 两流相加晚融合+激活：(B,300)
        q2 = self.layer_6(s2)  # Q2 输出：(B,300)->(B,1)
        return q1, q2  # 返回孪生 Q 值，训练时取 min 抗高估


# CNNTD3 network —— CNNTD3 智能体主类（网络组装 + TD3 训练循环 + 存取 + ROS 状态预处理）
# ===================== 类：CNNTD3（TD3 智能体总控） =====================
# 职责：组装 actor/critic 及各自 target 网络与优化器；实现 TD3 训练循环、动作选择、存/取档、状态预处理。
# TD3 三大改进（相对 DDPG）：双 Q 取 min / 目标动作加裁剪噪声（目标策略平滑）/ 策略延迟更新。
# 本仓特色：use_max_bound 开启后给 critic 加"Q 值不得超过物理回报上界"的正则项。
class CNNTD3(object):  # 智能体总控类（非 nn.Module，内部持有 4 个网络）
    """
    CNNTD3 (Twin Delayed Deep Deterministic Policy Gradient with CNN-based inputs) agent for
    continuous control tasks.

    This class encapsulates the full implementation of the TD3 algorithm using neural network
    architectures for the actor and critic, with optional bounding for critic outputs to
    regularize learning. The agent is designed to train in environments where sensor
    observations (e.g., LiDAR) are used for navigation tasks.

    Args:
        state_dim (int): Dimension of the input state.
        action_dim (int): Dimension of the output action.
        max_action (float): Maximum magnitude of the action.
        device (torch.device): Torch device to use (CPU or GPU).
        lr (float): Learning rate for both actor and critic optimizers.
        save_every (int): Save model every N training iterations (0 to disable).
        load_model (bool): Whether to load a pre-trained model at initialization.
        save_directory (Path): Path to the directory for saving model checkpoints.
        model_name (str): Base name for the saved model files.
        load_directory (Path): Path to load model checkpoints from (if `load_model=True`).
        use_max_bound (bool): Whether to apply maximum Q-value bounding during training.
        bound_weight (float): Weight for the bounding loss term in total loss.
    """

    # ===================== __init__：智能体初始化 =====================
    # 建 4 个网络（actor/critic 及各自 target）+ 2 个 Adam 优化器 + 记录器；target 初始与主网络同权重
    def __init__(  # 构造函数（参数多，跨行书写）
        self,  # 实例自身（Python 惯例）
        state_dim,  # 状态维数（本仓 185）
        action_dim,  # 动作维数（本仓 2）
        max_action,  # 动作幅值上界，用于 clip 输出动作
        device,  # torch.device：CPU 或 GPU
        lr=1e-4,  # 学习率：actor/critic 共用（TD3 用小学习率求稳）
        save_every=0,  # 每 N 次 train 自动存档；0=关闭
        load_model=False,  # 构造时是否加载预训练权重
        save_directory=Path("robot_nav/models/CNNTD3/checkpoint"),  # 存档目录（默认仓内相对路径）
        model_name="CNNTD3",  # 模型名：存档文件前缀 + TensorBoard 注释
        load_directory=Path("robot_nav/models/CNNTD3/checkpoint"),  # 加载目录（load_model=True 时用）
        use_max_bound=False,  # 是否启用"Q 不超物理回报上界"正则（CNNTD3 特色）
        bound_weight=0.25,  # 上界正则项权重
    ):  # 参数表结束，函数体开始
        # Initialize the Actor network —— 初始化 Actor（当前策略网络）
        self.device = device  # 记录运行设备
        self.actor = Actor(action_dim).to(self.device)  # 在线 actor：选动作+被训练
        self.actor_target = Actor(action_dim).to(self.device)  # 目标 actor：actor 的慢速副本，用来算 TD 目标，稳定训练
        self.actor_target.load_state_dict(self.actor.state_dict())  # 目标网络初始权重 = actor 权重（训练中仅软更新缓慢跟随）
        self.actor_optimizer = torch.optim.Adam(params=self.actor.parameters(), lr=lr)  # actor 的 Adam 优化器

        # Initialize the Critic networks —— 初始化 Critic（在线+目标）
        self.critic = Critic(action_dim).to(self.device)  # 在线 critic：被回归训练估值
        self.critic_target = Critic(action_dim).to(self.device)  # 目标 critic：算 TD 目标用
        self.critic_target.load_state_dict(self.critic.state_dict())  # 目标 critic 初始与 critic 同权重
        self.critic_optimizer = torch.optim.Adam(params=self.critic.parameters(), lr=lr)  # critic 的 Adam 优化器

        self.action_dim = action_dim  # 记录动作维数（噪声采样用）
        self.max_action = max_action  # 记录动作幅值上界（clip 用）
        self.state_dim = state_dim  # 记录状态维数（prepare_state 断言用）
        self.writer = SummaryWriter(comment=model_name)  # TensorBoard 写入器，runs 目录区分模型
        self.iter_count = 0  # train 调用计数（记录曲线横坐标/定期存档）
        if load_model:  # 若指定加载预训练权重
            self.load(filename=model_name, directory=load_directory)  # 从 load_directory 读 4 个网络权重
        self.save_every = save_every  # 存档频率
        self.model_name = model_name  # 存档文件名前缀
        self.save_directory = save_directory  # 存档目录
        self.use_max_bound = use_max_bound  # 是否启用上界正则
        self.bound_weight = bound_weight  # 上界正则权重

    # ===================== get_action：带探索噪声的动作选择 =====================
    # 输入：obs 单条状态（np 数组）、add_noise 开关；输出：np 动作向量
    # 环境交互入口：训练时 add_noise=True 靠高斯噪声探索，评估时 False
    def get_action(self, obs, add_noise):  # 环境交互入口：选动作（可选加探索噪声）
        """
        Selects an action for a given observation.

        Args:
            obs (np.ndarray): The current observation/state.
            add_noise (bool): Whether to add exploration noise to the action.

        Returns:
            (np.ndarray): The selected action.
        """
        if add_noise:  # 训练期探索：确定性动作 + 高斯噪声（TD3 的探索方式，噪声不进网络）
            return (  # 返回带噪动作（跨行表达式的开括号）
                self.act(obs) + np.random.normal(0, 0.2, size=self.action_dim)  # act 出确定性动作，再叠加 N(0,0.2) 噪声
            ).clip(-self.max_action, self.max_action)  # 裁剪回合法动作范围后返回
        else:  # 评估期：不加噪声
            return self.act(obs)  # 直接返回确定性策略动作

    # ===================== act：纯前向的确定性动作 =====================
    # 输入：state（np 数组）；输出：展平的 np 动作向量
    # numpy→torch→网络→numpy 的桥接薄层
    def act(self, state):  # 纯前向取确定性动作（不加噪声）
        """
        Computes the deterministic action from the actor network for a given state.

        Args:
            state (np.ndarray): Input state.

        Returns:
            (np.ndarray): Action predicted by the actor network.
        """
        # Function to get the action from the actor —— 从 actor 取确定性动作
        state = torch.Tensor(state).to(self.device)  # np 状态转 torch 张量并搬至训练设备
        return self.actor(state).cpu().data.numpy().flatten()  # 前向→回 CPU→脱计算图→np 数组并展平成 (action_dim,)

    # training cycle —— 训练主循环（一次调用 = iterations 轮梯度更新）
    # ===================== train：TD3 训练循环 =====================
    # 输入：replay_buffer（经验回放池：存放 (s,a,r,done,s') 供随机抽样打破时间相关性）、iterations、batch_size 及 TD3 超参
    # 流程（每轮）：采样→目标动作加裁剪噪声→双 Q 取 min→贝尔曼目标→critic 回归（+可选上界正则）→延迟的 actor 更新→软更新
    def train(  # TD3 训练主循环（参数跨多行）
        self,  # 实例自身
        replay_buffer,  # 经验回放池
        iterations,  # 本轮调用的梯度迭代次数
        batch_size,  # 每次采样的批大小
        discount=0.99,  # 折扣因子 γ：未来奖励打 99 折，平衡远近回报
        tau=0.005,  # 软更新系数：target = τ*新 + (1-τ)*旧，缓慢跟随保稳定
        policy_noise=0.2,  # 目标策略平滑噪声强度 σ（加在目标动作上，抗 critic 尖峰过高估）
        noise_clip=0.5,  # 目标噪声裁剪范围 ±0.5，防噪声过大
        policy_freq=2,  # 策略（actor）延迟更新频率：每 2 轮 critic 更新才更新 1 次 actor
        max_lin_vel=0.5,  # 物理上界计算用：最大线速度 m/s
        max_ang_vel=1,  # 物理上界计算用：最大角速度 rad/s
        goal_reward=100,  # 到达目标的奖励值（上界计算用）
        distance_norm=10,  # 距离归一化常数（上界计算用）
        time_step=0.3,  # 单步时长秒数（上界计算用）
    ):  # 参数表结束，函数体开始
        """
        Trains the CNNTD3 agent using sampled batches from the replay buffer.

        Args:
            replay_buffer (ReplayBuffer): Buffer storing environment transitions.
            iterations (int): Number of training iterations.
            batch_size (int): Size of each training batch.
            discount (float): Discount factor for future rewards.
            tau (float): Soft update rate for target networks.
            policy_noise (float): Std. dev. of noise added to target policy.
            noise_clip (float): Maximum value for target policy noise.
            policy_freq (int): Frequency of actor and target network updates.
            max_lin_vel (float): Maximum linear velocity for bounding calculations.
            max_ang_vel (float): Maximum angular velocity for bounding calculations.
            goal_reward (float): Reward value for reaching the goal.
            distance_norm (float): Normalization factor for distance in bounding.
            time_step (float): Time delta between steps.
        """
        av_Q = 0  # 平均 Q 累计器（本轮所有迭代的目标 Q 均值之和，写 TensorBoard 用）
        max_Q = -inf  # 最大 Q 记录，初始化为负无穷
        av_loss = 0  # critic 损失累计器
        for it in range(iterations):  # 主循环：每轮做一次完整的 critic(+actor) 梯度更新
            # sample a batch from the replay buffer —— 从回放池随机采一批经验
            (  # 元组解包开始：一次拿到五元组经验批
                batch_states,  # 状态批 (B,185)
                batch_actions,  # 动作批 (B,2)
                batch_rewards,  # 奖励批 (B,)
                batch_dones,  # 终止标志批 (B,)
                batch_next_states,  # 下一状态批 (B,185)
            ) = replay_buffer.sample_batch(batch_size)  # 均匀随机抽样，打破样本时间相关性
            state = torch.Tensor(batch_states).to(self.device)  # 转 tensor 上设备：(B,185)
            next_state = torch.Tensor(batch_next_states).to(self.device)  # 下一状态转张量上设备 (B,185)
            action = torch.Tensor(batch_actions).to(self.device)  # 动作转张量 (B,2)
            reward = torch.Tensor(batch_rewards).to(self.device).reshape(-1, 1)  # (B,)->(B,1)，对齐 Q 值形状（回放池返回的是一维）
            done = torch.Tensor(batch_dones).to(self.device).reshape(-1, 1)  # 终止标志 (B,)->(B,1)，对齐 Q 值形状

            # Obtain the estimated action from the next state by using the actor-target —— 用目标策略估计下一状态的动作
            next_action = self.actor_target(next_state)  # (B,2)；target 网络出动作，避免"追逐移动目标"的不稳定

            # Add noise to the action —— 目标策略平滑（TD3 关键技巧）
            noise = (  # 开始构造目标平滑噪声张量（跨行链式调用的开括号）
                torch.Tensor(batch_actions)  # 借 batch_actions 的形状造同形张量 (B,2)
                .data.normal_(0, policy_noise)  # 原地填入 N(0, σ=0.2)；.data 脱离计算图
                .to(self.device)  # 搬到设备
            )  # 噪声张量构造完毕，形状 (B,2)
            noise = noise.clamp(-noise_clip, noise_clip)  # 裁剪噪声到 ±0.5：平滑 critic 局部尖峰，防过高估
            next_action = (next_action + noise).clamp(-self.max_action, self.max_action)  # 加噪动作再裁回合法范围 (B,2)

            # Calculate the Q values from the critic-target network for the next state-action pair —— 目标 critic 双 Q 估值
            target_Q1, target_Q2 = self.critic_target(next_state, next_action)  # 各 (B,1)

            # Select the minimal Q value from the 2 calculated values —— 取小抗高估（clipped double Q）
            target_Q = torch.min(target_Q1, target_Q2)  # (B,1)；Q-learning 取 max 会系统性高估，取 min 偏保守可压制
            av_Q += torch.mean(target_Q)  # 累计均值（监控用）
            max_Q = max(max_Q, torch.max(target_Q))  # 刷新最大值（监控用）
            # Calculate the final Q value from the target network parameters by using Bellman equation —— 贝尔曼方程构造 TD 目标
            target_Q = reward + ((1 - done) * discount * target_Q).detach()  # y = r + γ·(1-done)·Q_min(s',a')；(B,1)；detach 使目标不参与梯度（固定回归靶）
            # 教学注：done=1（撞墙/到达目标）时后半项归零——终止后没有未来

            # Get the Q values of the basis networks with the current parameters —— 在线 critic 对当前 (s,a) 的估值
            current_Q1, current_Q2 = self.critic(state, action)  # 各 (B,1)

            # Calculate the loss between the current Q value and the target Q value —— critic 回归损失
            loss = F.mse_loss(current_Q1, target_Q) + F.mse_loss(current_Q2, target_Q)  # 双 Q 各自对同一目标做 MSE 后相加（两个头都回归 y）

            if self.use_max_bound:  # CNNTD3 特色：Q 值上界正则（默认关闭）
                max_bound = get_max_bound(  # 按物理极限（最大速度转向+直行+目标奖励）折算的回报上界 (B,1)
                    next_state,  # 下一状态（取 cos/sin/距离）
                    discount,  # 折扣因子
                    max_ang_vel,  # 最大角速度
                    max_lin_vel,  # 最大线速度
                    time_step,  # 单步时长
                    distance_norm,  # 距离归一化常数
                    goal_reward,  # 到达目标奖励
                    reward,  # 即时奖励
                    done,  # 终止标志
                    self.device,  # 计算设备
                )  # get_max_bound 调用结束，返回物理回报上界 (B,1)
                max_excess_Q1 = F.relu(current_Q1 - max_bound)  # Q1 超出上界的部分（没超则为 0）
                max_excess_Q2 = F.relu(current_Q2 - max_bound)  # Q2 超出上界的部分
                max_bound_loss = (max_excess_Q1**2).mean() + (max_excess_Q2**2).mean()  # 超出量的平方惩罚（只罚高估不罚低估）
                # Add loss for Q values exceeding maximum possible upper bound —— 把上界惩罚并入总损失
                loss += self.bound_weight * max_bound_loss  # 加权合并：MSE + 0.25*上界惩罚

            # Perform the gradient descent —— critic 梯度下降
            self.critic_optimizer.zero_grad()  # 清旧梯度
            loss.backward()  # 反向传播求梯度
            self.critic_optimizer.step()  # Adam 更新 critic 参数

            if it % policy_freq == 0:  # 策略延迟更新：每 2 轮才动一次 actor（让 critic 先收敛些，减小策略抖动）
                # Maximize the actor output value by performing gradient descent on negative Q values —— 最大化 actor 输出 Q 值
                # (essentially perform gradient ascent) —— 对 -Q 梯度下降 = 对 Q 梯度上升 = 确定性策略梯度 DPG
                actor_grad, _ = self.critic(state, self.actor(state))  # 重新前向：actor 新出动作 (B,2) 喂 critic，取 Q1 (B,1)（Q2 丢弃，_ 接住）
                actor_grad = -actor_grad.mean()  # 取负均值作损失：最小化它=最大化 Q
                self.actor_optimizer.zero_grad()  # 清 actor 梯度
                actor_grad.backward()  # 反传：梯度经 critic 动作流回传到 actor 参数
                self.actor_optimizer.step()  # Adam 更新 actor

                # Use soft update to update the actor-target network parameters by —— actor 目标网络软更新
                # infusing small amount of current parameters —— actor 目标网络软更新
                for param, target_param in zip(  # 遍历 actor 与 actor_target 的对应参数
                    self.actor.parameters(), self.actor_target.parameters()  # 逐参数配对
                ):  # for 循环体开始
                    target_param.data.copy_(  # 原地写入目标网络参数
                        tau * param.data + (1 - tau) * target_param.data  # 目标 ← 0.5% 新 + 99.5% 旧，缓慢跟随
                    )  # 该参数软更新完成
                # Use soft update to update the critic-target network parameters by infusing —— critic 目标网络软更新
                # small amount of current parameters —— critic 目标网络软更新（同公式）
                for param, target_param in zip(  # 遍历 critic 与 critic_target 的对应参数
                    self.critic.parameters(), self.critic_target.parameters()  # 逐参数配对
                ):  # for 循环体开始
                    target_param.data.copy_(  # 原地写入目标网络参数
                        tau * param.data + (1 - tau) * target_param.data  # 同样的指数滑动平均式更新
                    )  # 该参数软更新完成

            av_loss += loss  # 累计本轮损失（tensor，写曲线用）
        self.iter_count += 1  # train 调用次数 +1
        # Write new values for tensorboard —— 写 TensorBoard 曲线
        self.writer.add_scalar("train/loss", av_loss / iterations, self.iter_count)  # 平均 critic 损失
        self.writer.add_scalar("train/avg_Q", av_Q / iterations, self.iter_count)  # 平均目标 Q
        self.writer.add_scalar("train/max_Q", max_Q, self.iter_count)  # 最大目标 Q
        if self.save_every > 0 and self.iter_count % self.save_every == 0:  # 到达自动存档周期
            self.save(filename=self.model_name, directory=self.save_directory)  # 存 4 个网络权重

    # ===================== save：保存 4 个网络权重 =====================
    # 输入：filename 前缀、directory 目录；输出磁盘上 4 个 .pth 文件
    def save(self, filename, directory):  # 保存 4 个网络权重到磁盘
        """
        Saves the current model parameters to the specified directory.

        Args:
            filename (str): Base filename for saved files.
            directory (Path): Path to save the model files.
        """
        Path(directory).mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在不报错）
        torch.save(self.actor.state_dict(), "%s/%s_actor.pth" % (directory, filename))  # 存在线 actor 权重
        torch.save(  # 保存目标 actor 权重
            self.actor_target.state_dict(),  # 存目标 actor 权重
            "%s/%s_actor_target.pth" % (directory, filename),  # 文件名带 _actor_target 后缀
        )  # 目标 actor 存档完成
        torch.save(self.critic.state_dict(), "%s/%s_critic.pth" % (directory, filename))  # 存在线 critic 权重
        torch.save(  # 保存目标 critic 权重
            self.critic_target.state_dict(),  # 存目标 critic 权重
            "%s/%s_critic_target.pth" % (directory, filename),  # 文件名带 _critic_target 后缀
        )  # 目标 critic 存档完成

    # ===================== load：从磁盘恢复 4 个网络权重 =====================
    # 输入：filename 前缀、directory 目录；效果：4 个网络权重被覆盖为存档值
    def load(self, filename, directory):  # 从磁盘恢复 4 个网络权重
        """
        Loads model parameters from the specified directory.

        Args:
            filename (str): Base filename for saved files.
            directory (Path): Path to load the model files from.
        """
        self.actor.load_state_dict(  # 装入在线 actor 权重（跨行调用）
            torch.load("%s/%s_actor.pth" % (directory, filename))  # 读在线 actor 权重文件
        )  # 在线 actor 权重装入完毕
        self.actor_target.load_state_dict(  # 装入目标 actor 权重（跨行调用）
            torch.load("%s/%s_actor_target.pth" % (directory, filename))  # 读目标 actor 权重
        )  # 目标 actor 权重装入完毕
        self.critic.load_state_dict(  # 装入在线 critic 权重
            torch.load("%s/%s_critic.pth" % (directory, filename))  # 读在线 critic 权重
        )  # 在线 critic 权重装入完毕
        self.critic_target.load_state_dict(  # 装入目标 critic 权重（跨行调用）
            torch.load("%s/%s_critic_target.pth" % (directory, filename))  # 读目标 critic 权重
        )  # 目标 critic 权重装入完毕
        print(f"Loaded weights from: {directory}")  # 打印加载来源目录确认

    # ===================== prepare_state：ROS 原始数据 → 网络输入状态 =====================
    # 输入：一帧激光扫描 + 导航量 + 上一步动作；输出：(185 维归一化状态, 终止标志)
    # 训练/推理管线第一站：把物理量纲压到 O(1) 附近，网络才好学
    def prepare_state(self, latest_scan, distance, cos, sin, collision, goal, action):  # ROS 原始数据→归一化状态
        """
        Prepares the environment's raw sensor data and navigation variables into
        a format suitable for learning.

        Args:
            latest_scan (list or np.ndarray): Raw scan data (e.g., LiDAR).
            distance (float): Distance to goal.
            cos (float): Cosine of heading angle to goal.
            sin (float): Sine of heading angle to goal.
            collision (bool): Collision status (True if collided).
            goal (bool): Goal reached status.
            action (list or np.ndarray): Last action taken [lin_vel, ang_vel].

        Returns:
            (tuple):
                - state (list): Normalized and concatenated state vector.
                - terminal (int): Terminal flag (1 if collision or goal, else 0).
        """
        latest_scan = np.array(latest_scan)  # 列表转 np 数组，便于向量化处理 (180,)

        inf_mask = np.isinf(latest_scan)  # 找无穷远回波（激光没打到东西）的掩码
        latest_scan[inf_mask] = 7.0  # 无穷远截断为 7 米（传感器最大量级），避免 inf 毁掉网络
        latest_scan /= 7  # 除以 7 归一化到约 [0,1]

        # Normalize to [0, 1] range —— 各导航量归一化
        distance /= 10  # 距离除以 10（约 10 米量级）归一化
        lin_vel = action[0] * 2  # 上一步线速度仿射编码：×2
        ang_vel = (action[1] + 1) / 2  # 上一步角速度：[-1,1]→[0,1]
        state = latest_scan.tolist() + [distance, cos, sin] + [lin_vel, ang_vel]  # 拼接成 180+3+2=185 维状态列表（cos/sin 编码朝向角，避免 ±π 跳变）

        assert len(state) == self.state_dim  # 维度断言：与构造时 state_dim 一致才继续
        terminal = 1 if collision or goal else 0  # 终止标志：撞墙或到目标都算回合结束（done=1）

        return state, terminal  # 返回 (185 维状态, 终止标志)
