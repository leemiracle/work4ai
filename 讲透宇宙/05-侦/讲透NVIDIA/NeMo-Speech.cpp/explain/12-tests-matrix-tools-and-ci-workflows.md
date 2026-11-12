# 12 · 测试矩阵、诊断工具与 CI 三 workflow（L15 · 71 节点群）

## 角色定位

L15 层 71 节点是全仓质量基础设施：`tests/` 七个子目录按"无模型单测 → 带模型冒烟 → 契约/安装/集成"分层，`tools/` 三件诊断器，`.github/workflows/` 三条流水线把前两者按平台分摊。设计核心是**模型与测试解耦**：绝大多数 C++ 测试不需要下载 GGUF 即可编译运行，需要模型的测试由环境变量门控并写进 ctest，CI 再用按 `models/index.json` 哈希键控的缓存（build.yml:91-93）补一轮真模型冒烟——本地快速、云端彻底。

## 内部结构

**tests/cpp/asr 实为 23 个 test_*.cpp + 2 个共享头**（`itn_test_cases.h`/`numeric_parity.h`；任务书口径 17 偏旧），覆盖音频解码/重采样/mel 特征、CTC 与 RNNT 的 offline+streaming、cache-aware 流几何（专设 `NEMO_SPEECH_TEST_CACHE_AWARE_RNNT_MODEL` 变量与 TEST_ASR_MODEL 分离，tests/cpp/asr/CMakeLists.txt:11-13）、解码器、VAD/endpointer/postproc/pnc、diar 三件（state/streaming/recognizer）、sortformer 数值对齐、并发压测（test_rnnt_concurrency 链 Threads::Threads，tests/cpp/asr/CMakeLists.txt:26-28）、skinny q8 分发、OOV boost。注册策略三态：无模型可跑的直接 `add_test`（如 endpointer_policy，tests/cpp/asr/CMakeLists.txt:33-34）；合成 GGUF 恒跑+真模型可选比较的用 `SKIP_RETURN_CODE 77`（gguf_mmap_loader，tests/cpp/asr/CMakeLists.txt:19-21）；要模型的靠 env 注入。tests/cpp 其余：tts 12 件（MagpieTTS 注意力先验/缓存注意力/帧堆叠 + NanoCodec 守卫/半蛇形融合 + mandarin/single_chars 分词器 + 文本归一化/终止标点）、nmt 2 件（langpairs 表+nmt 翻译）、common 3 件（共享工具/字幕/HTTP 配置）、根下 test_cublas_shim_numerics.cu、`utils/wer.cpp` 编成 tests_cpp_wer 静态库供各处算 WER（tests/cpp/CMakeLists.txt:1-7）。

**tests/c 四件**：asr/tts 各配 smoke+dlopen——以 **C（非 C++）编译**证明 `include/nemo_speech/*.h` 是合法 C 头且 C ABI 库可链可跑（tests/c/asr_c_smoke.c:3-7）；无参只打印版本做链路检查，带参跑真识别。**Python 五线**：tests/ci/model_smoke.py 用真模型做 ASR（jfk.wav）、TTS 往返、TN/ITN 数字往返（"I paid 25 dollars"须先 TN 成 "twenty five" 再被 ITN 转回，model_smoke.py:28-31），比对用相似度比而非全等防后端数值抖动（model_smoke.py:7-11）；tests/cli 三件——cli_contract 校验错误输出 JSON 契约且错误不污染 stdout（cli_contract_test.py:25-29）、model_store（需 curl）、transcribe_workflow；tests/conversion 四件锁转换器契约与 TTS 布局/说话人名/分词 profile；tests/install 三件——sdk_consumer 直接注册进 ctest（installed_sdk_consumer，180s 超时，tests/cpp/CMakeLists.txt:34-41），install_sh_test 自建本地 http.server+tar 服务来测安装脚本（install_sh_test.py:8-12）；tests/integration 两件 http/voicechat 实时一致性（动态找空闲端口起服务，http_conformance_test.py:17-20）+ openai_client.mjs 参考客户端。

**tools 三件诊断器**：`bench_asr_batching` 双模式（stream 节拍 PCM 到达，latency=完成时刻-计划到达时刻使过载积压可见；offline 整句 Recognize），支持 --concurrency 1..16 扫描与 VAD/PNC 挂载，计时区内零文件 IO、配 cuBLAS shim 做 LD_LIBRARY_PATH A/B（tools/bench_asr_batching.cpp:3-21）；`check_backend_coverage` 载入 GGUF 对每个 Session 跑一步、dump 每个图节点的后端归属，**exit 2 = 检测到 CPU 回落**——每个回落算子迫使每音频块一次 GPU↔CPU 往返，对流式延迟是灾难（tools/check_backend_coverage.cpp:3-21），也是 llama.cpp rebase 后的必跑项（patches/README.md:96-100）；`nanocodec` 是 NanoCodec 独立入口。

## 外部连接

三条 workflow 分工：**build.yml**（GitHub 托管机）四 job——patch-series 10 分钟跑 `scripts/llama-patches.sh check`（系列必须能应用且与 export 字节级一致，build.yml:48-54）、linux-cpu 90 分钟（configure cpu-speech→ctest timeout 600→模型缓存→model_smoke，build.yml:56-99）、macos-metal 仅编译链接（托管 VM 的半虚拟 GPU 跑不了 Metal，推理在 CPU 验证，build.yml:6-8 头注释）、windows-cpu；draft PR 跳过、并发取消旧跑、action 全钉 SHA、permissions 只读（build.yml:21-28）。**gpu.yml**（NVIDIA 自托管 L4）：Linux CUDA job 用 cuda-speech preset（CMake 自动打补丁，gpu.yml:79-82）跑全量 ctest+真模型冒烟；Windows Vulkan job 构建+CPU 冒烟，vcpkg 缓存。**release.yml**：vX.Y.Z tag→draft（人审后发布）、nightly 定时→prerelease 原地重建、PR 仅当改动命中打包路径过滤正则才 dry run（release.yml:71-78）；tag 与 VERSION 不符直接 error（release.yml:90-92）；nightly 版本号形如 0.2.0+nightly.a1b2c3d 防与正式版混淆（release.yml:118）；ITN 文法产物按版本 pin 复用不重建（release.yml:16-17）。

## 数据流

ctest 聚合三层：C++ add_test（无模型+env 门控）→ Python 包装测试（installed_sdk_consumer/cli_contract/cli_model_store 经 `find_package(Python3)` 条件注册，tests/cpp/CMakeLists.txt:29-66）→ CI 专属冒烟（model_smoke 按 backend 参数分 CPU/CUDA）。test_files 夹具（jfk.wav、AMI 60s 三说话人片段、LJSpeech 10 行）贯穿单测与冒烟两层。

## 设计决策

- **SKIP_RETURN_CODE 77 语义**：模型缺席时测试显式跳过而非失败，ctest 绿灯保留（tests/cpp/asr/CMakeLists.txt:19-21）。
- **相似度而非全等**：真模型输出比对容忍后端数值差，冒烟只抓功能性回归（model_smoke.py:36-38）。
- **C 头自证**：tests/c 以纯 C 编译证明 ABI 头无 C++ 泄漏，这是 SDK 对外承诺的最硬证据（asr_c_smoke.c:3-7）。
- **patch-series 独立 job**：补丁合规（应用+export 复现）10 分钟内单独判定，不与 90 分钟构建耦合（build.yml:41-54）。

## 新人提示

本地最快验证循环：`cmake --preset cpu-speech -DNEMO_SPEECH_BUILD_TESTS=ON` + ctest（无需模型，对应 build.yml:79-82 的 configure/build 步）；想跑真模型设 `NEMO_SPEECH_TEST_ASR_MODEL`/`NEMO_SPEECH_MODEL_DIR` 后重跑 ctest，门控测试自动进池。提交前看 build.yml 的 patch-series job 是否绿——手改 .patch 文件必红。新增测试记得同步 tests/cpp/asr/CMakeLists.txt 的 add_executable/add_test 对；纯 Python 测试走 CMake 条件注册路径而非塞进 ctest 目录。性能回归排查顺序：check_backend_coverage（先排除 CPU 回落）→ bench_asr_batching 扫并发 → BENCHMARK.md 口径对表。
