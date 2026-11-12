# DeepWiki 收录探测台账（2026-10-08）

| 项 | 结果 |
|---|---|
| 目标 | deepwiki.com/chromium/chromium（GitHub 镜像仓 chromium/chromium） |
| 直连/代理访问 | 429 Vercel Security Checkpoint（~34KB 挑战页，与 DeepChat 轮 2026-10-08 钉版一致） |
| Wayback CDX deepwiki.com/chromium* | 零快照（仅 2011-2013 旧站首页，彼时非 Devin DeepWiki） |
| **结论** | **NORESET——DeepWiki 通道不可用** |

## 处置（按用户预案：找替代 → 实在没有走深入分析）
1. 替代源 = 官方文档三站（全部代理可达 200）：
   - developer.chrome.com/docs/chromium（主文档中心）
   - chromium.org/developers（开发者入口/Getting Around the Code Base）
   - source.chromium.org（代码浏览，不抓）
   - + 仓内 src/docs/（源码下载完成后本地可用，最权威设计文档层）
2. 主菜 = understand 深入分析图谱（本体 = src 源码）
