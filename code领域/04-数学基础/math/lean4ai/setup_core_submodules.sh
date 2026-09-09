#!/bin/bash
# 添加核心Lean4依赖为Git Submodule（不包括mathlib4）

echo "📦 添加核心Lean4依赖为Git Submodule..."

cd /mnt/c/workspace/math/lean4ai
git checkout master

# 小型仓库列表（不包括mathlib4）
declare -A repos=(
    ["batteries"]="https://github.com/leanprover-community/batteries.git"
    ["quote4"]="https://github.com/leanprover-community/quote4.git"
    ["repl"]="https://github.com/leanprover-community/repl.git"
    ["ProofWidgets4"]="https://github.com/leanprover-community/ProofWidgets4.git"
    ["aesop"]="https://github.com/leanprover-community/aesop.git"
    ["duper"]="https://github.com/leanprover-community/duper.git"
)

for repo in "${!repos[@]}"; do
    url="${repos[$repo]}"
    echo ""
    echo "➤ 添加 $repo..."
    
    # 删除现有目录
    [ -d "$repo" ] && rm -rf "$repo"
    
    # 添加submodule
    if git submodule add "$url" "$repo" 2>&1 | grep -q "already exists"; then
        echo "  ⚠️  已存在，跳过"
    else
        echo "  ✅ 添加成功"
    fi
done

echo ""
echo "📊 Submodule状态:"
git submodule status

echo ""
echo "💾 提交更改..."
git add .gitmodules
git commit -m "chore: Add Lean4 dependency submodules

- batteries: Extended standard library
- quote4: Metaprogramming tools
- repl: Interactive environment
- ProofWidgets4: Proof visualization
- aesop: Automated tactics
- duper: Automated proving"

echo ""
echo "✅ 完成！"
echo ""
echo "💡 下一步:"
echo "  git push origin master"
echo ""
echo "在其他电脑克隆时:"
echo "  git clone --recursive git@github.com:leemiracle/lean4ai.git"
echo "  或"
echo "  git clone git@github.com:leemiracle/lean4ai.git"
echo "  git submodule update --init --recursive"
