# Vim 生存 · 场景速查

> 命令原文 + 一句话场景。先会逃（:q!），再会存（:wq），最后会快。

## 🚨 最常用 5 条
```
:wq                # 保存并退出（:w 存 / :q 退 / :q! 不存强退救命用）
i                  # 在光标前进入插入模式（a 在后 / o 下开新行）
dd                 # 删整行（5dd 删 5 行）
yy                 # 复制整行（p 粘贴）
/关键词            # 搜索（n 下一个 / N 上一个）
```
> 记不住时按 `ESC` 回到普通模式，`:q!` 强退不保存，永远能逃生。

---

## 移动 / 跳转
```
h j k l            # 左 下 上 右（基础移动）
w / b              # 向前 / 向后跳一个单词
0 / ^              # 行首 / 第一个非空字符
$                  # 行尾
gg / G             # 文件开头 / 文件末尾
:42                # 跳到第 42 行
%                  # 跳到匹配的括号 ( [ { } ] )
*                  # 跳到当前光标下单词的下一个出现处
Ctrl-o / Ctrl-i    # 回到上一个 / 下一个光标位置（跳转历史）
gd                 # 跳到光标下变量的定义处
{  /  }            # 上一段 / 下一段空行
Ctrl-d / Ctrl-u    # 下 / 上翻半屏
```

## 编辑（插入 + 删除 + 改）
```
i  a  o            # 光标前插入 / 光标后插入 / 下方新行插入
I  A  O            # 行首插入 / 行尾追加 / 上方新行插入
x                  # 删一个字符（3x 删 3 个）
dw                 # 删到下一个单词开头
d$ / D             # 删到行尾
cc / S             # 改整行（删掉并进入插入）
cw                 # 改一个单词
u                  # 撤销（undo）
Ctrl-r             # 重做（redo）
.                  # 重复上一次修改命令（神技）
>>  <<             # 整行右移 / 左移（缩进）
guu  gUU           # 整行转小写 / 大写
~                  # 反转当前字符大小写
```

## 复制 / 粘贴 / 寄存器
```
yy                 # 复制当前行（3yy 复制 3 行）
yw                 # 复制一个单词
p  /  P            # 粘贴到光标后 / 前
V                  # 进入"行可视"模式，选中后 y 复制 / d 删除
Ctrl-v             # 进入"块可视"模式，可列选（批量加注释用）
"ay                # 复制到寄存器 a
"ap                # 从寄存器 a 粘贴（多段复制互不覆盖）
```

## 搜索替换
```
/foo               # 向下搜 foo
?foo               # 向上搜
n / N              # 下一个 / 上一个匹配
:%s/旧/新/g        # 全文替换（不加 g 只换每行第一个）
:%s/旧/新/gc       # 替换前逐个确认
:s/旧/新/g         # 只替换当前行
:5,20s/旧/新/g     # 只替换第 5-20 行
:noh               # 清掉高亮（搜索后满屏黄字看着烦）
*  然后 cw 改词     # 快速改名：* 定位→cw 改→n 找下一个→. 重复
```

## 多文件 / 分屏
```
:vsp file2         # 垂直分屏打开 file2（:sp 水平分屏）
:e file2           # 当前窗口换成 file2
:buffers / :ls     # 列出已打开的文件
:bn / :bp          # 切到下一个 / 上一个 buffer
Ctrl-w h/j/k/l      # 在分屏间移动焦点
Ctrl-w =            # 让所有分屏等大
Ctrl-w |            # 当前分屏最大化（垂直）
:q                  # 关闭当前分屏（:only 关掉其他只留当前）
```

## 宏录制（批量重复操作神器）
```
qa                 # 开始录制宏到寄存器 a
   ...你的操作...
q                  # 停止录制
@a                 # 执行寄存器 a 里的宏一次
100@a              # 执行 100 次（自动到尾停止）
@@                 # 重复执行上次的宏
```
> 经典场景：给每行行首加 `//` —— `qa` → `I// <Esc>` → `q` → 选中行后 `:@a`

## 选区批量操作（可视模式 + 块选）
```
Ctrl-v 选中几列    # 块可视模式列选
Shift-i 输入文本 Esc  # 给选中列每行都插入（批量注释/加前缀）
:  然后输入 s/^/\/\//g   # 给选中行批量加 // 注释
```

## 保存 / 退出 / 权限救场
```
:w                 # 存盘
:w!                # 强制存（只读文件先 :w!）
:wq / :x           # 存盘退出
:q!                # 不存盘强退（搞砸了就跑）
:w new.txt         # 另存为新文件
:w !sudo tee %     # 用 sudo 存只读系统文件（忘用 sudo 编辑 /etc 时救命）
ZZ / ZQ            # 等价 :x / :q!（快捷键）
```

## 最小配置（~/.vimrc，让 Vim 顺手）
```vim
syntax on                  " 语法高亮
set number                 " 显示行号
set relativenumber         " 相对行号（配合 5j 这类跳转）
set tabstop=4 shiftwidth=4 expandtab   " Tab=4空格，输入转空格
set autoindent             " 自动缩进
set hlsearch incsearch     " 高亮搜索 + 边打边搜
set ignorecase smartcase   " 搜小写忽略大小写，带大写则精确
set mouse=a                " 鼠标可用
set clipboard=unnamedplus  " 和系统剪贴板互通
nnoremap <C-s> :w<CR>      # Ctrl-s 保存
```

## 插件最小集（用 vim-plug 装在 ~/.vim/autoload/）
```
Plug 'tpope/vim-surround'      " 快速加/改/删引号括号 cs"' ds"
Plug 'tpope/vim-commentary'    " gcc 注释一行 / gc 注释选区
Plug 'preservim/nerdtree'      " :NERDTree 文件树侧栏
Plug 'junegunn/fzf.vim'        " :Files / :Rg 模糊搜（依赖 fzf）
Plug 'sheerun/vim-polyglot'    " 各语言语法高亮合集
```
> 安装：在 vim 里 `:PlugInstall`。不想折腾就用这些，覆盖 90% 日常。
