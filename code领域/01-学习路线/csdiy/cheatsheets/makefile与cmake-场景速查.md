# Makefile 与 CMake · 场景速查

> 命令原文 + 一句话场景。编译报错先 make clean，CMake 报错先删 build/。

## 🚨 最常用 5 条
```bash
make -j$(nproc)                     # 用全部 CPU 核心并行编译（最快）
make clean                          # 清理编译产物，从干净状态重来
make -B                             # 强制重新编译所有目标（改了头文件没生效时）
cmake -B build -DCMAKE_BUILD_TYPE=Debug   # 配置项目到 build/ 目录，开调试
cmake --build build                 # 实际编译（跨平台，替代 make）
```

---

## Makefile：第一个能用的模板
```makefile
# 最小 Makefile：保存为 Makefile，运行 make
CC = gcc
CFLAGS = -Wall -g

hello: hello.c
	$(CC) $(CFLAGS) -o hello hello.c

clean:
	rm -f hello
```
> 注意：命令行（`$(CC)...` 那行）必须用 **TAB** 缩进，不是空格，否则报 `missing separator`。

```bash
make                                # 构建第一个目标（hello）
make hello                          # 显式构建指定目标
make clean                          # 执行 clean 目标
```

## Makefile：多文件 + 自动依赖
```makefile
CC = gcc
CFLAGS = -Wall -g -MMD -MP

SRCS = $(wildcard *.c)              # 自动收集所有 .c
OBJS = $(SRCS:.c=.o)
TARGET = app

$(TARGET): $(OBJS)
	$(CC) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

-include $(SRCS:.c=.d)              # 自动追踪头文件依赖（改 .h 自动重编）

clean:
	rm -f $(OBJS) $(TARGET) *.d
```
> `-MMD -MP` 让 gcc 生成 `.d` 依赖文件，改了头文件不用 `make clean` 也能正确重编。

## Makefile 自动变量速记
```
$@  → 当前目标的名字
$<  → 第一个依赖
$^  → 所有依赖
$?  → 比目标新的那些依赖
```

## CMake：最小工程（CMakeLists.txt）
```cmake
cmake_minimum_required(VERSION 3.10)
project(hello VERSION 1.0)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

add_executable(hello main.cpp)
```

## CMake：标准构建流程
```bash
cmake -B build                      # 在 build/ 生成构建文件（out-of-source，源码目录保持干净）
cmake -B build -DCMAKE_BUILD_TYPE=Debug   # Debug 版（-g -O0）
cmake -B build -DCMAKE_BUILD_TYPE=Release # Release 版（-O3 -DNDEBUG）
cmake --build build                 # 编译（Linux 上等价于 cd build && make）
cmake --build build -j$(nproc)      # 并行编译
cmake --build build --target clean  # 清理
cmake --install build               # 安装到系统（需要 install 规则）
```

## CMake：多文件 + 子目录
```cmake
# 顶层 CMakeLists.txt
add_executable(app main.cpp util.cpp io.cpp)
# 或用变量收集
file(GLOB SOURCES "src/*.cpp")
add_executable(app ${SOURCES})
# 加头文件搜索路径
target_include_directories(app PRIVATE include)
# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
```

## CMake：加第三方库
```cmake
# 1. 系统已装的库（如 OpenCV）
find_package(OpenCV REQUIRED)
target_link_libraries(app PRIVATE ${OpenCV_LIBS})

# 2. modern 写法（推荐，带 imported target）
find_package(Threads REQUIRED)
target_link_libraries(app PRIVATE Threads::Threads)

# 3. 自己的子模块（add_subdirectory）
add_subdirectory(third_party/fmt)
target_link_libraries(app PRIVATE fmt::fmt)
```
```bash
cmake -B build -DOpenCV_DIR=/usr/local/opencv/cmake  # 库不在默认路径时指定
```

## 查看实际编译命令（编译报错看不懂时）
```bash
make V=1                            # Makefile：打印每条完整命令
VERBOSE=1 make                      # CMake 生成的 Makefile 用这个
cmake -B build -DCMAKE_VERBOSE_MAKEFILE=ON   # 让 CMake 永久开启详细输出
make -n                             # 只打印命令不执行（dry run）
```

## 常见报错急救
```
Makefile:5: *** missing separator. Stop.
  → 命令行用了空格，改成 TAB

No rule to make target 'xxx.o', needed by 'app'.
  → 源文件名写错了 / 路径不对

undefined reference to `xxx'
  → 链接阶段缺库：target_link_libraries 没加 / 顺序不对（被依赖的放后面）

CMake Error: Could not find package OpenCV
  → 装库 或 用 -DOpenCV_DIR 指定 cmake 配置文件位置

改了头文件但没重新编译
  → make -B 强制全编，或检查 .d 依赖是否生效
```

## 多目录项目典型结构
```
project/
├── CMakeLists.txt          # 顶层
├── include/                # 公共头文件
├── src/                    # 源码 + 各自 CMakeLists.txt
├── third_party/            # 第三方（submodule）
└── build/                  # 编译产物（gitignore 掉，随时可删）
```
```bash
# 改了 CMakeLists.txt 后不用删 build/，重跑 cmake -B build 即可重新配置
# 配置乱了 / 缓存出问题 → rm -rf build && cmake -B build
```
