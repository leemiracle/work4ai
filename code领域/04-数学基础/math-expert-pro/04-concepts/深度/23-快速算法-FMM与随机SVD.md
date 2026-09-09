# 快速算法：从 FFT 到随机 SVD

> "用数学减少计算"——从 O(N²) 到 O(N log N) 的飞跃。

## FFT（Cooley-Tukey 1965）
DFT: O(N²) → FFT: O(N log N)
核心：分治——把 DFT 分成偶数和奇数项递归

影响：数字时代的基石（音频/视频/通信/医学影像）

## 快速多极子方法（FMM, Greengard-Rokhlin 1987）
N 体问题（如万有引力/Coulomb）：O(N²) → O(N)
核心：多极展开（远场用低阶近似，近场精确计算）
应用：天体力学/分子动力学/电磁仿真

## 层次矩阵（H-matrices, Hackbusch 1999）
稠密矩阵的层次低秩近似：O(N²) → O(N log N)
应用：积分方程/边界元/有限元预处理

## 随机 SVD（Halko-Martinsson-Tropp 2011）
精确 SVD: O(mn²) → 随机 SVD: O(mnk)（k=目标秩）
核心：用随机投影降维 → 小矩阵 SVD → 回代

## 随机化数值线性代数
趋势：用随机化加速线性代数
- 随机投影降维
- 草图（sketching）
- 随机迹估计（Hutchinson）

## 关联
- [百科-10-计算数学](../百科-10-计算数学.md)
- [代码库 04-FFT](../../15-applications/代码库/04-傅里叶变换_音频频谱.py)
- [代码库 31-谱理论](../../15-applications/代码库/31-矩阵谱理论.py)
- [代码库 29-压缩感知](../../15-applications/代码库/29-压缩感知_稀疏恢复.py)
