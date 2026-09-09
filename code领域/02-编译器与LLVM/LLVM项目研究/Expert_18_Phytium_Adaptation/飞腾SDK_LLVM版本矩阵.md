# 飞腾 SDK 各 OS 的 LLVM/Clang 版本矩阵

> 实测日期：2026-07-07
> 数据源：`/data/usershare/ai/飞腾/phytium_repos/`

---

## 0. 一句话结论

飞腾 6 大 OS 栈用的 LLVM/Clang **全部是上游发行版**，版本从 9.0.1 到 19.1.7 不等，**零飞腾定制编译开关**。默认工具链多数是 GCC，LLVM/Clang 仅作可选/辅助。FreeBSD 是唯一把 Clang 作默认 base 编译器的。

---

## 1. 版本矩阵总表

| OS / SDK | LLVM/Clang 版本 | 角色 | 来源 | 飞腾定制 | 证据 |
|----------|----------------|------|------|---------|------|
| **phytium-linux-yocto** | LLVM **13.0.1** | 可选工具链 | github.com/llvm/llvm-project release/13.x（poky 上游 recipe） | **无** | llvm_git.bb:22 `PV="13.0.1"` `[实测-读文件]` |
| **phytium-linux-buildroot** | LLVM/Clang **9.0.1** | 可选包 | github.com/llvm/llvm-project llvmorg-9.0.1（buildroot 上游） | **无** | llvm.mk:8 `LLVM_VERSION=9.0.1` `[实测-grep]` |
| **phytium-pi-os** | Clang **9.0.1** | 可选包 | 同上 buildroot | **无** | clang.mk:8 `CLANG_VERSION=9.0.1` `[实测-读文件]` |
| **e2000-android11-device** | LLVM **12.0.0** | Android 预编译工具链 | AOSP 上游 LLVM 12 | **无**（零飞腾字符串） | external_llvm-project/llvm/CMakeLists.txt:8 `[实测-读文件]` |
| **freebsd** | Clang/LLVM **19.1.7** | **默认 base 编译器** | 上游 FreeBSD 15（llvmorg-19.1.7） | **无** | Version.inc `CLANG_VERSION 19.1.7` `[实测-读文件]` |
| **phytium-openeuler-embedded-bsp** | **无 LLVM** | 纯 GCC | recipes-devtools 仅 gcc | N/A | recipes-devtools 无 llvm `[实测-读文件]` |

---

## 2. 编译开关细节

### 2.1 Yocto LLVM 13.0.1 `[实测-读文件]` llvm_git.bb
- `LLVM_TARGETS ?= "AMDGPU;${@get_llvm_host_arch(bb, d)}"`（AArch64 平台即 AMDGPU + AArch64）
- 3 个 patch 全是 Yocto 上游社区 patch（非飞腾）：0006-TargetLibraryInfo、0007-env-override、0001-AsmMatcherEmitter
- 默认工具链仍是 GCC（LLVM 是 recipes-devtools 可选项）

### 2.2 Buildroot/pi-os Clang 9.0.1 `[实测-读文件]` clang.mk
- `-DBUILD_SHARED_LIBS=OFF`（生成静态库 + libclang.so）
- `-DCMAKE_BUILD_TYPE=Release`
- `-DLLVM_LINK_LLVM_DYLIB=ON` + `-DLLVM_DYLIB_COMPONENTS=all`
- `toolchain_buildroot.config`：`BR2_TOOLCHAIN_BUILDROOT_NONE`（默认 GCC）

### 2.3 FreeBSD 19.1.7 `[实测-读文件]`
- FreeBSD base 编译器（/usr/bin/cc 即 clang），非可选项
- FREEBSD_CC_VERSION 1500000（FreeBSD 15.0-CURRENT）
- 完整 contrib/llvm-project（clang/compiler-rt/libcxx/libunwind/lld/lldb/llvm/openmp）

### 2.4 Android 11 (e2000) LLVM 12.0.0 `[实测-读文件]`
- AOSP 标配 prebuilt，飞腾原样导入

---

## 3. PhyCC / PhyGCC 状态（已知信息 + 推测）

| 编译器 | 基础 | 状态 | 可信度 |
|--------|------|------|--------|
| PhyGCC 10.3.2 | GCC | 飞腾主推的服务器编译器 | `[已知-待开源实测]` |
| PhyCC 2.0 | LLVM（版本未公开） | 飞腾商业编译器，闭源 | `[推测-依据]` |
| PhyCC 1.0 | LLVM | 早期版本 | `[推测-依据]` |

**诚实声明**：PhyCC/PhyGCC 的发行版未在 phytium_repos 开源仓库中出现，无法实测其 LLVM 版本与是否含私有 patch。本矩阵仅覆盖**开源 SDK 栈**。

---

## 4. 对 Expert_18 写作的输入建议

1. **核心表**：把第1节版本矩阵写成 E18 的对照表，标题"飞腾开源 SDK 的 LLVM 版本——全是消费者，无 fork"。
2. **版本碎片化问题**：9.0.1 / 12.0.0 / 13.0.1 / 19.1.7 四个版本跨度过大（LLVM 9→19 跨 5 年），飞腾未统一——这是工程治理短板，可对偶 Expert_17（治理/许可证）。
3. **默认 GCC**：除 FreeBSD 外，飞腾所有 OS 默认用 GCC，LLVM 是可选——说明飞腾主编译器路线是 GCC（PhyGCC），LLVM 是次要。这与华为（毕昇=LLVM 优先）路线相反。
4. **盲区诚实段**：PhyCC/PhyGCC 闭源，无法实测；公开 SDK 证据指向"飞腾不自研 LLVM fork"，但商业版需另查（建议联系飞腾获取 PhyCC 试用或文档）。
5. **对偶链接**：与 Expert_09（x86）、Expert_10（RISC-V）对照——飞腾 ARM 身份使其可直接复用上游 LLVM AArch64，但这也意味着零特异性。
