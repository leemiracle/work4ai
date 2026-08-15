"""
15-112 Programming Fundamentals for CS (CMU)
================================================
覆盖主题（对应 lecture / unit）：
- 二维博弈：Tic-Tac-Toe minimax + alpha-beta 剪枝
- 动态规划入门：BlackJack 最优策略 DP（Kusty chart）
- 棋类评估函数：Othello position weights + mobility

核心教材/论文：
- "The Art of Computer Programming Vol 4" Knuth（minimax / alpha-beta）
- "Sutton & Barto Reinforcement Learning" Ch 6（BlackJack DP）
- Silver et al. 2016 "Mastering the game of Go with deep neural networks and tree search" Nature 529:484-489 (AlphaGo)（评估函数思想, 评估+搜索）

本文件实现：
- Tic-Tac-Toe minimax（完美博弈，绝不输）
- alpha-beta 剪枝（节点访问数对比）
- BlackJack 期望回报 DP（hit/stand 全空间）
- Othello 评估函数（mobility + corner）

运行：
    python3 fundamentals.py
"""
from __future__ import annotations
import math
import random
from functools import lru_cache

# ============ 1. Tic-Tac-Toe Minimax ============

# 棋盘编码: tuple of 9 cells, each 'X' / 'O' / '.'
WINS = [
    (0,1,2),(3,4,5),(6,7,8),  # rows
    (0,3,6),(1,4,7),(2,5,8),  # cols
    (0,4,8),(2,4,6),          # diags
]

def winner(board):
    for a,b,c in WINS:
        if board[a] == board[b] == board[c] != '.':
            return board[a]
    return None

def is_full(board):
    return '.' not in board

def empty_cells(board):
    return [i for i,c in enumerate(board) if c == '.']

# --- plain minimax: returns best score for current player ---

def minimax(board, is_maximizing, nodes=None):
    """X maximizes (+1 win), O minimizes (-1 win)."""
    if nodes is not None:
        nodes[0] += 1
    w = winner(board)
    if w == 'X':
        return 1
    if w == 'O':
        return -1
    if is_full(board):
        return 0
    player = 'X' if is_maximizing else 'O'
    if is_maximizing:
        best = -math.inf
        for i in empty_cells(board):
            nb = board[:i] + (player,) + board[i+1:]
            best = max(best, minimax(nb, False, nodes))
        return best
    else:
        best = math.inf
        for i in empty_cells(board):
            nb = board[:i] + (player,) + board[i+1:]
            best = min(best, minimax(nb, True, nodes))
        return best

# --- alpha-beta pruning ---

def alphabeta(board, alpha, beta, is_maximizing, nodes=None):
    if nodes is not None:
        nodes[0] += 1
    w = winner(board)
    if w == 'X':
        return 1
    if w == 'O':
        return -1
    if is_full(board):
        return 0
    player = 'X' if is_maximizing else 'O'
    if is_maximizing:
        best = -math.inf
        for i in empty_cells(board):
            nb = board[:i] + (player,) + board[i+1:]
            val = alphabeta(nb, alpha, beta, False, nodes)
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break  # beta cutoff
        return best
    else:
        best = math.inf
        for i in empty_cells(board):
            nb = board[:i] + (player,) + board[i+1:]
            val = alphabeta(nb, alpha, beta, True, nodes)
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break  # alpha cutoff
        return best

def best_move(board, player='X', use_ab=True):
    """Find best move for current player."""
    bl = list(board)
    best_val = -math.inf if player == 'X' else math.inf
    best_i = None
    for i in empty_cells(board):
        nb = board[:i] + (player,) + board[i+1:]
        if use_ab:
            val = alphabeta(nb, -math.inf, math.inf, player == 'O')
        else:
            val = minimax(nb, player == 'O')
        if player == 'X' and val > best_val:
            best_val, best_i = val, i
        elif player == 'O' and val < best_val:
            best_val, best_i = val, i
    return best_i, best_val


# ============ 2. BlackJack DP ============
# State: (player_sum 12-21, dealer_upcard 1-10, usable_ace 0/1)
# Action: HIT or STAND
# Returns: expected reward

@lru_cache(maxsize=None)
def blackjack_dp(player_sum, dealer_up, usable_ace, is_hit_phase):
    """
    Compute expected value of Blackjack state.
    Simplified: infinite deck, cards 1-10 with prob 1/13 each (face cards=10 → prob 4/13).
    """
    CARD_PROBS = [(v, 1/13 if v < 10 else 4/13) for v in range(1, 11)]

    if is_hit_phase:
        # Player decides to hit: draw one card
        ev = 0.0
        for card_val, prob in CARD_PROBS:
            new_sum = player_sum + card_val
            new_usable = usable_ace
            # handle ace
            if card_val == 1 and new_sum + 10 <= 21:
                new_sum += 10
                new_usable = 1
            # reduce from soft to hard if bust
            if new_sum > 21 and new_usable:
                new_sum -= 10
                new_usable = 0
            if new_sum > 21:
                ev += prob * (-1.0)  # bust
            else:
                # compare with stand value vs continue hitting
                stand_ev = dealer_ev(new_sum, dealer_up)
                hit_ev = blackjack_dp(new_sum, dealer_up, new_usable, True)
                ev += prob * max(stand_ev, hit_ev)
        return ev
    else:
        # STAND: see dealer play
        return dealer_ev(player_sum, dealer_up)

def dealer_ev(player_sum, dealer_up):
    """Dealer plays to 17 (stand on soft 17). Returns reward for player."""
    CARD_PROBS = [(v, 1/13 if v < 10 else 4/13) for v in range(1, 11)]
    # simulate dealer draws
    def simulate_dealer(d_sum, usable_ace):
        if d_sum >= 17:
            if d_sum > 21:
                return 1.0  # dealer bust → player wins
            if d_sum > player_sum:
                return -1.0
            elif d_sum < player_sum:
                return 1.0
            else:
                return 0.0
        ev = 0.0
        for card_val, prob in CARD_PROBS:
            ns = d_sum + card_val
            nu = usable_ace
            if card_val == 1 and ns + 10 <= 21:
                ns += 10
                nu = 1
            if ns > 21 and nu:
                ns -= 10
                nu = 0
            if ns > 21:
                ev += prob * 1.0
            else:
                ev += prob * simulate_dealer(ns, nu)
        return ev
    # dealer's visible upcard + hidden card
    ev = 0.0
    for card_val, prob in CARD_PROBS:
        d_sum = dealer_up + card_val
        usable = 0
        if dealer_up == 1 or card_val == 1:
            if d_sum + 10 <= 21:
                d_sum += 10
                usable = 1
        if d_sum > 21 and usable:
            d_sum -= 10
            usable = 0
        ev += prob * simulate_dealer(d_sum, usable)
    return ev

def blackjack_strategy_table():
    """Generate hit/stand table for player_sum 12-21 vs dealer 2-10."""
    table = {}
    for psum in range(12, 22):
        row = []
        for dup in range(2, 11):
            stand_ev = dealer_ev(psum, dup)
            hit_ev = blackjack_dp(psum, dup, 0, True)
            action = 'H' if hit_ev > stand_ev else 'S'
            row.append(action)
        table[psum] = row
    return table


# ============ 3. Othello Evaluation ============

# Othello position weights (classic)
OTHELLO_WEIGHTS = [
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120],
]

def othello_evaluate(board, player):
    """board: 8x8 with 'B'/'W'/'.', player: 'B' or 'W'."""
    opp = 'W' if player == 'B' else 'B'
    score = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == player:
                score += OTHELLO_WEIGHTS[r][c]
            elif board[r][c] == opp:
                score -= OTHELLO_WEIGHTS[r][c]
    # mobility
    my_moves = len(othello_legal_moves(board, player))
    opp_moves = len(othello_legal_moves(board, opp))
    if my_moves + opp_moves > 0:
        score += 10 * (my_moves - opp_moves) / (my_moves + opp_moves)
    return score

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def othello_legal_moves(board, player):
    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c] == '.' and _would_flip(board, r, c, player):
                moves.append((r, c))
    return moves

def _would_flip(board, r, c, player):
    opp = 'W' if player == 'B' else 'B'
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        found_opp = False
        while 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == opp:
            found_opp = True
            nr += dr
            nc += dc
        if found_opp and 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == player:
            return True
    return False


# ============ Demo ============

def demo():
    print("=" * 60)
    print("15-112 Fundamentals: Games, DP, Evaluation")
    print("=" * 60)
    random.seed(42)

    # --- 1. Tic-Tac-Toe ---
    print("\n📋 1. Tic-Tac-Toe Minimax vs Alpha-Beta")
    empty = tuple(['.'] * 9)

    nodes_plain = [0]
    minimax(empty, True, nodes_plain)

    nodes_ab = [0]
    alphabeta(empty, -math.inf, math.inf, True, nodes_ab)

    print(f"   Plain minimax nodes explored: {nodes_plain[0]}")
    print(f"   Alpha-beta nodes explored:    {nodes_ab[0]}")
    print(f"   Pruning ratio: {nodes_ab[0]/nodes_plain[0]:.1%} of nodes kept")

    # Verify perfect play: O plays center, X can force draw
    print(f"\n   Perfect play result (X first): {minimax(empty, True)}")
    print("   → 0 = draw (perfect play = never lose)")

    # --- 2. BlackJack DP ---
    print("\n📋 2. BlackJack Strategy (DP)")
    blackjack_dp.cache_clear()
    table = blackjack_strategy_table()
    print("       Dealer:  " + "  ".join(f"{d:>2}" for d in range(2,11)))
    print("   Player")
    for psum in range(12, 22):
        row = "  ".join(f" {a} " for a in table[psum])
        print(f"   {psum:>5}:  {row}")
    print("   H=Hit  S=Stand")

    # 反直觉：软 17 vs 硬 17
    soft17_stand = dealer_ev(17, 10)
    soft17_hit = blackjack_dp(17, 10, 1, True)
    hard16_stand = dealer_ev(16, 10)
    hard16_hit = blackjack_dp(16, 10, 0, True)
    print(f"\n   Soft 17 (usable ace) vs dealer 10:")
    print(f"     Stand EV = {soft17_stand:.3f}, Hit EV = {soft17_hit:.3f}")
    print(f"   Hard 16 vs dealer 10:")
    print(f"     Stand EV = {hard16_stand:.3f}, Hit EV = {hard16_hit:.3f}")
    print(f"   💡 反直觉：硬 16 vs 10 虽然大概率爆牌(H)，但 STAND 期望更差！")

    # --- 3. Othello ---
    print("\n📋 3. Othello Position Evaluation")
    mid = [['.']*8 for _ in range(8)]
    mid[3][3], mid[4][4] = 'W', 'W'
    mid[3][4], mid[4][3] = 'B', 'B'
    mid[0][0] = 'B'  # black takes a corner!
    ev_no_corner = othello_evaluate(
        [[mid[r][c] if (r,c)!=(0,0) else '.' for c in range(8)] for r in range(8)], 'B')
    ev_with_corner = othello_evaluate(mid, 'B')
    print(f"   Black evaluation WITHOUT corner (0,0): {ev_no_corner}")
    print(f"   Black evaluation WITH corner (0,0):    {ev_with_corner}")
    print(f"   💡 One corner = +{ev_with_corner - ev_no_corner} pts (corner worth ~120!)")

    print("\n✅ 15-112 Fundamentals 完成！")
    print("   覆盖：minimax / αβ剪枝 / BlackJack DP / Othello 评估")


if __name__ == "__main__":
    demo()
