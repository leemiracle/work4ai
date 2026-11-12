# Plugin organization and test suites

These conventions apply throughout this repository and reflect the maintainer's
preferred organization. Follow the existing Grafana, ReviewOps and React Native
to SwiftUI plugins when adding or changing a plugin.

- Keep each installable package in `plugins/<plugin-name>/`. Repository companion
  tests belong in `tests/<plugin-name>/`, with `unit/`, `integration/`, `security/`
  and `support/` directories where applicable. Existing deeper package suites
  should remain connected to the root master command.
- Provide one canonical root `npm run test:<plugin-name>` command that runs the
  complete automated suite: package, functional, integration/E2E, security and
  language-specific checks. The marketplace dispatcher must call this same
  command. Do not leave tests disconnected from the master suite.
- Expose **one master job in one plugin workflow**. Run the master suite and
  required build, native-source, audit and reproducibility checks as sequential
  steps in that job. Run supported Node versions sequentially, as neighboring
  plugin workflows do.
- Do not split a plugin across platform matrices, separate native workflows or
  independent test jobs, or add an aggregator job over such a split, unless the
  user explicitly requests that structure. Shared marketplace validation remains
  repository-wide and reuses each plugin's master command.
- Keep CI and test documentation aligned with the actual commands and runner.
  Distinguish host checks from other-platform and licensed-provider qualification;
  an explicit skip is not evidence that an external integration passed.
