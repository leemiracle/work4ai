# ============================================================================
# 模块: sim.py —— 单机器人 2D 导航仿真环境(继承 SIM_ENV 抽象基类)
# 职责: 封装 IRSim 2D 仿真器的单机器人场景, 提供 gym 风格的
#       step / reset 接口与一个"目标接近 + 避障"型奖励函数。
# 被谁调用: rl_train.py / rl_test.py / rnn_train.py 等训练测试脚本
#       通过 SIM('robot_world.yaml') 实例化后调用。
# 世界配置实证(robot_nav/worlds/robot_world.yaml):
#   * 世界 10x10 m, offset 默认 [0,0] -> x/y 范围都是 [0,10] m;
#   * step_time = sample_time = 0.3 s(每个 step 推进 0.3 秒仿真时间);
#   * 机器人: 差速驱动(diff), 圆形半径 0.2 m, 线速度 v∈[0,1.0] m/s,
#     角速度 ω∈[-1.0,1.0] rad/s; 到达判定 goal_threshold=0.3 m;
#   * 传感器 lidar2d: 180 束, 总视场角 angle_range=3.14 rad 即前向
#     ±90°(irsim 源码实证: angle_min=-ar/2, angle_max=+ar/2), 束间角
#     分辨率 = 3.14/180 ≈ 0.0174 rad ≈ 1°/束, 量程 [0,7] m, 测距噪声
#     高斯 std=0.08 m, 角度噪声 std=0.1 rad;
#   * 障碍: 4 个动态障碍(行为模式 rvo + wander=True 随机游走,
#     最大速度 0.2 m/s, 比机器人慢 -> 可绕行) + 3 个静态障碍 +
#     1 圈边界墙(linestring); collision_mode='reactive'。
# RVO 是什么(教学档): Reciprocal Velocity Obstacle(互惠速度障碍)——
#   一种去中心化避碰模型: 每个移动体假设对方也会分担一半避让
#   责任, 在"速度空间"里避开互惠碰撞锥来选速度; 本仓用它模拟
#   会互相礼让的行人式动态障碍, 让导航策略必须学会动态避让。
# ============================================================================
import irsim  # IRSim 2D 机器人仿真库: 提供世界解析/运动学/激光渲染
import numpy as np  # 数值计算: 向量范数(距离)、数组构造
import random  # 随机采样: 初始位姿/障碍/目标的位置分布

from robot_nav.SIM_ENV.sim_env import SIM_ENV  # 抽象基类: 强制实现 step/reset/get_reward 契约


# ---- 单机器人环境类: 本文件主体, 训练脚本的直接交互对象 ----
# 教学档(与 gym 的关系): 它没继承 gym.Env, 返回值是裸元组而非
#   (obs, reward, terminated, truncated, info) 五元组——各模型文件里的
#   prepare_state() 负责把这些裸量拼装、归一化成网络输入。
class SIM(SIM_ENV):
    """
    A simulation environment interface for robot navigation using IRSim.

    This class wraps around the IRSim environment and provides methods for stepping,
    resetting, and interacting with a mobile robot, including reward computation.

    Attributes:
        env (object): The simulation environment instance from IRSim.
        robot_goal (np.ndarray): The goal position of the robot.
    """

    # (docstring 按规范原样保留, 不添加注释)
    # ---- 构造函数: 加载 YAML 世界并缓存初始目标 ----
    # 输入: world_file=世界配置文件名; disable_plotting=是否关闭画图
    # 被谁调用: 训练/测试脚本创建环境时(rl_train.py 等)
    def __init__(self, world_file="robot_world.yaml", disable_plotting=False):
        """
        Initialize the simulation environment.

        Args:
            world_file (str): Path to the world configuration YAML file.
            disable_plotting (bool): If True, disables rendering and plotting.
        """
        display = False if disable_plotting else True  # display 与 disable_plotting 取反: 无头训练时不开窗口
        self.env = irsim.make(  # irsim.make: 解析 YAML -> 生成仿真环境实例(世界/机器人/障碍/传感器)
            world_file, disable_all_plot=disable_plotting, display=display  # 传入画图总开关与显示开关
        )  # irsim.make(...) 调用结束, 返回 EnvBase 实例挂到 self.env
        robot_info = self.env.get_robot_info(0)  # 取 0 号(唯一)机器人的信息对象(位姿/目标/半径等)
        self.robot_goal = robot_info.goal  # 缓存其目标点 np 列向量 [x_goal, y_goal, theta_goal](米/弧度)

    # ---- step: 环境推进一拍(0.3 s) ----
    # 输入: lin_velocity=线速度(m/s), ang_velocity=角速度(rad/s)
    #       —— 这就是连续动作空间的二维: 网络输出经缩放后填进来
    # 输出: 8 元组(激光/距离/方位/碰撞/到达/动作回显/奖励), 见各 return 行
    # 被谁调用: 训练主循环每步一次; reset 内部也会用零动作调它取初始观测
    def step(self, lin_velocity=0.0, ang_velocity=0.1):
        """
        Perform one step in the simulation using the given control commands.

        Args:
            lin_velocity (float): Linear velocity to apply to the robot.
            ang_velocity (float): Angular velocity to apply to the robot.

        Returns:
            (tuple): Contains the latest LIDAR scan, distance to goal, cosine and sine of angle to goal,
                   collision flag, goal reached flag, applied action, and computed reward.
        """
        self.env.step(action_id=0, action=np.array([[lin_velocity], [ang_velocity]]))  # 驱动 0 号机器人: irsim 要求动作是 2x1 列向量 [[v],[ω]]; 此调用内部完成碰撞检测/传感器更新, 仿真时间 +0.3 s
        self.env.render()  # 渲染一帧(disable_plotting=True 时为空操作); 注意 render 不推进物理, 只刷新显示

        scan = self.env.get_lidar_scan()  # 取激光雷达字典(ROS LaserScan 风格: angle_min/angle_max/range_min/range_max/ranges...)
        latest_scan = scan["ranges"]  # 只取 180 束的距离数组(米): 按角度从 -90° 到 +90° 排列; 无回波的束读数为 inf(模型侧会截断成 7.0)

        robot_state = self.env.get_robot_state()  # 机器人状态 [x, y, theta](米, 米, 弧度)
        goal_vector = [  # 目标方向向量 = 目标点 - 当前位置(米); 只取 x/y 分量, 不含朝向
            self.robot_goal[0].item() - robot_state[0].item(),  # Δx = x_goal - x (米), .item() 把张量/数组标量转 float
            self.robot_goal[1].item() - robot_state[1].item(),  # Δy = y_goal - y (米)
        ]  # goal_vector = [Δx, Δy], 指向目标的 2D 平移向量(米)
        distance = np.linalg.norm(goal_vector)  # 到目标的欧氏距离(米): reward 与观测都会用到
        goal = self.env.robot.arrive  # 到达标志: 距目标 < goal_threshold(0.3 m) 时 IRSim 置 True
        pose_vector = [np.cos(robot_state[2]).item(), np.sin(robot_state[2]).item()]  # 机器人朝向单位向量 (cosθ, sinθ): 由朝向角 theta(rad) 展开成直角坐标
        cos, sin = self.cossin(pose_vector, goal_vector)  # 父类工具: 朝向与目标方向的夹角 φ 的 (cos φ, sin φ)(无量纲)——观测的"该往哪转"信号
        collision = self.env.robot.collision  # 碰撞标志: 本步是否与障碍/墙/其他物体发生碰撞(reactive 模式下碰撞即停)
        action = [lin_velocity, ang_velocity]  # 把本步动作原样打包回显(供 replay buffer 存 (s,a,r,s'))
        reward = self.get_reward(goal, collision, action, latest_scan)  # 用激光最小值版奖励函数计算本步标量奖励 r

        return latest_scan, distance, cos, sin, collision, goal, action, reward  # 8 元组: 观测原料(laser/distance/cos/sin) + 终止语义(collision/goal) + 动作回显 + 奖励
        # 教学档(观测向量最终长什么样): 环境侧输出的是原始米制量; 真正喂给
        # 网络的归一化状态由模型侧 prepare_state 完成(DDPG.py:402-424 实证):
        # inf 激光 -> 7.0, 分箱取最小后 /7; distance/10(世界对角约 14 m, /10 后约 [0,1.4]);
        # 再拼上 cos/sin 与上一步动作 [v*2, (ω+1)/2] 映射到 [0,1]。

    # ---- reset: 开新局(episode 第 0 步) ----
    # 输入: robot_state=[[x],[y],[θ]] 列向量形式; robot_goal=固定目标;
    #       random_obstacles=是否随机重摆障碍; random_obstacle_ids=要重摆的障碍 id
    # 输出: 与 step 同构的 8 元组(初始观测, 碰撞/到达强制 False)
    # 被谁调用: 训练循环每个 episode 开始时
    def reset(
        self,  # reset 主体(多行签名: 参数多, 逐行注释)
        robot_state=None,  # 初始位姿; None 则随机采样
        robot_goal=None,  # 目标点; None 则随机采样(避开障碍)
        random_obstacles=True,  # 默认 True: 每局随机重摆障碍 -> 增强泛化, 防"背地图"
        random_obstacle_ids=None,  # 要随机化的障碍 id 列表; None 则默认 id 1..7
    ):  # 多行签名结束
        """
        Reset the simulation environment, optionally setting robot and obstacle states.

        Args:
            robot_state (list or None): Initial state of the robot as a list of [x, y, theta, speed].
            robot_goal (list or None): Goal state for the robot.
            random_obstacles (bool): Whether to randomly reposition obstacles.
            random_obstacle_ids (list or None): Specific obstacle IDs to randomize.

        Returns:
            (tuple): Initial observation after reset, including LIDAR scan, distance, cos/sin,
                   and reward-related flags and values.
        """
        if robot_state is None:  # 调用方没给初始位姿 -> 随机生成
            robot_state = [[random.uniform(1, 9)], [random.uniform(1, 9)], [0]]  # x~U(1,9), y~U(1,9)(米, 离 10x10 世界边界留 1 m 缓冲), θ=0(朝 x 正向); 结构是 3x1 列向量 [[x],[y],[θ]]

        self.env.robot.set_state(  # 把初始位姿写入机器人
            state=np.array(robot_state),  # 转成 3x1 numpy 数组(IRSim 状态格式)
            init=True,  # init=True: 按"初始状态"设置(同步几何原点, 供轨迹绘制/复位)
        )  # set_state(...) 结束: 初始位姿已生效

        if random_obstacles:  # 每局随机重摆(部分)障碍
            if random_obstacle_ids is None:  # 没指定 id 列表 -> 用默认
                random_obstacle_ids = [i + 1 for i in range(7)]  # 默认 id 1..7 共 7 个障碍(跳过 id 0; 此世界障碍与机器人共用 id 空间)
            self.env.random_obstacle_position(  # IRSim 批量随机摆障碍
                range_low=[0, 0, -3.14],  # 采样下界: x,y∈[0,10] m, 朝向 θ∈[-3.14, 3.14] rad
                range_high=[10, 10, 3.14],  # 采样上界(米/弧度)
                ids=random_obstacle_ids,  # 只重摆这些 id 的障碍
                non_overlapping=True,  # 保证互相不重叠(采样拒绝)
            )  # random_obstacle_position(...) 结束

        if robot_goal is None:  # 没指定目标 -> 随机采一个不与障碍重叠的目标
            self.env.robot.set_random_goal(  # IRSim 随机目标采样(内部会避开障碍列表)
                obstacle_list=self.env.obstacle_list,  # 传入全部障碍, 采样时做碰撞剔除
                init=True,  # 同上: 按初始状态登记
                range_limits=[[1, 1, -3.141592653589793], [9, 9, 3.141592653589793]],  # 目标采样盒: x,y∈[1,9] m(离墙留 1 m 缓冲), θ∈[-π,π] rad
            )  # set_random_goal(...) 结束: 目标已采样并生效
        else:  # 指定了固定目标(评测复现用)
            self.env.robot.set_goal(np.array(robot_goal), init=True)  # 直接写入给定目标点
        self.env.reset()  # 重置仿真器内部状态(步计数/缓存/传感器)
        self.robot_goal = self.env.robot.goal  # 回读最终生效的目标并缓存(step 里要用)

        action = [0.0, 0.0]  # 初始动作为零(v=0 m/s, ω=0 rad/s)
        latest_scan, distance, cos, sin, _, _, action, reward = self.step(  # 用零动作 step 一次, 取初始观测(忽略其中的碰撞/到达位, 用下面的 False)
            lin_velocity=action[0], ang_velocity=action[1]  # 传 0.0/0.0
        )  # 零动作 step 结束
        return latest_scan, distance, cos, sin, False, False, action, reward  # 初始观测: 碰撞/到达强制 False(开局不可能终止), 归一化仍交给模型侧

    # ---- get_reward: 单机器人奖励函数(静态方法, 纯函数) ----
    # 输入: goal=是否到达; collision=是否碰撞; action=[v,ω];
    #       laser_scan=180 束激光距离(米)
    # 输出: 标量奖励 r(RL 的学习信号)
    # 设计总览(教学档, 全部以代码实证):
    #   到达 +100 | 碰撞 -100 | 常态 = v - |ω|/2 - r3(min_scan)/2
    #   即"接近奖励靠前进速度, 代价是转向与贴障碍", 无显式时间惩罚项
    @staticmethod
    def get_reward(goal, collision, action, laser_scan):  # 签名(静态方法无 self): 见上方块注释的输入输出说明
        """
        Calculate the reward for the current step.

        Args:
            goal (bool): Whether the goal has been reached.
            collision (bool): Whether a collision occurred.
            action (list): The action taken [linear velocity, angular velocity].
            laser_scan (list): The LIDAR scan readings.

        Returns:
            (float): Computed reward for the current state.
        """
        if goal:  # 分项① 到达大奖
            return 100.0  # 一次性 +100(约等于 100 步常态奖励之和的量级) —— 稀疏强信号, 主学习目标
        elif collision:  # 分项② 碰撞大罚(episode 通常随之终止)
            return -100.0  # 与到达对称的 -100: 让"撞"和"到达"是同一量级的一票否决
        else:  # 分项③ 常态塑造项(每步都有, 引导中间行为)
            r3 = lambda x: 1.35 - x if x < 1.35 else 0.0  # 阈值函数: 障碍距离 x(米) < 1.35 m 时返回 (1.35-x), 否则 0 —— 1.35 m 之外完全不罚(安全边际免费), 之内线性加重
            return action[0] - abs(action[1]) / 2 - r3(min(laser_scan)) / 2  # r = v(前进奖励, m/s, ≤1) - 0.5|ω|(转向惩罚, 抑制画龙/省能耗) - 0.5·r3(min 激光)(贴障碍惩罚, 最大 0.675/步) —— min(laser_scan)=180 束里最近障碍距离(米), 无回波 inf 时视实现可能为 inf(模型侧已截断)
