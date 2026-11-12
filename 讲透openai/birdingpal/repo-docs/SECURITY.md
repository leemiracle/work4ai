# Security

Please do not report security vulnerabilities through public GitHub issues.
Use OpenAI's current vulnerability disclosure process instead.

This repository contains prototype code. The companion app's debug build reads
`OPENAI_API_KEY` from local build configuration and embeds it into the debug
APK. Do not distribute APKs built with this debug configuration. Public or
production use should replace embedded keys with server-issued ephemeral tokens
or another design that does not ship long-lived secrets to client devices.

Before publishing or redistributing changes, run a secret scan against the
tracked files and git history. The repository `.gitignore` is configured to
exclude `.env*`, `local.properties`, build outputs, dependency folders, and
generated Gradle state.
