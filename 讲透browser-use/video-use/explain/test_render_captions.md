# test_render_captions.py — 字幕分块与输出时间轴的回归防线

> 源码：`tests/test_render_captions.py`（106 行）。行号锚均从源码逐一核实；被测对象 `helpers/render.py` 的行号同样逐一核实。

## ① 角色定位

这是整个仓库**唯一的测试目录**里信息密度最高的一份：三个测试文件（captions/fps/orientation）共用同一套动态加载骨架，本文件覆盖 render.py 最核心的业务逻辑——字幕如何从词级时间戳变成不闪不糊的 cue，master.srt 时间轴为什么拼接后仍对得上。它守护 SKILL.md 两条硬规则：Rule 5（SKILL.md L26 "`output_time = word.start - segment_start + segment_offset`. Otherwise captions misalign after segment concat."）与 "2-word UPPERCASE chunks" 字幕风格（主 README.md L18）。

三个测试类各守一段：`ChunkWordsTests`（L33-59）测纯函数 `chunk_words`；`BuildMasterSrtTests`（L62-73）端到端验证 SRT 生成含时间轴偏移；`SubtitlesPathTests`（L76-101）测字幕路径解析与缺失报错。fps/orientation 兄弟文件测探测函数，本文件测**语义**——分块错了用户看得见。背景：helpers/ 不是包（pyproject.toml L23 `py-modules = []`），三个测试都走 `importlib.util.spec_from_file_location` 从文件路径直接加载被测模块——仓库存活的唯一测试形态。

## ② 内部结构

**动态加载骨架（L1-13）**：`MODULE_PATH = Path(__file__).parents[1] / "helpers" / "render.py"`（L9）从测试文件向上两级定位仓库根；`spec_from_file_location("video_use_render", MODULE_PATH)`（L10）造模块规格并具名注册（避免与 sys.modules 同名模块冲突）；`module_from_spec` + `exec_module`（L12-13）执行 render.py 顶层代码——**这段在 import 期就跑**，模块级常量就位，`main()` 有 `__main__` 守卫不执行。

**测试数据工厂（L16-26）**：`w(text, start, end)` 三行字典工厂（L16-17）；TAKE（L21-26）是**一条真实 take 的 Scribe 词级时间戳**（L20 注释："90% of what a web agent does is completely wasted. We fix this."），13 词、2.64s-6.70s。`does`(3.86-4.14) 与 `is`(4.48-4.56) 之间 0.34s 停顿、`wasted.` 句号后 0.74s 长隙——这些"真实世界的毛边"正是分块器要对付的东西。

**ChunkWordsTests 六连测（L33-59）**：`test_real_take`（L34-37）把整条 take 的分块逐块断言为 `["90% of", "what a web", "agent does", "is completely", "wasted.", "We fix this."]`；`test_pause_splits_across_words`（L40-43）断言**不含** "does is"——L41 注释交代历史：旧固定两词配对法把跨 0.34s 停顿的 "does is" 配进同一 cue，是"旧 bug 不复活"的回归钉；`test_no_multiword_cue_flashes`（L45-49）要求多词 cue（未达词数上限）在屏 ≥ `CHUNK_MIN_S`；其余三条（L51-59）钉住标点断块、`CHUNK_MAX_WORDS` 封顶、空白词过滤。

**BuildMasterSrtTests（L62-73）**：临时目录伪造 `transcripts/C0103.json`（L67 写入 `{"words": TAKE}`）与最小 EDL（L68：sources 映射 + 单段 `start: 2.55, end: 6.8`），调 `render.build_master_srt`（L70）后手工解析 SRT（L71）断言：六条 cue 全部大写（L72，尾逗号被 render.py L506 的 rstrip 剥掉），首条时间轴**精确等于** `"00:00:00,090 --> 00:00:00,590"`（L73）。

**SubtitlesPathTests（L76-101）**：EDL 目录相对解析（L77-81）；CWD 回退（L83-95，模拟 agent 从项目根写 "edit/master.srt" 而 EDL 在 edit/ 里的情况）；缺失即 SystemExit 且错误信息含 `--no-subtitles`（L97-101）。

## ③ 外部连接

- **被测对象 render.py**：`resolve_subtitles_path`（L96-107）、`chunk_words`（L439-464）、`build_master_srt`（L468-521）、常量 `CHUNK_WORDS=2 / CHUNK_MAX_WORDS=3 / CHUNK_MIN_S=0.35 / CHUNK_PAUSE_S=0.3`（L433-436）、`PUNCT_BREAK`（L407）。
- **兄弟测试**：test_render_fps.py（L13-17 同款骨架，测统一帧率传递）与 test_render_orientation.py（L9-13 同款骨架，测 is_portrait_source 的 rotation 语义）。
- **上游数据契约**：TAKE 的字典结构（type/text/start/end）就是 transcribe.py 落盘的 Scribe words 格式——本测试同时是数据契约的活文档；SKILL.md L26 Rule 5 公式是 L73 断言的规范出处。

## ④ 数据流

```
import 期：tests/test_render_captions.py
  → spec_from_file_location("video_use_render", helpers/render.py)
  → exec_module（render.py 模块级代码执行，得到可调函数）

测试期：TAKE（真实词级时间戳）
 → render.chunk_words(TAKE)                    [纯函数，零 IO]
     断言：六块 / 无跨停顿配对 / 多词块 ≥0.35s / 标点断块 / ≤3 词 / 跳空词
 → tempfile edit/ + transcripts/C0103.json + EDL{start:2.55,end:6.8}
 → render.build_master_srt(edl, edit, out)     [真实文件 IO]
     断言：cue 大写；首条 = 00:00:00,090 --> 00:00:00,590
 → render.resolve_subtitles_path(rel, edit_dir)
     断言：EDL 目录 → CWD 回退 → 双失败 SystemExit(--no-subtitles)
```

首条时间轴可手推：segment_start=2.55，首词 "90%" 2.64→3.04；`out_start = 2.64 − 2.55 = 0.09s`、`out_end = 0.59s`——正是 L73 的 090/590，同时验证裁剪边界、偏移公式、SRT 格式化三件事。

## ⑤ 设计决策与取舍

**真实数据锚定**：TAKE 来自一条实际 take（L20 注释），不是合成数据——真实停顿与长隙恰好落在分块器决策边界附近，合成数据踩不到边界，测试就退化成形式。六块期望可手工推演（我逐词验证过）：`what a web` 三词成块是因为 `what`+`a` 只有 0.18s 不满 CHUNK_MIN_S，吃进 `web` 后 0.34s 仍差一丝，最终被 CHUNK_MAX_WORDS=3 硬截——三个常量在一次分块里全部参与决策。

**零 mock 纯逻辑测试**：本文件不 patch 任何东西（兄弟文件才 mock subprocess）；chunk_words 是纯函数。分层取舍清晰：能纯函数化的逻辑不碰 mock，必须进程外探世的（ffprobe）才 mock——mock 面积最小化降低测试脆弱性。

**历史 bug 钉版**：`test_pause_splits_across_words`（L40-43）的存在理由写在 L41 注释里——"the old fixed pairs produced 'does is' across a 0.34 s pause"。保留失败历史的测试是最便宜的防御：重构分块器时这条断言保证旧病不犯。

**SRT 测试只测首条时间轴**：L72 断言全部六条文本，L73 只断言首条时间轴——时间轴算术每条同构，验证一条即验证公式；文本断言必须全量（每条都可能是 rstrip/upper 边界案例）。

**动态加载而非 sys.path 注入**：spec_from_file_location 显式声明"被测物就是这个文件"，不受运行目录与 PYTHONPATH 污染；代价是 render.py 若改包结构，三处骨架同步改。

## ⑥ 新人提示（坑/勘误）

1. **运行方式**：仓库无 pytest 依赖、无 CI（install.md 只字未提测试）。直接跑 `python tests/test_render_captions.py`（L104-105 `unittest.main()`），或仓库根 `python -m unittest discover tests`；三文件独立可单独跑。
2. **exec_module 在收集期执行**：L13 在 import 时就执行 render.py 全部模块级代码——顶层将来若出现副作用（建目录、读环境变量），import 阶段就炸。顶层纯净是被测方的隐性契约。
3. **"video_use_render" 是命名空间隔离**：L10 具名防撞；但 `module_from_spec` 建的对象**没有**进 sys.modules——render.py 若递归 import 自己，行为与正常 import 不同。
4. **L47 的豁免边界**：`test_no_multiword_cue_flashes` 只检查 `len(c) > 1 and len(c) < CHUNK_MAX_WORDS` 的块——**恰好达词数上限（3 词）的多词块被豁免**（L47 注释："only the word cap may leave a multi-word cue under the minimum"）。这是设计而非漏洞：极速语速下宁可让 3 词块略短也不能吞第 4 个词。
5. **TAKE 是英文数据**：分块器只覆盖空格分词的英文；CJK 无空格、`PUNCT_BREAK`（render.py L407）不含中文句号"。"——中文视频需自行适配，本测试不提供保障。
6. **CWD 回退测试会真的 chdir**（L89-94，有 finally 恢复）；线程级并行测试下是全局状态可能互踩，stdlib 串行执行无事。
7. **三兄弟骨架行号不同**：本文件 L9-13，test_render_fps.py L13-17（多三个 import），test_render_orientation.py L9-13——写新测试抄最近的那份。

---
*video-use explain 系列第 12 篇（helpers/references/tests 三线收官）。*
