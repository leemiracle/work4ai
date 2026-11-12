# 讲透 GreenLiT（NVIDIA BaseOS Linux 系统测试框架）

> 仓：NVIDIA/GreenLiT @550a74c（2026-09-21）· understand-anything 全链知识库 · 2026-11-08 生成
> 定位：NVIDIA 硬件（Grace/Vera/Tegra/DGX）上 Linux 发行版的系统级测试框架——glt-test-suite 一键跑 standard/disruptive/stress 测试计划，覆盖 20 个硬件域（ACPI/ARM64/CPU/CXL/GPIO/GPU/hwtracing/I2C/IOMMU/IRQ/IRQchip/MMU/MTD/PCI/Power/RTC/System/TPM/Virt），含 C 内核探针、kretprobe、bpftrace 观测全栈。

## 全链状态表

| 阶段 | 状态 | 指标 |
|---|---|---|
| 批分析（17 批） | ✅ | 1066 节点 / 2363 边（imports 426 = scanner 314 + ast/手扫补 112） |
| 终验+merge | ✅ | assembled 1066n/2330e（35 规范修正 + 1 前缀错位手工回补） |
| layers/tour | ✅ | 10 层 / 14 步导览，1066/1066 全覆盖零重复 |
| finalize | ✅ | validator 0 issues 0 warnings · fingerprints 223 文件 @550a74c |
| onboarding | ✅ | 7546 字（不计空格）/ 8 节 / 34 锚（锚验 35/36 好，1 短名锚消歧命中） |
| explain | ✅ | 5 篇 / 17445 字 / 118 锚（抽验全绿） |

图谱在仓内 `.understand-anything/knowledge-graph.json`（1066n/2330e）。字数口径=不计空格字符。

## 产物索引

- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——新人 8 节入门：定位/技术栈（Python+poetry src-layout、C 探针/Kbuild/bpftrace、systemd）/目录地图/调度链与探针签名加载链/测试生命周期/六项设计决策/14 步路径/坑清单
- [explain/01-CLI入口与测试调度核心.md](explain/01-CLI入口与测试调度核心.md)——glt-test-suite 入口、importlib 动态发现 glt_test_*、GLTCore/GLTTestBase/PostHooks 五钩子（3475 字/25 锚）
- [explain/02-探针编译签名加载链.md](explain/02-探针编译签名加载链.md)——glt_test_pci 1383 行的 chdir→make→sign_kernel_module→insmod 链、MOK/secure-boot、kretprobe handler（3497 字/27 锚）
- [explain/03-硬件域测试模块体系.md](explain/03-硬件域测试模块体系.md)——20 域全景+实存 19 域勘误、GLTTestBase 继承树、coresight 111/112 CPU 差一法边界（3483 字/16 锚）
- [explain/04-external-tests观测体系.md](explain/04-external-tests观测体系.md)——shell 五值 exit code 契约、kretprobe/用户态刺激线、bpftrace 双脚本与 PROBE_READY 防 race（3499 字/24 锚）
- [explain/05-配置协作与质量防线.md](explain/05-配置协作与质量防线.md)——00_default.yaml 键→真身映射、systemd 集成、7 行 CI 转发器、四镜头 AI 评审机器人（3491 字/26 锚）

## 甄别精选（流水线实证，均源码核实）

**框架与构建**
1. **poetry 顶层包名双导入根**（全仓级）：pyproject packages from="src" 把 common/modules/scripts 提为顶层包——运行态 sys.path=src 用 `common.*`，pytest 从仓根用 `src.common.*`；test_perf_coresight_compat.py 同时用两种风格 mock 同一模块树。scanner 因此系统性漏解带 as 别名的子模块导入（b1/b2/b4 三批互证 26+16+36 条手补）。
2. CLAUDE.md 是指向 AGENTS.md 的 9 字节符号链接（文件内 H1 仍写 AGENTS.md）。
3. .gitlab-ci.yml 是 7 行纯转发器（include 外部 dgx/mgx/greenlit-ci@main，GREENLIT_CI_REF 钉 ref），本仓零本地 job。
4. VERSION(3.1.1) 与 check_kernel_patches.py 仓内零消费者。

**疑似死代码与占位**
5. greenlit.py:381 `hasattr(attr.func, "allow_failure")` 恒 False——attr.func 是裸函数只挂 .attr，YAML 写入的是 attr.allow_failure（greenlit.py:89 + glt_core.py:356），FAIL→AFAIL 降级分支疑为死代码；单测只断言写入侧，perform_tests 全部单测中只被 mock 从未真跑。
6. test_nvidia_tpm 是 3 行占位测试（glt_test_tpm.py:42-44，直接 logger.info("PASS.")）恒 PASS。
7. mtd 是空壳域（仅 __init__.py），实存测试域 19 个非 20。
8. nv_device.py:116-121 has_hopper_gpu docstring 复制粘贴写反（"Returns False if system has Hopper GPU"）。

**探针与观测**
9. 探针链全貌：glt_test_pci.py:641-651 chdir→make→sign_kernel_module(aspm_saved_state_probe.ko)→insmod；glt_test_i2c.py:290 同款验证 kernel 9f855779a387；sva_trigger.c 的 kprobe+TimeoutExpired 判 FAIL 与 glt_test_iommu.py:128/277/307 互证。
10. hotplug_tlb/Makefile 是用户态交叉编译 Makefile（-ldl+aarch64-linux-gnu-gcc 回退链）非 Kbuild；其余探针 Makefile 是 obj-m Kbuild——形态二分。
11. bpftrace：observe.bt.in 的 DISP-003 后置 PROBE_READY 防 BEGIN race；BTF-dedup 缺口不读 tegra241_vintf 字段；@@TARGET_SMMU@@ 模板替换实际在 cmdqv_hyp_own_runner.py:468（observe.bt.in 占位符在 :7/:102）。
12. 树内 C 探针 22 条 #include 全为系统头（linux/*、asm/*），零仓内引号引用——探针各自独立，无跨文件 C 依赖。

**配置与协作**
13. 00_default.yaml 四键真身在 src/modules/<category>/glt_test_*.py（如 arm64:test_all_pmu_events→src/modules/arm64/glt_test_pmu.py:683），非直觉的 src/<category>/test_*.py；00_test.yaml 实为单测夹具名，仓内真身仅 00_default.yaml。
14. .ai-review-bot.yaml 是 4-lens AI 评审配置（convention/discriminator/common-helper-contracts/discovery × gemini-flash/grok），引用 linux-mainline+linux-nvidia 双内核仓作评审参照，YAML 注释保留内部 MR 讨论号（!379#note_…）作政策出处。
15. hardware-manifest.json→nv_device.py:204 消费 DMI modalias；进度文件真名 test_progress.json。
16. coresight 差一法边界锚在 glt_test_coresight.py:32-43 注释块（_MIN_CPUS_FOR_TRACE_ID_PRESSURE=112/_CONTROL_CPU_COUNT=111）+L229 测试（DGX-10931），非 L111-112。
17. olympus PMCCNTR FIX_COMMIT 49f2413f9b55 判定阈值 delta ratio 10%（glt_test_olympus_pmccntr.py 源码常量）。

## 图谱分层（10 层）

CI 基建(21 文件) → 文档(14) → 运行时配置(4) → 框架核心与 CLI 入口(22) → CPU/ARM64/MM 域(23) → 平台与总线固件域(30) → GPU/IOMMU/虚拟化域(19) → C 探针与内核模块(16) → external 外部测试(20) → pytest 单测层(54)
