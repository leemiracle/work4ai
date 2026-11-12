# 02 · GRU 重建：把 RNN 循环展开成 DLA 卷积积木

> 文件：`operators/op_reconstruction/GRU.py`（508 行，全仓最复杂）
> 图谱层：L07 | tour 步：T09

## 角色定位

GRU 是门控循环网络：每个时间步要做三个门（更新门 z/重置门 r/新记忆 h̃）的线性变换加逐元素门控。DLA 没有任何循环原语，也没有 Sigmoid/Tanh 之外的"循环感知"能力——这个文件证明**只要循环长度已知，RNN 就是有限个 Conv+ElementWise 的展开**。它是 op_reconstruction 复杂度天花板，也是"重建"二字最极端的注脚。

## 内部结构

类 `GRU`（GRU.py:31）20 个方法分四组：

- **搭积木静态方法**：`add_gru_conv`（GRU.py:97，线性变换 W·x 与 U·h 都用 Conv 表达）、`add_gru_act`（GRU.py:126，Sigmoid/Tanh）、`add_gru_elementwise`（GRU.py:118，门控 Mul/Add）、`add_gru_transpose`/`add_gru_slice`/`add_gru_const_op`/`from2dto4d`（GRU.py:93，DLA 要 NCHW 四维）；
- **展开引擎**：`reconstruct_step`（GRU.py:176）搭单时间步的 z/r/h̃ 门控与隐状态更新，`reconstruct`（GRU.py:289）循环 total_steps 次把整条序列铺平；
- **自洽测试**：`onnx_inference`（GRU.py:350，带 prev_output 的迭代推理）、`insert_transpose`（GRU.py:372）、`patch_gru_layout`（GRU.py:395）、`run_comparison`（GRU.py:413）、`test_config`（GRU.py:456）。

## 外部连接

继承 `Operator` 基类，import `onnxruntime_utils`；经 `op_reconstruction/__init__.py` barrel 进 `registry.py:21` 注册表，被 `test.py` 回归。唯一浮点容差豁免：`MAXABSDIFF_THRESHOLDS['GRU'] = 1e-6`（test.py:23），其余算子都是 0.0。

## 数据流

原始 GRU 节点（输入 X 序列 + 初始 H）→ qualify 检查 → 逐步：X 按时间切片（add_gru_slice）→ Conv(W·x_t)+Conv(U·h_{t-1}) → Sigmoid 门 → 逐元素 Mul/Add 组合出 h_t → 拼回输出序列。每一步产物都是 gs.Node，最终整张图无 GRU 节点，`verify_reconstruction` 断言通过。

## 设计决策

- **Conv 表达线性变换**：W·x 本是 MatMul，但 DLA 的 Conv 吞吐/能效远优于 MatMul 路径，重排成 1×1 Conv 是核心决策；
- **容差 1e-6 的诚实**：门控是乘加链组合，浮点结合顺序改变引入 ULP 级差异，框架不假装位级等价而是显式放宽并写进阈值表——量化工程序里这种"诚实标注"比硬撑 0.0 更有价值；
- **test_config 多配置回归**：hidden_size/num_iterations 参数化，防单点形状过拟合。

## 新人提示

不要顺着 508 行线性读。先读 `reconstruct`（GRU.py:289）看主循环怎么调 `reconstruct_step`（GRU.py:176），再进 add_gru_* 看单块积木；对照 ONNX GRU 定义（opset 14）的门公式理解每个 Mul/Add 对应哪一项。要复用这套展开思路到 LSTM，注意 LSTM 是四门且有两个隐状态，序列拼接的 slice 逻辑要相应加倍。
