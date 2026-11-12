# 03 · kernel-build.yml + config_4k/config_64k — 三档内核构建矩阵与 72 行页大小分叉

## 1. 角色定位

`kernel-build.yml`（98 行，workflow 名 Kernel Test）是"内核真的能编、能起、能过自测"的最终裁判：`workflow_dispatch` 下拉选 linux-nvidia-6.6/6.12/6.18（`kernel-build.yml:L3-13`），更常被 update-and-rebase.yml 每日 rebase 后以 `workflow_call` 复用（`.github/workflows/update-and-rebase.yml:L126/L133/L140`），`build_ref` 是刚推的 `<branch>-<tag>` 标签。`config_4k`/`config_64k`（约 1.47 万行）是 ARM64 两档武器：同为 Linux 6.12.33 基线、gcc 15.1.1 生成（`config_4k:L3-5`），仅 72 行差异（`<` 51 + `>` 21）——但这 72 行把内核切成 4K 与 64K 两个世界。

## 2. 内部结构

**矩阵**（`L26-33`）：三档 include——ubuntu-latest+defconfig、ubuntu-24.04-arm+config_4k、ubuntu-24.04-arm+config_64k（原生 ARM runner 非交叉模拟），job 名动态拼 x86_64/ARM64（`L23`）。**步骤链**：checkout 指定 ref 且 `fetch-depth: 0`（`L35-39`，用 `actions/checkout@v4`）；从 `origin/github-actions` 分支取两份 config（`L41-44`，内核分支不携带 CI 资产）；装 40+ 依赖含 `gcc-aarch64-linux-gnu` 交叉链（`L46-61`）；源码装 virtme-ng（`L63-68`）；Configure 步 `vng -vb --kconfig --config <file>` 注入后强制关 `CONFIG_WERROR`/`SYSTEM_TRUSTED_KEYS`/`SYSTEM_REVOCATION_KEYS`（`L70-81`，CI 无签名证书，不关必败）；`vng -vb` 编译（`L83-85`）；`vng -v -m 4G -- uname -a` 启动冒烟（`L87-89`）；kselftest 只跑 `TARGETS="mm dma iommu locking"`（`L91-98`）。

**config 差异骨架**：页大小开关 `CONFIG_ARM64_4K_PAGES=y`（`config_4k:L456`）对 `CONFIG_ARM64_64K_PAGES=y`（`config_64k:L452`），其余全是级联——`PAGE_SHIFT` 12→16（`config_4k:L835`/`config_64k:L819`）、`PGTABLE_LEVELS` 4→3（`L335`/`L332`）、`CONT_PTE_SHIFT` 4→5（`config_4k:L318`/`config_64k:L315`）、`MMAP_RND_BITS_MIN` 18→14（`L320`/`L317`）、`ARCH_FORCE_MAX_ORDER` 10→13（`L496`/`L491`）、`CONFIG_COMPAT=y` 整族仅 4K（`config_4k:L502`）、`THP_SWAP` 同（`config_4k:L1091`）、三级页表禁用项口径从 `VA_BITS_39`（`config_4k:L459`）换 `VA_BITS_42`（`config_64k:L453`）。

## 3. 外部连接

上游：update-and-rebase.yml 三个 build job 以 `uses: ./.github/workflows/kernel-build.yml` 消费（`L126/L133/L140`），条件 `!cancelled() && tag-6-x != ''`，rebase 失败不连坐；矩阵输出 `tag-6-6/6-12/6-18` 由 matrix job 聚合。横向：config 经 checkout 从 github-actions 分支来（`kernel-build.yml:L41-44`），与 patchscan.yml 取脚本同范式；`actions/checkout@v4`（`L36`）比 patchscan.yml 的 `@v6` 旧两代——全仓三种钉法并存（两处 tag、validate-pr-tests.yml SHA 钉）。

## 4. 数据流

输入唯一参数 `build_ref`（dispatch 是 choice 枚举、workflow_call 是裸 string，`L6/L16`——choice 类型不能跨 workflow 边界，故同参不同型）。流程：checkout ref → 注入 config → vng 编译出带 initramfs 的可启动内核 → QEMU/KVM 起机跑 `uname -a` → 编并跑四子系统自测（`--summary`）。无产物上传——**这是测试门不是发布管线**，成功即绿，失败即阻塞当日 rebase。

## 5. 设计决策

- **为何双页档**：页大小是 arm64 ABI 级配置——TLB 粒度、contiguous PTE、mmap 随机化位宽、伙伴系统阶数全随之改变，NVIDIA arm64 平台两档都在生产用，只测一档等于漏测一半内核。kselftest 精选 mm/iommu 正是对页大小最敏感的面。
- **72 行是语义级联不是漂移**：两 config 以同一 6.12.33 源树、同一 gcc 生成，只翻页大小开关再 olddefconfig，diff 每行皆可归因——config 当"派生物"管理的可审计范式。
- **`ARCH_FORCE_MAX_ORDER` 10→13**（`L496`/`L491`）：页变大 16 倍后最大阶数上调维持连续块量级；`MMAP_RND_BITS` 同理下调（`L320`/`L317`）。
- **`COMPAT` 只在 4K 开**（`config_4k:L502`）：64K 页下 AArch32 布局受限直接整族关闭——两档能力面不对等，选档须知。
- 【勘误/注意】`L81` 的 `--disable SYSTEM_REVOCATION_KEYS ""` 悬挂空串参数，属笔误形态；矩阵未显式 `fail-fast: false`（默认 true），一档失败取消其余档，与 update-and-rebase.yml 的策略不一致。

## 6. 新人提示

改 config 永远走"翻开关+`make olddefconfig` 重生成"，两份同源生成保持 diff 最小；手改单行会造成级联漂移。加 kselftest TARGETS 先估时长（ARM runner 慢）。`build_ref` 手动入口只有三分支可选，rebase tag 只能经流水触发。WERROR/证书三关（`L78-81`）是 CI 救生索，别"恢复"。
