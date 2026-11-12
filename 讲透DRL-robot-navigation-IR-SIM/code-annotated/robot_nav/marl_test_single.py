# ══════【教学注释版 · marl_test_single.py — 固定场景测试入口】══════
# 任务：加载训练脚本存下的 TDR-MARL-train 权重，在 circle_world 固定圆环
# 场景（每局同一布局、共享固定目标 (9,9)）连跑 100 局，统计无碰撞成功率、
# 平均到达数、平均局长与超时局数。
# 与 marl_test_random.py 的分工：本文件=固定场景收敛性测试（到达即冻结、
# 全员到达=成功局）；random=随机场景泛化测试（随机起点/目标、持续任务）。
# 关于"对手"的代码实证：两个测试都只建一个 TD3 实例并加载同一份训练权重，
# get_action 一次为全部 5 机出动作——所有机器人都跑同一个训练过的策略
# （参数共享自博弈式协同），不存在"随机策略对手"；差别只在场景与终止条件。
# ════════════════════════════════════════════════════【导读完】
import statistics  # 【基础】标准库统计模块：求均值 mean 与样本标准差 stdev
from pathlib import Path  # 【基础】路径类：构造权重加载目录

import irsim  # 【基础】IRSim 仿真内核库：2D 多机器人仿真框架，负责运动学积分、碰撞检测与渲染（本仓的"物理世界"）
from tqdm import tqdm  # 【基础】进度条库：可视化 100 个测试场景的完成进度

from robot_nav.SIM_ENV.sim_env import SIM_ENV  # 【基础】环境基类：SINGLE_SIM 继承它（复用 cossin 夹角计算等静态工具）
from robot_nav.models.MARL.marlTD3.marlTD3 import TD3  # 【基础】TD3 智能体类：与训练脚本同一实现，此处用于装载训练好的权重

import torch  # 【基础】PyTorch：张量运算（sigmoid 变换等）
import numpy as np  # 【基础】NumPy：向量范数与数组运算


# ── 类 SINGLE_SIM：固定场景（single 口径）测试环境 ──
# 职责：包装 IRSim，提供与训练环境 MARL_SIM 同构的 step/reset 十元组接口，
#       但语义不同——已到达的机器人动作被清零"原地冻结"（不换发新目标）；
#       reset 不做随机化，每局回到 YAML 定义的同一圆环布局。
# 输入输出：step(action, connection, combined_weights) → 十元组观测；
#       reset(...) → 十元组；get_reward(...) → float 奖励。
# 调用关系：本文件 main() 实例化并驱动；与 MARL_SIM 的语义差别正是
#       single / random 两种测试口径分歧的根源（详见各方法内注释）。
class SINGLE_SIM(SIM_ENV):  # 【基础】继承 SIM_ENV 基类的单场景测试环境
    """
    Simulation environment for multi-agent robot navigation using IRSim.

    This class extends the SIM_ENV and provides a wrapper for multi-robot
    simulation and interaction, supporting reward computation and custom reset logic.

    Attributes:
        env (object): IRSim simulation environment instance.
        robot_goal (np.ndarray): Current goal position(s) for the robots.
        num_robots (int): Number of robots in the environment.
        x_range (tuple): World x-range.
        y_range (tuple): World y-range.
    """

    # ── 方法 __init__：构造函数 ──
    # 职责：读世界 YAML 配置并创建 IRSim 环境，记录机数/世界范围/奖励版本。
    # 输入：world_file 世界配置、disable_plotting 无头开关、reward_phase 奖励版本。
    # 输出：无（初始化实例属性）；调用关系：main() 中被实例化一次。
    def __init__(  # 【基础】构造器定义（多行签名）
        self,  # 【基础】实例自身
        world_file="worlds/circle_world.yaml",  # 【基础】默认世界：12x12 场地，5 机以 (6,6) 为心、半径 4 的圆环分布，共享同一固定目标 (9,9)
        disable_plotting=False,  # 【基础】是否关闭渲染（main 里传 True 无头测试提速）
        reward_phase=2,  # 【基础】奖励版本：测试用 phase 2（与训练的 phase 1 不同；测试奖励只用于统计，不再引导策略）
    ):  # 【基础】构造器签名闭合括号
        """
        Initialize the MARL_SIM environment.

        Args:
            world_file (str, optional): Path to the world configuration YAML file.
            disable_plotting (bool, optional): If True, disables IRSim rendering and plotting.
        """
        display = False if disable_plotting else True  # 【基础】窗口显示开关：关绘图时连窗口一起关
        self.env = irsim.make(  # 【基础】按 YAML 配置创建 IRSim 环境实例
            world_file, disable_all_plot=disable_plotting, display=display  # 【基础】传世界文件与渲染/显示选项
        )  # 【基础】irsim.make 调用闭合
        self.num_robots = len(self.env.robot_list)  # 【基础】机器人数量（本世界为 5）
        self.x_range = self.env._world.x_range  # 【基础】世界 x 范围（供越界/目标采样用）
        self.y_range = self.env._world.y_range  # 【基础】世界 y 范围
        self.reward_phase = reward_phase  # 【基础】记住奖励版本号供 get_reward 分派

    # ── 方法 step：推进一步并产出十元组观测 ──
    # 职责：把策略动作下发给 IRSim（已到达的机器人动作清零冻结），随后逐机
    #       计算距离/朝向差/碰撞/到达/奖励，并按注意力权重绘制机间连线。
    # 输入：action=[[线速,角速],...]、connection=(5,4) 连接 logits、
    #       combined_weights=(5,4) 软注意力权重；输出：十元组（成员见 docstring）。
    # 调用关系：main 每步调用一次；reset 内部也调它拿初始观测。
    def step(self, action, connection, combined_weights=None):  # 【基础】单步接口：动作列表 + 连接张量 + 可选权重
        """
        Perform a simulation step for all robots using the provided actions and connections.

        Args:
            action (list): List of actions for each robot [[lin_vel, ang_vel], ...].
            connection (Tensor): Tensor of shape (num_robots, num_robots-1) containing logits indicating connections between robots.
            combined_weights (Tensor or None, optional): Optional weights for each connection, shape (num_robots, num_robots-1).

        Returns:
            tuple: (
                poses (list): List of [x, y, theta] for each robot,
                distances (list): Distance to goal for each robot,
                coss (list): Cosine of angle to goal for each robot,
                sins (list): Sine of angle to goal for each robot,
                collisions (list): Collision status for each robot,
                goals (list): Goal reached status for each robot,
                action (list): Actions applied,
                rewards (list): Rewards computed,
                positions (list): Current [x, y] for each robot,
                goal_positions (list): Goal [x, y] for each robot,
            )
        """
        act = [  # 【基础】构造实际下发的动作列表（已到者冻结）
            [0, 0] if self.env.robot_list[i].arrive else action[i]  # 【教学】与 MARL_SIM 的关键差别：到达的机器人动作置 [0,0] 原地不动（MARL_SIM 是换发新随机目标继续跑）——single 口径"到达即停"，才可能有"全员到达=成功"的判定
            for i in range(len(action))  # 【基础】逐机处理
        ]  # 【基础】act 冻结动作列表闭合
        self.env.step(action_id=[i for i in range(self.num_robots)], action=act)  # 【基础】驱动 IRSim：给 0..4 号机器人施加各自动作
        self.env.render()  # 【基础】渲染一帧（disable_plotting=True 时为空操作）

        poses = []  # 【基础】以下 9 个列表分别累积每台机器人的观测量
        distances = []  # 【基础】各机到目标距离
        coss = []  # 【基础】各机朝向差余弦
        sins = []  # 【基础】各机朝向差正弦
        collisions = []  # 【基础】各机碰撞标志
        goals = []  # 【基础】各机到达标志
        rewards = []  # 【基础】各机奖励
        positions = []  # 【基础】各机当前位置
        goal_positions = []  # 【基础】各机目标位置
        robot_states = [  # 【基础】预先缓存所有机器人的 (x,y)（下面算两两距离用）
            [self.env.robot_list[i].state[0], self.env.robot_list[i].state[1]]  # 【基础】第 i 台的 x,y 坐标
            for i in range(self.num_robots)  # 【基础】逐机提取
        ]  # 【基础】robot_states 位置缓存列表闭合
        for i in range(self.num_robots):  # 【基础】主循环：逐机计算观测与奖励

            robot_state = self.env.robot_list[i].state  # 【基础】第 i 台完整状态（x,y,θ 等）
            closest_robots = [  # 【基础】第 i 台到其他所有机器人的距离列表
                np.linalg.norm(  # 【基础】求二维欧氏范数（即距离）
                    [  # 【基础】坐标差向量
                        robot_states[j][0] - robot_state[0],  # 【基础】x 方向差
                        robot_states[j][1] - robot_state[1],  # 【基础】y 方向差
                    ]  # 【基础】坐标差向量闭合
                )  # 【基础】‖Δ‖=两机间距
                for j in range(self.num_robots)  # 【基础】遍历所有机器人
                if j != i  # 【基础】排除自身（得 N-1=4 个距离）
            ]  # 【基础】closest_robots 邻距列表闭合
            robot_goal = self.env.robot_list[i].goal  # 【基础】第 i 台的目标坐标（张量）
            goal_vector = [  # 【基础】由机器人指向目标的方向向量
                robot_goal[0].item() - robot_state[0].item(),  # 【基础】x 分量（.item() 把张量标量转 Python 数）
                robot_goal[1].item() - robot_state[1].item(),  # 【基础】y 分量
            ]  # 【基础】goal_vector 目标方向向量闭合
            distance = np.linalg.norm(goal_vector)  # 【基础】到目标的欧氏距离
            goal = self.env.robot_list[i].arrive  # 【基础】本步是否到达（位置模式，阈值 0.3m）
            pose_vector = [np.cos(robot_state[2]).item(), np.sin(robot_state[2]).item()]  # 【基础】机器人朝向的单位方向向量（用 cos/sin 表示避免角度 2π 突变）
            cos, sin = self.cossin(pose_vector, goal_vector)  # 【基础】基类静态工具：算朝向向量与目标向量的夹角余弦/正弦
            collision = self.env.robot_list[i].collision  # 【基础】本步碰撞标志（reactive 模式：互撞两机都置位）
            action_i = action[i]  # 【基础】第 i 台的输入动作（奖励函数要用）
            reward = self.get_reward(  # 【基础】计算第 i 台本步奖励
                goal, collision, action_i, closest_robots, distance, self.reward_phase  # 【基础】入参：到达/碰撞/动作/邻距表/目标距离/奖励版本
            )  # 【基础】get_reward 调用闭合

            position = [robot_state[0].item(), robot_state[1].item()]  # 【基础】第 i 台当前位置（浮点列表）
            goal_position = [robot_goal[0].item(), robot_goal[1].item()]  # 【基础】第 i 台目标位置

            distances.append(distance)  # 【基础】以下把本机各观测量加入对应列表
            coss.append(cos)  # 【基础】夹角余弦
            sins.append(sin)  # 【基础】夹角正弦
            collisions.append(collision)  # 【基础】碰撞标志
            goals.append(goal)  # 【基础】到达标志
            rewards.append(reward)  # 【基础】奖励值
            positions.append(position)  # 【基础】当前位置
            poses.append(  # 【基础】位姿三元组
                [robot_state[0].item(), robot_state[1].item(), robot_state[2].item()]  # 【基础】[x, y, θ]
            )  # 【基础】poses.append 调用闭合
            goal_positions.append(goal_position)  # 【基础】目标位置

            i_probs = torch.sigmoid(  # 【基础】把连接 logits 逐元素压到 (0,1) 概率
                connection[i]  # 【基础】第 i 台对其余 4 台的连接得分
            )  # connection[i] is logits for "connect" per pair  # 【基础】原注释：connection[i] 是逐对"是否连接"的 logits

            i_connections = i_probs.tolist()  # 【基础】概率张量转 Python 列表
            i_connections.insert(i, 0)  # 【基础】在位置 i 补自身列 0，把长度 4 还原成 5 以对齐全体机器人
            if combined_weights is not None:  # 【基础】若给了软权重则同样处理
                i_weights = combined_weights[i].tolist()  # 【基础】第 i 台的权重转列表
                i_weights.insert(i, 0)  # 【基础】同样补自身列 0

            for j in range(self.num_robots):  # 【基础】遍历全体机器人：决定画哪些注意力连线
                if i_connections[j] > 0.5:  # 【教学】连接概率过半才画线：注意力学的是"该关注谁"，图中连线即可视化的通讯拓扑（初始零 logits 时 sigmoid=0.5 不过阈，不画）
                    if combined_weights is not None:  # 【基础】有权重则线宽取权重
                        weight = i_weights[j]  # 【基础】i→j 的软注意力权重
                    else:  # 【基础】无权重回退
                        weight = 1  # 【基础】固定线宽 1
                    other_robot_state = self.env.robot_list[j].state  # 【基础】邻居 j 的状态
                    other_pos = [  # 【基础】邻居 j 的位置
                        other_robot_state[0].item(),  # 【基础】x 坐标
                        other_robot_state[1].item(),  # 【基础】y 坐标
                    ]  # 【基础】邻居位置列表闭合
                    rx = [position[0], other_pos[0]]  # 【基础】连线两端的 x 坐标
                    ry = [position[1], other_pos[1]]  # 【基础】连线两端的 y 坐标
                    self.env.draw_trajectory(  # 【基础】在仿真图上画线段
                        np.array([rx, ry]), refresh=True, linewidth=weight  # 【基础】线段坐标 / 每帧刷新 / 线宽=注意力权重（权重大=关注强=线粗）
                    )  # 【基础】draw_trajectory 画线调用闭合

        return (  # 【基础】按约定顺序返回十元组（与训练环境同构）
            poses,  # 【基础】位姿列表
            distances,  # 【基础】目标距离列表
            coss,  # 【基础】夹角余弦列表
            sins,  # 【基础】夹角正弦列表
            collisions,  # 【基础】碰撞标志列表
            goals,  # 【基础】到达标志列表
            action,  # 【基础】原样回传的入参动作
            rewards,  # 【基础】奖励列表
            positions,  # 【基础】当前位置列表
            goal_positions,  # 【基础】目标位置列表
        )  # 【基础】step 返回十元组闭合

    # ── 方法 reset：重置回 YAML 固定布局 ──
    # 职责：调 env.reset() 回到 circle_world 定义的同一初始状态（不随机化），
    #       再以全零动作走一步产出初始观测十元组。
    # 输入：4 个可选参数本脚本均未使用（保留与 MARL_SIM 相同签名）；
    #       输出：碰撞/到达全 False 的十元组。
    # 调用关系：main 的回合终止分支调用；是 single 口径"同一场景测 100 遍"的关键。
    def reset(  # 【基础】重置方法定义（多行签名）
        self,  # 【基础】实例自身
        robot_state=None,  # 【基础】可选：指定初始状态（未用，None 走 YAML 默认）
        robot_goal=None,  # 【基础】可选：指定目标（未用）
        random_obstacles=False,  # 【基础】可选：随机化障碍物（未用，本世界无障碍物）
        random_obstacle_ids=None,  # 【基础】可选：随机化哪些障碍物 id（未用）
    ):  # 【基础】reset 方法签名闭合括号
        """
        Reset the simulation environment and optionally set robot and obstacle positions.

        Args:
            robot_state (list or None, optional): Initial state for robots as [x, y, theta, speed].
            robot_goal (list or None, optional): Goal position(s) for the robots.
            random_obstacles (bool, optional): If True, randomly position obstacles.
            random_obstacle_ids (list or None, optional): IDs of obstacles to randomize.

        Returns:
            tuple: (
                poses (list): List of [x, y, theta] for each robot,
                distances (list): Distance to goal for each robot,
                coss (list): Cosine of angle to goal for each robot,
                sins (list): Sine of angle to goal for each robot,
                collisions (list): All False after reset,
                goals (list): All False after reset,
                action (list): Initial action ([[0.0, 0.0], ...]),
                rewards (list): Rewards for initial state,
                positions (list): Initial [x, y] for each robot,
                goal_positions (list): Initial goal [x, y] for each robot,
            )
        """
        self.env.reset()  # 【教学】只做原生 reset：机器人回到 YAML 圆环初始位姿、目标回到固定 (9,9)——与 MARL_SIM.reset 的随机抽样形成 single/random 口径对比
        self.robot_goal = self.env.robot.goal  # 【基础】记录默认机器人的目标（实例属性）

        action = [[0.0, 0.0] for _ in range(self.num_robots)]  # 【基础】初始动作全零
        con = torch.tensor(  # 【基础】零连接张量（与训练脚本初始连接一致）
            [[0.0 for _ in range(self.num_robots - 1)] for _ in range(self.num_robots)]  # 【基础】形状 (5,4) 全零
        )  # 【基础】con 零连接张量闭合
        poses, distance, cos, sin, _, _, action, reward, positions, goal_positions = (  # 【基础】零动作推进一步拿初始观测（第 5、6 位碰撞/到达丢弃）
            self.step(action, con)  # 【基础】调用本类 step 完成首步
        )  # 【基础】初始步解包闭合
        return (  # 【基础】返回十元组：碰撞与到达固定为全 False（刚重置）
            poses,  # 【基础】初始位姿
            distance,  # 【基础】初始距离
            cos,  # 【基础】初始夹角余弦
            sin,  # 【基础】初始夹角正弦
            [False] * self.num_robots,  # 【基础】碰撞标志全 False
            [False] * self.num_robots,  # 【基础】到达标志全 False
            action,  # 【基础】全零初始动作
            reward,  # 【基础】初始状态奖励
            positions,  # 【基础】初始位置
            goal_positions,  # 【基础】目标位置
        )  # 【基础】reset 返回十元组闭合

    # ── 方法 get_reward（静态）：奖励计算 ──
    # 职责：按 reward_phase 分派奖励公式；phase 2=到达+70 / 碰撞 -300·线速度 /
    #       3m 内邻居二次方邻近惩罚 / -0.5·|角速度|（无距离引导项）。
    # 输入：单机到达/碰撞/动作/邻距表/目标距离/版本号；输出：float 奖励。
    # 调用关系：step 内逐机调用；测试期奖励仅用于性能统计，不影响已训练策略的动作。
    @staticmethod  # 【基础】静态方法装饰器：不依赖实例状态即可调用
    def get_reward(goal, collision, action, closest_robots, distance, phase=2):  # 【基础】奖励函数签名（默认 phase=2）
        """
        Calculate the reward for a robot given the current state and action.

        Args:
            goal (bool): Whether the robot reached its goal.
            collision (bool): Whether a collision occurred.
            action (list): [linear_velocity, angular_velocity] applied.
            closest_robots (list): Distances to the closest other robots.
            distance (float): Distance to the goal.
            phase (int, optional): Reward phase/function selector (default: 1).

        Returns:
            float: Computed reward.
        """

        match phase:  # 【基础】Python 3.10+ 的 match-case 结构化匹配：按奖励版本分派（类似 switch）
            case 1:  # 【基础】版本 1（训练环境用）：带距离引导项
                if goal:  # 【基础】到达分支
                    return 100.0  # 【基础】到达大奖 +100
                elif collision:  # 【基础】碰撞分支
                    return -100.0 * 3 * action[0]  # 【教学】碰撞罚金 -300·线速度：撞得越快罚越重（鼓励慢行避碰）
                else:  # 【基础】正常行进分支
                    r_dist = 1.5 / distance  # 【教学】距离引导项：离目标越近每步奖励越高（势能差式 shaping，加速收敛）
                    cl_pen = 0  # 【基础】邻近惩罚累加器置零
                    for rob in closest_robots:  # 【基础】遍历到其他机器人的距离
                        add = 1.5 - rob if rob < 1.5 else 0  # 【基础】1.5m 内线性罚（越近罚越大），之外为 0
                        cl_pen += add  # 【基础】累加惩罚

                    return action[0] - 0.5 * abs(action[1]) - cl_pen + r_dist  # 【教学】phase 1 合成奖励：+线速度（鼓励前进）-0.5|角速度|（抑制抖动）-邻近惩罚+距离引导

            case 2:  # 【基础】版本 2（本测试默认）：无距离引导、惩罚更陡
                if goal:  # 【基础】到达分支
                    return 70.0  # 【基础】到达奖 +70（比 phase 1 低）
                elif collision:  # 【基础】碰撞分支
                    return -100.0 * 3 * action[0]  # 【基础】同样 -300·线速度
                else:  # 【基础】正常行进分支
                    cl_pen = 0  # 【基础】邻近惩罚累加器
                    for rob in closest_robots:  # 【基础】遍历邻距
                        add = (3 - rob) ** 2 if rob < 3 else 0  # 【教学】3m 内二次方罚（比 phase 1 的 1.5m 线性罚范围更大、曲线更陡——更强调相互避让）
                        cl_pen += add  # 【基础】累加惩罚

                    return -0.5 * abs(action[1]) - cl_pen  # 【教学】phase 2 合成奖励：仅 -0.5|角速度|-邻近惩罚，无前进/距离奖励——纯"安全平稳"口径

            case _:  # 【基础】其余版本兜底分支
                raise ValueError("Unknown reward phase")  # 【基础】非法版本号直接抛错


# ── 函数 outside_of_bounds：出界检测 ──
# 职责：判断是否有机器人跑出以世界中心 (6,6) 为心、半边长 10.5 的正方形边界。
# 输入：poses——各机器人位姿列表，每个元素为 [x, y, theta]；输出：布尔值。
# 调用关系：主循环每步调用；注意本脚本的终止条件实际未使用其返回值（见下）。
def outside_of_bounds(poses):  # 【基础】函数定义：接收所有机器人的位姿列表
    """
    Check if any robot is outside the defined world boundaries.

    Args:
        poses (list): List of [x, y, theta] poses for each robot.

    Returns:
        bool: True if any robot is outside the 21x21 area centered at (6, 6), else False.
    """
    outside = False  # 【基础】出界标志初始化为 False
    for pose in poses:  # 【基础】逐台机器人检查
        norm_x = pose[0] - 6  # 【基础】x 坐标对世界中心 6 取偏移
        norm_y = pose[1] - 6  # 【基础】y 坐标对世界中心 6 取偏移
        if abs(norm_x) > 10.5 or abs(norm_y) > 10.5:  # 【基础】任一方向偏心超过 10.5 判出界（世界实际 12x12，阈属冗余）
            outside = True  # 【基础】置出界标志
            break  # 【基础】提前退出循环
    return outside  # 【基础】返回是否出界


# ── 函数 main：single 固定场景测试主入口 ──
# 职责：加载训练产物 TDR-MARL-train 权重，在 circle_world 固定圆环场景连跑
#       100 局，统计无碰撞成功率、平均到达数、平均局长与超时局数。
# 输入：args=None（占位）；输出：无返回值，结果打印到控制台（不写 TensorBoard）。
# 调用关系：文件底部 if __name__ 直接调用；与 marl_test_random.py 共用同一份
#       训练权重，差别在场景固定 vs 随机、终止条件与统计口径（见循环内注释）。
def main(args=None):  # 【基础】主函数定义（args 未使用）
    """Main training function"""

    # ---- Hyperparameters and setup ----  # 【基础】分节注释：以下为测试超参与设置
    action_dim = 2  # number of actions produced by the model  # 【基础】动作维度 2（必须与训练一致）
    max_action = 1  # maximum absolute value of output actions  # 【基础】动作幅值上限 1（与训练一致）
    state_dim = 11  # number of input values in the neural network (vector length of state input)  # 【基础】状态维度 11（与训练一致——加载权重的形状必须对得上）
    device = torch.device(  # 【基础】选择计算设备
        "cuda" if torch.cuda.is_available() else "cpu"  # 【基础】有 GPU 用 cuda 否则 cpu
    )  # using cuda if it is available, cpu otherwise  # 【基础】device 传给 TD3 构造器
    epoch = 1  # starting epoch number  # 【基础】轮号变量：本脚本后续未使用（与训练脚本同构的遗留变量）
    episode = 0  # 【基础】测试局计数从 0 起（这里是 100 局的计数器，不是训练轮）
    max_steps = 600  # maximum number of steps in single episode  # 【教学】单局上限 600 步（训练是 300）：给足时间观察策略能否全员到达；超时计入 ran_out_of_time
    steps = 0  # starting step number  # 【基础】局内步数计数器
    save_every = 5  # save the model every n training cycles  # 【基础】存档间隔：测试不调用 train()，实际不会存档（同构遗留参数）
    test_scenarios = 100  # 【教学】测试规模：同一固定场景重复 100 局（random 口径是 1000 局随机场景）

    # ---- Instantiate simulation environment and model ----  # 【基础】分节注释：建环境与模型
    sim = SINGLE_SIM(  # 【基础】实例化固定场景测试环境（本文件自定义类）
        world_file="worlds/circle_world.yaml", disable_plotting=True, reward_phase=2  # 【基础】圆环世界 / 无头模式 / phase 2 奖励（仅统计用）
    )  # instantiate environment  # 【基础】每局 reset 回同一布局

    model = TD3(  # 【基础】实例化 TD3（网络结构与训练时一致，用于装载权重）
        state_dim=state_dim,  # 【基础】状态维度 11
        action_dim=action_dim,  # 【基础】动作维度 2
        max_action=max_action,  # 【基础】动作界 ±1
        num_robots=sim.num_robots,  # 【基础】机器人数 5（与训练一致）
        device=device,  # 【基础】计算设备
        save_every=save_every,  # 【基础】存档间隔（测试中不触发）
        load_model=True,  # 【教学】关键差别：True——构造时立即从 load_directory/load_model_name 加载训练好的四个 .pth（训练脚本此处为 False）
        model_name="TDR-MARL-test",  # 【基础】本实例命名：TensorBoard 日志 comment 后缀；不训练就不会产生存档
        load_model_name="TDR-MARL-train",  # 【教学】加载名=训练脚本的存档名——训练与测试的"交接约定"就在这一行（checkpoint 目录下的 TDR-MARL-train_*.pth 四件套）
        load_directory=Path("robot_nav/models/MARL/marlTD3/checkpoint"),  # 【基础】加载目录（与训练存档目录相同）
        attention="igs",  # 【教学】注意力后端 "igs"=IGA 注意力（iga.py 的 Attention 类）：结构强绑定，必须与训练用的一致才能对上权重；注：训练脚本写的 "iga" 是非法值（TD3 构造器只认 igs/g2anet，见 marl_train.py 注释）
    )  # instantiate a model  # 【基础】构造完成即已载入训练权重（load 内部打印 Loaded weights from: ...）

    connections = torch.tensor(  # 【基础】初始零连接张量
        [[0.0 for _ in range(sim.num_robots - 1)] for _ in range(sim.num_robots)]  # 【基础】形状 (5,4) 全零
    )  # 【基础】connections 零连接张量闭合

    # ---- Take initial step in environment ----  # 【基础】分节注释：取初始观测
    poses, distance, cos, sin, collision, goal, a, reward, positions, goal_positions = (  # 【基础】十元组解包起始行
        sim.step([[0, 0] for _ in range(sim.num_robots)], connections)  # 【基础】全零动作迈出第一步
    )  # get the initial step state  # 【基础】得到初始观测 s0
    running_goals = 0  # 【基础】本局累计到达标志数
    running_reward = 0  # 【基础】本局累计奖励（5 机求和）
    running_collisions = 0  # 【基础】本局累计碰撞标志数（注意：此处不除 2，最后统一 /2）
    running_timesteps = 0  # 【基础】本局步数
    ran_out_of_time = 0  # 【基础】超时局数统计（600 步用尽仍未全员到达）

    reward_per_ep = []  # 【基础】以下 8 个容器按"局/步"累积统计样本
    goals_per_ep = []  # 【基础】每局总到达数
    col_per_ep = []  # 【基础】每局碰撞标志累计
    lin_actions = []  # 【基础】所有步所有机的线速度样本（供分布分析）
    ang_actions = []  # 【基础】角速度样本
    entropy_list = []  # 【基础】每步注意力权重熵样本
    timesteps_per_ep = []  # 【基础】每局用时（步数）
    epsilon = 1e-6  # 【基础】数值稳定小量：防 log(0) 与除零
    pbar = tqdm(total=test_scenarios)  # 【基础】进度条：总数 100 局
    while episode < test_scenarios:  # 【教学】测试主循环：跑满 100 局即结束（对照训练的 while epoch < max_epochs）
        state, terminal = model.prepare_state(  # 【基础】编码当前观测为每机 11 维状态（与训练同一函数）
            poses, distance, cos, sin, collision, a, goal_positions  # 【基础】原始十元组字段
        )  # 【基础】prepare_state 调用闭合
        action, connection, combined_weights = model.get_action(  # 【基础】已训练策略前向：一次出 5 机动作+连接+权重
            np.array(state), False  # 【教学】add_noise=False：测试不加探索噪声，纯确定性策略——评估口径的核心（探索噪声只属于训练）
        )  # get an action from the model  # 【基础】动作形状 (5,2)

        combined_weights_norm = combined_weights / (  # 【基础】注意力权重按行归一化成分布
            combined_weights.sum(dim=-1, keepdim=True) + epsilon  # 【基础】每行求和（keepdim 保形）+ε 防除零
        )  # 【基础】权重归一化表达式闭合

        entropy = (  # 【基础】计算注意力分布熵（多行表达式开始）
            (  # 【基础】内层括号
                -(combined_weights_norm * (combined_weights_norm + epsilon).log())  # 【教学】熵公式 -Σ p·log p 的逐元素部分：p+ε 再取对数保证数值稳定；熵低=注意力集中（只盯少数邻居），熵高=注意力分散
                .sum(dim=-1)  # 【基础】对邻居维求和 → 每台机器人一个熵值
                .mean()  # 【基础】对 5 台机器人取平均 → 标量
            )  # 【基础】内层括号闭合
            .data.cpu()  # 【基础】.data 取值（不带梯度）并搬回 CPU
            .numpy()  # 【基础】转 NumPy 标量便于累计统计
        )  # 【基础】熵表达式闭合
        entropy_list.append(entropy)  # 【基础】记录本步熵

        a_in = [[(a[0] + 1) / 4, a[1]] for a in action]  # 【基础】与训练相同的动作重标度：线速 [-1,1]→[0,0.5] m/s，角速直传（到达机器人会在环境内被清零冻结）

        (  # 【基础】环境新十元组解包开始
            poses,  # 【基础】新位姿
            distance,  # 【基础】新距离
            cos,  # 【基础】夹角余弦
            sin,  # 【基础】夹角正弦
            collision,  # 【基础】碰撞标志
            goal,  # 【基础】到达标志
            a,  # 【基础】已执行动作
            reward,  # 【基础】奖励（phase 2 口径）
            positions,  # 【基础】当前位置
            goal_positions,  # 【基础】目标位置
        ) = sim.step(  # 【基础】推进一步
            a_in, connection, combined_weights  # 【基础】动作+连接+权重（后两者用于画注意力边）
        )  # get data from the environment  # 【教学】SINGLE_SIM 语义：已到达的机器人本步起动作被清零，停在原地等其余队友
        running_goals += sum(goal)  # 【基础】累计每步到达标志数（已到者保持置位，随步数增长）
        running_collisions += sum(collision)  # 【基础】累计碰撞标志（原始计数，未 /2）
        running_reward += sum(reward)  # 【基础】累计 5 机奖励和
        running_timesteps += 1  # 【基础】步数 +1
        for j in range(len(a_in)):  # 【基础】逐机收集动作样本
            lin_actions.append(a_in[j][0].item())  # 【基础】线速度样本（张量转 float）
            ang_actions.append(a_in[j][1].item())  # 【基础】角速度样本
        outside = outside_of_bounds(poses)  # 【基础】出界检测——注意：本脚本的终止条件并未使用该返回值（与 train/random 不同；固定圆环场景基本不会出界）

        if (  # 【基础】回合终止判定开始
            sum(collision) > 0.5 or steps == max_steps or int(sum(goal)) == len(goal)  # 【教学】single 口径三条件：任一机碰撞 / 600 步超时 / 全员到达（int(sum(goal))==5 即成功局）；对照 random 口径=碰撞/超时/出界且无"全员到达"（那里到达不终结）
        ):  # reset environment of terminal state reached, or max_steps were taken  # 【基础】进入重置分支
            (  # 【基础】重置十元组解包（回到同一固定布局）
                poses,  # 【基础】新局位姿（同 YAML 圆环）
                distance,  # 【基础】新局距离
                cos,  # 【基础】新局夹角余弦
                sin,  # 【基础】新局夹角正弦
                collision,  # 【基础】全 False
                goal,  # 【基础】全 False
                a,  # 【基础】全零动作
                reward,  # 【基础】初始奖励
                positions,  # 【基础】初始位置
                goal_positions,  # 【基础】固定目标 (9,9)
            ) = sim.reset()  # 【基础】重置调用闭合（回到同一固定布局）
            reward_per_ep.append(running_reward)  # 【基础】记录本局总奖励
            running_reward = 0  # 【基础】清零
            goals_per_ep.append(running_goals)  # 【基础】记录本局累计到达数
            running_goals = 0  # 【基础】清零
            col_per_ep.append(running_collisions)  # 【基础】记录本局碰撞标志累计
            running_collisions = 0  # 【基础】清零
            timesteps_per_ep.append(running_timesteps)  # 【基础】记录本局步数
            running_timesteps = 0  # 【基础】清零
            if steps == max_steps:  # 【基础】若是超时收局
                ran_out_of_time += 1  # 【基础】超时局数 +1

            steps = 0  # 【基础】新局步数清零
            episode += 1  # 【基础】完成局数 +1
            pbar.update(1)  # 【基础】进度条前进 1
        else:  # 【基础】未终止继续本局
            steps += 1  # 【基础】步数 +1

    cols = sum(col_per_ep) / 2  # 【教学】碰撞对数核算：reactive 模式下一对互撞两机各置位一次，/2 还原为"事件数"；因首次碰撞立即收局，每个碰撞失败局恰贡献 1 对 → cols≈碰撞失败局数
    goals_per_ep = np.array(goals_per_ep, dtype=np.float32)  # 【基础】每局到达数转 float32 数组（供统计计算）
    col_per_ep = np.array(col_per_ep, dtype=np.float32)  # 【基础】每局碰撞数转数组
    avg_ep_col = statistics.mean(col_per_ep)  # 【基础】平均每局碰撞标志数
    avg_ep_col_std = statistics.stdev(col_per_ep)  # 【基础】样本标准差（波动幅度）
    avg_ep_goals = statistics.mean(goals_per_ep)  # 【基础】平均每局累计到达数
    avg_ep_goals_std = statistics.stdev(goals_per_ep)  # 【基础】标准差
    t_per_ep = np.array(timesteps_per_ep, dtype=np.float32)  # 【基础】每局步数转数组
    avg_ep_t = statistics.mean(t_per_ep)  # 【基础】平均局长（步）
    avg_ep_t_std = statistics.stdev(t_per_ep)  # 【基础】标准差

    print(f"avg_ep_col: {avg_ep_col}")  # 【基础】输出平均每局碰撞
    print(f"avg_ep_col_std: {avg_ep_col_std}")  # 【基础】输出碰撞波动
    print(f"success rate: {test_scenarios - cols}")  # 【教学】成功率口径=总局数-碰撞失败局数（只扣碰撞不扣超时，超时局另列 ran out of time——严格说这是"无碰撞局数"，与"全员到达局数"并不等价）
    print(f"avg_ep_goals: {avg_ep_goals}")  # 【基础】输出平均到达数
    print(f"avg_ep_goals_std: {avg_ep_goals_std}")  # 【基础】输出到达波动
    print(f"avg_ep_t: {avg_ep_t}")  # 【基础】输出平均局长
    print(f"avg_ep_t_std: {avg_ep_t_std}")  # 【基础】输出局长波动
    print(f"ran out of time: {ran_out_of_time}")  # 【基础】输出超时局数（600 步未全员到达）
    print("..............................................")  # 【基础】结果分隔线


if __name__ == "__main__":  # 【基础】仅当直接运行本文件时执行测试
    main()  # 【基础】启动 single 口径测试
