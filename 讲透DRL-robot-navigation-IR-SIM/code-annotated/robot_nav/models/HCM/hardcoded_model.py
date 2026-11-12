# ============================================================================ #
# 【文件】HCM（Hard-Coded Model，硬编码模型）——纯手写规则的避障导航控制器。
# 定位：它不是学习方法！没有任何可训练参数（train/save/load 全是占位 pass）。
# 两大用途：①作 DRL 的基线/对照——与 SAC 同接口，同一训练脚本可无缝替换两个模型；
# ②类 docstring 自述"故意次优"：多撞多试，专门给 DRL 预训练收集含碰撞的经验样本
# （prepare_state 把样本落盘到 data.yml，供后续预训练加载）。
# ============================================================================ #
from math import atan2  # 反正切（按象限定角）：由 sin/cos 还原朝向角 ∈ (−π,π]

import numpy as np  # NumPy：LIDAR 分箱、inf 掩码、标量转换
from numpy import clip  # numpy 截断函数：把值压进 [min,max]（对 list 元素也生效）
# TensorBoard 写入器：__init__ 里创建但本类后续从未使用（与 SAC 接口对齐的占位）
from torch.utils.tensorboard import SummaryWriter
import yaml  # YAML 读写：把采集的样本追加落盘


# ============================== 类：HCM ============================== #
# 职责：硬编码控制律导航器——零可训练参数；与 SAC 模型类同接口（train/save/load/
# prepare_state/get_action），训练脚本可不改一行地互换两个模型做对照实验。
# 控制律（get_action 实证）：默认朝目标方位角转向；近处有障碍（激光<1.5m）时改
# "避障优先"——转向从最近障碍束向空侧偏移出的方向。输出 [lin_vel, rot_vel]：
# rot_vel=目标角截断到 [−1,1]；lin_vel=−|rot_vel|/2 恒 ≤0，调用方 rl_train.py 用
# (a0+1)/4 重映射成 [0,0.5] m/s 前进速度（越要转弯走得越慢）。
class HCM(object):  # 显式继承 object（Py2 风格）；不继承 nn.Module——它不是神经网络
    """
    A class representing a Hard-Coded model (HCM) for a robot's navigation system.

    This class contains methods for generating actions based on the robot's state, preparing state
    representations, training (placeholder method), saving/loading models, and logging experiences.
    The method is suboptimal in order to collect collisions for pre-training of DRL models.

    Attributes:
        max_action (float): The maximum possible action value.
        state_dim (int): The dimension of the state representation.
        writer (SummaryWriter): The writer for logging purposes.
        iterator (int): A counter for tracking sample addition.
        save_samples (bool): Whether to save the samples to a file.
        max_added_samples (int): Maximum number of samples to be added to the saved file.
        file_location (str): The file location for saving samples.
    """

    # 构造：只记录配置与计数器，无任何权重参数。
    def __init__(  # 构造函数：参数较多，按 PEP8 拆多行书写
        self,  # 实例自身
        state_dim,  # 状态维度 = LIDAR 分箱数 + 5（distance/cos/sin/上一步动作 2 维）
        max_action,  # 动作绝对值上界（本类仅保存不使用——控制律输出天然有界）
        save_samples,  # 是否把经验样本落盘
        max_added_samples=10_000,  # 落盘样本条数上限（默认 1 万；数字下划线是 Python 合法写法）
        file_location="robot_nav/assets/data.yml",  # 样本 YAML 文件路径（追加写）
    ):  # 形参列表结束
        """
        Initialize the HCM class with the provided configuration.

        Args:
            state_dim (int): The dimension of the state space.
            max_action (float): The maximum possible action value.
            save_samples (bool): Whether to save samples to a file.
            max_added_samples (int): The maximum number of samples to save.
            file_location (str): The file path for saving samples.
        """
        self.max_action = max_action  # 保存动作上界（未参与任何计算，接口对齐用）
        self.state_dim = state_dim  # 保存状态维度：get_action/prepare_state 都靠它切状态向量
        self.writer = SummaryWriter()  # 建 TensorBoard 写入器（本类未再使用；实例化会在 ./runs/ 建目录）
        self.iterator = 0  # 样本计数器：既当样本编号又配合 max_added_samples 限流
        self.save_samples = save_samples  # 落盘开关
        self.max_added_samples = max_added_samples  # 落盘上限
        self.file_location = file_location  # 落盘路径

    # 核心控制律：由状态直接算动作——无网络、无梯度、零延迟，也不学习。
    # 输入：state 一维状态向量（np.array 或 list），布局=prepare_state 的产物：
    #   [LIDAR 分箱 ×(state_dim−5), distance, cos, sin, 上一步 lin, 上一步 rot]；
    #   add_noise 形参存在但未被使用（与 SAC 的探索参数保持签名一致）。
    # 输出：[lin_vel, rot_vel]——rot_vel 是目标转角截断；lin_vel=−|rot_vel|/2 ≤0。
    def get_action(self, state, add_noise):  # 与 SAC 同名同签名，训练脚本可无缝换模型
        """
        Compute the action to be taken based on the current state of the robot.

        Args:
            state (list): The current state of the robot, including LIDAR scan, distance,
                          and other relevant features.
            add_noise (bool): Whether to add noise to the action for exploration.

        Returns:
            (list): The computed action [linear velocity, angular velocity].
        """
        sin = state[-3]  # 倒数第 3 个元素：朝向角的 sin（目标方位角正弦分量）
        cos = state[-4]  # 倒数第 4 个元素：朝向角的 cos
        angle = atan2(sin, cos)  # 由 (cos,sin) 还原带符号目标方位角 ∈ (−π,π]——默认转向指令
        laser_nr = self.state_dim - 5  # 激光分箱数：状态前 state_dim−5 个元素全是激光距离
        limit = 1.5  # 避障距离阈值（米）：相关激光束近于它就触发避障

        # 避障触发判断：取激光第 4 箱到倒数第 5 箱（跳过两端各 4 箱侧向束）的最小距离
        if min(state[4 : self.state_dim - 9]) < limit:  # 小于 1.5m ⇒ 近处有障碍，进入避障分支
            state = state.tolist()  # np.array → Python list：为了下一步用 list.index 精确定位
            # 找最近障碍束：min 取全部激光箱的最短距离（=最近障碍），index 定位其束序号（首次出现）
            idx = state[:laser_nr].index(min(state[:laser_nr]))
            if idx > laser_nr / 2:  # 障碍在序号大的一半（一侧）？
                sign = -1  # 是 ⇒ 往序号小的方向（另一侧）偏
            else:  # 障碍在序号小的一半
                sign = 1  # 否则往序号大的方向偏

            # 目标束 = 最近障碍束往空侧偏移 5×(1.5/最近距离) 箱：障碍越近偏得越狠；截断到 [0, laser_nr]
            idx = clip(idx + sign * 5 * (limit / min(state[:laser_nr])), 0, laser_nr)

            # 束序号线性映射成角度：0→−1.57、laser_nr→+1.57（前方 ±90° 扇区），
            # 覆盖掉上面的"朝目标"角——避障优先于导航
            angle = ((3.14 / (laser_nr)) * idx) - 1.57

        rot_vel = clip(angle, -1.0, 1.0)  # 转向指令=目标角截断到 [−1,1]（角度量级直接当角速度用）
        lin_vel = -abs(rot_vel / 2)  # 线速度=−|rot_vel|/2 ∈ [−0.5,0]：越要大转向越慢，走直线才最快
        return [lin_vel, rot_vel]  # 返回 [线速度, 角速度]；训练脚本会对 lin 再做 (a+1)/4 重映射

    # 【译注】"training cycle"——对硬编码模型而言没有可训练对象：
    # train/save/load 三个方法全为占位（pass），只求与 SAC 类接口一致，让训练脚本无感切换。
    # training cycle
    def train(  # 占位训练方法（与 SAC.train 同签名同默认超参，保证统一调用）
        self,  # 实例自身
        replay_buffer,  # 经验回放缓冲区：存 (s,a,r,s') 供采样（本方法不使用）
        iterations,  # 训练迭代数（本方法不使用）
        batch_size,  # 批大小（本方法不使用）
        discount=0.99999,  # 折扣因子 γ：未来奖励的折扣率（本方法不使用）
        tau=0.005,  # 目标网络软更新系数（本方法不使用）
        policy_noise=0.2,  # 策略目标平滑噪声，TD3 系参数（本方法不使用）
        noise_clip=0.5,  # 噪声截断幅度（本方法不使用）
        policy_freq=2,  # 策略更新频率（本方法不使用）
    ):  # 形参列表结束
        """
        Placeholder method for training the hybrid control model.

        Args:
            replay_buffer (object): The replay buffer containing experiences.
            iterations (int): The number of training iterations.
            batch_size (int): The batch size for training.
            discount (float): The discount factor for future rewards.
            tau (float): The soft update parameter for target networks.
            policy_noise (float): The noise added to actions during training.
            noise_clip (float): The clipping value for action noise.
            policy_freq (int): The frequency at which to update the policy.

        Note:
            This method is a placeholder and currently does nothing.
        """
        pass  # 什么都不做：规则已硬编码在 get_action 里，无需训练

    # 占位方法：无模型权重可存（SAC 版本在此保存网络状态字典，这里 pass 保接口一致）。
    def save(self, filename, directory):  # 占位：与 SAC.save 同签名
        """
        Placeholder method to save the current model state to a file.

        Args:
            filename (str): The name of the file where the model will be saved.
            directory (str): The directory where the file will be stored.

        Note:
            This method is a placeholder and currently does nothing.
        """
        pass  # 无可保存内容

    # 占位方法：无权重可载——全部"知识"都写在 get_action 的规则里。
    def load(self, filename, directory):  # 占位：与 SAC.load 同签名
        """
        Placeholder method to load a model state from a file.

        Args:
            filename (str): The name of the file to load the model from.
            directory (str): The directory where the model file is stored.

        Note:
            This method is a placeholder and currently does nothing.
        """
        pass  # 无可加载内容

    # 状态构造器 + 数据采集器（本类真正干活的方法，与 SAC.prepare_state 同签名）。
    # 输入：环境一步返回的原始量（LIDAR 序列/目标距离/朝向 cos,sin/碰撞与到达标志/动作）。
    # 输出：state 长度=state_dim 的列表 = [LIDAR 分箱最小值×(state_dim−5)] + [distance,
    #   cos, sin, action0, action1]，以及 terminal（碰撞或到达=1）；布局与 get_action
    #   的索引约定（state[-3]=sin、state[-4]=cos）严格对应。
    def prepare_state(self, latest_scan, distance, cos, sin, collision, goal, action):  # 与 SAC 同名同签名
        """
        Prepare the state representation for the model based on the current environment.

        Args:
            latest_scan (list): The LIDAR scan data.
            distance (float): The distance to the goal.
            cos (float): The cosine of the robot's orientation angle.
            sin (float): The sine of the robot's orientation angle.
            collision (bool): Whether a collision occurred.
            goal (bool): Whether the goal has been reached.
            action (list): The action taken by the robot, [linear velocity, angular velocity].

        Returns:
            (tuple): A tuple containing the prepared state and a terminal flag (1 if terminal state, 0 otherwise).
        """
        latest_scan = np.array(latest_scan)  # LIDAR 原始序列转 np 数组，便于向量化处理

        inf_mask = np.isinf(latest_scan)  # 找出"打到无穷远"的束（没测到障碍时仿真器常返回 inf）
        latest_scan[inf_mask] = 7.0  # inf 替换为 7.0 米：一个有限的"很远"，下游计算才吃得下

        max_bins = self.state_dim - 5  # 目标激光箱数：状态向量里留给激光的槽位数
        bin_size = int(np.ceil(len(latest_scan) / max_bins))  # 每箱束数 = 原始束数/箱数，向上取整

        # 【译注】以下为"分箱降维"：把几百束激光按顺序切进 max_bins 个组，每组只留最小值
        # （最短距离=最危险方向）——既压掉状态维度，又保留安全相关信息。
        # Initialize the list to store the minimum values of each bin
        min_values = []  # 存每箱最短距离的列表

        # Loop through the data and create bins
        for i in range(0, len(latest_scan), bin_size):  # 按箱宽步进遍历整条扫描序列
            # Get the current bin
            bin = latest_scan[i : i + min(bin_size, len(latest_scan) - i)]  # 当前箱切片（末箱可能不满：宽度取箱宽与剩余束数的较小值）
            # Find the minimum value in the current bin and append it to the min_values list
            min_values.append(min(bin))  # 记本箱最短距离——代表该扇区的最近障碍
        # 拼装完整状态：激光箱(×max_bins) + [distance, cos, sin] + [上一步 lin, 上一步 rot]
        state = min_values + [distance, cos, sin] + [action[0], action[1]]

        assert len(state) == self.state_dim  # 维度自检：与构造参数不一致说明状态布局错了
        terminal = 1 if collision or goal else 0  # 终止标志：碰撞或到达目标都算回合结束

        self.iterator += 1  # 计数器+1：为下一条样本编号
        if self.save_samples and self.iterator < self.max_added_samples:  # 开了落盘且未超上限才写
            # 恒等表达式：不管是不是 list 都原样返回（两分支相同——疑似未写完的类型转换遗留）
            action = action if type(action) is list else action
            action = [float(a) for a in action]  # 动作逐元素转 float（YAML 只收基本类型）
            sample = {  # 组装单条样本字典：外层键=样本序号
                self.iterator: {  # 本条样本编号（全局递增）
                    "latest_scan": latest_scan.tolist(),  # 激光序列（inf 已替换）转 list
                    "distance": distance.tolist(),  # 目标距离转 Python 数值（.tolist 兼容 numpy 标量）
                    "cos": cos.tolist(),  # 朝向 cos
                    "sin": sin.tolist(),  # 朝向 sin
                    "collision": collision,  # 是否碰撞（布尔）
                    "goal": goal,  # 是否到达目标（布尔）
                    "action": action,  # 当时执行的动作 [lin, rot]
                }  # 内层字典结束：单条样本的字段集
            }  # 外层字典结束：{样本序号: 样本字段}
            with open(self.file_location, "a") as outfile:  # 追加模式打开样本文件（不覆盖历史数据）
                yaml.dump(sample, outfile, default_flow_style=False)  # 块格式 YAML 追加写入——DRL 预训练的数据源

        return state, terminal  # 返回 (状态, 终止标志) 供训练循环使用
