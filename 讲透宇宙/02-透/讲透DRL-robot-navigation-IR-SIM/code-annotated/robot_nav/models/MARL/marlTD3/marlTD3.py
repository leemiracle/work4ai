# ============================================================================ #
# 逐行中文教学注释版 —— marlTD3.py（多智能体 TD3 + 注意力通信，CTDE 范式）
# 注释为纯增量：代码、原英文注释与 docstring 逐字符保持原样（原仓只读未动）。
# 原文件：robot_nav/models/MARL/marlTD3/marlTD3.py（633 行）
# ============================================================================ #
from pathlib import Path  # 导入 Path 对象：跨平台创建/操作模型存档目录

import numpy as np  # 数值计算库：状态向量组装、cos/sin 特征、探索噪声采样
import torch  # PyTorch 主库：张量定义、自动微分、GPU 加速
import torch.nn as nn  # 神经网络模块库：Linear 全连接层、Sequential 容器等
import torch.nn.functional as F  # 函数式接口：leaky_relu / mse_loss / BCE_with_logits
from numpy import inf  # 只导入无穷大 inf：max_Q 统计量初始化为 -inf 用
from torch.utils.tensorboard import SummaryWriter  # TensorBoard 写入器：记录训练曲线

from robot_nav.models.MARL.Attention.g2anet import G2ANet  # 注意力后端之二：G2ANet（硬门控+软加权双阶段图注意力）
from robot_nav.models.MARL.Attention.iga import Attention  # 注意力后端之一（默认）：IGA 图注意力（编码→硬门控选边→软加权消息传递→解码）


# ============================【类】Actor：策略网络（执行端）============================ #
# 职责：RL 的"策略网络/actor"=观测→动作的映射；本类先用注意力把 N 个机器人的观测
#       聚合成"自身嵌入 ⊕ 加权邻居嵌入"，再经 MLP 头输出连续动作（Tanh 压到 (-1,1)）。
# 输入输出：forward(obs) 形状 (B,N,obs_dim)→(B*N,action_dim) 动作+注意力诊断量。
# 位置：CTDE（集中式训练/分散式执行：训练可用全队信息，执行各 agent 独立前向）的
#       "分散执行"侧——注意力让每个 agent 聚合邻居信息后独立出动作。
class Actor(nn.Module):  # 继承 PyTorch 模块基类：自动注册参数，支持 .to(device)/state_dict
    """
    Policy network for multi-agent control with an attention encoder.

    The actor encodes inter-agent context (via IGA or G2ANet attention) and maps
    the attended embedding to continuous actions.

    Args:
        action_dim (int): Number of action dimensions per agent.
        embedding_dim (int): Dimensionality of the attention embedding.
        attention (str): Attention backend, one of {"igs", "g2anet"}.

    Attributes:
        attention (nn.Module): Attention encoder producing attended embeddings and
            diagnostics (hard logits, distances, entropy, masks, combined weights).
        policy_head (nn.Sequential): MLP mapping attended embeddings to actions in [-1, 1].
    """

    # 【方法】__init__：搭建 Actor 的两段式结构
    # 输入：action_dim（=2：线速度+角速度）、embedding_dim（=256：注意力嵌入维）、
    #       attention ∈ {"igs","g2anet"}；输出：无（仅建网络）。
    # 结构：注意力编码器（看全队）→ 策略头 MLP（出动作）。
    def __init__(self, action_dim, embedding_dim, attention):  # 三参构造：动作维/嵌入维/注意力类型
        super().__init__()  # 调用父类构造：初始化模块簿记（必须最先执行）
        if attention == "igs":  # 分支一：按字符串选注意力后端
            self.attention = Attention(embedding_dim)  # ➊ edge classifier ｜ IGA 编码器：内含边分类器，(B,N,obs)→(B*N,512) 嵌入+诊断量
        elif attention == "g2anet":  # 分支二：G2ANet 后端
            self.attention = G2ANet(embedding_dim)  # ➊ edge classifier ｜ G2ANet 编码器：Gumbel 门控决定"和谁通信"
        else:  # 其余取值一律拒绝
            raise ValueError("unknown attention mechanism in Actor")  # 抛异常：防拼写错误静默落空

        # ➋ policy head (everything _after_ attention) ｜ 策略头：注意力之后的所有层（➋为原注）
        self.policy_head = nn.Sequential(  # 顺序容器：按序堆叠以下各层
            nn.Linear(embedding_dim * 2, 400),  # 全连接 512→400（512=自身嵌入256 ⊕ 邻居加权嵌入256 拼接）
            nn.LeakyReLU(),  # 泄漏整流激活：负区保留 0.01 斜率，梯度不中断
            nn.Linear(400, 300),  # 全连接 400→300 隐层
            nn.LeakyReLU(),  # 再次非线性化
            nn.Linear(300, action_dim),  # 输出层 300→action_dim（=2）
            nn.Tanh(),  # Tanh 压到 (-1,1)：连续动作有界；环境交互时再按 max_action 缩放
        )  # Sequential 容器结束

    # 【方法】forward：观测→动作的前向推理（执行与训练共用同一条路径）
    # 输入：obs (B,N,obs_dim) 或 (N,obs_dim)（注意力内部会自动补 batch 维）、
    #       detach_attn=是否切断注意力输出与计算图的联系；
    # 输出：动作 (B*N,action_dim) + 5 个注意力诊断量（硬logits/成对距离/软熵/硬掩码/软权重）。
    def forward(self, obs, detach_attn=False):  # 前向传播入口
        """
        Run the actor to produce actions and attention diagnostics.

        Args:
            obs (Tensor): Observations of shape (B, N, obs_dim) or (N, obs_dim).
            detach_attn (bool, optional): If True, detaches attention features before
                the policy head (useful for target policy smoothing). Defaults to False.

        Returns:
            tuple:
                action (Tensor): Predicted actions, shape (B*N, action_dim).
                hard_logits (Tensor): Hard attention logits, shape (B*N, N-1).
                pair_d (Tensor): Unnormalized pairwise distances, shape (B*N, N-1, 1).
                mean_entropy (Tensor): Mean soft-attention entropy (scalar tensor).
                hard_weights (Tensor): Binary hard attention mask, shape (B, N, N).
                combined_weights (Tensor): Soft weights per (receiver, sender),
                    shape (N, N*(N-1)) for each batch item (batched internally).
        """
        attn_out, hard_logits, pair_d, mean_entropy, hard_weights, combined_weights = (  # 一行解包注意力六元组返回值
            self.attention(obs)  # 注意力前向：obs (B,N,11)→attn_out (B*N,512) 等（11 维布局见 prepare_state）
        )  # 解包语句收尾
        if detach_attn:  # used in the policy phase ｜ 原注：策略阶段用；真则切断注意力梯度
            attn_out = attn_out.detach()  # detach：该嵌入不再记入计算图（算目标动作时防梯度回传）
        action = self.policy_head(attn_out)  # 策略头 MLP：(B*N,512)→(B*N,action_dim)，值域 (-1,1)
        return action, hard_logits, pair_d, mean_entropy, hard_weights, combined_weights  # 返回动作+全部诊断量（训练算 BCE/熵正则要用）


# ============================【类】Critic：双 Q 评论家（训练端）============================ #
# 职责：Q 函数（评论家）=评估"状态 s 下做动作 a 的长期折扣回报期望"；TD3 用 twin critic
#       （两条独立 Q 支路）训练时取较小值，压制函数逼近器带来的 Q 高估偏差。
# 输入输出：forward(embedding (B,N,state_dim), action (B*N,action_dim))→q1/q2 (B*N,1)+诊断量。
# 位置：CTDE 的"集中式训练"侧——注意力把全队观测集中进每个 agent 的嵌入；
#       注意动作输入不是 N*action_dim 联合动作，而是逐 agent 的 (B*N,2)（见 forward 教学点）。
class Critic(nn.Module):  # 双 Q 评论家：注意力状态编码 + 两条独立 Q 支路
    """
    Twin Q-value critic with attention-based state encoding.

    Computes two independent Q estimates (Q1, Q2) from attended embeddings and
    concatenated actions, following the TD3 design.

    Args:
        action_dim (int): Number of action dimensions per agent.
        embedding_dim (int): Dimensionality of the attention embedding.
        attention (str): Attention backend, one of {"igs", "g2anet"}.

    Attributes:
        attention (nn.Module): Attention encoder producing attended embeddings and
            diagnostics (hard logits, distances, entropy, masks).
        layer_1..layer_6 (nn.Linear): MLP layers forming the twin Q networks.
    """

    # 【方法】__init__：搭建双 Q 网络（Q1/Q2 同构异参）
    # 输入：action_dim、embedding_dim、attention 后端名；输出：无。
    # 教学点：每条 Q 支路分"状态流(_s)"与"动作流(_a)"两支，在 300 维隐层逐元素相加融合（DDPG 式）。
    def __init__(self, action_dim, embedding_dim, attention):  # 与 Actor 同款三参构造
        super(Critic, self).__init__()  # 父类构造（老式写法，与 super().__init__() 等价）
        self.embedding_dim = embedding_dim  # 存下嵌入维（256），后面建层引用
        if attention == "igs":  # critic 自建一套注意力实例（与 actor 的不共享参数）
            self.attention = Attention(embedding_dim)  # IGA 后端：critic 学自己的"该关注谁"
        elif attention == "g2anet":  # G2ANet 后端分支
            self.attention = G2ANet(embedding_dim)  # ➊ edge classifier ｜ critic 侧独立的边分类器
        else:  # 非法类型兜底
            raise ValueError("unknown attention mechanism in Critic")  # 抛异常

        self.layer_1 = nn.Linear(self.embedding_dim * 2, 400)  # Q1 状态流第 1 层：注意力嵌入 512→400
        torch.nn.init.kaiming_uniform_(self.layer_1.weight, nonlinearity="leaky_relu")  # Kaiming 均匀初始化：适配 leaky_relu 的方差守恒

        self.layer_2_s = nn.Linear(400, 300)  # Q1 状态流第 2 层：400→300
        torch.nn.init.kaiming_uniform_(self.layer_2_s.weight, nonlinearity="leaky_relu")  # 状态流权重初始化

        self.layer_2_a = nn.Linear(action_dim, 300)  # Q1 动作流：action_dim(2)→300——输入是单个 agent 自己的动作
        torch.nn.init.kaiming_uniform_(self.layer_2_a.weight, nonlinearity="leaky_relu")  # 动作流权重初始化

        self.layer_3 = nn.Linear(300, 1)  # Q1 输出头：300→1 标量 Q 值
        torch.nn.init.kaiming_uniform_(self.layer_3.weight, nonlinearity="leaky_relu")  # 输出头初始化

        self.layer_4 = nn.Linear(self.embedding_dim * 2, 400)  # Q2 状态流第 1 层：同 Q1 结构但参数独立
        torch.nn.init.kaiming_uniform_(self.layer_4.weight, nonlinearity="leaky_relu")  # Q2 初始化

        self.layer_5_s = nn.Linear(400, 300)  # Q2 状态流第 2 层
        torch.nn.init.kaiming_uniform_(self.layer_5_s.weight, nonlinearity="leaky_relu")  # Q2 状态流初始化

        self.layer_5_a = nn.Linear(action_dim, 300)  # Q2 动作流：同样只进各 agent 自己的动作
        torch.nn.init.kaiming_uniform_(self.layer_5_a.weight, nonlinearity="leaky_relu")  # Q2 动作流初始化

        self.layer_6 = nn.Linear(300, 1)  # Q2 输出头：300→1
        torch.nn.init.kaiming_uniform_(self.layer_6.weight, nonlinearity="leaky_relu")  # Q2 输出头初始化

    # 【方法】forward：算双 Q 值（同一注意力嵌入喂两条独立支路）
    # 输入：embedding (B,N,state_dim) 全队观测、action (B*N,action_dim) 各 agent 自己的动作；
    # 输出：q1/q2 (B*N,1) + 注意力诊断量（熵/硬logits/成对距离/硬掩码）。
    # 教学点：集中式信息经注意力进嵌入（看到全队），动作轴却是逐 agent 的 (B*N,2)——
    #         多智能体维 N 被 batch 维吸收，等价于"每 agent 一个集中式 critic"的向量化实现。
    def forward(self, embedding, action):  # 前向：观测嵌入+动作→双 Q
        """
        Compute twin Q values from attended embeddings and actions.

        Args:
            embedding (Tensor): Agent embeddings of shape (B, N, state_dim).
            action (Tensor): Actions of shape (B*N, action_dim).

        Returns:
            tuple:
                Q1 (Tensor): First Q-value estimate, shape (B*N, 1).
                Q2 (Tensor): Second Q-value estimate, shape (B*N, 1).
                mean_entropy (Tensor): Mean soft-attention entropy (scalar tensor).
                hard_logits (Tensor): Hard attention logits, shape (B*N, N-1).
                unnorm_rel_dist (Tensor): Unnormalized pairwise distances, shape (B*N, N-1, 1).
                hard_weights (Tensor): Binary hard attention mask, shape (B, N, N).
        """

        (  # 多行解包 critic 注意力的六元组输出
            embedding_with_attention,  # 各 agent 注意力嵌入 (B*N,512)
            hard_logits,  # 硬注意力 logits (B*N,N-1)：通信边连通性打分
            unnorm_rel_dist,  # 未归一化成对距离 (B*N,N-1,1)：BCE 正类标签来源
            mean_entropy,  # 软注意力分布平均熵（标量）：正则项
            hard_weights,  # 硬注意力门控权重 (B,N,N)：>0.5 视为有边
            _,  # 联合软权重此处不需要，占位丢弃
        ) = self.attention(embedding)  # 跑 critic 自己的注意力：全队观测→逐 agent 嵌入+诊断量

        # Q1 ｜ 第一条 Q 支路
        s1 = F.leaky_relu(self.layer_1(embedding_with_attention))  # 状态支路：512→400 再激活，得 (B*N,400)
        s1 = F.leaky_relu(self.layer_2_s(s1) + self.layer_2_a(action))  # ✅ No .data ｜ 状态流(400→300)+动作流(2→300) 相加再激活（✅为原注）
        q1 = self.layer_3(s1)  # Q1 输出头：(B*N,300)→(B*N,1)

        # Q2 ｜ 第二条 Q 支路（同构但参数独立）
        s2 = F.leaky_relu(self.layer_4(embedding_with_attention))  # Q2 状态支路：与 Q1 共用嵌入、权重独立
        s2 = F.leaky_relu(self.layer_5_s(s2) + self.layer_5_a(action))  # ✅ No .data ｜ 同款双流融合
        q2 = self.layer_6(s2)  # Q2 输出头 (B*N,1)

        return q1, q2, mean_entropy, hard_logits, unnorm_rel_dist, hard_weights  # 双 Q+诊断量；取 min 防高估在 train() 里做


# ============================【类】TD3：多智能体 TD3 智能体外壳 ============================ #
# 职责：TD3（Twin Delayed DDPG）=确定性策略的 off-policy actor-critic（DDPG）加三件套：
#       ① twin critic 取 min 防 Q 高估；② 目标动作加截断噪声（目标策略平滑）；③ 策略延迟更新。
# 本实现的多智能体化：不建 N 份网络，actor/critic 各一套、N 个 agent 共享参数，靠注意力
#       按观测区分彼此；训练集中（全队状态入 critic）、执行分散（逐 agent 前向）=CTDE 范式。
class TD3(object):  # 智能体外壳：网络+优化器+训练循环+日志+存档（普通容器类，非 nn.Module）
    """
    Twin Delayed DDPG (TD3) agent for multi-agent continuous control.

    Wraps actor/critic networks, exploration policy, training loop, logging, and
    checkpointing utilities.

    Args:
        state_dim (int): Per-agent state dimension.
        action_dim (int): Per-agent action dimension.
        max_action (float): Action clip magnitude (actions are clipped to [-max_action, max_action]).
        device (torch.device): Target device for models and tensors.
        num_robots (int): Number of agents.
        lr_actor (float, optional): Actor learning rate. Defaults to 1e-4.
        lr_critic (float, optional): Critic learning rate. Defaults to 3e-4.
        save_every (int, optional): Save frequency in training iterations (0 = disabled). Defaults to 0.
        load_model (bool, optional): If True, loads weights on init. Defaults to False.
        save_directory (Path, optional): Directory for saving checkpoints.
        model_name (str, optional): Base filename for checkpoints. Defaults to "marlTD3".
        load_model_name (str or None, optional): Filename base to load. Defaults to None (uses model_name).
        load_directory (Path, optional): Directory to load checkpoints from.
        attention (str, optional): Attention backend, one of {"igs", "g2anet"}. Defaults to "igs".

    Attributes:
        actor (Actor): Policy network.
        actor_target (Actor): Target policy network.
        critic (Critic): Twin Q-value network.
        critic_target (Critic): Target critic network.
        actor_optimizer (torch.optim.Optimizer): Optimizer over attention + policy head.
        critic_optimizer (torch.optim.Optimizer): Optimizer over critic.
        writer (SummaryWriter): TensorBoard writer.
        iter_count (int): Training iteration counter for logging/saving.
        save_every (int): Save frequency.
        model_name (str): Base filename for checkpoints.
        save_directory (Path): Directory for saving checkpoints.
    """

    # 【方法】__init__：建网、复制 target、配优化器
    # 输入：state_dim=11、action_dim=2、max_action、device、num_robots=N 及训练/存档超参；
    # 关键动作：actor/critic 各建两份（在线+target，target 仅用来稳定 TD 目标），
    #           初始 target←原样复制在线权重；两个 Adam 分别管 actor（注意力+策略头）与 critic。
    def __init__(  # 构造函数签名（参数多，换行书写）
        self,  # 实例自身
        state_dim,  # 单 agent 状态维数（本任务 11，见 prepare_state）
        action_dim,  # 单 agent 动作维数（2：线速度+角速度）
        max_action,  # 动作幅值上限（交互时裁剪边界）
        device,  # 计算设备（cpu/cuda）
        num_robots,  # 智能体数量 N：train() 里所有 reshape 的多智能体维度来源
        lr_actor=1e-4,  # actor 学习率（TD3 惯例比 critic 小一个量级，策略更新更稳）
        lr_critic=3e-4,  # critic 学习率
        save_every=0,  # 每 N 轮训练自动存档（0=关闭）
        load_model=False,  # 是否初始化时加载旧权重
        save_directory=Path("robot_nav/models/MARL/marlTD3/checkpoint"),  # 存档目录默认值
        model_name="marlTD3",  # 存档文件名前缀
        load_model_name=None,  # 加载用文件名前缀（None 则沿用 model_name）
        load_directory=Path("robot_nav/models/MARL/marlTD3/checkpoint"),  # 加载目录默认值
        attention="igs",  # 注意力后端，默认 IGA
    ):  # 签名结束
        # Initialize the Actor network ｜ 开始搭建 Actor（原注）
        if attention not in ["igs", "g2anet"]:  # 提前校验注意力类型合法性
            raise ValueError("unknown attention mechanism specified for TD3 model")  # 非法类型抛异常
        self.num_robots = num_robots  # 记住 agent 数 N：train() 的 view() 全靠它
        self.device = device  # 记住设备：所有张量的搬运目的地
        self.actor = Actor(action_dim, embedding_dim=256, attention=attention).to(  # 在线 actor：嵌入维固定 256，搬到 device
            self.device  # .to() 的设备参数（换行写法）
        )  # Using the updated Actor ｜ 原注：使用新版 Actor
        self.actor_target = Actor(  # 目标 actor：结构同款、参数独立（软更新缓慢跟随）
            action_dim, embedding_dim=256, attention=attention  # 同一套超参建第二份
        ).to(self.device)  # 搬到 device；target 只用于算 TD 目标，不直接参与梯度下降
        self.actor_target.load_state_dict(self.actor.state_dict())  # 初始把在线权重原样复制给 target（两者起步一致）

        self.attn_params = list(self.actor.attention.parameters())  # 收集 actor 注意力模块参数（单独成组便于区分/裁剪）
        self.policy_params = list(self.actor.policy_head.parameters())  # 收集 actor 策略头参数（与注意力参数同入一个优化器）

        self.actor_optimizer = torch.optim.Adam(  # actor 优化器：Adam
            self.policy_params + self.attn_params, lr=lr_actor  # 策略头+注意力参数拼接后一起优化
        )  # TD3 policy ｜ 原注：TD3 策略优化器

        self.critic = Critic(action_dim, embedding_dim=256, attention=attention).to(  # 在线 critic：双 Q+自带注意力
            self.device  # 设备参数换行
        )  # Using the updated Critic ｜ 原注：使用新版 Critic
        self.critic_target = Critic(  # 目标 critic：算 TD 目标用
            action_dim, embedding_dim=256, attention=attention  # 同参建第二份
        ).to(self.device)  # 搬到 device
        self.critic_target.load_state_dict(self.critic.state_dict())  # 初始复制在线 critic 权重
        self.critic_optimizer = torch.optim.Adam(  # critic 优化器
            params=self.critic.parameters(), lr=lr_critic  # critic 全部参数（含其注意力模块）
        )  # 优化器构建收尾
        self.action_dim = action_dim  # 记录动作维：train() reshape 用
        self.max_action = max_action  # 记录动作上限：噪声/动作裁剪用
        self.state_dim = state_dim  # 记录状态维：train() reshape 用
        self.writer = SummaryWriter(comment=model_name)  # TensorBoard 写入器：曲线名带模型名以区分 run
        self.iter_count = 0  # 训练轮次计数器（注意：每次 train() 调用+1，非每梯度步）
        if load_model_name is None:  # 未单独指定加载名
            load_model_name = model_name  # 沿用默认模型名
        if load_model:  # 要求恢复旧权重
            self.load(filename=load_model_name, directory=load_directory)  # 从磁盘载入四份网络权重
        self.save_every = save_every  # 存档频率
        self.model_name = model_name  # 存档名
        self.save_directory = save_directory  # 存档目录

    # 【方法】get_action：环境交互用的带噪动作（执行端入口，含探索）
    # 输入：obs (N,state_dim) 或 (B,N,state_dim)、add_noise 是否加探索噪声；
    # 输出：action (N,2)、硬注意力 logits、软注意力权重。
    # 教学点：探索=高斯噪声叠加在确定性动作上；角速度分量噪声再除以 4（转向探索更保守）。
    def get_action(self, obs, add_noise):  # 对外取动作接口
        """
        Compute an action for the given observation, with optional exploration noise.

        Args:
            obs (np.ndarray): Observation array of shape (N, state_dim) or (B, N, state_dim).
            add_noise (bool): If True, adds Gaussian exploration noise and clips to bounds.

        Returns:
            tuple:
                action (np.ndarray): Actions reshaped to (N, action_dim).
                connection_logits (Tensor): Hard attention logits from the actor.
                combined_weights (Tensor): Soft attention weights per (receiver, sender).
        """
        action, connection, combined_weights = self.act(obs)  # 先走确定性策略拿动作与注意力量
        if add_noise:  # 需要探索时加噪
            noise = np.random.normal(0, 0.5, size=action.shape)  # 高斯噪声 σ=0.5，形状对齐展平动作 (N*2,)
            noise = [n / 4 if i % 2 else n for i, n in enumerate(noise)]  # 展平序 [lin,ang,lin,ang,...]：奇数位=角速度，噪声除以 4（σ≈0.125）
            action = (action + noise).clip(-self.max_action, self.max_action)  # 叠噪后裁剪回 [-max_action, max_action]

        return action.reshape(-1, 2), connection, combined_weights  # 整形 (N,2)：每行 [线速度,角速度]

    # 【方法】act：纯确定性动作（无噪声）
    # 输入：state (N,state_dim)；输出：展平动作 (N*action_dim,) + 硬 logits + 软权重。
    # 位置：get_action 与评估共用；numpy→tensor→网络→numpy 一次往返。
    def act(self, state):  # 确定性前向
        """
        Compute the deterministic action from the current policy.

        Args:
            state (np.ndarray): Observation array of shape (N, state_dim).

        Returns:
            tuple:
                action (np.ndarray): Flattened action vector of shape (N*action_dim,).
                connection_logits (Tensor): Hard attention logits from the actor.
                combined_weights (Tensor): Soft attention weights per (receiver, sender).
        """
        # Function to get the action from the actor ｜ 从 actor 取动作（原注）
        state = torch.Tensor(state).to(self.device)  # numpy→张量→device，形状 (N,state_dim)
        # res = self.attention(state) ｜ 遗留注释：旧版直接调注意力的写法已废弃（原注保留）
        action, connection, _, _, _, combined_weights = self.actor(state)  # actor 前向（默认 detach_attn=False）：动作 (N,2)+硬 logits+软权重
        return action.cpu().data.numpy().flatten(), connection, combined_weights  # 回 CPU 转 numpy 并展平为 (N*2,)

    # training cycle ｜ 训练循环入口（原注）
    # 【方法】train：TD3 训练循环（一次调用=iterations 个梯度步）
    # 输入：replay_buffer（sample_batch 给五元组）、batch_size、TD3 超参（γ/τ/平滑噪声/延迟频率）
    #       及注意力正则权重（BCE/熵/邻接阈值/梯度裁剪）；
    # 流程：采样→view 还原 N 维→目标动作加平滑噪声→双 Q 取 min 得 TD 目标→critic 回归+正则
    #       →每 policy_freq 步更新 actor→软更新两套 target 网络。
    def train(  # 训练主循环签名（参数多，分行）
        self,  # 实例自身
        replay_buffer,  # 经验回放池：存历史 (s,a,r,done,s')，随机抽批打破样本时间相关性
        iterations,  # 本次调用的梯度步数
        batch_size,  # 小批量大小 B
        discount=0.99,  # 折扣因子 γ：未来奖励每步打 99 折（权衡眼前/长远）
        tau=0.005,  # 软更新系数 τ：target←τ·online+(1-τ)·target，小步跟随保稳定
        policy_noise=0.2,  # 目标策略平滑噪声标准差（TD3 三件套之二）
        noise_clip=0.5,  # 平滑噪声裁剪幅值（防平滑变破坏）
        policy_freq=2,  # 策略延迟更新频率：每 2 次 critic 步做 1 次 actor 步（TD3 三件套之三）
        bce_weight=0.01,  # 硬注意力 BCE 辅助损失权重（邻接几何监督）
        entropy_weight=1,  # 软注意力熵奖励权重（鼓励注意力分布别过早塌缩到单一邻居）
        connection_proximity_threshold=4,  # 邻接判定距离阈值：<4 视为"有通信边"（BCE 正类）
        max_grad_norm=7.0,  # 梯度全局范数裁剪上限（防梯度爆炸）
    ):  # 签名结束
        """
        Run a TD3 training loop over sampled mini-batches.

        Args:
            replay_buffer: Buffer supporting ``sample_batch(batch_size)`` -> tuple of arrays.
            iterations (int): Number of gradient steps.
            batch_size (int): Mini-batch size.
            discount (float, optional): Discount factor γ. Defaults to 0.99.
            tau (float, optional): Target network update rate. Defaults to 0.005.
            policy_noise (float, optional): Std of target policy noise. Defaults to 0.2.
            noise_clip (float, optional): Clipping range for target noise. Defaults to 0.5.
            policy_freq (int, optional): Actor update period (in critic steps). Defaults to 2.
            bce_weight (float, optional): Weight for hard-connection BCE loss. Defaults to 0.01.
            entropy_weight (float, optional): Weight for attention entropy bonus. Defaults to 1.
            connection_proximity_threshold (float, optional): Distance threshold for the
                positive class when supervising hard connections. Defaults to 4.
            max_grad_norm (float, optional): Gradient clipping norm. Defaults to 7.0.

        Returns:
            None
        """
        av_Q = 0  # 平均目标 Q 累计器（日志用）
        max_Q = -inf  # 最大目标 Q 记录，初始化 -inf 保证首轮必被刷新
        av_loss = 0  # 总损失累计器
        av_critic_loss = 0  # critic MSE 损失累计器
        av_critic_entropy = []  # critic 注意力熵列表（每步 append 张量）
        av_actor_entropy = []  # actor 注意力熵列表（仅 actor 更新步有样本）
        av_actor_loss = 0  # actor 损失累计器
        av_critic_bce_loss = []  # critic BCE 损失列表
        av_actor_bce_loss = []  # actor BCE 损失列表

        for it in range(iterations):  # 主循环：每轮做一次 minibatch 梯度更新
            # sample a batch ｜ 从回放池采样一批经验（原注）
            (  # 五元组多行解包开始
                batch_states,  # 批状态 (B, N*state_dim)：N 个 agent 的状态展平存储
                batch_actions,  # 批动作 (B, N*action_dim)：同样展平存储
                batch_rewards,  # 批奖励 (B, N)：每个 agent 有各自的奖励信号
                batch_dones,  # 批结束标志 (B, N)：逐 agent 的终止信号
                batch_next_states,  # 批下一状态 (B, N*state_dim)
            ) = replay_buffer.sample_batch(batch_size)  # 随机抽 B 条 transition（打破时间相关性）

            state = (  # 当前状态张量化+还原 N 维
                torch.Tensor(batch_states)  # numpy→张量
                .to(self.device)  # 搬到 device
                .view(batch_size, self.num_robots, self.state_dim)  # 还原多智能体形状 (B,N,11)：N 轴是注意力聚合的维度
            )  # state 构建收尾
            next_state = (  # 下一状态同款处理
                torch.Tensor(batch_next_states)  # numpy→张量
                .to(self.device)  # 搬到 device
                .view(batch_size, self.num_robots, self.state_dim)  # 还原 (B,N,11)
            )  # next_state 收尾
            action = (  # 动作张量化
                torch.Tensor(batch_actions)  # numpy→张量
                .to(self.device)  # 搬到 device
                .view(batch_size * self.num_robots, self.action_dim)  # 摊平 batch×agent：(B*N,2)，逐 agent 配对
            )  # action 收尾
            reward = (  # 奖励张量化
                torch.Tensor(batch_rewards)  # numpy→张量
                .to(self.device)  # 搬到 device
                .view(batch_size * self.num_robots, 1)  # 逐 agent 奖励 (B*N,1)：与 Q 值一一对应
            )  # reward 收尾
            done = (  # 结束标志张量化
                torch.Tensor(batch_dones)  # numpy→张量
                .to(self.device)  # 搬到 device
                .view(batch_size * self.num_robots, 1)  # 逐 agent done (B*N,1)：终止时掐断 bootstrap
            )  # done 收尾

            with torch.no_grad():  # 目标计算不需要梯度：省显存、防梯度回传
                next_action, _, _, _, _, _ = self.actor_target(  # 目标 actor 给下一状态出动作
                    next_state, detach_attn=True  # detach_attn=True：注意力特征切断梯度
                )  # actor_target 前向收尾

            # --- Target smoothing --- ｜ 目标策略平滑（TD3 三件套之二，原注）
            noise = (  # 构造平滑噪声张量
                torch.Tensor(batch_actions)  # 借 batch_actions 的形状开张量（数值将被覆盖）
                .data.normal_(0, policy_noise)  # 原地填入 N(0,0.2)：省一次构造拷贝
                .to(self.device)  # 搬到 device
            ).reshape(-1, 2)  # 整形 (B*N,2)，与 next_action 对齐
            noise = noise.clamp(-noise_clip, noise_clip)  # 噪声裁剪到 ±0.5：平滑而非破坏目标动作
            next_action = (next_action + noise).clamp(-self.max_action, self.max_action)  # 加噪目标动作再裁回合法范围

            # --- Target Q values --- ｜ TD 目标=即时奖励+γ·min(双Q)（原注）
            target_Q1, target_Q2, _, _, _, _ = self.critic_target(  # 目标 critic 对 (s',a') 算双 Q
                next_state, next_action  # 输入：全队下一状态+平滑后的目标动作
            )  # 目标 critic 前向收尾
            target_Q = torch.min(target_Q1, target_Q2)  # TD3 核心：双 Q 取 min——悲观估计压制 Q 高估（三件套之一）
            av_Q += target_Q.mean()  # 累计平均 Q（日志用；此处未 .item()，张量带计算图，轻微占显存）
            max_Q = max(max_Q, target_Q.max().item())  # 刷新最大 Q 记录（.item() 转纯数）
            target_Q = reward + ((1 - done) * discount * target_Q).detach()  # Bellman 目标 y=r+(1-done)·γ·minQ；detach=固定回归靶子

            # --- Critic update --- ｜ critic 回归拟合 TD 目标（原注）
            (  # 在线 critic 前向解包开始
                current_Q1,  # 在线 Q1 (B*N,1)
                current_Q2,  # 在线 Q2 (B*N,1)
                mean_entropy,  # 软注意力熵（正则用）
                hard_logits,  # 硬注意力 logits（BCE 用）
                unnorm_rel_dist,  # 成对距离（BCE 正类标签来源）
                hard_weights,  # 硬掩码（此处解包但未使用）
            ) = self.critic(state, action)  # 用实际执行的 (s,a) 前向
            critic_loss = F.mse_loss(current_Q1, target_Q) + F.mse_loss(  # 双 Q 各自向 y 回归，两个 MSE 相加（TD3 联合损失）
                current_Q2, target_Q  # Q2 同样回归（换行续写 F.mse_loss 参数）
            )  # critic_loss 收尾

            targets = (  # BCE 正类标签构造
                unnorm_rel_dist.flatten() < connection_proximity_threshold  # 距离<4 →True：agent 对间"物理邻近可通信"
            ).float()  # 布尔→0/1 浮点
            flat_logits = hard_logits.flatten()  # 硬 logits 摊平，与标签逐元素对齐
            bce_loss = F.binary_cross_entropy_with_logits(flat_logits, targets)  # 监督硬注意力：通信边预测对齐几何邻近（自监督信号）

            av_critic_bce_loss.append(bce_loss)  # 记录 BCE（日志用）

            total_loss = (  # critic 总损失合成
                critic_loss - entropy_weight * mean_entropy + bce_weight * bce_loss  # MSE−熵奖励+加权BCE：负号=最大化软注意力熵防塌缩
            )  # total_loss 收尾
            av_critic_entropy.append(mean_entropy)  # 记录熵（日志用）

            self.critic_optimizer.zero_grad()  # 清旧梯度（PyTorch 梯度默认累加，须手动清零）
            total_loss.backward()  # 反向传播（对 critic 全部参数，含其注意力）
            torch.nn.utils.clip_grad_norm_(self.critic.parameters(), max_grad_norm)  # 全参数梯度范数裁剪防爆
            self.critic_optimizer.step()  # Adam 更新 critic

            av_loss += total_loss.item()  # 累计总损失（.item() 转纯数）
            av_critic_loss += critic_loss.item()  # 累计 critic MSE

            # --- Actor update --- ｜ 延迟策略更新（TD3 三件套之三，原注）
            if it % policy_freq == 0:  # 每 policy_freq 个 critic 步才动一次 actor

                action, hard_logits, unnorm_rel_dist, mean_entropy, hard_weights, _ = (  # actor 对当前状态重算动作（可微路径，梯度要流经 critic 回到 actor）
                    self.actor(state, detach_attn=False)  # detach_attn=False：注意力特征保留梯度
                )  # actor 前向收尾
                targets = (  # actor 侧 BCE 标签（与 critic 同口径）
                    unnorm_rel_dist.flatten() < connection_proximity_threshold  # 距离阈值判邻接
                ).float()  # 转 0/1 浮点
                flat_logits = hard_logits.flatten()  # actor 硬 logits 摊平
                bce_loss = F.binary_cross_entropy_with_logits(flat_logits, targets)  # actor 的注意力同样受邻接监督

                av_actor_bce_loss.append(bce_loss)  # 记录（日志用）

                actor_Q, _, _, _, _, _ = self.critic(state, action)  # 用在线 critic（非 target）给新动作打分——只取 Q1；策略梯度经 critic 流回 actor
                actor_loss = -actor_Q.mean()  # 最大化 Q ⟺ 最小化 -Q（DDPG 式确定性策略梯度）
                total_loss = (  # actor 总损失
                    actor_loss - entropy_weight * mean_entropy + bce_weight * bce_loss  # −Q−熵奖励+加权BCE（熵来自 actor 自己的注意力）
                )  # actor total_loss 收尾
                av_actor_entropy.append(mean_entropy)  # 记录熵（日志用）

                self.actor_optimizer.zero_grad()  # 清 actor 侧梯度
                total_loss.backward()  # 反传：也会给 critic 参数写入梯度，但下轮 critic zero_grad 会清掉，不会误更新 critic
                torch.nn.utils.clip_grad_norm_(self.policy_params, max_grad_norm)  # 只裁策略头参数（注意力参数未裁——与 critic 侧全裁不对称，留意）
                self.actor_optimizer.step()  # 更新策略头+注意力参数

                av_actor_loss += total_loss.item()  # 累计 actor 损失

                # Soft update target networks ｜ 软更新（EMA 式）两套 target 网络（原注）
                for param, target_param in zip(  # 遍历在线/target 参数对
                    self.actor.parameters(), self.actor_target.parameters()  # actor 两份网络逐参数配对
                ):  # zip 参数列表收尾
                    target_param.data.copy_(  # 目标参数原地写入
                        tau * param.data + (1 - tau) * target_param.data  # target←0.005·online+0.995·target：小步跟随，稳住 TD 目标
                    )  # copy_ 收尾

                for param, target_param in zip(  # 同款软更新用于 critic
                    self.critic.parameters(), self.critic_target.parameters()  # critic 两份网络逐参数配对
                ):  # zip 参数列表收尾
                    target_param.data.copy_(  # 目标参数原地写入
                        tau * param.data + (1 - tau) * target_param.data  # 同一 τ 混合：双 Q 的 target 也只小幅跟进
                    )  # copy_ 收尾

        self.iter_count += 1  # 训练轮次+1（注意粒度：一次 train() 调用记 1 轮，非单个梯度步）
        self.writer.add_scalar(  # 写 TensorBoard 标量
            "train/loss_total", av_loss / iterations, self.iter_count  # 总损失均值 vs 轮次
        )  # add_scalar 收尾
        self.writer.add_scalar(  # 写标量
            "train/critic_loss", av_critic_loss / iterations, self.iter_count  # critic MSE 均值
        )  # add_scalar 收尾
        self.writer.add_scalar(  # 写标量
            "train/av_critic_entropy",  # critic 注意力熵曲线名
            sum(av_critic_entropy) / len(av_critic_entropy),  # 熵张量求和/计数=均值
            self.iter_count,  # x 轴=轮次
        )  # add_scalar 收尾
        self.writer.add_scalar(  # 写标量
            "train/av_actor_entropy",  # actor 注意力熵曲线名
            sum(av_actor_entropy) / len(av_actor_entropy),  # 熵均值（仅 actor 更新步有样本）
            self.iter_count,  # x 轴=轮次
        )  # add_scalar 收尾
        self.writer.add_scalar(  # 写标量
            "train/av_critic_bce_loss",  # critic BCE 曲线名
            sum(av_critic_bce_loss) / len(av_critic_bce_loss),  # BCE 均值
            self.iter_count,  # x 轴=轮次
        )  # add_scalar 收尾
        self.writer.add_scalar(  # 写标量
            "train/av_actor_bce_loss",  # actor BCE 曲线名
            sum(av_actor_bce_loss) / len(av_actor_bce_loss),  # BCE 均值
            self.iter_count,  # x 轴=轮次
        )  # add_scalar 收尾
        self.writer.add_scalar("train/avg_Q", av_Q / iterations, self.iter_count)  # 平均目标 Q（监控 Q 高估的关键曲线）
        self.writer.add_scalar("train/max_Q", max_Q, self.iter_count)  # 最大目标 Q

        self.writer.add_scalar(  # 写标量
            "train/actor_loss",  # actor 损失曲线名
            av_actor_loss / (iterations // policy_freq),  # 除以 actor 实际更新次数（iterations//policy_freq）
            self.iter_count,  # x 轴=轮次
        )  # add_scalar 收尾

        if self.save_every > 0 and self.iter_count % self.save_every == 0:  # 到达存档频率则落盘
            self.save(filename=self.model_name, directory=self.save_directory)  # 保存四份网络权重

    # 【方法】save：存四份权重（actor/critic × 在线/target）
    # 输入：filename 名字前缀、directory 目录；输出：4 个 .pth 权重文件。
    # 位置：训练中按 save_every 周期调用，或评估前手动调用。
    def save(self, filename, directory):  # 存档入口
        """
        Saves the current model parameters to the specified directory.

        Args:
            filename (str): Base filename for saved files.
            directory (Path): Path to save the model files.
        """
        Path(directory).mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在不报错）
        torch.save(self.actor.state_dict(), "%s/%s_actor.pth" % (directory, filename))  # 存在线 actor 权重
        torch.save(  # 存目标 actor 权重
            self.actor_target.state_dict(),  # target 状态字典
            "%s/%s_actor_target.pth" % (directory, filename),  # 文件名=前缀+_actor_target.pth
        )  # torch.save 收尾
        torch.save(self.critic.state_dict(), "%s/%s_critic.pth" % (directory, filename))  # 存在线 critic 权重
        torch.save(  # 存目标 critic 权重
            self.critic_target.state_dict(),  # target 状态字典
            "%s/%s_critic_target.pth" % (directory, filename),  # 文件名=前缀+_critic_target.pth
        )  # torch.save 收尾

    # 【方法】load：恢复四份权重（与 save 一一对应）
    # 输入：filename 名字前缀、directory 目录；输出：无（原地覆盖四份网络参数）。
    def load(self, filename, directory):  # 加载入口
        """
        Loads model parameters from the specified directory.

        Args:
            filename (str): Base filename for saved files.
            directory (Path): Path to load the model files from.
        """
        self.actor.load_state_dict(  # 载入在线 actor
            torch.load("%s/%s_actor.pth" % (directory, filename))  # 从 .pth 反序列化
        )  # load_state_dict 收尾
        self.actor_target.load_state_dict(  # 载入目标 actor
            torch.load("%s/%s_actor_target.pth" % (directory, filename))  # 对应文件
        )  # load_state_dict 收尾
        self.critic.load_state_dict(  # 载入在线 critic
            torch.load("%s/%s_critic.pth" % (directory, filename))  # 对应文件
        )  # load_state_dict 收尾
        self.critic_target.load_state_dict(  # 载入目标 critic
            torch.load("%s/%s_critic_target.pth" % (directory, filename))  # 对应文件
        )  # load_state_dict 收尾
        print(f"Loaded weights from: {directory}")  # 打印加载来源目录

    # 【方法】prepare_state：环境原始量→11 维状态向量（感知端特征工程）
    # 输入：poses/distance/cos/sin/collision/action/goal_positions（均为长度 N 的逐 agent 列表）；
    # 输出：states（每 agent 11 维列表）、terminal（逐 agent 终止标志）。
    # 位置：喂给 actor/critic 注意力前的最后一步——注意力模块按此 11 维布局切片取位置/朝向/动作/目标。
    def prepare_state(  # 状态组装签名（参数多，分行）
        self, poses, distance, cos, sin, collision, action, goal_positions  # 七个逐 agent 列表参数
    ):  # 签名收尾
        """
        Convert raw environment outputs into per-agent state vectors.

        Args:
            poses (list): Per-agent poses [[x, y, theta], ...].
            distance (list): Per-agent distances to goal.
            cos (list): Per-agent cos(heading error to goal).
            sin (list): Per-agent sin(heading error to goal).
            collision (list): Per-agent collision flags (bool or {0,1}).
            action (list): Per-agent last actions [[lin_vel, ang_vel], ...].
            goal_positions (list): Per-agent goals [[gx, gy], ...].

        Returns:
            tuple:
                states (list): Per-agent state vectors (length == state_dim).
                terminal (list): Terminal flags (collision or goal), same length as states.
        """
        states = []  # 收集各 agent 的状态向量
        terminal = []  # 收集各 agent 的终止标志

        for i in range(self.num_robots):  # 逐个 agent 组装（循环 N 次）
            pose = poses[i]  # [x, y, theta] ｜ 取第 i 个位姿
            goal_pos = goal_positions[i]  # [goal_x, goal_y] ｜ 取第 i 个目标点
            act = action[i]  # [lin_vel, ang_vel] ｜ 取上一步动作

            px, py, theta = pose  # 解包位置与朝向角
            gx, gy = goal_pos  # 解包目标坐标

            # Heading as cos/sin ｜ 朝向用 cos/sin 编码（原注）
            heading_cos = np.cos(theta)  # cos(θ)：角度→连续特征，避免 ±π 处跳变
            heading_sin = np.sin(theta)  # sin(θ)：与 cos 联合唯一确定朝向

            # Last velocity ｜ 上一步速度（重缩放后入状态，原注）
            lin_vel = act[0] * 2  # Assuming original range [0, 0.5] ｜ 重缩放到 [0,1]
            ang_vel = (act[1] + 1) / 2  # Assuming original range [-1, 1] ｜ 重缩放到 [0,1]

            # Final state vector ｜ 拼 11 维状态向量（原注）
            state = [  # 列表字面量开始
                px,  # 1/11：位置 x
                py,  # 2/11：位置 y
                heading_cos,  # 3/11：自身朝向 cos
                heading_sin,  # 4/11：自身朝向 sin
                distance[i] / 17,  # 5/11：目标距离/17 归一化（17≈场地尺度）
                cos[i],  # 6/11：指向目标的航向误差 cos
                sin[i],  # 7/11：指向目标的航向误差 sin
                lin_vel,  # 8/11：上步线速度（已归一化）
                ang_vel,  # 9/11：上步角速度（已归一化）
                gx,  # 10/11：目标点 x
                gy,  # 11/11：目标点 y
            ]  # 状态列表结束

            assert (  # 维度守恒断言开始
                len(state) == self.state_dim  # 硬校验：拼出的维数必须等于 state_dim
            ), f"State length mismatch: expected {self.state_dim}, got {len(state)}"  # 断言失败提示（打印期望/实际）
            states.append(state)  # 收进批次列表
            terminal.append(collision[i])  # 终止=碰撞标志（注意：docstring 写 collision or goal，代码实际只取 collision）

        return states, terminal  # 返回状态批次与终止标志（喂回训练循环）
