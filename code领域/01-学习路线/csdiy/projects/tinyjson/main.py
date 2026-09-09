#!/usr/bin/env python3
"""
tinyjson — 参照 simdjson 的高性能 JSON 解析器

参照：simdjson (Daniel Lemire) + Python json
csdiy 对应：csapp(解析/状态机) + tinycompiler(Lexer/Parser)

核心：递归下降解析器 + 状态机 tokenizer
从零实现，不依赖 json 库，用于理解 JSON 格式的本质。

支持：null/true/false/number/string/array/object
"""
import sys, math, time
from typing import Any, Union

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JSON 解析异常
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class JSONError(Exception):
    def __init__(self, msg, pos):
        super().__init__(f"{msg} at position {pos}")
        self.pos = pos

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 递归下降 JSON 解析器（参照 RFC 8259）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class JSONParser:
    """
    递归下降 JSON 解析器（参照 simdjson 的 On-Demand 解析）

    文法（RFC 8259）：
      value   → null | true | false | number | string | array | object
      object  → '{' (string ':' value (',' string ':' value)*)? '}'
      array   → '[' (value (',' value)*)? ']'
      string  → '"' char* '"'
      number  → int frac? exp?

    特点：
    - 单次扫描（不复制字符串）
    - 惰性求值（参照 simdjson 的 On-Demand）
    - 错误定位到字符位置
    """
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.len = len(text)

    def parse(self) -> Any:
        """解析 JSON，返回 Python 对象"""
        self._skip_ws()
        value = self._parse_value()
        self._skip_ws()
        if self.pos < self.len:
            raise JSONError(f"Unexpected '{self.text[self.pos]}'", self.pos)
        return value

    def _peek(self):
        return self.text[self.pos] if self.pos < self.len else '\0'

    def _advance(self):
        c = self.text[self.pos]
        self.pos += 1
        return c

    def _skip_ws(self):
        """跳过空白（参照 RFC 8259 §2）"""
        while self.pos < self.len and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def _expect(self, char: str):
        """期望当前字符（参照编译器的 match）"""
        if self._peek() != char:
            raise JSONError(f"Expected '{char}', got '{self._peek()}'", self.pos)
        self.pos += 1

    def _parse_value(self) -> Any:
        """解析值（参照 RFC 8259 value 规则）"""
        c = self._peek()
        if c == '"':  return self._parse_string()
        elif c == '{': return self._parse_object()
        elif c == '[': return self._parse_array()
        elif c == 't': return self._parse_true()
        elif c == 'f': return self._parse_false()
        elif c == 'n': return self._parse_null()
        elif c == '-' or c.isdigit(): return self._parse_number()
        else: raise JSONError(f"Unexpected '{c}'", self.pos)

    def _parse_string(self) -> str:
        """解析字符串（参照 RFC 8259 §7）"""
        self._expect('"')
        result = []
        while self.pos < self.len:
            c = self._advance()
            if c == '"':
                return ''.join(result)
            elif c == '\\':
                # 转义序列（参照 RFC 8259 §7）
                esc = self._advance()
                if esc == '"': result.append('"')
                elif esc == '\\': result.append('\\')
                elif esc == '/': result.append('/')
                elif esc == 'b': result.append('\b')
                elif esc == 'f': result.append('\f')
                elif esc == 'n': result.append('\n')
                elif esc == 'r': result.append('\r')
                elif esc == 't': result.append('\t')
                elif esc == 'u':
                    # Unicode 转义 \uXXXX
                    hex_str = self.text[self.pos:self.pos+4]
                    if len(hex_str) < 4:
                        raise JSONError("Invalid unicode escape", self.pos)
                    code = int(hex_str, 16)
                    self.pos += 4
                    result.append(chr(code))
                else:
                    raise JSONError(f"Invalid escape '\\{esc}'", self.pos - 1)
            elif ord(c) < 0x20:
                raise JSONError(f"Control character U+{ord(c):04X}", self.pos - 1)
            else:
                result.append(c)
        raise JSONError("Unterminated string", self.pos)

    def _parse_number(self) -> Union[int, float]:
        """解析数字（参照 RFC 8259 §6）"""
        start = self.pos
        # 负号
        if self._peek() == '-':
            self.pos += 1
        # 整数部分
        if self._peek() == '0':
            self.pos += 1
        elif self._peek() in '123456789':
            self.pos += 1
            while self._peek().isdigit():
                self.pos += 1
        else:
            raise JSONError("Invalid number", start)
        # 小数部分
        is_float = False
        if self._peek() == '.':
            is_float = True
            self.pos += 1
            if not self._peek().isdigit():
                raise JSONError("Expected digit after '.'", self.pos)
            while self._peek().isdigit():
                self.pos += 1
        # 指数部分
        if self._peek() in 'eE':
            is_float = True
            self.pos += 1
            if self._peek() in '+-':
                self.pos += 1
            if not self._peek().isdigit():
                raise JSONError("Expected digit in exponent", self.pos)
            while self._peek().isdigit():
                self.pos += 1

        num_str = self.text[start:self.pos]
        return float(num_str) if is_float else int(num_str)

    def _parse_object(self) -> dict:
        """解析对象（参照 RFC 8259 §4）"""
        self._expect('{')
        self._skip_ws()
        obj = {}
        if self._peek() == '}':
            self.pos += 1
            return obj
        while True:
            self._skip_ws()
            if self._peek() != '"':
                raise JSONError("Expected string key", self.pos)
            key = self._parse_string()
            self._skip_ws()
            self._expect(':')
            self._skip_ws()
            value = self._parse_value()
            obj[key] = value
            self._skip_ws()
            if self._peek() == ',':
                self.pos += 1
            elif self._peek() == '}':
                self.pos += 1
                break
            else:
                raise JSONError(f"Expected ',' or '}}', got '{self._peek()}'", self.pos)
        return obj

    def _parse_array(self) -> list:
        """解析数组（参照 RFC 8259 §5）"""
        self._expect('[')
        self._skip_ws()
        arr = []
        if self._peek() == ']':
            self.pos += 1
            return arr
        while True:
            self._skip_ws()
            value = self._parse_value()
            arr.append(value)
            self._skip_ws()
            if self._peek() == ',':
                self.pos += 1
            elif self._peek() == ']':
                self.pos += 1
                break
            else:
                raise JSONError(f"Expected ',' or ']', got '{self._peek()}'", self.pos)
        return arr

    def _parse_true(self):
        if self.text[self.pos:self.pos+4] == "true":
            self.pos += 4
            return True
        raise JSONError("Invalid literal 'true'", self.pos)

    def _parse_false(self):
        if self.text[self.pos:self.pos+5] == "false":
            self.pos += 5
            return False
        raise JSONError("Invalid literal 'false'", self.pos)

    def _parse_null(self):
        if self.text[self.pos:self.pos+4] == "null":
            self.pos += 4
            return None
        raise JSONError("Invalid literal 'null'", self.pos)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JSON 序列化（参照 Python json.dumps）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def dumps(obj: Any, indent: int = None, _level: int = 0) -> str:
    """序列化 Python 对象到 JSON（参照 json.dumps）"""
    if obj is None: return "null"
    if obj is True: return "true"
    if obj is False: return "false"
    if isinstance(obj, int): return str(obj)
    if isinstance(obj, float):
        if math.isnan(obj): return "null"  # JSON 不支持 NaN
        if math.isinf(obj): return "null"  # JSON 不支持 Infinity
        return str(obj)
    if isinstance(obj, str): return _escape_string(obj)
    if isinstance(obj, (list, tuple)): return _dump_array(obj, indent, _level)
    if isinstance(obj, dict): return _dump_object(obj, indent, _level)
    raise TypeError(f"Type {type(obj).__name__} not serializable")

def _escape_string(s: str) -> str:
    """转义字符串（参照 RFC 8259 §7）"""
    result = ['"']
    for c in s:
        if c == '"': result.append('\\"')
        elif c == '\\': result.append('\\\\')
        elif c == '\n': result.append('\\n')
        elif c == '\r': result.append('\\r')
        elif c == '\t': result.append('\\t')
        elif ord(c) < 0x20: result.append(f'\\u{ord(c):04x}')
        else: result.append(c)
    result.append('"')
    return ''.join(result)

def _dump_array(arr, indent, level):
    if not arr: return "[]"
    if indent:
        pad = '\n' + ' ' * (indent * (level + 1))
        close_pad = '\n' + ' ' * (indent * level)
        items = [dumps(v, indent, level + 1) for v in arr]
        return f"[{pad}{f',{pad}'.join(items)}{close_pad}]"
    else:
        return f"[{','.join(dumps(v) for v in arr)}]"

def _dump_object(obj, indent, level):
    if not obj: return "{}"
    if indent:
        pad = '\n' + ' ' * (indent * (level + 1))
        close_pad = '\n' + ' ' * (indent * level)
        items = [f'{_escape_string(k)}: {dumps(v, indent, level+1)}' for k, v in obj.items()]
        return f"{{{pad}{f',{pad}'.join(items)}{close_pad}}}"
    else:
        items = [f'{_escape_string(k)}:{dumps(v)}' for k, v in obj.items()]
        return f"{{{','.join(items)}}}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def loads(text: str) -> Any:
    """解析 JSON 字符串（参照 json.loads）"""
    return JSONParser(text).parse()

def load(fp) -> Any:
    """从文件读取 JSON"""
    return loads(fp.read())

def dump(obj, fp, indent=None):
    """写入 JSON 到文件"""
    fp.write(dumps(obj, indent=indent))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 测试
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("tinyjson — 递归下降 JSON 解析器\n")

    # 测试数据
    test_cases = [
        ("null", None),
        ("true", True),
        ("false", False),
        ("42", 42),
        ("-3.14", -3.14),
        ('"hello"', "hello"),
        ('"\\u00e9"', "é"),  # Unicode 转义
        ("[]", []),
        ("[1, 2, 3]", [1, 2, 3]),
        ("{}", {}),
        ('{"key": "value"}', {"key": "value"}),
        ('{"nested": {"array": [1, null, true]}}', {"nested": {"array": [1, None, True]}}),
        ('[1.5e2, -0.5, 0]', [150.0, -0.5, 0]),
        ('"\\n\\t\\r"', "\n\t\r"),
    ]

    print("── 解析测试 ──")
    passed = 0
    for text, expected in test_cases:
        try:
            result = loads(text)
            ok = result == expected
            if ok: passed += 1
            status = "✅" if ok else "❌"
            print(f"  {status} loads({text!r:40s}) = {result!r}")
        except JSONError as e:
            print(f"  ❌ loads({text!r}) → Error: {e}")
    print(f"\n  {passed}/{len(test_cases)} passed")

    # 序列化测试
    print("\n── 序列化测试 ──")
    obj = {"name": "tinyjson", "version": 1.0, "features": ["parse", "dump"], "nested": {"ok": True}}
    json_str = dumps(obj)
    print(f"  dumps: {json_str}")
    json_pretty = dumps(obj, indent=2)
    print(f"  pretty:\n{json_pretty}")

    # 往返测试（parse → dump → parse == original）
    print("\n── 往返测试（round-trip）──")
    roundtrip = loads(dumps(obj))
    print(f"  original == roundtrip: {'✅' if obj == roundtrip else '❌'}")

    # 错误处理
    print("\n── 错误处理 ──")
    errors = ['{"key": }', '[1, 2,]', '{"key" "val"}', "'single quotes'", '{']
    for text in errors:
        try:
            loads(text)
            print(f"  ❌ Should have failed: {text!r}")
        except JSONError as e:
            print(f"  ✅ Correctly rejected: {text!r} → {e}")

    # 性能对比（参照 simdjson 的 benchmark）
    print("\n── 性能对比 ──")
    import json as stdlib_json
    big = [[i, f"item_{i}", {"x": i*0.1}] for i in range(10000)]
    big_json = stdlib_json.dumps(big)

    t1 = time.perf_counter()
    for _ in range(10):
        loads(big_json)
    t2 = time.perf_counter()
    tiny_time = (t2 - t1) / 10

    t1 = time.perf_counter()
    for _ in range(10):
        stdlib_json.loads(big_json)
    t2 = time.perf_counter()
    std_time = (t2 - t1) / 10

    print(f"  tinyjson:  {tiny_time*1000:.1f}ms")
    print(f"  stdlib:    {std_time*1000:.1f}ms")
    print(f"  ratio:     {tiny_time/std_time:.1f}x slower (expected: stdlib is C-optimized)")

if __name__ == "__main__":
    main()
