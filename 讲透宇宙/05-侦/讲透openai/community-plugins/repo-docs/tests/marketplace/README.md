# Marketplace runner contracts

Run the repository dispatcher through npm:

```sh
npm run test:marketplace
# Equivalent root entry point:
npm test
```

The dispatcher requires the existing npm lifecycle's absolute `npm_execpath`
to resolve to a regular `npm-cli.js`. It launches that entry point with the
current Node executable, without a command shell or a fallback to `npm` on
`PATH`. This works with the Windows npm command-file installation without
trying to execute `npm.cmd` directly. A direct `node
scripts/run-marketplace-tests.mjs` launch without the lifecycle prerequisites
fails with an npm-run diagnostic. Path and file-type checks are not
authentication of npm's identity; the checkout and launch environment remain
trusted developer inputs.

All catalog entries must have nonempty string master scripts before any master
starts. Masters run in catalog order and the first failure stops dispatch with
that status. The runner preserves inherited registry, proxy, user/global npm
configuration and other environment values. It does not install dependencies
or change npm configuration.

Run just the lightweight subprocess contracts with:

```sh
npm run test:marketplace:runner
```

These tests use disposable repositories and real Node subprocesses. A
self-terminating JavaScript probe records literal arguments, path handling,
order and inherited-setting hashes without implementing npm or executing
package scripts. Its private `PATH`-empty cases detect an unintended launcher
fallback; they do not change the user's configuration. A separate case uses
the actual inherited npm lifecycle to run two test-owned local scripts, without
installing dependencies or contacting a provider. Directly invoking the Node
test file skips that last check when npm lifecycle context is absent.

The outer test subprocesses have bounded output and timeouts. Probe children
terminate themselves; tests confirm the recorded processes are absent before
removing their private directories. Unconfirmed cleanup preserves the evidence.
The Marketplace workflow schedules these contracts on Linux, macOS and Windows.
A configured CI job is not an actual platform execution result, and these
runner checks do not qualify the plugins' external providers.
