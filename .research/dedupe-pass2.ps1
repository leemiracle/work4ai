# dedupe-pass2.ps1 — locate blocks by fingerprint line (backtrack to nearest '## ' header)
param()
$finger = '核心视角-总入口\.md`（规划中）|核心视角-锚点块\.md`（规划中）|视角-总入口\.md`（规划中）|视角-锚点块\.md`（规划中）'
$files = Get-ChildItem -Recurse -Filter *.md | Where-Object {
    $_.FullName -notmatch '\\\.git\\|\\\.research\\|\\\.workbuddy-ai\\|\\\.tools\\|\\\.agent\\' -and
    $_.FullName -ne "C:\workspace\work4ai\README.md" -and
    $_.Name -ne "黑格尔观念论核心视角-总入口.md"
}
$script:delBlocks = 0; $script:keepBlocks = 0; $script:delLines = 0; $script:fileCount = 0
foreach ($f in $files) {
    $raw = [IO.File]::ReadAllText($f.FullName)
    if ($raw -notmatch '（规划中）') { continue }
    $hasBom = $raw.Length -gt 0 -and $raw[0] -eq [char]0xFEFF
    $lines = $raw -split "`r?`n"
    $out = New-Object System.Collections.Generic.List[string]
    $i = 0; $fileDel = 0
    while ($i -lt $lines.Count) {
        $hit = $false
        # look ahead: if a fingerprint line appears before the next '## ' header, this is a template block
        if ($lines[$i] -match '^#{2,3} .{0,30}视角') {
            $end = $i + 1
            while ($end -lt $lines.Count -and $lines[$end] -notmatch '^## ' -and $lines[$end] -notmatch '^# ') { $end++ }
            $body = $lines[$i..($end-1)] -join "`n"
            if ($body -match $finger) {
                $hit = $true
                if ($body -match '本命题即主题') {
                    $script:keepBlocks++
                    for ($k=$i; $k -lt $end; $k++) { $out.Add($lines[$k]) }
                } else {
                    $script:delBlocks++; $fileDel++; $script:delLines += ($end - $i)
                }
                $i = $end
            }
        }
        if (-not $hit) { $out.Add($lines[$i]); $i++ }
    }
    if ($fileDel -gt 0) {
        $collapsed = New-Object System.Collections.Generic.List[string]
        $blankRun = 0
        foreach ($l in $out) {
            if ($l -match '^\s*$') { $blankRun++ } else {
                if ($blankRun -ge 1) { $collapsed.Add('') }
                $blankRun = 0; $collapsed.Add($l)
            }
        }
        $final = New-Object System.Collections.Generic.List[string]
        $n = $collapsed.Count
        for ($j=0; $j -lt $n; $j++) {
            if ($collapsed[$j] -match '^---\s*$') {
                $final.Add('---')
                $k = $j + 1
                while ($k -lt $n -and ($collapsed[$k] -match '^\s*$' -or $collapsed[$k] -match '^---\s*$')) { $k++ }
                $j = $k - 1
            } else { $final.Add($collapsed[$j]) }
        }
        while ($final.Count -gt 0 -and ($final[$final.Count-1] -match '^\s*$' -or $final[$final.Count-1] -match '^---\s*$')) { $final.RemoveAt($final.Count-1) }
        $newText = ($final -join "`n") + "`n"
        $useEnc = if ($hasBom) { New-Object Text.UTF8Encoding($true) } else { New-Object Text.UTF8Encoding($false) }
        [IO.File]::WriteAllText($f.FullName, $newText, $useEnc)
        $script:fileCount++
    }
}
"PASS2 DELETED: $script:delBlocks blocks / $script:delLines lines in $script:fileCount files; KEPT filled: $script:keepBlocks"
