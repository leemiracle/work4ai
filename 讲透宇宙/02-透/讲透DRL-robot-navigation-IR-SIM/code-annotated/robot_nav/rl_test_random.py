from robot_nav.models.SAC.SAC import SAC  # 导入 SAC 模型类（Soft Actor-Critic，最大熵强化学习：目标里除奖励外还最大化策略熵，输出随机策略、训练稳定，广泛用于机器人连续控制）
import statistics  # 标准库统计模块：算均值 mean 与样本标准差 stdev
import numpy as np  # NumPy：数组化奖励/动作序列、画直方图
import tqdm  # 进度条库：1000 个场景的长循环可视化进度
import matplotlib.pyplot as plt  # 绘图库：画动作分布直方图（对数纵轴）

import torch  # PyTorch：设备选择与权重加载
from robot_nav.SIM_ENV.sim import SIM  # 仿真环境：支持随机起点/随机目标/随机障碍的 reset


# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
# main —— SAC 模型「随机场景大样本」测试总入口（python rl_test_random.py）
# 职责：加载 SAC checkpoint，在 eval_world 上随机生成 1000 个场景（随机起点、
#       随机目标、6 类障碍随机摆放）跑确定性导航，统计口径远超其余测试脚本：
#       逐步/回合/非终止步奖励的均值与标准差、到达目标步数、线/角动作分布
#       （含直方图），全部写入 TensorBoard test/* 曲线与图表。
# 输入：args（未使用）；输出：无返回值。
# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
def main(args=None):  # 测试主函数定义；args 形参暂未使用
    """Main testing function"""  # 原 docstring：主测试函数（原样保留）
    action_dim = 2  # number of actions produced by the model ——动作维度=2（线速度、角速度）
    max_action = 1  # maximum absolute value of output actions ——动作幅值上限 1
    state_dim = 25  # number of input values in the neural network (vector length of state input) ——状态维度 25：与 TD3 同口径（激光分箱压缩为 20 维 + 5 个标量），SAC/CNNTD3 家族用同一套轻量状态
    device = torch.device(  # 构造计算设备（跨两行）
        "cuda" if torch.cuda.is_available() else "cpu"  # 有 GPU 用 GPU，否则 CPU
    )  # using cuda if it is available, cpu otherwise ——设备选择收尾
    epoch = 0  # epoch number ——TensorBoard 轮次号（单次测试恒为 0）
    max_steps = 300  # maximum number of steps in single episode ——单场景 300 步上限
    test_scenarios = 1000  # 测试场景总数：1000——大样本让均值/标准差有统计置信度（其余测试脚本只有十几个固定场景）

    model = SAC(  # 实例化 SAC 智能体（actor + 双 critic + 温度系数都在内部建好）
        state_dim=state_dim,  # 状态维度 25
        action_dim=action_dim,  # 动作维度 2
        max_action=max_action,  # 动作上限 1
        device=device,  # 计算设备
        load_model=True,  # True = 加载训练好的权重（默认目录 robot_nav/models/SAC/checkpoint/）
        model_name="SAC",  # checkpoint 文件名 "SAC"
    )  # instantiate a model ——模型实例化并完成加载

    sim = SIM(  # 实例化环境（参数跨两行）
        world_file="worlds/eval_world.yaml", disable_plotting=False  # 评估世界文件；False = 开启绘图（可实时看机器人在随机场景里跑）
    )  # instantiate environment ——环境就绪

    print("..............................................")  # 分隔线
    print(f"Testing {test_scenarios} scenarios")  # 提示将测试 1000 个随机场景
    total_reward = []  # 逐步奖励列表（每一步的 reward 都收集，最后算逐步统计）
    reward_per_ep = []  # 回合总奖励列表（只收集"正常终止"的场景：碰撞或达标，超时回合不入账）
    lin_actions = []  # 所有线速度动作收集器（画分布用）
    ang_actions = []  # 所有角速度动作收集器（画分布用）
    total_steps = 0  # 总步数计数
    col = 0  # 碰撞场景计数
    goals = 0  # 到达目标场景计数
    inter_rew = []  # 非终止步奖励列表：只收集"之后还在继续"的普通步——把终止步的大奖/大罚剔出来单独看
    steps_to_goal = []  # 各成功场景"走了多少步到达目标"列表（效率指标）
    for _ in tqdm.tqdm(range(test_scenarios)):  # 外层循环 1000 个场景，tqdm 包装迭代器 → 终端实时进度条
        count = 0  # 本场景步数计数
        ep_reward = 0  # 本场景奖励累计
        latest_scan, distance, cos, sin, collision, goal, a, reward = sim.reset(  # 重置环境（参数跨多行）
            robot_state=None,  # None = 起点位姿随机生成（对照 rl_test.py 的固定起点）
            robot_goal=None,  # None = 目标点随机生成
            random_obstacles=True,  # True = 障碍物随机摆放——与固定场景测试互补，考察泛化
            random_obstacle_ids=[i + 1 for i in range(6)],  # 参与随机摆放的障碍 ID 列表 [1..6]（列表推导式生成）
        )  # 取回随机场景的初始观测
        done = False  # 场景结束标志
        while not done and count < max_steps:  # 未终止且未超 300 步
            state, terminal = model.prepare_state(  # 原始观测 → 25 维压缩归一化状态
                latest_scan, distance, cos, sin, collision, goal, a  # 当前原始观测分量
            )  # 单帧状态，无历史队列（SAC 是无记忆模型）
            action = model.get_action(np.array(state), False)  # False = 不加噪声，取确定性/均值动作（SAC 训练时采样，测试时取均值）
            a_in = [(action[0] + 1) / 4, action[1]]  # 动作映射：线速度→[0,0.5] m/s，角速度原值
            lin_actions.append(a_in[0])  # 记录实际执行的线速度（分布统计用）
            ang_actions.append(a_in[1])  # 记录实际执行的角速度（分布统计用）
            latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 环境执行一步
                lin_velocity=a_in[0], ang_velocity=a_in[1]  # 物理速度指令
            )  # 取回下一观测与奖励
            ep_reward += reward  # 本场景奖励累计
            total_reward.append(reward)  # 全局逐步奖励列表追加
            total_steps += 1  # 总步数 +1
            count += 1  # 本场景步数 +1
            if collision:  # 发生碰撞
                col += 1  # 碰撞 +1（done 即退出，每场景至多 1 次）
            if goal:  # 到达目标
                goals += 1  # 到达 +1
                steps_to_goal.append(count)  # 记录本场景到达目标所耗步数（含最后一步）
            done = collision or goal  # 碰撞或达标即场景结束
            if done:  # 若场景在本步终止
                reward_per_ep.append(ep_reward)  # 本场景总奖励入"已终结回合"列表
            if not done:  # 若本步未终止（还能继续走）
                inter_rew.append(reward)  # 该步奖励入"普通步"列表（剔除终止步的大奖惩，看日常步奖励水平）

    total_reward = np.array(total_reward)  # 逐步奖励列表 → NumPy 数组（统计运算更快）
    reward_per_ep = np.array(reward_per_ep)  # 回合奖励 → 数组
    inter_rew = np.array(inter_rew)  # 非终止步奖励 → 数组
    steps_to_goal = np.array(steps_to_goal)  # 到达步数 → 数组
    lin_actions = np.array(lin_actions)  # 线速度动作 → 数组
    ang_actions = np.array(ang_actions)  # 角速度动作 → 数组
    avg_step_reward = statistics.mean(total_reward)  # 逐步平均奖励（全体步的均值）
    avg_step_reward_std = statistics.stdev(total_reward)  # 逐步奖励样本标准差（波动有多大）
    avg_ep_reward = statistics.mean(reward_per_ep)  # 已终结回合的平均总奖励
    avg_ep_reward_std = statistics.stdev(reward_per_ep)  # 回合总奖励标准差
    avg_col = col / test_scenarios  # 碰撞率 = 碰撞场景 / 1000
    avg_goal = goals / test_scenarios  # 到达率 = 达标场景 / 1000
    avg_inter_step_rew = statistics.mean(inter_rew)  # 普通步（非终止步）平均奖励
    avg_inter_step_rew_std = statistics.stdev(inter_rew)  # 普通步奖励标准差
    avg_steps_to_goal = statistics.mean(steps_to_goal)  # 平均到达步数（越小说明路径越高效）
    avg_steps_to_goal_std = statistics.stdev(steps_to_goal)  # 到达步数标准差
    mean_lin_action = statistics.mean(lin_actions)  # 线速度动作均值（是否总在满速冲？）
    lin_actions_std = statistics.stdev(lin_actions)  # 线速度动作标准差（动作是否多样）
    mean_ang_action = statistics.mean(ang_actions)  # 角速度动作均值（有无系统性偏转倾向）
    ang_actions_std = statistics.stdev(ang_actions)  # 角速度动作标准差
    print(f"avg_step_reward {avg_step_reward}")  # 打印逐步平均奖励
    print(f"avg_step_reward_std: {avg_step_reward_std}")  # 打印其标准差
    print(f"avg_ep_reward: {avg_ep_reward}")  # 打印回合平均奖励
    print(f"avg_ep_reward_std: {avg_ep_reward_std}")  # 打印其标准差
    print(f"avg_col: {avg_col}")  # 打印碰撞率
    print(f"avg_goal: {avg_goal}")  # 打印到达率
    print(f"avg_inter_step_rew: {avg_inter_step_rew}")  # 打印普通步平均奖励
    print(f"avg_inter_step_rew_std: {avg_inter_step_rew_std}")  # 打印其标准差
    print(f"avg_steps_to_goal: {avg_steps_to_goal}")  # 打印平均到达步数
    print(f"avg_steps_to_goal_std: {avg_steps_to_goal_std}")  # 打印其标准差
    print(f"mean_lin_action: {mean_lin_action}")  # 打印线速度均值
    print(f"lin_actions_std: {lin_actions_std}")  # 打印线速度标准差
    print(f"mean_ang_action: {mean_ang_action}")  # 打印角速度均值
    print(f"ang_actions_std: {ang_actions_std}")  # 打印角速度标准差
    print("..............................................")  # 分隔线
    model.writer.add_scalar("test/avg_step_reward", avg_step_reward, epoch)  # 逐步平均奖励入 TensorBoard
    model.writer.add_scalar("test/avg_step_reward_std", avg_step_reward_std, epoch)  # 其标准差曲线
    model.writer.add_scalar("test/avg_ep_reward", avg_ep_reward, epoch)  # 回合平均奖励曲线
    model.writer.add_scalar("test/avg_ep_reward_std", avg_ep_reward_std, epoch)  # 其标准差曲线
    model.writer.add_scalar("test/avg_col", avg_col, epoch)  # 碰撞率曲线
    model.writer.add_scalar("test/avg_goal", avg_goal, epoch)  # 到达率曲线
    model.writer.add_scalar("test/avg_inter_step_rew", avg_inter_step_rew, epoch)  # 普通步奖励曲线
    model.writer.add_scalar(  # 普通步奖励标准差（参数跨三行）
        "test/avg_inter_step_rew_std", avg_inter_step_rew_std, epoch  # 指标名、值、横轴
    )  # 该曲线写入收尾
    model.writer.add_scalar("test/avg_steps_to_goal", avg_steps_to_goal, epoch)  # 平均到达步数曲线
    model.writer.add_scalar("test/avg_steps_to_goal_std", avg_steps_to_goal_std, epoch)  # 其标准差曲线
    model.writer.add_scalar("test/mean_lin_action", mean_lin_action, epoch)  # 线速度均值曲线
    model.writer.add_scalar("test/lin_actions_std", lin_actions_std, epoch)  # 线速度标准差曲线
    model.writer.add_scalar("test/mean_ang_action", mean_ang_action, epoch)  # 角速度均值曲线
    model.writer.add_scalar("test/ang_actions_std", ang_actions_std, epoch)  # 角速度标准差曲线
    bins = 100  # 直方图分箱数：把 [-1,1] 动作区间切 100 格看分布形状
    model.writer.add_histogram("test/lin_actions", lin_actions, epoch, max_bins=bins)  # 线速度分布写入 TensorBoard 直方图（看策略是否塌缩到少数动作值）
    model.writer.add_histogram("test/ang_actions", ang_actions, epoch, max_bins=bins)  # 角速度分布直方图

    counts, bin_edges = np.histogram(lin_actions, bins=bins)  # 手工统计线速度直方图（各箱计数 + 箱边界），准备画 matplotlib 图
    fig, ax = plt.subplots()  # 建一张画布和坐标轴
    ax.bar(  # 画柱状图（参数跨三行）
        bin_edges[:-1], counts, width=np.diff(bin_edges), align="edge", log=True  # x=各箱左边界，y=计数，宽=箱宽，对齐箱边缘；log=True 纵轴取对数
    )  # Log scale on y-axis ——纵轴对数刻度：低频动作值也能看清（不被动作为 0/0.5 的高峰淹没）
    ax.set_xlabel("Value")  # x 轴标签：动作取值
    ax.set_ylabel("Frequency (Log Scale)")  # y 轴标签：频数（对数刻度）
    ax.set_title("Histogram with Log Scale")  # 图标题
    model.writer.add_figure("test/lin_actions_hist", fig)  # 把 matplotlib 图也存进 TensorBoard（test/lin_actions_hist）

    counts, bin_edges = np.histogram(ang_actions, bins=bins)  # 同法统计角速度直方图
    fig, ax = plt.subplots()  # 再建一张画布
    ax.bar(  # 画角速度柱状图（参数跨三行）
        bin_edges[:-1], counts, width=np.diff(bin_edges), align="edge", log=True  # 同款参数：箱左边界为 x、计数为 y、对数纵轴
    )  # Log scale on y-axis ——纵轴对数刻度
    ax.set_xlabel("Value")  # x 轴标签
    ax.set_ylabel("Frequency (Log Scale)")  # y 轴标签
    ax.set_title("Histogram with Log Scale")  # 图标题
    model.writer.add_figure("test/ang_actions_hist", fig)  # 角速度分布图存入 TensorBoard——两张直方图合看，可诊断策略是否模式单一（如只硬打满角速度）


if __name__ == "__main__":  # 直接运行本文件时才执行
    main()  # 启动随机场景大样本测试
