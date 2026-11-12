# ContrastiveLosses4VRD（讲透知识库）

NVIDIA/ContrastiveLosses4VRD：CVPR2019 论文 *Graphical Contrastive Losses for Scene Graph Parsing*（arXiv 1903.02728）官方 PyTorch 实现 + Google AI Open Images 视觉关系检测挑战赛第一名方案改进版。Detectron 系（roytseng-tw/Detectron.pytorch 子模块）关系检测研究代码：ReLDN 谓词分类头上的 spo/so/p 三种图结构对比损失。

源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/ContrastiveLosses4VRD`

## 全链状态表

| 产物 | 状态 | 说明 |
|---|---|---|
| deepwiki | ✅（2026-10-26 另线完成） | 9 章全量（另一会话产物，与本线独立） |
| understand 图谱 | ✅ | 165 节点 / 352 边 / 4 层 / 5 步 tour · validator 0 issues · fingerprints 50 文件 @ f7539ca1 · 图谱在仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ | `onboarding/ONBOARDING.md`（7878 字符不计空格 / 8 节 / 83 个唯一行号锚，全部源码核实 0 坏） |
| explain | ✅ | `explain/` 3 篇（对比损失头 / 数据管道 / config 与测试引擎），每篇六节结构、23-36 锚、2382-2547 字符 |
| README（本文件） | ✅ | 状态表 + 勘误清单 |

## 勘误与甄别清单（源码级实证，钉版）

1. **Detectron_pytorch 是 gitmodule 子模块、未随仓分发**：`.gitmodules:1-3` 登记唯一子模块 roytseng-tw/Detectron.pytorch，本地目录为空；所有 `import utils.*` / `roi_data.*` / `modeling.*` / `import nn as mynn`（reldn_heads.py:14、minibatch_rel.py:37-46、boxes_rel.py:59 等）指向外部父仓，克隆须 `--recurse-submodules`（README.md:37）。
2. **不存在 `cfg.RELDN.CONTRASTIVE_VERSION`**（图谱摘要讹传）：config.py 全文无 RELDN 键；对比损失由三个独立布尔开关控制（`config.py:454-464`），`model_builder_rel.py:506-520` 顺序分发，且六个主配置 yaml 三开叠加（spo 1.0/so 0.5/p 0.1）而非三选一。
3. **spt 空间特征 28 维而非 20 维**（图谱摘要讹传）：`boxes_rel.py:65-72` 拼接 6+6+6+5+5，与 `reldn_heads.py:54` `nn.Linear(28, 64)` 互证。
4. **test_net_rel.py:91-92 命令行覆盖 bug**：`args.set_cfgs` 非空时误执行 `merge_cfg_from_file(args.cfg_file)`（应为 merge_cfg_from_list），测试路径 opts 覆盖实际不生效。
5. **task_evaluation_sg 名不副实**：vg/vrd 数据集走 vg_and_vrd 评测器（`test_engine_rel.py:150-153`），"sg" 评测器实际只服务 oi_rel；其 `task_evaluation_sg.py:52` 硬编码作者机器路径 `/home/jiz/projects/100_img_special_set.txt`。
6. **类别数硬编码入口**：train_net_step_rel.py / test_net_rel.py 各自按 --dataset 分支写死 vrd 101/70、vg 151/50、oi_rel 58/9（`train_net_step_rel.py:158-172`）——NUM_PRD_CLASSES 默认 -1 靠入口赋值。
7. **boxes_rel.py:62 赋值式 re-export**：`bbox_pair_overlaps = cython_bbox_rel.bbox_pair_overlaps` 是 Cython 编译扩展别名（scanner 盲区），源在 cython_bbox_rel.pyx:37-77；lib/make.sh 编译。
8. **docker/Dockerfile 仅 8 行无多阶段**，基于 pytorch 0.4-cuda9-cudnn7-devel，末行 `RUN conda install opencv` 无换行符——PyTorch 0.4 是硬运行时约束。
9. json_dataset_rel.py 786 行（非"787"），dataset_catalog_rel.py 140 行纯字典（ANN_FN3='predicate_file'，`dataset_catalog_rel.py:34-37`）。
10. VRD 数据集必须先跑 tools/convert_vrd_anno_to_coco_format.py + tools/rename_vrd_with_numbers.py 两步预处理，否则 JsonDatasetRel 构造即 assert 失败。

## 产物索引

- `onboarding/ONBOARDING.md` —— 8 节上手（定位/四层架构/模型链路/对比损失/数据管道/训练评测/配置与复现/勘误）
- `explain/01-对比损失头-reldn-heads与FrequencyBias.md` —— reldn_head 四支路 + 三损失 split_pos_neg_* + FrequencyBias 先验表
- `explain/02-数据管道-json-dataset到loader与ap评测.md` —— catalog → JsonDatasetRel → roidb → loader → 两套评测器与 ap_eval
- `explain/03-config与测试引擎.md` —— config.py MODEL 段 + 6 yaml 矩阵 + test_engine 多卡推理与评测分发
- `deepwiki/` —— 另线产物（9 章）
