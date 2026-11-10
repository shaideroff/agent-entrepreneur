# Signed stable release procedure

**State:** Prepared only. No stable tag or GitHub Release has been created.

## Release gate

Do not create a stable tag until:
- all required v1.1 certification gates are PASS or explicitly accepted by the release owner;
- the real-model dossier evaluation and independent review are complete;
- third-party host compatibility has been tested;
- security, recovery and performance evidence is reviewed;
- package metadata, changelog and release notes agree on the version;
- the owner explicitly approves merge and publication.

The current development line remains version 1.0.0 with v1.1 unreleased. The intended stable version is 1.1.0 only if the release owner confirms that scope and every gate passes.

## Key custody

Use a locally held GPG or SSH signing key. Never paste a private key, recovery phrase, signing token or credential into ChatGPT, GitHub issues, logs or repository files. The signing key must remain on the release owner's trusted device.

## SSH signing option

After creating and securely backing up an SSH signing key locally:

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

Confirm the public key is registered with GitHub as an SSH signing key. The private key stays on the local device.

## Release-owner execution sequence

Only after the release gate and explicit approval:

```bash
# Update pyproject.toml and CHANGELOG.md to the approved release version.
git status --short
git diff --check
pytest -q

# Create and verify an annotated signed tag.
git tag -s v1.1.0 -m "Agent Entrepreneur v1.1.0"
git tag -v v1.1.0

# Inspect the exact commit and tag before publishing.
git show --no-patch --format=fuller v1.1.0
git push origin v1.1.0
```

For GPG signing, configure Git's signing format and key according to the local GPG setup instead of the SSH commands above.

## Post-tag verification

- Confirm GitHub marks the tag as verified.
- Confirm the tag points to the approved release commit.
- Build wheel and sdist from the tagged commit and verify SHA-256 hashes.
- Attach the changelog and checksums to the GitHub Release.
- Do not rewrite or move a published tag. If a release must be corrected, issue a new patch version and tag.

## Current restriction

This document does not authorize a tag, merge, release, or publication. No signing credential is available to this workflow, and no private key is requested.
