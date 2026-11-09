# ChatGPT Plugin submission dossier — Agent Entrepreneur 1.0.0

**Submission type:** Skills only  
**Submission state:** Package validated; not uploaded, submitted, approved or published  
**Package source commit:** ade9ec4788ef443dfa3e4fbe224d3f9ff34296a4  
**Validation workflow:** https://github.com/shaideroff/agent-entrepreneur/actions/runs/42717356538

## Exact validated package

- File: agent-entrepreneur-1.0.0.zip
- Size: 19,771 bytes
- SHA-256: 336b230abba330a73df6a973232e77078ddeaea95b8d76c700b1811482de30b4
- Entries: 16
- Skills: 4
- Positive test cases: 5
- Negative test cases: 3
- SVG assets: 3
- Python 3.11 and 3.12 CI artifacts contain byte-identical inner Plugin ZIPs.

The repository's custom validator passed on Python 3.11 and 3.12. It checks manifest metadata, safe paths, required release documents, SVG safety, Skill frontmatter, reviewer case completeness, excluded files, deterministic ZIP bytes and fresh-extraction validation. The exact ZIP was downloaded from the CI artifact and independently inspected; its internal manifest and case counts match the values above.

## Product boundary

This is a Skills-only package. It contains four reusable founder workflows: business diagnosis, market research, decision evaluation, and execution planning/outcome review. It does not contain an MCP endpoint, a hosted service, autonomous named-person agents, or external action execution. ChatGPT supplies model reasoning and any available research tools.

The Python/MCP server is a separate distribution and is not part of this Plugin ZIP.

## Submission blockers

1. **Publisher identity:** Complete individual or business identity verification in the OpenAI Platform and select the verified identity in the submission form.
2. **Submission permission:** Confirm the submitting account is an organization owner or has Apps Management Write permission.
3. **Execute required test cases:** Run all five positive and three negative cases against the exact final Skill bundle. Record actual outcomes, expected-result comparison, and any fixes. The case definitions are present, but execution evidence is not yet recorded.
4. **Host smoke test:** Install the exact package in a supported ChatGPT and/or Codex surface available to the publisher and verify Skill triggering and behavior. CI validates the package structure; it does not simulate the actual host UI/runtime.
5. **Portal review:** Upload the exact ZIP, complete listing fields and availability, inspect OpenAI's automated Skill scan, resolve findings, and complete policy attestations.
6. **Approval and publication:** Submit for review. Publishing is a separate action available only after approval.

## Listing and policy material

- Listing manifest: plugins/agent-entrepreneur/.codex-plugin/plugin.json
- Listing pack: plugins/agent-entrepreneur/submission/listing-pack.json
- Required test cases: plugins/agent-entrepreneur/submission/reviewer-cases.json
- Privacy notice: plugins/agent-entrepreneur/PRIVACY.md
- Terms: plugins/agent-entrepreneur/TERMS.md
- Support: https://github.com/shaideroff/agent-entrepreneur/issues
- Website/repository: https://github.com/shaideroff/agent-entrepreneur

Privacy and terms files are present on the public default branch. Recheck all public URLs and publisher identity immediately before submission.

## Official requirements reference

OpenAI's current submission guide: https://developers.openai.com/plugins/deploy/submission

The guide permits Skills-only submissions and requires a verified developer/business identity, Apps Management submission access, listing materials, starter prompts, at least five positive and three negative test cases, availability selection, release notes and policy attestations. An MCP endpoint, domain verification and MCP tool metadata are not applicable to this Skills-only architecture.

## Release controls

- Do not claim submitted, approved or published until the portal confirms each state.
- Do not replace the validated ZIP after submission without rebuilding, revalidating and updating the checksum.
- Keep the Plugin version (1.0.0) independent from the Python/MCP server's v1.1 certification work.
