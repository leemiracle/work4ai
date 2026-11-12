# DeepOps ONBOARDING（NVIDIA/deepops）

> 图谱基线：885 节点 / 703 边 / 14 层 / 15 步 tour / validator 0 issues / fingerprints 814 文件 @ `facc47e4`。
> 本文行号锚全部从源码逐条核实（commit facc47e4），与图谱（`/usr-data/data2/repos/agent-repos/NVIDIA/deepops/.understand-anything/knowledge-graph.json`）对齐。

---

## 1. 项目定位：K8s/Slurm 双栈 GPU 集群的一键部署运维仓

DeepOps 是 NVIDIA 官方维护的 GPU 集群操作系统仓：用一套 Ansible 资产把裸金属 NVIDIA 服务器变成开箱即用的生产级 GPU 集群，同一套 roles 支撑 **Slurm**（HPC 调度形态）与 **Kubernetes**（云原生形态）两种集群。它没有服务端组件——一切行为都是"playbook 作用于你自己的 inventory"（AGENTS.md:5-6 原文："Everything here is driven by playbooks against an inventory you control; there is no server component"）。

三个定位要点：

- **双总入口**：`playbooks/slurm-cluster.yml` 与 `playbooks/k8s-cluster.yml` 是仅有的两个集群级顶层入口（AGENTS.md:16 的 Repository map 把二者并列为 "the two top-level cluster deploys"），其余 60+ 个 playbook 全是二者的组件级子编排。
- **两个 git submodule 决定能力边界**：`.gitmodules:1-6` 声明了 `submodules/kubespray`（K8s 部署引擎，K8s 路径的集群本体完全委托给它）与 `submodules/packer-maas`（MAAS 镜像烘焙）。K8s 工作前必须初始化 submodule。
- **验证即产品的一部分**：AGENTS.md:35 明文规定 doctor 必须报 `"ok": true 才许跑集群 playbook；AGENTS.md:47/58 要求两种集群的 validator 分别达到 `gpu_job_ok: true` / `cuda_smoke_ok: true`。部署与验收在同一仓内闭环，这是 DeepOps 与"只管装不管验"的部署脚本的分水岭。

仓库形态：~850 个有效文件中 roles/（51 个 Ansible role，实证计数，`ls roles/` 除 requirements.yml 外 51 目录）占大头，加上 68 个 playbook、scripts/ 七个子域共 30 个脚本（deepops/k8s/validation/slurm/generic/airgap/nginx-docker-cache）、128 个 workload 示例。整个仓库自带 AI agent 协作层（AGENTS.md + skills/ 6 个 SKILL.md），是"给人和 agent 同时用的运维仓"这一新范式的早期样本。

上手三步（AGENTS.md:30-32）：`git submodule update --init --recursive` → `./scripts/setup.sh` → `cp -r config.example config`，然后先跑 `python3 scripts/validation/deepops_doctor.py --json` 做部署前体检。

---

## 2. 架构总览：14 层图谱与两大总编排

知识图谱把仓库切成 14 层（L01-L14）：L01 仓库工程基础 → L02 集群编排 playbook（68 文件）→ L03 Slurm 作业系统（72）→ L04 GPU 驱动与容器运行时（35）→ L05 DGX 固件硬件（38）→ L06 K8s GPU 与容器生态（49）→ L07 存储与网络（65）→ L08 集群系统服务（62）→ L09 HPC 软件栈（46）→ L10 监控可观测（33）→ L11 配置面与虚拟环境（50）→ L12 运维脚本与镜像源码（41）→ L13 工作负载与基准（128）→ L14 文档 CI 与验证（112）。

### 两大总编排的解剖

**Slurm 路径**：`playbooks/slurm-cluster.yml` 全文 155 行、**31 个 import_playbook**（实证 grep 计数；此前口径 30 偏差 1）。每个组件都是"import_playbook + when 变量开关 + hostlist 重定向"三元组，形成可裁剪部署管线：

- bootstrap 三件套在 L5/L8/L11（python/ssh/sudo），chrony 在 L24；
- 本地 registry 落 slurm-master（`container/standalone-container-registry.yml hostlist=slurm-master`，slurm-cluster.yml:28），NGINX 缓存代理默认落 slurm-cache 组（L36，`nginx_docker_cache_hostgroup | default('slurm-cache')`）；
- NFS 服务端默认落 **首个 NFS 节点**（L62：`nfs_server_group | default('slurm-nfs[0]')`），客户端落 slurm-nfs-client 组（L68）——"inventory 分组驱动角色落位"的直接证据；
- 驱动（L44）、CUDA（L51）、DCGM（L72，hostlist=slurm-node）、NHC（L76）、Slurm 本体（L80）、OpenMPI/Lmod/HPC SDK（L83/L87/L91）、监控全家桶（Prometheus L97 / Grafana L103 / Alertmanager L109 / 三类 exporter L115/L121/L125）、rsyslog（L129/L135）、GPU 时钟（L141）、Pyxis/Enroot（L145）、nv_peer_mem（L153）。

**K8s 路径**：`playbooks/k8s-cluster.yml` 全文 322 行、16 个 import_playbook。精髓在与 kubespray 的接缝处理：

- L12-22：按 `container_manager` 预设 facts——非 docker 运行时强制 GPU Operator + host etcd（L6 注释明说 `etcd_deployment_type must be host`）；
- L29-34：submodule 版本锁定在 playbook 内自动 `git submodule update --init`（delegate_to localhost）；
- L86-102：`dpkg_selections` purge 解除 Ubuntu 上被 hold 的 docker-ce/containerd.io——DGX OS 类预装环境的高频故障定点排除；
- L110：`import_playbook: ../submodules/kubespray/cluster.yml` 完成集群本体；随后是 DeepOps 增值层：禁 swap（L118/L120）、kubectl/helm 引导到管理节点（L186-261）、GFD（L291）、device plugin（L297）、GPU Operator（L303）、NFS provisioner（L309）、rsyslog（L313/L319）。

### 51 个 role 的八个语义族

按图谱 L03-L10 的分层，51 个 role 聚成八个语义族：① Slurm 族（slurm/pyxis/nhc）；② NVIDIA 单机软件族（nvidia_cuda、nvidia_dcgm、nvidia-dcgm-exporter、nvidia_container_toolkit、nvidia-peer-memory）；③ DGX 硬件族（nvidia-dgx、nvidia-dgx-firmware）；④ K8s GPU 族（nvidia-gpu-operator、nvidia-gpu-operator-node-prep、nvidia-k8s-gpu-device-plugin、nvidia-k8s-gpu-feature-discovery、nvidia-mig-manager、nvidia-network-operator + 三套 registry 角色）；⑤ 存储网络族（nfs、cachefilesd、autofs、move-home-dirs、mofed、netapp-trident、nfs-client-provisioner、roce_backend、dns-config、deepops_hosts）；⑥ 系统服务族（deepops_chrony、kerberos_client、nis_client、rsyslog_client/server、deepops_users、facts、maas-controller）；⑦ HPC 软件族（lmod、spack、easy-build、easy-build-packages、openmpi、nvidia_hpc_sdk、nvidia-gpu-tests）；⑧ 监控族（prometheus、prometheus-node-exporter、prometheus-slurm-exporter、grafana、alertmanager）+ docker-login/docker-rootless 杂项。

### 三个全局工程决策（改仓前必知）

- **roles_path 三段式**（ansible.cfg:3）：`./roles/galaxy:./roles:./submodules/kubespray/roles`——Galaxy 角色、自有 role、kubespray role 在同一 playbook 内无差别引用；ansible.cfg:4 还把 kubespray 的 library 也挂进来。inventory 也是双源（ansible.cfg:5：静态 `./config/inventory` + 动态 `./scripts/maas_inventory.py`）。
- **fact 缓存 86400 秒**（ansible.cfg:8-10）：jsonfile 缓存写 /var/tmp/ansible_cache。这是 AGENTS.md 中"主机名复用导致陈旧 fact"陷阱的直接来源——克隆虚拟机改主机名后旧 fact 会被吃一整天，排障时先清缓存。
- **粘合 playbook 复用 kubespray 变量体系**：`playbooks/container/docker.yml:9-18` 用 vars_files 直接加载 `submodules/kubespray/roles/kubespray_defaults/defaults/main/main.yml` 并 include 其 `0020-set_facts.yml` 任务（含 fallback_ips 空列表防未定义，L28），保证 docker role 看到的 facts 与 kubespray 一致；L19-25 先删 DGX OS 的 `/etc/systemd/system/docker.service.d/docker-override.conf` 冲突配置再装 Docker。

---

## 3. Slurm 作业系统：PAM、prolog/epilog 与 pyxis

slurm role 是全仓最大角色（2383 行），也是踩坑注释密度最高的地方。

### PAM 锁死 SSH：全仓最危险的坑

计算节点默认开启"有作业才能登录"（config.example/group_vars/slurm-cluster.yml:47 `slurm_restrict_node_access: true`；group_vars 里同时有 `slurm_manage_gpus: true` 让 Slurm 用 GRES 管 GPU，L11）。实现靠 PAM：`roles/slurm/tasks/compute.yml:193-205` 向 `/etc/pam.d/sshd` 注入三行——`-account sufficient pam_slurm_adopt.so action_no_jobs=ignore`（L197，无作业用户放行给下一行判断）、`-account sufficient pam_listfile.so item=user sense=allow file=/etc/localusers`（L198，本地白名单）、`-account required pam_slurm_adopt.so`（L199，最终裁决）。

坑在 compute.yml:161-165 的注释里写得很清楚：`slurm_pam_lib_dir` 是**按架构派生**的路径，已有安装版本匹配而跳过重编时，PAM 模块可能不在本轮选中的目录——一条指向不存在文件的 `-account` 行会**把操作员锁死在节点外**。防御是两段式：L167-174 先 stat 定位 `pam_slurm_adopt.so`，L176-191 stat 失败即 fail 并给出修复菜单（`slurm_force_rebuild=true` 重编，或手工指定 `slurm_pam_lib_dir`）。

### prolog/epilog：编号即执行序

Slurm 本体模板把钩子挂到共享脚本（roles/slurm/templates/etc/slurm/slurm.conf:62-63 `Prolog=`/`Epilog=`，L57 还有 `PrologFlags=Alloc,Serial,Contain`；L120 `AccountingStorageTRES=gres/gpu` 按 GPU 计账）。prolog.sh/epilog.sh 都只是 `set -e + logger 起止标记 + 调 run-parts.sh 遍历目录`的薄壳，**真正的执行序由文件名编号决定**。epilog.d 实证清单：

- `40-lastuserjob-processes`：`killall -9 -u` 杀光用户进程——注释（L4-12）明确它必须与兄弟脚本共享 `/etc/localusers` 豁免，否则在计算节点登录 shell 里提交作业的操作员会在 epilog 瞬间断连；
- `41-lastuserjob-ssh`：L4-8 先查 `localusers.backup`，不在豁免名单才 `sed -i` 把用户从 `/etc/localusers` 删除（撤销 SSH 资格）；
- `42-lastuserjob-cleanup`：清 /tmp 与 /dev/shm 用户文件；L10-11 注释点出账号常含点号（如 `je.kim`），必须 `grep -x -F` 整行字面匹配，正则词匹配会把 `.` 当任意字符；
- `50-exclusive-gpu`：`nvidia-smi pmon` 抓残留 GPU 进程 kill -9，杀不干净节点标记 drain；
- 另有 `50-lastuserjob-all-enroot-dirs`、`60-exclusive-cpu`、`80-exclusive-cleanup`；prolog.d 侧对称地有 `50-all-enroot-dirs/50-exclusive-cpu/50-exclusive-gpu/50-exclusive-ssh`。

遍历器 `shared/bin/run-parts.sh` 的注释是 shell 陷阱教科书：L29"重定向 stderr 不会吞掉退出状态"、L51"接进 `$(wc -l)` 会隐藏退出状态，必须显式捕获"——进程替换与命令替换在 `set -e` 下的语义差异被钉死在源码里。

这套钩子有独立回归测试：`tests/slurm-epilog/run-tests.sh:4-12` 说明设计哲学——molecule 容器跑不了 systemd 所以 slurm role 不进 CI，而这些脚本做的全是破坏性操作（killall/rm -fr），"误杀旁观者与正常清理的输出一模一样"，因此测试只钉"是否该杀"的判定守卫、零依赖可跑；render.py 先渲染模板保证测的就是部署形态。扩展点在 docs/slurm-cluster/slurm-prolog-epilog/（14 个示例脚本），其中 `prolog-mps-per-gpu:3` 用 `scontrol show job | grep Comment | grep -i mps-per-gpu` 解析 `sbatch --comment` 做作业级 MPS 开关——Slurm 生态少见的轻量扩展手法。

### pyxis：容器作业进 Slurm 的桥

pyxis role 以 **SPANK 插件**身份把 Enroot 容器拉进 Slurm 作业：`roles/pyxis/templates/etc/slurm/plugstack.conf` 只有一行 `include {{ slurm_config_dir }}/plugstack.conf.d/*.conf`，真正的插件声明在 `plugstack.conf.d/pyxis.conf:1`（`required /usr/local/src/pyxis/spank_pyxis.so`）；tasks/pyxis.yml:57/67 负责落位。版本锁 `slurm_pyxis_version: 0.11.1`（defaults/main.yml:4）；AppArmor 的 enroot-nsenter 豁免 profile 也随 role 分发（files/etc/apparmor.d/enroot-nsenter，defaults L23 注释解释 Ubuntu 默认 profile 会挡 nsenter）。入口在 slurm-cluster.yml:144-151，`slurm_install_enroot`+`slurm_install_pyxis` 双开关。验收链路 `playbooks/slurm-cluster/slurm-validation.yml` 完整复现用户视角：容器经 Pyxis/Enroot 进作业，NCCL allreduce 带宽做互联健康金标准。NHC 节点健康检查的 nhc.conf.j2 是 facts 驱动的模板：L4 用 `ansible_local.topology` 校验 CPU 拓扑、L7 物理内存 ±5% 容差、L10 根文件系统 rw。

---

## 4. GPU 栈：驱动、MIG 双路径与 DGX 固件

### systemd-run 包裹：本仓最经典的验证陷阱

DeepOps 把 GPU 从普通 SSH 会话的 cgroup 中隐藏（SSH 服务的 DeviceAllow 限制），所以**裸跑 nvidia-smi 验证不到作业视角**。三处独立实现同一防御：

- `playbooks/nvidia-software/nvidia-driver.yml:28-35`：装完驱动用 `systemd-run --wait --pipe --collect --quiet -- nvidia-smi` 冒烟（L30），在 systemd 瞬态单元里执行才命中与 Slurm 作业一致的设备可见性；DGX 机型跳过（L10-11 探测 /etc/dgx-release，L24 判定 DGX OS 自带驱动仓库）；
- `playbooks/nvidia-software/nvidia-mig.yml:31`：MIG 探测同样 systemd-run 包裹并 `|| exit 2`——L19-22 注释解释瞬态单元的原因，L48 区分"N/A"与"根本没答"两种输出；
- `playbooks/utilities/gpu-clocks.yml:8-10`：注释直接点名 "DeviceAllow on the ssh service" 是 Ansible 连接看不到设备的原因。

AGENTS.md:87 把这条升格为操作铁律：验证 GPU 必须走 `srun --gpus=1 nvidia-smi` 或 validate_slurm.py，**never with bare SSH**。

### MIG 双路径分治

MIG 配置有两条互斥路径：**Slurm/裸机走 playbook + GPU Operator 走 MIG Manager（mig-parted）**。K8s 侧 roles/nvidia-mig-manager 的制品直接来自 NVIDIA/mig-parted releases（defaults/main.yml:23-24 的 deb/rpm URL；tasks/main.yml:41 探测 `which nvidia-mig-parted`），默认 profile 是 `all-disabled`（config.example/group_vars/all.yml:283-286）。预设矩阵集中在 config.example/nvidia-mig-config.yml（L2 `mig-configs:` 键为预设名、值为设备段数组）——注意 L48 与 L54 存在重复键 `all-7g.80gb`，YAML 后值覆盖前值，属上游模板历史遗留，改配置时会静默丢前一份。

### DGX 固件：人工断电循环与安全前提

固件升级是全仓最高危链路。`playbooks/nvidia-dgx/nvidia-dgx-fw-update.yml:4-10` 强制 `connection: paramiko_ssh`——注释说明固件/BMC 升级会重启 sshd，OpenSSH 多路复用通道易被打断而 paramiko 独立会话更稳。role 侧（roles/nvidia-dgx-firmware/tasks/main.yml）的安全前提是：L35 systemd 停服、L43 `modprobe` 卸载 nvidia/nvidia_uvm 模块、L59 `always` 块保证任何失败都回收日志（高危运维任务的标准兜底）；get-data/check-firmware/run-diagnostics 等子任务分流采集，清单解析靠脚本式 CLI `files/parse_manifest.py`。整条链路含重启 BMC，**实操上需要人工断电循环**（playbook 注释与 docs 均提示会重启 sshd/整机）。

### 容器运行时侧的幂等手法

`roles/nvidia_container_toolkit/tasks/docker.yml:13-18` 不用 template 覆盖而是 command 内嵌 `python3` 对 `/etc/docker/daemon.json` 做读改写合并——保住现场已有键的幂等手法，changed 判定依赖脚本退出语义。K8s 侧的 nouveau 屏蔽在 roles/nvidia-gpu-operator-node-prep：`files/blocklist-nouveau.conf:1-2`（blacklist nouveau + modeset=0）+ tasks/main.yml:6-8 卸载模块。

---

## 5. K8s 生态：GPU Operator、绕过 helm 模块与三 registry

### GPU Operator 与 helm 模块绕行

K8s 路径的 GPU 栈整体交给 GPU Operator（驱动/toolkit/DCGM/MIG Manager 一并接管）。`roles/nvidia-gpu-operator/tasks/k8s.yml` 头部注释（L2-5）保留绕行历史："While we would prefer to use the Ansible helm module, it's broken!... See https://github.com/ansible/ansible/pull/57897... not be fixed until Ansible 2.10"——于是 L7 `helm repo add`、L15 `helm upgrade --install` 全部直调 `/usr/local/bin/helm` 二进制并压 `changed_when: false` 噪音，一条命令里 --set 透传 driver.version/mig.strategy/toolkit/dcgm/migManager 全套开关并 `--wait`。

同一手法在 `roles/k8s-internal-container-registry/tasks/main.yml` 复刻（L2-5 同款注释、同款 pull/57897 链接，L8 `helm repo add`、L24 `helm upgrade --install -f values`）。**对照样本**是 `roles/nvidia-network-operator/tasks/main.yaml`：L16 `kubernetes.core.helm_repository`、L21 `kubernetes.core.helm`、L32/L38 `kubernetes.core.k8s/k8s_info` 走的是正常模块路线——依赖 openshift python 库的场景用模块，无依赖场景用命令行，两种姿势在同一仓内并存，改 helm 相关逻辑前先看目标 role 用的哪条路。

### 三套 registry 语义各不同

① `standalone-container-registry`（roles/standalone-container-registry + playbooks/container/standalone-container-registry.yml）：Docker registry 直装，Slurm 路径默认开（slurm-cluster.yml:27-30 落 slurm-master）、K8s 路径落 kube_control_plane（k8s-cluster.yml:66）；② `k8s-internal-container-registry`：helm chart 部署进集群内；③ `nginx-docker-registry-cache`（server/client 两个 playbook，slurm-cluster.yml:32-38）：NGINX 中间人代理缓存上游镜像——roles/nginx-docker-registry-cache 的信任根可预生成（`nginx_docker_cache_ca` 变量指向 gen-ca.sh 产物），避免每次部署换 CA 导致全集群重配证书。

### 监控：两条监控栈与 592 行单文件

K8s 侧有一份 592 行的单文件监控全家桶 `workloads/examples/k8s/services/prometheus-monitor.yml`：ClusterRole（L4）→ ServiceAccount → Deployment（L44）→ ConfigMap（L470）→ Service×3（L530/L544/L558）→ PVC（L579）全在一个 YAML 里，配套部署脚本是 `scripts/k8s/deploy_monitoring.sh`（291 行）。Slurm 侧监控走 role 组合（prometheus/grafana/alertmanager/三 exporter，slurm-cluster.yml:97-125），接入模式是 `roles/prometheus/templates/prometheus.yml.j2:19-21` 的 file_sd 目录自注册——新 exporter 只需往 `{{ prometheus_cfg_endpoint_dir }}` 落一个片段 yml 即被纳管，无需改 Prometheus 配置。仓内唯一 Go 服务 prometheus-slurm-exporter（main.go）是纯标准库手写 HTTP exposition：L183 `metricsBuilder` 结构体、L187-188 手写 `# HELP/# TYPE` 行、L28 所有命令执行带 context 超时；Dockerfile 用 CGO_ENABLED=0 静态编译使二进制可跨基础镜像搬运。

### kubespray 补丁层与 Kubeflow 线

`config.example/group_vars/k8s_cluster.yml` 是对 kubespray 上游 bug 的定点补丁集：L7-8 `kubectl_localhost: false`（附 kubespray#5059 链接）、L85-86 `nerdctl_extra_flags: " --insecure-registry"`（#9956/#8529），**升级 kubespray 时须逐一复核**。Kubeflow 线在 scripts/k8s/：deploy_kubeflow.sh 的 get_opts（L44）支持 --version/--workspace，poll_url（L215）轮询代替固定 sleep 等就绪；update_kubeflow_config.py:28 直接 requests 解析 `api.ngc.nvidia.com/v2/repos` 拿最新 NGC 镜像 tag，PyYAML 读写同一 yaml 完成镜像引用替换。

---

## 6. 存储网络：NFS 双形态、mofed 用户态与占位 role

### NFS：一个 role，两种形态

roles/nfs 是"单 role 双形态"范本：`tasks/main.yml` 先按 OS include_vars（L4-15）并装包（Debian 装 nfs-common L21-26 / RHEL 装 nfs-utils L28-33）、配 NFSv4 idmapd 域（L41-47），随后 **L49-52 `include_tasks: server.yml` when `nfs_is_server`、L59-62 `include_tasks: client.yml` when `nfs_is_client`**——同一 role 内按变量分流服务端/客户端形态。导出表模板 exports.j2 尾部（L11-13）就一个 `{% for export in nfs_exports %}` 循环。谁当服务端由编排层决定：Slurm 默认 `slurm-nfs[0]`（slurm-cluster.yml:62），group_vars 里覆写为 `nfs_server_group: "slurm-master[0]"`（config.example/group_vars/slurm-cluster.yml:98）——/home 与 /sw 共享区默认从首个 master 导出。外围角色链：cachefilesd（FS-Cache 缓存）、autofs 按需挂载、move-home-dirs（tasks/move_users.yml:24-37 先建临时用户再切 `ansible_user` 身份——"当前登录用户不能搬自己的 home"是 user.move_home 的硬约束，L57 临时身份执行是 Ansible 改动执行者自身环境的经典解法）。

### mofed：全量装与用户态装的分层

InfiniBand 驱动 roles/mofed 从 Mellanox 官网拉 MLNX_OFED tgz（defaults/main.yml:7），L57-62 `yes | ./mlnxofedinstall {{ mofed_install_flags }}` 安装，默认 flags `--all --without-fw-update`（L9）。**用户态边界出现在 molecule 场景**：`roles/mofed/molecule/default/molecule.yml:19` 注入 `--user-space-only`——容器内没有内核栈，只能装用户态组件跑测试，这同时示范了 flags 变量对真实集群的裁剪能力。GPUDirect RDMA（nv_peer_mem）由 roles/nvidia-peer-memory 承担，在 slurm-cluster.yml:153 收尾。

### K8s CSI 与"空壳占位"role

- **netapp-trident**（374 行，K8s CSI 主力）：tasks/main.yml L4-6 helm repo add、L16-18 `helm upgrade --install --wait`，随后按需创建 trident-installer 工作目录（L20-24）下载安装器配 backends/StorageClasses/volume snapshots；专属 group_vars 在 config.example/group_vars/netapp-trident.yml；轻量替代是 nfs-client-provisioner（k8s-cluster.yml:309 引入）。
- **roce_backend 是"非典型 role"**：`tasks/main.yml` 全文 2 行、零任务（空壳占位），真正的逻辑在 allhosts.yaml/k8smaster.yaml 等分流文件里**由外部 playbook 直接调用**——k8smaster.yaml 用 k8s 模块部署 SR-IOV device-plugin/CNI 时直接 `lookup('url', ...)` 拉远端清单（L38/L46，ConfigMap 用 lookup('template') 渲染 config_dp.j2，L28），master 节点 run_once 幂等。读这个 role 别从 main.yml 入手。
- 命名解析：deepops_hosts（templates/etc_hosts.j2 渲染 /etc/hosts）与 dns-config（resolv.conf.j2）是 hostname→IP 的两个平面；kerberos_client/nis_client 提供身份认证接入（各自 molecule 场景照抄同源模板，nfs 的 molecule 注入过与场景无关的 kerberos 变量属复制痕迹，无实际影响）。

---

## 7. 工具与验证：从裸金属到验收闭环

### maas_deploy.sh：bash×python 混合的裸金属供给

集群从零建站的起点是 `scripts/maas_deploy.sh`——540 行、**21 个函数**（实证计数）：load_config:49 / parse_args:118 / maas_auth_header:163 / maas_get:173 / maas_post:178 / get_system_id:184 / get_status:196 / get_ip:205 / get_machine_info:227 / wait_for_status:246 / wait_for_ssh:269 / ensure_tag_exists:295 / add_tag_to_machine:301 / remove_tag:308 / clear_test_tags:314 / do_apply_profile:323 / resolve_machines:369 / do_status:384 / do_release:406 / do_deploy:438 / main:527。实现特征：bash 里内嵌 `python3 -c` 解析 JSON、curl 带 OAuth 头裸调 MAAS API 而不依赖 maas CLI。动态 inventory 由 `scripts/maas_inventory.py` 提供（ansible.cfg:5 把它注册为第二 inventory 源）；API 端点与 key 配置模板在 `config.example/maas-inventory.yml:12-16`（`http://<maas-server>:5240/MAAS/api/2.0`，环境变量优先于文件）。MAAS 仓库源还有版本分支逻辑：config.example/group_vars/all.yml:256 按 Ubuntu 24.04 切 ppa:maas/3.7 与 3.5。

### HPL 实验链：生成器范式

`workloads/bit/hpl/launch_hpl_experiment.sh`（488 行）是"生成器脚本"范本：把 syscfg + HPL.dat + 提交脚本拷进**每个实验独立的 WORKDIR** 再 sbatch，作业自包含、不依赖共享目录状态。调优矩阵在 hplfiles/（**41 份** HPL.dat 变体，实证计数，按机型×节点规模命名如 HPL.dat_128N_dgxa100_80G），配套 calculate_N.py 算问题规模、syscfg-dgxa100-80gb.sh 等按机型定亲和、format_results.py/verify_hpl_experiment.py 收结果。关键注释在 submit_hpl.sh：**不能靠 dirname 定位脚本**——批处理系统可能把脚本拷到 /tmp 执行，HPL_DIR 必须由启动器预设。

### validation 三件套：human/json 双输出契约

`scripts/validation/` 下三个工具共享同一输出契约：默认人读（每检查一行），`--json` 时打印单个 JSON 对象供 CI 判定。

- `validate_slurm.py`（228 行）：契约写在 docstring（L8），L113 定义 `--json`，GPU 检查是真实提交作业（L192-195 `srun --gpus=1 --time=5 ... nvidia-smi --query-gpu=name,driver_version`），L207-208 输出 JSON——AGENTS.md:47 要求 `ok:true` 且 `gpu_job_ok:true`；
- `validate_k8s.py`（280 行）：L7 起 CUDA smoke pod（SMOKE_POD=`deepops-validate-cuda`，L25），run_cuda_smoke 在 L120，AGENTS.md:55 的 `--cuda-smoke` 门槛即 `cuda_smoke_ok:true`；
- `deepops_doctor.py`（244 行）：部署前体检，L77 `--json`，L7 `--remote` 追加 SSH 可达性与 GPU 可见性检查（AGENTS.md:32-35：doctor 不过禁止跑集群 playbook）。

三工具还有单元测试 `scripts/validation/tests/test_validation_scripts.py` 钉住解析器行为。CI 侧另有 `scripts/deepops/check-template-syntax.py`：用 Environment 造桩 filter 做"解析不渲染"的 Jinja 静态检查——改模板语法不破坏解析的守卫。

---

## 8. 新人上手：skills、Jenkins 与虚拟沙箱

### skills/：给 AI agent 的部署知识库

`skills/` 下 6 个 SKILL.md 把运维流程写成 AI 可执行工作流（含前置条件、命令、预期输出、失败分支）：**deploy-airgapped（999 行，最大）**、deploy-k8s-gpu-cluster（72 行）、deploy-slurm-cluster（72 行）、diagnose-driver-install（82 行）、provision-with-maas（252 行）、validate-gpu-cluster（54 行）。deploy-airgapped 的 frontmatter（L1-5）description 完整覆盖"断网/限出口/离线场景部署+验证"场景；正文 L30-31 有一条重要负向指令——**不要跑 `scripts/airgap/build_offline_cache.sh`**，它调用的 `playbooks/airgap/build-offline-cache.yml` 已从仓里删除，镜像构建须按文档手工做。仓库还有 `.claude/skills/test-playbooks.md`（仓内 Claude skill）——这个仓把自己同时当人类运维手册和 agent 知识库来维护。

### Jenkins：4 条流水线 × 31 个验证脚本

`workloads/jenkins/` 有 4 个 Jenkinsfile（Jenkinsfile 主线 / Jenkinsfile-matrix / Jenkinsfile-nightly / Jenkinsfile-multi-nightly）+ **31 个脚本**（实证计数：scripts/ 目录 31 个脚本文件）。全部脚本共用 `jenkins-common.sh`：L6-9 定义 GPUDATA 环境变量格式（Jenkins GPU 锁分配结果，单卡 `"3-0x86"`、双卡 `"3-0x86,2-0x85"`），L19-20 校验非空，L31-33 cut 解析出 GPU 序号与 BUS ID。脚本覆盖 test-slurm-gpu.sh / test-kubeflow.sh / test-monitoring.sh / test-spack-install.sh / test-rsyslog-{slurm,k8s}.sh 等真实集群 E2E。注意 molecule CI（.github/workflows/molecule.yml）用 `ANSIBLE_ROLES_PATH` 同时指向 roles/galaxy 与仓内 roles，先装 roles/requirements.yml 再逐角色 molecule test；依赖 systemd 的角色（slurm/nis_client/rsyslog_*）在真实 MAAS VM 上端到端测——这正是 tests/slurm-epilog/ 存在的原因。

### config.example：拷贝即用的配置面

`config.example/`（18 个文件）是唯一合法模板源：group_vars 四组（all.yml / k8s_cluster.yml / netapp-trident.yml / slurm-cluster.yml）+ helm values 六份（monitoring.yml 87 行 / monitoring-no-persist.yml / metallb×2 / dcgm-exporter / rapids-dask）+ inventory（L11 `[all]` 起，含 kube_control_plane/etcd/kube_node/k8s_cluster 与 slurm-master/slurm-nfs/slurm-node/slurm-metric/slurm-login/slurm-cluster 双栈分组）+ host_vars/gpu01 + env.sh + maas-inventory.yml + nvidia-mig-config.yml + playbooks/example.yml。all.yml 是"文档式默认配置"：可选键几乎全注释态只展示形态，实际启用仅 chrony/用户/驱动分支/Enroot 等少数；enroot_rpm_packages（L200-202）用 Jinja2 版本比较在 el7/el8 制品间切换规避上游停发 el7。**铁律：永远 cp -r config.example config 后改自己的 config/，不直接改 example**（AGENTS.md:18-19；config/ 被 gitignore）。变量覆盖链由 `scripts/common.sh` 串起：L12 `DEEPOPS_CONFIG_DIR` 默认仓根 config/，L13-16 缺失仅告警不报错，L19 source env.sh 实现版本化覆盖，L24-25 `git describe` 推导 DEEPOPS_VERSION。

### 版本窗口与虚拟沙箱

`scripts/setup.sh:15-16` 用双变量钉 Ansible 版本窗（`ANSIBLE_VERSION=10.7.0` / `ANSIBLE_TOO_NEW=11.0.1`，全部可环境变量覆盖，L102 做比较判定）。本地全链演练走 `virtual/`：**18 个 Vagrantfile**（centos7/8 + ubuntu18.04/20.04/22.04 六系 OS × {基础, -full, -large-slurm} 三形态，实证文件计数），vagrant_startup.sh:136-140 按环境变量组合选择，三份 inventory（virtual_inventory / _full / _large_slurm）对应三拓扑。`virtual/cluster_up.sh:27-38` 是沙箱入口：export DEEPOPS_CONFIG_DIR 指向 virtual/config，默认清空重建（rm -rf 后 cp config.example + 按形态换 inventory）并清陈旧 fact 缓存——**这条流程同时演示了 fact 缓存 86400 带来的陈旧数据坑**。新人的完整闭环：vagrant 沙箱跑通 → deepops_doctor --json → 目标 inventory → 两条黄金路径之一 → 对应 validator 的 `"ok": true`。

---

## 附：口径勘误（本文实证 vs 此前口径）

- slurm-cluster.yml import_playbook 数：**31**（此前口径 30）；
- roles/ 角色目录：**51**（此前口径 57，roles/ 除 requirements.yml 外实证 51 个目录）；
- Jenkins 脚本：**31**（此前口径 20；workloads/jenkins/scripts/ 实证 31 个脚本 + files/ 目录）;
- HPL.dat 矩阵：**41**（此前口径 44；hplfiles/ 实证 41 份）；
- Vagrantfile 变体：**18**（此前口径 12；virtual/ 实证 6 OS × 3 形态）；
- "monitoring 592 行"：确指 `workloads/examples/k8s/services/prometheus-monitor.yml`（592 行单文件全家桶），非 prometheus role（roles/prometheus 全部任务+模板仅 112 行）。
