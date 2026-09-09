# 精讲：Python 异步 serve 引擎与前缀缓存

> 位置：`python/mlc_llm/serve/engine.py`（1946 行）+ `engine_base.py`（1278 行）+ `radix_tree.py`（154 行）
> 图谱：engine_base fan-out 12/16；prefix cache 为连续批处理性能关键
> 注：原述 async_engine.py 实为 engine.py+engine_base.py 二人组

## 角色定位

Python 宿主层：把 C++ 推理引擎包成 OpenAI 风格异步 API。妙在「薄」——调度/prefill/decode/采样都在 C++，Python 只做**协议翻译、异步流管理、增量 detokenization**。

`radix_tree.py` 薄到极致：154 行全 FFI 声明，本体在 `cpp/serve/radix_tree.cc`（845 行）；保留 Python 壳为 serve 侧直接操作前缀缓存。

## 内部结构

**engine.py 代理类族**：Chat/ChatCompletion/Completion 三接口 ×{Async,同步} 六个代理，模仿 OpenAI SDK 形态（`engine.chat.completions.create(...)`）——量大但纯协议。

**AsyncMLCEngine**：
- `_chat_completion`/`_completion`：参数→Pydantic 模型→`_handle_chat_completion` 渲染模板+编码→`async for` `_generate` 转流式响应 yield
- `_generate`（核心枢纽）：FFI 建请求+`AsyncRequestStream` 注册进 `state.async_streamers`（request_id 索引，n 个 TextStreamer）→ `add_request` 下沉 C++ → `async for ... yield`——**生产者在另一线程，这里只是消费者**
- `MLCEngine` 同步版：差异仅回调注入队列轮询

**engine_base.py 的 MLCEngineBase**：
- `__init__`：`get_global_func("mlc.serve.create_threaded_engine")` 拿 C++ 模块 → 注入设备与**流式回调** → **起双后台线程**（驱动+回传）→ `reload` 传配置 JSON 建引擎
- async 回调关键一行：`call_soon_threadsafe(...)`——C++ 输出安全投递回事件循环（注释坦承有 GIL）
- `_async_request_stream_callback_impl`：增量 detok；**final chunk 哨兵=usage JSON 非空**，final 时 push+finish+清理注册表
- `process_chat_completion_request` 等纯函数：模板渲染/停止条件/logprobs——同步异步共享

**radix_tree.py 的 PagedRadixTree**：七方法全转 FFI——`match`（最长公共前缀）、`add`/`remove`/`extend`、`rollback`（投机解码拒绝分支）、`fork`（父序列分叉，n>1 与 EAGLE 树）、`free_capacity`；tokens 走 `tvm_ffi.Shape` 零拷贝。

## 外部连接

- **向下**：`_ffi_api.py` get_global_func 直达 C++ ThreadedEngineModule
- **向上**：openai_entrypoints.py（REST）、interface/serve.py、bench
- **横向**：protocol/（Pydantic 模型）、tokenizers/、conversation_template（深拷贝防串话）

## 数据流

```
用户协程: await engine.chat.completions.create(..., stream=True)
→ _handle_chat_completion: 模板渲染+tokenize
→ _generate: 注册 AsyncRequestStream → FFI add_request
   ──▶ [C++线程1: 指令队列→EngineImpl.Step() 产出输出]
   ──▶ [C++线程2: StreamBackLoop 批量回调]
→ Python 回调: call_soon_threadsafe 投递
→ [事件循环]: delta_token_ids→TextStreamer→delta_text→stream.push
→ 用户协程 async for 收到流式响应
```

radix 在上游：C++ prefill 先 `match`（命中复用 KV 页，miss 才算），decode 后 `extend`，结束 `remove`。

## 设计决策

1. **三线程分工**（用户协程/C++ 引擎/C++ 回传）：推理不持 GIL——Python 的慢不拖累 GPU。
2. **final chunk 用 usage 作哨兵**：一字段承担「请求结束」协议。
3. **weakref 引擎**：代理持弱引用，防误持代理阻回收。
4. **radix 双语镜像**：逻辑只有一份（C++），Python 壳防漂移。
5. **同步引擎不另写**：差异压缩到回调注入点，process_* 纯函数全共享。

## 新人提示

- **改流式先看回调链**：`_async_request_stream_callback_impl` 是输出必经之路。
- **request_id 唯一键**：重复 id 主动报错而非静默覆盖。
- **测 prefix cache**：`test_serve_engine_prefix_cache.py` 是语义基准。
- **TextStreamer 非普通 detok**：处理 UTF-8 跨块截断与停止串部分匹配，勿用 decode 替换。
- **JIT 模式**：model_lib 缺失时现场编译，首次启动慢不是 bug。
