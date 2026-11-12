# Generic PostgreSQL Container

A self-contained PostgreSQL container image driven entirely by standard environment variables. It owns the full
database lifecycle — install, initialize, optionally restore from a dump, apply bundled schema files, create a
limited application role, and shut down gracefully — without any deployment-specific logic (no remote-access
tunneling, no environment selection, no bundled database dumps).

The lifecycle is split into three sequential phase scripts plus a thin orchestrator, all in `/usr/local/bin`:
`init-db.sh` (validate / install / init / create role / optional restore), `tables_manifest.sh` (apply the manifest's
schema files in order, then grant), and `run-postgres.sh` (foreground server under a graceful-shutdown trap).
`startup.sh` is the entrypoint: it sources the first two and execs the third.

The image ships the `orchestration.sql` schema and a manifest listing it, and applies it on every boot. To
run with a different schema, point `SCHEMA_DIR` at a directory of `*.sql` files plus a `tables_manifest.txt` that sets
the load order (see [Schema Initialization](#schema-initialization)).

The server is PostgreSQL 18, installed at startup from the PostgreSQL Global Development Group (PGDG) apt repository
rather than the base image's distribution archive, which carries a single major per release. The major is pinned by
`PG_MAJOR` in [BUILD](BUILD); see [PostgreSQL Version](#postgresql-version) for what changing it involves. The
install runs after the environment and data-directory checks, so a container that would be rejected fails without
downloading anything, and it is skipped when a restarted container already has the packages installed.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `POSTGRES_USER` | Yes | Application role to create with limited privileges (SELECT/INSERT/UPDATE/DELETE, no DDL). |
| `POSTGRES_PASSWORD` | Yes | Password for the application role. |
| `POSTGRES_DB` | Yes | Target database name to create / restore into. |
| `BACKUP_FILE` | No | Path to a `pg_dump -Fc` archive to restore on first initialization. If unset, the database starts empty. |
| `RESTORE_SCHEMA_ONLY` | No | Set to `true` to restore only the schema (no table data) from `BACKUP_FILE`. Intended for tests that exercise the restore path without the bulk-data cost. |
| `FORCE_REINIT` | No | Set to `true` to clear the data directory and reinitialize from scratch. |
| `SCHEMA_DIR` | No | Directory holding the schema `*.sql` files and the `tables_manifest.txt` that orders them, applied on every boot (default `/etc/postgres-schemas`). |
| `PG_MAJOR` | Set by the image | PostgreSQL major version installed at startup. Not meant to be overridden: the image is tested against one major. |

The server listens on port `5432` and accepts password-authenticated connections from any host, using
`scram-sha-256`. Data persists in `/var/lib/postgresql/data`; mount a volume there to retain it across container
restarts (subsequent starts skip initialization and restore, but still apply the schema files).

## PostgreSQL Version

A data directory records the major that created it in `PG_VERSION`, and no other major can start on it. The image
checks this before anything else touches the directory: a volume created by a different major stops the boot with
an error naming both majors, rather than letting the server fail later with a catalog-version mismatch.

Moving a volume to a new major is therefore a dump and restore:

1. With the previous image still running on the volume, dump each database: `pg_dump -Fc <database> > <database>.dump`.
2. Start the new image on an empty volume (or with `FORCE_REINIT=true`, which deletes the existing data), passing one
   archive as `BACKUP_FILE`. Restore any further databases with `pg_restore --create -d postgres <database>.dump`.

`pg_restore` reads archives written by older `pg_dump` versions, but not newer ones, so archives produced by this
image need a client of the same major or later to inspect them.

## Schema Initialization

On every boot, after the optional dump restore and before granting the application role, `tables_manifest.sh` reads
`tables_manifest.txt` from `SCHEMA_DIR` (default `/etc/postgres-schemas`) and applies each listed `*.sql` file **in the
order listed** (entries are filenames relative to `SCHEMA_DIR`; blank lines and `#`-comments are ignored). The grant
block runs at the end of `tables_manifest.sh`, after every manifest entry is applied, so the one-shot
`GRANT ... ON ALL TABLES` covers every object created here.

Every manifest file must be safe to apply repeatedly: `CREATE ... IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`, and no
seed rows. That is what lets a mounted volume keep up with the schema files however old it is, rather than staying
frozen at the schema it was created with — a divergence that surfaces only as application code failing against a
database that booted cleanly. A file that cannot be applied twice fails the boot.

This image bundles `orchestration.sql` and a `tables_manifest.txt` listing just that file. To apply a different schema
set or load order, supply your own `tables_manifest.txt` (and `*.sql` files) through `SCHEMA_DIR`.

## Build and Run

In the commands below, `dazel run //database:image_load` loads the image as `database-postgres:<version>`, where
`<version>` is the value of `VERSION` in [version.bzl](version.bzl) (currently `1.2.0`).

```bash
# Build and load the image into Docker
dazel run //database:image_load

# Run with only the bundled schema applied (no data)
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=appdb \
  -v postgres-data:/var/lib/postgresql/data \
  database-postgres:<version>

# Run and restore from a bundled/mounted dump on first start
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=appdb \
  -e BACKUP_FILE=/backups/snapshot.dump \
  -v /path/to/backups:/backups \
  -v postgres-data:/var/lib/postgresql/data \
  database-postgres:<version>
```

## Testing

```bash
# Boots the image with the POSTGRES_* contract (no BACKUP_FILE) and verifies the init / app-user / grant path, the
# pinned major, SCRAM authentication, and the rejection of a data directory from another major.
dazel test //database/tests:image_test
```
