# ============================================================================ #
# 【文件】SAC 工具箱——供 actor/critic 与 SAC.py 复用的基础设施：
# 目标网络软更新（soft_update_params）、全局随机种子、目录创建、正交权重初始化、
# MLP 工厂（mlp/MLP）、张量转 NumPy（to_np）。
# ============================================================================ #
import numpy as np  # NumPy：随机种子设置、to_np 的返回类型
import torch  # PyTorch：随机种子与张量
from torch import nn  # 神经网络基类：Linear 层的判别与初始化
from torch import distributions as pyd  # 分布库——本文件未直接使用（仓内也无 utils.pyd 引用，属冗余 import）
import torch.nn.functional as F  # 函数式算子——本文件未直接使用（冗余 import）
import os  # 路径拼接与建目录
from collections import deque  # 双端队列——本文件未直接使用（冗余 import）
import random  # Python 内建随机源（设种子用）
import math  # 数学库——本文件未直接使用（冗余 import）


# 职责：目标网络的软更新（Polyak 平均）——SAC.py 每次更新 critic 后调用一次。
# 目标网络：critic 的一份慢速副本，用来算 TD 学习目标；目标若随主网剧变，
# 就像追移动靶，训练易震荡。★软更新 vs 硬拷贝：硬拷贝每隔 N 步 100% 覆盖、
# 目标阶梯式跳变；软更新每步只挪 τ 比例（tau=0.005→每步吸收 0.5% 新参），平滑滞后更稳。
# 输入：net=主网络（新参来源）、target_net=目标网络（就地更新）、tau∈(0,1) 插值系数。
def soft_update_params(net, target_net, tau):  # 无返回值：直接改写 target_net 的参数
    """
    Perform a soft update of the parameters of the target network.

    Args:
        net (nn.Module): Source network whose parameters are used for updating.
        target_net (nn.Module): Target network to be updated.
        tau (float): Interpolation parameter (0 < tau < 1) for soft updates.
                     A value closer to 1 means faster updates.
    """
    # zip 按参数注册顺序逐个配对两网的参数（结构必须完全一致，否则会错位更新）
    for param, target_param in zip(net.parameters(), target_net.parameters()):
        # 就地写回插值结果：target ← τ·net + (1−τ)·target（逐元素）。
        # 走 .data 直接改值绕过 autograd——目标网络只是"权重容器"，自身不需要梯度。
        target_param.data.copy_(tau * param.data + (1 - tau) * target_param.data)


# 职责：统一固定 NumPy / random / PyTorch（含 CUDA）四处随机源，保证实验可复现。
# 输入：seed 整数；无返回；在训练脚本入口调用一次。
def set_seed_everywhere(seed):  # 同种子 → 同初始化 → 同采样序列
    """
    Set random seed for reproducibility across NumPy, random, and PyTorch.

    Args:
        seed (int): Random seed.
    """
    torch.manual_seed(seed)  # 固定 PyTorch CPU 随机源：权重初始化、采样等
    if torch.cuda.is_available():  # 有 GPU 才需要额外固定 CUDA 侧随机源
        torch.cuda.manual_seed_all(seed)  # 固定所有可见 GPU 设备的种子
    np.random.seed(seed)  # 固定 NumPy 随机源（环境噪声/数据采样等）
    random.seed(seed)  # 固定 Python 内建 random 随机源


# 职责：目录不存在则创建、已存在则静默跳过（幂等），返回路径字符串。
# 输入：任意个路径片段（*path_parts）；输出：拼接后的完整路径。
def make_dir(*path_parts):  # 训练脚本用它建模型/日志输出目录
    """
    Create a directory if it does not exist.

    Args:
        *path_parts (str): Components of the path to be joined into the directory.

    Returns:
        str: The full path of the created or existing directory.
    """
    dir_path = os.path.join(*path_parts)  # 拼接片段成完整路径，如 ("runs","exp1")→"runs/exp1"
    try:  # 容错创建：目录已存在时 os.mkdir 会抛异常
        os.mkdir(dir_path)  # 创建单级目录
    except OSError:  # 捕获"目录已存在"等 OS 错误
        pass  # 直接吞掉——保证重复调用无副作用（幂等）
    return dir_path  # 返回路径供调用方继续使用


# 职责：权重初始化回调，配 nn.Module.apply() 递归刷遍所有子层。
# 输入：m=单个子模块；无返回（原地改权重）。规则：Linear 正交初始化 + 偏置清零。
# 为什么正交初始化：各层输出方差保持约 1，深网前向信号不爆炸不衰减。
def weight_init(m):  # apply() 的回调签名：每次接收一个子模块
    """
    Custom weight initialization for layers.

    Applies orthogonal initialization to Linear layers and zero initialization to biases.

    Args:
        m (nn.Module): Layer to initialize.
    """
    if isinstance(m, nn.Linear):  # 只处理全连接层（ReLU 无参数，无需处理）
        nn.init.orthogonal_(m.weight.data)  # 正交初始化：行向量互相正交、范数为 1
        if hasattr(m.bias, "data"):  # 防御：个别层 bias 可能为 None
            m.bias.data.fill_(0.0)  # 偏置清零：初始零点对称，不引入先验偏移


# ============================== 类：MLP ============================== #
# 职责：函数式 mlp() 的 nn.Module 包装——构造即建网、即正交初始化，开箱即用。
# 输入：x (batch, input_dim)；输出：(batch, output_dim)。隐藏层 ReLU，输出层无激活。
class MLP(nn.Module):  # 标准 PyTorch 模块；actor/critic 也可直接用函数版 mlp()
    """
    Multi-layer perceptron (MLP) with configurable depth and optional output activation.

    Args:
        input_dim (int): Number of input features.
        hidden_dim (int): Number of hidden units in each hidden layer.
        output_dim (int): Number of output features.
        hidden_depth (int): Number of hidden layers.
        output_mod (nn.Module, optional): Optional output activation module (e.g., Tanh, Sigmoid).
    """

    # 构造：主体网络交给 mlp() 搭建，再整体 apply 做正交初始化。
    def __init__(  # 构造函数：参数较多，按 PEP8 行宽拆多行书写
        self, input_dim, hidden_dim, output_dim, hidden_depth, output_mod=None  # 五个维度/结构参数，含义见类 docstring
    ):  # 形参列表结束
        super().__init__()  # 初始化 nn.Module 基类
        # 主体：函数式 mlp() 返回的 Sequential（Linear→ReLU→…→Linear[→output_mod]）
        self.trunk = mlp(input_dim, hidden_dim, output_dim, hidden_depth, output_mod)
        self.apply(weight_init)  # 递归正交初始化 trunk 里的每个 Linear

    # 前向：直通 trunk；本类不添加任何额外计算。
    def forward(self, x):  # MLP(x) 即调用；(batch,input_dim)→(batch,output_dim)
        """
        Forward pass through the MLP.

        Args:
            x (Tensor): Input tensor of shape (batch_size, input_dim).

        Returns:
            Tensor: Output tensor of shape (batch_size, output_dim).
        """
        return self.trunk(x)  # Sequential 按序过每层


# 职责：MLP 工厂——按 hidden_depth 拼装 nn.Sequential，actor/critic/MLP 三方共用。
# 结构：[Linear(in,hidden)+ReLU]×depth → Linear(hidden,out) [+output_mod]。
# hidden_depth=0 时退化为单层线性映射（无隐藏层、无激活）。
def mlp(input_dim, hidden_dim, output_dim, hidden_depth, output_mod=None):  # 返回拼好的 nn.Sequential
    """
    Create an MLP as a `nn.Sequential` module.

    Args:
        input_dim (int): Input feature dimension.
        hidden_dim (int): Hidden layer size.
        output_dim (int): Output feature dimension.
        hidden_depth (int): Number of hidden layers.
        output_mod (nn.Module, optional): Output activation module.

    Returns:
        nn.Sequential: The constructed MLP.
    """
    if hidden_depth == 0:  # 特例：零隐藏层=线性模型（无 ReLU）
        mods = [nn.Linear(input_dim, output_dim)]  # 仅一层：in→out
    else:  # 常规：至少一层隐藏层
        mods = [nn.Linear(input_dim, hidden_dim), nn.ReLU(inplace=True)]  # 首层 in→hidden + ReLU（inplace 原地激活省显存）
        for i in range(hidden_depth - 1):  # 再叠 depth−1 个隐藏块
            mods += [nn.Linear(hidden_dim, hidden_dim), nn.ReLU(inplace=True)]  # 每块 hidden→hidden + ReLU
        mods.append(nn.Linear(hidden_dim, output_dim))  # 输出层 hidden→out；不加激活——μ/logσ/Q 值都要无界输出
    if output_mod is not None:  # 可选输出激活（本仓 actor/critic 均不传）
        mods.append(output_mod)  # 挂在末尾，如 nn.Tanh() 可直接约束输出范围
    trunk = nn.Sequential(*mods)  # 打包成顺序容器：调用时按序前向
    return trunk  # 返回组装好的网络


# 职责：PyTorch 张量 → NumPy 数组（搬回 CPU + 脱离计算图）。
# 输入：t 张量或 None；输出：ndarray / None / 空数组。
# 典型用途：SAC.act() 把动作张量转回 numpy 再喂环境（仿真器不吃 torch 张量）。
def to_np(t):  # torch 世界 → numpy/环境 世界的桥
    if t is None:  # None 透传
        return None  # 调用方按无值处理
    elif t.nelement() == 0:  # 空张量特判（元素数为 0）
        return np.array([])  # 返回空 NumPy 数组
    else:  # 正常张量
        return t.cpu().detach().numpy()  # 三连：搬回 CPU → 脱离 autograd → 转 ndarray
