# 讲透 nvidia-persistenced.c（守护进程主体，1043 行）

## 角色定位
本仓心脏：main 入口 + 全部设备状态管理 + daemon 化 + RPC 挂载。设备表 `devices`（:73）与全局静态量（pid/pid_fd/socket_fd/libnvidia_cfg，:69-76）都在此。函数覆盖"命令实现四件（nvPdSet/Get/ModeOnly/NumaStatus）+ setup 三件 + daemonize/shutdown + UVM 轮询"。

## 内部结构
- 命令层：`nvPdSetDevicePersistenceMode`（:109）是复合命令——先 `set_device_mode`（:343，open/close 设备+UVM）再 `set_device_numa_status`（:427），失败互回滚（:134-136）；ModeOnly（:150）与 NumaStatus（:171）是拆出来的单因子变体。
- 设备查找 `get_device`（:208）：线性扫 domain/bus/slot 三元组，**function 不参与匹配**。
- 生命周期：`daemonize`（:799，fork+init pipe 双进程握手）→ `setup_nvidia_cfg_api`（:606，dlopen+dlsym）→ `setup_devices`（:668）→ `setup_rpc`（:734）→ `init_complete`（:230）→ `svc_run`（:1033）；`shutdown_daemon`（:487）逆序回收。

## 外部连接
上连 command_server.c（RPC svc 直调 nvPd*）；下连 libnvidia-cfg.so.1（函数指针表 nv_cfg_api，:78-84）与 nvidia-numa.c（nvNumaOnline/OfflineMemory）；syslog 经 nvidia-syslog-utils.c 的 syslog_device/SYSLOG_DEVICE_VERBOSE 打 PCI 前缀。

## 数据流
请求流：RPC 参数(device+mode) → get_device 查表 → set_device_mode 调 nvCfgOpenPciDevice（:386）拿句柄存回 device->nv_cfg_handle → NUMA 状态机推进。UVM 分支：open 成功且命令行开了 --uvm-persistence-mode（:397）→ `enable_uvm_persistence_mode`（:290）轮询 nvCfgEnableUVMPersistence，NV_ERR_NVLINK_FABRIC_NOT_READY 时 sleep(1) 重试，30s 超时（fabricProbeTimeoutMs=30000，:292）只 WARNING 不 fail。

## 设计决策
① 先模式后 NUMA 的顺序被注释钉死（:123-128）：online 需 libnvidia-cfg 先建设备节点、offline 需先释放句柄；② dlopen 而非链接 libnvidia-cfg——守护可独立于驱动打包发布；③ PID 文件 lockf 排他（:964）而非 O_EXCL，崩溃自动释放；④ 自建目录才自删（remove_dir，:911-916），权限不对称场景显式降级为 notice（:566-577）。

## 新人提示
读代码从 main（:998）正向走一遍最快。注意两个易错点：非 root 降权后删不掉运行时目录是预期而非 bug；get_device 忽略 function（:208-223）+ setup_devices 硬编码 function=0（:702-703），RPC 传 function 只是协议完备性装饰。
