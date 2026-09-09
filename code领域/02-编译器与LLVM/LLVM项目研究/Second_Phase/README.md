# 第二期扩展专题

> 在 18 Expert + 7 Lens 第一期基础上的深度扩展，针对项目核心断层的专题深挖。
> 所有专题路径：`/data/usershare/ai/飞腾/LLVM项目研究/Second_Phase/`

---

## S1 — MLIR AI 编译器全景（StableHLO/IREE/torch-mlir/Mojo/Intel graph-compiler）

**承载断层**：② MLIR-core 融合裂痕

**核心问题**：MLIR 48 方言是否会让 AI 编译器碎片化？StableHLO 能否统一 ML 模型可移植层？Mojo 是否是 AI 编程第三语言？飞腾 NPU 是否应该转 MLIR？

**对偶**：Lens_01 历史（MLIR 颠覆 LLVM core?）+ Lens_02 Christensen（MLIR 潜伏 disruptive）+ E04 中端（MLIR 融合裂痕）

📄 完整文件：[`S1_MLIR_AI_Compilers.md`](./S1_MLIR_AI_Compilers.md)

---

## S2 — 飞腾商业版编译器深挖（PhyCC/PhyGCC 闭源推测）

**承载视角**：路线 B 的飞腾案例深化

**核心问题**：PhyCC 1.0 vs PhyCC 2.0 改了什么 LLVM？PhyGCC 10.3.2 的 `FTC86x.md` 内部结构？飞腾编译器团队规模？PhyCC 是否 fork 主线 LLVM？

**对偶**：E18 飞腾收口 + Lens_07 国产化 + 飞腾 E11 PhyGCC

📄 完整文件：[`S2_Phytium_Commercial_Compilers.md`](./S2_Phytium_Commercial_Compilers.md)

---

## S3 — LLVM 安全审计（miscompilation CVE 史 + 形式化验证 + xz utils 教训）

**承载断层**：③ 编译器供应链安全

**核心问题**：LLVM 30 年 miscompilation CVE 史？Alive2 覆盖率？xz utils 后门对 LLVM 的警示？AI 辅助审查 PR（Discourse 2026-03 30 bugs）？飞腾服务器 RAS 的编译器侧？

**对偶**：E14 Sanitizers+JIT + E02 IR + 飞腾 E23 RAS

📄 完整文件：[`S3_LLVM_Security_Audit.md`](./S3_LLVM_Security_Audit.md)

---

## S4 — 国产 CPU 厂商编译器研发投入量化研究

**承载视角**：Lens_07 国产化的量化深化

**核心问题**：六家国产 CPU 厂商（飞腾/华为/平头哥/龙芯/海光/申威）的编译器 commit 数？团队规模？论文输出？谁有护城河，谁没有？

**对偶**：Lens_07 国产化 + E18 飞腾收口 + E08 AArch64

📄 完整文件：[`S4_China_CPU_Compiler_Investment.md`](./S4_China_CPU_Compiler_Investment.md)

---

## S5 — 飞腾 RISC-V 转向的编译器就绪度评估

**承载视角**：Lens_01 历史（Apple 2005 切 x86 类比）+ Lens_07 国产化（RISC-V 转向）

**核心问题**：飞腾若从 ARM 切 RISC-V（重演 Apple 2005），LLVM RISC-V 后端就绪度？OS 生态？ABI 兼容？时间窗？trigger 条件？

**对偶**：Lens_01 历史 + Lens_07 国产化 + E10 RISC-V + 飞腾 E21 AI 定位

📄 完整文件：[`S5_Phytium_RISCV_Transition.md`](./S5_Phytium_RISCV_Transition.md)

---

## S6 — LLVM 编译器战争史（30 年 GCC vs LLVM vs MLIR）

**承载视角**：Lens_01 历史学家 + Lens_02 Christensen

**核心问题**：30 年编译器战争的每场（GCC vs 商业 → EGCS 分叉 → LLVM vs GCC → MLIR vs LLVM core → Mojo）模式、赢家、教训？

**对偶**：Lens_01 历史 + Lens_02 Christensen + Lens_04 经济

📄 完整文件：[`S6_Compiler_Wars_History.md`](./S6_Compiler_Wars_History.md)

---

## 与第一期的关系

第二期专题不是"新视角"，而是**对第一期 5 个核心断层的深度挖掘**：

| 断层 | 第一期承载 | 第二期深化 |
|------|---------|----------|
| ① GPU/异构后端对齐债 | E11 | S1（MLIR AI 编译器） |
| ② MLIR-core 融合裂痕 | E04 | **S1** |
| ③ 编译器供应链安全 | E14 | **S3** |
| ④ New PM 迁移债 | E03 | — |
| ⑤ Linux 内核 GCC→Clang | E17 | — |
| 飞腾案例深化 | E18 | **S2 + S4 + S5** |
| 历史视角深化 | Lens_01 | **S6** |

**第二期专题完成后，总产出**：
- 第一期：18 Expert + 7 Lens + 5 基建 + 5 E18 清单 = ~1.34MB
- 第二期：6 专题 = ~300-400KB（预计）
- **总计**：~1.7MB / ~55 万字

---

📌 **第二期扩展方向**（未来可选）：
- S7: LLVM 与 Rust 编译器（rustc 用 LLVM 的工程债）
- S8: LLVM 与 Swift 编译器（Swift SIL → LLVM IR 的 lowering）
- S9: LLVM 与 Zig/Carbon/ Mojo 等新语言
- S10: LLVM 与 WebAssembly（Emscripten/wasm-ld）
- S11: LLVM 与 GPU 驱动（AMD ROCm / NVIDIA CUDA / Intel oneAPI）
- S12: LLVM 在数据库/浏览器 JIT（V8/HotSpot/PG/MySQL 真实状态）
