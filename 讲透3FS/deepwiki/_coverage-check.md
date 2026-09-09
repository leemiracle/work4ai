# DeepWiki 抓取覆盖率检查

- _links.txt 链接总数: 50
- 实际 md 文件数: 48
- 缺失页: 2
- 空页(<= 500B): 0

## 结论
存在缺口，需补抓（重跑 dw_fetch.py 即断点续传补缺）：
- 缺失: 2.3-c++-build-configuration
- 缺失: 5.1-rust-c++-integration

## 抽查 3 页

| 页面 | 大小(B) | 状态 | 检查 |
|---|---|---|---|
| 6-distributed-services | 8447 | 正常 | PASS |
| 10-observability-and-monitoring | 7025 | 正常 | PASS |
| 8-storage-client | 6765 | 正常 | PASS |

