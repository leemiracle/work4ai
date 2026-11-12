# 04 · external_tests 观测体系：C / shell / bpftrace 三线内核深潜

> Python 层只能读 sysfs、跑命令、查 dmesg，而要回答的"IOMMU 写序、TLB 刷新对不对"发生在更深处——于是有了这套 C/shell/bpftrace 三线观测体系：仓根 `external_tests/` 自包含 shell 套件 + `src/modules/` 内嵌探针。

## ① 角色定位

- **仓根 `external_tests/`**（20 文件）：按子系统分目录（cpu/iommu/mair_el1_war/pci/pmu 等），每个 `.sh` 自包含可执行、自带构建签名加载清理全流程，由 `glt_ext_launcher.py` 发现期动态转成测试函数；
- **`src/modules/<category>/` 内嵌资产**：Python 测试同目录的 `.c`/`.bt` 随包分发，由 Python 编排 make→sign→insmod→判据→清理。

每条测试 docstring 都钉着 kernel commit（如 `glt_test_i2c.py:275` 的 `9f855779a387`），把"回归已修好"变成可重复观测。

## ② 内部结构

**shell 线靠 exit code 说话。** `glt_ext_launcher.py:77` 的 `discover()` DFS 收集全部可执行文件；`glt_ext_launcher.py:21-26` 定义五值契约（PASS=0/FAIL=1/XFAIL=2/XPASS=3/SKIP=4）。`test_mair_el1_war.sh`（584 行）的 pgprot 流程：`:404` Kbuild 构建（`obj-m`），`:416` Secure Boot 签名，`:420` insmod，`:427` gcc 现编用户态探针，`:435-440` 四连调用打 `/dev/pgprot_wc`（expect_sigbus=1）与 `/dev/pgprot_dma`（=0）。

**kretprobe 模块样板**在 i2c：`glt_test_i2c.py:290` 定位 kretprobes 目录，`:294-299` make→sign→insmod，`:302` `cat /proc/greenlit` 读命中数，`:306-308` PEC 未生效即 fail。`glt_test_cppc_cpc_read.py:300` 同构但把 insmod 超时归"结果不确定"（`:335-339`）。

**用户态刺激线**：`sva_trigger.c` dlopen libcuda、`cuMemAllocManaged` 建 SVA bind 后 800 轮 mmap→munmap 逼出 secondary TLB invalidate；未修复内核会 soft-lock，注释明说 harness 靠 TimeoutExpired 判 FAIL（`sva_trigger.c:27-28`）。`mm/hotplug_tlb/uvm_register.c` 同招：填 90% HBM 供计时 `rmmod nvidia_uvm`。两者 Makefile 同款且**非 Kbuild**：`HOST_ARCH` 探测、非 aarch64 host 回退 `aarch64-linux-gnu-gcc`、`LDLIBS = -ldl`（`sva_invalidate/Makefile:7-22`）。

**bpftrace 双脚本**：`cmdqv_hyp_own/observe.bt.in` 是模板，kprobe 谓词里的 `@@TARGET_SMMU@@`（`observe.bt.in:102`）由 `cmdqv_hyp_own_runner.py:468` 实例化；`observe_ste.bt` 是成品，`glt_test_nested_ste.py:70` 直接引用，kretprobe 里判 Config 6↔7 且 V 位清零即累计 disruptive_writes（`observe_ste.bt:53-58`）。

## ③ 外部连接

外部触点：tracefs 装 kprobe（`glt_test_iommu.py:277`）；内核 BTF——`cmdqv_hyp_own_runner.py:214` 查 `/sys/kernel/btf/vmlinux` 缺失即 SKIP；libcuda（两份 dlopen 刺激器）；libvirt——`glt_libvirt.py:29` 的 `GLTLibvirt` 薄 virsh 包装；kselftest 构建树钉死 `/usr/local/share/greenlit/linux`（`kselftest.py:46`），`glt_test_kselftest.py:49` 只跑 `TARGETS='kvm'`。

## ④ 数据流

1. **SVA 回归**：make→装 PID 过滤 kprobe→跑 sva_trigger→`glt_test_iommu.py:286` `_sizes_for_pid` 从 trace 提取 TLBI size→未页对齐即 fail。fail-closed：workload 退出 0 但零命中也 fail（`:301-308`）。
2. **CMDQV 观测**：模板实例化→bpftrace 子进程→轮询到 `PROBE_READY`（`cmdqv_hyp_own_runner.py:543`）→窗口内跑 O_DIRECT DMA→SIGINT→`END{}` 打唯一一行 `CMDQV_COUNTS`（`observe.bt.in:149-150`）→`guest_supports_cmd > 0` 判 FAIL。

## ⑤ 设计决策

**PROBE_READY 不用 BEGIN{}**——`BEGIN{}` 在自身 attach 完就执行，可能抢在其余 kprobe 就位前，用它发就绪信号会让 runner 在探针未全活时开跑。`observe.bt.in:81-90` 改用 `interval:s:1 /!@ready/` 后置 guard：interval 首 tick 天然晚于全部探针 attach。对照 `observe_ste.bt:23` 直接 `BEGIN { printf("PROBE_LIVE") }`——那里触发与观测由同一进程序列化驱动。

**BTF-dedup 缺口逼出判别器**——`observe.bt.in:57-63` 记录：`tegra241_vintf` 是 driver-private、只被指针引用，在运行内核 BTF 里不完整（`$vintf->hyp_own` 真机读不到），旧读字段方案废弃，改双函数计数判别器（`:9-20` 钉着 Vera 实测：unfixed nonnull=0/guest=246，fixed nonnull=258/guest=0），scoping miss 则 fail-closed 为 liveness SKIP。

**许可边界工程化**——bpftrace 链接 GPL-only BPF ABI，故 `observe_ste.bt:2`、`contpte_access_flags_probe.c:2` 标 GPL-2.0-only，主体 Apache-2.0；`glt_test_nested_ste.py:48-50` 声明其为独立许可产物。

**mm 两件兵器**——`bingo.c:22-23` 用 512M×2 的 `.bss`+`.rodata` 造巨型模块，`glt_test_module.py:92` 检查模块分配区 ≥1 GiB 否则点名 `3e35d303ab7d`；`contpte_access_flags_probe.c`（342 行）走 miscdevice+ioctl，`glt_test_contpte.py:30` 的 `GLT_CONTPTE_IOCTL_PROBE = 0x801C4751` 对应 28 字节判据结构，`false_noop` 置位即 fail。

## ⑥ 新人提示

- shell 测试只认 0-4 五个退出码；新目录放 `external_tests/` 下即被发现。
- `@@TARGET_SMMU@@` 是 `.bt.in` 唯一活占位符——`@@TARGET_SMMU_MMIO@@` 曾是死占位符后被删（`cmdqv_hyp_own_runner.py:461-464`）。
- `TimeoutExpired` 语义三态各异：cppc 归"不确定"、sva 当 soft-lock 铁证、tlb 线判 flush storm。
- bpftrace 退出自动打印非空 map，`observe.bt.in:140-155` 的 `clear()` 是防解析器读到重复行。

---
元数据：本篇不计空格字符 3499|锚 24
