# fix-remaining-links.ps1 — final pass: repair links in filled blocks + header lines + root README
param()
$ErrorActionPreference = "Stop"

# --- Part 1: 8 filled blocks (Neoplatonism x4, Augustinianism x4): replace dead "承接" line, drop dead "通用锚点" line
$pairs = @(
    @{ f="视角库\三本体.md" }, @{ f="视角库\太一流溢.md" }, @{ f="视角库\恶是匮乏.md" }, @{ f="视角库\灵魂上升.md" },
    @{ f="视角库\原罪与恩典.md" }, @{ f="视角库\恶的问题.md" }, @{ f="视角库\时间内省.md" }, @{ f="视角库\自由意志.md" }
)
foreach ($p in $pairs) {
    $path = "C:\workspace\work4ai\" + $p.f
    $lines = [IO.File]::ReadAllLines($path)
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($l in $lines) {
        if ($l -match '^> 承接 `../(新柏拉图主义|奥古斯丁主义)核心视角-总入口\.md`（规划中）。') {
            $out.Add("> 总目录：[README §哲学视角](../README.md)（各流派视角表 + [`视角库/`](README.md) 概念卡）")
        } elseif ($l -match '^\*\*通用锚点\*\*：`../(新柏拉图主义|奥古斯丁主义)核心视角-锚点块\.md`（规划中）\s*$') {
            # drop line
        } else { $out.Add($l) }
    }
    [IO.File]::WriteAllLines($path, $out, (New-Object Text.UTF8Encoding($false)))
}
"PART1 done: 8 filled blocks repaired"

# --- Part 2: Confucian header lines (5 files, line ~3)
$conf = @("中庸执两","修身务本","和而不同","学而时习","忠恕一贯")
foreach ($n in $conf) {
    $path = "C:\workspace\work4ai\视角库\$n.md"
    $raw = [IO.File]::ReadAllText($path)
    $raw = $raw -replace '> 儒家核心视角之一 ｜ 总入口：`../儒家核心视角-总入口\.md`（规划中） ｜ 锚点块：`../儒家核心视角-锚点块\.md`（规划中）', '> 儒家核心视角之一（概念卡体系：[`README.md`](README.md)；总目录：[../README §哲学视角](../README.md)）'
    [IO.File]::WriteAllText($path, $raw, (New-Object Text.UTF8Encoding($false)))
}
"PART2 done: 5 Confucian headers repaired"

# --- Part 3: inline echo links -> real concept cards
$fix3 = @(
    @{ f="视角库\情境自我.md"; old='`../儒家核心视角-总入口.md`（规划中）'; new='[`和而不同.md`](和而不同.md)' },
    @{ f="视角库\无知之幕.md"; old='`../墨家核心视角-总入口.md`（规划中）'; new='[`兼爱.md`](兼爱.md)' },
    @{ f="视角库\正义即公平.md"; old='`../墨家核心视角-总入口.md`（规划中）'; new='[`兼爱.md`](兼爱.md)' },
    @{ f="视角库\经验主义先声.md"; old='`../墨家核心视角-总入口.md`（规划中）'; new='[`三表法.md`](三表法.md)' },
    @{ f="视角库\自由与差异原则.md"; old='`../农家核心视角-总入口.md`（规划中）'; new='[`尽地利.md`](尽地利.md)' },
    @{ f="视角库\资格理论.md"; old='`../纵横家核心视角-总入口.md`（规划中）'; new='[`因势利导.md`](因势利导.md)' },
    @{ f="强化学习视角-元迭代器.md"; old='- `./强化学习视角-总入口.md`（规划中） — 迭代任务导航'; new='- 迭代任务导航即本文件（元迭代器）；姊妹：[`强化学习视角-元迭代器.md`](强化学习视角-元迭代器.md) 下的各视角卡' },
    @{ f="top-education-courses\README.md"; old='`../强化学习视角-总入口.md`（规划中）'; new='[`../强化学习视角-元迭代器.md`](../强化学习视角-元迭代器.md)' },
    @{ f="讲透模型宇宙\HISTORY.md"; old='> 通用锚点见 `../强化学习视角-锚点块.md`（规划中）。'; new='> 通用锚点见 [`../强化学习视角-元迭代器.md`](../强化学习视角-元迭代器.md)。' }
)
foreach ($x in $fix3) {
    $path = "C:\workspace\work4ai\" + $x.f
    $raw = [IO.File]::ReadAllText($path)
    if ($raw.Contains($x.old)) { $raw = $raw.Replace($x.old, $x.new); [IO.File]::WriteAllText($path, $raw, (New-Object Text.UTF8Encoding($false))); "  ok: $($x.f)" } else { "  MISS: $($x.f)" }
}

# --- Part 4: root README — drop self-referential dead lines in 15 sections
$path = "C:\workspace\work4ai\README.md"
$lines = [IO.File]::ReadAllLines($path)
$out = New-Object System.Collections.Generic.List[string]
$dropped = 0
foreach ($l in $lines) {
    if ($l -match '^> 承接 `.{1,20}核心视角-总入口\.md`（规划中，正文见本节/`视角库/` 概念卡）。\s*$') { $dropped++; continue }
    if ($l -match '^\*\*通用锚点\*\*：`.{1,20}核心视角-锚点块\.md`（规划中，正文见本节/`视角库/` 概念卡）\s*$') { $dropped++; continue }
    $out.Add($l)
}
[IO.File]::WriteAllLines($path, $out, (New-Object Text.UTF8Encoding($false)))
"PART4 done: root README dropped $dropped self-ref lines"
