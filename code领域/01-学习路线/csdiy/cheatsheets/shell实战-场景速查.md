# Shell 实战 · 场景速查

> 命令原文 + 一句话场景。命令行下能 10 秒解决的，别写脚本。

## 🚨 最常用 5 条
```bash
grep -rn "关键词" .                 # 全目录递归搜内容（最常用没有之一）
find . -name "*.py"                 # 按名字找文件
ps aux | grep python                # 看某进程在不在、PID 多少
df -h                               # 磁盘还剩多少
du -sh * | sort -h                  # 当前目录各项各占多大空间
```

---

## 找文件 / 找内容
```bash
find . -name "*.log" -mtime -7      # 找 7 天内修改过的日志
find . -type f -size +100M          # 找大于 100MB 的文件
find . -name "*.py" -delete         # 找到并直接删（危险，先去掉 -delete 预览）
find . -type d -name node_modules -prune   # 找目录，但跳过 node_modules
locate filename                     # 比 find 快，查全库索引（先 updatedb）
which python3                       # 命令的可执行文件在哪
grep -rn "TODO" --include=*.py      # 只在 .py 文件里搜 TODO
grep -i "error" app.log             # 忽略大小写搜
grep -v "^#" nginx.conf             # 去掉注释行，只看生效配置
grep -c "ERROR" app.log             # 数一下 ERROR 出现多少次
```

## 文本处理三剑客速用（grep / sed / awk）
```bash
# grep：筛选行
cat app.log | grep ERROR            # 只保留含 ERROR 的行
grep -E "ERR|WARN" app.log          # 正则，匹配 ERR 或 WARN
grep -A 3 -B 1 "PANIC" app.log      # 匹配行 + 后3行 + 前1行（看上下文）

# sed：流式替换/删除
sed -i 's/old/new/g' file.txt       # 全文替换并写回文件（-i 直接改）
sed '5d' file.txt                   # 删第 5 行（不改源，输出到屏幕）
sed '/^$/d' file.txt                # 删所有空行
sed -n '10,20p' file.txt            # 只看第 10-20 行

# awk：按列处理
awk '{print $2,$4}' file.txt        # 打印第 2、4 列
awk -F',' '{print $1}' data.csv     # CSV 按逗号切，取第 1 列
awk '{sum+=$1} END{print sum}' nums.txt   # 把第 1 列全加起来
awk 'NR==3' file.txt                # 只打印第 3 行（NR=行号）
```

## 批量改名 / 批量操作
```bash
rename 's/\.jpeg$/.jpg/' *.jpeg     # 批量改后缀（Debian 系有 rename）
for f in *.txt; do mv "$f" "${f%.txt}.md"; done   # 纯 bash 改后缀，通用
for f in *.jpg; do convert "$f" "thumb_$f"; done  # 批量加前缀处理
ls *.log | xargs gzip               # 批量压缩所有日志
find . -name "*.bak" | xargs rm     # 批量删除 .bak 文件
```

## 统计 / 计数
```bash
wc -l *.py                          # 数每个文件的行数
find . -name "*.py" | xargs wc -l | tail -1   # 统计所有 py 总行数
sort | uniq -c | sort -rn           # 频次统计 Top（经典三连）
ls | wc -l                          # 数当前目录多少个文件
grep -o "foo" file.txt | wc -l      # 数 foo 在文件里出现多少次
```

## 进程管理
```bash
ps aux | grep python                # 找某类进程
top                                 # 实时看资源占用（交互式）
htop                                # 更好用的 top（需装）
kill 12345                          # 按 PID 礼貌终止（SIGTERM）
kill -9 12345                       # 强杀（SIGKILL，进程不响应时）
pkill -f "python train.py"          # 按命令行关键词杀进程
jobs                                # 看后台任务
bg / fg                             # 后台 / 前台切换
nohup python run.py > log 2>&1 &    # 退出终端也继续跑
```

## 磁盘 / 内存排查
```bash
df -h                               # 各分区使用率
du -sh * | sort -h                  # 谁吃了磁盘
du -h --max-depth=1 /var            # 只看一层
ncdu /                              # 交互式找大目录（需装）
free -h                             # 内存占用
```

## 网络排查
```bash
ss -tlnp                            # 看哪些端口在监听（替代 netstat）
ss -tnp                             # 看当前所有 TCP 连接
curl -i https://api.example.com     # 看响应头和正文
curl -X POST -d '{"a":1}' -H "Content-Type: application/json" URL  # POST JSON
curl -fsSL https://get.docker.com | sh   # 下载脚本并执行
curl -o file.tar.gz URL             # 下载
curl -w "%{http_code}\n" -o /dev/null -s URL   # 只取 HTTP 状态码
jq '.data[].name' resp.json         # 解析 JSON，取嵌套字段
jq '.[] | select(.age>18)' users.json   # 过滤数组
ping -c 3 example.com               # 通不通
dig example.com                     # DNS 查询
```

## 压缩 / 解压
```bash
tar -czf archive.tar.gz dir/        # 打包并 gzip 压缩
tar -xzf archive.tar.gz             # 解压 .tar.gz
tar -xjf archive.tar.bz2            # 解压 .tar.bz2
unzip file.zip -d dest/             # 解压 zip 到目录
zip -r out.zip dir/                 # 压缩成 zip
```

## 实用组合（复制即用）
```bash
# 1. 统计当前项目代码行数（排除依赖）
find . -name "*.py" -not -path "*/venv/*" | xargs wc -l | tail -1

# 2. 找最近改过的 10 个文件
find . -type f -printf '%T@ %p\n' | sort -rn | head

# 3. 看日志最后实时刷新（排查线上问题）
tail -f app.log | grep ERROR

# 4. 按第 3 列数值降序排
sort -t' ' -k3 -rn file.txt

# 5. 统计某目录下各类文件数量
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
```
