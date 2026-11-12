# 09 · 五大 compute 驱动横评：注册表、探测优先级与隔离形态

## 一、角色定位

compute 驱动是 OpenShell"沙箱跑在哪"的可插拔答案。全部驱动实现同一个 proto 契约：`compute.v1.ComputeDriver` gRPC 服务（CreateSandbox/Start/Stop/Delete/Watch/EnsureWorkspace 等全集，vm/driver.rs 的 import 面可见其广）。五个驱动按隔离强度与平台分野：**docker**（本地容器）、**podman**（本地 rootless 容器）、**kubernetes**（集群 Pod）、**vm**（microVM 硬隔离）、**mxc**（Windows AppContainer，Microsoft MXC 隔离会话）。AGENTS.md 架构表对 vm 的定语是"Standalone libkrun-backed ComputeDriver subprocess（自带 rootfs 与运行时）"，对 mxc 是"In-process Windows AppContainer and isolation-session compute backend"——一句话点破两者的进程形态差异。

## 二、内部结构

**注册与选择机制**（server/lib.rs）。`ComputeDriverRegistry`（:1365，BTreeMap<String, ComputeDriverRegistration>）文档自比 sqlx 的 Any 驱动注册表："安装显式发生在二进制组装边界，运行时选择是泛型的"。`ComputeDriverRegistration`（:1276-1283）= 名字 + detection_priority + 探测闭包 + 工厂。`ComputeDriverFactory` trait（:1253-1272）两个方法：`validate_config`（纯预检，不开传输不碰状态）与 `build`。产物 `ComputeDriverInstance`（:1244-1249）两态：`InProcess`（驱动活在网关进程里）或 `ManagedRemote`（网关拉起并拥有驱动子进程）。

**五驱动档案**（行数均 src 下 .rs 总量）：

| 驱动 | 主结构 | 进程形态 | 客户端技术 | 探测函数 |
|---|---|---|---|---|
| vm | `VmDriver` crates/openshell-driver-vm/src/driver.rs:661 | ManagedRemote | libkrun FFI + QEMU 兜底 | 无（priority=u16::MAX） |
| docker | `DockerComputeDriver` crates/openshell-driver-docker/src/lib.rs:330 | InProcess | bollard | `is_available` crates/openshell-driver-docker/src/lib.rs:839 |
| podman | `PodmanComputeDriver` crates/openshell-driver-podman/src/driver.rs:110 | InProcess | 自研 HTTP client（client.rs，无成熟 Rust SDK） | `is_available` crates/openshell-driver-podman/src/driver.rs:389 |
| kubernetes | `KubernetesComputeDriver` crates/openshell-driver-kubernetes/src/driver.rs:685 | InProcess | kube-rs（Client+watcher） | env `KUBERNETES_SERVICE_HOST` |
| mxc | `MxcComputeBackend` mxc.rs:204 / `MxcComputeConfig` crates/openshell-driver-mxc/src/driver.rs:61 | InProcess（Windows-only） | 外部 `wxc-exec.exe` + ETW | 无（priority=u16::MAX） |

vm 驱动是重头：`driver.rs` 单文件 11459 行 + 全 crate 18532 行，`VmDriver`（:661-673）持有 rootfs 镜像缓存锁、vsock CID/GPU 库存、生命周期扩展注册表；`rootfs.rs`（1752 行）从 OCI 镜像制备 ext4 磁盘；`runtime.rs` 定义 `VmBackend::{Libkrun, Qemu}` 双后端（:23-26）——GPU 直通场景走 QEMU（`run_qemu_vm` 要求 gpu_bdf 与 vsock_cid，:61-68），普通场景走 libkrun 进程内 microVM；`lifecycle.rs`（1241 行）是 LaunchPlan/RestoreContext 生命周期扩展点；`ffi.rs`（202 行）裸包 libkrun C API。mxc 侧 `mxc.rs` 定义 MXC 配置 schema 版本 `"0.6.0-alpha"`（:21，配置 JSON base64 后喂给 `wxc-exec.exe`，默认路径 crates/openshell-driver-mxc/src/driver.rs:97）、mock 开关 `OPENSHELL_MXC_MOCK_WXC`（:31）；`policy_map/` 四文件负责策略到 AppContainer 能力的映射（loss.rs 专门记录"翻译损耗"）；`etw_consumer.rs`（2446 行）是 ETW→OCSF 审计消费器（见第 10 篇）。

## 三、外部连接

组装侧全部经 gateway/lib.rs `install_default_compute_drivers`（:47-65）——四家非 Windows 驱动注册优先级 kubernetes=100/podman=200/docker=300/vm=u16::MAX（:181-223）。mxc 走 Windows 专属分支（:68-76）。驱动之间共享的底座：`openshell-vfio`（GPU/PCI 直通准备）、`openshell-sandbox-backend`（boundary 协议，vm/driver.rs import）、`openshell-binary-identity`、各自 `isolation` 模块对接 `openshell-isolation-interface`（RFC 0012 的 IsolationBackend trait）。行为一致性由 `openshell-conformance` 场景注册表约束（跨驱动跑同一套生命周期/文件传输/策略场景）。另有三个**凭据驱动**（vault/db-credstore/kubernetes-secrets）名字像 compute 驱动但属完全另一条 CredentialDriver 线，别混。

## 四、数据流

以 CreateSandbox 为例：网关 grpc/sandbox.rs 收请求 → registry 解析出选中驱动 → InProcess 驱动直接 Arc 调用；vm 则不同——gateway 的 VmFactory.build（crates/openshell-gateway/src/lib.rs:400-427）先把空 grpc_endpoint 兜底成 `http(s)://127.0.0.1:{gateway_port}`，再 `vm::spawn` 拉起独立驱动子进程，返回 `ManagedRemote(endpoint)`——网关与 VM 驱动间也是走 gRPC，不是函数调用。vm 驱动内部：OCI 镜像拉取（oci_client）→ rootfs.rs 制备 root/overlay 双磁盘 → runtime.rs `run_vm` 起 libkrun/QEMU，vsock 做 host↔guest 通道（guest-cid 由 gpu.rs `allocate_vsock_cid` 分配，QEMU 侧 `vhost-vsock-pci` 挂 PCIe root port，crates/openshell-driver-vm/src/runtime.rs:128-131）→ 驱动经 boundary 协议与 guest 内监督器握手。kubernetes 驱动则把沙箱映射为 CRD/Pod，`watch_client` 双客户端分离 watch 与操作流（crates/openshell-driver-kubernetes/src/driver.rs:686-687），`resource_admission.rs` 处理配额拒绝的错误翻译（如把 "0/1 nodes are available: 1 Insufficient nvidia.com/gpu" 翻成人话提示）。podman 的探测是"socket 存在且响应"（socket_discovery.rs，systemd 单元用 Wants 而非 Requires，socket 重启窗口要容忍，crates/openshell-driver-podman/src/driver.rs:444-446 注释）。

## 五、设计决策

1. **优先级编码产品默认**：100/200/300 让"有集群用集群、退而 podman、再退 docker"全自动；vm 永远不自动选——microVM 的启动成本与运维复杂度必须由运维显式选择。
2. **统一 gRPC 契约让进程形态自由**：同一 proto 服务既可 InProcess（零开销）也可 ManagedRemote（vm 的崩溃隔离 + 版本解耦），网关代码不感知差异。
3. **探测是"响应性"而非"存在性"**：docker/podman 的 `is_available` 都调 `detect_socket()` 真连 socket，避免"文件在但守护进程死"的假阳性。
4. **mxc 的诚实损耗账本**：Windows AppContainer 能力模型与 OpenShell 策略语言不一一对应，`policy_map/loss.rs` 把翻译不过去的部分显式记成 loss 而非静默丢弃——跨平台策略等价性的负空间也进了一等公民。
5. **vm 自带 rootfs/runtime**（embedded_runtime.rs）：驱动子进程不依赖宿主发行版，嵌入 guest 内核与 supervisor，配合 procguard.rs（197 行）守护进程边界。

## 六、新人提示

- **别把 11459 行的 vm/driver.rs 当普通文件读**：先读 lib.rs 导出面 + lifecycle.rs 类型，再按 CreateSandbox 调用链切。
- **compute 驱动 ≠ 凭据驱动**：registry 里五个 compute；vault/kubernetes-secrets/db-credstore 是另一条线。
- **Windows 上 docker/k8s/podman/vm 四驱动的注册还在**但工厂只返回"unsupported on Windows"（crates/openshell-gateway/src/lib.rs:78-102）——注册表里有名字不等于可用，`installed_driver_names()` 在 Windows 测试里会列出它们（:544-561）。
- **mxc 的 ProcessContainer 是"真 default-deny"**（crates/openshell-driver-mxc/src/driver.rs:42 注释原话），但隔离语义与 Linux 侧不同——对照 conformance 场景矩阵看哪些场景在 Windows 被标记跳过。
- k8s 配置有两个环境变量后门：`OPENSHELL_K8S_WORKSPACE_DEFAULT_STORAGE_SIZE`/`OPENSHELL_K8S_WORKSPACE_STORAGE_CLASS`（crates/openshell-gateway/src/lib.rs:275-280），改行为时记得这里还有一层注入。
- 本地驱动（docker/podman/vm）+ 网关 TLS ⇒ 必须配 guest_tls_ca，`validate_local_driver_guest_tls`（crates/openshell-gateway/src/lib.rs:468-479）会在启动时挡下。
