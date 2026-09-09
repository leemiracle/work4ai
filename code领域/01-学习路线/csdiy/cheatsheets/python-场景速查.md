# Python 实战 · 场景速查

> 命令原文 + 一句话场景。能一行解决的别写脚本，能复现的别靠猜。

## 🚨 最常用 5 条
```bash
python -m venv .venv && source .venv/bin/activate    # 建虚拟环境并进入
pip install -r requirements.txt                       # 装依赖
python -m pdb script.py                               # 脚本崩了，挂调试器跑
python -m cProfile -s tottime script.py | head -30    # 看谁最耗时
python -m http.server 8000                            # 当前目录秒变 HTTP 服务
```

---

## 虚拟环境
```bash
python -m venv .venv                                  # 标准库建环境（最稳）
source .venv/bin/activate                             # 激活（Windows: .venv\Scripts\activate）
deactivate                                            # 退出虚拟环境
pip install pip-tools                                 # 装 pip-compile 做依赖锁定
pip-compile requirements.in                           # 把松散依赖解析成带版本hash 的 requirements.txt
pip-sync requirements.txt                             # 让环境严格匹配锁文件（多余的包会被删）
pip freeze > requirements.txt                         # 导出当前环境（粗糙版，不含依赖树）
pip list --outdated                                   # 看哪些包有新版
```

### uv（10-100x 快，替代 pip + venv）
```bash
uv venv                                               # 秒建虚拟环境
uv pip install -r requirements.txt                    # 高速装依赖
uv pip compile requirements.in -o requirements.txt    # 锁定依赖
uv pip sync requirements.txt                          # 严格同步
uv run script.py                                      # 自动建环境并跑，省去 activate
uv tool install ruff                                  # 装命令行工具，不污染项目环境
```

### poetry（项目化依赖管理）
```bash
poetry init                                           # 交互式生成 pyproject.toml
poetry add requests                                   # 加运行依赖
poetry add --group dev pytest ruff                    # 加开发依赖组
poetry install                                        # 按 pyproject.toml 装全部
poetry lock                                           # 重新解析锁定 poetry.lock
poetry run python main.py                             # 在项目环境里跑
poetry shell                                          # 进项目环境 shell
poetry export -f requirements.txt --output req.txt    # 导出给非 poetry 工具用
```

### 依赖冲突排解
```bash
pip install pkgA pkgB                                 # 报冲突：pkgA 要 numpy<2，pkgB 要 numpy>=2
pip show numpy                                        # 看当前装了哪个版本、被谁依赖
pip check                                             # 列出所有已安装包的依赖不一致
pipdeptree                                            # 画出依赖树，定位谁在拖旧版（pip install pipdeptree）
pipdeptree --reverse --packages numpy                 # 反查：谁依赖 numpy
pip install "numpy>=2" --force-reinstall              # 强制重装指定版本验证是否真不兼容
# 真冲突解不开：用 poetry/uv 分组隔离，或换其中一个库的替代品
```

---

## 调试
```bash
python -m pdb script.py arg1                          # 整个脚本挂 pdb 跑
python -m pdb -c continue script.py                   # 挂着 pdb 但跑到崩了才停
python -m ipdb script.py                              # ipdb：有语法高亮和补全的 pdb（pip install ipdb）
```

### 断点（推荐方式）
```python
breakpoint()                  # 3.7+ 内置，代码里插一行就停（自动用 PDB/IPDB）
import pdb; pdb.set_trace()   # 老写法，3.6 及更早
```

### pdb 内常用命令
```
n          # 下一行（不进函数）
s          # step，进入函数内部
c          # continue，跑到下个断点
l          # list，看当前代码上下文
p var      # print 变量
pp obj     # pretty print，复杂数据结构好看
w          # where，看调用栈
u / d      # up / down，在调用栈上下移动
b 42       # 在当前文件第 42 行下断点
b funcname # 在函数入口下断点
a          # args，看当前函数所有入参
q          # quit，退出调试器
!expr      # 执行任意表达式（如 !x = 5 改变量值）
```

### 事后调试（崩了再查现场）
```bash
python -i script.py          # 崩了不退出，进交互式，看 traceback 里的局部变量
```
```python
import pdb, traceback
traceback.print_exc()        # 重打一遍 traceback
pdb.pm()                     # post-mortem，直接停到崩的那一帧
```

### 远程 debug（生产容器里卡住）
```python
import debugpy
debugpy.listen(("0.0.0.0", 5678)); debugpy.wait_for_client()  # 监听 5678 等本地 IDE 接入
```
```bash
pip install debugpy          # VSCode/Cursor: launch.json "attach"，host=容器IP port=5678
```

### monkey patch（不改源码改行为）
```python
# hot_patch.py，用 PYTHONSTARTUP=/path/hot_patch.py 自动加载
def patch_requests():
    import requests
    _orig = requests.Session.request
    def traced(self, method, url, **kw):
        print(f"[REQ] {method} {url}")
        return _orig(self, method, url, **kw)
    requests.Session.request = traced
patch_requests()
```
```bash
PYTHONSTARTUP=./hot_patch.py python script.py   # 启动时自动打补丁
```

---

## 性能
```bash
python -m cProfile -o prof.out script.py         # 跑完生成统计文件
python -c "import pstats; pstats.Stats('prof.out').sort_stats('tottime').print_stats(20)"  # 按自身耗时排序看 top20
python -m cProfile -s cumtime script.py | head -30   # 按累计耗时（含子调用）排序
```

### py-spy（不用改代码，sampling profiler）
```bash
pip install py-spy
py-spy top --pid 12345                          # 实时看进程内函数热度（类似 top）
py-spy record --pid 12345 -o flame.svg --duration 30  # 抓 30 秒火焰图
py-spy dump --pid 12345                         # dump 当前所有线程的 Python 调用栈
py-spy record -- python script.py               # 直接启动并采样
```

### N+1 查询（ORM 最常见性能杀手）
```python
# 反例：循环里发查询（100 个用户 = 101 次 SQL）
for u in User.objects.all():
    print(u.profile.bio)        # 每次访问都查一次 profile 表

# 正解：预加载
User.objects.select_related('profile')          # 一对一/外键，JOIN 一次
User.objects.prefetch_related('posts')          # 一对多，两条 IN 查询
# SQLAlchemy: selectinload(User.posts)
```
```bash
# Django 里自动检测 N+1（开发期）
pip install django-debug-toolbar                # 每个 SQL 都显示出来，循环里刷一片就是 N+1
# nplusone 库：访问 N+1 时直接抛警告
```

### 内存
```bash
pip install tracemalloc objgraph memory_profiler
```
```python
import tracemalloc
tracemalloc.start()
# ... 跑你的代码 ...
snap = tracemalloc.take_snapshot()
for stat in snap.statistics('lineno')[:10]:     # 按行号看 top10 内存分配
    print(stat)

# 对比两次快照，定位泄漏
snap1 = tracemalloc.take_snapshot()
# ... 跑一会儿 ...
snap2 = tracemalloc.take_snapshot()
for stat in snap2.compare_to(snap1, 'lineno')[:10]:
    print(stat)
```
```python
import objgraph
objgraph.show_most_common_types()              # 哪类对象最多
objgraph.show_growth()                          # 两次调用间增长最快的类型（泄漏嫌疑）
objgraph.show_backrefs([obj], filename='ref.png')  # 画引用链，找谁拽着不释放
```
```bash
python -m memory_profiler script.py             # 逐行内存占用（@profile 装饰器标记函数）
mprof run script.py && mprof plot               # 内存随时间曲线
```

---

## 异步坑
### asyncio 基本用法
```python
import asyncio
async def fetch(url):
    await asyncio.sleep(0.1); return url
async def main():
    results = await asyncio.gather(            # 并发跑多个协程
        fetch("a"), fetch("b"), fetch("c"), return_exceptions=True)  # 异常也收集不抛
    try:
        r = await asyncio.wait_for(fetch("slow"), timeout=0.5)   # 超时控制
    except asyncio.TimeoutError: print("超时")
```

### 阻塞调用毒化事件循环
```python
async def bad():              # 错：async 里跑同步 IO/CPU，整个 loop 卡死
    time.sleep(5); requests.get(url)
async def good():             # 对：丢到线程池
    await asyncio.to_thread(time.sleep, 5)     # 3.9+
    r = await asyncio.get_running_loop().run_in_executor(None, requests.get, url)
```

### aiodns / DNS 在 asyncio 里
```bash
pip install aiodns          # aiohttp 默认用同步 DNS 会卡 loop；装 aiodns 自动用异步解析，无需改代码
```

### 常见坑
```python
result = async_func()       # 错：没 await，拿到的是 <coroutine> 不是结果；result = await ...
asyncio.run(main())         # 3.7+ 从同步入口跑 async；已有 loop 里再 asyncio.run 会 RuntimeError
# RuntimeWarning: coroutine was never awaited → grep 'never awaited' 日志，某分支忘 await 了
# gather 里一个抛异常其他被取消 → return_exceptions=True 或包 try/except
```

# 4. gather 里一个抛了，其他被取消
# 用 return_exceptions=True 收集异常，或包 try/except
```

---

## 打包
### pyproject.toml（现代标准，PEP 621）
```toml
[project]
name = "mypkg"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["requests>=2.31", "click>=8"]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[project.scripts]
mycli = "mypkg.cli:main"            # entry_points：装完自动有 mycli 命令

[build-system]
requires = ["hatchling"]            # 后端可选 hatchling/setuptools/flit/poetry-core
build-backend = "hatchling.build"
```

### 构建 wheel
```bash
pip install build
python -m build                    # 生成 dist/ 下 .tar.gz 和 .whl
python -m build --wheel            # 只打 wheel（推荐，装得快）
pip install dist/mypkg-0.1.0-py3-none-any.whl   # 本地验证能装能跑
twine check dist/*                 # 上传前检查元数据
twine upload dist/*                # 发到 PyPI（需账号 + API token）
```

### entry_points（装完即命令）
```python
# mypkg/cli.py
def main():
    print("hello")

# pyproject.toml 里 [project.scripts] 配好后，pip install . 就有 mycli 命令
# 等价于命令行跑 python -c "from mypkg.cli import main; main()"
```

---

## 常见陷阱
### 可变默认参数（经典坑）
```python
def add(x, lst=[]):          # 错：lst 在函数定义时只创建一次，所有调用共享
    lst.append(x)
    return lst
add(1); add(2)               # [1, 2] 不是 [2]

def add(x, lst=None):        # 对：每次用 None 哨兵
    if lst is None:
        lst = []
    lst.append(x)
    return lst
```

### late-binding closure
```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]         # [2, 2, 2] 不是 [0,1,2]，闭包引用的是同一个 i

funcs = [lambda i=i: i for i in range(3)]   # 用默认参数绑定当前值
[f() for f in funcs]         # [0, 1, 2]
```

### == vs is
```python
a = [1,2]; b = [1,2]
a == b        # True，值相等
a is b        # False，不是同一对象
# 小整数缓存陷阱：
x = 256; y = 256
x is y        # True，CPython 缓存 -5..256
x = 257; y = 257
x is y        # 可能 False，别用 is 比值
# 字符串：单例化（intern）有时 is 成立有时不成立，永远用 == 比值
# None 比较：永远用 is None / is not None
```

### NaN
```python
float('nan') == float('nan')   # False！NaN 不等于自己
import math
math.isnan(x)                  # 唯一可靠判定方式
# Pandas 里 NaN != NaN 同样成立，用 isna()/isnull()
# 列表去重时 NaN 会被当不同元素，set 里有多个 nan
```

### GIL（全局解释器锁）
```python
# 多线程 CPU 密集任务不加速：GIL 同一时刻只有一个线程跑 Python 字节码
# IO 密集（网络/文件）：多线程/asyncio 有效（等 IO 时释放 GIL）
# CPU 密集：用 multiprocessing 走多进程绕开 GIL
from multiprocessing import Pool
with Pool(4) as p: results = p.map(heavy_func, data)
# 或 C 扩展/numpy(C 层可释放 GIL)/Cython/numba；async+CPU 用 ProcessPoolExecutor
```

### 其他高频坑
```python
5 // 2     # 2；-5 // 2 = -3！向负无穷取整（不是 C 的截断）
1 < a < 10 # 链式比较，等价 1<a and a<10，不是 (1<a)<10
b = copy.deepcopy(a)    # 浅拷贝 a.copy() 嵌套列表仍共享，要深拷贝
for k in d: del d[k]    # RuntimeError: 字典遍历时改大小；改用 list(d) 或字典推导重建
```

---
*参考：本仓库 `notes/db-程序员视角` N+1 与索引、`notes/perf-程序员视角` 火焰图流水线。*
