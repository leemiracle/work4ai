# CMU 15-445 (BusTub) 从零跑起来

本手册基于 BusTub `2025.8`（仓库 `third-party/bustub`，CMakeLists `VERSION 2025.8`）。从装 clang-15、cmake 构建，到跑通 Project #1（Buffer Pool Manager）的本地测试并准备提交 Gradescope。

## 0. 一句话环境要求

Ubuntu 22.04 / 24.04（官方推荐 24.04，不支持 WSL）。需要：`clang-15`、`cmake`、`libelf-dev`。默认 Debug 模式自动开启 AddressSanitizer。

## 1. 安装依赖（官方一键脚本）

BusTub 自带 `build_support/packages.sh`（已读，会装 `clang-15` 全家桶）：

```bash
cd third-party/bustub
sudo build_support/packages.sh -y        # -y 跳过交互确认
```

等价的手动命令（Ubuntu，`packages.sh` 里 `CLANG_VERSION=15`）：

```bash
sudo apt-get update
sudo apt-get install -y build-essential \
    clang-15 clang-format-15 clang-tidy-15 \
    cmake git pkg-config zlib1g-dev \
    libelf-dev libdwarf-dev doxygen
```

验证：

```bash
clang-15 --version       # 期望 15.x
cmake --version          # >= 3.10
```

## 2. 构建 BusTub

注意：**必须在 `build/` 子目录跑 cmake**，在根目录跑会触发 `FATAL_ERROR`（CMakeLists 第 36 行专门拦截）。

```bash
cd third-party/bustub
mkdir build
cd build
cmake ..                              # 默认 Debug，开 ASan
make -j$(nproc)                       # 或 make -j8
```

成功标志：无报错，`build/bin/` 下生成 `bustub-shell` 等可执行文件。

> 想关闭 ASan（调试慢）：`cmake -DCMAKE_BUILD_TYPE=Release ..`
> 换 ThreadSanitizer：`cmake -DCMAKE_BUILD_TYPE=Debug -DBUSTUB_SANITIZER=thread ..`

## 3. Project #1：Buffer Pool Manager 跑通纸面测试

P1 涉及的文件（来自 CMakeLists `P1_FILES`）：
- `src/include/buffer/buffer_pool_manager.h` + `.cpp`
- `src/include/buffer/arc_replacer.h` + `.cpp`
- `src/include/storage/disk/disk_scheduler.h` + `.cpp`
- `src/include/storage/page/page_guard.h` + `page_guard.cpp`

### 3.1 本地测试（Googletest）

测试文件：`test/buffer/buffer_pool_manager_test.cpp`。

注意：BusTub 的测试用例默认带 `DISABLED_` 前缀（如 `DISABLED_VeryBasicTest`），**不跑**。要启用，把测试名前的 `DISABLED_` 删掉：

```cpp
// 改前：TEST(BufferPoolManagerTest, DISABLED_VeryBasicTest) {
// 改后：
TEST(BufferPoolManagerTest, VeryBasicTest) {
```

构建并运行单个测试（test/CMakeLists 用 `gtest_discover_tests` 自动注册目标，目标名 = 文件名去后缀）：

```bash
cd build
make buffer_pool_manager_test -j$(nproc)
./test/buffer_pool_manager_test                 # 跑全部用例
./test/buffer_pool_manager_test --gtest_filter=BufferPoolManagerTest.VeryBasicTest
```

跑所有测试：

```bash
make check-tests -j$(nproc)        # 构建并发现所有 gtest
ctest                              # 跑全部已注册测试
```

### 3.2 SQL Logic Test（P3 起，先了解）

BusTub 还有 `.slt` 测试（`make buffer_pool_manager_test` 这类不覆盖），P1 不用管：

```bash
make bustub-sqllogictest
./bin/bustub-sqllogictest ../test/sql/xxx.slt --verbose --in-memory -d
```

## 4. 提交到 Gradescope（自动评分）

BusTub 不在本地自动评分，正确性测试在 Gradescope 上跑。本地只做代码规范检查 + 打包。

### 4.1 签署协议（首次必须）

```bash
# 仓库根目录
python3 gradescope_sign.py
# 填 Name / Affiliation / Email / GitHub ID / Date，生成 GRADESCOPE.md
```

### 4.2 规范检查（提交前自查，否则自动判 0）

```bash
cd build
make format                 # 自动格式化（clang-format）
make check-format           # 检查格式，必须通过
make check-lint             # cpplint，必须通过
make check-clang-tidy-p1    # P1 文件的 clang-tidy 检查
```

### 4.3 打包提交

```bash
make submit-p1              # 生成 project1-submission.zip，含 P1_FILES 列出的所有文件
```

把 `project1-submission.zip` 上传到 Gradescope 的 "Project #1" 页面，等自动评分结果（含隐藏测试）。

> 各 Project 打包目标：`make submit-p0` / `submit-p1` / `submit-p2` / `submit-p3` / `submit-p4`（在 CMakeLists 末尾定义）。

## 5. 常见报错 → 修复

| # | 报错文本 | 一行修复 |
|---|---------|---------|
| 1 | `Run CMake from a build subdirectory! ... FATAL_ERROR` | 在根目录跑 cmake 了；删掉根目录 `CMakeCache.txt`、`CMakeFiles/`，改在 `build/` 里跑 |
| 2 | `We recommend that you use clang-15 ... You're using gcc` | 装并指定：`cmake -DCMAKE_CXX_COMPILER=clang-15 -DCMAKE_C_COMPILER=clang-15 ..` |
| 3 | `make check-format` 失败 / 上传后格式被拒 0 分 | 先 `make format` 自动修，再 `make check-format` 确认通过 |
| 4 | 测试编译过但跑出来 `[  PASSED  ] 0 tests`（全是 DISABLED） | 测试名带 `DISABLED_` 前缀默认不跑；删掉前缀才会执行 |
| 5 | `AddressSanitizer: heap-buffer-overflow` 运行测试崩溃 | 你越界了（Page 大小、指针算术）；按 ASan 栈定位，不要关 ASan 蒙混 |
| 6 | `make buffer_pool_manager_test` 报 `No rule to make target` | 没在 `build/` 跑，或 target 名写错；目标名是去 `.cpp` 的文件名：`buffer_pool_manager_test` |
| 7 | clang-tidy 报 `file not found` / `compile_commands.json` 缺失 | 没重新 cmake；`cd build && cmake ..` 会重新生成 `compile_commands.json` |
| 8 | `cmake ..` 卡在下载 googletest | 网络问题；googletest 在 `third_party/googletest` 已自带（offline 模式），确认没误删该目录 |

## 6. 下一步

- P1 完成后，每个新 Project 在独立 git 分支开发：`git checkout -b p2`。
- 官方约定：**不要公开 fork BusTub**（README 警告）。用 mirror 到私有仓库的方式协作。
- 进阶阅读：`src/include/storage/page/` 理解 Page 内存布局，是 P2 B+ Tree 的基础。
