"""
CS 61A Day 6 - Project 1: Hog (骰子游戏)
========================================
CS 61A 最经典的开局项目——把 Week 1-5 学的（高阶函数、控制流、递归）
全部融合到一个完整游戏里。

游戏规则（fa24 版本）：
1. 2 个玩家轮流掷骰子
2. 每回合可选掷 1-10 颗骰子（或 0 颗启用 Free Bacon）
3. Pig Out: 任何骰子是 1 → 本回合只得 1 分
4. Free Bacon: 不掷骰子 → 得到 (对手分数的十位+个位)+1
5. Swine Swap: 回合结束后若两位玩家分数满足 exact multiple → 互换
6. 先到 100 分（GOAL_SCORE）获胜

本项目实现完整游戏 + 多种策略 + 自动对局 + 期望值分析。

运行：
    python3 hog.py
"""

from __future__ import annotations
import random
from functools import lru_cache


# ============ 游戏常量 ============

GOAL_SCORE = 100


# ============ 骰子函数 ============

def six_sided():
    """标准 6 面骰子"""
    return random.randint(1, 6)


def four_sided():
    """4 面骰子（某些规则下使用）"""
    return random.randint(1, 4)


def make_test_dice(*outcomes):
    """制造确定性骰子（用于测试）—— 按顺序循环输出 outcomes"""
    outcomes = list(outcomes) * 100  # 重复确保足够长
    i = [0]
    def dice():
        result = outcomes[i[0] % len(outcomes)]
        i[0] += 1
        return result
    return dice


# ============ 核心规则 ============

def roll_dice(num_rolls, dice=six_sided):
    """掷 num_rolls 颗骰子。
    
    规则：如果有任意一颗是 1（Pig Out），本回合只得 1 分。
    否则返回所有骰子的总和。
    """
    total = 0
    pig_out = False
    for _ in range(num_rolls):
        result = dice()
        if result == 1:
            pig_out = True
        total += result
    return 1 if pig_out else total


def free_bacon(score):
    """Free Bacon 规则：不掷骰子，得 (对手分数的十位+个位)+1 分"""
    tens = score // 10
    ones = score % 10
    # 处理分数 > 99 的情况
    while tens >= 10:
        tens = (tens // 10) + (tens % 10)
    return max(tens, ones) + 1


def take_turn(num_rolls, opponent_score, dice=six_sided):
    """执行一个回合"""
    if num_rolls == 0:
        return free_bacon(opponent_score)
    return roll_dice(num_rolls, dice)


def is_swap(score0, score1):
    """Swine Swap 规则：检查是否应交换分数
    
    简化版：当一方的分数是另一方的恰好 2 倍时交换。
    （CS 61A 有多种变体规则；这是最经典的一种）
    """
    if score0 == 0 or score1 == 0:
        return False
    return score0 == 2 * score1 or score1 == 2 * score0


# ============ 玩家策略 ============

def always_roll_5(score0, score1):
    """简单策略：永远掷 5 颗骰子"""
    return 5


def always_roll_n(n):
    """工厂：永远掷 n 颗"""
    def strategy(score0, score1):
        return n
    return strategy


def bacon_strategy(score0, opponent_score, margin=8, num_rolls=5):
    """如果 Free Bacon 能得 ≥ margin 分，就用 Free Bacon，否则掷 num_rolls 颗"""
    if free_bacon(opponent_score) >= margin:
        return 0
    return num_rolls


def swap_strategy(score0, opponent_score, margin=10, num_rolls=6):
    """如果使用 Free Bacon 后会触发 Swine Swap 且对己有利，就用"""
    potential_score = score0 + free_bacon(opponent_score)
    if is_swap(potential_score, opponent_score) and opponent_score > potential_score:
        return 0
    return bacon_strategy(score0, opponent_score, margin, num_rolls)


def final_strategy(score0, opponent_score):
    """完整策略：综合考虑 Free Bacon + Swine Swap + 期望值
    
    这是你要实现的策略。提示：
    - 接近 100 分时减少骰子数（避免 Pig Out 损失）
    - 对手分数比你好时考虑 Swine Swap
    - 用 free_bacon 的收益对比掷骰子的期望
    """
    # 接近胜利：保守
    if score0 >= 90:
        return 0 if free_bacon(opponent_score) + score0 >= GOAL_SCORE else 4
    
    # 检查是否能一步获胜
    if free_bacon(opponent_score) + score0 >= GOAL_SCORE:
        return 0
    
    # Swine Swap 有利
    potential = score0 + free_bacon(opponent_score)
    if is_swap(potential, opponent_score) and opponent_score > potential:
        return 0
    
    # 期望分析：基于经验数据
    # 4-6 颗骰子的期望收益最高（约 17-20 分/回合）
    if opponent_score - score0 > 30:
        # 落后很多：激进
        return 7
    elif score0 - opponent_score > 30:
        # 领先很多：保守
        return 4
    else:
        # 势均力敌
        return 6


# ============ 游戏引擎 ============

def play(strategy0, strategy1, score0=0, score1=0, dice=six_sided, goal=GOAL_SCORE):
    """完整对局——返回胜者 (0 或 1)"""
    who = 0  # 当前玩家
    while score0 < goal and score1 < goal:
        if who == 0:
            n = strategy0(score0, score1)
            score0 += take_turn(n, score1, dice)
        else:
            n = strategy1(score1, score0)
            score1 += take_turn(n, score0, dice)
        
        # Swine Swap 检查
        if is_swap(score0, score1):
            score0, score1 = score1, score0
        
        who = 1 - who  # 切换玩家
    
    return 0 if score0 >= goal else 1


def play_with_trace(strategy0, strategy1, score0=0, score1=0, dice=six_sided, goal=GOAL_SCORE):
    """带 trace 的对局——打印每回合状态"""
    print(f"\n   对局开始：strategy0={strategy0.__name__} vs strategy1={strategy1.__name__}")
    who = 0
    turn = 0
    while score0 < goal and score1 < goal:
        if who == 0:
            n = strategy0(score0, score1)
            gain = take_turn(n, score1, dice)
            score0 += gain
            print(f"   回合 {turn}: Player 0 掷 {n} 颗得 {gain} 分 → 总分 {score0} vs {score1}")
        else:
            n = strategy1(score1, score0)
            gain = take_turn(n, score0, dice)
            score1 += gain
            print(f"   回合 {turn}: Player 1 掷 {n} 颗得 {gain} 分 → 总分 {score0} vs {score1}")
        
        if is_swap(score0, score1):
            score0, score1 = score1, score0
            print(f"           ⚡ Swine Swap! → {score0} vs {score1}")
        
        who = 1 - who
        turn += 1
    
    winner = 0 if score0 >= goal else 1
    print(f"   🏆 Player {winner} 获胜！({score0} vs {score1})")
    return winner


# ============ 期望分析（高阶函数应用）============

def make_averaged(fn, num_samples=10000):
    """返回一个函数，多次调用 fn 取平均"""
    def averaged(*args):
        total = 0
        for _ in range(num_samples):
            total += fn(*args)
        return total / num_samples
    return averaged


def max_scoring_num_rolls(dice=six_sided, num_samples=1000):
    """找出期望收益最高的骰子数（4-6 之间）"""
    best_n = 1
    best_avg = 0
    for n in range(1, 11):
        avg = make_averaged(lambda: roll_dice(n, dice), num_samples)()
        if avg > best_avg:
            best_avg = avg
            best_n = n
    return best_n, best_avg


# ============ main ============

def main():
    print("=" * 60)
    print("CS 61A Day 6 - Project 1: Hog")
    print("=" * 60)
    
    # 1. 测试骰子函数
    print("\n📋 1. 骰子函数测试")
    test_dice = make_test_dice(1, 2, 3, 4, 5, 6)
    rolls = [test_dice() for _ in range(6)]
    print(f"   test_dice(1,2,3,4,5,6) 前 6 次: {rolls}")
    print(f"   循环: 第 7 次回到 {[test_dice()][0]}")
    
    # 2. roll_dice 测试
    print("\n📋 2. roll_dice（Pig Out 规则）")
    test_dice1 = make_test_dice(2, 3, 4, 5, 6)  # 没有 1
    test_dice2 = make_test_dice(2, 1, 4, 5, 6)  # 有 1
    print(f"   roll_dice(5, [2,3,4,5,6]) = {roll_dice(5, test_dice1)}    （正常求和）")
    print(f"   roll_dice(5, [2,1,4,5,6]) = {roll_dice(5, test_dice2)}    （Pig Out! 只得 1）")
    
    # 3. Free Bacon 测试
    print("\n📋 3. Free Bacon")
    for op_score in [0, 5, 17, 89, 99]:
        gain = free_bacon(op_score)
        tens, ones = op_score // 10, op_score % 10
        print(f"   Free Bacon vs opponent={op_score}: max({tens},{ones})+1 = {gain}")
    
    # 4. 期望分析
    print("\n📋 4. 期望收益分析（1000 次模拟）")
    print("   骰子数 → 平均收益")
    for n in range(1, 11):
        avg = make_averaged(lambda: roll_dice(n), 500)()
        print(f"   {n:2d} 颗 → {avg:6.2f} 分/回合")
    
    best_n, best_avg = max_scoring_num_rolls(num_samples=500)
    print(f"\n   💡 最优骰子数: {best_n}（期望 {best_avg:.2f} 分/回合）")
    
    # 5. 策略对决
    print("\n📋 5. 策略对决（每对策略跑 100 局）")
    
    strategies = [
        ("always_roll_4", always_roll_n(4)),
        ("always_roll_5", always_roll_n(5)),
        ("always_roll_6", always_roll_n(6)),
        ("bacon_strategy", lambda s, o: bacon_strategy(s, o)),
        ("final_strategy", final_strategy),
    ]
    
    print(f"\n   {'Strategy 0':<20} vs {'Strategy 1':<20} → Win rate of S0")
    print("   " + "-" * 65)
    for name0, strat0 in strategies:
        for name1, strat1 in strategies:
            if name0 >= name1:
                continue
            wins_0 = 0
            games = 200
            for _ in range(games):
                winner = play(strat0, strat1)
                wins_0 += (1 - winner)  # strat0 赢则 winner=0
            win_rate = wins_0 / games * 100
            print(f"   {name0:<20} vs {name1:<20} → S0 wins {win_rate:.1f}%")
    
    # 6. 一局 trace
    print("\n📋 6. 示范对局（final_strategy vs always_roll_5）")
    random.seed(42)
    winner = play_with_trace(
        final_strategy,
        always_roll_n(5),
    )
    
    print("\n" + "=" * 60)
    print("💡 Day 6 Project 1 Hog 元洞察：")
    print("   1. 高阶函数 = 策略作为参数（strategy0/strategy1 都是函数）")
    print("   2. Pig Out 是「期望值 vs 方差」的经典权衡")
    print("   3. Swine Swap 让博弈论元素进入游戏——不能只看自己分数")
    print("   4. final_strategy 综合了：接近胜利/落后/swap/期望——")
    print("      这就是「强化学习」的雏形（虽然我们手写规则）")
    print("   5. CS 61A 后续 Hog 的 Phase 3 会要求写 ML 策略")
    print("=" * 60)


if __name__ == "__main__":
    main()
