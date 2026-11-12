from robot_nav.models.RCPG.RCPG import RCPG  # 导入 RCPG 模型类（Recurrent Convolutional Policy Gradient，循环策略梯度）——本仓自研的 actor-critic 算法，内部用 GRU 循环网络记忆历史，rnn_* 系脚本专为其服务（与 rl_* 系的 CNN/MLP 模型线相对）
from collections import deque  # 导入双端队列：用它维护"最近 history_len 帧状态"的滑动窗口，作为循环网络的时间维输入

import torch  # PyTorch：深度学习框架（张量、自动求导、GPU 加速、模型保存加载）
import numpy as np  # NumPy：数值计算库，这里主要用它把状态队列转成数组、生成探索噪声


from robot_nav.SIM_ENV.sim import SIM  # 仿真环境类：封装差速机器人运动学、激光雷达扫描、奖励计算、世界文件加载
from utils import get_buffer  # 工具函数：按模型类型构造经验回放池——对 RCPG 返回带历史序列的 RolloutReplayBuffer，对 TD3/CNNTD3 返回普通 ReplayBuffer


# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
# main —— 训练总入口（python rnn_train.py 直接运行）
# 职责：实例化 RCPG 模型 + 仿真环境 + 回放池，然后跑「epoch → episode → step」
#       三级训练循环：每个 step 采一个转移存回放池，每 2 个 episode 训练一轮，
#       每 70 个 episode 记一个 epoch 并调用 evaluate() 评估。
# 输入：args（当前未使用，预留命令行扩展）；输出：无返回值，模型 checkpoint
#       由 model.train 内部按 save_every 周期落盘到 robot_nav/models/RCPG/checkpoint/。
# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
def main(args=None):  # 训练主函数定义；args 形参暂未使用（保留接口）
    """Main training function"""  # 原 docstring：主训练函数（原样保留）
    action_dim = 2  # number of actions produced by the model ——动作维度=2，即输出 [线速度指令, 角速度指令] 两个分量
    max_action = 1  # maximum absolute value of output actions ——动作每个分量的绝对值上限为 1（网络末端用 tanh 输出，天然落在 [-1, 1]）
    state_dim = 185  # number of input values in the neural network (vector length of state input) ——状态向量长度 185：180 条激光射线（归一化后）+ 5 个标量（目标距离、朝向 cos、朝向 sin、上一步线速度、上一步角速度），见 RCPG.prepare_state 的拼接逻辑
    device = torch.device(  # 构造 PyTorch 计算设备对象（表达式跨下面两行）
        "cuda" if torch.cuda.is_available() else "cpu"  # 三元表达式：检测到 NVIDIA GPU（CUDA）就用显卡，否则退回 CPU 训练
    )  # using cuda if it is available, cpu otherwise ——device 赋值在此收尾：有 CUDA 用 CUDA，否则 CPU
    nr_eval_episodes = 10  # how many episodes to use to run evaluation ——每次评估跑 10 个回合取平均，降低单回合随机性
    max_epochs = 60  # max number of epochs ——最多训练 60 个 epoch（1 epoch = 70 个 episode）
    epoch = 0  # starting epoch number ——当前 epoch 计数从 0 开始
    episodes_per_epoch = 70  # how many episodes to run in single epoch ——每个 epoch 含 70 个 episode，跑满即触发一次评估
    episode = 0  # starting episode number ——当前 epoch 内的 episode 计数从 0 开始
    train_every_n = 2  # train and update network parameters every n episodes ——每收集 2 个 episode 的新经验就训练一轮（边采集边学习的节奏控制）
    training_iterations = 80  # how many batches to use for single training cycle ——每次训练从回放池采 80 个 batch 做梯度更新
    batch_size = 64  # batch size for each training iteration ——每个 batch 含 64 条转移样本（一次前向/反向传播的样本数）
    max_steps = 300  # maximum number of steps in single episode ——单个 episode 最多 300 步，超时强制截断（防止机器人在原地打转耗死）
    steps = 0  # starting step number ——当前 episode 内的步数计数器
    load_saved_buffer = False  # whether to load experiences from assets/data.yml ——是否从历史数据文件加载现成经验（False = 从零开始自己采集）
    pretrain = False  # whether to use the loaded experiences to pre-train the model (load_saved_buffer must be True) ——是否用加载的经验先做预训练（须先开 load_saved_buffer），类似" imitation 预热"
    history_len = 10  # 历史窗口长度：GRU 每次看最近 10 帧状态（这是 rnn 线区别于 rl 线的核心参数——rl 线只吃单帧）
    pretraining_iterations = (  # 预训练轮数赋值开始（数值在下一行，括号仅为换行书写）
        10  # number of training iterations to run during pre-training ——预训练阶段跑 10 轮迭代
    )  # pretraining_iterations 赋值在此收尾（=10）
    save_every = 10  # save the model every n training cycles ——每 10 次训练周期保存一次模型（在 model.train 内部按此参数触发 save）

    state_queue = deque(maxlen=history_len)  # 建立定长双端队列（容量 10）：append 超限自动挤出最旧帧——这就是"多历史帧喂进循环网络"的载体，np.array(state_queue) 形状为 (10, 185)

    model = RCPG(  # 实例化 RCPG 智能体（actor + twin critic + 各自 target 网络都会在内部建好）
        state_dim=state_dim,  # 状态输入维度 185
        action_dim=action_dim,  # 动作输出维度 2
        max_action=max_action,  # 动作幅值上限 1
        device=device,  # 计算设备（cuda/cpu）
        save_every=save_every,  # 训练内部每 10 个周期自动存 checkpoint
        load_model=False,  # 训练脚本从零开始，不加载已有权重（测试脚本才设 True）
        rnn="gru",  # 循环层类型选 GRU（门控循环单元：比普通 RNN 能更好地保存长程记忆、缓解梯度消失）
    )  # instantiate a model ——模型实例化完成

    sim = SIM()  # instantiate environment ——实例化仿真环境（默认世界文件；提供 step/reset，返回激光扫描、目标信息、奖励等 9 元组）
    replay_buffer = get_buffer(  # 构造经验回放池（按模型类型分发）
        model,  # 传入模型：识别出是 RCPG → 返回带 history_len 的 RolloutReplayBuffer
        sim,  # 传入环境：若启用预训练，可用 sim.get_reward 计算奖励
        load_saved_buffer,  # 是否从 YAML 数据文件加载经验（此处 False）
        pretrain,  # 是否先预训练（此处 False）
        pretraining_iterations,  # 预训练轮数
        training_iterations,  # 正式训练每轮迭代次数
        batch_size,  # batch 大小
    )  # 返回容量 50000 的回放池实例

    latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 环境先"空走一步"拿初始观测（动作全零）；返回：激光扫描、目标距离、朝向余弦/正弦、是否碰撞、是否到达、上步动作、奖励
        lin_velocity=0.0, ang_velocity=0.0  # 零线速度 + 零角速度：只取观测不真动
    )  # get the initial step state ——初始观测到手，训练主循环的输入
    fill_state = True  # 队列待填充标志：episode 刚开始时需要用首帧把历史队列填满（见下方 if fill_state 分支）
    while epoch < max_epochs:  # train until max_epochs is reached ——外层主循环：按 step 粒度推进，直到凑满 60 个 epoch
        state, terminal = model.prepare_state(  # 把环境原始 9 元组加工成网络吃的 185 维归一化状态向量（inf→7、/7、/10 等归一化都在模型侧做）
            latest_scan, distance, cos, sin, collision, goal, a  # 传入上一观测的原始分量
        )  # get state a state representation from returned data from the environment ——得到当前状态 state 与终止标志 terminal（碰撞/达标=1）
        if fill_state:  # 若是新 episode 的第一步（或环境刚 reset）
            state_queue.clear()  # 清空历史队列：防止上一 episode 的旧帧泄漏进本 episode 的记忆
            for _ in range(history_len):  # 把首帧状态复制 10 份
                state_queue.append(state)  # 逐份填入队列——用"假历史"垫底，GRU 从零记忆起步
            fill_state = False  # 填充完成，本 episode 后续步直接滑窗即可
        state_queue.append(state)  # 滑窗式追加当前帧（队列满 10 帧后最旧帧自动被挤出）——循环网络的时序输入就绪

        action = model.get_action(  # 智能体根据最近 10 帧状态选动作
            np.array(state_queue), True  # 队列转成 (10, 185) 数组；True = add_noise，在策略输出上加 N(0, 0.2) 高斯噪声做探索（训练期需要试错，评估期改 False 走确定性策略）
        )  # get an action from the model ——得到 [-1, 1] 范围内的 2 维动作
        a_in = [  # 把网络动作映射成仿真器可执行的物理指令
            (action[0] + 1) / 4,  # 线速度：[-1, 1] 线性映射到 [0, 0.5] m/s——机器人只前进不后退（初学者注意：这不是 clip 而是仿射变换）
            action[1],  # 角速度：直接取 [-1, 1] 原值（rad/s 量级），正为左转负为右转
        ]  # clip linear velocity to [0, 0.5] m/s range ——物理动作 a_in 组装完成

        latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 把动作交给环境执行一步，取回下一个观测与奖励
            lin_velocity=a_in[0], ang_velocity=a_in[1]  # 用映射后的物理速度驱动差速机器人
        )  # get data from the environment ——得到 s' 的原始观测与即时奖励 r
        next_state, terminal = model.prepare_state(  # 对新观测做同样的状态加工，得到 s'
            latest_scan, distance, cos, sin, collision, goal, a  # 注意 a 传的是刚执行的动作（状态里含上步动作，帮网络感知自身动力学）
        )  # get a next state representation ——下一状态与终止标志就绪
        replay_buffer.add(  # 把四/五元组转移存进回放池
            state, action, reward, terminal, next_state  # (s, a, r, terminal, s')；RCPG 的池会连带维护历史序列语义
        )  # add experience to the replay buffer ——一条经验入池，供后续随机采样打散时间相关性

        if (  # 终止判断开始（条件跨两行）
            terminal or steps == max_steps  # 碰撞/到达目标（terminal=1），或步数超上限被截断——两种情况都要 reset
        ):  # reset environment of terminal stat ereached, or max_steps were taken ——注意：超时截断时 terminal 未必为 1，属于 time-limit 截断而非环境终止
            fill_state = True  # 标记需要重新填充历史队列（下个 episode 首步触发）
            latest_scan, distance, cos, sin, collision, goal, a, reward = sim.reset()  # 重置环境：机器人/障碍回到初始布局，取回新 episode 的初始观测
            episode += 1  # episode 计数 +1（本回合正式结束）
            if episode % train_every_n == 0:  # 每凑满 2 个 episode 触发一次训练（对 2 取模为 0）
                model.train(  # 从回放池随机采样做梯度更新（actor + twin critic + 软更新 target 网络）
                    replay_buffer=replay_buffer,  # 数据源：经验回放池
                    iterations=training_iterations,  # 本轮训练迭代 80 次
                    batch_size=batch_size,  # 每次采 64 条样本
                )  # train the model and update its parameters ——参数更新完成（内部每 save_every=10 轮自动保存 checkpoint）

            steps = 0  # 步数计数器清零，为下个 episode 做准备
        else:  # 本步未终止，episode 继续
            steps += 1  # 步数计数 +1

        if (  # epoch 判断开始（条件跨两行）
            episode + 1  # 当前 episode 计数（+1 后再取模，使第 70 个回合结束时恰好整除触发）
        ) % episodes_per_epoch == 0:  # if epoch is concluded, run evaluation ——episode+1 能被 70 整除 = 本 epoch 的 70 个回合全部跑完
            episode = 0  # episode 计数清零（下个 epoch 重新数）
            epoch += 1  # epoch 计数 +1
            evaluate(  # 跑一轮无噪声评估，看当前策略真实水平
                model,  # 待评估的 RCPG 模型
                epoch,  # 当前 epoch 号（用作 TensorBoard 的横轴 x）
                sim,  # 仿真环境（评估与训练共用同一实例）
                history_len,  # 历史窗口长度（评估时同样要维护 10 帧队列）
                max_steps,  # 单回合步数上限 300
                eval_episodes=nr_eval_episodes,  # 评估回合数 10
            )  # 评估函数调用收尾


# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
# evaluate —— 阶段性评估函数（训练过程中被 main 周期性调用）
# 职责：用「确定性策略」（不加探索噪声）跑 eval_episodes 个回合，统计平均奖励、
#       碰撞率、到达目标率，并写入 TensorBoard 的 eval/* 曲线。
# 输入：model（模型）、epoch（轮次号）、sim（环境）、history_len（历史帧数）、
#       max_steps（步数上限）、eval_episodes（评估回合数）；输出：无返回值。
# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
def evaluate(model, epoch, sim, history_len, max_steps, eval_episodes=10):  # 评估函数定义：与训练共用 prepare_state/get_action，但探索开关关闭
    print("..............................................")  # 打印分隔线，便于在训练日志中定位评估块
    print(f"Epoch {epoch}. Evaluating scenarios")  # 提示当前是第几个 epoch 的评估
    avg_reward = 0.0  # 奖励累加器（先累加所有回合的总奖励，最后除以回合数得平均）
    col = 0  # 碰撞计数器
    goals = 0  # 到达目标计数器
    state_queue = deque(maxlen=history_len)  # 评估专用的历史队列（与训练队列分离，容量同为 10）
    for _ in range(eval_episodes):  # 依次跑 10 个评估回合
        fill_state = True  # 每回合开始都要重新填充历史队列
        count = 0  # 本回合步数计数
        latest_scan, distance, cos, sin, collision, goal, a, reward = sim.reset()  # 重置环境取初始观测（评估回合起点随机）
        done = False  # 回合结束标志
        while not done and count < max_steps:  # 内层循环：未终止且未超 300 步
            state, terminal = model.prepare_state(  # 原始观测 → 185 维状态向量
                latest_scan, distance, cos, sin, collision, goal, a  # 传入当前原始观测
            )  # 与训练完全一致的状态加工，保证评估口径一致
            if fill_state:  # 回合首步：先填满历史队列
                state_queue.clear()  # 清掉上一回合的残留帧
                for _ in range(history_len):  # 复制首帧 10 份
                    state_queue.append(state)  # 逐份垫底
                fill_state = False  # 本回合不再重复填充
            state_queue.append(state)  # 滑窗追加当前帧
            action = model.get_action(np.array(state_queue), False)  # 关键差异：第二参 False = 不加噪声，执行确定性策略，考察真实水平
            a_in = [(action[0] + 1) / 4, action[1]]  # 与训练相同的动作映射：线速度→[0, 0.5] m/s，角速度原值
            latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 环境执行一步
                lin_velocity=a_in[0], ang_velocity=a_in[1]  # 物理速度指令
            )  # 取回下一观测与奖励
            avg_reward += reward  # 累加奖励（10 个回合一起累加）
            count += 1  # 步数 +1
            if collision:  # 若本步发生碰撞
                col += 1  # 碰撞计数 +1（done 随即置 True，故每回合至多记 1 次——col 实际是"发生碰撞的回合数"）
            if goal:  # 若本步到达目标
                goals += 1  # 到达计数 +1（同理每回合至多 1 次）
            done = collision or goal  # 碰撞或达标都算回合结束
    avg_reward /= eval_episodes  # 平均回合奖励 = 总累加 / 10
    avg_col = col / eval_episodes  # 碰撞率 = 碰撞回合数 / 总回合数
    avg_goal = goals / eval_episodes  # 到达率 = 达标回合数 / 总回合数
    print(f"Average Reward: {avg_reward}")  # 打印平均回合奖励（训练是否在变好主要看它）
    print(f"Average Collision rate: {avg_col}")  # 打印碰撞率（越低越安全）
    print(f"Average Goal rate: {avg_goal}")  # 打印到达率（导航成功的核心指标，越高越好）
    print("..............................................")  # 评估块结束分隔线
    model.writer.add_scalar("eval/avg_reward", avg_reward, epoch)  # 把平均奖励写入 TensorBoard 曲线（writer 是模型内部的 SummaryWriter），横轴为 epoch
    model.writer.add_scalar("eval/avg_col", avg_col, epoch)  # 碰撞率曲线 eval/avg_col
    model.writer.add_scalar("eval/avg_goal", avg_goal, epoch)  # 到达率曲线 eval/avg_goal——三条曲线合看即可判断"学得快不快、稳不稳"


if __name__ == "__main__":  # 只有直接运行本文件（而非被 import）时才执行下面的调用
    main()  # 启动训练主流程
