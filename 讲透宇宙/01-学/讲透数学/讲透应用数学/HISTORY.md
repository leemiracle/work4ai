# 讲透应用数学 · HISTORY

## 2026-09-06 创刊即全量（五章 + 四实验）

- 五问模板第三例（首例集合、二例证明）；定位：**应用书架方法论总纲**
  ——优化/数值线代/信息论/博弈论/建模各是一门工具，本系列讲用工具的人的手艺
- 教材锚：Lin & Segel（天书级）+ Bender-Orszag（渐近）+ Strogatz（稳定性）
- 00-体系结构：建模→分析→计算三环+Validation 外环、分析环手艺工具箱
  （量纲/渐近/稳定性/守恒/量级估计）、与纯数学文化分野表
- 01-近五年（文献实查）：SciML 大潮——PINN→算子学习（FNO/DeepONet 2021）→
  PDE 基础模型（Poseidon NeurIPS'24/DPOT ICML'24/PROSE/MoE-POT 2025）→
  AI 气象业务化（GraphCast Science'23→NeuralGCM 混合范式→AIFS 2025-02-25 operational→NOAA 2026-01）
- 02-语言特征：渐近记号方言表（O/o/~/≪）、estimate-justify 文化 vs 定理-证明文化、
  validity 四级、Buckingham π 与"单位=类型系统"桥（pint/sympy 工程版）
- 03-可构造与结构：Hadamard 适定性三要件+正反热方程判例表、Tikhonov↔ridge 家谱、
  Lax 等价（计算版适定性）、Noether 发票、边界层/匹配渐近/刚性、保结构格式
- 04-转代码：六层栈（数值库→符号→autodiff→PINN→算子→基础模型）、
  可微化为震源、V&V 四本账、五堵墙（维数/混沌/刚性/湍流/不适定）
- 四实验全跑通：
  - 00_dimensional_pendulum.py：π 定理推 T∝√(L/g) + RK4 验证 log-log 斜率 0.5000
  - 02_asymptotics.py：摄动误差 O(εⁿ⁺¹) 标价实测（比≈1/ε）+ Catalan 渐近级数 +
    Richardson 外推 ×4→×16 阶跳
  - 03_wellposedness.py：正反热方程对拍（10⁻⁶ 扰动第 22 步爆 O(1)、频率依赖病）——
    修复基线污染叙述（改扰动单轨跟踪）
  - 04_physics_informed.py：PINN 裸核（基编码边界+配点最小二乘），误差 2e-1→1.7e-7
    ——修复 k=0 基的 0**-1 nan
- 挂网：宇宙 README（18 系列/应用书架首行总纲/依赖图 AM 节点）+ 根 README 总入口
