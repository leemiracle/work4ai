# 01 项目鸟瞰：README 流程图与 CMake 构建

> 对应导览第 1 步「项目鸟瞰：从 README 开始」｜节点：`document:README.md`、`config:CMakeLists.txt`

## ① 角色定位

本仓是 Animesh Trivedi 写的极简 RDMA 教学示例（作者注释见 `src/rdma_common.c:4`），全部逻辑集中在 `src/` 下 4 个文件、约 1470 行。README.md 是唯一文档，CMakeLists.txt 是唯一构建入口——图谱第 1 层「构建配置与入口文档」只收这两个节点，它们构成理解全仓的"目录页"：README 描述运行时序（客户端 7 步、服务端 6 步），CMake 描述编译时序（两个可执行目标）。图谱里有 3 条 `documents` 边从 README 指向 CMakeLists.txt 与两个 .c 文件、3 条 `depends_on` 边从 CMakeLists.txt 指向三个 .c 源文件，即文档层与构建层各覆盖了代码层一次，形成"读 README 知行为、读 CMake 知产物"的双入口。

## ② 内部结构

**README.md**（51 行）四段式：
- 客户端 7 步流程（`README.md:5-12`）：setup 资源 → connect → 经 send/recv 收服务端缓冲信息 → RDMA WRITE 把 `-s` 字符串写进服务端缓冲 → RDMA READ 读回第二个本地缓冲 → memcmp 校验 → disconnect。
- 服务端 6 步流程（`README.md:14-20`）：setup → 等连接 → 分配并 pin 服务端缓冲 → accept → 发本端缓冲信息 → 等断连。
- 运行说明（`README.md:22-48`）：`cmake . && make` 后 `./bin/rdma_server` 与 `./bin/rdma_client -a 127.0.0.1 -s textstring`，附一次真实输出的示例（`README.md:36-46`）。
- 无 RDMA 网卡的兜底（`README.md:50-51`）：用 SoftiWARP 软件设备跑通。

**CMakeLists.txt**（34 行）三段式：
- 输出路径（`CMakeLists.txt:7-10`）：把 `PROJECT_SOURCE_DIR` 重定义为 `src/`、`CMAKE_BINARY_DIR` 重定义为 `源码根/bin`，可执行文件最终落 `./bin/`——README 里 `./bin/rdma_server` 的出处。
- 编译器与 flags（`CMakeLists.txt:12-21`）：设了 `CMAKE_CXX_STANDARD 11`、`CMAKE_CXX_COMPILER g++`、`CMAKE_CXX_FLAGS "-O2 -Ofast -ffast-math -funroll-loops -march=native"`，注释自称"get crazy here"。
- 依赖与目标（`CMakeLists.txt:25-33`）：`find_library` 找 libibverbs/librdmacm（HINTS `/home/atr/local/lib`），`link_libraries(pthread ...)` 全局链接，`include_directories` 追加 `/home/atr/local/include/`，最后 `add_executable` 声明 rdma_server 与 rdma_client 两个目标——各自把 `rdma_common.c` 连同自己的主文件一起编入。

## ③ 外部连接

- `config:CMakeLists.txt → file:src/rdma_common.c / rdma_server.c / rdma_client.c`（3 条 depends_on）：构建层到代码层的全部依赖；rdma_common.h 不直接进 target，靠 `#include "rdma_common.h"` 间接卷入。
- `document:README.md → config:CMakeLists.txt / 两个 .c`（3 条 documents）：README 的 How to run 一节直接引用 CMake 产物路径，流程步骤与两端 main 函数一一对应。
- 两个 `add_executable`（`CMakeLists.txt:32-33`）都编入 `rdma_common.c`：公共层以"源文件重复编译"而非"静态库"的方式复用——这是本仓最重要的结构决定（见⑤）。

## ④ 数据流

构建期：`cmake .` 在源码根生成 Makefile → `make` 用系统 C 编译器编译 4 个翻译单元（3 个 .c + 头文件），链接出 `bin/rdma_server` 与 `bin/rdma_client`。

运行期按 README 流程对号入座——客户端 `src/rdma_client.c:517-547` 的 main 顺序调用 prepare→pre_post→connect→xchange→remote_ops→check→clean，恰是 README 7 步的代码化；服务端 `src/rdma_server.c:463-483` 的 start→setup→accept→send→cleanup 对应 README 6 步。README 示例输出里 `buffer attr, addr: 0x5629832e22c0...` 一行（`README.md:41`）正是公共层 `show_rdma_buffer_attr`（`src/rdma_common.c:27`）打印的，可作为读日志时的锚点。

## ⑤ 设计决策

- **为什么 rdma_common.c 不做成静态库**：教学仓求"一个 cmake + 一个 make 出两个 bin"的最短路径，重复编译 210 行公共代码的代价可忽略；做库反而要解释 `add_library`/`target_link_libraries` 两层概念。
- **为什么 flags 区写一堆 C++ 选项**：作者从 C++ 项目模板拷来（`CMakeLists.txt:18` 注释还在比较 g++ 与 clang++ 性能），但本仓源码全是 .c——这些设置实际全部落空（见⑥勘误①），属于"看起来在优化、其实不生效"的装饰性配置。
- **为什么 HINTS 指向 `/home/atr/local`**：作者在自己机器上把 ibverbs 装到了用户目录，find_library 的 HINTS 只是优先搜索路径，系统安装了 ibverbs 的机器上会回落到默认目录照常找到。

## ⑥ 新人提示（坑与勘误）

1. **CXX 设置全部不作用于 .c 编译（已知勘误）**：CMake 对 .c 文件用 `CMAKE_C_COMPILER` 与 `CMAKE_C_FLAGS`，而本文件只设了 `CMAKE_CXX_*` 系列（`CMakeLists.txt:12-21`）——实际编译一个 C++ flag 都没吃到。且 `set(CMAKE_CXX_COMPILER g++)` 写在 `project()` 之后本就不生效（编译器在 project() 时已锁定），双重落空。
2. **`/home/atr/local` 硬编码（已知勘误）**：`CMakeLists.txt:25-26` 的 HINTS 与 `:30` 的 include 路径都指向作者个人目录；在干净机器上 `-I/home/atr/local/include` 只是无害的空指针，但若恰好存在旧版头文件会优先命中，排查编译/链接异常时先看这里。
3. README 首行标题把 example 拼成了 "RDMA exmaple"（`README.md:1`）。
4. `cmake .` 是 in-source build，且第 8 行覆盖了 CMake 内建变量 `CMAKE_BINARY_DIR`——产物混进源码树（`./bin/`），`git status` 会脏，正规做法是 `cmake -B build` 外置构建。
5. `link_libraries` 里链了 pthread（`CMakeLists.txt:28`），但全仓没有任何 pthread 调用——`src/rdma_common.c:161-164` 的注释只是拿条件变量打比方，链上是多余的（可能为 librdmacm 间接依赖兜底）。
6. 图谱勘误：tree-sitter 提取漏了 `check_src_dst`（`src/rdma_client.c:31`）——逐行核实全仓 25 个函数定义，图谱只收了 24 个函数节点，`main:542` 调用的正是这个漏收函数。

——读完本篇请建立两个心智模型：**README 的 7/6 步 = 两端 main 的调用序列**；**CMake 的两个 target = 同一份公共层 + 各自的端逻辑**。后续 5 篇全部在 `src/` 内展开。
