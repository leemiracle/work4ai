from models.TD3.TD3 import TD3  # 导入 TD3 模型类（Twin Delayed DDPG：双 Q 网络取小值、延迟策略更新、目标策略平滑三件套的确定性策略算法）——注意 import 路径没有 robot_nav. 包前缀，说明本脚本需以 robot_nav/ 为工作目录运行（或把它加入 sys.path），与其它带前缀脚本的"仓库根运行"姿势不同

import torch  # PyTorch：设备选择与权重加载
import numpy as np  # NumPy：状态数组化
from robot_nav.SIM_ENV.sim import SIM  # 仿真环境（此行又带 robot_nav 前缀，印证上面的路径混用是仓里的历史遗留）
import yaml  # YAML 解析：读评估场景清单


# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
# main —— TD3 模型测试总入口（python rl_test.py 直接运行）
# 职责：加载训练好的 TD3 checkpoint，在 eval_world.yaml + eval_points.yaml 的
#       固定场景上跑确定性导航，统计总/平均/逐步奖励、碰撞率、到达率并写
#       TensorBoard test/* 曲线。与 rnn_test.py 同口径，差异有二：
#       ① 被测模型是纯 MLP 的 TD3（状态 25 维，激光被分箱压缩）；
#       ② 无历史队列——单帧状态直接决策。
# 输入：args（未使用）；输出：无返回值。
# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
def main(args=None):  # 测试主函数定义；args 形参暂未使用
    """Main testing function"""  # 原 docstring：主测试函数（原样保留）
    action_dim = 2  # number of actions produced by the model ——动作维度=2（线速度、角速度）
    max_action = 1  # maximum absolute value of output actions ——动作幅值上限 1
    state_dim = 25  # number of input values in the neural network (vector length of state input) ——状态维度仅 25：TD3.prepare_state 把 180 条激光扫描按箱取最小值压成 20 维（每箱保留最近障碍距离）+ 5 个标量（距离/cos/sin/上步动作 2 维）——轻量口径，与 RCPG/CNNTD3 的 185 维全扫描相对
    device = torch.device(  # 构造计算设备（跨两行）
        "cuda" if torch.cuda.is_available() else "cpu"  # 有 GPU 用 GPU，否则 CPU
    )  # using cuda if it is available, cpu otherwise ——设备选择收尾
    epoch = 0  # epoch number ——TensorBoard 记录轮次号（测试只跑一遍，恒为 0）
    max_steps = 300  # maximum number of steps in single episode ——单场景 300 步上限，超时算未完成

    model = TD3(  # 实例化 TD3 智能体（纯 MLP actor-critic，无卷积无循环）
        state_dim=state_dim,  # 状态维度 25，与 checkpoint 匹配
        action_dim=action_dim,  # 动作维度 2
        max_action=max_action,  # 动作上限 1
        device=device,  # 计算设备
        load_model=True,  # True = 加载训练好的权重（默认目录 robot_nav/models/TD3/checkpoint/）
        model_name="TD3",  # checkpoint 文件名用 "TD3"
    )  # instantiate a model ——模型实例化并完成加载

    sim = SIM(world_file="worlds/eval_world.yaml")  # instantiate environment ——评估专用世界文件建环境（考察对陌生地图的泛化）
    with open("robot_nav/eval_points.yaml") as file:  # 打开评估场景清单（注意路径带 robot_nav/ 前缀——与第一行的裸 import 形成对照，运行姿势需兼顾两者）
        points = yaml.safe_load(file)  # 安全解析 YAML
    robot_poses = points["robot"]["poses"]  # 各场景机器人初始位姿列表
    robot_goals = points["robot"]["goals"]  # 对应目标点列表（与 poses 按下标配对）

    assert len(robot_poses) == len(  # 断言起点数 == 目标数（配置防错）
        robot_goals  # 目标点个数（断言比对的另一侧：起点数必须与它相等）
    ), "Number of robot poses do not equal the robot goals"  # 断言失败信息

    print("..............................................")  # 分隔线
    print(f"Testing {len(robot_poses)} scenarios")  # 提示测试场景总数
    total_reward = 0.0  # 总奖励累加器
    total_steps = 0  # 总步数（算逐步平均用）
    col = 0  # 碰撞场景计数
    goals = 0  # 到达场景计数
    for idx in range(len(robot_poses)):  # 逐场景循环
        count = 0  # 本场景步数计数
        latest_scan, distance, cos, sin, collision, goal, a, reward = sim.reset(  # 重置到指定场景
            robot_state=robot_poses[idx],  # 本场景初始位姿
            robot_goal=robot_goals[idx],  # 本场景目标点
            random_obstacles=False,  # 障碍固定不随机 → 结果可复现
        )  # 取回初始观测
        done = False  # 场景结束标志
        while not done and count < max_steps:  # 未终止且未超 300 步
            state, terminal = model.prepare_state(  # 原始观测 → 25 维压缩状态（激光分箱取最小 + 标量归一化）
                latest_scan, distance, cos, sin, collision, goal, a  # 当前原始观测分量
            )  # 单帧状态直接用，无历史队列（TD3 是无记忆模型，靠状态里带上步动作弥补部分动力学信息）
            action = model.get_action(np.array(state), False)  # False = 确定性策略，无探索噪声（测试看真实水平）
            a_in = [(action[0] + 1) / 4, action[1]]  # 动作映射：线速度→[0,0.5] m/s（只前进），角速度原值
            latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 环境执行一步
                lin_velocity=a_in[0], ang_velocity=a_in[1]  # 物理指令
            )  # 取回下一观测与奖励
            total_reward += reward  # 累加总奖励
            total_steps += 1  # 累加总步数
            count += 1  # 本场景步数 +1
            if collision:  # 发生碰撞
                col += 1  # 碰撞 +1（done 即退出，每场景至多 1 次）
            if goal:  # 到达目标
                goals += 1  # 到达 +1
            done = collision or goal  # 碰撞或达标即场景结束
    avg_step_reward = total_reward / total_steps  # 逐步平均奖励（每步平均得分）
    avg_reward = total_reward / len(robot_poses)  # 场景平均奖励（每场平均得分）
    avg_col = col / len(robot_poses)  # 碰撞率
    avg_goal = goals / len(robot_poses)  # 到达率（导航成功率核心指标）
    print(f"Total Reward: {total_reward}")  # 打印总奖励
    print(f"Average Reward: {avg_reward}")  # 打印场景平均奖励
    print(f"Average Step Reward: {avg_step_reward}")  # 打印逐步平均奖励
    print(f"Average Collision rate: {avg_col}")  # 打印碰撞率
    print(f"Average Goal rate: {avg_goal}")  # 打印到达率
    print("..............................................")  # 分隔线
    model.writer.add_scalar("test/total_reward", total_reward, epoch)  # 总奖励入 TensorBoard
    model.writer.add_scalar("test/avg_reward", avg_reward, epoch)  # 场景平均奖励曲线
    model.writer.add_scalar("test/avg_step_reward", avg_step_reward, epoch)  # 逐步平均奖励曲线
    model.writer.add_scalar("test/avg_col", avg_col, epoch)  # 碰撞率曲线
    model.writer.add_scalar("test/avg_goal", avg_goal, epoch)  # 到达率曲线


if __name__ == "__main__":  # 直接运行本文件时才执行
    main()  # 启动测试主流程
