# restore-final.ps1
param()
$utf8 = New-Object Text.UTF8Encoding($false)
$root = "C:\workspace\work4ai\"

# --- 1. README: RL two rows back to HEAD (real entry/anchor files exist)
$c = [IO.File]::ReadAllText($root + "README.md", [Text.Encoding]::UTF8)
$c = $c.Replace('| [`强化学习视角-元迭代器.md`](./强化学习视角-元迭代器.md) | RL 视角迭代全项目的导航枢纽（四条阅读路径并入该文件）|', '| [`强化学习视角-总入口.md`](./强化学习视角-总入口.md) | RL 视角迭代全项目的导航枢纽（四条阅读路径）|')
$c = $c.Replace('| [`视角库/强化学习.md`](./视角库/强化学习.md) | 所有文件通用的 RL 视角锚点（轻量接入）|', '| [`强化学习视角-锚点块.md`](./强化学习视角-锚点块.md) | 所有文件通用的 RL 视角锚点（轻量接入）|')
[IO.File]::WriteAllText($root + "README.md", $c, $utf8)
"step1: RL rows restored"

# --- 2. README: philosophy section (from Mao header to EOF) replaced by HEAD version
$headAll = git -C $root show "HEAD:README.md" 2>$null
$hStart = 430
$hSec = $headAll[($hStart-1)..($headAll.Count-1)]
$cur = Get-Content ($root + "README.md") -Encoding UTF8
$mStart = ($cur | Select-String -Pattern "^## .{0,3}毛泽东哲学视角" | Select-Object -First 1).LineNumber
$new = $cur[0..($mStart-2)] + $hSec
[IO.File]::WriteAllLines($root + "README.md", $new, $utf8)
"step2: philosophy section restored from HEAD ($($hSec.Count) lines)"

# --- 3. Confucian headers (5 files): restore HEAD link format
$confHead = '> 儒家核心视角之一 ｜ 总入口：[`../儒家核心视角-总入口.md`](../儒家核心视角-总入口.md) ｜ 锚点块：[`../儒家核心视角-锚点块.md`](../儒家核心视角-锚点块.md)'
foreach ($n in @("中庸执两","修身务本","和而不同","学而时习","忠恕一贯")) {
    $p = $root + "视角库\$n.md"
    $t = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)
    $t = [regex]::Replace($t, '> 儒家核心视角之一[^\r\n]*', $confHead)
    [IO.File]::WriteAllText($p, $t, $utf8)
}
"step3: 5 Confucian headers restored"

# --- 4. inline echoes (6 files): restore HEAD link format
$fix4 = @(
    @{ f="视角库\情境自我.md"; old='[`和而不同.md`](和而不同.md)'; new='[`../儒家核心视角-总入口.md`](../儒家核心视角-总入口.md)'; ctx='呼应' },
    @{ f="视角库\无知之幕.md"; old='[`兼爱.md`](兼爱.md)'; new='[`../墨家核心视角-总入口.md`](../墨家核心视角-总入口.md)'; ctx='东方呼应' },
    @{ f="视角库\正义即公平.md"; old='[`兼爱.md`](兼爱.md)'; new='[`../墨家核心视角-总入口.md`](../墨家核心视角-总入口.md)'; ctx='东方呼应' },
    @{ f="视角库\经验主义先声.md"; old='[`三表法.md`](三表法.md)'; new='[`../墨家核心视角-总入口.md`](../墨家核心视角-总入口.md)'; ctx='三表法' },
    @{ f="视角库\自由与差异原则.md"; old='[`尽地利.md`](尽地利.md)'; new='[`../农家核心视角-总入口.md`](../农家核心视角-总入口.md)'; ctx='东方呼应' },
    @{ f="视角库\资格理论.md"; old='[`因势利导.md`](因势利导.md)'; new='[`../纵横家核心视角-总入口.md`](../纵横家核心视角-总入口.md)'; ctx='东方呼应' }
)
foreach ($x in $fix4) {
    $p = $root + $x.f
    $t = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)
    if ($t.Contains($x.old)) { $t = $t.Replace($x.old, $x.new); [IO.File]::WriteAllText($p, $t, $utf8); "  ok: $($x.f)" } else { "  MISS: $($x.f)" }
}

# --- 5. RL references (3 files): restore HEAD
$p = $root + "强化学习视角-元迭代器.md"
$t = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)
$t = [regex]::Replace($t, '- 迭代任务导航即本文件[^\r\n]*', '- [`强化学习视角-总入口.md`](./强化学习视角-总入口.md) — 迭代任务导航')
[IO.File]::WriteAllText($p, $t, $utf8)
$p = $root + "top-education-courses\README.md"
$t = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)
$t = $t.Replace('[`../强化学习视角-元迭代器.md`](../强化学习视角-元迭代器.md)', '[`../强化学习视角-总入口.md`](../强化学习视角-总入口.md)')
[IO.File]::WriteAllText($p, $t, $utf8)
$p = $root + "讲透模型宇宙\HISTORY.md"
$t = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)
$t = [regex]::Replace($t, '> 通用锚点见 \[`../强化学习视角-元迭代器\.md`\]\([^)]*\)。', '> 通用锚点见 [`../强化学习视角-锚点块.md`](../强化学习视角-锚点块.md)。')
[IO.File]::WriteAllText($p, $t, $utf8)
"step5: 3 RL refs restored"
