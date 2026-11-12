# DALI_deps Onboarding（微仓合并口径）

> 图谱基线：39 节点 / 66 边 / 3 层 / 4 步 tour · fingerprints 38 文件 @ 08d35594（"Update openssl, patch zlib, patch libsound, make c-ares top level dep #185"）。本仓无 DALI 源码——它是「怎么把 21 个第三方库装到一个用户可写 prefix」的全部知识。

## 1. 定位与三层结构

DALI 主仓裸机构建需要约 21 个第三方 C/C++ 库；本仓以三种资产聚合它们：**21 个 submodule 源码快照**（.gitmodules 全部指向上游 GitHub，third_party/ 下 21 个目录）、**23 个构建脚本**（build_scripts/，合计 1353 行）、**11 个补丁**（patches/，libsndfile ×7 / libtar ×2 / lmdb / zlib）+ libtar 补丁来源说明（patches/libtar/README.rst，openEuler CC BY-SA 4.0）。图谱三层：L01 构建脚本层 24 文件 / L02 补丁层 12 / L03 仓根文档层 3。

## 2. 总编排：build_deps.sh

入口 `build_deps.sh` 导出公共环境（HOST_INSTALL_PREFIX/INSTALL_PREFIX 默认 /usr/local，build_deps.sh:19-20）、source validate_toolchain_env.sh 校验后，按 `PACKAGE_LIST`（build_deps.sh:50）固定顺序逐个调 build_<pkg>.sh：zlib 打头（:51）→ protobuf（:52）→ 音频链 ogg→vorbis（:58-59 显式注释 "Install after libogg"）→ libsndfile → 共享的 openssl/curl（:64-68，aws-sdk 与 google-cloud-cpp 两家共用）→ grpc（:72，需 protobuf/openssl/zlib 就位）→ **google-cloud-cpp 收尾**（:73，"uses everything above"）。CLEANUP=1 时先对所有 submodule `git clean -fdx`（:42-46）。`WITH_FFMPEG=0` 跳过 FFmpeg（build_ffmpeg.sh:19）。

## 3. 脚本族的四种套路

- **纯 CMake 系**（多数）：source generate_toolchain_file.sh（函数定义在 :32）生成 toolchain.cmake 再 cmake。该函数以 `basename "$CC_COMP"` + `-dumpmachine`（:52-53）双判交叉——全路径 gcc 不会误判；仅真交叉才写 CMAKE_SYSTEM_NAME（:57）与 FIND_ROOT_PATH 三模式（:61-64）；**恒追加 -fPIC**（:67-68）使静态库可链入 DALI 共享库。前置 validate_toolchain_env.sh：CC/CXX 成对校验（:17-19）、变量字符白名单防注入（:23，这些值会被插值进 CMake 代码）、交叉时强制 CMAKE_TARGET_ARCH（:30-34）。
- **两段构建系**（protobuf/grpc）：protobuf v36.1 先宿主机构 protoc、再交叉编目标库（build_protobuf.sh:66-72 `-DWITH_PROTOC=$HOST_INSTALL_PREFIX/bin/protoc`），并以 `-Dprotobuf_FORCE_FETCH_DEPENDENCIES=ON`（:32）顺带拉装 **abseil（非 submodule，全仓唯一来源）**；gRPC 是最复杂脚本——先宿主构建 grpc_cpp_plugin（build_grpc.sh:73-77），目标库以 `gRPC_*_PROVIDER=package` 复用 protobuf/abseil/zlib/openssl 单一副本（:98-101），c-ares/re2 走 module 模式指向自家 third_party（:102-104）。
- **configure+sed 系**（FFmpeg n9.0.1）：configure 大裁剪后用 sed 给 ffbuild/library.mak 的版本脚本符号统一加 `DALI_` 前缀（build_ffmpeg.sh:59-60），防与宿主 FFmpeg 符号冲突——本仓独有的技巧。
- **补丁系**：libsndfile 安装前连打 7 个 CVE 补丁（build_libsndfile.sh:21-27，覆盖 CVE-2022-33065 及 extra、2024-50612、2025-56226 两连、2026-37555、2026-88386）；libtar 两个 openEuler CVE 补丁（build_libtar.sh:29-30）；lmdb Makefile 以 `-p3` 适配 prefix（build_lmdb.sh:20）；zlib CVE 补丁（build_zlib.sh:21）。**补丁一律由脚本 apply，勿手动**（CLAUDE.md 钉版）。
- 特例：zstd 不走 CMake 直接 make（HAVE_LZMA=0）；OpenCV 5.0.0 仅 BUILD_LIST=core,imgproc,imgcodecs（build_opencv.sh:41）且 OPENCV_TOOLCHAIN_FILE 禁 `..` 路径穿越（:28-29）；google-cloud-cpp 约 200 个库只建 GCS（storage）客户端（build_google-cloud-cpp.sh:18 注释），GOOGLE_CLOUD_CPP_OVERRIDE_GOOGLEAPIS_URL 指本地 googleapis 副本（:71-75）。

## 4. 数据流与新人路线

数据流：`git submodule update --depth 1`（浅克隆省历史）→ third_party/<pkg> 源码 → 脚本打补丁 → 工具链文件/宿主 protoc → 装进 `$HOST_INSTALL_PREFIX` → DALI 主仓 CMake 以 prefix 找齐依赖（Bare Metal Build）。新人路线：读 README.rst 版本许可证表（21 行，nlohmann_json 在 :61）→ 跟 build_deps.sh 的 PACKAGE_LIST 顺序读 3 个代表脚本（build_protobuf.sh 两段构建 / build_grpc.sh provider 复用 / build_libsndfile.sh 补丁串）→ 交叉编译再看 generate_toolchain_file.sh。注意：不要 sudo 跑，用用户可写 prefix；README.rst:20/31 的 redist tar 直链只是源码备选，submodule 本体指向上游 GitHub（勘误见组 README）。
