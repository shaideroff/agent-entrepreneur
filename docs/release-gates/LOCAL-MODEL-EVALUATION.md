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
- The run manifest marks every executed case GENERATED, never REVIEWED_PASS. Workflow success is not evaluation success; truncated output or judge failures block the gate.
- Human review of source fidelity, evidence citations, scope boundaries, transfer assumptions, and hallucination flags remains mandatory before any dossier promotion.
- If the runner fails or a case has no output, the case remains NOT_RUN.

## First completed model run — output generated, quality gate failed

- Run 42719845451 completed successfully at the workflow level and produced an artifact containing all 36 generation records and all 36 cross-model triage records. Artifact SHA-256: 4b8dea866cf2f8dd28789f2c3dc6624c7e7d868751bcbb32a349a8e8151af477.
- Generator digest: d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04. Judge digest: 07bd1f170855240f9e162bf54ea494a8bc1c73d8cbd1365d7fccbeb7d2504947.
- All 36 generation responses reached the 512-token cap. Candidate responses are therefore incomplete/truncated.
- Automated judge outcomes: 3 pass, 11 fail, 22 inconclusive. Eleven judge responses hit the 384-token output cap and returned invalid JSON; other uncertainty included non-exact evidence quotations. One case was flagged for transfer-condition and missing-evidence concerns.
- Therefore workflow execution succeeded, but the model-quality gate failed. These are preliminary automated signals, not human review.
- Corrective change: increase generator output budget to 1,400 tokens and structured-judge budget to 768 tokens; tighten exact-quote instructions and permit whitespace-normalized exact matching only. Re-run all 36 cases before drawing quality conclusions.

## Runtime issue and correction

- Initial run 42719241551 installed Ollama, verified its binary checksum, downloaded both models, then failed on the first Qwen3.5 response because /api/generate returned no visible final answer while the model used its thinking budget.
- Corrected the runner to use /api/chat with the documented top-level think=false setting. Automated tests verify this request shape and require exact evidence quotes from the candidate output.
- The runner checkpoints each generated case and each cross-model judgment so partial work survives a timeout or failure.
- The first test run also exposed a test-import issue (scripts is not a Python package); the test was corrected to load the script with runpy. Latest full CI run 42728723667 passes on Python 3.11 and 3.12.

## Corrective reruns and current run

- Preliminary run 42719845451 generated 36/36 outputs, but every generation response hit the 512-token cap and the automated judge results were unreliable/incomplete (3 pass, 11 fail, 22 inconclusive; 11 invalid-JSON judge responses). This is a failed quality gate, not a pass.
- Corrective run 42920487609 installed Ollama and downloaded both models, then stopped before generation because the exact-quote validator had a Python syntax error. No evaluation artifact was produced by that run.
- The syntax error was fixed in commit `561876b0f4f9a2a740d371b8f57e98f3e2f21e0a`. Current run 42920927913 is executing the full 36-case suite on that commit. At the latest inspection, runtime installation, loopback service startup and both model downloads had passed; the generation/judging step was still in progress.
- The corrected runner uses a 1,400-token generation budget and a 768-token structured-judge budget. Inspect the new artifact for `eval_count`, completion reasons, valid judge JSON, exact quote validation and all 36 case IDs. A workflow-level success is not sufficient.
- Keep all cases GENERATED/NOT REVIEWED until an independent human reviewer has assessed the actual outputs. Do not promote any dossier based on model triage alone.

## Model and runtime references

- Ollama Linux installation and version pinning: https://github.com/ollama/ollama/blob/main/docs/linux.mdx
- Ollama v0.40.14 release and binary checksum: https://github.com/ollama/ollama/releases/expanded_assets/v0.40.14 (Linux amd64 tarball SHA-256: 993e83d08c3d13d17c55009a3e2664c8a25445e644aec3a68bef5abb6abce67d)
- Ollama thinking controls and top-level think API parameter: https://github.com/ollama/ollama/blob/main/docs/capabilities/thinking.mdx
- Qwen3.5 4B Ollama model and Apache-2.0 licence: https://registry.ollama.com/library/qwen3.5%3A4b-q4_K_M
- IBM Granite 3.3 2B Ollama model and Apache-2.0 licence: https://registry.ollama.com/library/granite3.3%3A2b
