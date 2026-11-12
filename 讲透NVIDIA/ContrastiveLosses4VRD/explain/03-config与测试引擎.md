# 03 · config 与测试引擎：三数据集配置矩阵 + test_engine_rel

## 角色定位

`lib/core/config.py`（1264 行）是 Detectron 风格的全局配置中枢——模块级可变 AttrDict `cfg` 声明全部默认超参，配 merge_cfg_from_file/merge_cfg_from_list 做 YAML 与命令行覆盖（cfg_from_file/cfg_from_list 是旧名别名，`config.py:1139/1170`）。`lib/core/test_engine_rel.py`（319 行）是推理/评测编排引擎。configs/ 6 个 yaml 是论文实验矩阵的固化。

## 内部结构

关系检测专属开关集中在 MODEL 段：RUN_BASELINE `config.py:425`、USE_FREQ_BIAS `config.py:431`、USE_OVLP_FILTER `config.py:433`、USE_SPATIAL_FEAT `config.py:435`、ADD_SCORES_ALL `config.py:441`、ADD_SO_SCORES `config.py:443`、三个对比损失开关+margin+weight `config.py:454-464`、USE_SPO_AGNOSTIC_COMPENSATION `config.py:468`、NUM_PRD_CLASSES `config.py:473`（默认 -1）。

配置矩阵（L03 层全量 6 件）：vrd 双胞胎（VGG16/16 epochs，COCO 与 IN 预训练仅权重不同）、vg 主设定（X-101-64x4d-FPN/8 epochs）+ 消融（VGG16 no_spt 变体，USE_SPATIAL_FEAT: False 在该 yaml 第 7 行）、oi_rel/oi_rel_mini（X-101-FPN/12 epochs 竞赛设定）。vrd 版三损失全开（margin 全 0.2，yaml L12-19），NUM_GPUS:8（L22）、NODE_SAMPLE_SIZE:128（L20）。

test_engine_rel 三层：run_inference（`test_engine_rel.py:79`）单进程逐图或多卡模式；多卡走 test_net_on_dataset（`test_engine_rel.py:126`）为每张 GPU 拉起 CUDA_VISIBLE_DEVICES 子进程（`test_engine_rel.py:185` process_in_parallel），各跑 test_net（`test_engine_rel.py:208`）在 image_range 分片推理并 pickle 落盘。评测分发 `test_engine_rel.py:150-153`：数据集名含 vg/vrd → vg_and_vrd 版，否则 → sg 版。单图推理：im_detect_rels（`test_rel.py:55`）→ im_get_det_rels（`test_rel.py:67`，主宾得分笛卡尔组合出 top-k 三元组）。

## 外部连接

config 被 32 个文件 import（全仓 fan-in 第一）；`tools/_init_paths.py:17` 的 add_path 把本仓 lib/ 与 Detectron_pytorch/lib/ 都插进 sys.path——这是本仓与父仓代码能互相 import 的前提。入口脚本**硬编码数据集类别数**（train 侧 `train_net_step_rel.py:158-172`：vrd 101/70、vg 151/50、oi_rel 58/9），NUM_PRD_CLASSES 默认 -1 靠入口赋值而非 yaml。测试结果供 vg_vis_rels.ipynb 可视化复用。

## 数据流

命令行 → parse_args → merge_cfg_from_file(yaml) → （训练侧再 merge_cfg_from_list）→ assert_and_infer_cfg → cfg 驱动模型组装与 roidb 构建。测试流：ckpt 加载（utils_rel/net_rel.py:62 load_ckpt_rel，strict=False）→ run_inference → all_results（list[dict]）→ eval_rel_results → recall@K / mAP。

## 设计决策

1. **配置即实验记录**：yaml 文件名编码全部关键设定（骨干/epochs/损失变体/margin/weight/预训练来源），README 只给文件名——代价是名字极长。
2. 类别数不入 yaml 而硬编码入口——Detectron"数据集档位"惯例，但新增数据集要改代码。
3. 多卡测试用子进程而非 DataParallel：每 GPU 独立 CUDA context，结果以 pickle 文件为界。
4. test_net_rel 支持复用已落盘检测结果直接重评测。

## 新人提示

查参数先读 `config.py:425-473` 的 MODEL 段再 grep 全文。两个坑：其一，**`test_net_rel.py:91-92` 有 bug**——`args.set_cfgs` 非空时误执行 `merge_cfg_from_file(args.cfg_file)`（应为 merge_cfg_from_list），测试路径命令行覆盖实际不生效，改配置请直接改 yaml；其二，测试入口同样硬编码类别数（oi_rel 58/9 等，`test_net_rel.py:94-105`），--dataset 拼错不会报错而是静默用错类别数。复现路线：configs/vrd 的 COCO_pretrained 版 + train_net_step_rel.py --dataset vrd。
