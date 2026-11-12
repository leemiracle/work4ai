# 讲透Termux — termux org 全量知识库（2026-10-26）

源：github.com/termux 全部 63 公开仓（含 fork/archived，本地克隆 /usr-data/data2/repos/termux-repo，--depth 1，63/63 零失败）。

## 三步流水线状态

| 步骤 | 状态 |
|---|---|
| ① clone | ✅ 63/63（2026-10-26）|
| ② DeepWiki | ✅ 收官：24 仓收录全量抓取（全层级对账 TRUE100），39 仓未收录（MCP "Repository not found"，jina 通道 000 不可达无法二次甄别；走 understand 图谱唯一知识源先例）|
| ③ understand 图谱 | ✅ **四仓全链完成**（2026-10-27）：termux-app 1284n/2762e · proot-distro 1800n/3670e · proot 892n/1861e · termux-x11 519n/923e（合计 4495n/9216e，全部 0 issues+fingerprints 基线）|
| ④ onboard+explain | ✅ 四仓各 ONBOARDING + explain 12 篇（共 48 篇，全部行号锚现场核实）|

## 63 仓明细（DeepWiki 收录状态）

| 仓 | DeepWiki | 页数 | archived | fork | stars |
|---|---|---|---|---|---|
| [termux-app](https://github.com/termux/termux-app) | 收录 | 46 |  |  | 63430 |
| [termux-packages](https://github.com/termux/termux-packages) | 收录 | 33 |  |  | 17229 |
| [termux-x11](https://github.com/termux/termux-x11) | 收录 | 22 |  |  | 5021 |
| [termux-api](https://github.com/termux/termux-api) | 收录 | 16 |  |  | 4529 |
| [proot-distro](https://github.com/termux/proot-distro) | 收录 | 24 |  |  | 3583 |
| [termux-styling](https://github.com/termux/termux-styling) | 收录 | 20 |  |  | 1910 |
| [termux-widget](https://github.com/termux/termux-widget) | 收录 | 20 |  |  | 1839 |
| [termux-boot](https://github.com/termux/termux-boot) | 收录 | 21 |  |  | 1828 |
| [termux-api-package](https://github.com/termux/termux-api-package) | 收录 | 11 |  |  | 1731 |
| [termux-tasker](https://github.com/termux/termux-tasker) | 收录 | 19 |  |  | 1633 |
| [termux.github.io](https://github.com/termux/termux.github.io) | 收录 | 37 |  |  | 1491 |
| [termux-root-packages](https://github.com/termux/termux-root-packages) | 收录 | 16 | ✓ |  | 1220 |
| [termux-gui](https://github.com/termux/termux-gui) | 收录 | 24 |  |  | 1202 |
| [proot](https://github.com/termux/proot) | 收录 | 18 |  |  | 1161 |
| [termux-tools](https://github.com/termux/termux-tools) | 收录 | 27 |  |  | 898 |
| [termux-float](https://github.com/termux/termux-float) | 收录 | 19 |  |  | 872 |
| [termux-docker](https://github.com/termux/termux-docker) | 收录 | 24 |  |  | 748 |
| [termux-services](https://github.com/termux/termux-services) | 收录 | 22 |  |  | 462 |
| [termux-apt-repo](https://github.com/termux/termux-apt-repo) | 收录 | 15 |  |  | 410 |
| [game-packages](https://github.com/termux/game-packages) | 收录 | 15 | ✓ |  | 386 |
| [termux-exec-package](https://github.com/termux/termux-exec-package) | 收录 | 14 |  |  | 266 |
| [termux-language-server](https://github.com/termux/termux-language-server) | 收录 | 25 |  |  | 199 |
| [TermuxAm](https://github.com/termux/TermuxAm) | 收录 | 20 |  |  | 148 |
| [termux-core-package](https://github.com/termux/termux-core-package) | 收录 | 14 |  |  | 41 |
| [x11-packages](https://github.com/termux/x11-packages) | 未收录 | 0 | ✓ |  | 655 |
| [termux-create-package](https://github.com/termux/termux-create-package) | 未收录 | 0 |  |  | 509 |
| [termux-auth](https://github.com/termux/termux-auth) | 未收录 | 0 |  |  | 281 |
| [termux-elf-cleaner](https://github.com/termux/termux-elf-cleaner) | 未收录 | 0 |  |  | 276 |
| [science-packages](https://github.com/termux/science-packages) | 未收录 | 0 | ✓ |  | 247 |
| [command-not-found](https://github.com/termux/command-not-found) | 未收录 | 0 |  |  | 203 |
| [libandroid-shmem](https://github.com/termux/libandroid-shmem) | 未收录 | 0 |  |  | 165 |
| [play-audio](https://github.com/termux/play-audio) | 未收录 | 0 |  |  | 145 |
| [repology-metadata](https://github.com/termux/repology-metadata) | 未收录 | 0 |  |  | 138 |
| [termux-packaging](https://github.com/termux/termux-packaging) | 未收录 | 0 | ✓ |  | 122 |
| [glibc-packages](https://github.com/termux/glibc-packages) | 未收录 | 0 |  |  | 116 |
| [termux-root-packages-21-bin](https://github.com/termux/termux-root-packages-21-bin) | 未收录 | 0 |  |  | 112 |
| [termux.com](https://github.com/termux/termux.com) | 未收录 | 0 |  |  | 95 |
| [openjdk-mobile-termux](https://github.com/termux/openjdk-mobile-termux) | 未收录 | 0 |  | ✓ | 74 |
| [android-build-tools](https://github.com/termux/android-build-tools) | 未收录 | 0 |  |  | 63 |
| [termux-failsafe](https://github.com/termux/termux-failsafe) | 未收录 | 0 | ✓ |  | 62 |
| [termux-community](https://github.com/termux/termux-community) | 未收录 | 0 |  |  | 60 |
| [termux-am-socket](https://github.com/termux/termux-am-socket) | 未收录 | 0 |  |  | 59 |
| [game-packages-21-bin](https://github.com/termux/game-packages-21-bin) | 未收录 | 0 |  |  | 56 |
| [tsu](https://github.com/termux/tsu) | 未收录 | 0 |  | ✓ | 55 |
| [science-packages-21-bin](https://github.com/termux/science-packages-21-bin) | 未收录 | 0 |  |  | 51 |
| [wcwidth](https://github.com/termux/wcwidth) | 未收录 | 0 |  |  | 45 |
| [upload-release-action](https://github.com/termux/upload-release-action) | 未收录 | 0 | ✓ | ✓ | 44 |
| [libandroid-support](https://github.com/termux/libandroid-support) | 未收录 | 0 |  |  | 43 |
| [getconf](https://github.com/termux/getconf) | 未收录 | 0 |  |  | 34 |
| [termux-am-library](https://github.com/termux/termux-am-library) | 未收录 | 0 |  |  | 33 |
| [whatprovides](https://github.com/termux/whatprovides) | 未收录 | 0 | ✓ |  | 28 |
| [ndk-toolchain-clang-with-flang](https://github.com/termux/ndk-toolchain-clang-with-flang) | 未收录 | 0 |  |  | 19 |
| [shared-library-testcase](https://github.com/termux/shared-library-testcase) | 未收录 | 0 |  |  | 19 |
| [ghc-cross-tools](https://github.com/termux/ghc-cross-tools) | 未收录 | 0 |  |  | 18 |
| [distfiles](https://github.com/termux/distfiles) | 未收录 | 0 |  |  | 17 |
| [create-conventional-changelog](https://github.com/termux/create-conventional-changelog) | 未收录 | 0 |  |  | 16 |
| [rustls-native-certs](https://github.com/termux/rustls-native-certs) | 未收录 | 0 |  | ✓ | 16 |
| [libandroid-utimes](https://github.com/termux/libandroid-utimes) | 未收录 | 0 |  |  | 14 |
| [termux-fix-shebang](https://github.com/termux/termux-fix-shebang) | 未收录 | 0 |  |  | 14 |
| [tergent](https://github.com/termux/tergent) | 未收录 | 0 |  | ✓ | 13 |
| [termux-apt-repo-backups](https://github.com/termux/termux-apt-repo-backups) | 未收录 | 0 |  |  | 8 |
| [mirror-minder](https://github.com/termux/mirror-minder) | 未收录 | 0 |  | ✓ | 7 |
| [deno-snapshot](https://github.com/termux/deno-snapshot) | 未收录 | 0 | ✓ |  | 6 |

## 工具与坑（钉版）

- 抓取：pipeline-bin/deepwiki/dw_fetch_mcp.py（MCP 通道，curl 子进程直连）；终判：全层级对账（本仓 /tmp/opencode/termux_dw_reconcile.py，dw_reconcile_full 参数化版）。
- **新坑：exit 1 歧义**——dw_fetch_mcp 的覆盖率闸 sys.exit(1) 与 python 未捕获异常（Repository not found）同 exit 1，worker 三态判定必须 grep 日志里的 "not found/isError" 先于 rc==1 分支。
- 台账：/usr-data/data2/repos/termux-repo/_dw_results.tsv（DONE 24 / NOINDEX 39）。

## 源码级勘误与发现清单（understand 图谱+explain 阶段产出，2026-10-26~27）

### termux-app（12 篇 explain + ONBOARDING）
1. **ExtraKeysView.setLongPressRepeatDelay 疑似 bug**（ExtraKeysView.java:356-362）：区间校验两操作数误用字段 `mLongPressRepeatDelay` 而非参数——MIN/MAX 防线失效，外部传 0 可致 `scheduleWithFixedDelay(...,0)` 抛 IllegalArgumentException；对照 :342-348 正确写法，一行修法。
2. **local-socket 三缺陷**（与上游 master 同源）：readNative 分片读传全长（local-socket.cpp:390，越界风险）；runAmCommand 失败缺 return（AmSocketServer.java:119-124）；available() 误传服务端 fd（LocalClientSocket.java:277）。
3. TermuxConstants 注释≠值 ×3：TERMUX_FLOAT_SERVICE action 注释写 `com.termux.float.*` 实算 `com.termux.window.*`（:1248）；EXTRA_PLUGIN_API_HELP 注释 plugin_help 实为 plugin_api_help（:1029）；Float 通知 ID javadoc 错归属（:873）。
4. TermuxService switch 仅四 action，图谱摘要的 START_SERVICE 不存在（:141-156）；TermuxSession javadoc 写 SIGILL 实发 SIGKILL（:205）。
5. `toogleShowTerminalToolbar` 拼写错误冻结进公共 API（TermuxAppSharedPreferences.java:79）；TerminalEmulator 自述 "emulates a subset"（DA2 谎报 320 为刻意兼容设计 :1901）。

### proot（12 篇 explain + ONBOARDING）
1. **扩展事件 23 个非 21**（extension.h:33-176）：`[A-Z_]+` 类正则漏掉含数字的 LINK2SYMLINK_RENAME/UNLINK——"21"是计数工具假象（勘误的再勘误）。
2. fake_id0 元文件前缀实为 `.proot-meta-file.`（helper_functions.h:13），非 `.proot.meta`。
3. 构建系统纯 GNUmakefile+特性探测（.check_*.c→build.h），全仓无 CMake/meson。
4. proot.h 声称 "automatically generated from the documentation"，但 fork 新增选项（-H/-p/-L/--link2symlink/--sysvipc，proot.h:237-290）在 manual.txt 中 grep 不到——文档生成链已断裂，实为手改维护。
5. swap_config()（tracee.c:1027-1040）src/ 全树零调用者=孤儿 API；ldso.c:108 is_known 只置位无读取=死代码；src/GNUmakefile uninstall 目标（L276-283）规则体复制的是 install 命令非 rm。

### termux-x11（ONBOARDING + explain 进行中）
1. **buffer.c:433 潜伏指针 bug**：`outBuffer = NULL` 应为 `*outBuffer = NULL`（局部参数赋值）。
2. **InitOutput.c:867-868 上游笔误**：mmHeight 误用 `mode->mode.width` 计算（对照 :706-707 正确写法）。
3. Xau.cmake:4 `target_compile_options(Xdmcp ...)` 目标名误写，编译选项落不到 Xau 库。
4. bzip2 是唯一零消费孤儿 submodule（Xfont2.cmake:59 显式禁用）；xserver_main 编而未链（不在 XSERVER_LIBS，孤儿目标）。
5. lorie.h:245 注释宣称 eglSwapInterval(1)，实际代码为 0（renderer.cpp:286/745）——节流已移交 waitForNextFrame+AChoreographer；`-force-bgra` 死开关（InitOutput.c:366-367 零消费者）。
6. activity.cpp:106/118 poll 超时注释打架（实际 20ms）；IntPreference.defValue() 返回存储值而非默认值（LoriePreferences.java:857-860）。

### proot-distro（12 篇 explain + ONBOARDING，2026-10-27 补录）
1. **atomic.py 无 fsync 勘误**：真实链是 O_EXCL tmp→写→close→lstat/fstat inode 对账→os.replace，承诺 rename 原子性（读者不见半文件）非断电持久性（atomic.py:228-240）。
2. Python 重构版无发行版表（shell 版 SUPPORTED_DISTRIBUTIONS 已废），改 Docker registry 直连任意发行版（help/__init__.py:68-71）。
3. `--` 分隔符是内部命令强制契约：argparse 收进 login_cmd 后被 _split_separator 静默重置丢弃（cli.py:307-309）。
4. 三 shell 补全是七副本平行实现（含 Python 侧），tests/ 零引用=CI 无同步防护；fish 562 行比 bash/zsh 多 65% 因 pd 入口全量复制。
5. 实测新知：OCI 层串行下载是正确性要求（whiteout 顺序依赖）非性能缺陷；层缓存威胁模型=缓存目录 guest 可写（$TERMUX_PREFIX 绑定进容器）。

## 许可证与商用注意事项（2026-10-27，LICENSE 文件实证）

**核心误解纠正：GPL 系全部允许商用**（收费/卖产品/闭源服务都合法）；差别在分发时被要求回报什么。

### 许可证地图
| 范围 | 许可证 | 分发时义务 | 闭源可行性 |
|---|---|---|---|
| termux-app 主应用 | **GPLv3 only**（非 "or later"）| 提供完整源码含修改；反 Tivoization；专利授权 | ❌ |
| ├ terminal-view / terminal-emulator | Apache 2.0（继承 jackpal）| 保留 NOTICE；专利授权 | ✅ |
| └ termux-shared 库 | **MIT 为默认** + 例外：`termux/*` 子包 GPLv3（TermuxConstants/TermuxPropertyConstants 两文件单独 MIT）；`file/filesystem/*` GPLv2+Classpath 例外（libcore/ojluni 血统，链接方可闭源）| MIT 仅需保留声明 | ✅（避开 termux/*）|
| proot（Termux fork）| **GPLv2**（上游遗留）| 提供源码；无反 Tivoization/专利条款 | ❌（本体）|
| proot-distro / termux-x11 / termux-tools | GPLv3 | 同 GPLv3 | ❌ |

### 商用场景决策树
```
只用不分发（含服务器跑，GPL 非 AGPL 无网络条款） → 零义务
闭源 App 想要终端能力        → 取 terminal-view/emulator（Apache 2.0），别碰 termux-app 其余部分
做插件/配套 App              → 链接 termux-shared MIT 部分（官方四插件同路）；碰 termux/* 子包回落 GPLv3
fork 整个 App 分发           → 接受 GPLv3 开源；收费合法（服务/支持/预装硬件），"only" 措辞禁升 v4
商业产品带 proot             → proot 二进制附源码；guest 程序闭源没问题（进程聚合非链接）
预装硬件锁 bootloader        → GPLv3 反 Tivoization 是雷（v2 无此条款）
```

要点：termux-shared 的 MIT 默认是策略性开口（JitPack 发布供第三方插件链接而不被传染），但 TermuxConstants fan-in 33 的插件契约面正落在 GPLv3 边界上。工程实务判断，正式商业决策让法务过终稿——尤其 GPLv3 反 Tivoization 在 Android 签名体系下的适用边界有解释空间。
