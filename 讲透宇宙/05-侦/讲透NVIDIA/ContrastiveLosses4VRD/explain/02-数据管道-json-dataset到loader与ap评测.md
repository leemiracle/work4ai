# 02 · 数据管道：json_dataset → roidb → loader → ap_eval

## 角色定位

数据管道横跨 `lib/datasets_rel` 与 `lib/roi_data_rel` 两包，把三个数据集（VRD/Visual Genome/OpenImages）的原始 JSON 标注变成训练 minibatch 与评测指标。入口三件：注册表 `dataset_catalog_rel.py`（140 行）、加载器 `json_dataset_rel.py`（786 行）、训练组装 `roidb_rel.py`；出口：`loader_rel.py`/`minibatch_rel.py`/`fast_rcnn_rel.py` 产 blob，`task_evaluation_*` 与 `ap_eval_rel.py` 出 recall@K / mAP。

## 内部结构

注册表是纯字典：四键常量在 `dataset_catalog_rel.py:34-37`（ANN_FN3='predicate_file'）。`JsonDatasetRel`（`json_dataset_rel.py:60`）构造时用 COCO API 读对象标注（`json_dataset_rel.py:75`），再读关系标注与谓词表（`json_dataset_rel.py:84-92`，谓词类表不含背景）。`get_roidb`（`json_dataset_rel.py:128`）逐图生成 roidb 条目，_add_gt_annotations（`json_dataset_rel.py:252`）填充 sbj/obj/prd 五组真值关系字段，可缓存（`json_dataset_rel.py:113-124`）。外部提议合并两套：对象级 `add_proposals`（`json_dataset_rel.py:660`）与成对级 `add_rel_proposals`（`json_dataset_rel.py:521`）。

训练组装：`combined_roidb_for_training`（`roidb_rel.py:39`）拼多数据集、水平翻转翻倍（`roidb_rel.py:86`；框类字段单独翻转 `roidb_rel.py:118`）、加回归目标（`roidb_rel.py:78`）。加载层 `RoiDataLoader`（`loader_rel.py:20`）的 __getitem__ 接 (index, ratio) 做宽高比分组（`loader_rel.py:28`），配 MinibatchSampler（`loader_rel.py:163`）/BatchSampler（`loader_rel.py:198`）/collate_minibatch（`loader_rel.py:246`）——复刻父仓 loader。`get_minibatch`（`minibatch_rel.py:31`）先调父仓 add_rpn_blobs（`minibatch_rel.py:37-46`），再叠本仓 add_relpn_blobs（`minibatch_rel.py:48`）；主宾对采样核心 `_sample_pairs`（`fast_rcnn_rel.py:62`，`fast_rcnn_rel.py:64` 注释点明候选 pair 数平方增长）。

## 外部连接

上游接 VRD 预处理脚本（tools/convert_vrd_anno_to_coco_format.py、tools/rename_vrd_with_numbers.py）。几何工具全部来自 `lib/utils_rel/boxes_rel.py`：boxes_union/rois_union（`boxes_rel.py:91/100`）、get_spt_features 28 维空间特征（`boxes_rel.py:65-72`）、Cython 重导出 bbox_pair_overlaps（`boxes_rel.py:62`，源 cython_bbox_rel.pyx:37-77）。minibatch_rel/boxes_rel 的 `roi_data.*`/`utils.*` import 指向未随仓分发的 Detectron.pytorch。

## 数据流

标注 JSON → catalog 查路径 → get_roidb（缓存）→ combined_roidb_for_training → RoiDataLoader → get_minibatch（图像+rpn+relpn blob）→ Generalized_RCNN.forward。评测反向：模型输出 res 字典 → test_engine 落盘 pickle → eval_rel_results 逐图取 top-k（`task_evaluation_vg_and_vrd.py:70-76` 优先用 prd_scores_ttl）→ prepare_mAP_dets（`ap_eval_rel.py:40`）分桶 → ap_eval（`ap_eval_rel.py:122`）出 AP。

## 设计决策

1. roidb 是训练/评测唯一中间表示——真值三元组挂在条目字段，评测端不回读原 JSON。
2. 两套评测器按数据集名分发（test_engine_rel.py:150-153）：vg/vrd 走 vg_and_vrd 版（prd_k_set vg 到 20、vrd 到 70，`task_evaluation_vg_and_vrd.py:33-36`；reldet/phrdet 双模式 `task_evaluation_vg_and_vrd.py:40-43`），oi_rel 走 sg 版（`task_evaluation_sg.py:27`，oi 分支 eval_ap=True）——"sg" 名字只对 oi 成立。
3. 宽高比分组采样保住 Detectron 效率惯例，代价是 collate 处理可变尺寸 pad；翻转增广须同步翻转 sbj/obj 语义字段。

## 新人提示

先读 `dataset_catalog_rel.py`（140 行纯字典）建三数据集地图，再跟一条 vrd_train 条目走 get_roidb → _add_gt_annotations；训练侧从 `roidb_rel.py:39` 进。坑：VRD 标注必须先过两个预处理脚本，否则 JsonDatasetRel 构造即在 `json_dataset_rel.py:66-71` assert 报错；`task_evaluation_sg.py:52` 硬编码作者机器路径，勿开 do_special。
