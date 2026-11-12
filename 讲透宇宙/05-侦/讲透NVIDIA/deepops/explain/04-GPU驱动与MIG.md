# 04 · GPU 驱动与 MIG：双路径与三态探测

## 角色定位

NVIDIA 软件层有两条互斥路径装"驱动+MIG"：裸机/Slurm 线走 playbooks/nvidia-software/（nvidia-driver.yml 直装 + nvidia-mig.yml 用 mig-parted/mig-manager 切分），K8s 线默认走 GPU Operator（驱动容器 + MIG Manager 全在 Pod 里）。两条路径共享同一套探测纪律——因为 DeepOps 的 Slurm login 设置会把 GPU 从 SSH 会话的 cgroup 里藏起来，一切 nvidia-smi 探测必须 `systemd-run --wait --pipe --collect --` 包裹进瞬态单元跑。

## 内部结构

nvidia-driver.yml 先 stat `/etc/dgx-release`（`:8-11`）识别 DGX 预装环境，再 include facts 角色（:13-16，`ansible_local['gpus']['count']` 来自 lspci）；`:21-24` 只在"有 GPU 且非 DGX"时才装 nvidia.nvidia_driver（DGX 的驱动由厂商源码栈预装）。`:28-35` 的验证注释点破经典陷阱：裸跑 nvidia-smi 在 login-compute-setup 隐藏 GPU 的节点上"恰好验证不到真实作业视角"。nvidia-mig.yml 的探测（`:28-38`）是全仓退出码语义的范本：查询与匹配拆开（`mig_mode=$(... nvidia-smi --query-gpu=mig.mode.current ...) || exit 2` 再 grep），注释钉死三态——rc 0=有 GPU 报告 MIG 模式（配置该节点）、rc 1=查询成功但无 MIG 能力（跳过）、rc 2=查询本身失败（是错误不是答案）；`grep -E '^(Enabled|Disabled)$'` 取代旧 `grep -v N/A`，因为后者会误匹配 nvidia-smi 夹带的警告行。`:44-53` 把 rc==2 且 lspci>0 判为硬失败——"查询不到 GPU 的节点不等于没有 MIG 的节点"。roles/nvidia-mig-manager/tasks/main.yml:13-24 复用同款探测；:40-43 先 `which nvidia-mig-parted`，已手工装过 parted 则跳过 manager 包（:47-61 deb/rpm 分发）。

## 外部连接

nvidia-mig.yml:62-66 拷贝 `config/nvidia-mig-config.yml` 到节点——该文件以 `mig-configs:` 预设名组织（nvidia-mig-config.yml:2），如 `all-1g.5gb: {"1g.5gb": 7}`（:17-19）；apply/assert 都经 systemd-run 隔离（:71-76、:95-99），`nvidia-mig-parted apply -c 配置 -c profile -k hooks` 失败故意不处理——"没能应用的 MIG 布局不许伪装成已应用"。K8s 侧 roles/nvidia-gpu-operator 用 helm 直调（k8s.yml:6-16，一条 upgrade --install 带 `mig.strategy=mixed`、`driver.enabled`、`migManager.enabled` 全套 --set）；main.yml:2-6 对 DGX 预装环境 set_fact `gpu_operator_enable_driver: false`——operator 只补 toolkit 不重装驱动。defaults 锁定 chart v26.7.0、驱动 580.126.20、`k8s_gpu_mig_strategy: mixed`（defaults/main.yml:15-36）。

## 数据流

MIG 生坏流程：探测（三态）→ profile 配置文件就位 → mig-parted apply（若 RebootRequired 则 :79-93 async shutdown + wait_for_connection）→ assert 复核。驱动流程：DGX 判定 → lspci 计数 → 装或不装 → systemd-run 验证。K8s 分叉由 k8s-cluster.yml:166-167 的条件（operator 关闭或 preinstalled）与 :302-306（operator 开启）互补，两条 GPU 栈永不共存。

## 设计决策

① 探测三态化是核心决策：管道会吞退出码、合并跑则"N/A 答"与"没答"不可区分，DeepOps 反复为此付出事故代价后在 playbook、role 两层都写成拆开式。② DGX 与普通服务器分治：dgx-release 文件存在性是唯一判据，避免在 DGX 上重装驱动破坏厂商栈。③ MIG 双路径二选一不抽象统一——裸机用 mig-parted 命令行语义、K8s 用 operator CRD 语义，各自贴近平台习惯。④ reboot 用 `async:1 poll:0` 立即放行再 wait_for_connection 轮询（:80-89），而非 reboot 模块，配合 mig_manager_reboot_timeout 900。

## 新人提示

自己写 GPU 探测脚本时照抄 `set -o pipefail + 变量捕获 || exit 2 + 独立 grep` 三段式，并单独处理 rc>1。切换 MIG 布局前先 `nvidia-mig-parted assert` 确认当前态；改 profile 只动 config/nvidia-mig-config.yml 与 `mig_manager_profile` 变量，不碰 role。K8s 集群上看到驱动版本不对，先分清是宿主机包（preinstalled 路径）还是 operator 驱动容器（defaults 里 `gpu_operator_driver_version`）在管。
