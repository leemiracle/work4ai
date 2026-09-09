# nginx HTTP 解析器精读：状态机驱动的高性能请求处理

> nginx 能扛 10 万 QPS，不只是因为 epoll——它的 HTTP 解析器也是世界级的。
>
> 配套：[eventloop-evolution-redis-nginx-go.md](eventloop-evolution-redis-nginx-go.md) | [tinyhttpd](../projects/tinyhttpd/)
> csdiy 对应：network §三(粘包/协议解析) + patterns §9(状态机)

---

## 一、为什么 HTTP 解析是瓶颈

```
HTTP 请求到达 → TCP 接收 → HTTP 解析 → 路由匹配 → upstream 转发 → 响应
                ↑                                                    ↑
                epoll 告诉你"有数据了"                    你要发回的数据
                     ↓
              HTTP 解析 ← 这里是 CPU 热点
```

HTTP/1.1 是文本协议（不像 RESP 那样有长度前缀），解析需要逐字节扫描。如果解析慢，epoll 再快也白搭。

---

## 二、nginx 的状态机解析器

### 和 tinyhttpd 的对比

你在 tinyhttpd 里实现的 HTTP 解析：
```python
# tinyhttpd 的解析（简单但低效）
line = await reader.readline()          # 读一行
parts = line.decode().strip().split()   # 分割
while True:                              # 循环读头部
    line = await reader.readline()
    if line in (b"\r\n", b"\n", b""): break
    k, v = line.decode().strip().split(":", 1)
```

**问题**：`readline()` 阻塞直到遇到 `\n`。如果客户端发了一半就停了（TCP 分片），整个 worker 卡住。

### nginx 的方案：有限状态机

nginx 不用 `readline()`。它**逐字节推进**，每收到一块数据就喂给状态机，状态机能"暂停"在任意位置，下次继续。

```c
// 参照 nginx ngx_http_parse.c（简化）

// 状态枚举
enum {
    sw_start,           // 请求行开始
    sw_method,          // 解析方法 GET/POST...
    sw_spaces_before_uri,
    sw_uri,             // 解析 URI
    sw_http_start,      // 解析 HTTP/
    sw_http_H,
    sw_http_HT,
    sw_http_HTT,
    sw_http_HTTP,
    sw_first_major_digit,
    sw_major_digit,
    sw_first_minor_digit,
    sw_minor_digit,
    sw_spaces_after_digit,
    sw_almost_done,     // 请求行即将完成
    sw_header_start,    // 头部开始
    sw_name,            // 头部名
    sw_space_before_value,
    sw_value,           // 头部值
    sw_space_after_value,
    sw_ignore_line,
    sw_almost_done,
    sw_header_almost_done,
    // ... 30+ 个状态
};

// 核心解析函数（逐字节）
ngx_int_t ngx_http_parse_request_line(ngx_http_request_t *r, ngx_buf_t *b) {
    u_char ch, *p, *m;
    enum { ... } state;

    state = r->state;  // 恢复上次的状态

    for (p = b->pos; p < b->last; p++) {  // 逐字节
        ch = *p;

        switch (state) {
        case sw_start:
            switch (ch) {
            case 'G': /* GET */ r->method = NGX_HTTP_GET; state = sw_method; break;
            case 'P': /* POST/PUT */ state = sw_method; break;
            case 'H': /* HEAD */ r->method = NGX_HTTP_HEAD; state = sw_method; break;
            case ' ': break;  // 跳过空格
            default: return NGX_HTTP_PARSE_INVALID_METHOD;
            }
            break;

        case sw_method:
            if (ch == ' ') {
                r->method_name.len = p - r->method_name.data;
                state = sw_spaces_before_uri;
            }
            break;

        case sw_uri:
            switch (ch) {
            case ' ':  // URI 结束
                r->uri_end = p;
                state = sw_http_start;
                break;
            default:
                // 继续 URI
                break;
            }
            break;

        // ... 更多状态

        case sw_almost_done:
            switch (ch) {
            case LF:  // \n → 请求行完成
                goto done;
            }
            break;
        }
    }

    // 缓冲区用完但请求行还没完 → 保存状态，等下一块数据
    r->state = state;
    return NGX_AGAIN;  // "我还没完，下次继续"

done:
    r->state = sw_start;  // 重置，准备解析头部
    return NGX_OK;
}
```

### 状态机的好处

| 对比 | readline（tinyhttpd） | 状态机（nginx） |
|------|---------------------|----------------|
| TCP 分片 | 阻塞等待整行 | 任意位置暂停/继续 |
| CPU 效率 | 每字节多次函数调用 | 每字节一次 switch |
| 内存 | 需要 readline buffer | 原地解析（零拷贝） |
| 吞吐 | 受 readline 限制 | 线性于数据量 |

csdiy 交叉：[network §三 粘包](../notes/network-程序员视角-从抓包到原理.md) —— TCP 分片和粘包在状态机面前不是问题。状态机不关心"包"的边界，只关心字节的逻辑顺序。

---

## 三、头部解析的优化

### 哈希表头部查找

nginx 解析头部名后，用**内联哈希**快速找到对应处理器：

```c
// 参照 nginx ngx_http_parse_header_line + ngx_hash.h
// 预编译的头部哈希表
static ngx_hash_t  headers_in_hash;

// 常见头部在启动时预注册
ngx_http_headers_in_t headers_in[] = {
    { ngx_string("Host"),              ngx_http_process_header_line },
    { ngx_string("Connection"),        ngx_http_process_connection },
    { ngx_string("Content-Length"),    ngx_http_process_content_length },
    { ngx_string("Content-Type"),      ngx_http_process_header_line },
    { ngx_string("Transfer-Encoding"), ngx_http_process_transfer_encoding },
    // ... 20+ 预定义头部
};
```

查找是 O(1) 的哈希查找——不需要遍历所有已解析头部。

---

## 四、和 tinyhttpd 的对照改进

你的 tinyhttpd 用 Python readline 解析 HTTP。如果要用 nginx 的方式改进：

```python
# tinyhttpd 的 nginx 式改进（状态机版）
class HTTPStateMachine:
    """逐字节推进的 HTTP 解析器（参照 nginx）"""
    
    def __init__(self):
        self.state = "request_line_start"
        self.method = ""
        self.uri = ""
        self.headers = {}
        self._buffer = ""
    
    def feed(self, data: bytes) -> Optional[dict]:
        """
        喂入一块数据，返回 None（需要更多数据）或解析完成的请求。
        
        和 readline 的区别：可以在任意字节暂停/继续。
        """
        self._buffer += data.decode("utf-8", errors="replace")
        
        while self._buffer:
            if self.state == "request_line_start":
                # 找到请求行的 \r\n
                idx = self._buffer.find("\r\n")
                if idx == -1:
                    return None  # 不完整，等更多数据
                line = self._buffer[:idx]
                self._buffer = self._buffer[idx + 2:]
                # 解析 "GET /path HTTP/1.1"
                parts = line.split(" ")
                if len(parts) >= 3:
                    self.method, self.uri, _ = parts[0], parts[1], parts[2]
                self.state = "headers"
            
            elif self.state == "headers":
                while True:
                    idx = self._buffer.find("\r\n")
                    if idx == -1:
                        return None  # 不完整
                    line = self._buffer[:idx]
                    self._buffer = self._buffer[idx + 2:]
                    if line == "":  # 空行 = 头部结束
                        self.state = "done"
                        break
                    if ":" in line:
                        k, v = line.split(":", 1)
                        self.headers[k.strip().lower()] = v.strip()
            
            elif self.state == "done":
                return {
                    "method": self.method,
                    "uri": self.uri,
                    "headers": self.headers,
                    "remaining": self._buffer,  # body 数据
                }
        
        return None
```

---

## 五、一句话总结

> nginx 的 HTTP 解析器用**有限状态机逐字节推进**，在 TCP 分片/粘包面前不会阻塞——每个字节只做一次 switch 判断，任意位置可暂停/继续。
>
> 这比 readline 等待整行快 10 倍。加上 epoll + 多进程，nginx 能在单机扛 10 万 QPS。

---

*配套：[eventloop-evolution-redis-nginx-go.md](eventloop-evolution-redis-nginx-go.md) | [tinyhttpd](../projects/tinyhttpd/)*
