# 04 · gRPC 推断服务全链：proto 契约 → 生成桩 → 服务端/客户端

> 涉及：`setup/megamolbart.proto`、`generated/megamolbart_pb2.py`（47 行）/`megamolbart_pb2_grpc.py`（162 行）、`nemo_chem/models/megamolbart/grpc/service.py`（57 行）、`examples/chem/nbs/infer.py`（44 行）。行号锚经源码核实。

## ① 角色定位

MegaMolBART 的部署形态是"容器内 gRPC 服务 + 远端客户端"：模型重（Megatron + GPU），客户端轻（notebook/下游药物管线），用 protobuf 契约解耦两侧。三个 rpc 覆盖三种消费模式：SMILES→嵌入（相似度检索）、SMILES→隐状态（分析）、隐状态→SMILES（**生成**——MegaMolBART 的核心卖点）。

## ② 内部结构

**契约**（setup/megamolbart.proto）：package nemo_chem.models.megamolbart.grpc；消息 InputSpec（smis/hidden_states/dim/masks）与 OutputSpec（smis/hidden_states/embeddings/dim/masks）；服务 GenerativeSampler 三 rpc。

**生成桩**：`megamolbart_pb2.py:17` DESCRIPTOR 序列化协议 + **`_reflection.GeneratedProtocolMessageType` 赋值式建类**（megamolbart_pb2.py:21-26 的 InputSpec/OutputSpec）——静态分析与 tree-sitter 双盲区，知识图谱的类节点是手工补的；`megamolbart_pb2_grpc.py` 三件：`GenerativeSamplerStub`（L8，客户端阻塞调用面）、`GenerativeSamplerServicer`（L44，服务端基类，三 rpc 未实现体）、`add_GenerativeSamplerServicer_to_server`（L76，注册器）。

**服务端**（service.py）：`InferenceService`（service.py:13）继承 Servicer；构造懒加载推断器——Hydra `initialize/compose`（service.py:17-18）加载 infer.yaml 后造 `NeMoMegaMolBARTWrapper`；三 rpc 实现（L22/28/35）做 torch 张量↔proto 消息互转，`.cuda()` 硬编码 GPU（L38/41）；`main()`（L48）起 ThreadPoolExecutor(max_workers=10) 监听 `[::]:50051`（L53）。

**客户端**（nbs/infer.py）：`InferenceWrapper`（infer.py:10）连 `localhost:50051`（L13 硬编码）持 Stub，三方法打平张量随 dim 发送、按 resp.dim reshape 回来。

## ③ 外部连接

容器接线：`setup/startup.sh`（Dockerfile CMD）后台 `python service.py` 起 50051；`setup/entrypoint.sh`（Dockerfile ENTRYPOINT）另拉 JupyterLab——**8888 双 Jupyter 实例冗余**（批 4 甄别）。裸 import `megamolbart_pb2_grpc`（service.py:8、infer.py:4）依赖 PYTHONPATH 含 generated/（Dockerfile L57 的 RUN 设置）；service.py 的 config_path 相对路径（../../../../examples/chem/conf）以容器 cwd 为前提。下游：Inference.ipynb 演示 notebook。

## ④ 数据流

HiddenToSmis 一次往返：客户端把 hidden_states.flatten().tolist() + dim + masks 打包成 InputSpec → gRPC → 服务端 torch.FloatTensor(list(...)).reshape(spec.dim).cuda()（service.py:40-41）→ wrapper.hidden_to_smis 采样生成 → OutputSpec(smis=...) 回传。张量走 JSON 风格 repeated 字段（float 列表）——**每元素序列化，非零拷贝**，大 batch 是带宽瓶颈。

## ⑤ 设计决策

- **三 rpc 而非一个通用的 DoInference**：三种负载形状差异大（字符串入/张量入/张量出），显式契约优于万能消息；
- **dim 随载荷传输**：proto 无原生张量类型，shape 由发送方显式声明，接收方 reshape——简单但有畸形输入风险（无校验）；
- **ThreadPool 10 线程而非 asyncio**：PyTorch 推断本身 GIL 约束，线程池够用且代码最少。

## ⑥ 新人提示

1. 改 proto 后必须重新 protoc 生成 generated/ 两文件——手改生成代码会被下次生成覆盖；
2. 客户端硬编码 localhost:50051（infer.py:13），跨机部署要改地址或加环境变量；
3. 服务端相对 config_path（service.py:17）对 cwd 敏感——脱离容器目录结构启动会 FileNotFoundError；
4. 大张量跨进程慢是协议问题不是模型问题——瓶颈在 flatten().tolist() 序列化，不在 GPU。
