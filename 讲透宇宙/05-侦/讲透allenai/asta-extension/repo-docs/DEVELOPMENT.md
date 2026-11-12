# Development

## Building

Production builds require the `S2_API_URL` environment variable. Tests and dev builds work without it (uses public S2 API).

For environment variables and credentials, see the 1Password vault.

## Upstream Sync

1. Fetch and merge upstream:
   ```bash
   git fetch upstream
   git checkout -b sync/upstream-YYYY-MM main
   git merge upstream/master
   ```

2. Resolve conflicts:
   - Keep ours: `manifest.json`, `src/index.js`, `src/badges.js`, `src/background.js`, `src/components/HideableTally.js`

3. Create PR using **merge commit** (not squash) to preserve git history for future syncs

## Releasing

1. Update version in `package.json` and `extension/manifest.json`
2. Merge to main
3. Create a git tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. Build and publish (see 1Password vault for credentials)
