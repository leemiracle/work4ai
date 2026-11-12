# DeepWiki 抓取覆盖率检查

- _links.txt 链接总数: 37
- 实际 md 文件数: 35
- 缺失页: 2
- 空页(<= 500B): 0

## 结论
存在缺口，需补抓（重跑 dw_fetch.py 即断点续传补缺）：
- 缺失: 7-c++-runtime-and-build-system
- 缺失: 7.1-elasticbuffer-c++-implementation

## 抽查 3 页

| 页面 | 大小(B) | 状态 | 检查 |
|---|---|---|---|
| 10.1-code-formatting-and-linting | 8904 | 正常 | PASS |
| 5.3-nccl-backend-integration | 9751 | 正常 | PASS |
| 5.4-legacy-kernels-(v1) | 10507 | 正常 | PASS |

