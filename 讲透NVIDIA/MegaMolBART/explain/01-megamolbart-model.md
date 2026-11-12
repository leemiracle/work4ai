# 01 · megamolbart_model.py：MegaMolBARTModel 全仓核心

> 涉及：`nemo_chem/models/megamolbart/megamolbart_model.py`（329 行，17 方法）。行号锚经源码核实。

## ① 角色定位

全仓唯一的模型定义文件。`MegaMolBARTModel`（megamolbart_model.py:37）继承 NeMo 的 `MegatronLMEncoderDecoderModel`（import 在 megamolbart_model.py:22）——**本仓不写 Transformer 本体**，encoder-decoder 结构、注意力、Megatron 并行全部来自 NeMo-Megatron；这个类做的是化学域接线：用什么数据集、掩码长什么样、指标怎么算。

## ② 内部结构

三类方法：

**训练构建**：`__init__`（L42）只调父类构造；`_check_scheduler`（L46）校验 Noam 调度器配置；`build_train_valid_test_datasets`（L60）经 `expand_dataset` 按路径与格式建三 split 数据集（背后是 molecule_binary_dataset/csv_dataset）；`build_pretraining_data_loader`（L90）桥接 Megatron 的 consumed_samples 断点续训协议；`process_global_batch`（L117）把全局批摊平成 token 序列供 Megatron 消费。

**步骤与指标**：`validation_step`（L160）/`test_epoch_end`（L200）→ 统一走 `_inference_epoch_end`（L134，mode='val'/'test' 两路）；`calculate_character_accuracy`（L240）token 级重建准确率；`calculate_molecular_accuracy`（L270）**分子级**准确率（重建 SMILES 与目标完全一致才算对——化学上更严的口径）；`calculate_metrics`（L307）聚合入口。

**生成**：`sample_molecules`（L205）从 encoder 隐状态采样分子（tokens_enc+enc_mask+可选 hidden_states 注入）——生成式推断的核心钩子，gRPC 的 HiddenToSmis rpc 间接经 NeMoMegaMolBARTWrapper 走到这里。

## ③ 外部连接

上游：NeMo MegatronLMEncoderDecoderModel（训练循环/并行/优化器）；数据管线三件（augment 的 span 掩码在 collate 期生效）。下游：`infer.py:20` NeMoMegaMolBARTWrapper 恢复检查点后调 sample_molecules 系；`megamolbart_eval.py` 评估脚本。`list_available_models`（L328）注册 NGC 预训练权重名。

## ④ 数据流

一个训练 step：dataloader 出 (tokens_enc, tokens_dec, loss_mask, labels, target_smiles)——labels 由 span 掩码产生（掩码位置记 mask token id）→ Megatron encoder 吃 tokens_enc 出隐状态 → decoder 自回归重建 → loss 只在 loss_mask 位置计算 → 指标双口径（char acc 逐 token / mol acc 整分子）。推断 step：sample_molecules 从 encoder 输出逐 token 采样至 EOS 再 detokenize 回 SMILES。

## ⑤ 设计决策

- **薄子类而非复制**：329 行承载全部化学定制，避免 fork NeMo——NeMo 升级即受益（仓死于 2022-08，NeMo 已多次大版本演进，此耦合即升级债）；
- **双指标口径**：char acc 对训练曲线友好，mol acc 才是药物发现的真口径（一个原子错即整分子错）；
- **`_inference_epoch_end` 双 mode 复用**：val/test 共用聚合逻辑减少分叉。

## ⑥ 新人提示

1. 找注意力/MoE/优化器实现别在本仓——去 NeMo 仓的 megatron 目录；
2. mol acc 口径注意：megamolbart_eval.py 的重建判定用裸字符串相等，与 canonical SMILES 相等两种口径并存（批 1 甄别），对比论文数字先问口径；
3. `sample_molecules` 的 hidden_states 注入路径是条件生成的埋点——理解它就理解了"从隐状态控制生成"；
4. 该文件的测试（pre_train_model_test.py）260 行全注释停用——形状断言零覆盖，改动后自己跑 tests/test_inference.py。
