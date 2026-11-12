# Python 算法回接 Rust 示例

本目录在 `openjiuwen` **包外**，表示安装 wheel 之后宿主自己写算法。
[`prefer_first.py`](prefer_first.py) 演示如何实现 `decide(request, ctx)`。
`discover` 只扫描 `openjiuwen` 的子包，**不会**扫到这里；但导入本类时，
带稳定 `name` 且能无参构造的 `AlgorithmProvider` 子类会自动写入槽位。

```text
import PreferFirstAlgorithm
  -> 类定义时按 name 写入进程内注册表
  -> from_config(algorithm = "custom_prefer_first")
  -> PyAlgorithmAdapter 回调 obj.decide(request, ctx)
```

运行时先构建扩展，再执行示例：

```bash
maturin develop
python python/custom_test_algo/run_custom_algorithm.py
pytest tests/test_custom_algorithm.py -v
```

算法名必须与 TOML 中的 `algorithm` 一致（本示例为 `custom_prefer_first`）。
配置写在类属性上，不要给构造函数传参。
Python 算法只能做同步纯计算：不发网络请求、不读写文件、不修改跨请求状态。
