# Security Policy

## Supported Versions

Each package versions independently (see the
[README](./README.md#releases-and-roadmap)). The latest `1.x` release of each
package is supported with security updates; earlier releases are not:

| Package | Supported versions |
|---|---|
| `@nvidia/gui-icons` | latest `1.x` |
| `@nvidia/react-gui-icons` | latest `1.x` |
| `@nvidia/micro-gui-icons` | latest `1.x` |
| `@nvidia/react-micro-gui-icons` | latest `1.x` |

## Reporting a Vulnerability

NVIDIA is dedicated to the security and trust of our software products and
services, including all source code repositories managed through our
organization.

**Please do not report security vulnerabilities through GitHub.** If a
potential security issue is inadvertently reported via a public issue or pull
request, NVIDIA maintainers may limit public discussion and redirect the
reporter to the appropriate private disclosure channels below.

To report a potential security vulnerability in any NVIDIA product,
including these packages:

- **Web:** [Security Vulnerability Submission Form](https://www.nvidia.com/object/submit-security-vulnerability.html)
- **E-Mail:** psirt@nvidia.com
    - We encourage you to use the following PGP key for secure email
      communication: [NVIDIA public PGP Key for communication](https://www.nvidia.com/en-us/security/pgp-key)
    - Please include:
        - Package name(s) and version(s) affected
        - Type of vulnerability (code execution, denial of service, etc.)
        - Instructions to reproduce the vulnerability
        - Proof-of-concept or exploit code, if available
        - Potential impact of the vulnerability, including how an attacker
          could exploit it

While NVIDIA currently does not have a bug bounty program, we do offer
acknowledgement when an externally reported security issue is addressed under
our coordinated vulnerability disclosure policy. Visit our
[Product Security Incident Response Team (PSIRT)](https://www.nvidia.com/en-us/security/psirt-policies/)
policies page for more information.

Machine-readable contact info per [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116)
is published at [`/.well-known/security.txt`](./.well-known/security.txt).

## Response SLA

Security response is handled best-effort (see [SUPPORT.md](./SUPPORT.md)).
The targets below are what we aim for, not a contractual guarantee:

- **Initial acknowledgment:** best-effort within 2 business days
- **Status update:** best-effort within 10 business days
- **Disclosure policy:** coordinated disclosure; we request an embargo period
  before any public CVE or public disclosure to allow time for a fix to be
  prepared and released.

## Scope

These packages distribute SVG icon assets and React inline SVG components.
They have no runtime network dependencies, no authentication, and no server
components. The most likely security concerns are:

- Malicious SVG content embedded in icon assets
- Supply-chain attacks on devDependencies used at build time
- Inadvertent leakage of internal infrastructure references

We do not consider icon visual design bugs (wrong shape, wrong color) to be
security issues.
