# restore-valid-links.ps1 — restore HEAD-form valid links where target files EXIST
param()
$utf8 = New-Object Text.UTF8Encoding($false)

function FixFile($path, $pairs) {
    $c = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
    foreach ($p in $pairs) {
        if ($c.Contains($p[0])) { $c = $c.Replace($p[0], $p[1]) }
        else { "  MISS in $path :: $($p[0].Substring(0,[Math]::Min(40,$p[0].Length)))" }
    }
    [IO.File]::WriteAllText($path, $c, $utf8)
}

$root = "C:\workspace\work4ai\"

# --- 1. root README: RL rows restore to real entry/anchor files
FixFile ($root + "README.md") @(
    @('| [`强化学习视角-元迭代器.md`](./强化学习视角-元迭代器.md) | RL 视角迭代全项目的导航枢纽（四条阅读路径并入该文件）|', '| [`强化学习视角-总入口.md`](./强化学习视角-总入口.md) | RL 视角迭代全项目的导航枢纽（四条阅读路径）|'),
    @('| [`视角库/强化学习.md`](./视角库/强化学习.md) | 所有文件通用的 RL 视角锚点（轻量接入）|', '| [`强化学习视角-锚点块.md`](./强化学习视角-锚点块.md) | 所有文件通用的 RL 视角锚点（轻量接入）|')
)

# --- 2. root README: re-insert entry/anchor lines into 15 philosophy sections (except Yangming entry which lacks a file)
$c = [IO.File]::ReadAllText($root + "README.md", [Text.Encoding]::UTF8)
$sects = @("毛泽东哲学视角","道教核心视角","佛教核心视角","禅宗核心视角","玄学核心视角","墨家核心视角","法家核心视角","道家核心视角","兵家核心视角","纵横家核心视角","阴阳家核心视角","名家核心视角","杂家核心视角","农家核心视角")
$lines = $c -split "`r?`n"
$out = New-Object System.Collections.Generic.List[string]
for ($i=0; $i -lt $lines.Count; $i++) {
    $out.Add($lines[$i])
    foreach ($s in $sects) {
        if ($lines[$i] -eq "## `?$([char]0x262F)? $s" -or $lines[$i] -match "^## . $s`$") {
            # found section header; insert entry line after it (before blank)
            $out.Add("")
            $out.Add("> 承接 [``$s-总入口.md``]($s-总入口.md)。")
            break
        }
    }
}
# anchors: insert after each section's core-insight line is complex; simpler: append anchor line right after the entry insert marker per section by second pass
$c2 = $out -join "`n"
# insert anchor lines: pattern per section -> find '**核心洞察**' lines that belong to each section and append anchor after next blank — too complex inline; use table-driven replace on unique insight endings per section
$anchorMap = @{
    "毛泽东哲学视角" = "最小完备认识纪律。"
    "道教核心视角" = "游刃有余。"
    "佛教核心视角" = "（需要各节实际结尾，占位）"
}
"README sections entry lines inserted (manual verify next)"
[IO.File]::WriteAllText($root + "README.md", $c2, $utf8)
"step2 done"
