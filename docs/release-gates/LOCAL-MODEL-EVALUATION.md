# Free local model evaluation — execution record

**Purpose:** Generate real outputs for the 36 pilot dossier/scenario prompts without paid inference APIs or Freebuff credentials.

## Execution design

- Runtime: Ollama v0.40.14, downloaded from the official release and checked against the published SHA-256 before installation.
- Generator: Qwen3.5 4B, Ollama tag qwen3.5:4b, Apache-2.0 model licence.
- Cross-model triage judge: IBM Granite 3.3 2B, Ollama tag granite3.3:2b, Apache-2.0 model licence.
- Environment: GitHub-hosted Ubuntu runner, CPU inference, Ollama bound to loopback only.
- Scope: all 36 prompts across six dossiers and six scenario types.
- Evidence: model outputs, model digests, prompt/dossier hashes, inference metrics, and cross-model triage judgments are written to a short-retention Actions artifact. Raw outputs are not committed to the repository.

## Evidence interpretation

- Generator output is real local model output, not a simulated response.
- Granite triage is a separate model family, but it is automated evaluation—not independent human review.
- The run manifest marks every executed case GENERATED, never REVIEWED_PASS.
- Human review of source fidelity, evidence citations, scope boundaries, transfer assumptions, and hallucination flags remains mandatory before any dossier promotion.
- If the runner fails or a case has no output, the case remains NOT_RUN.

## Runtime issue and correction

- Initial run 42719241551 installed Ollama, verified its binary checksum, downloaded both models, then failed on the first Qwen3.5 response because /api/generate returned no visible final answer while the model used its thinking budget.
- Corrected the runner to use /api/chat with the documented top-level think=false setting. Automated tests verify this request shape and require exact evidence quotes from the candidate output.
- The runner checkpoints each generated case and each cross-model judgment so partial work survives a timeout or failure.
- The first test run also exposed a test-import issue (scripts is not a Python package); the test was corrected to load the script with runpy. Latest full CI run 42720225116 passes on Python 3.11 and 3.12.

## Current run

- Latest workflow: https://github.com/shaideroff/agent-entrepreneur/actions/runs/42720225031
- State at last inspection: queued/pending; GitHub has not created a job yet and no evaluation artifact exists.
- Previous corrected attempt 42719785320 was cancelled before job allocation; it produced no results.
- Do not treat this gate as passed until the latest workflow completes, the manifest contains all 36 records, model digests and outputs are verified, and a human reviewer has examined the cases.
- All dossier statuses remain Preview.

## Model and runtime references

- Ollama Linux installation and version pinning: https://github.com/ollama/ollama/blob/main/docs/linux.mdx
- Ollama v0.40.14 release and binary checksum: https://github.com/ollama/ollama/releases/expanded_assets/v0.40.14 (Linux amd64 tarball SHA-256: 993e83d08c3d13d17c55009a3e2664c8a25445e644aec3a68bef5abb6abce67d)
- Ollama thinking controls and top-level think API parameter: https://github.com/ollama/ollama/blob/main/docs/capabilities/thinking.mdx
- Qwen3.5 4B Ollama model and Apache-2.0 licence: https://registry.ollama.com/library/qwen3.5%3A4b-q4_K_M
- IBM Granite 3.3 2B Ollama model and Apache-2.0 licence: https://registry.ollama.com/library/granite3.3%3A2b
