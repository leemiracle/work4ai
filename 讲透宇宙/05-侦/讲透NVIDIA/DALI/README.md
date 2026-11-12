# 讲透 NVIDIA DALI

NVIDIA DALI（Data Loading Library）全链知识库：deepwiki 抓取 + understand 图谱 + explain 精讲。

- 仓库：`NVIDIA/DALI` @ `5fdb0b6a`（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/DALI`）
- 图谱在仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 环节 | 状态 | 统计 |
|---|---|---|
| deepwiki | ✅ 2026-10-26 | 25/25 页 TRUE_100（全层级对账终判） |
| understand 图谱 | ✅ 2026-11-07 | **4002 节点 / 8966 边 / 16 层 / 16 步 tour**，validator 0 issues / 0 warnings，fingerprints 1954 文件 @ `5fdb0b6a` |
| onboarding | ✅ 2026-11-07 | `onboarding/ONBOARDING.md`（组 1 实例产出） |
| explain | ✅ 12/12 | 组 1=篇 01-06，组 2=篇 07-12；口径=不计空格字符，六节结构，行号锚全部源码核实（basename 唯一消歧） |

节点构成：file 1776 / class 1196 / function 838 / document 148 / config 24 / schema 16 / pipeline 4；16 层收纳 1968 个结构节点，其余为符号节点。

## 图谱 16 层

| 层 | 名称 | 节点 | 对应 explain |
|---|---|---|---|
| L01 | 工程配置与构建系统 | 90 | —（散见各篇） |
| L02 | 核心类型与设备原语 | 144 | 01 |
| L03 | 内存资源管理与 GDS 直存 | 51 | 02 |
| L04 | kernels 执行框架 | 75 | 04 |
| L05 | kernels 图像处理家族 | 128 | 04/05 |
| L06 | kernels 通用计算家族 | 164 | 05 |
| L07 | pipeline DAG 执行引擎 | 195 | 03 |
| L08 | 数据读取与文件后端 | 141 | 06 |
| L09 | 图像解码器族 | 66 | 07 |
| L10 | 图像处理算子族 | 175 | 08 |
| L11 | 数学与表达式引擎 | 132 | 09 |
| L12 | 通用几何随机与算子注册 | 180 | —（并入 08/09 叙述） |
| L13 | 视频序列音频信号算子 | 108 | 10 |
| L14 | Python 主包 nvidia.dali | 130 | 11 |
| L15 | AutoGraph vendored | 76 | 12 |
| L16 | 框架插件与 C API 接口 | 113 | 11/12 |

## explain 索引（字数=不计空格）

| # | 文件 | 主题 | 字数 |
|---|---|---|---|
| 01 | `explain/01-core类型层-TensorShape-TensorView与公共头.md` | TensorShape/TensorView/span 与公共头 | 3677 |
| 02 | `explain/02-mm内存资源与GDS直存.md` | pmr 内存资源、分配器与 GDS | 3989 |
| 03 | `explain/03-pipeline-DAG引擎与executor流着色.md` | DAG 构建/执行器/流着色 | 3766 |
| 04 | `explain/04-kernels执行框架-GPU-CPU双实现.md` | kernels 框架双后端 | 3613 |
| 05 | `explain/05-案例深读-resampling与clahe.md` | 重采样与 CLAHE 案例深读 | 4064 |
| 06 | `explain/06-reader与文件后端.md` | reader/loader/文件后端 | 3703 |
| 07 | `explain/07-解码器族.md` | imgcodec/缓存/inflate/旁路解码 | 3477 |
| 08 | `explain/08-图像处理算子.md` | 注册层、融合核、实验后端 | 3468 |
| 09 | `explain/09-数学表达式引擎.md` | arithmetic 表达式解析求值 | 3500 |
| 10 | `explain/10-视频序列音频信号.md` | 视频三代/光流/音频 DSP | 3442 |
| 11 | `explain/11-Python主包.md` | nvidia.dali 主包+框架插件 | 3460 |
| 12 | `explain/12-AutoGraph与c_api.md` | AutoGraph vendored+c_api 双代 | 3499 |

## 勘误清单（全部源码/台账核实）

1. **paste 内核是拷贝改造**：`dali/kernels/imgproc/paste/paste_gpu.h:15` 头注释自述 "THIS WHOLE CODE IS A COPY-PASTE OF multiply-add kernel"——paste GPU 核整块拷贝自 multiply-add 内核后改，非独立设计。
2. **dummy.cu 是链接期占位**：`dali/kernels/dummy.cu:13-18` 空文件，注释明示老 CMake 在 `CMAKE_CUDA_RESOLVE_DEVICE_SYMBOLS=ON` 时仍用 Clang 链接，此文件强制走 NVCC 做 device linking。
3. **四处 vendored 三方代码混三种许可**：`include/dali/util/half.hpp:3`（Christian Rau half，MIT）提供全部半精度；`dali/operators/sequence/optical_flow/optical_flow_impl/nvOpticalFlowCommon.h:2`（NVIDIA OpticalFlow SDK 头，BSD-3）；`dali/operators/video/dynlink_nvcuvid/cuviddec.h:4`（NVDEC SDK 头，MIT）；`third_party/cutlass`（`cmake/Dependencies.common.cmake:252-253` SYSTEM include 直引）。
4. **include/dali 解析根缺失，1750 条 #include 手扫修复**：scanner 只认仓内相对根，第二包含根 `include/dali/` 下 450 文件的 include 边全部悬空；批 41-55 逐文件手扫修复，`tmp/dali-inc-fixed-41..55.json` 累计 `fixed: 1750` 实证。
5. **旧产物批号错位，文件级重组复用 933 文件**：旧一代批产物与 rebatch 后 batches.json 批号完全错位（含已被 .understandignore 裁掉的 `dali/benchmark/` 53 文件），按 file frozenset 指纹重组进 salvage-pool，933 文件旧分析零重做复用（台账 PROGRESS.md:11）。
6. **双实例撞车"只增不重复"协议**：batch-36-part-3.json 两实例同写，后到者并入对方独有 2 类节点+5 边后删除分片，无 merge 双收（PROGRESS.md:10）。
7. **proto schema 节点实为 16 非 192**：交接清单"proto schema 节点 192 非 file 前缀"与图谱不符——实测 `schema:` 前缀 16 个（5 文件级+11 消息级：dali.proto 的 PipelineDef/OpDef/Checkpoint、feature.proto 的 Feature/Features/FeatureLists、caffe2.proto TensorProto 等），按图谱钉正。
8. **tree-sitter C 解析器四类盲区全靠人工补**：C++ template/constexpr 零提取（`arithmetic_meta.h` 类/函数全为手扫）；宏工厂整文件一条语句（`expression_factory_instances/*.cc` 全是单条 IMPLEMENT_OP_FACTORY_* 宏）；`static_switch.h` 宏展开生成 switch 结构不可见；`.inl` 单行模板（`dynlink_cufile.inl`）零提取。
9. **公开符号拼写遗留**：`dali/python/backend_impl.cc:1879` `ExposeTesorListGPU`（Tesor 少 s），:2148 调用点同拼——历史命名未修。
10. **134 个 CMakeLists 以 document: 节点入库**：scanner 把根 `CMakeLists.txt` 与全部构建脚本归类 docs/txt → fileCategory 映射为 document 节点（如 `document:dali_tf_plugin/CMakeLists.txt`），实为构建配置核心。
11. **测试头 scope-cut 诚实丢弃**：`.understandignore` 锚定根路径裁 `/dali/test/`、`/dali/benchmark/`、`/docs/`、`/qa/`（磁盘上 `dali/benchmark` 现为空目录），图谱缺失≠仓库缺失；锚定根路径写法避免裸目录模式误伤子树。
12. **pyi 存根族非实现**：`plugin/numba/*.pyi`、`plugin/pytorch/_torch_function.pyi`、`tensors.pyi` 等仅签名无实现，供类型检查器消费，读代码别当逻辑源。
13. **new_crop_mirror_normalize.cu 的 include 是 27 条非 22 条**：批阶段笔记记 22，实测 `grep -c "#include"` = 27；三融合核路径 :109/:174/:267 属实。
14. **NVDEC 三代归 L13 非 L09**：交接 blurb 把"NVDEC/CUVID/nvdecoder 三代"标在解码器族（L09/篇 07）名下，实际在视频层（L13/篇 10）；L09 是 imgcodec 图像解码+缓存+inflate+音频旁路。
15. **c_api 一代错误处理是选择性 catch 非统一翻译**：`dali/c_api/c_api.cc` 仅 :564 out_of_range、:782/:791 bad_alloc 三处选择性捕获；"异常统一转错误码"的全量翻译是 c_api_2（`error_handling.cc:34` thread_local 槽+:87 HandleError）才有的。
16. **解码缓存策略是二分非三种**：`image_cache_factory.cc:32/34` 只认 `threshold`→ImageCacheBlob、`largest`→ImageCacheLargest；类名 Blob 由策略名 threshold 激活，命名陷阱。
17. **inflate 只支持 LZ4 且仅 GPU**：`inflate_params.h:41` 算法枚举写死 LZ4，`inflate_gpu.cc:177` 仅注册 GPU 后端，"gzip/zlib CPU/GPU 双实现"不成立。
18. **NVIDIA 也在用 agent 协作开发此仓**：`skills/dali-dynamic-mode/SKILL.md` 是标准 Claude/agent skill 格式（frontmatter name/description/metadata，author "DALI Team"）。

## 口径说明

- 字数=不计空格总字符（含代码符号）；行号锚经验证器 basename 唯一消歧+行界检查（组 2 六篇 0 坏锚）。
- 组 1（01-06）字数 3613-4064 略超 3500 上限，系该实例自校口径；组 2（07-12）全部压在 2000-3500 区间。
