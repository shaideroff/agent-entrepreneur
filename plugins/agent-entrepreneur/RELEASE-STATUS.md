# Release status — Agent Entrepreneur Plugin 1.0.0

**Current state: implementation draft; not submission-ready.**

## Completed in this branch

- Skills-only architecture selected to avoid exposing the loopback-only MCP server as a public hosted service.
- Four focused Skills: business diagnosis, market research, decision evaluation, execution planning and outcome review.
- Plugin manifest, README, privacy notice, terms and reviewer test draft.
- Public product boundary states that the host provides reasoning and any live research tools.
- Named entrepreneur profiles and Preview dossiers are not presented as autonomous agents.

## Mandatory remaining gates

1. Re-run the repository's custom package validator and deterministic ZIP build after any package-content change; upload the exact ZIP and resolve the OpenAI portal's own scan findings.
2. Extract a clean package and rerun validation.
3. Smoke-install and test the exact package in supported ChatGPT and Codex surfaces where access is available.
4. Review all Skill content for policy, attribution, privacy and security.
5. Execute and document all five positive and three negative test cases against the exact packaged Skills. OpenAI requires these cases for plugin submissions, including Skills-only submissions; each positive case needs a prompt, expected behavior, expected result shape and reproducible fixture, and each negative case needs a safe expected response and rationale.
6. Confirm the website, support, privacy and terms URLs resolve publicly from the default branch and match the selected verified publisher identity.
7. Verify the individual or business developer identity in OpenAI Platform and confirm the selected organization has submission access (organization owners can submit; other members need Apps Management Write).
8. Upload the exact validated ZIP, review automated metadata and Skill findings, complete required policy attestations, submit for review, and resolve any findings.
9. Publish only after OpenAI approval and an explicit publish action in the portal.

## Not claimed

- GitHub Actions generated a Plugin ZIP and the repository's custom package validator passed on Python 3.11 and 3.12. The archive was built twice per runtime, compared byte-for-byte, extracted to a clean directory and revalidated. The Python 3.11 and 3.12 inner Plugin ZIPs were byte-identical. The current archive SHA256 is recorded in the PR description and release checksum sidecar; rebuild after any package-content change.
- No ChatGPT/Codex app install smoke test has been run. CI clean-extraction validation passed.
- The required five-positive/three-negative case set is prepared but has not been executed against the final packaged Skills. Submission remains blocked until execution evidence and expected result records are complete.
- The user confirmed on 2026-11-10 that OpenAI Platform developer identity verification has not yet been completed.
- No submission, approval or public Plugin Directory publication has occurred.
- The existing Python/MCP server remains a separate product distribution and is not bundled in this Skills-only Plugin.
