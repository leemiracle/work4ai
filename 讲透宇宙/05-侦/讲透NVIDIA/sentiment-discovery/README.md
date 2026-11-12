# 讲透 NVIDIA/sentiment-discovery

OpenAI "情感神经元"论文（Radford et al. 2017, *Learning to Generate Reviews and Discovering Sentiment*）的工程复现与规模化仓：无监督预训练 4096 维 mLSTM / 字符级 Transformer → L1 逻辑回归逐神经元探测 → 生成时改写神经元操控情感，附带 FP16/分布式训练基建（apex 前身代码）与监督微调线。仓末次提交 17bcf05（2020-06-28，提交名即 "deprecation"，README 顶部 DEPRECATED 指向 Megatron-LM）。

**定位澄清**：本仓不是 Radford 2017 的官方宿主——README:8 自述 "born out of a desire to reproduce, analyze, and scale" 该论文，官方仓为 openai/generating-reviews-discovering-sentiment（本仓 logreg_utils.py:9 注明探测代码 "Modified version of openai implementation"）。本仓对应的自家论文是《Large Scale Language Modeling: Converging on 40GB of Text in Four Hours》与 arXiv 1812.01207。

## 全链状态表

| 产物 | 状态 | 说明 |
|---|---|---|
| deepwiki/ | 完成 | 23/23 结构页 TRUE_100（2026-10-26 MCP 抓取，INDEX.md + wiki_full.md + _coverage-check.md 终判） |
| 图谱 | 完成 | 271 节点 / 511 边 / 9 层 / 12 步 tour，fingerprints 69 文件 @ 17bcf051，validator 0 issues |
| onboarding/ONBOARDING.md | 完成 | 8 节，10259 不计空格字符，86 个行号锚全解析（basename 唯一匹配消歧） |
| explain/ 精讲 4 篇 | 完成 | 01 mLSTM 乘性单元（26 锚）/ 02 FP16 与 Checkpoint（14 锚）/ 03 Transformer 增量 KV（18 锚）/ 04 论文三幕剧（15 锚），每篇 1500-2500 字符六节结构 |
| 源码仓 | 只读 | /usr-data/data2/repos/agent-repos/NVIDIA/sentiment-discovery @ 17bcf05 |

## 勘误清单（源码实证 vs README / DeepWiki / 直觉认知）

1. **"官方宿主"表述不成立**：直觉认知与本任务书的"论文官方仓"说法均需修正——README:8 与 logreg_utils.py:9 双证据表明本仓是复现+规模化仓，自家论文另有其篇（见上"定位澄清"）。
2. **threshold.py 重复定义静默覆盖**：neutral_threshold_two_output 在 threshold.py:128 与 threshold.py:154 定义两次，后者覆盖前者；main() 的 task_dict（threshold.py:193）拿到的是 :154 向量版（30 档粒度），:128 的 pandas 200² 版为死代码。logreg_utils.py:18 绕开公共函数直接 import 私有 `_neutral_threshold_two_output`。
3. **model/checkpoint.py 是孤儿模块**：166 行 CheckpointFunction（带 CUDA RNG 保存/恢复，checkpoint.py:36-64）全仓零 import；transformer.py:19 实际用 torch.utils.checkpoint（sqrt 分块在 transformer.py:300-306）；且 RNNModel.forward 接收 chkpt_grad 却从不使用（model/model.py:37-44）——`--chkpt-grad` 对 mLSTM 臂静默无效。DeepWiki 6.2 页把 model/checkpoint.py 列为混合精度管线的活跃组件（"Gradient Checkpointing model/checkpoint.py"），与 import 图不符。
4. **DeepWiki "hidden states" 口径错误**：DeepWiki 2.2 页称 RNNFeaturizer 抽取 "RNN hidden states"、默认池化为 "Last Hidden State"——源码默认取 **cell state**：model/model.py:158-168 的 get_features 取 hidden[1]，transfer.py:86 docstring 明言 "should return cell state not hidden state"，arguments.py:182-183 的 --get-hidden 才是切换开关。情感神经元住在 cell state 里，按 wiki 口径复现会找错张量。
5. **MixtureOfSoftmax 引用未定义**：transformer.py:246-251 分支引用 MixtureOfSoftmax 类，全仓无定义（grep 实证仅 transformer.py 一处出现）——启用相关参数必 NameError。DeepWiki 2.2 页把 MoS 列为可用特性（"Mixture of Softmax: Optional MoS layer"）。
6. **main.py 与 pretrain.py 双入口职责**：README:135-148 全部训练示例走 pretrain.py；main.py 是遗留入口——37 个内联参数（数过；NOTES-DIGEST "约 80 个"口径偏高）、import apex（main.py:17）、用 LinearLR（main.py:19），而 pretrain.py 用仓内 reparameterization（pretrain.py:20）与 arguments.py（119 个 add_argument）。DeepWiki 6.2 流程图把 "Training Orchestration" 节点标为 main.py、"Dynamic Loss Scaling" 标为 "NVIDIA Apex"——运行时主链实际是 pretrain.py + 仓内 fp16 包（pretrain.py:14）。
7. **README:167-168 注释互换**：`run_sk_sst.sh` 实为默认 SST 数据（脚本仅 `transfer.py --load mlstm.pt --save-results sst`），README 注释却说 "on imdb dataset"；run_sk_imdb.sh（显式 `--data ./data/imdb/...`）被注成 "on sst dataset"。
8. **transfer.py 的 logit 直方图从未生成**：plot_logits 引用未定义的 trXt/trY（transfer.py:191）必 NameError，被 transfer.py:367-370 的 except 吞成 "no labels to plot logits for"——logit_vis 产物是永远缺席的。
9. **--load-optim 断链**：pretrain.py:47 的 optim_sd 赋值被注释掉，但 :79/:91/:342 仍引用——开启即 NameError，断点续训从未真正可用。
10. **generate.py 的样板残留与 apex 依赖**：文件头注释仍是 "Language Modeling on Penn Tree Bank"（generate.py:1-5，word_language_model 样板血统，实为字节级评论 LM）；args.data_size=256 硬编码（generate.py:70）；--visualize 的 help 自认 "not working yet"（generate.py:63）；且 generate.py:16 import apex——与"本仓 fp16 自足"的主链（pretrain.py）不一致，无 apex 环境第三幕入口直接 ImportError。
11. **RNN 工厂 Tanh 不可用**：models.py:55-56 连续构造两次 RNNCell，第二行引用未定义的 RNNTanhCell——`--model Tanh` 必 NameError（LSTM/GRU/ReLU/mLSTM 正常）。

## 产物索引

- onboarding/ONBOARDING.md——8 节上手指南（架构地图/mLSTM 深读/FP16/三幕剧/坑）
- explain/01-mLSTM-乘性单元与RNN后端.md
- explain/02-FP16与Checkpoint-训练基建.md
- explain/03-Transformer-增量KV实现.md
- explain/04-论文三幕剧-预训练探测操控.md
- deepwiki/——23 页全量 wiki 快照（INDEX.md 入口）

## 新人路线

先读 onboarding 第一节定位与第八节路线 → explain/04 串三幕剧 → explain/01 进 mLSTM 内部 → 需要训练基建再读 explain/02 → Transformer 臂读 explain/03。动手复现前必读勘误清单第 2/4/10 条（cell state 口径、threshold 重复定义、apex 依赖）。锚格式 `文件:行`，相对仓根 /usr-data/data2/repos/agent-repos/NVIDIA/sentiment-discovery/。
