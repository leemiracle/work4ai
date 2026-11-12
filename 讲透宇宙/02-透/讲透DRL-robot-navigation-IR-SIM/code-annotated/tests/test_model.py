# ============================================================
# 本文件 = 模型层冒烟测试（smoke test）：守护 6 个 RL 算法实现
# （RCPG/CNNTD3/TD3/SAC/DDPG/marlTD3）的"实例化→灌数据→训练"全链路。
# 特点：全程无 assert——pytest 里测试函数只要不抛异常就算通过，
# 因此这批测试守护的是"前后向传播、优化器、缓冲区对接不崩溃"这条回归防线。
# ============================================================
from pathlib import Path  # 导入 Path 类：跨平台路径拼接，下面用它定位离线数据文件 test_data.yml

import torch  # 导入 PyTorch：深度学习框架；本文件在多机测试里还直接用它构造通信占位张量

from robot_nav.SIM_ENV.marl_sim import MARL_SIM  # 导入多机器人仿真环境类（test_marl_models 的被测环境，基于 IRSim）
from robot_nav.models.RCPG.RCPG import RCPG  # 导入 RCPG（Recurrent Policy Gradient）：RNN 策略模型，状态带历史序列
from robot_nav.models.TD3.TD3 import TD3  # 导入 TD3（Twin Delayed DDPG）：连续动作 off-policy 算法
from robot_nav.models.CNNTD3.CNNTD3 import CNNTD3  # 导入 CNNTD3：用 CNN 直接吃原始 180 线激光雷达的 TD3 变体
from robot_nav.models.SAC.SAC import SAC  # 导入 SAC（Soft Actor-Critic）：最大熵 off-policy 算法
from robot_nav.models.DDPG.DDPG import DDPG  # 导入 DDPG：TD3 的前身算法（确定性策略梯度）
# 导入缓冲区工厂 get_buffer：内部按模型类型三路分发——PPO 返回自带 buffer、
# RCPG 返回 RolloutReplayBuffer（按完整 episode 存）、其余返回普通 ReplayBuffer
from robot_nav.utils import get_buffer  # 工厂函数：测试模型与训练数据之间的桥梁
from robot_nav.SIM_ENV.sim import SIM  # 导入单机器人仿真环境 SIM（注意导入的是类本身，测试里也不实例化它）
from robot_nav.models.MARL.marlTD3.marlTD3 import TD3 as marlTD3  # 导入多机器人版 TD3 并重命名为 marlTD3，避免与上面单机版 TD3 同名冲突
import pytest  # 导入 pytest 测试框架，本文件只用到它的参数化装饰器 parametrize

# 计算项目根目录：__file__ 是本测试文件路径，resolve 转绝对路径，
# parents[1] 取上上级（parents[0]=tests/，parents[1]=仓库根）——之后用它
# 拼出 test_data.yml 的绝对路径，保证从任何工作目录跑 pytest 都能找到数据文件
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # 定位仓库根目录：本文件上上级（tests/ 的上一级），用于拼数据文件绝对路径


# pytest.mark.parametrize 是"参数化"装饰器：把下方参数表里的每个元组
# 作为一组实参注入测试函数，自动展开成多个独立测试用例（运行时显示为
# test_models[RCPG-185] 这样的名字）。相比复制粘贴 5 个测试函数，好处是
# 失败时能一眼定位是哪个模型坏了，且新增模型只需加一行参数。
@pytest.mark.parametrize(  # 参数化装饰器开始：下方参数表将逐组注入 test_models
    "model, state_dim",  # 声明参数名（字符串形式），与测试函数形参一一对应
    [  # 参数表：每个元组 = 一次独立的测试运行
        # state_dim 决定状态向量构造：prepare_state 里雷达分箱数 = state_dim - 5，
        # 185-5=180 恰好每条射线一箱（不压缩，保留完整空间信息给 CNN/RNN）
        (RCPG, 185),  # RNN 策略模型：吃不压缩的原始雷达序列
        (CNNTD3, 185),  # CNN 版：同样 185 维，原始雷达直接喂卷积网络
        (TD3, 10),  # 经典 TD3：10 维 = 雷达压缩成 5 个扇区最小值 + 5 个辅助量
        (SAC, 10),  # SAC：与 TD3 同规格的低维状态输入
        (DDPG, 10),  # DDPG：与 TD3 同规格的低维状态输入
    ],  # 参数表结束：共 5 组，即 5 个独立测试用例
)  # parametrize 装饰器收尾：参数表定义完毕，下方即被装饰的测试函数
# 测试目标：5 个单机模型各自完成"构建→离线数据填充 buffer→跑 2 步训练"不崩溃
def test_models(model, state_dim):  # 冒烟测试入口：形参由 parametrize 注入（模型类 + 状态维度）
    # 用参数注入的类和维度实例化待测模型（每个用例独立建一个全新模型）
    test_model = model(  # 开始构造模型实例：类本身来自参数表
        state_dim=state_dim,  # 状态维度：185（原始雷达）或 10（压缩雷达），见上表注释
        action_dim=2,  # 动作维度 = 2：线速度 + 角速度（连续动作空间）
        max_action=1,  # 动作幅值上界 = 1：策略网络 tanh 输出的限幅系数
        device="cpu",  # 强制 CPU 运行：测试不依赖 GPU，任何环境（含 CI）都能跑
        save_every=0,  # 每 N 步存盘设为 0 = 不落盘，避免测试运行污染仓库文件
        load_model=False,  # 不加载旧权重：从随机初始化开始，保证测试自包含可复现
    )  # instantiate a model  # 实例化一个模型（原英文注释保留）

    # 注意这里传的是 SIM 类本身而不是实例！get_buffer 内部只用到 sim.get_reward，
    # 而它是静态方法（@staticmethod，无需实例即可调用），所以传类完全合法——
    # 这是测试代码"能不初始化就不初始化"的省资源技巧（跳过整个仿真环境构建）
    sim = SIM  # 赋值：SIM 类本身（注意不是实例）

    # 调用缓冲区工厂，得到预填充了离线经验的回放缓冲区
    prefilled_buffer = get_buffer(  # 开始调用工厂：返回灌好数据的 buffer
        model=test_model,  # 待测模型：get_buffer 按其类型决定 buffer 种类（非 PPO/RCPG → ReplayBuffer）
        sim=sim,  # 仿真环境：只被借用其 get_reward 静态方法来重算奖励
        load_saved_buffer=True,  # 关键开关：从 YAML 离线数据文件加载经验填充 buffer
        pretrain=False,  # 不执行预训练（只灌数据，不在这步练模型）
        pretraining_iterations=0,  # 预训练轮数 = 0（与上开关配合，双重保险不误触发）
        training_iterations=0,  # 每轮预训练的迭代步数 = 0
        batch_size=0,  # 预训练批大小 = 0（本测试稍后自己显式调 train）
        buffer_size=100,  # 缓冲区容量 100：离线文件有 999 条，环形 buffer 截断保留最后 100 条
        file_names=[PROJECT_ROOT.joinpath("tests/test_data.yml")],  # 离线数据文件（tests/ 下 999 条采集经验），绝对路径保证从任意目录启动都能找到
    )  # get_buffer 调用结束：返回的已是含 100 条经验的 buffer

    # 冒烟级训练：只跑 2 次迭代、批大小 8——验证前向/反向/优化器整条链路能通，
    # 不验证（也不可能验证）学习效果。若重构改坏了网络维度或 train 接口，这里立刻抛异常
    test_model.train(  # 开始训练调用：本测试的核心动作
        replay_buffer=prefilled_buffer,  # 用刚灌好离线数据的 buffer 供采样
        iterations=2,  # 训练 2 个 iteration：足够覆盖一次完整梯度更新即可
        batch_size=8,  # 每批采样 8 条经验（buffer 里有 100 条，充足）
    )  # train 调用结束：不抛异常即本用例通过


# 第二组参数化：专门守护 use_max_bound=True 这条非默认代码路径
# （TD3.py 训练循环里的 if self.use_max_bound: 分支——对 Q 值施加保守上界
# get_max_bound，用 ReLU 惩罚超出上界的 Q 估计，属于安全/保守 RL 机制）。
# 名单只有 3 个模型：SAC 与 RCPG 的构造函数没有该参数，天然不在此防线内
@pytest.mark.parametrize(  # 第二组参数化装饰器：同样机制展开 3 个用例
    "model, state_dim",  # 参数名同上：模型类 + 状态维度
    [  # 参数表：只列支持 use_max_bound 的三个模型
        (CNNTD3, 185),  # CNN 版 TD3 + Q 上界分支
        (TD3, 10),  # 经典 TD3 + Q 上界分支
        (DDPG, 10),  # DDPG + Q 上界分支
    ],  # 参数表结束：3 组用例
)  # parametrize 装饰器收尾：与第一组同机制
# 测试目标：与 test_models 相同的冒烟流程，但多打开 use_max_bound 开关，
# 守护"保守 Q 上界"分支的代码不被重构破坏（分支覆盖意义上的回归测试）
def test_max_bound_models(model, state_dim):  # 形参同样由 parametrize 注入
    # 实例化流程与 test_models 完全一致，仅多传一个 use_max_bound=True
    test_model = model(  # 开始构造模型实例：这次带保守上界开关
        state_dim=state_dim,  # 状态维度：185 或 10，含义同上一测试
        action_dim=2,  # 连续动作：线速度 + 角速度
        max_action=1,  # 动作限幅 = 1
        device="cpu",  # CPU 运行，无 GPU 依赖
        save_every=0,  # 不周期存盘
        load_model=False,  # 随机初始化，不读旧权重
        use_max_bound=True,  # 本测试的核心开关：训练时启用 Q 值保守上界约束
    )  # instantiate a model  # 实例化一个模型（原英文注释保留）

    # 同样只借用 SIM 类的静态奖励函数，不构建仿真实例
    sim = SIM  # 赋值：与上一测试同款——传类不传实例

    # 与上文完全相同的离线数据预填充流程（两条测试共用同一份 999 条经验的 YAML）
    prefilled_buffer = get_buffer(  # 开始调用工厂：流程与上一测试相同
        model=test_model,  # 带着刚实例化的模型来分发 buffer 类型
        sim=sim,  # 提供静态奖励函数 get_reward 的载体
        load_saved_buffer=True,  # 从离线 YAML 加载经验
        pretrain=False,  # 不在 get_buffer 内部触发预训练
        pretraining_iterations=0,  # 预训练轮数置零
        training_iterations=0,  # 预训练迭代步数置零
        batch_size=0,  # 预训练批大小置零
        buffer_size=100,  # 容量 100（环形截断语义同上）
        file_names=[PROJECT_ROOT.joinpath("tests/test_data.yml")],  # 同一份测试数据文件的绝对路径
    )  # get_buffer 调用结束：返回预填充 buffer

    # 冒烟训练：跑通 use_max_bound 分支下的完整梯度更新（含 get_max_bound 计算与 ReLU 惩罚）
    test_model.train(  # 开始训练：这次会走进 Q 上界惩罚分支
        replay_buffer=prefilled_buffer,  # 采样源：预填充的离线经验
        iterations=2,  # 2 个 iteration 足以进入被测分支
        batch_size=8,  # 每批 8 条经验
    )  # train 调用结束：不抛异常即通过


# 多机版冒烟测试（不参数化，单一用例）：MARL_SIM + marlTD3 的在线采集→训练链路。
# 与前两个测试的根本区别：没有现成的多机离线数据文件，必须在仿真里现采 10 步经验
def test_marl_models():  # 多机冒烟测试入口：无参数，环境与模型都在函数内自建
    # 实例化多机器人仿真环境；路径以 / 开头由 IRSim 内部解析（相对其包数据目录定位），
    # disable_plotting=True 关闭渲染窗口 = 无头模式（测试环境通常没有显示器）
    sim = MARL_SIM("/tests/test_marl_world.yaml", disable_plotting=True)  # 实例化多机环境：这是本文件唯一真正实例化的仿真
    # 实例化多机版 TD3；注意维度与单机版不同：state_dim=11 是多机观测的压缩维度，
    # num_robots 由仿真环境动态传入（机器人数量与 YAML 世界文件绑定）
    test_model = marlTD3(  # 开始构造多机版 TD3 实例
        state_dim=11,  # 多机状态向量维度（不同于单机的 10/185 两档）
        action_dim=2,  # 每台机器人仍是线速度 + 角速度两个连续动作
        max_action=1,  # 动作限幅 = 1
        num_robots=sim.num_robots,  # 机器人台数：从仿真环境读取，保持与世界文件一致
        device="cpu",  # CPU 运行
        save_every=0,  # 不存盘
        load_model=False,  # 随机初始化
    )  # instantiate a model  # 实例化一个模型（原英文注释保留）

    # 多机没有离线数据可加载：load_saved_buffer=False，得到一个空 buffer，
    # 后面手动与环境交互 10 步来填充它（这就是"在线采集"最小版）
    replay_buffer = get_buffer(  # 开始调用工厂：这次要一个空 buffer
        model=test_model,  # 多机模型：非 PPO/RCPG，分发到普通 ReplayBuffer
        sim=sim,  # 这次传的是真正的 MARL_SIM 实例（下面要用它 step）
        load_saved_buffer=False,  # 不加载离线文件（也没有多机版数据文件）
        pretrain=False,  # 不预训练
        pretraining_iterations=0,  # 预训练轮数置零
        training_iterations=0,  # 预训练迭代置零
        batch_size=0,  # 预训练批大小置零
        buffer_size=100,  # 容量 100，够放 10 步采集
    )  # get_buffer 调用结束：返回空 buffer 等待在线填充

    # 采集循环：与环境交互 10 步，每步存一条多机联合经验
    for _ in range(10):  # 循环 10 次：每次采集一条五元组经验
        # 构造通信占位张量：形状 (3, num_robots-1) 的全 0 矩阵。
        # 按源码 docstring，connections 是"机器人间成对连接的 logits"（去掉自连列），
        # 且当前仿真逻辑并不消费它——传全 0 张量即为最安全的占位值
        connections = torch.tensor(  # 开始构造张量：由嵌套列表字面量转换
            [[0.0 for _ in range(sim.num_robots - 1)] for _ in range(3)]  # 3 行 × (num_robots-1) 列的全 0 二维列表，外层 3 对应测试世界的 3 台机器人
        )  # torch.tensor 调用结束：得到 float 类型的通信占位张量
        # 调用多机环境的 step：给每台机器人发 [0,0]（原地不动）的动作，
        # 返回 10 元组（全部是"每机一个元素"的列表）：位姿/距离/朝向余弦/朝向正弦/
        # 碰撞标志/到达标志/动作回显/奖励/当前位置/目标位置
        (  # 多行解包开始：把 step 返回的 10 元组拆成命名变量
            poses,  # 各机位姿 [x, y, theta] 列表
            distance,  # 各机到目标的距离列表
            cos,  # 各机朝向与目标向量夹角的余弦列表
            sin,  # 各机朝向与目标向量夹角的正弦列表
            collision,  # 各机碰撞标志列表
            goal,  # 各机到达目标标志列表（到达即刻换新随机目标）
            a,  # 输入动作的回显列表
            reward,  # 各机奖励列表（由 get_reward 按多机奖励函数计算）
            positions,  # 各机当前位置 [x, y] 列表
            goal_positions,  # 各机当前目标坐标 [x, y] 列表
        ) = sim.step([[0, 0] for _ in range(sim.num_robots)], connections)  # 执行一步仿真：每台发 [0,0] 原地动作 + 通信占位张量
        # 用模型自带的 prepare_state 把原始多机观测压缩成 11 维网络输入 + 终止标志；
        # 注意多机版签名与单机版不同（喂的是 poses 列表和 goal_positions 列表）
        state, terminal = test_model.prepare_state(  # 开始状态构造：返回 (状态向量, 终止标志)
            poses, distance, cos, sin, collision, a, goal_positions  # 六类原始观测一次喂入，函数内部拼成 11 维状态
        )  # prepare_state 调用结束
        # 存入回放缓冲区：(state, action, reward, terminal, next_state) 五元组；
        # 这里 next_state 直接复用 state——因为动作全 0 机器人没动，状态不变，
        # 是测试里构造"合法但最简"transition 的常用简化
        replay_buffer.add(  # 开始写入 buffer
            state, [[0, 0] for _ in range(sim.num_robots)], reward, terminal, state  # 五元组：状态、全零动作、奖励、终止标志、下一状态（复用 state）
        )  # add 调用结束：本条经验已入队

    # 冒烟训练：10 条经验 > 批大小 8，刚好够采样，验证多机版前向/反向不崩溃
    test_model.train(  # 开始多机版训练
        replay_buffer=replay_buffer,  # 用刚在线采集填充的 buffer
        iterations=2,  # 2 个 iteration
        batch_size=8,  # 每批 8 条（buffer 里有 10 条，够采）
    )  # train 调用结束：不抛异常即通过
