# nurec-skills Onboarding（NuRec 生态 agent 技能包）

> 基座：知识图谱 164 节点/207 边/8 层/10 步 tour，commit `5b9d287e`（2026-11-10 分析）。
> 源码仓：/usr-data/data2/repos/agent-repos/NVIDIA/nurec-skills。所有 `路径:行号` 锚均经源码核实。

## 1. 这个仓是什么（30 秒版）

NVIDIA NuRec 生态面向 coding agent（Cursor / Claude Code / Codex）的**技能包集合**：把"神经重建 + 渲染"全流程（自动驾驶/机器人仿真数据 → 3DGUT/3DGRT 高斯重建 → 新视角渲染 → 资产收割 → 帧清理）教给 agent 去驱动。仓内一行重型引擎代码都没有——README.md:31-34 明确定位为 **thin coordination layer**：不分发 NVIDIA 源码，只教 agent 驱动公开的 NGC 容器（`nvcr.io/nvidia/nre/*`）、GitHub 仓（ncore、asset-harvester、harmonizer）与 HuggingFace 工件。

技能形态遵循 agentskills.io 规范：单篇 Markdown（SKILL.md）= YAML frontmatter（name/description/触发词/upstream pin）+ 精选菜谱（README.md:22-29）。Agent 按名解析技能，与磁盘位置无关。

## 2. 心智模型：六技能拓扑（四执行 + 一路由 + 一目录）

README.md:41-48 的路由表是全仓总纲：

| 技能 | 角色 | 上游 pin |
|------|------|----------|
| `nurec-index` | 路由器，第一跳（README.md:43 "Read first"） | hand-curated |
| `physical-ai-datasets` | 数据集目录（HF `PhysicalAI-*` 前缀全集） | hand-curated |
| `ncore` | 任意传感器录制 → NCore V4 格式 | 上游 `github.com/NVIDIA/ncore` 2026.04 |
| `nre` | 3DGUT/3DGRT 重建训练、渲染、导出、actor 编辑 | NRE `release_26.04` 容器 |
| `asset-harvester` | 逐对象 3D 高斯资产收割（SparseViewDiT+TokenGS） | `NVIDIA/asset-harvester` main |
| `nurec-fixer` | 渲染帧后处理（DiffusionHarmonizer 公开继承者） | HF `nvidia/DiffusionHarmonizer` |

主链路即四执行技能串：**ncore 转换 → nre 重建渲染 → asset-harvester 收割 / nurec-fixer 清理**，两端由 index 路由与数据集目录补齐。这就是任务语境里"五技能体系"的准确口径——五个管线技能（index/ncore/nre/harvester/fixer）+ 一个数据侧目录（physical-ai-datasets）。

两个结构性事实：

- `.agents/skills/` 只是 `skills/` 的 **symlink**（README.md:53；`readlink` 实证 `skills -> ../skills`），不是两棵树。跨技能相对链接 `../nre/SKILL.md` 在两种前缀下都成立（README.md:82-84）。
- `nurec-index/SKILL.md:9` 版本 v0.2.4、391 行 11 节，核心是 `## Pick a skill` 决策表（skills/nurec-index/SKILL.md:168 起）与 `## Easy mix-ups` 易混淆对照（skills/nurec-index/SKILL.md:216 起，如 "NuRec 是产品名、NRE 是引擎，都路由到 `nre`"）。它自己**不执行任何管线**——frontmatter `tools:` 仅声明读类工具；找不到兄弟技能时的路径解析顺序写在 skills/nurec-index/SKILL.md:329-330（`.agents/skills/` → `.claude/skills/` → `.cursor/skills/` → `~/.cursor/skills/` → 兜底 clone 本仓）。

## 3. nre：主力技能的文档面与执行面

`nre` 是全仓最大技能（58 文件，占全仓约三分之一），SKILL.md v0.2.2（skills/nre/SKILL.md:13）13 节覆盖 Purpose/触发边界（skills/nre/SKILL.md:67 含负触发：逐对象资产收割转 asset-harvester、传感器转 NCore 转 ncore）/Inputs/Instructions（skills/nre/SKILL.md:149）/Backend Selection（skills/nre/SKILL.md:241 区分本地 docker 与 OSMO 两条执行路径）/Troubleshooting top 4（skills/nre/SKILL.md:396）。frontmatter 硬件白名单精确到卡型号（skills/nre/SKILL.md:20-23：Ampere A100/A10/A40/RTX A6000、Ada L20/L40S、Hopper H100/H20、Blackwell RTX Pro 6000D；R580+ 驱动），metadata pin 容器代际 `release_26.04`（skills/nre/SKILL.md:44 release_date 2026-04-30）。

references/ 下 18 篇手册构成知识面：`cli-reference.md`（1062 行，以容器 `--help` 为权威枚举 train/val/export/render/serve-grpc/render-grpc/viewer）、`configuration.md`（621 行，训练旗标全部是 Hydra override 而非 CLI 旗标）、`grpc-api.md`（521 行 sensorsim gRPC 协议）、`local-render.md`（483 行）、`aux-data.md`（训练前置辅助数据：逐帧语义分割/深度/DINOv2 特征，以 `<NAME>.aux.<kind>.zarr` 存于 shard 旁）、`carline-adaptation.md`（车款适配=组合既有 NRE+Harmonizer 工作流，不引入新运行时）。

执行面四类资产：

1. **NRE_RenderClient 子技能**（references 内嵌的第二层技能，自带 agentskills.io frontmatter）。核心 `thin_client.py` 1068 行：宿主侧瘦 gRPC 渲染客户端，直连长驻 `nre serve-grpc` 服务器渲染 RGB/LiDAR 帧，**免每轮 Docker 启动与 Python+CUDA 冷启动**。独有能力：Hyperion rig 逐相机 F-theta + 挡风玻璃内参覆盖（`apply_intrinsics_override`，thin_client.py:356 起；`_scale_pixeldist_poly` :326 做像素距离多项式缩放）、轨迹 scipy Slerp 重采样（thin_client.py:552 `interpolate_trajectory_at_fps`，thin_client.py:577 用 `Slerp`）、多相机单次 `batch_render_rgb` 批量渲染（thin_client.py:702/:734）。位姿组合链在 thin_client.py:612/:621：`T_camera_world = T_rig_world @ rig_offset_se3 @ T_camera_rig`，与容器侧 `nre.utils.io.export.render_grpc.py` 严格对齐；`pose_offsets_to_se3`（thin_client.py:159-167）注释明言"lifted from nre.utils.geometry"——客户端是把 NRE 几何模块复刻了一份，避免依赖容器内 Python 环境。proto 发现走 `_find_proto_dir`（thin_client.py:89，sys.path 注入后 import）。
2. **会话管理脚本**：`session_warm_server.sh` 385 行幂等 warm-boot——不硬编码镜像 tag，遍历本地缓存镜像做版本探测选首个 26.04+（session_warm_server.sh:26；`semver_at_least_26_04`，session_warm_server.sh:183）；exit code 语义 0=已就绪/1=启动失败/2=前置不满足/3=版本<26.04（session_warm_server.sh:81-85），状态文件 `/tmp/nre-grpc-session.state`（session_warm_server.sh:96）供 teardown 判活；必填 `NRE_GRPC_USDZ_HOST_DIR` 挂载 /inputs/sdg（session_warm_server.sh:47）。能力不足时回退 per-turn `nre render` CLI。`session_teardown.sh` 56 行收尾。
3. **数据契约**：`rig-json/` 三样本——`rig.json` 1096 行 33 传感器完整 Hyperion rig（10 相机+LiDAR+IMU，nominalSensor2Rig_FLU 位姿 + ftheta 多项式内参字符串）；`augmented_rig.json` 与之**全量 diff 仅 2 个键**（sensors[4] 相机的 `windshield-{horizontal,vertical}-polynomial-approx-inverse`，augmented_rig.json:260-263）——"增强 rig"的语义就是补挡风玻璃畸变的逆多项式近似，供渲染端反畸变；`minimal-synthetic-target-rig.json` 30 行 1 传感器最小可用样本。
4. **环境自检**：`scripts/validate_setup.py` 250 行（asset-harvester/nurec-fixer 各有同名同构脚本）。

## 4. ncore 与数据侧：1058 行的转换百科

`skills/ncore/SKILL.md` 1058 行是全仓最大技能文档，17 节结构清晰：Mental model——V4 store（skills/ncore/SKILL.md:173）、Path A 驱动既有 in-tree 转换器（skills/ncore/SKILL.md:245）、Path B 从模板写新转换器（skills/ncore/SKILL.md:285）、V4 conventions you must obey（skills/ncore/SKILL.md:351）、AV 格式菜谱（skills/ncore/SKILL.md:468，PAI/Waymo/PandaSet/NuScenes）、非 AV 菜谱（skills/ncore/SKILL.md:629，ROS2 bag/mcap/RealSense/ZED/RGB-D/COLMAP/SfM）、r2s 机器人分片（skills/ncore/SKILL.md:907）、validate.py 诊断（skills/ncore/SKILL.md:963）。触发词表 30+ 术语。

扩展点在 `ncore_template/impl/data_converter/example_converter.py`（984 行，全仓最大 Python 文件）：演示转换器契约 `get_sequence_ids`/`from_config`/`convert_sequence` 与 `SequenceComponentGroupsWriter` 的全组件类型写入（Poses/Intrinsics/Masks/Camera/Lidar/Radar/Cuboids），输入为占位数据——新数据源从此起步。注意它 import 的是**用户 pip 安装的上游 `ncore.*` 包**（`pip install nvidia-ncore`，README.md:147），仓内不含 ncore 源码（thin coordination layer 的又一体现）。

`physical-ai-datasets/SKILL.md` 887 行：HF nvidia 下全部 `PhysicalAI-` 前缀数据集目录，按域组织（AV/Robotics-Manipulation/GR00T/mindmap/NuRec/Spatial Intelligence/Grasping/Healthcare/Sim-Ready/Material properties），逐数据集给规模/格式/门控/许可与下游消费技能（frontmatter description，skills/physical-ai-datasets/SKILL.md:3-22）；description 末尾自带负触发 "Do NOT use as a runtime — it routes you elsewhere"。它是唯一没有 BENCHMARK.md 的重文档技能。

## 5. 下游双技能：收割与帧清理

**asset-harvester**（SKILL.md:10 v0.1.1）：驱动 NVIDIA Asset Harvester 从 AV NCore V4 剪辑或带掩码单图提取逐对象 3D 高斯资产（`gaussians.ply` + `metadata.yaml`），供 NuRec 对象插入。frontmatter metadata（skills/asset-harvester/SKILL.md:27-40）pin 上游 GitHub + HF model/demo/dataset 四个工件。`references/installation.md` 记录关键陷阱：必须先装 pinned commit `b60e917c` 的 gsplat 源码编译版，否则 CUDA ABI 不匹配；`cli-reference.md` 给 `run_inference.py`（`--data_root` 与 `--image_dir` 互斥、diffusion/lifting/ahc 三 checkpoint、`--offload_model_to_cpu`）与 `run.sh`（默认 num-steps 30 / cfg-scale 2.0）全量旗标矩阵。

**nurec-fixer**（v0.5.0，14 节）：运行 NVIDIA DiffusionHarmonizer——SKILL.md:86 起专设 `## What changed from the older Fixer skill`，明言是老 Fixer 菜谱的公开继承者。运行时为 `harmonizer-cosmos-env` 镜像：`Dockerfile.cosmos` 在 `nvcr.io/nvidia/pytorch:25.10-py3` 基座上叠 cosmos-predict2 与补丁（SKILL.md:22-26，构建命令 nurec-fixer/SKILL.md:181）。双令牌门槛：`HF_TOKEN`（Harmonizer 权重 + Cosmos-Predict2-0.6B 基模型）+ `NGC_API_KEY`（pytorch 基镜像），约 120 GB 磁盘要求写进 compatibility。training/inference/evaluation/wrapper-image/troubleshooting 六篇参考覆盖模型训练到容器封装全周期。

## 6. 配置与工作流系统：Hydra 14 份 YAML + bash + osmo

`example-workflows/` 三种编排形态，全部围绕一个核心机制——**覆盖层挂载**：

- **Hydra 14 份 YAML**（12 顶层 + `nre-overrides/` 2 份）。骨架组：`paths.yaml` 从 `env:HOME`/`env:REPO_ROOT` 推导全套目录变量（所有工作流 defaults 第一项）；`personal-template.yaml` 五个凭据空槽（ngc_api_key/ngc_org/ngc_team/huggingface_token/huggingface_username，复制为 personal.yaml 填入，禁止提交）。步骤库：`nurec-steps.yaml` 367 行（ncore 数据集→nurec 训练共享 docker 步骤）、`pai-steps.yaml` 207 行（HF PAI 单剪辑下载→转换）、`tools.yaml` 273 行（驱动检查/NGC CLI 等环境准备）。端到端组合：`pai-nurec.yaml`/`waymo-nurec.yaml`/`render-pai-nurec.yaml`；前置转换 `pai-to-ncore.yaml`；取样 `download-{pai,waymo}-samples.yaml`。
- **bash 六段**：`nurec.sh` 是覆盖层注入的教科书实现——把仓内 overlay 挂到容器 `/app/run.runfiles/_main/configs/external_overrides.yaml`（nurec.sh:36），`--config-name=external_overrides` 选择（nurec.sh:38），并留 `NRE_CONFIG_DIR` 环境变量作镜像改版逃生口（nurec.sh:29）。`aux.sh` 严格模式（set -euo pipefail）对 PAI 剪辑跑 lidar-seg-camvis，显式点名 6 个相机 ID。
- **osmo 两份 DAG**：`pai-nurec.yaml` 串全链（其中 :91-100 硬编码容器内 `/home/builder/ncore` 路径做 bazel 构建，非宿主路径）、`render-usdz.yaml`。

覆盖层内容的关键在 `references/configs/pai.yaml`：defaults 基于 `/apps/prod/Hyperion-8.1/car2sim_6cam.yaml`（:11，Maglev PAI 重建工作流同款），只覆盖与 resolved 默认不同的键；`camera_ids`/`val_camera_ids` 显式列 6 相机（pai.yaml:26-32/:35-41，val 比 car2sim 默认多验两个后视相机）、`val_lidar: true`（pai.yaml:51）。**两段被注释掉的勘误性配置**必须一起看：pai.yaml:12-20 给各 layer 加 lidar `intensity` extra_signal 的覆盖（注明"每个 car2sim 定义的 layer 都必须列出，否则未列 layer 退回 semantics-only"），pai.yaml:53-58 对应的 intensity 监督 loss（注明"AV loss 菜谱默认 lambda_=0.0 关闭；不开监督则 intensity 只发射不学习，预测点云 intensity 无意义"）。只解开前者不开后者是真实踩坑点。

## 7. 治理面、上手路线与坑

**治理**：`request-nvskills-ci.yml` 是 GitHub Actions 可复用工作流调用（:22 `uses: NVIDIA/skills/.github/workflows/team-request.yml@main`），双触发——issue_comment 打 `/nvskills-ci` 或 push 且签名匹配（:10-20）。每技能带 `BENCHMARK.md`（NVSkills-Eval 三层评估）：**nre 整体判定 FAIL（skills/nre/BENCHMARK.md:12），但要看懂 FAIL 的成分**——Tier 1 静态扫描 9 项检查出 15630 条 findings（skills/nre/BENCHMARK.md:43），Top 项全是 `references/nre-image-notes.md:187-188`、`local-render.md:72`、`asset-editing.md:61/111` 里的 GPS 坐标 PII（真实采集数据的地理位置），外加 Tier 2 重复内容告警；Tier 3 live agent 评估反而 "not available"。同框架下 asset-harvester/nurec-index/nurec-fixer 均 PASS（各自 BENCHMARK.md:12）。即 FAIL 是**发布合规问题（文档含真实坐标），不是功能不可用**。合规基座：LICENSE(Apache-2.0)/LICENSE-CC-BY-4.0/NOTICE/THIRD_PARTY_NOTICES（声明 NumPy/upath 为 ncore_template 的运行时例外）+ 四套 issue 模板。

**上手路线**（10 步 tour 浓缩）：①README 路由表建心智 → ②nurec-index `Pick a skill` 决策表 → ③nre SKILL.md 能力边界 → ④`validate_setup.py` 环境自检 + NGC 凭据（README.md:142-145 列 HF_TOKEN 门控清单）→ ⑤hydra `pai-nurec.yaml` 端到端首跑 → ⑥`session_warm_server.sh` warm 会话 + thin_client 渲染 → ⑦rig-json 契约 → ⑧export_usdz/asset-editing 出口 → ⑨ncore 转换新数据源 → ⑩harvester/fixer 收尾。

**坑（全部源码实证）**：
1. nre BENCHMARK FAIL ≠ 技能坏了，是 references 文档含真实 GPS 坐标（见上）；引用时须带甄别结论。
2. `pai.yaml` 的 intensity extra_signal（:12-20）与 intensity loss（:53-58）是成对开关，只开前者产生"发射但未学习"的静默劣化。
3. `augmented_rig.json` ≠ 新 rig：全量 diff 只有挡风玻璃逆多项式 2 键（augmented_rig.json:260-263）。
4. `.agents/skills/` 是 symlink，别当第二棵树维护（README.md:53）。
5. osmo `pai-nurec.yaml:91-100` 的 `/home/builder/ncore` 是容器内路径，宿主侧照抄必错。
6. 仓库卫生：无 `.gitignore`，且 `skills/nurec-fixer/scripts/__pycache__/validate_setup.cpython-312.pyc` 被 git 追踪（git ls-files 实证）——本地跑过 validate_setup 的副产物直接进了版本库。
7. `thin_client.py` 的几何函数是从容器内 NRE 复刻的（thin_client.py:159 注释明言），上游 NRE 改几何约定时这里是静态漂移点。
