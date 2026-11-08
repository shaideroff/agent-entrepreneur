from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_stdio_transport_exposes_protocol_and_serves_tool_calls(
    tmp_path: Path,
) -> None:
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "agent_entrepreneur.server"],
        env={
            **os.environ,
            "AGENT_ENTREPRENEUR_TRANSPORT": "stdio",
            "AGENT_ENTREPRENEUR_DB": str(tmp_path / "stdio-protocol.sqlite3"),
        },
    )
    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            assert initialized.serverInfo.name == "Agent Entrepreneur"

            tools = await session.list_tools()
            assert {tool.name for tool in tools.tools} == {
                "understand_business",
                "research_market",
                "analyse_business",
                "evaluate_decision",
                "create_execution_plan",
                "review_outcomes",
            }

            resources = await session.list_resources()
            assert {str(resource.uri) for resource in resources.resources} == {
                "agent-entrepreneur://knowledge/specialists",
                "agent-entrepreneur://knowledge/entrepreneurs",
            }

            prompts = await session.list_prompts()
            assert {prompt.name for prompt in prompts.prompts} == {
                "business_diagnosis",
                "market_entry_assessment",
                "founder_execution_review",
            }

            invalid_result = await session.call_tool(
                "understand_business",
                {"industry": "software", "geography": "global"},
            )
            assert invalid_result.isError is True

            result = await session.call_tool(
                "understand_business",
                {"name": "Protocol Test Co", "industry": "software", "geography": "global"},
            )
            assert result.isError is False
            assert result.content
            payload = json.loads(result.content[0].text)
            assert payload["business"]["name"] == "Protocol Test Co"
