# Security Policy: NVMesh Documentation

This repository contains versioned product documentation, including operator guides,
REST API reference pages, release notes, kernel architecture notes, images, and
performance data. It does not contain a deployed service.

## Reporting a Vulnerability

If you discover a potential security vulnerability in this repository or in the
documented product behavior, **do not open a public issue, merge request, pull
request, or discussion.**

Report it privately through one of these channels:

- **Preferred:** [NVIDIA Vulnerability Disclosure Program](https://www.nvidia.com/en-us/security/)
- **Email:** [psirt@nvidia.com](mailto:psirt@nvidia.com). For sensitive reports,
  use the [NVIDIA public PGP key](https://www.nvidia.com/en-us/security/pgp-key).
- **Repository private reporting:** Use the repository's **Security** tab and
  private vulnerability reporting feature, when available.

Include:

- The project name and affected document version, branch, or commit
- The vulnerability type and affected product component or documentation file
- Step-by-step reproduction instructions
- Proof-of-concept material, if available and safe to share privately
- The expected and observed behavior
- An impact assessment and any suggested remediation

Detailed reports help NVIDIA evaluate and address issues faster. NVIDIA PSIRT will
acknowledge the report, validate the issue and assess its severity, coordinate and
test a fix, and publish a security bulletin when appropriate.

## Security Architecture & Context

NVMesh Documentation is a static documentation and data repository for a
distributed storage product. The primary artifacts are Markdown operator guides,
self-contained HTML REST API references, a CLI guide, kernel architecture notes,
images, a document file, and a performance-results data file. The repository
itself has no network listener, authentication implementation, database, or
runtime secret store.

Its primary security responsibility is to provide accurate, non-sensitive, and
integrity-protected operational guidance. The documentation describes privileged
installation and administration commands, REST and CLI interfaces, certificate
configuration, storage networking, kernel parameters, and recovery procedures.
Errors or unauthorized changes can therefore affect the confidentiality,
integrity, or availability of systems operated from these instructions.

**Repository Exposure Classification:** Public.
Basis: user-confirmed public visibility; this document is written to public-safe
detail even though the source checkout is hosted on a non-public forge.

**Service Exposure Classification:** Internal-Isolated (high confidence).
Basis: user-confirmed classification; this checkout contains static documentation
artifacts, with no live service or production deployment configuration.

### Security Boundaries and Interfaces

- **Contributors and reviewers to published artifacts:** Markdown, HTML, images,
  document files, and CSV data become trusted guidance after repository review.
- **Documentation to operator workstations:** Markdown renderers, browsers, and
  office applications consume repository artifacts, including self-contained HTML
  with bundled JavaScript.
- **Documentation to managed systems:** Administrators may execute commands from
  the User Guide and CLI Guide with elevated privileges or submit documented REST
  operations to a management endpoint.
- **Documentation to external dependencies:** Installation examples reference
  package repositories, signing keys, operating-system packages, and third-party
  setup scripts whose authenticity and availability are outside this repository.
- **Documentation to product implementation:** Architecture and API descriptions
  summarize behavior implemented elsewhere. This repository cannot enforce that
  deployed software matches the documented version or security controls.

## Threat Model

The following scenarios are the primary security concerns for this repository,
ordered by likely impact:

1. **Compromised operational instructions:** Unauthorized or insufficiently
   reviewed changes to the User Guide, CLI Guide, or module-parameter guides could
   persuade an administrator to run harmful commands with elevated privileges,
   weaken host protections, or alter storage availability.
2. **Unverified software installation:** Installation sections include commands
   that consume remote setup scripts and examples that disable package-signature
   checks. If followed without independent verification, a compromised download
   source or network path could introduce untrusted software.
3. **Unsafe credential examples:** The REST reference and deployment examples
   contain recognizable sample usernames and passwords. Readers could mistake
   placeholders for acceptable production credentials, expose credentials through
   command history or configuration URLs, or retain weak example values.
4. **Active-content artifact risk:** The versioned REST API references are
   self-contained HTML files with bundled JavaScript libraries. If a generated
   artifact is tampered with or rendered from an untrusted contribution, opening
   or publishing it can execute unexpected browser-side content.
5. **Sensitive-information publication:** Product topology, administrative
   interfaces, certificate handling, diagnostics, and release information are
   documented in detail. A future update could accidentally add private
   endpoints, live credentials, customer data, or non-public operational details
   to a world-readable artifact or embedded file metadata.
6. **Version and control drift:** This repository carries multiple API and hotfix
   artifacts alongside architecture notes derived from implementation source.
   Stale guidance can cause operators to use obsolete authentication,
   certificate, package, or recovery procedures against a different software
   release.
7. **Dangerous diagnostic settings:** The module-parameter documentation includes
   writable debug and test controls that can bypass normal I/O or locking
   behavior. Applying those controls outside an isolated test environment could
   cause data loss, corruption, or service interruption.

## Critical Security Assumptions

- Repository changes, generated HTML, binary documents, images, and data files are
  reviewed for integrity, active content, secrets, personal data, and non-public
  metadata before publication.
- Operators treat all credentials, hostnames, URLs, certificate names, and keys in
  examples as placeholders and supply unique values through approved secret
  handling mechanisms.
- Administrators verify package signatures, signing-key fingerprints, download
  sources, and script contents before executing installation commands, especially
  commands run with elevated privileges.
- Privileged, destructive, recovery, and debug commands are tested against the
  exact product version in an isolated environment before production use.
- Downstream Markdown, HTML, document, and CSV viewers enforce their own content
  isolation and remain patched; this repository does not sandbox rendered
  artifacts.
- Runtime authentication, authorization, transport security, audit logging,
  certificate validation, and storage integrity are enforced by the deployed
  product and infrastructure, not by this documentation repository.
- Publishers and operators confirm that the selected branch and artifact version
  match the software being documented or administered.

## Supported Versions

Security corrections should be applied to documentation branches that correspond
to product versions still receiving support. Reporters should identify the
affected branch or commit so maintainers can determine which maintained versions
require an update.

## Documentation Security Guidance

- Prefer signed packages and authenticated package sources; do not normalize
  examples that disable verification.
- Use obvious placeholders and avoid realistic default passwords, private
  endpoints, access tokens, private keys, or customer identifiers.
- Avoid shell pipelines that execute freshly downloaded content. When unavoidable,
  document checksum or signature verification before execution.
- Regenerate and review REST HTML after source changes, and inventory bundled
  browser libraries for maintained versions.
- Clearly label destructive, debug-only, alpha, and non-production procedures,
  including prerequisites and rollback expectations.
- Review generated and binary artifacts separately because ordinary text diffs may
  not reveal embedded scripts, metadata, links, or unexpected content.
