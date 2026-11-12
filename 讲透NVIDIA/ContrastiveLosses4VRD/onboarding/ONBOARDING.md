# ContrastiveLosses4VRD Onboarding（视觉关系检测对比损失 · Detectron 系研究代码）

> 图谱基线：165 节点 / 352 边 / 4 层 / 5 步导览 · fingerprints 50 文件 @ f7539ca1（"Update README.md"）
> 源码锚全部从仓内源码逐行核实（2026-11-07）；本仓 50 个文件、纯 Python+Cython+YAML，无 C++/CUDA 自有源码。

## 1. 项目定位：一句话与血统

这是 CVPR2019 论文 **Graphical Contrastive Losses for Scene Graph Parsing**（arXiv 1903.02728）的官方 PyTorch 实现，也是 **Google AI Open Images 视觉关系检测挑战赛第一名方案的改进版**（README.md:9）。核心贡献：在 ReLDN（Relation Detection Network）谓词分类头上一组**图结构对比损失（graphical contrastive losses）**——对同一主语（或宾语）节点下的正负谓词对做 margin ranking，把"这个节点真正成立的关系"与"同节点被错配的关系"在概率空间拉开。

血统上它是 **Detectron 系（Caffe2 Detectron → roytseng-tw/Detectron.pytorch）的关系检测扩展**：`.gitmodules:1-3` 登记唯一子模块 Detectron_pytorch 指向 roytseng-tw/Detectron.pytorch，本仓在其上加 `*_rel` 后缀的五个平行包（`lib/modeling_rel`、`lib/datasets_rel`、`lib/roi_data_rel`、`lib/utils_rel`、`lib/core`）。**本地克隆中 Detectron_pytorch/ 目录为空**（子模块未拉取），因此 `import utils.*`、`import roi_data.*`、`import modeling.*`、`import nn as mynn`（如 reldn_heads.py:14、minibatch_rel.py:37-46 的 `roi_data.rpn.add_rpn_blobs`、boxes_rel.py:59 的 `bbox_transform_inv`）全部指向未随仓分发的外部代码——克隆时必须 `--recurse-submodules`（README.md:37），图谱把这些依赖记为跨仓边。

## 2. 四层架构总览

图谱按依赖方向分四层：

| 层 | 内容 | 文件数 | 代表节点 |
|---|---|---|---|
| L01 模型与核心层 | modeling_rel 全部 + core 的 config/test/test_engine | 60 | config.py（fan-in 32 全仓第一）、Generalized_RCNN |
| L02 数据与工具层 | datasets_rel / roi_data_rel / utils_rel | 79 | JsonDatasetRel、RoiDataLoader、boxes_rel.py |
| L03 配置层 | vrd/vg/oi_rel(_mini) 三数据集 6 个 yaml | 6 | 文件名即完整实验设定 |
| L04 文档与资产层 | README/docker/两 PNG/notebook/tools 入口与 VRD 预处理 | 20 | train_net_step_rel.py、test_net_rel.py |

核心枢纽（图谱 fan-in 前列）：`lib/core/config.py`（被 32 个文件 import，`from core.config import cfg` 是全仓最常见行）、`lib/utils_rel/boxes_rel.py`（fan-in 7）、`lib/datasets_rel/json_dataset_rel.py`（fan-in 3）。

## 3. 模型链路：从像素到三元组

总装在 `lib/modeling_rel/model_builder_rel.py`（769 行）的 **Generalized_RCNN**（forward `model_builder_rel.py:262` / _forward `model_builder_rel.py:269`），按 cfg 组装：backbone（VGG16 或 X-101-64x4d-FPN，`modeling_rel/VGG16.py:29` 的 VGG16_conv_body 从 torchvision 预训练拆层）→ RPN/对象头（`fast_rcnn_heads.py:38` 的 fast_rcnn_outputs + `fast_rcnn_heads.py:54/69/83` 三种 ROI 特征头）→ **RelPyramid**（`rel_pyramid_module.py:23`，为 FPN 各层配 1×1 lateral 卷积 prd_conv_lateral，`rel_pyramid_module.py:30-38`）→ **RelPN**（`relpn_heads.py:26` single_scale_relpn_outputs：主宾对枚举、bbox_pair_overlaps 重叠过滤 `relpn_heads.py:73`、rois_union 联合框 `relpn_heads.py:94`、get_spt_features 空间特征 `relpn_heads.py:111`）→ **ReLDN**（`reldn_heads.py:22`）。`_add_loss`（`model_builder_rel.py:767`）汇总对象分支损失（fast_rcnn_heads.py 的 fast_rcnn_losses）+ 谓词交叉熵 + 对比损失。

注意模型组装走 Detectron 惯例的**字符串反射**：model_builder_rel.py 的 get_func 从 modeling/modeling_rel 命名空间按 cfg 取头构造器，对象分支直接依赖父仓 `modeling.rpn_heads` 等子模块。

## 4. 本仓灵魂：三种对比损失

仓名 ContrastiveLosses4VRD 的落点在 `lib/modeling_rel/reldn_heads.py`（345 行）：

- **spo 无差别** `reldn_contrastive_losses`（`reldn_heads.py:150`）：同一节点（一组相同主语框）内，取正例对概率最小值 vs 组外/组内负例最大值配对（split_pos_neg_spo_agnostic `reldn_heads.py:207`，min/max 在 `reldn_heads.py:223-224`），`F.margin_ranking_loss` 拉开（`reldn_heads.py:155`，margin=cfg.MODEL.NODE_CONTRASTIVE_MARGIN）。
- **so 感知** `reldn_so_contrastive_losses`（`reldn_heads.py:165`）：split_pos_neg_so_aware（`reldn_heads.py:233`）按 s_or_o='s'/'o'（`reldn_heads.py:256`）再按唯一宾语/主语标签分组（`reldn_heads.py:258/278`），负例只在同对象标签组内取 max，避免跨语义不公平比较；无负例组时 USE_SPO_AGNOSTIC_COMPENSATION（`reldn_heads.py:268`）回退 spo 配对。
- **p 感知** `reldn_p_contrastive_losses`（`reldn_heads.py:184`）：split_pos_neg_p_aware（`reldn_heads.py:302`）按**谓词标签**分组，且负例用模型自身检测标签 prd_labels_det（`reldn_heads.py:305`、`reldn_heads.py:322`）而非真值——训练/推理一致性设计。

三者由三个**独立布尔开关**控制（`config.py:454-464`，margin/weight 各自可调），`model_builder_rel.py:506-520` 顺序分发；**三开关可同时开启**——vrd/vg/oi_rel 六个主配置 yaml 全部三开（spo 权重默认 1.0、so 0.5、p 0.1，见 configs/vrd/...COCO_pretrained.yaml MODEL 段 L12-19）。配套的 **FrequencyBias**（`sparse_targets_rel.py:23`）把训练集 (主语,谓词,宾语) 共现统计转成对数先验 nn.Embedding（`sparse_targets_rel.py:54`），rel_index_with_labels（`sparse_targets_rel.py:59-64`）按主宾标签查表给谓词分布加频率偏置基线——数据来自 get_dataset_counts_rel.py 的 get_rel_counts。

## 5. 数据管道与三数据集

数据集注册表 `lib/datasets_rel/dataset_catalog_rel.py`（纯字典声明，键常量 IM_DIR/ANN_FN/ANN_FN2/ANN_FN3 在 `dataset_catalog_rel.py:34-37`，ANN_FN3='predicate_file'）登记 vrd/vg/oi_rel(_mini) 系列。加载核心 `json_dataset_rel.py` 的 **JsonDatasetRel**（`json_dataset_rel.py:60`）：__init__ 用 COCO API 读主标注（`json_dataset_rel.py:75`），再从 ANN_FN2 读关系标注、ANN_FN3 读谓词表（`json_dataset_rel.py:84-92`，谓词表显式不含背景类）；get_roidb（`json_dataset_rel.py:128`）产出带 `sbj_gt_boxes/sbj_gt_classes/obj_gt_*/prd_gt_classes` 的 roidb 条目（真值关系三元组在 _add_gt_annotations `json_dataset_rel.py:252` 填充），缓存键白名单 `json_dataset_rel.py:113-124`。外部提议有**两套合并管线**：对象级 add_proposals（`json_dataset_rel.py:660`）/成对级 add_rel_proposals（`json_dataset_rel.py:521`，_merge_paired_boxes_into_roidb `json_dataset_rel.py:557`）。

训练侧链路：roidb_rel.py 的 combined_roidb_for_training（`roidb_rel.py:39`）拼接多数据集+水平翻转增广（extend_with_flipped_entries `roidb_rel.py:86`，`roidb_rel.py:118` dont_copy 列表要单独翻转框字段）+ bbox 回归目标（`roidb_rel.py:78`）→ loader_rel.py 的 RoiDataLoader（`loader_rel.py:20`，__getitem__ 收 (index, ratio) 元组 `loader_rel.py:28` 做宽高比分组）+ MinibatchSampler（`loader_rel.py:163`）/BatchSampler（`loader_rel.py:198`）/collate_minibatch（`loader_rel.py:246`）→ minibatch_rel.py 的 get_minibatch（`minibatch_rel.py:31`：父仓 rpn blob + 本仓 add_relpn_blobs `minibatch_rel.py:48`）→ fast_rcnn_rel.py 的 add_rel_blobs（`fast_rcnn_rel.py:44`）/_sample_pairs（`fast_rcnn_rel.py:62`，正负主宾对采样核心，`fast_rcnn_rel.py:64` 注释点明 pair 数是平方级所以 FG_REL_FRACTION 配比特殊）。RelPN 的重叠过滤靠 Cython 扩展：`boxes_rel.py:62` `bbox_pair_overlaps = cython_bbox_rel.bbox_pair_overlaps` 赋值式 re-export，源在 cython_bbox_rel.pyx:37-77（lib/make.sh 编译，setup.py 注册）。

**VRD 数据集需先跑两步预处理**：tools/convert_vrd_anno_to_coco_format.py（convert_anno/box_transform）转 COCO 风格标注，tools/rename_vrd_with_numbers.py（process_vrd_split）把字符串类别名换成整数 id。

## 6. 训练与评测入口

- **训练** `tools/train_net_step_rel.py`：main（`train_net_step_rel.py:142`）按 --dataset 硬编码类别数（vrd 101/70、vg 151/50、oi_rel 58/9，`train_net_step_rel.py:158-172` 一带），`train_net_step_rel.py:196` `effective_batch_size = iter_size * batch_size` 以梯度累积模拟大 batch，`train_net_step_rel.py:213` 据此线性缩放 STEPS/MAX_ITER，`train_net_step_rel.py:447` 内层 iter_size 循环，save_ckpt `train_net_step_rel.py:122`。
- **测试** `tools/test_net_rel.py`：优先复用落盘检测结果直接评测；`lib/core/test_engine_rel.py` 的 run_inference（`test_engine_rel.py:79`）支持多卡模式——每 GPU 一个 CUDA_VISIBLE_DEVICES 子进程（`test_engine_rel.py:185` process_in_parallel）跑 test_net（`test_engine_rel.py:208`），结果 pickle 归并。
- **评测分发** `test_engine_rel.py:150-153`：数据集名含 `vg`/`vrd` → task_evaluation_vg_and_vrd.eval_rel_results（`task_evaluation_vg_and_vrd.py:31`，prd_k_set：vg 到 20、vrd 到 70；`task_evaluation_vg_and_vrd.py:40-43` reldet/phrdet 双模式）；否则（oi_rel）→ task_evaluation_sg.eval_rel_results（`task_evaluation_sg.py:27`，topk=100，oi 分支 eval_ap=True 走 mAP）。谓词级 AP 在 ap_eval_rel.py：prepare_mAP_dets（`ap_eval_rel.py:40`）按谓词分桶、ap_eval（`ap_eval_rel.py:122`）VOC 风格曲线积分。单图推理在 test_rel.py：im_detect_rels（`test_rel.py:55`）→ im_get_det_rels（`test_rel.py:67`，主宾得分笛卡尔组合出 top-k 三元组）。

## 7. 配置矩阵与复现环境

6 个 yaml 文件名即完整实验设定（L03 层全量）：vrd 两个（VGG16/16 epochs，COCO 与 ImageNet 预训练仅权重不同，消融预训练来源）、vg 两个（X-101-64x4d-FPN 8 epochs 主设定 + VGG16 no_spt 消融变体，USE_SPATIAL_FEAT: False 见该 yaml L7）、oi_rel/oi_rel_mini 各一（X-101-FPN 12 epochs 竞赛设定）。vrd 配置 NUM_GPUS:8、IMS_PER_BATCH:1、BATCH_SIZE_PER_IM:512、NODE_SAMPLE_SIZE:128。

环境：docker/Dockerfile 仅 8 行（无多阶段构建），基于 pytorch/pytorch:0.4-cuda9-cudnn7-devel（L1），末行 `RUN conda install opencv` 无换行符——**PyTorch 0.4 + CUDA9 是硬约束**。编译 Cython：`bash lib/make.sh`（设 CUDA_PATH 后 build_ext --inplace）。

## 8. 勘误与新人提示

1. **`cfg.RELDN.CONTRASTIVE_VERSION` 不存在**——config.py 无 RELDN 键；对比损失由三个独立布尔开关控制（`config.py:454-464`），分发在 `model_builder_rel.py:506-520`，且主配置三开叠加而非三选一。
2. **spt 空间特征是 28 维不是 20 维**：`boxes_rel.py:65-72` 拼接 6+6+6+5+5（pair_feature 6 维 ×3 + box_feature 5 维 ×2），与 `reldn_heads.py:54` `nn.Linear(28, 64)` 互证。
3. **`test_net_rel.py:91-92` 有 bug**：`args.set_cfgs` 非空时误写 `merge_cfg_from_file(args.cfg_file)`（应为 merge_cfg_from_list(args.set_cfgs)），测试路径命令行覆盖 opts 实际不生效。
4. task_evaluation_sg 名字有误导：vg 也走 vg_and_vrd 版（`test_engine_rel.py:150-153`），sg 评测器实际服务 oi_rel；其 `task_evaluation_sg.py:52` 还硬编码了作者机器路径 `/home/jiz/projects/100_img_special_set.txt`（仅 do_special=True 才触发）。
5. 新人路线：README.md 安装节 → docker 起 0.4 环境 → lib/make.sh 编 Cython → 读 `reldn_heads.py:150-344`（损失）→ `model_builder_rel.py:470-526`（分发）→ 挑 configs/vrd 一个 yaml 跑 train_net_step_rel.py。
