# 10 · cts 采集管线与 egopost 后处理：从表演者双手到训练资产

## 一、角色定位

这两个目录是 IsaacCapture 的"手部数据基础设施"双子星。`src/python/isaaccapture/cts/` 是 **Conformance Test Suite**——"The Conformance Test Suite (CTS) produces the evidence that the integration works"（`docs/source/conformance/overview.rst:9`）：设备厂商录一条脚本化 take，checker 只读录音就出判决，连同录音打包提交 PR，结构是 capture→checker→oracle 三件套。`src/python/isaaccapture_egopost/` 真名 **EgoHand**（v1，2026-10-21 发布，arXiv 2610.30293）：单目 3D 手部重建，1400 万图训练、约 9ms 推理，"enabling scalable annotation for dexterous robot policy learning"（`README.md:50`）——大规模自动标注的生产端。职责互补：cts 管少而精的质检判决，egopost 管多而快的资产生产。许可证显式分界：主仓 Apache-2.0，egopost 子树 LicenseRef-OpenMDW-1.1（`REUSE.toml:64`，precedence closest），packaging 测试专测这条策略（见 09 篇）。

## 二、内部结构

**cts 无 pyproject 无 CMake**——README+setup_env.sh+uv venv 脚本自组织。三层：`common/src/cts_common` 通用库，`checks/base.py:43` 的 `Check` 抽象是质检文法：增量累积 `update(frame)/result()`，类级字段 severity（`:53`）、attribution（`:55`）、depends_on（依赖失败则无答而非 pass，`:68`）、judged（False=纯测量）——四维正交拆开"多严重/怪谁/算不算数"；通用 checks 九种（rate/quaternion/continuity 等），frames.py 以 Protocol 定解码帧接口。`hand/capture` 采集端：record.sh 经主仓 TeleopSession 录 MCAP；session.py:15 十一步脚本（平放→握拳→四指捏→合掌→指尖触→两次翻掌→再平放，hold 3-6 秒）；steps.py:21 Phase 状态机 IDLE→CUEING→WAITING→HOLDING→CLOSING→DONE 驱动"念 cue→3-2-1→beep 开窗"，Window 为 `[start_ns,end_ns)` 半开区间（`steps.py:38`）；产物四件套 mcap/labels.json/溯源 json/log（`hand/capture/README.md:17-19`）。`hand/checker/src/hand_cts` 只 import mcap+flatbuffers，**零 isaaccapture 依赖**（`checker/README.md:26`）；钉 flatc v24.3.25 且校验生成 .bfbs 与 golden 字节一致（`:37-38`）；checks 四组 signal/shape/placement/windows（`:132-135`），窗口只测 held 窗后 60%（SETTLE_FRACTION=0.40，`labels.py:28`）。`hand/oracle` 裸脚本群：hand_model.py 26 关节右手（`:18`）、FK+拇指 IK、"independent of the checker"（`:4`）、左手镜像（`:7`）；generate_fixtures 造已知缺陷录音，`fixtures_index.json` 提交而录音不提交（`oracle/README.md:23`），生成 byte-deterministic，改生成器必改索引（`:25`）。

**egopost 独立 venv（Python 3.12+torch+DINOv3 --no-deps）。** 三块：`egohand/models` 模型本体（DINOv3 backbone、pose_transformer、rletr_occ/soma_hand_v2 双头）；`inference` 管线——camera 五件、hand_detector_2d（RT-DETRv2 ONNX+平滑+tracking）、pipeline（`EgoHandPredictor` `:97`，"writes soma.io-compatible prediction files" `predictor.py:9`）、preprocessing（crop.py:15 IMG_SIZE=256、warpAffine 裁剪 `:18`）、postprocessing（自适应平滑/世界坐标投影）、perf；`keypoint_2_soma_converter/src/soma_sequence_fit` 拟合器："Alternating native shape fitting and per-frame articulation optimization"（`fitting.py:4`），FitState 含 beta 体型/latent/root（`:32`），landmark/reprojection/silhouette 多损失。

## 三、外部连接

cts capture 向上借主仓 TeleopSession 录音、CloudXR（OpenXR session 必须在线，即使关节来自手套）、plugins（manus/wuji_glove）。checker 只碰 schema 文本与 golden bfbs；oracle 与 checker 互为对偶——fixtures_index 的 `expected_failing_check` 必须等于 Check.name。egopost 外部依赖全在 HuggingFace（EgoHand-v1/RT-DETR 检测器/SOMA-X 资产），微调走外部 GEM-X 仓。**两者零代码交叉引用**（双向 grep 实证，"cts" 命中皆 affected 子串）——闭环在语义层：同一套 OpenXR 26/21 关节约定，cts 证设备产出合格，egopost 把同构视频变训练资产。

## 四、数据流

**cts 判决流**：表演者听 cue 摆姿势→beep 开窗→MCAP 记 `core.HandPoseRecord` 双手+双控→checker 逐帧 Check.update→按 attribution 聚合：DEVICE 归因 FAIL→`fail`（exit 1）、PERFORMANCE FAIL→`retake`（exit 2）、必要检查无答→`insufficient_data`（exit 3）——"a performer who did not press the palms together has not shown that the glove is broken"。**oracle 镜像流**：FK 合成→缺陷变换→写录音→回读确认缺陷→索引锁定"此缺陷必触发彼检查"。**egopost 推理流**：mp4+标定 JSON→（可选）RT-DETR 检测手框，可拆两遍式——独立入口先出 `{left,right}_bbox.json` 供人工审阅、`SavedBBoxDetector` 回放（`run_hand_detector.py:6`、`:9`）→perspective crop 映射虚拟针孔 256²（`predictor.py:13`）→DINOv3 前向出弱透视相机 [s,tx,ty]→`compute_transl_full_cam` 升全透视平移（`cam_utils.py:78`）→左手镜像进出翻回右手轴（`predictor.py:45`）→自适应平滑→世界坐标投影→SOMA NPZ。PerfStage 十一段计时自带守恒（`collector.py:20`）。k2soma 补最后一环：2D 关键点→交替拟合→SOMA 序列资产。

## 五、设计决策

- **fail/retake 分离**是 cts 灵魂：归因比结论重要，exit 0-4 五级把"设备坏/演砸/数据不够/用错"分开。
- **oracle 独立于 checker**+byte-deterministic+committed index：测试测试器，防两侧共享代码同源盲区，生成器改动必在索引显形。
- **脚本即规范**：十一步不可编辑（`hand/README.md:377`），checker 按步名查测量；两侧脚本一致性由 `assert tuple(...) == SCRIPT`（`session.py:48`）import 期炸响。
- **checker 零 isaaccapture import**：判决不被被测系统污染，且能在 macOS 跑（采集必须 Linux）。
- **tolerances provisional and deliberately loose**：pass 只承诺"无反对证据"，不承诺质量好。
- **右手单模型+镜像**跨子系统一致：egopost 左手镜像进出（`predictor.py:45`），oracle 同款"右手构建、左手镜像"（`hand_model.py:7`）。
- **两遍式检测留人审闸门**：bbox 先审后推理；`EgoHandInferencePipeline` 构造注入 stub 可测（`pipeline.py:40`）。

## 六、新人提示

跑 cts 全链要 Linux+头显+CloudXR，`hand/README.md` 是唯一权威向导；checker 在 macOS 也能跑。oracle 单测在 fixtures 未生成前自动 skip（`HAND_FIXTURES` 可指他处）。labels 按录音同目录同名 `.labels.json` 寻址——symlink 或拷走录音会让窗口检查静默无答，报告里 `no motion-step labels` 是信号。读 egopost：README pipeline 图→predictor.py docstring（整条流浓缩）→crop.py→postprocessing/。判读报告记四标记：`meas` 是测量不是批准、`n/a` 永不变 pass。改 tolerances 前先读 hand README 顶部 Preview 警告——尚未对手套录音校准。

## 源码实证勘误

任务书五处修正：① **CTS 全称 Conformance Test Suite**（`overview.rst:9`）非 "Capture Tracking Sessions"；② 文件数——cts 实为 111 全文件（.py 72）非 108，egopost 116（.py 84）非 109；③ "cts→egopost 数据闭环"**无代码级连接**——双向 grep 零交叉 import，闭环只在语义层（见三节）；④ 线索漏了 oracle 核心机制（fixtures_index committed 金标准工厂）与五级 exit 判决表；⑤ egopost 产品名是 EgoHand（README 标题实证）；checks 实分两层（cts_common 九种+hand_cts 四组），线索只暗示一层。

---
chars(不含空格)=4722 anchors=23 勘误=5
