# compiler-driver.md — `python/triton/compiler/compiler.py`（编译驱动，Triton 3.8.0，520 行）

## 1. 角色定位

Triton 编译器**总编排层**，图谱归属 `layer:compiler-frontend 编译器前端驱动`。它不实现编译逻辑——AST→TTIR 在 `code_generator.py`，阶段降级在 `third_party/*/backend/compiler.py`，pass 本体是 C++ MLIR——只决定从哪级 IR 开始、跑哪些 stage、产物存哪/怎么装载。`triton/__init__.py` 顶层 `from .compiler import compile`，是库门面。

## 2. 内部结构

- **双源抽象**：`ASTSource`（L52）包装 `@jit` 函数（`make_ir` L78 委托 `ast_to_ttir`）；`IRSource`（L87）包装磁盘 `.ttir/.ttgir/.ptx`，服务离线编译——PTX 无解析器，用正则（L28）抠签名。
- **主流程**：`compile()`（L226）；`make_backend()`（L366）按 `GPUTarget` 唯一匹配后端。
- **产物句柄**：`CompiledKernel`（L407）持 metadata 与各级 IR 文本（`AsmDict` L390 惰性补 sass）；`_init_handles()`（L452）延迟装载；`LazyDict`（L374）惰性 launch metadata。
- **辅助**：`filter_traceback`（L149）剔内部栈帧；`CompileTimer`（L187）按 stage 计时。

## 3. 外部连接

出边：`triton._C.libtriton`（`ir`）、`backends/compiler.py`（`BaseBackend/GPUTarget/Language`）、`runtime/cache.py`、`runtime/driver.py`、`runtime/autotuner.py`（`OutOfResources`）、`tools/disasm.py`、`knobs.py`。入边：`runtime/jit.py:912`（`_do_compile` 调 `self.compile`，热路径唯一生产者）、`compiler/__init__.py`、`experimental/gluon/_runtime.py`；`ASTSource` 被 `GluonASTSource` 继承。下游 `third_party/nvidia|amd` backend（图谱未覆盖，0 节点）。

## 4. 数据流（一次 compile()）

1. 构造 `ASTSource` → `compile(src)`；`driver.active.get_current_target()` → `make_backend`（L231-234）。
2. `get_cache_key`（L246）混入后端 hash 与失效环境变量；命中则直接返回 `CompiledKernel`（L268-279）。
3. `backend.add_stages`（L291）填有序表 `{"ttir","ttgir","llir","ptx","cubin"}`；`first_stage = stages.keys().index(src.ext)`（L292），IRSource 再 `+1` 跳过起始阶段 pass（L294），便于手写 IR 测试。
4. `ir.context()` + 双 `load_dialects`（L299-302）→ `src.make_ir()` 产出 TTIR（L307）。
5. 降级循环（L326-352）：`compile_ir(module, metadata)` 逐级执行；每级写 cache group，dump 时同步落盘并在 cubin 级补 sass（L340-344）；override 可替换任一级 IR（L332-336）。metadata 跨 stage 传递。
6. metadata 写回（L354）返回 `CompiledKernel`；首次取 `.run` 才 `_init_handles()`——建 launcher、查 shared/tmem/threads 三项 `OutOfResources`（L471-488）、装 cubin；`__del__`（L440）按 pid 防 fork 误卸载。

## 5. 设计决策

- **stage 表自报而非硬编码**：驱动按 dict 序执行，后端可增删阶段（Gluon 从 ttgir 起），驱动零改动——后端插件系统支点。
- **四级 IR 分层**：TTIR（设备无关）→ TTGIR（layout 决策）→ LLIR（复用 LLVM）→ PTX/cubin（交 ptxas）；前端只生成 TTIR，GPU 决策全部推迟。
- **override/dump 埋在循环内**：任一级 IR 可替换后重跑，编译器即实验平台。
- **缓存即产品**：产物从磁盘 metadata 组装，跨进程与 warmup 成立。

## 6. 新人提示

- **阅读**：先 `compile()` L226-363 主线；配 DeepWiki `1.1-system-architecture-and-compilation-flow.md`。
- **dump**：`TRITON_KERNEL_DUMP=1 TRITON_DUMP_DIR=/tmp/d` 落盘全套；`MLIR_ENABLE_DUMP=1`（可填函数名，ir.cc:1948）打印每 pass 前后 IR；`TRITON_ALWAYS_COMPILE=1` 绕缓存。
- **相关**：`code_generator.py`（上游）、`third_party/nvidia/backend/compiler.py`（见 make-ttgir.md）、`runtime/jit.py:887-912`；回归 `test/TritonGPU/*.mlir`。
