# llamafile ONBOARDING · 单文件 LLM 分发系统新人导览

> 基于知识图谱（1994 节点/3051 边/14 层/15 步导览）与源码一手核实编写；源码 v0.10.x（Mozilla，Apache-2.0）。

## 1. 项目总览

llamafile 解决的问题是** LLM 分发的最后一公里**：把模型权重、推理引擎、Web UI 打包成一个跨平台单文件可执行程序——下载一个文件，`chmod +x` 后直接运行，无需安装 Python、无需编译。

三大技术支柱：

1. **Cosmopolitan Libc + APE 格式**：cosmocc 编译出 Actually Portable Executable——一份二进制同时是 Linux/macOS/Windows 等六大 OS 的原生可执行文件（polyfill 头 + fat binary 多 ISA 段）。
2. **二进制即 zip 容器**：APE 不规定文件尾布局，zip 中央目录可合法追加在尾部。GGUF 权重作为 zip 条目追加，运行时 zip.c 直读自身实现「自带模型」。
3. **浏览器 UI + 四种运行模式**：默认同时起 TUI 聊天与 OpenAI 兼容 HTTP server（含网页界面）；`--server` 纯服务；`--chat` 纯终端聊天；`--cli` 单次问答。

工程组织上不 fork 上游：llama.cpp / whisper.cpp / stable-diffusion.cpp 全是 vendored 子模块 + 补丁（41 个 .patch），llamafile 只维护胶水层。同一套容器技术复用三次：llamafile（LLM）、whisperfile（语音）、diffusionfile（文生图）。

## 2. 架构分层（14 层）

```
┌─────────────────────────────────────────────────────┐
│ L0  主程序与 Chatbot CLI     main.cpp / args / chatbot_*│
│ L1  Zip 容器与自解压          zip.c / datauri / image   │
│ L2  CPU SIMD 矩阵乘          sgemm / tinyblas / iqk    │
│ L3  GPU 后端动态加载          cuda.c / metal.c / vulkan │
│ L4  语法高亮引擎（44 语言）    highlight/               │
│ L5  llama.cpp 集成补丁        41 patches + BUILD.mk    │
├─────────────────────────────────────────────────────┤
│ L6  Whisper 语音工具链        whisperfile/transcribefile│
│ L7  Diffusion 图像生成        diffusionfile            │
│ L8  localscore 推理基准       localscore/              │
│ L9  mbedtls TLS 密码学        third_party/mbedtls (200)│
│ L10 其他第三方库              double-conversion/stb/sqlite│
│ L11 文档与 GitBook 站点       docs/                    │
│ L12 构建系统与 CI             Makefile / cosmocc / ci  │
│ L13 测试与集成验证            tests/integration (E2E)  │
└─────────────────────────────────────────────────────┘
```

- **L0**：统一入口与命令行体验；llamafile.c 是 fan-in 第 3 的运行时枢纽。
- **L1**：单文件分发的魔法层（zip 读写 + data URI 内嵌 + 构建期提取）。
- **L2**：性能皇冠——运行时 CPUID 探测微架构，分发到 fat binary 预编译微内核。
- **L3**：零 GPU SDK 链接，运行时 dlopen 探测 CUDA/Metal/Vulkan/ROCm，无 GPU 降级 CPU。
- **L4**：独立子库，服务 chatbot 着色与 server 网页 UI。
- **L5**：与上游的接口——补丁注入 zip 权重加载、sgemm 分发、沙箱。
- **L6-L8**：容器技术三次复用（语音/图像/基准）。
- **L9**：文件数最多（200 个），服务 https 下载与 TLS；Cosmopolitan 无系统 TLS 库故整体 vendored。
- **L10-L13**：支撑设施。

## 3. 核心模块

- **chatbot REPL**（约 15 个文件）：`chatbot.h` 会话全局状态；`chatbot_main.cpp` 加载模型后进 REPL；`chatbot_repl.cpp` 主循环；`chatbot_eval.cpp` 喂 token（含多模态 mtmd 路径）；`chatbot_hist.cpp` 历史与 undo/stack；`chatbot_comm.cpp` `/命令`；`chatbot_direct/api.cpp` 双后端。
- **args 参数系统**：`args.cpp` 把 llamafile 专属 flag 从 argv 剥掉，捕获 `-p/-m/-hf`，其余转交 llama.cpp。
- **zip 自解压**：`zip.c`（65 行）zip64 读取；`llamafile_open_zip` 把 `/zip/model.gguf` 路由到自身。
- **sandbox 沙箱**：`sandbox.c` 封装 pledge（SECCOMP 模拟）+ unveil（Landlock），默认拒绝外联与写文件。
- **sgemm 三件套**：`sgemm.cpp` 运行时分发；`tinyblas_cpu.h` 模板骨架+5 行 ISA 包装；`iqk_mul_mat.inc` 处理 K-quant；`compute.h/cpp` CPU 描述与线程。
- **GPU 后端**：`gpu_backend.c/h` 统一加载器；`cuda.c`/`metal.c`/`vulkan.c` 各自探测-加载-注册。
- **server**：不自带源码——server.cpp 补丁提取 `server_main()` 带回调入口，由 BUILD.mk 链进主程序。
- **whisperfile / diffusionfile**：容器技术第二、三次复用；**highlight/** 143 文件 44 语言；**mbedtls** vendored TLS 支撑 https 下载与 server TLS。

## 4. 关键概念

1. **APE「二进制即容器」**：APE 不约束文件尾，zip 中央目录可追加在可执行文件末尾——权重分发、Metal 源码内嵌、GPU DSO 分发全建立在这一个事实上；`zip -j model.gguf llamafile` 即产出带模型的发行文件，运行时 `/zip/` 前缀直读自身。
2. **Cosmopolitan Libc / cosmocc**：把 Linux syscall 语义 polyfill 到六大 OS；多目标编译让一份二进制含全部 ISA 微内核。
3. **__static_yoink**：Cosmopolitan 链接器指令，强制把源文件塞进 zip（`.zip.o` 对象）。metal.c 用它内嵌整个 ggml-metal 源码树，运行时编译 Metal dylib。
4. **TinyBLAS vs cuBLAS**：tinyblas.cu 是 cuBLAS API 兼容的自研 GPU 矩阵乘（模板 tile + Kahan 补偿 + warp 归约），无需闭源 cuBLAS 即可跑 GPU。
5. **iqk 单模板多 ISA**：一份 .inc 由各 ISA 包装 `#define llamafile_sgemm llamafile_sgemm_amd_zen4` 后 include，不同 -march 编译成多个 .o 全链入，运行时 CPUID 选择——BLIS/oneDNN 微内核分发的单文件复刻。
6. **gperf 关键字表**：highlight 库关键字判别由 gperf 生成完美哈希，O(1) 查找零启动开销。
7. **mbedtls 可重启运算**：多精度运算设计为可 setjmp/longjmp 中断重启，适配 Cosmopolitan 信号语义——少数能在 cosmo 上编译的 TLS 栈。
8. **GPU 后端 dlopen**：主二进制零 GPU SDK 链接；cuda.c/vulkan.c 运行时 dlopen 预编译 DSO，metal.c 现场从 zip 抽源码编译 dylib。
9. **pledge/unveil 沙箱**：OpenBSD 系统调用的 Linux 等价（SECCOMP/Landlock）；`anet` 只许 accept 不许 connect——被攻破的 server 也无法外传数据。
10. **chat 模板与 think 模式**：jinja 模板 + PEG 解析器把 `<think>` 推理流与正文流分离渲染；bestline（4092 行 linenoise 分支）承担行编辑。

## 5. 推荐学习路径（15 步）

1. **README + .gitmodules**：理解「子模块+补丁」策略——llamafile 只写胶水层。
2. **main.cpp + llamafile.c/h**：统一入口、四模式分发、运行时枢纽。
3. **chatbot 系列**：会话状态机与 REPL 主循环。
4. **zip 容器**：zip.c + datauri.cpp。
5. **sandbox.c + docs/security.md**：三级安全模型（默认 pledge、opt-in unveil、--unsecure 全关）。
6. **sgemm/tinyblas/iqk**：性能皇冠。
7. **GPU 动态加载**：gpu_backend.c + cuda/metal/vulkan 三实现。
8. **server 与补丁**：41 个补丁如何提取 server_main 并注入沙箱。
9. **whisperfile / diffusionfile**：容器第二、三次复用。
10. **highlight**：状态机高亮器 + gperf 关键字表。
11. **mbedtls**：基础层（platform.h fan-in 61 全库第一），理解为何整体 vendored。
12. **localscore**：最完整的「llamafile API 消费者」示例。
13. **构建系统**：根 Makefile 条件 include 各 BUILD.mk。
14. **测试**：tests/integration E2E + tests/sgemm + sandbox_test.c。

## 6. 文件地图（按层）

**L0 主程序**：`main.cpp`(507) 入口；`args.cpp/h` 参数过滤；`llamafile.c`(911)/`llamafile.h` 运行时枢纽；`chatbot.h`+`chatbot_main/repl/eval/hist/comm/cli(485)/direct/api.cpp` 会话全家桶；`bestline.c`(4092) 行编辑。

**L1 容器**：`zip.c/zip.h` zip64 读取；`datauri.cpp`；`image.cpp`；`extract_data_uris.cpp`。

**L2 矩阵乘**：`sgemm.cpp`(238) 分发器；`tinyblas_cpu.h`(1338) 模板骨架；`tinyblas_cpu_{sgemm,mixmul}_*.cpp` 各 ISA 包装；`iqk_mul_mat.inc`(3130)+包装；`fa_*_avx512f.cpp` FlashAttention 助手；`compute.cpp/h`。

**L3 GPU**：`gpu_backend.c/h` 统一加载器；`cuda.c`(194)/`vulkan.c`(162) DSO 加载；`metal.c`(679) 运行时编译；`parallel.c` 多卡。

**L5 补丁**：`apply-patches.sh`(81)；`patches/` 41 补丁；`llamafile-files/BUILD.mk`(652)；`fetch-ui-assets.sh`。

**L6-L8**：`whisperfile/`；`diffusionfile/`；`localscore/`。

**L9-L13**：`third_party/mbedtls/`（ssl_tls.c 8176、x509_crt.c 3282）+ double-conversion/stb/sqlite；docs/；Makefile+ci.yml；tests/（integration E2E、sgemm、sandbox_test.c）。

## 7. 复杂度热点

- `third_party/mbedtls/ssl_tls.c`（**8176 行**）：TLS 状态机全集，全库最大文件。
- `llamafile/bestline.c`（**4092 行**）：vendored 行编辑器，一般只调 API。
- `llamafile/iqk_mul_mat.inc`（**3130 行**）：量化矩阵乘模板，L2 层最难读；入口先看 DataInfo 与 mul_mat_t 指针类型。
- `third_party/mbedtls/x509_crt.c`（3282 行）：证书链解析。
- `tinyblas_cpu.h`（1338）/`tinyblas.cu`（1082）：CPU/GPU 模板骨架，读懂一个另一个是镜像。
- `metal.c`（679）：运行时编译 + __static_yoink。
- `llamafile-files/BUILD.mk`（652）：160+ 模型文件清单式构建。
- `main.cpp`（507）/`chatbot_cli.cpp`（485）：主流程，新人首读。

## 8. 与生态关系

- **vs llama.cpp 原生**：llama.cpp 是研究型多工具仓库；llamafile 把 server+chat 收敛为单文件产品，补丁跟随上游而非 fork。
- **vs ollama**：ollama 是「模型管理器+常驻服务+仓库」，需安装有 daemon；llamafile 零安装、模型即文件，但无模型版本管理。
- **vs LocalAI**：LocalAI 走「一个服务端多后端」；llamafile 差异化在分发格式本身，两者可互补。
- **Cosmopolitan 生态地位**：与 redbean 并列的门面应用，证明 APE + fat binary 能承载 G 级权重、SIMD 微内核、运行时 dylib 编译。
- **上游回馈**：sgemm/tinyblas CPU 路径以 `GGML_USE_LLAMAFILE` 宏被上游 llama.cpp 可选启用，下游反哺上游的典型。

> 阅读建议：先跑最小循环（`main.cpp → args.cpp → chatbot::main → repl`），再带着「权重从哪来（zip）/token 怎么算（sgemm）/安全谁保证（sandbox）」三个问题下钻 L1/L2/L5。
