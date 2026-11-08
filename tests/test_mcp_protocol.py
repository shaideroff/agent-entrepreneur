from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
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
