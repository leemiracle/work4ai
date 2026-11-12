# PSR: Tailscale Connection Hint Chrome Extension

## Summary

Chrome extension to improve developer experience when Tailscale MagicDNS `.local` domains fail to resolve. Instead of Chrome's generic "DNS_PROBE_FINISHED_NXDOMAIN" error, users see a helpful page with:
- Live connectivity monitoring
- Troubleshooting steps from our docs
- Links to #infra-assist
- Auto-redirect when connection is restored

## Permissions Requested

### API Permissions

| Permission | Required | Justification |
|------------|----------|---------------|
| `webNavigation` | Yes | To listen for `onErrorOccurred` events and detect DNS resolution failures |
| `tabs` | Yes | To update the current tab URL and redirect to our hint page |

### Host Permissions

| Pattern | Required | Justification |
|---------|----------|---------------|
| `<all_urls>` | Yes | We need to intercept DNS errors for any `.local` domain. Chrome doesn't support wildcard patterns like `*://*.local/*` in host_permissions. We only act on hostnames ending in `.local`. |

## Data Handling

- **No data collection**: Extension does not collect, store, or transmit any user data
- **No external requests**: Only makes requests to the original URL and kcprr.*.local for connectivity checks
- **No cookies/storage**: Does not access cookies, localStorage, or any stored data
- **Local only**: All processing happens client-side

## Code Review Notes

- Manifest V3 (modern, more secure)
- No content scripts (doesn't inject into pages)
- No remote code execution
- Service worker only activates on navigation errors
- Source code: [link to repo]

## Testing

1. Disconnect from Tailscale
2. Navigate to any `.local` URL (e.g., `http://test.sodium-a.local`)
3. See helpful hint page instead of Chrome error
4. Reconnect Tailscale
5. Page auto-redirects when connection restored

## Distribution

- Chrome Web Store (Private/Internal only)
- Force-install via Google Workspace for opt-in group
