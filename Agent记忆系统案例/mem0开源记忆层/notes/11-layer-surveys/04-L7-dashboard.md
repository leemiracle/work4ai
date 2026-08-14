# Layer 7 — Server Dashboard 综述(C 综述)

> 对应 ONBOARDING.md §5 Layer 7 / 8 个 ONBOARDING 提到的文件(实际 30+ ) / `notes/` 全空 → 本综述 100% 覆盖
> 范围:`server/dashboard/` Next.js 独立子项目
> 上游 HEAD:`4debc58a`

---

## 0. TL;DR

1. **Dashboard 是 self-hosted Mem0 server 的可视化管理面板**——Next.js 15 + shadcn/ui + axios + JWT auth + Redux,部署在 `:3000`,跟 FastAPI server(`:8888`)是两个独立服务,通过 `NEXT_PUBLIC_API_URL` 通信。
2. **3 件核心事**:认证(login/register/refresh + JWT)、setup 向导(5 步引导配 admin/provider/api-key)、5 个 dashboard 页(api-keys/memories/requests/configuration/settings)。
3. **设计哲学**:Next.js App Router + RSC + Route Groups(`(auth)` / `(root)`)+ 路由中间件守卫 + 客户端 axios + 401 自动 refresh——**这是 Next.js 15 全栈认证的范式实现**。

---

## 1. 该子项目的角色与边界

### 1.1 为什么有 Dashboard

Mem0 自托管模式(L8 Server)用 FastAPI 暴露 REST API——但运维和测试需要 GUI:
- 注册账号、登录、改密码
- 看 memory 列表、搜索 memory、删 memory
- 管理 API key
- 配 provider(LLM/embedder/vector_store)
- 看请求日志、调试

**Dashboard 就是这个 GUI**。它本身不含业务逻辑,所有数据操作都调 L8 Server 的 REST API。

### 1.2 边界

| 不归 Dashboard 做 | 归 Dashboard 做 |
|---|---|
| 实现 memory add/search 逻辑 | UI 渲染 + 表单提交 + 列表展示 |
| JWT 签发/验证 | 存储 access_token(内存)+ refresh_token(httpOnly cookie via Route Handler) |
| Provider 配置生效 | 5 步 setup 向导收集配置,POST 给 server |
| 权限校验 | UI 层 guard(isAdmin 隐藏 admin-only 入口)+ server 层最终校验 |

### 1.3 与 L8 Server 的关系

```
Browser ─── HTTPS ───► Dashboard (Next.js :3000)
                          │
                          │ axios (NEXT_PUBLIC_API_URL)
                          ▼
                       FastAPI Server (:8888)
                          │
                          ├── PostgreSQL (memories + users + api_keys)
                          ├── pgvector (vector search)
                          └── 可选 Neo4j (graph memory)
```

**关键**:Dashboard **不直接连 DB**,所有数据走 L8 Server REST。这意味着 Dashboard 可以单独部署多副本(无状态)。

---

## 2. 技术栈(从 `package.json` 和源码反推)

| 维度 | 选择 |
|---|---|
| Framework | Next.js 15(App Router) |
| React | 18+(RSC 支持) |
| TypeScript | strict mode |
| UI 库 | **shadcn/ui**(基于 Radix UI Primitives + Tailwind CSS) |
| 状态管理 | **Redux Toolkit**(`store/reducers/layoutReducer.ts`)+ React Context(`AuthProvider`) |
| HTTP 客户端 | **axios**(主)+ fetch(流式 + auth refresh) |
| 表单 | 标准 React state + custom validators |
| 图标 | **lucide-react** |
| 复制剪贴板 | `react-copy-to-clipboard` |
| 部署 | 独立 Dockerfile(跟 server 的 Dockerfile 分开) |
| 端口 | `:3000`(server 是 `:8888`) |

---

## 3. 完整文件清单(`server/dashboard/src/`)

ONBOARDING 提到 8 个文件,实际目录有 30+。完整结构:

### 3.1 顶层工具与配置

| 文件 | 行数 | 角色 |
|---|---|---|
| `src/middleware.ts` | 67 | **Next.js Edge Middleware**——所有路由的入口 guard |
| `src/utils/api.ts` | 113 | **axios 客户端工厂 + 401 refresh 拦截器** |
| `src/utils/self-hosted-config.ts` | (中) | 配置 helper(`buildProviderConfig` / `getEffectiveConfig`) |
| `src/lib/auth.tsx` | 135 | **AuthProvider** React Context |
| `src/lib/server-api-url.ts` | (小) | 服务端 API URL 解析(SSR 用) |
| `src/lib/validators.ts` | (小) | 邮箱/密码等 validator |
| `src/lib/error-message.ts` | (小) | 错误信息提取 helper |
| `src/lib/utils.ts` | (小) | 通用 helper(`cn` className 合并等) |

### 3.2 hooks

| 文件 | 角色 |
|---|---|
| ⭐ `src/hooks/use-api-query.ts` | 56 | **通用数据拉取 hook**(类似 react-query 的极简版,带并发去重) |
| `src/hooks/use-auth.ts` | (小) | `useAuth()`——useContext(AuthContext) 简单封装 |
| `src/hooks/useDebounce.ts` | (小) | debounce hook |

### 3.3 Redux store

| 文件 | 角色 |
|---|---|
| `src/store/store.ts` | Redux store 配置 |
| `src/store/rootReducer.ts` | root reducer |
| `src/store/reducers/layoutReducer.ts` | layout 状态(sidebar 开关等) |

**为什么同时用 Redux 和 Context**:Redux 管 UI 状态(sidebar 开关、theme),Context 管认证状态(user、token)。**认证用 Context 是因为它不频繁变化,UI 状态用 Redux 是因为有多组件订阅**。

### 3.4 类型与常量

| 文件 | 角色 |
|---|---|
| `src/types/api.ts` | API 类型定义 |
| `src/types/ui-components.ts` | UI 组件类型 |
| `src/types/imurmurhash.d.ts` | imurmurhash 类型声明 |
| `src/constants/index.ts` | 常量 |
| `src/constants/ui-components.ts` | UI 组件常量 |

### 3.5 App Router 页面(App Directory)

| 路径 | 角色 |
|---|---|
| `src/app/(auth)/login/page.tsx` | 登录页(route group `(auth)`) |
| ⭐🔥 `src/app/(auth)/login/login-form.tsx` | 登录表单组件 |
| `src/app/(auth)/layout.tsx` | 认证页 layout |
| ⭐🔥 `src/app/setup/page.tsx` | **763 行 5 步 setup 向导** |
| `src/app/setup/layout.tsx` | setup 页 layout |
| `src/app/api/health/route.ts` | health check endpoint |
| `src/app/api/auth/refresh/route.ts` | **refresh token 的 Route Handler**(httpOnly cookie 存储) |
| `src/app/(root)/layout.tsx` | 根 layout |
| `src/app/(root)/clientLayout.tsx` | 客户端 layout |
| `src/app/(root)/fonts.tsx` | 字体加载 |
| `src/app/(root)/dashboard/layout.tsx` | dashboard 区 layout |
| `src/app/(root)/dashboard-client-layout.tsx` | dashboard 客户端 layout |
| `src/app/(root)/dashboard/{api-keys,memories,requests,configuration,settings}/page.tsx` | **5 个 dashboard 功能页** |

### 3.6 组件

| 文件 | 角色 |
|---|---|
| `src/components/ui/sidebar.tsx` | 274 行 shadcn/ui 侧边栏(自定义) |
| `src/components/ui/use-toast.tsx + toaster.tsx` | shadcn/ui toast 系统 |
| `src/components/ui/{button,input,label,card,select,...}.tsx` | shadcn/ui 标准组件(20+) |
| `src/components/shared/data-table.tsx` | **通用数据表格**(api-keys/memories/requests 页都用) |

---

## 4. ⭐ 核心深读:`utils/api.ts`(113 行)— axios + 401 refresh

这是 dashboard 的"血管"。所有 API 调用都经过它。

### 4.1 设计要点

```typescript
// 简化结构
let cachedToken: string | null = null;          // access_token 在内存,不存 localStorage(XSS 防护)
const LOGIN_PATH = "/login";

const refreshAccessToken = async () => {        // 调 Route Handler(/api/auth/refresh)
  const refreshResponse = await fetch("/api/auth/refresh", {
    method: "POST",
    credentials: "include",                     // httpOnly cookie 自动带
  });
  if (!refreshResponse.ok) return null;
  const data = await refreshResponse.json();
  setAccessToken(data.access_token);
  return data.access_token;
};

const api = axios.create({ baseURL: process.env.NEXT_PUBLIC_API_URL });

api.interceptors.request.use((config) => {       // 请求拦截:注入 Authorization
  if (cachedToken) config.headers.Authorization = `Bearer ${cachedToken}`;
  return config;
});

api.interceptors.response.use(                   // 响应拦截:401 自动 refresh + retry
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const nextToken = await refreshAccessToken();
      if (nextToken) {
        error.config.headers.Authorization = `Bearer ${nextToken}`;
        return api.request(error.config);        // 重放原请求
      }
      redirectToLogin();                         // refresh 也失败 → 强制重新登录
    }
    return Promise.reject(error);
  }
);

// 流式 POST(用 fetch,因为 axios 不支持 stream)
const postStream = async (url, data) => { ... };
```

### 4.2 关键设计:双重 token 存储

| Token 类型 | 存储位置 | 为什么 |
|---|---|---|
| **access_token**(短命,如 15min) | 内存(`cachedToken` 变量) | 防 XSS——JS 读不到 localStorage 之外的内存？实际上内存 JS 也能读,但**至少不持久**,刷新页就没了 |
| **refresh_token**(长命,如 7d) | **httpOnly cookie** | JS 读不到,只有浏览器自动附给同源请求 |

**refresh 通过 Route Handler(`/api/auth/refresh`)中转**——browser JS 发 POST 给 Next.js Route Handler,Route Handler 在服务端读 httpOnly cookie、调 server 的 refresh endpoint、返回新 access_token。

### 4.3 postStream:为什么单独实现

axios 不支持 streaming response(`ReadableStream`),但 dashboard 的 chat 测试功能需要流式响应。所以 `postStream` 用原生 `fetch`——返回 `Response` 对象,caller 可以读 `response.body.getReader()` 流。

---

## 5. ⭐ 核心深读:`middleware.ts`(67 行)— 路由守卫

### 5.1 设计要点

```typescript
const PUBLIC_PATHS = ["/_next", "/api/auth", "/api/health", "/fonts", "/favicon"];

export async function middleware(request) {
  const { pathname } = request.nextUrl;
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) return NextResponse.next();
  
  const hasRefreshToken = request.cookies.has("mem0_refresh_token");
  
  // 对 "/", "/login", "/setup" 做 setup-status 检查
  if (pathname === "/" || pathname === "/login" || pathname === "/setup") {
    const res = await fetch(`${serverApiUrl}${SETUP_STATUS}`);
    if (res.ok) {
      const { needsSetup } = await res.json();
      if (needsSetup && pathname !== "/setup") return redirect("/setup");
      if (!needsSetup && pathname === "/setup") return redirect("/login");
    }
  }
  
  if (pathname === "/login" || pathname === "/setup") return NextResponse.next();
  if (pathname === "/") return redirect(hasRefreshToken ? "/dashboard/requests" : "/login");
  if (pathname === "/dashboard") return redirect("/dashboard/requests");
  
  if (!hasRefreshToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);    // 记住原始路径,登录后跳回
    return NextResponse.redirect(loginUrl);
  }
  
  return NextResponse.next();
}
```

### 5.2 路由决策矩阵

| Path | hasRefreshToken | needsSetup(server) | 结果 |
|---|---|---|---|
| `/` | true | false | → `/dashboard/requests` |
| `/` | false | false | → `/login` |
| `/` | * | true | → `/setup` |
| `/login` | * | false | 正常渲染 |
| `/login` | * | true | → `/setup` |
| `/setup` | * | false | → `/login` |
| `/setup` | * | true | 正常渲染 |
| `/dashboard/*` | true | * | 正常渲染 |
| `/dashboard/*` | false | * | → `/login?next=<原路径>` |
| `/api/auth/*` / `/api/health` | * | * | 正常(不 guard) |

### 5.3 关键设计:server-side fetch `setup-status`

middleware 在 Edge Runtime 跑,但能 fetch server API 判断"是否首次启动"。**这避免了用户在已 setup 的实例看到 setup 页,或在未 setup 的实例看到 login 页**——这种"chicken-and-egg"问题用 server-side check 解决。

---

## 6. ⭐ 核心深读:`lib/auth.tsx`(135 行)— AuthProvider Context

### 6.1 设计要点

```typescript
const AuthContext = createContext<AuthContextValue>({
  user: null, isLoading: true, isAdmin: false,
  login: async () => {}, register: async () => {},
  logout: async () => {}, refreshUser: async () => {},
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // mount 时尝试 refresh
  useEffect(() => {
    (async () => {
      const ok = await refreshSession();        // 调 /api/auth/refresh
      if (ok) await loadUser();                  // 调 GET /auth/me
      setIsLoading(false);
    })();
  }, []);
  
  const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    setAccessToken(res.data.access_token);
    await storeRefreshToken(res.data.refresh_token);   // PUT /api/auth/refresh
    await loadUser();
  };
  
  // register / logout 类似
  
  return <AuthContext.Provider value={{user, isLoading, isAdmin: user?.role === "admin", ...}}>{children}</AuthContext.Provider>;
}
```

### 6.2 关键设计:refresh token 的 4 个操作

通过 `/api/auth/refresh` Route Handler 用 HTTP method 区分操作:

| Method | 操作 |
|---|---|
| `POST` | 刷新 access token(用 cookie 里的 refresh_token 换新 access_token) |
| `PUT` | 存储 refresh_token(登录/注册成功后调用,把 refresh_token 写 httpOnly cookie) |
| `DELETE` | 清除 refresh_token(logout 时调用) |
| `GET` | (未实现,不需要——POST 已经能返回当前 token) |

### 6.3 isAdmin 的简化

`isAdmin: user?.role === "admin"`——一行判断。**真正的权限校验在 server**,client 只是隐藏 UI 入口。

---

## 7. ⭐ 核心深读:`hooks/use-api-query.ts`(56 行)— 极简 react-query

### 7.1 设计要点

```typescript
export function useApiQuery<T>(fetcher: () => Promise<T>, options) {
  const { enabled = true, errorToast, initialData } = options;
  const [data, setData] = useState(initialData);
  const [isLoading, setIsLoading] = useState(enabled);
  const [error, setError] = useState("");
  
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;                  // ref 保存最新 fetcher,避免重渲染
  
  const run = useCallback(async () => {
    setIsLoading(true); setError("");
    try {
      setData(await fetcherRef.current());
    } catch (err) {
      const message = getErrorMessage(err, errorToast || "Request failed");
      setError(message);
      if (errorToast) toast({ title: errorToast, description: message, variant: "destructive" });
    } finally { setIsLoading(false); }
  }, [errorToast]);
  
  useEffect(() => { if (enabled) void run(); }, [enabled, run]);
  
  return { data, isLoading, error, refetch: run };
}
```

### 7.2 关键设计:`fetcherRef` 避免重渲染

如果直接用 `useEffect(() => { run(); }, [fetcher])`,`fetcher` 每次 render 都是新引用(`() => api.get(...)` 每次重建),会无限触发。**用 `useRef` 保存最新 fetcher,但 deps 只有 `[enabled, run]`**——这是 React hook 的经典技巧。

### 7.3 为什么不用 react-query / SWR

依赖更少(零)、bundle 更小、对 Mem0 这种简单 admin 后台足够。**但失去了 react-query 的 cache / dedupe / retry / optimistic update**。是个 trade-off。

---

## 8. ⭐ 核心深读:`app/setup/page.tsx`(763 行)— 5 步引导向导

### 8.1 5 步流程

```typescript
const STEPS = ["Admin Account", "Providers", "API Key", "Use Case", "Quick Test"];
```

| Step | 收集什么 | POST 到哪 |
|---|---|---|
| 1. Admin Account | name / email / password | `/auth/register` |
| 2. Providers | LLM provider/model + embedder provider/model + vector_store | `/configure`(server 写 config) |
| 3. API Key | (展示自动生成的 admin API key) | `/api-keys` |
| 4. Use Case | use case preset(companion/coding/support/research/therapy) | server 记录,影响 default prompt |
| 5. Quick Test | add 一条 test memory + search | `/memories/add` + `/memories/search` |

### 8.2 关键设计

- **每步独立验证**:不能前进到下一步,除非当前步表单 valid
- **可回退**:点 Back 按钮回到上一步,数据保留
- **服务端 setup-status**:server 已 setup 时,middleware 自动重定向到 /login,不让用户看到 setup
- **use case preset**:5 种预设(companion / coding agent / customer support / research / therapy journaling)——server 根据选的 preset 调整 LLM prompt
- **bundled providers**:dashboard 知道哪些 provider 是 server 默认 bundled 的,展示在下拉框;非 bundled 的需要用户手工配

---

## 9. 共通模式

### 9.1 Route Groups 分组

Next.js 15 App Router 的 route groups(`(auth)` / `(root)`):
- `(auth)/` 共享认证页 layout(简洁、无 sidebar)
- `(root)/` 共享 dashboard layout(有 sidebar、有 nav、需要登录)

**这种分组让 layout 复用,不污染 URL**——`/login` 而不是 `/auth/login`。

### 9.2 Client Component vs Server Component

- 大部分页面是 **Client Component**(`"use client"`),因为要调 `useAuth` / `useApiQuery` / `useState`
- `middleware.ts` 是 Edge Runtime(server-side)
- `app/api/*/route.ts` 是 Route Handler(server-side)
- layout 文件可以 RSC,但 dashboard 内嵌的 client layout 转为 client

**整体偏 client-heavy**——因为 admin dashboard 交互多,RSC 优势不明显。

### 9.3 shadcn/ui + Tailwind + Radix

UI 完全基于 shadcn/ui(基于 Radix Primitives + Tailwind + CVA)。`components/ui/*.tsx` 是 shadcn CLI 生成的标准组件,可以直接 copy-paste 修改。

**为什么不用 Material UI / Ant Design**:bundle 大、定制难、风格强。shadcn 是"copy 当自己的",灵活。

### 9.4 Toast 错误处理统一

`useApiQuery` 的 `errorToast` 选项 + `toast({variant: "destructive"})`——所有错误统一弹 toast,不在页面内 inline 显示。**简化错误处理,但失去了 inline 错误上下文**。

---

## 10. 该层的"反模式 / 坑"

### 10.1 access_token 在内存 → 刷新页就丢失

刷新页面后 `cachedToken = null`,要重新调 `/api/auth/refresh` 拿新 token。这本身没问题,但**首次渲染时所有 API 都会 401 + refresh + retry**——增加首次加载延迟。

### 10.2 middleware fetch server 在每个请求

每次路由跳转都 fetch `/setup-status`——**慢**。可以加 Edge Cache,但 setup 状态会变化,缓存失效策略要谨慎。

### 10.3 Redux 与 Context 共存的复杂度

新加入的开发者会困惑"什么时候用 Redux,什么时候用 Context"。**有 React 18+ useSyncExternalStore 后,Redux 的优势减弱**——可以考虑全用 Context + useReducer。

### 10.4 setup 向导的"前进不可逆"

某些步骤(register、API key 生成)是不可逆的——如果用户在第 3 步刷新页面,可能进入奇怪状态。**setup 页本身需要更复杂的状态恢复机制**(localStorage 或 server-side state)。

### 10.5 postStream 的 401 处理简化

```typescript
// utils/api.ts postStream
if (response.status === 401) {
  handleTokenError();
  redirectToLogin();
  throw new Error("Unauthorized");
}
```

**没有 refresh 重试**——而 axios 的 401 拦截器有。**这是不一致**:同样的 401,POST 走 axios 会 refresh,走 postStream 直接踢登录。流式接口的用户体验更差。

---

## 11. 阅读完本综述后应该理解

- ✅ Dashboard 是 self-hosted Mem0 的 GUI,跟 FastAPI server 解耦
- ✅ 双重 token 存储(access 内存 + refresh httpOnly cookie)
- ✅ Route Handler(`/api/auth/refresh`)的中转设计
- ✅ middleware 的 setup-status 检查 + 路由守卫矩阵
- ✅ useApiQuery 的极简 react-query 替代
- ✅ 5 步 setup 向导的数据流
- ✅ Next.js 15 App Router 的 Route Groups
- ✅ shadcn/ui + Tailwind + Radix 的组合
- ✅ 该层与 L8 Server 的通信(REST only,无共享 DB)

---

📌 **下一步**:
- 已完成 4 篇:L10 D / L2 补丁 / L11 D / L7 C
- 接下来:**L6 TS SDK 补**(8 未覆盖,与 Python 平行,值得对照讲)
