# ═══════════════════════════════════════════════════════════════════════ 丨 教学注释版：注释为纯增量，代码逐字符未改
# 【教学注释版】iga.py —— IGA（Intention/Goal-aware Graph Attention，意图-目标图注意力）
# ───────────────────────────────────────────────────────────────────── 丨 文件导读
# 【在 MARL 中的作用】多机器人导航里每个机器人只有局部观测；避碰/协同需要"参考
#   邻居"。注意力机制=给每个候选邻居分配 0~1 的相关度权重，再对邻居信息加权求和
#   ——权重高的邻居对决策影响大。本文件是"两阶段注意力"：
#   ① 硬注意力（Gumbel-Softmax 二分类门控，tau=0.2）：决定"看谁/不看谁"，
#      只给选中的邻居建图边（图稀疏化）；
#   ② 软注意力（GoalAttentionLayer 消息传递）：在稀疏图上按相关度加权聚合邻居。
# 【与 g2anet.py 的差异（代码实证）】g2anet=稠密：对全部 N-1 邻居做 scaled
#   dot-product 打分后"乘"硬门控；本文件=稀疏：硬门控先剪边（>0.5 才建边），
#   软注意力换成 PyG MessagePassing + 打分 MLP（加性注意力，无 √d 缩放），
#   解码器两层（g2anet 只有一层）。
# 【勘误（以代码为准）】① 本类自带的 q/k/v/attn_score_layer 以及 forward 中算出
#   的 q 均未被后续消费——真正的软注意力在 message_graph 内部用自己的 q/k/v 计
#   算，外层投影是自 g2anet 迁移的"残留权重"（占参数但无功能）；
#   ② docstring 声称 hard_logits/距离为 (B*N,N-1)，实际未剔除自对角线，是 (B*N,N)。
# ═══════════════════════════════════════════════════════════════════════ 丨 教学注释版：注释为纯增量，代码逐字符未改
import numpy as np  # 导入 NumPy：本文件仅用其 np.pi / np.sqrt 数学常量
import torch  # 导入 PyTorch 主库：张量运算与自动微分
import torch.nn as nn  # 神经网络子模块别名 nn：Linear / Sequential / LeakyReLU 等层
import torch.nn.functional as F  # 函数式接口别名 F：leaky_relu / gumbel_softmax 等无状态调用
from torch_geometric.nn import MessagePassing  # PyG 消息传递基类：图上"沿边算消息→按节点聚合"的骨架
from torch_geometric.utils import softmax  # PyG 分组 softmax：按目标节点把边分数归一化为组内概率（和为 1）


# ── 函数职责：计算入边注意力分布的平均熵（香农熵），用于监控注意力集中度
# 输入：attn_weights 逐边概率 (E,)；target_nodes 逐边目标节点 (E,)；num_nodes 节点数
# 输出：标量（有入边节点的平均熵；完全无边时返回 0.0）；调用者=Attention.forward
# 教学点：熵低=权重集中少数邻居（专注），熵高=权重摊平（犹豫）；MARL 中可作熵正则项
def entropy_from_attention(attn_weights, target_nodes, num_nodes, eps=1e-10):  # 函数定义：注意力熵统计（职责/输入输出见上方块注释）
    """
    Compute mean per-node entropy of incoming softmax attention distributions.

    Args:
        attn_weights (Tensor): Per-edge attention probabilities of shape (num_edges,).
        target_nodes (Tensor): Destination node indices for each edge of shape (num_edges,).
        num_nodes (int): Total number of nodes/agents.
        eps (float, optional): Small constant for numerical stability in log. Defaults to 1e-10.

    Returns:
        Tensor: Scalar tensor containing the mean entropy across nodes that have at least
            one incoming edge. Returns 0.0 if no nodes have incoming edges.
    """
    # ↑ docstring 按规范原样保留（不添加/不修改/不删除），故其中行不带中文注释

    # Compute log(p), safe for zero 丨 对每条边的注意力概率取对数；+eps 防 p=0 时 log 发散（数值稳定技巧）
    attn_log = (attn_weights + eps).log()  # log(p+eps)：shape 仍为 (E,)

    # For each edge, p*log(p) 丨 每条边对熵的贡献项 -p·log p（p→0 或 1 时趋于 0，权重"半斤八两"时最大）
    contrib = -(attn_weights * attn_log)  # [num_edges] 丨 逐边熵贡献 (E,)
    # ↑ 以上两行合起来即香农熵公式 H=-Σ p log p 的被求和项

    # Sum contributions per node (i.e., sum over incoming edges) 丨 按目标节点分组求和：节点 i 的熵=其所有入边贡献之和
    entropies = torch.zeros(num_nodes, device=attn_weights.device).index_add_(  # 建 (num_nodes,) 全 0 向量并原位散射累加
        0, target_nodes, contrib  # 沿 dim0 把 contrib[t] 加到 entropies[target_nodes[t]] 上（同目标节点的多条边自动累加）
    )  # 至此 entropies[i] = 节点 i 所有入边的 -p log p 之和（先存"和"，下一步再除以边数）
    counts = torch.zeros(num_nodes, device=attn_weights.device).index_add_(  # 同法统计每个目标节点的入边条数 (num_nodes,)
        0, target_nodes, torch.ones_like(attn_weights)  # 每条边贡献 1；ones_like 保证 shape/dtype/device 与权重一致
    )  # counts[i] = 节点 i 的入边数

    # (Optional) Only average over nodes with at least one incoming edge 丨 只统计有入边的节点，避免 0 边节点（熵未定义）污染均值
    mask = counts > 0  # 布尔掩码 (num_nodes,)：入边数>0 为 True
    entropies = entropies[mask] / counts[mask]  # 有效节点的"逐边平均熵"=熵之和÷边数（非标准香农熵，作监控指标用）
    return (  # 返回平均熵；三元表达式跨多行书写
        entropies.mean()  # 有效节点熵再取均值 → 标量张量
        if mask.any()  # 只要存在任一有入边的节点就走真分支
        else torch.tensor(0.0, device=attn_weights.device)  # 图完全无边时返回 0.0，并保持在同一设备（CPU/GPU）
    )  # return 括号闭合


# ── 类职责：PyG MessagePassing 软注意力层——本文件中真正执行"邻居加权聚合"的部件
# 输入：x 节点特征 (N,node_dim)；edge_index [源,目标] (2,E)；edge_attr 边特征 (E,edge_dim)
# 输出：聚合后节点特征 (N,out_dim) + 逐边注意力权重 (E,)；调用者=Attention.forward
# 教学点：加性注意力——query 来自目标节点、key/value 来自边特征（几何关系），
#         拼接后过 MLP 打分（区别于 g2anet.py 的 q·k 点积式），softmax 按目标节点分组
class GoalAttentionLayer(MessagePassing):  # 类定义：图软注意力层（继承 PyG MessagePassing）
    """
    Message-passing layer with learned attention over goal/edge features.

    This layer computes attention scores from concatenated node queries and
    transformed edge attributes, then aggregates value projections with 'add'
    aggregation.

    Args:
        node_dim (int): Dimensionality of node features.
        edge_dim (int): Dimensionality of edge attributes.
        out_dim (int): Output dimensionality for projected messages.
    """
    # ↑ docstring 原样保留

    # 构造函数：声明本层全部可学习子模块（q/k/v 三投影 + 打分 MLP）
    # node_dim=节点特征维；edge_dim=边特征维（本仓=10：7 几何+3 目标极坐标）；out_dim=消息输出维
    def __init__(self, node_dim, edge_dim, out_dim):  # 构造函数：声明 q/k/v 投影与打分 MLP
        super().__init__(aggr="add")  # Could use 'mean' or 'max' as well. 丨 调 PyG 基类并指定聚合方式=求和（也可换 mean/max；add 保序且梯度直达每条消息）
        self.q = torch.nn.Linear(node_dim, out_dim, bias=False)  # Q（query/查询）投影：把"我的状态"映射为查询向量；Linear=全连接层 y=xA^T+b，bias=False 去偏置（打分只看方向）
        self.k = torch.nn.Linear(edge_dim, out_dim, bias=False)  # K（key/键）投影：把边特征（我与邻居的几何关系）映射为"键"，与 query 配对打分
        self.v = torch.nn.Linear(edge_dim, out_dim)  # V（value/值）投影：边特征→"值"=真正被聚合的信息内容；带偏置
        self.attn_score_layer = nn.Sequential(  # 打分网络（加性注意力核心）：输入 q⊕k 拼接，输出每条边的未归一化分数
            nn.Linear(node_dim * 2, node_dim),  # 第一层全连接：q⊕k（各 out_dim，拼接后 2*out_dim）→ out_dim
            nn.ReLU(),  # ReLU 非线性：负值清零、正值保留，赋予打分网络非线性表达力
            nn.Linear(node_dim, 1),  # 第二层全连接：out_dim → 1，每条边压成一个标量分数
        )  # Sequential 结束：三段串成"拼接→隐层→打分"的 MLP 打分器
        self._last_attn_weights = None  # 缓存槽：forward 后存最近一次逐边注意力权重（detach 出图，仅供熵统计/日志）

    # 前向：只做两步——先算全体 q，再交给 propagate（PyG 自动回调 message/aggregate）
    # 输入 x (N,node_dim)、edge_index (2,E)、edge_attr (E,edge_dim)；输出 (聚合特征, 边权重)
    def forward(self, x, edge_index, edge_attr):  # 前向入口：算 q 后交给 propagate
        """
        Run attention-based message passing.

        Args:
            x (Tensor): Node features of shape (num_nodes, node_dim).
            edge_index (LongTensor): Edge indices of shape (2, num_edges)
                with format [source, target].
            edge_attr (Tensor): Edge attributes of shape (num_edges, edge_dim).

        Returns:
            tuple:
                out (Tensor): Updated node features of shape (num_nodes, out_dim).
                attn_weights (Tensor or None): Last per-edge softmax weights of
                    shape (num_edges,). None if no edges.
        """
        # ↑ docstring 原样保留
        q = self.q(x)  # 全部节点的查询向量：(N,node_dim) → (N,out_dim)
        out = self.propagate(edge_index, x=q, edge_attr=edge_attr)  # PyG 消息传递入口：内部按边 gather 出目标端特征 x_i→回调 self.message 算带权消息→按 index 聚合回节点；(N,out_dim)
        return out, self._last_attn_weights  # 返回聚合结果 + 缓存的逐边权重（供熵分析）

    # PyG 回调：逐边计算"消息"。x_i 是 PyG 按边自动切出的目标端特征（每条边一份）
    # 输入 x_i (E,out_dim)、edge_attr (E,edge_dim)、index 目标节点编号 (E,)
    # 返回每条边加权消息 (E,out_dim)；PyG 会自动按 index 聚合该返回值
    def message(self, x_i, edge_attr, index, ptr, size_i):  # PyG 回调：逐边打分+加权（注意力核心）
        """
        Compute per-edge messages using attention weights.

        Args:
            x_i (Tensor): Target-node queries for each edge, shape (num_edges, out_dim).
            edge_attr (Tensor): Edge attributes for each edge, shape (num_edges, edge_dim).
            index (LongTensor): Target node indices per edge, shape (num_edges,).
            ptr: Unused (PyG internal).
            size_i: Unused (PyG internal).

        Returns:
            Tensor: Per-edge messages of shape (num_edges, out_dim).
        """
        # ↑ docstring 原样保留
        k = F.leaky_relu(self.k(edge_attr))  # 边特征→键：(E,edge_dim)→(E,out_dim)；LeakyReLU=负半轴保留小斜率(默认0.01)而非清零，防"死神经元"
        v = F.leaky_relu(self.v(edge_attr))  # 边特征→值：(E,edge_dim)→(E,out_dim)；同样激活
        attention_input = torch.cat([x_i, k], dim=-1)  # 拼接"目标节点查询 x_i ⊕ 键 k"：(E,out_dim)⊕(E,out_dim)→(E,2*out_dim)，加性注意力的标准输入组装
        scores = self.attn_score_layer(attention_input).squeeze(-1)  # 打分 MLP：(E,2*out_dim)→(E,1)，squeeze 去末维→每条边一个标量分数 (E,)
        attn_weights = softmax(scores, index)  # index = target node index 丨 PyG 分组 softmax：同一目标节点的所有入边分数归一化为概率（组内和为 1）——这就是"按相关度给邻居分配权重"
        self._last_attn_weights = attn_weights.detach()  # 缓存权重并 detach 脱离计算图（不回传梯度，专供熵监控）
        return v * attn_weights.unsqueeze(-1)  # 加权消息：权重 (E,)→(E,1) 广播乘到值 (E,out_dim)；随后 PyG 按目标节点 add 聚合

    # PyG 回调：聚合。本实现直接透传父类（aggr='add' 求和），显式重写只为文档化
    # 输入逐边消息 (E,out_dim)+目标索引 (E,)；输出每节点收到的消息之和 (N,out_dim)
    def aggregate(self, inputs, index, ptr=None, dim_size=None):  # PyG 回调：按目标节点聚合消息
        """
        Aggregate messages per target node.

        Args:
            inputs (Tensor): Per-edge messages, shape (num_edges, out_dim).
            index (LongTensor): Target node indices per edge, shape (num_edges,).
            ptr: Unused (PyG internal).
            dim_size (int or None): Number of target nodes (optional).

        Returns:
            Tensor: Aggregated node features, shape (num_nodes, out_dim).
        """
        # ↑ docstring 原样保留
        return super().aggregate(inputs, index, ptr, dim_size)  # 委托父类执行 add 聚合：等价于按 index 做 scatter-add


# ── 类职责：IGA 主模块——硬注意力门控筛邻居（建稀疏图）+ 图软注意力加权聚合 + 两层解码
# 输入：embedding (B,N,D≥11)（位置/朝向/体感特征/动作/目标按序拼接）；输出六元组（见下 docstring）
# 调用者：上游 MARL 算法网络（编码每个机器人的局部观测）；核心产物 att_embedding (B*N,2*emb)
# 教学点：与 g2anet.py 同源（hard_mlp/q/k/v 结构几乎复制），但硬门控在此是"建边过滤
#         器"、软注意力换成 GoalAttentionLayer 图消息传递（非稠密点积），解码两层
class Attention(nn.Module):  # 类定义：IGA 主模块（硬门控建边 + 图软注意力 + 解码）
    """
    Multi-robot attention mechanism combining hard (binary) and soft (weighted) attentions.

    The module encodes agent features, derives pairwise geometric edge attributes,
    computes hard attention masks and soft attention weights, performs message passing,
    and decodes concatenated self/attended embeddings.

    Args:
        embedding_dim (int): Dimension of the agent embedding vector.

    Attributes:
        embedding1 (nn.Linear): First layer for agent feature encoding.
        embedding2 (nn.Linear): Second layer for agent feature encoding.
        hard_mlp (nn.Sequential): MLP over concatenated node/edge features for hard attention.
        hard_encoding (nn.Linear): Outputs logits for binary attention (2 classes).
        q (nn.Linear): Query projection for soft attention.
        k (nn.Linear): Key projection from edge features for soft attention.
        v (nn.Linear): Value projection from edge features for soft attention.
        attn_score_layer (nn.Sequential): Computes unnormalized scores for soft attention.
        decode_1 (nn.Linear): First decoder layer for concatenated embeddings.
        decode_2 (nn.Linear): Second decoder layer for concatenated embeddings.
        message_graph (GoalAttentionLayer): Graph attention/message-passing layer.
        node_update (nn.Sequential): Optional node-update MLP (unused in forward aggregation).
    """
    # ↑ docstring 原样保留

    # 构造函数：逐个声明子模块（编码器/图注意力层/硬门控/软注意力投影/解码器）
    # embedding_dim=每个智能体最终嵌入维度（决定后续所有投影宽度）
    def __init__(self, embedding_dim):  # 构造函数：声明全部子模块
        """
        Initialize the attention module.

        Args:
            embedding_dim (int): Output embedding dimension per agent.
        """
        # ↑ docstring 原样保留
        super(Attention, self).__init__()  # 初始化 nn.Module 基类（注册参数/子模块所必需）
        self.embedding_dim = embedding_dim  # 记录嵌入维度，forward 中多处 reshape/视图要用

        self.node_update = nn.Sequential(  # 节点更新 MLP（残留模块）：两层全连接。注意：forward 里并未调用它，属"预留未用"代码
            nn.Linear(embedding_dim * 2, embedding_dim),  # 第一层：2*emb → emb（预期输入=自身⊕聚合的拼接）
            nn.LeakyReLU(),  # LeakyReLU 激活：负值保留 1% 斜率
            nn.Linear(embedding_dim, embedding_dim),  # 第二层：emb → emb
            nn.LeakyReLU(),  # 再次激活
        )  # node_update 定义结束（当前 forward 未使用）

        self.message_graph = GoalAttentionLayer(  # 图注意力层实例：软注意力消息传递真正发生的地方（本文件的核心算子）
            node_dim=embedding_dim, edge_dim=10, out_dim=embedding_dim  # 节点=嵌入维、边=10 维（7 几何+3 目标极坐标）、输出=嵌入维
        )  # message_graph 定义结束

        self.embedding1 = nn.Linear(5, 128)  # 编码器第一层：5 维原始体感特征 → 128 维（先升维再压缩，增大表达容量）
        nn.init.kaiming_uniform_(self.embedding1.weight, nonlinearity="leaky_relu")  # Kaiming(He) 均匀初始化：按激活函数增益设定方差，让信号方差不随深度爆炸/消失（深度网络训练稳定的关键）
        self.embedding2 = nn.Linear(128, embedding_dim)  # 编码器第二层：128 → embedding_dim
        nn.init.kaiming_uniform_(self.embedding2.weight, nonlinearity="leaky_relu")  # 同上 Kaiming 初始化

        # Hard attention MLP with distance 丨 硬注意力主干：输入"我的嵌入 ⊕ 7 维边几何"，输出中间表示
        self.hard_mlp = nn.Sequential(  # 硬注意力 MLP 开始
            nn.Linear(embedding_dim + 7, embedding_dim),  # (emb+7) → emb；7=距离1+相对角cos/sin2+对方朝向cos/sin2+动作2
            nn.ReLU(),  # ReLU 非线性
            nn.Linear(embedding_dim, embedding_dim),  # emb → emb（硬注意力 MLP 第二层全连接）
        )  # hard_mlp 结束
        self.hard_encoding = nn.Linear(embedding_dim, 2)  # 输出 2 类 logits：[不关注, 关注]——二分类决定是否把该邻居建为图边（logit=softmax 前的未归一化分数）

        # Soft attention projections 丨 软注意力投影。注意：本类自带的 q/k/v/attn_score_layer 在 forward 中并未真正使用——实际计算在 message_graph 内部，这些是自 g2anet 复制来的"残留权重"
        self.q = nn.Linear(embedding_dim, embedding_dim, bias=False)  # query 投影（未使用）
        self.k = nn.Linear(10, embedding_dim, bias=False)  # key 投影：10 维边特征→嵌入维（未使用）
        self.v = nn.Linear(10, embedding_dim)  # value 投影（未使用）

        # Soft attention score network (with polar other robot goal position) 丨 打分网络定义（同上未使用；真正打分在 GoalAttentionLayer.attn_score_layer）
        self.attn_score_layer = nn.Sequential(  # Sequential 开始（未使用）
            nn.Linear(embedding_dim * 2, embedding_dim),  # 2*emb → emb（未使用）
            nn.ReLU(),  # ReLU（未使用）
            nn.Linear(embedding_dim, 1),  # emb → 1 标量分数（未使用）
        )  # Sequential 结束（未使用）

        # Decoder 丨 解码器：把"自身嵌入 ⊕ 邻居聚合嵌入"映射为最终输出嵌入
        self.decode_1 = nn.Linear(embedding_dim * 2, embedding_dim * 2)  # 解码第一层：2*emb → 2*emb
        nn.init.kaiming_uniform_(self.decode_1.weight, nonlinearity="leaky_relu")  # Kaiming 初始化
        self.decode_2 = nn.Linear(embedding_dim * 2, embedding_dim * 2)  # 解码第二层：2*emb → 2*emb（g2anet 只有单层 decoding）
        nn.init.kaiming_uniform_(self.decode_2.weight, nonlinearity="leaky_relu")  # Kaiming 初始化

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
        embed = F.leaky_relu(self.embedding1(embed))  # 第一层+LeakyReLU：(B*N,5) → (B*N,128)
        embed = F.leaky_relu(self.embedding2(embed))  # 第二层+LeakyReLU：(B*N,128) → (B*N,emb)
        return embed  # 返回编码后的嵌入

    # 前向主流程：①切特征 ②算成对几何 ③硬门控采样 ④软注意力建图消息传递 ⑤拼接解码
    # 输入 (B,N,D≥11)；输出六元组 att_embedding/hard_logits/距离/熵/硬权重/组合权重
    def forward(self, embedding):  # 前向主入口：两阶段注意力全流程
        """
        Compute hard and soft attentions and produce attended embeddings.

        Args:
            embedding (Tensor): Input tensor of shape (B, N, D), where D ≥ 11. The first
                channels are expected to include position (x,y), heading (cos,sin),
                agent features for encoding, action, and goal.

        Returns:
            tuple:
                att_embedding (Tensor): Attended embedding, shape (B*N, 2*embedding_dim).
                hard_logits (Tensor): Logits for hard attention (keep class index 1),
                    shape (B*N, N-1).
                unnorm_rel_dist (Tensor): Unnormalized pairwise distances, shape (B*N, N-1, 1).
                mean_entropy (Tensor): Scalar mean entropy of soft attention per batch.
                hard_weights (Tensor): Binary hard attention mask, shape (B, N, N).
                comb_w (Tensor): Combined soft weights per (receiver, sender),
                    shape (N, N*(N-1)).
        """
        # ↑ docstring 原样保留（其 N-1 形状描述沿袭 g2anet；本实现未剔自对角线，实际为 N）
        if embedding.dim() == 2:  # 兼容单场景输入：若调用方没给 batch 维则按 B=1 处理
            embedding = embedding.unsqueeze(0)  # (N,D) → (1,N,D)：补上 batch 维
        batch_size, n_agents, _ = embedding.shape  # 解包维度：批大小 B、智能体数 N（特征维 D 弃用）

        # Extract sub-features 丨 按"魔法切片"从拼接大向量取各物理量：D=[x,y, cosθ,sinθ, 5维特征(4:9), 动作(7:9), 目标(-2:)]
        embed = embedding[:, :, 4:9].reshape(batch_size * n_agents, -1)  # 取 5 维体感特征并压平 batch：(B,N,5) → (B*N,5)
        position = embedding[:, :, :2].reshape(batch_size, n_agents, 2)  # 位置 (x,y)：(B,N,2)
        heading = embedding[:, :, 2:4].reshape(  # 取朝向 (cosθ,sinθ)：角度用 cos/sin 成对编码可避免 ±π 周期跳变，(B,N,2)
            batch_size, n_agents, 2  # 重塑为 (B,N,2)
        )  # assume (cos(θ), sin(θ)) 丨 原注释：假定该 2 维顺序为 (cosθ, sinθ)
        action = embedding[:, :, 7:9].reshape(batch_size, n_agents, 2)  # 最近动作 (2 维)：作为"对方在做什么"的意图线索进入边特征
        goal = embedding[:, :, -2:].reshape(batch_size, n_agents, 2)  # 目标点 (x,y)：取最后 2 维，(B,N,2)

        # Compute pairwise relative goal vectors (for each i,j) 丨 对每个有序对 (i,j)：j 的目标相对 i 的位置——刻画"j 想去哪"（IGA 的意图通道）
        goal_j = goal.unsqueeze(1).expand(-1, n_agents, -1, -1)  # goal (B,N,2)→unsqueeze(1)→(B,1,N,2)→expand→(B,N,N,2)：第 3 维=j 的目标广播给每个 i
        pos_i = position.unsqueeze(2)  # position (B,N,2)→(B,N,1,2)：第 2 维=i 的位置，准备广播相减
        goal_rel_vec = goal_j - pos_i  # 广播减法：(B,N,N,2)，goal_rel_vec[b,i,j]=j 的目标 − i 的位置

        # Encode agent features 丨 5 维原始特征 → 高维嵌入（embedding=把低维/原始输入映射为稠密向量，便于网络提取模式）
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

        # Broadcast agent embedding for all pairs (except self-pairs) 丨 把我的嵌入广播给全部 j（自对角线由下方"i≠j 才建边"天然排除）
        h_i_expanded = h_i.expand(-1, -1, n_agents, -1)  # (B,N,1,D) → (B,N,N,D)；expand=零拷贝广播视图

        h_i_flat = h_i_expanded.reshape(  # 压平 batch 维供 MLP 批处理
            batch_size * n_agents, n_agents, self.embedding_dim  # → (B*N, N, D)：压平后每行对应一个 (b,i)，含全部 j
        )  # reshape 完成
        edge_flat = edge_features.reshape(batch_size * n_agents, n_agents, -1)  # → (B*N, N, 7)：边特征同样压平

        # Concatenate agent embedding and edge features 丨 硬注意力输入 = 我的嵌入 ⊕ 边几何
        hard_input = torch.cat([h_i_flat, edge_flat], dim=-1)  # → (B*N, N, D+7)：每行=「我是谁 + 对面那位与我什么关系」

        # Hard attention forward 丨 硬注意力前向：对每个有序对输出"关注/不关注"概率
        h_hard = self.hard_mlp(hard_input)  # MLP 提特征：(B*N, N, D+7) → (B*N, N, D)
        hard_logits = self.hard_encoding(h_hard)  # 线性层出 2 类 logits：(B*N, N, 2)
        hard_weights = F.gumbel_softmax(hard_logits, hard=False, tau=0.2, dim=-1)[  # Gumbel-Softmax 采样：给 logits 加 Gumbel 噪声再做温度 softmax，等价"从二分类分布采样"；tau=0.2 低温→分布尖锐接近 one-hot；hard=False→返回软样本（保持可微，梯度能回传）
            ..., 1  # 取"关注"类（index=1）的概率 → (B*N, N)
        ].unsqueeze(2)  # 补回末维 → (B*N, N, 1)
        hard_weights = hard_weights.view(batch_size, n_agents, n_agents)  # 恢复 batch：(B,N,N)，hard_weights[b,i,j]=i 对 j 的关注概率

        unnorm_rel_dist = torch.linalg.vector_norm(rel_vec, dim=-1, keepdim=True)  # 未归一化的成对距离 (B,N,N,1)（备份返回给上游，供奖励/日志使用）
        unnorm_rel_dist = unnorm_rel_dist.reshape(batch_size * n_agents, n_agents, 1)  # → (B*N, N, 1)：距离张量压平

        # ---- Soft attention computation ---- 丨 软注意力段：先造目标极坐标边特征，再逐 batch 建图做消息传递
        q = self.q(agent_embed).reshape(batch_size * n_agents, -1)  # 算 query 并压平 (B*N,emb)。注意：此 q 后续并未被使用（真正 query 在 message_graph 内重算）——自 g2anet 迁移的残留计算

        attention_outputs = []  # 收集每个 batch 场景的聚合结果
        entropy_list = []  # 收集每个 batch 的注意力熵
        combined_w = []  # 收集每个 batch 的稠密组合权重矩阵

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
        soft_edge_features = torch.cat([edge_features, goal_polar], dim=-1)  # → (B,N,N,10)，与 message_graph 的 edge_dim=10 对齐

        attn_outputs = []  # 本地列表（与 attention_outputs 同义，逐 batch 填充——复制同源的命名痕迹）

        for b in range(batch_size):  # 逐 batch 场景处理：每个场景独立建图（硬门控决定的边集各不相同）
            edge_index_list = []  # 边列表：元素 [j,i] 表示 j→i（源→目标）
            edge_attr_list = []  # 与边一一对应的 10 维特征列表

            # Agent embeddings for this scenario 丨 取本场景的各张量子集
            node_feats = agent_embed[b]  # [n, emb_dim] 丨 本场景节点特征
            soft_feats = soft_edge_features[b]  # [n, n, edge_dim] 丨 本场景成对边特征（索引 [接收者,发送者]）
            hard_mask = hard_weights[b]  # [n, n] 丨 本场景硬门控概率矩阵

            # Only build edges where hard attention mask is active, no self-loops 丨 硬门控的实际作用点：只给"关注概率>0.5 的非自身对"建边——把稠密全图剪成稀疏图（与 g2anet 的乘法掩码路径根本不同）
            for i in range(n_agents):  # 遍历接收者 i（谁在看）
                for j in range(n_agents):  # 遍历发送者 j（看谁）
                    if i != j and hard_mask[i, j] > 0.5:  # 排除自环 + 硬门控阈值判定（0.5 二值化）
                        edge_index_list.append([j, i])  # from j (src) to i (tgt) 丨 记边 j→i
                        edge_attr_list.append(soft_feats[i, j])  # 该边的 10 维特征（行=接收者 i，列=发送者 j）

            # Edge tensors 丨 列表 → PyG 张量；空图分支保证零边时不崩溃
            if edge_index_list:  # 至少有一条通过硬门控的边
                edge_index = torch.tensor(  # 边索引转张量
                    edge_index_list, dtype=torch.long, device=embedding.device  # long 型（PyG 要求）、放同一设备（CPU/GPU）
                ).t()  # [2, num_edges] 丨 转置成 PyG 约定格式：第 0 行=源、第 1 行=目标
                edge_attr = torch.stack(edge_attr_list, dim=0)  # [num_edges, edge_dim] 丨 边特征沿新维度堆叠
            else:  # 空图兜底（所有邻居都被硬门控剪掉时）
                edge_index = torch.zeros(  # 空边索引 (2,0)
                    (2, 0), dtype=torch.long, device=embedding.device  # 形状/类型/设备与正常分支一致
                )  # 空索引构造完成
                edge_attr = torch.zeros(  # 空边特征 (0, edge_dim)
                    (0, soft_feats.shape[-1]),  # 特征维取自 soft_feats 末维（=10）
                    dtype=soft_feats.dtype,  # dtype 对齐
                    device=embedding.device,  # 设备对齐
                )  # 空特征构造完成

            # Message passing: edge-to-node aggregation only 丨 核心：在稀疏图上跑软注意力消息传递（q/k/v 打分→分组 softmax→加权和→按目标 add 聚合）
            attn_out, attn_weights = self.message_graph(  # 调 GoalAttentionLayer
                node_feats, edge_index, edge_attr  # 节点特征 + 边结构 + 边特征
            )  # [n, embedding_dim] 丨 返回聚合后节点特征 (N,emb) 与逐边权重 (E,)
            attn_outputs.append(attn_out)  # 收集本场景聚合结果
            batch_entropy = entropy_from_attention(  # 计算本场景平均注意力熵
                attn_weights, edge_index[1], num_nodes=n_agents  # 逐边权重 + 目标节点索引（edge_index[1]=目标行）
            )  # 熵计算完成
            entropy_list.append(batch_entropy)  # 收集熵

            combined_weights = torch.zeros(  # 把稀疏边权重摊回稠密 N×N 矩阵（0=无边/未选中）
                (n_agents, n_agents), device=attn_weights.device  # 形状 (N,N)、与权重同设备
            )  # 全零矩阵构造完成
            for idx in range(edge_index.shape[1]):  # 遍历每条边
                j = edge_index[0, idx].item()  # sender/source 丨 取发送者 j（第 0 行）
                i = edge_index[1, idx].item()  # receiver/target 丨 取接收者 i（第 1 行）
                combined_weights[i, j] = attn_weights[idx]  # 填入稠密矩阵（行=接收者 i，列=发送者 j）
            combined_w.append(combined_weights)  # 收集本场景稠密权重

        # Re-stack results for full batch (shape: [batch_size, n_agents, embedding_dim]) 丨 各场景结果重新堆叠回完整 batch
        attn_stack = torch.stack(attn_outputs, dim=0).reshape(batch_size * n_agents, -1)  # (B,N,emb) → 压平 (B*N,emb)
        self_embed = agent_embed.reshape(batch_size * n_agents, -1)  # 自身嵌入 (B*N,emb)——保底信息，不依赖任何邻居

        # Concat original + attended for each agent 丨 MARL 注意力输出的标准组装：自身嵌入 ⊕ 邻居加权聚合嵌入
        concat_embed = torch.cat(  # 沿特征维拼接
            [self_embed, attn_stack], dim=-1  # (B*N,emb) ⊕ (B*N,emb) → (B*N,2*emb)：自身与聚合嵌入拼接
        )  # [batch, n, 2*embedding_dim] 丨 原注释按 batch 结构描述；张量实际已压平为 B*N 行

        x = F.leaky_relu(self.decode_1(concat_embed))  # 解码第一层+LeakyReLU：(B*N,2*emb) → (B*N,2*emb)
        att_embedding = F.leaky_relu(self.decode_2(x))  # 解码第二层+LeakyReLU：(B*N,2*emb) → (B*N,2*emb) 最终嵌入
        mean_entropy = torch.stack(entropy_list).mean()  # 全 batch 平均熵（标量，监控/熵正则用）
        comb_w = torch.stack(combined_w, dim=1).reshape(n_agents, -1)  # 稠密权重堆叠变形 (N, B*N)：每行一个接收者、列展开所有 batch 的发送者

        return (  # 返回六元组（跨行书写；注意实际形状与 docstring 有出入，以注释为准）
            att_embedding,  # ① 最终注意力嵌入 (B*N,2*emb)：喂给下游 Q 网络/策略网络
            hard_logits[..., 1],  # ② 硬注意力"关注"类 logit (B*N,N)：供上游做辅助损失（教模型学会选邻居）；docstring 写 N-1 系沿袭 g2anet
            unnorm_rel_dist,  # ③ 未归一化成对距离 (B*N,N,1)
            mean_entropy,  # ④ 平均注意力熵（标量）
            hard_weights,  # ⑤ 硬门控概率 (B,N,N)
            comb_w,  # ⑥ 稠密软注意力权重 (N, B*N)
        )  # return 结束
