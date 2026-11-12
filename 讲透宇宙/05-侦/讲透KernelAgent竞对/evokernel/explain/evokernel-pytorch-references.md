# EvoKernel pytorch-references 任务协议深解

> 依据五文件采样推断（Attention/10_AdaptiveAttention、MHC/01_SinkhornKnopp、KernelBench level1/100_HingeLoss、level2/100_ConvTranspose3d_Clamp_Min_Divide、level3/10_ResNet101），并经全库 grep 与 dataset.json 交叉验证。

## ① 角色定位：kernel 合成目标的规范定义

`pytorch-references/` 是 EvoKernel 数据集的任务规范层：每个 `.py` 文件定义一个 kernel 合成目标，由「参照实现（Model）+ 输入生成器（get_inputs）+ 构造参数（get_init_inputs）」三件套构成完整规范。它同时扮演两个角色：**正确性 oracle**（生成的 kernel 输出须与 Model 输出在容差内一致）与**性能基线**（PyTorch eager 实现即被超越对象）。三子族共 344 个任务：Attention 79 + MHC 15 + KernelBench 250（L1/L2/L3 = 100/100/50）。与 `ops-*-910b`/`ops-*-cuda-ncu` 导出目录构成闭环：任务定义 → 生成 kernel（命名 `<PascalName>Custom`，如 MhcProjectorCustom）→ result.json 记录正确性与性能。

## ② 协议解剖与上游一致性

五个采样呈现完全同构的五段式结构：**(1)** 纯 torch import（torch/nn/F/math）；**(2)** 可选辅助构建类（GroupedQueryAttention、Bottleneck）；**(3)** 唯一导出的 `Model(nn.Module)` 参照实现；**(4)** 模块级配置变量（batch_size、d_model、layers…）集中管理超参；**(5)** `get_inputs()` 返回与 forward 形参一一对应的位置张量列表，`get_init_inputs()` 返回构造参数列表（可为空，如 HingeLoss）。

隐含契约：`Model(*get_init_inputs())(*get_inputs())` 即真值。全库 344/344 文件均定义这两个函数；仅 1 个文件（Attention/49_ACmix.py）残留 cuda/manual_seed 字样——设备、种子、dtype 一律交由 harness 控制，任务文件保持后端中立（同一套任务因此能同时驱动 Ascend 910B 与 CUDA 两条导出线）。

与上游 KernelBench 的关系：KernelBench/ 子族是 Stanford KernelBench 的直接移植——文件名逐字保留（含 `1_Square_matrix_multiplication_.py` 尾下划线怪癖），changelog/ 收录 original_files.txt 与 v0.1/v0.2 版本说明，100/100/50 配比与上游一致；无 device 绑定、无 Benchmark 头注释的形态对应上游 v0.2 清理后的 problem.py 协议。**结论：与上游协议完全一致，Attention/MHC 两族是按同一契约撰写的即插即用扩展。**

## ③ 三个子族的命名与组织差异

- **Attention 族**（79 任务）：扁平布局，按语义家族编号 1-79（1_ScaledDotProduct → 2_MultiHead → 4_Flash → 10_Adaptive → 21_SE/ECA/CBAM 等通道注意力 → LLM 推理算子 norm/quantization/MoE）；dataset.json 标注 17 个 category，层级经元数据标注（16 L1/38 L2/25 L3）而非目录区分。
- **MHC 族**（15 任务）：Matrix Hyper Connections（DeepSeek 风格超连接架构），两位数编号 01-15，4 个 category（mhc_core/module/block/projection），4 L1/4 L2/7 L3；文件头带 `# Source:` 出处注释（01_SinkhornKnopp.py 标注 MarcoDotIO/mhc-deepseek-implementation 仓库路径）——三族中唯一显式溯源者。
- **KernelBench 族**（250 任务）：by_level 目录布局，category 为 matmul/norm/pooling 等算子语义。

每族根下 dataset.json 统一为 `{root, layout, ops}`：ops 把文件词干映射到 `{level, category, normalized_name, pascal_name}`——pascal_name 正是下游 `<Name>Custom` 生成类命名的来源；layout 字段（flat vs by_level）声明目录组织方式。

## ④ 层级递进的复杂度梯度

采样对比：**L1** 100_HingeLoss.py 仅 25 行、无状态、forward 一行融合表达式（clamp+mul+mean）、init_inputs 为空；**L2** 100_ConvTranspose3d_Clamp_Min_Divide.py 35 行、三算子链（反卷积→clamp→除法）、单个参数化层、5D 张量；**L3** 10_ResNet101.py 125 行、整网（Bottleneck×33、_make_layer、下采样捷径、Conv+BN 堆叠）。语义即：L1=单算子/单函数粒度，L2=融合算子链/单模块，L3=端到端模型图。两处提醒：粒度≠行数——MHC 的 SinkhornKnopp 是 L1 却含 tmax=20 的迭代算法；Attention 族的 L2 样本（AdaptiveAttention，152 行，argmax 路由+掩码分组批处理 MHA/GQA/MQA）控制流复杂度远超 KernelBench 同级——跨族同级不可直接比难度。

## ⑤ 如何添加自定义任务

1. 在目标族目录新建 `NN_PascalName.py`（扁平族放根目录，KernelBench 族按难度放 levelN/）；
2. 按五段式模板填写：纯 torch import →（可选辅助类）→ 唯一 Model → 模块级配置变量 → get_inputs（张量列表，顺序严格对齐 forward 形参；双输入任务如 HingeLoss 即两元素）+ get_init_inputs（无参则 `[]`）；
3. 禁止在任务内绑定 device/seed/dtype（后端中立铁律）；
4. 在该族 dataset.json 的 ops 中登记 `level(1-3) + category + normalized_name + pascal_name`——漏登则任务对 harness 不可见。

## ⑥ 新人提示

- 先记住 oracle 契约 `Model(*init)(*inputs)`：读任何任务先看两个函数签名，再看 Model 内部；
- KernelBench 族文件名是上游原样拷贝（含尾下划线），为可追溯性勿重命名；对照上游用 changelog/；
- category 是现成的跨族分层评估轴（按 matmul/channel_attention/mhc_core 切片统计）；
- 任务内无种子，同任务多次运行输入不同——复现实验须在 harness 侧设种子；
- 新任务建议补 MHC 式 `# Source:` 溯源注释；写完跑一行冒烟验证契约：`Model(*get_init_inputs())(*get_inputs())` 能否前向。
