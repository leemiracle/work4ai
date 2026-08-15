# update-audit-ledgers.ps1
param()
$utf8 = New-Object Text.UTF8Encoding($false)

# 1. promised.md
$p = "C:\workspace\work4ai\.agent\audit\problems\promised.md"
$c = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)
$old1 = "# B类：「规划中」承诺 共 121 个目标文件`r`n`r`n## 仍缺失（承诺未兑现）：121"
$old1b = "# B类：「规划中」承诺 共 121 个目标文件`n`n## 仍缺失（承诺未兑现）：121"
$new1 = "# B类：「规划中」承诺 共 121 个目标文件`n`n> **✅ 2026-08-15 全量清理完毕**：经熵治理裁决，121 个「X核心视角-总入口/锚点块」承诺文件**全部决定不建**（与 2026-08-15 西方哲学流派「决定不建」决策一致——42×2 近空壳违反「不留空壳」红线）。全部内嵌模板块（~1037 块 / ~17100 行，跨 ~230 文件）已删除；8 个已填写块（新柏拉图 x4 + 奥古斯丁 x4）保留并改链至 root README；行内呼应引用改指视角库概念卡。下列历史清单仅存档。`n`n## 历史清单（已全部解决，存档）"
if ($c.Contains($old1)) { $c = $c.Replace($old1, $new1) } elseif ($c.Contains($old1b)) { $c = $c.Replace($old1b, $new1) } else { "WARN: promised.md header not matched" }
[IO.File]::WriteAllText($p, $c, $utf8)
"promised.md updated"

# 2. broken_links.md annotation
$b = "C:\workspace\work4ai\.agent\audit\problems\broken_links.md"
$c2 = [IO.File]::ReadAllText($b, [Text.Encoding]::UTF8)
$note = "# A类：断链（链接指向不存在的文件）共 217 个目标`n`n> **⚠ 2026-08-15 勘误**：本账本存在中文文件名编码误报——`黑格尔观念论核心视角-总入口.md`、`西方哲学诸流派核心视角-设计总纲.md`、`西方哲学诸流派核心视角-总完成报告.md`、`故事即世界迭代器-元理论.md` 等条目**文件实际存在**（audit 脚本在 GBK console 下存在性判断失效）。引用前先复核。"
$head2 = "# A类：断链（链接指向不存在的文件）共 217 个目标"
if ($c2.Contains($head2) -and -not $c2.Contains("2026-08-15 勘误")) { $c2 = $c2.Replace($head2, $note) }
[IO.File]::WriteAllText($b, $c2, $utf8)
"broken_links.md annotated"

# 3. western report annotation
$r = "C:\workspace\work4ai\西方哲学诸流派核心视角-总完成报告.md"
$c3 = [IO.File]::ReadAllText($r, [Text.Encoding]::UTF8)
$mark = "## 完成后的视角库全景"
$add3 = "> **🗑 2026-08-15 熵治理后续**：各组概念卡尾部内嵌的「X核心视角」模板块（承接行+指引表格+锚点行，全库约千块）经裁决为冗余复制（表格右列为填写指引而非内容，且总入口已决定不建）已全部移除；仅 8 个含真实映射的填写块（新柏拉图 x4：三本体/太一流溢/恶是匮乏/灵魂上升；奥古斯丁 x4）保留在概念卡内。本报告与设计总纲作为设计记录存档。`n`n"
if ($c3.Contains($mark) -and -not $c3.Contains("熵治理后续")) { $c3 = $c3.Replace($mark, $add3 + $mark) }
[IO.File]::WriteAllText($r, $c3, $utf8)
"report annotated"
