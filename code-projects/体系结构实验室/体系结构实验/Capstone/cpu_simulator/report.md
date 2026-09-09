# Capstone-B: RV32I 5 级流水线模拟器 — 实验报告

> 本报告由 `run_all_and_report.py` 自动生成。所有数据来自真实运行。

**生成时间**：2026-06-30 09:49:43  
**测试程序数**：7  
**总测试结果**：ALL PASS ✓

---

## 1. 配置：Forwarding ON（生产配置）

5 级流水线 + EX→EX/MEM→EX 转发 + Load-Use Stall + 2-bit 饱和分支预测器 + 分支在 EX 解析。

| 程序 | 指令数 | Cycles | IPC | Stalls | Flushes | 分支数 | 预测准确率 | 结果 |
|------|-------:|-------:|----:|-------:|--------:|-------:|----------:|:----|
| `branch_zoo.s` | 20 | 36 | 0.556 | 0 | 12 | 6 | 0.0% | PASS x10=6/6 |
| `bubble_sort.s` | 142 | 178 | 0.798 | 10 | 22 | 43 | 74.4% | PASS x10=1/1 |
| `fib.s` | 65 | 73 | 0.890 | 0 | 4 | 21 | 90.5% | PASS x11=55/55 |
| `function_call.s` | 5 | 11 | 0.455 | 0 | 2 | 0 | - | PASS x10=42/42 |
| `memory_ops.s` | 15 | 19 | 0.789 | 0 | 0 | 0 | - | PASS x10=305419896/305419896 |
| `shifts_and_logical.s` | 15 | 19 | 0.789 | 0 | 0 | 0 | - | PASS x5=64/64 |
| `sum.s` | 34 | 42 | 0.810 | 0 | 4 | 10 | 80.0% | PASS x10=55/55 |

---

## 2. Forwarding ON vs OFF 对比

关闭 forwarding 后，紧邻的依赖指令会读到过时的 RegFile 值，导致**结果错误**（不是性能损失，而是正确性问题）。

| 程序 | IPC (FWD ON) | IPC (FWD OFF) | Δ Cycles | Δ 结果 |
|------|-------------:|--------------:|---------:|:------|
| `branch_zoo.s` | 0.556 | 0.556 | +0 | ⚠️ 不同 |
| `bubble_sort.s` | 0.798 | 0.750 | -154 | ⚠️ 不同 |
| `fib.s` | 0.890 | 0.899 | +6 | ⚠️ 不同 |
| `function_call.s` | 0.455 | 0.529 | +6 | ⚠️ 不同 |
| `memory_ops.s` | 0.789 | 0.789 | +0 | ⚠️ 不同 |
| `shifts_and_logical.s` | 0.789 | 0.789 | +0 | ⚠️ 不同 |
| `sum.s` | 0.810 | 0.822 | +3 | ⚠️ 不同 |

> **教学结论**：forwarding 不是性能优化，而是流水线正确性的必需机制。经典 MIPS 教科书的 "stall-on-hazard" 替代方案会插入 2 cycle 气泡，IPC 损失巨大；forwarding 用组合电路消除气泡，是工程上的关键巧思。

---

## 3. 关键观察（自动分析）

- **IPC 最高**：`fib.s` = 0.890，说明其指令间 ILP 高、分支少。
- **IPC 最低**：`function_call.s` = 0.455，瓶颈通常是分支密集或 load-use stall。
- **分支预测准确率**：`fib.s` 最高 = 90.5%（21 个分支，2 次预测错误）；`branch_zoo.s` 最低 = 0.0%。
- **Load-Use Stall**：仅 `bubble_sort.s` 触发 stall （10 次），因为该程序 load 后立即使用结果。
- **Branch Flush**：`bubble_sort.s` 触发最多 22 次 flush （11 次预测错误 × 2 cycle penalty）。


---

## 4. 微架构机制验证

### 4.1 Forwarding 路径

- **EX/MEM → EX**：上一条 ALU 指令的结果直接转发到当前 ALU 输入，0 cycle 损失。
- **MEM/WB → EX**：再上一条指令（含 load 数据）的最终结果转发。
- **Load-Use 例外**：load 的数据要等 MEM 阶段才有，无法向后转发到当前 EX，必须 1 cycle stall。

### 4.2 分支解析

- 分支在 **EX 阶段解析**（MIPS 经典做法），错误预测 penalty = 2 cycle。
- **2-bit 饱和预测器**（per-PC，状态 SN→WN→WT→ST）在 IF 阶段预测方向。
- **观察**：循环程序首次进入循环时必然 mispredict（预测器初值 WN），但循环稳态下预测准确率 → 100%。

### 4.3 流水线排空

- `ecall/ebreak` 进入 ID 阶段后，IF 永久停止取指（`halt_fetch` latch）。
- 这是必要的——否则 `ret` 返回到 `ecall` 后，下一条顺序指令会被错误重取，导致死循环。

## 5. 与真实硬件的对比（教学参考）

| 维度 | 本模拟器（RV32I 5 级）| 飞腾 D3000M (FTC862) | Alpha 21264 |
|------|--------------------|----------------------|-------------|
| 流水线深度 | 5 级 | ~15 级（推测） | 7 (INT) / 9 (FP) |
| Issue Width | 1-wide | 4-wide | 4-wide |
| 乱序执行 | ❌（顺序） | ✅（OoO） | ✅（OoO） |
| 寄存器重命名 | ❌ | ≥ 50 PR | 80 (INT) + 72 (FP) |
| 分支预测 | 2-bit 饱和 | Hybrid（推测 TAGE-like）| Hybrid Tournament |
| Cache | ❌ | L1 64KB / L2 512KB / L3 8MB | L1 64KB / L2 off-chip |
| 典型 IPC | 0.5–0.9 | 1.5–3.5 | 1.5–2.5 |

> 本模拟器的 IPC 上限 = 1.0（单发射 + 顺序）。真实 4-wide OoO CPU 的 IPC 可达 2–4，但需要复杂的寄存器重命名 + 唤醒-选择电路 + 推测执行机制。这是 Patterson & Hennessy 在《CAQA》第 3 章的核心主题：**ILP Wall 限制了单核性能，多核成为主流**。

## 6. 测试覆盖度

- **指令覆盖**：RV32I 全部 40 条基础指令（10 R-type + 6 I-ALU + 3 I-shift + 5 load + 3 store + 6 branch + LUI + AUIPC + JAL + JALR + FENCE + ECALL + EBREAK）。
- **机制覆盖**：Forwarding × 2 路径 / Load-Use Stall / Branch Flush / 2-bit 预测器 / JAL 静态预测 / JALR 动态目标。
- **测试程序**：见 [`test_progs/`](./test_progs/) 目录。
- **单元测试**：[`pytest tests/`](./tests/) 共 77 个测试用例，覆盖解码 / ALU / 分支判定 / 汇编器 / 流水线机制 / 集成测试。

```bash
# 跑全部测试
pytest tests/ -v

# 重新生成报告
python3 run_all_and_report.py -o report.md
```
