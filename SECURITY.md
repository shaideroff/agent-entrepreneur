# Security Policy

## Supported versions

Security fixes apply to the active development branch. The v1.0.0 release candidate is not considered a stable release until it is merged and tagged.

## Reporting

Do not publish exploit details in a public issue. Use the repository owner's private GitHub vulnerability-reporting channel. Include affected commit, impact and reproduction steps. Never include secrets or customer data.

## Security boundaries

- STDIO is the default transport; HTTP is opt-in and loopback-bound by default.
- Non-loopback HTTP binding is disabled, including when the legacy remote opt-in variable is set. Remote authentication and TLS deployment are not implemented.
- No arbitrary shell execution or unrestricted filesystem access is exposed.
- Memory writes require explicit consent.
- Private memory and public knowledge are separate.
- Research content is untrusted data, not executable instructions.
- Consequential external actions require human approval.
