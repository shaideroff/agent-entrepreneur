from __future__ import annotations

import json
from pathlib import Path

import scripts.architecture_graph as architecture_graph


ROOT = Path(__file__).resolve().parents[1]


def test_graph_contains_internal_modules_and_resolved_import_edges() -> None:
    graph = architecture_graph.build_graph(ROOT)
    nodes = {node["id"] for node in graph["nodes"]}
    edges = {(edge["source"], edge["target"]) for edge in graph["edges"]}

    assert "agent_entrepreneur.server" in nodes
    assert "agent_entrepreneur.services.core" in nodes
    assert ("agent_entrepreneur.server", "agent_entrepreneur.services.core") in edges
    assert all(edge["source"] in nodes and edge["target"] in nodes for edge in graph["edges"])


def test_graph_excludes_external_and_unresolved_imports() -> None:
    graph = architecture_graph.build_graph(ROOT)
    nodes = {node["id"] for node in graph["nodes"]}

    assert all(node.startswith("agent_entrepreneur.") for node in nodes)
    assert all(edge["source"] in nodes and edge["target"] in nodes for edge in graph["edges"])


def test_graph_output_is_deterministic_and_rendered_mermaid_is_valid_shape() -> None:
    first = architecture_graph.build_graph(ROOT)
    second = architecture_graph.build_graph(ROOT)

    assert first == second
    rendered = architecture_graph.render_graph(first)
    assert "flowchart LR" in rendered
    assert "agent_entrepreneur.server" in rendered


def test_graph_snapshot_check_fails_when_document_is_stale(tmp_path: Path) -> None:
    graph = architecture_graph.build_graph(ROOT)
    snapshot = tmp_path / "graph.json"
    snapshot.write_text('{"nodes": [], "edges": []}\n', encoding="utf-8")

    assert snapshot.read_text(encoding="utf-8") != json.dumps(graph, indent=2, sort_keys=True) + "\n"
