from typing import List  # 类型标注工具：List[str] 给 file_names 参数用，支持静态检查与 IDE 提示
from tqdm import tqdm  # 进度条库：给数据加载/预训练外循环加可视化进度
import yaml  # YAML 解析器：full_load 把预录制经验 data.yml 整体解析成 Python 对象
import torch  # PyTorch：get_max_bound 用张量做批量上界代数（可跑 GPU）

from robot_nav.models.RCPG.RCPG import RCPG  # 循环策略梯度模型：需有 prepare_state（状态组装）与 train 方法，get_buffer 用 isinstance 分派
from robot_nav.replay_buffer import ReplayBuffer, RolloutReplayBuffer  # 两种缓冲区：get_buffer 按模型类型选型构造
from robot_nav.models.PPO.PPO import PPO  # PPO 模型：on-policy 算法，走 model.buffer 旁路（与经验回放不兼容）


# ===================== 类 Pretraining：离线数据加载 + 预训练编排 =====================
# 职责：读预录制的 YAML 经验 → 用 model.prepare_state 组装 s 与 s2 → 用 reward_function
#   （sim.get_reward）重算奖励 r → 逐条灌入 replay_buffer；之后可对 model 反复做预训练。
# 被谁调用：utils.get_buffer（load_saved_buffer=True 时实例化并触发）。
class Pretraining:  # 离线经验预训练编排器：YAML 数据 → 缓冲区 → 预训练循环
    """
    Handles loading of offline experience data and pretraining of a reinforcement learning model.

    Attributes:
        file_names (List[str]): List of YAML files containing pre-recorded environment samples.
        model (object): The model with `prepare_state` and `train` methods.
        replay_buffer (object): The buffer used to store experiences for training.
        reward_function (callable): Function to compute the reward from the environment state.
    """

    # ---- __init__：注入数据来源、模型、缓冲区与奖励函数 ----
    # 输入：file_names 离线 YAML 路径列表；model 须实现 prepare_state/train；
    #   replay_buffer 是 ReplayBuffer 或 RolloutReplayBuffer；reward_function 来自 sim.get_reward。
    def __init__(  # 多行参数表（black 格式风格），共 5 个参数
        self,  # 实例自身（Python 方法惯例首位参数）
        file_names: List[str],  # YAML 文件列表：每个文件是一段（或多段）预录制的经验序列
        model: object,  # RL 模型：TD3/RCPG 等都满足 prepare_state+train 协议
        replay_buffer: object,  # 目标缓冲区：经 .add() 被逐条填充
        reward_function,  # 奖励函数：sim.get_reward(goal, collision, action, laser_scan)，离线数据重算奖励用
    ):  # 无返回值；仅保存 4 个引用供 load_buffer/train 使用
        self.file_names = file_names  # 保存 YAML 路径列表
        self.model = model  # 保存模型引用
        self.replay_buffer = replay_buffer  # 保存目标缓冲区引用
        self.reward_function = reward_function  # 保存奖励函数引用

    # ---- load_buffer：解析离线 YAML 经验、逐条组装转移并灌满缓冲区 ----
    # 输出：返回灌满后的 replay_buffer（即构造时注入的同一对象）。
    # 数据格式：samples[i] 是 dict，键含 latest_scan/distance/cos/sin/collision/goal/action；
    #   奖励不读文件而用 reward_function 现算——换奖励函数无需重录数据，离线数据可复用。
    def load_buffer(self):  # 单遍扫描全部文件，O(总样本数)
        """
        Load samples from the specified files and populate the replay buffer.

        Returns:
            (object): The populated replay buffer.
        """
        for file_name in self.file_names:  # 逐个经验文件处理
            print("Loading file: ", file_name)  # 打印当前加载的文件名
            with open(file_name, "r") as file:  # 只读打开，with 保证自动关闭
                samples = yaml.full_load(file)  # 整体解析 YAML 为 list；samples[i] = 第 i 步观测+动作的 dict
                # 【教学】i 从 1 起到 len-2 止：第 0 步缺"前一步动作"特征无法组装状态；
                #   i 最大取 len-2 是因为还要读 samples[i+1] 当 s2，留出右端。
                for i in tqdm(range(1, len(samples) - 1)):  # 遍历中间样本，带进度条
                    sample = samples[i]  # 当前步的观测/动作 dict
                    latest_scan = sample["latest_scan"]  # 红外/激光扫描向量：各方向到障碍的距离
                    distance = sample["distance"]  # 到目标的距离
                    cos = sample["cos"]  # 朝向角余弦（与 sin 成对编码角度，避免 ±π 跳变）
                    sin = sample["sin"]  # 朝向角正弦
                    collision = sample["collision"]  # 本步是否发生碰撞
                    goal = sample["goal"]  # 本步是否到达目标
                    action = sample["action"]  # 本步动作 [线速度, 角速度]

                    state, terminal = self.model.prepare_state(  # 模型自定制的组装：原始量 → 归一化状态向量 + 终止旗标
                        latest_scan, distance, cos, sin, collision, goal, action  # 当前步全部观测量按位传入
                    )  # 返回 state（state_dim,）与 terminal（0/1）

                    if terminal:  # 当前步已是终止（碰撞/达阵）：无有效"下一步"，跳过
                        continue  # 进入下一循环

                    next_sample = samples[i + 1]  # 下一时刻样本：提供 s2 的全部观测量
                    next_latest_scan = next_sample["latest_scan"]  # 下一步扫描
                    next_distance = next_sample["distance"]  # 下一步距离
                    next_cos = next_sample["cos"]  # 下一步 cos
                    next_sin = next_sample["sin"]  # 下一步 sin
                    next_collision = next_sample["collision"]  # 下一步碰撞旗标
                    next_goal = next_sample["goal"]  # 下一步达阵旗标
                    next_action = next_sample["action"]  # 下一步动作（进入状态向量末两维作"上一步动作"特征）
                    next_state, next_terminal = self.model.prepare_state(  # 同法组装下一状态 s2 与其终止旗标
                        next_latest_scan,  # 下一步扫描
                        next_distance,  # 下一步距离
                        next_cos,  # 下一步 cos
                        next_sin,  # 下一步 sin
                        next_collision,  # 下一步碰撞旗标
                        next_goal,  # 下一步达阵旗标
                        next_action,  # 下一步动作
                    )  # 返回 s2（state_dim,）与下一终止旗标
                    reward = self.reward_function(  # 用仿真奖励函数重算 r：goal→+100，collision→-100，否则 线速度−|角速度|/2−近障罚/2（SIM_ENV/sim.py 实证）
                        next_goal, next_collision, action, next_latest_scan  # 用"下一步结局 + 当前动作 + 当前扫描"评价这一步
                    )  # 得到标量奖励 r
                    self.replay_buffer.add(  # 转移 (s, a, r, done, s2) 入缓冲区
                        state, action, reward, next_terminal, next_state  # 五元组按 add(s,a,r,t,s2) 位序传入
                    )  # 离线经验就此进入回放池

        return self.replay_buffer  # 返回灌满的缓冲区，交给 get_buffer 继续预训练/在线训练

    # ---- train：预训练外循环——反复调用 model.train 消费回放缓冲区 ----
    # 输入：pretraining_iterations 外循环次数 P；replay_buffer 训练数据源；
    #   iterations 每轮内层梯度步数；batch_size 每步批量大小 B。
    def train(  # 多行参数表
        self,  # 实例自身
        pretraining_iterations,  # P：外循环次数，每轮调一次 model.train
        replay_buffer,  # 待消费缓冲区（load_buffer 的返回值）
        iterations,  # 每次调用 model.train 的梯度步数
        batch_size,  # 小批量尺寸
    ):  # 返回 None；模型参数原地更新
        """
        Run pretraining on the model using the replay buffer.

        Args:
            pretraining_iterations (int): Number of outer loop iterations for pretraining.
            replay_buffer (object): Buffer to sample training batches from.
            iterations (int): Number of training steps per pretraining iteration.
            batch_size (int): Batch size used during training.
        """
        print("Running Pretraining")  # 宣告预训练开始
        for _ in tqdm(range(pretraining_iterations)):  # 外循环 P 次，带进度条；_ 表示循环变量不用
            self.model.train(  # 委托模型自己的 train（如 TD3.train：sample_batch → 更新 critic/actor）
                replay_buffer=replay_buffer,  # 训练数据源
                iterations=iterations,  # 梯度步数
                batch_size=batch_size,  # 批量大小
            )  # 一次调用 = iterations 步"采样→算损失→更新"
        print("Model Pretrained")  # 宣告预训练完成


# ===================== 函数 get_buffer：训练入口的缓冲区工厂 + 预训练编排 =====================
# 职责：按模型类型选缓冲区（PPO 用自带 buffer / RCPG 用 Rollout 版 / 其余用标准版），
#   可选地加载离线 YAML 灌满并立即触发预训练。
# 被谁调用：rl_train.py / rnn_train.py / marl_train.py 训练脚本（开训前的缓冲区装配），以及 tests/test_utils.py、tests/test_model.py。
def get_buffer(  # 11 个参数，其中 6 个带默认值
    model,  # RL 模型实例（PPO/RCPG/TD3/SAC...）
    sim,  # 仿真环境：此处只用它的 get_reward 作为奖励函数源
    load_saved_buffer,  # 开关：是否从文件加载离线经验灌缓冲区
    pretrain,  # 开关：灌完后是否立刻预训练（前置依赖 load_saved_buffer=True）
    pretraining_iterations,  # 预训练外循环次数（传给 Pretraining.train）
    training_iterations,  # 预训练每轮内层梯度步数（以 iterations 名义传入）
    batch_size,  # 训练批量大小
    buffer_size=50000,  # 缓冲区容量，默认 5 万（转移/回合）
    random_seed=666,  # 抽样种子，默认 666（覆盖 ReplayBuffer 形参默认的 123）
    file_names=["robot_nav/assets/data.yml"],  # 离线数据文件路径列表
    history_len=10,  # 历史窗长 H（只对 RCPG 的 RolloutReplayBuffer 生效）
):  # 返回构造好（可能已灌满/已预训练）的缓冲区对象
    """
    Get or construct the replay buffer depending on model type and training configuration.

    Args:
        model (object): The RL model, can be PPO, RCPG, or other.
        sim (object): Simulation environment with a `get_reward` function.
        load_saved_buffer (bool): Whether to load experiences from file.
        pretrain (bool): Whether to run pretraining using the buffer.
        pretraining_iterations (int): Number of outer loop iterations for pretraining.
        training_iterations (int): Number of iterations in each training loop.
        batch_size (int): Size of the training batch.
        buffer_size (int, optional): Maximum size of the buffer. Defaults to 50000.
        random_seed (int, optional): Seed for reproducibility. Defaults to 666.
        file_names (List[str], optional): List of YAML data file paths. Defaults to ["robot_nav/assets/data.yml"].
        history_len (int, optional): Used for RCPG buffer configuration. Defaults to 10.

    Returns:
        (object): The initialized and optionally pre-populated replay buffer.
    """
    # 【教学】PPO 是 on-policy：其 buffer 只能存当前策略最新一批 rollout（每次更新后作废），
    #   历史经验会使重要性采样比率失真，因此不做经验回放，直接返回模型自带的 buffer。
    if isinstance(model, PPO):  # PPO 分支：绕过两种回放缓冲区
        return model.buffer  # 返回 PPO 内部 rollout buffer（每轮更新用完即清）

    if isinstance(model, RCPG):  # RCPG 分支：需要历史观测序列 → 回合级缓冲区
        replay_buffer = RolloutReplayBuffer(  # 构造整回合回放缓冲区
            buffer_size=buffer_size, random_seed=random_seed, history_len=history_len  # 容量/种子/历史窗 H 三个配置透传
        )  # 得到空的回合级 buffer
    else:  # 其余 off-policy 模型（TD3/SAC 等）→ 步级标准缓冲区
        replay_buffer = ReplayBuffer(buffer_size=buffer_size, random_seed=random_seed)  # 标准环形经验回放

    if pretrain:  # 预训练的前置约束：必须有离线数据来源
        assert (  # 断言 load_saved_buffer 为真
            load_saved_buffer  # 被断言的条件表达式：pretrain 却不给数据源 = 配置自相矛盾
        ), "To pre-train model, load_saved_buffer must be set to True"  # 断言失败时抛出的错误信息（原样保留）

    if load_saved_buffer:  # 离线灌数分支
        pretraining = Pretraining(  # 实例化预训练编排器
            file_names=file_names,  # 离线数据路径
            model=model,  # 待预训练模型
            replay_buffer=replay_buffer,  # 灌注目标
            reward_function=sim.get_reward,  # 奖励函数从仿真环境取
        )  # instantiate pre-trainind  # 原注释保留（pre-trainind 为原拼写）｜实例化预训练编排器
        replay_buffer = (  # 重新绑定：装入离线经验后的缓冲区（仍是同一对象）
            pretraining.load_buffer()  # 执行加载：遍历 YAML → 组装转移 → buffer.add 逐条灌入
        )  # fill buffer with experiences from the data.yml file  # 原注释保留｜用 data.yml 经验填满缓冲区
        if pretrain:  # 灌满后立即预训练
            pretraining.train(  # 外循环调用 model.train 消费缓冲区
                pretraining_iterations=pretraining_iterations,  # 外循环次数
                replay_buffer=replay_buffer,  # 数据源
                iterations=training_iterations,  # 每轮梯度步数（注意：training 改名 iterations 传入）
                batch_size=batch_size,  # 批量
            )  # run pre-training  # 原注释保留｜执行预训练

    return replay_buffer  # 返回缓冲区，供训练主循环继续在线交互使用


# ===================== 函数 get_max_bound：Max Upper Bound Loss 的"回报理论上界"计算 =====================
# 职责：不依赖价值网络，仅用运动学极限（最大角速度 ω / 最大线速度 v）解析地算出
#   "从 next_state 出发、哪怕此后每步都走最优，折扣回报最多是多少"→ max_bound (B,1)。
# 上界剧本（贪心、假设无障碍）：先原地以 ω 转向对准目标 → 再以 v 全速直行 → 达阵拿 goal_reward。
#   对照奖励函数（sim.get_reward）：直行步奖励上界 = +v（取 action[0]=v）；
#   转向步为负（action[0]=0 时奖励为负）；达阵 +goal_reward（实证 +100）。
# 被谁调用：TD3.train（TD3.py:303，use_max_bound=True 时启用）——
#   max_bound_loss = mean(relu(Q1−max_bound)²) + mean(relu(Q2−max_bound)²)，以 bound_weight=0.25
#   加进 critic 损失：惩罚超出物理上界的 Q 预测，抑制过估计（overestimation）。
# 实际计算式（代码实证，N_turn=|θ|/(ω·dt)，N_lin=(dist·norm)/(v·dt)，θ=atan2(sin,cos)）：
#   max_bound = r + (1−done) · [ −ω·γ^⌊N_turn⌋ − γ^(⌊N_turn⌋+1)·frac(N_turn)     ← 转向阶段（近似记账，非精确几何级数和）
#               + goal_reward·γ^(⌈N_lin⌉+⌊N_turn⌋+1)                          ← 达阵奖励按总步数折扣
#               + Σ_{k=⌊N_turn⌋+2}^{⌊N_lin⌋+⌊N_turn⌋+1} v·γ^k ]              ← 直行阶段逐步奖励折扣和
def get_max_bound(  # 解析计算"从 s' 出发最优剧本的折扣回报上界"（Max Upper Bound Loss 的界）
    next_state,  # (B, state_dim) 下一状态批；末 5 维 = [distance, cos, sin, lin_vel, ang_vel]（RCPG.prepare_state 实证）
    discount,  # γ 折扣因子：未来奖励按步数几何衰减
    max_ang_vel,  # ω：最大角速度（rad/s），转向阶段步数与罚项都用它
    max_lin_vel,  # v：最大线速度（m/s），直行阶段步数与每步奖励上界
    time_step,  # dt：环境单步时长（s），角/位移换算成"步数"的分母
    distance_norm,  # 距离归一化因子：状态里 distance 已 /10，此处乘回物理米制
    goal_reward,  # 达阵奖励（sim.get_reward 实证 +100.0）
    reward,  # (B,1) 当前步即时奖励
    done,  # (B,1) 终止旗标，1=回合结束（后续回报不再计入）
    device,  # torch 设备（cpu/cuda）：决定新建 arange 张量落哪个设备
):  # 返回 max_bound (B,1)：每个样本从 s' 出发可得的折扣回报上界
    """
    Estimate the maximum possible return (upper bound) from the next state onward.

    This is used in constrained RL or safe policy optimization where a conservative
    estimate of return is useful for policy updates.

    Args:
        next_state (torch.Tensor): Tensor of next state observations.
        discount (float): Discount factor for future rewards.
        max_ang_vel (float): Maximum angular velocity of the agent.
        max_lin_vel (float): Maximum linear velocity of the agent.
        time_step (float): Duration of one time step.
        distance_norm (float): Normalization factor for distance.
        goal_reward (float): Reward received upon reaching the goal.
        reward (torch.Tensor): Immediate reward from the environment.
        done (torch.Tensor): Binary tensor indicating episode termination.
        device (torch.device): PyTorch device for computation.

    Returns:
        (torch.Tensor): Maximum return bound for each sample in the batch.
    """
    # 【教学】三个 clone 是纯函数卫生：下面 full_turn_steps += 1 等是原地写，
    #   不 clone 会改到调用方（TD3.train）还在用的 next_state/reward/done 张量。
    next_state = next_state.clone()  # Prevents in-place modifications  # 原注释保留｜复制 next_state，防原地写污染调用方张量
    reward = reward.clone()  # Ensures original reward is unchanged  # 原注释保留｜同理复制 reward
    done = done.clone()  # 复制 done（原行无注释，此处为纯增量注释）
    cos = next_state[:, -4]  # (B,) 取倒数第 4 维：朝向角余弦（状态布局 scan+[dist,cos,sin,v,ω] 实证）
    sin = next_state[:, -3]  # (B,) 取倒数第 3 维：朝向角正弦
    theta = torch.atan2(sin, cos)  # (B,) 由 (sin,cos) 重建朝向角 θ=atan2∈(−π,π]：还差多少弧度对准目标

    # Compute turning steps  # 原注释保留｜——转向阶段步数
    turn_steps = theta.abs() / (max_ang_vel * time_step)  # (B,) 实数步数 N_turn=|θ|/(ω·dt)：以最大角速转过 θ 需要几步
    full_turn_steps = torch.floor(turn_steps)  # (B,) 完整转向步数 ⌊N_turn⌋（float 张量但取值为整数）
    turn_rew = -max_ang_vel * discount**full_turn_steps  # (B,) 转向阶段折扣罚项 −ω·γ^⌊N_turn⌋：转向时步奖励为负（action[0]=0），按最后一步折扣的近似记账（非精确几何级数和）
    turn_rew[full_turn_steps == 0] = 0  # Handle zero case  # 原注释保留｜θ=0 无需转向时罚项清零（否则 γ^0=1 会凭空产生 −ω）
    final_turn_rew = -(discount ** (full_turn_steps + 1)) * (  # (B,) 末尾不足一步的"零头转向"按比例折扣：−γ^(⌊N⌋+1)·frac
        turn_steps - full_turn_steps  # 零头步数 frac(N_turn) = N_turn − ⌊N_turn⌋ ∈ [0,1)
    )  # 与 turn_rew 同量纲，可与完整步罚项直接相加
    full_turn_rew = turn_rew + final_turn_rew  # (B,) 转向阶段总回报记账 = −ω·γ^⌊N⌋ − γ^(⌊N⌋+1)·frac(N)

    # Compute distance-based steps  # 原注释保留｜——直行阶段步数
    full_turn_steps += 1  # Account for the final turn step  # 原注释保留｜步数统一 +1 记上那个零头转向步（原地加，这就是上面要 clone 的原因）
    distances = (next_state[:, -5] * distance_norm) / (max_lin_vel * time_step)  # (B,) 实数步数 N_lin=(dist·norm)/(v·dt)：乘 norm 还原米制再除以每步最大位移
    final_steps = torch.ceil(distances) + full_turn_steps  # (B,) 总步数上界 ⌈N_lin⌉+⌊N_turn⌋+1：达阵奖励的折扣指数
    inter_steps = torch.trunc(distances) + full_turn_steps  # (B,) 完整直行步数 ⌊N_lin⌋+⌊N_turn⌋+1：直行奖励求和的截止索引

    final_rew = goal_reward * discount**final_steps  # (B,) 达阵奖励按总步数折扣：goal_reward·γ^(⌈N_lin⌉+⌊N_turn⌋+1)

    # Compute intermediate rewards using a sum of discounted steps  # 原注释保留｜——直行阶段逐步奖励的折扣求和
    max_inter_steps = inter_steps.max().int().item()  # 标量：批内最大完整步数，决定查表长度（最长求和区间）
    discount_exponents = discount ** torch.arange(1, max_inter_steps + 1, device=device)  # (max_inter_steps,) 预生成 γ^1..γ^max 公共查表，避免逐样本重算幂
    inter_rew = torch.stack(  # (B,) 把逐样本的直行折扣和堆叠成批
        [  # 列表推导：逐样本算一段折扣和
            (max_lin_vel * discount_exponents[int(start) + 1 : int(steps)]).sum()  # 查表切片求和：Σ v·γ^k（直行段逐步奖励折扣和）
            for start, steps in zip(full_turn_steps, inter_steps)  # start=转向后步数起点，steps=完整步数终点
        ]  # 得到 B 个零维张量
    )  # torch.stack 堆叠 → (B,)
    # 【教学】切片 [start+1, steps) 取的索引 j 对应表项 γ^(j+1)，故实际求和 Σ_{k=start+2}^{steps} v·γ^k：
    #   转向刚结束后的奖励已由转向罚项覆盖，这里只累计直行段每步 +v 的折扣；空切片 sum()=0 不报错。
    # Compute final max bound  # 原注释保留｜——汇总总上界
    max_bound = reward + (1 - done) * (full_turn_rew + final_rew + inter_rew).view(  # (B,1) 总上界 = r + (1−done)·(转向罚+达阵奖+直行和)；done=1 的样本只剩即时 r
        -1, 1  # (B,) → (B,1) 对齐 reward/done 的列向量形状
    )  # max_bound 定形 (B,1)
    return max_bound  # (B,1) 物理回报上界；TD3.train 中用于 relu(Q−max_bound)² 正则（Max Upper Bound Loss）
