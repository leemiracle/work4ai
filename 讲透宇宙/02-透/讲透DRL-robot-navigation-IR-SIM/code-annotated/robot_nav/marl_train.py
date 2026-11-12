# ══════【教学注释版 · marl_train.py — MARL 训练入口】══════
# 任务：在 IRSim 2D 仿真里训练 5 台差速机器人（红外导航场景）协同避碰导航。
# 算法：TD3（Twin Delayed DDPG，双延迟深度确定性策略梯度）+ 图注意力
# （IGA/G2ANet），模型实现在 robot_nav/models/MARL/marlTD3/marlTD3.py，
# 环境包装在 robot_nav/SIM_ENV/marl_sim.py。
# 主循环三级结构：step（仿真一步）⊂ episode（一局：碰撞/超时/出界即重置）
# ⊂ epoch（每 10 局一个 epoch，epoch 末做 80 批梯度更新并记 TensorBoard）。
# 产物：checkpoint 目录下 TDR-MARL-train_{actor,actor_target,critic,
# critic_target}.pth 四件套，供 marl_test_single.py / marl_test_random.py 加载。
# ═══════════════════════════════════════════════════【导读完】
from pathlib import Path  # 【基础】路径工具类：下面的 checkpoint 目录参数用它构造

from robot_nav.models.MARL.marlTD3.marlTD3 import TD3  # 【基础】TD3 智能体类：训练算法主体（内含 Actor/Critic/目标网络/优化器/权重存取/日志）

import torch  # 【基础】PyTorch 深度学习框架：张量与神经网络
import numpy as np  # 【基础】NumPy 数值库：状态/动作的数组表示
from robot_nav.SIM_ENV.marl_sim import MARL_SIM  # 【基础】多机器人仿真环境包装类：封装 IRSim 的 step/reset 与奖励计算
from utils import get_buffer  # 【基础】工具函数：按模型类型构造（并可离线填充/预热）经验回放缓冲区


# ── 函数 outside_of_bounds：出界检测 ──
# 职责：判断是否有机器人跑出以世界中心 (6,6) 为心、半边长 10.5 的正方形边界。
# 输入：poses——各机器人位姿列表，每个元素为 [x, y, theta]；输出：布尔值。
# 调用关系：主循环每步调用一次，返回值是"出界即重置一局"的第三个终止条件。
def outside_of_bounds(poses):  # 【基础】函数定义：接收所有机器人的位姿列表
    """
    Check if any robot is outside the defined world boundaries.

    Args:
        poses (list): List of [x, y, theta] poses for each robot.

    Returns:
        bool: True if any robot is outside the 21x21 area centered at (6, 6), else False.
    """
    outside = False  # 【基础】出界标志初始化为 False（默认未出界）
    for pose in poses:  # 【基础】逐台机器人检查
        norm_x = pose[0] - 6  # 【基础】x 坐标对世界中心 6 取偏移（中心化）
        norm_y = pose[1] - 6  # 【基础】y 坐标对世界中心 6 取偏移
        if abs(norm_x) > 10.5 or abs(norm_y) > 10.5:  # 【基础】任一方向偏心超过 10.5（21x21 正方形边界）判出界；注：YAML 世界实际仅 12x12，此阈属宽松冗余护栏
            outside = True  # 【基础】置出界标志
            break  # 【基础】发现一台即够，提前退出循环
    return outside  # 【基础】返回是否出界


# ── 函数 main：训练主入口 ──
# 职责：设定超参 → 实例化环境与 TD3 模型 → 备好回放缓冲区 → 运行
#       "采集经验（每 10 局）→ 批量训练（80 批）→ 自动存档"的主循环直至 160 个 epoch。
# 输入：args=None（占位参数，未使用）；输出：无返回值，产物为 checkpoint 与 TensorBoard 日志。
# 调用关系：文件底部 if __name__ == "__main__" 直接调用一次。
def main(args=None):  # 【基础】主函数定义（args 存在但未使用）
    """Main training function"""

    # ---- Hyperparameters and setup ----  # 【基础】分节注释：以下集中定义训练超参数
    action_dim = 2  # number of actions produced by the model  # 【基础】每台机器人动作维度=2：线速度 + 角速度
    max_action = 1  # maximum absolute value of output actions  # 【基础】动作幅值上限：网络 tanh 输出天然在 [-1,1]，探索噪声裁剪也以此为界
    state_dim = 11  # number of input values in the neural network (vector length of state input)  # 【基础】每机状态向量长度 11（x,y,cosθ,sinθ,距离/17,夹角cos,夹角sin,线速,角速,目标x,目标y——见模型 prepare_state）
    device = torch.device(  # 【基础】创建计算设备对象：决定网络与张量放 CPU 还是 GPU
        "cuda" if torch.cuda.is_available() else "cpu"  # 【基础】三目表达式：检测到 NVIDIA GPU 用 cuda，否则回退 cpu
    )  # using cuda if it is available, cpu otherwise  # 【基础】device 将传给 TD3 构造器统一部署
    max_epochs = 160  # max number of epochs  # 【教学】训练总轮数：1 epoch=10 局 → 全程约 1600 局仿真
    epoch = 1  # starting epoch number  # 【基础】轮计数器从 1 起（while 终止条件用）
    episode = 0  # starting episode number  # 【基础】局计数器从 0 起
    train_every_n = 10  # train and update network parameters every n episodes  # 【教学】"先采集后学习"节奏：每攒 10 局经验才做一轮梯度更新——TD3 是 off-policy（离策略）算法，允许旧经验反复利用，不必每步都学
    training_iterations = 80  # how many batches to use for single training cycle  # 【基础】每轮训练取 80 个 mini-batch 逐批更新
    batch_size = 16  # batch size for each training iteration  # 【基础】每批 16 条样本（每条是 5 机联合转移，训练时重塑为 (16,5,11)）
    max_steps = 300  # maximum number of steps in single episode  # 【基础】单局步数上限：超时强制重置，防止卡死局浪费样本
    steps = 0  # starting step number  # 【基础】局内步数计数器
    load_saved_buffer = False  # whether to load experiences from assets/data.yml  # 【教学】离线经验开关：True 时从 robot_nav/assets/data.yml 读预录驾驶数据填充缓冲区（示范数据热身）
    pretrain = False  # whether to use the loaded experiences to pre-train the model (load_saved_buffer must be True)  # 【教学】预训练开关：True 时先用离线数据跑若干轮更新再开始在线交互（前提 load_saved_buffer=True，见 utils.get_buffer 内断言）
    pretraining_iterations = (  # 【基础】预训练外循环轮数（这对括号只为换行排版，值为 10）
        10  # number of training iterations to run during pre-training  # 【基础】预训练跑 10 轮
    )  # 【基础】闭合括号完成赋值
    save_every = 5  # save the model every n training cycles  # 【教学】存档节奏：model.train() 每被调一次内部计数 iter_count+1，逢 5 的倍数自动存盘——即每 5 个 epoch（约 50 局）一存

    # ---- Instantiate simulation environment and model ----  # 【基础】分节注释：下面创建仿真环境与智能体
    sim = MARL_SIM(  # 【基础】实例化多机器人仿真环境
        world_file="worlds/multi_robot_world.yaml",  # 【基础】世界配置：12x12 场地，5 台差速机器人圆形分布（半径 5，中心 (6,6)），初始共享目标 (9,9)
        disable_plotting=True,  # 【基础】关闭渲染窗口：无头训练换速度
        reward_phase=1,  # 【教学】奖励函数版本：训练用 phase 1（到达+100 / 碰撞 -300·线速度 / 距离引导 1.5÷d / 邻近惩罚，见 marl_sim.get_reward 的 match-case 分支）；两个测试脚本用 phase 2
    )  # instantiate environment  # 【基础】sim.step 返回十元组观测；sim.reset 随机化起点与目标

    model = TD3(  # 【基础】实例化 TD3 智能体（Actor-Critic 架构 + 注意力编码器）
        state_dim=state_dim,  # 【基础】单机状态维度 11
        action_dim=action_dim,  # 【基础】单机动作维度 2
        max_action=max_action,  # 【基础】动作界 ±1
        num_robots=sim.num_robots,  # 【教学】机器人数 5：单一策略网络经"参数共享"同时为 5 台机器人产出动作——本仓多智能体协同的实现方式，训练与测试皆如此
        device=device,  # 【基础】网络部署设备
        save_every=save_every,  # 【基础】训练中每 5 个周期自动存档
        load_model=False,  # 【教学】False=从零开始新训练；两个测试脚本此处为 True（加载训练产物）
        model_name="TDR-MARL-train",  # 【教学】存档基础名：checkpoint 目录会生成 TDR-MARL-train_actor.pth / _actor_target.pth / _critic.pth / _critic_target.pth 四件套；也是 TensorBoard 日志目录的 comment 后缀
        load_model_name="saved_model",  # 【基础】欲加载权重的基础名（load_model=False 时不生效）
        load_directory=Path("robot_nav/models/MARL/marlTD3/checkpoint"),  # 【基础】加载目录（保存目录用模型内默认的同一 checkpoint 路径）
        attention="iga",  # 【教学·坑】注意力后端——但 TD3 构造器只认 "igs"/"g2anet"（marlTD3.py 构造函数首行校验），传 "iga" 会直接抛 ValueError：本脚本按原样运行无法启动，需改为 "igs"（即 iga.py 的 Attention 类）才能跑通；两个测试脚本用的正是 "igs"
    )  # instantiate a model  # 【基础】内部含 actor/actor_target/critic/critic_target、两个 Adam 优化器与 TensorBoard SummaryWriter 日志器

    # ---- Setup replay buffer and initial connections ----  # 【基础】分节注释：准备回放缓冲区与初始连接张量
    replay_buffer = get_buffer(  # 【基础】调用工具函数构造回放缓冲区
        model,  # 【基础】传入模型：PPO 用自带缓冲，其余（含 TD3）用通用 ReplayBuffer
        sim,  # 【基础】传入环境：离线加载经验时用 sim.get_reward 重算奖励
        load_saved_buffer,  # 【基础】是否读离线数据（此处 False）
        pretrain,  # 【基础】是否先预训练（此处 False）
        pretraining_iterations,  # 【基础】预训练轮数 10
        training_iterations,  # 【基础】正式训练每周期批数 80
        batch_size,  # 【基础】批大小 16
    )  # 【教学】经验回放缓冲区（replay buffer）：存 (s,a,r,done,s') 五元组的环形队列（容量 5 万），训练时随机抽样——打碎时间相关性、让一条经验被多次学习，是 TD3 这类 off-policy 算法的标配组件
    connections = torch.tensor(  # 【基础】构造初始连接打分张量（全零）
        [[0.0 for _ in range(sim.num_robots - 1)] for _ in range(sim.num_robots)]  # 【基础】嵌套列表推导：形状 (5,4)——每台对其余 4 台的连接得分（不含自身列）
    )  # 【教学】首步交互用零连接：sigmoid(0)=0.5 恰不满足 >0.5，不会画注意力边；此后连接打分由模型 get_action 返回

    # ---- Take initial step in environment ----  # 【基础】分节注释：先迈一步拿初始观测
    poses, distance, cos, sin, collision, goal, a, reward, positions, goal_positions = (  # 【基础】十元组解包起始行：位姿/目标距离/朝向差cos/朝向差sin/碰撞标志/到达标志/已执行动作/奖励/当前位置/目标位置
        sim.step([[0, 0] for _ in range(sim.num_robots)], connections)  # 【基础】5 台机器人全零动作推进一步（列表推导生成 5 个 [0,0]）
    )  # get the initial step state  # 【教学】RL 惯用法：进主循环前先取 s0，保证循环体 state→action→next_state 时序闭合
    running_goals = 0  # 【基础】epoch 内累计"到达"事件数（统计分子）
    running_collisions = 0  # 【基础】epoch 内累计碰撞标志数（一对互撞两机各置位一次）
    running_timesteps = 0  # 【基础】epoch 内累计仿真步数（统计分母）

    # ---- Main training loop ----  # 【基础】分节注释：主训练循环开始
    while epoch < max_epochs:  # train until max_epochs is reached  # 【教学】外层终止按 epoch 计：循环体内按 step（每步采集）→ episode（终局重置）→ epoch（每 10 局训练+记日志）三级推进
        state, terminal = model.prepare_state(  # 【基础】把环境原始十元组编码为每机 11 维状态
            poses, distance, cos, sin, collision, a, goal_positions  # 【基础】入参为当前观测（prepare_state 内做距离 /17 归一、速度反归一、朝向 cos/sin 编码）
        )  # get state a state representation from returned data from the environment  # 【教学】terminal 只继承碰撞标志——"到达"不算终止：训练环境中到达即换发新随机目标，属持续型任务（continuing task）

        action, connection, combined_weights = model.get_action(  # 【基础】策略前向：一次输出全部 5 机的动作、注意力连接 logits、软注意力权重
            np.array(state), True  # 【教学】第二参 add_noise=True：训练期叠加高斯探索噪声 N(0,0.5)（角速度维噪声再 /4，最后裁回 [-1,1]）——TD3 靠噪声探索连续动作空间；噪声标准差全程固定、无衰减调度；两个测试脚本均传 False 走无噪声确定性策略
        )  # get an action from the model  # 【基础】返回：动作数组 (5,2)、连接张量与组合权重

        a_in = [  # 【基础】构造真正下发给机器人的物理动作列表
            [(a[0] + 1) / 4, a[1]] for a in action  # 【基础】逐机仿射映射：线速度 [-1,1]→[0,0.5] m/s（机器人不倒车），角速度原样直传 [-1,1] rad/s
        ]  # clip linear velocity to [0, 0.5] m/s range  # 【教学·勘误】原注释称 clip，实为线性重标度 (a+1)/4 而非裁剪；另注意回放缓冲区存的是归一化 action 原值，不是这里的物理量 a_in

        (  # 【基础】多行元组解包开始：接收环境新十元组
            poses,  # 【基础】各机新位姿 [x,y,θ]
            distance,  # 【基础】各机到目标的新距离
            cos,  # 【基础】各机朝向与目标方向夹角的余弦
            sin,  # 【基础】对应正弦
            collision,  # 【基础】各机本步碰撞标志
            goal,  # 【基础】各机本步到达标志
            a,  # 【基础】环境回传的已执行动作（即 a_in）
            reward,  # 【基础】各机本步奖励（phase 1 奖励函数）
            positions,  # 【基础】各机当前位置 [x,y]
            goal_positions,  # 【基础】各机当前目标点 [x,y]（换发新目标后会更新）
        ) = sim.step(  # 【基础】推进仿真一个 step_time=0.3s
            a_in, connection, combined_weights  # 【基础】入参：物理动作 + 连接 logits + 软权重（后两者用于渲染注意力边）
        )  # get data from the environment  # 【教学】MARL_SIM.step 内部：到达的机器人当场领取新随机目标——所以本训练里"到达"不是终点，一局只有碰撞/超时/出界三种结局
        running_goals += sum(goal)  # 【基础】累加本步到达次数（布尔求和）
        running_collisions += sum(collision)  # 【基础】累加本步碰撞标志数（一对互撞计 2）
        running_timesteps += 1  # 【基础】步数累计 +1
        next_state, terminal = model.prepare_state(  # 【基础】把新观测编码为 s'（与 state 同构）
            poses, distance, cos, sin, collision, a, goal_positions  # 【基础】注意：用的是 step 之后的最新十元组
        )  # get a next state representation  # 【基础】terminal'=新一步的碰撞标志
        replay_buffer.add(  # 【基础】向回放缓冲区写入一条联合转移
            state, action, reward, terminal, next_state  # 【教学】五元组 (s,a,r,done,s')——a 存的是策略原始输出（归一化域 [-1,1]），与物理动作 a_in 解耦，保证训练批内动作尺度一致
        )  # add experience to the replay buffer  # 【基础】每次交互存 1 条（内含全部 5 机的联合转移）
        outside = outside_of_bounds(poses)  # 【基础】检测本步是否有机出界
        if (  # 【基础】一局终止判定开始（三条件取或）
            any(terminal) or steps == max_steps or outside  # 【教学】终止条件=任一机碰撞 / 超 300 步 / 出界；注意"全部到达"不在其中——新目标已换发，任务继续
        ):  # reset environment of terminal state reached, or max_steps were taken  # 【基础】满足任一条件：重置环境收束本局
            (  # 【基础】重置返回的十元组再次解包（拿到新局初始观测）
                poses,  # 【基础】新局各位姿
                distance,  # 【基础】新局各目标距离
                cos,  # 【基础】新局各朝向差余弦
                sin,  # 【基础】新局各朝向差正弦
                collision,  # 【基础】新局碰撞标志（reset 固定返回全 False）
                goal,  # 【基础】新局到达标志（全 False）
                a,  # 【基础】初始动作（全零）
                reward,  # 【基础】初始状态奖励
                positions,  # 【基础】新局初始位置
                goal_positions,  # 【基础】新局随机目标位置
            ) = sim.reset()  # 【教学】MARL_SIM.reset 的随机化：每机在 [3,9]x[3,9] 均匀抽起点（两两间距强制 ≥0.6m）、随机朝向，并各自抽新目标——训练场景多样性的来源（random 测试口径正是复用此机制）
            episode += 1  # 【基础】局数 +1
            if episode % train_every_n == 0:  # 【教学】每满 10 局（=1 个 epoch）触发一次：写统计日志 + 做梯度更新
                model.writer.add_scalar(  # 【基础】向 TensorBoard 写一条标量曲线（writer=SummaryWriter 实例）
                    "run/avg_goal", running_goals / running_timesteps, epoch  # 【基础】指标=本 epoch 内平均每步到达率，横轴为 epoch
                )  # 【基础】曲线名 run/avg_goal
                model.writer.add_scalar(  # 【基础】再写一条碰撞率曲线
                    "run/avg_collision", running_collisions / running_timesteps, epoch  # 【基础】平均每步碰撞标志率（分母同为期内总步数）
                )  # 【基础】曲线名 run/avg_collision
                running_goals = 0  # 【基础】分子清零：下一 epoch 重新累计
                running_collisions = 0  # 【基础】清零
                running_timesteps = 0  # 【基础】分母清零
                epoch += 1  # 【基础】轮数 +1（推进 while 终止条件）
                model.train(  # 【基础】真正的学习阶段：TD3 批量更新
                    replay_buffer=replay_buffer,  # 【基础】数据源：回放缓冲区随机抽样
                    iterations=training_iterations,  # 【基础】本轮 80 个批次
                    batch_size=batch_size,  # 【基础】每批 16 条联合转移
                )  # train the model and update its parameters  # 【教学】train() 内部即 TD3 三大机制：双 Critic 取 min 抑制 Q 值高估 / 目标策略平滑（目标动作加 σ=0.2、裁剪 ±0.5 的噪声）/ 策略延迟更新（每 2 批更一次 Actor）+ 目标网络软更新（τ=0.005）；另叠加注意力 BCE 辅助损失与熵正则；每调用一次 iter_count+1，逢 5 的倍数自动存档

            steps = 0  # 【基础】新局步数清零
        else:  # 【基础】未触发终止：本局继续
            steps += 1  # 【基础】步数 +1


if __name__ == "__main__":  # 【基础】仅当直接运行本文件时执行（被 import 时不触发训练）
    main()  # 【基础】启动训练主流程
