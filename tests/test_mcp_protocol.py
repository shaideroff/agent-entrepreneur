from collections.abc import AsyncGenerator
import os
from pathlib import Path
import sys

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.shared.memory import create_connected_server_and_client_session

from agent_entrepreneur.config import Settings
from agent_entrepreneur.server import create_server


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client_session(tmp_path: Path) -> AsyncGenerator[ClientSession, None]:
    server = create_server(Settings(database_path=tmp_path / "agent-entrepreneur.db"))
    async with create_connected_server_and_client_session(
        server, raise_exceptions=True
    ) as session:
        yield session


@pytest.mark.anyio
async def test_mcp_protocol_exposes_tools_resources_prompts_and_invokes_tool(
    client_session: ClientSession,
) -> None:
    tools = await client_session.list_tools()
    assert {tool.name for tool in tools.tools} == {
        "understand_business",
        "research_market",
        "analyse_business",
        "evaluate_decision",
        "create_execution_plan",
        "review_outcomes",
    }

    resources = await client_session.list_resources()
    assert {str(resource.uri) for resource in resources.resources} == {
        "agent-entrepreneur://knowledge/specialists",
        "agent-entrepreneur://knowledge/entrepreneurs",
    }

    prompts = await client_session.list_prompts()
    assert {prompt.name for prompt in prompts.prompts} == {
        "business_diagnosis",
        "market_entry_assessment",
        "founder_execution_review",
    }

    result = await client_session.call_tool(
        "understand_business",
        {"name": "Protocol Test Co", "industry": "software", "geography": "global"},
    )
    assert result.isError is False
    assert result.structuredContent is not None
    assert result.structuredContent["business"]["name"] == "Protocol Test Co"


@pytest.mark.anyio
async def test_stdio_transport_initializes_and_serves_tool_calls(tmp_path: Path) -> None:
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
            assert "understand_business" in {tool.name for tool in tools.tools}

            result = await session.call_tool(
                "understand_business",
                {"name": "STDIO Protocol Co", "industry": "software"},
            )
            assert result.isError is False
            assert result.structuredContent is not None
            assert result.structuredContent["business"]["name"] == "STDIO Protocol Co"
