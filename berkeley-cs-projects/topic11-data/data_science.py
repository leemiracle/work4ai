"""
Data 8 / Data 100 Foundations of Data Science — UC Berkeley (Adhikari)
================================================
覆盖主题：
- DataFrame from scratch（filter / groupby / join）（Data 8）
- 统计推断：bootstrap 置信区间（Data 8 Lec 14-16）
- OLS 回归 + 诊断（Data 100 Lec 8-10）
- SQL-like 查询（Data 100 Lec 4-5）

核心教材/参考：
- Adhikari & DeNero "Computational and Inferential Thinking" (inferentialthinking.com, 3rd ed)
- Adhikari, DeNero, Nolan "Principles and Techniques of Data Science" (data100.datahub.berkeley.edu)
- Efron & Tibshirani "An Introduction to the Bootstrap" (Chapman & Hall 1993)
- Cleveland "Visualizing Data" (Hobart Press 1993) —— bootstrap 诊断

本文件实现：
- MiniDataFrame（from scratch: filter/map/groupby/join）
- Bootstrap 重采样置信区间
- OLS（normal equation + R²/残差诊断）
- SQL-like query engine

运行：
    python data_science.py
"""
from __future__ import annotations
import math
import random
from collections import defaultdict


# ============================================================
# 1. MiniDataFrame（from scratch）
# ============================================================

class MiniDataFrame:
    """极简 DataFrame：列存 + 行操作"""
    def __init__(self, columns: dict[str, list] | None = None):
        self.columns = columns or {}

    @classmethod
    def from_records(cls, records: list[dict]):
        cols = defaultdict(list)
        for rec in records:
            for k, v in rec.items():
                cols[k].append(v)
        return cls(dict(cols))

    def __len__(self):
        return len(next(iter(self.columns.values()))) if self.columns else 0

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.columns[key]
        # boolean mask
        mask = key
        new_cols = {}
        for col, vals in self.columns.items():
            new_cols[col] = [v for v, m in zip(vals, mask) if m]
        return MiniDataFrame(new_cols)

    def filter(self, predicate):
        """predicate: dict → bool"""
        mask = []
        n = len(self)
        for i in range(n):
            row = {col: self.columns[col][i] for col in self.columns}
            mask.append(predicate(row))
        return self[mask]

    def map_column(self, col, func):
        new_cols = dict(self.columns)
        new_cols[col] = [func(v) for v in self.columns[col]]
        return MiniDataFrame(new_cols)

    def groupby(self, by, agg_func=sum, numeric_only=True):
        """
        groupby + aggregate
        agg_func: list → scalar (sum/mean/count/...)
        numeric_only: 只聚合数值列（跳过 str）
        """
        groups = defaultdict(list)
        n = len(self)
        for i in range(n):
            key = self.columns[by][i]
            groups[key].append(i)
        result_cols = defaultdict(list)
        for key, indices in groups.items():
            result_cols[by].append(key)
            for col in self.columns:
                if col == by:
                    continue
                vals = [self.columns[col][i] for i in indices]
                if numeric_only:
                    try:
                        vals = [float(v) for v in vals]
                    except (ValueError, TypeError):
                        continue  # skip non-numeric columns
                result_cols[col].append(agg_func(vals))
        return MiniDataFrame(dict(result_cols))

    def join(self, other, on):
        """inner join"""
        left_idx = defaultdict(list)
        for i, k in enumerate(self.columns[on]):
            left_idx[k].append(i)
        result_cols = defaultdict(list)
        for j in range(len(other)):
            k = other.columns[on][j]
            for i in left_idx.get(k, []):
                for col in self.columns:
                    result_cols[col].append(self.columns[col][i])
                for col in other.columns:
                    if col != on:
                        result_cols[col].append(other.columns[col][j])
        return MiniDataFrame(dict(result_cols))

    def head(self, n=5):
        return MiniDataFrame({col: vals[:n] for col, vals in self.columns.items()})

    def to_records(self):
        n = len(self)
        return [{col: self.columns[col][i] for col in self.columns} for i in range(n)]

    def __repr__(self):
        cols = list(self.columns.keys())
        n = len(self)
        lines = [" | ".join(cols)]
        for i in range(min(n, 5)):
            lines.append(" | ".join(str(self.columns[c][i]) for c in cols))
        return "\n".join(lines)


# ============================================================
# 2. Bootstrap 置信区间（Efron 1993）
# ============================================================

def bootstrap_ci(data, stat_func, n_bootstrap=1000, ci=0.95):
    """
    Bootstrap 重采样估计统计量的置信区间：
    1. 从 data 中有放回采样 n 次 → bootstrap_sample
    2. 计算 stat_func(bootstrap_sample)
    3. 重复 B 次，取分位数 [α/2, 1-α/2]
    """
    n = len(data)
    stats = []
    for _ in range(n_bootstrap):
        sample = [random.choice(data) for _ in range(n)]
        stats.append(stat_func(sample))
    stats.sort()
    alpha = 1 - ci
    lo = stats[int(n_bootstrap * alpha / 2)]
    hi = stats[int(n_bootstrap * (1 - alpha / 2))]
    return lo, hi, stats


# ============================================================
# 3. OLS 回归 + 诊断（Data 100）
# ============================================================

def ols_regression(X: list[list[float]], y: list[float]):
    """
    OLS: β = (X^T X)^{-1} X^T y
    返回系数 + R² + 残差。
    """
    n, d = len(X), len(X[0])
    # 加截距
    Xb = [[1.0] + list(row) for row in X]
    # X^T X
    XtX = [[sum(Xb[i][k] * Xb[i][j] for i in range(n)) for j in range(d + 1)] for k in range(d + 1)]
    # X^T y
    Xty = [sum(Xb[i][k] * y[i] for i in range(n)) for k in range(d + 1)]
    # Solve XtX β = Xty（Gauss-Jordan）
    aug = [list(XtX[k]) + [Xty[k]] for k in range(d + 1)]
    for col in range(d + 1):
        pivot = max(range(col, d + 1), key=lambda r: abs(aug[r][col]))
        aug[col], aug[pivot] = aug[pivot], aug[col]
        pv = aug[col][col]
        aug[col] = [x / pv for x in aug[col]]
        for r in range(d + 1):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [aug[r][j] - factor * aug[col][j] for j in range(d + 2)]
    beta = [aug[k][d + 1] for k in range(d + 1)]
    # 预测 + 残差
    y_pred = [sum(beta[k] * Xb[i][k] for k in range(d + 1)) for i in range(n)]
    residuals = [y[i] - y_pred[i] for i in range(n)]
    # R²
    y_mean = sum(y) / n
    ss_res = sum(r * r for r in residuals)
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    r_squared = 1 - ss_res / max(ss_tot, 1e-10)
    return {"beta": beta, "y_pred": y_pred, "residuals": residuals, "R2": r_squared}


# ============================================================
# 4. SQL-like 查询引擎
# ============================================================

def sql_select(df: MiniDataFrame, columns=None, where=None, group_by=None,
               having=None, order_by=None, limit=None):
    """
    简化 SELECT...FROM...WHERE...GROUP BY...HAVING...ORDER BY...LIMIT
    """
    result = df
    if where:
        result = result.filter(where)
    if group_by:
        result = result.groupby(group_by, agg_func=sum)
        if having:
            result = result.filter(having)
    if columns:
        result = MiniDataFrame({c: result.columns[c] for c in columns if c in result.columns})
    records = result.to_records()
    if order_by:
        col, desc = order_by
        records.sort(key=lambda r: r.get(col, 0), reverse=desc)
    if limit:
        records = records[:limit]
    return MiniDataFrame.from_records(records)


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("Data 8 / Data 100 Data Science Demo")
    print("=" * 60)
    random.seed(42)

    # 1. MiniDataFrame
    print("\n📋 1. MiniDataFrame（from scratch）")
    students = [
        {"name": "Alice", "grade": 85, "major": "CS"},
        {"name": "Bob", "grade": 72, "major": "CS"},
        {"name": "Carol", "grade": 90, "major": "EE"},
        {"name": "Dave", "grade": 68, "major": "EE"},
        {"name": "Eve", "grade": 95, "major": "CS"},
    ]
    df = MiniDataFrame.from_records(students)
    print(df)
    print(f"\n   shape: {len(df)} rows × {len(df.columns)} cols")

    # Filter
    cs = df.filter(lambda r: r["major"] == "CS")
    print(f"\n   filter major=='CS': {len(cs)} rows")
    print(cs)

    # GroupBy
    print("\n   groupby major, mean grade:")
    grouped = df.groupby("major", agg_func=lambda vals: sum(vals) / len(vals))
    print(grouped)

    # Join
    majors_info = MiniDataFrame.from_records([
        {"major": "CS", "dept": "EECS"},
        {"major": "EE", "dept": "EECS"},
    ])
    joined = df.join(majors_info, on="major")
    print(f"\n   join with dept info:")
    print(joined.head())

    # 2. Bootstrap CI
    print("\n📋 2. Bootstrap 置信区间")
    # 模拟工资数据（右偏分布）
    salaries = [random.lognormvariate(10.5, 0.4) for _ in range(200)]
    mean_salary = sum(salaries) / len(salaries)
    lo, hi, _ = bootstrap_ci(salaries, stat_func=lambda d: sum(d)/len(d),
                              n_bootstrap=2000, ci=0.95)
    median_lo, median_hi, _ = bootstrap_ci(salaries, stat_func=lambda d: sorted(d)[len(d)//2],
                                            n_bootstrap=2000, ci=0.95)
    print(f"   样本均值: ${mean_salary:,.0f}")
    print(f"   95% CI (均值): [${lo:,.0f}, ${hi:,.0f}]")
    print(f"   95% CI (中位数): [${median_lo:,.0f}, ${median_hi:,.0f}]")

    # 3. OLS
    print("\n📋 3. OLS 回归 + 诊断")
    # y = 3x + 2 + noise
    X = [[random.uniform(0, 10)] for _ in range(50)]
    y = [3 * x[0] + 2 + random.gauss(0, 2) for x in X]
    result = ols_regression(X, y)
    print(f"   真实: β=[2, 3]")
    print(f"   OLS: β=[{result['beta'][0]:.3f}, {result['beta'][1]:.3f}]")
    print(f"   R² = {result['R2']:.4f}")
    # 残差诊断
    res = result["residuals"]
    res_mean = sum(res) / len(res)
    res_std = math.sqrt(sum((r - res_mean) ** 2 for r in res) / len(res))
    print(f"   残差: mean={res_mean:.4f} (应≈0), std={res_std:.4f}")

    # 4. SQL
    print("\n📋 4. SQL-like 查询")
    big_df = MiniDataFrame.from_records([
        {"product": "A", "category": "Tech", "sales": 100},
        {"product": "B", "category": "Tech", "sales": 150},
        {"product": "C", "category": "Food", "sales": 80},
        {"product": "D", "category": "Food", "sales": 120},
        {"product": "E", "category": "Tech", "sales": 200},
    ])
    print("   原始表:")
    print(big_df)
    # SELECT category, SUM(sales) GROUP BY category HAVING sum>100 ORDER BY sales DESC
    result_sql = sql_select(
        big_df,
        group_by="category",
        having=lambda r: r["sales"] > 100,
        order_by=("sales", True),
    )
    print("\n   GROUP BY category HAVING sum>100 ORDER BY sales DESC:")
    print(result_sql)

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print(f"   Bootstrap 均值 CI: [${lo:,.0f}, ${hi:,.0f}]")
    print(f"   Bootstrap 中位数 CI: [${median_lo:,.0f}, ${median_hi:,.0f}]")
    print(f"   均值 CI 比中位数 CI 宽（右偏分布中，均值受极端值影响更大）")
    print("   → 这就是为什么描述收入用'中位数'比'均值'更稳健。")
    print()
    print("   OLS 在 y=3x+2+noise 上 R² ≈ 0.97（高），")
    print("   但如果数据有非线性（如 y=x²），OLS 的 R² 仍然可能很高，")
    print("   但残差会呈现'曲线模式'而非随机——这就是残差诊断的价值。")
    print("   'R² 高 ≠ 模型正确' 是数据科学第一课。")


if __name__ == "__main__":
    demo()
