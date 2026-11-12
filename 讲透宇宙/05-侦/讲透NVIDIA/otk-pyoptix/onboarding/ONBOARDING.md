# otk-pyoptix Onboarding（OptiX Toolkit 的 Python 绑定）

> 基座：知识图谱 143 节点/165 边/6 层/8 步 tour，commit `3144f224`（git log 实证 "Scikit migration (#9)"，2026-11-10 分析）。
> 源码仓：/usr-data/data2/repos/agent-repos/NVIDIA/otk-pyoptix。所有 `路径:行号` 锚均经源码核实。

## 1. 这个仓是什么（30 秒版）

NVIDIA OptiX Toolkit 家族的 **pyoptix**：把 OptiX 7+ 光线追踪 C API 暴露给 Python 的 pybind11 绑定。整体极小——运行时代码只有一份 `src/main.cpp`（4162 行）编译成 `_optix` 扩展 + 28 行的包入口 `src/optix/__init__.py`，其余全是示例、设备侧着色器与测试。能力面（`__init__.py` 文档串，src/optix/__init__.py:6-14）：DeviceContext/Module/ProgramGroup/Pipeline/Denoiser 句柄五件套、加速结构构建、SBT 打包、launch、AI 降噪。要求 OptiX SDK 7.6+/CUDA 10.0+/RTX GPU。wheel 版本号 9.1.0（pyproject.toml:10），与 FetchContent 拉取的 optix-dev 头文件代际（v9.1.0）联动。

## 2. 构建链：scikit-build-core + FetchContent，免装 SDK

三份文件构成从源码到 wheel 的完整链路：

- `pyproject.toml`：build-system 用 scikit-build-core>=0.12 + pybind11>=2.13.0（pyproject.toml:2-6）；`dependencies = []`（pyproject.toml:36）——wheel 运行时零 Python 依赖，cupy/numpy/Pillow 只进 `dependency-groups` 的 examples 组（pyproject.toml:44-59），test 组仅 pytest；`[tool.scikit-build]` 段 wheel.packages 只装 `src/optix`（pyproject.toml:67），`sdist.exclude = [".claude"]`（pyproject.toml:68）把开发者本地 agent 目录挡在源码包外；pytest 配置 testpaths=test（pyproject.toml:70-72）。
- `CMakeLists.txt`：**不需要单独安装 OptiX SDK**——FetchContent 浅克隆 `NVIDIA/optix-dev` tag v9.1.0（CMakeLists.txt:28-33），包成 `OptiX::OptiX` INTERFACE 目标（CMakeLists.txt:37-38）；CUDAToolkit 最低 10.0（CMakeLists.txt:44）；`python_add_library(_optix MODULE src/main.cpp WITH_SOABI)`（CMakeLists.txt:51）产出扩展，链接 cuda_driver/cudart/pybind11 头（CMakeLists.txt:53-58），C++17（CMakeLists.txt:60）。
- 双许可：project 声明 BSD-3-Clause 且 license-files 同时收 LICENSE.txt 与 OptiX_LICENSE.txt（pyproject.toml:14-15）——本仓 BSD + 上游 OptiX 许可并存。

## 3. 绑定核心：main.cpp 的三类语法糖

`src/main.cpp`（4162 行）是全仓心脏，PYBIND11_MODULE 入口在 main.cpp:2318。经 grep 实证的成分：

- **26 个包装 struct**（main.cpp:105-961）：句柄五件套 DeviceContext（main.cpp:105）/Module（:112）/ProgramGroup（:119）/Pipeline（:126）/Denoiser（:132），四种 BuildInput（Triangle :170/Curve :225/CustomPrimitive :275/Instance :314），变换族 StaticTransform（:423）/MatrixMotionTransform（:468）/SRTData（:516），选项描述符族 MotionOptions（:385）/PipelineCompileOptions（:558）/PipelineLinkOptions（:594）/ShaderBindingTable（:612）/PayloadType（:743）/ModuleCompileOptions（:774）/ProgramGroupDesc（:864）等。BuildInput 族带 setXxx/sync 方法在绑定层对齐 C API 的 union 布局；句柄 struct 全带 operator==。
- **两个 `convertBuildInputs` 重载**（main.cpp:95 与 :1001），在 accelBuild 调用点（:1625/:1661）前把 Python 对象列表转成 C 数组——这是 Python 列表语义到 OptiX 数组参数的边界翻译层。
- **9 个自由函数 m.def**（main.cpp:2339-2347：version/deviceContextCreate/getErrorName/getErrorString/launch/sbtRecordPackHeader/sbtRecordGetHeader/convertPointerToTraversableHandle/getDeviceRepresentation）+ 41 处 class_ 方法绑定 + 31 个 `py::enum_`（OptixResult 到 ProgramGroupFlags）。

`src/optix/__init__.py` 是唯一 Python 桥：`from ._optix import *`（__init__.py:25）后用 `__all__ = [name for name in dir() if not name.startswith('_')]` 动态再导出（__init__.py:28）。注意 `__version__ = "0.1.0"`（__init__.py:20）与 pyproject 的 9.1.0 并存（见坑 1）。

## 4. 设备侧：vec_math.h 教学数学库 + 五对着色器

`examples/vec_math.h`（2626 行）是自包含设备侧向量库：float2/3/4、int/uint/longlong 全家族 make/clamp/lerp/dot/normalize/reflect 与全套运算符重载，**不依赖 CUDA 头文件**（教学式实现）；`cross` 只有 float3 族一份（vec_math.h:541-542）。五对 .cu/.h：hello（渐变背景 raygen）、triangle/sphere（求交入门）、curves（OptiX 内置曲线相交类型）、simpleMotionBlur（运动模糊）。这些 .cu 一律由 Python 侧 NVRTC 在线编译（或测试里直接喂 PTX），不存在独立设备侧构建物。

## 5. 示例族：六示例一条管线骨架

六个 .py 示例（加 path_util.py 共七个驱动文件）全部复用同一骨架——**ctx→module→PG→pipeline→SBT→launch 六阶段**：

- `hello.py`（393 行）最短完整走查：compile_cuda NVRTC 编译（hello.py:97）→ create_ctx 里 `optix.deviceContextCreate`（hello.py:153）→ create_module（:168）→ create_program_groups（:210）→ `pipelineCreate`（:249）→ create_sbt（:280）→ `optix.launch`（:347），main 在 :371 串全流程并计时。
- 几何示例换求交不换骨架：triangle.py:160 与 sphere.py:177 的 `create_accel`（sphere 走 AABB+内置 SPHERE 相交类型）；curves.py:207 用 `BuildInputCurveArray`（:219 accelComputeMemoryUsage、:224 accelBuild、SBT 在 :367）；simpleMotionBlur.py:213 `build_triangle_gas` 配 `MotionOptions`（numKeys/timeBegin/timeEnd，simpleMotionBlur.py:217-221），:304 `build_sphere_gas` 走 custom primitive，:366 `create_sphere_xform` 用 MatrixMotionTransform 双关键帧（:368-379）——顶层 IAS 挂两个 GAS 的层级加速结构演示。
- `denoiser.py`（334 行）：OpenEXR/Imath 读 EXR、cupy 管 GPU 内存（denoiser.py:8-13）；`create_optix_image_2D`（:66）把 numpy 图包成 OptixImage2D；Denoiser 全链 `denoiserCreate(DENOISER_MODEL_KIND_HDR)`（:248）→ computeMemoryResources（:250）→ `denoiser.setup`（:265）→ computeIntensity（:287）→ **`invokeTiled`**（:295）。固定输入是 examples/data/ 六张 EXR（beauty/albedo + diffuse/glossy/specular/normal）。

`examples/path_util.py` 只有 8 行：`optix_include_path = "/home/kmorley/Code/support/optix/9.1.0/include/"`（path_util.py:4）是**开发者个人家目录硬编码**，克隆后必改第一处（:7 的 CUDA 路径一般无需动）。

## 6. 测试体系：预生成 PTX 免工具链回归

`test/` 四件套 + util：`conftest.py` 只做一件事——`sys.path.append(os.path.join(os.path.dirname(__file__), 'util'))`（conftest.py:8），让四个测试文件裸名 `import tutil`。`test/util/tutil.py`（426 行）主体是多段**预生成 PTX 字符串常量**：`ptx_string_old` 带 `.version 7.1` 老格式（tutil.py:10/:19），新版带 `.visible` 限定符（:26 起 `__raygen__hello` 等 entry）——测试因此不依赖本机 CUDA/NVRTC；尾部工具 Logger 回调类（:382）、`create_default_ctx`（:395）、`optix_version_gte`（:402）、`default_debug_level`（:410，按 7.1+ 分支选 COMPILE_DEBUG_LEVEL）、`create_default_module`（:418 一步建 (ctx, module)）。`test/sample_ptx.py`（620 行）是另一批 PTX 夹具：`hello_ptx`（sample_ptx.py:6）与 `triangle_ptx`（sample_ptx.py:278）两大段字符串常量。四个测试文件分工：test_context.py 验句柄（:26 test_default_ctor）、test_module.py 验编译（:122 test_create_destroy、:146 payload_semantics、:209 builtin_is_module_get）、test_program_group.py 最全（:57 raygen/:75 miss/:94 callables/:115 hitgroup/:152 stack size）、test_pipeline.py 验管线（:18）。

## 7. 上手路线与坑

**路线**（8 步 tour 浓缩）：①README+pyproject+CMakeLists 建构建心智 → ②main.cpp:2318 起 PYBIND11_MODULE 读绑定面 → ③hello.py+hello.cu 跑通最小管线 → ④vec_math.h 看设备数学 → ⑤四几何示例对比求交差异 → ⑥denoiser.py + 六 EXR 走 AI 降噪 → ⑦tutil PTX 夹具理解回归防线 → ⑧回看六层结构（门面/绑定/设备侧/驱动/数据/测试）。

**坑（源码实证）**：
1. **版本号双轨**：pyproject `version = "9.1.0"`（pyproject.toml:10，随 OptiX 代际走）vs `__init__.py:20` `__version__ = "0.1.0"`（绑定自身成熟度）——报告 bug 时先说清指的是哪个。
2. **import optix 的语义补边**：示例/测试里 `import optix` 解析到的是 `src/optix/__init__.py`（src layout），从源码跑示例需先 `pip install -e .` 或把 src 挂进 sys.path；path_util.py:4 的家目录硬编码不改，NVRTC 编译第一个示例就报头文件找不到。
3. **conftest 的 sys.path 注入只对 pytest 生效**：直接 `python test/test_module.py` 运行会 ImportError——测试入口必须走 pytest（pyproject.toml:70-72 testpaths）。
4. **denoiser API 命名是方法链不是自由函数**：绑定层实际暴露 `denoiserCreate`/`setup`/`invokeTiled`（denoiser.py:248/:265/:295），图谱摘要里"denoiserSetup→denoiserInvoke"的写法与真实符号不符。
5. **sdist 干净但开发目录有 .claude**：pyproject.toml:68 显式排除；同时 examples/data 的 8.7MB EXR 是仓内二进制载荷，浅克隆也要全量拉。
