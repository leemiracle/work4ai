# Coverage Check

## 2026-10-28 全量刷新（本轮）

- repo: vllm-project/vllm
- 通道: mcp.deepwiki.com/mcp（MCP 直连，绕开网页端 Vercel 盾）
- fetched: 2026-10-28
- 结构清单页数: 74 · 落盘页数: 74 · 覆盖 74/74 (100%)
- 全层级对账终判（dw_reconcile_dir.py）: struct=74 disk=74 extra=0 missing=0 → **TRUE_100**
- 对应源码基线: vLLM commit `06e172b5cf`（2026-10-28）

### 与 2026-09-02 版的差异

- 共同页 56 页**全部内容更新**（0 页未变）——DeepWiki 对 vLLM 做了整代重生成
- 新增 18 页 🆕：1.1/1.2/1.3（上手/示例/recipes）、4.6（确定性批不变）、5.6（vllm/models 厂商模型）、5.7（混合线性注意力）、5.8（pooling）、6.6（scale-out TITO）、7.5（自定义内核/C++扩展）、9.5（KV offload 分层）、9.6（权重传输×RL）、12.5（开发者工具治理）；改名扩展 5 处（5.2/6.3/8.2/12/12.4→新名）
- 移除 6 页（均为改名/重组旧名）
- 大幅扩容页：2.3 环境变量 +14KB、8.1 后端选择 +11KB、12.2 Buildkite +11KB、10.4 XPU/CPU/TPU +13KB、7.1 量化总览 +9KB
- 大幅精简页：13 术语表 -17KB、2 总章 -14KB、9.4 KV 传输 -12KB（细节下沉到新子页 9.5/9.6）

### 与图谱增量的互证

DeepWiki 新页主题与 understand 图谱增量（2026-09→10-28）高度互证：5.6↔vllm/models 新目录（DeepSeek V3.2/V4/V4.1 实现）、6.5↔rust/src 扩展、9.6↔entrypoints/rl+weight_transfer、1.3↔recipes/ 目录、6.3↔vllm/parser 新模块。

## 2026-09-02 首轮（历史）

- 62/62 页 100% 覆盖（dw_fetch.py 通道），3 页抽样正文校验 PASS
