# Release status — Agent Entrepreneur Plugin 1.0.0

**Current state: implementation draft; not submission-ready.**

## Completed in this branch

- Skills-only architecture selected to avoid exposing the loopback-only MCP server as a public hosted service.
- Four focused Skills: business diagnosis, market research, decision evaluation, execution planning and outcome review.
- Plugin manifest, README, privacy notice, terms and reviewer test draft.
- Public product boundary states that the host provides reasoning and any live research tools.
- Named entrepreneur profiles and Preview dossiers are not presented as autonomous agents.

## Mandatory remaining gates

1. Run the Plugin Autopilot analyzer, validator, directory pack builder and deterministic ZIP build twice.
2. Extract a clean package and rerun validation.
3. Smoke-install and test the exact package in supported ChatGPT and Codex surfaces where access is available.
4. Review all Skill content for policy, attribution, privacy and security.
5. Execute the repository's five-positive/three-negative golden-case suite as an internal product-quality gate; these are not MCP reviewer requirements for this Skills-only package under the current OpenAI submission guidance.
6. Confirm the website, support, privacy and terms links resolve from the default branch and accurately identify the publisher. These URLs are included as good public practice; current guidance makes the four URLs mandatory for MCP review, not Skills-only submission.
7. Verify the individual or business developer identity in OpenAI Platform and confirm the selected organization has submission access (organization owners can submit; other members need Apps Management Write).
8. Upload the exact validated ZIP, review automated metadata and Skill findings, complete required policy attestations, submit for review, and resolve any findings.
9. Publish only after OpenAI approval and an explicit publish action in the portal.

## Not claimed

- GitHub Actions generated a Plugin ZIP and the repository's custom package validator passed on Python 3.11 and 3.12. The archive was built twice per runtime, compared byte-for-byte, extracted to a clean directory and revalidated. The Python 3.11 and 3.12 inner Plugin ZIPs were byte-identical. The current archive SHA256 is recorded in the PR description and release checksum sidecar; rebuild after any package-content change.
- No ChatGPT/Codex app install smoke test has been run. CI clean-extraction validation passed.
- The internal golden-case QA suite has not been executed; it is retained as additional quality evidence, not a mandatory MCP review pack for this Skills-only package.
- The user confirmed on 2026-11-10 that OpenAI Platform developer identity verification has not yet been completed.
- No submission, approval or public Plugin Directory publication has occurred.
- The existing Python/MCP server remains a separate product distribution and is not bundled in this Skills-only Plugin.
