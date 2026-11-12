# Mix Go SDK v0.2.1 Streaming Bug

## Issue
`mixClient.Streaming.StreamEvents()` returns streams that immediately fail with "context canceled" error.

## Root Cause
**File**: `streaming.go` lines 76-85, 216, 301

```go
if timeout != nil {
    ctx, cancel = context.WithTimeout(ctx, *timeout)
    defer cancel()  // ❌ Cancels when function returns
}

// Create stream with context
out := stream.NewEventStream(ctx, httpRes.Body, unmarshaller, "")
return res, nil  // ❌ defer cancel() executes, canceling context
```

The `defer cancel()` executes when `StreamEvents()` returns, but the returned `EventStream` still needs the context for reading events. When user calls `stream.Next()`, it detects the canceled context and immediately returns false.

## Impact
- SDK streaming client unusable
- All SSE events lost
- Stream appears to connect then immediately cancel

## Workaround
Use manual HTTP SSE connection with `net/http` and `bufio.Scanner`:

```go
req, _ := http.NewRequestWithContext(ctx, "GET", streamURL, nil)
resp, _ := http.DefaultClient.Do(req)
scanner := bufio.NewScanner(resp.Body)
for scanner.Scan() {
    // Parse SSE events
}
```

## Status
Reported to Mix Go SDK maintainers. Use manual HTTP streaming until fixed.

## Related Issue (TypeScript SDK)
In the TS SDK streaming path used by `mix_dev_tool`, SSE events often deserialize with empty `data`. We consistently saw `complete` events with `contentLength=0` and `timelineLength=0`, while DB persistence was correct. Switching to raw `EventSource` parsing immediately fixed live streaming. This points to a TS SDK event deserialization issue (data loss), not a backend stream issue. Workaround: bypass SDK streaming and parse SSE manually.
