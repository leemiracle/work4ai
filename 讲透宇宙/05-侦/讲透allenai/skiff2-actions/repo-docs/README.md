# allenai/skiff2-actions

Reusable GitHub Actions for deploying services on Skiff2 — a GCP-based platform that builds Docker images and deploys them as Cloud Run services behind a shared load balancer, managed via Terraform.

All behavior is driven by action inputs. The build and deploy actions derive their configuration entirely from a `skiff2.json` file (passed as an input) along with a small set of additional inputs (e.g. `project_id`, `region`). No configuration is baked into the actions themselves.

## Actions

### Testing

Install `act`: https://nektosact.com/installation/index.html. On MacOS, install with `brew`:

```sh
brew install act
```

Run `act` targeting the test workflow (example uses the shared build action):

```sh
act -W shared-actions/build/test/test-action.yml
```

If you're having trouble with docker sockets when using colima, follow these instructions: https://github.com/nektos/act/issues/2239#issuecomment-2466020469

### `shared-actions/setup`

Takes GCP credentials and project inputs and sets up Workload Identity Federation authentication, Cloud SDK, and Docker for GCR.

### `shared-actions/build`

Takes a `skiff2.json` config and image-tagging inputs, builds Docker images for the defined services, and pushes them to GCR.

### `shared-actions/deploy-infra`

Takes a `skiff2.json` config and a `command` input (`plan` or `apply`), transforms the config into Terraform variables, and provisions shared infrastructure (load balancer, URL map, NEGs, SSL certificates).

### `shared-actions/deploy-services`

Takes a `skiff2.json` config, an `environment` input, and a `command` input (`plan` or `apply`), transforms the config into Terraform variables, and deploys Cloud Run services into the specified Terraform workspace.

## Terraform modules

The `project-terraform/` directory contains the Terraform modules used by the deploy actions:

- `infra/` — shared infrastructure (load balancer, networking)
- `services/` — Cloud Run service definitions

## Formatting

To format files, run `npx prettier . --write`.

## License

Apache 2.0 — see [LICENSE](./LICENSE).
