# 讲透 NVIDIA IsaacCapture

> NVIDIA IsaacCapture（commit df8384f3，VERSION 1.7.x）——Isaac 生态数据采集基础设施：teleop 遥操作 / retargeting 重定向 / trackers 追踪 / 19 目录硬件插件群 / viz 自研 Vulkan 引擎。**agent-first 仓第七例**（.claude/skills 双配方）。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析 | ✅（前会话） | assembled-graph 6542n/11416e |
| layers | ✅ 2026-11-08 | 16 层，1857/1857 file 级节点全覆盖零重复 |
| tour | ✅ 2026-11-08 | 16 步 105 节点（dlopen/CTS 两处误述已于图谱内修正+重校验 0 issues） |
| finalize | ✅ 2026-11-08 | knowledge-graph.json 6542n/11416e/16 层/16 步，validator **0 issues 0 warnings**，fingerprints **1844 文件@df8384f3** |
| onboarding | ✅ | onboarding/ONBOARDING.md **11981 字符**（不计空格）/8 节/**94 锚**/勘误 8 条，含 agent-first 专节 |
| explain | ✅ 10 篇 | 见下表，六节结构+行号锚全源码核实 |
| README | ✅ | 本文件 |

图谱在仓内：`/usr-data/data2/repos/agent-repos/NVIDIA/IsaacCapture/.understand-anything/knowledge-graph.json`。

## explain 十篇索引

| 篇 | 主题 | chars（不计空格） | file:line 锚 | 勘误 |
|---|---|---|---|---|
| 01 | retargeting 引擎（计算图内核） | 4945* | 26 | 5 |
| 02 | core 追踪三轨（live/deviceio/replay） | 5207* | 28 | 5 |
| 03 | schema fbs 数据契约+codegen | 6320* | 27 | 5 |
| 04 | teleop 双示例（示例集+ROS2 应用） | 4714 | 25 | 4 |
| 05 | plugins 手部/触觉群 | 4748 | 22 | 5 |
| 06 | plugins 动捕/全身/主从臂群 | 4750 | 14 | 5 |
| 07 | viz C++ Vulkan 引擎 | 4797 | 26 | 1 |
| 08 | core deviceio 基座+运行时粘合 | 4790 | 36 | 3 |
| 09 | tests 双语（pytest+Catch2） | 4744 | 20 | 4 |
| 10 | cts 采集管线+egopost 后处理 | 4722 | 23 | 5 |

\* 01/02/03 超出 4800 上限 3%/8%/32%：六节结构+行号锚+勘误完整性的密度下限取舍（每锚 160-230 字符），锚与勘误零删减；其余七篇在限内。

## 甄别清单（源码实证勘误精选，全部以源码为准）

**重大（推翻任务书/常见直觉）**
1. **插件装载模型非 dlopen**：grep 全 src/core 零 dlopen/dlsym；PluginManager=plugin.yaml 清单发现+fork/execvp **子进程监督器**（plugin.cpp:319/396），隔离靠进程边界，数据走 OpenXR 扩展通道（SchemaPusher）。图谱 tour 第 5 步原误述已修。
2. **CTS 全称 = Conformance Test Suite**（docs/source/conformance/overview.rst:9）——设备一致性测试套件，非 "Capture Tracking Sessions"。tour 第 10 步与 ONBOARDING 初稿误述均已修。
3. **C++ 测试框架是 Catch2 非 gtest**：17 个 CMakeLists 实证、grep gtest 零命中（tests/AGENTS.md 布局明文）。
4. **sensing/ 不是插件**：11 文件全是 scripts/docker/configs（SENSING GMSL 相机部署工具集），无 plugin.yaml 无 C++。
5. **plugin.hpp 无生命周期契约接口**：`core::Plugin` 是宿主侧子进程 RAII 包装器（零虚函数）；真实契约=plugin.yaml 清单+main.cpp 信号循环+OpenXR session 三件套。
6. **cts↔egopost 零代码交叉引用**：双向 grep 实证（"cts" 命中皆 affected 子串）——"数据闭环"只在语义层，无 import 边。
7. **pyproject description 仍是历史名 "Isaac Teleop"**；1.6 起包名 isaacteleop→isaaccapture，双名并存（CMake 工程名仍是 IsaacTeleop）。

**口径与计数**
8. trackers.toml 16 条目（haptic_command 唯一 push）；tracker 家族=8 手写类+16 清单类；examples 实为 22 目录（"28"含子目录）；tests/python 无根 conftest.py（入口 repo_paths.py）；测试源文件 128 py+63 cpp（179/97 为全文件口径）；schema/python/ 33 文件全是 C++ 绑定源码非 Python。
9. oak 的 plugin.yaml 描述失实：宣称 CloudXR streaming+MP4，源码实为裸 H.264 NAL 文件+元数据 MCAP 二选一。
10. egopost 许可证 OpenMDW-1.1（非主仓 Apache-2.0，README badge 双许可）；EgoHand 论文 arXiv 2610.30293。
11. 其余核实属实：插件群构成、retargeting 三层结构、viz MuJoCo robot_twin、cloudxr 打包-only、双 agent skill、SBOM 管线。

## 流水线备注

- 2026-11-08 上午全链主体完成；午间 1308 限额团灭（onboard/组A/组C 死于收尾压缩轮），13:12 watchdog 恢复后主会话接手：补写 09/10、压缩 01/02/03/08 与 ONBOARDING、修图谱 tour 两处误述并重校验——盘上产物零损失。
- 瞬时 1302 限流三波均按钉版处置（sleep 45-75s 重试，先只读后写盘）。
- 甄别条款全程生效：子代理纠正任务书锚点错误 6 处（如 vehicle_teleop 入口文件名、examples/teleop 真身为 retargeting 示例集非 ROS2-free 原版）。
