# 04 RL_KTO/ 偏好优化线：KTO 数据加工与 llamafactory-cli 启动链

## 角色定位

`RL_KTO/` 是 RARE 的强化学习后段：把 SFT 后模型在训练集上的推理结果转成 KTO（Kahneman-Tversky Optimization）偏好格式——每条样本只有单边标签（好/坏）而非成对比较——再用 LLaMA-Factory 做 KTO 微调。组件：`process_kto.py` 数据转换、`RL_KTO/data/dataset_info.json` 七数据集注册表、`train_kto.sh` 启动脚本、`ds_z3_offload_config.json` DeepSpeed 配置。readme.md:320-329 把它定位为"Reinforcement Learning"扩展。

## 内部结构

**`process_kto.py`（41 行）**：`extract_option`（L5-15，与全仓同源的四级正则）分别抽取 `predict`（模型输出）与 `output`（金标）的选项字母，相等则 `kto_tag=True`（L23）——答对即偏好正例、答错即负例，这是 KTO 单边标签的全部语义。随后组装 `{"conversations": [human=instruction, gpt=predict], "kto_tag": bool}`（L25-30）写出。CLI 只有 `--input_path`/`--output_path` 两参（L38-39）。

**`train_kto.sh`（50 行）**：变量区定义 `model_name_or_path`（L2）、`temp=llama3`（L5，注释留了切换位）、`dataset=covert_kto`（L11）、`OUTPUT_DIR`（L14）；L16 起 `llamafactory-cli train` 长命令：`--stage kto`（L17）、full 微调（L21）、`--dataset_dir RL_KTO/data`（L24）、lr 5e-6 × 3 epoch（L27-28）、KTO 三参数 `--pref_beta 0.1 --pref_ftx 0 --pref_loss sigmoid`（L46-48）、DeepSpeed ZeRO-3（L49）。

**`RL_KTO/data/dataset_info.json`**：七条 KTO 注册（pubmed/pubhealth/bioasq/covert/medqa/finfact/casehold，L3-58），均 sharegpt 格式。**`ds_z3_offload_config.json`**：ZeRO-3 + 双 CPU offload，`stage3_gather_16bit_weights_on_model_save=true` 保证保存时聚出完整权重。

## 外部连接

上游消费 SFT 模型的推理输出：readme.md:324 示例 `python RL_KTO/process_kto.py --input_path data/train_covert.json --output_path RL_KTO/data/train_covert_kto.json`——输入须先用 SFT 模型跑 `inference/vllm_infer_text.py` 生成 predict 字段。下游完全寄生于 llamafactory 0.9.2：`--stage kto`、`pref_*`、dataset_info 格式全是 LLaMA-Factory 协议。注意 **covert 与 bioasq 在仓内没有 process 构建脚本**——process/ 只覆盖六个领域，注册表（L19、L27）与 readme 却引用了它们，输入 JSON 只能自备。

## 数据流

```
SFT 模型 + train_*.json
  → vllm_infer_text.py 写回 predict
  → process_kto.py：predict vs output 抽选项比对 → kto_tag
  → RL_KTO/data/train_*_kto.json → dataset_info.json 注册
  → train_kto.sh（llamafactory-cli + DeepSpeed ZeRO-3）
  → saves/RL_KTO/llama3_covert_kto
```

负样本是模型答错的完整推理（含错误思维链），正样本是答对的推理——模型从"自己的失败"学偏好，这正是论文 RL 章节验证的"筛真蒸馏 + KTO 叠加增益"。

## 设计决策（含批判）

**用预测对错当偏好标签**极简且无需奖励模型，但有隐含偏差：答对=好推理在长思维链上并不总成立（蒙对的答案会被当正例）。**`${model_path}` 与 `${len}` 双坑**是本线最著名的 bug：train_kto.sh:19 写 `--model_name_or_path ${model_path}`，但 L2 定义的变量名是 `model_name_or_path`；L26 写 `--cutoff_len ${len}`，`len` 也从未定义。bash 对未定义变量静默展开为空串（无 `set -u`），实际执行的是空值参数，llamafactory-cli 要么报校验错要么按危险默认跑——照抄必翻车。**finfact_kto 注册不一致**：其余六条都指向 `train_*_kto.json`，唯独它指向 `train_finfact.json`（L44），跑前必须核对盘上实际文件名。

## 新人提示

1. 跑 train_kto.sh 前先补两个变量：L19 改 `${model_name_or_path}`（或给 `model_path` 赋值）、L26 给 `len` 赋值——这是本线的入门税。
2. KTO 输入必须先有 predict 字段：完整链是 SFT 推理 → process_kto → 训练，跳过第一步会 KeyError。
3. covert/bioasq 无构建脚本，注册表里它们是"承诺"不是"现货"。
4. DeepSpeed 双 offload 换来小显存跑 8B 全参，代价是速度显著下降；卡够可删两个 offload 段。
