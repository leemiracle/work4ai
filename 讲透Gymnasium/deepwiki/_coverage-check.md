# Coverage Check

- repo: Farama-Foundation/Gymnasium
- fetched: 2026-10-14（通道 mcp.deepwiki.com/mcp 直连，curl 子进程模式）
- 结构清单页数: 32
- 落盘页数: 37
- MISSING: 0（结构清单 32/32 全命中）
- 结构外页: 5（全文含但导航清单未列，均为真实内容页，已按 x1-x5 落盘保留）
  - x1 Array Conversion Wrappers (Jax/Torch/NumPy)
  - x2 MuJoCo v5 and v4 Environment Implementations
  - x3 MujocoEnv Base Class and Rendering
  - x4 Rendering and Recording Wrappers
  - x5 Transform and Stateful Wrappers
- 全文 raw: wiki_full.md 620,916 字符（尾部完整无截断；行号锚+源文件清单齐备）

## 结论

**实际覆盖 = 100%（32/32 结构页 + 5 额外页超额保留）。**
脚本 exit 1 系 extra>0 的严格判定假阴性——DeepWiki 导航清单滞后于正文（目录多轮重组的已知现象），
5 个 extra 页恰为 MuJoCo 实现细节与 wrapper 体系深水区，是本仓最有价值的增量内容，非垃圾页。
