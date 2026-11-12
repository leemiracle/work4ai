# 03 · 测试体系与 tutil：预生成 PTX 的免工具链回归

## 角色定位

`test/` 是绑定层的回归防线：四个测试文件验证句柄创建、模块编译、程序组与管线的绑定正确性。设计要点是**测试不依赖本机 CUDA/NVRTC**——PTX 全部预生成为字符串常量，任何有 OptiX 驱动与 RTX 卡的机器都能跑。

## 内部结构

入口 `test/conftest.py` 仅一行实效代码：`sys.path.append(os.path.join(os.path.dirname(__file__), 'util'))`（conftest.py:8），让测试文件裸名 `import tutil`/`import sample_ptx`。`test/util/tutil.py`（426 行）两段式：主体是 PTX 常量——`ptx_string_old` 为 `.version 7.1` 老格式（tutil.py:10/:19，NVVM 产物），新版常量带 `.visible` 限定符（tutil.py:26 起 `__raygen__hello` 及 :257-347 的 noop 全家：anyhit/closesthit/intersection/miss/direct_callable/continuation_callable）；尾部是共享工具 Logger 回调类（tutil.py:382）、`create_default_ctx`（tutil.py:395）、`optix_version_gte`（tutil.py:402）、`default_debug_level`（tutil.py:410，按 7.1+ 分支选 COMPILE_DEBUG_LEVEL）、`create_default_module`（tutil.py:418，一步返回 (ctx, module) 元组）。`test/sample_ptx.py`（620 行）是第二批夹具：`hello_ptx`（sample_ptx.py:6）与 `triangle_ptx`（sample_ptx.py:278），CUDA 11.2 NVVM 编译产物（sm_60）。

## 外部连接

四个测试文件各司其职：`test_context.py` 验句柄构造（test_context.py:26 test_default_ctor 起）；`test_module.py` 验模块编译面（test_module.py:122 test_create_destroy、:146 test_payload_semantics_use、:178 bound_values、:209 builtin_is_module_get）；`test_program_group.py` 最全，覆盖四种程序组（test_program_group.py:57 raygen/:75 miss/:94 callables/:115 hitgroup）加 stack size（:152），基类 setup_method/teardown_method 每用例建拆 ctx+module（test_program_group.py:18）；`test_pipeline.py` 验管线选项（test_pipeline.py:18）。测试发现由 pyproject.toml:70-72 的 testpaths=test 钉死。

## 数据流

PTX 常量 → `create_default_module`（tutil.py:418）走 moduleCreateFromPTX → 程序组/管线照常构建 → 断言句柄与属性。Logger（tutil.py:382）挂到 DeviceContext 收日志回调，出错时给出 OptiX 诊断文本。

## 设计决策

- **PTX 跨版本双轨**：old（7.1 无 .visible）+ new 双常量并测，专防"旧 PTX 在新 OptiX 上被拒"的兼容回归——tutil.py:410 的 default_debug_level 同样按 7.1 分支。
- **夹具下沉 util 而非 conftest fixture**：conftest 只做 sys.path（conftest.py:8），工具显式 import，测试文件自包含可读。
- **测试依赖最小化**：test 组只有 pytest（pyproject.toml:45-47），cupy/numpy 都不进——与 examples 组严格分离。

## 新人提示

跑测试必须 `pytest`（直接 `python test/test_module.py` 会因 sys.path 注入未发生而 ImportError）；加新 PTX 夹具放 sample_ptx.py 而非 tutil.py，保持"工具库/夹具库"分工；noop 全家（tutil.py:257-347）是拼装任意程序组的最小积木。
