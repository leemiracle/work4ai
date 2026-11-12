# 06 · docker/Dockerfile — 源码编译栈（BundleSDF/SAM2/RoMa/kaolin）

## ① 角色定位

`docker/Dockerfile`（313 行）是 x86_64 主镜像的**唯一构建脚本**：在 `nvcr.io/nvidia/pytorch:25.04-py3` 基座（:1，CUDA 12.8 世代）之上装 7 个源码编译 C++ 库 + 6 个研究仓产物，合成一张"重建管线一体机"。README 默认安装路径就是 Docker；ARM/Jetson 侧另有 Dockerfile.aarch64 姊妹版。图谱将其建模为 service + 16 个 step 节点，是全仓"环境即代码"的根。

## ② 内部结构

七层（未注文件名的行号均指 docker/Dockerfile）：

1. **版本钉版**（:3-22）：cmake 3.28.3 / Eigen 3.4.0 / OpenCV 4.12.0 / pybind11 2.13.0 / yaml-cpp 0.8.0 拆成三组 ARG，改版本不动命令体。
3. **C++ 源码编译五连**（:47-169）：cmake 自举（:47-53）→ Eigen（:56-65）→ **OpenCV 4.12+contrib 双仓**（:71-115，`OPENCV_ENABLE_NONFREE=ON`(:83) 开 SIFT 专利族、`WITH_CUDA=ON`(:98)、CUDA_ARCH_BIN 七档(:104)）→ PCL 1.10（:116-141，纯 CPU 点云栈）→ pybind11（:144-152）→ yaml-cpp（:155-169，`CMAKE_POLICY_VERSION_MINIMUM=3.5` 绕策略检查）。
3. **Python 钉版层**（:68,174-195）：`PIP_NO_BINARY=torch,torchvision,torchaudio`（:68）锁死基座 NGC torch；requirements（:174-176）、open3d/numpy 钉版组（:179-188）、**kaolin 源码七档 arch 编译**（:189-193，NerfRunner 八叉树算子来源）、pytorch3d 0.7.9 第三方 wheel（:194）、onnxruntime-gpu 1.23.2（:195）。
4. **Theseus 链**（:197-216）：baspacho 稀疏求解器源码编译（:199-206）→ torchlie/torchkin → theseus 以 `BASPACHO_ROOT_DIR` 安装（:212-213）→ flash-attn（:216）。
5. **C++ 管线链**（:234-265）：clone BundleSDF 并 checkout `nvbundlesdf` 定制分支（:234）；mycuda 拷成 /customize_cuda pip 编译（:236-238）——Python 侧 `import my_cpp` 的实体；**BundleTrack 编译后只拷三个 so**（my_cpp*.so 进 dist-packages、两个 lib*.so 进 /usr/local/lib，:250-265）删源码。
6. **感知模型库**（:268-278）：segment-anything-2 可编辑安装（:269-273）；RoMa **钉 commit edd1b8b**（:275-278）防上游漂移。
7. **收尾**（:280-314）：清缓存（:281-287）；COPY 三目录 + editable 装本包（:292-299）；Jupyter 空密码 + EXPOSE 8888 + CMD（:300-314）。

## ③ 外部连接

上游两处构建入口：deploy.sh 的 build_image（按 ARCH_SUFFIX 选本文件或 aarch64 版）与 test_reconstruction.sh（缺镜像时现场构建）。下游是 compose 的 reconstruction-app 服务（nvidia runtime、shm 8gb、挂载 src/data/notebooks 热更新）；上下文受 .dockerignore 约束。仓内代码的依赖是隐式的：schema.py 默认权重路径、`import my_cpp`（nvbundlesdf.py:56）、`from romatch import roma_outdoor`（nvbundlesdf.py:43）只在镜像内成立。

## ④ 数据流

构建期：git 上下文 + 五个上游仓（opencv/pcl/BundleSDF/sam2/RoMa）+ wheel 源 + pip 索引 → 逐层缓存。运行期：Jupyter（8888）工作目录 /workspace/3d-object-reconstruction；权重由 deploy.sh 下载并校验 md5 后挂载注入——**镜像本身不含任何神经网络权重**（kaolin/theseus 是代码库不是模型库）。

## ⑤ 设计决策

1. **全源码编译的理由**：apt 的 OpenCV 无 CUDA/NONFREE（SIFT 要用）；PCL 1.10 是 BundleTrack 血统版本。
2. **单 stage 而非多阶段**：C++ 产物必须留在最终层、Python 源码编译无明确构建/运行边界，多阶段收益低；代价是镜像巨大。
3. **PIP_NO_BINARY 先立后破**（:68 与 :272 注释"temporarily unset"）：防 pip 用 PyPI torch 轮子覆盖 NGC 基座的 CUDA 绑定 torch——同一纪律两面执行。
4. **LD_LIBRARY_PATH 前置 HPC-X UCX**（:218-220）：HPC-X 自带 UCX 与系统 UCX 冲突，靠路径次序让 libucc.so.1 找到符号。
5. **PYOPENGL_PLATFORM=egl + NVIDIA EGL vendor**（:222-225）：pyrender 离屏渲染（nerf_runner 的 ModelRendererOffscreen）无头环境必须走 EGL，Mesa 报 EGL_NOT_INITIALIZED。
6. **七档 CUDA arch 处处重复**（:104,191-198,238）：Volta 到 Blackwell 全覆盖，编译时长换通用性。

## ⑥ 新人提示

- **RUN alias 无效**（:229）：alias 只活在单条 RUN 内，真正让 `python` 生效的是 update-alternatives（:231-232）。
- 改 src/requirements.txt 会使 :174 之后全部层缓存失效——CI 里最后改。
- RoMa 钉版 commit（:276）与 roma.py 调用面是隐式契约，升级 RoMa 先查 roma.py 的 tuple 变换类是否被上游改名。
- my_cpp 不是 PyPI 包：pip 装的是 /customize_cuda（:236-238），这步失败要到运行期 `import my_cpp` 才崩——构建日志 grep customize_cuda 确认。
- Jupyter 空 token + allow_root（:306-307）是内网单机取向，公网暴露 8888 前必须改。

---
*甄别：图谱 16 个 step 与源码段一一对应，"313 行"与 wc -l 一致，无冲突。*
