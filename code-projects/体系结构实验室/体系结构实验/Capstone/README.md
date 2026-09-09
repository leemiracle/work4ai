# Capstone — 综合项目（三选一或并行）

完成 Lab00-Lab05 后，选择一个深入方向，把它**做透**。

---

## 选项 A：论文精读 — Alpha 21264 vs 飞腾 D3000M

> 对应：📕 姚永斌《超标量处理器设计》Ch11

### 任务
1. **精读论文**：Kessler, "The Alpha 21264 Microprocessor" (IEEE Micro 1999)
2. **画出 Alpha 21264 的微架构图**（取指/重命名/发射/执行/提交全流程）
3. **对照飞腾 D3000M**：
   - 用 Lab04 的反推参数填表
   - 对比 ROB/PRF/Issue Queue/分支预测器结构
   - 找出 25 年间的演进（21264 vs 飞腾）
4. **写一份 5-10 页报告**：包含架构图、参数对比表、性能对比、设计哲学讨论

### 输出
- `alpha_21264_study/notes.md` — 论文精读笔记
- `alpha_21264_study/arch_diagram.md` — 架构图（mermaid）
- `alpha_21264_study/comparison.md` — 21264 vs D3000M 对比报告

### 评分维度
- 论文细节准确度
- 反推实验设计严谨度
- 对比深度（不是罗列，而是分析"为什么这样设计"）

---

## 选项 B：自写周期级 CPU 模拟器（RV32I）

> 对应：🎓 ETHz DDCA + CS61C Proj3 + CAQA App C

### 任务
用 Python（或 C++）实现一个**周期精确**的 RV32I CPU 模拟器：
1. **5 级流水线**：IF / ID / EX / MEM / WB
2. **完整 hazard 处理**：
   - forwarding（RAW）
   - stall（load-use）
   - branch flushing
3. **基本分支预测**（2-bit 饱和 + BTB）
4. **可选扩展**：
   - 超标量（2-wide 或 4-wide）
   - 简化寄存器重命名
   - Cache 模型

### 输出
- `cpu_simulator/simulator.py` — 主程序
- `cpu_simulator/test_progs/` — 测试程序（fib, sum, sort）
- `cpu_simulator/report.md` — 报告（含 IPC 分析、hazard 统计）

### 评分维度
- 流水线正确性（hazard 处理）
- 周期计数准确度
- 测试覆盖度

---

## 选项 C：工作负载刻画 — llama.cpp 推理（或其他真实负载）

> 对应：📕 实战性能分析

### 任务
选一个真实工作负载（推荐：llama.cpp 在飞腾上的推理），完整刻画其微架构行为：
1. **Top-Down 分析**：用 PhyTune topdown-tool 跑出 Frontend/Backend/Spec/Retire 比例
2. **Cache 行为**：L1D/L2/L3 miss rate，分析热点函数
3. **分支行为**：哪些函数分支预测失败率高
4. **TLB 行为**：是否需要大页
5. **NUMA 行为**：多核时跨 socket 访问占比
6. **优化建议**：基于数据，提出 3-5 条可落地的优化建议

### 输出
- `workload_characterization/profile.md` — 完整 profile 报告
- `workload_characterization/data/` — 原始 perf 数据
- `workload_characterization/recommendations.md` — 优化建议

### 评分维度
- profile 数据完整性
- 分析深度（不是罗列指标，而是找根因）
- 优化建议的可落地性

---

## 推荐路径

| 你的目标 | 推荐 Capstone |
|---------|---------------|
| 想做学术研究 / 读博 | A（论文） |
| 想去芯片公司 / 写硬件 | B（模拟器） |
| 想做性能工程 / 软件优化 | C（工作负载） |
| 全栈提升 | 三个都做（每个 4 周，共 12 周） |

---

## 评分原则（与三本书的呼应）

| 维度 | 来源 | 权重 |
|------|------|------|
| 量化严谨度 | 📗 CAQA | 30% |
| 硬件细节准确 | 📕 姚永斌 | 25% |
| 系统化思维 | 📘 Patterson | 25% |
| 实战落地 | 🎓 csdiy 课程 | 20% |
