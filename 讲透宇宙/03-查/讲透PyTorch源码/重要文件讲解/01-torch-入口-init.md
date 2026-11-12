# torch/__init__.py — `import torch` 时究竟发生了什么

> 源文件：`torch/__init__.py`（3548 行）
> 知识图谱节点：`file:torch/__init__.py`，complexity=complex，tags=[入口点, 核心组件, public-api, 符号形状, 配置]
> 图谱 commit：f634d0e91da4cc1d4d669a60ede149214b754854（2026-09-03 分析）

---

## 一、它在架构中的位置

这是整个 PyTorch 的**顶层包入口门面（facade）**。知识图谱把它归入
`layer:tensor-core-dispatch`（张量核心与 C++ 调度）层——这一层包含 ATen/c10 的 C++
核心与 `torch/_tensor.py` 等 Python 门面；而本文件正是把 C++ 编译产物 `torch._C`
"翻译/组装"成你天天用的 `torch.*` Python API 的那个组装点。同时它也是 Tour #1
（仓库概览）的终点站：README → GLOSSARY → 本文件，构成理解仓库的"地图目录"。

从依赖图看它的分量：

- **入边 307 条**（272 个文件 `import torch` + 35 个 `depends_on`）——全仓库被引用最多的文件，事实上的依赖图根节点；
- **出边 76 条**：`contains` 40（本文件定义的函数/类）、`exports` 25（进入 public API）、`imports` 10（`torch/_tensor.py`、`torch/nn/__init__.py`、`torch/optim/__init__.py`、`torch/cuda/__init__.py`、`torch/distributed/__init__.py`、`torch/fx/__init__.py`、`torch/export/__init__.py`、`torch/profiler/__init__.py`、`torch/_ops.py`、`torch/_tensor_str.py`）、`depends_on` 1（`torch/_dynamo/__init__.py`）。

一句话定位：**它不做计算，它负责"把 C++ 内核装进 Python 命名空间"**——加载动态库、
修正命名、注册子模块、管理 `__all__`，并托管一小批必须住在顶层的 API
（SymInt 家族、默认 dtype/device、确定性开关、`torch.compile`）。

---

## 二、内部结构：按执行顺序拆解

这个文件几乎是**顺序执行**的初始化脚本。以下按 `import torch` 的真实时间线分段
（行号均为当前源码行号）。

### 阶段 0：标准库导入与版本（L11-66）

```python
import builtins, ctypes, functools, glob, importlib, ...  # L11-44
from torch.torch_version import __version__ as __version__  # L66
```

两个细节：

- 注释里大量使用 `builtins.bool` / `builtins.int` 全限定写法（如 L50、L821）。因为本文件
  会把 `torch.bool`（dtype 实例）、`e`/`pi`/`nan`/`inf`、`compile` 等名字放进模块全局
  命名空间，全限定写法杜绝类型检查器与读者的歧义。
- `__version__` 不在本文件定义，来自 `torch/torch_version.py`（构建时生成）。

### 阶段 1：`__all__` 的"种子列表"（L82-159）

手写维护的 `__all__` 列表（L82-155），紧跟一个**运行时自检**（L158-159）：

```python
if __all__ != sorted(__all__):
    raise AssertionError("__all__ must be kept sorted")
```

注意这只是种子。后面会看到 `__all__` 被 `append`/`extend` 多次扩充——它是**动态组装**
出来的：种子 → `dir(_C)` 循环 → `_VariableFunctions` 循环 → dtype 扫描 → 数学常量。

### 阶段 2：平台相关的动态库装载（L162-453）

这是整个文件最"系统编程"的部分，目标只有一个：让 `from torch._C import *`（L478/L495）
能成功。

1. **ROCm runtime wheels**（L171-177）：尝试 `from . import _rocm_init`，存在则调用
   `_rocm_init.initialize()`；不存在静默跳过（ImportError → pass）。
2. **Windows DLL 手动装载**（L180-310，`_load_dll_libraries`）：用 `ctypes.WinDLL`
   调 `kernel32.LoadLibraryExW`，把 `torch/lib`、CUDA Toolkit、NvToolsExt 等 DLL 目录
   逐一 `os.add_dll_directory`。细节：DLL 锚点用 `importlib.util.find_spec("torch._C").origin`
   而非 `__file__`（L191-197 注释解释：editable 安装时源码树的 `lib/` 是空的）。
3. **Linux CUDA 依赖预载**（L313-388）：
   - `_get_cuda_dep_paths`（L313）：兼容三种 wheel 布局——`nvidia/<lib>/lib/`、
     `nvidia/cuXX/lib/`（CUDA 13.0 起）、`<lib>/lib/`；
   - `_preload_cuda_deps`（L351）：**顺序敏感**！L353-356 注释明确：必须先
     `libcublasLt` 后 `libcublas`，否则 libcublas 会经 RUNPATH 拉起系统里版本不匹配
     的 cublasLt，导致符号错误。列表覆盖 cudnn/nvrtc/cudart/cupti/cufft/nccl/cusolver 等
     全家桶。
4. **`_load_global_deps`**（L392-453，见 C++ 侧 Note [Global dependencies]）：
   `ctypes.CDLL("libtorch_global_deps.so", mode=ctypes.RTLD_GLOBAL)`（L423）。
   这个小库的唯一使命是把 libstdc++/mkl 等公共符号以 `RTLD_GLOBAL` 方式先拉进进程，
   避免各 SO 各自装载冲突版本。随后读 `/proc/self/maps`（L431）判断 libcudart 是否
   已加载，据此决定是否 best-effort 预载 CUDA 组件 wheel（L445），注释解释了这是
   为了让已存在的 wheel 在 `libtorch_cpu` 的 DT_NEEDED soname 查找中"抢先中标"。
5. **关键分叉**（L456-495）：
   ```python
   if (USE_RTLD_GLOBAL_WITH_LIBTORCH or os.getenv("TORCH_USE_RTLD_GLOBAL")) and ...:
       sys.setdlopenflags(os.RTLD_GLOBAL | os.RTLD_LAZY)
       from torch._C import *   # L478 "hard way"
   else:
       if USE_GLOBAL_DEPS:
           _load_global_deps()
       from torch._C import *   # L495 "easy way"，绝大多数用户走这条
   ```
   L483-486 注释说明为何默认不用 RTLD_GLOBAL：防止 libtorch 的 C++ 符号污染全局
   符号表、与其他库冲突产生神秘 segfault。

### 阶段 3：符号类型 SymInt / SymFloat / SymBool（L498-1407）

占了文件近 1/3 篇幅，是 dynamic shapes（`torch.compile` 符号形状推断）的 Python 面：

- 三个"类型桩"基类 `_SymTypingMagicAlsoBool` / `_SymTypingMagic` /
  `_SymTypingMagicBitwise`（L511/L613/L783）：满屏
  `raise TypeError("type stub not overridden")`。**它们不是实现**——真正的魔术方法由
  `torch.fx.experimental.sym_node` 在 L3347 被 import 时以副作用方式装回去
  （L3346 注释："Populate magic methods on SymInt and SymFloat"）。桩存在的意义是给
  静态类型检查器提供精确的 overload 签名（如 `SymInt + float -> SymFloat` 的类型提升
  规则，L503-507 有专门注释）。
- `SymInt`（L806）/`SymFloat`（L961）/`SymBool`（L1070）：薄包装，
  `self.node` 字段持有 `SymNode`（L816-819 注释：字段名必须是 `node`，C++ binding
  依赖此约定）。
- `sym_not` / `sym_float` / `sym_int` / `sym_max` / `sym_min` / `sym_sum` / `sym_ite` /
  `sym_fresh_size`（L1159-1407）：符号感知的工具函数，入口都有
  `overrides.has_torch_function` 分支以支持 `__torch_function__` 协议。
- 工厂循环生成 `_sym_sqrt` / `_sym_sin` 等（`_get_sym_math_fn`，L1352-1385），循环变量
  用完即 `del`（L1385）——本文件反复出现的命名空间卫生手法。

### 阶段 4：`torch._C` 哨兵检查与命名修正（L1410-1483）

- L1412-1434：用 `from torch._C import _initExtension` 作哨兵探测 C 扩展可用性；
  失败且 `torch/_C` 是源码目录（`__file__ is None`）时，抛出一段**手把手指引**
  （"用 `pip install -e .` 的 develop 工作流"）的 ImportError——这是给从源码树构建
  PyTorch 的开发者的救命提示。
- L1442-1460：核心循环——遍历 `dir(_C)`，把公开名（不以 `_` 开头、不以 `Base` 结尾）
  加入 `__all__`，并把 C++ 对象的 `__module__` 改写为 `"torch"`（L1455），这样
  `repr`/pickle 显示的模块是 `torch` 而非 `torch._C`。特例：`TensorBase` 被主动
  `delattr` 出 torch 命名空间（L1456-1458，issue 109438——防止与 `torch.Tensor` 混淆）。
- L1467-1483：`_import_extension_to_sys_modules`——C 扩展的子模块（如
  `_C._dynamo.eval_frame`）不是标准 Python 包，pickle 找不到它们；此函数递归地把
  这些伪子模块注册进 `sys.modules`（L1478），修复 pickle（Python issue 43367）。

### 阶段 5：顶层工具函数（L1490-2320）

必须在子模块之前定义（子模块会引用它们）：

- `typename` / `is_tensor` / `is_storage`（L1490/1525/1540）——注意签名用的是
  `_TypeIs`/`_TypeGuard`（L1525），现代 type-narrowing 注解。
- 默认设备/dtype 管理：`get_default_device`（L1574）、`set_default_device`（L1607）、
  `set_default_tensor_type`（L1671，legacy）、`set_default_dtype`（L1702）——
  落到 `_C._set_...` 系列 C 调用。
- 确定性算法：`use_deterministic_algorithms`（L1755）、
  `are_deterministic_algorithms_enabled`（L1905）、`set/get_deterministic_debug_mode`
  （L1920/1964）。
- `get/set_float32_matmul_precision`（L1979/1986，TF32 三档 "highest"/"high"/"medium"）。
- `_check*` 家族（L2080-2286）+ `_assert`（L2665）：**可被符号追踪的 assert**——普通
  `assert` 在 export/compile 时无法变成 guard，而 `_check` 会转成
  `torch._check` 语义供 AOTAutograd 记录约束。这是 export 工作流的关键设施。
- L2315-2320：从 `math` 导入 `e, inf, nan, pi`，定义 `newaxis = None`，全部
  `extend` 进 `__all__`——为了对齐 Python Array API 规范与 NumPy 习惯
  （`torch.newaxis` 就是 `None`）。

### 阶段 6：Tensor 与 Storage（L2322-2565）

```python
from torch._tensor import Tensor  # usort: skip   (L2326)
from torch import storage as storage  # usort: skip (L2329)
```

- `Tensor` 类本体在 `torch/_tensor.py`（图谱中本文件对它有 `imports` 边）；
  `torch/__init__.py` 只负责把它挂到顶层。`# usort: skip` 注释全文随处可见——
  因为这里的导入顺序是**语义正确的必要条件**，不允许排序工具重排。
- L2339 注释立规矩：**新的 dtype 不要再加 `<Type>Storage` 类，直接用
  `TypedStorage`**。随后的 `ByteStorage`…`QUInt2x4Storage`（L2341-2530）全是用
  `classproperty` 覆写 `dtype` 的 legacy 壳，且访问即触发弃用警告
  （`_warn_typed_storage_removal`）。
- L2554-2565：`amp`/`random`/`serialization` 模块及 `autocast`、`GradScaler`、
  `manual_seed`、`load`/`save` 等挂顶。L2553 注释提醒：改这些 import 要同步改
  `torch/__init__.py.in`（代码生成模板，见构建系统）。

### 阶段 7：扩展初始化 `_initExtension`（L2568-2621）

```python
_C._initExtension(_manager_path())  # L2584
```

这是 Python 侧与 C++ 侧的"握手"：把 `torch_shm_manager` 可执行文件路径
（`_manager_path`，L2574-2581）传给 C++，供 `torch.multiprocessing` 的共享内存
管理器使用；同时 C++ 侧完成 dispatcher 相关初始化（`memory_format` 等常量在
此后才可用，见 L2782 `contiguous_format` 的注释 "defined by _C._initExtension()"）。

随后 L2606-2621 第二个命名搬运循环：遍历 `_C._VariableFunctions`（ATen 生成的
out-of-place 算子表），把 `torch.add`、`torch.matmul`、`torch.rand` 等注入全局命名
空间并修 `__module__`。两个特殊处理：

- `PRIVATE_OPS = ("unique_dim",)`（L2604）——辅助算子不暴露；
- `segment_reduce` 被复制成公开 `_segment_reduce` 原名反而不进 `__all__`（L2613-2616，
  旗标特性窗口期的兼容处理）。

### 阶段 8：dtype 进 `__all__`、functional 覆写（L2623-2657）

- L2630-2635：`import torch`（自己！因为此时模块已基本成形），把所有
  `isinstance(getattr(torch, name), torch.dtype)` 的名字（`float32`、`int64`……）
  extend 进 `__all__`。
- L2642：先导 `torch._compile._disable_dynamo`（注释：必须在 functional 之前，
  避免循环依赖）。
- L2649-2650：`from torch.functional import *`——**Python 侧覆写 ATen 绑定**
  （注释 L2648："needs to be after the above ATen bindings so we can overwrite from
  Python side"）。即同名函数（如 `stack`/`chunk`）Python 实现覆盖 C++ 自动生成的版本，
  通常是补 docstring、参数校验或语义微调。
- L2656-2657：`del _StorageBase, del _LegacyStorage`——基类使命完成，从命名空间清除。

### 阶段 9：子模块总装（L2677-2739）

这是"torch.nn / torch.optim 在哪注册"的答案——**eager import，一次性挂载**：

```python
from torch.autograd import enable_grad, inference_mode, no_grad, set_grad_enabled  # L2686
from torch import (
    autograd, backends,
    # Device modules must be imported before other modules (e.g., multiprocessing)
    # that need to access their classes at import time.
    cpu, cuda, mps, mtia, xpu,          # L2700-2706：设备模块必须先行
    distributed, distributions, fft, foreach, futures, hub, jit, linalg,
    multiprocessing, nested, nn, optim, overrides, profiler, sparse,
    special, testing, types, utils, version,
)                                        # L2693-2727
import torch.nn.intrinsic / qat / quantizable / quantized  # L2736-2739
```

顺序即依赖：设备模块（cpu/cuda/mps/mtia/xpu）注释要求最先；量化家族（`ao`、
`nn.quant*`）注释要求最后（L2731-2735："nothing is expected to depend on them"）。
图谱中本文件对 `nn`/`optim`/`cuda`/`distributed`/`fx`/`export`/`profiler` 的
`imports` 边就是这一段。

之后收尾：`_C._init_names(list(_storage_classes))`（L2742，把 Storage 类登记给 C++）、
挂 docstring 后立即 `del _torch_docs` 等（L2745-2748）、`ops`/`classes` 命名空间用
`sys.modules.setdefault(f"{__name__}.ops", ops)` 注册（L2760-2764，让
`import torch.ops` 这种写法也能工作——ops 其实是 `_OpsNamespace` 对象不是真模块）、
c10d opaque type 注册（L2766-2770）、OpenMP 的 `register_after_fork`
（L2784-2789，fork 子进程重初始化线程数，gh-28389）、以及
`quantized_lstm = ops.aten.quantized_lstm` 一类**向后兼容别名**（L2796-2800）。

### 阶段 10：`torch.compile` 与编译栈挂载（L2817-3298）

- `_TorchCompileInductorWrapper` / `_TorchCompileAOTInductorWrapper` /
  `_TorchCompileWrapper`（L2820/2929/2970）：把 backend（"inductor" 字符串或 callable）
  统一包装成 `_dynamo.optimize` 可用的形式，且构造函数内才 import
  `torch._inductor`（L2829）——**把重编译器挡在 import 之外**。
- `compile()` 三个 overload（L3022-3071 两个签名 + 实现），支持
  `@torch.compile`（装饰器）与 `torch.compile(model)`（直接调用）两种形态，
  最终委托 `torch._dynamo.optimize(...)`（L3298 附近）。

### 阶段 11：export/func/高阶算子、sym_node 装配（L3321-3348）

```python
from torch import export, func, library, return_types   # L3321
from torch._higher_order_ops import cond, while_loop    # L3327
from torch.func import vmap                              # L3328
import torch.fx.experimental.sym_node                    # L3347 ★
```

L3347 是阶段 3 埋的伏笔的回收：这次 import 的副作用把真正的魔术方法实现安装到
`SymInt`/`SymFloat`/`SymBool` 的类型桩上。

### 阶段 12：lazy 模块与模块级 `__getattr__`（L3390-3422）★ 本文件最值得学的惯用法

```python
_lazy_modules = {"_dynamo", "_inductor", "_export", "onnx"}   # L3391-3397

def __getattr__(name: str) -> _Any:                    # L3399（模块级！PEP 562）
    replacement = _deprecated_attrs.get(name)          # has_cuda 等弃用属性 → 警告+转发
    if replacement is not None: ...                    # L3401-3409
    if name in _lazy_modules:
        return importlib.import_module(f".{name}", __name__)  # L3412-3413
    if name == "set_vital": ...                        # L3416-3420
    raise AttributeError(...)                          # L3422
```

要点澄清：**只有这 4 个编译器/ONNX 模块是 lazy 的**。`torch.nn`、`torch.optim` 等
都是 eager import（阶段 9）；lazy 的收益是 `import torch` 不必连带拉起整个
Dynamo/Inductor/ONNX 栈，首次访问 `torch._dynamo` 时才装载。`_deprecated_attrs`
（L3372-3377：`has_cuda`→`torch.backends.cuda.is_built()` 等）也借这个钩子做
warning + 转发。TYPE_CHECKING 分支（L3379-3388）则让 IDE 补全仍然可用——运行时
lazy、类型检查时 eager，两头兼顾。

### 阶段 13：设备模块注册与三方后端 autoload（L3301-3548）

- `_register_device_module`（L3301）：私有 API，out-of-tree 设备后端（如
  PrivateUse1 系）把自己的模块注册成 `torch.xxx` 属性 + `sys.modules` 条目。
- `get_device_module`（L3426，`@functools.cache`）：device → 模块（`torch.cuda` 等），
  device 为 None 时取当前 accelerator（`_C._accelerator_getAccelerator()`，L3437），
  无则回落 `cpu`。
- `_constrain_as_size`（L3451）：告诉 export "这个 int 可当作 size 用"（min/max 区间），
  是解决 unbacked SymInt 上 `GuardOnDataDependentSymNode` 报错的官方出口。
- `_import_device_backends`（L3478）：扫 `entry_points(group="torch.backends")` 并
  逐个 `load()()`——**Python 插件机制装载三方设备扩展**（RFC issue #122468），
  开关是环境变量 `TORCH_DEVICE_BACKEND_AUTOLOAD`（默认开，L3515）。
- 最后三步（L3540-3548）：`from torch import _logging` → `_logging._init_logs()`
  （解析 `TORCH_LOGS`，注释要求放在后端 autoload 之后，让后端能先注册日志名）→
  全文件最后一行 `import torch._native`（注册 `torch/_native` 里声明的
  custom/override ops）。

---

## 三、`import torch` 的完整数据流（一图流）

```
import torch
  │
  ├─ ① stdlib imports; __version__ ← torch/torch_version.py
  ├─ ② ROCm wheel init（若存在 _rocm_init）
  ├─ ③ Windows: 手动 LoadLibrary DLL 群 / Linux: _load_global_deps(RTLD_GLOBAL)
  │     └─ 失败 → _preload_cuda_deps 从 site-packages/nvidia/** 抢救
  ├─ ④ from torch._C import *          ← ★ libtorch_cpu/libtorch_cuda 的 Python 绑定进进程
  ├─ ⑤ 定义 SymInt/SymFloat/SymBool 类型桩 + sym_* 工具
  ├─ ⑥ dir(_C) 循环: __all__ 扩充 + __module__ 改写为 "torch"; TensorBase 剔除
  ├─ ⑦ 定义顶层工具（default device/dtype、deterministic、_check*…）
  ├─ ⑧ from torch._tensor import Tensor; 装配 legacy Storage 群
  ├─ ⑨ _C._initExtension(shm_manager_path) ← ★ Python↔C++ 握手
  │     └─ _VariableFunctions 循环: torch.add/matmul/rand… 上线
  ├─ ⑩ dtype 实例进 __all__; torch.functional import * 覆写
  ├─ ⑪ 子模块总装: cpu/cuda/… 先行 → nn/optim/autograd/jit… → ao/nn.quant* 殿后
  ├─ ⑫ _C._init_names; ops/classes 命名空间; c10d 注册; OpenMP atfork
  ├─ ⑬ compile 包装类（内部才 import _inductor）
  ├─ ⑭ export/func/cond/while_loop/vmap; sym_node 装配 Sym 魔术方法 ★
  ├─ ⑮ __getattr__ 挂钩（_dynamo/_inductor/_export/onnx 惰性 + 弃用属性）
  └─ ⑯ entry_points autoload 三方设备后端; _init_logs; import torch._native
        │
        ▼
  torch.Tensor / torch.add / torch.nn / torch.compile … 全部可用
```

---

## 四、外部连接（图谱证据）

| 方向 | 边 | 含义 |
|---|---|---|
| 出 | `imports → torch/_tensor.py` | Tensor 类本体（Python 门面层核心） |
| 出 | `imports → torch/nn/__init__.py` 等 10 个 | 阶段 9 的 eager 总装（nn/optim/cuda/distributed/fx/export/profiler/_ops/_tensor_str） |
| 出 | `depends_on → torch/_dynamo/__init__.py` | `torch.compile` 委托 Dynamo |
| 出 | `contains` 40 个函数/类 | SymInt 家族、default-device/dtype 管理、`_check*`、`compile` 等 |
| 出 | `exports` 25 个 | 进入 public API 的部分（`__all__` 的子集） |
| 入 | 272 个 `imports` + 35 个 `depends_on` | 全仓库事实上的依赖根：`torch/_dynamo/**`、`torch/distributed/tensor/_ops/**`、`torch/fx/experimental/symbolic_shapes.py` 等一切内部代码都 `import torch` |

---

## 五、值得吃透的惯用法（超出本文件也通用）

1. **PEP 562 模块级 `__getattr__`**（L3399）：模块也能"属性惰性求值"。配合
   `_lazy_modules` 白名单，把最重的编译器栈挡在冷启动之外；同时兼容弃用属性的
   warning 转发——一个钩子三种职责，但用白名单严格圈定边界。
2. **动态组装的 `__all__`**：种子列表（手写、强制排序、运行时断言 L158）+
   `dir(_C)` 扫描 + `_VariableFunctions` 扫描 + dtype 反射扫描 + 常量 extend。
   启示：跨 Python/C++ 边界的 public API 无法静态维护，只能"装配 + 反射收尾"。
3. **命名空间卫生**：临时变量用完即 `del`（`del __name, __obj` L1460/L2621、
   `del _manager_path` L2586、`del _torch_docs` L2748、`del _StorageBase` L2656）。
   顶层的全局变量就是用户的 `torch.xxx`，一个泄漏的循环变量就是一个意外的
   public API。
4. **`__module__` 改写**（L1447-1455）：把 C++ 对象的归属改写为 `"torch"`，让
   repr/pickle/文档系统看到统一门面。第三方扩展库常用同款技巧。
5. **类型桩 + 运行时装配**（L511 桩、L3347 装配）：桩方法统一
   `raise TypeError("type stub not overridden")`，真实现由 `sym_node` import 副作用
   注入。这是"给类型检查器一套精确 overload、给运行时另一套实现"的解耦模式。
6. **包装类延迟重型 import**（`_TorchCompileInductorWrapper` L2820 等）：不是用
   `__getattr__` 而是把 import 挪进构造器/方法体，粒度更细。
7. **顺序即契约**：满篇 `# usort: skip` 与顺序注释（设备模块先行 L2700、
   `_disable_dynamo` 先于 functional L2641、quantized 殿后 L2731、`_init_logs`
   在后端 autoload 后 L3543）。在循环依赖密集的代码库里，import 顺序是被测试
   锁定的接口。
8. **可诊断的失败**：L1419-1434 的 ImportError 给出精确修复命令；
   L353-356 用注释钉死 cublasLt/cublas 装载顺序的根因。动态库问题的排障信息
   直接写在装载代码旁。
9. **哨兵探测**：`from torch._C import _initExtension`（L1414）用一个必然存在的
   符号探测整个 C 扩展健康度，比 try/except 整个 import 更精准。
10. **sys.modules 手工登记**：L1478（pickle 修复）、L2763-2764（让 `torch.ops`
    可被 import）、L3318（设备模块注册）——当对象不是真模块却希望表现得像模块时，
    直接改 `sys.modules` 是标准姿势。

---

## 六、常见误区澄清

- **"torch.nn 是惰性加载的"** —— 否。`nn`/`optim`/`jit` 等在阶段 9 eager 导入；
  惰性的只有 `_dynamo`/`_inductor`/`_export`/`onnx` 四个（L3391）。
- **"算子直接定义在 `__init__.py`"** —— 否。`torch.add` 等来自
  `_C._VariableFunctions` 的循环搬运（L2607）；Python 侧同名覆写在
  `torch/functional.py`。
- **`__version__` 在哪** —— `torch/torch_version.py`（L66），构建系统生成。
- **为什么 `import torch` 慢** —— 主要耗时在阶段 3（CDLL 动态库装载）与阶段 9
  （数十个子模块的总装），而非 Python 代码本身；这也是社区持续做 lazy import
  优化的方向（本文件 L3390 的 `_lazy_modules` 是已落地的一部分）。

---

## 附：快速行号索引

| 行号 | 内容 |
|---|---|
| 82-159 | `__all__` 种子 + 排序断言 |
| 180-310 | Windows DLL 装载 |
| 313-388 | CUDA 依赖预载（cublasLt 先于 cublas） |
| 392-453 | `_load_global_deps`（RTLD_GLOBAL） |
| 456-495 | `from torch._C import *` 双路径 |
| 806/961/1070 | SymInt / SymFloat / SymBool |
| 1412-1435 | `_C` 哨兵检查 + 可诊断错误 |
| 1442-1460 | `dir(_C)` 命名搬运循环 |
| 2326 | `from torch._tensor import Tensor` |
| 2584 | `_C._initExtension(_manager_path())` |
| 2606-2621 | `_VariableFunctions` 算子搬运循环 |
| 2693-2727 | 子模块总装（nn/optim/…） |
| 3347 | `import torch.fx.experimental.sym_node`（装配 Sym 魔术方法） |
| 3399-3422 | 模块级 `__getattr__`（PEP 562 lazy） |
| 3478-3498 | 设备后端 entry_points autoload |
| 3548 | `import torch._native`（最后一行） |
