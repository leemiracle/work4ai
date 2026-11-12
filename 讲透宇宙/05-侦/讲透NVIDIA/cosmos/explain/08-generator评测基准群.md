# 08 · Generator 评测基准群：五套 fork 新增的生成侧基准

## ① 角色定位

`evaluation/cosmos3/generator/` 五套基准是 fork 为 Cosmos3 生成模型新增的评测线，与 reasoner 侧 vlmevalkit 完全独立。共同形态：每套一个 `run_with_cosmos_framework.ipynb` 入口，用 `python -m cosmos_framework.scripts.inference` 生成视频，评测器**全部外置**——要么 clone 上游评测库（PAI-Bench 用 SHI-Labs/physical-ai-bench、RBench 用 ReVidgen），要么自带 VLM 判官。分工：

- **paibench_c**（条件生成）：600 任务 × 4 控制模态（edge/blur/depth/seg），测空间可控性；
- **paibench_g**：AV 驾驶/机器人/工业/物理/人类/常识六域 1044 样本，T2V+I2V 双任务；
- **physics_iq**：198 prompt × I2V/V2V，专测物理合理性（Super 参考分 I2V 43.8 / V2V 59.7）；
- **rbench**：具身 650 例 × 9 类（single_arm/dual_arm/humanoid/quad 各 100，其余五类各 50，实测核对）；
- **unigenbench**：唯一自带判官（`ugb_scorer.py`）且**唯一没有 README**。

## ② 内部结构

**setup_paibench_scorer.sh**（220 行，paibench_g 环境管家）：:7-21 参数全可环境变量覆盖，:48 clone 后打印 scorer SHA——复现性第一道锚；:55-67 打 vLLM 兼容补丁（vLLM 0.14 拒绝对 dense Qwen2.5-VL 开专家并行而 pinned scorer 无条件开，patch 把 `enable_expert_parallel: True` 从 `vqa_evaluation.py` 删除），patch 幂等：`apply --check`→`--reverse --check` 二段识别，皆败即退；:69-84 打分布式 object-gather 补丁（上游把结果 dict 序列化进 CUDA byte tensor 再 gather，size 损坏会触发**多 TB 分配**，补丁改 `torch.distributed.all_gather_object`）；:86-95 防 notebook 导出的生成环境劫持安装（`UV_PROJECT_ENVIRONMENT` 同路径即报错）；:112-124 钉版本手术——GUI OpenCV 依赖 libGL → 换 `opencv-python-headless==4.11.0.86`+钉 `numpy==1.26.4`，DreamSim 0.2.1 放任 PEFT 到 0.19 与 Transformers 4.57 冲突 → `--no-deps` 强装 `peft==0.17.1`；:128-133 预置 DINO 绕开 GitHub 限流；:169-208 校验段断言 NumPy<2、断言 `gather_list_of_dict` 源码含 `all_gather_object`（:199-201，即补丁生效）、Detectron2 默认不装（:156-166）。

**run_motion_smoothness_sharded.py**（342 行）：AMT-S 运动平滑度的单机分片版，绕开 PAIBench 分布式评测器 process group。mp worker 按 GPU 认领队列，每视频完成即 `write_json_atomic`（:45-49，临时文件+`os.replace`）写断点；`write_merged_result`（:172-184）收尾严格对账——多出/缺失均报错，均值 `fmean` 落标准 schema。

**rbench 双脚本**：`setup_rbench_scorer.sh` 把 ReVidgen **钉死 commit b03df27f**（:14），打 `revidgen-configurable-openai-model.patch`——上游六个评测脚本全硬编码 `"gpt-5-2025-08-07"`，补丁逐处换 `os.environ.get("OPENAI_MODEL") or "gpt-5-2025-08-07"`；`setup_rbench_embodiment_scorer.sh` 是**独立第二环境** `.venv-rbench-ops`（:11），注释点名：Q-Align 要老 Transformers/PEFT 栈而 GroundingDINO 要对 CUDA 编译，与 VLM scorer 不相容；`MPLBACKEND=Agg`（:9）防 Jupyter 内联 matplotlib 进 headless。`revidgen-qalign-decode-once.patch` 是性能修复：滑窗逐窗 `VideoReader.get_batch()` 重复解码重叠帧，改为一次全量解码再索引。

**unigenbench/ugb_scorer.py**（480 行，NVIDIA 专有保密声明头 :1-13）：27 种 testpoint 的 `EXPLANATION_DICT`（:33-61）；`build_request()`（:153-184）把 testpoint 定义、逐条描述、**逐 testpoint 的输出 YAML 模板**（:144-150）全塞进 prompt；`parse_vlm_response()`（:187-229）三级校验——YAML 可解析、条数相等、verdict 可 coerce（:122-137），testpoint 名用 **NED ≤ 0.1** 容差匹配（:86-87 + :222-225）；`main()`（:333-461）批循环把解析失败样本塞回队尾重试（:430-433），结果按文件名前缀 `orig`/`phi` 分组（:292-301）算三套准确率。**utils.py 的 `GatewayVLM`**（:39-141）后台线程跑事件循环（:54-56）、Semaphore 限并发（默认 128，:473）。

## ③ 外部连接

- **生成端**：统一 `python -m cosmos_framework.scripts.inference`（外部包，本仓无源码），checkpoint 走 HF gated repo（需 `HF_TOKEN`）。
- **数据端**：paibench_c/paibench_g 用 `shi-labs/physical-ai-bench-*` HF 数据集（git clone+LFS），rbench 用 `DAGroup-PKU/RBench`，physics_iq 走 gcloud/gsutil。README 明说数据集只供控制图/条件帧，**prompt 全部仓内自带**。
- **评测端**：paibench_c 用 `trungtpham/pai-bench-c-cosmos3` fork（README "Changes" 表列 9 项上游 bug 修复：DOVER 重编码 -1.1 分偏置、si-RMSE ±10 截断、Canny 的 RGB/BGR 混用、SAM2 钉 1.1.0）；rbench 用 ReVidgen；unigenbench 自足。
- **判官端**：rbench 走 OpenAI 兼容端点（`OPENAI_BASE_URL`/`RBENCH_VLM_API_KEY`）；unigenbench 走 `--gateway_url/--gateway_api` 通用网关。
- **specs 同构**：`paibench_c/specs/{edge,blur,depth,seg}.json` 与 cookbooks transfer 线 `specs/` 同 schema，差异仅 seed（2025 vs 2026）与演示资产路径——评测线与教程线共享同一套 spec 约定。

## ④ 数据流

以 paibench_c 为例：`assets/tasks.json`（600 条，含 caption/各模态路径/negative_prompt）+ `specs/<modality>.json` → notebook 逐任务生成 121 帧 720p/30FPS 视频 → HF 数据集供 GT 与控制信号 → 打分调 `trungtpham/pai-bench-c-cosmos3`：GT 深度/分割**现场重算**（`--force_recompute_gt_seg --force_recompute_gt_depth`，丢弃数据集自带缓存以对齐内部 imaginaire4 管线），预测分割永远从原始 pred 字节解码（杜绝有损重编码）→ Canny F1/SSIM/si-RMSE/mIoU/DOVER 五类指标。paibench_g 的 motion smoothness 单独由分片脚本跑完再汇入聚合。rbench 双判官（GPT/本地 Qwen2.5-VL-72B）产物分目录 `gpt`/`qwen_local`，换判官不触发重新生成。

## ⑤ 设计决策

1. **生成与评测彻底解耦**：评测器全部独立 venv（.venv-scorer/.venv-rbench-scorer/.venv-rbench-ops），setup 专门防御两环境同路径（:86-95）。根源是评测器依赖（vLLM/Q-Align/Detectron2/SAM2）比生成栈更脆。
2. **用 patch 而非 fork-pin 传递上游修复**：三个 patch 全幂等，上下文漂移时 fail loud——把"上游演进致补丁失效"从隐性风险变显式报错。
3. **参考分数公开+偏差声明**：每套 README 给参考分表，paibench_c 明说与论文分数可能略有出入（论文用内部管线）——诚实标注复现边界。
4. **断点友好**：motion smoothness 每视频原子写盘；ugb_scorer 重试队列+结果存在即跳过（:352-356）。600×4 模态长评测中断续跑是刚需。
5. **判官可替换**：rbench 双通道 + unigenbench 任意 OpenAI 兼容网关，把判官从基础设施降级为配置项。

## ⑥ 新人提示（坑与勘误）

1. **unigenbench 是"隐形基准"**：无 README，用法只能读 notebook 和 `ugb_scorer.py --help`（:464-476）；文件头是 NVIDIA 专有保密声明（:1-13），与其余四套 OpenMDW-1.1/Apache 不同——引用代码注意许可差异。
2. **physics_iq 的 V2V 帧数是"补 1"约定**：官方 72 帧条件素材 pad 到 73 帧（3D VAE 对齐），生成 193 帧、只打 73..192 段——裁错段会把条件帧当生成分拉低分数。
3. **paibench_c 参考分是"修复后"口径**：9 项 bug 修复使本仓数字与 physical-ai-bench 主干不可直接对比；README 承诺 PR #8 合入后切回主干，跑分前先确认脚本 clone 的哪个源。
4. **seed 语义别混**：paibench_c spec seed=2025 且 README 注明 fps/aspect_ratio/seed 会被 tasks.json 逐任务覆写；paibench_g/rbench seed=0 固定。
5. **硬件门槛是硬约束**：paibench_g/rbench 默认 8 GPU、paibench_c/physics_iq 默认 4 GPU（`COSMOS3_NUM_GPUS` 可调），189 帧 720p 生成在小节点会 OOM。
6. **`gpt-5-2025-08-07` 是默认判官名**：rbench 不设 `OPENAI_MODEL` 时用它；自建端点若不认这个 ID 会在评测段（而非生成段）才失败，别浪费一整轮生成。
