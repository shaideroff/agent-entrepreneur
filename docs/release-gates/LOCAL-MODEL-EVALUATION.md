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

## Current run

- Workflow: https://github.com/shaideroff/agent-entrepreneur/actions/runs/42719241551
- State at record creation: generation and cross-model triage job in progress; no results have been accepted.
- A second run may be queued for the subsequent runner hardening commit; compare run manifests and retain only the latest reproducible run for release evidence.

## Model and runtime references

- Ollama Linux installation and version pinning: https://github.com/ollama/ollama/blob/main/docs/linux.mdx
- Ollama v0.40.14 release and binary checksum: https://github.com/ollama/ollama/releases/expanded_assets/v0.40.14
- Qwen3.5 4B Ollama model and Apache-2.0 licence: https://registry.ollama.com/library/qwen3.5%3A4b-q4_K_M
- IBM Granite 3.3 2B Ollama model and Apache-2.0 licence: https://registry.ollama.com/library/granite3.3%3A2b
