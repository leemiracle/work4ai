# Publishing `@browser_use/eve`

The package is publish-ready: `files: ["dist"]`, `prepare` builds on publish,
scoped under @browser_use. The GitHub repo
(`github.com/browser-use/eve`, private) already exists and is pushed.

## Internal (today) — git install, no npm

```bash
npm i github:browser-use/eve     # needs access to the private repo
npx @browser_use/eve add
```

## Public — publish to npm (outward, gated)

```bash
# 1. log in (opens a browser; needs your 2FA)
npm login

# 2. publish — scoped public (publishConfig.access=public); prepare builds dist
cd ~/Projects/lab/browser-use-eve
npm publish

# 3. verify
npm view @browser_use/eve
```

Then `npm i @browser_use/eve && npx @browser_use/eve add` works for anyone.

## After publish

- [ ] Smoke test in a fresh eve app: `npm i @browser_use/eve && npx @browser_use/eve add`
- [ ] Tag the release: `git tag v0.0.1 && git push --tags`
- [ ] Consider making the GitHub repo public (so a deploy-button template can build)
- [ ] Open the eve Integrations gallery PR / cross-link from Browser Use docs

## Notes

- The tarball contains only `dist/` (+ README, LICENSE, package.json) — verify with `npm pack --dry-run`.
- Scoped packages default to private; `publishConfig.access: "public"` makes it public.
- `peerDependencies` (`eve`, `zod`) come from the consuming eve app; `browser-use-sdk` installs with the package.
- Publishing is public + effectively permanent (unpublish is restricted to 72h).
