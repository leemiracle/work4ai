# IsaacCapture understand 全链台账（2026-11-08 起）

仓库：/usr-data/data2/repos/agent-repos/NVIDIA/IsaacCapture（NVIDIA IsaacCapture，commit df8384f3，只读）
流水线：layers/tour → finalize → onboard → explain → README（本代理认领全链）

## 阶段状态

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析（前会话） | ✅ | assembled-graph.json 6542n/11416e |
| layers.json | ✅ 2026-11-08 | 16 层 1857/1857 file 级节点全覆盖零重复（脚本 /tmp/ic_layers.py） |
| tour.json | ✅ 2026-11-08 | 16 步 105 节点（/tmp/ic_tour.py） |
| finalize | ✅ 2026-11-08 | knowledge-graph.json 6542n/11416e/16层/16步，validator 0 issues 0 warnings，fingerprints 1844@df8384f3，intermediate 已清（scan-result.json 保留） |
| onboard-input.json | ✅ | 288KB（onboard_prep.py，finalize 后仍可用） |
| onboarding | ✅ | 11981 字符/8 节/94 锚/勘误 8（含 CTS=Conformance Test Suite 修正） |
| explain | ✅ | 10 篇全落盘：01=4945/02=5207/03=6320（超限取舍见 README）/04-06=压缩工定稿/07=4797/08=4790/09=4744/10=4722 |
| README | ✅ | 状态表+11 条甄别清单 |
| 图谱勘误回写 | ✅ | tour 第 5 步 dlopen→子进程模型、第 10 步 CTS 全称，修后重校验 0 issues |

## 16 层结构（1857 file 级节点）

L01 门面/根构建/CI/脚本 89 · L02 core schema+codegen 141 · L03 core deviceio 基座 54 · L04 core trackers 三轨 74 · L05 core oxr/mcap/plugin_manager+compat 37 · L06 plugins I 手部触觉传感 71 · L07 plugins II 动捕全身 SE3 47 · L08 plugins III 主从臂驾驶输入 68 · L09 isaaccapture cts 108 · L10 retargeting 引擎线 79 · L11 teleop 会话/viz桥/云XR 79 · L12 egopost 109 · L13 viz C++ 91 · L14 examples 286 · L15 tests 278 · L16 docs/deps/LICENSES 246

## 枢纽事实（派发用）

- 全仓扇入 top：retargeting_engine/tensor_types/__init__ (92) > interface/__init__ (81) > interface/retargeter_core_types (79) > tensor_group_type (67) > deviceio_source_nodes/__init__ (66) > Python 门面 schema/__init__ (73)/teleop_session_manager (49)/deviceio (47)/cloudxr (43)
- C++ 侧枢纽：schema/python/schema_serialized.h (23) > log_bridge/logger.hpp (17) > deviceio_session.hpp (12) > deviceio_base/tracker.hpp (11) > viz vk_context.hpp (19)
- examples/teleop = retargeting 示例集（14 脚本零 ROS）；teleop_ros2 = 完整 ROS2 应用；vehicle_teleop worker = isaac_remote_steering_worker.py（任务书曾给错名 teleop_vehicle.py，已纠正）
- tests/python 无根 conftest.py，入口=repo_paths.py；tests/cpp 按子目录 core/plugins/viz 组织

## explain 选题（10 篇）

1. retargeting 引擎（L10） 2. core trackers 三轨（L04） 3. teleop 双示例（L14） 4. plugins 手部触觉群（L06） 5. plugins 动捕全身群（L07+L08 部分） 6. viz C++ 引擎（L13） 7. schema fbs+codegen（L02） 8. core deviceio 基座（L03+L05） 9. tests 双语（L15） 10. cts+egopost 数据闭环（L09+L12）
