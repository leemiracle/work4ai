# DeepWiki 抓取覆盖率检查

- _links.txt 链接总数: 25
- 实际 md 文件数: 24
- 缺失页: 1
- 空页(<= 500B): 0

## 结论
存在缺口，需补抓（重跑 dw_fetch.py 即断点续传补缺）：
- 缺失: 6.2-fused-swiglu-+-quantization-kernels

## 抽查 3 页

| 页面 | 大小(B) | 状态 | 检查 |
|---|---|---|---|
| 4.1-mhc-kernels | 12986 | 正常 | PASS |
| 5.2-moe-dispatch-and-reduction-kernels | 8406 | 正常 | PASS |
| 4.2-mhc-modeling-api | 11769 | 正常 | PASS |

