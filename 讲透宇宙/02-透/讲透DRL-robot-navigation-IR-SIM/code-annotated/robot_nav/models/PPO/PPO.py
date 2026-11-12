import torch  # PyTorch 主库：张量运算 + 自动微分，深度 RL 的底座
import torch.nn as nn  # 神经网络模块箱：Linear / Tanh / MSELoss 等层与损失
from torch.distributions import MultivariateNormal  # 多元正态分布：连续动作策略 π(a|s) 的采样与 log_prob
import numpy as np  # NumPy：环境侧数组处理（状态归一化、动作转 np 返回）
from torch.utils.tensorboard import SummaryWriter  # TensorBoard 写手：训练曲线（loss/价值）可视化
from pathlib import Path  # 路径对象：checkpoint 目录创建与默认路径
from numpy import inf  # 正无穷：初始化 max_state_value 的哨兵值


# RolloutBuffer：PPO 的轨迹缓冲区（on-policy 经验容器）。
# 职责：按时间顺序暂存 rollout（当前策略与环境交互采到的转移序列），
# 供 train() 做一次多轮（K-epoch）更新，用完必须 clear()。
# 与 off-policy replay buffer 的本质区别：数据必须由"当前策略"亲自采样（rollout=拿当前策略去环境里跑），
# 旧数据不能复用——这正是 PPO 属于 on-policy 算法的代码体现。
class RolloutBuffer:  # PPO 的轨迹缓冲区（on-policy 经验容器）
    """
    Buffer to store rollout data (transitions) for PPO training.

    Attributes:
        actions (list): Actions taken by the agent.
        states (list): States observed by the agent.
        logprobs (list): Log probabilities of the actions.
        rewards (list): Rewards received from the environment.
        state_values (list): Value estimates for the states.
        is_terminals (list): Flags indicating episode termination.
    """

    # 构造函数：初始化六个平行列表（同一时间步的数据靠下标对齐）
    def __init__(self):  # 初始化六个平行空列表
        """
        Initialize empty lists to store buffer elements.
        """
        self.actions = []  # 每步执行的动作（张量），下标 t 对应第 t 步
        self.states = []  # 每步观测到的状态，与 actions 按下标一一对应
        self.logprobs = []  # 每步动作在旧策略下的对数概率 log π_old(a|s)，PPO 算重要性权重的锚点
        self.rewards = []  # 每步环境返回的即时奖励 r_t
        self.state_values = []  # 每步 critic 的状态价值估计 V(s)（算优势的基线）
        self.is_terminals = []  # 每步是否 episode 结束（截断 Monte Carlo 回报递推用）

    # clear：原地清空六个列表。
    # PPO 每次更新后数据即作废（策略已改变，旧数据不再反映当前策略分布），这是 on-policy 铁律
    def clear(self):  # 原地清空全部经验
        """
        Clear all stored data from the buffer.
        """
        del self.actions[:]  # 原地清空动作列表（del lst[:] 不新建对象、保留引用）
        del self.states[:]  # 原地清空状态列表
        del self.logprobs[:]  # 原地清空对数概率列表
        del self.rewards[:]  # 原地清空奖励列表
        del self.state_values[:]  # 原地清空状态价值列表
        del self.is_terminals[:]  # 原地清空终止标志列表

    # add：向缓冲区追加一条转移 (s, a, r, done, s')。
    # 注意本实现是 Partial（部分实现）：只存 states/rewards/is_terminals 三项，
    # actions/logprobs/state_values 由 get_action() 采样时直接写入 buffer（见下方 get_action）；
    # next_state 始终未存——因为这份 PPO 用 Monte Carlo 回报（整条轨迹自己算折扣和），不需要 bootstrap 用的 s'。
    def add(self, state, action, reward, terminal, next_state):  # 追加一条转移（部分实现：仅存 s/r/done）
        """
        Add a transition to the buffer. (Partial implementation.)

        Args:
            state (list or np.array): The current observed state.
            action (list or np.array): The action taken.
            reward (float): The reward received after taking the action.
            terminal (bool): Whether the episode terminated.
            next_state (list or np.array): The resulting state after taking the action.
        """
        self.states.append(state)  # 存状态 s_t（由外部环境循环调用）
        self.rewards.append(reward)  # 存即时奖励 r_t
        self.is_terminals.append(terminal)  # 存终止标志（True=episode 边界，回报递推在此清零）


# ActorCritic：PPO 的"演员-评论家"网络（两个子网打包进一个 nn.Module）。
# Actor（演员）= 策略网络：输入状态 s，输出高斯动作分布的均值，(state_dim,) → (action_dim,)
# Critic（评论家）= 价值网络：输入 s，输出标量 V(s)（这个状态有多好），(state_dim,) → (1,)
# 二者分工：actor 靠 critic 给出的优势信号改进动作，critic 靠真实回报回归校正估值
class ActorCritic(nn.Module):  # 演员-评论家联合网络
    """
    Actor-Critic neural network model for PPO.

    Attributes:
        actor (nn.Sequential): Policy network (actor) to output action mean.
        critic (nn.Sequential): Value network (critic) to predict state values.
        action_var (Tensor): Diagonal covariance matrix for action distribution.
        device (str): Device used for computation ('cpu' or 'cuda').
        max_action (float): Clipping range for action values.
    """

    # 构造函数：搭建 actor / critic 两个 MLP，并初始化各维同方差的高斯探索噪声。
    # 输入：state_dim 状态维数、action_dim 动作维数、action_std_init 初始探索标准差、max_action 动作幅值上界、device
    def __init__(self, state_dim, action_dim, action_std_init, max_action, device):  # 建 actor/critic 两个子网并初始化方差
        """
        Initialize the Actor and Critic networks.

        Args:
            state_dim (int): Dimension of the input state.
            action_dim (int): Dimension of the action space.
            action_std_init (float): Initial standard deviation of the action distribution.
            max_action (float): Maximum value allowed for an action (clipping range).
            device (str): Device to run the model on.
        """
        super(ActorCritic, self).__init__()  # 调用 nn.Module 父类初始化（注册子模块与参数的必要步骤）

        self.device = device  # 记录计算设备（'cpu'/'cuda'），新建张量时统一 .to(device)
        self.max_action = max_action  # 动作裁剪边界：动作元素限制在 ±max_action 内

        self.action_dim = action_dim  # 动作维数（本机器人=2：线速度 + 角速度）
        self.action_var = torch.full(  # 构造探索方差向量（注意存的是方差 σ²，不是标准差 σ）
            (action_dim,), action_std_init * action_std_init  # 形状 (action_dim,)，每一维 = std²（各维独立同方差）
        ).to(self.device)  # 搬到计算设备
        # actor  # 原注释：策略网络定义开始
        self.actor = nn.Sequential(  # Sequential 顺序容器：依次堆叠下列 7 个模块
            nn.Linear(state_dim, 400),  # 全连接层：state_dim → 400（升维提特征）
            nn.Tanh(),  # 双曲正切激活，输出压到 (-1,1)，与有界动作天然匹配
            nn.Linear(400, 300),  # 全连接层：400 → 300（逐层收窄）
            nn.Tanh(),  # 激活
            nn.Linear(300, action_dim),  # 输出层：300 → action_dim，输出高斯分布的均值 μ(s)
            nn.Tanh(),  # 均值再过 Tanh：把动作均值天然约束在 (-1,1)（配合外层 max_action 缩放）
        )  # actor 网络堆叠收尾（7 模块）
        # critic  # 原注释：价值网络定义开始
        self.critic = nn.Sequential(  # 顺序容器
            nn.Linear(state_dim, 400),  # 全连接层：state_dim → 400（与 actor 同构）
            nn.Tanh(),  # 激活
            nn.Linear(400, 300),  # 全连接层：400 → 300（逐层收窄）
            nn.Tanh(),  # 激活
            nn.Linear(300, 1),  # 输出层：300 → 1，即状态价值估计 V(s)（标量）
        )  # critic 网络堆叠收尾（5 模块）

    # set_action_std：整体替换探索噪声强度（内部转成方差 σ² 存储）
    def set_action_std(self, new_action_std):  # 更新探索方差（转 σ² 存储）
        """
        Set a new standard deviation for the action distribution.

        Args:
            new_action_std (float): New standard deviation.
        """
        self.action_var = torch.full(  # 用新 std 重建方差向量
            (self.action_dim,), new_action_std * new_action_std  # (action_dim,)，每维 = 新 std²
        ).to(self.device)  # 搬到设备

    # forward：刻意不实现。本类只用 act()/evaluate() 两个显式接口，
    # 留空 nn.Module 约定的 forward() 是为了防止误用（直接调用会立刻报错提醒）
    def forward(self):  # 刻意禁用的默认前向
        """
        Forward method is not implemented, as it's unused directly.

        Raises:
            NotImplementedError: Always raised when called.
        """
        raise NotImplementedError  # 主动抛错：提示调用方应使用 act/evaluate

    # act：环境交互时的动作生成（推理路径，无梯度）。
    # 输入：单个状态 state，shape (state_dim,)；sample=True 训练期随机采样 / False 评估期取均值
    # 输出：三元组 (action, action_logprob, state_val)，全部已 detach（存进 buffer 当"数值"用，不进计算图）
    # 流程位置：rollout 采集阶段，由 PPO.get_action() 调用
    def act(self, state, sample):  # 交互期动作生成（无梯度路径）
        """
        Compute an action, its log probability, and the state value.

        Args:
            state (Tensor): Input state tensor.
            sample (bool): Whether to sample from the action distribution or use mean.

        Returns:
            (Tuple[Tensor, Tensor, Tensor]): Sampled (or mean) action, log probability, and state value.
        """
        action_mean = self.actor(state)  # 策略网络前向：state (state_dim,) → 均值 μ (action_dim,)
        cov_mat = torch.diag(self.action_var).unsqueeze(dim=0)  # 方差向量→对角协方差矩阵：(action_dim,) → (1, action_dim, action_dim)
        dist = MultivariateNormal(action_mean, cov_mat)  # 构造对角高斯策略 π(a|s) = N(μ(s), diag(σ²))（连续动作的标准参数化）

        if sample:  # 训练期：从分布随机采样（带探索噪声，"试错"的来源）
            action = torch.clip(  # 对采样结果做幅值裁剪
                dist.sample(), min=-self.max_action, max=self.max_action  # 限制到 ±max_action（机器人速度物理界）
            )  # clip 收尾：动作限定在界内
        else:  # 评估/部署期：直接取分布均值（确定性动作，无噪声，考察策略真实水平）
            action = dist.mean  # 评估期：直接取分布均值（确定性动作）
        action_logprob = dist.log_prob(action)  # 该动作的对数概率 log π(a|s)（标量）——更新时算重要性比率的分母
        state_val = self.critic(state)  # critic 现场估值 V(s)，shape (1,)

        return action.detach(), action_logprob.detach(), state_val.detach()  # 全部 detach：经验只需数值，切断梯度追踪

    # evaluate：训练阶段用"当前策略"重估"旧动作"（带梯度的前向）。
    # 输入：批量 state (B, state_dim)、旧动作 action (B, action_dim)
    # 输出：三元组 (log π_θ(a|s), V_θ(s), 熵 H)——与 act() 的本质区别是不断开计算图，梯度可流回 actor/critic
    # 流程位置：train() 的 K-epoch 循环内，每个 epoch 都重算一遍（新参数 → 新估值）
    def evaluate(self, state, action):  # 训练期重估旧动作（有梯度路径）
        """
        Evaluate action log probabilities, entropy, and state values for given states and actions.

        Args:
            state (Tensor): Batch of states.
            action (Tensor): Batch of actions.

        Returns:
            (Tuple[Tensor, Tensor, Tensor]): Action log probabilities, state values, and distribution entropy.
        """
        action_mean = self.actor(state)  # 新参数下重算均值：state (B, state_dim) → (B, action_dim)

        action_var = self.action_var.expand_as(action_mean)  # 方差向量广播到批量：→ (B, action_dim)
        cov_mat = torch.diag_embed(action_var).to(self.device)  # 每个样本一份对角协方差：→ (B, action_dim, action_dim)
        dist = MultivariateNormal(action_mean, cov_mat)  # 批量构造高斯分布（逐行是各样本的策略分布）

        # For Single Action Environments.  # 原注释：一维动作空间的特殊处理
        if self.action_dim == 1:  # 动作维数为 1 时
            action = action.reshape(-1, self.action_dim)  # 强制拉成 (B, 1) 二维，防 MultivariateNormal 因形状歧义报错

        action_logprobs = dist.log_prob(action)  # 新策略下旧动作的 log π_θ(a|s)：(B,)——与 old_logprobs 相减即得 log(重要性比率)
        dist_entropy = dist.entropy()  # 分布熵 H(π(·|s))：衡量策略随机程度，(B,)——熵正则项的原料
        state_values = self.critic(state)  # 新 critic 的 V_θ(s)：(B, 1)——价值回归项的原料

        return action_logprobs, state_values, dist_entropy  # 三件套返回，train() 用来拼总 loss


# PPO：近端策略优化主控制器（外层训练循环的"大脑"）。
# 核心思想：clip 代理目标限制每次策略更新步长（信赖域思想的简化实现），防止一步更新把策略改崩。
# 数据流：get_action 采集 rollout → train() 算 MC 回报与优势 → K-epoch clip 更新 → 同步 policy_old → 清 buffer → 探索退火。
# 本实现三特点（与教程标准版略有出入，注释中如实指出）：MC 回报（非 GAE）、整批更新（非 minibatch）、固定 std 探索退火（非学习 std）。
class PPO:  # PPO 主控制器（外层训练大脑）
    """
    Proximal Policy Optimization (PPO) implementation for continuous control tasks.

    Attributes:
        max_action (float): Maximum action value.
        action_std (float): Standard deviation of the action distribution.
        action_std_decay_rate (float): Rate at which to decay action standard deviation.
        min_action_std (float): Minimum allowed action standard deviation.
        state_dim (int): Dimension of the state space.
        gamma (float): Discount factor for future rewards.
        eps_clip (float): Clipping range for policy updates.
        device (str): Device for model computation ('cpu' or 'cuda').
        save_every (int): Interval (in iterations) for saving model checkpoints.
        model_name (str): Name used when saving/loading model.
        save_directory (Path): Directory to save model checkpoints.
        iter_count (int): Number of training iterations completed.
        buffer (RolloutBuffer): Buffer to store trajectories.
        policy (ActorCritic): Current actor-critic network.
        optimizer (torch.optim.Optimizer): Optimizer for actor and critic.
        policy_old (ActorCritic): Old actor-critic network for computing PPO updates.
        MseLoss (nn.Module): Mean squared error loss function.
        writer (SummaryWriter): TensorBoard summary writer.
    """

    # 构造函数：建网络 / 优化器 / 旧策略副本 / 日志器。
    # 要点：actor 与 critic 分开学率（critic 更快，价值回归是更"好学"的任务）；
    # policy_old 是采数据专用副本——PPO 的重要性比率 π_θ/π_old 需要"数据来源策略"的锚点
    def __init__(  # 多行签名开始
        self,  # 实例自身
        state_dim,  # 状态空间维数（雷达分箱数 + 5 个导航/速度特征）
        action_dim,  # 动作空间维数（2：线速度 / 角速度）
        max_action,  # 动作幅值上界
        lr_actor=0.0003,  # actor 学习率（默认 3e-4）
        lr_critic=0.001,  # critic 学习率（默认 1e-3，比 actor 快 3 倍多：价值函数要先行收敛才能指导策略）
        gamma=0.99,  # 折扣因子 γ：未来奖励每步打 99 折（越接近 1 越"有远见"，但训练越不稳定）
        eps_clip=0.2,  # PPO 裁剪幅度 ε=0.2（论文推荐值：把重要性比率限制在 [1-ε, 1+ε]）
        action_std_init=0.6,  # 初始探索标准差（偏大 → 前期大胆探索）
        action_std_decay_rate=0.015,  # 每次更新后 std 的线性衰减量
        min_action_std=0.1,  # std 衰减下限（保底随机性，防策略过早"僵化"收敛到次优）
        device="cpu",  # 计算设备
        save_every=10,  # 每 10 次 train() 存一次 checkpoint（0=关闭）
        load_model=False,  # 是否从磁盘加载预训练权重（断点续训）
        save_directory=Path("robot_nav/models/PPO/checkpoint"),  # checkpoint 保存目录
        model_name="PPO",  # 模型名（存/读文件与 TensorBoard 注释标识）
        load_directory=Path("robot_nav/models/PPO/checkpoint"),  # 加载目录
    ):  # 构造函数签名收尾
        self.max_action = max_action  # 存动作上界
        self.action_std = action_std_init  # 当前探索 std（训练中会逐步衰减）
        self.action_std_decay_rate = action_std_decay_rate  # std 每次衰减量
        self.min_action_std = min_action_std  # std 下限
        self.state_dim = state_dim  # 状态维数（prepare_state 里做维度对账用）
        self.gamma = gamma  # 折扣因子 γ
        self.eps_clip = eps_clip  # 裁剪幅度 ε
        self.device = device  # 设备
        self.save_every = save_every  # 保存间隔
        self.model_name = model_name  # 模型名
        self.save_directory = save_directory  # 保存目录
        self.iter_count = 0  # 更新轮次计数器（TensorBoard x 轴与保存节拍）

        self.buffer = RolloutBuffer()  # 建 on-policy 轨迹缓冲区

        self.policy = ActorCritic(  # 待训练的当前策略网络 π_θ（train() 更新的就是它）
            state_dim, action_dim, action_std_init, self.max_action, self.device  # 五个构造参数
        ).to(device)  # 搬到设备
        self.optimizer = torch.optim.Adam(  # 一个 Adam 同时管 actor+critic，但分组设不同学习率
            [  # 参数组列表
                {"params": self.policy.actor.parameters(), "lr": lr_actor},  # 第 1 组：actor 参数 + actor 学率
                {"params": self.policy.critic.parameters(), "lr": lr_critic},  # 第 2 组：critic 参数 + critic 学率
            ]  # Adam 参数组列表收尾
        )  # 分组 Adam 构造收尾

        self.policy_old = ActorCritic(  # 旧策略 π_old 副本：专职采数据 / 评估期推理（参数不直接被优化器更新）
            state_dim, action_dim, action_std_init, self.max_action, self.device  # 与 policy 完全同构
        ).to(device)  # 搬到设备
        self.policy_old.load_state_dict(self.policy.state_dict())  # 初始硬同步（此刻两者相同，比率恒为 1）
        if load_model:  # 断点续训开关打开
            self.load(filename=model_name, directory=load_directory)  # 从磁盘恢复权重到 policy_old 与 policy

        self.MseLoss = nn.MSELoss()  # critic 价值回归损失：MSE(V(s), G_t)
        self.writer = SummaryWriter(comment=model_name)  # TensorBoard 写手实例

    # set_action_std：把新 std 同时写入当前策略与旧策略。
    # 为什么两边都要写：保持两者探索幅度一致，重要性比率 π_θ/π_old 才不被 std 差异污染
    def set_action_std(self, new_action_std):  # 把新 std 写入两个网络
        """
        Set a new standard deviation for the action distribution.

        Args:
            new_action_std (float): New standard deviation value.
        """
        self.action_std = new_action_std  # 更新记录值
        self.policy.set_action_std(new_action_std)  # 写入当前策略的方差
        self.policy_old.set_action_std(new_action_std)  # 写入旧策略的方差

    # decay_action_std：探索退火——每次 train() 后把 std 线性减一点，直到下限。
    # 为什么：训练前期要大噪声广撒网探索，后期策略趋好应逐渐收敛到确定性利用（探索-利用权衡的工程化）
    def decay_action_std(self, action_std_decay_rate, min_action_std):  # 探索退火一步（线性减 std 至下限）
        """
        Decay the action standard deviation by a fixed rate, down to a minimum threshold.

        Args:
            action_std_decay_rate (float): Amount to reduce standard deviation by.
            min_action_std (float): Minimum value for standard deviation.
        """
        print(  # 打印分隔线（控制台训练日志的分节）
            "--------------------------------------------------------------------------------------------"  # 100 字符横线
        )  # 分隔线打印收尾
        self.action_std = self.action_std - action_std_decay_rate  # std 线性递减一步
        self.action_std = round(self.action_std, 4)  # 四舍五入 4 位小数（防浮点误差累积）
        if self.action_std <= min_action_std:  # 已跌破下限
            self.action_std = min_action_std  # 钉死在下限
            print(  # 打印触底提示
                "setting actor output action_std to min_action_std : ", self.action_std  # 提示文本 + 当前 std
            )  # 触底提示打印收尾
        else:  # 尚未触底
            print("setting actor output action_std to : ", self.action_std)  # 打印新 std
        self.set_action_std(self.action_std)  # 把新 std 写入两个网络
        print(  # 再打一条分隔线收尾
            "--------------------------------------------------------------------------------------------"  # 100 字符横线
        )  # 尾部分隔线打印收尾

    # get_action：对外动作接口，环境循环每步调用。
    # add_noise=True（训练）：从 π_old 随机采样并把经验存入 buffer；False（评估）：取确定性均值且不污染 buffer
    # 返回 np.ndarray（flatten），供 ROS / 仿真器直接消费
    def get_action(self, state, add_noise):  # 对外动作接口（环境每步调用）
        """
        Sample an action using the current policy (optionally with noise), and store in buffer if noise is added.

        Args:
            state (array_like): Input state for the policy.
            add_noise (bool): Whether to sample from the distribution (True) or use the deterministic mean (False).

        Returns:
            (np.ndarray): Sampled action.
        """

        with torch.no_grad():  # 采样阶段不需要梯度（省显存省计算）
            state = torch.FloatTensor(state).to(self.device)  # np/list → 浮点张量并上设备，shape (state_dim,)
            action, action_logprob, state_val = self.policy_old.act(state, add_noise)  # 用旧策略生成动作三件套（on-policy：数据永远来自 π_old）

        if add_noise:  # 只有训练采样时才缓存经验（评估动作不入 buffer）
            # self.buffer.states.append(state)  # 原注释（已弃用写法）：状态改由 buffer.add() 统一存
            self.buffer.actions.append(action)  # 存动作
            self.buffer.logprobs.append(action_logprob)  # 存 log π_old(a|s)——PPO 更新时重要性比率的分母锚点
            self.buffer.state_values.append(state_val)  # 存旧 critic 的 V(s)——算优势的基线

        return action.detach().cpu().numpy().flatten()  # 张量→CPU numpy→拉平成一维（去掉多余维度）

    # train：PPO 核心更新入口，每次喂一整段 rollout。
    # 四步流水线：① 倒序递推算 MC 回报 G_t → ② 归一化 + 算优势 A_t → ③ K-epoch clip 代理目标更新 → ④ 同步旧策略 + 清 buffer + 探索退火
    # 参数 replay_buffer / batch_size 是与 SAC 统一训练接口的占位：本实现整批使用、不抽样（batch_size 未用）
    def train(self, replay_buffer, iterations, batch_size):  # 核心更新入口（四步流水线）
        """
        Train the policy and value function using PPO loss based on the stored rollout buffer.

        Args:
            replay_buffer (object): Placeholder for compatibility (not used).
            iterations (int): Number of epochs to optimize the policy per update.
            batch_size (int): Batch size (not used; training uses the whole buffer).
        """
        # Monte Carlo estimate of returns  # 原注释：Monte Carlo 法估计回报
        rewards = []  # 回报列表（倒序递推、头插法正序存）
        discounted_reward = 0  # 滚动的折扣累积回报 G_t
        for reward, is_terminal in zip(  # 从后往前扫整段轨迹
            reversed(self.buffer.rewards), reversed(self.buffer.is_terminals)  # 奖励与终止标志均倒序
        ):  # zip 倒序遍历收尾
            if is_terminal:  # 碰到 episode 边界
                discounted_reward = 0  # 回报清零：不同 episode 的回报不跨界累积（bootstrap 截断点）
            discounted_reward = reward + (self.gamma * discounted_reward)  # 递推式：G_t = r_t + γ·G_{t+1}（MC 法无偏但方差高——见下方优势处的偏差-方差讨论）
            rewards.insert(0, discounted_reward)  # 头插：倒着算、正着存，rewards[t] 即 G_t

        # Normalizing the rewards  # 原注释：回报归一化
        rewards = torch.tensor(rewards, dtype=torch.float32).to(self.device)  # list → 张量 (N,)
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-7)  # 标准化到 0 均值 1 方差（+1e-7 防除零）。注：标准 PPO 常归一化的是优势 A，这里归一化回报 G，效果类似——都为稳定数值量纲、加速收敛

        # convert list to tensor  # 原注释：列表转批量张量
        assert len(self.buffer.actions) == len(self.buffer.states)  # 断言动作数=状态数（buffer 完整性自检）

        states = [torch.tensor(st, dtype=torch.float32) for st in self.buffer.states]  # 逐条状态先转张量
        old_states = torch.squeeze(torch.stack(states, dim=0)).detach().to(self.device)  # 堆叠 → (N, state_dim)，squeeze 去多余维度；detach 后整批当作旧策略的"数据常量"
        old_actions = (  # 旧动作批
            torch.squeeze(torch.stack(self.buffer.actions, dim=0))  # 堆叠 → (N, action_dim)
            .detach()  # 断梯度
            .to(self.device)  # 上设备
        )  # old_actions 张量构造收尾
        old_logprobs = (  # 旧策略 log 概率批
            torch.squeeze(torch.stack(self.buffer.logprobs, dim=0))  # 堆叠 → (N,)
            .detach()  # 断梯度——重要性比率的分母必须冻结，梯度只流向新策略
            .to(self.device)  # 上设备
        )  # old_logprobs 张量构造收尾
        old_state_values = (  # 旧 critic 价值批
            torch.squeeze(torch.stack(self.buffer.state_values, dim=0))  # 堆叠 → (N,)
            .detach()  # 断梯度
            .to(self.device)  # 上设备
        )  # old_state_values 张量构造收尾

        # calculate advantages  # 原注释：计算优势
        advantages = rewards.detach() - old_state_values.detach()  # 优势 A_t = G_t − V_old(s_t)：这步动作比"平均水平"好多少；(N,)。教学注：本实现用 MC 回报减基线——无偏但方差高；经典 GAE(λ) 则用 TD 残差指数加权 δ_t + λδ_{t+1} + …，以少量偏差换显著降方差（λ=0 退化为高偏差低方差的 TD，λ=1 等价本式 MC），此处是"偏差-方差权衡"光谱上的 λ=1 端点

        av_state_values = 0  # 平均状态价值累积器（TensorBoard 曲线用）
        max_state_value = -inf  # 最大状态价值（初值负无穷哨兵）
        av_loss = 0  # 平均 loss 累积器
        # Optimize policy for K epochs  # 原注释：同一批数据跑 K 轮优化。教学注：这正是 PPO 的"安全数据复用"——clip 保证策略偏离旧策略不超 ε，使旧数据在 K 轮内仍近似有效；K 轮后必须丢弃（下方 clear），这是与 off-policy 的分水岭
        for _ in range(iterations):  # K-epoch 循环（整批更新，无 minibatch 切分）
            # Evaluating old actions and values  # 原注释：用当前策略重估旧动作
            logprobs, state_values, dist_entropy = self.policy.evaluate(  # 新参数前向：log π_θ(a|s)、V_θ(s)、H(π_θ)
                old_states, old_actions  # 输入旧数据 (N, state_dim) / (N, action_dim)
            )  # evaluate 调用收尾

            # match state_values tensor dimensions with rewards tensor  # 原注释：对齐维度
            state_values = torch.squeeze(state_values)  # (N,1) → (N,)，与归一化回报对齐
            av_state_values += torch.mean(state_values)  # 累积本轮均值（标量）
            max_state_value = max(max_state_value, max(state_values))  # 更新历史最大值
            # Finding the ratio (pi_theta / pi_theta__old)  # 原注释：重要性采样比率
            ratios = torch.exp(logprobs - old_logprobs.detach())  # ratio = exp(log π_θ − log π_old) = π_θ(a|s)/π_old(a|s)，(N,)——同一动作在新旧策略下的概率倍数，>1 表示新策略更倾向选它

            # Finding Surrogate Loss  # 原注释：代理损失两支
            surr1 = ratios * advantages  # 未裁剪支：ratio·A，即标准重要性加权策略梯度目标
            surr2 = (  # 裁剪支：把 ratio 钉死在 [1−ε, 1+ε] 再乘优势
                torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages  # clamp 后乘优势，(N,)
            )  # 裁剪支括号收尾

            # final loss of clipped objective PPO  # 原注释：三项之和的最终 loss
            loss = (  # 逐样本 loss 向量 (N,)
                -torch.min(surr1, surr2)  # ① clip 代理项取负（最大化→最小化）。min 是信赖域思想的化身：策略把 ratio 推出界后该项梯度自动归零，单步更新幅度被硬性限住，防止策略崩溃
                + 0.5 * self.MseLoss(state_values, rewards)  # ② critic 回归：0.5·MSE(V_θ(s), G_t)，让价值网络拟合真实回报（提供下一轮更准的基线）
                - 0.01 * dist_entropy  # ③ 熵正则取负：loss 减熵 → 鼓励高熵（保持探索、防过早收敛到确定性次优）；0.01 是探索-利用的权衡系数
            )  # 三项 loss 括号收尾

            # take gradient step  # 原注释：走一步优化
            self.optimizer.zero_grad()  # 清空上轮梯度（PyTorch 梯度默认累加，必须手动清零）
            loss.mean().backward()  # 向量 loss 取均值后反向传播（一次回传同时更新 actor+critic 两组参数）
            self.optimizer.step()  # Adam 步进
            av_loss += loss.mean()  # 累积本轮标量 loss

        # Copy new weights into old policy  # 原注释：新权重同步给旧策略
        self.policy_old.load_state_dict(self.policy.state_dict())  # θ_old ← θ：更新完毕立即同步，下一轮 ratio 重新从 1 出发（π_old 永远是"采这批数据时"的策略）
        # clear buffer  # 原注释：清空缓冲区
        self.buffer.clear()  # on-policy 铁律：旧数据随旧策略一起作废，绝不复用
        self.decay_action_std(self.action_std_decay_rate, self.min_action_std)  # 探索退火一步（随后打日志）
        self.iter_count += 1  # 更新轮次 +1
        # Write new values for tensorboard  # 原注释：写 TensorBoard
        self.writer.add_scalar("train/loss", av_loss / iterations, self.iter_count)  # 本轮平均 loss 曲线
        self.writer.add_scalar(  # 本轮平均价值曲线
            "train/avg_value", av_state_values / iterations, self.iter_count  # tag / 值 / x 轴步号
        )  # 平均价值曲线写入收尾
        self.writer.add_scalar("train/max_value", max_state_value, self.iter_count)  # 本轮最大价值曲线
        if self.save_every > 0 and self.iter_count % self.save_every == 0:  # 到达保存节拍
            self.save(filename=self.model_name, directory=self.save_directory)  # 存 checkpoint

    # prepare_state：传感器原始数据 → 策略可吃的归一化状态向量。
    # 输入：雷达扫描序列、目标距离与方向角 cos/sin、碰撞/到达标志、上一步动作
    # 输出：(长度 state_dim 的 list, terminal 0/1)；与 SAC 版逐字相同——两算法共享同一套环境状态编码
    def prepare_state(self, latest_scan, distance, cos, sin, collision, goal, action):  # 传感器原始数据→归一化状态向量
        """
        Convert raw sensor and navigation data into a normalized state vector for the policy.

        Args:
            latest_scan (list[float]): LIDAR scan data.
            distance (float): Distance to the goal.
            cos (float): Cosine of angle to the goal.
            sin (float): Sine of angle to the goal.
            collision (bool): Whether the robot has collided.
            goal (bool): Whether the robot has reached the goal.
            action (tuple[float, float]): Last action taken (linear and angular velocities).

        Returns:
            (tuple[list[float], int]): Processed state vector and terminal flag (1 if terminal, else 0).
        """
        latest_scan = np.array(latest_scan)  # 雷达数据转 np 数组（便于布尔掩码与切片）

        inf_mask = np.isinf(latest_scan)  # 找出"无回波"的 inf 读数（测距超出雷达量程）
        latest_scan[inf_mask] = 7.0  # inf 统一替换为 7.0m（=有效最远距离，也是下文 /7 归一化的基准）

        max_bins = self.state_dim - 5  # 雷达分箱数：总维度减去 5 个导航/速度特征（距离、cos、sin、线速、角速）
        bin_size = int(np.ceil(len(latest_scan) / max_bins))  # 每箱原始射线数（向上取整，保证最后一段也覆盖）

        # Initialize the list to store the minimum values of each bin  # 原注释：各箱最小值列表
        min_values = []  # 装每箱"最近障碍距离"

        # Loop through the data and create bins  # 原注释：分箱循环
        for i in range(0, len(latest_scan), bin_size):  # 按箱宽步进遍历雷达射线
            # Get the current bin  # 原注释：取当前箱
            bin = latest_scan[i : i + min(bin_size, len(latest_scan) - i)]  # 切出第 i 箱（末箱可能不足整箱宽）
            # Find the minimum value in the current bin and append it to the min_values list  # 原注释：取箱内最小值
            min_values.append(min(bin) / 7)  # 箱内最近障碍距离 /7 → 归一化 [0,1]（取 min=最保守安全假设：箱内任何一个障碍都算数）

        # Normalize to [0, 1] range  # 原注释：全状态归一化到 [0,1]
        distance /= 10  # 目标距离 /10（10m 量程）
        lin_vel = action[0] * 2  # 上一步线速度特征映射
        ang_vel = (action[1] + 1) / 2  # 上一步角速度 (-1,1) → (0,1)
        state = min_values + [distance, cos, sin] + [lin_vel, ang_vel]  # 拼完整状态：分箱雷达 + 3 导航特征 + 2 速度特征

        assert len(state) == self.state_dim  # 维度断言（分箱数算错在此立刻拦截）
        terminal = 1 if collision or goal else 0  # 碰撞或到达目标即终止

        return state, terminal  # 返回 (状态向量, 终止标志)

    # save：存旧策略权重。
    # 为什么存 policy_old 而非 policy：训练后两者已同步，而评估/续训都从 policy_old 出发（act 用的就是它）
    def save(self, filename, directory):  # 存旧策略权重到磁盘
        """
        Save the current policy model to the specified directory.

        Args:
            filename (str): Base name of the model file.
            directory (Path): Directory to save the model to.
        """
        Path(directory).mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在不报错）
        torch.save(  # 序列化 state_dict 落盘
            self.policy_old.state_dict(), "%s/%s_policy.pth" % (directory, filename)  # 旧策略参数 → {dir}/{name}_policy.pth
        )  # torch.save 收尾

    # load：从 checkpoint 恢复权重。
    # policy_old 与 policy 加载同一份权重：保证采数据策略与待训练策略一致（ratio 从 1 重新出发）
    def load(self, filename, directory):  # 从磁盘恢复权重（两网络对齐）
        """
        Load the policy model from a saved checkpoint.

        Args:
            filename (str): Base name of the model file.
            directory (Path): Directory to load the model from.
        """
        self.policy_old.load_state_dict(  # 恢复旧策略
            torch.load(  # 读盘
                "%s/%s_policy.pth" % (directory, filename),  # 文件路径
                map_location=lambda storage, loc: storage,  # 张量留在其原生设备（跨 CPU/GPU 加载友好）
            )  # torch.load 内层括号收尾（policy_old）
        )  # policy_old 加载收尾
        self.policy.load_state_dict(  # 同一份权重恢复给当前策略（两者对齐）
            torch.load(  # 再次读盘
                "%s/%s_policy.pth" % (directory, filename),  # 同一路径
                map_location=lambda storage, loc: storage,  # 同样的设备映射策略
            )  # torch.load 内层括号收尾（policy）
        )  # policy 加载收尾
        print(f"Loaded weights from: {directory}")  # 打印加载来源确认
