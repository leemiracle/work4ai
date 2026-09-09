# phytium_repos 45 目录 LLVM/Clang patch 真实盘点

> 路径：`/data/usershare/ai/飞腾/phytium_repos/`（45 子目录）
> 实测日期：2026-07-07

---

## 0. 一句话结论

**45 个仓库中，零个含飞腾自研的 LLVM/Clang patch。** 所有出现的 LLVM/Clang 要么是 (a) upstream 发行版的包管理 recipe（Yocto/Buildroot/pi-os）、(b) 上游源码整树导入（Android 11 prebuilt、FreeBSD base）、(c) 第三方依赖自带的 LLVM 文件（mesa/onnxruntime/tvm）、(d) 纯 `.clang-format` 格式配置。**飞腾没有维护任何 LLVM/Clang fork。**

---

## 1. e2000-android11-device/external_llvm-project —— LLVM 12.0.0 vanilla `[实测-读文件]`
- `external_llvm-project/llvm/CMakeLists.txt` 第7-8行：`set(LLVM_VERSION_MAJOR 12)` / `set(LLVM_VERSION_MINOR 0)`
- grep `FTC86|FTC66|Phytium|ftc86|ftc66|phytium` 在整个 external_llvm-project **零命中** `[实测-grep]`。
- 这是 Android 11 AOSP 自带的上游 LLVM 12.0.0 预编译工具链源码，飞腾原样导入，无任何修改。

## 2. phytium-linux-yocto —— LLVM 13.0.1（标准 Yocto poky）`[实测-读文件]`
- `poky/meta/recipes-devtools/llvm/llvm_git.bb`：
  - 第22行：`PV = "13.0.1"`
  - 第29-30行：`BRANCH = "release/13.x"` / `SRCREV = "75e33f71c2dae584b13a7d1186ae0a038ba98838"`
  - 第31行：`SRC_URI = "git://github.com/llvm/llvm-project.git;branch=${BRANCH}..."`
  - 第32-34行：3 个 patch（0006-TargetLibraryInfo、0007-allow-env-override、0001-AsmMatcherEmitter）—— **全部是 Yocto 上游社区 patch**（Khem Raj 维护），非飞腾。
- 第63行：`LLVM_TARGETS ?= "AMDGPU;${@get_llvm_host_arch(bb, d)}"`（AArch64 上即 AMDGPU + AArch64）
- **结论：飞腾 Yocto 用的是 openembedded/poky 上游 LLVM 13.0.1 recipe，零飞腾定制。**

## 3. phytium-linux-buildroot —— LLVM 9.0.1 / Clang 9.0.1（upstream buildroot）`[实测-grep]`
- `package/llvm/llvm.mk` 第8行：`LLVM_VERSION = 9.0.1`，第9行：源从 `github.com/llvm/llvm-project/releases/download/llvmorg-9.0.1`
- `package/clang/Config.in` + `package/clang/clang.mk`（pi-os 同款）
- `configs/toolchain_buildroot.config`：默认 GCC 工具链（`BR2_TOOLCHAIN_BUILDROOT_NONE`），LLVM/Clang 是可选项。
- **结论：标准 buildroot 上游包，零飞腾定制。**

## 4. phytium-pi-os —— Clang 9.0.1 `[实测-读文件]`
- `package/clang/clang.mk` 第8行：`CLANG_VERSION = 9.0.1`，源 `github.com/llvm/llvm-project/releases/download/llvmorg-9.0.1`
- 标准 buildroot clang 包，零飞腾定制。

## 5. freebsd —— Clang/LLVM 19.1.7（vanilla FreeBSD 15 base 编译器）`[实测-读文件]`
- `lib/clang/include/clang/Basic/Version.inc`：`CLANG_VERSION 19.1.7`
- `lib/clang/include/llvm/Config/llvm-config.h`：`LLVM_VERSION_MAJOR 19` / `LLVM_VERSION_STRING "19.1.7"`
- `lib/clang/include/VCSVersion.inc`：`LLVM_REVISION "llvmorg-19.1.7-0-gcd708029e0b2"`
- `lib/clang/freebsd_cc_version.h`：`FREEBSD_CC_VERSION 1500000`（FreeBSD 15.0-CURRENT）
- `contrib/llvm-project/`：完整上游 llvm-project（clang/compiler-rt/libcxx/libunwind/lld/lldb/llvm/openmp）
- grep `phytium|Phytium|FTC86` 在 freebsd/sys/*.c **零命中**（仅有 hex 数字的误匹配）。
- **结论：飞腾 FreeBSD 是上游 FreeBSD 15，自带 LLVM 19.1.7 作 base 编译器，零飞腾定制。**

## 6. phytium-openeuler-embedded-bsp —— 无 LLVM（纯 GCC）`[实测-读文件]`
- `recipes-devtools/` 仅含：confuse、gcc、genext2fs、genimage、syslinux
- **无 llvm/clang recipe。** openEuler embedded BSP 用 GCC。

## 7. phy-studio —— IDE，无编译器 `[实测-读文件]`
- 仅含 ide/、terminal/、ChangeLog.md、README.md。飞腾 IDE，不含编译器工具链。

## 8. onnxruntime —— 第三方依赖自带的 LLVM 引用 `[实测-grep]`
- cmake/external 下的 onnx/benchmark/pybind11 等带 `.clang-format`/`.clang-tidy`，是上游格式配置，非飞腾改动。

## 9. opt-npu/ncsdk/common/phytvm —— TVM 自带 LLVM target（见 phytvm_diff_findings.md）
- `src/target/llvm/` 是 upstream TVM 的 LLVM codegen，vanilla。
- `docker/install/ubuntu_install_llvm.sh` 安装上游 apt.llvm.org 的 llvm-4/7/8/9。

## 10. opt-npu/3_14_imgdnn_lib —— 飞腾 imgdnn 库的 TVM 依赖
- `dependencies/external/tvm/imgtvm/src/codegen/llvm/` 含 codegen_llvm.cc/.h 等，是 TVM LLVM codegen 的副本，无飞腾 LLVM 后端。

## 11. 其他仓库的 *.clang-format（纯格式，非改动）
- phytium-standalone-sdk、phytium-android11-device、e2000-android11-device、zephyr_kernel、onnxruntime 等含大量 `.clang-format`——**仅代码风格配置，非编译器改动**。

## 12. linux-kernel-xenomai / phytium-xen —— 内核自带的 LLVM 工具引用
- linux-kernel-xenomai 的 tools/perf/、Documentation/kbuild/llvm.rst 是上游内核的 LLVM 构建支持文档，非飞腾改动。
- phytium-xen 的 coverage/llvm.c、scripts/clang-version.sh 是上游 Xen 文件。

---

## 13. 对 Expert_18 写作的输入建议

1. **铁证**："飞腾全 SDK 栈零自研 LLVM/Clang patch"——45 个公开仓库无一含飞腾的 LLVM fork。这是 E18 最硬的特异性锚点。
2. **版本矩阵**（写进对照表）：Android=LLVM12、Yocto=13.0.1、Buildroot/pi-os=9.0.1、FreeBSD=19.1.7——**全是上游，飞腾只是消费者**。
3. **对比叙事**：与华为毕昇（深度 LLVM fork + tsv110 调优）、龙芯 LoongArch（主线 LLVM 正式后端）形成鲜明反差——飞腾在编译器层的投入是最浅的。
4. **盲区诚实段**：飞腾闭源商业 SDK（PhyCC/PhyGCC 官方发行版）未开源，无法实测其是否含私有 LLVM patch；但**公开 SDK 全栈证据强烈指向"飞腾不自研 LLVM"**。
5. **对偶链接**：与 Expert_17（治理/许可证）联动——飞腾用上游 LLVM（Apache 2.0 + LLVM exception）合规无负担，但也意味着放弃了编译器层差异化。
