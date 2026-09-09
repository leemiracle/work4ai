# Project 10 — Compiler I：Tokenizer + Parser（语法分析）

> **一句话目标**：实现 Jack 编译器的**前端**——把 `.jack` 源码拆成 Token 流，再构建**语法树（XML）**。
> 不生成代码，**只做分析**。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch10.1-10.4**（Compiler I）|
| 🎥 Coursera | [Unit 10.1-10.7](https://www.coursera.org/learn/nand2tetris2) |
| 🛠 工具 | Python 3 + TextComparer（验证 XML）|
| ⏱ 预计工时 | 10–20 小时 |

---

## 1. 编译器的 3 个经典阶段

```
.jack 源码
    │
    ▼
[Tokenizer 词法分析]   把字符流切分成 Token 流
    │
    ▼ Token 流
[Parser 语法分析]     根据 Jack 文法构建语法树（P10）
    │
    ▼ AST（抽象语法树）
[CodeGen 代码生成]    把 AST 翻译为 VM（P11）
    │
    ▼ .vm
[VM 翻译器]           P07-P08 你已经实现
    │
    ▼ .asm
[汇编器]              P06 你已经实现
```

P10 做 Tokenizer + Parser。

---

## 2. Jack Tokenizer

### 2.1 Jack 的 5 种 Token

| 类型 | 例子 |
|------|------|
| `KEYWORD` | class, method, function, constructor, int, boolean, char, void, var, field, static, let, do, if, else, while, return, true, false, null, this |
| `SYMBOL` | { } ( ) [ ] . , ; + - * / & \| < > = ~ |
| `IDENTIFIER` | 字母/数字/下划线，不以数字开头 |
| `INT_CONST` | 数字字面量（0–32767）|
| `STRING_CONST` | `"..."` 之间的字符 |

### 2.2 Tokenizer 的输出（XML 形式）

输入 `Main.jack`：
```jack
class Main {
    function void main() {
        var int x;
        let x = 5;
        return;
    }
}
```

输出 `MainT.xml`：
```xml
<tokens>
  <keyword> class </keyword>
  <identifier> Main </identifier>
  <symbol> { </symbol>
  <keyword> function </keyword>
  <keyword> void </keyword>
  <identifier> main </identifier>
  <symbol> ( </symbol>
  <symbol> ) </symbol>
  <symbol> { </symbol>
  <keyword> var </keyword>
  <keyword> int </keyword>
  <identifier> x </identifier>
  <symbol> ; </symbol>
  <keyword> let </keyword>
  <identifier> x </identifier>
  <symbol> = </symbol>
  <integerConstant> 5 </integerConstant>
  <symbol> ; </symbol>
  <keyword> return </keyword>
  <symbol> ; </symbol>
  <symbol> } </symbol>
  <symbol> } </symbol>
</tokens>
```

### 2.3 符号转义（XML 特殊字符）

| Jack 符号 | XML 表示 |
|-----------|----------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `&` | `&amp;` |

---

## 3. Jack Parser

### 3.1 Jack 文法（递归下降）

```
class        ::= 'class' className '{' classVarDec* subroutineDec* '}'
classVarDec  ::= ('static'|'field') type varName (',' varName)* ';'
subroutineDec ::= ('constructor'|'function'|'method')
                  ('void'|type) subroutineName '(' parameterList ')'
                  subroutineBody
parameterList ::= ((type varName) (',' type varName)*)?
subroutineBody ::= '{' varDec* statements '}'
varDec       ::= 'var' type varName (',' varName)* ';'

type         ::= 'int'|'char'|'boolean'|className

statements   ::= statement*
statement    ::= letStatement | ifStatement | whileStatement
                | doStatement | returnStatement

letStatement ::= 'let' varName ('[' expression ']')? '=' expression ';'
ifStatement  ::= 'if' '(' expression ')' '{' statements '}'
                ('else' '{' statements '}')?
whileStatement ::= 'while' '(' expression ')' '{' statements '}'
doStatement  ::= 'do' subroutineCall ';'
returnStatement ::= 'return' expression? ';'

expression   ::= term (op term)*
term         ::= integerConstant | stringConstant | keywordConstant
                | varName | varName '[' expression ']'
                | subroutineCall
                | '(' expression ')'
                | unaryOp term
subroutineCall ::= subroutineName '(' expressionList ')'
                | (className|varName) '.' subroutineName '(' expressionList ')'
expressionList ::= (expression (',' expression)*)?
op            ::= '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
unaryOp       ::= '-'|'~'
keywordConstant::= 'true'|'false'|'null'|'this'
```

### 3.2 Parser 的输出（嵌套 XML）

输入（同上），Parser 输出：
```xml
<class>
  <keyword> class </keyword>
  <identifier> Main </identifier>
  <symbol> { </symbol>
  <subroutineDec>
    <keyword> function </keyword>
    <keyword> void </keyword>
    <identifier> main </identifier>
    <symbol> ( </symbol>
    <parameterList> </parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <varDec>
        <keyword> var </keyword>
        <keyword> int </keyword>
        <identifier> x </identifier>
        <symbol> ; </symbol>
      </varDec>
      <statements>
        <letStatement>
          <keyword> let </keyword>
          <identifier> x </identifier>
          <symbol> = </symbol>
          <expression>
            <term>
              <integerConstant> 5 </integerConstant>
            </term>
          </expression>
          <symbol> ; </symbol>
        </letStatement>
        <returnStatement>
          <keyword> return </keyword>
          <symbol> ; </symbol>
        </returnStatement>
      </statements>
      <symbol> } </symbol>
    </subroutineBody>
  </subroutineDec>
  <symbol> } </symbol>
</class>
```

---

## 4. Python 实现骨架

```python
#!/usr/bin/env python3
"""Jack Compiler 前端：Tokenizer + Parser"""

from dataclasses import dataclass
from typing import Optional

# ============= Tokenizer =============

KEYWORDS = {'class','constructor','function','method','field','static',
            'var','int','char','boolean','void','true','false','null',
            'this','let','do','if','else','while','return'}

SYMBOLS = set('{}()[].,;+-*/&|<>=~')

@dataclass
class Token:
    type: str       # KEYWORD / SYMBOL / IDENTIFIER / INT_CONST / STRING_CONST
    value: str

class Tokenizer:
    def __init__(self, source: str):
        self.source = self._strip_comments(source)
        self.pos = 0
        self.tokens: list[Token] = []
    
    def _strip_comments(self, src: str) -> str:
        # TODO: 移除 // 单行注释、/* */ 块注释、API 文档注释
        # 注意：不要移除字符串里的 //
        ...
    
    def tokenize(self) -> list[Token]:
        while self.pos < len(self.source):
            c = self.source[self.pos]
            if c.isspace():
                self.pos += 1
            elif c in SYMBOLS:
                self.tokens.append(Token('SYMBOL', c))
                self.pos += 1
            elif c == '"':
                self.tokens.append(self._read_string())
            elif c.isdigit():
                self.tokens.append(self._read_int())
            elif c.isalpha() or c == '_':
                self.tokens.append(self._read_identifier())
            else:
                raise ValueError(f'非法字符：{c}')
        return self.tokens
    
    def _read_string(self) -> Token:
        end = self.source.index('"', self.pos + 1)
        s = self.source[self.pos + 1:end]
        self.pos = end + 1
        return Token('STRING_CONST', s)
    
    def _read_int(self) -> Token:
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.pos += 1
        return Token('INT_CONST', self.source[start:self.pos])
    
    def _read_identifier(self) -> Token:
        start = self.pos
        while self.pos < len(self.source) and (
            self.source[self.pos].isalnum() or self.source[self.pos] == '_'
        ):
            self.pos += 1
        word = self.source[start:self.pos]
        if word in KEYWORDS:
            return Token('KEYWORD', word)
        return Token('IDENTIFIER', word)


# ============= Parser =============

class CompilationEngine:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.output = []
    
    def current(self) -> Token:
        return self.tokens[self.pos]
    
    def advance(self):
        self.pos += 1
    
    def eat(self, expected_type: str = None, expected_value: str = None):
        tok = self.current()
        if expected_type and tok.type != expected_type:
            raise SyntaxError(f'期望 {expected_type}，实际 {tok}')
        if expected_value and tok.value != expected_value:
            raise SyntaxError(f'期望 {expected_value}，实际 {tok.value}')
        self.emit(tok)
        self.advance()
    
    def emit(self, tok: Token):
        xml_tag = {
            'KEYWORD': 'keyword',
            'SYMBOL': 'symbol',
            'IDENTIFIER': 'identifier',
            'INT_CONST': 'integerConstant',
            'STRING_CONST': 'stringConstant',
        }[tok.type]
        value = self._escape(tok.value)
        self.output.append(f'<{xml_tag}> {value} </{xml_tag}>')
    
    @staticmethod
    def _escape(s: str) -> str:
        return (s.replace('&', '&amp;')
                 .replace('<', '&lt;')
                 .replace('>', '&gt;')
                 .replace('"', '&quot;'))
    
    def compile_class(self):
        self.output.append('<class>')
        self.eat(expected_value='class')
        self.eat('IDENTIFIER')        # className
        self.eat(expected_value='{')
        while self.current().value in ('static', 'field'):
            self.compile_class_var_dec()
        while self.current().value in ('constructor', 'function', 'method'):
            self.compile_subroutine()
        self.eat(expected_value='}')
        self.output.append('</class>')
    
    def compile_class_var_dec(self):
        # TODO
        ...
    
    def compile_subroutine(self):
        # TODO
        ...
    
    def compile_statements(self):
        # TODO: 分派 let/if/while/do/return
        ...
    
    def compile_expression(self):
        # TODO: term (op term)*
        ...


# ============= 主入口 =============

def compile_file(input_path: str):
    source = open(input_path).read()
    tokens = Tokenizer(source).tokenize()
    engine = CompilationEngine(tokens)
    engine.compile_class()
    print('\n'.join(engine.output))


if __name__ == '__main__':
    import sys
    compile_file(sys.argv[1])
```

---

## 5. 测试

nand2tetris 提供 `Square` 和 `ExpressionlessSquare` 测试集：

```bash
# 期望输出：Square.xml, SquareT.xml（与官方对比）
python3 src/JackCompiler.py tests/Square/Main.jack
diff tests/Square/Main.xml tests/Square/Main_expected.xml
```

---

## 6. 常见坑

### 坑 1：注释里的字符串、字符串里的注释符

```jack
let s = "// not a comment";   // 字符串里
let url = "http://...";       // 字符串里有 //
```

→ 必须先识别字符串再处理注释。

### 坑 2：`/** ... */` API 注释

Jack 支持 `/** */` 的文档注释，与普通 `/* */` 同样要移除。

### 坑 3：XML 的"非终结符"节点

Parser 输出比 Tokenizer 多了**非终结符节点**：
- `<class>`, `<subroutineDec>`, `<letStatement>`, `<expression>`, `<term>` 等
- 这些不在 Tokenizer 输出里

### 坑 4：表达式优先级

Jack 文法允许 `expression ::= term (op term)*`，**不显式处理优先级**——
所有运算符同级（左结合），由 VM 翻译器在编译时决定。
（这是教学简化，真实语言要处理优先级。）

### 坑 5：unaryOp

```jack
let x = -5;        // - 是 unaryOp
let y = a - b;     // - 是 binaryOp
```

Parser 必须区分这两种 `-`。

---

## 7. 与本项目其他模块的连接

### 7.1 与 [`View_01_Compiler`](../../View_01_Compiler/) 的连接

学完 P10 后看 GCC 的 `-fdump-tree-original` 或 LLVM 的 `clang -emit-ast`，
你会发现**工业编译器的 AST 比 Jack 的 XML 复杂 100 倍**——但思路完全一样。

### 7.2 与 [`Expert_11_Compiler_Research`](../../Expert_11_Compiler_Research/) 的连接

GCC/LLVM 的 IR 是 **SSA 形式**（每个变量只赋值一次），
Jack VM 是**栈式 IR**——两种风格各有优劣：
- 栈式：编译器简单，VM 简单
- SSA：易优化，但实现复杂

### 7.3 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

P10 让你**站在 L4（ABI）的上面看 L5（应用）**——
编译器是连接高级语言抽象和机器现实的核心工具。

---

## 8. 扩展挑战

1. **加优先级**：让 `1 + 2 * 3` 得到 7 而不是 9（标准运算符优先级）
2. **生成 AST 而非 XML**：返回真正的 Python 对象树
3. **加类型检查**：检测 `let x = "hello"; x + 1;` 类型错误
4. **加宏**：支持 `#define MAX(a, b) ((a) > (b) ? (a) : (b))`
5. **加泛型**：参考 Java Generics（难度跳跃）

---

## 9. 检查清单

- [ ] 理解 5 种 Token 类型
- [ ] 能默写 Jack 文法（class → subroutineDec → statements → expression → term）
- [ ] 理解递归下降 Parser 的原理
- [ ] 完整实现 Tokenizer + Parser
- [ ] 跑通官方 Square 测试

---

## 📌 下一步

完成 P10 后，进 [`Project_11_Compiler_II/`](../Project_11_Compiler_II/)。
你将在 P10 的 AST 上添加**代码生成器**——
**把 AST 翻译为 VM bytecode**，最终能跑你 P09 写的 Jack App！
