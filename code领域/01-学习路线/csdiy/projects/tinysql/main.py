#!/usr/bin/env python3
"""
tinysql — 参照 PostgreSQL parser 的 SQL 解析+执行引擎

参照：PostgreSQL parser + SQLite VDBE + DuckDB
csdiy 对应：db 全部 + tinycompiler(Lexer/Parser) + tinysearch

核心：SQL → AST → 执行 → 结果
"""
import re
from dataclasses import dataclass

# ━━━━ AST ━━━━
@dataclass
class Column: name: str; type: str = "TEXT"
@dataclass
class CreateTable: name: str; columns: list
@dataclass
class Insert: table: str; columns: list; values: list
@dataclass
class Select: table: str; columns: list; where: str = None
@dataclass
class Delete: table: str; where: str = None
@dataclass
class Update: table: str; sets: dict; where: str = None

class SQLParser:
    """SQL 解析器（参照 PostgreSQL parser + tinycompiler 的递归下降）"""
    def parse(self, sql):
        sql = sql.strip().rstrip(";")
        upper = sql.upper()
        if upper.startswith("CREATE TABLE"):
            return self._parse_create(sql)
        elif upper.startswith("INSERT"):
            return self._parse_insert(sql)
        elif upper.startswith("SELECT"):
            return self._parse_select(sql)
        elif upper.startswith("DELETE"):
            return self._parse_delete(sql)
        elif upper.startswith("UPDATE"):
            return self._parse_update(sql)
        raise ValueError(f"Unsupported SQL: {sql[:30]}")

    def _parse_create(self, sql):
        m = re.match(r'CREATE TABLE\s+(\w+)\s*\((.+)\)', sql, re.I)
        if not m: raise ValueError("Invalid CREATE TABLE")
        name = m.group(1)
        cols = []
        for col_def in m.group(2).split(","):
            parts = col_def.strip().split()
            cols.append(Column(parts[0], parts[1] if len(parts) > 1 else "TEXT"))
        return CreateTable(name, cols)

    def _parse_insert(self, sql):
        m = re.match(r'INSERT INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)', sql, re.I)
        if not m: raise ValueError("Invalid INSERT")
        table = m.group(1)
        columns = [c.strip() for c in m.group(2).split(",")]
        values = [self._parse_value(v.strip()) for v in m.group(3).split(",")]
        return Insert(table, columns, values)

    def _parse_select(self, sql):
        m = re.match(r'SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?$', sql, re.I)
        if not m: raise ValueError("Invalid SELECT")
        columns = [c.strip() for c in m.group(1).split(",")]
        table = m.group(2)
        where = m.group(3)
        return Select(table, columns, where)

    def _parse_delete(self, sql):
        m = re.match(r'DELETE FROM\s+(\w+)(?:\s+WHERE\s+(.+))?$', sql, re.I)
        if not m: raise ValueError("Invalid DELETE")
        return Delete(m.group(1), m.group(2))

    def _parse_update(self, sql):
        m = re.match(r'UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?$', sql, re.I)
        if not m: raise ValueError("Invalid UPDATE")
        sets = {}
        for s in m.group(2).split(","):
            k, v = s.split("=", 1)
            sets[k.strip()] = self._parse_value(v.strip())
        return Update(m.group(1), sets, m.group(3))

    def _parse_value(self, v):
        v = v.strip().strip("'\"")
        return v if v.isdigit() else v

class TinySQL:
    """SQL 执行引擎（参照 SQLite VDBE + PostgreSQL executor）"""
    def __init__(self):
        self.tables: dict[str, dict] = {}  # table → {columns, rows}
        self.parser = SQLParser()

    def execute(self, sql: str):
        ast = self.parser.parse(sql)
        if isinstance(ast, CreateTable):
            return self._exec_create(ast)
        elif isinstance(ast, Insert):
            return self._exec_insert(ast)
        elif isinstance(ast, Select):
            return self._exec_select(ast)
        elif isinstance(ast, Delete):
            return self._exec_delete(ast)
        elif isinstance(ast, Update):
            return self._exec_update(ast)

    def _exec_create(self, ast):
        self.tables[ast.name] = {"columns": [c.name for c in ast.columns], "types": ast.columns, "rows": []}
        return f"CREATE TABLE {ast.name} ({len(ast.columns)} columns)"

    def _exec_insert(self, ast):
        table = self.tables.get(ast.table)
        if not table: raise ValueError(f"Table {ast.table} not found")
        row = dict(zip(ast.columns, ast.values))
        table["rows"].append(row)
        return f"INSERT 1 row into {ast.table}"

    def _exec_select(self, ast):
        table = self.tables.get(ast.table)
        if not table: raise ValueError(f"Table {ast.table} not found")
        rows = table["rows"]
        # WHERE 过滤（简化版）
        if ast.where:
            col, _, val = ast.where.partition("=")
            col, val = col.strip(), val.strip().strip("'\"")
            rows = [r for r in rows if str(r.get(col)) == val]
        # 列选择
        if ast.columns == ["*"]:
            cols = table["columns"]
        else:
            cols = ast.columns
        results = [[r.get(c) for c in cols] for r in rows]
        return {"columns": cols, "rows": results}

    def _exec_delete(self, ast):
        table = self.tables.get(ast.table)
        if not table: return f"Table {ast.table} not found"
        if ast.where:
            col, _, val = ast.where.partition("=")
            col, val = col.strip(), val.strip().strip("'\"")
            before = len(table["rows"])
            table["rows"] = [r for r in table["rows"] if str(r.get(col)) != val]
            deleted = before - len(table["rows"])
        else:
            deleted = len(table["rows"])
            table["rows"] = []
        return f"DELETE {deleted} rows from {ast.table}"

    def _exec_update(self, ast):
        table = self.tables.get(ast.table)
        if not table: return f"Table {ast.table} not found"
        count = 0
        for row in table["rows"]:
            if ast.where:
                col, _, val = ast.where.partition("=")
                if str(row.get(col.strip())) != val.strip().strip("'\""): continue
            row.update(ast.sets)
            count += 1
        return f"UPDATE {count} rows in {ast.table}"

def main():
    print("tinysql — SQL 解析+执行引擎（参照 PostgreSQL）\n")
    db = TinySQL()

    print(db.execute("CREATE TABLE users (id INT, name TEXT, age INT)"))
    print(db.execute("INSERT INTO users (id, name, age) VALUES (1, Alice, 30)"))
    print(db.execute("INSERT INTO users (id, name, age) VALUES (2, Bob, 25)"))
    print(db.execute("INSERT INTO users (id, name, age) VALUES (3, Carol, 35)"))

    print("\nSELECT * FROM users:")
    result = db.execute("SELECT * FROM users")
    print(f"  {'  '.join(result['columns'])}")
    for row in result["rows"]:
        print(f"  {row}")

    print("\nSELECT name, age FROM users WHERE id = 2:")
    result = db.execute("SELECT name, age FROM users WHERE id = 2")
    for row in result["rows"]:
        print(f"  {row}")

    print("\nUPDATE users SET age = 26 WHERE id = 2")
    print("  " + db.execute("UPDATE users SET age = 26 WHERE id = 2"))

    print("\nDELETE FROM users WHERE id = 3")
    print("  " + db.execute("DELETE FROM users WHERE id = 3"))

    print("\nSELECT * FROM users:")
    result = db.execute("SELECT * FROM users")
    for row in result["rows"]:
        print(f"  {row}")

if __name__ == "__main__": main()
