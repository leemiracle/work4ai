# 02 · nre 渲染链：thin_client 与 rig 契约

## 角色定位

nre 技能的渲染执行面由三件套构成：容器内 `nre serve-grpc` 服务端（协议见 references/grpc-api.md，521 行）、宿主侧瘦客户端 `thin_client.py`（1068 行，skills/nre/references/NRE_RenderClient/scripts/ 下）、以及描述相机/激光雷达几何的 rig JSON 数据契约。NRE_RenderClient 本身是嵌套在 nre references 里的第二层技能（自带 agentskills.io frontmatter）。

## 内部结构

`thin_client.py` 的关键函数链：`_find_proto_dir`（thin_client.py:89）定位并 sys.path 注入 proto 桩；`parse_rig_file`（thin_client.py:241）解析 Hyperion rig；`apply_intrinsics_override`（thin_client.py:356）做逐相机内参覆盖，其中 `_scale_pixeldist_poly`（thin_client.py:326）把 angle-to-pixel-distance 多项式按分辨率缩放——这是 gRPC override 路径独有能力（CLI 渲染没有）；`interpolate_trajectory_at_fps`（thin_client.py:552）用 scipy `Slerp`（thin_client.py:577）对轨迹做重采样；`build_rgb_request`（thin_client.py:597）组装请求。服务端生命周期由 `session_warm_server.sh`（385 行）管理：幂等启动容器、不硬编码 tag 而是遍历本地镜像选首个 26.04+（session_warm_server.sh:26，比较函数 :183），exit code 四态 0/1/2/3（session_warm_server.sh:81-85），状态文件 `/tmp/nre-grpc-session.state`（session_warm_server.sh:96）供 `session_teardown.sh` 判活。

## 外部连接

proto 桩由 `setup_protos.sh` 预提取：支持 `--image/--out/--force`（setup_protos.sh:21-23）与 `NRE_IMAGE` 环境覆盖（setup_protos.sh:26），从本地镜像里按 `nre[-_:]` 正则发现并排除 tools/isaac 兄弟镜像；若 warm server 已运行则直接读它的状态文件拿镜像名（setup_protos.sh:59-61）。`start_grpc.sh` 是裸启动路径。位姿数学刻意不依赖容器：`pose_offsets_to_se3`（thin_client.py:159-167）注释明言 "lifted from nre.utils.geometry"——把 NRE 几何复刻到客户端，上游改约定时这里是漂移点。

## 数据流

rig JSON → 解析 → 内参覆盖 → 位姿组合 → gRPC 请求 → 帧返回。位姿组合链在 thin_client.py:612/:621：`T_camera_world = T_rig_world @ rig_offset_se3 @ T_camera_rig`，与容器侧 `render_grpc.py` 严格对齐；`rig_offset_se3` 由 `pose_offsets_to_se3` 从 rig 的平移+RPY 轴序置换得出（thin_client.py:830 调用点）。多相机场景一次 `batch_render_rgb`（thin_client.py:734，批处理逻辑 :702）逐 pose 批量渲染，省掉逐相机往返。

## 设计决策

- **warm 会话换吞吐**：每轮渲染免 Docker 启动 + Python/CUDA 冷启动（这正是 README 宣传 thin_client 的主卖点）；能力不足时回退 per-turn `nre render` CLI，双路径并存。
- **rig 契约最小增量**：`augmented_rig.json`（1097 行）与 `rig.json`（1096 行）全量 diff 仅 2 键——sensors[4] 相机补 `windshield-{horizontal,vertical}-polynomial-approx-inverse`（augmented_rig.json:260-263），即"增强 rig"= 挡风玻璃畸变逆多项式近似；`minimal-synthetic-target-rig.json` 30 行 1 传感器是合成最小样本。
- **机器可读优先**：ftheta 内参用多项式系数字符串表达、位姿用 FLU 坐标 nominalSensor2Rig_FLU，让契约可 diff、可校验。

## 新人提示

调试顺序：先 `validate_setup.py` 自检，再 warm server（看 exit code 语义），再用 thin_client 单相机小图跑通，最后开多相机批量。`NRE_GRPC_USDZ_HOST_DIR` 是必填项（session_warm_server.sh:47），漏挂 USDZ 场景下载会失败。
