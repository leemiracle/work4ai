# llamafile server 集成精讲 — server.cpp 补丁 + BUILD.mk 构建系统

## 角色定位

llamafile 没有 server 源码——HTTP 服务完全来自 llama.cpp 子模块，经 `llama.cpp.patches/` 定制后编进主二进制。链路三件套：`patches/tools_server_server.cpp.patch`（263 行功能改造）、`llamafile-files/BUILD.mk`（652 行构建注入）、`apply-patches.sh`（81 行）。不 fork，上游更新只需调和补丁。

## 内部结构

**server.cpp 补丁**做三件事：

1. **server_main() 提取**：上游 main 逻辑提取为 `server_main(argc, argv, on_ready, on_shutdown_available)`——on_ready 让 main.cpp 后台拉起 TUI；on_shutdown_available 把关停函数交给 TUI，退出聊天即优雅关停。
2. **沙箱注入**：load_model() 之前调 `llamafile_sandbox_server(&spec, ...)`——时机刻意在「不可信 GGUF 解析前」。combined 模式跳过沙箱并警告（TUI 要 connect 本地 server，与 accept-only 冲突）。
3. **flag 消化**：`llamafile_consume_flag` 移除 --confine-reads 等专属项，防上游报错。

同目录另有 server-http/models/queue/stream 四补丁（UI 路由、元数据等）；`ggml_src_ggml-cpu_*.patch` 系列把 `GGML_USE_LLAMAFILE → llamafile_sgemm()` 钩进算子层。

**BUILD.mk（llamafile-files/）** 构建心脏，六段式：GGML / LLAMA（+160+ models/*.cpp）/ COMMON（采样/jinja 模板/PEG/https）/ MTMD（clip+40 视觉模型）/ cpp-httplib（`CPPHTTPLIB_MBEDTLS_SUPPORT` 编进 vendored mbedtls——宏改类布局，触及 httplib.h 者必须统一看见）/ TOOLS。链接规则压轴：llama-server = server+UI+MTMD+HTTPLIB 对象 + llamafile.o/gpu.a/sandbox.o/zip.o + TINYBLAS_CPU_OBJS + llama.cpp.a + mbedtls.a，`.SECONDEXPANSION` 引用 llamafile/BUILD.mk 后定义的 TINYBLAS 变量。`-DGGML_USE_LLAMAFILE -DGGML_USE_CPU_REPACK -DGGML_MULTIPLATFORM -fopenmp` 全体生效。

**Web UI 管线**：上游 UI 是 Svelte/PWA，但 cosmocc 无 JS 工具链——`fetch-ui-assets.sh` 从 ggml-org/llama-ui 的 HF 桶拉预构建 dist，embed.cpp 嵌成 ui.cpp/ui.h（gzip 资产服务）；无资产退化为 stub。

**apply-patches.sh**：校验子模块干净 → 拷 llamafile-files/ → renames.sh 重排 → rm Makefile → 逐个 `patch -p1`。strict 首败即停；`--tolerant` 留 .rej 续跑供上游 bump 调和。

## 外部连接

上游：llama.cpp 子模块（pin 特定 commit，UI 资产版本配套）。下游：llamafile/BUILD.mk 把 server.cpp.o 指向补丁后的 llama.cpp/tools/server/server.cpp，与主对象链接成单文件。generate-patches 反向 diff 出新补丁。

## 数据流

```
git submodule pin llama.cpp@X
  └─ make setup ─▶ apply-patches.sh
        ├─ cp llamafile-files/* → llama.cpp/ + renames.sh + rm Makefile
        ├─ patch -p1 × 41（strict 败即停）
        └─ fetch-ui-assets.sh → embed.cpp → ui.cpp/ui.h
  └─ make: GGML/LLAMA/COMMON/MTMD/HTTPLIB → llama.cpp.a
        链接: server*.o + ui.o + llamafile.o/gpu.a/sandbox.o/zip.o
              + tinyblas*.o + mbedtls.a → llama-server
运行期: --server ─▶ server_main(null)
        (AUTO)  ─▶ server_main(起TUI, 交给TUI)
```

## 设计决策

1. **回调注入代替 fork**：TUI+server 协作用两个回调达成，补丁面最小、diff 最稳。
2. **沙箱住进 server 补丁**：必须赶在 load_model 前落锁，时序决定注入点。
3. **BUILD.mk 注入而非改上游 CMake**：cosmocc 与 CMake 语义差异大（APE 多目标、zip 对象）。
4. **预构建 UI**：承认 cosmocc 边界，用 HF 资产换构建简单性。
5. **strict/tolerant 双模式**：日常严格防漂移，升级宽容留调和。

## 新人提示

- 调和上游 bump：先跑 `--tolerant`，逐个 .rej 手工落位，再 generate-patches 重出补丁集；别直接编辑 patch 文件。
- server 行为差异先查补丁：`grep -n llamafile llama.cpp.patches/patches/tools_server_*`，多数答案在补丁里。
- include httplib.h 的新文件必须挂同一 CPPHTTPLIB_MBEDTLS_SUPPORT 宏，否则 ODR 崩溃。
