from __future__ import annotations

from pathlib import Path

import pytest

from agent_entrepreneur.architecture_graph import (
    build_graph,
    check_snapshot,
    render_graph,
    snapshot_content,
    write_snapshot,
)

ROOT = Path(__file__).resolve().parents[1]


def test_graph_contains_internal_modules_and_resolved_import_edges() -> None:
    graph = build_graph(ROOT)
    nodes = {node["id"] for node in graph["nodes"]}
    edges = {(edge["source"], edge["target"]) for edge in graph["edges"]}

    assert "agent_entrepreneur.server" in nodes
    assert "agent_entrepreneur.services.core" in nodes
    assert ("agent_entrepreneur.server", "agent_entrepreneur.services.core") in edges
    assert all(source in nodes and target in nodes for source, target in edges)


def test_graph_excludes_external_imports_and_unresolved_symbols() -> None:
    graph = build_graph(ROOT)
    nodes = {node["id"] for node in graph["nodes"]}

    assert nodes
    assert all(node.startswith("agent_entrepreneur") for node in nodes)
    assert all(edge["target"] in nodes for edge in graph["edges"])
    assert not any(edge["target"].startswith(("mcp.", "pydantic.")) for edge in graph["edges"])


def test_graph_is_deterministic_and_rendered_as_mermaid() -> None:
    graph = build_graph(ROOT)

    assert graph == build_graph(ROOT)
    rendered = render_graph(graph)
    assert rendered.startswith("flowchart LR\n")
    assert "agent_entrepreneur_server" in rendered


def test_snapshot_write_and_check_round_trip(tmp_path: Path) -> None:
    snapshot = tmp_path / "graph.json"
    write_snapshot(ROOT, snapshot)
    assert check_snapshot(ROOT, snapshot)
    assert snapshot.read_text(encoding="utf-8") == snapshot_content(build_graph(ROOT))


def test_snapshot_check_detects_stale_and_missing_files(tmp_path: Path) -> None:
    snapshot = tmp_path / "stale.json"
    assert not check_snapshot(ROOT, snapshot)
    snapshot.write_text('{"nodes": [], "edges": []}\n', encoding="utf-8")
    assert not check_snapshot(ROOT, snapshot)


def test_invalid_python_source_fails_with_file_context(tmp_path: Path) -> None:
    package = tmp_path / "src" / "agent_entrepreneur"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "broken.py").write_text("def broken(:\n", encoding="utf-8")

    with pytest.raises(ValueError, match="cannot parse module"):
        build_graph(tmp_path)


def test_dependency_cycle_detector_reports_closed_cycle() -> None:
    from agent_entrepreneur.architecture_graph import find_dependency_cycles

    graph = {
        "nodes": [{"id": name} for name in ("a", "b", "c", "d")],
        "edges": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "c"},
            {"source": "c", "target": "a"},
            {"source": "c", "target": "d"},
        ],
    }

    assert find_dependency_cycles(graph) == [["a", "b", "c", "a"]]


def test_import_boundary_checker_rejects_domain_dependencies_on_outer_layers() -> None:
    from agent_entrepreneur.architecture_graph import find_import_boundary_violations

    graph = {
        "nodes": [
            {"id": "agent_entrepreneur.domain.models"},
            {"id": "agent_entrepreneur.services.core"},
            {"id": "agent_entrepreneur.storage.database"},
        ],
        "edges": [
            {
                "source": "agent_entrepreneur.domain.models",
                "target": "agent_entrepreneur.services.core",
            },
            {
                "source": "agent_entrepreneur.storage.database",
                "target": "agent_entrepreneur.domain.models",
            },
        ],
    }

    assert find_import_boundary_violations(graph) == [
        {
            "source": "agent_entrepreneur.domain.models",
            "target": "agent_entrepreneur.services.core",
            "rule": "domain_must_not_depend_on_application_or_infrastructure",
        }
    ]
