# CostAwareAlgorithm（团队 demo）

外部团队随包算法的最小示例。实现 [`cost_aware.py`](cost_aware.py)。

发现与默认安装不在本目录：由 [`../discover.py`](../discover.py) 扫描
`openjiuwen` 下所有子包（`test_algo`、`test_algo2` …）。

Python 算法只能做同步纯计算：不发网络请求、不读写文件、不修改跨请求状态。
