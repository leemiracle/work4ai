# 讲透 nvidia-persistenced（全链索引）

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ | `deepwiki/`（20 页 TRUE_100） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`：137n/223e/7层/7步，validate 0 issues，fingerprints 44 文件@57f3a3f7 |
| onboarding | ✅ | `onboarding/ONBOARDING.md`（7 节，锚 45+） |
| explain | ✅ | `explain/` 3 篇（nvidia-persistenced.c / nvidia-numa.c / init/install.sh） |

**定位**：NVIDIA Linux 驱动持久化守护——持有每台 GPU 的 libnvidia-cfg 句柄使驱动常驻初始化态，附带 GPU NUMA 内存上下线（memory-hotplug）与 UVM persistence。C99 + libtirpc，约 1 万行/44 文件，版本 615.78.08（version.mk:1）。

## 源码级勘误（均经行号核实，vs 上游文档/DeepWiki/直觉认知）

1. **"All RPC operations require root" 不成立（DeepWiki 2.2 勘误）**：DeepWiki 页称所有 RPC 操作都要 root。源码中 `_nvpdIsClientRoot()`（command_server.c:37-53）只在三个 Set 入口被调（:64/:108/:131）；**`nvpdgetpersistencemode_1_svc` 不做任何凭据检查**（command_server.c:82-95）——任意本地用户可经 unix socket 查询任意 GPU 的 persistence 模式。
2. **command_server.c 注释复制粘贴错名**：command_server.c:78-80 的函数头注释写着 `nvpdsetpersistencemode_1_svc() - ... to get the persistence mode`，实际函数是 `nvpdgetpersistencemode_1_svc`（:82）——上游源码自身的注释 bug。
3. **rpcgen 不在构建期运行**：Makefile:80-81 的注释"rpcgen generates code..."易被读成构建时生成；事实是 RPC 三件（nvpd_rpc.h/nvpd_rpc_server.c/nvpd_rpc_xdr.c）全部**预生成入库**（README:11-13 明说，为消除目标机 rpcgen 依赖），仓库不含 .x 源文件，dist-files.mk:32-33 直接编译入库产物，Makefile:82-84 只是压这些生成代码的编译警告。
4. **非法命令行参数以 0 退出**：parse_options 的 default 分支打印错误后 `exit(EXIT_SUCCESS)`（options.c:188-190）——非法参数退出码是成功，依赖 $? 判错的脚本会漏。
5. **RPC 参数里的 PCI function 字段是装饰**：`get_device` 只匹配 domain/bus/slot（nvidia-persistenced.c:208-223），且建表时 `pci_info.function = 0` 硬编码（:702-703，注释明言 nvidia-cfg 不填该字段）。协议带 function（nvpd_rpc.h:37）纯粹为 API 完整性。
6. **V2 协议没有 Get**：nvpd_rpc.h:105-124 的 VersionTwo 只定义 SetPersistenceModeOnly/SetNumaStatus 两过程，GetPersistenceMode 仅存在于 V1；守护把 V1/V2 同时注册在同一 unix transport（nvidia-persistenced.c:758-763）。
7. **NUMA 上线命令是 online_movable 且倒序**：BRING_ONLINE_CMD="online_movable"（nvidia-numa.c:50，不是 "online"），上线循环从高端块号往低走（:357-374，引 patchwork 9625081：倒序才能落 Movable zone），下线才正序（:376-387）。
8. **systemd 停机兜底删整个运行时目录**：service 模板 `ExecStopPost=/bin/rm -rf /var/run/nvidia-persistenced`（init/systemd/nvidia-persistenced.service.template:34）——目录清理靠 init 系统兜底而非守护自身（守护只删自己 mkdir 的目录，nvidia-persistenced.c:911-916）。
9. **install.sh 的 -d 会吞掉其后的 -u**：-d 置 nvpd_user=""（install.sh:663），-u 处理被 `if [ "$nvpd_user" != "" ]` 守卫拦截（:651-652）——"卸载但保留指定用户"必须 `-d -u <user>` 且 -d 在前。

## 关键事实速查
- RPC：ONC RPC over AF_UNIX（/var/run/nvidia-persistenced/socket，nvpd_defs.h:35-38），NVPD_PROG=35006（nvpd_rpc.h:84），安全=SO_PEERCRED 查 uid==0（command_server.c:42-50）。
- ioctl 契约：NV_IOCTL_MAGIC='F'（nv-ioctl-numbers.h:33），NV_ESC_NUMA_INFO/SET_NUMA_STATUS=200+15/16（nv-ioctl-numa.h:44-45），黑名单地址上限 64（:47）。
- 构建：libtirpc≥1.0.1 硬依赖（Makefile:108-117），m4 合成 manpage（:177-182），输出进 `_out/`。
