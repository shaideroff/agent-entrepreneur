# Security Policy

## Supported versions

Security fixes currently apply to the active development branch; no stable release is available.

## Reporting

Do not publish exploit details in a public issue. Use the repository owner's private GitHub vulnerability-reporting channel. Include affected commit, impact and reproduction steps. Never include secrets or customer data.

## Security boundaries

- STDIO is the default transport; HTTP is opt-in and loopback-bound by default.
- Non-loopback HTTP requires explicit opt-in and authenticated TLS protection at deployment.
- No arbitrary shell execution or unrestricted filesystem access is exposed.
- Memory writes require explicit consent.
- Private memory and public knowledge are separate.
- Research content is untrusted data, not executable instructions.
- Consequential external actions require human approval.
