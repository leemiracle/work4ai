# Nautobot Changelog Reporting Through  Nats

## Introduction
This is an [event broker](https://docs.nautobot.com/projects/core/en/next/user-guide/platform-functionality/events/) for [Nautobot](https://github.com/nautobot/nautobot) that publishes events to [NATS](https://nats.io).

## Configuration

Add this to your nautobot_config.py:
```
connect = {}

# Optional path to a credentials file.
if "NATS_CRED" in os.environ:
    connect["user_credentials"] = os.environ["NATS_CRED"]

from nautobot.core.events import register_event_broker
from nautobot_nats_broker import NATSEventBroker

register_event_broker(
    NATSEventBroker(
        servers="nats-server-url",
        stream="nautobot",
        **connect,
    )
)
```

## Example Outputs

This is what shows up on NATS when you have this plugin configured and then create a new Namespace resource:
```
{
  "request": {
    "id": "501a0004-0fdd-404e-b46c-d2a189d868df",
    "user": "test_user"
  },
  "event": "create",
  "model": "ipam.namespace",
  "record": {
    "id": "c310b8cc-bceb-49a2-b323-c109ed828b10",
    "url": "/api/ipam/namespaces/c310b8cc-bceb-49a2-b323-c109ed828b10/",
    "name": "test_namespace",
    "tags": [],
    "created": "2026-03-25T19:18:15.841125Z",
    "display": "test_namespace",
    "location": null,
    "notes_url": "/api/ipam/namespaces/c310b8cc-bceb-49a2-b323-c109ed828b10/notes/",
    "description": "",
    "object_type": "ipam.namespace",
    "last_updated": "2026-03-25T19:18:15.841138Z",
    "natural_slug": "test_namespace_c310",
    "custom_fields": {}
  },
  "@url": "/api/ipam/namespaces/c310b8cc-bceb-49a2-b323-c109ed828b10/",
  "@timestamp": "2026-03-25T19:18:15Z",
  "response": {
    "host": "test_host.example.com"
  }
}

```

## Publishing

Publishing is handled by GitHub Actions through PyPI Trusted Publishing.

The release workflow uses two tag types:

- `X.Y.Z-rc.N` on a commit that is not reachable from `main` exercises the release process, creates a GitHub prerelease, uploads package assets, and skips PyPI upload.
- `X.Y.Z` on a commit that is reachable from `main` creates a GitHub release, uploads package assets, and publishes those assets to PyPI.

The version in `pyproject.toml` must stay in stable `X.Y.Z` form. Release candidate tags use the same base version. For example, `pyproject.toml` can contain `1.2.3` while the RC tag is `1.2.3-rc.1`.

1. Update the version number in `pyproject.toml`.

2. Update and verify the lock file.

```bash
uv lock
uv lock --check
```

3. Commit the version and lock-file changes.

```bash
git add pyproject.toml uv.lock
git commit -m "Release X.Y.Z"
```

4. Exercise the release flow with a release candidate tag from the branch containing the version-change commit before it is merged to `main`.

```bash
git checkout <release-branch>
git push origin HEAD
git tag X.Y.Z-rc.1
git push origin X.Y.Z-rc.1
```

Expected result: GitHub Actions validates the tag, builds the package, creates a prerelease, uploads the package assets, and skips PyPI publishing.

5. Merge the version-change branch to `main`, then create and push the stable release tag from `main`.

```bash
git checkout main
git pull --ff-only
git tag X.Y.Z
git push origin X.Y.Z
```

Expected result: GitHub Actions validates the tag, builds the package, creates a release, uploads the package assets, and publishes to PyPI.
