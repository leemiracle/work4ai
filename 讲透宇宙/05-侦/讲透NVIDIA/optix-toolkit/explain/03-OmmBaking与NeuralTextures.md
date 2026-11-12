# 03 · OmmBaking 与 NeuralTextures：烘焙加速与神经压缩的两条正交路线

## 角色定位

两个中级库各解决一个渲染性能痛点：**OmmBaking**（`OmmBaking/`，70 文件）把"带 alpha 裁剪纹理的几何"预烘焙成 Opacity Micromap Array（OMM），让 OptiX 在求交前就能裁剪透明区域，省掉海量 alpha 裁剪着色调用；**NeuralTextures**（`NeuralTextures/`，15 文件）把 NTC（NVIDIA 神经纹理压缩）格式接进按需加载。二者互不相干，却都站在 DemandLoading 的肩膀上。

## 内部结构

**OmmBaking** 公开 API 唯一头 `OmmBaking/include/OptiXToolkit/CuOmmBaking/CuOmmBaking.h`（505 行）：数据 POD 族——BakeOptions（`CuOmmBaking.h:46`，烘焙精度/模式）、TextureDesc（`CuOmmBaking.h:232`，不透明度纹理描述）、BakeInputDesc（`CuOmmBaking.h:253`，三角形索引+UV+纹理绑定；`CuOmmBaking.h:258`/`:275` 注明 GetPreBakeInfo 调用可零传）、多输入共享纹理时按描述值比对去重（`CuOmmBaking.h:303` 注释）；两段式入口 GetPreBakeInfo（`CuOmmBaking.h:472`，探输出规模）与 BakeOpacityMicromaps（`CuOmmBaking.h:497`，执行烘焙）。实现 `OmmBaking/src/CuOmmBakingImpl.cpp`/`.cu`；纹理侧 `OmmBaking/src/SummedAreaTable.h`+`OmmBaking/src/Texture.cu` 做 SAT 纹理不透明度积分图求值；`OmmBaking/src/Util/Rasterize.h` 光栅化三角形 UV 覆盖；Triangle/Util（BufferLayout/XXH 哈希）。`OmmBaking/support/` 内嵌四套 vendored 单头库：tinyddsloader（+gl3w）、tinyexr、tinygltf（捆 json.hpp/stb_image）——测试资产读取的零依赖通道。tests/ 27 份，含 3dmd/DuckHole DDS/EXR 真实纹理基准。

**NeuralTextures** 是适配器形态：`NeuralTextures/include/OptiXToolkit/NeuralTextures/NeuralTextureSource.h:19`——class NeuralTextureSource : public imageSource::ImageSourceBase。readTile（`NeuralTextures/include/OptiXToolkit/NeuralTextures/NeuralTextureSource.h:45`）按 latent mip 层转发给 NTC 解码；getSamplerExtraData（`NeuralTextureSource.h:54`）直接返回 makeOptixInferenceData(optixContext) 的产物；makeOptixInferenceData（`NeuralTextureSource.h:57`）把 NTC 推理权重/层布局打包成 OptiX 设备侧 CUdeviceptr。配套：`NeuralTextures/include/OptiXToolkit/NeuralTextures/NtcImageReader.h`（.ntc 容器读取）、`Texture2DNeural.h`（神经纹理 2D 封装）、`InferenceDataOptix.h`/`InferenceOptix.h`（OptixInferenceData 结构——device kernel 采样时现场推理的输入布局）、`InferenceConstants.h`。

## 外部连接

OmmBaking：向上被 OptiX 加速结构消费（OMM 挂 IAS/GAS 实例），向下读纹理资产（`OmmBaking/support/` 的单头读取器）；独立于 DemandLoading 也可用（烘焙是离线工序）。NeuralTextures：向下依赖 NTC 运行时解码（.ntc），向上完全走 ImageSource 契约（`DemandLoading/ImageSource/include/OptiXToolkit/ImageSource/ImageSource.h:73` readTile）+ DemandTexture 采样路径；NeuralTextureViewer 示例（examples/DemandLoading/NeuralTextureViewer）是端到端验证，公共框架在 `examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKApp.h`（162 行）。

## 数据流

**烘焙链**：输入几何（三角形+UV，BakeInputDesc 于 `CuOmmBaking.h:253`）+不透明度纹理（TextureDesc 于 `CuOmmBaking.h:232`）→ `OmmBaking/src/Util/Rasterize.h` 光栅化 UV 覆盖 → `OmmBaking/src/SummedAreaTable.h` SAT 求每 texel 不透明度 → 按 BakeOptions（`CuOmmBaking.h:46`）精度量化成 micromap 子块 → BakeOpacityMicromaps（`CuOmmBaking.h:497`）产出 OMM 数组 → 运行期挂 OptiX 几何实例 → 求交时 ray 先查 OMM：全透明当 miss、全不透明直接命中、只有边界 texel 进着色做 alpha 裁剪。**神经链**：DemandLoader 缺页 → readTile（`NeuralTextureSource.h:45`）→ NTC 解 latent 数据填 tile；采样时 device kernel 经 getSamplerExtraData（`NeuralTextureSource.h:54`）注入的推理数据现场解码像素——压缩发生在"存 latent+采样时神经网络推理"两段。

## 设计决策

①**两段式 API（GetPreBakeInfo `CuOmmBaking.h:472`/Bake `:497`）**——先探规模再分配输出缓冲，GPU 工作流友好的经典契约；②**纹理描述值去重**（`CuOmmBaking.h:303`）——多个 bake 输入共享同一纹理时只算一次 SAT，省显存与带宽；③**NeuralTextures 做适配器而非并列大库**（仅 15 文件）——NTC 的重活（网络/权重）在 NTC SDK，本仓只做 ImageSource 桥（`NeuralTextureSource.h:19` 继承）与 OptiX 推理数据打包（`:57`），职责边界干净；④**vendored 单头库进 support/**——测试资产读取不引入外部构建依赖，与顶层 vcpkg 治理分层。

## 新人提示

烘焙管线从 `CuOmmBaking.h:46`（BakeOptions）与 `:253`（BakeInputDesc）读输入契约，跑 examples/CuOmmBaking/Simple 看最小调用；调精度拿 DuckHole 基准（tests 的 3dmd/DuckHole 纹理）对比吞吐与质量。NTC 侧从 `NeuralTextureSource.h:19` 继承链入手，理解 latent mip 与普通 mip 的差别（readTile 的 mipLevel 语义在 `:45` 被重载）；推理数据布局改动必须同步 `InferenceDataOptix.h` 与 device 采样 kernel 两处。OMM 与 NTC 可以叠用（神经纹理供不透明度输入再烘焙），示例层暂无此组合——是不错的贡献点。
