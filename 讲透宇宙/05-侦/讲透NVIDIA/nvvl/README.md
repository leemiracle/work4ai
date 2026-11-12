# 讲透 NVIDIA/nvvl（NVVL · NVIDIA Video Loader）

NVVL：GPU 硬件解码（NVDEC）+ 纹理单元后处理的视频帧加载库，面向深度学习训练；**已并入 DALI、停止维护**（README 首行宣告）。本目录是该仓的深度知识库产物集。

## 产物状态表

| 产物 | 状态 | 规模 | 说明 |
|---|---|---|---|
| deepwiki/ | ✅ 完成（2026-10-26） | 30/30 页 100%（TRUE_100 终判） | NVIDIA/nvvl DeepWiki 全量抓取，含 INDEX 与 _coverage-check |
| 知识图谱 | ✅ 完成（2026-11-10） | 2682 节点 / 4116 边 / 14 层 / 16 步 tour / validator 0 issues | 仓内 `.understand-anything/knowledge-graph.json`；fingerprints 1301 文件 @ a94c7493 |
| onboarding/ONBOARDING.md | ✅ 完成 | 11,884 字符（不计空格）· 8 节 · 73 行号锚 | 全链路导览，锚全部源码核实 |
| explain/ 5 篇 | ✅ 完成 | 01 C API 与 pImpl（3,083 字符/22 锚）/ 02 NvDecoder nvcuvid 链（3,131/15）/ 03 Queue 与 imgproc kernel（3,092/18）/ 04 Python 双世代绑定（3,004/15）/ 05 vendored Boost 与构建（3,125/13） | 六节结构，行号锚逐篇核实；字符数不计空格 |
| NOTES-DIGEST | ✅ 完成 | 25 条批阶段甄别笔记 | 仓内 `.understand-anything/NOTES-DIGEST.md` |

## 快速上手

- 新人路径：`onboarding/ONBOARDING.md` 第 1-2 节 → 按第 8 节阅读路线进源码 → 卡在哪个子系统就翻对应 explain 篇。
- explain 索引：01 契约层（include/ 两头 + variant 容器）/ 02 解码状态机（NvDecoder + nvcuvid 三回调）/ 03 异步基建（Queue 中断路径 + BT.601 kernel）/ 04 绑定换代（cffi→pybind11）/ 05 构建与 Boost（FFmpeg 探测宏 + 桩库）。

## 勘误与钉版（DeepWiki/直觉 vs 源码实证）

1. **"NVVL 是 NVIDIA 支持的产品"——错**。根 `README.md:1-5` 首行即宣告并入 DALI、停止维护，`:20-24` 自述"example code from a research project…not a supported NVIDIA product"。所有 issue 应去 DALI 仓。
2. **"库对外暴露 12 个 C 函数"——不完整**。是两个头各 12 个：`VideoLoader.h:64-122` 12 个（create/destroy/size/frame_count/read_sequence/receive_frames×2/get_stats/reset_stats/set_log_level），`PictureSequence.h:250-331` 另 12 个（sequence 生命周期 + layer/meta 存取 + wait），合计 24 个 `nvvl_*`。
3. **"vendored Boost 五域 41 批"——批次口径勘误**。实测 63 个分析批中 **49 个为纯 Boost 批**（另 3 批混有 Boost 文件），Boost 文件 1201/1301=92%；mpl 759 件占全仓 58.3%（非 57%）。图谱 14 层中 L11-L14 四层都是 Boost。
4. **scanner 对 C/C++ 近乎全盲，节点靠批阶段手扫补偿**。tree-sitter 对纯 C 声明头（`src/nvcuvid/cuviddec.h`、`nvcuvid.h` 的 `typedef struct` 声明）提取为零，对模板重度头（variant.hpp/mpl 759 件）同样零提取——2666 个 Boost/SDK 头节点全部由 worker 依据 #include 图与宏结构人工重建，锚定于批回执。
5. **图谱类型修正：Dockerfile 相关节点应为 `service:` 而非 `step:`**。`docker/Dockerfile.build` 与 `examples/pytorch_superres/docker/Dockerfile` 按 file-analyzer 规范归 service 类（构建服务设施），批阶段已修正；task 里"step→service 类型修正"即此。
6. **`libnvcuvid.so` 是 ELF 桩库制品，不是源码**。`examples/pytorch_superres/docker/libnvcuvid.so` 经 `file` 实证为 stripped ELF 64-bit shared object；由 `make-stub.sh:13-18` 用 `nm -D` 抽符号自动生成，所有函数体只返回 `CUDA_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND`（`:16`），仅供 nvidia-docker 构建期过链接。
7. **cffi 绑定不是手写声明，是 `gcc -E -DCFFI` 预处理产物**。`pytorch/Makefile:7` 把 C++ 头喂给 `gcc -E -P -DCFFI` 生成 `nvvl_generated.h`；`include/PictureSequence.h:3-10` 顶部的 CFFI 宏分支（前置声明 `CUstream_st` 顶掉 cuda_runtime.h）专为该管线存在。
8. **解码面常量不一致**：`frame_in_use_` 位图按 32 格建（`src/detail/NvDecoder.cpp:36`，注释称"32 is cuvid's max number of decode surfaces"），但 parser 实际以 20 面创建（`:117` 传入 + `src/detail/CUVideoDecoder.cpp:162`）；且 `src/detail/CUVideoParser.h:51` 在 HEVC 分支给 `ulMaxNumDecodeSurfaces` 赋的 20 会被 `:57` 统一赋值立即覆盖——死赋值。
9. **PyTorch 1.0 绑定仍是 THC 过渡态**：`pytorch1.0/src/nvvl_th.cpp:2,6,97-99` 仍 include `<THC/THC.h>` 借 `THCState_getCurrentStream` 拿流（THC 在 PyTorch 1.11+ 已删除）；cffi 世代的 `pytorch/nvvl/src/nvvl_th.c` 更只剩 8 行一个转发函数。现代移植第一刀是换 `c10::cuda::getCurrentCUDAStream`。
10. **一个 VideoLoader 只能吃同规格文件**：尺寸或 codec 不同的后续文件直接抛异常（`src/VideoLoader.cpp:253-264`），且仅支持 H.264/HEVC（`:276-282` + `src/detail/NvDecoder.cpp:102-115`）——DeepWiki 泛读时容易漏掉这个硬约束。

## 复验口径

- 全部行号锚 2026-11-10 对源码核实（git a94c7493ec9f309cc54acf81a66c62a068a06962）。
- 图谱校验：`.understand-anything/validate-report.json` issues=[] warnings=[]。
- 字数口径：不计空格字符。explain 各篇因行号锚密度落在 3,004-3,131（目标带上沿，Gymnasium 轮"锚密度所致"同款漂移）；ONBOARDING 11,884。
- 锚验证口径：全量 165 处 `path:line(-line)` 锚跑脚本对账（文件存在 + 行号界内），0 坏；另对 25 处关键锚做行内容语义抽验全中。
