# Capstone-B: 自写周期级 CPU 模拟器（RV32I）

> 选自 🎓 ETHz DDCA + CS61C Proj3 + CAQA App C

---

## 1. 任务

用 Python（或 C++）实现一个**周期精确**的 RV32I CPU 模拟器：
- 5 级流水线
- forwarding / stall / flush
- 2-bit 分支预测器
- 可选：超标量（2-wide）+ 寄存器重命名

---

## 2. 项目结构

```
Capstone/cpu_simulator/
├── README.md                  ← 本文件
├── rv32i_sim.py               ← 主模拟器（700 行，完整 RV32I 5 级流水线）
├── assembler.py               ← 迷你 RV32I 汇编器（伪指令 + 标签 + ABI 别名）
├── run_all_and_report.py      ← 自动跑测试 + 生成 report.md
├── report.md                  ← 由上述脚本自动生成的实验报告
├── test_progs/                ← 7 个测试程序（带 @expect 自验证）
│   ├── sum.s                  ← 求 1+2+...+10 = 55
│   ├── fib.s                  ← 迭代 fib(10) = 55
│   ├── bubble_sort.s          ← 冒泡排序
│   ├── branch_zoo.s           ← 6 种分支全覆盖
│   ├── shifts_and_logical.s   ← 移位 + 逻辑运算
│   ├── memory_ops.s           ← lb/lh/lw/lbu/lhu + sb/sh/sw
│   └── function_call.s        ← JAL/JALR 函数调用
└── tests/
    └── test_rv32i.py          ← pytest 套件（77 个测试，0.17s 跑完）
```

---

## 3. 评分维度

| 维度 | 权重 |
|------|------|
| 流水线正确性（hazard 处理）| 30% |
| 周期计数准确度 | 25% |
| 测试覆盖度（至少 5 个测试程序）| 20% |
| 报告深度（IPC 分析、stall 来源）| 25% |

---

## 4. 实现（已完成）

详见 `rv32i_sim.py` + `assembler.py`（共 ~1100 行 Python）。
配套 [`tests/test_rv32i.py`](./tests/test_rv32i.py) 共 77 个 pytest 测试用例覆盖：
- 40 条 RV32I 指令的解码与编码
- ALU 运算 / 分支判定 / 立即数符号扩展
- Forwarding × 2 路径 / Load-Use Stall / Branch Flush
- 2-bit 饱和分支预测器
- 7 个完整测试程序的端到端正确性

跑测试 + 生成报告：
```bash
cd Capstone/cpu_simulator
pytest tests/ -v                          # 77 个测试全过
python3 run_all_and_report.py -o report.md  # 自动生成 IPC/stall/flush 报告
python3 rv32i_sim.py test_progs/fib.s     # 单跑某个程序
```

---

## 5. 可选扩展

- 加 cache 模型（L1/L2，看 miss rate 对 IPC 影响）
- 加推测执行（看到分支就预测）
- 加多核模拟（共享内存 + MESI 一致性）
