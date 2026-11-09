"""Bounded local MCP STDIO latency smoke test; not a production load test."""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import sys
import tempfile
import time
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

TOOL_CALLS: list[tuple[str, dict[str, Any]]] = [
    ("discover_experience_agents", {"query": "Built from Zero"}),
    ("get_experience_agent_profile", {"agent_id": "built_from_zero"}),
    ("recommend_experience_agent_council", {"objective": "Evaluate a constrained founder launch."}),
    ("prepare_experience_agent_council_work", {"objective": "Evaluate a constrained founder launch."}),
    ("prepare_experience_agent_work_packet", {"agent_id": "built_from_zero", "objective": "Evaluate a constrained founder launch."}),
    (
        "synthesize_experience_agent_council",
        {
            "objective": "Evaluate a constrained founder launch.",
            "contributions": [
                {"agent_id": "built_from_zero", "recommendations": ["Test demand first."]},
                {"agent_id": "jeff_bezos", "recommendations": ["Build repeatable mechanisms."]},
            ],
            "recommendation": "Run a bounded pilot with explicit decision gates.",
        },
    ),
]


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return round(ordered[index], 3)


async def run_benchmark(iterations: int, database_path: Path) -> dict[str, Any]:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "agent_entrepreneur.server"],
        env={
            **os.environ,
            "AGENT_ENTREPRENEUR_TRANSPORT": "stdio",
            "AGENT_ENTREPRENEUR_DB": str(database_path),
        },
    )
    measurements: dict[str, list[float]] = {name: [] for name, _ in TOOL_CALLS}
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            if initialized.serverInfo.name != "Agent Entrepreneur":
                raise AssertionError("unexpected MCP server identity")
            available = {tool.name for tool in (await session.list_tools()).tools}
            for tool_name, arguments in TOOL_CALLS:
                if tool_name not in available:
                    raise AssertionError(f"missing tool: {tool_name}")
                for _ in range(iterations):
                    started = time.perf_counter()
                    result = await session.call_tool(tool_name, arguments)
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    if result.isError:
                        raise AssertionError(f"{tool_name} returned an MCP error")
                    measurements[tool_name].append(elapsed_ms)

    return {
        "suite": "experience-agent-stdio-performance-smoke-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "platform": platform.platform(),
            "python": sys.version,
            "transport": "stdio",
            "client": "Python MCP SDK ClientSession",
        },
        "iterations_per_tool": iterations,
        "total_calls": iterations * len(TOOL_CALLS),
        "results": {
            name: {
                "samples": len(values),
                "p50_ms": percentile(values, 0.50),
                "p95_ms": percentile(values, 0.95),
                "max_ms": round(max(values), 3),
                "errors": 0,
            }
            for name, values in measurements.items()
        },
        "limitations": [
            "Single GitHub-hosted runner and local subprocess transport only.",
            "Small bounded sample; not a production-scale capacity or tail-latency claim.",
            "No concurrent clients or network transport are exercised.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.iterations <= 200:
        parser.error("--iterations must be between 1 and 200")

    with tempfile.TemporaryDirectory() as directory:
        report = asyncio.run(
            run_benchmark(args.iterations, Path(directory) / "benchmark.sqlite3")
        )
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
