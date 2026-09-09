# llamafile/main.cpp + args.cpp 精讲 — 统一入口与参数系统

## 角色定位

main.cpp（507 行）是 llamafile 唯一的 `int main`，把原始 argv 变成「确定的执行模式 + 过滤后的上游参数」。args.cpp（127 行）+ args.h 是前置过滤器：llamafile 新增的 flag（--server/--chat/--cli/--gpu/--unsecure 等）上游解析器不认识，必须在转交前剥掉。这对文件是所有功能的汇聚点——四种模式、GPU 早期初始化、日志静默策略都在此定调。

## 内部结构

main.cpp 的结构按执行顺序分五段：

1. **诊断信号处理器**：`diag_signal_log` 是 async-signal-safe 信号记录器，仅 `LLAMAFILE_TRACE_SIGNALS=1` 时安装，追查 EINTR 类崩溃；SIGINT/SIGTERM 不动，留给上游优雅关停。
2. **双层 --help**：`print_*_help` 手写 llamafile 自有模式简介；`print_llama_cpp_usage` 把完整目录委托给 `common_params_parse()`——同一代码路径保证 help 与实际 flag 永不漂移。
3. **combined_main**：AUTO 模式双线程编排——server 跑主线程（独占 GPU/CUDA），TUI 跑后台 pthread，`pthread_attr_setstacksize(8MiB)` 是踩坑修复：Cosmopolitan 默认线程栈扛不住 httplib+SSE+json 递归调用链。mutex+condition_variable 同步 shutdown_fn 就绪。
4. **main 主体**：`cosmo_args("/zip/.args")` 读入打包时默认参数 → `--version` 短路 → 解析 → help/缺 -m 错误路径 → 非 verbose 三连静默（llama/metal/cuda 日志，顺序敏感：cuda 的 log_set 触发 DSO 加载）→ 非 server 注入 `--log-verbosity 1` → `llamafile_has_gpu()` 触发 GPU 加载 → switch 分发四模式。

`parse_llamafile_args` 做四件事：先调 `llamafile_early_gpu_init`（须在过滤前，读 --gpu/-ngl 设 FLAG_gpu）；捕获 `-p/-m/-hf/--model-url` 值（多个 -p 后者胜，有意的 override）；由 flag 定 ProgramMode（AUTO 兜底）；`is_llamafile_flag` 白名单过滤 argv，`--gpu` 连带跳过值参数。过滤结果存静态 `g_filtered_argv`——函数返回后仍需存活，刻意的生命周期设计。

## 外部连接

上游依赖：`arg.h`（common_params_parse）、`chatbot.h`（chatbot 三入口）、`llamafile.h`（FLAG_* 与 GPU 探测）、前置声明的 `server_main`（定义在打过补丁的 llama.cpp server.cpp 里，链接期才见面）。combined_main 经 `chatbot::api_main(listen_addr,...)` 把 server 就绪地址喂给 TUI；`on_shutdown` 回调把关停函数交给 TUI，实现「退出聊天即退出整个程序」。`LlamafileArgs` 结构体是 main→各模式的数据契约（mode + llama_argc/argv + 三缓存）。

## 数据流

```
argv ──cosmo_args──▶ /zip/.args 合并
     ──parse_llamafile_args──▶ {mode, FLAG_*, llama_argv(过滤后), 提示词缓存}
        ┌───────────┼─────────────┬──────────────┐
        ▼           ▼             ▼              ▼
   server_main  chatbot::main  chatbot::cli  combined_main
   (主线程)     (直接加载模型)  (单次问答)    (主线程server+子线程TUI,
                                              api_main走HTTP客户端)
```

- `--version` 在一切之前处理，忽略其余参数。
- 缺 `-m` 且无 `-hf/--model-url` 时打印对应模式 help 并 `return 1`（remote_model 兜底：模型可由上游在加载期 https 下载）。
- `--confine-reads` 只对 --server 生效，其它模式显式 warning 而非静默忽略。

## 设计决策

1. **过滤而非重写解析器**：llamafile 不复制 llama.cpp 参数体系，只做减法+转发，上游加新 flag 零成本继承——「补丁式跟随上游」策略在参数层的投影。
2. **help 委托**：与解析逻辑同源，天然防漂移。
3. **server 占主线程**：CUDA 上下文绑定 OS 主线程最稳，TUI 作为 HTTP 客户端反而轻——主从倒置是 combined 模式核心决策。
4. **静态存储 g_filtered_argv**：单次解析单次使用，悬垂指针最简单的解。

## 新人提示

- 改执行模式逻辑先看 `ProgramMode` 枚举与 main 尾部 switch（default 兜底）。
- 新增 llamafile 专属 flag 要动两处：`is_llamafile_flag` 白名单（args.cpp）+ help 文本（main.cpp），漏一处要么上游报错要么 help 缺项。
- `print_llama_cpp_usage` 内 `common_params_parse` 在 --help 时 `exit(0)`，后面 return 0 不可达。
- 调信号问题设 `LLAMAFILE_TRACE_SIGNALS=1`；调参数问题打印 llama_argv 确认过滤结果。
- combined 模式 TUI 挂 8MiB 栈 pthread，此链路新增递归解析要先算栈深。
