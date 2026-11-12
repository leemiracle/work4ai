# Tailscale Connection Hint

Chrome extension that shows helpful troubleshooting when `.local` domains (Tailscale MagicDNS) fail to resolve.

## Features

- Intercepts DNS resolution failures for `.local` domains
- Shows live connectivity monitoring with two graphs:
  - **Your Service**: The URL you were trying to reach
  - **kcprr (infrastructure)**: Verifies Tailscale connectivity
- Auto-redirects when connection is restored
- Distinguishes between "Tailscale down" vs "Service unavailable"
- Copy-able latency stats on click
- Links to #infra-assist and Tailscale docs

## Permissions Justification

| Permission | Justification |
|------------|---------------|
| `webNavigation` | Required to intercept `onErrorOccurred` events for DNS failures |
| `tabs` | Required to redirect the tab to our hint page |
| `<all_urls>` (host) | Required because `.local` domains can be any URL pattern; we only act on `*.local` hostnames |

## Installation (Development)

1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select this directory

## Files

- `manifest.json` - Extension manifest (Manifest V3)
- `background.js` - Service worker that intercepts DNS errors
- `tailscale-hint.html` - The helpful error page
- `hint.js` - Connectivity monitoring and UI logic
- `icons/` - Extension icons

## Author

@nova (nova@anthropic.com)
