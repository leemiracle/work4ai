# 02 · ImageSource 族：读取器×装饰器的组合式图像供给

## 角色定位

ImageSource（`DemandLoading/ImageSource/`，80 文件）是按需加载的数据供给抽象：DemandLoader 不知道 EXR/DDS/NTC 的区别，只认"能 readTile 的东西"。它用**读取器族**（格式适配）×**装饰器族**（行为组合）两组正交维度拼出整个图像来源空间，是本仓最教科书级的接口设计。

## 内部结构

根接口 `DemandLoading/ImageSource/include/OptiXToolkit/ImageSource/ImageSource.h:45`（class ImageSource，153 行）：生命周期 open（`ImageSource.h:52`）/close（`:55`）/isOpen（`:58`）/getInfo（`:63`）、内容读取 readTile（`:73`，dest+mipLevel+Tile+stream 四参契约）/readMipLevel（`:77`）/readMipTail（`:84`）/readBaseColor（`:91`）、getFillType（`:66`，区分 host 填充还是 device 填充）；配 ImageSourceBase 半实现与 Tile/PixelPosition POD。元信息 `DemandLoading/ImageSource/include/OptiXToolkit/ImageSource/TextureInfo.h`（宽高/格式/mip 数/tile 尺寸 + isBcFormat 判定）是全族公共描述。

读取器族全继承 ImageSourceBase：`EXRReader.h:28`（class EXRReader）、`CoreEXRReader.h:23`（OpenEXR core API 更轻）、`DDSImageReader.h:106`（GPU 压缩纹理格式直读）、`OIIOReader.h:20`（OpenImageIO 插件式全格式+half↔float）。装饰器族组合行为：`MipMapImageSource.h:16`（class MipMapImageSource : public WrappedImageSource——包装任意源生成 mip 金字塔）、`RateLimitedImageSource.h:20`（读速限流，同为 WrappedImageSource 模式）、`CascadeImage.h:13`（级联 id 映射）、`CheckerBoardImage.h:18`（程序化棋盘）、`DeviceMandelbrotImage.h:20`（device kernel 生成分形，配 DeviceMandelbrotParams.h）、DeviceConstantImage、TiledImageSource（强制分块）。缓存层 `ImageSourceCache.h:20`（class ImageSourceCache）以文件名为键缓存打开的源，配 ImageSourceCacheStatistics.h 统计；CompressedTextureCacheManager.h 服务压缩纹理缓存场景。

## 外部连接

上游唯一消费者是 DemandLoading 核心：`DemandLoading/DemandLoading/src/DemandLoaderImpl.cpp:159`（createTexture 接 shared_ptr<ImageSource>）与 `:181`（createUdimTexture 多文件版）；TextureRequestHandler 调 readTile 填传输缓冲；readBaseColor（`ImageSource.h:91`）供降级显示（tile 未加载时用基色）。下游 NeuralTextures 库实现该接口（`NeuralTextures/include/OptiXToolkit/NeuralTextures/NeuralTextureSource.h:19` 继承 ImageSourceBase）把 NTC 接进家族。示例侧 UdimTextureViewer/CompressedTextureCache/TexturePainting 各演示一种组合。

## 数据流

一次 tile 加载：DemandLoader 缺页 → TextureRequestHandler::fillRequest → readTile（`ImageSource.h:73`）→ 装饰器链逐层处理（MipMap 先查该 mip 层→Tiled 算文件内偏移→RateLimited 限速放行）→ 最内层读取器解压（EXRReader 解 EXR/OIIOReader 调插件）→ 原始像素写 host 传输缓冲 →（getFillType==device 时）device kernel 再转换。open（`ImageSource.h:52`）首次调用返回 TextureInfo 决定页表布局；readMipTail（`:84`）处理稀疏纹理 mip 尾部（无法按 tile 切的最粗层）——注意它不走 readTile。

## 设计决策

①**单一接口扛全部格式**——`ImageSource.h:45` 起 17 方法含生命周期/读取/元信息三组，格式差异（块压缩/半精度/平铺）全部压进实现；代价是接口略胖，ImageSourceBase 半实现消化次要方法；②**装饰器而非格式选项**——mip 化/分块/限流都是"包一层"（`MipMapImageSource.h:16` 的 WrappedImageSource 模式）而非构造参数，任意组合不自爆；③**shared_ptr+Cache 双管**——`ImageSourceCache.h:20` 以文件名缓存，多个 DemandTexture 引用同一文件零重复解码；④**程序化源与文件源同权**——`DeviceMandelbrotImage.h:20` 证明该抽象不仅服务磁盘文件，测试与演示用它零资产依赖。

## 新人提示

加新格式=继承 ImageSourceBase（对照 `ImageSource.h:45` 起的纯虚清单，只覆写 open/readTile 等少数），再在 OIIOReader 兜底前注册特化。读组合行为从 `MipMapImageSource.h:16` 入手（最薄装饰器）。tile 偏移错位九成在 TextureInfo 的 tile 尺寸与 readTile（`ImageSource.h:73`）的 Tile 参数不匹配。缓存命中率排查用 ImageSourceCacheStatistics；mip 尾部加载走 readMipTail（`:84`）不是 readTile——常见误读。Udim 场景（多文件映射）看 `DemandLoaderImpl.cpp:181` 的 createUdimTexture 与 CascadeImage.h:13 的配合。
