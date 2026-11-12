from collections import deque  # 双端队列：维护最近 5 帧状态的滑动窗口，作为 GRU 循环网络的时间维输入（与训练脚本同款机制，但窗口更短，见下）

from robot_nav.models.RCPG.RCPG import RCPG  # 导入 RCPG 模型类：rnn_* 系测试脚本服务的对象（GRU 循环 actor-critic，与 rnn_train.py 训练出的 checkpoint 配套）

import torch  # PyTorch：用于选择计算设备、加载模型权重
import numpy as np  # NumPy：把状态队列转数组、承接模型输出动作
from robot_nav.SIM_ENV.sim import SIM  # 仿真环境类：提供 step/reset 接口
import yaml  # YAML 解析库：读取评估场景清单文件（起点/终点坐标对）


# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
# main —— RCPG 模型测试总入口（python rnn_test.py 直接运行）
# 职责：加载训练好的 RCPG checkpoint，在 eval_world.yaml 世界 + eval_points.yaml
#       固定场景清单上逐个场景跑「确定性策略」导航，统计总/平均奖励、逐步奖励、
#       碰撞率、到达率，并写入 TensorBoard 的 test/* 曲线。
# 输入：args（未使用）；输出：无返回值（指标打印 + TensorBoard 落盘）。
# 评估口径：固定起点/终点、无随机障碍（random_obstacles=False）——可复现的
#       "标准化考试"，与 rl_test_random.py 的随机大样本评估互补。
# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
def main(args=None):  # 测试主函数定义；args 形参暂未使用
    """Main testing function"""  # 原 docstring：主测试函数（原样保留）
    action_dim = 2  # number of actions produced by the model ——动作维度=2（线速度、角速度），必须与训练时一致
    max_action = 1  # maximum absolute value of output actions ——动作幅值上限 1，与训练一致
    state_dim = 185  # number of input values in the neural network (vector length of state input) ——状态维度 185 = 180 条激光射线 + 5 个标量（目标距离/朝向 cos、sin/上步动作 2 维），须与被测模型结构完全对应
    device = torch.device(  # 构造计算设备（表达式跨两行）
        "cuda" if torch.cuda.is_available() else "cpu"  # 有 GPU 用 GPU，否则 CPU（测试计算量小，CPU 也能跑）
    )  # using cuda if it is available, cpu otherwise ——设备选择收尾
    epoch = 0  # epoch number ——TensorBoard 记录用的轮次号（测试只跑一遍，固定为 0）
    max_steps = 300  # maximum number of steps in single episode ——单场景最多 300 步，超时视为失败（未碰撞也未到达）

    model = RCPG(  # 实例化 RCPG 智能体（注意：测试不传 save_every/rnn 等训练参数，走默认值）
        state_dim=state_dim,  # 状态维度 185，与 checkpoint 匹配
        action_dim=action_dim,  # 动作维度 2
        max_action=max_action,  # 动作上限 1
        device=device,  # 计算设备
        load_model=True,  # 关键差异：True = 从默认目录 robot_nav/models/RCPG/checkpoint/ 加载训练好的权重（文件名默认 "RCPG"+"gru"="RCPGgru"，与训练脚本 rnn="gru" 恰好对上）
    )  # instantiate a model ——模型实例化并完成权重加载

    sim = SIM(world_file="worlds/eval_world.yaml")  # instantiate environment ——用「评估专用世界文件」建环境（与训练世界不同，考察泛化能力）
    with open("robot_nav/eval_points.yaml") as file:  # 打开评估场景清单文件（上下文管理器保证用后自动关闭）
        points = yaml.safe_load(file)  # 安全解析 YAML（safe_load 不执行任意代码）
    robot_poses = points["robot"]["poses"]  # 取出所有场景的机器人初始位姿列表（起点坐标+朝向）
    robot_goals = points["robot"]["goals"]  # 取出对应的目标点列表——与 poses 按下标配对，一个起点配一个终点

    assert len(robot_poses) == len(  # 断言：起点数与目标数必须相等（不等说明配置文件写错了）
        robot_goals  # 目标点个数（断言比对的另一侧：起点数必须与它相等）
    ), "Number of robot poses do not equal the robot goals"  # 断言失败时抛出的错误信息

    print("..............................................")  # 打印分隔线
    print(f"Testing {len(robot_poses)} scenarios")  # 提示共测试多少个固定场景
    total_reward = 0.0  # 所有场景的奖励总和
    total_steps = 0  # 所有场景的总步数（用于算逐步平均奖励）
    col = 0  # 碰撞场景计数
    goals = 0  # 到达目标场景计数
    state_queue = deque(maxlen=5)  # 历史队列——注意：这里窗口长度是 5，而训练时是 10（GRU 按序列输入，窗口长度允许不一致，但这是仓里训练/测试口径的一个实际差异点，值得留意）
    for idx in range(len(robot_poses)):  # 逐场景循环（每轮一个起点-终点组合）
        fill_state = True  # 每个场景开始都要用首帧重新填充历史队列
        count = 0  # 本场景步数计数
        latest_scan, distance, cos, sin, collision, goal, a, reward = sim.reset(  # 按清单重置环境到指定场景
            robot_state=robot_poses[idx],  # 指定机器人初始位姿（本场景起点）
            robot_goal=robot_goals[idx],  # 指定本场景目标点
            random_obstacles=False,  # 关闭随机障碍：障碍布局固定 → 测试结果可复现
        )  # 取回场景初始观测
        done = False  # 场景结束标志
        while not done and count < max_steps:  # 未碰撞/未达标且未超 300 步就继续导航
            state, terminal = model.prepare_state(  # 原始观测 → 185 维归一化状态向量
                latest_scan, distance, cos, sin, collision, goal, a  # 当前原始观测分量
            )  # 与训练一致的加工逻辑，保证分布对齐
            if fill_state:  # 场景首步：填充历史队列
                state_queue.clear()  # 清掉上一场景残留帧
                for _ in range(5):  # 复制首帧 5 份（与队列容量 5 对应）
                    state_queue.append(state)  # 逐份垫底，GRU 从零记忆起步
                fill_state = False  # 本场景后续步不再填充
            state_queue.append(state)  # 滑窗追加当前帧 → (5, 185) 序列输入
            action = model.get_action(np.array(state_queue), False)  # 选动作；False = 不加探索噪声，执行确定性策略（测试看真实水平）
            a_in = [(action[0] + 1) / 4, action[1]]  # 动作映射：线速度 [-1,1]→[0,0.5] m/s（只前进），角速度原值
            latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 环境执行一步
                lin_velocity=a_in[0], ang_velocity=a_in[1]  # 物理速度指令
            )  # 取回下一观测与奖励
            total_reward += reward  # 累加到总奖励
            total_steps += 1  # 累加到总步数
            count += 1  # 本场景步数 +1
            if collision:  # 本步发生碰撞
                col += 1  # 碰撞场景数 +1（done 随即置 True，故每场景至多计 1 次）
            if goal:  # 本步到达目标
                goals += 1  # 到达场景数 +1
            done = collision or goal  # 碰撞或达标即本场景结束
    avg_step_reward = total_reward / total_steps  # 逐步平均奖励 = 总奖励 / 总步数（衡量"平均每走一步值多少分"）
    avg_reward = total_reward / len(robot_poses)  # 场景平均奖励 = 总奖励 / 场景数（衡量"每个场景整体表现"）
    avg_col = col / len(robot_poses)  # 碰撞率 = 碰撞场景数 / 场景数
    avg_goal = goals / len(robot_poses)  # 到达率 = 达标场景数 / 场景数（导航成功率的核心指标）
    print(f"Total Reward: {total_reward}")  # 打印总奖励
    print(f"Average Reward: {avg_reward}")  # 打印场景平均奖励
    print(f"Average Step Reward: {avg_step_reward}")  # 打印逐步平均奖励
    print(f"Average Collision rate: {avg_col}")  # 打印碰撞率（越低越好）
    print(f"Average Goal rate: {avg_goal}")  # 打印到达率（越高越好）
    print("..............................................")  # 结束分隔线
    model.writer.add_scalar("test/total_reward", total_reward, epoch)  # 总奖励写入 TensorBoard test/ 组曲线
    model.writer.add_scalar("test/avg_reward", avg_reward, epoch)  # 场景平均奖励曲线
    model.writer.add_scalar("test/avg_step_reward", avg_step_reward, epoch)  # 逐步平均奖励曲线
    model.writer.add_scalar("test/avg_col", avg_col, epoch)  # 碰撞率曲线
    model.writer.add_scalar("test/avg_goal", avg_goal, epoch)  # 到达率曲线——测试指标统一挂在 test/ 前缀下，与训练的 eval/ 区分


if __name__ == "__main__":  # 直接运行本文件时才执行
    main()  # 启动测试主流程
