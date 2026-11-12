# 讲透国产 GPU 栈逆向（第八轮·通信库主线 2026-11-11）

> 工作区：/usr-data/data1/reverse/cuda-stack（PROGRESS.md 台账 + samples/ 四厂商全量样本 + reports/ + tools/）。
> 任务书：TASK-vendor.md（2026-11-11 用户令）。前置：CUDA-Stack-RE 第一~七轮（fatbin/libcuda/NCCL SASS/devcode 等，见 ../讲透CUDA-Stack-RE/）。

## 本轮四报告

| 报告 | 厂商/线 | 血统链结论 | 一句话 |
|---|---|---|---|
| corex-REPORT.md | 天数智芯 | **NCCL 2.28.9 vanilla fork+改名层**（ixccl/pixccl；GIN/GDAKI/DOCA 均为上游 2.28 件） | 符号改名的上游正版；私有增量=双前缀 env+CONFIG_ENUM |
| metax-REPORT.md | 沐曦 | **NCCL→RCCL(AMD)→MSCCL(MS)→MCCL(沐曦 2026)** 版权栈一行钉死 | AMD 系四跳血统；pmccl 头声明二进制无；Ext+AllToAll 族独有 |
| dtk-REPORT.md | 海光 | **NCCL→RCCL(2.22.3)→海光内建**（无版权戳，内网 LLVM17 fork 痕迹） | 导出全 nccl 原生前缀（碰撞极值）+du\* 第二 API 族+XHCL/ROME/XDP |
| nvnccl-REPORT.md | NVIDIA 对照 | NV 2.27.3 主机侧 Ghidra 深挖 | pnccl=强符号探桩机制 37 对；对称窗口 2MiB 双对齐契约；源码树底图 |

## 跨厂商核心结论速查

- **三大派系定型**（通信域）：NV 系（NV+天数 fork）/ AMD-RCCL 系（海光+沐曦再 fork）/ 私有增量层（沐曦 Ext/AllToAll、海光 du\*/XHCL）。
- **探桩机制仅 NV 系有**：pnccl(T)/nccl(W) 同地址别名 37 对（corex 改名保留+兼容层升强）；AMD 系两家头文件抄声明二进制无。
- **对称内存 Window API**：NV 2.27.3+ 与天数有（2MiB baseAddr/baseSize 双对齐硬契约）；沐曦/海光无（沐曦由独立 libmxshmem 承载）。
- **同名碰撞极值=海光**：librccl 导出 36 个 nccl\* 强符号与真 libnccl 同名同 SONAME 体系外共存——UCCL DEEPBIND 必须性实证。
- 四库导出面 diff 总表+T/W 机制表：见 corex-REPORT §4.5/§4.6。

## 样本资产（samples/，全 md5 验收）

corex/（libnccl.so.5.0.0.2289 146MB aarch64+libixsysnccl+ixccl.h/IX 头+宿主 driver 层）/ metax/（libmccl.so 815MB amd64+libmcruntime+mxshmem+mccl.h）/ dtk/（librccl.so.1.0 173MB+galaxyhip+rccl 头）/ NV libnccl.so.2.27.3 411MB。Ghidra 工程：节点 13 /root/ghidra-proj3(nccl-re) 全量分析可复用。

## 终夜补遗（2026-11-11 23:4x，"继续完成所有"清账轮）

- corex：私有项终判（Get/SetAttribute+RBUFF+MIX_NV 上游零命中）；fork 点精确 2.28.9；GDAKI 实现层；**WindowRegister=异步 devr 任务队列 vs NV 同步 2MiB 前置检查（DWARF 直读对照）**
- metax：AllToAlld 指针数组语义；Ext=内部路径变体；mcclFC 算法调度表；**拓扑=Dragonfly16**
- dtk：du\*=独立数据面（调用集零交叉）；**XHCL=rsmi 链路查询族；ROME=机型预置拓扑画像（model_22/23）**；25.04→26.04 版本冻结+导出清洗 353→120+XDP 新增
- nvnccl：MemAlloc 粒度上取整语义；proxy/bootstrap 簇定位；**互操作三元组（COMM_ID/SOCKET_IFNAME/IB_GID_INDEX）四库钉版——仅沐曦改 MCCL\_ 前缀**
- 新工具：tools/xdis.py（capstone 跨架构反汇编）+ ghidra_xref_strings.java

## 补全章（2026-11-12，"继续完成所有"清账终章）

- **device 容器层三模式（任务书动作6 通信库部分）**：天数=127×自研 fatbin(0x20160329) AOT 114MB/78%；沐曦=bundle v7+**bitcode-JIT**（xcore1000/1500/1600-bc）803MB/98.6%——**libmccompiler.so 依赖根因**；海光=bundle v6+五架构 AOT（gfx906-938）172MB/99.2%
- proxy 主循环（sched_yield 自旋+vtable 回调+"NCCL Progress"线程名未改名）+NCCL_PROXY_DUMP_SIGNAL 后门
- MIX_NV 终判：库内零内部消费者（ADRP 普查），仅 GetAttribute 暴露外部
- du 数据面=标准 HIP 之上（零 hsa/du 导入），与 galaxyhip AQL 族两层
- skill 陷阱表升至 11 条

## 反哺落地章（2026-11-12 0:2x）

- **UCCL patch 落地**（+15/-3，L1 33+L2 17 测试全绿零回归，未 commit 留开发线审）：UCCL_CAP_DU_FASTPATH bit9+du raw 探测+hg galaxyhip 回退+t_types 不变式 9→10
- KCCL 顺检：仅 nv/mx adapter 无 hg 线，无需改动
- 反哺双闭环：报告 §7 建议 → skill（方法层，11 陷阱）+ UCCL patch（代码层）

## 同版本终审章（2026-11-12 晨）

- **NV 正版 2.28.9 双构建形态**（aidp-vllm-nv 镜像）：sys=ENDBR✓ vs **pip wheel=无 ENDBR**——UCCL 真机 SIGSEGV 真相=wheel 缺 -fcf-protection×CET/IBT（非 NCCL 机制变化；**p 探桩面同地址同无 ENDBR，换 p 面不解决**——已预警开发线）；skill 陷阱 #12
- **同版本对照终审**：GIN/Team/LLA2A/Lsa=上游 2.28 面从推断升同版本二进制逐字实证；corex 额外导出收缩为 11 符号（Attribute 对+DevKernel/Symk/GetExportTable 内省族）

## PyPI 终章（2026-11-12 09:5x）

- 2.29.7 x86_64 wheel 实测（400MB 归档）：**p 面与普通面同地址同无 ENDBR——换 p 探桩规避 IBT 崩溃无效（实锤）**；wheel 全版本线（2.28.9/2.29.7/2.30.7 双架构）无 CET 保护定型，sys/deb 带保护
- NV wheel 也带 libnccl_device.bc——bitcode 分发不是沐曦独有
- 第八轮全部开放项清零

## 实证章（2026-11-12 10:4x）

- **dlopen 本机三连**（2.30.7 aarch64 wheel）：dlsym 两名同一指针（T/W 别名 dlsym 语义层实证）+间接调用成功（非 BTI 强制环境无保护前缀安全）+null 出参=4——x86 默认 IBT 不强制，139 只在显式 CET 进程发生；tools/dlopen_probe.c 固化（开发线一分钟复核法）
- **UCCL patch 合入确认**：56da648 含本人 DU_FASTPATH（git log -S 命中）；其"p 面优先 IBT 修"与铁数据矛盾（同地址同函数体）——归因疑点+复核法已写 nvnccl 报告 §2
- **2.32.6 最新版仍无 ENDBR**（T≡W@0xf839b）——wheel 无 CET 保护贯穿四版本点（2.28.9→2.32.6），NVIDIA 未修属常态；420MB 归档 samples/nv-pip326
- **归档位置变更**：work4ai 讲透宇宙重组（另一实例 a3f8f17a2），本目录新路径=讲透宇宙/03-查/讲透国产GPU栈逆向
