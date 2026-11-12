# 讲透 GR00T-Dreams（NVIDIA/GR00T-Dreams）

NVIDIA Isaac GR00T-Dreams blueprint：用 Cosmos 世界基础模型从**单张图片+语言指令**生成海量合成机器人轨迹（DreamGen 论文 [arXiv 2505.12705](https://arxiv.org/abs/2505.12705) 开源实现）。五段式管线：微调世界模型 → 生成合成视频 → IDM 提取动作（LeRobot 格式）→ GR00T N1 微调 → DreamGenBench 评测。本地仓 `/usr-data/data2/repos/agent-repos/NVIDIA/GR00T-Dreams` @ec3881d4（125 文件，17k 行 Python）。

## 全链状态表（2026-11-07 收官）

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki（L0 轮） | ✅ | `deepwiki/`（INDEX+页面+coverage） |
| 批分析 17 批 | ✅ | 17 逻辑批（b17 拆 2 part），349 节点/787 边，imports 1:1 对账+ast 补扫（ipynb 27 条 scanner 全盲由 worker 补齐） |
| merge | ✅ | 悬空边 1 条归因回补（batch-13 猜 `config:` 前缀 vs batch-12 实建 `schema:` 节点，前缀错位非真缺失） |
| layers/tour | ✅ | **12 层**（125 文件全覆盖零重复）/ **15 步** tour（64 节点引用） |
| finalize | ✅ | validator **0 issues 0 warnings**；图谱在仓内 `.understand-anything/knowledge-graph.json`（349n/787e） |
| fingerprints | ✅ | 125 files @ec3881d4（增量更新基线） |
| onboarding | ✅ | `onboarding/ONBOARDING.md`——8000 不计空格字符，8 节，35 锚（终验 0 坏） |
| explain | ✅ | `explain/` 6 篇 22,929 字符（3,492-4,197/篇），**153 行号锚全量终验 0 坏** |

## explain 索引（六节结构：角色定位/内部结构/外部连接/数据流/设计决策/新人提示）

1. `01-gr00t-n1-双系统架构.md`——System 2 Eagle2 VLM × System 1 流匹配动作头；multimodal_projector 投影；identity 空骨干留给动作头独立预训练
2. `02-数据层-lerobot-schema与transform.md`——LeRobotSingleDataset 加载/统计；state_action 606 行归一化与视角对齐；视频抽帧与多模态拼接
3. `03-idm-dump-动作提取管线.md`——convert_directory→split→preprocess→raw_to_lerobot→dump_idm_actions 全链；hydra 装配；fps 16/8 内部矛盾
4. `04-训练框架-runner与data-config.md`——9 具身配置类继承树；DualBrainTrainer 双系统联合优化；runner 孪生 diff 实测仅 11 行；peft/LoRA
5. `05-动作头-flow-matching与dit.md`——条件流匹配数学（线性 OT 路径+Beta(1.5,1) 偏噪声）落地三行锚；DiT 交叉注意力；SigLIP vendored 三注意力继承树
6. `06-评测-dreamgenbench与推理服务.md`——VLM 整段判成功率（IF）与物理对齐（PA）；RobotInferenceClient 多继承远程化；三 gym wrapper

## 甄别清单（源码级实证，与文档/直觉的差集）

1. **四个 `__init__.py` 非 barrel**：`gr00t/__init__.py` 等是纯 Apache 许可头零 re-export；`eagle_backbone.py:L26-28` 用 `os.path.dirname(gr00t.__file__)` 定位仓内 eagle2_hg_model 权重目录——被 import 仅作路径锚点
2. **复制粘贴双胞胎**：`data_config.py` 与 `data_config_idm.py` 各 788 行，唯一实质差异=链尾 `GR00TTransform`(Eagle)↔`GR00TIDMTransform`(SigLIP)；`runner.py`/`runner_idm.py` diff 实测仅 11 行（模型类型+collator+transforms）
3. **疑似 bug 三处**：`flow_matching_action_head_idm.py:349` `vis_sep_embedding` 从未在 `__init__` 定义（组1 进一步实证：token 图不生成 sep token，故是**死代码**而非运行时崩溃）；同文件 `get_action:457` 硬编码 `.cuda()`（CPU 下崩）；`raw_to_lerobot.py` fps 16/8 内部矛盾
4. **IDM 训练走 hydra 动态装配**：`idm_training.py` 从 `IDM_dump/base.yaml` 的 `_target_` 注入式构建（identity 骨干+flow matching 头）；IdentityBackbone 在 `backbone/identity.py`（直觉猜 backbone.py 是错的）
5. **dreamgenbench 四坑**：argparse `type=bool` 陷阱（`--zeroshot false` 仍解析为 True）；qwen 版 zeroshot **双重死代码**（`:144` 未传参）；gpt4o 版 `:28` `openai.api_key` 旧式死代码；两版 continue/分母口径不一致（视频路径不存在时 gpt4o 版会崩）
6. **Dockerfile 版本降级**：base 镜像 torch 2.6.0 被 L32 force-reinstall 降 2.5.1（transformer-engine 冲突）；opencv 卸载重锁 4.8.0.74
7. **pyproject 死配置**：`tool.setuptools.dynamic` 声明 version attr=`gr00t.version.VERSION` 但 `gr00t/version.py` 不存在（静态钉 0.1.0）
8. **sys.path hack**：`getting_started/examples/eval_gr00t_so100.py:36` 的 `from service import` 实际指向 `gr00t/eval/service.py`；同文档 `5_policy_deployment.md` 两处引用该脚本路径均不准
9. **上游特性勿混淆**：`draw_emoji` 本仓不存在（上游 Isaac-GR00T 特性）；eagle 配置复用 transformers 上游 `SiglipVisionConfig` 而非本仓 vendored 副本（vendored 四件套仅 IDM 线消费）
10. **外部资产**：IDM checkpoint 来自 HF `seonghyeonye/IDM_*`；eagle2 tokenizer 词表 vocab 49152+added 12=49164 与 `config.json` 精确对齐
11. **DiT 细节**（05 篇实证）：`BasicTransformerBlock` 无 attn2（diffusers 模板化石 `:117`）；`encoder_attention_mask` 全链未生效（`:302-307→:287→:171`）
12. **杂项**：`py.typed` PEP 561 空标记；issue 模板链接指向上游 NVIDIA/Isaac-GR00T；`groot` 拼写致 VideoColorJitter 过滤失效、`add_seperator_token` 幽灵配置（组1 新发现）；demo parquet 行数与 episodes.jsonl 精确对齐（ep0=416 行，pyarrow 实证 10 列 LeRobot 格式）

## 12 层速览

L1 仓库门面与工程治理 · L2 LeRobot 数据格式与演示数据集 · L3 数据变换管线 · L4 GR00T 模型核心与公共工具 · L5 动作头流匹配与 DiT · L6 SigLIP vendored · L7 Eagle2 VLM 骨干与 tokenizer · L8 训练实验框架 · L9 IDM 动作提取管线 · L10 具身形态配置资产 · L11 评测与推理服务 · L12 上手教程与示例

> 字数口径：不计空格总字符（钉版双口径之采信口径）。锚口径：`file.py:L12`/`file.py:12` 行号锚，界内即好；153 锚 0 坏。
