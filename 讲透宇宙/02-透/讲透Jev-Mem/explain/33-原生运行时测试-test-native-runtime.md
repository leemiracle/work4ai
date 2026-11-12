> 标题：原生运行时测试——macOS OpenMP/Metal 崩溃防护的子进程验证法 · 源文件：tests/test_native_runtime.py（89 行）· 图谱标签：test / runtime / subprocess（图谱度数 in=0 / out=8）

## 角色定位

全仓最小的测试文件之一，守的却是最难复现的一类 bug：**原生库崩溃**。文件头一句话方法论（tests/test_native_runtime.py:1）："Native crashes must be checked in a fresh process, not pytest's runtime"——torch/FAISS 的 OpenMP 死锁或 macOS Metal 断言是进程级 abort，不是 Python 异常；在 pytest 进程内触发等于杀掉整个测试套件，且 import 顺序污染（原生线程池已在进程里初始化）无法逆转。所以本文件把最重的两个测试放进 `subprocess.run` 的干净解释器里跑（tests/test_native_runtime.py:48、83），pytest 只检查退出码与输出。

被测机制有两处：一是 `memory/local_device.py` 的设备策略——macOS 一律 CPU、其他平台 auto、显式指定永远赢（memory/local_device.py:6-14，docstring 直说动机是 "Avoid macOS Metal command-buffer aborts"，Metal 断言 abort 掉 Python 进程，连异常兜底的机会都不给）；二是 `memory/__init__.py` 包入口在 darwin 上对 `OMP_NUM_THREADS`/`MKL_NUM_THREADS` 的 setdefault（memory/__init__.py:15-17），注释要求这必须发生在 torch/FAISS/sklearn 加载原生 OpenMP 运行时**之前**。本文件就是这两道防线的行为契约。

## 内部结构

四个测试，两轻两重：

- **设备策略矩阵（tests/test_native_runtime.py:14-22）**：六参数组全展开——darwin 上 None/auto 都落 cpu、显式 "cpu" 原样通过；linux 上 None/auto 落 None（交原生自动探测）、显式 "cuda:1" 原样通过。打桩手法是 `monkeypatch.setattr(local_device, "sys", type("Platform", (), {"platform": platform}))`（tests/test_native_runtime.py:21）——把 local_device 模块里的 `sys` 名字整个换成类属性 platform 为目标串的空壳类型，函数内 `sys.platform` 取到的就是它。这一惯用法在 tests/test_laya_backend.py:115-116 也有同款，属仓内标准工艺。
- **编码器设备落点（tests/test_native_runtime.py:25-40）**：更进一层的集成验证。伪造 `SentenceTransformer` 类在构造时记录 device 参数（tests/test_native_runtime.py:30-35），连同可用性开关一起 patch 进 vector_db 命名空间（tests/test_native_runtime.py:37-38——能这样 patch 是因为 vector_db 用 `from sentence_transformers import SentenceTransformer` 把名字引进了自己模块，见 memory/vector_db.py:31-34）；随后真实构造 `VectorEncoder(use_openai=False)`，断言 dimension 为 384 且记录到的设备列表恰好 `["cpu"]`（tests/test_native_runtime.py:39-40）。这钉住了生产调用点 `SentenceTransformer(model_name, device=local_model_device())`（memory/vector_db.py:567）确实吃到了设备策略。
- **线程默认值先于 import（tests/test_native_runtime.py:43-77）**：全文件的重头戏，darwin 专属（skipif 见 tests/test_native_runtime.py:43）。子进程脚本分四幕：第一幕从环境里剥掉 OMP/MKL 两变量（tests/test_native_runtime.py:46-47）模拟裸机器；第二幕 `import memory` 后立即断言两变量已被包入口设成 1、且 torch/faiss **尚未**进入 sys.modules（tests/test_native_runtime.py:52-54）——这验证的是 memory/__init__.py 的惰性 `__getattr__`（_MODULES 字典按需加载）真的把原生库挡在了包 import 之外；第三幕按 benchmark 顺序导入 MemoryBuilder、faiss、torch、numpy（tests/test_native_runtime.py:56-59），断言 torch 线程数与 faiss OpenMP 上限都是 1（tests/test_native_runtime.py:60-61）；第四幕压轴——ThreadPoolExecutor 三 worker 各跑五轮 `torch.nn.Linear` 前向 + FAISS IndexFlatL2 建索引加查询（tests/test_native_runtime.py:63-72），模拟并发查询工作负载（正对 local_device.py 的 docstring 场景 "parallel query workers"）。收尾断言：退出码零、"native runtime exited cleanly" 在 stdout、stderr 里没有 "leaked semaphore"（tests/test_native_runtime.py:75-77）——后者是 macOS 上 faiss/torch 多线程拆机时的经典僵尸信号量残留。超时给到两分钟（tests/test_native_runtime.py:74）。
- **显式配置不被覆盖（tests/test_native_runtime.py:80-88）**：环境预设 OMP/MKL 为 2，子进程 import memory 后断言仍是 2——钉死包入口用的是 setdefault 而非硬覆盖（memory/__init__.py:16-17），用户手工调过的线程配置必须被尊重。

## 外部连接

仓内 import 全部函数内延迟（tests/test_native_runtime.py:20、26），目标只有两个模块：memory/local_device（策略本体，memory/local_device.py:6）与 memory/vector_db（设备策略的消费现场，import 于 memory/vector_db.py:19、调用于 memory/vector_db.py:567）。被测机制 memory/__init__.py:15-17 虽不被 import，却是两个子进程测试的真正靶子。设备策略的另三个消费方不直接出现在本文件：memory/laya_backend.py:7、utils/utils.py:2、utils/memory_layer.py:4——它们与 vector_db 共享同一 `local_model_device`，本文件等于替四处消费方统一验收。CI：`python -m pytest -q`（.github/workflows/ci.yml:29）在 ubuntu/macos 双矩阵（.github/workflows/ci.yml:15）上拉起；注意 CI 工作流自己在 env 层也设了 OMP/MKL 为 1（.github/workflows/ci.yml:20-21 一带），所以"默认值"测试的真实增量发生在本地裸环境与显式传 env 的子进程里（tests/test_native_runtime.py:46-47 的剥离与 82 的显式 2 都自带环境，不受 CI env 干扰）。图谱 in=0/out=8：无被测代码 import 本文件，符合测试文件常态。

## 数据流

两条链路。轻链路（前两个测试）：monkeypatch 替换 local_device.sys 或 vector_db 命名空间内的符号 → 调真实函数/构造器 → 断言返回值或被记录的设备参数。重链路（后两个测试）：pytest 进程组装内联 Python 脚本字符串与定制 env → subprocess 起干净解释器（cwd 钉在仓根，tests/test_native_runtime.py:11 的 ROOT）→ 子进程内 import memory（触发 setdefault）→ 按 benchmark 顺序加载原生栈 → 多线程压测 → 退出 → pytest 检查 returncode/stdout/stderr 三元组。数据不落盘，全部断言在内存与进程输出里完成。

## 设计决策

**子进程隔离的三重理由**：一，原生 abort 杀进程，pytest 进程内跑会把兄弟测试一起陪葬；二，import 顺序是进程级状态，"setdefault 必须先于 torch import"只能在从未 import 过 torch 的解释器里验证（tests/test_native_runtime.py:54 的反向断言尤其如此）；三，OpenMP 线程数在进程内不可靠地重置。这套结构与文件头宣言互为表里，是"测不了的就换进程测"的教科书示范。

**打桩不打桩的边界划得很准**：设备策略与编码器落点用 monkeypatch 轻量替换（快、可重复）；真正涉及原生库行为的部分一个 stub 都不打，宁可子进程慢启动也要测真 torch/faiss——因为要抓的正是 stub 永远模拟不出的原生线程交互。

**缝隙与代价要认清**：其一，两个重测试 skipif 非 darwin（tests/test_native_runtime.py:43、80），CI 的 ubuntu 腿整段跳过——Linux 上的 OpenMP 行为实际无人守护；其二，"leaked semaphore" 是字符串嗅探（tests/test_native_runtime.py:77），抓的是已知失败签名，新的崩溃形态（如 Metal command buffer abort 的输出变体）不保证命中，退出码零才是主断言；其三，压测负载是五轮小算例（tests/test_native_runtime.py:64-70），对竞态是冒烟级不是压力级——它的价值在于回归信号（改了 import 结构或线程默认后立刻红）而非穷尽；其四，设备矩阵里的 linux 分支只测 `local_model_device` 纯函数返回 None，"None 交给 SentenceTransformer 后原生如何选设备"不在射程内。

## 新人提示

先读 tests/test_native_runtime.py:1 的宣言与 44-77 的子进程脚本——把那段内联代码当独立小程序读，四幕结构在脚本注释里标得清楚。跑法：macOS 上 `python -m pytest tests/test_native_runtime.py -q` 全量；Linux 上只跑前两个轻测试，后两个 skip 属预期，别当成 bug 修。

四个坑：一，动 memory/__init__.py 的 import 结构（哪怕只是调整 _MODULES 字典外的普通 import）先跑本文件——惰性边界一破，53-54 行的断言最先说话；二，想给 CI 加 Windows 腿时注意这两个 darwin 测试的 skipif 不会自动挡 Windows，得另加条件；三，子进程脚本是字符串内联（tests/test_native_runtime.py:48-73），改它没有语法检查兜底，pytest 收集阶段不报错、跑起来才报——改完务必真跑一次；四，`type("Platform", (), {"platform": platform})` 这种类当模块的写法只适用于被测代码只读 `sys.platform` 属性的场景，local_device 若将来改用 `sys.version` 或 `platform.machine()` 会静默拿到 AttributeError 之外的东西，扩展被测面时要同步升级桩。
