# 09 · cuRAND：引擎×分布矩阵与"Host API"的真实含义

## 角色定位

cuRAND 域（L08 层，66 节点）结构是一张 **9 引擎×4 分布**矩阵：xorwow（默认）/mrg32k3a/mt19937/mtgp32/philox 五种伪随机引擎 + sobol32/sobol64/scrambled_sobol32/scrambled_sobol64 四种 Sobol 准随机引擎，各配 uniform/normal/lognormal/poisson 四示例，共 36 个几乎同构的 .cpp。目录名 `Host/` 需要勘误式解读：**它指"宿主 API 族"而非"仅宿主执行"**——每个示例都同时跑 device 与 host 两条生成路径并打印对照。

## 内部结构

单文件双函数是全部 36 例的模板：`run_on_device` 用 `curandCreateGenerator`（philox 例 :48）+ `curandSetGeneratorOffset/Ordering/Seed` 三连，`curandGenerateUniform` 写 device 缓冲（:63）后 memcpy 回；`run_on_host` 换 `curandCreateGeneratorHost`（:84）直接写宿主内存（:99）。Sobol 例多一步 `curandSetQuasiRandomGeneratorDimensions`（sobol32 例 :57），引擎类型换 `CURAND_RNG_QUASI_SOBOL32`（:48），ordering 换 `CURAND_ORDERING_QUASI_DEFAULT`（:110）。伪随机引擎 ordering 分两派：philox 用 `PSEUDO_BEST`（:110）、mt19937 用 `PSEUDO_DEFAULT`（mt19937 例 :102）——矩阵内部仍有微差异。

## 外部连接

共享枢纽 `utils/curand_utils.h`：`CUDA_CHECK`/`CURAND_CHECK` 双宏（:31/:41）+ `print_vector` 模板显式特化。构建走双轨且都体现 **nvcc/g++ 分野**：Makefile 模式规则 `%: %.cpp` 用 nvcc 编译纯 C++ 源（philox/Makefile:28-29，`-O3 -std=c++11`）；CMake 则声明 `LANGUAGES C CXX CUDA`（CMakeLists.txt:25）但 `curand_example.cmake:16` 的 `add_curand_example` 把 `CUDA_ARCHITECTURES OFF`（:18）——纯 .cpp 无需 arch，nvcc 只是当 C++ 编译器+链接器用，这些文件其实 g++ 也能编（只链 cudart/curand）。

## 数据流

标准五步：create→configure（offset/seed/ordering/dimensions）→generate→（device 路径才有的 memcpy+sync）→destroy。同一 seed+offset 下 host 与 device 两路输出逐值相等——示例 main 先打印 Host 再打印 Device（philox 例 :123-131），人眼即可验证可复现性。n=12 的小样本（:112）刻意保持输出可读。

## 设计决策

"一个矩阵跑全族"的生成式布局把引擎语义差异压缩到常数区：计数器型 Philox（无状态可跳跃，适合并行分 offset）、状态型 xorwow/mt19937、GPU 友好型 mtgp32、低差异 Sobol（积分收敛 O(1/N) vs 蒙特卡洛 O(1/√N)），比较维度全部隔离在 create/dimensions 两行。README 是自动生成式文档的翻车现场：sobol32 条目（README:93-95）描述误写 "scrambled sobol32"，与 scrambled_sobol32 条目（:125）复制粘贴错位——读 README 学 cuRAND 会把两族引擎混为一谈，须以代码为准。

## 新人提示

认准两条 create 的区别即可通读全部 36 例：`curandCreateGenerator`（device 生成）vs `curandCreateGeneratorHost`（host 生成）；Sobol 族记得先设 dimensions 再生成。poisson 分布双参数（lambda）与 lognormal 双参数（mean/stddev）在各自示例的 n/参数区找。想看设备端 kernel 内随机数（curand_init/curand_uniform 内建），本仓不含——那条线在 MathDx/cuRANDDx 的 02_thread_api 示例。
