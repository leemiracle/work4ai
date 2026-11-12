# 讲透 Eigensolver_gpu

NVIDIA 2016 年开源的 **Quantum ESPRESSO 定制 GPU 广义特征值求解器**（MIT）：求解 $Ax=\lambda Bx$（B 对称/Hermitian 正定），对标 LAPACK DSYGVD/X·ZHEGVD/X 与 MAGMA，卖点是 CPU 依赖更少（仅剩 dstedc/zstedc 一个 CPU 调用点）。PGI CUDA Fortran 微中仓（21 文件，~4200 行 .F90/.c + 2 Makefile）。

## 全链状态表

| 阶段 | 状态 | 产物与指标 |
|---|---|---|
| 批分析 | ✅ | 1 批 2 part（67 节点→拆 35+31），66 节点 122 边；Fortran `use` 模块依赖 28 条 imports 全手扫+磁盘核实（scanner 对 f90 零解析）；calls 跨文件调用图 14 条 |
| 终验 | ✅ | json.load 全过 / ID 唯一 66/66 / 文件覆盖 21/21 / 零悬空零自环 |
| merge | ✅ | 66n/122e——merge 误删 2 条 tested_by 边（`.F90` 扩展名不在测试文件模式表）已归因回补+打 "tested" 标签 |
| layers/tour | ✅ | 7 层（文档构建/运行时上下文/顶层求解器/归约+标准求解/三对角化主控/kernel 群/测试）/12 步 tour，python 自检全覆盖 66/66 |
| finalize | ✅ | validator 0 issues 0 warnings；fingerprints 21 文件基线 @7c6d9f64 |
| onboard | ✅ | `onboarding/ONBOARDING.md`（8 节，锚 40+） |
| explain | ✅ | 2 篇（求解流水四阶段 / 三对角化 kernel 群），行号锚全核实 |
| 图谱位置 | — | 仓内 `.understand-anything/knowledge-graph.json`（66n/122e/7层/12步） |

## 一句话架构

实/复双线同构的四阶段流水：Cholesky(B)（cuSOLVER）→ 广义归约 dsygst/zhegst（分块两角法）→ 标准求解 dsyevd/zheevd（GPU 三对角化 + **CPU stedc** + GPU 块反射器回乘）→ 三角回解 trsm；计算底座是 14 个手写 CUDA Fortran kernel，精华在 **last-block 融合模式**（threadfence+atomicinc 让最后完成的 block 接做下一步尾工）。

## 甄别清单（源码级实证）

1. **随机矩阵模式下 M 未初始化即被用作 iu**：`test_driver/test_dsygvdx.F90:109` 单参分支只设 N，L246/L302 `iu = M` 消费未定义值——`./test_dsygvdx N` 跑法有坑，双参文件分支才设 M（复数版同构）。
2. **工作区预检阈值与报错文案不一致**：dsygvdx 实检 `liwork_h < N` 却报 "must be at least 3+5*N"（`lib_eigsolve/dsygvdx_gpu.F90:109-110`）；zhegvdx 五连预检中 lwork_h/liwork_h 两处同款——检的从宽、文案照抄 LAPACK 真实需求。
3. **四个死 kernel**：`dsyr2_mv_kernel`/`stacked_dgemv_N`（`lib_eigsolve/dsytrd_gpu.F90:166/511`）唯一调用点已注释（L145/L157），被 last-block 融合版取代；复数版 `zher2_mv_kernel`/`stacked_zgemv_N` 同理——分析调用链时勿当活路径。
4. **dsyevd_gpu 的 Z 按 lda 而非 ldz 声明**（`lib_eigsolve/dsyevd_gpu.F90:47`）：靠调用方 ldz=lda 成立，外部直调且 ldz≠lda 会静默越界。
5. **暂存-还原配对是隐式契约**：入口把 A 下三角暂存进 Z（`dsygvdx_gpu.F90:131`），dsyevd 结束时还原（L87 注释自曝 "works if called from zhegvd only!"）——接口不可见，重构暗雷。
6. **三组块大小各自硬编码**：gst 用 nb=448、trd 用 nb1=32、回乘用 nb2=64——没有统一 NB；末 32 列切换单 block kernel（dsytd2/zhetd2，kernel 签名硬编码 32）。
7. **三档编译参数的跨架构玄机**：dsymv/zhemv 用 cc60+maxregcount:255+nordc 编译（Makefile 注释明言 Pascal 目标码在 Volta 上更快、勿改 cc 值）——性能敏感点的非直觉调优样本。
8. **`not(skip_host_copy)` 是位反内置的 PGI 扩展用法**（`dsygvdx_gpu.F90:159`），移植 gfortran 需改 `.not.`。
9. **`create_random_hermetian_pd` 拼写**：hermetian 系上游原文（非 hermitian），引用保持原文。
10. **流水线工具盲区钉版**：merge 脚本 `is_test_path` 按扩展名查测试文件名模式，`.F90` 不在表 → `test_*.F90` 被判为生产码、合法 tested_by 边被按 prod↔prod 丢弃——本轮人工回补，后续 Fortran 仓 merge 后需专项核对 tested_by。

## 相关产物

- 图谱：`/usr-data/data2/repos/agent-repos/NVIDIA/Eigensolver_gpu/.understand-anything/knowledge-graph.json`
- 精讲：`explain/lib_eigsolve-pipeline.md`（四阶段求解流水）/ `explain/lib_eigsolve-kernels.md`（三对角化 kernel 群与 last-block 融合）

*2026-11-07 全链收官（understand 流水线，微仓口径 1 批 2 part/7 层/12 步/2 篇 explain）。字数双口径钉版：onboard 不计空格 6147（汉字 1379）、explain 两篇 3227/3371——行号锚密度所致非空格字符偏高，验收口径=不计空格总字符（与 Gymnasium/SB3 轮一致）。*
