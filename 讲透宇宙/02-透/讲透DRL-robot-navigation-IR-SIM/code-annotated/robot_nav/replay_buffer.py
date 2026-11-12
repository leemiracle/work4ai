import random  # 标准库随机模块：random.seed() 给全局播种保证采样序列可复现；random.sample() 做无放回均匀抽样
from collections import deque  # 双端队列：两端 append/popleft 都是 O(1)（list.pop(0) 是 O(n)），实现"定容覆盖写"的天然容器
import itertools  # 迭代器工具：itertools.islice 给 deque 做切片（deque 不支持列表式切片），采样时只取完整 episode

import numpy as np  # NumPy：把采样出的转移元组列表堆叠成 (B, ...) 向量化批量数组


# ===================== 类 ReplayBuffer：标准经验回放缓冲区 =====================
# 职责：为 off-policy（离策略，"off-policy"= 可用旧策略/别策略产生的数据训练当前策略）算法
#   存转移五元组，训练时随机抽样。经验回放=把交互历史存起来反复利用，一条数据可训练多次，样本效率高。
# 被谁调用：utils.get_buffer 为非 PPO/RCPG 模型（如 TD3）构造；utils.Pretraining.load_buffer 灌离线数据；
#   TD3.train 每个梯度步调 sample_batch(batch_size) 取训练批。
# 为何与 on-policy（在策略，PPO）不兼容：PPO 的策略梯度带重要性比率，要求样本产自当前策略，
#   旧策略数据会使梯度估计有偏 → utils.get_buffer 遇 PPO 直接绕过本类返回 model.buffer。
class ReplayBuffer(object):  # 标准经验回放缓冲区：定容环形存转移 + 均匀随机抽样小批量
    """
    Standard experience replay buffer for off-policy reinforcement learning algorithms.

    Stores tuples of (state, action, reward, done, next_state) up to a fixed capacity,
    enabling sampling of uncorrelated mini-batches for training.
    """

    # ---- __init__：初始化容量、计数器、底层容器与随机种子 ----
    # 输入：buffer_size=最多存多少条转移；random_seed=播种 random 模块保证抽样可复现
    # 输出：self 上挂 buffer_size / count / buffer 三个属性，全局 random 已播种
    def __init__(self, buffer_size, random_seed=123):  # 构造一个空 buffer；默认种子 123
        """
        Initialize the replay buffer.

        Args:
            buffer_size (int): Maximum number of transitions to store in the buffer.
            random_seed (int): Seed for random number generation.
        """
        self.buffer_size = buffer_size  # 容量上限：固定内存预算，交互百万步也不会内存溢出
        self.count = 0  # 当前元素数：增长到 buffer_size 后封顶（满了走覆盖分支）
        self.buffer = deque()  # 底层容器：注意未设 maxlen，环形覆盖由 add() 手工实现（对照下面 Rollout 版用 maxlen 自动化）
        random.seed(random_seed)  # 播种全局随机模块：同一种子 → 同一抽样序列，实验可复现

    # ---- add：写入单条转移（经验回放的核心写接口）----
    # 输入：s 当前状态 (state_dim,)；a 动作 (action_dim,)；r 奖励 float；
    #   t 终止旗标 bool（True=回合结束，用于 Bellman 目标截断未来项）；s2 下一状态 (state_dim,)
    # 被谁调用：utils.Pretraining.load_buffer（离线 YAML 灌数据）、训练主循环每次 env.step 之后。
    def add(self, s, a, r, t, s2):  # 一条马尔可夫转移 (s,a,r,done,s')；t 是 terminal 缩写
        """
        Add a transition to the buffer.

        Args:
            s (np.ndarray): State.
            a (np.ndarray): Action.
            r (float): Reward.
            t (bool): Done flag (True if episode ended).
            s2 (np.ndarray): Next state.
        """
        # 【教学】为何"定容 + 覆盖最旧"（环形缓冲）：
        #  1) 内存 O(buffer_size) 有上界，长训练不会泄漏；
        #  2) 旧转移来自很多代之前的策略，覆盖旧数据让训练分布持续贴近当前策略；
        #  3) 配合随机抽样打破时间相关性——时序相邻的转移几乎相同，按序喂网络会让梯度
        #     方向来回震荡；随机抽样近似恢复 iid（独立同分布）假设，这是 SGD 收敛的前提。
        experience = (s, a, r, t, s2)  # 五元组打包成不可变 tuple，作为 deque 的单个元素
        if self.count < self.buffer_size:  # 未满：增长期，只管追加
            self.buffer.append(experience)  # 右端入队，O(1)
            self.count += 1  # 计数 +1
        else:  # 已满：进入环形覆盖模式——固定容量，永远只覆盖最旧的一条
            self.buffer.popleft()  # 左端弹出最老转移（先进先出 FIFO），腾出一个位置，O(1)
            self.buffer.append(experience)  # 右端写入新转移；净效果 = 新数据覆盖旧数据

    # ---- size：查询当前已存转移条数 ----
    # 被谁调用：训练脚本在开训前判断存量是否够一个 batch。
    def size(self):  # O(1) 查询，不遍历容器
        """
        Get the number of elements currently in the buffer.

        Returns:
            (int): Current buffer size.
        """
        return self.count  # 直接返回计数器（满后恒等于 buffer_size）

    # ---- sample_batch：无放回均匀抽样一个训练小批（经验回放的核心读接口）----
    # 输入：batch_size = B；输出五个批量数组：
    #   s_batch (B, state_dim)、a_batch (B, action_dim)、r_batch (B,)、t_batch (B,)、s2_batch (B, state_dim)
    # 被谁调用：TD3.train——每个梯度步取一批算 critic/actor 损失。
    def sample_batch(self, batch_size):  # B = 本次抽取的转移条数
        """
        Sample a batch of experiences from the buffer.

        Args:
            batch_size (int): Number of experiences to sample.

        Returns:
            (Tuple of np.ndarrays): Batches of states, actions, rewards, done flags, and next states.
        """
        if self.count < batch_size:  # 存量不足：降级返回全部存量（批会小于 B）
            batch = random.sample(self.buffer, self.count)  # 无放回抽 count 条，避免 sample 大于 population 报错
        else:  # 正常情形
            batch = random.sample(self.buffer, batch_size)  # 均匀无放回抽 B 条：打破时间相关性的关键一步——样本可能来自不同回合/不同时期

        # 【教学】批量维度：下面的列表推导把 B 条同构转移"堆叠"成二维数组，
        #   第 0 维是批内样本索引、第 1 维是特征维，正好对上网络的输入 (B, in_dim)。
        s_batch = np.array([_[0] for _ in batch])  # 取每条转移的第 0 元（state）→ (B, state_dim)
        a_batch = np.array([_[1] for _ in batch])  # 取第 1 元（action）→ (B, action_dim)
        r_batch = np.array([_[2] for _ in batch])  # 取第 2 元（reward）→ (B,) 一维，未 reshape 成 (B,1)，调用方自行对齐
        t_batch = np.array([_[3] for _ in batch])  # 取第 3 元（done）→ (B,)
        s2_batch = np.array([_[4] for _ in batch])  # 取第 4 元（next_state）→ (B, state_dim)

        return s_batch, a_batch, r_batch, t_batch, s2_batch  # 返回批五元组；Bellman 目标 = r + (1-t)*γ*Q(s2, π(s2))

    # ---- return_buffer：全量导出整个缓冲区为五个对齐数组 ----
    # 与 sample_batch 的区别：不抽样、返回全部 N 条；r/t 已 reshape(-1,1) 成 (N,1)，
    #   可与 critic 输出 (N,1) 直接按元素运算。
    def return_buffer(self):  # N = 当前存量（全文导出，逐条不漏）
        """
        Return the entire buffer contents as separate arrays.

        Returns:
            (Tuple of np.ndarrays): Full arrays of states, actions, rewards, done flags, and next states.
        """
        s = np.array([_[0] for _ in self.buffer])  # 全部状态 → (N, state_dim)
        a = np.array([_[1] for _ in self.buffer])  # 全部动作 → (N, action_dim)
        r = np.array([_[2] for _ in self.buffer]).reshape(-1, 1)  # 全部奖励 → (N,1)；-1 = 自动推断为 N
        t = np.array([_[3] for _ in self.buffer]).reshape(-1, 1)  # 全部 done → (N,1)
        s2 = np.array([_[4] for _ in self.buffer])  # 全部下一状态 → (N, state_dim)

        return s, a, r, t, s2  # 形状清单：(N,state_dim), (N,action_dim), (N,1), (N,1), (N,state_dim)

    # ---- clear：清空缓冲区、计数器归零 ----
    def clear(self):  # 用于多次独立训练间的重置
        """
        Clear all contents of the buffer.
        """
        self.buffer.clear()  # deque 原地清空所有元素
        self.count = 0  # 计数归零，重新进入增长期


# ===================== 类 RolloutReplayBuffer：整回合（episode 级）经验回放 =====================
# 职责：按"回合"存完整轨迹（rollout = 从开局到 done 的一整条轨迹），采样时返回
#   某时刻的转移 + 它前面 history_len 步的状态序列，服务"以历史观测为条件"的策略（RNN 系）。
# 与 ReplayBuffer 的本质区别：存储粒度从"单条转移"升到"整条 episode"——当环境部分可观测
#   （单帧状态不满足马尔可夫性）时，单帧不足以决策，必须喂最近 H 帧的窗口。
# 被谁调用：utils.get_buffer 为 RCPG 模型构造；RCPG.train 从中采样历史序列训练。
class RolloutReplayBuffer(object):  # 回合级回放缓冲区：整条轨迹存取 + 历史窗口序列采样
    """
    Replay buffer that stores full episode rollouts, allowing access to historical trajectories.

    Useful for algorithms that condition on sequences of past states (e.g., RNN-based policies).
    """

    # ---- __init__：初始化回合容器与历史窗长 ----
    # 输入：buffer_size=最多存多少"条 episode"；random_seed=抽样种子；history_len=历史窗口 H
    def __init__(self, buffer_size, random_seed=123, history_len=10):  # H=10：每个采样点带过去 10 步观测
        """
        Initialize the rollout replay buffer.

        Args:
            buffer_size (int): Maximum number of episodes (rollouts) to store.
            random_seed (int): Seed for random number generation.
            history_len (int): Number of past steps to return for each sampled state.
        """
        self.buffer_size = buffer_size  # 回合容量上限（单位是 episode 不是 transition）
        self.count = 0  # 已"完结"的回合计数（注意：不是转移条数，size() 语义随之不同）
        self.buffer = deque(maxlen=buffer_size)  # deque 自带 maxlen：满后再 append 自动挤掉最左 episode——声明式环形覆盖，无需手工 popleft
        random.seed(random_seed)  # 播种随机抽样
        self.buffer.append([])  # 预开第 1 个空 episode；容器结构 = 列表的 deque，buffer[i] 是第 i 条回合的转移列表
        self.history_len = history_len  # 历史窗长 H，sample_batch 里用于补齐/截断

    # ---- add：把转移追加到当前（最右侧）episode；若该转移终结回合，则自动封存并开新回合 ----
    # 输入：五元组同 ReplayBuffer.add；t=True 标记回合结束。
    def add(self, s, a, r, t, s2):  # 永远写入 self.buffer[-1]（当前活跃 episode）
        """
        Add a transition to the current episode.

        If the transition ends the episode (t=True), a new episode is started.

        Args:
            s (np.ndarray): State.
            a (np.ndarray): Action.
            r (float): Reward.
            t (bool): Done flag.
            s2 (np.ndarray): Next state.
        """
        experience = (s, a, r, t, s2)  # 打包转移
        if t:  # 终结转移：存入并封存本回合
            self.count += 1  # 完结回合计数 +1
            self.buffer[-1].append(experience)  # 终结转移也入当前回合，保证轨迹完整（含最后一步）
            self.buffer.append([])  # 开下一条空 episode；若已满，deque(maxlen) 自动丢最老回合（环形覆盖）
        else:  # 回合中段转移
            self.buffer[-1].append(experience)  # 追加进当前活跃 episode

    # ---- size：查询已完结的回合条数 ----
    def size(self):  # 注意与 ReplayBuffer.size 的语义差异（那边数转移，这边数回合）
        """
        Get the number of complete episodes in the buffer.

        Returns:
            (int): Number of episodes.
        """
        return self.count  # 返回完结回合数

    # ---- sample_batch：从完结回合均匀抽 B 个"回合内位置"，每个位置返回 H 步历史序列 ----
    # 输出形状：
    #   s_batch (B, H, state_dim) 状态历史窗（时间正序；不足 H 用最早状态补齐）
    #   a_batch (B, action_dim) 采样位置处的动作
    #   r_batch (B,1)、t_batch (B,1) 采样位置处的奖励与 done
    #   s2_batch (B, H, state_dim) 下一状态历史窗
    # 被谁调用：RCPG.train——循环/历史条件策略的输入是序列而非单帧。
    def sample_batch(self, batch_size):  # B = 抽取的序列样本数
        """
        Sample a batch of state sequences and corresponding transitions from full episodes.

        Returns past `history_len` steps for each sampled transition, padded with the earliest step if necessary.

        Args:
            batch_size (int): Number of sequences to sample.

        Returns:
            (Tuple of np.ndarrays): Sequences of past states, actions, rewards, done flags, and next states.
        """
        # 【教学】islice(0, len-1) 排除最右侧元素——那是"未完结的当前回合"（可能是 __init__
        #   预开的空表或仍在写入的半截回合），不参与抽样，避免抽到空序列。
        if self.count < batch_size:  # 完结回合不足 B 条：降级全抽
            batch = random.sample(  # 无放回均匀抽 self.count 条完结回合
                list(itertools.islice(self.buffer, 0, len(self.buffer) - 1)), self.count  # islice 切出完结回合列表，第二参 = 抽取条数
            )  # 得到"回合列表"的样本（每条是一整条轨迹）
        else:  # 正常情形
            batch = random.sample(  # 无放回均匀抽 B 条完结回合
                list(itertools.islice(self.buffer, 0, len(self.buffer) - 1)), batch_size  # 同上切片，正常抽满 batch_size 条
            )  # 样本 = B 条完结回合

        idx = [random.randint(0, len(b) - 1) for b in batch]  # 每条回合内再随机挑一个位置；randint 是闭区间 [0, len-1]

        s_batch = []  # 收集各样本的状态历史窗，最终堆叠为 (B, H, state_dim)
        s2_batch = []  # 收集各样本的下一状态历史窗，同形状
        for i in range(len(batch)):  # 逐个处理抽中的回合
            if idx[i] == len(batch[i]):  # 防御分支（实际不可达：idx[i] ≤ len-1 < len），且两分支取值相同
                s = batch[i]  # 取整条回合
                s2 = batch[i]  # 同源
            else:  # 主路径
                s = batch[i][: idx[i] + 1]  # 取从回合开头到采样位置（含）的前 idx+1 条转移
                s2 = batch[i][: idx[i] + 1]  # 同一段转移，稍后从中抽 next_state
            s = [v[0] for v in s]  # 抽出各转移的 state → 从开局到当前的状态列表
            s = s[::-1]  # 反转为 [当前, 上一帧, ..., 回合开头]——列表尾部代表"最老"

            s2 = [v[4] for v in s2]  # 抽出各转移的 next_state → 与 s 等长
            s2 = s2[::-1]  # 同样反转为"由新到旧"

            # 【教学】补齐/截断到定长 H：RNN 小批量要求同一 batch 内序列等长。
            if len(s) < self.history_len:  # 历史不足 H（靠近回合开头）
                missing = self.history_len - len(s)  # 缺的帧数
                s += [s[-1]] * missing  # 用"最老的那帧"（反转后的 s[-1] 即回合第一帧）复制补齐——首帧重复 padding
                s2 += [s2[-1]] * missing  # s2 同法补齐
            else:  # 历史够长
                s = s[: self.history_len]  # 反转序下前 H 帧恰是"最近的 H 帧"，直接截断
                s2 = s2[: self.history_len]  # 同法截断
            s = s[::-1]  # 再反转为时间正序 [最老, ..., 当前]，喂给 RNN
            s_batch.append(s)  # 收进批：长度 H 的状态序列
            s2 = s2[::-1]  # s2 也反回时间正序
            s2_batch.append(s2)  # 收进批：长度 H 的下一状态序列

        a_batch = np.array([batch[i][idx[i]][1] for i in range(len(batch))])  # 各采样位置的动作 → (B, action_dim)
        r_batch = np.array([batch[i][idx[i]][2] for i in range(len(batch))]).reshape(  # 各采样位置的奖励 → (B,1)
            -1, 1  # -1 自动推断为 B，明确成一列
        )  # r_batch 定形 (B,1)
        t_batch = np.array([batch[i][idx[i]][3] for i in range(len(batch))]).reshape(  # 各采样位置的 done → (B,1)
            -1, 1  # 同上，一列
        )  # t_batch 定形 (B,1)

        return np.array(s_batch), a_batch, r_batch, t_batch, np.array(s2_batch)  # 批五元组：状态窗 (B,H,state_dim)、动作 (B,action_dim)、奖励 (B,1)、done (B,1)、下一状态窗 (B,H,state_dim)

    # ---- clear：清空全部回合 ----
    def clear(self):  # 注意：清空后未像 __init__ 那样重开空 episode，若直接 add 会 IndexError（原代码行为照录）
        """
        Clear all stored episodes from the buffer.
        """
        self.buffer.clear()  # 清掉全部回合（含活跃回合）
        self.count = 0  # 完结回合计数归零
