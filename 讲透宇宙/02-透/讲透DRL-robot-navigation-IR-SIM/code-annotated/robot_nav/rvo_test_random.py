# ============================================================================
# rvo_test_random.py —— RVO 经典基线 ×"随机持续巡航"场景的批量评估脚本（逐行中文注释版）
# ============================================================================
# 【与 rvo_test_single.py 的差异（代码实证）】同是 RVO 基线，本脚本换了评估口径：
# ① 场景：multi_robot_world.yaml + reset() 每回合随机重摆机器人（x,y~U(3,9)、
#    两两间距≥0.6）并随机派目标——1000 个随机回合 vs single 版固定圆周×100；
# ② 目标机制：机器人到达目标不出局，step() 里立刻派新随机目标（持续巡航），
#    因此"到达数"是吞吐量指标而非任务成功标志；
# ③ 终止条件：只认 碰撞 / 300 步超时 / 越界（没有"全员到达"出口——巡航无终点）；
# ④ 统计口径：碰撞按"机器人侧标志数"直接求和（不再 /2 折算事件数），且删掉了
#    超时计数与步数统计（running_timesteps 成死代码）——与 single 版数字不可直接混比。
# 【RVO 在哪】同 single 版：控制器由 world YAML 的 robot.behavior 配置激活（irsim
# 内置 lib/algorithm/rvo.py，reciprocal_vel_obs 类）。注意实证：multi_robot_world.yaml
# 里连 behavior 行都没有，复现 RVO 基线需自行添加（circle_world.yaml 中是被注释的现成行）。
# RVO（Reciprocal Velocity Obstacle，互惠速度障碍）＝经典非学习避障：把邻居建模成
# 自己速度空间中的禁区并各让一半责任，作 DRL 方法的对照组。
# ============================================================================
import statistics  # 标准库统计模块：结尾求每回合指标的均值/标准差

from tqdm import tqdm  # 进度条库：1000 个回合的进度可视化

import torch  # PyTorch：本文件实际未使用——RVO 非学习基线（import 骨架复制自 DRL 脚本）
import numpy as np  # NumPy：向量范数（重采样间距检查）与统计数组


import irsim  # IRSim：2D 多机器人仿真器，RVO 行为/运动学/碰撞检测都在其内部
import numpy as np  # 重复导入 np（无害但冗余——上下两个 import 块拼贴的痕迹）
import random  # 随机库：本版真正在用——reset() 的随机初始位姿/随机目标全靠它
import torch  # 重复导入 torch（同样未使用，冗余）

# 导入抽象基类 SIM_ENV：ABC+abstractmethod 规定子类必须实现 step/reset/get_reward，
# 使 RL、MARL、RVO 三类环境共享同一接口——同一评估循环可无差别插拔（对照组实验的接口层保障）
from robot_nav.SIM_ENV.sim_env import SIM_ENV  # 基类只定契约、不含实现


# ----------------------------------------------------------------------------
# 类 RVO_RANDOM_SIM：随机场景（持续巡航）RVO 评估环境
# 职责：包装 IRSim，并把 reset() 改造成"随机重摆机器人+随机派目标"、step() 里
#       给到达者即时换新目标——构造一个永不结束的巡航任务，专测持续避障能力。
# 输入：构造参数同 single 版（world_file / disable_plotting）；reset() 随机化参数见其块注。
# 输出：step() → (碰撞标志, 到达标志, 位置)；reset() → 同构三元组（全 False 起步）。
# 调用关系：main() → step()/reset()；对手＝其余 4 台同规格 RVO 机器人（对称互惠）。
# ----------------------------------------------------------------------------
class RVO_RANDOM_SIM(SIM_ENV):  # 定义随机场景仿真环境类，实现基类三个抽象方法
    """
    Simulation environment for randomized multi-agent robot navigation using IRSim.

    This class extends `SIM_ENV` and provides a wrapper for running a multi-robot
    simulation where robots navigate toward randomly assigned goals. It includes
    environment reset, step execution, and collision/goal state tracking.

    Attributes:
        env (object): IRSim simulation environment instance.
        robot_goal (np.ndarray): Current goal positions for all robots.
        num_robots (int): Number of robots in the environment.
        x_range (tuple): Range of the x-axis for the simulation world.
        y_range (tuple): Range of the y-axis for the simulation world.
    """

    # ---- 构造函数：与 single 版几乎逐行相同（创建 IRSim、缓存规模信息）----
    # 世界 multi_robot_world.yaml：12×12、5 台差速机器人、圆周分布半径 4；
    # 与 single 版的差别只在世界文件与后续 reset()/step() 的随机化逻辑。
    def __init__(self, world_file="multi_robot_world.yaml", disable_plotting=False):
        """
        Initialize the randomized IRSim-based multi-robot environment.

        Args:
            world_file (str, optional): Path to the YAML configuration file defining
                the world layout. Defaults to "multi_robot_world.yaml".
            disable_plotting (bool, optional): If True, disables visual rendering
                and live plotting in IRSim. Defaults to False.
        """
        display = False if disable_plotting else True  # 显示开关与绘图总闸联动（等价于 not disable_plotting）：无头模式不开窗，批量评估提速
        self.env = irsim.make(  # 创建 IRSim 环境实例（类比 gym.make）
            world_file, disable_all_plot=disable_plotting, display=display  # 传入世界 YAML；关闭全部绘图与显示
        )  # 闭合多行调用
        robot_info = self.env.get_robot_info(0)  # 取 0 号（ego）机器人的信息对象
        self.robot_goal = robot_info.goal  # 缓存其目标（本版目标随后会被随机化覆盖）
        self.num_robots = len(self.env.robot_list)  # 机器人总数（=5），决定遍历与统计列表长度
        self.x_range = self.env._world.x_range  # 世界水平范围（直接摸下划线私有属性；随机目标的范围基准）
        self.y_range = self.env._world.y_range  # 世界垂直范围

    # ---- step()：推进一步 + 本版差异点——给到达者即时派新随机目标 ----
    # 与 single 版唯一的实质差异是 if goal: 分支调用 set_random_goal：
    # 机器人到达后立刻转向新目标继续巡航（回合不因到达而结束）。
    def step(self):  # 推进一步：IRSim 走一步 + 给到达者即时换新目标
        """
        Perform one simulation step for all robots and update goals dynamically.

        Each robot moves based on IRSim’s physics step, with collisions, goals,
        and positions collected. If a robot reaches its goal, a new random goal
        is automatically assigned.

        Returns:
            tuple:
                collisions (list of bool): Collision flags for each robot.
                goals (list of bool): Goal completion flags for each robot.
                positions (list of [float, float]): Current [x, y] positions for each robot.
        """
        self.env.step()  # 推进 IRSim 一步：RVO 解算速度、移动、碰撞检测都在其内部
        self.env.render()  # 渲染一帧（无头模式下近似空操作）

        collisions = []  # 各机器人本步碰撞标志（irsim collision 属性）
        goals = []  # 各机器人本步到达标志（arrive 属性；到位阈值 goal_threshold=0.3）
        positions = []  # 各机器人 [x, y] 位置
        for i in range(self.num_robots):  # 逐台读取状态
            robot_state = self.env.robot_list[i].state  # 第 i 台的状态列向量 [x, y, θ, ...]
            position = [robot_state[0].item(), robot_state[1].item()]  # 取 x/y 并 .item() 转 Python float
            positions.append(position)  # 记入位置列表

            goal = self.env.robot_list[i].arrive  # 是否到达当前目标
            collision = self.env.robot_list[i].collision  # 本步是否碰撞
            collisions.append(collision)  # 记入碰撞列表
            goals.append(goal)  # 记入到达列表

            if goal:  # 到达者：本回合不出局，改派新目标（持续巡航的核心机制）
                # set_random_goal 语义（irsim 源码实证）：在 range_limits 内重抽目标，
                # free=True 时以 0.2 半径做障碍碰撞检查、至多重试 100 次；
                # init=True 表示按"初始目标"语义写入。目标范围＝世界边界内缩 1 米。
                self.env.robot_list[i].set_random_goal(  # 给第 i 台派新随机目标
                    obstacle_list=self.env.obstacle_list,  # 提供障碍物清单用于避障采样
                    init=True,  # 以初始化语义写入目标
                    range_limits=[  # 目标采样范围（下标 0=下界、1=上界，各含 [x, y, θ]）
                        [self.x_range[0] + 1, self.y_range[0] + 1, -3.141592653589793],  # 下界：边界内缩 1，θ=-π
                        [self.x_range[1] - 1, self.y_range[1] - 1, 3.141592653589793],  # 上界：边界内缩 1，θ=+π
                    ],  # 闭合 range_limits 列表
                )  # 闭合 set_random_goal 多行调用

        return collisions, goals, positions  # 三份逐机器人状态交还评估循环

    # ---- reset()：随机重摆全部机器人 + 随机派目标（本版的灵魂）----
    # 实现要点：①初始位姿用"拒绝采样"——在 3~9 均匀重抽，直到与已放置机器人两两
    #   距离≥0.6（术语：拒绝采样＝不满足条件就丢弃重抽，直到合格为止）；
    # ②random_obstacles 分支（随机化 7 个障碍）在本测试中不触发——main() 调
    #   reset() 时不传该参，且本世界 YAML 根本没定义障碍物，属预留接口；
    # ③robot_goal 为 None 时逐台派随机目标，否则只给第一台设传入目标。
    def reset(  # 多行签名：随机重摆+随机派目标（见上方块注释）
        self,  # 实例引用（Python 实例方法的第一个参数）
        robot_state=None,  # 自定义初始状态；None 进随机分支（但随即被循环内重采样覆盖，属死分支）
        robot_goal=None,  # 自定义目标；None → 每台随机派目标
        random_obstacles=False,  # 是否随机化障碍物位置（本测试恒为 False，分支不触发）
        random_obstacle_ids=None,  # 要随机化的障碍编号；None 时默认取机器人 id 之后的 7 个
    ):  # 闭合多行签名
        """
        Reset the simulation environment, optionally randomizing robots and obstacles.

        Randomly reinitializes robot positions while avoiding collisions and can
        optionally re-randomize obstacle positions.

        Args:
            robot_state (list or None, optional): Custom initial state for robots as
                [x, y, theta, speed]. If None, random states are assigned.
            robot_goal (list or None, optional): Custom goal positions. If None, random
                goals are assigned within bounds.
            random_obstacles (bool, optional): Whether to randomize obstacle locations.
                Defaults to False.
            random_obstacle_ids (list or None, optional): List of obstacle IDs to randomize.
                If None, defaults to the first 7 obstacles after robots.

        Returns:
            tuple:
                collisions (list of bool): All False immediately after reset.
                goals (list of bool): All False immediately after reset.
                positions (list of [float, float]): Initial [x, y] positions for all robots.
        """
        if robot_state is None:  # 未显式传入初始状态时
            robot_state = [[random.uniform(3, 9)], [random.uniform(3, 9)], [0]]  # 给个默认随机位姿（(3,1) 嵌套列表）——实证：随即被下方循环重采样覆盖，此赋值实为死代码

        init_states = []  # 已放置机器人的 [x, y]，用于新采样点的最小间距检查
        for robot in self.env.robot_list:  # 逐台重摆
            conflict = True  # 冲突标志：先置 True 以进入重采样循环
            while conflict:  # 拒绝采样：抽到与已有机器人太近就重抽
                conflict = False  # 先假定本次采样合法
                robot_state = [  # 重抽初始位姿 [[x],[y],[θ]]：x,y~U(3,9)，θ~U(-π,π)（无条件覆盖传入的 robot_state）
                    [random.uniform(3, 9)],  # x 坐标（列向量形式）
                    [random.uniform(3, 9)],  # y 坐标
                    [random.uniform(-3.14, 3.14)],  # 朝向角全域随机
                ]  # 闭合重抽位姿列表
                pos = [robot_state[0][0], robot_state[1][0]]  # 展开成平面坐标 [x, y] 便于比较
                for loc in init_states:  # 与所有已放置机器人逐一比对
                    vector = [  # 当前采样点减已放置点的差向量
                        pos[0] - loc[0],  # x 方向差
                        pos[1] - loc[1],  # y 方向差
                    ]  # 闭合差向量列表
                    if np.linalg.norm(vector) < 0.6:  # 两点距离 <0.6（≈两机半径 0.2×2 + 0.2 安全余量）
                        conflict = True  # 太近 → 判冲突，触发外层 while 重抽
            init_states.append(pos)  # 采样合格：登记该机位置

            robot.set_state(  # 把合格位姿写入该机器人
                state=np.array(robot_state),  # 嵌套列表 → (3,1) numpy 状态向量
                init=True,  # 以初始化语义写入（同步内部期望状态/目标队列）
            )  # 闭合 set_state 多行调用

        if random_obstacles:  # 障碍随机化分支（本测试 main() 不传参，恒不触发）
            if random_obstacle_ids is None:  # 未指定障碍编号
                random_obstacle_ids = [i + self.num_robots for i in range(7)]  # 默认取机器人 id 之后的前 7 个（需世界先定义这些障碍才有效）
            self.env.random_obstacle_position(  # 随机重摆指定障碍
                range_low=[self.x_range[0], self.y_range[0], -3.14],  # 采样下界：全世界范围，θ=-π
                range_high=[self.x_range[1], self.y_range[1], 3.14],  # 采样上界：θ=+π
                ids=random_obstacle_ids,  # 目标障碍 id 列表
                non_overlapping=True,  # 要求障碍彼此不重叠
            )  # 闭合多行调用

        for robot in self.env.robot_list:  # 第二遍循环：统一派目标
            if robot_goal is None:  # 未显式给目标 → 逐台随机派
                robot.set_random_goal(  # 同 step() 换目标逻辑（范围＝边界内缩 1）
                    obstacle_list=self.env.obstacle_list,  # 障碍清单（避障采样）
                    init=True,  # 初始化语义
                    range_limits=[  # 目标采样范围（下界/上界）
                        [self.x_range[0] + 1, self.y_range[0] + 1, -3.141592653589793],  # 下界：内缩 1，θ=-π
                        [self.x_range[1] - 1, self.y_range[1] - 1, 3.141592653589793],  # 上界：内缩 1，θ=+π
                    ],  # 闭合 range_limits 列表
                )  # 闭合多行调用
            else:  # 显式给了目标
                self.env.robot.set_goal(np.array(robot_goal), init=True)  # 实证：只给 env.robot（第一台）设目标，并非逐台设置
        self.env.reset()  # IRSim 底层复位：清空轨迹/标志，按刚写入的随机状态与目标重建初始局面
        self.robot_goal = self.env.robot.goal  # 刷新 ego 机器人目标缓存

        _, _, positions = self.step()  # 立即走一步同步状态并取初始位置（副作用：若有机器人恰好瞬时就到达，会先被换一次目标）
        return [False] * self.num_robots, [False] * self.num_robots, positions  # 刚重置：碰撞/到达全 False，位置照实返回

    # ---- get_reward()：基类抽象方法的空占位 ----
    # RVO 非学习、不用奖励；docstring 提到的 MARL 奖励留给学习版环境实现。
    def get_reward(self):  # 奖励占位（RVO 非学习、不消费奖励）
        """
        Placeholder for computing reward functions for the simulation.

        Intended for integration with learning-based algorithms (e.g. MARL),
        calculating per-agent or global rewards based on goal progress,
        collisions, or path efficiency.

        Returns:
            None
        """
        pass  # 空实现：对照组不需要奖励信号


# ----------------------------------------------------------------------------
# 函数 outside_of_bounds(poses)：与 single 版逐字符相同的越界检测
# 输入：各机器人位置列表；输出：任一机体超出中心 (6,6)±10.5 的宽松边界即 True。
# 调用关系：main() 每步调用一次，作为回合终止条件之一。
# 教学点：世界实际 12×12，判界却按 21×21——兜底"跑飞检测"而非严格出界判定。
# ----------------------------------------------------------------------------
def outside_of_bounds(poses):  # 遍历位置做中心化偏移检查
    """
    Determine whether any robot is outside the simulation’s defined world boundary.

    The environment is assumed to be centered at (6, 6) with a 21×21 area.

    Args:
        poses (list of [float, float, float]): Robot poses in [x, y, theta] format.

    Returns:
        bool: True if any robot is outside the world boundary; False otherwise.
    """
    outside = False  # 越界标志，默认未越界
    for pose in poses:  # 遍历每台机器人的位置
        norm_x = pose[0] - 6  # 相对世界中心的 x 偏移（中心取 6）
        norm_y = pose[1] - 6  # 相对世界中心的 y 偏移
        if abs(norm_x) > 10.5 or abs(norm_y) > 10.5:  # 任一轴偏离中心超过 10.5（=21 的一半）即视为跑飞
            outside = True  # 标记越界
            break  # 已判越界，无需再查其余机器人
    return outside  # 返回是否有机器人越界


# ----------------------------------------------------------------------------
# 函数 main()：随机巡航场景的主评估循环（1000 回合）
# 职责：每回合从随机布局起步持续巡航，直到首次碰撞 / 300 步超时 / 越界；
#       记录每回合"累计到达目标数"（吞吐量）与碰撞数，结束时打印均值±标准差。
# 与 single 版口径差异（实证）：无"全员到达"出口、碰撞不除 2、无超时/步数统计
# （running_timesteps 累计后从未被消费——死代码）、回合数 1000 vs 100。
# ----------------------------------------------------------------------------
def main(args=None):  # 评估入口，args 仅占位未用
    """
    Run multiple randomized test scenarios in the RVO_RANDOM_SIM environment.

    Executes a series of randomized navigation tests, stepping through the environment
    while tracking the number of goals reached, collisions, and time steps per episode.
    Prints out aggregated performance metrics across all episodes.

    Args:
        args (Namespace or None, optional): Optional runtime arguments (unused).

    Prints:
        Summary statistics including:
            - Average collisions per episode (and standard deviation)
            - Average goals per episode (and standard deviation)
    """
    episode = 0  # 已完成回合计数（外层 while 控制器）
    max_steps = 300  # maximum number of steps in single episode  # 中文：单回合步数上限（0.3s/步 → 一回合最长 90s 仿真时间）
    steps = 0  # starting step number  # 中文：当前回合步数计数器
    test_scenarios = 1000  # 随机回合总数（比 single 版多一个量级——随机场景需更多样本才有稳定的均值）

    # ---- Instantiate simulation environment and model ---- 中文：实例化随机评估环境（"model"沿袭 DRL 版命名——RVO 无模型）
    # 世界用 multi_robot_world.yaml；RVO 行为需在 YAML 中补 behavior 行（见文件头注释）
    sim = RVO_RANDOM_SIM(  # 创建随机场景评估环境实例
        world_file="worlds/multi_robot_world.yaml", disable_plotting=True  # 指定多机器人随机世界；无头模式
    )  # instantiate environment  # 中文：环境就绪（原文注释原样保留）

    running_goals = 0  # 本回合累计到达次数（巡航吞吐量，可达数十次）
    running_collisions = 0  # 本回合累计碰撞（"机器人侧标志数"口径，无 /2 折算）
    running_timesteps = 0  # 本回合步数计数——实证：累计后从未被读取或清零，死代码（single 版才有步数统计）

    goals_per_ep = []  # 每回合累计到达数样本表
    col_per_ep = []  # 每回合碰撞数样本表
    pbar = tqdm(total=test_scenarios)  # 建进度条，总量=1000 回合
    # ---- Main training loop ---- 中文：主评估循环（"training"系沿袭 DRL 版的命名——本脚本只测不训）
    while episode < test_scenarios:  # 跑满 1000 回合为止

        collision, goal, poses = sim.step()  # get data from the environment  # 中文：取本步碰撞/到达/位置（到达者已在 step 内换好新目标）
        running_goals += sum(goal)  # 本步到达台数累加（吞吐量口径）
        running_collisions += sum(collision)  # 碰撞标志数直接累加（与 single 版不同：不除 2 折算成事件数）

        running_timesteps += 1  # 步数 +1（该累计值无人消费，见上）
        outside = outside_of_bounds(poses)  # 宽松越界检测

        if (  # 三个终止条件任一命中即收束回合（没有"全员到达"出口）
            sum(collision) > 0.5 or steps == max_steps or outside  # ①碰撞（sum>0.5 即至少一台置位） ②300 步超时 ③越界跑飞
        ):  # reset environment of terminal state reached, or max_steps were taken  # 中文：终局或超时→重置并记账
            sim.reset()  # 随机重摆全部机器人并随机派目标（下一回合是全新随机场景）
            goals_per_ep.append(running_goals)  # 本回合累计到达数入样本表
            running_goals = 0  # 清零，供下一回合
            col_per_ep.append(running_collisions)  # 本回合碰撞数入样本表
            running_collisions = 0  # 清零

            steps = 0  # 步数计数器复位
            episode += 1  # 回合计数 +1
            pbar.update(1)  # 进度条前进一格
        else:  # 未触发终止条件
            steps += 1  # 继续下一巡航步

    goals_per_ep = np.array(goals_per_ep, dtype=np.float32)  # 到达样本 → float32 数组
    col_per_ep = np.array(col_per_ep, dtype=np.float32)  # 碰撞样本 → float32 数组
    avg_ep_col = statistics.mean(col_per_ep)  # 每回合平均碰撞标志数（越低越好；注意口径≠single 版）
    avg_ep_col_std = statistics.stdev(col_per_ep)  # 其标准差（回合间波动）
    avg_ep_goals = statistics.mean(goals_per_ep)  # 每回合平均到达数——本版核心指标：首次碰撞/超时前平均完成多少次导航（吞吐量）
    avg_ep_goals_std = statistics.stdev(goals_per_ep)  # 其标准差

    print(f"avg_ep_col: {avg_ep_col}")  # 打印平均每回合碰撞数
    print(f"avg_ep_col_std: {avg_ep_col_std}")  # 打印其标准差
    print(f"avg_ep_goals: {avg_ep_goals}")  # 打印平均每回合到达数（与 DRL/MARL 版同口径对比的核心数字）
    print(f"avg_ep_goals_std: {avg_ep_goals_std}")  # 打印其标准差
    print("..............................................")  # 分隔线（便于与其它测试脚本输出并排汇总）


# 命令行入口：直接运行本文件时才启动 1000 回合评估，被 import 时不触发
if __name__ == "__main__":  # 模块作为主脚本执行的守卫判断
    main()  # 启动评估
