# 12 · cuEST 与 cuTENSOR：量子化学最大域与张量缩并现代姿势

## 角色定位

cuEST（L15 层，265 节点，全仓最大域）是 NVIDIA 量子化学库 cuEST 的官方示例集，三线布局：`c_examples` 七主题 29 个 .c（context/基础数据结构/单电子积分/密度拟合/交换相关/有效核势/PCM 溶剂）；`python_examples` 同七主题 22 个 run.py；`cuest_scf_examples` 是压舱石——`cuest_scf` Python 包（30 模块）自带 RHF/UHF/MP2/CPHF 四个驱动示例与 pytest 集成。cuTENSOR 家族（L16 层 43 节点）则覆盖 C++ 13 示例 + torch/TF 双 Python 绑定 + cuTENSORMg/cuTENSORMp 分布式两支。

## 内部结构

cuest_scf 包的核心是 **rhf.py 1735 行 / uhf.py 1790 行**的双子实现：`class RHF`（rhf.py:52）与 `class UHF`（uhf.py:52）全部能量分量挂 `@memoized_property`（rhf.py:18 导入、:192 起十余连）——`cuest_primary`（:192 AO 基组）、`cuest_auxiliary`（:199 DF 辅助基）、`cuest_ecp_basis`（:206）、`cuest_xc_grid`（:216 分子网格）都是惰性属性，首次访问才触发 cuEST 调用，SCF 主循环里 DIIS（:918-919 计时+solve_diis，实现在 :1129）与 maxiter=100（:75）参数化。UHF 多出 alpha/beta 双密度矩阵处理，正是多出的 55 行。底层适配层 `helpers/cuda_utils.py` 纯 ctypes：cuEST 是 C API，Python 侧把用户管理的 GPU 资源以回调/句柄回灌 `cuestCreate`；cphf-1 示例的 kernel_helper.py 走 cuda-python+NVRTC 双依赖 JIT（arch 探测→编译→cuModuleLoad）。

## 外部连接

C 线的公共件在 `c_examples/common/`：`helper_gbs_parser.h:118` 的 `parseGBSFileForElement` 解析 Gaussian 基组、`helper_xyz_parser.h` 分子几何、`helper_workspaces.h` 工作区统一管理；数据在 `data/`（h2o.xyz + def2-svp.gbs）。cuTENSOR 侧：`contraction.cu` 的三段式（PlanPreference :194→workspace 估计 :205-211→CreatePlan :218）与 `utils.cuh:52` 的 `cuda_ptr`（unique_ptr+cudaFree 删除器）；Python 双栈 torch `EinsumFunction(torch.autograd.Function)`（einsum.py:25，forward :28/backward :48）与 TF 的 `py_func` 桥（tensorflow/einsum.py:35 的 einsum、:86 的梯度转置收缩）。

## 数据流

RHF 主链：xyz/gbs 解析→GPU 矩阵对象（gpu_matrix.py）→AO 基组/对列表→S/T/V 单电子积分→SAD 初猜（sad_atom_structure.py 的 aufbau 排布）→SCF 迭代（Fock 构建→DIIS 外推→对角化）→能量树汇总。cuTENSOR C++ 链：描述符→PlanPreference→workspace query→Plan 缓存（contraction_plan_cache.cu 专示复用）→execute；einsum.cu 把这套封装成解析下标字符串的类（main 仅 21 行量级，逻辑在 Einsum 类）。

## 设计决策

cuEST 的 Python 包用 memoized 声明式能量树换取可读性（物理结构=属性依赖图），代价是首次访问的长尾延迟；C 线则全部回调化内存管理（allocateWorkspace/freeWorkspace 成对）。cuTENSOR 的 workspace 两遍式（query 后 execute）与 JIT 路线（contraction_jit.cu 即时编译 kernel）是同一权衡的两端：plan 换启动开销、JIT 换峰值性能。TF 绑定用 REGISTER_GPU 宏三次实例化 double/float/Eigen::half（einsum_kernel.cc:112-114）而 torch 绑定走 autograd 原语——同一后端两代框架集成范式；einsum.cu 本体是 `struct Einsum` 模板（:59，main :434 只做调用）。

## 新人提示

跑 cuest_scf 先 `pip install nvidia-cuest-cu12` 再 pytest（README 的安装段）；读代码从 examples/rhf-1/test.py 顺藤摸属性树。cuTENSOR 构建必设 `CUTENSOR_ROOT`（Makefile:17-18 强制报错），库目录按 nvcc 主版本号探测 `lib/<major>`（:35）。分布式需求看 cuTENSORMg 的 discretize/collect 模式与 cuTENSORMp 的 NVSHMEM split_equation（603 行）。
