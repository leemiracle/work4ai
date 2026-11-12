# ============================================================================
# 模块: marl_sim.py —— 多机器人(Multi-Agent)导航仿真环境(继承 SIM_ENV)
# 职责: 封装 IRSim 的多机器人世界, 一步同时驱动 N 台差速机器人,
#       为每台单独计算奖励(接近项/碰撞项/机间避让项), 并把注意力
#       网络输出的"机间连接权重"画成可视化边。
# 被谁调用: marl_train.py / marl_test_*.py 通过 MARL_SIM(...) 实例化。
# 世界配置实证(robot_nav/worlds/multi_robot_world.yaml):
#   * 世界 12x12 m(x/y 范围 [0,12] m), step_time=0.3 s;
#   * 5 个差速机器人(diff), 圆形半径 0.2 m, 初始圆形分布(半径 4 m,
#     圆心 (6,6)), 线速度 v∈[0,0.5] m/s, 角速度 ω∈[-1,1] rad/s;
#   * goal_threshold=0.3 m(距目标 0.3 m 内判到达);
#   * 本世界没有配置任何传感器 -> 多机观测是几何量(pose/distance/
#     cos/sin/机间距离), 不用激光; 单机环境的激光在 sim.py。
# 与单机版的关键差异(教学档):
#   1) action 是"每台机器人一个 [v, ω]"的列表(动作空间=单机动作×N);
#   2) 奖励里的"避障"由机间距离 closest_robots 承担(1.25 m/3 m 阈值),
#      不再用激光最小值;
#   3) reward_phase 课程开关: phase 1(前期, 密集塑造) -> phase 2
#      (后期, 塑造项退场, 只留转向+安全间距惩罚);
#   4) 到达目标不结束 episode, 而是立刻换一个新随机目标(持续导航)。
# ============================================================================
import irsim  # IRSim 2D 机器人仿真库(世界解析/运动学/渲染)
import numpy as np  # 数值计算: 欧氏范数/数组
import random  # 随机采样: 初始位姿/目标位置
import torch  # PyTorch: reset 里构造零张量 connection(兼容网络输入类型)

from robot_nav.SIM_ENV.sim_env import SIM_ENV  # 抽象基类: step/reset/get_reward 接口契约


# ---- 多机器人环境类: N 台机器人同步推进, 逐机计算奖励 ----
class MARL_SIM(SIM_ENV):
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

    # (类 docstring 按规范原样保留)
    # ---- 构造函数: 加载多机器人世界并缓存规模/边界 ----
    # 输入: world_file=世界 YAML; disable_plotting=无头训练开关;
    #       reward_phase=奖励函数变体(1 或 2, 课程学习用)
    def __init__(
        self,  # 构造函数主体(多行签名)
        world_file="multi_robot_world.yaml",  # 默认多机器人世界(12x12 m, 5 台 diff 机器人)
        disable_plotting=False,  # True 时关闭全部画图(无头训练提速)
        reward_phase=1,  # 奖励相位: 1=前期密集塑造, 2=后期塑造退场(见 get_reward)
    ):  # 多行签名结束
        """
        Initialize the MARL_SIM environment.

        Args:
            world_file (str, optional):
                Path to an IRSim YAML world configuration. Defaults to
                "multi_robot_world.yaml".
            disable_plotting (bool, optional):
                If True, disables all IRSim plotting and display windows.
                Useful for headless training. Defaults to False.
            reward_phase (int, optional):
                Selects the reward function variant used by `get_reward`.
                Supported values: {1, 2}. Defaults to 1.
        """
        display = False if disable_plotting else True  # display 与 disable_plotting 取反(无头时不弹窗)
        self.env = irsim.make(  # 解析 YAML -> 生成多机器人仿真环境实例
            world_file, disable_all_plot=disable_plotting, display=display  # 画图总开关 + 显示开关
        )  # irsim.make(...) 结束, 环境实例挂到 self.env
        robot_info = self.env.get_robot_info(0)  # 取 0 号机器人信息对象(代表)
        self.robot_goal = robot_info.goal  # 缓存 0 号目标(3x1 列向量, 米/弧度); 注意 step/reset 会各自刷新
        self.num_robots = len(self.env.robot_list)  # 机器人总数 N(YAML 实证默认 5)
        self.x_range = self.env._world.x_range  # 世界 x 范围(米; 12x12 世界即 [0.0, 12.0])
        self.y_range = self.env._world.y_range  # 世界 y 范围(米)
        self.reward_phase = reward_phase  # 记住奖励相位, step 里透传给 get_reward

    # ---- step: 一次驱动全部 N 台机器人并逐机收集观测/奖励 ----
    # 输入: action=[[v,ω]]*N(米/秒 与 弧度/秒); connection=注意力 logits
    #       (本方法不消费, 仅保持接口); combined_weights=机间边权(仅画图)
    # 输出: 10 元组(poses/distances/coss/sins/collisions/goals/action/
    #       rewards/positions/goal_positions), 各元素按机器人编号排列
    # 被谁调用: marl_train.py 主循环每步; 本类 reset 尾部(零动作)也调它
    def step(self, action, connection, combined_weights=None):
        """
        Perform a simulation step for all robots using the provided actions and connections.

        Args:
            action (list):
                A list of length `num_robots`. Each element is
                `[linear_velocity, angular_velocity]` to be applied to the
                corresponding robot for this step. Units follow IRSim's
                kinematics setup (typically m/s and rad/s).
            connection (Tensor):
                A torch.Tensor of shape `(num_robots, num_robots-1)` containing
                *logits* that indicate pairwise connections per robot *without*
                the self-connection column. This is not used for logic here,
                but preserved for compatibility (see commented code); you may
                use it upstream to form `combined_weights`.
            combined_weights (Tensor or None, optional):
                A torch.Tensor of shape `(num_robots, num_robots)` **or**
                `(num_robots, num_robots-1)` that encodes visualization weights
                for robot-to-robot edges. When provided, edges from robot *i* to
                *j* are drawn with line width `weight * 2`. If you pass the
                `(num_robots, num_robots-1)` form, ensure indexing aligns with
                how you constructed it (self-column typically omitted).

        Returns:
            tuple:
                (
                    poses (list[list[float]]):
                        `[x, y, theta]` for each robot after the step.
                    distances (list[float]):
                        Euclidean distance from each robot to its goal.
                    coss (list[float]):
                        Cosine of the angle between robot heading and goal vector.
                    sins (list[float]):
                        Sine of the angle between robot heading and goal vector.
                    collisions (list[bool]):
                        Collision flags for each robot, as reported by IRSim.
                    goals (list[bool]):
                        Arrival flags for each robot. If True this step, a new
                        random goal was scheduled for that robot.
                    action (list):
                        Echo of the input `action`.
                    rewards (list[float]):
                        Per-robot rewards computed by `get_reward(...)`.
                    positions (list[list[float]]):
                        `[x, y]` positions for each robot after the step.
                    goal_positions (list[list[float]]):
                        `[x, y]` goal coordinates for each robot after any
                        arrival updates this step.
                )
        """
        # (上方长 docstring 原样保留; 以下为 step 主体)
        self.env.step(action_id=[i for i in range(self.num_robots)], action=action)  # 批量驱动: id 列表 0..N-1 与 action 一一对应, 一次推进全部机器人 0.3 s
        self.env.render()  # 渲染一帧(无头时为空操作); 物理已在上一步推进, 这里只刷显示

        poses = []  # 每台机器人 [x, y, θ](米/弧度) 的累积列表
        distances = []  # 每台到各自目标的欧氏距离(米)
        coss = []  # 每台"朝向 vs 目标方向"夹角的余弦(无量纲)
        sins = []  # 每台对应正弦(无量纲; 与 cos 联立编码目标方位)
        collisions = []  # 每台本步碰撞标志
        goals = []  # 每台本步到达标志
        rewards = []  # 每台本步奖励(标量)
        positions = []  # 每台 [x, y] 位置(米)——与 poses 的差别是不含朝向
        goal_positions = []  # 每台目标 [x, y](米)
        robot_states = [  # 先拍一份"步后位置快照"(每台 [x, y])——循环里算机间距离全用这份快照, 保证用同一步的一致状态
            [self.env.robot_list[i].state[0], self.env.robot_list[i].state[1]]  # 取第 i 台的 x, y 分量(米)
            for i in range(self.num_robots)  # 列表推导遍历所有机器人
        ]  # robot_states = N x [x, y] 位置快照(米)
        for i in range(self.num_robots):  # ---- 逐机器人收集观测与奖励 ----

            robot_state = self.env.robot_list[i].state  # 第 i 台完整状态 [x, y, θ, ...](米/弧度)
            closest_robots = [  # 到"其余每台机器人"的欧氏距离列表(米), 长度 N-1: 奖励里的机间避让项要用
                np.linalg.norm(  # 2D 欧氏范数 = √(Δx²+Δy²)
                    [  # 位移向量列表开始
                        robot_states[j][0] - robot_state[0],  # Δx = x_j - x_i(米, 用步后快照)
                        robot_states[j][1] - robot_state[1],  # Δy = y_j - y_i(米)
                    ]  # 位移向量 [Δx, Δy](米)
                )  # norm(...) 返回 i 到 j 的距离(米)
                for j in range(self.num_robots)  # 遍历全部机器人
                if j != i  # 跳过自己(自己到自己距离恒 0, 无意义)
            ]  # closest_robots = 长度 N-1 的距离列表(米)
            robot_goal = self.env.robot_list[i].goal  # 第 i 台当前目标(3x1 列向量; 到达换新后会变)
            goal_vector = [  # 目标方向向量(米) = 目标 - 当前位置
                robot_goal[0].item() - robot_state[0].item(),  # Δx(米); .item() 张量标量 -> float
                robot_goal[1].item() - robot_state[1].item(),  # Δy(米)
            ]  # goal_vector = [Δx, Δy] 指向目标的平移向量(米)
            distance = np.linalg.norm(goal_vector)  # 到目标欧氏距离(米)
            goal = self.env.robot_list[i].arrive  # 到达标志(距目标 < 0.3 m 时 True)
            pose_vector = [np.cos(robot_state[2]).item(), np.sin(robot_state[2]).item()]  # 朝向单位向量 (cosθ, sinθ)
            cos, sin = self.cossin(pose_vector, goal_vector)  # 父类工具: 朝向与目标方向夹角的 (cos φ, sin φ)
            collision = self.env.robot_list[i].collision  # 第 i 台碰撞标志
            action_i = action[i]  # 第 i 台本步动作 [v, ω](奖励里要用于前进/转向分项)
            reward = self.get_reward(  # 逐机奖励(静态方法; 见文件末尾的分项拆解)
                goal, collision, action_i, closest_robots, distance, self.reward_phase  # 传: 到达/碰撞/动作/机间距离/目标距离/相位
            )  # get_reward(...) 结束, 返回本机标量奖励

            position = [robot_state[0].item(), robot_state[1].item()]  # 本机 [x, y](米)——positions 列表用
            goal_position = [robot_goal[0].item(), robot_goal[1].item()]  # 本机目标 [x, y](米)

            distances.append(distance)  # 累积距离(米)
            coss.append(cos)  # 累积 cos
            sins.append(sin)  # 累积 sin
            collisions.append(collision)  # 累积碰撞标志
            goals.append(goal)  # 累积到达标志
            rewards.append(reward)  # 累积奖励
            positions.append(position)  # 累积位置
            poses.append(  # 累积完整位姿 [x, y, θ](米/弧度)——多机观测的主干
                [robot_state[0].item(), robot_state[1].item(), robot_state[2].item()]  # 三分量打包
            )  # poses.append(...) 结束
            goal_positions.append(goal_position)  # 累积目标位置(米)

            if combined_weights is not None:  # 注意力权重可视化: 取第 i 行转 python 列表
                i_weights = combined_weights[i].tolist()  # 行内是 i 对其他机器人的边权(形状随上游构造, 见下方坑注)

            for j in range(self.num_robots):  # ---- 画 i->j 的注意力边(双重循环, 共 N 条/每 i) ----
                if combined_weights is not None:  # 只在有权重时取
                    weight = i_weights[j]  # 边宽 = 权重×2(下方 draw_trajectory)
                # 潜在坑(代码实证, 静态): combined_weights=None 时 weight 从未赋值
                #   -> 下方 linewidth=weight*2 会 NameError; 作者注释掉的两行
                #   else/weight=1 正是为该分支预留的修复位。
                # 潜在坑(实测): 上游 G2ANet 输出形状 (N, N-1)(g2anet.py 实测
                #   comb shape=(5,4)), 行长 N-1 < N, 本循环 j 取到 N-1 时
                #   i_weights[N-1] 越界 IndexError——docstring 里"ensure
                #   indexing aligns"的警告即指此处; 传 (N,N) 补齐自列可避开。
                    # else:
                    #     weight = 1
                    other_robot_state = self.env.robot_list[j].state  # 对端机器人 j 的状态(米/弧度)
                    other_pos = [  # 对端 [x, y](米)
                        other_robot_state[0].item(),  # x_j(米)
                        other_robot_state[1].item(),  # y_j(米)
                    ]  # other_pos = [x_j, y_j](米)
                    rx = [position[0], other_pos[0]]  # 线段两端 x 坐标(i 端, j 端; 米)
                    ry = [position[1], other_pos[1]]  # 线段两端 y 坐标(米)
                    self.env.draw_trajectory(  # 在画布上画这条 i->j 的边(注意力可视化)
                        np.array([rx, ry]), refresh=True, linewidth=weight * 2  # 2x2 坐标数组; refresh=True 每步重画; 线宽=2×边权(注意力越强线越粗)
                    )  # draw_trajectory(...) 结束, 本条 i->j 边画完

            if goal:  # 本步到达 -> 立刻换新随机目标(episode 不终止: 持续导航式课程)
                self.env.robot_list[i].set_random_goal(  # IRSim 随机目标采样(内部避开障碍)
                    obstacle_list=self.env.obstacle_list,  # 障碍列表(采样时剔除重叠)
                    init=True,  # 按初始状态登记
                    range_limits=[  # 采样盒下界/上界: 世界边界内缩 1 m(12x12 -> [1,11]), 朝向 ±π 全范围
                        [self.x_range[0] + 1, self.y_range[0] + 1, -3.141592653589793],  # 下界 [x_min+1, y_min+1, -π](米/弧度)
                        [self.x_range[1] - 1, self.y_range[1] - 1, 3.141592653589793],  # 上界 [x_max-1, y_max-1, +π](米/弧度)
                    ],  # range_limits = [下界; 上界] 两行采样盒
                )  # set_random_goal(...) 结束: 该机已换新随机目标

        return (  # ---- 10 元组返回(与 docstring 一一对应; 各列表第 k 项属于机器人 k) ----
            poses,  # N x [x, y, θ] 位姿(米/弧度)
            distances,  # N 个到目标距离(米)
            coss,  # N 个 cos
            sins,  # N 个 sin
            collisions,  # N 个碰撞标志
            goals,  # N 个到达标志
            action,  # 输入动作原样回显(供 replay buffer)
            rewards,  # N 个奖励
            positions,  # N x [x, y](米)
            goal_positions,  # N 个目标 [x, y](米)
        )  # step 的 10 元组返回结束

    # ---- reset: 开新局——随机摆 N 台机器人(带最小间距拒绝采样) ----
    # 输入: robot_state(注意: 多机分支会被循环内随机值覆盖, 见坑注)/
    #       robot_goal(注意: 固定目标只写到 0 号机器人)/随机障碍开关与 id
    # 输出: 与 step 同构的 10 元组(碰撞/到达强制全 False)
    def reset(
        self,  # reset 主体(多行签名)
        robot_state=None,  # 初始位姿(实际上不生效, 见下方坑注)
        robot_goal=None,  # 固定目标(None 则每台随机采样)
        random_obstacles=False,  # 多机默认 False(单机版默认 True): 本世界无障碍段
        random_obstacle_ids=None,  # 要重摆的障碍 id; None 则取机器人之后的 7 个 id
    ):  # 多行签名结束
        """
        Reset the simulation environment and optionally set robot and obstacle positions.

        Args:
            robot_state (list or None, optional): Initial robot state(s) as [[x], [y], [theta]].
                If None, random states are assigned ensuring minimum spacing between robots.
            robot_goal (list or None, optional): Fixed goal position(s) for robots. If None, random
                goals are generated within the environment boundaries.
            random_obstacles (bool, optional): If True, reposition obstacles randomly within bounds.
            random_obstacle_ids (list or None, optional): IDs of obstacles to randomize. Defaults to
                seven obstacles starting from index equal to the number of robots.

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
        # (docstring 原样保留; 以下为 reset 主体)
        if robot_state is None:  # 没传初始位姿 -> 先给个默认值
            robot_state = [[random.uniform(3, 9)], [random.uniform(3, 9)], [0]]  # x,y~U(3,9)(米, 12x12 世界中部), θ=0; 3x1 列向量。坑注(代码实证): 此值随后被下面循环内的随机采样无条件覆盖, 传参实际上不生效

        init_states = []  # 已接受初始化的机器人位置(米)——用于最小间距检查
        for robot in self.env.robot_list:  # 逐台采样初始位姿(拒绝采样: 保证两两间距)
            conflict = True  # 先假设有冲突, 进入 while 重采样
            while conflict:  # 直到与所有已放置的机器人都不冲突为止
                conflict = False  # 乐观复位, 下面检查再置位
                robot_state = [  # 重新随机采样本台位姿(覆盖默认值/入参)
                    [random.uniform(3, 9)],  # x ~ U(3,9)(米)
                    [random.uniform(3, 9)],  # y ~ U(3,9)(米)
                    [random.uniform(-3.14, 3.14)],  # 朝向 θ ~ U(-π, π)(弧度)——开局朝向随机
                ]  # robot_state = 3x1 列向量 [[x],[y],[θ]](米/弧度)
                pos = [robot_state[0][0], robot_state[1][0]]  # 本台候选 [x, y](米)
                for loc in init_states:  # 与每台已放置的机器人比较
                    vector = [  # 候选位置到已放置位置的位移向量(米)
                        pos[0] - loc[0],  # Δx = 候选点 - 已放置点 的 x 分量(米)
                        pos[1] - loc[1],  # Δy = 候选点 - 已放置点 的 y 分量(米)
                    ]  # vector = [Δx, Δy] 位移向量(米)
                    if np.linalg.norm(vector) < 0.6:  # 两台间距 < 0.6 m(机器人直径 0.4 m 再留缓冲) -> 冲突
                        conflict = True  # 置冲突, 重采样
            init_states.append(pos)  # 通过检查, 登记(米)

            robot.set_state(  # 把采样位姿写入机器人
                state=np.array(robot_state),  # 转 3x1 numpy 数组(IRSim 格式)
                init=True,  # 按初始状态设置(同步几何原点)
            )  # set_state(...) 结束: 本机初始位姿生效

        if random_obstacles:  # 可选: 随机重摆障碍(多机世界 YAML 无障碍段, 默认 False 不触发)
            if random_obstacle_ids is None:  # 未指定 id -> 默认
                random_obstacle_ids = [i + self.num_robots for i in range(7)]  # id = N..N+6: irsim 里机器人先占 0..N-1, 障碍 id 接在其后
            self.env.random_obstacle_position(  # IRSim 批量随机摆障碍
                range_low=[self.x_range[0], self.y_range[0], -3.14],  # 采样下界(米/弧度)
                range_high=[self.x_range[1], self.y_range[1], 3.14],  # 采样上界(米/弧度)
                ids=random_obstacle_ids,  # 只重摆这些 id
                non_overlapping=True,  # 互相不重叠(采样拒绝)
            )  # random_obstacle_position(...) 结束

        for robot in self.env.robot_list:  # 逐台分配目标
            if robot_goal is None:  # 没给固定目标 -> 每台随机采样(避开障碍)
                robot.set_random_goal(  # IRSim 随机目标
                    obstacle_list=self.env.obstacle_list,  # 障碍列表(剔除重叠采样)
                    init=True,  # 按初始状态登记
                    range_limits=[  # 采样盒: 世界内缩 1 m([1,11] m), 朝向 ±π
                        [self.x_range[0] + 1, self.y_range[0] + 1, -3.141592653589793],  # 下界(米/弧度)
                        [self.x_range[1] - 1, self.y_range[1] - 1, 3.141592653589793],  # 上界(米/弧度)
                    ],  # range_limits = [下界; 上界] 采样盒(世界内缩 1 m)
                )  # set_random_goal(...) 结束: 本机随机目标已生效
            else:  # 给了固定目标 -> 写入。坑注(代码实证): 这里是 self.env.robot(0 号)而非遍历中的 robot, 即固定目标只对 0 号机器人生效
                self.env.robot.set_goal(np.array(robot_goal), init=True)  # 0 号机器人设置固定目标
        self.env.reset()  # 重置仿真器内部(步计数/缓存)
        self.robot_goal = self.env.robot.goal  # 回读 0 号最终目标缓存

        action = [[0.0, 0.0] for _ in range(self.num_robots)]  # 初始动作: 每台 [v=0 m/s, ω=0 rad/s]
        con = torch.tensor(  # 构造全零 connection 张量占位(形状 (N, N-1), 与真实注意力 logits 同构)
            [[0.0 for _ in range(self.num_robots - 1)] for _ in range(self.num_robots)]  # N 行 x (N-1) 列的零矩阵(无自连接列)
        )  # con = 全零 connection 张量, 形状 (N, N-1)
        poses, distance, cos, sin, _, _, action, reward, positions, goal_positions = (  # 零动作 step 一次取初始观测(忽略返回的碰撞/到达位)
            self.step(action, con)  # 传零动作与零连接(注意未传 combined_weights -> 见 step 里的 NameError 坑注)
        )  # 零动作 step(...) 结束, 元组解包到左侧 10 个变量
        return (  # 初始 10 元组: 碰撞/到达强制全 False(开局不可能终止)
            poses,  # N x [x, y, θ](米/弧度)
            distance,  # N 个到目标距离(米)
            cos,  # N 个 cos
            sin,  # N 个 sin
            [False] * self.num_robots,  # 碰撞标志全 False
            [False] * self.num_robots,  # 到达标志全 False
            action,  # 零动作回显
            reward,  # 初始奖励(常态项)
            positions,  # N x [x, y](米)
            goal_positions,  # N 个目标(米)
        )  # reset 的 10 元组返回结束

    # ---- get_reward: 多机器人奖励函数(静态方法; 两个相位=课程两阶段) ----
    # 输入: goal=到达/collision=碰撞/action=[v,ω]/closest_robots=到其余
    #       机器人距离(米)/distance=到目标距离(米)/phase=1 或 2
    # 输出: 标量奖励 r
    # 两相位设计意图(教学档, 权重全部代码实证):
    #   phase 1(前期): 密集塑造——1.5/d 接近项 + v 前进项引导学会"奔向
    #     目标"; 机间安全距离 1.25 m, 违者二次惩罚;
    #   phase 2(后期): 塑造退场——去掉 1.5/d 与 v, 只留 0.5|ω| 转向
    #     惩罚 + 安全距离扩大到 3 m(惩罚更陡), 到达奖从 100 降到 70,
    #     迫使策略从"贪奖励梯度"过渡到"又快又稳的协同避让"。
    @staticmethod  # 静态方法: 不依赖 self, 便于独立测试与两相位复用
    def get_reward(goal, collision, action, closest_robots, distance, phase=1):  # 签名: 输入输出见上方块注释
        """
        Compute the reward for a single robot based on goal progress, collisions,
        control effort, and proximity to other robots.

        Args:
            goal (bool): Whether the robot reached its goal.
            collision (bool): Whether the robot collided with an obstacle or another robot.
            action (list): [linear_velocity, angular_velocity] applied by the robot.
            closest_robots (list): Distances to other robots.
            distance (float): Current distance to the goal.
            phase (int, optional): Reward configuration (1 or 2). Default is 1.

        Returns:
            float: Computed scalar reward.

        Raises:
            ValueError: If an unknown reward phase is specified.
        """

        # (docstring 原样保留; 以下为奖励计算主体)
        match phase:  # Python 3.10 结构匹配: 按 phase 选择奖励变体
            case 1:  # ---- 相位 1: 前期(密集塑造) ----
                if goal:  # 到达: 大奖
                    return 100.0  # +100 一次性大额奖励(稀疏主目标)
                elif collision:  # 碰撞: 与速度挂钩的大罚
                    return -100.0 * 3 * action[0]  # -300·v(m/s): 撞得越快罚越重(速度责任); v∈[0,0.5] -> 罚域 [-150, 0]
                else:  # 常态塑造项
                    r_dist = 1.5 / distance  # 接近奖励: 1.5(m)/d(m) -> 无量纲; 距离越近值越大(d=1.5 m 时=1), 逼近期标时急剧增大
                    cl_pen = 0  # 机间避让惩罚累加器
                    for rob in closest_robots:  # 遍历到其余每台机器人的距离(米)
                        add = (1.25 - rob) ** 2 if rob < 1.25 else 0  # 距离 < 1.25 m 时罚 (1.25-d)²(m²), 否则 0——1.25 m 安全圈外免费
                        cl_pen += add  # 累加(多台逼近则惩罚叠加)
                    # 教学档: ① v 前进奖励(≤0.5/步) ② -0.5|ω| 转向惩罚(抑制画龙)
                    # ③ -cl_pen 机间二次惩罚 ④ +1.5/d 接近奖励

                    return action[0] - 0.5 * abs(action[1]) - cl_pen + r_dist  # 常态奖励合计: 前进奖 v - 转向罚 0.5|ω| - 机间罚 cl_pen + 接近奖 1.5/d

            case 2:  # ---- 相位 2: 后期(塑造退场, 更保守的安全距离) ----
                if goal:  # 到达: 奖励降额
                    return 70.0  # +70(比相位 1 的 100 低: 后期到达不是唯一重点)
                elif collision:  # 碰撞: 与相位 1 相同
                    return -100.0 * 3 * action[0]  # -300·v: 同样按速度加重
                else:  # 常态: 只剩转向惩罚 + 机间惩罚(无接近项/前进项)
                    cl_pen = 0  # 机间避让惩罚累加器
                    for rob in closest_robots:  # 遍历机间距离(米)
                        add = (3 - rob) ** 2 if rob < 3 else 0  # 安全圈扩大到 3 m, 罚 (3-d)²(m²)——比相位 1 更早且更陡地惩罚接近
                        cl_pen += add  # 累加(多台逼近则惩罚叠加)

                    return -0.5 * abs(action[1]) - cl_pen  # r = -0.5|ω| - cl_pen: 引导信号退场, 行为定型靠到达/碰撞大额事件

            case _:  # 未知相位: 直接报错(防御式编程, 防配置笔误静默训练)
                raise ValueError("Unknown reward phase")  # 抛出 ValueError
