# NVIDIA cosmos 仓新人导读（ONBOARDING）

> 基线：git `3e3c6d61`（2026-09-29，"Add TensorRT-LLM Transfer and Action guides (#310)"）。1179 个 git 追踪文件（知识图谱分析其中 1097 个文本文件），图谱 3694 节点 / 8276 边 / 16 层 / 16 步 tour。本文所有路径与行号均按该 commit 从源码核实。

## 1. 一句话定位

**这是 NVIDIA Cosmos 世界模型家族的「评测 + 教程」仓**：Reasoner 推理评测 = `evaluation/cosmos3/reasoner/vlmevalkit/`（整棵 vendored 的 VLMEvalKit fork，内嵌 NVIDIA Metropolis TAR/VANTAGE 基准与 `cosmos_eval/` 一键复现套件）；Generator 评测 = `evaluation/cosmos3/generator/`（五套生成基准）；教程 = `cookbooks/cosmos3/`（四线 notebook + SFT/蒸馏配方 + NIM 文档群）。

**理解本仓的第一关键：cosmos-framework 本体不在仓内。** 仓根 `README.md:76` 的四仓分工表写得明白——本仓只管「探索、运行、评测」；训练（SFT/LoRA/RL/蒸馏）在 cosmos-framework，数据治理在 cosmos-curator，自动评测系统在 cosmos-evaluator。cookbooks 里所有 finetune 脚本都是 `python -m cosmos_framework.scripts.train --sft-toml=...` 形式的「配方入口」（见 `cookbooks/cosmos3/reasoner/finetune/launch_sft_videophy2_nano.sh`），真实训练代码在外部 pip 包里。在本仓找训练实现会一无所获——这是新人第一个方向性坑。

模型谱系（`docs/reference/models.md`）：Cosmos3 三档基座 Super 64B / Nano 16B / Edge 4B，统一 Mixture-of-Transformers（自回归 + 扩散双 Transformer 共享权重）omnimodal 架构，两个「表面」：**Reasoner**（图文视频理解推理）与 **Generator**（t2v/i2v/transfer/action 视听动作仿真）。仓根 README 的 quickstart 用 diffusers 的 `Cosmos3OmniPipeline` 十分钟出第一条视频（需 Guardrail 门控登录）。

## 2. 仓库全貌

1179 个追踪文件的分布高度不均，一条主线（评测栈）+ 三条辅线（教程/配方/部署）：

| 目录 | 文件数 | 内容 |
| --- | ---: | --- |
| `evaluation/cosmos3/reasoner/` | 880 | 全部是 `vlmevalkit/` 这棵 vendored fork（含其自带 docs/CI/scripts），占全仓 75% |
| `cookbooks/cosmos3/generator/` | 172 | action / audiovisual / transfer 三线教程 notebook、finetune/distill 配方、LeRobot 动作数据样例 |
| `evaluation/cosmos3/generator/` | 41 | 生成侧五套基准：paibench_c / paibench_g / physics_iq / rbench / unigenbench（notebook 入口 + scorer 脚本 + specs + patches） |
| `cookbooks/cosmos3/nim/` | 33 | NIM 推理微服务文档群（deployment/configuration/support-matrix 等）+ `examples/` 全功能 REST 示例 |
| `cookbooks/cosmos3/reasoner/` | 32 | 六本推理 notebook + `reasoner_prompt_guide.md` + finetune 配方 |
| 仓根 | ~10 | `README.md`、`inference_benchmarks.md`（59KB，全仓最重文档：三档模型 × 双表面 × 多后端延迟基准总表）、`docs/reference/models.md`、`RELEASE.md`、`CONTRIBUTING.md`、`SECURITY.md`、`.github/workflows/validate-notebooks.yml`（notebook 校验 CI） |

读图要点：evaluation/reasoner 与 cookbooks 的文件比约 880 vs 237——**评测栈才是本仓的主体工程**，cookbooks 是面向用户的薄层；而评测栈里 312 个文件又集中在 `vlmeval/dataset/utils/`（判分器群），是最大的单簇。

## 3. 核心架构：vendored VLMEvalKit 的分层

fork 保留了上游 VLMEvalKit 的经典分层（自底向上六层 + 一个编排层）：

1. **smp 基座**（`vlmeval/smp/`）：`file.py`（LMUDataRoot 数据根、按扩展名分派的 dump/load、带重试下载与断点续评复用）、`log.py`、`misc.py`（分布式）、`vlm.py`（模型自动加载）。`smp/__init__.py` 星号再导出，是全仓被引用最多的工具面（fan-in 308）。
2. **模型注册表** `vlmeval/config.py`（2663 行）：约 80 个 partial 工厂组聚合成 `supported_VLM` 大表，模型名 → wrapper 构造参数。NVIDIA 增量在此：`cosmos_series`（:2425，`Cosmos-Reason1-7B` 走 `vlm.Cosmos`+vLLM）与 `cosmos_reason1_7b`（:173，`api.CosmosReason1`，api_base 指向 lepton.run 公开演示端点）。
3. **数据集层**（`vlmeval/dataset/`）：`__init__.py` 聚合 import 225 个数据集类，组成 IMAGE/VIDEO/TEXT/CUSTOM/COLLECTION 五类 `DATASET_CLASSES`（:401），展开成 `SUPPORTED_DATASETS` 总表；`build_dataset` 工厂（:448）按名查找并兜底 CustomMCQ/VQA。基类体系：`image_base.py` 的 `ImageBaseDataset`（39-216 行：TSV 载入、MD5 校验与 legacy 文件名迁移、base64 图像落盘、≤64 字符的图像间接索引解析）与 `video_base.py` 的 `VideoBaseDataset`（17-264 行：decord 抽帧的 nframe/fps/pack 三模式、LMU 帧缓存）；`image_mcq.py`（单文件 30 类、基类 53-476 行，含 circular/heuristic/verifier 三条评估路径）等是其题型特化。190+ 基准名全部由此派生。
4. **本地模型 wrapper 层**（`vlmeval/vlm/`，195 文件）：`base.py` 的 `BaseModel`（9-224 行）定义 generate/chat 两级入口（内容归一化后分派 `generate_inner`/`chat_inner` 抽象方法）；60+ 家族 wrapper。NVIDIA 自有两支：`vlm/cosmos.py`（vLLM 本地）与 `vlm/cosmos_reason_hf.py`（`CosmosReasonHF`，HF 直跑、VIDEO_LLM=True 整视频输入）。
5. **API 后端层**（`vlmeval/api/`，48 文件）：`base.py` 的 `BaseAPI`（12-335 行：retry/wait 重试循环包裹 `generate_inner`、多模态消息模板、pickle 状态裁剪）；44 个后端适配（gpt/gemini/claude/国产系）。`api/cosmos_reason.py` 是 Cosmos reasoner 推理服务接入，与 vlm/ wrapper 在 `run.py` 层面等价互换（`build_model_from_config` 先查 `vlmeval.api` 再查 `vlmeval.vlm`）。
6. **推理管线**：顶层 `run.py`（551 行主入口，`--data`+`--model` 或 `--config` JSON 二选一）按数据集模态分发到 `vlmeval/inference.py`（图像 `infer_data_job`）、`inference_video.py`（`infer_data_job_video`）、`inference_mt.py`（多轮）、`inference_api.py`；带 GPU 探测、分布式 rank 切分与断点续评。`run_api.py` 是纯 API 模式入口。
7. **判分中枢**（`vlmeval/dataset/utils/`，312 文件）：`multiple_choice.py`（选择题 + 两轮循环评测）、`judge_util.py`（`build_judge` 构造 LLM 判官 + JudgeTracker 落盘抽取失败）、各基准专用判分子目录；`vlmeval/utils/__init__.py` 的 can_infer 系列做答案推断；`vlmeval/tools.py` 管理已缓存结果的提取展示——排错先看这里的结果目录约定。
8. **cosmos_eval 编排层**（fork 顶层新增，`cosmos_eval/`）：`run_all.py` + `manifest.json` + `models/` + `data/` + `parse_score.py`，见 §4。

分层阅读心法：**任何一条评测 = 模型（vlm/ 或 api/）× 数据集（dataset/）× 判分（dataset/utils/）的组合**，三层在 `run.py` 汇合；fork 的增量集中在第 3 层（metropolis/vantage/av_* 系基准）与第 8 层。

## 4. 关键模块深读（七件）

**（1）`run.py`（551 行）——评测总闸门。** 解析 CLI/YAML/JSON 配置后构建模型与数据集，执行推理、评分并汇总输出。三个要点：`--config` 模式断言 `--data`/`--model` 必须为空（:230-232），这是 cosmos_eval 驱动它的方式；judge 默认值是一张按数据集名路由的巨型 if/elif 表（MCQ 类默认 chatgpt-0125、MathVista 系 gpt-4o-mini、VGRPBench gpt-4o 等）；只有 RANK==0 执行判分，分布式下先 `dist.barrier()` 对齐。

**（2）`vlmeval/dataset/__init__.py`——注册中枢。** 195 条 import 聚合 225 个类；fork 特有基准（av_*/cosmos_*/metropolis_*/vantage_*、aetcbench、EgoExoBench、CGAVCounting 等）与上游基准混在同一张 `SUPPORTED_DATASETS` 里；EASI 团队增补的 7 个视频基准用 `VIDEO_DATASET += [...]` 追加。想知道某基准是不是真实现，先到这里查它挂在哪个类、再去读那个文件——stub 类也在这里 import（见 §7 坑 1）。

**（3）`image_base.py` + `video_base.py`——数据集骨架。** ImageBaseDataset：`load_data` → 无图行过滤（skip_noimg）→ 图像索引解析（image 列可存 base64 或指向另一行的短索引，≤64 字符判间接引用）→ `post_build` 钩子；`prepare_tsv` 带 MD5 校验与 legacy 文件名迁移。VideoBaseDataset：构造时探测 decord → 调子类 `prepare_dataset`（返回 data_file+root）→ 建 LMU 帧缓存；fps 与 nframe 互斥、都未设时对 VIDEO_LLM 模型放行（模型侧自己处理视频）、对非 VIDEO_LLM 模型则会在抽帧时报错。pack 模式按视频分组、非 pack 按题分组。

**（4）`vlmeval/api/cosmos_reason.py`（774 行）——Cosmos reasoner 的 API 双后端 wrapper。** `CosmosReason(BaseAPI)`（:234）：`VIDEO_LLM=True` + nframe/fps/total_pixels/max_pixels/min_pixels/max_frames 视频参数族；`__init__` 从环境变量读 `COSMOS_API_KEY`，随后 `_check_endpoint_health()` 探活、`_resolve_model_name()` 查 `/v1/models` 在声明名与端点不符时自动改名（5 次重试）。「双后端」体现在两处：`use_nim` 开关切 NIM 语义，`extra_body` 透传 vLLM 专属字段（如 structured_outputs），`response_format` 支持逐基准 JSON schema 约束输出。视频路径：`tensor_video_to_base64` / `process_video_info_to_video_url`（借 qwen_vl_utils 的 process_vision_info）+ `use_video_cache` 挂 `vlmeval/utils/video_cache.py` 缓存。类族：CosmosReason1（model='cosmos_reason1_7b'）→ CosmosReason1Think；CosmosReason2（默认 model='qwen3_30b_a3b'，即 Cosmos3 reasoner 的服务名）→ CosmosReason2Think → Qwen3VLThink（:766）。`generate` 还覆写了基类（:667）以带统计与错误类型追踪。

**（5）`vlmeval/vlm/base.py` + `vlm/cosmos_reason_hf.py`——本地对照组。** BaseModel 的两级入口契约是全部 60+ wrapper 的公共形态；`CosmosReasonHF` 是「不开服务、进程内直跑」的那一支：Qwen2-VL 架构视频语言模型，fps 默认 16、total_pixels 默认 8192×28×28，数据集侧传来的视频参数会覆盖模型默认。与 api/cosmos_reason.py 构成「本地 / 远程」两条接入路径。

**（6）`vlmeval/dataset/utils/megabench/metric_type.py`——lazy_import 判分注册表。** `MetricType` 枚举 → `class_impl` cached_property 里几十条 `lazy_import("vlmeval.dataset.utils.megabench.scoring.<模块>", "<类名>")` 映射：精确串匹配、bbox IoU、坐标序列、LaTeX 等值、BLEU/GLEU、NLI 蕴含……判分器按需加载，避免 312 个判分文件的依赖全部常驻。修 MegaBench 系评分问题从这张表定位实现文件最快（nli_entailment 的坑见 §7 坑 8）。

**（7）`cosmos_eval/`——一键复现套件。** `run_all.py`（279 行，stdlib only，无 vlmeval-metric 依赖）：读 `manifest.json`（9 个基准：AETCBench_all + 8 个 VANTAGE_*，统一 api_nproc=8/judge_nproc=4）→ `load_model_layer`（`models/cosmos.json`：class=CosmosReason2，默认 enable_thinking=false、max_tokens 8192、timeout 600、retry 10、temperature 0）+ `load_data_conf`（`data/metropolis/<bench>.json` 数据集层）→ dumb dict-merge compose 出每基准一份 `run.py --config` JSON（`_render_env` 展开 `${COSMOS_API_BASE}` 等环境变量）→ ThreadPoolExecutor 并发跑 stock `run.py` → `parse_score.py` 报分。两个精妙细节：逐基准 override 在 model 层内（VANTAGE_DVC max_tokens 16384+total_pixels 8MiB、VANTAGE_SOT response_format json_schema strict）；`_CONCAT_BENCHES={"VANTAGE_Astro2D"}` 特例——ConcatDataset 基准判分时 `eval_file.replace(dataset_name, sub_name)` 会重写路径里的一切同名成分，work-dir 路径含基准名就会 FileNotFoundError，故给它编号目录。`parse_score.py` 是内部 `vlmeval_metric/score_parser.py`+`eval_data.py` 的 verbatim vendored port，靠维护者 CI 对拍保证公开分数与内部管线一致。

## 5. 数据流走读：VANTAGE_SOT 从配置到分数

以 manifest 里的视频基准 VANTAGE_SOT（单目标跟踪：一样本 = N 帧独立图像，第 0 帧带 GT bbox 初始化，模型须在单次 JSON 响应里输出其余帧的 bbox）为例，走完整旅程：

1. **编排**：`cosmos_eval/run_all.py` 读 manifest.json 取 `metropolis/VANTAGE_SOT` 条目与 run flags；compose 合并 `data/metropolis/VANTAGE_SOT.json`（数据集层：TSV/视频路径/S3 配置）与 `models/cosmos.json` 的 VANTAGE_SOT override（response_format json_schema、name=sot_predictions、strict），环境变量渲染后写成一份 config JSON，subprocess 拉起 stock `run.py --config <cfg>`。
2. **构建数据集**：run.py 走 `build_dataset('VANTAGE_SOT')` 命中 `vantage_sot.py:515` 的 `VANTAGE_SOT(VideoBaseDataset)`（TYPE='SOT'，DATASET_CONFIGS 还带 tiny/16f 等变体）；`prepare_dataset` 优先查本地 `LMUDataRoot()/datasets/` 完整性（TSV+videos 目录），否则经 s3fs 从 VANTAGE-bench S3 stage 拉「HF-release-with-annotations」子集——**注意数据尚未公开发布**（fork README 明示 VANTAGE/TAR challenge 进行中）。
3. **构建模型**：config 的 model 段经 `supported_VLM`/类名分派构造 `CosmosReason2`（api 层）；`__init__` 探活端点并 resolve 模型名，`COSMOS_API_BASE/COSMOS_MODEL/COSMOS_API_KEY` 三个环境变量在此生效。
4. **推理**：run.py 按 MODALITY=VIDEO 进 `inference_video.py:231` 的 `infer_data_job_video`。`build_prompt_input` 携带 `VIDEO_LLM` 标志；VANTAGE_SOT.build_prompt（vantage_sot.py:738）在图像序列模式下还会 `extract_target_crop`（:187）裁出首帧目标 crop 作提示；CosmosReason.VIDEO_LLM=True 时视频整体进 `model.generate` → BaseAPI 重试循环 → `generate_inner`（vlmeval/api/cosmos_reason.py:536）把帧/视频 base64 化并命中 `vlmeval/utils/video_cache.py` 缓存；请求体带 strict JSON schema 约束输出。预测逐题落盘 work_dir 的 `{model}_{dataset}_*.pkl/.xlsx`（断点续评即靠这些中间文件）。
5. **判分**：RANK==0 调 `VANTAGE_SOT.evaluate`（vantage_sot.py:810）：逐行 `parse_sot_response` 正则抽各帧 bbox → `compute_sot_metrics` 对 gt_bboxes/frame_ids/occluded 算跟踪指标 → `compute_seq_tags` 按遮挡/同窗多目标拥挤/robot-vs-person 打标签分桶出子分；`--save-eval-results` 把分数写 `*.eval.json`。
6. **出分**：cosmos_eval 侧 `parse_score.py` 读 eval JSON：先 `_detect_format` 判 A（标量 dict）/B（多 split 数组）/C（索引列表）/D（纯数值）四种格式，再套每基准 override，报 headline Overall（0-100 归一）+ 全部原生子分键；run_all.py 汇总打印。

一条弯路提示：这条链上「视频帧抽取」只发生在非 VIDEO_LLM 模型（数据集侧 decord 抽帧拼多图）；对 Cosmos reasoner 全程是模型侧处理，`video_base.py` 的 fps/nframe 校验对它只警告不拦截。

## 6. 设计决策与取舍

**（1）为什么 vendored fork 而非依赖上游 VLMEvalKit。** fork 层 `evaluation/cosmos3/reasoner/vlmevalkit/README.md` 开宗明义：目的是让 cosmos-reasoner 在 Metropolis 基准上的分数「publicly reproducible」。整棵钉死在仓内 = 推理与判分引擎版本不随上游漂移，历史分数永远可复现；也便于深度改造（fork 改了 dataset 注册表、api 层、视频缓存等骨架代码）。代价：880 文件的维护面积、上游修复不会自动同步（上游文档 `docs/en/Quickstart.md` 等原样随附，路径漂移就开始出现，见 §7 坑 5）。

**（2）公开版剥离的 stub 边界。** 45 个数据集类是 17 行骨架：文件头注释「Stub: dataset implementation not included in this public release」、`supported_datasets()` 返回空列表、`__init__` 直接 `raise RuntimeError`。它们**全部仍被 import 进 `dataset/__init__.py`**，多数还挂在 DATASET_CLASSES 列表里（如 CosmosCABVideoGeneral/Camera 在 VIDEO_DATASET）——内外一套代码、公开版只掏空实现。因为 supported_datasets() 为空，这些名字不会进 SUPPORTED_DATASETS，`--data` 按名找不到；但任何直接实例化路径（被其他代码/config 引用）都会当场 RuntimeError。

**（3）fork 新增基准：真实现与 stub 并存。** metropolis 系（metropolis_vqa 861 行、metropolis_dvc 776、metropolis_event_verification/temporal）、vantage 系（vantage_sot 968、vantage_pointing 219）、aetcbench 778 都是真实实现；而 videophy2.py 反而是 17 行 stub——但 reasoner SFT 配方（`finetune/toml/sft_config/videophy2_sft_nano.toml` + launch 脚本三档）完整可用，因为训练数据准备走 cosmos-framework 的 `prepare_videophy2_from_hf`，与仓内评测数据集类互不相干。「数据集类是 stub」≠「这条线不能做」。

**（4）parse_score.py 的 verbatim vendored port。** 宁可整段搬运内部模块也不重写，文件头直接警告不要手改、由生成器再生，且维护者 CI 用同一批 eval JSON 对拍内外两版断言输出一致——「公开分数必须与内部管线 bit 级一致」压倒代码优雅。

**（5）cookbooks 的后端矩阵。** `cookbooks/cosmos3/README.md` 用一张后端表统一环境说明：Cosmos Framework（torchrun 原生）、Diffusers、TensorRT-LLM Generator/Reasoner 两面、Transformers、vLLM（Reasoner）、vLLM-Omni（Generator）、NIM 三种容器——同一能力多后端复用一套教程骨架，CUDA 驱动与 cuXXX torch 版本匹配、Guardrail 关闭方式（各后端开关不同）都集中在此表。Generator 三线（action 的 fd/id/policy 三任务、audiovisual 的 t2v/i2v、transfer 视频迁移）与 reasoner 六后端 notebook 都挂在这张表下。

**（6）cosmos-framework 外置。** 训练配方 = launch 脚本（torchrun FSDP）+ TOML 配置 + 数据准备入口三件套，三档基座 × 四条任务线（videophy2 物理合理性 SFT、llava-ov SFT、action 的 DROID/LIBERO/RoboCasa 策略后训练、audiovisual 的 t2i/i2v 四步蒸馏）全参数化；本仓不留一行训练代码，评测与教程才是它的本体。

## 7. 已知坑与勘误（新人别踩清单）

按「先踩会痛」排序，全部经源码逐条核实（含对批量分析结论的两处修正）：

1. **45 个公开版剥离 stub**（videophy2 / cosmos_cab_image / cosmos_cab_video / cosmos_erqa / cosmos_reason / worldbench / IFBench/ifbench / Omni3D / av_* 系 / blink_depth / camera_bench / causalvqa / motionbench / mvpbench / spar_bench 等）：注册表里看得见、跑不起来。判别法：文件头「Stub: dataset implementation not included in this public release」。选基准前先 grep 这行。
2. **6 本孤儿 SGLang notebook**：`cookbooks/cosmos3/reasoner/run_with_sglang.ipynb`、`generator/transfer/run_video_transfer_with_sglang.ipynb`、`generator/audiovisual/run_with_sglang.ipynb`、`generator/action/run_{fd,id,policy}_with_sglang.ipynb`——全仓任何 cookbook README 都不含 "sglang" 一词（reasoner README 只链了 5/6 本，transfer 4/5，audiovisual/action 的 sglang 本同样未收录）。批量分析报「两个」是低估，实测 6 本全部无文档入口；能用但版本兼容性自担，引用前先跑通第一个 cell。
3. **RELEASE.md 双坑**：两行都链 `release_notes/v0p1.md`，该路径在仓内不存在（v1.0 行链的还是 v0p1 文件）；且内容是 2024-11/2025-01 旧世代（tokenizer/WFM 首发），与当前 Cosmos3 世代存在代差。看版本以 git tag 为准。
4. **`reasoner/vlmevalkit/requirements.txt:48` 注释粘连**：`# acceleratepython-box` 一行把 accelerate 和 python-box 都吞进注释——`pip install -r` 后两者皆缺，本地 vlm wrapper（需 accelerate）与依赖 python-box 的代码会 ImportError。装完环境先补这两个包。
5. **vendored 文档路径漂移**：`docs/en/Quickstart.md:141` 引用上游 `vlmeval/vlm/internvl_chat.py`，本 fork 已重组为 `vlmeval/vlm/internvl/internvl_chat.py`。fork 内文档一律先按磁盘实际路径核对。
6. **`vgrpbench/score.py:439`**：`if __name__ == '__main__': main()`，但全文件 440 行没有 def main——直接 `python score.py` 必 NameError。VGRPBench 的正确判分入口是同目录 `evaluation.py`。
7. **`vgrpbench/puzzles/common_get_game_factory.py:43`**：21 个 if/elif 分支没有 else，未知 game_type 直落 `return GameFactory` → UnboundLocalError。新增谜题类型忘了登记时就是这种炸法（报错点在 return 行而非 dispatch 处，注意甄别）。
8. **`megabench/scoring/nli_entailment.py:13` 类型守卫疑似写反**：`if not isinstance(response, str) or isinstance(correct_answer, str): return 0`——正常 (str, str) 输入条件为 True 直接 0 分；只有 correct_answer 非 str 才进 NLI 管线（随后大概率在 .strip() 处炸）。MegaBench 走 NLI_ENTAILMENT 指标的全 0 结果，先查这里（第二个 isinstance 疑漏 not）。
9. **`SArena/video/FVD.py:67` 键契约错位**：`calculate_score` 只读了 `pred_video_fvd`/`overall_video` 两键，`meter.update` 却取 `batch['gt_video']`——按 FVDCalculator 自己声明的键构造 batch 会 KeyError。SArena 指标族的入参契约以 `SArena/base_metric.py` 的七键（gt_im/pred_im/gt_video/pred_video/gt_svg/pred_svg/caption）为准。
10. **eval()/exec() 注入面**：`NPMM/maximum_set.py:24` 对模型输出 `answer_part` 直接 `eval()`（方括号格式即触发）；`megabench/scoring/program_judge.py:96/99` `exec(self.user_code)` 执行模型生成代码（设计使然，无沙箱）；另有十余处对 TSV/预测文本的裸 eval()（`miabench.py:14-15`、`dataset/worldsense.py:289`、`mathvista.py:84`、`bmmr_grade.py:163` 等，全清单见附录表第 12 行）。跑不可信来源的评测数据或模型输出 ≈ 任意代码执行，务必在最小权限环境。
11. **dotfile 假阴性（对批量结论的修正）**：`cookbooks/cosmos3/nim/AGENTS.md` 引用的 `.agents/skills/cosmos3-nim-user/SKILL.md` **实际存在且被 git 追踪**（commit 3e3c6d61 引入）。批量分析判「不存在」是 `ls` 不带 `-A` 看不见隐藏目录的经典假阴性。结论：该引用有效；教训：找 NIM 文档群相关文件一律 `ls -A`。
12. **VANTAGE/TAR 数据未公开**：fork README 用加粗警示 challenges 进行中、数据集暂不可得；metropolis/vantage 的 `prepare_dataset` 走内部 S3（s3fs 凭据）。公开复现当前只有 configs 参考，端点自备（COSMOS_API_BASE）时能跑通管线但数据侧要等发布。

## 8. 上手路径（前三天，结合 16 步 tour）

**Day 1 建坐标系（tour step 01-02）**：`README.md`（定位 + 四仓分工 + quickstart）→ `inference_benchmarks.md`（对各后端延迟建立量级预期）→ `docs/reference/models.md`（三档模型谱系）→ `cookbooks/cosmos3/README.md` 后端表（决定你用哪条推理栈）。全程半天足够，重点是内化「本仓没有训练代码」。

**Day 2 评测栈纵深（tour step 02→03→04→07→08→11）**：`run.py` 通读 CLI 与主循环 → `vlmeval/smp/` 四件（file/log/misc/vlm）→ `dataset/__init__.py` 注册机制 + `image_base.py`/`video_base.py` 两基类 → `vlm/base.py` 与 `api/base.py` 两基类对照 → 精读 `api/cosmos_reason.py` 全文 → `cosmos_eval/` 三件套（run_all/manifest+models/parse_score）。动手题：`python cosmos_eval/run_all.py --export-configs ./cfgs` 导出一份组合配置逐字段读——比真跑十遍更懂 compose 逻辑。

**Day 3 教程与训练面（tour step 12-16）**：generator 五套基准 README（`physics_iq/README.md` 带 Cosmos3-Super 参考分 I2V 43.8 / V2V 59.7，先跑 `setup_*_scorer.sh` 装外部打分器）→ reasoner 六后端 notebook（跳过或专门审无文档的 sglang 本）→ 任一 `finetune/launch_sft_*.sh` 读出 cosmos_framework 依赖链 → `nim/` 文档群（deployment/support-matrix + `examples/reasoner.py` 等 REST 示例）收尾。想贡献代码再看 `CONTRIBUTING.md`（Python 3.10+、CUDA 12.8/13.x、uv≥0.11.3）与 `.github/workflows/validate-notebooks.yml`（notebook CI 校验，改 notebook 必过此关）。

## 附：勘误与死代码清单

路径均相对 `evaluation/cosmos3/reasoner/vlmevalkit/`（个别注明仓根）。

| # | 位置 | 现象 | 影响 | 处置 |
| --- | --- | --- | --- |---|
| 1 | 仓根 `RELEASE.md` | 死链 `release_notes/v0p1.md`（v1.0 行也链它）；内容为 2024-25 旧世代 | 版本信息误导 | 以 git tag 为准 |
| 2 | `reasoner/vlmevalkit/requirements.txt:48` | `# acceleratepython-box` 注释粘连 | accelerate 与 python-box 双双缺席 | 安装后手动补装 |
| 3 | `docs/en/Quickstart.md:141` | 引上游 `vlm/internvl_chat.py` 旧路径 | 文档导航扑空 | 实路径 `vlmeval/vlm/internvl/internvl_chat.py` |
| 4 | `vlmeval/dataset/utils/vgrpbench/score.py:439` | `__main__` 调用未定义的 `main()` | 直跑 NameError | 判分入口改用同目录 evaluation.py |
| 5 | `.../vgrpbench/puzzles/common_get_game_factory.py:43` | 21 分支无 else，`return GameFactory` 未绑定 | 未知 game_type → UnboundLocalError | 补 `else: raise ValueError` |
| 6 | `.../megabench/scoring/nli_entailment.py:13` | 类型守卫 `or isinstance(correct_answer, str)` 疑漏 not | 正常输入恒 0 分 | 修正第二条件为 `not isinstance(...)` |
| 7 | `.../SArena/video/FVD.py:67` | 只读 pred_video_fvd/overall_video 却取 `batch['gt_video']` | KeyError | 统一 base_metric.py 七键契约 |
| 8 | `.../NPMM/maximum_set.py:24`；`.../megabench/scoring/program_judge.py:96,99` | 裸 `eval()` 模型输出 / `exec()` 模型代码 | 任意代码执行面 | 沙箱运行；可换 ast.literal_eval 处 |
| 9 | `vlmeval/dataset/` 下 45 个 stub 文件（如 `cosmos_cab_image.py`、`videophy2.py`、`worldbench.py`、`IFBench/ifbench.py`、`Omni3D/omni3d_dataset.py`） | 17 行 RuntimeError 骨架仍入注册表 | 名义基准不可运行 | 认准 stub 头注释 |
| 10 | `cookbooks/cosmos3/` 下 6 本 `*sglang*.ipynb`（reasoner/transfer/audiovisual/action×3） | 无任何 README 收录 | 孤儿教程，无版本承诺 | 引用前自验 |
| 11 | 仓根 `cookbooks/cosmos3/nim/AGENTS.md` → `.agents/skills/cosmos3-nim-user/SKILL.md` | 引用**有效**（批量判死是 ls 漏隐藏目录的假阴性） | 易误判死链 | 排查一律 `ls -A` |
| 12 | `miabench.py:14-15`、`dataset/worldsense.py:289`、`mmsci.py:247`、`mathvista.py:84,139`、`dataset/tempcompass.py:151`、`qspatial.py:68`、`dataset/utils/qbench_video.py:41`、`lens.py:33-42`、`dataset/utils/vdc.py:80`、`bmmr_grade.py:163,304-306`、`chartmimic/evaluator/grid_evaluator.py:60`（均 `vlmeval/dataset[/utils]/` 下） | 对 TSV/预测文本裸 `eval()` | 不可信数据即注入面 | 只跑可信来源 |

——完。基线 commit 3e3c6d61；本导读由 understand-anything 知识图谱（3694 节点/8276 边/16 层/16 步 tour）驱动写作，全部锚点经源码复核。
