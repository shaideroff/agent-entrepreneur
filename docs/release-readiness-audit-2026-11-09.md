# Global Public-Use Readiness Audit

**Repository:** `shaideroff/agent-entrepreneur`  
**Audit date:** 9 November 2026  
**Audited baseline:** `dafb8f61b1db41b72e34f839a2a96703bb291209`  
**Audit type:** Repository and public-release readiness review  
**Decision:** **Not yet certified for global production use.** The current repository is a useful local-first MCP foundation with passing CI evidence, but public release certification requires the product implementation and client/security validation gates below.

## Executive assessment

Agent Entrepreneur is a Python MCP server and structured entrepreneurial workflow foundation. It is not yet a finished global entrepreneur experience-agent platform. The distinction matters: MCP protocol tests prove server interoperability at the protocol layer; they do not prove that Codex, Claude, Cursor or another host has been tested end-to-end, nor that the named entrepreneur agents described in the v1.1 design are implemented.

The public repository has no GitHub Release published at the audited baseline. The package metadata reports version 1.0.0, but a package version alone is not a stable-release artefact. Keep the release status explicit until a versioned tag, release notes, distribution artefacts and release checks are complete.

## Verified repository facts

| Area | Audited state | Evidence |
|---|---|---|
| Repository visibility | Public GitHub repository | Repository metadata |
| Licence | Apache-2.0 | Repository metadata and LICENSE |
| Package | Python package, Python 3.11+ | `pyproject.toml` |
| MCP server | FastMCP server with STDIO default and configured HTTP transport | `src/agent_entrepreneur/server.py`, `config.py` |
| Core business tools | Six: understand, research, analyse, evaluate, plan, review | Server tool registrations |
| Specialist workflow tools | Plan, complete and resume | Server tool registrations |
| Knowledge/memory tools | Entrepreneur search; save, search and delete memory | Server tool registrations |
| MCP resources | Specialist catalogue and entrepreneur catalogue | Server resource registrations |
| MCP prompts | Business diagnosis, market entry assessment and founder execution review | Server prompt registrations |
| Local persistence | SQLite-backed memory/checkpoint state | Storage and memory modules |
| Consent boundary | Memory writes require explicit consent | `save_memory` tool |
| Model boundary | Connected MCP client performs reasoning; server validates and structures work | Server instructions and workflow responses |
| Remote HTTP | Loopback-only; not production remote hosting | Configuration and security docs |
| v1.1 named-agent layer | Not implemented at audited baseline | No experience-agent models, dossier registry, direct-agent runtime or Lead/Council MCP tools in repository tree |
| GitHub Release | None published at audited baseline | Releases API returned an empty list |

## CI evidence

The documentation PR #11 completed these repository workflows successfully:

- Python 3.11 and 3.12 CI, including Ruff, mypy, pytest and architecture graph check.
- Package build, metadata validation, clean installation, CLI smoke test and real MCP STDIO smoke test on Python 3.11 and 3.12.
- MCP protocol integration on the pinned SDK 1.9.0 and the workflow's latest-SDK job.
- Dependency vulnerability inventory and licence inventory.
- Git-history secret scan.

These results are valuable, but they are evidence for the repository commit and the checks listed—not a penetration test, formal security certification, cross-platform test matrix, or third-party host certification.

## Release blockers

### P0 — Implement the product promised by v1.1

The v1.1 design and implementation plan describe a named experience-agent platform, but the audited source tree contains only generic specialist disciplines and the existing workflow orchestrator. The named agents, versioned dossier contracts, dossier registry, Lead Entrepreneur selection, Expert Council lifecycle and their MCP tools are not present.

Required deliverables:

1. Versioned Pydantic contracts for agents, dossiers, claims, responses, selection and council synthesis.
2. A 12-entry stable catalogue; incomplete dossiers remain Preview and cannot be selected for active work.
3. Sourced pilot dossiers with claim-level provenance, counter-evidence, failure cases, transfer conditions and limitations.
4. Direct named-agent work packets that clearly identify the connected-client reasoning boundary.
5. Neutral Lead Entrepreneur selection with a bounded council and transparent selection rationale.
6. Expert Council independent contributions, challenge round, synthesis and preserved disagreement.
7. Additive MCP tools only; preserve every v1.0 tool name, schema and behavior.
8. Deterministic tests for dossier integrity, evidence references, preview gating, workflow resume and impersonation safeguards.

**Public representation rule:** The public entrepreneur directory should describe people naturally and professionally. It must not blanket-label a whole person “unverified.” Internally, founder-supplied or other first-party material must be attributed at claim level and must not be represented as independent corroboration. This distinction applies to every dossier, including S Haider's.

### P0 — Certify MCP client interoperability

The client setup guide documents Codex, Claude Code, Claude Desktop and Cursor, but these are setup targets—not verified integrations.

For each client, maintain a reproducible test record containing client version, OS, Python/package version, MCP SDK version, date and results for:

- Server startup and handshake.
- Tools, resources and prompts discovery.
- All core tools and representative specialist workflows.
- Structured result handling and tool error behavior.
- Approval/consent behavior for memory writes.
- Workflow checkpoint/resume and server restart.
- Unicode, long inputs, malformed inputs and timeout behavior.

Add client-specific automated or repeatable smoke tests where feasible. Keep status at “runtime verification pending” until evidence exists. Expand to VS Code, Windsurf, Gemini CLI and other clients only after the first four clients are tested.

### P0 — Keep remote deployment disabled until secured

Do not expose the current loopback HTTP transport publicly. A production remote MCP service needs a separate security design and implementation, including authentication/authorization, OAuth 2.1 resource-server considerations where applicable, TLS termination, rate limits, audit events, tenant/data isolation, secret management, abuse controls, operational monitoring, incident response and threat-model review. Add negative tests for unauthorized access and cross-user data isolation before any remote launch.

### P1 — Public package and release hygiene

Before stable v1.0.0 or v1.1 publication:

- Publish a Git tag and GitHub Release matching the package version.
- Attach reproducible wheel and source distributions and verify hashes.
- Document supported operating systems and tested Python versions.
- Keep dependency constraints aligned with the actual MCP SDK compatibility matrix. Do not widen a major-version range solely because a “latest” test job passes.
- Add an SBOM or retain the generated licence/dependency inventory as a release artefact.
- Publish support, vulnerability disclosure and deprecation policies.
- Review public repo description, topics, installation instructions and contribution guidance.
- Confirm all public claims match implemented functionality.

### P1 — Operational and privacy readiness

- Document SQLite file location, permissions, backup, restore, retention and deletion behavior.
- Test concurrent access and corruption recovery.
- Define memory scope/tenant semantics before multi-user or hosted deployment.
- State clearly that SQLite memory is local and not application-encrypted.
- Review log redaction and avoid storing credentials, sensitive personal data or unnecessary raw prompts.
- Test malicious/untrusted source material and prompt-injection handling end-to-end.

## Client compatibility status

| Client | Setup guide | Live end-to-end verification |
|---|---|---|
| OpenAI Codex CLI / IDE | Documented | Pending |
| Claude Code | Documented | Pending |
| Claude Desktop | Documented | Pending |
| Cursor | Documented | Pending |
| ChatGPT MCP hosts | Host-dependent notes | Pending |
| VS Code, Windsurf, Gemini CLI and others | Future targets | Not assessed |

MCP protocol compatibility is necessary but insufficient for client certification. Do not advertise a client as “supported” without a named tested version and reproducible evidence.

## Release gates

A release can be called **Local MCP Preview** when package install, STDIO handshake, tool discovery, core tests, memory consent, documentation and local security boundaries pass.

A release can be called **Global Client-Compatible Release Candidate** only when the first four priority clients have reproducible runtime results, the named-agent features advertised in that release are implemented, the security review is complete for the deployment mode, and all CI/package checks pass.

A release can be called **Production Remote MCP** only after remote authentication, authorization, isolation, TLS, abuse controls, operational controls and independent security review pass. The current code is not at this gate.

## Audit limitations

This audit used the public repository tree, source files, configuration, documentation, GitHub metadata and completed GitHub Actions results. It did not execute an independent local clone, run a penetration test, install the package on physical Windows/macOS/Linux machines, or connect a live Codex/Claude/Cursor client. Those checks remain explicitly open.

## Recommended execution order

1. Implement v1.1 contracts, evidence-gated catalogue and pilot dossier infrastructure.
2. Add direct agent, Lead Entrepreneur and Expert Council MCP tools with compatibility regression tests.
3. Add deterministic agent evaluation sets and public documentation.
4. Run client integration tests for Codex, Claude Code, Claude Desktop and Cursor.
5. Complete local privacy/security hardening and a separate remote MCP threat model.
6. Publish a tagged release only when the relevant release gates pass.

**Audit conclusion:** Keep the existing MCP foundation. Do not rebrand documentation work as product completion. Build the named-agent layer additively, certify each client with evidence, and keep remote hosting disabled until it is secure.
