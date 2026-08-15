# fix-readme-variants.ps1
param()
$path = "C:\workspace\work4ai\README.md"
$lines = [IO.File]::ReadAllLines($path)
$out = New-Object System.Collections.Generic.List[string]
$n = 0
foreach ($l in $lines) {
    if ($l -match '^> 承接 `.{1,20}(视角|心学)-总入口\.md`（规划中，正文见本节') { $n++; continue }
    if ($l -match '^\*\*通用锚点\*\*：`.{1,20}(视角|心学)-锚点块\.md`（规划中，正文见本节') { $n++; continue }
    if ($l -match '^\| `./强化学习视角-总入口\.md`（规划中') -or $l -match '^\| `./强化学习视角-锚点块\.md`（规划中）') {
        $out.Add('| [`强化学习视角-元迭代器.md`](强化学习视角-元迭代器.md) | RL 视角迭代正文（原总入口/锚点块规划已并入该文件） |')
        continue
    }
    $out.Add($l)
}
[IO.File]::WriteAllLines($path, $out, (New-Object Text.UTF8Encoding($false)))
"README fixed: $n variant lines dropped, RL rows repointed"
