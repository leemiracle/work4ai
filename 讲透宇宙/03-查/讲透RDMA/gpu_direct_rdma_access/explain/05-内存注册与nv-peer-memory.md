# 05 内存注册与 nv-peer-memory：pin 住显存、七段描述串与 AH 缓存

> 对应 tour 第 8 步「pin 住显存：MR 注册、描述串与 AH 缓存」。锚均对 HEAD `a99d506` 核实。

## 一、角色定位

GPU Direct 的核心魔法发生在三个函数里：`rdma_buffer_reg` 让 NIC 获得"直接 DMA 这块显存"的钥匙（rkey），`rdma_buffer_get_desc_str` 把钥匙连同地址、DCTN、GID 序列化成一条可上链的凭据串，`rdma_create_ah_cached` 在 server 侧把对端地址信息编译成可复用的地址句柄。三者共同回答一个问题：**client 怎么把"我的显存"变成 server 硬件能理解的目标**。操作系统背景是：GPU 显存页默认不可被 PCIe 外设 DMA——`ibv_reg_mr` 注册显存之所以能成，全靠 nv_peer_memory 内核模块（README.md:42）在 reg 时经 get_user_pages 路径把 GPU 页 pin 成物理页并建立 IOMMU/NIC 可见映射；没有它，本篇第一个函数必然在 :1170 失败并打出 "Couldn't register GPU MR"（:1172）。

## 二、内部结构

`rdma_buffer_reg`（gpu_direct_rdma_access.c:1155-1192）：calloc 一个 rdma_buffer（:1160）→以三位全开权限 `IBV_ACCESS_LOCAL_WRITE|REMOTE_READ|REMOTE_WRITE` 调 `ibv_reg_mr`（:1166、:1170）→回填 buf_addr/buf_size/rkey/rdma_dev 四字段（:1178-1181）→设备侧 `rdma_buff_cnt++`（:1182）。它对"显存还是主机内存"完全无感——addr 就是个 void*，第 3 篇的 64KB 对齐指针与 server 的 memalign 指针走同一条路；**差别全在内核侧**（谁替这页做了 pin）。`rdma_buffer_dereg`（:1195-1212）对称：ibv_dereg_mr（:1201）→cnt--（:1207）→free。cnt 是关闭闸门：close 时非零直接拒关（:1083-1087），防 MR 泄漏。

`rdma_buffer_get_desc_str`（:1242-1262）：先以 `sizeof` 字面量算死缓冲长度 `BUFF_DESC_STRING_LENGTH`（:1240 的七段模板串）——长度检查（:1244-1248）后一条 sprintf 输出六段：`addr(16位hex):size(8):rkey(8):lid(4):dctn(6):g(1)`（:1251-1257），第七段 gid 用 `gid_to_wire_gid` 直接追加在固定偏移后（:1259）。wire 格式的 gid 经 htonl 逐 32 位字序化（:1229-1236），对端 `wire_gid_to_gid` 以 ntohl 还原（:1215-1227）。返回 strlen+1 含结尾符（:1261）。

`rdma_create_ah_cached`（:1264-1305）：以**整个 ah_attr 结构**为键查 khash（kh_get，:1272）→未命中则 ibv_create_ah（:278）并 kh_put 入表（:1286），入表失败回滚销毁刚建的 AH（:1289-1292）→命中直接取值（:1299）。AH 缓存挂在设备对象上（:128），close 时 kh_foreach_value 统一销毁（:1135）。

## 三、外部连接

- **上游**：client.c:362 是 reg 的唯一带显存场景调用；server.c:273 同样 reg 自己的主机缓冲作 local_buf——注意 RDMA Write 的源端缓冲也必须是 MR。
- **下游**：desc_str 离开本库后经 client.c:370 的 get_desc_str 生成，pack 进 TCP 包（client.c:385），server 收回后填进 task_attr（server.c:345），最终由 `rdma_submit_task` 消费（见下）。AH 缓存的键材料（rem_gid/rem_lid）同样来自 submit 解析。
- **khash**：缓存数据结构是 klib 定制版哈希（include 于 :54），自定义 hash/equal 见 :178-190——第 6 篇专讲。
- **内核模块**：nv_peer_memory 不出现在任何 include 里，它是 ibv_reg_mr 的运行时依赖；README.md:40-42 给出装法。卸载/缺失时 reg 显存报错而 reg 主机内存照常——这是诊断"模块是否就位"的天然对照实验。

## 四、数据流

**client 侧（出）**：显存指针进 reg（client.c:362）→rkey 进 desc_str（:370）→串上链（:417）。
**server 侧（入）**：`rdma_submit_task`（:1342-1419）解析凭据：sscanf 按六段格式还原 addr/size/rkey/lid/dctn/is_global（:1363-1366），is_global 为真再 wire_gid_to_gid 取第七段（:1368-1369）→offset 平移远端窗口：addr+=offset、size-=offset（:1381-1382，允许 client 指定从缓冲内某处开始写）→组装 ah_attr：is_global/dlid/port_num + RoCE 路由头（dgid=rem_gid、sgid_index=本端 gidx、traffic_class=TC_PRIO<<5，:1401-1411）→`rdma_create_ah_cached` 拿 AH（:1413）→exec_params 整备完毕交 `rdma_exec_task`（:1416）。之后 verbs 动词把 rkey+addr 写进 RDMA WRITE 报文（第 12 步篇目展开），NIC 据此直接对 client 显存 DMA——rkey 就是 client 侧 MR 的远程访问凭据，desc_str 第七段 GID 让 RoCE 报文找到 client 的 HCA，dctn 段让报文命中 client 的 DCT。

## 五、设计决策

- **权限三位全开而非按需最小化**（:1166）：样例要同时支持 WRITE/READ 两种任务，索性全开；注释自认"本地缓冲场景其实只需 LOCAL_WRITE"（:1167）。生产上 REMOTE_WRITE 范围应收窄到需要的缓冲。
- **描述串用文本而非结构体**：TCP 控制面传 `addr:size:rkey:lid:dctn:g:gid` 冒号串（:1251），牺牲一点字节数换来可 debug（client debug 输出能直接看到凭据，client.c:416）与端序无关（全部是 ASCII hex，仅 gid 内部做 htonl 对齐 32 位边界，:1235）；sscanf 反解析（:1363）与 sprintf 正解析共享同一格式串模板（:1240、:1361-1362 两处注释互相引用）。
- **长度上限 sizeof 字面量定死**（:1240）：缓冲大小随格式演进而自动跟进——改模板串一处即可，但调用方 desc_str[256]（client.c:368）与 server 的 desc_str[sizeof "同模板"]（server.c:303）各自声明，存在漂移风险，样例靠"两处都够长"苟着。
- **AH 缓存键=完整 attr 结构 memcmp**（:187-190）：AH 创建要下到硬件，重复对端反复建是纯浪费；以结构体整体为键（而非手工挑 dgid 字段）保证语义完备——代价是 hash 函数必须自己写（XOR 混合 subnet_prefix/interface_id/dlid，:179-184）。
- **rkey 与 lkey 分用**：desc_str 只带 rkey（远程写凭据，:1180 注释"本地场景不用"），本地 SGE 用 mr->lkey（:1353）——verbs 的远程/本地钥匙二分被接口忠实保留。
- **debug 才验尺寸**：`buff_size_validation`（:1308-1339）检查 iovec 越界与总量失配，但只在 debug_fast_path 下跑（:1388-1395，注释：fast path 上错了硬件完成时会报错）——软件校验与硬件兜底的取舍。

## 六、新人提示

1. **验证 nv_peer_memory 就位**：`lsmod | grep nvidia_peermem`；跑 client（-u）看 reg 是否过 :1170。一个常见坑是装了模块但 GPU 驱动版本不匹配导致 pin 失败——报错文案只有 "Couldn't register GPU MR"（:1172），得靠 dmesg 找真因。
2. **desc_str 各段宽度记不牢没关系，记锚**：模板在 :1240/:1249-1250，七段含义的注释在 :1361-1362；两处对读即可。
3. **DCTN 藏在第五段**（:1256 注释 `/* dctn */`）：QP 号被复用为 DCT 号，DC 报文靠它寻靶——client 的 qp_num 在 DCT 创建后即生效（:630）。
4. **同一对端重复 submit 不再建 AH**：khash 命中走 :1297-1301 快路；想观测缓存效果开 -D 位 0，看 "ibv_create_ah" 日志只在首个迭代出现。
5. **offset 的语义**（:1381-1382）：远端窗口起点平移、长度缩短——它把"在 64KB 对齐大缓冲里取一片"下放到 server 侧解析，client 不必为不同 offset 反复 reg。
6. **dereg 失败会漏 cnt--**：ibv_dereg_mr 出错时提前 return（:1202-1205）且不 free、不减计数——闸门因此保持关闭（close 拒关），这是有意的"卡死好过泄漏"。
