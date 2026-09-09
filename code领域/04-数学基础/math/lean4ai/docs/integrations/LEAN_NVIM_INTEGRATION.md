# lean.nvim 集成：Neovim 中的 Lean 开发环境

## 📖 项目概述

**lean.nvim** 是 Neovim 的 Lean 4 支持插件，提供完整的 Lean 开发体验，包括 LSP、语义高亮、infoview 等。

### 核心功能

| 功能 | 描述 |
|------|------|
| **LSP 支持** | Language Server Protocol |
| **语义高亮** | 服务器驱动的语法高亮 |
| **Infoview** | 交互式证明状态查看 |
| **代码操作** | 代码建议和快速修复 |
| **自动补全** | 智能补全支持 |
| **映射** | 丰富的快捷键 |

---

## 🎯 与我们项目的整合价值

### 1. 完整的开发环境

```
我们的 Lean4 开发环境：
┌─────────────────────────────────────────────┐
│              编辑器选择                │
├─────────────────────────────────────────────┤
│                                         │
│  VS Code                    Neovim       │
│  ├── lean4 扩展            ├── lean.nvim │
│  ├── 图形化界面            ├── 终端集成  │
│  └── Git 集成               └── Vim 优势   │
│                                         │
├─────────────────────────────────────────────┤
│              Lean4 验证层                │
│  ├── Leantime                            │
│  ├── Agile                               │
│  ├── Quant                               │
│  └── Medical                             │
└─────────────────────────────────────────────┘
```

### 2. 技术借鉴

| 技术 | 用途 | 我们的应用 |
|------|------|-----------|
| **Infoview** | 实时证明状态 | 验证状态查看器 |
| **语义高亮** | 智能高亮 | 项目文件高亮 |
| **代码操作** | 快速修复 | 验证错误修复 |
| **映射系统** | 快捷键 | 统一快捷键 |

---

## 🔧 安装和配置

### 1. 使用 lazy.nvim 安装（推荐）

```lua
-- ~/.config/nvim/lua/plugins/lean.lua

return {
  'Julian/lean.nvim',
  event = { 'BufReadPre *.lean', 'BufNewFile *.lean' },
  
  dependencies = {
    'nvim-lua/plenary.nvim',
    -- 可选依赖
    'hrsh7th/nvim-cmp',         -- 补全
    'nvim-telescope/telescope.nvim', -- pickers
  },
  
  ---@type lean.Config
  opts = {
    mappings = true,  -- 启用建议的映射
    infoview = {
      autoopen = true,  -- 自动打开 infoview
      width = 0.4,      -- 占屏幕 40%
      height = 0.4,
    },
    abbreviations = {
      enable = true,
      extra = {
        wknight = '♘',  -- 添加骑士符号
      },
    },
  },
}
```

### 2. 使用 vim-plug 安装

```vim
" ~/.config/nvim/plugin/lean.vim

Plug 'Julian/lean.nvim'
Plug 'nvim-lua/plenary.nvim'

lua require('lean').setup{ mappings = true }
```

### 3. 完整配置示例

```lua
-- ~/.config/nvim/lua/config/lean.lua

local M = {}

function M.setup()
  require('lean').setup({
    -- 映射
    mappings = true,
    
    -- LSP 设置
    lsp = {
      init_options = {
        editDelay = 10,        -- 编辑延迟（毫秒）
        hasWidgets = true,     -- 启用 widgets
      },
    },
    
    -- 语义高亮
    -- 需要在颜色方案中配置
    
    -- 防止意外修改标准库
    nomodifiable = {
        -- 保护 Lean 标准库
        -- 可以添加我们自己的受保护路径
      },
    
    -- 缩写支持
    abbreviations = {
      enable = true,
      extra = {
        -- 数学符号
        forall = '∀',
        exists = '∃',
        lambda = 'λ',
        arrow = '→',
        -- 国际象棋符号（示例）
        wknight = '♘',
      },
    },
    
    -- Infoview 设置
    infoview = {
      autoopen = true,       -- 自动打开
      width = 0.4,           -- 宽度 40%
      height = 0.4,          -- 高度 40%
      orientation = "auto",  -- 自动方向
    },
    
    -- 进度指示器
    progress_bars = {
      -- 在大型项目中显示进度
      enable = true,
    },
  })
  
  -- 设置 LocalLeader
  vim.g.maplocalleader = ' '  -- 空格键
  
  -- 自动命令
  vim.api.nvim_create_autocmd('FileType', {
    pattern = 'lean',
    callback = function()
      -- 设置缩进
      vim.bo.tabstop = 2
      vim.bo.shiftwidth = 2
      vim.bo.expandtab = true
      
      -- 自动打开 infoview
      vim.cmd('LeanInfoview')
    end,
  })
end

return M
```

---

## ⌨️ 快捷键映射

### 在 Lean 文件中

| 快捷键 | 功能 | 描述 |
|-------|------|------|
| `<LocalLeader>i` | 切换 infoview | 打开/关闭证明状态窗口 |
| `<LocalLeader>p` | 暂停 infoview | 暂停当前证明状态 |
| `<LocalLeader>r` | 重启服务器 | 重启 Lean LSP 服务器 |
| `<LocalLeader>v` | 配置视图 | 配置 infoview 选项 |
| `<LocalLeader>x` | 放置 pin | 放置 infoview pin |
| `<LocalLeader>c` | 清除 pins | 清除所有 pins |
| `<LocalLeader>dx` | 放置 diff pin | 放置差异 pin |
| `<LocalLeader>dc` | 清除 diff | 清除差异 pins |
| `gd` | 跳转定义 | 跳转到定义 |
| `gD` | 跳转声明 | 跳转到声明 |
| `gy` | 跳转类型 | 跳转到类型定义 |
| `K` | 悬停文档 | 显示悬停文档 |
| `gr` | 查找引用 | 查找所有引用 |
| `<Esc>` | 清除提示 | 清除所有提示 |
| `J` | 跳转到提示 | 跳转到下一个提示 |
| `C` | 关闭 tooltip | 关闭当前 tooltip |

### 在 Infoview 中

| 快捷键 | 功能 |
|-------|------|
| `<LocalLeader><Tab>` | 跳转到下一个 infoview |

---

## 💡 实用技巧

### 1. Infoview 工作流

```lua
-- 在 Neovim 中打开 Lean 文件
:e MyProject/Basic.lean

-- Infoview 会自动打开
-- 显示当前证明状态

-- 按 <LocalLeader>i 手动切换
-- 按 <LocalLeader>p 暂停

-- 放置 pin 以跟踪特定位置
-- 按 <LocalLeader>x 在当前行放置 pin
-- 按 <LocalLeader>c 清除所有 pins
```

### 2. 代码操作

```lua
-- 在 Lean 文件中
-- 光标在 "sorry" 上时按 <LocalLeader>...

-- 或者使用 Neovim 的代码操作
:lua vim.lsp.buf.code_action()
```

### 3. 缩写输入

```lua
-- 输入 \forall 然后按空格
-- 会自动展开为 ∀

-- 自定义缩写（在配置中添加）
forall → ∀
exists → ∃
lambda → λ
arrow → →
```

### 4. 语义高亮配置

```lua
-- 在颜色方案中添加（例如 ~/.config/nvim/colors/my_theme.lua）

-- Lean 语义高亮组
vim.api.nvim_set_hl(0, '@lsp.type.namespace.lean', { link = 'Type' })
vim.api.nvim_set_hl(0, '@lsp.type.function.lean', { link = 'Function' })
vim.api.nvim_set_hl(0, '@lsp.type.variable.lean', { link = 'Identifier' })
vim.api.nvim_set_hl(0, '@lsp.type.keyword.lean', { link = 'Keyword' })
vim.api.nvim_set_hl(0, '@lsp.type.comment.lean', { link = 'Comment' })
vim.api.nvim_set_hl(0, '@lsp.type.string.lean', { link = 'String' })
```

---

## 🔗 与我们项目的集成

### 1. 统一开发环境配置

```lua
-- 为我们的项目创建特定配置
-- ~/.config/nvim/ftplugin/lean_project.lua

vim.api.nvim_create_autocmd('FileType', {
  pattern = 'lean',
  callback = function()
    -- 检查是否在项目目录中
    local cwd = vim.fn.getcwd()
    if cwd:find('lean4ai') then
      -- 项目特定设置
      vim.opt.makeprg = 'lake build'
      
      -- 自定义映射
      vim.api.nvim_buf_set_keymap(0, 'n', '<Leader>lb', 
        '<cmd>lua require("lean").build()<CR>', 
        { silent = true }
      )
      
      vim.api.nvim_buf_set_keymap(0, 'n', '<Leader>lt',
        '<cmd>lua require("lean").test()<CR>',
        { silent = true }
      )
    end
  end,
})
```

### 2. 与 YC-Killer 集成

```lua
-- ~/.config/nvim/lua/plugins/yc_killer.lua

return {
  'sahibzada-allahyar/YC-Killer',  -- 假设有一个 Neovim 插件
  
  config = function()
    -- 集成 lean.nvim 和 YC-Killer
    vim.api.nvim_create_autocmd('FileType', {
      pattern = 'lean',
      callback = function()
        -- YC-Killer AI 助手
        vim.api.nvim_buf_set_keymap(0, 'n', '<Leader>ai',
          '<cmd>YCKillerAssist<CR>',
          { silent = true }
        )
      end,
    })
  end,
}
```

### 3. 项目特定映射

```lua
-- ~/.config/nvim/lua/config/lean_mappings.lua

local M = {}

function M.setup_project_mappings()
  vim.api.nvim_create_autocmd('FileType', {
    pattern = 'lean',
    callback = function()
      -- 项目管理快捷键
      vim.api.nvim_buf_set_keymap(0, 'n', '<Leader>vp',
        '<cmd>lua require("leantime").verify_project()<CR>',
        { desc = 'Verify project', silent = true }
      )
      
      -- Sprint 验证
      vim.api.nvim_buf_set_keymap(0, 'n', '<Leader>vs',
        '<cmd>lua require("agile").verify_sprint()<CR>',
        { desc = 'Verify sprint', silent = true }
      )
      
      -- 风险评估
      vim.api.nvim_buf_set_keymap(0, 'n', '<Leader>vr',
        '<cmd>lua require("leantime").assess_risks()<CR>',
        { desc = 'Assess risks', silent = true }
      )
      
      -- 生成报告
      vim.api.nvim_buf_set_keymap(0, 'n', '<Leader>gr',
        '<cmd>lua require("leantime").generate_report()<CR>',
        { desc = 'Generate report', silent = true }
      )
    end,
  })
end

return M
```

---

## 📊 与 VS Code 对比

| 功能 | VS Code | Neovim + lean.nvim |
|------|---------|-------------------|
| **LSP** | ✅ | ✅ |
| **Infoview** | ✅ | ✅ |
| **语义高亮** | ✅ | ✅ |
| **代码操作** | ✅ | ✅ |
| **性能** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **键盘导向** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **可扩展性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **终端集成** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Git 集成** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **学习曲线** | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🚀 快速开始

### 1. 安装 Neovim（如果还没有）

```bash
# Linux
sudo apt install neovim

# MacOS
brew install neovim

# Windows (WSL)
# 已安装
```

### 2. 配置 Neovim

```bash
# 创建配置目录
mkdir -p ~/.config/nvim/lua/plugins

# 创建 lean.nvim 配置
cat > ~/.config/nvim/lua/plugins/lean.lua << 'EOF'
return {
  'Julian/lean.nvim',
  event = { 'BufReadPre *.lean', 'BufNewFile *.lean' },
  dependencies = { 'nvim-lua/plenary.nvim' },
  opts = { mappings = true },
}
EOF

# 安装插件
nvim --headless '+Lazy! sync' +qa
```

### 3. 打开 Lean 文件

```bash
cd /mnt/c/workspace/math/lean4ai/YC-Killer-Lean4/Agile
nvim Verification.lean
```

### 4. 验证安装

```
-- 在 Neovim 中按：
:checkhealth lean

-- 应该显示：
-- lean.nvim: ok
-- Lean LSP: running
-- Infoview: attached
```

---

## 📚 相关资源

### 官方资源
- **lean.nvim GitHub**: https://github.com/Julian/lean.nvim
- **Wiki**: https://github.com/Julian/lean.nvim/wiki
- **dotfyle**: https://dotfyle.com/plugins/Julian/lean.nvim

### Neovim 资源
- **Neovim**: https://neovim.io
- **lazy.nvim**: https://github.com/folke/lazy.nvim
- **nvim-cmp**: https://github.com/hrsh7th/nvim-cmp

---

## 💡 总结

### lean.nvim 为我们带来

| 优势 | 描述 |
|------|------|
| **性能** | 比 VS Code 快得多 |
| **键盘导向** | 完全不用鼠标 |
| **终端集成** | 无缝终端工作流 |
| **可扩展** | Lua 配置强大 |

### 为什么选择 Neovim

1. ✅ **轻量级** - 启动快，内存占用小
2. ✅ **键盘导向** - 高效的编辑工作流
3. ✅ **终端友好** - 与 WSL/SSH 完美集成
4. ✅ **可扩展** - Lua 脚本强大
5. ✅ **社区活跃** - 持续更新

---

## 🎯 下一步

1. **安装 Neovim**: 如果还没有
2. **配置 lean.nvim**: 按照上面的步骤
3. **打开我们的 Lean 文件**: 测试功能
4. **自定义配置**: 根据需要调整

---

**项目状态**: ✅ **推荐使用**

**编辑器支持**: VS Code + lean.nvim (Neovim)

**最后更新**: 2025-03-25
