"""Generate and validate a deterministic internal Python dependency graph.

Run as a module with --write to refresh docs/architecture-dependencies.json
or --check to validate the committed snapshot. Only statically resolvable
imports inside the application package are included.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

PACKAGE = "agent_entrepreneur"
DEFAULT_SNAPSHOT = Path("docs/architecture-dependencies.json")


def _module_name(source_root: Path, path: Path) -> str:
    parts = list(path.relative_to(source_root).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _is_package_module(module: str) -> bool:
    return module == PACKAGE or module.startswith(PACKAGE + ".")


def _relative_name(package: str, level: int, module: str | None) -> str:
    parts = package.split(".")
    keep = len(parts) - level + 1
    if keep < 0:
        raise ValueError("relative import escapes package")
    prefix = parts[:keep]
    if module:
        prefix.extend(module.split("."))
    return ".".join(prefix)


def _resolve_import(current: str, node: ast.AST, known: set[str], *, is_package: bool) -> set[str]:
    if isinstance(node, ast.Import):
        return {alias.name for alias in node.names if alias.name in known}
    if not isinstance(node, ast.ImportFrom):
        return set()

    package = current if is_package else current.rpartition(".")[0]
    try:
        base = _relative_name(package, node.level, node.module) if node.level else (node.module or "")
    except ValueError:
        return set()

    targets: set[str] = set()
    if base in known:
        targets.add(base)
    for alias in node.names:
        candidate = f"{base}.{alias.name}" if base else alias.name
        if candidate in known:
            targets.add(candidate)
    return targets


def build_graph(repository_root: Path) -> dict[str, Any]:
    source_root = repository_root / "src"
    package_root = source_root / PACKAGE
    if not package_root.is_dir():
        raise FileNotFoundError(f"application package not found: {package_root}")

    files = sorted(package_root.rglob("*.py"))
    module_paths = {_module_name(source_root, path): path for path in files}
    known = set(module_paths)
    edges: set[tuple[str, str]] = set()

    for module, path in module_paths.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            raise ValueError(f"cannot parse module {path}: {exc}") from exc
        for node in ast.walk(tree):
            for target in _resolve_import(module, node, known, is_package=path.name == "__init__.py"):
                if target != module:
                    edges.add((module, target))

    return {
        "schema_version": 1,
        "package": PACKAGE,
        "nodes": [
            {"id": module, "path": path.relative_to(repository_root).as_posix()}
            for module, path in sorted(module_paths.items())
        ],
        "edges": [{"source": source, "target": target} for source, target in sorted(edges)],
    }


def find_dependency_cycles(graph: dict[str, Any]) -> list[list[str]]:
    """Return deterministic, closed paths for statically detected import cycles."""
    adjacency: dict[str, set[str]] = {node["id"]: set() for node in graph["nodes"]}
    for edge in graph["edges"]:
        source, target = edge["source"], edge["target"]
        if source in adjacency and target in adjacency:
            adjacency[source].add(target)

    state: dict[str, int] = {}
    stack: list[str] = []
    cycles: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for target in sorted(adjacency[node]):
            if state.get(target, 0) == 0:
                visit(target)
            elif state.get(target) == 1:
                start = stack.index(target)
                body = stack[start:]
                rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
                canonical = min(rotations)
                if canonical not in seen:
                    seen.add(canonical)
                    cycles.append(list(canonical) + [canonical[0]])
        stack.pop()
        state[node] = 2

    for node in sorted(adjacency):
        if state.get(node, 0) == 0:
            visit(node)
    return sorted(cycles)


def find_import_boundary_violations(graph: dict[str, Any]) -> list[dict[str, str]]:
    """Enforce inward-only dependencies for the domain layer."""
    forbidden_domain_targets = (
        "agent_entrepreneur.agents",
        "agent_entrepreneur.memory",
        "agent_entrepreneur.security",
        "agent_entrepreneur.server",
        "agent_entrepreneur.services",
        "agent_entrepreneur.storage",
        "agent_entrepreneur.workflows",
    )
    violations: list[dict[str, str]] = []
    for edge in graph["edges"]:
        source, target = edge["source"], edge["target"]
        if source.startswith("agent_entrepreneur.domain.") and target.startswith(
            forbidden_domain_targets
        ):
            violations.append({
                "source": source,
                "target": target,
                "rule": "domain_must_not_depend_on_application_or_infrastructure",
            })
    return sorted(violations, key=lambda item: (item["source"], item["target"], item["rule"]))


def architecture_violations(graph: dict[str, Any]) -> list[str]:
    """Format cycle and layer-boundary findings for CI and CLI output."""
    findings = [
        "dependency cycle: " + " -> ".join(cycle)
        for cycle in find_dependency_cycles(graph)
    ]
    findings.extend(
        f"import boundary violation ({item['rule']}): {item['source']} -> {item['target']}"
        for item in find_import_boundary_violations(graph)
    )
    return findings

def render_graph(graph: dict[str, Any]) -> str:
    lines = ["flowchart LR"]
    for node in graph["nodes"]:
        lines.append(f'    {node["id"].replace(".", "_")}["{node["id"]}"]')
    for edge in graph["edges"]:
        source = edge["source"].replace(".", "_")
        target = edge["target"].replace(".", "_")
        lines.append(f"    {source} --> {target}")
    return "\n".join(lines) + "\n"


def snapshot_content(graph: dict[str, Any]) -> str:
    return json.dumps(graph, indent=2, sort_keys=True) + "\n"


def check_snapshot(repository_root: Path, snapshot_path: Path = DEFAULT_SNAPSHOT) -> bool:
    path = repository_root / snapshot_path
    try:
        actual = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    return actual == snapshot_content(build_graph(repository_root))


def write_snapshot(repository_root: Path, snapshot_path: Path = DEFAULT_SNAPSHOT) -> Path:
    path = repository_root / snapshot_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(snapshot_content(build_graph(repository_root)), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if the committed graph is stale")
    mode.add_argument("--write", action="store_true", help="write the current graph snapshot")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    args = parser.parse_args()
    root = Path.cwd()
    if args.write:
        print(f"Updated {write_snapshot(root, args.snapshot)}")
        return 0
    if not check_snapshot(root, args.snapshot):
        print("Architecture dependency snapshot is stale; regenerate it with --write.")
        return 1
    graph = build_graph(root)
    violations = architecture_violations(graph)
    if violations:
        for violation in violations:
            print(f"Architecture violation: {violation}")
        return 1
    print(f"Architecture dependency snapshot is current and policy-clean: {args.snapshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
