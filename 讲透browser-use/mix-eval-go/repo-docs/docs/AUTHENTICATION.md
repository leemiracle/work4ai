# Authentication System

The evaluation platform handles authenticated tasks (social media, paywalls) using a centralized credential pool stored in Convex.

## How It Works

Tasks reference credentials via `auth_keys` or include pre-populated `loginCookie` strings. Runners fetch credentials from `/api/getAuthDistribution`, inject them as browser cookies, and the browser starts already authenticated.

## Credential Pool

The `authDistribution` table in Convex stores:
- Shared credentials across all runners (Google, GitHub, LinkedIn, NYT, etc.)
- Lifecycle management: `isCycledOut`, `isOnHold` flags for rotation
- Access tracking: `accessCount`, `lastAccessedAt` for monitoring

## Authentication Flow

```
Task Definition → Runner Fetches Credentials → Inject Cookies → Authenticated Browser
     ↓                      ↓                         ↓                    ↓
auth_keys:          GET /api/getAuth          storage_state.json    Site sees logged-in
["nytimes"]         Distribution               with session          user, no paywall
                    Returns loginInfo          cookies loaded
```

## Sample Task Definition

```json
{
  "task_id": "1284368",
  "confirmed_task": "Find DataRobot pricing on their enterprise page",
  "website": "datarobot.com",
  "auth_keys": ["datarobot"],
  "login_cookie": "session=abc123; auth_token=xyz789",
  "category": "pricing_research",
  "outputSchema": {"price": "string", "tier": "string"}
}
```

## Current Implementation

**Note**: mix-eval-go currently defines the `LoginCookie` field but delegates authentication to Mix Agent. Future versions may implement direct credential injection.
