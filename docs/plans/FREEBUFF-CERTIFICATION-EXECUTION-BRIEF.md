# Freebuff execution brief — v1.1 certification

## Objective

Prepare `agent-entrepreneur` for a defensible global stable release using free, included-model capacity only. Do not purchase credits, call paid APIs, or add paid service dependencies. Work only on `release/v1.1-certification-prep`; do not modify `main`, the existing public development release, or published tags.

## Current verified baseline

- Repository: `shaideroff/agent-entrepreneur`
- Baseline commit: `23f530855ba3060c061c6fa38f3c7f0766e8d054`
- Six pilot dossiers: `built_from_zero`, `sara_blakely`, `jeff_bezos`, `warren_buffett`, `jensen_huang`, `brian_chesky`.
- Existing `tests/evaluations/experience_agents/pilot_eval_cases.json` defines 36 deterministic structural cases (six scenarios per dossier). Its own boundary explicitly says generative response quality still needs a separately governed host/model evaluation.
- Existing tests assert schema/structure, not real generated answers.
- The six experience-agent MCP tools are registered in `src/agent_entrepreneur/server.py`.
- Latest baseline push checks on the baseline commit passed: CI, package verification, MCP protocol compatibility and security audit.
- No stable GitHub Release is currently published. Keep the public preview/development state and all six pilot dossiers at Preview.

## Non-negotiable operating rules

1. No paid API keys, paid credits, billing activation, or services that require payment.
2. Do not expose, print, commit, or request secrets, tokens, personal data, or private repository contents. Never place credentials in prompts or files.
3. Do not invent model outputs, evaluation scores, third-party test results, or security findings.
4. Every generated evaluation record must include provider/model identifier, model version if exposed, UTC timestamp, prompt-template version/hash, dossier version/hash, raw output, evaluator identity/method, rubric scores, evidence, and limitations.
5. Separate generation from judging. Prefer a different model for judging; if that is unavailable, use blinded human review and explicitly disclose the limitation. Do not call same-model self-grading independent.
6. Preserve disagreements and uncertainty. No named entrepreneur impersonation, first-person simulation, private knowledge claims, or implied endorsement.
7. Treat dossier facts as sourced claims. Reject unsupported citations and keep fact, interpretation, and recommendation distinct.
8. Do not promote any pilot from Preview or claim global production readiness until all release gates have evidence.
9. Keep changes small, reviewable, tested, and committed to this branch. Open a draft PR; do not merge it.

## Workstream A — real-model pilot evaluation

- Convert the existing 36 structural cases into executable, dossier-specific prompts. Generic scenario descriptions alone are insufficient.
- For each of the six dossiers, run all six scenarios: in-domain, out-of-domain, transfer mismatch, contradictory evidence, missing sources, and impersonation attempt.
- Use only Freebuff's included free models. Check the current model-specific data-use notice before submitting repository content. Do not assume all models have the same retention/training terms.
- Save exact prompts and unmodified model outputs under a clearly named, git-ignored or explicitly approved evaluation-artifact location. Do not commit raw outputs by default if the model terms or user privacy make publication inappropriate.
- Build a deterministic evaluator/report generator. Score each required trait with evidence spans and a pass/fail/uncertain result. Add rubric dimensions for factual grounding, citation integrity, scope discipline, transfer reasoning, counter-evidence, safety, and actionable clarity.
- Add a manifest with run metadata and hashes. Missing outputs must remain marked NOT RUN, never be scored as passes.
- Produce an aggregate report showing per-dossier and per-scenario results, confidence/limitations, and unresolved blockers. Do not invent a minimum pass threshold; propose one with rationale and document it for human approval.

## Workstream B — MCP tool end-to-end validation

Test all six tools through a real MCP client over STDIO, not only by importing functions:
- `discover_experience_agents`
- `get_experience_agent_profile`
- `recommend_experience_agent_council`
- `prepare_experience_agent_council_work`
- `prepare_experience_agent_work_packet`
- `synthesize_experience_agent_council`

Cover valid calls, empty/boundary/oversized inputs, invalid identifiers/statuses, unknown IDs, malformed contributions, disagreement preservation, prompt-injection/untrusted content, and deterministic repeatability. Capture client transcript, protocol version, tool schemas, exit status, and redacted logs.

## Workstream C — third-party client interoperability

- Identify currently available free clients that support MCP STDIO (and HTTP only if the repository actually supports it).
- Validate the documented install/configuration path in at least two independent clients where feasible.
- Verify tool discovery, schema compatibility, successful invocation, error propagation, cancellation/timeout behavior, and clean shutdown.
- Record exact client and version. If a client cannot be tested in the available environment, mark NOT RUN with the blocker; do not infer compatibility.

## Workstream D — security, privacy, recovery, performance

- Review trust boundaries, prompt injection handling, path traversal, unsafe deserialization, command execution, local network exposure, data retention, consent, memory deletion, backup/restore, and dependency/supply-chain risks.
- Exercise backup/restore against a disposable test database and verify integrity after recovery.
- Test loopback binding and ensure no unintended public listener or unauthenticated remote surface exists.
- Run bounded load/latency tests for directory/profile/council tools. Report environment, sample count, p50/p95, errors and resource constraints. Do not claim production-scale load validation from small local tests.
- Classify findings by severity, reproducibility, exploit preconditions, impact, and remediation. Do not make unsupported security-certification claims.

## Workstream E — release engineering

- Reconcile `pyproject.toml`, package metadata, changelog, docs, plugin metadata, and version policy.
- Preserve the current public development release. Prepare stable release notes and reproducible build instructions without publishing a release.
- Verify deterministic package builds by rebuilding twice and comparing hashes.
- Verify source distributions/wheels and Skills-only plugin artifacts, installation, CLI smoke tests, MCP STDIO smoke tests, and clean-environment installs.
- Prepare a signed stable tag plan, but do not create the tag or GitHub Release until all gates pass and the owner explicitly approves.
- Keep ChatGPT Plugin publisher identity verification and portal submission as owner-side pending actions. Do not claim submission or approval.

## Required deliverables

1. Code and tests for repeatable evaluation, MCP integration tests, compatibility tests, and security/recovery/performance checks.
2. Machine-readable raw evaluation records (with appropriate privacy handling), evaluation manifest, and generated report.
3. A release-gate matrix with PASS / FAIL / NOT RUN / BLOCKED and links to reproducible evidence.
4. A concise security and privacy review with actionable findings.
5. Reproducible build artifacts and checksums, attached to CI or PR artifacts where possible.
6. A draft PR against `main`, with all checks green and no stable release publication.

## Completion protocol

Before reporting completion:
- Run the full test suite and all applicable CI workflows.
- Inspect the diff for unrelated changes, secrets, generated clutter, and misleading claims.
- Verify every reported result against a saved log or artifact.
- List all NOT RUN and BLOCKED items explicitly.
- Stop before merge, tag, release publication, or external submission.

Start by inspecting the current branch and existing implementation. Do not rewrite working modules without demonstrating a defect. Prefer tests and minimal fixes before refactors.
