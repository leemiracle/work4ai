# Git 进阶 · 救命场景速查

> 命令原文 + 一句话场景。先救命，再优雅。

## 🚨 最常用 5 条
```bash
git status                          # 我现在处于什么状态
git diff                            # 到底改了什么（未暂存的）
git log --oneline --graph -10       # 看最近 10 个提交的脉络
git stash                           # 先把改动藏起来，待会儿再处理
git reset --hard HEAD               # 彻底丢弃所有改动，回到上次提交
```

---

## 撤回 commit
```bash
git commit --amend --no-edit        # 刚 commit 完发现忘加文件，追加进去
git commit --amend                   # 改最近一次 commit 的信息
git reset --soft HEAD~1              # 撤销 commit，改动全部留在暂存区
git reset --mixed HEAD~1             # 撤销 commit + 撤销 add，改动留在工作区（默认）
git reset --hard HEAD~1              # 撤销 commit 并彻底丢弃改动（危险）
git revert <commit>                 # 已 push 的提交，用反向提交安全撤销
git push --force-with-lease          # 强推的"安全版"，别人推过你会被拦下
```

## 找回误删分支 / 误操作救命
```bash
git reflog                          # 看所有 HEAD 移动记录，误删分支的救命稻草
git checkout -b <分支> <reflog哈希>  # 从 reflog 指向的点重新建分支
git fsck --lost-found               # 找回被 git gc 但还没清的悬空对象
git stash list                      # 查看藏起来的改动
git stash pop                       # 取回最近一次 stash
git stash drop stash@{0}            # 丢弃指定 stash
```

## 合并冲突速解
```bash
git merge <分支>                    # 合并，冲突时会在文件里标出 <<<<<<<
git status                          # 列出所有冲突文件
# 编辑冲突文件，删掉 <<<<<<< ======= >>>>>>> 标记
git add <冲突文件>                  # 标记冲突已解决
git commit                          # 完成合并提交
git merge --abort                   # 合并搞砸了，整个回退到合并前
git rebase -i HEAD~5                # 交互式整理最近 5 个提交（合并/改序/改名）
git rebase --abort                  # rebase 冲突太多，放弃重来
git checkout --ours <文件>          # 冲突时一律保留"自己"的版本
git checkout --theirs <文件>        # 冲突时一律保留"对方"的版本
```

## bisect 二分定位引入 bug 的 commit
```bash
git bisect start                    # 开始二分查找
git bisect bad                      # 标记当前（出 bug）提交为坏
git bisect good <正常commit哈希>     # 标记一个已知正常的提交为好
# git 会自动切到中间提交，你测试后继续：
git bisect good                     # 这个提交正常
git bisect bad                      # 这个提交有 bug
git bisect reset                    # 找到元凶后退出，回到起点
git bisect log                      # 记录 bisect 过程，可重放
```

## submodule 翻车
```bash
git submodule update --init --recursive   # clone 含子模块的项目后必跑
git submodule update --remote             # 拉取子模块的最新代码
git submodule add <仓库URL> <路径>        # 添加一个子模块
git submodule deinit -f <路径>            # 子模块坏了，先取消初始化
git rm <路径>                              # 再删除子模块目录
git submodule status                      # 看每个子模块当前指向哪个 commit
```

## 清理历史 / 整理提交
```bash
git rebase -i HEAD~3                 # 压缩、改写最近 3 个提交
git rebase origin/main               # 把自己的提交挪到最新主干之上
git log --author="$(git config user.name)" --oneline   # 看自己的所有提交
git cherry-pick <commit>             # 把别的分支某个提交单独搬过来
git tag -a v1.0 -m "发布说明"         # 打带说明的标签
git push --tags                      # 把标签推到远端
```

## 清理 / 垃圾回收
```bash
git clean -fd                        # 删除所有未跟踪的文件和目录（先 -n 预览）
git clean -nd                        # 预览会删哪些，不真删
git branch -d <分支>                 # 删除已合并的本地分支
git branch -D <分支>                 # 强制删除本地分支（不管是否合并）
git remote prune origin              # 清理远端已删但本地还在的分支引用
git gc --prune=now                   # 立即压缩清理，仓库变大时跑一下
```

## 速查：到底该用哪个撤销？
```
还没 commit    → git restore <文件>        / git checkout -- <文件>
已 add 未commit→ git restore --staged <文件>(取消暂存，改动保留)
已 commit 未push→ git reset --soft HEAD~1  (留改动) / --hard(全删)
已 push         → git revert <commit>      (安全，新增反向提交)
```
