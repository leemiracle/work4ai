# DALI_deps（讲透知识库）

NVIDIA/DALI_deps：DALI（GPU 数据加载与图像处理库）**裸机构建所需的全部第三方 C/C++ 依赖的构建脚本 + 源码快照聚合仓**——本仓没有任何 DALI 源码，只有 23 个构建脚本、11 个补丁、21 个 submodule 指针和三份根文档（README.rst / CLAUDE.md / .gitmodules）。

源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/DALI_deps`

## 全链状态表

| 产物 | 状态 | 说明 |
|---|---|---|
| deepwiki | ❌ 不适用 | 纯构建脚本仓，无 wiki 收录 |
| understand 图谱 | ✅ | 39 节点 / 66 边 / 3 层 / 4 步 tour · validator 0 issues · fingerprints 38 文件 @ 08d35594 · 图谱在仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ | `onboarding/ONBOARDING.md`（微仓合并口径，与本 README 合计 3000 字级 / 锚 20+，全部源码核实） |
| explain | — | 微仓不单设 explain（并入 onboarding） |
| README（本文件） | ✅ | 状态表 + 勘误清单 |

## 勘误与甄别清单（源码级实证，钉版）

1. **NOTES-DIGEST 修正：.gitmodules 的 21 个 submodule 全部指向上游 GitHub URL**（libsndfile→github.com/libsndfile/libsndfile、FFmpeg→github.com/FFmpeg/FFmpeg 等）；「指向 NVIDIA redist tar 包」的说法实为 **README.rst:20/31 表格里附列的备选 Source Snapshot 直链**（developer.download.nvidia.com/compute/redist/nvidia-dali/），不是 submodule 的 url。
2. **README 只点名部分补丁**：表格里只有 flac 标 "with cross-compilation patch"（README.rst:26，该补丁在 flac submodule 快照内）与 libtar 标 "+ patches"（README.rst:43）；**补丁大头 libsndfile 7 连 CVE 补丁（build_libsndfile.sh:21-27）与 zlib CVE-2026-85091 补丁（build_zlib.sh:21）在 README 只字未提**——补丁全貌只能从 build_scripts 读出（合计 11 个 .patch：libsnd ×7、libtar ×2、lmdb、zlib）。
3. **abseil 不是 submodule**：由 build_protobuf.sh 以 `-Dprotobuf_FORCE_FETCH_DEPENDENCIES=ON` 顺带 fetch+install（build_protobuf.sh:32），gRPC 再以 `gRPC_ABSL_PROVIDER=package` 复用这唯一副本（build_grpc.sh:100）——全仓「唯一副本」策略的支点。
4. **c-ares 已升格顶层依赖**（commit 08d3559 "make c-ares top level dep"）：独立 submodule + `gRPC_CARES_PROVIDER=module` + `CARES_ROOT_DIR` 指向 third_party/c-ares（build_grpc.sh:102-103），以便比 gRPC 上游更快地升版本（build_grpc.sh:24-25 注释自述）。
5. **third_party/ 21 个目录本地全空**（submodule 未初始化）；fingerprints 38 = 23 build_scripts + 11 patches + patches/libtar/README.rst + 3 根文件（libtar/LICENSE 被裁）。
6. 依赖顺序是构建正确性的一部分：zlib 最先（build_deps.sh:51）、libvorbis 必须在 libogg 后（build_deps.sh:59 注释）、grpc 在 protobuf/openssl/zlib 后（build_deps.sh:72）、google-cloud-cpp 收尾因为复用前面全部产物（build_deps.sh:73）。
7. FFmpeg 符号加 `DALI_` 前缀防与宿主 FFmpeg 冲突：sed 注入版本脚本生成命令（build_ffmpeg.sh:59-60）；WITH_FFMPEG=0 可整体跳过（build_ffmpeg.sh:19）。
8. 交叉编译安全层：validate_toolchain_env.sh 校验 CC/CXX 成对（:17-19）与变量字符白名单（:23，防注入——这些值会被插值进 CMake 代码）；generate_toolchain_file.sh 用 basename(gcc)+`-dumpmachine` 双重判交叉（:52-53），仅真交叉才写 CMAKE_SYSTEM_NAME（:57），恒追加 -fPIC（:67-68）。
9. 仓根有 CLAUDE.md——NVIDIA 同样以 agent 协作开发此仓（与 cuda-tile 仓先例一致），其中钉了「补丁由脚本 apply、勿手动」等规则。

## 产物索引

- `onboarding/ONBOARDING.md` —— 三层结构导览（构建脚本族 / 补丁族 / 仓根文档）+ 构建数据流 + 新人路线
