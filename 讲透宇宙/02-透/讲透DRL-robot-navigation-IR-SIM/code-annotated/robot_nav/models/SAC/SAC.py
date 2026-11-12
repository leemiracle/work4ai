from pathlib import Path  # 路径工具：checkpoint 目录创建与默认路径

import numpy as np  # NumPy：环境侧数组处理（观测转张量、动作加噪、雷达状态编码）
import torch  # PyTorch 主库：张量 + 自动微分
import torch.nn.functional as F  # 函数式接口：F.mse_loss 等（与 PPO 的 nn.MSELoss 等价）
from statistics import mean  # 纯 Python 均值：对 metrics 列表求平均写 TensorBoard
import robot_nav.models.SAC.SAC_utils as utils  # SAC 工具箱：to_np（张量转 numpy）、soft_update_params（软更新）等
from robot_nav.models.SAC.SAC_critic import DoubleQCritic as critic_model  # 双 Q 评论家网络（twin Q 结构定义在 SAC_critic.py）
from robot_nav.models.SAC.SAC_actor import DiagGaussianActor as actor_model  # 对角高斯演员网络（输出经 Tanh 压缩的分布对象）
from torch.utils.tensorboard import SummaryWriter  # TensorBoard 日志写手


# SAC：Soft Actor-Critic"最大熵"软演员-评论家主控制器（off-policy）。
# 目标函数 J = E[Σ γ^t (r_t + α·H(π(·|s_t)))]：不只追回报，还奖励策略熵（随机性）——
# 熵项让策略保持多样探索、对扰动更鲁棒；α（温度）控制"回报 vs 熵"的权衡，且可自动调。
# 流程：replay buffer 随机抽批 → 更新 critic（软贝尔曼靶 + 双 Q 取 min）→ 更新 actor（重参数化）→ 调 α → 软更新目标网。
# 与 PPO 的分水岭：数据来自 replay buffer 随机采样可无限复用（off-policy），无 policy_old / clip / 清 buffer 概念。
class SAC(object):  # SAC 主控制器（off-policy 最大熵算法）
    """
    Soft Actor-Critic (SAC) implementation.

    This class implements the SAC algorithm using a Gaussian policy actor and double Q-learning critic.
    It supports automatic entropy tuning, model saving/loading, and logging via TensorBoard.

    Args:
        state_dim (int): Dimension of the observation/state space.
        action_dim (int): Dimension of the action space.
        device (torch.device): PyTorch device (e.g., 'cpu' or 'cuda').
        max_action (float): Maximum magnitude of actions.
        discount (float): Discount factor for rewards.
        init_temperature (float): Initial entropy temperature.
        alpha_lr (float): Learning rate for entropy temperature alpha.
        alpha_betas (tuple): Adam optimizer betas for alpha.
        actor_lr (float): Learning rate for actor network.
        actor_betas (tuple): Adam optimizer betas for actor.
        actor_update_frequency (int): Frequency of actor updates.
        critic_lr (float): Learning rate for critic network.
        critic_betas (tuple): Adam optimizer betas for critic.
        critic_tau (float): Soft update parameter for critic target.
        critic_target_update_frequency (int): Frequency of critic target updates.
        learnable_temperature (bool): Whether alpha is learnable.
        save_every (int): Save model every N training steps. Set 0 to disable.
        load_model (bool): Whether to load model from disk at init.
        log_dist_and_hist (bool): Log distribution and histogram if True.
        save_directory (Path): Directory to save models.
        model_name (str): Name for model checkpoints.
        load_directory (Path): Directory to load model checkpoints from.
    """

    # 构造函数：建三个网络（actor / critic / critic_target）+ 三个独立优化器 + α 与目标熵。
    # 与 PPO 的三处结构差异：① critic 吃 (s,a) 而非只吃 s；② 多一个慢速跟随的目标网络；
    # ③ actor 输出"分布参数"（μ, log σ）而非动作本身，采样在训练时由 rsample 完成
    # 默认超参沿用官方 SAC 实现：lr=1e-4、τ=0.005、目标熵=-|A|
    def __init__(  # 多行签名开始
        self,  # 实例自身
        state_dim,  # 状态维数
        action_dim,  # 动作维数（决定目标熵 -|A|）
        device,  # 计算设备
        max_action,  # 动作幅值上界（裁剪用）
        discount=0.99,  # 折扣因子 γ：未来奖励逐期打折
        init_temperature=0.1,  # α 初值：熵温度，奖励与熵的权衡系数
        alpha_lr=1e-4,  # α 的学习率
        alpha_betas=(0.9, 0.999),  # α 的 Adam 动量参数
        actor_lr=1e-4,  # actor 学习率
        actor_betas=(0.9, 0.999),  # actor 的 Adam 动量参数
        actor_update_frequency=1,  # 每几步更新一次 actor（1=每步都更）
        critic_lr=1e-4,  # critic 学习率
        critic_betas=(0.9, 0.999),  # critic 的 Adam 动量参数
        critic_tau=0.005,  # 目标网软更新系数 τ（很小的插值比例=慢跟随）
        critic_target_update_frequency=2,  # 每几步软更新一次目标网（延迟更新）
        learnable_temperature=True,  # α 是否可学习（自动熵调温开关）
        save_every=0,  # 每几步存 checkpoint（0=关闭）
        load_model=False,  # 是否断点续训
        log_dist_and_hist=False,  # 是否记录网络参数直方图
        save_directory=Path("robot_nav/models/SAC/checkpoint"),  # 保存目录
        model_name="SAC",  # 模型名
        load_directory=Path("robot_nav/models/SAC/checkpoint"),  # 加载目录
    ):  # 构造函数签名收尾
        super().__init__()  # 父类 object 初始化（形式调用）

        self.state_dim = state_dim  # 存状态维数
        self.action_dim = action_dim  # 存动作维数
        self.action_range = (-max_action, max_action)  # 动作区间元组：供 clamp(*range) 与 np.clip 使用
        self.device = device  # 存设备
        self.discount = discount  # 存 γ
        self.critic_tau = critic_tau  # 存软更新 τ
        self.actor_update_frequency = actor_update_frequency  # 存 actor 更新频率
        self.critic_target_update_frequency = critic_target_update_frequency  # 存目标网更新频率
        self.learnable_temperature = learnable_temperature  # 存 α 可学开关
        self.save_every = save_every  # 存保存间隔
        self.model_name = model_name  # 存模型名
        self.save_directory = save_directory  # 存保存目录
        self.log_dist_and_hist = log_dist_and_hist  # 存直方图日志开关

        self.train_metrics_dict = {  # 训练指标累积字典（每步 append 数值，train() 汇总求均值后写 TensorBoard）
            "train_critic/loss_av": [],  # critic loss 历史
            "train_actor/loss_av": [],  # actor loss 历史
            "train_actor/target_entropy_av": [],  # 目标熵历史（常量，记录便于对比）
            "train_actor/entropy_av": [],  # 策略实际熵历史
            "train_alpha/loss_av": [],  # α loss 历史
            "train_alpha/value_av": [],  # α 值历史
            "train/batch_reward_av": [],  # 批平均奖励历史
        }  # 指标字典收尾

        self.critic = critic_model(  # 在线双 Q 网络（同一模块输出 Q1、Q2 两路）
            obs_dim=self.state_dim,  # 观测维数
            action_dim=action_dim,  # 动作维数（critic 吃 (s,a) 联合输入）
            hidden_dim=400,  # 隐层宽 400
            hidden_depth=2,  # 2 个隐层
        ).to(self.device)  # 上设备
        self.critic_target = critic_model(  # 目标 critic：结构同款、参数慢速跟随（提供稳定的 Bellman 回归靶，切断"追自己尾巴"的震荡）
            obs_dim=self.state_dim,  # 同构
            action_dim=action_dim,  # 同构
            hidden_dim=400,  # 同构
            hidden_depth=2,  # 同构
        ).to(self.device)  # 上设备
        self.critic_target.load_state_dict(self.critic.state_dict())  # 初始硬拷贝同步（此后只靠软更新慢跟随，与 PPO 每轮硬同步 policy_old 不同）

        self.actor = actor_model(  # 高斯演员：输出 Tanh 压缩的对角高斯分布对象
            obs_dim=self.state_dim,  # 观测维数
            action_dim=action_dim,  # 动作维数
            hidden_dim=400,  # 隐层宽
            hidden_depth=2,  # 隐层数
            log_std_bounds=[-5, 2],  # log σ 截断界：σ∈[e⁻⁵, e²]≈[0.007, 7.39]，防方差爆炸/塌缩（对应 PPO 的手动 std 退火，SAC 让网络自己学 σ）
        ).to(self.device)  # 上设备

        if load_model:  # 断点续训开关
            self.load(filename=model_name, directory=load_directory)  # 恢复三网络权重

        self.log_alpha = torch.tensor(np.log(init_temperature)).to(self.device)  # 存 log α 而非 α：对数参数化保证 α=exp(log α) 恒正，且梯度数值稳定
        self.log_alpha.requires_grad = True  # 打开梯度追踪：α 成为可学习参数（自动调温的物质基础）
        # set target entropy to -|A|  # 原注释：目标熵 = 动作维数的负值
        self.target_entropy = -action_dim  # 目标熵 H_target=-|A|：经验法则——每个动作维至少贡献 1 nat 熵；α 的调节就为把策略熵拉到这条线

        # optimizers  # 原注释：三个互相独立的优化器（三套目标解耦，各自学率）
        self.actor_optimizer = torch.optim.Adam(  # actor 的 Adam
            self.actor.parameters(), lr=actor_lr, betas=actor_betas  # 参数 + 学率 + 动量
        )  # actor 优化器构造收尾

        self.critic_optimizer = torch.optim.Adam(  # critic 的 Adam
            self.critic.parameters(), lr=critic_lr, betas=critic_betas  # 参数 + 学率 + 动量
        )  # critic 优化器构造收尾

        self.log_alpha_optimizer = torch.optim.Adam(  # α 的专属 Adam（与两个网络解耦，只优化一个标量参数）
            [self.log_alpha], lr=alpha_lr, betas=alpha_betas  # 单参数列表 + 学率 + 动量
        )  # α 优化器构造收尾

        self.critic_target.train()  # 目标网显式 train 模式（SAC 惯例：目标网不用 eval/BatchNorm 冻结语义，保持与在线网一致的 forward 行为）

        self.actor.train(True)  # actor 切 train 模式
        self.critic.train(True)  # critic 切 train 模式
        self.step = 0  # train() 调用计数器（日志 x 轴与更新频率判断用）
        self.writer = SummaryWriter(comment=model_name)  # TensorBoard 写手实例

    # save：三网络权重各存一个 .pth 文件（actor / critic / critic_target）
    def save(self, filename, directory):  # 三网络权重落盘
        """
        Save the actor, critic, and target critic models to the specified directory.

        Args:
            filename (str): Base name of the saved files.
            directory (Path): Directory where models are saved.
        """
        Path(directory).mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在不报错）
        torch.save(self.actor.state_dict(), "%s/%s_actor.pth" % (directory, filename))  # 存 actor → {dir}/{name}_actor.pth
        torch.save(self.critic.state_dict(), "%s/%s_critic.pth" % (directory, filename))  # 存 critic → {dir}/{name}_critic.pth
        torch.save(  # 存目标 critic
            self.critic_target.state_dict(),  # 目标网参数
            "%s/%s_critic_target.pth" % (directory, filename),  # 写入 {dir}/{name}_critic_target.pth
        )  # 目标网保存调用收尾

    # load：三网络从磁盘恢复（save 的镜像操作）
    def load(self, filename, directory):  # 三网络权重恢复
        """
        Load the actor, critic, and target critic models from the specified directory.

        Args:
            filename (str): Base name of the saved files.
            directory (Path): Directory where models are loaded from.
        """
        self.actor.load_state_dict(  # 恢复 actor
            torch.load("%s/%s_actor.pth" % (directory, filename))  # 读盘
        )  # actor 加载收尾
        self.critic.load_state_dict(  # 恢复 critic
            torch.load("%s/%s_critic.pth" % (directory, filename))  # 读盘
        )  # critic 加载收尾
        self.critic_target.load_state_dict(  # 恢复目标 critic
            torch.load("%s/%s_critic_target.pth" % (directory, filename))  # 读盘
        )  # 目标网加载收尾
        print(f"Loaded weights from: {directory}")  # 打印来源确认

    # train：外层训练入口——连跑 iterations 次 update，随后汇总日志、按节拍存档。
    # 与 PPO 的根本不同（代码实证）：数据喂给 update 后由 replay_buffer.sample_batch 随机抽样反复用，
    # 没有"用完即清"的 on-policy 语义，buffer 与算法生命周期解耦
    def train(self, replay_buffer, iterations, batch_size):  # 外层训练入口（iterations 次 update）
        """
        Run multiple training updates using data from the replay buffer.

        Args:
            replay_buffer: Buffer from which to sample training data.
            iterations (int): Number of training iterations to run.
            batch_size (int): Batch size for each update.
        """
        for _ in range(iterations):  # 连续 iterations 次完整更新
            self.update(  # 单步流水线：critic → actor/α → 软更新目标网
                replay_buffer=replay_buffer, step=self.step, batch_size=batch_size  # 传 buffer / 步数 / 批大小
            )  # update 调用收尾

        for key, value in self.train_metrics_dict.items():  # 遍历累积的指标字典
            if len(value):  # 本轮确有数据才写
                self.writer.add_scalar(key, mean(value), self.step)  # 求均值写入 TensorBoard
            self.train_metrics_dict[key] = []  # 清空累积（下一轮重新收集）
        self.step += 1  # train 调用计数 +1（update 内部的频率判断也用它）

        if self.save_every > 0 and self.step % self.save_every == 0:  # 到达保存节拍
            self.save(filename=self.model_name, directory=self.save_directory)  # 存三网络 checkpoint

    # alpha 属性：从 log α 反解 α。
    # α（熵温度）是最大熵 RL 特有系数：目标里 α·log π 项的权重——
    # α 大 → 更鼓励随机（多探索）；α 小 → 更贪婪利用。用 property 每次现算，保证与 log_alpha 同步
    @property  # 把方法包装成只读属性：self.alpha 直接取值无需调用括号
    def alpha(self):  # 只读属性方法：反解当前温度 α
        """
        Returns:
            torch.Tensor: Current value of the entropy temperature alpha.
        """
        return self.log_alpha.exp()  # α = exp(log α)，恒为正

    # get_action：对外动作接口，环境循环每步调用。
    # add_noise=True 时在策略输出上再叠一层 σ=0.2 的均匀高斯噪声并裁回界内。
    # 教学注：与 PPO 不同——SAC 的策略本身就是随机的（rsample），这层噪声是环境侧的额外探索冗余
    def get_action(self, obs, add_noise):  # 对外动作接口（含额外探索噪声）
        """
        Select an action given an observation.

        Args:
            obs (np.ndarray): Input observation.
            add_noise (bool): Whether to add exploration noise.

        Returns:
            np.ndarray: Action vector.
        """
        if add_noise:  # 训练期：加噪动作
            return (  # 返回下式构造的 np 数组
                self.act(obs) + np.random.normal(0, 0.2, size=self.action_dim)  # 策略输出 + N(0, 0.2²·I) 探索噪声，shape (action_dim,)
            ).clip(self.action_range[0], self.action_range[1])  # 裁回 [-max_action, max_action]
        else:  # 评估期：不加噪
            return self.act(obs)  # 直接用策略输出

    # act：单观测推理内部通道。
    # obs (state_dim,) → 加 batch 维 → 分布对象 → sample 或 mean → clamp → np (action_dim,)
    # sample 默认 False 取均值：部署用确定性动作；训练路径的随机性由 get_action / rsample 承担
    def act(self, obs, sample=False):  # 单观测推理内部通道
        """
        Generate an action from the actor network.

        Args:
            obs (np.ndarray): Input observation.
            sample (bool): If True, sample from the policy; otherwise use the mean.

        Returns:
            np.ndarray: Action vector.
        """
        obs = torch.FloatTensor(obs).to(self.device)  # np → 浮点张量上设备，(state_dim,)
        obs = obs.unsqueeze(0)  # 补 batch 维：(state_dim,) → (1, state_dim)（网络约定吃二维输入）
        dist = self.actor(obs)  # actor 前向：返回分布对象（非动作本身）——SAC actor 输出 π(·|s) 的参数化分布
        action = dist.sample() if sample else dist.mean  # 从分布采样（随机）或取均值（确定性），(1, action_dim)
        action = action.clamp(*self.action_range)  # 裁剪进动作界内：clamp(-max_action, max_action)
        assert action.ndim == 2 and action.shape[0] == 1  # 形状自检：必须恰为 (1, action_dim)
        return utils.to_np(action[0])  # 去 batch 维并转 numpy：(action_dim,)

    # update_critic：critic 一步更新——SAC 的"软"贝尔曼目标。
    # 输入：批量 obs (B, state_dim) / action (B, action_dim) / reward (B,1) / next_obs (B, state_dim) / done (B,1)
    # 回归靶 y = r + γ(1−done)·[ min(Q₁',Q₂') − α·log π(a'|s') ]，三个部件各有深意：
    # min 双 Q=压过估计偏差；−α·log π=最大熵折扣；目标网=稳定靶防追自己尾巴
    def update_critic(self, obs, action, reward, next_obs, done, step):  # critic 一步更新（软贝尔曼靶）
        """
        Update the critic network based on a batch of transitions.

        Args:
            obs (torch.Tensor): Batch of current observations.
            action (torch.Tensor): Batch of actions taken.
            reward (torch.Tensor): Batch of received rewards.
            next_obs (torch.Tensor): Batch of next observations.
            done (torch.Tensor): Batch of done flags.
            step (int): Current training step (for logging).
        """
        dist = self.actor(next_obs)  # 当前 actor 对下一状态出策略分布：next_obs (B, state_dim) → dist
        next_action = dist.rsample()  # 重参数化采样 a'：把随机性拆成独立噪声 ε，a'=f(ε,θ)——梯度可穿过采样算子流回 actor 参数（普通 sample 采样不可导，这是 SAC 能端到端训演员的关键技巧）
        log_prob = dist.log_prob(next_action).sum(-1, keepdim=True)  # log π(a'|s')：对动作维求和并保持列形状 → (B, 1)
        target_Q1, target_Q2 = self.critic_target(next_obs, next_action)  # 目标网双 Q 值：各 (B, 1)（用慢速参数评估，靶子稳定）
        target_V = torch.min(target_Q1, target_Q2) - self.alpha.detach() * log_prob  # 软价值 V' = min Q' − α·log π：取 min 是 clipped double Q 思想——两 Q 里挑悲观的，系统性压制函数逼近带来的过估计；α detach 保证本步不调温度
        target_Q = reward + ((1 - done) * self.discount * target_V)  # 软贝尔曼靶 y = r + γ(1−done)·V'：done=1 时未来项归零（终态无后继）
        target_Q = target_Q.detach()  # 靶子整体冻结：回归"标签"不参与求导，否则目标会跟着 critic 一起漂

        # get current Q estimates  # 原注释：当前 Q 估计
        current_Q1, current_Q2 = self.critic(obs, action)  # 在线双 Q 评估批内真实动作：Q₁(s,a)、Q₂(s,a)，各 (B, 1)
        critic_loss = F.mse_loss(current_Q1, target_Q) + F.mse_loss(  # 双 Q 各自向同一靶回归的 MSE 相加（两路都被训练）
            current_Q2, target_Q  # 第二项：Q₂ 的回归误差
        )  # 双 Q 回归损失表达式收尾
        self.train_metrics_dict["train_critic/loss_av"].append(critic_loss.item())  # 累积指标（.item() 取 python float 脱离计算图）
        self.writer.add_scalar("train_critic/loss", critic_loss, step)  # 逐步写 TensorBoard

        # Optimize the critic  # 原注释：优化 critic
        self.critic_optimizer.zero_grad()  # 清空 critic 梯度
        critic_loss.backward()  # 反向传播（critic_optimizer 只挂 critic 参数，本步只更新 critic）
        self.critic_optimizer.step()  # Adam 步进
        if self.log_dist_and_hist:  # 直方图日志开关打开时
            self.critic.log(self.writer, step)  # 记录 critic 参数分布（诊断用）

    # update_actor_and_alpha：actor 与 α 的更新（策略提升 + 自动调温）。
    # actor loss = E[α·log π(a|s) − min Q(s,a)]：要 Q 大（高回报）且 log π 小（高熵）——最大熵目标的直接体现。
    # α loss = E[α·(H − H_target).detach()]：熵不足则升 α（更重随机）、熵过剩则降 α——负反馈恒温器
    def update_actor_and_alpha(self, obs, step):  # actor 与 α 更新（策略提升+调温）
        """
        Update the actor and optionally the entropy temperature.

        Args:
            obs (torch.Tensor): Batch of observations.
            step (int): Current training step (for logging).
        """
        dist = self.actor(obs)  # 当前策略分布：obs (B, state_dim) → dist
        action = dist.rsample()  # 重参数化采样 a~π(·|s)：让 Q 对动作的梯度能穿过随机采样回传到 actor（与 update_critic 中同理）
        log_prob = dist.log_prob(action).sum(-1, keepdim=True)  # log π(a|s)：sum 沿动作维 → (B, 1)
        actor_Q1, actor_Q2 = self.critic(obs, action)  # critic 给采样动作打分：各 (B, 1)

        actor_Q = torch.min(actor_Q1, actor_Q2)  # 双 Q 取 min：悲观价值估计，抑制过估计（与靶值构造口径一致）
        actor_loss = (self.alpha.detach() * log_prob - actor_Q).mean()  # E[α·log π − min Q]（取负的最小化=最大化 min Q − α·log π）；α detach：更新 actor 时冻结温度，二者解耦各走各的优化器
        self.train_metrics_dict["train_actor/loss_av"].append(actor_loss.item())  # 累积 actor loss
        self.train_metrics_dict["train_actor/target_entropy_av"].append(  # 累积目标熵
            self.target_entropy  # 常量 −|A|，记录便于与实际熵对照
        )  # 目标熵累积 append 收尾
        self.train_metrics_dict["train_actor/entropy_av"].append(  # 累积策略实际熵
            -log_prob.mean().item()  # 用 −E[log π] 近似记录熵（Tanh 变换分布的解析熵在分布类内部处理，此处是日志口径）
        )  # 实际熵累积 append 收尾
        self.writer.add_scalar("train_actor/loss", actor_loss, step)  # 写 actor loss 曲线
        self.writer.add_scalar("train_actor/target_entropy", self.target_entropy, step)  # 写目标熵参考线
        self.writer.add_scalar("train_actor/entropy", -log_prob.mean(), step)  # 写实际熵曲线

        # optimize the actor  # 原注释：优化 actor
        self.actor_optimizer.zero_grad()  # 清空 actor 梯度
        actor_loss.backward()  # 反向传播：梯度经 rsample 的重参数化路径流入 actor；critic 此处只当"评委"（其优化器不 step，参数不动）
        self.actor_optimizer.step()  # Adam 步进 actor
        if self.log_dist_and_hist:  # 直方图日志开关
            self.actor.log(self.writer, step)  # 记录 actor 参数分布

        if self.learnable_temperature:  # 自动熵调温开启
            self.log_alpha_optimizer.zero_grad()  # 清空 α 梯度
            alpha_loss = (  # α 的损失 E[α·(−log π − H_target).detach()]
                self.alpha * (-log_prob - self.target_entropy).detach()  # 括号内 = 实际熵 H(≈−log π) 偏离目标 H_target 的量；detach 让梯度只作用于 α，α 当"温度计"不反过来搅动策略梯度
            ).mean()  # 批均值。方向性：H < H_target（熵不足）→ 括号为正 → 梯度下降推高 α → 更重视熵；反之调低 α
            self.train_metrics_dict["train_alpha/loss_av"].append(alpha_loss.item())  # 累积 α loss
            self.train_metrics_dict["train_alpha/value_av"].append(self.alpha.item())  # 累积 α 当前值
            self.writer.add_scalar("train_alpha/loss", alpha_loss, step)  # 写 α loss 曲线
            self.writer.add_scalar("train_alpha/value", self.alpha, step)  # 写 α 值演化曲线
            alpha_loss.backward()  # 对 log_alpha 求梯度
            self.log_alpha_optimizer.step()  # 更新 log_alpha（α=exp(·) 随之改变，下次 update 即生效）

    # update：单步完整更新流水线（SAC 标准节奏）。
    # ① replay buffer 随机抽批——off-policy 核心动作：均匀抽样打破时间相关性 + 历史数据反复复用（PPO 做不到）
    # ② update_critic（每步必做）③ 按频率 update_actor_and_alpha ④ 按频率软更新目标网
    def update(self, replay_buffer, step, batch_size):  # 单步完整更新流水线
        """
        Perform a full update step (critic, actor, alpha, target critic).

        Args:
            replay_buffer: Buffer to sample from.
            step (int): Current training step.
            batch_size (int): Size of sample batch.
        """
        (  # 多行解包赋值开始
            batch_states,  # 批状态 np (B, state_dim)
            batch_actions,  # 批动作 np (B, action_dim)
            batch_rewards,  # 批奖励 np (B,)
            batch_dones,  # 批终止标志 np (B,)
            batch_next_states,  # 批下一状态 np (B, state_dim)
        ) = replay_buffer.sample_batch(batch_size)  # 从历史经验池均匀随机抽 B 条转移（新旧数据同权混用）

        state = torch.Tensor(batch_states).to(self.device)  # → 张量 (B, state_dim)
        next_state = torch.Tensor(batch_next_states).to(self.device)  # 转张量 → (B, state_dim)
        action = torch.Tensor(batch_actions).to(self.device)  # 转张量 → (B, action_dim)
        reward = torch.Tensor(batch_rewards).to(self.device).reshape(-1, 1)  # → (B, 1)（列向量，与 Q 值形状对齐）
        done = torch.Tensor(batch_dones).to(self.device).reshape(-1, 1)  # 转列向量 → (B, 1)
        self.train_metrics_dict["train/batch_reward_av"].append(  # 累积批奖励均值
            batch_rewards.mean().item()  # np 均值转 float
        )  # 批奖励累积 append 收尾
        self.writer.add_scalar("train/batch_reward", batch_rewards.mean(), step)  # 写批奖励曲线

        self.update_critic(state, action, reward, next_state, done, step)  # ② critic 更新（每步必做：价值先行的依赖顺序）

        if step % self.actor_update_frequency == 0:  # ③ 到 actor 更新节拍（默认每步）
            self.update_actor_and_alpha(state, step)  # actor + α 更新

        if step % self.critic_target_update_frequency == 0:  # ④ 到目标网更新节拍（默认每 2 步，延迟更新降开销）
            utils.soft_update_params(self.critic, self.critic_target, self.critic_tau)  # 软更新 θ' ← τθ + (1−τ)θ'（Polyak 平均：τ=0.005 意味着每步只吸收 0.5% 新参数，目标网慢速跟随保稳定——与 PPO 的整权重硬同步形成对照）

    # prepare_state：传感器原始数据 → 归一化状态向量（与 PPO 版逐字相同——两算法共享同一套环境状态编码接口）。
    # 输入：雷达扫描、目标距离与方向 cos/sin、碰撞/到达标志、上一步动作
    # 输出：(长度 state_dim 的 list, terminal 0/1)
    def prepare_state(self, latest_scan, distance, cos, sin, collision, goal, action):  # 传感器原始数据→归一化状态向量
        """
        Convert raw sensor input into a normalized state vector.

        Args:
            latest_scan (list or np.ndarray): Laser scan distances.
            distance (float): Distance to goal.
            cos (float): Cosine of heading angle to goal.
            sin (float): Sine of heading angle to goal.
            collision (bool): Whether the robot has collided.
            goal (bool): Whether the goal has been reached.
            action (list): Last action taken [linear_vel, angular_vel].

        Returns:
            tuple: (state vector as list, terminal flag as int)
        """
        latest_scan = np.array(latest_scan)  # 雷达数据转 np 数组（便于布尔掩码与切片）

        inf_mask = np.isinf(latest_scan)  # 找出"无回波"的 inf 读数（超出雷达量程）
        latest_scan[inf_mask] = 7.0  # inf 统一替换为 7.0m（=有效最远距离，也是下文 /7 归一化的基准）

        max_bins = self.state_dim - 5  # 雷达分箱数：总维度减去 5 个导航/速度特征
        bin_size = int(np.ceil(len(latest_scan) / max_bins))  # 每箱原始射线数（向上取整保证末段覆盖）

        # Initialize the list to store the minimum values of each bin  # 原注释：各箱最小值列表
        min_values = []  # 装每箱"最近障碍距离"

        # Loop through the data and create bins  # 原注释：分箱循环
        for i in range(0, len(latest_scan), bin_size):  # 按箱宽步进遍历雷达射线
            # Get the current bin  # 原注释：取当前箱
            bin = latest_scan[i : i + min(bin_size, len(latest_scan) - i)]  # 切出第 i 箱（末箱可能不足整箱宽）
            # Find the minimum value in the current bin and append it to the min_values list  # 原注释：取箱内最小值
            min_values.append(min(bin) / 7)  # 箱内最近障碍距离 /7 → 归一化 [0,1]（取 min=最保守安全假设）

        # Normalize to [0, 1] range  # 原注释：全状态归一化到 [0,1]
        distance /= 10  # 目标距离 /10（10m 量程）
        lin_vel = action[0] * 2  # 上一步线速度特征映射
        ang_vel = (action[1] + 1) / 2  # 上一步角速度 (-1,1) → (0,1)
        state = min_values + [distance, cos, sin] + [lin_vel, ang_vel]  # 拼完整状态：分箱雷达 + 3 导航特征 + 2 速度特征

        assert len(state) == self.state_dim  # 维度断言（分箱数算错在此立刻拦截）
        terminal = 1 if collision or goal else 0  # 碰撞或到达目标即终止

        return state, terminal  # 返回 (状态向量, 终止标志)
