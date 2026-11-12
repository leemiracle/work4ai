from robot_nav.models.CNNTD3.CNNTD3 import CNNTD3  # 导入 CNNTD3 模型类：CNN（3 层一维卷积直接卷激光扫描序列）+ TD3（Twin Delayed DDPG，双 Q 网络取小值 + 延迟策略更新 + 目标策略平滑）——rl_* 系脚本服务的"普通（非循环）"模型线之一

import torch  # PyTorch：张量运算、自动求导、设备管理
import numpy as np  # NumPy：数组化状态、动作容器
from robot_nav.SIM_ENV.sim import SIM  # 仿真环境：step/reset 返回激光扫描、目标信息、奖励等 9 元组
from utils import get_buffer  # 工具函数：按模型类型构造回放池——CNNTD3 不是 RCPG/PPO，会拿到普通 ReplayBuffer（不需要历史序列）


# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
# main —— CNNTD3 训练总入口（python rl_train.py 直接运行）
# 职责：实例化 CNNTD3 + 环境 + 普通回放池，跑「epoch → episode → step」训练循环。
#       与 rnn_train.py 的结构性差异：没有 state_queue 历史队列——CNNTD3 吃"单帧"
#       185 维状态（卷积在扫描的空间维提特征，而非用 GRU 在时间维记历史）。
# 输入：args（未使用）；输出：无返回值，checkpoint 由 model.train 内部按
#       save_every=5 周期落盘到 robot_nav/models/CNNTD3/checkpoint/。
# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
def main(args=None):  # 训练主函数定义；args 形参暂未使用（预留）
    """Main training function"""  # 原 docstring：主训练函数（原样保留）
    action_dim = 2  # number of actions produced by the model ——动作维度=2：[线速度, 角速度]
    max_action = 1  # maximum absolute value of output actions ——动作幅值上限 1（tanh 输出范围）
    state_dim = 185  # number of input values in the neural network (vector length of state input) ——状态维度 185 = 180 条激光射线 + 5 个标量，与 RCPG 相同；区别在 CNN 对 180 条扫描做卷积、MLP 对全部 185 维做全连接
    device = torch.device(  # 构造计算设备（表达式跨两行）
        "cuda" if torch.cuda.is_available() else "cpu"  # 有 GPU 用 GPU，否则 CPU
    )  # using cuda if it is available, cpu otherwise ——设备选择收尾
    nr_eval_episodes = 10  # how many episodes to use to run evaluation ——每轮评估 10 个回合
    max_epochs = 60  # max number of epochs ——最多 60 个 epoch（1 epoch = 70 episode）
    epoch = 0  # starting epoch number ——epoch 计数从 0 起
    episodes_per_epoch = 70  # how many episodes to run in single epoch ——每 epoch 70 个回合
    episode = 0  # starting episode number ——epoch 内 episode 计数从 0 起
    train_every_n = 2  # train and update network parameters every n episodes ——每 2 个 episode 训练一轮
    training_iterations = 80  # how many batches to use for single training cycle ——每轮训练 80 次迭代
    batch_size = 64  # batch size for each training iteration ——batch 大小 64
    max_steps = 300  # maximum number of steps in single episode ——单回合 300 步上限
    steps = 0  # starting step number ——回合内步数计数器
    load_saved_buffer = False  # whether to load experiences from assets/data.yml ——不从 YAML 加载现成经验，从零采集
    pretrain = False  # whether to use the loaded experiences to pre-train the model (load_saved_buffer must be True) ——不做预训练（若开启须同时开 load_saved_buffer）
    pretraining_iterations = (  # 预训练轮数赋值开始（数值在下一行）
        10  # number of training iterations to run during pre-training ——预训练迭代 10 轮
    )  # 预训练轮数赋值收尾（=10）
    save_every = 5  # save the model every n training cycles ——每 5 个训练周期存一次 checkpoint（比 RCPG 的 10 更勤）

    model = CNNTD3(  # 实例化 CNNTD3 智能体（CNN actor + twin critic + target 网络内部建好）
        state_dim=state_dim,  # 状态维度 185
        action_dim=action_dim,  # 动作维度 2
        max_action=max_action,  # 动作上限 1
        device=device,  # 计算设备
        save_every=save_every,  # 训练内部每 5 周期自动保存
        load_model=False,  # 从零训练，不加载旧权重
        model_name="CNNTD3",  # 模型名（决定 checkpoint 文件名与 TensorWriter 注释标签）
    )  # instantiate a model ——模型实例化完成

    sim = SIM(  # 实例化训练环境（参数跨两行）
        world_file="worlds/robot_world.yaml", disable_plotting=False  # 指定训练世界文件；False = 开启实时绘图（可在窗口里看机器人跑，调试友好但略耗性能）
    )  # instantiate environment ——训练环境就绪
    replay_buffer = get_buffer(  # 构造经验回放池（CNNTD3 → 普通 ReplayBuffer，存单帧转移）
        model,  # 模型实例（用于类型分发）
        sim,  # 环境（预训练时可用其 get_reward）
        load_saved_buffer,  # 是否加载 YAML 经验（False）
        pretrain,  # 是否预训练（False）
        pretraining_iterations,  # 预训练轮数
        training_iterations,  # 训练迭代数
        batch_size,  # batch 大小
    )  # 回放池实例返回

    latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 环境空走一步取初始观测（零动作）
        lin_velocity=0.0, ang_velocity=0.0  # 零线速度 + 零角速度
    )  # get the initial step state ——初始观测到手

    while epoch < max_epochs:  # train until max_epochs is reached ——step 粒度主循环，直到 60 个 epoch
        state, terminal = model.prepare_state(  # 原始观测 → 185 维归一化状态（与 RCPG 同构的拼接：180 扫描 + 5 标量）
            latest_scan, distance, cos, sin, collision, goal, a  # 当前原始观测分量
        )  # get state a state representation from returned data from the environment ——单帧状态直接用，无历史队列（这是与 rnn 线的本质差异）

        action = model.get_action(np.array(state), True)  # get an action from the model ——单帧状态选动作；True = 加探索噪声（高斯噪声，训练期试错必需）
        a_in = [  # 网络动作 → 物理指令
            (action[0] + 1) / 4,  # 线速度 [-1,1] → [0, 0.5] m/s（仿射映射，只前进）
            action[1],  # 角速度原值 [-1,1]
        ]  # clip linear velocity to [0, 0.5] m/s range ——物理动作组装完成

        latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 环境执行一步
            lin_velocity=a_in[0], ang_velocity=a_in[1]  # 物理速度指令
        )  # get data from the environment ——下一观测 s' 与奖励 r
        next_state, terminal = model.prepare_state(  # 新观测加工成 s'
            latest_scan, distance, cos, sin, collision, goal, a  # 含刚执行的动作 a
        )  # get a next state representation ——下一状态就绪
        replay_buffer.add(  # 转移入池
            state, action, reward, terminal, next_state  # 五元组 (s, a, r, terminal, s')，供随机采样训练
        )  # add experience to the replay buffer ——一条经验入池

        if (  # 终止判断开始（条件跨两行）
            terminal or steps == max_steps  # 碰撞/达标，或步数超 300 被截断
        ):  # reset environment of terminal stat ereached, or max_steps were taken ——超时截断时 terminal 不一定是 1（time-limit 截断，非环境自然终止）
            latest_scan, distance, cos, sin, collision, goal, a, reward = sim.reset()  # 重置环境，取新回合初始观测（rnn 线还要置 fill_state=True 清队列，这里无此负担）
            episode += 1  # episode 计数 +1
            if episode % train_every_n == 0:  # 每 2 个 episode 触发训练
                model.train(  # 采样训练：TD3 三件套都在这里——双 Q 取小抑制高估、目标动作加裁剪噪声（policy_noise=0.2, noise_clip=0.5）做目标策略平滑、策略网络延迟更新
                    replay_buffer=replay_buffer,  # 数据源回放池
                    iterations=training_iterations,  # 迭代 80 次
                    batch_size=batch_size,  # batch 64——每次迭代从回放池采 64 条转移样本
                )  # train the model and update its parameters ——参数更新完成（每 save_every=5 轮自动存 checkpoint）

            steps = 0  # 步数清零
        else:  # 回合继续
            steps += 1  # 步数 +1

        if (  # epoch 判断开始（条件跨两行）
            episode + 1  # 当前 episode 计数（+1 后再取模，使第 70 个回合结束时恰好整除触发）
        ) % episodes_per_epoch == 0:  # if epoch is concluded, run evaluation ——70 个回合跑满即一个 epoch 结束
            episode = 0  # episode 清零重新计
            epoch += 1  # epoch +1——轮次号递增（TensorBoard 评估曲线的横轴）
            evaluate(model, epoch, sim, eval_episodes=nr_eval_episodes)  # 无噪声评估 10 回合并写 TensorBoard（无需传 history_len——没有历史队列）


# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
# evaluate —— CNNTD3 阶段性评估函数（训练中周期调用）
# 职责：确定性策略（无探索噪声）跑 eval_episodes 个回合，统计平均奖励、碰撞率、
#       到达率，写 TensorBoard eval/* 曲线。与 rnn_train.evaluate 的差异：
#       无历史队列维护，且内层步数上限硬编码 501（比训练的 300 更宽）。
# 输入：model、epoch、sim、eval_episodes；输出：无返回值。
# ==================== 教学讲解块（装饰边框行，内容见中间各行） ====================
def evaluate(model, epoch, sim, eval_episodes=10):  # 评估函数定义
    print("..............................................")  # 分隔线
    print(f"Epoch {epoch}. Evaluating scenarios")  # 提示当前 epoch 评估
    avg_reward = 0.0  # 奖励累加器
    col = 0  # 碰撞计数
    goals = 0  # 到达计数
    for _ in range(eval_episodes):  # 跑 10 个评估回合
        count = 0  # 回合步数计数
        latest_scan, distance, cos, sin, collision, goal, a, reward = sim.reset()  # 重置环境取初始观测
        done = False  # 回合结束标志
        while not done and count < 501:  # 未终止且步数 < 501——注意这里是硬编码 501（约 500 步），比训练的 max_steps=300 宽松，评估给策略更多时间
            state, terminal = model.prepare_state(  # 观测 → 185 维状态
                latest_scan, distance, cos, sin, collision, goal, a  # 当前原始观测
            )  # 单帧状态，无队列操作
            action = model.get_action(np.array(state), False)  # False = 确定性策略，无探索噪声
            a_in = [(action[0] + 1) / 4, action[1]]  # 同款动作映射
            latest_scan, distance, cos, sin, collision, goal, a, reward = sim.step(  # 环境执行一步
                lin_velocity=a_in[0], ang_velocity=a_in[1]  # 物理指令
            )  # 取回下一观测与奖励
            avg_reward += reward  # 累加奖励
            count += 1  # 步数 +1
            if collision:  # 发生碰撞
                col += 1  # 碰撞 +1（done 即退出，每回合至多 1 次）
            if goal:  # 到达目标
                goals += 1  # 到达 +1
            done = collision or goal  # 碰撞或达标即回合结束
    avg_reward /= eval_episodes  # 平均回合奖励
    avg_col = col / eval_episodes  # 碰撞率
    avg_goal = goals / eval_episodes  # 到达率
    print(f"Average Reward: {avg_reward}")  # 打印平均奖励
    print(f"Average Collision rate: {avg_col}")  # 打印碰撞率
    print(f"Average Goal rate: {avg_goal}")  # 打印到达率
    print("..............................................")  # 分隔线
    model.writer.add_scalar("eval/avg_reward", avg_reward, epoch)  # TensorBoard 平均奖励曲线
    model.writer.add_scalar("eval/avg_col", avg_col, epoch)  # 碰撞率曲线
    model.writer.add_scalar("eval/avg_goal", avg_goal, epoch)  # 到达率曲线


if __name__ == "__main__":  # 直接运行本文件时才执行
    main()  # 启动训练主流程
