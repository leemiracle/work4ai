# 08 · Python 打包四 wheel 线：占位符模板与 PEP 517 后端

> 图谱锚：L10「Python wheel 打包与 tensorrt.plugin 包」（36 节点）。源码根 `python/packaging/`（五子目录）+ `python/scripts/process_wheel_template.py`。

## 一、角色定位

pip 上的 TensorRT 是一族 wheel：`tensorrt_cu12`（frontend 元包）依赖 `tensorrt_cu12_bindings` 与 `tensorrt_cu12_libs`，另有 frontend_sdist 与 metapackage。本域是生产这族 wheel 的流水线：**同一套模板 + 构建期占位符替换 + 自研 PEP 517 后端**。它解释一个反直觉事实——仓里的 `tensorrt/__init__.py` 不是合法 Python（含 `##TENSORRT_MODULE##`，import 必 SyntaxError），它是模板而非源码（NOTES batch-99 钉版）。

## 二、内部结构

**五目录分工**：`bindings_wheel/`（绑定 wheel 模板 + 可选 `tensorrt/plugin/` 九文件组）、`libs_wheel/`（纯库 wheel）、`frontend_sdist/`（前端源码包，`frontend_sdist/tensorrt/__init__.py:18` 的 `from ##TENSORRT_MODULE##_bindings import *` 把真身转指绑定 wheel）、`metapackage/`、`tensorrt_build_backend/`（共享构建后端）。

**占位符全表**（消费端 `bindings_wheel/tensorrt/__init__.py`）：`##TENSORRT_MODULE##` 在 `__init__.py:26`（import libs）、`__init__.py:84`（LIBRARIES 字典键选择）、`__init__.py:96`（`from .##TENSORRT_MODULE## import *`——真正拉起 pybind 模块的一行）、`__init__.py:135`（条件补丁）；`##TENSORRT_NVINFER_NAME##` 在 `__init__.py:33` 决定 RTX 变体库名后缀；`##TENSORRT_PYTHON_VERSION##` 落 `__init__.py:98`。替换引擎 `python/scripts/process_wheel_template.py`：以 `--trt-module/--trt-nvinfer-name/--plugin-disabled` 等实参（process_wheel_template.py:74-83）驱动一连串 `contents.replace()`。CMake 入口 `python/packaging/CMakeLists.txt:17` `processWheelTemplates()` 把 `tensorrt/` 前缀改写为 `${moduleName}/`（packaging/CMakeLists.txt:32-33——模板目录与产物包名解耦的关键），`bindings_wheel/CMakeLists.txt:31` `buildBindingsWheel()` 决定顶层是否加 `_bindings` 后缀。

**PEP 517 后端** `tensorrt_build_backend/__init__.py`：后端 __init__.py:21 明言 "PEP 517 compliant build backend that wraps setuptools"。核心钩子 `build_wheel`（backend __init__.py:180）三步：取 `wheel-type` 配置（backend __init__.py:140-148，四值 binding/binding_standalone/libs/frontend）→ `_compute_package_names`（backend __init__.py:95-122）算分发名/导入名 → `_update_pyproject_for_build`（backend __init__.py:151-177）**就地改写 pyproject.toml**（backend __init__.py:166-169 换实名）再委托 setuptools（backend __init__.py:58-64、backend __init__.py:229），产物先落临时目录再 `shutil.move`（backend __init__.py:244）防并行冲突；`--python-tag/--plat-name` 经 `--build-option` 透传（backend __init__.py:214-224）。

## 三、外部连接

上游是第 7 篇 pybind 产物——`bindings_wheel/CMakeLists.txt` 把 `tensorrt.so`（Linux）或 `.pyd`（MSVC，注释原话 "yet another naming convention™"）拷进展开目录。下游：frontend wheel 被 Polygraphy `mod/trt_importer.py` 与用户脚本 import；plugin 包九文件仅在 `TRT_BUILD_PLUGINS` 开启时并入 wheel（bindings_wheel/CMakeLists.txt:46-56）。

## 四、数据流

standalone 绑定 wheel 构建：CMake `processWheelTemplates` 逐文件展开占位符 → `copyTRTBuildBackend` 宏拷后端到生成目录 → build 前端以 `--config-setting=wheel-type=binding_standalone` 调后端 → 后端改写 pyproject → setuptools 打包 → wheel 产出。安装期在 `bindings_wheel/tensorrt/__init__.py`：`__init__.py:24-30` 先试 `import tensorrt_libs`；失败且 Windows 则进手动 DLL 加载——`find_lib`（`__init__.py:40`）沿 PATH + 相邻 libs 目录（`__init__.py:45`）搜 DLL，按 `__init__.py:65-84` 的 LIBRARIES 表**依赖序**逐个 `ctypes.CDLL`（tensorrt→plugin→onnxparser→builder_resource），`__init__.py:64` 注释明言 "Order matters here because of dependencies"；最后 `__init__.py:96` 才 import pybind 真身。

## 五、设计决策

1. **模板占位符而非 configure_file**：Python 源码需保持运行期语义完整（IDE/类型检查可用），独立替换脚本让规则集中可测试。
2. **构建期改写 pyproject.toml**（backend __init__.py:151-177）是 PEP 517 下"动态包名"的务实 hack——正规动态元数据表达不了四形态命名矩阵；代价是构建目录不可重入（需重新展开模板恢复 placeholder）。
3. **多形态单源**：四模块共享一份模板，差异全由占位符吸收——与第 7 篇 `py::module_local` 互为表里（另一半在打包层：不同 wheel 不同 import 名）。
4. **Windows DLL 预载顺序敏感**：nvinfer 依赖 plugin/builder_resource 的导出符号，CDLL 顺序错即加载失败。
5. **Python 层补丁收敛废弃面**：`__init__.py:102-116` 把 context manager 统一替换为 DeprecationWarning 空操作。

## 六、给新人的提示

改 `tensorrt/__init__.py` 前先确认改的是模板还是展开产物——grep 到的 `##...##` 都是待替换标记，永远不要"修复"它们。排查"装了却 import 失败"按 `__init__.py:24` → `__init__.py:36` → `__init__.py:96` 三段定位。版本升级要同步 process_wheel_template.py 实参与 CMake 版本源。报 issue 先贴 `pip show tensorrt-cu12-bindings` 完整版本号——同一 commit 按 CUDA/RTX 矩阵可出多套 wheel。
