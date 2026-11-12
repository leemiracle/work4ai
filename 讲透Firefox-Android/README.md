# 讲透 Firefox for Android（mozilla-central Android 版）

> 生成：2026-10-09 · 源码锚点 hg `3e41f4d5acb8`（2026-10-07 tip）· 源 `https://hg-edge.mozilla.org/mozilla-central`

## 产物导航

| 路径 | 内容 |
|---|---|
| `deepwiki/firefox-android/` | DeepWiki：mozilla-mobile/firefox-android 全 20 页 100%（Fenix UI 架构/主题、AC 引擎抽象/状态管理、Focus、i18n、测试、遥测） |
| `deepwiki/gecko-dev/` | DeepWiki：mozilla/gecko-dev 全 26 页 100%（mozilla-central 官方 GitHub 镜像的 wiki；6 Mobile Platforms = Fenix/AC/GeckoView 三章 + 7.2 Android Build Configuration 重点关注） |
| `analysis/ARCHITECTURE-NOTES.md` | 源码实证深入分析：四大子系统依赖图、144 个 AC 组件版图、构建系统、DeepWiki 路径映射勘误 |
| `analysis/00-07*.txt` | 结构扫描素材：目录树、组件清单、文件统计、版本锚点、variables.gradle |

## 源码本地位置

`/usr-data/data1/browser/mozilla-central`（完整 hg 仓 15GB，含全部历史；mobile/android 15,285 文件 = fenix 3,871 + android-components 9,471 + focus-android 742 + geckoview 614）

更新方式：
```bash
cd /usr-data/data1/browser/mozilla-central && ~/.local/bin/hg pull -u https://hg-edge.mozilla.org/mozilla-central
```

## 渠道决策记录（钉版）

1. **hg-edge 是唯一权威现行源**：GitHub `mozilla/gecko-dev` 镜像 2025-07-09 已停更；DeepWiki 两个 wiki 快照均滞后（firefox-android 为 2023-11 合仓前布局，gecko-dev 为 2025-07 前）。
2. **源码获取**：hgweb archive 端点 403（禁用）→ 走官方 CDN clonebundle（zstd-max 2.8GB）。代理通道长连接会被挂起停滞；**S3 直连 + curl 4 路 Range 分段 + 每轮 HTTP 206 校验追加**稳定 2.8MB/s（单连接被限速 ~0.9MB/s）。
3. **DeepWiki 通道**：网页端被 Vercel 盾拦 → `mcp.deepwiki.com/mcp` stateless MCP 端点（`dw_fetch_mcp.py`，REA 轮钉版工具复用），两仓均一次 100%。
4. **坑钉版**：分段下载若直接 `-r A-B -o - >> part` 追加，S3 偶发 200 全文响应会污染分块（首拼报废 2.7GB 重下）——必须 tmp 文件 + 校验 `http_code==206 && size_download==tmp大小` 才可追加。

## 阅读建议

1. 先 `analysis/ARCHITECTURE-NOTES.md` 建立当前源码的全景（最新布局）
2. DeepWiki `deepwiki/gecko-dev/6.3-geckoview.md` + `deepwiki/firefox-android/2.1-browser-engine-abstraction.md` 对照理解 GeckoView 桥
3. DeepWiki `deepwiki/firefox-android/3.1-fenix-ui-architecture.md`（源文件清单含 `fenix/` 前缀，按 §6 映射表换算路径）
