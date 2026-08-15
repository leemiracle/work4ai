# dedupe-philosophy-blocks.ps1 — remove duplicated philosophy template blocks across md files
# Keeps: root README.md (authoritative), blocks containing real filled content ('本命题即主题')
param()

$hdrPattern = '^## .{0,6}(新柏拉图主义|道家|道教|佛教|禅宗|玄学|墨家|法家|兵家|儒家|名家|纵横家|农家|杂家|小说家|阴阳家|斯多葛主义|黑格尔观念论|人道教|阳明心学|毛泽东哲学|荀子|庄子|老子|气学|理学|心学|功利主义|实用主义|存在主义|现象学|结构主义|后现代|分析哲学|语言哲学|科学哲学|认识论|形而上学|伦理学|政治哲学|亚里士多德主义|伊壁鸠鲁主义|斯多葛|怀疑主义|经院哲学|理性主义|经验主义|德国观念论|浪漫主义|唯意志论|实证主义|新康德主义|生命哲学|过程哲学|实用|逻辑实证|批判理性|历史主义|解释学|法兰克福学派|存在|解构|后结构)(核心视角|视角|主义视角)\s*$'

$files = Get-ChildItem -Recurse -Filter *.md | Where-Object {
    $_.FullName -notmatch '\\\.git\\|\\\.research\\|\\\.workbuddy-ai\\|\\\.tools\\|\\\.agent\\' -and
    $_.FullName -ne "C:\workspace\work4ai\README.md"
}

$script:delBlocks = 0
$script:keepBlocks = 0
$script:delLines = 0
$script:fileCount = 0
$script:report = @()

foreach ($f in $files) {
    $raw = [IO.File]::ReadAllText($f.FullName)
    $enc = New-Object Text.UTF8Encoding($false)
    $hasBom = $raw.Length -gt 0 -and $raw[0] -eq [char]0xFEFF
    $lines = $raw -split "`r?`n"
    $out = New-Object System.Collections.Generic.List[string]
    $i = 0
    $fileDel = 0
    while ($i -lt $lines.Count) {
        if ($lines[$i] -match $hdrPattern) {
            $end = $i + 1
            while ($end -lt $lines.Count -and $lines[$end] -notmatch '^## ' -and $lines[$end] -notmatch '^# ') { $end++ }
            $body = $lines[$i..($end-1)] -join "`n"
            # SAFETY: only delete blocks carrying the template fingerprint (planned-file reference)
            # AND without real filled content
            if ($body -match '本命题即主题' -or $body -notmatch '（规划中）') {
                $script:keepBlocks++
                for ($k=$i; $k -lt $end; $k++) { $out.Add($lines[$k]) }
                $i = $end
            } else {
                $script:delBlocks++
                $fileDel++
                $script:delLines += ($end - $i)
                # swallow trailing separator blank lines handled by collapse pass
                $i = $end
                # if next non-blank line is '---' separator that belonged to the removed block section, keep it (collapse pass will dedupe)
            }
        } else {
            $out.Add($lines[$i])
            $i++
        }
    }
    if ($fileDel -gt 0) {
        # collapse: 3+ consecutive blanks -> 1 blank line
        $collapsed = New-Object System.Collections.Generic.List[string]
        $blankRun = 0
        foreach ($l in $out) {
            if ($l -match '^\s*$') { $blankRun++ }
            else {
                if ($blankRun -ge 2) { $collapsed.Add('') }
                elseif ($blankRun -eq 1) { $collapsed.Add('') }
                $blankRun = 0
                $collapsed.Add($l)
            }
        }
        # collapse duplicate '---' separated only by blanks
        $final = New-Object System.Collections.Generic.List[string]
        $n = $collapsed.Count
        for ($j=0; $j -lt $n; $j++) {
            if ($collapsed[$j] -match '^---\s*$') {
                # look ahead: skip blanks and another '---', keep single
                $final.Add('---')
                $k = $j + 1
                while ($k -lt $n -and ($collapsed[$k] -match '^\s*$' -or $collapsed[$k] -match '^---\s*$')) { $k++ }
                # preserve at most one blank after separator
                $j = $k - 1
            } else { $final.Add($collapsed[$j]) }
        }
        # trim trailing blanks / separators
        while ($final.Count -gt 0 -and ($final[$final.Count-1] -match '^\s*$' -or $final[$final.Count-1] -match '^---\s*$')) { $final.RemoveAt($final.Count-1) }
        $newText = ($final -join "`n") + "`n"
        $useEnc = if ($hasBom) { New-Object Text.UTF8Encoding($true) } else { $enc }
        [IO.File]::WriteAllText($f.FullName, $newText, $useEnc)
        $script:fileCount++
        $script:report += "$($f.FullName.Replace('C:\workspace\work4ai\','')) : -$fileDel blocks"
    }
}
"DELETED: $script:delBlocks blocks / $script:delLines lines in $script:fileCount files; KEPT filled: $script:keepBlocks"
$script:report | Select-Object -First 15
