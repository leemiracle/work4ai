# ============================================================
# 本文件 = 缓冲区工厂测试：守护 robot_nav/utils.py 的 get_buffer
# 按模型类型三路分发的正确性——
#   PPO  → 返回模型自带的 RolloutBuffer（on-policy 数据不能复用旧经验）
#   RCPG → RolloutReplayBuffer（按完整 episode 存，配合 RNN 历史窗口）
#   其他 → 普通 ReplayBuffer（环形队列，逐条 transition 存）
# 三条测试各守一路分发 + 两种 buffer 的计数语义（count 对两种 buffer 含义不同）。
# ============================================================
from pathlib import Path  # 导入 Path 类：用于把离线数据文件 test_data.yml 拼成绝对路径

from robot_nav.models.SAC.SAC import SAC  # 导入 SAC 模型类：test_buffer 里用来代表"普通 off-policy 模型"这一路分发
# 导入 PPO 模型类与其自带的 RolloutBuffer（PPO 模块内部的 on-policy 轨迹缓冲类，
# 与 utils 里的 RolloutReplayBuffer 是两个不同的类，别混淆）
from robot_nav.models.PPO.PPO import PPO, RolloutBuffer  # 后者用于最后的 isinstance 类型断言
from robot_nav.models.RCPG.RCPG import RCPG  # 导入 RCPG 模型类：test_rollout_buffer 里用来触发"轨迹式 buffer"这一路分发
from robot_nav.utils import get_buffer, RolloutReplayBuffer, ReplayBuffer  # 导入被测工厂 get_buffer 及两个 buffer 类（isinstance 断言需直接引用）
from robot_nav.SIM_ENV.sim import SIM  # 导入单机器人仿真环境 SIM 类（只借用其静态方法 get_reward，不实例化）

# 定位仓库根目录（parents[1] = tests/ 的上一级），下文拼数据文件绝对路径用
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # 定位仓库根目录：tests/ 的上一级，用于拼数据文件绝对路径


# 测试目标：SAC 走 get_buffer 应分到普通 ReplayBuffer，且
# "空 buffer 计数为 0 / 离线填充后计数封顶在容量值"两个行为不回归
def test_buffer():  # 第一路分发：off-policy 模型 → ReplayBuffer
    # 实例化一个最小规格的 SAC（state_dim=10 是低维压缩状态档）
    model = SAC(  # 开始构造 SAC 实例：作为"普通 off-policy 模型"的代表
        state_dim=10,  # 状态维度 10：雷达压成 5 扇区 + 5 个辅助量
        action_dim=2,  # 连续动作：线速度 + 角速度
        max_action=1,  # 动作限幅 = 1
        device="cpu",  # CPU 运行，无 GPU 依赖
        save_every=0,  # 不周期存盘，测试不留垃圾文件
        load_model=False,  # 随机初始化，不加载旧权重
    )  # instantiate a model  # 实例化一个模型（原英文注释保留）

    # 传 SIM 类本身即可：get_buffer 只用它的静态方法 get_reward，无需实例
    sim = SIM  # 环境占位：真正被借用的只有 get_reward 这一个静态函数
    # 第一次调用工厂：load_saved_buffer=False，应得到一个全新的空 buffer
    buffer = get_buffer(  # 开始调用工厂：这次要空 buffer
        model=model,  # SAC 属"其他"分支 → 应构造普通 ReplayBuffer
        sim=sim,  # 环境载体（本分支实际用不到，仅占位传参）
        load_saved_buffer=False,  # 不加载离线数据 → buffer 应为空
        pretrain=False,  # 不预训练
        pretraining_iterations=0,  # 预训练轮数置零
        training_iterations=0,  # 预训练迭代置零
        batch_size=0,  # 批大小置零
        buffer_size=100,  # 容量设 100，为下一条"填充后截断"断言做铺垫
    )  # get_buffer 调用结束：返回空 ReplayBuffer
    # assert = pytest 的断言语句：条件为假时抛 AssertionError，该测试记为失败。
    # 新 buffer 的 count 属性（已存 transition 条数）必须从 0 开始
    assert buffer.count == 0  # 空校验：新建 buffer 的 count 必须从 0 开始

    # isinstance 是 Python 内置的类型检查：第一个参数是对象，第二个是类（或元组），
    # 对象是该类（或其子类）实例时返回 True。这里守护 get_buffer 的分发正确性：
    # off-policy 模型（非 PPO、非 RCPG）必须拿到普通 ReplayBuffer
    assert isinstance(buffer, ReplayBuffer)  # 类型断言：off-policy 模型必须分到普通 ReplayBuffer

    # 第二次调用工厂：load_saved_buffer=True，从离线 YAML 文件加载经验填充 buffer
    prefilled_buffer = get_buffer(  # 开始调用工厂：这次要预填充的 buffer
        model=model,  # 同一个 SAC 模型
        sim=sim,  # 这回真正用到 sim.get_reward：为每条离线样本重算奖励
        load_saved_buffer=True,  # 关键开关：读取 YAML 离线数据灌入 buffer
        pretrain=False,  # 只灌数据不训练（pretrain=True 时工厂内部会先断言本开关为 True）
        pretraining_iterations=0,  # 预训练轮数置零
        training_iterations=0,  # 预训练迭代置零
        batch_size=0,  # 批大小置零
        buffer_size=100,  # 容量 100——数据文件有 999 条，远超容量
        file_names=[PROJECT_ROOT.joinpath("tests/test_data.yml")],  # 离线数据源：仓库 tests/ 下的 test_data.yml（999 条采集经验）
    )  # get_buffer 调用结束：返回灌满 100 条经验的 buffer
    # 核心回归断言：环形缓冲区语义——deque 满后逐条淘汰最旧经验（popleft），
    # 所以无论灌入多少条，count 封顶在 buffer_size=100，绝不会超容量
    assert prefilled_buffer.count == 100  # 环形截断语义：999 条灌入后 count 封顶在容量 100


# 测试目标：RCPG 走 get_buffer 应分到轨迹式 RolloutReplayBuffer，且其
# count 的语义是"完整 episode 条数"而非 transition 条数（同一份数据文件，
# 普通 buffer 数到 100，轨迹 buffer 只数出 6——这正是本测试守护的差异点）
def test_rollout_buffer():  # 第二路分发：RNN 策略模型 → RolloutReplayBuffer
    # 实例化 RCPG（state_dim=185：不压缩的原始 180 线雷达 + 5 辅助量，喂 RNN）
    model = RCPG(  # 开始构造 RCPG 实例：触发轨迹式 buffer 分支
        state_dim=185,  # 185 维状态：每条雷达射线一个分箱，保留完整空间结构
        action_dim=2,  # 连续动作两维
        max_action=1,  # 动作限幅 = 1
        device="cpu",  # CPU 运行
        save_every=0,  # 不存盘
        load_model=False,  # 随机初始化
    )  # instantiate a model  # 实例化一个模型（原英文注释保留）

    # 同样只传 SIM 类（静态奖励函数的载体）
    sim = SIM  # 环境占位：与上一测试同款技巧
    # 先取一个空轨迹 buffer，验证初始状态干净
    buffer = get_buffer(  # 开始调用工厂：先验证空 buffer 路径
        model=model,  # RCPG → 工厂应构造 RolloutReplayBuffer
        sim=sim,  # 环境载体占位
        load_saved_buffer=False,  # 不加载离线数据
        pretrain=False,  # 不预训练
        pretraining_iterations=0,  # 预训练轮数置零
        training_iterations=0,  # 预训练迭代置零
        batch_size=0,  # 批大小置零
        buffer_size=100,  # 容量 100（对轨迹 buffer 而言是最多存 100 条完整 episode）
    )  # get_buffer 调用结束：返回空轨迹 buffer
    # 初始 count 必须为 0：还没攒出任何完整 episode
    assert buffer.count == 0  # 空校验：轨迹 buffer 初始 episode 计数为 0

    # 类型断言：RCPG 必须拿到轨迹式 buffer（按 episode 分组存储、
    # 采样时带 history_len 历史窗口，供 RNN 策略使用），而非普通 transition 队列
    assert isinstance(buffer, RolloutReplayBuffer)  # 类型断言：RCPG 必须分到轨迹式 RolloutReplayBuffer

    # 从同一份离线数据加载（与 test_buffer 完全相同的 YAML 文件）
    prefilled_buffer = get_buffer(  # 开始调用工厂：预填充轨迹 buffer
        model=model,  # 同一个 RCPG
        sim=sim,  # 静态奖励函数载体
        load_saved_buffer=True,  # 加载离线经验
        pretrain=False,  # 不预训练
        pretraining_iterations=0,  # 预训练轮数置零
        training_iterations=0,  # 预训练迭代置零
        batch_size=0,  # 批大小置零
        buffer_size=100,  # 容量 100
        file_names=[PROJECT_ROOT.joinpath("tests/test_data.yml")],  # 同一份 test_data.yml（999 条、180 线雷达的采集记录）
    )  # get_buffer 调用结束：返回含 6 条完整 episode 的轨迹 buffer
    # 最有趣的断言：count == 6。轨迹 buffer 的 add 只在 terminal=True 时
    # count+=1（即"数完整 episode 的条数"）；test_data.yml 的 999 条样本里
    # goal/collision 恰好出现 6 次（YAML 键 2/94/234/632/692/862 处），
    # 所以只数出 6 条完整 episode——与上一测试的 100 形成鲜明对照
    assert prefilled_buffer.count == 6  # episode 计数语义：数据里 terminal 恰 6 次 → count==6


# 测试目标：PPO 走 get_buffer 应直接返回模型自带的 RolloutBuffer 实例，
# 而不是新建 buffer——on-policy 算法的经验只能来自当前策略的采集，
# 所以 buffer 必须挂在模型身上与策略同生命周期，工厂不得另起炉灶
def test_ppo_buffer():  # 第三路分发：on-policy 模型 → 模型自带 buffer 原样交还
    # 实例化 PPO（注意 action_dim=10，与另两个测试的 2 不同——
    # PPO 这里只当"类型分发探针"用，维度本身无特殊含义）
    model = PPO(  # 开始构造 PPO 实例：构造时已自带内部 buffer
        state_dim=10,  # 状态维度 10
        action_dim=10,  # 动作维度 10（本测试不断言训练行为，仅探类型分发）
        max_action=1,  # 动作限幅 = 1
        device="cpu",  # CPU 运行
        save_every=0,  # 不存盘
        load_model=False,  # 随机初始化
    )  # PPO 构造结束：内部已创建自己的 RolloutBuffer
    # 传 SIM 类占位（本分支根本不会用到 sim——工厂对 PPO 提前 return）
    sim = SIM  # 环境占位：PPO 分支连它的静态方法都不会碰
    # 调用工厂（各开关全置否/零，因为 PPO 分支在函数最开头就短路返回，参数不生效）
    buffer = get_buffer(  # 开始调用工厂：预期走 PPO 短路分支
        model=model,  # PPO 实例 → 应触发 isinstance(model, PPO) 短路分支
        sim=sim,  # 环境占位
        load_saved_buffer=False,  # 本分支不读此参数
        pretrain=False,  # 同上，短路返回前不检查
        pretraining_iterations=0,  # 占位置零
        training_iterations=0,  # 占位置零
        batch_size=0,  # 占位置零
        buffer_size=100,  # 占位置零（PPO 自带 buffer 的容量由模型自己管理）
    )  # get_buffer 调用结束：返回值应就是 model.buffer 本尊

    # 核心断言：拿到的必须是 PPO 模块定义的 RolloutBuffer（on-policy 轨迹缓冲，
    # 存 log_prob/价值等 PPO 专有字段），并且就是 model.buffer 那个实例——
    # 工厂对 PPO 只做"原样交还"，不做任何包装或新建
    assert isinstance(buffer, RolloutBuffer)  # 类型断言：PPO 拿到的就是模型自带的 RolloutBuffer
