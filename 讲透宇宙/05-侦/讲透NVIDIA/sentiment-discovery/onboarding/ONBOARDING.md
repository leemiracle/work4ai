# sentiment-discovery 讲透上手指南（ONBOARDING）

> 仓库：NVIDIA/sentiment-discovery @ 17bcf05（2020-06-28，末次提交名即 "deprecation"，README:1-2 顶部 DEPRECATED 指向 Megatron-LM）
> 定位：OpenAI《Learning to Generate Reviews and Discovering Sentiment》（Radford et al. 2017，"情感神经元"）的**工程复现与规模化仓**——README:8 自述 "born out of a desire to reproduce, analyze, and scale" 该论文；logreg_utils.py:9 注明逻辑回归探测代码"Modified version of openai implementation"（官方宿主是 openai/generating-reviews-discovering-sentiment，本仓自己的论文是 40GB/4h 大批量 LM 训练与 arXiv 1812.01207 文本分类）。
> 图谱：271 节点 / 511 边 / 9 层 / 12 步 tour / fingerprints 69 文件 @ 17bcf051
> 本文档所有行号锚均经源码逐条核实（2026-11-10）。

## 一、一句话定位

在 Amazon 评论语料上无监督预训练 4096 维 mLSTM（或字符级 Transformer）语言模型，然后用 L1 逻辑回归逐神经元扫描找出编码情感的单个"情感神经元"，再在生成时强行改写该神经元值操控文本情感——预训练、探测、操控三幕剧的完整可复现实现，附带 FP16/分布式训练基建（NVIDIA apex 的前身代码）与监督微调线。

## 二、整体架构与模块地图

全仓 45 个 Python 文件（约 9200 行），图谱九层单向依赖 `文档配置 → 参数/数据中枢 → 数据资产 → 惰性加载 → 模型装配 → mLSTM 后端 → FP16/重参数化 → 五大入口 → 实验脚本`：

| 子系统 | 角色 | 关键文件 |
|---|---|---|
| 参数中枢 | 119 个 add_argument 分 9 组注册（arguments.py），被全部新入口共享 | `arguments.py:11`（通用）、`arguments.py:62`（无监督数据） |
| 数据配置 | DataConfig 描述 amazon/imdb/sst/semeval 数据集协议 | `configure_data.py:6`、`configure_data.py:27`（make_loaders） |
| 数据资产 | ./data/ 内置 binary_sst、imdb、semeval；amazon 需自行下载 | `arguments.py:204-205`（transfer 默认 SST 三 split） |
| 惰性加载 | 69 亿 token 不落内存：mmap 拼接大文件 + 长度表切片 | `data_utils/lazy_loader.py:68`（lazy_array_loader）、`data_utils/lazy_loader.py:87`（mmap） |
| 采样/整理 | 连续 token 流按 shard 切批、跨 shard 保持时序状态 | `data_utils/samplers.py:214`（BatchShardSampler）、`data_utils/datasets.py:395`（data_shard） |
| 模型装配 | RNNModel/RNNFeaturizer 与 TransformerDecoderModel/TransformerFeaturizer 双臂 | `model/model.py:12`、`model/model.py:61`、`model/model.py:195`、`model/model.py:279` |
| RNN 后端 | 显式 Python 时间步循环 + 乘性 mLSTM 单元（论文主模型） | `model/RNN_utils/RNN/RNNBackend.py:100`、`model/RNN_utils/RNN/cells.py:13` |
| Transformer 臂 | fairseq vendored 简化版 + 增量 KV 解码 | `model/transformer.py:21`、`model/transformer_utils.py:20` |
| 训练基建 | FP16_Optimizer（23 方法）、DDP、weight_norm、LR 调度族 | `fp16/fp16.py:58`、`model/distributed.py:8`、`reparameterization/weight_norm.py:22`、`learning_rates.py:61` |
| 五大入口 | pretrain / transfer / generate / finetune_classifier / run_classifier | `pretrain.py:27`、`transfer.py:83`、`generate.py:98`、`model/sentiment_classifier.py:269` |

旧入口 main.py 与新入口 pretrain.py 并存：main.py 内联 37 个参数（数过）、import apex（main.py:17）、用 LinearLR（main.py:19）；pretrain.py 走共享 arguments.py 与仓内 reparameterization（pretrain.py:20），README:135-148 全部示例只推 pretrain.py——**README 主推 pretrain.py，main.py 是遗留遗迹**。

## 三、核心模块深读

### 3.1 mLSTM 乘性单元（论文主模型落点）

工厂 `mLSTM(input_size, hidden_size, num_layers...)`（model/RNN_utils/RNN/models.py:59）构造 mLSTMRNNCell（cells.py:13）再交给 stackedRNN 堆层——工厂函数里还留着 `print("Creating mlstm")`（models.py:63）调试残留。乘性机制在 mLSTMCell（cells.py:56）：`m = F.linear(input, w_mih) * F.linear(hidden[0], w_mhh)`（cells.py:63），即 m_t = (W_mi·x_t)⊙(W_mh·h_{t-1})，两组额外参数 w_mih/w_mhh 在 cells.py:22-23 注册；随后把 m 当作"等效隐状态"喂标准 LSTM 门——CUDA 路径直接调 `_VF.lstm_cell(input, (m, hidden[1]), ...)`（cells.py:65-66）复用 ATen 融合核，CPU 路径手工展开 i/f/o/c 四门（cells.py:70-81）。乘性交互让单元状态可表达秩更高的输入-历史耦合，论文中 4096 维单元里第 ~3672 号神经元（cell state）即情感神经元。

### 3.2 显式时间步 RNN 后端

stackedRNN（RNNBackend.py:100）不用 cudnn 融合，forward（RNNBackend.py:132）里显式 Python 双层循环：外层 `for seq in inp_iter`（:144）、内层逐层（:147-151），每时间步先按 reset_mask 重置边界样本（:145-146，`hidden * (1 - reset_mask)` 在 :358）。基类 RNNCell（:245）持有 w_ih/w_hh（:270-271）与可选输出投影 w_ho（:274-275）；init_hidden 惰性建零状态（:327-345）；detach_hidden（:365-373）就是截断 BPTT 的断梯点——RNNModel.forward 每步先 `self.rnn.detach_hidden()` 再前向（model/model.py:39），隐藏状态跨 batch 保留但梯度不回传上一批。代价是速度：pretrain.py:292 与 main.py:105 都 `torch.backends.cudnn.enabled = False`。

### 3.3 FP16_Optimizer（apex 前身，23 方法）

fp16/fp16.py 的 FP16_Optimizer（:58）数下来恰好 23 个方法（含 9 个私有/property 存取器）：构造时把每个 param_group 拆成 fp16 参数与 fp32 主副本（:166-186，`detach().clone().float()` 在 :181），优化器只看得见 fp32 组；静态/动态 loss scale 二选一（:194-202，静态 LossScaler 恒不溢出，动态 DynamicLossScaler 初始 2^32、连稳 1000 步翻倍，fp16/loss_scaler.py:37-39）；动态模式 `update_master_grads` 先查 inf/nan（fp16.py:502-504），溢出则 step 打印 "OVERFLOW! Skipping step"（:390-393）并自动降 scale 重来。梯度拷贝/回写走 fp16/fp16util.py:93/:115。README:218 致谢说这些工具"最新版本在 APEx github"——本仓代码即 apex 开源前的家版本。

### 3.4 fairseq 式 Transformer 与增量 KV

transformer.py:9 自述 "Code adapted from fairseq"；MultiheadAttention 自实现于 transformer_utils.py:20（in_proj_weight 3*embed_dim 拼合投影 :35）：forward（:51）用 `data_ptr()` 判 qkv/kv 同源（:63-64），incremental_state 非空时读 prev_key/prev_value 缓存、concat 当步 k/v 后写回（:101-108）——逐 token 解码 O(1) 增量；beam search 重排走 reorder_incremental_state（:220）；实例级缓存键由 `_fairseq_instance_id` 生成（:371-375）。DecoderPreprocessor（transformer.py:102）把 src_tokens 原样当 encoder_out（:106-110）——LM 形态下"编码器"是直通用例。解码器训练期可用 sqrt 分块梯度检查点（:300-306，chunk=ceil(sqrt(层数))）。

### 3.5 论文三幕剧

- **第一幕 预训练**：pretrain.py 的 setup_model_and_optim（:27）装配模型+优化器+调度器；get_batch 把 data[:, :-1]/[:, 1:] 错位成输入/目标（:134-135）；fp16 时 backward/clip/step 全改走 optim（:202-222），溢出跳过 LR 步进（:233-238）。
- **第二幕 探测**：transfer.py 的 transform（:83）批量抽特征（docstring :86 明言 "should return cell state not hidden state"），train_logreg（logreg_utils.py:20）默认 L1 惩罚扫 9 档 C=2^-8..2^0（:21）；get_top_k_neuron_weights（transfer.py:158）按权重 L1 范数排序取 top-k 神经元（:169-179 三分支按 k 规模选 argmax/argsort/argpartition）。
- **第三幕 操控**：generate.py 的 get_neuron_and_polarity（:98）从 checkpoint 的 classifier 权重取绝对值最大位定位神经元（:111-112）、符号定极性（:113-117）；process_hidden 在每步前向後把最后层 cell 的该维直接 fill 成 ±1（:120-126，取 model.rnn.rnns[-1].hidden 于 :131）；--visualize 时 seaborn 热力图逐字符着色（make_heatmap，:180-204）。

### 3.6 监督线与评估

finetune_classifier.py（639 行，最大入口）端到端反传进 LM 编码器；SentimentClassifier（model/sentiment_classifier.py:269）按 model_type 选 TransformerFeaturizer（:278）或 RNNFeaturizer（:281-283），头上叠 BinaryClassifier（:10，单层）或 MultiLayerBinaryClassifier（:106，MLP+多头+方差正则）。threshold.py 做阈值搜索：二分类每类 linspace 200 档扫最优（:28），三态（pos/neg/neutral）双阈值 30² 网格（_neutral_threshold_two_output，:164）。

## 四、数据流全链路（预训练一轮）

1. `pretrain.py main()`：add_general/model/unsupervised 三组参数装配（pretrain.py:285-290）；`--loss_scale≠1` 且 `--dynamic_loss_scale` 同开直接 raise（:321-322）。
2. `data_config.apply(args)`（configure_data.py:12）→ make_loaders（:27）：num_workers=4 + pin_memory（:41-45），L2R 模式选 ShardLoader 并注入 seq_len/persist_state（:48-49）。
3. 语料物化：make_lazy 把 tokenize 后语料写成单一大文件 + 长度 pkl（lazy_loader.py:29，rank0 写其余进程轮询等待 :38-52）；读取端 lazy_array_loader 按累计偏移切片（:90、:98-120），mmap 时零拷贝（:87）；file_read 加线程锁但源码自留 "TODO: Solve race condition"（:127）。
4. 分词默认 CharacterLevelTokenizer（tokenization.py:122）：词表=256 字节 + 命令 token 偏移（TokenToId=ord+n，:153-154）；process_str 统一 '\n ' 前后垫（preprocess.py:38）。SentencePiece BPE 是可选分支（tokenization.py:189）。
5. 训练循环 train()（pretrain.py:170）：模型前向接 reset_mask 维持样本边界（:192-194）；fp16 三步曲 backward→clip_master_grads→update_master_grads→step（:202-222）；分布式由 multiproc.py 每卡 fork 一个带 --rank 的进程（multiproc.py:24-35），梯度经 DDP 扁平化 all_reduce（model/distributed.py:39-44），pretrain 显式调 model.allreduce_params()（:210）。
6. 检查点：save_iters 触发增量保存 e{iter}.pt + optim.pt + rng.pt（:252-265，rng 存 CUDA/CPU 双状态供精确续训）。
7. 切换到第二幕：transfer.py --load 读同一 ckpt，权重加载失败时先 apply_weight_norm 再卸（transfer.py:62-79）——weight_norm（Salimans & Kingma 2016）训练期把 W 拆成 g·v/||v||（reparameterization/weight_norm.py:56），推理/探测时移除。

## 五、配置与运行入口

- 主链五命令：`pretrain.py`（预训练，README:130 默认即 weight-norm 4096 维 mLSTM+64 维字符嵌入）、`transfer.py`（探测+两轮回归）、`generate.py --load_model --overwrite 1 --neuron -1`（操控生成）、`finetune_classifier.py --lr 2e-5 --aux-lm-loss --aux-lm-loss-weight .02`（端到端微调，README:181）、`run_classifier.py --load_model ama_sst.pt`（免训练分类）。
- 参数三层来源：arguments.py:89 add_model_args 按 `--model` 是否 transformer 条件装配（parse_known_args 分流）；classifier 组的 --concat-max/min/mean（:176-181）与 --get-hidden（:182-183，"用 hidden 而非 cell"——反向印证默认特征是 cell state）；finetune 组 --freeze-lm（:262）与 aux-lm-loss-weight 默认 1.0 但 help 自曝 "Way too high -- reasonable around 0.02"（:266-267）。
- 数据默认值：configure_data.py:125 训练默认 ./data/imdb/unsup.json、:140 --data-size 256（字符词表）；amazon 训练走 experiments/train_mlstm_singlenode.sh：`python -m multiproc pretrain.py --data ./data/amazon/reviews.json --lazy --dynamic-loss-scale --fp16 --train-iters 73000 --lr 3e-3`。
- 学习率族：AnnealingLR（learning_rates.py:142）+ WarmupLR（:185）为主；--stlr-cut-frac 切 ULMFiT 式 SlantedTriangularLR（:61，注释引 arXiv 1801.06146）。

## 六、关键设计决策

1. **特征=cell state 而非 hidden state**：RNNFeaturizer.get_features 默认取 hidden[1]（cell）再取最末层（model/model.py:158-168）；论文情感神经元住在 mLSTM 的**单元状态**里，--get-hidden 才切换口径。这是复现时最容易搞错的点。
2. **截断 BPTT 的极简实现**：不裁剪序列，只在每个 batch 边界 detach（model/model.py:39），配合 reset_mask 做样本级重置（RNNBackend.py:145-146）——隐藏跨批延续、梯度不延续。
3. **fp32 主权重 + 动态 loss scale** 全在仓内自实现（fp16/fp16.py），先于 apex 开源；静态/动态互斥在入口就 raise（pretrain.py:321-322）。
4. **两臂对照**：mLSTM 与 Transformer 共用数据/训练/探测管线，仅模型臂不同（pretrain.py:29-34 分派）——论文结论"方法不挑架构"的实验设计直接体现在代码结构里。
5. **惰性语料管线**：tokenize 只做一次落盘（lazy_loader.py:29），npy 分片 + mmap + ShardLoader 流式读取，69 亿 token 语料训练内存可控。
6. **weight_norm 训练期挂、加载期兜底**：所有 load 都 try 直接加载、失败再挂 weight_norm 装载后移除（pretrain.py:51-59、transfer.py:62-79、generate.py:91-96 三处同构）。

## 七、坑与勘误（详版见 ../README.md 勘误清单）

1. threshold.py 的 neutral_threshold_two_output 在 :128 与 :154 **重复定义两次**，后者静默覆盖前者；main() 的 task_dict（:193）拿到的是 :154 的向量版（30 档粒度），:128 的 pandas 200² 版是死代码。logreg_utils.py:18 绕开公共函数直接 import 私有 `_neutral_threshold_two_output`。
2. model/checkpoint.py（166 行 CheckpointFunction，带 RNG 状态管理）**全仓零 import**——孤儿模块；transformer.py:19 实际用 torch.utils.checkpoint；RNNModel.forward 收 chkpt_grad 参数但从不使用（model/model.py:37-44），RNN 路径 --chkpt-grad 静默无效。
3. transformer.py:246-251 引用 MixtureOfSoftmax，全仓无定义——相关分支必 NameError。
4. transfer.py 的 plot_logits 引用未定义的 trXt/trY（:191），必 NameError 后被 :367-370 的 except 吞成 "no labels to plot logits for"——logit_vis 直方图从未真正生成。
5. main.py:17 与 generate.py:16 仍 `from apex.reparameterization import ...`——不装 apex 这两个入口直接 ImportError，而主链 pretrain.py 用的是仓内 reparameterization（:20）。
6. pretrain.py --load-optim 断链：optim_sd 的赋值被注释（:47），:79/:91/:342 仍引用它，开启即 NameError。
7. generate.py:1-5 文件头注释还是 "Language Modeling on Penn Tree Bank"（word_language_model 样板血统），实际是字节级评论 LM；--visualize 的 help 自认 "not working yet"（generate.py:63）。
8. RNN 工厂 Tanh 函数连续构造两次（models.py:55-56），第二行引用未定义的 RNNTanhCell——`--model Tanh` 必 NameError。

## 八、新人上手路线

1. **第 1 步（30 分钟）**：读仓 README 与本页第一、二节；跑 `python3 transfer.py --load mlstm.pt`（需下载预训练 mLSTM，README:87），看 `<model>_transfer/` 下的 neurons_score.txt 与 weight_vis.png。
2. **第 2 步（1 小时）**：精读三幕剧：pretrain.py:126-247（get_batch→train 循环）→ transfer.py:83-180（transform→get_top_k_neuron_weights）→ generate.py:98-146（定位神经元→process_hidden 改写）。对照第六节第 1 条盯紧"cell state"口径。
3. **第 3 步（1 小时）**：读 mLSTM 双件套：cells.py 全文 84 行 + RNNBackend.py:100-208（时间步循环与 hidden 张量格式注释）；再读 model/model.py:37-44 数清 detach 时机。
4. **第 4 步（1 小时）**：读 fp16/fp16.py 的 FP16_Optimizer 构造与 step/backward（:151-202、:345-402、:434-506），配 pretrain.py:202-238 的调用侧；对照 distributed.py 理解 2018 年多卡 allreduce 手法。
5. **第 5 步（进阶）**：读 transformer_utils.py:51-151 增量 KV 全流程 + transformer.py:272-325 解码器；最后浏览 finetune_classifier.py 与 threshold.py 评估线，注意第七节的坑再动手。
6. **避坑**：别用 main.py/generate.py 前忘了装 apex；复现论文数字时坚持默认 L1+cell state+单神经元（transfer.py:311-338 的第二回归）；改 RNN 相关代码前记住 cudnn 被全局关闭是有意为之。

> 锚格式 `文件:行`，相对仓根 /usr-data/data2/repos/agent-repos/NVIDIA/sentiment-discovery/。配合 deepwiki/ 27 页与 explain/ 4 篇精讲食用。
