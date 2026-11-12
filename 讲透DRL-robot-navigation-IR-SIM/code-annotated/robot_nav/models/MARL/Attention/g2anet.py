# ═══════════════════════════════════════════════════════════════════════ 丨 教学注释版：注释为纯增量，代码逐字符未改
# 【教学注释版】g2anet.py —— G2ANet（双阶段 hard+soft 注意力，稠密计算版）
# ───────────────────────────────────────────────────────────────────── 丨 文件导读
# 【在 MARL 中的作用】多机器人导航中每个机器人需要"参考邻居"再决策。本模块是
#   双阶段注意力编码器：
#   ① 硬注意力（Gumbel-Softmax 二分类门控，tau=0.5）：对每个邻居给出"关注/不关
#      注"的软采样概率，作为开关；
#   ② 软注意力（scaled dot-product）：q·k/√d 打分 + softmax，对全部 N-1 个邻居
#      按相关度分配权重；
#   最终权重 = 软权重 × 硬门控，对邻居 value 加权求和——即"先粗筛、再细配权"。
# 【与经典论文的差异（如实标注）】Liu et al.(2020, AAAI) 的 G2ANet 原版软注意力
#   打分是 ESL+CSL 双阶段（逐元素层+拼接层）+ GLU 门控；本实现简化为单阶段
#   scaled dot-product（q·k/√d），无 GLU——双阶段 hard+soft 的总体思想保留，
#   打分器实现与论文不同。
# 【与 iga.py 的差异（代码实证）】① 稠密：逐个 i 显式遍历全部 N-1 个 j（不建图、
#   无 PyG MessagePassing）；② 硬门控以"乘法掩码"进入最终权重，而非先剪边；
#   ③ 软注意力带 √d 缩放（iga 的打分 MLP 无显式缩放）；④ 解码器单层无激活
#   （iga 两层+LeakyReLU）；⑤ tau=0.5（iga 用 0.2）。
# ═══════════════════════════════════════════════════════════════════════ 丨 教学注释版：注释为纯增量，代码逐字符未改
import torch  # 导入 PyTorch 主库：张量运算与自动微分
import torch.nn as nn  # 神经网络子模块别名 nn：Linear / Sequential 等层
import torch.nn.functional as F  # 函数式接口别名 F：relu / softmax / gumbel_softmax 等无状态调用
import numpy as np  # 导入 NumPy：本文件用其 np.pi / np.sqrt 数学常量


# ── 类职责：G2ANet 双阶段注意力编码器——硬门控（Gumbel 二分类）× 软注意力
#       （scaled dot-product）相乘后对全部 N-1 个邻居加权求和，再拼接自身解码
# 输入：embedding (B,N,D≥11)（位置/朝向/特征/动作/目标按序拼接）
# 输出：六元组（见 forward docstring），核心 output (B*N,2*emb)
# 调用者：上游 MARL 算法网络；与 iga.py 返回签名一致，二者可互换（性能对比用）
# 教学点：本文件无图结构——"邻居集合"就是除我以外的所有人，硬门控不剪集合、
#         只以乘法方式把未选中邻居的权重压向 0
class G2ANet(nn.Module):  # 类定义：G2ANet 双阶段注意力模块
    """
    Graph-based attention network for multi-agent coordination.

    Encodes per-agent features, builds pairwise geometric edge features, computes
    hard (binary) attention and soft (weighted) attention, and decodes the
    concatenation of self and attended features.

    Args:
        embedding_dim (int): Dimensionality of the internal agent embedding.

    Attributes:
        hard_encoding (nn.Linear): Outputs logits for binary attention (2 classes).
        q (nn.Linear): Query projection for soft attention.
        k (nn.Linear): Key projection from edge features for soft attention.
        v (nn.Linear): Value projection from edge features for soft attention.
        hard_mlp (nn.Sequential): MLP over concatenated node/edge features for hard attention.
        decoding (nn.Linear): Final decoder mapping concatenated embeddings to output.
        embedding1 (nn.Linear): First layer for agent feature encoding.
        embedding2 (nn.Linear): Second layer for agent feature encoding.
    """
    # ↑ docstring 原样保留

    # 构造函数：硬门控头 + 软注意力 q/k/v 三投影 + 硬注意力 MLP + 单层解码器 + 编码器
    # embedding_dim=内部嵌入维；注意与 iga.py 差异：这里没有 MessagePassing/图结构
    def __init__(self, embedding_dim):  # 构造函数：声明全部子模块
        super(G2ANet, self).__init__()  # 初始化 nn.Module 基类（注册参数/子模块所必需）
        self.embedding_dim = embedding_dim  # 记录嵌入维度，forward 中多处要用
        self.hard_encoding = nn.Linear(embedding_dim, 2)  # 硬注意力分类头：emb → 2 类 logits（不关注/关注），二分类决定"看不看这个邻居"

        # Soft 丨 软注意力三投影（query/key/value 范式：query=我想找什么信息，key=对方条目的"标签"，value=对方条目的实际内容；打分=query 与 key 的相似度）
        self.q = nn.Linear(embedding_dim, embedding_dim, bias=False)  # Q 投影：智能体嵌入→查询向量（无偏置，打分只看方向）
        self.k = nn.Linear(10, embedding_dim, bias=False)  # K 投影：10 维边特征→键（10=7 几何+3 目标极坐标，与 iga 相同）
        self.v = nn.Linear(10, embedding_dim)  # V 投影：10 维边特征→值=被聚合的信息内容（带偏置）

        self.hard_mlp = nn.Sequential(  # 硬注意力主干 MLP：输入"我的嵌入 ⊕ 7 维边几何"
            nn.Linear(embedding_dim + 7, embedding_dim),  # (emb+7) → emb；7=距离1+相对角cos/sin2+对方朝向cos/sin2+动作2
            nn.ReLU(),  # ReLU 非线性：负值清零
            nn.Linear(embedding_dim, embedding_dim),  # emb → emb（硬注意力 MLP 第二层全连接）
        )  # hard_mlp 结束

        self.decoding = nn.Linear(embedding_dim * 2, embedding_dim * 2)  # 解码器（单层、无激活——iga.py 是两层+LeakyReLU）：拼接嵌入 → 输出 2*emb

        self.embedding1 = nn.Linear(5, 128)  # 编码器第一层：5 维原始体感特征 → 128 维
        nn.init.kaiming_uniform_(self.embedding1.weight, nonlinearity="leaky_relu")  # Kaiming(He) 均匀初始化：方差匹配激活增益，防信号随深度爆炸/消失
        self.embedding2 = nn.Linear(128, embedding_dim)  # 编码器第二层：128 → embedding_dim
        nn.init.kaiming_uniform_(self.embedding2.weight, nonlinearity="leaky_relu")  # 同上 Kaiming 初始化

    # 特征编码：两层 MLP 把 5 维原始特征升维为 embedding_dim 嵌入
    # 输入 (B*N,5) → 输出 (B*N,embedding_dim)；调用者=forward
    def encode_agent_features(self, embed):  # 特征编码函数：两层 MLP 升维
        """
        Encode per-agent features with a two-layer MLP.

        Args:
            embed (Tensor): Raw agent features of shape (B*N, 5).

        Returns:
            Tensor: Encoded embeddings of shape (B*N, embedding_dim).
        """
        # ↑ docstring 原样保留
        embed = F.leaky_relu(self.embedding1(embed))  # 第一层+LeakyReLU：(B*N,5) → (B*N,128)；LeakyReLU=负半轴保留小斜率而非清零
        embed = F.leaky_relu(self.embedding2(embed))  # 第二层+LeakyReLU：(B*N,128) → (B*N,emb)
        return embed  # 返回编码后的嵌入

    # 前向主流程：①切特征 ②成对几何边特征 ③硬门控（Gumbel 采样）④软注意力
    # （scaled dot-product）⑤软×硬组合加权求和 ⑥拼接自身解码
    # 与 iga.py 差异（代码实证）：不建图——对每个 i 稠密遍历全部 N-1 个 j 打分，
    # 硬门控以"乘法掩码"进入最终权重，而非像 iga.py 先剪边再消息传递
    def forward(self, embedding):  # 前向主入口：双阶段注意力全流程
        """
        Compute hard and soft attentions and produce attended embeddings.

        Args:
            embedding (Tensor): Input tensor of shape (B, N, D), where D ≥ 11. Expected to
                include position (x,y), heading (cos,sin), agent features (for encoding),
                action, and goal.

        Returns:
            tuple:
                output (Tensor): Attended embedding, shape (B*N, 2*embedding_dim).
                hard_logits (Tensor): Hard attention logits (keep class index 1),
                    shape (B*N, N-1).
                unnorm_rel_dist (Tensor): Unnormalized pairwise distances,
                    shape (B*N, N-1, 1).
                mean_entropy (Tensor): Scalar mean entropy of combined (soft×hard) weights.
                hard_weights (Tensor): Binary hard attention mask, shape (B, N, N-1).
                comb_w (Tensor): Combined weights per (receiver, sender) after soft×hard,
                    shape (N, N*(N-1)).
        """
        # ↑ docstring 原样保留
        if embedding.dim() == 2:  # 兼容无 batch 维输入：按 B=1 处理
            embedding = embedding.unsqueeze(0)  # (N,D) → (1,N,D)：补上 batch 维
        batch_size, n_agents, _ = embedding.shape  # 解包维度：批大小 B、智能体数 N（特征维弃用）

        # Extract sub-features 丨 按"魔法切片"从拼接大向量取各物理量：D=[x,y, cosθ,sinθ, 5维特征(4:9), 动作(7:9), 目标(-2:)]（与 iga.py 完全一致的切法）
        embed = embedding[:, :, 4:9].reshape(batch_size * n_agents, -1)  # 取 5 维体感特征并压平 batch：(B,N,5) → (B*N,5)
        position = embedding[:, :, :2].reshape(batch_size, n_agents, 2)  # 位置 (x,y)：(B,N,2)
        heading = embedding[:, :, 2:4].reshape(  # 取朝向 (cosθ,sinθ)：成对编码避免 ±π 周期跳变，(B,N,2)
            batch_size, n_agents, 2  # 重塑为 (B,N,2)
        )  # assume (cos(θ), sin(θ)) 丨 原注释：假定该 2 维顺序为 (cosθ, sinθ)
        action = embedding[:, :, 7:9].reshape(batch_size, n_agents, 2)  # 最近动作 (2 维)：作为对方"意图"线索进入边特征
        goal = embedding[:, :, -2:].reshape(batch_size, n_agents, 2)  # 目标点 (x,y)：取最后 2 维，(B,N,2)

        # Compute pairwise relative goal vectors (for each i,j) 丨 对每个有序对 (i,j)：j 的目标相对 i 的位置——"j 想去哪"
        goal_j = goal.unsqueeze(1).expand(-1, n_agents, -1, -1)  # goal (B,N,2)→(B,1,N,2)→expand→(B,N,N,2)：j 的目标广播给每个 i
        pos_i = position.unsqueeze(2)  # position (B,N,2)→(B,N,1,2)：i 的位置，准备广播相减
        goal_rel_vec = goal_j - pos_i  # 广播减法：(B,N,N,2)，goal_rel_vec[b,i,j]=j 的目标 − i 的位置

        # Encode agent features 丨 5 维原始特征 → 高维嵌入（embedding=把原始输入映射为稠密向量，便于网络提取模式）
        agent_embed = self.encode_agent_features(embed)  # 编码：(B*N,5) → (B*N,emb)
        agent_embed = agent_embed.view(batch_size, n_agents, self.embedding_dim)  # 恢复 batch 结构：(B*N,emb) → (B,N,emb)

        # Prep for hard attention: compute all relative geometry for each agent pair 丨 为硬注意力准备所有有序对 (i,j) 的相对几何量
        h_i = agent_embed.unsqueeze(2)  # (B, N, 1, D) 丨 我的嵌入沿 j 维广播
        pos_i = position.unsqueeze(2)  # (B, N, 1, 2) 丨 我的位置（覆盖上文 goal 段的同名变量）
        pos_j = position.unsqueeze(1)  # (B, 1, N, 2) 丨 对方位置沿 i 维广播
        heading_i = heading.unsqueeze(2)  # (B, N, 1, 2) 丨 我的朝向
        heading_j = heading.unsqueeze(1).expand(-1, n_agents, -1, -1)  # (B, 1, N, 2) 丨 对方朝向广播到全部 (i,j) 对

        # Compute relative vectors and distance 丨 有序对 (i,j)：j 相对 i 的位置向量与欧氏距离
        rel_vec = pos_j - pos_i  # (B, N, N, 2) 丨 广播相减：rel_vec[b,i,j] = pos_j − pos_i
        dx, dy = rel_vec[..., 0], rel_vec[..., 1]  # 拆出 x/y 分量 (B,N,N)，供下方角度计算
        rel_dist = (  # 归一化距离：欧氏范数 ÷ 12（场地尺度），把数值压到 O(1) 利于训练
            torch.linalg.vector_norm(rel_vec, dim=-1, keepdim=True) / 12  # L2 范数 (B,N,N,1)；/12=按地图尺寸归一
        )  # (B, N, N, 1) 丨 keepdim=True 保留末维，便于后续拼接

        # Relative angle in agent i's frame 丨 把 j 的方位角转到 i 的机体系（机器人只理解自身坐标系）
        angle = torch.atan2(dy, dx) - torch.atan2(heading_i[..., 1], heading_i[..., 0])  # 全局方位角 atan2(dy,dx) 减去我的朝向角 → 机体系相对角 (B,N,N)
        angle = (angle + np.pi) % (2 * np.pi) - np.pi  # 折叠到 (−π,π]：加 π、模 2π、再减 π（处理角度环绕）
        rel_angle_sin = torch.sin(angle)  # 相对角正弦 (B,N,N)
        rel_angle_cos = torch.cos(angle)  # 相对角余弦 (B,N,N)——角度用 sin/cos 成对编码，避免周期跳变

        # Other agent's heading 丨 对方 j 的朝向分量（cos/sin 成对）
        heading_j_cos = heading_j[..., 0]  # (B, 1, N) 丨 j 的 cosθ
        heading_j_sin = heading_j[..., 1]  # (B, 1, N) 丨 j 的 sinθ

        # Edge features for hard attention 丨 拼出 7 维硬注意力边特征 [距离1 + 相对角2 + 对方朝向2 + 动作2]
        edge_features = torch.cat(  # 沿最后一维拼接，输出 (B,N,N,7)
            [  # 拼接列表开始
                rel_dist,  # (B, N, N, 1) 丨 归一化距离
                rel_angle_cos.unsqueeze(-1),  # (B, N, N, 1) 丨 相对角 cos（补回末维）
                rel_angle_sin.unsqueeze(-1),  # (B, N, N, 1) 丨 相对角 sin
                heading_j_cos.unsqueeze(-1),  # (B, N, N, 1) 丨 对方朝向 cos
                heading_j_sin.unsqueeze(-1),  # (B, N, N, 1) 丨 对方朝向 sin
                action.unsqueeze(1).expand(-1, n_agents, -1, -1),  # (B, N, N, 2) 丨 j 的最近动作广播到所有 i（"j 在做什么"的意图线索）
            ],  # 列表结束
            dim=-1,  # 最后一维拼接
        )  # edge_features 完成：(B,N,N,7)

        # Broadcast agent embedding for all pairs (except self-pairs) 丨 把我的嵌入广播给全部 j；与 iga.py 不同：这里随后真的用掩码剔除自对角线
        h_i_expanded = h_i.expand(-1, -1, n_agents, -1)  # (B,N,1,D) → (B,N,N,D)；expand=零拷贝广播视图

        # Remove self-pairs using mask 丨 用"非单位阵"布尔掩码把 N×N 中的自对角线剔掉 → 每行只剩 N-1 个邻居
        mask = ~torch.eye(n_agents, dtype=torch.bool, device=embedding.device)  # ~eye：对角线 False、其余 True，(N,N)——True 位置保留
        h_i_flat = h_i_expanded[:, mask].reshape(  # 布尔索引取出非自身对（高级索引会摊平被选维度）
            batch_size * n_agents, n_agents - 1, self.embedding_dim  # 重塑为 (B*N, N-1, D)：每个 i 恰好 N-1 个邻居
        )  # reshape 完成
        edge_flat = edge_features[:, mask].reshape(  # 同法剔除自对角线的边特征
            batch_size * n_agents, n_agents - 1, -1  # → (B*N, N-1, 7)：边特征压平（每行一个 (b,i)）
        )  # reshape 完成

        # Concatenate agent embedding and edge features 丨 硬注意力输入 = 我的嵌入 ⊕ 边几何
        hard_input = torch.cat([h_i_flat, edge_flat], dim=-1)  # → (B*N, N-1, D+7)：每行=「我是谁 + 对面那位与我什么关系」

        # Hard attention forward 丨 硬注意力前向：对每个邻居对输出"关注/不关注"概率
        h_hard = self.hard_mlp(hard_input)  # MLP 提特征：(B*N, N-1, D+7) → (B*N, N-1, D)
        hard_logits = self.hard_encoding(h_hard)  # 线性层出 2 类 logits：(B*N, N-1, 2)（logit=softmax 前的未归一化分数）
        hard_weights = F.gumbel_softmax(hard_logits, hard=False, tau=0.5, dim=-1)[  # Gumbel-Softmax 采样：logits 加 Gumbel 噪声+温度 softmax，等价从二分类分布采样；tau=0.5 低温→接近 one-hot（iga.py 用更低的 0.2）；hard=False→软样本可微
            ..., 1  # 取"关注"类（index=1）的概率 → (B*N, N-1)
        ].unsqueeze(2)  # 补回末维 → (B*N, N-1, 1)
        hard_weights = hard_weights.view(batch_size, n_agents, n_agents - 1)  # 恢复 batch：(B,N,N-1)，hard_weights[b,i,:]=i 对各邻居的关注概率
        # hard_weights = hard_weights.permute(1, 0, 2) 丨 原作者注释掉的旧代码（维度转置实验），按规范原样保留

        unnorm_rel_dist = torch.linalg.vector_norm(rel_vec, dim=-1, keepdim=True)  # 未归一化成对距离 (B,N,N,1)（备份返回给上游，供奖励/日志使用）
        unnorm_rel_dist = unnorm_rel_dist[:, mask].reshape(  # 同掩码剔除自对角线
            batch_size * n_agents, n_agents - 1, 1  # → (B*N, N-1, 1)：距离张量压平
        )  # reshape 完成

        # ---- Soft attention computation ---- 丨 软注意力段：目标极坐标特征 → q/k/v 全量投影 → 逐 i 稠密打分
        attention_outputs = []  # 预留列表（本实现实际未填充——自 iga.py 复制同源的痕迹，真正收集在下方 x）
        entropy_list = []  # 收集每个智能体的组合权重熵
        combined_w = []  # 收集每个智能体的软×硬组合权重

        # Goal-relative polar features for soft attention 丨 目标相对量→极坐标（距离+角度 cos/sin）：软注意力的额外"意图"通道
        goal_rel_dist = torch.linalg.vector_norm(goal_rel_vec, dim=-1, keepdim=True)  # j 的目标到我的距离 (B,N,N,1)
        goal_angle_global = torch.atan2(goal_rel_vec[..., 1], goal_rel_vec[..., 0])  # 目标全局方位角 (B,N,N)
        heading_angle = torch.atan2(heading_i[..., 1], heading_i[..., 0])  # 我的朝向角 (B,N,1)（广播参与下行减法）
        goal_rel_angle = goal_angle_global - heading_angle  # 转到我的机体系 (B,N,N)
        goal_rel_angle = (goal_rel_angle + np.pi) % (2 * np.pi) - np.pi  # 折叠回 (−π,π]
        goal_rel_angle_cos = torch.cos(goal_rel_angle).unsqueeze(-1)  # 目标相对角 cos (B,N,N,1)
        goal_rel_angle_sin = torch.sin(goal_rel_angle).unsqueeze(-1)  # 目标相对角 sin (B,N,N,1)
        goal_polar = torch.cat(  # 拼成 3 维目标极坐标特征
            [goal_rel_dist, goal_rel_angle_cos, goal_rel_angle_sin], dim=-1  # → (B,N,N,3)：极坐标三元组拼接
        )  # goal_polar 完成

        # Soft attention edge features (include goal polar) 丨 软注意力边特征 = 7 维几何 + 3 维目标极坐标 = 10 维
        soft_edge_features = torch.cat([edge_features, goal_polar], dim=-1)  # → (B,N,N,10)，与 self.k/self.v 的输入维 10 对齐

        q = self.q(agent_embed)  # 全体查询向量 (B,N,emb)——与 iga.py 不同：这里的 q 真正参与点积打分
        epsilon = 1e-6  # 防除零小量（熵归一化时用）

        # q = self.q(h_out).reshape(-1, self.args.n_agents, self.args.attention_dim)  # (batch_size, n_agents, args.attention_dim) 丨 原作者注释掉的旧代码（args 风格源自开源 G2A 实现），原样保留
        k = self.k(soft_edge_features)  # 全部有序对的键：(B,N,N,10) → (B,N,N,emb)；k[b,i,j]=i 眼中 j 这条"关系"的键
        v = F.relu(self.v(soft_edge_features))  # 全部有序对的值（ReLU 激活；注意 k 未激活、iga.py 用 LeakyReLU——两文件激活选择不同）
        x = []  # 收集每个智能体 i 的聚合输出
        for i in range(n_agents):  # 逐接收者 i 计算注意力（N 次循环=稠密注意力；iga.py 无此循环，换成逐 batch 建图）
            q_i = q[:, i].view(-1, 1, self.embedding_dim)  # 我的查询 (B,emb) → (B,1,emb)：行向量形态，准备与各邻居键做点积
            k_b = k[:, i, :, :]  # 我对所有 j 的键 (B,N,emb)
            k_i = [  # 收集"除我以外"所有邻居的键（列表推导）
                k_b[:, j] for j in range(n_agents) if j != i  # 逐 j 取 (B,emb)，剔除 j=i（自身）
            ]  # keys of all other agents w.r.t agent i 丨 得到 N-1 个 (B,emb)
            v_b = v[:, i, :, :]  # 我对所有 j 的值 (B,N,emb)
            v_i = [  # 同法收集非自身的值
                v_b[:, j] for j in range(n_agents) if j != i  # 逐 j 取 (B,emb)，剔除自身
            ]  # values of all other agents w.r.t agent i 丨 得到 N-1 个 (B,emb)

            k_i = torch.stack(  # 列表堆叠成张量
                k_i, dim=0  # 沿新维度 0 堆叠 N-1 个 (B,emb)
            )  # (n_agents - 1, batch_size, args.attention_dim) 丨 原注释保留（args.* 命名系旧代码痕迹）：堆叠后形状
            k_i = k_i.permute(1, 2, 0)  # -> (batch_size, embedding_dim, n_agents - 1) 丨 维度重排 → (B,emb,N-1)：emb 居中才能与 q_i 做矩阵乘
            v_i = torch.stack(v_i, dim=0)  # 值同样堆叠 (N-1, B, emb)
            v_i = v_i.permute(1, 2, 0)  # → (B,emb,N-1)：值矩阵重排完成

            # (batch_size, 1, attention_dim) * (batch_size, attention_dim，n_agents - 1) = (batch_size，1，n_agents - 1) 丨 原注释（含全角逗号）说明点积的维度收缩：q 与每个邻居 k 的内积
            score = torch.matmul(q_i, k_i)  # 批量点积：(B,1,emb) × (B,emb,N-1) → (B,1,N-1)：我对每个邻居的原始相似度分

            # scale then softmax for soft weights 丨 缩放+softmax：scaled dot-product attention 的标准两步
            scaled_score = score / np.sqrt(self.embedding_dim)  # 除以 √d_k：内积方差随维度线性增大，不缩放会让 softmax 进入饱和区（梯度消失）——这就是 "scaled" 的含义（iga.py 的 MLP 打分无此步）
            soft_weight = F.softmax(  # 对 N-1 个邻居的分数归一化
                scaled_score, dim=-1  # 沿邻居维 softmax：权重非负且和为 1
            )  # (batch_size，1, n_agents - 1) 丨 原注释保留（全角逗号）：输出形状 (B,1,N-1)

            # combine soft and hard weights, then weighted sum of values 丨 软×硬组合（G2ANet 招牌）：硬门控像开关把未选中邻居的权重压向 0（iga.py 是先剪边，此处是乘掩码）
            x_i = (v_i * soft_weight * hard_weights[:, i, :].unsqueeze(1)).sum(dim=-1)  # 三项逐元素乘 (B,emb,N-1)×(B,1,N-1)×(B,1,N-1) 再沿邻居维求和 → (B,emb)：邻居信息加权聚合的落点
            x.append(x_i)  # 收集智能体 i 的聚合结果

            combined_weights = soft_weight * hard_weights[:, i, :].unsqueeze(  # 组合权重=软×硬（未归一化，和不再为 1）
                1  # unsqueeze(1) 跨行书写：把 (B,N-1) 变 (B,1,N-1) 以广播
            )  # (B, 1, N-1) 丨 组合权重形状
            combined_w.append(combined_weights)  # 收集组合权重

            # Normalize for entropy calculation 丨 熵计算前归一化：softmax 权重乘硬门控后不再和为 1，除以总和恢复成概率分布
            combined_weights_norm = combined_weights / (  # 归一化组合权重
                combined_weights.sum(dim=-1, keepdim=True) + epsilon  # 沿邻居维求和 + ε 防除零
            )  # 归一化完成 (B,1,N-1)

            # Entropy for analysis/logging 丨 注意力熵：监控权重集中度（低熵=专注少数邻居，高熵=权重摊平）
            entropy = (  # 熵 = −Σ p·log p，跨多行链式书写
                -(combined_weights_norm * (combined_weights_norm + epsilon).log())  # 每个邻居的 −p·log(p)；+ε 防 log(0)
                .sum(dim=-1)  # 沿邻居维求和 → 每个 batch 一个熵值
                .mean()  # 对 batch 取均值 → 标量
            )  # 熵计算完成
            entropy_list.append(entropy)  # 收集智能体 i 的熵

        # concatenate self and attended features per agent 丨 MARL 注意力输出标准组装：自身嵌入 ⊕ 邻居加权聚合嵌入
        x = torch.stack(x, dim=1).reshape(  # N 个 (B,emb) 沿 dim1 堆叠 → (B,N,emb)
            -1, self.embedding_dim  # 压平 batch 维 → (B*N, emb)
        )  # (batch_size * n_agents, args.attention_dim) 丨 原注释保留：最终形状（args 命名系旧代码痕迹）
        self_embed = agent_embed.reshape(-1, self.embedding_dim)  # 自身嵌入 (B*N,emb)——保底信息，不依赖任何邻居
        final_input = torch.cat([self_embed, x], dim=-1)  # 拼接 → (B*N, 2*emb)
        output = self.decoding(final_input)  # 单层线性解码（无激活；iga.py 为两层+LeakyReLU）：(B*N,2*emb) → (B*N,2*emb)
        mean_entropy = torch.stack(entropy_list).mean()  # 所有智能体熵的平均（标量，监控/熵正则用）
        comb_w = torch.stack(combined_w, dim=1).reshape(n_agents, -1)  # 组合权重堆叠变形 (N, B*(N-1))：每行一个接收者、列展开 batch×发送者

        return (  # 返回六元组——与 iga.py 返回签名完全一致（上层算法可无缝互换两个注意力模块做对比实验）
            output,  # ① 注意力输出 (B*N,2*emb)：喂给下游 Q 网络/策略网络
            hard_logits[..., 1],  # ② 硬注意力"关注"类 logit (B*N,N-1)：供上游做辅助损失
            unnorm_rel_dist,  # ③ 未归一化成对距离 (B*N,N-1,1)
            mean_entropy,  # ④ 软×硬组合权重的平均熵（标量）
            hard_weights,  # ⑤ 硬门控概率 (B,N,N-1)
            comb_w,  # ⑥ 软×硬组合权重 (N, B*(N-1))
        )  # return 结束
