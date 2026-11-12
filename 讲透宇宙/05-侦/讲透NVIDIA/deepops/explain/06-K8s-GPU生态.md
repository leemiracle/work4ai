# 06 · K8s-GPU 生态：GPU Operator、SR-IOV 与三套 registry

## 角色定位

K8s 线的 GPU 生态由三平面组成：算力（nvidia-gpu-operator 角色 helm 部署 GPU Operator 管 driver/toolkit/DCGM/MIG）、网络（nvidia-network-operator 角色 + SR-IOV 策略）、镜像（三套 registry 角色覆盖离线/加速/集群内）。config.example/group_vars/k8s_cluster.yml 是变量契约层，一半内容是对 kubespray 上游 bug 的定点补丁。

## 内部结构

GPU Operator：roles/nvidia-gpu-operator/tasks/k8s.yml 开头注释（`:2-5`）保留绕行历史——Ansible helm 模块当时损坏（ansible/ansible#57897），故 helm 全套 command 直调并 `changed_when: false` 压噪音（:6-16），一条命令 --set 出 driver.version/mig.strategy 等开关。main.yml:2-6 对 DGX 预装环境关闭 driver 只保 toolkit。网络平面走对照路线：roles/nvidia-network-operator/tasks/main.yaml 用 `kubernetes.core.helm/k8s` 模块（:15-29 helm、:31-35 NicClusterPolicy），代价是先 `pip3 install openshift`（:10-13）——有无 python 库依赖决定"模块 or 直调"两种姿势。SR-IOV 链：:65-67 逐 `intf_resources` 建 SriovNetworkNodePolicy（sriovnetworknodepolicy.yaml:4-22，apiVersion `sriovnetwork.openshift.io/v1`），:69-71 建 IB attachment，:37-47 轮询 nv-ipam CRD 再建 IPPool（:49-63）；values.yaml:8 开 sriovNetworkOperator。

## 外部连接

k8s-cluster.yml 的接缝：`:4-6` 注释定调"非 docker 运行时即启用 GPU Operator"，`:109-112` import kubespray cluster.yml；宿主机预装分支（:160-178）在 `gpu_operator_preinstalled_nvidia_software` 时直装 driver+nvidia-docker。k8s_cluster.yml 的补丁带：`kubectl_localhost: false`（:7-8，kubespray#5059）、`kubelet_flexvolumes_plugins_dir` 复位（:19-21，修 Rook）、containerd insecure registry 因 kubespray#9956 整段注释（:74-79）、`nerdctl_extra_flags: --insecure-registry`（:85-86，#8529）。三 registry：①standalone-container-registry（standalone-container-registry.yml:2-9 先 import docker.yml 再挂 role），Slurm 线落 slurm-master（slurm-cluster.yml:28）、K8s 线落 kube_control_plane（k8s-cluster.yml:66）；②nginx-docker-registry-cache 分 server/client（slurm-cluster.yml:31-41，默认 slurm-cache/slurm-node 组），server.yml 支持 `nginx_docker_cache_ca` 预生成信任根（:20-34）免得换 CA 全集群重配证书；③k8s-internal-container-registry——同款 helm bug 绕行（tasks/main.yml:1-5、:25-29），对应 k8s_cluster.yml:70-72 的 `registry.local:31500` insecure registry。

## 数据流

GPU 请求流：容器 → operator 部署的 nvidia-container-toolkit（节点级）→ device plugin/GFD（operator 内置，k8s-cluster.yml:291-300 的独立 GFD/plugin 仅在 operator 关闭时部署）。镜像流分流：完全离线用 standalone、拉取加速用 nginx cache、集群内共享用 internal registry。RDMA 流：SR-IOV VF→nv-ipam 分 IPPool 块→network attachment 接入 Pod。

## 设计决策

① "bug 注释+绕行+changed_when"三元组是仓库惯用式，issue 链接入码供升级复核。② GPU Operator 优先于手拼 device plugin——`deepops_gpu_operator_enabled`（k8s_cluster.yml:25）一条变量切换整条栈。③ 三 registry 不合并——信任模型不同：standalone 要自签体系、cache 要 CA 预置、internal 假定集群内可信。

## 新人提示

升级 kubespray 后把 k8s_cluster.yml 里所有带 issue 链接的变量重测一遍。GPU 排障顺序：`kubectl get pods -n gpu-operator` → 宿主机 `nvidia-smi` → node feature discovery 标签。搭 SR-IOV 前确认网卡 pf_name（roles/nvidia-network-operator/vars/main.yaml:4，即开 SR-IOV 的物理口）且交换机侧已配 RoCE。
