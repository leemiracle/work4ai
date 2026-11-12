# ============================================================================
# 模块: sim_env.py —— 仿真环境包的抽象基类（接口契约层）
# 职责: 用 Python 的 ABC(抽象基类) 规定所有仿真环境子类必须实现
#       step / reset / get_reward 三个方法, 并提供一个共用的数学工具
#       cossin(计算两个 2D 向量夹角的余弦与正弦)。
# 被谁调用: sim.py 的 SIM(单机器人环境) 与 marl_sim.py 的 MARL_SIM
#       (多机器人环境) 都继承本类; 训练脚本 rl_train.py / marl_train.py
#       只通过这两个子类与环境交互, 本文件本身不参与仿真计算。
# RL 背景速览(初学者版): 本仓库遵循 gym 风格的环境接口——
#   * reset(): 开一局新 episode(回合), 随机布置机器人/障碍/目标,
#     返回初始观测;
#   * step(action): 把智能体输出的动作(如 [线速度 m/s, 角速度 rad/s])
#     作用到仿真里, 推进一个控制周期(本仓 YAML 实证为 0.3 秒/步),
#     返回新观测与奖励、终止标志等;
#   * observation(观测): 智能体能"看到"的传感器数据(激光测距、
#     到目标的距离与方位等); action(动作): 智能体的控制输出。
# ============================================================================
from abc import ABC, abstractmethod  # ABC=抽象基类机制; abstractmethod=强制子类覆写的装饰器
import numpy as np  # 数值计算库: 用于向量范数(np.linalg.norm)与点积(np.dot)


# ---- 抽象基类 SIM_ENV: 只定"必须有哪些方法", 不写具体仿真逻辑 ----
# 教学档(为什么用 ABC): 子类若忘记实现任一抽象方法, 在实例化那一刻
#   就会抛 TypeError——把接口缺失错误从"训练中途莫名崩溃"提前到
#   "程序启动即暴露", 这是环境工程里最廉价的防御性设计。
class SIM_ENV(ABC):
    # 声明 step 为抽象方法: 每个子类必须给出自己的版本
    @abstractmethod
    # step 语义: 输入动作 -> 环境推进一拍 -> 返回(观测, 奖励, 终止...)元组;
    # 单机版返回 8 元组(laser, distance, cos, sin, collision, goal, action, reward),
    # 多机版返回 10 元组(见各子类实现)
    def step(self):
        # 抽象方法本体只抛"未实现"异常; 真正逻辑由 SIM / MARL_SIM 提供
        raise NotImplementedError("step method must be implemented by subclass.")  # 父类兜底: 防止子类漏写

    # 声明 reset 为抽象方法: 每个子类必须覆写
    @abstractmethod
    # reset 语义: episode 的第 0 步——重摆机器人初始位姿/随机障碍/
    # 随机目标, 然后用零动作 step 一次, 取得初始观测供策略网络起步
    def reset(self):
        raise NotImplementedError("reset method must be implemented by subclass.")  # 同上, 兜底异常

    # 静态方法装饰器: 表明这是不访问 self/实例状态的纯数学函数
    @staticmethod
    # cossin: 求两个 2D 向量夹角 θ 的 (cos θ, sin θ)
    # 输入: vec1, vec2 —— 两个二维向量(本仓的典型用法: vec1=机器人
    #       朝向单位向量 (cosθ_r, sinθ_r), vec2=指向目标的方向向量);
    # 输出: (cos, sin) 元组, 无量纲, 均在 [-1, 1]
    # 被谁调用: sim.py 与 marl_sim.py 的 step/reset 中, 用来把"目标在
    #       我哪个方向"编码成对神经网络友好的两个数。
    def cossin(vec1, vec2):
        """
        Compute the cosine and sine of the angle between two 2D vectors.

        Args:
            vec1 (list): First 2D vector.
            vec2 (list): Second 2D vector.

        Returns:
            (tuple): (cosine, sine) of the angle between the vectors.
        """
        # ↓ 以下 4 行是实际计算; 上方 docstring 按规范原样保留, 不加注释
        vec1 = vec1 / np.linalg.norm(vec1)  # 把 vec1 归一化为单位向量(模长 1); norm=√(x²+y²), 即欧氏长度(米单位被约掉)
        vec2 = vec2 / np.linalg.norm(vec2)  # vec2 同样归一化——两边都变成纯方向, 消除"距离远近"对夹角计算的干扰
        cos = np.dot(vec1, vec2)  # 单位向量点积 = cos θ ∈ [-1,1](无量纲); 1=正对目标, -1=背对目标
        sin = vec1[0] * vec2[1] - vec1[1] * vec2[0]  # 二维叉积(标量) = |v1||v2|·sin θ, 归一化后即 sin θ; 符号=转向方向(正表示目标在左手边/逆时针)
        return cos, sin  # 返回 (cos θ, sin θ): 两者联立可无歧义还原 [-π,π] 全周期方位角(单用 cos 分不清左右)

    # 双装饰器: staticmethod(纯函数) + abstractmethod(子类必须实现)
    # get_reward 是 RL 训练信号的唯一来源——它定义"什么是好行为"
    @staticmethod  # 静态方法: 奖励计算不依赖实例状态, 便于离线复现与单元测试
    @abstractmethod  # 同时标记为抽象方法: 子类必须实现自己的奖励函数
    # get_reward: 依据(是否到达/是否碰撞/动作/传感器读数)计算本步
    # 标量奖励 r; 子类的具体分项设计见 sim.py(单机)与 marl_sim.py(多机)
    def get_reward():
        raise NotImplementedError("get_reward method must be implemented by subclass.")  # 兜底: 强制子类给出奖励函数
