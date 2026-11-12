# 02 USE_CUDA 条件构建与拓扑准备：Makefile、ARP 卫生与 PCI 亲和

> 对应 tour 第 2、3 步「构建入口：USE_CUDA 开关」「机器准备：ARP 卫生与 PCI 拓扑亲和」。行号锚均对 HEAD `a99d506` 核实。

## 一、角色定位

这是三条"代码之外的代码"：Makefile 决定同一份源码编译出什么样的二进制（带不带 CUDA、带不带延迟打点），arp_announce_conf.sh 治多宿主 RoCE 机器的 ARP 应答错乱，map_pci_nic_gpu.sh 回答"哪块 GPU 离哪块网卡最近"。GPU Direct RDMA 跑不通的故障里，构建形态配错和拓扑选错占大头——README.md:44-50 把这两脚本列进 Installation Guide 而非使用文档，正说明它们是**运行前置条件**而非可选工具。三者共同守着一条铁律：GPU Direct 的性能根基不在软件里，而在 PCIe 拓扑与网络卫生里。

## 二、内部结构

**Makefile（54 行）只有两个开关一个骨架**。开关一 `USE_CUDA`（Makefile:5-13）：为 1 时追加两套 CUDA include 路径（:6-7）、在 CFLAGS 里定义 `-DHAVE_CUDA`（:8）、链接表多出 `-lcuda`（:9）；否则 CFLAGS 仅 `-I$(IDIR) -g`（:11），LIBS 只有 rdmacm/ibverbs/mlx5 三件（:12）。开关二 `PRINT_LAT`（:15-19）：为 1 时追加 `-DPRINT_LATENCY`。骨架是三条公共目标文件 `gpu_direct_rdma_access.o gpu_mem_util.o utils.o`（Makefile:30-32），分别加 server.o/client.o 链成两个可执行文件（:41-45），产物都落在 obj/ 目录（:34-35、:47-48）。注意 DEPS 把五个本地头全部列为依赖（:24-28），任何一个头改动都会触发全部重编——对小仓是正确的保守策略。

**arp_announce_conf.sh（63 行）**：外壳两层循环——遍历 `/sys/class/infiniband/` 下每个 HCA（arp_announce_conf.sh:40-42）、每 HCA 的每个 port（:46），只对 `link_layer == "Ethernet"` 的 RoCE 端口（:50）取其关联 ndev（:51，读 `gid_attrs/ndevs/0`），用 `ip link` 判 UP（:52）后对该 ndev 打两条 sysctl（:55-56）：`arp_announce=1`（用最优本地源地址发 ARP）与 `arp_ignore=2`（只应答目标地址完全匹配的 ARP 请求）。

**map_pci_nic_gpu.sh（85 行）**：同样的两层循环骨架（map_pci_nic_gpu.sh:44-50），对每个 UP 的 RoCE ndev 取 IP（:52），然后做三步拓扑解算——readlink 解出 HCA 自身 PCI 设备路径（:57-58）、再 `dirname` 两次上溯到上级 bridge（:59-60）；遍历 `/sys/class/pci_bus/`（:63），对每条总线同样上溯三级到 bridge（:65-68），bridge 名相等即同桥（:70）；跳过 HCA 自身所在总线（:71-74）后，`lspci -D -s $pci:00.0` 打印该总线上的设备（:75-78），输出 `IP (mlx5_12) is near 0000:b7:00.0 ...`（:79）——这一行就是 client `-u` 参数的直接来源（README.md:78-88）。

## 三、外部连接

- **Makefile → gpu_mem_util.c**：`-DHAVE_CUDA` 直接决定 gpu_mem_util.c 里 161 行 CUDA 代码（:66-226）是否存在——include cuda.h 本身就在 `#ifdef HAVE_CUDA` 内（:51-54）。不开 USE_CUDA 编 server，链接表没有 -lcuda（Makefile:12），符号级自洽。
- **Makefile → gpu_direct_rdma_access.c**：`-DPRINT_LATENCY` 激活该文件两套分支——CQ 从 ibv_cq 换成 ibv_cq_ex 带 completion timestamp（gpu_direct_rdma_access.c:104-108、:563-574），submit/poll 路径埋入三段时钟采样（:906-917、:997-1004、:1435-1522）。
- **两脚本 → sysfs 树**：都消费 `/sys/class/infiniband/<dev>/ports/<port>/` 下的 link_layer、gid_attrs/ndevs/0（两脚本 :48/:51）；map 脚本另消费 `/sys/class/infiniband/<dev>/device` 软链与 `/sys/class/pci_bus/`（map_pci_nic_gpu.sh:57、:63）。
- **README → 两脚本**：安装指南第 4 步点名跑 arp 脚本（README.md:44-50），运行指南第一步就是 map 脚本输出（README.md:75-84）——脚本输出直接进入 client 命令行。
- **sysctl → 内核 ARP 栈**：两条 sysctl 是运行时全局设定（-w），重启即失效——样例没做持久化，部署时要进 systemd 或 sysctl.d。

## 四、数据流

构建侧的"数据流"是宏定义的传播：`make USE_CUDA=1` → `-DHAVE_CUDA` 进所有 .c 的编译（Makefile:8）→ gpu_mem_util.c 的 init_gpu/get_gpu_device_id_from_bdf/free_gpu 三个静态函数被编入（:113-225）→ work_buffer_alloc 的 GPU 分支可用（:238-239）→ client 的 `-u` 生效。反向 `make`（server 机器）时同一 work_buffer_alloc 走 CPU 分支（:247-255，memalign 按 sysconf 页大小对齐），CUDA 符号全不存在。

拓扑侧的数据流是一次"探测→选卡→绑定"：map 脚本读 sysfs 算出 (IP, NIC, GPU BDF) 三元组 → 人工挑一条 → client 以 `-a IP -u BDF` 启动 → gpu_mem_util 按 BDF 定位 CUDA 设备序号（gpu_mem_util.c:113-154），而 `-a IP` 进入 `rdma_open_device_client` 后经 rdma_cm 的 `rdma_bind_addr` 绑定到同一块 HCA（gpu_direct_rdma_access.c:262）——**IP 与 BDF 必须出自脚本同一行输出**，否则 GPU 与 NIC 不同桥甚至不同机，GPU Direct 退化为跨根复合体的低效路径。

## 五、设计决策

- **条件编译而非条件运行**：CUDA 依赖用编译期开关而非运行时 dlopen，server 机器因此完全不用装 CUDA Toolkit——样例的目标读者是"存储侧工程师也要能编"，这个取向把依赖传染掐死在链接期。
- **include 路径写死两个候选**（Makefile:6-7）：cuda-10.1 精确路径加一个通用软链路径，是 2019 年 CUDA 装机现实的妥协；现代环境多半要手改。
- **ARP 卫生只治 RoCE**：脚本对 InfiniBand 链路层（link_layer=IB）整段跳过（两脚本 :50）——LID 路由不碰 ARP，这是 IB 与 RoCE 分叉处最常见的环境差异点。
- **同桥判断用 sysfs 层级而非 lspci -t 解析**：readlink+dirname 数出 bridge 层级（map_pci_nic_gpu.sh:57-68），避开了 lspci 树形输出的解析脆弱性；代价是 HCA 路径上溯两级、总线路径上溯三级的不对称（HCA 的 device 节点比 pci_bus 节点深一层），读懂脚本必须先看懂这两条不同长度的路径。
- **PRINT_LAT 默认关闭**：延迟打点要在 submit 路径插两次 `ibv_query_rt_values_ex`（gpu_direct_rdma_access.c:912、:998），影响被测路径——性能采样与性能本身互斥，样例选择默认干净。

## 六、新人提示

1. **`make PRINT_LAT=1` 当前必编译失败**：rdma_poll_completions 的 PRINT_LATENCY 分支在 gpu_direct_rdma_access.c:1453 引用 `wc[i].wr_id`，但该分支内既无 `wc` 数组也无循环变量 `i`（CQE 的 wr_id 在 `rdma_dev->cq->wr_id`，:1447）——这条路径久未被构建验证，想用延迟统计得先修它。这是全仓最典型的"条件编译即盲区"实证。
2. **两脚本第一个位置参数都可传 dev 名**（两脚本 :39-42）：只调某块网卡时 `./map_pci_nic_gpu.sh mlx5_12` 可跳过全量扫描；`debug` 首参还能开 echodbg 打印中间量（:31-37）。
3. **map 脚本的"near"是同 bridge 不是同 switch**：上溯到的是 PCI-to-PCI bridge 一级；如果 GPU 与 NIC 同 switch 不同 bridge，脚本不报，但带宽已受损。要更细的亲和判断需看 `nvidia-smi topo -m` 一类工具。
4. **BDF 格式有校验**：gpu_mem_util.c:123-132 用 sscanf 严格要求 `bus:dev.func` 三段且 func=0，漏写 `.0` 直接报错退出——README 示例里 `-u b7:00.0` 的域名段 `0000:` 可以省，是 sscanf 宽容性所致，但保持完整格式更稳。
5. **obj/ 目录与 clean**：产物在 obj/、可执行文件在仓根（Makefile:41-45），`make clean` 只删这两处（:53）；换编译形态（如 server 误用 USE_CUDA 编过）务必先 clean，否则 obj/ 里旧 .o 会带着 HAVE_CUDA 混进链接。
