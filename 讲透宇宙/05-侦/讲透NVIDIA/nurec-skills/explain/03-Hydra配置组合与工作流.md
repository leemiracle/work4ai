# 03 · Hydra 配置组合与工作流系统

## 角色定位

`skills/nre/references/example-workflows/` 是 nre 技能的编排层：14 份 Hydra YAML（12 顶层 + `nre-overrides/` 2 份）+ bash 六段脚本 + osmo 两份 DAG，全部围绕一个机制——**把覆盖层挂进容器当 external_overrides.yaml**。它回答"同一套 NRE 容器如何参数化地服务不同数据集"。

## 内部结构

Hydra 组合分四层。骨架：`paths.yaml`（所有工作流 defaults 第一项，`home: ${env:HOME}` 在 paths.yaml:1、`repo_dir` 回退链在 paths.yaml:2）与 `personal-template.yaml`（personal-template.yaml:4/:8 等五个空槽，复制为 personal.yaml 填入、禁止提交）。步骤库：`nurec-steps.yaml` 367 行（nurec-steps.yaml:8 `shm_size: 64g` 等共享变量 + ncore 数据集→nurec 训练全套 docker 步骤）、`pai-steps.yaml` 207 行（HF PAI 单剪辑下载→转换）、`tools.yaml` 273 行（驱动/NGC CLI 环境准备）、`ncore-steps.yaml`。端到端组合：`pai-nurec.yaml`/`waymo-nurec.yaml`/`render-pai-nurec.yaml`。辅助：`pai-to-ncore.yaml` 前置转换、`download-{pai,waymo}-samples.yaml` 取样。覆盖层本体在 `references/configs/` 与 `nre-overrides/`：`pai.yaml` 的 defaults 基于 `/apps/prod/Hyperion-8.1/car2sim_6cam.yaml`（configs/pai.yaml:11），只覆盖与 resolved 默认不同的键。

## 外部连接

bash 侧 `nurec.sh` 是挂载机制的参考实现：宿主 overlay 只读挂到容器 `/app/run.runfiles/_main/configs/external_overrides.yaml`（example-workflows/bash/nurec.sh:36），容器内用 `--config-name=external_overrides` 选择（nurec.sh:38）；`NRE_CONFIG_DIR` 环境变量留作镜像目录改版的逃生口（nurec.sh:29）。osmo 侧 `osmo/pai-nurec.yaml` 把同一链路表达为 DAG（:91-100 在容器内 clone 上游 ncore 并 bazel 构建，注意 `/home/builder/ncore` 是容器内路径）。`configuration.md`（621 行）定义总规则：训练应用全部旗标均为 Hydra override 而非 CLI 旗标。

## 数据流

以 PAI 端到端为例：`personal.yaml`（凭据）+ `paths.yaml`（目录）+ `tools.yaml`（环境检查）→ `pai-steps.yaml` 下载单剪辑 → `pai-to-ncore.yaml` 转 V4 shard → `pai.yaml`/`nre-overrides/pai.yaml` 覆盖层随 `nurec-steps.yaml` 训练步骤挂入 GA 容器 → 产出 USDZ/PLY。`aux.sh` 在训练前对同一剪辑跑 nre-tools 容器生成 aux zarr（aux.sh:2 `set -euo pipefail`，:6 CLIP_ID 默认值，显式点名 6 个相机 ID）。

## 设计决策

- **覆盖不复制**：pai.yaml 全文只写差异键 + 一处显式 `camera_ids` 守卫（configs/pai.yaml:26-32），上游 car2sim_6cam 的 resolved 默认全继承——升级基座配置时下游工作流零改动。
- **成对开关的诚实注释**：configs/pai.yaml:12-20 是注释掉的 lidar `intensity` extra_signal 覆盖（并警告"car2sim 定义的每个 layer 都必须列出，否则未列 layer 退回 semantics-only"），configs/pai.yaml:53-58 是对应的 intensity 监督 loss（警告"不开监督则 intensity 只发射不学习"）——两段必须成对解注释，这是仓里最值钱的自文档化勘误。
- **val 相机守卫**：`val_camera_ids` 显式列全 6 相机（configs/pai.yaml:35-41），因 car2sim 默认只验 4 个前/侧相机会漏掉两个后视相机。

## 新人提示

首跑从 `download-pai-samples.yaml`（download-pai-samples.yaml:2 起，单剪辑下载）+ `render-pai-nurec.yaml` 的最小组合开始；改配置先分清"骨架/步骤/覆盖层"三角色再动手；osmo 路径的硬编码容器内目录不要照搬到宿主侧。
