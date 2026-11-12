# 精讲一：mLSTM 乘性单元与显式 RNN 后端

## 角色定位

model/RNN_utils/RNN/ 是论文主模型的物理落点：情感神经元诞生在 mLSTMRNNCell 的 4096 维单元状态里。这一目录自成一个微型框架——cells.py 提供 LSTM/GRU/Tanh/ReLU/mLSTM 四类单元（models.py:9-14 的 _rnn_impls 把前三类映射到 ATen 融合核 _VF.*_cell），RNNBackend.py 提供显式 Python 时间步循环的 stackedRNN/bidirectionalRNN 容器，model/model.py:20 用 `getattr(RNN, rnn_type)` 按字符串装配——`--model mLSTM` 一路落到 models.py:59 的 mLSTM 工厂。

## 内部结构

mLSTMRNNCell（cells.py:13）在标准 RNNCell 骨架（RNNBackend.py:245，gate_multiplier=4，cells.py:19）之上多注册两组参数 w_mih/w_mhh（cells.py:22-23）。计算核心 mLSTMCell（cells.py:56）：先算乘性交互 `m = F.linear(input, w_mih) * F.linear(hidden[0], w_mhh)`（cells.py:63），即 m_t=(W_mi·x_t)⊙(W_mh·h_{t-1})；CUDA 路径把 (m, c) 直接喂 `_VF.lstm_cell`（cells.py:65-66）——mLSTM 等价于"递归输入换成 m 的标准 LSTM"，可复用融合核；CPU 路径手工展开四门（cells.py:70-81，cy=(f⊙c)+(i⊙g) 在 :80）。stackedRNN（RNNBackend.py:100）逐时间步、逐层推进（:144-151），层的输入是上一层输出元组的第 0 位（:158）；RNNCell.init_hidden 惰性建零状态（RNNBackend.py:327-345），输出投影 w_ho 仅在 output_size≠hidden_size 时存在（:274-275）。

## 外部连接

上游是 model/model.py 的两个消费者：训练用 RNNModel（:12，encoder+decoder 包 rnn），探测用 RNNFeaturizer（:61，逐时间步 collect_hidden=True 调用 :89-91）；generate.py:131 直接伸手进 `model.rnn.rnns[-1].hidden` 取最后层状态改写神经元。forward 签名带 reset_mask：stackedRNN 每步先按掩码把越界样本的隐状态清零（RNNBackend.py:145-146，乘法实现 `hidden*(1-reset_mask)` 在 :358），保证一个 batch 内多条样本互不渗漏。

## 数据流

单步：input[seq] → 各层 cell 依序推进 → 每层返回 (h,c) 元组。批量后 hidden 的形状约定写在 stackedRNN 文档串（RNNBackend.py:124-131）：list[hidden_states][seq][layer]。RNNModel.forward 每次先 detach_hidden（model/model.py:39，RNNBackend.py:365-373 逐状态 detach）——这就是截断 BPTT：隐藏值跨 batch 延续、梯度图每批切断。RNNFeaturizer.get_features 再从 hidden[1]（cell）取最末层（model/model.py:158-168），交给逻辑回归当 4096 维特征。

## 设计决策

其一，放弃 cudnn 融合而用显式 Python 循环，是为了三个 cudnn 给不了的能力：自定义 mLSTM 单元、逐时间步 reset_mask 边界重置、collect_hidden 取全程状态；代价是 pretrain.py:292 直接 `torch.backends.cudnn.enabled = False`。其二，乘性单元的理论动机：m_t 的外积式耦合让单元状态可达秩随输入维度增长，长程依赖更易保持——这正是 4096 维大单元里浮现单一情感编码神经元的架构前提。其三，w_mih/w_mhh 默认 bias=False（cells.py:18），门偏置由 b_ih/b_hh 统一承担。其四，reset_parameters 用 uniform(-1/sqrt(hidden), ...)（RNNBackend.py:304-310），xavier 版本被注释弃用（:312-326）。

## 新人提示

先读 cells.py 全文 84 行——它可能是全仓密度最高的文件；再读 RNNBackend.py:124-131 的张量格式注释，否则 get_features 的三重索引（model/model.py:160-168）看不懂。三个雷：工厂 Tanh 函数连续构造两次且第二行引用未定义的 RNNTanhCell（models.py:55-56），`--model Tanh` 必 NameError；models.py:63 残留 `print("Creating mlstm")`，日志里看见别惊讶；改隐状态逻辑时记得 detach 在 model.py:39 而非后端内——别在循环里重复 detach 把跨批记忆也断了。
