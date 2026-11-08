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
                "plan_specialist_workflow",
                "complete_specialist_workflow",
                "resume_specialist_workflow",
                "search_entrepreneurs",
                "save_memory",
                "search_memory",
                "delete_memory",
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

            plan_result = await session.call_tool(
                "plan_specialist_workflow",
                {"objective": "evaluate pricing", "domains": ["finance"], "max_specialists": 1},
            )
            assert plan_result.isError is False
            plan = json.loads(plan_result.content[0].text)
            assert len(plan["specialists"]) == 1
            specialist_id = plan["specialists"][0]["specialist_id"]

            completed = await session.call_tool(
                "complete_specialist_workflow",
                {
                    "workflow_id": plan["workflow_id"],
                    "objective": "evaluate pricing",
                    "domains": ["finance"],
                    "max_specialists": 1,
                    "specialist_responses": [
                        {
                            "specialist_id": specialist_id,
                            "findings": [
                                {
                                    "statement": "Pricing needs a paid validation test.",
                                    "evidence_status": "unverified",
                                }
                            ],
                            "recommendations": ["Run a bounded paid pilot."],
                        }
                    ],
                },
            )
            assert completed.isError is False
            workflow = json.loads(completed.content[0].text)
            assert workflow["status"] == "completed"
            assert workflow["steps_completed"] == 1

            interrupted_plan_result = await session.call_tool(
                "plan_specialist_workflow",
                {
                    "objective": "validate market entry",
                    "domains": ["finance", "operations"],
                    "context": "A small pilot with limited capital",
                    "max_specialists": 2,
                },
            )
            interrupted_plan = json.loads(interrupted_plan_result.content[0].text)
            first_specialist, second_specialist = interrupted_plan["specialists"]
            partial = await session.call_tool(
                "complete_specialist_workflow",
                {
                    "workflow_id": interrupted_plan["workflow_id"],
                    "objective": "validate market entry",
                    "domains": ["finance", "operations"],
                    "context": "A small pilot with limited capital",
                    "max_specialists": 2,
                    "specialist_responses": [
                        {
                            "specialist_id": first_specialist["specialist_id"],
                            "findings": [
                                {
                                    "statement": "The pilot budget needs a capped downside.",
                                    "evidence_status": "unverified",
                                }
                            ],
                        },
                        {
                            "specialist_id": second_specialist["specialist_id"],
                            "findings": [
                                {
                                    "statement": "Operations capacity is ready.",
                                    "evidence_status": "supported",
                                }
                            ],
                        },
                    ],
                },
            )
            partial_workflow = json.loads(partial.content[0].text)
            assert partial_workflow["status"] == "partial"
            resumed = await session.call_tool(
                "resume_specialist_workflow",
                {
                    "workflow_id": interrupted_plan["workflow_id"],
                    "objective": "validate market entry",
                    "domains": ["finance", "operations"],
                    "context": "A small pilot with limited capital",
                    "max_specialists": 2,
                    "specialist_responses": [
                        {
                            "specialist_id": second_specialist["specialist_id"],
                            "findings": [
                                {
                                    "statement": "Operations capacity still needs a measured pilot.",
                                    "evidence_status": "unverified",
                                }
                            ],
                        }
                    ],
                },
            )
            assert resumed.isError is False
            assert json.loads(resumed.content[0].text)["status"] == "completed"

            profile_result = await session.call_tool(
                "search_entrepreneurs", {"query": "Canva", "region": "Oceania"}
            )
            assert profile_result.isError is False
            profiles = json.loads(profile_result.content[0].text)
            assert profiles[0]["name"] == "Melanie Perkins"

            denied_memory = await session.call_tool(
                "save_memory", {"content": "pricing notes", "consent": False}
            )
            assert denied_memory.isError is True
            saved_memory = await session.call_tool(
                "save_memory", {"content": "pricing notes", "consent": True}
            )
            assert saved_memory.isError is False
            memory = json.loads(saved_memory.content[0].text)
            searched_memory = await session.call_tool(
                "search_memory", {"query": "pricing"}
            )
            assert searched_memory.isError is False
            assert json.loads(searched_memory.content[0].text)[0]["id"] == memory["record_id"]
            deleted_memory = await session.call_tool(
                "delete_memory", {"record_id": memory["record_id"]}
            )
            assert deleted_memory.isError is False
