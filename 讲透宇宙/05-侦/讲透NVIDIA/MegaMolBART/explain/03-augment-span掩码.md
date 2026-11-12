# 03 · augment.py：span 掩码——BART 自监督信号的化学形态

> 涉及：`nemo_chem/data/augment.py`（277 行）、`examples/chem/conf/megamolbart_pretrain_base.yaml:86-88`。行号锚经源码核实。

## ① 角色定位

预训练任务是"重建被遮住的片段"，这个文件决定**遮什么、遮多长**——它是 MegaMolBART 自监督信号的唯一来源。`MoleculeEnumeration`（augment.py:31）在 collate 期对每个 batch 做两件事：SMILES 规范化增强（RDKit RenumberAtoms 原子重编号——同分子不同写法，天然数据增广）与 span 掩码。

## ② 内部结构

构造签名（augment.py:36）收 `mask_scheme/mask_prob/span_lambda` 三参（存 L46/L48）。掩码实现三个方法：

- **`_mask_span`（augment.py:241）——现行唯一分支**：遍历 token 序列，以 `mask_prob`（Bernoulli）概率采 span 起点，长度取 `torch.poisson(span_lambda)`（augment.py:253，配置 3.0 即平均 3 个 token）；整段塌缩为**单个** mask token——输出序列因此比输入短，重建目标仍按原 token 对齐；
- **`_mask_replace`（augment.py:234）——死代码**：逐 token 独立掩码的备选方案；
- **`_mask_token`（augment.py:266）——死代码**：token 级替换。

分支选择处（augment.py:222-227）的 `if mask_scheme == "replace"/"span"` 判断**整段被注释**——无论配置传什么都走 span；两个死方法还引用 `show_mask_token_prob/chem_token_idxs/decode_vocab` 等**从未在 __init__ 定义的符号**（代码内自标 FIXME not working），复活需先补这批属性。

## ③ 外部连接

上游：`prepare_dataset.py`（collate 装配层）把 MoleculeEnumeration 挂进数据加载链；配置来源 base.yaml 的 model.data 节（mask_scheme: span / mask_prob: 0.1 / span_lambda: 3.0，yaml L86-88）——**三个 *_span_aug.yaml 变体不含任何增强开关字段**，span_aug 命名只是继承这条数据增强线。下游：tokenize(mask=True) 与 MegaMolBARTModel 的 loss_mask。pysmilesutils 的 SMILESAugmenter 虽被 import 但未用（批 3 甄别）——增强是手写 RenumberAtoms。

## ④ 数据流

一个分子进 collate：SMILES → RDKit 解析 → RenumberAtoms 得等价 SMILES（增广）→ tokenize → `_mask_span`：约 10% 位置起 Poisson(3) 长度的段替换为 mask token → 输出 (tokens_enc 含 mask, labels 原词, loss_mask 标注被遮位置)。模型学习的即"从上下文恢复被挖掉的连续化学子结构"。

## ⑤ 设计决策

- **span 而非逐 token**：化学官能团是连续子串（如 `C(=O)O`），span 掩码迫使模型学习官能团级重建而非单字符拼写——这是 BART 对化学域的关键适配；
- **塌缩为单 mask token**：输出变短、计算省，但要求 decoder 对齐逻辑记住被吞掉的长度（labels 不塌缩）；
- **RenumberAtoms 而非 SMILESAugmenter**：手写增强少依赖且可控——被 import 未用的 pysmilesutils 是历史残留。

## ⑥ 新人提示

1. 想改掩码率只动 yaml（mask_prob/span_lambda），别动代码——mask_scheme 分支是注释掉的摆设；
2. 复活 `_mask_replace` 前先补 `show_mask_token_prob` 等符号定义，否则 NameError；
3. Poisson 采样是随机的——复现实验要同时固定 torch 种子（增广+掩码两处随机源）；
4. 评估脚本不经此文件（eval 无增广），训练 loss 与 eval 指标的掩码分布差异要心里有数。
