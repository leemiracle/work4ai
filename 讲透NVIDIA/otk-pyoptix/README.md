# 讲透 otk-pyoptix（OptiX Toolkit · PyOptiX 绑定）

上游：github.com/NVIDIA/otk-pyoptix · 本地克隆 /usr-data/data2/repos/agent-repos/NVIDIA/otk-pyoptix · HEAD `3144f224`（"Scikit migration (#9)"）。
定位：OptiX 7+ 光线追踪 C API 的 pybind11 Python 绑定（pyoptix 9.1.0）。核心三件：src/main.cpp 4162 行绑定、六示例一条管线骨架（ctx→module→PG→pipeline→SBT→launch）、预生成 PTX 测试体系。

## 全链状态表

| 阶段 | 产物 | 状态 |
|------|------|------|
| deepwiki | deepwiki/（7 章 19 页 + INDEX/_coverage-check/wiki_full） | ✅ 100%（19/19，2026-10-26） |
| understand 图谱 | 仓内 .understand-anything/knowledge-graph.json | ✅ 143 节点/165 边/6 层/8 步 tour，validator 0 issues，fingerprints 41 文件@3144f224（2026-11-10） |
| onboarding | onboarding/ONBOARDING.md | ✅ 7 节 / 非空白 6112 字符 / 严格锚 33 |
| explain | explain/ 3 篇 | ✅ 01 pybind11 绑定层 / 02 示例全管线六阶段 / 03 测试体系与 tutil（六节结构，锚 10+） |

## 源码级勘误与甄别（7 条，全部行号实证）

1. **`import optix` 语义补边**：示例/测试的 `import optix` 解析到 src layout 的 `src/optix/__init__.py`（`from ._optix import *`，__init__.py:25）——从源码仓直接跑示例需先 `pip install -e .` 或把 src 挂上 sys.path；wheel 里只有 `src/optix`（pyproject.toml:67），examples/test 都不随包分发。
2. **conftest 的 sys.path 注入有盲区**：conftest.py:8 只把 `test/util` 追加进 sys.path，注入发生在 pytest 收集期——直接 `python test/test_module.py` 必 ImportError；测试唯一合法入口是 pytest（testpaths=test，pyproject.toml:70-72）。
3. **path_util 硬编码家目录**：examples/path_util.py:4 `optix_include_path = "/home/kmorley/Code/support/optix/9.1.0/include/"` 是开发者个人路径，五个 NVRTC 示例全部 import 它（仓内唯一项目内 import 汇点）；克隆后不改此行，第一个示例的 NVRTC 编译即失败。
4. **双许可口径**：pyproject `license = "BSD-3-Clause"` 但 license-files 同时收 LICENSE.txt 与 OptiX_LICENSE.txt（pyproject.toml:14-15）——本仓 BSD-3 + 上游 OptiX SDK 许可并存，分发时两份都要带。
5. **FetchContent 自动拉 optix-dev v9.1.0**：构建不需要单独安装 OptiX SDK（CMakeLists.txt:28-33 浅克隆 NVIDIA/optix-dev tag v9.1.0，:37-38 包成 INTERFACE 目标）；代价是首次构建联网拉头文件，且 OptiX 代际与 pyproject 的 `version="9.1.0"`（pyproject.toml:10）手动联动——升级要同时改两处。
6. **版本号双轨**：pyproject `version="9.1.0"` vs `src/optix/__init__.py:20` `__version__="0.1.0"`——前者随 OptiX 代际、后者表绑定成熟度，报 bug/引依赖时先声明口径。
7. **denoiser API 真名是方法链**：图谱摘要写"denoiserSetup→denoiserInvoke"，实际绑定符号是 `denoiserCreate`（denoiser.py:248）→ `denoiser.setup`（denoiser.py:265）→ `invokeTiled`（denoiser.py:295）；引用 API 名以示例源码为准。

## 导读顺序

上游 README → 本仓 ONBOARDING.md → explain 01/02/03 → examples/hello.py + hello.cu 对照跑 → main.cpp:2318 起读绑定面。
