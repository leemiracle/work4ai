# 11 HPL 实验链：launch_hpl_experiment 生成器模式、41 份 HPL.dat 与 verify 抖动分析

## 一、角色定位

对应图谱 L13 工作负载层的 `workloads/bit/hpl/`——GPU 集群 burn-in（烤机）实验链，回答"持续满载下哪些节点掉队"。四组件：launch_hpl_experiment.sh（488 行总启动器）、submit_hpl.sh（144 行作业体）、hplfiles/ 下 **41 份 HPL.dat** 预调输入档、verify_hpl_experiment.py（281 行抖动检测）；calculate_N.py/format_results.py 是推新机型参数与汇总 CSV 的辅助。

## 二、内部结构

**launch 是"生成器模式"典范**：自定位共享目录（:18，HPL_DIR 由 dirname 派生可覆盖），默认 niters=5、容器 nvcr.io/nvidia/hpc-benchmarks:21.4-hpl（:22,33）；机型分支设 gpus_per_node+SYSCFG+GPUMEM（dgx2 为 16 卡 :153-155，dgxa100_80G :160-163），**自定义机型必须给 syscfg 脚本否则退出**（:165-172）；容器运行时 singularity/enroot 可选、bare 明确"not supported yet"（:224-227）。HPL.dat 选择走 find_hpl_dat_file（:91）按 `${nnodes}N_${system}` 命名匹配（_ai 后缀表 HPL-AI）；**手动 --hpldat 时文件反客为主**：`tail -n +10/11/12` 直读第 10-12 行反推 nodes_per_job（:251-259）——文件内容覆盖命令行参数的少见方向。

**41 份 HPL.dat 是预调参数库**：dgxa100_40G/80G 各 14 份、_ai 变体 3 份、dgx1v_16G 5 份、dgx1v_32G 3 份、dgx2 2 份；规模 1N 到 140N（SuperPOD 级），16 种 P×Q 网格（单机 4×2 到 140N 的 35×32）。样板 1N_dgxa100_80G：N=288000/NB=288/P×Q=4×2（hplfiles/HPL.dat_1N_dgxa100_80G:6,8,11-12）；140N_80G 给 6 个候选 N（3452256..3453696，:6）配 P=35/Q=32（:11-12）。

**verify 做"参考值+抖动"双验证**（文件头 :7-9 自述）：解析每个 .out 的 WR 行（verify_hpl_experiment.py:118-142，HPL_AI 时列偏移 off=1、gflops 取第 10 列而非第 6 列），PASSED/FAILED 从残差行提取（:142-150），HOSTLIST 记录节点归属（:149）；抖动判定 `time > besttime*HPLTHRESH`（:210），阈值 HPLTHRESH=CPUTHRESH=1.05（:23-24）——**以本实验最快作业为基准，慢 5% 即记 slow**，按 HOSTLIST 归因到节点（:197）；Summary 输出 Max/MinPerf 与 Percent Range（:274）。

## 三、外部连接

上游依赖 Slurm（sinfo :283/sbatch :397/squeue :455）与容器运行时；syscfg-dgx*.sh 四个机型档案提供 CPU/GPU/网卡亲和性与告警阈值（80GB 版与 40GB 版 CPU_AFFINITY 顺序不同、UCX 走附加网卡槽位）；submit_hpl.sh 注释明确"不能靠 dirname 定位脚本（批处理系统可能拷到 /tmp 执行）"，必须由启动器预设 HPL_DIR。launch 收尾自动调用 verify 并 tee 落盘（:476）闭环。

## 四、数据流

sinfo 抓 idle 节点（:283）→include/exclude 过滤（:288-306）→每轮把节点切成 nodes_per_job 大小的作业（`-w` 列表，或 --nores 模式 --dependency=singleton :360）→**每作业独立 WORKDIR**：HPL.dat+syscfg 拷入再 sbatch（:378-395），`--export ALL,CONT,SYSCFG,...`（:401）保证自包含→squeue 10 秒轮询守候（:449-464）→verify 按节点聚合 slow/failed/unknown/dnc 四桶（:197-230）→报告落 results/<EXPNAME>/。

## 五、设计决策与甄别

1. **作业自包含**：每实验拷输入到独立 WORKDIR，不依赖共享目录状态——与 submit 的"dirname 不可信"注释互为因果。
2. **对照基准内生化**：verify 不需外部参考性能，用 besttime 判慢节点——烤机场景"和同伴比"比"和理论峰值比"更真实。
3. **勘误（本仓未修笔误）**：excludelist 分支 `mv ${MACHINFILE}.t2 ${MACHINEFILE}`（:303）把 MACHINEFILE 拼错成 MACHINFILE——变量展开为空后 mv 必失败，**`-x` 排他列表过滤实际从不生效**，潜伏 bug。
4. **-r/--random 用 shuf 打乱每轮节点顺序**（:56），抑制"同批节点永远同组"的系统性偏差——实验设计的自觉。

## 六、新人提示

1. 先跑单节点（-c 1 -s dgxa100_80G --iters 1）验证全链路；EXPDIR 已存在直接报错退出（:275）。
2. verify 报 "Cases do not match" 说明混入不同 N/P/Q 作业，检查是否误并多个实验目录。
3. 新机型用 calculate_N.py --mem/--nb/--ranks 推 N 候选，按 140N 文件的多候选样式落 HPL.dat。
4. 读结果先看 Percent Range（:274）：>5% 与 HPLTHRESH 呼应，慢节点按出现次数排序直接定位硬件嫌疑。
