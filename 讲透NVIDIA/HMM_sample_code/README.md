# 讲透 HMM_sample_code

NVIDIA [HMM_sample_code](https://github.com/NVIDIA/HMM_sample_code)——CUDA 12.2 **Heterogeneous Memory Management（异构内存管理）** 演示仓（博客 *Simplifying GPU Application Development with HMM* 配套代码）。**语义钉版：HMM ≠ Hidden Markov Model**，全仓无任何前向/后向算法，README 标题实证。

## 全链状态表

| 阶段 | 状态 | 明细 |
|---|---|---|
| DeepWiki | ✗ 未收录 | 后台未索引（收录决定权钉版），**本图谱为唯一知识源** |
| understand 图谱 | ✅ | 21 节点 / 24 边 / 5 层 / 10 步 tour，validator 0 issues |
| fingerprints | ✅ | 11 文件基线 @a6a749a3 |
| onboarding | ✅ | [ONBOARDING.md](onboarding/ONBOARDING.md) 4992 字（不计空格）8 节 42 锚 |
| explain | ✅ | 2 篇 4991 字合计，39 锚（[01 miniapp](explain/01-miniapp-weather-app-cu-HMM零拷贝实证.md) / [02 四 demo+ci](explain/02-src四demo与ci-polyglot编排.md)） |

图谱位置：仓内 `.understand-anything/knowledge-graph.json`。

## 结构速览

- `src/` 四个 C++20 demo：atomic_flag、ticket_lock、file_before/file_after（fread vs mmap 对照）——全部是 **bash/C++ polyglot**（首块 `#if 0` 对 bash 是注释、内嵌 `nvc++ -stdpar=gpu` 自编译命令，`bash ticket_lock.cpp` 可直接跑）
- `miniapp/` ERA5 40 年降水 HMM 实证：era5_preicp_nc_to_bin.py 预转 2MB 对齐二进制 → weather_app.cu 以 MAP_FIXED mmap 直读 → cub 归约（malloc 指针直进 kernel）
- `ci/` nvhpc:23.5 容器一键运行（run + demos 编排，POSIX sh）

## 甄别精选（源码级实证，详见 onboarding §7）

1. **HMM 语义勘误**（贯穿）：异构内存管理，非隐马尔可夫模型
2. `weather_app.cu:282` 收尾 unmap 循环误用 `argc` 当文件数（只处理 3/480 个月度文件），靠 `:291` 整段 munmap 兜底掩盖 fd 泄漏
3. `weather_app.cu:235` cub 归约 `num_items=(721/2)*1440` 整数除法只覆盖**半张网格**——复现博客数字的口径前提
4. `weather_app.cu:145` va_alloc_size 多乘一次 sizeof(float)，VA 预留约 4 倍需求（≈5.4TB PROT_NONE，无害但勿学）
5. `src/file_before.cpp:3` 自编译命令**不带** `-gpu=nomanaged`（其余三 demo 都带）——before/after 对照落在编译器 flag 层
6. `file_after.cpp:44` 用 MAP_SHARED：GPU 排序结果会**回写文件本身**
7. `src/ticket_lock.cpp:86` 成功串拼作 `SUCESS`；`README.md:25` 博客链接是占位符 `link.`
8. 直方图 cudaMalloc ≈34GiB（366×24×721×1440 float）——miniapp 显存门槛量化
9. 项目内 quoted include 为 0：四 demo 零相互依赖、独立成篇

## 工艺备注

- tree-sitter 对本仓 .cpp 无 functions 提取、.cu 零提取（C++20 语法+polyglot 结构），全部函数节点人工源码补齐
- ci/demos、ci/run 为 POSIX sh（scanner 语言 unknown），已按 sh 锚定行号
