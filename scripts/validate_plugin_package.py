#!/usr/bin/env python3
"""Validate the Agent Entrepreneur Skills-only Plugin and prove deterministic packaging."""
from __future__ import annotations

import hashlib
import json
import re
import stat
import tempfile
import zipfile
from pathlib import Path
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
    manifest_dir_files = sorted(p.name for p in manifest_dir.iterdir() if p.is_file())
    if manifest_dir_files != ["plugin.json"]:
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
    required_fields = ("displayName", "shortDescription", "longDescription", "developerName", "category", "websiteURL", "privacyPolicyURL", "termsOfServiceURL", "composerIcon", "logo")
    for field in required_fields:
        if not interface.get(field):
            fail(f"interface missing {field}")
    if len(interface["shortDescription"]) > 30:
        fail("shortDescription exceeds 30 characters")
    if len(interface["longDescription"]) > 4000:
        fail("longDescription exceeds 4000 characters")
    if not isinstance(interface.get("defaultPrompt"), list) or not interface["defaultPrompt"]:
        fail("defaultPrompt must be a non-empty list")

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
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if not skill_dirs:
        fail("no Skill directories found")
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
        if not desc_match.group(1).strip():
            fail(f"empty Skill description: {skill_file}")

    cases = json.loads((root / "submission" / "reviewer-cases.json").read_text(encoding="utf-8"))
    positive = cases.get("positive_cases", [])
    negative = cases.get("negative_cases", [])
    if len(positive) < 5 or len(negative) < 3:
        fail("reviewer case pack needs at least five positive and three negative cases")
    for required in ("README.md", "PRIVACY.md", "TERMS.md", "RELEASE-STATUS.md", "BRAND.md"):
        if not (root / required).is_file():
            fail(f"missing release file: {required}")
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
        print(f"PASS: {stats['skills']} Skills; {stats['positive_cases']} positive and {stats['negative_cases']} negative reviewer cases; {stats['assets']} SVG asset checks")
        print(f"PASS: deterministic ZIP SHA256 {hash_one}")
        print("PASS: fresh extraction revalidated")


if __name__ == "__main__":
    main()
