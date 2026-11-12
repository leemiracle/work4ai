# wsl_labs · WSL 进阶实验（lab08 / lab09）

服务 [16 章 CFR](../16-CFR与扑克AI.md)（lab08）与 [17 章 自博弈](../17-自博弈与多智能体RL.md)（lab09）。

## 环境（一次性）

```bash
wsl -d Ubuntu-22.04                       # 发行版：Ubuntu-22.04（python3.10 + pip3）
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple open_spiel matplotlib numpy
python3 -c "import pyspiel; print(pyspiel.load_game('kuhn_poker'))"   # 自检
```

- 镜像先行（清华源），失败再走代理——与主 [README 运行环境](../README.md)公约一致。
- lab09 是**纯标准库 + numpy/matplotlib**，不依赖 open_spiel——Windows 侧直接 `python experiments/` 同样可跑。
- 本目录所有产物 png 与脚本同目录落盘：仓库在 `/mnt/c/...` 同盘，WSL 写入后 **Windows 侧立即可见**，无需拷贝。

## 运行

```bash
wsl -d Ubuntu-22.04 -- bash -lc "cd /mnt/c/workspace/work4ai/讲透博弈论/wsl_labs && python3 lab08_openspiel_cfr.py"
wsl -d Ubuntu-22.04 -- bash -lc "cd /mnt/c/workspace/work4ai/讲透博弈论/wsl_labs && python3 lab09_selfplay_mcts.py"
```

- lab08（~2 分钟）：OpenSpiel 官方 `CFRSolver`/`CFRPlusSolver` 跑 Kuhn 10⁵ 迭代——与理论 −1/18、[lab07](../experiments/lab07_learning_cfr.py) 手写值**三方对拍** + nash_conv 双对数收敛曲线 → `openspiel_cfr.png`。
- lab09（~30 秒）：纯 python MCTS（UCB1 + 随机 rollout + **MCTS-Solver**，Winands 2008）自博弈井字棋，{0,10²,10³,10⁴} 模拟/步 四档棋力矩阵 + Elo 曲线 → `mcts_selfplay.png`。诚实标注：随机 rollout 的 vanilla UCT 在井字棋上有战术盲区（实测 23% 合法局面选掉分，装 Solver 后 13%）——这正是 17 章"价值网络替代 rollout"动机的最小现场。
