from pathlib import Path  # 导入 Path：跨平台路径对象，用于存档目录与文件名拼接

import numpy as np  # 导入 numpy：环境侧数组运算与探索噪声采样
import torch  # 导入 PyTorch 主库：张量运算 + autograd 自动求导
import torch.nn as nn  # 导入神经网络模块：Linear/Conv1d/LSTM/GRU 等带参数层
import torch.nn.functional as F  # 导入函数式接口：leaky_relu/mse_loss 等无参数算子
from numpy import inf  # 导入正无穷：作 max_Q 统计的初始最小值
from torch.utils.tensorboard import SummaryWriter  # 导入 TensorBoard 写入器：记录训练曲线


# ===================== 类：Actor（演员 / 循环卷积策略网络） =====================
# 职责：输入"最近 history_len(默认10) 帧状态序列"，输出窗口末端的连续动作；
#       与 CNNTD3 的差别 = 多了一层 RNN（GRU/LSTM/RNN 三选一），用历史记忆弥补部分可观测（POMDP）。
# 输入输出：s (B, H, 185)（训练批）或单条 (H, 185)（推理，内部补 batch 维）；输出 a (B, 2)∈(-1,1)。
# 算法位置：确定性策略（TD3 家族），训练时朝 critic 的 Q 梯度上升方向更新。
class Actor(nn.Module):  # Actor：循环卷积确定性策略网络（演员）
    """
    Actor network that outputs continuous actions for a given state input.

    Architecture:
        - Processes 1D laser scan inputs through 3 convolutional layers.
        - Embeds goal and previous action inputs using fully connected layers.
        - Combines all features and passes them through an RNN (GRU, LSTM, or RNN).
        - Outputs action values via a fully connected feedforward head with Tanh activation.

    Parameters
    ----------
    action_dim : int
        Dimensionality of the action space.
    rnn : str, optional
        Type of RNN layer to use ("lstm", "gru", or "rnn").
    """

    # ===================== __init__：搭建 Actor 的层 =====================
    # 四段式：3 层卷积（逐帧激光特征）+ 2 个嵌入层 + RNN（跨时间聚合）+ 3 层 MLP（出动作）
    def __init__(self, action_dim, rnn="gru"):  # action_dim 动作维数（本仓 2）；rnn 选循环层类型，默认 GRU
        super(Actor, self).__init__()  # 注册 nn.Module 机制
        assert rnn in ["lstm", "gru", "rnn"], "Unsupported rnn type"  # 防御：rnn 类型必须是三者之一

        self.cnn1 = nn.Conv1d(1, 4, kernel_size=8, stride=4)  # 卷积层1：1→4 通道、核宽8/步幅4；单帧 (·,1,180)->(·,4,44)
        self.cnn2 = nn.Conv1d(4, 8, kernel_size=8, stride=4)  # 卷积层2：4→8 通道；(·,4,44)->(·,8,10)
        self.cnn3 = nn.Conv1d(8, 4, kernel_size=4, stride=2)  # 卷积层3：8→4 通道；(·,8,10)->(·,4,4)

        self.goal_embed = nn.Linear(3, 10)  # 目标嵌入：3 维[距离,cos,sin]→10 维
        self.action_embed = nn.Linear(2, 10)  # 上一步动作嵌入：2 维[线速,角速]→10 维

        # ---- RNN 段：三选一，输入/隐藏都是 36 维（与拼接特征同宽） ----
        if rnn == "lstm":  # 选 LSTM（长短期记忆，带遗忘门的循环网络）
            self.rnn = nn.LSTM(  # 构造 LSTM 层
                input_size=36, hidden_size=36, num_layers=1, batch_first=True  # 输入 36、隐藏 36、单层、(B,H,feat) 维序
            )  # Actor 的 LSTM 层构造完毕
        elif rnn == "gru":  # 选 GRU（门控循环单元，比 LSTM 少一门，训练更快）
            self.rnn = nn.GRU(  # 构造 GRU 层
                input_size=36, hidden_size=36, num_layers=1, batch_first=True  # 参数含义同上
            )  # Actor 的 GRU 层构造完毕（默认分支）
        else:  # 其余情况（前面 assert 已保证只剩 "rnn"）
            self.rnn = nn.RNN(  # 构造朴素 RNN 层（无门控，难长程记忆，作对照）
                input_size=36, hidden_size=36, num_layers=1, batch_first=True  # 参数含义同上
            )  # Actor 的朴素 RNN 层构造完毕

        self.layer_1 = nn.Linear(36, 400)  # 决策层1：RNN 末步输出 36→400
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # Kaiming 初始化：适配 leaky_relu 的方差保持
        self.layer_2 = nn.Linear(400, 300)  # 决策层2：400→300
        torch.nn.init.kaiming_uniform_(self.layer_2.weight, nonlinearity="leaky_relu")  # 同上初始化
        self.layer_3 = nn.Linear(300, action_dim)  # 输出层：300→action_dim
        self.tanh = nn.Tanh()  # tanh：动作压到 (-1,1)

    # ===================== forward：状态历史序列 → 动作 =====================
    # 输入：s (B,H,185)（训练，H=history_len=10）或 (H,185)（单条推理）；输出：a (B,2)
    # 教学要点：先把 (B,H,·) 摊平成 (B*H,·) 让 CNN 逐帧并行提特征，再折回 (B,H,·) 喂 RNN
    def forward(self, s):  # 前向传播：状态历史序列→动作
        if len(s.shape) == 2:  # 推理期输入是单条历史 (H,185)（无 batch 维）
            s = s.unsqueeze(0)  # 补成 (1,H,185)，统一按批量处理

        batch_n, hist_n, state_n = s.shape  # 拆出维度：B=batch，H=历史步数，S=单帧状态维数
        s = s.reshape(batch_n * hist_n, state_n)  # 摊平批与时间步：(B,H,185)->(B*H,185)，让 CNN 一视同仁处理每帧

        laser = s[:, :-5]  # 切激光段（每帧末 5 位之外）：(B*H,185)->(B*H,180)
        goal = s[:, -5:-2]  # 切目标段 [距离,cos,sin]：(B*H,3)
        act = s[:, -2:]  # 切上一步动作段 [线速,角速]：(B*H,2)
        laser = laser.unsqueeze(1)  # 加通道维满足 Conv1d：(B*H,180)->(B*H,1,180)

        l = F.leaky_relu(self.cnn1(laser))  # 卷积1+激活：(B*H,1,180)->(B*H,4,44)
        l = F.leaky_relu(self.cnn2(l))  # 卷积2：(B*H,4,44)->(B*H,8,10)
        l = F.leaky_relu(self.cnn3(l))  # 卷积3：(B*H,8,10)->(B*H,4,4)
        l = l.flatten(start_dim=1)  # 展平通道×位置：(B*H,4,4)->(B*H,16)

        g = F.leaky_relu(self.goal_embed(goal))  # 目标嵌入：(B*H,3)->(B*H,10)

        a = F.leaky_relu(self.action_embed(act))  # 上步动作嵌入：(B*H,2)->(B*H,10)

        s = torch.concat((l, g, a), dim=-1)  # 每帧三路拼接：16+10+10=36，(B*H,36)

        s = s.reshape(batch_n, hist_n, -1)  # 折回时间结构：(B*H,36)->(B,H,36)，-1 自动推成 36
        output, _ = self.rnn(s)  # RNN 沿时间维滚动：输出每步隐藏态 (B,H,36)（第二个返回值 h_n 末状态元组被丢弃）
        last_output = output[:, -1, :]  # 只取最后一步隐藏态 (B,H,36)->(B,36)：序列的"读后总结"
        s = F.leaky_relu(self.layer_1(last_output))  # 决策层1：36→400
        s = F.leaky_relu(self.layer_2(s))  # 决策层2：400→300
        a = self.tanh(self.layer_3(s))  # 输出层+tanh：300→2 并压到 (-1,1)
        return a  # 返回动作 (B,2)


# ===================== 类：Critic（评论家 / 循环卷积孪生 Q 网络） =====================
# 与"普通 actor-critic"的三大差异（代码实证）：
#   1) 双 Q 头（Q1/Q2 参数独立、训练取 min）——普通 AC 只有一个 critic，Q-learning 高估偏差无压制；
#   2) 状态编码器是 CNN+RNN 共享主干（吃 10 帧历史），普通 AC 通常单帧 MLP；
#   3) 动作不与状态早拼接，而是经 layer_2_a/layer_5_a 变换后与状态流逐元素相加（TD3 式晚融合）。
# 输入输出：s (B,H,185)、action (B,2)；输出 q1/q2 各 (B,1)。
class Critic(nn.Module):  # Critic：循环卷积孪生 Q 值网络（评论家）
    """
    Critic network that estimates Q-values for state-action pairs.

    Architecture:
        - Processes the same input as the Actor (laser scan, goal, and previous action).
        - Uses two separate Q-networks (double Q-learning) for stability.
        - Each Q-network receives both the RNN-processed state and current action.

    Parameters
    ----------
    action_dim : int
        Dimensionality of the action space.
    rnn : str, optional
        Type of RNN layer to use ("lstm", "gru", or "rnn").
    """

    # ===================== __init__：共享编码器 + 孪生 Q 头 =====================
    # 编码器（卷积+嵌入+RNN）与 Actor 同构且为 Q1/Q2 共享；Q1=layer_1/2_*/3，Q2=layer_4/5_*/6
    def __init__(self, action_dim, rnn="gru"):  # action_dim 动作维数；rnn 循环层类型
        super(Critic, self).__init__()  # 注册 nn.Module 机制
        assert rnn in ["lstm", "gru", "rnn"], "Unsupported rnn type"  # 防御：类型合法性检查

        self.cnn1 = nn.Conv1d(1, 4, kernel_size=8, stride=4)  # 共享卷积1：单帧 (·,1,180)->(·,4,44)
        self.cnn2 = nn.Conv1d(4, 8, kernel_size=8, stride=4)  # 共享卷积2：(·,4,44)->(·,8,10)
        self.cnn3 = nn.Conv1d(8, 4, kernel_size=4, stride=2)  # 共享卷积3：(·,8,10)->(·,4,4)

        self.goal_embed = nn.Linear(3, 10)  # 共享目标嵌入：3→10
        self.action_embed = nn.Linear(2, 10)  # 共享上步动作嵌入：2→10（嵌的是状态里的上一步动作，不是待评估动作）

        # ---- 共享 RNN 段（与 Actor 同款三选一） ----
        if rnn == "lstm":  # 选 LSTM
            self.rnn = nn.LSTM(  # 构造 LSTM 层
                input_size=36, hidden_size=36, num_layers=1, batch_first=True  # 输入/隐藏均 36 维、单层、batch 在前
            )  # Critic 的 LSTM 层构造完毕
        elif rnn == "gru":  # 选 GRU
            self.rnn = nn.GRU(  # 构造 GRU 层
                input_size=36, hidden_size=36, num_layers=1, batch_first=True  # 参数含义同上
            )  # Critic 的 GRU 层构造完毕（默认分支）
        else:  # 其余情况（assert 已保证是 "rnn"）
            self.rnn = nn.RNN(  # 构造朴素 RNN 层
                input_size=36, hidden_size=36, num_layers=1, batch_first=True  # 参数含义同上
            )  # Critic 的朴素 RNN 层构造完毕

        self.layer_1 = nn.Linear(36, 400)  # Q1 第 1 层：RNN 末步特征 36→400
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q1 第 1 层
        self.layer_2_s = nn.Linear(400, 300)  # Q1 状态流分支：400→300
        torch.nn.init.kaiming_uniform_(self.layer_2_s.weight, nonlinearity="leaky_relu")  # Kaiming 初始化状态流
        self.layer_2_a = nn.Linear(action_dim, 300)  # Q1 动作流分支：action_dim→300（待评估动作的入口）
        torch.nn.init.kaiming_uniform_(self.layer_2_a.weight, nonlinearity="leaky_relu")  # Kaiming 初始化动作流
        self.layer_3 = nn.Linear(300, 1)  # Q1 输出层：300→1
        torch.nn.init.kaiming_uniform_(self.layer_3.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q1 输出层

        self.layer_4 = nn.Linear(36, 400)  # Q2 第 1 层：36→400（结构与 Q1 相同、参数独立）
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # 注意：这里初始化的仍是 layer_1（按命名本意应是 layer_4 的疑似笔误），layer_4 实际保持默认初始化
        self.layer_5_s = nn.Linear(400, 300)  # Q2 状态流分支：400→300
        torch.nn.init.kaiming_uniform_(self.layer_5_s.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q2 状态流
        self.layer_5_a = nn.Linear(action_dim, 300)  # Q2 动作流分支：action_dim→300
        torch.nn.init.kaiming_uniform_(self.layer_5_a.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q2 动作流
        self.layer_6 = nn.Linear(300, 1)  # Q2 输出层：300→1
        torch.nn.init.kaiming_uniform_(self.layer_6.weight, nonlinearity="leaky_relu")  # Kaiming 初始化 Q2 输出层

    # ===================== forward：状态历史 + 动作 → 孪生 Q 值 =====================
    # 输入：s (B,H,185)、action (B,2)（窗口末端执行的动作）；输出：(q1, q2) 各 (B,1)
    # 教学要点：动作分支用 .data 手工矩阵乘（沿自经典 TD3 参考实现），两流晚融合
    def forward(self, s, action):  # 前向传播：(状态历史, 动作)→(q1,q2)
        batch_n, hist_n, state_n = s.shape  # 拆维度：critic 只在训练期被调用，输入必为 (B,H,S) 三维
        s = s.reshape(batch_n * hist_n, state_n)  # 摊平批×时间步：(B,H,185)->(B*H,185)

        laser = s[:, :-5]  # 切激光段：(B*H,180)
        goal = s[:, -5:-2]  # 切目标段 [距离,cos,sin]：(B*H,3)
        act = s[:, -2:]  # 切上一步动作段：(B*H,2)
        laser = laser.unsqueeze(1)  # 加通道维：(B*H,1,180)

        l = F.leaky_relu(self.cnn1(laser))  # 共享卷积1：(B*H,4,44)
        l = F.leaky_relu(self.cnn2(l))  # 共享卷积2：(B*H,8,10)
        l = F.leaky_relu(self.cnn3(l))  # 共享卷积3：(B*H,4,4)
        l = l.flatten(start_dim=1)  # 展平：(B*H,16)

        g = F.leaky_relu(self.goal_embed(goal))  # 目标嵌入：(B*H,10)

        a = F.leaky_relu(self.action_embed(act))  # 上步动作嵌入：(B*H,10)

        s = torch.concat((l, g, a), dim=-1)  # 每帧拼接特征：(B*H,36)

        s = s.reshape(batch_n, hist_n, -1)  # 折回时间结构：(B,H,36)
        output, _ = self.rnn(s)  # RNN 滚动聚合历史：输出 (B,H,36)，h_n 丢弃
        last_output = output[:, -1, :]  # 取末步隐藏态：(B,36)——Q1/Q2 共享这一份"历史总结"

        s1 = F.leaky_relu(self.layer_1(last_output))  # Q1 第 1 层：吃 RNN 末步特征 (B,36)->(B,400)
        self.layer_2_s(s1)  # 调用但丢弃返回值（经典 TD3 参考实现的遗留写法，真正生效的是下面两行手工矩阵乘）
        self.layer_2_a(action)  # 同上：结果被丢弃
        s11 = torch.mm(s1, self.layer_2_s.weight.data.t())  # 手工复刻 Linear——状态流：(B,400)x(400,300)->(B,300)；.data 脱图，该权重不收梯度
        s12 = torch.mm(action, self.layer_2_a.weight.data.t())  # 手工复刻——动作流：(B,2)x(2,300)->(B,300)；梯度仍可经 action 回传至 actor
        s1 = F.leaky_relu(s11 + s12 + self.layer_2_a.bias.data)  # 状态流+动作流逐元素相加（晚融合）加偏置再激活：(B,300)
        q1 = self.layer_3(s1)  # Q1 输出：(B,1)

        s2 = F.leaky_relu(self.layer_4(last_output))  # Q2 第 1 层：同样吃 RNN 末步特征 (B,36)->(B,400)
        self.layer_5_s(s2)  # 同 Q1 模式：返回值丢弃
        self.layer_5_a(action)  # 同上
        s21 = torch.mm(s2, self.layer_5_s.weight.data.t())  # Q2 状态流：(B,300)
        s22 = torch.mm(action, self.layer_5_a.weight.data.t())  # Q2 动作流：(B,300)
        s2 = F.leaky_relu(s21 + s22 + self.layer_5_a.bias.data)  # Q2 晚融合+激活：(B,300)
        q2 = self.layer_6(s2)  # Q2 输出：(B,1)
        return q1, q2  # 返回孪生 Q 值：训练时取 min 抑制高估


# RCPG network —— RCPG 智能体主类（Recurrent Convolutional Policy Gradient）
# ===================== 类：RCPG（循环卷积策略梯度智能体总控） =====================
# 职责：组装循环版 actor/critic 及 target 网络，实现 TD3 式训练循环、动作选择、存/取档、状态预处理。
# 算法定位（代码实证）：训练循环与 TD3 完全同构（双 Q 取 min + 目标动作裁剪噪声 + 策略延迟更新 + 软更新），
# 网络换成"CNN 逐帧编码 + RNN 聚合历史"，专吃 (B,10,185) 状态序列——名字叫 Policy Gradient，实为
# 确定性策略梯度（DPG）家族的 recurrent 变体；与 CNNTD3 的差异是没有 use_max_bound 上界正则。
class RCPG(object):  # 智能体总控类（非 nn.Module，内部持有 4 个网络）
    """
    Recurrent Convolutional Policy Gradient (RCPG) agent for continuous control tasks.

    This class implements a recurrent actor-critic architecture using twin Q-networks and soft target updates.
    It includes model initialization, training, inference, saving/loading, and ROS-based state preparation.

    Parameters
    ----------
    state_dim : int
        Dimensionality of the input state.
    action_dim : int
        Dimensionality of the action space.
    max_action : float
        Maximum allowable action value.
    device : torch.device
        Device to run the model on (e.g., 'cuda' or 'cpu').
    lr : float, optional
        Learning rate for actor and critic optimizers. Default is 1e-4.
    save_every : int, optional
        Frequency (in iterations) to save model checkpoints. Default is 0 (disabled).
    load_model : bool, optional
        Whether to load pretrained model weights. Default is False.
    save_directory : Path, optional
        Directory where models are saved. Default is "robot_nav/models/RCPG/checkpoint".
    model_name : str, optional
        Name prefix for model checkpoint files. Default is "RCPG".
    load_directory : Path, optional
        Directory to load pretrained models from. Default is "robot_nav/models/RCPG/checkpoint".
    rnn : str, optional
        Type of RNN to use in networks ("lstm", "gru", or "rnn"). Default is "gru".
    """

    # ===================== __init__：智能体初始化 =====================
    # 建 4 个网络（actor/critic + 各自 target）+ 2 个 Adam 优化器 + TensorBoard；target 初始同权重
    def __init__(  # 构造函数（参数多，跨行书写）
        self,  # 实例自身（Python 惯例）
        state_dim,  # 单帧状态维数（本仓 185）
        action_dim,  # 动作维数（本仓 2）
        max_action,  # 动作幅值上界，clip 用
        device,  # torch.device：CPU 或 GPU
        lr=1e-4,  # 学习率：actor/critic 共用
        save_every=0,  # 每 N 次 train 自动存档；0=关闭
        load_model=False,  # 构造时是否加载预训练权重
        save_directory=Path("robot_nav/models/RCPG/checkpoint"),  # 存档目录（默认仓内相对路径）
        model_name="RCPG",  # 模型名前缀（会拼上 rnn 类型成 "RCPGgru" 等）
        load_directory=Path("robot_nav/models/RCPG/checkpoint"),  # 加载目录（load_model=True 时用）
        rnn="gru",  # 循环层类型："lstm"/"gru"/"rnn"
    ):  # 参数表结束，函数体开始
        # Initialize the Actor network —— 初始化 Actor（当前策略网络，带 RNN）
        self.device = device  # 记录运行设备
        self.actor = Actor(action_dim, rnn).to(self.device)  # 在线 actor：选动作+被训练
        self.actor_target = Actor(action_dim, rnn).to(self.device)  # 目标 actor：算 TD 目标用的慢速副本
        self.actor_target.load_state_dict(self.actor.state_dict())  # 目标初始权重 = actor 权重
        self.actor_optimizer = torch.optim.Adam(params=self.actor.parameters(), lr=lr)  # actor 的 Adam 优化器

        # Initialize the Critic networks —— 初始化 Critic（在线+目标，均带 RNN）
        self.critic = Critic(action_dim, rnn).to(self.device)  # 在线 critic：被回归训练估值
        self.critic_target = Critic(action_dim, rnn).to(self.device)  # 目标 critic：算 TD 目标
        self.critic_target.load_state_dict(self.critic.state_dict())  # 目标初始权重 = critic 权重
        self.critic_optimizer = torch.optim.Adam(params=self.critic.parameters(), lr=lr)  # critic 的 Adam 优化器

        self.action_dim = action_dim  # 记录动作维数（噪声采样用）
        self.max_action = max_action  # 记录动作上界（clip 用）
        self.state_dim = state_dim  # 记录状态维数（prepare_state 断言用）
        self.writer = SummaryWriter(comment=model_name)  # TensorBoard 写入器
        self.iter_count = 0  # train 调用计数（曲线横坐标/定期存档）
        self.model_name = model_name + rnn  # 拼出带循环层类型的模型名，如 "RCPGgru"（存档文件互相区分）
        if load_model:  # 若指定加载预训练权重
            self.load(filename=self.model_name, directory=load_directory)  # 读取 4 个网络权重
        self.save_every = save_every  # 存档频率
        self.save_directory = save_directory  # 存档目录

    # ===================== get_action：带探索噪声的动作选择 =====================
    # 输入：obs 状态历史 (H,185)（np 数组）、add_noise 开关；输出：np 动作向量
    # 环境交互入口：训练时加 N(0,0.2) 高斯噪声探索，评估时关闭
    def get_action(self, obs, add_noise):  # 环境交互入口：选动作（可选加探索噪声）
        """
        Computes an action for the given observation, with optional exploration noise.

        Parameters
        ----------
        obs : array_like
            Input observation (state).
        add_noise : bool
            If True, adds Gaussian noise for exploration.

        Returns
        -------
        np.ndarray
            Action vector clipped to [-max_action, max_action].
        """
        if add_noise:  # 训练期：确定性动作 + 噪声（TD3 探索方式，噪声加在网络外）
            return (  # 返回带噪动作（跨行表达式的开括号）
                self.act(obs) + np.random.normal(0, 0.2, size=self.action_dim)  # act 出确定性动作再叠加高斯噪声
            ).clip(-self.max_action, self.max_action)  # 裁回合法范围后返回
        else:  # 评估期：不加噪声
            return self.act(obs)  # 纯确定性策略动作

    # ===================== act：纯前向的确定性动作 =====================
    # 输入：state（状态历史 np 数组 (H,185)）；输出：展平 np 动作 (2,)
    # numpy→torch→网络→numpy 的桥接薄层
    def act(self, state):  # 纯前向取确定性动作（不加噪声）
        """
        Returns the actor network's raw output for a given input state.

        Parameters
        ----------
        state : array_like
            State input.

        Returns
        -------
        np.ndarray
            Deterministic action vector from actor network.
        """
        # Function to get the action from the actor —— 从 actor 取确定性动作
        state = torch.Tensor(state).to(self.device)  # np 转 torch 张量并上设备 (H,185)
        return self.actor(state).cpu().data.numpy().flatten()  # 前向（网络内补 batch 维）→回 CPU→脱图→np 展平成 (2,)

    # training cycle —— 训练主循环（一次调用 = iterations 轮梯度更新）
    # ===================== train：TD3 式训练循环 =====================
    # 损失构成（代码实证）：critic = MSE(Q1,y)+MSE(Q2,y)（无 CNNTD3 的上界正则项）；
    # actor = -mean(Q1)（对 Q 梯度上升）；y = r + γ(1-done)·min(Q1',Q2')，目标动作加裁剪噪声。
    # 输入：RolloutReplayBuffer（按回合存、回放带 history_len 帧历史）；reward/done 无需 reshape（该 buffer 已返回 (B,1)）
    def train(  # TD3 式训练主循环（参数跨多行）
        self,  # 实例自身
        replay_buffer,  # 序列回放池（存整回合，采样返回 (B,H,185) 状态窗口）
        iterations,  # 本轮梯度迭代次数
        batch_size,  # 采样批大小
        discount=0.99,  # 折扣因子 γ：未来奖励打折，平衡远近回报
        tau=0.005,  # 软更新系数：target = τ*新 + (1-τ)*旧
        policy_noise=0.2,  # 目标策略平滑噪声强度 σ
        noise_clip=0.5,  # 目标噪声裁剪范围 ±0.5
        policy_freq=2,  # 策略延迟更新频率：每 2 轮 critic 更新才 1 次 actor 更新
    ):  # 参数表结束，函数体开始
        """
        Performs training over a number of iterations using batches from a replay buffer.

        Parameters
        ----------
        replay_buffer : object
            Experience replay buffer with a sample_batch method.
        iterations : int
            Number of training iterations.
        batch_size : int
            Size of each training batch.
        discount : float, optional
            Discount factor for future rewards (γ). Default is 0.99.
        tau : float, optional
            Soft update parameter for target networks. Default is 0.005.
        policy_noise : float, optional
            Standard deviation of noise added to target actions. Default is 0.2.
        noise_clip : float, optional
            Range to clip the noise. Default is 0.5.
        policy_freq : int, optional
            Frequency of policy updates relative to critic updates. Default is 2.
        """
        av_Q = 0  # 平均目标 Q 累计器（写 TensorBoard 用）
        max_Q = -inf  # 最大目标 Q 记录，初始负无穷
        av_loss = 0  # critic 损失累计器
        for it in range(iterations):  # 主循环：每轮一次完整 critic(+延迟的 actor) 更新
            # sample a batch from the replay buffer —— 采一批"带历史窗口"的经验
            (  # 元组解包开始：一次拿到五元组经验批
                batch_states,  # 状态历史窗口批 (B,10,185)
                batch_actions,  # 窗口末端动作批 (B,2)
                batch_rewards,  # 奖励批 (B,1)（RolloutReplayBuffer 内已 reshape）
                batch_dones,  # 终止标志批 (B,1)（同上）
                batch_next_states,  # 下一状态历史窗口批 (B,10,185)
            ) = replay_buffer.sample_batch(batch_size)  # 按回合随机抽样并截历史窗口
            state = torch.Tensor(batch_states).to(self.device)  # 转 tensor 上设备 (B,10,185)
            next_state = torch.Tensor(batch_next_states).to(self.device)  # 下一状态历史窗口转张量 (B,10,185)
            action = torch.Tensor(batch_actions).to(self.device)  # 动作转张量 (B,2)
            reward = torch.Tensor(batch_rewards).to(self.device)  # (B,1)——与 CNNTD3 不同：这里不 reshape，因为序列回放池已给 (B,1)（代码实证）
            done = torch.Tensor(batch_dones).to(self.device)  # (B,1)，同理

            # Obtain the estimated action from the next state by using the actor-target —— 目标策略出下一状态的动作
            next_action = self.actor_target(next_state)  # (B,2)；用 target 网络稳定 TD 目标

            # Add noise to the action —— 目标策略平滑（TD3 关键技巧）
            noise = (  # 开始构造目标平滑噪声张量（跨行链式调用的开括号）
                torch.Tensor(batch_actions)  # 借 batch_actions 形状造同形张量 (B,2)
                .data.normal_(0, policy_noise)  # 原地填 N(0,σ=0.2)；.data 脱离计算图
                .to(self.device)  # 搬到设备
            )  # 噪声张量构造完毕，形状 (B,2)
            noise = noise.clamp(-noise_clip, noise_clip)  # 噪声裁到 ±0.5：抹平 critic 尖峰、抗过高估
            next_action = (next_action + noise).clamp(-self.max_action, self.max_action)  # 加噪动作裁回合法范围 (B,2)

            # Calculate the Q values from the critic-target network for the next state-action pair —— 目标 critic 双 Q 估值
            target_Q1, target_Q2 = self.critic_target(next_state, next_action)  # 各 (B,1)

            # Select the minimal Q value from the 2 calculated values —— 双 Q 取小（clipped double Q）
            target_Q = torch.min(target_Q1, target_Q2)  # (B,1)；压制 Q-learning 的系统性高估
            av_Q += torch.mean(target_Q)  # 累计均值（监控）
            max_Q = max(max_Q, torch.max(target_Q))  # 刷新最大值（监控）
            # Calculate the final Q value from the target network parameters by using Bellman equation —— 贝尔曼方程构造 TD 目标
            target_Q = reward + ((1 - done) * discount * target_Q).detach()  # y = r + γ·(1-done)·min Q'，(B,1)；detach 固定回归靶不传梯度
            # 教学注：done=1（撞墙/到目标）时未来项归零——终止后没有未来

            # Get the Q values of the basis networks with the current parameters —— 在线 critic 对当前 (s,a) 的估值
            current_Q1, current_Q2 = self.critic(state, action)  # 各 (B,1)

            # Calculate the loss between the current Q value and the target Q value —— critic 回归损失（总损失只此两项，无正则）
            loss = F.mse_loss(current_Q1, target_Q) + F.mse_loss(current_Q2, target_Q)  # 双 Q 各自对同一目标 y 的 MSE 相加

            # Perform the gradient descent —— critic 梯度下降
            self.critic_optimizer.zero_grad()  # 清旧梯度
            loss.backward()  # 反向传播
            self.critic_optimizer.step()  # Adam 更新 critic

            if it % policy_freq == 0:  # 策略延迟更新：每 2 轮动一次 actor（先让 critic 收敛些）
                # Maximize the actor output value by performing gradient descent on negative Q values —— 最大化 actor 输出 Q 值
                # (essentially perform gradient ascent) —— 对 -Q 下降 = 对 Q 上升 = 确定性策略梯度
                actor_grad, _ = self.critic(state, self.actor(state))  # actor 现出新动作 (B,2) 喂 critic，取 Q1 (B,1)（Q2 丢弃）
                actor_grad = -actor_grad.mean()  # 负均值当损失：最小化它即最大化 Q
                self.actor_optimizer.zero_grad()  # 清 actor 梯度
                actor_grad.backward()  # 梯度经 critic 动作流（.data 矩阵乘仍对 action 可导）回传到 actor
                self.actor_optimizer.step()  # Adam 更新 actor

                # Use soft update to update the actor-target network parameters by —— actor 目标网络软更新
                # infusing small amount of current parameters —— actor 目标网络软更新
                for param, target_param in zip(  # 遍历 actor 与 actor_target 对应参数
                    self.actor.parameters(), self.actor_target.parameters()  # 逐参数配对
                ):  # for 循环体开始
                    target_param.data.copy_(  # 原地写入目标参数
                        tau * param.data + (1 - tau) * target_param.data  # 目标 ← 0.5% 新 + 99.5% 旧，缓慢跟随
                    )  # 该参数软更新完成
                # Use soft update to update the critic-target network parameters by infusing —— critic 目标网络软更新
                # small amount of current parameters —— critic 目标网络软更新（同公式）
                for param, target_param in zip(  # 遍历 critic 与 critic_target 对应参数
                    self.critic.parameters(), self.critic_target.parameters()  # 逐参数配对
                ):  # for 循环体开始
                    target_param.data.copy_(  # 原地写入目标参数
                        tau * param.data + (1 - tau) * target_param.data  # 同样的指数滑动平均式更新
                    )  # 该参数软更新完成

            av_loss += loss  # 累计本轮损失
        self.iter_count += 1  # train 调用计数 +1
        # Write new values for tensorboard —— 写 TensorBoard 曲线
        self.writer.add_scalar("train/loss", av_loss / iterations, self.iter_count)  # 平均 critic 损失
        self.writer.add_scalar("train/avg_Q", av_Q / iterations, self.iter_count)  # 平均目标 Q
        self.writer.add_scalar("train/max_Q", max_Q, self.iter_count)  # 最大目标 Q
        if self.save_every > 0 and self.iter_count % self.save_every == 0:  # 到达自动存档周期
            self.save(filename=self.model_name, directory=self.save_directory)  # 存 4 个网络权重

    # ===================== save：保存 4 个网络权重 =====================
    # 输入：filename 前缀（含 rnn 类型，如 RCPGgru）、directory 目录；输出磁盘 4 个 .pth
    def save(self, filename, directory):  # 保存 4 个网络权重到磁盘
        """
        Saves actor and critic model weights to disk.

        Parameters
        ----------
        filename : str
            Base name for saved model files.
        directory : str or Path
            Target directory to save the models.
        """
        Path(directory).mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在不报错）
        torch.save(self.actor.state_dict(), "%s/%s_actor.pth" % (directory, filename))  # 存在线 actor 权重
        torch.save(  # 保存目标 actor 权重
            self.actor_target.state_dict(),  # 目标 actor 的参数字典
            "%s/%s_actor_target.pth" % (directory, filename),  # 文件名带 _actor_target 后缀
        )  # 目标 actor 存档完成
        torch.save(self.critic.state_dict(), "%s/%s_critic.pth" % (directory, filename))  # 存在线 critic 权重
        torch.save(  # 保存目标 critic 权重
            self.critic_target.state_dict(),  # 目标 critic 的参数字典
            "%s/%s_critic_target.pth" % (directory, filename),  # 文件名带 _critic_target 后缀
        )  # 目标 critic 存档完成

    # ===================== load：从磁盘恢复 4 个网络权重 =====================
    # 输入：filename 前缀、directory 目录；效果：4 个网络权重被覆盖为存档值
    def load(self, filename, directory):  # 从磁盘恢复 4 个网络权重
        """
        Loads model weights for actor and critic networks from disk.

        Parameters
        ----------
        filename : str
            Base name of saved model files.
        directory : str or Path
            Directory from which to load model files.
        """
        self.actor.load_state_dict(  # 装入在线 actor 权重（跨行调用）
            torch.load("%s/%s_actor.pth" % (directory, filename))  # 读在线 actor 权重文件
        )  # 在线 actor 权重装入完毕
        self.actor_target.load_state_dict(  # 装入目标 actor 权重（跨行调用）
            torch.load("%s/%s_actor_target.pth" % (directory, filename))  # 读目标 actor 权重
        )  # 目标 actor 权重装入完毕
        self.critic.load_state_dict(  # 装入在线 critic 权重（跨行调用）
            torch.load("%s/%s_critic.pth" % (directory, filename))  # 读在线 critic 权重
        )  # 在线 critic 权重装入完毕
        self.critic_target.load_state_dict(  # 装入目标 critic 权重（跨行调用）
            torch.load("%s/%s_critic_target.pth" % (directory, filename))  # 读目标 critic 权重
        )  # 目标 critic 权重装入完毕
        print(f"Loaded weights from: {directory}")  # 打印加载来源目录确认

    # ===================== prepare_state：ROS 原始数据 → 网络输入状态 =====================
    # 输入：一帧激光扫描 + 导航量 + 上一步动作；输出：(185 维归一化状态, 终止标志)
    # 与 CNNTD3.prepare_state 完全同构：物理量纲压到 O(1)；序列化进 state_queue 后由网络吃历史
    def prepare_state(self, latest_scan, distance, cos, sin, collision, goal, action):  # ROS 原始数据→归一化状态
        """
        Converts raw sensor and environment data into a normalized input state vector.

        Parameters
        ----------
        latest_scan : list or np.ndarray
            Laser scan data.
        distance : float
            Distance to the goal.
        cos : float
            Cosine of the heading angle.
        sin : float
            Sine of the heading angle.
        collision : bool
            Whether a collision has occurred.
        goal : bool
            Whether the goal has been reached.
        action : list or np.ndarray
            Previous action taken [linear, angular].

        Returns
        -------
        state : list
            Normalized input state vector.
        terminal : int
            Terminal flag: 1 if goal reached or collision, otherwise 0.
        """
        latest_scan = np.array(latest_scan)  # 列表转 np 数组便于向量化处理 (180,)

        inf_mask = np.isinf(latest_scan)  # 找无穷远回波（激光没打到东西）的掩码
        latest_scan[inf_mask] = 7.0  # 无穷远截断为 7 米，避免 inf 毁掉网络
        latest_scan /= 7  # 除以 7 归一化到约 [0,1]

        # Normalize to [0, 1] range —— 各导航量归一化
        distance /= 10  # 距离除以 10（约 10 米量级）归一化
        lin_vel = action[0] * 2  # 上一步线速度仿射编码：×2
        ang_vel = (action[1] + 1) / 2  # 上一步角速度：[-1,1]→[0,1]
        state = latest_scan.tolist() + [distance, cos, sin] + [lin_vel, ang_vel]  # 拼成 180+3+2=185 维状态（cos/sin 编码朝向，避免 ±π 跳变）

        assert len(state) == self.state_dim  # 维度断言：与构造时 state_dim 一致才继续
        terminal = 1 if collision or goal else 0  # 终止标志：撞墙或到目标都算回合结束

        return state, terminal  # 返回 (185 维状态, 终止标志)
