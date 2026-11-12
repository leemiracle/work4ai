# 讲透 Imageinary

NVIDIA [Imageinary](https://github.com/NVIDIA/Imageinary)——可复现大规模随机图像数据集生成器：随机 numpy 数组 → JPEG/PNG/BMP/RecordIO/TFRecord 任意尺寸输出，服务 DL 基准测试（公开数据集尺寸有限，压测管线需要可变尺寸输入）。**语义钉版：不是 GAN 库**——图像内容是纯噪声，全库 0 个网络/模型类（imagine.py 为 11 个模块级函数）。

## 全链状态表

| 阶段 | 状态 | 明细 |
|---|---|---|
| DeepWiki | ✗ 未收录 | 后台未索引（收录决定权钉版），**本图谱为唯一知识源** |
| understand 图谱 | ✅ | 33 节点 / 67 边 / 6 层 / 11 步 tour，validator 0 issues |
| fingerprints | ✅ | 17 文件基线 @aa44843e |
| onboarding | ✅ | [ONBOARDING.md](onboarding/ONBOARDING.md) 4994 字（不计空格）8 节 62 锚 |
| explain | ✅ | 2 篇（2500+2495 字，34+29 锚）：[01 核心管线](explain/01-imagine-py核心管线.md) / [02 软依赖双轨与测试 CI](explain/02-软依赖双轨与测试CI.md) |

图谱位置：仓内 `.understand-anything/knowledge-graph.json`。

## 结构速览

- `imagine/` 核心库：__init__.py 一行 barrel + imagine.py 纯函数式 API（create_images 主入口、create_recordio/create_tfrecords 训练格式分支、_main CLI）
- `tests/` unit（TestUnits 白盒直测私有函数）+ functional（四格式黑盒落盘）
- 双轨依赖：requirements.txt（TF2）与 requirements.txt.tf1（TF1.14 锁版本）；pushtest.yml 双 job 回归
- `setup.py` console_scripts `imagine=imagine:_main`，extras tfrecord/mxnet/all 对应软依赖

## 甄别精选（125 锚终验界内 0 坏，详见 onboarding §7）

1. **README CLI 三处示例照抄会报错**：文档写选项式 `--path/--name/--image_format`，`_parse_args` 实为位置参数定义（imagine.py:73-94）
2. README:145-147 RecordIO 段复制粘贴误写 TFRecords
3. imagine.py:67 `ArgumentParser(message)` 把使用文案当 `prog` 参数传
4. **TFRecord 输出无扩展名**（imagine.py:402，测试只断言 `tmprecord_0`）——图谱摘要".tfrecord 文件"以代码为准修正
5. mxnet/tensorflow 均为 try-import 哨兵软依赖：不装框架核心图像功能可用，RecordIO/TFRecord 才 ImportError
6. tests/unit 白盒跨过门面直调 imagine.py 私有函数（与 functional 黑盒互为表里）
7. requirements.txt 被 scanner 误标 docs/txt，已纠正为 config 节点

## 工艺备注

- Python 仓 scanner 质量好：imports 7/7 全量对账零补扫
- tested_by 全部 production→test 方向合规（merge 词法判定通过）
