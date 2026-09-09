# 视角 14：规范/标准专家（Standards Engineer）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（calm-indigo-otter），ARM v9 spec 审阅 / PCIe·CCIX 工作组 / 国密 GM/T 标准化经验
> **方法**：对照 ARMv8.2-A ARM、MISRA-C:2012、CERT C、GM/T 国密族、信创/等保/密评、MLPerf/oneAPI 做符合度评估

---

## 1. 视角定位（80 字）

我是"标准守门员"。算子库要进政务云/信创采购，必须同时过四关：**ARM 架构合规**、**编程规范**（MISRA/CERT C）、**国密合规**（SM2/3/4/9 + GM/T）、**信创/安全合规**（等保 2.0 + 密评 + GB/T 37092）。本项目当前四关全不过。

## 2. 八个盲区

### ① 国密算子零实现 —— 信创"一票否决"项 ⛔
全仓 `grep "SM[2349]"` = **0 匹配**。`OPTIMAL-PARAMS.md` 把 13 类算子做到 98% 峰值，却没有任何一行涉及 **SM3 哈希 / SM4 分组密码**。这两者正是政务云"算子库"采购的**强制项**（GM/T 0004-2012 SM3、GM/T 0002-2012 SM4）。

### ② MISRA-C:2012 Rule 21.3 全仓违反 ⛔
`grep malloc` 命中 **100+ 处**。Rule 21.3（内存分配函数不得使用）是安全关键（ISO 26262 ASIL-D、政务密评）硬门槛。无 `.clang-tidy`、无 `.cppcheck.cfg`。

### ③ CERT C 多条 Critical 违规（CWE-120/190/787）⛔
- INT32-C（CWE-190）：`gemm_mr8_verify.c:177` `malloc(M*K*4)` 三元乘在 int 域溢出
- MEM30-C：`attention_neon.c` malloc 返回值零校验
- ARR30-C：`gemm_s8.c:48` K 非 4 倍数时越界读
- EXP33-C：v4_dual 奇数 M 尾行未初始化（CWE-908 信息泄漏）

### ④ 零 MLPerf / 零公开 benchmark 📊
全仓 `grep "MLPerf"` = 0。性能数据全部"自测自报"。无 MLPerf 等效跑分，飞腾 D3000 vs 鲲鹏/海光对比只能凭厂商白皮书。

### ⑤ 无 interconnect / 互连标准视角 🌐
D3000 FTC862 的 SoC 间互联是 PCIe 4.0 / CCIX 还是 CXL 2.0？项目文档零提及。算子库在多 socket / 分离式内存下，GEMM 的 KC 分块策略完全不同。

### ⑥ ARM CCA / 安全扩展集成缺位 🔐
D3000 是 ARMv8.2-A，不含 RME。算子库作为"信创标准件"必须为 CCA-ready 预留：BTI/PAC/MTE。当前 Makefile `ARCH_FLAGS` 零 `+bt+pauth+memtag`，无 `-mbranch-protection=standard`。

### ⑦ 无 LICENSE / NOTICE / SBOM —— IP 合规零分 ⚖️
`glob "**/LICENSE*"` = 0。信创政务云采购要求**开源组件 SBOM（SPDX/CycloneDX）+ 许可证清单 + NOTICE 文件**。

### ⑧ 无国密合规与密评映射文档 📋
**GB/T 39786-2021** 规定密码应用五层。本项目：无 `docs/SECURITY.md`；无密码学模块边界声明（GB/T 37092-2018）；`expf` 时序侧信道在密评场景是**直接降级项**。

## 3. 改造建议

### 🔥 P0（信创招标前置门槛）
1. **`docs/STANDARDS-COMPLIANCE.md`**：CWE/MISRA Rule/GB-T 标准号 ↔ 代码位置 ↔ 修复状态三栏对照表
2. **Makefile 加 `misra`/`cert` 目标**：cppcheck + clang-tidy MISRA addon
3. **`malloc` → `kl_alloc` 包装**（Rule 21.3 + MEM30-C 双满足）

### 🎯 P1（国密合规核心）
4. **`src/sm3_neon.c`**：NEON 化 SM3（8-lane W 并行，目标 2 cycles/byte），对照 GM/T 0004-2012 KAT
5. **`src/sm4_neon.c`**：SM4 NEON，对照 GM/T 0002-2012
6. **`-mbranch-protection=standard`** 加入 ARCH_FLAGS（BTI+PAC）

### 📚 P2
7. **MLPerf Inference v5.0** 跑分
8. **SBOM**：`syft dir:. -o cyclonedx-json > sbom.cdx.json` + LICENSE + NOTICE + CHANGELOG
9. **CXL 2.0 / CCIX 1.5 互联建模**

## 4. 关键洞察

**洞察 A — 算子库是信创"标准件"，标准本身是护城河。** 信创采购评标中国密合规权重往往 ≥30%。SM3/SM4 NEON 化是"一行代码价值千万元订单"的杠杆——飞腾若能出**国标 KAT 向量通过 + NEON 加速 + 密评模块边界清晰**的算子库，可在政务云 CPU 招标中直接对鲲鹏（已支持 SM4 指令 `sm4e`）形成差异化。

**洞察 B — 参与 oneAPI/MLPerf 对飞腾品牌的价值是"被引用"。** D3000 当前在国际生态中近乎"隐形"。把 `kl_gemm` 适配 oneDNN，并提交一条 MLPerf D3000 结果，就能让飞腾从"国产替代故事"升级为"国际可对标实体"。

**洞察 C — ARM spec 边界已被踩线。** `bench_gemm.c:44` 用 `vdotq_laneq_s32`，Makefile 声明 `+dotprod` 是对的，但若移植到纯 ARMv8.2-A 不带 +dotprod 的核会编译失败——**应在运行时做 `getauxval(AT_HWCAP)` 探测 `HWCAP_ASIMDDM`**，这是 SBSA Level 6 的可移植性要求。

## 5. 新增实验清单

| 文件 | 目的 | 对照标准 |
|---|---|---|
| `docs/STANDARDS-COMPLIANCE.md` | CWE/MISRA/GB-T 三栏映射 | GB/T 22239-2019 |
| `docs/INTERCONNECT.md` | D3000 互连标准 + 跨节点 GEMM | PCIe 5.0 / CXL 2.0 |
| `src/sm3_neon.c` | SM3 NEON 8-lane 并行 | GM/T 0004 / GB/T 32905-2016 |
| `src/sm4_neon.c` | SM4 分组密码 NEON | GM/T 0002 / GB/T 32907-2016 |
| `analysis/lens-compliance.c` | cppcheck + clang-tidy MISRA 汇总 | MISRA-C:2012 |
| `.clang-tidy` / `.cppcheck.cfg` | 静态分析配置 | Rule 21.3/8.13/11.5 |
| `LICENSE` + `NOTICE` + `sbom.cdx.json` | IP 合规三件套 | SPDX 2.3 |

---

**一句话结论**：性能 92 分、合规 18 分。**国密 SM3/SM4 是信创入场券**（P0 级杠杆，2 周可落地），**MISRA Rule 21.3 是安全关键门槛**（P0 一周可清），**MLPerf + SBOM 是品牌国际化跳板**。八处盲区里有三处（国密 / MISRA / LICENSE）是政务云招标的**硬否决项**——技术再强，标书这一页空白就直接出局。
