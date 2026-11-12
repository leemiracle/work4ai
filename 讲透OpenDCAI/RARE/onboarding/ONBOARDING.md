# RARE 新工程师入门指南（ONBOARDING）

> OpenDCAI/RARE @0f6d706（图谱 102n/169e，11 层 12 步 tour）。行号锚从源码核实，冲突以源码为准。

## 1. 一句话定位

RARE（Retrieval-Augmented Reasoning Modeling，KDD 2026，arXiv:2503.23513）是一个**规则化数据清洗研究仓**：`process/` 把 PubMedQA、MedQA、PubHealth、CaseHOLD、FinFact、MM-RAIT 六域数据统一成「检索文档+选择题」json，教师模型（QwQ-32B/Qwen2.5-VL-32B）蒸馏出 `<think>…</think><answer>X</answer>` 思维链，再训练 Llama-3.1-8B 一类小模型「基于检索文档推理」而非死记知识——核心主张：**知识存储**交给检索、**推理建模**交给训练。全仓无常驻服务，是按 readme.md 手册串起的 20 个独立脚本，构成 process 构建→蒸馏→SFT/KTO 训练→推理评测的研究闭环。

## 2. 心智模型

把 RARE 当**流水线脚本集合**而非软件系统：

**① 零 py→py import，靠数据文件衔接。** 20 个脚本相互零 import（只 import 外部库 vllm/trl/llamafactory/qdrant_client），接力棒是 `data/` 下的 json：process_*.py 产出 `train_*.json`（instruction 题面+output 真值）→ 推理脚本写回 `predict` 键 → select_true.py 产出 `*_true.json` → 训练脚本直接 `open()`。看懂数据格式变迁就看懂全仓。

**② 双训练线并存。** 自研线 `train/sft.sh`→`sft.py`：torchrun+FSDP 手写 trl.SFTTrainer，直读 json 不经注册表；LLaMA-Factory 线 `train/train.py`：9 行薄入口（train.py:5 只调 `run_exp()`），超参全在 YAML，数据集按名引用 `data/dataset_info.json` 注册表。readme.md:177 自述自研线可能重复生成，推荐 LF 线兜底。

**③ 数据与模型是生成物。** `data/` 只放注册表，`saves/`、`Pre_Experiment/model|result` 仅 .gitkeep 占位，训练数据都要现场跑 process/ 构建。

## 3. 代码地图（按 11 层）

| 层 | 内容 | 代表锚 |
|---|---|---|
| L01 依赖与数据集注册 | requirements.txt 钉版本（llamafactory 0.9.2/vllm 0.7.3）；两份 dataset_info.json（data/ 版 4 文本集+mmrait，RL_KTO/data/ 版 7 个 KTO 集） | data/dataset_info.json |
| L02 文本域构建族 | 5 个同构 process_*.py；pubmed/medqa 是 embedding+Qdrant 检索双胞胎，pubhealth/casehold/finfact 覆盖健康/法律/金融 | process/process_pubmed.py:34 |
| L03 多模态构建与筛选 | mmrait 构建插 `<image>` 占位并整目录拷图；select_true「答对才留」质量闸门 | process/select_true.py:49 |
| L04 vLLM 推理蒸馏 | 文本/多模态/拒绝采样三版同构 + aiohttp API 备用通道（无本地 GPU 时用） | inference/vllm_infer_text.py:81 |
| L05 自研 SFT 线 | torchrun 8 卡 + FSDP 三胞胎配置 + 只对回答段计 loss | train/sft.sh:16 |
| L06 LLaMA-Factory 线 | 薄入口+4 个 YAML（全参/LoRA/多模态）+ ZeRO-3 双 offload+merge_lora 导出 | train/train.py:5 |
| L07 RL_KTO 偏好优化 | 推理产物转 kto_tag 对话对，Llama-3.1-8B 全参 KTO（sigmoid/beta 0.1） | RL_KTO/train_kto.sh:16 |
| L08 预实验·准备 | 基模加 [RETRIEVAL]/[ENTITIES]/[SEP]/[REASONING] 四特殊 token 并 resize 词嵌入；3 个 preprocess 转 x/R_x/r/output 四元组 | Pre_Experiment/customize_model.py:4 |
| L09 预实验·度量 | VLLMLossCalculator 用 prompt_logprobs 把答案对数概率拆成知识损失 L_A 与推理损失 L_B | Pre_Experiment/pre_experiment.py:27 |
| L10 demo 与评估 | 文本/多模态两条一键复现线 + 统一评估出口 | eval/eval.py:6 |
| L11 主文档 | readme 17 节权威手册 | readme.md |

## 4. 核心链路走读：一条数据的旅程（文本线）

1. **构建**：`process_pubmed.py` 读 rare_share 原始数据（:141）；DocumentProcessor（:34）用 llm-embedder embedding+`QdrantClient(":memory:")` 向量库（:44），每题检索 top-3 文档块（:110），塞进模板（:19-31，规定 `<think>/<answer>` 输出合同），真值写 `<answer>{gold}</answer>`（:200），落盘 `data/train_pubmed.json`（:220）。
2. **蒸馏**：`vllm_infer_text.py` 按模型族包装题面（:21-33），QwQ-32B 批量生成（:146），输出写回 `predict` 键（:153），写前备份 .bak（:158）。升级版 `vllm_infer_text_reject_sampling.py` 温度多采样、check_answer 只留答对（:108-112），readme.md:134 推荐替代前者。
3. **筛选**：`select_true.py` 用 extract_option 比对 output 与 predict（:57-70），答对样本产出 `*_true.json`（:77）；`--mm` 连带拷图（:79-99）。
4. **训练（自研线）**：`sft.sh:16` torchrun 8 卡拉 `sft.py`；sft.py:66-76 按模型族拼 chat 模板——训练文本是 instruction+**predict**（教师思维链才是学习目标）；:116 DataCollatorForCompletionOnlyLM 只对回答段计 loss；:125 SFTTrainer；FSDP 粒度=fsdp_config_llama.json 的 `LlamaDecoderLayer`。
5. **训练（LF 线）**：accelerate launch → train.py:5 `run_exp()` → training_args.yaml（`dataset: pubmed` 按名引用注册表，超参与 sft.sh 一一对应）。
6. **推理+评估**：vllm_infer_text 对 `data/test_pubmed.json` 生成、写 `llm_predict_rare_llama` 键；eval.py:6-22 四级正则（`<answer>` 闭/开标签→行首字母→Answer:）抽选项，calculate_accuracy（:25）算准确率。

## 5. 运行与调试

- **环境**：readme.md:58-66，py3.10+requirements.txt；vllm==0.7.3/flash-attn==2.7.2 较老，新卡先确认 CUDA 兼容。
- **数据需自生成**：文本线先下载 rare_share 并解压 3 zip（readme.md:93-96），mmrait 线下载 whalezzz/M2RAG（demo:3）再跑 process/。
- **fsdp 三胞胎怎么选**：三个 json 只差一行 `transformer_layer_cls_to_wrap`——llama/mistral/qwen 分别对应 *DecoderLayer；换基模只改 sft.sh:27 的 `--fsdp_config` 指向。
- **accelerate_config_mm.yaml 不存在**：readme.md:192 与 demo/qwenvl_mmrait_rare.sh:20 都引用，但 train/ 下只有 accelerate_config.yaml——多模态线复用它即可。
- **两线怎么选**：自研线直读 json 更快；LF 线是官方兜底（LoRA/多模态/KTO 全在此线）。硬件量级 demo 自述 8×A100 起；KTO 的 ZeRO-3 双 offload 是 8B 全参显存兜底。
- **调试切入口**：先单跑 `process_pubhealth.py`（最轻）核对格式；prediction_key 写回机制可在同一 json 上多次推理、eval 按 key 区分。

## 6. 已知 bug 与坑（源码实证）

1. **pre_experiment.py 双杀**：①:66-67 `list(set(convert_tokens_to_ids(...)))` 括号未闭合（开 4 关 3），SyntaxError 起不来，且 list 塞 set() 本身 unhashable。②argparse 名不匹配：定义 `--model_path_or_name`（:18）/`--dataset_name`（:22），:93 却用 `args.model_path`、:113 用 `args.data_name`——修完语法必再撞 AttributeError。
2. **customize_model.py:28 三连击**：传了 args.model_name、args.special_tokens 两个未定义属性（定义的是 model_name_or_path），且函数签名（:4）只收 2 参却传 3 个。
3. **train_kto.sh 未定义变量**：:19 `${model_path}`、:26 `${len}` 未定义（定义的是 model_name_or_path:2），bash 展开为空，llamafactory-cli 拿到空参数。
4. **test_mmarit.json 拼写**：demo/qwenvl_mmrait_rare.sh:34 评估用 `data/test_mmarit.json`（少个 r），同脚本 :28 推理与 process_mmrait.py:9 真实产物都是 `test_mmrait.json`——照抄必 FileNotFoundError。
5. **extract_option 重复实现（实为四处，非三处）**：eval/eval.py:6-22、process/select_true.py:8-22、RL_KTO/process_kto.py:5-15、inference/vllm_infer_text_reject_sampling.py:85-105 逐字复制；reject_sampling 版多「只保留首字母」（:103-105），改抽取规则须四处同步。
6. **补充三坑**：readme.md:129 引用 `scripts/vllm_infer_mm.py` 不存在（实际在 inference/）；sft.sh:19 `--train_file_path="data/train_pubmed"` 缺 `.json`（sft.py:57 直接 open 必失败，demo 同参数带 .json）；RL_KTO/data/dataset_info.json:44 finfact_kto 指向 `train_finfact.json`，与其他 `*_kto.json` 命名不一致。

## 7. 上游与生态

- **org 归属**：remote 指 github.com/OpenDCAI/RARE；readme.md:7 徽章仍写旧名 Open-DataFlow/RARE——org 已改名，以 OpenDCAI 为准。姊妹仓有 DataFlow（主仓，通用数据清洗流水线框架，RARE 可视为其在推理数据方向的论文级实例）、DataFlex/DataMind/One-Eval/Data-Preparation-Bench 等。
- **论文定位**：arXiv:2503.23513（Wang et al.，PKU），2026/05 KDD 2026 接收（readme.md:13）；数据发布在 HF RARE111/rare_share（readme.md:5）。预实验（L08-L09）是立论实验：L_A/L_B 分解验证「检索对推理的贡献大于对知识记忆」。
- **致谢上游**（readme.md:354）：LLaMA-Factory（L06/L07 训练框架）、s1（蒸馏方法论参考）。

## 8. 学习路径

**12 步 tour 走法**（tour 顺序即学习顺序，5 天）：

- 第 1 天 **s01-s02**：通读 readme 建立框架，对照两份 dataset_info.json 吃透注册表模式；
- 第 2 天 **s03-s05**（process 层）：先读最简的 process_pubhealth.py，再啃 pubmed/medqa 双胞胎，最后 mmrait+select_true；
- 第 3 天 **s06-s07**（inference 层）：text 与 reject_sampling 对照读（同构+增量最易迁移），api_infer_post 了解即可；
- 第 4 天 **s08-s10**（train+KTO）：两线并行对比——同一组超参在 sft.sh 与 training_args.yaml 一一对应，是理解 FSDP vs ZeRO-3 双 offload 的活教材；
- 第 5 天 **s11 预实验**（论文核心假设，先修第 6 节 bug 才能跑）+ **s12 demo 串读**收尾，自测：能否默写一条数据到准确率的键名变迁。

**explain 6 篇配套**（与 tour 配读）：①process_pubmed 深讲（s03-s04）②vllm 推理三兄弟（s06-s07）③自研 FSDP 训练线（s08）④LLaMA-Factory 配置宇宙（s09）⑤RL_KTO 与预实验（s10-s11）⑥demo+eval 端到端（s12）。每读一篇回 demo dry-run 对应命令最快内化；修第 6 节五类 bug 就是最好的练手题。
