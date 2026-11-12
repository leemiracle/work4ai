# 03 · 打包部署链 —— Python 源到 systemd 服务

## 1. 角色定位

本篇覆盖交付链 8 个非 Python 文件（autogen.sh、configure.ac、两个 Makefile.am、DEBIAN 四件、service unit），把 9 个 Python 源变成 Debian 包：pyinstaller 打单文件装 /usr/sbin，unit 与配置随包安装，postinst 接驳 systemd。Autotools+pyinstaller 组合——用 C 构建系统打包 Python——是本仓最大坑源。

## 2. 内部结构

**bootstrap（autogen.sh）**：L12 预建 `config m4` 目录，L13 `autoreconf --force --install` 生成 configure，L15-20 检查 `$?` 报结果。

**配置（configure.ac）**：`configure.ac:3` `AC_INIT(hrgrest, 0.1)` 定包名版本——包名是 **hrgrest** 非 nvsm（第 5 节勘误）；L17-28 探测整套 C/Go 工具链；L34-38 声明三个输出：根 Makefile、子目录 Makefile、DEBIAN/control（control.in 替换而来）。

**顶层发布链（Makefile.am）**：L5 `release : rpm debian`；L8-13 强制 `--sysconfdir=/etc`；L16-19 以 `DESTDIR=$(PWD)/tmp_pkg_tree` 组装安装树；L21-26 `debian`：依赖前两步 → 拷入 DEBIAN → `fakeroot dpkg-deb --build` → `dpkg-name`。

**子目录（nvsm_exporters/Makefile.am）**：L11-19 用 9 个 .py 当 SOURCES；L21-22 unit 装 `$(libdir)/systemd/system`、L24-26 config 装 `$(sysconfdir)/nvsm-apis`；L28-30 覆盖 automake 链接规则：`pyinstaller --onefile main.py` 再 `mv dist/main`。

**Debian 脚本与 unit**：`postinst:7-13` daemon-reload + enable + restart；`prerm:3-4` stop + disable。`nvsm-prometheus-exporters.service:4` `After=nvsm-apis.service`、L7 ExecStart 指向产物、L8-9 `Restart=on-failure` 配 300 秒/10 次熔断。

## 3. 外部连接

- **模板替换链**：`./configure` 按 `configure.ac:34-38` 生成三文件——`control.in:2` 的 `@PACKAGE_VERSION@` 替换出 deb 版本号，缺这步 `make debian` 拿不到 DEBIAN/control。
- **工具依赖**：autoconf/automake、pip 装 pyinstaller（`README.md:21-22`）、fakeroot 与 dpkg-deb（`Makefile.am:25`）。
- **包间依赖**：`control.in:9` Depends 三项，末项 `nvsm-apis` 是命脉——273 端口服务与 JWT 都由它供给。

## 4. 数据流

```
autogen.sh:13 → configure（模板替换）→ make debian
  子 Makefile.am:29 pyinstaller → dist/main → 改名装 /usr/sbin
  顶层 Makefile.am:18-26 DESTDIR 组装 + DEBIAN → .deb
dpkg -i → postinst:7-13 reload/enable/restart
service:7 拉起单文件 → main.py 流程（见 01 篇）
```

三段接力零测试：无 make check、无 CI，质量靠部署后看指标。

## 5. 设计决策

**勘误（hrgrest 残留）**：`configure.ac:3` 包名 hrgrest 是复制其他项目模板的残留，连带 `AC_PROG_GO`（L21）、`includepaths` 空转目标（L15，全仓无实现）、C 工具链全套（L17-28）与 `config.h`（L9）——纯 Python 项目全用不上。distname 与 deb 包名（`control.in:1`）不一致但互不干扰；改 deb 版本仍回 L3。

**勘误（rpm 目标缺失）**：`Makefile.am:5` `release` 依赖 `rpm`，但全仓无 rpm 规则——`make release` 必报 "No rule"，只能 `make debian`；L39 清 `*.spec` 是 rpm 链被删后的残迹，release 属漏删。

**pyinstaller --onefile 的代价**：.py 列进 SOURCES（L11-19）只为骗 automake 追踪变更，真产物出自 L28-30；单文件是自解压 Python 非真编译，零依赖部署但排障无源码可读。

**postinst 直接 enable+restart**：装包即监控；升级时 restart 保证新二进制生效；prerm/postrm 极简，不碰配置与 JWT（属 nvsm-apis 包）。

## 6. 新人提示

- 只用 `make debian`；`make release` 因 rpm 缺失必失败。
- **configure 必带 `--sysconfdir=/etc`**，否则 `Makefile.am:8-13` 硬校验中断。
- **改版本号**在 `configure.ac:3` 参数二，流经 AC_SUBST 到 deb。
- **加新 exporter** 除 01 篇三处，还需 `nvsm_exporters/Makefile.am:11-19` SOURCES 加行。
- **别手工改装机后的 unit/config**：dpkg 不知情，升级即被覆盖；改源重新打包才是正路。

*锚自构建与打包文件核实（a892c4cc）。*