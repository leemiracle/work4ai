# GreenLiT 新人入门指南（ONBOARDING）

> 基于知识图谱（1066 节点/2330 边/10 层/14 步 tour，commit 550a74c，223 文件指纹基线）与源码逐锚核实撰写。所有 `文件:行号` 锚均经 nl/grep 实证。

## 一、项目定位与一句话画像

GreenLiT 是 NVIDIA 开源的 **BaseOS Linux 系统级测试框架**：以 root 身份在 Grace/Hopper/Vera 等真机上，对内核、固件、总线与硬件子系统做"能装载、能对话、能回归"的自动化验证。一句话画像——**一个用 Python 调度器把 sysfs/lspci/kprobe/bpftrace/C 探针/外部脚本统一编排成可断点续跑测试套件的系统测试框架**。

给谁用：NVIDIA BaseOS/DGX Spark 级机型的内核集成团队（测试大量绑定 DGX-xxxx Jira 单与上游 kernel commit）；也开放给社区在 NVIDIA arm64 平台上跑内核验证。解决什么问题：内核 backport 是否真的在树上（如 i2c 探针判定 commit 9f855779a387）、平台 erratum 缺陷是否修复（Olympus T410-OLY-1027）、以及重启类/破坏性测试的跨重启状态管理——这些都不是普通 CI 单测能覆盖的。

## 二、技术栈与运行形态

- **Python 3.9+ / Poetry src-layout**：`pyproject.toml:13-17` 把 `greenlit/common/modules/scripts` 四包从 `src/` 提为顶层安装包，`src/bin/*` 打入 `greenlit/_runtime/bin`；控制台入口 `glt-test-suite = greenlit.greenlit:main`（`pyproject.toml:44`）。`poetry.toml` 特意禁用 venv（create=false + system-site-packages）——系统级测试必须直装系统 Python。
- **C 探针/Kbuild**：每个探针目录带独立 Kbuild Makefile（obj-m），测试运行时 `make` → MOK 签名 → `insmod`。例外：hotplug_tlb 与 sva_invalidate 是**用户态**程序，用 `-ldl` + aarch64-linux-gnu-gcc 交叉编译回退链（`src/modules/mm/hotplug_tlb/Makefile:16,22`）。
- **bpftrace 观测**：arm-smmu-v3 域的 `.bt` 脚本做 kprobe 级计数判别。
- **systemd 集成**：`confs/greenlit.timer:5` 的 OnActiveSec=10s 触发 greenlit.service 执行 `glt-test-suite --resume -1`，开机自动续跑中断的套件。
- **外部依赖**：ipmitool、perf、bpftrace、libvirt/QEMU、lspci、mokutil、stress-ng、nvidia-smi 等，由 `install.sh`（root）按 apt/dnf/zypper/yum 四包管理器安装，并做 Secure Boot/MOK 检查（`install.sh:412`）。

## 三、目录地图

```
├── src/greenlit/greenlit.py   # CLI 主入口（--run/--resume/--list）
├── src/common/                # 框架核心：glt_core/glt_utils/glt_conf/glt_session
│   │                          #   设备抽象：nv_device/cpu_topology/pci_utils/cxl_utils
│   │                          #   工具层：perf_utils/kernel_cmdline/glt_ext_launcher
│   └── virt/glt_libvirt.py    # virsh 轻量封装
├── src/modules/               # 20 个硬件域：acpi arm64 cpu cxl gpio gpu hwtracing
│                              #   i2c iommu ipmi irq irqchip mm mtd pci power rtc
│                              #   system tpm virt；每域 glt_test_*.py + C 探针目录
├── src/scripts/               # check_kernel_config / check_kernel_patches 两个独立 CLI
├── external_tests/            # 独立可执行外部测试（shell/C/CUDA），按退出码接入
├── tests/                     # 框架自身单测（GLTTestBase 基类 + common/modules/greenlit 三层）
├── confs/                     # glt-confs.d/00_default.yaml + systemd 单元 + hardware-manifest.json
└── docs/                      # user-guides / developer-docs / reference 三板块
```

架构铁律见 `docs/developer-docs/architecture.md` 的"改什么放哪里"对照表：测试用例进 `src/modules/<category>/`，共享 helper 进 `src/common/`，独立脚本进 `external_tests/`，版本例外进 YAML。

## 四、核心架构链路

**调度链**：`glt-test-suite`（main 在 `src/greenlit/greenlit.py:731`）解析参数后，用 glob+importlib 动态发现 `src/modules/*/glt_test_*.py`（`src/greenlit/greenlit.py:592,597`），模块级 `@GLTCore.GLTTestAttr()`（`src/common/glt_core.py:348`）与 `@GLTCore.GLTPlan()` 装饰器把函数注册进调度器；GLTScheduler（`src/common/glt_core.py:558`）按 GLTRequires 依赖做 Kahn 式拓扑排序（deque 队列在 `src/common/glt_core.py:734`）后顺序执行。执行中测试以异常为信号——`GLTTestResult` 枚举定义 SKIP/PASS/AFAIL/FAIL/WARN/NA 六态（`src/common/glt_core.py:485`），`fail()/skip()` 靠抛 GLTTestFail/GLTTestSkip 异常终止，**只能在被装饰函数的直接调用栈内生效**。每个测试挂 PostHooks（`src/common/glt_core.py:33`）五槽位：PASS→postsuccess、SKIP→postskip、FAIL→postfail、AFAIL→postafail、WARN→postwarn——跨重启测试用它注册"重启后接着验"的续命逻辑。

**探针编译签名加载链**（流水线实证，以 ASPM 为例）：测试运行时 `chdir` 到探针目录 → `make`（独立 Kbuild）→ `glt_utils.sign_kernel_module()` 用 MOK 私钥签 .ko → `insmod`，失败则 fail/skip 并指向 secure-boot 文档，见 `src/modules/pci/glt_test_pci.py:641-651`；i2c 域同构链在 `src/modules/i2c/glt_test_i2c.py:291-299`。

**系统底座**：`glt_utils.run_command`（`src/common/glt_utils.py:374`）统一 shell-free 命令执行；`check_kernel_log`（`src/common/glt_utils.py:471`）配 journald 检查点做增量日志断言；`is_cli_available`（`src/common/glt_utils.py:771`）做工具守卫；kexec 重启以 `glt_kexec_boot=1` 内核参数自识别（`src/common/glt_utils.py:787`）。

## 五、数据流与测试生命周期

1. **test plan**：`--run standard|disruptive|stress` 三计划，测试按 @GLTPlan 归属可跨计划复用。
2. **YAML 例外注入**：`glt_conf` 按文件名字典序加载 `/usr/share/greenlit/confs.d/`，CLI 把 `allow-failure`/`conditional-skip` 条件（distro 版本比较或 bash script）编译成过滤函数挂到对应测试对象上（`src/greenlit/greenlit.py:83-96`）。仓内默认层 `confs/glt-confs.d/00_default.yaml` 的四个条目键与 `src/modules/<域>/glt_test_*.py` 中的函数一一对应（如 `arm64:test_all_pmu_events` → `src/modules/arm64/glt_test_pmu.py:680-683`）。
3. **会话与归档**：每次运行创建 `/var/cache/greenlit/<时间戳>/` 会话目录（`src/common/glt_utils.py:725`），日志按模块落盘（glt_logger 双通道），进度写 `test_progress.json`（`src/common/glt_session.py:25`）。
4. **断点续跑**：reboot/REISUB/kexec 类测试中断后，systemd timer 于开机 10s 后自动 `--resume -1` 恢复上一会话。
5. **外部测试接入**：`glt_ext_launcher.discover()`（`src/common/glt_ext_launcher.py:77`）递归扫描 external_tests/ 可执行文件，动态生成带装饰器的 Python 测试，按退出码枚举映射（PASS=0/FAIL=1/XFAIL=2/XPASS=3/SKIP=4，`src/common/glt_ext_launcher.py:15-21`）。

## 六、关键设计决策

1. **双导入根并存（poetry 顶层包布局的代价）**：`packages from="src"` 使运行态以 `common.*` 顶层包导入，而 pytest 从仓根跑时又可用 `src.common.*`——`tests/modules/test_perf_coresight_compat.py:12` 用 `from common import glt_core`、`:14` 同时用 `from src.modules.hwtracing import ...`，两种风格 mock 的是不同路径的模块树。读测试代码必须先分辨当前用哪个根（流水线实证）。
2. **异常即信号 + 装饰器独占**：`GLTTestResult.fail()/skip()` 是抛异常而非返回值，因此 AGENTS.md 硬性规定禁止在非 @GLTTestAttr 装饰函数内调用——否则异常会逃逸成框架错误。AFAIL（allowed failure）语义独立于 FAIL，供"已知失败但想记录"的场景。
3. **探针各自独立 Makefile 而非统一 Kbuild**：每个探针目录一个 obj-m Makefile，测试代码运行时 chdir 进去现编现签现载。好处是探针零安装、随源码分发、按需构建；代价是每次测试付出编译时间，且 Secure Boot 环境必须预先登记 MOK。
4. **bpftrace 后置 PROBE_READY 防 race**：`observe.bt.in` 不用 `BEGIN{}` 打就绪标记，而用 `interval:s:1` 一次性后置守卫（`src/modules/iommu/cmdqv_hyp_own/observe.bt.in:81-97`）——BEGIN 在探针全挂上之前就执行，会让 runner 过早开 DMA 触发窗口产生假活信号（DISP-003）。模板占位符 `@@TARGET_SMMU@@` 由 runner 运行时替换（`src/modules/iommu/cmdqv_hyp_own_runner.py:468`）。
5. **不锁版本**：AGENTS.md 禁止提交 poetry.lock——测试对象是活的内核/OS，依赖锁定反而失真；运行依赖仅 pyyaml+packaging 两个。
6. **判定即证据**：测试大量绑定 kernel commit SHA 与 Jira 单号（如 SVA invalidate 回归对 commit 95a5885 的 TimeoutExpired 判 FAIL，`src/modules/iommu/glt_test_iommu.py:281-285`），失败信息直接给出"缺哪个补丁"。

## 七、新人上手路径（按 tour 顺序）

1. 读 `README.md`+`docs/home.md`+`docs/developer-docs/architecture.md`，建立"改什么放哪里"的全局观。
2. 过一遍 `install.sh` 与 `pyproject.toml`、systemd 单元，理解系统级安装形态与 MOK 前提。
3. 精读 `src/greenlit/greenlit.py` 主入口：参数→发现→调度→报告的主干。
4. 精读 `src/common/glt_core.py`：装饰器/异常族/GLTScheduler/PostHooks 是全框架的心脏。
5. 看 `glt_conf.py`+`00_default.yaml`+configuration 指南，理解条件跳过的编译与注入。
6. 浏览 `glt_utils.py`/`kernel_cmdline.py`/`perf_utils.py` 系统级工具底座（1300 行，用到再查）。
7. 读 `nv_device.py`+`hardware-manifest.json`+`cpu_topology.py`，掌握平台识别与按机型跳过机制。
8. 读 `glt_ext_launcher.py`+一个 external_tests 样例（mair_el1_war 套件），理解退出码契约。
9. 按 `writing-test-cases.md` 写第一个测试，样板：`src/modules/gpu/glt_test_nvidia_gpu.py:28`（persistence mode 检查）。
10. 进入探针深水区：cppc_cpc_read_probe（错误注入）→ aspm_saved_state_probe（kretprobe 观测）→ i2c kretprobe（backport 判定）。
11. 读 mm 域三资产：TLB flush 风暴、bingo.c 巨型段冒烟（`src/modules/mm/bingo/bingo.c:22` 512MB .bss）、contpte access flags 探针。
12. 读 IOMMU"观测+触发"范式：`observe_ste.bt:30` 按 comm 过滤 + `trigger.py:598` 纯 ctypes iommufd uAPI 驱动。
13. 读 virt 域 Arm CCA 测试与 glt_libvirt 封装，了解机密计算就绪检查。
14. 收尾质量防线：`tests/test_base.py:8` 基类→test_glt_core→test_greenlit，再读 AGENTS.md 硬边界清单。

## 八、常见坑与勘误（流水线实证）

- **nv_device docstring 复制粘贴 bug**：`src/common/nv_device.py:120` 写着 "Returns False if system has hopper GPU"——应为"没有 Hopper GPU 时返回 False"，读文档别被带偏，看实现。
- **CLAUDE.md 是符号链接**：9 字节 symlink → AGENTS.md，两份 agent 规范实为同一文件；`.gitlab-ci.yml` 是纯转发器（仅 include 外部 dgx/mgx/greenlit-ci@main 并用 GREENLIT_CI_REF 钉 ref），本仓内找不到任何本地 CI job 属正常。
- **进度文件真名是 test_progress.json**（`src/common/glt_session.py:25`），不是想当然的 progress.json。
- **hotplug_tlb/sva_invalidate 的 Makefile 不是 Kbuild**：没有 obj-m，是用户态程序交叉编译 Makefile（-ldl、aarch64-linux-gnu-gcc 回退），别按内核模块去找 .ko。
- **test_nvidia_tpm 是占位测试**：`src/modules/tpm/glt_test_tpm.py:42-44` 函数体只有一行 logger.info("PASS.")，TPM 域真实测试在同文件的 test_tegra_quad_spi/test_tegra_qspi_xfer_kasan_oob。
- **VERSION(3.1.1) 仓内零消费者**：Python 代码与打包配置都不读它，供外部发布流程用；pyproject.toml 里另有一份版本号，改版本要两处对齐。
- **00_default.yaml 的键只是"例外声明"**：真正测试函数在 src/modules 各域（pmu.py:683 实证），改条件别只改 YAML 不看测试。
- **XPASS(3) 按 FAILED 处理**：外部测试"预期失败却通过"视为失败，这是刻意设计（troubleshooting.md 有记载）。
- **无 root/无真机禁跑**：glt-test-suite 与 external_tests 全部与内核接口/物理设备交互，CI 与开发环境只能跑 tests/ 单测与 lint。
- **单测里 sys.path 双根**：mock `common.glt_utils` 不会影响 `src.common.glt_utils` 的引用者，写测试先统一导入根。

---
**元数据**：字数（不计空格）：7546 | 锚点：34 | 节数：8 | 图谱基线：1066n/2330e@550a74c | 撰写：understand-anything onboarding 流水线
