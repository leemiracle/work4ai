# 正则表达式 · 实战场景速查

> 一行场景 → 一条正则。先能跑，再谈优化。不同引擎差异是真坑，见末节。

## 🚨 最常用 5 条
```bash
grep -E 'error|warn' app.log              # 提取日志里 error 或 warn 行
rg 'TODO|FIXME' --type py                 # ripgrep 跨文件搜（比 grep 快 10x）
sed -i 's/foo/bar/g' file.txt             # 全文替换并写回
perl -i -pe 's/\d+/NUM/g' file.txt        # perl 替换（比 sed 强，跨平台一致）
echo "a=1,b=2" | grep -oE '[0-9]+'        # 只输出匹配部分
```

---

## 提取
```bash
grep -E 'pattern' file                    # 基本提取匹配行
grep -oE '[0-9.]+' file                   # -o 只输出匹配部分（不输出整行）
grep -oE 'pattern' file | sort | uniq -c  # 提取并统计频次
rg 'pattern'                              # ripgrep 递归当前目录，默认忽略 .gitignore
rg -i 'error' --type py                   # 忽略大小写 + 只搜 .py
rg -n 'TODO' -g '*.md' -g '!node_modules' # 包含 .md 排除 node_modules
rg -A2 -B2 'panic'                        # 匹配行 + 上下各 2 行
grep -P '\b(\w+)\1\b' file                # PCRE：回溯引用（grep -P 才支持）
```

### capture group（捕获组）
```bash
echo "2024-01-15 error: disk full" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
# 输出: 2024-01-15
echo "user=alice" | sed -E 's/user=(.*)/\1/'           # 用 \1 反向引用提取
echo "name: Bob" | grep -oP '(?<=name: ).*'            # grep -P 支持后向断言
echo "a=1,b=2,c=3" | grep -oE '[a-z]=[0-9]'            # 提取所有 key=value
```

### 命名捕获
```bash
# Python：命名捕获更清晰，复杂正则强烈推荐
python3 -c "
import re
m = re.search(r'(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<level>\w+):\s*(?P<msg>.*)', '2024-01-15 ERROR: disk full')
print(m.group('date'), m.group('level'), m.group('msg'))
"
# perl 命名捕获 (?<name>...)
echo "2024-01-15" | perl -ne '/(?<y>\d{4})-(?<m>\d{2})/ and print "$+{y}/$+{m}"'
```

### ripgrep 高级
```bash
rg -r '$1' '(https?://\S+)' file.md       # -r 替换（只输出，不改文件）
rg --json 'pattern' | jq                  # 结构化输出给脚本处理
rg -P '(?<=prefix)\w+'                    # 用 PCRE 引擎（后向断言等）
rg --pcre2 'pattern'                      # 显式指定 pcre2 引擎
```

---

## 替换
```bash
sed -i 's/old/new/g' file.txt             # 全局替换写回文件（GNU sed）
sed -i '' 's/old/new/g' file.txt          # macOS BSD sed 需要多一个空 -i''
sed -i.bak 's/old/new/g' file.txt         # 顺便备份原文件 file.txt.bak
sed -E 's/[0-9]+/N/g'                     # -E 用扩展正则（+ ? {} 不用转义）
```

### perl 替换（最强，跨平台一致）
```bash
perl -i -pe 's/foo/bar/g' file.txt        # 等价 sed -i 但所有系统行为一致
perl -i -pe 's/(\w+)=(\w+)/$2=$1/' file   # 交换 key=value
perl -i -pe 's/\d+/sprintf("X%03d",$&)/e' # /e 执行 perl 代码做替换
perl -0777 -i -pe 's/<script.*?<\/script>//gs' file.html  # -0777 滑过换行；/s 让 . 匹配换行
perl -i.bak -ne 'print if /pattern/' file # 当 grep 用，过滤行写回
```

### Python re.sub
```python
import re
re.sub(r'\d+', 'N', "a1b22c333")          # 'aNbNcN'
re.sub(r'(\w+)=(\w+)', r'\2=\1', "a=1")    # '1=a'，反向引用
re.sub(r'\d+', lambda m: str(int(m.group())*2), "a3b5")  # 函数做动态替换 → 'a6b10'
re.sub(r'(?P<x>\d+)', r'<\g<x>>', "a1")    # 命名组反向引用
# flags：re.IGNORECASE / re.DOTALL(. 匹配换行) / re.MULTILINE(^$ 匹配每行)
```

---

## 常用模式
```bash
# Email（RFC 5322 太复杂，实战用这版够 90% 场景）
grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

# IPv4
grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b'
# IPv4 严格（每段 0-255）
perl -ne 'print "$1\n" while /((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})/g'

# IPv6（简化版，匹配压缩形式 :: ）
grep -oE '([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:)*::([0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}'

# URL
grep -oE 'https?://[A-Za-z0-9./?=_&%#:+~-]+'
# 更严格的 URL（含 host 校验）用 Python urllib.parse 验证

# 中文（Unicode 范围）
grep -oP '[\x{4e00}-\x{9fff}]+'           # PCRE 写法
python3 -c "import re; print(re.findall(r'[\u4e00-\u9fff]+', 'hello 世界 abc 中国'))"   # Python

# 手机号（中国大陆）
grep -oE '1[3-9][0-9]{9}'

# 身份证号（粗）
grep -oE '[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]'

# JSON 里提取字符串值
echo '{"name":"alice","age":30}' | grep -oP '"name"\s*:\s*"\K[^"]*'    # 输出 alice
echo '{"name":"alice"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])"  # 别用正则，用解析器

# 弱密码检测（无大小写无数字无符号，<8 位）
grep -E '^[a-z]{1,7}$' /etc/passwd 2>/dev/null || echo "demo only"
```

---

## 贪婪 vs 非贪婪 & 回溯灾难（ReDoS）
```bash
# 贪婪：默认匹配尽可能多
echo '<a><b>' | grep -oE '<.*>'           # <a><b>（贪婪，吃到最后的 >）
echo '<a><b>' | grep -oE '<.*?>'          # <a> <b>（非贪婪，加 ?）
```

### ReDoS（正则灾难性回溯）
```python
# 经典邪恶模式 (a+)+$ —— 输入 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!" 卡死
import re
re.search(r'^(a+)+$', 'a' * 30 + '!')     # 指数级回溯，CPU 100% 几十秒
# Cloudflare 2019 因为 (?:(?:\"|'|\)|\|\s|(?:%|&|\?|\*|@|\$)\s).*){32,} 这类规则
# 把 WAF 打挂（CVE-2019-11043 是另一种，php-fpm 正则引发）
```
**ReDoS 识别要点：**
- 嵌套量词 `(a+)+` `(a*)*` `(a|a)*`
- 重叠的交替 `(a|ab)+`
- 输入无法匹配但前缀大量匹配 → 引擎穷举所有分割方式

**防御：**
```bash
# 用 RE2（Go/C++/Rust 默认）—— 线性时间，不回溯
# Python 装 google-re2，Java 装 com.google.re2j
pip install google-re2
python3 -c "import re2; re2.search(r'^(a+)+\$', 'a'*30+'!')"   # 瞬间返回 None
# 或设超时（Python 3.11+）
# signal.alarm / 用子进程跑
```

---

## 不同引擎差异（真坑）
```
BRE (basic)    sed/grep 默认： + ? {} () 需转义 \+ \? \{1,3\} \(\)
ERE (extended) grep -E / sed -E： + ? () 直接用，反向引用 \1
PCRE           grep -P / perl / python re： 最全，支持后向断言/命名组/原子组
RE2            Go regexp / Rust regex / google-re2： 线性时间，无回溯引用 \1
```

### 为什么 RE2 / Go 没有反向引用
```go
// Go 的 regexp 包基于 RE2：
//   - 保证 O(n) 时间，不会有 ReDoS
//   - 代价：不支持 backreference (\1) 和 lookahead
// 真要 backreference：github.com/dlclark/regexp2（PCRE 兼容）
re := regexp.MustCompile(`(\w+)\s+\1`)   // Go: 编译错误 error parsing regexp
// Python re 支持 \1；re.search(r'(\w+)\s+\1', 'hello hello') 命中
```

### 各工具默认引擎
```bash
grep          # 默认 BRE，-E 走 ERE，-P 走 PCRE
sed           # 默认 BRE，-E 走 ERE
awk           # ERE
perl          # PCRE（事实标准）
python re     # PCRE 风格，略有差异（如 \d 默认 Unicode）
go regexp     # RE2（无 backreference）
rg / ripgrep  # 默认 Rust regex（RE2 系），--pcre2 切到 PCRE
```

### 跨平台兼容性
```bash
# macOS 的 sed/grep 是 BSD 版，行为和 GNU 不一致
# -i 在 BSD 必须带 -i ''（GNU 可不带）
# 推荐：macOS brew install grep sed perl，用 ggrep / gsed，或干脆用 perl
```

---

## 性能优化
```bash
grep -E '^ERROR' app.log          # 锚定：能加 ^ $\b 就加，前缀固定可 Boyer-Moore，快很多
grep -E '[0-9]{4}'                # 具体字符类比 .... 快（引擎知道只匹配数字）
rg 'pattern' big.log              # 大文件用 rg > grep（SIMD 加速 5-10x）；避免嵌套量词 (a+)+
```

### 原子组 / 固化分组（PCRE 才有）
```bash
perl -ne 'print if /^(?>a+)+b$/'      # (?>...) 原子组：匹配后不回溯，防 ReDoS
# Python re 不支持 (?>)，re2 天然不回溯不需要；Java 同 PCRE
```

### 编译复用（编程场景）
```python
import re
# 循环里多次匹配同一正则：预编译，避免每次解析，比 re.search(r'...', line) 快 10x+
PAT = re.compile(r'\d{4}-\d{2}-\d{2}')
for line in big_file:
    if PAT.search(line): ...
# 比 re.search(r'...', line) 每次重编译快 10x+
```

---

## 工具
```bash
# 在线测试（必用）
# https://regex101.com —— 选 PCRE/Python/Go/Java 引擎，实时高亮+解释
# https://regexr.com —— 教学友好
# https://debuggex.com —— 画正则可视化 railroad 图

# 命令行工具
rg --pcre2 'pattern'                     # ripgrep 用 PCRE2
pcre2grep 'pattern' file                 # 直接用 PCRE2 grep
python3 -c "import re; print(re.findall(r'\d+', open('f').read()))"
```

---

## 实战 30 例

### 日志解析
```bash
# 1. 提取 ERROR 级别 + 时间戳
grep -E '^\[.*ERROR' app.log

# 2. 统计各 HTTP 状态码数量
grep -oE 'HTTP/[0-9.]+" [0-9]{3}' access.log | grep -oE '[0-9]{3}$' | sort | uniq -c | sort -rn

# 3. 提取 5xx 错误的 URL
grep -oE '"[A-Z]+ (\S+) HTTP.*" 5[0-9]{2}' access.log | awk '{print $1, $2}'

# 4. 找最慢的 10 个请求（从耗时字段）
grep -oE '[0-9.]+$' access.log | sort -rn | head -10

# 5. 提取异常堆栈的方法名
grep -oE 'at (\S+)\(' stacktrace.log | awk '{print $2}'

# 6. 日志去重（同模式归并）
sed -E 's/[0-9]+/N/g; s/[0-9a-f]{8,}/HASH/g' app.log | sort | uniq -c | sort -rn | head

# 7. 提取 JSON 日志字段（推荐 jq，不要硬抠正则）
cat log.jsonl | jq 'select(.level=="error") | .msg'

# 8. 提取 nginx upstream 响应时间
grep -oE 'upstream_response_time=([0-9.]+)' nginx.log
```

### CSV / 数据处理
```bash
# 9. 第 3 列包含某值的行
awk -F',' '$3 ~ /keyword/' data.csv

# 10. 替换 CSV 里所有空字符串为 NULL
perl -F, -alne '$_ =~ s/,,/,NULL,/g for @F; print join ",", @F' data.csv

# 11. 提取引号内的字段（处理逗号在引号内的情况）
python3 -c "import csv,sys; [print(r[2]) for r in csv.reader(sys.stdin)]" < data.csv

# 12. 拆分 key=value 列表
echo "a=1 b=2 c=3" | grep -oE '\b\w+=\w+\b'

# 13. 校验整列是不是都是数字
awk -F',' '{if ($2 !~ /^[0-9]+$/) print NR": "$2}' data.csv

# 14. 行号重排（重置 1..N）
awk 'BEGIN{n=0} {n++; print n","$0}' data.txt
```

### 手机号 / 电话规范化
```bash
# 15. 把各种格式手机号统一成 11 位
echo "138-1234-5678 / 138 1234 5678 / +86 13812345678" | \
  grep -oE '1[3-9][0-9 -]{8,11}' | tr -d ' -'

# 16. 提取文本里所有电话
perl -ne 'print "$1\n" while /((?:\+?86[-\s]?)?1[3-9]\d{9})/g' text.txt

# 17. 给电话打码（中间 4 位变 *）
sed -E 's/(1[3-9][0-9])[0-9]{4}([0-9]{4})/\1****\2/' contacts.txt

# 18. 提取带区号的座机
grep -oE '0[0-9]{2,3}-[0-9]{7,8}' file
```

### 代码 / 配置
```bash
# 19. 删除行尾空格
sed -i 's/[ \t]*$//' file.py

# 20. 把 TAB 换成 4 空格
unexpand -t 4 file | expand -t 4        # 或 sed 's/\t/    /g'

# 21. 提取所有 TODO/FIXME 加注释
grep -rEn 'TODO|FIXME' --include='*.py'

# 22. 把单引号字符串改成双引号
perl -i -pe "s/'([^']*)'/\"\$1\"/g" file.py

# 23. 找未关闭的括号（简易）
python3 -c "
s=open('f').read()
print('paren diff:', s.count('(')-s.count(')'))
print('brace diff:', s.count('{')-s.count('}'))
"

# 24. 提取 Python 函数定义
grep -nE '^\s*def\s+\w+' module.py

# 25. nginx 配置去掉注释和空行
grep -vE '^\s*#|^\s*$' nginx.conf
```

### 文本清洗
```bash
# 26. 合并多行（CSV 一行一条但内部换行）—— 用 perl 滑过整个文件
perl -0777 -pe 's/\n(?!\d)/ /g' data.txt

# 27. 全角转半角
python3 -c "import sys; sys.stdout.write(sys.stdin.read().translate(str.maketrans('０１２３４５６７８９ＡＺ','0123456789AZ')))"

# 28. 提取 markdown 链接 URL
grep -oE '\]\(\K[^)]+' README.md

# 29. 检测重复行（去重前后对比）
sort file | uniq -d

# 30. 简易敏感信息扫描（信用卡/邮箱/密钥模式）
grep -rE '(4[0-9]{12}(?:[0-9]{3})?|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+|api[_-]?key["'\'' ]*[:=]["'\'' ]*[A-Za-z0-9]{16,})' . --include='*.json'
```

---
*参考：本仓库 `github-repos/references/CS-Notes/`（正则/编辑器笔记）、`notes/code-review-程序员视角`（敏感信息扫描）。规则线上测试必上 regex101.com。*
