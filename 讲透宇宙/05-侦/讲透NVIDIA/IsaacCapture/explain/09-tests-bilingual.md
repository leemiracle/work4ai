# 09 · tests 双语测试领土：pytest×uv 与 Catch2×CTest 的镜像矩阵

## 一、角色定位

`tests/` 是 IsaacCapture（内部名 IsaacTeleop）唯一的双语言测试领土：278 个文件 = python 179 + cpp 97，双框架官方定调写在门牌上——"pytest + Catch2/CTest"（`tests/CMakeLists.txt:5`），整棵树由 `BUILD_TESTING` 门控（`tests/CMakeLists.txt:11`）。它是一套**镜像纪律**：目录按产品区复制 `src/` 与 `examples/` 的形状（`tests/AGENTS.md` 布局表），Python 叶与 C++ 叶一一对应——`tests/cpp/core/schema/` 与 `tests/python/core/schema/` 测同一批 FlatBuffers 类型的双语行为。CTest 是两岸唯一汇流点：pytest 经 `add_test` 包装、Catch2 经 `catch_discover_tests` 注册，CI 只认 `ctest` 一个入口。

## 二、内部结构

**Python 侧（tests/python，7 区）。** `ci/`（1）、`compat/`（5）、`core/`（cloudxr 15、deviceio_trackers 1、logging_config 7、retargeting_engine 45、schema 23、teleop_session_manager 8）、`examples/`（camera_viz 14 等 7 例）、`packaging/`（2）、`viz/`（5）。组织单元是叶目录，每叶三件套：测试文件 + 自己的 `pyproject.toml` + `CMakeLists.txt`。CMake 为每个 `test_*.py` 生成一个 CTest 条目，命令 `uv run --python ${ISAAC_TELEOP_PYTHON_VERSION} --extra dev pytest -v --tb=short`、`WORKING_DIRECTORY` 设为叶目录（`core/schema/CMakeLists.txt:23-31`）——"一文件一进程一 uv 环境"是硬约定（`tests/AGENTS.md:53`）。**没有根 conftest.py**：fixture 全下沉叶级，跨叶唯一共享是 17 行的 `repo_paths.py`，唯一函数 `repo_root()` 靠 VERSION+CMakeLists.txt 双标记向上探测（`repo_paths.py:11-14`），官方明令禁止硬编码 `parents[N]`（`tests/AGENTS.md:55`）——目录深度重构测试不断。

**C++ 侧（tests/cpp，3 区）。** core 八叶（schema 21 文件最大、mcap、deviceio_trackers、replay_deviceio_session、live_trackers、tracker_metadata、log_bridge、plugin_manager）、plugins 四叶、viz 六叶外加 `viz/support/` 两个**非可执行**共享 fixture 库。每可运行叶 = 一个 Catch2 可执行：源文件进 `add_executable`、链 `Catch2::Catch2WithMain` 免写 main、`catch_discover_tests` 注册（`core/schema/CMakeLists.txt:32`、`:51`）。viz 系叶多 `ADD_TAGS_AS_LABELS`：`[unit]/[gpu]/[xr]` 标签升格为 CTest label，`ctest -L unit` 过滤（`tests/cpp/viz/core/CMakeLists.txt:26-27`）。schema 测试是契约测试范本，编译期三板斧：FlatBuffer vtable 偏移按 `VT(field)=(field+2)*2` 锁字段 ID（`test_hand.cpp:23-24`）、`is_trivially_copyable` 锁内存布局、逐关节与 OpenXR 头做序数 parity（`test_hand.cpp:50-51` 断言 `HandJoint_NUM_JOINTS==XR_HAND_JOINT_COUNT_EXT`）。tracker_metadata 叶自带迷你夹具生态：`fbs/test_tracker_metadata.fbs:8` 单字段 schema、`trackers.toml`、假 ONNX runtime 头。

## 三、外部连接

一切入口通向 CI 的 `ctest --test-dir "${BUILD_DIR}" --output-on-failure --parallel`（`build-ubuntu.yml:184`），sanitizers job 再用 `-L unit` 按 Catch2 标签筛（`build-ubuntu.yml:775`）。Python 测试不装包：PYTHONPATH 指向构建树 `python_package/$<CONFIG>`，import 到的是刚编译的 pybind11 产物。packaging 测试把防线伸进交付物：`test_wheel_contents.py` 解包真实 wheel，断言顶层包恰为 `{isaaccapture, robotic_grounding}`（`:24-25` 定义 ALIAS/VENDORED），不走 ctest 时 `pytest.skip` 让步（`:31`）；`test_license_policy.py` 用 runpy 直接执行 `scripts/check_licenses.py`（`:14`）、构造临时 REUSE 项目，专测 egopost 子树 `LicenseRef-OpenMDW-1.1` 特殊许可与 sidecar 回退（`:27`）。**领土之外还有五种测试形态**（`tests/AGENTS.md` "Out of scope" 节）：examples 自带 tests、`src/core/codegen` unittest、oxr python 独立脚本、ROS2 docker 集成、`scripts/sbom/tests/`——SBOM 收集器测试自成 uv 项目（`:82`），CI 构建后驱动 `isaaccapture-sbom build/check`（`build-ubuntu.yml:307`）。

## 四、数据流

一次 ctest 的生命周期：configure 期 `file(GLOB)` 枚举叶内 `test_*.py` → 逐个 `add_test` → 运行期 CTest 拉起 `uv run pytest` 子进程（uv 按**叶级** pyproject 解析依赖，mujoco 钉版只进需要的叶）→ PYTHONPATH 注入构建树 → 测试体内经 `repo_paths.repo_root()` 定位源码资源 → 结果回传 CTest。Catch2 侧多一步运行期发现：`catch_discover_tests` 先跑一次可执行枚举 TEST_CASE 生成带标签条目。`compat/` 是最讲究的隔离样本：isaacteleop→isaaccapture 改名迁移测试，"一文件一 ctest = 每个测试拿全新解释器"（`compat/CMakeLists.txt:4`），因为 DeprecationWarning 进程级一次性、meta-path finder 是全局态——`test_deprecation_notice.py` 断言警告恰好一次且指向 import 行（`:13`）、消息含新版名与删除版本 "1.9"（`:28`）。`ci/test_docs_preview.py` 示范第三种数据流：importlib 动态装载 `.github/scripts/docs_preview.py`（`:13-14`），fake GitHub API 单测 CI 脚本本身。

## 五、设计决策

- **每文件一个 ctest**：代价是解释器启动 ×145，换进程级隔离最大化——sys.modules/警告过滤器污染不外溢；compat 的"警告恰好一次"断言只在 fresh interpreter 里非空洞。
- **每叶一个 pyproject、无根 conftest**：同一哲学。依赖按需下放（mujoco pin 不拖累 ROS2 叶），共享 fixture 视为隐性耦合，宁可复制小件（`retargeting_engine/conftest.py` 全是 5 行 fixture）也不造全局 conftest。
- **可执行名与前缀是 CI 契约**（`tests/AGENTS.md:33-36`）：`viz_*_tests` 被 CI glob 拿去打 GPU 包、`schema_*` 等前缀被脚本消费，改名即断 CI。
- **golden 路径烧进二进制**：schema 测试把 `.fbs`/golden 目录的绝对路径编译进宏（`core/schema/CMakeLists.txt:42`），产物只能在构建机跑，于是打 `ISAACTELEOP_NEEDS_SOURCE_TREE` 属性（`:48`）阻止进 wheel PATH——宁可不装，不装一个到别处必炸的二进制。
- **cloudxr 合成包技巧**（`core/cloudxr/conftest.py:36`、`:44`）：手工拼 `cloudxr_py_test_ns` 两层合成模块、`__path__` 指向源码树，未安装时带 sibling relative import 的模块也能加载与 patch。

## 六、新人提示

加测试按官方四步（`tests/AGENTS.md`）：选/建镜像叶 → 拷兄弟叶 CMakeLists → 父级同 `BUILD_*` 门接线 → 永不把测试 colocate 进 `src/`。写 schema 断言先记：生成的 `VT_*` 是 vtable 偏移**不是**字段 ID，对照公式 `(field_id+2)*2`（`tests/AGENTS.md:73`）。动 import 路径后跑 `ruff format`；`pytest.raises(match=...)` 一律 raw string。spawn 替身子进程时 `python -m <builtin>` 立即退出不算存活，`Popen()` 后立刻读 `/proc/<pid>/cmdline` 可能为空、必须轮询（官方点名 `test_background.py`）。覆盖矩阵看叶厚度：retargeting_engine 45 文件是 Python 重镇、schema 21 是 C++ 重镇，两边都薄的（deviceio_trackers）即新产品落地处。

## 源码实证勘误

任务书三处口径修正：① **C++ 框架是 Catch2 不是 gtest**——17 个 CMakeLists 全链 `Catch2::Catch2WithMain`、`catch_discover_tests` 15 处、grep gtest 零命中；② "SBOM 测试在 tests/"半对——packaging 确在 `tests/python/packaging/`，SBOM 测试物理住 `scripts/sbom/tests/`（`tests/AGENTS.md:82`），由 build-ubuntu.yml 驱动；③ 179/97 是全文件口径（`.py` 实数 145、cpp 源文件实数 70）。另：`ci/` 唯一测试用 `unittest.TestCase` 写就、由 pytest 执行。

---
chars(不含空格)=4744 anchors=20 勘误=4
