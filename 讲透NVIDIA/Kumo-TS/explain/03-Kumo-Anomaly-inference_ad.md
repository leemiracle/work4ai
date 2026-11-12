# 03 · Kumo-Anomaly/sdk/inference_ad.py — 异常检测推理主入口

## 角色定位

inference_ad.py 是异常线的 SDK 推理主入口（1478 行）：把 DataFrame 变成异常分数。它实现"Tesseract2"推理管线——PCA/填充特征定维、三种窗口 Dataset、扩散重构与残差合并，提供单进程与共享内存多 GPU 两个入口。文件头 docstring 自带用法速查（含调用形态与结果字典键位，inference_ad.py:29）。

## 内部结构

头部：设备自动检测 cuda→mps→cpu（inference_ad.py:94）；HF 默认仓 nvidia/Kumo-Anomaly 与默认权重 final_model.pth+curriculum_medium.yaml（inference_ad.py:102）；多卡 worker 脚本路径常量（inference_ad.py:107）。特征段：pca_features/pad_features/match_target_dim 把任意列数定维到 target_dim（inference_ad.py:163-192），_build_score_feature_mask 区分调用方与变换特征空间的打分掩码（inference_ad.py:217）。数据段：InferenceData 等三种 Dataset（inference_ad.py:245 起）。推理段：evaluate_ad_tesseract2（inference_ad.py:852）七步流水——扩散采样、样本中位数（inference_ad.py:899）、展平、clip、NaN 清洗、残差计算（inference_ad.py:936）、可选画像；入口单进程 inference_ad_tesseract2（inference_ad.py:1134，use_dpm_solver 默认 True）与多进程 _mp（inference_ad.py:1222）。尾部 NVTesseractADDiffusion 是 HF 包装类（inference_ad.py:1409）。

## 外部连接

上游编排：anomaly_analysis.py 的 perform_anomaly_analysis_with_diffusion 直接调 _mp 入口并消费 residual/target/valid_feature_mask（anomaly_analysis.py:184）。模型侧：from models.main_model import TSDiffuser_Generic（inference_ad.py:89）构造模型（inference_ad.py:1187，target_dim 缺省 40 见 inference_ad.py:1185）；评测经 models/utils.py 按 use_dpm_solver 分流标准/DPM 采样。多卡形态由父进程 subprocess 逐卡拉起 inference_worker.py（CUDA_VISIBLE_DEVICES 预设+共享内存窗口分发）。文档串保留手写 sys.path.append('/path/to/Kumo-Anomaly') 占位示例（inference_ad.py:12），真实注册在 inference_ad.py:88。

## 数据流

单进程：df →（编排层已数值化）get_dataloader 构互补掩码双 loader → evaluate_ad_tesseract2 → evaluate 内部对两 loader 各按自身 target mask 重构 → 样本拼合取 nsample 中位数为重构（inference_ad.py:899）→ 与 target 展平对齐 → 仅在 valid_feature_mask 有效维上算逐行 MAE/L2 残差（inference_ad.py:936）→ 返回七键结果字典（inference_ad.py:961）。多进程：device_count≤1 退回单进程（inference_ad.py:1270）；否则父进程预处理定维、窗口张量写共享内存、按 GPU 数分片派发 worker、_merge_chunked_results 合并并保留父掩码。

## 设计决策

一为互补掩码双 loader：两个 loader 的 target mask 互补，各自重构自己负责的段，合并即全覆盖——test_inference_mask_merge.py 锁定"每个 target mask 只取自己策略的重构"语义。二为 padding 不进分数：SDK 补零维通过 valid_feature_mask 剔除（v1.0.0 修复项，CHANGELOG 记载），MAE/L2/阈值只算真实特征。三为多 GPU 选 subprocess+共享内存而非 DataParallel：每卡独立加载完整模型、窗口级分片、共享内存免序列化拷贝；worker 生命周期（评估期间保持打开、失败也关闭）有专门测试。四为 DPM-Solver 默认开：单进程签名 use_dpm_solver=True（inference_ad.py:1140），速度优先质量损失可忽略。五为画像开关 TESSERACT_PROFILE_RESIDUALS 环境变量（inference_ad.py:113），残差各步耗时可选输出。

## 新人提示

从 docstring（inference_ad.py:4）与 evaluate_ad_tesseract2 的七步注释入手最快。target_dim 来自 checkpoint 内嵌 config 而非调用方（inference_ad.py:1180），列数不足会直接报错——编排层最小行数校验在 anomaly_analysis.py:176。复现结果先 set_seed（inference_ad.py:119）。改窗口/掩码逻辑先跑 sdk/tests 四件套：掩码合并、padding 掩码、尺度契约、worker 生命周期都在里面锁定。
