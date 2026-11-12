# ══════【教学注释版 · marl_test_random.py — 随机场景测试入口】══════
# 任务：加载 TDR-MARL-train 训练权重，在 multi_robot_world 上连跑 1000 局
# 随机场景（每局随机起点+随机目标，到达即换新目标），统计平均奖励/碰撞/
# 到达数/动作分布/注意力熵，写入 TensorBoard（12 条标量+2 直方图+2 张图）。
# 与 marl_test_single.py 的分工：本文件无"成功率"概念（到达不终结回合），
# 口径是持续型任务的平均性能；single 是固定场景 100 局、全员到达=成功。
# 关于"对手"的代码实证：与 single 相同——只建一个 TD3 实例、加载同一份
# 训练权重、get_action 一次驱动全部 5 机；差别在环境 reset 随机化（起点
# 均匀采样+两两间距≥0.6m+随机目标），而非对手策略（不存在随机策略对手）。
# ════════════════════════════════════════════════════【导读完】
import statistics  # 【基础】标准库统计模块：求均值 mean 与样本标准差 stdev
from pathlib import Path  # 【基础】路径类：构造权重加载目录

from tqdm import tqdm  # 【基础】进度条库：可视化 1000 个随机场景的完成进度
import matplotlib.pyplot as plt  # 【基础】matplotlib 绘图库：文件末尾画动作值对数直方图并写入 TensorBoard
from robot_nav.models.MARL.marlTD3.marlTD3 import TD3  # 【基础】TD3 智能体类：与训练同一实现，此处加载训练好的权重

import torch  # 【基础】PyTorch：张量与神经网络
import numpy as np  # 【基础】NumPy：数组与直方图计算
from robot_nav.SIM_ENV.marl_sim import MARL_SIM  # 【基础】训练同款环境类：reset 随机化起点/目标，且到达即换发新随机目标（持续任务）


# ── 函数 outside_of_bounds：出界检测 ──
# 职责：判断是否有机器人跑出以世界中心 (6,6) 为心、半边长 10.5 的正方形边界。
# 输入：poses——各机器人位姿列表，每个元素为 [x, y, theta]；输出：布尔值。
# 调用关系：主循环每步调用；返回值是本脚本"出界即重置一局"的终止条件之一
# （与训练脚本一致；single 测试未使用该条件）。
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
        norm_x = pose[0] - 6  # 【基础】x 坐标对世界中心 6 取偏移（中心化）
        norm_y = pose[1] - 6  # 【基础】y 坐标对世界中心 6 取偏移
        if abs(norm_x) > 10.5 or abs(norm_y) > 10.5:  # 【基础】任一方向偏心超过 10.5 判出界；random 口径下随机目标可能贴边，此护栏能兜住极端局
            outside = True  # 【基础】置出界标志
            break  # 【基础】提前退出循环
    return outside  # 【基础】返回是否出界


# ── 函数 main：random 随机场景测试主入口 ──
# 职责：加载训练产物，在 multi_robot_world 连跑 1000 局随机场景，统计平均
#       奖励/碰撞对数/到达数/动作均值/注意力熵（均值±标准差），
#       打印并写入 TensorBoard（标量 + 动作直方图 + 对数直方图图片）。
# 输入：args=None（占位）；输出：无返回值；产物=控制台打印 + TensorBoard 日志。
# 调用关系：文件底部 if __name__ 直接调用；与 single 口径的差异见循环内注释。
def main(args=None):  # 【基础】主函数定义（args 未使用）
    """Main training function"""

    # ---- Hyperparameters and setup ----  # 【基础】分节注释：以下为测试超参与设置
    action_dim = 2  # number of actions produced by the model  # 【基础】动作维度 2（必须与训练一致）
    max_action = 1  # maximum absolute value of output actions  # 【基础】动作幅值上限 1（与训练一致）
    state_dim = 11  # number of input values in the neural network (vector length of state input)  # 【基础】状态维度 11（与训练一致——加载权重的形状必须对得上）
    device = torch.device(  # 【基础】选择计算设备
        "cuda" if torch.cuda.is_available() else "cpu"  # 【基础】有 GPU 用 cuda 否则 cpu
    )  # using cuda if it is available, cpu otherwise  # 【基础】device 传给 TD3 构造器
    epoch = 1  # starting epoch number  # 【基础】轮号=1：作为末尾所有 TensorBoard 曲线的横轴（单次测试快照）
    episode = 0  # 【基础】测试局计数从 0 起（1000 局计数器）
    max_steps = 600  # maximum number of steps in single episode  # 【教学】单局上限 600 步（训练是 300）：持续任务下防无限跑，超时强制换下一随机场景
    steps = 0  # starting step number  # 【基础】局内步数计数器
    save_every = 5  # save the model every n training cycles  # 【基础】存档间隔：测试不调用 train()，实际不会存档（同构遗留参数）
    test_scenarios = 1000  # 【教学】测试规模 1000 局随机场景（single 是固定场景 100 局）——量大因为场景随机，需平均掉方差

    # ---- Instantiate simulation environment and model ----  # 【基础】分节注释：建环境与模型
    sim = MARL_SIM(  # 【基础】实例化多机器人仿真环境（与训练同款类）
        world_file="worlds/multi_robot_world.yaml",  # 【基础】世界配置：与训练同一个世界文件（12x12、5 机圆环初始分布、共享初目标 (9,9)）
        disable_plotting=True,  # 【基础】无头模式：关渲染提速
        reward_phase=2,  # 【教学】奖励版本 phase 2（训练用 phase 1）：测试奖励只用于统计性能，不影响已训练策略的动作
    )  # instantiate environment  # 【基础】与 single 的差别：reset 会随机化起点与目标，到达即换新目标

    model = TD3(  # 【基础】实例化 TD3（网络结构与训练时一致，用于装载权重）
        state_dim=state_dim,  # 【基础】状态维度 11
        action_dim=action_dim,  # 【基础】动作维度 2
        max_action=max_action,  # 【基础】动作界 ±1
        num_robots=sim.num_robots,  # 【基础】机器人数 5（与训练一致）
        device=device,  # 【基础】计算设备
        save_every=save_every,  # 【基础】存档间隔（测试中不触发）
        load_model=True,  # 【教学】True——构造时立即加载训练产物（训练脚本为 False）
        model_name="TDR-MARL-test",  # 【基础】本实例命名：TensorBoard 日志 comment 后缀；不训练就不会产生存档
        load_model_name="TDR-MARL-train",  # 【教学】与 single 完全相同的加载约定：两个测试脚本消费的是同一份 TDR-MARL-train_*.pth 四件套
        load_directory=Path("robot_nav/models/MARL/marlTD3/checkpoint"),  # 【基础】加载目录（与训练存档目录相同）
        attention="igs",  # 【教学】注意力后端 "igs"=IGA 注意力（iga.py 的 Attention 类）：必须与训练用的一致才能对上权重；注：训练脚本写的 "iga" 是非法值（TD3 构造器只认 igs/g2anet，见 marl_train.py 注释）
    )  # instantiate a model  # 【基础】构造完成即已载入训练权重（load 内部打印 Loaded weights from: ...）

    connections = torch.tensor(  # 【基础】初始零连接张量
        [[0.0 for _ in range(sim.num_robots - 1)] for _ in range(sim.num_robots)]  # 【基础】形状 (5,4) 全零
    )  # 【基础】connections 零连接张量闭合

    # ---- Take initial step in environment ----  # 【基础】分节注释：取初始观测
    poses, distance, cos, sin, collision, goal, a, reward, positions, goal_positions = (  # 【基础】十元组解包起始行：位姿/距离/夹角cos/夹角sin/碰撞/到达/动作/奖励/位置/目标
        sim.step([[0, 0] for _ in range(sim.num_robots)], connections)  # 【基础】全零动作迈出第一步
    )  # get the initial step state  # 【基础】得到初始观测 s0
    running_goals = 0  # 【基础】本局累计到达事件数
    running_reward = 0  # 【基础】本局累计奖励（5 机求和）
    running_collisions = 0  # 【基础】本局累计碰撞对数（下面累加时已即时 /2，与 single 的事后统一 /2 不同）
    running_timesteps = 0  # 【基础】本局步数

    reward_per_ep = []  # 【基础】以下 6 个容器按"局/步"累积统计样本（比 single 少局长与超时两项）
    goals_per_ep = []  # 【基础】每局总到达数
    col_per_ep = []  # 【基础】每局碰撞对数
    lin_actions = []  # 【基础】所有步所有机的线速度样本（画分布）
    ang_actions = []  # 【基础】角速度样本
    entropy_list = []  # 【基础】每步注意力权重熵样本
    epsilon = 1e-6  # 【基础】数值稳定小量：防 log(0) 与除零
    pbar = tqdm(total=test_scenarios)  # 【基础】进度条：总数 1000 局
    while episode < test_scenarios:  # 【教学】测试主循环：跑满 1000 局随机场景即结束
        state, terminal = model.prepare_state(  # 【基础】编码当前观测为每机 11 维状态（与训练同一函数）
            poses, distance, cos, sin, collision, a, goal_positions  # 【基础】原始十元组字段
        )  # 【基础】prepare_state 调用闭合
        action, connection, combined_weights = model.get_action(  # 【基础】已训练策略前向：一次出 5 机动作+连接+权重
            np.array(state), False  # 【教学】add_noise=False：测试不加探索噪声，纯确定性策略——评估口径核心（与 single 相同）
        )  # get an action from the model  # 【基础】动作形状 (5,2)

        combined_weights_norm = combined_weights / (  # 【基础】注意力权重按行归一化成分布
            combined_weights.sum(dim=-1, keepdim=True) + epsilon  # 【基础】每行求和（keepdim 保形）+ε 防除零
        )  # 【基础】权重归一化表达式闭合

        # Entropy for analysis/logging  # 【中文注】原英文注释行：注意力熵仅用于分析/日志，不参与控制
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

        a_in = [  # 【基础】构造真正下发给机器人的物理动作
            [(a[0] + 1) / 4, a[1]] for a in action  # 【基础】逐机仿射映射：线速度 [-1,1]→[0,0.5] m/s（不倒车），角速度直传
        ]  # clip linear velocity to [0, 0.5] m/s range  # 【教学·勘误】原注释称 clip，实为线性重标度 (a+1)/4 而非裁剪；已到达的机器人由 MARL_SIM 内部换发新目标继续行动

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
            goal_positions,  # 【基础】目标位置（到达换新目标后会更新）
        ) = sim.step(  # 【基础】推进一步
            a_in, connection, combined_weights  # 【基础】动作+连接+权重（后两者用于渲染注意力边）
        )  # get data from the environment  # 【教学】MARL_SIM 语义：到达的机器人当场换发新随机目标继续跑——random 口径是持续型任务，"到达"只计事件不终结回合
        running_goals += sum(goal)  # 【基础】累计本步到达事件（一局内可多次到达）
        running_collisions += sum(collision) / 2  # 【教学】与 single 的核算点差异：此处即时 /2 折算"碰撞对数"（reactive 模式一对互撞两机都置位）
        running_reward += sum(reward)  # 【基础】累计 5 机奖励和
        running_timesteps += 1  # 【基础】步数 +1
        for j in range(len(a_in)):  # 【基础】逐机收集动作样本
            lin_actions.append(a_in[j][0].item())  # 【基础】线速度样本（张量转 float）
            ang_actions.append(a_in[j][1].item())  # 【基础】角速度样本
        outside = outside_of_bounds(poses)  # 【基础】出界检测（本脚本终止条件用到，与 single 不同）

        if (  # 【基础】回合终止判定开始
            sum(collision) > 0.5 or steps == max_steps or outside  # 【教学】random 口径三条件：任一碰撞 / 600 步超时 / 出界；没有"全员到达"条件——到达不终结（新目标持续发放），故本脚本不打印成功率，改报平均到达数等平均指标
        ):  # reset environment of terminal state reached, or max_steps were taken  # 【基础】进入重置分支
            (  # 【基础】重置十元组解包（进入下一随机场景）
                poses,  # 【基础】随机新起点位姿
                distance,  # 【基础】到新目标的距离
                cos,  # 【基础】夹角余弦
                sin,  # 【基础】夹角正弦
                collision,  # 【基础】全 False
                goal,  # 【基础】全 False
                a,  # 【基础】全零动作
                reward,  # 【基础】初始奖励
                positions,  # 【基础】随机初始位置
                goal_positions,  # 【基础】随机新目标
            ) = sim.reset()  # 【教学】MARL_SIM.reset 随机化：每机在 [3,9]x[3,9] 均匀抽起点（两两间距≥0.6m）+随机朝向+各自抽新目标——"random 场景"的全部随机性来源
            reward_per_ep.append(running_reward)  # 【基础】记录本局总奖励
            running_reward = 0  # 【基础】清零
            goals_per_ep.append(running_goals)  # 【基础】记录本局总到达数
            running_goals = 0  # 【基础】清零
            col_per_ep.append(running_collisions)  # 【基础】记录本局碰撞对数
            running_collisions = 0  # 【基础】清零

            steps = 0  # 【基础】新局步数清零
            episode += 1  # 【基础】完成局数 +1
            pbar.update(1)  # 【基础】进度条前进 1
        else:  # 【基础】未终止继续本局
            steps += 1  # 【基础】步数 +1

    reward_per_ep = np.array(reward_per_ep, dtype=np.float32)  # 【基础】各统计列表转 float32 数组（供均值/标准差/直方图计算）
    goals_per_ep = np.array(goals_per_ep, dtype=np.float32)  # 【基础】每局到达数转数组
    col_per_ep = np.array(col_per_ep, dtype=np.float32)  # 【基础】每局碰撞对数转数组
    lin_actions = np.array(lin_actions, dtype=np.float32)  # 【基础】线速度样本转数组
    ang_actions = np.array(ang_actions, dtype=np.float32)  # 【基础】角速度样本转数组
    entropy = np.array(entropy_list, dtype=np.float32)  # 【基础】每步熵样本转数组
    avg_ep_reward = statistics.mean(reward_per_ep)  # 【基础】平均每局总奖励
    avg_ep_reward_std = statistics.stdev(reward_per_ep)  # 【基础】奖励样本标准差
    avg_ep_col = statistics.mean(col_per_ep)  # 【基础】平均每局碰撞对数
    avg_ep_col_std = statistics.stdev(col_per_ep)  # 【基础】碰撞标准差
    avg_ep_goals = statistics.mean(goals_per_ep)  # 【基础】平均每局到达数（random 口径的核心性能指标，取代 single 的成功率）
    avg_ep_goals_std = statistics.stdev(goals_per_ep)  # 【基础】到达标准差
    mean_lin_action = statistics.mean(lin_actions)  # 【基础】线速度总体均值（行为特征：偏快/偏慢）
    lin_actions_std = statistics.stdev(lin_actions)  # 【基础】线速度标准差
    mean_ang_action = statistics.mean(ang_actions)  # 【基础】角速度总体均值
    ang_actions_std = statistics.stdev(ang_actions)  # 【基础】角速度标准差
    mean_entropy = statistics.mean(entropy)  # 【基础】注意力熵均值（低=关注集中，高=分散）
    mean_entropy_std = statistics.stdev(entropy)  # 【基础】熵标准差

    print(f"avg_ep_reward: {avg_ep_reward}")  # 【基础】输出平均局奖励
    print(f"avg_ep_reward_std: {avg_ep_reward_std}")  # 【基础】输出奖励波动
    print(f"avg_ep_col: {avg_ep_col}")  # 【基础】输出平均碰撞对数
    print(f"avg_ep_col_std: {avg_ep_col_std}")  # 【基础】输出碰撞波动
    print(f"avg_ep_goals: {avg_ep_goals}")  # 【基础】输出平均到达数
    print(f"avg_ep_goals_std: {avg_ep_goals_std}")  # 【基础】输出到达波动
    print(f"mean_lin_action: {mean_lin_action}")  # 【基础】输出线速度均值
    print(f"lin_actions_std: {lin_actions_std}")  # 【基础】输出线速度波动
    print(f"mean_ang_action: {mean_ang_action}")  # 【基础】输出角速度均值
    print(f"ang_actions_std: {ang_actions_std}")  # 【基础】输出角速度波动
    print(f"mean_entropy: {mean_entropy}")  # 【基础】输出注意力熵均值
    print(f"mean_entropy_std: {mean_entropy_std}")  # 【基础】输出熵波动
    print("..............................................")  # 【基础】分隔线
    model.writer.add_scalar("test/avg_ep_reward", avg_ep_reward, epoch)  # 【基础】TensorBoard 标量：平均局奖励（横轴 epoch=1，本脚本单点快照）
    model.writer.add_scalar("test/avg_ep_reward_std", avg_ep_reward_std, epoch)  # 【基础】标量：奖励标准差
    model.writer.add_scalar("test/avg_ep_col", avg_ep_col, epoch)  # 【基础】标量：平均碰撞对数
    model.writer.add_scalar("test/avg_ep_col_std", avg_ep_col_std, epoch)  # 【基础】标量：碰撞标准差
    model.writer.add_scalar("test/avg_ep_goals", avg_ep_goals, epoch)  # 【基础】标量：平均到达数
    model.writer.add_scalar("test/avg_ep_goals_std", avg_ep_goals_std, epoch)  # 【基础】标量：到达标准差
    model.writer.add_scalar("test/mean_lin_action", mean_lin_action, epoch)  # 【基础】标量：线速度均值
    model.writer.add_scalar("test/lin_actions_std", lin_actions_std, epoch)  # 【基础】标量：线速度标准差
    model.writer.add_scalar("test/mean_ang_action", mean_ang_action, epoch)  # 【基础】标量：角速度均值
    model.writer.add_scalar("test/ang_actions_std", ang_actions_std, epoch)  # 【基础】标量：角速度标准差
    model.writer.add_scalar("test/mean_entropy", mean_entropy, epoch)  # 【基础】标量：注意力熵均值
    model.writer.add_scalar("test/mean_entropy_std", mean_entropy_std, epoch)  # 【基础】标量：熵标准差
    bins = 100  # 【基础】直方图分箱数（值域 [-1,1] 或 [0,0.5] 切 100 箱）
    model.writer.add_histogram("test/lin_actions", lin_actions, epoch, max_bins=bins)  # 【基础】线速度分布直方图写入 TensorBoard（观察是否饱和在 0.5 等）
    model.writer.add_histogram("test/ang_actions", ang_actions, epoch, max_bins=bins)  # 【基础】角速度分布直方图写入 TensorBoard

    counts, bin_edges = np.histogram(lin_actions, bins=bins)  # 【基础】线速度分布：各箱计数与箱边界
    fig, ax = plt.subplots()  # 【基础】新建 matplotlib 画布与坐标轴
    ax.bar(  # 【基础】画柱状直方图
        bin_edges[:-1], counts, width=np.diff(bin_edges), align="edge", log=True  # 【基础】每箱左边界为 x、箱宽=相邻边界之差、柱与边对齐、y 轴取对数
    )  # Log scale on y-axis  # 【教学】对数纵轴的作用：动作值高度集中（如线速度饱和在 0.5）时线性轴会压扁其余箱，log 轴让低频箱也可见
    ax.set_xlabel("Value")  # 【基础】x 轴标签：动作值
    ax.set_ylabel("Frequency (Log Scale)")  # 【基础】y 轴标签：频数（对数刻度）
    ax.set_title("Histogram with Log Scale")  # 【基础】图标题
    model.writer.add_figure("test/lin_actions_hist", fig)  # 【基础】把 matplotlib 图作为图片写入 TensorBoard（test/lin_actions_hist 面板）

    counts, bin_edges = np.histogram(ang_actions, bins=bins)  # 【基础】角速度分布：各箱计数与箱边界
    fig, ax = plt.subplots()  # 【基础】再建一张画布
    ax.bar(  # 【基础】画柱状直方图
        bin_edges[:-1], counts, width=np.diff(bin_edges), align="edge", log=True  # 【基础】同样参数：左对齐、箱宽 diff、对数 y 轴
    )  # Log scale on y-axis  # 【教学】同上：对数纵轴直方图，观察角速度分布形态（如集中在 0=直行偏好）
    ax.set_xlabel("Value")  # 【基础】x 轴标签
    ax.set_ylabel("Frequency (Log Scale)")  # 【基础】y 轴标签
    ax.set_title("Histogram with Log Scale")  # 【基础】图标题
    model.writer.add_figure("test/ang_actions_hist", fig)  # 【基础】第二张直方图写入 TensorBoard


if __name__ == "__main__":  # 【基础】仅当直接运行本文件时执行测试
    main()  # 【基础】启动 random 口径测试
