# 性能分析 · 场景速查（CPU / 内存 / IO / 锁 / 网络 / eBPF）

> 一行场景 → 一条命令 + 一句话何时用。系统级和语言级一起看，瓶颈才看得清。

## 🚨 最常用 5 条
```bash
top -H                                          # 看哪个线程吃 CPU（-H 显示线程）
pidstat 1                                       # 进程级 CPU/内存/IO 一秒一刷
iostat -xz 1                                    # 磁盘 busy% / await / iops
ss -tnp                                         # 当前 TCP 连接及对应进程
perf top                                        # 内核+用户态函数实时热度
```

---

## CPU 热点
### perf（Linux 内核级 profiler）
```bash
perf top -p <pid>                               # 实时看某进程函数热度
perf top -p <pid> -K                            # 只看用户态（隐藏内核符号）
perf record -p <pid> -g --call-graph dwarf -F 99 -- sleep 30  # 采 30 秒带调用栈
perf report --no-children -g graph,0.5          # 看报告，按自身耗时排序
perf record -F 99 -ag -- sleep 10               # 全机采样 10 秒（-a 全部 CPU -g 调用栈）
perf stat -p <pid> -- sleep 5                   # 看硬件计数器（IPC / cache miss / 分支预测）
perf stat -e cache-misses,branch-miss <cmd>     # 细粒度：缓存失效/分支预测失败次数
```

### 火焰图（perf 数据可视化）
```bash
# 需 github.com/brendangregg/FlameGraph
git clone https://github.com/brendangregg/FlameGraph
perf record -F 99 -p <pid> -g -- sleep 30
perf script > out.perf
./FlameGraph/stackcollapse-perf.pl out.perf > out.folded
./FlameGraph/flamegraph.pl out.folded > cpu.svg
# xz cpu.svg 解压后浏览器打开：宽=耗时，纵=调用栈；找最宽的"平台"就是热点
```

### py-spy（Python sampling profiler，不用改代码）
```bash
pip install py-spy
py-spy top --pid <pid>                          # 实时函数热度
py-spy record --pid <pid> -o flame.svg --duration 30  # 火焰图 30 秒
py-spy dump --pid <pid>                         # dump 所有线程调用栈
py-spy record -- python app.py                  # 启动并采样
```

### pprof（Go / C++ gperftools）
```bash
# Go 内建：在代码里 import _ "net/http/pprof"，然后：
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30   # 采 30 秒 CPU
go tool pprof -http=:8080 profile.pb.gz          # 浏览器看火焰图
# 内存：
curl http://localhost:6060/debug/pprof/heap > heap.pb.gz
go tool pprof -http=:8080 heap.pb.gz
# 在 pprof 交互里：top / list <func> / web
```

### async-profiler（Java 低开销）
```bash
# 下载 async-profiler，目标 JVM 不用改代码
./profiler.sh -d 30 -f flame.html <pid>         # CPU 采 30 秒出火焰图
./profiler.sh -d 30 -e alloc -f alloc.html <pid>  # 内存分配火焰图
./profiler.sh -d 30 -e lock -f lock.html <pid>  # 锁等待火焰图
# 比 JFR 更轻；和 perf 互补（perf 看 native，async-profiler 看 Java 栈）
```

---

## 内存
### 进程级
```bash
ps -o pid,rss,vsz,cmd -p <pid>                  # RSS（实际物理内存）/ VSZ（虚拟）
top -p <pid>                                    # 实时看 RES 列
pmap -x <pid> | sort -k3 -rn | head             # 看映射段哪块最大（按 RSS 排）
cat /proc/<pid>/status | grep -E 'VmRSS|VmHWM|VmPeak'   # RSS/峰值/最高水位
cat /proc/<pid>/smaps_rollup                    # 汇总：Rss/Pss/Swap
```

### heaptrack / massif（堆分配追踪）
```bash
# Linux C/C++：heaptrack（追每次 malloc，定位泄漏）
heaptrack <cmd>
heaptrack_print heaptrack.<pid>.gz | head -50   # 看 top 分配点

# Valgrind massif（堆增长曲线，慢但精确）
valgrind --tool=massif --massif-out-file=m.out <cmd>
ms_print m.out | less                           # 看堆随时间增长
```

### Java
```bash
jmap -heap <pid>                                # 堆配置 + 各代占用
jmap -histo:live <pid> | head -30               # 活对象按类统计（触发一次 GC）
jcmd <pid> GC.heap_info                         # 1.8+ 推荐
jcmd <pid> GC.heap_dump /tmp/heap.hprof         # dump 堆，用 MAT/jvisualvm 分析
jstack <pid> | grep -A5 "Heap"                  # 看是否频繁 Full GC（搭配 jstat）
jstat -gcutil <pid> 1000 10                     # 每秒一次看 10 次：Eden/Old/Metaspace 占用+GC 次数
```

### Python
```python
import tracemalloc
tracemalloc.start()
# ... 业务代码 ...
s = tracemalloc.take_snapshot()
for stat in s.statistics('lineno')[:10]:
    print(stat)            # 哪一行代码吃内存最多
# objgraph 找泄漏对象引用链
import objgraph
objgraph.show_most_common_types()
objgraph.show_backrefs([leaked], filename='ref.png')
```

### /proc/smaps 详解
```bash
cat /proc/<pid>/smaps | less
# 每段映射：Size(虚拟) Rss(物理) Pss(按比例分摊) Swap Private_Dirty(独占改过)
# 排查共享库占用：PSS < RSS，因为库被多进程共享
# Private_Dirty 大 = 该进程独占修改的页，看是不是 mmap 后又写一堆
```

---

## IO
### iostat（磁盘整体）
```bash
iostat -xz 1                                    # 每秒一次扩展视图
# 关注：%util（接近 100% = 瓶颈）、await（>10ms 偏慢）、r/s w/s、rkB/s wkB/s
# aqu-sz 大但 await 高 = 队列堵了
iostat -d 1                                     # 只看设备
```

### iotop（哪个进程在读写）
```bash
sudo iotop -oP                                  # 只显示有 IO 的进程，按进程聚合
sudo iotop -oPa                                 # 累计模式，看一段时间总量
# 没装 iotop：用 pidstat -d 1
pidstat -d 1                                    # 每秒各进程读写 KB/s
```

### blktrace（块设备级追踪）
```bash
sudo blktrace -d /dev/sda -o - | blkparse -i -  # 实时看每个 IO 请求
sudo blktrace -d /dev/sda -w 30 -o trace        # 采 30 秒
sudo btrace /dev/sda                            # 一行：blktrace + blkparse 管道
# 分析：哪些扇区被频繁访问、IO 大小分布
```

### fio（压测磁盘能力）
```bash
# 顺序读吞吐
fio --name=seqread --rw=read --bs=1M --size=1G --runtime=30 --time_based --numjobs=1
# 随机写 IOPS
fio --name=randwrite --rw=randwrite --bs=4k --size=1G --runtime=30 --time_based --numjobs=4 --iodepth=32
# 关注：IOPS、BW（带宽）、clat（完成延迟）、stdev（延迟抖动）
# 对比硬件标称值，判断是否达标
```

### 文件级
```bash
du -xah | sort -rh | head -20                   # 找最大的文件/目录
find / -xdev -type f -size +1G 2>/dev/null      # 找 >1GB 的大文件
lsof +L1                                        # "已删但仍被进程持有未释放"的文件（空间没回收的真凶）
```

---

## 锁 / 调度
### off-CPU 火焰图（看"在哪等"）
```bash
# perf 默认看 on-CPU（在跑啥）；off-CPU 看阻塞在哪，用 bcc tools/profile（基于 BPF）
sudo /usr/share/bcc/tools/profile -p <pid> -F 99 30 -f > offcpu.folded
./FlameGraph/flamegraph.pl offcpu.folded > offcpu.svg   # 宽的栈=花最多时间在等（锁/IO/sleep）
```

### perf sched（内核调度）
```bash
sudo perf sched record -- sleep 5               # 录 5 秒调度事件
sudo perf sched latency --sort max              # 看哪些任务调度延迟最大
# 关注：最大 schedule latency、是否频繁迁移 CPU、run queue 长
```

### bcc / bpftrace（BPF 工具集）
```bash
# bcc 工具（/usr/share/bcc/tools/）：opensnoop=谁 open 文件；biolatency=IO 延迟直方图；biosnoop=按进程 IO
sudo /usr/share/bcc/tools/opensnoop
sudo /usr/share/bcc/tools/runqlat               # 调度延迟分布
sudo /usr/share/bcc/tools/offcputime -p <pid>   # off-CPU 时间（阻塞分析）
sudo /usr/share/bcc/tools/lockstat              # 内核锁竞争
sudo /usr/share/bcc/tools/ext4slower            # 文件系统慢操作（>10ms）
sudo /usr/share/bcc/tools/tcptop                # TCP 连接吞吐排行
sudo /usr/share/bcc/tools/tcpretrans            # TCP 重传（网络丢包信号）
```
```bash
# bpftrace（更轻量，一行探针）
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { @[comm] = count(); }'  # 谁在 open 文件，计数
sudo bpftrace -e 'kprobe:do_nanosleep { @[comm]++ }' interval:s:5 { print(@); clear(@); }
sudo bpftrace -e 'profile:hz:99 { @[ustack] = count(); }'  # 简易火焰图采样
```

### 用户态锁分析
```bash
# pthread_mutex 卡死：gdb 看调用栈
gdb -p <pid> -batch -ex 'info threads' -ex 'thread apply all bt'
# 大量 futex 系统调用 = 在等锁：strace -f -e futex -p <pid> -c
strace -f -e futex -p <pid> -c                  # 统计 futex 调用次数/耗时
```

---

## 网络
### tcpdump 一行（抓包神器）
```bash
sudo tcpdump -i eth0 -nn port 80                # 抓 80 端口流量
sudo tcpdump -i eth0 -nn host 1.2.3.4 and port 443
sudo tcpdump -i any -nn -A 'tcp port 80'        # -A 打印 ASCII（明文 HTTP）
sudo tcpdump -i eth0 -nn -w cap.pcap            # 存文件用 wireshark 看
sudo tcpdump -i eth0 -nn 'tcp[tcpflags] & tcp-syn != 0'   # 只看 SYN（建连）
sudo tcpdump -i eth0 -nn 'tcp[tcpflags] & tcp-rst != 0'   # 只看 RST
sudo tcpdump -nn -c 100 -i eth0                 # 抓 100 个包退出
# 排查思路：先抓包，再用 wireshark/tshark 分析 -r cap.pcap
```

### ss（替代 netstat）
```bash
ss -tnp                                         # 当前 TCP 连接 + 进程
ss -tlnp                                        # 监听端口
ss -tn state established '( dport = :443 )'    # 已建立的 443 连接
ss -s                                            # 连接数汇总
ss -tn state time-wait | wc -l                  # TIME_WAIT 堆积？
ss -ti                                           # 看 TCP 内部参数（rtt/cwnd/mss）
```

### nstat / mtr / 连通性
```bash
nstat -az                                       # 内核网络协议栈计数器（TcpExt/Sock）
mtr -rwc 100 <host>                             # 100 包路由追踪，看丢包在哪跳
ping -c 5 <host>
traceroute -T -p 443 <host>                     # TCP 模式（ICMP 被防火墙挡时用）
ethtool -S eth0 | grep -iE 'drop|err|discard'   # 网卡硬件丢包计数
ethtool -g eth0                                 # 环形缓冲区大小，rx_missed 在涨就调大
ip -s link show eth0                            # 接口收发包/丢包/错误统计
```

### 网络延迟定位
```bash
# 三段式：本机 → 中间网络 → 对端
ping <host>                                     # RTT 基线
tcpping <host>:443                              # 应用层 RTT（需装）
curl -w "@curl-fmt" -o /dev/null -s https://host   # 看 dns/connect/ttfb/total 各段耗时
# curl-fmt 文件内容：
#   dns: %{time_namelookup} connect: %{time_connect} ttfb: %{time_starttransfer} total: %{time_total}\n
```

---

## 系统级（综合指标）
### vmstat
```bash
vmstat 1                                        # 每秒一刷
# r（就绪队列长 >CPU 数 = CPU 瓶颈）
# b（D 状态进程，在等 IO）
# bi/bo（块 IO 读/写 KB/s）
# us/sy/id/wa/st（用户/系统/空闲/IO 等待/被偷走时间）
# wa 高 = IO 瓶颈；sy 高 = 系统调用开销大
```

### sar（历史趋势）
```bash
sar -u 1 5                                      # CPU 5 次
sar -q                                          # 运行队列/负载
sar -r                                          # 内存
sar -W                                          # swap 换入换出
sar -d                                          # 磁盘
sar -n DEV                                      # 网卡
sar -n TCP,ETCP                                 # TCP 重传/建连
# 历史数据：sar -f /var/log/sa/sa05（看 5 号那天的）
```

### pidstat
```bash
pidstat 1                                       # 所有进程 CPU
pidstat -r 1                                    # 内存（RSS）
pidstat -d 1                                    # 磁盘 IO
pidstat -w 1                                    # 上下文切换
pidstat -t 1                                    # 按线程粒度
pidstat -p <pid> -urd 1                         # 一个进程同时看 CPU/内存/IO
```

### /proc/meminfo 解读
```bash
cat /proc/meminfo
# MemTotal/MemFree/MemAvailable                  —— 可用内存看 Available（含可回收 cache）
# Buffers/Cached                                  —— 文件缓存，压力大会自动释放
# SwapCached/SwapTotal/SwapFree                  —— swap 用了 = 物理内存不够
# Active/Inactive                                 —— 活跃/非活跃 LRU
# Slab/SReclaimable/SUnreclaim                    —— 内核对象缓存；SUnreclaim 涨 = 内核泄漏
# Shmem                                           —— tmpfs/共享内存，不算可回收
# AnonPages                                       —— 匿名页（进程堆），回收得靠 swap
# Committed_AS                                    —— 已承诺虚拟内存总量（OOM 风险指标）
```

### OOM 排查
```bash
dmesg -T | grep -i 'killed process'             # 内核杀进程记录 + 当时内存情况
journalctl -k | grep -i oom                     # 同上
# oom_score（被杀优先级）：
cat /proc/<pid>/oom_score
echo -1000 > /proc/<pid>/oom_score_adj          # 设为 -1000 让关键进程几乎不被杀
```

---

## 在线持续（eBPF / Continuous Profiling）
### eBPF 持续观测（无需改应用）
```bash
# bcc 工具可持续跑，开销 <1%
sudo /usr/share/bcc/tools/biolatency 60         # 每 60 秒输出一次 IO 延迟分布
sudo /usr/share/bcc/tools/runqlat 60            # 调度延迟
sudo /usr/share/bcc/tools/cachestat 5           # 每 5 秒 cache 命中率
# 写自定义 BPF 程序：bpftrace 脚本持续 print
```

### Pyroscope（持续火焰图聚合）
```bash
docker run -it -p 4040:8080 grafana/pyroscope       # 服务端
pip install pyroscope-io                             # 应用侧（Python）
import pyroscope; pyroscope.configure(application_name="myapp", server_address="http://pyroscope:4040")
# Web UI 看随时间变化的火焰图，对比版本差异
```

### Parca（开源 continuous profiling，多语言）
```bash
docker run -it -p 7070:7070 ghcr.io/parca-dev/parca:v0.19.0    # 各语言 agent 采集上报，UI 看火焰图+diff
# SaaS 替代：Grafana Cloud / Datadog / Polar Signals（CI 里对比每 commit 性能回归）
```

### 持续观测的黄金组合
```
应用层: py-spy/async-profiler/HeapProf → 火焰图上传 Pyroscope
系统层: bcc/bpftrace 持续采 + Prometheus 导出指标
网络层: tcpretrans + TCP 重传率告警
磁盘层: iostat 导 Prometheus + biolatency BPF
CI/CD : 每次 release 跑 bench + 上传 profile，回归即报警
```

---
*参考：本仓库 `notes/perf-程序员视角-定位与优化.md`（6 优化案例 + 火焰图流水线）、`github-repos/references/REKCARC-TSC-UHT/`（操作系统/系统编程课程）。Brendan Gregg 的《Systems Performance》《BPF Performance Tools》是这套方法论的源头。*
