# 讲透 NVIDIA/deepops

NVIDIA/deepops 知识库全链产物索引。deepwiki 27 页全量 + understand 图谱（885 节点/703 边/14 层/15 步 tour/validator 0 issues/fingerprints 814 文件基线@git facc47e4，2026-11-07 分析）+ onboarding + explain 12 篇。

## 全链状态表

| 阶段 | 产物 | 状态 |
|------|------|------|
| DeepWiki | deepwiki/（27 页 100%，INDEX+_coverage-check） | ✅ |
| understand 图谱 | 仓内 .understand-anything/knowledge-graph.json：885n/703e/14L/15T/0 issues/fp=814@facc47e4 | ✅ |
| NOTES 收割 | 仓内 .understand-anything/NOTES-DIGEST.md（56 条批阶段甄别笔记） | ✅ |
| Onboarding | onboarding/ONBOARDING.md | ✅（并行实例，2026-11-07） |
| explain 组 1（篇 1-6 核心链路） | explain/01~06 | ✅（并行实例，2026-11-07） |
| explain 组 2（篇 7-12 外围线） | explain/07~12 | ✅ 本轮 6 篇 |

## explain 索引（12 篇全）

| 篇 | 主题 | 要点 |
|----|------|------|
| 01 | 两大总编排 | slurm-cluster.yml 31 个 import 与 k8s-cluster.yml 16 个 import 的可裁剪管线 |
| 02 | Slurm 作业系统 | PAM 锁死 SSH 踩坑、prolog/epilog 编号序、PATH drop-in |
| 03 | Pyxis 与 NHC | 容器作业入口（pyxis+enroot）与节点健康门禁 |
| 04 | GPU 驱动与 MIG | 直装/GPU Operator 双路径、MIG 三态探测、systemd-run 验证陷阱 |
| 05 | DGX 固件升级 | 12 任务流水线、always 日志回收、人工断电环 |
| 06 | K8s-GPU 生态 | GPU Operator、SR-IOV、三套 registry 方案 |
| 07 | 存储与网络 | nfs 单角色双形态布尔分流、mofed 版本探测安装、netapp-trident helm 编排、roce_backend 空壳甄别 |
| 08 | 系统服务 | chrony 的 Galaxy 整编痕迹（.galaxy_install_info 化石）、gen-ca.sh CA 预生成、move-home-dirs 临时用户搬运工 |
| 09 | 监控可观测 | prometheus file_sd 自注册、自研 slurm-exporter（258 行 Go）、EFK 六清单、ipmi-exporter 重复键与 privileged 甄别 |
| 10 | MAAS 与裸机 | maas_deploy.sh 21 函数 OAuth 直调、paramiko 固件升级动因、common.sh 运行时锚定 |
| 11 | HPL 实验链 | 488 行生成器模式、41 份 HPL.dat（16 种 P×Q 到 35×32）、verify 1.05 抖动阈值、MACHINFILE 潜伏笔误 |
| 12 | 验证与 AI 知识库 | 三验证器 human/json 双契约、skills/ 六 agent 程序（deploy-airgapped 999 行）、run-tests.sh 603 行破坏性守卫测试 |

## 勘误清单（源码级实证，14 条）

以下均为源码核实过的"文档/直觉 vs 实际"差集，引用可直接定位：

1. **mig-config 重复键**：`config.example/nvidia-mig-config.yml:48` 与 `:54` 两次定义 `all-7g.80gb:`，YAML 后值覆盖前值——上游模板历史遗留，取值时以第二段为准。
2. **nfs molecule 的 kerberos 残留**：`roles/nfs/molecule/default/molecule.yml:19` 注入的是与 NFS 无关的 `kerberos_client_realm_name`，四个 molecule 场景同源复制的痕迹，对本场景无实际影响。
3. **policy-rc.d shebang 笔误**：`roles/cachefilesd/molecule/default/prepare.yml:12` 与 `roles/rsyslog_client/molecule/default/prepare.yml:12` 均写作 `printf '$!/bin/sh\nexit 0'`——单引号内 `$!` 不展开，落盘成字面 `$!/bin/sh`；容器场景只需该文件存在且退出 0，属"带病工作"。
4. **update_kubeflow_config.py 零调用方**：`scripts/k8s/update_kubeflow_config.py`（requests 解析 NGC API + PyYAML 双写镜像引用）在全仓 playbooks/roles/scripts/docs 中无任何调用——孤儿工具，引用前需自行接线。
5. **gpu-operator-node-prep 自证过期**：`roles/nvidia-gpu-operator-node-prep/tasks/main.yml:2-5` 注释自述"GPU Operator ≥1.9.0 起 本角色不再需要，保留至 v1.10.0"——升级集群时应整体跳过；同文件 `:3` 还有 "GPU Oparator" 拼写错误。
6. **roce_backend 是空壳 role**：`roles/roce_backend/tasks/main.yml` 仅 2 行注释零任务，分流文件（allhosts.yaml/k8smaster.yaml 等）由 `playbooks/k8s-cluster/roce.yaml:8,34` 以 `tasks_from` 直接调用——按角色名找逻辑会扑空。
7. **vagrant 版本注释滞后**：`virtual/vagrant_startup.sh:56` 注释"frozen at 2.2.3"，`:58` 实际 wget 下载 2.2.14（ubuntu 路径 `:112/:114` 同款）——注释与制品相差一个代次。
8. **ipmi-exporter 首行重复键化石**：`workloads/examples/k8s/services/ipmi-exporter.yml:1` 注释的 docker run 含两个 `--name`（ipmi_exporter 与 prometheus-ipmi-exporter）；现行方案是 `:20` 起的 DaemonSet，且因 hostPath `type: CharDevice` 不工作必须 `privileged: true`（`:42-43`，`:48` 注释实证）。
9. **HPL 启动器 MACHINFILE 笔误（潜伏 bug，本仓未修）**：`workloads/bit/hpl/launch_hpl_experiment.sh:303` `mv ${MACHINFILE}.t2 ${MACHINEFILE}` 拼错变量名（缺 E），展开为空后 mv 必失败——**`-x` 排他节点列表过滤实际从不生效**。
10. **chrony 是 Galaxy 外来角色**：`roles/deepops_chrony/meta/main.yml:3` 作者 unxnn、`meta/.galaxy_install_info:1` 安装时间 2020-04-02——目录内 .travis.yml 等化石勿当成 DeepOps 亲写代码重构。
11. **deploy-airgapped 诚实标注仓内死脚本**：`skills/deploy-airgapped/SKILL.md:30-32` 明文"Do not run scripts/airgap/build_offline_cache.sh: it calls the removed playbooks/airgap/build-offline-cache.yml"——脚本残骸仍在（`scripts/airgap/build_offline_cache.sh:98`），知识库以警告而非删除处理。
12. **监控清单是版本化石**：`workloads/examples/k8s/services/prometheus-monitor.yml:63,88` 锁 prometheus v2.1.0/alertmanager v0.14.0（2018 年代），Kibana 5.6.4（`logging/kibana-deployment.yaml:24`）——示例定位，生产需自行换新。
13. **AGENTS.md 是 agent 操作宪法而非普通 README**：仓根 AGENTS.md 定义 golden path 与硬规约（如 `:87` "验证 GPU 用 `srun --gpus=1 nvidia-smi` 或 validate_slurm.py，never with bare SSH"——DeepOps 把 GPU 藏进 cgroup，裸 SSH 验证不到作业视角）；skills/README 要求"every command must work as written from a clean checkout"。
14. **图谱方法论注记**：本仓 Ansible YAML 的 import/include 语义边 scanner 自动解析全空，703 条边中约 237 条依赖关系为批阶段人工源码补扫（include_tasks/import_playbook/roles_path 三段式 ansible.cfg 解析）——增量更新时此类边需重新人工核对。

## 本目录结构

```
讲透NVIDIA/deepops/
├── README.md          # 本文件（状态表+勘误）
├── deepwiki/          # DeepWiki 27 页 100%（前轮）
├── onboarding/        # ONBOARDING.md（并行实例）
└── explain/           # 12 篇源码精讲（1-6 并行实例 / 7-12 本轮）
```

图谱源文件在仓库内 `/usr-data/data2/repos/agent-repos/NVIDIA/deepops/.understand-anything/knowledge-graph.json`（fingerprints 基线支持增量更新，重跑前先核对 git commit）。

字数口径：explain 各篇字数为"不计空格总字符数"，规格 1500-2500（12 篇实际落在 2360-2500）；行号锚均经源码 grep 核实（源码 commit facc47e4），锚数 23-41/篇。
