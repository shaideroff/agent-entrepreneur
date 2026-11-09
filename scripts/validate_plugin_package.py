#!/usr/bin/env python3
"""Validate the Agent Entrepreneur Skills-only Plugin and prove deterministic packaging."""
from __future__ import annotations

import hashlib
import json
import re
import stat
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "agent-entrepreneur"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def safe_relative(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or value != value.strip():
        fail(f"invalid package path: {value!r}")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts or "\\" in value:
        fail(f"unsafe package path: {value!r}")
    resolved = (root / candidate).resolve()
    if root.resolve() not in resolved.parents:
        fail(f"package path escapes root: {value!r}")
    if not resolved.exists() or not resolved.is_file():
        fail(f"declared file is missing: {value!r}")
    return resolved


def validate_tree(root: Path) -> dict[str, int]:
    manifest_dir = root / ".codex-plugin"
    manifest_path = manifest_dir / "plugin.json"
    if not manifest_path.is_file():
        fail("missing .codex-plugin/plugin.json")
    manifest_dir_entries = sorted(p.name for p in manifest_dir.iterdir())
    if manifest_dir_entries != ["plugin.json"]:
        fail(".codex-plugin must contain plugin.json only")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for field in ("name", "version", "description", "skills", "interface"):
        if field not in manifest:
            fail(f"manifest missing {field}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest["name"]):
        fail("plugin name must be kebab-case")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
        fail("plugin version must be strict semver")
    interface = manifest["interface"]
    required_fields = ("displayName", "shortDescription", "longDescription", "developerName", "category", "websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL", "composerIcon", "logo")
    for field in required_fields:
        if not interface.get(field):
            fail(f"interface missing {field}")
    if len(interface["displayName"]) > 30:
        fail("displayName exceeds 30 characters")
    if len(interface["shortDescription"]) > 30:
        fail("shortDescription exceeds 30 characters")
    if len(interface["longDescription"]) > 4000:
        fail("longDescription exceeds 4000 characters")
    if len(interface["developerName"]) > 80:
        fail("developerName exceeds 80 characters")
    categories = {"Productivity", "Creativity", "Developer Tools", "Business & Operations", "Data & Analytics", "Communication", "Education & Research", "Security", "Finance", "Healthcare", "Travel", "Entertainment", "Other"}
    if interface["category"] not in categories:
        fail("unsupported directory category")
    def luminance(color: str) -> float:
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    for field, background in (("brandColor", "#FFFFFF"), ("brandColorDark", "#212121")):
        color = interface.get(field)
        if color is not None:
            if not isinstance(color, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
                fail(f"{field} must be a six-digit hex color")
            high, low = sorted((luminance(color), luminance(background)), reverse=True)
            if (high + 0.05) / (low + 0.05) < 2.0:
                fail(f"{field} must have at least 2:1 contrast against {background}")
    for field in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        value = interface[field]
        parsed = urlparse(value)
        if len(value) > 1024 or parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            fail(f"{field} must be a public HTTPS URL <=1024 characters without embedded credentials")
    for field in ("homepage", "repository"):
        parsed = urlparse(manifest.get(field, ""))
        if parsed.scheme != "https" or not parsed.netloc:
            fail(f"{field} must be a public HTTPS URL")
    if not isinstance(manifest.get("author"), dict) or not manifest["author"].get("name"):
        fail("author.name is required")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities or len(capabilities) > 20:
        fail("capabilities must be a non-empty list containing at most 20 entries")
    if any(not isinstance(x, str) or not x.strip() or len(x) > 120 or "\n" in x or "\r" in x for x in capabilities):
        fail("each capability must be a non-empty one-line string <=120 characters")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts or len(prompts) > 3:
        fail("defaultPrompt must contain one to three prompts")
    normalized_prompts = set()
    for prompt in prompts:
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 128 or "\n" in prompt or "\r" in prompt:
            fail("each defaultPrompt must be a non-empty one-line string <=128 characters")
        if re.search(r"(?<![A-Za-z0-9._%+-])@[A-Za-z0-9_-]+", prompt):
            fail("defaultPrompt must not contain app @mentions")
        normalized = " ".join(unicodedata.normalize("NFKC", prompt).split()).casefold()
        if normalized in normalized_prompts:
            fail("defaultPrompt entries must be unique after Unicode and whitespace normalization")
        normalized_prompts.add(normalized)

    assets = [safe_relative(root, interface["composerIcon"]), safe_relative(root, interface["logo"])]
    for variant in ("assets/logo-light.svg", "assets/logo-dark.svg"):
        assets.append(safe_relative(root, variant))
    for asset in assets:
        try:
            tree = ET.parse(asset)
        except (ET.ParseError, OSError) as exc:
            fail(f"invalid SVG/XML at {asset.relative_to(root)}: {exc}")
        svg = tree.getroot()
        if not svg.tag.endswith("svg"):
            fail(f"asset is not SVG: {asset.relative_to(root)}")
        viewbox = svg.attrib.get("viewBox", "").split()
        try:
            square = len(viewbox) == 4 and float(viewbox[2]) == float(viewbox[3])
        except ValueError:
            square = False
        if not square:
            fail(f"asset must have square numeric viewBox: {asset.relative_to(root)}")
        for node in svg.iter():
            if node.tag.split("}")[-1].lower() in {"script", "image", "foreignobject"}:
                fail(f"unsafe SVG element in {asset.relative_to(root)}")
            for key, value in node.attrib.items():
                if key.lower().endswith("href") and not value.startswith("#"):
                    fail(f"external SVG reference in {asset.relative_to(root)}")

    skills_value = manifest["skills"]
    if not isinstance(skills_value, str) or not skills_value.startswith("./") or ".." in Path(skills_value).parts:
        fail("skills path must be a safe package-relative path")
    skills_dir = (root / skills_value.rstrip("/")).resolve()
    if root.resolve() not in skills_dir.parents or not skills_dir.is_dir():
        fail("skills path must resolve to a directory inside the package")
    skill_entries = sorted(skills_dir.iterdir())
    if not skill_entries or any(not p.is_dir() or p.is_symlink() for p in skill_entries):
        fail("every direct child of skills/ must be a real Skill directory")
    skill_dirs = skill_entries
    skill_names: set[str] = set()
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            fail(f"missing SKILL.md in {skill_dir.name}")
        content = skill_file.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            fail(f"missing YAML frontmatter in {skill_file}")
        end = content.find("\n---", 4)
        if end < 0:
            fail(f"unterminated YAML frontmatter in {skill_file}")
        frontmatter = content[4:end]
        name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.M)
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
        if not name_match or not desc_match:
            fail(f"Skill requires name and description: {skill_file}")
        name = name_match.group(1).strip()
        if name in skill_names:
            fail(f"duplicate Skill name: {name}")
        skill_names.add(name)
        description = desc_match.group(1).strip()
        if not description or len(description) > 1024:
            fail(f"Skill description must be non-empty and <=1024 characters: {skill_file}")
        if len(f"{manifest['name']}:{name}") > 64:
            fail(f"combined plugin and Skill identity exceeds 64 characters: {name}")

    listing = json.loads((root / "submission" / "listing-pack.json").read_text(encoding="utf-8"))
    if listing.get("submissionType") != "skills_only":
        fail("listing pack must identify the Skills-only submission type")
    release_notes = listing.get("releaseNotes")
    if not isinstance(release_notes, str) or not release_notes.strip() or len(release_notes) > 2000:
        fail("listing pack requires release notes of 1-2000 characters")
    availability = listing.get("availabilitySelection")
    if not isinstance(availability, dict) or availability.get("status") not in {
        "pending_owner_selection",
        "selected",
    }:
        fail("listing pack must explicitly track country availability selection")

    cases = json.loads((root / "submission" / "reviewer-cases.json").read_text(encoding="utf-8"))
    positive = cases.get("positive_cases", [])
    negative = cases.get("negative_cases", [])
    if len(positive) < 5 or len(negative) < 3:
        fail("reviewer case pack needs at least five positive and three negative cases")
    for case in positive:
        for field in ("id", "prompt", "expected", "expected_result_shape", "fixture"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                fail(f"positive reviewer case requires non-empty {field}")
    for case in negative:
        for field in ("id", "prompt", "expected", "expected_safe_fallback", "reason"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                fail(f"negative reviewer case requires non-empty {field}")
    for required in ("README.md", "INSTALL.md", "PRIVACY.md", "TERMS.md", "RELEASE-STATUS.md", "BRAND.md"):
        if not (root / required).is_file():
            fail(f"missing release file: {required}")
    for item in root.rglob("*"):
        relative = item.relative_to(root)
        if item.is_symlink():
            fail(f"symlinks are not allowed in the public package: {relative}")
        if item.is_dir() and item.name in {"__pycache__", ".git"}:
            fail(f"transient directory is not allowed in the public package: {relative}")
        if item.is_file():
            if item.name in {".DS_Store", "Thumbs.db"} or item.name.startswith("._"):
                fail(f"operating-system metadata is not allowed: {relative}")
            if item.suffix.lower() in {".pyc", ".pyo"}:
                fail(f"Python bytecode is not allowed: {relative}")
            name = item.name.lower()
            if name in {".npmrc", ".pypirc", "auth.json"} or name.startswith((".env", "credential", "secret")):
                fail(f"secret-shaped file is not allowed: {relative}")
    return {"skills": len(skill_dirs), "positive_cases": len(positive), "negative_cases": len(negative), "assets": len(assets)}


def make_zip(root: Path, destination: Path) -> str:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            relative = path.relative_to(root)
            if any(part in {"__pycache__", ".git"} for part in relative.parts) or path.name == ".DS_Store":
                continue
            if path.is_symlink():
                fail(f"symlink not allowed: {relative}")
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes())
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def main() -> None:
    stats = validate_tree(PLUGIN_ROOT)
    with tempfile.TemporaryDirectory(prefix="agent-entrepreneur-plugin-") as temp:
        temp_path = Path(temp)
        first, second = temp_path / "first.zip", temp_path / "second.zip"
        hash_one = make_zip(PLUGIN_ROOT, first)
        hash_two = make_zip(PLUGIN_ROOT, second)
        if first.read_bytes() != second.read_bytes() or hash_one != hash_two:
            fail("deterministic package builds differ")
        extracted = temp_path / "extracted"
        extracted.mkdir()
        with zipfile.ZipFile(first) as archive:
            archive.extractall(extracted)
        extracted_stats = validate_tree(extracted)
        if extracted_stats != stats:
            fail("clean extraction validation differs from source validation")
        dist_dir = PLUGIN_ROOT.parents[1] / "dist"
        dist_dir.mkdir(parents=True, exist_ok=True)
        artifact = dist_dir / "agent-entrepreneur-1.0.0.zip"
        artifact.write_bytes(first.read_bytes())
        checksum = artifact.with_suffix(".zip.sha256")
        checksum.write_text(f"{hash_one}  {artifact.name}\n", encoding="utf-8")
        print(f"PASS: {stats['skills']} Skills; {stats['positive_cases']} positive and {stats['negative_cases']} negative reviewer cases; {stats['assets']} SVG asset checks")
        print(f"PASS: deterministic ZIP SHA256 {hash_one}")
        print("PASS: fresh extraction revalidated")
        print(f"ARTIFACT: {artifact}")


if __name__ == "__main__":
    main()
