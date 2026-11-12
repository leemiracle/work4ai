# explain-01 · FFI 入口与包门面：python/tvm/__init__.py 与 tvm_ffi 桥

## 角色定位

`python/tvm/__init__.py` 是整个 TVM Python 包的总门面：用户 `import tvm` 的第一瞬间，它按严格顺序装载 FFI 桥、运行时对象系统、各 IR 域（ir/tirx/te/relax）与后端工具。本 fork 最醒目的差异就在第 26 行——`from tvm_ffi import register_object, register_global_func, get_global_func`：上游 TVM 用自带的 `tvm._ffi` 子包，本仓把整个 Python↔C++ 桥抽成了**独立外部包 `tvm_ffi`**（PyPI 式依赖），`python/tvm` 里已没有 `_ffi` 目录。这个改动让 FFI 层可以单独发版、被 out-of-tree 后端复用，也意味着读代码时不能再按上游经验找 `tvm/_ffi/registry.py`。

与门面配套的两个小文件是真正的机制承载者：`python/tvm/base.py`（127 行内的库装载器）负责找到并 `dlopen` 两份动态库；`python/tvm/runtime/_ffi_node_api.py` 展示 `tvm_ffi.init_ffi_api` 的标准用法——全包 63 处 `_ffi_api.py` 都是这个模式。

## 内部结构

门面的装载顺序本身就是一张依赖图（行号锚定 `python/tvm/__init__.py`）：

- L26：最先 import `tvm_ffi` 的三个注册原语——注释 L25 明言 "ffi module must load first"；
- L29-30：`libinfo.__version__` 与 `base._RUNTIME_ONLY`，后者决定后面是否加载编译器；
- L33-36：从 `.runtime` 导入 `Object`、`device/cpu/cuda/vulkan` 等设备构造器与 `DataType`——对象系统先于一切 IR；
- L49：`from . import script` 抢在所有方言包之前——注释 L47-48 解释：方言 `__init__` 运行时要调 `tvm.script.register_dialect`，所以 TVMScript 基座必须先就位；
- L52-53：`tirx`（本 fork 的 TIR 本体）与 `ir.prim`；L62 `te`；L65 `from .driver import build, compile`——顶层 `tvm.build` 从这里来；
- L73-74：副作用导入 `support.rocm`/`support.nvcc`，注册 CUDA/ROCm 的 FFI 回调；
- L78-80：`if not _RUNTIME_ONLY` 才导入 `relax`——runtime-only 轮胎里没有编译器；
- L118：`sys.excepthook = tvm_wrap_excepthook(...)`，拦截 `DiagnosticError` 时提示 `TVM_BACKTRACE=1` 并 terminate 所有子进程（L110-113）；
- L125-127：`_autoload_backends()`——通过 entry-point 组 `tvm.backends` 自动加载树外后端，可用 `TVM_DEVICE_BACKEND_AUTOLOAD=0` 关闭。

`base.py` 的装载逻辑是两段式：L44-46 先以 `RTLD_GLOBAL` 加载 `libtvm_runtime.so`（符号暴露给后续扩展），L48-56 再尝试以 `RTLD_LOCAL` 加载 `libtvm_compiler.so`；失败（缺 LLVM 依赖等）不抛错，而是降级 `_RUNTIME_ONLY = True`。runtime-only 模式下 L59-61 还设置了 `tvm_ffi.registry._SKIP_UNKNOWN_OBJECTS = True`，让反序列化遇到编译器专属类型时跳过而不是崩。

`_ffi_node_api.py` 则是每个子域 `_ffi_api.py` 的模板：L28-37 先定义 runtime-only 兜底的 `AsRepr/SaveJSON/LoadJSON`（后者直接 raise "Do not support object serialization in runtime only mode"），L41 `tvm_ffi.init_ffi_api("node", __name__)` 把 C++ 侧 `TVM_REGISTER_GLOBAL` 的同名函数批量绑定进来覆盖兜底实现，L44 把 `tvm_ffi.core.__object_repr__` 指向 `AsRepr` 定制所有 Object 的 `repr`。

## 外部连接

- **`tvm_ffi` 外部包**：提供 `register_object`（按 C++ type_key 生成 Python 包装类）、`register_global_func/get_global_func`（跨语言函数表）、`init_ffi_api`（按命名空间批量拉取）、`Shape`、`access_path.AccessPath`（见 `runtime/script_printer.py:23-24`）等。它自带 `libinfo.load_lib_ctypes`（`base.py:23`），说明 dlopen 逻辑也下沉到了外部包。
- **libinfo**：`python/tvm/libinfo.py` 的 `package_lib_paths()`（L37）与 `find_libtvm_runtime()`（L59-77）提供 wheel 内 .so 搜索路径。
- **下游消费**：全包 63 个 `_ffi_api.py`（如 `runtime/disco/_ffi_api.py:21`、`testing/_ffi_api.py:19-24`、`s_tir/meta_schedule/_ffi_api.py`）都是 `_ffi_node_api.py` 模式的复制；`target/virtual_device.py:25-26` 直接用 `@tvm_ffi.register_object("target.VirtualDevice")` 演示了不写 C++ 也能挂对象。
- **树外后端生态**：L120-124 注释给出扩展协议——`[project.entry-points."tvm.backends"]` 声明即自动加载。

## 数据流

`import tvm` 的时序：Python 解释器执行 `__init__.py` → `tvm_ffi` 已先行可用（它自身是纯桥不含 TVM 符号）→ `base.py` dlopen `libtvm_runtime.so`（RTLD_GLOBAL，C++ 侧的 `TVM_REGISTER_GLOBAL` 函数表随库初始化注册进 tvm_ffi registry）→ 可用时再 dlopen `libtvm_compiler.so` → 各域 `_ffi_api.py` 通过 `init_ffi_api("tirx", ...)` 等把函数表拉成 Python 属性 → 顶层命名空间按 L33-80 顺序把 `Object/IRModule/build/...` 逐个挂到 `tvm.` 上。此后任何 Python 调用（如 `tvm.build`）都经 tvm_ffi 的 ctypes trampoline 进入 C++，返回的 `ObjectRef` 被包装成 `tvm_ffi.core.Object` 子类实例，refcount 由桥双向维护。

## 设计决策

1. **FFI 外包化**是本 fork 最大的结构投资：好处是编译器内核与语言绑定解耦，`tvm_ffi` 可服务多个项目、独立演进 ABI；代价是"读 TVM 学 FFI"的人必须去看另一个仓库。代码里所有 `import tvm._ffi` 的肌肉记忆都要换成 `import tvm_ffi`。
2. **双库拆分**（runtime RTLD_GLOBAL + compiler RTLD_LOCAL，`base.py:42-52`）：让只部署推理的环境不背 LLVM 链，且 compiler 符号不污染全局表、避免与扩展里的 LLVM 版本冲突；加载失败静默降级而非报错，是"能跑多少是多少"的发行哲学。
3. **异常钩子收尾子进程**（L110-113）：TVM 大量用 multiprocessing 跑测量，Ctrl-C 时主动 terminate 全部 active_children，防孤儿进程。
4. **script 先于方言**（L47-49）与 **relax 仅编译包**（L78）两处顺序约束都有注释钉版，改动 import 顺序会直接破坏方言注册。

## 新人提示

- 排查 "cannot find libtvm" 类问题从 `base.py:44` 与 `libinfo.py:59-77` 入手；设置 `TVM_USE_RUNTIME_LIB=1`（`base.py:33`）可强制 runtime-only。
- 遇到 Python 侧对象打印怪异，看 `_ffi_node_api.py:44` 的 `__object_repr__` 覆盖链。
- 想加树外 codegen，读 L120-127 的 autoload 协议比翻文档快。
- 本系列后续 11 篇所讲的 tirx/relax/s_tir 全部经由本篇的桥暴露给 Python——锚点失效时先确认你读的是 fork 布局（`tirx`/`s_tir`）而非上游（`tir`）。
