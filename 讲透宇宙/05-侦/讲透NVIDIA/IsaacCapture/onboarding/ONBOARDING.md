# NVIDIA IsaacCapture ONBOARDING.md

> 基于 understand-anything 图谱（6542n/11416e/16 层/16 步）+ 源码锚逐一核实撰写。

## 1. 仓库定位与全景

**Isaac Capture** 是 NVIDIA Isaac 生态的数据采集基础设施：为遥操作与自我中心数据采集提供共享的设备插件、retargeter（重定向器）与数据工具（`README.md:28`）。两大组件：**Isaac Teleop**——机器人在环遥操作（Teleop Session/Remote Assist），场景含 XR 头显夹爪/三指手、XR+手套灵巧手、Homie 坐姿全身、SONIC 全身控制；原为独立产品现并入 Isaac Capture（`AGENTS.md:29`），品牌保留——仓内双名并存（CMake 工程名 `IsaacTeleop`，`CMakeLists.txt:39`；wheel 依赖 `isaacteleop>=1!1.6.dev0`，`pyproject.toml:34`）。**Ego Pipeline**——无机器人在环的 egocentric 采集+后处理；egopost 是论文级资产：EgoHand 单目 3D 手部重建（arXiv 2610.30293，`src/python/isaaccapture_egopost/README.md:16`），DINOv3 以 git pin 引入（`requirements-dinov3.txt:7`）。

**给谁用**：遥操作开发者（XR/手套/主从臂录 demonstration）、具身数据团队（CTS 把"采到了"变成"采合格了"）、硬件集成者（写新插件）。**生态位置**：Isaac Lab 3.0.0 EA 组成部分；CloudXR 串流、MCAP/SOMA 对接训练侧。**技术形态**：C++（core/plugins/viz）+Python 双栈；FlatBuffers 公共契约，codegen 从 TOML 生成骨架；硬件插件是**独立进程**（plugin.yaml+子进程管理）而非 dlopen；**agent-first 仓**（见第 5 节）。

## 2. 架构总览与数据流

```
schema/fbs(31 契约) ─flatc→ C++/pybind；─codegen(trackers.toml)→ tracker 七文件束(仅构建树)
C++ core(base/session/oxr/pusherio/plugin_manager/mcap)
  ├pybind11→ Python isaaccapture(schema/retargeting_engine/teleop_session_manager/cts)
  └插件子进程(src/plugins/*): SDK→SchemaPusher→session
出口: viz(Vulkan+MuJoCo) / cts / MCAP / egopost
```

数据流：**schema→设备进程推送→会话聚合→Python 重定向计算图→机器人/可视化/录制**。

1. **契约层**：31 个 `.fbs`。C++ 入口 `serialized.hpp:1`；Python `schema/__init__.py:9`——table 是编码字节**只读视图**，关节零拷贝 NumPy view，构造即编码。
2. **设备层**：插件是独立进程（`src/plugins/gamepad/plugin.yaml:4`）。`PluginManager`（`plugin_manager.hpp:54`）扫描 plugin.yaml（`plugin_manager.cpp:124`），`start()` 返回 RAII `Plugin`（`plugin.hpp:74`）——SIGINT→2 秒（`:23`）→SIGKILL；`SchemaPusher`（`schema_pusher.hpp:88`）推数据进 OpenXR；崩溃隔离 `PluginCrashException`（`plugin.hpp:66`）+`ProcessSnapshot`（`:114`）。
3. **会话层**：`DeviceIOSession`（`deviceio_session.hpp:63`）实现 ITrackerSession，工厂 `run()`（`:74`）绑 trackers+OpenXR+`McapRecordingConfig`（`:38`）+`VendorConfig`（`:54`，切原生 XR/插件推送 vendor）；每帧 `update()`（`:92`）驱动 tracker，录制写 MCAP。
4. **追踪三轨**：deviceio（注册表 `trackers.toml:4`）/live（`live_deviceio_factory.hpp`）/replay。采集/回放对称：录一遍 MCAP 同一套下游回放。
5. **Python 计算层**：retargeting_engine 是数学核心（tensor_types 92 扇入全仓第一）；`BaseRetargeter`（`base_retargeter.py:40`）声明输入/输出 spec+`_compute_fn`；`deviceio_source_nodes/` 21 种源/汇节点。
6. **编排出口**：`TeleopSession`（`teleop_session.py:108`）+`TeleopSessionConfig`（`config.py:349`）；出口四路 viz/cts/MCAP/egopost。

**关键设计决策**：改 `.fbs` 会让旧录制不可读（MCAP 内嵌 schema+golden+回放校验）；schema-based tracker 源码只在构建树（`src/core/AGENTS.md` 钉版）；`OpenXRSession` 默认无限等头显且持 GIL，无头测试须自设超时；单一日志树（六环境变量契约 `AGENTS.md:152`，禁 basicConfig `AGENTS.md:112`）。

## 3. 环境搭建与构建

**路径 A pip（用户）**：`uv venv --python 3.11 --seed .venv` 后 `uv pip install 'isaaccapture[cloudxr,retargeters]~=1.0'`（`docs/source/teleop/quick_start.rst:53`）；1.6 起从 `isaacteleop` 改名（`:38`）。可选组（`pyproject.toml:42`）：cloudxr/retargeters（pin>=4.1 pinocchio、dex-retargeting、torch、nlopt）/grounding/wuji/ui。

**路径 B 源码（开发者）**：`pyproject.toml:6` 声明 `scikit-build-core>=1.0`——`pip install .` 驱动**同一 CMakeLists**，与 `cmake -B build` 共存。Python 版本单一事实源 `ISAAC_TELEOP_PYTHON_VERSION`（默认 3.11，`CMakeLists.txt:51`），SetupPython 经 uv 先行配置（`:59`）。

CMake 选项（`CMakeLists.txt:66` 起）：PLUGINS/PYTHON_BINDINGS/EXAMPLES/TESTING 默认 ON；`BUILD_VIZ` 自动（Vulkan+CUDA 探测，`:82`）；OAK（`:35`）/Noitom/OGLO/Wuji/Sharpa 默认 OFF（需厂商 SDK 缺则跳过）；Windows FATAL_ERROR（`:115`）；前缀默认 `install/`（`:22`）；Linux clang-format（`:111`，CI 用 -14）。

**版本与合规**：`VERSION` 为根（`CMakeLists.txt:16`）；REUSE.toml+LICENSES（Apache-2.0 默认，egopost OpenMDW-1.1）+`scripts/sbom/` 自研 SBOM 收集器——wheel 内嵌 SBOM 从构建推导（`AGENTS.md:284`）；CloudXR 脚本起环境。

## 4. 核心子系统导览（16 层）

- **L01 门面/CI/脚本（89f）**：根文件+`.github/workflows` 五族+`cmake/`+`scripts/`；重量级 `scripts/sbom/`（discovery.py 2390 行溯源/licensing.py 1351 行 SPDX/wheelfile.py 证据打回 wheel）。
- **L02 schema+codegen（141f）**：31 fbs+schema_compat+`generate_trackers.py`；`_render_tracker_set`（`generate_trackers.py:47`）每条目生成**七文件束**，pull/push 两族（`:74`）；生成物只在构建树。
- **L03 设备 IO 基座（54f）**：tracker 三层（`tracker.hpp:16` ITrackerImpl→`:50` ITrackerSession→`:60` ITracker）；deviceio_session/pusherio/core-python pybind/log_bridge（`logger.hpp` 单例）。
- **L04 追踪三轨（74f）**：`trackers.toml:4` 注册表 16 条目（`haptic_command` 唯一 push `:78`）；`keyboard_tracker.hpp`（205 行）协议范本：W3C+evdev 双码制+事件状态机。
- **L05 core 杂项（37f）**：`oxr_session.hpp:23` OpenXRProviderState；`tracker_channels.hpp:49` 通道写模板+`:33` mcap_topic；plugin_manager；src/compat。
- **L06 插件 I 手部/触觉（71f）**：manus（26 方法手套接口）/wuji_glove（635 行连接线程+坐标基重映射）/oglo_tactile（BLE client+parser）/haptikos/controller_synthetic_hands（**无硬件合成手**，测试神器）/sensing/plugin_utils。
- **L07 插件 II 动捕/全身（47f）**：xsens_full_body（438 行 UDP+会话恢复+错误注入钩子）/sharpa_avatar（734 行地标→OpenXR 关节映射）/noitom/双 se3_tracker。
- **L08 插件 III 主从臂/驾驶（68f）**：rebot_devarm_leader（636 行 RobStride 双读+标定）/so101_leader（lerobot 标定/homing/滑窗去噪）/spacemouse（hidraw）/gamepad（SDL3）/steering_wheel/pedal/oak。
- **L09 cts 采集管线（108f）**：CTS=**Conformance Test Suite**（`docs/source/conformance/overview.rst:9`——录规定脚本 take，checker 只读录制给判决，作为 PR 证据）；`frames.py:12` Frame 协议、`checks/base.py:43` Check 基类；hand 三件套 capture（Take 状态机）/checker（`profile.py` 26 关节**仅 21 受判**）/oracle。
- **L10 retargeting 引擎（79f）**：扇入霸主（tensor_types 92/interface 81/core_types 79）；`base_retargeter.py:40`（434 行）；`deviceio_tensor_types.py` 18 种 Tracked（`:81`）；retargeters 大桶 dex_hand/se3/gamepad/locomotion/vehicle/tactile+G1/SO101+ee_pose_jump_guard。
- **L11 teleop/门面/cloudxr（79f）**：包根 `__init__` 是 C++ 的 Python 门面（schema 73/deviceio 47/deviceio_trackers 31/oxr 27）；teleop_session_manager 编排（状态机+异步 runner+twin_runner）；cloudxr 两包。
- **L12 egopost（109f）**：inference/（`camera_models.py` 855 行含鱼眼 rational；run_hand_detector.py 435 行 DINOv3 CLI）/egohand/（`cam_utils.py` 338 行）/keypoint_2_soma_converter（`geometry.py` 鲁棒对齐）；测试注入 stub 无 GPU 全跑。
- **L13 viz（91f）**：自研 Vulkan 引擎 Televiz；session（`viz_session.hpp:29` 生命周期状态机，XR 加 kStopping/kLost；display_backend 统一窗口/XR/离屏）；robot_twin（**MuJoCo 数字孪生** mj_api.hpp，全 private header 合规则 6）。
- **L14 examples（286f/22 目录）**：teleop（14 个 retargeting 脚本+`_example_loop.py`，零 ROS）/teleop_ros2（ROS2 参考）/camera_viz/mcap_record_replay（`common.py` 568 行）/rebot/vehicle_teleop/soma/native_openxr/lerobot 等。
- **L15 tests（278f）**：见第 7 节。
- **L16 docs/deps/许可证（246f）**：docs/source Sphinx 九族；deps/（cloudxr SDK 111f）；LICENSES。

## 5. agent-first 专节

### .claude/skills/cmake-structure——教 agent 摆文件

frontmatter（`.claude/skills/cmake-structure/SKILL.md:2`）触发面：凡 edit CMakeLists.txt、增删 target、设 include/link、定头 private/public、写/重排 `#include`、重构 src//deps/ 必触发。正文薄壳指向单一事实源 `cmake/cmake-structure.md`（148 行）**六条不可协商规则**（`:20`）：①每叶子目录一 target；②禁 `../`；③自己的头用 `"..."` 相对引用；④`<...>` 只给 std 与外部模块；⑤公共头带模块前缀（INTERFACE 只暴露父目录）；⑥inc/ 只放导出头，可执行/插件叶子**没有 inc/**。配套推荐结构（`:66`）+13 条 checklist（`:125`）。

### .claude/skills/rebot-orin-setup——硬件 bring-up 蒸馏成配方

frontmatter（`.claude/skills/rebot-orin-setup/SKILL.md:2`）：初始化 reBot B601-RS（RobStride 六自由度七电机）臂，用 Jetson AGX Orin **片上 CAN（mttcan）**+SN65HVD230——不用 USB-CAN 适配器；覆盖 uv/motorbridge、can0@1Mbit、总线验证、持久化、电机 ID、零点标定、排障树。真身 `examples/rebot/SKILL.md`（196 行）：仅 B601-RS 实测（`:23`）；接线（`:56`）pin31→TX/pin29→RX/**3.3V 非 5V** pin17，~60Ω 终端电阻；**排障金律**（`:175`）——电机没电⇒CAN 无应答，先查电源再查软件；pinmux 重启清零（脚本+systemd 持久化）；六步（uv sync→can0→验证（loopback 只证驱动不证接线）→systemd→电机 ID（扫描 ~2 分钟静默不是挂）→零点标定（gateway 独占总线））；排障表（`:173`）：MUX UNCLAIMED 是红鲱鱼（读 0x0c303010 应为 0xc400）。

### 与普通仓库的差异

同一 `cmake/cmake-structure.md` 被 .claude/skills、`.cursor/rules/`、`.github/instructions/`、`.coderabbit.yaml` 四工具位点引用，薄壳规则只写一遍（`:17`）。AGENTS.md 强制预检（`AGENTS.md:9`）：改文件前读路径**每一级** AGENTS.md。强制学习回路（`AGENTS.md:322`）：纠偏/CI 失败/重复错误当场写进最近 AGENTS.md；AI 起草 commit 必须 DCO 签名（`AGENTS.md:220`）。rebot skill 本质是把两天硬件排障固化为 agent 可执行的程序性知识——普通仓库 docs 罕有此密度。

## 6. 硬件接入路线

以最干净的 **spacemouse** 插件为范式，七步：

**① 定义 schema**：`src/core/schema/fbs/<device>.fbs`，参照 `spacemouse.fbs:16` 三纪律：显式 field id；数据表+Record 包装（`:29`）；语义中立（`:9`——轴义归消费端，轴值归一 [-1,1]）。高危：改既有 fbs 旧录制不可读。

**② 注册 tracker**：`trackers.toml` 加 `[[tracker]]`；configure 期生成七文件束+工厂注册+pybind 导出——**三轨+绑定一次全出**。`max_flatbuffer_size` 后期调大破坏配对生产者（`trackers.toml:12` 注释教训）。

**③ 写插件进程**：spacemouse 范式 core/（hid_report+discovery+connection）与 app/ 分层；`kMaxFlatbufferSize=256` **必须匹配 trackers.toml**（`spacemouse_plugin.cpp:26`）；`required_extensions()` 从 SchemaPusher 起底（`:28`）——**插件自己就是 OpenXR 应用**，经 SchemaPusher 推数据。

**④ plugin.yaml**（`src/plugins/spacemouse/plugin.yaml:4`）：name/description/command/version/devices。**进 wheel 的插件**须 bundle 进 `isaaccapture/plugins/<name>/` 且不依赖 wheel 外共享库（`src/core/AGENTS.md` 钉版）。

**⑤ 系统接线**：HID 类带 udev 规则（`70-spacemouse.rules`）；主从臂参考 so101_leader 标定。**⑥ CMake 接线**：守六规则；需 SDK 插件 option 门控+缺失跳过。**⑦ 消费端验证**：CTS 收口（`cts/hand/README.md:11`）——录 11 步规定脚本（约两分钟），checker 查 HandPoseRecord 满足 retargeter 依赖（26 关节/米制/OpenXR 系/名实相符）；再写专属 retargeter（参考 `spacemouse_se3_retargeter.py`）。

## 7. 测试与质量

**双语测试树（278 文件；128 py+63 cpp）**：`tests/AGENTS.md:17` 定布局——`tests/cpp/` **Catch2**（一叶子一 target）+pytest（一叶子一 pyproject），按 core/viz/plugins/examples 四区镜像 src/。命名不变量（`tests/AGENTS.md:33`）：可执行名稳定（CI glob `viz_*_tests`）、CTest 前缀稳定、tag 转 label。基建：日志路由夹具、CloudXR 免安装+FakeAdb、mcap RAII、仓库根定位器（`repo_paths.py`）、SBOM 合成世界工厂（`synth.py` 1095 行伪造 git/ELF/CMake 回复）。

**门禁**：pre-commit——ruff+ruff-format、REUSE lint、check-dco-signoff（`.pre-commit-config.yaml:46`）；本地与 CI 同款 `SKIP=check-copyright-year pre-commit run --all-files`（`AGENTS.md:259`，先 `git add -A`）；C++ 格式 CI 把关（clang-format-14，`AGENTS.md:272`）。CI（build-ubuntu.yml）：SOURCE_DATE_EPOCH→uv→CUDA→CloudXR→vcpkg→configure→build→ctest→SBOM。日志 grep 是接口（`AGENTS.md:143`）——改措辞先 grep .github/；SBOM 停构建修根因不排除文件（`AGENTS.md:288`）。

## 8. 新人第一周路线图

**Day 1 跑起来**：uv venv→pip install→跑 `se3_retargeting_example.py`；无头显跑 mcap_record_replay/合成手。**Day 2 构建树与契约**：`cmake -B build` **必跑**（tracker 源码只在构建树）；读 spacemouse.fbs→trackers.toml→build/generated→`generate_trackers.py:47`；`cmake-structure.md`+AGENTS.md。**Day 3 C++ 设备链**：tracker.hpp→deviceio_session.hpp→plugin_manager.hpp→spacemouse 全链；再扫一个复杂插件。**Day 4 Python 数学**：base_retargeter.py→deviceio_tensor_types.py→简单（spacemouse_se3）对比复杂（dex_hand）→teleop_session.py→跑 examples/teleop。**Day 5 质检收口**：有硬件录 take 走 checker；跑 ctest+pytest；装 pre-commit。

**改什么**：补插件缺失 python_accessor/文档；按第 6 节接新 HID 设备（evdev 类最简）。**每次改动**：读路径全部 AGENTS.md→pre-commit 全量→clang-format-14→Signed-off-by。

## 源码实证勘误

以源码为准核实任务书与图谱输入，发现：

1. **插件装载模型**（重大）：图谱 tour 第 5 步称"dlopen 动态库"。grep 证实**零 dlopen/dlsym**：实为 **plugin.yaml+子进程模型**（发现→fork/exec→SIGINT/超时/SIGKILL），数据走 OpenXR 扩展通道（SchemaPusher）。
2. **trackers.toml 条目数**：16 个（初稿曾误写 14，已全量清点修正）；haptic_command 唯一 push。
3. **examples 目录数**：22 个（图谱 L14/tour 第 15 步"28 个"把子目录计入）；teleop 脚本 14+共享 `_example_loop.py`。
4. **src/plugins 目录数**：19 个子目录（含 plugin_utils 与 sensing；纯硬件插件 17）。
5. **测试计数口径**：图谱"179/97"是全部文件口径；测试源文件 128 py+63 cpp。
6. **C++ 测试框架**：Catch2/CTest（`tests/AGENTS.md` 明证），非 gtest。
7. 其余背景（插件群构成、cts 三件套、egopost DINOv3+SOMA、viz MuJoCo robot_twin、cloudxr、两 skill）逐项核实**属实**。8. **CTS 全称**：Conformance Test Suite（`docs/source/conformance/overview.rst:9`），非 "Capture Tracking Sessions"（tour 第 10 步沿用了任务书误称）。

## 附录：锚清单（94 个逐一核实；行号逗号分隔）

- core 设备栈：deviceio_base/…/tracker.hpp:16,31,50,60；deviceio_session.hpp:38,54,63,74,92；plugin_manager/…/plugin.hpp:23,66,74,114；plugin_manager.hpp:54；plugin_manager.cpp:124；pusherio/…/schema_pusher.hpp:88；codegen/generate_trackers.py:47,74；deviceio_trackers/trackers.toml:4,12,78,103；schema/cpp/…/serialized.hpp:1；schema/fbs/spacemouse.fbs:9,16,29；oxr/…/oxr_session.hpp:23；mcap/…/tracker_channels.hpp:33,49；log_bridge/…/logger.hpp:1（…=src/core/ 下完整路径）
- Python 主库：isaaccapture/schema/__init__.py:9；retargeting_engine/interface/base_retargeter.py:40；deviceio_source_nodes/deviceio_tensor_types.py:81；teleop_session_manager/teleop_session.py:108 与 config.py:349；cts/common/…/frames.py:12,65 与 checks/base.py:16,43；cts/hand/README.md:11；isaaccapture_egopost/README.md:16 与 requirements-dinov3.txt:7（…=src/python/ 下）
- viz 与插件：viz/session/…/viz_session.hpp:29；plugins/gamepad/plugin.yaml:4；plugins/spacemouse/plugin.yaml:4 与 app/spacemouse_plugin.cpp:26,28
- 构建/agent-first/治理：`CMakeLists.txt:16,22,35,39,51,59,66,82,111,115`；`pyproject.toml:6,34,42`；`cmake/cmake-structure.md:17,20,66,125`；`.claude/skills/cmake-structure/SKILL.md:2`；`.claude/skills/rebot-orin-setup/SKILL.md:2`；`examples/rebot/SKILL.md:23,56,173,175`；`AGENTS.md:9,29,99,112,143,152,220,259,265,272,284,288,322`
- 测试与文档：tests/AGENTS.md:17,33；tests/python/repo_paths.py:1；cloudxr/conftest.py:1；logging_config/conftest.py:1；mcap_test_support.hpp:1；.pre-commit-config.yaml:46；quick_start.rst:38,53；README.md:28
- 另有文件级引用（无行号）：live_deviceio_factory.hpp、ee_pose_jump_guard.py 等均核实存在。

## 元数据

- 字数口径：不计空格总字符（python `re.sub(r'\s','',s)` 统计），数值见交付回执
- 锚数：94 个 `路径:行号` 锚（附录分组列出）
- 层覆盖：16/16（L01-L16 每层一条+代表文件）
- 图谱基线：6542 节点/11416 边/16 层/16 步 tour/30 枢纽
