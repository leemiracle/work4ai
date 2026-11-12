# ============================================================
# 本文件 = 仿真环境层测试：守护 SIM（单机器人）与 MARL_SIM（多机器人）
# 两个环境封装的运动学正确性（step 前进量）、观测规格（雷达 180 线、
# 障碍物数量）、reset 随机化行为，以及 cossin 三角工具函数。
# 与模型层测试不同，这里全部用 assert 做精确断言（浮点用 np.isclose 近似比较）。
# ============================================================
import os  # 导入 os：读取环境变量 CI，用于判断当前是否跑在 GitHub Actions 上

# 导入 pytest：本文件用到 skipif 条件跳过标记
import pytest  # 测试框架：这里主要消费它的 mark.skipif
# 导入 torch：构造多机测试的通信占位张量
import torch  # 导入 PyTorch：构造多机测试的通信占位张量

from robot_nav.SIM_ENV.marl_sim import MARL_SIM  # 导入多机器人仿真环境 MARL_SIM（test_marl_sim 的被测对象）
from robot_nav.SIM_ENV.sim import SIM  # 导入单机器人仿真环境 SIM（test_sim / test_sincos 的被测对象）
import numpy as np  # 导入 numpy：浮点近似比较 np.isclose 与不等判断 np.not_equal 都来自它

# 定义一个可复用的"条件跳过"标记：pytest.mark.skipif 会在条件为真时把
# 挂了该标记的测试标记为 SKIPPED（既不算通过也不算失败，报告中灰色显示），
# 与失败（FAILED）不同——它表示"这个环境跑不了，主动放弃"。
# 这里条件是环境变量 CI == "true"（GitHub Actions 会自动注入该变量），
# 即 CI 上跳过，因为依赖 IRSim 渲染/显示的用例在无显示器的 CI 容器里会崩
skip_on_ci = pytest.mark.skipif(  # 开始构造条件跳过标记：存成变量便于多个测试复用
    os.getenv("CI") == "true", reason="Skipped on CI (GitHub Actions)"  # 跳过条件：CI 环境变量为 "true"；reason 是跳过原因说明（原样保留）
)  # skipif 标记构造结束


# 测试目标：单机环境三件事——①step(1,0) 让机器人沿朝向精确前进 1 个单位；
# ②观测规格（雷达 180 线、世界 7 个障碍物）不漂移；③reset 随机化初始位姿
@skip_on_ci  # 挂上条件跳过标记：CI 环境下整个用例跳过（依赖仿真世界文件与渲染后端）
def test_sim():  # 单机环境测试入口：无参数，环境自建自测
    # 实例化单机环境：世界文件路径以 / 开头，由 IRSim 内部解析定位；
    # disable_plotting=True 关渲染 = 无头模式跑测试
    sim = SIM("/tests/test_world.yaml", disable_plotting=True)  # 实例化单机环境：路径由 IRSim 解析；无头模式
    # 取机器人初始状态（[x, y, theta] 位姿），作为 step 前的基准值
    robot_state = sim.env.get_robot_state()  # 记录 step 前的机器人位姿 [x, y, theta] 作基准
    # 执行一步：线速度=1、角速度=0（直行不转向）——step 返回完整观测元组，
    # 但这里只关心它顺利执行，返回值存进 state 供下面查雷达线数
    state = sim.step(1, 0)  # 直行一步（线速度 1、角速度 0），返回完整观测元组
    # 再取一次状态：与 step 前对比，验证运动学效果
    next_robot_state = sim.env.get_robot_state()  # step 后再取位姿，与基准对比
    # np.isclose 是浮点近似相等（默认相对容差 1e-8）——浮点运算有舍入误差，
    # 永远不要用 == 比较浮点。断言"旧 x == 新 x - 1"：即线速度 1 走一步，
    # 机器人应沿 x 方向精确前进 1 个单位（角速度 0 时朝向不变）
    assert np.isclose(robot_state[0], next_robot_state[0] - 1)  # 运动学锚点：x 应精确 +1（线速度 1 走一步）
    # 这行写的是 robot_state[1] 与自身比较——恒为真，断言强度为零，
    # 疑似笔误（本意应是 next_robot_state[1]，即"角速度 0 → y 不变"；
    # 若写对了也会通过，因为直行确实不改变 y）。如实保留原代码，不替作者修 bug
    assert np.isclose(robot_state[1], robot_state[1])  # 疑似笔误：与自身比较恒真（本意应为 next_robot_state[1]）

    # state[0] 是雷达扫描 latest_scan：必须恒为 180 线——这是观测规格的
    # 回归防线（180 线 = 185 维状态模型里"每射线一箱"的前提，改动会被立刻抓到）
    assert len(state[0]) == 180  # 观测规格：雷达必须恒为 180 线
    # 世界文件 test_world.yaml 定义了 7 个障碍物：环境加载正确的规格锚点
    assert len(sim.env.obstacle_list) == 7  # 世界规格：test_world.yaml 定义了 7 个障碍物

    # reset 并指定随机化障碍物：random_obstacle_ids=[1..6] 表示 id 1-6 的
    # 障碍物位置随机重摆（id 0 不动），机器人的初始位姿也随之变化
    sim.reset(random_obstacle_ids=[i + 1 for i in range(6)])  # 重摆 id 1-6 障碍物并随机化机器人初始位姿
    # 取随机化后的新初始位姿
    new_robot_state = sim.env.get_robot_state()  # 取随机化后的新初始位姿
    # np.not_equal 判断不相等：reset 后 x 必须与上次不同——守护
    # "reset 真的做了随机化"（若随机化失效、位姿不变，这条断言立刻失败）
    assert np.not_equal(robot_state[0], new_robot_state[0])  # 守护随机化：reset 后 x 必须改变
    # 同理：y 坐标也必须被随机化改变
    assert np.not_equal(robot_state[1], new_robot_state[1])  # 守护随机化：reset 后 y 必须改变


# 测试目标：多机环境同款三件事（无 CI 跳过标记——不依赖渲染显示，
# 且 MARL_SIM 全程 disable_plotting，CI 上也能跑）：
# ①三台机器人各自直行前进 1 单位；②多机世界无障碍物；③reset 随机化
def test_marl_sim():  # 多机环境测试入口：不挂跳过标记，CI 上也执行
    # 实例化多机环境（3 台机器人的世界文件），无头模式
    sim = MARL_SIM("/tests/test_marl_world.yaml", disable_plotting=True)  # 实例化 3 机器人多机环境（无头模式）
    # 记录每台机器人 step 前的 [x, y]（state 前 two 个分量；
    # 列表推导按 robot_list 顺序取前 3 台）
    robot_state = [sim.env.robot_list[i].state[:2] for i in range(3)]  # 记录每台 step 前的 [x, y]（state 前两个分量）
    # 构造 (3, num_robots-1) 的全 0 通信占位张量：connections 表示机器人间
    # 成对连接 logits（去掉自连列），当前仿真逻辑不消费它，全 0 即安全占位
    connections = torch.tensor(  # 开始构造张量：由嵌套列表字面量转换
        [[0.0 for _ in range(sim.num_robots - 1)] for _ in range(3)]  # 3 行 × (num_robots-1) 列全 0 二维列表，外层 3 对应 3 台机器人
    )  # torch.tensor 调用结束：得到 float 类型通信占位张量

    # 三台机器人各发 [1, 0]（直行不转向）执行一步；返回值用 _ 丢弃
    # （多机 step 返回 10 元组，本测试只关心机器人实际动了没有）
    _ = sim.step([[1, 0], [1, 0], [1, 0]], connections)  # 三台各直行一步；返回的 10 元组用 _ 丢弃
    # 记录 step 后每台机器人的 [x, y]，与 step 前逐台对比
    next_robot_state = [sim.env.robot_list[i].state[:2] for i in range(3)]  # step 后每台的 [x, y]，与 step 前逐台对比
    # 逐台验证运动学：每台 x 都应精确 +1（线速度 1、角速度 0 的直行语义）
    for j in range(3):  # 遍历 3 台机器人逐台断言
        assert np.isclose(robot_state[j][0], next_robot_state[j][0] - 1)  # 每台 x 都应精确 +1（直行运动学）
        # y 不变：角速度 0 直行不产生横向位移
        assert np.isclose(robot_state[j][1], robot_state[j][1])  # 同款自比较恒真（与 49 行同模式的疑似笔误）

    # 多机世界文件没有定义障碍物：obstacle_list 必须为空（环境加载规格锚点）
    assert len(sim.env.obstacle_list) == 0  # 多机世界无障碍物：环境加载规格锚点

    # 无参 reset：随机化机器人初始位姿（多机版不重摆障碍物，因为没有）
    sim.reset()  # 无参 reset：随机化机器人初始位姿
    # 取 reset 后每台机器人的新 [x, y]
    new_robot_state = [sim.env.robot_list[i].state[:2] for i in range(3)]  # reset 后每台的新 [x, y]
    # 逐台断言 x、y 都被随机化改变——守护多机 reset 的随机化不失效
    for j in range(3):  # 遍历 3 台机器人逐台断言
        assert np.not_equal(robot_state[j][0], new_robot_state[j][0])  # 守护多机随机化：x 必须改变
        assert np.not_equal(robot_state[j][1], new_robot_state[j][1])  # 守护多机随机化：y 必须改变


# 测试目标：SIM.cossin 三角工具函数——计算机器人朝向向量与目标向量
# 夹角的 (cos, sin)。用一对正交向量造出 90 度夹角的已知答案做验证
@skip_on_ci  # CI 跳过：本用例构造 SIM 时没传 disable_plotting（会初始化渲染），CI 无显示器会崩
def test_sincos():  # 三角工具函数测试入口：已知答案法验证
    # 注意这里没有 disable_plotting=True（与前两个用例不同），
    # 代价是初始化时尝试开渲染窗口——正是它需要挂 CI 跳过标记的原因
    sim = SIM("/tests/test_world.yaml")  # 注意：这里没传 disable_plotting（正是需要 CI 跳过的原因）
    # 输入两个正交向量：朝向 [1,0]（x 正方向）、目标方向 [0,1]（y 正方向），
    # 夹角应为 90 度 → cos=0、sin=1（cossin 返回夹角的余弦和正弦标量）
    cos, sin = sim.cossin([1, 0], [0, 1])  # 正交向量对 → 90 度夹角的已知答案验证
    # 90 度夹角的余弦 ≈ 0（浮点上 cos(pi/2) 是 1e-17 量级的尘埃，isclose 容差内视为 0）
    assert np.isclose(cos, 0)  # 90 度夹角余弦 ≈ 0（浮点尘埃在容差内）
    # 90 度夹角的正弦 = 1：方向约定（从朝向转到目标向量的有向角）的回归锚点
    assert np.isclose(sin, 1)  # 90 度夹角正弦 = 1（有向角方向的回归锚点）
