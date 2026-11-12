# 02 · networks/ 感知组件 — sam2infer.py 与 foundationstereo_onnx.py

## ① 角色定位

这两个文件是管线的**感知前置层**，回答"重建谁"与"离多远"。`sam2infer.py`（570 行）用 SAM2 视频分割把目标物体从每帧抠成二值掩码（BundleTrack/NeRF/点云清洗全吃它的产出）；`foundationstereo_onnx.py`（453 行）用 ONNX Runtime 跑 FoundationStereo 立体匹配，把左右目对变成米制深度图（管线唯一深度来源）。共同形态是**外部模型仓适配层**：SAM2 来自 segment-anything-2 包、FoundationStereo 来自导出 onnx，本仓只做装配、调用与落盘。CLI 四步的前两步就是它们。

## ② 内部结构

**sam2infer.py**（行号指该文件）分四块：
- **导入期 monkey patch 区**（:30-53,455-456）：`torch.load` 遇 weights_only=True 强改 False（:48-50，兼容旧 checkpoint）；`misc.load_video_frames` 整体替换成 PNG 目录版（:456）。**patch 在 import 时全局生效**。
- **帧加载器** `png_compatible_load_video_frames`（:84-182）：枚举 jpg/png → 字典序（:145）→ resize 1024² → /255 → ImageNet 归一（:178-180）。
- **掩码生产** `process_directory_masks`（:331-452，核心）：bbox 空时取首帧中央 80% 兜底（:376-388）；build_sam2_video_predictor → init_state → `add_new_points_or_box`（**bbox+中心正点击同时给**，:411-426）→ `propagate_in_video` 传播全帧（:429-436）→ 掩码 ×255 存 PNG（:444-449）。另有单图版（:248-328）。
- **门面与幂等**：`Sam2Infer`（:459-498）四键 config 薄包装；`run_mask_extraction`（:501-542）管线入口——**已存掩码数==RGB 帧数则跳过**（:526-530），异常吞成 False。

**foundationstereo_onnx.py**：
- `InputPadder`（:35-118）：把 H/W 补到 divis_by 整倍数（sintel 模式四边均分 :63-67），pad 用 edge 复制（:96），unpad 切回。**实际调用处 divis_by=32**（:301），不是类默认的 8。
- `preprocess_each_image_pair`（:122-139）：Resize + ToTensor + ImageNet 归一。
- `FoundationStereoProcessorOnnx`（:142-381）：构造建 InferenceSession（CUDA 优先，:188-193）、发现左图序列、内参按 scale 缩放（:230-238）；`infer`（:240-324）——**尺寸自适应带副作用**：低于 onnx_input_min/高于 onnx_input_max 时改写 self.config['scale'] 并重算内参（:281-288）；pad→ORT→unpad（:301-309）；`depth = fx·baseline/disp`（disp≤0 置 inf，:317-318）；`run`（:326-381）批量，右图=左图兄弟 right/ 目录按名替换（:358），深度存 .npy。
- `run_depth_estimation_onnx`（:384-453）：管线入口，OmegaConf 包装 config（:442），**已有深度数 ≥ RGB 数则跳过**（:427-435）。

## ③ 外部连接

sam2infer 依赖 `sam2.build_sam` 与 `sam2.utils.misc`（:27-28）；foundationstereo 依赖 onnxruntime（:25，模块级日志级别 3，:29）+ torchvision。上游：cli/main.py 第 1/2 步直接调两个 run_* 入口；networks/__init__.py 聚合导出。下游：掩码进 erode_mask/use_mask=1；深度 .npy 被 NVBundleSDF 读入深度处理链。

## ④ 数据流

SAM2 侧：left/*.png + bbox（yaml 或 BoundingBoxWidget 交互产出）→ masks/*.png（与帧同名）。深度侧：left+right →（scale 降采样 + 32 倍数 pad）→ ORT → 视差 → fx·baseline/d → depth/N.npy（float32，米制）。两者接口都是"目录级产物 + 数量对账幂等"，失败不抛顶层（run_* 返回 bool/None）。

## ⑤ 设计决策

1. **bbox 一次标注 + 视频传播**（:419-436）：SAM2 memory attention 让首帧提示传播全序列，用户只标一帧——"单物体扫描"交互模型的基础。
2. **monkey patch 而非 fork 上游**（:53,456）：checkpoint 格式与帧加载是版本耦合细节，三行 patch 换掉 fork 整库的维护成本。
3. **ONNX 而非 pth 推理**：0.2.0 商业化改版——ONNX 解耦 PyTorch 版本、可进 TensorRT 链；代价是 config 键与 schema 脱节（见⑥）。
4. **数量对账幂等**（:526-530,427-435）：重跑不重算已完成感知产物，服务长管线断点续跑。
5. **pad 用 edge 复制而非零**（:96）：立体 cost volume 对黑边敏感，边缘延拓降伪深度泄漏。

## ⑥ 新人提示

- **重磅：导入即进入 bfloat16 autocast 且不退出**——`torch.autocast("cuda", dtype=torch.bfloat16).__enter__()`（:70）在 import 时执行且无 `__exit__`。**import sam2infer 后全进程 CUDA 算术都落在 autocast 上下文**，影响后续任意同进程模型的数值路径；当前靠 cli 分步调用隔离。
- **schema 没有 ONNX 的键**：ProcessorOnnx 读 config['onnx_path']/['onnx_input_min']/['onnx_input_max']（:192,281,285），schema.py 的 FoundationStereoConfig（:26-38）只有 pth_path/cfg_path——这些键必须 yaml 显式给，漏键是运行期 KeyError 而非启动期。
- **CPU 配置形同虚设**：device='cpu' 时 provider 正确切 CPU（:188），但 :195-196 无条件 raise CUDA required——纯 CPU 跑不起来是设计如此。
- **死代码警示**：segment_image_with_bbox 里 preprocess_single_image 的产出从未喂给 predictor（:281-285 算完即弃，init_state 自己重读目录）——单图版是视频版的雏形复制品，别照它理解数据流。
- `infer` 尺寸自适应**有状态**：mutate config['scale']（:283,287）并重算内参，连续处理不同分辨率图时后续帧用的是上一帧改过的 scale。
- 右图靠 `left→right` 字符串替换（:358）：文件名含其它 "left" 字样会被误替换。
- 默认 checkpoint 参数 /sam2/checkpoints（:251-252）与部署路径（:547-554）不一致——永远显式传参。

---
*甄别：图谱 summary 与源码一致；"autocast 导入副作用/schema 缺 onnx 键/CPU 分支矛盾/单图版死代码"为本轮源码级实证发现，图谱未载。*
